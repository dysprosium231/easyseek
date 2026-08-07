import json
import unittest
from pathlib import Path

from scansci_find.reconcile import reconcile


def _candidate(doi="10.1000/x", arxiv_id=""):
    return {
        "title": "Paper",
        "authors": ["Ada Li"],
        "year": 2024,
        "doi": doi,
        "arxiv_id": arxiv_id,
        "journal": "Journal",
        "source_hits": ["OpenAlex"],
        "relevance_score": 0.5,
        "links": {},
        "access": {"fulltext_hint": "unknown", "requires_login": False, "requires_institution": False},
    }


def _entry(identifier, doi, success, error_type="", reason="", source=""):
    return {
        "identifier": identifier,
        "doi": doi,
        "success": success,
        "source": source,
        "file": "p.pdf" if success else "",
        "cached": False,
        "preprint_fallback": "",
        "error_type": error_type,
        "reason": reason,
    }


def _write_runs(tmp: Path, candidates, entries):
    (tmp / "candidates.json").write_text(json.dumps(candidates, ensure_ascii=False), encoding="utf-8")
    (tmp / "download_results.json").write_text(
        json.dumps({"service": "scansci-pdf", "entries": entries}, ensure_ascii=False), encoding="utf-8"
    )
    (tmp / "protocol.json").write_text(json.dumps({"query": "heat mapping"}), encoding="utf-8")


class ReconcileTests(unittest.TestCase):
    def test_success_writes_downloaded_status_and_source(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            candidates = [_candidate(doi="10.1000/x")]
            _write_runs(tmp, candidates, [_entry("10.1000/x", "10.1000/x", True, source="Sci-Hub(se)")])

            report = reconcile(tmp)

            self.assertEqual(report["updated"], 1)
            self.assertEqual(report["status_counts"], {"downloaded": 1})
            candidate = json.loads((tmp / "candidates.json").read_text(encoding="utf-8"))[0]
            self.assertEqual(candidate["access"]["access_status"], "downloaded")
            self.assertEqual(candidate["access"]["download_source"], "Sci-Hub(se)")
            self.assertTrue(candidate["access"]["download_checked"])
            self.assertTrue((tmp / "reconcile_report.json").exists())
            self.assertTrue((tmp / "evidence_table.csv").exists())

    def test_paywall_failure_maps_to_needs_institution(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            candidates = [_candidate(doi="10.1000/x")]
            _write_runs(tmp, candidates, [_entry("10.1000/x", "10.1000/x", False, error_type="paywall")])

            reconcile(tmp)

            candidate = json.loads((tmp / "candidates.json").read_text(encoding="utf-8"))[0]
            self.assertEqual(candidate["access"]["access_status"], "needs_institution")

    def test_cloudflare_failure_maps_to_anti_bot_blocked(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            candidates = [_candidate(doi="10.1000/x")]
            _write_runs(tmp, candidates, [_entry("10.1000/x", "10.1000/x", False, error_type="cloudflare_blocked")])

            reconcile(tmp)

            candidate = json.loads((tmp / "candidates.json").read_text(encoding="utf-8"))[0]
            self.assertEqual(candidate["access"]["access_status"], "anti_bot_blocked")

    def test_suspicious_pdf_maps_to_html_not_pdf(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            candidates = [_candidate(doi="10.1000/x")]
            _write_runs(tmp, candidates, [_entry("10.1000/x", "10.1000/x", False, error_type="suspicious_pdf")])

            reconcile(tmp)

            candidate = json.loads((tmp / "candidates.json").read_text(encoding="utf-8"))[0]
            self.assertEqual(candidate["access"]["access_status"], "html_not_pdf")

    def test_arxiv_candidates_match_by_arxiv_id(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            candidates = [_candidate(doi="", arxiv_id="2401.00001")]
            _write_runs(tmp, candidates, [_entry("2401.00001", "", True, source="arXiv")])

            report = reconcile(tmp)

            self.assertEqual(report["updated"], 1)

    def test_unmatched_candidates_are_left_untouched(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            candidates = [_candidate(doi="10.1000/x")]
            _write_runs(tmp, candidates, [_entry("10.9999/other", "10.9999/other", True)])

            report = reconcile(tmp)

            self.assertEqual(report["updated"], 0)
            candidate = json.loads((tmp / "candidates.json").read_text(encoding="utf-8"))[0]
            self.assertNotIn("download_checked", candidate["access"])

    def test_evidence_dimensions_are_recomputed(self):
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            tmp = Path(directory)
            candidates = [_candidate(doi="10.1000/x")]
            _write_runs(tmp, candidates, [_entry("10.1000/x", "10.1000/x", True, source="OA")])

            reconcile(tmp)

            candidate = json.loads((tmp / "candidates.json").read_text(encoding="utf-8"))[0]
            self.assertEqual(candidate["evidence_dimensions"]["availability"]["status"], "downloaded")


if __name__ == "__main__":
    unittest.main()
