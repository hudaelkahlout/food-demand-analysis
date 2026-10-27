# Food demand dashboard

Run commands from the repository root (`food-demand-analysis`). Python 3.11+ is required. The dashboard uses the project's pinned environment; it does not train models or rerun promotion inference.

## Start locally

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open [the local dashboard](http://127.0.0.1:8501). Stop it with Ctrl+C in the terminal. The bind address keeps this local; deployment and publishing are outside Phase 13.

For headless startup or focused validation:

```powershell
.venv/Scripts/python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false --server.fileWatcherType none
```

In a second terminal, with that server running:

```powershell
.venv/Scripts/python.exe -m docs.validate_phase13
```

This uses Streamlit's AppTest and HTTP health/page checks, not the complete analytical test suite. No model fitting occurs. The local validation command records a pre-run integrity snapshot under ignored `data/processed/phase13/` if one is absent, verifies raw files against the original baseline, and checks before/after immutability. The dashboard itself does not depend on the Phase 13 snapshot or validation script.

## Required existing inputs

Keep original files in ignored `data/raw/`:

- `train.csv`, `test.csv`, `meal_info.csv`, `fulfilment_center_info.csv` (matching the Phase 1 hashes).

Reuse these ignored, previously generated files:

- `data/processed/train_prepared.csv` — validated Phase 5 enriched observations.
- `data/processed/phase6/eda_results.json` — demand, concentration, center and center-type results.
- `data/processed/phase7/kpi_results.json` — exact KPI definitions/results and CV provenance.
- `data/processed/phase8/promotion_results.json` — fixed observational promotion/pricing populations and combined-state summaries.
- `data/processed/phase9/inventory_segments.json` — all meal CVs, volume cutoffs, assignments and 14-meal priority order.
- `data/processed/phase10/results.json`, `holdout_predictions.csv`, `test_predictions.csv` — measured model comparison and saved forecasts.

Also retain the checked-in project documentation/provenance (`docs/phase5_audit.json`, `docs/phase12_validation.json`) and final PNGs under `reports/figures/`. The read-only loader checks raw/prepared/CV/chart provenance and forecast alignment. If inputs are missing or inconsistent, it shows a visible error instead of silently launching expensive notebooks or substituting synthetic data. Data files remain ignored and must be supplied locally; installing dependencies alone does not create them.

## Navigation and scope

- **Overview:** six full-history KPI cards. Revenue is explicitly a proxy with unspecified currency; promotion shares count observed records, not orders.
- **Demand:** historical filters update weekly demand, category concentration and meal concentration using the existing Phase 6 `analyze_records` function. Full scope reuses its saved output directly.
- **Centers:** the same historical filters; switch between total demand and average orders per observed week. Center-type totals and observed-center-week rates are separate. Center 13 remains identified as the full-history volume leader even when a filtered ranking changes.
- **Promotions & Pricing:** reuse the final comparison/density PNGs and saved combined-condition summaries. Populations and means stay fixed to the validated Phase 8 analysis; historical filters do not silently redefine statistical results. These are associations, not causal effects.
- **Inventory Risk:** retain the final volume/CV figure and all 14 priority meals with volume, CV, category/cuisine and segment. Portfolio medians and priority ranking stay fixed, independent of historical filters. The full 51-meal table is expandable.
- **Forecasting:** model MAEs and 32.71% Random Forest improvement stay fixed to the chronological holdout. Weekly actual-versus-predicted holdout totals cover the same rows. Separate center, meal and forecast-week controls update future totals, the original-order preview and CSV download. No test MAE is claimed.

Historical filters: week range, category, meal ID, center ID, center type, cuisine and promotion condition. Empty multi-selects mean all values. The reset button restores the full historical selection; selected and outside-selection rows/orders are disclosed. Contradictory choices show an empty state. Forecast filters have their own scope and preserve original prediction identifiers/order in downloads. IDs are coded labels; meal names were not supplied.

## Operation and limitations

Streamlit native navigation, cards, charts, tables, tooltips, expanders and downloads provide the UI; no custom animation or separate frontend is required. Read-only data and selected aggregates are cached. Restart after any authorized change to validated inputs so caches are cleared; changing raw files without revalidation is unsupported.

Missing observations remain absent. Filtered trend lines connect observed weeks, without inventing zero demand or calendar seasons. Promotion and discount results are observational. CV includes variation between centers and weeks. Forecasts are conditional on supplied pricing/promotion plans, and recursive error can accumulate. Recipes, stock, lead times and shelf life are unavailable, so no exact purchasing or safety-stock quantity is proposed.

See [Phase 13 progress](../docs/phase13_progress.md) and [actual focused validation](../docs/phase13_validation.json).
