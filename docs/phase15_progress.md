# Phase 15 progress — Arabic technical report

Date: 2026-10-27. Status: **Phase 15 fully complete.** Phase 16 has not been started. No commit or push performed.

## Completed checklist

- [x] Read the complete attached request, Phase 15 plan, AGENTS.md and project rules.
- [x] Review existing data-quality, KPI, statistical, inventory, forecasting, testing, skills, visualization and dashboard records alongside actual reusable source.
- [x] Create [the Arabic technical report](../reports/technical_report.md) with all 15 requested sections, without duplicating the client report verbatim.
- [x] Explain technical terms at first introduction, preserve code/file identifiers in code formatting, and use clean Markdown without RTL HTML wrappers.
- [x] Document exactly the implemented merge/retention policy, observed-week denominators, comparison populations, inference limits, inventory medians, fixed-origin recursion and train-only preprocessing.
- [x] Report validated model scores and winner, original-order test forecasts, historical tests/notebook runs and independent checks without claiming reruns.
- [x] Document only verified AI/tool/skill activity and its limited behavioral evidence; do not invent another assistant, human audit or productivity gain.
- [x] Link all six unchanged final figures and supporting project documentation; provide reproduction commands clearly labeled as instructions rather than executed work.
- [x] Validate numbers, methodology, source configuration, links and unchanged protected inputs; stop before Phase 16.

## Sections delivered

The report contains project overview; data sources/relationships; preparation/quality; exploratory analysis; KPI definitions; promotion/pricing methodology; volume/volatility; forecasting; testing/validation; six final figures; dashboard; AI-assisted workflow; reproduction; limitations; and technical conclusion.

Its content is for a technical evaluator, not a second business summary. It distinguishes pooled Mann–Whitney reference statistics from equally weighted context means, the serial-dependence limitation of IID p-values, first-order week-block uncertainty and its assumptions, and descriptive within-context correlations. It preserves negative discounts and observed-only populations, and explains why these do not establish causal campaign effects.

Forecasting describes exactly weeks 1–135 fitting and 136–145 fixed-origin recursive holdout, not a rolling evaluation consuming holdout actuals. It records the exact previous-week lookup/fallback, preceding-four-week available history, numeric/categorical pipeline, treatment of unavailable history, signed floating model discounts, prediction clipping before scoring, and refitting/forecast alignment. Rounded CV thresholds are identified as display values; exact saved cutoffs are used by the code. Forest configuration was checked directly from the source syntax tree against saved results.

## Numerical and methodology validation actually performed

Executed only bounded report validation:

```powershell
.venv/Scripts/python.exe -m docs.validate_phase15
```

Result: **passed**. [Machine-readable evidence](phase15_validation.json) records **115 source-claim entries** and **124 numerical occurrences** in report prose/tables, with display rounding and source paths. File/code literals and reproduction commands are treated separately from analytical numbers; forest parameters and the week-block seed/configuration are checked against source/results. Dataset dimensions, quality flags/gaps, KPIs, contrast samples/effects/U values/intervals, correlation summaries, quadrant counts, model rows/scores/clipping, historical test counts and dashboard acceptance counts match their recorded sources.

All **11** explicit methodology checks pass, covering fixed-origin target isolation, exact prior-week features, training-only pipelines, unseen categories, clipping, floating model discount arithmetic, pooled-not-paired U, nonconfirmatory reference p-values, first-order block resampling, manual skill routing and historical-not-rerun evidence. Manual review also covered cohort weighting, signed discount/revenue definitions, observed-center-week denominators, no missing-week zero filling, interpretation limitations and correspondence to the implementation.

Checked all 15 report headings, six figure links/hashes, other local documentation links, current code configuration, and unchanged installed skill source files. The AI workflow is grounded in `docs/find_skills.md`, source manifests, `docs/skills_testing.md` and original observed responses: two external skills, two custom skills, four bounded positive/negative cases. The report does not claim broad automatic activation, another AI product, universal independent human review or measured productivity gains.

Raw SHA-256 values match the original baseline. The pre-Phase-15 integrity snapshot confirms unchanged raw data, analytical source, tests, dashboard modules, notebooks, saved analytical/model outputs, final chart PNGs, client report and requirements. No analytical component or test was changed. No statistical/model analysis, full test suite, notebook execution or UI acceptance suite was rerun. The reported 66 automated test passes and 20 dashboard acceptance checks are previous actual evidence, explicitly identified as such.

## Deliverables and boundary

- `reports/technical_report.md` — requested concise Arabic technical report.
- `docs/validate_phase15.py` — saved-value/source/editorial verification, without analytical computation or fitting.
- `docs/phase15_validation.json` — actual source map, methodology results and integrity evidence.
- This progress record and README status/report links.

The local integrity snapshot is under ignored `data/processed/phase15/`. No package was added, no raw dataset was edited, and the Arabic client report remains unchanged. **Phase 16 remains unstarted. No commit or push.**
