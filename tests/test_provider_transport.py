import io
import json
import os
import urllib.error
import urllib.parse
import unittest
from unittest.mock import Mock, patch

from scansci_find.adapters import (
    HttpProvider,
    OpenAlexProvider,
    ProviderConfigurationError,
    PubMedProvider,
    SemanticScholarProvider,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class ProviderTransportTests(unittest.TestCase):
    def test_http_provider_retries_429_and_respects_retry_after(self):
        provider = HttpProvider()
        limited = urllib.error.HTTPError(
            "https://example.test",
            429,
            "Too Many Requests",
            {"Retry-After": "2"},
            io.BytesIO(),
        )
        with patch("scansci_find.adapters.urllib.request.urlopen", side_effect=[limited, FakeResponse({"ok": True})]), patch(
            "scansci_find.adapters.time.sleep"
        ) as sleep:
            payload = provider._json("https://example.test")

        self.assertEqual(payload, {"ok": True})
        sleep.assert_called_once_with(2.0)

    def test_openalex_fails_explicitly_without_required_key(self):
        with patch.dict(os.environ, {"OPENALEX_API_KEY": ""}):
            with self.assertRaisesRegex(ProviderConfigurationError, "requires OPENALEX_API_KEY"):
                OpenAlexProvider().search("urban ecology", 10)

    def test_openalex_uses_current_key_and_pagination_parameters(self):
        provider = OpenAlexProvider()
        provider._json = Mock(return_value={"results": [], "meta": {"count": 0, "next_cursor": None}})
        with patch.dict(os.environ, {"OPENALEX_API_KEY": "test-key"}):
            provider.search("urban ecology", 500)

        url = provider._json.call_args.args[0]
        params = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        self.assertEqual(params["api_key"], ["test-key"])
        self.assertEqual(params["per_page"], ["100"])
        self.assertTrue(provider.last_search_metadata["pagination_complete"])

    def test_openalex_follows_cursor_until_the_requested_budget_is_filled(self):
        provider = OpenAlexProvider()
        provider._json = Mock(
            side_effect=[
                {"results": [{"title": f"Paper {index}"} for index in range(100)], "meta": {"count": 150, "next_cursor": "next-page"}},
                {"results": [{"title": f"Paper {index}"} for index in range(100, 150)], "meta": {"count": 150, "next_cursor": None}},
            ]
        )
        with patch.dict(os.environ, {"OPENALEX_API_KEY": "test-key"}):
            rows = provider.search("urban ecology", 150)

        self.assertEqual(len(rows), 150)
        self.assertEqual(provider._json.call_count, 2)
        second_url = provider._json.call_args_list[1].args[0]
        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlparse(second_url).query)["cursor"], ["next-page"])
        self.assertTrue(provider.last_search_metadata["pagination_complete"])

    def test_semantic_scholar_sends_optional_api_key_as_header(self):
        provider = SemanticScholarProvider()
        provider._json = Mock(return_value={"data": [], "total": 0})
        with patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "s2-key"}):
            provider.search("retrieval", 5)

        self.assertEqual(provider._json.call_args.kwargs["headers"], {"x-api-key": "s2-key"})

    def test_semantic_scholar_uses_offsets_for_multi_page_budgets(self):
        provider = SemanticScholarProvider()
        provider._json = Mock(
            side_effect=[
                {"data": [{"title": f"Paper {index}"} for index in range(100)], "total": 150},
                {"data": [{"title": f"Paper {index}"} for index in range(100, 150)], "total": 150},
            ]
        )
        rows = provider.search("retrieval", 150)

        self.assertEqual(len(rows), 150)
        second_url = provider._json.call_args_list[1].args[0]
        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlparse(second_url).query)["offset"], ["100"])
        self.assertTrue(provider.last_search_metadata["pagination_complete"])

    def test_pubmed_propagates_optional_api_key_to_search_and_summary(self):
        provider = PubMedProvider()
        provider._json = Mock(
            side_effect=[
                {"esearchresult": {"count": "1", "idlist": ["123"]}},
                {"result": {"123": {"uid": "123", "title": "Paper"}}},
            ]
        )
        with patch.dict(os.environ, {"NCBI_API_KEY": "ncbi-key", "NCBI_EMAIL": "researcher@example.org"}):
            rows = provider.search("pollinators", 5)

        self.assertEqual(len(rows), 1)
        for call in provider._json.call_args_list:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(call.args[0]).query)
            self.assertEqual(params["api_key"], ["ncbi-key"])
            self.assertEqual(params["email"], ["researcher@example.org"])


if __name__ == "__main__":
    unittest.main()
