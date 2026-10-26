"""Shortlist model for `learned-shortlist`, from the decisions of `archetype-learning`.

    python train_shortlist.py 52001 120 shortlist_model.json

As in the original run, the seeds are dealt to four workers (seeds[0::4],
seeds[1::4], ...) and their decisions concatenated in that order before the
seeded shuffle that splits them.
"""

from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import random
import sys

import numpy as np

import swarmbench as sb
from swarmbench.strategies import adaptive, shortlist

WORKERS = 4
decisions = []


def collect(world, info, own, bats, progress):
    """Label every candidate the rollouts evaluated: 1 if they ranked it among the best three.
    Each row also keeps the candidate's immediate reward, which the shortlist never prunes away."""
    values = info["values"]
    if len(values) < 4:
        return
    best = max(n[0] for n in info["all_nominal"])
    top = set(sorted(values, key=values.get, reverse=True)[:3])
    candidates = zip(info["all_candidates"], info["all_tags"], info["all_nominal"])
    decisions.append([(shortlist.features(world, bid, tag, nominal, own, bats, best, progress), int(i in top),
                       nominal[0]) for i, (bid, tag, nominal) in enumerate(candidates) if i in values])


def worker(seeds: list[int]) -> list:
    adaptive.COLLECT = collect                       # the planner's hook for a decision recorder
    decisions.clear()
    market = sb.Market("graded")
    for seed in seeds:
        seats = [sb.seat(sb.get_spec(bot)) for bot in ("naive-max", "even-split", "proportional")]
        seats.append(sb.seat(sb.get_spec("archetype-learning"), team="agent-archetype-learning", baseline=False))
        market.play(seed, seats)
    return list(decisions)


def recall(model: dict, groups: list, size: int) -> dict:
    """Per held-out decision: the share of the planner's top three that a shortlist of `size` keeps."""
    kept = positives = complete = 0
    for group in groups:
        scores = [shortlist.score(model, features) for features, _, _ in group]
        keep = set(sorted(range(len(group)), key=lambda i: scores[i], reverse=True)[:size])
        keep.add(max(range(len(group)), key=lambda i: group[i][2]))   # the best immediate bid stays
        hits, labels = sum(group[i][1] for i in keep), sum(label for _, label, _ in group)
        kept, positives, complete = kept + hits, positives + labels, complete + (hits == labels)
    return {"top3_recall": kept / max(1, positives), "decisions_fully_kept": complete / max(1, len(groups))}


def main() -> None:
    first, count, output = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
    seeds = list(range(first, first + count))
    with ProcessPoolExecutor(WORKERS) as pool:
        parts = pool.map(worker, [seeds[i::WORKERS] for i in range(WORKERS)])
        groups = [group for part in parts for group in part]

    random.Random(7).shuffle(groups)
    split = int(0.8 * len(groups))                   # whole decisions held out to measure recall
    rows = [(features, label) for group in groups[:split] for features, label, _ in group][:60000]
    x = np.array([features for features, _ in rows])
    y = np.array([label for _, label in rows], dtype=float)
    mean, scale = x.mean(axis=0), x.std(axis=0)
    mean[0], scale[0] = 0.0, 1.0                     # feature 0 is the intercept
    scale[scale == 0] = 1.0
    z = (x - mean) / scale
    penalty = np.eye(z.shape[1])
    penalty[0, 0] = 0.0                              # ridge 1 on every weight but the intercept
    w = np.zeros(z.shape[1])
    for _ in range(12):                              # Newton's method on the penalized log-loss
        p = 1 / (1 + np.exp(-np.clip(z @ w, -30, 30)))
        hessian = (z * (p * (1 - p))[:, None]).T @ z + penalty
        w -= np.linalg.solve(hessian, z.T @ (p - y) + penalty @ w)
    model = {"coef": w.tolist(), "mean": mean.tolist(), "scale": scale.tolist(),
             "training_seeds": [seeds[0], seeds[-1]], "decisions": len(groups), "rows": len(rows),
             "positive_rate": float(y.mean()), "held_out_decisions": len(groups) - split}
    model.update({f"held_out_size_{size}": recall(model, groups[split:], size) for size in (5, 7, 9)})
    output.write_text(json.dumps(model, indent=1), encoding="utf-8")
    print({k: v for k, v in model.items() if k not in ("coef", "mean", "scale")})


if __name__ == "__main__":
    main()
