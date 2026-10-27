# Food Demand Analysis: agent instructions

## Scope and instruction map

Read this file, [project rules](.github/instructions/project-rules.md), and the authorized phase of [the implementation plan](FOOD_DEMAND_ANALYSIS_IMPLEMENTATION_PLAN.md) before working. The project rules are mandatory across this repository; this file supplies project context and the working workflow, while the rules file owns the detailed safeguards. Follow the user's authorized scope and stop at its phase boundary. Writing instructions for future work does not authorize implementing it.

## Client and objective

The client is a meal-delivery company operating through multiple fulfilment centers. Weekly purchasing relies heavily on managerial judgment, creating possible waste in some centers and stockouts in others. Marketing can send promotional emails, feature meals on the homepage, and change prices or discounts. Analyze demand patterns to improve weekly purchasing and inventory planning. Forecasting is a core project component when its phase is authorized.

## Core analytical questions

1. How does total demand change week to week?
2. Which categories and meals generate most demand?
3. Which centers perform best, and does center type matter?
4. Are email promotions and homepage featuring associated with higher demand, and by how much?
5. What is the relationship between discount and demand?
6. Which meals have volatile demand and may need larger safety stock?
7. Can future demand be forecast more accurately than a simple previous-week baseline?

## Verified data context

Use [the Phase 1 inventory](docs/data_inventory.md) as the authoritative inspected schema and source-hash record. Reproduce inspection with `python docs/inspect_phase1.py` (Python 3 standard library only). These are observed file dimensions, excluding headers:

| File under `data/raw/` | Rows | Columns | Role |
| --- | ---: | ---: | --- |
| `train.csv` | 456,548 | 9 | Demand observations for weeks 1–145, including `num_orders` |
| `test.csv` | 32,573 | 8 | Prediction inputs for weeks 146–155, without `num_orders` |
| `meal_info.csv` | 51 | 3 | Meal lookup: `meal_id`, `category`, `cuisine` |
| `fulfilment_center_info.csv` | 77 | 5 | Center lookup: `center_id`, `city_code`, `region_code`, `center_type`, `op_area` |

The eight shared demand columns are `id`, `week`, `center_id`, `meal_id`, `checkout_price`, `base_price`, `emailer_for_promotion`, and `homepage_featured`, in that order. They match in inferred type. IDs, week, promotion flags, location codes, and orders are integer-formatted; price fields and `op_area` are decimal numeric; category, cuisine, and center type are text. Codes and identifiers are labels, not continuous measurements.

`id` is unique in each demand file and disjoint across train/test. (`week`, `center_id`, `meal_id`) is unique within each demand file. Lookup primary keys are `meal_id` and `center_id`; all observed demand references resolve to them. Both demand files cover 51 meals and 77 centers. Phase 1 found no missing cells, malformed records, or invalid numeric values, but this is not a guarantee for future inputs or a completed cleaning audit.

Checkout exceeds base price in 116,101 training rows and 8,937 test rows. Test price maxima exceed training maxima. Preserve these observations for later investigation under Rule A. Week numbers are not calendar dates; currency, operating-area units, real location identities, and the meaning of absent series observations are not established by the files.

## Mandatory working behavior

- **Data integrity:** apply Rule A before any data operation. Use raw files as read-only inputs and place derived datasets in ignored `data/processed/`. Recheck the inventory assumptions instead of treating them as permanent guarantees.
- **Reproducibility and code quality:** apply Rule E. Keep reusable, narrowly scoped functions under the relevant `src/` subdirectory and narrative exploration in notebooks. Prefer project-relative paths, explicit configuration, clear names, docstrings for non-obvious behavior, and explicit validation failures. Avoid hidden notebook state, absolute user-machine paths in project code, and unnecessary frameworks.
- **Statistical claims and reporting:** apply Rule B. Separate observed facts, statistical evidence, interpretation, recommendations, and limitations. Keep technical methods, AI-tool documentation, and test results in technical documentation; write client outputs in plain language.
- **Visualization:** apply Rule D to every final figure. Chart conclusions must come from executed analysis.
- **Machine learning and leakage prevention:** apply Rule C before constructing features or evaluating forecasts. Preserve identifiers for future test predictions; do not use them as arbitrary numerical predictors.
- **Testing:** apply Rule F to the authorized change. Do not claim a notebook, test suite, or dashboard passed until it actually ran.
- **Documentation:** maintain the current phase's progress and validation record. Keep numerical claims linked to reproducible outputs. Record cleaning decisions only after investigation; document AI tools and skills only when actually used. Do not invent future-phase metrics, findings, or test outcomes.

## Phase workflow and project locations

Inspect existing files first, implement only the authorized phase plus necessary support, run relevant validation, fix failures, and record actual outcomes before reporting completion. If a blocker prevents completion, record it explicitly. Do not continue to the next phase without user authorization.

Use `src/data_processing/`, `src/analysis/`, `src/statistics/`, and `src/machine_learning/` for reusable code as those phases are authorized. Later planned outputs include `notebooks/analysis.ipynb`, `notebooks/machine_learning.ipynb`, `reports/figures/`, `dashboard/`, `reports/`, and `presentation/`. Reserve `.github/skills/` for the later skill phases; do not create or test skills during Phase 2.

Current dependencies remain in `requirements.txt`; only add packages when the authorized implementation needs them. Phase 1 and Phase 2 require no third-party Python packages. Run commands from the repository root and document exact commands with results. Do not commit or push unless the user authorizes it.

## Installed existing skills (Phase 3)

Two existing skills are installed locally for Codex discovery. Read the relevant skill's SKILL.md before using it in an authorized phase. Project rules and the user's phase boundary take precedence over generic examples.

- [exploratory-data-analysis](.agents/skills/exploratory-data-analysis/SKILL.md): bounded CSV inspection and EDA diagnostics for Phases 5–6. Explicitly disclose scan limits and preserve raw data.
- [scikit-learn](.agents/skills/scikit-learn/SKILL.md): regression, preprocessing pipelines, and evaluation support for Phases 10–11. Adapt examples to week-based chronological validation and MAE.

See [Find Skills documentation](docs/find_skills.md) for sources, pinned provenance, project adaptations, actual usage, and validation limits. Upstream files remain unchanged. These are the two existing skills, not the Phase 4 custom promotion-analysis and client-reporting skills. Skill installation does not authorize later phases.

## Custom project skills (Phase 4)

For applicable requests, read the named SKILL.md before proceeding. These two canonical definitions live in `.github/skills/`; do not copy or replace the installed existing skills. The links provide explicit project routing for agents that do not automatically discover this directory.

- [promotion-impact-analysis](.github/skills/promotion-impact-analysis/SKILL.md): use for analysis or methodology of email/homepage promotion, discounts, and observed demand within center-meal context. Do not use for repository setup, generic EDA, ML implementation, or rewriting already-verified client findings.
- [client-insight-reporting](.github/skills/client-insight-reporting/SKILL.md): use to translate verified food-demand findings into client-facing insights, recommendations, or chart takeaways. Do not use for computing promotion effects, statistical/ML implementation, generic EDA, or repository setup.

Choose based on the requested task; unrelated prompts need neither skill. Read both only when a request actually spans analysis and client communication and both are authorized. A methodology or synthetic skill test does not authorize raw-data work or a later implementation phase. See [skill testing](docs/skills_testing.md) for the actual routing checks and their limits.
