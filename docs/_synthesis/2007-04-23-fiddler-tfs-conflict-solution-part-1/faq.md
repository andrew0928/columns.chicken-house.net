---
layout: synthesis
title: "Fiddler 跟 TFS 相衝的問題解決 - I"
synthesis_type: faq
source_post: /2007/04/23/fiddler-tfs-conflict-solution-part-1/
redirect_from:
  - /2007/04/23/fiddler-tfs-conflict-solution-part-1/faq/
---

# Fiddler 跟 TFS 相衝的問題解決 - I（FAQ 重組）

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Fiddler？
- A簡: Fiddler 是 HTTP 除錯代理，攔截並檢視應用程式發出的 HTTP/HTTPS 流量。
- A詳: Fiddler 是一套以系統代理方式運作的 HTTP(S) 封包除錯工具。它會將自己設成系統 Proxy，讓來自瀏覽器或應用程式的 HTTP/HTTPS 請求先經過 Fiddler，再轉送至目的伺服器。開發者可檢視、篩選、修改請求與回應，快速定位問題，特別適合 AJAX、Web API、OAuth/認證等無法從「檢視原始碼」看出的互動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1, C-Q2

A-Q2: 什麼是 TFS（Team Foundation Server）與 VS2005 的關聯？
- A簡: TFS 是微軟 ALM 伺服器，VS2005 透過 HTTP 與 TFS 進行原始碼與工作項目等整合。
- A詳: Team Foundation Server 是微軟的應用生命週期管理（ALM）平台，提供版本控制、工作項目追蹤、建置與報表。Visual Studio 2005 透過 HTTP Web 服務與 TFS 通訊，進行簽入/簽出、取得工作清單等。因採用 HTTP 與整合式驗證，若系統代理被更動（如 Fiddler 開啟），連線流程可能受影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q9, B-Q3

A-Q3: 為什麼 AJAX 開發特別需要 Fiddler 這類工具？
- A簡: AJAX 以背景 HTTP 通訊為主，瀏覽器看不到細節，需用代理工具檢視封包。
- A詳: AJAX 應用多以背景 XHR/Fetch 交換 JSON/XML，網頁原始碼無法呈現實際的請求標頭、主體與回應。Fiddler 攔截並顯示這些隱形流量，包含重導、快取、Cookie、認證交握與錯誤碼。能協助定位跨域、授權、API 套件參數與效能瓶頸，是前後端整合除錯的關鍵工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q5

A-Q4: 什麼是 Proxy（代理伺服器）？
- A簡: Proxy 代送 HTTP 請求與回應，可控管、快取、記錄或變更流量路徑。
- A詳: 代理伺服器位於用戶端與伺服器間，接收用戶端請求並代為轉送至目的地，再將回應傳回。用途包含存取控制、快取加速、內容過濾與審計。系統設定代理後，多數應用會循代理連線。Fiddler 便是本機代理，用於攔截檢視或改寫 HTTP 封包。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, B-Q15

A-Q5: 什麼是 WinINET（Windows Internet 設定）？
- A簡: WinINET 是 Windows 提供的網路堆疊與設定，IE 與多數應用沿用其 Proxy 設定。
- A詳: WinINET 是 Windows 提供的網路 API 與設定儲存，包含 Proxy 啟用、位址、例外清單等。IE 及使用 WinINET 的應用（如 VS2005 的某些模組）會共用這些設定。Fiddler 開啟時通常會修改 WinINET 的 Proxy 至 127.0.0.1:8888 以攔截全系統流量。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q6, C-Q6

A-Q6: 什麼是 IE Proxy Settings？
- A簡: IE 代理設定是 WinINET 的圖形介面，可設定代理與例外清單。
- A詳: 透過 Internet 選項（inetcpl.cpl）可設定 LAN 代理伺服器與「不使用代理的位址」（Proxy 例外清單）。變更後會影響使用 WinINET 的應用程式。Fiddler 一旦啟動，通常會暫時把此處的代理改為本機 127.0.0.1:8888，以便攔截 HTTP 流量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q6, C-Q1

A-Q7: 什麼是 Proxy bypass host list（例外清單）？
- A簡: 例外清單是設定哪些主機名稱不走代理，直接連線到伺服器。
- A詳: 在 IE/WinINET 代理設定中可指定主機或網域，使該等位址不經代理直連，例如「tfs.mycorp.com」或使用萬用字元「*.mycorp.com」，以及 <local> 代表本機名稱。不走代理可避免敏感服務被攔截或遭代理影響認證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q1, C-Q2

A-Q8: 什麼是 HTTP 401 Unauthorized？
- A簡: 401 表示伺服器要求驗證，客戶端尚未提供或提供失敗。
- A詳: 當伺服器需要認證（如 NTLM/Kerberos/Basic）時，會回應 401，附帶 WWW-Authenticate 挑戰標頭。客戶端再依機制送出 Authorization。若途中有代理或設定不當，可能導致憑證無法正確傳遞，形成 401 循環或最終失敗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q5, D-Q2

A-Q9: 為何 Fiddler 開啟時 VS2005 與 TFS 會衝突？
- A簡: 因代理攔截導致認證交握未正確通過，伺服器回應 401。
- A詳: VS2005 與 TFS 透過 HTTP 進行整合式驗證。Fiddler 開啟時系統代理改為本機，請求先經 Fiddler。若代理介入造成認證標頭處理差異、連線重用或分片不符預期，可能使憑證未被正確轉遞至 TFS，Fiddler 日誌會見到 401，VS 則可能顯示不直觀的錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q4, D-Q1

A-Q10: 為何將 TFS 網址加入 bypass 可暫解問題？
- A簡: 直連 TFS 避免代理介入，認證流程不被改變而順利通過。
- A詳: 把 TFS 主機加入 Proxy 例外清單後，VS2005 對 TFS 的請求不再經過 Fiddler，改為直連伺服器。因不再有代理轉送或改寫，整合式驗證如 NTLM/Kerberos 可按預期進行，避免 401 循環，實務上可迅速恢復工作流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, D-Q1, C-Q1

A-Q11: 什麼是 Fiddler 的 OnAttach 事件？
- A簡: OnAttach 是 Fiddler 啟用攔截時觸發的腳本事件，可自動執行動作。
- A詳: FiddlerScript（JScript.NET）提供事件鉤子，如 OnBoot、OnAttach、OnBeforeRequest。OnAttach 在 Fiddler 設為系統代理時觸發，可用於自動調整設定或寫入日誌。文章構想是在 OnAttach 裡自動將 TFS 主機加入 Proxy 例外清單，降低手動操作負擔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q3

A-Q12: 「正規解法」與「繞過代理」的差異？
- A簡: 正規解法是讓認證穿過代理；繞過則直接避開代理快速解法。
- A詳: 正規解法著眼於調整代理/客戶端設定，使整合式驗證在代理存在下仍成功，例如檢查連線重用、認證標頭與代理透明性。繞過代理則將特定主機加入例外清單，直接連線避免代理影響。前者通用性高但較花工，後者快速實用但失去攔截能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q4, D-Q8

A-Q13: HTTP 401 與 403 的差異？
- A簡: 401 是未驗證或認證失敗；403 是已驗證但被禁止存取。
- A詳: 401 Unauthorized 代表需認證或認證未通過，伺服器會附 WWW-Authenticate。403 Forbidden 表示身份已確認但無權存取該資源。401 多與憑證傳遞、代理或挑戰回應有關；403 通常涉及授權設定、ACL 或伺服器端規則。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q5, D-Q2

A-Q14: HTTP 401 與 407 的差異？
- A簡: 401 是伺服器要求認證；407 是代理要求認證（Proxy Authentication）。
- A詳: 401 來自目的伺服器，標頭為 WWW-Authenticate；407 則來自代理伺服器，標頭為 Proxy-Authenticate。面對 407，客戶端需對代理提供憑證方能轉送請求。辨識 401/407 有助判斷問題在代理或伺服器端，制定相應解法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, D-Q4

A-Q15: 系統 Proxy 與應用程式自訂 Proxy 的差異？
- A簡: 系統 Proxy 全域適用；應用自訂 Proxy 僅影響該應用內的 HTTP 客戶端。
- A詳: 使用 WinINET 的應用多遵循系統 Proxy；部分應用或 .NET 程式可在程式層設定 WebRequest/WebProxy 覆寫系統 Proxy。系統 Proxy 改變影響更廣，較易發生連鎖效應；應用層 Proxy 可精準控制但需程式支援。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q7

A-Q16: Fiddler 與封包嗅探器（如 Wireshark）的差異？
- A簡: Fiddler 是代理層的 HTTP 工具；Wireshark 是底層封包擷取分析。
- A詳: Fiddler 以代理身份操作 HTTP(S)，可改寫內容與重送請求，對應用層最友善。Wireshark 在網路層擷取全協定封包，解析更全面但不會改變流量。若要觀察 VS 與 TFS 的 HTTP 往來，Fiddler更直觀；要查低層連線問題則 Wireshark 合適。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1

A-Q17: 為何 VS2005 使用 IE 的 Proxy 設定？
- A簡: VS2005 部分組件基於 WinINET，因而沿用 IE 的代理設定。
- A詳: Visual Studio 2005 與其 TFS 客戶端元件在網路層使用 WinINET 或 .NET 上層 API，預設讀取系統（IE）代理設定。因此當 Fiddler 改寫 IE 代理為 127.0.0.1:8888 時，VS2005 對 TFS 的連線也會經過 Fiddler，導致本文所述的相互影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6, B-Q6

A-Q18: bypass 清單的匹配規則有哪些？
- A簡: 支援主機片段、萬用字元與 <local>；以分號分隔多項目。
- A詳: Proxy 例外清單中可寫入「主機」或「*.網域」模式，條目以分號區隔，例如「tfs.mycorp.com;*.intra.local;<local>」。<local> 代表不含點的本機網域名稱。匹配以主機名為主，通常不含協定與路徑。語法錯誤會導致繞過無效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q5

A-Q19: 將關鍵服務加入 bypass 的風險與利弊？
- A簡: 優點是穩定恢復；缺點是失去攔截與審計，可能降低能見度。
- A詳: 將 TFS 直連可避免代理干擾認證，快速穩定；但除錯代理無法再觀察該流量，也無法套用代理端的安全與審計策略。若需調查 TFS 問題，可能須改用伺服器端日誌或低層擷取，需在可觀測性與穩定性間取捨。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, B-Q15, D-Q10

A-Q20: 使用 Fiddler 偵錯 TFS 流量的核心價值是什麼？
- A簡: 提供可視化 HTTP 往返，協助理解與診斷 VS 與 TFS 的互動。
- A詳: Fiddler 能清楚呈現 VS 與 TFS 間的請求、回應、狀態碼、標頭與主體，包含 401 挑戰、重導與 Cookie。即使最終選擇繞過代理以恢復工作，理解這些互動仍有助日後規劃正規解法、設計 PAC 規則、或與網管協調代理策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, D-Q2

### Q&A 類別 B: 技術原理類

B-Q1: Fiddler 如何攔截 HTTP 流量？
- A簡: 透過將系統 Proxy 設為 127.0.0.1:8888，所有 HTTP 先經 Fiddler 再轉發。
- A詳: 原理說明：Fiddler 啟動後設定 WinINET 代理為本機 127.0.0.1:8888。用戶端連線到 Fiddler，Fiddler 代表用戶端與伺服器溝通。關鍵流程：修改代理→接收請求→記錄/修改→轉送→回傳。核心組件：oProxy（代理引擎）、FiddlerScript（事件處理）、會話記錄器與檢視器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q4, B-Q6

B-Q2: WinINET Proxy 設定如何保存與生效？
- A簡: 設定存於使用者登錄機碼，變更後透過系統通知使應用重新載入。
- A詳: 原理說明：WinINET 將 ProxyEnable、ProxyServer、ProxyOverride 存於 HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings。流程：寫入登錄→廣播設定變更→應用程式重讀。核心組件：inetcpl.cpl、InternetSetOption API、訊息廣播。Fiddler 透過 API 變更並生效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6, C-Q6

B-Q3: VS2005 與 TFS 的認證流程為何（401 挑戰）？
- A簡: 伺服器回 401 要求認證，客戶端再送 Authorization 完成交握。
- A詳: 技術原理：TFS 通常使用整合式驗證（NTLM/Kerberos）。執行流程：1) 客戶端請求→2) 伺服器 401 含 WWW-Authenticate→3) 客戶端依機制送 Authorization→4) 成功授權回 200/204。核心組件：WWW-Authenticate/Authorization 標頭、連線重用、憑證快取。代理介入可能影響第2-3步的傳遞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q4, D-Q2

B-Q4: 代理如何影響 Windows 整合式驗證（NTLM/Kerberos）？
- A簡: 代理改變連線與標頭處理，可能破壞交握或 SPN 對應導致失敗。
- A詳: 技術原理：NTLM 依賴連線狀態與多步挑戰；Kerberos 需正確 SPN。代理可能導致請求分段、連線重建、標頭轉譯問題。流程影響：挑戰/回應跨代理、連線池化不一致。核心組件：Connection/Keep-Alive、SPN、Proxy-Connection。這些都可能造成 401 循環。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q9, B-Q3, D-Q8

B-Q5: 在 Fiddler 中如何解讀 401 往返？
- A簡: 觀察 401 回應與後續帶 Authorization 的重送，判斷交握是否完成。
- A詳: 技術原理：Fiddler 會顯示狀態碼與標頭。流程：初始請求→401（WWW-Authenticate: NTLM/Kerberos/Basic）→帶 Authorization 重送→成功 200 或再 401。核心組件：Timeline、Inspectors、Headers 頁籤。若反覆 401 或缺 Authorization，表示憑證未通過或被移除。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, D-Q2, C-Q9

B-Q6: Fiddler 開啟時如何自動調整 IE Proxy 設定？
- A簡: 啟動時透過 WinINET API 設為 127.0.0.1:8888，停止時恢復原值。
- A詳: 技術原理：Fiddler 調用 InternetSetOption 設定 ProxyEnable/ProxyServer/ProxyOverride。關鍵步驟：保存原設定→設為本機代理→廣播變更→攔截→關閉時復原。核心組件：oProxy、設定儲存、系統廣播。此自動化讓全系統流量經過 Fiddler。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q5, C-Q6

B-Q7: bypass host list 的解析順序與通配符機制？
- A簡: 以主機名匹配，依條目順序測試；支援 *.domain 與 <local>。
- A詳: 技術原理：WinINET 解析 ProxyOverride 字串，以分號分隔；對請求主機逐一比較通配條目。流程：取得主機→逐條比對→命中則直連→未命中走代理。核心組件：ProxyOverride 字串解析、萬用字元匹配、<local> 判斷。注意不處理協定與路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q18, D-Q5

B-Q8: FiddlerScript 的事件模型（OnBoot/OnAttach/OnBeforeRequest）？
- A簡: 提供啟動、代理附掛、請求前等時機點，能自動化規則與日誌。
- A詳: 技術原理：FiddlerScript 是 JScript.NET，透過事件掛鉤流量生命週期。關鍵步驟：OnBoot（程式啟動）、OnAttach（成為系統代理）、OnBeforeRequest/OnBeforeResponse（每個會話）。核心組件：oSession、FiddlerApplication、UI 介面。可在 OnAttach 執行設定調整，例如自動加 bypass。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, C-Q8

B-Q9: 用 OnAttach 自動化 bypass 的運作機制？
- A簡: 在 OnAttach 事件中寫入 ProxyOverride，加入 TFS 主機直連。
- A詳: 技術原理：OnAttach 觸發時，透過登錄或 API 更新 ProxyOverride。流程：讀現值→判重→追加 tfs 主機→寫回→通知生效。核心組件：Registry/InternetSetOption、FiddlerApplication.Log。如此每次啟用代理時，自動確保 TFS 不走代理，減少手動設定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, B-Q8, C-Q3

B-Q10: Fiddler 與 WinHTTP 的差異及對 VS2005 的影響？
- A簡: Fiddler與IE基於WinINET；WinHTTP是另一堆疊，部分服務不受影響。
- A詳: 技術原理：WinINET 供互動式應用（IE 等），WinHTTP 多用於服務或後台。VS2005 與 TFS 客戶端以 WinINET 為主，因而受 Fiddler 影響；若應用用 WinHTTP，IE 代理不一定生效。關鍵組件：WinINET 設定、WinHTTP 代理。影響評估需辨識應用所用堆疊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q15, C-Q6

B-Q11: <local> 如何判定本機位址？
- A簡: <local> 代表不含點的主機名，通常為內部 NetBIOS 名稱。
- A詳: 技術原理：WinINET 將「不含點」的主機（如「intranet」）視為本機名稱，匹配 <local> 時繞過代理。流程：解析主機→檢查是否含點→命中 <local> 則直連。核心：ProxyOverride 解析規則。若 TFS 用的是 FQDN，<local> 可能不生效，需明確列出主機或 *.domain。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q5

B-Q12: Fiddler 處理 HTTPS 與 HTTP 的差異？
- A簡: HTTP 直通代理；HTTPS 需憑證解密（可選），易影響認證流程。
- A詳: 技術原理：HTTP 可直接檢視/改寫。HTTPS 需啟用解密（MITM），Fiddler 產生根憑證並重簽站台憑證。流程：CONNECT 隧道→可選解密→檢視/轉送。核心組件：憑證信任、TLS。啟用解密可能改變連線行為，應謹慎用於敏感服務如 TFS。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, D-Q8

B-Q13: VS2005 與 TFS web 服務呼叫在代理下的路徑？
- A簡: VS2005→Fiddler（127.0.0.1:8888）→TFS；bypass 時 VS2005→TFS。
- A詳: 技術原理：設為系統代理後，VS2005 的 HTTP 連線指向本機 Fiddler，Fiddler 轉送至 TFS。bypass 對特定主機直連，略過 Fiddler。流程：解析主機→檢查 bypass→決定路徑。核心組件：WinINET、ProxyOverride、Fiddler 轉送器。此路徑決策影響認證與能見度。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q7, C-Q1

B-Q14: 為何 VS2005 的錯誤訊息可能與 401 不一致？
- A簡: 上層封裝或例外轉譯，使顯示訊息未直接反映底層 HTTP 狀態。
- A詳: 技術原理：VS2005/TFS 客戶端封裝 HTTP 通訊，可能在 401 循環後回報一般性錯誤（逾時、連線失敗）。流程：底層 401→重試→超時→上拋泛化例外。核心組件：例外處理、逾時策略。需配合 Fiddler 日誌判讀真正原因。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q5, D-Q2

B-Q15: 「繞過代理」與「保留代理」兩種流量路由的技術影響？
- A簡: 繞過提升穩定性但失去攔截；保留可觀測但需處理認證相容。
- A詳: 技術原理：繞過代理讓連線直達伺服器，減少變數；保留代理可檢視與控管流量。流程影響：DNS 解析位置、連線重用、TLS 結束點。核心組件：ProxyOverride、Fiddler 解密、認證協定。選擇需依調試需求與風險權衡。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q19, D-Q10

B-Q16: 代理例外如何影響連線重試與 DNS 解析？
- A簡: 直連時由客戶端自行解析與重試；經代理則由代理代勞並可能改寫。
- A詳: 技術原理：直連情境下，客戶端作 DNS 解析與重試策略；代理情境下，目的連線由代理處理，DNS 與重試策略取決於代理。流程：解析→連線→重試/回退。核心：DNS 伺服器選擇、TCP 建立、Keep-Alive。對認證時序有間接影響。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, D-Q3

B-Q17: Fiddler 過濾器與系統 bypass 的差異與適用情境？
- A簡: 過濾器只隱藏顯示，流量仍經 Fiddler；bypass 則完全不經代理。
- A詳: 技術原理：Filters（或 FiddlerScript 註記 ui-hide）影響 UI 呈現，不改變路徑；bypass 改變 WinINET 路由，流量不再經 Fiddler。流程：請求→（過濾器：仍轉送）或（bypass：直連）。核心：UI 層 vs 網路層。隱藏噪音用過濾器；解決認證衝突用 bypass。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q8, D-Q1

B-Q18: 使用 PAC 檔時的決策流程與 DIRECT/PROXY 返回值？
- A簡: PAC 回傳 DIRECT 直連或 PROXY 指向代理，依 host/URL 邏輯決定。
- A詳: 技術原理：PAC 是 JavaScript 函數 FindProxyForURL，輸入 URL 與 host，回傳「DIRECT」或「PROXY host:port」。流程：客戶端呼叫 PAC→取得路由→執行連線。核心：dnsDomainIs、isInNet 等輔助。可精細定義 TFS 直連，其餘走 Fiddler。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q7, D-Q7

B-Q19: 多使用者/多網卡環境下 WinINET 設定作用域？
- A簡: WinINET 為每使用者設定；多網卡通常不影響代理邏輯但影響解析。
- A詳: 技術原理：WinINET 設定儲於 HKCU，與使用者登入關聯。多網卡主要影響路由與 DNS 選擇，代理邏輯仍依 WinINET。流程：讀取使用者設定→決定路由→系統 TCP/IP 決策。核心：使用者範疇、網路堆疊。佈署時需針對每位使用者設定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q10, D-Q6

B-Q20: 保存與恢復代理設定的機制（步驟與原理）？
- A簡: 啟用前保存 Proxy 值，停用或故障時還原，確保網路可用性。
- A詳: 技術原理：讀取並保存 ProxyEnable/ProxyServer/ProxyOverride。流程：啟用前存檔→修改代理→需時還原。核心：登錄存取、設定快照、錯誤回復。這是避免「關閉 Fiddler 後無網路」的保護機制，也利於自動化腳本安全回退。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, D-Q6

### Q&A 類別 C: 實作應用類

C-Q1: 如何手動將 TFS 網址加入 IE 的 Proxy 例外清單？
- A簡: 透過 Internet 選項在「例外」加入 TFS 主機或網域，直連不經代理。
- A詳: 具體步驟：1) 開啟控制台→網際網路選項→連線→區域網路設定。2) 勾選「為 LAN 使用 Proxy」→按「進階」。3) 在「不使用 Proxy 的位址」輸入「tfs.mycorp.com」或「*.mycorp.com」，多項以分號分隔。4) 確定儲存。注意事項：確認無多餘空白/錯字；必要時重啟 VS。最佳實踐：只加入必要主機。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q7, D-Q1

C-Q2: 如何在 Fiddler 設定中加入「Bypass Fiddler for URLs」？
- A簡: 在 Fiddler Options 的 Connections 加入 TFS 開頭的 URL 模式。
- A詳: 具體步驟：Fiddler→Tools→Options→Connections→在「Bypass Fiddler for URLs that start with:」加入「http://tfs.mycorp.com;https://tfs.mycorp.com」。關鍵設定：分號分隔多項；包含 http/https。注意事項：此設定會影響 WinINET 例外；重啟 VS 以套用。最佳實踐：使用精確主機避免過度繞過。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q6, B-Q17

C-Q3: 如何用 FiddlerScript 在 OnAttach 自動加入 TFS 至 bypass？
- A簡: 在 OnAttach 事件修改登錄 ProxyOverride，追加 TFS 主機字串。
- A詳: 步驟：1) Rules→Customize Rules 打開 FiddlerScript。2) 在 OnAttach 加入修改 ProxyOverride 程式碼。3) 儲存並重啟 Fiddler。程式碼片段（JScript.NET）： 
  import Microsoft.Win32;
  static function OnAttach() {
    var rk = Registry.CurrentUser.OpenSubKey("Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings", true);
    var s : String = String(rk.GetValue("ProxyOverride", ""));
    var add = "tfs.mycorp.com";
    if (s.IndexOf(add) < 0) { if (s.Length>0 && !s.EndsWith(";")) s += ";"; s += add; rk.SetValue("ProxyOverride", s); FiddlerApplication.Log.LogString("Added bypass: " + add); }
  }
  注意：必要時手動重啟 VS 以套用；具系統政策限制時可能失敗。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, B-Q8, B-Q9

C-Q4: 如何驗證 VS2005 對 TFS 已直連而非經 Fiddler？
- A簡: 嘗試連線 TFS，Fiddler 不應出現該主機會話；TFS 功能恢復正常。
- A詳: 步驟：1) 啟動 Fiddler。2) 在 VS2005 執行「連線到 TFS/版本控制操作」。3) 檢視 Fiddler 會話清單應無 tfs.mycorp.com 紀錄。4) 確認 TFS 操作成功。注意事項：若仍出現會話，檢查 bypass 規則拼寫；必要時重啟 VS 或清除 Proxy 快取。最佳實踐：同時測試 http 與 https。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q1, D-Q3

C-Q5: 如何暫停 Fiddler 對系統代理的影響？
- A簡: 取消系統代理或關閉 Capturing，即可讓流量不再經過 Fiddler。
- A詳: 步驟：1) Fiddler 左下角點「Capturing」切換關閉；或 Tools→Options→Connections 取消「Act as system proxy」。2) 需要時再重啟。注意事項：某些應用需重啟才會重新讀取代理設定。最佳實踐：在關鍵操作前暫停攔截，避免影響認證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q6

C-Q6: 如何備份與還原目前的 Proxy 設定？
- A簡: 匯出 WinINET 相關登錄值，異常時匯入還原，確保可回退。
- A詳: 步驟（PowerShell/命令列）：備份
  reg export "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" "%USERPROFILE%\proxy_backup.reg" /y
  還原
  reg import "%USERPROFILE%\proxy_backup.reg"
  注意事項：僅限目前使用者；匯入後可能需登出/重啟應用。最佳實踐：在自動化修改前先備份，並記錄 ProxyServer/ProxyOverride 現值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q20, D-Q6

C-Q7: 如何用 PAC 檔讓 TFS 直連、其餘走 Fiddler？
- A簡: 撰寫 PAC 返回 TFS 為 DIRECT，其餘為 PROXY 127.0.0.1:8888。
- A詳: 步驟：1) 建立 PAC 檔：
  function FindProxyForURL(url, host){ if (dnsDomainIs(host, "tfs.mycorp.com")) return "DIRECT"; return "PROXY 127.0.0.1:8888"; }
  2) 在 IE 設定使用自動設定指令碼。注意事項：PAC 位置可為本機或 HTTP。最佳實踐：加入多主機與 HTTPS；測試生效（about:internet）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q18, D-Q7, A-Q18

C-Q8: 如何在 FiddlerScript 中隱藏 TFS 封包僅供視覺清爽？
- A簡: OnBeforeRequest 設定 ui-hide 屬性，讓特定主機的會話不顯示。
- A詳: 步驟：Rules→Customize Rules，於 OnBeforeRequest 加入：
  if (oSession.HostnameIs("tfs.mycorp.com")) { oSession["ui-hide"] = "true"; }
  注意：這只隱藏顯示，不會繞過代理。最佳實踐：搭配顏色規則區分關鍵會話；若需解決衝突請用 bypass。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q17, D-Q1

C-Q9: 如何用 Fiddler 分析 401 問題的發生點？
- A簡: 觀察初始請求、401 挑戰、Authorization 重送與最終狀態碼。
- A詳: 步驟：1) 篩選 TFS 主機。2) 查看第一個 401 的 WWW-Authenticate。3) 檢查後續是否帶 Authorization；比較標頭內容。4) 用 Timeline 看重試與逾時。注意事項：區分 401 與 407。最佳實踐：導出 SAZ 與團隊分享，對照伺服器日誌定位根因。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q2, D-Q3

C-Q10: 如何在團隊中推廣並維護 TFS bypass 的一致設定？
- A簡: 制定主機清單、文件化操作、用腳本或 GPO 發佈並定期稽核。
- A詳: 步驟：1) 確認 TFS 主機/網域清單。2) 提供操作指引與截圖。3) 以批次/PowerShell 或群組原則設定 ProxyOverride。4) 建立驗證清單（連線測試）。注意事項：不同使用者範疇需分別套用。最佳實踐：版本化設定，納入新主機時通報更新。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q19, D-Q10, C-Q6

### Q&A 類別 D: 問題解決類

D-Q1: 遇到 VS2005-TFS 連線被 Fiddler 擋住怎麼辦？
- A簡: 優先將 TFS 主機加入 Proxy 例外或 Fiddler 的 bypass 設定以直連。
- A詳: 症狀：VS 連線/版本控制卡住，Fiddler 顯示 401。原因：代理介入導致認證交握失敗。解決步驟：1) 於 IE 或 Fiddler 加入 TFS bypass（C-Q1/C-Q2）。2) 重啟 VS 測試。3) 必要時暫停 Fiddler（C-Q5）。預防：將關鍵服務納入例外清單並文件化（C-Q10）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q13, C-Q4

D-Q2: Fiddler 顯示 401 但 VS2005 錯誤訊息無關，如何判斷？
- A簡: 以 Fiddler 觀察 401/Authorization 流程，辨識在代理或伺服器端。
- A詳: 症狀：VS 報一般錯誤（逾時/連線失敗），Fiddler 顯示 401。原因：上層封裝隱匿底層 401。解決：1) 用 C-Q9 的流程檢視 401 交握。2) 若 Authorization 未送達或反覆 401，嘗試 bypass。3) 若為 403/權限問題，檢查授權。預防：調試時總是對照 Fiddler 與伺服端日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q13, A-Q14

D-Q3: 加入 bypass 後仍 401，可能原因與處置？
- A簡: 例外清單未匹配、主機錯誤、快取未更新或真權限問題。
- A詳: 症狀：已加 bypass 但仍見 401 或仍經 Fiddler。可能原因：1) 例外語法錯誤、少了 https 或萬用字元。2) VS 尚未重讀代理設定。3) 真正權限/帳號問題。解決：檢查 ProxyOverride、加上 http/https；重啟 VS；嘗試瀏覽器驗證帳密。預防：用 PAC 精確規則（C-Q7）、文件化範例（C-Q1）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q7, C-Q4

D-Q4: Fiddler 開啟後 IE/其他應用也連不上 TFS，如何排解？
- A簡: 確認是否都經代理，為 TFS 設例外，或暫停 Fiddler 攔截。
- A詳: 症狀：多應用對 TFS 失敗。原因：系統代理全局生效，Fiddler 攔截影響認證。解決：1) 於 IE 設定 TFS 例外（C-Q1）。2) 或暫停 Fiddler（C-Q5）。3) 若見 407，檢查代理認證。預防：將關鍵主機列入企業標準例外，避免被除錯代理影響。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q6, C-Q2

D-Q5: 例外清單語法錯誤導致無效，如何診斷與修正？
- A簡: 檢查分號分隔、萬用字元與 <local> 使用是否正確，避免多餘空白。
- A詳: 症狀：設定例外卻仍經代理。原因：拼寫/語法錯誤，如少分號、萬用字元位置錯、含空白。解決：1) 以 A-Q18 規則檢查字串。2) 同時加入 http/https 模式於 Fiddler bypass。3) 測試主機別名與 FQDN。預防：用 PAC 寫明確邏輯，或用指令批次設定以避免人為錯誤。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q7, C-Q7

D-Q6: 關閉 Fiddler 後網路異常（代理未還原），怎麼辦？
- A簡: 還原 WinINET 代理設定或匯入備份，必要時手動關閉代理。
- A詳: 症狀：關閉 Fiddler 後仍設有代理導致無連線。原因：設定未還原或損毀。解決：1) Internet 選項取消代理並套用。2) 匯入 C-Q6 備份或重設 ProxyEnable=0。3) 重啟應用。預防：啟用前先備份；使用可靠腳本保存/還原（B-Q20）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q6, B-Q20

D-Q7: 使用 PAC 檔時 bypass 不生效，如何修復？
- A簡: 確認 PAC 可存取且語法正確，並驗證函式邏輯與快取。
- A詳: 症狀：PAC 已設但仍經代理。原因：PAC URL 無法存取、語法錯誤、快取未更新。解決：1) 在瀏覽器測試載入 PAC。2) 用 PAC 驗證工具或簡化函式。3) 變更版本號避免快取；刷新設定。預防：部署前測試多案例；記錄變更流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q18, C-Q7

D-Q8: 若必須經 Fiddler 完成認證，該如何提高成功率？
- A簡: 盡量保持代理透明，避免改寫認證相關標頭與連線行為。
- A詳: 症狀：無法繞過代理但需除錯。原因：代理干擾認證。解決：1) 不啟用 HTTPS 解密於敏感主機。2) 避免腳本改寫 Authorization/Connection。3) 測試單一連線、關閉重寫規則。4) 與網管確認 SPN/Kerberos 配置。預防：將敏感主機列入「不解密」清單，縮小攔截範圍。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q4, B-Q12, B-Q15

D-Q9: FiddlerScript 修改 Proxy 設定失敗，如何處理？
- A簡: 檢查權限與登錄路徑，並確保廣播設定變更或重啟應用。
- A詳: 症狀：腳本執行無錯但設定未生效。原因：無寫入權限、64/32 位路徑差異、未廣播、VS 未重讀。解決：1) 以目前使用者權限執行。2) 確認 HKCU 路徑。3) 手動重啟 VS。4) 改改用 UI 設定驗證。預防：在 Log 記錄寫入結果；保留回退機制。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, C-Q3, C-Q6

D-Q10: 如何預防 Fiddler 與關鍵服務（如 TFS）衝突再發？
- A簡: 建立例外清單、標準化設定與檢核流程，定期驗證連線。
- A詳: 症狀：反覆遇到代理衝突。原因：設定分散、缺乏標準。解決：1) 制定企業層級例外清單（含 TFS）。2) 用腳本/GPO 佈署。3) 實施定期健康檢查（C-Q4）。預防：將繞過與代理策略文件化；教育訓練；在新環境驗收時納入測試項目。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q19, C-Q10, B-Q19

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Fiddler？
    - A-Q4: 什麼是 Proxy（代理伺服器）？
    - A-Q2: 什麼是 TFS 與 VS2005 的關聯？
    - A-Q6: 什麼是 IE Proxy Settings？
    - A-Q7: 什麼是 Proxy bypass host list（例外清單）？
    - A-Q8: 什麼是 HTTP 401 Unauthorized？
    - A-Q3: 為什麼 AJAX 開發特別需要 Fiddler？
    - B-Q1: Fiddler 如何攔截 HTTP 流量？
    - B-Q5: 在 Fiddler 中如何解讀 401 往返？
    - C-Q1: 如何手動將 TFS 網址加入 IE 的 Proxy 例外清單？
    - C-Q2: 如何在 Fiddler 設定中加入「Bypass Fiddler for URLs」？
    - C-Q5: 如何暫停 Fiddler 對系統代理的影響？
    - D-Q1: 遇到 VS2005-TFS 連線被 Fiddler 擋住怎麼辦？
    - D-Q2: Fiddler 顯示 401 但 VS2005 錯誤訊息無關，如何判斷？
    - A-Q13: HTTP 401 與 403 的差異？

- 中級者：建議學習哪 20 題
    - A-Q9: 為何 Fiddler 開啟時 VS2005 與 TFS 會衝突？
    - A-Q10: 為何將 TFS 網址加入 bypass 可暫解問題？
    - A-Q11: 什麼是 Fiddler 的 OnAttach 事件？
    - A-Q17: 為何 VS2005 使用 IE 的 Proxy 設定？
    - A-Q18: bypass 清單的匹配規則有哪些？
    - B-Q2: WinINET Proxy 設定如何保存與生效？
    - B-Q3: VS2005 與 TFS 的認證流程為何（401 挑戰）？
    - B-Q6: Fiddler 開啟時如何自動調整 IE Proxy 設定？
    - B-Q7: bypass host list 的解析順序與通配符機制？
    - B-Q8: FiddlerScript 的事件模型（OnBoot/OnAttach/OnBeforeRequest）？
    - B-Q13: VS2005 與 TFS web 服務呼叫在代理下的路徑？
    - B-Q17: Fiddler 過濾器與系統 bypass 的差異與適用情境？
    - C-Q3: 如何用 FiddlerScript 在 OnAttach 自動加入 TFS 至 bypass？
    - C-Q4: 如何驗證 VS2005 對 TFS 已直連而非經 Fiddler？
    - C-Q6: 如何備份與還原目前的 Proxy 設定？
    - C-Q9: 如何用 Fiddler 分析 401 問題的發生點？
    - D-Q3: 加入 bypass 後仍 401，可能原因與處置？
    - D-Q4: Fiddler 開啟後 IE/其他應用也連不上 TFS，如何排解？
    - D-Q5: 例外清單語法錯誤導致無效，如何診斷與修正？
    - D-Q6: 關閉 Fiddler 後網路異常（代理未還原），怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q12: 「正規解法」與「繞過代理」的差異？
    - A-Q19: 將關鍵服務加入 bypass 的風險與利弊？
    - A-Q20: 使用 Fiddler 偵錯 TFS 流量的核心價值是什麼？
    - B-Q4: 代理如何影響 Windows 整合式驗證（NTLM/Kerberos）？
    - B-Q12: Fiddler 處理 HTTPS 與 HTTP 的差異？
    - B-Q15: 「繞過代理」與「保留代理」兩種流量路由的技術影響？
    - B-Q16: 代理例外如何影響連線重試與 DNS 解析？
    - B-Q18: 使用 PAC 檔時的決策流程與 DIRECT/PROXY 返回值？
    - B-Q19: 多使用者/多網卡環境下 WinINET 設定作用域？
    - B-Q20: 保存與恢復代理設定的機制（步驟與原理）？
    - C-Q7: 如何用 PAC 檔讓 TFS 直連、其餘走 Fiddler？
    - C-Q8: 如何在 FiddlerScript 中隱藏 TFS 封包僅供視覺清爽？
    - D-Q7: 使用 PAC 檔時 bypass 不生效，如何修復？
    - D-Q8: 若必須經 Fiddler 完成認證，該如何提高成功率？
    - D-Q9: FiddlerScript 修改 Proxy 設定失敗，如何處理？