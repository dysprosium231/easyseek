import importlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
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


FIXTURE = {
    "candidates": [
        {
            "title": "Urban ecology and pollinator diversity",
            "authors": ["Ada Li"],
            "year": 2025,
            "doi": "10.1234/example",
            "arxiv_id": "",
            "journal": "Global Change Biology",
            "issn": "1354-1013",
            "eissn": "1365-2486",
            "source_hits": ["fixture"],
            "relevance_score": 0.8,
            "links": {"paper": "https://doi.org/10.1234/example"},
        },
        {
            "title": "Urban ecology in an unknown journal",
            "authors": ["Bert Ng"],
            "year": 2024,
            "doi": "10.1234/unknown",
            "arxiv_id": "",
            "journal": "Unknown Journal",
            "issn": "",
            "eissn": "",
            "source_hits": ["fixture"],
            "relevance_score": 0.7,
            "links": {"paper": "https://doi.org/10.1234/unknown"},
        }
    ],
    "journal_scout": {
        "version": "journal-scout-test",
        "data_sha256": "sha256-test",
        "results": [
            {
                "matched_journal": "Global Change Biology",
                "passed": True,
                "policy_result": {
                    "policy": "high_quality_broad",
                    "pass": True,
                    "reasons": ["JCR Q1", "中科院1区"],
                    "evidence": {
                        "title": "Global Change Biology",
                        "if_2023": 12.1,
                        "if_year": "2024",
                        "if_history": [{"year": "2024", "if_value": 12.1}],
                        "jcr_quartile": "Q1",
                        "cas_2025": "1区",
                        "sources": ["showjcr:JCR2024"],
                    },
                },
            },
            {
                "matched_journal": "Unknown Journal",
                "passed": False,
                "policy_result": {
                    "policy": "high_quality_broad",
                    "pass": False,
                    "reasons": ["未满足 high_quality_broad"],
                    "evidence": {
                        "title": "Unknown Journal",
                        "if_2023": 1.0,
                        "if_year": "2024",
                        "if_history": [{"year": "2024", "if_value": 1.0}],
                    },
                },
            }
        ],
    },
}


class CliOutputTests(unittest.TestCase):
    def test_search_command_writes_expected_artifacts_from_fixture(self):
        cli_main = require("scansci_find.cli.main")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture_path = root / "fixture.json"
            out_dir = root / "run"
            fixture_path.write_text(json.dumps(FIXTURE), encoding="utf-8")

            exit_code = cli_main(
                [
                    "search",
                    "urban ecology pollinator diversity",
                    "--quality",
                    "high_quality_broad",
                    "--mode",
                    "boost",
                    "--out",
                    str(out_dir),
                    "--fixture",
                    str(fixture_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            for name in [
                "candidates.json",
                "candidates.jsonl",
                "download_queue.json",
                "papers.md",
                "quality_report.json",
                "refs.bib",
                "references.bib",
                "references.md",
                "dois.md",
                "protocol.json",
                "coverage_report.json",
                "coverage_report.md",
                "prisma.json",
                "PRISMA.md",
                "human_queue.csv",
                "evidence_table.csv",
                "zotero_items.json",
                "run_manifest.json",
                "citation_rounds.json",
                "identifier_verification.json",
                "oa_report.json",
            ]:
                self.assertTrue((out_dir / name).exists(), name)

            candidates = json.loads((out_dir / "candidates.json").read_text(encoding="utf-8"))
            self.assertEqual(candidates[0]["quality"]["jif_latest"]["value"], 12.1)
            self.assertEqual(candidates[0]["download"]["identifier"], "10.1234/example")
            self.assertTrue(candidates[0]["download"]["queue"])
            queue = json.loads((out_dir / "download_queue.json").read_text(encoding="utf-8"))
            self.assertEqual(queue[0]["identifier"], "10.1234/example")
            self.assertEqual(queue[0]["recommended_strategy"], "oa_first")
            paper_md = (out_dir / "papers.md").read_text(encoding="utf-8")
            self.assertIn("PASS", paper_md)
            self.assertIn("IF 12.1 (2024)", paper_md)
            refs = (out_dir / "refs.bib").read_text(encoding="utf-8")
            self.assertIn("@article{", refs)
            coverage = json.loads((out_dir / "coverage_report.json").read_text(encoding="utf-8"))
            self.assertEqual(coverage["method_status"], "bounded_search")
            self.assertFalse(coverage["systematic_complete"])
            manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertIn("run_manifest.json", manifest["artifacts"])

    def test_explicit_quality_defaults_to_hard_mode_when_mode_is_omitted(self):
        cli_main = require("scansci_find.cli.main")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture_path = root / "fixture.json"
            out_dir = root / "run"
            fixture_path.write_text(json.dumps(FIXTURE), encoding="utf-8")

            exit_code = cli_main(
                [
                    "search",
                    "urban ecology pollinator diversity",
                    "--quality",
                    "high_quality_broad",
                    "--out",
                    str(out_dir),
                    "--fixture",
                    str(fixture_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            candidates = json.loads((out_dir / "candidates.json").read_text(encoding="utf-8"))
            report = json.loads((out_dir / "quality_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["mode"], "hard")
            self.assertEqual([item["journal"] for item in candidates], ["Global Change Biology"])

    def test_browser_doctor_command_prints_shared_browser_discovery_json(self):
        cli_main = require("scansci_find.cli.main")
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = cli_main(["browser-doctor"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["profile_dir"], "D:/Dev/browser-profiles/scansci")
        self.assertEqual(payload["cache_dir"], "D:/Dev/cache/browser")
        self.assertIn("install_needed", payload)

    def test_estimate_command_can_persist_a_stage_report(self):
        cli_main = require("scansci_find.cli.main")

        class FakeService:
            def estimate_search(self, query, **kwargs):
                return {"stage": "estimate", "query": query, "size_band": "workable", "kwargs": kwargs}

        with tempfile.TemporaryDirectory() as tmp:
            out_path = Path(tmp) / "nested" / "estimate_report.json"
            with patch("scansci_find.cli.ScanSciFindService", return_value=FakeService()):
                exit_code = cli_main(
                    [
                        "estimate",
                        "urban heat",
                        "--domain",
                        "environmental_science",
                        "--out",
                        str(out_path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["stage"], "estimate")
            self.assertEqual(payload["size_band"], "workable")

    def test_verify_command_accepts_jsonl_candidate_input(self):
        cli_main = require("scansci_find.cli.main")

        class FakeService:
            def verify_identifiers(self, candidates, limit=None):
                self.received = candidates
                return {"candidates": candidates, "checked": len(candidates), "unchecked": 0, "all_verified": True}

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidates = [{"title": "Urban ecology", "doi": "10.1234/a"}, {"title": "Pollinator study", "doi": "10.1234/b"}]
            jsonl_path = root / "candidates.jsonl"
            jsonl_path.write_text("\n".join(json.dumps(item) for item in candidates) + "\n", encoding="utf-8")
            out_path = root / "verify_report.json"

            service = FakeService()
            with patch("scansci_find.cli.ScanSciFindService", return_value=service):
                exit_code = cli_main(["verify", str(jsonl_path), "--out", str(out_path)])

            self.assertEqual(exit_code, 0)
            self.assertEqual([item["doi"] for item in service.received], ["10.1234/a", "10.1234/b"])
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertTrue(payload["all_verified"])

    def test_verify_command_accepts_json_object_with_candidates_list(self):
        cli_main = require("scansci_find.cli.main")

        class FakeService:
            def verify_identifiers(self, candidates, limit=None):
                self.received = candidates
                return {"candidates": candidates, "checked": len(candidates), "unchecked": 0, "all_verified": True}

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            json_path = root / "candidates.json"
            json_path.write_text(json.dumps({"candidates": [{"title": "Urban ecology", "doi": "10.1234/a"}]}), encoding="utf-8")

            service = FakeService()
            with patch("scansci_find.cli.ScanSciFindService", return_value=service):
                exit_code = cli_main(["verify", str(json_path)])

            self.assertEqual(exit_code, 0)
            self.assertEqual([item["doi"] for item in service.received], ["10.1234/a"])


if __name__ == "__main__":
    unittest.main()
