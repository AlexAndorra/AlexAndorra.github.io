import subprocess
from pathlib import Path

import pytest

import build_cv
from build_cv import (
    ROOT,
    check_private_destination,
    find_chrome,
    inject_phone,
    render_pdf,
    write_private_html,
)

PLACEHOLDER_HTML = '<head></head><p>a@b.c<span class="phone" data-private></span></p>'


def test_inject_phone_fills_placeholder():
    out = inject_phone(PLACEHOLDER_HTML, "+1 555 0100")
    assert "+1 555 0100" in out
    assert 'data-private></span>' not in out


def test_inject_phone_requires_placeholder():
    with pytest.raises(ValueError):
        inject_phone("<p>no placeholder here</p>", "+1 555 0100")


@pytest.mark.parametrize("bad", ["<script>alert(1)</script>", "+1 555 <b>0100</b>", "call me", ""])
def test_inject_phone_rejects_non_phone_values(bad):
    with pytest.raises(ValueError):
        inject_phone(PLACEHOLDER_HTML, bad)


@pytest.mark.parametrize("good", ["+33 6 12 34 56 78", "(415) 555-0100", "+1.415.555.0100"])
def test_inject_phone_accepts_common_formats(good):
    assert good in inject_phone(PLACEHOLDER_HTML, good)


def test_private_destination_inside_repo_is_rejected():
    with pytest.raises(ValueError):
        check_private_destination(ROOT / "cv" / "private.pdf")
    with pytest.raises(ValueError):
        check_private_destination(Path("cv/../tmp-private.pdf"))


def test_private_destination_outside_repo_is_allowed(tmp_path):
    assert check_private_destination(tmp_path / "cv.pdf") == (tmp_path / "cv.pdf").resolve()


def test_private_html_is_unique_and_outside_repo():
    a = write_private_html('<html><head></head><body><img src="photo.jpg"></body></html>')
    b = write_private_html('<html><head></head><body></body></html>')
    try:
        assert a != b
        assert ROOT not in a.resolve().parents
        # Relative assets still resolve against cv/ via an injected <base>.
        assert (ROOT / "cv").resolve().as_uri() + "/" in a.read_text()
    finally:
        for p in (a, b):
            p.unlink(missing_ok=True)


def test_find_chrome_honours_valid_env(monkeypatch, tmp_path):
    exe = tmp_path / "chrome"
    exe.write_text("#!/bin/sh\n")
    exe.chmod(0o755)
    monkeypatch.setenv("CHROME_BIN", str(exe))
    assert find_chrome() == str(exe)


def test_find_chrome_rejects_invalid_env(monkeypatch, tmp_path):
    monkeypatch.setenv("CHROME_BIN", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError):
        find_chrome()


def test_failed_render_keeps_existing_pdf(monkeypatch, tmp_path):
    dest = tmp_path / "cv.pdf"
    dest.write_bytes(b"%PDF-previous")

    def boom(cmd, **kwargs):
        # Simulate Chrome writing a partial file then crashing.
        out = next(a for a in cmd if a.startswith("--print-to-pdf=")).split("=", 1)[1]
        Path(out).write_bytes(b"%PDF-partial")
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr(build_cv, "find_chrome", lambda: "/bin/true")
    monkeypatch.setattr(build_cv.subprocess, "run", boom)
    with pytest.raises(subprocess.CalledProcessError):
        render_pdf(tmp_path / "in.html", dest)
    assert dest.read_bytes() == b"%PDF-previous"


def test_non_pdf_output_is_rejected(monkeypatch, tmp_path):
    dest = tmp_path / "cv.pdf"

    def garbage(cmd, **kwargs):
        out = next(a for a in cmd if a.startswith("--print-to-pdf=")).split("=", 1)[1]
        Path(out).write_bytes(b"<html>error</html>")

    monkeypatch.setattr(build_cv, "find_chrome", lambda: "/bin/true")
    monkeypatch.setattr(build_cv.subprocess, "run", garbage)
    with pytest.raises(RuntimeError):
        render_pdf(tmp_path / "in.html", dest)
    assert not dest.exists()
