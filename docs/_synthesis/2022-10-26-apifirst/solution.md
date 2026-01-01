---
layout: synthesis
title: "架構師觀點 - API First 的開發策略"
synthesis_type: solution
source_post: /2022/10/26/apifirst/
redirect_from:
  - /2022/10/26/apifirst/solution/
postid: 2022-10-26-apifirst
---
{% raw %}

以下內容根據原文「架構師觀點 - API First 的開發策略」逐一萃取、重構，產出 18 個具教學價值的「問題解決案例」。每個案例均涵蓋問題、根因、解法、實施步驟、關鍵設定/程式碼、成效與學習要點等，供實戰教學、專案練習與能力評估之用。

## Case #1: 設計先行的 API 合約，讓需求在寫 code 前對齊

### Problem Statement（問題陳述）
- 業務場景：產品團隊習慣以 UI/APP 開發為先，API 作為附帶產出，導致需求變動時 API 規格頻繁修改，跨團隊協作成本高。希望以 API First 將「合約」放在最前，讓利益關係人可在任何程式碼產生前就對齊需求與使用行為，減少返工與溝通成本。
- 技術挑戰：缺乏一致的 API 規格與審查機制；無法在前端/後端同步開發；沒有可用的 Mock 伺服器進行早期驗證。
- 影響範圍：研發時程、跨團隊協作、需求返工率、對外整合速度。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. UI/APP 驅動開發，API 成為事後重構產物，難以穩定再利用。
  2. 缺少「合約」與「審查」流程，無法在程式碼前先獲得回饋。
  3. 無法早期驗證設計（缺 Mock），上線後才暴露問題導致返工。
- 深層原因：
  - 架構層面：介面/合約未被視為產品的第一公民。
  - 技術層面：未採用 OpenAPI/JSON Schema 等規格與工具鏈。
  - 流程層面：缺少設計審查、樣例與演練流程，沒有 DX 指標。

### Solution Design（解決方案設計）
- 解決策略：採用 Design-First 工作流，以 OpenAPI3/JSON Schema 定義介面合約；建立審查與 Mock 機制讓 Stakeholders 在寫任何程式前就能試用與回饋；以此合約為唯一真相，同步驅動前端/後端與測試工作。

- 實施步驟：
  1. 定義領域與使用者旅程
     - 實作細節：用例、資源模型、狀態與操作草圖
     - 所需資源：Miro/Excalidraw、事件風暴
     - 預估時間：1-2 天
  2. 撰寫 OpenAPI 合約與範例
     - 實作細節：Resource 命名、錯誤模型、範例 payload
     - 所需資源：OpenAPI 3.1、Stoplight/Swagger Editor
     - 預估時間：1-3 天
  3. 啟動 Mock 與設計審查
     - 實作細節：Mock server（Prism）、邀請 PO/前後端試走流程
     - 所需資源：Prism、Redoc/Elements 頁面
     - 預估時間：0.5-1 天
  4. 確認合約凍結與版本標記
     - 實作細節：打 tag（v1.0.0），建立更版規則
     - 所需資源：Git、語意化版本規則
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# openapi.yaml（節錄）
openapi: 3.1.0
info:
  title: Orders API
  version: 1.0.0
paths:
  /orders:
    post:
      summary: Create an order
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateOrderRequest'
      responses:
        '201':
          description: Created
          headers:
            Location:
              schema: { type: string }
              description: URL of the created order
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Order' }
components:
  schemas:
    CreateOrderRequest:
      type: object
      required: [items]
      properties:
        items:
          type: array
          items:
            type: object
            required: [sku, qty]
            properties:
              sku: { type: string }
              qty: { type: integer, minimum: 1 }
    Order:
      type: object
      properties:
        id: { type: string }
        status: { type: string, enum: [PENDING, CONFIRMED, CANCELED] }
```

- 實際案例：原文強調「先定義 API 合約，於寫任何 code 前拿合約與關係人回饋」，並推崇將 API 視為 contract。
- 實作環境：OpenAPI 3.1 + Stoplight/Prism + Redoc；Git + CI。
- 實測數據：
  - 改善前：需求頻繁返工；前後端難以同步；整合期長。
  - 改善後：在設計階段即可回饋；前後端可並行；整合缺陷下降。
  - 改善幅度：未提供數值（定性成效：對齊速度與穩定度顯著提升）。

- Learning Points（學習要點）
  - 核心知識點：
    - Design-First 與 API as Contract
    - OpenAPI/JSON Schema 的重要性
    - Mock 驗證與利益關係人回饋
  - 技能要求：
    - 必備技能：API 規格撰寫、JSON Schema
    - 進階技能：領域建模、設計審查與工作坊引導
  - 延伸思考：
    - 可應用於 B2B 對接、行動 App 與後端協作
    - 風險：合約凍結過早；需求未知時需迭代
    - 優化：設計評審清單、Linter 規則、樣例驅動

- Practice Exercise（練習題）
  - 基礎練習：用 OpenAPI 定義「建立訂單」與「查詢訂單」，並產出成功/失敗範例
  - 進階練習：啟用 Prism Mock，邀請同事以 Postman 走完 happy path
  - 專案練習：完成 v1.0 合約、建立 Redoc 文件與 CI 驗證（Spectral + 合約測試）

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：資源、方法與錯誤模型齊備
  - 程式碼品質（30%）：規格一致、命名清晰、有範例
  - 效能優化（20%）：Mock/文件可即時預覽，開箱即用
  - 創新性（10%）：設計審查流程、回饋機制設計

---

## Case #2: 合約驅動的平行開發與 Contract Testing

### Problem Statement（問題陳述）
- 業務場景：APP 與 API 需同時開發，但因缺少共同合約與驗證機制，經常到整合階段才發現不相容。希望建立「合約即真相」與自動化驗證，讓前後端能並行且持續信心交付。
- 技術挑戰：缺少可機器驗證的合約；沒有 provider/consumer 契約測試；CI 缺口導致破壞性變更溜進主線。
- 影響範圍：整合風險、交付節奏、缺陷率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 沒有 consumer 驗證，僅以手動 smoke 測試驗證 API。
  2. 合約未被 CI 作為 gate 條件，破壞性變更未被攔截。
  3. 合約散落於文件/對話，無法機器化驗證。
- 深層原因：
  - 架構層面：未將 API 合約當作系統對外協作的中心產物。
  - 技術層面：缺乏 Pact/Dredd 等工具導入。
  - 流程層面：缺少「契約分流與驗證」之 Pull Request 檢查。

### Solution Design（解決方案設計）
- 解決策略：建立「契約倉庫」，使用 Dredd/Pact 實作 consumer/provider 契約測試，將合約驗證與破壞性檢查納入 CI gate，讓 APP 與 API 能在合約穩定下平行開發。

- 實施步驟：
  1. 契約集中化
     - 細節：合約獨立 repo；用 Git tag 管版本
     - 資源：Git、OpenAPI
     - 時間：0.5 天
  2. Consumer 測試
     - 細節：由前端維護使用到的 endpoints 與範例
     - 資源：Pact/Dredd、Postman
     - 時間：1-2 天
  3. Provider 驗證
     - 細節：API 器服務啟動後以 Dredd 驗證 responses
     - 資源：Dredd、Docker
     - 時間：1 天
  4. CI Gate
     - 細節：PR 需通過 spectral+lints+契約測試
     - 資源：GitHub Actions/GitLab CI
     - 時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# .github/workflows/contract.yml
name: Contract Gate
on: [pull_request]
jobs:
  verify-contract:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install deps
        run: |
          npm i -g @stoplight/spectral-cli dredd
      - name: Lint OpenAPI
        run: spectral lint openapi.yaml
      - name: Start API (provider)
        run: docker compose up -d api
      - name: Dredd verify
        run: dredd openapi.yaml http://localhost:8080 --no-color
```

- 實際案例：原文提到「先定義 API contract，讓前後端同時開發與提早回饋」，本案例將其落實為可驗證的 CI。
- 實作環境：OpenAPI + Dredd/Pact + GitHub Actions + Docker。
- 實測數據：
  - 改善前：整合階段大量接口錯誤，返工週期長。
  - 改善後：破壞性變更在 PR 階段即被攔截；可並行開發。
  - 改善幅度：未提供數值（定性成效：整合風險顯著下降）。

- Learning Points
  - 核心知識點：契約測試、CI Gate、合約版本化
  - 技能要求：OpenAPI、CI/CD、Dredd/Pact
  - 延伸思考：多消費者情境；快照 vs 實時資料一致性；金絲雀釋出

- Practice Exercise
  - 基礎：建置 Dredd 對簡單 API 驗證
  - 進階：加入 consumer-driven 合約與 mock
  - 專案：完成契約倉庫+PR Gate+破壞性變更報告

- Assessment Criteria
  - 功能完整性（40%）：Consumer/Provider 測試齊備
  - 程式碼品質（30%）：CI 腳本簡潔、易維護
  - 效能優化（20%）：驗證時間可控，緩存與並行
  - 創新性（10%）：契約差異可視化

---

## Case #3: 禁止共享資料庫，統一以 API 溝通（AWS 備忘錄實踐）

### Problem Statement（問題陳述）
- 業務場景：多團隊共享同一資料庫以達到「快速整合」，但導致耦合嚴重、相互干擾、變更風險高。希望改以 API 作為唯一協作界面，建立可擴展的服務邊界。
- 技術挑戰：拆除共享 DB 依賴；對既有整合流程影響大；服務網路與權限需重塑。
- 影響範圍：跨團隊協作、資料安全、彈性擴展能力。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 共享 DB 讓多方直接讀寫核心資料，互相影響。
  2. 無正式協作合約，資料 schema 改動即破壞整合。
  3. 無網段隔離與權限邊界，容易產生事故。
- 深層原因：
  - 架構層面：未以服務為邊界建立清晰介面。
  - 技術層面：缺少 API 網關與服務間認證授權。
  - 流程層面：缺 ADR（Architecture Decision Record）與治理規範。

### Solution Design（解決方案設計）
- 解決策略：以 ADR 正式決議「禁止共享 DB、必須 API 通訊」，配合網路隔離、最小權限、API Gateway 與觀測機制；分段替換既有整合，逐步落地。

- 實施步驟：
  1. 發佈 ADR 與例外處理機制
     - 細節：定義禁止共享 DB 與例外審核流程
     - 資源：ADR 模板、內網 Wiki
     - 時間：0.5 天
  2. 網路隔離與最小權限
     - 細節：K8s NetworkPolicy/雲端 Security Group；DB 僅服務帳號可用
     - 資源：Kubernetes、雲管平台
     - 時間：1-2 天
  3. API Gateway 與服務憑證
     - 細節：JWT/MTLS；路由與速率限制；審計
     - 資源：Kong/Apigee、IdP
     - 時間：2-3 天
  4. 漸進式替換整合點
     - 細節：先讀後寫，再完全切換
     - 資源：雙寫/事件匯流排
     - 時間：視規模 2-6 週

- 關鍵程式碼/設定：
```yaml
# Kubernetes NetworkPolicy（僅允許 api-namespace 存取 db 服務）
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-allow-api-only
  namespace: data
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: api
      ports:
        - protocol: TCP
          port: 5432
```

- 實際案例：原文引用 AWS 2002 備忘錄精神「團隊間僅以 API 溝通，不准共享 DB」，此案為實用落地步驟。
- 實作環境：Kubernetes + API Gateway + Cloud IAM/SG。
- 實測數據：
  - 改善前：DB schema 變更常引發跨團隊事故。
  - 改善後：服務邊界清晰；改動可控；審計可追蹤。
  - 改善幅度：未提供數值（定性：耦合與事故風險明顯下降）。

- Learning Points
  - 核心知識點：服務邊界、零信任、API Gateway
  - 技能要求：K8s 網路、IAM、API 管理
  - 延伸思考：事件驅動取代同步耦合、資料複本策略

- Practice Exercise
  - 基礎：撰寫 ADR 禁止共享 DB
  - 進階：實施一組 NetworkPolicy 並驗證
  - 專案：為既有共享查詢改造為 API + JWT 授權

- Assessment Criteria
  - 功能完整性（40%）：策略+網路+授權齊備
  - 程式碼品質（30%）：設定可讀、標準化
  - 效能優化（20%）：封路不影響正常流量
  - 創新性（10%）：漸進替換策略設計

---

## Case #4: 用 BFF/SDK 劃清 API 與 APP 邊界，兼顧通用性與好用性

### Problem Statement（問題陳述）
- 業務場景：API 被 UI 細節綁死，跨領域重用困難（例：零售到餐飲）。需要核心 API 維持精簡、通用，並讓前端有好用的開發體驗。
- 技術挑戰：如何避免把複雜度塞進 API；如何兼顧 DX 與 API 穩定。
- 影響範圍：API 可重用性、跨產品線擴展、前端開發效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. UI 驅動而非領域驅動，API 泥化成 UI 專用。
  2. 缺少 BFF 層或 SDK，導致把組合語意塞入 API。
  3. API/APP 分界無決策者，容易過度設計或過度耦合。
- 深層原因：
  - 架構層面：未區分「通用核心 API」與「情境特化組合」。
  - 技術層面：無 API Codegen/SDK 與 BFF 樣板。
  - 流程層面：缺少 API/APP 邊界審查。

### Solution Design
- 解決策略：核心 API 提供最小但完備的領域語意；以 BFF 實作前端所需的組合；用 OpenAPI Codegen 提供 SDK，降低接入成本，兼顧 DX 與通用性。

- 實施步驟：
  1. 定義最小可用領域資源
     - 細節：拆出通用資源與操作
     - 資源：DDD、API 設計準則
     - 時間：1-2 天
  2. 建立 BFF
     - 細節：聚合/轉換/快取
     - 資源：Node.js/Express/NestJS
     - 時間：2-3 天
  3. 產生 SDK
     - 細節：OpenAPI Generator/NSwag
     - 資源：OpenAPI、Codegen
     - 時間：0.5-1 天

- 關鍵程式碼/設定：
```js
// bff/index.js (示意)
const express = require('express');
const fetch = require('node-fetch');
const app = express();

app.get('/ui/orders/:id', async (req, res) => {
  // 聚合核心 API 多個呼叫，回傳前端友善格式
  const [order, items] = await Promise.all([
    fetch(`http://core-api/orders/${req.params.id}`).then(r => r.json()),
    fetch(`http://core-api/orders/${req.params.id}/items`).then(r => r.json())
  ]);
  res.json({
    id: order.id,
    status: order.status,
    lines: items.map(x => ({ sku: x.sku, qty: x.qty }))
  });
});

app.listen(3000);
```

- 實際案例：原文建議「維持精簡 API，複雜組合提供 SDK/Template/BFF」，避免 API 被 UI 綁死。
- 實作環境：Node.js + Express/Nest + OpenAPI Generator。
- 實測數據：
  - 改善前：API 無法跨域重用；前端實作重複。
  - 改善後：核心穩定；前端以 BFF/SDK 快速開發。
  - 改善幅度：未提供數值（定性：重用性/DX 顯著提升）。

- Learning Points
  - 核心知識點：API/APP 邊界、BFF、SDK
  - 技能要求：REST 設計、Node.js、Codegen
  - 延伸思考：GraphQL 作為 BFF；快取與權限下推策略

- Practice Exercise
  - 基礎：以 BFF 聚合兩個核心 API
  - 進階：加入快取與錯誤處理
  - 專案：由 OpenAPI 生成 TypeScript SDK 並整合到前端

- Assessment Criteria
  - 功能完整性（40%）：聚合、轉換、錯誤處理齊備
  - 程式碼品質（30%）：模組化、測試
  - 效能優化（20%）：快取/併發請求
  - 創新性（10%）：BFF 模式延伸（GraphQL/Edge）

---

## Case #5: 把 API 當產品經營（API Economy 與 DX）

### Problem Statement
- 業務場景：API 被視為產品附屬，缺少路線圖、SLA、開發者支援，導致對外整合難以規模化。需以 API as Product 的方式經營與量化 DX。
- 技術挑戰：缺乏開發者入口、金鑰發放、配額/速率管控與監控。
- 影響範圍：商業擴展能力、合作夥伴接入、品牌形象。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. API 文件零散、無自助化 onboarding。
  2. 無 SLA、配額與金鑰管理，營運風險高。
  3. 無 DX 指標，無法量化改善。
- 深層原因：
  - 架構層面：缺開發者入口與 API 產品化思維。
  - 技術層面：API Gateway/Portal 缺位。
  - 流程層面：未定義版本/廢棄政策與支援流程。

### Solution Design
- 解決策略：建立 Developer Portal、金鑰與配額策略、文件與範例程式、回饋通道與指標儀表板，將 API 視為可管理的產品。

- 實施步驟：
  1. Developer Portal 上線
     - 細節：文件、範例、Try it
     - 資源：Redocly/Stoplight/SwaggerHub
     - 時間：2-3 天
  2. 金鑰與配額
     - 細節：Key Auth/OAuth、速率限制
     - 資源：Kong/Apigee
     - 時間：1-2 天
  3. DX 指標儀表板
     - 細節：TTFS、錯誤率、成功率
     - 資源：GA/Amplitude/APM
     - 時間：1-2 天

- 關鍵程式碼/設定：
```yaml
# Kong declarative (金鑰與速率限制)
services:
- name: orders
  url: http://orders:8080
  routes:
  - name: orders-route
    paths: ["/api/orders"]
plugins:
- name: key-auth
- name: rate-limiting
  config:
    minute: 60
    policy: local
```

- 實際案例：原文提出「API 經濟」與標準化/規模化效益，強調 DX 先行。
- 實作環境：Kong/Apigee + Redocly + Metrics。
- 實測數據：
  - 改善前：對接耗時、支援工單高。
  - 改善後：自助化接入、可觀測、可治理。
  - 改善幅度：未提供數值（定性：接入速度提升、工單下降）。

- Learning Points
  - 核心知識點：API as Product、DX 指標
  - 技能要求：API Gateway、Portal、度量
  - 延伸思考：商業模式（計費）、流量變現

- Practice Exercise
  - 基礎：以 Redoc 部署文件
  - 進階：於 Gateway 開啟 key-auth + rate-limit
  - 專案：設計 DX 儀表板與回饋管道

- Assessment Criteria
  - 功能完整性（40%）：Portal、金鑰、配額齊備
  - 程式碼品質（30%）：設定清晰、可版本化
  - 效能優化（20%）：低延遲、穩定
  - 創新性（10%）：TTFS 指標與 A/B 文件實驗

---

## Case #6: 規格標準化與 Style Guide 避免 API 叢林

### Problem Statement
- 業務場景：多團隊各自定義 API，風格不一致，使用者困惑。需要風格指南與 Linter 在落地，降低認知負擔。
- 技術挑戰：如何在不限制創新的前提下標準化命名、錯誤、分頁等。
- 影響範圍：可用性、維護性、跨團隊協作。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無統一命名/錯誤/分頁規範。
  2. 缺工具自動校驗規格。
  3. 未建立設計審查與範例庫。
- 深層原因：
  - 架構層面：缺「設計原則」與「共用字典」。
  - 技術層面：未用 Spectral/Ruleset 等工具。
  - 流程層面：審查會議/PR Gate 缺失。

### Solution Design
- 解決策略：制定 API Style Guide（命名、層級、錯誤模型、分頁、過濾），以 Spectral Linter 自動化檢查並納入 PR gate，建立規範範例庫。

- 實施步驟：
  1. 撰寫 Style Guide 與範例
     - 資源：Confluence/Wiki、樣例
     - 時間：1-2 天
  2. 建立 Spectral 規則
     - 資源：@stoplight/spectral
     - 時間：0.5-1 天
  3. PR Gate 整合
     - 資源：CI
     - 時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# .spectral.yaml
extends: ["spectral:oas"]
rules:
  operation-success-response:
    description: "2xx responses required"
    given: "$.paths[*][get,post,put,patch,delete].responses"
    then:
      field: "@key"
      function: pattern
      functionOptions: { match: "^2\\d\\d$" }
  no-trailing-slash:
    given: "$.paths"
    then:
      function: pattern
      functionOptions: { notMatch: "/$" }
```

- 實際案例：原文提「Continuous API Management」與設計模式，強調標準化與規模化。
- 實作環境：Spectral + CI + Wiki。
- 實測數據：定性提升一致性與可讀性；審查時間下降。

- Learning Points
  - 核心：風格指南、Lint 自動化
  - 技能：OpenAPI、Spectral、CI Gate
  - 延伸：Design Tokens；跨語言 SDK 風格統一

- Practice Exercise
  - 基礎：加入兩條自訂規則
  - 進階：為錯誤模型設規範與 Lint
  - 專案：建立 Style Guide 網站與範例庫

- Assessment Criteria
  - 功能（40%）：指南+規則+CI
  - 品質（30%）：清楚、可擴充
  - 效能（20%）：Lint 速度
  - 創新（10%）：自動修正建議

---

## Case #7: 版本控管與相容性策略（SemVer、去破壞性演進）

### Problem Statement
- 業務場景：API 規格頻繁變更導致客戶端破壞。需建立版本策略、去破壞性演進與廢棄流程。
- 技術挑戰：如何在不影響既有客戶的前提下演進。
- 影響範圍：客戶端穩定、營運風險、品牌信任。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無清楚版本策略（URL/標頭/媒體類型）。
  2. 缺少 deprecation 與落日政策。
  3. 破壞性改動未被識別/公告。
- 深層原因：
  - 架構：未建立相容性原則（只加不減）。
  - 技術：無相容性檢查工具。
  - 流程：缺少公告、試用期、切換窗口。

### Solution Design
- 解決策略：採 SemVer；加法演進；使用 Accept/Content-Type 或 URL 版本化；Deprecation Header 與公告，建立落日政策與相容性檢查。

- 實施步驟：
  1. 決定版本標示方式
     - 資源：ADR
     - 時間：0.5 天
  2. 建立 deprecation 流程
     - 資源：Portal、公告模板
     - 時間：0.5 天
  3. 相容性檢查
     - 資源：OpenAPI diff 工具
     - 時間：0.5 天

- 關鍵程式碼/設定：
```http
GET /orders/123 HTTP/1.1
Accept: application/vnd.company.orders.v1+json
# 回應若即將淘汰：
Deprecation: true
Sunset: Wed, 01 Jan 2025 00:00:00 GMT
Link: <https://developer.example.com/changelog>; rel="deprecation"
```

- 實際案例：原文指「API 必須長期穩定，若變更需前相容」，本案為落地策略。
- 實作環境：ADR + OpenAPI-diff + Portal。
- 實測數據：定性「破壞性變更率下降、客戶端穩定提升」。

- Learning Points
  - 核心：版本策略、去破壞演進
  - 技能：OpenAPI diff、HTTP Header
  - 延伸：多版本共存、灰度發布

- Practice Exercise
  - 基礎：替 API 加上版本媒體類型
  - 進階：產出 deprecation 公告與 Sunset 管理
  - 專案：加入 OpenAPI diff 檢查 PR

- Assessment Criteria
  - 功能（40%）：版本、公告、檢查齊備
  - 品質（30%）：一致、可追溯
  - 效能（20%）：diff 快速、準確
  - 創新（10%）：自動產 changelog

---

## Case #8: 大量資料的分頁與過濾設計（Snapshot 與游標）

### Problem Statement
- 業務場景：客戶需要查詢大量訂單（百萬級），一次性傳回不可行。需設計分頁、過濾與一致性策略。
- 技術挑戰：資料持續變動時分頁一致性；效能與延遲控制。
- 影響範圍：可用性、效能、資料一致性認知。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無分頁/過濾，造成超時或大量傳輸。
  2. 即時資料變動造成翻頁不一致。
  3. 無排序/游標策略，導致跳頁/重覆。
- 深層原因：
  - 架構：缺預設排序與 snapshot 觀念。
  - 技術：未使用游標/令牌。
  - 流程：未在合約中明確定義語意。

### Solution Design
- 解決策略：採用游標式分頁（nextPageToken），固定排序欄位；提供 snapshotId 選項確保一致視圖；明確定義語意與時效。

- 實施步驟：
  1. 設計排序與游標
     - 資源：DB 索引、游標設計
     - 時間：1 天
  2. Snapshot 支援
     - 資源：讀寫分離/快照表
     - 時間：1-2 天
  3. 合約註明語意
     - 資源：OpenAPI
     - 時間：0.5 天

- 關鍵程式碼/設定：
```http
GET /orders?limit=50&nextPageToken=eyJvZmZzZXQiOiIxMjM0NSJ9
X-Snapshot-Id: 2025-08-26T10:00:00Z
Link: <.../orders?limit=50&nextPageToken=abc>; rel="next"
```

- 實際案例：原文參照「API Design Patterns」中關於分頁/過濾的重要模式。
- 實作環境：REST + OpenAPI + DB 索引。
- 實測數據：定性「查詢穩定、一致性明確、效能可控」。

- Learning Points
  - 核心：游標分頁、Snapshot 語意
  - 技能：索引設計、合約描述
  - 延伸：流式傳輸、後台匯出任務

- Practice Exercise
  - 基礎：以游標分頁提供列表
  - 進階：加入 snapshotId 與 Link header
  - 專案：設計可配置的排序/過濾語法

- Assessment Criteria
  - 功能（40%）：分頁、排序、過濾
  - 品質（30%）：一致性語意清楚
  - 效能（20%）：查詢耗時與資源
  - 創新（10%）：客製化過濾 DSL

---

## Case #9: 長時間操作的非同步設計（LRO Pattern）

### Problem Statement
- 業務場景：進行大型資料匯出/重算等長時間操作，HTTP 同步超時。需提供非同步工作模式。
- 技術挑戰：作業追蹤、重試、狀態管理與通知。
- 影響範圍：可靠性、用戶體驗、系統資源。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 同步請求超時與資源鎖定。
  2. 無作業狀態與結果檔案查詢。
  3. 重覆提交造成重複作業。
- 深層原因：
  - 架構：未採 LRO 資源模式。
  - 技術：缺排程/工作隊列。
  - 流程：未定義 SLA 與通知方式。

### Solution Design
- 解決策略：採 202 Accepted + Operation 資源；提供作業查詢與結果下載；選配 Webhook/Event 通知；加入冪等與退避策略。

- 實施步驟：
  1. 設計 Operation 資源
     - 資源：OpenAPI
     - 時間：0.5 天
  2. 背景任務與儲存
     - 資源：隊列（SQS/RabbitMQ）
     - 時間：1-2 天
  3. 通知與重試
     - 資源：Webhook、退避
     - 時間：1 天

- 關鍵程式碼/設定：
```http
POST /exports
201 Created
Location: /operations/789

GET /operations/789
200 OK
{
  "id": "789",
  "status": "SUCCEEDED",
  "result": { "url": "/downloads/exp-789.csv" }
}
```

- 實際案例：原文引用「API Design Patterns」談長時作業與重試/可重入工作模式。
- 實作環境：REST + Queue + Worker。
- 實測數據：定性「超時消失、穩定性提升、UX 可預期」。

- Learning Points
  - 核心：LRO、Operation 資源
  - 技能：隊列/Worker、重試退避
  - 延伸：Webhooks 安全、簽章驗證

- Practice Exercise
  - 基礎：提供非同步匯出接口
  - 進階：加入 Webhook 通知與重試
  - 專案：實作可恢復/可重入作業

- Assessment Criteria
  - 功能（40%）：提交/查詢/結果
  - 品質（30%）：狀態轉移清晰
  - 效能（20%）：資源使用平滑
  - 創新（10%）：Webhooks 防偽

---

## Case #10: 冪等性與重試去重（Idempotency-Key）

### Problem Statement
- 業務場景：支付/下單在網路抖動下重試，造成重覆扣款/下單。需提供冪等機制。
- 技術挑戰：如何跨實例去重；鍵保存/過期策略；與重試搭配。
- 影響範圍：財務風險、客訴、可靠性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無冪等鍵與結果快取。
  2. 無全域唯一約束。
  3. 重試機制無退避與上限。
- 深層原因：
  - 架構：無「請求等於意圖」的識別設計。
  - 技術：缺少唯一索引/儲存。
  - 流程：未在合約要求提供鍵。

### Solution Design
- 解決策略：要求客戶端提供 Idempotency-Key；服務端以唯一鍵儲存請求指紋與結果；在 TTL 內重送直接回相同結果；搭配退避重試策略。

- 實施步驟：
  1. 合約擴充要求鍵
     - 資源：OpenAPI header 定義
     - 時間：0.5 天
  2. 服務端去重
     - 資源：DB 唯一索引/Redis
     - 時間：1 天
  3. 客戶端重試策略
     - 資源：SDK/文件
     - 時間：0.5 天

- 關鍵程式碼/設定：
```js
// Node.js 範例（概念）
app.post('/payments', async (req, res) => {
  const key = req.header('Idempotency-Key');
  if (!key) return res.status(400).json({ error: 'Idempotency-Key required' });

  const existing = await db.getResultByKey(key);
  if (existing) return res.json(existing); // 回放結果

  const result = await chargeCard(req.body);
  await db.saveResult(key, result); // 唯一鍵約束
  res.json(result);
});
```

- 實際案例：原文在安全/可靠性設計段落延伸到「請求去重與重試」的設計模式。
- 實作環境：REST + 唯一索引/Redis + SDK。
- 實測數據：定性「重覆交易歸零，重試安全」。

- Learning Points
  - 核心：冪等設計、退避重試
  - 技能：Header/儲存設計
  - 延伸：多區高可用、跨區一致性

- Practice Exercise
  - 基礎：新增 Idempotency-Key 支援
  - 進階：Redis 去重與 TTL
  - 專案：SDK 內建重試與鍵管理

- Assessment Criteria
  - 功能（40%）：鍵、儲存、回放
  - 品質（30%）：錯誤處理與時限
  - 效能（20%）：低延遲
  - 創新（10%）：鍵衝突可觀測

---

## Case #11: 設計階段導入安全性（OAuth2、輸入驗證、權限模型）

### Problem Statement
- 業務場景：安全性常被延後到實作末期，導致滲透風險與返工。需在設計階段就確立授權流、權限範圍與輸入驗證。
- 技術挑戰：權限切分、Scope 設計、驗證一致性。
- 影響範圍：資安風險、合規性、開發成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 合約缺安全定義，開發各自為政。
  2. 缺輸入驗證，攻擊面大。
  3. 無最小權限原則。
- 深層原因：
  - 架構：未建立權限模型與資源範圍。
  - 技術：缺 OAuth2/OIDC 與 JSON Schema 驗證。
  - 流程：未將安全視為設計審查要點。

### Solution Design
- 解決策略：在 OpenAPI 中定義 securitySchemes 與 scopes；所有請求/回應以 JSON Schema 驗證；以最小權限原則設計資源與操作；設計審查納入安全清單。

- 實施步驟：
  1. 建立授權流與 Scope
     - 資源：OAuth2/OIDC
     - 時間：1 天
  2. JSON Schema 驗證
     - 資源：Ajv/express-openapi-validator
     - 時間：0.5-1 天
  3. 安全審查清單
     - 資源：Checklist
     - 時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# OpenAPI 安全定義
components:
  securitySchemes:
    oauth2:
      type: oauth2
      flows:
        clientCredentials:
          tokenUrl: https://idp/oauth/token
          scopes:
            orders.read: "Read orders"
            orders.write: "Create/update orders"
security:
  - oauth2: [orders.read]
```

- 實際案例：原文「從設計階段就考慮安全性」，強調合約層面表達安全與驗證。
- 実作環境：OpenAPI + IdP + 驗證中介軟體。
- 實測數據：定性「風險下降、返工減少、合規提升」。

- Learning Points
  - 核心：安全作為設計產物
  - 技能：OAuth2、JSON Schema、最小權限
  - 延伸：安全測試、自動化掃描

- Practice Exercise
  - 基礎：為 API 加上 scopes 與驗證
  - 進階：錯誤模型統一（401/403）
  - 專案：安全審查清單與 CI 安全掃描

- Assessment Criteria
  - 功能（40%）：授權/驗證/錯誤
  - 品質（30%）：Schema 嚴謹
  - 效能（20%）：低開銷
  - 創新（10%）：動態權限政策

---

## Case #12: 避免過度設計，採用演進式設計與 BFF 緩衝

### Problem Statement
- 業務場景：工程團隊追求「完美通用」導致過度設計，開發資源未用於當前最重要任務。需建立「適度模組化」的決策框架。
- 技術挑戰：如何決定抽象邊界與時機；避免過早泛化。
- 影響範圍：研發效率、商業對齊、技術債。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 需求未明就設計高抽象框架。
  2. 缺乏經驗法則與審查。
  3. 無「先用 BFF/SDK 緩衝」的策略。
- 深層原因：
  - 架構：未定義演進式設計原則。
  - 技術：缺少臨時適配層。
  - 流程：未保留探索性容量。

### Solution Design
- 解決策略：建立決策清單（MVP 優先、抽象時機、YAGNI），以 BFF/SDK 作為變化緩衝，核心 API 保持精簡，於證實重覆需求後再抽象。

- 實施步驟：
  1. 決策框架與 ADR
     - 時間：0.5 天
  2. BFF/SDK 緩衝策略
     - 時間：1 天
  3. Sprint 容量保留（探索/重構）
     - 時間：流程調整

- 關鍵程式碼/設定：
```md
# ADR-Template: Abstraction Timing
- Context: 重覆需求 >= 3 次才抽象
- Decision: 核心 API 保持最小集合，先用 BFF 服務特化需求
- Consequences: 降低過早設計風險，保留演進空間
```

- 實際案例：原文引用 GIPI「模組化與客製化是光譜」，並建議用 BFF/SDK 降低複雜度。
- 實作環境：ADR + BFF + Scrum 規則。
- 實測數據：定性「迭代速度提升、重構成本降低」。

- Learning Points
  - 核心：YAGNI、演進式設計、緩衝層
  - 技能：ADR、產品決策
  - 延伸：度量抽象投報比

- Practice Exercise
  - 基礎：撰寫一次抽象時機的 ADR
  - 進階：用 BFF 解一次特化需求
  - 專案：回顧 3 次需求後抽象核心

- Assessment Criteria
  - 功能（40%）：策略能落地
  - 品質（30%）：ADR 清楚
  - 效能（20%）：迭代速度
  - 創新（10%）：度量與回饋

---

## Case #13: 敏捷架構師設置與 20% 能力保留

### Problem Statement
- 業務場景：團隊專注短期交付，長期架構/非功能需求（技術債、安全、API 設計）被忽略。需設置敏捷架構師與固定容量保留。
- 技術挑戰：角色定位、授權、跨團隊協調。
- 影響範圍：長期可演進性、品質、風險。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 長期需求「重要但不緊急」，被延宕。
  2. 缺架構師統整跨團隊視角。
  3. 無固定容量處理技術債。
- 深層原因：
  - 架構：缺少負責核心機制抽象的人。
  - 技術：跨 repo/capability 缺指揮。
  - 流程：無 20% 固定容量政策。

### Solution Design
- 解決策略：指定 Agile Architect（理解需求脈絡/設計核心機制/溝通與支持/驗證實作），並在每 sprint 保留 20% 處理架構議題與技術債。

- 實施步驟：
  1. 角色與職責定義
     - 時間：0.5 天
  2. Sprint 容量保留
     - 時間：流程調整
  3. 架構審查與 Roadmap
     - 時間：每月 1 次

- 關鍵程式碼/設定：
```yaml
# team-policy.yaml
architecture:
  role: Agile Architect
  responsibilities:
    - domain abstraction & core mechanisms
    - cross-team alignment & reviews
    - API boundary & version strategy
capacity:
  reserved: 0.2   # 20% for long-term/tech debts
cadence:
  arch-review: monthly
```

- 實際案例：原文引用多篇文獻說明敏捷架構師角色與任務，並提固定容量處理長期議題。
- 實作環境：Scrum/看板 + 會議節奏。
- 實測數據：定性「技術債增長放緩、決策一致」。

- Learning Points
  - 核心：設計公式/核心機制、長短期平衡
  - 技能：架構審查、溝通協調
  - 延伸：架構度量（可變更性/配適性）

- Practice Exercise
  - 基礎：撰寫角色與 R&R
  - 進階：建立每月架構審查流程
  - 專案：以核心機制解一組分散需求

- Assessment Criteria
  - 功能（40%）：流程落地
  - 品質（30%）：責任邊界清楚
  - 效能（20%）：節奏穩定
  - 創新（10%）：度量與透明化

---

## Case #14: 讀書會與系統化知識內化（CAPM、Patterns、Google SE）

### Problem Statement
- 業務場景：團隊缺少 API 治理/設計模式/工程文化的系統性知識。需透過讀書會與內化產出來提升整體能力。
- 技術挑戰：書籍選用、節奏、輸出轉化到實作。
- 影響範圍：設計品質、跨團隊共識、人才梯隊。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 知識零散，無系統累積。
  2. 缺內化輸出（規範/樣板）。
  3. 場域經驗未沉澱。
- 深層原因：
  - 架構：缺知識治理機制。
  - 技術：缺工具與材料庫。
  - 流程：未固定節奏與成果要求。

### Solution Design
- 解決策略：以「持續 API 治理」、「API Design Patterns」、「Software Engineering at Google」為核心教材，設定固定節奏、輸出物（指南、樣板、工具），以資深成員帶讀。

- 實施步驟：
  1. 設定書單與節奏
     - 時間：0.5 天
  2. 章節導讀與實作題
     - 時間：每週 1-2 小時
  3. 內化產出（規範/工具）
     - 時間：每月一次彙整

- 關鍵程式碼/設定：
```text
repo/
  reading-club/
    schedule.md
    summaries/  # 每章摘要
    actions/    # 對應改善行動與 PR
    artifacts/  # 規範/樣板/工具清單
```

- 實際案例：原文分享三本書與讀書會實務，強調資深成員帶讀與落地。
- 實作環境：Git Repo + 會議節奏。
- 實測數據：定性「規範產出、共識提升」。

- Learning Points
  - 核心：知識治理、制度化
  - 技能：導讀、選題、落地轉化
  - 延伸：社群交流、外部分享

- Practice Exercise
  - 基礎：建立讀書會 Repo 與排程
  - 進階：每章對應一個改善 PR
  - 專案：產出一版 API Style Guide

- Assessment Criteria
  - 功能（40%）：節奏與輸出完整
  - 品質（30%）：摘要與行動明確
  - 效能（20%）：持續 8 週以上
  - 創新（10%）：導入外部講者

---

## Case #15: 折扣規則的抽象化與結帳引擎（設計公式）

### Problem Statement
- 業務場景：多樣且多變的折扣需求導致程式散亂。需抽象「設計公式」：以購物車作為唯一輸入，計算引擎輸出結果，達到穩定介面與可擴充性。
- 技術挑戰：規則可插拔；輸入/輸出穩定；UI 與引擎解耦。
- 影響範圍：功能擴展速度、錯誤率、重構成本。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 規則直寫 UI/流程，耦合嚴重。
  2. 缺穩定介面，變更波及大。
  3. 測試困難，回歸成本高。
- 深層原因：
  - 架構：未定義核心機制（計算引擎）。
  - 技術：無規則介面與組合模式。
  - 流程：未以 core vs customization 劃分。

### Solution Design
- 解決策略：以「購物車 input/結算 output」定義穩定契約，設計 RuleBase 介面與管線（pipeline）執行，UI 僅負責收集輸入與呈現結果；透過 API 暴露結帳服務。

- 實施步驟：
  1. 定義資料模型與契約
     - 時間：1 天
  2. 實作規則引擎與管線
     - 時間：2-3 天
  3. API 化與測試
     - 時間：1-2 天

- 關鍵程式碼/設定：
```ts
// TypeScript：核心介面
interface Product { sku: string; price: number; }
interface CartItem { sku: string; qty: number; }
interface Cart { items: CartItem[]; coupons?: string[]; memberId?: string; }
interface CheckoutResult { total: number; discounts: {rule: string; amount: number}[]; }

interface Rule {
  name: string;
  apply(cart: Cart, products: Product[]): { amount: number };
}

function checkout(cart: Cart, rules: Rule[], catalog: Product[]): CheckoutResult {
  const discounts = rules.map(r => ({ rule: r.name, amount: r.apply(cart, catalog).amount }));
  const discountTotal = discounts.reduce((a, b) => a + b.amount, 0);
  const itemsTotal = cart.items.reduce((sum, it) =>
    sum + catalog.find(p => p.sku === it.sku)!.price * it.qty, 0);
  return { total: Math.max(0, itemsTotal - discountTotal), discounts };
}
```

- 實際案例：原文提供「折扣規則抽象化」文章與接口設計思路，作為 API First 背後「設計公式」示例。
- 實作環境：TypeScript/Node + REST API。
- 實測數據：定性「新增規則成本降低、回歸易測」。

- Learning Points
  - 核心：抽象化、核心機制、穩定契約
  - 技能：策略模式/管線、資料建模
  - 延伸：規則配置化、沙盒測試

- Practice Exercise
  - 基礎：實作兩個折扣規則
  - 進階：將 checkout 暴露為 API 並撰寫合約
  - 專案：規則 A/B 測試與回歸套件

- Assessment Criteria
  - 功能（40%）：規則插拔、契約穩定
  - 品質（30%）：測試充足
  - 效能（20%）：計算效率
  - 創新（10%）：規則組態與可觀測

---

## Case #16: API 治理與生命週期管理（API as Product）

### Problem Statement
- 業務場景：組織內 API 數量成長成「叢林」，缺少治理與生命週期管理（規劃、設計、開發、發布、維運、退場）。需導入持續 API 治理。
- 技術挑戰：目錄化、版本/相容策略、退場管理。
- 影響範圍：一致性、成本、風險。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 無 API Catalog 與擁有者。
  2. 無生命週期標記與規則。
  3. 缺治理角色與流程。
- 深層原因：
  - 架構：未以產品思維經營 API。
  - 技術：缺工具鏈支援。
  - 流程：無治理委員會/例會。

### Solution Design
- 解決策略：建立 API Catalog（owner、狀態、版本、SLA、依賴）、治理角色（產品/設計/安全/平台）、生命週期規則（提案/設計/試行/正式/維護/廢棄），以例會持續演進。

- 實施步驟：
  1. Catalog 與 Ownership
     - 時間：1-2 天
  2. Lifecycle 與 Gate
     - 時間：1 天
  3. 治理例會與變更控制
     - 時間：每雙週

- 關鍵程式碼/設定：
```yaml
# api-catalog.yaml
- name: Orders API
  owner: team-commerce
  lifecycle: GA        # PROPOSAL | EXPERIMENTAL | GA | DEPRECATED
  version: 1.3.0
  sla: 99.9
  dependencies: [Identity API]
  portal: https://developer.example.com/orders
```

- 實際案例：原文推薦「持續 API 治理」書籍並概述 API 叢林與生命週期觀。
- 實作環境：Git 目錄 + 治理例會 + Portal。
- 實測數據：定性「可見性提升、風險可控」。

- Learning Points
  - 核心：治理、生命週期、Catalog
  - 技能：Owner 模型、變更管理
  - 延伸：依賴圖譜、風險分析

- Practice Exercise
  - 基礎：建立 Catalog 條目
  - 進階：定義 Lifecycle Gate 與表單
  - 專案：導入治理例會與退場政策

- Assessment Criteria
  - 功能（40%）：Catalog+Lifecycle
  - 品質（30%）：資料完整
  - 效能（20%）：維護成本低
  - 創新（10%）：依賴可視化

---

## Case #17: 以康威定律調整組織與 API 邊界（Team Topologies）

### Problem Statement
- 業務場景：API 規格品質低、難以改善，實際根因在組織分工與溝通邊界。需依康威定律調整團隊切分，使系統邊界與團隊邊界對齊。
- 技術挑戰：職能分配、接口協商流程、責任界定。
- 影響範圍：API 設計品質、交付效率、協作成本。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. API 由不負責該領域的團隊定義。
  2. 跨團隊協商僅口頭/臨時。
  3. 缺 API Owner 與合約管理。
- 深層原因：
  - 架構：團隊切分與領域不匹配。
  - 技術：無接口協商與審查工具。
  - 流程：缺 RACI 與決策機制。

### Solution Design
- 解決策略：以業務領域劃分團隊與 API Owner；建立接口協商流程（草案→審查→凍結）、RACI 矩陣與跨團隊例會；以合約為唯一真相。

- 實施步驟：
  1. Domain 分割與 Team 對齊
     - 時間：1-2 週
  2. 合約協商流程
     - 時間：1-2 天
  3. RACI 與節奏
     - 時間：0.5 天

- 關鍵程式碼/設定：
```yaml
# api-ownership.yaml
orders:
  owner: team-commerce
  raci:
    responsible: [team-commerce]
    accountable: [architect-guild]
    consulted: [team-app]
    informed: [security, ops]
cadence:
  contract-review: bi-weekly
```

- 實際案例：原文強調「API 規格開得不好常是組織問題，需調整組織分工」。
- 實作環境：組織規劃 + 例會。
- 實測數據：定性「協作效率提升、API 決策更穩定」。

- Learning Points
  - 核心：Conway's Law、Team boundaries
  - 技能：RACI、協商流程設計
  - 延伸：Team Topologies 模式

- Practice Exercise
  - 基礎：為一條 API 指定 Owner 與 RACI
  - 進階：設計協商流程與時間盒
  - 專案：完成一次跨團隊合約審查

- Assessment Criteria
  - 功能（40%）：Owner/RACI/流程
  - 品質（30%）：角色清晰
  - 效能（20%）：協作成本下降
  - 創新（10%）：自動排程與紀錄

---

## Case #18: 建立開發者入口與可試用文件（Developer Portal）

### Problem Statement
- 業務場景：外部開發者難以快速上手 API，缺乏「可試用」與範例。需用 Portal 展示規格、Try-it、SDK 下載與變更日誌。
- 技術挑戰：多版本共存文件、沙箱、金鑰發放。
- 影響範圍：接入速度、支援負擔、口碑。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 文件零散，不可互動。
  2. 無沙箱/Mock。
  3. 缺 SDK 與範例。
- 深層原因：
  - 架構：未將 DX 列為產品需求。
  - 技術：缺生成工具與沙箱環境。
  - 流程：無變更日誌與公告節奏。

### Solution Design
- 解決策略：以 Redoc/Stoplight Elements 建 Portal，提供 Try-it 與 Sandbox；整合金鑰申請、SDK 下載與 Changelog；版本切換清楚。

- 實施步驟：
  1. 文檔站部署
     - 時間：0.5-1 天
  2. Try-it 與 Sandbox
     - 時間：1 天
  3. SDK 與範例
     - 時間：1-2 天

- 關鍵程式碼/設定：
```yaml
# docker-compose.yml：提供 Redoc 與 Prism Mock
services:
  mock:
    image: stoplight/prism:4
    command: mock -h 0.0.0.0 /spec/openapi.yaml
    ports: ["4010:4010"]
    volumes: ["./spec:/spec"]
  docs:
    image: redocly/redoc
    environment:
      SPEC_URL: /spec/openapi.yaml
    ports: ["8080:80"]
    volumes: ["./spec:/usr/share/nginx/html/spec:ro"]
```

- 實際案例：原文強調 DX 與「先做 API 再做產品」，Portal 為落地關鍵。
- 實作環境：Redoc + Prism + Codegen。
- 實測數據：定性「TTFS 降低、工單下降」。

- Learning Points
  - 核心：DX、可試用文件
  - 技能：文檔生成、Mock、SDK
  - 延伸：互動教學、演練腳本

- Practice Exercise
  - 基礎：以 Redoc 部署文件
  - 進階：整合 Mock Try-it
  - 專案：加入 SDK 下載與版本切換

- Assessment Criteria
  - 功能（40%）：Try-it、Sandbox、SDK
  - 品質（30%）：易讀、易搜尋
  - 效能（20%）：載入與互動性能
  - 創新（10%）：互動教學流程

----------------------------

案例分類

1) 按難度分類
- 入門級（適合初學者）：
  - Case 14（讀書會與知識內化）
  - Case 18（Developer Portal 基礎）
  - Case 6（Style Guide + Linter 入門）
- 中級（需要一定基礎）：
  - Case 1（設計先行合約）
  - Case 2（契約測試與並行開發）
  - Case 4（BFF/SDK 邊界）
  - Case 5（API as Product/DX）
  - Case 7（版本策略）
  - Case 8（分頁/過濾）
  - Case 9（長時作業）
  - Case 10（冪等性）
  - Case 11（安全設計）
  - Case 12（避免過度設計）
  - Case 18（Portal 進階）
- 高級（需要深厚經驗）：
  - Case 3（禁止共享 DB、API-only）
  - Case 15（折扣規則抽象化/結帳引擎）
  - Case 16（API 治理與生命週期）
  - Case 17（康威定律與組織調整）

2) 按技術領域分類
- 架構設計類：
  - Case 3, 4, 12, 13, 15, 16, 17
- 效能優化類：
  - Case 8, 9, 10（可靠性/延遲/資源）
- 整合開發類：
  - Case 1, 2, 4, 5, 6, 18
- 除錯診斷類：
  - Case 2（契約退回）、Case 7（破壞性變更檢查）
- 安全防護類：
  - Case 3（網路/權限）、Case 11（OAuth/驗證）

3) 按學習目標分類
- 概念理解型：
  - Case 5（API 經濟）、Case 13（敏捷架構師）、Case 16（治理）、Case 17（康威定律）
- 技能練習型：
  - Case 1（OpenAPI）、Case 2（契約測試）、Case 6（Linter）、Case 8（分頁）、Case 9（LRO）、Case 10（冪等）、Case 11（安全）
- 問題解決型：
  - Case 3（共享 DB -> API）、Case 4（邊界與 BFF）、Case 7（版本相容）、Case 12（過度設計）
- 創新應用型：
  - Case 15（設計公式/引擎）、Case 18（互動式 Portal）

----------------------------

案例關聯圖（學習路徑建議）

- 先學哪些案例？
  - 起步概念與基礎：Case 14（知識內化）、Case 5（API as Product/DX）、Case 1（設計先行合約）
- 依賴關係：
  - Case 1 → Case 2（有合約才有契約測試）
  - Case 1/6 → Case 7（有規格與風格才談版本策略）
  - Case 4（BFF/SDK）依賴 Case 1/6（穩定合約與風格）
  - Case 3（API-only）依賴 Case 1（合約）與 Case 11（安全）
  - Case 16（治理）整合 Case 6/7/18（規範、版本、Portal）
  - Case 15（設計公式）依賴 Case 13（架構師角色）與 Case 1（合約）
  - Case 17（組織調整）影響並支撐所有案例的落地
- 完整學習路徑建議：
  1) 概念與文化：Case 14 → Case 5 → Case 13 → Case 17
  2) 規格與設計：Case 1 → Case 6 → Case 7 → Case 11
  3) 開發與整合：Case 2 → Case 4 → Case 18
  4) 模式與可靠性：Case 8 → Case 9 → Case 10
  5) 架構與治理：Case 3 → Case 16
  6) 進階抽象：Case 12 → Case 15
  - 以上路徑建議由左至右循序深化，途中穿插實作專題（例如以 Case 1/2/4/8/9/10/11/18 組成一條端到端 API First 實作線），最後導入 Case 16 的治理與 Case 17 的組織對齊，形成可持續的 API First 能力體系。

{% endraw %}