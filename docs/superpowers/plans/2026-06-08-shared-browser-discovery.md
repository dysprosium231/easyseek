# Shared Browser Discovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a no-install browser runtime discovery layer so ScanSci Find can prefer shared browser capabilities instead of installing or embedding duplicate browser stacks.

**Architecture:** Add a small resolver module inside ScanSci Find that probes configured shared commands, PATH commands, importable packages, existing ScanSci PDF browser modules, and system Chrome/Edge. Expose the result through `scansci-browser doctor`, `scansci-find browser-doctor`, and an MCP `browser_doctor` tool. The resolver never installs dependencies; it only reports reuse options and install hints.

**Tech Stack:** Python 3.11 standard library only, pytest/unittest for tests, existing argparse-based CLI and JSON-RPC MCP contract.

---

### Task 1: Resolver Tests

**Files:**
- Create: `tests/test_browser_discovery.py`

- [x] Write tests for priority order: explicit `SCANSCI_BROWSER_COMMAND`, `scansci-browser` on PATH, importable `scansci_browser`, existing ScanSci PDF browser module, system Chrome/Edge, then install hint.
- [x] Verify the tests fail because `scansci_find.browser_discovery` does not exist.

### Task 2: Resolver Implementation

**Files:**
- Create: `scansci_find/browser_discovery.py`

- [x] Implement `BrowserRuntimeResolver` with injectable probes for deterministic tests.
- [x] Implement `doctor()` returning a JSON-serializable dict with `selected`, `candidates`, `install_needed`, `install_hint`, `profile_dir`, and `cache_dir`.
- [x] Ensure no function installs packages or downloads browsers.

### Task 3: CLI/MCP Exposure

**Files:**
- Modify: `scansci_find/cli.py`
- Modify: `scansci_find/mcp_contract.py`
- Modify: `pyproject.toml`

- [x] Add `scansci-find browser-doctor`.
- [x] Add console script `scansci-browser = scansci_find.browser_discovery:main`.
- [x] Add MCP tool `browser_doctor`.

### Task 4: Documentation

**Files:**
- Modify: `README.md`
- Modify: `plugin/scansci-find/skills/scansci-find/SKILL.md`
- Modify: `plugin/scansci-find/skills/scansci-find/references/scansci-find-contract.md`

- [x] Document probe order, no-install behavior, and shared `D:\Dev\browser-profiles\scansci` / `D:\Dev\cache\browser` defaults.

### Task 5: Verification

**Commands:**
- `python -m pytest -q`
- `python -m unittest discover -v`
- `python -m scansci_find browser-doctor`

- [x] All tests pass.
- [x] Doctor command returns JSON and does not install anything.
