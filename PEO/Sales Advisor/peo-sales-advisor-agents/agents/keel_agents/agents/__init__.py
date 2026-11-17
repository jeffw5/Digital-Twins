"""Generated index of hosted agents: agent ID -> task_from_event."""
from __future__ import annotations

from typing import Any, Callable

from . import sharepoint_delta_agent
from . import web_crawl_agent
from . import feed_listener_agent
from . import identity_resolver
from . import format_extractor
from . import content_type_classifier
from . import persona_and_job_step_tagger
from . import claim_extractor
from . import jurisdiction_and_validity_miner
from . import pii_and_sensitivity_detector
from . import entitlement_enforcer
from . import concept_mapping_agent
from . import rule_binding_agent
from . import shacl_publisher
from . import mapping_drift_sentinel
from . import intent_and_rcb_agent
from . import federated_query_planner
from . import facet_navigator
from . import mapping_resolver
from . import precision_extractor
from . import brief_assembler
from . import machine_package_agent
from . import grounding_guard
from . import outcome_binder
from . import job_step_telemetry_agent
from . import value_gap_monitor
from . import decision_impact_tracker
from . import content_change_monitor
from . import semantic_change_monitor
from . import rdf_structure_monitor
from . import impact_analyzer
from . import incremental_refresh_service
from . import cache_invalidation_agent
from . import causal_graph_builder
from . import effect_estimator
from . import risk_and_opportunity_ranker
from . import counterfactual_explainer
from . import action_proposer

TASKS: dict[str, Callable[[dict[str, Any]], str]] = {
    "AG-01": sharepoint_delta_agent.task_from_event,
    "AG-02": web_crawl_agent.task_from_event,
    "AG-03": feed_listener_agent.task_from_event,
    "AG-04": identity_resolver.task_from_event,
    "AG-05": format_extractor.task_from_event,
    "AG-06": content_type_classifier.task_from_event,
    "AG-07": persona_and_job_step_tagger.task_from_event,
    "AG-08": claim_extractor.task_from_event,
    "AG-09": jurisdiction_and_validity_miner.task_from_event,
    "AG-10": pii_and_sensitivity_detector.task_from_event,
    "AG-11": entitlement_enforcer.task_from_event,
    "AG-12": concept_mapping_agent.task_from_event,
    "AG-13": rule_binding_agent.task_from_event,
    "AG-14": shacl_publisher.task_from_event,
    "AG-15": mapping_drift_sentinel.task_from_event,
    "AG-16": intent_and_rcb_agent.task_from_event,
    "AG-17": federated_query_planner.task_from_event,
    "AG-18": facet_navigator.task_from_event,
    "AG-19": mapping_resolver.task_from_event,
    "AG-20": precision_extractor.task_from_event,
    "AG-21": brief_assembler.task_from_event,
    "AG-22": machine_package_agent.task_from_event,
    "AG-23": grounding_guard.task_from_event,
    "AG-24": outcome_binder.task_from_event,
    "AG-25": job_step_telemetry_agent.task_from_event,
    "AG-26": value_gap_monitor.task_from_event,
    "AG-27": decision_impact_tracker.task_from_event,
    "AG-28": content_change_monitor.task_from_event,
    "AG-29": semantic_change_monitor.task_from_event,
    "AG-30": rdf_structure_monitor.task_from_event,
    "AG-31": impact_analyzer.task_from_event,
    "AG-32": incremental_refresh_service.task_from_event,
    "AG-33": cache_invalidation_agent.task_from_event,
    "AG-34": causal_graph_builder.task_from_event,
    "AG-35": effect_estimator.task_from_event,
    "AG-36": risk_and_opportunity_ranker.task_from_event,
    "AG-37": counterfactual_explainer.task_from_event,
    "AG-38": action_proposer.task_from_event,
}
