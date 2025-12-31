---
layout: synthesis
title: "Policy Injection Application Block 小發現..."
synthesis_type: summary
source_post: /2008/11/18/policy-injection-application-block-small-discovery/
redirect_from:
  - /2008/11/18/policy-injection-application-block-small-discovery/summary/
postid: 2008-11-18-policy-injection-application-block-small-discovery
---

# Policy Injection Application Block 小發現...

## 摘要提示
- Enterprise Library 研究動機: 因工作需求研究 Enterprise Library 與 Patterns & Practices 的 Application Block，特別注意到 Policy Injection。
- Policy Injection 重點: 以宣告式方式在方法呼叫前後插入橫切關注點，如授權、快取、記錄等。
- CAS 對比: .NET 的 Role-based Security 以 Attribute 宣告檢查角色，漂亮但難以自訂擴充。
- 自訂行為困境: 直接掛自訂 Attribute 不會被 CLR 觸發，難以插入自訂邏輯。
- AOP 與 Remoting 線索: 早期從 AOP 與 .NET Remoting 的 IMessage/IMessageSink/Proxy 機制看見可行解。
- 本地代理關鍵: Policy Injection 其實是本地使用 .NET Remoting 的 RealProxy 機制包裝，透過 Create/Wrap 建立「加料」物件。
- 使用體驗: 建立方式由 new 改為 Create，其餘呼叫幾乎不變，包裝自然。
- 內建 Handlers: 提供 Authorization、Caching、Exception Handling、Logging、Performance Counter、Validation 與自訂管線。
- 實用價值: 快取可直接回傳先前結果、Logging/Performance 即插即用，大幅降低重複樣板碼。
- 個人心得: 解開多年疑惑，後續將持續研究深入細節，官方文件與 QuickStart 足以上手。

## 全文重點
作者因工作研究 Microsoft Enterprise Library，特別關注其中的 Policy Injection Application Block。回顧當年對 .NET Role-based Security（CAS）驚豔：只需以 Attribute 標註方法，執行時自動檢查呼叫者角色，達成優雅的宣告式安全控管；但當想自訂擴充（如加上自製授權、記錄或驗證），卻發現這行為由 CLR 直接支援，自訂 Attribute 並不會被觸發，從而受限。作者曾探索 AOP 與 .NET Remoting，理解到在遠端呼叫中，透過 Proxy 及 IMessage/IMessageSink 可攔截並注入邏輯，但因實務上未使用 Remoting 而擱置。

近期研究 Policy Injection 時，看到以 AuthorizationCallHandler 等 Attribute 在方法呼叫前做授權檢查的範例，且與單純角色檢查不同，這是更細緻的「授權」語義（類似 ACL 可拒絕 Administrators 的精細控制）。進一步挖掘後豁然開朗：Policy Injection 的本質，是在本地利用 .NET Remoting 的 RealProxy 機制，將標註了 Attribute 的目標物件包裝成「加料」代理；只要透過其提供的 Create/Wrap 工廠建立物件，後續呼叫都會經過攔截點，以管線方式注入各式 CallHandler。除了建立方式由 new 改為 Create，其他使用幾乎一致，包裝相當優雅。

內建 Handler 相當實用：Authorization 可做細緻授權；Caching 可在有快取結果時直接回傳，省卻重複查快取與落盤的樣板碼；Logging 能在呼叫時自動記錄；Performance Counter 可即時累積統計，方便以 perfmon 觀測；Exception Handling、Validation 亦可統一掛載。整體上，Policy Injection 以宣告式與攔截式方式，將安全、記錄、快取、驗證等橫切關注點從業務邏輯中抽離，且不需變更既有呼叫端程式碼結構，大幅提升可維護性。文章最後作者表示此篇以記錄解惑為主，深入教學可參考官方文件與 QuickStart，後續將再分享研究心得。

## 段落重點
### 研究 Enterprise Library 與 Policy Injection 的動機
作者因工作需求研究 Enterprise Library 及 Patterns & Practices 的 Application Block，注意到 Policy Injection，並指出介紹文獻眾多，本文聚焦於其使用方式與帶來的「宣告式攔截」價值，而非完整教學。

### CAS範例程式與宣告式安全的優雅
回顧 .NET 的 Role-based Security：在方法上加 PrincipalPermissionAttribute，執行時自動檢查呼叫者角色，違反則拋 SecurityException。這種宣告式方式能避免在業務邏輯中充斥權限檢查碼。然而作者也發現自訂 Attribute 不會被 CLR 觸發，無法擴充行為（如客製 Log 或額外檢查），成為技術痛點。

### AOP 與 .NET Remoting 的早期探索
作者曾研究 AOP，理解其能解決橫切關注點，但當時可用解法實務性不足。後來發現 .NET Remoting 架構中，Client/Server 間以 IMessage 封裝呼叫，經 Proxy 還原並透過 Reflection 執行，若在 IMessageSink 插點上攔截即可注入邏輯。然而因實務上不使用 Remoting，當時未採納此路線。

### Policy Injection Sample 與「授權 vs 角色」的差異
透過 AuthorizationCallHandler 標註的方法，呼叫前會做授權檢查。作者強調其語義較角色檢查更進階：角色像「預設特權」，授權則類 ACL 的明確允許/拒絕規則，可精細控制是否能執行特定操作。此示例與 CAS 相似但更彈性，且為可自訂的 Attribute 與攔截行為。

### 揭露：本地使用 .NET Remoting RealProxy 的代理機制
關鍵發現是 Policy Injection 的核心在於「本地代理」：以 Create 或 Wrap 方式生成被加料的代理物件，底層是繼承自 System.Runtime.Remoting.Proxies.RealProxy 的類別。對代理進行呼叫時，會經過攔截管線，將宣告的處理邏輯注入，再轉至真實物件。除了建立方式改變，其他使用體驗幾乎相同，整體封裝自然不突兀。

### 內建 CallHandler 功能總覽與實用性
列舉並簡述內建 Handlers：Authorization（授權）、Caching（結果快取加速）、Exception Handling（統一例外策略）、Logging（呼叫記錄）、Performance Counter（即時統計曝光於 perfmon）、Validation（參數/狀態驗證）、Custom Pipeline（自訂攔截鏈）。這些處理能在不污染業務碼的前提下，即插即用，尤其 Caching 能直接回傳先前結果，省去繁瑣的快取判斷與寫入邏輯。

### 結語與後續計畫
作者表示本文重點在於記錄解開多年來關於「如何以宣告方式自訂插入行為」的疑惑：答案是本地 RealProxy 代理與攔截管線。深入實作可參考官方文件與 QuickStart 範例，未來將在進一步研究後分享更完整的教學與實務心得。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- .NET 基礎（C#, 屬性 Attributes, 反射 Reflection）
- 物件導向與介面設計（介面導向、抽象化）
- AOP 基本概念（橫切關注點、攔截 interception）
- .NET Remoting/RealProxy 基本概念（代理、訊息攔截）
- Enterprise Library 概觀（特別是 Policy Injection、Security、Logging、Caching、Exception Handling、Validation 等 Blocks）

2. 核心概念：本文的 3-5 個核心概念及其關係
- 屬性驅動的攔截：以 Attribute 標注方法，於呼叫前後插入行為（類似 AOP）
- Policy Injection Application Block（PIAB）：以 Create/Wrap 產生代理物件，串起攔截管線（Call Handlers）
- Call Handlers 管線：授權、快取、例外處理、記錄、效能計數、驗證等可組合的攔截元件
- RealProxy/.NET Remoting 技術基礎：本機透過代理呼叫目標物件，於代理中注入自定邏輯
- 與 CAS/Role-based 的對比：從單純角色判斷，提升到可自定授權與多種橫切關注點

3. 技術依賴：相關技術之間的依賴關係
- PIAB 依賴 RealProxy/.NET Remoting 進行方法攔截
- Call Handlers 以屬性與設定組態驅動，與 Enterprise Library 其他 Blocks（Security、Logging、Caching、Exception Handling、Validation、Performance）整合
- 應用程式以 PIAB 的 Create 或 Wrap 建立代理物件，呼叫時由攔截管線處理再委派至目標物件

4. 應用場景：適用於哪些實際場景？
- 權限與授權檢查（比單純角色更細的授權規則）
- 橫切關注點注入：記錄（Logging）、例外處理標準化、輸入驗證
- 效能監控：自動寫入 Windows Performance Counter
- 快取：對昂貴/重複查詢的方法進行結果快取
- 以宣告式方式維護非功能性需求，降低散落在業務邏輯中的樣板碼

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 Attributes 與 Reflection 在 .NET 的基本用法
- 讀 Enterprise Library 概觀，認識 Policy Injection 的定位
- 跑官方 QuickStart 範例：以 AuthorizationCallHandler、LoggingCallHandler 觀察攔截效果
- 練習使用 PolicyInjection.Create<T>() 建立代理並呼叫方法

2. 進階者路徑：已有基礎如何深化？
- 熟悉各類內建 Call Handlers（Authorization、Caching、Exception Handling、Logging、Performance、Validation）的配置與組合
- 研究攔截管線順序、處理鏈組態與生命週期
- 實作自訂 Call Handler，處理專案特有的橫切關注（例如審計、租戶隔離、遮罩 PII）
- 探索與 Security Application Block 的授權模型整合與差異

3. 實戰路徑：如何應用到實際專案？
- 對現有服務層/應用服務以 Wrap 策略逐步導入（先 Logging/Exception，再 Authorization/Validation，再 Caching/Performance）
- 以設定檔驅動開關與順序，建立可觀測性（log 格式、perf counters 命名）
- 撰寫端到端測試：驗證攔截器執行順序、快取命中、授權拒絕與例外處理一致性
- 制定治理規範：哪些方法允許攔截、效能與快取失效策略、與 DI 容器/組態管理整合

### 關鍵要點清單
- 宣告式安全 vs 授權差異: CAS/Role 只判角色，PIAB/Authorization 可檢查更細的授權規則 (優先級: 高)
- PolicyInjection 代理建立: 以 Create 或 Wrap 取得「加料」過的代理物件，呼叫才會被攔截 (優先級: 高)
- RealProxy 技術基礎: PIAB 在本機利用 .NET Remoting/RealProxy 攔截方法呼叫 (優先級: 高)
- Call Handler 管線: 多個攔截器可組合、排序，於呼叫前後插入邏輯 (優先級: 高)
- AuthorizationCallHandler: 以授權規則控制方法可執行性，強於單純角色檢查 (優先級: 高)
- Logging Handler: 自動記錄方法呼叫資訊與結果，減少樣板碼 (優先級: 中)
- Exception Handling Handler: 標準化例外處理/轉換，提高一致性與可維運性 (優先級: 中)
- Caching Handler: 針對昂貴方法快取結果，命中時直接回傳提升效能 (優先級: 高)
- Performance Counter Handler: 自動更新 Windows 效能計數器，便於監控 (優先級: 中)
- Validation Handler: 在方法入口進行參數/物件驗證，避免無效輸入流入核心邏輯 (優先級: 中)
- 自訂 Handler 擴充: 依專案需求實作自訂攔截器（審計、遮罩、租戶等） (優先級: 中)
- 組態驅動與可觀測性: 以設定檔控制開關與順序，強化部署靈活與診斷 (優先級: 中)
- 導入策略: 從低風險的 Logging/Exception 開始，逐步擴大至 Auth/Validation/Caching (優先級: 高)
- 與業務邏輯解耦: 橫切關注外移到攔截層，保持核心程式碼乾淨 (優先級: 高)
- 與傳統 AOP 的關係: PIAB 提供務實的 .NET 原生攔截路徑，避免複雜工具鏈 (優先級: 中)