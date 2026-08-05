import unittest

from scansci_find.adapters import search_query_variants_with_status


class RecordingProvider:
    def __init__(self):
        self.calls = []

    def search(self, query, limit):
        self.calls.append((query, limit))
        return [
            {
                "title": query,
                "authors": [],
                "year": 2025,
                "doi": "",
                "arxiv_id": "",
                "journal": "",
                "source_hits": ["recording"],
                "relevance_score": 1.0,
                "links": {},
            }
        ]


class QueryVariantTests(unittest.TestCase):
    def test_variants_are_executed_with_a_bounded_per_source_budget_and_audited(self):
        provider = RecordingProvider()
        result = search_query_variants_with_status(
            ["urban heat health", "urban heat mortality", "heat island health"],
            ["recording"],
            10,
            providers={"recording": provider},
        )

        self.assertEqual(len(provider.calls), 3)
        self.assertTrue(all(limit == 4 for _, limit in provider.calls))
        self.assertEqual(result["source_status"][0]["status"], "ok")
        self.assertEqual(len(result["source_status"][0]["queries"]), 3)
        self.assertFalse(result["source_status"][0]["pagination_complete"])
        self.assertIn("retrieval_queries", result["candidates"][0])


if __name__ == "__main__":
    unittest.main()
