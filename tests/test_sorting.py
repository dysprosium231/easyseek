import unittest
from datetime import date, timedelta

from scansci_find.quality import VALID_SORTS, apply_quality, mark_recent


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


def _candidate(title, relevance, citations=0, published_date="", year=None):
    return {
        "title": title,
        "authors": ["Ada Li"],
        "year": year if year is not None else (int(published_date[:4]) if published_date else 2024),
        "doi": "",
        "arxiv_id": "",
        "journal": "Journal",
        "source_hits": ["OpenAlex"],
        "relevance_score": relevance,
        "citation_count": citations,
        "published_date": published_date,
        "links": {},
        "access": {},
    }


class SortingTests(unittest.TestCase):
    def test_citations_sort_orders_by_citation_count(self):
        rows = [
            _candidate("low", 0.9, citations=1),
            _candidate("high", 0.5, citations=99),
        ]

        screened = apply_quality(rows, JournalGateway(), sort="citations")

        self.assertEqual(screened[0]["title"], "high")

    def test_recency_sort_puts_recent_papers_first_regardless_of_relevance(self):
        old = _candidate("old-but-relevant", 0.9, published_date="2019-01-01")
        fresh = _candidate("fresh", 0.1, published_date=(date.today() - timedelta(days=30)).isoformat())

        screened = apply_quality([old, fresh], JournalGateway(), sort="recency")

        self.assertEqual(screened[0]["title"], "fresh")
        self.assertTrue(screened[0]["recency"]["is_recent"])
        self.assertFalse(screened[1]["recency"]["is_recent"])

    def test_recency_annotation_uses_year_approximation_when_date_missing(self):
        candidate = _candidate("recent-by-year", 0.5, year=date.today().year)

        mark_recent(candidate)

        self.assertTrue(candidate["recency"]["is_recent"])

    def test_recency_flag_is_false_for_old_papers(self):
        candidate = _candidate("old", 0.5, published_date="2020-06-01")

        mark_recent(candidate)

        self.assertFalse(candidate["recency"]["is_recent"])

    def test_boost_and_hard_semantics_survive_non_default_sorts(self):
        rows = [
            _candidate("a", 0.5, citations=1),
            _candidate("b", 0.5, citations=2),
        ]
        screened = apply_quality(rows, JournalGateway(), mode="boost", sort="citations")
        self.assertEqual([row["relevance_score"] for row in screened], [0.75, 0.75])

    def test_unknown_sort_raises(self):
        with self.assertRaises(ValueError):
            apply_quality([_candidate("a", 0.5)], JournalGateway(), sort="bogus")

    def test_valid_sorts_enum(self):
        self.assertEqual(set(VALID_SORTS), {"relevance", "recency", "citations"})


if __name__ == "__main__":
    unittest.main()
