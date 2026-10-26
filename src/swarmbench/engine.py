"""The market engine: one episode of the unchanged arena with chosen participants.

It drives the arena engine (:mod:`swarmbench.arena.state`) in-process, with no
sockets and no injected faults: the public swarm view is captured right
after a round opens, every admissible participant bids, the round settles, and
each agent receives its own results with the live agent's one-round lag. Bots
never read results, matching the shipped bot runner.

Fairness: every participant gets the same device, minted from the seed and
a fixed device label (:data:`DEVICE_LABEL`, used by every stored experiment),
so a score compares strategies, not hardware draws.
"""

from copy import deepcopy
from dataclasses import dataclass, field
import math
from pathlib import Path
import statistics
import time

from .agent import RESOURCES, Agent, Observation
from .arena.config import SCENARIO_DIR, ScenarioConfig
from .arena.state import Arena
from .catalog import AgentSpec

#: Seed label of the shared device. The arena mints a device from the seed and
#: this label, so changing it changes every device and every stored score.
DEVICE_LABEL = "CardanoEdge"


@dataclass
class Seat:
    """A participant: an agent instance seated under a team name."""

    spec: AgentSpec
    team: str
    agent: Agent
    baseline: bool                     # registered as a supplied bot (real bot name)
    node: object = None
    history: list = field(default_factory=list)
    ms: list = field(default_factory=list)
    exceptions: int = 0


@dataclass
class EpisodeResult:
    """The outcome of one episode."""

    seed: int
    lsw_total: float                   # sum over rounds of the arena's log social welfare
    welfare: float                     # utilitarian welfare: sum of all participants' scores
    rows: list                         # one dict per participant


def _sanitise(bid, budget: float) -> dict:
    """The live agent's last line of defence: non-finite or negative values become 0,
    an over-budget bid is scaled down to the budget."""
    clean = {}
    for k in RESOURCES:
        try:
            v = float((bid or {}).get(k, 0.0))
        except (TypeError, ValueError, AttributeError):
            v = 0.0
        if v != v or v in (float("inf"), float("-inf")) or v < 0.0:
            v = 0.0
        clean[k] = v
    total = sum(clean.values())
    if total > budget and total > 0:
        clean = {k: v * (budget / total) for k, v in clean.items()}
    return clean


class Market:
    """One configured market; call :meth:`play` once per seed.

    ``scenario`` is a bundled scenario name (``graded``, ``practice``) or a path
    to a scenario YAML file; ``rounds`` overrides its length; ``capacity_scale``
    multiplies the pool capacities (e.g. to size them for a larger market).
    """

    def __init__(self, scenario: str = "graded", rounds: int | None = None,
                 device_label: str = DEVICE_LABEL, history_lag: int = 1, capacity_scale: float = 1.0):
        self.scenario, self.rounds = scenario, rounds
        self.device_label, self.history_lag = device_label, history_lag
        self.capacity_scale = capacity_scale      # >1 sizes the pools for a larger market

    def config(self, seed: int) -> ScenarioConfig:
        """The scenario configuration of one episode."""
        path = Path(self.scenario)
        if path.suffix not in (".yaml", ".yml"):
            path = SCENARIO_DIR / f"{self.scenario}.yaml"
        config = ScenarioConfig.from_yaml(path)
        config.seed = seed
        if self.rounds:
            config.total_rounds = self.rounds
        config.capacity_base *= self.capacity_scale
        # In-process, participants decide one after another: the wall-clock
        # window must never close a round mid-way (no effect on game logic).
        config.round_seconds, config.lease_seconds = 1e9, 2e9
        config.validate()
        return config

    def play(self, seed: int, seats: list[Seat], observer=None) -> EpisodeResult:
        """Play one episode. ``observer(state, seats)``, if given, is called after
        every settled round (for traces; it must not change anything)."""
        config = self.config(seed)
        arena = Arena(config)
        template = arena._mint_node(self.device_label, False)   # the shared device
        for seat in seats:
            seat.node = arena.register(seat.team, is_baseline=seat.baseline)
            seat.agent.reset(seed)
        for seat in seats:
            arena.clone_device(seat.node, template)
        oracles = [i for i, s in enumerate(seats) if getattr(s.agent, "clairvoyant", False)]
        if oracles:
            arena.log = lambda *args, **kwargs: None    # outcome-neutral; keeps market copies small
        lsw = 0.0
        for _ in range(config.total_rounds):
            state = arena.open_round()
            public = deepcopy(arena.swarm())
            for i, seat in enumerate(seats):
                if i not in oracles:
                    self._bid(arena, state, public, seat, config)
            for i in oracles:           # clairvoyant references bid last, seeing the others
                self._clairvoyant(arena, state, public, seats, i, config)
            lsw += self._close(arena, state, seats, observer)
        board = {row["node_id"]: row for row in arena.leaderboard()}
        rows = []
        for seat in seats:
            row = board[seat.node.node_id]
            others = [r for r in board.values() if r["node_id"] != seat.node.node_id]
            rows.append({
                "seed": seed, "agent": seat.spec.key, "team": seat.team, "bot": seat.spec.bot,
                "score": row["score"], "rank": row["rank"], "nodes": len(board),
                "beat_all": all(row["score"] > r["score"] for r in others),
                "participated": row["rounds_participated"], "idle": row["rounds_idle"],
                "missed": row["rounds_missed"], "floors": row["floor_violations"],
                "exceptions": seat.exceptions, "decisions": len(seat.ms),
                "ms_mean": statistics.fmean(seat.ms) if seat.ms else 0.0,
                "ms_max": max(seat.ms) if seat.ms else 0.0,
                "others_score": sum(r["score"] for r in others),
            })
        welfare = sum(r["score"] for r in board.values())
        for r in rows:
            r["lsw_total"], r["welfare"] = lsw, welfare
        return EpisodeResult(seed=seed, lsw_total=lsw, welfare=welfare, rows=rows)

    # ------------------------------------------------------------------ steps
    def _observe(self, seat: Seat, state, public, config) -> Observation:
        node = seat.node
        history = [] if seat.baseline else \
            [e for e in seat.history if e["round"] < state.index - self.history_lag]
        return Observation(round=state.index, total_rounds=config.total_rounds,
                           budget=node.budget, prices=dict(state.prices),
                           capacities=dict(state.capacities), profile=node.profile(),
                           rivals=[n for n in public if n["node_id"] != node.node_id],
                           history=history)

    def _bid(self, arena, state, public, seat: Seat, config, record: bool = True,
             agent: Agent | None = None) -> None:
        node = seat.node
        if not node.admissible(config.battery_cutoff, config.kappa_bar):
            return
        obs = self._observe(seat, state, public, config)
        started = time.perf_counter()
        try:
            bid = (agent or seat.agent).bid(obs)
        except Exception:
            # the live agent bids its preference weights when a strategy raises.
            if record:
                seat.exceptions += 1
            bid = {k: node.budget * obs.weights[k] for k in RESOURCES}
        if record:
            seat.ms.append(1000 * (time.perf_counter() - started))
        arena.submit(node, state.index, _sanitise(bid, node.budget))

    def _close(self, arena, state, seats, observer=None) -> float:
        arena.settle()
        if observer:
            observer(state, seats)
        for seat in seats:
            result = arena.result_for(seat.node, state.index)
            if result["participated"]:
                seat.history.append(result)
        return state.lsw

    def _clairvoyant(self, arena, state, public, seats, i: int, config) -> None:
        """A reference oracle sees the others' bids and evaluates candidates in copies."""
        seat = seats[i]
        node = seat.node
        if not node.admissible(config.battery_cutoff, config.kappa_bar):
            return
        obs = self._observe(seat, state, public, config)
        rival_bids = {nid: dict(b) for nid, b in state.bids.items() if nid != node.node_id}
        others = {k: sum(float(b.get(k, 0.0)) for b in rival_bids.values()) for k in RESOURCES}
        started = time.perf_counter()
        bid = seat.agent.choose(obs, others, rival_bids,
                                lambda first: self._rollout(arena, seats, i, _sanitise(first, node.budget),
                                                            seat.agent.horizon_for(obs), config))
        seat.ms.append(1000 * (time.perf_counter() - started))
        arena.submit(node, state.index, _sanitise(bid, node.budget))

    def _rollout(self, arena, seats, i: int, first: dict, horizon: int, config) -> float:
        """Play ``first`` now and ``horizon`` more rounds in a copy; the oracle's utility."""
        arena, seats = deepcopy((arena, seats))
        me = seats[i]
        state = arena.current
        arena.submit(me.node, state.index, first)
        self._close(arena, state, seats)
        total = arena.result_for(me.node, state.index).get("utility", 0.0) or 0.0
        for _ in range(horizon):
            if len(arena.rounds) >= config.total_rounds:
                break
            state = arena.open_round()
            public = deepcopy(arena.swarm())
            for j, seat in enumerate(seats):
                if j != i:
                    self._bid(arena, state, public, seat, config, record=False)
            if me.node.admissible(config.battery_cutoff, config.kappa_bar):
                # inside the rollout the oracle still sees the others' bids: battery-safe best response
                obs = self._observe(me, state, public, config)
                others = {k: sum(float(b.get(k, 0.0)) for nid, b in state.bids.items()
                                 if nid != me.node.node_id) for k in RESOURCES}
                arena.submit(me.node, state.index, _sanitise(me.agent.base_bid(obs, others), me.node.budget))
            self._close(arena, state, seats)
            total += arena.result_for(me.node, state.index).get("utility", 0.0) or 0.0
        return total


def seat(spec: AgentSpec, team: str | None = None, baseline: bool | None = None) -> Seat:
    """Seat a catalog agent. Bots keep their real names unless ``team`` is given."""
    if baseline is None:
        baseline = spec.bot and team is None
    team = team or (f"bot-{spec.key}" if spec.bot else f"agent-{spec.key}")
    return Seat(spec=spec, team=team, agent=spec.make(), baseline=baseline)


def finite(x: float) -> bool:
    return x is not None and math.isfinite(x)
