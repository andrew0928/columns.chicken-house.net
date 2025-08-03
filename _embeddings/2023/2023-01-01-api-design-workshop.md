---
source_file: "_posts/2023/2023-01-01-api-design-workshop.md"
generated_date: "2025-01-03 16:00:00 +0800"
version: "1.1"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# 架構師觀點 - API Design Workshop - 生成內容

## Metadata

### 原始 Metadata
```yaml
layout: post
title: "架構師觀點 - API Design Workshop"
categories:
- "系列文章: 微服務架構"
tags: ["系列文章", "架構師的修練", "microservices"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2023-01-01-api-design-workshop/slides/slides-01.png
```

### 自動識別關鍵字
keywords:
  primary:
    - API Design
    - API First
    - 物件導向
    - 狀態機
    - REST API
    - 架構設計
  secondary:
    - OOP
    - State Machine
    - 微服務
    - Contract First
    - 狀態轉移
    - 授權機制
    - Entity Design
    - Event Driven Architecture

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - Java
    - C++
  frameworks:
    - ASP.NET Core
    - REST
  tools:
    - Visual Studio
    - Swagger
    - OpenAPI
    - AsyncAPI
  platforms:
    - .NET
  concepts:
    - Object Oriented Programming
    - Finite State Machine
    - API First Development
    - Contract First
    - Event Driven Architecture

### 參考資源
references:
  internal_links:
    - /2020/03/10/interview-abstraction/
    - /2022/10/26/apifirst/
  external_links:
    - https://www.ithome.com.tw/article/38577
    - https://www.learncpp.com/cpp-tutorial/the-virtual-table/
    - https://learn.microsoft.com/zh-tw/dotnet/api/system.security.principal.iidentity
    - https://learn.microsoft.com/zh-tw/dotnet/api/system.security.principal.iprincipal
    - https://learn.microsoft.com/zh-tw/dotnet/api/system.security.claims.claimsprincipal
    - https://www.asyncapi.com/blog/openapi-vs-asyncapi-burning-questions
  mentioned_tools:
    - C#
    - Java
    - C++
    - Swagger
    - OpenAPI
    - AsyncAPI
    - Mermaid
    - Visual Studio

### 內容特性
content_metrics:
  word_count: 15000
  reading_time: "45 分鐘"
  difficulty_level: "進階"
  content_type: "教學"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)

作者在這篇文章中深入探討了 API First 開發方法的實際應用，從物件導向思維出發，系統性地介紹了 API 設計的完整流程。文章的核心理念是將物件導向的設計思維運用到 REST API 的規格設計上，透過狀態機分析來建構穩健的 API 架構。作者強調，成功的 API 設計關鍵在於掌握物件導向的基本精神，特別是封裝的概念，將複雜的商業邏輯封裝在明確定義的介面之後。文章提供了一個完整的會員註冊系統案例，從狀態圖的建立、行為的定義、角色的標記到事件的規劃，展示了如何將抽象的設計概念轉化為具體的 API 規格。作者特別強調了 Contract First 的開發流程優勢，指出這種方法能夠讓前後端團隊同步開發，並且能夠在設計階段就考慮安全性問題。

### 關鍵要點 (Key Points)

- API First 的核心是將物件導向的介面設計概念應用到 REST API 設計上
- 狀態機是 API 設計的基礎工具，能夠明確定義物件的生命週期和允許的操作
- Contract First 開發流程能夠提早確認設計正確性，降低開發風險
- 良好的 API 設計應該從商業邏輯的本質出發，而不是單純針對需求開發
- 封裝原則要求物件狀態只能透過定義的方法來改變，不能直接修改
- 授權機制應該在設計階段就考慮，並且要細緻到操作層級
- 事件驅動架構是現代 API 設計不可忽視的重要環節

### 前言: 習慣物件導向的思考方式

作者在前言中闡述了自己偏好基本功夫組合應用的設計哲學，反對過度依賴複雜方法論的做法。作者認為物件導向是解決設計問題的基礎工具，比起 DDD 等系統性方法論，更適合作為思考的起點。文中提到了一個重要觀念：「物件導向技術，就是模擬世界，加以處理」，這句話成為作者理解 OOP 的關鍵。作者展示了如何將 C# 類別的設計直接對應到 REST API 的路徑結構，例如靜態方法對應到不需要實體 ID 的操作，而實體方法則對應到需要指定 ID 的操作。這種對應關係使得 API 的設計變得有系統性和邏輯性，而不是隨意的端點集合。作者強調掌握 OOP 基本精神的重要性，並且建議不熟悉 OOP 的開發者應該將此視為基本功來練習。

### 0. 正文開始

作者說明了這篇文章是基於 .NET Conf Taiwan 2022 的演講內容擴展而成，主要聚焦在 API First 的「如何實作」層面。文章將從四個面向來探討 API 設計：規格優先的開發流程改變、設計方式的改變與標準化、從設計階段考慮安全性、以及思考是否過度設計。作者通過一個 OAuth2 授權確認畫面的案例，引導讀者思考 API 設計中的安全性考量。這個案例凸顯了兩個建立信任的方式：技術規格保證和品牌信譽保證，其中技術規格保證正是本文要探討的重點。作者強調 API 設計的困難在於無法預期使用者的呼叫方式和順序，因此必須對服務領域有深度掌握，從開放服務的角度來設計 API 規格。

### 1. 開發流程上的改變

作者詳細比較了 Code First 和 Contract First 兩種開發方式的差異。在 Code First 的模式下，開發者先實作功能讓程式能運作，接著重構並加入 API 層，最後開發客戶端程式。而 Contract First 的模式則是先定義 API 規格並準備 Mock，然後前後端可以同時開發，最後進行整合測試。這種流程上的改變帶來顯著的好處：不同角色的團隊成員可以同步作業，包括架構師可以提早驗證設計、開發和測試人員可以提早準備測試案例、技術寫手可以及早撰寫文件、開發者可以同步開發 SDK。作者特別強調 Contract First 的最大價值在於能夠「把事情做對」，而不只是「把事情做好」。透過抽象化和 Mock 的方式，可以用最少的資源來驗證核心邏輯的正確性，大幅降低後續開發的風險。

### 2. API Design Workshop

作者以一個電玩動漫社群網站的會員註冊流程為實際案例，展示完整的 API 設計過程。這個案例包含四個步驟：用戶輸入 email 啟動註冊、系統寄送驗證信、用戶點擊驗證連結、系統要求用戶完成註冊資訊。作者指出，當業務擴展需要將部分功能外包時，就需要將核心功能 API 化，既要授權外包商必要的功能，又要保護核心資產不受威脅。作者強調在設計 API 之前必須先思考清楚：API 的目的是要開放什麼價值？是資料、運算還是流程？如果沒有想清楚，就容易設計出與前端緊耦合的 API，失去了解耦的效果。對於會員註冊系統，核心價值應該是會員資料的生命週期管理，而不只是註冊流程本身。

### 2-1. 找出狀態圖

作者展示了如何建立會員生命週期的狀態圖，定義了六個狀態：Create（建立但不保存）、Unverified（未驗證）、Verified（已驗證）、Restricted（受限制）、Banned（封鎖）和 Deleted（已刪除）。狀態圖清楚標示了各個狀態之間的轉移路徑，例如從 Create 到 Unverified 透過 Register 操作，從 Unverified 到 Verified 透過 Verify 操作。作者提供了 Mermaid 語法來描述狀態圖，便於團隊溝通和文件維護。這個狀態圖成為後續所有 API 設計的基礎，確保每個操作都符合狀態轉移的規則。作者強調狀態圖就像地圖一樣，定義了物件可以移動的路徑，如果沒有直接路徑就必須找出間接路徑，這種約束確保了系統的一致性和可預測性。

### 2-2. 標示能改變狀態的行為

作者在狀態圖上標示了所有能夠改變狀態的操作，包括 Register、Verify、Restrict/Allow、Ban/Permit 和 Remove。這些操作定義了狀態轉移的觸發條件和路徑。作者對比了基於 CRUD 和基於狀態轉移的 API 設計差異：CRUD 方式讓呼叫者可以任意設定狀態，容易造成不一致的問題；而狀態轉移方式則將狀態變更封裝在特定的操作中，確保每次變更都符合商業邏輯。作者提供了 C# 類別的程式碼範例，展示如何實作狀態轉移的封裝：每個方法都先檢查當前狀態是否允許執行操作，然後執行必要的邏輯，最後更新狀態。這種實作方式確保了狀態變更的原子性和一致性，並且每個 API 的職責都非常明確和單純。

### 2-3. 標示 "不能" 改變狀態的行為

作者說明了如何在狀態圖上標示不會改變狀態的操作，這些操作在圖上表現為從狀態指向自身的箭頭。這類操作包括 Login（登入驗證）、ResetPassword（重設密碼）、Get（取得會員資料）、Get-Masked（取得遮罩資料）和 Get-Statistics（取得統計資訊）。雖然這些操作不會改變物件的主要狀態，但仍然需要在狀態圖上標示，因為不同狀態下可能允許不同的操作。例如，被封鎖的會員可能無法執行某些查詢操作，或者未驗證的會員只能執行有限的功能。這種完整的標示方式有助於後續設計授權機制，確保每個操作都在正確的狀態下執行，同時也讓整個 API 的行為變得可預測和一致。

### 2-5. 標示相關角色

作者在狀態圖上為每個操作標示了可以執行該操作的角色，包括 Guest/User（使用者）、Staff（客服人員）、Staff Manager（客服主管）、System Service（系統服務）和 Partners（外部協力廠商）。這種角色標示為後續的授權機制設計提供了基礎，明確定義了誰可以執行什麼操作。作者說明了如何將這些角色資訊轉換為實際的身分認證和授權機制，例如使用 APIKEY、登入 token 或 JWT 等方式。在 .NET 環境中，這些身分資訊會被抽象化為 IIdentity 和 IPrincipal 介面，然後在 Controller 的方法上使用 AuthorizeAttribute 來標記所需的權限。這種設計方式確保了安全性考量從設計階段就被納入，而不是事後添加，大大提升了系統的安全性和可維護性。

### 2-6. 標示事件

作者介紹了事件（Event）的概念，說明這是讓外部系統能夠監聽並回應物件狀態變化的機制。事件機制在不同的技術平台有不同的實作方式：C# 有語言層級的 delegate 和 event 支援，Java 則在類別庫層級支援，而在 API 層級則對應到 WebHook 的 callback 機制。作者定義了三種適合發出事件的情況：狀態轉移完成後的 StateChangedEvent、操作執行中的 ExecutingEvent 和操作成功執行後的 ExecutedEvent。這些事件讓系統具備了良好的擴展性，外部系統可以訂閱感興趣的事件來執行相應的處理，例如註冊成功後自動發送歡迎信件。作者建議在設計階段先列出所有可能的事件，然後根據實際需求篩選必要的事件，避免過度設計同時確保重要的整合需求能夠被滿足。

### 2-7. 轉成 API Spec (REST)

作者將前面分析的結果轉換為具體的 REST API 規格，分為四個部分：Entity（實體定義）、Action（行為定義）、Authorize（授權定義）和 Event（事件定義）。在 Entity 部分，作者採用 JSON 結構來定義會員資料，包含系統必要資訊（ID、email、state）和可擴充的區域（fields、masked-fields、statistics-fields）。在 Action 部分，作者將操作分為四類：不需要 ID 的操作（如 Register、Login）、需要 ID 且會影響狀態的操作（如 Restrict、Ban）、需要 ID 但不影響狀態的操作（如 Get、Get-Masked）和處理多筆資料的操作。在 Authorize 部分，作者定義了 CRUD、REGISTER、BASIC、STAFF、ADMIN 和 SYSTEM 等 scope，提供細緻的權限控制。在 Event 部分，作者定義了狀態變更事件和操作執行事件的 payload 格式，支援 WebHook 的整合需求。

### 2-8, 用狀態機驗證情境

作者展示了如何使用狀態機來驗證設計的可行性，就像玩大富翁遊戲一樣在狀態圖上移動棋子來模擬情境。這種驗證方法的優點是可以在投入大量開發資源之前就確認設計的正確性，屬於早期的風險管控機制。作者提供了一個完整的使用者註冊和購物情境案例，逐步驗證每個操作是否符合狀態機的約束。例如，用戶註冊操作從 created 狀態透過 register 操作到達 unverified 狀態，接著透過 verify 操作到達 verified 狀態，最後在購物時透過 Get 和 Get-Masked 操作取得必要的會員資訊。每個步驟都對應到狀態圖上的特定路徑，確保整個流程的一致性和可行性。這種驗證方式特別適合在設計階段與各利害關係人溝通，因為它使用視覺化的方式來呈現複雜的邏輯關係。

### 2-9, 設計小結

作者總結了整個 API 設計過程，指出雖然還沒有產出最終的 API 規格文件，但所有必要的設計元素（State、Entity、Action、Authorize、Event）都已經定義完成。下一步只需要根據選擇的技術（REST、GraphQL、gRPC 等）來轉換為具體的規格文件。作者強調這篇文章整合了多場演講和分享的精華內容，為讀者提供了一個完整的 API 設計思維框架。這個設計過程的最大價值在於它提供了系統性的方法來處理複雜的 API 設計問題，確保設計出來的 API 既符合商業需求又具備良好的技術特性。作者預告下一篇文章將深入探討安全性的分析，並且將所有分析結果實作為 ASP.NET Core WebAPI，為整個設計過程提供完整的技術實現。

## 問答集 (Q&A Pairs)

### Q1: API First 的核心思想是什麼？
Q: API First 開發方法的核心理念是什麼？與傳統的 Code First 有什麼不同？
A: API First 的核心思想是將物件導向的介面設計概念應用到 REST API 設計上，先定義好 Contract（合約）再進行開發。與 Code First 不同的是，API First 讓前後端可以同時開發，提早確認設計正確性，降低開發風險。這種方法強調「把事情做對」而不只是「把事情做好」。

### Q2: 為什麼要使用狀態機來設計 API？
Q: 狀態機在 API 設計中扮演什麼角色？為什麼比 CRUD 方式更好？
A: 狀態機定義了物件的生命週期和允許的操作路徑，確保每次狀態變更都符合商業邏輯。相比 CRUD 方式讓呼叫者任意設定狀態，狀態機將狀態變更封裝在特定操作中，避免不一致的問題，讓每個 API 的職責更加明確和單純。

### Q3: 如何將物件導向的類別設計對應到 REST API？
Q: 物件導向的 class 設計如何轉換為 REST API 的規格？
A: 基本對應規則是：靜態方法對應到不需要實體 ID 的操作（如 POST /api/members/register），實體方法對應到需要指定 ID 的操作（如 POST /api/members/{id}:verify）。方法的參數對應到 request body，回傳值對應到 response。

### Q4: Contract First 的開發流程有什麼優勢？
Q: Contract First 相比傳統開發流程有哪些具體的好處？
A: Contract First 允許多個角色同時作業：架構師可以提早用 Mock 驗證設計、QA 可以提早準備測試案例、技術寫手可以及早撰寫文件、開發者可以同步開發 SDK。最重要的是能在投入大量資源前就確認設計的正確性。

### Q5: 如何在設計階段考慮 API 的安全性？
Q: API 設計時應該如何納入安全性考量？
A: 在狀態機分析時就要標示每個操作可以被哪些角色執行，定義細緻的 scope 來控制權限。例如區分 BASIC（會員本人可執行）、STAFF（客服人員可執行）、SYSTEM（系統自動執行）等不同層級的授權範圍，確保安全性從設計階段就被考慮。

### Q6: 什麼情況下應該發出事件（Event）？
Q: API 設計中何時需要定義事件機制？有哪些類型的事件？
A: 主要有三種情況：1）狀態轉移完成後的 StateChangedEvent，2）操作執行中的 ExecutingEvent，3）操作成功執行後的 ExecutedEvent。事件機制讓外部系統可以訂閱並回應物件的變化，提供良好的擴展性和解耦效果。

### Q7: 如何驗證 API 設計的可行性？
Q: 設計完成後如何確認 API 設計是否可行？
A: 使用狀態機驗證法，就像玩大富翁一樣在狀態圖上移動棋子來模擬情境。將實際的業務流程分解為步驟，檢查每個步驟是否符合狀態機的約束條件。這種方法可以在早期發現設計問題，避免後期修正的高成本。

### Q8: API 設計時如何避免過度設計？
Q: 如何在 API 設計中找到適當的抽象層級，避免過度設計？
A: 從商業邏輯的本質出發，模擬真實世界的運作方式。先列出所有可能的需求，然後找出最大公因數般的基本單位來組合。重點是掌握核心價值（如會員生命週期管理），而不是針對特定需求設計，這樣可以適應未來的需求變化。

## 解決方案 (Solutions)

### P1: 如何建立以狀態機為基礎的 API 設計
Problem: 傳統的 CRUD API 設計容易造成狀態不一致和邏輯混亂的問題
Root Cause: 缺乏對物件生命週期的系統性分析，讓呼叫者可以任意改變物件狀態，沒有商業邏輯的約束和保護
Solution: 
- 首先分析主體物件的生命週期，建立完整的狀態圖
- 定義所有可能的狀態和允許的狀態轉移路徑
- 將狀態變更封裝在特定的操作方法中
- 每個操作都要先檢查當前狀態是否允許執行
- 確保狀態變更的原子性和一致性

Example: 
```csharp
public bool Verify(string code)
{
    if (this.State != MemberStateEnum.UNVERIFIED) return false;
    // check verify code here
    this.State = MemberStateEnum.VERIFIED;
    return true;
}
```

### P2: 如何實現 Contract First 的開發流程
Problem: 傳統的先實作後設計方式導致前後端無法同步開發，且設計驗證太晚
Root Cause: 沒有在開發初期建立明確的介面合約，導致各團隊無法平行作業，風險延後到整合階段才發現
Solution:
- 先定義完整的 API 規格和資料模型
- 建立可執行的 Mock 服務來驗證設計
- 使用狀態機和情境驗證來確保設計可行性
- 讓前後端、測試、文件等團隊可以同時開始工作
- 定期檢視和調整 Contract 直到各方都認可

Example:
```
1. 先定義 API Spec 並準備 Mock
2. 前後端同時開發 (後端實作真實邏輯，前端使用 Mock)
3. 最後進行整合測試
```

### P3: 如何設計細緻的 API 授權機制
Problem: API 的權限控制過於粗糙，無法滿足複雜的商業需求和安全要求
Root Cause: 在設計階段沒有系統性地分析角色和操作的對應關係，依賴基礎設施的簡單開關控制
Solution:
- 在狀態機分析時標示每個操作可執行的角色
- 定義最小粒度的 scope 來組合各種權限需求
- 區分不同層級的授權（如 BASIC, STAFF, ADMIN, SYSTEM）
- 考慮「會員本人」等商業語境的權限控制
- 在 API 實作層面處理精細的授權邏輯

Example:
```yaml
scopes:
  - BASIC: 會員本人可執行的操作
  - STAFF: 客服人員可執行的操作  
  - ADMIN: 管理員可執行的操作
  - SYSTEM: 系統自動執行的操作
```

### P4: 如何處理 API 的事件驅動需求
Problem: API 需要與外部系統整合，但缺乏有效的通知和回調機制
Root Cause: 設計時只考慮同步的請求回應模式，沒有規劃非同步的事件通知機制
Solution:
- 定義三類事件：狀態變更事件、操作執行中事件、操作完成事件
- 設計標準化的事件 payload 格式包含事件類型和實體資訊
- 提供事件訂閱和通知機制（如 WebHook）
- 考慮事件的版本控制和向後相容性
- 選擇適當的消息中間件來處理事件傳遞

Example:
```json
{
  "event": {
    "type": "state-changed",
    "entity-id": "member/000123", 
    "origin-state": "unverified",
    "final-state": "verified",
    "action": "verify"
  },
  "entity": { /* 完整的實體資料 */ }
}
```

### P5: 如何驗證複雜 API 設計的可行性
Problem: 複雜的 API 設計完成後無法確定是否能滿足實際的業務流程需求
Root Cause: 缺乏系統性的驗證方法，依賴完整實作後才能發現設計問題，修正成本過高
Solution:
- 收集典型的業務情境和使用案例
- 使用狀態機圖進行情境模擬驗證
- 將業務流程分解為具體的操作步驟
- 檢查每個步驟是否符合狀態轉移的約束
- 在投入開發資源前就確認設計的正確性

Example:
情境：用戶註冊並完成首次購物
1. Register (created → unverified)
2. Verify (unverified → verified)  
3. Get (verified → verified, 用於購物時取得會員資訊)
4. Get-Masked (verified → verified, 提供給協力廠商)

## 版本異動紀錄

### v1.1 (2025-01-03)
- 修正摘要格式，改用第三人稱敘述，加入生成工具資訊
- 完善關鍵字分類和技術堆疊分析
- 優化問答對和解決方案的結構

### v1.0 (2025-01-03)
- 初始版本
