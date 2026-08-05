# Audit artifacts

Interpret run outputs as follows:

- `protocol.json`: intended method and source plan.
- `source_report.json`: runtime source success, failure, count, and elapsed time.
- `dedupe_clusters.json`: records merged into each canonical candidate.
- `evidence_table.csv`: compact identity, corroboration, access, venue, and warning dimensions.
- `identifier_verification.json`: verification counts and DOI/PMID/arXiv status; candidates retain per-record evidence.
- `oa_report.json`: Unpaywall resolution status and OA count; errors do not imply that an article is closed access.
- `citation_rounds.json`: selected citation provider(s), round novelty, saturation, and provider failures.
- `estimate_report.json`, `smoke_report.json`, `calibration_report.json`: optional stage-gate evidence when a workflow persists the preflight stages.
- `human_queue.csv`: unresolved identifiers, single-source records, or metadata conflicts.
- `coverage_report.*`: gold-set recall, unconsulted sources, source contribution, citation rounds, and limitations.
- `prisma.json` / `PRISMA.md`: mechanical counts; unscreened records remain explicitly awaiting screening.
- `run_manifest.json`: run identity, method status, and artifact inventory.

Do not infer that a missing artifact step occurred. In particular, `depth=systematic` is only intent; `systematic_complete=true` is the completion claim.
