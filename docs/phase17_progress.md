# Phase 17 progress — root README

Date: 2026-10-27. Status: **Phase 17 fully complete.** Phase 18 has not been started. No commit or push performed.

## Completed checklist

- [x] Read the Phase 17 requirements, user scope, project instructions and existing README/run guides.
- [x] Replace the accumulated English phase-by-phase README with one professional Arabic project entry point.
- [x] Include the business problem, dataset roles/counts, seven core questions, five validated headline findings, forecasting comparison, dashboard and project structure.
- [x] Provide setup, preparation/analysis, forecasting, figure/forecast validation, test-suite and dashboard commands, explicitly presented as reviewer instructions rather than commands executed in this phase.
- [x] Link client report, technical report, AI usage record, final figures, data inventory, testing report and dashboard guide.
- [x] Summarize confirmed ChatGPT planning, recorded Codex implementation, Find Skills discovery, both external and custom skills, and evidence-based safeguards; do not claim unsupported AI products.
- [x] Explain intentionally excluded raw/derived data, local data prerequisites, observed-only handling, noncausal marketing findings, unknown costs/currency and forecast uncertainty.
- [x] Review numbers, existing command targets, local links, phase boundary and pre-existing file hashes without rerunning any analytical/test/UI component.
- [x] Stop before Phase 18; do not commit or push.

## What changed

The root README is now organized around the reader's tasks rather than the sequence of past turns. It starts with a short business overview and prominent report/figure links, followed by five supported findings. A compact forecasting table preserves baseline MAE 119.613, Linear Regression 115.689, Random Forest 80.483 and 32.71% RF improvement. The time window and forecast/error unit remain explicit.

Removed obsolete statements that forecasting, final figures or the dashboard were unimplemented, and removed duplicated historical run instructions from the main entry point. The current analysis runner is documented with `--phase 9` because it executes the full present analysis notebook; old phase-boundary validators are not promoted as current acceptance commands. Full methodological detail remains in the reports and prior records, not copied into README.

Setup instructions target the verified Windows/PowerShell environment and give the equivalent virtual-environment interpreter path for Linux/macOS. Data must be supplied locally and derived outputs generated before the dashboard is used. Figure export/validation commands are separate from expensive fitting. Dashboard filters and the fixed scope of statistical comparisons/model metrics are summarized.

## Documentation validation

Reviewed stored Phase 5–10 outputs, Phase 11 test results, actual runner/parser/module paths, `requirements.txt`, `.gitignore`, the dashboard guide and AI usage record. Confirmed the five findings, dataset row counts, temporal windows and model scores agree with existing validated evidence. Historical test success is labeled as a prior result, not a new suite execution.

Checked all relative file/directory links, command file/module targets, requested AI/skill names, five headline rows, seven core questions, raw-data exclusion statement, current completion state and absence of unsupported AI usage claims. Read-only hashes confirm raw sources match their baseline and pre-existing code, tests, notebooks, dashboard, reports, figures, AI usage documentation and requirements remain unchanged.

No environment installation, data preparation, analysis, model fit, notebook, dashboard or test was run. No raw file was modified. `README.md` was rewritten and this progress record was created. Link review found the requested `docs/ai_usage.md` missing while the existing content was at `reports/ai_usage.md`; restored the required documentation path from that existing file without modifying or removing the report copy. No new AI usage claims were added; the temporary local integrity snapshot is under ignored `data/processed/phase17/`. **Phase 18 remains unstarted. No commit or push.**


## Resolved link discrepancy

The initial link audit found `docs/ai_usage.md` absent in the current workspace although the request and Phase 16 record identify that path. Existing `reports/ai_usage.md` contains the previously documented Arabic content. Restored a byte-identical copy to the explicitly requested `docs/ai_usage.md`, where its original relative evidence links resolve. Kept the pre-existing report file unchanged and did not move/delete it. This is a supporting documentation-path repair, not new analysis or a later-phase implementation.


Final documentation review passed: five headline findings, seven core questions, dataset/model/test values, all README/progress/restored-AI-document links and existing command targets match recorded sources. All protected file hashes and the four original raw-data hashes remain unchanged. Commands were inspected as text only; none were executed.


## User-requested English translation

After the initial Arabic delivery, the user requested an English version of the README. Translated the root file in place; the reports and other documents retain their original languages. Static comparison confirms all numerical values, link destinations and complete command blocks are unchanged. All local targets resolve. No analysis, notebook, model, dashboard or test was executed, and Phase 18 was not started.
