import unittest

from scansci_find.protocol import build_protocol
from scansci_find.vocab import expand_terms, load_user_vocab


class VocabExpansionTests(unittest.TestCase):
    def test_abbreviation_expands_to_full_form(self):
        self.assertEqual(expand_terms(["LLM"]), ["LLM", "large language model"])

    def test_full_form_expands_back_to_abbreviation(self):
        expanded = expand_terms(["large language model"])
        self.assertIn("llm", expanded)
        self.assertEqual(expanded[0], "large language model")

    def test_domain_synonym_applies_only_in_that_domain(self):
        self.assertIn("cerebrovascular accident", expand_terms(["stroke"], domain="medicine"))
        self.assertEqual(expand_terms(["stroke"], domain="general"), ["stroke"])

    def test_user_terms_are_never_renamed_or_dropped(self):
        expanded = expand_terms(["mri", "custom term"], domain="medicine")
        self.assertEqual(expanded[0], "mri")
        self.assertIn("custom term", expanded)
        self.assertIn("magnetic resonance imaging", expanded)

    def test_expansion_is_deterministic_and_deduplicated(self):
        self.assertEqual(expand_terms(["ai", "AI"]), ["ai", "artificial intelligence"])

    def test_extra_vocab_merges_last(self):
        expanded = expand_terms(["foo"], extra_vocab={"foo": ["bar", "baz"]})
        self.assertEqual(expanded, ["foo", "bar", "baz"])

    def test_user_vocab_directory_empty_when_unconfigured(self):
        self.assertEqual(load_user_vocab(""), {})


class ProtocolQueryExpansionTests(unittest.TestCase):
    def test_protocol_variants_include_expanded_terms_for_known_abbreviations(self):
        protocol = build_protocol(
            "mri stroke",
            domain="medicine",
            concept_blocks=[
                {"name": "modality", "terms": ["mri"]},
                {"name": "condition", "terms": ["stroke"]},
            ],
        )

        self.assertIn("magnetic resonance imaging", protocol.boolean_query)
        self.assertIn("cerebrovascular accident", protocol.boolean_query)

    def test_expansion_is_a_pure_function_of_terms_so_protocol_id_stays_stable(self):
        first = build_protocol("mri stroke", domain="medicine")
        second = build_protocol("mri stroke", domain="medicine")
        self.assertEqual(first.protocol_id, second.protocol_id)
        self.assertEqual(first.boolean_query, second.boolean_query)


if __name__ == "__main__":
    unittest.main()
