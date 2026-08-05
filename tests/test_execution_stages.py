import unittest

from scansci_find.adapters import normalize_crossref_work
from scansci_find.service import ScanSciFindService


class StageProvider:
    def __init__(self, total=123, source_hits=None):
        self.total = total
        self.source_hits = source_hits or ["Crossref", "OpenAlex"]
        self.last_search_metadata = {}
        self.calls = []

    def search(self, query, limit):
        self.calls.append((query, limit))
        count = min(limit, 3)
        self.last_search_metadata = {
            "returned": count,
            "total_available": self.total,
            "pagination_complete": count >= self.total,
            "pagination": "fixture",
        }
        rows = []
        for index in range(count):
            row = normalize_crossref_work(
                {
                    "title": [f"{query} {index}"],
                    "author": [{"given": "Ada", "family": "Li"}],
                    "issued": {"date-parts": [[2025]]},
                    "DOI": f"10.1000/{index}",
                    "container-title": ["Example Journal"],
                }
            )
            row["source_hits"] = list(self.source_hits)
            rows.append(row)
        return rows


class ExecutionStageTests(unittest.TestCase):
    def service(self, provider=None):
        return ScanSciFindService(journal_gateway=object(), providers={"crossref": provider or StageProvider()})

    def test_estimate_search_reports_known_counts_and_size_band(self):
        result = self.service(StageProvider(total=123)).estimate_search(
            "urban heat",
            sources=["crossref"],
        )

        self.assertEqual(result["known_source_total"], 123)
        self.assertEqual(result["size_band"], "narrow")
        self.assertEqual(result["estimates"][0]["estimate_status"], "reported")

    def test_smoke_search_checks_source_and_candidate_contracts(self):
        result = self.service().smoke_search("urban heat", sources=["crossref"])

        self.assertTrue(result["contract_ok"])
        self.assertEqual(result["records_per_source"], 4)
        self.assertEqual(result["candidate_contract_errors"], [])

    def test_calibration_recommends_proceed_when_queue_rate_is_below_threshold(self):
        result = self.service().calibrate_search(
            "urban heat",
            sources=["crossref"],
            sample_size=10,
            human_queue_threshold=0.15,
        )

        self.assertEqual(result["calibration_status"], "proceed")
        self.assertEqual(result["human_queue_rate"], 0)
        self.assertEqual(result["per_source_budget"], 10)


if __name__ == "__main__":
    unittest.main()
