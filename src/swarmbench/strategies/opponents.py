"""archetype-learning: online behaviour models for unknown or mismatched rivals.

Identification. A rival's public battery falls by alpha*(1+m_j)*x_j + beta
when it is awake, so its energy share x_j is recoverable from the public swarm view. The
next round's published energy price is total_E / C_E, so its energy BID is
b_j = x_j * price_E, and its energy fraction is b_j / W (the wallet is common).
Compute/security bids are not individually identifiable; their aggregate error
is left to the market residual.

Each rival keeps a tempered Bayesian posterior over behavioural archetypes,
scored on the identified energy fractions. A known baseline name is trusted
until its observed fractions contradict the published policy; then it is
modelled like an unknown participant. In stochastic rollouts each scenario
samples one archetype per rival from the posterior (common random numbers).
"""

import math

from . import strategy as base

RESOURCES = base.RESOURCES
SIGMA = 0.03           # energy-fraction observation noise for the likelihood
FORGET = 0.9           # tempering of old log-likelihood (regime changes)
MISMATCH_RMS = 0.03    # a named bot whose fractions miss by more is relearned
MIN_OBSERVATIONS = 3


def _weights(spec) -> dict:
    total = sum(max(0.0, spec.weights[k]) for k in RESOURCES) or 1.0
    return {k: max(0.0, spec.weights[k]) / total for k in RESOURCES}


def _split(spec, energy_fraction: float, budget: float) -> dict:
    """Energy at a fraction of the wallet; the rest by compute/security weight."""
    w = _weights(spec)
    energy_fraction = min(1.0, max(0.0, energy_fraction))
    nonenergy = w["compute"] + w["security"] or 1.0
    rest = budget * (1 - energy_fraction)
    return {"compute": rest * w["compute"] / nonenergy, "energy": budget * energy_fraction,
            "security": rest * w["security"] / nonenergy}


_TABLE: dict = {}


def archetypes() -> dict:
    if not _TABLE:
        _TABLE.update(_build())
    return _TABLE


def _build() -> dict:
    from . import adaptive

    def naive(spec, battery, budget, prices, caps, fit):
        return {k: budget * spec.weights[k] for k in RESOURCES}

    def even(spec, battery, budget, prices, caps, fit):
        return {k: budget / 3 for k in RESOURCES}

    def proportional(spec, battery, budget, prices, caps, fit):
        return adaptive.proportional_bid(spec, budget, prices, caps)

    def taper(spec, battery, budget, prices, caps, fit):
        keep = max(0.0, (battery - 0.05) / 0.95)
        return _split(spec, _weights(spec)["energy"] * keep, budget)

    def regression(spec, battery, budget, prices, caps, fit):
        a, b = fit
        return _split(spec, a + b * battery, budget)
    return {"naive": naive, "even": even, "prop": proportional, "taper": taper, "regression": regression}


class Posterior:
    stochastic = True

    def __init__(self):
        self.loglik = {name: 0.0 for name in archetypes()}
        self.loglik["regression"] = -2.0   # weak prior against the free model
        self.seen = 0
        self.n = 0
        self.fit = (0.2, 0.0)
        self.moments = [0.0] * 5           # EW sums: w, x, y, xx, xy
        self.mismatch = 0.0
        self.mismatch_n = 0
        self.cached = None

    def update(self, spec, observation) -> None:
        _, fraction, battery, prices, caps, wallet = observation
        if prices is None or caps is None:
            return
        table = archetypes()
        for name, fn in table.items():
            predicted = fn(spec, battery, wallet, prices, caps, self.fit)["energy"] / wallet
            self.loglik[name] = FORGET * self.loglik[name] - 0.5 * ((fraction - predicted) / SIGMA) ** 2
        w, x, y, xx, xy = (FORGET * m for m in self.moments)
        self.moments = [w + 1, x + battery, y + fraction, xx + battery * battery, xy + battery * fraction]
        w, x, y, xx, xy = self.moments
        variance = xx / w - (x / w) ** 2
        slope = (xy / w - x * y / w / w) / variance if variance > 1e-4 else 0.0
        slope = max(-2.0, min(2.0, slope))
        self.fit = (y / w - slope * x / w, slope)
        self.n += 1
        self.cached = None

    def probabilities(self) -> dict:
        if self.cached is None:
            self.cached = self._probabilities()
        return self.cached

    def _probabilities(self) -> dict:
        top = max(self.loglik.values())
        raw = {k: math.exp(v - top) for k, v in self.loglik.items()}
        if self.n < MIN_OBSERVATIONS:
            raw["regression"] = 0.0
        total = sum(raw.values())
        return {k: v / total for k, v in raw.items()}

    def predict(self, spec, battery, budget, prices, caps, draw=None) -> dict:
        table = archetypes()
        probabilities = self.probabilities()
        if draw is not None:
            cumulative = 0.0
            for name, p in probabilities.items():
                cumulative += p
                if draw <= cumulative:
                    return table[name](spec, battery, budget, prices, caps, self.fit)
            return table[name](spec, battery, budget, prices, caps, self.fit)
        bid = {k: 0.0 for k in RESOURCES}
        for name, p in probabilities.items():
            if p > 1e-6:
                part = table[name](spec, battery, budget, prices, caps, self.fit)
                for k in RESOURCES:
                    bid[k] += p * part[k]
        return bid


def attach(track, specs: list, physics: tuple) -> None:
    """Update every rival's posterior with new telemetry; attach models."""
    from . import adaptive
    models = track.extra.setdefault("opponents", {})
    summary = track.extra_summary.setdefault("opponent_models", {})
    for spec in specs:
        observations = track.opponent_energy.get(spec.team, [])
        model = models.get(spec.team)
        if model is None:
            model = models[spec.team] = Posterior()
        for observation in observations[model.seen:]:
            if spec.kind in ("naive", "even", "prop"):
                _, fraction, battery, prices, caps, wallet = observation
                if prices is not None and caps is not None:
                    expected = adaptive.predict(spec, battery, wallet, prices, caps)["energy"] / wallet
                    model.mismatch = FORGET * model.mismatch + (fraction - expected) ** 2
                    model.mismatch_n = FORGET * model.mismatch_n + 1
            model.update(spec, observation)
        model.seen = len(observations)
        named = spec.kind in ("naive", "even", "prop")
        mismatched = named and model.n >= MIN_OBSERVATIONS and \
            math.sqrt(model.mismatch / max(1e-9, model.mismatch_n)) > MISMATCH_RMS
        if not named or mismatched:
            spec.kind = "learned"
            spec.model = model
        probabilities = model.probabilities()
        summary[spec.team] = {"modelled": spec.kind, "observations": model.n,
                              "top": max(probabilities, key=probabilities.get),
                              "p_top": max(probabilities.values()), "fit": model.fit}
