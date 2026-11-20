# Decisions

## 2026-11-20 — Approved by the owner

- Move the original build spec and Word proposal to Git-ignored `local/`; retain a tracked spec copy in `docs/`. Preserve the Word file unchanged for later writing.
- Keep generated research `outputs/` and model artifacts tracked, as specified. Use `local/` for private working files and temporary staging, never check-in answers.
- Obtain only MD Shariful Islam's original Kaggle Student Mental health dataset and validate its shape/counts; no substitute dataset.
- Change pipeline order to imputation/categorical preparation → SMOTENC → one-hot faculty encoding → scaling → classifier. SMOTENC before independent dummy columns prevents invalid category combinations. Everything remains in a single in-fold imblearn pipeline.

## 2026-11-20 — Implementation defaults

- Python 3.11 in Docker; pinned direct dependencies are selected for compatibility but cannot yet be called installed/tested. Shell DNS and Docker socket access were unavailable during implementation.
- Fit rare-faculty merging independently inside each training fold, rather than learning frequencies from the full dataset. The final pipeline retains the mapping fitted on all source rows; metadata exposes it to the future API.
- `Other` is the fallback bucket and may itself have fewer than five observations in a fold. Every retained named group must meet the five-row minimum. Do not invent a large Other group by reassigning an unrelated faculty.
- Fixed binary vocabularies, canonical faculty labels, and ordinal year/CGPA definitions do not learn from observations. Unknown course strings map to Other with low confidence; no fuzzy matching. Provisional abbreviation mappings must be reviewed against the downloaded source before research acceptance.
- SMOTENC uses at most five neighbours and further bounds that count using only the labels in its current training call. Fail if either class has fewer than two training observations.
- Hyperparameter mode means the most frequent complete parameter combination. Count ties compare smaller values in alphabetical parameter-name order; finite depths sort before None, and strings sort lexically.
- Retain GridSearchCV scoring="f1" and standard estimator.predict for main research metrics. Preserve the specified probability threshold 0.5 for deployment. Since SVC's calibrated probabilities can disagree with predict, generate a separate threshold-based table and an explicit mismatch warning. Do not silently equate these estimates.
- Compute permutation importance for every candidate during its outer fit, then publish the selected model's headline summary. Save detailed values to permit audit without refitting.
- Use the fitted scaler's output for SHAP so explanations reach the classifier in its actual input space. Sum signed one-hot contributions per row before taking the parent faculty feature's mean absolute magnitude.
- A numerical reproducibility command repeats the complete run twice and compares CSV bytes, excluding timestamps and model serialization.
- Stage research products under ignored `local/`; publish only after all computations succeed, writing the run manifest last. Source CSV checksums are verified before publication.
- Record null git commit when the repository has no commit, plus branch, dirty status, and source hashes. Never invent a revision identifier.
- Use default Daybreak design when the UI phase starts; no supplied reference images exist.

## Assumptions retained from the build spec

- Marital Yes means married and No means single.
- Deployed risk threshold is 0.5. Students will see categories, not raw probabilities.
- The 5.0-scale CGPA mapping uses approximate proportional rescaling and will disclose that limitation.
- Support contacts remain unverified until personally checked; never claim verified availability or government operation without evidence.

## Checkpoints

Report phase completion with actual evidence. Pause after ML results before the web phase, and after the first UI preview set before further polish. Do not deploy. These checkpoints come from `docs/BUILD_SPEC.md` sections 14 and 9.2. Authentic ML results now exist for review; UI previews remain pending.

## 2026-11-20 — Original-source review

- Retrieved the original Kaggle archive and validated 101 rows, 11 columns, target counts 66/35, and one missing age. Source SHA-256: `c0d1300dd5225b426f91ee75c81e5068efdadf528416628994a5a6e013063f0a`. The CSV remains unchanged.
- Inspected all 49 raw course strings (48 after whitespace stripping). Added literal Accounting and Marine science mappings to Business and economics and Natural and applied sciences. Ambiguous abbreviations and truncated labels remain Other at low confidence, including BCS, BIT, BENL/Benl, ENM, CTS, ALA, TAASL, MHSC, Malcom, Engine and engin; no inferred expansions.
- Canonical full-source groups below five observations are Natural and applied sciences (3) and Law (3), merged into Other in the final fit. Fold-specific retained groups remain learned only from each training fold.

- Docker installation and the ten targeted real-data/leakage tests now pass. The development image lacked Git, required by provenance and ignore-rule checks; install Git only in that stage and trust the explicit /workspace bind mount for its non-root user. The runtime image does not need Git.

- Completed two unchanged full protocols via `make verify` (384.259 s and 368.568 s), with identical bytes for all 12 research CSVs. All 40 tests passed; the final second-run artifact/output checks passed again (4 tests). The specified selection rule chose logistic regression with C=1 and l2 penalty; retain all nine main features and threshold 0.5. Small descriptive ablation changes do not authorise changing the prespecified protocol. The ML owner-review checkpoint is now ready.

## 2026-11-20 — Web phase authorised and verified

- The owner reviewed the ML results and explicitly authorised the functional web phase. Preserve the fitted model, nine features, and threshold 0.5.
- Load and integrity-check the complete joblib pipeline once per lifespan. API feature conversion uses the saved encodings and shared map_faculty function. Answers remain request-local; output contains categories and supportive copy only.
- Keep all copy and contacts in config. Escape the small startup fallback copy into the HTML shell so a config-fetch failure has readable text without inline JavaScript.
- Use one same-origin FastAPI process, a buildless frontend, strict request validation, generic errors, security headers, no-store prediction responses, and Uvicorn with access logs disabled. No request logging, accounts, storage, or external runtime requests.
- Source the SURPIN entry through the connected local-hotline lookup. Do not reproduce the directory-only MANI number without confirmation from that lookup. Keep verified_on null for all entries; personal verification remains pending. Emergency/Miva entries retain owner-supplied provenance.
- The complete suite passed 104 tests; Chrome checks passed at 390×844 and 1280×800, including keyboard completion, validation, both real model categories, restart, dialog dismissal/focus, age/year disclosures, and a real server-stop/retry. The browser connection initially failed but is now available. No Docker browser target or extra browser installation was retained.
- Phase 2 uses minimal styling. Proceed to the prescribed Daybreak first-preview set, then stop for visual review before polish.

## 2026-11-20 — Daybreak first preview

- Implement the specified default Daybreak direction because no visual references were supplied. Use original small SVGs and self-hosted Latin WOFF2 fonts with their actual OFL licences and source checksums; no runtime font service is contacted.
- Use existing installed Chrome for make preview, launched with a temporary clean profile through the pinned Playwright library. No extra browser download or browser-test Docker image is retained. Capture full pages at the specified viewport sizes so long result/support content is visible.
- Never mock a model result for screenshots. Briefly hold a genuine prediction request to capture loading; abort a test request to capture network failure, then retry against the real model. Synthetic test inputs are only QA fixtures, never research data or real submitted answers.
- Runtime checks verify empty browser storage/cookies and same-origin requests. Keep selected controls identifiable by check marks and text; support links, buttons, and option labels meet the 48 px target requirement. Contrast checks are generated from the implemented text/control colour pairs.
- The first authentic design set is complete and visually inspected. Stop here for owner visual review, as BUILD_SPEC 9.2/14 require, before further polish. Final report screenshots and broader acceptance checks follow that review.

- Fix an observed live-browser cache mismatch with a public content fingerprint in static/config URLs and Cache-Control no-cache on static responses. This fingerprint contains only public asset/config bytes, never answers or user identifiers. Keep predictions no-store. The final suite passes 105 tests, and existing Chrome now displays the current preview.
