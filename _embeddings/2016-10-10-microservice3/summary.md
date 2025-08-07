# API & SDK Design #1, 資料分頁的處理方式

## 摘要提示
- 微服務架構: 服務化後 API 必須以 DX 為核心，文件、介面與 SDK 都要對開發者友善。
- 資料分頁: 不論 UI 或 API，分頁邏輯若落到前端組裝，極易產生「義大利麵式」程式碼。
- C# yield return: 透過迭代器模式可優雅地隱藏分頁流程，讓資料存取與處理高度解耦。
- API 設計: 範例 API 每次最多回傳 10 筆，使用 $start/$take 參數與自訂 Header 傳遞總筆數等資訊。
- DX 考量: 好的 API 除了功能完整，更要效能佳、行為穩定、文件清楚，才能被開發者採用。
- Server 端實作: 以 ASP.NET Web API 實作 BirdsController，從 JSON 檔快速提供查詢服務。
- Client 直接呼叫: 傳統 HttpClient + 迴圈處理分頁，程式碼冗長且邏輯交織。
- Client 改用 yield: GetBirdsData() 以 yield return 包裝，主程式可 LINQ 過濾並即時中斷。
- 效能驗證: yield 版能在找到目標後立即停止後續呼叫，省流量又省時間。
- OData 比較: 若可使用 OData/IQueryable，可將查詢條件推送到伺服器端，效能更上一層樓。

## 全文重點
本文延續「微服務架構」主題，以政府公開的鳥類觀察資料為例，示範服務化後的 API、SDK 與應用程式三者的關係，並聚焦於「資料分頁」處理技巧。作者指出，API 的直接使用者是開發者，衡量標準是 DX 而非 UX，因此在設計上必須讓查詢介面簡潔、文件完善、效能穩定。範例 Server 端採用 ASP.NET Web API，將 1000 筆 JSON 資料包裝成 /api/birds 服務，提供 $start 與 $take 參數限制一次最多 10 筆，並於 Response Header 回傳總筆數等資訊。同時支援 HEAD 動作，方便 Client 只要統計資料量而不下載內容。

在 Client 端，作者先示範傳統 HttpClient 逐頁呼叫的寫法，需自行維護 current、pagesize、迴圈與過濾邏輯，程式碼顯得雜亂。接著改以 C# 的 yield return 實作 GetBirdsData()，將「取得下一頁」包進迭代器，主程式僅以 LINQ 查詢並 foreach 處理結果，分頁與過濾自然分離，程式碼更易讀、易維護。實測顯示，yield 版會在每取得一頁後立即處理，並可在找到目標資料後中斷迴圈，不會再向 Server 發出不必要的請求。

最後作者將此方式與 OData/IQueryable 作比較：yield + IEnumerable 只能逐筆掃描；若採 OData，查詢條件可被翻譯為 Server 端 SQL，僅回傳真正需要的資料，效能更佳。總結而言，善用語言特性與正確的 API 設計原則，可大幅提升微服務環境下的 DX 與系統維護性。

## 段落重點
### 範例 Data API Service: Server Side Data Paging
說明文章動機與背景：微服務拆分完成後，需要設計對開發者友善的 API；分頁則是最常見卻也最容易寫得雜亂的功能。作者決定以鳥類觀察資料為例，示範完整的 Server、SDK 及 APP 間互動，同時觀察團隊常犯的實作疏忽。

### DATA FORMAT 說明
為簡化示範，未使用資料庫與 EF，而是下載「特生中心 102 年繁殖鳥大調查」的 JSON 檔，共 1000 筆。並列出兩筆資料格式，包含 SerialNo、SurveyDate、Location…等欄位，存放於 ~/App_Data/birds.json，方便程式直接讀取。

### API CODE (SERVER) 說明
建立 Azure Web App 類型的 ASP.NET Web API 專案，保留最精簡結構。BirdsController 於 Initialize 時讀取 JSON 至記憶體，並實作 HEAD 及 GET 兩動作：HEAD 僅回傳總筆數 Header；GET 依 $start/$take 參數分頁，補上 X-DATAINFO-* 自訂 Header，再用 LINQ Skip/Take 切片後回傳 IEnumerable<BirdInfo>。

### API 呼叫方式說明
1. /api/birds?$start&$take：列舉所有資料，預設從 0 起，最大一次 10 筆，並透過 Header 回報 TOTAL、START、TAKE；HEAD 動作只取 Header。  
2. /api/birds/{id}：依 BirdId 取單筆。作者指出，正式專案可用 EF + OData 自動完成，但為了示範手刻分頁才採手動實作。

### APP CODE 說明 (直接使用 HttpClient)
以 Console App 示範最直覺的呼叫方式：設定 BaseAddress，迴圈維護 current 與 pagesize，每頁呼叫一次 API，再用 Json 反序列化、手動過濾 Location="玉山排雲山莊"。整段邏輯摻雜分頁與過濾，共 20 行以上，程式難以維護且可讀性差；在本機測試需約 3 秒掃完。

### APP CODE 說明 (使用 C# yield return)
改寫為 GetBirdsData() 方法，以 HttpClient 逐頁抓取資料、內部 foreach yield return；呼叫端 ListAll_UseYield 只需一行 LINQ 過濾 + foreach 即可列印結果。此作法將「資料取得」與「資料處理」切開，程式清晰，且執行時仍維持分頁抓取而非一次載入。

### 結果觀察 - 觀察 API 呼叫與資料處理的交錯執行狀況
透過在 GetBirdsData() 內插入 log，可見每抓一頁就立即處理該頁資料，印完再進下一頁，證明 yield return 產生的迭代器確實交錯執行，不會先全部下載後才處理。

### 結果觀察 - 中斷迴圈，資料載入狀況觀察
將主程式改為 Take(1) 或在 foreach 中 break，可觀察到當找到目標資料後即停止後續 API 呼叫，總耗時僅 266ms。示範 yield return 能在任意時刻優雅終止，節省頻寬與時間。

### yield return 應用小結
作者總結：yield return 是處理遠端分頁資料的經典技巧，可讓 iterator 抽象化分頁流程；若環境允許，使用 OData 及 IQueryable 可再把查詢條件推向 Server 端，效能更卓越。理解兩種模式的差異，能在不同專案中彈性選擇最合適的實作方式。