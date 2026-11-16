import pytest


@pytest.fixture(scope="module")
def site(root) -> str:
    return " ".join((root / "index.html").read_text().split())


@pytest.mark.parametrize("stale", [
    "Palo Alto", "Senior Applied Scientist</title>", "Senior Data Scientist at Meta",
    "generative models", "50K+ tracking events", "Nov 2025", "Mar 2021 – Present",
    "$1M profit", "profit", "foresight", "#1a6b5a", "--teal", "--charcoal", "rgba(26, 107, 90",
    "rgba(34, 145, 122",
])
def test_site_stale_facts_absent(site, stale):
    assert stale not in site


@pytest.mark.parametrize("fact", [
    "San Francisco Bay Area", "Data Scientist at Meta", "1M+ tracking events", "Oct 2025",
    "Mar 2021 – Jul 2024", "annual revenue", "Carnegie Mellon", "Princeton", "StanCon",
    'href="cv/"', "Model Evaluation", "TensorFlow", "Deep Learning", "--olive: #4b5a32",
    "synthetic control", "Codex",
])
def test_site_new_facts_present(site, fact):
    assert fact in site


def test_photo_small(root):
    assert (root / "profile-photo.jpg").stat().st_size < 300_000
