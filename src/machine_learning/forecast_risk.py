"""Post-hoc forecast error bands from saved holdout predictions; never fits models."""
from pathlib import Path
import argparse
import json

import numpy as np
import pandas as pd

RF = "Random Forest"
LEVELS = {"meal": ["meal_id"], "center": ["center_id"],
          "meal_center": ["meal_id", "center_id"]}


def validate_holdout(frame):
    """Require one finite, non-negative observation per ID and series-week."""
    required = {"id", "week", "meal_id", "center_id", "num_orders", RF}
    if not required.issubset(frame.columns) or frame.empty:
        raise ValueError("Missing holdout columns or empty holdout")
    for column in required:
        values = pd.to_numeric(frame[column], errors="raise").to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"Invalid values: {column}")
        if column != RF and (values != np.floor(values)).any():
            raise ValueError(f"Expected integer values: {column}")
    if set(frame.week) != set(range(136, 146)):
        raise ValueError("Expected the complete Phase 10 holdout window 136–145")
    if frame.id.duplicated().any() or frame.duplicated(["week", "meal_id", "center_id"]).any():
        raise ValueError("Duplicate holdout identifier or series-week")


def assign_bands(mae):
    """Unweighted group-MAE tertiles, with deterministic inclusive boundaries.

    Low <= Q(1/3), Medium <= Q(2/3), High > Q(2/3). Linear interpolation;
    equal values stay together, so tied distributions need not yield equal counts.
    """
    if len(mae) == 0 or not np.isfinite(mae).all() or (mae < 0).any():
        raise ValueError("Band calibration requires finite non-negative group MAEs")
    low, high = np.quantile(mae, [1 / 3, 2 / 3], method="linear")
    labels = np.where(mae <= low, "Low", np.where(mae <= high, "Medium", "High"))
    return labels, {"low_max_mae": float(low), "medium_max_mae": float(high)}


def risk_summary(frame, keys, min_weeks=1):
    """Compute MAE, signed bias and WAPE on observed rows only.

    Positive bias = overforecast. WAPE is undefined when actual demand sums to
    zero. Sparse groups remain in the table as Insufficient coverage, and do not
    enter band calibration. Thresholds describe this holdout, not future bounds.
    """
    if not 1 <= min_weeks <= 10:
        raise ValueError("min_weeks must be between 1 and 10")
    validate_holdout(frame)
    work = frame.copy()
    work["error"] = work[RF] - work.num_orders
    work["absolute_error"] = work.error.abs()
    grouped = work.groupby(keys, sort=True, observed=True).agg(
        observations=("id", "size"), observed_weeks=("week", "nunique"),
        actual_orders=("num_orders", "sum"), predicted_orders=(RF, "sum"),
        absolute_error_sum=("absolute_error", "sum"), mae=("absolute_error", "mean"),
        bias=("error", "mean"),
    ).reset_index()
    grouped["wape_pct"] = 100 * grouped.absolute_error_sum / grouped.actual_orders.replace(0, np.nan)
    grouped["eligible"] = grouped.observed_weeks >= min_weeks
    grouped["risk_band"] = "Insufficient coverage"
    eligible = grouped.eligible
    if not eligible.any():
        raise ValueError("No sufficiently observed groups to calibrate bands")
    labels, thresholds = assign_bands(grouped.loc[eligible, "mae"].to_numpy())
    grouped.loc[eligible, "risk_band"] = labels
    grouped = grouped.sort_values(["mae"] + keys, ascending=[False] + [True] * len(keys)).reset_index(drop=True)
    bands = {}
    total_rows = int(grouped.observations.sum())
    total_error = float(grouped.absolute_error_sum.sum())
    for band in ["Low", "Medium", "High", "Insufficient coverage"]:
        part = grouped[grouped.risk_band == band]
        bands[band] = {"groups": len(part), "observations": int(part.observations.sum()),
                       "actual_orders": int(part.actual_orders.sum()),
                       "row_share_pct": 100 * float(part.observations.sum()) / total_rows,
                       "absolute_error_share_pct": (100 * float(part.absolute_error_sum.sum()) / total_error
                                                    if total_error else None)}
    return grouped, {**thresholds, "min_observed_weeks": min_weeks,
                     "all_groups": len(grouped), "eligible_groups": int(eligible.sum()), "bands": bands}


def plot_risk(tables, metadata, destination):
    """One final figure: the six largest group MAEs at each aggregation level."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    colors = {"Low": "#4D8065", "Medium": "#C68B2B", "High": "#B74343"}
    fig, axes = plt.subplots(1, 3, figsize=(16, 6.5))
    for ax, (level, keys) in zip(axes, LEVELS.items()):
        top = tables[level].loc[lambda x: x.eligible].head(6).iloc[::-1]
        labels = [" / ".join(str(int(row[key])) for key in keys) for _, row in top.iterrows()]
        bars = ax.barh(labels, top.mae, color=[colors[b] for b in top.risk_band])
        for bar, (_, row) in zip(bars, top.iterrows()):
            ax.text(bar.get_width() + top.mae.max() * .02, bar.get_y() + bar.get_height() / 2,
                    f"{row.mae:.1f} (n={int(row.observations):,})", va="center", fontsize=9)
        ax.set_xlim(0, top.mae.max() * 1.65)
        ax.set_xlabel("MAE (orders per meal-center-week)")
        ax.set_title({"meal": "Meals", "center": "Centers", "meal_center": "Meal / center pairs (8+ weeks)"}[level])
        ax.spines[["right", "top"]].set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(axis="x", alpha=.18)
        m = metadata[level]
        ax.text(0, -.22, f"MAE cutoffs: {m['low_max_mae']:.2f} / {m['medium_max_mae']:.2f}",
                transform=ax.transAxes, fontsize=9)
    meal_leader = tables["meal"].loc[lambda x: x.eligible].iloc[0]
    center_leader = tables["center"].loc[lambda x: x.eligible].iloc[0]
    pair_leader = tables["meal_center"].loc[lambda x: x.eligible].iloc[0]
    fig.suptitle(f"Meal {int(meal_leader.meal_id)} and Center {int(center_leader.center_id)} have the highest aggregate forecast errors", fontsize=17, y=.97)
    fig.text(.5, .88, f"Largest eligible pair: meal {int(pair_leader.meal_id)} / center {int(pair_leader.center_id)} — "
             f"MAE {pair_leader.mae:.1f} orders over {int(pair_leader.observations)} observations",
             ha="center", fontsize=11)
    fig.legend(handles=[Patch(color=c, label=b) for b, c in colors.items()], loc="lower center",
               bbox_to_anchor=(.5, .09), ncol=3, frameon=False)
    fig.text(.5, .025, "Source: saved Random Forest holdout predictions, weeks 136–145; no retraining.\n"
             "Bands use separate group-MAE tertiles at each level. Top six shown; higher volume can raise absolute error.\n"
             "Historical review priorities, not prediction intervals or guaranteed future risk; missing weeks remain absent.",
             ha="center", fontsize=9)
    fig.subplots_adjust(left=.055, right=.99, bottom=.29, top=.77, wspace=.43)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=180, facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root
    frame = pd.read_csv(root / "data/processed/phase10/holdout_predictions.csv")
    prior = json.loads((root / "data/processed/phase10/results.json").read_text())
    validate_holdout(frame)
    overall = float((frame[RF] - frame.num_orders).abs().mean())
    if len(frame) != prior["holdout_rows"] or int(frame.num_orders.sum()) != prior["holdout_orders"]:
        raise ValueError("Holdout row/order total differs from Phase 10")
    if not np.isclose(overall, prior["metrics"][RF]["mae"], rtol=1e-12, atol=0):
        raise ValueError("Saved Random Forest MAE differs from Phase 10")
    output = root / "data/processed/phase19"
    output.mkdir(parents=True, exist_ok=True)
    tables, metadata = {}, {}
    for level, keys in LEVELS.items():
        tables[level], metadata[level] = risk_summary(frame, keys, 8 if level == "meal_center" else 1)
        tables[level].to_csv(output / f"{level}_risk.csv", index=False)
    result = {"source": "data/processed/phase10/holdout_predictions.csv", "model": RF,
              "holdout_weeks": [136, 145], "observations": len(frame),
              "actual_orders": int(frame.num_orders.sum()), "mae": overall,
              "method": "Separate unweighted group-MAE tertiles; linear interpolation; Low <= Q1/3, Medium <= Q2/3, High > Q2/3",
              "levels": metadata}
    (output / "risk_results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    plot_risk(tables, metadata, root / "reports/figures/forecast_risk_bands.png")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
