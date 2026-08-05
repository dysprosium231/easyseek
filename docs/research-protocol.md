# Research protocol contract

## Default assumptions

- Use `domain=general` when the user has not identified a discipline.
- Use concept blocks as the default query framework.
- Treat PICO, PECO, SPIDER, PICo, and problem-method-dataset-metric as optional domain templates.
- Keep records with missing year, language, or type metadata during high-recall filtering; exclude only known mismatches.
- Require explicit evidence before calling a run systematic or exhaustive.

## Depth semantics

`quick` produces orientation and seeds. `standard` plans domain sources and one citation round but remains bounded until citation expansion is executed. `systematic` plans supplemental sources and multiple rounds; the coverage report determines whether the run actually reached systematic completeness.

## Gold set

A gold set contains known relevant papers expressed with DOI, arXiv ID, PMID, or title. Gold-set recall calibrates query coverage. It is not a test set for article quality and must not be silently added from the retrieved result set.

## Screening

Store inclusion, exclusion, and uncertainty as explicit decisions with reasons. Do not treat missing metrics, unavailable abstracts, preprint status, or low journal impact as automatic exclusion unless the protocol says so.

## Citation closure

Run citation expansion after the initial candidate screen. Record each round's attempted seeds, fetched records, new unique records, novelty ratio, failures, and saturation decision.
