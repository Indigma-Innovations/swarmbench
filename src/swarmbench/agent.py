"""The agent interface: what an agent sees and what it must return.

Write an agent by subclassing :class:`Agent` and implementing :meth:`Agent.bid`::

    class MyAgent(Agent):
        def bid(self, obs: Observation) -> dict:
            return {k: obs.budget * obs.weights[k] for k in RESOURCES}

Everything an agent receives is public in the live arena: the round payload
(wallet, capacities, last round's clearing prices), the agent's own profile,
the public swarm view of every other node, and the agent's own settled
results, delivered with the same one-round lag as the live agent loop.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Callable

RESOURCES = ("compute", "energy", "security")


@dataclass
class Observation:
    """One decision's inputs. All fields are public information.

    Attributes:
        round: Current round, 1-based.
        total_rounds: Length of the episode.
        budget: This round's wallet ``W`` (common to all nodes).
        prices: Last round's clearing prices per pool (total bid / capacity).
        capacities: This round's pool sizes ``C_k``.
        profile: The node's own profile: ``features`` (battery, mobility, ...),
            ``weights``, ``q_min`` and ``s_min``.
        rivals: Public views of all other nodes (the arena's swarm view).
        history: The node's own settled results, delivered one round late.
    """

    round: int                    # current round, 1-based
    total_rounds: int
    budget: float                 # this round's wallet W (common to all nodes)
    prices: dict                  # LAST round's clearing prices (total bid / capacity)
    capacities: dict              # this round's pool sizes C_k
    profile: dict                 # own profile: features (battery, mobility, ...), weights, q_min, s_min
    rivals: list = field(default_factory=list)   # public views of all other nodes
    history: list = field(default_factory=list)  # own settled results, lagged one round

    @property
    def battery(self) -> float:
        """Own battery charge in [0, 1]."""
        return float(self.profile.get("features", {}).get("battery", 1.0))

    @property
    def mobility(self) -> float:
        """Own mobility m (raises the battery drain by the factor 1 + m)."""
        return float(self.profile.get("features", {}).get("mobility", 0.0))

    @property
    def weights(self) -> dict:
        """Own preference weights per pool (they sum to 1)."""
        return {k: float(self.profile.get("weights", {}).get(k, 1 / 3)) for k in RESOURCES}

    @property
    def floors(self) -> tuple[float, float]:
        """Own service floors ``(q_min, s_min)``: minimum compute and security shares."""
        return float(self.profile.get("q_min", 0)), float(self.profile.get("s_min", 0))

    def arena_profile(self) -> dict:
        """The profile dict the built-in strategies expect (public rivals under ``_market``)."""
        profile = dict(self.profile)
        profile["_market"] = {"round": self.round, "total_rounds": self.total_rounds,
                              "nodes": list(self.rivals)}
        return profile


class Agent(ABC):
    """Base class. One instance plays one episode; keep per-run state on ``self``."""

    #: shown in reports; set by the catalog or by you
    name: str = "agent"

    def reset(self, seed: int) -> None:
        """Called once before an episode starts."""

    @abstractmethod
    def bid(self, obs: Observation) -> dict:
        """Return {"compute": b_C, "energy": b_E, "security": b_S}, non-negative,
        summing to at most ``obs.budget``. Invalid values are clamped the way the
        live agent does it; an exception costs the round's bid (the engine then
        bids the preference weights, as the live agent does)."""


class FunctionAgent(Agent):
    """Adapt a plain function ``f(budget, prices, capacities, profile, history) -> bid``,
    the signature of the built-in strategies and bots. ``profile["_market"]["nodes"]``
    carries the public rivals."""

    def __init__(self, function: Callable[..., dict], name: str | None = None):
        self.function = function
        self.name = name or getattr(function, "__name__", "function")

    def bid(self, obs: Observation) -> dict:
        return self.function(obs.budget, dict(obs.prices), dict(obs.capacities),
                             obs.arena_profile(), list(obs.history))
