# Example

## Three-Stage Workflow (Data → RNBI → VIKOR)

This concise walkthrough mirrors the core workflow in the repository:

1. **Data loading** — read the curated input tables from `data/`.
2. **RNBI optimization** — build the multi-objective LP model and generate a Pareto set of diet baskets.
3. **VIKOR selection** — rank the resulting baskets to identify a compromise solution.

## Minimal code snippet

> Run this from the repository root (so `data/` and `code/classes/` resolve correctly).

```python
import os
import sys

# Make class modules importable
sys.path.append(os.path.join(os.getcwd(), "code", "classes"))

from DATA import Data
from MODEL import Model
from RNBI import RNBI
from MULTIPLEFOODBASKETS import MultipleFoodBaskets
from VIKOR import VIKOR

# --- 1) Data loading ---
data = Data(data_dir="data")

# Pick a population group + region present in the data
population_group = (
    "Woman of reproductive age"  # example label in nutritional_requirements.xlsx
)
region = "Kampot and Kep"  # example label in food_prices.xlsx / food_consumption.xlsx

# --- 2) RNBI optimization ---
model = Model(data, population_group=population_group, region=region)
model.set_objective_limits(
    {
        "Cost (KHR/day)": None,
        "Dietary-shift index (unitless)": 2,
        "CO2e (Kg/day)": 5,
    }
)

# cutting_points controls the granularity of the Pareto front sampling
rnbi = RNBI(model, cutting_points=5, normalize=True, plane_point="nadir")

# Convert efficient solutions to objective values.
# Rows are criteria and columns are alternative baskets.
objectives_df = MultipleFoodBaskets(rnbi).multiple_baskets_method_df(
    "objectives_df", fillna=0
)

# --- 3) VIKOR selection ---
# Weights must match the objective names in objectives_df.index.
criteria_weights = {
    "Cost (KHR/day)": 1 / 3,
    "Dietary-shift index (unitless)": 1 / 3,
    "CO2e (Kg/day)": 1 / 3,
}

vikor = VIKOR(criteria_values=objectives_df, criteria_weights=criteria_weights, v=0.5)
vikor.compute_S_R_Q(criteria_weights)

best_basket_id = vikor.best_alternative(method="Q")
print("Selected basket:", best_basket_id)
print(vikor.sorted_df_S_R_Q(method="Q"))
```

## Notes

- **Choosing labels**: The `population_group` and `region` strings must match entries in the Excel data tables under `data/`.
- **Granularity**: Higher `cutting_points` values yield more RNBI reference points (and more candidate baskets), at the cost of runtime.
- **Weights**: Adjust `criteria_weights` to reflect stakeholder priorities; `v` controls the trade-off between group utility (S) and individual regret (R).
- **Submission analyses**: The regional notebooks use `cutting_points=15`; the value `5` above is a faster functional example.
