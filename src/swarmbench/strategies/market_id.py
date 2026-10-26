"""The identified-market planners: identify the market from public telemetry, without
assuming who the rivals are or how they bid.

Model. Every rival j is a battery-gated linear bidder: while it is admissible
it bids  b_j = W * phi_j  (phi_j in R^3, unknown), while asleep it bids nothing.
This nests any fixed-fraction policy exactly and is a first-order description
of any other; what remains is left to the market residual.

Identification, all from public data and our own records:

* Participation. A rival that bid in round l drained at least beta, a rival that
  rested recharged, so p_{j,l} = 1[B_{j,l+1} < B_{j,l}] (public batteries).
* Energy, per rival. Its energy share is x_j = (B_{j,l} - B_{j,l+1} - beta) /
  (alpha (1+m_j)), and the next published energy price is total_E / C_E, so
  its energy bid is  b_{j,E} = x_j * price_E(l+1).
* Every resource, in aggregate. The next published price gives the total bid,
  so rival demand is S_{k,l} = price_k(l+1) C_{k,l} - b^own_{k,l} =
  W_l * sum_j p_{j,l} phi_{j,k}. Rivals sleep at different times, so their
  own battery cycles act as natural experiments and least squares separates
  each rival's phi_j from these aggregates.

Estimation is ridge regression with exponential forgetting, refitted from the
stored rows each decision (n rivals is small). The prior mean is the rival's
public preference weights (spend the wallet as you value it), sd 0.3.

identified-logit replaces the constant fractions by a multinomial-logit demand system,

    b_{j,k} = W * psi_j * softmax_k(theta_{j,k} + gamma_j * log(C_k / price_k)),

a standard price-taking budget-share model: gamma = 0 is a fixed-fraction
bidder, gamma = 1 a Cobb-Douglas price taker. The covariates are the public
capacities and prices of the round. It is fitted to the same rows by
regularized Gauss-Newton (priors: theta = log weights, gamma = 0, psi = 1).
"""

import math

from . import strategy as base

RESOURCES = base.RESOURCES
FORGET = 0.9          # per-round weight decay: rivals may change behaviour
AGGREGATE_SD = 0.05   # misspecification allowance for aggregate rows (per wallet)
ENERGY_SD = 0.01      # direct energy rows: battery rounding and physics error
PRIOR_SD = 0.3
# Large markets: refit at most this many rivals per decision, least recently
# fitted first. With up to REFIT_CAP rivals every rival is refitted every
# decision, exactly as in the published 4-node results.
REFIT_CAP = 4


def refit_order(last_fit: dict, teams: list, now: int) -> list:
    """Teams to refit now, in sorted order; all of them when few enough."""
    if len(teams) <= REFIT_CAP:
        return list(teams)
    chosen = sorted(teams, key=lambda t: (last_fit.get(t, -1), t))[:REFIT_CAP]
    for t in chosen:
        last_fit[t] = now
    return sorted(chosen)


def _solve(a: list, b: list) -> list:
    from . import bandit
    return bandit._solve(a, b)


class MarketModel:
    def __init__(self):
        self.rows = []          # (round, resource, {team: coefficient}, y, weight)
        self.prior = {}         # team -> {k: prior mean}
        self.phi = {}           # team -> {k: estimate}
        self.last = 0
        self.observations = 0
        self.covariates = {}    # round -> z_k = log(C_k / price_k) the rivals saw
        self.inputs = {}        # round -> (wallet, caps, prices) the rivals saw

    def observe(self, track, round_index: int, prices: dict, physics: tuple) -> None:
        """Add the rows for round l = round_index - 1, once."""
        index = round_index - 1
        if index <= self.last:
            return
        self.last = index
        record = track.decisions.get(index)
        before, after = track.snapshots.get(index), track.snapshots.get(round_index)
        if not record or not before or not after or not record.get("wallet"):
            return
        alpha, beta, _ = physics
        wallet = record["wallet"]
        participation = {}
        for team, node in before.items():
            if team not in after or node.get("ejected") or not node.get("active", True):
                continue
            b0, b1 = float(node["features"]["battery"]), float(after[team]["features"]["battery"])
            participation[team] = 1.0 if (b0 > 0.05 and b1 < b0 - 1e-9) else 0.0
            if team not in self.prior:
                weights = base._weights(node)
                self.prior[team] = dict(weights)
            if participation[team] and b1 > 0:
                mobility = float(node["features"].get("mobility", 0))
                share = max(0.0, (b0 - b1 - beta) / (alpha * (1 + mobility)))
                y = share * float(prices.get("energy", 0)) / wallet
                self.rows.append((index, "energy", {team: 1.0}, y, 1 / ENERGY_SD ** 2))
        for k in RESOURCES:
            price = float(prices.get(k, 0))
            if price <= 0.0100001 or not record.get("caps"):
                continue
            demand = price * float(record["caps"][k]) - record["bid"][k]
            self.rows.append((index, k, dict(participation), demand / wallet, 1 / AGGREGATE_SD ** 2))
        self.covariates[index] = _covariates(record.get("caps") or {}, record.get("prices") or {})
        self.inputs[index] = (wallet, dict(record.get("caps") or {}), dict(record.get("prices") or {}))
        self.observations += 1
        self.rows = [r for r in self.rows if r[0] > index - 40]
        self.fit(index)

    def fit(self, now: int) -> None:
        teams = sorted(self.prior)
        position = {t: i for i, t in enumerate(teams)}
        n = len(teams)
        estimates = {t: {} for t in teams}
        for k in RESOURCES:
            a = [[(1 / PRIOR_SD ** 2 if i == j else 0.0) for j in range(n)] for i in range(n)]
            b = [self.prior[t][k] / PRIOR_SD ** 2 for t in teams]
            for index, resource, coefficients, y, weight in self.rows:
                if resource != k:
                    continue
                w = weight * FORGET ** (now - index)
                items = [(position[t], c) for t, c in coefficients.items() if c and t in position]
                for i, ci in items:
                    b[i] += w * ci * y
                    for j, cj in items:
                        a[i][j] += w * ci * cj
            solution = _solve(a, b)
            for t, value in zip(teams, solution):
                estimates[t][k] = max(0.0, value)
        self.phi = estimates

    def fractions(self, team: str, node: dict) -> dict:
        if team in self.phi:
            return self.phi[team]
        return self.prior.get(team) or base._weights(node)


class IdentifiedRival:
    """Spec.model: bid = wallet * phi_j while awake (gating is done by the planner)."""

    stochastic = False

    def __init__(self, fractions: dict):
        self.fractions = fractions

    def predict(self, spec, battery, budget, prices, caps, draw=None) -> dict:
        return {k: budget * self.fractions[k] for k in RESOURCES}


def attach(track, specs: list, round_index: int, prices: dict, physics: tuple,
           kind: str = "linear") -> None:
    model = track.extra.get("market_id")
    if model is None:
        model = track.extra["market_id"] = {"logit": LogitMarketModel, "structural": StructuralMarketModel}.get(
            kind, MarketModel)()
    model.observe(track, round_index, prices, physics)
    for spec in specs:
        spec.kind = "identified"
        spec.model = (model.model_for(spec.team, spec.node) if kind in ("logit", "structural")
                      else IdentifiedRival(model.fractions(spec.team, spec.node)))
    if kind in ("logit", "structural"):
        track.extra_summary["identified_params"] = {
            t: [round(v, 3) for v in p] for t, p in model.params.items()}
    track.extra_summary["identified_phi"] = {t: {k: round(v, 4) for k, v in phi.items()}
                                             for t, phi in model.phi.items()}
    track.extra_summary["identified_rounds"] = model.observations


def _covariates(caps: dict, prices: dict) -> dict:
    return {k: math.log(max(1e-6, float(caps.get(k, 1))) / max(0.01, float(prices.get(k, 1))))
            for k in RESOURCES}


def _shares(params: list, z: dict) -> dict:
    """params = (theta_C, theta_E, theta_S, gamma, log psi) -> bid per unit wallet."""
    logits = [params[i] + params[3] * z[k] for i, k in enumerate(RESOURCES)]
    top = max(logits)
    exp = [math.exp(v - top) for v in logits]
    total = sum(exp)
    psi = math.exp(min(0.0, params[4]))
    return {k: psi * e / total for k, e in zip(RESOURCES, exp)}


class LogitMarketModel(MarketModel):
    PRIOR_SD = (1.0, 1.0, 1.0, 1.0, 0.1)

    def __init__(self):
        super().__init__()
        self.params = {}

    def prior_params(self, team: str) -> list:
        w = self.prior[team]
        return [math.log(max(1e-3, w[k])) for k in RESOURCES] + [0.0, 0.0]

    def fit(self, now: int) -> None:
        teams = sorted(self.prior)
        n = len(teams)
        if not n:
            return
        if n > REFIT_CAP:
            return self._fit_blocks(teams, now)
        x = []
        for t in teams:
            x += self.params.get(t) or self.prior_params(t)
        prior = [v for t in teams for v in self.prior_params(t)]
        rows = [r for r in self.rows if r[0] in self.covariates]
        sd = self.PRIOR_SD * n

        def residuals(theta: list) -> list:
            per = {t: theta[5 * i:5 * i + 5] for i, t in enumerate(teams)}
            out = []
            for index, k, coefficients, y, weight in rows:
                z = self.covariates[index]
                pred = sum(c * _shares(per[t], z)[k] for t, c in coefficients.items() if c and t in per)
                out.append(math.sqrt(weight * FORGET ** (now - index)) * (y - pred))
            out += [(v - p) / s for v, p, s in zip(theta, prior, sd)]
            return out
        m = len(x)
        for _ in range(4):  # Gauss-Newton with a small Levenberg damping
            r0 = residuals(x)
            jac = []
            for i in range(m):
                xi = list(x)
                xi[i] += 1e-5
                jac.append([(a - b) / 1e-5 for a, b in zip(residuals(xi), r0)])
            # Normal equations: (J^T J + mu I) delta = -J^T r, with J = -d r / d x
            jtj = [[sum(a * b for a, b in zip(jac[i], jac[j])) + (1e-3 if i == j else 0.0)
                    for j in range(m)] for i in range(m)]
            jtr = [-sum(a * b for a, b in zip(jac[i], r0)) for i in range(m)]
            delta = _solve(jtj, jtr)
            step = max(abs(d) for d in delta) if delta else 0.0
            if step > 1.0:
                delta = [d / step for d in delta]
            x = [a + d for a, d in zip(x, delta)]
            if step < 1e-4:
                break
        self.params = {t: x[5 * i:5 * i + 5] for i, t in enumerate(teams)}
        self.phi = {t: _shares(self.params[t], next(iter(self.covariates.values()))) for t in teams} \
            if self.covariates else {}

    def _fit_blocks(self, teams: list, now: int) -> None:
        """Large markets: one rival at a time (others fixed), a few per decision."""
        rows = [r for r in self.rows if r[0] in self.covariates]
        params = {t: list(self.params.get(t) or self.prior_params(t)) for t in teams}
        indices = {r[0] for r in rows}
        cache = {t: {i: _shares(params[t], self.covariates[i]) for i in indices} for t in teams}
        last_fit = self.__dict__.setdefault("last_fit", {})
        for team in refit_order(last_fit, teams, now):
            mine = [r for r in rows if r[2].get(team)]
            if not mine:
                continue
            prior = self.prior_params(team)

            def residuals(theta: list) -> list:
                out = []
                for index, k, coefficients, y, weight in mine:
                    own = coefficients[team] * _shares(theta, self.covariates[index])[k]
                    rest = sum(c * cache[t][index][k] for t, c in coefficients.items()
                               if c and t != team and t in cache)
                    out.append(math.sqrt(weight * FORGET ** (now - index)) * (y - rest - own))
                return out + [(v - p) / s for v, p, s in zip(theta, prior, self.PRIOR_SD)]
            x = params[team]
            for _ in range(2):
                x = StructuralMarketModel._step(residuals, x)
            params[team] = x
            cache[team] = {i: _shares(x, self.covariates[i]) for i in indices}
        self.params = params

    def model_for(self, team: str, node: dict):
        if team not in self.prior:
            self.prior[team] = dict(base._weights(node))
        return LogitRival(self.params.get(team) or self.prior_params(team))


class LogitRival:
    stochastic = False

    def __init__(self, params: list):
        self.params = params

    def predict(self, spec, battery, budget, prices, caps, draw=None) -> dict:
        shares = _shares(self.params, _covariates(caps, prices))
        return {k: budget * v for k, v in shares.items()}


# ---------------------------------------------------------------------------
# identified-structural: rational-component demand system
# ---------------------------------------------------------------------------
STRUCTURAL_PRIOR = (1.0, 1.0, 1.0, 1.0, 0.1, 2.0, 0.3)  # sd of theta(3), gamma, log psi, d, mu
BELIEF_PRIOR = -3.0   # softplus(-3) = 0.05: a priori a rival does not buy floors
FLOORS = (("compute", "q_min"), ("security", "s_min"))


def structural_bid(params: list, floors: dict, budget: float, caps: dict, prices: dict) -> dict:
    """Secure the public floors against believed rival demand d with margin mu,
    then split by a price-responsive logit. d = 0 is a pure logit bidder.

    params = (theta_C, theta_E, theta_S, gamma, log psi, d, mu)."""
    shares = _shares(params, _covariates(caps, prices))
    bid = {k: budget * v for k, v in shares.items()}
    # softplus keeps the believed rival demand positive with a usable gradient
    belief, margin = math.log1p(math.exp(min(30.0, params[5]))), max(0.0, params[6])
    for k, key in FLOORS:
        cap = float(caps.get(k, 1))
        target = min(0.95 * cap, margin * floors[key])
        if target <= 0 or target >= cap:
            continue
        deficit = belief * target / (cap - target) - bid[k]
        if deficit <= 0:
            continue
        donors = [r for r in RESOURCES if r != k and bid[r] > 0]
        available = sum(bid[r] for r in donors)
        take = min(deficit, available)
        if available > 1e-12:
            for r in donors:
                bid[r] -= take * bid[r] / available
        bid[k] += take
    return bid


class StructuralMarketModel(MarketModel):
    def __init__(self):
        super().__init__()
        self.params = {}
        self.floors = {}

    def prior_params(self, team: str) -> list:
        w = self.prior[team]
        return [math.log(max(1e-3, w[k])) for k in RESOURCES] + [0.0, 0.0, BELIEF_PRIOR, 1.1]

    def observe(self, track, round_index: int, prices: dict, physics: tuple) -> None:
        for team, node in (track.snapshots.get(round_index) or {}).items():
            self.floors.setdefault(team, {"q_min": float(node.get("q_min", 0)),
                                          "s_min": float(node.get("s_min", 0))})
        super().observe(track, round_index, prices, physics)

    def predict_row(self, team: str, params: list, index: int) -> dict:
        record = self.inputs[index]
        return {k: v / record[0] for k, v in
                structural_bid(params, self.floors[team], record[0], record[1], record[2]).items()}

    def fit(self, now: int) -> None:
        """Block-coordinate Gauss-Newton: one rival at a time, others fixed.

        Each rival is fitted under two hypotheses, "secures its floors"
        (started at d = 1) and "pure logit" (d near 0), and the better
        penalized fit is kept: a two-model selection rather than one
        non-convex fit that can stall at either."""
        teams = [t for t in sorted(self.prior) if t in self.floors]
        rows = [r for r in self.rows if r[0] in self.inputs]
        if not teams or not rows:
            return
        params = {t: list(self.params.get(t) or self.prior_params(t)) for t in teams}
        cache = {t: {i: self.predict_row(t, params[t], i) for i in {r[0] for r in rows}} for t in teams}
        last_fit = self.__dict__.setdefault("last_fit", {})
        for team in refit_order(last_fit, teams, now):
            mine = [r for r in rows if r[2].get(team)]
            if not mine:
                continue
            prior = self.prior_params(team)

            def residuals(theta: list) -> list:
                out = []
                for index, k, coefficients, y, weight in mine:
                    own = self.predict_row(team, theta, index)[k]
                    rest = sum(c * cache[t][index][k] for t, c in coefficients.items()
                               if c and t != team and t in cache)
                    out.append(math.sqrt(weight * FORGET ** (now - index)) * (y - rest - own))
                return out + [(v - p) / s for v, p, s in zip(theta, prior, STRUCTURAL_PRIOR)]
            def descend(x: list, iterations: int) -> list:
                for _ in range(iterations):
                    x = self._step(residuals, x)
                return x
            current = descend(params[team], 2)
            floors = list(current)
            floors[5], floors[6] = max(floors[5], 1.0), max(floors[6], 1.1)
            floors = descend(floors, 3)
            loss = lambda theta: sum(v * v for v in residuals(theta))
            x = min((current, floors), key=loss)
            params[team] = x
            cache[team] = {i: self.predict_row(team, x, i) for i in cache[team]}
        self.params = params

    @staticmethod
    def _step(residuals, x: list) -> list:
        """One damped Gauss-Newton step with a finite-difference Jacobian."""
        r0 = residuals(x)
        jac = []
        for i in range(len(x)):
            xi = list(x)
            xi[i] += 1e-5
            jac.append([(a - b) / 1e-5 for a, b in zip(residuals(xi), r0)])
        m = len(x)
        jtj = [[sum(a * b for a, b in zip(jac[i], jac[j])) + (1e-3 if i == j else 0.0)
                for j in range(m)] for i in range(m)]
        jtr = [-sum(a * b for a, b in zip(jac[i], r0)) for i in range(m)]
        delta = _solve(jtj, jtr)
        step = max(abs(d) for d in delta)
        if step > 0.5:
            delta = [d * 0.5 / step for d in delta]
        return [a + d for a, d in zip(x, delta)]

    def model_for(self, team: str, node: dict):
        if team not in self.prior:
            self.prior[team] = dict(base._weights(node))
        floors = self.floors.get(team) or {"q_min": float(node.get("q_min", 0)),
                                           "s_min": float(node.get("s_min", 0))}
        return StructuralRival(self.params.get(team) or self.prior_params(team), floors)


class StructuralRival:
    stochastic = False

    def __init__(self, params: list, floors: dict):
        self.params, self.floors = params, floors

    def predict(self, spec, battery, budget, prices, caps, draw=None) -> dict:
        return structural_bid(self.params, self.floors, budget, caps, prices)
