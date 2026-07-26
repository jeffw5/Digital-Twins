"""
Governance Console -- the single consolidated deliverable that merges:

  - aicb/dashboard.py's THREE live-telemetry tabs (E2E Agent Flow, Live Morphism
    Evaluation, Training & Feedback / HITL) -- built from a running CircuitBreaker.
  - aicb/architecture_explorer.py's reference tabs (Value Points, Architecture Tier 1-4 /
    Part II, Governance Tuple H/O/V/A, Morphism Quadrant & Composition Theorem,
    Simulation, Glossary) -- built from the design documents.

into one self-contained HTML file with one shared tab nav, so a Trustee reviewing a
flagged event can, in the same window, jump to the reference material that explains
*why* a boundary's tolerance is set where it is, without losing their place.

Both source modules independently define the SAME generic drawer primitive
(`openDrawer(titleHtml, bodyHtml)` / `closeDrawer()` / the backdrop click listener), the
same `esc()` helper, and the same tab-button wiring -- they are byte-identical between
the two files by design, specifically so this module can treat dashboard.py's copies as
duplicates and drop them wholesale rather than reconciling two different
implementations. What's left to reconcile is narrower than it looks:

  1. dashboard.py's `const DATA` -> `LIVE_DATA` (and every reference to it), so it can't
     collide with architecture_explorer.py's own `const DATA` (the static reference
     payload keeps the `DATA` name -- it's the "default" namespace since most of this
     console's content is reference material).
  2. dashboard.py's live-telemetry `renderMorphism()` (d_S/d_M scatter of actual MER
     records, now with a forward/backward step-through) is renamed `renderLiveMorphism()`
     / `tab-live-morphism`, distinguishing it from architecture_explorer.py's
     `renderMorphism()` (the static quadrant map + Composition Theorem calculator),
     which keeps its original name and `tab-morphism` id.

Each transform is applied via an exact-substring `str.replace` against the *current*
source text of dashboard._JS, with an assertion that the expected substring is present --
if either source file's JS is edited later in a way that changes these specific blocks,
generating the console will raise loudly instead of silently producing broken JS.
"""
from __future__ import annotations

import html
import json

from . import architecture_explorer as _arch
from . import dashboard as _dash
from .breaker import CircuitBreaker


# ========================================================================================
# JS merge -- resolve the three collisions described above, once, at import time.
# ========================================================================================

def _prepare_live_js() -> str:
    js = _dash._JS

    # DATA -> LIVE_DATA, every whole-word occurrence (declaration + all reads).
    import re
    js = re.sub(r"\bDATA\b", "LIVE_DATA", js)

    # Drop dashboard's own tab-btn wiring -- architecture_explorer.py's identical wiring
    # (below) already covers all nine buttons since it selects '.tab-btn' generically.
    tab_wiring = """document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tabpanel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
  });
});

"""
    assert tab_wiring in js, "dashboard._JS tab wiring block drifted from expected text"
    js = js.replace(tab_wiring, "")

    # Drop dashboard's own esc() -- architecture_explorer.py provides an identical one.
    esc_fn = """function esc(s) {
  return String(s === undefined || s === null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
"""
    assert esc_fn in js, "dashboard._JS esc() drifted from expected text"
    js = js.replace(esc_fn, "")

    # Drop dashboard's own generic drawer primitive (openDrawer/closeDrawer/backdrop
    # listener) -- byte-identical to architecture_explorer.py's by design; dashboard.py's
    # openFlaggedEventDrawer(seq)/openLayerDrawer(tag)/openBoundaryDrawer(id) all call
    # into this shared primitive, so nothing else needs to change to make them work
    # against the ONE drawer element in the merged document.
    drawer_primitive = """function openDrawer(titleHtml, bodyHtml) {
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
"""
    assert drawer_primitive in js, "dashboard._JS drawer primitive drifted from architecture_explorer.py's copy"
    js = js.replace(drawer_primitive, "")

    # Rename the live-telemetry morphism renderer + its target element id so it can't
    # collide with architecture_explorer.py's reference renderMorphism()/tab-morphism.
    assert "function renderMorphism()" in js
    js = js.replace("function renderMorphism()", "function renderLiveMorphism()")
    assert "document.getElementById('tab-morphism')" in js
    js = js.replace("document.getElementById('tab-morphism')", "document.getElementById('tab-live-morphism')")
    assert "renderMorphism();" in js
    js = js.replace("renderMorphism();", "renderLiveMorphism();")

    return js


# Computed once at import time -- both source _JS strings are static, only the embedded
# DATA/LIVE_DATA JSON blobs vary per render() call.
#
# One extra `renderValuePoints();` is appended at the very end, after LIVE_DATA has been
# declared: the explorer's own init sequence (inside _arch._JS) already calls
# renderValuePoints() once, but at that point in the merged script LIVE_DATA is still a
# hoisted-but-uninitialized const from the *later* dashboard section (a JS variable is
# in its "temporal dead zone" until its own declaration line runs) -- renderValuePoints()
# handles that gracefully (see its try/catch around reading LIVE_DATA.status), but the
# Value Points tab's Overview banner can only show the live governance status once
# LIVE_DATA actually exists, so it needs one more render pass after that happens.
_MERGED_JS = (
    _arch._JS
    + "\n\n// ============================== LIVE TELEMETRY (from dashboard.py) ==============\n"
    + _prepare_live_js()
    + "\nrenderValuePoints(); // re-render now that LIVE_DATA exists, so Overview shows live status\n"
)

_TAB_SEP_CSS = """
  .tab-sep { display: inline-block; width: 1px; margin: 8px 10px; background: #2c3e5c; align-self: stretch; }
"""

_MERGED_CSS = _arch._CSS + "\n" + _dash._CSS + _TAB_SEP_CSS


# ========================================================================================
# render / write
# ========================================================================================

def render(breaker: CircuitBreaker, title: str = "AI Circuit Breaker -- Governance Console") -> str:
    live_payload = _dash._build_payload(breaker)
    explorer_payload = _arch._payload()

    status = live_payload["status"]
    g = live_payload["gauges"]

    gauges_html = "".join(
        [
            _dash._gauge_svg("Credibility", g["credibility"], green=0.85, alert=0.65),
            _dash._gauge_svg("Validity", g["validity"], green=0.90, alert=0.70),
            _dash._gauge_svg("Viability", g["viability"], green=0.80, alert=0.60),
            _dash._gauge_svg("Overall Trust", g["trust"], green=0.75, alert=0.55),
        ]
    )

    lockout_banner = ""
    if status["locked_out"]:
        lockout_banner = (
            f'<div class="banner">SOP-02 LOCKOUT ACTIVE &mdash; '
            f'{html.escape(status["lockout_reason"] or "")}. Autonomous operation halted '
            f'pending Trustee re-authorization.</div>'
        )

    live_json = json.dumps(live_payload, default=str)
    explorer_json = json.dumps(explorer_payload, default=str)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{html.escape(title)}</title>
<style>
{_MERGED_CSS}
</style>
</head>
<body>
<header>
  <h1>{html.escape(title)}</h1>
  <div class="sub">Live governance status, business model, and business domains are in the Value Points tab's Overview.</div>
</header>
{lockout_banner}

<nav class="tabs">
  <button class="tab-btn active" data-tab="value">Value Points</button>
  <span class="tab-sep"></span>
  <button class="tab-btn" data-tab="flow">E2E Agent Flow</button>
  <button class="tab-btn" data-tab="live-morphism">Live Morphism Evaluation</button>
  <button class="tab-btn" data-tab="hitl">Training &amp; Feedback (HITL)</button>
  <span class="tab-sep"></span>
  <button class="tab-btn" data-tab="architecture">Architecture (Tier 1-4 / Part II)</button>
  <button class="tab-btn" data-tab="tuple">Governance Tuple (H,O,V,A)</button>
  <button class="tab-btn" data-tab="morphism">Morphism Quadrant &amp; Composition Theorem</button>
  <button class="tab-btn" data-tab="simulation">Simulation</button>
  <button class="tab-btn" data-tab="glossary">Glossary</button>
</nav>

<div class="container">
  <div class="grid">
    <div class="card gauges">{gauges_html}</div>
    <div class="card stat"><div class="n">{status['mtbh_hours']:.2f} h</div><div class="l">MTBH</div></div>
    <div class="card stat"><div class="n">{status['total_hallucinations']}</div><div class="l">Total Trips</div></div>
    <div class="card stat"><div class="n">{status['flagged_for_review']}</div><div class="l">Flagged for Trustee Review</div></div>
    <div class="card stat"><div class="n">{status['htdr_entries']}</div><div class="l">HTDR Reviews Logged</div></div>
  </div>

  <section id="tab-value" class="tabpanel active"></section>

  <section id="tab-flow" class="tabpanel"></section>
  <section id="tab-live-morphism" class="tabpanel"></section>
  <section id="tab-hitl" class="tabpanel"></section>

  <section id="tab-architecture" class="tabpanel"></section>
  <section id="tab-tuple" class="tabpanel"></section>
  <section id="tab-morphism" class="tabpanel"></section>
  <section id="tab-simulation" class="tabpanel"></section>
  <section id="tab-glossary" class="tabpanel"></section>
</div>

<div id="drawer-backdrop" class="drawer-backdrop"></div>
<aside id="drawer" class="drawer"></aside>

<script id="explorer-data" type="application/json">{explorer_json}</script>
<script id="aicb-data" type="application/json">{live_json}</script>
<script>
{_MERGED_JS}
</script>
</body>
</html>"""


def write(breaker: CircuitBreaker, path: str, title: str = "AI Circuit Breaker -- Governance Console") -> str:
    content = render(breaker, title=title)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
