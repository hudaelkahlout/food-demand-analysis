# Phase 12 progress — final client-ready visualizations

Date: 2026-10-27. Status: **Phase 12 fully complete.** Phase 13 has not been started. No commit or push performed.

## Completed checklist

- [x] Read project rules and Phase 12 requirements; review all existing figures before creating new charts.
- [x] Reuse and finalize suitable existing designs; retain the suitable volume-versus-volatility PNG unchanged.
- [x] Deliver all four required charts plus complementary center demand and existing volume/volatility charts: six final PNGs under `reports/figures/`.
- [x] Use verified conclusion titles, readable labels/units, short callouts, source/population notes and applicable legends/caveats.
- [x] Verify every plotted metric and displayed analytical value against validated historical analysis; confirm full density coverage and signed discounts.
- [x] Open and visually review all final images; fix layout/label issues in the same canonical files.
- [x] Confirm unchanged raw data, existing source/tests/notebooks and dependencies; use targeted plot validation without a full-suite rerun.
- [x] Record actual skill use and validation; stop before Phase 13; do not commit or push.

## Existing-figure review and reuse decisions

Before export, opened all five exploratory PNGs embedded in `notebooks/analysis.ipynb` (weekly trend, category Pareto, meal Pareto, center demand, center-type demand) and the existing final `demand_volume_volatility.png`. The notebook images were extracted only to ignored `data/processed/phase12/review/` for inspection.

The weekly, category and center designs were suitable foundations. The exporter calls the existing `weekly_figure`, `pareto_figure` and `center_figure` functions, then finalizes labels, callouts and source/context for client use. Their implementations and analytical data are unchanged. There was no existing promotion or discount plot to reuse; those two required views were added from the validated Phase 8 results. The volume/CV chart already met requirements and remains byte-for-byte unchanged.

The 51-meal Pareto has dense coded labels and repeats the concentration theme covered by the category chart; the center-type draft is optional. Both remain in the historical notebook. Neither was duplicated as another final export. No existing final chart was removed. Layout iterations overwrote the same canonical PNGs, without versioned duplicate files.

## Final chart register and verified findings

All historical demand figures cover the 456,548 recorded center-meal-week observations from training weeks 1–145. None substitutes test predictions for observed demand. Numerical sources are the validated Phase 6 output, Phase 8 output, and Phase 9 meal/CV output, with Phase 7 CV provenance. Phase 10 results were reviewed as available validated evidence but no optional ML chart was needed; no model was refitted.

| Final PNG | Reuse / creation | Finding and callout supported | Important context |
| --- | --- | --- | --- |
| [Weekly demand](../reports/figures/weekly_demand.png) | Existing Phase 6 two-panel design finalized | Demand peaked in **week 48 at 1,303,457 orders**. The chart also marks **week 62 at 380,065 orders** and shows all 144 consecutive weekly percentage changes. | Total orders are in millions on a zero-based vertical axis; changes are percentages around zero. Week indices are not calendar dates. Observation coverage and assortment vary; absent meal-center weeks stay absent. |
| [Category concentration](../reports/figures/category_pareto.png) | Existing Phase 6 Pareto finalized | **5 of 14 categories account for 81.40% of orders**: Beverages, Rice Bowl, Sandwich, Salad and Pizza. | Shows all category totals and the full cumulative curve; blue bars identify the smallest ranked prefix reaching 80%, including the crossing category. Orders are in millions; cumulative share is percent. This measures order concentration, not margin. |
| [Promotion comparison](../reports/figures/promotion_comparison.png) | New required view of existing Phase 8 results | Email: **621.8 vs 214.2** average orders, **+190.2%** observed difference. Homepage: **633.8 vs 244.8**, **+158.9%**. | Both means weight eligible meal-center groups equally. Email uses **2,482 groups**, with **36,089 flagged / 299,781 reference records**; homepage uses **2,432 groups**, **48,451 / 282,271 records**. Each group has at least five records per state. Separate panels share a zero-based scale. Discounts, timing and other flags differ; these are associations and the channel populations differ. |
| [Discount and demand](../reports/figures/discount_demand.png) | New required view of existing Phase 8 results | Discounts have a **weak positive association** with demand: **Spearman rho = 0.122**, rounded from 0.12181339880018344. | Density includes **all 456,548 records**, including **116,101 negative discounts**. Signed discount is `(base − checkout) / base`. Negative rates mean checkout exceeds base. Both positive demand and density color use explicitly labeled log scales; signed discount stays linear. Full observed ranges are visible; no causal line or unsupported significance claim is added. |
| [Center demand](../reports/figures/center_demand.png) | Existing Phase 6 center view finalized | **Center 13 leads recorded demand**: callout **29,631 orders per observed week**, rounded from 29,631.344827586207; its validated total is **4,296,545 orders** over 145 weeks. | Displays the top 10 of 77 centers by total orders, with bars showing average orders per observed center-week. Zero-based scale; coded IDs remain labels. Different assortment, coverage and operating area prevent an efficiency interpretation. |
| [Volume versus volatility](../reports/figures/demand_volume_volatility.png) | Existing Phase 9 final PNG retained unchanged | **14 meals combine high volume and high relative variation**, jointly representing **45.93% of observed orders**. | Both median thresholds are used: **1,489,681 orders**, **CV 0.8777404888357695** (chart rounds CV to 0.8777). Legend segment sizes are **14 / 12 / 12 / 13**. Top-five high/high meal labels: **2290, 1754, 1109, 1971, 1727**. CV pools center and temporal differences; it does not establish an exact safety-stock quantity. |

Every final chart has a conclusion-oriented title, a specific finding callout, readable labels, relevant units and source/context. The promotion figure avoids attributing the observed difference to the flag alone; the discount figure explicitly notes meal/center mix and promotion overlap. No achieved purchasing, waste, stockout or profit benefit is claimed.

## Numerical and visual validation actually performed

Commands executed from the project root:

```powershell
.venv/Scripts/python.exe -m docs.finalize_phase12
.venv/Scripts/python.exe -m docs.validate_phase12
.venv/Scripts/python.exe -m py_compile docs/finalize_phase12.py docs/validate_phase12.py
```

[Targeted validation](phase12_validation.json) passed. It reads the unchanged prepared data and independently checks:

- **145 weekly totals and 144 weekly changes**, including peak/trough annotations and rendered line/bar values.
- **All 14 category totals and cumulative shares**, the five-category 80% prefix, displayed 81.40%, and rendered bars/curve.
- **All 10 center bars**, selection by total, observed-week mean, leading coded ID and rounded callout.
- **Both promotion comparisons** using independent per-state/per-context pandas counts/means. Every displayed mean, percentage, group count and sample count agrees with Phase 8 and the actual rendered bar/text values. Comparison/complement row/order totals reconcile to the full source: email comparison 335,870 rows with 120,678 outside; homepage 330,722 with 125,826 outside. These are display populations, not source deletions.
- **Discount correlation**, recomputed using independent Decimal arithmetic and rank correlation, matching Phase 8. Hexagon counts sum to **456,548**; all negative rates remain; axis bounds encompass the full demand and signed-discount ranges. Log scales are explicit, and no sample or cropped-out tail is presented as the whole dataset.
- **All 51 meal volumes/CVs**, median cutoffs and segment sizes agree with Phase 7/9. The retained inventory PNG matches its pre-Phase-12 SHA-256 exactly.
- **Six valid PNGs**, each at least 1,800 × 1,000 pixels; final file hashes, source-result hashes and plotted Matplotlib artist data are recorded for traceability.

Opened all six final PNGs with the image viewer and inspected titles, axes, annotations, legends, density/color scale, footer readability and image boundaries. First-pass layout review found a duplicate old/new center title and a category callout intersecting the cumulative line. Both were corrected and the canonical files reopened. Promotion-state labels were made flag-specific (email absent/present; not featured/featured), and colorbar powers were replaced with plain counts. Final review passed.

An initial numeric check found rho 0.12181341116384894 when discounts were computed directly in floating point; tiny roundoff changed tied ranks. The final exporter reuses the existing validated Phase 7 Decimal discount function, and the independent validator uses its own Decimal expression. It matches the saved Phase 8 rho without loosening tolerances or changing that result. No historical numerical output was rewritten.

The export manifest, actual plotted numbers/text, original hashes and review copies are under ignored `data/processed/phase12/`. Reproduction initializes the integrity snapshot if absent, verifies the raw baseline and requires the existing Phase 9 PNG. Figures are generated from the saved validated analysis outputs, not from newly fitted or tuned models.

## Integrity and scope

All four raw-file SHA-256 values match the Phase 1 inventory before and after execution. Prepared input, existing reusable source, tests, notebooks and requirements remain unchanged. No rows were deleted, no negative discounts clamped, no outliers removed and no missing weeks filled. No new package was installed.

Only presentation/export code and its targeted validation were added under `docs/`; business, statistical and ML logic were not changed. The complete test suite was therefore **not rerun**. The Phase 11 result remains historical evidence of 66 passing tests, not a new test claim for Phase 12. Existing analysis and ML notebooks were not re-executed or edited.

Created `docs/finalize_phase12.py`, `docs/validate_phase12.py`, this progress record, `docs/phase12_validation.json`, and five new canonical final PNG exports; retained the sixth existing PNG unchanged. README current status and chart links were updated. **Phase 13 remains unstarted. No commit or push.**

## Actual skill use

Used the custom [client-insight-reporting skill](../.github/skills/client-insight-reporting/SKILL.md) for evidence-based chart titles, concise takeaways, units/populations and noncausal wording. Its role was communicating existing verified findings; it was not used to compute a new promotion result, retrain a model or create a client report. No recommendation or unsupported success claim was added.
