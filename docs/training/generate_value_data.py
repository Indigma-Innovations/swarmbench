"""Value-model corpus: public states of `lookahead` against the bots, labeled with the realized remaining score.

    python generate_value_data.py 4001 100 value.jsonl
"""

import json
from pathlib import Path
import sys

import swarmbench as sb
from swarmbench.arena.game import clearing_prices
from swarmbench.strategies.planner import value_features


def episode(market: sb.Market, seed: int) -> list[dict]:
    seats = [sb.seat(sb.get_spec(bot)) for bot in ("naive-max", "even-split", "proportional")]
    me = sb.seat(sb.get_spec("lookahead"), team="agent-lookahead", baseline=False)
    seats.append(me)
    total = market.config(seed).total_rounds
    states = []

    def observe(state, seats):  # after every settled round: the public state the agent sees next
        prices = {k: round(max(0.01, v), 6) for k, v in clearing_prices(state.bids, state.capacities).items()}
        rivals = [s.node.public() for s in seats if s is not me]
        states.append((state.index, value_features(me.node.profile(), rivals, prices, total - state.index)))

    market.play(seed, seats, observer=observe)
    utility = {r["round"]: float(r.get("utility", 0)) for r in me.history}
    rows, remaining_score = [], 0.0
    for index, features in reversed(states):  # last round first, as the original corpus
        if index < total:
            rows.append({"episode_seed": seed, "features": features, "target_remaining_score": remaining_score})
        remaining_score += utility.get(index, 0.0)
    return rows


def main() -> None:
    first, count, output = int(sys.argv[1]), int(sys.argv[2]), Path(sys.argv[3])
    market = sb.Market("graded")
    with output.open("w", encoding="utf-8") as out:
        for seed in range(first, first + count):
            for row in episode(market, seed):
                out.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
