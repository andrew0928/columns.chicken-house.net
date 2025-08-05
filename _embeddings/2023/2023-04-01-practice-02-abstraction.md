---
- source_file: /docs/_posts/2023/2023-04-01-practice-02-abstraction.md
- tools: BlogIndex.SyncPost 1.0.0
- model: o3, endpot: https://app-azureopenai.openai.azure.com/
---
[架構師的修練] #3 刻意練習──如何鍛鍊你的抽象化能力 摘要

## Metadata
```yaml
# 原始 Front Matter
layout: post
title: "[架構師的修練] #3, 刻意練習 - 如何鍛鍊你的抽象化能力"
categories: ["系列文章: 架構師的修練"]
tags: ["系列文章", "架構師的修練", "架構師觀點", "刻意練習", "抽象化"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo:

# 自動識別關鍵字
primary-keywords:
  - 抽象化 (Abstraction)
  - 刻意練習 (Deliberate Practice)
  - Interface 設計
  - ChatGPT / AI 助理
  - 折扣規則計算
  - API First
secondary-keywords:
  - .NET / C#
  - Github Copilot
  - Prompt Engineering
  - 電輔車心法 (e-Bike Analogy)
  - 黃金圈 (Why / How / What)
  - Code POC
  - 規格驅動開發 (Spec-Driven Dev)

# 技術堆疊
tech_stack:
  languages:       [C#]
  frameworks:      []
  tools:           [ChatGPT, GitHub Copilot, Visual Studio / VS Code]
  platforms:       [.NET Core / .NET 6+, OpenAI API]
  concepts:
    - Interface & Contract-First 設計
    - 折扣引擎 / Rule Engine
    - Deliberate Practice Framework
    - API First / Spec First

# 參考資源
references:
  internal_links:
    - https://columns.chicken-house.net/2016/05/05/archview-net-open-source/
    - https://columns.chicken-house.net/2020/03/10/interview-abstraction/
  external_links:
    - https://openai.com
    - https://github.com/features/copilot
    - https://skoda-eddie.blogspot.com/2022/03/blog-post_25.html
  mentioned_tools:
    - ChatGPT
    - GitHub Copilot
    - Visual Studio
    - AI Test Generator

# 內容特性
content_metrics:
  word_count: 5600           # 估算
  reading_time: "18 分鐘"
  difficulty_level: "中高階"
  content_type: "技術隨筆 / 架構思維"
  last_generated: "2025-08-06 00:12:08"
  version: "1.0.0"
```

## 文章層級摘要（10-20 句，<1000 字）

作者以多年來持續推廣「API First」與「刻意練習」的經驗，重新檢視「抽象化」這項核心能力在 AI 時代的重要性。文首先回顧 2016 年及 2020 年兩篇舊文，說明自己如何從 Microsoft 封閉轉向開放、再到面對 ChatGPT 帶來的工作模式衝擊。作者選擇面試中命中率不到 10% 的「零售折扣計算介面」題目，拿 ChatGPT 做實測：僅以三句需求，即獲得具擴充性、含折扣明細與提示的 C# interface 與兩組規則實作。接著再追加「整車購物車」及「優惠券」等變更，AI 仍能迅速迭代出可用設計，令作者兩度震撼。  
透過實驗，作者體悟：1) AI 已能處理設計／應用層級工作；2) 人類優勢轉向「問對問題、判斷好壞、抽象化對應需求」；3) 想善用 AI，必須有基礎知識與刻意練習，能快速驗證並修正 AI 輸出。文章以電輔車類比：體力＝Skill 交給 AI；控制＝決策留給人；經驗＝刻意練習累積。展望未來五年，程式撰寫、測試產生將高度自動化，唯有「定規格、抽象化、API 與資料管線」仍需架構師主導。最後作者預告後續將以「生命遊戲」與團隊實務練習，示範如何系統化鍛鍊抽象化思考。

## 段落層級摘要（依主要 H2）

1. 引言：舊文回顧與 AI 衝擊  
   作者翻出 2016、2020 兩篇舊文，感懷微軟生態變革與 ChatGPT 帶來的再一次洗牌，引出本篇主軸──抽象化練習在 AI 時代更顯關鍵。  

2. ChatGPT 折扣介面實測  
   僅三句需求即獲得 IRetailDiscountCalculator 設計與範例實作，證明 AI 已能完成中高階軟體設計；亦顯示良好 Prompt 與判斷力的重要。  

3. 迭代：加入購物車與優惠券  
   透過連續提問，AI 依序改為 List<CartItem>、加入 Coupon 參數等設計；雖有輸出參數語意小瑕疵，但整體已極具可用性，反映 AI 遇強則強特性。  

4. 反思：人與 AI 的角色分工  
   AI 可快速補足 Skill，但 WHY / 抽象決策仍仰賴人。要競爭的是「比 AI 更懂抽象、更能判斷」的人，而非手動重複寫 Code 的人。  

5. 電輔車比喻與能力矩陣  
   體力＝技能、控制＝決策、經驗＝練習；AI 如助力馬達，能放大有經驗者的輸出，同時無差別碾壓純勞力型知識工作者。  

6. 未來五年與 Spec-Driven 開發  
   當 AI 可自產 Code/Tests，最具價值的工作是「訂規格、維運 API、治理資料」。抽象化與 API First 將決定 AI 能否帶來倍增效果。  

7. 刻意練習計畫與文章結構  
   作者說明本系列第三、四篇將結合 .NET Conf 演講與「生命遊戲」練習，提供讀者與團隊可落地的練習流程與題庫。  

## 問答集（10 組）

Q1 什麼是「抽象化能力」，為何在 AI 時代更重要？  
A: 抽象化是將複雜需求映射成可重複、可組合的介面 / 模組。AI 已能寫程式與產生測試，唯有訂出正確抽象與規格、人才能確保 AI 走在正確方向，並判斷輸出品質，因此抽象化更成為決勝點。

Q2 作者如何用 ChatGPT 驗證折扣計算介面？  
A: 先給三句需求（可擴充規則、需列折扣與提示），ChatGPT 即回傳包含 IRetailDiscountCalculator 與 CalculationResult 的 C# 碼，再進一步請 AI 實作兩組規則，完成 POC。  

Q3 AI 輸出的設計存在哪些小問題？  
A: 第三輪迭代中，AI 把折扣結果 List 傳入當參數而非輸出語意，還可用 out 或 Tuple 改進；顯示 AI 尚未完全掌握語義細節，需要人類介入微調。  

Q4 如何確保自己能「問對問題」？  
A: 需理解領域需求、掌握設計原則與最佳實踐，再將核心條件轉化為具體且完整的 Prompt；同時準備期望輸出格式，以便快速驗證。  

Q5 如果完全不懂程式，AI 能讓你瞬間變專家嗎？  
A: 否。AI 可生成程式碼，但不懂基礎者難以分辨好壞、無法追問或整合；最終仍卡在維護與迭代。  

Q6 電輔車比喻對軟體開發的啟示？  
A: AI 如馬達可省去體力活（寫樣板 Code），但路線判斷與煞車仍靠騎士（架構師）。有經驗者可用同樣時間走更遠，無經驗者則可能失控。  

Q7 未來五年哪些能力最可能被 AI 取代？  
A: 重複性高、標準化、可由大量資料訓練的 Skill 層，例如樣板程式撰寫、簡單測試撰寫、文件生成。  

Q8 哪些能力短期內難被 AI 取代？  
A: 需求抽象、跨系統協調、商業取捨決策、API 與資料治理，及對複雜情境的道德／社會判斷。  

Q9 如何在團隊導入「刻意練習」？  
A: 制定練習題（如生命遊戲）、明確目標技能、設置檢核標準、定期回饋；結合 AI 助教角色，加快迭代。  

Q10 如果想立即開始練習抽象化，作者建議的第一步？  
A: 挑選一個小而完整的業務情境（如折扣引擎），先手動設計介面，接著用 ChatGPT 做多輪對話產生實作，再審核、重構、比較差異，培養分解與評估能力。  

## 問題與解決方案

Problem 1: 如何在 AI 時代保持個人技術競爭力？  
Root Cause: 過度依賴技能層工作，缺乏抽象化與規格制定能力。  
Solution: 1) 系統化刻意練習抽象化；2) 用 AI 當練習助教快速 POC；3) 聚焦 Spec-Driven Dev 與 API First。  
Example: 將零售折扣業務拆分為 IDiscountCalculator interface + 多個 plugin，交給 AI 實作，再由人類優化抽象細節。

Problem 2: 如何有效驗證 AI 產生的程式碼？  
Root Cause: 人工 Review 成本高且難以覆蓋邊角。  
Solution: 以同一份規格再讓 AI 生成測試案例，自動交叉驗證。  
Example: 需求→Spec→AI 產生折扣引擎與 xUnit 測試，CI 跑綠燈即通過。

Problem 3: 團隊成員差異大，練習難度無法統一？  
Root Cause: 缺乏分層練習機制。  
Solution: 以「基礎語法→小型抽象→跨域設計」三段式題庫，並提供 AI hints；進階者可挑戰多系統整合。  
Example: 生命遊戲→折扣引擎→微服務購物車。

## 版本紀錄
1.0.0 (2025-08-06): 首次生成摘要、Metadata 擴增、段落摘要、10 組 Q&A 與 3 項問題-解決方案。