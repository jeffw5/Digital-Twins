"""
AI Circuit Breaker (aicb)
=========================

A domain-agnostic, dependency-light "deterministic veto" governance layer that can be
inserted in front of (or inside) any AI model or agent.

Implements the architecture described in:
  - "AI Circuit Breaker: Section 1 - The Framework" (design spec)
  - "AI Circuit Breaker: Section 2 - Trustworthiness Metrology & Semantic Governance"
  - "AI Circuit Breaker: Section 3 - Metrics Definitions and Sources of Record"
  - "Technical Design Document: AI Circuit Breaker Technical Implementation Framework"
  - "Wach & Wallk, AI Circuit Breaker" abstract (five-layer measurement architecture)
  - "Addendum A: The Governance Quad-Tuple (H, O, V, A)"

Core idea: trust is treated as a *measured engineering property*, not a vibe. Every
AI assertion is scored against a deterministic ground truth (an ontology + live sensor/
context data) before it is allowed to act. If the delta between AI intent and ground
truth exceeds an engineered tolerance, the breaker trips and the system falls back to a
graduated safe state instead of executing the AI's proposed action.

The package is intentionally free of any ML/embedding-model dependency (only numpy +
stdlib) so that it can be dropped in front of literally any model -- a hosted LLM API,
a local model, a rules engine, or a full agent tool-calling loop -- without adding a
second opaque model on top of the first one you're trying to govern.
"""

from .tuple_config import (
    AuthorityEnvelope,
    HolonicBoundary,
    OntologyRule,
    DomainOntology,
    VectorContextStore,
    AgentAssertion,
    GroundTruth,
)
from .metrics import (
    semantic_anomaly_score,
    contextual_relevancy_index,
    mtbh,
    human_ai_calibration_coefficient,
    value_drift_coefficient,
    composite_trust_index,
)
from .breaker import CircuitBreaker, BreakerConfig, BreakerDecision, SafeState
from .audit import AuditTrail
from .insert import protect, ToolGate, CircuitBreakerTrip
from .morphism import Boundary, MorphismChain, MorphismEvaluationRecord, PassResult, structural_distance, semantic_distance
from .hitl import ReviewLog, ReviewAction, HTDR
from . import console

__all__ = [
    "AuthorityEnvelope",
    "HolonicBoundary",
    "OntologyRule",
    "DomainOntology",
    "VectorContextStore",
    "AgentAssertion",
    "GroundTruth",
    "semantic_anomaly_score",
    "contextual_relevancy_index",
    "mtbh",
    "human_ai_calibration_coefficient",
    "value_drift_coefficient",
    "composite_trust_index",
    "CircuitBreaker",
    "BreakerConfig",
    "BreakerDecision",
    "SafeState",
    "AuditTrail",
    "protect",
    "ToolGate",
    "CircuitBreakerTrip",
    "Boundary",
    "MorphismChain",
    "MorphismEvaluationRecord",
    "PassResult",
    "structural_distance",
    "semantic_distance",
    "ReviewLog",
    "ReviewAction",
    "HTDR",
    "console",
]

__version__ = "0.1.0"
