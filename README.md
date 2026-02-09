# Multi-Objective Diet Optimization: Exploring Trade-offs in Cambodia

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

This repository provides the data, code, and analysis notebooks for a multi-objective diet optimization and decision-support framework applied to Cambodia. The framework generates Pareto-efficient diet baskets that simultaneously consider affordability, greenhouse gas emissions (GHGe), and dietary continuity (deviation from current consumption patterns), and supports the selection of compromise solutions through multi-criteria decision analysis.

## Overview

The framework consists of three main stages:

1. **Mathematical model formulation** — a multi-objective linear program (LP) that simultaneously minimizes three objectives: cost, GHGe, and a dietary-shift index measuring deviation from observed consumption patterns, subject to nutritional adequacy, food group balance, and dietary continuity constraints.
2. **RNBI (Revised Normal Boundary Intersection)** — generates a discrete set of Pareto-efficient diet baskets by systematically exploring the trade-off surface defined by the LP model.
3. **VIKOR (Multi-Criteria Decision Making)** — ranks the generated baskets and identifies compromise solutions under different preference weightings, supporting transparent decision-making rather than prescribing a single "optimal" diet.

The tool is designed as a decision-support system: it maps the feasible trade-off space and helps stakeholders understand the consequences of prioritizing one objective over another.

## Repository Structure

```
.
├── README.md
├── BLUEPRINT.md                          # Detailed repository overview
├── EXAMPLE.md                            # Quick-start guide and workflow walkthrough
├── requirements.txt
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
│       ├── 1-Data-Model-Molp.ipynb
│       ├── Data-class.ipynb
│       ├── Model-class.ipynb
│       └── all.ipynb
├── data/                                  # Input datasets (Excel)
│   ├── food_items_match.xlsx
│   ├── food_prices.xlsx
│   ├── food_nutritional_composition.xlsx
│   ├── food_environmental.xlsx
│   ├── food_consumption.xlsx
│   ├── nutritional_requirements.xlsx
│   ├── afe_factors.xlsx
│   └── ...                                # Additional data files (see BLUEPRINT.md)
└── results/                               # Region-specific analysis notebooks
    ├── a-kampot-and-kep-woman/
    ├── b-mondulkiri-and-rattanakiri/
    ├── c-preah-vihear-and-stung-treng/
    └── d-prey-veng/
```

## Installation

**Requirements:** Python 3.11 or higher.

```bash
git clone https://github.com/polgilf/diet-basket-tradeoffs.git
cd diet-basket-tradeoffs
pip install -r requirements.txt
```

Note: PuLP uses the HiGHS solver for optimization. The `highspy` package is included in `requirements.txt` so it is installed automatically; without it you may see `PulpSolverError: HiGHS: Not Available`.

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

All data inputs required to reproduce the analyses are provided in the repository.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
