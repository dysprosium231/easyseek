import os
import unittest
import urllib.parse
from unittest.mock import Mock, patch

from scansci_find.adapters import ProviderConfigurationError
from scansci_find.support_sources import UnpaywallProvider, resolve_open_access


class NoopResolver:
    def resolve_doi(self, doi):
        raise AssertionError("Unpaywall should not be called for an already-OA candidate")


class SupportSourceTests(unittest.TestCase):
    def test_unpaywall_requires_responsible_contact_email(self):
        with patch.dict(os.environ, {"UNPAYWALL_EMAIL": "", "SCANSCI_FIND_CONTACT_EMAIL": ""}):
            with self.assertRaises(ProviderConfigurationError):
                UnpaywallProvider().resolve_doi("10.1000/test")

    def test_unpaywall_uses_v2_doi_endpoint_and_normalizes_oa_result(self):
        provider = UnpaywallProvider(email="researcher@example.org")
        provider._json = Mock(
            return_value={
                "is_oa": True,
                "oa_status": "green",
                "data_standard": 2,
                "oa_locations": [{"url": "https://repo.example/landing"}],
                "best_oa_location": {
                    "url_for_pdf": "https://repo.example/paper.pdf",
                    "url_for_landing_page": "https://repo.example/landing",
                    "license": "cc-by",
                    "version": "acceptedVersion",
                    "host_type": "repository",
                },
            }
        )

        result = provider.resolve_doi("https://doi.org/10.1000/TEST")

        url = provider._json.call_args.args[0]
        self.assertIn("/v2/10.1000%2Ftest", url)
        self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["email"], ["researcher@example.org"])
        self.assertTrue(result["is_oa"])
        self.assertEqual(result["license"], "cc-by")

    def test_oa_resolution_enriches_links_without_overwriting_existing_pdf(self):
        class Resolver:
            def resolve_doi(self, doi):
                return {
                    "status": "resolved",
                    "source": "Unpaywall",
                    "doi": doi,
                    "is_oa": True,
                    "oa_status": "green",
                    "pdf_url": "https://repo.example/new.pdf",
                    "landing_page_url": "https://repo.example/landing",
                    "license": "cc-by",
                }

        result = resolve_open_access(
            [{"title": "Paper", "doi": "10.1000/test", "links": {"pdf": "https://existing.example/paper.pdf"}}],
            provider=Resolver(),
        )

        candidate = result["candidates"][0]
        self.assertEqual(candidate["links"]["pdf"], "https://existing.example/paper.pdf")
        self.assertEqual(candidate["access"]["fulltext_hint"], "oa")
        self.assertEqual(result["oa_found"], 1)

    def test_candidate_with_existing_oa_link_skips_unpaywall(self):
        class Resolver:
            def __init__(self):
                self.calls = []

            def resolve_doi(self, doi):
                self.calls.append(doi)
                raise AssertionError("Unpaywall should not be called for an already-OA candidate")

        resolver = Resolver()
        result = resolve_open_access(
            [
                {
                    "title": "Paper",
                    "doi": "10.1000/test",
                    "source_hits": ["OpenAlex"],
                    "links": {"pdf": "https://api.openalex.org/oa.pdf"},
                }
            ],
            provider=resolver,
        )

        candidate = result["candidates"][0]
        self.assertEqual(resolver.calls, [])
        self.assertTrue(candidate["oa_resolution"]["is_oa"])
        self.assertEqual(candidate["oa_resolution"]["source"], "openalex")
        self.assertEqual(candidate["access"]["fulltext_hint"], "oa")
        self.assertEqual(result["oa_found"], 1)
        self.assertEqual(result["resolvers_used"], {"openalex": 1})

    def test_europe_pmc_fulltext_link_is_attributed_to_europepmc(self):
        result = resolve_open_access(
            [
                {
                    "title": "Paper",
                    "doi": "10.1000/test",
                    "source_hits": ["Europe PMC"],
                    "links": {"fulltext": "https://europepmc.org/articles/PMC1234567"},
                }
            ],
            provider=NoopResolver(),
        )

        self.assertEqual(result["resolvers_used"], {"europepmc": 1})
        self.assertTrue(result["candidates"][0]["oa_resolution"]["is_oa"])

    def test_unresolved_candidates_still_call_unpaywall_and_are_counted(self):
        class Resolver:
            def __init__(self):
                self.calls = []

            def resolve_doi(self, doi):
                self.calls.append(doi)
                return {
                    "status": "resolved",
                    "source": "Unpaywall",
                    "doi": doi,
                    "is_oa": False,
                    "oa_status": "closed",
                    "pdf_url": "",
                    "landing_page_url": "",
                    "license": "",
                }

        resolver = Resolver()
        result = resolve_open_access(
            [
                {"title": "A", "doi": "10.1000/a", "links": {}},
                {"title": "B", "doi": "10.1000/b", "links": {}},
            ],
            provider=resolver,
        )

        self.assertEqual(resolver.calls, ["10.1000/a", "10.1000/b"])
        self.assertEqual(result["resolvers_used"], {"unpaywall": 2})
        self.assertEqual(result["status_counts"], {"resolved": 2})
        self.assertEqual(result["oa_found"], 0)


if __name__ == "__main__":
    unittest.main()
