# Search protocol

Use `general` unless the task clearly belongs to another profile. Record the question, concept blocks, criteria, languages, years, document types, depth, gold set, source plan, record ceiling, citation rounds, and saturation threshold.

Depth meanings:

- `quick`: orientation; no citation closure.
- `standard`: normal review; plan one citation round.
- `systematic`: high-recall workflow; plan supplemental sources and up to three rounds.

For high-recall work, use 3–5 concept blocks. Combine synonyms within a block with OR and required blocks with AND where the source supports Boolean search. For sources without Boolean APIs, retrieve broadly and apply the same criteria locally.

Do not silently discard records with missing abstracts, metrics, language, or year. Send ambiguous records to the human queue.

A gold set should contain known relevant DOI, arXiv, PMID, or title records chosen independently of the run. Report recall and missing gold items.

Before a full standard/systematic run:

1. Run `estimate_search` and revise queries whose known-source total exceeds the recorded broadness threshold.
2. Run `smoke_search` at four records per source. Do not proceed while an executable source fails or normalized records violate the candidate contract.
3. Run `calibrate_search` at 100 records. Review deduplication, human-queue ratio, source status, and independent gold-set recall. A `revise_protocol` decision is a gate, not a cosmetic warning.

Retrieval must honor the recorded budget through real source pagination. Preserve cursor/offset, reported source totals, elapsed time, and `pagination_complete`; a budget-limited result can be successful while still incomplete.

Run backward/forward citation expansion after initial screening. Use Semantic Scholar, OpenCitations, or both; prefer both for high-recall work when available. Stop only when the planned rounds finish or the novelty ratio meets the recorded saturation threshold. Report partial provider failures and do not hide zero-yield rounds.

Verify every available DOI with Crossref, PMID with PubMed, and arXiv identifier with arXiv metadata before calling them verified. Distinguish `partial`, `not_found`, `metadata_mismatch`, configuration/authentication, rate-limit, and network errors. Resolve OA locations separately through Unpaywall; OA availability is not a relevance or quality signal.
