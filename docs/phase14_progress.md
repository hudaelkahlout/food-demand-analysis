# Phase 14 progress — Arabic client report

Date: 2026-10-27. Status: **Phase 14 fully complete.** Phase 15 has not been started. No commit or push performed.

## Completed checklist

- [x] Read the complete attached request, Phase 14 plan, project rules and custom client-insight-reporting skill.
- [x] Create [the requested Arabic client report](../reports/client_report.md) for purchasing, operations, marketing and management.
- [x] Deliver all 11 requested sections; executive summary has four concise statements, starting with the 81.40% category-concentration finding.
- [x] Cover required demand/concentration/center/promotion/inventory/forecast facts without unexplained statistical or algorithmic terms.
- [x] Include four recommendations, each with action, supporting evidence, business reason and a proposed monitoring KPI/cadence.
- [x] Reference six existing validated final figures, each with an Arabic management takeaway; create no new chart.
- [x] Validate every displayed number and its population against existing results, plus Arabic-visible text and figure paths/hashes.
- [x] Confirm raw and protected artifacts unchanged; do not rerun expensive analysis or the complete suite.
- [x] Stop before Phase 15; create no technical report; do not commit or push.

## Report sections

The report contains exactly these 11 sections:

1. الملخص التنفيذي
2. المشكلة التجارية
3. نظرة عامة على الطلب
4. أين يتركّز الطلب؟
5. مراكز التوزيع
6. الترويج والتسعير
7. مخاطر تخطيط المخزون
8. التنبؤ بالطلب
9. التوصيات
10. حدود النتائج
11. الخلاصة الإدارية

The four recommendations address high-volume/high-variation meals, differentiated center planning, controlled promotion measurement with pricing coordination, and forecast-supported weekly purchasing. Suggested outcomes are explicitly future monitoring, not achieved savings or stockout/waste improvements.

## Evidence and language decisions

Used the custom [client-insight-reporting skill](../.github/skills/client-insight-reporting/SKILL.md) to translate verified results into concise Arabic findings, business implications, actions, monitoring measures and limitations. No new statistical analysis, model fit or client financial benefit was invented.

All report headings, sentences, table labels and link labels are Arabic. Original coded center categories are rendered as «أ» and «ب», with their mapping to TYPE_A/TYPE_B recorded in the validation evidence. The chosen forecast is described as the best selected model in business terms; its underlying winner is the already validated Random Forest. No algorithm explanation or unexplained abbreviation is needed in the report.

The user allows embedding or referencing existing charts. Used Arabic descriptive links to the six unchanged final PNGs rather than embedding their English text into the Arabic report. Each link has a short Arabic management takeaway. No translation/replacement of existing figures, additional chart or unvalidated illustration was created.

The report separates observed facts from proposed actions. Email, homepage and combined-condition percentages retain their respective comparison populations; the combined result is versus neither flag in common contexts. Channel percentages are not ranked as effectiveness, and promotion alone is not credited with the observed differences. Discount overlap is illustrated with validated global email-state means, explicitly distinguished from the comparable-group table.

Inventory attention uses both volume and variation. The highest-volume five priority IDs/volumes match Phase 9, and variation is described as including center and time differences. The forecast-error improvement refers to the historical weeks 136–145 comparison per meal-center-week, not company-total error or guaranteed future performance. Limitations cover missing weeks, coded geography, unknown costs/inventory/lead times/shelf life, revenue proxy and unspecified currency.

## Actual numerical/editorial validation

Executed:

```powershell
.venv/Scripts/python.exe -m docs.validate_phase14
```

Result: **passed**. The check reads saved Phase 6–10 results and their previously passed validation records; it does not regenerate them. [Machine-readable evidence](phase14_validation.json) contains **37 source-backed claim entries**, a check of all **53 displayed numerical occurrences**, rounding/formatting and source references. Repeated report figures are included in the occurrence scan. Worded numerical statements, center-type ordering, category translations and business interpretation were also reviewed against the saved values.

Verified total/average/peak/trough demand, category and meal concentration, center leadership/type rankings, eligible promotion group counts and all three percentages, discount-overlap means, the weak positive discount association, all five priority meal IDs/volumes, and baseline/selected forecast errors and improvement. Validated exactly 11 headings, four executive statements, four recommendation rows with all required columns, six Arabic chart takeaways and six existing figure links/hashes. Visible text contains no Latin-script words; filenames occur only in link destinations.

All four raw-file hashes match the original baseline. Existing data-preparation/analysis/model code, tests, both notebooks, saved forecasts and all final PNGs retain their pre-Phase-14 hashes. No input dataset was changed, no expensive analysis or full-suite run occurred, and no dependency was added.

## Deliverables and boundary

- `reports/client_report.md` — requested Arabic business report.
- `docs/validate_phase14.py` — bounded saved-value/editorial checks.
- `docs/phase14_validation.json` — actual numerical/source/structure/integrity evidence.
- This progress record and README client-report/status links.

The integrity snapshot is under ignored `data/processed/phase14/`. No technical report was created and Phase 15 remains unstarted. No commit or push.


## Meal lookup clarification before closing Phase 14

Read all 51 rows and the header of the original `meal_info.csv`, then verified IDs 2290, 1754, 1109, 1971 and 1727. The file contains only `meal_id`, `category`, and `cuisine`. IDs 2290/1109/1727 are Rice Bowl / Indian; 1754/1971 are Sandwich / Italian. These are shared classifications, not distinct meal names or detailed dish descriptions. Kept the IDs and order volumes unchanged, and corrected the Inventory Planning Risk sentence in Arabic to describe the lookup's actual fields and missing specific names/descriptions. The raw lookup hash remains unchanged. Revalidated the report's numbers, structure and chart links after the sentence edit.
