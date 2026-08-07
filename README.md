# ScanSci Find

ScanSci Find is a domain-neutral, auditable academic discovery layer for ScanSci. It searches and normalizes scholarly records, records what was and was not consulted, keeps journal-level evidence separate from article validity, and hands verified identifiers to ScanSci PDF and Zotero workflows.

Medicine is supported through an optional domain profile. The default identity and query model are general academic research; PICO, PubMed, Europe PMC, and clinical-trial sources are activated only when the task calls for them.

## Product boundaries

- MCP is the capability layer.
- Skill is the cognitive orchestration layer.
- CLI is the reproducible human and test entrypoint.
- Plugin is the ScanSci distribution layer.
- Journal Scout supplies venue-level evidence; it does not determine whether an individual article is valid.
- ScanSci PDF handles lawful full-text retrieval; ScanSci Find emits queues and access evidence.
- Browser-backed and institutional sources remain explicit adapters. ScanSci Find does not bypass login, captcha, subscriptions, or publisher controls.

## Search workflow

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

## Install for local development

```powershell
python -m pip install -e .
```

The package requires Python 3.11+ and has no mandatory runtime dependencies beyond the standard library.

## CLI

Inspect the source and domain registry:

```powershell
scansci-find sources
```

Build a protocol without searching:

```powershell
scansci-find plan "urban heat adaptation" --domain environmental_science --depth standard
```

For high-recall work, validate the protocol before the full run:

```powershell
scansci-find estimate "urban heat adaptation" --domain environmental_science --depth systematic
scansci-find smoke "urban heat adaptation" --domain environmental_science
scansci-find calibrate "urban heat adaptation" --domain environmental_science --depth systematic --sample-size 100
```

Run a general academic search:

```powershell
scansci-find search "urban ecology pollinator diversity" --domain general --depth standard --out runs/urban-ecology
```

Run citation chasing, identifier verification, OA resolution, and preprint matching explicitly when needed:

```powershell
scansci-find search "urban ecology pollinator diversity" --domain general --depth systematic --expand-citations --citation-source both --verify-identifiers --resolve-oa --find-preprints --out runs/urban-ecology-systematic
```

`--resolve-oa` requires `UNPAYWALL_EMAIL` or `SCANSCI_FIND_CONTACT_EMAIL`. Identifier, OA, and preprint support can also be run on an existing candidate file with `scansci-find verify`, `scansci-find resolve-oa`, and `scansci-find preprints`. Preprint matching searches arXiv and the Europe PMC Preprint Citation Index (bioRxiv, medRxiv, SSRN, Research Square) using conservative title-plus-author-or-year matching, and only enriches paywalled candidates — it never modifies a candidate's DOI or arXiv identity.

Order results by recency or citations instead of relevance, and attach Papers with Code code links:

```powershell
scansci-find search "time series forecasting" --sort recency --code-links --out runs/ts-recency
```

Interactive two-pass exploration (pass 1 summary table, then deep fetch on the confirmed subset):

```powershell
scansci-find explore "diffusion models in medical imaging" --domain medicine --limit 30 --out runs/explore.json
scansci-find deep-fetch runs/explore.json --out runs/explore-deep.json
```

Reproducible retrieval benchmarks (abstract coverage per source and per publisher, by DOI prefix):

```powershell
scansci-find benchmark "urban heat island" --sources openalex,pubmed,arxiv --sample-size 100 --out runs/bench-uhi
```

Use medicine only when requested:

```powershell
scansci-find search "remote monitoring after cardiac surgery" --domain medicine --depth standard --out runs/cardiac-monitoring
```

Route Chinese literature explicitly:

```powershell
scansci-find search "城市热岛 遥感" --domain chinese_general --cn --field title --year 2020:2026 --exclude-warning --out runs/cn-heat-island
scansci-find search "遥感 土地利用" --source cnki,baidu-scholar --doc-type journal --quality domestic_core --out runs/cn-land-use
```

Research-data discovery remains a separate quality profile:

```powershell
scansci-find search "pollinator image dataset" --profile research_data --domain research_data --out runs/pollinator-data
```

`--fixture <path>` runs deterministic tests or demonstrations without live network calls.

## Depth profiles

| Depth | Intended use | Per-source ceiling | Citation rounds | Claim boundary |
|---|---|---:|---:|---|
| `quick` | orientation and seed discovery | 20 | 0 | bounded search |
| `standard` | normal literature review | 100 | 1 planned | bounded until closure is run |
| `systematic` | high-recall protocol | 500 | up to 3 | never called complete without audit evidence |

## Domain profiles

The default `general` profile uses concept blocks and the cross-disciplinary metadata backbone. Additional profiles include `interdisciplinary`, `computer_science`, `engineering`, `natural_sciences`, `mathematics`, `physics_astronomy`, `chemistry_materials`, `earth_sciences`, `agriculture`, `medicine`, `life_sciences`, `public_health`, `social_sciences`, `education`, `psychology`, `law`, `humanities`, `economics`, `environmental_science`, `chinese_general`, and `research_data`.

Medical frameworks such as PICO/PECO and social-science frameworks such as SPIDER/PICo are optional protocol templates, not universal assumptions.

## Source architecture

Native connectors currently include:

- OpenAlex, Crossref, Semantic Scholar
- OpenCitations citation expansion and Meta enrichment; Unpaywall OA resolution
- arXiv, DBLP
- PubMed, Europe PMC
- Zenodo, DataCite, OpenML, Hugging Face Datasets, Kaggle
- Baidu Scholar, an external authorized CNKI MCP command, and Papers with Code code availability
- Google Scholar and CNKI via CDP: drives the user's own Chrome (remote debugging enabled via `chrome://inspect/#remote-debugging`), so login state carries over without any credential handling; requires `pip install scansci-find[cdp]` and degrades gracefully otherwise

The registry also describes contract-backed sources such as CORE, BASE, OpenAIRE, DOAJ, HAL, OSF Preprints, SciELO, Redalyc, OpenReview, CVF, zbMATH Open, MathSciNet, NASA ADS, INSPIRE HEP, ChemRxiv, AGRICOLA, ERIC, APA PsycInfo, NSSD, Wanfang, CQVIP, Web of Science, Scopus, Dimensions, The Lens, ProQuest Dissertations, ScienceDirect, IEEE Xplore, ACM DL, SSRN, JSTOR, DOAB, WorldCat, and ClinicalTrials.gov. Registration does not imply that credentials or an adapter are available; every run reports missing and unconsulted sources.

Discovery sources are kept separate from support routes. OpenCitations is implemented for citation expansion, Unpaywall for OA resolution, and Crossref/PubMed/arXiv for identity checks; they are not treated as interchangeable keyword-search databases.

## Run artifacts

Backward-compatible artifacts remain available:

- `candidates.json`
- `papers.md`
- `quality_report.json`
- `download_queue.json`
- `refs.bib`
- `source_report.json`
- `data_queue.json` when relevant

Auditable v0.2 artifacts add:

- `protocol.json`
- `run_manifest.json`
- `candidates.jsonl`
- `dedupe_clusters.json`
- `filter_report.json`
- `coverage_report.json` and `coverage_report.md`
- `prisma.json` and `PRISMA.md`
- `human_queue.csv`
- `evidence_table.csv`
- `dois.md`, `references.md`, and `references.bib`
- `zotero_items.json`

v0.3 adds:

- `citation_rounds.json` with the selected citation source, novelty, saturation, and partial failures
- `identifier_verification.json` for DOI/PMID/arXiv resolution and metadata mismatch status
- `oa_report.json` for Unpaywall OA locations and licenses (including which resolvers contributed OA links)
- `preprint_report.json` for matched preprint copies of paywalled candidates (arXiv / Europe PMC PPR)
- `code_report.json` for Papers with Code code-availability metadata
- `oa_manifest.json` routing each record to direct download (`eligible`) or the institutional phase, by full-text status
- optional `estimate_report.json`, `smoke_report.json`, and `calibration_report.json` for staged workflows
- `benchmark_report.json` / `benchmark_report.md` from the `benchmark` command (reproducible coverage measurements)

`download_queue.json` entries may carry `preprint_identifiers` (arXiv IDs of matched open versions) that ScanSci PDF can download directly — including as fallbacks when a paywalled DOI fails. `coverage_report` includes a Chapman capture-recapture population estimate when both PubMed and OpenAlex contributed records, and gold-set recall is bucketed into `found_in_window` / `found_out_of_window` / `found_undated`. When PRISMA counts are inconsistent, `PRISMA.md` is refused and `prisma_inconsistency.md` records why.

After ScanSci PDF runs (`scansci-pdf batch` or `scansci-pdf manifest`), `scansci-find reconcile <runs-dir>` writes the actual download outcomes back into `candidates.json`: successful downloads become `access_status=downloaded` (with the winning source), paywall failures `needs_institution`, Cloudflare/captcha failures `anti_bot_blocked`, and HTML/not-a-PDF responses `html_not_pdf` — the full-text status then reflects reality rather than prediction.

`coverage_report` explicitly records omitted sources, incomplete pagination, missing gold sets, and incomplete citation closure. A `systematic` request remains `bounded_search` until those conditions are satisfied.

## MCP

```powershell
scansci-find-mcp
```

New workflows should use:

- `plan_search`
- `estimate_search`
- `smoke_search`
- `calibrate_search`
- `search_academic`
- `expand_citations`
- `verify_identifiers`
- `resolve_open_access`
- `find_preprints`
- `enrich_code_links`
- `explore` (two-pass pass 1: summary table)
- `deep_fetch` (two-pass pass 2: verification + OA + preprints + code + BibTeX)

The v0.1 tools remain available for compatibility:

- `health_check`
- `list_sources`
- `search_science`
- `screen_candidates`
- `explain_candidate`
- `build_download_queue`
- `browser_doctor`

## Configuration

Copy `.env.example` values into your own environment or ignored local configuration. Never commit API keys, institutional credentials, cookies, or browser profiles.

OpenAlex changed its API policy on 2026-02-13 and now requires a free key on every request. Set `OPENALEX_API_KEY`; otherwise that source is reported as `blocked_configuration` while the remaining sources continue. `SEMANTIC_SCHOLAR_API_KEY`, `OPENCITATIONS_ACCESS_TOKEN`, and `NCBI_API_KEY` are optional but improve isolation from shared rate limits. Unpaywall requires `UNPAYWALL_EMAIL` or the shared `SCANSCI_FIND_CONTACT_EMAIL`. Contact variables are used for responsible API identification, and transient 429/5xx responses use bounded exponential backoff.

Source loops, identifier verification, and per-DOI OA resolution run in parallel by default (up to 8 workers). Set `SCANSCI_FIND_SEARCH_WORKERS` (source loops and verification) or `SCANSCI_FIND_OA_WORKERS` (Unpaywall lookups) to `1` for strictly serial behavior. Citation expansion remains serial because the OpenCitations rate limiter holds per-instance state; saturation now requires consecutive below-threshold rounds (`saturation_consecutive_rounds`, default 2).

Query terms are expanded deterministically before variant generation: built-in abbreviation/full-form pairs (LLM↔large language model, MRI↔magnetic resonance imaging, ...) apply bidirectionally, plus small per-domain synonym tables. Expansion never renames or drops a user term, so protocol fingerprints stay stable. Add your own vocabulary as JSON files (`{"pairs": {...}, "synonyms": {...}}`) in the directory named by `SCANSCI_FIND_VOCAB_DIR`.

Sorting: `--sort relevance|recency|citations`. Recency flags papers published in the last 6 months as `[新]` and places them first; boost/hard quality semantics are orthogonal to the sort.

CDP sources (Google Scholar, CNKI) need `pip install scansci-find[cdp]` and a Chrome with remote debugging enabled; without either they report `blocked_configuration` and the remaining sources continue. `scansci-find browser-doctor` now reports a `cdp_chrome` candidate.

CNKI remains compatible with the previous variable:

```powershell
$env:SCANSCI_FIND_CNKI_MCP_COMMAND='["uvx","--from","git+https://github.com/h-lu/cnki-mcp","cnki-mcp"]'
```

## Compatibility

Existing `scansci-find search`, `search_science`, legacy candidate fields, Journal Scout policies, and ScanSci PDF queues are preserved. See `docs/migration-v0.2.md` for the domain-neutral foundation and `docs/migration-v0.3.md` for staged retrieval, citation, verification, and OA additions.

## Acknowledgements

The retrieval protocol, measurement machinery, and browser-source designs in
this project were informed by two open-source projects:

- [lit-search](https://github.com/luwill/research-skills) — protocol-first
  high-recall retrieval with gold-set recall, saturation criteria, and
  PRISMA honesty; its documented coverage measurements motivated our
  reproducible `benchmark` command.
- [Academic-Search](https://github.com/ustc-ai4science/academic-search) —
  CDP-driven reuse of the user's own Chrome login state for Google Scholar
  and CNKI, the two-pass explore/deep-fetch flow, and the full-text status
  taxonomy.

Both are MIT-licensed; this project re-implements and extends those ideas in
its own engine rather than embedding their code.
