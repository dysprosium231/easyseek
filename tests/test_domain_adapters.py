import unittest

from scansci_find.adapters import normalize_dblp_record, normalize_europe_pmc_record, normalize_pubmed_record


class DomainAdapterTests(unittest.TestCase):
    def test_pubmed_normalization_preserves_medical_identifiers_without_changing_core_shape(self):
        candidate = normalize_pubmed_record(
            {
                "uid": "123",
                "title": "A clinical paper",
                "pubdate": "2025 Jan",
                "authors": [{"name": "Li A"}],
                "fulljournalname": "Example Medicine",
                "articleids": [{"idtype": "doi", "value": "10.1000/med"}, {"idtype": "pmc", "value": "PMC123"}],
            }
        )

        self.assertEqual(candidate["pmid"], "123")
        self.assertEqual(candidate["pmcid"], "PMC123")
        self.assertEqual(candidate["doi"], "10.1000/med")
        self.assertEqual(candidate["identifiers"]["pmid"], "123")
        self.assertIn("PubMed", candidate["source_hits"])

    def test_europe_pmc_and_dblp_are_domain_adapters_on_the_same_candidate_contract(self):
        europe = normalize_europe_pmc_record(
            {"pmid": "321", "pmcid": "PMC321", "title": "Biology paper", "pubYear": "2024", "journalTitle": "Biology", "isOpenAccess": "Y"}
        )
        dblp = normalize_dblp_record(
            {"info": {"key": "conf/test/Li25", "title": "Systems paper", "year": "2025", "venue": "TestConf", "authors": {"author": [{"text": "Ada Li"}]}}}
        )

        self.assertEqual(europe["access"]["fulltext_hint"], "oa")
        self.assertEqual(dblp["dblp_id"], "conf/test/Li25")
        for candidate in (europe, dblp):
            self.assertIn("identifiers", candidate)
            self.assertIn("source_records", candidate)
            self.assertIn("artifact_type", candidate)


if __name__ == "__main__":
    unittest.main()
