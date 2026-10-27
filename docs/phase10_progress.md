# Phase 10 — forecasting progress and actual results

Date: 2026-10-27. Status: **Phase 10 fully complete.** Phase 11 has not been started. No commit or push performed.

## Completed requirements

- [x] Read the plan, AGENTS.md, project rules, installed scikit-learn skill and pipeline/supervised references.
- [x] Create an executable ML notebook and reusable forecasting code.
- [x] Final 10 weeks form the chronological holdout; no random splitting/shuffling.
- [x] Compare previous-week baseline, Linear Regression and seeded Random Forest using MAE on identical rows.
- [x] Restrict features to origin-available inputs; train-only preprocessing; recursive forecasting without holdout actuals.
- [x] Select by holdout MAE, refit using full observed training history and predict test in original order.
- [x] Validate finite non-negative forecasts, leakage controls, source immutability, joins, and independently recompute results.
- [x] Run deterministic tests and the notebook top to bottom in a fresh kernel.
- [x] Record actual skill use, interpretation, business use and limitations; stop before Phase 11.

## Design and row accounting

Target is `num_orders` per recorded center-meal-week. Fixed origin at the end of week 135; forecast all ten holdout weeks 136–145 recursively. Initial fit: **423,727 rows**, **112,097,205 orders**, weeks 1–135. Holdout: **32,821 rows**, **7,460,280 orders**. Together **456,548 rows** and **119,557,485 orders**: zero exclusions, deletions, or inserted zero-demand observations. The final-ten-week split conserves all rows and targets. No filtering by availability of lag is applied.

At the origin, assume that the meal/center metadata and published prices and promotion plans for the next ten weeks are known. Forecasts are conditional on these plans, not inferred from actual demand. Test rows represent the provided assortment, not all possible center-meal combinations. A changed plan requires a forecast rerun. No claim of calendar seasonality is made from week numbers.

This fixed-origin design deliberately matches the ten-week unlabeled test horizon. Earlier holdout actuals are never ingested, including when making the later holdout forecasts. Each model feeds its own earlier predictions into subsequent weeks; the baseline does likewise. Baseline formula is exact prior numbered week for the same center/meal. If absent, use only the initial fitting-window global target median **136.0**. This is an explicit baseline fallback, not a fabricated observation. Gaps do not use a distant last observation or become zero.

## Features and preprocessing

Categorical labels: center_id, meal_id, category, cuisine, center_type, city_code, region_code. Numeric: week (trend index), op_area, checkout_price, base_price, discount_rate, emailer_for_promotion, homepage_featured, exact prior-week demand, mean of available observations/predictions in the preceding four numbered weeks, and the count of those available records. The rolling mean uses 1–4 prior available values; when none exist it stays missing. It never includes the current week or other series.

No `id`, current target, full-period demand aggregates, Phase 7 CV, or holdout targets are features. The fitting table's lag features use strictly earlier actuals; future batches use strictly earlier recursive predictions. Missing numeric values are filled with fitting-window medians, with missing indicators, then standardized. Categories are one-hot encoded with unknown-category handling. The entire preprocessing is fitted inside each model pipeline. After selection, a fresh pipeline is fitted on weeks 1–145.

Signed discount is `(base_price - checkout_price) / base_price`. Nonpositive/invalid denominators produce a missing feature for train-only imputation. All **116,101** training and **8,937** test checkout-above-base rows remain unchanged, with negative discounts retained. These are not clamped. Negative model predictions alone are clipped to zero consistently for evaluation and deployment; actual clipping counts appear below. Predictions remain floating point, not artificially rounded to integer orders.

Random Forest was fixed before observing holdout results: {'n_estimators': 40, 'max_depth': 14, 'min_samples_leaf': 5, 'max_features': 0.5, 'max_samples': 0.35, 'random_state': 42, 'n_jobs': 1}. No hyperparameter search or holdout-driven retuning was performed. Internal forest bootstrapping belongs to model fitting; the fitting/holdout partition is exclusively chronological. Linear Regression is ordinary least squares. Forest uses one worker to avoid Windows multiprocessing-pipe permissions and to keep execution reproducible.

## Actual holdout comparison

MAE is orders per observed center-meal-week. Improvement = `100 × (baseline MAE − model MAE) / baseline MAE`; negative values mean deterioration. All rows are scored, including fallback/imputed cases.

| Model | MAE | Improvement vs baseline | Missing prior-week inputs | Negative predictions clipped |
| --- | ---: | ---: | ---: | ---: |
| Previous-week baseline | 119.61305262 | 0.00000% | 1,576 | 0 |
| Linear Regression | 115.68906833 | 3.28057% | 1,576 | 5,947 |
| Random Forest | 80.48260830 | 32.71419% | 1,576 | 0 |

Winner: **Random Forest**, chosen by the lowest holdout MAE. Training accuracy was not used for selection. One final holdout comparison is not an independent post-selection accuracy guarantee.

| Holdout week | Rows | Baseline MAE | Linear Regression MAE | Random Forest MAE |
| --- | ---: | ---: | ---: | ---: |
| 136 | 3,273 | 85.45738 | 102.14226 | 67.58527 |
| 137 | 3,283 | 108.99391 | 111.61924 | 69.93660 |
| 138 | 3,278 | 125.32581 | 111.03398 | 74.42947 |
| 139 | 3,279 | 118.90607 | 110.86303 | 75.60514 |
| 140 | 3,332 | 121.32353 | 126.27814 | 84.08456 |
| 141 | 3,263 | 128.76065 | 116.41312 | 91.03772 |
| 142 | 3,238 | 123.36535 | 115.04026 | 82.93133 |
| 143 | 3,305 | 123.31074 | 119.38234 | 80.04324 |
| 144 | 3,302 | 133.14264 | 120.00159 | 94.66510 |
| 145 | 3,268 | 127.46267 | 123.88772 | 84.43625 |

The selected model's largest weekly MAE is **94.66510 orders** in week **144**. Even the winning forecast retains material errors; review exceptions before purchasing.

## Interpretation

The notebook records the 20 largest absolute Linear Regression coefficients and the top 20 Random Forest impurity importances from the initial fit. Numeric coefficients refer to standardized predictors; one-hot coefficients depend on correlated/redundant category encoding. Forest importances are descriptive, favor variables offering more splits and share credit among correlated variables. They are not causal promotion effects, and were not used to retune the model. Leading selected-model features (if an ML model won):

- numeric__lag_1: 0.336130
- numeric__prior_4_mean: 0.275768
- numeric__emailer_for_promotion: 0.089568
- numeric__discount_rate: 0.065434
- numeric__checkout_price: 0.054019
- numeric__homepage_featured: 0.030450
- numeric__base_price: 0.020932
- numeric__week: 0.018748

## Final refit and test forecasts

After selection, refit Random Forest on all 456,548 observed rows, weeks 1–145, and recursively forecast 146–155. When the baseline wins it requires no estimator fit: update history and fallback using the full training history. The independent validator confirms original IDs and row order exactly. Output: `data/processed/phase10/test_predictions.csv` with `id,num_orders`, **32,573 rows**. Minimum **17.521429**, maximum **4161.864651**, mean **255.521987**, predicted total **8323117.673956** orders. Negative forecasts clipped: **0**. Missing prior-week inputs: **1649**. Every output is finite and non-negative. Test has no target: there is no measured test MAE.

Both test-to-lookup joins use many-to-one validation: 32,573 rows before and after each; zero unmatched keys and zero duplicate expansion, unique IDs and row order preserved. Target totals are not applicable to test. Detailed join records, row/order totals, versions, feature-missingness counts, metrics and configuration are in ignored `data/processed/phase10/results.json`.

## Purchasing use and limits

Use center-meal forecasts as a starting point for weekly demand review and ingredient planning, conditional on the planned prices/promotions. Review high-volume errors and changed marketing plans before purchases. Success KPIs: prospectively measured weekly MAE and signed bias, with stockout/waste rates once operational outcomes become available. No stockout reduction, waste reduction or causal benefit has been measured here.

Recipes, inventory on hand, lead times, shelf life, service targets, real currency/area units and calendar dates are unavailable. These forecasts cannot establish exact purchasing or safety-stock quantities. Recursive error accumulates; fitting uses actual histories while future features use predicted histories. A single ten-week period may not represent future conditions. Missing rows can reflect unknown assortment/availability, not zero demand. Unseen categories are handled without runtime errors but may be poorly predicted. Test price extremes can exceed training ranges. Clipping does not quantify uncertainty. No prediction intervals, causal marketing claims, or Phase 11 enhancement was implemented.

## Actual validation and reproducibility

Executed:

```powershell
.venv/Scripts/python.exe -m pip install scikit-learn==1.9.1 pandas==3.0.3
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe -m pip check
.venv/Scripts/python.exe docs/run_ml_notebook.py
.venv/Scripts/python.exe -m docs.validate_phase10
```

- **66 tests passed**, including **15 forecasting tests**: chronological split, exact lags, prior-only rolling features, no cross-series mixing, missing-week handling, current/future-label invariance, recursive target isolation, multi-series alignment, train-only imputation, unknown categories, invalid denominators, MAE, non-negative/finite validation and seeded forest determinism.
- Fresh notebook: **6 code cells**, **0 errors**, valid nbformat. It actually refits/evaluates both models, selects/refits the winner, writes test forecasts and invokes independent validation.
- Independent validation: SQLite source counts/totals; scalar absolute-error MAE and percentage arithmetic for every model; baseline recursion independently reconstructed from origin history; winner verified; all test IDs/order and forecast values validated. Source-scale current/future target poisoning leaves prediction-week features identical.
- All four raw SHA-256 hashes and the Phase 5 prepared-data hash remain unchanged. Four temporary-Git ignore probes confirm raw inputs and Phase 10 predictions/results are under `/data/`. No repository was initialized in the workspace and no data was committed.
- `pip check`: no broken requirements. Runtime versions: {'python': '3.11.4', 'numpy': '2.4.6', 'pandas': '3.0.3', 'sklearn': '1.9.1'}.

The first offline dependency installation failed to resolve packages; network-enabled installation succeeded. The initial parallel-forest synthetic test hit a Windows permission error; single-worker execution resolved it and the full suite passed afterward. Windows Jupyter execution uses the same approved kernel-ACL allowance as earlier phases; successful fresh execution is recorded in [notebook validation](phase10_notebook_validation.json). An initial 80-tree, depth-18 full-sample forest run was stopped for runtime reasons before any model scores were inspected or reported; the final 40-tree, depth-14 bootstrap-subsampled configuration was fixed before the evaluated comparison. No result from the stopped run is reported. These resolved environment/runtime issues did not change the holdout or model comparison population.

## Skill use and artifacts

Used the installed [scikit-learn skill](../.agents/skills/scikit-learn/SKILL.md), pipeline/composition reference and supervised-learning reference for regression, pipeline-contained preprocessing, seeded forest, MAE, unknown-category handling and training-only transformations. Adapted generic examples to the project's chronological fixed-origin protocol. Existing upstream attribution is retained in [Find Skills](find_skills.md#upstream-attribution); see its Phase 10 actual-use entry. Installed upstream skill files remain unchanged.

Created `src/machine_learning/forecast.py`, `tests/test_forecasting.py`, `notebooks/machine_learning.ipynb`, `docs/create_phase10_notebook.py`, `docs/run_ml_notebook.py`, `docs/validate_phase10.py`, `docs/write_phase10_progress.py`, this progress record and [independent validation](phase10_validation.json). Updated requirements, README, skill-use record and Phase 9 snapshot linkage. Results, holdout predictions and test forecasts are under ignored `data/processed/phase10/`. The analysis notebook and raw datasets were not modified. Phase 11 remains unstarted.
