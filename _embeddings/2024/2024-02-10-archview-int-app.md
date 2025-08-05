---
- source_file: /docs/_posts/2024/2024-02-10-archview-int-app.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
# 替你的應用程式加上智慧! 談 LLM 的應用程式開發

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "替你的應用程式加上智慧! 談 LLM 的應用程式開發"
categories:
  - "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆","AI","Semantic Kernel"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-02-10-archview-int-app/2024-02-17-10-06-40.png

# 自動識別關鍵字
primary-keywords:
  - LLM (大型語言模型)
  - Semantic Kernel
  - Azure OpenAI
  - Copilot / Agent
  - RAG (Retrieval-Augmented Generation)
  - Function Calling / Skill / Plugin
  - Prompt Engineering
  - Andrew Shop PoC
secondary-keywords:
  - GPTs Custom Actions
  - Text Embedding
  - Vector Database
  - .NET 8 / C#
  - Chat History / Memory
  - Assistant API
  - Knowledge Base
  - Persona

# 技術堆疊分析
tech_stack:
  languages:
    - C#
    - Python (code-interpreter 示意)
  frameworks:
    - .NET 8
    - Microsoft Semantic Kernel (≥1.3)
  tools:
    - Azure OpenAI Service (GPT-4 1106-preview)
    - ChatGPT Plus (GPTs & Plugins)
    - GitHub Copilot
  platforms:
    - Azure
    - Windows / Android / iOS (OS-level Agent 想像)
  concepts:
    - RAG Pipeline
    - Skill / Plugin 註冊
    - Vector Embedding
    - Copilot Pattern
    - Persona 設定
    - Prompt / Planner / Memory

# 參考資源
references:
  internal_links:
    - /2024/01/15/archview-llm/
  external_links:
    - https://learn.microsoft.com/semantic-kernel/overview
    - https://platform.openai.com/docs/guides/function-calling
    - https://github.blog/2023-10-30-the-architecture-of-todays-llm-applications/
    - https://youtu.be/JhCl-GeT4jw
  mentioned_tools:
    - ChatGPT
    - GPT-4
    - GitHub Copilot
    - Azure OpenAI
    - Smalltalk (比喻)
    - Stack Overflow

# 內容特性
content_metrics:
  word_count: 15,600
  reading_time: "50 分鐘"
  difficulty_level: "進階 / 架構"
  content_type: "技術長文 / PoC 筆記"
  generated_at: 2025-08-06 00:00:42
```

---

## 文章摘要
作者延續先前「安德魯小舖 GPTs」實驗，進一步探討如何把 LLM 視為「能理解語意的人」，並用 Azure OpenAI + Semantic Kernel 重新開發智慧化應用。文章先拆解「讓 APP 加上智慧」的四級演進：  
1) 傳統操作模式；  
2) 關鍵環節用 AI 做風險評估；  
3) 全程 Copilot 式提示；  
4) 完整對話驅動，AI 代理使用者操作。  
對每級都提供 .NET 8 範例程式與 Console Demo，示範 LLM 如何透過 Skills（KernelFunction / API）完成購物流程，自動判斷商品、金額與限制並生成提醒。

第二部分聚焦架構視角，說明將 LLM 整進系統時必備的五大構件：LLM 大腦、Chat History（短期記憶）、Knowledge / RAG（長期記憶）、Skills / Plugins（才能）、Persona（角色）。作者逐一圖解這些構件如何在 Semantic Kernel 對應到 Model / Memory / Plugins，並分享 Attribute 標註 C# 方法即可讓 LLM 學會呼叫。文中以「店長助理」System Prompt、FAQ、技能簽章等示範 Prompt Engineering 關鍵性。

最後作者提出對軟體產業的展望：10 年內 AI 運算成本與可靠度將足以支撐「用自然語言寫程式」；Developer 的核心將從手刻程式碼轉向設計 Prompt、定義 Skill 與 orchestrate 任務。呼籲資深技術人放下舊有精準控制思維，先理解全貌，再判斷「該不該」導入 AI，而非只糾結「會不會」使用工具。

---

## 段落摘要

### 1. 「安德魯小舖」的進化
作者將傳統購物 APP 拆成四級智慧化過程，逐級以 Console 範例驗證：  
1-1 標準選單操作為對照組；  
1-2 結帳前由 LLM 檢查常識與風險（年齡、糖分等）；  
1-3 Copilot 監聽全程操作，依次發出 HINT／OK；  
1-4 允許自然語言一次下單，LLM 自動呼叫多個 API 完成交互。每級實作皆展示 System Prompt、User Prompt、Function Call Trace，突顯 Prompt 與 Skill 描述品質對結果影響。

### 2. 探索 LLM 應用的系統架構與開發框架
先以傳統 UI / Domain / Data 三層對照，引入 LLM + Chat History（短期）、RAG（長期）、Skill（才能）、Persona（角色）組成完整 Agent。接著解析 Text Embedding 與 Vector DB 在檢索增強中的角色；說明 Function Calling 讓 LLM 能「選用正確 API 並補齊參數」的突破。最後對照 Semantic Kernel 與 LangChain 把這些構件模組化，示例 C# Attribute 將方法暴露為 Kernel Plugin。

### 3. 未來的發展（個人觀點）
作者預期 AI 將使「自然語言 = 程式語言」成為十年內常態，Developer 轉型重點：Prompt Engineering、Skill 設計與 AI Orchestration。以 Smalltalk「message passing」類比 LLM 的不可預測性，強調企業早已容忍人類員工的不確定，同理應接受 AI 的機率性。引用多篇文章與演講（Matt Welsh「The End of Programming」等）佐證：真正的挑戰不是 AI 會不會出錯，而是我們如何在系統與流程上接納它並放大產能。

---

## 問答集

### 概念解釋
Q1: 什麼是 RAG？它在文章中扮演什麼角色？  
A1: RAG（Retrieval-Augmented Generation）是一種先檢索再生成的流程：把提問轉成向量到向量資料庫找相關知識片段，再連同上下文餵給 LLM 生成答案。作者用它為 LLM 注入「店長 SOP、FAQ」等長期記憶，避免大量 token 開銷，也讓回答更可靠。

Q2: Skill / Plugin 與傳統 API 有何差異？  
A2: Skill 仍是 API，但附帶完整自然語言描述與參數註解，使 LLM 能基於語意自行選用並補齊呼叫。重點在可被語言模型解析，而非只給開發者看的規格。

### 操作指導
Q3: 如何在 Semantic Kernel 暴露一個 Skill？  
A3: 在 C# 方法加上 [KernelFunction] 與 [Description] Attribute，於啟動時 `builder.Plugins.AddFromType<YourType>()` 註冊即可。LLM 便能讀取描述並於對談中嘗試呼叫。

Q4: 若想讓 Copilot 監聽操作歷程，需要哪些 Prompt 設計？  
A4: 作者在 System Prompt 加入「我已進行操作: XXX」規格，並規定 LLM 回 OK 或 HINT。每次 UI 動作後將敘述包成 User Prompt 發送，如此即可即時提示但不干擾正常流程。

### 問題排除
Q5: LLM 第一次沒提醒酒類限制，第二次才提醒，原因？  
A5: LLM 具有機率性，回應受上下文及溫度影響。第一次可能評估風險較低未觸發 HINT，第二次因重複行為與 FAQ 規則交叉影響而觸發。可透過降低 temperature 或加 stronger constraint 提升一致性。

Q6: 如何避免 LLM 誤呼叫錯誤 Skill？  
A6: 控制 Skill 數量、撰寫精準 Description，並在 System Prompt 加入使用守則；必要時於 Semantic Kernel 設定 FunctionFilter 進行白名單或參數驗證。

### 比較分析
Q7: 直接把應用放在 ChatGPT GPTs 與內嵌 SDK 差在哪？  
A7: GPTs 受制於 ChatGPT 流量與訂閱門檻，且難以整合現有登入、UI、快取。內嵌 SDK 可與原系統共用 session、權限與部署管線，更符合企業產品化需求。

### 進階思考
Q8: 為何作者認為資深工程師更易被舊習綁住？  
A8: 資深人員習慣明確規則與可預測流程，而 LLM 引入機率與黑箱特性，需要先接受「不精確但足夠好」的思維後再談工程控制，這與既有心智模式衝突。

Q9: LLM 不可預測性是否會阻礙關鍵業務？  
A9: 作者主張可用「人類員工也會犯錯」類比：系統應透過流程、回饋與多層檢查容納機率性，而非要求零錯；把 LLM 投入適合的任務並配合守門邏輯即可。

Q10: Prompt Engineering 與傳統 Coding 哪些能力重疊？  
A10: 都需理解 domain 規則、資料流與目標；差異在 Prompt 需「以人話表達約束與背景」，並考量 token 成本與模型行為，而非語法層面的迴圈與類別結構。

---

## 問題與解決方案

### 問題 1：如何讓傳統 APP 在不重寫 UI 的前提下取得 AI 智慧？
Root Cause：UI 與後端未暴露語意層，LLM 無法判讀意圖。  
Solution：以 Semantic Kernel 將現有核心服務包裝成 Skill；於關鍵節點插入 System + User Prompt 驅動 LLM；保留原 UI 僅增添提示區，即可漸進升級。  
Example：結帳前呼叫 `ShopFunction_EstimatePrice()` 並送出客戶註記，讓 LLM 根據 FAQ 自動生成 HINT。

### 問題 2：大規模知識無法塞進 Prompt 導致回答片段化
Root Cause：Token 成本高、上下文長度有限。  
Solution：導入 RAG，將 SOP、FAQ、歷史服務紀錄向量化存入 Vector DB；詢問時先檢索 top-k，再交由 LLM 組合。  
Example：店長助理需回答法規與飲料健康建議，從向量庫撈出對應段落後生成完整提醒。

### 問題 3：LLM 誤用 API 造成業務風險
Root Cause：Skill 描述不精確或缺乏授權機制。  
Solution：1) 精寫 Description；2) 使用 Semantic Kernel 的 FunctionFilter 進行參數驗證；3) 對敏感 Skill 添加二次確認。  
Example：`ShopFunction_Checkout` 前先 require LLM 回覆 `CONFIRM_checkout`，再由程式層核對金額一致性後真正執行。

### 問題 4：工程團隊難以接受 LLM 機率性
Root Cause：傳統 CI/CD 追求可重製結果，LLM 回覆具隨機性。  
Solution：將 AI 任務與決策點外掛為服務；以 A/B 測試收集資料；用 retry、temperature 控制與後置規則校正結果；保持核心交易流程 deterministic。  
Example：Copilot 的 HINT 僅提示不直接下單，真正下單仍走嚴格 API 與資料庫交易。

---

## 版本異動紀錄
- 1.0.0 (2025-08-06)  
  • 初版生成：含 Metadata 擴增、文章摘要、段落摘要、10 組 Q&A 與 4 組問題-解決方案。