# Migration from ScanSci Find v0.1

## Preserved interfaces

- Package name `scansci-find`
- Python package `scansci_find`
- CLI commands `scansci-find search` and `scansci-find browser-doctor`
- MCP server `scansci-find-mcp`
- MCP tools `search_science`, `screen_candidates`, `explain_candidate`, and `build_download_queue`
- Flat candidate fields and v0.1 artifact names
- Journal Scout and ScanSci PDF handoff contracts
- `SCANSCI_FIND_CNKI_MCP_COMMAND`

## Additive interfaces

- CLI: `plan`, `sources`, `--domain`, `--depth`, `--question`, language/year controls, and citation-round planning
- MCP: `plan_search`, `search_academic`, and `expand_citations`
- Candidate fields: `canonical_id`, `identifiers`, `source_records`, and `evidence_dimensions`
- Audit and interoperability artifacts documented in the README
- Native PubMed, Europe PMC, and DBLP connectors
- Full source and domain capability registry

## Behavioral changes

- The new default research identity is general academic search. Medicine is opt-in.
- `search_science` keeps its former quick-source behavior for compatibility.
- `search_academic` exposes protocol and coverage information and may report contract sources as unconsulted.
- A requested `systematic` depth does not make the result systematic by itself.
- Venue metrics carry an explicit journal-level scope warning.

## Rollback

No old project directory, data file, browser profile, credential, or environment is moved. The v0.1 entrypoints remain callable, so callers can migrate incrementally.
