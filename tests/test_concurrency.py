import os
import threading
import unittest
from unittest.mock import patch

from scansci_find.adapters import search_sources_with_status
from scansci_find.verification import verify_identifiers


class BlockingProvider:
    """Provider whose search blocks until every sibling provider is in flight.

    If the source loop ran serially, the barrier would time out and raise
    BrokenBarrierError; passing it proves parallel execution.
    """

    name = "block"

    def __init__(self, barrier):
        self.barrier = barrier
        self.last_search_metadata = {}

    def search(self, query, limit):
        self.barrier.wait(timeout=3)
        return [{"title": "x", "doi": "", "source": self.name}]


class ConcurrencyTests(unittest.TestCase):
    def test_search_sources_runs_sources_in_parallel_and_preserves_order(self):
        barrier = threading.Barrier(3)
        providers = {"a": BlockingProvider(barrier), "b": BlockingProvider(barrier), "c": BlockingProvider(barrier)}

        with patch.dict(os.environ, {"SCANSCI_FIND_SEARCH_WORKERS": "3"}):
            result = search_sources_with_status("q", ["a", "b", "c"], 10, providers=providers)

        self.assertEqual([status["name"] for status in result["source_status"]], ["a", "b", "c"])
        self.assertEqual([status["status"] for status in result["source_status"]], ["ok", "ok", "ok"])
        self.assertEqual(len(result["candidates"]), 3)

    def test_worker_override_of_one_forces_serial_order(self):
        calls = []

        class RecordingProvider:
            name = "rec"

            def __init__(self, label):
                self.label = label
                self.last_search_metadata = {}

            def search(self, query, limit):
                calls.append(self.label)
                return []

        providers = {"a": RecordingProvider("a"), "b": RecordingProvider("b"), "c": RecordingProvider("c")}

        with patch.dict(os.environ, {"SCANSCI_FIND_SEARCH_WORKERS": "1"}):
            search_sources_with_status("q", ["a", "b", "c"], 10, providers=providers)

        self.assertEqual(calls, ["a", "b", "c"])

    def test_verify_identifiers_runs_candidates_in_parallel(self):
        barrier = threading.Barrier(3)

        class BlockingVerifier:
            def verify(self, candidate):
                barrier.wait(timeout=3)
                return {
                    "status": "verified",
                    "identifier_type": "doi",
                    "identifier": candidate["doi"],
                    "source": "Crossref",
                    "checks": [],
                }

        with patch.dict(os.environ, {"SCANSCI_FIND_SEARCH_WORKERS": "3"}):
            result = verify_identifiers(
                [{"doi": "10.1000/a"}, {"doi": "10.1000/b"}, {"doi": "10.1000/c"}],
                verifier=BlockingVerifier(),
            )

        self.assertEqual(result["status_counts"], {"verified": 3})
        self.assertTrue(result["all_verified"])
        self.assertEqual(
            [row["identifier_verification"]["identifier"] for row in result["candidates"]],
            ["10.1000/a", "10.1000/b", "10.1000/c"],
        )


if __name__ == "__main__":
    unittest.main()
