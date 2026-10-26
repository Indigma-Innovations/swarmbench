"""Checks for SwarmBench: catalog, engine, modes, reports, CLI and the stored results.

The checks against the stored results in ``results/paper`` are bit-identical
comparisons.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import swarmbench as sb
from swarmbench import cli
from swarmbench.report import load_rows, summarize

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "paper"
needs_results = unittest.skipUnless((RESULTS / "solo" / "episodes.csv.gz").exists(), "stored results not present")


class WeightAgent(sb.Agent):
    def bid(self, obs):
        return {k: obs.budget * obs.weights[k] for k in sb.RESOURCES}


class BrokenAgent(sb.Agent):
    def bid(self, obs):
        raise RuntimeError("boom")


def stored_scores(name: str, seed: int) -> dict:
    return {(r["table"], r["agent"]): r["score"] for r in load_rows(RESULTS / name) if r["seed"] == seed}


class CatalogTests(unittest.TestCase):
    def test_paper_roster_order_and_realism(self):
        paper = sb.resolve(["paper"])
        self.assertEqual(len(paper), 36)
        self.assertEqual([s.key for s in paper[:3]], ["naive-max", "even-split", "proportional"])
        families = [sb.FAMILIES.index(s.family) for s in paper]
        self.assertEqual(families, sorted(families), "families must follow the idea order")
        self.assertEqual(len({s.family for s in paper}), 5)
        realistic = {s.key for s in paper if s.realistic and not s.bot}
        self.assertEqual(realistic, {"template", "taper", "floors", "price-taker", "market-taper", "kelly",
                                     "kelly-drain", "kelly-blend", "ucb-energy", "identified-linear",
                                     "identified-logit", "identified-structural", "identified-robust"})
        self.assertTrue(all(s.realistic for s in paper if s.bot))

    def test_aliases_and_groups(self):
        self.assertEqual(sb.get_spec("oracle").key, "clairvoyant")   # aliases resolve to their entry
        with self.assertRaises(KeyError):
            sb.get_spec("no-such-agent")
        self.assertEqual(len(sb.resolve(["bots"])), 3)
        self.assertEqual(len(sb.resolve(["agents"])), 33)
        self.assertEqual([s.key for s in sb.resolve(["kelly", "kelly", "bots"])][:2], ["kelly", "naive-max"])
        with self.assertRaises(KeyError):
            sb.get_spec("no-such-agent")

    def test_jobs_per_mode(self):
        entries = ["a", "b", "c", "d"]
        self.assertEqual(len(sb.jobs("solo", entries, range(5))), 20)
        self.assertEqual(len(sb.jobs("head-to-head", entries, range(5))), 30)
        self.assertEqual(len(sb.jobs("all-together", entries, range(5))), 5)
        self.assertEqual(len(sb.jobs("head-to-head", entries, range(1), focus=["a"])), 3)

    def test_package_data_loads(self):
        from swarmbench.strategies import bandit, planner, shortlist
        self.assertIsNotNone(planner.load_value_model())
        self.assertIsNotNone(planner.load_catboost_model())
        self.assertTrue(bandit.PRIOR_PATH.exists())
        self.assertTrue(shortlist.MODEL_PATH.exists())
        config = sb.Market().config(1)
        self.assertEqual((config.name, config.total_rounds), ("graded", 60))

    def test_no_path_manipulation(self):
        source = Path(sb.__file__).parent
        offenders = [p.name for p in source.rglob("*.py") if "sys.path" in p.read_text(encoding="utf-8")]
        self.assertEqual(offenders, [])


class EngineTests(unittest.TestCase):
    def test_deterministic_and_welfare_is_sum_of_scores(self):
        first = sb.play(("all-together", ("naive-max", "kelly", "identified-linear"), 3), rounds=15)
        second = sb.play(("all-together", ("naive-max", "kelly", "identified-linear"), 3), rounds=15)
        self.assertEqual([r["score"] for r in first], [r["score"] for r in second])
        self.assertAlmostEqual(first[0]["welfare"], sum(r["score"] for r in first), places=9)

    def test_custom_agents_and_exception_fallback(self):
        for key in ("t-weights", "t-broken", "t-function"):
            sb.CATALOG.pop(key, None)
        sb.register_agent("t-weights", WeightAgent, family="Traditional (rules)")
        sb.register_agent("t-broken", BrokenAgent, family="Traditional (rules)")
        sb.register_agent("t-function", lambda: sb.FunctionAgent(
            lambda budget, prices, capacities, profile, history:
                {k: budget * profile["weights"][k] for k in sb.RESOURCES}), family="Traditional (rules)")
        try:
            rows = {r["agent"]: r for r in sb.play(("head-to-head", ("t-weights", "t-broken"), 9), rounds=10)}
            self.assertEqual(rows["t-broken"]["exceptions"], rows["t-broken"]["decisions"])
            self.assertEqual(rows["t-weights"]["exceptions"], 0)
            # the fallback bids the weights, so both played the same bids on the same device
            self.assertEqual(rows["t-weights"]["score"], rows["t-broken"]["score"])
            template = sb.play(("solo", ("template",), 9), rounds=10)[0]
            mine = sb.play(("solo", ("t-weights",), 9), rounds=10)[0]
            function = sb.play(("solo", ("t-function",), 9), rounds=10)[0]
            self.assertEqual(template["score"], mine["score"])
            self.assertEqual(template["score"], function["score"])
            with self.assertRaises(ValueError):
                sb.register_agent("t-weights", WeightAgent)
        finally:
            for key in ("t-weights", "t-broken", "t-function"):
                sb.CATALOG.pop(key, None)

    def test_market_and_seats(self):
        market = sb.Market(rounds=6)
        seats = [sb.seat(sb.get_spec(b)) for b in ("naive-max", "even-split", "proportional")]
        seats.append(sb.seat(sb.get_spec("kelly"), team="agent-kelly", baseline=False))
        episode = market.play(70001, seats)
        self.assertEqual(len(episode.rows), 4)
        self.assertEqual(sorted(r["rank"] for r in episode.rows), [1, 2, 3, 4])
        self.assertTrue(all(r["decisions"] <= 6 for r in episode.rows))


@needs_results
class StoredResultsTests(unittest.TestCase):
    """Fresh episodes must reproduce the stored scores bit for bit."""

    def test_solo_scores(self):
        want = stored_scores("solo", 70001)
        for key in ("template", "taper", "kelly", "kelly-drain", "ucb-energy", "identified-linear",
                    "identified-robust", "cycle-aware", "catboost-terminal", "linucb-modes",
                    "archetype-learning", "learned-shortlist"):
            self.assertEqual(sb.play(("solo", (key,), 70001))[0]["score"], want[(key, key)], key)

    def test_head_to_head_scores(self):
        want = stored_scores("head-to-head", 70002)
        for pair in (("kelly-drain", "cycle-aware"), ("identified-structural", "ucb-energy")):
            table = "|".join(pair)
            for row in sb.play(("head-to-head", pair, 70002)):
                self.assertEqual(row["score"], want[(table, row["agent"])], row["agent"])

    def test_heldout_scores(self):
        want = stored_scores("solo-heldout", 70003)
        opponents = ("energy-hoarder", "contrarian", "random")
        for key in ("kelly", "identified-robust"):
            row = sb.play(("solo", (key,), 70003), opponents=opponents)[0]
            self.assertEqual(row["score"], want[(key, key)], key)


class ReportAndCliTests(unittest.TestCase):
    def test_cli_run_report_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "h2h"
            argv = ["--mode", "head-to-head", "--agents", "template", "kelly", "naive-max",
                    "--seeds", "2", "--rounds", "8", "--workers", "1", "--output", str(out)]
            self.assertEqual(cli.main(argv), 0)
            rows = load_rows(out)
            self.assertEqual(len(rows), 3 * 2 * 2)
            summary = json.loads((out / "summary.json").read_text())
            self.assertEqual(set(summary["_matrix"]), {"template", "kelly", "naive-max"})
            self.assertIn("Win rate", (out / "report.md").read_text())
            self.assertEqual(cli.main(argv), 0)            # resumes: nothing new to run
            self.assertEqual(len(load_rows(out)), len(rows))

    def test_publish_then_reproduce(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            run = tmp / "run"
            argv = ["--mode", "solo", "--agents", "template", "kelly", "--seeds", "2", "--rounds", "6",
                    "--workers", "2", "--output", str(run), "--name", "tiny"]
            self.assertEqual(cli.main(argv), 0)
            self.assertEqual(cli.main(["--publish", str(run), "--results", str(tmp / "stored")]), 0)
            self.assertTrue((tmp / "stored" / "tiny" / "episodes.csv.gz").exists())
            code = cli.main(["--reproduce", "--experiments", "tiny", "--results", str(tmp / "stored"),
                             "--workers", "1", "--output", str(tmp / "again")])
            self.assertEqual(code, 0)

    def test_summary_metrics(self):
        rows = sb.run_mode("solo", ["template", "cycle-aware"], range(1, 3), workers=1, rounds=10)
        summary = summarize(rows, "solo")
        self.assertIn("gain_vs_reference", summary["template"])
        self.assertNotIn("gain_vs_reference", summary["cycle-aware"])
        for key in ("ms_mean", "welfare", "lsw", "mean_score", "ci95"):
            self.assertIn(key, summary["template"])

    @needs_results
    def test_stored_summaries_match_their_episodes(self):
        for name in ("solo", "head-to-head"):
            stored = json.loads((RESULTS / name / "summary.json").read_text())
            fresh = summarize(load_rows(RESULTS / name), name)
            for key in ("cycle-aware", "kelly-drain"):
                self.assertEqual(stored[key]["mean_score"], fresh[key]["mean_score"])

    @needs_results
    def test_win_rate_over_distinct_entries(self):
        """The head-to-head win rates of the paper count each distinct behaviour once."""
        fresh = summarize(load_rows(RESULTS / "head-to-head"), "head-to-head")
        expected = {"ucb-energy": 0.834, "kelly-drain": 0.829, "learned-shortlist": 0.810, "cycle-aware": 0.567}
        for key, value in expected.items():
            self.assertAlmostEqual(fresh[key]["win_rate_distinct"], value, places=3)
        refs = summarize(load_rows(RESULTS / "head-to-head-references"), "head-to-head")
        self.assertAlmostEqual(refs["clairvoyant"]["win_rate_distinct"], 0.866, places=3)

    @needs_results
    @unittest.skipUnless(importlib.util.find_spec("scipy"), "needs scipy (the analysis extra)")
    def test_metagame_matches_stored(self):
        from swarmbench.metagame import metagame
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("head-to-head", "head-to-head-references"):
                (Path(tmp) / name).mkdir()
                for file in ("spec.json", "summary.json"):
                    shutil.copyfile(RESULTS / name / file, Path(tmp) / name / file)
            fresh = metagame(Path(tmp) / "head-to-head")
        stored = json.loads((RESULTS / "head-to-head" / "metagame.json").read_text())
        for part in ("all", "realistic"):
            self.assertEqual(set(fresh[part]["support"]), set(stored[part]["support"]))
            for key, value in stored[part]["rating"].items():
                self.assertAlmostEqual(fresh[part]["rating"][key], value, delta=2e-3)
        self.assertEqual(fresh["references"], stored["references"])


if __name__ == "__main__":
    unittest.main()
