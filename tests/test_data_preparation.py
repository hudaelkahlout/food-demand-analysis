"""Deterministic Phase 5 integrity tests; no dependency on the real datasets."""

import csv
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.data_processing.prepare import (
    DataValidationError, SCHEMAS, demand_audit, duplicate_rows, iqr_limits,
    load_csv, quantile, sha256, table_audit, validated_left_join, week_coverage,
)


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("CREATE TABLE demand (id TEXT, week TEXT, center_id TEXT, meal_id TEXT, num_orders TEXT)")
        self.connection.executemany("INSERT INTO demand VALUES (?,?,?,?,?)", [("1", "1", "10", "20", "100"), ("2", "2", "10", "20", "200")])
        self.connection.execute("CREATE TABLE meals (meal_id TEXT, category TEXT)")
        self.connection.execute("INSERT INTO meals VALUES ('20','Beverages')")

    def tearDown(self):
        self.connection.close()

    def test_many_to_one_preserves_each_row_and_total(self):
        result = validated_left_join(self.connection, "demand", "meals", "meal_id", "enriched")
        self.assertEqual(result["before"], result["after"])
        self.assertEqual(result["after"]["num_orders_total"], 300)
        self.assertEqual(result["duplicate_expansion_rows"], 0)
        self.assertEqual(self.connection.execute("SELECT id,category FROM enriched ORDER BY rowid").fetchall(), [("1", "Beverages"), ("2", "Beverages")])

    def test_duplicate_lookup_rejected_before_expansion(self):
        self.connection.execute("INSERT INTO meals VALUES ('20','Conflicting')")
        with self.assertRaisesRegex(DataValidationError, "Duplicate lookup"):
            validated_left_join(self.connection, "demand", "meals", "meal_id", "bad")
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='bad'").fetchone()[0], 0)

    def test_unmatched_key_rejected(self):
        self.connection.execute("UPDATE meals SET meal_id='99'")
        with self.assertRaisesRegex(DataValidationError, "Unmatched lookup"):
            validated_left_join(self.connection, "demand", "meals", "meal_id", "bad")

    def test_missing_join_key_rejected(self):
        self.connection.execute("UPDATE meals SET meal_id=''")
        with self.assertRaisesRegex(DataValidationError, "Missing join key"):
            validated_left_join(self.connection, "demand", "meals", "meal_id", "bad")

    def test_overlapping_nonkey_column_rejected(self):
        self.connection.execute("ALTER TABLE meals ADD COLUMN num_orders TEXT")
        with self.assertRaisesRegex(DataValidationError, "Overlapping"):
            validated_left_join(self.connection, "demand", "meals", "meal_id", "bad")

    def test_missing_and_different_duplicate_definitions(self):
        self.connection.execute("INSERT INTO demand VALUES ('3','1','10','20','100')")
        self.connection.execute("INSERT INTO demand VALUES ('3','1','10','20','100')")
        self.connection.execute("INSERT INTO demand VALUES ('4','3','10','20','NA')")
        audit = table_audit(self.connection, "demand")
        self.assertEqual(audit["exact_duplicate_rows_beyond_first"], 1)
        self.assertEqual(audit["logical_duplicate_rows_beyond_first"], 2)
        self.assertEqual(audit["missing"]["num_orders"]["count"], 1)
        self.assertEqual(audit["missing"]["num_orders"]["percent"], 20)

    def test_coverage_distinguishes_internal_and_boundary_absence(self):
        summary, details = week_coverage({("a", "m"): {1, 3}, ("b", "m"): {2, 4}}, 1, 4)
        self.assertEqual(summary["internal_absent_slots"], 2)
        self.assertEqual(summary["leading_absent_slots"], 1)
        self.assertEqual(summary["trailing_absent_slots"], 1)
        self.assertEqual(summary["absent_slots_within_observed_groups"], 4)
        self.assertEqual(summary["groups_with_internal_gaps"], 2)

    def test_quantile_interpolation_and_constant_series(self):
        self.assertEqual(quantile([0, 10, 20, 30], .25), 7.5)
        self.assertEqual(iqr_limits([10, 10, 10, 10]), (10, 10))
        self.assertIsNone(quantile([], .5))

    def test_anomalies_preserved_and_loader_does_not_write_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "train.csv"
            with path.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(SCHEMAS["train"])
                for i, orders in enumerate([10, 10, 10, 10, 1000], 1):
                    writer.writerow([str(i), str(i), "10", "20", "101.00", "100.00", "0", "0", str(orders)])
            before = sha256(path)
            load_csv(self.connection, path, "source", SCHEMAS["train"])
            audit = demand_audit(self.connection, "source", Path(temporary) / "coverage.csv")
            self.assertEqual(audit["pricing"]["checkout_above_base_rows"], 5)
            self.assertEqual(audit["orders"]["global_iqr_outlier_rows"], 1)
            self.assertEqual(audit["retention"]["rows_after"], 5)
            self.assertEqual(audit["retention"]["num_orders_after"], 1040)
            self.assertEqual(audit["retention"]["rows_removed"], 0)
            self.assertEqual(sha256(path), before)

    def test_malformed_row_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "bad.csv"
            path.write_text("meal_id,category,cuisine\n20,OnlyTwoFields\n", encoding="utf-8")
            with self.assertRaisesRegex(DataValidationError, "Malformed"):
                load_csv(self.connection, path, "source", SCHEMAS["meal_info"])


if __name__ == "__main__":
    unittest.main()
