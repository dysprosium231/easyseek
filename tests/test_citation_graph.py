import unittest
from unittest.mock import Mock

from scansci_find.citation_graph import (
    CompositeCitationProvider,
    OpenCitationsCitationProvider,
    build_citation_provider,
    expand_citations,
)


class FakeCitationProvider:
    def expand(self, candidate, direction, limit):
        if candidate.get("doi") == "10.1000/seed":
            return [
                {
                    "title": "Citing paper",
                    "authors": ["Ada Li"],
                    "year": 2025,
                    "doi": "10.1000/new",
                    "arxiv_id": "",
                    "journal": "Journal",
                    "source_hits": ["Semantic Scholar"],
                    "relevance_score": 1.0,
                    "links": {},
                }
            ]
        return []


class CitationGraphTests(unittest.TestCase):
    def test_rounds_report_novelty_and_stop_at_saturation(self):
        seed = {
            "title": "Seed",
            "authors": ["Bert Ng"],
            "year": 2024,
            "doi": "10.1000/seed",
            "arxiv_id": "",
            "journal": "Journal",
            "source_hits": ["OpenAlex"],
            "relevance_score": 1.0,
            "links": {},
        }
        result = expand_citations([seed], rounds=3, provider=FakeCitationProvider(), saturation_threshold=0.01)

        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(result["rounds"][0]["new_unique_records"], 1)
        self.assertEqual(result["rounds"][1]["new_unique_records"], 0)
        self.assertTrue(result["saturated"])

    def test_opencitations_resolves_relation_metadata_and_audit_fields(self):
        provider = OpenCitationsCitationProvider(access_token="test-token")
        provider._json = Mock(
            side_effect=[
                [
                    [
                        {
                            "citing": "doi:10.1000/seed",
                            "cited": "doi:10.1000/reference",
                            "oci": "020010-test",
                            "creation": "2024-03-01",
                            "timespan": "P2Y",
                        }
                    ]
                ],
                [
                    {
                        "id": "doi:10.1000/reference pmid:123456",
                        "title": "Reference paper",
                        "author": "Li, Ada [orcid:0000-0001]; Ng, Bert",
                        "pub_date": "2022-06-01",
                        "venue": "Example Journal [issn:1234-5678]",
                        "type": "journal article",
                    }
                ],
            ]
        )

        rows = provider.expand({"doi": "10.1000/seed", "canonical_id": "doi:10.1000/seed"}, "backward", 20)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["doi"], "10.1000/reference")
        self.assertEqual(rows[0]["pmid"], "123456")
        self.assertEqual(rows[0]["authors"], ["Li, Ada", "Ng, Bert"])
        self.assertEqual(rows[0]["discovery"]["direction"], "backward")
        self.assertEqual(rows[0]["citation_relation"]["oci"], "020010-test")
        index_call, metadata_call = provider._json.call_args_list
        self.assertIn("/index/v2/references/doi:10.1000/seed", index_call.args[0])
        self.assertEqual(index_call.kwargs["headers"], {"authorization": "test-token"})
        self.assertIn("/meta/v1/metadata/doi:10.1000/reference", metadata_call.args[0])

    def test_composite_provider_records_partial_failure_without_losing_results(self):
        class BrokenProvider:
            name = "broken"

            def expand(self, candidate, direction, limit):
                raise RuntimeError("temporary outage")

        provider = CompositeCitationProvider([BrokenProvider(), FakeCitationProvider()])
        seed = {
            "title": "Seed",
            "authors": ["Bert Ng"],
            "year": 2024,
            "doi": "10.1000/seed",
            "arxiv_id": "",
            "journal": "Journal",
            "source_hits": ["OpenAlex"],
            "relevance_score": 1.0,
            "links": {},
        }

        result = expand_citations([seed], rounds=1, provider=provider)

        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(result["failures"][0]["provider"], "broken")
        self.assertEqual(result["citation_source"], "both")

    def test_opencitations_keeps_minimal_relation_when_meta_is_unavailable(self):
        provider = OpenCitationsCitationProvider()
        provider._json = Mock(
            side_effect=[
                [{"citing": "doi:10.1000/seed", "cited": "doi:10.1000/reference", "oci": "test"}],
                RuntimeError("meta unavailable"),
            ]
        )

        result = expand_citations(
            [{"title": "Seed", "doi": "10.1000/seed", "source_hits": ["fixture"], "links": {}}],
            rounds=1,
            direction="backward",
            provider=provider,
        )

        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(result["failures"][0]["provider"], "opencitations-meta")
        self.assertEqual(result["failures"][0]["error_type"], "RuntimeError")

    def test_citation_provider_factory_rejects_unknown_source(self):
        with self.assertRaisesRegex(ValueError, "semantic, opencitations, or both"):
            build_citation_provider("unknown")


if __name__ == "__main__":
    unittest.main()
