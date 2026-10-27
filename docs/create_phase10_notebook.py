from pathlib import Path
import nbformat
root=Path.cwd()
md=nbformat.v4.new_markdown_cell; code=nbformat.v4.new_code_cell
nb=nbformat.v4.new_notebook(cells=[
md('''# Phase 10 — chronological demand forecasting
Target: observed `num_orders` per center-meal-week. Fixed-origin forecast: fit weeks 1–135, recursively predict 136–145 without observing any holdout labels. All three models face the same ten-week horizon. After selection, refit through week 145 and recursively predict 146–155. No random split or tuning on holdout. Phase 11 is outside scope.

The installed scikit-learn skill and its pipeline reference guide train-only imputation/scaling/encoding, unknown-category handling, MAE, and seeded Random Forest. See `docs/phase10_progress.md` for actual use and limitations.'''),
code('''from pathlib import Path
import sys, json
ROOT = Path.cwd()
if not (ROOT / 'src').is_dir(): ROOT = ROOT.parent
sys.path.insert(0, str(ROOT))
from src.machine_learning.forecast import run
results = run(ROOT)'''),
md('''## Features and information contract
Known meal/center metadata and planned weekly prices/promotions are assumed available at the origin for every forecast week. These are scenario forecasts if the marketing plan changes. IDs are preserved for alignment and excluded as predictors; center/meal/location codes are categorical. Week is a trend index, not calendar seasonality.

Exact prior-week demand and mean/count over the preceding four numbered weeks use strictly earlier records. Missing weeks remain absent. Training features use earlier actuals; recursive holdout/test features use earlier predictions after the origin. No full-period target aggregates. Numeric median imputation and scaling, categorical one-hot encoding, and all fitting use fitting rows only. Baseline missing lag uses the fitting-window global median. Discount `(base-checkout)/base` remains negative when checkout exceeds base; invalid/nonpositive denominators become missing for training-only imputation.

Random Forest settings are fixed in code (40 trees, depth 14, bootstrap sample fraction 0.35, feature fraction 0.5, leaf minimum 5, seed 42); no holdout-driven tuning. Negative Linear Regression outputs are clipped to zero for both evaluation and deployment, with counts recorded.'''),
code('''print(json.dumps({k:results[k] for k in ['design','fit_weeks','holdout_weeks','fit_rows','holdout_rows','fit_orders','holdout_orders','features','joins']},indent=2))'''),
code('''import pandas as pd
comparison = pd.DataFrame(results['metrics']).T
print(comparison.to_string())
print('Selected by lowest holdout MAE:',results['winner'])
print(pd.DataFrame(results['weekly_mae']).to_string(index=False))'''),
md('''## Interpretation and operational use
MAE is the average absolute error in orders per observed center-meal-week; lower is better. The percentage improvement is `100 × (baseline MAE − model MAE) / baseline MAE`. Negative values mean deterioration. Weekly MAE shows where errors remain. Only one historical ten-week period was evaluated; selection on it makes its winning score optimistic as a future guarantee.

The next cell shows standardized numeric linear coefficients and one-hot category coefficients, plus forest impurity importance. These are descriptive model associations, not causal promotion effects. Correlated features share importance; impurity importance favors variables with many potential splits. No tuning follows interpretation.'''),
code('''for name, rows in results['interpretation'].items():
    print(name)
    print(pd.DataFrame(rows).to_string(index=False))'''),
code('''print(json.dumps(results['test_summary'],indent=2))
predictions = pd.read_csv(ROOT/'data/processed/phase10/test_predictions.csv')
raw_test = pd.read_csv(ROOT/'data/raw/test.csv')
assert predictions.id.tolist() == raw_test.id.tolist()
print(predictions.head().to_string(index=False))'''),
md('''## Limitations and purchasing support
Forecasts can provide a center-meal demand starting point for weekly purchasing review. Translate orders to ingredients only with recipes, lead times, shelf life, on-hand stock and service goals; these data are unavailable, so no exact purchase or safety-stock quantity is claimed. Compare forecasts with actuals weekly using MAE and bias, and monitor stockouts/waste once available.

Ten-week recursive errors can compound; training uses actual histories while future weeks use predicted histories. Missing series observations are not evidence of zero demand. Planning prices/promotions must be known; test prices can exceed training ranges. Unseen categories are encoded safely but may forecast poorly. Clipping prevents negative orders but adds no uncertainty interval. Test has no target, so no test MAE is reported. Center-meal forecasts support managerial review rather than automatic replenishment.'''),
code('''from docs.validate_phase10 import main as validate_phase10
validate_phase10()''')])
nb.metadata['kernelspec']={'display_name':'Food demand project Python','language':'python','name':'python3'}
nbformat.write(nb,root/'notebooks/machine_learning.ipynb')
