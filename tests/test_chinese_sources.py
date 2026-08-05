import importlib
import os
import unittest
from unittest.mock import patch


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


class ChineseSourceTests(unittest.TestCase):
    def test_baidu_scholar_records_normalize_to_chinese_candidate_contract(self):
        normalize_baidu = require("scansci_find.adapters.normalize_baidu_scholar_record")

        candidate = normalize_baidu(
            {
                "title": "城市热岛遥感研究",
                "authors": ["张三", "李四"],
                "publishYear": "2025",
                "paperId": "BD123",
                "url": "https://xueshu.baidu.com/usercenter/paper/show?paperid=BD123",
                "abstract": "摘要文本",
                "keywords": ["城市热岛", "遥感"],
                "source": "CNKI",
            }
        )

        self.assertEqual(candidate["title_zh"], "城市热岛遥感研究")
        self.assertEqual(candidate["source_platform"], "baidu_scholar")
        self.assertEqual(candidate["source_record_id"], "BD123")
        self.assertEqual(candidate["source_url"], "https://xueshu.baidu.com/usercenter/paper/show?paperid=BD123")
        self.assertEqual(candidate["article_type"], "journal")
        self.assertEqual(candidate["access"]["fulltext_hint"], "unknown")
        self.assertFalse(candidate["access"]["requires_login"])
        self.assertIn("Baidu Scholar", candidate["source_hits"])

    def test_cli_accepts_chinese_routing_options_and_comma_sources(self):
        build_parser = require("scansci_find.cli.build_parser")
        resolve_sources = require("scansci_find.cli.resolve_sources")

        args = build_parser().parse_args(
            [
                "search",
                "城市热岛 遥感",
                "--cn",
                "--source",
                "cnki,baidu-scholar",
                "--doc-type",
                "journal",
                "--field",
                "title",
                "--year",
                "2020:2026",
                "--access",
                "institution",
                "--exclude-warning",
                "--out",
                "runs/cn",
            ]
        )

        self.assertTrue(args.cn)
        self.assertEqual(resolve_sources(args), ["cnki", "baidu-scholar"])
        self.assertEqual(args.doc_type, "journal")
        self.assertEqual(args.field, "title")
        self.assertEqual(args.year, "2020:2026")
        self.assertEqual(args.access, "institution")
        self.assertTrue(args.exclude_warning)

    def test_chinese_title_dedupe_uses_title_author_and_year_without_collapsing_unrelated_titles(self):
        dedupe_candidates = require("scansci_find.dedupe.dedupe_candidates")

        candidates = [
            {
                "title": "《城市热岛遥感研究》",
                "authors": ["张三", "李四"],
                "year": 2025,
                "doi": "",
                "arxiv_id": "",
                "journal": "地理科学",
                "source_platform": "cnki",
                "source_record_id": "",
                "source_hits": ["CNKI"],
                "relevance_score": 0.7,
                "links": {},
            },
            {
                "title": "城市热岛 遥感研究",
                "authors": ["张三"],
                "year": 2025,
                "doi": "",
                "arxiv_id": "",
                "journal": "地理科学",
                "source_platform": "baidu_scholar",
                "source_record_id": "",
                "source_hits": ["Baidu Scholar"],
                "relevance_score": 0.6,
                "links": {},
            },
            {
                "title": "县域碳排放产业结构",
                "authors": ["王五"],
                "year": 2025,
                "doi": "",
                "arxiv_id": "",
                "journal": "生态经济",
                "source_platform": "cnki",
                "source_record_id": "",
                "source_hits": ["CNKI"],
                "relevance_score": 0.5,
                "links": {},
            },
        ]

        deduped = dedupe_candidates(candidates)

        self.assertEqual(len(deduped), 2)
        first = next(item for item in deduped if item["journal"] == "地理科学")
        self.assertEqual(first["source_hits"], ["Baidu Scholar", "CNKI"])

    def test_baidu_provider_requires_api_key_and_never_logs_key_value(self):
        BaiduScholarProvider = require("scansci_find.adapters.BaiduScholarProvider")

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                BaiduScholarProvider().search("人工智能", 1)

        message = str(ctx.exception)
        self.assertIn("BAIDU_API_KEY", message)
        self.assertNotIn("Bearer", message)

    def test_cnki_provider_requires_external_mcp_command_instead_of_scraping_in_tree(self):
        CNKIMcpProvider = require("scansci_find.adapters.CNKIMcpProvider")

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                CNKIMcpProvider().search("人工智能", 1)

        self.assertIn("SCANSCI_FIND_CNKI_MCP_COMMAND", str(ctx.exception))

    def test_paper_candidate_without_artifact_type_does_not_enter_data_queue(self):
        build_data_queue = require("scansci_find.outputs.build_data_queue")

        queue = build_data_queue(
            [
                {
                    "title": "A paper without explicit artifact type",
                    "doi": "10.1234/paper",
                    "links": {"paper": "https://doi.org/10.1234/paper"},
                    "source_hits": ["OpenAlex"],
                }
            ]
        )

        self.assertEqual(queue, [])


if __name__ == "__main__":
    unittest.main()
