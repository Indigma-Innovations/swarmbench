"""The built-in bidding policies of the catalog, one function per entry.

Only public round inputs, swarm observations and the agent's own results are
used. No arena imports, seed access, third-party dependencies or URLs.

Copyright 2026 The CoGNETs Consortium
SPDX-License-Identifier: Apache-2.0
"""

import math
from typing import Callable

RESOURCES = ("compute", "energy", "security")


def _weights(profile: dict) -> dict:
    weights = {k: max(0.0, float(profile.get("weights", {}).get(k, 1 / 3))) for k in RESOURCES}
    total = sum(weights.values()) or 1.0
    return {k: v / total for k, v in weights.items()}


def _normalize(bid: dict, budget: float) -> dict:
    clean = {k: max(0.0, float(bid.get(k, 0))) for k in RESOURCES}
    total = sum(clean.values())
    if total <= 0:
        return {k: max(0, budget) / 3 for k in RESOURCES}
    return {k: v * max(0, budget) / total for k, v in clean.items()}


def _battery(profile: dict) -> float:
    return min(1.0, max(0.0, float(profile.get("features", {}).get("battery", 1))))


def _taper(bid: dict, budget: float, profile: dict, power: float = 1.0) -> dict:
    keep = max(0.0, (_battery(profile) - 0.05) / 0.95) ** power
    bid = dict(bid)
    freed = bid["energy"] * (1 - keep)
    bid["energy"] *= keep
    weights = _weights(profile)
    nonenergy = weights["compute"] + weights["security"] or 1
    for k in ("compute", "security"):
        bid[k] += freed * weights[k] / nonenergy
    return _normalize(bid, budget)


def estimate_others(budget: float, profile: dict, history: list, window: int = 4) -> dict:
    """Invert awarded shares: S = b * (C / x - 1).

    A result's `prices` precede its capacities in this arena, so price*capacity
    is not its round's total bid. Allocation, own bid and capacity DO align.
    Normalize by the past wallet to adapt estimates to this round's wallet.
    """
    weights = _weights(profile)
    estimates = {}
    for k in RESOURCES:
        samples = []
        for entry in history[-window:]:
            own = float(entry.get("bid", {}).get(k, 0))
            share = float(entry.get("allocation", {}).get(k, 0))
            capacity = float(entry.get("capacities", {}).get(k, 0))
            spend = float(entry.get("spend", 0))
            if own > 1e-8 and share > 1e-8 and capacity > 0 and spend > 0:
                samples.append(max(1e-4, own * (capacity / share - 1)) / spend)
        estimates[k] = budget * (sum(samples) / len(samples) if samples else 3 * weights[k])
    return estimates


def _floor_needs(capacities: dict, profile: dict, others: dict, margin: float = 1.10) -> dict:
    lower = {k: 0.0 for k in RESOURCES}
    for k, key in (("compute", "q_min"), ("security", "s_min")):
        cap = max(1e-8, float(capacities.get(k, 1)))
        target = min(0.98 * cap, max(0, float(profile.get(key, 0))) * margin)
        lower[k] = max(0.0, others[k]) * target / max(1e-8, cap - target)
    return lower


def _reserve(bid: dict, budget: float, lower: dict) -> dict:
    """Reserve both floors simultaneously, avoiding sequential top-up theft."""
    required = sum(lower.values())
    if required >= budget:
        return _normalize(lower, budget)
    surplus = {k: max(0, bid[k] - lower[k]) for k in RESOURCES}
    total = sum(surplus.values())
    if not total:
        surplus = {k: 1.0 for k in RESOURCES}
        total = 3.0
    return {k: lower[k] + (budget - required) * surplus[k] / total for k in RESOURCES}


def template(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """The supplied weight-proportional policy, unchanged as a comparator."""
    return {k: budget * float(profile.get("weights", {}).get(k, 1 / 3)) for k in RESOURCES}


def taper(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    return _taper(template(budget, prices, capacities, profile, history), budget, profile)


def floors(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    others = estimate_others(budget, profile, history)
    return _reserve(template(budget, prices, capacities, profile, history), budget,
                    _floor_needs(capacities, profile, others))


def price_taker(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """Price/market allocation alone, intentionally without battery control."""
    weights = _weights(profile)
    others = estimate_others(budget, profile, history)
    bid = _normalize({k: weights[k] ** 2 * max(0, capacities.get(k, 1)) / max(0.05, others[k])
                      for k in RESOURCES}, budget)
    return _reserve(bid, budget, _floor_needs(capacities, profile, others))


def market_taper(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    bid = _taper(price_taker(budget, prices, capacities, profile, history), budget, profile)
    others = estimate_others(budget, profile, history)
    return _reserve(bid, budget, _floor_needs(capacities, profile, others))


def _maximize(fn: Callable[[float], float], low: float, high: float, steps: int = 18) -> float:
    """Bounded golden-section search; also evaluate both boundary solutions."""
    left, right = low, max(low, high)
    ratio = (math.sqrt(5) - 1) / 2
    a = right - ratio * (right - left)
    b = left + ratio * (right - left)
    fa, fb = fn(a), fn(b)
    for _ in range(steps):
        if fa > fb:
            right, b, fb = b, a, fa
            a = right - ratio * (right - left)
            fa = fn(a)
        else:
            left, a, fa = a, b, fb
            b = left + ratio * (right - left)
            fb = fn(b)
    return max((low, high, a, b), key=fn)


def _utility(bid: dict, capacities: dict, profile: dict, others: dict) -> float:
    weights = _weights(profile)
    allocation = {k: max(0, capacities.get(k, 1)) * max(0, bid[k]) / max(1e-9, max(0, bid[k]) + others[k])
                  for k in RESOURCES}
    score = sum(weights[k] * math.sqrt(allocation[k]) for k in RESOURCES) ** 2
    if allocation["compute"] + 1e-9 < float(profile.get("q_min", 0)):
        score *= 0.5
    if allocation["security"] + 1e-9 < float(profile.get("s_min", 0)):
        score *= 0.5
    return score


def _physics(profile: dict, history: list) -> tuple[float, float]:
    coefficient = 0.30 * (1 + float(profile.get("features", {}).get("mobility", 0)))
    samples = []
    for entry in history[-8:]:
        energy = float(entry.get("allocation", {}).get("energy", 0))
        if energy > 1e-6 and "battery_drawn" in entry:
            samples.append(max(1e-6, (float(entry["battery_drawn"]) - 0.004) / energy))
    if samples:
        coefficient = sum(samples) / len(samples)
    return coefficient, 0.22


def _kelly(budget: float, capacities: dict, profile: dict, others: dict,
           energy_limit: float, energy_cost: float = 0.0, coefficient: float = 0.3,
           recharge: float = 0.22) -> dict:
    lower = _floor_needs(capacities, profile, others)
    if sum(lower.values()) >= budget:
        # Floors can be mutually unaffordable under a noisy estimate. Do not
        # pretend scaling reservations down still guarantees either floor.
        candidates = [_normalize(lower, budget)]
        for k in ("compute", "security"):
            candidate = {r: 0.0 for r in RESOURCES}
            candidate[k] = min(budget, lower[k])
            other = "security" if k == "compute" else "compute"
            candidate[other] = budget - candidate[k]
            candidates.append(candidate)
        return max(candidates, key=lambda bid: _utility(bid, capacities, profile, others))
    limit = max(0, min(energy_limit, budget - lower["compute"] - lower["security"]))

    def split(energy: float) -> dict:
        available = budget - energy
        def value(compute: float) -> float:
            bid = {"compute": compute, "energy": energy, "security": available - compute}
            return _utility(bid, capacities, profile, others)
        compute = _maximize(value, lower["compute"], available - lower["security"], 16)
        return {"compute": compute, "energy": energy, "security": available - compute}

    def value(energy: float) -> float:
        bid = split(energy)
        share = max(0, capacities.get("energy", 1)) * energy / max(1e-9, energy + others["energy"])
        # Effective reward per work+recharge cycle, with a tunable drain price.
        return _utility(bid, capacities, profile, others) / (1 + energy_cost * (coefficient * share + 0.004) / recharge)

    energy = _maximize(value, 0.0, limit, 12)
    return _normalize(split(energy), budget)


def kelly(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """Kelly best response under the taper's energy allowance and reserved floors."""
    others = estimate_others(budget, profile, history)
    limit = taper(budget, prices, capacities, profile, history)["energy"]
    return _kelly(budget, capacities, profile, others, limit)


def _adaptive(budget: float, prices: dict, capacities: dict, profile: dict,
              history: list, energy_cost: float = 1.0) -> dict:
    others = estimate_others(budget, profile, history)
    coefficient, recharge = _physics(profile, history)
    # Keep a charge reserve. An uncertain market warrants a tighter allowance
    # as the battery falls, rather than trusting its estimated share exactly.
    capacity = max(1e-8, float(capacities.get("energy", 1)))
    share = max(0, min(0.90 * capacity, (_battery(profile) - 0.07 - 0.004) / coefficient))
    limit = others["energy"] * share / max(1e-8, capacity - share)
    limit = min(limit, taper(budget, prices, capacities, profile, history)["energy"] * 1.5)
    return _kelly(budget, capacities, profile, others, limit, energy_cost, coefficient, recharge)


def kelly_drain(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    return _adaptive(budget, prices, capacities, profile, history)


_learning: dict = {}


def reset_learning() -> None:
    """Used by isolated benchmark runs; process startup is naturally isolated."""
    _learning.clear()
    import sys
    module = sys.modules.get(f"{__package__}.adaptive")
    if module is not None:  # the adaptive planners keep per-run world-model state
        module.reset()


def episode_diagnostics() -> dict | None:
    """Predicted-versus-realized summary of the current run (adaptive planners only)."""
    import sys
    module = sys.modules.get(f"{__package__}.adaptive")
    return module.episode_diagnostics() if module else None


def ucb_energy(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """UCB selection among three energy prices, updated only by real feedback."""
    signature = tuple(profile.get("weights", {}).get(k, 0) for k in RESOURCES) + (
        profile.get("features", {}).get("mobility", 0),)
    latest = int(history[-1].get("round", 0)) if history else 0
    if (_learning.get("signature") != signature or latest < _learning.get("seen", 0)):
        reset_learning()
        _learning.update(signature=signature, seen=0, counts=[0, 0, 0], rewards=[0.0, 0.0, 0.0], pending=[])
    for entry in history:
        rnd = int(entry.get("round", 0))
        if rnd <= _learning["seen"]:
            continue
        actual = tuple(round(float(entry.get("bid", {}).get(k, 0)), 6) for k in RESOURCES)
        pending = _learning["pending"]
        matched = next((i for i, (_, bid) in enumerate(pending) if bid == actual), None)
        if matched is not None:
            arm, _ = pending.pop(matched)
            reward = float(entry.get("utility", 0)) / (1 + float(entry.get("battery_drawn", 0)) / 0.22)
            _learning["counts"][arm] += 1
            _learning["rewards"][arm] += reward
        _learning["seen"] = rnd
    counts = _learning["counts"]
    choices = [0.6, 1.0, 1.6]
    # Include unobserved decisions so delayed feedback does not repeatedly
    # explore the same arm before its first reward arrives.
    effective = [counts[i] + sum(arm == i for arm, _ in _learning["pending"]) for i in range(3)]
    arm = next((i for i, count in enumerate(effective) if not count), None)
    if arm is None:
        total = max(2, sum(effective))
        arm = max(range(3), key=lambda i: _learning["rewards"][i] / max(1, counts[i])
                  + 0.08 * math.sqrt(math.log(total) / max(1, effective[i])))
    bid = _adaptive(budget, prices, capacities, profile, history, choices[arm])
    _learning["pending"].append((arm, tuple(round(bid[k], 6) for k in RESOURCES)))
    _learning["pending"] = _learning["pending"][-20:]
    return bid


def kelly_blend(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """A conservative ensemble: taper plus the constrained Kelly policy."""
    first = taper(budget, prices, capacities, profile, history)
    second = kelly(budget, prices, capacities, profile, history)
    mix = 0.65
    bid = {k: (1 - mix) * first[k] + mix * second[k] for k in RESOURCES}
    return _reserve(bid, budget, _floor_needs(capacities, profile, estimate_others(budget, profile, history)))


def bot_aware(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    from .planner import opponent_aware
    return opponent_aware(budget, prices, capacities, profile, history)


def lookahead(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    from .planner import plan
    return plan(budget, prices, capacities, profile, history)


def ridge_value(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    from .planner import learned_plan
    return learned_plan(budget, prices, capacities, profile, history)


def ridge_terminal_4(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    from .planner import plan, load_value_model
    if load_value_model() is None:
        return kelly(budget, prices, capacities, profile, history)
    return plan(budget, prices, capacities, profile, history, horizon=4, terminal_model=True)


def ridge_terminal_6(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """Controlled six-round ridge comparator; same horizon and scenarios as lookahead."""
    from .planner import plan, load_value_model
    if load_value_model() is None:
        return kelly(budget, prices, capacities, profile, history)
    return plan(budget, prices, capacities, profile, history, horizon=6, terminal_model=True)


def catboost_terminal(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """Controlled six-round CatBoost terminal value, exported for stdlib inference."""
    from .planner import plan, load_catboost_model
    if load_catboost_model() is None:
        return lookahead(budget, prices, capacities, profile, history)
    return plan(budget, prices, capacities, profile, history, horizon=6, terminal_kind="catboost")


def lookahead_cutoff(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """lookahead with own/opponent battery-threshold candidates."""
    from .planner import plan
    return plan(budget, prices, capacities, profile, history, thresholds=True)


def lookahead_refine(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """lookahead with one bounded, causal branching point in the continuation."""
    from .planner import plan
    return plan(budget, prices, capacities, profile, history, refine=True)


def cycle_aware(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """Combine threshold candidates and bounded continuation improvement."""
    from .planner import plan
    return plan(budget, prices, capacities, profile, history, thresholds=True, refine=True)


def cycle_aware_diagnostics(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
    """cycle-aware's bids, plus predicted-versus-realized diagnostics (adaptive.py)."""
    from . import adaptive
    return adaptive.cycle_aware_diagnostics(budget, prices, capacities, profile, history)


def _adaptive_policy(key: str) -> Callable[..., dict]:
    def policy(budget: float, prices: dict, capacities: dict, profile: dict, history: list) -> dict:
        from . import adaptive
        return adaptive.decide(adaptive.CONFIGS[key], budget, prices, capacities, profile, history)
    policy.__name__ = key.replace("-", "_")
    return policy


# The adaptive planners (adaptive.py): online battery physics, market residual,
# noisy scenarios, probabilistic cutoffs, CVaR risk, dynamic horizon, strategy
# modes, the adaptive cycle-aware planner, bandit modes, rival archetypes, a
# learned shortlist, and the opponent-agnostic identified market (linear,
# logit, rational demand, robust crossings; no names or bot formulas).
ADAPTIVE = ["physics", "residual", "noisy-scenarios", "prob-cutoff", "cvar", "dynamic-horizon", "modes",
            "adaptive-cycle-aware", "linucb-modes", "archetype-learning", "learned-shortlist",
            "identified-linear", "identified-logit", "identified-structural", "identified-robust"]


STRATEGIES: dict[str, Callable[..., dict]] = {
    "template": template, "taper": taper, "floors": floors, "price-taker": price_taker,
    "market-taper": market_taper, "kelly": kelly, "kelly-drain": kelly_drain, "ucb-energy": ucb_energy,
    "kelly-blend": kelly_blend, "bot-aware": bot_aware, "lookahead": lookahead, "ridge-value": ridge_value,
    "ridge-terminal-4": ridge_terminal_4, "ridge-terminal-6": ridge_terminal_6,
    "catboost-terminal": catboost_terminal, "lookahead-cutoff": lookahead_cutoff,
    "lookahead-refine": lookahead_refine, "cycle-aware": cycle_aware,
    "cycle-aware-diagnostics": cycle_aware_diagnostics,
    **{key: _adaptive_policy(key) for key in ADAPTIVE},
}
