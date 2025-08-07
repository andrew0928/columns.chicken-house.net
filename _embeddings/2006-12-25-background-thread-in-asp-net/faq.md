# Background Thread in ASP.NET

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 ASP.NET Web 應用程式中，能不能不另外寫 Windows Service，而直接執行背景工作？
可以。你可以在 Global.asax 的 `Application_Start` 事件中手動建立一條背景 Worker Thread，讓它在無窮迴圈中執行排程或長時間工作的程式碼，直到 `Application_End` 時才結束。這種作法可讓背景工作與網站程式碼、設定檔 (web.config) 共享，同時保留 XCopy Deploy 的優勢。

## Q: 哪些功能類型不適合用傳統「一請求一回應」的網頁模式實作？
1. 需要輸出大量資料的功能，例如產生大型報表或一次列出大量清單而不想分頁。  
2. 執行時間很長的批次工作，例如資料轉檔，可能一跑就是半小時。  
3. 需要定期且持續在背景執行的排程程式。

## Q: 如果將背景工作拆成獨立的 Windows Service、Message Queue 或 Console/排程程式，會遇到哪些缺點？
1. 設定檔 (configuration) 無法共用，必須同時維護 web.config 與 app.exe.config。  
2. 需要另外設計與維護 Library；Web 專案中放在 `App_Code` 的程式碼無法直接重用。  
3. 部署不再是單純的 XCopy；還得安裝 MSMQ、註冊 Windows Service 或設定排程，增加安裝與維護成本。

## Q: 在 ASP.NET 中使用背景 Worker Thread 會有哪些限制或風險？
1. 應用程式必須先被「有人連線」喚醒，背景執行緒才會啟動；如果 IIS 啟動後一直沒有任何請求，背景工作不會執行。  
2. 一旦 IIS 決定回收或卸載應用程式，背景執行緒會被迫終止，生命週期難以像 Windows Service 那樣精確控制。  
3. ASP.NET 會嚴格管控 Thread 數量；佔用一條 Thread 來跑背景工作，等於減少一條用來處理 HTTP Request 的資源，可能影響效能，除非調高 Thread 上限。  
4. 背景執行緒不隸屬於任何 HTTP Request，因此取不到 `Request`、`Response`、`Session` 等 ASP.NET 特有物件，但仍能正常使用 `ConfigurationManager` 讀取設定。

## Q: 背景執行緒對 ASP.NET 的效能有何影響？需要特別設定嗎？
預設情況下，ASP.NET 大約只會配置 20–25 條工作執行緒處理 HTTP Request。若你固定佔用一條 Thread 來跑背景任務，就等於少了一條可服務的 Thread。可視需要調整 Thread Pool 上限，或確保背景工作足夠輕量，避免拖慢整體網站效能。

## Q: 背景 Thread 是否能直接使用 ASP.NET 的 `HttpContext`、`Request`、`Response` 或 `Session`？
不能。因為它並不運行在特定的 HTTP Request 範圍內，因此取不到大多數 ASP.NET 專屬物件。若需要與使用者狀態互動，必須改以其他管道（例如資料庫、快取或訊息佇列）來溝通。