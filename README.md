# Food Demand Analysis

A project analyzing weekly demand for a meal-delivery company to support purchasing and inventory planning by meal and fulfilment center. It addresses the balance between excess stock that may go to waste and shortages that prevent orders from being fulfilled, while accounting for changing prices and promotions.

[Client report — Arabic](reports/client_report.md) · [Technical report — Arabic](reports/technical_report.md) · [AI usage documentation — Arabic](docs/ai_usage.md) · [Final figures](reports/figures/) · [Dashboard instructions](dashboard/README.md)

## Key Validated Findings

| Finding | Business relevance and limits |
| --- | --- |
| **119,557,485 orders**, averaging approximately **824,534 per week**. | Requirements vary across weeks; the overall average alone is insufficient for purchasing decisions. |
| Five categories account for **81.40%** of demand; the top **22** meals account for **81.18%**. | Concentration helps prioritize purchasing and planning attention. |
| Email promotion is associated with a **190.21%** demand difference, and homepage featuring with **158.87%**, within comparable meal-center groups. | These are observational associations with discount overlap. The comparison populations differ, and the percentages do not establish isolated causal effects. |
| **14 meals** combine high volume and high variability, accounting for **45.93%** of demand. | They warrant closer review, without implying an exact safety-stock quantity. |
| Random Forest reduced mean absolute forecast error by **32.71%** compared with the previous-week baseline. | This is a historical holdout result, not a guarantee of future accuracy. |

These figures come from previously validated outputs. The [technical report](reports/technical_report.md) explains definitions, comparison populations, limitations, and validation evidence.

## Analysis Questions

1. How does demand change from week to week?
2. Where is demand concentrated across categories and meals?
3. How do fulfilment centers and center types compare?
4. How are email promotion and homepage featuring associated with demand?
5. How does discount relate to demand, and how does it overlap with promotion?
6. Which meals combine high volume and high variability and deserve inventory-planning attention?
7. Can forecasting outperform the previous week's demand as a planning baseline?

## Data

| File in `data/raw/` | Rows | Purpose |
| --- | ---: | --- |
| `train.csv` | 456,548 | Recorded demand for weeks 1–145, including the target `num_orders`. |
| `test.csv` | 32,573 | Inputs for weeks 146–155 without observed demand; used to generate forecasts. |
| `meal_info.csv` | 51 | Meal ID, category, and cuisine; no individual meal names. |
| `fulfilment_center_info.csv` | 77 | Center ID, attributes, and coded location information. |

Demand records link to reference data through `meal_id` and `center_id`. The [data inventory](docs/data_inventory.md) documents columns, keys, and file hashes.

**Raw data is intentionally excluded from Git and GitHub publication.** `.gitignore` excludes the entire `data/` directory, including derived data and predictions. Supply the original files locally without changing them; downloading the project and installing dependencies does not provide the datasets. Ignore rules do not untrack files already tracked by Git.

## Demand Forecasting

Models train on weeks **1–135** and are evaluated chronologically on **136–145**, without random splitting. All ten weeks are forecast recursively from a fixed origin: held-out actual demand is never used to construct features, and earlier predictions supply history as the forecast advances.

The primary metric is mean absolute error (`MAE`): the average magnitude of the difference between actual and predicted orders per meal-center-week. Lower is better.

| Method | MAE, orders | Improvement over baseline |
| --- | ---: | ---: |
| Previous-week demand | 119.613 | Baseline |
| Linear Regression | 115.689 | 3.28% |
| Random Forest | **80.483** | **32.71%** |

Random Forest was selected for the lowest holdout error, then refitted on the available training history to generate **32,573** forecasts while preserving identifiers and row order. Predictions are saved in `data/processed/phase10/test_predictions.csv`. Test inputs have no observed targets, so future prediction accuracy cannot be measured from them.

### Forecast Risk Bands — Phase 19

Post-hoc review of the **32,821 saved holdout predictions** identifies where planners should review forecasts more closely. Meal **1727** has the highest meal-level MAE (**224.66 orders**), Center **13** the highest center-level MAE (**161.81**), and meal **2707 / Center 13** the highest sufficiently observed pair MAE (**925.24**, ten observations). The latter was underforecast in all ten observed weeks. These are errors per meal-center-week, rather than errors in weekly totals.

Low / Medium / High bands use separate group-MAE tertiles for meals, centers, and pairs. The two cutoffs are **42.43 / 78.57**, **65.80 / 80.78**, and **38.82 / 82.18 orders**, respectively. Classification uses full precision. Pairs require at least **8 of 10** observed weeks: **3,136 pairs** qualify; **411** remain explicitly unclassified. High-risk meals account for **66.76%** of absolute error across **39.72%** of holdout rows.

Review upcoming price/promotion plans, availability, and stock before approving quantities for these groups; monitor new weekly MAE and signed bias before making systematic overrides. Bands are relative historical review priorities, **not prediction intervals or future guarantees**. Absolute error also reflects demand volume, so the saved tables include bias and WAPE for context. See the [final chart](reports/figures/forecast_risk_bands.png), [Arabic technical findings](reports/technical_report.md#نطاقات-مخاطر-التنبؤ--المرحلة-19), and [method and validation record](docs/phase19_progress.md).

With the existing Phase 10 holdout files available, reproduce only this enhancement:

```powershell
.venv/Scripts/python.exe -m src.machine_learning.forecast_risk
.venv/Scripts/python.exe -m unittest discover -s tests -p test_forecast_risk.py -v
.venv/Scripts/python.exe docs/validate_phase19.py
```

No model training is performed. The independent validator also requires the local pre-execution integrity snapshot `data/processed/phase19/before.json`, whose creation is documented in the progress record.

## Interactive Dashboard

The local `Streamlit` dashboard provides Overview, Demand, Centers, Promotions & Pricing, Inventory Risk, and Forecasting sections. It includes KPI cards; week-range, meal, center, center-type, category, cuisine, and promotion filters; forecast exploration; and a selected-forecast `CSV` download.

Demand and center filters update aggregates using the same validated functions. Statistical comparisons, inventory priorities, and model accuracy retain their validated population scopes. The dashboard does not retrain models. See the [dashboard guide and input requirements](dashboard/README.md).

## Project Structure

| Path | Contents |
| --- | --- |
| `data/raw/` and `data/processed/` | Original sources and local derived data; excluded from version control. |
| `src/data_processing/` | Data preparation, merge validation, and quality checks. |
| `src/analysis/` and `src/statistics/` | Demand, KPIs, inventory segmentation, and statistical comparisons. |
| `src/machine_learning/` | Time-aware features, forecasting, and evaluation. |
| `notebooks/` | Executable analysis and forecasting notebooks. |
| `tests/` | Formula, integrity, analysis, and forecasting tests. |
| `dashboard/` | Streamlit application and run instructions. |
| `reports/` and `reports/figures/` | Arabic reports and final visualizations. |
| `docs/` | Inventory, decisions, evidence, and progress records. |
| `.agents/skills/` and `.github/skills/` | External and custom skills; project instructions are in `AGENTS.md` and `.github/instructions/`. |

## Setup and Run Instructions

Requirements: `Python 3.11+` and the original datasets available locally. Run the following commands from the project root in Windows `PowerShell`. On Linux or macOS, replace `.venv/Scripts/python.exe` with `.venv/bin/python`.

### Create the Environment

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

### Prepare Data and Run the Analysis

Place all four original source files in `data/raw/`, then run:

```powershell
.venv/Scripts/python.exe -m src.data_processing.prepare
.venv/Scripts/python.exe docs/run_analysis_notebook.py --phase 9
```

The second command executes the complete current `notebooks/analysis.ipynb`, including KPIs, promotion comparisons, and inventory segmentation. It saves derived outputs without changing raw data. The phase argument selects the appropriate execution record; it does not restrict execution to the notebook's final section.

### Run Forecasting

```powershell
.venv/Scripts/python.exe docs/run_ml_notebook.py
```

This executes `notebooks/machine_learning.ipynb`, fits and compares models, and generates test predictions. It can take time. Viewing saved forecasts in the dashboard does not require rerunning model fitting.

### Figures, Validation, and Tests

To regenerate figures from saved results and validate them and the forecasts:

```powershell
.venv/Scripts/python.exe -m docs.finalize_phase12
.venv/Scripts/python.exe -m docs.validate_phase12
.venv/Scripts/python.exe -m docs.validate_phase10
```

To run the test suite:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

The latest recorded complete run passed **66 tests**, with no failures, errors, or skips. This is historical evidence, not a claim that tests were rerun while editing this page. See the [testing report](docs/testing_report.md).

### Start the Dashboard Locally

Once the required outputs are available:

```powershell
.venv/Scripts/python.exe -m streamlit run dashboard/app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
```

Open the [local dashboard](http://127.0.0.1:8501) and stop it with `Ctrl+C`. The application checks its inputs; it does not generate missing datasets or substitute synthetic examples.

These are reproduction instructions for reviewers and were not executed while editing this page. Execution commands regenerate derived outputs and saved evidence. Earlier phase records remain historical snapshots, including checks for files that had not yet been created at the time.

## AI-Assisted Workflow

`ChatGPT` supported planning, phase breakdown, result review, and implementation instructions, as confirmed by the project owner. `Codex` was the main implementation assistant, with evidence-based review. `Find Skills` was used to discover `exploratory-data-analysis` and `scikit-learn`, alongside the project's custom `promotion-impact-analysis` and `client-insight-reporting` skills.

Project instructions constrained the work, and outputs were checked through tests, independent calculations, notebook execution, and raw-file hashes. The [AI usage record](docs/ai_usage.md) documents roles, evidence, and limitations without claiming unsupported tools or invented productivity gains.

## Limitations

- Week numbers are not calendar dates, and locations are coded; specific seasons or real locations cannot be inferred.
- Promotions and discounts overlap. Association does not establish causation or campaign profitability.
- Missing meal-center-week records were not treated as zero demand. The variability measure includes differences across centers and time.
- Inventory, waste, supplier lead times, and purchasing costs are unavailable. No achieved savings or exact safety-stock quantity is established. Revenue is a proxy rather than profit, and currency is unspecified.
- Forecasts depend on pricing and promotion plans, and recursive errors can accumulate. Historical performance does not guarantee future performance.

Final QA: **79 checklist items reviewed**, **74/74 tests passed**, dependencies verified, raw data unchanged, and the [Arabic presentation](presentation/final_presentation.pptx) finalized (13 slides). See the [final audit](docs/final_audit.md) and [Phase 20 record](docs/phase20_progress.md). Final acceptance remains open for Git/publication verification (this copy has no `.git`) and a clean-environment installation test. No commit or push was performed.
