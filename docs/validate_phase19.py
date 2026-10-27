"""Independent CSV/scalar validation of Phase 19; no model imports or training."""
import csv
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def near(a, b):
    assert math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-9), (a, b)


def quantile(values, probability):
    ordered = sorted(values)
    location = (len(ordered) - 1) * probability
    low = math.floor(location)
    fraction = location - low
    return ordered[low] + fraction * (ordered[min(low + 1, len(ordered) - 1)] - ordered[low])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-integrity", action="store_true",
                        help="Create the local before-snapshot once, before generating Phase 19 outputs")
    args = parser.parse_args()
    output = ROOT / "data/processed/phase19"
    if args.capture_integrity:
        output.mkdir(parents=True, exist_ok=True)
        paths = (list((ROOT / "data/raw").glob("*.csv")) +
                 list((ROOT / "data/processed/phase10").glob("*")) +
                 [ROOT / "notebooks/machine_learning.ipynb", ROOT / "requirements.txt",
                  ROOT / "src/machine_learning/forecast.py"])
        snapshot = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                    for path in paths if path.is_file()}
        inventory = (ROOT / "docs/data_inventory.md").read_text(encoding="utf-8")
        raw_hashes = [value for path, value in snapshot.items() if path.startswith("data/raw/")]
        assert len(raw_hashes) == 4 and all(value in inventory for value in raw_hashes)
        with (output / "before.json").open("x", encoding="utf-8") as handle:
            json.dump(snapshot, handle, indent=2)
        print(f"Created pre-execution snapshot for {len(snapshot)} files; existing snapshots are never overwritten")
        return
    source = rows(ROOT / "data/processed/phase10/holdout_predictions.csv")
    saved = json.loads((output / "risk_results.json").read_text())
    phase10 = json.loads((ROOT / "data/processed/phase10/results.json").read_text())
    assert len(source) == saved["observations"] == phase10["holdout_rows"] == 32821
    assert {int(row["week"]) for row in source} == set(range(136, 146))
    assert len({row["id"] for row in source}) == len(source)
    assert len({(row["meal_id"], row["center_id"], row["week"]) for row in source}) == len(source)
    total_actual = sum(int(row["num_orders"]) for row in source)
    assert total_actual == saved["actual_orders"] == phase10["holdout_orders"]
    errors = [abs(float(row["Random Forest"]) - int(row["num_orders"])) for row in source]
    near(math.fsum(errors) / len(source), saved["mae"])
    near(saved["mae"], phase10["metrics"]["Random Forest"]["mae"])
    checks = {}
    for level, keys in {"meal": ["meal_id"], "center": ["center_id"], "meal_center": ["meal_id", "center_id"]}.items():
        grouped = defaultdict(list)
        for row in source:
            grouped[tuple(row[key] for key in keys)].append(row)
        table = rows(output / f"{level}_risk.csv")
        assert len(table) == len(grouped)
        assert len({tuple(row[key] for key in keys) for row in table}) == len(table)
        independent = {}
        for key, part in grouped.items():
            n = len(part)
            actual = sum(int(row["num_orders"]) for row in part)
            prediction = math.fsum(float(row["Random Forest"]) for row in part)
            absolute = math.fsum(abs(float(row["Random Forest"]) - int(row["num_orders"])) for row in part)
            bias = math.fsum(float(row["Random Forest"]) - int(row["num_orders"]) for row in part) / n
            independent[key] = {"observations": n, "observed_weeks": len({row["week"] for row in part}),
                                "actual_orders": actual, "predicted_orders": prediction,
                                "absolute_error_sum": absolute, "mae": absolute / n, "bias": bias,
                                "wape_pct": 100 * absolute / actual if actual else None}
        minimum = 8 if level == "meal_center" else 1
        eligible = [row["mae"] for row in independent.values() if row["observed_weeks"] >= minimum]
        low, high = quantile(eligible, 1 / 3), quantile(eligible, 2 / 3)
        meta = saved["levels"][level]
        near(low, meta["low_max_mae"])
        near(high, meta["medium_max_mae"])
        band_rows = defaultdict(list)
        for row in table:
            reference = independent[tuple(row[key] for key in keys)]
            for field, value in reference.items():
                if value is None:
                    assert row[field] == ""
                else:
                    near(row[field], value)
            eligible_flag = reference["observed_weeks"] >= minimum
            assert row["eligible"] == str(eligible_flag)
            expected = ("Insufficient coverage" if not eligible_flag else
                        "Low" if reference["mae"] <= low else
                        "Medium" if reference["mae"] <= high else "High")
            assert row["risk_band"] == expected
            band_rows[expected].append(reference)
        assert sum(int(row["observations"]) for row in table) == len(source)
        assert sum(int(row["actual_orders"]) for row in table) == total_actual
        near(math.fsum(float(row["absolute_error_sum"]) for row in table), math.fsum(errors))
        for band, meta_band in meta["bands"].items():
            part = band_rows[band]
            assert len(part) == meta_band["groups"]
            assert sum(row["observations"] for row in part) == meta_band["observations"]
            assert sum(row["actual_orders"] for row in part) == meta_band["actual_orders"]
            near(100 * sum(row["observations"] for row in part) / len(source), meta_band["row_share_pct"])
            near(100 * math.fsum(row["absolute_error_sum"] for row in part) / math.fsum(errors),
                 meta_band["absolute_error_share_pct"])
        assert all(float(table[i]["mae"]) >= float(table[i + 1]["mae"]) for i in range(len(table) - 1))
        checks[level] = {"groups_verified": len(table), "eligible_groups": len(eligible),
                         "rows_conserved": len(source), "orders_conserved": total_actual,
                         "weighted_mae": math.fsum(row["absolute_error_sum"] for row in independent.values()) / len(source),
                         "all_metrics_and_labels_match": True}
    before = json.loads((output / "before.json").read_text())
    assert all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected for path, expected in before.items())
    raw = {path: value for path, value in before.items() if path.startswith("data/raw/")}
    inventory = (ROOT / "docs/data_inventory.md").read_text(encoding="utf-8")
    assert len(raw) == 4 and all(value in inventory for value in raw.values())
    report = (ROOT / "reports/technical_report.md").read_text(encoding="utf-8").split("## نطاقات مخاطر التنبؤ — المرحلة 19")[-1]
    meal_rows = rows(output / "meal_risk.csv")[:6]
    center_rows = rows(output / "center_risk.csv")[:6]
    pair_rows = [row for row in rows(output / "meal_center_risk.csv") if row["eligible"] == "True"][:6]
    for row in meal_rows:
        expected = f"| {int(row['observations'])} | {float(row['mae']):.2f} | {float(row['bias']):+.2f} | High |"
        assert expected in report
    for row in center_rows:
        expected = f"| {row['center_id']} | {int(row['observations'])} | {float(row['mae']):.2f} | {float(row['bias']):+.2f} | High |"
        assert expected in report
    for row in pair_rows:
        expected = (f"| {row['meal_id']} / {row['center_id']} | {row['observations']} / {row['observed_weeks']} | "
                    f"{int(row['actual_orders']):,} | {float(row['mae']):.2f} | {float(row['bias']):+.2f} | "
                    f"{float(row['wape_pct']):.2f}% | High |")
        assert expected in report
    for meal, center, sign in [(2707, 13, -1), (2631, 23, 1)]:
        part = [row for row in source if int(row['meal_id']) == meal and int(row['center_id']) == center]
        assert len(part) == 10 and all(sign * (float(row['Random Forest']) - int(row['num_orders'])) > 0 for row in part)
    from PIL import Image
    with Image.open(ROOT / "reports/figures/forecast_risk_bands.png") as figure:
        figure.verify()
    result = {"status": "pass", "method": "Independent csv.DictReader / math.fsum / scalar quantiles; no risk-module import",
              "source_rows": len(source), "actual_orders": total_actual, "levels": checks,
              "unchanged_files": len(before), "raw_files_unchanged_and_match_inventory": 4,
              "phase10_outputs_unchanged": True, "figure_png_valid": True,
              "technical_report_top18_rows_match": True, "directional_pair_claims_verified": True,
              "scope": "Phase 19 focused checks only; no full suite, notebooks, dashboard or model execution"}
    (ROOT / "docs/phase19_validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
