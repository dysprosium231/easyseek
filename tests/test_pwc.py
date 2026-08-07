import unittest
from unittest.mock import Mock

from scansci_find.pwc import PwcProvider, enrich_code_availability


class PwcTests(unittest.TestCase):
    def test_lookup_uses_arxiv_id_endpoint(self):
        provider = PwcProvider()
        provider._json = Mock(
            return_value={
                "results": [
                    {"id": "attention-is-all-you-need", "title": "Attention Is All You Need", "url": "https://paperswithcode.com/paper/attention-is-all-you-need"}
                ]
            }
        )

        paper = provider.lookup(arxiv_id="https://arxiv.org/abs/1706.03762")

        self.assertIsNotNone(paper)
        url = provider._json.call_args.args[0]
        self.assertIn("arxiv_id=1706.03762", url)
        self.assertEqual(paper["id"], "attention-is-all-you-need")

    def test_repositories_requests_the_paper_repo_endpoint(self):
        provider = PwcProvider()
        provider._json = Mock(return_value={"repositories": []})

        provider.repositories("attention-is-all-you-need")

        url = provider._json.call_args.args[0]
        self.assertIn("/papers/attention-is-all-you-need/repositories/", url)

    def test_enrich_attaches_best_repository_official_first(self):
        provider = PwcProvider()
        provider._json = Mock(
            side_effect=[
                {"results": [{"id": "paper-x", "url": "https://paperswithcode.com/paper/x"}]},
                {
                    "repositories": [
                        {"url": "https://github.com/fork/x", "stars": 500, "framework": "PyTorch", "is_official": False},
                        {"url": "https://github.com/official/x", "stars": 1200, "framework": "TensorFlow", "is_official": True},
                    ]
                },
            ]
        )
        candidate = {"title": "Paper X", "arxiv_id": "2401.00001", "source_hits": ["OpenAlex"], "links": {}}

        result = enrich_code_availability([candidate], provider=provider)

        self.assertEqual(result["matched"], 1)
        self.assertEqual(result["status_counts"], {"matched": 1})
        code = result["candidates"][0]["code"]
        self.assertEqual(code["url"], "https://github.com/official/x")
        self.assertTrue(code["is_official"])
        self.assertEqual(code["stars"], 1200)

    def test_enrich_reports_no_code_when_repositories_empty(self):
        provider = PwcProvider()
        provider._json = Mock(
            side_effect=[
                {"results": [{"id": "paper-x", "url": "https://paperswithcode.com/paper/x"}]},
                {"repositories": []},
            ]
        )

        result = enrich_code_availability([{"title": "Paper X", "arxiv_id": "2401.00002"}], provider=provider)

        self.assertEqual(result["status_counts"], {"no_code": 1})
        self.assertEqual(result["matched"], 0)


if __name__ == "__main__":
    unittest.main()
