# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print cv/index.html to PDF with headless Chrome.

Public PDF (no phone):   uv run tools/build_cv.py
Private PDF (with phone): CV_PHONE='+1 ...' uv run tools/build_cv.py --private OUT.pdf

The phone number is injected into a temporary copy of the HTML that lives next to
the original (so relative assets resolve) and is deleted right after printing; it
never touches tracked files.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CV_HTML = ROOT / "cv" / "index.html"
PUBLIC_PDF = ROOT / "cv" / "Alexandre-Andorra-CV.pdf"
CHROME = os.environ.get(
    "CHROME_BIN", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
)
PLACEHOLDER = '<span class="phone" data-private></span>'


def inject_phone(html: str, phone: str) -> str:
    """Fill the private phone placeholder; fail loudly if it is missing."""
    if PLACEHOLDER not in html:
        raise ValueError("phone placeholder not found in CV HTML")
    filled = f'<span class="phone" data-private>{phone}</span>'
    return html.replace(PLACEHOLDER, filled, 1)


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    """Print an HTML file to PDF (Letter size comes from the page's @page rule)."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        subprocess.run(
            [
                CHROME,
                "--headless=new",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--user-data-dir={profile}",
                "--virtual-time-budget=15000",
                "--run-all-compositor-stages-before-draw",
                f"--print-to-pdf={pdf_path}",
                html_path.resolve().as_uri(),
            ],
            check=True,
            capture_output=True,
        )
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError(f"Chrome produced no PDF at {pdf_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, help="write a phone-bearing PDF here")
    args = parser.parse_args(argv)

    if args.private is None:
        render_pdf(CV_HTML, PUBLIC_PDF)
        print(PUBLIC_PDF)
        return 0

    phone = os.environ.get("CV_PHONE")
    if not phone:
        parser.error("--private needs the CV_PHONE environment variable")
    tmp = CV_HTML.with_name(".private-cv.html")
    try:
        tmp.write_text(inject_phone(CV_HTML.read_text(), phone))
        render_pdf(tmp, args.private)
    finally:
        tmp.unlink(missing_ok=True)
    print(args.private)
    return 0


if __name__ == "__main__":
    sys.exit(main())
