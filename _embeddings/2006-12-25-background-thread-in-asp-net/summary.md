# Background Thread in ASP.NET

## 摘要提示
- 大量資料輸出: 報表或一次列出海量清單時，不適合用同步回應的網頁模式。
- 長時間任務: 轉檔等動輒半小時以上的流程需脫離使用者請求另外處理。
- 週期性背景作業: 需定期、無人值守執行的排程功能在 Web App 中也很常見。
- 傳統解法複雜: MSMQ、Windows Service 或排程程式會帶來安裝及維護痛點。
- XCopy 部署優勢: 希望所有功能都放在 ASP.NET 內即可一次部署。
- 背景執行緒技巧: 於 Application_Start 建立無窮迴圈的 worker thread 來扮演服務。
- 共用組態與程式庫: 直接使用 Web.Config 與 App_Code 共享程式，降低重工。
- 啟動與生命週期限制: 必須有人連線才啟動，IIS 回收時亦會被迫中止。
- 效能與環境侷限: 佔用一條 Thread、取不到 Request/Session 等 ASP.NET 物件。
- 範例程式: 提供示範碼，每 10 秒將時間寫入 Log 以展示概念。

## 全文重點
當 Web 應用愈趨完整，必然遇到三種不易用傳統同步網頁解決的需求：大量資料輸出、長時間運算，以及需定期執行的背景排程。一般做法多半是額外撰寫 Windows Service、Console 程式或整合 MSMQ、Reporting Service 等外部元件，但這些作法帶來組態檔分離、程式庫重複與部署安裝繁瑣等成本，違背 ASP.NET 強調的 XCopy 部署精神。

作者因而研究 Community Server 的做法：在 Global.asax 的 Application_Start 中建立一條長壽命背景執行緒，進入無窮迴圈週期性執行工作，模擬 Windows Service 行為。此設計能直接共用 Web.Config 與 App_Code 的程式碼，也省去安裝 Windows Service 或排程的麻煩，對簡易 Scheduler 十分便利。

然而評估後仍有侷限：首先，Web 應用必須在首次被存取後 Thread 才會啟動，且 IIS 若因 Idle Time 或記憶體回收而卸載應用程式，背景工作也會跟著終止，生命週期無法像 Windows Service 那樣受控；其次，ASP.NET 預設嚴格控管 Thread Pool，一條 Thread 被占用意味著少一條可處理 HTTP Request，除非調高上限，否則對效能有影響；最後，Worker Thread 不在特定 HTTP 要求上下文中運行，因此無法使用 Request、Response、Session 等物件，但組態系統仍可正常存取。

總結來說，此技巧對單純、需求不高的排程任務是低成本方案，但若對執行可靠度及精確控制有要求，仍建議使用獨立 Windows Service。文末附上示範程式碼，展示 Web 應用啟動後每十秒將現在時間寫入日誌的方法，供讀者實作與參考。

## 段落重點
### 引言：Web App 與非同步需求
隨著 Web Application 功能增多，單純以「使用者點擊 → 伺服器生成頁面」的即時回應流程已不足以支援大量報表、長時間執行或定期排程等需求，因此需尋求替代方案。

### 三大常見需求類型
1. 大量資料輸出：一次性生成大型報表或無分頁清單。  
2. 長時間任務：如批次轉檔、資料匯整，可能執行數十分鐘。  
3. 週期性背景作業：定時執行、無人監看，但必須長期運作。

### 傳統解決方案與痛點
常用 MSMQ、Reporting Service、Windows Service、Console + 排程等方式，使程式分散、組態檔無法共用、需額外安裝與註冊服務或排程，違背 ASP.NET 強調的 XCopy 部署與易維護特性。

### 在 ASP.NET 中建立背景執行緒
仿造 Community Server 作法，在 Application_Start 建一條 Worker Thread，進入無窮迴圈定時執行工作，使其行為類似 Windows Service，而又能共用 Web.Config 與 App_Code 的程式碼。

### 評估結果：優點與侷限
優點：單一部署、共用設定、快速上手。  
侷限：首次有人連線才啟動；IIS 回收即被中斷；占用 Thread Pool 對效能有衝擊；無法取得 Request/Session 等 ASP.NET 專屬物件，僅適合簡單排程任務。

### 範例程式與結語
作者提供範例程式，展示 Web 應用啟動後每十秒寫一次時間到日誌檔的基本排程邏輯。此方案雖非完美，但對輕量化需求可快速解決；如需更高可靠度仍建議使用獨立服務。