import unittest

from scansci_find.adapters import ProviderNotFoundError, normalize_arxiv_entry, normalize_crossref_work, normalize_pubmed_record
from scansci_find.verification import IdentifierVerifier, verify_identifiers


class Lookup:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        self.calls = []

    def lookup_doi(self, value):
        self.calls.append(value)
        if self.error:
            raise self.error
        return self.value

    def lookup_pmid(self, value):
        self.calls.append(value)
        if self.error:
            raise self.error
        return self.value

    def lookup_arxiv(self, value):
        self.calls.append(value)
        if self.error:
            raise self.error
        return self.value


class VerificationTests(unittest.TestCase):
    def test_doi_is_verified_against_crossref_metadata(self):
        crossref = Lookup(
            normalize_crossref_work(
                {"title": ["Urban Heat and Health"], "DOI": "10.1000/HEAT", "issued": {"date-parts": [[2025]]}}
            )
        )
        verifier = IdentifierVerifier(crossref=crossref, pubmed=Lookup(), arxiv=Lookup())

        report = verifier.verify({"title": "Urban heat and health", "doi": "https://doi.org/10.1000/heat"})

        self.assertEqual(report["status"], "verified")
        self.assertEqual(report["source"], "Crossref")
        self.assertEqual(crossref.calls, ["10.1000/heat"])

    def test_resolved_identifier_with_conflicting_title_is_not_called_verified(self):
        crossref = Lookup(normalize_crossref_work({"title": ["Completely Different Study"], "DOI": "10.1000/heat"}))
        verifier = IdentifierVerifier(crossref=crossref, pubmed=Lookup(), arxiv=Lookup())

        report = verifier.verify({"title": "Urban heat and health", "doi": "10.1000/heat"})

        self.assertEqual(report["status"], "metadata_mismatch")
        self.assertTrue(report["identifier_match"])

    def test_not_found_is_distinguished_from_transport_failure(self):
        crossref = Lookup(error=ProviderNotFoundError("missing DOI"))
        verifier = IdentifierVerifier(crossref=crossref, pubmed=Lookup(), arxiv=Lookup())

        report = verifier.verify({"title": "Missing", "doi": "10.1000/missing"})

        self.assertEqual(report["status"], "not_found")

    def test_pmid_and_arxiv_are_supported_when_doi_is_absent(self):
        pubmed = Lookup(normalize_pubmed_record({"uid": "123", "title": "Medical Study"}))
        arxiv = Lookup(normalize_arxiv_entry({"arxiv_id": "2501.00001", "title": "Systems Study"}))
        verifier = IdentifierVerifier(crossref=Lookup(), pubmed=pubmed, arxiv=arxiv)

        self.assertEqual(verifier.verify({"title": "Medical Study", "pmid": "123"})["status"], "verified")
        self.assertEqual(verifier.verify({"title": "Systems Study", "arxiv_id": "2501.00001v2"})["status"], "verified")

    def test_batch_report_preserves_candidates_and_counts_statuses(self):
        class BatchVerifier:
            def verify(self, candidate):
                return {"status": "verified" if candidate.get("doi") else "unsupported"}

        result = verify_identifiers(
            [{"title": "A", "doi": "10.1/a"}, {"title": "B", "doi": ""}],
            verifier=BatchVerifier(),
        )

        self.assertEqual(result["checked"], 2)
        self.assertEqual(result["status_counts"], {"unsupported": 1, "verified": 1})
        self.assertIn("identifier_verification", result["candidates"][0])

    def test_all_available_identifiers_are_checked_and_partial_is_explicit(self):
        crossref = Lookup(normalize_crossref_work({"title": ["Shared Study"], "DOI": "10.1000/shared"}))
        pubmed = Lookup(error=ProviderNotFoundError("missing PMID"))
        verifier = IdentifierVerifier(crossref=crossref, pubmed=pubmed, arxiv=Lookup())

        report = verifier.verify(
            {"title": "Shared Study", "doi": "10.1000/shared", "pmid": "123456"}
        )

        self.assertEqual(report["status"], "partial")
        self.assertEqual([item["status"] for item in report["checks"]], ["verified", "not_found"])
        self.assertEqual(crossref.calls, ["10.1000/shared"])
        self.assertEqual(pubmed.calls, ["123456"])


if __name__ == "__main__":
    unittest.main()
