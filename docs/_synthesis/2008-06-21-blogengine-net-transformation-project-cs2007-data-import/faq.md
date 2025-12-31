---
layout: synthesis
title: "[BlogEngine.NET] 改造工程 - CS2007 資料匯入"
synthesis_type: faq
source_post: /2008/06/21/blogengine-net-transformation-project-cs2007-data-import/
redirect_from:
  - /2008/06/21/blogengine-net-transformation-project-cs2007-data-import/faq/
postid: 2008-06-21-blogengine-net-transformation-project-cs2007-data-import
---

# [BlogEngine.NET] 改造工程 - CS2007 資料匯入

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 BlogEngine.NET？
- A簡: BlogEngine.NET 是基於 ASP.NET 的開源部落格引擎，內建文章、留言、檔案處理與擴充機制。
- A詳: BlogEngine.NET 是一套以 ASP.NET/C# 開發的輕量開源部落格系統，提供文章與留言管理、檔案/圖片透過 HttpHandler 提供、Slug 友善網址、Widget/Theme 擴充等功能。相較於大型平台，它架構單純、程式庫易讀，便於客製化與二次開發。本案例選擇它作為從 CS2007 遷移的目標，因匯入 API 清晰、可自建匯入流程，降低維護負擔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q9, B-Q3

A-Q2: 什麼是 Community Server 2007（CS2007）？
- A簡: CS2007 是整合部落格、論壇、相簿的社群平台，資料模型與屬性序列化較複雜。
- A詳: Community Server 2007 是 Telligent 推出的社群整合平台，含部落格、論壇、相簿等功能。其部落格資料結構複雜，部分欄位採 PropertyNames/PropertyValues 串接的序列化方式存放，增加移轉解析難度。網址多樣且大量依賴 URL Rewrite。本案從 CS2007 轉至 BlogEngine.NET，需處理舊 PostID、留言屬性、內外部連結與計數等資訊還原。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q4, D-Q2

A-Q3: 什麼是 BlogML？用途為何？
- A簡: BlogML 是部落格資料交換的 XML 格式，用於文章、留言等跨系統匯入匯出。
- A詳: BlogML（Blog Markup Language）是一種標準化的 XML 架構，用於在不同部落格平台間交換內容，涵蓋文章、分類、留言、附件等。其優點是中立且結構化，工具支援多；限制是平台特有的欄位（如 CS2007 的匿名留言 IP、某些計數）可能未涵蓋，需透過自訂流程或擴充欄位補齊。本案先以 BlogML 完成約九成，剩餘以自製匯入器補足。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q1, D-Q1

A-Q4: 為什麼從 CS2007 遷移到 BlogEngine.NET？
- A簡: 因維護與客製成本、效能與單純性考量，轉到易擴充的 BlogEngine.NET。
- A詳: 遷移動機包含：1) 架構單純，二次開發負擔較小；2) 核心程式易讀，能快速客製匯入器與處理流程；3) 可用 Slug 與 HttpHandler 提供友善網址與檔案服務；4) 降低依賴複雜 URL Rewrite 規則；5) 以 BlogML 結合自製工具能完整帶出資料。相對於 CS2007，BlogEngine 更符合輕量、可控、易維護的目標。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q9, B-Q13

A-Q5: 匯入（Import）與遷移（Migration）的差異？
- A簡: 匯入是搬內容；遷移還包括識別、轉換與連結修補與重導等系統性變更。
- A詳: 匯入指將文章、留言等資料載入新系統，著重資料到位。遷移則更全面，包含：欄位對映與轉換、舊新 ID 對照表建立、內外部連結重寫、媒體路徑改制、計數與日期校正、SEO 與重導策略等。本案先以 BlogML 匯入，再加上 Regex 修正、HttpHandler 重導與屬性解析，形成完整遷移流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q5, D-Q8

A-Q6: 什麼是 PostID？為何要保留舊 ID？
- A簡: PostID 是舊系統文章識別碼；保留可建立新舊對照，支援重導與連結修補。
- A詳: 在 CS2007 中，PostID 為整數型識別碼，存在於多種網址形式。遷移後 BlogEngine 使用 GUID 與 Slug，因此需保留舊 PostID 與新 GUID 的對照關係。用途包括：1) 修正站內舊連結；2) 建立 CSUrlMap 進行 301/重導；3) 供外站舊連結正確跳轉；4) 事後稽核與問題追蹤。對照表是遷移成功的關鍵工件。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q6, D-Q9

A-Q7: 什麼是 Slug？與 PostID 有何差異？
- A簡: Slug 是基於標題的友善網址片段；PostID 是數值或 GUID 識別，兩者用途不同。
- A詳: Slug 是文章標題經格式化後的 URL 片段，如 /post/my-title.aspx，利於閱讀與 SEO。BlogEngine 會以文章屬性產生 Slug。PostID 則是資料庫層的唯一識別，CS 用整數，BlogEngine 用 GUID。遷移時以 PostID 對應新 GUID，再由新系統產生 Slug，內部與外部連結需視情境以 GUID 或 Slug URL 建立。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q5, D-Q8

A-Q8: 什麼是 PageViewCount？為何需要匯入？
- A簡: PageViewCount 為文章瀏覽次數；匯入可保持歷史指標與熱門文章排序。
- A詳: PageViewCount 反映文章歷史熱度與讀者行為，常用於熱門文章模組與營運分析。若遷移忽略此欄位，排行榜、熱門排序與長期成效分析會失準。本案以自製匯入器補齊 BlogML 未涵蓋的計數，將舊值帶入新系統，維持體驗與資料連續性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q1, D-Q10

A-Q9: 什麼是 HttpHandler（.ashx）？與 WebService（.asmx）差異？
- A簡: HttpHandler 處理特定路徑請求，輕量高效；WebService 提供遠端方法呼叫。
- A詳: HttpHandler 是 ASP.NET 管線中的末端處理元件，負責回應特定路徑，如 image.axd。其優點是輕量、無頁面生命週期負擔、適合檔案與重導。WebService 則提供 SOAP 風格的遠端方法呼叫，序列化開銷較大，逐筆呼叫效率較差。本案以 ASHX 批次匯入取代 asmx 逐篇匯入，加速與掌控流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q12, C-Q1

A-Q10: 什麼是兩階段（2-pass）匯入？為何需要？
- A簡: 先匯入內容與建對照，再依新 ID 回填站內連結；因新網址須待匯入後生成。
- A詳: 兩階段策略是先將文章與留言匯入，建立舊 PostID 與新 GUID 的對照，第二階段再以對照表修補內容中的站內連結。因為新系統在匯入後才知道實際 GUID/Slug，故一次無法精準替換。此法將不可避免的依賴分離，確保連結修補準確並可重複執行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5, D-Q4

A-Q11: 什麼是 CS2007 的 PropertyNames/PropertyValues 格式？
- A簡: 以 Name:Type:Start:End 片段描述屬性，值集中存於 PropertyValues 字串。
- A詳: CS2007 將多個屬性壓縮於兩欄：PropertyNames 保存多組「名稱:型別:起:訖」片段，PropertyValues 存放串接的值。解析需讀取每個片段，依起訖位置從值字串擷取，如 SubmittedUserName 與 TitleUrl。此序列化節省欄位但解析複雜，是匯入匿名留言資訊的關鍵難點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, D-Q2

A-Q12: 什麼是內部連結與外部連結修正？
- A簡: 內部連結改指新站文章；外部連結透過重導接住舊網址以保 SEO 與體驗。
- A詳: 內部連結指文內指向本站其他文章或資源的 URL，需改為 BlogEngine 的 GUID/Slug 型式；外部連結指其他網站連到舊 CS 網址，無法修改對方內容，需在新站撰寫 HttpHandler，攔截 /blogs/*.aspx 形式，解析舊 PostID，查表後 301/轉送至新網址，維持 SEO 與使用者路徑連續。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q7, D-Q8

A-Q13: 什麼是 URL Rewrite？在兩系統中的角色？
- A簡: Rewrite 改寫請求到實際資源；CS 依賴度高，BlogEngine 較多用 Handler。
- A詳: URL Rewrite 將友善網址映射到實際處理程式或檔案。CS2007 大量以規則管理眾多網格式樣；BlogEngine 傾向用 HttpHandler（如 file.axd、image.axd）與 Slug 生成簡化配置。遷移時需理解舊規則以擷取 PostID 與比對對照表，新站側以 Handler 還原對應與重導，降低規則複雜度。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q9, C-Q7

A-Q14: 為什麼用正規表示式（Regex）改寫連結？
- A簡: Regex 精準匹配多種舊網址樣式，安全替換必要區段，避免誤傷其他內容。
- A詳: 舊站存在多網域、多年代與手工撰寫的多樣連結格式。用純文字取代易誤判。透過 Regex 可定義可選網域、目錄與檔名規則，僅匹配所需段落，擷取 PostID 或路徑再重寫。例如：(http://(columns|community).*)?/blogs/chicken/... 的設計有效涵蓋分家前後網域，且保留 RSS 等特殊路徑排除。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q7, C-Q4

A-Q15: Server.Transfer 與 Redirect 差異？遷移時如何取捨？
- A簡: Transfer 伺服器內部換頁不改網址；Redirect 告知瀏覽器跳轉，適合 SEO。
- A詳: Server.Transfer 在伺服器端切換處理頁，效能佳但瀏覽器網址不變，適合內部流程控制與顯示提示頁。Redirect（含 301/302）回應客戶端，更新網址並傳達永久/暫時重導語意，有利 SEO 與外部鏈接更新。本案在 CSUrlMap 中以 Server.Transfer 移交至說明頁，再由頁面決定是否使用 301 導向新文章。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q7, D-Q8

### Q&A 類別 B: 技術原理類

B-Q1: BlogEngine 的 BlogImporter.asmx 如何運作？
- A簡: 以 WebMethod 逐篇文章與留言呼叫寫入，序列化 BlogML 片段，效率較低。
- A詳: BlogImporter.asmx 暴露少量 WebMethod，每次呼叫處理一篇文章或一則留言，伺服器端使用 BlogEngine.Core API 新增資料。流程包含 SOAP 序列化、驗證、寫入與回應。優點是遠端可用、邏輯清楚；缺點是往返成本高、欄位覆蓋有限。本案以其程式碼為範本，改以 ASHX 批次處理，繞過逐筆呼叫瓶頸。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q9, C-Q1

B-Q2: 自製 ASHX 匯入器的執行流程為何？
- A簡: 於 App_Data 讀入 BlogML，雙迴圈走文章與留言，寫入並記錄 ID 對照。
- A詳: ASHX 啟動時讀取預先放在 ~/App_Data 的 BlogML，解析後：1) 迴圈處理每篇文章，建立 BlogEngine 文章物件，寫入並取得 GUID；2) 內層迴圈處理留言，補上匿名作者資訊；3) 同步 PageViewCount 與 Modified Date 修正；4) 寫入舊 PostID 與新 GUID 對照；5) 產生報告供第二階段連結修補。整體在伺服器端一次完成，效率高。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q8, C-Q1

B-Q3: BlogEngine 圖片與檔案下載的 HttpHandler 機制是什麼？
- A簡: 透過 image.axd、file.axd 處理資源請求，集中控管與權限、路徑抽象化。
- A詳: BlogEngine 在 web.config 註冊 image.axd、file.axd，由對應的 HttpHandler 接管 *.axd 請求，解析查詢參數（如 picture 路徑），從存放區讀取檔案後輸出。好處是資源路徑可抽象、可控權限與快取策略，遷移時可將原絕對圖檔連結改寫為 image.axd?picture=...，無需暴露實體路徑，便於跨站搬遷與整併。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q4, D-Q3

B-Q4: CS2007 屬性序列化的解析機制為何？
- A簡: 以 PropertyNames 片段描述區段，依起訖索引從 PropertyValues 切出值。
- A詳: PropertyNames 由多組「名稱:型別:起:訖」構成，型別如 S 代表字串。解析流程：1) 將 PropertyNames 以分隔符號切分；2) 逐組讀出起訖索引；3) 對 PropertyValues 作 Substring 拿到實際值；4) 映射到物件屬性。此設計讓資料庫 schema 簡化，但解析需自寫程式，特別對匿名留言的 SubmittedUserName、TitleUrl、IP 等欄位尤為關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, D-Q2

B-Q5: 使用 SQL Server FOR XML 輸出資料的原理？
- A簡: FOR XML 將查詢結果序列化為 XML，模式如 AUTO/RAW，便於後續處理。
- A詳: SQL Server 的 FOR XML 子句能把 SELECT 結果轉為 XML。以 AUTO 模式會依表別名產生元素，欄位為屬性。本案以「select ... from cs_posts where ApplicationPostType=4 for xml auto」輸出留言屬性，再加上根節點存檔，供後續程式離線解析。此法快速、免寫連線程式碼，適合一次性資料萃取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q3, D-Q1

B-Q6: 內部連結識別的 Regex 設計思路？
- A簡: 鎖定可選網域與固定目錄，擷取最後的 PostID，避免誤傷 RSS 與特殊頁。
- A詳: 內部連結格式眾多，核心是萃取 PostID。Regex 需：1) 支援可選網域（columns/community）；2) 指定/blogs/chicken/archive/年月日層級；3) 擷取最後數字為 PostID；4) 避免匹配 rss.aspx。示例：(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/archive/\d+/\d+/\d+/(\d+)\.aspx。以群組擷取 ID 供對照替換。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, C-Q5, D-Q5

B-Q7: 影像連結 Regex 設計與網域覆蓋策略？
- A簡: 使用可選網域與目錄固定前綴，群組擷取尾端相對路徑，統一改為 image.axd。
- A詳: 舊圖檔有分家前後網域與相對路徑版本，Regex 設計：(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/([a-zA-Z0-9\-_\./%]* )，群組3取得實體路徑，重寫為 image.axd?picture=$3。需排除 rss.aspx 等保留頁，並依序處理（先完整網域，再相對路徑）避免重疊替換。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, C-Q4, D-Q3

B-Q8: 新舊 ID 對照表如何建立與運作？
- A簡: 匯入時記錄 CS PostID 與新 GUID，持久化供連結修補與重導查詢。
- A詳: 在寫入新文章時，同步取得 BlogEngine 產生的 GUID，與來源的整數 PostID 組成鍵值對，儲存於資料表/檔案（如 XML/JSON/DB）。第二階段替換內部連結與重導 Handler 依此查詢新網址。設計要點：唯一性約束、完整性報表、查無對應時的降級策略（如導首頁並提示）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q6, D-Q9

B-Q9: CSUrlMap HttpHandler 如何攔截與重導？
- A簡: 以 Regex 判定請求類型，擷取 PostID，查對照表後設定目標並轉送/重導。
- A詳: Handler 在 web.config 註冊攔截 /blogs/*.aspx 與 RSS。流程：1) 若是 RSS 路徑，直接輸出新 RSS；2) 若匹配含 PostID 的舊文章 URL，擷取 PostID，查表得新 GUID，將 postID 與提示寫入 context.Items；3) 若匹配舊 Slug URL，直接映射；4) 未命中則提示回首頁；最後 Server.Transfer 至 AutoRedirFromCsUrl.aspx，統一處理訊息與可能的 301。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q10, C-Q7

B-Q10: Server.Transfer 為何適合此重導流程？
- A簡: 可攜帶 context.Items 與狀態，減少往返；再由頁面決策 301 或顯示說明。
- A詳: 直接 Response.Redirect 雖簡單，但難以攜帶額外描述與統一樣板頁。以 Server.Transfer 將控制權交給 ASPX 頁，能在同一請求中讀取 context.Items 的 postID 與訊息，決定是否做 301/302 或呈現友善提示，減少重導跳動並利於記錄統計。此模式兼顧 UX 與 SEO 的可控性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, C-Q7, D-Q8

B-Q11: BlogEngine 文章 URL 結構與 Slug 生成機制？
- A簡: 支援 GUID 查詢參數與 Slug 友善網址；Slug 多由標題正規化生成。
- A詳: BlogEngine 預設提供兩種文章網址：/post.aspx?id=GUID 與 /post/slug.aspx。Slug 由標題轉小寫、移除特殊字元、以連字號連接產生。匯入時可先用 GUID 型式建立連結，再待 Slug 確認後轉用友善型，或直接由 API 取得 Slug。理解兩者關係有助於連結修補與外部重導策略設計。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q5, D-Q8

B-Q12: Web 應用管線中 HttpHandler 的角色與順序？
- A簡: Handler 是請求終結者；在模組與路由後接手，輸出回應或再轉移。
- A詳: ASP.NET 請求經過 HTTP Modules（驗證、Rewrite、記錄等）後，由對應的 HttpHandler 處理實際內容輸出。Handler 適合靜態/動態檔案輸出、API、重導器。本案的 image.axd、file.axd 與 CSUrlMap 皆屬此層。理解其生命週期可正確安排 Regex 判斷、權限、快取與 Transfer/Redirect 行為。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, B-Q3, B-Q9

B-Q13: 為何 WebService 逐篇匯入效能較差？瓶頸在哪？
- A簡: 多次網路往返與序列化成本高；每篇一呼叫增加延遲與伺服器負擔。
- A詳: WebService 以 SOAP/XML 序列化請求與回應，每篇文章、每則留言都需單獨往返，造成高 RTT 與 CPU 解碼成本。另受限於 WebMethod 參數設計，無法攜帶擴充欄位。改以 ASHX 批次匯入在本機一次解析與寫入，避免網路瓶頸，並可自定欄位處理與錯誤控管，大幅縮短總時間。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q1, C-Q1

B-Q14: Modified Date 錯誤的成因與修補位置？
- A簡: 匯入邏輯未正確寫入修改時間或被覆蓋；需於寫入時強制設定來源值。
- A詳: 有些匯入工具僅設定 Created/Published 時間，忽略 Modified，或在後續更新動作中以 Now 覆蓋導致全部相同。本案於自製匯入器呼叫 BlogEngine.Core API 時，明確對文章物件設定 Modified 日期為來源值，且避免後續流程重新 Save 時重置，確保歷史正確。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q7, B-Q2

B-Q15: 匿名留言與 IP 等敏感欄位的安全與相容性考量？
- A簡: 僅匯入必要欄位並遮蔽敏感資訊，符合隱私，兼顧顯示與稽核需求。
- A詳: CS2007 中匿名留言記錄作者名、網址、IP。遷移時須評估：1) 隱私與法規，避免公開 IP；2) 相容性，確保新系統欄位可承載；3) 用途分離，顯示用與稽核用分開儲存；4) 匯入時對缺失欄位提供預設。建議僅顯示暱稱與網址，IP 存入後台或雜湊，避免洩漏。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, C-Q3, D-Q2

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何建立一個 ASHX 匯入器讀取 BlogML？
- A簡: 建立 .ashx 讀取 App_Data 的 BlogML，迴圈寫入文章與留言並記錄對照。
- A詳: 實作步驟：1) 新增 MyImporter.ashx；2) 於 ProcessRequest 讀入 ~/App_Data/blog.xml；3) 解析 BlogML；4) 迴圈建立 Post 與 Comment，呼叫 BlogEngine.Core API 寫入；5) 記錄 CS PostID 與新 GUID 對照；6) 產生日誌。範例片段：
```csharp
var doc=XDocument.Load(Server.MapPath("~/App_Data/blog.xml"));
// foreach (entry) { var p=new Post(); p.Id=Guid.NewGuid(); p.Save(); map[csId]=p.Id; }
```
注意：權限與例外處理、Idempotent 設計與避免重覆匯入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q13, C-Q6

C-Q2: 如何用 SQL Management Studio 將查詢結果輸出為 XML？
- A簡: 在查詢中加 FOR XML AUTO，點擊結果儲存為 XML，手動加上根節點。
- A詳: 步驟：1) 開啟 SSMS，連線 CSDB；2) 執行查詢：
```sql
SELECT PostID,PostAuthor,PropertyNames,PropertyValues
FROM cs_posts WHERE ApplicationPostType=4 FOR XML AUTO
```
3) 在結果窗點開 XML 內容，另存為 .xml；4) 視需要加上 <root> 包裝；5) 供匯入器離線解析。最佳實踐：限定條件、防止特殊字元破壞、版本備份。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q3, D-Q1

C-Q3: 如何解析 PropertyNames/PropertyValues 並轉成 XML？
- A簡: 依名稱:型別:起:訖解析，Substring 取值，序列化為自訂 XML 供匯入。
- A詳: 步驟：1) 讀入 C-Q2 產生的 XML；2) 將 PropertyNames 以冒號拆分；3) 以四個為一組讀出 Name/Type/Start/End；4) 對應 PropertyValues Substring(Start,End-Start)；5) 組成 <comment user="..." url="..." ip="..."/>；6) 儲存新 XML。程式碼要點：邊界檢查、UTF-8 編碼、缺失欄位預設值。避免以 SQL/XPath 強拆，改由程式處理可控性更高。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q4, D-Q2

C-Q4: 如何以 Regex 修正舊圖檔連結為 image.axd？
- A簡: 使用涵蓋多網域與相對路徑的 Regex，擷取路徑重寫為 image.axd。
- A詳: 步驟：1) 準備 Regex：(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/([a-zA-Z0-9\-_\./%]*)；2) 對文章 HTML 進行替換，將群組3重寫為 image.axd?picture=$3；3) 排除 rss.aspx；4) 依序替換完整網域→相對路徑。注意：測試樣本覆蓋舊/新網域、手打路徑，避免破壞非圖片連結。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q7, D-Q3

C-Q5: 如何以兩階段流程修正站內文章連結？
- A簡: 首輪匯入記對照；二輪用 Regex 抓舊 PostID，查表換成新 GUID/Slug。
- A詳: 步驟：1) 首輪匯入後產生 map[oldId]=newGuid；2) 準備 Regex：(http\://(columns|community)\.chicken\-house\.net)?/blogs/chicken/archive/\d+/\d+/\d+/(\d+)\.aspx；3) 針對內容替換，將群組2 oldId 轉為 /post.aspx?id=newGuid 或 /post/new-slug.aspx；4) 重複掃描直到無變更。注意：保持可重入性、記錄未命中以人工核查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q6, C-Q6

C-Q6: 如何在 BlogEngine 建置新舊 ID 對照表？
- A簡: 匯入時紀錄 oldId→newGuid，持久化至 DB/檔案並提供查詢 API。
- A詳: 步驟：1) 設計資料結構（OldId int, NewGuid uniqueidentifier, Slug nvarchar）；2) 匯入時即時寫入；3) 實作簡易查詢類別供連結替換與重導使用；4) 加上唯一索引避免重覆；5) 匯出報表核對。示例：
```sql
CREATE TABLE IdMap(OldId INT PRIMARY KEY, NewGuid UNIQUEIDENTIFIER, Slug NVARCHAR(128))
```
最佳實踐：備份、稽核欄位（CreatedAt, Source）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5, D-Q9

C-Q7: 如何實作 CSUrlMap HttpHandler 並註冊路由？
- A簡: 撰寫處理 /blogs/*.aspx 的 Handler，web.config 註冊，內部轉交重導頁。
- A詳: 步驟：1) 建立 CSUrlMap.cs 實作 IHttpHandler；2) 準備三組 Regex：RSS、含 PostID、含舊 Slug；3) 依匹配設定 context.Items 並 Server.Transfer("~/blogs/AutoRedirFromCsUrl.aspx")；4) 在 web.config 加入 httpHandlers 路徑。片段：
```csharp
if (matchPostID.IsMatch(path)){ var id=...; context.Items["postID"]=map[id]; }
context.Server.Transfer("~/blogs/AutoRedirFromCsUrl.aspx");
```
注意：避免與既有路由衝突，測試 301 回應碼。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q10, D-Q8

C-Q8: 如何修正 BlogEngine 匯入時 Modified Date 問題？
- A簡: 在建立文章後立即設定 Modified 為來源值，避免後續 Save 覆蓋。
- A詳: 步驟：1) 解析來源 Modified；2) 建立 Post 物件後，於 Persist 前設定 post.DateModified=src.Modified；3) 確認後續流程不重置；4) 必要時修改核心或利用擴充點；5) 匯入完成後抽樣比對。程式片段：
```csharp
var p=new Post{DateCreated=src.Create, Title=src.Title};
p.DateModified=src.Modified; p.Save();
```
最佳實踐：統一時區、避免 Now() 誤用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, D-Q7, C-Q1

C-Q9: 如何驗證匯入成果與進行回滾備援？
- A簡: 以報表與抽樣檢核關鍵欄位，建立資料庫快照與檔案備份以便回滾。
- A詳: 步驟：1) 匯入前完整備份 DB 與 be-files；2) 匯入後產生比對報表（篇數、留言數、空欄位、未命中連結）；3) 抽樣檢查 Modified、PageView、匿名留言欄位；4) 測試重導與圖檔顯示；5) 問題即時回滾至快照；6) 修復後再試。最佳實踐：在 staging 測試、版本管控匯入程式與 Regex。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q10, D-Q9, C-Q6

C-Q10: 如何避開 RSS 與特殊路徑的誤判代換？
- A簡: 在 Regex 加入白名單/黑名單規則，或先行判斷路徑後再替換。
- A詳: 步驟：1) 於影像與內鏈替換前，先檢查是否匹配 rss.aspx、/rss.xml 等；2) Regex 以負向前瞻或條件分支排除；3) 替換順序從最特定到最一般；4) 同時保留例外清單供人工確認。示例：先判定 if (matchRss.IsMatch(path)) return; 再進行替換。避免將 RSS 與管理頁誤改導致不可用。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q9, D-Q9

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 匯入後少了約 10% 資料怎麼辦？
- A簡: BlogML 未涵蓋欄位需自製匯入補齊，離線抓取並寫入 BlogEngine API。
- A詳: 症狀：留言細節、計數等缺失。原因：BlogML 標準未包含平台特有欄位。解法：1) 以 SSMS FOR XML 輸出原表；2) 解析 PropertyNames/Values 還原匿名欄位；3) 自製 ASHX 以 BlogEngine.Core API 補寫入；4) 建立報表核對差異。預防：遷移前盤點欄位清單，先用沙箱測試涵蓋度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q2, C-Q3

D-Q2: 匯入的留言作者名稱或網址遺失的原因與解法？
- A簡: CS 將留言屬性序列化集中儲存，需解析 PropertyNames/Values 才能取回。
- A詳: 症狀：匿名留言顯示為空白或缺網址。原因：BlogML 未含 CS 特有欄位，且 CS 將 SubmittedUserName、TitleUrl 等壓在 PropertyValues。解法：以自製解析器依 Name:Type:Start:End 取值，補寫入 BlogEngine 的 Comment 欄位。預防：先抽樣驗證解析正確性、處理編碼與缺值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q4, C-Q3

D-Q3: 匯入後圖檔顯示 404 的原因？
- A簡: 舊絕對路徑失效或新系統改用 Handler，需以 Regex 重寫為 image.axd。
- A詳: 症狀：文章內圖片破圖。原因：CS 使用 /blogs/chicken/... 絕對網址，BlogEngine 以 image.axd 提供；域名變動也會致 404。解法：用 Regex 擷取舊圖路徑，改寫為 image.axd?picture=...；測試分家前/後域名與相對路徑。預防：替換順序嚴謹、排除 RSS、完整測試樣本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q7, C-Q4

D-Q4: 站內連結仍指向 CS 舊站如何處理？
- A簡: 採兩階段；建立 ID 對照後，以 Regex 捕捉舊 URL 轉換為新 GUID/Slug。
- A詳: 症狀：點擊仍到舊站或 404。原因：首輪匯入未有新 GUID/Slug，無法即時替換。解法：建立 oldId→newGuid 對照表，第二階段用 Regex 擷取 PostID，替換為 /post.aspx?id=newGuid 或 Slug 型。預防：導入流程設計為可重入、多次掃描直到收斂。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q6, C-Q5

D-Q5: 正規表示式沒有匹配某些古早手工連結？
- A簡: 擴充分支與測試樣本，加入相對路徑與大小寫、符號變體的容錯。
- A詳: 症狀：少數連結未被替換。原因：早期手打連結不符現有模式、大小寫差異或特殊字元。解法：擴充 Regex 覆蓋相對路徑、允許符號集、加上可選群組；建立未命中清單人工修補。預防：以 Regex 測試工具（如 regexlib）反覆驗證，版本管控規則。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q7, C-Q10

D-Q6: 使用 WebService 匯入過慢或逾時怎麼改善？
- A簡: 改用伺服器端批次匯入（ASHX），減少往返與序列化負擔。
- A詳: 症狀：大量文章匯入耗時、逾時。原因：每篇/每則留言都發出獨立 SOAP 呼叫。解法：改以 ASHX 本地批次匯入；若不得已，則增大逾時、批次打包與壓縮傳輸。預防：估算規模、壓力測試、監控失敗重試策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q13, C-Q1

D-Q7: 文章 Modified Date 全錯或相同如何排查？
- A簡: 檢查匯入程式是否覆蓋 Modified，改於保存前設定來源值。
- A詳: 症狀：所有文章修改時間相同或為當天。原因：匯入程式用 Now() 覆蓋或未填寫導致預設值。解法：在建立 Post 後、儲存前指定 DateModified=來源值；檢查後續流程是否再 Save 覆寫。預防：單元測試日期欄位、統一時區、抽樣比對。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q8, C-Q9

D-Q8: 外部網站連到舊 CS 網址的 SEO 影響與解法？
- A簡: 以 CSUrlMap 攔截舊 URL，301 重導到新文章，保留排名與權重。
- A詳: 症狀：外站連結跳到 404，SEO 流失。解法：實作 CSUrlMap HttpHandler，解析舊 URL 中的 PostID/Slug，查對照表，回應 301 至新 URL；無對應則導首頁並提示。預防：完整覆蓋舊網址樣式、提供 RSS 舊路徑的對應、持續監控 404 日誌。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q9, C-Q7

D-Q9: 重導到首頁或找不到文章的錯誤如何診斷？
- A簡: 檢查 Regex 匹配、對照表是否有 OldId、與 Handler 路由衝突。
- A詳: 症狀：總被導至首頁或顯示查無此頁。原因：Regex 未抓到 PostID、對照表缺值、Handler 未正確註冊或被其他路由攔截。解法：開啟日誌記錄匹配結果與查表狀態；確認 httpHandlers 註冊順序；補齊對照表。預防：上線前跑全站掃描、導入監控與警示。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q9, C-Q6

D-Q10: 匯入後出現重複文章或缺漏如何修復？
- A簡: 以對照表與唯一鍵查核，支援重跑可重入，差異報表協助人工補救。
- A詳: 症狀：文章重覆或少數漏匯。原因：無唯一鍵保護、匯入中斷未續傳。解法：為新資料表加唯一索引；匯入程式以 OldId 判斷是否已存在再決定新增/更新；產生差異報表重試；必要時回滾重跑。預防：事前設計 Idempotent 流程、階段性快照。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, C-Q9, B-Q8

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 BlogEngine.NET？
    - A-Q2: 什麼是 Community Server 2007（CS2007）？
    - A-Q3: 什麼是 BlogML？用途為何？
    - A-Q4: 為什麼從 CS2007 遷移到 BlogEngine.NET？
    - A-Q5: 匯入（Import）與遷移（Migration）的差異？
    - A-Q6: 什麼是 PostID？為何要保留舊 ID？
    - A-Q7: 什麼是 Slug？與 PostID 有何差異？
    - A-Q8: 什麼是 PageViewCount？為何需要匯入？
    - B-Q1: BlogEngine 的 BlogImporter.asmx 如何運作？
    - B-Q5: 使用 SQL Server FOR XML 輸出資料的原理？
    - B-Q11: BlogEngine 文章 URL 結構與 Slug 生成機制？
    - D-Q6: 使用 WebService 匯入過慢或逾時怎麼改善？
    - D-Q3: 匯入後圖檔顯示 404 的原因？
    - D-Q4: 站內連結仍指向 CS 舊站如何處理？
    - C-Q2: 如何用 SQL Management Studio 將查詢結果輸出為 XML？

- 中級者：建議學習哪 20 題
    - A-Q9: 什麼是 HttpHandler（.ashx）？與 WebService（.asmx）差異？
    - A-Q10: 什麼是兩階段（2-pass）匯入？為何需要？
    - A-Q11: 什麼是 CS2007 的 PropertyNames/PropertyValues 格式？
    - A-Q12: 什麼是內部連結與外部連結修正？
    - A-Q13: 什麼是 URL Rewrite？在兩系統中的角色？
    - A-Q14: 為什麼用正規表示式（Regex）改寫連結？
    - B-Q2: 自製 ASHX 匯入器的執行流程為何？
    - B-Q3: BlogEngine 圖片與檔案下載的 HttpHandler 機制是什麼？
    - B-Q4: CS2007 屬性序列化的解析機制為何？
    - B-Q6: 內部連結識別的 Regex 設計思路？
    - B-Q7: 影像連結 Regex 設計與網域覆蓋策略？
    - B-Q8: 新舊 ID 對照表如何建立與運作？
    - B-Q9: CSUrlMap HttpHandler 如何攔截與重導？
    - B-Q10: Server.Transfer 為何適合此重導流程？
    - C-Q1: 如何建立一個 ASHX 匯入器讀取 BlogML？
    - C-Q3: 如何解析 PropertyNames/PropertyValues 並轉成 XML？
    - C-Q4: 如何以 Regex 修正舊圖檔連結為 image.axd？
    - C-Q5: 如何以兩階段流程修正站內文章連結？
    - C-Q6: 如何在 BlogEngine 建置新舊 ID 對照表？
    - D-Q2: 匯入的留言作者名稱或網址遺失的原因與解法？

- 高級者：建議關注哪 15 題
    - A-Q15: Server.Transfer 與 Redirect 差異？遷移時如何取捨？
    - B-Q12: Web 應用管線中 HttpHandler 的角色與順序？
    - B-Q13: 為何 WebService 逐篇匯入效能較差？瓶頸在哪？
    - B-Q14: Modified Date 錯誤的成因與修補位置？
    - B-Q15: 匿名留言與 IP 等敏感欄位的安全與相容性考量？
    - C-Q7: 如何實作 CSUrlMap HttpHandler 並註冊路由？
    - C-Q8: 如何修正 BlogEngine 匯入時 Modified Date 問題？
    - C-Q9: 如何驗證匯入成果與進行回滾備援？
    - C-Q10: 如何避開 RSS 與特殊路徑的誤判代換？
    - D-Q1: 匯入後少了約 10% 資料怎麼辦？
    - D-Q5: 正規表示式沒有匹配某些古早手工連結？
    - D-Q7: 文章 Modified Date 全錯或相同如何排查？
    - D-Q8: 外部網站連到舊 CS 網址的 SEO 影響與解法？
    - D-Q9: 重導到首頁或找不到文章的錯誤如何診斷？
    - D-Q10: 匯入後出現重複文章或缺漏如何修復？