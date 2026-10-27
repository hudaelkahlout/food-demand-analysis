# Phase 6 progress and exploratory findings

Date: 2026-10-27 (Asia/Hebron).

Status: **Phase 6 fully complete.** Phases 1–5 remain complete. This record describes the Phase 6 completion snapshot. Subsequent Phase 7 work is recorded in [Phase 7 progress](phase7_progress.md). These are technical exploratory observations, not final client-report claims or recommendations.

## Completed checklist

- [x] Read the project rules, Phase 6 requirements, installed EDA skill and applicable tabular guidance.
- [x] Create `notebooks/analysis.ipynb` using the unchanged, hash-verified Phase 5 analytical table.
- [x] Analyze observed weekly totals, consecutive-week changes, peak/trough and unusual transitions without calendar inference.
- [x] Produce complete category and meal rankings and the smallest prefixes reaching 80% of recorded demand.
- [x] Analyze total and observed-week demand by center, and total/exposure-adjusted demand by center_type with area context.
- [x] Move reusable logic and exploratory plotting to `src/analysis/`.
- [x] Actually invoke the installed EDA skill on the enriched file and document its scan limits and contribution.
- [x] Add targeted tests and execute the notebook top to bottom in a fresh kernel.
- [x] Independently validate aggregates, threshold crossing, exposure denominators, embedded figures and raw/enriched input hashes.
- [x] Stop before Phase 7; do not modify raw data, create final reports, commit or push.

## Input, reproducibility and definitions

Input: `data/processed/train_prepared.csv`, verified against the SHA-256 recorded by Phase 5. All **456,548 observed rows** and **119,557,485 orders** are retained. There are 145 recorded global weeks, 14 categories, 51 meals and 77 centers. Every weekly/category/meal/center/type partition conserves the same order total; no filtering, joins, imputations or row deletions are performed.

`src/analysis/demand.py` streams records and rejects duplicate IDs/logical keys or conflicting center/meal attributes. Percentage changes require consecutive observed week indices and a nonzero preceding total; unavailable comparisons are left unavailable. No missing weeks are generated. Center weekly demand first sums recorded meals within a center-week, then averages the center's observed weeks. This is not the mean of raw center-meal rows.

Concentration ranks all observed groups by orders descending, breaks ties lexically, and includes the group that crosses 80%. The previous-prefix share is retained so the minimal crossing set is auditable. Aggregate display selections record selected/remaining group counts and order totals; they do not remove source observations.

From the project root:

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe -m unittest discover -s tests -v
./.venv/Scripts/python.exe docs/run_analysis_notebook.py
./.venv/Scripts/python.exe docs/validate_phase6.py
```

Direct notebook dependencies are pinned in requirements.txt: matplotlib 3.11.2, nbclient 0.11.0, nbformat 5.11.1, ipykernel 7.4.0, ipython 9.17.1 and jupyter-client 8.10.0. Core aggregation uses the standard library. The complete installed Windows/Python 3.11.4 environment snapshot is in `docs/phase6_environment.txt`; no forecasting or statistical package was added. The runner uses its own Python environment via a temporary kernel specification, clears prior cell outputs/counts, executes a fresh kernel, checks embedded images and notebook schema, then saves the executed notebook. No global kernel registration is needed.

## Actual weekly-demand findings

- Peak: **1,303,457 orders in week 48**.
- Trough: **380,065 orders in week 62**.
- Endpoints: 792,261 orders in week 1 versus 671,926 in week 145, a **-15.19%** change. This does not mean a monotonic decline.
- First ten observed weeks average 830,448.8 orders; last ten average 746,028.0, **-10.17%** lower. This is a descriptive block comparison, not a trend test or calendar-seasonality finding.
- Largest week-to-week percentage rise: week 63, **+113.67%**, or +432,010 orders.
- Largest percentage and absolute fall: week 62, **-55.81%**, or -480,040 orders.
- Largest absolute rise: week 48, **+495,188 orders** (+61.27%). The week-62 trough and week-63 rebound are notable descriptive transitions, not explained causes.

Full 145-week totals, observation counts, and changes are in the notebook and ignored `data/processed/phase6/eda_results.json`. Changing assortment/observation coverage can affect aggregates. No global week is absent, but underlying center-meal gaps remain unfilled.

## Actual 80% concentration findings

**5 of 14 categories cover 81.3997%** of recorded demand: Beverages, Rice Bowl, Sandwich, Salad, Pizza. The first four cover only 75.2238%, so the fifth category is required to cross 80%.

**22 of 51 meals cover 81.1818%**. The first 21 cover only 79.7189%. The crossing set, in ranked order, is:

2290, 1885, 1754, 1993, 1109, 2707, 1971, 2826, 1727, 1062, 2664, 2490, 2569, 1778, 1962, 2539, 2581, 2322, 2640, 1230, 1207, 1558.

The complete 14-category and 51-meal rankings and Pareto charts remain in the notebook. These are volume concentrations, not an instruction to remove the remaining groups.

## Actual center-performance findings

Center **13 (TYPE_B)** leads both recorded total demand (**4,296,545 orders**) and observed weekly average (**29,631.34 orders per observed week, averaged over 145 recorded weeks**). Its recorded operating area is 6.7, with physical units unspecified. Total volume is not evidence of efficiency.

Center **24 (TYPE_B)** has only **120 observed weeks**, with 25 global weeks unrecorded. Its 1,997,535 orders yield **16,646.125 per observed week**, using 120 as the denominator. No zero-demand assumptions were made for those absent weeks. The other 76 centers have 145 observed weeks.

| Center type | Centers | Recorded orders | Observed center-weeks | Orders per observed center-week | Median center weekly average | Median recorded op_area |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| TYPE_A | 43 | 68,978,517 | 6,235 | 11,063.11 | 10,007.21 | 4.0 |
| TYPE_B | 15 | 29,996,073 | 2,150 | 13,951.66 | 13,148.52 | 4.4 |
| TYPE_C | 19 | 20,582,895 | 2,755 | 7,471.11 | 7,006.34 | 3.0 |

TYPE_A leads total demand but has more centers. TYPE_B has the highest orders per observed center-week. The type average is weighted by recorded center-weeks; the median center weekly average is reported separately. Area ranges and medians are shown as context, not used to claim productivity or causation. Center type, area, assortment, location and missingness are not controlled for in these descriptive comparisons.

## Actual installed-skill use

Read the installed exploratory-data-analysis entrypoint and tabular guidance; used its requirements for explicit observation units, full-scan disclosure, missing-vs-zero separation, and noncausal interpretation. The notebook executed the installed `capability_manifest.py` on the enriched file before `tabular_profile.py --max-rows 500000`. Both succeeded. The profile scanned **456,548 rows**, with `row_limit_reached=false`. Exact commands are retained under ignored `data/processed/phase6/skill_commands.json`, alongside the manifest/profile JSON.

The skill's bounded numeric sampling is not used for the business aggregates: those use every observed row through project code. No inference, transformation or automatic deletion is performed. Attribution remains in the notebook and `docs/find_skills.md` (Kassis et al., 2026, Scientific Agent Skills, DOI 10.48550/arXiv.2609.00065; source metadata verified in Phase 3). Neither custom skill nor scikit-learn was invoked in this descriptive phase.

## Executed tests, notebook and independent validation

- `python -m unittest discover -s tests -p test_demand_analysis.py -v`: **10 new tests passed**.
- `./.venv/Scripts/python.exe -m unittest discover -s tests -v`: **20 total tests passed**, including the 10 Phase 5 tests.
- New coverage includes missing-week non-bridging, no zero imputation, unavailable zero-denominator changes, threshold crossing/exact-boundary/tie handling, invalid concentration inputs, summing meals before weekly center averaging, unequal center-week exposure, duplicate rejection, conflicting lookup attributes and invalid/empty records.
- Final notebook execution: **9 code cells executed sequentially from a fresh kernel, 0 errors, 5 embedded PNG charts**, nbformat validation passed. Saved actual result: `docs/phase6_notebook_validation.json`.
- Independent SQLite calculations matched all weekly, category, meal, center and type aggregates; exact-integer threshold crossing and observed-center-week denominators were verified. Output: `docs/phase6_validation.json` (status passed).
- `pip check`: **No broken requirements found**.
- Inspected all five saved exploratory charts visually: titles, axes/units, category/meal labels, cumulative 80% lines and explanatory captions are readable without clipping. Draft PNGs remain under ignored `data/processed/phase6/`; no final figures were written to `reports/figures/`.
- Raw hashes match the Phase 5/Phase 1 records; the Phase 5 enriched input hash is unchanged. No missing weeks were filled and no source rows removed.

Initial execution issues were resolved: Windows sandbox denied Jupyter's temporary connection-file ACL operation, so local kernel execution required an escalated command. An initial calculation run completed but using the noninteractive matplotlib backend did not embed charts; replaced figure display with explicit PNG image display and reran the entire notebook successfully. The final saved notebook has five embedded images. Local-kernel transport/shutdown notices were not cell errors. No failed run is reported as the final successful validation.

The Phase 5 validator's historical no-analysis-notebook assertion was moved behind `--phase5-snapshot`, preserving its full data checks for use after authorized Phase 6 creation. Its old validation JSON remains the original Phase 5 snapshot. The default current validator reports a later notebook as outside its scope.

## Files created or updated

Created:

- `notebooks/analysis.ipynb` (executed with actual tables, findings and five exploratory charts).
- `src/analysis/__init__.py`, `src/analysis/demand.py`, `src/analysis/plots.py`.
- `tests/test_demand_analysis.py`.
- `docs/run_analysis_notebook.py`, `docs/validate_phase6.py`.
- `docs/phase6_notebook_validation.json`, `docs/phase6_validation.json`, `docs/phase6_environment.txt`, and this `docs/phase6_progress.md`.
- Ignored Phase 6 result/skill/integrity JSON and five draft PNGs under `data/processed/phase6/`.

Updated requirements.txt, README.md, docs/find_skills.md, the Phase 5 progress forward link, and docs/validate_phase5.py for the boundary compatibility described above.

## Stopping boundary and limitations

No Phase 7 KPI suite, revenue/discount/promotion-share/volatility calculations, statistical tests, promotion analysis, ML, dashboard, final report or final-figure deliverable was started. The notebook's requested totals and descriptive weekly averages do not constitute the later KPI suite. No calendar seasonality is inferred, and center-volume comparisons do not establish an intrinsic type effect. No final client-report claims or recommendations were authored. No raw data changes, commits or pushes occurred.
