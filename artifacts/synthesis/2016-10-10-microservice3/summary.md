# API & SDK Design #1, 資料分頁的處理方式

## 摘要提示
- 微服務與DX: API面向開發者，應重視DX（文件、API、SDK、效能與穩定），不同於一般App的UX訴求
- 資料分頁痛點: 分頁在UI與API層都繁瑣，client端重組常導致義大利麵式程式碼
- 範例來源: 以政府開放資料（特生中心繁殖鳥大調查1000筆JSON）為資料來源示範
- 服務端分頁API: 以ASP.NET Web API實作$start/$take查詢，並以自訂Header回傳總筆數與分頁資訊
- 兩種查詢方式: 提供列表分頁查詢與依ID單筆查詢，回應格式統一為JSON
- 直呼HttpClient缺點: client端自行迭代分頁與過濾，流程與邏輯交織，程式可讀性與維護性差
- yield return優勢: 以迭代器分離「資料取得」與「資料處理」，維持串流式逐頁載入與處理
- 交錯執行驗證: 觀察log證實每頁資料取得後立即處理，非先全取後處理
- 早停機制: 透過Linq.Take(1)或在foreach中break，可在找到目標後立刻停止後續API呼叫
- IEnumerable vs IQueryable: IEnumerable偏向單向遍歷（類table scan），IQueryable可將查詢條件下推至Server，若可用OData建議採用

## 全文重點
本文延續微服務架構設計的討論，聚焦於API/SDK/APP之間的互動，並以「資料分頁」為案例，探討如何在不引入OData的前提下，兼顧效能與開發者體驗（DX）。作者以政府開放資料的鳥類觀察紀錄（1000筆JSON）為範例，建立一個ASP.NET Web API服務，支援以$start與$take進行分頁查詢，每次最多回傳10筆，並以回應Header提供X-DATAINFO-TOTAL/START/TAKE等輔助資訊，同時也提供依ID取單筆的端點。

在客戶端，作者先示範以HttpClient直接呼叫API並自行實作分頁迴圈與過濾邏輯的作法。此作法需手動維護起始索引、頁大小、迴圈終止條件、資料反序列化與過濾，導致不同目的的程式碼混雜，產生難維護的「義大利麵」風格。接著作者引入C#的yield return，將「資料取得」實作為一個可逐步產生資料的IEnumerable迭代器（GetBirdsData），前端主流程則只專注於以Linq表達過濾條件並逐筆處理。此設計不僅讓程式碼更精煉、關注點分離，也保留串流式的逐頁載入行為：每次呼叫API取回一頁，立即yield逐筆給前端處理，再依需求繼續向後取頁。

作者以log驗證執行時序，證明資料取得與處理是交錯進行的，非先全取後處理。同時也驗證了「早停」能力：無論以Linq的Take(1)限制筆數，或在foreach迴圈中break，一旦達成目標即不再進行後續的API呼叫，達到效能與成本最佳化。最後，作者說明本例以IEnumerable達成串流遍歷；若在可行環境中採用OData與IQueryable，則能將查詢條件下推到Server端進行最佳化（例如索引利用、減少傳輸），效能更佳。因此，當環境允許時建議採用OData；但在非OData情境，善用yield return依然能優雅解決分頁與資料處理的痛點，提供良好的DX。

## 段落重點
### 前言與目標
作者從微服務重構談起，指出API服務的主要使用者是開發者，應重視DX而非UX。本文以「資料分頁」為案例，展示API、SDK與APP在設計上的細節，特別是如何避免client端為了重組分頁資料而產生混亂程式碼。核心解法是以C#的yield return實作迭代器，優雅地將server端分頁與client端處理分離，提升可讀性、可維護性與效能。

### 範例 Data API Service: Server Side Data Paging
範例資料來自政府開放資料平台之鳥類生態觀察紀錄（JSON，約1000筆），作為「無資料庫、無EF」的輕量示例。作者批判業界常忽略API實作細節，導致維運困難，並提醒API需優化DX：清楚的文件、合理的API介面、輔助性的SDK與可靠穩定的表現。本文將以實作與程式碼說明如何設計出符合DX期待的資料分頁API。

### DATA FORMAT 說明
資料以JSON陣列存放於App_Data/birds.json，每筆含流水號、日期、地點、經緯度、科名、學名、中研院學名代碼、中文名、數量、鳥名代碼與調查站碼等欄位。本文以其中兩筆作為格式範例，實際共有1000筆，方便在無資料庫情境下快速演示API與client端邏輯。

### API CODE (SERVER) 說明
以ASP.NET Web API建立BirdsController，在Initialize中讀入JSON資料。提供Head()用以回傳總筆數於Header（X-DATAINFO-TOTAL），Get()則支援$start與$take參數，限制每次最多10筆，並在回應Header附帶總筆數、起始與筆數限制。若超過MaxTake自動截斷。另提供Get(id)以ID查詢單筆。此設計兼顧簡潔與可觀測性（藉Header提供上下文資訊），適合前端與SDK取得分頁狀態。

### API 呼叫方式說明
兩個端點：1) ~/api/birds?$start={start}&$take={take}，回傳JSON列表並於Header回報X-DATAINFO-TOTAL/START/TAKE；也支援HEAD方法取得總筆數而不取資料。2) ~/api/birds/{birdid} 回傳指定ID資料。作者指出正式情境可改用OData與EF自動支援分頁與查詢，但為教學目的採自製簡化版，強調理解底層行為與設計考量。

### APP CODE 說明 (直接使用 HttpClient)
示範Console App以HttpClient逐頁抓取、手動控制$start/$take、反序列化、再在client端過濾「地點=玉山排雲山莊」。由於無server-side query，需從頭掃描所有資料。此寫法雖可運作，但分頁控制、終止條件、過濾與輸出混在同一迴圈內，產生維護困難的混雜程式碼。以本機測試1000筆，約需3000毫秒，揭示流程雜湊與效能上的考量。

### APP CODE 說明 (使用 C# yield return)
以yield return實作GetBirdsData()，內部負責：依$start/$take逐頁呼叫API、反序列化，並逐筆yield回傳。主程式僅以Linq表達過濾條件並foreach處理，達到關注點分離。雖改寫後行數差異不大，卻大幅改善結構與可讀性；更重要的是，保留「一次一頁、逐步處理」的串流語意，不會先載回全部資料。

### 結果觀察 - 觀察 API 呼叫與資料處理的交錯執行狀況
以Console輸出觀察，證實每取回一頁資料即分別yield逐筆給前端處理，API呼叫與資料處理交錯進行，並非先全量下載後才處理。範例log顯示「loading data... (95~100)」後立即出現符合條件的資料列印，再繼續「loading data... (100~105)」，符合設計目標：節省記憶體、降低延遲、提升使用者體驗與效能。

### 結果觀察 - 中斷迴圈，資料載入狀況觀察
兩種早停測試：1) 以Linq的Take(1)只取第一筆符合資料；2) 在foreach內break。一旦找到目標即停止後續API呼叫，log顯示只載入到必要頁數（例如載到「(45~50)」即停），整體執行時間亦顯著縮短。此證明迭代器與延遲評估的結合，自然帶來高效率的短路行為。

### yield return 應用小結
本例展現yield return在分頁資料巡覽上的典型應用：以IEnumerable建立串流迭代，分離「資料取得」與「資料處理」，強化DX與可維護性。然而IEnumerable本質是單向迭代，較像table scan；若採用IQueryable與OData，則能將Linq查詢條件轉譯並下推至Server端進行最佳化（如走索引、減少傳輸），效能更佳。因此，能用OData時建議使用；在非OData環境，結合yield return與良好SDK設計，依然能達到優雅、有效率且開發者友善的解決方案。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 C# 語法與集合操作（foreach、IEnumerable）
   - HTTP/REST 基礎（GET、HEAD、QueryString、HTTP Header）
   - JSON 序列化/反序列化（如 Json.NET）
   - ASP.NET Web API 基礎與控制器設計
2. 核心概念：
   - 資料分頁機制：服務端限制每次傳回筆數，並透過查詢參數與回應標頭攜帶分頁資訊
   - DX（Developer Experience）：以開發者為中心設計 API/SDK，降低用戶端處理分頁的複雜度
   - yield return 與迭代器模式：以延遲評估的序列抽象跨頁取得資料，解耦「取資料」與「用資料」
   - IEnumerable vs IQueryable：前者單向巡覽（常見於客製 API），後者可表達查詢、利於 OData 服務端過濾
   - OData 對照：若能用標準，讓查詢在服務端執行可大幅提升效率
3. 技術依賴：
   - 伺服端：ASP.NET Web API → 控制器 → 讀取資料來源（此例 JSON 檔）→ 分頁策略與回應標頭
   - 用戶端：HttpClient → 反序列化（Json.NET）→ IEnumerable + yield return → LINQ 過濾/投影
   - 進階替代：OData（IQueryable）→ 將 LINQ 條件轉成查詢參數由伺服端執行
4. 應用場景：
   - 微服務中的資料查詢 API 需要分頁控制與一致的回應格式
   - SDK 封裝跨頁讀取，提供開發者「像列舉單一集合」一樣使用資料的體驗
   - 非 OData/非資料庫來源 API（例如外部開放資料、舊系統）需要在 Client 端優雅處理分頁
   - 需要可中斷的串流式讀取（找到條件即停止）以節省請求與處理成本

### 學習路徑建議
1. 入門者路徑：
   - 學 C# 基本集合、foreach、LINQ 基礎
   - 了解 REST/HTTP 基礎、狀態碼、Header、Query 參數
   - 用 ASP.NET Web API 建立最小可用的 GET 端點、回傳 JSON
2. 進階者路徑：
   - 掌握 yield return 與迭代器模式，實作延遲載入與分頁跨頁巡覽
   - 設計一致的分頁協定（$start/$take、X-DATAINFO-* 標頭、MaxTake）
   - 強化用戶端 SDK：錯誤處理、重試、節流、可中斷列舉、與 LINQ 組合
   - 理解 IEnumerable vs IQueryable 差異，評估是否導入 OData
3. 實戰路徑：
   - 實作伺服端分頁 API（含 HEAD 支援與回應標頭）
   - 開發用戶端 SDK：以 IEnumerable<T> 封裝跨頁取得、允許 LINQ 篩選、支援停止迭代即中止請求
   - 壓力與延遲評估：觀察 API 呼叫與處理交錯、測量早停（Take(1)/break）節省情況
   - 文件化與DX優化：明確規格（參數、Header、限制）、提供範例碼與測試

### 關鍵要點清單
- 分頁協定設計：以 $start/$take 控制範圍，並限制 MaxTake，避免過大請求 (優先級: 高)
- 回應標頭資訊：X-DATAINFO-TOTAL/START/TAKE 提供分頁中繼資料，支援 HEAD 查詢總筆數 (優先級: 高)
- SDK 的角色：用戶端不應在業務碼中充斥分頁細節，應由 SDK 抽象處理 (優先級: 高)
- yield return 與延遲評估：以 IEnumerable 逐頁產出項目，讓取用與處理交錯進行 (優先級: 高)
- LINQ 組合能力：在迭代序列上以 where/Take 等運算子過濾與早停，減少不必要請求 (優先級: 高)
- 早停行為驗證：Take(1) 或 break 能立即停止後續 API 呼叫，降低延遲與流量 (優先級: 高)
- 職責分離：GetBirdsData 專注取數、呼叫端專注處理與過濾，提升可讀性與維護性 (優先級: 中)
- IEnumerable vs IQueryable：IEnumerable 適合客製分頁巡覽；IQueryable 可由 OData 在伺服端執行查詢 (優先級: 中)
- OData 優勢與取捨：能在伺服端過濾/排序/分頁，效率高；但不一定適用於所有資料來源/既有 API (優先級: 中)
- HttpClient 使用要點：基底位址、GET/HEAD 呼叫、錯誤處理與反序列化（Json.NET） (優先級: 中)
- API 效能與穩定：限制單次傳回筆數、減少大資料回傳、可雲端部署（Azure Web App/API App） (優先級: 中)
- DX（Developer Experience）：規格清晰、文件完整、提供可直接使用的 SDK 與範例碼 (優先級: 高)
- 伺服端實作簡化：無資料庫時仍可透過檔案（JSON）與 LINQ 實作分頁示範 (優先級: 低)
- 可測性與觀測：以 log/列印驗證 API 呼叫與資料處理的交錯時序與效能 (優先級: 中)
- 擴充與可靠性：加入重試、節流、取消權杖（CancellationToken）、異步支援以更貼近生產需求 (優先級: 中)