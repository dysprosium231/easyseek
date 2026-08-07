import unittest

from scansci_find.evidence import _access_status, evidence_dimensions
from scansci_find.outputs import build_oa_manifest


def _candidate(doi="10.1000/x", status="unknown", pdf_url="", extra_access=None):
    access = {"access_status": status}
    if extra_access:
        access.update(extra_access)
    return {
        "title": "Paper",
        "doi": doi,
        "arxiv_id": "",
        "journal": "Journal",
        "source_hits": ["OpenAlex"],
        "access": access,
        "links": {"pdf": pdf_url} if pdf_url else {},
        "quality": {},
        "metrics": {},
    }


class AccessStatusTests(unittest.TestCase):
    def test_explicit_status_wins(self):
        candidate = _candidate(status="needs_institution")
        self.assertEqual(_access_status(candidate, candidate["access"]), "needs_institution")

    def test_legacy_oa_hint_maps_to_open_pdf(self):
        candidate = _candidate(status="", extra_access={"fulltext_hint": "oa"})
        self.assertEqual(_access_status(candidate, candidate["access"]), "open_pdf")

    def test_pdf_link_without_status_maps_to_open_pdf(self):
        candidate = _candidate(status="", pdf_url="https://example.org/paper.pdf")
        self.assertEqual(_access_status(candidate, candidate["access"]), "open_pdf")

    def test_institution_required_maps_to_needs_institution(self):
        candidate = _candidate(status="", extra_access={"fulltext_hint": "institution_required"})
        self.assertEqual(_access_status(candidate, candidate["access"]), "needs_institution")

    def test_evidence_availability_carries_status_enum(self):
        candidate = _candidate(status="preprint")
        evidence = evidence_dimensions(candidate)
        self.assertEqual(evidence["availability"]["status"], "preprint")
        self.assertEqual(evidence["availability"]["fulltext_hint"], "unknown")


class OaManifestTests(unittest.TestCase):
    def test_open_pdf_with_url_is_eligible(self):
        manifest = build_oa_manifest([_candidate(status="open_pdf", pdf_url="https://example.org/paper.pdf")])

        self.assertEqual(manifest["total"], 1)
        self.assertEqual(manifest["eligible"], 1)
        self.assertEqual(manifest["entries"][0]["download_status"], "eligible")
        self.assertEqual(manifest["entries"][0]["reason"], "")

    def test_preprint_with_url_is_eligible(self):
        manifest = build_oa_manifest([_candidate(status="preprint", pdf_url="https://arxiv.org/pdf/2401.00001")])
        self.assertEqual(manifest["eligible"], 1)

    def test_needs_institution_is_skipped_with_reason(self):
        manifest = build_oa_manifest([_candidate(status="needs_institution")])

        self.assertEqual(manifest["eligible"], 0)
        self.assertEqual(manifest["entries"][0]["download_status"], "skipped")
        self.assertIn("fulltext_status=needs_institution", manifest["entries"][0]["reason"])

    def test_open_pdf_without_url_is_skipped(self):
        manifest = build_oa_manifest([_candidate(status="open_pdf")])
        self.assertEqual(manifest["eligible"], 0)


if __name__ == "__main__":
    unittest.main()
