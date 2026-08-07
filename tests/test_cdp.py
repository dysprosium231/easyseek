import io
import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from scansci_find.adapters import ProviderConfigurationError


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


class CdpDiscoveryTests(unittest.TestCase):
    def test_discovers_chrome_from_devtools_active_port_file(self):
        from scansci_find import cdp

        port_file = Path("fake-user-data") / "DevToolsActivePort"
        port_file.parent.mkdir(parents=True, exist_ok=True)
        port_file.write_text("9222\n/devtools/browser/abc-123\n", encoding="utf-8")
        try:
            with patch.object(cdp, "_devtools_active_port_files", return_value=[port_file]), patch.object(
                cdp, "_tcp_open", return_value=True
            ):
                result = cdp.discover_chrome()
        finally:
            port_file.unlink()
            port_file.parent.rmdir()

        self.assertIsNotNone(result)
        self.assertEqual(result["port"], 9222)
        self.assertEqual(result["source"], "DevToolsActivePort")
        self.assertIn("/devtools/browser/abc-123", result["ws_url"])

    def test_falls_back_to_port_scan_when_no_active_port_file(self):
        from scansci_find import cdp

        def fake_tcp_open(host, port):
            return port == 9229

        with patch.object(cdp, "_devtools_active_port_files", return_value=[]), patch.object(
            cdp, "_tcp_open", side_effect=fake_tcp_open
        ), patch("scansci_find.cdp.urllib.request.urlopen", return_value=FakeResponse({"webSocketDebuggerUrl": "ws://127.0.0.1:9229/devtools/browser/x"})):
            result = cdp.discover_chrome()

        self.assertIsNotNone(result)
        self.assertEqual(result["source"], "port_scan")
        self.assertEqual(result["port"], 9229)

    def test_returns_none_when_nothing_is_debuggable(self):
        from scansci_find import cdp

        with patch.object(cdp, "_devtools_active_port_files", return_value=[]), patch.object(
            cdp, "_tcp_open", return_value=False
        ):
            self.assertIsNone(cdp.discover_chrome())

    def test_cdp_session_without_optional_dependency_raises_helpful_error(self):
        from scansci_find.cdp import CdpError, CdpSession

        with patch("scansci_find.cdp.cdp_available", return_value=False):
            with self.assertRaises(CdpError) as ctx:
                CdpSession("ws://127.0.0.1:9222/devtools/browser")
        self.assertIn("scansci-find[cdp]", str(ctx.exception))

    def test_cdp_browser_without_debuggable_chrome_raises_helpful_error(self):
        from scansci_find.cdp import CdpBrowser, CdpError

        with patch("scansci_find.cdp.discover_chrome", return_value=None):
            with self.assertRaises(CdpError) as ctx:
                CdpBrowser()
        self.assertIn("remote debugging", str(ctx.exception))


class BrowserSourceProviderTests(unittest.TestCase):
    def test_google_scholar_provider_degrades_to_configuration_error_without_cdp(self):
        from scansci_find.browser_sources import GoogleScholarCdpProvider

        with patch("scansci_find.cdp.discover_chrome", return_value=None):
            with self.assertRaises(ProviderConfigurationError):
                GoogleScholarCdpProvider().search("transformer", 5)

    def test_cnki_provider_error_mentions_both_cdp_and_mcp_remedies(self):
        from scansci_find.browser_sources import CNKICdpProvider

        with patch("scansci_find.cdp.discover_chrome", return_value=None):
            with self.assertRaises(ProviderConfigurationError) as ctx:
                CNKICdpProvider().search("人工智能", 5)

        message = str(ctx.exception)
        self.assertIn("SCANSCI_FIND_CNKI_MCP_COMMAND", message)
        self.assertIn("remote debugging", message)


if __name__ == "__main__":
    unittest.main()
