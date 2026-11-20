# Agent guide

These instructions apply to this repository. Follow the user's current instructions first.

## Before changing code

- Read `docs/BUILD_SPEC.md`, including its approved amendments, and `docs/DECISIONS.md`. The current build spec takes precedence over the original Word proposal.
- Check `git status` and inspect the relevant implementation and tests. Preserve unrelated work; never reset or overwrite it.
- Consult `docs/IMPLEMENTATION_STATUS.md` for handoff context, then verify current capabilities. Earlier network or Docker failures are not permanent assumptions.
- Keep changes within the current phase. Record methodological choices and approved deviations in `docs/DECISIONS.md`.

## Project map

- `ml/`: immutable-source loading, shared feature mapping, pipelines, evaluation, selection, sensitivity, explanations, and generated reports.
- `config/`: shared configuration; future UI text and support contacts belong here.
- `app/`: future FastAPI backend and buildless HTML/CSS/JavaScript frontend.
- `tests/`: standard-library checks plus pytest data, leakage, determinism, and artifact tests.
- `outputs/` and `models/`: generated research evidence and fitted artifacts; intended to be committed.
- `local/`: private original documents and temporary working files; excluded from Git and Docker. Never persist check-in answers here.

## Commands and verification

Docker Compose is the primary environment; Python 3.11 is the application runtime.

| Task | Command |
| --- | --- |
| Build development environment | `make setup` |
| Obtain/validate the exact source | `make data` |
| Run the complete research protocol | `make train` |
| Run automated checks | `make test` |
| Run dependency-free checks | `make check` (host Python 3.9+) |
| Verify two complete numerical runs | `make verify` |
| Validate Compose without building | `docker compose config --quiet` |
| Build runtime image | `make docker` |

- Run checks appropriate to the change. Use targeted pytest tests for code changes, then broaden when needed. Documentation edits need link/command checks, not new tests.
- `make test` requires the real CSV, installed dependencies, and a trained artifact. A missing prerequisite is a blocker, not a passing or silently skipped acceptance test.
- `make check` does not establish ML correctness. Run `make verify` when research acceptance requires reproducibility; it is two full runs, not a quick smoke test.
- Verify startup, health, and prediction behaviour once the web phase exists. `make run` and `make preview` currently report readiness gaps; they are not implemented demos.

## Research invariants

- Never fabricate results, observations, citations, or verification claims. All research outputs must come from repository code run against the required real dataset. Synthetic fixtures are permitted only in tests.
- Never modify `data/raw/Student_Mental_health.csv`. Download only the specified original; stop and report schema/count mismatches rather than adapting silently.
- Fit every learned transform and tuning operation on training folds only, in one `imblearn.pipeline.Pipeline`. This includes rare-group frequencies and imputation.
- Preserve the approved order: categorical preparation/imputation → SMOTENC → faculty one-hot encoding → scaling → classifier. Share faculty mapping between training and inference.
- Preserve seed 42, all five models, both baselines, fixed grids, 5×10 outer CV, three-fold inner tuning, ablations, and the prespecified selection rule. Do not reduce the protocol to obtain better scores or shorter runtimes.
- Keep deployed threshold 0.5 unless the owner changes it. Distinguish `estimator.predict` comparison metrics from probability-threshold estimates, especially for SVC.
- Treat SHAP as in-sample model explanation and permutation importance as held-out evidence; neither proves causation. Do not claim significance from dependent folds.
- Generate tables/figures through code, retain provenance, and report actual runtime and installed versions. Do not hand-edit outputs to improve a finding.

## Application boundaries

- Build only the specified check-in flow. No accounts, database, answer history, analytics, or third-party runtime requests.
- Never persist or log submitted answers. Do not echo sensitive values in errors. Disable access logs and prevent prediction-response caching.
- Keep the frontend buildless and assets self-hosted. Use the shared config for user-facing copy and support contacts; never invent contact details.
- Use non-diagnostic, supportive wording and disclose the dataset's limitations. A higher-risk result must never use alarming or celebratory presentation.

## Handoff and checkpoints

- Keep the README lean; put implementation detail in `docs/`. Report what changed, checks actually run, blockers, and exact next commands.
- Leave the Word report unchanged until the report-writing task is requested.
- Report real ML results and wait for review before the web phase. Capture the first authentic UI preview set and obtain visual review before further polish, as specified in sections 14 and 9.2.
- Screenshots must show the actual app. Store final report images in `docs/screenshots/`; add README image links only after files exist and have been inspected. Do not substitute mockups for implementation evidence.
- Work on feature branches. Never push to `main` or deploy without the user's instruction. Do not expose private documents, secrets, or submitted student data in commits or screenshots.
