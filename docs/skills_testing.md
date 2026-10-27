# Custom skill trigger testing

Date: 2026-10-27 (Asia/Hebron). Phase 4 only.

## Method and evidence

Ran one positive and one unrelated negative test for each of the two custom skills. An independent Codex subagent, without the parent conversation or an expected-answer key, first read only the candidates’ YAML names/descriptions (plus the project safety instructions). It recorded routing for all four prompts before reading selected skill bodies. It then read the selected instructions and returned bounded responses. The parent compared the observed selections and responses with the criteria below after the run.

This is an actual, manually routed behavioral test, not host automatic-activation telemetry, a statistical analysis, or a general routing benchmark. No live dataset was read by the evaluator. Positive tests deliberately requested a method outline or a supplied synthetic example so Phase 5 and later work would not begin. The evaluator wrote only the evidence JSON.

Full exact prompts, routing reasons, responses and limitations are preserved in [the unedited evaluator record](phase4_trigger_observations.json). The evaluator did not assign pass/fail; the parent reviewed the actual outcomes below.

## Results

| Case | Custom skill | Test | Observed selection | Result |
| --- | --- | --- | --- | --- |
| P1 | `promotion-impact-analysis` | Positive | promotion-impact-analysis | PASS |
| P2 | `promotion-impact-analysis` | Negative | Neither custom skill | PASS |
| P3 | `client-insight-reporting` | Positive | client-insight-reporting | PASS |
| P4 | `client-insight-reporting` | Negative | Neither custom skill | PASS |

### P1: promotion-impact-analysis, positive test

**Exact prompt:**

> Outline how you would assess whether email promotions and homepage featuring are associated with higher num_orders in this meal-delivery dataset, accounting for discounts and center-meal context. This is a methodology-only skill test: do not load data, compute actual results, or advance project phases.

**Expected behavior:** Select promotion-impact-analysis and return a center-meal-aware methodology, without performing analysis or inventing findings.

**Actual observed behavior:** Selected only promotion-impact-analysis. Produced a plan covering within-center-meal comparisons, both promotion states, sample/series counts and coverage, mean/median/IQR, consistent percentage denominators, conditional Mann–Whitney U, within-context Spearman, discounts/other-flag confounding, separate statistical/business interpretation, and limitations. It explicitly treated all numerical outputs as future requirements and did not read raw data.

**Pass/fail:** PASS.

**Notes:** Manual metadata routing, not automatic host activation evidence. Methodology only; no empirical assumption checks, results or operational recommendation were produced.

### P2: promotion-impact-analysis, negative test

**Exact prompt:**

> List the repository directories intended for notebooks, reusable Python code, and final figures. Do not create or change anything.

**Expected behavior:** Do not select the promotion skill for a repository-directory lookup; answer directly without mutations.

**Actual observed behavior:** Selected neither custom skill. Returned the notebook, src subdirectories, and final-figure locations from instructions. Did not create directories or claim an existence check.

**Pass/fail:** PASS.

**Notes:** Locations were read from instructions; directory existence was not inspected. No custom skill was selected.

### P3: client-insight-reporting, positive test

**Exact prompt:**

> Write one client-facing insight and chart takeaway from this supplied synthetic verified summary only: for the same meal at the same center over a fictional comparison window, 120 promoted observations averaged 200 orders and 180 non-promoted observations averaged 160 orders. The analyst notes discounts co-occurred with promotions and has not supplied an inferential test. Explain what a purchasing manager could do next, which KPI to monitor, and the caveat. Do not run new analysis or write a real client report.

**Expected behavior:** Select client-insight-reporting and translate the supplied synthetic evidence into an insight, action, KPI, caveat and chart takeaway without new analysis.

**Actual observed behavior:** Selected only client-insight-reporting. Kept the supplied 200 versus 160 average orders and 120 versus 180 observations tied to the fictional window and center-meal. Explained purchasing relevance, proposed a review with marketing, specified weekly average-orders monitoring by promotion/discount status, retained the discount-confounding and absent-inference caveats, and supplied a finding-oriented chart takeaway with synthetic source context. It did not recommend a safety-stock quantity or claim achieved waste/stockout reduction.

**Pass/fail:** PASS.

**Notes:** Synthetic supplied evidence only; no inference, additional analysis or real client report. No variability or waste/stockout measurements were supplied, so no inventory quantity or achieved inventory benefit is claimed.

### P4: client-insight-reporting, negative test

**Exact prompt:**

> Explain the purpose of .gitignore and whether raw project CSVs belong in version control. Do not edit files.

**Expected behavior:** Do not select the reporting skill for Git exclusion guidance; answer directly without editing or claiming a live Git audit.

**Actual observed behavior:** Selected neither custom skill. Explained exclusion of untracked raw/processed data and the already-tracked-file limitation. Made no edits and did not claim it inspected current Git state.

**Pass/fail:** PASS.

**Notes:** Current .gitignore contents and Git tracking state were not inspected. No custom skill was selected.

## Behavioral review

- Promotion positive test: required evidence/design elements appeared in the returned outline, including the repeated-week independence caveat. It did not invent p-values, correlations, effects or sample counts from the project data.
- Reporting positive test: all seven required insight components were present. The only counts and means came from the clearly synthetic prompt; no significance or achieved business benefit was claimed. The caption identified population, sample sizes, source and confounding.
- Negative tests: both tasks were answered without selecting either custom skill. This demonstrates relevance discrimination on these prompts, rather than forced invocation.
- Cross-skill routing: the methods prompt did not select client reporting, and the client rewrite did not select promotion analysis. This reduces duplication between the two custom roles.

## Structural and scope validation

Ran the skill-creator validator for both folders:

```powershell
python <skill-creator>/scripts/quick_validate.py .github/skills/promotion-impact-analysis
python <skill-creator>/scripts/quick_validate.py .github/skills/client-insight-reporting
```

Both returned `Skill is valid!` with exit code 0. `<skill-creator>` refers to the installed system skill directory read for this task; its `quick_validate.py` uses the already-available PyYAML tooling. No project dependency was added.

Also verified exactly two custom SKILL.md files at the requested locations, valid project-rule/inventory links, unchanged hashes for all four raw CSVs, and all 32 installed upstream skill files unchanged against the Phase 3 source manifest. Neither custom skill duplicates those upstream definitions. AGENTS.md links the two custom definitions for explicit project routing without additional copies in `.agents/skills/`.

## Limits and follow-up

All four required test cases passed. A single evaluator and four prompts do not establish universal routing accuracy, prove automatic host discovery from `.github/skills/`, or validate future statistical computations and client reports. No later-phase analytical claims are made. Re-run behavioral checks after changes to names, descriptions, or instructions, and use the skills on actual authorized work in their later phases.

No raw dataset was modified, no Phase 5 preparation was performed, and no commit or push occurred.
