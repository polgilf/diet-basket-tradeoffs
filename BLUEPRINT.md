# Blueprint

## Introduction
This repository contains data, Python classes, and analysis notebooks for building and evaluating optimized diet baskets with multi-objective linear programming methods. It is organized into source code, input datasets, and region-specific result notebooks.

## Repository scaffold
- `README.md` — Placeholder README for the project (currently empty).
- `BLUEPRINT.md` — High-level overview of the repository structure and contents.
- `code/` — Source code and notebooks used to build and analyze diet basket models.
  - `classes/` — Core Python modules that implement data loading, modeling, optimization, and analysis utilities.
    - `DATA.py` — Loads Excel inputs and prepares data structures and helper accessors for the optimization models.
    - `FOODBASKET.py` — Defines a food basket object and methods to summarize composition, nutrition, and energy metrics.
    - `MODEL.py` — Builds the multi-objective linear programming model and constraints with PuLP.
    - `MOLP.py` — Implements multi-objective linear programming utilities, including ideal/nadir points and normalization.
    - `MULTIPLEFOODBASKETS.py` — Provides helpers for working with collections of optimized baskets and exporting results.
    - `PLOTS.py` — Visualization routines for Pareto fronts and related comparative plots.
    - `RNBI.py` — Implements the Revised Normal Boundary Intersection (RNBI) method for generating efficient solutions.
    - `SOLUTION.py` — Encapsulates optimization solutions with helpers to extract objective and variable values.
    - `VIKOR.py` — Multi-criteria decision-making (VIKOR) implementation for ranking alternatives.
    - `utils.py` — Small utilities for distributing reference points along lines and triangles.
  - `usage-examples/` — Example notebooks demonstrating how to use the model and data classes.
    - `1-Data-Model-Molp.ipynb` — Walkthrough of data loading, model creation, and MOLP usage.
    - `Data-class.ipynb` — Focused notebook on the `Data` class and its outputs.
    - `all.ipynb` — End-to-end notebook combining data, modeling, and analysis steps.
    - `Model-class.ipynb` — Notebook illustrating the `Model` class setup and solving.
- `data/` — Input Excel datasets used by the modeling pipeline.
  - `afe_factors.xlsx` — Age/sex adjustment factors for energy requirements.
  - `current_environmental_impact.xlsx` — Baseline environmental impact data for comparison with optimized baskets.
  - `current_food_expenditure.xlsx` — Baseline food expenditure data for comparison.
  - `food_consumption.xlsx` — Regional food consumption statistics used for deviation constraints.
  - `food_environmental.xlsx` — Environmental impact coefficients for food items.
  - `food_group_lower_limits.xlsx` — Lower bounds for food group quantities.
  - `food_group_percentages.xlsx` — Healthy diet basket energy share targets by food group.
  - `food_items_match.xlsx` — Food item IDs, groupings, and metadata for joins.
  - `food_nutritional_composition.xlsx` — Nutrient composition values for food items.
  - `food_prices.xlsx` — Regional food item prices.
  - `food_subgroup_colors.xlsx` — Color mapping for food subgroup visualizations.
  - `food_subgroup_importance.xlsx` — Importance weights for food subgroup lower limits.
  - `food_subgroup_lower_limits.xlsx` — Lower bounds for food subgroup quantities.
  - `nutrient_match.xlsx` — Nutrient identifiers used to align inputs across datasets.
  - `nutritional_requirements.xlsx` — Nutritional requirement targets by population group.
  - `offal_food_items.xlsx` — List of offal items subject to special constraints.
- `results/` — Region-specific analysis notebooks and generated results.
  - `a-kampot-and-kep-woman/` — Results for the Kampot and Kep (women) scenario.
    - `1-code-and-results.ipynb` — Notebook with code and outputs for this scenario.
  - `b-mondulkiri-and-rattanakiri/` — Results for the Mondulkiri and Rattanakiri scenario.
    - `1-code-and-results.ipynb` — Notebook with code and outputs for this scenario.
  - `c-preah-vihear-and-stung-treng/` — Results for the Preah Vihear and Stung Treng scenario.
    - `1-code-and-results.ipynb` — Notebook with code and outputs for this scenario.
  - `d-prey-veng/` — Results for the Prey Veng scenario.
    - `1-code-and-results.ipynb` — Notebook with code and outputs for this scenario.
