# ScanSci Find — Domain-neutral, auditable, multi-source academic discovery

<p align="center"><b><a href="README.md">中文</a> | English</b></p>

ScanSci Find is the academic discovery layer of ScanSci: it treats literature search as engineering. It searches and normalizes scholarly records across many sources, records what was and was not consulted, keeps journal-level evidence separate from article validity, and hands verified identifiers to ScanSci PDF and Zotero workflows. Protocols come first, recall is measurable, and every claim lands as an auditable artifact.

## Product boundaries

- **MCP** is the capability layer.
- **Skill** is the cognitive orchestration layer.
- **CLI** is the reproducible human and test entrypoint.
- **Journal Scout** supplies venue-level evidence; it does not determine whether an individual article is valid.
- **ScanSci PDF** handles lawful full-text retrieval; ScanSci Find emits queues and access evidence.
- Browser-backed and institutional sources remain explicit adapters. ScanSci Find does not bypass login, captcha, subscriptions, or publisher controls.

Medicine is supported through an optional domain profile. The default identity and query model are general academic research; PICO, PubMed, Europe PMC, and clinical-trial sources are activated only when the task calls for them.

## Quick start

```powershell
python -m pip install -e .          # Python 3.11+, no mandatory runtime dependencies
scansci-find search "urban heat island" --depth standard --verify-identifiers --resolve-oa --find-preprints --out runs/heat
scansci-find explore "diffusion models" --domain medicine --limit 30    # two-pass pass 1: summary table
scansci-find deep-fetch runs/explore.json --out runs/explore-deep.json # pass 2: deep enrichment
scansci-find benchmark "urban heat island" --sample-size 100 --out runs/bench   # reproducible coverage benchmark
```

## The pipeline

```text
question -> protocol -> volume estimate -> 4-record smoke test
         -> 100-record calibration -> budgeted paginated retrieval
         -> normalization/deduplication -> screening -> citation chasing
         -> identifier/OA verification -> coverage/PRISMA -> PDF/Zotero handoff
```

The protocol separates four concepts that older search tools often blur:

1. A source can be registered without being executable on the current machine.
2. A source can be queried without providing full text.
3. Journal evidence is not article-level evidence.
4. A run is not systematic unless pagination, planned-source coverage, gold-set checks, and citation closure are actually complete.

## Capabilities

### Search & routing

| Capability | Description |
|---|---|
| 13-source federation | OpenAlex / Crossref / Semantic Scholar / arXiv / DBLP / PubMed / Europe PMC / Zenodo / DataCite / OpenML / Hugging Face / Kaggle / Baidu Scholar / CNKI, routed by domain |
| CDP browser sources | Google Scholar and CNKI drive your own Chrome (remote debugging), carrying login state without any credential handling; `pip install scansci-find[cdp]` |
| Query expansion | Built-in bidirectional abbreviation pairs and per-domain synonyms; expansion is a pure function so protocol fingerprints stay stable; user vocab via `SCANSCI_FIND_VOCAB_DIR` |
| Sorting | `--sort relevance\|recency\|citations`; recency flags papers from the last 6 months as `[新]` and places them first |
| Chinese routing | `--domain chinese_general --cn`; CNKI / Baidu Scholar / Wanfang / CQVIP / NSSD |

### Enrichment

- **Preprint matching**: conservatively matches paywalled papers to open versions on arXiv and the Europe PMC Preprint Citation Index (bioRxiv / medRxiv / SSRN / Research Square) by title similarity plus author or year; additive only, never mutates identity.
- **Code links**: no-key Papers with Code enrichment (official repositories first, then star count).
- **OA resolution**: aggregates candidate-carried OpenAlex / Semantic Scholar / Europe PMC links before spending Unpaywall quota, with concurrent lookups.
- **Identifier verification**: DOI→Crossref, PMID→PubMed, arXiv→arXiv cross-checks distinguishing verified / partial / mismatch / not_found.
- **Citation chasing**: bidirectional expansion via Semantic Scholar + OpenCitations; saturation requires consecutive below-threshold rounds.

### Interaction

- **explore** (two-pass pass 1): quick search → lightweight summary table (title, year, venue, citations, PDF hint, `[新]` flag), no abstracts.
- **deep-fetch** (pass 2): full enrichment on the confirmed subset — verification + OA + preprints + code + BibTeX.

### Measurement & audit

- **Chapman capture-recapture**: PubMed∩OpenAlex overlap estimates the population size with a 95% CI, reported in the coverage report.
- **PRISMA refusal**: inconsistent counts refuse to render PRISMA.md; `prisma_inconsistency.md` records why.
- **`benchmark` command**: classifies publishers by DOI prefix and measures per-source abstract coverage — reproducible measurements, not one-off claims.
- **Window-bucketed gold-set recall**: `found_in_window` / `found_out_of_window` / `found_undated`.

### Artifacts & closed loop

`candidates.json`, `download_queue.json`, `oa_manifest.json` (routing `open_pdf` records to direct download and `needs_institution` records to the institutional phase), `coverage_report`, `PRISMA.md`, `benchmark_report`, `preprint_report.json`, `code_report.json`, and more.

Closed loop with ScanSci PDF:

```powershell
litloop manifest runs/x/oa_manifest.json --output runs/x/pdfs   # manifest-routed downloads
litloop batch queue.txt --scihub --runs-dir runs/x              # queue + preprint fallbacks (failed paywalled DOIs retry their arXiv versions)
scansci-find reconcile runs/x                                       # write download outcomes back: downloaded / anti_bot_blocked / html_not_pdf
```

## CLI reference

| Command | Purpose |
|---|---|
| `scansci-find plan / estimate / smoke / calibrate` | Protocol-first gates: build the protocol, estimate volume, 4-record smoke contract check, 100-record calibration (stop when the human queue exceeds 15%) |
| `scansci-find search` | Full search with audit artifacts (`--expand-citations --verify-identifiers --resolve-oa --find-preprints --code-links --sort`) |
| `scansci-find explore / deep-fetch` | Two-pass interaction |
| `scansci-find verify / resolve-oa / preprints / codes` | Standalone enrichment on existing candidate files |
| `scansci-find benchmark` | Reproducible coverage benchmark |
| `scansci-find reconcile <runs-dir>` | Write ScanSci PDF download outcomes back into candidates |
| `scansci-find browser-doctor / sources` | Browser runtime probe / source registry |

## Depth profiles & domains

| Depth | Intended use | Per-source ceiling | Citation rounds | Claim boundary |
|---|---:|---:|---|
| `quick` | orientation and seed discovery | 20 | 0 | bounded search |
| `standard` | normal literature review | 100 | 1 planned | bounded until closure is run |
| `systematic` | high-recall protocol | 500 | up to 3 | never called complete without audit evidence |

Domain profiles: `general` (default), `interdisciplinary`, `computer_science`, `engineering`, `natural_sciences`, `mathematics`, `physics_astronomy`, `chemistry_materials`, `earth_sciences`, `agriculture`, `medicine`, `life_sciences`, `public_health`, `social_sciences`, `education`, `psychology`, `law`, `humanities`, `economics`, `environmental_science`, `chinese_general`, and `research_data`. Frameworks such as PICO/PECO and SPIDER/PICo are optional templates, not universal assumptions.

## MCP tools

New workflows: `plan_search`, `estimate_search`, `smoke_search`, `calibrate_search`, `search_academic`, `expand_citations`, `verify_identifiers`, `resolve_open_access`, `find_preprints`, `enrich_code_links`, `explore`, `deep_fetch`.

v0.1 compatibility tools: `health_check`, `list_sources`, `search_science`, `screen_candidates`, `explain_candidate`, `build_download_queue`, `browser_doctor`.

## Configuration

Copy `.env.example` values into your own environment or an ignored local configuration. Never commit API keys, institutional credentials, cookies, or browser profiles.

- `OPENALEX_API_KEY`: OpenAlex requires a free key on every request since 2026-02-13; when missing, that source reports `blocked_configuration` while the remaining sources continue.
- `UNPAYWALL_EMAIL` or `SCANSCI_FIND_CONTACT_EMAIL`: required for Unpaywall resolution; contact variables identify the caller responsibly.
- Concurrency: source loops and verification default to 8 workers (`SCANSCI_FIND_SEARCH_WORKERS`), Unpaywall lookups to `SCANSCI_FIND_OA_WORKERS`; set to `1` for strictly serial behavior. Citation expansion stays serial (OpenCitations rate limiter holds per-instance state).
- `SCANSCI_FIND_VOCAB_DIR`: custom query-expansion vocabulary (`{"pairs": {...}, "synonyms": {...}}` JSON files).
- CDP sources (Google Scholar / CNKI) need `pip install scansci-find[cdp]` and a Chrome with remote debugging enabled (`chrome://inspect/#remote-debugging`); otherwise they degrade to `blocked_configuration`. `scansci-find browser-doctor` reports a `cdp_chrome` candidate.
- CNKI remains compatible with the previous variable:

```powershell
$env:SCANSCI_FIND_CNKI_MCP_COMMAND='["uvx","--from","git+https://github.com/h-lu/cnki-mcp","cnki-mcp"]'
```

## Compliance

- No bypassing of paywalls, captcha, login, institutional access, or publisher controls.
- CDP sources drive the user's own Chrome, never touch credentials, stop on CAPTCHA, and honor per-session search budgets.
- Commercially licensed or copyrighted ranking data (JCR / CCF / CAS quartiles) is never bundled; supply it yourself.
- This layer never downloads; ScanSci PDF handles full-text retrieval.

## Compatibility

Existing `scansci-find search`, `search_science`, legacy candidate fields, Journal Scout policies, and ScanSci PDF queues are preserved. See `docs/migration-v0.2.md` for the domain-neutral foundation and `docs/migration-v0.3.md` for staged retrieval, citation, verification, and OA additions.

## Acknowledgements

The retrieval protocol, measurement machinery, and browser-source designs in this project were informed by two open-source projects:

- [lit-search](https://github.com/luwill/research-skills) — protocol-first high-recall retrieval with gold-set recall, saturation criteria, and PRISMA honesty; its documented coverage measurements motivated our reproducible `benchmark` command.
- [Academic-Search](https://github.com/ustc-ai4science/academic-search) — CDP-driven reuse of the user's own Chrome login state for Google Scholar and CNKI, the two-pass explore/deep-fetch flow, and the full-text status taxonomy.

Both are MIT-licensed; this project re-implements and extends those ideas in its own engine rather than embedding their code.

## License

MIT
