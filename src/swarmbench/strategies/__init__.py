"""The built-in strategies behind the catalog's 33 agents.

These modules are the bidding policies developed for the VelesHack 2026
challenge, kept as they were measured so that the stored results reproduce
bit for bit. They are reached through the catalog (``swarmbench.get_spec``);
:mod:`.strategy` holds the rule-based and one-round policies and dispatches
the planners (:mod:`.planner`, :mod:`.adaptive`), the identified-market model
(:mod:`.market_id`), the rival archetype learner (:mod:`.opponents`), the
LinUCB mode selector (:mod:`.bandit`), the learned shortlist
(:mod:`.shortlist`) and the CatBoost value export
(:mod:`.catboost_value_model`). The JSON files next to them are the offline
trained model parameters.

Every policy is a plain function ``f(budget, prices, capacities, profile,
history) -> bid`` that reads only public information.
"""
