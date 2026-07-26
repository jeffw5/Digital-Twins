# AI Circuit Breaker -- Working Prototype

> **v2 update:** the dashboard is now a three-tab Trust Metrology console covering the
> full agent pipeline (E2E Flow), per-boundary morphism evaluation (d_S/d_M, Composition
> Theorem), and a Human-in-the-Loop review queue for digging into specific AI faults and
> making corrections. See "The v2 additions" below for what's new and how it maps to
> `morphism_assurance_v1.2.docx`.
>
> **v3 update:** added `architecture_explorer.html` -- a separate, static reference and
> simulation tool: every Tier 1 / Tier 2 (TB-02, TB-03, TB-04, TB-07b, TB-02/03, TB-06) /
> Part II component is clickable for its full detail design, a searchable glossary
> covers every term across all source documents, the morphism quadrant map has four
> distinctly colored regions with adjustable thresholds, the Composition Theorem has an
> interactive calculator, the Governance Quad-Tuple (H,O,V,A) is fully visualized, and a
> forward/backward stepper simulates an event traveling through L1-L5. See "The v3
> addition: Architecture Explorer" below.
>
> **v4 update:** three things. (1) `architecture_explorer.html` now also covers Tier 3
> (the four submission shells -- DARPA/SBIR/NSF-NIH/Defense Prime -- with their section
> maps and a cross-shell comparison table), Tier 4 (Qualifications, TRL Progression,
> Evaluation Plan, Commercialization), and the 15-figure Diagram Index -- the full
> breadth of `morphism_assurance_v1.2.docx`, not just Tier 1/2/Part II. (2) A new
> **Talking Points (Eric Ries)** tab incorporates the business/investor framing document
> -- the four HITL scenarios (advisory/investment/operations/strategy), the Lean-Startup
> Build-Measure-Learn parallel, the Multi-Agent Governance Hierarchy, and the
> reconciliation between this document's L1-L5 business labels and TB-02's L1-L5
> architecture labels (they are NOT the same scale -- see the glossary's disambiguation
> entry). (3) **`governance_console.html`** is a new, single consolidated deliverable
> that merges the live dashboard's three telemetry tabs with the explorer's six
> reference tabs into one nine-tab file, so a Trustee can dig into a flagged event and
> the reference material that explains its tolerance in the same window. See
> "The v4 addition: Governance Console" below.
>
> **v5 update:** the agent under governance is now named **AI Circuit Breaker** (the
> holon is `Wireless Communications - Edge Based Services Agent`) rather than "North
> Shore 5G Edge Agent," and every header now states the business model and business
> domains it's built for, right under the title. **Value Points** replaces **Talking
> Points (Eric Ries)** -- same content, but reframed around **Trustworthy
> Decision-Making Through Autonomous Automation** rather than one person's personal
> framing, folded together with the old Master Narrative hook/claims (no more
> duplication between the two), and moved to the **first** tab in every nav, since it's
> the entry point for a first-time reader. Three tabs gained real interactivity beyond
> v1-v4's static reference material: **E2E Agent Flow** -- every L1-L5 layer node and
> B1-B3 boundary node is now clickable, opening a detail drawer (function/invariant/
> what-to-watch-for for layers; structural+semantic check/tolerance rationale/
> evaluation history for boundaries) instead of just being a colored diagram. **Live
> Morphism Evaluation** -- a full Prev/Next/Play stepper walks through an agent's actual
> boundary-crossing history one MER at a time, highlighting the current point on the
> d_S/d_M scatter and its row in the table; click any row to jump straight to it.
> **Architecture** gained a new **System Diagram** sub-tab -- every component (the
> governed Agent, L1-L5, the knowledge/vector stores, SHACL/MCP/PROV-O integration
> points, analytics, the console itself) is a clickable node showing its detail design
> and its API/integration protocol, with the wiring between them drawn as labeled edges.
> Last, the **Glossary** is now a genuine vocabulary export rather than a flat
> alphabetical list: 103 terms across 9 named vocabularies (core, architecture,
> morphism, governance-tuple, hitl, value, regulatory, program, tooling), each with a
> synthesized IRI (`https://aicb.dev/vocab/{vocabulary}#{term}`) and a `broader` parent
> IRI, presented as a Vocabulary > Category > Term tree so you can see a term's
> parentage as you step through it -- click any term for its full IRI, breadcrumb, and
> (where one exists) its broader/parent term. See "The v5 additions" below.
>
> **v6 update:** two things, both sourced from the underlying documentation rather than
> newly authored. (1) **Tier 1** now renders Figure 1 from `morphism_assurance_v1.2.docx`
> in full -- the source document's own "component content system" diagram, showing every
> one of its 18 components in one view: the Master Narrative, all **nine** Tier 2
> technical blocks (TB-01 Morphism through Part II Tooling -- two of these, TB-01 and
> TB-05, are newly added; only 6 of the 9 existed as explorable blocks before v6), all
> four Tier 3 submission shells, and all four Tier 4 gap blocks. Every box is clickable
> for a summary and a one-click jump to that component's full page -- this is the "so I
> can see all the components" solution architecture view. (2) Every clickable component
> across TB-02 (L1-L5 layers), TB-03 (d_S/d_M metrics), TB-04 (F1-F4 ECG boundaries),
> TB-06 (five provenance record types), and TB-07b (the Wymore 7-tuple) now opens a
> drawer with a full description AND a concrete worked example pulled directly from
> `Technical Design ECG AI Circuit Breaker.pdf` -- the ECG-specific trip logic, the
> AAMI beat-classification mapping, the four hard-coded "impossible state" ontology
> guardrails, the Knowledge Fabric technology stack, and the SOP-02 Triple-Trip Lockout
> protocol, cited by section. TB-05's own technical content was never fully drafted in
> the source material (the Master Narrative says as much of itself), so it's included
> as a short, honestly-scoped placeholder rather than padded out with invented detail.
> See "The v6 additions" below.
>
> **v7 update:** the Diagram Index's 15 rows are no longer text-only -- every one now has
> a **View** link that opens a real diagram. Figures 1 and 3 already have full live
> interactive tabs elsewhere in the explorer (the Tier 1 Figure-1 diagram, the Morphism
> Quadrant tab), so their View link jumps straight there instead of duplicating them. The
> other 13 (five-layer architecture, ECG boundary chain, Wymore map, CB/ML interface
> paths, provenance-to-regulation mapping, tooling stack, all four Tier 3 volume maps,
> TRL timeline, evaluation-plan chains, and the commercialization map) each open a
> compact SVG diagram built live from the same structured data already documented on
> that figure's own page -- no new content invented, just visualized. See "The v7
> addition" below.
>
> **v8 update:** the masthead paragraph every file used to show under its title --
> Holon / Ontology / Handshake / Decision chain / HTDR chain / Reference material, plus
> Business model and Business domains -- has moved into a new **Overview** section at
> the very top of the Value Points tab, visible the moment that (now-first) tab opens
> rather than sitting above all nine tabs regardless of which one is active. The
> masthead itself is now a single short line pointing to it. `governance_console.html`'s
> Overview shows the full live status line plus the business summary; the standalone
> `architecture_explorer.html` (which has no running `CircuitBreaker` to report live
> status for) shows the business summary only. Fixing this exposed and fixed a real
> temporal-dead-zone bug in the merged console's script -- see "The v8 addition" below.

A domain-agnostic, dependency-light "deterministic veto" governance layer, built from
the design specification and supporting documentation (design spec Sections 1-3, the
ECG technical design document, the SE4AI abstract, and the Governance Quad-Tuple
addendum). It is built to be **inserted in front of, or inside of, any AI model or
agent** without modifying that model.

## What this is

Every AI-proposed action is scored against a deterministic ground truth *before* it is
allowed to execute. If the gap between what the AI intends and what the ontology + live
sensor/context data say is true exceeds an engineered tolerance, the breaker trips and
the system falls back to a graduated safe state (soft alert -> hold -> halt -> lockout)
instead of letting the action through. This is "Observability-First": trust is a
measured engineering property, not a confidence score the model reports about itself.

## Architecture: the Governance Quad-Tuple (H, O, V, A)

Per Addendum A, a circuit breaker can't be correctly built from a subset of four
co-defined components. This prototype implements all four as first-class objects:

| Element | Module | What it is |
|---|---|---|
| **H** - Holonic Boundary | `aicb.tuple_config.HolonicBoundary` | This agent's authority envelope (allowed/forbidden actions, risk tiers) and escalation topology. Distinguishes "near the edge of my authority" from "outside my authority entirely." |
| **O** - Domain Ontology | `aicb.tuple_config.DomainOntology` | Reference ("known-good") assertions that define the valid-state centroid, plus hard `OntologyRule` constraints that define physically/logically impossible states. |
| **V** - Vector Context Store | `aicb.tuple_config.VectorContextStore` | Live scenario context and the historical decision distribution used to calibrate SPC control limits -- without it, thresholds are theoretical, not measured. |
| **A** - Domain Agent | *any callable* | The model/agent being governed. Never subclassed or modified -- adapted via two small functions (see Insertion API below). |

These four are assembled into a `CircuitBreaker(holon, ontology, vector_store, config)`.

## The five subsystems / five-layer measurement architecture

Mapped from the design spec and abstract onto the code:

1. **Semantic Knowledge Layer** -> `DomainOntology` (Section 1, Subsystem 1)
2. **Context Engine** -> `VectorContextStore` + `GroundTruth` (Subsystem 2)
3. **AI Circuit Breaker / The Veto Gate** -> `CircuitBreaker.evaluate()` (Subsystem 3)
4. **Recursive Learning & Model Governance** -> `CircuitBreaker.recursive_learning_batch()`, `propose_ontology_enhancements()` (Subsystem 4, SOP-03)
5. **Human Interaction / Underwriting** -> `aicb.dashboard` + `resume_from_lockout()` (Subsystem 5)

Layer 3 (Statistical Control) additionally implements a subset of Western Electric
rules (`aicb.spc`) so that thresholds aren't purely guessed static numbers once enough
history exists (cold-start = 25 observations, per the abstract's Phase I target).

## Metrics implemented (Section 2 of the design spec)

All in `aicb/metrics.py`, pure functions, unit-tested in `tests/test_breaker.py`:

- **Semantic Anomaly Score (Sa)** = `1 - cos(Intent Vector, Ontology Centroid)`. Trip ceiling default `0.15`.
- **Contextual Relevancy Index (Cr)** = weighted `1 - |AI context - sensor ground truth|`. Trip floor default `0.85`.
- **Mean Time Between Hallucinations (MTBH)** = operational time / trip count.
- **Human-AI Calibration Coefficient (Ktrust)** = AI health / human cognitive load. Lockdown floor `0.5`.
- **Value-Drift Coefficient (VDC)** and **Composite Trust Index** (Credibility 0.35 / Validity 0.40 / Viability 0.25, from the ECG technical design doc's dashboard weighting).

Embeddings are produced by a **deterministic, dependency-free feature-hashing
transform** (`aicb/vectorize.py`) rather than a second learned model -- a governance
layer that is itself an opaque neural net doesn't actually solve the trust problem, it
relocates it. Swap in a real sentence-embedding model at that one seam if you want
richer semantics; nothing else in the package needs to change.

## The Veto Gate: trip logic

Directly implements the ECG technical design doc's core trip logic, generalized:

```
IF   action is outside the holon's authority envelope (H)             -> HALT (hard trip)
OR   an ontology impossible-state rule is violated (O, severity 3)    -> HALT (hard trip)
OR   Semantic Anomaly Score >= ceiling
OR   Contextual Relevancy Index < minimum
OR   Composite Trust Index < minimum
OR   Human-AI Calibration Coefficient < lockdown floor
OR   SPC detects statistically significant drift (Layer 3)
THEN trip the breaker, select a safe-state level, exclude the epoch from training (SOP-03),
     log a hash-chained audit entry (Layer 5)
ELSE transmit the AI's action, attach trust metadata
```

Three safe-state levels plus a lockout state, matching the ECG doc's Three-Level Safe
State Activation and SOP-02 Triple-Trip Lockout:

- **Level 1 -- Soft Alert**: action proceeds, flagged for review.
- **Level 2 -- Hold**: action withheld, human review required.
- **Level 3 -- Halt**: autonomous operation for this action stops.
- **Lockout (SOP-02)**: 3+ trips in a 10-minute window locks out *all* autonomous
  operation for the holon until a human Trustee calls `resume_from_lockout()`.

## Insertion API -- how you actually plug this into a model or agent

Two patterns, both adapter-based so the breaker never needs to know anything about your
model's internals:

### 1. Decorator, for single-shot calls (LLM completion, classifier, etc.)

```python
from aicb.insert import protect

@protect(breaker, to_assertion=my_output_adapter, to_ground_truth=my_sensor_fn, on_trip="raise")
def call_llm(prompt: str) -> str:
    return my_llm_client.complete(prompt)   # any SDK -- OpenAI, Anthropic, local model, etc.

result = call_llm("reroute traffic through node 7")
result.output          # original return value (only reachable if not tripped, or on_trip != "raise")
result.trust_metadata  # Sa, Cr, trust_index, decision, audit hash, ...
```

### 2. `ToolGate`, for agent tool-calling loops (LangChain/AutoGen/MCP/custom ReAct)

```python
from aicb.insert import ToolGate

gate = ToolGate(breaker, to_assertion=my_tool_adapter, to_ground_truth=my_sensor_fn)
result = gate.guard(tool_name, tool_args, executor=real_tool_executor)
# real_tool_executor is only called if the breaker allows it -- true PRE-execution veto
```

In both cases the only integration work is writing two small functions that map your
model's inputs/outputs into `AgentAssertion` (what the AI is proposing) and
`GroundTruth` (what the deterministic sensors/context actually say). That's the entire
integration surface -- the breaker is otherwise blind to what kind of model it's
governing.

## The v2 additions: morphism evaluation + Training & Feedback (HITL)

Built from `morphism_assurance_v1.2.docx` ("Morphism-Grounded Compositional Assurance"),
which reframes the same architecture in more formal terms: a two-axis morphism distance
(d_S structural, d_M semantic) evaluated at every boundary an agent's pipeline crosses,
a Composition Theorem showing fidelity degrades *multiplicatively* across boundaries
(phi(Fn ... F1) >= prod(phi(Fi))), and a five-layer containment model (L1 Ground Truth,
L2 Functor Certification, L3 Consistency Manager, L4 Circuit Breaker + Monitor, L5 Human
Trustee) with five provenance record types (MER, CBER, SR, CER, HTDR).

| Doc concept | Code |
|---|---|
| Boundary (F_i), tau_S/tau_M/w_c | `aicb.morphism.Boundary` |
| d_S / d_M / Functor Certification | `aicb.morphism.structural_distance`, `semantic_distance`, `MorphismChain.evaluate_pass` |
| MER (Morphism Evaluation Record) | `aicb.morphism.MorphismEvaluationRecord` |
| Composition Theorem (hidden loss) | `aicb.morphism.PassResult.hidden_loss` |
| HTDR (Human Trustee Decision Record) | `aicb.hitl.HTDR`, `aicb.hitl.ReviewLog` |
| L5 Human Trustee digging into a fault and correcting it | `CircuitBreaker.review_flagged_event()` |

Two things worth calling out about how this was implemented:

- **The decision audit trail (L4) and the review log (L5) are two separate hash chains.**
  A human correcting a flagged event never edits the original tamper-evident decision
  record -- it appends a new HTDR that references it by sequence number. `CircuitBreaker.
  effective_recursive_learning_batch()` joins the two at read time. This is the standard
  pattern for regulated systems: corrections are new events, not edits to history.
- **A "Corrected Label" review writes directly into the ontology.** `review_flagged_event(...,
  action="corrected_label", corrected_intent_text=...)` calls
  `ontology.add_reference_assertion(...)` -- the human's correction becomes part of what
  the breaker considers "known-good" going forward. That's the actual "make corrections"
  mechanism, not just a note in a log.

### The dashboard's three tabs

`trust_dashboard.html` is a single self-contained file (still zero external
dependencies/CDNs) with three views, switchable via the top nav:

1. **E2E Agent Flow** -- the L1-L5 containment diagram, live-colored by current state,
   plus (if a `MorphismChain` is attached) the agent's pipeline boundary chain showing
   each boundary's latest certification result. Since v5, every L1-L5 layer node and
   B1-B3 boundary node is clickable, opening a drill-down drawer: layers show their
   function/invariant/what-to-watch-for; boundaries show their structural + semantic
   check, why their tau_S/tau_M/w_c tolerances are set where they are, and their full
   evaluation history.
2. **Live Morphism Evaluation** -- a d_S/d_M quadrant scatter plot (one point per MER,
   dashed rectangles marking each boundary's tau_S x tau_M certification region), the MER
   table, and a Composition Theorem panel comparing composed (correct) fidelity against
   the naive per-boundary average so the "hidden loss" is visible, not just asserted.
   Since v5, it's step-through interactive: Prev/Next/Play walk through the agent's
   actual boundary-crossing history one MER at a time, highlighting the current point on
   the scatter and its row in the table; click any row to jump straight to it.
3. **Training & Feedback (Human-in-the-Loop)** -- the Trustee review queue: every
   flagged/tripped event, clickable to a full detail drawer (reasons, metrics, raw
   intent, prior reviews). From there a Trustee can stage one of four actions --
   **Confirm Hallucination**, **Override (False Positive)**, **Correct Label & Add to
   Ontology**, or **Escalate** -- and export the staged batch as `hitl_decisions.json`.

### Closing the loop: dashboard -> apply -> dashboard

The dashboard is a static file, so staged HITL decisions are *exported*, not applied
live. `examples/apply_hitl_review.py` is the other half: it deterministically replays
the same scenario set (so audit sequence numbers line up), applies each decision via
`CircuitBreaker.review_flagged_event(...)`, and regenerates the dashboard so the
correction is now visible -- the review queue shows it as reviewed, the ontology has
grown if it was a correction, and `effective_recursive_learning_batch()` reflects the
new training-eligible/purged split.

```bash
python3 examples/pipeline_review_demo.py           # -> trust_dashboard.html (unreviewed queue)
#   ...open it, dig into flagged events, stage decisions, click "Export Review Decisions (JSON)"...
python3 examples/apply_hitl_review.py hitl_decisions.json   # applies the export, regenerates the dashboard
#   (or, with no argument, apply_hitl_review.py applies a built-in sample batch so the
#    whole loop is runnable and demonstrable without a browser)
```

## The v3 addition: Architecture Explorer

`architecture_explorer.html` is a companion, purely static reference tool -- it has no
connection to a live `CircuitBreaker` instance, unlike `trust_dashboard.html`. It exists
to answer "what IS this architecture, in detail" rather than "what is this specific
breaker doing right now." Six tabs:

1. **Architecture (Tier 1-4 / Part II)** -- a pill-nav across the Master Narrative (since
   v5, its hook/claims live in Value Points -- this sub-tab is now a short redirect plus
   whatever isn't better said there, followed since v6 by **Figure 1**, the source
   document's own full "component content system" diagram: 18 clickable boxes covering
   the Master Narrative, all **nine** Tier 2 technical blocks, all four Tier 3 submission
   shells, and all four Tier 4 gap blocks in one view, each opening a summary + a
   one-click jump to its full page), a **System Diagram** (since v5: every component --
   the governed Agent, L1-L5, knowledge/vector stores, SHACL/MCP/PROV-O integration
   points, analytics, the console -- is a clickable node opening a drawer with its detail
   design and its API/integration protocol, wired together with labeled edges), all
   **nine** Tier 2 technical blocks (TB-01 Morphism, TB-02 Architecture, TB-03 Metrics,
   TB-04 Domain/ECG, TB-05 ML/Bayesian, TB-06 Provenance, TB-07b Wymore, TB-02/03 CB/ML
   Interface, and Part II Tooling -- since v6, all nine are fully explorable; TB-01 and
   TB-05 are new), **Tier 3** (the four submission shells -- DARPA BAA, DoD SBIR/STTR,
   NSF/NIH, Defense Prime RFP -- each with its section-by-section map and pagination,
   plus a cross-shell comparison table showing how every Tier-2 block is
   weighted/reframed/omitted per shell), **Tier 4** (Qualifications & Team, TRL
   Progression, Evaluation Plan & Metrics, Commercialization & Transition), the 15-figure
   **Diagram Index** (every figure in the source doc, with its location, purpose, and --
   since v7 -- a **View** link that opens a real diagram for it: figures 1 and 3 jump to
   their own live interactive tabs, the other 13 open a compact SVG built from the same
   data documented on that figure's page), and Part II's tooling inventory. Every
   component (each L1-L5 layer in TB-02, each metric in
   TB-03, each F1-F4 boundary in TB-04, each Wymore-tuple symbol in TB-07b, each record
   type in TB-06, each novel claim in TB-01) is a clickable card that opens a detail
   drawer with its full function/invariant, and -- since v6 -- a full description AND a
   concrete worked example sourced from `Technical Design ECG AI Circuit Breaker.pdf`
   (the ECG-specific trip logic, AAMI beat-classification mapping, hard-coded
   impossible-state ontology guardrails, Knowledge Fabric technology stack, and SOP-02
   Triple-Trip Lockout protocol, cited by section). TB-05's page is deliberately left as a
   short summary rather than padded out, since its technical content was never fully
   drafted in the source material. Part II's tooling table is cross-referenced from the
   companion Technical Design Document's Knowledge Fabric stack, since the source doc's
   Part II gives only a summary count (23 components, TRL 7+) without naming all of them
   -- the explorer is explicit about which entries are named vs. summarized.
2. **Governance Tuple (H,O,V,A)** -- the four-node tuple diagram (fully interconnected,
   not a stack/pipeline, per the Addendum's own argument for why), each node clickable
   for its full definition / "without it" failure mode / CB-layer dependency; the
   Stack-vs-Pipeline-vs-Menu-vs-Tuple comparison; the full tuple-completeness table (what
   breaks with every partial-tuple combination); the version-lock deployment rule; and
   the Lean Startup structural-equivalence framing.
3. **Morphism Quadrant & Composition Theorem** -- the four-box d_S/d_M matrix with a
   distinct color per quadrant (Ideal / Precise-but-Wrong / Coarse-but-Safe / Divergent,
   per the SE4AI abstract's Fig. 2 framing), draggable tau_S/tau_M sliders that move the
   certification boundary live, click-to-test-a-point interaction, and a Composition
   Theorem calculator (adjustable chain length + per-layer fidelity) that bar-charts the
   naive per-layer average against the true composed fidelity so the "hidden loss" is
   visible, not just asserted.
4. **Simulation** -- forward/backward step-through of an event traveling L1 -> L2 -> L3
   -> L4 -> L5, with two worked scenarios: a clean certified pass, and a pass where Layer
   2 (Functor Certification) catches a semantic hallucination that Layer 3's ontology
   check alone would have missed -- illustrating why the layers are complementary, not
   redundant. Click any layer node to jump directly to that step, or use Forward/Back.
5. **Value Points** -- since v5, this is the first tab in every nav: the business/
   investor framing document, reframed around Trustworthy Decision-Making Through
   Autonomous Automation (not one person's personal thesis), with the old Master
   Narrative hook and its three foundational claims folded straight into the thesis
   sub-tab (no separate, redundant claims section in Architecture anymore). Since v8, it
   opens with an **Overview** banner (live governance status, business model, and
   business domains -- moved here from the top masthead; see "The v8 addition" below),
   followed by its own sub-tabbed section: the thesis + foundational claims, four worked
   HITL scenarios (advisory / investment / operations / strategy, each with its own
   five-vector risk profile and escalation path), the five-layer business-framing stack
   (Reference Standard / Measurement Engine / Statistical Process Control / Holonic
   Immune Response / Provenance Audit Trail) with an explicit reconciliation to TB-02's
   differently-labeled L1-L5, the Multi-Agent Governance Hierarchy (Individual Agent CB
   -> Domain Cluster CB -> Enterprise Orchestrator CB -> HITL Governance Board) and its
   cross-agent mechanisms (Irreversibility Firewall, Global Trust Budget, Behavioral
   Entropy Monitor), the tailoring/tuning loop, HITL roles and review cadence, and a
   closing summary (business model/domains now live in the Overview above, not repeated
   here).
6. **Glossary** -- since v5, a genuine vocabulary export rather than a flat alphabetical
   list: 103 terms across 9 named vocabularies (core, architecture, morphism,
   governance-tuple, hitl, value, regulatory, program, tooling), spanning every term used
   across this project's source documents (design spec, ECG technical design doc, SE4AI
   abstract, morphism assurance doc, the quad-tuple addendum, and the Value Points
   document). Each term carries a synthesized IRI
   (`https://aicb.dev/vocab/{vocabulary}#{term}`) and a `broader` parent IRI -- either a
   default Vocabulary > Category parent, or, where one document's term is genuinely a
   specialization of another (e.g. "MTBH (business framing)" is a child of the core
   "MTBH" term, not just a category-sibling), an explicit term-to-term parent. Rendered
   as an expandable Vocabulary > Category > Term tree so you can see a term's parentage
   as you step through it; click any term for its full IRI, breadcrumb, aliases, and
   broader term. Live-searchable across term/definition/alias/IRI, with explicit
   disambiguation where documents reuse the same short name for different things -- most
   notably, **four** distinct "L1-L5"-shaped scales appear across the source material
   (TB-02's Architecture Layers, Value Points' business-framing relabeling of that same
   stack, Value Points' separate Multi-Agent Governance Hierarchy, and the SE4AI
   abstract's Context Assurance Levels) and are called out explicitly in one glossary
   entry so they don't get conflated.

Generate/regenerate it with:

```bash
python3 examples/generate_architecture_explorer.py   # -> architecture_explorer.html
```

The content lives in `aicb/architecture_explorer.py` as plain Python data structures
(`GLOSSARY`, `TUPLE_ELEMENTS`, `TIER2_BLOCKS`, `TIER3_SHELLS`, `TIER4_BLOCKS`,
`DIAGRAM_INDEX`, `PART2_TOOLING`, `QUADRANTS`, `SIMULATION_SCENARIOS`, `TALKING_POINTS`,
etc.) rather than being buried in an HTML string, so it's the place to edit if the source
documents are revised or extended.

## The v4 addition: Governance Console

`governance_console.html` merges everything above into one file: **Value Points** first
(since v5 -- it's the entry point for a first-time reader), then the live dashboard's
three telemetry tabs (E2E Agent Flow, Live Morphism Evaluation, Training & Feedback /
HITL), then the explorer's remaining five reference tabs (Architecture, Governance
Tuple, Morphism Quadrant & Composition Theorem, Simulation, Glossary), under one shared
tab nav -- nine tabs total, one file. It's generated by `aicb/console.py`, which does
*not* re-implement either tab set; it imports `aicb/dashboard.py` and
`aicb/architecture_explorer.py`'s already-verified CSS/JS/render logic directly and
applies a small set of explicit, assertion-guarded text transforms to resolve the three
naming collisions that come from combining two independently-built single-page tools:

1. Both scripts declared `const DATA`. The live payload becomes `LIVE_DATA`; the static
   reference payload keeps `DATA`.
2. Both scripts defined a function called `openDrawer`, with different signatures. The
   dashboard's per-flagged-event version is refactored into `openFlaggedEventDrawer(seq)`,
   which builds its title/body HTML and calls the explorer's generic `openDrawer(titleHtml,
   bodyHtml)` -- there's now exactly one drawer primitive shared by all nine tabs (a
   Trustee reviewing a flagged event and a user browsing the TB-04 boundary reference
   table get the same slide-out panel).
3. Both scripts defined a function called `renderMorphism()`, targeting different tab
   ids (`tab-morphism`) with different content -- one a live MER scatter plot, the other
   the static quadrant map. The live one is renamed `renderLiveMorphism()` /
   `tab-live-morphism`; the reference one keeps its original name and id.

Every transform is an exact-substring replace guarded by an `assert` against the source
text it expects -- if `dashboard.py`'s JS is ever edited in a way that changes one of
these specific blocks, generating the console raises immediately instead of silently
shipping broken JS. Since v5, both source files also share the same generic drawer
primitive byte-for-byte by design (`openDrawer`/`closeDrawer`/backdrop listener), so the
merge can drop dashboard.py's copy as a pure duplicate instead of reconciling two
different implementations. This was verified with a headless Node harness that executes
the merged script end-to-end -- all six Value Points sub-tabs and all four scenario ids,
every Architecture block including the new System Diagram's 13 clickable nodes, the
Governance Tuple / Morphism Quadrant / Simulation reference tabs, the Glossary tree
render plus a term-drawer click for all 103 terms, the E2E Agent Flow's layer + boundary
drill-down drawers, the Live Morphism stepper (forward, backward, and row-click-to-jump
across all records, including clamping past both ends), and the HITL flagged-event
drawer -- with zero runtime errors.

Generate/regenerate it with:

```bash
python3 examples/pipeline_review_demo.py   # writes trust_dashboard.html AND governance_console.html
python3 examples/apply_hitl_review.py      # regenerates both, with review history applied
```

## The v5 and v6 additions: naming, Value Points, and interactivity

**v5** renamed the governed agent from "North Shore 5G Edge Agent" to **AI Circuit
Breaker** and its holon to `Wireless Communications - Edge Based Services Agent`, added
a business model + business domains line under every file's header, replaced **Talking
Points (Eric Ries)** with **Value Points** (same content, reframed around Trustworthy
Decision-Making Through Autonomous Automation, with the old Master Narrative hook and
its three foundational claims folded straight in -- no more duplication between the
two), and moved Value Points to the first tab in every nav. It also made three
previously-static tabs interactive: **E2E Agent Flow**'s L1-L5 layer and B1-B3 boundary
nodes are clickable drill-down drawers; **Live Morphism Evaluation** got a full
Prev/Next/Play stepper through an agent's actual boundary-crossing history; and
**Architecture** gained a clickable **System Diagram** covering the governed Agent,
L1-L5, the knowledge/vector stores, and their integration protocols.

**v6** answers two follow-up asks about the Architecture tab specifically, both pulled
from the underlying documentation rather than newly authored:

1. **Tier 1 now shows the full solution architecture diagram.** `morphism_assurance_v1.2.docx`'s
   own Diagram Index describes Figure 1 as "Component content system -- four-tier
   architecture overview showing MN, nine technical blocks, four submission shells, and
   four gap blocks" -- that figure, not a redirect note, is now what Tier 1 renders: all
   18 components in one clickable diagram, each opening a summary and a one-click jump
   to its full page. Building it honestly required first fixing a gap it exposed: only 6
   of the source document's own nine Tier 2 technical blocks had ever been built out as
   explorable pages. **TB-01** (Morphism-Grounded Compositional Assurance -- the
   Composition Theorem and the Master Narrative's three novel claims) and **TB-05**
   (Probabilistic Functors and Belief Revision) are new. TB-05's own technical exposition
   was never fully drafted in the source material -- the Master Narrative says as much of
   its own claims -- so its page is a short, honestly-scoped summary rather than invented
   detail; every other block's content is sourced directly from the documentation.
2. **Every TB component's drawer now has a full description AND a worked example.**
   Previously several components (TB-03's metrics, TB-04's boundaries, TB-07b's Wymore
   symbols, TB-06's record types) rendered with blank or minimal detail in their drawers
   due to a field-naming mismatch between the data and the renderer -- fixed as part of
   this pass. Every component across TB-02, TB-03, TB-04, TB-06, and TB-07b now carries a
   full paragraph description plus a concrete worked example cited to a specific section
   of `Technical Design ECG AI Circuit Breaker.pdf`: the ECG-specific circuit-breaker
   trip logic and its numeric thresholds, the AAMI 5-category beat-classification
   mapping, the four hard-coded "impossible state" ontology guardrails (e.g. a
   ventricular rate over 300 bpm without documented pre-excitation), the Knowledge Fabric
   technology stack (GraphDB, Metaphactory, MCP), and the SOP-02 Triple-Trip Lockout
   protocol. TB-02/03 also gained three new named components (Primary Inference Path,
   Semantic Guardrail Trigger Path, L5 Escalation Path) describing the parallel-path
   architecture its summary paragraph described but never broke into clickable pieces.

Verified with the same headless Node harness used for every prior round, extended to
click through all 18 Tier 1 diagram nodes and every component across all nine Tier 2
blocks, confirming each has both a description and an example -- zero runtime errors.

## The v7 addition: a real diagram behind every Diagram Index entry

Before v7, the Diagram Index tab was a text-only table -- 15 rows naming a figure, its
location, and its purpose, with no actual diagram attached. Every row now has a **View**
link that opens one:

- **Figures 1 and 3** already have full, live interactive diagrams elsewhere in this
  explorer -- Figure 1 is the Tier 1 tab's Figure-1 solution architecture diagram (added
  in v6), Figure 3 is the Morphism Quadrant tab's draggable quadrant map. Duplicating
  them as flat pictures would just be a worse copy of something already one click away,
  so their View link jumps straight to that live tab instead.
- **The other 13 figures** (five-layer architecture, ECG boundary chain, Wymore
  correspondence map, CB/ML interface's three parallel paths, provenance-to-regulation
  mapping, tooling stack by layer, all four Tier 3 submission-shell volume maps, TRL
  progression timeline, evaluation-plan chains, and the commercialization map) each open
  a compact inline SVG diagram -- a vertical stack of labeled, color-coded boxes (chained
  with connecting arrows where the figure describes a sequence, e.g. the ECG boundary
  chain or the TRL timeline). Every diagram is generated live from the exact same
  structured data already documented on that figure's own Architecture-tab page (TB-02's
  layer list, TB-04's boundary table, TB-06's record-to-regulation mapping, the Tier 3
  shells' section maps, and the Tier 4 gap blocks' rows/paths) -- nothing new was
  authored, this is a visualization of facts already on the page, just made visible as a
  diagram instead of only as a table row. The one shell without a section-level table
  (NSF/NIH, Shell 3) falls back to splitting its existing comparison note into per-sentence
  cards rather than fabricating a section breakdown that was never in the source data.

Verified by clicking every one of the 15 View links (confirming figures 1 and 3 open
their live-tab jump buttons and that clicking them actually navigates, and confirming
each of the other 13 produces a non-empty diagram) through the same headless Node
harness -- zero runtime errors.

## The v8 addition: an Overview at the top of Value Points

Every file's masthead used to carry a growing paragraph under the title -- the live
Holon/Ontology/Handshake/Decision-chain/HTDR-chain status line (governance_console.html
only) plus Business model and Business domains (all three HTML files) -- shown above
whichever of the nine tabs happened to be open. That content now lives in a single
**Overview** block at the very top of the Value Points tab instead, above its own
sub-tab nav, so it shows once, at the actual entry point, rather than repeating above
every tab regardless of relevance. The masthead is now one short line pointing there.
`governance_console.html`'s Overview shows both the live status line and the business
summary; `architecture_explorer.html` (no running `CircuitBreaker`, so no live status to
show) renders the business summary only -- `renderValuePoints()` detects which case it's
in by whether `LIVE_DATA` is available, not by which file it's running in, so the same
function correctly serves both.

Moving this exposed a real bug, not just a cosmetic one: `governance_console.html` is
`aicb/architecture_explorer.py`'s script with `aicb/dashboard.py`'s script appended
after it, and the explorer's own script already calls `renderValuePoints()` as part of
its normal startup sequence -- which now runs *before* the appended dashboard section's
`const LIVE_DATA = ...` has executed. In JavaScript, a `const`/`let` is hoisted to the
top of its scope but left in a "temporal dead zone" until its declaration line actually
runs -- so simply checking `typeof LIVE_DATA !== 'undefined'` still threw a
`ReferenceError` at that point, which the headless test caught immediately on the first
regenerate. Fixed two ways: `renderValuePoints()` now reads `LIVE_DATA.status` inside a
try/catch instead of a `typeof` guard (both "never declared" in the standalone explorer
and "not yet initialized" in the console are ordinary, catchable `ReferenceError`s), and
`aicb/console.py`'s merge appends one extra `renderValuePoints();` call at the very end
of the combined script, after `LIVE_DATA` truly exists, so the Overview's final,
displayed state is always the fully-live one.

Verified with the same headless harness, extended to load each file's full script (not
just call individual functions -- this is what originally caught the temporal-dead-zone
bug), confirm the Overview appears with the live status line and business summary in
the console but business-summary-only in the standalone explorer, and confirm neither
masthead paragraph reappears in the raw `<header>` HTML -- zero runtime errors.

## Running the prototype

```bash
pip install -r requirements.txt   # numpy only
python3 tests/test_breaker.py               # unit tests, no network/API needed
python3 examples/pipeline_review_demo.py    # FLAGSHIP demo: full E2E pipeline with morphism
                                             # evaluation across boundaries -> writes
                                             # trust_dashboard.html AND governance_console.html,
                                             # both with an unreviewed HITL queue
python3 examples/apply_hitl_review.py       # applies a sample Trustee review batch, shows the
                                             # before/after SOP-03 split, regenerates BOTH files
python3 examples/network_ops_demo.py        # simpler Sa/Cr-only version (no morphism/HITL)
                                             # -> writes network_ops_dashboard_basic.html
python3 examples/tool_gate_demo.py          # pre-execution veto in a tool-calling loop
python3 examples/generic_llm_wrapper.py     # decorator pattern in front of a (fake) LLM client
python3 examples/generate_architecture_explorer.py   # -> architecture_explorer.html (static reference + simulation)
```

Open `governance_console.html` for the full experience in one file: gauges (Credibility
/ Validity / Viability / Overall Trust) and MTBH; the Value Points tab's Overview shows
the live governance status plus the business model and domains (see "The v8 addition"
above); and all nine tabs, Value Points first -- Value Points, E2E Flow, Live Morphism
Evaluation, Training & Feedback (HITL), Architecture (Tier 1-4/Part II), Governance
Tuple, Morphism Quadrant & Composition Theorem,
Simulation, and Glossary. `trust_dashboard.html` (live tabs only) and
`architecture_explorer.html` (reference tabs only) remain available as the smaller,
focused single-purpose files if you don't need the combined view.

## What's deliberately simplified vs. the full design

This is a working prototype, not the production system described in the abstract's
five-layer architecture:

- Ontology rules are Python predicates, not OWL 2 DL + SHACL/SWRL. The `OntologyRule`
  interface is the seam where a real reasoner (e.g. GraphDB + SHACL validation) would
  plug in without changing the breaker's evaluation logic.
- Embeddings are a deterministic hashing transform, not a domain-tuned sentence-embedding
  model or the vector-DB-backed semantic neighborhood described in Subsystem 1.
- The three-axis morphism distance (D_s, D_b, D_r) and STPA/STAMP unsafe-control-action /
  non-stationary-UCA-space detection from the SE4AI abstract are not implemented; Sa/Cr
  here are a practical two-axis approximation (semantic + contextual) of that richer model.
- The holonic immune system (cross-holon metastatic-pattern surveillance across a
  holarchy of agents) is represented only as a single `HolonicBoundary` per breaker
  instance -- multi-agent holarchy composition is a natural next step, not built here.
- The audit trail is an in-memory hash chain, not a PROV-O/SPARQL-queryable store or
  WORM-backed ledger.
- d_S (structural distance) is a normalized-feature-diff approximation, not a true
  graph-edit-distance over the pipeline's actual intermediate representations; in this
  demo the per-boundary (d_S, d_M) pairs are hand-set to tell a legible story rather
  than computed from real intermediate agent state (`aicb.morphism.structural_distance`
  is ready to receive real structural feature dicts once a pipeline has them).
- The dashboard's HITL actions are staged client-side and exported as JSON rather than
  applied live against a running server -- `apply_hitl_review.py` is a deliberately
  explicit, auditable "apply" step rather than a hidden background write, but a
  production deployment would likely wire the Export button directly to an API.

## File map

```
aicb/
  vectorize.py     deterministic embeddings (Sa's I / No)
  tuple_config.py  H, O, V dataclasses + AgentAssertion/GroundTruth
  metrics.py       Sa, Cr, MTBH, Ktrust, VDC, composite trust index
  spc.py           Layer 3 statistical control (Western Electric rules)
  audit.py         hash-chained, tamper-evident decision log (Layer 4)
  morphism.py      Layer 2 Functor Certification: Boundary, d_S/d_M, MER, Composition Theorem
  hitl.py          Layer 5 Human Trustee review: HTDR, ReviewLog (separate hash chain)
  breaker.py       CircuitBreaker: trip logic, safe states, SOP-01/02/03, HITL review API
  insert.py        protect() decorator + ToolGate -- the insertion API
  dashboard.py     self-contained HTML dashboard: E2E Flow / Morphism Evaluation / Training & Feedback
  architecture_explorer.py  static content model + renderer for architecture_explorer.html
                   (Value Points, Tier 1-4, Part II, System Diagram, Governance Tuple,
                    Morphism Quadrant, Simulation, IRI-organized Glossary)
  console.py       merges dashboard.py + architecture_explorer.py into governance_console.html
                   (imports both modules' CSS/JS/render logic; resolves the DATA/openDrawer/
                    renderMorphism naming collisions via assertion-guarded text transforms)
examples/
  pipeline_review_demo.py         FLAGSHIP: full pipeline incl. morphism chain -> unreviewed HITL
                                   queue; writes trust_dashboard.html + governance_console.html
  apply_hitl_review.py            applies a review batch (exported or sample), regenerates both
  network_ops_demo.py             simpler Sa/Cr-only scenario run (original design-spec domain)
  tool_gate_demo.py               pre-execution veto in a tool-calling loop
  generic_llm_wrapper.py          decorator pattern in front of any LLM client
  generate_architecture_explorer.py  -> architecture_explorer.html
tests/
  test_breaker.py  sanity tests, runnable without pytest
```
