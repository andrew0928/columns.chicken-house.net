---
layout: synthesis
title: "FlickrProxy #2 - 實作"
synthesis_type: faq
source_post: /2008/05/19/flickrproxy-2-implementation/
redirect_from:
  - /2008/05/19/flickrproxy-2-implementation/faq/
---

# FlickrProxy #2 - 實作

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 FlickrProxy？
- A簡: FlickrProxy 是一個 ASP.NET HttpHandler，攔截網站圖片請求，首次自動上傳至 Flickr，之後以 302 轉址到 Flickr 圖片，節省站台頻寬且不需改動原有 HTML。
- A詳: FlickrProxy 是以 ASP.NET HttpHandler 為核心的「圖片代理」方案。它在 IIS 讓 .JPG 由 ASP.NET 接管，Handler 判斷是否需轉移至 Flickr：若未上傳過，先用 FlickrNet API 上傳並建立快取資訊；若已存在，直接回應 302 Redirect 指向 Flickr 圖片網址。此設計讓 Blogger 維持既有上傳與引用圖片的習慣，不需修改任何 HTML 或資料結構，同時把圖片流量轉移到 Flickr，達到頻寬節省與快速回覆。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1

Q2: FlickrProxy 的核心目標是什麼？
- A簡: 不改變 Blogger 使用習慣與資料結構，自動化圖片上傳與轉址，達到頻寬外移、可逆調整與維持使用者體驗一致。
- A詳: 核心目標包含三點：一、不改變內容生產者的工作流程與現有 HTML，讓 Blogger 完全無感；二、以自動化機制將圖片上傳到 Flickr 並以轉址提供外部載入，將圖片流量從自家伺服器導向 Flickr；三、所有改變均可逆，包含可關閉機制或回復為站內靜態檔案回應，確保資料安全性與風險可控。這些目標透過 IIS 對應、HttpHandler 控制、快取與 Flickr API 整合實現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q20, B-Q1

Q3: 為什麼選擇 HttpHandler 而非修改 HTML？
- A簡: HttpHandler 方案不需觸碰內容與版面，集中在伺服器端攔截圖片請求；相較改寫 HTML，更可逆、風險低且維護成本小。
- A詳: 修改 HTML 需逐頁處理字串替換或重寫標記，開發維護成本高且易誤傷內容。以 HttpHandler 攔截請求，對前端透明、對資料零侵入，僅調整 IIS/ASP.NET 對應與單一程式碼路徑即可管理所有圖片請求。此外，遇到問題可立即以 web.config 切回內建 StaticFileHandler，快速回復原狀。這種「管線攔截」比「內容改寫」更穩健與可逆。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2, C-Q3

Q4: 什麼是 ASP.NET HttpHandler？
- A簡: HttpHandler 是 ASP.NET 處理特定 URL 模式的端點，可接管請求、回應內容或轉址，常用於動態資源或自訂協議。
- A詳: HttpHandler 透過 web.config 註冊，將符合路徑與動詞的 HTTP 請求導向特定類別處理。它實作 IHttpHandler.ProcessRequest，能讀取請求、執行業務邏輯、輸出回應或進行 302 轉址。相較 Page，它更輕量、適合針對單一資源類型（如圖片、檔案、縮圖、代理）進行自訂處理。本案例中，Handler 依條件判斷是否上傳 Flickr 與快取，最後回應 Redirect。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q4

Q5: IIS 與 ASP.NET 在處理靜態檔案的關係是什麼？
- A簡: 預設 IIS 直接回傳靜態檔案；若將副檔名對應到 ASP.NET ISAPI，才會進入 ASP.NET 管線，由 HttpHandler 決定處理方式。
- A詳: IIS 的「應用程式對應」決定請求走向。未對應 ASP.NET 的副檔名（如 .jpg）會由 IIS 直接傳回檔案；若對應到 aspnet_isapi.dll，請求將進入 ASP.NET 管線，再由 web.config 的 httpHandlers 決定最終處理者。本文先將 .jpg 交給 ASP.NET，再於全域使用 StaticFileHandler 維持原行為，最後在特定目錄覆蓋為 FlickrProxyHttpHandler。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, C-Q3, B-Q7

Q6: aspnet_isapi.dll 的角色是什麼？
- A簡: aspnet_isapi.dll 是 IIS 與 ASP.NET 的橋接程式，將符合對應的請求導入 ASP.NET 執行管線，以便由 Handler/Module 處理。
- A詳: 在 IIS 6（經典管線）或啟用 ISAPI 的情境下，aspnet_isapi.dll 是讓特定副檔名（.aspx、.ashx、.jpg 等視設定）被 ASP.NET 接手的關鍵。它不負責商業邏輯，而是接入點，後續由 ASP.NET 根據 web.config 解析 httpHandlers、httpModules，決定最終處理方式。本文藉此讓 .jpg 進入 ASP.NET，才有機會由自訂 Handler 接管。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q7

Q7: System.Web.StaticFileHandler 是什麼？
- A簡: StaticFileHandler 是 ASP.NET 內建處理器，行為等同 IIS 靜態回傳，原封不動傳回檔案位元組內容。
- A詳: 當某副檔名被 ASP.NET 接手，但你仍希望維持靜態檔案回應行為，可在 httpHandlers 指派 System.Web.StaticFileHandler。它尊重檔案系統與 HTTP 快取標頭，不做額外轉換。本文先全域將 *.jpg 指派給 StaticFileHandler，再在特定目錄覆寫為 FlickrProxyHttpHandler，以避免全站破圖。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3

Q8: 什麼是 FlickrNet？
- A簡: FlickrNet 是 .NET 版 Flickr API 包裝函式庫，提供上傳圖片、查詢照片資訊與取得各尺寸 URL 的方法。
- A詳: FlickrNet 封裝 Flickr REST API，簡化認證與呼叫流程。使用者需提供 API Key、Shared Secret 與授權取得的 Token，之後可呼叫 UploadPicture 上傳檔案，透過 PhotosGetInfo 取得 PhotoInfo 物件，其中包含 Medium、Large、Original 等尺寸 URL。本文利用它進行首次上傳與取得轉址目標。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q4, C-Q6

Q9: Flickr API 的 Key、Secret、Token 分別是什麼？
- A簡: Key 與 Shared Secret 由 Flickr 申請取得；Token 需使用者授權流程頒發，三者齊備後才能以 API 執行上傳等受權操作。
- A詳: API Key 是應用識別，Shared Secret 用於簽名與驗證請求完整性；Token 則是使用者授權的存取憑證，透過導流至 Flickr 登入與允許後取得。本文以 FlickrNet 示例程式協助完成授權，將三者配置於 appSettings，Handler 才能上傳與查詢照片資訊。Token 可能失效，需再授權。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q8, D-Q6

Q10: 什麼是 302 Redirect？為何本方案使用？
- A簡: 302 是暫時性轉址狀態碼，指示瀏覽器改向新 URL 載入資源。本方案用它把圖片載入改由 Flickr 伺服器負責。
- A詳: 302 表示資源暫時移動，瀏覽器會自動對 Location 標頭的目標 URL 發出新請求。由於我們希望第一次由伺服器完成上傳與紀錄，之後都交由 Flickr 提供圖片，302 是最輕量與通用的方法。它不改變原頁 HTML，也不需複雜代理串流，讓頻寬消耗落在 Flickr，一次轉址的網路開銷極小。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q9

Q11: FlickrProxy 的快取策略是什麼？
- A簡: 結合檔案快取與 ASP.NET 記憶體快取：本機 XML 檔存放 Flickr URL 與 photoID，並以 CacheDependency 對應，快速讀取且能同步失效。
- A詳: 首次上傳後，Handler 以 Hash 命名建立快取資訊檔（XML，含 src、url、photoID），同時將 Flickr URL 放入 HttpContext.Cache，設定對該檔案的 CacheDependency。後續請求先查記憶體快取，命中則直接 302；未命中則讀檔補 Cache。當快取檔更動或刪除時，記憶體快取會自動失效，保持一致性與效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q6, C-Q5

Q12: 為何要計算 Hash？用在何處？
- A簡: Hash 用於識別圖片與對應快取檔名/Key，避免重複上傳與衝突，並作為 ASP.NET Cache 的鍵值組成部分。
- A詳: Handler 以檔案內容或路徑計算 Hash，組成快取檔案名稱與記憶體快取鍵（如 flickr.proxy.[hash]）。好處是可快速判斷是否已有對應 Flickr URL 與 photoID，避免重複上傳，且在分散式或重啟後依檔案重建快取關聯。Hash 也便於檔案改變時自然導致鍵不同，觸發重新上傳與快取刷新。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q5, D-Q9

Q13: web.config 的 httpHandlers 與 location 有何作用？
- A簡: httpHandlers 決定路徑/副檔名的處理器；location 可對特定目錄覆蓋設定。兩者合用可精準指派 Handler。
- A詳: 在 system.web/httpHandlers 中註冊「誰處理哪些路徑與動詞」，例如全域 *.jpg 指向 StaticFileHandler。再用 <location path="storage"> 區塊，在該目錄覆蓋為自訂 FlickrProxyHttpHandler。這種「先全域保守，再局部覆寫」的手法，確保不影響全站並逐步導入，利於風險控制與回滾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3

Q14: 為什麼建議直接在 IIS 上開發與測試？
- A簡: Visual Studio DevWeb 與 IIS 在管線、路徑與對應行為差異大，易發生路徑解析不一致。直接用 IIS 可避免落差。
- A詳: 文中指出 DevWeb 與 IIS 在 PathInfo、對應、副檔名處理等常有差異，導致 Handler 無法命中或路徑不符。由於本案高度仰賴 IIS 對應與 ASP.NET 管線行為，開發階段就使用實際 IIS（同版）能提早暴露設定與權限問題，減少上線風險。亦便於驗證 302 行為與檔案權限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q7, C-Q1

Q15: 什麼是「延遲上傳／按需上傳」？
- A簡: 按需上傳指首次有人請求圖片時才上傳到 Flickr，避免無人觀看的檔案佔用外部資源，並平衡上線初期成本。
- A詳: 相較於發佈時即批次上傳，本文採「首次請求才上傳」：只有當圖片被讀取時，Handler 才呼叫 FlickrNet 上傳，取得 URL 後建立快取與 302 導向。優點是省去冷門圖片的外部上傳成本；缺點是首次請求會較慢。可搭配預溫策略改善熱門內容初次延遲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, C-Q10

Q16: Flickr 圖片尺寸 Medium/Large/Original 有何差異？
- A簡: 代表不同解析度與檔案大小。部分照片可能不提供某些尺寸，需檢查可用性並選擇最大可用連結。
- A詳: Flickr 會為上傳照片產生多種尺寸 URL（Medium/Large/Original 等）。但受原圖限制或處理延遲，特定尺寸可能暫不可用，出現「photo not available」。本文策略是依序嘗試 Medium→Large→Original，利用 HTTP 檢測可用性，最後保留最大可用的 URL，降低破圖風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, D-Q4

Q17: UML 序列圖在本文中的用途是什麼？
- A簡: 序列圖協助表達 Browser、Blog Server、Flickr 之間的互動順序與訊息流，清晰呈現首次與後續請求差異。
- A詳: 文中以序列圖說明兩種關鍵路徑：首次請求時，Blog Server 檢查快取→上傳 Flickr→建快取→回傳 302；後續請求則直接命中快取→302 轉 Flickr。可視化流程有助溝通設計、揭露潛在例外點（上傳失敗、URL 不可用）與快取決策位置，便於實作與除錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2

Q18: 為什麼要檢查 Flickr 圖片可用性？
- A簡: 因 Flickr 端可能回應「photo not available」或特定尺寸暫缺，必須逐一試探可用尺寸，選擇最大可用連結。
- A詳: 文中實測顯示 Flickr 偶有忙碌或尺寸尚未產生的情況，直接使用某尺寸 URL 可能拋例外或顯示不可用。解法是用 Try/Catch 逐尺寸檢查，或以 HEAD/GET 探測回應，保留最後可用的最大尺寸 URL。這可顯著降低破圖，提升穩定性與用戶體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q4

Q19: FlickrProxy 如何節省頻寬？核心價值何在？
- A簡: 首次上傳後改以 302 讓瀏覽器向 Flickr 下載圖片，網站只負擔轉址開銷。長期將圖片流量外移，減少伺服器負載。
- A詳: 在一般情境，網站需回傳完整圖片內容。採 FlickrProxy 後，首次請求雖需上傳，但後續請求僅回傳 302（體積極小），圖片資料流量由 Flickr 提供。對高流量圖片頁，能大幅降低主站頻寬、I/O 與 CPU 負載，同時沿用原有內容產製流程，價值在於低侵入、高可逆與快速見效。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q8, C-Q9

Q20: 本方案對資料可逆性與風險控制的價值是什麼？
- A簡: 變更集中於設定與單點程式，隨時可切回靜態處理；不觸碰既有資料與 HTML，降低回滾難度與營運風險。
- A詳: 所有行為透過 IIS 對應與 web.config 設定控制：全域仍可由 StaticFileHandler 處理，僅在特定子目錄套用 Handler。若出現異常，移除 location 設定即可回復；既有檔案與 HTML 未變更，不需資料轉換。再加上快取文件化，可檢查、修復或清除，讓風險可控且回復迅速。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, D-Q1

### Q&A 類別 B: 技術原理類

Q1: FlickrProxy 的整體運作流程如何？
- A簡: 攔截圖片→檢查快取→無則上傳 Flickr 並建快取→回傳 302 指向 Flickr；下次命中快取，直接 302，無須再上傳。
- A詳: 技術原理說明：IIS 對應讓 .jpg 進入 ASP.NET；Handler 先確認快取（記憶體 Cache 優先，無則讀取檔案 XML）；若無快取，執行上傳：以 FlickrNet 以 Key/Secret/Token 認證，UploadPicture 取得 photoID，PhotosGetInfo 拿尺寸 URL，逐一檢測可用性，選最大可用。寫入 XML（src/url/photoID）並以 CacheDependency 放入記憶體快取。流程步驟：攔截→快取→上傳→寫快取→302。核心組件：IIS 對應、HttpHandler、FlickrNet、ASP.NET Cache、檔案快取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q11, B-Q4

Q2: HttpHandler 在本案的執行流程為何？
- A簡: 進入 ProcessRequest 後，先確保快取目錄，檢查快取鍵與 XML 檔；若無則建檔與上傳，最後 Response.Redirect 302。
- A詳: 技術原理說明：Handler 建立快取資料夾，組成 cacheKey（含 Hash）查 HttpContext.Cache；未命中則讀取 CacheInfo XML；再不在則呼叫 BuildCacheInfoFile 完成上傳與寫檔。關鍵步驟：檔案存在檢查、記憶體快取查詢、檔案快取讀寫、Flickr 上傳、URL 檢測、302 轉址。核心組件：HttpContext、Cache、CacheDependency、XmlDocument、FlickrNet。此設計以最少 I/O 回應請求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q5, B-Q1

Q3: 快取檔案（CacheInfo XML）的結構與生成流程？
- A簡: XML 節點 proxy，含 src、url、photoID。首次上傳成功後建立，並作為記憶體快取的依賴對象。
- A詳: 技術原理說明：BuildCacheInfoFile 於上傳後建立 XmlDocument，根節點 <proxy> 設定 src（本機來源路徑）、url（Flickr 可用 URL）、photoID。關鍵步驟：計算 Hash 決定檔名、確保資料夾存在、上傳→取 info→檢測尺寸→寫 XML、Insert 記憶體 Cache 並以 CacheDependency 指向該檔。核心組件：XmlDocument、CacheDependency、FlickrNet PhotoInfo。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, C-Q6

Q4: BuildCacheInfoFile 背後機制與步驟是什麼？
- A簡: 使用 FlickrNet 載入憑證→上傳檔案取 photoID→PhotosGetInfo→檢測尺寸 URL→寫入快取 XML→回傳可用 URL。
- A詳: 技術原理說明：建立 Flickr 實例（Key/Secret）、設定 AuthToken；呼叫 UploadPicture(filePath) 得 photoID；以 PhotosGetInfo(photoID) 取得 PhotoInfo；依序 MediumUrl→LargeUrl→OriginalUrl 檢測可用性；將 src/url/photoID 寫入 XML 檔並保存；回傳選定的 Flickr URL。關鍵步驟：認證、上傳、資訊查詢、可用性檢測、持久化。核心組件：Flickr、PhotoInfo、XmlDocument。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q9, C-Q6

Q5: CheckFlickrUrlAvailability 的機制是什麼？
- A簡: 以程式對候選 URL 進行實際 HTTP 檢測（HEAD/GET），遇例外則跳出，保留上一個成功的最大尺寸網址。
- A詳: 技術原理說明：對 PhotoInfo 的尺寸屬性取 URL，逐一傳入可用性檢測方法。檢測可用時回傳該 URL，否則丟出例外促使跳出序列，保留最後成功者。關鍵步驟：嘗試順序、HTTP 連線測試、例外處理、回傳策略。核心組件：HttpWebRequest/HttpClient（或 FlickrNet 提供例外）、Try/Catch。此策略緩解 Flickr 偶發尺寸不可用問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, A-Q18, D-Q4

Q6: ASP.NET Cache 與 CacheDependency 如何協作？
- A簡: 將 Flickr URL 以鍵存入記憶體快取，並以 CacheDependency 綁定 XML 檔；當檔案變更，記憶體快取自動失效。
- A詳: 技術原理說明：context.Cache.Insert(key, value, new CacheDependency(filePath)) 可建立記憶體快取與檔案關聯。當快取檔被更新或刪除，依賴關係觸發使對應的記憶體項目自動移除。關鍵步驟：產生 key、讀/寫 XML、Insert Cache、命中優先。核心組件：System.Web.Caching.Cache、CacheDependency、檔案系統。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q5

Q7: IIS 檔案對應與 ASP.NET 接管流程如何設計？
- A簡: 先於 IIS 將 .jpg 對應 ASP.NET；web.config 全域以 StaticFileHandler；再用 location 在特定目錄覆寫為自訂 Handler。
- A詳: 技術原理說明：IIS「應用程式對應」把 .jpg 交給 aspnet_isapi.dll；ASP.NET 依 httpHandlers 決定處理器。關鍵步驟：IIS 對應設定→web.config 全域處理→location 局部覆蓋。核心組件：IIS 對應、aspnet_isapi.dll、httpHandlers、location。此分層配置避免全站破圖，並讓導入範圍可控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q1, C-Q2, C-Q3

Q8: 302 轉址後瀏覽器的行為與效益是什麼？
- A簡: 瀏覽器遵循 Location 對新 URL 發送請求，圖檔由 Flickr 提供；網站僅負擔小型 302 回應，顯著節省頻寬。
- A詳: 技術原理說明：瀏覽器收到 302 會自動請求 Location 指向的 Flickr 圖片，快取政策也以 Flickr 響應為準。關鍵步驟：初次上傳後回應 302→第二次直接 302→瀏覽器取圖。核心組件：HTTP 狀態碼、Location 標頭、瀏覽器。效益是降低主站 I/O 與流量，並由 Flickr 全球基礎設施提供圖片。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q19, C-Q9

Q9: Flickr 認證流程與 Token 取得的原理？
- A簡: Key/Secret 標識應用並簽名；使用者在 Flickr 授權後頒發 Token。Token 存入設定檔供伺服器端受權操作。
- A詳: 技術原理說明：Flickr 採 OAuth 式授權概念（FlickrNet 封裝），應用以 Key/Secret 構造請求，引導使用者登入 Flickr 同意授權，取得 Token 後才能上傳、刪除等受權動作。關鍵步驟：申請 Key/Secret→跑示例授權→保存 Token。核心組件：FlickrNet 認證 API、appSettings。Token 可能過期，需要重新授權。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q8, D-Q6

Q10: 本案的錯誤處理與降級策略是什麼？
- A簡: 以 Try/Catch 包覆尺寸檢測與 URL 取得，保留最後可用；設定層面可隨時改回 StaticFileHandler，迅速回退。
- A詳: 技術原理說明：對 PhotoInfo 尺寸屬性與 HTTP 檢測採例外控制，確保至少選到能用的 URL；若快取缺失或上傳失敗，可回應本地靜態或暫時停用目錄覆寫。關鍵步驟：例外攔截、可用性回退、設定回滾。核心組件：Try/Catch、web.config location、StaticFileHandler。此策略降低線上中斷風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q4, C-Q2

### Q&A 類別 C: 實作應用類

Q1: 如何在 IIS 設定讓 .JPG 交由 ASP.NET 處理？
- A簡: 於 IIS 應用程式對應將 .jpg 指向 aspnet_isapi.dll，使請求進入 ASP.NET 管線，便能被 HttpHandler 接手處理。
- A詳: 具體實作步驟：1) 開啟 IIS 管理，編輯站台的「對應」或「處理常式對應」；2) 新增或編輯 .jpg 副檔名，對應至 aspnet_isapi.dll（經典）或啟用整合管線的 managed handler；3) 套用。關鍵程式碼片段或設定：IIS 端操作，無需程式碼。注意事項：此變更會讓所有 .jpg 進入 ASP.NET，請配合 web.config 全域設為 StaticFileHandler，避免全站破圖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q2

Q2: 如何用 web.config 將預設 .JPG 還原為靜態處理？
- A簡: 在 system.web/httpHandlers 指定 *.jpg 使用 System.Web.StaticFileHandler，維持與 IIS 相同的靜態回傳行為。
- A詳: 具體實作步驟：在 web.config 加入以下設定。程式碼片段： 
  <httpHandlers>
    <add path="*.jpg" verb="*" type="System.Web.StaticFileHandler" />
  </httpHandlers>
注意事項與最佳實踐：先全域套用 StaticFileHandler，確保不影響既有頁面，之後再局部覆寫特定目錄為自訂 Handler，能逐步導入與快速回滾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q3

Q3: 如何在特定目錄改用自訂 FlickrProxyHttpHandler？
- A簡: 透過 <location path="storage"> 覆寫 httpHandlers，將 *.jpg 指向自訂 Handler，僅影響該目錄與子目錄。
- A詳: 具體實作步驟：在 web.config 加入： 
  <location path="storage">
    <system.web>
      <httpHandlers>
        <add path="*.jpg" verb="*" type="ChickenHouse.Web.HttpHandlers.FlickrProxyHttpHandler,App_Code" />
      </httpHandlers>
    </system.web>
  </location>
關鍵設定：type 指向 Handler 聯編。注意事項：可改放至子目錄 web.config；確認路徑大小寫與程式集定位正確。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q2, C-Q4

Q4: 如何撰寫 FlickrProxyHttpHandler 主程式骨架？
- A簡: 在 ProcessRequest 建立快取資料夾→查記憶體快取→讀/建 XML 檔→取得 Flickr URL→Response.Redirect 302。
- A詳: 具體實作步驟：1) 確保快取目錄存在；2) 以 Hash 組 key 查 context.Cache；3) 未命中則載入或建立快取 XML；4) 取得 Flickr URL 後 Redirect。關鍵程式碼片段：
  if (!File.Exists(CacheInfoFile)) flickrURL = BuildCacheInfoFile(ctx);
  else { load XML or cache.Insert(key, url, new CacheDependency(CacheInfoFile)); }
  ctx.Response.Redirect(flickrURL);
注意事項：避免多執行緒競態；Redirect 使用相對應狀態碼（預設 302）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q5, C-Q6

Q5: 如何實作快取檢查與 CacheDependency？
- A簡: 以 Hash 產生 cacheKey，讀取 XML 的 url，並以 CacheDependency 監控 XML 檔變動，命中則直接 302。
- A詳: 具體實作步驟：1) var key = "flickr.proxy." + GetFileHash(); 2) var url = context.Cache[key] as string; 3) 若 null，載入 XML 取 url 並插入 Cache，附加 CacheDependency(CacheInfoFile)；4) Redirect(url)。關鍵程式碼：
  context.Cache.Insert(key, url, new CacheDependency(CacheInfoFile));
注意事項：確保 XML 結構正確；Cache 容量與過期策略需評估；檔案 I/O 需處理例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q6, A-Q11

Q6: 如何實作 BuildCacheInfoFile 與上傳 Flickr？
- A簡: 用 FlickrNet 以 Key/Secret/Token 認證→UploadPicture→PhotosGetInfo→檢測可用尺寸→寫入 XML→回傳 URL。
- A詳: 具體實作步驟與關鍵程式碼：
  var flickr = new Flickr(key, secret); flickr.AuthToken = token;
  var photoID = flickr.UploadPicture(FileLocation);
  var pi = flickr.PhotosGetInfo(photoID);
  var url = TryPick(pi.MediumUrl, pi.LargeUrl, pi.OriginalUrl);
  var x = new XmlDocument(); x.LoadXml("<proxy/>");
  x.DocumentElement.SetAttribute("src", FileLocation);
  x.DocumentElement.SetAttribute("url", url);
  x.DocumentElement.SetAttribute("photoID", photoID);
  x.Save(CacheInfoFile); return url;
注意事項：處理例外；確保 API 憑證安全；檔案路徑權限要足夠。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, C-Q8

Q7: 如何實作圖片 URL 可用性檢查方法？
- A簡: 以 HEAD/GET 連線檢測 200 回應視為可用；序列嘗試多尺寸，遇例外或非 2xx 即跳過，保留最後成功者。
- A詳: 具體實作步驟：1) 定義 Check(url)：發送 HEAD（無則 GET range）檢查狀態碼；2) 依序檢查 medium/large/original；3) 第一個失敗觸發例外則保留上個成功 URL。範例（C# 概念）： 
  HttpWebRequest r = (HttpWebRequest)WebRequest.Create(u); r.Method="HEAD";
  using(var resp=(HttpWebResponse)r.GetResponse()) return resp.StatusCode==HttpStatusCode.OK;
注意事項：設定逾時；處理 429/5xx 重試；避免同步阻塞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q4

Q8: 如何設定 appSettings 中的 API Key/Secret/Token？
- A簡: 在 web.config appSettings 增加三項設定並安全存放，於程式讀取後指派給 FlickrNet 實例與 AuthToken。
- A詳: 具體實作步驟：在 web.config：
  <appSettings>
    <add key="flickrProxy.API.key" value="YOUR_KEY"/>
    <add key="flickrProxy.API.security" value="YOUR_SECRET"/>
    <add key="flickrProxy.API.token" value="YOUR_TOKEN"/>
  </appSettings>
程式讀取：ConfigurationManager.AppSettings["..."]。注意事項：避免將敏感資料入庫版；建議以機密保護（如加密 configSection、環境變數或外部祕密管理）；Token 失效需重新授權。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q9, D-Q6

Q9: 如何用 Fiddler 驗證 302 轉址與 Flickr 下載？
- A簡: 以瀏覽器載入含圖片頁，於 Fiddler 觀察 .jpg 請求收到 302，後續請求轉向 flickr.com，確認圖片來自 Flickr。
- A詳: 具體實作步驟：1) 啟動 Fiddler；2) 瀏覽測試頁；3) 找到對 storage/*.jpg 的請求，狀態應為 302，Location 指向 Flickr URL；4) 觀察緊接著的 Flickr 請求為 200 並有圖片內容；5) 首次會見到上傳前的延遲。注意事項：清瀏覽器快取以重現流程；檢查是否有重複 302 或循環。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q8

Q10: 如何在部署與回滾時維持可逆性？
- A簡: 採「全域靜態、區域覆寫」配置；問題時移除 location 區塊或降回 StaticFileHandler，立即回復原站行為。
- A詳: 具體實作步驟：1) 先上線 web.config 全域 *.jpg→StaticFileHandler；2) 針對目錄新增 location 指向 FlickrProxy；3) 發生異常時移除或註解該 location；4) 保留快取檔與設定版控。注意事項：使用分階段發布、功能旗標；維持快取資料夾權限設定；提供監控指標（302 命中率、上傳失敗率）決定是否回滾。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q20, B-Q10, D-Q1

### Q&A 類別 D: 問題解決類

Q1: 全站 .JPG 破圖怎麼辦？
- A簡: 可能是 IIS 對應進入 ASP.NET 後未指定 StaticFileHandler。先全域還原為靜態，再局部覆寫特定目錄。
- A詳: 問題症狀：所有 .jpg 都無法顯示。可能原因：IIS 對應導入 ASP.NET，但 web.config 未設定 *.jpg→StaticFileHandler，或自訂 Handler 套用到整站。解決步驟：1) 在 system.web/httpHandlers 加入 StaticFileHandler；2) 僅在目錄用 location 覆寫；3) 檢查 type 名稱與組件指向。預防措施：先灰度導入；設定版管與回滾流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, B-Q7

Q2: 500 錯誤顯示無法建立 CacheInfo 檔怎麼辦？
- A簡: 多半是快取資料夾不存在或無寫入權限。建立資料夾並賦予應用程式帳號寫入權限。
- A詳: 問題症狀：首次請求拋例外，Server Error。原因分析：Directory 不存在、IIS 應用程式池帳號無權限、磁碟路徑錯誤。解決步驟：1) 在配置中指定快取路徑；2) 建立資料夾；3) 設定 NTFS 權限（IIS AppPool Identity 可寫）；4) 例外日誌確認。預防措施：部署腳本自動建立與驗證權限；加入開機自檢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, C-Q5

Q3: 第一次請求延遲很長如何優化？
- A簡: 首次需上傳 Flickr 與建快取，可用預溫熱門圖片、背景批次上傳、非同步處理與逾時/重試控制。
- A詳: 症狀：首訪圖片載入慢。原因：上傳與 PhotosGetInfo 網路延遲。解法：1) 發佈後預先觸發熱門圖；2) 背景作業批次上傳並預建快取；3) Handler 中非同步檢測尺寸；4) 合理逾時與重試；5) 對小圖或低流量路徑設門檻不上傳。預防：建立熱度模型，分層處理策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q10

Q4: 出現「photo not available」導致圖片不顯示怎麼辦？
- A簡: 對各尺寸逐一檢測可用性，保留最大可用 URL；必要時重試或暫用較小尺寸，避免破圖。
- A詳: 症狀：Flickr 有時回應不可用。原因：處理延遲、尺寸未生成、服務忙碌。解決步驟：1) 在 Handler 依序測試 Medium→Large→Original；2) HEAD/GET 檢測 200 才採用；3) 設定重試與回退；4) 寫入快取避免重複測。預防：加入延時再查策略；監控 Flickr 可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q7, A-Q16

Q5: 302 轉址陷入循環怎麼辦？
- A簡: 檢查 Redirect 目標是否錯指回本站而非 Flickr；正確填入 Flickr URL，避免相對路徑或代理誤配。
- A詳: 症狀：連續多次 302，最終失敗。原因：快取 XML url 寫錯、環境變數影響組 URL、反向代理重寫。解決步驟：1) 檢視快取 XML 的 url 值；2) Fiddler 檢查 Location；3) 修正為 Flickr 的絕對 URL；4) 清除錯誤快取。預防：以 FlickrNet 回傳的 URL，不自行組字串；加入 URL 格式驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, C-Q9

Q6: FlickrNet 認證失敗無法上傳怎麼排查？
- A簡: 驗證 Key/Secret/Token 是否正確與有效；Token 可能過期，需重新授權並更新設定。
- A詳: 症狀：上傳拋授權相關例外。原因：Key/Secret 錯誤、Token 失效或未授權範圍。解決步驟：1) 重新比對 appSettings；2) 以示例工具重跑授權流程取得 Token；3) 檢查伺服器時間同步；4) 觀察 API 回應碼。預防：祕密管理與輪換策略；監控上傳失敗率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q8, B-Q9

Q7: DevWeb 正常、IIS 失敗（404/路徑錯誤）怎麼辦？
- A簡: DevWeb 與 IIS 管線與 PathInfo 不同。改用 IIS 開發，檢查 Handler 對應、實體路徑與大小寫，調整程式。
- A詳: 症狀：部署 IIS 後 Handler 不生效或找不到檔案。原因：路徑解析差異、對應規則不同。解決步驟：1) 直接在 IIS 建測試站；2) 確認 .jpg 對應 ASP.NET 與 httpHandlers 設定；3) 使用 Server.MapPath 防呆；4) 檢查位於子應用程式時的 web.config 繼承。預防：一開始即用 IIS 測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q1, C-Q3

Q8: 首次高併發造成重複上傳怎麼避免？
- A簡: 對相同資源加鎖或使用檔案鎖與原子檢查；建立快取檔前再次確認，避免競態。
- A詳: 症狀：多個同圖請求同時到達，產生多次上傳。原因：缺少臨界區保護。解決步驟：1) 以字典+lock 針對 hash 加鎖；2) 建檔前 File.Exists 再檢查；3) 使用互斥鎖/命名 Mutex。預防：加入去重機制與延遲合併；監控上傳次數與 photoID 重複率。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q4, C-Q5, A-Q12

Q9: 快取失效導致每次都重傳怎麼辦？
- A簡: 檢查快取鍵與 Hash 設計、CacheDependency 與 XML 路徑是否穩定；避免每次產生不同鍵或誤判變更。
- A詳: 症狀：重複上傳、無命中記憶體快取。原因：Hash 來源不穩（含時序）、快取檔路徑不同、依賴檔被頻繁變動。解決步驟：1) 以檔案內容或規範化路徑算 Hash；2) 固定快取目錄；3) 僅在必要時更新 XML；4) 檢查 Cache.Insert 的依賴設定。預防：單元測試鍵生成；日誌追蹤快取命中。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, C-Q5

Q10: 如何控制哪些圖片不上傳（尺寸/大小門檻）？
- A簡: 在 Handler 加條件判斷檔案大小、目錄或命名規則，未達門檻者直接由 StaticFileHandler 回應。
- A詳: 症狀：小圖不需外移卻被上傳。原因：缺少條件控管。解決：1) 在流程第一步檢查 FileInfo.Length、Path 或標記；2) 不符合者 return 靜態回應；3) 對特殊目錄全禁用。預防：以設定檔管理白/黑名單；記錄門檻命中率以調整策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q4, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 FlickrProxy？
    - A-Q2: FlickrProxy 的核心目標是什麼？
    - A-Q3: 為什麼選擇 HttpHandler 而非修改 HTML？
    - A-Q4: 什麼是 ASP.NET HttpHandler？
    - A-Q5: IIS 與 ASP.NET 在處理靜態檔案的關係是什麼？
    - A-Q7: System.Web.StaticFileHandler 是什麼？
    - A-Q8: 什麼是 FlickrNet？
    - A-Q9: Flickr API 的 Key、Secret、Token 分別是什麼？
    - A-Q10: 什麼是 302 Redirect？為何本方案使用？
    - A-Q14: 為什麼建議直接在 IIS 上開發與測試？
    - A-Q16: Flickr 圖片尺寸 Medium/Large/Original 有何差異？
    - B-Q8: 302 轉址後瀏覽器的行為與效益是什麼？
    - C-Q2: 如何用 web.config 將預設 .JPG 還原為靜態處理？
    - C-Q3: 如何在特定目錄改用自訂 FlickrProxyHttpHandler？
    - C-Q9: 如何用 Fiddler 驗證 302 轉址與 Flickr 下載？

- 中級者：建議學習哪 20 題
    - B-Q1: FlickrProxy 的整體運作流程如何？
    - B-Q2: HttpHandler 在本案的執行流程為何？
    - A-Q11: FlickrProxy 的快取策略是什麼？
    - A-Q12: 為何要計算 Hash？用在何處？
    - B-Q3: 快取檔案的結構與生成流程？
    - B-Q4: BuildCacheInfoFile 背後機制與步驟是什麼？
    - B-Q5: CheckFlickrUrlAvailability 的機制是什麼？
    - B-Q6: ASP.NET Cache 與 CacheDependency 如何協作？
    - B-Q7: IIS 檔案對應與 ASP.NET 接管流程如何設計？
    - C-Q4: 如何撰寫 FlickrProxyHttpHandler 主程式骨架？
    - C-Q5: 如何實作快取檢查與 CacheDependency？
    - C-Q6: 如何實作 BuildCacheInfoFile 與上傳 Flickr？
    - C-Q7: 如何實作圖片 URL 可用性檢查方法？
    - C-Q8: 如何設定 appSettings 中的 API Key/Secret/Token？
    - D-Q1: 全站 .JPG 破圖怎麼辦？
    - D-Q2: 500 錯誤顯示無法建立 CacheInfo 檔怎麼辦？
    - D-Q4: 出現「photo not available」導致圖片不顯示怎麼辦？
    - D-Q5: 302 轉址陷入循環怎麼辦？
    - D-Q6: FlickrNet 認證失敗無法上傳怎麼排查？
    - D-Q7: DevWeb 正常、IIS 失敗（404/路徑錯誤）怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q15: 什麼是「延遲上傳／按需上傳」？
    - A-Q19: FlickrProxy 如何節省頻寬？核心價值何在？
    - A-Q20: 本方案對資料可逆性與風險控制的價值是什麼？
    - B-Q10: 本案的錯誤處理與降級策略是什麼？
    - C-Q10: 如何在部署與回滾時維持可逆性？
    - D-Q3: 第一次請求延遲很長如何優化？
    - D-Q8: 首次高併發造成重複上傳怎麼避免？
    - D-Q9: 快取失效導致每次都重傳怎麼辦？
    - D-Q10: 如何控制哪些圖片不上傳（尺寸/大小門檻）？
    - B-Q1: FlickrProxy 的整體運作流程如何？
    - B-Q5: CheckFlickrUrlAvailability 的機制是什麼？
    - B-Q7: IIS 檔案對應與 ASP.NET 接管流程如何設計？
    - C-Q4: 如何撰寫 FlickrProxyHttpHandler 主程式骨架？
    - C-Q6: 如何實作 BuildCacheInfoFile 與上傳 Flickr？
    - C-Q7: 如何實作圖片 URL 可用性檢查方法？