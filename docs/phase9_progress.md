# Phase 9 progress and validation

Date: 2026-10-27 (Asia/Hebron).

Status: **Phase 9 fully complete.** Phases 1–8 remain complete. This is the Phase 9 completion snapshot. Phase 10 was subsequently authorized; see [Phase 10 progress](phase10_progress.md).

## Completed checklist

- [x] Read project rules, Phase 9 requirements and the exact Phase 7 CV definition.
- [x] Specify joint volume/CV median thresholds before calculating segment results.
- [x] Reuse all 51 Phase 7 CVs unchanged and aggregate observed meal volumes from the validated analytical data.
- [x] Assign all meals to exactly four segments, handling equality explicitly and rejecting undefined metrics.
- [x] Identify primary planning-attention meals using both dimensions and document actual IDs, category/cuisine, orders, CV and interpretation.
- [x] Create and inspect a clear final volume-versus-volatility figure and embed it in the notebook.
- [x] Add reusable logic, deterministic tests, independent validation and actual findings.
- [x] Execute the complete notebook from a fresh kernel without errors.
- [x] Verify source conservation and raw/prepared hashes; do not zero-fill missing weeks or invent exact safety stock.
- [x] Update progress records; stop before Phase 10; do not commit or push.

## Actual segmentation and priorities

See [full findings and meal-level record](phase9_findings.md).

Method: unweighted medians across 51 meals; high means >= cutoff, low means < cutoff. Volume cutoff is **1,489,681 recorded orders**; CV cutoff is **0.8777404888357695**, using full precision. These are relative screening conventions, not validated risk probabilities or stock-policy limits. Volume sums actual recorded orders across weeks 1–145. CV is the Phase 7 sample std/mean over observed center-meal-week records, pooling center and time differences. No missing observations are inserted.

| Segment | Meals | Orders | Demand share |
| --- | ---: | ---: | ---: |
| High volume / high volatility | 14 | 54,918,637 | 45.9349% |
| High volume / low volatility | 12 | 48,502,252 | 40.5681% |
| Low volume / high volatility | 12 | 8,644,891 | 7.2307% |
| Low volume / low volatility | 13 | 7,491,705 | 6.2662% |

The primary review group is the high/high segment. Within it, priority order uses volume descending, CV descending for volume ties, then numeric ID. The five largest-volume meals in that group are:

| Meal ID | Category / cuisine | Orders | CV |
| --- | --- | ---: | ---: |
| 2290 | Rice Bowl / Indian | 9,770,303 | 1.15413492 |
| 1754 | Sandwich / Italian | 6,818,059 | 1.16904977 |
| 1109 | Rice Bowl / Indian | 6,367,773 | 0.92119788 |
| 1971 | Sandwich / Italian | 5,728,620 | 1.44532816 |
| 1727 | Rice Bowl / Indian | 4,735,987 | 1.19324535 |

No meal names are supplied; IDs and category/cuisine descriptors are used without inventing names. All 14 primary review meals and all 51 full assignments are documented. High-volume/low-CV meals are still material to replenishment, and low-volume/high-CV meals are not assigned primary priority solely because of CV.

Supported action: include high/high meals in weekly center-level purchasing exception reviews before considering stock-policy changes; monitor stockout/waste rates once inventory outcomes are available and per-meal out-of-time forecast error when forecasting is authorized. These are proposed monitoring KPIs, not measured improvements. No lead-time, inventory or service-level data supports exact buffer units, safety stock, stockout probabilities, or a calibrated loss score.

## Implementation and outputs

Created:

- `src/analysis/inventory.py`: observed-volume aggregation, Phase 7 provenance/coverage checks, median segmentation, joint priority ordering, and plotting.
- `tests/test_inventory_analysis.py`: eight deterministic integrity/boundary tests.
- `docs/validate_phase9.py`: independent per-meal sums/variance, medians, quadrants, priorities and notebook/source checks.
- `docs/phase9_findings.md`, `docs/phase9_progress.md`, `docs/phase9_validation.json`, and `docs/phase9_notebook_validation.json`.
- `reports/figures/demand_volume_volatility.png`: final Phase 9 volume/CV visualization, labeled with thresholds, all segments/counts, top-five IDs, source and caveats.
- Ignored `data/processed/phase9/inventory_segments.json` and `meal_inventory_segments.csv`: all 51 meal records including observations/center/week coverage and interpretations.

Updated `notebooks/analysis.ipynb`, notebook runner phase/figure expectations, README and Phase 8 progress forward reference. The Phase 6 validator now permits later authorized embedded/final figures instead of enforcing its old absence condition; its historical result JSON was preserved. No dependency changes or new skills were needed.

## Executed validation

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -p test_inventory_analysis.py -v
./.venv/Scripts/python.exe -m unittest discover -s tests -v
./.venv/Scripts/python.exe docs/run_analysis_notebook.py --phase 9
./.venv/Scripts/python.exe docs/validate_phase9.py
./.venv/Scripts/python.exe -m pip check
```

All commands exited **0**:

- **8 new tests passed**, covering all quadrants, conservation, inclusive median boundaries, rejecting CV-only priority, deterministic volume-first ordering, unchanged input/no imputation, median ties, missing/nonfinite/negative metrics, duplicate meal keys and invalid thresholds.
- **51 total tests passed**, including every prior preparation, EDA, KPI and promotion test.
- Full fresh-kernel notebook: **16 code cells, 0 errors, 6 embedded images**, nbformat validation passed. Actual evidence: `docs/phase9_notebook_validation.json`.
- Independent validator: **51 meals verified**. It uses SQLite sums/counts and independently derives sample variance from sums of squares, selects the 26th sorted value for each 51-meal median, assigns quadrants independently and checks exact reuse of stored Phase 7 CVs. It verifies all segment totals, priority order, metadata, CSV row count, current notebook and PNG signature. Actual evidence: `docs/phase9_validation.json` (passed).
- Volume/CV combination: 51 volume keys and 51 CV records become exactly 51 meal records; zero unmatched keys or expansion. All **456,548 observations** and **119,557,485 orders** reconcile across the segment partitions.
- All four raw SHA-256 values and the Phase 5 enriched-file hash remain unchanged; Phase 7 CV source provenance is recorded. No row deletion, zero filling, target editing or price correction occurred.
- The figure was visually reviewed: 51 points, exact full-precision thresholds used for assignment, readable axes/legend/caption, and five priority labels without clipping. Plot zeros are axis origins, not fabricated missing demand.
- `pip check`: **No broken requirements found**.

No Phase 9 numerical test or notebook failure occurred. Existing Phase 6–8 cells were rerun as required for whole-notebook validation, without changing their analytical logic. Earlier phase execution records remain historical snapshots.

## Completion boundary and limitations

The medians are relative, not operationally optimized. CV combines between-center and temporal variation and is influenced by uneven coverage and retained extreme demand. Missing weeks remain unknown observations. No exact stock quantity or achieved inventory improvement is claimed. No forecasting design/model, Phase 10 notebook, final client report, raw-data modification, commit or push was performed.
