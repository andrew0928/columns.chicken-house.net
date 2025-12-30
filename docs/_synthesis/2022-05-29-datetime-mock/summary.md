---
layout: synthesis
title: "[架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用"
synthesis_type: summary
source_post: /2022/05/29/datetime-mock/
redirect_from:
  - /2022/05/29/datetime-mock/summary/
---

# [架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用

## 摘要提示
- DateTime.Now 難測問題: 靜態屬性不可注入，導致單元測試與PoC難以控制時間與預期結果
- 既有解法三類: 自製替代品、接口抽換、Microsoft Fakes（Shims）各有優缺，Fakes僅適合Unit Test
- 取徑—Ambient Context: 採用Ambient context approach，以單例方式在系統層級控管「現在」時間
- DateTimeUtil 設計核心: 以時間差偏移與事件檢查機制，實現可控、可流動的「現在」時間
- 時光跳躍 TimePass: 允許將系統時間「快轉」到目標點，便於驗證排程/月結等時間觸發行為
- 跨日事件 RaiseDayPassEvent: 以事件模型在跨午夜（00:00:00）時觸發，支援補發與誤差容忍
- 單元測試三場景: 驗證時間推進、搭配事件的跨日統計、真實時間流逝下的事件觸發
- 實作要點: 儲存實際時間與模擬時間之差、惰性檢查補觸發事件、禁止時間倒流（需Reset）
- 與PoC的關聯: 以「降維打擊」快速驗證概念，降低分散式、資料庫、事件系統的複雜度
- 實務應用與UI: 在原型/後台提供Now顯示與快轉按鈕，讓流程與假設可視化、可演示

## 全文重點
作者從單元測試與PoC的實務痛點出發：DateTime.Now 是靜態屬性，無法以依賴注入等「正規」手段直接替換，造成無法精準預期測試結果。市面上常見的解方包括自製SystemTime、以介面抽換、以及Microsoft Fakes（Shims）攔截呼叫。作者認為Fakes較不優雅，且受限Enterprise版與效能，適合Unit Test而不利PoC，因此採取Ambient context approach，並以單例實作DateTimeUtil，提供可控且會隨「真實時間」推進的Now，滿足PoC對「時間流動」與「可快轉」的需求。

DateTimeUtil的接口設計重點有三：其一，Now回傳基於「實際時間＋偏移量」的值，初始化後會持續隨時間流動；其二，TimePass方法可將系統時間快轉到指定時刻或持續時間，以便模擬月結、排程等情境；其三，提供RaiseDayPassEvent事件，當時間跨越每日00:00:00就觸發，用者可用事件模型驅動定期任務。為避免邏輯混亂，TimePass不允許時間倒流，若需重來，應Reset後再Init。

在實作上，DateTimeUtil以兩個內部狀態完成目標：_realtime_offset紀錄「模擬時間與實際時間的差值」；_last_check_event_time紀錄最後檢查事件的時間點。每次讀取Now或執行TimePass時，會呼叫Seek_LastEventCheckTime檢查是否跨日並補發RaiseDayPassEvent。事件的TimePassEventArgs中包含OccurTime，區分「應該觸發」的日界點與「實際觸發」時機可能的延遲。作者並以三個測試展示用法：TimePassTest驗證時間推進與誤差容忍；TimePassWithEventTest驗證跨日事件次數；RealtimeEventTest驗證真實時間流逝下，於下一次讀取Now時準確補觸發事件。另舉JWT測試案例說明如何用Init與TimePass避免固定Token過期造成的測試不穩定。

進一步，作者連結到PoC方法學：複雜系統設計需以「降維打擊」聚焦概念驗證，如以執行緒替代多主機、以本地呼叫替代RPC、以Linq/集合替代資料庫、以C#事件替代消息匯流排，快速檢驗想法的正確性與可行性。透過可控時間與事件的DateTimeUtil，原本難以演示的「時間序、事件驅動」流程可以即時演練、量化觀察，降低認知負擔與溝通成本。最後，作者建議在原型UI加入Now顯示與快轉控制，提升PoC表達力；並附上多篇延伸文章，展示以指標與降維手法驗證架構設計的實務脈絡。

## 段落重點
### 引言與問題背景
作者點出在單元測試/PoC中控制DateTime.Now的困難：Now是static property，無法注入或包裝替換。雖然Google可查到多種Mock方法，但多半僅把Now固定為某時刻，對PoC來說不足，因PoC需時間「流動」、能「快轉」、並能驅動與時間相關的事件（如排程）。故作者打算自製工具來同時滿足測試與PoC的需求。

### 前言: DateTime.Now 的問題
整理可行方案三類：自製替代品（如SystemTime.Now）、以介面抽換（IDateTimeProvider）、Microsoft Fakes（ShimsContext攔截呼叫）。作者不偏好Fakes，因為需要VS Enterprise、影響效能、僅適合Unit Test。引用MethodPoet的「四種策略」：包裝介面、SystemTime、Ambient context、把DateTime當類別屬性，並表明選用Ambient context approach，但以自家情境改寫。目標除可控制回傳時間，還要讓時間隨實際流逝同步增加，並可與計時器等時間事件連動。

### 設計: DateTimeUtil 介面定義
DateTimeUtil以單例暴露：Instance、Init(expectedTimeNow)、Reset()，提供Now、TimePass(TimeSpan/DateTime)、GoNextDays/GoNextHours等便利方法，另定義RaiseDayPassEvent事件，於跨日觸發。與一般「凍結時間」的測試不同，作者要的是「有偏移的流動時間」。此外需支援「時光機」能力（TimePass）以快速跳到月中、月底等關鍵點；並透過事件機制於快轉過程補觸發應有的定期任務。時間不允許倒流，若需回頭必須Reset後再Init，讓語義明確。作者以JWT過期案例示範如何用Init與TimePass穩定長期測試。

### 實作: Code Review
核心期望：1) Now需隨真實時間推移；2) 無論真實流逝或TimePass快轉，跨日都要觸發事件。內部狀態：_realtime_offset保存「模擬時間=實際時間+偏移」；_last_check_event_time保存最後檢查點。每次Now或TimePass後，呼叫Seek_LastEventCheckTime，若跨日則逐日補發RaiseDayPassEvent，事件提供OccurTime標示應觸發日。作者選擇不開背景執行緒監測，而是在惰性讀取Now或TimePass時檢查，接受些許延遲。也提到可把大跨度TimePass拆日補發以減少誤差，屬未來可加強點。

### 使用情境 - TimePassTest
示範Reset後Init為指定起點，使用GoNextHours、TimePass、以及Thread.Sleep來觀察Now是否如預期前進。由於真實時間引入毫秒級不確定性，採用1秒誤差容忍判斷。此例驗證了偏移模型能同時支援手動快轉與真實時間流動。

### 使用情境 - TimePassWithEventTest
註冊RaiseDayPassEvent累計觸發次數，將時間快轉35天15小時，預期跨越36日界點，最後以Assert檢驗事件觸發次數。此例證明TimePass會在跨日過程中逐日補發事件，適合用來驅動定期任務（例如月結）。

### 使用情境 - RealtimeEventTest
測試不靠TimePass、僅依賴真實時間前進下，事件會在下一次讀取Now時補觸發：先睡眠跨過午夜，確認事件尚未觸發；讀取Now後出現補觸發；再透過GoNextDays與TimePass逼近跨日前2秒，觀察事件計數遞增；最後再次睡眠並讀取Now，驗證惰性觸發機制的正確性。此例強化了「讀取點補檢查」的設計語義。

### 延伸思考: PoC 的應用
闡述PoC的價值與方法論，核心是以「降維打擊」聚焦概念驗證，避免在早期就背負基礎設施與跨領域實作成本。例：用執行緒代替多主機、用本地呼叫代替RPC、用集合/Linq代替資料庫、用C#事件代替消息匯流排。前提是清楚知道PoC與真實系統的對應關係與限制。DateTimeUtil讓時間序與事件驅動更易觀察，幫助呈現與驗證流程。作者亦建議在原型UI直接顯示模擬Now與提供快轉按鈕，提升演示與溝通效率，並附多篇延伸文章展示以指標化、降維化推進架構設計的實務。

### 小結
本文以DateTime.Now的可測問題為切入，提出Ambient context式的DateTimeUtil：以偏移量維持流動時間、提供TimePass時光跳躍、用RaiseDayPassEvent在跨日補發事件。此工具不僅穩定單元測試，更在PoC中藉可控時間與事件，強化對時間序與事件驅動流程的驗證與展示。作者在實務上甚至將其UI化，讓概念可視化、可演示，降低抽象思考與團隊溝通成本。工具源碼簡潔，易於複製與擴充，適合在原型與內部專案中即取即用。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- C# 基礎語法與物件導向（static、class、event、delegate）
- DateTime 與 TimeSpan 基本操作
- 單元測試框架基本用法（MSTest/NUnit/xUnit）
- 事件驅動程式設計觀念
- 依賴反轉與抽換（DI/介面封裝）的基本概念

2. 核心概念：本文的 3-5 個核心概念及其關係
- DateTime.Now 的測試困難：因為是 static property，時間不可預測、不可 DI
- Mock 的四種策略：介面封裝、SystemTime 類、Ambient Context、在類別上提供 DateTime 屬性
- Ambient Context 實作：以全域/單例的 DateTimeUtil 封裝可控的「系統時間」
- 可前進的模擬時間：不僅可固定起點，還會隨真實時間推進，並支援手動快轉 TimePass
- 事件觸發與時間旅行：跨日 RaiseDayPassEvent 讓排程/定期任務在 PoC 中被精準重播
這些概念串起來，構成從「時間控制」到「可重播流程」再到「PoC 驗證」的工具鏈。

3. 技術依賴：相關技術之間的依賴關係
- C# 語言與 .NET 時間型別（DateTime、TimeSpan）是基礎
- 單元測試框架用於驗證 DateTimeUtil 的行為
- Microsoft Fakes（可選）屬於 runtime 攔截技術，依賴 VS Enterprise，較適合純 UT 場景
- 事件機制（EventHandler<T>）用於在時間快轉或讀取 Now 時觸發跨日事件
- 設計模式依賴：Singleton（簡化 Ambient Context）、Facade/Wrapper（對應 DateTimeUtil）

4. 應用場景：適用於哪些實際場景？
- 單元測試中需要可預期的時間行為（含跨日、期限檢核）
- PoC/原型開發中需要「時間旅行」來重播流程（如月結、對帳、報表、排程）
- Demo/教學中以 UI 控制系統「認知時間」，快速演示定時任務
- 與時間密切相關的業務規則驗證（Token 有效期、排程觸發、月底/跨年邏輯）
- 不便改動大量既有程式碼、又不想依賴 Fakes 的環境

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 了解 DateTime、TimeSpan 基本操作與 static 成員的特性
- 寫一個最小單元測試，觀察 DateTime.Now 不可預測帶來的測試不穩定
- 嘗試以簡單的包裝類（如 SystemTime.Now）回傳固定時間，體會可控性
- 練習事件訂閱與觸發（EventHandler、事件參數）

2. 進階者路徑：已有基礎如何深化？
- 比較四種策略（介面封裝、SystemTime、Ambient Context、類別屬性）與 Microsoft Fakes 的優缺點
- 實作文中 DateTimeUtil：支持 Init、Reset、Now、TimePass、RaiseDayPassEvent
- 加入跨日事件與誤差容忍（tolerance）測試設計
- 思考與 Timer/排程整合、以及多執行緒讀寫時的正確性（必要時加入同步化）

3. 實戰路徑：如何應用到實際專案？
- 在入口點（Main/測試初始化）設定 DateTimeUtil.Init，並規範使用 DateTimeUtil.Instance.Now
- 對於需重播的定期任務，改為訂閱 RaiseDayPassEvent，使用 TimePass 模擬跨日/跨月
- 建置 PoC 控制台或簡易 UI：顯示「系統認知時間」與按鈕（快進小時/天）
- 把與時間有關的驗證（如 JWT 期限）改以可控時間驅動，確保測試可長期穩定

### 關鍵要點清單
- DateTime.Now 的測試問題: 因為是 static 且不可 DI，導致不可預測與難以 Mock（優先級: 高）
- 四種常見策略: 介面封裝、SystemTime、Ambient Context、類別屬性，各有擴充性與改動成本（優先級: 高）
- Microsoft Fakes 葉克膜比喻: 最少改動但需 VS Enterprise 且有效能/限制，較適合純 UT（優先級: 中）
- Ambient Context 概念: 在當前上下文提供可替代的「現在時間」，不侵入大量程式碼（優先級: 高）
- DateTimeUtil 單例設計: 以 Singleton 模式提供 Instance.Now、Init、Reset（優先級: 高）
- 可前進的模擬時間: 以 realtime_offset 記錄偏移，Now 隨真實時間推移而變（優先級: 高）
- TimePass 快轉機制: 支援 TimeSpan/語法糖方法（GoNextDays/GoNextHours），便於「時間旅行」（優先級: 高）
- 跨日事件 RaiseDayPassEvent: 在跨越 00:00:00 觸發，用以模擬排程/定期任務（優先級: 高）
- 事件觸發時機限制: 僅在讀取 Now 或呼叫 TimePass 時檢測，允許非即時的微小延遲（優先級: 中）
- 誤差容忍設計: 測試中以 1 秒容忍度避免機器/單步偵錯造成的毫秒級不穩定（優先級: 中）
- 不允許時間倒流: 只能 Reset 再 Init，避免資料一致性與流程重入混亂（優先級: 中）
- 與排程/Timer 對應: 以事件驅動替代真實 Timer，降低 PoC 複雜度（優先級: 中）
- 與 JWT/有效期測試: 用可控時間跨越有效期，避免硬編碼到期日造成測試失效（優先級: 高）
- PoC 的降維打擊: 把跨程序/跨機維度降到語言層（event、介面、集合/Linq）快速驗證概念（優先級: 高）
- 實務導入建議: 在專案入口統一初始化、規範取時 API、提供 Demo UI 以快速溝通流程（優先級: 中）