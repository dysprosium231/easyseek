from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


# Journal Scout accepts journal-quality filters only. Retrieval filters such as
# ``year``, ``doc_type``, and ``field`` are applied locally by the service and
# must never be forwarded to the gateway.
JOURNAL_SCOUT_FILTER_KEYS = {
    "cas_2025",
    "jcr_quartile",
    "hq_levels",
    "hq_catalog",
    "hq_field_keywords",
    "exclude_warning",
    "min_if",
    "is_top",
    "xuankan_2026",
    "pku_core",
    "cssci_type",
    "cscd_type",
    "ei_indexed",
    "xuankan_warning",
}


def _scout_filters(filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not filters:
        return None
    supported = {key: value for key, value in filters.items() if key in JOURNAL_SCOUT_FILTER_KEYS}
    return supported or None


class JournalScoutMcpGateway:
    version = ""
    data_sha256 = ""

    def __init__(
        self,
        command: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        data_path: Optional[str] = None,
    ) -> None:
        self.cwd = cwd or os.environ.get("JOURNAL_SCOUT_REPO") or r"D:\scansci\journal-scout"
        self.data_path = data_path or os.environ.get("JOURNAL_SCOUT_DATA_PATH") or str(Path(self.cwd) / "data" / "journals.json")
        self.command = command or [sys.executable, "-m", "journal_scout_mcp", "--data-path", self.data_path]

    def health_check(self) -> Dict[str, Any]:
        payload = self.call_tool("health_check", {})
        self.version = payload.get("server_version") or payload.get("version") or self.version
        data = payload.get("data") or {}
        self.data_sha256 = data.get("sha256") or self.data_sha256
        return payload

    def screen_papers(self, papers: List[Dict[str, Any]], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        args: Dict[str, Any] = {"papers": papers}
        if policy:
            args["policy"] = policy
        scout_filters = _scout_filters(filters)
        if scout_filters:
            args["filters"] = scout_filters
        return self.call_tool("screen_papers", args)

    def explain_journal(self, candidate: Dict[str, Any], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        args: Dict[str, Any] = {
            "query": candidate.get("journal") or candidate.get("title") or "",
            "issn": candidate.get("issn") or candidate.get("eissn") or "",
        }
        if policy:
            args["policy"] = policy
        scout_filters = _scout_filters(filters)
        if scout_filters:
            args["filters"] = scout_filters
        return self.call_tool("explain_journal", args)

    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        env = os.environ.copy()
        env.setdefault("PYTHONIOENCODING", "utf-8")
        process = subprocess.Popen(
            self.command,
            cwd=self.cwd if Path(self.cwd).exists() else None,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            env=env,
        )
        try:
            initialize = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-06-18",
                    "capabilities": {},
                    "clientInfo": {"name": "scansci-find", "version": "0.4.0"},
                },
            }
            tool_call = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
            assert process.stdin is not None
            process.stdin.write(json.dumps(initialize, ensure_ascii=False) + "\n")
            process.stdin.write(json.dumps(tool_call, ensure_ascii=False) + "\n")
            process.stdin.flush()
            result = self._read_response(process, wanted_id=2)
            if "error" in result:
                raise RuntimeError(result["error"].get("message") or "Journal Scout MCP error")
            payload = result.get("result") or {}
            if payload.get("isError"):
                structured = payload.get("structuredContent") or {}
                raise RuntimeError(structured.get("message") or "Journal Scout MCP tool error")
            return payload.get("structuredContent") or {}
        finally:
            try:
                process.terminate()
                process.wait(timeout=2)
            except Exception:
                process.kill()

    def _read_response(self, process: subprocess.Popen, wanted_id: int) -> Dict[str, Any]:
        assert process.stdout is not None
        while True:
            line = process.stdout.readline()
            if not line:
                stderr = process.stderr.read() if process.stderr else ""
                raise RuntimeError(f"Journal Scout MCP exited before response: {stderr.strip()}")
            payload = json.loads(line)
            if payload.get("id") == wanted_id:
                return payload


class FixtureJournalScoutGateway:
    def __init__(self, fixture: Dict[str, Any]) -> None:
        section = fixture.get("journal_scout") or {}
        self.version = section.get("version") or "fixture"
        self.data_sha256 = section.get("data_sha256") or ""
        self._results = list(section.get("results") or [])

    def health_check(self) -> Dict[str, Any]:
        return {"server_version": self.version, "data": {"sha256": self.data_sha256, "journal_count": len(self._results)}}

    def screen_papers(self, papers: List[Dict[str, Any]], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        rows = []
        for index, paper in enumerate(papers):
            row = dict(self._results[index]) if index < len(self._results) else {}
            row.setdefault("paper", paper)
            rows.append(row)
        return {"policy": policy, "data": {"sha256": self.data_sha256}, "results": rows, "total": len(rows)}

    def explain_journal(self, candidate: Dict[str, Any], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._results[0] if self._results else {}


UNSCREENED_REASON = "Journal Scout not installed: journal-level screening skipped"


class UnavailableJournalScoutGateway:
    """Stand-in when Journal Scout (a private component) is not installed.

    Every paper passes unscreened, so "hard" quality mode cannot drop all
    results and the uniform "boost" leaves the ranking unchanged. The quality
    block says explicitly that no journal evidence was applied.
    """

    version = ""
    data_sha256 = ""

    def __init__(self, reason: str = UNSCREENED_REASON) -> None:
        self.reason = reason

    def health_check(self) -> Dict[str, Any]:
        return {"available": False, "server_version": "", "message": self.reason}

    def screen_papers(self, papers: List[Dict[str, Any]], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        row = {"passed": True, "policy_result": {"policy": "unscreened", "pass": True, "reasons": [self.reason]}}
        return {"papers": [dict(row) for _ in papers]}

    def explain_journal(self, candidate: Dict[str, Any], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"available": False, "message": self.reason}


class ResilientJournalScoutGateway:
    """Use Journal Scout, but fall back to unscreened results if a call fails."""

    def __init__(self, primary: Any) -> None:
        self.primary = primary
        self.fallback: Optional[UnavailableJournalScoutGateway] = None

    @property
    def version(self) -> str:
        return getattr(self.primary, "version", "")

    @property
    def data_sha256(self) -> str:
        return getattr(self.primary, "data_sha256", "")

    def _call(self, name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        if self.fallback is None:
            try:
                return getattr(self.primary, name)(*args, **kwargs)
            except Exception as exc:  # broken install, missing data, crashed server
                print(f"scansci-find: Journal Scout unavailable ({exc}); results are unscreened", file=sys.stderr)
                self.fallback = UnavailableJournalScoutGateway(f"{UNSCREENED_REASON} ({exc})")
        return getattr(self.fallback, name)(*args, **kwargs)

    def health_check(self) -> Dict[str, Any]:
        return self._call("health_check")

    def screen_papers(self, papers: List[Dict[str, Any]], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._call("screen_papers", papers, policy=policy, filters=filters)

    def explain_journal(self, candidate: Dict[str, Any], policy: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._call("explain_journal", candidate, policy=policy, filters=filters)


def default_journal_gateway() -> Any:
    """Journal Scout when installed, otherwise an explicit unscreened stand-in.

    Journal Scout is a private component (its journal data is licensed), so a
    public install usually lacks it. SCANSCI_FIND_JOURNAL_SCOUT=off forces the
    stand-in even when it is installed.
    """
    import importlib.util

    if os.environ.get("SCANSCI_FIND_JOURNAL_SCOUT", "").strip().lower() in {"0", "off", "false", "no"}:
        return UnavailableJournalScoutGateway("Journal Scout disabled (SCANSCI_FIND_JOURNAL_SCOUT=off)")
    primary = JournalScoutMcpGateway()
    installed = importlib.util.find_spec("journal_scout_mcp") is not None or Path(primary.cwd).exists()
    if not installed:
        return UnavailableJournalScoutGateway()
    return ResilientJournalScoutGateway(primary)
