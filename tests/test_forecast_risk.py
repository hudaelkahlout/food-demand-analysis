"""Focused deterministic checks for post-hoc error analysis (no model training)."""
import unittest
import numpy as np
import pandas as pd
from src.machine_learning.forecast_risk import assign_bands, risk_summary, validate_holdout


def fixture():
    rows = []
    for meal, actual, predicted, weeks in [(1, 10, 12, 10), (2, 20, 14, 10), (3, 0, 10, 7)]:
        for week in range(136, 136 + weeks):
            rows.append([len(rows) + 1, week, meal, 5, actual, predicted])
    return pd.DataFrame(rows, columns=["id", "week", "meal_id", "center_id", "num_orders", "Random Forest"])


class ForecastRiskTests(unittest.TestCase):
    def test_mae_bias_wape_and_conservation(self):
        f = fixture()
        t, _ = risk_summary(f, ["meal_id"])
        one = t.set_index("meal_id").loc[1]
        self.assertEqual((one.mae, one.bias, one.wape_pct), (2, 2, 20))
        self.assertEqual(t.observations.sum(), len(f))
        self.assertAlmostEqual(t.absolute_error_sum.sum() / len(f), (20 + 60 + 70) / 27)
        self.assertTrue(np.isnan(t.set_index("meal_id").loc[3, "wape_pct"]))
        self.assertEqual(t.set_index("meal_id").loc[2, "bias"], -6)

    def test_sparse_pairs_retained_without_zero_filling(self):
        t, meta = risk_summary(fixture(), ["meal_id", "center_id"], 8)
        sparse = t[t.meal_id == 3].iloc[0]
        self.assertEqual((sparse.observations, sparse.observed_weeks, sparse.risk_band), (7, 7, "Insufficient coverage"))
        self.assertEqual(meta["eligible_groups"], 2)
        self.assertEqual(t.observations.sum(), 27)

    def test_tertile_boundaries_and_ties(self):
        labels, limits = assign_bands(np.array([0., 3., 6., 9.]))
        self.assertEqual(labels.tolist(), ["Low", "Low", "Medium", "High"])
        self.assertEqual(limits, {"low_max_mae": 3., "medium_max_mae": 6.})
        self.assertEqual(assign_bands(np.ones(6))[0].tolist(), ["Low"] * 6)

    def test_eight_week_boundary(self):
        f = fixture()
        extra = f[f.meal_id == 3].iloc[-1:].copy()
        extra["week"], extra["id"] = 143, 99
        t, _ = risk_summary(pd.concat([f, extra]), ["meal_id", "center_id"], 8)
        self.assertTrue(t[t.meal_id == 3].iloc[0].eligible)

    def test_order_invariance(self):
        a, am = risk_summary(fixture(), ["meal_id"], 1)
        b, bm = risk_summary(fixture().sample(frac=1, random_state=42), ["meal_id"], 1)
        pd.testing.assert_frame_equal(a, b)
        self.assertEqual(am, bm)

    def test_reject_duplicate_id_and_series_week(self):
        f = fixture()
        for same_id in [True, False]:
            duplicate = f.iloc[:1].copy()
            if not same_id:
                duplicate["id"] = 999
            with self.assertRaises(ValueError):
                validate_holdout(pd.concat([f, duplicate]))

    def test_reject_invalid_targets_predictions_and_window(self):
        for column, value in [("num_orders", -1), ("Random Forest", np.inf),
                              ("Random Forest", np.nan), ("week", 135), ("meal_id", 1.5)]:
            f = fixture().astype(float)
            f.loc[0, column] = value
            with self.assertRaises(ValueError):
                validate_holdout(f)

    def test_reject_unusable_calibration(self):
        for values in [np.array([]), np.array([np.nan]), np.array([-1.])]:
            with self.assertRaises(ValueError):
                assign_bands(values)
        with self.assertRaises(ValueError):
            risk_summary(fixture(), ["meal_id"], 11)


if __name__ == "__main__":
    unittest.main()
