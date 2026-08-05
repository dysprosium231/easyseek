# ScanSci Find v0.2 architecture

## Design objective

Evolve ScanSci Find into a general academic discovery and evidence-engineering layer while preserving the v0.1 CLI, MCP tools, candidate fields, Journal Scout integration, and ScanSci PDF queue.

The core must not encode medicine as the default discipline. Medical databases and frameworks are domain adapters selected by protocol.

## Layer model

```text
Skill / agent policy
    -> protocol and domain routing
        -> source capability registry
            -> native, external, or contract adapters
                -> normalization and conservative deduplication
                    -> evidence dimensions and Journal Scout venue evidence
                        -> screening and citation expansion
                            -> coverage, PRISMA, queues, Zotero, references
```

### Protocol layer

`scansci_find.protocol.SearchProtocol` records the research question, domain, framework, depth, concept blocks, criteria, languages, years, document types, gold set, source plan, record ceilings, citation rounds, and saturation threshold.

The protocol identifier is deterministic for the stable search inputs. The generation timestamp is informational and is excluded from the identifier hash.

### Source layer

`scansci_find.source_registry` is the canonical capability directory. Every source declares:

- role and supported domains;
- search, citation, full-text, export, or dataset capabilities;
- access model;
- `native` or `contract` implementation status;
- core, domain, or supplemental tier.

The registry is not an availability claim. Runtime `source_status` is the only evidence that a source was actually queried.

The protocol also separates discovery sources from support routes: identity/metadata verification, citation expansion, and OA resolution. A support service such as OpenCitations or Unpaywall is not counted as an independent keyword-search database merely because it is registered.

### Candidate layer

The v0.1 flat candidate shape remains valid. v0.2 adds:

- `canonical_id`;
- `identifiers` for DOI, arXiv, PMID, PMCID, and DBLP keys;
- `source_records` for source-local provenance;
- `evidence_dimensions` for identity, corroboration, availability, venue, citation signal, and warnings.

Deduplication remains conservative: exact persistent identifiers are preferred, followed by normalized title plus author/year or journal/year. The engine writes `dedupe_clusters.json` so merges can be audited.

### Quality layer

Journal Scout evidence has explicit scope `journal_level_evidence_not_article_validity`. It may boost or filter candidates when the user asks for venue restrictions, but it is never presented as proof that an article's methods or conclusions are sound.

Research-data records use a separate scope and are not judged with JIF.

### Audit layer

Every run reports raw, deduplicated, retained, included, excluded, and awaiting-screening counts. It also records source overlap, unique contribution, gold-set recall, citation rounds, unconsulted sources, and methodological limitations.

`systematic_complete` is false unless all of these are evidenced:

- full pagination verified;
- planned sources successfully consulted;
- requested citation rounds completed or saturation reached;
- a gold set was supplied and checked.

## Compatibility boundary

`search_science` remains the v0.1 compatibility entrypoint and defaults to the former four-source quick search. `search_academic` is the v0.2 protocol-aware entrypoint. Existing artifact names are retained alongside new audit artifacts.

No existing source, credential, browser profile, or project is moved by this upgrade.
