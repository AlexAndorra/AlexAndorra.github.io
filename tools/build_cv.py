# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print cv/index.html to PDF with headless Chrome.

Public PDF (no phone):    uv run tools/build_cv.py
Private PDF (with phone): CV_PHONE='+1 ...' uv run tools/build_cv.py --private OUT.pdf

The phone number is injected into a unique temporary copy of the HTML created
outside the repository, and the private PDF must also be written outside the
repository, so phone-bearing files can never land in the published tree.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CV_DIR = ROOT / "cv"
CV_HTML = CV_DIR / "index.html"
PUBLIC_PDF = CV_DIR / "Alexandre-Andorra-CV.pdf"
PLACEHOLDER = '<span class="phone" data-private></span>'
PHONE_FORMAT = re.compile(r"^\+?[\d\s().-]{6,24}$")
CHROME_NAMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")
CHROME_APP_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
)


def inject_phone(page: str, phone: str) -> str:
    """Fill the private phone placeholder with a validated, escaped phone number."""
    if PLACEHOLDER not in page:
        raise ValueError("phone placeholder not found in CV HTML")
    phone = phone.strip()
    if not PHONE_FORMAT.fullmatch(phone) or sum(c.isdigit() for c in phone) < 6:
        raise ValueError("CV_PHONE does not look like a phone number")
    filled = f'<span class="phone" data-private>{html.escape(phone)}</span>'
    return page.replace(PLACEHOLDER, filled, 1)


def check_private_destination(path: Path) -> Path:
    """Refuse to write a phone-bearing PDF anywhere inside the repository."""
    resolved = path.resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise ValueError(f"private PDF must be written outside the repository: {resolved}")
    return resolved


def write_private_html(page: str) -> Path:
    """Write HTML to an exclusive temp file outside the repo; relative assets resolve to cv/."""
    base = f'<base href="{CV_DIR.resolve().as_uri()}/">'
    page = page.replace("<head>", f"<head>\n{base}", 1)
    fd, name = tempfile.mkstemp(prefix="cv-private-", suffix=".html")  # O_EXCL, mode 0600
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(page)
    return Path(name)


def find_chrome() -> str:
    """Locate a Chrome/Chromium executable; CHROME_BIN wins but must be valid."""
    env = os.environ.get("CHROME_BIN")
    if env:
        if Path(env).is_file() and os.access(env, os.X_OK):
            return env
        raise FileNotFoundError(f"CHROME_BIN is not an executable file: {env}")
    for name in CHROME_NAMES:
        found = shutil.which(name)
        if found:
            return found
    for app in CHROME_APP_PATHS:
        if Path(app).is_file() and os.access(app, os.X_OK):
            return app
    raise FileNotFoundError("Chrome/Chromium not found; set CHROME_BIN to its executable")


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    """Print an HTML file to PDF, replacing pdf_path only once a valid PDF exists."""
    chrome = find_chrome()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as work:
        out = Path(work) / "out.pdf"
        argv = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--user-data-dir={Path(work) / 'profile'}",
            "--virtual-time-budget=15000",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={out}",
            html_path.resolve().as_uri(),
        ]
        # argv list, no shell: the executable is validated by find_chrome() and the
        # remaining arguments are fixed flags or paths we created.
        subprocess.run(argv, check=True, capture_output=True)  # nosemgrep
        if not out.is_file() or out.stat().st_size == 0 or not out.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError(f"Chrome did not produce a valid PDF for {html_path}")
        staged = pdf_path.with_name(f".{pdf_path.name}.{uuid.uuid4().hex}.tmp")
        try:
            shutil.copyfile(out, staged)
            os.replace(staged, pdf_path)
        finally:
            staged.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, help="write a phone-bearing PDF here (outside the repo)")
    args = parser.parse_args(argv)

    if args.private is None:
        render_pdf(CV_HTML, PUBLIC_PDF)
        print(PUBLIC_PDF)
        return 0

    phone = os.environ.get("CV_PHONE")
    if not phone:
        parser.error("--private needs the CV_PHONE environment variable")
    try:
        dest = check_private_destination(args.private)
        page = inject_phone(CV_HTML.read_text(encoding="utf-8"), phone)
    except ValueError as err:
        parser.error(str(err))
    tmp = write_private_html(page)
    try:
        render_pdf(tmp, dest)
    finally:
        tmp.unlink(missing_ok=True)
    print(dest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
