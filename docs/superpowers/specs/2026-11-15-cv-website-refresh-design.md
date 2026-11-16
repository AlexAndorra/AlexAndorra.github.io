# CV + personal website refresh — design

## Intent
Alex (Data Scientist at Meta; PyMC core dev; LBS podcast host) is targeting **Applied Research
Scientist (ARS) roles at frontier LLM labs**. The CV must read as *research scientist*, not
founder/consultant, while staying honest: no claims a lab reviewer can't verify. The personal
site (https://alexandorra.github.io, this repo, single `index.html`) must match the CV's facts,
use the new photo, and share the new visual identity if it looks better.

Source of truth for content: `~/Downloads/AlexandreAndorra.pdf` (identical text to the .docx /
Google Doc). New photo: `~/Downloads/IMG_3523.jpg` (1633×1633, olive-tree background, dark olive
jacket, sage tee).

## Goals
1. `cv/index.html` — a single-source HTML CV, max **2 US-Letter pages** when printed, modern
   styling coherent with the site, palette taken from the photo.
2. PDF exports from that HTML via headless Chrome:
   - `cv/Alexandre-Andorra-CV.pdf` (public, committed, **no phone number**), linked from the site.
   - `~/Downloads/Alexandre-Andorra-CV-private.pdf` (with phone, never committed).
3. Website: new photo, facts aligned with the CV, new talks + roles, link to the CV, palette swap.
4. Automated checks (written first): page count == 2, PDF text extractable and contains key
   strings in reading order, all hyperlinks present, public PDF/HTML contain no phone number,
   site HTML has no stale facts (list below).

## Non-goals
- No `foresight` mention anywhere (not public yet). No new claims of RL/LLM-evals experience.
- No change to the site's information architecture beyond what content needs (sections stay).
- No JS frameworks / build step for the site; it stays a static GitHub Pages file.

## Anti-goals (failure even if it "works")
- CV spills to a 3rd page, or shrinks fonts below ~9pt to fit.
- Two-column layout that scrambles text order for ATS parsers (Greenhouse/Ashby/Lever).
- Any overstated claim (e.g. "RL expert", "LLM evals") a reviewer could puncture.
- Phone number published on the public web.

## Substance decisions (CV)
- **Headline:** `Machine Learning Scientist · Probabilistic ML, Causal Inference & Model Evaluation`.
  RL dropped from the headline (only evidence is podcast hosting); "AI Evals" reframed as
  *model evaluation*, which Alex genuinely does (calibration, proper scoring, LOO-CV, PPCs,
  measuring AI-tool impact at Meta).
- **Summary:** research-forward, ~3 lines: uncertainty quantification & rigorous evaluation of
  models in production; measuring AI's impact at Meta scale; open-source + publications;
  science communication as a research-community asset.
- **Remove the "Key Impact" section.** Every item duplicates a line elsewhere (podcast appears 3×,
  $1M 3×, Nature 2×, $100K 2×). Replace with a one-line "highlights" strip under the header
  (4–5 compact stats) — costs ~2 lines instead of ~6.
- **Order:** Header → Summary → Experience (Meta, Marlins, PyMC Labs, earlier one-liner) →
  Research & Open Source (Nature-review preprint, Soccer Factor Model arXiv, PyMC core dev +
  docs, Baygent Skills, PollsPosition) → Teaching & Community (Intuitive Bayes, LBS) → Talks →
  Skills → Education.
- **Meta bullets:** tightened wording, active voice, no invented metrics. Flag to Alex: add a
  number if he's allowed to.
- **Skills:** add a "Model Evaluation" row (proper scoring rules, calibration/PIT, LOO-CV & model
  comparison, posterior predictive checks, A/B & causal measurement). Keep PyTorch/JAX; drop
  TensorFlow and "Deep Neural Networks" as standalone claims (weakly evidenced). Keep "AI agents"
  as "Agentic AI tooling" backed by Baygent Skills.
- Drop "References … available upon request".

## Fact reconciliation (CV numbers win unless noted)
| Item | CV | Site | Use |
|---|---|---|---|
| Meta title | Data Scientist | Senior Data Scientist | Data Scientist (Meta's official title has no level) |
| Location | Sunnyvale, CA | Palo Alto, CA | Sunnyvale, CA |
| Marlins end | Oct 2025 | Nov 2025 | Oct 2025 |
| PyMC Labs end | Jul 2024 | Present | Jul 2024 |
| Tracking data | 1M+ events | 50K+ events/game | 1M+ tracking events |
| PyMC Labs money | "$1M business" / "$1M annual profit" | "$1M profit" | "$0 → $1M annual profit in 2 years" everywhere |
| Growth | 50% YoY / 50% YoY client growth | — | "50% YoY client growth" |
| Baygent compat | Claude Code, Codex, Gemini CLI | Claude Code, Cursor, Gemini CLI | Claude Code, Codex, Cursor, Gemini CLI |
| Site title tag | — | "Senior Applied Scientist" | "Machine Learning Scientist" |

## Visual identity (from the photo)
Fonts as on the site: DM Serif Display (name/headings), DM Sans (body), JetBrains Mono (dates,
labels). Palette:
- `--ink` #23291d (jacket shadow) — text/headers
- `--olive` #4b5a32 (leaves) — primary accent, section labels, header band on site
- `--sage` #8e9d74 (tee / leaf highlights) — rules, photo ring, tags
- `--paper` #faf8f2 (warm cream) — background
- `--terra` #b5603e (skin-warm / site heritage) — links & sparse highlights
- `--brass` #a88a4f (jacket snaps) — tiny details only
Site: teal → olive, charcoal hero → deep olive-ink, terracotta kept as accent. Dark-mode not
required for the CV; the site keeps its current light-only theme.

## CV layout
Single reading-order column (ATS-safe). Header: name + headline + contact row on the left,
circular photo (~1.05in) with sage ring on the right. Highlights strip below. Section labels in
small-caps mono with a thin sage rule. Entries: org + role on the left, dates/location
right-aligned in mono. Body 9.5–10pt DM Sans, line-height ~1.35. Margins ~0.5in. On screen the
page renders as paper sheets on a sage-tinted background with a "Download PDF" button
(`@media print` hides it).

## Approaches considered
1. **HTML + print CSS → headless-Chrome PDF (chosen).** One source for web + PDF, matches the
   site's fonts/palette exactly, testable (page count, text, links).
2. Restyled .docx/Google Doc — keeps Alex's current editing flow but can't match the site look.
3. LaTeX (e.g. moderncv) — great typography, second toolchain, look drifts from the site.
Alex delegated the "how"; option 1 is the builder's call.

## Website changes
- Photo: new `profile-photo.jpg` resized to 800×800 (~150 KB; current one is 6.8 MB).
- Hero tagline + `<title>`: "Machine Learning Scientist · Probabilistic ML, Causal Inference &
  Model Evaluation". Location line → Sunnyvale, CA.
- About: Meta paragraph aligned with CV; Marlins 1M+ events; PyMC Labs dates; "$1M annual profit".
- Career highlights: add Meta card; fix Marlins/PyMC Labs dates.
- Talks: add CMU (Oct 2026), Princeton (Sep 2026), StanCon (Aug 2026) with CV links.
- Contact row: add "CV" button → `cv/`.
- Palette swap per above; keep layout, sections, testimonials, awards untouched.

## Builder-check resolutions (builder's calls unless noted)
- **Carried-over numbers:** keep Alex's own figures verbatim (15%, $100M+, 40+ workshops/500+
  practitioners, 15+ contracts, 12K listeners, top 1.5%). Cut unverifiable superlatives
  ("leading Bayesian ML consultancy", "largest Bayesian statistics community"). "Under review in
  Nature" kept but **flagged to Alex** to confirm it's still current.
- **RL:** keep the true fact (hosting a 12-episode RL series) in the LBS line; remove RL from the
  Skills row. Remove "Deep Learning"/"Neural Networks"/TensorFlow from the site Skills grid.
- **Site ↔ CV scope:** *all* facts on the site align with the CV — About text (drop "generative
  models"; use CV's Meta description), Impact cards ("$1M annual profit"), Skills grid (mirrors
  CV skill rows), dates, location, title. The stale-facts test lists every superseded string.
- **Done =** branch `worktree-cv-website-refresh` pushed + **draft PR**; nothing merged to `main`
  (= nothing live) until Alex reviews. Phone number never enters git (private PDF built from an
  untracked/env-provided value, written to `~/Downloads`).

## Alex's corrections (2026-11-15) — these override anything above
- **Keep** "leading Bayesian ML consultancy", "largest Bayesian statistics community", and
  "under review in Nature" (confirmed still under review).
- **Keep** TensorFlow and Deep Learning / Deep Neural Networks — on the site *and* the CV.
- **Location:** "San Francisco Bay Area" (CV + site), not Sunnyvale / Palo Alto.
- **PyMC Labs:** "$0 → $1M annual **revenue** in 2 years" everywhere (not profit).
- **Private PDF (with phone):** uploaded to Alex's Google Drive folder
  `1LNMgiVA6aEbfAm7baEpJY5X5C8ttlOYo` as the golden source — not ~/Downloads, never git.
- **Meta bullets:** no metrics (6 months in). Alex confirmed: methods = quasi-experimental causal
  inference (DiD, synthetic control, etc.); tools = coding assistants *and* internal agents;
  output = inputs to exec-level AI investment decisions. Use all three.
- **No skeptic review:** this is brand marketing; confident framing/overstatement is acceptable.

## Left to the builder
Exact spacing/typography tuning to hit 2 pages; highlight-strip stat choice; test tooling
(uv + pypdf/pytest or Node); how the private PDF injects the phone (e.g. a build script with a
placeholder substituted from an untracked local file).
