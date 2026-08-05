# Source catalog guidance

Use sources by role rather than treating every database as interchangeable.

## Cross-disciplinary backbone

- OpenAlex: broad discovery, citation graph, OA clues. Its API requires `OPENALEX_API_KEY` on every request as of 2026-02-13; a missing key must be reported as `blocked_configuration`.
- Crossref: DOI and publisher metadata verification.
- Semantic Scholar: discovery, citation graph, OA clues.
- OpenCitations Index v2 plus Meta: native backward/forward citation expansion and citation metadata enrichment; optional access token.
- Unpaywall v2: native DOI-to-OA location and license resolution; requires a responsible contact email.

## Domain adapters

- Computer science and engineering: arXiv, DBLP, OpenReview, CVF, IEEE Xplore, ACM DL.
- Mathematics, physics, astronomy, and chemistry: arXiv, zbMATH Open, MathSciNet, NASA ADS, INSPIRE HEP, ChemRxiv.
- Medicine and life sciences: PubMed, Europe PMC, bioRxiv, medRxiv, ClinicalTrials.gov.
- Agriculture, education, and psychology: AGRICOLA, ERIC, APA PsycInfo.
- Social sciences, law, economics, and humanities: SSRN, RePEc, JSTOR, NSSD, Google Scholar, DOAB, WorldCat, The Lens.
- Research data and software: Zenodo, DataCite, OpenML, Hugging Face, Kaggle, GitHub.

## Open and regional breadth

CORE, BASE, OpenAIRE, DOAJ, HAL, OSF Preprints, SciELO, and Redalyc supplement disciplinary indexes. OpenCitations belongs to citation expansion, Unpaywall to OA resolution, and Crossref/DataCite to identity and metadata checks; do not count support services as independent keyword-search sources.

## Chinese and institutional adapters

Use CNKI, NSSD, Wanfang, CQVIP, Baidu Scholar, Web of Science, Scopus, ScienceDirect, IEEE, ACM, and JSTOR only when their runtime status confirms an authorized adapter and access. Browser/login availability is not implied by registration.

## Retrieval and enrichment

Crossref and DataCite are often metadata/enrichment sources rather than independent high-recall search sources. Repository sources may supply lawful full text but weaker canonical metadata. Preserve both roles in provenance.

Native HTTP adapters use bounded retries for 429/5xx responses and preserve pagination evidence. Semantic Scholar and NCBI keys are optional; DBLP requests must respect its published pacing guidance. Never turn a blocked, throttled, or first-page-only response into an `ok + complete` claim.
