"""
Trust Metrology Dashboard (Layer 5 - Underwriting Interface).

Renders a single self-contained HTML file -- no CDN/JS-framework dependency, no network
call -- with three views:

  1. E2E Agent Flow      the L1-L5 containment diagram (per TB-02, Fig. 2) plus, if a
                         MorphismChain is attached, the pipeline's boundary chain
                         (per TB-04, Fig. 4) with live certification state per boundary.

  2. Morphism Evaluation  the d_S / d_M quadrant map (per TB-03, Fig. 3), the running
                         MER (Morphism Evaluation Record) log, and a Composition Theorem
                         panel that makes the "hidden loss" from multiplicative fidelity
                         degradation visible (per TB-01's headline claim).

  3. Training & Feedback  the Human Trustee's review queue (every flagged/tripped
     (Human-in-the-Loop)  epoch), a drill-down detail view per event, and staged
                         review actions (Confirm Hallucination / False-Positive
                         Override / Corrected Label / Escalate) that export as a JSON
                         file. See examples/apply_hitl_review.py for how an exported
                         file is applied back through CircuitBreaker.review_flagged_event
                         so the correction actually changes system state (SOP-03
                         eligibility, ontology reference set) -- the dashboard is the
                         "dig into it" surface, the apply script is the "make the
                         correction stick" surface.

All data is embedded as a single JSON blob; everything else is vanilla HTML/CSS/JS.
"""
from __future__ import annotations

import html
import json
import math
import time

from .breaker import CircuitBreaker
from . import architecture_explorer as _arch


# --------------------------------------------------------------------- layer reference --
# Static reference text for the E2E Agent Flow drill-down drawers (L1-L5). Flow-oriented
# (function / invariant / what to watch for in THIS live view), distinct from -- not a
# duplicate of -- architecture_explorer.py's spec-oriented TB02_LAYERS content.

LAYER_REFERENCE = [
    dict(tag="L1", name="Ground Truth Authority",
         function="Live sensor and context telemetry -- link state, congestion, interference, RF/optical "
                  "readings -- treated as the deterministic physical reality every other layer is measured "
                  "against. This layer has no opinion; it only reports what the network is actually doing right now.",
         invariant="Sensor-deterministic ground truth holds a deterministic veto over any AI assertion -- if the "
                    "AI's context model disagrees with L1, L1 wins.",
         watch_for="Viability (how well the AI's situational model tracks live sensor truth). This is where an "
                    "AI that 'thinks the link is up when it's actually down' gets caught."),
    dict(tag="L2", name="Functor Certification",
         function="Every boundary the agent's pipeline crosses (B1 -> B2 -> B3) is measured for structural "
                  "distance (d_S) and semantic distance (d_M) against engineered tolerances. A boundary is "
                  "certified iff both are within tolerance.",
         invariant="Certified iff d_S <= tau_S AND d_M <= tau_M -- independent of whether Layer 3/4 downstream "
                    "happen to also catch the same fault.",
         watch_for="Uncertified boundary count, and which specific boundary is uncertified. Pairs with the Live "
                    "Morphism Evaluation tab's step-through to see exactly where in the pipeline meaning started "
                    "to drift."),
    dict(tag="L3", name="Consistency Manager",
         function="Checks the proposed action against hard ontology rules -- physically/logically impossible "
                  "states (e.g. requested bandwidth exceeding a link's physical capacity) -- independent of any "
                  "distance/similarity score.",
         invariant="Impossible states halt coupling unconditionally, regardless of how small the measured "
                    "Sa/Cr/d_S/d_M scores are.",
         watch_for="Ontology violation count on the most recent decision -- this is the layer that catches "
                    "hallucinations that are internally consistent (low Sa) but ontologically invalid."),
    dict(tag="L4", name="Circuit Breaker + Monitor",
         function="The CB state machine itself: combines Sa/Cr/trust-index thresholds, SPC drift detection, and "
                  "L2/L3 findings into a single decision (TRANSMIT / SOFT_ALERT / HOLD / HALT / LOCKOUT), and "
                  "maintains the running MTBH counter.",
         invariant="Trips at 1.5x the engineering tolerance (Alert state below that line); executes an Emergency "
                    "Halt on any guardrail violation independent of the numeric threshold path.",
         watch_for="MTBH trend and the most recent decision -- a declining MTBH across passes is the earliest "
                    "system-level signal of model drift."),
    dict(tag="L5", name="Human Trustee",
         function="The ultimate veto and re-coupling authority. Every flagged or tripped epoch lands in this "
                  "layer's review queue; a Trustee digs into the specific fault (Training & Feedback tab) and can "
                  "confirm, override, correct, or escalate.",
         invariant="Cannot be overridden by any automated layer -- resuming from a lockout requires an explicit "
                    "Trustee action.",
         watch_for="Flagged-for-review count and HTDR entries logged -- jump to the Training & Feedback tab to "
                    "work the queue directly."),
]


# ---------------------------------------------------------------------------- helpers --

def _json_safe(obj):
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


def _gauge_color(value: float, green: float, alert: float) -> str:
    if value >= green:
        return "#1e8e3e"
    if value >= alert:
        return "#e8a300"
    return "#d93025"


def _gauge_svg(label: str, value: float, green: float = 0.85, alert: float = 0.65) -> str:
    value = max(0.0, min(1.0, value))
    color = _gauge_color(value, green, alert)
    pct = value * 100
    circumference = 2 * 3.14159265 * 42
    offset = circumference * (1 - value)
    return f"""
    <div class="gauge">
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#e8eaed" stroke-width="10"/>
        <circle cx="50" cy="50" r="42" fill="none" stroke="{color}" stroke-width="10"
                stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{offset:.2f}"
                stroke-linecap="round" transform="rotate(-90 50 50)"/>
        <text x="50" y="55" text-anchor="middle" font-size="17" font-weight="700" fill="#202124">{pct:.0f}%</text>
      </svg>
      <div class="gauge-label">{html.escape(label)}</div>
    </div>
    """


def _build_payload(breaker: CircuitBreaker) -> dict:
    status = breaker.status()

    if breaker.vector_store.history:
        last = breaker.vector_store.history[-1].metrics
        gauges = dict(
            credibility=last.get("credibility", 1.0),
            validity=last.get("validity", 1.0),
            viability=last.get("viability", 1.0),
            trust=last.get("trust_index", 1.0),
        )
    else:
        gauges = dict(credibility=1.0, validity=1.0, viability=1.0, trust=1.0)

    audit = [e.to_dict() for e in breaker.audit.entries]
    htdr = [e.to_dict() for e in breaker.review_log.entries]

    morphism = None
    if breaker.morphism_chain is not None:
        mc = breaker.morphism_chain
        morphism = {
            "boundaries": [
                dict(
                    boundary_id=b.boundary_id, name=b.name, tau_s=b.tau_s, tau_m=b.tau_m,
                    w_c=b.w_c, description=b.description, trip_multiplier=b.trip_multiplier,
                )
                for b in mc.boundaries
            ],
            "records": [r.to_dict() for r in mc.records],
            "passes": [
                dict(
                    pass_id=p.pass_id,
                    composed_fidelity=p.composed_fidelity,
                    naive_avg_fidelity=p.naive_avg_fidelity,
                    hidden_loss=p.hidden_loss,
                    all_certified=p.all_certified,
                    worst_boundary=p.worst_boundary,
                    record_seqs=[r.seq for r in p.records],
                )
                for p in mc.passes
            ],
        }

    holon = {
        "name": breaker.holon.name,
        "allowed_actions": sorted(breaker.holon.authority.allowed_actions),
        "forbidden_actions": sorted(breaker.holon.authority.forbidden_actions),
        "max_risk_tier": breaker.holon.authority.max_risk_tier,
        "escalation_topology": breaker.holon.escalation_topology,
    }
    ontology = {
        "name": breaker.ontology.name,
        "version": breaker.ontology.version,
        "reference_assertions": breaker.ontology.reference_assertions,
        "rules": [
            dict(rule_id=r.rule_id, description=r.description, severity=r.severity)
            for r in breaker.ontology.rules
        ],
    }

    payload = {
        "generated_at": time.time(),
        "status": status,
        "gauges": gauges,
        "audit": audit,
        "htdr": htdr,
        "morphism": morphism,
        "holon": holon,
        "ontology": ontology,
        "layer_reference": LAYER_REFERENCE,
    }
    return _json_safe(payload)


# ----------------------------------------------------------------------------- render --

def render(breaker: CircuitBreaker, title: str = "AI Circuit Breaker -- Trust Metrology Dashboard") -> str:
    payload = _build_payload(breaker)
    status = payload["status"]
    g = payload["gauges"]

    gauges_html = "".join(
        [
            _gauge_svg("Credibility", g["credibility"], green=0.85, alert=0.65),
            _gauge_svg("Validity", g["validity"], green=0.90, alert=0.70),
            _gauge_svg("Viability", g["viability"], green=0.80, alert=0.60),
            _gauge_svg("Overall Trust", g["trust"], green=0.75, alert=0.55),
        ]
    )

    lockout_banner = ""
    if status["locked_out"]:
        lockout_banner = (
            f'<div class="banner">SOP-02 LOCKOUT ACTIVE &mdash; '
            f'{html.escape(status["lockout_reason"] or "")}. Autonomous operation halted '
            f'pending Trustee re-authorization.</div>'
        )

    data_json = json.dumps(payload, default=str)
    biz = _arch.BUSINESS_SUMMARY
    domains = " &middot; ".join(html.escape(d) for d in biz["business_domains"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<style>
{_CSS}
</style>
</head>
<body>
<header>
  <h1>{html.escape(title)}</h1>
  <div class="sub">Holon: {html.escape(status['holon'])} &middot; Ontology: {html.escape(status['ontology'])} &middot;
  Handshake: {"PASSED" if status['handshake_ok'] else "FAILED"} &middot;
  Decision chain: {"VALID" if status['chain_valid'] else "TAMPERED"} &middot;
  HTDR chain: {"VALID" if status['htdr_chain_valid'] else "TAMPERED"}</div>
  <div class="sub" style="margin-top:3px;">Business model: {html.escape(biz['business_model'])}</div>
  <div class="sub" style="margin-top:1px;">Business domains: {domains}</div>
</header>
{lockout_banner}

<nav class="tabs">
  <button class="tab-btn active" data-tab="flow">E2E Agent Flow</button>
  <button class="tab-btn" data-tab="morphism">Morphism Evaluation</button>
  <button class="tab-btn" data-tab="hitl">Training &amp; Feedback (HITL)</button>
</nav>

<div class="container">
  <div class="grid">
    <div class="card gauges">{gauges_html}</div>
    <div class="card stat"><div class="n">{status['mtbh_hours']:.2f} h</div><div class="l">MTBH</div></div>
    <div class="card stat"><div class="n">{status['total_hallucinations']}</div><div class="l">Total Trips</div></div>
    <div class="card stat"><div class="n">{status['flagged_for_review']}</div><div class="l">Flagged for Trustee Review</div></div>
    <div class="card stat"><div class="n">{status['htdr_entries']}</div><div class="l">HTDR Reviews Logged</div></div>
  </div>

  <section id="tab-flow" class="tabpanel active"></section>
  <section id="tab-morphism" class="tabpanel"></section>
  <section id="tab-hitl" class="tabpanel"></section>
</div>

<div id="drawer-backdrop" class="drawer-backdrop"></div>
<aside id="drawer" class="drawer"></aside>

<script id="aicb-data" type="application/json">{data_json}</script>
<script>
{_JS}
</script>
</body>
</html>"""


def write(breaker: CircuitBreaker, path: str, title: str = "AI Circuit Breaker -- Trust Metrology Dashboard") -> str:
    content = render(breaker, title=title)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# ----------------------------------------------------------------------------- CSS -----

_CSS = """
  * { box-sizing: border-box; }
  body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; background: #f6f7f9; color: #202124; }
  header { background: #10233f; color: white; padding: 18px 32px; }
  header h1 { margin: 0; font-size: 19px; }
  header .sub { opacity: .78; font-size: 12.5px; margin-top: 4px; }
  .banner { background: #d93025; color: white; padding: 10px 32px; font-weight: 600; font-size: 13px; }
  nav.tabs { display: flex; gap: 4px; background: #0c1c33; padding: 0 28px; }
  .tab-btn { background: transparent; border: none; color: #b7c2d6; padding: 12px 18px; font-size: 13px; font-weight: 600;
             cursor: pointer; border-bottom: 3px solid transparent; }
  .tab-btn:hover { color: white; }
  .tab-btn.active { color: white; border-bottom-color: #4c8dff; }
  .container { padding: 22px 32px 60px; }
  .grid { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 22px; }
  .card { background: white; border-radius: 10px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
  .gauges { display: flex; gap: 6px; }
  .gauge { text-align: center; }
  .gauge-label { font-size: 11px; color: #5f6368; margin-top: 2px; }
  .stat { min-width: 140px; }
  .stat .n { font-size: 24px; font-weight: 700; }
  .stat .l { font-size: 11px; color: #5f6368; text-transform: uppercase; letter-spacing: .03em; }
  table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
  th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #eee; font-size: 12.5px; vertical-align: top; }
  th { background: #f1f3f4; font-size: 10.5px; text-transform: uppercase; color: #5f6368; position: sticky; top: 0; }
  tr.clickable { cursor: pointer; }
  tr.clickable:hover { background: #f6f9ff; }
  tr.current-step { background: #eaf0ff; box-shadow: inset 3px 0 0 #4c8dff; }
  .pill { color: white; padding: 2px 8px; border-radius: 999px; font-size: 10.5px; font-weight: 700; display: inline-block; }
  .badge { padding: 1px 7px; border-radius: 999px; font-size: 10.5px; font-weight: 700; display: inline-block; border: 1px solid; }
  .badge.ok { color: #1e8e3e; border-color: #1e8e3e; background: #eaf7ee; }
  .badge.bad { color: #d93025; border-color: #d93025; background: #fdecea; }
  .reasons { max-width: 340px; color: #5f6368; }
  .hash { font-family: monospace; color: #9aa0a6; font-size: 11px; word-break: break-all; }
  .tabpanel { display: none; }
  .tabpanel.active { display: block; }
  h2.section-title { font-size: 15px; margin: 22px 0 10px; }
  h2.section-title:first-child { margin-top: 0; }
  p.hint { color: #5f6368; font-size: 12.5px; margin: -4px 0 14px; }

  /* --- Flow diagram --- */
  .flow-row { display: flex; align-items: stretch; gap: 8px; overflow-x: auto; padding: 6px 2px 18px; }
  .flow-node { flex: 1 0 150px; background: white; border-radius: 10px; padding: 12px 14px; box-shadow: 0 1px 3px rgba(0,0,0,.08);
               border-top: 4px solid #9aa0a6; position: relative; cursor: pointer; transition: transform .1s ease; }
  .flow-node:hover { transform: translateY(-2px); box-shadow: 0 2px 8px rgba(0,0,0,.14); }
  .flow-node .fn-tag { font-size: 10px; color: #9aa0a6; text-transform: uppercase; letter-spacing: .04em; font-weight: 700; }
  .flow-node .fn-title { font-size: 13px; font-weight: 700; margin: 3px 0 6px; }
  .flow-node .fn-detail { font-size: 11.5px; color: #5f6368; line-height: 1.5; }
  .flow-node.state-normal { border-top-color: #1e8e3e; }
  .flow-node.state-alert { border-top-color: #e8a300; }
  .flow-node.state-trip { border-top-color: #e8730a; }
  .flow-node.state-halt, .flow-node.state-lockout { border-top-color: #d93025; }
  .flow-arrow { align-self: center; font-size: 20px; color: #b7c2d6; flex: 0 0 auto; }

  /* --- Morphism scatter --- */
  .scatter-wrap { background: white; border-radius: 10px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,.08); margin-bottom: 18px; }
  .legend { display: flex; gap: 14px; flex-wrap: wrap; font-size: 11.5px; color: #5f6368; margin-top: 8px; }
  .legend .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 5px; }

  .fidelity-panel { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 18px; }
  .fidelity-card { flex: 1 0 220px; background: white; border-radius: 10px; padding: 14px 16px; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
  .fidelity-card .big { font-size: 22px; font-weight: 700; }
  .fidelity-card .loss { color: #d93025; font-weight: 700; }

  /* --- HITL drawer --- */
  .drawer-backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,.35); z-index: 40; }
  .drawer-backdrop.open { display: block; }
  .drawer { position: fixed; top: 0; right: -520px; width: 500px; max-width: 92vw; height: 100%; background: white;
            box-shadow: -4px 0 18px rgba(0,0,0,.18); z-index: 50; transition: right .18s ease; overflow-y: auto; padding: 20px 22px 40px; }
  .drawer.open { right: 0; }
  .drawer h3 { margin-top: 0; font-size: 16px; }
  .drawer .close-btn { position: absolute; top: 14px; right: 16px; border: none; background: none; font-size: 18px; cursor: pointer; color: #5f6368; }
  .drawer label { display: block; font-size: 11.5px; font-weight: 700; text-transform: uppercase; color: #5f6368; margin: 14px 0 4px; }
  .drawer textarea, .drawer input[type=text] { width: 100%; padding: 8px; border: 1px solid #dadce0; border-radius: 6px; font-size: 13px; font-family: inherit; }
  .drawer .action-btns { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
  .btn { border: 1px solid #dadce0; background: white; border-radius: 6px; padding: 7px 12px; font-size: 12.5px; font-weight: 600; cursor: pointer; }
  .btn:hover { background: #f1f3f4; }
  .btn.primary { background: #0c1c33; color: white; border-color: #0c1c33; }
  .btn.primary:hover { background: #17304f; }
  .btn.danger { color: #d93025; border-color: #d93025; }
  .btn.ok { color: #1e8e3e; border-color: #1e8e3e; }
  .kv { font-size: 12.5px; margin: 3px 0; }
  .kv b { color: #5f6368; font-weight: 600; }
  .metrics-mini { display: grid; grid-template-columns: 1fr 1fr; gap: 4px 14px; margin: 8px 0 4px; }

  .staged-panel { position: fixed; bottom: 0; left: 0; right: 0; background: #0c1c33; color: white; padding: 10px 26px;
                  display: none; align-items: center; gap: 16px; z-index: 30; font-size: 12.5px; }
  .staged-panel.show { display: flex; }
  .staged-panel .count { font-weight: 700; }
"""

# ----------------------------------------------------------------------------- JS ------

_JS = """
const DATA = JSON.parse(document.getElementById('aicb-data').textContent);
const STATE_COLOR = { normal: '#1e8e3e', alert: '#e8a300', trip: '#e8730a', emergency_halt: '#d93025' };
const DECISION_COLOR = {
  TRANSMIT: '#1e8e3e', SOFT_ALERT: '#e8a300', HOLD: '#e8730a', HALT: '#d93025',
  LOCKOUT: '#8b0000', RESUME_AUTHORIZED: '#1a73e8'
};
const BOUNDARY_PALETTE = ['#4c8dff', '#7b5fd9', '#d9527b', '#2ba0a0', '#d98b2b', '#5f6368'];
let pendingDecisions = [];
let trusteeId = '';
let liveMorphStep = 0;
let liveMorphPlayTimer = null;

// ---------------------------------------------------------------- tabs -----
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tabpanel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

function esc(s) {
  return String(s === undefined || s === null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
function fmt3(x) { return (x === null || x === undefined || isNaN(x)) ? '-' : Number(x).toFixed(3); }
function fmtTime(ts) { return ts ? new Date(ts * 1000).toLocaleTimeString() : '-'; }

// ==================================================================== FLOW =
function stateClassForLevel(level) {
  return ({0: 'normal', 1: 'alert', 2: 'trip', 3: 'halt', 4: 'lockout'})[level] || 'normal';
}

function computeFlowNodes() {
  const s = DATA.status;
  const lastAudit = DATA.audit.length ? DATA.audit[DATA.audit.length - 1] : null;
  const l4state = lastAudit ? stateClassForLevel(lastAudit.safe_state_level) : 'normal';
  const l3ok = !lastAudit || !(lastAudit.metrics && lastAudit.metrics.ontology_violations > 0);
  const l1state = (DATA.gauges.viability >= 0.8) ? 'normal' : (DATA.gauges.viability >= 0.6 ? 'alert' : 'trip');
  const l5state = s.locked_out ? 'halt' : (s.flagged_for_review > 0 ? 'alert' : 'normal');

  return [
    { tag: 'L1', title: 'Ground Truth Authority', state: l1state,
      detail: 'Live sensor / context ground truth.<br/>Viability: ' + (DATA.gauges.viability*100).toFixed(0) + '%' },
    { tag: 'L2', title: 'Functor Certification', state: DATA.morphism ? (DATA.morphism.records.some(r=>r.state==='emergency_halt') ? 'halt' : (DATA.morphism.records.some(r=>!r.certified) ? 'alert' : 'normal')) : 'normal',
      detail: DATA.morphism ? (DATA.morphism.boundaries.length + ' boundaries &middot; ' + DATA.morphism.records.filter(r=>!r.certified).length + ' uncertified') : 'No boundary chain configured' },
    { tag: 'L3', title: 'Consistency Manager', state: l3ok ? 'normal' : 'halt',
      detail: 'Ontology impossible-state detection.<br/>' + (l3ok ? 'No active violations' : 'Violation on last cycle') },
    { tag: 'L4', title: 'Circuit Breaker + Monitor', state: l4state,
      detail: 'MTBH: ' + s.mtbh_hours.toFixed(2) + 'h &middot; Trips: ' + s.total_hallucinations + '<br/>Last: ' + (lastAudit ? lastAudit.decision : 'n/a') },
    { tag: 'L5', title: 'Human Trustee', state: l5state,
      detail: s.flagged_for_review + ' flagged for review<br/>' + s.htdr_entries + ' HTDR entries logged' },
  ];
}

function layerStateColor(state) {
  return ({ normal: '#1e8e3e', alert: '#e8a300', trip: '#e8730a', halt: '#d93025', lockout: '#8b0000', emergency_halt: '#d93025' })[state] || '#5f6368';
}

function openLayerDrawer(tag) {
  const ref = (DATA.layer_reference || []).find(l => l.tag === tag);
  const node = computeFlowNodes().find(n => n.tag === tag);
  if (!ref || !node) return;
  const titleHtml = '<h3>' + esc(tag) + ' &mdash; ' + esc(ref.name) + '</h3>' +
    '<span class="pill" style="background:' + layerStateColor(node.state) + '">' + node.state.toUpperCase() + '</span>';
  const bodyHtml =
    '<div class="kv-label">Function</div><p>' + esc(ref.function) + '</p>' +
    '<div class="kv-label">Key invariant</div><p>' + esc(ref.invariant) + '</p>' +
    '<div class="kv-label">What to watch for here</div><p>' + esc(ref.watch_for) + '</p>' +
    '<div class="kv-label">Current live state</div><p>' + node.detail + '</p>';
  openDrawer(titleHtml, bodyHtml);
}

function openBoundaryDrawer(boundaryId) {
  if (!DATA.morphism) return;
  const b = DATA.morphism.boundaries.find(x => x.boundary_id === boundaryId);
  if (!b) return;
  const records = DATA.morphism.records.filter(r => r.boundary_id === boundaryId);
  const latest = records.length ? records[records.length - 1] : null;

  const titleHtml = '<h3>' + esc(b.boundary_id) + ' &mdash; ' + esc(b.name) + '</h3>';
  let bodyHtml = '<div class="kv-label">Context</div><p>' + esc(b.description || '(no description provided)') + '</p>' +
    '<div class="kv-label">Engineering tolerances</div><p>&tau;<sub>S</sub> = ' + b.tau_s + ' &middot; &tau;<sub>M</sub> = ' + b.tau_m +
    ' &middot; consequence weight w<sub>c</sub> = ' + b.w_c + ' &middot; trip multiplier = ' + b.trip_multiplier + 'x</p>';
  if (latest) {
    bodyHtml += '<div class="kv-label">Latest evaluation</div><p>d<sub>S</sub>=' + fmt3(latest.d_s) + ', d<sub>M</sub>=' + fmt3(latest.d_m) +
      ' &middot; <span class="badge ' + (latest.certified ? 'ok' : 'bad') + '">' + (latest.certified ? 'CERTIFIED' : 'NOT CERTIFIED') + '</span> &middot; state: ' + esc(latest.state) + '</p>';
  } else {
    bodyHtml += '<div class="kv-label">Latest evaluation</div><p class="hint" style="margin:0">Not yet evaluated.</p>';
  }
  bodyHtml += '<div class="kv-label">Evaluation history (' + records.length + ' pass' + (records.length === 1 ? '' : 'es') + ')</div>';
  bodyHtml += '<table><thead><tr><th>Pass</th><th>d_S</th><th>d_M</th><th>State</th><th>Certified</th></tr></thead><tbody>';
  records.slice().reverse().forEach(r => {
    bodyHtml += '<tr><td>' + esc(r.pass_id) + '</td><td>' + fmt3(r.d_s) + '</td><td>' + fmt3(r.d_m) + '</td>' +
      '<td><span class="pill" style="background:' + (STATE_COLOR[r.state] || '#5f6368') + '">' + esc(r.state) + '</span></td>' +
      '<td>' + (r.certified ? '<span class="badge ok">YES</span>' : '<span class="badge bad">NO</span>') + '</td></tr>';
  });
  bodyHtml += '</tbody></table>';
  openDrawer(titleHtml, bodyHtml);
}

function renderFlow() {
  const nodes = computeFlowNodes();

  let html = '<h2 class="section-title">Five-Layer Assurance Architecture &mdash; Live State</h2>';
  html += '<p class="hint">L1&ndash;L5 containment per TB-02. Each box reflects the CURRENT measured state of that layer, not just the final decision. Click any layer to dig underneath it.</p>';
  html += '<div class="flow-row">';
  nodes.forEach((n, i) => {
    html += '<div class="flow-node state-' + n.state + '" data-tag="' + esc(n.tag) + '"><div class="fn-tag">' + n.tag + '</div>' +
            '<div class="fn-title">' + esc(n.title) + '</div><div class="fn-detail">' + n.detail + '</div></div>';
    if (i < nodes.length - 1) html += '<div class="flow-arrow">&rarr;</div>';
  });
  html += '</div>';

  if (DATA.morphism && DATA.morphism.boundaries.length) {
    html += '<h2 class="section-title">Agent Pipeline &mdash; Boundary Chain</h2>';
    html += '<p class="hint">Each boundary is one handoff between pipeline stages (sensing &rarr; features &rarr; classification &rarr; decision, etc). Colored by its most recent Functor Certification result. Click a boundary for its full context and evaluation history.</p>';
    html += '<div class="flow-row">';
    const latestByBoundary = {};
    DATA.morphism.records.forEach(r => { latestByBoundary[r.boundary_id] = r; });
    DATA.morphism.boundaries.forEach((b, i) => {
      const rec = latestByBoundary[b.boundary_id];
      const state = rec ? rec.state : 'normal';
      const detail = rec
        ? ('d<sub>S</sub>=' + fmt3(rec.d_s) + ' (&tau;=' + b.tau_s + ') &middot; d<sub>M</sub>=' + fmt3(rec.d_m) + ' (&tau;=' + b.tau_m + ')<br/>w<sub>c</sub>=' + b.w_c + ' &middot; ' + (rec.certified ? '<span class="badge ok">CERTIFIED</span>' : '<span class="badge bad">NOT CERTIFIED</span>'))
        : 'not yet evaluated';
      html += '<div class="flow-node state-' + state + '" data-bid="' + esc(b.boundary_id) + '"><div class="fn-tag">' + esc(b.boundary_id) + '</div>' +
              '<div class="fn-title">' + esc(b.name) + '</div><div class="fn-detail">' + detail + '</div></div>';
      if (i < DATA.morphism.boundaries.length - 1) html += '<div class="flow-arrow">&rarr;</div>';
    });
    html += '</div>';
  }

  html += '<h2 class="section-title">Holon Authority Envelope (H)</h2>';
  html += '<table><tbody>' +
    '<tr><td style="width:160px"><b>Holon</b></td><td>' + esc(DATA.holon.name) + '</td></tr>' +
    '<tr><td><b>Allowed actions</b></td><td>' + (DATA.holon.allowed_actions.map(esc).join(', ') || '(none declared)') + '</td></tr>' +
    '<tr><td><b>Forbidden actions</b></td><td>' + (DATA.holon.forbidden_actions.map(esc).join(', ') || '(none declared)') + '</td></tr>' +
    '<tr><td><b>Max risk tier</b></td><td>' + DATA.holon.max_risk_tier + '</td></tr>' +
    '<tr><td><b>Escalation topology</b></td><td>' + Object.entries(DATA.holon.escalation_topology).map(([k,v]) => 'L'+k+' &rarr; '+esc(v)).join(' &middot; ') + '</td></tr>' +
    '</tbody></table>';

  document.getElementById('tab-flow').innerHTML = html;

  document.querySelectorAll('#tab-flow .flow-node[data-tag]').forEach(n => {
    n.addEventListener('click', () => openLayerDrawer(n.dataset.tag));
  });
  document.querySelectorAll('#tab-flow .flow-node[data-bid]').forEach(n => {
    n.addEventListener('click', () => openBoundaryDrawer(n.dataset.bid));
  });
}

// =============================================================== MORPHISM ==
function renderMorphism() {
  const el = document.getElementById('tab-morphism');
  if (!DATA.morphism || !DATA.morphism.boundaries.length) {
    el.innerHTML = '<p class="hint">No MorphismChain attached to this breaker. Pass <code>morphism_chain=MorphismChain([...])</code> to CircuitBreaker and call <code>chain.evaluate_pass(...)</code> per pipeline traversal to populate this view.</p>';
    return;
  }
  const boundaryColor = {};
  DATA.morphism.boundaries.forEach((b, i) => { boundaryColor[b.boundary_id] = BOUNDARY_PALETTE[i % BOUNDARY_PALETTE.length]; });

  const records = DATA.morphism.records;
  const curIdx = records.length ? Math.max(0, Math.min(liveMorphStep, records.length - 1)) : -1;
  liveMorphStep = curIdx;

  const W = 480, H = 420, PAD = 44;
  const sx = x => PAD + x * (W - PAD - 16);
  const sy = y => (H - PAD) - y * (H - PAD - 16);

  let svg = '<svg width="100%" viewBox="0 0 ' + W + ' ' + H + '" style="max-width:560px">';
  // grid
  for (let t = 0; t <= 1.0001; t += 0.25) {
    svg += '<line x1="' + sx(t) + '" y1="' + sy(0) + '" x2="' + sx(t) + '" y2="' + sy(1) + '" stroke="#eee"/>';
    svg += '<line x1="' + sx(0) + '" y1="' + sy(t) + '" x2="' + sx(1) + '" y2="' + sy(t) + '" stroke="#eee"/>';
    svg += '<text x="' + sx(t) + '" y="' + (sy(0)+16) + '" font-size="9" fill="#9aa0a6" text-anchor="middle">' + t.toFixed(2) + '</text>';
    svg += '<text x="' + (sx(0)-8) + '" y="' + (sy(t)+3) + '" font-size="9" fill="#9aa0a6" text-anchor="end">' + t.toFixed(2) + '</text>';
  }
  svg += '<text x="' + (W/2) + '" y="' + (H-6) + '" font-size="11" fill="#5f6368" text-anchor="middle">d_S (structural distance) &rarr;</text>';
  svg += '<text x="12" y="' + (H/2) + '" font-size="11" fill="#5f6368" text-anchor="middle" transform="rotate(-90 12 ' + (H/2) + ')">d_M (semantic distance) &rarr;</text>';

  // tolerance rectangles per boundary
  DATA.morphism.boundaries.forEach(b => {
    const color = boundaryColor[b.boundary_id];
    const x0 = sx(0), y0 = sy(0), x1 = sx(Math.min(b.tau_s,1)), y1 = sy(Math.min(b.tau_m,1));
    svg += '<rect x="' + x0 + '" y="' + y1 + '" width="' + (x1-x0) + '" height="' + (y0-y1) + '" fill="none" stroke="' + color + '" stroke-width="1.4" stroke-dasharray="4,3" opacity="0.85"/>';
  });

  // points -- the current step (per liveMorphStep) is drawn larger with a dark ring so
  // the user can visually follow the agent stepping through the pipeline boundary by
  // boundary, not just see the final scattered cloud.
  records.forEach((r, idx) => {
    const color = STATE_COLOR[r.state] || '#5f6368';
    const isCurrent = idx === curIdx;
    const rad = isCurrent ? 9 : 5;
    const strokeW = isCurrent ? 3 : 1;
    const strokeColor = isCurrent ? '#202124' : 'white';
    const shape = r.state === 'emergency_halt'
      ? '<rect x="' + (sx(r.d_s)-rad) + '" y="' + (sy(r.d_m)-rad) + '" width="' + (rad*2) + '" height="' + (rad*2) + '" fill="' + color + '" stroke="' + strokeColor + '" stroke-width="' + strokeW + '"/>'
      : '<circle cx="' + sx(r.d_s) + '" cy="' + sy(r.d_m) + '" r="' + rad + '" fill="' + color + '" stroke="' + strokeColor + '" stroke-width="' + strokeW + '"/>';
    svg += '<g>' + shape + '<title>' + esc(r.boundary_name) + ' (' + esc(r.pass_id) + ')\\nd_S=' + fmt3(r.d_s) + '  d_M=' + fmt3(r.d_m) + '\\n' + r.state + '</title></g>';
  });
  svg += '</svg>';

  let legend = '<div class="legend">';
  Object.entries(STATE_COLOR).forEach(([k,v]) => { legend += '<span><span class="dot" style="background:' + v + '"></span>' + k + '</span>'; });
  legend += '</div><div class="legend">';
  DATA.morphism.boundaries.forEach(b => { legend += '<span><span class="dot" style="background:' + boundaryColor[b.boundary_id] + '"></span>' + esc(b.name) + ' tolerance region</span>'; });
  legend += '</div>';

  // step-through controls -- walk the agent forward/backward one boundary crossing at a
  // time and watch the highlighted point move on the scatter above.
  let stepPanel = '';
  if (records.length) {
    const cur = records[curIdx];
    stepPanel = '<div class="sim-panel" style="margin-bottom:18px;">' +
      '<span class="sim-verdict ' + (cur.state === 'normal' ? 'ok' : 'trip') + '">' + cur.state.toUpperCase() + '</span>' +
      '<h3>Step ' + (curIdx+1) + ' / ' + records.length + ' &mdash; ' + esc(cur.boundary_name) + ' <span class="hint" style="margin:0">(' + esc(cur.pass_id) + ')</span></h3>' +
      '<div class="metrics-mini">' +
        '<div class="kv"><b>d_S</b>: ' + fmt3(cur.d_s) + ' (&tau;=' + cur.tau_s + ')</div>' +
        '<div class="kv"><b>d_M</b>: ' + fmt3(cur.d_m) + ' (&tau;=' + cur.tau_m + ')</div>' +
        '<div class="kv"><b>w_c</b>: ' + cur.w_c + '</div>' +
        '<div class="kv"><b>Certified</b>: ' + (cur.certified ? 'yes' : 'no') + '</div>' +
      '</div>' +
      '<div class="sim-controls">' +
        '<button class="btn" id="live-morph-prev" ' + (curIdx===0?'disabled':'') + '>&larr; Prev boundary crossing</button>' +
        '<button class="btn primary" id="live-morph-next" ' + (curIdx===records.length-1?'disabled':'') + '>Next boundary crossing &rarr;</button>' +
        '<button class="btn" id="live-morph-play">' + (liveMorphPlayTimer ? 'Pause' : 'Play \\u25b6') + '</button>' +
      '</div></div>';
  }

  // composition fidelity panel (latest pass)
  let fidelityHtml = '';
  if (DATA.morphism.passes.length) {
    const p = DATA.morphism.passes[DATA.morphism.passes.length - 1];
    fidelityHtml = '<div class="fidelity-panel">' +
      '<div class="fidelity-card"><div class="l" style="font-size:11px;color:#5f6368;text-transform:uppercase">Composed fidelity (correct)</div><div class="big">' + (p.composed_fidelity*100).toFixed(1) + '%</div></div>' +
      '<div class="fidelity-card"><div class="l" style="font-size:11px;color:#5f6368;text-transform:uppercase">Naive per-boundary average</div><div class="big">' + (p.naive_avg_fidelity*100).toFixed(1) + '%</div></div>' +
      '<div class="fidelity-card"><div class="l" style="font-size:11px;color:#5f6368;text-transform:uppercase">Hidden loss (Composition Theorem)</div><div class="big loss">' + (p.hidden_loss*100).toFixed(1) + ' pts</div></div>' +
      '<div class="fidelity-card"><div class="l" style="font-size:11px;color:#5f6368;text-transform:uppercase">Worst boundary (latest pass)</div><div class="big" style="font-size:15px">' + esc(p.worst_boundary || '-') + '</div></div>' +
      '</div>' +
      '<p class="hint">phi(Fn&deg;&hellip;&deg;F1) &ge; &prod; phi(Fi). The composed fidelity multiplies each boundary\\'s fidelity together; the naive average is what a per-layer-only dashboard would report. The gap between them is degradation no single boundary\\'s own test would catch.</p>';
  }

  let mer = '<table><thead><tr><th>Pass</th><th>Boundary</th><th>State</th><th>d_S</th><th>&tau;_S</th><th>d_M</th><th>&tau;_M</th><th>w_c</th><th>Certified</th></tr></thead><tbody>';
  records.slice().reverse().forEach((r, revIdx) => {
    const idx = records.length - 1 - revIdx;
    mer += '<tr class="clickable' + (idx===curIdx?' current-step':'') + '" data-step="' + idx + '"><td>' + esc(r.pass_id) + '</td><td>' + esc(r.boundary_name) + '</td>' +
      '<td><span class="pill" style="background:' + (STATE_COLOR[r.state]||'#5f6368') + '">' + r.state.toUpperCase() + '</span></td>' +
      '<td>' + fmt3(r.d_s) + '</td><td>' + r.tau_s + '</td><td>' + fmt3(r.d_m) + '</td><td>' + r.tau_m + '</td><td>' + r.w_c + '</td>' +
      '<td>' + (r.certified ? '<span class="badge ok">YES</span>' : '<span class="badge bad">NO</span>') + '</td></tr>';
  });
  mer += '</tbody></table>';

  el.innerHTML =
    '<h2 class="section-title">Two-Axis Morphism Quality &mdash; d_S / d_M Quadrant Map</h2>' +
    '<p class="hint">Every point is one Morphism Evaluation Record (MER): one boundary crossing, one pass through the pipeline. Dashed rectangles mark each boundary\\'s certification region (0..&tau;_S by 0..&tau;_M). Step through below to watch the agent move boundary by boundary -- the current step is drawn larger with a dark ring.</p>' +
    '<div class="scatter-wrap">' + svg + legend + '</div>' +
    stepPanel +
    '<h2 class="section-title">Composition Theorem</h2>' + fidelityHtml +
    '<h2 class="section-title">Morphism Evaluation Records (MER) <span class="hint" style="margin:0;text-transform:none;font-weight:400;">-- click a row to jump the stepper there</span></h2>' + mer;

  const prevBtn = document.getElementById('live-morph-prev');
  const nextBtn = document.getElementById('live-morph-next');
  const playBtn = document.getElementById('live-morph-play');
  if (prevBtn) prevBtn.addEventListener('click', () => { liveMorphStep = Math.max(0, liveMorphStep - 1); renderMorphism(); });
  if (nextBtn) nextBtn.addEventListener('click', () => { liveMorphStep = Math.min(records.length - 1, liveMorphStep + 1); renderMorphism(); });
  if (playBtn) playBtn.addEventListener('click', () => {
    if (liveMorphPlayTimer) {
      clearInterval(liveMorphPlayTimer);
      liveMorphPlayTimer = null;
      renderMorphism();
      return;
    }
    liveMorphPlayTimer = setInterval(() => {
      if (liveMorphStep >= records.length - 1) {
        clearInterval(liveMorphPlayTimer);
        liveMorphPlayTimer = null;
        renderMorphism();
        return;
      }
      liveMorphStep++;
      renderMorphism();
    }, 900);
    renderMorphism();
  });
  el.querySelectorAll('tr.clickable[data-step]').forEach(tr => {
    tr.addEventListener('click', () => { liveMorphStep = parseInt(tr.dataset.step, 10); renderMorphism(); });
  });
}

// ==================================================================== HITL =
function reviewsForSeq(seq) { return DATA.htdr.filter(h => h.audit_seq === seq); }

function renderHitl() {
  const flagged = DATA.audit.filter(e => e.decision !== 'TRANSMIT' && !e.action.startsWith('__')).slice().reverse();

  let html = '<h2 class="section-title">Trustee Review Queue</h2>';
  html += '<p class="hint">Every flagged/tripped epoch the AI produced. Click a row to dig into the specific fault: full reasons, metrics, and the raw intent, then stage a correction.</p>';
  html += '<div class="card" style="margin-bottom:16px;display:flex;gap:10px;align-items:center;">' +
          '<label style="font-size:12px;font-weight:700;color:#5f6368;text-transform:uppercase;">Trustee ID</label>' +
          '<input type="text" id="trustee-input" placeholder="e.g. j.wallk" style="padding:6px 10px;border:1px solid #dadce0;border-radius:6px;font-size:13px;min-width:220px;">' +
          '</div>';
  html += '<table><thead><tr><th>#</th><th>Time</th><th>Decision</th><th>Action</th><th>Top reason</th><th>Reviewed</th></tr></thead><tbody>';
  if (!flagged.length) {
    html += '<tr><td colspan="6">No flagged events. Nothing needs Trustee review right now.</td></tr>';
  }
  flagged.forEach(e => {
    const reviews = reviewsForSeq(e.seq);
    const reviewedBadge = reviews.length
      ? '<span class="badge ok">' + reviews[reviews.length-1].action.toUpperCase().replace(/_/g,' ') + '</span>'
      : '<span class="badge bad">PENDING</span>';
    html += '<tr class="clickable" data-seq="' + e.seq + '">' +
      '<td>' + e.seq + '</td><td>' + fmtTime(e.timestamp) + '</td>' +
      '<td><span class="pill" style="background:' + (DECISION_COLOR[e.decision]||'#5f6368') + '">' + esc(e.decision) + '</span></td>' +
      '<td>' + esc(e.action) + '</td>' +
      '<td class="reasons">' + esc((e.reasons && e.reasons[0]) || '-') + '</td>' +
      '<td>' + reviewedBadge + '</td></tr>';
  });
  html += '</tbody></table>';

  html += '<h2 class="section-title">Review History (HTDR Log)</h2>';
  html += '<p class="hint">Human Trustee Decision Records already applied via CircuitBreaker.review_flagged_event(...) &mdash; permanent, hash-chained, never edits the original decision.</p>';
  html += '<table><thead><tr><th>#</th><th>Time</th><th>Trustee</th><th>Refers to #</th><th>Action</th><th>Note / Correction</th></tr></thead><tbody>';
  if (!DATA.htdr.length) {
    html += '<tr><td colspan="6">No reviews recorded yet.</td></tr>';
  }
  DATA.htdr.slice().reverse().forEach(h => {
    const extra = h.corrected_intent_text ? ('Corrected intent: &ldquo;' + esc(h.corrected_intent_text) + '&rdquo;') : esc(h.note || '-');
    html += '<tr><td>' + h.seq + '</td><td>' + fmtTime(h.timestamp) + '</td><td>' + esc(h.trustee_id) + '</td>' +
      '<td>#' + h.audit_seq + '</td><td><b>' + esc(h.action.toUpperCase().replace(/_/g,' ')) + '</b></td><td class="reasons">' + extra + '</td></tr>';
  });
  html += '</tbody></table>';

  document.getElementById('tab-hitl').innerHTML = html;

  document.getElementById('trustee-input').addEventListener('input', e => { trusteeId = e.target.value; });
  document.querySelectorAll('#tab-hitl tr.clickable').forEach(tr => {
    tr.addEventListener('click', () => openFlaggedEventDrawer(parseInt(tr.dataset.seq, 10)));
  });
}

function findAuditEntry(seq) { return DATA.audit.find(e => e.seq === seq); }

function openDrawer(titleHtml, bodyHtml) {
  const d = document.getElementById('drawer');
  d.innerHTML = '<button class="close-btn" onclick="closeDrawer()">&times;</button>' + titleHtml + bodyHtml;
  document.getElementById('drawer-backdrop').classList.add('open');
  d.classList.add('open');
}
function closeDrawer() {
  document.getElementById('drawer-backdrop').classList.remove('open');
  document.getElementById('drawer').classList.remove('open');
}
document.getElementById('drawer-backdrop').addEventListener('click', closeDrawer);

function openFlaggedEventDrawer(seq) {
  const e = findAuditEntry(seq);
  if (!e) return;
  const reviews = reviewsForSeq(seq);
  const m = e.metrics || {};

  let metricsHtml = '<div class="metrics-mini">';
  const showMetrics = ['semantic_anomaly_score','contextual_relevancy_index','intent_delta','trust_index',
                        'credibility','validity','viability','ontology_violations','composed_fidelity','naive_avg_fidelity'];
  showMetrics.forEach(k => {
    if (m[k] !== undefined && m[k] !== null) {
      metricsHtml += '<div class="kv"><b>' + k + '</b>: ' + fmt3(m[k]) + '</div>';
    }
  });
  metricsHtml += '</div>';

  let reasonsHtml = '<ul style="margin:6px 0 0 18px;padding:0;font-size:12.5px;color:#5f6368;">' +
    (e.reasons || []).map(r => '<li>' + esc(r) + '</li>').join('') + '</ul>';
  if (!e.reasons || !e.reasons.length) reasonsHtml = '<p class="hint" style="margin:4px 0;">No specific reasons logged.</p>';

  let historyHtml = '';
  if (reviews.length) {
    historyHtml = '<label>Prior reviews</label>' + reviews.map(r =>
      '<div class="kv">' + fmtTime(r.timestamp) + ' &middot; <b>' + esc(r.trustee_id) + '</b> &middot; ' + esc(r.action) +
      (r.note ? (' &mdash; ' + esc(r.note)) : '') + '</div>').join('');
  }

  const titleHtml = '<h3>Event #' + e.seq + ' &mdash; ' + esc(e.decision) + '</h3>';
  const bodyHtml =
    '<div class="kv"><b>Time</b>: ' + fmtTime(e.timestamp) + '</div>' +
    '<div class="kv"><b>Action proposed</b>: ' + esc(e.action) + '</div>' +
    '<div class="kv"><b>Intent text</b>: &ldquo;' + esc(e.intent_text) + '&rdquo;</div>' +
    '<div class="kv"><b>Safe-state level</b>: ' + e.safe_state_level + ' &middot; <b>Excluded from training</b>: ' + (e.excluded_from_training ? 'yes' : 'no') + '</div>' +
    '<div class="kv hash"><b>Audit hash</b>: ' + esc(e.entry_hash) + '</div>' +
    '<label>Why it was flagged</label>' + reasonsHtml +
    '<label>Metrics</label>' + metricsHtml +
    historyHtml +
    '<label>Trustee note</label><textarea id="dr-note" rows="2" placeholder="Root cause, context, rationale..."></textarea>' +
    '<label>Corrected intent (for &ldquo;Correct Label&rdquo; only)</label>' +
    '<input type="text" id="dr-corrected" placeholder="What the AI SHOULD have proposed, in the same phrasing style as the ontology...">' +
    '<div class="action-btns">' +
      '<button class="btn danger" onclick="stageDecision(' + e.seq + ',\\'confirm_hallucination\\')">Confirm Hallucination</button>' +
      '<button class="btn ok" onclick="stageDecision(' + e.seq + ',\\'false_positive_override\\')">Override &mdash; False Positive</button>' +
      '<button class="btn primary" onclick="stageDecision(' + e.seq + ',\\'corrected_label\\')">Correct Label &amp; Add to Ontology</button>' +
      '<button class="btn" onclick="stageDecision(' + e.seq + ',\\'escalate\\')">Escalate</button>' +
    '</div>';

  openDrawer(titleHtml, bodyHtml);
}

function stageDecision(seq, action) {
  if (!trusteeId || !trusteeId.trim()) {
    alert('Enter a Trustee ID at the top of the review queue before staging a decision.');
    return;
  }
  const note = (document.getElementById('dr-note') || {}).value || '';
  const corrected = (document.getElementById('dr-corrected') || {}).value || '';
  if (action === 'corrected_label' && !corrected.trim()) {
    alert('Provide the corrected intent text before staging a "Correct Label" decision.');
    return;
  }
  pendingDecisions.push({
    audit_seq: seq, trustee_id: trusteeId.trim(), action: action,
    note: note, corrected_intent_text: corrected, corrected_action: ''
  });
  updateStagedPanel();
  closeDrawer();
}

function updateStagedPanel() {
  let panel = document.getElementById('staged-panel');
  if (!panel) {
    panel = document.createElement('div');
    panel.id = 'staged-panel';
    panel.className = 'staged-panel';
    panel.innerHTML = '<span class="count"></span><span id="staged-list" style="flex:1;opacity:.85;"></span>' +
      '<button class="btn" style="background:transparent;color:white;border-color:#4c6488;" onclick="clearStaged()">Clear</button>' +
      '<button class="btn primary" onclick="exportStaged()">Export Review Decisions (JSON)</button>';
    document.body.appendChild(panel);
  }
  panel.classList.toggle('show', pendingDecisions.length > 0);
  panel.querySelector('.count').textContent = pendingDecisions.length + ' decision' + (pendingDecisions.length===1?'':'s') + ' staged';
  panel.querySelector('#staged-list').textContent = pendingDecisions.map(d => '#' + d.audit_seq + ' -> ' + d.action).join('   ');
}
function clearStaged() { pendingDecisions = []; updateStagedPanel(); }
function exportStaged() {
  if (!pendingDecisions.length) return;
  const blob = new Blob([JSON.stringify(pendingDecisions, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'hitl_decisions.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

renderFlow();
renderMorphism();
renderHitl();
"""
