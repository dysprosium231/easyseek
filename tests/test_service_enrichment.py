import unittest
from unittest.mock import patch

from scansci_find.adapters import normalize_crossref_work
from scansci_find.service import ScanSciFindService


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
            "identifier": candidate["doi"],
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
            "pdf_url": "https://repository.example/paper.pdf",
            "landing_page_url": "https://repository.example/paper",
            "license": "cc-by",
        }


class ServiceEnrichmentTests(unittest.TestCase):
    def test_search_can_verify_identifiers_and_resolve_oa_in_one_run(self):
        candidate = normalize_crossref_work(
            {
                "title": ["Urban Heat Study"],
                "author": [{"given": "Ada", "family": "Li"}],
                "issued": {"date-parts": [[2025]]},
                "DOI": "10.1000/heat",
                "container-title": ["Example Journal"],
            }
        )
        retrieval = {
            "candidates": [candidate],
            "source_status": [
                {
                    "name": "crossref",
                    "status": "ok",
                    "count": 1,
                    "pagination_complete": True,
                }
            ],
            "query_variants": ["urban heat"],
        }
        service = ScanSciFindService(
            journal_gateway=JournalGateway(),
            identifier_verifier=Verifier(),
            oa_resolver=OaResolver(),
        )

        with patch("scansci_find.service.search_query_variants_with_status", return_value=retrieval):
            result = service.search_academic(
                "urban heat",
                depth="quick",
                sources=["crossref"],
                verify_candidate_identifiers=True,
                resolve_oa=True,
            )

        row = result["candidates"][0]
        self.assertEqual(result["verification_report"]["status_counts"], {"verified": 1})
        self.assertEqual(result["oa_report"]["oa_found"], 1)
        self.assertEqual(row["links"]["pdf"], "https://repository.example/paper.pdf")
        self.assertEqual(row["evidence_dimensions"]["identity"]["verification_status"], "verified")
        self.assertEqual(row["access"]["license"], "cc-by")


if __name__ == "__main__":
    unittest.main()
