# Phase 8 observational findings

Date: 2026-10-27 (Asia/Hebron). Technical findings only. Phase 9 has not started.

## Design

Used the custom [promotion-impact-analysis skill](../.github/skills/promotion-impact-analysis/SKILL.md). All 456,548 observed center-meal-week records and 119,557,485 orders from the hash-verified Phase 5 export are retained. All 116,101 negative discounts remain unchanged. No source records are deleted or missing weeks filled. Test.csv has no observed target and is not used.

Binary comparisons require at least five observations in each state of the same center-meal context. Average demand within each state/context, then give eligible contexts equal weight. Percentage difference uses the equal-context unpromoted mean as denominator. This controls the identity of meal and center, but does not adjust for discounts, time, the other flag, availability or selection into promotion. Pooled row summaries and tests have different weighting and are labeled separately.

Combined comparisons require at least five observations in all four states and at least 30 common contexts. These prespecified thresholds support descriptive comparison, not independence. Five demand contrasts are declared: email, homepage, and three states versus neither.

## Binary comparisons

| Flag | Eligible contexts | Flagged n | Reference n | Equal-context flagged mean | Reference mean | Difference orders | Difference % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| email | 2,482 | 36,089 | 299,781 | 621.7657 | 214.2454 | +407.5203 | +190.2119% |
| homepage | 2,432 | 48,451 | 282,271 | 633.8146 | 244.8429 | +388.9717 | +158.8658% |

Email and homepage use different eligible populations; the percentages are not a controlled comparison of channel performance. Differences are orders per recorded observation averaged equally over eligible contexts, not changes in total company orders.

### Pooled distributions within eligible contexts

| Flag/state | n | Mean | Median | Q1 | Q3 |
| --- | ---: | ---: | ---: | ---: | ---: |
| email/flagged | 36,089 | 630.8134 | 337.0000 | 161.0000 | 730.0000 |
| email/reference | 299,781 | 224.3895 | 135.0000 | 55.0000 | 296.0000 |
| homepage/flagged | 48,451 | 597.8534 | 350.0000 | 136.0000 | 742.0000 |
| homepage/reference | 282,271 | 250.2132 | 149.0000 | 67.0000 | 324.0000 |

### Scope accounting: no source deletion

| Flag | Contexts lacking a state | Both states but below minimum | Excluded contexts | Comparison rows / outside rows | Comparison orders / outside orders |
| --- | ---: | ---: | ---: | --- | --- |
| email | 767 | 348 | 1,115 | 335,870 / 120,678 | 90,033,133 / 29,524,352 |
| homepage | 669 | 496 | 1,165 | 330,722 / 125,826 | 99,594,525 / 19,962,960 |

Each comparison and its complement reconcile to all 456,548 rows and 119,557,485 orders. Excluded contexts remain in the source and global analysis.

## Mann–Whitney and dependence-aware uncertainty

Mann–Whitney is two-sided, asymptotic, tie-corrected, with continuity correction; promoted records are sample x. U compares pooled distributions within eligible contexts. It is not a paired or stratified test, does not test the equal-context mean difference, and is not automatically a median test. P-values require independent rows. Repeated weeks and shared shocks violate that calibration, so these are **IID-reference p-values only**, not confirmatory significance. Every nominal p-value underflows to 0.0; this is not an exact zero.

For the equal-context mean difference, weekly residual contrast scores use fixed original per-state counts. The score is the equal-context average of flagged residual/n_flagged minus reference residual/n_reference. Joint circular week-block resampling uses the same week draws for every context; missing records add no observed residual, not zero orders. Keeping the eligible contexts fixed avoids silently changing populations when a bootstrap state vanishes.

Use 2,000 seeded replicates (20261027), primary blocks of eight weeks and four/twelve-week sensitivity. The first-order bootstrap assumes an approximately weakly dependent/stationary score process. It is conditional on these contexts, does not adjust systematic confounding, and does not sample new centers. Circular wrapping is computational, not calendar seasonality. Pointwise intervals are 95%; per-contrast 99% intervals implement the Bonferroni threshold for five contrasts at family alpha .05, with approximate rather than guaranteed coverage. Percentage intervals scale the difference bounds by the fixed original reference, not a full ratio-estimator bootstrap.

| Comparison | U (pooled reference) | IID p | 8-week 95% difference interval | 8-week 99% family interval |
| --- | ---: | --- | --- | --- |
| email | 7,782,078,033.5 | Underflow; not calibrated | 370.26 to 444.07 | 357.90 to 451.33 |
| homepage | 9,401,139,402.5 | Underflow; not calibrated | 357.16 to 424.91 | 346.40 to 435.26 |
| email_only vs neither | 179,927,434.5 | Underflow; not calibrated | 289.06 to 394.81 | 261.18 to 410.13 |
| homepage_only vs neither | 171,160,278.0 | Underflow; not calibrated | 216.93 to 310.09 | 208.99 to 329.44 |
| both vs neither | 310,911,613.0 | Underflow; not calibrated | 442.77 to 539.66 | 427.30 to 553.02 |

All five 99% intervals are above zero for each block length. This supports positive observed contrasts **under the resampling assumptions**, not isolated promotion attribution. Weekly-score lag-1 correlations are 0.0886 for email and 0.1988 for homepage; these are diagnostics, not stationarity tests. Longer dependence/drift can remain. Mean within-context probabilities of superiority are 0.8691 and 0.8324, respectively, using equal context weights.

**Business magnitude is separate:** these observed differences are substantial in orders per recorded observation. P-values or positive conditional intervals do not establish campaign profitability, a forecast, or a purchasing quantity. Costs, margins and counterfactual demand are unavailable.

## Combined conditions

Global context-only summaries, not adjusted comparisons:

| Condition | Observations | Contexts | Mean orders | Median | Q1 | Q3 | Mean discount |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| neither | 388,874 | 3,597 | 211.4170 | 122.0 | 53.0 | 283.0 | 3.5420% |
| email_only | 17,819 | 2,696 | 431.2776 | 229.0 | 107.0 | 473.0 | 22.5498% |
| homepage_only | 30,624 | 2,776 | 455.8762 | 258.0 | 95.0 | 594.0 | 11.2800% |
| both | 19,231 | 2,489 | 816.2461 | 474.0 | 243.0 | 1012.0 | 25.3029% |

**490 common meal-center contexts** satisfy the four-state rule. The common neither baseline is 151.3901 orders, with 50,156 observations. The four states in this restricted population total 67,831 observations. Other states/contexts remain outside each two-state contrast and are counted rather than deleted.

| Condition versus neither | Flagged n | Equal-context mean | Difference orders | Difference % |
| --- | ---: | ---: | ---: | ---: |
| email_only | 4,868 | 494.8347 | +343.4447 | +226.8608% |
| homepage_only | 5,475 | 409.9645 | +258.5745 | +170.8001% |
| both | 7,332 | 643.8474 | +492.4574 | +325.2904% |

Both flags have the highest observed state mean, but this is not an interaction/synergy test or an isolated channel contribution. Full pooled medians/IQRs, pairwise counts/order complements, U references and interval sensitivity appear in the notebook and result JSON.

## Spearman discount-demand association

All 456,548 records: **rho=0.12181340**, a weak positive monotonic association. The IID-reference p-value underflows to 0.0. It does not provide calibrated confirmatory significance under repeated observations, nor does a large sample make a small coefficient important. A dependence-aware significance test for rho was not performed; confirmatory significance is unestablished, not disproved.

Within-context distribution: 3,571 contexts with at least ten observations and nonconstant variables; mean rho=0.26292983, median=0.26009067; 3,177 positive coefficients. These are descriptive correlations, not combined p-values or a single adjusted correlation. The within-context summary includes 456,415 rows and 119,550,125 orders, excluding 26 contexts, 133 rows and 7,360 orders. Global Spearman retains all observations.

Constant/insufficient paired inputs return an unavailable result with a reason, not a fabricated zero. Correlation does not establish a causal relationship.

## Discount and other-channel overlap

Global signed-discount summaries:

| Flag/state | n | Mean discount | Median | Q1 | Q3 | Other flag present |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| email/0 | 419,498 | 4.1068% | 0.0000% | -0.1721% | 0.6628% | 7.3002% |
| email/1 | 37,050 | 23.9789% | 24.2413% | 16.3213% | 33.1000% | 51.9055% |
| homepage/0 | 406,693 | 4.3748% | 0.0000% | -0.1613% | 0.6693% | 4.3814% |
| homepage/1 | 49,855 | 16.6892% | 16.8732% | 0.8128% | 28.3273% | 38.5739% |

Overlap persists within the eligible binary-comparison scope: email-flagged discount averages 24.1451% versus 4.0501%; homepage-flagged averages 16.6996% versus 4.4354%. These are pooled row discount means, not an adjusted price effect.

The 19,231 both-flag observations represent 51.9055% of email records and 38.5739% of homepage records. Larger discounts and joint marketing co-occur, so promotion associations may partly reflect pricing and combined conditions. The data/design do not identify how much belongs to discount, channel selection, time or other factors.

## Limitations and reproduction

No randomized assignment, real calendar dates, availability roster, costs/margins or reliable zero-demand indicators are supplied. Missing observations, changing assortment, selective promotions, retained extremes, repeated series and shared weeks limit interpretation. Minimum counts and block sensitivity do not prove independence or full dependence capture. Do not generalize restricted-context estimates to unsupported contexts or infer safety stock, campaign ROI or causation. All 116,101 negative discounts were retained and source hashes remained unchanged.

Run `./.venv/Scripts/python.exe docs/run_analysis_notebook.py --phase 8`, `./.venv/Scripts/python.exe -m unittest discover -s tests -v`, and `./.venv/Scripts/python.exe docs/validate_phase8.py`. Core logic: [promotions.py](../src/statistics/promotions.py). Actual validation: [independent results](phase8_validation.json), [notebook results](phase8_notebook_validation.json), and [progress](phase8_progress.md). Aggregate machine-readable results live under ignored `data/processed/phase8/promotion_results.json`.

API references: [SciPy Mann–Whitney](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html) and [SciPy Spearman](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html). SciPy 1.17.1 was actually used and tested. No Phase 9 implementation, raw-data alteration, commit or push occurred.
