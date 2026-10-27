# Phase 13 progress — interactive Streamlit dashboard

Date: 2026-10-27. Status: **Phase 13 fully complete.** Phase 14 has not been started. No commit or push performed.

## Completed checklist

- [x] Read the Phase 13 plan, project rules and client-insight-reporting skill; inspect existing outputs/functions before implementation.
- [x] Build six client-facing sections under `dashboard/` using Streamlit native components.
- [x] Reuse validated Phase 5–10 data/functions and Phase 12 figures; avoid separate analytical definitions, model fitting or promotion-inference reruns.
- [x] Implement historical and forecast controls with clear scope, empty/reset states and immutable source accounting.
- [x] Preserve all six KPI definitions, association caveats, unspecified currency, Center 13 leadership, 14-meal inventory cohort and 32.71% measured RF improvement.
- [x] Add/pin Streamlit, document local run commands and required local inputs.
- [x] Start the actual server; verify HTTP health/page responses and focused AppTest acceptance checks.
- [x] Confirm raw/source/notebook/chart/forecast immutability and stop before Phase 14.

## Sections and client-facing behavior

| Section | Implemented content | Scope / explanation |
| --- | --- | --- |
| Overview | Six cards: **119,557,485 total orders**, **824,534 average weekly demand**, **31.92 billion revenue proxy**, **5.72% mean signed discount**, **8.12% email share**, **10.92% homepage share**; validated weekly chart. | Saved Phase 7 values, rounded only for display. Revenue is checkout price × orders with currency unspecified, not profit. Shares refer to observed records; negative discounts remain included. |
| Demand | Weekly trend, all category contributions/cumulative shares, meal concentration and selectable displayed meal count. | Full scope reuses Phase 6 JSON. Filtered subsets call the existing `src.analysis.demand.analyze_records` implementation, retaining its ranking, 80% crossing and observed-week conventions. No missing weeks are zero-filled. |
| Centers | Center ranking, total-versus-observed-week measure, center table and center-type totals/rates/counts. Center **13** is identified as the full-history leader (**4,296,545 orders**, **29,631 per observed week**). | The ranking follows the current selection, while the portfolio-leader notice is explicitly full-history. Different mix/area/coverage means this is not an efficiency ranking. |
| Promotions & Pricing | Final email/homepage comparison chart, coverage expanders, saved combined-flag pooled means/counts, final signed-discount density chart. | Fixed validated Phase 8 populations. Repeated statements identify associations rather than causal effects and explain unequal channel populations, discount/time/other-flag overlap and the pooled combined-condition distinction. |
| Inventory Risk | Existing volume/CV chart, all **14** priority meals in volume-first order, observed orders/CV/category/cuisine/segment, full 51-meal expandable table. | Fixed Phase 9 portfolio screening, thresholds 1,489,681 orders and CV 0.87774049. Both dimensions matter; no exact safety-stock quantity is claimed. |
| Forecasting | Baseline, Linear Regression and Random Forest MAE table/chart; best-model highlight; **32.71%** lower RF MAE; holdout actual/predicted weekly totals; future trend, selected total, original-order preview and CSV download. | Measured fixed-origin holdout stays at weeks 136–145 / 32,821 rows. The saved winner was refitted through 145. Forecasts 146–155 are conditional on supplied plans; no test target or test accuracy exists. |

No hyperparameters, notebook plumbing or statistical-test implementation details are exposed in the client flow. Help text, captions, source context, chart units and ordinary table labels explain the metrics. Native responsive columns, sidebar navigation, sortable tables and chart hover behavior keep the layout simple; no animation/custom frontend was added.

## Filters and source accounting

Demand and Centers share historical week-range, category, meal, center, center-type, cuisine and promotion-condition controls. Empty multi-selects mean all values. Reset clears the historical selection. Selected versus outside rows and actual order totals are disclosed in the coverage expander; no source deletion occurs. Empty/contradictory selections show an informative state, rather than fabricated zero series.

The forecasting view has separate center, meal and future-week controls; it updates future totals/chart/preview/download. Original identifiers and input order are preserved. Display preview is limited to 100 rows, while the download contains the full selected set. Historical filters do not alter model MAE, promotion comparisons or the fixed 14-meal inventory cohort; scope is stated on those sections.

Actual acceptance example: Beverages / Center 13 / historical weeks 1–10 selects **119 records and 103,601 orders**, leaving **456,429 records / 119,453,884 orders** outside the view. These reconcile to **456,548 / 119,557,485**. A Center 13 + TYPE_A combination correctly produces an empty view (Center 13 is TYPE_B).

Forecast example: Center 13 / meal 2290 / weeks 146–148 returns **three saved forecast rows**, totaling **5,604.570620673541 predicted orders** before display rounding. It retains their original order/values. Forecast metadata mapping keeps **32,573 rows and 32,573 unique IDs**, zero unmatched metadata and zero duplicate expansion. Actual order totals are not applicable to future inputs.

## Reused data and implementation

- Read-only Phase 5 `train_prepared.csv`; no raw preprocessing is rerun.
- Phase 6 `eda_results.json` and its existing `analyze_records` function for filtered descriptive demand/center calculations.
- Phase 7 `kpi_results.json` including exact definitions/provenance; no alternative KPI formulas.
- Phase 8 `promotion_results.json`, including saved comparison populations and combined-state summaries; no Mann–Whitney, correlation or bootstrap execution on dashboard load.
- Phase 9 `inventory_segments.json` and Phase 12 final inventory/promotion/discount/weekly PNGs; no inventory re-segmentation.
- Phase 10 `results.json`, `holdout_predictions.csv` and `test_predictions.csv`; test inputs supply week/center/meal and the validated prepared metadata supplies names/types. Row-aligned prediction assignment and metadata mapping are checked rather than performing an unchecked merge. No estimator is trained.

Read-only `dashboard/data.py` checks missing input files, raw/prepared/CV/chart provenance, historical population totals and forecast identifier/value alignment. `dashboard/app.py` owns native Streamlit rendering and controls. Cached inputs and bounded cached filtered aggregates avoid repeated preparation. Local data are not bundled into code; see [dashboard run instructions](../dashboard/README.md).

## Actual validation

Streamlit installed and pinned: **1.66.1**. Existing dependency versions were retained. `pip check` returned **No broken requirements found**. Syntax compilation of both dashboard modules passed.

Started the actual local server:

```powershell
.venv/Scripts/python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false --server.fileWatcherType none
```

Server reported `Uvicorn server started on 127.0.0.1:8501`. HTTP checks to `/` and `/_stcore/health` returned **200**, with health body `ok`. The server remains available locally at [127.0.0.1:8501](http://127.0.0.1:8501); no external deployment occurred.

Executed focused acceptance validation:

```powershell
.venv/Scripts/python.exe -m docs.validate_phase13
```

**20 focused acceptance checks passed** with zero AppTest exceptions. [Machine-readable results](phase13_validation.json) record all cases: all six pages, exact KPI formatting, model MAEs/winner/improvement, all 14 ordered priority rows/CVs, filtered demand versus independent source grouping, persistence/reset, ranking switch, combined filter operation, empty history/forecast states, fixed-cohort isolation, forecast subset/download value and order checks, coverage reconciliation and HTTP startup.

The AppTest bare-mode runner emits its normal `missing ScriptRunContext` warning for its controlling thread; app executions themselves had no exceptions. This is programmatic Streamlit rendering/interaction validation plus HTTP startup, not a claim of browser pixel/screenshot testing or a deployed-app security audit. No unresolved application error was found.

All four raw SHA-256 values match the pre-Phase-13 snapshot and original Phase 1 values. Existing reusable source, tests, notebooks, final chart files and Phase 10 output files are unchanged. No expensive analysis, estimator fit, full notebook run or complete test-suite rerun occurred. Focused UI/data adapter checks were sufficient for this additive dashboard change.

## Files and scope

Created:

- `dashboard/app.py` — six-section native Streamlit app.
- `dashboard/data.py` — read-only loading, filtering, original-function delegation, alignment and selection accounting.
- `dashboard/README.md` — setup/run, local data requirements, filter scope, caching and limitations.
- `docs/validate_phase13.py` — focused AppTest, data consistency, immutability and HTTP checks.
- `docs/phase13_validation.json` and this progress record.

Updated `requirements.txt` with `streamlit==1.66.1` and README status/run links. The integrity snapshot is ignored under `data/processed/phase13/`. No raw data, original analysis/ML code, notebooks or final chart was modified. Phase 14 was not started. No commit or push.

## Actual skill use and limits

Used the custom [client-insight-reporting skill](../.github/skills/client-insight-reporting/SKILL.md) for clear KPI/forecast explanations, source populations, noncausal marketing language and inventory/purchasing caveats. It did not authorize a new client report or new statistical/model analysis. Recipes, stock, lead times, shelf life, actual future orders and achieved waste/stockout outcomes remain unavailable; the dashboard does not invent them.
