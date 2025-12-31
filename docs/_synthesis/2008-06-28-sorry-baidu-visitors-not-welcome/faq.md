---
layout: synthesis
title: "很抱歉，本站不歡迎來自 [百度] (Baidu.com) 的訪客 !!"
synthesis_type: faq
source_post: /2008/06/28/sorry-baidu-visitors-not-welcome/
redirect_from:
  - /2008/06/28/sorry-baidu-visitors-not-welcome/faq/
postid: 2008-06-28-sorry-baidu-visitors-not-welcome
---

# 很抱歉，本站不歡迎來自 [百度] (Baidu.com) 的訪客 !!

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是網路盜文（抄襲）？
- A簡: 網路盜文是未經授權將他人原創內容複製、轉載，且未標示出處或取得同意的行為，侵害著作權與作者權益。
- A詳: 網路盜文指未經原作者授權或合法授權，將他人原創內容（文章、圖片、程式碼等）直接複製、轉載，且未標示出處或未依授權條款（如 CC 授權）進行的行為。此舉侵害著作權、署名權與可能的經濟利益，也破壞知識生態與創作者意願。本文案例中，作者文章被完整貼到問答平台且未標示出處，即屬典型盜文。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, A-Q6

A-Q2: 什麼是智慧財產權在網路上的基本觀念？
- A簡: 智慧財產權保障創作成果，網路公開不等於放棄權利，使用需依授權、註明出處並尊重作者意志。
- A詳: 智慧財產權（IPR）在網路環境同樣適用。內容公開、免費閱讀，不等於進入公有領域，也不代表可任意複製散佈。合法使用內容需遵守授權條款（例：著作權法例外、CC 授權），遵循署名與不得改作等要求。本文強調「資訊可得不代表可踐踏」，提醒平台與使用者均需尊重著作權，違反者可能需負法律責任或面臨下架處置。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, A-Q5

A-Q3: 為何免費資訊也需尊重著作權？
- A簡: 免費僅指讀取不收費，不影響著作權存在；尊重署名與授權是維繫創作生態與信任的基礎。
- A詳: 免費資訊通常指讀者不需付費即可存取，但著作權仍屬作者所有。即使內容不收費，仍需遵守署名、連結、不得商用或改作等授權規範。尊重著作權能維持創作誘因，避免資源濫用，並促進正向的知識共享。本文作者以案例說明：未標明出處的完整轉載，引發不滿並促成以技術手段抗議。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, A-Q6

A-Q4: 什麼是「百度知道」？
- A簡: 百度知道是問答平台，類似「奇摩知識+」，用戶以回答換取點數，常見引用他文作答的情境。
- A詳: 百度知道為問答社群服務，提供用戶提問、回答、累積點數等機制，屬內容聚合與社群互動型平台。此類平台常見引用外部文章作答的情境，若未遵循著作權與署名規範，容易產生侵權爭議。本文案例即發生在百度知道，原作者文章被不當全文貼上且未註明來源，引發投訴與後續技術抗議。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q6, A-Q18

A-Q5: 什麼是「引用需註明出處」的原則？
- A簡: 合法引用須依授權與合理使用，明確標示作者、來源連結與必要的授權條款，避免構成侵權。
- A詳: 引用他人內容時，除非屬著作權法合理使用範圍，通常需取得授權並清楚標示作者姓名、原文連結、來源網站與授權條款（若有）。即便合理使用，也應避免超量引用、不得影響原作市場。本文案例中，回答者未標示出處、全文複製，已超出合理引用範圍，構成對作者權益的不尊重與可能侵權。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, A-Q3

A-Q6: 本文事件概要是什麼？
- A簡: 作者文章遭問答平台用戶全文貼上且未註明來源，投訴後遭刪留言與無作為，遂以技術手段示意抗議。
- A詳: 作者發現百度知道有用戶將其文章一字不漏貼作答案，未標示出處。作者留言抗議並向站方反映，但多次留言遭刪除，站方亦回覆未違規、未處理。對比過往向 Google 反映即迅速下架，作者深感不滿，採用 ASP.NET HttpModule 技術，對自站內所有從百度連入的訪客先顯示抗議頁 60 秒再導回原頁，以此消極抗議。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q7, A-Q18

A-Q7: 什麼是 ASP.NET HttpModule？
- A簡: HttpModule 是 ASP.NET 要求管線中的可插拔元件，能攔截並處理每個 HTTP 請求與回應的橫切邏輯。
- A詳: ASP.NET HttpModule 實作 IHttpModule 介面，註冊後可在應用程式生命週期的多個事件（例如 BeginRequest、AuthenticateRequest）攔截處理請求。適合實作驗證、記錄、重寫、過濾、導向等橫切關注。本文以 HttpModule 檢查 HTTP_REFERER 是否含 baidu.com，若是則 Server.Transfer 至抗議頁，再返回原目標頁，達成全站一致的行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q1, B-Q2

A-Q8: 使用 HttpModule 的核心價值是什麼？
- A簡: 將跨頁面、全站性的政策（驗證、導向、記錄）集中管理，減少重複與遺漏，易維護與統一。
- A詳: HttpModule 將與單一頁面無關、但需全站一致的邏輯集中實作，例如權限檢查、流量控制、來源判斷、URL 重寫與記錄。此做法可避免在各頁面散落相同程式碼，降低錯漏與維護成本。本文案例用一個模組即套用到所有連結，任何請求都不會「漏網」，充分體現集中式策略的價值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q1, B-Q13

A-Q9: 什麼是 HTTP Referer（HTTP_REFERER）？
- A簡: Referer 是瀏覽器送出的來源頁資訊，表示使用者從哪個頁面點擊連入，常用於分析或限制來路。
- A詳: HTTP Referer 為請求標頭中的可選欄位，記錄引導使用者至當前資源的上一個 URL。ASP.NET 可由 Request.ServerVariables["HTTP_REFERER"] 取得。它能用於流量分析、CSRF 防護與來源限制。本文以 Referer 領域判定是否來自 baidu.com，若是則導向抗議頁。不過需注意 Referer 可能空缺、被隱藏或偽造，判斷時應妥善處理例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q10, D-Q1

A-Q10: 什麼是 Server.Transfer？
- A簡: Server.Transfer 在伺服器端改變處理目標頁，不發新請求，URL 多半不變，狀態留在同一個請求內。
- A詳: Server.Transfer 將目前請求的處理流程轉交至同站內另一資源，屬伺服器端切換，不需往返瀏覽器，因此能保留 HttpContext 與表單資料，速度快且減少重導流量。本文用它把請求送往抗議頁顯示訊息，再返回原目標。需注意相對路徑、查詢參數傳遞與避免迴圈導向，必要時可透過 QueryString 或 Context.Items 帶回目標 URL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q14, D-Q4

A-Q11: AuthenticateRequest 事件是什麼？
- A簡: AuthenticateRequest 在 ASP.NET 管線中負責身分驗證前後的時點，適合進行來源檢查與前置邏輯。
- A詳: AuthenticateRequest 是 ASP.NET HttpApplication 生命週期事件之一，在授權（AuthorizeRequest）前後的序列中執行，通常用於設定使用者主體、執行身分驗證或前置檢查。本文在此事件檢查 Referer，及早攔截並 Transfer 至抗議頁，避免後續頁面負擔。若需更早攔截亦可選 BeginRequest，但 AuthenticateRequest 平衡了時機與上下文可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q1, B-Q13

A-Q12: 所有請求都會經過 HttpModule 嗎？
- A簡: 一般而言動態資源會經過模組；IIS 整合管線可設定所有請求（含靜態）也經過，視組態而定。
- A詳: 在傳統（經典）管線中，ASP.NET 只處理對 .aspx、.ashx 等動態資源的請求；在 IIS7 之後的整合式管線，設定 runAllManagedModulesForAllRequests="true" 可讓所有請求（含靜態檔）經過模組。本文強調「任何 LINK 都跑不掉」的精神，即希冀全站皆受策略控管；實務上需確認 IIS 與 Web.config 的管線設定是否涵蓋預期資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, D-Q2

A-Q13: 為何選擇依據 Referer 判斷來路？
- A簡: Referer 能快速辨識導流來源，不需維護 IP 清單，適用特定來源導向或告示的全站策略。
- A詳: 透過 Referer 判斷來源域名（如含 baidu.com），可在不依賴易變的 IP 清單與不侵入頁面程式下，快速對特定流量施作差異化流程，例如顯示告示頁。與封鎖 IP 相比更彈性、易維護，也避免誤傷不同服務共用的 IP 段。但需處理 Referer 缺失與偽造的情形，並設計安全的後備策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, D-Q1, B-Q10

A-Q14: 依據 Referer 判斷的限制是什麼？
- A簡: Referer 可能為空或被偽造，隱私設定與 HTTPS→HTTP 轉址也會遺失，需有安全後備處理。
- A詳: Referer 非強制欄位，瀏覽器或隱私外掛可移除；從 HTTPS 跳至 HTTP 時亦可能不送出；某些代理會改寫。攻擊者可偽造 Referer 欺騙判斷。因此 Referer 適合作為提示或用於體驗分流，較不宜作為安全邊界。實作時應處理為空情況、避免誤攔，並可採白名單、Cookie 標記與記錄以提升健壯性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q1, B-Q23

A-Q15: 顯示 60 秒抗議頁的用意是什麼？
- A簡: 以短暫延遲與明確訊息傳達立場，同時不永久阻斷閱讀，兼顧抗議表態與使用者可存取性。
- A詳: 抗議頁提供明確敘述與立場，給予從特定來源導入的訪客知悉事件的機會。60 秒延遲能引起注意並表達不滿，但不至於永久封鎖內容，避免對一般讀者造成過度干擾。此設計在抗議與可用性間取得折衷，也降低 SEO 與用戶體驗的負面影響。之後自動回到原目標頁，完成初衷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q7, C-Q3

A-Q16: 為何作者選擇技術手段消極抗議？
- A簡: 正規申訴未獲處理、留言遭刪，技術方式可自主可控地表達不滿，且影響僅限特定來路。
- A詳: 在平台回應不彰、申訴頻遭忽視的情況下，站主採用自身可控的網站層技術，讓從特定來源導入的流量先看到抗議內容，兼顧表態與不過度影響其他來源使用者。此為非對抗性、可逆的策略，可隨時調整或移除，並透過 Web.config 掛載即可全站生效，達到最小實作成本與最大覆蓋面。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q8, C-Q1

A-Q17: Response.Redirect 與 Server.Transfer 有何差異？
- A簡: Redirect 發送 3xx 要求瀏覽器重取新 URL；Transfer 伺服器端切換處理，URL 多不變，效率較高。
- A詳: Response.Redirect 會回傳 302/307 等狀態碼與 Location 標頭，瀏覽器再請求新 URL，會變更位址列並多一次往返。Server.Transfer 僅在伺服器端切換處理管線，不更動瀏覽器 URL，保留同一 HttpContext。本文選擇 Transfer 能快速導向抗議頁並保留狀態；若需顯示新網址或跨站導向，Redirect 較合適。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q14, D-Q3

A-Q18: 本文對 Google 與百度處理的差異為何？
- A簡: 作者稱向 Google 反映即下架侵權頁；向百度反映則留言遭刪且被認定未違規，未採取處置。
- A詳: 依本文敘述，作者曾向 Google 反映博客抄襲，獲迅速關閉侵權頁；此次向百度平台反映類似狀況，卻遭刪除抗議留言，並回覆未違規，未採取下架或更正措施。此對照凸顯平台治理與著作權處理流程差異，引發作者採用技術抗議。此為案例描述，非普遍性結論，旨在提醒平台應建立明確可回應的處理機制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q19, D-Q10

A-Q19: 為何平台的著作權治理很重要？
- A簡: 平台處理申訴的效率與公平性影響創作者信任、內容品質與社群風氣，關乎生態長遠健康。
- A詳: UGC 平台承載龐大內容，若缺乏有效侵權識別與申訴機制，盜文會侵蝕西者權益並打擊創作意願，最終降低內容品質。透明、可預期、可追蹤的處理流程，能維持社群秩序、避免惡性競逐。本文案例反映平台回應不彰帶來的挫折，也顯示創作者可能轉而採技術防線，這對體驗與生態均非最佳解。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, D-Q10, A-Q5

A-Q20: 以 HttpModule 實作站點級策略有何好處？
- A簡: 一次掛載，全站生效；集中管理、可測、可維護，便於快速啟閉與擴展策略與規則。
- A詳: HttpModule 是橫切邏輯的理想載體：只需在 Web.config 註冊，便可作用於全站請求。策略調整（如新增白名單、延遲秒數）集中於一處，降低修改風險。亦可加入記錄、A/B 測試與動態配置，提升可運維性。本文以一個模組達成從特定來源導向告示頁的需求，展示其敏捷與覆蓋能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q8, C-Q10

A-Q21: 面對侵權事件，有哪些正規處理管道？
- A簡: 蒐證、聯繫對方、向平台申訴、引用法規條款要求下架，必要時尋求法律協助或發函。
- A詳: 正規處理流程包含：保留證據（截圖、時間戳）、與侵權方聯繫、向平台提交申訴與授權證明、引用當地法規（如通知移除）請求下架、追蹤進度。若未果，可尋求律師意見或寄發法律函件。本文案例先走平台申訴與溝通，未獲回應後才採技術抗議，顯示仍以正規路徑為先。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q19, D-Q10

A-Q22: 為何不直接封鎖 IP 或 User-Agent？
- A簡: IP 易變且共享，誤傷風險高；User-Agent 易偽造。Referer 更貼近導流來源，管理較彈性。
- A詳: 基於 IP 的封鎖可能誤攔共享或動態位址；CDN、NAT 也會混淆來源。User-Agent 字串可任意偽造，可信度低。Referer 雖非安全訊號，但反映導流來源，較適合體驗分流與告示用途。若需更嚴格策略，可綜合白名單、簽章連結與行為檢測，平衡準確性與可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q15, D-Q7

A-Q23: 這樣的抗議做法對 SEO 可能有何影響？
- A簡: 若搜尋引擎爬蟲被導向非內容頁或大量 3xx/非預期內容，可能影響收錄與排名，需要謹慎處理。
- A詳: 若模組誤將搜尋引擎爬蟲（bot）導至抗議頁，可能導致內容抓取受阻、索引品質下降。Server.Transfer 不回傳 3xx，但內容變了也可能造成「軟 404」或品質評估降低。可用 User-Agent 白名單、僅對人類流量顯示、對抗議頁加上 noindex，以及避免對主要內容頁做永久阻擋，降低風險。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q14, D-Q6, C-Q4

A-Q24: 本案例帶給開發者的啟示是什麼？
- A簡: 技術可作為表態與風控工具，但應以正規申訴為先；實作需兼顧體驗、SEO 與可維護性。
- A詳: 案例顯示：當平台治理不足時，站方仍可用技術保護自身立場與權益。選擇 HttpModule 可快速部署全站策略，但需考量 Referer 可靠性、導向迴圈、靜態資源、白名單、記錄與 SEO 等面向。原則上，以正規申訴與溝通優先，技術做為輔助與暫時性方案，確保不過度傷害正常使用者體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q20, D-Q3


### Q&A 類別 B: 技術原理類

B-Q1: HttpModule 在 ASP.NET 要求管線中的運作原理是什麼？
- A簡: 模組掛入 HttpApplication 事件，攔截請求與回應，執行橫切邏輯；順序由註冊與管線決定。
- A詳: ASP.NET 將請求交由 HttpApplication 執行生命週期事件（BeginRequest→AuthenticateRequest→AuthorizeRequest→…→EndRequest）。HttpModule 透過 Init 註冊對這些事件的處理器，以攔截與處理請求/回應。多個模組依註冊順序與管線模式決定先後。本文模組在 AuthenticateRequest 檢查 Referer 並 Server.Transfer。核心組件：IHttpModule、HttpApplication、HttpContext。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q11, B-Q13

B-Q2: AuthenticateRequest 的執行流程與適用情境？
- A簡: 於驗證階段觸發，常用於設定使用者主體、前置檢查、來源判斷與早期攔截，提高效率。
- A詳: AuthenticateRequest 在建立管線物件後、授權前觸發。其優點是上下文已就緒、但尚未執行頁面邏輯，適合做粗粒度策略：來源判斷、A/B 分流、黑白名單、主體設定。本文利用此時點檢查 HTTP_REFERER，減少後續頁面開銷。若需更早處理（含 URL 重寫）可用 BeginRequest；需憑權限資訊則可用 AuthorizeRequest。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q1, B-Q13

B-Q3: 解析 HTTP_REFERER 的機制與注意事項？
- A簡: 從 ServerVariables 或 Headers 取值，可能為空或不合法，需先檢查後再用 Uri 安全解析。
- A詳: 在 ASP.NET 可從 Request.ServerVariables["HTTP_REFERER"] 或 Request.UrlReferrer 取得來源；值可能為 null、空字串或格式不正確。正確流程：先檢查非空，再以 Uri.TryCreate 解析；僅使用 Host 做比對，避免路徑誤判；比較時採不區分大小寫與文化的方式（ToUpperInvariant 或 OrdinalIgnoreCase）。必要時記錄原始值以利診斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q11, D-Q1

B-Q4: 如何安全比對來源域名（如 baidu.com）？
- A簡: 以 Uri.Host 取主機名，做尾段比對和子網域處理，避免僅用 Contains 造成誤判與旁路。
- A詳: 取得 Uri.Host 後，建議採「結尾比對」與點分隔檢查，例如 host==baidu.com 或 host.EndsWith(".baidu.com")。避免字串 Contains 造成 foo-notbaidu.com 被誤判。對國際或多 TLD（baidu.com.cn）需配置化清單。可先標準化大小寫，並移除尾端點號。此流程提升準確與安全。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q22, D-Q3

B-Q5: Server.Transfer 的內部機制與行為？
- A簡: 伺服器端將執行管線切換到新 Handler，保持同一 HttpContext，不修改瀏覽器 URL。
- A詳: 呼叫 Server.Transfer 時，ASP.NET 將目前 HttpContext 與 Request 交給新的 IHttpHandler（例如新 .aspx 頁），不經瀏覽器重送。原始表單與上下文可用；URL 大多不變。可透過 Server.Transfer("url", preserveForm: true) 或加入 QueryString 傳遞目標資訊。缺點是相對路徑解析與瀏覽器顯示不一致，需注意避免混淆與 SEO 影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q14, D-Q4

B-Q6: 如何保留原請求目標，以便抗議頁後導回？
- A簡: 以 QueryString 搭配 UrlEncode 帶 returnUrl，或存於 Context.Items/Session，再由前端取用跳轉。
- A詳: 常見方案：1) Server.Transfer 至抗議頁時附帶 ?returnUrl=UrlEncode(Request.RawUrl)；抗議頁以 JS setTimeout 後 window.location=returnUrl。2) 以 Context.Items["returnUrl"]=Request.RawUrl；抗議頁從 Context 取值（需同一請求）。3) 存 Session/Cookie，跨請求可用。QueryString最直觀、可跨請求且可記錄，實作簡單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q7, C-Q3

B-Q7: 抗議頁自動跳回的機制是什麼？
- A簡: 前端用 JavaScript setTimeout 或 <meta http-equiv="refresh">，等待秒數後導向 returnUrl。
- A詳: 抗議頁載入後，以 JS 計時：setTimeout(()=>location.href=returnUrl, 60000)。returnUrl 由 QueryString 帶入並 decode；另可用 meta refresh content="60;url=..." 作為無 JS 備援。顯示期間提供案情說明、尊重著作權訴求與操作選項。為避免 SEO 影響，可加上 noindex。並應驗證 returnUrl 避免開放式重導。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, C-Q3, D-Q3

B-Q8: 如何在 Web.config 註冊 HttpModule（經典/整合管線）？
- A簡: 經典用 <httpModules>，整合式用 <modules>；若需涵蓋靜態檔，加 runAllManagedModulesForAllRequests。
- A詳: 在 ASP.NET 2.0（經典）於 system.web/httpModules 新增 <add name="SiteBlocker" type="..."/>。IIS7 整合式在 system.webServer/modules 註冊。若要讓所有資源經過模組，於 system.webServer/modules 加上 runAllManagedModulesForAllRequests="true"。不同環境需確保兩處都正確配置並測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q2, D-Q2

B-Q9: 靜態資源請求如何經過模組處理？
- A簡: 需啟用整合式管線或 URL Rewrite/Handler 映射，否則經典模式僅動態資源會進入 ASP.NET。
- A詳: 經典模式下，IIS 將靜態檔（.jpg、.css）直接回應，不進入 ASP.NET。整合式管線可讓所有請求進入 Managed Pipeline；或透過重寫與映射讓靜態路徑進 ASP.NET。若策略僅針對頁面可無須涵蓋靜態，但若抗議頁需攔截所有資源以避免「漏出內容」，建議使用整合式並啟用全請求模式。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q8, D-Q2

B-Q10: Referer 為空或偽造時的處理原則？
- A簡: 將 Referer 視為提示而非安全邊界；空值預設放行並記錄，偽造應結合白名單與行為檢測。
- A詳: 因 Referer 不可靠，建議：空值或不合法時採保守放行，並記錄來源 IP/UA 以觀察；對已知可信來源採白名單通行；對「含特定來源」採弱提示邏輯（顯示告示）；不以 Referer 作為安全驗證。必要時加入 CSRF Token、簽章連結、Cookie 標記等機制輔助辨識，提升整體韌性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q1, B-Q23

B-Q11: ToUpperInvariant/不分文化比較的必要性？
- A簡: 網域比較需文化無關、大小寫無關，以避免特定文化規則改變字元行為造成誤判。
- A詳: .NET 字串在不同文化可能有大小寫轉換差異（例如土耳其語 i/I）。為精準比對域名，應使用 OrdinalIgnoreCase 或先以 ToUpperInvariant 正規化後比較，避免文化敏感性問題。本文範例使用 ToUpperInvariant 再 Contains，實務上建議改為 OrdinalIgnoreCase 的 EndsWith 比較以更安全。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q4, D-Q3, C-Q1

B-Q12: 如何註冊事件處理器（context.AuthenticateRequest += ...）？
- A簡: 在 Init 傳入的 HttpApplication 上掛事件委派，使模組在對應生命週期接收回呼處理請求。
- A詳: 實作 IHttpModule.Init(HttpApplication context) 後，於該方法中以 context.AuthenticateRequest += new EventHandler(Handler) 註冊處理器。這讓模組得以在每次請求的該事件時點執行自定邏輯。注意避免閉包抓取不必要資源，釋放需釋放的物件，並在 Dispose 實作必要清理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, C-Q1

B-Q13: 多個模組的執行順序與相互影響？
- A簡: 順序受註冊先後與管線決定；後續模組可能受前序變更影響，需避免相互干擾與迴圈。
- A詳: 模組在每個事件的呼叫順序通常依註冊順序決定。若前序模組修改了 HttpContext（例如重寫路徑、設定 Items），後續模組需相容處理。導向或 Transfer 會中止後續頁面處理，但其他模組仍可能已執行部分邏輯。建議明確規範順序、檢查路徑避免對抗議頁再次導向、並加入短路條件以防迴圈。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q3, C-Q8, B-Q1

B-Q14: Server.Transfer 對 SEO 與狀態碼的影響？
- A簡: Transfer 不回 3xx，搜尋引擎可能看到非預期內容，需避免對爬蟲生效或加上 noindex。
- A詳: 因為 Transfer 不改變狀態碼與 URL，爬蟲可能把抗議頁內容視為原頁，影響收錄品質。對 SEO 敏感頁面應避免 Transfer 干預內容，或對已識別的 bot 放行，對抗議頁加入 noindex、nofollow。若需顯示不同 URL，使用 Redirect 更合適，且可配合 302 表示暫時性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, A-Q23, D-Q6

B-Q15: 黑名單/白名單策略該如何設計？
- A簡: 將可疑來源列黑名單導入告示頁，可信來源列白名單放行，清單配置化並可動態更新。
- A詳: 將來源域名清單配置在 appSettings 或外部設定（JSON/DB），啟動時載入，運行中可熱更新。比對時先檢查白名單（放行），再檢查黑名單（導向）。可搭配權重與過期時間。記錄命中統計以調整策略。此模式讓策略調整無需重新部署，維護成本低。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q8, B-Q4

B-Q16: 如何在模組中做日誌紀錄與觀察？
- A簡: 記錄來源域名、UA、IP、目標 URL、時間與處置結果，便於追蹤成效與調整策略。
- A詳: 於命中條件時，寫入結構化日誌（JSON）包含 referer、parsedHost、requestUrl、returnUrl、userAgent、clientIp、action（blocked/notice/shown）等。可用 System.Diagnostics.Trace、log4net、Serilog。定期彙整儀表板觀察趨勢與誤攔比，持續調整清單與規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q8, B-Q20

B-Q17: 如何只顯示一次抗議頁（Cookie 控制）？
- A簡: 設置短期 Cookie 標記已顯示，後續請求檢查 Cookie 放行，平衡體驗與表態頻率。
- A詳: 模組在命中來源時先檢查特定 Cookie（如 protest_shown=1），若已存在則放行；否則導向抗議頁並於回應寫入 Cookie（設有效期數小時或一天）。此作法減少重複打擾，並可配合白名單避免關鍵頁面顯示。需注意跨子域名 Cookie 範圍設定與用戶隱私告知。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q3, B-Q15

B-Q18: 模組的可測試性如何提升？
- A簡: 抽象化時間、設定與環境相依性，注入介面；以模擬 HttpContext 單元測試條件分支。
- A詳: 以介面封裝設定來源（IConfig）、時間提供者（IClock）、記錄器（ILogger），以依賴注入傳入模組。將判斷函數抽出為純函式，方便單測。測試時可用 HttpContext 模擬器或自建測試 HttpApplication，注入不同 Referer/UA/URL 驗證行為。避免靜態狀態，降低耦合。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q7, B-Q20, D-Q8

B-Q19: 執行緒安全與狀態管理注意什麼？
- A簡: 避免使用靜態可變共享狀態；每請求用 HttpContext；共享資料採唯讀或鎖定與原子更新。
- A詳: 模組可能同時被多執行緒呼叫，應避免非同步安全的靜態集合或變數。設定資料應唯讀或使用 Concurrent 容器；熱更新需採換引用策略。每請求資料放在 HttpContext.Items。寫日誌需非阻塞。確保 Dispose 正確釋放非託管資源。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q18, C-Q10, D-Q8

B-Q20: 效能與延遲如何最小化？
- A簡: 簡化判斷、避免同步 IO、使用快取與預先編譯 Regex，記錄採非阻塞，減少字串配置。
- A詳: 核心路徑使用 O(1) 邏輯：快速檢查空 Referer，Host 取值與尾段比對；清單緩存到記憶體；字串比較用 OrdinalIgnoreCase；必要 Regex 預編譯。日誌非同步批次寫入。避免在模組內做遠端呼叫或重 IO。壓測驗證延遲影響與吞吐能力。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q8, B-Q16, C-Q6

B-Q21: 在反向代理/負載平衡下有何差異？
- A簡: 來源 IP/標頭可能被改寫，需信任清單與從 X-Forwarded-* 取得資訊，並確認 Referer 傳遞。
- A詳: 經過代理時，客戶端 IP 由 X-Forwarded-For 提供；Referer 一般會原樣轉發，但某些中介會清除或規範化。應設定可信代理清單，僅在可信來源時採用轉發標頭。記錄時同時保存原始與解析後資訊，便於追蹤。對 HTTPS 終止點亦需驗證安全性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q7, B-Q10, B-Q16

B-Q22: 如何處理多 TLD 與子域名的來源比對？
- A簡: 構建可配置的網域集合（含主域與子域），以精準尾段比對，避免誤判與漏判。
- A詳: 將來源網域清單設計為集合，如 ["baidu.com","baidu.com.cn","baidu.hk"]。比對流程：Normalize(host)→若 host==域名或 host.EndsWith("."+域名) 則命中。可加入通配規則與排除清單。維護時以設定檔更新，避免硬編碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q10, D-Q3

B-Q23: 例外處理與 Fail-safe 設計？
- A簡: 任何解析或導向失敗時應放行原請求並記錄，避免把網站變磚或造成大面積阻斷。
- A詳: 針對 Uri 解析失敗、字串操作例外、Transfer 例外等，捕捉後記錄詳細上下文並放行，以確保可用性優先。避免在例外中再次導向造成迴圈。可設全域開關快速停用策略。健康檢查與監控能即時發現異常行為比例異常，降低風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q4, D-Q3, C-Q9


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何實作 SiteBlockerHttpModule？
- A簡: 建立類別實作 IHttpModule，在 Init 掛 AuthenticateRequest 事件，解析 Referer 命中後 Transfer 至抗議頁。
- A詳: 
  - 具體步驟:
    1) 新增類別 SiteBlockerHttpModule: IHttpModule。
    2) 在 Init 掛 context.AuthenticateRequest。
    3) 取 HTTP_REFERER，Uri.TryCreate 解析 Host。
    4) 尾段比對 baidu.com 系列網域。
    5) 命中則 Server.Transfer("~/Blogs/ShowBlockedMessage.aspx?returnUrl="+UrlEncode(Request.RawUrl)).
  - 關鍵程式碼:
    ```csharp
    public class SiteBlockerHttpModule : IHttpModule {
      public void Init(HttpApplication app) {
        app.AuthenticateRequest += OnAuth;
      }
      void OnAuth(object s, EventArgs e) {
        var app = (HttpApplication)s;
        var ctx = app.Context;
        var refStr = ctx.Request.ServerVariables["HTTP_REFERER"];
        if (!string.IsNullOrEmpty(refStr) &&
            Uri.TryCreate(refStr, UriKind.Absolute, out var u)) {
          var host = u.Host;
          if (host.Equals("baidu.com", StringComparison.OrdinalIgnoreCase) ||
              host.EndsWith(".baidu.com", StringComparison.OrdinalIgnoreCase)) {
            var ret = HttpUtility.UrlEncode(ctx.Request.RawUrl);
            ctx.Server.Transfer("~/Blogs/ShowBlockedMessage.aspx?returnUrl=" + ret);
          }
        }
      }
      public void Dispose() { }
    }
    ```
  - 注意事項: 使用尾段比對，避免 Contains 誤判；處理參數編碼，避免開放式重導。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q4, C-Q8

C-Q2: 如何在 Web.config 註冊 HttpModule？
- A簡: 在 system.web/httpModules 與 system.webServer/modules 註冊，整合式可啟 runAllManagedModulesForAllRequests。
- A詳:
  - 具體步驟:
    1) system.web/httpModules 加入：
       ```xml
       <httpModules>
         <add name="SiteBlocker" type="MyApp.SiteBlockerHttpModule"/>
       </httpModules>
       ```
    2) system.webServer/modules 加入：
       ```xml
       <modules runAllManagedModulesForAllRequests="true">
         <add name="SiteBlocker" type="MyApp.SiteBlockerHttpModule"/>
       </modules>
       ```
  - 注意事項: 避免重複註冊造成兩次觸發；在整合式管線用 system.webServer；測試動靜態涵蓋。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, B-Q9, D-Q2

C-Q3: 如何實作 ShowBlockedMessage.aspx 與 60 秒自動返回？
- A簡: 把 returnUrl 帶入頁面，顯示訊息與倒數，用 JS setTimeout 與 meta refresh 60 秒後導回。
- A詳:
  - 步驟:
    1) 建立 ShowBlockedMessage.aspx，讀取 Request["returnUrl"]。
    2) 顯示抗議文字與倒數。
    3) 用 JS/Meta 實作延遲導回。
  - 程式碼片段:
    ```aspx
    <%@ Page Language="C#" %>
    <script runat="server">
      protected string ReturnUrl;
      protected void Page_Load(object s, EventArgs e) {
        ReturnUrl = HttpUtility.UrlDecode(Request["returnUrl"] ?? "/");
        // 安全檢查：僅允許站內路徑
        if (!ReturnUrl.StartsWith("/", StringComparison.Ordinal)) ReturnUrl = "/";
      }
    </script>
    <html><head>
      <meta name="robots" content="noindex,nofollow" />
      <meta http-equiv="refresh" content="60;url=<%= ReturnUrl %>" />
      <script>
        setTimeout(function(){location.href = "<%= ReturnUrl %>";}, 60000);
      </script>
    </head>
    <body>
      <h1>尊重智慧財產權</h1>
      <p>本頁為告示，60 秒後將返回：<%= Server.HtmlEncode(ReturnUrl) %></p>
    </body></html>
    ```
  - 注意: 驗證 returnUrl 僅站內路徑，避免開放式重導。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q6, D-Q3

C-Q4: 如何加上白名單放行特定來源或路徑？
- A簡: 於設定加入白名單網域/路徑，命中時略過導向；配置化便於動態調整，減少誤攔。
- A詳:
  - 步驟:
    1) 在 web.config appSettings 定義 WhitelistDomains、WhitelistPaths。
    2) 模組啟動時解析清單。
    3) 事件中先檢查白名單命中則放行。
  - 程式碼片段:
    ```csharp
    var whitePaths = new[] { "/health", "/sitemap.xml" };
    if (whitePaths.Any(p => ctx.Request.Path.StartsWith(p, StringComparison.OrdinalIgnoreCase)))
      return; // 放行
    ```
  - 注意: 白名單優先於黑名單；維持最小集合，定期檢視命中日誌調整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, B-Q16, D-Q6

C-Q5: 如何用 Cookie 只顯示一次抗議頁？
- A簡: 檢查特定 Cookie，不存在才顯示；顯示時設定短期 Cookie，後續請求直接放行。
- A詳:
  - 步驟:
    1) 讀取 Request.Cookies["protest_shown"]。
    2) 若無且命中來源，導向抗議頁，並在 Response.Cookies 設置。
    3) 已存在則放行。
  - 程式碼:
    ```csharp
    var shown = ctx.Request.Cookies["protest_shown"]?.Value == "1";
    if (!shown && IsFromBaidu(host)) {
      ctx.Response.Cookies.Add(new HttpCookie("protest_shown","1"){ Expires=DateTime.UtcNow.AddHours(12) });
      ctx.Server.Transfer("~/Blogs/ShowBlockedMessage.aspx?returnUrl=" + ret);
    }
    ```
  - 注意: 設定 Cookie 範圍（Domain/Path），尊重隱私並提供說明。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, D-Q3, C-Q3

C-Q6: 如何加入日誌紀錄與監控？
- A簡: 在命中與放行處記錄關鍵欄位，輸出至檔案或觀測平台，建立儀表板監看趨勢。
- A詳:
  - 步驟:
    1) 設計日誌模型（referer、host、path、action、ip、ua）。
    2) 以 Serilog 或內建 Trace 寫出 JSON。
    3) 配置收集與可視化（ELK、Seq）。
  - 程式碼:
    ```csharp
    Log.Information("block={block} ref={ref} host={host} url={url} ip={ip}",
      blocked, refStr, host, ctx.Request.RawUrl, ctx.Request.UserHostAddress);
    ```
  - 注意: 避免同步 IO；敏感資訊脫敏；保留取樣降低開銷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, B-Q20, D-Q8

C-Q7: 如何為模組撰寫單元測試？
- A簡: 抽出判斷函式，使用模擬 HttpContext 載入不同 Referer/URL，驗證是否導向或放行。
- A詳:
  - 步驟:
    1) 抽出 IsFromBlockedSource(Uri u) 與 ShouldShowProtest(ctx)。
    2) 使用自訂 HttpContext 假件或第三方模擬器建構測資。
    3) 驗證命中/白名單/空 Referer 等分支。
  - 片段:
    ```csharp
    Assert.True(IsFromBlockedSource(new Uri("https://zhidao.baidu.com/...")));
    Assert.False(IsFromBlockedSource(new Uri("https://www.google.com")));
    ```
  - 注意: 避免依賴靜態時間與環境，注入設定物件。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q18, D-Q2, C-Q1

C-Q8: 如何避免迴圈導向（抗議頁再被攔）？
- A簡: 在模組中檢查當前路徑是否抗議頁，命中即放行；或加旗標於 Context.Items。
- A詳:
  - 步驟:
    1) 若 Request.Path.StartsWith("~/Blogs/ShowBlockedMessage.aspx") 則直接 return。
    2) 或於初次命中時設置 Context.Items["ProtestHandled"]=true，後續檢查存在則放行。
  - 程式碼:
    ```csharp
    if (ctx.Request.Path.IndexOf("ShowBlockedMessage.aspx", StringComparison.OrdinalIgnoreCase)>=0) return;
    if (ctx.Items["ProtestHandled"]!=null) return;
    ctx.Items["ProtestHandled"]=true;
    ```
  - 注意: 配合 Cookie 一次性策略更穩妥；撰寫測試涵蓋此情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, B-Q13, C-Q3

C-Q9: 如何部署並驗證模組生效？
- A簡: 部署至 IIS，確認管線與 Web.config 註冊；用不同 Referer 模擬測試命中、白名單與放行。
- A詳:
  - 步驟:
    1) 發佈網站至測試環境。
    2) 確認 AppPool 為整合式（若需全請求）。
    3) 以 curl 或瀏覽器外掛設定 Referer 測試。
    4) 檢查日誌與瀏覽器行為。
  - 測試:
    ```bash
    curl -H "Referer: https://zhidao.baidu.com/q" https://your.site/path
    ```
  - 注意: 驗證 bot 放行、靜態資源行為、性能指標與回退開關。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q2, B-Q20

C-Q10: 如何擴展為多來源可配置阻擋？
- A簡: 將來源清單外部化（JSON/DB），開機載入並緩存，支援熱更新與權重優先順序。
- A詳:
  - 步驟:
    1) 定義設定模型：BlockDomains、AllowDomains、ExcludePaths。
    2) 啟動時讀入設定，監控變更事件。
    3) 判斷流程：先白名單→黑名單→其他規則。
  - 片段:
    ```csharp
    class BlockConfig { public string[] BlockDomains; public string[] AllowDomains; }
    var cfg = JsonConvert.DeserializeObject<BlockConfig>(File.ReadAllText("block.json"));
    ```
  - 注意: 版本控管設定檔，更新時採用雙緩存切換，記錄命中以回饋調整。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, B-Q20, C-Q6


### Q&A 類別 D: 問題解決類（10題）

D-Q1: Referer 為空導致無法判斷怎麼辦？
- A簡: 將空 Referer 視為非命中並放行，同時記錄觀察；避免因嚴格策略誤攔正常流量。
- A詳:
  - 症狀: 許多請求無 Referer 值，無法識別來源。
  - 原因: 隱私設定、HTTPS→HTTP、代理清除或瀏覽器策略。
  - 解決步驟: 空值放行、記錄比例；必要時僅對明確命中來源顯示告示；避免把 Referer 當安全依據。
  - 預防: 文件化策略、加白名單與 Cookie 控制，降低打擾與誤攔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q10, C-Q6

D-Q2: 模組似乎沒有生效或不觸發怎麼診斷？
- A簡: 檢查 Web.config 註冊位置、IIS 管線模式與部署環境，利用日誌與最小重現驗證。
- A詳:
  - 症狀: 來源命中也未導向抗議頁。
  - 可能原因: 註冊在錯誤節點、IIS 經典/整合管線不符、程式未部署、命名空間錯誤。
  - 解決步驟: 檢查 system.web/httpModules 與 system.webServer/modules；確認 AppPool 模式；加入日誌；建立簡單頁測試。
  - 預防: 加入啟動健康檢查與部署清單，持續整合測試配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, C-Q9

D-Q3: 出現無限導向迴圈時怎麼辦？
- A簡: 為抗議頁與處理過請求加放行條件，並使用 Cookie 一次性顯示，防止重複進入。
- A詳:
  - 症狀: 抗議頁載入後再次被模組攔截，無法返回原頁。
  - 原因: 模組未排除抗議頁路徑或缺乏處理旗標。
  - 解決步驟: 檢查 Path 排除；設定 Context.Items["ProtestHandled"]；加 Cookie 控制；驗證 returnUrl 安全。
  - 預防: 單元測試涵蓋；日誌監控導向次數異常告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, B-Q13, C-Q5

D-Q4: Server.Transfer 拋出路徑類型錯誤如何處理？
- A簡: 確保使用應用程式相對路徑與正確語法，必要時改用 ResolveUrl 或 Response.Redirect。
- A詳:
  - 症狀: HttpException「路徑須為應用程式相對」。
  - 原因: 傳入絕對 URL 或不正確相對路徑。
  - 解決步驟: 使用 "~/" 開頭路徑；避免外部 URL；如需跨站導向改用 Redirect；傳遞 returnUrl 用 QueryString。
  - 預防: 封裝 TransferHelper，統一處理與驗證路徑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q3, A-Q10

D-Q5: 使用者直接輸入網址繞過抗議頁怎麼辦？
- A簡: 抗議頁只針對來源導流體驗，直接存取屬正常；若需更嚴格，需改採驗證或權限控制。
- A詳:
  - 症狀: 直接輸入 URL 可不經抗議頁。
  - 原因: 策略以 Referer 為依據，非強制封鎖。
  - 解決步驟: 明確定位為告示功能無需處理；若要強制，需引入登入、權限或簽章鏈接等。
  - 預防: 文件化策略目標，避免誤解；對特定敏感頁另設保護。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q10, A-Q23

D-Q6: 抗議頁影響 SEO 或收錄下降怎麼辦？
- A簡: 對爬蟲放行、抗議頁標註 noindex，必要時僅對人類流量顯示或縮短停留時間。
- A詳:
  - 症狀: 搜尋流量下降、收錄異常。
  - 原因: 爬蟲取得抗議頁而非內容頁，或視為低品質。
  - 解決步驟: 檢測 UA 白名單放行 bot；抗議頁加 noindex；用 302 Redirect 替代 Transfer（依需求）。
  - 預防: 定期 Search Console 監看；A/B 小流量測試策略變更。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q14, A-Q23, C-Q4

D-Q7: 經過 CDN/代理後 Referer/標頭異常怎麼調整？
- A簡: 與 CDN 同步設定轉發規則，使用可信代理清單與 X-Forwarded-*，並調整策略容錯。
- A詳:
  - 症狀: Referer 消失或被改寫、來源判斷錯誤。
  - 原因: 代理移除隱私性標頭或重新封包。
  - 解決步驟: 與 CDN 配置保留/轉發 Referer；使用可信代理名單；從 X-Forwarded-Proto 等補充資訊。
  - 預防: 變更前壓測與灰度發布，監控異常比例。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q21, B-Q10, C-Q9

D-Q8: 高流量下效能不佳怎麼優化？
- A簡: 優化比對邏輯與資料結構、啟用快取與非同步日誌、剖析熱點並移除同步阻塞。
- A詳:
  - 症狀: CPU 飆高、延遲增加。
  - 原因: 重 IO、頻繁字串配置、同步日誌、Regex 過重。
  - 解決步驟: 用尾段比對取代 Regex；預先載入清單；非同步批次日誌；壓測與剖析定位瓶頸。
  - 預防: 性能守門檻、自動化壓測，持續觀測延遲指標。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q20, C-Q6, B-Q16

D-Q9: URL 編碼或多語系導致 returnUrl 錯亂？
- A簡: 統一使用 UrlEncode/Decode 與 UTF-8，回傳前 HTML 編碼顯示，避免路徑與 XSS 問題。
- A詳:
  - 症狀: 返回 URL 亂碼或導向失敗。
  - 原因: 未正確編碼/解碼，或混用編碼。
  - 解決步驟: 傳遞前 HttpUtility.UrlEncode；頁面端 UrlDecode；輸出前 Server.HtmlEncode；限制僅站內路徑。
  - 預防: 加入編碼測試用例，跨語系驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q6, D-Q3

D-Q10: 面對平台處理申訴不力時的綜合對策？
- A簡: 持續蒐證與申訴、公開透明溝通、採技術輔助、必要時法律途徑，兼顧體驗與比例原則。
- A詳:
  - 症狀: 申訴無回應、留言被刪。
  - 原因: 平台流程缺陷或執行不彰。
  - 解決步驟: 蒐證；再次提交並要求書面回覆；公開聲明；採技術告示保護立場；評估法律協助。
  - 預防: 在網站標示授權條款、加註來源要求，建立聯絡管道與範本文字。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q21, A-Q19, A-Q6


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是網路盜文（抄襲）？
    - A-Q2: 什麼是智慧財產權在網路上的基本觀念？
    - A-Q3: 為何免費資訊也需尊重著作權？
    - A-Q4: 什麼是「百度知道」？
    - A-Q5: 什麼是「引用需註明出處」的原則？
    - A-Q6: 本文事件概要是什麼？
    - A-Q7: 什麼是 ASP.NET HttpModule？
    - A-Q9: 什麼是 HTTP Referer（HTTP_REFERER）？
    - A-Q10: 什麼是 Server.Transfer？
    - A-Q11: AuthenticateRequest 事件是什麼？
    - A-Q15: 顯示 60 秒抗議頁的用意是什麼？
    - C-Q2: 如何在 Web.config 註冊 HttpModule？
    - C-Q3: 如何實作 ShowBlockedMessage.aspx 與 60 秒自動返回？
    - D-Q1: Referer 為空導致無法判斷怎麼辦？
    - D-Q2: 模組似乎沒有生效或不觸發怎麼診斷？

- 中級者：建議學習哪 20 題
    - A-Q8: 使用 HttpModule 的核心價值是什麼？
    - A-Q12: 所有請求都會經過 HttpModule 嗎？
    - A-Q13: 為何選擇依據 Referer 判斷來路？
    - A-Q17: Response.Redirect 與 Server.Transfer 有何差異？
    - A-Q20: 以 HttpModule 實作站點級策略有何好處？
    - B-Q1: HttpModule 在 ASP.NET 要求管線中的運作原理是什麼？
    - B-Q2: AuthenticateRequest 的執行流程與適用情境？
    - B-Q3: 解析 HTTP_REFERER 的機制與注意事項？
    - B-Q4: 如何安全比對來源域名（如 baidu.com）？
    - B-Q5: Server.Transfer 的內部機制與行為？
    - B-Q6: 如何保留原請求目標，以便抗議頁後導回？
    - B-Q7: 抗議頁自動跳回的機制是什麼？
    - B-Q8: 如何在 Web.config 註冊 HttpModule（經典/整合管線）？
    - B-Q15: 黑名單/白名單策略該如何設計？
    - B-Q16: 如何在模組中做日誌紀錄與觀察？
    - C-Q1: 如何實作 SiteBlockerHttpModule？
    - C-Q5: 如何用 Cookie 只顯示一次抗議頁？
    - C-Q8: 如何避免迴圈導向（抗議頁再被攔）？
    - C-Q9: 如何部署並驗證模組生效？
    - D-Q3: 出現無限導向迴圈時怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q23: 這樣的抗議做法對 SEO 可能有何影響？
    - A-Q24: 本案例帶給開發者的啟示是什麼？
    - B-Q9: 靜態資源請求如何經過模組處理？
    - B-Q10: Referer 為空或偽造時的處理原則？
    - B-Q11: ToUpperInvariant/不分文化比較的必要性？
    - B-Q13: 多個模組的執行順序與相互影響？
    - B-Q14: Server.Transfer 對 SEO 與狀態碼的影響？
    - B-Q18: 模組的可測試性如何提升？
    - B-Q19: 執行緒安全與狀態管理注意什麼？
    - B-Q20: 效能與延遲如何最小化？
    - B-Q21: 在反向代理/負載平衡下有何差異？
    - B-Q22: 如何處理多 TLD 與子域名的來源比對？
    - B-Q23: 例外處理與 Fail-safe 設計？
    - D-Q6: 抗議頁影響 SEO 或收錄下降怎麼辦？
    - D-Q8: 高流量下效能不佳怎麼優化？