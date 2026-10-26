"""Warm-start prior for `linucb-modes`: persistent learners over many training episodes, merged.

    python train_bandit.py 50001 400 bandit_prior.json

As in the original run, the seeds are dealt to four workers (seeds[0::4],
seeds[1::4], ...), each with its own learner, and the learners' statistics
are summed: LinUCB statistics are additive, so the merge is exact.
"""

from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import statistics
import sys

import swarmbench as sb
from swarmbench.strategies import bandit

WORKERS = 4


def worker(seeds: list[int]) -> dict:
    # Training mode: one learner across this worker's episodes, a doubled exploration bonus, no prior.
    bandit._state.update(training=True, persistent=None, warm=False)
    market = sb.Market("graded")
    scores = []
    for seed in seeds:
        seats = [sb.seat(sb.get_spec(bot)) for bot in ("naive-max", "even-split", "proportional")]
        seats.append(sb.seat(sb.get_spec("linucb-modes"), team="agent-linucb-modes", baseline=False))
        scores.append(market.play(seed, seats).rows[-1]["score"])
    return {**bandit._state["persistent"].export(), "scores": scores}


def main() -> None:
    first, count, output = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
    seeds = list(range(first, first + count))
    with ProcessPoolExecutor(WORKERS) as pool:
        parts = list(pool.map(worker, [seeds[i::WORKERS] for i in range(WORKERS)]))
    d = bandit.DIMENSION
    prior = {"a": {}, "b": {}, "pulls": {}}
    for arm in bandit.ARMS:
        # A = I plus every worker's A - I; b = the sum of the workers' b (added in this order).
        a = [[1.0 if i == j else 0.0 for j in range(d)] for i in range(d)]
        b = [0.0] * d
        for part in parts:
            for i in range(d):
                b[i] += part["b"][arm][i]
                for j in range(d):
                    a[i][j] += part["a"][arm][i][j] - (1.0 if i == j else 0.0)
        prior["a"][arm], prior["b"][arm] = a, b
        prior["pulls"][arm] = sum(part["pulls"][arm] for part in parts)
    prior["training_seeds"] = [seeds[0], seeds[-1]]
    prior["training_mean_score"] = statistics.mean(s for p in parts for s in p["scores"])
    output.write_text(json.dumps(prior), encoding="utf-8")
    print(f"pulls={prior['pulls']} mean training score={prior['training_mean_score']:.4f}")


if __name__ == "__main__":
    main()
