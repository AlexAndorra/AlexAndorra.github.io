# CV + Website Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A 2-page, photo-palette HTML CV (+ public/private PDFs) aimed at frontier-lab ARS roles, and the personal site updated to match it.

**Architecture:** `cv/index.html` is the single source; `tools/build_cv.py` prints it to PDF with headless Chrome (optionally injecting the phone into a temp copy for the private PDF). pytest checks the PDF (pages, text, links, fonts, no phone) and the site (stale facts gone, new facts present). Site stays one static `index.html`.

**Tech Stack:** HTML/CSS, Google Fonts (DM Serif Display, DM Sans, JetBrains Mono), headless Google Chrome, uv inline-script deps, pytest + pypdf, poppler (`pdfinfo`, `pdffonts`, `pdftotext`), macOS `sips`.

**Spec:** `docs/superpowers/specs/2026-11-15-cv-website-refresh-design.md` (its "Alex's corrections" section overrides earlier sections).

## Global Constraints
- Max **2 US-Letter pages**; body text ≥ 9pt.
- Single reading-order column (ATS-safe).
- Location string everywhere: `San Francisco Bay Area`.
- PyMC Labs: `$0 → $1M annual revenue in 2 years` (never "profit").
- Headline: `Machine Learning Scientist · Probabilistic ML, Causal Inference & Model Evaluation`.
- No `foresight` anywhere. RL not in headline/skills; LBS RL-series fact stays.
- Keep: "leading Bayesian ML consultancy", "largest Bayesian statistics community", "under review in Nature", TensorFlow, Deep Learning.
- Phone number never in git: public HTML/PDF have none; private PDF built from env `CV_PHONE`, uploaded to Drive folder `1LNMgiVA6aEbfAm7baEpJY5X5C8ttlOYo`.
- Palette tokens: `--ink #23291d`, `--olive #4b5a32`, `--sage #8e9d74`, `--paper #faf8f2`, `--terra #b5603e`, `--brass #a88a4f`.
- Nothing merged to `main`; deliver as draft PR.

## Review Focus
1. Web fonts not loaded when Chrome prints → fallback metrics → 3rd page. Expect DM Sans embedded in the PDF. → `test_pdf_embeds_dm_fonts` (Task 1/2).
2. ATS text order scrambled (name not first, sections out of order). → `test_pdf_text_order` (Task 2).
3. Hyperlinks lost in PDF (CSS-styled anchors still must be link annotations). → `test_pdf_link_targets` (Task 2).
4. CV page on a phone (390px) scrolls horizontally / photo overflows. → manual screenshot check in Task 2 step + site in Task 3.
5. PDF bloated by the 1.5 MB photo. Expect public PDF < 1 MB. → `test_pdf_size` (Task 2).

---

### Task 1: Build tool + test harness

**Files:**
- Create: `tools/build_cv.py` (PEP 723 header: deps none)
- Create: `tests/test_build.py`, `tests/conftest.py`
- Create: `_config.yml` with `exclude: [tools, tests, docs]` (keep tooling off GitHub Pages)

**Interfaces — Produces:**
- `inject_phone(html: str, phone: str) -> str` — fills the element `<span class="phone" data-private></span>` with `phone` and a leading separator `" • "`; raises `ValueError` if the placeholder is absent.
- `render_pdf(html_path: Path, pdf_path: Path) -> None` — runs Chrome `--headless=new --no-pdf-header-footer --virtual-time-budget=10000 --print-to-pdf=…` on the file URL.
- CLI: `uv run tools/build_cv.py` → `cv/Alexandre-Andorra-CV.pdf`; `CV_PHONE=… uv run tools/build_cv.py --private OUT.pdf` → injects phone into a temp copy **inside `cv/`** (so relative assets resolve), prints, deletes the temp copy.
- `conftest.py` fixture `public_pdf` (session) → builds and returns the public PDF path.

- [ ] Step 1: Write failing tests `test_inject_phone_fills_placeholder` (assert `"+1 555" in out` and placeholder text non-empty), `test_inject_phone_requires_placeholder` (`pytest.raises(ValueError)`).
- [ ] Step 2: Run `uv run --with pytest --with pypdf pytest tests/test_build.py -q` → FAIL (import error).
- [ ] Step 3: Implement both functions + CLI.
- [ ] Step 4: Re-run → PASS.
- [ ] Step 5: Commit `build: add CV PDF build tool and tests`.

### Task 2: The CV (`cv/index.html`)

**Files:**
- Create: `cv/index.html`, `tests/test_cv.py`
- Modify: `profile-photo.jpg` (replace with `~/Downloads/IMG_3523.jpg` resized via `sips -Z 800`, JPEG quality ~82; shared by CV and site; CV references `../profile-photo.jpg`)
- Output: `cv/Alexandre-Andorra-CV.pdf`

**Interfaces — Consumes:** `render_pdf`, `public_pdf` fixture.

- [ ] Step 1: Write failing tests in `tests/test_cv.py`:
  - `test_pdf_two_pages`: `len(PdfReader(p).pages) == 2`.
  - `test_pdf_text_order`: in `pdftotext -layout` output, indices strictly increase for `"ALEXANDRE ANDORRA"` (case-insensitive), `"Experience"`, `"Meta"`, `"Miami Marlins"`, `"PyMC Labs"`, `"Research"`, `"Talks"`, `"Skills"`, `"Education"`.
  - `test_pdf_required_facts`: text contains `"San Francisco Bay Area"`, `"annual revenue"`, `"under review in Nature"`, `"Model Evaluation"`, `"TensorFlow"`, `"leading Bayesian ML consultancy"`, `"largest Bayesian statistics community"`, `"Carnegie Mellon"`, `"Princeton"`, `"StanCon"`.
  - `test_pdf_forbidden`: text lacks `"foresight"`, `"profit"`, `"Sunnyvale"`, `"Palo Alto"`, `"Reinforcement Learning •"` (skills row) — but contains `"reinforcement learning"` (LBS series).
  - `test_pdf_link_targets`: set of `/URI` annotations ⊇ all 20 hyperlinks from the source docx (list them as a constant: alexandorra.github.io, arxiv 2412.05911, github AlexAndorra, baygent-skills repo, learnbayesstats.com, the two LBS StanCon episodes, Princeton news, statsandstories, biorxiv, cmsaconference, intuitivebayes, linkedin, pymc.io, pymc gallery, soccerfactormodel, superdatascience, the two YouTube talks, pollsposition about) + `mailto:andorra.alexandre@gmail.com`.
  - `test_pdf_embeds_dm_fonts`: `pdffonts` output contains `DMSans` and `DMSerifDisplay`.
  - `test_pdf_size`: `< 1_000_000` bytes.
  - `test_html_has_phone_placeholder_only`: html contains `data-private></span>` and no phone-number pattern.
- [ ] Step 2: Run `uv run --with pytest --with pypdf pytest tests/test_cv.py -q` → FAIL (no html).
- [ ] Step 3: Resize photo; write `cv/index.html` per spec "CV layout", "Substance decisions", "Fact reconciliation", corrections. Content source: `~/Downloads/AlexandreAndorra.pdf`. `@page { size: Letter; margin: 0.5in }`; screen view = paper sheets on sage-tinted bg + "Download PDF" button linking `Alexandre-Andorra-CV.pdf` (hidden in print); `<meta name="viewport">`, sheets fluid below 8.5in.
- [ ] Step 4: `uv run tools/build_cv.py`; run tests → PASS. Iterate spacing (not font size < 9pt) until 2 pages.
- [ ] Step 5: Visual check: `pdftoppm -r 80 -png` both pages, view them; Chrome headless `--screenshot --window-size=390,2000` of `cv/index.html`, view it (no horizontal overflow).
- [ ] Step 6: Commit `cv: add 2-page HTML CV with photo palette and public PDF`.

### Task 3: Website update (`index.html`)

**Files:**
- Modify: `index.html` (CSS `:root` tokens lines ~14–35, hero, about, career cards, impact cards, skills grid, projects, talks)
- Create: `tests/test_site.py`

- [ ] Step 1: Write failing tests in `tests/test_site.py` (read `index.html` as text):
  - `test_site_stale_facts_absent`: none of `"Palo Alto"`, `"Senior Applied Scientist</title>"`, `"Senior Data Scientist at Meta"`, `"generative models"`, `"50K+ tracking events"`, `"Nov 2025"`, `"Mar 2021 – Present"`, `"$1M profit"`, `"foresight"`, `"#1a6b5a"` (old teal).
  - `test_site_new_facts_present`: `"San Francisco Bay Area"`, `"Data Scientist at Meta"`, `"1M+ tracking events"`, `"Oct 2025"`, `"Mar 2021 – Jul 2024"`, `"annual revenue"`, `"Carnegie Mellon"`, `"Princeton"`, `"StanCon"`, `'href="cv/"'`, `"Model Evaluation"`, `"TensorFlow"`, `"Deep Learning"`, `"--olive: #4b5a32"`.
  - `test_photo_small`: `profile-photo.jpg` < 300 KB.
- [ ] Step 2: Run → FAIL.
- [ ] Step 3: Edit `index.html`: palette swap (teal→olive family, charcoal hero→`--ink`, keep terracotta), title/tagline/location, About + cards + impact + skills aligned with CV, Meta career card, three 2026 talks, "CV" contact button. Load `frontend-design` skill first.
- [ ] Step 4: Run all tests → PASS. Screenshot desktop (1280) + mobile (390) and view.
- [ ] Step 5: Commit `site: new photo, CV-aligned content, olive palette, CV link`.

### Task 4: Red-team, publish branch, private PDF

- [ ] Step 1: (Skeptic review dropped per Alex — branding, not research.) Self-check rendered PNGs for visual defects.
- [ ] Step 2: Re-run `uv run --with pytest --with pypdf pytest -q` → all PASS; rebuild public PDF; commit.
- [ ] Step 3: `CV_PHONE='<phone>' uv run tools/build_cv.py --private $CLAUDE_JOB_DIR/tmp/Alexandre-Andorra-CV.pdf`; verify `pdftotext` contains the phone and 2 pages; upload to Drive folder `1LNMgiVA6aEbfAm7baEpJY5X5C8ttlOYo`.
- [ ] Step 4: `git push -u origin worktree-cv-website-refresh`; `gh pr create --draft`.
