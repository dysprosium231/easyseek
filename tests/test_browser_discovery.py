import importlib
import json
import tempfile
import unittest
from pathlib import Path


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


class BrowserDiscoveryTests(unittest.TestCase):
    def resolver(self, **kwargs):
        BrowserRuntimeResolver = require("scansci_find.browser_discovery.BrowserRuntimeResolver")
        return BrowserRuntimeResolver(**kwargs)

    def test_explicit_shared_browser_command_wins_and_never_requires_install(self):
        resolver = self.resolver(
            env={"SCANSCI_BROWSER_COMMAND": "scansci-browser serve --port 8765"},
            path_lookup=lambda name: None,
            import_exists=lambda name: False,
            path_exists=lambda path: False,
        )

        result = resolver.doctor()

        self.assertEqual(result["selected"], "configured_command")
        self.assertEqual(result["source"], "SCANSCI_BROWSER_COMMAND")
        self.assertEqual(result["command"], ["scansci-browser", "serve", "--port", "8765"])
        self.assertFalse(result["install_needed"])

    def test_path_scansci_browser_is_selected_before_package_and_system_browser(self):
        resolver = self.resolver(
            env={},
            path_lookup=lambda name: f"C:/Tools/{name}.exe" if name == "scansci-browser" else None,
            import_exists=lambda name: name in {"scansci_browser", "cloakbrowser"},
            path_exists=lambda path: str(path).endswith("chrome.exe"),
            default_system_browser_paths=["C:/Program Files/Google/Chrome/Application/chrome.exe"],
        )

        result = resolver.doctor()

        self.assertEqual(result["selected"], "scansci_browser_command")
        self.assertEqual(result["path"], "C:/Tools/scansci-browser.exe")
        self.assertFalse(result["install_needed"])

    def test_existing_scansci_pdf_browser_module_is_reusable_without_installing_browser(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = root / "src" / "scansci_pdf" / "browser_engine.py"
            module.parent.mkdir(parents=True)
            module.write_text("# existing browser engine", encoding="utf-8")
            resolver = self.resolver(
                env={"SCANSCI_PDF_REPO": str(root)},
                path_lookup=lambda name: None,
                import_exists=lambda name: False,
                path_exists=lambda path: Path(path).exists(),
                default_system_browser_paths=[],
                scansci_pdf_roots=[str(root)],
            )

            result = resolver.doctor()

        self.assertEqual(result["selected"], "scansci_pdf_browser")
        self.assertEqual(result["source"], "existing_scansci_pdf")
        self.assertFalse(result["install_needed"])

    def test_system_chrome_is_a_valid_fallback_before_install_hint(self):
        resolver = self.resolver(
            env={},
            path_lookup=lambda name: None,
            import_exists=lambda name: False,
            path_exists=lambda path: str(path).endswith("chrome.exe"),
            default_system_browser_paths=["C:/Program Files/Google/Chrome/Application/chrome.exe"],
        )

        result = resolver.doctor()

        self.assertEqual(result["selected"], "system_browser")
        self.assertEqual(result["browser_binary"], "C:/Program Files/Google/Chrome/Application/chrome.exe")
        self.assertFalse(result["install_needed"])

    def test_no_browser_runtime_reports_install_hint_without_installing(self):
        resolver = self.resolver(
            env={},
            path_lookup=lambda name: None,
            import_exists=lambda name: False,
            path_exists=lambda path: False,
            default_system_browser_paths=[],
            scansci_pdf_roots=[],
        )

        result = resolver.doctor()

        self.assertEqual(result["selected"], "")
        self.assertTrue(result["install_needed"])
        self.assertIn("pip install cloakbrowser", result["install_hint"])

    def test_empty_probe_lists_disable_default_scansci_pdf_and_system_browser_scans(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            module = root / "src" / "scansci_pdf" / "browser_engine.py"
            module.parent.mkdir(parents=True)
            module.write_text("# existing browser engine", encoding="utf-8")
            resolver = self.resolver(
                env={"SCANSCI_PDF_REPO": str(root)},
                path_lookup=lambda name: None,
                import_exists=lambda name: False,
                path_exists=lambda path: Path(path).exists() or str(path).endswith("chrome.exe"),
                default_system_browser_paths=[],
                scansci_pdf_roots=[],
            )

            result = resolver.doctor()

        self.assertEqual(result["selected"], "")
        self.assertTrue(result["install_needed"])

    def test_doctor_result_is_json_serializable_and_uses_shared_data_dirs(self):
        resolver = self.resolver(
            env={"SCANSCI_BROWSER_COMMAND": "scansci-browser serve"},
            path_lookup=lambda name: None,
            import_exists=lambda name: False,
            path_exists=lambda path: False,
        )

        result = resolver.doctor()

        json.dumps(result)
        self.assertEqual(result["profile_dir"], "D:/Dev/browser-profiles/scansci")
        self.assertEqual(result["cache_dir"], "D:/Dev/cache/browser")


if __name__ == "__main__":
    unittest.main()
