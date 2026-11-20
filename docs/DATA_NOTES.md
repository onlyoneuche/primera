# Data notes

## Required source

Only the Student Mental health survey published by MD Shariful Islam on Kaggle is in scope. Expected: 101 responses, 11 fields, 66 No and 35 Yes depression responses, and one missing age. The original Kaggle CSV was retrieved and validated on 20 November 2026: these counts were observed in the source. Its SHA-256 is `c0d1300dd5225b426f91ee75c81e5068efdadf528416628994a5a6e013063f0a`; download provenance is in `data/source.json`.

The pipeline validates source bytes before modelling, leaves age missing until in-fold imputation, strips string whitespace, normalises year case and CGPA labels, and groups courses using explicit rules. It preserves original untrimmed course labels in the audit table. Unknown abbreviations remain Other at low confidence. All 49 raw course labels were inspected (48 after stripping whitespace). Case variants, trailing spaces, and the literal typo Mathemathics are present. Accounting and Marine science use literal discipline mappings. BCS, BIT, BENL/Benl, ENM, CTS, ALA, TAASL, MHSC, Malcom, Engine and engin remain unresolved at low confidence; their presence makes Other a substantial category. Natural and applied sciences and Law each have three source rows and merge into Other for the final fit; fold merges are independently learned.

The survey has a self-reported target rather than a PHQ-9 or DASS-21 result. Associations between anxiety, panic, specialist help and depression can reflect overlapping concurrent self-reports. They do not establish causality or prospective early-warning validity. The four planned ablations make this limitation visible.

## Observed research findings

The generated profile flags marital status as strongly associated with the target (phi 0.596), above anxiety (0.274) and panic (0.247). Both the selected model's in-sample SHAP and held-out permutation importance rank marital status first. Removing anxiety and panic changes mean F1 by +0.008; this small descriptive difference does not establish an improvement. Do not repeat the proposal's expectation that anxiety and panic dominate as though it were an observed finding. See `outputs/RESULTS_SUMMARY.md` for the complete generated tables and uncertainty.

## Coverage and encoding

- Single Malaysian institution; no Nigerian validation dataset or new participant collection.
- Ages 18–24 and study years 1–4 only; age imputation stays within training folds.
- Two gender options represented in training; no invented coverage for other groups.
- Marital Yes/No interpreted as married/single, an unconfirmed assumption.
- CGPA is a band on a 4.0 scale, not an exact grade.
- Planned 5.0-scale bands are converted approximately using the spec's proportional mapping and must be disclosed in the UI.
- Rare faculty counts must be fitted inside each fold. Final counts, low-confidence labels, and merged groups are recorded by the real run in the generated profile, grouping table, per-fold records, and model metadata.

## Report reconciliation for the later writing task

The Word proposal was read for context and remains unchanged in `local/`.

- Section 1.6 still names a 1,800-row, 16-column dataset, whereas section 3.3 and the current build spec identify the 101-row survey. Correct the obsolete statement later.
- Section 3.3 calls anxiety optional; the build spec includes it in the nine-feature main model and tests its removal through sensitivity analyses.
- Section 3.4 leaves row removal versus median imputation open. The build spec fixes in-fold median imputation and preserves all 101 rows.
- Section 3.5 references a feature-identification objective that does not match the current approved objectives. Preserve the official aim/objectives and reconcile the cross-reference later.
- Sections 3.6–3.7 leave k=5 versus k=10 open and discuss five-fold results. The build spec fixes nested 5-fold CV repeated ten times, with three-fold inner tuning.
- Section 3.7 refers to Research Question 4 for evaluation; the current evaluation question is Research Question 3.
- Historical defence dates are proposal context, not evidence of current implementation or project completion.
- Do not repeat the claim that cross-validation overcomes low statistical power. It provides descriptive validation under limited data; small-sample uncertainty remains.

Chapters 4 and 5 must use generated research outputs and the actual test evidence. Do not insert predicted or illustrative metrics as measured results.
