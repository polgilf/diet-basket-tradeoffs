# Reproducing the submission analyses

## Archived version

The *Food Security* submission refers to GitHub release `v1.0.0-submission`. Check out that release before running the analysis:

```bash
git clone https://github.com/polgilf/diet-basket-tradeoffs.git
cd diet-basket-tradeoffs
git checkout v1.0.0-submission
```

## Environment

The release was tested with Python 3.12.10. `requirements.txt` pins the direct dependencies and `requirements-lock.txt` pins the complete Python 3.12 environment.

```bash
python -m venv .venv

# Windows
.venv\Scripts\python -m pip install -r requirements-lock.txt
.venv\Scripts\python scripts/smoke_test.py

# macOS/Linux
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/smoke_test.py
```

The smoke test runs the Kampot and Kep model with a five-point RNBI grid and equal VIKOR weights. It must finish with `Smoke test passed`.

## Full regional analyses

The four notebooks below contain the complete analysis that generated the committed tables, figures, and serialized result objects:

- `results/a-kampot-and-kep-woman/1a-code-and-results-kampot-and-kep-woman.ipynb`
- `results/b-mondulkiri-and-rattanakiri/1b-code-and-results-mondulkiri-and-rattanakiri.ipynb`
- `results/c-preah-vihear-and-stung-treng/1c-code-and-results-preah-vihear-and-stung-treng.ipynb`
- `results/d-prey-veng/1d-code-and-results-prey-veng.ipynb`

Open each notebook from its existing directory and run all cells from a fresh kernel. The notebooks use a 15-point RNBI grid, write their outputs back to the same regional directory, and may take substantially longer than the smoke test.

The committed `.xlsx`, `.png`, `.pkl`, notebook, and HTML files are the reference outputs used to prepare the manuscript. Pickle files should only be loaded from this trusted release; Python pickle is not safe for untrusted input.

## Solver note

The primary optimization calls use HiGHS through PuLP and `highspy`. The RNBI dominance checks currently call PuLP's bundled CBC backend. This mixed backend behavior is retained in the submission release to match the code used to generate the committed results.

## Inputs

The analysis reads the 16 workbooks under `data/`. Their contents, provenance, aggregation level, and reuse caveats are documented in `data/README.md`.