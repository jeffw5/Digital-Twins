"""
Generates architecture_explorer.html: the clickable Tier 1 / Tier 2 / Part II component
browser, glossary, colored morphism quadrant map, Composition Theorem calculator,
Governance Quad-Tuple (H,O,V,A) diagram, and forward/backward L1-L5 simulation.

This content is static reference material (not live breaker telemetry -- see
trust_dashboard.html / pipeline_review_demo.py for that), so this script just renders
aicb/architecture_explorer.py's embedded content model to a file.

Run: python3 examples/generate_architecture_explorer.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aicb import architecture_explorer


def main():
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "architecture_explorer.html"))
    architecture_explorer.write(out_path)
    print(f"Architecture Explorer written to: {out_path}")
    print("Tabs: Value Points | Architecture (Tier 1-4/Part II) | Governance Tuple (H,O,V,A) | "
          "Morphism Quadrant & Composition Theorem | Simulation | Glossary")


if __name__ == "__main__":
    main()
