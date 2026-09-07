# Multi-Objective Diet Optimization: Exploring Trade-offs in Cambodia

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

This repository provides the data, code, and analysis notebooks for a multi-objective diet optimization and decision-support framework applied to Cambodia. The framework generates Pareto-efficient diet baskets that simultaneously consider affordability, greenhouse gas emissions (GHGe), and dietary continuity (deviation from current consumption patterns), and supports the selection of compromise solutions through multi-criteria decision analysis.

The version accompanying the *Food Security* submission is [`v1.0.0-submission`](https://github.com/polgilf/diet-basket-tradeoffs/releases/tag/v1.0.0-submission). Use that immutable release, rather than the moving `main` branch, to reproduce the submitted results.

## Overview

The framework consists of three main stages:

1. **Mathematical model formulation** — a mixed-integer multi-objective linear program that simultaneously minimizes three objectives: cost, GHGe, and a dietary-shift index measuring deviation from observed consumption patterns, subject to nutritional adequacy, food group balance, and dietary continuity constraints. Binary indicators prevent simultaneous positive lower- and upper-bound deviations for a food subgroup.
2. **RNBI (Revised Normal Boundary Intersection)** — generates a discrete set of Pareto-efficient diet baskets by systematically exploring the trade-off surface defined by the LP model.
3. **VIKOR (Multi-Criteria Decision Making)** — ranks the generated baskets and identifies compromise solutions under different preference weightings, supporting transparent decision-making rather than prescribing a single "optimal" diet.

The tool is designed as a decision-support system: it maps the feasible trade-off space and helps stakeholders understand the consequences of prioritizing one objective over another.

## Repository Structure

```
.
├── README.md
├── EXAMPLE.md                            # Quick-start guide and workflow walkthrough
├── REPRODUCIBILITY.md                    # Exact environment and rerun instructions
├── CITATION.cff                          # Machine-readable citation metadata
├── requirements.txt
├── requirements-lock.txt                 # Fully resolved Python 3.12 environment
├── LICENSE
├── code/
│   ├── classes/                           # Core Python modules
│   │   ├── DATA.py                        # Data loading and preparation
│   │   ├── MODEL.py                       # Multi-objective LP model (PuLP)
│   │   ├── MOLP.py                        # MOLP utilities (ideal/nadir points, normalization)
│   │   ├── RNBI.py                        # Revised Normal Boundary Intersection method
│   │   ├── VIKOR.py                       # VIKOR multi-criteria decision making
│   │   ├── SOLUTION.py                    # Solution wrapper for optimization results
│   │   ├── FOODBASKET.py                  # Food basket composition and nutrition analysis
│   │   ├── MULTIPLEFOODBASKETS.py         # Batch operations on collections of baskets
│   │   ├── PLOTS.py                       # Pareto front and comparison visualizations
│   │   └── utils.py                       # Reference point distribution utilities
│   └── usage-examples/                    # Tutorial notebooks
│       ├── Data-Model-Molp.ipynb
│       ├── Data-class.ipynb
│       └── Model-class.ipynb
├── data/                                  # Input datasets (Excel)
│   ├── food_items_match.xlsx
│   ├── food_prices.xlsx
│   ├── food_nutritional_composition.xlsx
│   ├── food_environmental.xlsx
│   ├── food_consumption.xlsx
│   ├── nutritional_requirements.xlsx
│   ├── afe_factors.xlsx
│   └── ...                                # Additional model input tables
└── results/                               # Region-specific analysis notebooks
    ├── a-kampot-and-kep-woman/
    ├── b-mondulkiri-and-rattanakiri/
    ├── c-preah-vihear-and-stung-treng/
    └── d-prey-veng/
```

## Installation

**Requirements:** Python 3.12.10. The direct and transitive package versions used for the submission release are pinned in `requirements-lock.txt`.

```bash
git clone https://github.com/polgilf/diet-basket-tradeoffs.git
cd diet-basket-tradeoffs
git checkout v1.0.0-submission
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-lock.txt  # Windows
# .venv/bin/python -m pip install -r requirements-lock.txt    # macOS/Linux
```

Run `.venv\Scripts\python scripts/smoke_test.py` on Windows, or `.venv/bin/python scripts/smoke_test.py` on macOS/Linux, to exercise data loading, model construction, RNBI generation, and VIKOR selection. See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the complete regional workflow and expected artifacts.

Primary optimization calls use HiGHS through `highspy`; the current RNBI dominance-check implementation calls PuLP's bundled CBC backend. Both are installed with the pinned environment.

## Quick Start

See [EXAMPLE.md](EXAMPLE.md) for a concise walkthrough of the three-stage workflow (data loading, RNBI optimization, VIKOR selection) and a minimal code snippet to get started.

The `code/usage-examples/` directory contains tutorial notebooks that demonstrate each component:

- `Data-class.ipynb` -- loading and inspecting input data
- `Model-class.ipynb` -- building the optimization model
- `Data-Model-Molp.ipynb` -- data loading through MOLP setup

For complete regional analyses, see the notebooks in `results/`.

## Data

Input datasets are included in the `data/` directory. Key data sources:

- **Food prices and consumption patterns**: Cambodia Socio-Economic Survey (CSES) 2021 and Fill the Nutrient Gap (FNG) Cambodia analysis.
- **Nutritional composition**: FNG Cambodia food composition data.
- **Environmental impact coefficients**: Based on Poore & Nemecek (2018) global food systems environmental impact data.
- **Nutritional requirements**: Population-group-specific dietary reference intakes.

All data inputs required to reproduce the analyses are provided in the repository. See [data/README.md](data/README.md) for file-level provenance, aggregation level, and privacy information.

## License

The original source code is licensed under the MIT License; see [LICENSE](LICENSE).
