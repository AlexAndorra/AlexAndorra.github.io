import re
import subprocess
from pathlib import Path

import pytest
from pypdf import PdfReader

# Any international/US-style phone number (no real digits hardcoded in the repo).
PHONE_RE = re.compile(r"\+?\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]\d{2,4}[\s.-]\d{2,4}")

# Every hyperlink in the source CV (Google Doc / docx), plus the email.
# Matched as prefixes so tracking params (?si=...) don't matter.
EXPECTED_LINKS = [
    "https://alexandorra.github.io/",
    "https://alexandorra.github.io/pollsposition_blog/about/",
    "https://arxiv.org/abs/2412.05911",
    "https://github.com/AlexAndorra",
    "https://github.com/Learning-Bayesian-Statistics/baygent-skills",
    "https://learnbayesstats.com",
    "https://learnbayesstats.com/episode/118-exploring-the-future-of-stan-with-charles-margossian-brian-ward",
    "https://learnbayesstats.com/episode/amortized-bayesian-inference-gpu-computing-stan-stancon-paul-burkner-steve-bronder",
    "https://psych.princeton.edu/news-events/2026/alexandre-andorra-senior-data-scientist",
    "https://statsandstories.net/sports1/learning-baseball-through-statistics",
    "https://www.biorxiv.org/content/10.1101/2025.04.24.650194v1",
    "https://www.cmsaconference.com/speakers-1",
    "https://www.intuitivebayes.com",
    "https://www.linkedin.com/in/alex-andorra/",
    "https://www.pymc.io",
    "https://www.pymc.io/projects/examples/en/latest/gallery.html",
    "https://www.soccerfactormodel.com/",
    "https://www.superdatascience.com/podcast/sds-793-bayesian-methods-and-applications-with-alexandre-andorra",
    "https://youtu.be/lXU5dr6Lmgo",
    "https://youtu.be/u6I5pN_Q6r4",
    "mailto:andorra.alexandre@gmail.com",
]


def pdf_text(pdf: Path) -> str:
    return subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True
    ).stdout


def link_uris(pdf: Path) -> set[str]:
    uris = set()
    for page in PdfReader(pdf).pages:
        for annot in page.get("/Annots") or []:
            action = annot.get_object().get("/A")
            if action and "/URI" in action:
                uris.add(str(action["/URI"]))
    return uris


def test_pdf_two_pages(public_pdf):
    assert len(PdfReader(public_pdf).pages) == 2


def test_pdf_text_order(public_pdf):
    text = pdf_text(public_pdf).lower()
    anchors = ["alexandre andorra", "experience", "meta", "miami marlins", "pymc labs",
               "research", "talks", "skills", "education"]
    # Each anchor must appear after the previous one (sequential search), so
    # earlier mentions (e.g. "Meta" in the summary) don't mask a scrambled order.
    pos = 0
    for anchor in anchors:
        found = text.find(anchor, pos)
        assert found >= 0, f"{anchor!r} not found after offset {pos}"
        pos = found + len(anchor)
    # Section headings themselves must be in order too.
    heads = ["experience", "research", "teaching", "selected talks", "skills", "education"]
    matches = [re.search(rf"^\s*{h}\b", text, re.M) for h in heads]
    assert all(matches), dict(zip(heads, matches))
    hpos = [m.start() for m in matches]
    assert hpos == sorted(hpos), dict(zip(heads, hpos))


@pytest.mark.parametrize("phrase", [
    "San Francisco Bay Area", "annual revenue", "under review in Nature", "Model Evaluation",
    "TensorFlow", "leading Bayesian ML consultancy", "largest Bayesian statistics community",
    "Carnegie Mellon", "Princeton", "StanCon", "synthetic control", "coding assistants",
    "reinforcement learning", "interrupted time series", "state space", "IRT",
    "internal agents", "exec-level",
])
def test_pdf_required_facts(public_pdf, phrase):
    flat = " ".join(pdf_text(public_pdf).split())
    assert phrase.lower() in flat.lower()


@pytest.mark.parametrize("phrase", [
    "foresight", "profit", "Sunnyvale", "Palo Alto", "Reinforcement Learning •",
])
def test_pdf_forbidden(public_pdf, phrase):
    flat = " ".join(pdf_text(public_pdf).split())
    assert phrase.lower() not in flat.lower()


def test_pdf_link_targets(public_pdf):
    uris = link_uris(public_pdf)
    missing = [e for e in EXPECTED_LINKS if not any(u.startswith(e) for u in uris)]
    assert not missing


def test_pdf_embeds_dm_fonts(public_pdf):
    fonts = subprocess.run(["pdffonts", str(public_pdf)], capture_output=True, text=True).stdout
    assert "DMSans" in fonts
    assert "DMSerifDisplay" in fonts


def test_pdf_size(public_pdf):
    assert public_pdf.stat().st_size < 1_000_000


def test_html_has_phone_placeholder_only(root):
    html = (root / "cv" / "index.html").read_text()
    assert 'class="phone" data-private></span>' in html
    visible = re.sub(r'href="[^"]*"', "", html)  # DOIs in URLs look phone-like
    assert not PHONE_RE.search(visible)


def test_public_pdfs_have_no_phone(public_pdf, committed_pdf):
    for pdf in (public_pdf, committed_pdf):
        assert not PHONE_RE.search(pdf_text(pdf)), pdf


def test_committed_pdf_is_two_pages(committed_pdf):
    assert len(PdfReader(committed_pdf).pages) == 2


def test_phone_regex_catches_phones():
    assert PHONE_RE.search("+33 612 345 678")
    assert PHONE_RE.search("(415) 555-0100")
    assert not PHONE_RE.search("Apr 2026 – Present, 1M+ tracking events, 2412.05911")


def test_baygent_leads_research_section(public_pdf):
    text = pdf_text(public_pdf).lower()
    start = re.search(r"^\s*research & open source", text, re.M).end()
    names = ["baygent skills", "hidden diversity", "soccer factor model", "pymc", "pollsposition"]
    first = {n: text.find(n, start) for n in names}
    assert min(first, key=first.get) == "baygent skills", first


def test_green_card_category(public_pdf):
    assert "EB-1A" in pdf_text(public_pdf)
