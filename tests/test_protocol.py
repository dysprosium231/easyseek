import unittest

from scansci_find.protocol import build_protocol
from scansci_find.source_registry import get_source, route_sources


class ProtocolTests(unittest.TestCase):
    def test_general_profile_is_domain_neutral_and_does_not_default_to_medical_sources(self):
        protocol = build_protocol("urban heat island adaptation", domain="general", depth="standard")

        self.assertEqual(protocol.domain, "general")
        self.assertEqual(protocol.framework, "concept-blocks")
        self.assertEqual(protocol.optional_frameworks, [])
        self.assertNotIn("pubmed", protocol.planned_sources)
        self.assertNotIn("europe-pmc", protocol.planned_sources)
        self.assertNotIn("PICO", protocol.framework)

    def test_medicine_is_an_optional_domain_pack_not_the_core_identity(self):
        protocol = build_protocol("intervention outcomes", domain="medicine", depth="standard")

        self.assertIn("pubmed", protocol.planned_sources)
        self.assertIn("europe-pmc", protocol.planned_sources)
        self.assertIn("PICO", protocol.optional_frameworks)
        self.assertEqual(protocol.framework, "concept-blocks")

    def test_systematic_plan_names_conditional_sources_instead_of_claiming_they_ran(self):
        routed = route_sources("general", "systematic")

        self.assertIn("web-of-science", routed["conditional"])
        self.assertIn("hal", routed["conditional"])
        self.assertIn("dimensions", routed["conditional"])
        self.assertIn("openalex", routed["executable"])
        # Google Scholar now ships a CDP implementation; it is executable at
        # runtime only when a debuggable Chrome is available.
        self.assertIn("google-scholar", routed["executable"])
        self.assertEqual(get_source("google-scholar").implementation, "cdp")

    def test_concept_blocks_compile_boolean_and_plain_query_variants(self):
        protocol = build_protocol(
            "urban heat health",
            concept_blocks=[
                {"name": "exposure", "terms": ["urban heat", "heat island"]},
                {"name": "outcome", "terms": ["mortality", "health"]},
            ],
        )

        self.assertIn("AND", protocol.boolean_query)
        self.assertIn("urban heat mortality", protocol.query_variants)
        self.assertEqual(protocol.query_variants[0], "urban heat health")

    def test_source_catalog_distinguishes_capabilities_access_and_implementation(self):
        pubmed = get_source("pubmed")
        wos = get_source("wos")

        self.assertTrue(pubmed.executable)
        self.assertIn("search", pubmed.capabilities)
        self.assertFalse(wos.executable)

        opencitations = get_source("opencitations")
        unpaywall = get_source("unpaywall")
        self.assertEqual(opencitations.implementation, "native")
        self.assertFalse(opencitations.executable)
        self.assertTrue(opencitations.support_executable)
        self.assertFalse(unpaywall.executable)
        self.assertTrue(unpaywall.support_executable)
        self.assertEqual(wos.access, "institution")

    def test_domain_catalog_covers_non_medical_discipline_adapters_and_separates_support_routes(self):
        protocol = build_protocol("spectral geometry", domain="mathematics", depth="standard")

        self.assertIn("zbmath-open", protocol.planned_sources)
        self.assertIn("mathscinet", protocol.conditional_sources)
        self.assertIn("opencitations", protocol.support_sources["citation_expansion"])
        self.assertNotIn("opencitations", protocol.planned_sources)

    def test_invalid_year_range_is_rejected_before_search(self):
        with self.assertRaises(ValueError):
            build_protocol("topic", year_from=2026, year_to=2020)

    def test_protocol_id_changes_when_a_material_search_decision_changes(self):
        first = build_protocol("topic", inclusion_criteria=["peer reviewed"])
        second = build_protocol("topic", inclusion_criteria=["all records"])
        same_as_first = build_protocol("topic", inclusion_criteria=["peer reviewed"])

        self.assertNotEqual(first.protocol_id, second.protocol_id)
        self.assertEqual(first.protocol_id, same_as_first.protocol_id)


if __name__ == "__main__":
    unittest.main()
