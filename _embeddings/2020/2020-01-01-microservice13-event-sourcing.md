---
source_file: "_posts/2020/2020-01-01-microservice13-event-sourcing.md"
generated_date: "2025-08-03 15:30:00 +0800"
version: "1.0"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# 微服務架構設計 - Event Sourcing - 生成內容

## Metadata

### 原始 Metadata
```yaml
layout: post
title: "微服務架構設計 - Event Sourcing"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "架構師", ]
published: false
comments: true
redirect_from:
logo: 
```

### 自動識別關鍵字
keywords:
  primary:
    - Event Sourcing
    - Cloud Native
    - 微服務架構
    - CQRS
    - 分散式系統
  secondary:
    - Message Queue
    - Streaming Data Processing
    - 資料一致性
    - 校正回歸
    - 時間維度

### 技術堆疊分析
tech_stack:
  concepts:
    - Event Sourcing
    - CQRS (Command Query Responsibility Segregation)
    - DDD (Domain Driven Development)
    - Cloud Native
    - Microservices
  patterns:
    - Message Queue
    - Streaming Data Processing
    - No SQL (key value store)
    - MapReduce
    - SAGA patterns
  platforms:
    - Google Cloud Platform
    - Kubernetes
    - BigTable

### 參考資源
references:
  external_links:
    - https://martinfowler.com/eaaDev/EventSourcing.html
    - https://zhuanlan.zhihu.com/p/38968012
    - https://www.infoq.cn/article/L*bT1UfuVoj1I6NRNM3U
  mentioned_concepts:
    - Martin Fowler Event Sourcing
    - Google MapReduce
    - Container Orchestration
    - 深入淺出Event Sourcing和CQRS

### 內容特性
content_metrics:
  word_count: 12500
  reading_time: "20 分鐘"
  difficulty_level: "高級"
  content_type: "架構觀念"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)
作者深入探討Event Sourcing在微服務架構中的應用，不僅介紹了Event Sourcing的基本概念，更從Cloud Native的角度解釋為何需要這種設計模式。文章以銀行存摺為例說明Event Sourcing的核心理念：儲存的不是最後的資料，而是記錄讓資料改變的資訊歷程。作者強調Event Sourcing並非單純為了處理巨量資料，而是Cloud Native整體思維下的一個常用pattern，通常需要搭配CQRS來發揮最大效益。文章後半部以疫情期間的「校正回歸」現象為例，深刻說明了在即時性需求與資料處理延遲之間的矛盾，並提出使用Event Sourcing + CQRS來解決時間維度問題的架構方案。

### 關鍵要點 (Key Points)
- Event Sourcing的核心是儲存資料變更的歷程而非最終狀態
- Cloud Native思維下，Event Sourcing是處理大規模分散式系統的重要模式
- 需要搭配CQRS來處理查詢與命令的責任分離
- 即時性需求與資料處理延遲的矛盾是現代系統的普遍挑戰
- 時間維度是分散式系統設計中必須考慮的重要因素

### 段落摘要 (Section Summaries)

1. **Event Sourcing簡介**：作者以銀行存摺為例解釋Event Sourcing的基本概念，強調其核心理念是記錄資料變更的歷程而非最終狀態。這種設計的好處包括能完整保存異動過程、在需要時能重新還原過程、以及資料只會新增不會更新或刪除的特性。作者特別指出，Event Sourcing適合交易相關的資料處理，因為需要保留完整的流水帳記錄。然而這種設計也有明顯的缺點，就是需要耗費大量的儲存空間和運算能力，因此不見得適用於所有場景。

2. **Cloud Native架構設計觀念**：作者詳細闡述了從傳統企業IT到Cloud Native的架構演進過程，特別提到Google在處理大規模系統時的核心觀念轉變。在傳統架構中，系統依賴高級硬體來提升可靠度，但在雲端規模下，硬體故障變成不可避免的常態。因此Google發展出在軟體層面允許設備故障的設計理念，包括BigTable這類儲存方式和MapReduce運算模式。作者強調，Cloud Native不只是流量大或交易量大的差異，而是計算架構的本質性改變，需要完全不同的設計方式。

3. **Event Sourcing在Cloud Native中的定位**：作者認為Event Sourcing本質上是純架構的選擇，是為了同時保存原始event記錄，並用streaming processing的方式在收到資料時就處理好，直接以查詢需要的方式預先處理後存下來。這種設計犧牲了強一致性來換取最終一致性，能夠支撐更大的處理規模。作者特別強調，關聯式資料庫強調正規化和一致性，而Cloud Native的策略則是在收到資料時就做好必要的處理和複寫，透過可靠的通訊機制來確保資料的序列化執行。

4. **校正回歸現象的系統架構分析**：作者以疫情期間的「校正回歸」現象為例，深入分析了即時性需求與資料處理延遲之間的矛盾。當系統期待的資訊回應速度與資料收集處理的延遲產生落差時，就會出現需要修正歷史資料的情況。作者提出了實際的解決方案，包括定義資料發生時間與收到時間的差異、善用Event Sourcing機制按時間序處理、使用CQRS模式來呈現不同的統計需求，以及定義系統能忍受的最大延遲時間。這種架構設計能夠兼顧系統的回應時間、資料的正確性和處理架構的優雅性。

## 問答集 (Q&A Pairs)

### Q1: 什麼是Event Sourcing？
Q: Event Sourcing的核心概念是什麼？
A: Event Sourcing的核心理念是儲存的不是最後的資料，而是記錄讓資料改變的資訊歷程。如果能完整記錄這些歷程，就有能力還原任何時間點的資料狀態。就像銀行存摺一樣，記錄每一筆進出款項的異動，最後附上結算餘額。

### Q2: Event Sourcing有什麼優缺點？
Q: 採用Event Sourcing設計有哪些優點和缺點？
A: 優點包括：1)完整保存資料異動順序和過程 2)能在需要時重新還原過程 3)來源資料只會新增，不會更新或刪除，適合交易相關資料處理。缺點則是必須耗費大量的storage和運算能力，開發人員的技能要求門檻也較高。

### Q3: 為什麼說Event Sourcing是Cloud Native的一部分？
Q: Event Sourcing與Cloud Native架構有什麼關係？
A: Event Sourcing是Cloud Native整體思維下的一個常用pattern。在Cloud Native架構中，當運算規模大到某個程度時，需要採取不同的處理策略，犧牲強一致性換取最終一致性，用streaming processing方式處理資料，支撐更大的處理規模和線性擴充能力。

### Q4: 什麼是CQRS，為什麼要搭配Event Sourcing？
Q: CQRS是什麼概念，為什麼需要與Event Sourcing一起使用？
A: CQRS是Command Query Responsibility Segregation（命令與查詢責任分離）。Event Sourcing記錄異動歷程，但不利於頻繁計算最終結果的操作，因此需要搭配CQRS同步更新aggregation view，分別處理資料異動和查詢需求。

### Q5: 什麼情況下需要考慮Event Sourcing？
Q: 在什麼場景下應該認真考慮使用Event Sourcing？
A: 當系統需要同時保存原始event記錄，並用streaming processing方式在收到資料時就處理好，直接以查詢需要的方式預先處理後存下來時。通常不會單獨使用Event Sourcing，而是作為整體Cloud Native架構的一部分。

### Q6: 校正回歸現象在系統架構中代表什麼問題？
Q: 疫情期間的「校正回歸」現象反映了什麼系統問題？
A: 這反映了系統期待的資訊回應速度與資料收集處理延遲之間的矛盾。當即時性需求越來越高，但資料處理速度跟不上時，就會出現需要修正歷史資料的情況。這是現代系統普遍面臨的時間維度問題。

### Q7: 如何解決資料延遲與即時性需求的矛盾？
Q: 如何在系統架構上解決資料處理延遲與即時性需求的衝突？
A: 可以採用以下策略：1)定義資料發生時間與收到時間的差異 2)善用Event Sourcing按時間序處理 3)使用CQRS模式建立不同的view來滿足不同呈現需求 4)定義系統能忍受的最大延遲時間，超過則走例外處理流程。

### Q8: Cloud Native與傳統架構的本質差異是什麼？
Q: Cloud Native架構與傳統三層式架構有什麼根本上的不同？
A: 傳統架構依賴高級硬體和強一致性來確保可靠度，而Cloud Native架構則接受硬體故障為常態，在軟體層面設計容錯機制。在資料處理上，傳統架構強調正規化和即時join，Cloud Native則在收到資料時就做好處理和複寫，犧牲強一致性換取最終一致性和更大的擴充能力。

## 解決方案 (Solutions)

### P1: 需要完整記錄資料異動歷程
Problem: 系統需要保留完整的資料變更記錄，並能在需要時重新還原任何時間點的狀態
Root Cause: 傳統CRUD模式只保存最終狀態，缺乏變更歷程的完整記錄，無法支援資料回溯和重新計算需求
Solution: 
- 採用Event Sourcing模式，將所有資料異動記錄為事件流
- 設計不可變的事件記錄，只允許新增不允許修改或刪除
- 實現事件回放機制，能從事件流重新計算任意時間點的狀態
- 搭配CQRS模式，分離命令和查詢的責任

Example: 
```
// 銀行存摺記錄模式
Event: { timestamp: "2020-01-01 10:00", type: "deposit", amount: 1000 }
Event: { timestamp: "2020-01-01 15:00", type: "withdraw", amount: 500 }
// 可以重新計算任何時間點的餘額
```

### P2: 分散式系統的資料一致性問題
Problem: 大規模分散式系統中難以維持強一致性，需要在一致性和可用性之間取得平衡
Root Cause: 傳統關聯式資料庫的強一致性機制在分散式環境下成為效能瓶頸，無法支撐大規模的線性擴充
Solution:
- 採用最終一致性模型，接受短期的資料不一致
- 使用Message Queue確保事件的可靠傳遞和順序處理
- 實現冪等性設計，確保重複處理不會造成錯誤
- 建立事件驅動的微服務架構，每個服務維護自己的資料狀態

Example:
```
// 事件驅動的資料同步
AccountService -> EventBus -> [BalanceService, NotificationService, AuditService]
// 每個服務根據事件更新自己的view
```

### P3: 即時性需求與資料處理延遲的矛盾
Problem: 系統需要提供即時報表，但部分資料來源有處理延遲，造成資料不完整或需要後續修正
Root Cause: 資料收集和處理的物理限制無法滿足業務對即時性的要求，形成系統架構上的根本矛盾
Solution:
- 區分即時資訊和歷史資訊的處理邏輯
- 建立多層次的資料呈現機制：即時部分資料、完整歷史資料、修正通知
- 定義資料發生時間和收到時間的差異，支援資料回填
- 設定最大容許延遲時間，超過則走例外處理流程

Example:
```
// 分層資料呈現
即時報表: 顯示已收到的資料 + "部分資料處理中"警告
歷史報表: 等待完整資料後產生
修正通知: 當延遲資料到達時發送alert並更新歷史資料
```

### P4: 系統架構無法支撐大規模擴充
Problem: 傳統架構在達到一定規模後效能急劇下降，無法線性擴充
Root Cause: 傳統架構依賴集中式處理和強一致性約束，造成擴充瓶頸和單點故障風險
Solution:
- 實施Cloud Native設計理念，接受故障為常態
- 採用分散式資料處理模式，將運算送到資料所在位置
- 使用水平擴充策略，透過增加節點提升處理能力
- 實現無狀態服務設計，支援彈性擴縮容

Example:
```
// MapReduce模式
Query -> [DataNode1, DataNode2, DataNode3] -> Local Processing -> Result Aggregation
// 避免大量資料傳輸，提升處理效率
```

### P5: 多種資料呈現需求的架構設計
Problem: 同一份資料需要支援多種不同的查詢和呈現方式，傳統單一資料模型無法滿足
Root Cause: 不同業務場景對資料的組織和呈現方式有不同要求，單一正規化模型難以兼顧所有需求
Solution:
- 實施CQRS模式，為不同查詢需求建立專門的view
- 使用Event Sourcing作為唯一的事實來源
- 根據業務需求建立多個materialized view
- 透過事件流同步更新各個view的資料

Example:
```
// CQRS多view設計
Events -> [財務報表View, 營運分析View, 稽核追蹤View]
// 每個view針對特定查詢需求優化資料結構
```

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本，基於原始文章生成
- 涵蓋Event Sourcing基本概念、Cloud Native架構理念、校正回歸現象分析
- 包含8個Q&A對和5個解決方案
