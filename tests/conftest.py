import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_cv import CV_HTML, PUBLIC_PDF, render_pdf  # noqa: E402


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def public_pdf(tmp_path_factory) -> Path:
    """A fresh render of the current HTML (kept out of the tree so tests don't dirty it)."""
    out = tmp_path_factory.mktemp("cv") / "cv.pdf"
    render_pdf(CV_HTML, out)
    return out


@pytest.fixture(scope="session")
def committed_pdf() -> Path:
    """The PDF actually published on the site."""
    return PUBLIC_PDF
