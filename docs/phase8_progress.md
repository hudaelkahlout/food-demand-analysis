# Phase 8 progress and validation

Date: 2026-10-27 (Asia/Hebron).

Status: **Phase 8 fully complete.** Phases 1–7 remain complete. This record describes the Phase 8 completion snapshot. Subsequent Phase 9 work is recorded in [Phase 9 progress](phase9_progress.md).

## Completed checklist

- [x] Read and use the custom promotion-impact-analysis skill and project statistical/data-integrity rules.
- [x] Compare email and homepage flag states within eligible same-meal/same-center contexts.
- [x] Report observation/series counts, comparison exclusions, demand summaries, absolute/percentage differences and Mann–Whitney results.
- [x] Compare four combined marketing states on adequate common support.
- [x] Calculate global and within-context Spearman association for signed discount versus demand.
- [x] Investigate discount and other-channel overlap and explain remaining confounding.
- [x] Separate observed magnitude from IID-reference p-values and dependence-aware conditional uncertainty.
- [x] Preserve all 116,101 negative discounts, source rows, orders and raw/prepared input hashes.
- [x] Add reusable logic, deterministic tests, independent validation and actual notebook findings.
- [x] Run the full notebook from a fresh kernel; update actual findings/progress; do not start Phase 9, commit or push.

## Implementation and actual skill use

Used `.github/skills/promotion-impact-analysis/SKILL.md` as the project-specific analytical workflow. Implemented its same-meal/center comparisons, separate flag states, observation/series coverage, mean/median/IQR and percentage differences, conditional Mann–Whitney reporting, Spearman, signed-discount preservation, cross-channel overlap, and distinct evidence/business interpretation. Read the source restrictions for both SciPy tests from official documentation. No client-reporting or ML skill was invoked.

Main outputs are [actual findings and limitations](phase8_findings.md), the executed notebook, and ignored `data/processed/phase8/promotion_results.json`. Source records were not deleted or rewritten. Binary contexts need five observations per state; all four combined states must have five observations in the same context, with at least 30 such contexts for combined comparisons. These rules and the primary estimator were specified before computing results.

## Main actual results

- Email: 2,482 eligible contexts; 36,089 flagged and 299,781 unflagged records. Equal-context means 621.7657 versus 214.2454 orders; difference +407.5203 (+190.2119%). Pooled Mann–Whitney U=7,782,078,033.5.
- Homepage: 2,432 eligible contexts; 48,451 flagged and 282,271 unflagged records. Equal-context means 633.8146 versus 244.8429; difference +388.9717 (+158.8658%). Pooled Mann–Whitney U=9,401,139,402.5.
- Combined: 490 common contexts; neither n=50,156, email only n=4,868, homepage only n=5,475, both n=7,332. Equal-context means 151.3901, 494.8347, 409.9645 and 643.8474, respectively. Differences against neither: +226.8608%, +170.8001% and +325.2904%.
- Global Spearman: rho=0.12181340, n=456,548; weak positive monotonic association. Within-context mean rho=0.26292983 and median=0.26009067 over 3,571 eligible contexts. No combined significance test was inferred from those correlations.
- Mean global signed discounts: email 23.9789% versus 4.1068%; homepage 16.6892% versus 4.3748%. Both flags occur in 19,231 records. This overlap limits attribution of apparent promotion associations.

Full medians/IQRs, exclusion counts and order totals, signed-discount distributions, nominal p-value interpretation, combined-condition details, and all bootstrap intervals are in the findings document and notebook.

## Statistical interpretation and uncertainty

Mann–Whitney p-values and the global Spearman p-value numerically underflow to 0.0 under independent-row reference models; they are not exact zeros or calibrated confirmatory significance after repeated weeks/shared shocks. U describes pooled rank differences, not a paired/stratified test or automatic median test. The equal-context mean difference is a separate estimand.

For five predeclared demand contrasts, use a linearized common-week-block bootstrap over the same fixed contexts. There are 2,000 replicates, seed 20261027, primary 8-week blocks and 4/12-week sensitivity. Pointwise 95% and family-threshold 99% intervals are approximate and conditional on weak-dependence/stationarity assumptions. They capture joint weekly residual variation, not systematic discount/time confounding or new-center uncertainty. Percent bounds scale by the original baseline. Circular wrapping is computational, not a calendar-seasonality claim.

All five approximate 99% intervals exclude zero for all three block lengths; that is conditional evidence for positive observed contrasts under the resampling design. It does not establish isolated channel contributions, causation, profitability, or inventory requirements. Confirmatory dependence-aware significance for Spearman is not established because such a test was not performed; its coefficient and descriptive within-context distribution are reported honestly.

## Commands and actual validation results

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -v
./.venv/Scripts/python.exe docs/run_analysis_notebook.py --phase 8
./.venv/Scripts/python.exe docs/validate_phase8.py
./.venv/Scripts/python.exe -m pip check
```

- Ten new statistical tests passed; **43 total tests passed**. Cases cover equal-context rather than pooled weighting, missing states/insufficient samples and coverage, tie-aware U orientation, insufficient/constant rank inputs, Spearman direction, invalid paired values, zero percentage denominator, negative-discount retention, seeded bootstrap reproducibility, and rejecting nonconsecutive global weeks for block inference.
- An initial one-observation synthetic test found a missing probability-of-superiority field when the p-value wrapper correctly declined a small-sample test. Corrected descriptive within-context U calculation to be independent of p-value availability. The final ten new tests and all 43 tests passed. Real-data comparisons already required at least five observations per state.
- Final fresh-kernel notebook execution: **14 code cells, 0 error outputs, 5 existing embedded charts**, nbformat schema validation passed. The final rerun includes explicit within-context Spearman row/order coverage. Actual evidence: `docs/phase8_notebook_validation.json`.
- Independent validation passed: explicit frequency-count Mann–Whitney U and tie-corrected normal reference p; separate context/state means and counts; all five contrasts’ 4/8/12-week bootstrap intervals replicated with scalar block draws; global and within-context Spearman via independently assigned midranks and Pearson rank correlation; SQLite overlap counts/means; raw and analytical-input hashes. Result: `docs/phase8_validation.json`.
- Within-context Spearman scope reconciles 456,415 eligible rows / 119,550,125 orders and 133 excluded rows / 7,360 orders; 26 contexts lack the minimum/nonconstant support. Global Spearman still includes all records.
- `pip check` returned **No broken requirements found**. SciPy 1.17.1 was added for the requested tests; NumPy 2.4.6 is now a direct requirement for numerical analysis. Actual full environment captured in `docs/phase8_environment.txt`.
- The raw files and Phase 5 prepared table remain byte-identical to their recorded hashes; all 456,548 observations and 119,557,485 orders are retained in the analytical source. No discount is clamped.

## Files created or updated

Created `src/statistics/__init__.py`, `src/statistics/promotions.py`, `tests/test_promotions.py`, `docs/validate_phase8.py`, `docs/phase8_findings.md`, `docs/phase8_progress.md`, `docs/phase8_validation.json`, `docs/phase8_notebook_validation.json`, `docs/phase8_environment.txt`, and the ignored aggregate result JSON.

Updated `notebooks/analysis.ipynb` with design, actual comparisons, p-value limitations, common support, bootstrap sensitivity, Spearman and overlap; `docs/run_analysis_notebook.py` with phase 8 evidence support; requirements.txt with actually needed dependencies; README and Phase 7 progress forward references. The Phase 7 validator accepts appended later notebook cells while preserving its historical validation record; its KPI checks remain unchanged. No existing skill was rewritten or duplicated.

## Completion boundary

No Phase 9 volatility-volume ranking, segmentation, safety-stock recommendations or final inventory-risk visualization was created. Prior Phase 7 CV cells rerun unchanged as part of notebook validation. There is no forecasting, client-report deliverable, causal interpretation, raw-data change, Git commit or push. Findings remain observational and restricted to the documented populations and assumptions.
