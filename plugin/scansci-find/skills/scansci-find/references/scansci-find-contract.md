# ScanSci Find contract

## Entrypoints

CLI:

```powershell
scansci-find sources
scansci-find plan "<topic>" --domain general --depth standard
scansci-find estimate "<topic>" --domain general --depth standard
scansci-find smoke "<topic>" --domain general
scansci-find calibrate "<topic>" --domain general --sample-size 100
scansci-find search "<topic>" --domain general --depth standard --out runs/<slug>
scansci-find verify candidates.json --out verified.json
scansci-find resolve-oa verified.json --out resolved.json
scansci-find browser-doctor
```

MCP tools:

- `health_check`
- `list_sources`
- `plan_search`
- `estimate_search`
- `smoke_search`
- `calibrate_search`
- `search_academic`
- `search_science` (v0.1 compatibility)
- `verify_identifiers`
- `resolve_open_access`
- `screen_candidates`
- `explain_candidate`
- `build_download_queue`
- `expand_citations`
- `browser_doctor`

## Candidate compatibility

Preserved fields include `artifact_type`, `title`, `title_zh`, `title_en`, `authors`, `year`, `doi`, `arxiv_id`, `journal`, `issn`, `eissn`, `source_hits`, `relevance_score`, `quality`, `download`, `links`, `abstract`, `keywords`, and `access`.

Additive v0.2 fields include `pmid`, `pmcid`, `dblp_id`, `identifiers`, `canonical_id`, `source_records`, and `evidence_dimensions`.

Additive v0.3 fields include `identifier_verification`, `oa_resolution`, citation `discovery`/`citation_relation` provenance, and OA status/license in `access`. The search API adds `citation_source`, `verify_candidate_identifiers`, and `resolve_oa` without changing existing defaults.

`quality.scope=journal_level_evidence_not_article_validity` means Journal Scout evidence applies to the venue, not the paper's methods or findings.

## Artifacts

Compatibility artifacts:

- `candidates.json`
- `papers.md`
- `quality_report.json`
- `download_queue.json`
- `refs.bib`
- `source_report.json`

Audit and interoperability artifacts:

- `protocol.json`
- `run_manifest.json`
- `candidates.jsonl`
- `dedupe_clusters.json`
- `filter_report.json`
- `coverage_report.json` and `coverage_report.md`
- `prisma.json` and `PRISMA.md`
- `human_queue.csv`
- `evidence_table.csv`
- `dois.md`
- `references.md` and `references.bib`
- `zotero_items.json`
- `citation_rounds.json`
- `identifier_verification.json`
- `oa_report.json`
- optional `estimate_report.json`, `smoke_report.json`, and `calibration_report.json`
- `data_queue.json` when research objects are present

## Compatibility

Keep `search_science`, existing CLI flags, `SCANSCI_FIND_CNKI_MCP_COMMAND`, Journal Scout fields, and ScanSci PDF queue entries working for v0.1 callers.
