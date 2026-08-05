import importlib
import unittest


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


class FakeJournalScoutGateway:
    version = "journal-scout-test"

    def __init__(self):
        self.data_sha256 = "sha256-test"

    def health_check(self):
        return {
            "server_version": self.version,
            "data": {"sha256": self.data_sha256, "journal_count": 2},
            "policies": ["high_quality_broad"],
        }

    def screen_papers(self, papers, policy=None, filters=None):
        results = []
        for paper in papers:
            passed = paper.get("journal") == "Global Change Biology"
            journal = {
                "title": paper.get("journal") or "",
                "if_2023": 12.1 if passed else 1.2,
                "if_year": "2024",
                "if_history": [
                    {"year": "2024", "if_value": 12.1 if passed else 1.2, "quartile": "Q1" if passed else "Q4"}
                ],
                "jcr_quartile": "Q1" if passed else "Q4",
                "cas_2025": "1区" if passed else "4区",
                "sources": ["showjcr:JCR2024"],
            }
            results.append(
                {
                    "paper": paper,
                    "matched_journal": journal["title"],
                    "passed": passed,
                    "policy_result": {
                        "policy": policy or "custom_filters",
                        "pass": passed,
                        "reasons": ["JCR Q1"] if passed else ["未满足 high_quality_broad"],
                        "evidence": journal,
                    },
                }
            )
        return {
            "data": {"sha256": self.data_sha256, "journal_count": 2},
            "policy": policy,
            "results": results,
        }


class QualityTests(unittest.TestCase):
    def candidate(self, journal):
        return {
            "title": f"Paper in {journal}",
            "authors": ["Ada Li"],
            "year": 2025,
            "doi": f"10.1234/{journal.replace(' ', '-').lower()}",
            "arxiv_id": "",
            "journal": journal,
            "issn": "",
            "eissn": "",
            "source_hits": ["OpenAlex"],
            "relevance_score": 0.5,
            "links": {},
        }

    def test_journal_scout_if_fields_are_mapped_to_jif_latest(self):
        map_jif = require("scansci_find.quality.map_jif")

        result = map_jif({"if_2023": 12.1, "if_year": "2024", "if_history": [{"year": "2024", "if_value": 12.1}]})

        self.assertEqual(result["value"], 12.1)
        self.assertEqual(result["year"], "2024")
        self.assertEqual(result["source"], "JCR")
        self.assertEqual(result["raw_fields"]["if_2023"], 12.1)

    def test_boost_mode_keeps_failed_candidates_but_marks_quality_and_boosts_passed(self):
        apply_quality = require("scansci_find.quality.apply_quality")
        candidates = [self.candidate("Global Change Biology"), self.candidate("Unknown Journal")]

        screened = apply_quality(candidates, FakeJournalScoutGateway(), policy="high_quality_broad", mode="boost")

        self.assertEqual(len(screened), 2)
        self.assertTrue(screened[0]["quality"]["passed"])
        self.assertFalse(screened[1]["quality"]["passed"])
        self.assertGreater(screened[0]["relevance_score"], screened[1]["relevance_score"])
        self.assertEqual(screened[0]["quality"]["jif_latest"]["year"], "2024")
        self.assertEqual(screened[0]["quality"]["data_sha256"], "sha256-test")
        self.assertEqual(screened[0]["quality"]["journal_scout_version"], "journal-scout-test")

    def test_hard_mode_removes_failed_candidates(self):
        apply_quality = require("scansci_find.quality.apply_quality")
        candidates = [self.candidate("Global Change Biology"), self.candidate("Unknown Journal")]

        screened = apply_quality(candidates, FakeJournalScoutGateway(), policy="high_quality_broad", mode="hard")

        self.assertEqual([item["journal"] for item in screened], ["Global Change Biology"])

    def test_retrieval_filters_are_not_forwarded_to_journal_scout(self):
        _scout_filters = require("scansci_find.journal_scout._scout_filters")

        forwarded = _scout_filters(
            {
                "year": "2026:2026",
                "doc_type": "journal",
                "field": "title",
                "access": "oa",
                "exclude_warning": True,
                "jcr_quartile": ["Q1", "Q2"],
            }
        )

        self.assertEqual(forwarded, {"exclude_warning": True, "jcr_quartile": ["Q1", "Q2"]})

    def test_scout_filters_returns_none_when_no_supported_keys_remain(self):
        _scout_filters = require("scansci_find.journal_scout._scout_filters")

        self.assertIsNone(_scout_filters({"year": "2026:2026", "doc_type": "journal"}))
        self.assertIsNone(_scout_filters(None))
        self.assertIsNone(_scout_filters({}))


if __name__ == "__main__":
    unittest.main()

