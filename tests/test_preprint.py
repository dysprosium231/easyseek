import unittest

from scansci_find.outputs import download_entry
from scansci_find.preprint import PreprintFinder, find_preprints


class FakeProvider:
    def __init__(self, rows=None, error=None):
        self.rows = rows or []
        self.error = error
        self.queries = []

    def search(self, query, limit):
        self.queries.append(query)
        if self.error:
            raise self.error
        return self.rows[:limit]


def _arxiv_row(title="Heat island mapping with remote sensing", arxiv_id="2401.12345", year=2024):
    return {
        "title": title,
        "authors": ["Ada Li"],
        "year": year,
        "arxiv_id": arxiv_id,
        "doi": "",
        "journal": "arXiv",
        "links": {"paper": f"https://arxiv.org/abs/{arxiv_id}", "pdf": f"https://arxiv.org/pdf/{arxiv_id}"},
    }


def _epmc_row(title="Heat island mapping with remote sensing", pmcid="PMC1234567", year=2024):
    return {
        "title": title,
        "authors": ["Ada Li"],
        "year": year,
        "arxiv_id": "",
        "doi": "10.1101/2024.01.01.123456",
        "pmcid": pmcid,
        "journal": "bioRxiv",
        "links": {"fulltext": f"https://europepmc.org/articles/{pmcid}", "paper": f"https://europepmc.org/article/PPR/123456"},
    }


def _paywalled_candidate():
    return {
        "title": "Heat island mapping with remote sensing",
        "authors": ["Ada Li", "Bo Chen"],
        "year": 2024,
        "doi": "10.1000/heat",
        "journal": "Paywalled Journal",
        "source_hits": ["Crossref"],
        "links": {"paper": "https://doi.org/10.1000/heat"},
        "access": {"fulltext_hint": "unknown", "requires_login": False, "requires_institution": True},
    }


class PreprintMatchTests(unittest.TestCase):
    def test_arxiv_match_enriches_candidate_and_sets_preprint_hint(self):
        finder = PreprintFinder(arxiv=FakeProvider(rows=[_arxiv_row()]), europe_pmc=FakeProvider())
        candidate = _paywalled_candidate()

        result = find_preprints([candidate], finder=finder)

        self.assertEqual(result["matched"], 1)
        self.assertEqual(result["status_counts"], {"matched": 1})
        row = result["candidates"][0]
        self.assertEqual(row["links"]["preprint"], "https://arxiv.org/abs/2401.12345")
        self.assertEqual(row["links"]["pdf"], "https://arxiv.org/pdf/2401.12345")
        self.assertEqual(row["access"]["fulltext_hint"], "preprint")
        self.assertEqual(row["preprint_versions"][0]["arxiv_id"], "2401.12345")

    def test_europe_pmc_ppr_query_covers_preprint_servers(self):
        provider = FakeProvider(rows=[_epmc_row()])
        finder = PreprintFinder(arxiv=FakeProvider(), europe_pmc=provider)

        result = find_preprints([_paywalled_candidate()], finder=finder)

        self.assertEqual(result["matched"], 1)
        self.assertIn('SRC:"PPR"', provider.queries[0])
        self.assertIn('TITLE:"Heat island mapping with remote sensing"', provider.queries[0])
        self.assertEqual(result["candidates"][0]["preprint_versions"][0]["server"], "bioRxiv")

    def test_arxiv_query_is_title_scoped(self):
        provider = FakeProvider(rows=[_arxiv_row()])
        finder = PreprintFinder(arxiv=provider, europe_pmc=FakeProvider())

        find_preprints([_paywalled_candidate()], finder=finder)

        self.assertTrue(provider.queries[0].startswith('ti:"Heat island mapping with remote sensing"'))

    def test_low_title_similarity_is_not_matched(self):
        finder = PreprintFinder(
            arxiv=FakeProvider(rows=[_arxiv_row(title="A completely different paper about glaciers")]),
            europe_pmc=FakeProvider(),
        )

        result = find_preprints([_paywalled_candidate()], finder=finder)

        self.assertEqual(result["status_counts"], {"not_found": 1})
        self.assertEqual(result["matched"], 0)

    def test_matching_author_but_wrong_year_still_matches(self):
        finder = PreprintFinder(arxiv=FakeProvider(rows=[_arxiv_row(year=2019)]), europe_pmc=FakeProvider())

        result = find_preprints([_paywalled_candidate()], finder=finder)

        self.assertEqual(result["status_counts"], {"matched": 1})

    def test_same_year_but_different_author_still_matches(self):
        candidate = _paywalled_candidate()
        candidate["authors"] = ["Zoe Wu"]
        finder = PreprintFinder(arxiv=FakeProvider(rows=[_arxiv_row()]), europe_pmc=FakeProvider())

        result = find_preprints([candidate], finder=finder)

        self.assertEqual(result["status_counts"], {"matched": 1})

    def test_different_author_and_distant_year_is_not_matched(self):
        candidate = _paywalled_candidate()
        candidate["authors"] = ["Zoe Wu"]
        candidate["year"] = 2024
        finder = PreprintFinder(arxiv=FakeProvider(rows=[_arxiv_row(year=2019)]), europe_pmc=FakeProvider())

        result = find_preprints([candidate], finder=finder)

        self.assertEqual(result["status_counts"], {"not_found": 1})

    def test_already_oa_or_arxiv_candidates_are_skipped(self):
        oa_candidate = _paywalled_candidate()
        oa_candidate["access"] = {"fulltext_hint": "oa", "requires_login": False, "requires_institution": False}
        arxiv_candidate = _paywalled_candidate()
        arxiv_candidate["arxiv_id"] = "2301.99999"
        finder = PreprintFinder(arxiv=FakeProvider(rows=[_arxiv_row()]), europe_pmc=FakeProvider())

        result = find_preprints([oa_candidate, arxiv_candidate], finder=finder)

        self.assertEqual(result["status_counts"], {"skipped": 2})
        self.assertEqual(result["matched"], 0)

    def test_provider_failures_are_reported_not_hidden(self):
        finder = PreprintFinder(arxiv=FakeProvider(error=RuntimeError("boom")), europe_pmc=FakeProvider(error=RuntimeError("down")))

        result = find_preprints([_paywalled_candidate()], finder=finder)

        self.assertEqual(result["status_counts"], {"error": 1})
        self.assertEqual(result["provider_status"], {"arxiv": {"searched": 0, "errored": 1}, "europe-pmc": {"searched": 0, "errored": 1}})

    def test_candidate_without_title_is_unsupported(self):
        finder = PreprintFinder(arxiv=FakeProvider(rows=[_arxiv_row()]), europe_pmc=FakeProvider())

        result = find_preprints([{"doi": "10.1000/x"}], finder=finder)

        self.assertEqual(result["status_counts"], {"unsupported": 1})

    def test_download_entry_carries_preprint_identifiers(self):
        candidate = {
            "title": "Heat island mapping",
            "doi": "10.1000/heat",
            "preprint_versions": [
                {"arxiv_id": "2401.12345", "url": "https://arxiv.org/abs/2401.12345"},
                {"arxiv_id": "2401.12345", "url": "https://arxiv.org/abs/2401.12345v2"},
                {"arxiv_id": "2401.67890", "url": ""},
            ],
        }

        entry = download_entry(candidate)

        self.assertEqual(
            entry["preprint_identifiers"],
            [
                {"type": "arxiv", "value": "2401.12345", "url": "https://arxiv.org/abs/2401.12345"},
                {"type": "arxiv", "value": "2401.67890", "url": ""},
            ],
        )


if __name__ == "__main__":
    unittest.main()
