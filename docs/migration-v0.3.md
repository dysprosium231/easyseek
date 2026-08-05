# ScanSci Find v0.3 migration

v0.3 is additive. Existing `search`, `search_science`, candidate fields, Journal Scout integration, and ScanSci PDF queues retain their previous defaults.

## New execution stages

- `estimate_search` estimates known source totals using a one-record request.
- `smoke_search` retrieves four records per source and validates the normalized candidate contract.
- `calibrate_search` retrieves a bounded sample (100 records by default), deduplicates it, measures the human-review ratio, and checks an independent gold set.
- OpenAlex and Semantic Scholar now continue through real cursor/offset pagination until the per-source budget or source end is reached. Source reports retain total, pagination token, and completeness evidence.

CLI equivalents are `estimate`, `smoke`, and `calibrate`. Existing `plan` and `search` commands are unchanged.

## Citation, identity, and access support

- `expand_citations` accepts `source=semantic|opencitations|both`.
- `search_academic` accepts `citation_source`, `verify_candidate_identifiers`, and `resolve_oa`.
- `verify_identifiers` checks every available DOI through Crossref, PMID through PubMed, and arXiv ID through arXiv metadata while separating full verification, partial verification, missing records, metadata mismatch, rate limits, and provider failures.
- `resolve_open_access` uses Unpaywall v2 and requires `UNPAYWALL_EMAIL` or `SCANSCI_FIND_CONTACT_EMAIL`.

OpenCitations and Unpaywall are support services, not keyword-discovery databases. Their provenance is recorded separately from source-hit corroboration.

## New artifacts

Search run directories now always contain `identifier_verification.json` and `oa_report.json`; they are empty when those optional operations were not requested. `citation_rounds.json` now identifies the selected provider and records partial provider failures. Stage reports can be persisted as `estimate_report.json`, `smoke_report.json`, and `calibration_report.json` through `write_outputs`.

`evidence_table.csv` adds identifier-verification status, OA status, and license columns. These are additive columns.
