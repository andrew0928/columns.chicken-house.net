---
source_file: "_posts/2024/2024-08-04-llm-abstraction.md"
generated_date: "2025-08-03 15:00:00 +0800"
version: "1.0"
tools: github_copilot
model: claude_sonnet_3_5
---

# [架構師觀點] LLM 的抽象化介面設計 - 生成內容

## Metadata

### 原始 Metadata

layout: post
title: "[架構師觀點] LLM 的抽象化介面設計"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 

### 自動識別關鍵字

keywords:
  primary:
    - LLM
    - 抽象化介面設計
    - API設計
    - 架構設計
    - 介面設計
    - 軟體架構
  secondary:
    - OpenAI
    - Chat Completion
    - Assistant API
    - 工人智慧
    - 圖靈測試
    - POC設計
    - 框架設計
    - Uber模式
    - Session管理
    - Tool Use

### 技術堆疊分析

tech_stack:
  languages:
    - C#
  frameworks:
    - .NET
  tools:
    - Visual Studio
  platforms:
    - Windows
  concepts:
    - Interface Design
    - API Architecture
    - Abstraction Patterns
    - Software Engineering
    - Framework Development
    - Service Design

### 參考資源

references:
  internal_links:
    - Build School 分享主題
    - 架構師的修練系列文章
  external_links:
    - OpenAI Chat Completion API
    - OpenAI Assistant API
    - Microsoft Semantic Kernel
    - LangChain
    - Ollama API
    - LM Studio
    - Windows Copilot Runtime
    - OnnxRuntime
  mentioned_tools:
    - OpenAI API
    - Microsoft Semantic Kernel
    - LangChain
    - LM Studio
    - Ollama
    - Windows Copilot Runtime
    - OnnxRuntime
    - Uber Platform

### 內容特性

content_metrics:
  word_count: 2970
  reading_time: "10 分鐘"
  difficulty_level: "中級"
  content_type: "思考練習"

## 摘要

### 文章摘要

作者透過抽象化思考練習的方式，探討如何為LLM設計合適的介面架構。文章的起源是作者觀察到各大廠商的LLM API和SDK介面設計各有不同，從OpenAI的Chat Completion到Assistant API，從Microsoft Semantic Kernel到LangChain等開源框架，以及本地運行的LM Studio、Ollama等不同平台都有各自的介面規格。作者認為與其等待市場統一標準，不如透過自己重新發明輪子的方式來理解這些設計背後的思維邏輯。文章採用「工人智慧」的概念作為出發點，將LLM想像成真人提供問答服務，並以此為基礎設計抽象介面。作者提出了從簡單的IChatBot介面開始，逐步擴展到支援多工作者分配、會話狀態管理、工具使用等複雜功能的設計演進過程。文章強調這種自我練習的方法能夠幫助架構師建立深層的理解能力，當面對新技術時能夠快速掌握其設計脈絡，並具備預測技術發展方向的能力。作者分享了過去在Thread Pool、ORM、權限控制等領域採用相同方法獲得的寶貴經驗，說明了這種「重新發明輪子」的練習對於架構師能力提升的重要價值。

### 關鍵要點

- 透過自己重新發明輪子來理解技術背後的設計思維和原理
- 將LLM抽象化為「工人智慧」的概念，以真人服務的角度設計介面
- 從簡單的問答介面逐步演進到支援會話管理、工具使用的複雜系統
- 抽象化思考能夠幫助架構師精確運用各種成熟元件
- 透過POC驗證設計想法，與大廠方案對比來學習和改進
- 這種練習方法能夠培養預測技術發展方向的能力
- 架構設計的核心是定義良好的介面，所有軟體工程都從此發展
- 理解原理後再看規格文件會更有效率，避免死記硬背

### 寫在前面, "工人智慧" 的介面設計

作者以2010年代Uber等媒合平台的興起為背景，說明了「工人智慧」的概念。當時有些號稱人工智慧的聊天機器人，實際上背後是真人在操作，被稱為「工人智慧」。作者認為這個概念對於理解LLM的抽象設計很重要，因為無論背後是真人還是神經網路，使用者都是透過相同的聊天介面與服務溝通。這種思維方式幫助作者開始思考如何設計邊界和介面，為後續的POC練習建立基礎。作者將LLM想像成真人提供問答服務的API，這種類比讓整個API的設計脈絡變得更加清晰和直觀。

### 開始 coding

作者從最簡單的IChatBot介面開始設計，包含一個Ask方法接收問題並返回答案。隨著需求的演進，介面逐步發展到支援串流回應、多工作者分配、會話狀態管理等功能。文章提到了類似Uber的工作者分派機制，透過接線生(Operator)操作交換器(Switch)來分配真人工作者處理問題。作者透過class diagram展示了整個系統的架構設計，包含客戶端、分派系統、工作者等核心元件的關係。這個設計過程展示了如何從簡單的介面逐步演進到複雜的分散式系統架構。

### 定義: 圖靈測試, 如果我真的要寫成圖靈測試 APP

作者提出了IIntelligence介面的設計概念，將人工智慧和真人智慧都抽象為相同的介面。隨著對話複雜度的增加，引入了SessionState來管理對話的前後文歷史。為了支援大規模應用，需要SessionState的管理機制，包括Factory、Dispatch、Load Balancer等元件。作者對比了Uber時代透過平台化分配人力資源，與AI時代透過API Token直接獲取服務的差異。文章還提到了Tool Use功能的設計，將可用工具放入SessionState中，並修改Ask方法的回傳值來支援工具使用的結果。

### 架構師的學習方法論

作者強調這種自我練習方法的價值，說明與直接學習API規格相比，透過理解背後原理再看規格會更有效率。這就像學會英文後查字典確認拼字，而不是拿著字典學英文的差別。作者分享了過去在多個技術領域採用相同方法的經驗，包括文字模式視窗介面、Stack Machine、ORM設計、Thread Pool等。這些練習讓作者在面對新技術時能夠快速理解其設計脈絡，並具備預測技術發展方向的能力。當新版本發布時，能夠立即理解新功能的用途和價值，而不是被動地學習和適應變化。

## 問答集

### Q1: 為什麼要用「工人智慧」的概念來思考LLM介面設計？
Q: 將LLM抽象為真人服務有什麼設計上的好處？
A: 「工人智慧」的概念幫助我們從使用者角度思考介面設計。無論背後是真人還是AI，使用者都是透過對話與服務溝通。這種抽象讓我們專注於介面的一致性和易用性，而不會被底層實作細節影響設計思維。同時，這種類比也幫助理解會話狀態、工作者分配、回應時間等實際運營問題。

### Q2: 為什麼建議架構師要「重新發明輪子」？
Q: 自己實作POC與直接使用現成方案有什麼差別？
A: 重新發明輪子的目的不是要使用自己的實作，而是要理解設計背後的思維邏輯。透過自己實作，你會遇到所有主要的設計障礙和取捨考量，這讓你能夠精確理解和運用成熟的解決方案。當你有了自己的實作經驗，就能夠判斷大廠方案的優劣，並具備預測技術發展方向的能力。

### Q3: 如何從簡單的IChatBot介面演進到複雜的系統架構？
Q: 介面設計的演進過程中需要考慮哪些因素？
A: 從簡單的Ask方法開始，隨著需求增加逐步擴展功能。首先考慮串流回應的需求，然後是會話狀態管理、多工作者分配、工具使用等。每個階段都要考慮可擴展性、狀態管理、錯誤處理等問題。關鍵是保持介面的一致性，讓新功能能夠自然地融入現有架構中。

### Q4: SessionState在LLM介面設計中扮演什麼角色？
Q: 為什麼需要專門設計會話狀態管理機制？
A: SessionState負責管理對話的前後文歷史，這對於LLM的有效運作至關重要。它需要儲存對話歷史、可用工具、使用者偏好等資訊。在大規模應用中，SessionState的管理還涉及分散式儲存、狀態同步、工作者切換等複雜問題。良好的SessionState設計能夠確保對話的連貫性和系統的可擴展性。

### Q5: 這種學習方法如何培養預測技術發展的能力？
Q: 為什麼理解原理後就能預測新功能的出現？
A: 當你深入理解某個領域的核心問題和解決方案後，就能夠識別現有方案的限制和改進空間。你會開始思考「如果是我來設計，我會怎麼做」，這些思考往往與技術的實際發展方向一致。當新版本發布時，你會發現很多功能正是你認為「應該要有」的改進，這就是專業判斷力的體現。

## 解決方案

### 問題：如何為LLM設計統一的抽象介面
問題：面對各大廠商不同的LLM API規格，如何設計統一的抽象層？
根本原因：各廠商的API設計理念和應用場景不同，缺乏統一的抽象思維框架
解決方案：
- 從最基本的IChatBot介面開始，專注於核心的問答功能
- 使用「工人智慧」的概念，將LLM抽象為真人服務提供者
- 設計可擴展的介面架構，支援從簡單問答到複雜工具使用的演進
- 引入SessionState管理對話狀態和工具配置
- 建立統一的IIntelligence介面，讓人工智慧和真人智慧可以互換

基礎介面設計：
```csharp
interface IChatBot
{
    IEnumerable<string> Ask(string question);
}

interface IIntelligence
{
    string Ask(string question, SessionState session);
}

public class SessionState
{
    public IEnumerable<string> GetHistory() { ... }
    public Dictionary<string, Func> Tools { get; set; }
}
```

### 問題：如何設計支援大規模應用的LLM服務架構
問題：單一LLM服務如何擴展到支援多使用者、多工作者的分散式系統？
根本原因：缺乏對分散式系統設計原則的理解，以及會話狀態管理的複雜性
解決方案：
- 設計IOperator接線生介面負責工作者分派
- 實作ISwitch交換器介面管理連線和路由
- 建立無狀態的工作者設計，狀態資訊由SessionState統一管理
- 實作工作者切換機制，確保服務的連續性
- 考慮類似Uber的媒合平台架構，高效分配運算資源

架構設計：
```csharp
interface IOperator
{
    IWorker AssignWorker(SessionRequest request);
    void ReleaseWorker(IWorker worker);
}

interface ISwitch
{
    void Connect(IClient client, IWorker worker);
    void Transfer(SessionState state, IWorker newWorker);
}
```

### 問題：如何透過POC驗證設計想法並與業界標準對比
問題：自己的設計如何與OpenAI、Microsoft等大廠的方案進行有效對比？
根本原因：缺乏系統性的驗證方法和對比框架，無法客觀評估設計優劣
解決方案：
- 建立可執行的POC來驗證介面設計的可行性
- 對比分析OpenAI Chat Completion API和Assistant API的設計理念
- 研究Microsoft Semantic Kernel、LangChain等框架的抽象方式
- 分析本地運行方案（Ollama、LM Studio）的介面特點
- 透過實際場景測試來驗證設計的實用性

驗證方法：
- 實作基本的圖靈測試應用來驗證介面設計
- 對比Token計費、工具使用、會話管理等功能的實作方式
- 分析不同方案在可擴展性、效能、易用性方面的優劣
- 預測技術發展方向，提前準備介面的擴展空間

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本，基於原始文章內容生成
- 包含LLM抽象化介面設計的完整思考過程
- 提供從工人智慧概念到複雜系統架構的設計演進
- 分享架構師學習新技術的方法論和實踐經驗
