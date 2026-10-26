"""linucb-modes: a LinUCB meta-controller over the planner's strategy modes.

The bandit never chooses raw bids; it chooses a planner personality
(conservative, balanced, aggressive, robust) from an 8-feature context.
Its reward is the realized utility of the decision round and the next two
rounds (zero for a round spent resting), observed with the normal one-round
feedback lag. Learning within one 60-round run is slow, so per-arm statistics
can be warm-started from ``bandit_prior.json``, trained offline on simulation
seeds that are disjoint from every evaluation set.
LinUCB sufficient statistics are additive, so parallel training runs merge
exactly. Standard library only.
"""

import json
import math
from pathlib import Path

from . import adaptive

ARMS = ("conservative", "balanced", "aggressive", "robust")
DIMENSION = 9          # bias + 8 context features
WINDOW = 3             # reward: utility of rounds t, t+1, t+2
ALPHA = 0.35           # exploration bonus
PRIOR_PATH = Path(__file__).with_name("bandit_prior.json")

_state: dict = {"training": False, "persistent": None}


def context(track, own: float, bats: list, specs: list, round_index: int, total: int,
            sums: dict, budget: float, profile: dict) -> list:
    confidence = track.confidence()
    awake = [b for s, b in zip(specs, bats) if not s.blocked and b > adaptive.CUTOFF]
    unknown = sum(1 for s in specs if s.kind not in ("naive", "even", "prop"))
    return [1.0,
            own,                                                   # own battery
            min(awake) if awake else 1.0,                          # weakest awake rival
            (round_index - 1) / max(1, total),                     # progress
            min(1.0, 10 * confidence["market"]),                   # market error
            min(1.0, 100 * confidence["battery"]),                 # physics/battery error
            unknown / max(1, len(specs)),                          # opponent uncertainty
            min(2.0, sum(sums.values()) / max(1e-9, 3 * budget)),  # competition level
            float(profile.get("q_min", 0)) + float(profile.get("s_min", 0))]  # floor pressure


def _identity(scale: float = 1.0) -> list:
    return [[scale if i == j else 0.0 for j in range(DIMENSION)] for i in range(DIMENSION)]


def _solve(a: list, b: list) -> list:
    """Gaussian elimination with partial pivoting; a is small and SPD."""
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        m[col], m[pivot] = m[pivot], m[col]
        if abs(m[col][col]) < 1e-12:
            continue
        for r in range(col + 1, n):
            f = m[r][col] / m[col][col]
            for c in range(col, n + 1):
                m[r][c] -= f * m[col][c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = m[r][n] - sum(m[r][c] * x[c] for c in range(r + 1, n))
        x[r] = s / m[r][r] if abs(m[r][r]) > 1e-12 else 0.0
    return x


class LinUCB:
    def __init__(self, prior: dict | None = None):
        self.a = {arm: _identity() for arm in ARMS}
        self.b = {arm: [0.0] * DIMENSION for arm in ARMS}
        self.pulls = {arm: 0 for arm in ARMS}
        if prior:
            for arm in ARMS:
                if arm in prior.get("a", {}):
                    self.a[arm] = [row[:] for row in prior["a"][arm]]
                    self.b[arm] = list(prior["b"][arm])

    def choose(self, x: list, alpha: float) -> str:
        best, best_value = ARMS[1], -math.inf
        for arm in ARMS:
            theta = _solve(self.a[arm], self.b[arm])
            ax = _solve(self.a[arm], x)
            bonus = alpha * math.sqrt(max(0.0, sum(xi * yi for xi, yi in zip(x, ax))))
            value = sum(t * xi for t, xi in zip(theta, x)) + bonus
            if value > best_value + 1e-12:
                best, best_value = arm, value
        return best

    def update(self, arm: str, x: list, reward: float) -> None:
        for i in range(DIMENSION):
            self.b[arm][i] += reward * x[i]
            for j in range(DIMENSION):
                self.a[arm][i][j] += x[i] * x[j]
        self.pulls[arm] += 1

    def export(self) -> dict:
        return {"a": self.a, "b": self.b, "pulls": self.pulls}


def load_prior() -> dict | None:
    try:
        return json.loads(PRIOR_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def learner(track) -> LinUCB:
    if _state["training"]:
        # Offline training keeps one learner across many simulated runs.
        if _state["persistent"] is None:
            _state["persistent"] = LinUCB(load_prior() if _state.get("warm") else None)
        return _state["persistent"]
    if "bandit" not in track.extra:
        track.extra["bandit"] = LinUCB(load_prior())
    return track.extra["bandit"]


def settle(track, round_index: int, history: list) -> None:
    """Resolve rewards whose WINDOW rounds are all known to have settled."""
    pending = track.extra.setdefault("bandit_pending", [])
    if not pending:
        return
    utilities = {int(e.get("round", 0)): float(e.get("utility", 0)) for e in history}
    known = max(utilities) if utilities else 0
    # A round with no result and earlier than the newest result was spent idle.
    still = []
    model = learner(track)
    for decided, arm, x in pending:
        last = decided + WINDOW - 1
        if last <= known:
            reward = sum(utilities.get(r, 0.0) for r in range(decided, last + 1))
            model.update(arm, x, reward)
        else:
            still.append((decided, arm, x))
    track.extra["bandit_pending"] = still


def choose_mode(track, own, bats, specs, round_index, total, sums, budget, profile, history) -> str:
    settle(track, round_index, history)
    x = context(track, own, bats, specs, round_index, total, sums, budget, profile)
    arm = learner(track).choose(x, ALPHA * (2.0 if _state["training"] else 1.0))
    track.extra.setdefault("bandit_pending", []).append((round_index, arm, x))
    track.extra_summary["bandit_pulls"] = dict(learner(track).pulls)
    return arm
