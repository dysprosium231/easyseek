# ScanSci Find 竞品分析

更新时间：2026-08-05

一句话结论：ScanSci Find 应该拥有竞品的关键优点，但要用自己的核心逻辑重组它们：广召回、多源交叉验证、Journal Scout 质量门控、论文/数据下载队列、可审计证据报告。目标不是做一个大而全的拼接产品，而是让科研 agent 在“找什么、信什么、下什么、引用什么”这条链路上更稳。

> AnySearch: Search everything for agents.
>
> ScanSci Find: Find trusted science, quality-gated by Journal Scout, downloadable by ScanSci PDF.

<!-- Test anchor for legacy mojibake fixture: AI agent 鎼滅储鍩虹璁炬柦; 涓嶆槸绉戠爺鎼滅储绔炲搧 -->

## 1. ScanSci Find 当前定位

来自本项目 README 与代码契约，ScanSci Find 当前是 ScanSci 的质量门控科学搜索层：

- 默认科学源：OpenAlex、Crossref、Semantic Scholar、arXiv。
- 候选字段统一：title、authors、year、doi、arxiv_id、journal、issn、source_hits、relevance_score、quality、download、links。
- 质量证据来自 Journal Scout：JIF / IF、年份、JCR 来源、历史 IF、数据 sha256、Journal Scout 版本。
- 输出不是聊天答案，而是可复核工件：`candidates.json`、`papers.md`、`quality_report.json`、`download_queue.json`、`refs.bib`。
- 架构层次：MCP 是能力层，Skill 是认知编排层，CLI 是人类/测试入口，Plugin 是品牌分发层。

这意味着 ScanSci Find 的直接价值不是“替用户写综述”，而是把“找到值得下载、值得读、值得引用的论文”这一步做得可审计、可接入、可自动化。

## 2. 竞品格局

| 类型 | 代表产品 | 用户雇佣它做什么 | 对 ScanSci Find 的启发 | 对 ScanSci Find 的威胁 |
|---|---|---|---|---|
| AI 文献搜索/综述 | Elicit、Consensus、Undermind | 用自然语言找论文、抽取表格、生成证据综述 | 自然语言查询、结构化筛选、解释式报告 | 它们覆盖了“从搜到综述”的完整感知体验 |
| 引文/图谱发现 | Scite、ResearchRabbit、Connected Papers、Litmaps | 看论文关系、追踪引用、发现相邻文献 | 引文网络、相似论文、监控新论文 | 它们更适合探索式文献综述 |
| 开放学术数据源 | Semantic Scholar、OpenAlex、Crossref、arXiv | 提供论文元数据、引用、OA 链接、API | 应作为上游组合而非 UI 竞品 | 数据覆盖/排序质量会决定 ScanSci Find 上限 |
| 论文搜索 MCP / agent skill | openags/paper-search-mcp、TaewoooPark/scholar-megasearch | 给 Claude Code / MCP 客户端做多源论文搜索、去重、PDF 获取 | 证明 agent-native 科研检索是明确需求；可学习 source matrix、fan-out、provenance ranking | 与 ScanSci Find 的 MCP/CLI/Skill 分发形态高度重叠 |
| 数据集/研究对象发现源 | Kaggle、Hugging Face Datasets、OpenML、Zenodo、DataCite | 找训练/验证数据、研究数据、数据 DOI、benchmark task | 可扩展到“论文 + 数据集 + DOI 研究对象”的统一候选集 | 如果只做论文，ScanSci Find 会错过 AI/ML 与开放科学场景 |
| Agent 搜索基础设施 | anysearch-ai/anysearch-skill | 给 AI agent 提供通用搜索、批量搜索、网页抽取 | 可借鉴垂直路由、批量搜索、URL 抽取、多运行时 CLI | 不是科研质量源，但可能成为 agent 默认搜索入口 |
| 传统数据库 | Google Scholar、PubMed、Scopus、Web of Science | 权威检索、机构订阅、领域数据库 | 质量/覆盖/可解释性基准 | 机构用户已有习惯和预算锁定 |

## 3. 能力吸收矩阵

ScanSci Find 的路线应该从“避开竞品长板”改成“吸收竞品长板，但换成可审计科研工作流”。每个优点都要落到明确的产品能力、输出字段或执行模式里。

| 来源 | 必须拥有的优点 | ScanSci Find 的实现形态 | 约束 |
|---|---|---|---|
| Elicit | 证据表、字段抽取、系统综述式筛选 | `evidence_table`、候选级 inclusion/exclusion reason、可导出 Markdown/JSON/CSV | 先保证候选事实可追溯，再让 LLM 写摘要 |
| Consensus | 语义检索 + 关键词检索 + 质量重排 | `quality_ranker` 结合 relevance、source_agreement、journal_quality、recency、citation signals | 不做黑箱答案，所有排序信号要可解释 |
| Undermind | 深度检索、查询澄清、长任务代理 | `deep` mode、scope clarification、后台 fan-out、失败源报告 | 深搜结果必须保留检索路径和失败说明 |
| Scite | 引文语境、support/contradict/mention | `citation_evidence` 可选字段，后续接 Scite/OpenCitations/Semantic Scholar citation contexts | 不把引用语境等同于期刊质量 |
| ResearchRabbit / Litmaps / Connected Papers | collection、图谱发现、prior/derivative works、alerts | `collection`、`followup_queries`、`classic_prior`、`recent_derivative`、`monitor` | 第一阶段可先做数据结构和导出，不急着做重 UI |
| openags/paper-search-mcp | 广源连接器、OA-first 下载回退、平台能力矩阵 | `source_matrix`、`oa_status`、`download_trace`、可选 upstream benchmark | 不能让下载广度盖过 Journal Scout 质量门控 |
| scholar-megasearch | domain routing、source buckets、subagent fan-out、corroboration ranking | `domain_router`、`source_buckets`、`min_sources`、`source_agreement` | 保持 ScanSci Find 的 MCP 工具调用足够轻 |
| Kaggle / Hugging Face / OpenML / Zenodo / DataCite | 数据集、benchmark、数据 DOI、研究对象发现 | `artifact_type`、`research_data` profile、`data_queue.json`、paper-data links | 数据集不能用期刊 IF 判断，需单独质量模型 |
| AnySearch | 垂直路由、批量搜索、URL 抽取、agent search infrastructure | optional upstream，用于 web/context 补充和 URL 内容抽取 | 不进入默认科学源，不替代论文元数据源 |

统一产品公式：

```text
ScanSci Find = broad recall + source agreement + quality gate + retrieval queue + evidence report
```

这句话比“只做高质量论文搜索”更完整：它允许 ScanSci Find 吸收竞品的广度、深度、图谱、数据集和 agent 编排能力，同时把所有能力收束到可信候选集和可复核工件。

## 4. 主要竞品拆解

### Elicit

Elicit 的强项是从检索进入系统综述工作流。其公开价格页显示：免费层可在 1.38 亿篇以上论文中搜索，支持 Zotero 导入、来源可见、论文聊天；Pro/Scale 面向系统综述、报告、抽取列、API、团队协作，企业层强调 PRISMA 级筛选与 4 万篇规模筛选。来源：https://elicit.com/pricing

对 ScanSci Find 的判断：

- 要拥有：表格化证据、筛选理由、候选级字段抽取。
- 实现方式：先输出 `evidence_table` 和 inclusion/exclusion reason，再让 Skill 层决定是否生成综述摘要。
- 保持边界：ScanSci Find 的质量门控来自 Journal Scout 数据与可记录版本，LLM 只能解释和整理，不能替代事实字段。

### Consensus

Consensus 是 AI-powered academic search engine，官方帮助页称其数据库覆盖 2.2 亿以上 peer-reviewed papers，并说明其检索流程是混合语义搜索 + BM25，再按 recency、citation count、journal impact and reputation 重排；它还提供 Research Agent、Pro Analysis、Consensus Meter、Ask Paper、Study Snapshot 等功能。来源：https://help.consensus.app/en/articles/9922673-how-consensus-works

对 ScanSci Find 的判断：

- 要拥有：语义检索、关键词检索、质量重排、简洁的结论性摘要。
- 实现方式：把 `quality_ranker` 写成可解释组件，展示 relevance、source_agreement、journal_quality、recency、citation signals。
- 保持边界：不做黑箱 Consensus Meter；结论必须引用候选 ID、来源和质量证据。

### Undermind

Undermind 的公开页面强调 deep literature search：review thousands of papers、把相关论文带入 project、读取 OA PDF / 上传 PDF、生成 verified citations 的写作输出，并分析 figures。来源：https://app.undermind.ai/

对 ScanSci Find 的判断：

- 要拥有：复杂查询澄清、深度检索模式、长任务进度和失败源报告。
- 实现方式：增加 `deep` mode 和后台 fan-out；先生成高置信候选，再把深读交给 ScanSci PDF 或后续阅读工具。
- 保持边界：深搜不能牺牲可复现性；每个结果都要保留检索路径、失败源、下载状态。

### Scite

Scite 的核心护城河是 Smart Citations。其官网称覆盖 280M+ sources、1.6B+ citations，并能判断后续研究是 support / contradict / mention。来源：https://scite.ai/

对 ScanSci Find 的判断：

- 要拥有：引用语境证据，尤其是 support / contradict / mention 这种“被后续研究如何使用”的信号。
- 实现方式：先预留 `citation_evidence` 字段，后续可接 Scite、OpenCitations、Semantic Scholar citation contexts。
- 保持边界：引用语境是“研究状态证据”，Journal Scout 是“期刊质量证据”，两者要并列展示，不能互相替代。

### ResearchRabbit

ResearchRabbit 面向探索式文献发现：它强调根据用户阅读路径学习，给出更相关推荐，并用 interactive maps 连接 papers、authors、concepts。来源：https://www.researchrabbit.ai/features

对 ScanSci Find 的判断：

- 要拥有：collection、迭代推荐、相邻论文发现。
- 实现方式：先做 `collection`、`followup_queries`、`related_candidates` 数据结构，再决定是否做可视化 UI。
- 保持边界：图谱不是终点；ScanSci Find 需要把发现结果继续转成下载队列、BibTeX 和质量报告。

### Connected Papers

Connected Papers 是视觉化论文发现工具；公开价格页显示免费层每月 5 个 graph，并包含 similarity graphs、prior and derivative works、multi-origin graphs、saved papers、graph history。来源：https://www.connectedpapers.com/pricing

对 ScanSci Find 的判断：

- 要拥有：seed paper 扩展、prior works、derivative works。
- 实现方式：把 `classic_prior`、`recent_derivative`、`similar_methods` 做成每篇候选的后续查询，而不只是一个视觉 graph。
- 保持边界：入口仍应支持 topic/query；seed-paper graph 是模式之一，不是唯一入口。

### Litmaps

Litmaps 的功能页称其 catalogue 有 270M+ papers，并基于 citations / references 找相关论文；它还提供 Zotero sync、advanced discovery、visualize、share、monitor。价格页显示免费层有输入数和 map 限制，Pro 约 $10/month。来源：https://www.litmaps.com/features 与 https://www.litmaps.com/pricing

对 ScanSci Find 的判断：

- 要拥有：Zotero 同步、monitor alerts、基于引用关系的持续发现。
- 实现方式：中期增加 `monitor` profile，定期重跑 query/collection，输出新增高质量候选。
- 保持边界：协作和地图 UI 可以后置；先把“找出高质量论文 -> 进入 ScanSci PDF 下载 -> 生成 refs.bib”做顺。

### openags/paper-search-mcp

openags/paper-search-mcp 是 ScanSci Find 目前最接近的相邻竞品。其 README 定位为 MCP server，用于从多个来源搜索和下载学术论文，并强调 free-first 策略、可选 API key、LLM-friendly retrieval、source transparency。它提供两层架构：高层 `search_papers` 做多源并发搜索与去重，`download_with_fallback` 做开放获取下载回退；底层是 arXiv、PubMed、bioRxiv、Semantic Scholar、Crossref、OpenAlex、PMC、CORE、Europe PMC、DOAJ、BASE、Zenodo、HAL、SSRN、Unpaywall 等平台连接器。来源：https://github.com/openags/paper-search-mcp

GitHub 页面核对时间：2026-06-08。页面显示约 1.7k stars、177 forks、20 issues、25 pull requests。

对 ScanSci Find 的判断：

- 要拥有：广源连接器、平台能力矩阵、OA-first fallback chain、源限制透明化。
- 实现方式：增加 `source_matrix`、`oa_status`、`download_trace`，并把 download fallback 的每一步写进输出工件。
- 保持边界：广源下载是基础设施能力；ScanSci Find 的主轴仍是 Journal Scout 质量门控、JIF/JCR/CAS 证据、质量报告和 ScanSci PDF 队列契约。
- 产品动作：把 `paper-search-mcp` 作为召回/下载广度基准；如果接入，应作为 optional upstream，并保留 ScanSci Find 自己的候选 schema 与质量策略。

### TaewoooPark/scholar-megasearch

scholar-megasearch 是 Claude Code 的大规模多源学术搜索 skill。其 README 称它会把 topic 分解后 fan out 到 20+ scholarly databases，合并成去重、排序、带 provenance 的 corpus，并通过开放获取路径获取 PDF。它强调 subagent fan-out、DOI/arXiv/title 去重、corroboration ranking、domain-aware routing，并把输出落到 `raw/`、`corpus.json`、`corpus.md`、`pdfs/`、`summary.md`。来源：https://github.com/TaewoooPark/scholar-megasearch

GitHub 页面核对时间：2026-06-08。页面显示 12 stars、5 forks、0 issues，最新 release 为 2026-05-29 的 v0.3.1。

对 ScanSci Find 的判断：

- 要拥有：domain routing、source buckets、subagent fan-out、多源交叉验证。
- 实现方式：增加 `domain_router`、`source_buckets`、`depth`、`min_sources`、`source_agreement`；让 broad/deep 模式决定 fan-out 宽度。
- 保持边界：scholar-megasearch 更像深度文献搜集工程；ScanSci Find 仍要保持轻、稳、可嵌入 MCP 工具调用，并用 Journal Scout 做明确质量门控。
- 产品动作：用 `source_agreement` / `min_sources` 回应 corroboration ranking，同时把高质量期刊证据作为排序和解释主轴。

### Semantic Scholar / OpenAlex / Crossref / arXiv

这些更像 ScanSci Find 的上游而不是终端竞品：

- Semantic Scholar API 可查询 papers、authors、citations、venues、SPECTER2 embeddings，并提供 recommendations 与 datasets。来源：https://www.semanticscholar.org/product/api
- OpenAlex 是 fully open catalog of the global research system，含 works、authors、sources、institutions、topics、publishers、funders 等实体，并提供 API 与数据快照。来源：https://developers.openalex.org/
- Crossref REST API 暴露成员与可信来源沉积的 scholarly metadata，支持 works、journals、members、funders、licenses 等端点。来源：https://www.crossref.org/documentation/retrieve-metadata/rest-api/
- arXiv 是预印本源，适合作为“快速前沿”补充，但不应直接通过期刊质量门控判断。

策略：这些源决定召回面；Journal Scout 决定质量证据；ScanSci Find 的价值在于统一字段、去重、排序、可解释输出。

### Kaggle / Hugging Face / OpenML / Zenodo / DataCite

这组不是论文搜索竞品，而是“研究数据与研究对象发现源”。如果 ScanSci Find 只找 paper，会在机器学习、数据科学、开放科学、可复现实验场景里缺一块。

- Kaggle：官方 Kaggle API/CLI 支持 datasets list/download/create/update 等数据集操作，Kaggle 数据集元数据遵循 Data Package 风格，并包含 license、resources、schema、keywords 等字段。来源：https://www.kaggle.com/docs/api 与 https://github.com/Kaggle/kaggle-api/wiki/Dataset-Metadata
- Hugging Face Datasets：Hub 托管大量 community-curated datasets，覆盖 translation、ASR、image classification 等任务；每个 dataset 是 Git repository，可通过 search bar、main datasets page 以及 `huggingface_hub` 的 `list_datasets()` 搜索。来源：https://huggingface.co/docs/hub/en/datasets-overview 与 https://huggingface.co/docs/huggingface_hub/guides/search
- OpenML：围绕 datasets、tasks、flows、runs 和 benchmarks 组织机器学习实验，tasks 定义可复现实验设置与 train/test splits，适合模型 benchmark 发现。来源：https://docs.openml.org/
- Zenodo：REST API 支持 published records 搜索、files 下载/上传、deposit 发布研究输出；记录类型覆盖 publication、dataset、software、poster、presentation 等。来源：https://developers.zenodo.org/
- DataCite：REST API 用于检索、创建、更新 DataCite DOI metadata records，`/dois` 可返回 DOI 列表，覆盖 datasets、text documents 等研究对象。来源：https://support.datacite.org/docs/api

对 ScanSci Find 的判断：

- 不应把这些混进默认 paper 排序：dataset 的质量标准不是 JIF，不能用 Journal Scout 直接判定。
- 应增加新对象类型：`artifact_type = paper | dataset | software | benchmark | record`，并把 DOI、license、file availability、schema、version、citation、related paper 作为数据集质量证据。
- 可差异化：做“论文-数据集闭环”。例如论文候选旁边标出 associated dataset DOI / Zenodo record / Hugging Face dataset / OpenML task / Kaggle dataset，并输出可下载的数据候选队列。
- 产品动作：新增 `research_data` profile，默认仍以 paper 为主；当 query 明确包含 dataset、benchmark、replication、code、model training、OpenML task 等意图时再启用数据源。

## 5. AnySearch 的特殊定位

anysearch-ai/anysearch-skill 是相邻竞品，不是科研搜索直接竞品。它的 README 定位是 “Unified real-time search engine skill for AI agents”，支持 general web search、vertical domain search、parallel batch search、full-page content extraction。官网定位是 AI Search Infrastructure for Agents。来源：https://github.com/anysearch-ai/anysearch-skill 与 https://www.anysearch.com/

GitHub API 核对时间：2026-06-08。`anysearch-ai/anysearch-skill` 当时为 2671 stars、190 forks、3 open issues，`pushed_at` 为 `2026-06-03T04:16:40Z`。

对 ScanSci Find 的判断：

- AnySearch 是 AI agent 搜索基础设施，不是科研搜索竞品。
- 可以借鉴：vertical_domain_routing、batch_search、url_content_extraction、multi_runtime_cli。
- 不应默认接入：它依赖外部 API，不提供本地 Journal Scout 质量库，也不负责论文元数据规范化和期刊质量门控。
- 在本项目中应作为 `optional_upstreams`，而不是 `DEFAULT_SOURCES`。

## 6. ScanSci Find 护城河

1. 质量门控是第一特征，不是搜索后的附属标签  
   大多数工具把 journal impact 当排序信号或过滤器；ScanSci Find 可以把 Journal Scout 证据、数据版本、匹配原因和未通过原因作为主输出。

2. 和 ScanSci PDF 的下载闭环  
   竞品多止步于“发现/综述/收藏”。ScanSci Find 可以输出 `download_queue.json`，直接进入下载与全文处理工作流。

3. Agent-native 但 science-specific  
   AnySearch 是通用搜索，Elicit/Consensus 是终端应用；ScanSci Find 可以做成专门服务科研 agent 的 MCP 能力层。

4. 可审计、可测试、可复现  
   候选标准化、去重、质量报告、BibTeX、数据 sha256 都适合严肃科研自动化。

## 7. 当前短板

- 没有 UI 或图谱探索体验，吸引力弱于 ResearchRabbit / Litmaps。
- 没有 AI 综述/抽取表格，感知价值弱于 Elicit / Consensus。
- 没有全文阅读与 figure 分析，深读能力弱于 Undermind。
- 质量门控依赖 Journal Scout 可用性；若 Journal Scout 数据缺失，产品价值会下降。
- 默认源仍偏元数据召回，对灰色文献、中文文献、机构订阅全文覆盖不足。

## 8. 推荐路线

### 近期：先拥有竞品级基础能力

- 增加 quality explanation：每篇论文展示通过/未通过、Journal Scout 匹配项、JIF 年份、JCR/CAS、数据版本。
- 增加 source agreement：展示 OpenAlex/Crossref/Semantic/arXiv 的命中重叠，重叠越多可信度越高。
- 增加 query profiles：`fast_broad`、`high_quality_broad`、`frontier_preprint`、`review_seed`。
- 增加 evidence table：吸收 Elicit 的表格化证据输出，但每个字段必须有来源。
- 增加 quality ranker：吸收 Consensus 的质量重排，把排序信号展开给用户看。
- 增加 OA/download trace：吸收 paper-search-mcp 的下载回退透明度，优先补齐平台限制说明与 OA-first 下载状态。
- 增加 source buckets：吸收 scholar-megasearch 的 source bucket 思路，但先不做重型 subagent 编排。
- 保持 AnySearch optional：吸收其 vertical routing、batch search、URL extraction，但不让它进入默认科学源。

### 中期：拥有发现、监控、数据集闭环

- 对每篇候选生成 `classic_prior`、`recent_derivative`、`similar_methods` 三类后续查询。
- 增加 Zotero / RIS / BibTeX 互操作。
- 增加 alerts 的最小版本：定期重跑查询，输出新增高质量候选。
- 增加 `research_data` profile：只在用户明确找 dataset、benchmark、replication data、training data 时启用 Kaggle、Hugging Face、OpenML、Zenodo、DataCite。
- 增加 paper -> data links：把论文 DOI 与 DataCite/Zenodo/Hugging Face/OpenML/Kaggle 记录关联，输出 `data_queue.json` 或扩展 `download_queue.json`。
- 增加 collection：吸收 ResearchRabbit / Litmaps 的收藏与迭代发现，但先以 JSON/Markdown 工件呈现。

### 远期：拥有深搜、引用语境、证据报告

- 先输出可审计 evidence table，再让 LLM 写摘要。
- 摘要必须引用候选 ID 与来源字段。
- 不把模型生成内容混入候选事实字段。
- 建立 research object 质量模型：论文走 Journal Scout，数据集走 license、version、schema、file availability、citation、maintainer、benchmark usage、related_identifier。
- 增加 citation evidence：吸收 Scite 的引用语境，区分 support、contradict、mention。
- 增加 deep mode：吸收 Undermind / scholar-megasearch 的深搜体验，但所有 subtask、source failure、download failure 都要进入报告。

## 9. 产品能力总纲

ScanSci Find 最终应具备四层能力：

1. 召回层：OpenAlex、Crossref、Semantic Scholar、arXiv、PubMed/PMC、OpenAIRE/CORE/DOAJ、Kaggle/Hugging Face/OpenML/Zenodo/DataCite 等来源按 domain routing 启用。
2. 验证层：source agreement、DOI/arXiv/title 去重、Journal Scout 期刊质量、OA/download trace、citation evidence、research object quality。
3. 工件层：`candidates.json`、`papers.md`、`quality_report.json`、`download_queue.json`、`data_queue.json`、`refs.bib`、`evidence_table.csv`。
4. 编排层：MCP 工具、CLI、Skill、query profiles、deep mode、monitor mode、optional upstreams。

产品原则：

- 竞品有的强体验，ScanSci Find 要有对应能力。
- 每个能力都必须落到可审计字段、报告或队列。
- 不让 LLM 生成内容污染事实字段。
- 不用单一质量分数掩盖不同证据类型：期刊质量、引用语境、数据集质量、下载可得性要分开解释。
- 默认路径保持轻，deep/research_data/monitor 作为显式 profile。

## 10. 产品话术

建议主文案：

> Find trusted science, quality-gated by Journal Scout, downloadable by ScanSci PDF.

中文版本：

> 找到值得下载、值得阅读、值得引用的科研论文候选集。

不要主打：

- “AI 自动写综述”
- “比 Google Scholar 更全”
- “一键生成论文”

应该主打：

- 多源召回
- Journal Scout 质量门控
- 证据可解释
- ScanSci PDF-ready
- MCP / CLI / Skill 可接入

## 11. 2026-08 补充调研与架构决策

本轮补充核验了以下 agent-native 学术工作流：

- Cangjie Skill: https://github.com/kangarooking/cangjie-skill
- lit-search / research-skills: https://github.com/luwill/research-skills
- Academic Research Skills: https://github.com/Imbad0202/academic-research-skills
- ARS-Codex: https://github.com/Imbad0202/academic-research-skills-codex
- paper-search-pro: https://github.com/O0000-code/paper-search-pro
- scholar-kit: https://github.com/lottshin/scholar-kit
- paper-search-mcp: https://github.com/openags/paper-search-mcp
- Oh My Paper: https://github.com/LigphiDonk/Oh-my--paper
- cookjohn 学术源适配器生态: https://github.com/cookjohn
- scientific-skills: https://github.com/yorkeccak/scientific-skills
- scholar-deep-research: https://github.com/Agents365-ai/scholar-deep-research

### 用户指定微信文章：`/lit-search，专用于文献检索的科研skill`

原文：https://mp.weixin.qq.com/s/CjATBJ7z6JRbdD4AtDAigg

核验时间：2026-08-05。文章署名鲁工，发布于 2026-08-03，页面标注修改于 2026-08-04。以下数字均为作者披露的实践记录，不作为独立性能基准：

- 主干检索源为 OpenAlex、PubMed、Europe PMC、arXiv；CVF、OpenReview、Zenodo 用作顶会与灰色文献补充；Crossref 只做 metadata enrich，不算独立检索源。
- 先将主题拆成 3–5 个概念块，并准备 5–10 篇 gold papers；先展开检索式和估算量级，再冻结协议。
- 正式执行前先用 4 条记录检查 API 契约，再用 100 条校准人工队列；作者建议人工队列超过 15% 时暂停并修改标准。
- 强制“先筛选、再滚雪球”，并让筛选与引文扩展交替进行。作者给出的一个饱和案例三轮新增纳入比例为 34.7%、4.1%、0.4%，但这只是单次运行案例。
- `dois.md`、`references.md`、`PRISMA.md`、`coverage_report.md` 是核心交付物；PRISMA 计数不等于系统综述已经完成。
- 缺少期刊指标不能直接等同于低质量，质量分层应优先用于标注与排序，不应自动删除记录。
- 作者明确说明 lit-search 当前针对医学 AI，其他领域需要领域适配。

对 ScanSci Find 的直接影响：保留这套检索工程和诚实报告机制，但将 source routing、question framework、质量证据和对象类型抽象为通用学科协议。医学成为 `medicine` / `life_sciences` / `public_health` profile，而不是默认产品身份。ScanSci Find 还需比原流程更严格地区分“source registered”“adapter executable”“credential available”“source actually consulted”四种状态。

### Cangjie Skill

Cangjie 不是文献检索竞品。它的价值在于来源蒸馏、证据定位、边界描述、反例和压力测试。ScanSci Find 吸收的是工程方法：每个 source/domain workflow 都要有证据、边界、失败模式和测试，不复制其内容蒸馏定位。

### lit-search

lit-search 对 ScanSci Find 的直接影响最大。应吸收：检索协议先行、3–5 个概念块、gold set、完整分页、多源独特贡献、初筛后的前后向引用扩展、饱和曲线、PRISMA、人工队列，以及明确写出未执行步骤的 coverage report。

它原本偏医学 AI；ScanSci Find 把方法抽象为通用协议。PubMed、Europe PMC、PICO、PECO、ClinicalTrials.gov 等只属于医学/生命科学 profile。

### Academic Research Skills 与 ARS-Codex

ARS 的强项是从研究问题到写作、审稿、修订的完整性门禁，以及 Material Passport、引用核验、人类检查点和 claim-level provenance。ScanSci Find 不复制整个写作流水线，而是为上层 ARS/写作 agent 提供可验证候选、来源状态、全文读取范围和审计工件。

### paper-search-pro 与 paper-search-mcp

paper-search-pro 提供分层检索、多源路由、去重、引用追踪和 PRISMA-S 思路；paper-search-mcp 提供开放源连接器池和 OA-first fallback。ScanSci Find 分别吸收“协议”和“连接器能力矩阵”，但保持自身候选 schema、Journal Scout 边界及 ScanSci PDF 队列。

### scholar-kit 与 cookjohn 生态

这些项目证明中文与机构数据库必须是一等适配器，但不能伪装成开放 API。ScanSci Find 的源目录把 CNKI、NSSD、Wanfang、CQVIP、Google Scholar、WoS、Scopus、ScienceDirect、IEEE、ACM 和 JSTOR 标为条件源；只有 runtime source status 能证明本轮实际访问。

### Oh My Paper

Oh My Paper 的角色隔离、项目记忆和研究流水线适合上层研究 harness。ScanSci Find 保持能力层边界，把 protocol、manifest 和工件写入磁盘，供外部 conductor、literature scout、writer 或 reviewer 按需读取。

### scientific-skills

生物医学、临床试验、药物和专利源作为领域插件有价值，但不能定义产品身份。ScanSci Find 的默认 `general` profile 不含 PubMed/Europe PMC；`medicine`、`life_sciences` 和 `public_health` profile 才启用医学源和可选医学框架。

### 社区反馈转化

X 上的项目传播信号用于判断需求和可理解性，不用于判断技术性能。Reddit 反馈集中在假 DOI、失效链接、私有机构数据库、本地模型接入、上下文成本和缺少明确检索标准。对应产品要求为：

- canonical identifier verification；
- source-local provenance；
- browser/credential isolation；
- discovery-first、full-text-later；
- criteria and gold set before high-recall retrieval；
- explicit human queue；
- coverage and limitations instead of confident completeness claims。

可复核的社区样本（均为经验性反馈，不当作性能测评）：

- Reddit 的 LitReviewSkill 作者强调 seed papers、前后向引文扩展、筛选和迭代，而不是一次浅搜索：https://www.reddit.com/r/AIToolBench/comments/1su9rqu/i_built_a_agent_skill_for_academic_literature/
- reproducibility 讨论主张把抓取、DOI/标题去重、引文追踪和导出做成确定性步骤，LLM 只辅助人工筛选；回复同时质疑“systematic”覆盖声明是否充分：https://www.reddit.com/r/academicpublishing/comments/1uh3aen/looking_for_feedback_on_an_opensource_literature/
- 教师、审稿人与图书馆员集中报告伪造 DOI、真实 DOI 与错误元数据配对、以及必须独立核验的问题：https://www.reddit.com/r/academia/comments/1rdjj1m/rejected_another_paper_for_fabricated_dois_why/ 、https://www.reddit.com/r/Professors/comments/1st5mq3/i_tested_chatgpt_claude_and_gemini_on_academic/ 、https://www.reddit.com/r/librarians/comments/1smk89z/how_are_we_dealing_with_fake_citations/
- X 上的 agent-skill 讨论强调技能应积累 gotchas、保留执行日志并可组合；autoresearch 讨论则区分 optimization、reflection 和持续运行三类循环。它们支持“可迭代协议 + 可审计状态”，但不能证明某个学术检索器更准：https://x.com/NickSpisak_/status/2033974734723887333 、https://x.com/ZechenZhang5/status/2034008586293321991

## 12. v0.2 竞争策略结论

ScanSci Find 不再用“高 IF 搜索”定义自己。新的产品公式是：

```text
ScanSci Find = protocol + federated discovery + identity/provenance
             + conservative dedupe + multidimensional evidence
             + citation closure + measurable coverage
             + PDF/Zotero/research-agent handoff
```

Journal Scout 仍是重要差异化能力，但只占多维证据中的 venue 维度。默认体验面向所有学科，医学兼容但不强调医学。

## 13. v0.3 落地审计

本轮不是按竞品名称拼接功能，而是把竞品分析中的共同长板压缩成一条可执行、可审计的检索管线。

| 竞品长板 | v0.3 落地 | 状态与边界 |
|---|---|---|
| lit-search 的协议先行与高召回门禁 | `plan_search` → `estimate_search` → 4 条 `smoke_search` → 100 条 `calibrate_search` → 正式检索 | 已实现；校准会检查来源失败、候选契约、人工队列比例和独立 gold set |
| 多源深检与完整性证据 | OpenAlex cursor、Semantic Scholar offset 的真实预算内分页；保留来源总量、游标和 `pagination_complete` | 已实现；仍只对原生适配器声明完成度，不替条件源代报成功 |
| ResearchRabbit/Litmaps 式引文扩展 | Semantic Scholar + OpenCitations Index v2/Meta，可单源或双源，逐轮报告新颖度、饱和与部分失败 | 已实现基础图扩展；尚未提供交互式图谱、提醒或 collection UI |
| Reddit 社区最关心的假 DOI 防线 | DOI→Crossref、PMID→PubMed、arXiv→arXiv 元数据核验，分离 `verified`、`metadata_mismatch`、`not_found`、限流和网络失败 | 已实现；标识符存在不再自动等于已核验 |
| paper-search-mcp 的 OA-first 支持 | Unpaywall v2 解析 OA 状态、PDF/落地页、license、version 和 host type，且不覆盖已有 PDF 链接 | 已实现；需要责任邮箱，不绕过付费墙或登录 |
| Elicit/ARS 的证据与人工检查点 | `evidence_table.csv`、`human_queue.csv`、dedupe clusters、coverage、PRISMA、Zotero/BibTeX、验证/OA 工件 | 已实现候选级证据；claim-level 事实抽取与全文证据护照仍属于后续阅读/写作层 |
| 通用学科路由 | 默认 `general`，医学、生命科学、计算机、社科、人文、中文、研究数据等作为 profile | 已实现；医学兼容但不定义产品身份 |

因此，“按竞品分析构建”在 v0.3 的准确说法是：核心检索方法与可信性门禁已经落地，交互图谱、持续监控、claim-level 引文语境、更多机构数据库原生适配器和语义向量重排仍是明确的后续边界，不能假装已经完成。
