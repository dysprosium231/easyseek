import importlib
import unittest


def require(name):
    module_name, attr_name = name.rsplit(".", 1)
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        raise AssertionError(f"expected module {module_name} to exist") from exc
    try:
        return getattr(module, attr_name)
    except AttributeError as exc:
        raise AssertionError(f"expected {name} to exist") from exc


class OkProvider:
    name = "ok"

    def search(self, query, limit):
        return [
            {
                "title": "A paper",
                "authors": [],
                "year": 2025,
                "doi": "10.1/ok",
                "arxiv_id": "",
                "journal": "Ecology",
                "issn": "",
                "eissn": "",
                "source_hits": ["ok"],
                "relevance_score": 1.0,
                "quality": {},
                "download": {},
                "links": {},
            }
        ]


class BadProvider:
    name = "bad"

    def search(self, query, limit):
        raise RuntimeError("rate limited")


class SourceStatusTests(unittest.TestCase):
    def test_search_sources_with_status_reports_failures_and_missing_sources(self):
        search_sources_with_status = require("scansci_find.adapters.search_sources_with_status")

        result = search_sources_with_status(
            "pollinators",
            ["ok", "bad", "missing"],
            5,
            providers={"ok": OkProvider(), "bad": BadProvider()},
        )

        self.assertEqual(len(result["candidates"]), 1)
        status = {item["name"]: item for item in result["source_status"]}
        self.assertEqual(status["ok"]["status"], "ok")
        self.assertEqual(status["ok"]["count"], 1)
        self.assertEqual(status["bad"]["status"], "error")
        self.assertIn("rate limited", status["bad"]["message"])
        self.assertEqual(status["missing"]["status"], "missing")


if __name__ == "__main__":
    unittest.main()
