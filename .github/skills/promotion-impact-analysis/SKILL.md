---
name: promotion-impact-analysis
description: Analyze or plan comparisons of email promotions, homepage featuring, and discounts against weekly meal demand in this food-demand-analysis project, accounting for center-meal context and observational limits. Use for promotion-effect methods or evidence, not generic EDA, ML implementation, repository setup, or rewriting already-verified client findings.
---

# Promotion impact analysis

## Scope and project inputs

Use this skill for `emailer_for_promotion`, `homepage_featured`, discount, and `num_orders` comparisons. It supplies project-specific analytical decisions; it does not replace the installed EDA tools, scikit-learn guidance, or the client-insight-reporting skill.

Read [project rules](../../instructions/project-rules.md) and [the data inventory](../../../docs/data_inventory.md). A demand observation is one (`week`, `center_id`, `meal_id`). Historical `train.csv` contains `num_orders` for weeks 1–145; future `test.csv` has no target and cannot establish observed promotion effects. Treat center and meal IDs as categories. Lookups can supply meal/category/cuisine and center attributes when an authorized preparation phase has validated their joins.

Stay within the authorized phase. For a methodology request or skill test, return a proposed approach without loading or joining raw data, running tests on it, or inventing results. Raw datasets remain unchanged. Do not start cleaning or analysis merely because this skill is relevant.

## Comparisons and evidence

1. State the question, population, time window, observational unit, and comparison statistic before examining significance. Use the same meal within the same center where both promotion states are observed. Identify and count series lacking a comparison state rather than silently dropping them. A global comparison may be descriptive context, but it is not an adjusted promotion estimate.
2. Separate promotion and non-promotion observations for each flag. Report both observation counts and center-meal series counts, comparable-series coverage, and exclusions. Describe how series enter any pooled summary and whether series or observations receive equal weight; do not let high-volume groups implicitly define an unexplained effect.
3. Compare central tendency with mean and median plus a spread measure suited to skewed demand, such as IQR. Report the absolute difference and percentage difference using the same stated statistic and population: `100 × (promotion_statistic - nonpromotion_statistic) / nonpromotion_statistic`. If the reference is zero or unavailable, report the percentage as unavailable and retain the absolute difference. Do not call a median difference a mean lift or an unadjusted difference a matched effect.
4. Consider Mann–Whitney U for independent promotion/non-promotion samples when rank-based comparison is appropriate for skewed demand. Repeated weeks within a center-meal series can violate independence; assess temporal dependence and the actual comparison design before reporting a p-value. Do not mechanically apply an independent-sample test to matched pairs or interpret Mann–Whitney as a median test unless distributional-shape conditions support that reading. If assumptions are not defensible, label inference unavailable or use an explicitly justified dependence-aware approach. Describe uncertainty, the significance criterion, and any multiple-comparison handling. Never infer significance from a large-looking difference.
5. Calculate discount as `(base_price - checkout_price) / base_price` only for valid positive base prices. Retain and flag negative discounts rather than clipping or removing checkout-above-base rows. State the valid observation count. Use Spearman correlation for discount versus demand where enough nonconstant paired values exist; check within center-meal context, disclose any pooling, and assess repeated-observation dependence before inferential interpretation. Constants or insufficient observations produce an unavailable result with a reason, not a fabricated zero correlation.
6. Check promotion/discount confounding: compare discount distributions across promotion states and examine overlap with the other marketing flag. When sample sizes support it, distinguish neither, email only, homepage only, and both. Explain sparse groups and remaining time, price, selection, and availability differences. Do not attribute combined marketing associations solely to email or the homepage.
7. Report statistical significance separately from business effect. Explain the magnitude in orders and percentage terms, population coverage, uncertainty, and operational relevance. Label observed differences as associations; observational evidence does not show that promotion alone caused demand changes. State limitations including repeated observations, confounding, coverage, and unknown calendar dates.

## Output contract

For completed authorized analysis, return: question and comparison design; sample/series counts and coverage; demand summaries; absolute and percentage difference with denominator; discount/other-promotion overlap; method, assumptions and uncertainty; separate business interpretation; limitations; and reproducible code/output references. Use only executed results. For a plan-only request, mark these as required outputs to obtain, not completed findings.

Pass verified evidence to client-insight-reporting only when a client-facing write-up is requested. Do not create a recommendation or causal claim unsupported by the evidence.
