"""Phase 5 preparation. Run: python -m src.data_processing.prepare.

Preserve source cell strings, use SQLite for many-to-one enrichment, and write
derived artifacts only below data/processed. No deletion, imputation or modeling.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import platform
import sqlite3
import subprocess
import sys
import os

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = {
    "train": "id week center_id meal_id checkout_price base_price emailer_for_promotion homepage_featured num_orders".split(),
    "test": "id week center_id meal_id checkout_price base_price emailer_for_promotion homepage_featured".split(),
    "meal_info": "meal_id category cuisine".split(),
    "fulfilment_center_info": "center_id city_code region_code center_type op_area".split(),
}
INTEGER = set("id week center_id meal_id emailer_for_promotion homepage_featured num_orders city_code region_code".split())
DECIMAL = {"checkout_price", "base_price", "op_area"}
MISSING = {"", "na", "nan", "null", "none", "n/a"}


class DataValidationError(ValueError):
    """An input or merge failed a required integrity check."""


def require(condition, message):
    if not condition:
        raise DataValidationError(message)


def identifier(name):
    """Quote internal identifiers; never interpolate data values into SQL."""
    return '"' + name.replace('"', '""') + '"'


def sha256(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def columns(connection, table):
    return [row[1] for row in connection.execute(f"PRAGMA table_info({identifier(table)})")]


def is_missing(value):
    return value is None or value.strip().lower() in MISSING


def load_csv(connection, path, table, expected):
    """Strict CSV parsing and type validation; retain original field strings."""
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream, strict=True)
        header = next(reader)
        require(header == expected, f"Unexpected schema: {path.name}")
        require(len(set(header)) == len(header), "Duplicate column names")
        connection.execute(f"CREATE TABLE {identifier(table)} ({', '.join(identifier(c) + ' TEXT' for c in header)})")
        statement = f"INSERT INTO {identifier(table)} VALUES ({','.join('?' for _ in header)})"
        batch = []
        for row_number, row in enumerate(reader, 2):
            require(len(row) == len(header), f"Malformed record in {path.name}, CSV record {row_number}")
            for name, value in zip(header, row):
                if is_missing(value):
                    continue
                try:
                    if name in INTEGER:
                        require(str(int(value)) == value, f"Noncanonical integer in {name}")
                    elif name in DECIMAL:
                        require(Decimal(value).is_finite(), f"Nonfinite numeric field: {name}")
                except (ValueError, InvalidOperation) as error:
                    raise DataValidationError(f"Invalid {name} in {path.name}, record {row_number}") from error
            batch.append(row)
            if len(batch) == 5000:
                connection.executemany(statement, batch)
                batch.clear()
        if batch:
            connection.executemany(statement, batch)


def duplicate_rows(connection, table, keys):
    grouping = ', '.join(map(identifier, keys))
    query = f"SELECT COALESCE(SUM(n-1),0) FROM (SELECT COUNT(*) n FROM {identifier(table)} GROUP BY {grouping} HAVING COUNT(*)>1)"
    return connection.execute(query).fetchone()[0]


def table_summary(connection, table):
    names = columns(connection, table)
    summary = {"rows": connection.execute(f"SELECT COUNT(*) FROM {identifier(table)}").fetchone()[0]}
    summary["num_orders_total"] = (connection.execute(f"SELECT SUM(CAST(num_orders AS INTEGER)) FROM {identifier(table)}").fetchone()[0]
                                   if "num_orders" in names else None)
    for key in ("id", "meal_id", "center_id"):
        if key in names:
            summary[f"unique_{key}"] = connection.execute(f"SELECT COUNT(DISTINCT {identifier(key)}) FROM {identifier(table)}").fetchone()[0]
    if "week" in names:
        summary["unique_logical_keys"] = connection.execute(f"SELECT COUNT(*) FROM (SELECT week,center_id,meal_id FROM {identifier(table)} GROUP BY week,center_id,meal_id)").fetchone()[0]
    return summary


def table_audit(connection, table):
    names = columns(connection, table)
    summary = table_summary(connection, table)
    count = summary["rows"]
    missing = {}
    for name in names:
        n = connection.execute(f"SELECT COUNT(*) FROM {identifier(table)} WHERE {identifier(name)} IS NULL OR LOWER(TRIM({identifier(name)})) IN (?,?,?,?,?,?)", tuple(MISSING)).fetchone()[0]
        missing[name] = {"count": n, "percent": 100 * n / count if count else 0, "decision": "retain; no imputation"}
    logical = ["week", "center_id", "meal_id"] if "week" in names else [names[0]]
    return {**summary, "columns": len(names), "missing": missing,
            "exact_duplicate_rows_beyond_first": duplicate_rows(connection, table, names),
            "logical_key": logical, "logical_duplicate_rows_beyond_first": duplicate_rows(connection, table, logical),
            "primary_key_duplicate_rows_beyond_first": duplicate_rows(connection, table, ["id" if "id" in names else names[0]])}


def validated_left_join(connection, left, right, key, output):
    """Perform a lossless many-to-one join, reject missing or duplicate keys."""
    left_columns, right_columns = columns(connection, left), columns(connection, right)
    require(key in left_columns and key in right_columns, "Join key missing")
    require(not ((set(left_columns) & set(right_columns)) - {key}), "Overlapping non-key columns")
    require(duplicate_rows(connection, right, [key]) == 0, f"Duplicate lookup key: {right}.{key}")
    for table in (left, right):
        require(not any(is_missing(row[0]) for row in connection.execute(f"SELECT DISTINCT {identifier(key)} FROM {identifier(table)}")), f"Missing join key: {table}")
    before = table_summary(connection, left)
    unmatched_rows, unmatched_keys = connection.execute(
        f"SELECT COUNT(*),COUNT(DISTINCT l.{identifier(key)}) FROM {identifier(left)} l LEFT JOIN {identifier(right)} r ON l.{identifier(key)}=r.{identifier(key)} WHERE r.{identifier(key)} IS NULL").fetchone()
    require(unmatched_rows == 0, f"Unmatched lookup keys: {right}; rows={unmatched_rows}, keys={unmatched_keys}")
    additions = [f"r.{identifier(c)}" for c in right_columns if c != key]
    connection.execute(f"CREATE TABLE {identifier(output)} AS SELECT l.*, {', '.join(additions)} FROM {identifier(left)} l LEFT JOIN {identifier(right)} r ON l.{identifier(key)}=r.{identifier(key)} ORDER BY l.rowid")
    after = table_summary(connection, output)
    require(before == after, f"Join conservation failure: {output}")
    require(duplicate_rows(connection, output, ["id"]) == 0, "Duplicate expansion detected")
    unmatched_after = connection.execute(f"SELECT COUNT(*) FROM {identifier(output)} o LEFT JOIN {identifier(right)} r ON o.{identifier(key)}=r.{identifier(key)} WHERE r.{identifier(key)} IS NULL").fetchone()[0]
    return {"left": left, "right": right, "key": key, "output": output, "cardinality": "many-to-one",
            "before": before, "after": after, "lookup": table_summary(connection, right),
            "unmatched_rows_before": unmatched_rows, "unmatched_keys_before": unmatched_keys,
            "unmatched_rows_after": unmatched_after, "unmatched_keys_after": unmatched_keys,
            "duplicate_expansion_rows": after["rows"] - before["rows"], "validation": "passed"}


def quantile(ordered, probability):
    """Linear interpolation at (n-1)*p, using all supplied values."""
    if not ordered:
        return None
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def distribution(values):
    ordered = sorted(values)
    return {"count": len(ordered), "min": ordered[0] if ordered else None,
            **{label: quantile(ordered, p) for label, p in [("q01", .01), ("q25", .25), ("median", .5), ("q75", .75), ("q95", .95), ("q99", .99), ("q999", .999)]},
            "max": ordered[-1] if ordered else None}


def iqr_limits(values):
    ordered = sorted(values)
    q1, q3 = quantile(ordered, .25), quantile(ordered, .75)
    require(q1 is not None, "Cannot compute IQR on empty values")
    return q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)


def week_coverage(groups, first, last):
    """Measure leading/internal/trailing absence without inserting observations."""
    details = []
    for key, weeks in sorted(groups.items()):
        ordered = sorted(weeks)
        leading, trailing = ordered[0] - first, last - ordered[-1]
        gaps = [b - a - 1 for a, b in zip(ordered, ordered[1:]) if b > a + 1]
        internal = sum(gaps)
        details.append({"key": list(key), "observed_weeks": len(weeks), "first_week": ordered[0], "last_week": ordered[-1],
                        "leading_absent": leading, "internal_absent": internal, "trailing_absent": trailing,
                        "gap_runs": len(gaps), "longest_internal_gap": max(gaps, default=0)})
    summary = {"observed_groups": len(details), "window": [first, last],
               "groups_with_any_absence": sum(d["observed_weeks"] < last - first + 1 for d in details),
               "groups_with_internal_gaps": sum(d["internal_absent"] > 0 for d in details),
               "groups_with_leading_absence": sum(d["leading_absent"] > 0 for d in details),
               "groups_with_trailing_absence": sum(d["trailing_absent"] > 0 for d in details),
               "leading_absent_slots": sum(d["leading_absent"] for d in details),
               "internal_absent_slots": sum(d["internal_absent"] for d in details),
               "trailing_absent_slots": sum(d["trailing_absent"] for d in details),
               "longest_internal_gap": max((d["longest_internal_gap"] for d in details), default=0)}
    summary["absent_slots_within_observed_groups"] = sum(summary[k] for k in ("leading_absent_slots", "internal_absent_slots", "trailing_absent_slots"))
    return summary, details


def demand_audit(connection, table, detail_path):
    """Exact full-data diagnostics only; no inferential tests or demand EDA."""
    values = []
    grouped = defaultdict(list)
    pair_weeks, meal_weeks = defaultdict(set), defaultdict(set)
    positive_deltas = []
    prices_invalid, nonpositive_orders, bad_flags = 0, 0, 0
    above_count, above_orders, above_promoted = 0, 0, 0
    flagged_series, flagged_weeks = set(), set()
    rows = connection.execute(f"SELECT week,center_id,meal_id,checkout_price,base_price,emailer_for_promotion,homepage_featured,num_orders FROM {identifier(table)}")
    for week, center, meal, checkout, base, email, homepage, orders in rows:
        week, orders = int(week), int(orders)
        checkout, base = Decimal(checkout), Decimal(base)
        pair = (center, meal)
        values.append(orders)
        grouped[pair].append(orders)
        pair_weeks[pair].add(week)
        meal_weeks[(meal,)].add(week)
        nonpositive_orders += orders <= 0
        prices_invalid += base <= 0 or checkout <= 0
        bad_flags += email not in {"0", "1"} or homepage not in {"0", "1"}
        difference = checkout - base
        if difference > 0:
            positive_deltas.append(float(difference))
            above_count += 1
            above_orders += orders
            above_promoted += email == "1" or homepage == "1"
            flagged_series.add(pair)
            flagged_weeks.add(week)
    total = sum(values)
    lower, upper = iqr_limits(values)
    limits = {key: iqr_limits(items) for key, items in grouped.items()}
    global_count = global_orders = group_count = overlap = lower_count = 0
    within_groups_of_global = set()
    top = []
    for week, center, meal, order, email, homepage in connection.execute(f"SELECT week,center_id,meal_id,num_orders,emailer_for_promotion,homepage_featured FROM {identifier(table)}"):
        n = int(order)
        pair = (center, meal)
        global_flag = n < lower or n > upper
        local_flag = n < limits[pair][0] or n > limits[pair][1]
        group_count += local_flag
        overlap += global_flag and local_flag
        lower_count += n < lower
        if global_flag:
            global_count += 1
            global_orders += n
            within_groups_of_global.add(pair)
    # Inspect highest counts in their own series, with no identifiers in public logs.
    for week, center, meal, orders, email, homepage in connection.execute(f"SELECT week,center_id,meal_id,num_orders,emailer_for_promotion,homepage_featured FROM {identifier(table)} ORDER BY CAST(num_orders AS INTEGER) DESC, rowid LIMIT 10"):
        local = sorted(grouped[(center, meal)])
        n = int(orders)
        top.append({"orders": n, "series_observations": len(local), "series_median": quantile(local, .5),
                    "series_q99": quantile(local, .99), "series_rows_at_least_half_this_value": sum(x >= n / 2 for x in local),
                    "either_promotion": email == "1" or homepage == "1"})
    first, last = min(min(w) for w in pair_weeks.values()), max(max(w) for w in pair_weeks.values())
    series_summary, details = week_coverage(pair_weeks, first, last)
    meal_summary, _ = week_coverage(meal_weeks, first, last)
    with detail_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["center_id", "meal_id", "observed_weeks", "first_week", "last_week", "leading_absent", "internal_absent", "trailing_absent", "gap_runs", "longest_internal_gap"])
        for detail in details:
            writer.writerow(detail["key"] + [detail[k] for k in ("observed_weeks", "first_week", "last_week", "leading_absent", "internal_absent", "trailing_absent", "gap_runs", "longest_internal_gap")])
    global_weeks = set().union(*pair_weeks.values())
    possible_pairs = len({p[0] for p in pair_weeks}) * len({p[1] for p in pair_weeks})
    series_summary["never_observed_pairs_in_center_meal_cartesian_product"] = possible_pairs - len(pair_weeks)
    series_summary["slots_in_never_observed_pairs"] = (possible_pairs - len(pair_weeks)) * (last - first + 1)
    require(len(values) + series_summary["absent_slots_within_observed_groups"] == len(pair_weeks) * (last - first + 1), "Coverage accounting failed")
    return {"pricing": {"checkout_above_base_rows": above_count, "checkout_above_base_order_total": above_orders,
                        "other_rows": len(values) - above_count, "other_order_total": total - above_orders,
                        "affected_series": len(flagged_series), "affected_weeks": len(flagged_weeks),
                        "positive_difference_distribution": distribution(positive_deltas),
                        "positive_difference_at_most_one_price_unit": sum(x <= 1 for x in positive_deltas),
                        "positive_difference_exactly_one_price_unit": positive_deltas.count(1.0),
                        "above_base_with_either_promotion_rows": above_promoted,
                        "nonpositive_price_rows": prices_invalid, "decision": "retain all prices unchanged; cause unverified"},
            "orders": {"distribution": distribution(values), "global_iqr_fences": [lower, upper],
                       "global_iqr_outlier_rows": global_count, "lower_fence_outlier_rows": lower_count,
                       "global_outlier_orders": global_orders, "other_orders": total - global_orders,
                       "other_rows": len(values) - global_count, "affected_series": len(within_groups_of_global),
                       "within_series_iqr_outlier_rows": group_count, "global_and_within_series_outlier_rows": overlap,
                       "top10_context": top, "nonpositive_order_rows": nonpositive_orders,
                       "decision": "retain all orders; fences are descriptive flags, not deletion criteria"},
            "invalid_promotion_flag_rows": bad_flags,
            "weeks": {"globally_absent_weeks": sorted(set(range(first, last + 1)) - global_weeks),
                      "observed_week_count": len(global_weeks), "meal_level": meal_summary, "center_meal_level": series_summary,
                      "decision": "absence meaning unknown; no inserted weeks and no zero filling"},
            "retention": {"rows_before": len(values), "rows_after": len(values), "rows_removed": 0,
                          "num_orders_before": total, "num_orders_after": total, "num_orders_removed": 0,
                          "imputed_cells": 0, "price_values_changed": 0, "orders_changed": 0}}


def write_csv(connection, table, path):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(columns(connection, table))
        writer.writerows(connection.execute(f"SELECT * FROM {identifier(table)} ORDER BY rowid"))


def run_skill(root, output, expected_rows):
    """Execute the installed skill, preserving its exact commands and scope."""
    scripts = root / ".agents/skills/exploratory-data-analysis/scripts"
    output.mkdir(exist_ok=True)
    commands = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for name, count in expected_rows.items():
        source = f"data/raw/{name}.csv"
        for program, suffix, arguments in [("capability_manifest.py", "manifest", ["inspect", source]),
                                            ("tabular_profile.py", "profile", [source, "--max-rows", "500000"])]:
            destination = output / f"{name}_{suffix}.json"
            command = [sys.executable, str(scripts / program), *arguments, "--root", str(root),
                       "--output", str(destination), "--force"]
            if suffix == "profile":
                for missing in sorted(MISSING - {""}):
                    command.extend(["--missing-token", missing])
            subprocess.run(command, check=True, cwd=root, env=environment)
            report = json.loads(destination.read_text(encoding="utf-8"))
            if suffix == "profile":
                require(report["analysis"]["rows_scanned"] == count, f"Skill scan incomplete: {name}")
                require(not report["analysis"]["row_limit_reached"], f"Skill scan truncated: {name}")
            commands.append(["python", str((scripts / program).relative_to(root)), *arguments,
                             "--root", ".", "--output", str(destination.relative_to(root)), "--force"] +
                            ([item for missing in sorted(MISSING - {""}) for item in ("--missing-token", missing)] if suffix == "profile" else []))
    destination = output / "train_order_sensitivity.json"
    command = [sys.executable, str(scripts / "distribution_sensitivity.py"), "data/raw/train.csv",
               "--root", str(root), "--max-rows", "500000", "--column", "num_orders", "--output", str(destination), "--force"]
    subprocess.run(command, check=True, cwd=root, env=environment)
    report = json.loads(destination.read_text(encoding="utf-8"))
    require(report["analysis"]["rows_scanned"] == expected_rows["train"] and not report["analysis"]["row_limit_reached"], "Incomplete sensitivity scan")
    commands.append(["python", str((scripts / "distribution_sensitivity.py").relative_to(root)), "data/raw/train.csv", "--root", ".", "--max-rows", "500000", "--column", "num_orders", "--output", str(destination.relative_to(root)), "--force"])
    return {"skill": "exploratory-data-analysis", "commands": commands,
            "scope": "Full CSV row scans; distribution summaries use the skill's bounded numeric sample, not all values.",
            "distribution_diagnostics": report["analysis"]}


def prepare(root=ROOT):
    root = Path(root).resolve()
    raw, output = root / "data/raw", root / "data/processed"
    output.mkdir(parents=True, exist_ok=True)
    require(not output.is_symlink() and output.resolve().is_relative_to(root / "data"), "Unsafe output location")
    inventory = (root / "docs/data_inventory.md").read_text(encoding="utf-8")
    before = {f"{name}.csv": sha256(raw / f"{name}.csv") for name in SCHEMAS}
    require(all(value in inventory for value in before.values()), "Raw hashes differ from Phase 1 inventory")
    report = {"phase": 5, "python": platform.python_version(), "sqlite": sqlite3.sqlite_version,
              "quantile_method": "linear interpolation at (n-1)*p; full-data audit quantiles are exact",
              "raw_sha256_before": before}
    try:
        with sqlite3.connect(":memory:") as connection:
            report["input_audits"] = {}
            for name, expected in SCHEMAS.items():
                load_csv(connection, raw / f"{name}.csv", name, expected)
                report["input_audits"][name] = table_audit(connection, name)
            require(report["input_audits"]["train"]["primary_key_duplicate_rows_beyond_first"] == 0, "Duplicate train IDs")
            require(report["input_audits"]["train"]["logical_duplicate_rows_beyond_first"] == 0, "Duplicate demand logical keys")
            require(all(item["count"] == 0 for item in report["input_audits"]["train"]["missing"].values()), "Missing training values require investigation")
            report["merges"] = [validated_left_join(connection, "train", "meal_info", "meal_id", "train_meal")]
            report["merges"].append(validated_left_join(connection, "train_meal", "fulfilment_center_info", "center_id", "train_prepared"))
            report["prepared_audit"] = table_audit(connection, "train_prepared")
            report["quality"] = demand_audit(connection, "train_prepared", output / "center_meal_week_coverage.csv")
            # Verify every original cell and row order before exporting enrichment.
            original_columns = ', '.join(map(identifier, SCHEMAS["train"]))
            originals = connection.execute(f"SELECT {original_columns} FROM train ORDER BY rowid")
            enriched = connection.execute(f"SELECT {original_columns} FROM train_prepared ORDER BY rowid")
            require(all(a == b for a, b in zip(originals, enriched, strict=True)), "Source cell/order mismatch")
            write_csv(connection, "train_prepared", output / "train_prepared.csv")
            report["skill_use"] = run_skill(root, output / "phase5_skill", {k: v["rows"] for k, v in report["input_audits"].items()})
            report["all_original_train_cells_and_order_preserved"] = True
    finally:
        after = {f"{name}.csv": sha256(raw / f"{name}.csv") for name in SCHEMAS}
        require(before == after, "Raw files changed during execution")
    report["raw_sha256_after"] = after
    report["raw_unchanged"] = True
    report["outputs"] = {name: {"path": f"data/processed/{name}", "sha256": sha256(output / name)}
                         for name in ("train_prepared.csv", "center_meal_week_coverage.csv")}
    (root / "docs/phase5_audit.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"merges": report["merges"], "prepared_columns": report["prepared_audit"]["columns"],
                      "quality": report["quality"], "raw_unchanged": True}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    prepare(parser.parse_args().root)
