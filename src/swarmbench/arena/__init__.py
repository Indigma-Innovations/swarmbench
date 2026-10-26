"""The CoGNETs Swarm Arena game engine, run in-process by SwarmBench.

This is the unchanged game logic of the arena prepared by the CoGNETs
consortium for the VelesHack 2026 challenge "Dynamic Node Registration and
Resource Allocation in an Edge Computing Environment": the node registry,
round lifecycle, Kelly allocation, CES utility with service floors, battery
physics and scoring (:mod:`.state`, :mod:`.game`) and the scenario files
(:mod:`.config`, ``scenarios/*.yaml``). The HTTP server, fault injection and
dashboard of the original arena are not part of SwarmBench.

Copyright 2026 The CoGNETs Consortium
SPDX-License-Identifier: Apache-2.0
"""

__all__ = ["config", "game", "state"]
