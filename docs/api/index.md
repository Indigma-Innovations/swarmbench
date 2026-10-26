# API reference

Everything below is importable from the top-level package:

```python
import swarmbench as sb

sb.Agent, sb.Observation, sb.FunctionAgent, sb.RESOURCES      # writing agents
sb.register_agent, sb.get_spec, sb.resolve, sb.ordered         # the catalog
sb.CATALOG, sb.FAMILIES, sb.AgentSpec
sb.Market, sb.seat, sb.Seat, sb.EpisodeResult                  # one episode
sb.play, sb.run_mode, sb.jobs, sb.MODES                        # the modes
```

| Module | Content |
|---|---|
| [`swarmbench.agent`](agent.md) | `Agent`, `Observation`, `FunctionAgent` |
| [`swarmbench.catalog`](catalog.md) | the catalog and `register_agent` |
| [`swarmbench.engine`, `swarmbench.modes`](engine.md) | `Market`, `seat`, `play`, `run_mode` |
| [`swarmbench.report`, `swarmbench.metagame`, `swarmbench.oracle`](analysis.md) | metrics, reports, Nash averaging, the clairvoyant reference |
| [`swarmbench.arena`](arena.md) | the CoGNETs Swarm Arena game engine |
| [`swarmbench.bots`](bots.md) | the three supplied baseline bots |
| `swarmbench.cli` | the `swarmbench` command (see [command line](../cli.md)) |
| `swarmbench.strategies` | the built-in strategies, reached through the catalog |
