"""Search must work without the private Journal Scout component."""

import importlib.util

import pytest

from scansci_find import journal_scout as js
from scansci_find.quality import apply_quality


def _papers():
    return [{"title": "A", "relevance_score": 0.5}, {"title": "B", "relevance_score": 0.9}]


def test_default_gateway_without_journal_scout(monkeypatch, tmp_path):
    monkeypatch.setenv("JOURNAL_SCOUT_REPO", str(tmp_path / "missing"))
    monkeypatch.delenv("SCANSCI_FIND_JOURNAL_SCOUT", raising=False)
    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a: None)
    assert isinstance(js.default_journal_gateway(), js.UnavailableJournalScoutGateway)


def test_env_switch_disables_journal_scout(monkeypatch):
    monkeypatch.setenv("SCANSCI_FIND_JOURNAL_SCOUT", "off")
    assert isinstance(js.default_journal_gateway(), js.UnavailableJournalScoutGateway)


def test_installed_journal_scout_is_used(monkeypatch, tmp_path):
    monkeypatch.setenv("JOURNAL_SCOUT_REPO", str(tmp_path))  # exists
    monkeypatch.delenv("SCANSCI_FIND_JOURNAL_SCOUT", raising=False)
    gw = js.default_journal_gateway()
    assert isinstance(gw, js.ResilientJournalScoutGateway)
    assert isinstance(gw.primary, js.JournalScoutMcpGateway)


@pytest.mark.parametrize("mode", ["hard", "boost"])
def test_unscreened_keeps_all_and_order(mode):
    out = apply_quality(_papers(), js.UnavailableJournalScoutGateway(), mode=mode)
    assert [p["title"] for p in out] == ["B", "A"]  # nothing dropped, ranking unchanged
    for p in out:
        assert p["quality"]["passed"] is True
        assert p["quality"]["policy"] == "unscreened"
        assert js.UNSCREENED_REASON in p["quality"]["evidence"][0]


def test_resilient_gateway_falls_back_on_failure(capsys):
    class Broken:
        version = ""
        data_sha256 = ""

        def health_check(self):
            raise RuntimeError("No module named journal_scout_mcp")

        def screen_papers(self, *a, **k):
            raise AssertionError("must not be called after the first failure")

    gw = js.ResilientJournalScoutGateway(Broken())
    out = apply_quality(_papers(), gw, mode="hard")
    assert len(out) == 2 and all(p["quality"]["policy"] == "unscreened" for p in out)
    assert "results are unscreened" in capsys.readouterr().err
