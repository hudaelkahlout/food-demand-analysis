"""Independent full-output cross-check for Phase 5; writes no datasets."""

from collections import defaultdict
import argparse
import csv
from decimal import Decimal
import hashlib
from itertools import zip_longest
import json
from pathlib import Path
import statistics
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase5-snapshot', action='store_true', help='Require later analysis notebook to be absent (historical Phase 5 boundary only)')
    args = parser.parse_args()
    audit = json.loads((ROOT / "docs/phase5_audit.json").read_text(encoding="utf-8"))
    inventory = (ROOT / "docs/data_inventory.md").read_text(encoding="utf-8")
    raw = ROOT / "data/raw"
    hashes = {path.name: digest(path) for path in raw.glob("*.csv")}
    assert len(hashes) == 4
    assert hashes == audit["raw_sha256_before"] == audit["raw_sha256_after"]
    assert all(value in inventory for value in hashes.values())
    lookups = {}
    for name, key in [("meal_info", "meal_id"), ("fulfilment_center_info", "center_id")]:
        with (raw / f"{name}.csv").open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
        lookups[key] = {row[key]: row for row in rows}
        assert len(lookups[key]) == len(rows)
    total, count, above_count, above_orders = 0, 0, 0, 0
    orders, series = [], defaultdict(set)
    with (raw / "train.csv").open(newline="", encoding="utf-8-sig") as source:
        with (ROOT / "data/processed/train_prepared.csv").open(newline="", encoding="utf-8") as enriched:
            original_reader, prepared_reader = csv.DictReader(source), csv.DictReader(enriched)
            expected_columns = original_reader.fieldnames + ["category", "cuisine", "city_code", "region_code", "center_type", "op_area"]
            assert prepared_reader.fieldnames == expected_columns
            for original, prepared in zip_longest(original_reader, prepared_reader):
                assert original is not None and prepared is not None, "Output length mismatch"
                assert all(prepared[key] == value for key, value in original.items()), "Source cell/order mismatch"
                for key, lookup in lookups.items():
                    assert all(prepared[name] == value for name, value in lookup[original[key]].items()), "Incorrect lookup values"
                count += 1
                n = int(original["num_orders"])
                orders.append(n)
                total += n
                series[(original["center_id"], original["meal_id"])].add(int(original["week"]))
                if Decimal(original["checkout_price"]) > Decimal(original["base_price"]):
                    above_count += 1
                    above_orders += n
    assert count == 456548 and total == audit["prepared_audit"]["num_orders_total"]
    for merge in audit["merges"]:
        assert merge["before"] == merge["after"]
        assert merge["before"]["rows"] == count and merge["before"]["num_orders_total"] == total
        assert not any(merge[key] for key in ("unmatched_rows_before", "unmatched_keys_before", "unmatched_rows_after", "unmatched_keys_after", "duplicate_expansion_rows"))
    quality = audit["quality"]
    assert above_count == quality["pricing"]["checkout_above_base_rows"]
    assert above_orders == quality["pricing"]["checkout_above_base_order_total"]
    q1, _, q3 = statistics.quantiles(orders, n=4, method="inclusive")
    lower, upper = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    assert [lower, upper] == quality["orders"]["global_iqr_fences"]
    assert sum(n < lower or n > upper for n in orders) == quality["orders"]["global_iqr_outlier_rows"]
    assert sum(n for n in orders if n < lower or n > upper) == quality["orders"]["global_outlier_orders"]
    with (ROOT / "data/processed/center_meal_week_coverage.csv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == len(series)
    for row in rows:
        weeks = sorted(series[(row["center_id"], row["meal_id"])])
        assert int(row["observed_weeks"]) == len(weeks)
        assert int(row["first_week"]) == weeks[0] and int(row["last_week"]) == weeks[-1]
        assert int(row["leading_absent"]) == weeks[0] - 1
        assert int(row["trailing_absent"]) == 145 - weeks[-1]
        assert int(row["internal_absent"]) == weeks[-1] - weeks[0] + 1 - len(weeks)
    coverage = quality["weeks"]["center_meal_level"]
    for field, summary in [("leading_absent", "leading_absent_slots"), ("internal_absent", "internal_absent_slots"), ("trailing_absent", "trailing_absent_slots")]:
        assert sum(int(row[field]) for row in rows) == coverage[summary]
    profiles = ROOT / "data/processed/phase5_skill"
    for name, table in audit["input_audits"].items():
        profile = json.loads((profiles / f"{name}_profile.json").read_text())
        assert profile["analysis"]["rows_scanned"] == table["rows"]
        assert not profile["analysis"]["row_limit_reached"]
    for artifact in audit["outputs"].values():
        assert digest(ROOT / artifact["path"]) == artifact["sha256"]
    probes = ["data/raw/train.csv", "data/processed/train_prepared.csv", "data/processed/center_meal_week_coverage.csv", "data/processed/phase5_skill/train_profile.json"]
    with tempfile.TemporaryDirectory(prefix="food-demand-phase5-git-") as directory:
        subprocess.run(["git", "init", "--bare", "--quiet", directory], check=True)
        for probe in probes:
            check = subprocess.run(["git", f"--git-dir={directory}", f"--work-tree={ROOT}", "check-ignore", "--no-index", "-v", "--", probe], capture_output=True, text=True, check=True)
            assert "/data/" in check.stdout
    assert hashes == {path.name: digest(path) for path in raw.glob("*.csv")}
    notebook_exists = (ROOT / "notebooks/analysis.ipynb").exists()
    if args.phase5_snapshot:
        assert not notebook_exists
    print(json.dumps({"status": "passed", "rows_independently_verified": count, "num_orders_independently_verified": total,
                      "all_original_cells_row_order_and_lookup_attributes": "passed", "merge_conservation": "passed",
                      "exact_pricing_and_global_iqr_counts": "passed", "all_center_meal_week_coverage": "passed",
                      "skill_full_row_scans": "passed", "output_hashes": "passed", "git_ignore_probes": len(probes),
                      "raw_unchanged": True, "phase6_notebook": "present; outside Phase 5 scope" if notebook_exists else "absent"}, indent=2))


if __name__ == "__main__":
    main()
