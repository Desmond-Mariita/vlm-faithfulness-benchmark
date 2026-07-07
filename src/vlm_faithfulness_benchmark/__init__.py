"""VLM Faithfulness Benchmark — implementation package.

Scaffolding only: per the release plan, no normative pipeline code exists
before implementation authorization (V1-044). Component subpackages map
one-to-one to the accepted implementation architecture
(``docs/design/Implementation_Architecture_S01-S19.md`` §2):

- ``ingestion``  (C1, S01)      - ``generation`` (C2, S02-S03)
- ``gating``     (C3, S04-S11)  - ``labeling``   (C4, S12-S13)
- ``sealing``    (C5, S14-S15)  - ``assembly``   (C6, S16-S17)
- ``release``    (C7, S18)      - ``views``      (C8, S19)

All code in this package is bound by the repository code standard
(CONTRIBUTING.md "Code standards"): Google-style docstrings, PEP 484 type
hints, math implemented from scratch with LaTeX in a comment above each
formula, small testable units, and invariants encoded as asserts or tests
mapped in the V1-040 acceptance matrix.
"""

__version__ = "0.0.1"
