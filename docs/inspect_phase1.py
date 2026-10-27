"""Read-only Phase 1 CSV inspection. Run from any directory; emits JSON to stdout."""

import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
NAMES = ("train.csv", "test.csv", "meal_info.csv", "fulfilment_center_info.csv")
TEXT = {"category", "cuisine", "center_type"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(path):
    before = digest(path)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        columns = next(reader)
        assert len(set(columns)) == len(columns), "Duplicate column names"
        values = {column: set() for column in columns}
        missing = dict.fromkeys(columns, 0)
        integers = dict.fromkeys(columns, True)
        numeric = dict.fromkeys(columns, True)
        invalid_numeric = dict.fromkeys(columns, 0)
        seen_keys = set()
        duplicate_keys = 0
        malformed = 0
        count = 0
        logical = ("week", "center_id", "meal_id") if "week" in columns else ()
        primary = "id" if "id" in columns else columns[0]
        key_columns = logical or (primary,)
        price_above_base = 0
        for row in reader:
            count += 1
            if len(row) != len(columns):
                malformed += 1
                continue
            record = dict(zip(columns, row))
            key = tuple(record[column] for column in key_columns)
            duplicate_keys += key in seen_keys
            seen_keys.add(key)
            for column, value in record.items():
                if not value.strip() or value.strip().lower() in {"na", "nan", "null", "none", "n/a"}:
                    missing[column] += 1
                    continue
                values[column].add(value)
                integers[column] &= bool(re.fullmatch(r"[+-]?\d+", value))
                try:
                    finite = math.isfinite(float(value))
                except ValueError:
                    finite = False
                numeric[column] &= finite
                if column not in TEXT and not finite:
                    invalid_numeric[column] += 1
            if "checkout_price" in columns:
                price_above_base += float(record["checkout_price"]) > float(record["base_price"])
    types = {column: "integer" if integers[column] else "decimal" if numeric[column] else "string"
             for column in columns}
    ranges = {column: [min(map(float, items)), max(map(float, items))]
              for column, items in values.items() if numeric[column] and items}
    after = digest(path)
    assert before == after, f"File changed during inspection: {path.name}"
    return {
        "file": path.name, "bytes": path.stat().st_size, "rows": count,
        "column_count": len(columns), "columns": columns, "inferred_types": types,
        "missing_by_column": missing, "invalid_numeric_by_column": invalid_numeric,
        "malformed_width_rows": malformed, "primary_key": primary,
        "duplicate_primary_key_rows": count - len(values[primary]),
        "logical_key": list(key_columns), "duplicate_logical_key_rows": duplicate_keys,
        "distinct_counts": {column: len(items) for column, items in values.items()},
        "numeric_ranges": ranges,
        "promotion_values": {column: sorted(values[column]) for column in
                             ("emailer_for_promotion", "homepage_featured") if column in columns},
        "checkout_above_base_rows": price_above_base,
        "sha256_before": before, "sha256_after": after,
    }, values


def main():
    results = {}
    values = {}
    initial = {name: digest(RAW / name) for name in NAMES}
    for name in NAMES:
        results[name], values[name] = inspect(RAW / name)
    train = results["train.csv"]["columns"]
    test = results["test.csv"]["columns"]
    schema = {
        "train_only": [column for column in train if column not in test],
        "test_only": [column for column in test if column not in train],
        "shared_column_order_matches": [column for column in train if column in test] == test,
        "shared_type_mismatches": [column for column in test if column in train and
                                   results["train.csv"]["inferred_types"][column] !=
                                   results["test.csv"]["inferred_types"][column]],
        "overlapping_ids": len(values["train.csv"]["id"] & values["test.csv"]["id"]),
    }
    references = {}
    for name in ("train.csv", "test.csv"):
        references[name] = {
            "unmatched_distinct_meal_ids": len(values[name]["meal_id"] - values["meal_info.csv"]["meal_id"]),
            "unmatched_distinct_center_ids": len(values[name]["center_id"] - values["fulfilment_center_info.csv"]["center_id"]),
        }
    unchanged = all(digest(RAW / name) == initial[name] for name in NAMES)
    assert unchanged, "Source file changed during inspection run"
    print(json.dumps({"files": results, "train_test_schema": schema,
                      "reference_key_checks": references, "all_raw_hashes_unchanged": unchanged}, indent=2))


if __name__ == "__main__":
    main()
