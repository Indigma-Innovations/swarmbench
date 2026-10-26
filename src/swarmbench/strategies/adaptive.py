"""The adaptive planners: the cycle-aware planner with measured extensions.

cycle-aware (see strategy.py) is the reference. Everything here is built so
that, with every feature switched off, the planner returns exactly
cycle-aware's bid. Each entry adds one measured component on top of that
baseline:

    cycle-aware-diagnostics  cycle-aware's bids plus predicted-versus-realized logging
    physics          online battery physics (alpha, beta, rho) used inside the rollouts
    residual         market residual: model error on rival demand is learned and added;
                     unknown participants and missing snapshots no longer force kelly
    noisy-scenarios  market and battery noise from residuals,
                     five common-random-number scenarios
    prob-cutoff      probabilistic cutoff reasoning: confidence-shifted crossing targets
                     and a P(desired transition) > tau gate on costly manipulations
    cvar             risk-aware MPC: (1-lambda) E[Q] + lambda CVaR_20%, by run progress
    dynamic-horizon  planning horizon from model confidence
    modes            explicit strategy modes selected by a deterministic rule
    adaptive-cycle-aware  the components selected on development seeds,
                     frozen before the holdout

Inputs are the same public data cycle-aware uses: the round payload, the
agent's own profile/results, and the public swarm snapshots. No arena import,
seed or future draw. The rollout random streams (61983, 61984, 61985) are
fixed planner constants.
"""

from dataclasses import dataclass, replace
import logging
import math
import random
from statistics import NormalDist

from . import strategy as base

RESOURCES = base.RESOURCES
LOG = logging.getLogger("agent.adaptive")
KNOWN_BOTS = {"bot-naive-max": "naive", "bot-even-split": "even", "bot-proportional": "prop"}
PRIOR_PHYSICS = (0.30, 0.004, 0.22)  # drain coefficient, idle drain, recharge
PHYSICS_BOUNDS = ((0.10, 0.90), (0.0, 0.03), (0.05, 0.60))
PHYSICS_TOLERANCE = (0.003, 0.0003, 0.003)
CUTOFF = 0.05
CROSSING_RIVALS = 3   # rivals considered for battery-crossing candidates (all of them in 4-node markets)
ZEROS = {"compute": 0.0, "energy": 0.0, "security": 0.0}
COLLECT = None  # a training script can install a decision recorder here
_NORMAL = NormalDist()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    """One planner personality. Defaults reproduce cycle-aware exactly."""

    physics: bool = False            # physics: estimated alpha/beta/rho
    residual: bool = False           # residual: additive rival-demand correction
    unknown_prior: bool = False      # residual: model unknown nodes instead of kelly
    impute: bool = False             # residual: one-step forecast for a missed snapshot
    scenarios: int = 3               # outer future paths
    noise: bool = False              # noisy-scenarios: market/battery noise in scenarios
    noise_battery: bool = True       # noisy-scenarios: also perturb rival battery transitions
    noise_scale: float = 1.0         # multiplier on measured error scales
    prob_cutoff: bool = False        # prob-cutoff
    tau: float = 0.7                 # prob-cutoff: confidence gate
    sacrifice: float = 0.01          # prob-cutoff: immediate-utility loss needing the gate
    cutoff_margin: float = 0.0       # fixed crossing margin delta (targets 0.05 +- delta)
    margin_k: float = 0.0            # identified-robust: per-rival margin = k * measured battery forecast RMS
    risk: tuple = (0.0, 0.0, 0.0)    # cvar: lambda for early / middle / late run
    horizon: int = 6
    dynamic_horizon: bool = False    # dynamic-horizon
    horizon_low_error: int = 6       # development: 8 cost -1.7%
    horizon_high_error: int = 4
    exact_tail: int = 6              # dynamic-horizon: plan to the end when this close
    terminal_own: float = 1.2
    terminal_others: float = 0.15
    opponent_thresholds: bool = True
    refine: bool = True
    refine_top: int = 3              # cycle-aware refines its three best bids
    antithetic: bool = False         # mirrored scenario pairs (variance reduction)
    modes: bool = False              # modes
    learn_opponents: bool = False    # archetype-learning (see opponents.py)
    identify: bool = False           # identified-linear: rivals identified from telemetry, names ignored
    identify_model: str = "linear"   # identified-logit: "logit" price-responsive demand system
    bandit: bool = False             # linucb-modes (see bandit.py)
    shortlist_model: bool = False    # learned-shortlist (see shortlist.py)
    shortlist_size: int = 7


# ---------------------------------------------------------------------------
# Lightweight world model: same arithmetic as planner.py, no deepcopy
# ---------------------------------------------------------------------------
class Spec:
    """Static public description of one competitor."""

    __slots__ = ("team", "kind", "weights", "q", "s", "mf", "active", "ejected",
                 "blocked", "model", "node")

    def __init__(self, node: dict, kind: str):
        self.node = node
        self.team = node.get("team", "")
        self.kind = kind
        weights = node.get("weights", {})
        self.weights = {k: float(weights.get(k, 1 / 3)) for k in RESOURCES}
        self.q = float(node.get("q_min", 0))
        self.s = float(node.get("s_min", 0))
        self.mf = 1 + float(node.get("features", {}).get("mobility", 0))
        self.active = bool(node.get("active", True))
        self.ejected = bool(node.get("ejected"))
        self.blocked = self.ejected or not self.active or self.q + self.s >= 0.99
        self.model = None


class Me:
    __slots__ = ("w", "q", "s", "mf")

    def __init__(self, profile: dict):
        self.w = base._weights(profile)
        self.q = float(profile.get("q_min", 0))
        self.s = float(profile.get("s_min", 0))
        self.mf = 1 + float(profile.get("features", {}).get("mobility", 0))


def proportional_bid(spec: Spec, budget: float, prices: dict, caps: dict) -> dict:
    """planner.predict_bot for bot-proportional, verbatim arithmetic."""
    w = spec.weights
    scores = {k: w[k] ** 2 * float(caps.get(k, 1)) / max(0.05, float(prices.get(k, 1)))
              for k in RESOURCES}
    bid = base._normalize(scores, budget)
    for k, floor in (("compute", spec.q), ("security", spec.s)):
        cap = float(caps.get(k, 1))
        target = min(0.95 * cap, 1.2 * floor)
        if target <= 0 or target >= cap:
            continue
        needed = target / (cap - target)
        deficit = needed - bid[k]
        if deficit <= 0:
            continue
        donors = [r for r in RESOURCES if r != k and bid[r] > 0]
        available = sum(bid[r] for r in donors)
        headroom = max(0, budget - sum(bid.values()))
        take = min(deficit, headroom + available)
        from_donors = take - min(take, headroom)
        if available > 1e-9:
            for r in donors:
                bid[r] -= from_donors * bid[r] / available
        bid[k] += take
    return base._normalize(bid, budget)


def predict(spec: Spec, battery: float, budget: float, prices: dict, caps: dict,
            draw: float | None = None) -> dict:
    if spec.blocked or battery <= CUTOFF:
        return ZEROS
    kind = spec.kind
    if kind == "naive":
        return {k: budget * spec.weights[k] for k in RESOURCES}
    if kind == "even":
        return {k: budget / 3 for k in RESOURCES}
    if kind == "prop":
        return proportional_bid(spec, budget, prices, caps)
    if spec.model is not None:
        return spec.model.predict(spec, battery, budget, prices, caps, draw)
    return {k: budget / 3 for k in RESOURCES}  # uninformed prior for an unknown node


def utility(bid: dict, caps: dict, me: Me, others: dict) -> float:
    """strategy._utility with the weights normalized once."""
    w = me.w
    bc, be, bs = max(0, bid["compute"]), max(0, bid["energy"]), max(0, bid["security"])
    ac = max(0, caps.get("compute", 1)) * bc / max(1e-9, bc + others["compute"])
    ae = max(0, caps.get("energy", 1)) * be / max(1e-9, be + others["energy"])
    as_ = max(0, caps.get("security", 1)) * bs / max(1e-9, bs + others["security"])
    # sum(), not a+b+c: Python >= 3.12 sums floats with compensation, as cycle-aware does.
    score = sum((w["compute"] * math.sqrt(ac), w["energy"] * math.sqrt(ae),
                 w["security"] * math.sqrt(as_))) ** 2
    if ac + 1e-9 < me.q:
        score *= 0.5
    if as_ + 1e-9 < me.s:
        score *= 0.5
    return score


def floor_needs(caps: dict, me: Me, others: dict, margin: float) -> dict:
    lower = {k: 0.0 for k in RESOURCES}
    for k, floor in (("compute", me.q), ("security", me.s)):
        cap = max(1e-8, float(caps.get(k, 1)))
        target = min(0.98 * cap, max(0, floor) * margin)
        lower[k] = max(0.0, others[k]) * target / max(1e-8, cap - target)
    return lower


def split_energy(energy: float, budget: float, caps: dict, me: Me, others: dict) -> dict:
    energy = min(max(0, energy), budget)
    available = budget - energy
    lower = floor_needs(caps, me, others, 1.002)
    low, high = lower["compute"], available - lower["security"]

    def value(compute: float) -> float:
        return utility({"compute": compute, "energy": energy, "security": available - compute},
                       caps, me, others)
    if low <= high:
        compute = base._maximize(value, low, high, 14)
    else:
        candidates = [0, available, min(available, low), max(0, high)]
        candidates += [available * i / 12 for i in range(1, 12)]
        compute = max(candidates, key=value)
    bid = {"compute": max(0, compute), "energy": energy, "security": max(0, available - compute)}
    return base._normalize(bid, budget)


def taper_energy(budget: float, me: Me, battery: float) -> float:
    keep = max(0.0, (battery - 0.05) / 0.95) ** 1.0
    bid = {k: budget * me.w[k] for k in RESOURCES}
    freed = bid["energy"] * (1 - keep)
    bid["energy"] *= keep
    nonenergy = me.w["compute"] + me.w["security"] or 1
    for k in ("compute", "security"):
        bid[k] += freed * me.w[k] / nonenergy
    return base._normalize(bid, budget)["energy"]


def continuation(own: float, others: dict, budget: float, caps: dict, me: Me) -> dict:
    if own <= CUTOFF:
        return ZEROS
    energy = budget * me.w["energy"] * max(0, (own - 0.05) / 0.95)
    return split_energy(energy, budget, caps, me, others)


class World:
    """Everything the rollouts need for one decision."""

    def __init__(self, me: Me, specs: list, physics: tuple, rate: dict | None,
                 sigma_market: dict | None, sigma_battery: list | None, cfg: Config):
        self.me, self.specs, self.physics, self.cfg = me, specs, physics, cfg
        self.rate = rate                  # residual demand per unit wallet
        self.sigma_market = sigma_market  # per unit wallet
        self.sigma_battery = sigma_battery
        self.sigma_battery_own = 5e-5
        self.shortlist = None
        self.inner_futures = None      # experiments only: perfect-foresight bound
        self.outer_override = None

    def predict_all(self, bats: list, budget: float, prices: dict, caps: dict,
                    draws: list | None = None) -> list:
        if draws is None:
            return [predict(s, b, budget, prices, caps) for s, b in zip(self.specs, bats)]
        return [predict(s, b, budget, prices, caps, d) for s, b, d in zip(self.specs, bats, draws)]

    def sums(self, preds: list, budget: float) -> dict:
        totals = {k: sum(p[k] for p in preds) for k in RESOURCES}
        if self.rate is not None:
            totals = {k: max(0.0, totals[k] + self.rate[k] * budget) for k in RESOURCES}
        return totals

    def step(self, own: float, bats: list, budget: float, prices: dict, caps: dict,
             bid: dict, preds: list, sums: dict, battery_noise: list | None = None):
        """One simultaneous auction; planner.transition's arithmetic."""
        alpha, beta, rho = self.physics
        own_active = own > CUTOFF
        totals = {k: (bid[k] if own_active else 0) + sums[k] for k in RESOURCES}
        if own_active:
            alloc_e = caps["energy"] * bid["energy"] / max(1e-9, totals["energy"])
            others = {k: totals[k] - bid[k] for k in RESOURCES}
            value = utility(bid, caps, self.me, others)
            next_own = round(max(0, own - alpha * self.me.mf * alloc_e - beta), 4)
        else:
            value = 0
            next_own = round(min(1, own + rho), 4)
        next_bats = []
        for index, (spec, battery, pred) in enumerate(zip(self.specs, bats, preds)):
            if spec.ejected:
                next_bats.append(battery)
                continue
            if sum(pred.values()) > 0:
                share = caps["energy"] * pred["energy"] / max(1e-9, totals["energy"])
                battery = max(0, battery - alpha * spec.mf * share - beta)
            else:
                battery = min(1, battery + rho)
            if battery_noise is not None:
                battery = min(1, max(0, battery + battery_noise[index]))
            next_bats.append(round(battery, 4))
        next_prices = {k: round(max(0.01, totals[k] / max(1e-9, caps[k])), 6) for k in RESOURCES}
        return value, next_own, next_bats, next_prices

    def terminal(self, own: float, bats: list) -> float:
        return self.cfg.terminal_own * own - self.cfg.terminal_others * sum(bats)


def energy_candidates(budget: float, caps: dict, me: Me, own: float, others: dict) -> list:
    cap = float(caps["energy"])
    amounts = [0.0, budget * 1e-5]
    for share in (0.015, 0.03, 0.055, 0.085, 0.125, 0.18, 0.25, 0.36, 0.5, 0.7):
        target = min(cap * 0.95, share)
        amounts.append(min(budget, others["energy"] * target / max(1e-9, cap - target)))
    amounts.append(taper_energy(budget, me, own))
    return [split_energy(e, budget, caps, me, others) for e in sorted(set(round(e, 8) for e in amounts))]


def threshold_candidates(world: World, budget: float, caps: dict, own: float, bats: list,
                         preds: list, others: dict, own_targets=(0.0498, 0.0502),
                         opponent_targets=None, opponents: bool = True):
    """planner.threshold_candidates, generalized; returns (bids, tags)."""
    me = world.me
    alpha, beta, _ = world.physics
    candidates = energy_candidates(budget, caps, me, own, others)
    tags = [None] * len(candidates)
    amounts = {bid["energy"]: None for bid in candidates}
    cap, demand = float(caps["energy"]), others["energy"]
    coefficient = alpha * me.mf
    for target in own_targets:
        share = (own - beta - target) / coefficient
        if demand > 0 and 0 < share < cap:
            amounts.setdefault(demand * share / (cap - share), ("own", target))
    if opponents:
        # Large markets: only the rivals closest to the cutoff can be pushed
        # across it; with up to CROSSING_RIVALS rivals all are considered,
        # exactly as in the published 4-node results.
        eligible = [i for i, b in enumerate(preds) if b["energy"] > 0]
        if len(eligible) > CROSSING_RIVALS:
            eligible = set(sorted(eligible, key=lambda i: (bats[i], i))[:CROSSING_RIVALS])
        for index, (spec, battery, bid) in enumerate(zip(world.specs, bats, preds)):
            if bid["energy"] <= 0 or index not in eligible:
                continue
            targets = opponent_targets[index] if opponent_targets else (0.0498, 0.0502)
            for target in targets:
                drain = battery - beta - target
                if drain <= 0:
                    continue
                amounts.setdefault(alpha * spec.mf * cap * bid["energy"] / drain - demand,
                                   (index, target))
    known = {round(bid["energy"], 8) for bid in candidates}
    rounded = {}
    for amount, tag in amounts.items():
        if math.isfinite(amount) and 0 <= amount <= budget:
            rounded.setdefault(round(amount, 8), tag)
    for amount in sorted(set(rounded) - known):
        candidates.append(split_energy(amount, budget, caps, me, others))
        tags.append(rounded[amount])
    return candidates, tags


_DRAWS: dict = {}


def outer_scenarios(count: int, depth: int, antithetic: bool = False) -> list:
    """lookahead's capacity/wallet paths. The first three never depend on count.

    Antithetic: count/2 paths plus their mirror images about the mean (1.0),
    a classical variance-reduction device for comparing candidates."""
    if antithetic:
        key = ("anti", count, depth)
        if key not in _DRAWS:
            half = outer_scenarios(max(1, count // 2), depth)
            mirror = [[({k: 2.0 - v for k, v in caps.items()}, 2.0 - wallet) for caps, wallet in path]
                      for path in half]
            _DRAWS[key] = [p for pair in zip(half, mirror) for p in pair]
        return _DRAWS[key]
    key = ("outer", count, depth)
    if key not in _DRAWS:
        rng = random.Random(61983)
        _DRAWS[key] = [[({k: rng.uniform(0.7, 1.3) for k in RESOURCES}, rng.uniform(0.75, 1.25))
                        for _ in range(depth - 1)] for _ in range(count)]
    return _DRAWS[key]


def inner_futures() -> list:
    if "inner" not in _DRAWS:
        rng = random.Random(61984)
        _DRAWS["inner"] = [({k: rng.uniform(0.7, 1.3) for k in RESOURCES}, rng.uniform(0.75, 1.25))
                           for _ in range(3)]
    return _DRAWS["inner"]


def noise_draws(count: int, depth: int, nodes: int) -> list:
    """Standard normals and uniforms shared by every candidate (common random numbers)."""
    key = ("noise", count, depth, nodes)
    if key not in _DRAWS:
        rng = random.Random(61985)
        _DRAWS[key] = [[([rng.gauss(0, 1) for _ in RESOURCES], [rng.gauss(0, 1) for _ in range(nodes)])
                         for _ in range(depth)] for _ in range(count)]
        rng = random.Random(61986)
        _DRAWS[key + ("u",)] = [[rng.random() for _ in range(nodes)] for _ in range(count)]
    return _DRAWS[key], _DRAWS[key + ("u",)]


def two_step(world: World, own: float, bats: list, budget: float, prices: dict, caps: dict,
             remaining: int, preds: list, sums: dict, thresholds: bool = True) -> dict:
    """planner.two_step_continuation on the light state (causal, nominal)."""
    if own <= CUTOFF:
        return ZEROS
    if thresholds:
        candidates, _ = threshold_candidates(world, budget, caps, own, bats, preds, sums,
                                             opponents=world.cfg.opponent_thresholds)
    else:
        candidates = energy_candidates(budget, caps, world.me, own, sums)
    futures = (world.inner_futures or inner_futures()) if remaining > 1 else []
    steps = None
    if world.shortlist is not None:
        tags = [None] * len(candidates)
        steps = [world.step(own, bats, budget, prices, caps, bid, preds, sums) for bid in candidates]
        candidates, _, steps = world.shortlist(world, candidates, tags, steps, own, bats, remaining)
        steps = {id(bid): step for bid, step in zip(candidates, steps)}

    def value(bid: dict) -> float:
        if steps is not None:
            reward, after, competitors, next_prices = steps[id(bid)]
        else:
            reward, after, competitors, next_prices = world.step(own, bats, budget, prices, caps, bid, preds, sums)
        total = 0.0
        for caps2, wallet in futures:
            preds2 = world.predict_all(competitors, wallet, next_prices, caps2)
            sums2 = world.sums(preds2, wallet)
            action = continuation(after, sums2, wallet, caps2, world.me)
            value2, last, others_last, _ = world.step(after, competitors, wallet, next_prices, caps2,
                                                      action, preds2, sums2)
            terminal = world.terminal(last, others_last) if remaining > 2 else 0
            total += value2 + terminal
        return reward + total / len(futures) if futures else reward
    return max(candidates, key=value)


def cvar_mix(values: list, lam: float) -> float:
    total = 0.0
    for value in values:  # cycle-aware accumulates path values sequentially
        total += value
    mean = total / len(values)
    if lam <= 0:
        return mean
    tail = sorted(values)[:max(1, round(0.2 * len(values)))]
    return (1 - lam) * mean + lam * sum(tail) / len(tail)


def plan_core(world: World, budget: float, prices: dict, caps: dict, own: float, bats: list,
              remaining: int, depth: int, lam: float = 0.0, thresholds: bool = True,
              targets=None, shortlist=None) -> tuple[dict, dict]:
    """The cycle-aware MPC. Returns (bid, diagnostics for the chosen bid)."""
    cfg = world.cfg
    preds0 = world.predict_all(bats, budget, prices, caps)
    sums0 = world.sums(preds0, budget)
    if thresholds:
        own_targets, opponent_targets = targets or ((0.0498, 0.0502), None)
        candidates, tags = threshold_candidates(world, budget, caps, own, bats, preds0, sums0,
                                                own_targets, opponent_targets, cfg.opponent_thresholds)
    else:
        candidates = energy_candidates(budget, caps, world.me, own, sums0)
        tags = [None] * len(candidates)
    nominal = [world.step(own, bats, budget, prices, caps, bid, preds0, sums0) for bid in candidates]
    if cfg.prob_cutoff:
        candidates, tags, nominal = cutoff_gate(world, candidates, tags, nominal)
    if shortlist is not None:
        candidates, tags, nominal = shortlist(world, candidates, tags, nominal, own, bats, remaining)
    scenarios = world.outer_override or outer_scenarios(cfg.scenarios, depth, cfg.antithetic)
    noisy = cfg.noise and (world.sigma_market is not None or world.sigma_battery is not None)
    if noisy:
        noise, uniforms = noise_draws(len(scenarios), depth, len(world.specs))
    sm = world.sigma_market or {k: 0.0 for k in RESOURCES}
    sb = world.sigma_battery or [0.0] * len(world.specs)
    learned = any(spec.model is not None and getattr(spec.model, "stochastic", False)
                  for spec in world.specs)

    def realized(sums: dict, z: list, wallet: float) -> dict:
        return {k: max(0.0, sums[k] + sm[k] * wallet * zk) for k, zk in zip(RESOURCES, z)}

    def q_values(index: int, improved: bool) -> list:
        bid = candidates[index]
        results = []
        for s, scenario in enumerate(scenarios):
            draws = uniforms[s] if noisy and learned else None
            if noisy:
                zm, zb = noise[s][0]
                p0 = world.predict_all(bats, budget, prices, caps, draws) if draws else preds0
                s0 = world.sums(p0, budget) if draws else sums0
                reward, cur_own, cur_bats, cur_prices = world.step(
                    own, bats, budget, prices, caps, bid, p0, realized(s0, zm, budget),
                    [sigma * z for sigma, z in zip(sb, zb)])
            else:
                reward, cur_own, cur_bats, cur_prices = nominal[index]
            score = reward
            for step, (step_caps, wallet) in enumerate(scenario):
                preds = world.predict_all(cur_bats, wallet, cur_prices, step_caps, draws)
                sums = world.sums(preds, wallet)
                if improved and step == 0:
                    action = two_step(world, cur_own, cur_bats, wallet, cur_prices, step_caps,
                                      remaining - 1, preds, sums, thresholds)
                else:
                    action = continuation(cur_own, sums, wallet, step_caps, world.me)
                if noisy:
                    zm, zb = noise[s][step + 1]
                    value, cur_own, cur_bats, cur_prices = world.step(
                        cur_own, cur_bats, wallet, cur_prices, step_caps, action, preds,
                        realized(sums, zm, wallet), [sigma * z for sigma, z in zip(sb, zb)])
                else:
                    value, cur_own, cur_bats, cur_prices = world.step(
                        cur_own, cur_bats, wallet, cur_prices, step_caps, action, preds, sums)
                score += value
            if remaining - depth:
                score += world.terminal(cur_own, cur_bats)
            results.append(score)
        return results

    cache: dict = {}

    def value(index: int, improved: bool = False) -> float:
        key = (index, improved)
        if key not in cache:
            cache[key] = cvar_mix(q_values(index, improved), lam)
        return cache[key]
    order = list(range(len(candidates)))
    if cfg.refine and depth > 1:
        shortlisted = sorted(order, key=value, reverse=True)[:cfg.refine_top]
        chosen = max(shortlisted, key=lambda i: value(i, True))
        improved = True
    else:
        chosen = max(order, key=value)
        improved = False
    info = {"value": value(chosen, improved), "tag": tags[chosen], "nominal": nominal[chosen],
            "candidates": len(candidates), "preds": preds0, "sums": sums0, "chosen": chosen,
            "all_candidates": candidates, "all_tags": tags, "all_nominal": nominal,
            "values": {i: v for (i, imp), v in cache.items() if not imp}}
    return candidates[chosen], info


def cutoff_gate(world: World, candidates: list, tags: list, nominal: list):
    """prob-cutoff: drop costly crossing bids unlikely to produce their transition."""
    cfg = world.cfg
    sigma_own = max(5e-5, world.sigma_battery_own)
    sb = world.sigma_battery or [5e-5] * len(world.specs)
    best = max((n[0] for n, t in zip(nominal, tags) if t is None), default=0.0)
    keep = []
    for bid, tag, nom in zip(candidates, tags, nominal):
        if tag is not None and nom[0] < best * (1 - cfg.sacrifice):
            who, target = tag
            predicted = nom[1] if who == "own" else nom[2][who]
            sigma = sigma_own if who == "own" else max(5e-5, sb[who])
            sleep = _NORMAL.cdf((CUTOFF - predicted) / sigma)
            if (sleep if target < CUTOFF else 1 - sleep) < cfg.tau:
                continue
        keep.append((bid, tag, nom))
    return [k[0] for k in keep], [k[1] for k in keep], [k[2] for k in keep]


# ---------------------------------------------------------------------------
# Online statistics
# ---------------------------------------------------------------------------
class EW:
    """Exponentially weighted mean and second moment with a decaying prior."""

    def __init__(self, lam: float, prior_mean: float = 0.0, prior_sd: float = 0.0,
                 prior_weight: float = 0.0):
        self.lam, self.n = lam, 0
        self.w = prior_weight
        self.s1 = prior_mean * prior_weight
        self.s2 = (prior_sd ** 2 + prior_mean ** 2) * prior_weight

    def add(self, x: float) -> None:
        self.w = self.lam * self.w + 1
        self.s1 = self.lam * self.s1 + x
        self.s2 = self.lam * self.s2 + x * x
        self.n += 1

    @property
    def mean(self) -> float:
        return self.s1 / self.w if self.w else 0.0

    @property
    def rms(self) -> float:
        return math.sqrt(max(0.0, self.s2 / self.w)) if self.w else 0.0

    @property
    def sd(self) -> float:
        return math.sqrt(max(0.0, self.s2 / self.w - self.mean ** 2)) if self.w else 0.0


class Cum:
    """Plain cumulative error summary for reporting (MAE, RMSE, bias)."""

    def __init__(self):
        self.n, self.total, self.absolute, self.square = 0, 0.0, 0.0, 0.0

    def add(self, error: float) -> None:
        self.n += 1
        self.total += error
        self.absolute += abs(error)
        self.square += error * error

    def summary(self) -> dict:
        if not self.n:
            return {"n": 0}
        return {"n": self.n, "mae": self.absolute / self.n, "rmse": math.sqrt(self.square / self.n),
                "bias": self.total / self.n}


class Physics:
    """Bayesian weighted least squares for drawn = alpha*(1+m)*x_E + beta,
    plus a shrunk mean for the recharge rho. Priors are the published constants."""

    def __init__(self, lam: float = 0.98, noise_sd: float = 0.002):
        a0, b0, r0 = PRIOR_PHYSICS
        self.prior = [[noise_sd ** 2 / 0.05 ** 2, 0.0], [0.0, noise_sd ** 2 / 0.002 ** 2]]
        self.prior_b = [self.prior[0][0] * a0, self.prior[1][1] * b0]
        self.data = [[0.0, 0.0], [0.0, 0.0]]
        self.data_b = [0.0, 0.0]
        self.lam, self.drains = lam, 0
        self.rho = EW(0.95, r0, 0.0, 2.0)

    def add_drain(self, z: float, drawn: float) -> None:
        lam = self.lam
        x = (z, 1.0)
        for i in range(2):
            self.data_b[i] = lam * self.data_b[i] + x[i] * drawn
            for j in range(2):
                self.data[i][j] = lam * self.data[i][j] + x[i] * x[j]
        self.drains += 1

    def add_recharge(self, gain: float) -> None:
        if 0 < gain < 1:
            self.rho.add(gain)

    def estimate(self) -> tuple:
        a = [[self.prior[i][j] + self.data[i][j] for j in range(2)] for i in range(2)]
        b = [self.prior_b[i] + self.data_b[i] for i in range(2)]
        det = a[0][0] * a[1][1] - a[0][1] * a[1][0]
        if det <= 0:
            alpha, beta = PRIOR_PHYSICS[:2]
        else:
            alpha = (b[0] * a[1][1] - a[0][1] * b[1]) / det
            beta = (a[0][0] * b[1] - a[1][0] * b[0]) / det
        rho = self.rho.mean
        (la, ha), (lb, hb), (lr, hr) = PHYSICS_BOUNDS
        estimate = (min(ha, max(la, alpha)), min(hb, max(lb, beta)), min(hr, max(lr, rho)))
        # Conservative update: keep each published constant until the data
        # contradict it by more than rounding noise could explain.
        return tuple(prior if abs(value - prior) < tolerance else value
                     for value, prior, tolerance in zip(estimate, PRIOR_PHYSICS, PHYSICS_TOLERANCE))


# ---------------------------------------------------------------------------
# The tracker: predictions versus what actually happened
# ---------------------------------------------------------------------------
class Tracker:
    def __init__(self):
        self.key = None
        self.last_round = 0
        self.decisions: dict = {}
        self.snapshots: dict = {}      # round -> {team: node dict}, real observations only
        self.believed: dict = {}       # round -> {team: node dict} imputed for a missing snapshot
        self.imputed = 0
        self.seen_history: set = set()
        self.market_done: set = set()
        self.physics = Physics()
        self.residual = {k: EW(0.85, 0.0, 0.0, 1.0) for k in RESOURCES}
        self.residual_fast = {k: EW(0.5) for k in RESOURCES}
        # Weak priors (a quarter of one observation): noise follows measured
        # errors, as specified, rather than an assumed uncertainty.
        self.market_error = {k: EW(0.85, 0.0, 0.05, 0.25) for k in RESOURCES}  # per wallet
        self.battery_error = EW(0.9, 0.0, 0.003, 0.25)
        self.own_battery_error = EW(0.9, 0.0, 0.003, 0.25)
        # Per rival, with a deliberately wide prior (0.01, one observation): a
        # rival is presumed unpredictable until its forecasts have been right.
        self.battery_error_by: dict = {}
        self.report = {"market_model": {k: Cum() for k in RESOURCES},
                       "market_used": {k: Cum() for k in RESOURCES},
                       "market_alloc_vs_price": Cum(),
                       "own_battery": Cum(), "opponent_battery": Cum(),
                       "awake": {"tp": 0, "tn": 0, "fp": 0, "fn": 0},
                       "drawn": Cum(), "recharge": Cum()}
        self.rows: list = []
        self.opponent_energy: dict = {}   # team -> [(round, fraction, battery, prices, caps, wallet)]
        self.fallbacks = 0
        self.modes: dict = {}
        self.extra: dict = {}             # state owned by learning modules
        self.extra_summary: dict = {}
        self.own_seen: dict = {}          # round -> own battery at that decision
        self.mobility = 1.0

    # ------------------------------------------------------------ ingest
    def ingest(self, round_index: int, budget: float, prices: dict, caps: dict,
               profile: dict, history: list) -> None:
        self.own_seen[round_index] = base._battery(profile)
        nodes = (profile.get("_market") or {}).get("nodes") or []
        if nodes:
            self.snapshots[round_index] = {n.get("team", ""): n for n in nodes}
        alpha, beta, _ = self.physics.estimate()
        # Price-based realized rival demand of the previous round: lag one.
        previous = self.decisions.get(round_index - 1)
        if previous and previous.get("caps"):
            realized = {}
            for k in RESOURCES:
                price = float(prices.get(k, 0))
                if price > 0.0100001:
                    realized[k] = price * float(previous["caps"][k]) - previous["bid"][k]
            if len(realized) == len(RESOURCES):
                self._market(round_index - 1, realized, "price")
        # Own settled results: physics, own battery, allocation-based demand.
        for entry in history:
            index = int(entry.get("round", 0))
            if index in self.seen_history:
                continue
            self.seen_history.add(index)
            allocation, bid = entry.get("allocation", {}), entry.get("bid", {})
            if "battery_drawn" in entry:
                z = self.mobility * float(allocation.get("energy", 0))
                record = self.decisions.get(index)
                if record and record.get("physics"):
                    a, b, _ = record["physics"]
                    self.report["drawn"].add(float(entry["battery_drawn"]) - (a * z + b))
                self.physics.add_drain(z, float(entry["battery_drawn"]))
            realized = {}
            for k in RESOURCES:
                own, share = float(bid.get(k, 0)), float(allocation.get(k, 0))
                capacity = float(entry.get("capacities", {}).get(k, 0))
                if own > 1e-8 and share > 1e-8 and capacity > 0:
                    realized[k] = own * (capacity / share - 1)
            record = self.decisions.get(index)
            if record is not None:
                record["S_alloc"] = realized
                if "battery" in entry and record.get("own_next") is not None:
                    error = float(entry["battery"]) - record["own_next"]
                    self.report["own_battery"].add(error)
                    self.own_battery_error.add(error)
                    record["own_actual"] = float(entry["battery"])
                if record.get("S_price"):
                    for k in realized:
                        self.report["market_alloc_vs_price"].add(realized[k] - record["S_price"][k])
            if len(realized) == len(RESOURCES) and index not in self.market_done:
                self._market(index, realized, "allocation")
            # Own recharge: a known post-round battery at or below the cutoff,
            # then the next observed battery after k idle rounds.
            if "battery" in entry and float(entry["battery"]) <= CUTOFF:
                later = [r for r in self.own_seen if r > index + 1]
                if later and self.own_seen[min(later)] < 0.9999:
                    nxt = min(later)
                    self.physics.add_recharge((self.own_seen[nxt] - float(entry["battery"])) / (nxt - index - 1))
        # Opponents: battery forecasts, awake status, recharge, energy bids.
        now, before = self.snapshots.get(round_index), self.snapshots.get(round_index - 1)
        record = self.decisions.get(round_index - 1)
        if now and record and record.get("opp_next"):
            for team, predicted in record["opp_next"].items():
                node = now.get(team)
                if node is None:
                    continue
                actual = float(node["features"]["battery"])
                error = actual - predicted
                self.report["opponent_battery"].add(error)
                self.battery_error.add(error)
                self.battery_error_by.setdefault(team, EW(0.8, 0.0, 0.01, 1.0)).add(error)
                awake_pred, awake = predicted > CUTOFF, actual > CUTOFF
                key = ("t" if awake_pred == awake else "f") + ("p" if awake_pred else "n")
                self.report["awake"][key] += 1
                record.setdefault("opp_actual", {})[team] = actual
        if now and before:
            rho = self.physics.estimate()[2]
            for team, node in now.items():
                old = before.get(team)
                if old is None or old.get("ejected") or node.get("ejected"):
                    continue
                b0, b1 = float(old["features"]["battery"]), float(node["features"]["battery"])
                if b0 <= CUTOFF:
                    if b1 < 0.9999:
                        self.report["recharge"].add((b1 - b0) - rho)
                        self.physics.add_recharge(b1 - b0)
                elif b1 > 0 and record and record.get("wallet") and old.get("active", True):
                    # Public battery telemetry identifies each rival's energy share.
                    mf = 1 + float(old["features"].get("mobility", 0))
                    share = max(0.0, (b0 - b1 - beta) / (alpha * mf))
                    fraction = share * float(prices.get("energy", 0)) / record["wallet"]
                    self.opponent_energy.setdefault(team, []).append(
                        (round_index - 1, fraction, b0, record.get("prices"), record.get("caps"),
                         record["wallet"]))
        for old in [r for r in self.snapshots if r < round_index - 3]:
            del self.snapshots[old]
        for old in [r for r in self.own_seen if r < round_index - 12]:
            del self.own_seen[old]
        self.last_round = round_index

    def _market(self, index: int, realized: dict, source: str) -> None:
        record = self.decisions.get(index)
        if record is None or index in self.market_done or not record.get("S_model"):
            return
        self.market_done.add(index)
        record["S_" + source] = realized
        wallet = record["wallet"]
        row = {"round": index, "source": source}
        for k in RESOURCES:
            model_error = realized[k] - record["S_model"][k]
            used_error = realized[k] - record["S_used"][k]
            self.report["market_model"][k].add(model_error)
            self.report["market_used"][k].add(used_error)
            self.residual[k].add(model_error / wallet)
            self.residual_fast[k].add(model_error / wallet)
            self.market_error[k].add(used_error / wallet)
            row[k] = {"pred": record["S_used"][k], "model": record["S_model"][k], "real": realized[k]}
        self.rows.append(row)
        LOG.info("market r%d (%s) %s", index, source, " ".join(
            f"{k[:3]}:pred={row[k]['pred']:.4f},real={row[k]['real']:.4f}" for k in RESOURCES))

    # ------------------------------------------------------------ record
    def record(self, round_index: int, budget: float, prices: dict, caps: dict, own: float,
               bid: dict, s_model: dict | None, s_used: dict | None, own_next: float | None,
               opp_next: dict | None, physics: tuple | None, mode: str | None = None) -> None:
        self.decisions[round_index] = {
            "wallet": budget, "prices": dict(prices), "caps": dict(caps), "bid": dict(bid),
            "own_battery": own, "S_model": s_model, "S_used": s_used, "own_next": own_next,
            "opp_next": opp_next, "physics": physics, "mode": mode}
        if mode:
            self.modes[mode] = self.modes.get(mode, 0) + 1
        for old in [r for r in self.decisions if r < round_index - 12]:
            del self.decisions[old]
        if round_index % 10 == 0:
            LOG.info("diagnostics r%d %s", round_index, self.brief())

    # ------------------------------------------------------------ queries
    def residual_rate(self) -> dict:
        """Mean residual demand per unit wallet, zero unless significant."""
        rate = {}
        for k in RESOURCES:
            stat = self.residual[k]
            n_eff = max(1.0, stat.w)
            significant = abs(stat.mean) > max(1e-3, 2 * stat.sd / math.sqrt(n_eff))
            rate[k] = stat.mean if stat.n >= 2 and significant else 0.0
        return rate

    def market_sigma(self) -> dict:
        return {k: self.market_error[k].rms for k in RESOURCES}

    def battery_sigma(self) -> float:
        return self.battery_error.rms

    def confidence(self) -> dict:
        return {"market": sum(self.market_error[k].rms for k in RESOURCES) / 3,
                "battery": self.battery_error.rms, "own_battery": self.own_battery_error.rms}

    def brief(self) -> str:
        c = self.confidence()
        a, b, r = self.physics.estimate()
        return (f"alpha={a:.4f} beta={b:.4f} rho={r:.4f} market_rms={c['market']:.4f} "
                f"battery_rms={c['battery']:.4f} modes={self.modes}")

    def summary(self) -> dict:
        report = {}
        for name, value in self.report.items():
            if isinstance(value, Cum):
                report[name] = value.summary()
            elif name.startswith("market"):
                report[name] = {k: v.summary() for k, v in value.items()}
            else:
                report[name] = dict(value)
        awake = report["awake"]
        total = sum(awake.values())
        awake["accuracy"] = (awake["tp"] + awake["tn"]) / total if total else None
        alpha, beta, rho = self.physics.estimate()
        report["physics"] = {"alpha": alpha, "beta": beta, "rho": rho,
                             "drain_observations": self.physics.drains,
                             "recharge_observations": self.physics.rho.n}
        report["residual_rate"] = self.residual_rate()
        report["fallbacks"] = self.fallbacks
        report["imputed"] = self.imputed
        report["modes"] = dict(self.modes)
        report["rows"] = len(self.rows)
        report.update(self.extra_summary)
        return report


_tracker: dict = {}


def tracker(profile: dict, round_index: int, total_rounds: int) -> Tracker:
    """One tracker per run; a new run (counter goes back, or a new device) resets it."""
    key = (total_rounds, tuple(sorted(profile.get("weights", {}).items())),
           profile.get("q_min"), profile.get("s_min"))
    current = _tracker.get("t")
    if current is None or current.key != key or round_index < current.last_round:
        current = Tracker()
        current.key = key
        current.mobility = 1 + float(profile.get("features", {}).get("mobility", 0))
        _tracker["t"] = current
    return current


def reset() -> None:
    _tracker.clear()


def episode_diagnostics() -> dict | None:
    current = _tracker.get("t")
    return current.summary() if current else None


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------
def _round_info(profile: dict) -> tuple[int, int]:
    observation = profile.get("_market") or {}
    return int(observation.get("round", 0)), int(observation.get("total_rounds", 0))


def cycle_aware_diagnostics(budget, prices, capacities, profile, history) -> dict:
    """Instrumentation only: cycle-aware's exact bid, plus a record of what it predicted."""
    from . import planner
    round_index, total = _round_info(profile)
    track = tracker(profile, round_index, total)
    track.ingest(round_index, budget, prices, capacities, profile, history)
    bid = planner.plan(budget, prices, capacities, profile, history, thresholds=True, refine=True)
    nodes = (profile.get("_market") or {}).get("nodes") or []
    me, own = Me(profile), base._battery(profile)
    if nodes and all(n.get("team") in KNOWN_BOTS for n in nodes):
        world = World(me, [Spec(n, KNOWN_BOTS[n["team"]]) for n in nodes], PRIOR_PHYSICS,
                      None, None, None, Config())
        bats = [float(n["features"]["battery"]) for n in nodes]
        preds = world.predict_all(bats, budget, prices, capacities)
        sums = world.sums(preds, budget)
        _, own_next, next_bats, _ = world.step(own, bats, budget, prices, capacities, bid, preds, sums)
        track.record(round_index, budget, prices, capacities, own, bid, sums, sums, own_next,
                     {s.team: b for s, b in zip(world.specs, next_bats)}, PRIOR_PHYSICS)
    else:
        others = base.estimate_others(budget, profile, history)
        track.fallbacks += 1
        track.record(round_index, budget, prices, capacities, own, bid, others, others, None, None,
                     PRIOR_PHYSICS)
    return bid


def _impute(track: Tracker, round_index: int) -> list | None:
    """Replace a missing snapshot with last round's one-step battery forecast.

    Chains: last round's state may itself have been imputed, as long as we
    decided (and therefore forecast) every round in between."""
    record = track.decisions.get(round_index - 1)
    last = track.snapshots.get(round_index - 1) or track.believed.get(round_index - 1)
    if not record or not last or not record.get("opp_next"):
        return None
    nodes = []
    for team, node in last.items():
        if team not in record["opp_next"]:
            return None
        clone = dict(node)
        clone["features"] = dict(node["features"], battery=record["opp_next"][team])
        nodes.append(clone)
    return nodes


def _horizon(cfg: Config, track: Tracker, remaining: int) -> int:
    if not cfg.dynamic_horizon:
        return min(cfg.horizon, remaining)
    if remaining <= cfg.exact_tail:
        return remaining
    c = track.confidence()
    if c["market"] > 0.04 or c["battery"] > 0.01:
        return min(cfg.horizon_high_error, remaining)
    if c["market"] < 0.01 and c["battery"] < 0.002:
        return min(cfg.horizon_low_error, remaining)
    return min(cfg.horizon, remaining)


def _lambda(cfg: Config, round_index: int, total: int, remaining: int) -> float:
    if remaining <= 5 or total <= 0:
        return 0.0
    progress = (round_index - 1) / total
    return cfg.risk[0] if progress < 1 / 3 else cfg.risk[1] if progress < 2 / 3 else cfg.risk[2]


MODES = {
    "conservative": dict(risk=(0.5, 0.4, 0.2), terminal_own=1.5, opponent_thresholds=False, tau=0.9),
    "balanced": dict(),
    "aggressive": dict(risk=(0.0, 0.0, 0.0), terminal_others=0.25, tau=0.5, sacrifice=0.03),
    "robust": dict(horizon=3, dynamic_horizon=False, opponent_thresholds=False, risk=(0.3, 0.3, 0.1)),
}


def select_mode(track: Tracker, own: float, bats: list, specs: list, remaining: int) -> str:
    """modes: a deterministic rule from model confidence and the battery state."""
    c = track.confidence()
    if c["market"] > 0.05 or c["battery"] > 0.015:
        return "robust"
    vulnerable = any(CUTOFF < b < 0.15 and not s.blocked for s, b in zip(specs, bats))
    if c["market"] < 0.01 and c["battery"] < 0.003 and vulnerable and own > 0.2:
        return "aggressive"
    if own < 0.25 and remaining > 12:
        return "conservative"
    return "balanced"


def decide(cfg: Config, budget: float, prices: dict, capacities: dict, profile: dict,
           history: list, mode: str | None = None) -> dict:
    from . import planner
    round_index, total = _round_info(profile)
    track = tracker(profile, round_index, total)
    track.ingest(round_index, budget, prices, capacities, profile, history)
    own = base._battery(profile)
    nodes = (profile.get("_market") or {}).get("nodes") or []
    if not nodes and cfg.impute:
        nodes = _impute(track, round_index) or []
        if nodes:
            track.imputed += 1
            track.believed[round_index] = {n.get("team", ""): n for n in nodes}
            for old in [r for r in track.believed if r < round_index - 3]:
                del track.believed[old]
    unknown = [] if cfg.identify else [n for n in nodes if n.get("team") not in KNOWN_BOTS]
    remaining = total - round_index + 1
    if not nodes or (unknown and not cfg.unknown_prior) or remaining < 1:
        bid = (planner.opponent_aware(budget, prices, capacities, profile, history)
               if nodes and not unknown and remaining < 1 else base.kelly(budget, prices, capacities, profile, history))
        others = base.estimate_others(budget, profile, history)
        track.fallbacks += 1
        track.record(round_index, budget, prices, capacities, own, bid, others, others, None, None, None)
        return bid
    physics = track.physics.estimate() if cfg.physics else PRIOR_PHYSICS
    specs = [Spec(n, KNOWN_BOTS.get(n.get("team"), "unknown")) for n in nodes]
    if cfg.identify:
        from . import market_id
        market_id.attach(track, specs, round_index, prices, physics, cfg.identify_model)
    elif cfg.learn_opponents:
        from . import opponents
        opponents.attach(track, specs, physics)
    bats = [float(n["features"]["battery"]) for n in nodes]
    if cfg.bandit and mode is None:
        from . import bandit
        nominal = [predict(spec, b, budget, prices, capacities) for spec, b in zip(specs, bats)]
        sums = {k: sum(p[k] for p in nominal) for k in RESOURCES}
        mode = bandit.choose_mode(track, own, bats, specs, round_index, total, sums, budget, profile, history)
    if cfg.modes and mode is None:
        mode = select_mode(track, own, bats, specs, remaining)
    if mode:
        cfg = replace(cfg, **MODES[mode])
    rate = track.residual_rate() if cfg.residual else None
    if rate is not None and not any(rate.values()):
        rate = None  # exactly the nominal model when nothing is significant
    sigma_market = ({k: cfg.noise_scale * v for k, v in track.market_sigma().items()}
                    if cfg.noise else None)
    sigma_battery = ([cfg.noise_scale * track.battery_sigma()] * len(specs)
                     if cfg.noise and cfg.noise_battery else None)
    me = Me(profile)
    world = World(me, specs, physics, rate, sigma_market, sigma_battery, cfg)
    world.sigma_battery_own = track.own_battery_error.rms
    targets = None
    if cfg.prob_cutoff:
        z = _NORMAL.inv_cdf(min(0.995, max(0.5, cfg.tau)))
        own_margin = max(0.0002, z * track.own_battery_error.rms)
        opp_margin = max(0.0002, z * track.battery_sigma())
        targets = ((CUTOFF - own_margin, CUTOFF + own_margin),
                   [(CUTOFF - opp_margin, CUTOFF + opp_margin)] * len(specs))
        # Keep cycle-aware's exact crossings too: they remain valid points estimates.
        targets = (tuple(sorted(set(targets[0]) | {0.0498, 0.0502})),
                   [tuple(sorted(set(t) | {0.0498, 0.0502})) for t in targets[1]])
    if cfg.cutoff_margin > 0:
        margin = cfg.cutoff_margin
        targets = ((CUTOFF - margin, CUTOFF + margin), [(CUTOFF - margin, CUTOFF + margin)] * len(specs))
    if cfg.margin_k > 0:
        # identified-robust: aim each crossing k forecast-standard-errors beyond the cutoff,
        # per rival; exact forecasts collapse this to cycle-aware's 0.0002.
        def margin(sigma: float) -> float:
            return max(cfg.cutoff_margin or 0.0002, cfg.margin_k * sigma)
        own_m = margin(track.own_battery_error.rms)
        prior = EW(0.8, 0.0, 0.01, 1.0)
        targets = ((CUTOFF - own_m, CUTOFF + own_m),
                   [(CUTOFF - margin(track.battery_error_by.get(s.team, prior).rms),
                     CUTOFF + margin(track.battery_error_by.get(s.team, prior).rms)) for s in specs])
    shortlist = None
    progress = (round_index - 1) / max(1, total)
    if cfg.shortlist_model:
        from . import shortlist as learned_shortlist
        shortlist = learned_shortlist.make(cfg.shortlist_size, progress)
        world.shortlist = learned_shortlist.make(cfg.shortlist_size, progress)
    depth = _horizon(cfg, track, remaining)
    lam = _lambda(cfg, round_index, total, remaining)
    bid, info = plan_core(world, budget, prices, capacities, own, bats, remaining, depth, lam,
                          thresholds=True, targets=targets, shortlist=shortlist)
    if COLLECT is not None:
        COLLECT(world, info, own, bats, progress)
    model_sums = {k: sum(p[k] for p in info["preds"]) for k in RESOURCES}
    _, own_next, next_bats, _ = info["nominal"]
    track.record(round_index, budget, prices, capacities, own, bid, model_sums, info["sums"], own_next,
                 {s.team: b for s, b in zip(specs, next_bats)}, physics, mode)
    return bid


# ---------------------------------------------------------------------------
# Versions
# ---------------------------------------------------------------------------
PHYSICS = Config(physics=True)
RESIDUAL = replace(PHYSICS, residual=True, unknown_prior=True, impute=True)
NOISY_SCENARIOS = replace(RESIDUAL, scenarios=5, noise=True)
PROB_CUTOFF = replace(NOISY_SCENARIOS, prob_cutoff=True)
CVAR = replace(PROB_CUTOFF, risk=(0.25, 0.15, 0.0))
DYNAMIC_HORIZON = replace(CVAR, dynamic_horizon=True)
STRATEGY_MODES = replace(DYNAMIC_HORIZON, modes=True)
# adaptive-cycle-aware: the components that survived development seeds
# 31001-31040 / 32001-32020, frozen before the holdout. Noise (noisy-scenarios),
# risk (cvar) and the dynamic horizon (dynamic-horizon) were neutral or harmful
# there and are left out; those entries remain measured as specified.
ADAPTIVE_CYCLE_AWARE = replace(RESIDUAL, prob_cutoff=True)
LINUCB_MODES = replace(ADAPTIVE_CYCLE_AWARE, bandit=True)
ARCHETYPE_LEARNING = replace(ADAPTIVE_CYCLE_AWARE, learn_opponents=True)
LEARNED_SHORTLIST = replace(ARCHETYPE_LEARNING, shortlist_model=True, shortlist_size=9)
# identified-linear: adaptive-cycle-aware with every rival identified from public
# telemetry as a battery-gated linear bidder; no names or bot formulas.
IDENTIFIED_LINEAR = replace(ADAPTIVE_CYCLE_AWARE, identify=True)
IDENTIFIED_LOGIT = replace(IDENTIFIED_LINEAR, identify_model="logit")
IDENTIFIED_STRUCTURAL = replace(IDENTIFIED_LINEAR, identify_model="structural")
# identified-robust: aim battery crossings 0.002 beyond the
# cutoff instead of cycle-aware's 0.0002, because identified forecasts are never exact
# (a 2% forecast bias costs the exact-crossing planner 6.7%; development seeds).
IDENTIFIED_ROBUST = replace(IDENTIFIED_STRUCTURAL, cutoff_margin=0.002)
CONFIGS = {
    "physics": PHYSICS,
    "residual": RESIDUAL,
    "noisy-scenarios": NOISY_SCENARIOS,
    "prob-cutoff": PROB_CUTOFF,
    "cvar": CVAR,
    "dynamic-horizon": DYNAMIC_HORIZON,
    "modes": STRATEGY_MODES,
    "adaptive-cycle-aware": ADAPTIVE_CYCLE_AWARE,
    "linucb-modes": LINUCB_MODES,
    "archetype-learning": ARCHETYPE_LEARNING,
    "learned-shortlist": LEARNED_SHORTLIST,
    "identified-linear": IDENTIFIED_LINEAR,
    "identified-logit": IDENTIFIED_LOGIT,
    "identified-structural": IDENTIFIED_STRUCTURAL,
    "identified-robust": IDENTIFIED_ROBUST,
}

