"""Exercise the core data, RNBI, and VIKOR workflow on a small grid."""

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code" / "classes"))

from DATA import Data
from MODEL import Model
from MULTIPLEFOODBASKETS import MultipleFoodBaskets
from RNBI import RNBI
from VIKOR import VIKOR


data = Data(str(ROOT / "data"))
model = Model(data, "Woman of reproductive age", "Kampot and Kep")
model.set_objective_limits(
    {
        "Cost (KHR/day)": None,
        "Dietary-shift index (unitless)": 2,
        "CO2e (Kg/day)": 5,
    }
)

rnbi = RNBI(model, cutting_points=5, normalize=True, plane_point="nadir")
objectives = MultipleFoodBaskets(rnbi).multiple_baskets_method_df(
    "objectives_df", fillna=0
)
weights = {criterion: 1 / 3 for criterion in objectives.index}
vikor = VIKOR(objectives, weights, v=0.5)
vikor.compute_S_R_Q(weights)

assert len(objectives.columns) > 3, "RNBI produced no interior efficient solutions"
assert vikor.Q.notna().all(), "VIKOR produced an undefined score"
print(
    f"Smoke test passed: {len(objectives.columns)} solutions; "
    f"selected {vikor.best_alternative('Q')}"
)