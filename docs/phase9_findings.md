# Phase 9 inventory-planning screening

Date: 2026-10-27 (Asia/Hebron). Technical observed-demand findings; no Phase 10 forecasting or exact stock policy.

## Segmentation method and thresholds

All **51 meals** are assigned to exactly one volume/CV quadrant. Volume is total recorded orders for the meal across weeks 1–145, summed from the unchanged Phase 5 enriched table. Volatility is the **unchanged Phase 7 per-meal CV**, defined as sample std (ddof=1) divided by mean of observed center-meal-week order counts, pooled across centers and weeks. Phase 9 does not substitute a different CV or zero-fill absent records.

Threshold rule specified before segmentation: use the **unweighted median across the 51 meals** for each dimension. A value at or above the median is high; a value strictly below is low. Ties are not artificially split.

- High volume: **orders ≥ 1,489,681**.
- High volatility: **CV ≥ 0.8777404888357695** (displayed as 0.87774049).

Use full-precision CVs for assignment rather than rounded display values. These are relative portfolio thresholds for screening, not empirically calibrated probabilities of stockout, service-level limits, or optimized stock quantities. A lower-volatility meal can still be operationally important; pooled CV is not pure lead-time demand variation.

## Segment counts and exposure

| Segment | Meals | Observed orders | Recorded observations | Demand share |
| --- | ---: | ---: | ---: | ---: |
| high volume / high volatility | 14 | 54,918,637 | 149,177 | 45.9349% |
| high volume / low volatility | 12 | 48,502,252 | 122,939 | 40.5681% |
| low volume / high volatility | 12 | 8,644,891 | 95,061 | 7.2307% |
| low volume / low volatility | 13 | 7,491,705 | 89,371 | 6.2662% |

Counts sum to 51 meals; segment orders sum to 119,557,485; recorded observations sum to 456,548. No rows or meals are removed, and no missing weeks are inserted. Meal volume and Phase 7 CV metadata have one matching record per meal, zero unmatched keys and zero duplicate expansion; order totals are unchanged before/after that combination.

## Meals warranting primary planning attention

The primary group must have **both high volume and high CV**. It contains 14 meals, representing **54,918,637 observed orders (45.9349%)**. Within this group, order by total volume descending, then CV descending and numeric ID for ties. This is a transparent exposure-first review queue, not a measured loss-risk score or a ranking by CV alone. All 14 appear below; the chart labels the five largest-volume meals.

The files contain meal IDs, category and cuisine, but no actual meal names. Category/cuisine below are descriptors, not invented names.

| Meal ID | Category | Cuisine | Recorded orders | Phase 7 CV | Segment / interpretation |
| --- | --- | --- | ---: | ---: | --- |
| 2290 | Rice Bowl | Indian | 9,770,303 | 1.15413492 | High/high: review material volume and variation together |
| 1754 | Sandwich | Italian | 6,818,059 | 1.16904977 | High/high: review material volume and variation together |
| 1109 | Rice Bowl | Indian | 6,367,773 | 0.92119788 | High/high: review material volume and variation together |
| 1971 | Sandwich | Italian | 5,728,620 | 1.44532816 | High/high: review material volume and variation together |
| 1727 | Rice Bowl | Indian | 4,735,987 | 1.19324535 | High/high: review material volume and variation together |
| 2490 | Salad | Italian | 3,709,125 | 1.26501604 | High/high: review material volume and variation together |
| 1962 | Pizza | Continental | 3,235,780 | 0.96487842 | High/high: review material volume and variation together |
| 2539 | Beverages | Thai | 3,234,528 | 0.87774049 | High/high: review material volume and variation together |
| 2581 | Pizza | Continental | 2,399,000 | 0.95867107 | High/high: review material volume and variation together |
| 2322 | Beverages | Continental | 2,298,221 | 0.88977408 | High/high: review material volume and variation together |
| 1558 | Pizza | Continental | 1,748,940 | 0.98624116 | High/high: review material volume and variation together |
| 1525 | Other Snacks | Thai | 1,719,378 | 1.03879410 | High/high: review material volume and variation together |
| 2704 | Other Snacks | Thai | 1,610,896 | 0.90811543 | High/high: review material volume and variation together |
| 1878 | Starters | Thai | 1,542,027 | 0.88927675 | High/high: review material volume and variation together |

**Supported next action:** include these meals in each weekly center-level purchasing exception review; confirm local demand patterns, available meals and operational changes before changing buffers. Evidence is each meal's recorded volume and CV, not a claim that stockouts already occurred. Monitor stockout and waste rates once inventory outcome records are supplied, and per-meal out-of-time forecast errors after the forecasting phase is authorized. These monitoring KPIs are proposed, not already measured, and no numerical target is invented.

High-volume/low-CV meals account for another 40.5681% of recorded demand and still need reliable replenishment. Low-volume/high-CV meals account for 7.2307%: relative variability alone does not establish a large inventory consequence. Category, perishability and local service requirements can change priorities once relevant operational evidence is available.

## Volume-versus-volatility visualization

[Volume/CV quadrant figure](../reports/figures/demand_volume_volatility.png) plots all 51 meals using total observed volume on the horizontal axis and the exact Phase 7 CV on the vertical axis. Dashed lines are the two medians; colors show all four segments and counts; labels identify the five largest-volume high/high meals. The title, units, legend, source context and caveats are included. The notebook embeds the same figure, and it has been visually checked for legibility and clipping.

## Full meal-level record

Complete metadata, sample sizes/observed center and week coverage, full-precision CVs and segment interpretations are also retained in the notebook and ignored `data/processed/phase9/meal_inventory_segments.csv` and `inventory_segments.json`.

| Meal ID | Category | Cuisine | Recorded orders | CV | Segment | Interpretation |
| --- | --- | --- | ---: | ---: | --- | --- |
| 1062 | Beverages | Italian | 4,712,795 | 0.58122764 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 1109 | Rice Bowl | Indian | 6,367,773 | 0.92119788 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1198 | Extras | Thai | 1,018,280 | 0.79010233 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1207 | Beverages | Continental | 1,800,856 | 0.86770888 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 1216 | Pasta | Italian | 533,564 | 0.79842813 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1230 | Beverages | Continental | 1,843,969 | 0.86622972 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 1247 | Biryani | Indian | 231,897 | 0.70014947 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1248 | Beverages | Indian | 874,750 | 1.12397451 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 1311 | Extras | Thai | 1,489,681 | 0.80742779 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 1438 | Soup | Thai | 395,084 | 0.82569288 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1445 | Seafood | Continental | 1,059,221 | 1.33801619 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 1525 | Other Snacks | Thai | 1,719,378 | 1.03879410 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1543 | Desert | Indian | 791,037 | 0.85964453 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1558 | Pizza | Continental | 1,748,940 | 0.98624116 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1571 | Fish | Continental | 404,932 | 0.90707359 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 1727 | Rice Bowl | Indian | 4,735,987 | 1.19324535 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1754 | Sandwich | Italian | 6,818,059 | 1.16904977 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1770 | Biryani | Indian | 190,709 | 0.71119765 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1778 | Beverages | Italian | 3,308,383 | 0.77100772 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 1803 | Extras | Thai | 1,477,018 | 0.73349872 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1847 | Soup | Thai | 277,635 | 0.84121496 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1878 | Starters | Thai | 1,542,027 | 0.88927675 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1885 | Beverages | Thai | 8,346,246 | 0.83923491 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 1902 | Biryani | Indian | 209,242 | 0.74384942 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 1962 | Pizza | Continental | 3,235,780 | 0.96487842 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1971 | Sandwich | Italian | 5,728,620 | 1.44532816 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 1993 | Beverages | Thai | 6,656,856 | 0.76356944 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 2104 | Fish | Continental | 159,957 | 0.94875005 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2126 | Pasta | Italian | 597,580 | 0.82873720 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 2139 | Beverages | Indian | 380,997 | 0.76124390 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 2290 | Rice Bowl | Indian | 9,770,303 | 1.15413492 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 2304 | Desert | Indian | 609,378 | 0.89835163 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2306 | Pasta | Italian | 506,600 | 1.08999292 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2322 | Beverages | Continental | 2,298,221 | 0.88977408 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 2444 | Seafood | Continental | 942,568 | 1.42360526 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2490 | Salad | Italian | 3,709,125 | 1.26501604 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 2492 | Desert | Indian | 540,339 | 0.95040718 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2494 | Soup | Thai | 366,927 | 0.79465074 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 2539 | Beverages | Thai | 3,234,528 | 0.87774049 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 2569 | Salad | Italian | 3,334,399 | 0.69154697 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 2577 | Starters | Thai | 1,021,735 | 0.81389865 | low volume / low volatility | Proportionate routine review; local constraints still matter |
| 2581 | Pizza | Continental | 2,399,000 | 0.95867107 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 2631 | Beverages | Indian | 1,090,132 | 0.95275398 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2640 | Starters | Thai | 2,085,360 | 0.85235015 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 2664 | Salad | Italian | 3,900,812 | 0.62598150 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 2704 | Other Snacks | Thai | 1,610,896 | 0.90811543 | high volume / high volatility | Primary review: both dimensions meet high thresholds |
| 2707 | Beverages | Italian | 5,932,792 | 0.84891807 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 2760 | Other Snacks | Thai | 1,436,019 | 1.15107203 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2826 | Sandwich | Italian | 5,090,103 | 0.83923665 | high volume / low volatility | Maintain reliable replenishment for material volume |
| 2867 | Seafood | Continental | 713,925 | 1.26809376 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |
| 2956 | Fish | Continental | 307,070 | 0.93897049 | low volume / high volatility | Investigate selectively; high CV alone does not justify buffers |

Volume-median boundary meal(s): 1311. CV-median boundary meal(s): 2539. Equality places these on the high side; classification is sensitive to the chosen cutoff, especially at a boundary. No claim is made that the median is an operationally optimal breakpoint.

## Limits on inventory interpretation

CV mixes cross-center scale differences and within-center temporal variation. Observed totals depend on the period, assortment, center coverage and absent observations; none of the unrecorded weeks are assumed to have zero demand. Retained extreme orders also influence CV. This is an observed portfolio screen, not a calibrated forecast of shortages, waste or financial loss.

Supplier lead-time distributions, on-hand inventory, order constraints, shelf life, service-level targets and inventory outcomes are unavailable. **An exact safety-stock quantity cannot be justified.** Review at center level and obtain those inputs before making stock-policy changes; this phase does not prescribe buffer units or claim achieved waste/stockout reductions.

## Reproduction and validation

```powershell
./.venv/Scripts/python.exe -m unittest discover -s tests -v
./.venv/Scripts/python.exe docs/run_analysis_notebook.py --phase 9
./.venv/Scripts/python.exe docs/validate_phase9.py
```

Reusable logic: [inventory.py](../src/analysis/inventory.py). Actual execution: [Phase 9 progress](phase9_progress.md), [independent validation](phase9_validation.json), and [notebook validation](phase9_notebook_validation.json). The validator independently recomputes all meal totals and sample variances using SQLite sums/sums of squares, selects medians using the 26th order statistic, checks all quadrant assignments and priority ordering, and verifies exact reuse of the Phase 7 CV values.

All 51 meals and all source rows/orders reconcile; raw and prepared input hashes remain unchanged. No missing weeks are filled and no Phase 10 notebook/model, commit or push was created.
