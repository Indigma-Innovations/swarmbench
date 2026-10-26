"""learned-shortlist: a learned candidate shortlist inside the analytical MPC.

learned proposal -> analytical safety/feasibility check -> MPC refinement.

A logistic model, trained offline on decisions of the adaptive-cycle-aware
planner, scores each candidate bid from cheap
one-step features. Only the best ``size`` candidates (plus the best immediate
bid, always) reach the expensive rollouts, at the top level and inside the
two-round continuation. Every executed bid is still produced and valued by
the analytical planner; the model only prunes. Without shortlist_model.json
the hook keeps every candidate, i.e. the planner is unchanged.
"""

import json
import math
from pathlib import Path

MODEL_PATH = Path(__file__).with_name("shortlist_model.json")
_cache: dict = {}


def features(world, bid: dict, tag, nominal: tuple, own: float, bats: list,
             best_reward: float, progress: float) -> list:
    from . import adaptive
    reward, own_next, bats_next, _ = nominal
    budget = max(1e-9, sum(bid.values()))
    energy = bid["energy"] / budget
    n = max(1, len(bats))
    asleep_now = sum(1 for s, b in zip(world.specs, bats) if not s.blocked and b <= adaptive.CUTOFF)
    asleep_next = sum(1 for s, b in zip(world.specs, bats_next) if not s.blocked and b <= adaptive.CUTOFF)
    relative = reward / best_reward if best_reward > 1e-9 else 0.0
    return [1.0, energy, energy * energy, relative, relative * relative, own, own_next,
            float(own_next <= adaptive.CUTOFF), (asleep_next - asleep_now) / n, sum(bats_next) / n,
            float(tag is not None and tag[0] == "own"), float(tag is not None and tag[0] != "own"),
            progress, progress * energy, own * energy]


def load() -> dict | None:
    if "model" not in _cache:
        try:
            _cache["model"] = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _cache["model"] = None
    return _cache["model"]


def score(model: dict, x: list) -> float:
    z = sum(c * (v - m) / s for c, v, m, s in zip(model["coef"], x, model["mean"], model["scale"]))
    return 1 / (1 + math.exp(-max(-30.0, min(30.0, z))))


def make(size: int, progress: float):
    model = load()

    def prune(world, candidates, tags, nominal, own, bats, remaining):
        if model is None or len(candidates) <= size:
            return candidates, tags, nominal
        best = max(n[0] for n in nominal)
        scores = [score(model, features(world, c, t, n, own, bats, best, progress))
                  for c, t, n in zip(candidates, tags, nominal)]
        keep = set(sorted(range(len(candidates)), key=lambda i: scores[i], reverse=True)[:size])
        keep.add(max(range(len(candidates)), key=lambda i: nominal[i][0]))
        order = sorted(keep)  # preserve the planner's candidate order for ties
        return [candidates[i] for i in order], [tags[i] for i in order], [nominal[i] for i in order]
    return prune
