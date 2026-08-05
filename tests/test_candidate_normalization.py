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


class CandidateNormalizationTests(unittest.TestCase):
    def test_openalex_crossref_semantic_and_arxiv_records_share_candidate_shape(self):
        normalize_openalex = require("scansci_find.adapters.normalize_openalex_work")
        normalize_crossref = require("scansci_find.adapters.normalize_crossref_work")
        normalize_semantic = require("scansci_find.adapters.normalize_semantic_paper")
        normalize_arxiv = require("scansci_find.adapters.normalize_arxiv_entry")

        openalex = normalize_openalex(
            {
                "title": "Urban ecology and pollinator diversity",
                "publication_year": 2025,
                "doi": "https://doi.org/10.1234/example",
                "authorships": [{"author": {"display_name": "Ada Li"}}],
                "primary_location": {
                    "source": {
                        "display_name": "Global Change Biology",
                        "issn_l": "1354-1013",
                        "issn": ["1354-1013", "1365-2486"],
                    }
                },
                "open_access": {"oa_url": "https://example.test/paper.pdf"},
                "id": "https://openalex.org/W1",
            }
        )
        crossref = normalize_crossref(
            {
                "title": ["Urban ecology and pollinator diversity"],
                "issued": {"date-parts": [[2025, 1, 2]]},
                "DOI": "10.1234/example",
                "author": [{"given": "Ada", "family": "Li"}],
                "container-title": ["Global Change Biology"],
                "ISSN": ["1354-1013", "1365-2486"],
                "URL": "https://doi.org/10.1234/example",
            }
        )
        semantic = normalize_semantic(
            {
                "title": "Urban ecology and pollinator diversity",
                "year": 2025,
                "externalIds": {"DOI": "10.1234/example"},
                "authors": [{"name": "Ada Li"}],
                "journal": {"name": "Global Change Biology"},
                "openAccessPdf": {"url": "https://example.test/paper.pdf"},
                "url": "https://semanticscholar.org/paper/1",
            }
        )
        arxiv = normalize_arxiv(
            {
                "title": "Urban ecology and pollinator diversity",
                "year": 2025,
                "arxiv_id": "2501.00001v2",
                "authors": ["Ada Li"],
                "url": "https://arxiv.org/abs/2501.00001v2",
                "pdf_url": "https://arxiv.org/pdf/2501.00001v2",
            }
        )

        for candidate in [openalex, crossref, semantic, arxiv]:
            with self.subTest(source=candidate["source_hits"]):
                self.assertEqual(candidate["title"], "Urban ecology and pollinator diversity")
                self.assertIn("authors", candidate)
                self.assertIn("year", candidate)
                self.assertIn("doi", candidate)
                self.assertIn("arxiv_id", candidate)
                self.assertIn("journal", candidate)
                self.assertIn("issn", candidate)
                self.assertIn("eissn", candidate)
                self.assertIn("source_hits", candidate)
                self.assertIn("relevance_score", candidate)
                self.assertIn("links", candidate)

        self.assertEqual(openalex["doi"], "10.1234/example")
        self.assertEqual(crossref["issn"], "1354-1013")
        self.assertEqual(crossref["eissn"], "1365-2486")
        self.assertEqual(semantic["journal"], "Global Change Biology")
        self.assertEqual(arxiv["arxiv_id"], "2501.00001")

    def test_dedupe_prefers_doi_then_arxiv_then_normalized_title_and_accumulates_sources(self):
        dedupe_candidates = require("scansci_find.dedupe.dedupe_candidates")

        candidates = [
            {
                "title": "A Study",
                "authors": ["Ada Li"],
                "year": 2025,
                "doi": "https://doi.org/10.1000/ABC",
                "arxiv_id": "",
                "journal": "Nature",
                "issn": "0028-0836",
                "eissn": "",
                "source_hits": ["OpenAlex"],
                "relevance_score": 0.7,
                "links": {"paper": "https://openalex.org/W1"},
            },
            {
                "title": "A study",
                "authors": ["Ada Li", "Bert Ng"],
                "year": 2025,
                "doi": "10.1000/abc",
                "arxiv_id": "",
                "journal": "Nature",
                "issn": "",
                "eissn": "1476-4687",
                "source_hits": ["Crossref"],
                "relevance_score": 0.9,
                "links": {"doi": "https://doi.org/10.1000/abc"},
            },
            {
                "title": "Preprint Study",
                "authors": ["Cy Rao"],
                "year": 2024,
                "doi": "",
                "arxiv_id": "2401.00001v3",
                "journal": "",
                "issn": "",
                "eissn": "",
                "source_hits": ["arXiv"],
                "relevance_score": 0.6,
                "links": {},
            },
            {
                "title": "preprint study",
                "authors": ["Cy Rao"],
                "year": 2024,
                "doi": "",
                "arxiv_id": "2401.00001",
                "journal": "",
                "issn": "",
                "eissn": "",
                "source_hits": ["Semantic Scholar"],
                "relevance_score": 0.5,
                "links": {"paper": "https://example.test/preprint"},
            },
        ]

        deduped = dedupe_candidates(candidates)

        self.assertEqual(len(deduped), 2)
        doi_record = deduped[0]
        self.assertEqual(doi_record["doi"], "10.1000/abc")
        self.assertEqual(doi_record["authors"], ["Ada Li", "Bert Ng"])
        self.assertEqual(doi_record["source_hits"], ["Crossref", "OpenAlex"])
        self.assertEqual(doi_record["relevance_score"], 0.9)
        self.assertEqual(doi_record["eissn"], "1476-4687")
        arxiv_record = deduped[1]
        self.assertEqual(arxiv_record["arxiv_id"], "2401.00001")
        self.assertEqual(arxiv_record["source_hits"], ["Semantic Scholar", "arXiv"])

    def test_decision_letter_doi_variants_collapse_into_one_article_record(self):
        dedupe_candidates = require("scansci_find.dedupe.dedupe_candidates")

        candidates = [
            {
                "title": "Habitat Restorations in an Urban Landscape",
                "authors": ["Ada Li"],
                "year": 2025,
                "doi": "10.1111/ele.70037/v1/decision1",
                "arxiv_id": "",
                "journal": "Ecology Letters",
                "source_hits": ["Crossref"],
                "relevance_score": 0.7,
            },
            {
                "title": "Habitat Restorations in an Urban Landscape",
                "authors": ["Ada Li"],
                "year": 2025,
                "doi": "10.1111/ele.70037/v2/decision1",
                "arxiv_id": "",
                "journal": "Ecology Letters",
                "source_hits": ["Crossref"],
                "relevance_score": 0.8,
            },
            {
                "title": "Habitat Restorations in an Urban Landscape",
                "authors": ["Ada Li"],
                "year": 2025,
                "doi": "10.1111/ele.70037/v4/decision1",
                "arxiv_id": "",
                "journal": "Ecology Letters",
                "source_hits": ["Crossref"],
                "relevance_score": 0.9,
            },
            {
                "title": "A Genuinely Different Study",
                "authors": ["Bert Ng"],
                "year": 2024,
                "doi": "10.1111/ele.70038/v1/decision1",
                "arxiv_id": "",
                "journal": "Ecology Letters",
                "source_hits": ["Crossref"],
                "relevance_score": 0.6,
            },
        ]

        deduped = dedupe_candidates(candidates)

        self.assertEqual(len(deduped), 2)
        article = next(item for item in deduped if item["doi"] == "10.1111/ele.70037")
        self.assertEqual(article["relevance_score"], 0.9)
        self.assertEqual(article["identifiers"]["doi"], "10.1111/ele.70037")
        other = next(item for item in deduped if item["doi"] == "10.1111/ele.70038")
        self.assertEqual(other["title"], "A Genuinely Different Study")

    def test_plain_doi_is_not_altered_by_decision_letter_normalization(self):
        dedupe_candidates = require("scansci_find.dedupe.dedupe_candidates")

        deduped = dedupe_candidates(
            [
                {
                    "title": "A Study",
                    "authors": ["Ada Li"],
                    "year": 2025,
                    "doi": "10.1002/ecy.3631",
                    "arxiv_id": "",
                    "journal": "Ecology",
                    "source_hits": ["Crossref"],
                    "relevance_score": 0.7,
                }
            ]
        )

        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0]["doi"], "10.1002/ecy.3631")


if __name__ == "__main__":
    unittest.main()
