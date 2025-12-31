---
layout: synthesis
title: "換訂閱的網址了!"
synthesis_type: faq
source_post: /2008/06/19/changed-subscription-url/
redirect_from:
  - /2008/06/19/changed-subscription-url/faq/
postid: 2008-06-19-changed-subscription-url
---

# 換訂閱的網址了!

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 RSS/Atom 訂閱？
- A簡: RSS/Atom 是用標準格式輸出網站更新，讀者以訂閱網址讓閱讀器自動抓取新內容。
- A詳: RSS/Atom 是網站以結構化 XML 格式發佈更新的標準。使用者在閱讀器中加入訂閱網址（Feed URL），閱讀器會定期抓取，顯示標題、摘要、內文與附件（如圖片、音訊）。它解耦內容與呈現，讓讀者不必逐站造訪，也便於跨平台聚合與離線閱讀。本文更換的就是此「訂閱網址」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, B-Q7

A-Q2: 什麼是訂閱網址（Feed URL）？
- A簡: 訂閱網址是供閱讀器抓取更新的專用 URL，與一般瀏覽用頁面網址不同。
- A詳: 訂閱網址（Feed URL）是一個返回 RSS/Atom XML 的端點，供 Feed 讀取器週期性擷取更新。相較一般網頁 URL 返回 HTML 給瀏覽器，Feed URL 返回機器可讀的結構資料。本文舊址與新址皆為 Feed URL，需在閱讀器內更新為新端點以確保內容正確。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, B-Q7

A-Q3: 什麼是 FeedBurner？
- A簡: FeedBurner 是第三方 feed 代理與統計服務，轉發原生 feed 並提供追蹤與功能。
- A詳: FeedBurner 充當網站原生 feed 與讀者之間的代理。它抓取來源 feed，重新輸出統一的訂閱網址，並提供訂閱數、點擊、郵件訂閱、摘要重寫等功能。本文的 FeedBurner 位址為 http://feeds.feedburner.com/andrewwu，可續用，但文內相對路徑可能造成圖片掉失。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q2, C-Q5

A-Q4: 為什麼要更換訂閱網址？
- A簡: 舊址需長期掛轉址，易遺留問題；新址直連來源，內容與顯示較穩定。
- A詳: 作者曾把舊訂閱網址自動轉到新站，但發現舊址需永久維持，使用者也容易多年不更新。加上文章內含相對路徑，透過代理或轉址易出現掉圖或連結錯位。故主動提醒更新至新 feed（http://columns.chicken-house.net/syndication.axd）或繼續用 FeedBurner，提升長期穩定與可維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q8, B-Q4

A-Q5: 自動轉址與手動更換有何差異？
- A簡: 自動轉址便利短期導流；手動更換可從根本更新來源，長期更穩健。
- A詳: 自動轉址（301/302）能快速把舊訂閱導到新源，但需持續維護轉址規則，且有閱讀器緩存與更新延遲。手動更換是由使用者在閱讀器改存新 URL，之後直接抓取新源，減少中間代理與依賴。本文選擇提醒手動更換，以避免長期掛轉址與資訊折損。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q2, D-Q3

A-Q6: 什麼是相對路徑與絕對路徑？
- A簡: 相對路徑依當前位置解析；絕對路徑含完整網域能獨立被任何客戶端解析。
- A詳: 相對路徑如 /images/a.png 或 ./img/a.png，需結合當前文件 URL 才能定位。絕對路徑如 https://example.com/images/a.png，包含協定與網域，任何環境解析一致。Feed 經代理或跨網域顯示時，相對路徑易解析錯誤導致掉圖，本文即提醒此風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q3, C-Q4

A-Q7: 為何相對路徑會在閱讀器中掉圖？
- A簡: 閱讀器解析相對路徑時基準不一，經代理或轉址後來源上下文改變。
- A詳: 許多閱讀器與代理（如 FeedBurner）以自身的 feed URL 作為解析基準，若內文使用相對路徑，基準一旦變成代理的網域或重導後的 URL，就會找不到原站資源，導致圖片或連結失效。改為絕對路徑或內容重寫可避免此問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q4, D-Q2

A-Q8: 舊 Community Server 訂閱網址與新網址差異？
- A簡: 舊址為 /blogs/chicken/rss.aspx，新址為 /syndication.axd，後者為未來唯一來源。
- A詳: 舊址 http://columns.chicken-house.net/blogs/chicken/rss.aspx 屬於原 Community Server 架構下的 feed 端點。新址 http://columns.chicken-house.net/syndication.axd 為新站的訂閱來源。作者將新址作為今後唯一發佈點，舊址留下提示文提醒更換，以免讀者卡在過時來源。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q1, D-Q1

A-Q9: 什麼是 syndication.axd？
- A簡: syndication.axd 常見於 .NET 部落格系統的 feed 輸出端點，返回 RSS/Atom。
- A詳: 在部分 .NET 型部落格與 CMS（如 Subtext/DasBlog/自製）中，syndication.axd 是負責輸出 RSS/Atom 的 HTTP 處理器端點。請閱讀器訂閱該 URL，即可獲得標準的 XML feed。本文明確指向此新端點，作為未來的訂閱來源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q1, B-Q1

A-Q10: FeedBurner 與原生 feed 有何差異？
- A簡: 原生 feed 直接出自網站；FeedBurner 為代理層，提供重寫與統計等額外服務。
- A詳: 原生 feed 由網站直接輸出，路徑與資源參照最一致；FeedBurner 抓取原生 feed 後再輸出代理 URL，能加入追蹤、郵件訂閱與廣告，但多一層轉發與緩存。當內文含相對路徑或需即時更新時，原生 feed 更穩；需行銷與統計時可用 FeedBurner。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q2, D-Q5

A-Q11: 為何保留 FeedBurner 仍可能出現顯示問題？
- A簡: 代理重寫與相對路徑解析差異，可能導致圖片或連結在部分客戶端失效。
- A詳: FeedBurner 會重寫追蹤連結、緩存內容，並以自身域名發佈。若文章內有相對路徑或內嵌資源依賴原站上下文，代理後的基準改變會造成解析錯誤。雖可續用 FeedBurner，但最佳做法是使用絕對路徑或在源端改寫內容以確保一致顯示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, C-Q4

A-Q12: 訂閱者長期不更換 URL 的風險？
- A簡: 會停留在過時來源、看不到新文或僅見提示，且易發生資源載入錯誤。
- A詳: 若依賴轉址而不主動更換，隨著架構演進與規則過期，讀者可能只看到舊站固定提示、不再接收新文章，或遇到圖片、連結失效等體驗問題。長期看，手動更新至新 feed 能降低維護成本與顯示風險，確保持續獲取正確內容。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, D-Q1, D-Q3

A-Q13: 什麼是 301 與 302 轉址？
- A簡: 301 為永久轉址，建議更新書籤；302 為暫時轉址，來源未改變。
- A詳: HTTP 301 表示資源永久移動，客戶端與搜尋引擎應更新為新 URL；302 則為暫時性轉移，未承諾永久改變。Feed 遷移時，多用 301 將舊 feed 指向新端點，但仍建議用戶手動改訂閱，避免永續依賴轉址鏈造成失效與維護負擔。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, D-Q8

A-Q14: 什麼是閱讀器（Feed Reader）？
- A簡: 閱讀器是訂閱並呈現 RSS/Atom 的應用，如 Feedly、Outlook、Thunderbird。
- A詳: Feed Reader 會管理多個訂閱來源、定期抓取、去重與呈現內容，並支援標籤、同步、搜尋等功能。不同閱讀器對 HTML、圖片、腳本與相對路徑的處理略有差異，是本文提及掉圖與轉址體驗差異的關鍵環節。更新訂閱網址需在閱讀器內操作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, B-Q7, D-Q9

A-Q15: 為何文章內連結設計會影響訂閱體驗？
- A簡: 內容在閱讀器與代理中呈現，連結解析、資源載入與安全限制皆受影響。
- A詳: Feed 內文會在多個環境顯示（Web、App、代理），若使用相對路徑、混合內容或外連需權限，會因基準、CORS、HTTPS 政策而失效。改用絕對 HTTPS、CDN 穩定域名與正確 MIME，可顯著提升跨平台顯示一致性，減少掉圖與錯鏈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, C-Q9

### Q&A 類別 B: 技術原理類

B-Q1: RSS/Atom feed 如何運作？
- A簡: 站點輸出 XML，閱讀器依計畫抓取並比對新項目後呈現內容給使用者。
- A詳: 站點根據 RSS/Atom 規範輸出 channel、item（或 entry）等 XML 節點，包含標題、連結、摘要、發佈時間與內容。閱讀器以 ETag/Last-Modified 控制抓取，解析後去重與排序，將新項目呈現。附件可透過 enclosure 或內文 <img> 參照。本文更換的是該 XML 端點的 URL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q2, B-Q7

B-Q2: FeedBurner 的工作流程與架構是什麼？
- A簡: 它抓取來源 feed、緩存與重寫，輸出代理 URL 並提供統計與增值功能。
- A詳: FeedBurner 週期性抓取來源 feed，進行格式驗證、壓縮、緩存與內容重寫（追蹤參數、點擊計數）。讀者訂閱 FeedBurner URL，請求先到 FeedBurner，再回源更新或用緩存回應。此代理層提供訂閱統計、郵件推送等，但可能引入延遲與相對路徑解析差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q10, D-Q5

B-Q3: 相對/絕對路徑在客戶端如何被解析？
- A簡: 相對路徑以文件基準 URL 解析；絕對路徑以協定+網域直達資源。
- A詳: URL 解析遵循 RFC 3986。相對路徑需結合 base URI（可由 HTML <base> 或文件 URL 推導）。在 feed 內文中，閱讀器常以 feed 本身 URL 為基準，或忽略 <base>。若 feed 由代理輸出，基準變成代理域名，故相對路徑常失效。絕對路徑跨環境穩定解析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, C-Q4

B-Q4: 301/302 在 feed 遷移中的行為機制？
- A簡: 閱讀器收到 301 會更新快取與目標；302 多視為暫時且不改存檔。
- A詳: 多數閱讀器對 301 會在後續抓取直接請求新 URL，部分甚至更新本地記錄；對 302 則保持原 URL 不變並臨時跟隨。然並非所有客戶端都永遠記住 301，且企業快取可能攔截，導致長鏈或循環風險。因此仍建議用戶手動更新，避免依賴自動行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q13, D-Q8

B-Q5: Community Server 與 feed 產生的關係為何？
- A簡: 其內建產生 RSS 端點（如 rss.aspx），輸出文章列表的標準 XML。
- A詳: Community Server 是早期 .NET 社群/部落格平台，提供內建 RSS 端點（多見於 rss.aspx），將資料庫文章序列化為 RSS XML。遷移平台時，舊端點仍可存活或設置轉址。本文舊址即為此類端點，現已以新端點取代作為主來源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q6, C-Q3

B-Q6: syndication.axd 可能的實作機制是什麼？
- A簡: 由 .NET HTTP Handler 產生 RSS/Atom，查詢資料後串流回傳 XML。
- A詳: 在 ASP.NET 中，.axd 常由 IHttpHandler 處理。syndication.axd 接收請求，查詢資料源（DB/檔案），使用 SyndicationFeed/XmlWriter 等 API 序列化為 RSS/Atom，設定 Content-Type 為 application/rss+xml 或 application/atom+xml，並支援 ETag/壓縮。這解釋了本文新端點的技術背景。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q1, C-Q1

B-Q7: 閱讀器如何抓取與快取 feed？
- A簡: 依間隔發送 If-None-Match/If-Modified-Since，比對後回 304 或取新內容。
- A詳: 閱讀器會根據訂閱量與策略設定抓取頻率，透過 ETag 與 Last-Modified 與伺服器協商。若無更新則回 304，節省頻寬；有更新則回 200 與新 XML。代理如 FeedBurner 亦有自己的抓取周期與快取層，可能造成延遲或不同步。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2, D-Q4

B-Q8: 圖片在 feed 中的引用機制是什麼？
- A簡: 可用內文 <img> 直接嵌入，或以 enclosure 作附件；皆需可公開存取。
- A詳: 多數部落格將圖片以 <img> 引用，閱讀器會嘗試載入該 URL。另可用 enclosure 指向媒體，並由閱讀器決定呈現方式。若 URL 為相對路徑、需 Cookie、或不支援跨域/HTTPS，容易失敗。絕對 HTTPS、CDN 與正確 Content-Type 是成功關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q9, D-Q2

B-Q9: 轉址鏈過長對體驗與 SEO 的影響？
- A簡: 增加延遲與失敗率，並稀釋權重；對 feed 亦會導致抓取不穩。
- A詳: 多重轉址會增加 RTT、降低成功率，代理與企業防火牆也可能截斷。搜尋引擎處理轉址會傳遞權重但有損失；閱讀器在長鏈下更易快取錯亂或放棄更新。故 feed 遷移應以單一 301 並鼓勵手動更換，縮短鏈路，保持來源清晰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q13, D-Q8

B-Q10: Feed URL 變更對統計與追蹤的影響？
- A簡: 代理統計可能重置或分裂，原生與代理數據需重新對齊。
- A詳: 變更 URL 後，依賴代理（如 FeedBurner）的訂閱數、點擊與來源追蹤會因新舊 URL 並存而分裂。若改直訂新源，代理端統計可能下滑、但原生端日誌可補充。可用 UTM、統一外鏈、過渡期雙發佈等手法，平滑過渡數據。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q6, A-Q10

B-Q11: 多來源 feed 同步的維護策略？
- A簡: 設定單一權威來源，其他代理訂閱此源並監測同步延遲。
- A詳: 建議確立「權威源」（如新 syndication.axd），所有代理與鏡像均從該源抓取。設定健康檢查與延遲監控，避免重入與循環轉址。必要時對代理設定更新頻率與時區一致，並限制保留歷史項目數以防重複推送。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q2, C-Q5, D-Q7

B-Q12: 內容中的相對連結如何被重寫為絕對？
- A簡: 以伺服器或發佈流程插入基底網域，輸出絕對 HTTPS URL。
- A詳: 可在渲染層掃描 HTML，將 <img src>、<a href> 等相對路徑前置站點根（含協定與網域），或於 CMS 編輯器保存時即轉換。亦可加入 <base>，但閱讀器支援不一。發佈管線自動化重寫最可靠，確保跨環境一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q2, A-Q6

B-Q13: 網站「訂閱」按鈕如何實作自動發現？
- A簡: 於頁頭加入 rel="alternate" 的 link 標籤，指向 RSS/Atom。
- A詳: 瀏覽器與擴充套件會讀取 <link rel="alternate" type="application/rss+xml" title="..." href="..."> 自動發現 feed。也可提供多格式（RSS/Atom）多條 link。本文提到可點網站上方「訂閱」功能，即常見的 UI 與 auto-discovery 結合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, A-Q2, B-Q1

B-Q14: 舊 feed 僅顯示提示文的技術做法？
- A簡: 以伺服器判斷舊端點，輸出固定 RSS 條目提醒用戶更換。
- A詳: 在舊端點路徑上，改由程式輸出只有一則 item 的 RSS，內容為「請更換訂閱網址」，並在描述中附上新 URL。此法比硬轉址更易被讀者看見提醒，且避免閱讀器忽略 301。本文即採用此策略，讓舊址只見提示文章。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2, D-Q1

B-Q15: 版本控制與回溯如何幫助 feed 遷移？
- A簡: 以版本化設定與回滾策略，快速恢復錯誤配置與內容重寫問題。
- A詳: 將轉址規則、內容重寫器、模板與自動化腳本納入版本控制（Git），搭配環境化設定與藍綠部署。若遷移後出現掉圖或循環轉址，可快速回滾至上一版，並藉由差異比較定位問題，提高遷移安全性與可觀測性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q3, C-Q4, D-Q8

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在網站設定新的 feed URL（syndication.axd）？
- A簡: 確認端點輸出正確 XML，於導航與頁頭提供連結供用戶訂閱。
- A詳: 步驟：1) 部署 syndication.axd，確保 Content-Type 與 RSS/Atom 格式正確；2) 導航加入「訂閱」連結指向 http://columns.chicken-house.net/syndication.axd；3) 頁頭加 auto-discovery。程式碼：<link rel="alternate" type="application/rss+xml" href="http://columns.chicken-house.net/syndication.axd">。注意啟用壓縮與快取標頭，確保效能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q13, C-Q8

C-Q2: 如何通知用戶更換訂閱網址？
- A簡: 多管齊下：站內公告、舊 feed 提示文、社群貼文與郵件提醒。
- A詳: 步驟：1) 發公告文置頂；2) 舊 feed 僅輸出「請更換訂閱」條目；3) 社群平台同步貼文；4) 若有郵件訂閱，寄出教學；5) FAQ 提供各閱讀器更換指引。最佳實踐：維持至少 60-90 天過渡期，定期提醒。可使用 UTM 追蹤通知成效。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q14, A-Q12, C-Q6

C-Q3: 如何在伺服器設定從舊到新的 301 轉址？
- A簡: 以伺服器重寫規則將舊 rss.aspx 永久導向 syndication.axd。
- A詳: Apache: Redirect 301 /blogs/chicken/rss.aspx https://columns.chicken-house.net/syndication.axd。Nginx: location = /blogs/chicken/rss.aspx { return 301 https://columns.chicken-house.net/syndication.axd; }。IIS web.config: <rule name="rss301"><match url="^blogs/chicken/rss\.aspx$" /><action type="Redirect" url="https://columns.chicken-house.net/syndication.axd" redirectType="Permanent" /></rule>。測試循環與 HTTPS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q4, D-Q8

C-Q4: 如何將文章內相對路徑批次改為絕對？
- A簡: 以腳本或 CMS 插件重寫 HTML 屬性，前置站點完整域名與協定。
- A詳: 步驟：1) 匯出文章 HTML；2) 用腳本掃描 src/href 以 / 或 ./ 開頭之路徑；3) 以 https://columns.chicken-house.net 作前綴；4) 回寫資料庫。範例（Node.js）：html.replace(/(src|href)="(\/[^"]+)"/g, '$1="https://columns.chicken-house.net$2"')。注意備份、測試、避免雙重前綴與外站連結誤改。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q12, D-Q2

C-Q5: 如何在 FeedBurner 中更新來源 feed？
- A簡: 登入 FeedBurner，於 Edit Feed Details 將原始 Source URL 改為新端點。
- A詳: 步驟：1) 登入 FeedBurner；2) 選擇對應 feed；3) 於 Edit Feed Details 將 Original Feed 改為 http://columns.chicken-house.net/syndication.axd；4) Resync/Resheed；5) 檢查 BrowserFriendly 與追蹤設定。注意：觀察抓取錯誤與延遲，並在公告同步說明 FeedBurner 與原生的取用差異。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q2, D-Q5

C-Q6: 如何在常見閱讀器更改訂閱 URL？
- A簡: 在訂閱設定中編輯來源 URL，貼上新 feed，保存並強制刷新。
- A詳: Feedly：選擇訂閱→三點→Edit Website→替換 URL。Outlook：檔案→帳戶設定→RSS 摘要→選訂閱→變更→貼新 URL。Thunderbird：右鍵 RSS 資料夾→訂閱→編輯來源→貼新 URL。操作後手動更新一次，確認新文章與圖片正常顯示。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, D-Q1, D-Q9

C-Q7: 如何在網站提供 feed 自動發現（autodiscovery）？
- A簡: 在 <head> 加入 rel="alternate" 的 RSS/Atom link，並標示標題。
- A詳: 於模板 head 區加入：<link rel="alternate" type="application/rss+xml" title="訂閱本部落格" href="https://columns.chicken-house.net/syndication.axd">。若支援 Atom，再加一條。測試瀏覽器擴充是否能偵測。避免多個不同 feed 混淆，確立唯一權威來源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, C-Q1, A-Q2

C-Q8: 如何驗證新 feed 的有效性？
- A簡: 使用驗證器檢查格式與連結，並在多個閱讀器實測呈現。
- A詳: 步驟：1) 以 W3C/Feed Validator 驗證 RSS/Atom 格式；2) 用 curl 檢查 Content-Type、壓縮、ETag；3) 在 Feedly/Outlook/Thunderbird 訂閱實測；4) 檢查圖片、外連、時區與排序；5) 監控日誌錯誤。確保 200/304 正常回應與更新頻率合理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q7, D-Q9

C-Q9: 如何避免遷移期間圖片掉圖？
- A簡: 改絕對 HTTPS、固定域名，必要時使用 CDN 與內容重寫。
- A詳: 步驟：1) 將內文資源改為絕對 HTTPS；2) 啟用穩定的 images 子域或 CDN；3) 於渲染層重寫相對路徑；4) 檢查跨域與權限；5) 在測試閱讀器驗證。最佳實踐：避免需 Cookie 才能取用的圖片，並設定正確 Cache-Control 與 MIME。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q8, D-Q2

C-Q10: 如何設計 feed 遷移的過渡期策略？
- A簡: 雙路徑並行、單一權威源、明確時程與多次提醒，最後收斂。
- A詳: 方案：1) 設定 301 與舊 feed 提示文並存；2) 所有代理改抓新源；3) 公佈時程（如 90 天）；4) 定期提醒與教程；5) 監控錯誤與訂閱遷移率；6) 過期後停用舊源或僅保留提示。以數據決定延長與否，確保最小干擾切換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q10, D-Q6

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 閱讀器只顯示「請更換訂閱網址」怎麼辦？
- A簡: 表示仍訂閱舊 feed，請在閱讀器改為新 URL 再重新抓取。
- A詳: 症狀：所有新文章未更新，僅見一則提醒文章。原因：仍指向舊端點 http://columns.chicken-house.net/blogs/chicken/rss.aspx。解法：在閱讀器編輯訂閱，改為 http://columns.chicken-house.net/syndication.axd 或 FeedBurner URL。刷新後檢查是否出現近期文章。預防：完成後刪除舊訂閱，避免混淆。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q6, C-Q2

D-Q2: 圖片在閱讀器不顯示如何排查？
- A簡: 檢查路徑是否相對、是否 HTTPS、是否需權限或跨域受限。
- A詳: 症狀：文字可見但圖片占位或破圖。原因：相對路徑解析錯誤、混合內容（HTTP 圖片）、需登入權限、CORS/防盜鍊。步驟：1) 檢視原始 HTML；2) 嘗試以絕對 HTTPS 直開；3) 修正路徑與權限；4) 清除代理緩存重抓。預防：發佈流程自動轉絕對、統一 HTTPS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q8, C-Q4

D-Q3: 轉址後仍停留舊 feed 的原因與解法？
- A簡: 客戶端未更新、緩存緊黏或 302 導致；手動改 URL 並用 301。
- A詳: 症狀：反覆回舊源或偶爾才看到新文。原因：閱讀器未遵循 301 更新、用 302、快取代理未刷新。解法：改用永久 301、縮短舊源 Cache-Control、在公告引導用戶手動更換。預防：過渡期監控日誌，確保大多數請求直達新源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q13, C-Q3

D-Q4: Feed 抓取頻率過高造成負載怎麼辦？
- A簡: 設定正確快取標頭與 ETag，限制頻率並使用 CDN 緩解。
- A詳: 症狀：伺服器負載升高、頻繁 200 回應。原因：閱讀器未協商快取或過度頻繁抓取。解法：設定 ETag/Last-Modified、合理 Cache-Control、啟用壓縮；必要時以 CDN 緩存。預防：提供「建議更新週期」的 Retry-After/FeedHints（若支援）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q8, B-Q1

D-Q5: FeedBurner 抓取失敗如何診斷？
- A簡: 檢查來源 URL 可達性、格式、HTTP 狀態與防火牆限制。
- A詳: 症狀：FeedBurner 顯示抓取錯誤或過久未更新。原因：來源 4xx/5xx、格式不合法、TLS 問題、阻擋 UA。步驟：1) 直接以 curl 取源；2) 驗證 XML；3) 查 TLS/CA；4) 暫停阻擋；5) 在 FeedBurner Resync。預防：監控來源可用性與格式驗證自動化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q5, C-Q8

D-Q6: 訂閱統計下滑如何分析與補救？
- A簡: 分辨遷移造成的統計分裂，整合多源數據並持續引導更換。
- A詳: 症狀：總訂閱顯著下降。原因：新舊 URL 分裂、代理與原生口徑不同。步驟：1) 匯總代理數與伺服器日誌；2) 比對遷移時程；3) 強化提醒與教學；4) 延長過渡期；5) 於站內顯示新 feed 的醒目按鈕。預防：事前設指標基準線與 UTM 追蹤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q10, C-Q2

D-Q7: 出現重複文章或排序錯亂怎麼處理？
- A簡: 檢查 GUID、發佈時間與時區，確保唯一性與一致排序。
- A詳: 症狀：同文反覆出現或順序漂移。原因：item GUID 改變、pubDate 時區錯、代理重寫。解法：固定 GUID、使用 UTC 時間、避免改動舊項目；代理層開啟「不改 GUID」。預防：發布管線測試，確保遷移不改歷史項目。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q11, C-Q10

D-Q8: 轉址導致循環重導如何排查？
- A簡: 檢查新舊規則互指、代理回源邏輯與路由前綴。
- A詳: 症狀：請求往返多次後失敗（過多轉址）。原因：舊→新 301，同時新環境反向導回舊；或代理抓取使用舊 URL。步驟：1) 以 -L 追蹤 curl；2) 檢視伺服器與代理規則；3) 白名單代理 UA；4) 修正唯一路徑。預防：單向 301、清楚權威源設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q3, B-Q9

D-Q9: 特定閱讀器無法解析新 feed 怎麼辦？
- A簡: 驗證格式與編碼，檢查 Content-Type 與特殊字元。
- A詳: 症狀：某閱讀器報錯或不顯示。原因：MIME 錯誤、UTF-8/BOM、非法 XML 字元、過長欄位。解法：用驗證器檢測、設定正確 Content-Type（application/rss+xml）、移除非法字元、縮短標題。預防：CI 驗證與跨閱讀器測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, B-Q1, B-Q6

D-Q10: 遷移後 SEO 與外鏈流量下滑如何補救？
- A簡: 完整 301 覆蓋、站內外更新連結、提供清晰入口與站點地圖。
- A詳: 症狀：來自搜尋或外站的流量減少。原因：連結仍指向舊源或轉址鏈失效。解法：補齊 301 規則、更新站內連結與社群檔案、通知友站更新連結、提交新的 sitemap 與 feed 給搜尋引擎。預防：過渡期監測 404 與轉址命中率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q3, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 RSS/Atom 訂閱？
    - A-Q2: 什麼是訂閱網址（Feed URL）？
    - A-Q3: 什麼是 FeedBurner？
    - A-Q4: 為什麼要更換訂閱網址？
    - A-Q5: 自動轉址與手動更換有何差異？
    - A-Q6: 什麼是相對路徑與絕對路徑？
    - A-Q7: 為何相對路徑會在閱讀器中掉圖？
    - A-Q8: 舊 Community Server 訂閱網址與新網址差異？
    - A-Q9: 什麼是 syndication.axd？
    - A-Q13: 什麼是 301 與 302 轉址？
    - A-Q14: 什麼是閱讀器（Feed Reader）？
    - A-Q15: 為何文章內連結設計會影響訂閱體驗？
    - C-Q1: 如何在網站設定新的 feed URL（syndication.axd）？
    - C-Q2: 如何通知用戶更換訂閱網址？
    - D-Q1: 閱讀器只顯示「請更換訂閱網址」怎麼辦？

- 中級者：建議學習哪 20 題
    - B-Q1: RSS/Atom feed 如何運作？
    - B-Q2: FeedBurner 的工作流程與架構是什麼？
    - B-Q3: 相對/絕對路徑在客戶端如何被解析？
    - B-Q4: 301/302 在 feed 遷移中的行為機制？
    - B-Q7: 閱讀器如何抓取與快取 feed？
    - B-Q8: 圖片在 feed 中的引用機制是什麼？
    - B-Q10: Feed URL 變更對統計與追蹤的影響？
    - B-Q11: 多來源 feed 同步的維護策略？
    - B-Q12: 內容中的相對連結如何被重寫為絕對？
    - B-Q13: 網站「訂閱」按鈕如何實作自動發現？
    - B-Q14: 舊 feed 僅顯示提示文的技術做法？
    - C-Q3: 如何在伺服器設定從舊到新的 301 轉址？
    - C-Q4: 如何將文章內相對路徑批次改為絕對？
    - C-Q5: 如何在 FeedBurner 中更新來源 feed？
    - C-Q6: 如何在常見閱讀器更改訂閱 URL？
    - C-Q8: 如何驗證新 feed 的有效性？
    - C-Q9: 如何避免遷移期間圖片掉圖？
    - C-Q10: 如何設計 feed 遷移的過渡期策略？
    - D-Q2: 圖片在閱讀器不顯示如何排查？
    - D-Q3: 轉址後仍停留舊 feed 的原因與解法？

- 高級者：建議關注哪 15 題
    - B-Q5: Community Server 與 feed 產生的關係為何？
    - B-Q6: syndication.axd 可能的實作機制是什麼？
    - B-Q9: 轉址鏈過長對體驗與 SEO 的影響？
    - B-Q15: 版本控制與回溯如何幫助 feed 遷移？
    - D-Q4: Feed 抓取頻率過高造成負載怎麼辦？
    - D-Q5: FeedBurner 抓取失敗如何診斷？
    - D-Q6: 訂閱統計下滑如何分析與補救？
    - D-Q7: 出現重複文章或排序錯亂怎麼處理？
    - D-Q8: 轉址導致循環重導如何排查？
    - D-Q9: 特定閱讀器無法解析新 feed 怎麼辦？
    - D-Q10: 遷移後 SEO 與外鏈流量下滑如何補救？
    - A-Q10: FeedBurner 與原生 feed 有何差異？
    - A-Q11: 為何保留 FeedBurner 仍可能出現顯示問題？
    - A-Q12: 訂閱者長期不更換 URL 的風險？
    - C-Q7: 如何在網站提供 feed 自動發現（autodiscovery）？