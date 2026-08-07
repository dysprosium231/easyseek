import unittest

from scansci_find.benchmark import DEFAULT_BENCHMARK_SOURCES, publisher_from_doi, run_benchmark, write_benchmark


class BenchmarkPublisherTests(unittest.TestCase):
    def test_publisher_from_doi_prefix(self):
        self.assertEqual(publisher_from_doi("10.1016/j.media.2024.103123"), "Elsevier")
        self.assertEqual(publisher_from_doi("10.1007/s10208-024-09600-0"), "Springer")
        self.assertEqual(publisher_from_doi("10.1109/TPAMI.2024.1234567"), "IEEE")
        self.assertEqual(publisher_from_doi("10.1038/s41586-024-00000-0"), "Nature")
        self.assertEqual(publisher_from_doi("10.1145/3613904.3642330"), "ACM")
        self.assertEqual(publisher_from_doi("10.48550/arXiv.2401.00001"), "arXiv")

    def test_unknown_doi_prefix_is_other(self):
        self.assertEqual(publisher_from_doi("10.9999/unknown"), "other")
        self.assertEqual(publisher_from_doi(""), "other")


class BenchmarkRunTests(unittest.TestCase):
    def test_run_benchmark_reports_coverage_per_source_and_publisher(self):
        providers = {
            "openalex": _FakeProvider(
                [
                    {"title": "A", "doi": "10.1016/j.x.1", "abstract": "abs", "source_hits": ["OpenAlex"]},
                    {"title": "B", "doi": "10.1016/j.x.2", "abstract": "", "source_hits": ["OpenAlex"]},
                ]
            ),
            "crossref": _FakeProvider(
                [
                    {"title": "C", "doi": "10.1016/j.x.3", "abstract": "abs", "source_hits": ["Crossref"]},
                ]
            ),
        }

        report = run_benchmark("test query", sources=["openalex", "crossref"], sample_size=10, providers=providers)

        self.assertEqual(report["record_count"], 3)
        by_source = {item["source"]: item for item in report["abstract_coverage"]["per_source"]}
        self.assertEqual(by_source["OpenAlex"]["coverage"], 0.5)
        by_publisher = {item["publisher"]: item for item in report["publisher_coverage"]}
        self.assertEqual(by_publisher["Elsevier"]["total"], 3)
        self.assertEqual(by_publisher["Elsevier"]["coverage"], round(2 / 3, 4))

    def test_default_sources_are_the_benchmark_backbone(self):
        self.assertEqual(DEFAULT_BENCHMARK_SOURCES, ["openalex", "crossref", "arxiv", "pubmed", "europe-pmc"])

    def test_write_benchmark_persists_json_and_markdown(self, tmp_path=None):
        import tempfile
        from pathlib import Path

        report = {"query": "q", "sources": ["openalex"], "abstract_coverage": {"per_source": []}, "publisher_coverage": []}
        with tempfile.TemporaryDirectory() as directory:
            artifact = write_benchmark(report, Path(directory))
            self.assertTrue(Path(directory, "benchmark_report.json").exists())
            self.assertTrue(Path(directory, "benchmark_report.md").exists())
            self.assertEqual(artifact.name, "benchmark_report.json")


class _FakeProvider:
    last_search_metadata = {}

    def __init__(self, rows):
        self._rows = rows

    def search(self, query, limit):
        self.last_search_metadata = {"returned": len(self._rows), "total_available": len(self._rows), "pagination_complete": True}
        return self._rows[:limit]


if __name__ == "__main__":
    unittest.main()
