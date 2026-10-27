# Phase 5 progress and validation

Date: 2026-10-27 (Asia/Hebron).

Status: **Phase 5 fully complete.** Phases 1–4 remain complete. This record describes the Phase 5 completion snapshot. Subsequent Phase 6 work is recorded in [Phase 6 progress](phase6_progress.md).

## Completed checklist

- [x] Read project instructions, Phase 5 requirements, the installed EDA skill, and its general-tabular reference.
- [x] Verify all raw hashes against the Phase 1 inventory before work.
- [x] Add reusable strict CSV loading, validated enrichment, and data-quality functions under `src/data_processing/`.
- [x] Merge training with meal lookup on `meal_id` and center lookup on `center_id`, validating before/after counts, keys, orders, unmatched references and expansion.
- [x] Audit missing fields per column with count/percentage, exact and logical duplicates, prices, order extremes, and missing weeks.
- [x] Investigate price-difference magnitudes, series/week coverage, extreme-order group context, global versus within-series IQR flags, and internal versus boundary gaps before documenting retention decisions.
- [x] Use the installed EDA skill's actual tools and record their commands, row limits and numerical sampling limits.
- [x] Create `docs/cleaning_decisions.md` with counts, investigations, decisions, reasons and impacts.
- [x] Export the lossless 15-column training enrichment and separate series-coverage diagnostics only under ignored `data/processed/`.
- [x] Execute targeted tests and an independent full-file validator, fix relevant failures if any, and record actual results.
- [x] Verify source immutability and preserve original training cell values and row order.
- [x] Stop before Phase 6; do not commit or push.

## Actual execution

Commands run from the project root:

```powershell
python -m unittest discover -s tests -p test_data_preparation.py -v
python -m src.data_processing.prepare
python docs/validate_phase5.py
```

All exited **0**. The first command ran **10 tests, all passed**. The preparation command completed both joins, the full-data audit, and all nine installed-skill commands. The independent validator returned `status: passed`; its actual output is saved in `docs/phase5_validation.json`.

Python 3.11.4 and standard-library SQLite were used; exact runtime versions are in `docs/phase5_audit.json`. No third-party package is required or added. `requirements.txt` comments now describe the current standard-library workflow.

## Merge results

| Stage | Rows before → after | Orders before → after | Distinct IDs / logical keys | Distinct meal / center keys | Unmatched rows/keys before → after | Expansion |
| --- | ---: | ---: | --- | --- | --- | ---: |
| Meal enrichment | 456,548 → 456,548 | 119,557,485 → 119,557,485 | 456,548 / 456,548 | 51 / 77 | 0/0 → 0/0 | 0 |
| Center enrichment | 456,548 → 456,548 | 119,557,485 → 119,557,485 | 456,548 / 456,548 | 51 / 77 | 0/0 → 0/0 | 0 |

The final CSV has 456,548 rows × 15 columns. No source field values or row ordering changed. Joined attributes match the lookup entries for every row.

## Findings and decisions

- Missing values, exact duplicates, logical duplicates, and duplicate primary keys: **0** in every input and the prepared table. Per-column missing counts/percentages are in the audit and decisions document.
- Checkout above base: **116,101 training rows**. Positive differences range 0.03–185.30 price units; 73,687 equal 1.00. The issue spans 3,593 series and all 145 weeks. Retain original prices; the files do not establish the mechanism.
- Global order IQR flags: **32,937 rows** above 729 orders; none below −351. Local center-meal IQR flags: **26,158 rows**, with **10,532** overlapping global flags. Investigated quantiles and top-count series context. Retain all order values; neither magnitude nor a descriptive fence establishes invalidity.
- Missing-week slots in the 3,597 observed center-meal pairs: **65,017**, comprising **21,468 leading**, **40,548 internal**, and **3,001 trailing**. Internal gaps affect **2,129 pairs**. In total 2,350 observed pairs have some absence; longest internal gap is 121 weeks.
- **330 never-observed pairs** in the possible center×meal product represent another **47,850 potential slots**, not confirmed offerings. At meal level, **6 meals** have **222 absent meal-week slots**. All 145 weeks occur globally. Meaning of absence remains unknown; no zeros or fabricated series inserted.
- Nonpositive training prices/orders and invalid promotion flags: **0**.
- Final cleaning impact: **0 removed rows, 0 inserted rows, 0 imputations, 0 edited prices, and 0 edited targets**. All 119,557,485 orders retained. Detailed evidence and rationale are in `docs/cleaning_decisions.md`.

## Actual EDA skill use

Executed its capability manifest and tabular profile for each of the four raw CSVs, then order-distribution sensitivity on training. Every profile and the sensitivity tool scanned the full input with a 500,000-row cap and no row-limit truncation. Profiles received explicit missing tokens matching the inventory policy.

The sensitivity tool's numeric summaries use a deterministic **4,096-value sample** even when the row scan is complete. The sample found Q3=325, upper IQR fence=731.5 and 272 sampled flags. The separate exact full-data audit found Q3=324, upper fence=729 and 32,937 flags. These scopes are explicitly separated; no sampled count was extrapolated. No optional transformations, hypothesis tests or automatic deletion were performed. Exact executed command arguments are preserved in `docs/phase5_audit.json`; tool outputs are under `data/processed/phase5_skill/`.

## Validation coverage

Ten synthetic tests cover valid many-to-one preservation, rejection of duplicate lookup keys before expansion, unmatched keys, missing join keys, overlapping non-key columns, missingness and exact/logical duplicate distinctions, internal/boundary gap accounting, quantile interpolation/constants, retention of price anomalies and high orders, source immutability, and malformed-record rejection.

The independent validator streamed raw training and prepared output side by side and checked every original cell and row order plus all joined attributes. It independently recomputed rows, orders, exact price-above-base and global-IQR counts, and each observed series' week coverage. It checked every saved output hash and all skill row-scan counts, then validated four raw/processed ignore probes through real Git with temporary metadata. The workspace itself still has no `.git` directory; no repository initialization or staging occurred.

All four before/after raw SHA-256 values match the Phase 1 inventory. No Phase 6 analysis notebook exists. The implementation plan and installed skill sources remain unchanged. No failures occurred in the executed Phase 5 tests or main workflow.

## Files created or updated

Created:

- `src/data_processing/__init__.py`
- `src/data_processing/prepare.py`
- `tests/test_data_preparation.py`
- `docs/validate_phase5.py`
- `docs/phase5_audit.json`
- `docs/phase5_validation.json`
- `docs/cleaning_decisions.md`
- `docs/phase5_progress.md`
- Ignored `data/processed/train_prepared.csv`, `data/processed/center_meal_week_coverage.csv`, and nine tool JSON files under `data/processed/phase5_skill/`.

Updated README.md, requirements.txt comments, the Phase 4 progress forward link, and the EDA skill's actual-use record in docs/find_skills.md.

## Scope limits

This phase performs data preparation and diagnostic investigation, not business EDA or promotion-effect inference. Retention does not certify that every extreme record is valid; it records the lack of evidence justifying alteration. The dataset cannot distinguish unavailable meals from unrecorded or zero-demand weeks. Diagnostic target thresholds are not ML features or fitted forecasting transforms. No Phase 6 work, commits, or pushes were performed.
