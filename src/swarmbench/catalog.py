"""The agent catalog: every agent with its family, idea order and realism.

Agents are ordered from the simplest idea to the most complex: traditional
rules first, then mathematical optimization and model-based planning, then
machine learning. Each entry is *realistic* when it never relies on the
supplied bots' team names or source code, i.e. it can face unnamed opponents
as they are. Entries are addressed by their key (``cycle-aware``).

Add your own agent with :func:`register_agent`.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from functools import partial
from typing import Callable

from .agent import RESOURCES, Agent, Observation

FAMILIES = (
    "Traditional (rules)",
    "Optimization (one round)",
    "Planning (exact bot model)",
    "Planning (identified market)",
    "Machine learning",
    "Reference",
)


@dataclass
class AgentSpec:
    """A catalog entry: metadata plus a factory that makes a fresh agent."""

    key: str                       # stable slug used on the command line
    name: str                      # human-readable name
    family: str
    order: int                     # position in the idea-complexity ordering
    realistic: bool                # handles unnamed opponents without bot names or code
    description: str
    factory: Callable[[], Agent]
    bot: bool = False              # one of the three supplied baseline bots
    aliases: tuple = field(default_factory=tuple)
    note: str = ""
    falls_back_to: str | None = None   # plays exactly as this entry when no rival is a known bot

    def make(self) -> Agent:
        """A fresh agent instance named after the entry's key."""
        agent = self.factory()
        agent.name = self.key
        return agent


class BotAgent(Agent):
    """A supplied baseline bot. Like the shipped runner, it never reads results."""

    def __init__(self, bot: str):
        from .bots import STRATEGIES
        self.bot = bot
        self.function = STRATEGIES[bot]

    def bid(self, obs: Observation) -> dict:
        return self.function(obs.budget, dict(obs.prices), dict(obs.capacities), obs.profile, [])


class RandomAgent(Agent):
    """Reference point: spends the whole wallet on a uniformly random split (seeded)."""

    def reset(self, seed: int) -> None:
        import random
        self.rng = random.Random(seed * 7919 + 17)

    def bid(self, obs: Observation) -> dict:
        draws = [self.rng.expovariate(1.0) for _ in RESOURCES]   # uniform on the simplex
        total = sum(draws)
        return {k: obs.budget * d / total for k, d in zip(RESOURCES, draws)}


class FixedSplitAgent(Agent):
    """Held-out opponent: a fixed budget split, whatever the market does."""

    def __init__(self, split: dict):
        self.split = split

    def bid(self, obs: Observation) -> dict:
        return {k: obs.budget * self.split[k] for k in RESOURCES}


class ContrarianAgent(Agent):
    """Held-out opponent: weights tilted toward the pools that cleared cheapest last round."""

    def bid(self, obs: Observation) -> dict:
        w = obs.weights
        score = {k: w[k] * obs.capacities.get(k, 1.0) / max(0.05, float(obs.prices.get(k, 1.0))) for k in RESOURCES}
        total = sum(score.values()) or 1.0
        return {k: obs.budget * score[k] / total for k in RESOURCES}


class StrategyAgent(Agent):
    """One of the built-in strategies of :mod:`swarmbench.strategies`.

    The original strategies keep per-run state in module globals (the UCB
    bandit, the adaptive tracker of the adaptive planners). Each instance owns
    that state and swaps it in before every decision, so several instances can
    share one market.
    """

    def __init__(self, key: str):
        from .strategies import strategy
        self.function = strategy.STRATEGIES[key]
        self._learning: dict = {}
        self._tracker: dict = {}

    def reset(self, seed: int) -> None:
        self._learning, self._tracker = {}, {}

    def bid(self, obs: Observation) -> dict:
        from .strategies import adaptive, strategy
        strategy._learning = self._learning
        adaptive._tracker = self._tracker
        return self.function(obs.budget, dict(obs.prices), dict(obs.capacities),
                             obs.arena_profile(), deepcopy(obs.history))

    def diagnostics(self) -> dict | None:
        """The adaptive planners' predicted-versus-realized summary, if any."""
        current = self._tracker.get("t")
        return current.summary() if current else None


CATALOG: dict[str, AgentSpec] = {}
_ALIASES: dict[str, str] = {}
_IMPORTED: list[str] = []          # modules loaded by import_agents, replayed in spawned workers


def import_agents(*modules: str) -> None:
    """Import modules that register agents (``swarmbench --import``).

    The modules are remembered, so worker processes that are spawned rather
    than forked (Windows) import them too before they play."""
    import importlib
    for module in modules:
        importlib.import_module(module)
        if module not in _IMPORTED:
            _IMPORTED.append(module)


def register_agent(key: str, factory: Callable[[], Agent], *, name: str | None = None,
                   family: str = "Machine learning", realistic: bool = True, description: str = "",
                   order: int | None = None, bot: bool = False,
                   aliases: tuple = (), note: str = "", falls_back_to: str | None = None) -> AgentSpec:
    """Add an agent to the catalog so the CLI, modes and reports can use it.

    ``factory`` must return a fresh :class:`Agent` (one per episode). ``family``
    should be one of :data:`FAMILIES`; ``realistic`` declares that the agent
    never relies on the supplied bots' names or code; ``order`` places it in
    the idea ordering (default: after every built-in entry). Raises
    :class:`ValueError` if the key is taken."""
    if key in CATALOG or key in _ALIASES:
        raise ValueError(f"agent {key!r} is already registered")
    spec = AgentSpec(key=key, name=name or key, family=family,
                     order=order if order is not None else 1000 + len(CATALOG), realistic=realistic,
                     description=description, factory=factory, bot=bot,
                     aliases=tuple(aliases), note=note, falls_back_to=falls_back_to)
    CATALOG[key] = spec
    for alias in aliases:
        _ALIASES[alias] = key
    return spec


def get_spec(key: str) -> AgentSpec:
    """The catalog entry for a key or alias; :class:`KeyError` if unknown."""
    key = _ALIASES.get(key, key)
    if key not in CATALOG:
        raise KeyError(f"unknown agent {key!r}; run `swarmbench --list`")
    return CATALOG[key]


def ordered(keys=None) -> list[AgentSpec]:
    """Catalog entries (all, or the given keys) in idea order."""
    specs = [get_spec(k) for k in keys] if keys else list(CATALOG.values())
    unique = {s.key: s for s in specs}
    return sorted(unique.values(), key=lambda s: s.order)


def _in_roster(spec: AgentSpec) -> bool:
    """Aliases and reference points are runnable but not part of the paper roster."""
    return not spec.note.startswith(("alias", "reference"))


def resolve(names: list[str]) -> list[AgentSpec]:
    """Expand keys and group names into catalog entries, in the given order, without duplicates.

    Groups: ``paper`` / ``all`` (the 36-entry roster), ``agents`` (the 33
    agents), ``bots`` (the three supplied bots), ``realistic`` and
    ``distinct`` (one entry per distinct behaviour among unnamed rivals)."""
    out: list[AgentSpec] = []
    for name in names:
        if name in ("all", "paper"):
            out += [s for s in ordered() if _in_roster(s)]
        elif name == "agents":
            out += [s for s in ordered() if not s.bot and _in_roster(s)]
        elif name == "bots":
            out += [s for s in ordered() if s.bot]
        elif name == "realistic":
            out += [s for s in ordered() if s.realistic and _in_roster(s)]
        elif name == "distinct":
            # one entry per distinct behaviour among unnamed rivals (the crowd market)
            out += [s for s in ordered() if _in_roster(s) and not s.falls_back_to]
        else:
            out.append(get_spec(name))
    seen, unique = set(), []
    for spec in out:
        if spec.key not in seen:
            seen.add(spec.key)
            unique.append(spec)
    return unique


# ---------------------------------------------------------------------------
# The built-in roster, in idea-complexity order
# ---------------------------------------------------------------------------
T, O, P, I, M, REF = FAMILIES
_BUILTIN = [
    # key, bot, family, realistic, name, description
    ("naive-max", True, T, True, "Naive max (bot)",
     "Spends the wallet in proportion to its preference weights."),
    ("even-split", True, T, True, "Even split (bot)", "One third of the wallet on each pool."),
    ("proportional", True, T, True, "Proportional (bot)",
     "Price-taker split w^2 C / price, then buys its service floors."),
    ("template", False, T, True, "Template: weight bids",
     "The supplied template: bid the preference weights."),
    ("taper", False, T, True, "Battery taper",
     "Template bid; energy cut as the battery falls, freed budget to compute/security."),
    ("floors", False, O, True, "Floor reservation",
     "Rival demand inverted from own results; reserves both service floors."),
    ("price-taker", False, O, True, "Price-taker split + floors",
     "w^2 C / estimated demand split with floor reserves; no battery control."),
    ("market-taper", False, O, True, "Price-taker + taper", "The price-taker split with the battery taper."),
    ("kelly", False, O, True, "Guarded Kelly best response",
     "Numerical one-round best response under the taper energy cap and floor reserves."),
    ("kelly-drain", False, O, True, "Kelly with drain price",
     "Best response with an estimated drain coefficient and a charge reserve."),
    ("kelly-blend", False, O, True, "Taper/Kelly blend", "Convex mix of the taper and Kelly bids."),
    ("bot-aware", False, O, False, "Best response to bot forecasts",
     "One-round best response to the bots' bids predicted from their published code."),
    ("lookahead", False, P, False, "Lookahead planner (MPC)",
     "Six-round stochastic rollouts with the exact bot model and battery dynamics."),
    ("lookahead-cutoff", False, P, False, "Lookahead + cutoff crossings",
     "Adds bids that push own/rival batteries exactly across the admission cutoff."),
    ("lookahead-refine", False, P, False, "Lookahead + refinement",
     "Re-evaluates the best three bids with a two-round improved continuation."),
    ("cycle-aware", False, P, False, "Cycle-Aware planner (selected)",
     "Cutoff crossings and refinement combined; the selected challenge submission."),
    ("physics", False, P, False, "+ online battery physics",
     "Cycle-Aware with drain, idle drain and recharge estimated online."),
    ("residual", False, P, False, "+ market residual",
     "Learns unexplained rival demand; models unknown nodes; imputes missing snapshots."),
    ("noisy-scenarios", False, P, False, "+ noisy scenarios",
     "Five common-random-number scenarios with calibrated market and battery noise."),
    ("prob-cutoff", False, P, False, "+ probabilistic cutoffs",
     "Confidence-shifted crossing targets and a P(transition) > tau gate."),
    ("cvar", False, P, False, "+ CVaR risk", "Mean blended with the 20% conditional value at risk."),
    ("dynamic-horizon", False, P, False, "+ dynamic horizon",
     "Planning horizon shortened when forecasts are unreliable."),
    ("modes", False, P, False, "+ strategy modes",
     "Conservative / balanced / aggressive / robust personalities chosen by a fixed rule."),
    ("adaptive-cycle-aware", False, P, False, "Adaptive cycle-aware",
     "The components that survived development: physics, residual, imputation, cutoff gate."),
    ("identified-linear", False, I, True, "Identified market: linear",
     "Rivals as battery-gated constant-fraction bidders identified from public telemetry."),
    ("identified-logit", False, I, True, "Identified market: logit demand",
     "Adds a price-responsive multinomial-logit budget split per rival."),
    ("identified-structural", False, I, True, "Identified market: rational demand",
     "Logit split plus securing public floors, with two-hypothesis model selection."),
    ("identified-robust", False, I, True, "Identified market: robust crossings",
     "Rational demand, aiming battery crossings 0.002 beyond the cutoff."),
    ("ucb-energy", False, M, True, "UCB over energy prices",
     "A three-armed UCB bandit choosing the drain price of the Kelly bid from realized rewards."),
    ("ridge-value", False, M, False, "Learned value (ridge), greedy",
     "Immediate utility plus a ridge-regression value of the next state."),
    ("ridge-terminal-4", False, M, False, "Planner + ridge terminal (4 rounds)",
     "Four-round rollouts with a learned terminal value."),
    ("ridge-terminal-6", False, M, False, "Planner + ridge terminal (6 rounds)",
     "Six-round rollouts with a learned terminal value."),
    ("catboost-terminal", False, M, False, "Planner + CatBoost terminal",
     "Six-round rollouts with a gradient-boosted terminal value (pure-Python export)."),
    ("linucb-modes", False, M, False, "LinUCB mode selector",
     "A contextual bandit, warm-started offline, chooses the planner personality each round."),
    ("archetype-learning", False, M, False, "Bayesian rival archetypes",
     "Per-rival Bayesian posteriors over behaviour archetypes learned online."),
    ("learned-shortlist", False, M, False, "Learned candidate shortlist",
     "A logistic model trained offline prunes candidate bids before the rollouts."),
]


# Entries that play exactly as another entry when no rival is one of the supplied bots
# (verified: identical scores on all 100 seeds of the 36-node market, nominal and scaled).
_FALLBACKS = {
    "template": "naive-max",
    **{key: "kelly" for key in ("bot-aware", "lookahead", "lookahead-cutoff", "lookahead-refine", "cycle-aware",
                               "physics", "ridge-value", "ridge-terminal-4", "ridge-terminal-6",
                               "catboost-terminal")},
}


def _register_builtin() -> None:
    for order, (key, bot, family, realistic, name, description) in enumerate(_BUILTIN, start=1):
        factory = partial(BotAgent if bot else StrategyAgent, key)
        register_agent(key, factory, name=name, family=family, realistic=realistic,
                       description=description, order=order, bot=bot, falls_back_to=_FALLBACKS.get(key))
    # Identical bids to cycle-aware, so not run by default.
    register_agent("cycle-aware-diagnostics", partial(StrategyAgent, "cycle-aware-diagnostics"),
                   name="Cycle-Aware + diagnostics", family=P, realistic=False,
                   description="cycle-aware's bids plus predicted-versus-realized logging.",
                   order=16.2, note="alias of cycle-aware (instrumented)")
    # Held-out opponents: no catalog agent was developed against them (not in the roster).
    register_agent("energy-hoarder", lambda: FixedSplitAgent({"compute": 0.25, "energy": 0.5, "security": 0.25}),
                   name="Energy hoarder (held-out)", family=REF, realistic=True, order=0.6,
                   description="Half of every wallet on energy, a quarter on each other pool.",
                   note="reference: held-out opponent")
    register_agent("contrarian", ContrarianAgent, name="Contrarian (held-out)", family=REF, realistic=True,
                   order=0.7, description="Weight x capacity / last price: leans into the cheapest pools.",
                   note="reference: held-out opponent")
    register_agent("random", RandomAgent, name="Random split (reference)", family=REF, realistic=True,
                   description="Whole wallet on a uniformly random split each round.", order=0.5,
                   note="reference: random split; also a held-out opponent")
    from .oracle import ClairvoyantAgent
    register_agent("clairvoyant", ClairvoyantAgent, name="Oracle (reference)", family=REF, aliases=("oracle",),
                   realistic=False, order=0.4,
                   description="Sees the others' current bids and plays candidate bids forward in copies "
                               "of the market; not an admissible agent.",
                   note="reference: oracle")


_register_builtin()
__all__ = ["CATALOG", "FAMILIES", "RESOURCES", "AgentSpec", "BotAgent", "ContrarianAgent",
           "FixedSplitAgent", "RandomAgent", "StrategyAgent", "get_spec", "import_agents", "ordered", "register_agent",
           "resolve"]
