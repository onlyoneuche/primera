# First Daybreak preview set

These are screenshots of the running application, not mockups. The model produced both result categories. The 11 required states were captured at 390×844 (phone) and 1280×800 (desktop); full-page images can be taller than the viewport. All 22 images were visually reviewed. This is the first design-review checkpoint, not the final report screenshot set.

| State | Phone | Desktop |
| --- | --- | --- |
| Welcome | [View](welcome-phone.png) | [View](welcome-desktop.png) |
| Choice and selected state | [View](choice-question-phone.png) | [View](choice-question-desktop.png) |
| Age | [View](age-question-phone.png) | [View](age-question-desktop.png) |
| Faculty | [View](faculty-question-phone.png) | [View](faculty-question-desktop.png) |
| CGPA and scale disclosure | [View](cgpa-question-phone.png) | [View](cgpa-question-desktop.png) |
| Validation error | [View](error-state-phone.png) | [View](error-state-desktop.png) |
| Loading | [View](loading-phone.png) | [View](loading-desktop.png) |
| Lower-risk result | [View](lower-result-phone.png) | [View](lower-result-desktop.png) |
| Higher-risk result | [View](higher-result-phone.png) | [View](higher-result-desktop.png) |
| How this works | [View](how-this-works-phone.png) | [View](how-this-works-desktop.png) |
| Network error | [View](network-error-phone.png) | [View](network-error-desktop.png) |

[Browser verification](browser_checks.json) · [Contrast checks](contrast.md) · [Design specification](../DESIGN_SPEC.md)

Generate again with `make run` and `make preview`, following the environment setup in docs/DEVELOPMENT.md. The preview command uses the already-installed Chrome with a temporary clean profile. It holds a real request briefly for the loading capture and deliberately aborts a test request for the network-error capture; it never substitutes a model response. All form inputs used for QA are synthetic fixtures.

## Self-review

- Welcome has one original rising-sun illustration, warm accents, readable typography, and a clear primary action.
- Questions retain a consistent single-column flow. Selected choices have an explicit check as well as colour. Validation has a specific message and focus outline.
- Results use a calm leaf or amber lantern, explicit labels, supportive wording, limitations, and a support list. Higher risk has no alarming or celebratory presentation.
- The CGPA page and result pages scroll vertically; no horizontal overflow was found at either viewport.
- The modal scrolls internally so all transparency/support content remains reachable. Escape restores focus to its trigger.
- Text/control contrast checks pass. Interactive targets are at least 48 px; keyboard-only completion, result focus, back navigation, restart clearing, retry, and runtime browser privacy checks pass.

Owner approval of the look is required before further polish (BUILD_SPEC sections 9.2 and 14). Automated axe auditing, actual 200% browser-zoom review, and final screenshots in docs/screenshots remain for the subsequent acceptance/hardening work. Contact details still need personal verification before launch.
