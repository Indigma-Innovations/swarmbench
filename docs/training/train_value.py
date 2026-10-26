"""Ridge value model: alpha chosen on whole held-out episodes, then refit on every episode.

    python train_value.py value.jsonl value_model.json
"""

import hashlib
import json
from pathlib import Path
import sys

import numpy as np


def main() -> None:
    data, output = Path(sys.argv[1]), Path(sys.argv[2])
    rows = [json.loads(line) for line in data.read_text(encoding="utf-8").splitlines()]
    features = np.array([r["features"] for r in rows])
    target = np.array([r["target_remaining_score"] for r in rows])
    episodes = sorted({r["episode_seed"] for r in rows})
    held_out = set(episodes[int(0.8 * len(episodes)):])          # the last 20% of the episodes
    valid = np.array([r["episode_seed"] in held_out for r in rows])
    every = np.ones(len(rows), dtype=bool)

    def standardize(mask):
        mean, scale = features[mask].mean(axis=0), features[mask].std(axis=0)
        mean[0] = 0.0                                             # feature 0 is the intercept
        scale[scale < 1e-8] = 1.0
        return mean, scale, (features - mean) / scale

    def fit(x, mask, alpha):
        penalty = alpha * np.eye(x.shape[1])
        penalty[0, 0] = 0.0                                       # the intercept is not penalized
        return np.linalg.solve(x[mask].T @ x[mask] + penalty, x[mask].T @ target[mask])

    _, _, x = standardize(~valid)
    errors = {str(alpha): float(np.sqrt(np.mean((x[valid] @ fit(x, ~valid, alpha) - target[valid]) ** 2)))
              for alpha in (0.01, 0.1, 1.0, 10.0, 100.0)}
    alpha = float(min(errors, key=errors.get))
    mean, scale, x = standardize(every)
    coefficients = fit(x, every, alpha)
    model = {"schema": 1, "model": "ridge Monte Carlo remaining-score value", "alpha": alpha,
             "means": mean.tolist(), "scales": scale.tolist(), "coefficients": coefficients.tolist(),
             "training": {"episodes": len(episodes), "examples": len(rows),
                          "seed_range": [episodes[0], episodes[-1]], "grouped_validation_rmse": errors,
                          "selected_validation_rmse": errors[str(alpha)],
                          "refit_training_rmse": float(np.sqrt(np.mean((x @ coefficients - target) ** 2))),
                          "data_sha256": hashlib.sha256(data.read_bytes()).hexdigest()}}
    output.write_text(json.dumps(model, indent=2), encoding="utf-8")
    print(f"alpha={alpha:g}, held-out RMSE={errors[str(alpha)]:.4f}")


if __name__ == "__main__":
    main()
