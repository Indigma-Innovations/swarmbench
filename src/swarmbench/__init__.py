"""SwarmBench: a benchmark for strategic agents in the CoGNETs Swarm Arena.

    import swarmbench as sb

    class MyAgent(sb.Agent):
        def bid(self, obs: sb.Observation) -> dict:
            return {k: obs.budget * obs.weights[k] for k in sb.RESOURCES}

    sb.register_agent("my-agent", MyAgent)
    rows = sb.run_mode("solo", ["my-agent", "cycle-aware"], range(70001, 70011))

Write an agent (subclass :class:`Agent`), register it, and run any of the
three modes: ``solo`` (against the three supplied bots), ``head-to-head``
(every pair) and ``all-together`` (one shared market).
"""
__version__ = "1.0.0"

from .agent import RESOURCES, Agent, FunctionAgent, Observation
from .catalog import CATALOG, FAMILIES, AgentSpec, get_spec, ordered, register_agent, resolve
from .engine import EpisodeResult, Market, Seat, seat
from .modes import MODES, jobs, play, run_mode

__all__ = ["CATALOG", "FAMILIES", "MODES", "RESOURCES", "Agent", "AgentSpec", "EpisodeResult", "FunctionAgent",
           "Market", "Observation", "Seat", "__version__", "get_spec", "jobs", "ordered", "play",
           "register_agent", "resolve", "run_mode", "seat"]
