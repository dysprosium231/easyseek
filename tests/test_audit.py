import unittest

from scansci_find.audit import coverage_report, gold_set_report, prisma_counts
from scansci_find.protocol import build_protocol


class AuditTests(unittest.TestCase):
    def candidate(self, title="A Paper", doi="10.1000/a", sources=None):
        return {
            "title": title,
            "doi": doi,
            "arxiv_id": "",
            "pmid": "",
            "source_hits": sources or ["OpenAlex"],
            "screening": {},
        }

    def test_gold_set_recall_uses_verified_identifier_or_title(self):
        report = gold_set_report(
            [{"doi": "10.1000/A"}, {"title": "Missing paper"}],
            [self.candidate()],
        )

        self.assertEqual(report["found"], 1)
        self.assertEqual(report["recall"], 0.5)

    def test_systematic_label_is_withheld_when_sources_pagination_or_closure_are_incomplete(self):
        protocol = build_protocol("topic", depth="systematic", gold_set=[{"doi": "10.1000/a"}]).to_dict()
        report = coverage_report(
            protocol=protocol,
            source_status=[{"name": "openalex", "status": "ok", "count": 1, "message": ""}],
            raw_count=2,
            deduplicated_count=1,
            candidates=[self.candidate()],
            citation_rounds=[],
            pagination_complete=False,
        )

        self.assertFalse(report["systematic_complete"])
        self.assertEqual(report["method_status"], "bounded_search")
        self.assertIn("planned_sources_not_consulted", report["limitations"])
        self.assertIn("full_pagination_not_verified", report["limitations"])

    def test_prisma_counts_never_invent_screening_decisions(self):
        rows = [self.candidate(), self.candidate("B", "10.1000/b")]
        rows[0]["screening"] = {"decision": "include"}
        counts = prisma_counts(raw_count=4, deduplicated_count=2, candidates=rows, human_queue_count=1)

        self.assertEqual(counts["duplicates_removed"], 2)
        self.assertEqual(counts["included"], 1)
        self.assertEqual(counts["awaiting_screening"], 1)


if __name__ == "__main__":
    unittest.main()
