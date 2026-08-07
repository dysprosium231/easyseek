# ScanSci Find — 领域无关、可审计的多源学术发现引擎

> Domain-neutral, auditable, multi-source academic discovery for ScanSci.

ScanSci Find 是 ScanSci 的学术发现层：把"找文献"当作工程来做。它跨源检索并归一化学术记录、如实记录哪些源被咨询过而哪些没有、把期刊级证据与文章有效性严格分开，并把验证过的标识符交给 ScanSci PDF 与 Zotero 工作流。检索协议先行、召回可测量、每个结论都落成可复核的工件。

ScanSci Find is the academic discovery layer of ScanSci: it treats literature search as engineering. It searches and normalizes scholarly records across many sources, records what was and was not consulted, keeps journal-level evidence separate from article validity, and hands verified identifiers to ScanSci PDF and Zotero workflows. Protocols come first, recall is measurable, and every claim lands as an auditable artifact.

## 产品边界 / Product boundaries

- **MCP** 是能力层 / the capability layer。
- **Skill** 是认知编排层 / the cognitive orchestration layer。
- **CLI** 是可复现的人工与测试入口 / the reproducible human and test entrypoint。
- **Journal Scout** 提供期刊级证据，但**不**判定单篇文章是否有效 / supplies venue-level evidence; it does not determine whether an individual article is valid。
- **ScanSci PDF** 负责合法全文获取；ScanSci Find 只产出队列与访问证据 / handles lawful full-text retrieval; ScanSci Find emits queues and access evidence。
- 浏览器与机构源始终是显式适配器。ScanSci Find 不绕过登录、验证码、订阅或出版商管控 / Browser-backed and institutional sources remain explicit adapters. ScanSci Find does not bypass login, captcha, subscriptions, or publisher controls.

医学通过可选 domain profile 支持：默认身份与查询模型是一般学术研究，PICO、PubMed、Europe PMC 与临床试验源只在任务需要时激活。

Medicine is supported through an optional domain profile. The default identity and query model are general academic research; PICO, PubMed, Europe PMC, and clinical-trial sources are activated only when the task calls for them.

## 一分钟开始 / Quick Start

```powershell
python -m pip install -e .          # Python 3.11+，核心零依赖 / core has zero mandatory deps
scansci-find search "urban heat island" --depth standard --verify-identifiers --resolve-oa --find-preprints --out runs/heat
scansci-find explore "diffusion models" --domain medicine --limit 30    # 两遍交互：先出摘要表
scansci-find deep-fetch runs/explore.json --out runs/explore-deep.json # 确认核心论文后深拉
scansci-find benchmark "urban heat island" --sample-size 100 --out runs/bench   # 可复现的覆盖率基准
```

## 检索流水线 / The Pipeline

```text
question -> protocol -> volume estimate -> 4-record smoke test
         -> 100-record calibration -> budgeted paginated retrieval
         -> normalization/deduplication -> screening -> citation chasing
         -> identifier/OA verification -> coverage/PRISMA -> PDF/Zotero handoff
```

协议把旧式检索工具常混淆的四件事严格分开 / The protocol separates four concepts that older search tools often blur:

1. 源被注册 ≠ 在当前机器可执行 / a source can be registered without being executable。
2. 源可查询 ≠ 提供全文 / a source can be queried without providing full text。
3. 期刊证据 ≠ 文章级证据 / journal evidence is not article-level evidence。
4. 分页、源覆盖、金标准与引文闭包全部完成，才谈得上 systematic / a run is not systematic unless pagination, planned-source coverage, gold-set checks, and citation closure are actually complete。

## 能做什么 / Capabilities

### 检索与路由 / Search & routing

| 能力 | 说明（中 / EN） |
|---|---|
| 13 源联邦 | OpenAlex / Crossref / Semantic Scholar / arXiv / DBLP / PubMed / Europe PMC / Zenodo / DataCite / OpenML / Hugging Face / Kaggle / 百度学术 / CNKI，按 domain 路由 / federated with domain routing |
| CDP 浏览器源 | Google Scholar 与 CNKI 驱动用户自己的 Chrome（远程调试），登录态自动携带、无凭证处理；`pip install scansci-find[cdp]` / drive your own Chrome for Scholar & CNKI, login state without credentials |
| query 扩展 | 内置缩写-全称双向对与学科同义词，纯函数、协议指纹稳定；`SCANSCI_FIND_VOCAB_DIR` 可加自定义词表 / deterministic expansion, stable protocol ids, user vocab supported |
| 排序 | `--sort relevance\|recency\|citations`；recency 把近 6 个月文献标 `[新]` 置顶 / recency-first with a `[新]` flag |
| 中文路由 | `--domain chinese_general --cn`，CNKI / 百度学术 / Wanfang / CQVIP / NSSD / Chinese explicit routing |

### 增强 / Enrichment

- **预印本匹配 / preprint matching**：付费墙论文按"标题相似 + 作者或年份"保守匹配 arXiv 与 Europe PMC PPR（bioRxiv / medRxiv / SSRN / Research Square）的开放版本，只增不改 / finds lawful open copies of paywalled papers, never mutates identity。
- **代码补全 / code links**：Papers with Code 免 key 补全代码仓库（官方优先、按 star 排序）/ official-first repository metadata。
- **OA 解析 / OA resolution**：聚合候选自带的 OpenAlex / Semantic Scholar / Europe PMC 链接后再消耗 Unpaywall 配额，并发解析 / multi-resolver aggregation before Unpaywall quota。
- **标识符验证 / verification**：DOI→Crossref、PMID→PubMed、arXiv→arXiv 交叉验证，区分 verified / partial / mismatch / not_found。
- **引文闭包 / citation chasing**：Semantic Scholar + OpenCitations 双向扩展，连续两轮 novelty 低于阈值才算饱和 / consecutive-round saturation。

### 交互 / Interaction

- **explore**（两遍策略第一遍）：quick 检索 → 轻量摘要表（标题/年份/Venue/引用数/PDF 提示/`[新]`），不拉摘要 / pass 1: lightweight summary table。
- **deep-fetch**（第二遍）：对确认的核心论文跑 验证 + OA + 预印本 + 代码 + BibTeX / pass 2: full enrichment on the confirmed subset。

### 测量与审计 / Measurement & audit

- **Chapman 捕获-再捕获**：PubMed∩OpenAlex 重叠估算文献总量与 95% CI，进 coverage report / population estimation from two-source overlap。
- **PRISMA 拒渲染**：计数不自洽时拒绝出 PRISMA.md，改写 `prisma_inconsistency.md` / refuses to render inconsistent counts。
- **`benchmark` 命令**：按 DOI 前缀分类出版商，实测各源摘要覆盖率——可复现的测量，而非一次性声明 / reproducible per-source & per-publisher coverage measurements。
- **金标准窗口召回**：`found_in_window` / `found_out_of_window` / `found_undated` 分桶 / window-bucketed gold-set recall。

### 产物与闭环 / Artifacts & closed loop

`candidates.json`、`download_queue.json`、`oa_manifest.json`（open_pdf 直接下载 / needs_institution 走机构阶段的路由清单）、`coverage_report`、`PRISMA.md`、`benchmark_report`、`preprint_report.json`、`code_report.json` 等。

与 ScanSci PDF 形成闭环 / Closed loop with ScanSci PDF:

```powershell
scansci-pdf manifest runs/x/oa_manifest.json --output runs/x/pdfs   # 按 manifest 路由下载
scansci-pdf batch queue.txt --scihub --runs-dir runs/x              # 队列 + 预印本兜底（付费墙失败自动用 arXiv 版重试）
scansci-find reconcile runs/x                                       # 下载结果回写候选：downloaded / anti_bot_blocked / html_not_pdf
```

## 命令速查 / CLI reference

| 命令 | 用途 / Purpose |
|---|---|
| `scansci-find plan / estimate / smoke / calibrate` | 协议先行：构建检索协议、预估量级、4 条冒烟契约校验、100 条校准（人工队列 >15% 即停）/ protocol → estimate → smoke → calibrate gates |
| `scansci-find search` | 全量检索 + 审计产物 / full search with audit artifacts（`--expand-citations --verify-identifiers --resolve-oa --find-preprints --code-links --sort`）|
| `scansci-find explore / deep-fetch` | 两遍交互 / two-pass interaction |
| `scansci-find verify / resolve-oa / preprints / codes` | 对已有候选文件单独跑验证/OA/预印本/代码补全 / standalone enrichment on candidate files |
| `scansci-find benchmark` | 可复现覆盖率基准 / reproducible coverage benchmark |
| `scansci-find reconcile <runs-dir>` | 把 ScanSci PDF 下载结果回写候选 / write download outcomes back |
| `scansci-find browser-doctor / sources` | 浏览器运行时探测 / 源目录 / browser runtime & source registry |

## 深度与领域 / Depth & domains

| 深度 | 用途 / Use | 每源上限 / Ceiling | 引文轮数 / Rounds | 结论边界 / Claim |
|---|---:|---:|---|
| `quick` | 方向感与种子发现 / orientation | 20 | 0 | bounded search |
| `standard` | 常规综述 / normal review | 100 | 1 计划 | 闭包完成前保持 bounded |
| `systematic` | 高召回协议 / high-recall | 500 | 至多 3 | 无审计证据绝不称 complete |

领域 profile：`general`（默认）、`interdisciplinary`、`computer_science`、`engineering`、`natural_sciences`、`mathematics`、`physics_astronomy`、`chemistry_materials`、`earth_sciences`、`agriculture`、`medicine`、`life_sciences`、`public_health`、`social_sciences`、`education`、`psychology`、`law`、`humanities`、`economics`、`environmental_science`、`chinese_general`、`research_data`。PICO/PECO、SPIDER/PICo 等是可选模板，不是默认前提。

## MCP 工具 / MCP tools

新工作流 / New workflows：`plan_search`、`estimate_search`、`smoke_search`、`calibrate_search`、`search_academic`、`expand_citations`、`verify_identifiers`、`resolve_open_access`、`find_preprints`、`enrich_code_links`、`explore`、`deep_fetch`。

v0.1 兼容工具 / Legacy tools：`health_check`、`list_sources`、`search_science`、`screen_candidates`、`explain_candidate`、`build_download_queue`、`browser_doctor`。

## 配置 / Configuration

把 `.env.example` 的值复制到自己的环境或本地忽略文件。绝不提交 API key、机构凭证、cookie 或浏览器 profile。

- `OPENALEX_API_KEY`：OpenAlex 自 2026-02-13 起每个请求都需要免费 key；缺失时该源报告 `blocked_configuration`，其余源继续。
- `UNPAYWALL_EMAIL` 或 `SCANSCI_FIND_CONTACT_EMAIL`：Unpaywall 解析必需；联系邮箱用于负责任的 API 识别。
- 并发：源循环与验证默认 8 worker（`SCANSCI_FIND_SEARCH_WORKERS`），Unpaywall 并发 `SCANSCI_FIND_OA_WORKERS`；设为 `1` 强制串行。引文扩展保持串行（OpenCitations 限速器为实例状态）。
- `SCANSCI_FIND_VOCAB_DIR`：自定义 query 扩展词表（`{"pairs": {...}, "synonyms": {...}}` JSON）。
- CDP 源（Google Scholar / CNKI）需要 `pip install scansci-find[cdp]` 与开启远程调试的 Chrome（`chrome://inspect/#remote-debugging`）；否则优雅降级为 `blocked_configuration`。`scansci-find browser-doctor` 会报告 `cdp_chrome` 候选。
- CNKI 兼容既有变量：

```powershell
$env:SCANSCI_FIND_CNKI_MCP_COMMAND='["uvx","--from","git+https://github.com/h-lu/cnki-mcp","cnki-mcp"]'
```

## 合规边界 / Compliance

- 不绕过付费墙、验证码、登录、机构访问或出版商管控 / no paywall, captcha, login, or publisher-control bypass。
- CDP 源驱动用户自己的 Chrome，不接触任何凭证；遇 CAPTCHA 即停，单会话有检索预算 / CDP drives your own Chrome, stops on CAPTCHA, bounded per-session budget。
- JCR / CCF / 中科院分区等商业或版权数据不内置，由用户自行提供 / commercially licensed ranking data is never bundled。
- 不下载：全文获取交给 ScanSci PDF，本层只产出队列与访问证据 / this layer never downloads; ScanSci PDF does.

## 兼容性 / Compatibility

既有 `scansci-find search`、`search_science`、候选字段、Journal Scout 策略与 ScanSci PDF 队列全部保留。参见 `docs/migration-v0.2.md`（领域中立基础）与 `docs/migration-v0.3.md`（分阶段检索、引文、验证、OA）。

## 致谢 / Acknowledgements

本项目的检索协议、测量机制与浏览器源设计受两个开源项目启发：

The retrieval protocol, measurement machinery, and browser-source designs in this project were informed by two open-source projects:

- [lit-search](https://github.com/luwill/research-skills) — 协议先行的查全检索、金标准召回、饱和判据与 PRISMA 诚实；其记录在案的覆盖率测量促成了我们可复现的 `benchmark` 命令 / protocol-first high-recall retrieval with gold-set recall, saturation criteria, and PRISMA honesty; its documented coverage measurements motivated our reproducible `benchmark` command。
- [Academic-Search](https://github.com/ustc-ai4science/academic-search) — 复用用户自己 Chrome 登录态的 CDP 方案、两遍 explore/deep-fetch 流程与全文状态分类 / CDP-driven reuse of the user's own Chrome login state, the two-pass explore/deep-fetch flow, and the full-text status taxonomy。

两者均为 MIT 许可；本项目在自己的引擎里重实现并扩展了这些思路，而非内嵌它们的代码。

Both are MIT-licensed; this project re-implements and extends those ideas in its own engine rather than embedding their code.

## 许可 / License

MIT
