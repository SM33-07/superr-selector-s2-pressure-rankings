import ast
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

BATTER_RANKINGS = [
    ("Abhishek Sharma", 46.0, 36, 58, 0.64, 327, 0.98),
    ("Suryakumar Yadav", 35.9, 30, 45, 0.67, 509, 1.00),
    ("Heinrich Klaasen", 32.4, 26, 38, 0.68, 228, 0.92),
    ("Phil Salt", 33.3, 22, 40, 0.58, 241, 0.88),
    ("Tim David", 31.7, 25, 42, 0.63, 334, 0.85),
    ("Travis Head", 28.1, 13, 41, 0.61, 168, 0.60),
    ("Yashasvi Jaiswal", 22.2, 11, 30, 0.71, 258, 0.35),
    ("Jos Buttler", 23.0, 15, 31, 0.65, 320, 0.45),
    ("Shreyas Iyer", 23.2, 15, 31, 0.60, 379, 0.28),
    ("Andre Russell", 22.1, 11, 31, 0.63, 163, 0.38),
]

BOWLER_RANKINGS = [
    ("Sunil Narine", 26.3, 18, 33, 0.56, 309, 0.95),
    ("Rashid Khan", 24.5, 15, 29, 0.55, 461, 0.75),
    ("Kuldeep Yadav", 22.2, 14, 28, 0.63, 349, 0.72),
    ("Varun Chakravarthy", 23.7, 15, 33, 0.56, 359, 0.78),
    ("Jasprit Bumrah", 22.1, 12, 33, 0.54, 348, 0.68),
    ("Josh Hazlewood", 22.0, 6, 34, 0.49, 274, 0.60),
    ("Mitchell Santner", 18.3, 12, 28, 0.59, 270, 0.40),
    ("Krunal Pandya", 17.8, 9, 27, 0.60, 216, 0.42),
    ("Mustafizur Rahman", 17.9, 11, 24, 0.59, 298, 0.45),
    ("Mohsin Khan", 19.7, 0, 39, 0.51, 143, 0.30),
]

PHASE = {
    "Abhishek Sharma": (232, 92, 3), "Suryakumar Yadav": (112, 306, 91),
    "Heinrich Klaasen": (8, 131, 89), "Phil Salt": (151, 76, 14),
    "Tim David": (11, 116, 207), "Travis Head": (133, 35, 0),
    "Yashasvi Jaiswal": (130, 121, 7), "Jos Buttler": (146, 116, 58),
    "Shreyas Iyer": (87, 218, 74), "Andre Russell": (0, 63, 100),
    "Sunil Narine": (32, 211, 66), "Rashid Khan": (36, 297, 128),
    "Kuldeep Yadav": (5, 229, 115), "Varun Chakravarthy": (51, 239, 69),
    "Jasprit Bumrah": (135, 69, 144), "Josh Hazlewood": (121, 51, 102),
    "Mitchell Santner": (50, 160, 60), "Krunal Pandya": (17, 189, 10),
    "Mustafizur Rahman": (63, 69, 166), "Mohsin Khan": (36, 56, 51),
}

ROBUSTNESS = [
    ("LI >= 1.25", "8/10", "7/10"),
    ("LI >= 2.0", "8/10", "8/10"),
    ("IPL balls only", "6/10", "7/10"),
    ("Recency-weighted", "7/10", "8/10"),
    ("Weaker shrinkage (150)", "9/10", "9/10"),
    ("Stronger shrinkage (1000)", "9/10", "9/10"),
    ("Rating only", "8/10", "8/10"),
    ("Consistency-heavy (50/50)", "8/10", "8/10"),
]


class ReportReconciliationTests(unittest.TestCase):
    def assert_csv_rankings(self, filename, expected):
        df = pd.read_csv(ROOT / "data" / filename)
        self.assertEqual(len(df), 10)
        self.assertEqual(df["rank"].tolist(), list(range(1, 11)))
        self.assertEqual(df["name"].nunique(), 10)
        self.assertEqual(df["name"].tolist(), [row[0] for row in expected])
        for index, row in enumerate(expected):
            name, rating, lo, hi, cons, balls, top10 = row
            actual = df.iloc[index]
            self.assertEqual(actual["name"], name)
            self.assertAlmostEqual(actual["pressure"], rating)
            self.assertEqual(actual["boot_lo"], lo)
            self.assertEqual(actual["boot_hi"], hi)
            self.assertAlmostEqual(actual["cons"], cons)
            self.assertEqual(actual["p_balls"], balls)
            self.assertAlmostEqual(actual["p_top10_rating"], top10)

    def test_batter_csv(self):
        self.assert_csv_rankings("batters.csv", BATTER_RANKINGS)

    def test_bowler_csv(self):
        self.assert_csv_rankings("bowlers.csv", BOWLER_RANKINGS)

    def test_phase_totals(self):
        dfs = {
            "batters.csv": pd.read_csv(ROOT / "data" / "batters.csv"),
            "bowlers.csv": pd.read_csv(ROOT / "data" / "bowlers.csv"),
        }
        totals = pd.concat(
            [df.set_index("name")["p_balls"] for df in dfs.values()]
        ).to_dict()
        for name, phases in PHASE.items():
            self.assertEqual(sum(phases), totals[name], name)

    def test_excluded_players_are_not_ranked(self):
        for filename in ("batters.csv", "bowlers.csv"):
            df = pd.read_csv(ROOT / "data" / filename)
            self.assertNotIn("Reeza Hendricks", df["name"].tolist())
            self.assertNotIn("Blessing Muzarabani", df["name"].tolist())

    def test_app_uses_exact_robustness_table(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        app_robustness = None
        for node in tree.body:
            if isinstance(node, ast.Assign):
                if any(isinstance(target, ast.Name) and target.id == "ROBUSTNESS" for target in node.targets):
                    app_robustness = ast.literal_eval(node.value)
        normalized = [(label.replace("≥", ">=").replace(" 1.25", " 1.25"), bat, bowl)
                      for label, bat, bowl in app_robustness]
        expected = ROBUSTNESS
        self.assertEqual(normalized, expected)
        self.assertNotIn('"10/10"', source)
        self.assertNotIn('"9/10"', source[source.find("Consistency-heavy"):])

    def test_apptest_runs_without_exceptions(self):
        try:
            from streamlit.testing.v1 import AppTest
        except ImportError:
            self.skipTest("Streamlit AppTest is unavailable")

        at = AppTest.from_file(str(ROOT / "app.py")).run(timeout=20)
        self.assertFalse(at.exception)

        at.radio[0].set_value("Bowlers").run(timeout=20)
        self.assertFalse(at.exception)


if __name__ == "__main__":
    unittest.main()
