"""CatBoost value model on the same corpus and split, exported as standalone Python.

    python train_catboost.py value.jsonl catboost_value_model.py
"""

import importlib.util
import json
from pathlib import Path
import sys

from catboost import CatBoostRegressor
import numpy as np


def main() -> None:
    data, output = Path(sys.argv[1]), Path(sys.argv[2])
    rows = [json.loads(line) for line in data.read_text(encoding="utf-8").splitlines()]
    x = np.array([r["features"] for r in rows])
    y = np.array([r["target_remaining_score"] for r in rows])
    episodes = sorted({r["episode_seed"] for r in rows})
    held_out = set(episodes[int(0.8 * len(episodes)):])
    valid = np.array([r["episode_seed"] in held_out for r in rows])

    common = {"learning_rate": 0.03, "loss_function": "RMSE", "eval_metric": "RMSE", "random_seed": 137,
              "thread_count": 2, "task_type": "CPU", "grow_policy": "SymmetricTree", "boosting_type": "Plain",
              "allow_writing_files": False, "verbose": False}
    best = None
    for depth in (3, 4, 6):
        for l2 in (3.0, 10.0):
            model = CatBoostRegressor(**common, iterations=1200, depth=depth, l2_leaf_reg=l2)
            model.fit(x[~valid], y[~valid], eval_set=(x[valid], y[valid]),
                      early_stopping_rounds=70, use_best_model=True)
            rmse = float(np.sqrt(np.mean((model.predict(x[valid]) - y[valid]) ** 2)))
            print(f"depth={depth} l2={l2:g} trees={model.tree_count_} held-out RMSE={rmse:.4f}")
            if best is None or rmse < best[0]:
                best = (rmse, depth, l2, model.tree_count_)

    # Freeze the depth, the regularization and the number of trees; refit on every episode.
    _, depth, l2, trees = best
    final = CatBoostRegressor(**common, iterations=trees, depth=depth, l2_leaf_reg=l2)
    final.fit(x, y)
    final.save_model(str(output), format="python")   # plain Python: no CatBoost needed to predict

    # Parity: the export prints the borders to nine digits, CatBoost compares in float32.
    spec = importlib.util.spec_from_file_location("export", output)
    export = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(export)
    export.catboost_model.float_feature_borders = [
        [float(np.float32(b)) for b in borders] for borders in export.catboost_model.float_feature_borders]
    exported = np.array([export.apply_catboost_model(row.tolist()) for row in x.astype(np.float32)])
    error = float(np.max(np.abs(exported - final.predict(x))))
    if error > 1e-8:
        raise SystemExit(f"export parity failed: {error}")
    print(f"exported {trees} trees of depth {depth}; parity {error:.2g}")


if __name__ == "__main__":
    main()
