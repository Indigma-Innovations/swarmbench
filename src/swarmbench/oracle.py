"""A clairvoyant reference: exact one-round best responses plus lookahead.

:class:`ClairvoyantAgent` is a *reference point*, not an admissible agent. The
engine gives it two things no real node has:

1. the other nodes' bids of the current round before it bids, and
2. a ``value(bid)`` function that plays ``bid`` now and the next ``horizon``
   rounds in a copy of the whole market (true future draws, every other agent's
   real code and internal state) and returns the oracle's utility.

Each round it evaluates a small candidate set, the floor-aware best responses
to the others' true bids under several energy limits plus its base agent's
bid, and commits the best. Because the base bid is always a candidate, the
oracle is a rollout improvement of its base agent (over the lookahead window).

The one-round best response is exact up to bisection tolerance: with
x_k = C_k b_k / (b_k + B_k) and CES rho = 1/2, maximizing utility is maximizing
sum_k w_k sqrt(x_k), which is separable and concave; floors are handled by
solving once per floor pattern with the floor-buying bid as a lower bound.
"""

import math

from .agent import RESOURCES, Agent, Observation

_FLOOR_KEYS = (("compute", "q_min"), ("security", "s_min"))


def _utility(bid: dict, others: dict, caps: dict, w: dict, q: float, s: float) -> float:
    x = {k: (caps[k] * bid[k] / (bid[k] + others[k]) if bid[k] + others[k] > 0 else 0.0) for k in RESOURCES}
    u = sum(w[k] * math.sqrt(max(x[k], 0.0)) for k in RESOURCES) ** 2
    if x["compute"] + 1e-9 < q:
        u *= 0.5
    if x["security"] + 1e-9 < s:
        u *= 0.5
    return u


def _solve(budget: float, others: dict, caps: dict, w: dict, lo: dict, hi: dict) -> dict | None:
    """max sum_k w_k sqrt(C_k b_k/(b_k+B_k)) s.t. sum b <= budget, lo <= b <= hi."""
    if sum(lo.values()) > budget + 1e-12:
        return None
    eps = 1e-9 * max(budget, 1e-9)

    def marginal(k: str, b: float) -> float:
        B, C = others[k], caps[k]
        if B <= 0:                     # nobody else bids: any positive bid takes the pool
            return 0.0 if b > eps else float("inf")
        b = max(b, 1e-15)
        return w[k] * math.sqrt(C) * 0.5 * math.sqrt((b + B) / b) * B / (b + B) ** 2

    def demand(k: str, mu: float) -> float:
        a, z = lo[k], hi[k]
        if marginal(k, z) >= mu:
            return z
        if marginal(k, a) <= mu:
            return a
        for _ in range(60):
            m = 0.5 * (a + z)
            if marginal(k, m) > mu:
                a = m
            else:
                z = m
        return 0.5 * (a + z)

    if sum(hi.values()) <= budget:
        return dict(hi)
    lo_mu, hi_mu = 1e-12, 1e12
    for _ in range(100):
        mu = math.sqrt(lo_mu * hi_mu)
        total = sum(demand(k, mu) for k in RESOURCES)
        if total > budget:
            lo_mu = mu
        else:
            hi_mu = mu
        if hi_mu - lo_mu < 1e-12 * hi_mu:
            break
    bid = {k: demand(k, hi_mu) for k in RESOURCES}
    spare = budget - sum(bid.values())
    if spare > 0:                       # rounding: give the rest to the steepest pool
        k = max(RESOURCES, key=lambda r: marginal(r, bid[r]) if bid[r] < hi[r] else -1)
        bid[k] = min(hi[k], bid[k] + spare)
    return bid


def best_response(obs: Observation, others: dict, energy_min: float = 0.0,
                  energy_max: float | None = None) -> dict:
    """Floor-aware best response to the others' summed bids ``others`` (per pool)."""
    budget, caps, w = obs.budget, obs.capacities, obs.weights
    q, s = obs.floors
    best, best_u = None, -1.0
    for need_c in (True, False):
        for need_s in (True, False):
            lo = {k: 0.0 for k in RESOURCES}
            hi = {k: budget for k in RESOURCES}
            lo["energy"] = min(energy_min, budget)
            if energy_max is not None:
                hi["energy"] = max(min(energy_max, budget), lo["energy"])
            feasible = True
            for (k, key), need in zip(_FLOOR_KEYS, (need_c, need_s)):
                floor = q if key == "q_min" else s
                if not need:
                    continue
                if floor >= caps[k]:
                    feasible = False
                    break
                lo[k] = max(lo[k], others[k] * floor / (caps[k] - floor) * (1 + 1e-6) + 1e-12)
            if not feasible:
                continue
            bid = _solve(budget, others, caps, w, lo, hi)
            if bid is None:
                continue
            u = _utility(bid, others, caps, w, q, s)
            if u > best_u:
                best, best_u = bid, u
    return best or {k: budget * w[k] for k in RESOURCES}


ALPHA, BETA, CUTOFF = 0.30, 0.004, 0.05      # battery physics of the graded scenario


def _energy_for_share(share: float, others_e: float, cap: float) -> float | None:
    """Own energy bid that wins exactly ``share`` of the pool against ``others_e``."""
    if share <= 0:
        return 0.0
    if share >= cap:
        return None
    return others_e * share / (cap - share)


class ClairvoyantAgent(Agent):
    """Reference oracle; see the module docstring. Needs engine support (it is
    detected through ``clairvoyant = True``); elsewhere it plays its base policy
    without clairvoyance."""

    clairvoyant = True

    def __init__(self, horizon: int = 10, base: str = "kelly-drain", energy_caps: tuple = (0.0, 0.05, 0.15),
                 energy_floor: float = 0.5, rivals_considered: int = 3, large_market: int = 8,
                 large_horizon: int = 1):
        from .catalog import get_spec
        self.horizon, self.large_market, self.large_horizon = horizon, large_market, large_horizon
        self.base = get_spec(base).make() if base != "safe" else None
        self.energy_caps, self.energy_floor = energy_caps, energy_floor
        self.rivals_considered = rivals_considered
        self.evaluations = 0

    def horizon_for(self, obs: Observation) -> int:
        """Lookahead length; markets above ``large_market`` nodes cost too much per simulated round."""
        return self.large_horizon if len(obs.rivals) + 1 > self.large_market else self.horizon

    # -- the policy played inside rollouts: a battery-safe clairvoyant best response
    def _safe_cap(self, obs: Observation, others: dict) -> float | None:
        """Largest energy bid that keeps the own battery above the cutoff."""
        m = obs.mobility
        share = (obs.battery - CUTOFF - BETA - 1e-4) / (ALPHA * (1 + m))
        if share <= 0:
            return 0.0
        return _energy_for_share(share, others["energy"], obs.capacities["energy"])

    def reset(self, seed: int) -> None:
        if self.base:
            self.base.reset(seed)

    def base_bid(self, obs: Observation, others: dict) -> dict:
        """The policy played after the first move inside rollouts."""
        if self.base:
            return self.base.bid(obs)
        return best_response(obs, others, energy_max=self._safe_cap(obs, others))

    def bid(self, obs: Observation) -> dict:          # without engine support: no clairvoyance
        if self.base:
            return self.base.bid(obs)
        guess = {k: float(obs.prices.get(k, 1.0)) * obs.capacities.get(k, 1.0) for k in RESOURCES}
        return self.base_bid(obs, guess)

    def candidates(self, obs: Observation, others: dict, rival_bids: dict) -> list:
        budget, cap_e = obs.budget, obs.capacities["energy"]
        out = [self.base_bid(obs, others), best_response(obs, others)]
        out += [best_response(obs, others, energy_max=c * budget) for c in self.energy_caps]
        out.append(best_response(obs, others, energy_min=self.energy_floor * budget))
        # Own crossing: win enough energy to drop below the cutoff now (sleep, recharge).
        need = (obs.battery - CUTOFF - BETA + 1e-4) / (ALPHA * (1 + obs.mobility))
        e = _energy_for_share(need, others["energy"], cap_e)
        if e is not None and 0 < e < budget:
            out.append(best_response(obs, others, energy_min=e))
        # Rival crossings: leave rival j just enough energy share to fall under the cutoff.
        large = len(obs.rivals) + 1 > self.large_market
        rivals = [] if large else [r for r in obs.rivals if r.get("node_id") in rival_bids
                  and float(r.get("features", {}).get("battery", 1.0)) > CUTOFF]
        rivals.sort(key=lambda r: float(r["features"]["battery"]))
        for r in rivals[: self.rivals_considered]:
            b_j = float(rival_bids[r["node_id"]].get("energy", 0.0))
            if b_j <= 0:
                continue
            share = (float(r["features"]["battery"]) - CUTOFF - BETA + 1e-4) / \
                (ALPHA * (1 + float(r["features"].get("mobility", 0.0))))
            if share <= 0 or share >= cap_e:
                continue
            rest = others["energy"] - b_j
            limit = cap_e * b_j / share - b_j - rest            # our energy bid at most this
            if limit >= 0:
                out.append(best_response(obs, others, energy_max=limit * (1 - 1e-6)))
        unique = []
        for bid in out:
            if not any(all(abs(bid[k] - u[k]) < 1e-7 for k in RESOURCES) for u in unique):
                unique.append(bid)
        return unique

    def choose(self, obs: Observation, others: dict, rival_bids: dict, value) -> dict:
        options = self.candidates(obs, others, rival_bids)
        values = [value(bid) for bid in options]
        self.evaluations += len(options)
        return options[max(range(len(options)), key=values.__getitem__)]
