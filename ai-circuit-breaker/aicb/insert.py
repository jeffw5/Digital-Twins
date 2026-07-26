"""
The Insertion API.

This is the point of the whole exercise: the breaker has to be trivially "insertable"
into any AI model or agent, without requiring that model/agent to be rebuilt, retrained,
or rearchitected. Two insertion patterns are provided:

  1. `@protect(...)` -- a decorator for anything that looks like a function call: a raw
     LLM completion call, a classifier, a single-shot agent invocation. Wrap the call,
     supply two small adapter functions that translate the call's inputs/outputs into
     the breaker's standard (AgentAssertion, GroundTruth) shapes, and every call is now
     governed.

  2. `ToolGate` -- for agentic tool-calling loops (LangChain/AutoGen/custom ReAct loops/
     MCP tool servers/etc). Insert `gate.guard(tool_name, tool_args, executor)` at the
     point where the agent is about to *execute* a tool call. The breaker evaluates the
     proposed action BEFORE it runs -- true pre-execution veto, matching "The Veto Gate"
     in the design spec -- rather than after-the-fact detection.

Both patterns are adapter-based on purpose: the breaker never needs to understand your
model's internals, prompt format, or framework. It only needs an AgentAssertion (what is
the AI proposing to do, and how confident is it) and a GroundTruth (what does the
deterministic sensor/context data actually say). That is the entire integration surface.
"""
from __future__ import annotations

import functools
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .breaker import CircuitBreaker, BreakerDecision, SafeState
from .tuple_config import AgentAssertion, GroundTruth


class CircuitBreakerTrip(Exception):
    """Raised by `protect(..., on_trip="raise")` when the breaker vetoes an action."""

    def __init__(self, decision: BreakerDecision):
        self.decision = decision
        super().__init__(
            f"AI Circuit Breaker tripped [{decision.decision_label}]: {'; '.join(decision.reasons)}"
        )


@dataclass
class AICBResult:
    """Wraps a governed call's output together with the breaker's verdict, so callers can
    still access `result.output` normally while inspecting `result.decision` for trust
    metadata (attached to the output per the spec's "ATTACH trust_score_metadata to
    output record").
    """

    output: Any
    decision: BreakerDecision

    @property
    def passed(self) -> bool:
        return self.decision.passed

    @property
    def trust_metadata(self) -> dict:
        return {
            "decision": self.decision.decision_label,
            "safe_state": int(self.decision.safe_state),
            "audit_hash": self.decision.audit_hash,
            **self.decision.metrics,
        }


def protect(
    breaker: CircuitBreaker,
    *,
    to_assertion: Callable[..., AgentAssertion],
    to_ground_truth: Callable[..., GroundTruth],
    on_trip: str = "raise",  # "raise" | "fallback" | "flag_and_pass"
    fallback: Any = None,
):
    """Decorator that inserts the circuit breaker around any callable.

    Example
    -------
    @protect(breaker, to_assertion=my_adapter, to_ground_truth=my_sensor_fn, on_trip="raise")
    def call_llm(prompt: str) -> str:
        return my_llm_client.complete(prompt)

    result = call_llm("reroute traffic through node 7")
    # result.output        -> the original LLM string (only reachable if not tripped, or on_trip != "raise")
    # result.trust_metadata -> Sa, Cr, trust_index, decision, audit hash, etc.
    """
    if on_trip not in ("raise", "fallback", "flag_and_pass"):
        raise ValueError("on_trip must be one of: raise, fallback, flag_and_pass")

    def decorator(fn: Callable[..., Any]):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> AICBResult:
            raw_output = fn(*args, **kwargs)
            assertion = to_assertion(raw_output, *args, **kwargs)
            ground_truth = to_ground_truth(*args, **kwargs)
            decision = breaker.evaluate(assertion, ground_truth)

            if decision.passed or decision.safe_state == SafeState.LEVEL1_SOFT_ALERT:
                return AICBResult(output=raw_output, decision=decision)

            if on_trip == "raise":
                raise CircuitBreakerTrip(decision)
            elif on_trip == "fallback":
                return AICBResult(output=fallback, decision=decision)
            else:  # flag_and_pass
                return AICBResult(output=raw_output, decision=decision)

        wrapper.__wrapped_by_aicb__ = True
        wrapper.breaker = breaker
        return wrapper

    return decorator


@dataclass
class ToolGateResult:
    executed: bool
    output: Any
    decision: BreakerDecision


class ToolGate:
    """Pre-execution veto for agent tool-calling loops.

    Insert this at the point in your agent framework where a tool call is about to be
    dispatched (e.g. a LangChain `Tool.run` override, an OpenAI/Anthropic tool-use
    handler, or a custom ReAct loop's action-execution step). The breaker evaluates the
    proposed tool call BEFORE `executor` runs; if it trips, the tool never executes.
    """

    def __init__(
        self,
        breaker: CircuitBreaker,
        to_assertion: Callable[[str, dict], AgentAssertion],
        to_ground_truth: Callable[[str, dict], GroundTruth],
    ) -> None:
        self.breaker = breaker
        self.to_assertion = to_assertion
        self.to_ground_truth = to_ground_truth

    def guard(
        self,
        tool_name: str,
        tool_args: dict,
        executor: Callable[[str, dict], Any],
    ) -> ToolGateResult:
        assertion = self.to_assertion(tool_name, tool_args)
        ground_truth = self.to_ground_truth(tool_name, tool_args)
        decision = self.breaker.evaluate(assertion, ground_truth)

        allow_execute = decision.passed or decision.safe_state == SafeState.LEVEL1_SOFT_ALERT
        if not allow_execute:
            return ToolGateResult(executed=False, output=None, decision=decision)

        output = executor(tool_name, tool_args)
        return ToolGateResult(executed=True, output=output, decision=decision)
