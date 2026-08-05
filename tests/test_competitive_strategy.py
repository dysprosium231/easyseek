import unittest
from pathlib import Path

from scansci_find.service import DEFAULT_SOURCES, ScanSciFindService


class CompetitiveStrategyTests(unittest.TestCase):
    def test_anysearch_is_optional_agent_search_infrastructure_not_default_science_source(self):
        service = ScanSciFindService(journal_gateway=None)

        sources = service.list_sources()

        self.assertNotIn("anysearch", DEFAULT_SOURCES)
        self.assertFalse(any(item["name"] == "anysearch" for item in sources["sources"]))
        anysearch = next(item for item in sources["optional_upstreams"] if item["name"] == "anysearch")
        self.assertEqual(anysearch["type"], "ai_agent_search_infrastructure")
        self.assertFalse(anysearch["enabled_by_default"])
        self.assertIn("vertical_domain_routing", anysearch["borrowed_strengths"])
        self.assertIn("batch_search", anysearch["borrowed_strengths"])
        self.assertIn("url_content_extraction", anysearch["borrowed_strengths"])
        self.assertIn("multi_runtime_cli", anysearch["borrowed_strengths"])
        self.assertIn("external_api_dependency", anysearch["limitations"])
        self.assertIn("no_local_journal_quality_database", anysearch["limitations"])

    def test_competitive_analysis_doc_records_anysearch_positioning_and_scan_sci_moat(self):
        doc = Path("docs/competitive-analysis.md")

        text = doc.read_text(encoding="utf-8")

        self.assertIn("anysearch-ai/anysearch-skill", text)
        self.assertIn("AI agent 搜索基础设施", text)
        self.assertIn("不是科研搜索竞品", text)
        self.assertIn("AnySearch: Search everything for agents.", text)
        self.assertIn("ScanSci Find: Find trusted science, quality-gated by Journal Scout, downloadable by ScanSci PDF.", text)
        self.assertIn("2671", text)
        self.assertIn("190", text)
        self.assertIn("2026-06-03T04:16:40Z", text)


if __name__ == "__main__":
    unittest.main()

