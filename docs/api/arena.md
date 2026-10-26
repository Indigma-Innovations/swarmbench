# Arena engine

The game engine of the CoGNETs Swarm Arena, unchanged apart from packaging.
SwarmBench drives it through [`Market`](engine.md#swarmbench.engine.Market);
you rarely need it directly.

::: swarmbench.arena

::: swarmbench.arena.game

::: swarmbench.arena.config
    options:
      members: [ScenarioConfig, SCENARIO_DIR]

::: swarmbench.arena.state
    options:
      members: [Arena, NodeState, RoundState]
