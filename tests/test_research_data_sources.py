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


class ResearchDataSourceTests(unittest.TestCase):
    def test_research_data_normalizers_share_candidate_shape_and_artifact_type(self):
        normalize_zenodo = require("scansci_find.adapters.normalize_zenodo_record")
        normalize_datacite = require("scansci_find.adapters.normalize_datacite_work")
        normalize_openml = require("scansci_find.adapters.normalize_openml_dataset")
        normalize_hf = require("scansci_find.adapters.normalize_huggingface_dataset")
        normalize_kaggle = require("scansci_find.adapters.normalize_kaggle_dataset")

        candidates = [
            normalize_zenodo(
                {
                    "metadata": {
                        "title": "Pollinator image dataset",
                        "publication_date": "2025-01-02",
                        "doi": "10.5281/zenodo.1",
                        "creators": [{"name": "Li, Ada"}],
                        "resource_type": {"type": "dataset"},
                    },
                    "links": {"html": "https://zenodo.org/records/1"},
                    "files": [{"links": {"self": "https://zenodo.org/api/files/data.csv"}}],
                }
            ),
            normalize_datacite(
                {
                    "id": "10.1234/data",
                    "attributes": {
                        "titles": [{"title": "Soil carbon data"}],
                        "publicationYear": 2024,
                        "creators": [{"name": "Ng, Bert"}],
                        "types": {"resourceTypeGeneral": "Dataset"},
                        "url": "https://example.test/data",
                    },
                }
            ),
            normalize_openml(
                {
                    "did": 61,
                    "name": "iris",
                    "version": 1,
                    "NumberOfInstances": 150,
                    "NumberOfFeatures": 4,
                }
            ),
            normalize_hf(
                {
                    "id": "org/pollinator-dataset",
                    "downloads": 42,
                    "likes": 7,
                    "tags": ["task_categories:image-classification", "license:cc-by-4.0"],
                }
            ),
            normalize_kaggle(
                {
                    "ref": "ada/pollinator-dataset",
                    "title": "Pollinator dataset",
                    "downloadCount": 100,
                    "voteCount": 5,
                    "licenseName": "CC0-1.0",
                }
            ),
        ]

        for candidate in candidates:
            with self.subTest(source=candidate["source_hits"]):
                self.assertIn(candidate["artifact_type"], {"dataset", "benchmark", "record"})
                self.assertIn("title", candidate)
                self.assertIn("doi", candidate)
                self.assertIn("links", candidate)
                self.assertIn("download", candidate)


if __name__ == "__main__":
    unittest.main()
