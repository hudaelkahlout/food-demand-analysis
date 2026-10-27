# Find Skills: Phase 3 selection and verification

Date: 2026-10-27 (Asia/Hebron). Exactly **two existing project skills** selected and installed. The Phase 4 custom skills had not been created at this Phase 3 snapshot; their subsequent creation is recorded in [Phase 4 progress](phase4_progress.md).

## Discovery method and actual searches

Used the official [Find Skills workflow](https://github.com/vercel-labs/skills/blob/main/skills/find-skills/SKILL.md), read from its upstream source because it was not installed locally. Reviewed the [skills.sh leaderboard](https://skills.sh/) first, then executed the workflow's CLI searches with Skills CLI **1.5.18**:

```powershell
npx.cmd --yes skills find data-validation
npx.cmd --yes skills find scikit-learn
npx.cmd --yes skills find exploratory-data-analysis
npx.cmd --yes skills find forecasting
```

All four searches completed successfully. Find Skills was the discovery workflow, not a third selected project skill. Search counts below are approximate registry displays observed during this run, not measures of correctness. Inspected the selected upstream SKILL.md files and relevant references rather than selecting solely by popularity. GitHub showed approximately 54.8K stars for the public, non-archived K-Dense source repository.

## Relevant candidates considered

| Candidate | Source | Observed installs | Decision |
| --- | --- | ---: | --- |
| `exploratory-data-analysis` | K-Dense-AI/scientific-agent-skills | 2.2K | Selected: first-party source within this suite, bounded standard-library CSV tools, documentation and reusable references |
| `scikit-learn` | K-Dense-AI/scientific-agent-skills | 2.2K | Selected: directly supports the plan's regression algorithms, preprocessing and evaluation |
| `exploratory-data-analysis` | davila7/claude-code-templates | 1.9K | Not selected: would duplicate the selected EDA role; reviewed search result only |
| `data-validation` | anthropics/knowledge-work-plugins | 256 | Considered for QA; selected EDA provides a more direct executable CSV-inspection path; reviewed registry overview |
| `scikit-learn-best-practices` | mindrally/skills | 890 | Alternative ML guidance; selected the more widely installed suite with its inspected pipeline and evaluation references; reviewed search result only |
| `statsmodels` | K-Dense-AI/scientific-agent-skills | 2.1K | Relevant forecasting alternative, but scikit-learn fits the required Linear Regression and Random Forest scope more directly; reviewed search result only |
| `inventory-demand-planning` | affaan-m/ecc | 9.9K | Relevant domain candidate, but selected the two technical foundations most directly tied to the current implementation plan; reviewed search result only |
| `statistical-analysis` | K-Dense-AI/scientific-agent-skills | 2.3K | Found in the registry overview; not selected because its hypothesis-test/reporting scope overlaps more with planned promotion-impact analysis |

No rejected candidate was installed or claimed to have been used.

## Selected skill 1: exploratory-data-analysis

- **Skill name/version:** `exploratory-data-analysis`, upstream metadata version 1.4.
- **Source:** [upstream skill](https://github.com/K-Dense-AI/scientific-agent-skills/tree/5f2bc0341354fd5590aef76a533ada1e1e5b4e62/skills/exploratory-data-analysis), discovered through [its registry entry](https://skills.sh/k-dense-ai/scientific-agent-skills/exploratory-data-analysis).
- **Purpose:** bounded local file inspection, schema profiles, missingness and leakage diagnostics, distribution/outlier sensitivity, and reporting scaffolds. Core CSV tools use Python's standard library.
- **Why selected:** provides executable inspection and diagnostic utilities for the four supplied CSVs, preserves raw inputs, distinguishes missing observations from zero, and exposes scan limits. It complements the custom promotion-analysis skill's domain comparisons and the client-reporting skill's business communication.
- **Where it will be used:** Phase 5 data-quality audit and Phase 6 EDA, with later diagnostic support as warranted. It does not replace project-specific key checks, merge conservation checks, or the eventual statistical analysis.
- **Availability:** installed as an unchanged upstream copy at `.agents/skills/exploratory-data-analysis/`, including SKILL.md, all references, scripts, and template assets (21 files). Codex discovery verified by the Skills CLI.
- **Project configuration:** declare the project root explicitly. Train has 456,548 rows, so a future full scan must explicitly raise the default 100,000-row cap, for example to 500,000. A bounded prefix is not a full-data audit. Match explicit missing-token settings to the inventory's documented policy. Use sequential week numbers directly in project-specific temporal checks; do not reinterpret them as calendar dates for the generic date parser. Interpret repeated center-meal observations and any cross-split entity flags using the forecast horizon; recurring entities alone do not prove leakage.
- **Actual Phase 3 use/observed benefit:** read the workflow, ran its manifest and profile tools on a temporary three-row synthetic CSV, verified a two-row cap is disclosed, and verified an out-of-root input is rejected. The run demonstrated functioning local, read-only inspection and explicit truncation. No project EDA or raw-data profile was run in Phase 3.

## Selected skill 2: scikit-learn

- **Skill name/version:** `scikit-learn`, upstream metadata version 1.5; guidance targets scikit-learn 1.9.1 on Python 3.11+.
- **Source:** [upstream skill](https://github.com/K-Dense-AI/scientific-agent-skills/tree/5f2bc0341354fd5590aef76a533ada1e1e5b4e62/skills/scikit-learn), discovered through [its registry entry](https://skills.sh/k-dense-ai/scientific-agent-skills/scikit-learn).
- **Purpose:** classical ML algorithms, preprocessing, compositional pipelines, model evaluation and tuning guidance, with reference material and illustrative scripts.
- **Why selected:** directly supports the mandatory Linear Regression and Random Forest models, mixed categorical/numeric fields, and MAE evaluation. It fills the ML implementation role, separate from promotion inference and client insight writing.
- **Where it will be used:** Phase 10 forecasting implementation and Phase 11 ML validation when authorized. Relevant references cover supervised learning, preprocessing, pipelines, and evaluation.
- **Availability:** installed as an unchanged upstream copy at `.agents/skills/scikit-learn/`, including SKILL.md, all references and example scripts (11 files). Codex discovery verified by the Skills CLI.
- **Project configuration:** use regression estimators and MAE, not the guide's illustrative classification metrics. Keep preprocessing inside the fitted pipeline. Replace random/stratified example splits with chronological **week-based** splits: fit initially on weeks 1–135 and hold out 136–145. Inner folds must keep all records for a week on the same side; generic row-index `TimeSeriesSplit` is not by itself sufficient for this panel. Include only information available at each prediction origin, handle unseen categories, and preserve the mandatory previous-week baseline. Project rules override generic examples.
- **Actual Phase 3 use/observed benefit:** read the skill and pipeline reference, located the LinearRegression, RandomForestRegressor, TimeSeriesSplit and MAE references, and used them for the project-compatibility review above. This identified concrete adaptations needed to prevent inappropriate random splitting or row-level time folds. API verification is isolated and synthetic; no demand model was fitted or evaluated.
- **Runtime scope:** the bundled workspace Python initially lacked sklearn. The skill instructions and references are available without that package. Runtime API verification uses a separate temporary environment with scikit-learn 1.9.1, leaving project dependencies unchanged. Full example scripts needing pandas/matplotlib are retained but are not claimed as executed or validated. Add project ML dependencies only when Phase 10 is authorized and revalidate their APIs then.

## Installation and provenance

The Skills CLI could not install a raw commit SHA as a branch. A default-branch clone was then stopped because the large repository download stalled. No project skill installation succeeded during those attempts.

Resolved upstream revision with `git ls-remote ... refs/heads/main`: **5f2bc0341354fd5590aef76a533ada1e1e5b4e62**. Downloaded only the two selected folders plus the repository license from that fixed revision into OS temporary staging. Verified each downloaded file's Git blob SHA against the upstream tree, then installed the local staging directory using the Find Skills workflow's own CLI:

```powershell
npx.cmd --yes skills add <temporary-staging-directory> --skill exploratory-data-analysis scikit-learn --agent codex --copy --yes
npx.cmd --yes skills list --agent codex
```

Both commands succeeded. Exactly two skills were copied into project-local `.agents/skills/`; no global skill installation occurred. This standard project discovery location is linked from AGENTS.md. `.github/skills/` remains reserved for the two future custom skills.

The installer generated `skills-lock.json` with the actual local staging source and content hashes. Its staging path is historical and is not a portable upstream address. Portable provenance is recorded separately in [the source manifest](phase3_skill_sources.json): canonical repository, pinned revision, upstream paths, Git blob IDs, and SHA-256 for all 32 skill files plus the license. Existing copies can be used directly without the staging directory. To reinstall the same revision, retrieve those recorded paths from the pinned source, verify the recorded hashes, then rerun the local installation command above. Do not use an unreviewed update as an equivalent reproduction.

Retained the upstream [repository license](third_party/scientific-agent-skills_LICENSE.md). SKILL.md files also retain their upstream license metadata (EDA: MIT; scikit-learn: BSD-3-Clause). Upstream skill files were not rewritten into project-specific custom skills.

Discovery initially encountered npm's offline-cache restriction; network-enabled retry succeeded. CLI `add --help` without a source returned its missing-source usage error and did not install anything. These discovery/installation issues were resolved before completion.

## Verification and limits

See [Phase 3 progress](phase3_progress.md) and [machine-readable validation](phase3_validation.json). Reproduce structural and synthetic EDA checks with:

```powershell
python docs/validate_phase3_skills.py
```

To include the isolated scikit-learn API check, create a temporary environment, install the documented package version there, and pass its Python path:

```powershell
python -m venv <temporary-venv>
<temporary-venv>/Scripts/python.exe -m pip install scikit-learn==1.9.1
python docs/validate_phase3_skills.py --runtime-python <temporary-venv>/Scripts/python.exe
```

The validation checks installation count, upstream hashes, skill metadata, local links, script syntax, EDA operation on synthetic fixtures, ML references, source-data hashes, and absence of Phase 4 custom skills. The optional API check imports the relevant ML components, constructs unfitted estimators, exercises a tiny chronological split and deterministic MAE arithmetic, and performs no model fitting. These checks establish availability and basic usability, not the correctness of future project analyses or every optional skill capability.

The two selected skills must actually be invoked again for their appropriate tasks when those phases are authorized. No later-phase benefit, forecasting accuracy, statistical result, or custom-skill trigger test is claimed here. No datasets were modified, committed, or pushed.

## Upstream attribution

The source requests attribution when it contributes to reports or code. Added this reference after checking the current arXiv record (v2, revised 2026-09-02; no publisher DOI listed): Kassis, T., Agarwal, V., He, Y., Patel, D., and Brueckner, A. M. (2026). *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. [arXiv / DOI](https://doi.org/10.48550/arXiv.2609.00065).

Phase 4 compatibility note: the installed-skill validation command now permits later custom-skill artifacts by default. Use its optional --phase3-snapshot flag only when reproducing the original pre-Phase-4 boundary; it intentionally fails once Phase 4 artifacts exist.

## Actual use update: Phase 5

The installed exploratory-data-analysis skill was used on the real source files during the authorized preparation audit: four capability manifests, four complete CSV profiles with a 500,000-row cap and explicit missing-token settings, and one training-order sensitivity report. All row scans were complete. The sensitivity numerical summaries used 4,096 values and were kept distinct from the exact full-data IQR counts computed by project preparation code. No transformation or automatic deletion was applied. See [cleaning decisions](cleaning_decisions.md), [actual audit and tool commands](phase5_audit.json), and [Phase 5 progress](phase5_progress.md). The scikit-learn skill was not invoked for Phase 5; no model was run.


## Actual use update: Phase 6

Used exploratory-data-analysis on the validated enriched analytical file: a capability manifest followed by a complete 456,548-row profile with a 500,000-row cap, executed in `notebooks/analysis.ipynb`. Applied its observation-unit, bounded-scan, missing-vs-zero and noncausal-interpretation guidance. All business aggregates were computed from full data by project code, not the skill's bounded numerical samples. Exact commands and outputs are in ignored `data/processed/phase6/`. See [Phase 6 progress](phase6_progress.md) for actual findings and validation. No promotion inference, client-report writing, or scikit-learn usage occurred in Phase 6.

## Actual use update: Phase 10

Read `scikit-learn/SKILL.md` and `references/pipelines_and_composition.md` before implementing forecasting. Applied `Pipeline` + `ColumnTransformer`, training-only median imputation/scaling, one-hot categorical encoding with unknown-category handling, `LinearRegression`, seeded `RandomForestRegressor`, and `mean_absolute_error`. Used the skill's train-only transformation and time-appropriate split guidance; adapted generic random-split examples to the mandatory final-ten-week fixed-origin recursive holdout. No random split, holdout tuning or Phase 11 enhancement was performed. Runtime uses scikit-learn 1.9.1. The upstream attribution above applies to this code contribution; no new bibliographic claims were introduced. Actual metrics and validation are recorded in [Phase 10 progress](phase10_progress.md).
