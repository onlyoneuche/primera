# Implementation status — 20 November 2026

## Current checkpoint

Repository setup and the full ML protocol have now run successfully in Docker. The original dataset, generated tables, eight figures, fitted pipeline, metadata, and run manifest exist. Two complete runs produced byte-identical contents for all 12 CSV outputs. The owner approved the ML results and Phase 2. The functional app is complete, with the complete test suite passing and real Chrome checks. The first Daybreak preview set is ready: 22 actual-app screenshots. **Await owner visual approval before further polish**, as required by BUILD_SPEC sections 9.2 and 14.

Work remains on `feature/ml-foundation`. Research artifacts were generated before the initial repository commit, so their manifest retains the authentic null commit and dirty status from that run. Git history records subsequent revisions. The owner has authorised pushing the current project to GitHub on this feature branch. No deployment has occurred. A clean-clone workflow has not been independently tested.

## Changes in this continuation

- Retrieved only the original Kaggle archive, preserved the CSV bytes, and recorded provenance in `data/source.json`.
- Inspected all 49 raw course labels (48 after stripping whitespace). Added literal Accounting and Marine science mappings; uncertain abbreviations remain explicitly low-confidence Other.
- Added Git to the development image for provenance and ignore-rule checks, with the explicit `/workspace` repository trusted for the non-root user.
- Added acceptance checks for complete shared outer folds, saved predictions matching reported metrics, manifest files, and all four sensitivity subsets.
- Generated all research outputs and the final logistic-regression pipeline; updated data notes and development documentation with observed evidence.

## Verification actually completed

| Check | Observed result |
| --- | --- |
| `make setup` | Development Docker image built with pinned direct dependencies and Git |
| `python3 -m scripts.fetch_data` with network permission | Downloaded and validated the original source |
| `make data` | Validated the existing original without modifying it |
| Targeted data/leakage pytest in Docker | 10 passed in 2.70 s |
| `make verify` | Two complete runs: 384.259 s and 368.568 s; all 12 CSVs identical |
| `make test` | 40 passed in 3.83 s against the first completed run |
| Final artifact/output pytest in Docker | 4 passed in 1.74 s against the second published run |
| `make check` | All 26 dependency-free checks passed |
| `docker compose config --quiet` | Passed |
| Figure review | All eight figures visually inspected; labels and layouts readable |
| Original Word-report SHA-256 | Still `8b6b5340f128d348fd0e9ae482f30417a25821c1694be8d05a698c9c0758c6d9` |
| Original build-spec SHA-256 | Still `442dfd06a4fa4e3a05875492b7603be6eacb15a4a6d331dce917c0cefb751db7` |

The former network/Docker restrictions were resolved by approved execution outside the sandbox. Earlier failures are historical, not current blockers. Python was 3.11.18; complete installed versions, source hashes, runtime, and provenance are in `outputs/run_manifest.json`. The native training alternative has not been independently verified. The Docker application builds, serves predictions, and reports healthy.

Exact targeted commands:

```sh
docker compose run --rm dev python -m pytest -q tests/test_data.py tests/test_pipeline_no_leakage.py
docker compose run --rm dev python -m pytest -q tests/test_artifact.py tests/test_research_outputs.py
```

## Research review

Use `outputs/RESULTS_SUMMARY.md` for the complete generated mean ± SD table, baselines, sensitivity results, explanation rankings, and threshold estimates.

- Random forest has the highest mean F1, 0.635 ± 0.123. All five candidates fall within its one-SD tie range. The fixed simplicity rule selects logistic regression, F1 0.585 ± 0.183, with modal parameters C=1 and l2 penalty.
- Ablation F1: all nine features 0.585 ± 0.183; without anxiety/panic 0.593 ± 0.200; without specialist 0.577 ± 0.171; without all three 0.565 ± 0.193. Differences are descriptive and small relative to fold variability.
- SHAP ranks marital status, anxiety, and faculty first. Held-out permutation importance ranks marital status, anxiety, and specialist first. SHAP is in-sample; neither establishes causation.
- Marital status has phi 0.596 with the target; anxiety and panic did not dominate the observed results. Each test fold has only seven positives. The small Malaysian self-report survey has no Nigerian or clinical validation.
- The threshold remains 0.5. Selected-model estimator predictions and this probability threshold agree for all saved out-of-fold predictions. Pooled threshold F1 differs from mean fold F1 because aggregation differs.

## Assumptions and remaining work

Retained assumptions to confirm: marital Yes/No means married/single; category-only results with hidden probabilities; threshold 0.5; approximate proportional CGPA conversion for 5.0-scale grades. Support contacts require personal verification before launch. See `docs/DECISIONS.md` and `docs/DATA_NOTES.md`.

1. ML results reviewed and functional web phase authorised by the owner.
2. Functional API/frontend, copy/config, API tests, and privacy tests completed.
3. First Daybreak preview set completed. Obtain owner visual review before further polish.
4. Complete browser/accessibility checks, production Docker startup/health/prediction checks, deployment instructions, and final report screenshots.
5. Keep deployment and Word report writing for their explicitly authorised later tasks. A production image build alone would not establish app readiness at this stage.

## Commands and Chapter 4 inputs

Review `outputs/RESULTS_SUMMARY.md`, `outputs/model_selection.md`, and `outputs/model_card.md` now. To reproduce or check:

```sh
make setup
make data
make train
make test
make verify
```

`make train` performs one full run. `make verify` performs two full runs, as already verified. `make run` now builds and starts the functional app on localhost. `make preview` captures and verifies the real app using the installed Chrome browser.

Chapter 4 inputs now available: `outputs/data_profile.md`, `outputs/course_grouping.csv`, `outputs/metrics_summary.csv`, `outputs/confusion_matrices.csv`, `outputs/model_selection.md`, `outputs/sensitivity_analysis.csv`, `outputs/shap_mean_abs.csv`, `outputs/permutation_importance.csv`, `outputs/threshold_tradeoffs.csv`, `outputs/figures/`, `outputs/model_card.md`, and `outputs/run_manifest.json`. Use the actual test evidence above. UI screenshots are pending. The Word report remains unchanged.

## Phase 2 verification — 20 November 2026

- `make test`: 104 passed in 3.94 s, with one dependency deprecation warning from Starlette/AnyIO.
- `make run`: runtime image built and localhost app started. `docker compose ps --format json` reports healthy, bound to 127.0.0.1:8000 only.
- `make check`: 26 passed; JavaScript syntax and Compose configuration checks passed.
- Real Chrome checks at 390×844 and 1280×800: keyboard-only nine-question completion, missing/invalid errors, CGPA scale conversion disclosure, both actual model result categories, result focus, restart clearing, age/year notes, modal Escape/focus restoration, and successful retry after deliberately stopping/restarting the server. No console errors were reported.
- Functional QA screenshots are in docs/design/previews/phase2/. They are implementation evidence, not final design or report screenshots. The extension does not expose browser storage globals to its read-only evaluator; the subsequent Playwright preview command verified those runtime assertions directly.

## Phase 3 first-preview checkpoint — 20 November 2026

- Implemented Daybreak with original SVG illustrations, self-hosted Bricolage Grotesque/Figtree WOFF2 fonts and OFL licences, warm risk labels, explicit selected checks, segmented progress, responsive layouts, and reduced-motion CSS.
- `make preview` generated all 22 required actual-app screenshots. It verified real lower/higher model responses, keyboard-only phone completion, back/restart behaviour, retry, result/dialog focus, coverage notes, prediction no-store, 48 px targets, and no horizontal overflow at both viewports.
- Browser privacy assertions passed: zero local/session storage keys, IndexedDB databases, cookies, third-party page requests, or JavaScript errors. See docs/design/previews/browser_checks.json for the browser version, viewports, and asset hashes.
- All 15 text/control colour contrast pairs passed. See docs/design/previews/contrast.md. Decorative illustration/progress colours are supplementary to textual information.
- All 22 screenshots were inspected. Capture reflow and retry-button spacing issues found during review were corrected. The complete index and self-review are in docs/design/previews/README.md.
- `make test` passed 105 tests in 3.81 s after the design/cache changes; one existing Starlette/AnyIO deprecation warning remains. No ML protocol, threshold, dataset, fitted model, or research result was changed.
- Remaining acceptance work after visual approval: automated axe audit, actual 200% browser zoom review, any owner-requested adjustments, final report screenshots, clean-checkout verification, and deployment instructions. No deployment or Word-report edit is authorised by this checkpoint.

Owner action: review the first-preview set and approve or request changes. Do not continue visual polish until this review is received. The goal remains incomplete while this checkpoint and later hardening work are outstanding.

Final preview consistency check: the existing Chrome tab initially retained old unversioned CSS/JavaScript. Added a public content fingerprint to asset/config URLs and static-response revalidation; a regression test verifies the fingerprint and response policy. The live Chrome tab now shows the same current design as the captured previews. The final preview command passed all 22 captures again, and asset hashes match the current files. The original Word checksum was rechecked and remains unchanged.
