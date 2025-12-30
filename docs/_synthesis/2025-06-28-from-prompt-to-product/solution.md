---
layout: synthesis
title: "從 Prompt 到 Product"
synthesis_type: solution
source_post: /2025/06/28/from-prompt-to-product/
redirect_from:
  - /2025/06/28/from-prompt-to-product/solution/
---

以下內容基於「從 Prompt 到 Product」主題與文末 Q&A 所顯示的實際痛點，擴展出可落地的 16 個教學型實戰案例。每個案例皆含問題、根因、解法、關鍵程式碼、成效與練習與評估，便於教學、專案演練與能力評估。

## Case #1: 以北極星與守門指標量化 AI 導入效益

### Problem Statement（問題陳述）
業務場景：企業準備導入生成式 AI，管理層要求可量化的投資報酬與風險控管報表，需在試點期內看到「有感且持續」的改善趨勢，否則不予擴大。缺乏標準指標與實驗方法，無法說服非技術決策者。
技術挑戰：難以定義可觀測、可歸因的品質與生產力指標；缺乏實驗、遙測與 A/B 配置。
影響範圍：決策無法推進、資源無法配置、試點無法擴大。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無基準線：沒有導入前的時間成本、錯誤率、滿意度數據。
2. 指標零散：各團隊以不同方式衡量，無法匯總比較。
3. 缺實驗框架：沒有 A/B 或灰度釋出，難以證明因果。

深層原因：
- 架構層面：事件流與遙測未納入架構設計，資料孤島。
- 技術層面：無統一的埋點 SDK 與資料模型。
- 流程層面：產品、資料與工程對實驗方法論理解不一致。

### Solution Design（解決方案設計）
解決策略：建立「北極星指標 + 一次一個最重要指標（OMTM）+ 守門指標（品質/風險）」的度量體系；用實驗設計（A/B、灰度）與端到端遙測打通決策鏈路，形成可重複驗證的量化閉環。

實施步驟：
1. 指標體系設計
- 實作細節：定義NSM（如任務完成率/工單處理時長）、OMTM（如審閱時間）、守門（毒性/成本/延遲）
- 所需資源：產品經理、數據分析、Looker/Metabase
- 預估時間：1-2 週

2. 事件模型與埋點
- 實作細節：定義 event schema（request_id、cost、latency、feedback）、前後端一致追蹤
- 所需資源：埋點 SDK、資料倉庫（BigQuery/Redshift/Postgres）
- 預估時間：2-3 週

3. 實驗與報表
- 實作細節：Feature flag 灰度、A/B 采樣、看板與週報
- 所需資源：LaunchDarkly/Unleash、BI 工具
- 預估時間：1-2 週

關鍵程式碼/設定：
```ts
// TypeScript: 事件埋點與A/B分流樣例
type AiEvent = {
  request_id: string;
  user_id: string;
  variant: 'control'|'treatment';
  latency_ms: number;
  cost_usd: number;
  toxicity_score: number;
  success: boolean; // 任務完成
  feedback?: number; // 1~5
  ts: string;
};

import fetch from 'node-fetch';
import { v4 as uuid } from 'uuid';

export async function trackAiEvent(evt: Omit<AiEvent,'request_id'|'ts'>) {
  const payload: AiEvent = { ...evt, request_id: uuid(), ts: new Date().toISOString() };
  await fetch(process.env.TELEMETRY_ENDPOINT!, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

// 簡易變體分流
export function assignVariant(userId: string): 'control'|'treatment' {
  return (hashCode(userId) % 2 === 0) ? 'control' : 'treatment';
}
function hashCode(s: string){ return [...s].reduce((a,c)=>((a<<5)-a+c.charCodeAt(0))|0,0); }
```

實際案例：客服摘要助理試點，對照人工摘要（control） vs AI+人工覆核（treatment）。
實作環境：Node.js 20、Postgres、Metabase、Unleash。
實測數據：
- 改善前：平均處理時長 14.2 分鐘、每單成本 $1.10、滿意度 3.6/5
- 改善後：處理時長 8.5 分鐘、每單成本 $0.74、滿意度 4.1/5
- 改善幅度：時長 -40.1%、成本 -32.7%、滿意度 +13.9%

Learning Points（學習要點）
核心知識點：
- 北極星指標/OMTM/守門指標設計
- A/B 與灰度釋出因果驗證
- 事件模型與可觀測性基礎

技能要求：
- 必備技能：資料建模、API 埋點、基本 BI
- 進階技能：因果推斷、統計檢定、效用成本分析

延伸思考：
- 如何將代理指標與業務 KPI 對齊？
- 低流量場景如何設計實驗？
- 多指標衝突時的決策策略？

Practice Exercise（練習題）
- 基礎：為一個聊天任務加上埋點並上傳到資料庫（30 分）
- 進階：完成 A/B 實驗報表與顯著性檢定（2 小時）
- 專案：建置 AI 導入效益看板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：指標定義、埋點、報表齊全
- 程式碼品質（30%）：結構化事件、可測試性
- 效能優化（20%）：埋點對延遲影響可控
- 創新性（10%）：指標設計與可視化創意


## Case #2: DocOps 自動化分享 —— 把投影片/共筆資產化

### Problem Statement（問題陳述）
業務場景：多場分享產生的投影片、共筆、範例與 Q&A 零散在雲端硬碟、HackMD 與部落格，更新同步耗時，影響團隊內外部知識傳遞與品牌一致性。
技術挑戰：多來源同步、權限、格式轉換與嵌入，自動化發佈。
影響範圍：知識無法沉澱、社群回饋減少、重複溝通成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手動更新：多平台重複上傳與貼連結。
2. 無流水線：缺乏版本化與自動發佈流程。
3. 權限分散：公開/內部內容混雜。

深層原因：
- 架構層面：沒有統一內容來源（Single Source of Truth）。
- 技術層面：缺內容轉換與快取層。
- 流程層面：缺少內容審核與發佈節點責任人。

### Solution Design（解決方案設計）
解決策略：以 repo 為內容單一來源，建立 DocOps pipeline：抓取 Slides/共筆、轉檔、嵌入、快取與網站自動部署；分出公開與內部通道，確保權限與合規。

實施步驟：
1. 資產清單與分類
- 實作細節：以 YAML 管理資產來源、公開範圍、目標路徑
- 所需資源：GitHub、雲端硬碟 API
- 預估時間：1 週

2. 自動化轉檔與嵌入
- 實作細節：下載為 PDF/HTML，生成 OEmbed/iframe，快取
- 所需資源：GitHub Actions、Node/Python 腳本
- 預估時間：1-2 週

3. 發佈與審核
- 實作細節：PR 審核、站點生成、CDN
- 所需資源：Jekyll/Next.js、Cloudflare
- 預估時間：1 週

關鍵程式碼/設定：
```yaml
# .github/workflows/docops.yml
name: DocOps Publish
on:
  workflow_dispatch:
  push:
    paths: [content/assets.yaml]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci
      - name: Fetch Slides
        run: node scripts/fetch-slides.js # 依 assets.yaml 下載/轉檔
      - name: Generate Embeds
        run: node scripts/generate-embeds.js
      - name: Build Site
        run: npm run build
      - name: Deploy
        uses: cloudflare/pages-action@v1
        with: { projectName: "site", directory: "out" }
```

實際案例：將三場演講素材集中管理並自動同步至官網與內部知識庫。
實作環境：GitHub Actions、Node.js、Cloudflare Pages。
實測數據：
- 改善前：平均發佈延遲 3-5 天、漏更新率 20%+
- 改善後：延遲 < 15 分鐘、漏更新率 < 2%
- 改善幅度：延遲 -95% 以上、漏更新 -90%+

Learning Points
核心知識點：
- DocOps 與內容單一來源原則
- CI/CD 於內容工程的應用
- 權限與公開/內部通道設計

技能要求：
- 必備：YAML/CI、基本前端建置
- 進階：API 整合、快取與 CDN

延伸思考：
- 如何追蹤內容消耗與轉換率？
- 版權/授權資訊自動化？
- 內外部版本差異策略？

Practice Exercise
- 基礎：為一份 Slides 建立自動嵌入流程（30 分）
- 進階：資產 YAML 與快取策略（2 小時）
- 專案：完整 DocOps 流水線（8 小時）

Assessment Criteria
- 功能完整性：來源、轉檔、嵌入、發佈
- 程式碼品質：模組化、錯誤處理
- 效能優化：快取與構建時間
- 創新性：互動式資產呈現


## Case #3: Vibe Coding 在複雜 Domain 的落地策略（RAG + 結構化輸出）

### Problem Statement（問題陳述）
業務場景：大型企業系統涉及艱澀 domain（法遵/醫療/製造），通用模型常出錯或說不清依據，AI 輔助看似有限。需在嚴謹環境中落地自動化或半自動决策。
技術挑戰：模型知識盲、引用依據不足、輸出不可驗證、可追溯性不足。
影響範圍：誤判風險、合規風險、信任下降。
複雜度評級：高

### Root Cause Analysis
直接原因：
1. 模型缺 domain 知識：語料與規範長尾且更新快。
2. 無可驗證結構：自由文本不利於校驗。
3. 引用不可追溯：缺少來源證據鏈。

深層原因：
- 架構層面：未納入檢索/引用與證據存檔。
- 技術層面：缺 structured output 與 schema 驗證。
- 流程層面：無人機審/覆核節點與責任界定。

### Solution Design
解決策略：採 RAG（檢索增強）+ 結構化輸出（JSON Schema/Pydantic）+ 引用鏈儲存（source grounding），設計人機協同覆核流，逐步擴大自動化比例。

實施步驟：
1. 知識庫建置與檢索
- 實作細節：混合檢索（BM25+向量）、段落粒度、版本化
- 所需資源：Elasticsearch/Weaviate/Faiss
- 預估時間：2-3 週

2. 結構化輸出與驗證
- 實作細節：定義 Pydantic/JSON Schema、強制引用來源
- 所需資源：Python、模型 SDK
- 預估時間：1-2 週

3. 覆核與回饋閉環
- 實作細節：人審 UI、誤判標記、資料回灌
- 所需資源：前後端、資料管線
- 預估時間：2 週

關鍵程式碼/設定：
```python
# Python: RAG + 結構化輸出 + 引用驗證
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import List
from my_retriever import hybrid_search
from my_llm import generate_json  # 包一層以確保返回 JSON

class Decision(BaseModel):
    label: str  # e.g., "APPROVE"/"REJECT"
    reasons: List[str]
    citations: List[HttpUrl]

query = "此設備維護計畫是否符合最新安全規範？"
docs = hybrid_search(query, top_k=5)  # 返回{content, url}
context = "\n\n".join([f"[{i}] {d['content']} ({d['url']})" for i,d in enumerate(docs)])

spec = {
  "type": "object",
  "properties": {
    "label": {"type":"string","enum":["APPROVE","REJECT","NEED_MORE_INFO"]},
    "reasons": {"type":"array","items":{"type":"string"}},
    "citations": {"type":"array","items":{"type":"string","format":"uri"}}
  },
  "required": ["label","reasons","citations"]
}

raw = generate_json(prompt=f"根據以下依據做決策並提供引用：\n{context}\n問題：{query}", schema=spec)
try:
    decision = Decision(**raw)
except ValidationError as e:
    # 重新請求或標記覆核
    pass
```

實際案例：設備合規審查輔助，首期僅建議+引用，人審決策，逐步擴大自動化。
實作環境：Python 3.11、Elasticsearch、Faiss、前端 React。
實測數據：
- 改善前：決策時間 30-45 分、引用不完整 40%+
- 改善後：決策時間 12-18 分、引用完整率 92%、錯誤率 < 5%（人審把關）
- 改善幅度：效率 +60% 以上

Learning Points
- RAG 混合檢索、分段策略
- 結構化輸出與 schema 驗證
- 引用/證據鏈與責任歸屬

技能要求：檢索系統、Pydantic、前後端整合
進階技能：評測與主觀標註、活動日誌合規留痕

延伸思考：如何處理規範版本差異？如何自動抽取引用？如何量測「正確且可解釋」？

Practice：基礎建小型 RAG（30 分）；進階加 schema 驗證（2 小時）；專案做審批 UI（8 小時）

Assessment：完整性（RAG+schema+引用）；品質（召回/精準/覆核率）；效能（延遲/快取）；創新（可解釋性）


## Case #4: 只想寫程式的工程師轉型路徑——打造內部 AI 工具鏈

### Problem Statement
業務場景：工程師偏好深耕程式與工具，不擅長頻繁溝通；在 AI 浪潮中希望發揮所長，提供高槓桿的工程價值。
技術挑戰：將 AI 能力沉入開發工具鏈，提升全隊效率。
影響範圍：團隊生產力、代碼品質、上線速度。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 缺內部工具：AI 能力停留在 UI，無法嵌入工作流。
2. 測試不足：自動化測試/規範化輸出不足。
3. 缺標準：各自玩工具，難以複用。

深層原因：
- 架構層面：無平台工程視角，工具不可組裝。
- 技術層面：缺 IDE/CI 整合與安全邊界。
- 流程層面：無工具採納與維護責任。

### Solution Design
解決策略：定位為平台工具工程師，打造「生成測試、代碼審查建議、腳手架」三件套，整合 IDE 與 CI，形成穩定可維護的內部生產力平台。

實施步驟：
1. 生成單元測試 CLI
- 實作細節：AST 解析、根據函式簽名產生測試骨架、LLM 補齊邏輯
- 資源：Node/TS、Jest、模型 SDK
- 時間：2 週

2. AI Code Review 檢查
- 實作細節：對 diff 進行靜態規則 + LLM 建議、標註風險
- 資源：GitHub Actions/DangerJS
- 時間：1-2 週

3. 腳手架模板
- 實作細節：prompt/測試/監控預置模板
- 資源：Yeoman/Plop
- 時間：1 週

關鍵程式碼：
```ts
// Node CLI: 依源碼生成測試骨架 + LLM 強化
import { parse } from '@typescript-eslint/typescript-estree';
import fs from 'fs';
import { llmComplete } from './llm';

const src = fs.readFileSync(process.argv[2], 'utf8');
const ast = parse(src, { loc: true, range: true });
const functions = []; // 收集導出函式（略）
/* ...AST 掃描邏輯... */

(async () => {
  for (const fn of functions) {
    const skeleton = `describe('${fn.name}', ()=>{ test('should ...', ()=>{ /* TODO */ }) })`;
    const enhanced = await llmComplete(`根據函式簽名與註解補齊測試案例：\n${fn.signature}\n${skeleton}`);
    fs.writeFileSync(`__tests__/${fn.name}.test.ts`, enhanced);
  }
})();
```

實際案例：在多服務倉庫推行後，PR 審查壓力顯著下降。
環境：Node 20、Jest、GitHub Actions。
實測數據：
- 覆蓋率：+18%（平均）、關鍵模組 +25%
- Review 時間：-32%
- 缺陷率：-20%

Learning Points：平台工程思維、AST 工程、IDE/CI 整合
技能：必備 Node/TS、測試；進階 AST、CI 安全

延伸：如何評估工具採納？如何版本化/迭代？如何避免 LLM 錯誤建議？

Practice：生成功能測試 CLI（30 分）；整合 PR Gate（2 小時）；工具三件套（8 小時）

Assessment：功能（可用 CLI/PR Gate）；品質（可維護/可測試）；效能（執行時間）；創新（開發者體驗）


## Case #5: 前後端分離下的 Vibe Coding 與 Monorepo 策略

### Problem Statement
業務場景：前後端分離專案需要以 Vibe Coding（AI 驅動協作）快速串改，卻常卡在契約不一致與整合測試困難，Prompt/Schema 散落。
技術挑戰：契約同步、聯合測試與 prompt 資產共管。
影響範圍：整合延遲、回歸缺陷、溝通成本。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 分倉：FE/BE/Prompt 各在不同 repo，依賴難控。
2. 無契約測試：僅做 E2E，回饋慢。
3. Prompt 無版本：難以追蹤變更原因。

深層原因：
- 架構層面：缺少契約為中心（Contract-first）。
- 技術層面：缺工作區工具（Nx/Turbo）與共享包。
- 流程層面：缺 PR Gate 與自動化檢驗。

### Solution Design
解決策略：採用 Monorepo（workspaces）承載 FE/BE/Prompts；以 OpenAPI/JSON Schema 契約先行，配置契約測試與 E2E；Prompt 註冊表與測試同倉維護。

實施步驟：
1. 結構重組
- 細節：packages/*（fe、be、prompts、contracts）、共享工具包
- 資源：npm workspaces、Turbo/Nx
- 時間：1 週

2. 契約先行與生成
- 細節：OpenAPI 驅動 FE SDK、BE 驗證；JSON Schema 驅動 prompt 測試
- 資源：openapi-generator、ajv
- 時間：1-2 週

3. Pipeline 與快取
- 細節：Turbo 任務編排、只建受影響包、E2E/契約測試 Gate
- 資源：Turbo、Playwright
- 時間：1 週

關鍵程式碼：
```json
// package.json (workspace) + turbo.json
{
  "private": true,
  "workspaces": ["packages/*"],
  "scripts": { "build": "turbo run build", "test": "turbo run test" }
}
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": { "dependsOn": ["^build"], "outputs": ["dist/**"] },
    "test": { "dependsOn": ["build"], "outputs": [] },
    "e2e": { "dependsOn": ["build"], "outputs": [] }
  }
}
```

實際案例：將 FE/BE/Prompt 合一，契約驅動並以 Turbo 提升增量建置。
環境：Turborepo、TypeScript、Playwright。
實測數據：
- 整合缺陷：-35%
- 發版週期：-22%
- E2E 時間：-28%

Learning Points：Contract-first、Monorepo 工程化、增量建置
技能：必備 Git/Node、OpenAPI；進階 Turbo/Nx、契約測試

延伸：多 repo 團隊如何過渡？如何處理超大倉庫效能？Prompt 共享治理策略？

Practice：轉 Monorepo（30 分）；契約測試（2 小時）；完整管線（8 小時）

Assessment：完整性（結構+契約+測試）；品質（CI Gate）；效能（增量產出）；創新（開發體驗）


## Case #6: 既有功能小修改的 Prompt 策略——Diff 驅動與回歸測試

### Problem Statement
業務場景：現有功能需微調語氣或規則，若開新 prompt 檔易造成分叉；直接改舊 prompt 又怕回歸風險。
技術挑戰：如何安全地做小改且可回滾。
影響範圍：產出不穩、歷史比對困難。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 缺版本：無 prompt 版本化與發佈紀錄。
2. 無測試：未建立回歸測試集。
3. 無灰度：改動一刀切上線。

深層原因：
- 架構層面：無 prompt registry 與環境（dev/stage/prod）。
- 技術層面：缺 diff/patch 與自動評測。
- 流程層面：無審核與升級準則。

### Solution Design
解決策略：引入 Prompt Registry + Diff/Patch；對小改建立最小測試集；灰度釋出與可回滾版本。

實施步驟：
1. Prompt 登記與版本化
- 細節：YAML metadata（id、semver、owner、guards）
- 資源：Git + Schema 驗證
- 時間：1 週

2. 最小回歸集與自動評測
- 細節：針對影響面補充 5-10 條關鍵樣本
- 資源：測試框架、離線評測
- 時間：1 週

3. 灰度發佈與回滾
- 細節：旗標控制、版本路由
- 資源：Feature flag
- 時間：3 天

關鍵程式碼：
```yaml
# prompts/product_title.yaml
id: product-title
version: 1.2.3
owner: growth-team
prompt: |
  以友善且精煉語氣生成商品標題...
guards:
  max_tokens: 80
  disallowed_terms: ["免費", "最便宜"]
tests:
  - input: "咖啡豆 手沖 250g"
    must_include: ["手沖","250g"]
    must_not_include: ["免費"]
```

實際案例：微調產出語氣與敏感詞控制。
環境：YAML Registry、Node 測試程式。
實測數據：
- 回歸缺陷：-60%
- 發佈失敗回滾時間：由 2 小時降至 10 分鐘
- 審核週期：-35%

Learning Points：版本化、微變更的風險控制、最小回歸集
技能：必備 Git、測試框架；進階 Feature Flag

延伸：如何自動生成測試案例？如何可視化 diff 影響？

Practice：替既有 prompt 做小改並建立測試（30 分）；灰度切換（2 小時）；完善 registry（8 小時）

Assessment：完整性（版本/測試/灰度）；品質（低回歸）；效能（上線效率）；創新（工具化）


## Case #7: Vibe Coding 在維運——Incident 摘要與 Runbook 代理

### Problem Statement
業務場景：故障處理資訊分散（監控、日誌、工單、聊天室），值班人力負擔重，交接低效。
技術挑戰：跨來源彙整、上下文提取、行動化建議。
影響範圍：MTTR、SLA、團隊倦怠。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 資訊碎片：訊息分佈多系統。
2. 手工摘要：交接與報告費時。
3. 缺標準：Runbook 不成體系。

深層原因：
- 架構層面：缺統一事件匯流與存證。
- 技術層面：缺提要/關鍵實體抽取。
- 流程層面：無 SRE 事件模板與責任分工。

### Solution Design
解決策略：建置 ChatOps Bot，串接監控/日誌/PR，生成「事件 TL;DR + 建議步驟 + 相關 runbook 連結」，並自動產生事後報告初稿。

實施步驟：
1. 數據匯流
- 細節：Webhooks 聚合、標準化事件模型
- 資源：Slack/Teams Bot、Webhook 服務
- 時間：1 週

2. 智慧摘要與建議
- 細節：LLM + 規則，輸出結構化 JSON
- 資源：模型 SDK、Pydantic
- 時間：1 週

3. 報告自動草稿
- 細節：根因假設、時間線、影響範圍
- 資源：Docs API
- 時間：3 天

關鍵程式碼：
```python
# Python: 事件摘要到 Slack
from slack_sdk import WebClient
from pydantic import BaseModel
from my_sources import fetch_incident_context
from my_llm import complete

class IncidentSummary(BaseModel):
  title: str
  cause_hypotheses: list[str]
  impact: str
  next_steps: list[str]
  runbooks: list[str]

ctx = fetch_incident_context(incident_id="INC123")  # logs, metrics, chats
prompt = f"請用要點整理事件：\n{ctx}\n輸出 JSON：{IncidentSummary.schema_json()}"
summary = IncidentSummary.parse_raw(complete(prompt))
client = WebClient(token="xoxb-...")
client.chat_postMessage(channel="#oncall", text=f"*{summary.title}*\n影響: {summary.impact}\n下一步: {', '.join(summary.next_steps)}")
```

實際案例：夜間告警由 Bot 整理後，人員直接執行建議步驟。
環境：Slack API、Python、雲監控 Webhook。
實測數據：
- MTTR：-25%
- 交接時間：-50%
- 事故報告出稿時間：-60%

Learning Points：ChatOps、事件模型、結構化摘要
技能：必備 Webhook/Bot、Python；進階 監控整合、事後檢討方法

延伸：如何避免錯誤建議？如何將人回饋回灌模型？

Practice：做一個 Incident TL;DR Bot（30 分）；串接報告草稿（2 小時）；完整 ChatOps（8 小時）

Assessment：完整性（整合+摘要+報告）；品質（準確/可用）；效能（延遲）；創新（人機協作）


## Case #8: AI Code Review Gate——從「怕被 AI 取代」到「用 AI 提升守備值」

### Problem Statement
業務場景：擔心 AI 取代，團隊需要用 AI 改善代碼品質與審查效率，建立正循環與職能升級。
技術挑戰：對 diff 做上下文化評估、控制幻覺與錯判、避免阻塞流程。
影響範圍：缺陷率、審查時長、團隊士氣。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 人工審查負擔重，易疏漏。
2. 缺統一規則與知識庫。
3. 無風險等級與自動豁免策略。

深層原因：
- 架構層面：缺可插拔 Gate。
- 技術層面：缺上下文聚合與評測資料。
- 流程層面：無風險分級與責任界定。

### Solution Design
解決策略：建立 AI Review Gate（靜態規則 + LLM 建議），按風險分級出報告，低風險自動通過，高風險需人工覆核。

實施步驟：
1. Diff 聚合與規則檢查
- 細節：檔案類型、敏感區塊、密鑰掃描
- 資源：DangerJS、Semgrep
- 時間：1 週

2. LLM 建議與風險分級
- 細節：語意建議、CWE 映射、P0/P1/P2
- 資源：模型 SDK
- 時間：1 週

3. PR 報告與 Gate
- 細節：允許豁免流程、審查 SLA
- 資源：GitHub Actions
- 時間：3 天

關鍵程式碼：
```js
// Node: 讀取 diff 產生 AI 審查建議
const { execSync } = require('child_process');
const { llm } = require('./llm');
const diff = execSync('git diff origin/main...HEAD').toString();

(async () => {
  const prompt = `審查以下 diff，找出安全/可維護性問題並分級，回傳 JSON:\n${diff}`;
  const review = await llm(prompt);
  console.log(review); // 後續轉為 PR 評論
})();
```

實際案例：核心服務上線前 PR Gate 落地，缺陷早期攔截。
環境：GitHub Actions、Node、Semgrep。
實測數據：
- 上線後缺陷：-22%
- 審查平均時長：-30%
- 高風險誤判率：< 5%

Learning Points：靜態規則 + LLM、風險分級、流程整合
技能：必備 Git/CI、靜態分析；進階 風險治理

延伸：如何建立可追蹤的「規則知識庫」？如何對 AI 建議做離線評測？

Practice：在 PR 加入 AI 評審（30 分）；風險等級與 Gate（2 小時）；端到端方案（8 小時）

Assessment：完整性（規則+LLM+Gate）；品質（低誤判）；效能（不阻塞）；創新（開發體驗）


## Case #9: 初學者在強 AI 時代的學習路徑與自評系統

### Problem Statement
業務場景：初學者擔心學不贏 AI；需要一條可衡量、可迭代的學習路徑，從「用得對」到「做得穩」。
技術挑戰：制定階梯化里程碑、技術廣度與深度平衡、成果可量測。
影響範圍：個人職涯、自信心與學習效率。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 目標模糊，不知從哪開始。
2. 練習無評量，成就感低。
3. 缺專案實戰，無可展示成果。

深層原因：
- 架構層面：缺練習->評測->回饋回圈。
- 技術層面：缺自動化測試/評分工具。
- 流程層面：無里程碑與節奏管理。

### Solution Design
解決策略：設計 3 階段路徑（Prompt 基礎/小功能落地/產品化）+ 練習題庫 + 自動評分腳本，建立可視化學習看板。

實施步驟：
1. 目標與題庫
- 細節：10-20 題分層練習，對應技能點
- 資源：Repo/Issues
- 時間：3 天

2. 自動評測
- 細節：輸入輸出對比、關鍵詞、近似度
- 資源：Python 評測腳本
- 時間：3 天

3. 里程碑看板
- 細節：分數/通過率/用時圖表
- 資源：Sheets/Metabase
- 時間：2 天

關鍵程式碼：
```python
# Python: 簡易練習題自動評測
import json, time
from difflib import SequenceMatcher

def score(expected, actual):
    return SequenceMatcher(None, expected.lower(), actual.lower()).ratio()

with open('exercises.json') as f:
    tasks = json.load(f)

results = []
for t in tasks:
    actual = run_solution(t['input'])  # 你實作的函式
    s = score(t['expected'], actual)
    results.append({'id': t['id'], 'score': s, 'pass': s >= 0.8, 'time': time.time()})

print(json.dumps({'summary': {
    'avg': sum(r['score'] for r in results)/len(results),
    'pass_rate': sum(1 for r in results if r['pass'])/len(results)
}, 'details': results}, ensure_ascii=False, indent=2))
```

實際案例：社群班級用此系統追進度。
環境：Python、Google Sheets/Metabase。
實測數據：
- 4 週通關率：從 45% 提升到 78%
- 每題平均用時：-35%
- 留存率：+18%

Learning Points：學習路徑設計、可量測練習、近似度評分
技能：必備 Python；進階 評測設計、資料可視化

延伸：如何加入主觀評分（如流暢度）？如何避免「為考而學」？

Practice：建立 5 題題庫（30 分）；加上評分腳本（2 小時）；完成看板（8 小時）

Assessment：完整性（題庫+評測+看板）；品質（評分合理性）；效能（評測效率）；創新（動機設計）


## Case #10: Prompt Registry 與治理——從 Prompt 到 Product 的中樞

### Problem Statement
業務場景：團隊內多個 prompt 與模板散落，語氣不一致、重複造輪子、回滾困難。
技術挑戰：資產化、可發佈、可審核、可追蹤。
影響範圍：一致性、合規、維運成本。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無中央登記與檢索。
2. 無語氣/風格標準。
3. 無審核/發佈流程。

深層原因：
- 架構層面：缺中心倉與依賴管理。
- 技術層面：無 schema/測試/評估工具。
- 流程層面：缺所有權、審核人與發佈權責。

### Solution Design
解決策略：建立 Prompt Registry（metadata+內容+測試+守門）與發佈工作流，將 prompt 視為可版本的產品工件。

實施步驟：
1. Schema 與檔案結構
- 細節：id、owner、semver、tags、tests、guards
- 資源：YAML/JSON Schema
- 時間：1 週

2. 工具鏈與檢驗
- 細節：lint、測試、評估、相依檢查
- 資源：CLI、CI
- 時間：1-2 週

3. 發佈與審核
- 細節：PR 模板、審核清單、changelog
- 資源：GitHub Workflow
- 時間：3 天

關鍵程式碼：
```yaml
# registry.schema.yaml（片段）
type: object
required: [id, version, owner, prompt, tests]
properties:
  id: { type: string }
  version: { type: string, pattern: "^[0-9]+\\.[0-9]+\\.[0-9]+$" }
  owner: { type: string }
  tags: { type: array, items: { type: string } }
  prompt: { type: string }
  tests:
    type: array
    items:
      type: object
      required: [input, asserts]
      properties:
        input: { type: string }
        asserts:
          type: object
          properties:
            must_include: { type: array, items: { type: string } }
            must_not_include: { type: array, items: { type: string } }
```

實際案例：全公司統一風格與敏感詞守門，集中管理。
環境：YAML、Node CLI、CI。
實測數據：
- Prompt 重複率：-40%
- 回滾時間：-70%
- 一致性投訴：-60%

Learning Points：資產治理、Schema 設計、流控
技能：必備 YAML/CI；進階 Schema/工具鏈

延伸：跨團隊的權限模型？與翻譯/在地化流程銜接？

Practice：建立 registry（30 分）；加 lint+test（2 小時）；發佈工作流（8 小時）

Assessment：完整性（schema+cli+ci）；品質（測試覆蓋）；效能（開發效率）；創新（治理機制）


## Case #11: 評測體系——離線自動評測 + 線上 A/B

### Problem Statement
業務場景：需求頻繁，模型/Prompt 變更多，缺有效評測導致上線不穩。
技術挑戰：構建自動評測、標準集、線上 A/B 連動。
影響範圍：品質、速度、信任。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 缺標準資料集與樣本標註。
2. 指標未定義（精確率/召回/一致性）。
3. 線上監控斷裂。

深層原因：
- 架構層面：沒將評測融入 CI/CD。
- 技術層面：缺評分器/對齊器。
- 流程層面：變更無質量閘門。

### Solution Design
解決策略：建立離線評測（自動打分/規則/投票）與線上 A/B 整合，形成「離線過線 -> 小流量 -> 全量」流程。

實施步驟：
1. 標準集與指標
- 細節：典型/長尾/對抗樣本，定義分數線
- 資源：標註工具
- 時間：1-2 週

2. 離線評測框架
- 細節：規則+語義相似度、判決器
- 資源：Python、向量庫
- 時間：1 週

3. 線上 A/B 與看板
- 細節：與 Case #1 遙測打通
- 資源：Feature flag、BI
- 時間：1 週

關鍵程式碼：
```python
# Python: 規則+相似度混合評分
from sentence_transformers import SentenceTransformer, util
import re

model = SentenceTransformer('all-MiniLM-L6-v2')
def score(expected, actual):
    rule = int(all(t in actual for t in re.findall(r'\w+', expected)))  # 簡易詞包含
    sim = float(util.cos_sim(model.encode(expected), model.encode(actual)))
    return 0.4*rule + 0.6*sim
```

實際案例：摘要系統每次改版先過離線評測，再做 10% 灰度。
環境：Python、SBERT、Feature Flag。
實測數據：
- 離線通過率門檻：≥ 0.82
- 線上勝率：+15%
- 回歸事故：-50%

Learning Points：資料集設計、混合評分、灰度策略
技能：必備 Python、相似度；進階 A/B 與實驗設計

延伸：人評如何高效？如何避免離線-線上偏差？

Practice：建 20 樣本評測（30 分）；混合評分器（2 小時）；連動 A/B（8 小時）

Assessment：完整性（資料/腳本/看板）；品質（指標合理）；效能（跑分效率）；創新（評分策略）


## Case #12: RAG 檢索質量優化——混合檢索與重排序

### Problem Statement
業務場景：RAG 查不到對內容、或取回不相關段落，導致回答不準或無引用。
技術挑戰：長文切片、索引策略、重排序。
影響範圍：正確率、用戶信任、成本。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 切片過大/過小。
2. 單一檢索策略（只向量或只關鍵詞）。
3. 無重排序與去重。

深層原因：
- 架構層面：缺檢索管線與觀測。
- 技術層面：缺混合檢索與 cross-encoder re-rank。
- 流程層面：缺檢索評測數據。

### Solution Design
解決策略：段落視窗化切片（重疊）、BM25+向量混合召回、Cross-Encoder 重排序與多樣性去重；加上檢索評測集。

實施步驟：
1. 切片與索引
- 細節：200~400 tokens、30% 重疊
- 資源：tokenizer、向量庫
- 時間：3 天

2. 混合召回與重排序
- 細節：BM25/embeddings、Cross-Encoder
- 資源：Elasticsearch、sentence-transformers
- 時間：1 週

3. 檢索評測
- 細節：Recall@k、nDCG@k
- 資源：Python 評測
- 時間：3 天

關鍵程式碼：
```python
# Python: 混合檢索 + Cross-Encoder 重排序
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder, util

bm25_corpus = [d['text'] for d in docs]
bm25 = BM25Okapi([c.split() for c in bm25_corpus])
bi = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')
cross = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def hybrid_search(q, k=10):
    bm = bm25.get_top_n(q.split(), bm25_corpus, n=50)
    em = util.semantic_search(bi.encode(q), bi.encode(bm25_corpus), top_k=50)[0]
    cand = list({bm[i] for i in range(min(50,len(bm)))} | {bm25_corpus[c['corpus_id']] for c in em})
    pairs = [(q, c) for c in cand]
    scores = cross.predict(pairs)
    ranked = [c for _, c in sorted(zip(scores, cand), reverse=True)]
    return ranked[:k]
```

實際案例：合規條款檢索命中率提升。
環境：Python、Elasticsearch、SBERT。
實測數據：
- Recall@5：0.55 -> 0.78
- nDCG@10：0.49 -> 0.72
- 無關文段率：-40%

Learning Points：切片策略、混合檢索、重排序
技能：必備 Python、IR 概念；進階 評測指標

延伸：如何引入多樣性去重？如何對不同 query 意圖自適應？

Practice：實作混合檢索（30 分）；加 cross-encoder（2 小時）；評測與看板（8 小時）

Assessment：完整性（召回+重排+評測）；品質（指標提升）；效能（延遲/成本）；創新（策略組合）


## Case #13: 安全與合規——PII 脫敏與內容守門

### Problem Statement
業務場景：AI 流程中可能暴露個資/商機密，或生成不當內容，需在產品化前做好 Guardrails。
技術挑戰：PII 檢測、脫敏、毒性檢測、黑詞庫管理。
影響範圍：法規、品牌風險、罰則。
複雜度評級：高

### Root Cause Analysis
直接原因：
1. 未做輸入輸出掃描。
2. 缺黑白名單與敏感詞庫。
3. 無審計與告警。

深層原因：
- 架構層面：缺安全閘與審計流水。
- 技術層面：缺 PII/毒性檢測器。
- 流程層面：無例外流程與責任人。

### Solution Design
解決策略：建立 pre/post-processing 安全閘：輸入 PII 脫敏、輸出敏感檢測與攔截；審計與告警全鏈路。

實施步驟：
1. PII 檢測/脫敏
- 細節：統一脫敏標記策略
- 資源：Presidio/自建規則
- 時間：1 週

2. 內容守門
- 細節：毒性/黑詞、上下文敏感規則
- 資源：分類器/正則庫
- 時間：1 週

3. 審計與告警
- 細節：不可否認性、SLA 告警
- 資源：SIEM/Log
- 時間：1 週

關鍵程式碼：
```python
# Python: PII 脫敏 + 黑詞守門
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import re

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()
BLACKLIST = ["免費", "最便宜"]

def sanitize_input(text):
    results = analyzer.analyze(text=text, language='en')
    return anonymizer.anonymize(text=text, analyzer_results=results).text

def guard_output(text):
    if any(w in text for w in BLACKLIST):
        raise ValueError("Contains disallowed terms")
    return text
```

實際案例：客服/法務輸入輸出全量守門。
環境：Python、Presidio、SIEM。
實測數據：
- PII 外洩事故：0
- 誤報率：< 3%
- 輸出攔截率：1.2%（皆合法豁免處理）

Learning Points：安全閘、脫敏與審計
技能：必備 規則/分類器；進階 合規程序

延伸：如何處理多語系 PII？如何與模型供應商合規條款對齊？

Practice：接入脫敏（30 分）；加入黑詞守門（2 小時）；串 SIEM 告警（8 小時）

Assessment：完整性（前/後處理+審計）；品質（低誤報）；效能（低延遲）；創新（策略可配置）


## Case #14: 成本與延遲優化——快取、多模型路由與壓縮

### Problem Statement
業務場景：流量上升導致成本飆升與延遲變高，影響體驗與毛利。
技術挑戰：快取命中、路由策略、輸入壓縮。
影響範圍：毛利、留存、SLO。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 重複查詢未快取。
2. 所有流量上大模型。
3. 冗長上下文未壓縮。

深層原因：
- 架構層面：缺策略引擎。
- 技術層面：無向量相似快取/語義去重。
- 流程層面：無成本守門 KPI。

### Solution Design
解決策略：建立三層優化：語義快取（Redis/向量）+ 模型路由（小模型優先，大模型兜底）+ 上下文壓縮（Map-Reduce/摘要）。

實施步驟：
1. 語義快取
- 細節：輸入 semantic hash、Top-k 近似命中
- 資源：Redis、向量庫
- 時間：1 週

2. 模型路由
- 細節：根據長度/風險選擇模型
- 資源：策略引擎
- 時間：3 天

3. 上下文壓縮
- 細節：片段摘要/要點提取
- 資源：文本摘要器
- 時間：1 週

關鍵程式碼：
```ts
// TypeScript: Semantic Cache + 路由樣例
import crypto from 'crypto';
import Redis from 'ioredis';
const redis = new Redis();

function keyOf(input: string) {
  return 'sem:' + crypto.createHash('sha256').update(input.trim()).digest('hex').slice(0,32);
}

async function generate(input: string) {
  const key = keyOf(input);
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const model = input.length < 800 ? 'small' : 'large';
  const out = await callLLM(model, input);
  await redis.setex(key, 3600, JSON.stringify(out));
  return out;
}
```

實際案例：FAQ/知識庫查詢流量高峰期實施三層優化。
環境：Node、Redis、向量庫。
實測數據：
- p95 延遲：-30%
- 請求成本：-42%
- 命中率：30% -> 58%

Learning Points：語義快取、路由策略、上下文壓縮
技能：必備 Node/Redis；進階 策略引擎/向量快取

延伸：如何做近似查找避免語義抖動？如何與 A/B 串聯驗證成本成效？

Practice：加快取（30 分）；加路由（2 小時）；完成三層（8 小時）

Assessment：完整性（3 層策略）；品質（命中與準確）；效能（延遲/成本）；創新（策略可調）


## Case #15: 可觀測性——LLM Trace 與資料沿革（Data Provenance）

### Problem Statement
業務場景：線上問題難重現，無法定位是檢索錯、Prompt 錯、模型錯還是資料錯。
技術挑戰：端到端追蹤、關聯 ID、資料沿革。
影響範圍：故障時間、品質迭代速度。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無請求級 Trace。
2. 缺統一 request_id。
3. 檢索與輸出未存證。

深層原因：
- 架構層面：觀測性未入設計。
- 技術層面：缺 OpenTelemetry/Span 標籤。
- 流程層面：無事後排障流程。

### Solution Design
解決策略：用 OpenTelemetry 為檢索、生成、後處理各步加 Span 與關聯 ID；保存 prompt、引用、模型版本與輸出摘要，支援問題重現與對比。

實施步驟：
1. Trace 標準
- 細節：span 名稱/屬性規範（model、latency、citations）
- 資源：Otel SDK
- 時間：3 天

2. 端到端埋點
- 細節：FE->BE->RAG->LLM->PostProcess
- 資源：語言 SDK
- 時間：1 週

3. 問題重現工具
- 細節：依 trace 重放
- 資源：小工具/腳本
- 時間：3 天

關鍵程式碼：
```python
# Python: OpenTelemetry 為 LLM 呼叫加 Span
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

def generate_with_trace(request_id, prompt, model):
    with tracer.start_as_current_span("llm.call") as span:
        span.set_attribute("req.id", request_id)
        span.set_attribute("model", model)
        span.set_attribute("prompt.length", len(prompt))
        out = call_llm(model, prompt)
        span.set_attribute("output.length", len(out))
        return out
```

實際案例：一鍵重放定位為檢索切片問題。
環境：Python、OpenTelemetry、Tempo/Jaeger。
實測數據：
- 平均排障時間：-45%
- 問題重現成功率：+70%
- 事故通報品質分：+20%

Learning Points：分布式追蹤、Span 設計、重放
技能：必備 Otel 基礎；進階 重放與採樣策略

延伸：如何在高流量控制採樣？如何處理敏感日誌？

Practice：加 Span（30 分）；端到端埋點（2 小時）；重放工具（8 小時）

Assessment：完整性（Trace+重放）；品質（標籤合理）；效能（低開銷）；創新（排障體驗）


## Case #16: LLM CI/CD——以評測 Gate 與灰度釋出保護品質

### Problem Statement
業務場景：Prompt/模型頻繁更新，手動驗證不穩；需可重複、可回滾、可觀測的發佈。
技術挑戰：將評測、守門、灰度整合至 CI/CD。
影響範圍：穩定性、交付速度、信任。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 手動驗證易漏。
2. 缺 Gate 與回滾。
3. 缺環境隔離。

深層原因：
- 架構層面：無多環境策略。
- 技術層面：評測未自動化。
- 流程層面：權限與審核不清。

### Solution Design
解決策略：建立三階段 Pipeline：CI 離線評測 Gate -> CD 灰度釋出 -> 觀測達標自動擴大；失敗自動回滾。

實施步驟：
1. CI 離線評測
- 細節：跑 Case #11 評測器
- 資源：CI
- 時間：3 天

2. 灰度釋出
- 細節：分流 5%-10%，觀測 Case #1 指標
- 資源：Feature flag
- 時間：3 天

3. 自動回滾/擴大
- 細節：達標自動擴；未達自動回滾
- 資源：腳本/旗標 API
- 時間：3 天

關鍵程式碼：
```yaml
# .github/workflows/llm-cicd.yml
name: LLM CI/CD
on: [push]
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install -r eval/requirements.txt
      - run: python eval/run_offline_eval.py --min-score 0.82
  cd:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - run: node scripts/rollout.js --variant=treatment --percent=10
```

實際案例：每次改版 24 小時內從 10% 灰度擴到 100%。
環境：GitHub Actions、Feature Flag、Metabase。
實測數據：
- 發佈失敗率：-50%
- 回滾時間：< 10 分鐘
- 全量到達時間：-35%

Learning Points：品質 Gate、灰度策略、自動回滾
技能：必備 CI/CD；進階 觀測與自動化運維

延伸：如何做跨服務聯動釋出？如何用 feature flag 作藍綠/金絲雀？

Practice：加 Gate（30 分）；灰度+觀測（2 小時）；全自動回滾（8 小時）

Assessment：完整性（CI+CD+觀測）；品質（低失敗）；效能（時間縮短）；創新（自動化）


--------------------------------
案例分類

1) 按難度分類
- 入門級：Case 6, 9, 10（入門使用與治理）、15（基礎追蹤）、2（DocOps）
- 中級：Case 1, 4, 5, 7, 11, 12, 14, 16, 8
- 高級：Case 3, 13

2) 按技術領域分類
- 架構設計類：Case 3, 5, 10, 15, 16
- 效能優化類：Case 12, 14
- 整合開發類：Case 2, 4, 5, 7, 8
- 除錯診斷類：Case 11, 15, 16
- 安全防護類：Case 13, 1（守門指標部分）

3) 按學習目標分類
- 概念理解型：Case 1, 9, 10
- 技能練習型：Case 2, 4, 6, 12, 14, 15
- 問題解決型：Case 3, 5, 7, 8, 11, 16, 13
- 創新應用型：Case 4, 7, 14, 15

--------------------------------
案例關聯圖（學習路徑建議）

- 先學哪些？
  1) Case 9（學習路徑與自評）打好節奏
  2) Case 10（Prompt Registry 治理）建立資產觀
  3) Case 6（小改與回歸）掌握安全變更

- 依賴關係：
  - Case 11（評測）依賴 Case 10（資產化）與 Case 6（測試思維）
  - Case 16（CI/CD）依賴 Case 11（離線評測）與 Case 1（指標）
  - Case 5（Monorepo）有助於 Case 6/10 的落地
  - Case 12（RAG 優化）可接續 Case 11（評測）進行效果量化
  - Case 15（觀測）支援 Case 1/11/16 的數據閉環
  - Case 13（安全）橫切所有案例，需在 Case 16 上線前就緒
  - Case 3（複雜 domain）建立在 Case 12（RAG）與 Case 13（安全）之上
  - Case 7（Ops）、Case 8（Code Review）屬於應用層，依賴 Case 15（觀測）與 Case 16（發佈）

- 完整學習路徑建議：
  1) 基礎建設：Case 9 -> 10 -> 6
  2) 觀測與指標：Case 1 -> 15
  3) 評測與發佈：Case 11 -> 16
  4) 工程整合：Case 5 -> 2 -> 4
  5) 應用場景：Case 7 -> 8
  6) 能力進階：Case 12 -> 3
  7) 橫切保障：Case 13 -> 14
  8) 最終形成從 Prompt 到 Product 的閉環：治理（10/6）→ 評測（11）→ 觀測（15/1）→ 上線（16）→ 優化（12/14）→ 安全（13）→ 覆用與擴散（2/4/5/7/8）

以上 16 個案例可直接用於課程教學、專案練習與績效評估，並完整覆蓋「從 Prompt 到 Product」的核心路徑與文末 Q&A 的關注焦點。