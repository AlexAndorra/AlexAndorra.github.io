import pytest

from build_cv import inject_phone

PLACEHOLDER_HTML = '<p>a@b.c<span class="phone" data-private></span></p>'


def test_inject_phone_fills_placeholder():
    out = inject_phone(PLACEHOLDER_HTML, "+1 555 0100")
    assert "+1 555 0100" in out
    assert 'data-private></span>' not in out


def test_inject_phone_requires_placeholder():
    with pytest.raises(ValueError):
        inject_phone("<p>no placeholder here</p>", "+1 555 0100")
