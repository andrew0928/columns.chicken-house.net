---
layout: synthesis
title: "從 Prompt 到 Product"
synthesis_type: solution
source_post: /2025/06/28/from-prompt-to-product/
redirect_from:
  - /2025/06/28/from-prompt-to-product/solution/
postid: 2025-06-28-from-prompt-to-product
---
以下案例以「從 Prompt 到 Product」主題與文中 Q&A 所涉及的核心難題為主軸，提煉並延展為可落地的實戰型問題解決案例。每個案例都包含問題、根因、方案、程式碼、實測數據與教學練習，適合教學、專案演練與評估使用。

注意：實測數據為企業內常見導入專案的可參考區間與樣例，供教學模擬與評量之用。


## Case #1: 建立 AI 導入的量化評估框架（ROI 與效益儀表板）

### Problem Statement（問題陳述）
**業務場景**：公司計畫導入 AI 於客服工單自動分類與回覆建議，但管理層擔心投資報酬率不明，無法量化節省人力與提升顧客滿意度的效益。需要一套可追蹤、可審計、可對比的量化指標與決策機制，支撐持續投資與擴大試點。
**技術挑戰**：缺乏基準線資料、事件追蹤不一致、無自動化評估與 A/B 實驗能力。
**影響範圍**：預算審核、產品路線、跨部門協作效率、AI 導入速度。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 事件追蹤缺失：前後端未統一事件模式，導致數據不可比。
2. 無實驗框架：缺 A/B 或灰度發佈，難以區分模型效果與外部變因。
3. 欠缺效益模型：未將節省時間、轉單率、CSAT 轉為貨幣價值。

**深層原因**：
- 架構層面：觀測性與資料管線未設計為一等公民。
- 技術層面：缺資料倉儲、ETL/ELT 與可重現的評估作業。
- 流程層面：目標管理未對齊 North Star Metric 及對應的子指標。

### Solution Design（解決方案設計）
**解決策略**：建立「指標樹 + 事件模式 + 實驗框架 + ROI 模型 + 儀表板」的一體化方案。先定義 North Star（例如成功自動解決率），再自頂向下拆解可觀測事件與資料欄位，導入 A/B 與灰度釋出，將時間節省、轉化提升與基礎設施成本換算為淨效益。

**實施步驟**：
1. 指標樹設計與基準線蒐集
- 實作細節：定義 NSM、子指標（FRT、CSAT、Deflection Rate、人工干預率）
- 所需資源：產品/營運/資料分析三方工作坊、Notion/Confluence
- 預估時間：1-2 週

2. 事件模式與資料管線
- 實作細節：定義事件結構（schema）、追蹤 SDK、打通 DWH
- 所需資源：Segment/GA4、dbt、BigQuery/Snowflake/ClickHouse
- 預估時間：2-3 週

3. 實驗框架與灰度釋出
- 實作細節：A/B assignment、變體旗標、離線/線上評估指標
- 所需資源：LaunchDarkly/Unleash、Experimentation SDK
- 預估時間：1-2 週

4. ROI 模型與儀表板
- 實作細節：將節省工時、提升轉化、基礎設施費用換算為淨現金流
- 所需資源：Metabase/Looker/Grafana、Python/SQL
- 預估時間：1 週

**關鍵程式碼/設定**：
```sql
-- 基準線與實驗變體的 ROI 匯總（示例）
WITH base AS (
  SELECT
    variant,
    COUNTIF(resolved_by_ai = TRUE) AS ai_resolved,
    COUNT(*) AS tickets,
    AVG(human_minutes) AS avg_human_mins,
    AVG(ai_inference_cost_usd) AS avg_cost
  FROM support_events
  WHERE event_date BETWEEN '2025-05-01' AND '2025-05-31'
  GROUP BY variant
)
SELECT
  variant,
  ai_resolved / tickets AS deflection_rate,
  (avg_human_mins_base - avg_human_mins) * labor_cost_per_min AS labor_saving_usd,
  ai_resolved * avg_cost AS inference_cost_usd,
  (labor_saving_usd - inference_cost_usd) AS net_roi_usd
FROM base
JOIN (SELECT AVG(human_minutes) AS avg_human_mins_base FROM support_events WHERE variant='control') c;
-- Implementation Example（實作範例）
```

實際案例：客服 AI 自動建議回覆 + 智能分流試點
實作環境：BigQuery + dbt Core + Metabase；Experiment: Unleash；SDK: TypeScript/Node 20
實測數據：
- 改善前：平均首次回覆（FRT）12 小時；AI 解決率 0%；人工作答每單 18 分鐘
- 改善後：FRT 2 小時；AI 解決率 28%；人工作答每單降至 10 分鐘；推估淨 ROI +$15K/月
- 改善幅度：FRT -83%；人工作答時間 -44%；AI 解決率 +28pp

Learning Points（學習要點）
核心知識點：
- 指標樹與 NSM 拆解法
- 事件模式化與數據可觀測性
- A/B 實驗與 ROI 模型建構

技能要求：
- 必備技能：SQL/ETL、事件追蹤、儀表板
- 進階技能：效益貨幣化、統計實驗設計

延伸思考：
- 可用於行銷轉化、內部自動化、人資流程 AI 化
- 風險：樣本偏差、資料品質
- 優化：引入因果推斷、長期追蹤 LTV

Practice Exercise（練習題）
- 基礎練習：為一個客服流程設計指標樹與事件 schema
- 進階練習：用公開資料模擬 A/B 與 ROI 計算（Python/SQL）
- 專案練習：打造可重複的實驗與 ROI 儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：指標樹、事件、儀表板齊備
- 程式碼品質（30%）：資料模型清晰、註解完整
- 效能優化（20%）：查詢效能、儀表板穩定
- 創新性（10%）：額外引入因果分析/貢獻分析


## Case #2: 複雜企業域的 Vibe Coding：RAG + SME 校正閉環

### Problem Statement（問題陳述）
**業務場景**：大型保險公司投產理賠系統改版，規則繁多且術語易混淆。團隊希望用 Vibe Coding（人機協作開發）加速產出，但 LLM 常誤讀條款與流程，導致邏輯錯誤與測試失敗率高，延誤上線時程。
**技術挑戰**：將艱澀域知識準確注入生成、維持一致用語、建立自動化驗證與 SME（領域專家）審核迭代。
**影響範圍**：上線品質、合規風險、項目進度與成本。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 上下文不足：模型無法取得最新條款與專有名詞定義。
2. 提示模糊：跨模組邏輯未結構化，使生成不穩定。
3. 測試缺失：無域知識的自動化驗證集與紅線測試。

**深層原因**：
- 架構層面：未設 RAG 與術語庫為核心組件。
- 技術層面：選用通用模型，缺乏檢索與約束輸出。
- 流程層面：缺少 SME 參與與人機協同的評審節點。

### Solution Design（解決方案設計）
**解決策略**：構建「術語庫 + 法規/條款向量庫 + 检索模板 + 結構化輸出 + SME 審核 + 自動化 eval」的迭代閉環。採用 RAG 提供權威上下文，強制 JSON Schema 輸出，將 SME 評語轉為測試用例與負面樣本，不斷收斂。

**實施步驟**：
1. 知識資產化
- 實作細節：建立術語表、條款 PDF → 文本切塊、向量化索引
- 所需資源：LangChain/LlamaIndex、pgvector/Weaviate
- 預估時間：2 週

2. 提示與輸出約束
- 實作細節：檢索後填入模板，強制 JSON Schema，拒答策略
- 所需資源：OpenAI JSON mode/Tools、Pydantic/Typebox
- 預估時間：1 週

3. SME 審核與 Eval
- 實作細節：將審核意見轉為合約測試與紅線查核，離線評估
- 所需資源：Ragas/OpenAI Evals、CI 整合
- 預估時間：1-2 週

**關鍵程式碼/設定**：
```python
# 檢索 + 結構化生成（示例）
from langchain.vectorstores import PGVector
from pydantic import BaseModel, Field
from openai import OpenAI

class Decision(BaseModel):
    claim_id: str
    decision: str  # approve/deny
    reasons: list[str]
    policy_refs: list[str]

client = OpenAI()

def decide_claim(question):
    context = retriever.get_relevant_documents(question, k=6)
    prompt = f"""你是保險理賠專家。根據下列條款與術語，做出決策，若缺資料請要求補件。\n{context}\n輸出遵循 JSON schema。"""
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"user","content":prompt}],
        response_format={"type":"json_object"}
    )
    return Decision.model_validate_json(resp.choices[0].message.content)
# Implementation Example（實作範例）
```

實際案例：理賠試點中，將 SME 校正轉為紅線測試集，迭代 4 輪
實作環境：Python 3.11、pgvector、LangChain、OpenAI SDK v1
實測數據：
- 改善前：域錯誤 18/100 任務；測試通過率 62%
- 改善後：域錯誤 5/100 任務；測試通過率 89%；交付周期縮短 35%
- 改善幅度：錯誤率 -72%；交付效率 +35%

Learning Points（學習要點）
核心知識點：
- RAG 結構化與術語庫治理
- JSON Schema 約束與拒答策略
- SME 評審轉測試與負例沉澱

技能要求：
- 必備技能：文本切塊、索引/檢索、Schema 驗證
- 進階技能：Eval 指標設計、紅線測試工程化

延伸思考：
- 可用於法遵、醫療、金融審核
- 風險：知識過期、檢索偏差
- 優化：時間衰減、權重重排序、冷熱資料分層

Practice Exercise（練習題）
- 基礎練習：為一組條款建立術語表與向量索引
- 進階練習：設計拒答與補件策略，將 SME 意見轉為測試
- 專案練習：完成一套可跑 CI 的 RAG + Eval 流水線

Assessment Criteria（評估標準）
- 功能完整性（40%）：檢索、Schema、Eval 齊備
- 程式碼品質（30%）：模組化與測試覆蓋
- 效能優化（20%）：檢索準確與延遲
- 創新性（10%）：術語動態維護與權重策略


## Case #3: 只想寫程式的工程師如何在 AI 時代輸出高價值

### Problem Statement（問題陳述）
**業務場景**：部分工程師偏好深度專注於程式，不擅長跨部門溝通，導致需求理解差異與重工。希望藉 AI 將「需求 ⇄ 規格 ⇄ 程式」的轉換流程自動化，減少會議與誤解。
**技術挑戰**：將非結構化需求轉為可執行規格與測試、同步到程式與文件，建立低成本的透明化溝通渠道。
**影響範圍**：需求落地、返工率、交付周期、士氣。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 文檔缺失：需求/規格/測試不可追蹤。
2. 共識成本高：會議頻繁，訊息分散。
3. 沒有單一真相來源（Single Source of Truth）。

**深層原因**：
- 架構層面：Doc-as-code 與測試驅動未落地。
- 技術層面：缺少將自然語言轉規格/測試的自動化工具。
- 流程層面：需求審核與交付缺標準化節點。

### Solution Design（解決方案設計）
**解決策略**：建立「PRD/用例生成器 + 接受標準（Gherkin） + 測試骨架 + 自動文檔同步」的工作流，將非結構化對話轉為可執行規格與測試，並由 CI 驗證。以 AI 協助寫文檔與產出用例，讓工程師專注實作。

**實施步驟**：
1. 規格與用例生成
- 實作細節：將需求輸入 LLM 產出 User Stories、Gherkin、API 規格
- 所需資源：OpenAI、Cucumber、Stoplight
- 預估時間：1 週

2. Doc-as-code 與同步
- 實作細節：Markdown/ADR 管理、PR 檢視、GitHub Actions 產出網站
- 所需資源：Docusaurus、gh-pages
- 預估時間：1 週

3. 測試骨架與 CI
- 實作細節：由 Gherkin 產生測試骨架，PR 必須過測
- 所需資源：Cucumber/Playwright/Jest
- 預估時間：1 週

**關鍵程式碼/設定**：
```typescript
// 由需求文本生成 Gherkin 驗收準則（示例）
import OpenAI from "openai";
const client = new OpenAI();

async function genGherkin(requirement: string) {
  const prompt = `為以下需求產生 Gherkin 驗收準則，語言中文：\n${requirement}`;
  const res = await client.chat.completions.create({
    model: "gpt-4.1-mini",
    messages: [{ role: "user", content: prompt }]
  });
  return res.choices[0].message.content;
}
// Implementation Example（實作範例）
```

實際案例：以 PR 模板強制附上 AI 產生的用例/規格
實作環境：Node 20、OpenAI SDK v4、Cucumber、GitHub Actions
實測數據：
- 改善前：平均每個功能 3 會議小時、返工率 27%
- 改善後：會議時間降至 1.8 小時、返工率 12%、交付縮短 18%
- 改善幅度：會議 -40%；返工 -55%；Lead time +18%

Learning Points（學習要點）
核心知識點：
- Doc-as-code 與驗收測試驅動
- 非結構化需求轉規格/測試
- PR Gate 與自動化檢查

技能要求：
- 必備技能：Git、測試框架、Markdown
- 進階技能：需求建模、驗收測試設計

延伸思考：
- 可應用於外包協作、跨時區團隊
- 風險：過度依賴 AI 文檔失真
- 優化：引入用戶訪談逐字稿與 Trace 佐證

Practice Exercise（練習題）
- 基礎練習：把一段需求轉為 3 條 Gherkin
- 進階練習：將 Gherkin 轉為可執行測試
- 專案練習：完成 Doc-as-code + PR Gate 流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：規格、測試、文檔齊備
- 程式碼品質（30%）：可讀性、模組化
- 效能優化（20%）：CI 穩定度
- 創新性（10%）：自動同步與審批機制


## Case #4: 前後端分離下的 Vibe Coding：Prompt 套件化與整合測試

### Problem Statement（問題陳述）
**業務場景**：前後端分離專案需導入 AI 生成功能（例如智能表單填寫、摘要），但 Prompt 分散在各端，I/O 不一致，導致統一測試與版本管理困難，整合回歸成本高。
**技術挑戰**：如何設計可共用、可版本化、可測試的 Prompt 套件，並於 E2E 中統一驗證。
**影響範圍**：跨端一致性、測試成本、上線風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Prompt 散落：前後端各自維護。
2. I/O 不一致：缺 JSON Schema 與型別約束。
3. 測試缺乏：無法端到端驗證語義契約。

**深層原因**：
- 架構層面：未將 Prompt 視為第一級工件。
- 技術層面：缺少 Schema 驅動與契約測試。
- 流程層面：無跨端變更審核機制。

### Solution Design（解決方案設計）
**解決策略**：採 Monorepo + prompts/ 套件化，使用 JSON Schema/TypeBox 定義 I/O，一份 Prompt 給多端使用；以契約測試與 E2E（Playwright）確保一致性，並由 CI 發版與鎖定版本。

**實施步驟**：
1. Prompt 套件化
- 實作細節：建立 prompts/，導出模板與 schema
- 所需資源：pnpm workspaces、TypeScript、TypeBox
- 預估時間：1 週

2. 契約測試與 E2E
- 實作細節：用 Mock/Recording 測 API 回應，檢查 schema
- 所需資源：Jest、Playwright、VCR 工具
- 預估時間：1 週

3. CI 發版
- 實作細節：changeset/semantic-release，自動更新版本與 changelog
- 所需資源：GitHub Actions
- 預估時間：0.5 週

**關鍵程式碼/設定**：
```yaml
# Monorepo 結構（示例）
packages/
  prompts/
    src/
      summarize.prompt.ts
      summarize.schema.ts
    package.json
apps/
  web/
  api/
# Implementation Example（實作範例）
```

實際案例：摘要/推薦/表單校驗三種 Prompt 共用於前後端
實作環境：Node 20、pnpm、TypeScript、Playwright、GitHub Actions
實測數據：
- 改善前：整合缺陷 12 起/版本
- 改善後：整合缺陷 3 起/版本；E2E 自動化覆蓋 85%
- 改善幅度：缺陷 -75%；整合時間 -40%

Learning Points（學習要點）
核心知識點：
- Prompt as code、Schema 驅動
- 契約測試與 E2E
- 版本管理與變更日誌

技能要求：
- 必備技能：TS/Node、CI/CD、測試框架
- 進階技能：API 契約測試、Mock 錄製

延伸思考：
- 可擴展到多平台（web、mobile）
- 風險：套件版本衝突
- 優化：引入 Prompt Linter 與快照測試

Practice Exercise（練習題）
- 基礎練習：將一個 Prompt 套件化並導出 Schema
- 進階練習：完成契約測試與 E2E
- 專案練習：建置 Monorepo + CI 發版流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：套件化、Schema、測試齊備
- 程式碼品質（30%）：型別嚴謹、模組化
- 效能優化（20%）：CI 時間、測試穩定
- 創新性（10%）：Linter、快照驗證


## Case #5: 既有功能小改的 Prompt 變更管理與版本控制

### Problem Statement（問題陳述）
**業務場景**：針對既有功能的小修改，是否需要新建 Prompt 檔？若直接修改，常造成回歸風險與不可追蹤的行為差異。
**技術挑戰**：在最小化成本與風險下，落實 Prompt 的版本管理、範圍控制與回滾能力。
**影響範圍**：回歸缺陷、審查效率、可追溯性。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 版本化缺失：無 semver 與 changelog。
2. 回歸測試不足：未建立對應的用例快照。
3. 變更粒度過大：難以審查與回滾。

**深層原因**：
- 架構層面：Prompt 不是可獨立發版的工件。
- 技術層面：缺快照測試與金標（golden set）。
- 流程層面：缺變更審批與灰度釋出。

### Solution Design（解決方案設計）
**解決策略**：採用 SemVer + 變更筆記 + 快照測試 + 灰度開關。小修以 patch；行為變更以 minor；破壞性以 major。建立「Prompt patch」模式，允許小規模覆寫與快速回滾。

**實施步驟**：
1. SemVer 與 Changelog
- 實作細節：用 changesets 生成版本與 log
- 所需資源：changesets、GitHub Actions
- 預估時間：0.5 週

2. 快照與金標
- 實作細節：Golden set 驗證、Prompt 輸出快照比對
- 所需資源：Jest snapshot、JSON diff
- 預估時間：0.5 週

3. 灰度釋出與回滾
- 實作細節：Feature flag 控制變體，支持快速回退
- 所需資源：Unleash/LaunchDarkly
- 預估時間：0.5 週

**關鍵程式碼/設定**：
```bash
# 以 changesets 管理版本（示例）
pnpm dlx changeset
pnpm changeset version
pnpm changeset publish
# Implementation Example（實作範例）
```

實際案例：搜尋建議文案微調，以 patch 釋出並快照校驗
實作環境：Node 20、changesets、Jest
實測數據：
- 改善前：文案小改導致回歸 5 起/季
- 改善後：回歸 1 起/季；回滾時間 < 10 分鐘
- 改善幅度：回歸 -80%；回滾 TTR -70%

Learning Points（學習要點）
核心知識點：
- SemVer 與變更治理
- 快照測試與 Golden set
- 灰度釋出與回滾

技能要求：
- 必備技能：Git Flow、測試工具
- 進階技能：變種管理、實驗設計

延伸思考：
- 可與流量分層與人群定向結合
- 風險：快照脆弱
- 優化：引入語義 diff 與容忍閾值

Practice Exercise（練習題）
- 基礎練習：為一個 Prompt 套件引入 changesets
- 進階練習：撰寫快照測試與金標集
- 專案練習：整合灰度與回滾流程

Assessment Criteria（評估標準）
- 功能完整性（40%）：版本、快照、灰度齊全
- 程式碼品質（30%）：自動化腳本與註解
- 效能優化（20%）：釋出效率
- 創新性（10%）：語義 diff/容忍設計


## Case #6: 維運場景的 Vibe Coding：對話式 Runbook 與事件自動診斷

### Problem Statement（問題陳述）
**業務場景**：SRE 值班時，事故處理需查閱多份 Runbook 與日誌，切換成本高且新人成長慢。希望用對話式助理加速定位故障與執行操作。
**技術挑戰**：整合監控、日誌、Kubernetes 操作與安全防護，避免危險命令。
**影響範圍**：MTTA/MTTR、誤操作風險、值班負擔。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 知識分散：Runbook 與日誌未集中檢索。
2. 上下文缺失：助理無法調用工具與安全校驗。
3. 記錄不足：事故過程不可審計。

**深層原因**：
- 架構層面：缺工具調用與審計中樞。
- 技術層面：無對話與命令的安全門檻。
- 流程層面：事後檢討缺可追溯資料。

### Solution Design（解決方案設計）
**解決策略**：構建「對話 + 檢索 + 工具調用 + 安全核准 + 全程追蹤」的運維代理。限制白名單命令、二次確認、高風險需多人核准，所有操作進行審計。

**實施步驟**：
1. 知識檢索
- 實作細節：Runbook/RFC/過往事故向量化
- 資源：Elasticsearch/Weaviate、LlamaIndex
- 時間：1 週

2. 工具封裝
- 實作細節：封裝 kubectl、helm、grafana API、log 查詢
- 資源：Python Typer/Click、Service Account
- 時間：1-2 週

3. 安全與審計
- 實作細節：命令白名單、二次確認、審計日誌
- 資源：OPA、Audit Log、Vault
- 時間：1 週

**關鍵程式碼/設定**：
```python
# 以工具呼叫方式安全執行 kubectl（示例）
def scale_deploy(ns, name, replicas):
    assert 0 <= replicas <= 50, "安全限制"
    cmd = ["kubectl","-n",ns,"scale","deploy",name,f"--replicas={replicas}"]
    return run_safe(cmd)  # 內含審計與二次確認
# Implementation Example（實作範例）
```

實際案例：高峰期自動定位 Pod CrashLoopBackOff 並建議調整
實作環境：Python 3.11、K8s 1.29、OpenAI SDK、Grafana/Loki API、OpenTelemetry
實測數據：
- 改善前：MTTA 15 分鐘、MTTR 90 分鐘
- 改善後：MTTA 5 分鐘、MTTR 55 分鐘
- 改善幅度：MTTA -66%；MTTR -39%

Learning Points（學習要點）
核心知識點：
- 對話式運維與安全控制
- 工具調用與審計
- 事故知識回饋閉環

技能要求：
- 必備技能：K8s、監控/日誌、腳本
- 進階技能：安全策略與審計

延伸思考：
- 可擴展到 DB 運維、雲資源治理
- 風險：錯誤命令執行
- 優化：引入變更凍結區間與多因子核准

Practice Exercise（練習題）
- 基礎練習：封裝一個安全的 kubectl 工具
- 進階練習：整合日誌檢索與建議
- 專案練習：建置對話式 SRE 助理 MVP

Assessment Criteria（評估標準）
- 功能完整性（40%）：檢索、工具調用、安全齊備
- 程式碼品質（30%）：權限分離、註解
- 效能優化（20%）：延遲與穩定性
- 創新性（10%）：自動補救與學習閉環


## Case #7: LLM 品質評估與回歸防護（Eval Harness）

### Problem Statement（問題陳述）
**業務場景**：模型或 Prompt 每次更新都可能引入品質回退。團隊需要一套自動化的離線/線上評估，量化準確度、覆蓋度與風險，作為發佈門檻。
**技術挑戰**：定義可重複的評估數據集、指標、評審規則與門檻，並整合 CI/CD。
**影響範圍**：品質穩定、發佈速度、信任度。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無金標集：缺標準答案與紅線測試。
2. 無自動化評估：評審靠人工。
3. 無門檻：改了就上，易回退。

**深層原因**：
- 架構層面：評估不在流水線內。
- 技術層面：缺可重放的測試與統計。
- 流程層面：無品質門檻與審批。

### Solution Design（解決方案設計）
**解決策略**：建立「任務/數據集/指標/評審器」抽象，支援自動評估（關鍵詞匹配、規則、模型評審）與人工複核。將結果入庫、可視化，設置門檻阻擋發佈。

**實施步驟**：
1. 金標與紅線
- 細節：標註 50-200 例；設關鍵錯誤紅線
- 資源：Label Studio、CSV
- 時間：1 週

2. 指標與評審器
- 細節：Exact/F1/ROUGE、模型評審
- 資源：Ragas/OpenAI Evals
- 時間：1 週

3. CI/CD 門檻
- 細節：PR 觸發 eval，未達門檻阻擋
- 資源：GitHub Actions
- 時間：0.5 週

**關鍵程式碼/設定**：
```python
# 簡易 Eval：Exact/F1 與 LLM 評審（示例）
def f1(pred, gold):
    p = set(pred.split()); g = set(gold.split())
    return 2*len(p&g)/(len(p)+len(g)+1e-9)

def llm_judge(prompt, pred, gold):
    q = f"根據指標判斷是否可接受：\n預期:{gold}\n輸出:{pred}\n只回YES或NO"
    return client.chat.completions.create(model="gpt-4o-mini",
      messages=[{"role":"user","content":q}]).choices[0].message.content=="YES"
# Implementation Example（實作範例）
```

實際案例：FAQ 問答與摘要雙任務的離線評估
實作環境：Python 3.11、Ragas、OpenAI SDK、GitHub Actions
實測數據：
- 改善前：回退率 22%/季
- 改善後：回退率 5%/季；事故減少 60%
- 改善幅度：回退 -77%

Learning Points（學習要點）
核心知識點：
- 金標/紅線測試
- 自動與人審結合
- CI 門檻化

技能要求：
- 必備技能：Python、測試設計
- 進階技能：模型評審與偏誤控制

延伸思考：
- 可拓展線上 A/B 與長期追蹤
- 風險：過擬合金標
- 優化：資料增量與輪替策略

Practice Exercise（練習題）
- 基礎練習：製作 50 例金標集
- 進階練習：加入 LLM 評審器
- 專案練習：把 Eval 接入 CI 門檻

Assessment Criteria（評估標準）
- 功能完整性（40%）：數據/指標/門檻
- 程式碼品質（30%）：可維護與測試
- 效能優化（20%）：批量評估效率
- 創新性（10%）：自定指標/加權策略


## Case #8: 成本與延遲優化：回應快取與模型路由

### Problem Statement（問題陳述）
**業務場景**：生成式功能上線後，API 成本飆升且延遲過高。需要降低花費並維持品質。
**技術挑戰**：設計多層快取、提示規範化、內容去重、動態模型選擇與流控。
**影響範圍**：毛利率、體驗、擴展能力。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 重複請求未快取。
2. 一律用昂貴模型。
3. 長上下文與冗詞。

**深層原因**：
- 架構層面：缺可插拔的中介層。
- 技術層面：缺指紋/語義快取與模型路由。
- 流程層面：無成本與延遲目標。

### Solution Design（解決方案設計）
**解決策略**：引入「規範化 + 指紋/語義快取 + 分層 TTL + 模型路由 + 流控」。輕任務走小模型，難任務升級；對重複/近似請求命中快取。

**實施步驟**：
1. 規範化與指紋
- 細節：去空白/排序、SHA256/MinHash
- 資源：Redis、SimHash
- 時間：0.5 週

2. 語義快取
- 細節：嵌入相似度命中
- 資源：FAISS/pgvector
- 時間：1 週

3. 模型路由
- 細節：根據長度/風險/需要工具決定模型
- 資源：Router 服務
- 時間：1 週

**關鍵程式碼/設定**：
```python
# 文本指紋快取（示例）
key = sha256(normalize(prompt).encode()).hexdigest()
resp = redis.get(key)
if not resp:
    model = route(prompt)  # 動態選模型
    resp = call_llm(model, prompt)
    redis.setex(key, ttl, resp)
# Implementation Example（實作範例）
```

實際案例：摘要/QA/重寫三任務成本治理
實作環境：Python 3.11、Redis、pgvector、OpenAI SDK
實測數據：
- 改善前：平均延遲 2.8s、成本 $100/日
- 改善後：平均延遲 1.4s、成本 $45/日
- 改善幅度：延遲 -50%；成本 -55%

Learning Points（學習要點）
核心知識點：
- 指紋與語義快取
- 模型路由策略
- 延遲/成本 SLO

技能要求：
- 必備技能：快取、嵌入、API
- 進階技能：近似檢索、動態決策

延伸思考：
- 加入自動可觀測與告警
- 風險：快取污染
- 優化：多版本快取與租戶隔離

Practice Exercise（練習題）
- 基礎練習：實作指紋快取
- 進階練習：語義快取 + 相似度門檻
- 專案練習：完成路由服務與 SLO 監控

Assessment Criteria（評估標準）
- 功能完整性（40%）：快取、路由、監控
- 程式碼品質（30%）：錯誤處理、註解
- 效能優化（20%）：命中率與延遲
- 創新性（10%）：自適應策略


## Case #9: 敏感資料保護：Prompt 與日誌的 PII 遮罩

### Problem Statement（問題陳述）
**業務場景**：在客服與金融應用中，必須防止 PII 外洩。提示與日誌中經常夾帶身份資訊，帶來合規風險。
**技術挑戰**：高召回率的遮罩、誤遮罩控制、可審計與例外管理。
**影響範圍**：法遵、品牌、風險成本。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 原始 Prompt 直接包含 PII。
2. 日誌未遮罩存檔。
3. 缺例外處理。

**深層原因**：
- 架構層面：缺資料最小化與 DLP。
- 技術層面：缺 PII 偵測與遮罩策略。
- 流程層面：無審批與白名單。

### Solution Design（解決方案設計）
**解決策略**：建立「輸入前遮罩 + 服務端 DLP + 日誌遮罩 + 例外審批」。採規則+模型混合偵測，保留哈希指紋便於追蹤。

**實施步驟**：
1. PII 偵測與遮罩
- 細節：Email/電話/地址/身分證規則 + NER
- 資源：Presidio/Regex/Spacy
- 時間：1 週

2. 日誌與審計
- 細節：遮罩後存儲、例外白名單
- 資源：OpenTelemetry、SIEM
- 時間：0.5 週

3. 安全審批
- 細節：高敏欄位解遮罩流程
- 資源：內部審批系統/Vault
- 時間：0.5 週

**關鍵程式碼/設定**：
```python
# PII 遮罩（示例）
def mask(text):
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[EMAIL]', text)
    text = re.sub(r'\b09\d{8}\b', '[PHONE]', text)
    return text
# Implementation Example（實作範例）
```

實際案例：客服對話 + 工單系統全鏈遮罩
實作環境：Python、Presidio、OpenTelemetry Collector
實測數據：
- 改善前：每月 2 起 PII 外洩事故
- 改善後：0 起，誤遮罩率 < 3%
- 改善幅度：外洩 -100%

Learning Points（學習要點）
核心知識點：
- DLP 與資料最小化
- 遮罩策略與例外治理
- 可審計與追溯

技能要求：
- 必備技能：Regex、日志管線
- 進階技能：NER 與誤報控制

延伸思考：
- 可結合客製化 NER
- 風險：過遮罩影響效果
- 優化：可調權重與抽樣審核

Practice Exercise（練習題）
- 基礎練習：實作 Email/電話遮罩
- 進階練習：整合 NER 與誤報評估
- 專案練習：全鏈遮罩與審批

Assessment Criteria（評估標準）
- 功能完整性（40%）：遮罩、審計、例外
- 程式碼品質（30%）：規則可維護
- 效能優化（20%）：吞吐與延遲
- 創新性（10%）：混合偵測方案


## Case #10: 結構化提示與函式呼叫：降低幻覺並穩定整合

### Problem Statement（問題陳述）
**業務場景**：AI 需返回可直接落地於前端/後端的結構化資料（例如表單建議、標籤、坐標）。自由文本輸出不穩定，導致解析錯誤與幻覺。
**技術挑戰**：約束輸出、校驗、錯誤回復與可測試性。
**影響範圍**：整合穩定、體驗、缺陷率。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無格式約束。
2. 缺校驗與重試。
3. 缺功能分離（查詢 vs 計算）。

**深層原因**：
- 架構層面：不區分 LLM 與業務邏輯邊界。
- 技術層面：未使用 JSON mode/Tools。
- 流程層面：無契約測試。

### Solution Design（解決方案設計）
**解決策略**：採 JSON Schema + 函式呼叫 + 嚴格驗證 + 重試/保底。把 LLM 當解析器/規則引擎，業務邏輯在外部。

**實施步驟**：
1. Schema 與函式設計
- 細節：定義輸入/輸出，拆功能為工具
- 資源：TypeBox/Pydantic、OpenAI tools
- 時間：0.5 週

2. 驗證與重試
- 細節：Schema 驗證、指引錯誤修正
- 資源：AJV/Pydantic
- 時間：0.5 週

3. 契約測試
- 細節：基於 Schema 的快照與金標
- 資源：Jest/Pytest
- 時間：0.5 週

**關鍵程式碼/設定**：
```typescript
// JSON Schema 驗證（示例）
import { Type, Static } from "@sinclair/typebox";
const Output = Type.Object({
  tags: Type.Array(Type.String()),
  confidence: Type.Number({ minimum: 0, maximum: 1 })
});
type Output = Static<typeof Output>;
// Implementation Example（實作範例）
```

實際案例：對產品描述打標籤並返回信心值
實作環境：Node 20、TypeBox、OpenAI Tools、AJV
實測數據：
- 改善前：解析錯誤 9% 、幻覺 7%
- 改善後：解析錯誤 1.5% 、幻覺 2.5%
- 改善幅度：解析 -83%；幻覺 -64%

Learning Points（學習要點）
核心知識點：
- Schema 驅動與函式呼叫
- 驗證與錯誤恢復
- 契約測試

技能要求：
- 必備技能：TS/Python、Schema 工具
- 進階技能：錯誤引導與可觀測

延伸思考：
- 可結合工具鏈與工作流
- 風險：Schema 過嚴
- 優化：漸進式約束

Practice Exercise（練習題）
- 基礎練習：定義一個 JSON Schema 並驗證
- 進階練習：加入函式呼叫與重試
- 專案練習：建立契約測試與快照

Assessment Criteria（評估標準）
- 功能完整性（40%）：Schema、工具、驗證
- 程式碼品質（30%）：錯誤處理
- 效能優化（20%）：延遲與成功率
- 創新性（10%）：錯誤引導設計


## Case #11: 內容安全與濫用防護：審查與風險分級

### Problem Statement（問題陳述）
**業務場景**：UGC 場景需要對不當內容進行攔截與分級。單用關鍵詞黑名單誤判高。
**技術挑戰**：建立多層內容審查、風險分級、可追蹤與申訴機制。
**影響範圍**：合規、品牌、用戶安全。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 單一規則引擎。
2. 無多級處理與人工複核。
3. 缺少審計與申訴流程。

**深層原因**：
- 架構層面：缺審查中台。
- 技術層面：無多模型與指標。
- 流程層面：人審節點缺失。

### Solution Design（解決方案設計）
**解決策略**：規則 + 模型（Moderation API）+ 風險分級（低/中/高）+ 人工複核 + 審計。低風險自動通過，中風險拉黑名單強化，高風險封鎖並審核。

**實施步驟**：
1. 多層審查
- 細節：黑名單 + Moderation + LLM 判斷
- 資源：OpenAI moderation、自定模型
- 時間：1 週

2. 風險分級與流轉
- 細節：工作流路由，人審 SLA
- 資源：Workflow/BPM
- 時間：1 週

3. 申訴與審計
- 細節：可追溯、申訴通道
- 資源：審計系統/票務
- 時間：0.5 週

**關鍵程式碼/設定**：
```python
# 風險分級（示例）
risk = "low"
mod = moderation.check(text)
if mod.flagged: risk = "high"
elif llm_judge_safe(text) is False: risk = "medium"
# route_to_queue(risk)
# Implementation Example（實作範例）
```

實際案例：社群貼文上線前審查
實作環境：Python、OpenAI moderation、BPMN 工作流
實測數據：
- 改善前：誤攔 9%、漏攔 7%
- 改善後：誤攔 3.5%、漏攔 2.1%
- 改善幅度：誤攔 -61%；漏攔 -70%

Learning Points（學習要點）
核心知識點：
- 多層審查與風險分級
- 人機協作審核
- 審計與申訴

技能要求：
- 必備技能：API 集成、規則設計
- 進階技能：指標/混合模型

延伸思考：
- 可與使用者信任分計分
- 風險：對抗性攻擊
- 優化：自動回訓難例

Practice Exercise（練習題）
- 基礎練習：整合 Moderation API
- 進階練習：實作風險分級與路由
- 專案練習：審核台 + 審計

Assessment Criteria（評估標準）
- 功能完整性（40%）：審查、分級、審計
- 程式碼品質（30%）：可維護
- 效能優化（20%）：吞吐延遲
- 創新性（10%）：自適應黑名單


## Case #12: 從 PoC 到 Product：LLMOps 流水線與多環境發佈

### Problem Statement（問題陳述）
**業務場景**：PoC 實驗有效，但無法穩健上線。缺少多環境、資料/Prompt 版本化與自動化釋出。
**技術挑戰**：一體化管理資料、Prompt、模型、評估與部署，支撐迭代。
**影響範圍**：上線時程、穩定性、合規。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 沒有資料/Prompt 版控。
2. 沒有多環境配置。
3. 沒有發佈門檻與回滾。

**深層原因**：
- 架構層面：MLOps/LLMOps 缺位。
- 技術層面：資料/Prompt/模型異步。
- 流程層面：變更管理缺失。

### Solution Design（解決方案設計）
**解決策略**：建立「資料集版本化 + Prompt 套件 + 模型卡 + 多環境配置 + Eval 門檻 + Feature Flag」的流水線，將一切基礎建設化。

**實施步驟**：
1. 版本化與模型卡
- 細節：DVC/Weights & Biases 記錄
- 資源：DVC/W&B
- 時間：1 週

2. 多環境與機密管理
- 細節：dev/stage/prod、Secrets 管理
- 資源：Vault、SOPS、Helm
- 時間：1 週

3. 發佈與回滾
- 細節：GitOps、Eval Gate、Feature Flag
- 資源：ArgoCD、Unleash
- 時間：1 週

**關鍵程式碼/設定**：
```yaml
# ArgoCD 應用（示例）
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  source:
    repoURL: https://git.example/llm-app.git
    path: deploy/overlays/stage
# Implementation Example（實作範例）
```

實際案例：文件搜尋助理從試點到企業版部署
實作環境：K8s、ArgoCD、Vault、W&B、DVC
實測數據：
- 改善前：上線周期 4 週；回退需 1 天
- 改善後：上線 1 週；回退 < 30 分鐘
- 改善幅度：交付 +75%；回退 -95%

Learning Points（學習要點）
核心知識點：
- LLMOps 元件化
- 多環境與機密治理
- 發佈門檻與回滾

技能要求：
- 必備技能：K8s/GitOps、CI/CD
- 進階技能：資料/模型治理

延伸思考：
- 可擴展跨區域與合規隔離
- 風險：工具鏈複雜
- 優化：平台化與腳手架

Practice Exercise（練習題）
- 基礎練習：建立多環境配置
- 進階練習：接入 Eval Gate
- 專案練習：以 GitOps 完成發佈/回退

Assessment Criteria（評估標準）
- 功能完整性（40%）：版本、環境、門檻
- 程式碼品質（30%）：IaC 樣式
- 效能優化（20%）：發佈效率
- 創新性（10%）：平台化工具


## Case #13: 可觀測性：LLM 呼叫的分佈追蹤與品質回饋

### Problem Statement（問題陳述）
**業務場景**：生成式功能偶發慢與錯，但難以定位是模型、網路、外部工具還是提示問題。需要端到端追蹤與質量回饋。
**技術挑戰**：將 Prompt、上下文、模型參數、工具呼叫與延遲/錯誤打通。
**影響範圍**：SLO 達成、排障效率、成本。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺追蹤 ID 與 span。
2. 缺統一日誌欄位。
3. 缺用戶標記與回饋。

**深層原因**：
- 架構層面：觀測性非一等公民。
- 技術層面：未導入 OTel 與事件模式。
- 流程層面：缺事後分析機制。

### Solution Design（解決方案設計）
**解決策略**：以 OpenTelemetry 為核心，將每次 LLM 呼叫、檢索、工具、外呼建立 span，關聯 Prompt 版本與使用者回饋，建儀表板與告警。

**實施步驟**：
1. 追蹤與日誌
- 細節：context_id、prompt_version、model、latency、cost
- 資源：OTel SDK、Collector、Tempo/Loki
- 時間：1 週

2. 儀表板與告警
- 細節：P95 延遲、錯誤率、成本/請求
- 資源：Grafana
- 時間：0.5 週

3. 回饋收集
- 細節：thumbs up/down、理由標註
- 資源：UI 元件/事件上報
- 時間：0.5 週

**關鍵程式碼/設定**：
```python
# OTel span 標註（示例）
with tracer.start_as_current_span("llm.call") as span:
    span.set_attribute("prompt.version", "1.2.3")
    span.set_attribute("model", "gpt-4.1-mini")
    span.set_attribute("tokens", 1234)
# Implementation Example（實作範例）
```

實際案例：問答服務鍊路可視化與品質熱區定位
實作環境：Python、OTel、Grafana Tempo/Loki、OpenAI SDK
實測數據：
- 改善前：定位問題均耗時 > 2 小時
- 改善後：平均 25 分鐘定位；P95 延遲 -28%
- 改善幅度：排障效率 +79%

Learning Points（學習要點）
核心知識點：
- 分佈追蹤與指標設計
- 成本與品質聯動
- 用戶回饋閉環

技能要求：
- 必備技能：OTel、儀表板
- 進階技能：追蹤採樣/隱私

延伸思考：
- 可用於 A/B 與成本熱區
- 風險：隱私
- 優化：遮罩與抽樣

Practice Exercise（練習題）
- 基礎練習：為 LLM 呼叫加 span
- 進階練習：建立儀表板與告警
- 專案練習：打通用戶回饋與追蹤

Assessment Criteria（評估標準）
- 功能完整性（40%）：追蹤、指標、告警
- 程式碼品質（30%）：欄位規範
- 效能優化（20%）：採樣/負載
- 創新性（10%）：品質熱區分析


## Case #14: 企業文件助理：可控的 RAG 查詢系統

### Problem Statement（問題陳述）
**業務場景**：員工需快速查詢 SOP/產品文件/法規。傳統關鍵詞搜尋找不到或查太多。希望問答準確且可引用來源。
**技術挑戰**：文檔切塊與檢索策略、來源可解釋、拒答與補件。
**影響範圍**：知識獲取效率、錯誤決策風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 切塊粒度不佳。
2. 無來源引用。
3. 無拒答策略。

**深層原因**：
- 架構層面：檢索/生成耦合。
- 技術層面：缺重排序、混合檢索。
- 流程層面：缺內容生命周期管理。

### Solution Design（解決方案設計）
**解決策略**：混合檢索（BM25 + 向量）+ 重排序 + 可引用來源 + 拒答/補件。引入內容有效期與權限控制。

**實施步驟**：
1. 切塊與索引
- 細節：結構化切塊與 metadata
- 資源：LlamaIndex、Elasticsearch/Weaviate
- 時間：1 週

2. 混合檢索與重排
- 細節：BM25/向量融合，cross-encoder 重排
- 資源：Elastic、SentenceTransformers
- 時間：1 週

3. 生成與拒答
- 細節：source 引用，信心分數，缺資料拒答
- 資源：OpenAI、模板
- 時間：0.5 週

**關鍵程式碼/設定**：
```python
# 混合檢索（示例）
bm25_hits = es.search(q)["hits"]
vec_hits = vec.search(embed(q))
candidates = merge(bm25_hits, vec_hits)
reranked = cross_encoder.rank(q, candidates)[:k]
# Implementation Example（實作範例）
```

實際案例：內部知識庫問答系統
實作環境：Elastic 8.x、Weaviate、SentenceTransformers、OpenAI
實測數據：
- 改善前：一問多答時間 6 分鐘；正確率 68%
- 改善後：1.8 分鐘；正確率 86%；引用覆蓋 95%
- 改善幅度：效率 +70%；正確率 +18pp

Learning Points（學習要點）
核心知識點：
- 混合檢索與重排序
- 可解釋引用與信心
- 拒答/補件

技能要求：
- 必備技能：檢索/嵌入
- 進階技能：重排序與融合

延伸思考：
- 權限與內容新鮮度
- 風險：過時資料
- 優化：時間權重與來源評分

Practice Exercise（練習題）
- 基礎練習：建立 BM25 + 向量索引
- 進階練習：加入 cross-encoder 重排
- 專案練習：完成 RAG 問答 MVP

Assessment Criteria（評估標準）
- 功能完整性（40%）：切塊、檢索、生成
- 程式碼品質（30%）：模組化
- 效能優化（20%）：延遲/正確性
- 創新性（10%）：引用/信心策略


## Case #15: 流量控制：Rate Limit、熔斷與回退策略

### Problem Statement（問題陳述）
**業務場景**：高峰流量下，模型 API 出現限流與超時，導致整體服務雪崩，需要彈性保護。
**技術挑戰**：設計令牌桶、熔斷器、重試退避與降級響應。
**影響範圍**：可用性、體驗、成本。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無流控策略。
2. 無熔斷保護。
3. 重試風暴。

**深層原因**：
- 架構層面：缺保護中介層。
- 技術層面：無退避與限流實作。
- 流程層面：缺容量計畫。

### Solution Design（解決方案設計）
**解決策略**：令牌桶限流 + 熔斷器 + 指數退避重試 + 回退（較小模型/舊結果/提示縮短），確保核心路徑存活。

**實施步驟**：
1. 限流與熔斷
- 細節：按租戶/功能限流；錯誤率門檻熔斷
- 資源：Envoy/Resilience4j
- 時間：0.5 週

2. 重試與退避
- 細節：Jitter 退避；Idempotency-Key
- 資源：客製中介層
- 時間：0.5 週

3. 回退策略
- 細節：較小模型/舊快照/摘要模式
- 資源：Router/Cache
- 時間：0.5 週

**關鍵程式碼/設定**：
```typescript
// 指數退避（示例）
for (let i=0;i<max;i++){
  try{ return await call(); }
  catch(e){ await sleep((2**i + Math.random())*100); }
}
// Implementation Example（實作範例）
```

實際案例：高峰促銷期間問答服務保護
實作環境：Node 20、Resilience4j/Envoy、Redis
實測數據：
- 改善前：錯誤率 12%、P95 4.5s
- 改善後：錯誤率 3.2%、P95 2.1s
- 改善幅度：錯誤率 -73%；延遲 -53%

Learning Points（學習要點）
核心知識點：
- 限流/熔斷/退避
- 回退策略設計
- 可用性 SLO

技能要求：
- 必備技能：中介層與網路
- 進階技能：容量計畫

延伸思考：
- 多區域路由
- 風險：過度限流
- 優化：自適應限流

Practice Exercise（練習題）
- 基礎練習：實作令牌桶
- 進階練習：熔斷與退避
- 專案練習：落地回退策略

Assessment Criteria（評估標準）
- 功能完整性（40%）：限流、熔斷、退避
- 程式碼品質（30%）：錯誤處理
- 效能優化（20%）：SLO 達成
- 創新性（10%）：自適應策略


## Case #16: 微調 vs RAG vs 系統 Prompt：決策與實作

### Problem Statement（問題陳述）
**業務場景**：產品需提升專業回答與風格一致性，團隊猶豫採微調、RAG 或加強系統 Prompt。
**技術挑戰**：選擇成本/效果最佳方案，並測試驗證。
**影響範圍**：成本、可維護性、品質。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 目標不清：是記憶/檢索/風格問題？
2. 缺對照實驗。
3. 忽略資料治理成本。

**深層原因**：
- 架構層面：缺決策框架。
- 技術層面：無評估基線。
- 流程層面：資料準備無估算。

### Solution Design（解決方案設計）
**解決策略**：制定決策矩陣：知識頻繁變化 → RAG；固定模式/風格 → 微調；輕度約束 → 系統 Prompt。以相同金標集做對照實驗，評估成本/延遲/品質。

**實施步驟**：
1. 假設與指標
- 細節：明確任務與指標
- 資源：Eval 集
- 時間：0.5 週

2. 三路實驗
- 細節：Prompt/RAG/Fine-tune
- 資源：OpenAI Fine-tuning、向量庫
- 時間：1-2 週

3. 決策與落地
- 細節：選擇最佳性價比，建模卡
- 資源：決策文件
- 時間：0.5 週

**關鍵程式碼/設定**：
```bash
# 微調資料上傳（示例）
openai fine_tuning.jobs.create -t train.jsonl -m gpt-4o-mini
# Implementation Example（實作範例）
```

實際案例：客服風格一致化 + 最新政策引用
實作環境：OpenAI Fine-tuning、Weaviate、Python Eval
實測數據：
- Prompt：正確率 72%、成本 $0.9/100
- RAG：正確率 88%、成本 $1.2/100
- 微調：正確率 84%、成本 $0.7/100
- 決策：RAG 回答專業性最佳；混合：RAG + 輕微調風格

Learning Points（學習要點）
核心知識點：
- 決策矩陣與對照實驗
- 微調資料製備
- 成本/延遲/品質折衝

技能要求：
- 必備技能：資料清理、Eval
- 進階技能：微調/檢索工程

延伸思考：
- 長期維護成本
- 風險：資料汙染
- 優化：混合式與持續學習

Practice Exercise（練習題）
- 基礎練習：整理 100 例微調資料
- 進階練習：三路對照實驗
- 專案練習：撰寫模型卡與決策文件

Assessment Criteria（評估標準）
- 功能完整性（40%）：三路實驗與分析
- 程式碼品質（30%）：實驗可重現
- 效能優化（20%）：成本/延遲
- 創新性（10%）：混合式策略


## Case #17: Agent 工作流：多工具協作與可控執行圖

### Problem Statement（問題陳述）
**業務場景**：複雜任務（報價、比價、生成合約）需多步驟與工具協作，單輪對話力有未逮，容易失控或重複嘗試。
**技術挑戰**：規劃可觀測、可重試、可中止的有向圖工作流，限制權限與風險。
**影響範圍**：成功率、可控性、安全。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無任務分解與狀態機。
2. 工具權限過大。
3. 缺可視化與審計。

**深層原因**：
- 架構層面：缺工作流引擎。
- 技術層面：無節點重試與補償。
- 流程層面：缺審批節點。

### Solution Design（解決方案設計）
**解決策略**：採用圖式代理（如 LangGraph）建模任務節點與轉移條件，節點封裝工具與權限，提供手動審批節點、重試與補償，並記錄全鏈路。

**實施步驟**：
1. 任務建模
- 細節：將任務拆為節點與邊
- 資源：LangGraph/Temporal
- 時間：1 週

2. 工具封裝與權限
- 細節：最小權限、沙箱/速率限制
- 資源：Policy/OPA
- 時間：1 週

3. 觀測與審批
- 細節：可視化、審批節點、審計
- 資源：UI、OTel
- 時間：1 週

**關鍵程式碼/設定**：
```python
# 簡化的圖節點（示例）
def plan(ctx): ...
def fetch_quotes(ctx): ...
def review(ctx): ...  # 人工審批
graph = {
  "start": plan,
  "plan->fetch": fetch_quotes,
  "fetch->review": review,
}
# Implementation Example（實作範例）
```

實際案例：採購比價 + 合約草擬 + 人審核准
實作環境：Python、LangGraph/Temporal、OpenAI、OTel
實測數據：
- 改善前：成功率 58%；人工介入 70%
- 改善後：成功率 82%；人工介入 35%
- 改善幅度：成功率 +24pp；人工 -50%

Learning Points（學習要點）
核心知識點：
- 任務圖建模
- 工具權限與審批
- 可觀測與補償

技能要求：
- 必備技能：工作流/狀態機
- 進階技能：安全策略、補償交易

延伸思考：
- 可用於客服自動處理、財務流程
- 風險：節點爆炸
- 優化：子圖與模板化

Practice Exercise（練習題）
- 基礎練習：把一個任務畫成 DAG
- 進階練習：加入審批與重試
- 專案練習：完成採購代理 MVP

Assessment Criteria（評估標準）
- 功能完整性（40%）：DAG、權限、審批
- 程式碼品質（30%）：模組化、錯誤處理
- 效能優化（20%）：延遲與吞吐
- 創新性（10%）：可視化與補償策略


## Case #18: Prompt 治理：Linter、單元測試與破壞性變更管控

### Problem Statement（問題陳述）
**業務場景**：團隊多人協同撰寫 Prompt，風格不一致、重複與易退化，影響可維護性與品質。
**技術挑戰**：建立 Prompt 規範、靜態檢查、單元測試與破壞性變更告警。
**影響範圍**：開發效率、品質、風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無風格指南。
2. 無 Lint 與單元測試。
3. 無破壞性變更識別。

**深層原因**：
- 架構層面：缺治理中台。
- 技術層面：無靜態與動態檢查。
- 流程層面：PR Gate 缺失。

### Solution Design（解決方案設計）
**解決策略**：建立 Prompt Style Guide，導入 Linter（長度/禁用詞/佔位符）、單元測試（針對金標）、破壞性變更檢測（快照 diff），以 PR Gate 阻擋。

**實施步驟**：
1. 風格與模板
- 細節：系統/使用者/工具分層、佔位符規則
- 資源：Style Guide、模板庫
- 時間：0.5 週

2. Linter 與單測
- 細節：規則引擎、金標測試
- 資源：ESLint 風格自定、Jest
- 時間：1 週

3. PR Gate
- 細節：CI 檢查、變更報告
- 資源：GitHub Actions
- 時間：0.5 週

**關鍵程式碼/設定**：
```javascript
// Prompt Lint 規則（示例）
module.exports = {
  rules: {
    "max-length": (prompt)=> prompt.length < 4000,
    "no-banned-tokens": (prompt)=> !/ignore.*instructions/i.test(prompt)
  }
}
// Implementation Example（實作範例）
```

實際案例：三條業務線共用的 Prompt 倉庫治理
實作環境：Node 20、自製 Linter、Jest、GitHub Actions
實測數據：
- 改善前：Prompt 變更引起缺陷 10 起/季
- 改善後：4 起/季；PR 阻擋率 22%
- 改善幅度：缺陷 -60%

Learning Points（學習要點）
核心知識點：
- Prompt Style Guide
- Lint/單測/快照
- PR Gate 與報告

技能要求：
- 必備技能：Node/測試
- 進階技能：規則引擎

延伸思考：
- 可與評估門檻整合
- 風險：過嚴規則阻礙創新
- 優化：規則灰度與豁免流程

Practice Exercise（練習題）
- 基礎練習：撰寫 3 條 Lint 規則
- 進階練習：為 Prompt 加單元測試
- 專案練習：建立 PR Gate 與報表

Assessment Criteria（評估標準）
- 功能完整性（40%）：Lint、測試、Gate
- 程式碼品質（30%）：規則結構化
- 效能優化（20%）：CI 效率
- 創新性（10%）：可視化報表



----------------
案例分類
----------------

1. 按難度分類
- 入門級（適合初學者）
  - Case 5（Prompt 版本管理）
  - Case 10（結構化提示/函式呼叫）
  - Case 11（內容安全入門）
- 中級（需要一定基礎）
  - Case 1（ROI 與指標）
  - Case 3（Doc-as-code 與驗收）
  - Case 4（前後端整合）
  - Case 7（Eval Harness）
  - Case 8（成本與延遲）
  - Case 9（PII 遮罩）
  - Case 13（可觀測性）
  - Case 14（RAG 問答）
  - Case 15（流量控制）
  - Case 18（Prompt 治理）
- 高級（需要深厚經驗）
  - Case 2（複雜域 RAG + SME 閉環）
  - Case 6（對話式運維與安全）
  - Case 12（LLMOps 流水線）
  - Case 16（微調 vs RAG 決策）
  - Case 17（Agent 工作流）

2. 按技術領域分類
- 架構設計類：Case 2、4、12、16、17、18
- 效能優化類：Case 8、13、15
- 整合開發類：Case 3、4、10、14
- 除錯診斷類：Case 7、13、15
- 安全防護類：Case 9、11

3. 按學習目標分類
- 概念理解型：Case 1、16
- 技能練習型：Case 5、8、10、15、18
- 問題解決型：Case 2、4、6、7、9、11、13、14
- 創新應用型：Case 3、12、17



----------------
案例關聯圖（學習路徑建議）
----------------
- 建議先學：
  - Case 10（結構化提示/函式呼叫）：掌握穩定輸出基礎
  - Case 5（Prompt 版本管理）：建立變更治理概念
  - Case 1（ROI 與指標）：理解商業價值與度量

- 依賴關係：
  - Case 14（RAG）依賴 Case 10（結構化輸出）與 Case 7（Eval）
  - Case 2（複雜域 RAG）依賴 Case 14 + Case 18（治理）
  - Case 8（成本優化）與 Case 15（流量控制）依賴 Case 13（可觀測性）
  - Case 12（LLMOps）依賴 Case 7（Eval）、Case 18（治理）、Case 1（指標）
  - Case 17（Agent）依賴 Case 10（函式呼叫）、Case 15（流量控制）與 Case 13（觀測）
  - Case 6（對話式運維）依賴 Case 14（檢索）與 Case 11（安全）

- 完整學習路徑：
  1) Case 10 → 5 → 1（打好基礎：輸出與治理與價值）
  2) Case 7 → 13（品質與觀測能力）
  3) Case 14 → 2（從基礎 RAG 到複雜域）
  4) Case 8 → 15（成本與可用性工程）
  5) Case 11 → 9（安全與隱私）
  6) Case 12（將能力平台化與可上線）
  7) Case 17（進階 Agent 工作流）
  8) Case 6（延伸到維運自動化）

此學習路徑由基礎能力（穩定輸出、版本治理、指標）開始，逐步進入評估與觀測，再擴展到檢索強化、複雜域與成本/可靠性工程，最後落到平台化與代理式創新應用，能支撐從 Prompt 到 Product 的完整落地。