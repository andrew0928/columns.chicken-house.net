---
- source_file: /docs/_posts/2023/2023-01-01-api-design-workshop.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# 架構師觀點 – API Design Workshop 摘要  

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "架構師觀點 - API Design Workshop"
categories:
  - "系列文章: 微服務架構"
tags: ["系列文章","架構師的修練","microservices"]
published: true
logo: /wp-content/images/2023-01-01-api-design-workshop/slides/slides-01.png

# 自動擴增欄位
primary-keywords:
  - API First / Contract First
  - API Spec / OpenAPI / Swagger
  - OOP 與 State Machine
  - Scope-Based Authorization (OAuth2)
  - Entity-Action-Event 模型
  - Microservices / REST
secondary-keywords:
  - CRUD vs 行為導向 API
  - AsyncAPI / WebHook
  - NoSQL 資料建模
  - .NET / ASP.NET Core
  - JWT / ClaimsPrincipal
  - FSM (Finite-State-Machine)
  - Event Driven Architecture
tech_stack:
  languages: [C#, Java, C++]
  frameworks: [ASP.NET Core, Swagger / Swashbuckle]
  tools: [OpenAPI Generator, JWT, Mermaid, Kafka/RabbitMQ/NATS]
  platforms: [.NET 6+, Azure/AWS 任一雲端]
  concepts:
    - Domain-Driven-Design
    - Repository & ORM
    - API Gateway
    - Scope Design
    - Mock / Stub / Contract Testing
references:
  internal_links:
    - /2020/03/10/interview-abstraction/
    - /2022/12/01/devopsdays-api-first/
  external_links:
    - https://swagger.io/specification
    - https://www.asyncapi.com
    - https://learn.microsoft.com/dotnet/api/system.security.claims.claimsprincipal
    - https://zh.wikipedia.org/wiki/有限狀態機
mentioned_tools:
  - Swagger-UI
  - Postman / New-man
  - ChatGPT (協助撰寫 OpenAPI 片段)
content_metrics:
  word_count: 15500   # 估算
  reading_time: "50–60 分鐘"
  difficulty_level: "進階"
  content_type: "Workshop 筆記 / 架構設計"
generated_at: 2025-08-06 00:10 UTC
version: 1.0.0
```

---

## 文章摘要
作者以「API First 等於 OO 的 Interface First」為核心，示範如何把物件導向思維、有限狀態機與 OAuth2 Scope 管理整合成一套可落地的 API Design Workflow。  
全文先說明「先定契約、後寫程式」帶來的流程優勢，再透過會員註冊範例示範七個步驟：1) 畫出 Domain 狀態圖；2) 標註改變與不改變狀態的行為；3) 標示互動角色；4) 列出事件；5) 轉成 Entity-Action-Event API Spec；6) 定義 Scope；7) 用狀態圖跑情境驗證。  
作者強調：  
• 規格決定 70 % 成敗；API 若僅做 CRUD 難以防呆與授權。  
• 以 FSM + 封裝行為替代「讓呼叫端直接改資料」可大幅降低誤用。  
• Scope 是最小授權單位，必須從 Domain 而非 HTTP 動詞推導。  
• OpenAPI 描述同步呼叫；AsyncAPI 描述事件；兩者合併才能完整交付 Contract。  
• Mock 早於實作，可讓前後端、QA、Tech Writer 並行；也讓 SA 及早驗證「做對」而非「只做好」。

---

## 關鍵要點
- API First = Interface First：先談抽象、後談程式。
- 用狀態機拆解 Domain，可自然推導 Entity / Action / Event。
- 行為導向 API 能將「驗證、鎖定、狀態轉移」封裝於服務端。
- OAuth2 Scope 應以業務語義切分：CRUD ≠ 安全需求。
- OpenAPI + AsyncAPI 是完整 Contract；Mock 可用 Stub 自動產生。
- 「一次處理多筆」操作需獨立 Scope，避免資料被列舉爬走。
- 事件建議至少定義：state-changed、action-executing、action-executed。
- 先用 Console + In-Memory Collection POC，可在百行程式內驗證設計。
- Contract Testing 讓前後端同步開工，縮短整體 Lead Time。
- 思考安全性要前移到設計階段，而非 API 完成後才補救。

---

## 段落摘要

### 前言：物件導向思考與 API First
作者自述討厭背公式，習慣以少數基本功組合解決問題；API First 本質上就是把 OOP Interface 翻成 API Spec。只要掌握狀態、行為、資料與事件就能產生高可重用介面。

### 0. 正文開始（.NET Conf 投影片脈絡）
本篇延伸 2022 DevOpsDays Keynote，聚焦「HOW」。提出規格優先、設計標準化、安全前置與避免過度設計四大面向。

### 1. 開發流程上的改變
對比 Code First 與 Contract First。Contract First 先 Mock Spec，可讓 SA、RD、QA、Tech Writer 同步作業，同時亦提早驗證「對不對」，降低後期返工。

### 2. API Design Workshop（主案例）
以會員註冊流程為例，展示七步驟：
2-1 畫 FSM；2-2 標行為；2-3 標非狀態行為；2-4（略）；2-5 標角色；2-6 標事件；2-7 轉 API Spec；2-8 用情境走棋驗證；2-9 總結與 OpenAPI / AsyncAPI 關聯。

### 2-1 找出狀態圖
定義 CREATED/UNVERIFIED/VERIFIED/RESTRICTED/BANNED/DELETED 六狀態並以 Mermaid 表示。

### 2-2 標示改變狀態的行為
列出 register、verify、restrict/allow、ban/permit、remove；示範 C# 封裝策略（static method vs instance method）。

### 2-3 標示不改變狀態的行為
列 login、reset-password、get、get-masked、get-statistics；突顯封裝及鎖定需求較低。

### 2-5 標示互動角色
區分 Guest/User、Staff、Staff Manager、System Service、Partners；說明授權模型將映射到 OAuth2 Scope。

### 2-6 標示事件
建議三類事件：state-changed、action-executing、action-executed；並給出 payload 範本。

### 2-7 轉成 API Spec
提出 Entity-Action-Authorize-Event 四表；Action 再分四型；介紹 OpenAPI 描述同步、AsyncAPI 描述事件。

### 2-8 用狀態機驗證情境
把 Story 拆步驟，像玩大富翁移棋子；驗證每步在 FSM 合法並符合角色與 Scope。

### 2-9 設計小結
當 Entity / Action / Event 與 Scope 確認後，餘下只是選框架與編寫 YAML；安全議題留待下一篇。

---

## 問答集

### Q1 什麼是 Contract First？  
A: Contract First 指先制定 API Spec（OpenAPI/AsyncAPI）與 Mock，前、後端及測試皆依契約開發；相較 Code First，可提前驗證設計並並行作業。

### Q2 為何作者強調狀態機而非 CRUD？  
A: CRUD 允許呼叫端直接修改資料欄位，易破壞商業規則；狀態機將資料生命週期以封裝行為管理，可防呆、易授權、降低維運風險。

### Q3 Scope 與 HTTP 動詞有何不同？  
A: Scope 基於業務語意（如 REGISTER、STAFF），代表授權範圍；HTTP 動詞僅是技術操作。相同動詞在不同 Domain 行為下風險差異大，因此須用 Scope 管控。

### Q4 怎樣判斷需要 AsyncAPI？  
A: 若 API 需推送事件、支援 Pub/Sub 或 WebHook，單靠 OpenAPI 不足；AsyncAPI 允許描述 Topic、Payload 與訂閱方式，能完整定義 EDA 契約。

### Q5 Mock 要做到多真？  
A: 只需「能呼叫且回傳結構正確」，不必含商業邏輯；重點在讓前端與測試早開工及驗證 Spec。

### Q6 若團隊不熟 FSM，怎麼落地？  
A: 從現有 CRUD API 開始畫資料狀態流程圖，再把「改狀態的操作」獨立成 Endpoint；逐步遷移即可，不必一次重寫。

### Q7 多筆查詢為何要獨立 Scope？  
A: 列舉型查詢可在短時間內抓走整庫資料，屬高風險操作；獨立 Scope 才能額外做 Rate Limit 或僅授權給內部服務。

### Q8 事件要不要全列？  
A: 先列三大類再刪減：state-changed、action-executing、action-executed。過多事件會增加維運成本。

### Q9 如何在 .NET 中落實 Scope？  
A: 使用 JWT + ClaimsPrincipal，將 scope 陣列寫入 claim；在 Controller 方法加 [Authorize(Policy="scope:REGISTER")]; Startup 中用 Policy-Based Authorization 核心比對。

### Q10 OpenAPI 如何寫 Scope？  
A: 在 components.securitySchemes 下宣告 type: oauth2 並列 scopes；Endpoint 的 security 欄指定 { schemeName: [scope1, scope2] } 即可。

---

## 解決方案

Problem 1: API 規格常被 CRUD 心態綁架  
Root Cause: 忽視 Domain 狀態與封裝，導致授權與一致性難控。  
Solution: 以 FSM 描述生命週期 → 封裝行為 → 轉成 Entity-Action-Event；每條 Action 對應 Scope。  
Example: POST /api/members/{id}:ban 只允許 scope=STAFF，並於服務端內部鎖定改狀態。

Problem 2: 授權粒度過粗造成資安風險  
Root Cause: 只用 API-Key 或角色，不分操作與資料範圍。  
Solution: 依業務語意定最小 Scope；OAuth2 發 token 時僅授權所需範圍；API 端用 Policy 驗證。  
Example: Scope QUERY 僅給資料匯出排程，不給外包 App。

Problem 3: 事件傳遞無標準導致整合困難  
Root Cause: 只用自訂 JSON，缺乏契約管理與版本控。  
Solution: 採 AsyncAPI 定義 topic、payload、version；在 header 加 X-Webhook-Version。  
Example: state-changed v1.0 payload 如前述範本，升版時保留舊 topic 3 月。

Problem 4: 設計難以驗證，風險後移  
Root Cause: Spec 完成後才實作，直到整合才發現缺口。  
Solution: 用 OpenAPI-Generator 產生 Stub；在 CI 執行 Contract Test；狀態圖走棋驗證業務流程。  
Example: 每次 PR 產生 Mock Server，自動跑 Story Case。

---

## 版本異動紀錄
- 1.0.0 (2025-08-06) 首版：完成 Metadata 擴增、文章摘要、段落摘要、10 組 Q&A、4 項問題-解決方案整理。