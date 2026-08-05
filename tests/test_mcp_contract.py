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


class McpContractTests(unittest.TestCase):
    def test_tool_list_exposes_planned_capability_surface(self):
        list_tools = require("scansci_find.mcp_contract.list_tools")

        tools = list_tools()

        names = [tool["name"] for tool in tools]
        self.assertEqual(
            names,
            [
                "health_check",
                "list_sources",
                "plan_search",
                "estimate_search",
                "smoke_search",
                "calibrate_search",
                "search_academic",
                "search_science",
                "verify_identifiers",
                "resolve_open_access",
                "screen_candidates",
                "explain_candidate",
                "build_download_queue",
                "expand_citations",
                "browser_doctor",
            ],
        )
        for tool in tools:
            self.assertIn("inputSchema", tool)
            self.assertIn("outputSchema", tool)

    def test_browser_doctor_tool_returns_service_browser_discovery_payload(self):
        handle_tool_call = require("scansci_find.mcp_contract.handle_tool_call")

        class FakeService:
            def browser_doctor(self):
                return {"selected": "system_browser", "install_needed": False}

        response = handle_tool_call("browser_doctor", {}, FakeService())

        self.assertFalse(response["isError"])
        self.assertEqual(response["structuredContent"]["selected"], "system_browser")
        self.assertFalse(response["structuredContent"]["install_needed"])

    def test_tool_errors_are_structured_for_unavailable_journal_scout(self):
        handle_tool_call = require("scansci_find.mcp_contract.handle_tool_call")

        class BrokenService:
            def health_check(self):
                raise RuntimeError("journal scout unavailable")

        response = handle_tool_call("health_check", {}, BrokenService())

        self.assertTrue(response["isError"])
        self.assertEqual(response["structuredContent"]["error_code"], "TOOL_ERROR")
        self.assertEqual(response["structuredContent"]["tool"], "health_check")
        self.assertIn("journal scout unavailable", response["structuredContent"]["message"])

    def test_json_rpc_serialization_is_safe_for_windows_gbk_stdout(self):
        serialize_response = require("scansci_find.mcp_server.serialize_response")

        line = serialize_response(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "structuredContent": {
                        "title": "Expectation vs.\u00a0Experience",
                        "journal": "生态学报",
                    }
                },
            }
        )

        line.encode("gbk")
        self.assertIn("\\u00a0", line)


if __name__ == "__main__":
    unittest.main()
