# Phase 7 progress and KPI definitions

Date: 2026-10-27 (Asia/Hebron).

Status: **Phase 7 fully complete.** Phases 1–6 remain complete. This record describes the Phase 7 completion snapshot. Subsequent Phase 8 work is recorded in [Phase 8 progress](phase8_progress.md). Descriptive KPIs only; no inferential or causal claims.

## Completed checklist

- [x] Read Phase 7 requirements and project rules, and inspect the existing notebook/execution workflow.
- [x] Calculate total orders, average weekly demand, revenue proxy, signed discount rates, email/homepage observation shares, and CV for every meal.
- [x] Add reusable KPI functions under src/analysis/ and complete KPI tables to notebooks/analysis.ipynb.
- [x] Preserve negative discounts and all original values; disclose invalid-denominator coverage and unavailable values.
- [x] Add deterministic tests for formulas, grouping, denominator definitions, empty/invalid input and CV edge cases.
- [x] Execute the entire notebook from a fresh kernel and independently validate every KPI.
- [x] Verify raw and Phase 5 analytical input hashes unchanged.
- [x] Update progress documentation; stop before Phase 8; do not commit or push.

## Actual scalar KPI values

Population: **456,548 observed center-meal-week records**, weeks 1–145, from the unchanged hash-verified Phase 5 enriched table. No input records were filtered, merged, altered, or deleted. Pricing-valid subsets below are calculation denominators only, with explicit counts and order coverage.

| KPI | Actual value | Definition / denominator |
| --- | ---: | --- |
| Total orders | 119,557,485 | Sum num_orders over all observed rows |
| Average weekly demand | 824,534.37931034 | Mean of weekly order totals, over 145 observed global weeks; no absent weeks filled |
| Revenue proxy | 31922771040.11 | Sum checkout_price × num_orders, exact decimal arithmetic; price/currency units unspecified |
| Mean signed discount rate | 5.71950027% | Arithmetic mean of valid per-row (base_price−checkout_price)/base_price; unweighted observations |
| Email-promotion share | 8.11524747% | 37,050 / 456,548 observed rows |
| Homepage-feature share | 10.91999089% | 49,855 / 456,548 observed rows |

Revenue is a **proxy**, not profit or verified accounting revenue. It assumes that the recorded checkout price applies to every ordered unit in its row. It does not establish realized collections, returns, delivery charges, tax treatment, or costs. No currency has been invented.

## Discount and invalid-denominator handling

**116,101 negative-rate rows** remain included, corresponding to checkout_price above base_price. No value is altered, floored, capped or clamped. Mean signed discount is 5.71950027%; median 0.14121701%; minimum -72.78975320%; maximum 99.06086957%. The headline is an observation-weighted mean, not an order-weighted discount and not a ratio of aggregate prices.

Actual valid revenue rows: 456,548; invalid revenue rows: 0; excluded revenue orders: 0. Actual valid discount rows: 456,548; invalid discount rows: 0; excluded discount orders: 0. Thus the actual calculations cover all records and orders. The source's negative discount values are valid signed outputs, not invalid denominators.

Reusable logic returns an unavailable discount for nonpositive/invalid/nonfinite base prices or invalid/negative checkout prices. It records invalid row counts and associated orders, rather than deleting rows. If any checkout price is invalid, the complete revenue KPI is unavailable and a separately labeled valid-row subtotal and coverage are supplied. A zero checkout price remains a valid free-price observation. Empty observation denominators yield unavailable averages/shares; invalid binary flags and duplicate observations cause explicit errors.

## Demand volatility per meal

Primary definition: **sample standard deviation (ddof=1) / arithmetic mean** of observed num_orders, grouped by meal across center-meal-week records. Each observed row receives equal weight. This includes both between-center heterogeneity and temporal variation; it is not a pure within-meal weekly time-series CV.

All **51 meals** have defined CV. The smallest is **0.581227636 for meal 1062** (mean 423.165574 orders, sample std 245.955526, n=11,137). The largest is **1.445328164 for meal 1971** (mean 515.998919, sample std 745.787771, n=11,102). These are descriptive endpoints, not a Phase 9 inventory-risk segmentation or a safety-stock recommendation.

The notebook displays the complete table for every meal, with n, observed center/week coverage, mean, sample standard deviation, CV and any unavailable reason. The table is sorted by meal ID. All group observation counts sum to 456,548. Missing center-meal-week records are not inserted or set to zero; retained extreme counts and differing coverage influence CVs. The calculation is descriptive, not an ML feature fitted on future evaluation data.

CV is unavailable when n<2 or mean≤1e−12 orders. The low-mean threshold is an explicit numerical guard, not a claimed business cutoff; no actual meal triggers it. Constant positive observations yield CV=0, whereas zero-mean observations yield unavailable CV. Negative or nonfinite demand is rejected. No target values are transformed or winsorized.

## Reproduction and saved outputs

From the project root using the already configured environment:

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -v
./.venv/Scripts/python.exe docs/run_analysis_notebook.py --phase 7
./.venv/Scripts/python.exe docs/validate_phase7.py
```

No new package was required; the existing pinned notebook environment is unchanged. Core KPI functions use standard-library Decimal/statistics and all original input strings remain intact. The runner now accepts --phase for the validation record and explicitly shuts down its temporary local kernel; it writes the current notebook validation to `docs/phase7_notebook_validation.json`, preserving the earlier Phase 6 snapshot.

Ignored outputs regenerated by the KPI notebook cells:

- `data/processed/phase7/kpi_results.json`: all KPI values, coverage definitions, negative-rate count and complete per-meal table.
- `data/processed/phase7/kpi_summary.csv`: six scalar KPI rows with units and denominators.
- `data/processed/phase7/meal_volatility.csv`: all 51 meal CV rows and coverage.

The full notebook rerun also regenerates existing Phase 6 derived aggregates/skill profiles and retains its five charts. The installed EDA profile runs only as part of the existing Phase 6 notebook cells; no new promotion-analysis skill or statistical procedure was invoked for KPI calculation.

## Actual tests and independent validation

- New KPI suite: **13 tests passed**.
- Full test command: **33 tests passed**, including all 20 prior preparation/EDA tests.
- New cases check decimal-cents multiplication, signed/zero discounts, invalid/nonfinite prices and zero/negative denominators, observed-week aggregation rather than row means, observation-based shares, sample-std CV versus population std, constant/empty/single/zero/near-zero CV cases, invalid demand, correct meal grouping, explicit partial-price coverage, unweighted discount averaging, and duplicate/nonbinary rejection.
- Fresh-kernel full notebook: **11 code cells, 0 error outputs, 5 embedded charts**, nbformat schema validation passed. Actual record: `docs/phase7_notebook_validation.json`.
- Independent validator: `docs/validate_phase7.py` imports no KPI logic. It parses price strings into integer cents, checks exact revenue with SQLite integer products, recomputes weekly totals/average and flag shares, compares discount summaries with independent floating SQL arithmetic, and independently computes all 51 sample variances from sums of squares. Rate/CV comparisons use 1e−12 absolute/relative tolerance; revenue matches to the cent.
- Actual independent result is `status: passed` in `docs/phase7_validation.json`; 6 scalar KPIs and 51 CVs matched and all 116,101 negative discounts were retained.
- Original raw hashes and the Phase 5 enriched-file hash remain unchanged. No rows removed, values clamped, or weeks imputed.

## Files created or updated

Created `src/analysis/kpis.py`, `tests/test_kpis.py`, `docs/validate_phase7.py`, `docs/phase7_notebook_validation.json`, `docs/phase7_validation.json`, and this progress record, plus the three ignored Phase 7 outputs listed above.

Updated `notebooks/analysis.ipynb` with definitions, actual KPI tables, coverage/caveats and the complete meal CV table; `docs/run_analysis_notebook.py` for phase-specific evidence and kernel cleanup; README.md and the Phase 6 progress forward reference. Existing analysis and raw inputs were preserved.

## Completion boundary

No demand comparison between promoted and non-promoted groups, Mann–Whitney, Spearman, p-values, correlation analysis, effect estimates, or Phase 8 implementation was performed. Promotion shares merely count flags. No final client report, forecast, volatility-risk segmentation, dataset edits, commits or pushes were created.
