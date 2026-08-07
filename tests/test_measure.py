import unittest

from scansci_find.measure import abstract_coverage, estimate_population


def _candidate(title, sources, abstract=""):
    return {
        "title": title,
        "doi": "",
        "arxiv_id": "",
        "source_hits": list(sources),
        "abstract": abstract,
        "links": {},
    }


class ChapmanTests(unittest.TestCase):
    def test_estimator_uses_chapman_formula_with_known_numbers(self):
        # n_a = 10 (PubMed), n_b = 12 (OpenAlex), m = 3 (both)
        candidates = (
            [_candidate(f"a{i}", ["PubMed"]) for i in range(7)]
            + [_candidate(f"b{i}", ["OpenAlex"]) for i in range(9)]
            + [_candidate(f"c{i}", ["PubMed", "OpenAlex"]) for i in range(3)]
        )

        result = estimate_population(candidates)

        self.assertIsNotNone(result)
        # N = (10+1)(12+1)/(3+1) - 1 = 34.75
        self.assertEqual(result["estimated_total"], 34.75)
        self.assertEqual(result["seen_a"], 10)
        self.assertEqual(result["seen_b"], 12)
        self.assertEqual(result["seen_both"], 3)
        self.assertIn("two-source overlap diagnostic", result["note"])

    def test_returns_none_without_overlap(self):
        candidates = [_candidate("a", ["PubMed"]), _candidate("b", ["OpenAlex"])]
        self.assertIsNone(estimate_population(candidates))

    def test_returns_none_when_one_source_missing(self):
        candidates = [_candidate("a", ["PubMed"]), _candidate("b", ["PubMed"])]
        self.assertIsNone(estimate_population(candidates))


class AbstractCoverageTests(unittest.TestCase):
    def test_coverage_counts_abstracts_per_source(self):
        candidates = [
            _candidate("a", ["PubMed"], abstract="full abstract"),
            _candidate("b", ["PubMed"], abstract=""),
            _candidate("c", ["OpenAlex"], abstract="full abstract"),
        ]

        result = abstract_coverage(candidates)

        by_source = {item["source"]: item for item in result["per_source"]}
        self.assertEqual(by_source["PubMed"]["coverage"], 0.5)
        self.assertEqual(by_source["OpenAlex"]["coverage"], 1.0)
        self.assertEqual(result["overall"], round(2 / 3, 4))


if __name__ == "__main__":
    unittest.main()
