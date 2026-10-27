---
applyTo: "**"
---

# Mandatory project rules

These rules apply to all food-demand-analysis work. Read [AGENTS.md](../../AGENTS.md) for client context, the inspected data description, business questions, and phase workflow. Detailed safeguards live here to avoid maintaining duplicate rule sets.

## Rule A — Data integrity

- Never edit, overwrite, rename, delete, or normalize files in `data/raw/`. Treat source CSVs as read-only. Check SHA-256 hashes against `docs/data_inventory.md` before and after work that reads or processes raw data; report any mismatch before relying on a changed input.
- Keep all raw and processed datasets under ignored `/data/`; save derived data to `data/processed/`. Keep data out of commits, including accidental copies outside that directory. Before any future authorized commit, inspect staged paths and tracked data: ignore patterns alone do not untrack files.
- Before and after each merge, record row counts, relevant unique-key counts, total `num_orders` when present, unmatched keys, and duplicate expansion. Use many-to-one validation for demand-to-meal and demand-to-center lookup joins. Fail on unexplained row multiplication, row loss, or changed order totals. Test inputs lack the target: mark order-total checks not applicable rather than inventing values.
- After every filtering operation or row deletion, log before/after row counts and relevant totals, including `num_orders` where present. Log rows removed, reasons, and effects in the cleaning record when that phase is authorized. Never silently drop anomalous observations.
- Revalidate schemas, missing values, primary keys, logical keys, join coverage, and promotion-flag domains when inputs change. Do not automatically delete checkout-above-base observations or high demand. Do not convert missing center-meal-week observations to zero without evidence about availability and measurement.

## Rule B — Evidence, statistical claims, and reporting

- No numerical claim without a reproducible source: retain the generating code/notebook and identify the input, aggregation, population, and output behind the claim. Do not fabricate statistics, citations, metrics, or tool usage.
- Do not use causal language for observational associations. Describe promotion, homepage, and discount relationships as associations unless an explicitly justified causal design supplies causal evidence.
- For promotion comparisons, account for meal and center context, state sample sizes and comparison groups, and investigate discount overlap/confounding. Use Mann–Whitney and Spearman only when suitable for the question and data; state assumptions and limitations. Statistical significance must be distinguished from business importance: report the effect magnitude alongside test evidence, not a p-value alone.
- Separate observed facts, statistical evidence, interpretation, recommendations, and limitations. Every recommendation must include supporting evidence, an actionable decision, and a success KPI. Every report must contain limitations.
- Client reports use simple, non-technical language. Put implementation details, model evaluation methods, AI usage, skill testing, and code-test evidence in technical documentation unless necessary for client understanding.
- Do not infer calendar seasonality from numbered weeks or identify real locations from city/region codes. State unknown currency and operating-area units. Label `checkout_price × num_orders` as a revenue proxy, never profit. Guard invalid/zero `base_price` in discount calculations. Inventory recommendations must consider volume as well as volatility; CV alone is insufficient.

## Rule C — Machine learning and leakage prevention

- Never randomly split or shuffle time-dependent forecasting records for evaluation. Use the final 10 training weeks (136–145 for the inspected data) as the chronological holdout, with weeks 1–135 for initial model fitting. `test.csv` covers weeks 146–155 and has no observed target; it cannot provide measured forecast accuracy.
- Prevent target leakage. Build center-meal lag and rolling features after sorting by week, shift before rolling, and use only information available before each prediction origin. Never use the current/future `num_orders`, target-derived full-period aggregates, or holdout/test targets in feature construction or fitting.
- Declare the prediction horizon and information available at forecast time. A rolling one-week evaluation may use earlier holdout actuals only when those would already be observed. A fixed-origin or multiweek forecast must not consume those unknown actuals; handle recursive predictions or other leakage-safe horizon design explicitly. Apply the same information constraints to the baseline and models.
- Fit imputation, scaling, encoding, feature selection, and any learned transformations only on the fitting window within each split, preferably through a pipeline. Use time-aware tuning within the pre-holdout window; do not repeatedly tune against final holdout results.
- Compare Linear Regression and Random Forest with the mandatory previous-week center-meal baseline using MAE on a documented, comparable evaluation population. Explicitly handle unavailable lags and unseen categories, and report coverage/exclusions. Select primarily by out-of-time performance. Report metrics honestly even if ML does not beat the baseline; never invent improvements.
- After evaluation and selection, document retraining on available training history. For test forecasts, preserve `id` and row alignment, output one finite non-negative prediction per input row, document any clipping, and save predictions only in ignored data storage. Never claim test MAE without ground truth.

## Rule D — Visualization

- Every final chart title must communicate a verified finding, using actual results rather than a generic topic or an invented conclusion.
- Label axes and units clearly, explain coded variables, and provide legends and source/context when needed. Do not invent currency or area units absent from the source.
- Avoid misleading scales, truncated comparisons without clear disclosure, and visual encodings that hide uncertainty or distort relative magnitudes. Keep comparable panels consistent.
- Add a concise interpretation or annotation to each final chart explaining the result and any material caveat. Save final PNG figures in `reports/figures/` when the visualization phase is authorized.

## Rule E — Reproducibility and implementation

- Keep numerical outputs reproducible from unchanged source files and versioned code. Use deterministic random seeds where randomness exists and record configurations, data windows, preprocessing choices, and package versions used for results.
- Keep `requirements.txt` limited to dependencies actually needed, with reproducible version constraints when packages are introduced. Document environment setup and exact execution commands. Do not install future-phase dependencies preemptively.
- Notebooks must run top to bottom from a fresh kernel without hidden state or manual edits. Keep reusable transformations in small, readable functions, validate inputs explicitly, and use project-relative paths. Do not suppress errors merely to produce apparently successful outputs.
- Update phase progress, validation evidence, and relevant technical documentation after authorized changes. Document failed checks and unresolved limitations alongside successful ones. Stop at the authorized phase boundary.

## Rule F — Testing and verification

- Validate checks appropriate to the authorized phase before marking it complete. For documentation changes, review requirement coverage, factual consistency, and links; do not create analytical test implementations merely to validate prose.
- When data-processing code is authorized, test required schemas and keys, raw-source immutability, many-to-one join row/order conservation, unmatched keys, and detection of duplicate expansion. Use deterministic small fixtures to exercise failure cases as well as valid inputs.
- When KPI and statistical functions are authorized, test formulas, grouping, promotion separation, insufficient samples, zero-denominator handling, and result structure. Never require a real-world hypothesis to be significant.
- When forecasting code is authorized, test chronological splits, lag/rolling construction and absence of future information, prediction length/alignment, non-negative finite forecasts, MAE, and deterministic behavior where seeded.
- Run meaningful automated tests and notebook execution as their phases become applicable. Record the exact command, actual result, and interpretation. Do not report planned tests as executed or passing, and fix relevant failures before declaring completion.
