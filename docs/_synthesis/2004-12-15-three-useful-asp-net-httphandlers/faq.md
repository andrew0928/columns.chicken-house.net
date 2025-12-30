---
layout: synthesis
title: "三個好用的 ASP.NET HttpHandler"
synthesis_type: faq
source_post: /2004/12/15/three-useful-asp-net-httphandlers/
redirect_from:
  - /2004/12/15/three-useful-asp-net-httphandlers/faq/
---

# 三個好用的 ASP.NET HttpHandler

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 ASP.NET HttpHandler？
- A簡: 處理特定 URL 或副檔名請求的輕量端點，直接輸出回應，不經過頁面生命週期，適合高效能與客製化內容。
- A詳: ASP.NET HttpHandler 是處理 HTTP 要求的最小單位，對映特定路徑或副檔名並實作 ProcessRequest 直接回應。相比 .aspx 頁面，它省略繁雜的頁面管線，適合檔案串流、動態產生小片段內容、或協定轉換（如 HTTP 到 MMS）。在靜態站點中，Handler 能以最少改動新增 RSS 或虛擬檔案系統等能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1

A-Q2: HttpHandler 與 HttpModule 有何差異？
- A簡: Handler 產生回應；Module 攔截與擴充管線。Handler 是終結點，Module 是橫切關注，用於驗證、記錄等。
- A詳: HttpHandler 負責最終生成回應內容，直接對應特定路徑或副檔名；HttpModule 以事件方式插入 ASP.NET 管線，能在 BeginRequest、Authenticate 等階段攔截並附加行為，如記錄、權限或壓縮。兩者常搭配：Module 處理橫切需求，Handler 聚焦輸出與效能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1

A-Q3: HttpHandler 與 .aspx 頁面有何不同？
- A簡: Handler 輕量直達輸出，.aspx 走完整頁面生命週期。Handler 適合串流與簡單動態，頁面適合豐富 UI。
- A詳: .aspx 頁面具備控制項、ViewState 與生命週期事件，利於 UI 開發；Handler 僅實作 ProcessRequest，無伺服器控制項體系，配置與維護較簡潔。當需求是檔案串流、協定轉換、動態產生小型文件（RSS、ASX）時，Handler 更高效；需要複雜表單與狀態管理則用頁面。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1

A-Q4: 為什麼用 HttpHandler 可增強靜態網站？
- A簡: 以路徑攔截與動態輸出，無需改動既有靜態檔，即可加上 RSS、虛擬目錄與下載控制。
- A詳: 靜態網站常缺少動態功能與後台邏輯。註冊 Handler 後，仍可沿用原有靜態結構，卻能在特定路徑上動態輸出 RSS、將 ZIP 視為資料夾瀏覽、或轉向媒體串流服務。這種非侵入式擴充，降低改版成本，維運風險小，特別適合內容以檔案為主的站點。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q10, C-Q1

A-Q5: 這篇介紹的三個 HttpHandler 是哪些？
- A簡: 媒體轉向 MediaService、資料夾轉 RSS 的 RssMonitor、ZIP 虛擬資料夾 ZipVirtualFolder。
- A詳: 文中實作三個實用 Handler：MediaServiceHttpHandler 將請求自動導向 Windows Media Services（mms://）節省頻寬；RssMonitorHttpHandler 將某資料夾檔案當成文章輸出 RSS，便於訂閱變更；ZipVirtualFolderHttpHandler 讓 .zip 如資料夾般瀏覽與直連，並可一鍵下載，減少重複維護。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q8, A-Q10

A-Q6: 什麼是 MediaServiceHttpHandler？
- A簡: 自動將網站上的影音檔轉交 Windows Media Services 串流，簡化網址並節省網站頻寬。
- A詳: MediaServiceHttpHandler 針對 .wmv/.wma 等媒體請求，回應播放器可理解的轉向（常見為 ASX 播放清單或 302 轉址），使實際傳輸改由 mms:// 來源服務完成。使用者僅訪問 http 網址即可播放，Media Player 7 以上會自動處理，網站本身負載與頻寬壓力大幅降低。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q2, C-Q3

A-Q7: MediaServiceHttpHandler 的核心價值是什麼？
- A簡: 降低網站頻寬負擔、簡化使用者操作、統一網址，並保有串流播放體驗與續傳能力。
- A詳: 將重載的媒體傳輸交由專用串流伺服器處理，可利用其最佳化緩衝、位元率與防斷線能力；前端保持單一 http 入口，免教育使用者切換協定。對站台而言，降低頻寬帳單與 CPU，對使用者而言，點擊即播且相容主流播放器，整體體驗與維運成本同時改善。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q5, D-Q2

A-Q8: 什麼是 RssMonitorHttpHandler？
- A簡: 將資料夾內檔案視為文章，自動輸出 RSS 供訂閱，無須改動既有靜態頁面。
- A詳: RssMonitorHttpHandler 週期性或按需列舉目標目錄檔案，依時間排序並輸出符合 RSS 2.0 規範的 feed。新增檔案即等同發佈新文章，RSS 閱讀器會提示更新。特別適合全靜態網站，快速補齊「訂閱更新」能力，降低使用者追蹤成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, C-Q4

A-Q9: 為什麼用 RSS 追蹤資料夾變更？
- A簡: RSS 提供標準通知機制，使用者以閱讀器自動接收新增或更新檔案訊息。
- A詳: RSS 是成熟的聚合標準，具時間戳、標題、連結等欄位，能代表檔案更新事件。以 RSS 表達目錄變更，免除人工比對時間排序與上次瀏覽記錄，並可跨平台、跨客戶端使用。同時，它對搜尋與歸檔友善，讓靜態資產擁有類似部落格的發布與追蹤體驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q8, D-Q3

A-Q10: 什麼是 ZipVirtualFolderHttpHandler？
- A簡: 讓 .zip 檔像資料夾般可瀏覽與連結，並支援直接下載，減少檔案重複維護。
- A詳: ZipVirtualFolderHttpHandler 攔截 *.zip 路徑，將其視為一個虛擬目錄：/a.zip 顯示索引，/a.zip/file.htm 直連壓縮內檔案；加上 ?download 則回傳整包下載。如此只需上傳一份 zip 即可同時提供線上瀏覽與下載，省去同步兩份內容的困擾。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q6

A-Q11: 把 ZIP 視為虛擬資料夾有何好處？
- A簡: 一份檔同時供瀏覽與下載，降低重複、提升維護性，網址也更直覺且可深連。
- A詳: 同個相簿或報表常需線上瀏覽與封包下載，若維護兩份（解壓與壓縮）易出現版本不一。虛擬資料夾模式讓 zip 成為來源事實，列表頁自動生成、檔案可深鏈、下載可控權限與檔名，並可套用快取與 CDN，大幅簡化流程與成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q11, C-Q7

A-Q12: 什麼是 Windows Media Services 與 mms://？
- A簡: WMS 為微軟串流伺服器，mms:// 是其串流協定，優化即時播放與網路抖動。
- A詳: Windows Media Services 提供音影片即時串流，含緩衝、位元率調整與多人同播等能力。mms:// 為其常見協定，播放器能直接連線取得串流。以 Handler 將 http 問路轉往 mms，可保留使用者簡單入口，同時借力專用伺服器的串流效能與穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q3, D-Q2

A-Q13: RSS 訂閱對純靜態網站的價值是什麼？
- A簡: 無須後端系統即可推送更新，提升回訪率與觸達，對 SEO 與使用者體驗皆有益。
- A詳: 靜態站點缺乏資料庫與程式邏輯，但可由 Handler 掃描檔案輸出 RSS。訂閱者將自動收到新增或更新通知，降低資訊落差；搜尋引擎也常抓取 RSS，加速索引。整體上以低成本帶來更高互動與流量品質。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q7, D-Q3

A-Q14: ?download 參數的用途與行為差異？
- A簡: 控制回應為直接下載或線上瀏覽，常以 Content-Disposition 切換附件或內嵌。
- A詳: 在 ZipVirtualFolder 中，附加 ?download 代表要求整包下載；未附加則顯示索引頁或串流單檔。實作上透過 Content-Disposition 設定 attachment 或 inline，並搭配正確 MIME type 與檔名。此模式也可拓展到其他資源的下載政策。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8, D-Q7

A-Q15: 為何說「科技來自惰性」是設計動機？
- A簡: 以最小改動自動化繁瑣步驟，藉懶人思維驅動高效工具與維運簡化。
- A詳: 文中三個 Handler 都旨在省去重複與教學成本：自動轉向串流省頻寬、資料夾即 RSS 免手動公告、ZIP 虛擬資料夾免重複部署。透過「不想做重工」的動機，促成兼顧效率、穩定與體驗的實用設計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5

A-Q16: 何時不適合使用 HttpHandler？
- A簡: 需要複雜 UI、狀態管理或 MVC 路由一致性時，應以頁面或框架方案處理。
- A詳: Handler 適合單一職責、無 UI 的輸出。若需求涉及豐富介面、模型繫結、驗證流程、國際化 UI 或需與 MVC 統一路由，採用頁面或控制器更易維護。同樣地，若需跨多端共用中介行為，HttpModule 或反向代理可能更恰當。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q3, B-Q14, D-Q9

### Q&A 類別 B: 技術原理類

B-Q1: HttpHandler 在 ASP.NET 管線中如何運作？
- A簡: 請求進入 IIS 與 ASP.NET 管線後，依對映規則選擇 Handler，執行 ProcessRequest 產出回應。
- A詳: 流程為：IIS 接收請求，交由 ASP.NET 管線；根據設定（system.web/httpHandlers 或 system.webServer/handlers）匹配路徑與副檔名，解析到對應 Handler 類型。建立實例後呼叫 ProcessRequest（或非同步模式），寫入 Response，再回傳至伺服器。Module 可在多個節點橫切加入行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q2, B-Q2

B-Q2: Handler 的註冊與匹配順序是什麼？
- A簡: 依組態節點順序與最長路徑優先匹配；IIS 整合與傳統模式映射節點不同。
- A詳: 在 .NET Framework 傳統模式使用 system.web/httpHandlers；IIS 7+ 整合模式以 system.webServer/handlers 為主。匹配時先比對明確路徑，再比副檔名萬用字元，越具體越優先。順序影響結果，避免與 MVC 路由重疊時需調整優先權與 ignore 路由規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q9, D-Q10

B-Q3: MediaService 的轉向機制是什麼？
- A簡: 以 ASX 播放清單或 HTTP 302 將請求導向 mms://，播放器自動解析並串流播放。
- A詳: 常見做法為回傳 Content-Type: video/x-ms-asf 並輸出 ASX，內含 mms:// 真實來源；或以 302 Location 指向 mms://。ASX 相容性佳且可容納多來源與中繼資訊。Handler 判斷副檔名後動態生成轉向內容，前端網址保持 http 統一入口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q12, C-Q3

B-Q4: 如何辨識媒體副檔名與播放器相容性？
- A簡: 以白名單比對副檔名，設定適當 MIME；如需，偵測 User-Agent 或回退方案。
- A詳: 設定可播放副檔名白名單（如 .wmv/.wma/.asf），對應 MIME type 與轉向策略。若需提高相容，可依 User-Agent 選擇 ASX 或直接檔案下載作為回退。為避免誤判，拒絕未知副檔名，並記錄日誌以利調整白名單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q11, D-Q1

B-Q5: 如何產生 ASX 播放清單與設定 Content-Type？
- A簡: 輸出簡單 ASX XML，Content-Type 設為 video/x-ms-asf，內含 mms:// 目標。
- A詳: ASX 本質為 XML。最小結構包含 asx 與 entry 的 ref href 指向 mms://。回應標頭需設 Content-Type: video/x-ms-asf，避免瀏覽器當純文字下載。可加 title、author 等中繼資料。簡潔輸出即可滿足 Media Player 7+ 自動播放需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q1

B-Q6: RssMonitor 的流程為何？
- A簡: 列舉資料夾檔案、依時間排序、映射為 RSS item，輸出 RSS 2.0 XML。
- A詳: Handler 解析目標目錄，取得 FileInfo 清單，按 LastWriteTime 降冪排序。每檔案映射為 item：title 用檔名、link 指向對應網址、pubDate 用 UTC。可限制數量與副檔名，並輸出有效期與快取標頭，減少讀取成本與頻寬。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q7, C-Q4

B-Q7: RSS 2.0 的基本結構是什麼？
- A簡: rss 根含 channel，內有 title、link、description 與多個 item，item 含標題、連結、日期。
- A詳: RSS 2.0 採用 rss version="2.0"，channel 節點包含標題、站台連結、摘要、語言等；每個 item 代表一則更新，含 title、link、guid、pubDate、description。內容採 UTF-8，pubDate 用 RFC 1123。對靜態資源，可用檔案大小與時間組合成 guid。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q4, D-Q3

B-Q8: RSS 的條件式請求與快取如何運作？
- A簡: 以 Last-Modified 與 ETag 支援 304，RSS 閱讀器可減少流量並加速同步。
- A詳: Handler 計算 feed 的 Last-Modified（最新檔案時間）與 ETag（如哈希：時間+數量）。當客戶端帶 If-Modified-Since 或 If-None-Match 比對相同時，回 304 Not Modified。並可設定 Cache-Control 與 Expires，平衡即時性與效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q8

B-Q9: Zip 虛擬資料夾如何解析路徑？
- A簡: 解析 /a.zip 與子路徑 /a.zip/x，決定列出清單或回傳壓縮內對應條目。
- A詳: 先分離實體 zip 路徑與 zip 內子路徑。若指向 zip 根且無 download 參數，生成索引頁；若包含內部子路徑，尋找對應 ZipEntry 串流輸出；若帶 ?download 則回傳整包。需處理路徑正規化、大小寫與分隔符一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q6, C-Q7

B-Q10: 讀取 ZIP 的核心組件有哪些選擇？
- A簡: 新版可用 System.IO.Compression，舊版可用 SharpZipLib，依需求取捨效能與相依。
- A詳: .NET 4.5+ 提供 ZipArchive 與 ZipArchiveEntry，API 簡潔且整合。早期框架可採用 SharpZipLib 等第三方函式庫。選擇時考量串流存取、解壓單檔、不展開至磁碟、及大檔效能。避免將整包載入記憶體，採逐段讀寫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q6

B-Q11: 串流與回應標頭該如何設計？
- A簡: 設定正確 MIME、Content-Length、Content-Disposition；採用逐段串流避免記憶體爆量。
- A詳: 根據副檔名決定 Content-Type；檔長已知可填 Content-Length 以利進度條；下載時使用 Content-Disposition: attachment; filename="..."；串流時使用 4–64KB 緩衝循環寫出，關閉 Response.BufferOutput 以減少延遲，並適度設定 Cache-Control。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, C-Q8, D-Q7

B-Q12: 如何支援 Range 斷點續傳與節流？
- A簡: 解析 Range 標頭，回 206 與 Content-Range，僅輸出指定區段；節流控制輸出速率。
- A詳: 當請求帶 Range: bytes=start-end，驗證範圍後回 206 Partial Content，標頭含 Accept-Ranges、Content-Range、對應 Content-Length。串流僅從偏移開始輸出。節流可每迴圈 Sleep 或計時控制吞吐，避免壓垮伺服器或頻寬。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q7, D-Q6

B-Q13: 安全防護應考慮哪些面向？
- A簡: 防路徑穿越、限制副檔名、避免任意檔案下載、過濾不安全輸入並記錄。
- A詳: 驗證請求字串，移除 .. 與非法字元；僅允許白名單副檔名；ZIP 內路徑需正規化防穿越；下載檔名需編碼；避免回應敏感系統檔。記錄異常請求與拒絕原因，並於錯誤時回適當狀態碼，防信息洩漏。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q5, D-Q10

B-Q14: IIS 傳統與整合管線在映射上有何差異？
- A簡: 傳統用 system.web/httpHandlers；整合用 system.webServer/handlers，且可攔截所有請求。
- A詳: IIS 6 與 classic 模式僅映射已註冊副檔名；IIS 7+ integrated 模式把所有請求交給 ASP.NET，可針對無副檔名路徑運作。註冊位置、順序與權限略有差異，建議同時配置兩節點以相容不同部署環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q10

B-Q15: 何時採用非同步 HttpHandler？
- A簡: 長時間 I/O（串流遠端、雲端存取）用非同步釋放執行緒，提高併發效率。
- A詳: 非同步 Handler 以 IHttpAsyncHandler 或 async/await 模式實作，將等待 I/O 的時間讓出，提升可擴展性。適用於串流媒體來源、雲端儲存讀取或大型 ZIP 條目存取。需注意回應生命週期與例外處理一致性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q10, C-Q7

B-Q16: 如何讓 Handler 易於維運與配置？
- A簡: 以組態驅動目錄、白名單與目標主機，支援熱更新與清晰日誌。
- A詳: 將目標資料夾、ZIP 列表樣式、媒體轉向主機、允許副檔名等設為 appSettings 或自定節點，部署時無需重編。加上結構化日誌（來源、延遲、錯誤碼），並提供健康檢查端點，方便監控與問題排查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, D-Q8, D-Q10

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Web.config 註冊三個 Handler？
- A簡: 於 system.webServer/handlers 與 system.web/httpHandlers 註冊對應路徑與型別，確保兩模式相容。
- A詳: 具體步驟：1) 參考組件 ChickenHouse.Web；2) 在 system.web/httpHandlers 加入 add path="*.wmv" type="...MediaServiceHttpHandler"、add path="rss/*" type="...RssMonitorHttpHandler"、add path="*.zip" type="...ZipVirtualFolderHttpHandler"；3) 在 system.webServer/handlers 重覆註冊並設定 verb="GET" resourceType="Unspecified"；4) 部署後以測試 URL 驗證匹配。注意順序與萬用字元避免衝突。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q14

C-Q2: 如何實作 MediaServiceHttpHandler 基本骨架？
- A簡: 實作 IHttpHandler，判斷副檔名，建立 mms 目標並輸出轉向內容或 302。
- A詳: 步驟：1) 建類別實作 IHttpHandler；2) 於 ProcessRequest 取得原始 URL 與檔名；3) 比對白名單（.wmv/.wma）；4) 構造 mms://host/path；5) 依策略輸出 ASX 或設 Response.StatusCode=302、Location=mms://...；6) 設定 Content-Type 與快取。範例程式碼：class MediaServiceHttpHandler : IHttpHandler { public void ProcessRequest(HttpContext ctx){ /* build mms and write ASX */ } public bool IsReusable=>true; }。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, B-Q5

C-Q3: 如何產生 ASX 並正確設定 Content-Type？
- A簡: 回傳 video/x-ms-asf，輸出含 mms 連結的 asx+xml，確保播放器自動啟播。
- A詳: 步驟：1) Response.ContentType="video/x-ms-asf"；2) 以 UTF-8 輸出字串：<asx version="3.0"><entry><ref href="mms://host/file.wmv" /></entry></asx>；3) 可加 <title> 與多個 entry 作備援；4) 設定 Cache-Control 與 Expires；5) 測試用戶端 Media Player、VLC 相容性。注意避免 HTML 編碼破壞 XML。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q1

C-Q4: 如何實作 RssMonitor 將資料夾輸出為 RSS？
- A簡: 列舉檔案、排序、映射 item，輸出 RSS 2.0 XML，連結指回原檔或頁面。
- A詳: 步驟：1) 讀取目標根目錄（組態）；2) Directory.EnumerateFiles 過濾副檔名；3) 依 LastWriteTimeUtc 排序取前 N；4) 生成 XML：channel 與 item；5) link 指向網站對應可瀏覽網址；6) 設 ContentType="application/rss+xml"；7) 加入 Last-Modified 與 ETag。程式碼片段：foreach(var f in files){ writer.WriteStartElement("item"); /* title/link/pubDate */ }。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, B-Q8

C-Q5: 如何為 RSS 加入 ETag 與 304 支援？
- A簡: 以最新檔案時間與數量產生指紋，對應 If-None-Match 或 If-Modified-Since 回 304。
- A詳: 步驟：1) 取得最新 LastWriteTimeUtc 與檔案總數；2) 以 $"{ticks}-{count}" 計算雜湊作 ETag；3) Response.AddHeader("ETag", etag)；4) Response.Cache.SetLastModified(latest)；5) 比對 Request.Headers 中 If-None-Match 與 If-Modified-Since，一致則 Response.StatusCode=304 並 End；6) 確保時區用 UTC，避免誤判。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q8

C-Q6: 如何實作 ZipVirtualFolder 列表頁？
- A簡: 開啟 zip，羅列條目為超連結，資料夾以階層呈現，並提供一鍵下載連結。
- A詳: 步驟：1) 判斷是否在 zip 根路徑；2) 使用 ZipArchive 讀取 entries；3) 建立目錄樹；4) 產出簡單 HTML：資料夾與檔案，對檔案建立 /a.zip/path/to/file 連結；5) 提供 /a.zip?download 下載按鈕；6) 避免 XSS，對名稱做 HTML 編碼；7) 可加入簡易樣式與分頁。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10

C-Q7: 如何從 ZIP 串流內部單一檔案？
- A簡: 取得 ZipArchiveEntry 開啟串流，以固定緩衝寫入 Response，設定正確 MIME 與長度。
- A詳: 步驟：1) 解析 zip 路徑與內部子路徑；2) 使用 ZipArchive.GetEntry 找到檔案；3) 以 entry.Open() 得到 Stream；4) Response.ContentType=MimeMap.Get(ext)；5) 若可取得長度，設定 Content-Length；6) while(read) Response.OutputStream.Write(buffer)；7) 支援 Range 時計算偏移。注意關閉資源與例外處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q12, D-Q6

C-Q8: 如何實作 ?download 切換下載或內嵌？
- A簡: 解析查詢字串，設 Content-Disposition 為 attachment 或 inline，並處理安全檔名。
- A詳: 步驟：1) var dl = Request["download"]!=null；2) 若 dl 為真，Response.AddHeader("Content-Disposition",$"attachment; filename=\"{safe}\"")；3) safe 以 UrlPathEncode 或 RFC5987 方式處理；4) 未帶 dl 則 inline；5) 搭配 Cache-Control 與 ETag；6) 實測瀏覽器行為（Chrome、Edge）確保一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q7

C-Q9: 如何為 Handler 寫單元測試？
- A簡: 以模擬 HttpContext 或使用 HttpSimulator，注入假請求與回應串流驗證輸出。
- A詳: 步驟：1) 將核心邏輯抽出為可測方法（路徑解析、ASX/RSS 生成）；2) 使用自製 FakeHttpContext 包裝記憶體串流；3) 呼叫 ProcessRequest，檢查 ContentType、狀態碼與輸出字串；4) 為錯誤情境建立測試（不存在檔、非法路徑）；5) 在 CI 中自動執行回歸。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q16, D-Q10

C-Q10: 如何部署到 IIS 並驗證？
- A簡: 複製組件、更新 Web.config 映射，設定處理常式權限，逐一測試三條功能路徑。
- A詳: 步驟：1) 發佈網站與 ChickenHouse.Web.dll；2) 設定 handlers（整合模式建議）；3) 確認應用程式集區 .NET 版本；4) 測試：a) 影音檔 http URL 會播放；b) RSS 位址能被閱讀器訂閱；c) zip 根、子檔、?download 均工作；5) 檢查 IIS 日誌與事件檢視器；6) 加上健康檢查與監控。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q14, D-Q10

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 影音點開卻下載 .asx 不自動播放，怎麼辦？
- A簡: 檢查 Content-Type 是否為 video/x-ms-asf，並驗證用戶端播放器相容與副檔名。
- A詳: 症狀：瀏覽器直接下載 .asx 或以文字顯示。可能原因：Content-Type 錯誤、ASX 格式不正確、用戶端無關聯播放器。解法：1) 設定 video/x-ms-asf；2) 驗證 ASX 結構與 mms 連結；3) 測試 Media Player、VLC；4) 提供回退為直接下載。預防：建立自動化測試與白名單檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q3

D-Q2: 播放器無法連到 mms://，如何排查？
- A簡: 檢查 mms 來源可達性、防火牆與 DNS，必要時改走 http 串流或備援來源。
- A詳: 症狀：播放器啟動後顯示無法連線。原因：WMS 未啟動、防火牆阻擋、mms 不被允許、DNS 解析失敗。步驟：1) 以播放器直連測試；2) 檢查 WMS 狀態與埠；3) 網路追蹤（tracert、telnet）；4) 在 ASX 提供 http 備援來源。預防：監控來源可用性與自動切換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q3

D-Q3: RSS 閱讀器無法訂閱或報 XML 錯誤？
- A簡: 檢查 XML 格式、UTF-8 編碼、Content-Type 與必要欄位，修正不合法字元。
- A詳: 症狀：解析失敗、亂碼或顯示空白。原因：缺少 channel 欄位、日期格式錯、編碼非 UTF-8、描述含未轉義字元。解法：1) 驗證 RSS 2.0 結構；2) 設 Content-Type=application/rss+xml；3) 使用 RFC1123 pubDate；4) HTML/XML 轉義。預防：加入驗證器測試與單元測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q4

D-Q4: RSS 項目時間顯示不正確，如何修正？
- A簡: 統一使用 UTC 並格式化為 RFC1123，避免時區與夏令時間造成偏差。
- A詳: 症狀：閱讀器顯示時間早/晚數小時。原因：使用本地時間、時區未標註、格式不符。解法：1) 使用 DateTime.UtcNow 與 LastWriteTimeUtc；2) ToString("r") 產生 RFC1123；3) 伺服器時間同步 NTP。預防：以測試涵蓋跨時區與夏令時間案例。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q4, C-Q5

D-Q5: ZIP 列表中文檔名亂碼怎麼辦？
- A簡: 檢查 ZIP 內編碼旗標與檔名轉碼，輸出時做正確的 HTML 編碼。
- A詳: 症狀：列表顯示亂碼或連結失效。原因：ZIP 使用舊編碼、未標 UTF-8、瀏覽器解讀不同。解法：1) 使用支援 UTF-8 的 Zip 函式庫；2) 嘗試以指定編碼讀取；3) 連結與頁面皆做 HTML/URL 編碼。預防：建立命名規範，優先使用 UTF-8。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q6

D-Q6: ZIP 串流速度慢或 CPU 高，如何優化？
- A簡: 採逐段串流、避免解壓到磁碟、使用較大緩衝與非同步 I/O，必要時節流。
- A詳: 症狀：高延遲、CPU 飆高。原因：一次性解壓、緩衝太小、同步阻塞。解法：1) 逐段讀寫 32–64KB；2) 避免中間檔；3) 使用 async/await；4) 啟用壓縮等級調整或關閉重壓縮；5) 開啟 HTTP 壓縮僅限文字。預防：壓測、監控延遲與吞吐。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q12, C-Q7

D-Q7: ?download 無效仍被瀏覽器內嵌開啟？
- A簡: 強制 Content-Disposition=attachment 並設定八位元組安全檔名與正確 MIME。
- A詳: 症狀：PDF、影像仍內嵌顯示。原因：瀏覽器預設行為、MIME 判斷優先。解法：1) 明確 attachment；2) 設定不易被內嵌的 MIME 或副檔名；3) 加上 X-Content-Type-Options: nosniff；4) 驗證檔名編碼。預防：提供一致下載子網域或規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8

D-Q8: RSS 或列表無快取導致瀏覽慢，如何改善？
- A簡: 實作 Last-Modified/ETag、設定 Cache-Control 與伺服器端快取或記憶體快取。
- A詳: 症狀：每次請求都全量掃描與生成。原因：缺少條件式請求與伺服器快取。解法：1) 加入 304 支援；2) 設 Expires/Max-Age；3) 用 MemoryCache 暫存生成結果；4) 設快取失效條件（檔案變更）。預防：監控快取命中率並調整策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5

D-Q9: Handler 與 MVC 路由衝突怎麼辦？
- A簡: 調整 handlers 映射順序或於路由忽略特定模式，確保請求正確落到 Handler。
- A詳: 症狀：請求被 MVC 攔截回 404 或錯誤。原因：整合管線中 MVC 路由先匹配。解法：1) 在 RouteConfig 忽略相符路徑（routes.IgnoreRoute）；2) 提升 handlers 優先權與明確 path；3) 使用獨立虛擬目錄。預防：規劃清楚路徑命名避免重疊。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, B-Q14, C-Q1

D-Q10: 部署後回 404 或 500，Handler 未觸發？
- A簡: 檢查 IIS 管線模式、處理常式對應、應用程式集區版本與組件部署完整性。
- A詳: 症狀：請求未經 Handler 或拋例外。原因：未註冊 handlers、IIS 模式不符、缺少組件、權限不足。步驟：1) 確認 system.webServer/handlers 設定；2) 檢查應用程式集區 .NET 版本；3) 檢視事件記錄與詳細錯誤；4) 開啟 Failed Request Tracing。預防：部署腳本化與健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 ASP.NET HttpHandler？
    - A-Q2: HttpHandler 與 HttpModule 有何差異？
    - A-Q3: HttpHandler 與 .aspx 頁面有何不同？
    - A-Q4: 為什麼用 HttpHandler 可增強靜態網站？
    - A-Q5: 這篇介紹的三個 HttpHandler 是哪些？
    - A-Q6: 什麼是 MediaServiceHttpHandler？
    - A-Q8: 什麼是 RssMonitorHttpHandler？
    - A-Q10: 什麼是 ZipVirtualFolderHttpHandler？
    - A-Q13: RSS 訂閱對純靜態網站的價值是什麼？
    - A-Q14: ?download 參數的用途與行為差異？
    - B-Q1: HttpHandler 在 ASP.NET 管線中如何運作？
    - B-Q7: RSS 2.0 的基本結構是什麼？
    - C-Q1: 如何在 Web.config 註冊三個 Handler？
    - C-Q4: 如何實作 RssMonitor 將資料夾輸出為 RSS？
    - C-Q10: 如何部署到 IIS 並驗證？

- 中級者：建議學習哪 20 題
    - A-Q7: MediaServiceHttpHandler 的核心價值是什麼？
    - A-Q9: 為什麼用 RSS 追蹤資料夾變更？
    - A-Q11: 把 ZIP 視為虛擬資料夾有何好處？
    - A-Q12: 什麼是 Windows Media Services 與 mms://？
    - A-Q16: 何時不適合使用 HttpHandler？
    - B-Q2: Handler 的註冊與匹配順序是什麼？
    - B-Q3: MediaService 的轉向機制是什麼？
    - B-Q4: 如何辨識媒體副檔名與播放器相容性？
    - B-Q5: 如何產生 ASX 播放清單與設定 Content-Type？
    - B-Q6: RssMonitor 的流程為何？
    - B-Q8: RSS 的條件式請求與快取如何運作？
    - B-Q9: Zip 虛擬資料夾如何解析路徑？
    - B-Q10: 讀取 ZIP 的核心組件有哪些選擇？
    - B-Q11: 串流與回應標頭該如何設計？
    - C-Q2: 如何實作 MediaServiceHttpHandler 基本骨架？
    - C-Q3: 如何產生 ASX 並正確設定 Content-Type？
    - C-Q5: 如何為 RSS 加入 ETag 與 304 支援？
    - C-Q6: 如何實作 ZipVirtualFolder 列表頁？
    - C-Q7: 如何從 ZIP 串流內部單一檔案？
    - D-Q3: RSS 閱讀器無法訂閱或報 XML 錯誤？

- 高級者：建議關注哪 15 題
    - B-Q12: 如何支援 Range 斷點續傳與節流？
    - B-Q13: 安全防護應考慮哪些面向？
    - B-Q14: IIS 傳統與整合管線在映射上有何差異？
    - B-Q15: 何時採用非同步 HttpHandler？
    - B-Q16: 如何讓 Handler 易於維運與配置？
    - C-Q8: 如何實作 ?download 切換下載或內嵌？
    - C-Q9: 如何為 Handler 寫單元測試？
    - D-Q1: 影音點開卻下載 .asx 不自動播放，怎麼辦？
    - D-Q2: 播放器無法連到 mms://，如何排查？
    - D-Q5: ZIP 列表中文檔名亂碼怎麼辦？
    - D-Q6: ZIP 串流速度慢或 CPU 高，如何優化？
    - D-Q7: ?download 無效仍被瀏覽器內嵌開啟？
    - D-Q8: RSS 或列表無快取導致瀏覽慢，如何改善？
    - D-Q9: Handler 與 MVC 路由衝突怎麼辦？
    - D-Q10: 部署後回 404 或 500，Handler 未觸發？