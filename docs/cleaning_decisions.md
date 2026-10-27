# Cleaning decisions: Phase 5

Date: 2026-10-27 (Asia/Hebron). Training enrichment and data-quality investigation only.

## Reproduction and scope

Run `python -m src.data_processing.prepare` from the project root using Python 3.11+; no third-party Python packages are required. The command strictly loads all four CSVs, audits source tables, enriches training through two validated left joins, investigates training anomalies and observation coverage, runs the installed EDA skill, checks raw hashes, and writes the aggregate [audit record](phase5_audit.json). Run `python docs/validate_phase5.py` for the independent full-output cross-check and `python -m unittest discover -s tests -p test_data_preparation.py -v` for deterministic integrity tests.

The four source tables receive missingness and duplicate checks. Price/order anomaly and missing-week investigation below concerns the historical training table; future test inputs are not merged or used to infer demand. No Phase 6 business EDA, trend/category ranking, charts, KPIs, inferential tests, or modeling were started.

## Merge validation

Both joins are many-to-one left joins with unique lookup keys. Each checks row count, unique identifiers/keys, order total, unmatched row/key counts, and duplicate expansion before/after. Missing or duplicated join keys and unmatched demand references cause an explicit failure.

| Join | Rows before → after | num_orders before → after | Unmatched rows/keys before → after | Duplicate expansion |
| --- | ---: | ---: | --- | ---: |
| `meal_info` on `meal_id` | 456,548 → 456,548 | 119,557,485 → 119,557,485 | 0 / 0 → 0 / 0 | 0 |
| `fulfilment_center_info` on `center_id` | 456,548 → 456,548 | 119,557,485 → 119,557,485 | 0 / 0 → 0 / 0 | 0 |

Unique IDs and logical week/center/meal keys remain 456,548 at each stage; distinct meal and center IDs remain 51 and 77. The meal lookup has 51 unique meal keys; the center lookup has 77 unique center keys. The final `data/processed/train_prepared.csv` has **456,548 rows × 15 columns**: the original nine columns plus category, cuisine, city_code, region_code, center_type, and op_area. Every original training cell string and its row order was preserved. No target-dependent audit flags, thresholds, or statistics were added as model features.

## Decisions

| Issue | Count | Investigation | Decision | Reason | Impact |
| --- | --- | --- | --- | --- | --- |
| Missing values | 0 cells in all four inputs and all 15 prepared columns | Full scans; empty/whitespace and NA/NaN/null/none/N/A markers checked per column | No imputation | No detected missing cells; absent observations are assessed separately below | 0 cells changed |
| Exact and logical duplicates | 0 excess rows in each input and prepared table | Grouped by all source columns for exact duplicates; by week/center/meal for demand logical keys; lookup IDs for lookup keys | No deduplication | No duplicates identified | 0 rows removed |
| Checkout price above base price | 116,101 training rows | Differences span 0.03–185.30 price units; median 1.00; 73,687 are exactly 1.00; 74,621 are at most 1.00; occurs in 3,593 series across all 145 weeks | Retain original checkout and base prices; negative discounts remain possible | Small recurring differences coexist with larger discrepancies. CSVs cannot identify taxes, fees, reference-price timing, or recording errors; these are possible explanations, not established facts | 0 price edits; 0 deletions; all 26,320,670 orders on flagged rows retained |
| Global num_orders IQR flags | 32,937 rows, all above 729; 0 below −351 | Exact Q1=54, median=136, Q3=324; 99th percentile=1,796; maximum=24,299. Compare within-series fences and extreme-record group context | Retain all orders without capping, winsorizing, log-transforming, or deletion | A skewed heterogeneous demand distribution and promotional context do not establish erroneous records; automated fences alone cannot justify removal | 0 order edits; retain 42,374,283 orders on globally flagged rows |
| Within-center-meal IQR flags | 26,158 rows (lower or upper local fences); 10,532 also globally flagged | Fences computed separately per observed center-meal series from all its recorded weeks; compare with global flags | Descriptive audit only, not an automatic exclusion rule | Different normal demand scales change flags; no independently verified invalid values | No removal; no group-derived features persisted |
| Missing weeks within observed center-meal pairs | 65,017 absent pair-week slots across 2,350 of 3,597 observed pairs | 21,468 leading, 40,548 internal, 3,001 trailing; 2,129 pairs have internal gaps, longest 121 weeks | Preserve observed rows; do not insert weeks or fill zero | Absence may reflect availability, recording gaps, or no demand; the files provide no availability/zero-sales indicator to distinguish them | 0 rows inserted and 0 zeros imputed; gaps remain explicit in separate coverage diagnostics |
| Never-observed center-meal pairs | 330 of 77×51 candidate pairs; 47,850 potential pair-week slots | Separate from the 3,597 observed pairs; a Cartesian product is not a confirmed offered-meal roster | Do not synthesize these series | No evidence every center offered every meal | No fabricated records |
| Missing meal-level weeks | 6 meals; 222 meal-week slots | 209 before first observation, 13 internal across 3 meals, 0 trailing; all 145 weeks occur somewhere in training | Retain gaps and avoid calendar explanations | Delayed availability is plausible but unverified; global week completeness does not imply per-meal completeness | No reindexing or zero filling |
| Nonpositive prices/orders or invalid binary flags | 0 training rows | Positive price/order ranges; both marketing flags checked against exactly 0/1 | No correction | No violations found | 0 edits |

## Investigation details and interpretation limits

### Pricing

Pricing flags cover 3,593 of 3,597 observed series and all 145 training weeks, so the issue is not confined to a single isolated week or series. Positive differences have Q1=1.00, median=1.00, Q3=2.00, 95th percentile=2.00, and 99th percentile=20.31 price units. The maximum is 185.30. This pattern supports treating the observations as an unresolved reference-price issue rather than asserting that every row is corrupt. Exactly 7,896 flagged rows have either marketing flag set; that is a context check, not an estimated promotion effect. The actual mechanism needs source-owner clarification in future work. Preserve both price columns and allow future discount logic to retain negative values explicitly.

### Order extremes

The global flags occur across 1,472 series. Of the 32,937 global flags, 22,405 are not flagged by their own series’ IQR fences; 15,626 additional rows are flagged only by local fences. Threshold sensitivity demonstrates why a single global deletion rule is inappropriate.

The maximum observed count (24,299) belongs to a series with 145 observations and median 1,391; that series contains three observations at least half as large as the maximum. All ten highest observed counts have at least one marketing flag, and their series medians range from 420 to 1,565. For two of those ten records, their series contains no other observation at least half as large. These checks provide context, not proof of validity or causation. Without transaction corrections or operational records, retain the extremes and disclose their influence rather than presume measurement error.

All full-data quantiles and IQR counts use exact values with linear interpolation at (n−1)×p, not a bounded sample. These target-based audit diagnostics use all historical training rows, including the eventual holdout, only for data-quality description. They are not forecasting transformations or feature-selection rules. Any future learned preprocessing or outlier treatment must be fitted inside its training window without holdout leakage.

### Missing-week accounting

Observed series cover 456,548 pair-week observations. The 3,597 observed pairs have 3,597×145 = 521,565 potential slots within the common training window; 65,017 are absent. Internal gaps contribute 40,548 slots, before-first-observation absence contributes 21,468, and after-last-observation absence contributes 3,001. These components sum exactly to 65,017. Leading/trailing absence is kept distinct from an interruption between observed weeks.

The full 77×51×145 Cartesian grid has 569,415 potential slots, but that is not an availability roster. Its 112,867 unobserved slots comprise 65,017 in observed pairs plus 47,850 in 330 never-observed pairs. No global training week is missing. Six meals are absent in at least one week when pooling all centers; 222 missing meal-week slots comprise 209 leading and 13 internal. Detailed per-series coverage is saved only under ignored `data/processed/center_meal_week_coverage.csv`.

## Missing values: per-column count, percentage and decision

All rows below are full-file checks. The prepared table is checked after both joins. Zero refers to absent field values, not missing records.

| Table | Column | Missing count | Missing percentage | Decision |
| --- | --- | ---: | ---: | --- |
| `train` | `id` | 0 | 0.0000% | No imputation |
| `train` | `week` | 0 | 0.0000% | No imputation |
| `train` | `center_id` | 0 | 0.0000% | No imputation |
| `train` | `meal_id` | 0 | 0.0000% | No imputation |
| `train` | `checkout_price` | 0 | 0.0000% | No imputation |
| `train` | `base_price` | 0 | 0.0000% | No imputation |
| `train` | `emailer_for_promotion` | 0 | 0.0000% | No imputation |
| `train` | `homepage_featured` | 0 | 0.0000% | No imputation |
| `train` | `num_orders` | 0 | 0.0000% | No imputation |
| `test` | `id` | 0 | 0.0000% | No imputation |
| `test` | `week` | 0 | 0.0000% | No imputation |
| `test` | `center_id` | 0 | 0.0000% | No imputation |
| `test` | `meal_id` | 0 | 0.0000% | No imputation |
| `test` | `checkout_price` | 0 | 0.0000% | No imputation |
| `test` | `base_price` | 0 | 0.0000% | No imputation |
| `test` | `emailer_for_promotion` | 0 | 0.0000% | No imputation |
| `test` | `homepage_featured` | 0 | 0.0000% | No imputation |
| `meal_info` | `meal_id` | 0 | 0.0000% | No imputation |
| `meal_info` | `category` | 0 | 0.0000% | No imputation |
| `meal_info` | `cuisine` | 0 | 0.0000% | No imputation |
| `fulfilment_center_info` | `center_id` | 0 | 0.0000% | No imputation |
| `fulfilment_center_info` | `city_code` | 0 | 0.0000% | No imputation |
| `fulfilment_center_info` | `region_code` | 0 | 0.0000% | No imputation |
| `fulfilment_center_info` | `center_type` | 0 | 0.0000% | No imputation |
| `fulfilment_center_info` | `op_area` | 0 | 0.0000% | No imputation |
| `train_prepared` | `id` | 0 | 0.0000% | No imputation |
| `train_prepared` | `week` | 0 | 0.0000% | No imputation |
| `train_prepared` | `center_id` | 0 | 0.0000% | No imputation |
| `train_prepared` | `meal_id` | 0 | 0.0000% | No imputation |
| `train_prepared` | `checkout_price` | 0 | 0.0000% | No imputation |
| `train_prepared` | `base_price` | 0 | 0.0000% | No imputation |
| `train_prepared` | `emailer_for_promotion` | 0 | 0.0000% | No imputation |
| `train_prepared` | `homepage_featured` | 0 | 0.0000% | No imputation |
| `train_prepared` | `num_orders` | 0 | 0.0000% | No imputation |
| `train_prepared` | `category` | 0 | 0.0000% | No imputation |
| `train_prepared` | `cuisine` | 0 | 0.0000% | No imputation |
| `train_prepared` | `city_code` | 0 | 0.0000% | No imputation |
| `train_prepared` | `region_code` | 0 | 0.0000% | No imputation |
| `train_prepared` | `center_type` | 0 | 0.0000% | No imputation |
| `train_prepared` | `op_area` | 0 | 0.0000% | No imputation |

## Diagnostic selections and retained totals

These are audit partitions, not filtering/deletion operations on the prepared table. Their complements are recorded so all rows and orders are accounted for.

| Diagnostic selection | Selected rows | Selected orders | Complement rows | Complement orders | Dataset rows deleted |
| --- | ---: | ---: | ---: | ---: | ---: |
| Checkout above base | 116,101 | 26,320,670 | 340,447 | 93,236,815 | 0 |
| Global order IQR flags | 32,937 | 42,374,283 | 423,611 | 77,183,202 | 0 |

After all decisions, the prepared table still contains **456,548 observations and 119,557,485 orders**. Rows removed, rows inserted, imputed cells, corrected prices and altered targets are all **0**. Enrichment adds only lookup attributes.

## Actual installed-skill use

Used the installed [exploratory-data-analysis skill](../.agents/skills/exploratory-data-analysis/SKILL.md) and its general-tabular reference for this data-quality audit. Executed four manifests, four full-row tabular profiles, and one order-distribution sensitivity report. The exact commands are recorded in `skill_use.commands` in [phase5_audit.json](phase5_audit.json). Raw skill outputs live under ignored `data/processed/phase5_skill/`.

Each CSV profile explicitly used a 500,000-row limit and the inventory missing-token policy; all four profiles scanned every row with `row_limit_reached=false`. The order sensitivity tool also scanned all 456,548 rows, but its moments/quantiles/outlier sensitivity used a deterministic **4,096-value sample**. Its sample Q3=325 and upper fence=731.5 differ from the full-data Q3=324 and upper fence=729; the sample found 272 flags, which must not be represented as the full-data flag count. The exact custom audit supplies the reported 32,937 full-data flags.

The skill’s robust-summary and transformation suggestions are diagnostic only: no rows were deleted, no values were winsorized, no log transformation was applied, and no statistical tests were run. Its sample-based sensitivity demonstrates influence from the upper tail, but is not a full-data sensitivity estimate or an instruction to transform the target. This documented distinction between row scan coverage and sampled numerical summaries is an observed benefit of using the skill.

Attribution: Kassis, T., Agarwal, V., He, Y., Patel, D., and Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. [DOI](https://doi.org/10.48550/arXiv.2609.00065). Current-record details were verified during Phase 3; see [source and attribution record](find_skills.md).

## Integrity and validation

All four SHA-256 source hashes matched the Phase 1 inventory before and after execution. An independent CSV validator compared every original training cell and row order plus every joined lookup value, recomputed totals and exact pricing/global-IQR counts, checked every coverage record, verified output hashes and full skill scan coverage, and confirmed data paths remain ignored by Git. See [actual validation results](phase5_validation.json) and [Phase 5 progress](phase5_progress.md). Raw files were not modified. No commit or push occurred.
