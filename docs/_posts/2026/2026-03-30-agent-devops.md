---
layout: post
title: ""
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---


# 一、更新後文章結構（以 Agent 開發流程為主軸）

## 文章主題（建議）

**Agent 的開發方式演進：用 Coding Agent + SDK 重建從需求到營運的完整流程**

---

## 0. 開場：為什麼 Agent 開發不能沿用傳統軟體流程

* Agent 與傳統軟體的本質差異

  * 處理不確定性
  * 以模型推理與工具協作為核心
  * 流程動態、結果機率性高
* 因此不能只用傳統 application / UI 的心智模型來開發
* 本文主張：應以 **5 階段流程** 來看 Agent 開發

---

## 1. 需求分析：先定義 Skill + Tools，而不是先畫 UI / API

> 對應你定義的第 1 步

### 1.1 Agent 的需求分析在分析什麼

* 不只是功能需求，而是「任務完成能力」需求
* 要先定義成功條件、失敗邊界、人工介入點

### 1.2 從專家流程拆解需求

* 訪談專家
* 拆成可驗證的任務步驟
* 評估哪些步驟 AI 能做、哪些需要工具補足

### 1.3 Skill + Tools 的需求規格化

* Skill：流程知識、操作策略、上下文使用方式
* Tools（MCP / scripts / CLI / APIs）：對外部系統的操作能力
* 需求分析的輸出物：初版 Skill/Tools 設計清單

---

## 2. 設計驗證：用 Prototype（based on Coding Agent）收斂設計

> 對應你定義的第 2 步

### 2.1 為什麼 Agent 設計驗證要用 Prototype

* 文字 spec 很難描述不確定性情境
* 可執行 Prototype 更適合驗證流程、例外狀況與結果品質

### 2.2 用 Coding Agent 建立 Prototype 的做法

* instructions / prompts / skills / tools / workspace 配置
* 產出 markdown / 附檔 / 操作結果
* 直接讓專家或內部用戶試用

### 2.3 Prototype 驗證的重點

* 任務完成率
* 失敗型態
* 工具使用是否穩定
* 是否需要調整 Skill 或人機分工

### 2.4 從 Prototype 萃取設計（可銜接後續開發）

* 將已驗證流程轉成可實作的設計輸入
* 建立 SDK 開發前的「已收斂版本」

---

## 3. 開發：用 Agent SDK 將已驗證能力整合進正式服務

> 對應你定義的第 3 步

### 3.1 SDK 在流程中的正確位置

* SDK 不是起點，而是產品化階段的整合工具
* 目標是搬運 Prototype 已驗證的能力，而非重造一套 Agent

### 3.2 開發工作的重點（Agent SDK 階段）

* 串接既有 service / UI / API
* 權限與身份管理
* 工作流程控制與錯誤處理
* 服務化與版本管理

### 3.3 這樣做的價值

* 工程投入更聚焦
* 減少把時間浪費在 Agent plumbing
* 更快把能力融入正式產品

---

## 4. 部署：依 Agent 特性設計 Sandbox 與部署模式

> 對應你定義的第 4 步（這段會很有亮點）

### 4.1 為什麼 Agent 的部署和傳統服務不同

* Agent 會調用 tools、處理檔案、執行多步流程
* 對執行環境隔離、權限、安全與可觀測性要求更高

### 4.2 Sandbox 的角色

* local machine 驗證 vs cloud sandbox 正式運行
* 隔離執行、限制權限、資源與網路控管
* 讓 Agent 能安全使用工具與外部系統

### 4.3 技術選型如何影響部署方式

* in-process（library 型）vs out-of-process（remote-control 型）
* CLI-based / SDK-based 架構對部署拓樸的影響
* 容器化、版本解耦、獨立升級策略

### 4.4 從 local machine 到 cloud 的平順轉移

* Prototype 環境與產品環境一致性的重要性
* 你主張的做法：用 Coding Agent + SDK 降低遷移摩擦

---

## 5. 服務品質評估與回饋修正：Agent 版的品質管理與迭代

> 對應你定義的第 5 步，也是 BizDevOps 的核心落點

### 5.1 Agent 服務的品質不是只有功能是否完成

* 任務成功率 / 失敗率
* 人工接手率
* 成本（token、工具、時間）
* 使用者信任與可接受程度

### 5.2 需要觀測什麼（Ops 面）

* 任務執行紀錄
* 工具調用結果與錯誤型態
* 不同輸入情境的品質差異
* Sandbox / 執行環境穩定性

### 5.3 回饋修正的對象（Dev 面）

* Skills
* Tools / MCP
* prompts / instructions
* 人機分工邊界
* 部署與權限策略

### 5.4 Agent 的 BizDevOps 循環（整體收斂）

* 需求（Skill + Tools）→ Prototype 驗證 → SDK 開發 → Sandbox 部署 → 品質觀測 → 回饋修正
* 與傳統 App 開發循環的差異：從「功能迭代」轉為「任務能力迭代」

---

## 6. 補充：Claude Agent SDK vs GitHub Copilot SDK 的應用場景（放在流程脈絡內）

> 你原本要保留的 SDK 比較，現在改成支援流程選型，而不是獨立評測

### 6.1 設計哲學：減法 vs 加法

* Claude Agent SDK（減法）
* GitHub Copilot SDK（加法）

### 6.2 在「開發階段」的選型考量

* 深度客製 vs 快速搬運驗證成果
* Node/Python 生態 vs 多語言整合需求

### 6.3 在「部署階段」的選型考量

* in-process vs remote-control
* 分散式部署、容器化、版本管理策略

### 6.4 實務建議

* 不先問哪套 SDK 最強
* 先問你的 Agent 在流程中要解什麼問題

---

## 7. （預留）實際案例：用 SDK 開發 Agent 應用

* 案例背景與目標
* 需求分析（Skill + Tools）
* Prototype 驗證方式
* SDK 開發與整合
* Sandbox 部署與品質觀測
* 修正與迭代結果

> ✅ 這章保留，之後你補案例時可以直接填入，不用重改架構。

---

## 8. 結論：Agent 開發不是傳統軟體流程加上 AI，而是新的工程方法

* 用 5 階段流程收束全文
* 強調 Agent / Chat 是新一代服務模式，不只是 UI 替換
* 給讀者的行動建議：先從任務能力與 Prototype 驗證開始，再談 SDK 與部署

---

# 二、內容簡介短文（約 300 字）

在 AI 時代，Agent 類型的軟體已經不只是「傳統應用程式加上一個聊天介面」。它處理的是不確定性問題：輸入不穩定、流程動態、結果具機率性，核心能力建立在模型推理（GPU）與工具協作之上，而不再只是資料庫欄位、固定演算法與明確流程控制。這也代表，分析、設計、開發、部署與品質管理的方法，不能再沿用既有 application/UI 的做法。

本講將 Agent 開發流程整理為五個階段：**需求分析（Skill + Tools）→ 設計驗證（以 Coding Agent 為核心的 Prototype）→ 開發（用 Agent SDK 整合）→ 部署（依 Agent 特性規劃 Sandbox 與技術選型）→ 服務品質評估與回饋修正**。我會從實務經驗回顧 Agent 架構的演進（Model → Agent → Skill），並討論如何讓能力從 local machine 的驗證環境，平順轉移到 cloud sandbox 與正式服務。同時也會比較 GitHub Copilot SDK 與 Claude Agent SDK 在不同開發/部署情境下的適用場景，說明如何用 Coding Agent + SDK 建立可落地、可迭代的 Agent 產品開發方法。

---


