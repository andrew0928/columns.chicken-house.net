---

source\_file: "\_posts/2024/2024-01-15-archview-llm.md" generated\_date: "2025-08-03 11:00:00 +0800" version: "1.0" tools:

- github\_copilot
- claude\_sonnet\_3\_5 model: "claude-3-5-sonnet-20241022"

---

# [架構師觀點] 開發人員該如何看待 AI 帶來的改變? - 生成內容

## 原始 Metadata

```yaml
layout: post
title: "[架構師觀點] 開發人員該如何看待 AI 帶來的改變?"
categories:
  - "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-01-15-archview-llm/2024-01-20-12-29-24.jpg
```

## 擴增 Metadata

### 自動識別關鍵字

```yaml
keywords:
  primary:
    - AI
    - 大型語言模型 (LLM)
    - API First
    - GPTs
    - 使用者體驗 (UX)
    - Function Calling
  secondary:
    - ChatGPT
    - OpenAI
    - PoC
    - 電子商務
    - 雲端服務
    - Azure App Service
    - Swagger
```

### 技術堆疊分析

```yaml
tech_stack:
  languages:
    - C#
    - JavaScript
  frameworks:
    - ASP.NET Core
    - React (於概念討論中提及)
  tools:
    - Docker
    - Swagger / OpenAPI
    - GitHub
  platforms:
    - Azure App Service
    - Linux (部署環境)
```

### 參考資源

```yaml
references:
  internal_links:
    - /2016/05/05/archview-net-open-source/
  external_links:
    - https://openai.com/blog/introducing-gpts
    - https://andrewshopoauthdemo.azurewebsites.net/swagger/index.html
    - https://github.com/andrew0928/AndrewDemo.NetConf2023
  mentioned_tools:
    - ChatGPT
    - GPTs
    - Swagger
    - Azure App Service
```

### 內容特性

```yaml
content_metrics:
  word_count: 6200  # 估算中文字數
  reading_time: "15 分鐘"
  difficulty_level: "中高級"
  content_type: "心得"
```

## 摘要 (Summaries)

### 文章摘要 (Article Summary)

作者以自行開發的「安德魯小舖」線上商店 PoC 為例，示範如何在 GPTs 中掛載自家 API，讓大型語言模型化身店長，透過自然語言與使用者互動並自動呼叫 API 完成購物、結帳、查詢訂單等流程。實作過程揭示：LLM 可補足傳統 UI 在「理解使用者意圖」上的缺口，API 設計必須從「供開發者使用」升級為「可被 AI 正確理解與推理」。作者進一步反思，AI 時代的軟體開發將從「操作導向」轉向「意圖導向」，UX 重心將由前端介面移向語意層；開發者應聚焦於穩固的 API First 思維與商業模型，以迎接 AI + API 帶來的典範轉移。

### 關鍵要點 (Key Points)

- LLM 能透過 Function Calling 將自然語言轉譯為精確的 API 呼叫，顛覆傳統 ChatBot。
- API 不再只服務人類開發者，還必須對 AI「可解釋、易推理」。
- UX 將從縮短操作流程的 UI 進化到直接理解使用者意圖的對話式互動。

### 段落摘要 (Section Summaries)

1. **1 安德魯小舖 GPTs – Demo**：作者說明 GPTs 服務特色，展示如何透過 OpenAPI 讓 GPTs 自動呼叫線上商店 API。Demo 步驟涵蓋商品瀏覽、折扣計算、結帳、訂單統計等，突顯 GPTs 在理解複雜口語需求與動態推理折扣規則上的能力，並說明整合門檻低、思維轉換高。

2. **2 軟體開發的改變**：作者回顧自身 20 年開發經驗，指出電腦一直缺乏「意圖理解」能力。隨著 LLM 成熟，使用者與軟體間的「意圖—操作」鴻溝被縮短；傳統 UX 優化將被 LLM 的「降維打擊」取代，開發者需重新定位 API 角色與商業模式。

3. **2‑1 使用者體驗**：剖析 UX 演進史—從鍵盤指令到觸控體感—仍未解決長輩一類使用者的操作困難。LLM 可直接理解自然語言意圖，讓操作負擔從使用者轉移到模型。

4. **2‑2 由 LLM 整合所有資源**：引用 OpenAI Function Calling 文件，說明 LLM 可將「誰是我最重要客戶？」自動映射為 get\_customers API。前端 UI 與後端 API 之間的翻譯工作被 LLM 接手，API 設計需足以讓模型演繹正確參數與語意。

## 問答集 (Q&A Pairs)

### Q1 LLM 為何能提升使用者體驗？

Q: 什麼原因使大型語言模型在 UX 上構成「降維打擊」？ A: 因為 LLM 能理解自然語言並推理使用者意圖，直接將需求轉譯成後端操作，省去多層 UI 流程，讓互動更直覺。

### Q2 API 設計在 AI 時代需注意什麼？

Q: 面對會呼叫 API 的 AI，開發者應如何調整 API 設計？ A: 必須提供清楚的參數語意、完整錯誤訊息與一致的資源模型，讓模型能推理正確使用時機並自動處理例外。

### Q3 GPTs Custom Action 的核心條件？

Q: 若要將自家 API 掛入 GPTs，需要滿足哪些條件？ A: 需提供符合 OpenAPI 規格的描述，包含路徑、方法、參數與回傳格式；GPTs 會自動解析並決定調用時機。

### Q4 PoC 中折扣規則如何被模型推理？

Q: Demo 中「啤酒第二件六折」並未寫在 API，GPTs 為何能計算？ A: 模型先嘗試加入購物車並呼叫估價 API，比對回應金額推導折扣邏輯，再依口語指令動態調整購物清單。

### Q5 傳統 ChatBot 與 GPTs 有何差異？

Q: 為何作者認為過去的 ChatBot 僅像在 CLI？ A: 傳統 ChatBot 依賴固定指令與關鍵字，無法真正理解上下文；GPTs 透過 LLM 能連貫對話並進行邏輯推理。

### Q6 開發者應如何迎接 AI + API 時代？

Q: 除了學習 LLM，開發者應優先投入哪些領域？ A: 深化領域知識、建立穩固的 API First 架構，並設計易於 AI 理解的資料與權限模型，以支撐未來自動化。

### Q7 UX 設計師角色是否會被取代？

Q: 若 LLM 可直接理解意圖，UX 設計師還有何價值？ A: UX 焦點將從視覺與流程優化轉向對話體驗、提示工程與跨通道整合，設計師角色依舊重要但技能需求改變。

### Q8 PoC 的侷限是什麼？

Q: 作者提到 Demo 沒有 100% 穩定，問題出在哪？ A: 因模型推理具隨機性且 API 僅存記憶體無狀態保護，偶爾出現不合理購物建議；正式環境需加入驗證與重試機制。

## 解決方案 (Solutions)

### P1 使用者意圖難以捕捉

Problem: 傳統 UI 只能縮短操作流程，無法真正理解意圖。 Root Cause: 缺乏語意解析能力，需使用者自行映射操作。 Solution: 透過 LLM + Function Calling，自然語言直接轉為後端操作；前端僅需提供對話介面。 Example: GPTs 呼叫 `/api/carts/{id}/estimate` 自動計算折扣。

### P2 API 無法被 AI 正確使用

Problem: API 僅為開發者而設計，缺少語意說明與一致性。 Root Cause: 參數命名曖昧、回傳格式不統一。 Solution: 採用 API First，使用 OpenAPI 精準描述資源與範例，並保持 idempotent 與一致錯誤碼。 Example: 在 Swagger 內為每個 path 撰寫清楚 summary/description。

### P3 Demo 不穩定與狀態遺失

Problem: PoC 部署在無狀態記憶體中，重啟即遺失資料，推理結果偶爾錯誤。 Root Cause: 缺乏持久化與重試機制；模型隨機性導致結果漂移。 Solution: 引入資料庫持久化購物車與訂單、實作 retry/back‑off 策略、加入驗證邏輯限制不合理輸入。 Example: 使用 Azure SQL 做資料持久化，於 API 建立交易鎖與日誌。

## Version Changes

- v1.0 (2025-08-03): 初始版本

