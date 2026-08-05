---
name: scansci-find
description: Use ScanSci Find for domain-neutral academic literature discovery, high-recall multi-source searches, systematic-search protocols, citation chasing, Chinese and international source routing, research-data discovery, Journal Scout venue evidence, PRISMA and coverage reporting, Zotero exports, and ScanSci PDF download queues. Trigger when a user asks to find papers, search scholarly databases, build a literature corpus or review seed set, verify bibliographic records, search CNKI/PubMed/arXiv/OpenAlex or related sources, trace citations, assess search coverage, or prepare references and full-text retrieval queues.
---

# ScanSci Find

## Core policy

Treat ScanSci Find as a general academic discovery and evidence-engineering workflow. Default to `domain=general`. Activate medicine, computer science, engineering, social science, humanities, environmental science, Chinese, or research-data profiles only when the task requires them.

Do not impose PICO or medical terminology on general questions. Use PICO/PECO, SPIDER/PICo, or problem-method-dataset-metric only as optional domain templates.

Keep the layers separate:

- Use MCP/CLI for deterministic retrieval, normalization, deduplication, evidence, and artifacts.
- Use this skill for scoping, query design, screening judgment, source selection, and interpretation.
- Use Journal Scout only for journal-level evidence.
- Hand verified identifiers to ScanSci PDF for lawful full-text retrieval.

Read `references/search-protocol.md` when planning standard or systematic work. Read `references/source-catalog.md` when choosing databases or diagnosing source coverage. Read `references/audit-artifacts.md` when interpreting a completed run. Read `references/scansci-find-contract.md` for exact CLI, MCP, field, and compatibility contracts.

## Workflow

1. Clarify the research question, scope, years, languages, document types, and intended depth.
2. Build a protocol with `plan_search` or `scansci-find plan` before standard/systematic work.
3. Define 3–5 concept blocks and useful synonyms for complex questions. Preserve the user's exact terms.
4. Ask for or derive a small gold set when high recall matters. Never construct the gold set from the same retrieved results used to measure recall.
5. Call `estimate_search` to detect an empty, narrow, workable, broad, or revision-needed query before spending the full budget.
6. Call `smoke_search` with four records per source. Repair failed source configuration or candidate-contract errors before continuing.
7. For standard/systematic work, call `calibrate_search` with a 100-record sample. Revise the protocol when ambiguity exceeds the threshold or the independent gold set is missed.
8. Route sources by domain and access. Distinguish registered, executable, configured, failed, and unconsulted sources.
9. Execute `search_academic`. Use `search_science` only when compatibility with a v0.1 caller is required.
10. Inspect source failures, pagination evidence, dedupe clusters, identifier conflicts, and the human queue before summarizing.
11. Screen candidates with explicit include/exclude/uncertain decisions and reasons. Missing metrics are not automatic exclusion.
12. For standard/systematic work, call `expand_citations` after initial screening. Prefer `source=both` when Semantic Scholar and OpenCitations are available, and record each source failure, round novelty, and saturation state.
13. Call `verify_identifiers` before describing DOI/PMID/arXiv values as verified. Use `resolve_open_access` only after identity resolution and report Unpaywall failures separately from paywall status.
14. Report coverage, gold-set recall, source contribution, PRISMA counts, and limitations. State what was not searched.
15. Export verified DOI/BibTeX/Zotero artifacts and pass `download_queue.json` to ScanSci PDF when full text is needed.

## Depth rules

- Use `quick` for orientation and seed discovery.
- Use `standard` for normal literature reviews. Plan one citation round, but describe the result as bounded until it is executed.
- Use `systematic` only when the user needs high recall and auditability. A requested depth is not proof of systematic completeness.

Never describe a run as exhaustive or systematic when `coverage_report.systematic_complete` is false. Say `bounded search` and name the missing conditions.

## Quality rules

- Keep relevance, bibliographic identity, source corroboration, availability, citation signals, journal evidence, and article-level appraisal separate.
- Never treat JIF, JCR/CAS quartile, citations, or source count as proof that an article is valid.
- Use `boost` when quality should influence ordering without hiding records.
- Use `hard` only for explicit user restrictions such as “只要”“必须”“限定” or a registered review protocol.
- Preserve preprints, grey literature, negative results, and no-metric papers unless the protocol excludes them.

## Access and safety

- Do not bypass paywalls, captcha, login, institutional access, or publisher controls.
- Reuse authorized browser/MCP adapters and the user's existing authenticated session when permitted.
- Never store credentials, cookies, tokens, or browser profiles in run artifacts.
- Treat Google Scholar, CNKI, Wanfang, CQVIP, WoS, Scopus, ScienceDirect, IEEE, ACM, and JSTOR as conditional until runtime status proves access.

## Reporting

Lead with the search scope and method status. Include candidate counts, sources consulted/failed, major coverage limitations, and whether citation closure was performed. Cite candidate identifiers or source URLs for substantive claims.

Use artifacts outside the skill folder. Preserve the run directory so another agent can audit or continue the search.
