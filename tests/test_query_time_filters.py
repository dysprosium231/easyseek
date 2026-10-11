import io
import json
import urllib.error

import pytest

from scansci_find import adapters


def test_openalex_abstract_is_rebuilt_from_inverted_index():
    work = {"title": "t", "abstract_inverted_index": {"SiOC": [0], "oxidises": [1], "slowly": [2]}}
    assert adapters.normalize_openalex_work(work)["abstract"] == "SiOC oxidises slowly"


def test_year_range_reaches_openalex_and_crossref(monkeypatch):
    monkeypatch.setenv("SCANSCI_FIND_YEAR_FROM", "2022")
    monkeypatch.setenv("SCANSCI_FIND_YEAR_TO", "2024")
    monkeypatch.setenv("OPENALEX_API_KEY", "k")
    urls = []

    def fake_json(self, url, headers=None):
        urls.append(url)
        return {"results": [], "meta": {}} if "openalex" in url else {"message": {"items": []}}

    monkeypatch.setattr(adapters.HttpProvider, "_json", fake_json)
    adapters.OpenAlexProvider().search("SiOC", 5)
    adapters.CrossrefProvider().search("SiOC", 5)
    assert "from_publication_date%3A2022-01-01%2Cto_publication_date%3A2024-12-31" in urls[0]
    assert "from-pub-date%3A2022%2Cuntil-pub-date%3A2024" in urls[1]


def test_keyless_semantic_scholar_gives_up_on_first_429(monkeypatch):
    monkeypatch.delenv("SEMANTIC_SCHOLAR_API_KEY", raising=False)
    calls = []

    def fake_urlopen(request, timeout=None):
        calls.append(request.full_url)
        raise urllib.error.HTTPError(request.full_url, 429, "Too Many", {"Retry-After": "30"}, io.BytesIO())

    monkeypatch.setattr(adapters.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(adapters.time, "sleep", lambda s: pytest.fail("should not wait"))
    with pytest.raises(adapters.ProviderRateLimitError):
        adapters.SemanticScholarProvider().search("SiOC", 5)
    assert len(calls) == 1