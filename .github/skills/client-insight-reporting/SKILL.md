---
name: client-insight-reporting
description: Turn supplied, verified food-demand-analysis findings into plain-language insights, recommendations, report sections, or chart takeaways for the meal-delivery client. Use when communicating established evidence to a non-technical audience, not when calculating promotion effects, running statistical or ML methods, performing generic EDA, or creating repository files.
---

# Client insight reporting

## Scope and evidence gate

Translate verified analytical outputs for the meal-delivery company's purchasing, marketing, and inventory decisions. This skill owns communication, not EDA, promotion testing, or model training. Use the other skills for those tasks only when separately authorized.

Read [project rules](../../instructions/project-rules.md) and use [the inventory](../../../docs/data_inventory.md) for field meanings and known limits. Respect the authorized phase: a skill test can use explicitly labeled synthetic supplied evidence, but must not create a real client report, load raw data, or launch later-phase analysis.

Before writing, identify the evidence source (executed code/output or a supplied verified summary), metric definition, comparison denominator, population, time window, and important caveats. Check that quantities use compatible units and aggregations. If required evidence is missing or contradictory, state what is unavailable and request the specific missing result; do not fill gaps with guessed numbers, new causal conclusions, or invented model/test results. Simple arithmetic derived from supplied values is allowed when its inputs and formula are recorded.

## Required insight components

For every important insight, communicate:

1. **Finding:** one precise conclusion tied to the observed population and time window.
2. **Supporting number:** the verified magnitude and comparison, including baseline/denominator and sample size when it affects interpretation. Keep its reproducible source identifiable in a source note or technical evidence record.
3. **Plain-language meaning:** what that number tells a planner, without unnecessary statistical jargon.
4. **Business implication:** the relevance to purchasing, waste/stockout risk, marketing, or forecast review. Label an implication as interpretation rather than another measured result.
5. **Recommended action where appropriate:** a practical step supported by the evidence. If evidence is insufficient, recommend further measurement or omit a business intervention rather than inventing certainty.
6. **KPI to monitor:** identify the measurement, population and review cadence that would assess the proposed action. Distinguish a proposed success target from an achieved result, and do not invent an arbitrary target when none is supported.
7. **Limitation/caveat:** the specific uncertainty that could change the decision. Include limitations in every report, even when an executive summary is short.

The seven components need not become seven repetitive headings in client prose. Use a short paragraph, compact table, or clearly labeled sections suited to the requested deliverable, while retaining all required information.

## Project-specific wording and charts

- Describe promotion and discount findings as associations. A small p-value is not proof of causation or a large business benefit; explain the measured difference and caveat in ordinary language. Do not upgrade a supplied observational result into an experiment.
- Call `checkout_price × num_orders` a revenue proxy, never profit. Do not invent currency. Do not label operating area with an unknown unit, decode anonymized location codes, or convert week indices into real dates or calendar seasons.
- For inventory implications, combine demand volume with volatility. CV alone does not establish a safety-stock quantity, and the available dataset does not directly measure waste or stockouts. Do not claim that an action already reduced either without evidence.
- Describe forecast MAE as the average absolute error in orders per evaluated observation at the documented horizon. State the comparison with the previous-week baseline only after evaluation has run. Do not claim accuracy on `test.csv`, which has no observed `num_orders`.
- Give every final chart a conclusion-oriented title supported by its actual values and a short conclusion/caption explaining what it shows. Keep axes, units, population and source/context clear, retain material caveats, and avoid misleading scales. When only a chart takeaway is requested, do not create a new chart or calculate new results.
- Put code, detailed statistical methodology, AI tooling, skill tests, and implementation validation in technical documentation. Client prose should explain evidence and decisions in simple language.

## Output check

Confirm every number is traceable, every proposed recommendation has evidence and a success KPI, chart text matches its source, and limitations remain visible. Clearly label synthetic examples and proposed actions. If only a plan or draft based on incomplete evidence is requested, state the missing inputs rather than presenting a final verified finding.
