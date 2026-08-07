import unittest
from unittest.mock import patch

from scansci_find.service import ScanSciFindService
from scansci_find.two_pass import render_summary_markdown, summarize_candidates


class JournalGateway:
    def health_check(self):
        return {"server_version": "test", "data": {"sha256": "test"}}

    def screen_papers(self, papers, policy=None, filters=None):
        return {
            "results": [
                {
                    "passed": True,
                    "matched_journal": paper.get("journal") or "",
                    "policy_result": {"policy": policy, "pass": True, "reasons": [], "evidence": {}},
                }
                for paper in papers
            ]
        }


class Verifier:
    def verify(self, candidate):
        return {
            "status": "verified",
            "identifier_type": "doi",
            "identifier": candidate.get("doi", ""),
            "source": "Crossref",
            "checks": [],
        }


class OaResolver:
    def resolve_doi(self, doi):
        return {
            "status": "resolved",
            "source": "Unpaywall",
            "doi": doi,
            "is_oa": True,
            "oa_status": "green",
            "pdf_url": "https://repo.example/paper.pdf",
            "landing_page_url": "https://repo.example/paper",
            "license": "cc-by",
        }


class PreprintFinder:
    def _candidate_skippable(self, candidate):
        return False

    def find(self, candidate, per_source_limit=5):
        return [], {"arxiv": {"searched": 1, "errored": 0}}


class PwcProvider:
    def lookup(self, *, arxiv_id="", title=""):
        return None

    def repositories(self, paper_id):
        return []


def _candidate(title="Paper", year=2024, citations=0, published_date=""):
    return {
        "title": title,
        "authors": ["Ada Li"],
        "year": year,
        "doi": "10.1000/x",
        "arxiv_id": "",
        "journal": "Journal",
        "source_hits": ["OpenAlex"],
        "relevance_score": 0.5,
        "citation_count": citations,
        "published_date": published_date,
        "links": {},
        "access": {},
    }


class SummarizeTests(unittest.TestCase):
    def test_summary_rows_are_lightweight(self):
        summary = summarize_candidates([_candidate()])

        self.assertEqual(summary["total"], 1)
        row = summary["rows"][0]
        self.assertEqual(row["title"], "Paper")
        self.assertIn("year", row)
        self.assertIn("citation_count", row)
        self.assertNotIn("abstract", row)

    def test_summary_markdown_marks_recent_papers(self):
        from datetime import date, timedelta

        fresh = _candidate(title="Fresh", published_date=(date.today() - timedelta(days=10)).isoformat())
        from scansci_find.quality import mark_recent

        mark_recent(fresh)
        markdown = render_summary_markdown(summarize_candidates([fresh]))

        self.assertIn("[新]", markdown)


class TwoPassServiceTests(unittest.TestCase):
    def test_explore_returns_summary_with_markdown(self):
        retrieval = {
            "candidates": [_candidate(title="Heat mapping")],
            "source_status": [{"name": "openalex", "status": "ok", "count": 1, "pagination_complete": True}],
            "query_variants": ["heat"],
        }
        service = ScanSciFindService(journal_gateway=JournalGateway())

        with patch("scansci_find.service.search_query_variants_with_status", return_value=retrieval):
            result = service.explore("heat mapping", domain="general", limit=10)

        self.assertEqual(result["summary"]["total"], 1)
        self.assertIn("Pass 1", result["summary"]["markdown"])
        self.assertEqual(len(result["candidates"]), 1)

    def test_deep_fetch_runs_full_chain_and_renders_bibtex(self):
        service = ScanSciFindService(
            journal_gateway=JournalGateway(),
            identifier_verifier=Verifier(),
            oa_resolver=OaResolver(),
            preprint_finder=PreprintFinder(),
            pwc_provider=PwcProvider(),
        )

        result = service.deep_fetch([_candidate(title="Heat mapping")])

        self.assertEqual(result["reports"]["verification"]["status_counts"], {"verified": 1})
        self.assertEqual(result["reports"]["oa"]["oa_found"], 1)
        self.assertEqual(result["reports"]["preprints"]["matched"], 0)
        self.assertEqual(result["reports"]["code"]["matched"], 0)
        self.assertIn("@article", result["bibtex"])
        self.assertEqual(result["candidates"][0]["links"]["pdf"], "https://repo.example/paper.pdf")


if __name__ == "__main__":
    unittest.main()
