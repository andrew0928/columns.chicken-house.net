---
layout: synthesis
title: "[RUN! PC] 2008 四月號"
synthesis_type: faq
source_post: /2008/04/04/run-pc-2008-april-issue/
redirect_from:
  - /2008/04/04/run-pc-2008-april-issue/faq/
---

# [RUN! PC] 2008 四月號：ASP.NET 與執行緒、IE 連線上限測試要點

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是「ASP.NET 與執行緒搭配」的核心議題？
- A簡: 在請求處理中安全使用執行緒，避免阻塞與資源遺失，同時維持併發與可擴展性。
- A詳: ASP.NET 每個 HTTP 請求由伺服器分派工作緒處理。若在程式中再自行建立或阻塞執行緒，容易造成 ThreadPool 飢餓、請求逾時、資源無法回收等問題。核心在於：搞清楚請求生命週期、使用非同步 I/O 取代同步等待、避免長駐背景緒，以及測試時考慮瀏覽器連線上限。文章提醒 IE 對同站連線預設有限制，會影響併發觀察，需適當調整或改用測試工具。整體目標是用對策略達到正確、可重現與可擴展的併發行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q7, B-Q3

A-Q2: 為什麼在 ASP.NET 中直接建立 Thread 通常不建議？
- A簡: 易受應用程式回收影響、缺乏生命週期管理，且可能造成 ThreadPool 飢餓與資源洩漏。
- A詳: ASP.NET 應用受 IIS 管控，回收或部署時會卸載 AppDomain。自行建立的背景緒不受框架管理，可能被中止或遺失工作與狀態。此外，手動 Thread 常與請求緒競爭資源，阻塞會拖垮 ThreadPool，導致排隊與逾時。若有背景任務需求，應改採工作佇列與外部工作程序，或使用框架提供的非同步模型，讓請求釋放工作緒，提升延展性與穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q11, D-Q4

A-Q3: 什麼是瀏覽器「每伺服器連線上限」？
- A簡: 瀏覽器對同一主機的同時連線數限制，會直接影響前端觀察到的併發行為。
- A詳: 多數瀏覽器對同一網域（主機名與埠）會限制同時 TCP 連線數。舊版 IE 預設每伺服器連線上限偏低（常見為 2），致使同站多請求會被排隊，影響測試結果。IE 也分別對 HTTP/1.1 與 1.0 設定上限。若要以同一瀏覽器觀察高併發，需調整設定或改用壓力測試工具，否則易誤判伺服器端的並行處理能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q1, D-Q1

A-Q4: IE 對 HTTP/1.1 與 1.0 的連線上限有何差異？
- A簡: IE 對 HTTP/1.1 與 1.0 各有獨立上限，舊版預設多為 2，可透過註冊表分別調整。
- A詳: IE 透過兩個註冊值控制同站上限：MaxConnectionsPerServer（HTTP/1.1）與 MaxConnectionsPer1_0Server（HTTP/1.0）。兩者互不影響，對應伺服器通訊協定版本。若測試頁走 HTTP/1.1，僅調整 1.1 的值才會生效。舊版 IE 常預設為 2，導致前端僅見兩個並行下載。調整這兩個值（例如設為 8）可改善觀察到的併發，但也可能增加伺服器負載。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, D-Q9

A-Q5: 調整 MaxConnectionsPerServer 有何影響與風險？
- A簡: 可提升同站併發下載速度，但可能放大伺服器壓力、影響網路公平性與測試可比性。
- A詳: 調高同站連線上限能加快多資源載入，適合本機驗證併發行為。然而，過高的連線數會同時啟動更多請求，造成伺服器 CPU、記憶體與連線資源壓力上升，也可能加劇排隊與逾時。對性能測試而言，設定不一致會導致結果不可比。建議僅在受控環境使用，並同步監控伺服器負載與併發度，或改用專業壓測工具統一參數。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q7, D-Q10

A-Q6: ASP.NET 要求處理緒與 ThreadPool 的關係是什麼？
- A簡: IIS 佇列請求，ASP.NET 以 ThreadPool 分派工作緒處理，非同步作業可釋放緒以增進伸縮。
- A詳: 請求先入 HTTP.sys 佇列，再由 w3wp 工作者程序接手。ASP.NET 使用 .NET ThreadPool 的工作緒處理同步任務，I/O 完成緒處理非同步回呼。同步阻塞會占住工作緒，減少可用緒數，引發排隊與逾時；非同步 I/O 則在等待外部資源時釋放工作緒，完成後再續行，提高吞吐。理解這層關係有助於選擇正確模型與避免 ThreadPool 飢餓。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q8, D-Q8

A-Q7: 同步阻塞與非同步 I/O 在 Web 中有何差異？
- A簡: 同步會占住執行緒等待，非同步在等待時釋放執行緒，改善可擴展與併發能力。
- A詳: 同步模型例如 Thread.Sleep 或等待資料庫回應時，執行緒被占用；在高負載下易耗盡 ThreadPool，產生排隊。非同步 I/O 使用作業系統的完成通知機制，等待期間不佔用工作緒，完成後透過回呼續處理。對 I/O 密集的 Web 應用，非同步可大幅提升同時連線處理能力與效能穩定性，是首選策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q4, C-Q5

A-Q8: 為何測試頁可能出現與預期不同的併發結果？
- A簡: 受瀏覽器連線上限、資源快取、Session 鎖、伺服器佇列與網路條件影響，結果易偏差。
- A詳: 前端因素包含瀏覽器同站上限、阻塞式腳本下載、快取命中；中端可能有 CDN 或代理行為；後端有 Session 鎖序列化、ThreadPool 飢餓、IIS 佇列、應用程式集區回收等。網路延遲與 DNS 也會造成變動。測試前應控管瀏覽器參數、關閉快取、設計無副作用測試端點，並用壓測工具量測伺服器端真實併發能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q9, D-Q2

A-Q9: 在 ASP.NET 何時應使用非同步頁面或處理常式？
- A簡: 當請求等待外部 I/O（HTTP、DB、檔案）時，改用非同步頁面/處理常式可提升併發。
- A詳: 非同步適用於 I/O 密集情境，如呼叫外部 API、資料庫長查詢、檔案/雲端儲存存取等。改用 PageAsyncTask、HttpTaskAsyncHandler 或 IHttpAsyncHandler，能在等待期間釋放工作緒，減少排隊，避免 ThreadPool 飢餓。CPU 密集工作不適合在網站中執行，應移交背景服務或分散式工作系統處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, C-Q4

A-Q10: 背景工作在網站中應如何設計與部署？
- A簡: 避免網站內長駐緒；採工作佇列與外部工作者（服務/排程）確保可靠與可擴展。
- A詳: 網站易受回收與部署中斷影響，長駐背景緒風險高。建議採用佇列（如訊息佇列、資料表）作為可靠緩衝，Web 僅入列；再由外部工作程式（Windows 服務、容器工作、排程器）出列處理，分離生命週期並便於擴展與監控。這種架構可避免任務遺失並提升容錯性與可維護性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q4, C-Q8, B-Q11

A-Q11: ASP.NET Session 鎖對併發的影響是什麼？
- A簡: 預設 Session 為互斥鎖定，同一用戶同時請求會被序列化，降低併發度。
- A詳: 使用 InProc 或預設設定時，ASP.NET 以排他鎖保護每個 Session 狀態，一個使用者若同時發出多個需要寫 Session 的請求，會被序列化執行。可將頁面或控制器標示為只讀 Session，允許並行讀取，或移除不必要的 Session 存取以提升併發。測試時應關注此機制避免誤判。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q7, A-Q8

A-Q12: 應用程式集區回收對背景執行緒有何影響？
- A簡: 回收會卸載 AppDomain，任務中斷或遺失；自行緒不可靠，需外移或妥善終止。
- A詳: 回收可能因設定、閒置、錯誤或部署觸發。卸載時背景緒可能被中止，未持久化的工作會遺失。即便攔截事件亦難保任務完成。故不建議在網站中長時間執行背景工作；須用可靠外部處理與持久化佇列，或至少設計可恢復與冪等的任務流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, D-Q4, A-Q10

A-Q13: HttpContext 在背景執行緒中的可見性如何？
- A簡: 離開請求管線後 HttpContext 可能為 null，不應跨緒依賴；必要資料應先抽取。
- A詳: HttpContext 與相關物件綁定於當前請求執行流程。非同步續行雖可透過同步內容傳遞，但跨越請求生命週期或手動 Thread 後，常出現 null 或不一致。最佳實務是於請求早期將必要資料（如用戶識別、追蹤 ID）複製到自有模型，避免在背景工作中直接讀取 HttpContext。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q6, C-Q8

A-Q14: 什麼是 per-host 連線上限與跨網域拆分？
- A簡: 每主機有獨立上限；早期可透過子網域分散資源以提高前端載入併發。
- A詳: 瀏覽器限制是「每主機」計數，因此將資源分散到多個子網域可突破單一主機上限，改善平行載入。不過這會增加 DNS 開銷與複雜度。現代協定（如 HTTP/2）提供多工能力，減少此技巧的必要性。針對舊版 IE 測試，此概念有助解讀併發表現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q9, D-Q1

A-Q15: 為何該範例需要調整 IE 連線數？
- A簡: 為避免 IE 預設兩連線限制扭曲結果，調高上限以正確觀察併發效果。
- A詳: 文內範例展示 ASP.NET 與併發行為。若用 IE 預設設定（常見同站僅 2 連線），多請求會被前端限制排隊，導致測得的併發度偏低。調整註冊表的 MaxConnectionsPerServer 與 MaxConnectionsPer1_0Server（例如設為 8），或改用壓測工具，可更忠實反映伺服器端並行處理能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, D-Q1, A-Q3

### Q&A 類別 B: 技術原理類

B-Q1: IE 如何決定 MaxConnectionsPerServer 的使用？
- A簡: 依通訊協定版本選用對應註冊值，對同一主機限制同時連線數，藉此排程請求。
- A詳: 技術原理說明：IE 使用 WinINet 堆疊，啟動時讀取 HKEY_CURRENT_USER\...\Internet Settings 下的 MaxConnectionsPerServer（HTTP/1.1）與 MaxConnectionsPer1_0Server（HTTP/1.0）。關鍵步驟或流程：1) 判斷目標主機與協定版本；2) 套用對應上限；3) 多餘請求排隊等待連線可用。核心組件介紹：WinINet、連線管理器與請求排程器。變更後通常需重啟 IE 才完全生效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q1, D-Q9

B-Q2: HTTP/1.1 keep-alive 與連線重用如何影響併發？
- A簡: 持久連線降低握手成本，但同站上限限制同時請求數，影響實際併發與載入順序。
- A詳: 技術原理說明：HTTP/1.1 預設啟用 keep-alive，連線可被多個請求序列重用。關鍵步驟：1) 建立 TCP 連線；2) 於同連線依序發送請求；3) 閒置時間達閾值關閉。核心組件：TCP、HTTP/1.1 連線管理。由於 1.1 缺乏多工（pipelining 在多數瀏覽器停用），同一連線多為序列，需透過多連線取得併發，受上限制約。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q9, A-Q14

B-Q3: ASP.NET 請求管線如何配置與使用執行緒？
- A簡: HTTP.sys 佇列請求，IIS 工作者取出並交由 .NET ThreadPool 工作緒或 I/O 完成續行。
- A詳: 技術原理說明：IIS 接收請求後，整合管線將其交給註冊模組/處理常式；同步處理佔用 ThreadPool 工作緒，非同步 I/O 則等待完成埠回呼續行。關鍵步驟：佇列→分派→執行→回應→回收資源。核心組件介紹：HTTP.sys、w3wp、ASP.NET 模組/處理常式、ThreadPool（工作緒與 I/O 緒）。正確使用非同步可提升吞吐量。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q8, D-Q8

B-Q4: ThreadPool 工作佇列與請求限額如何互動？
- A簡: 阻塞工作佔滿工作緒，造成佇列累積；ThreadPool 動態補緒，但反應滯後導致逾時。
- A詳: 技術原理說明：ThreadPool 有最小/最大緒數與增長策略，遇長阻塞會耗盡可用緒。關鍵步驟：1) 請求入佇列；2) 分派工作緒執行；3) 阻塞導致可用緒不足；4) ThreadPool 緩慢增補；5) 請求逾時。核心組件：ThreadPool 排程器、工作佇列、I/O 完成緒。避免在請求中同步等待，改用非同步以釋放工作緒。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, D-Q8, C-Q4

B-Q5: ASP.NET 的 SynchronizationContext 有什麼作用？
- A簡: 協調非同步續行回到安全的執行環境，維持請求語意與資源一致性。
- A詳: 技術原理說明：ASP.NET 設定特製的 SynchronizationContext，將非同步續行排回可用的請求處理環境，不保證同一實體緒但保留語意。關鍵步驟：1) 設定同步內容；2) await 釋放；3) 完成後 Post 回續行。核心組件：SynchronizationContext、AsyncLocal/CallContext。離開請求生命週期後，續行可能不再有 HttpContext，需提前取值。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q13, D-Q5

B-Q6: PageAsyncTask 在 Web Forms 中如何運作？
- A簡: 以註冊非同步任務於頁面生命週期執行，完成後續行產生輸出，避免阻塞請求緒。
- A詳: 技術原理說明：PageAsyncTask 支援 Begin/End 或 Task 型式，讓頁面於等待 I/O 時釋放緒。關鍵步驟：1) RegisterAsyncTask；2) ASP.NET 排入非同步管線；3) I/O 完成續行；4) 完成頁面生命週期。核心組件：PageAsyncTask、IHttpAsyncHandler、SynchronizationContext。適合呼叫外部服務或長 I/O 作業。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, B-Q7, A-Q9

B-Q7: IHttpAsyncHandler 的執行流程是什麼？
- A簡: 透過 BeginProcessRequest/EndProcessRequest（或 Task）非同步處理請求並回寫回應。
- A詳: 技術原理說明：IHttpAsyncHandler 以 APM 模式運作；現代可用 HttpTaskAsyncHandler（Task 型）。關鍵步驟：1) Begin 啟動非同步 I/O；2) I/O 完成觸發回呼；3) End 收尾並輸出結果。核心組件：IHttpHandler、IHttpAsyncHandler、HttpContext、作業系統 I/O 完成埠。適用於需要精準控制請求的高效非同步處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, B-Q14, A-Q7

B-Q8: 造成 ThreadPool 飢餓的機制是什麼？
- A簡: 大量同步等待或長阻塞占滿工作緒，I/O 回呼無緒可續行，形成全域停滯與逾時。
- A詳: 技術原理說明：ThreadPool 採全域工作緒池。若請求中普遍同步等待（如 Thread.Sleep、Result/Wait），可用緒迅速耗盡。關鍵步驟：1) 同步阻塞蔓延；2) ThreadPool 緩慢擴張；3) 續行回呼搶不到緒；4) 請求雪崩。核心組件：ThreadPool 排程器、非同步回呼佇列。解法是改為真正非同步 I/O、避免同步封鎖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q8, A-Q7, C-Q4

B-Q9: 瀏覽器同站連線上限與資源載入優先序如何運作？
- A簡: 在上限約束下，瀏覽器依類型與依賴排程資源；阻塞性腳本會延後同源其他資源。
- A詳: 技術原理說明：資源載入策略考慮 HTML 解析、CSS/JS 阻塞、優先序與快取。關鍵步驟：1) 建立請求佇列；2) 依上限取出；3) 遵循阻塞/延遲規則；4) 完成後釋放名額。核心組件：網頁解析器、網路排程器、連線池。上限越低，排隊越多，對觀察併發影響越大。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q14, D-Q1

B-Q10: Registry 設定機制與 IE 讀取時機是什麼？
- A簡: IE 自 HKEY_CURRENT_USER 讀取設定，變更後通常需重啟 IE 以套用新上限。
- A詳: 技術原理說明：使用者層級的 Internet Settings 透過 WinINet 讀取。關鍵步驟：1) 開機或啟動 IE 時載入；2) 查詢對應鍵值；3) 套用到連線管理。核心組件：Windows Registry、WinINet。若有群組原則或企業管理代理，設定可能被覆寫，需檢查策略或權限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q9, A-Q4

B-Q11: ASP.NET 背景工作與 AppDomain 卸載的關係？
- A簡: 卸載會停止背景緒；若未持久化或支援恢復，工作可能中止或遺失。
- A詳: 技術原理說明：IIS 回收觸發 AppDomain.Unload，CLR 嘗試優雅終止執行緒，不保證完成。關鍵步驟：1) 發送停止訊號；2) 超時則強制中止；3) 釋放資源。核心組件：AppDomain、IIS 回收器、Thread 中止。可靠的做法是外移背景工作或以持久化佇列與冪等處理設計支援恢復。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, D-Q4, C-Q8

B-Q12: SessionStateModule 如何序列化同一 Session 的請求？
- A簡: 透過互斥鎖保護 Session，讀寫請求序列化；唯讀可並行，減少阻塞。
- A詳: 技術原理說明：SessionStateModule 為每個 Session 建鎖，預設 ReadWrite。關鍵步驟：1) 取得鎖；2) 執行頁面；3) 釋放鎖。唯讀頁面可標記為 ReadOnly 以允許並行讀取。核心組件：SessionStateModule、鎖管理。避免不必要的 Session 依賴有助提升併發與避免「同用戶互鎖」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q7, A-Q8

B-Q13: HttpContext 與 AsyncLocal 在非同步中的傳遞機制？
- A簡: 透過 CallContext/AsyncLocal 保留請求語意，但跨生命週期或手動緒切換可能遺失。
- A詳: 技術原理說明：ASP.NET 將環境資訊存於呼叫內容或 AsyncLocal，讓 await 後續行可取得同一請求語意。關鍵步驟：1) 設定環境；2) 非同步釋放；3) 續行時提取。核心組件：HttpContext、SynchronizationContext、CallContext/AsyncLocal。自建 Thread 或離開請求後，環境不保證存在，需自備資料傳遞。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, D-Q6, B-Q5

B-Q14: 非同步 I/O 與 I/O 完成埠在 Windows 的角色？
- A簡: 作業系統以完成埠回報 I/O 完成，使應用在等待期間不占用工作緒，提升伸縮性。
- A詳: 技術原理說明：Windows Overlapped I/O 將請求提交後立即返回，完成時透過完成埠通知。關鍵步驟：1) 提交 I/O；2) 事件驅動通知；3) 續行回呼。核心組件：I/O 完成埠（IOCP）、ThreadPool I/O 緒。ASP.NET/CLR 建立在此之上實現高效非同步，避免同步等待導致 ThreadPool 飢餓。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q7, B-Q7, C-Q5

B-Q15: 伺服器端與客戶端連線限制會如何疊加影響？
- A簡: 兩端限制同時生效，實際併發受較小者主導；需同時考量瀏覽器與伺服器配額。
- A詳: 技術原理說明：客戶端有同站上限，伺服器端有連線池、最大並行請求、Queue 長度等。關鍵步驟：1) 客端限制產生排隊；2) 伺服器資源也有上限；3) 兩者共同決定吞吐與延遲。核心組件：瀏覽器連線管理、IIS 佇列、應用程式 ThreadPool。調整測試參數需兩端同步，才能得到可比較結果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, D-Q10, C-Q7

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何調整 IE 同站連線上限（匯入 .reg）？
- A簡: 建立 .reg 檔匯入使用者註冊表，將 MaxConnectionsPerServer 與 MaxConnectionsPer1_0Server 提高。
- A詳: 具體實作步驟：1) 建立文字檔 IE.reg；2) 貼上下列內容；3) 以雙擊匯入；4) 重啟 IE。關鍵設定： [HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings] "MaxConnectionsPerServer"=dword:00000008 "MaxConnectionsPer1_0Server"=dword:00000008 注意事項：先備份註冊表；僅於測試時使用，避免對生產環境造成副作用；變更後重啟瀏覽器生效。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q10, D-Q9

C-Q2: 如何用 regedit 手動修改 MaxConnectionsPerServer？
- A簡: 於 regedit 導覽至 Internet Settings，新增或修改兩個 DWORD 值為期望上限。
- A詳: 具體步驟：1) Win+R 輸入 regedit；2) 前往 HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings；3) 新增 DWORD（32 位元）值 MaxConnectionsPerServer 與 MaxConnectionsPer1_0Server；4) 設為十進位 8；5) 關閉並重啟 IE。注意：需使用對應使用者帳號操作；企業環境可能被群組原則覆寫；誤改他鍵值風險高，建議先備份。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, D-Q9, A-Q5

C-Q3: 如何建立模擬長工時的 ASP.NET 測試頁？
- A簡: 建立簡單端點，故意延遲回應，用於觀察併發與瀏覽器連線上限的影響。
- A詳: 具體步驟：1) 新增 Web Forms/Handler；2) 加入延遲；3) 於瀏覽器同時觸發多請求觀察。關鍵程式碼片段（僅測試用）：protected void Page_Load(object s, EventArgs e){ System.Threading.Thread.Sleep(5000); Response.Write("done"); } 注意：實務請改用非同步 Task.Delay；勿於生產使用 Thread.Sleep；端點應關閉快取避免干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q6, D-Q3

C-Q4: 如何在 Web Forms 使用 PageAsyncTask 實作非同步？
- A簡: 於頁面註冊 PageAsyncTask，使用 await 非同步等待 I/O，避免阻塞工作緒。
- A詳: 具體步驟：1) 在 Page_Load 早期註冊任務；2) 以 Task 型式撰寫非同步邏輯；3) 輸出結果。關鍵程式碼：protected void Page_Load(object s, EventArgs e){ RegisterAsyncTask(new PageAsyncTask(async ct=>{ await Task.Delay(5000, ct); Response.Write("done"); })); } 注意：避免擷取 HttpContext 後跨緒使用；確保例外被妥善處理；測試回應逾時設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q5, D-Q5

C-Q5: 如何寫一個 HttpTaskAsyncHandler 進行非同步處理？
- A簡: 繼承 HttpTaskAsyncHandler，於 ProcessRequestAsync 使用 await 執行非同步 I/O。
- A詳: 具體步驟：1) 新增類別並繼承；2) 覆寫非同步方法；3) 在 Web.config 映射路徑。關鍵程式碼：public class Slow:HttpTaskAsyncHandler{ public override async Task ProcessRequestAsync(HttpContext ctx){ await Task.Delay(5000); ctx.Response.Write("OK"); } } 注意：處理例外與逾時；避免使用 Thread.Sleep；必要資料先取出再 await。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q14, D-Q5

C-Q6: 如何用瀏覽器同時觸發多個請求觀察併發？
- A簡: 以多分頁、多資源或簡易腳本同時呼叫慢端點，並使用開發者工具觀察網路佇列。
- A詳: 具體步驟：1) 在頁面插入多個 <img src="/slow.ashx">；2) 或用 JS 迴圈 fetch 同一端點；3) 開啟 Network 面板觀察併發。關鍵片段：for(let i=0;i<10;i++){fetch('/slow.ashx?i='+i);} 注意：IE 有同站上限，需先調整；關閉快取；確保端點為無副作用 GET；標注查詢字串避免快取合併。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q1, D-Q1

C-Q7: 如何用 curl/ab 工具做併發測試，避開 IE 限制？
- A簡: 使用命令列壓測工具直接對端點發出多併發請求，精準控制參數並記錄結果。
- A詳: 具體步驟：1) 安裝 ApacheBench 或使用 curl 並行；2) 設定 -n 次數與 -c 併發；3) 觀察吞吐與延遲。關鍵命令：ab -n 100 -c 10 http://host/slow.ashx；或：seq 50|xargs -P10 -I{} curl -s http://host/slow.ashx。注意：對生產環境小心；確保網路穩定；同步監控伺服器資源與日誌。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q15, D-Q2

C-Q8: 如何將背景工作移出網站改用服務/佇列？
- A簡: 將工作入列至持久化佇列，另建常駐服務出列處理，分離生命週期並提高可靠性。
- A詳: 具體步驟：1) 設計工作資料模型與冪等處理；2) Web 將任務寫入佇列/資料表；3) 建立 Windows 服務/容器 Worker 出列執行；4) 加入重試與監控。關鍵程式碼：Web 僅呼叫 QueueClient.Enqueue(job); 注意：確保持久化、重試、告警與可觀測；Web 不直接長時間執行背景任務。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, B-Q11, D-Q4

C-Q9: 如何在 ASP.NET 觀測效能計數器診斷執行緒瓶頸？
- A簡: 透過 PerfMon 監看 ASP.NET 請求佇列、ThreadPool 使用率與逾時，定位阻塞與飢餓。
- A詳: 具體步驟：1) 開啟效能監視器；2) 加入計數器：ASP.NET Requests Queued/Executing，.NET CLR ThreadPool Active/Available；3) 重現問題並記錄數據。關鍵設定：同時觀測 CPU、IIS 當機回收事件。注意：對照應用日誌與端到端追蹤，判斷是同步阻塞或外部 I/O 拖延，導引非同步化改造。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q8, A-Q6

C-Q10: 如何撰寫安全的 .reg 並能還原設定？
- A簡: 在 .reg 文件中明確只修改需要的鍵，另備份/還原檔將值重設或刪除。
- A詳: 具體步驟：1) 匯出原鍵做備份；2) 建立 set.reg 設定上限；3) 建立 reset.reg 將兩值刪除或設回預設。關鍵內容：set.reg 如 C-Q1；reset.reg：Windows Registry Editor Version 5.00 [-HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings] 或將值設為 dword:00000002。注意：以最小權限執行；標註用途；於測試完畢恢復設定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, D-Q9

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 瀏覽器只看到兩個同時請求，怎麼辦？
- A簡: 這是 IE 的同站連線上限所致；調整註冊表或改用壓測工具觀察併發。
- A詳: 問題症狀：多個資源請求呈串行或僅 2 個併發。可能原因：IE 預設 MaxConnectionsPerServer/Per1_0Server 值低。解決步驟：依 C-Q1/C-Q2 調整為 6~8；重啟 IE；或用 ab/curl 直接測伺服器。預防措施：測試前統一瀏覽器/工具設定，記錄測試環境，避免跨環境比較失準。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, C-Q7

D-Q2: 併發測試結果不穩定或與他人不同，如何診斷？
- A簡: 檢查瀏覽器上限、快取、DNS/CDN、網路延遲與伺服器負載，建立可重現流程。
- A詳: 症狀：次次數字不同。可能原因：同站上限不一致、快取命中不同、CDN/代理路徑不同、伺服器資源壓力、資料集差異。解決步驟：關閉快取、固定測試端點、統一工具與參數、採多輪中位數。預防措施：建立測試腳本與環境檢核表，納入效能監控與日誌關聯分析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q7, B-Q15

D-Q3: 使用 Thread.Sleep 測試導致逾時或吞吐下降，怎麼辦？
- A簡: Thread.Sleep 會阻塞工作緒，改用非同步 Task.Delay 或 I/O 模擬以免 ThreadPool 飢餓。
- A詳: 症狀：請求數升高即爆量逾時。原因：Sleep 阻塞 ThreadPool，其他請求排隊。解決步驟：改為 async/await + Task.Delay 模擬等待；或以非同步 I/O 實測；調整逾時與 ThreadPool 預熱。預防措施：測試端點避免同步阻塞；將 CPU 密集工作移出網站。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q3, B-Q8

D-Q4: 背景執行緒在 IIS 回收後消失，任務遺失怎麼辦？
- A簡: 回收卸載 AppDomain 會終止背景緒；改用持久化佇列與外部工作者確保可靠。
- A詳: 症狀：部署或回收後未完成任務消失。原因：自建 Thread 不受框架管理。解決步驟：將工作改為入列；建立獨立 Worker 服務出列處理；加上重試與冪等。預防措施：避免在網站內長時間背景工作；監控回收事件與任務狀態。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, B-Q11, C-Q8

D-Q5: 非同步頁面沒有回呼或永遠等待，如何處理？
- A簡: 確認非同步任務正確完成並回傳，避免同步阻塞與跨緒存取錯誤導致未續行。
- A詳: 症狀：頁面卡住、沒有輸出。原因：未完成 Task、例外被吞、同步阻塞、跨緒取用無效 HttpContext。解決步驟：改用 async/await；確保所有 await 都非同步；記錄例外；避免 .Result/Wait；必要資料先取出。預防措施：撰寫整合測試覆蓋逾時與例外；加入逾時取消與告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q4, C-Q5

D-Q6: 發現 HttpContext.Current 為 null，該怎麼辦？
- A簡: 這通常發生在背景緒或請求後續行；避免依賴，改於請求早期提取所需資料。
- A詳: 症狀：背景工作或延遲回呼中取用 HttpContext 為 null。原因：已離開請求生命週期或跨緒。解決步驟：在請求開始取出必需資料（用戶、追蹤 ID）；以參數傳遞；避免在背景工作取用 HttpContext。預防措施：用明確的相依注入與資料模型取代隱式全域狀態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q13, C-Q8

D-Q7: 同一使用者多個請求互相等待，原因是什麼？
- A簡: 多為 Session 排他鎖導致序列化；改用唯讀 Session 或移除不必要的 Session 存取。
- A詳: 症狀：同帳號同時觸發多請求僅見一個執行。原因：SessionStateModule 預設加鎖。解決步驟：將不需寫入的頁面標示為唯讀；減少 Session 存取；必要時改用無鎖的外部儲存策略。預防措施：設計時盡量無狀態；把狀態最小化到必要範圍。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q12, A-Q8

D-Q8: 503/逾時且 Requests Queued 飆高，怎麼診斷？
- A簡: 典型 ThreadPool 飢餓或資源飽和；檢查阻塞程式碼並改非同步，觀測計數器驗證。
- A詳: 症狀：高併發時 503、逾時、佇列累積。原因：同步阻塞、外部 I/O 緩慢、ThreadPool 不足。解決步驟：用 PerfMon 看 ThreadPool/Requests；找出阻塞段落改 async；增加資源或調整逾時。預防措施：以非同步為預設；壓測前預熱；監控與自動化告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q9, A-Q7

D-Q9: 匯入 .reg 後 IE 無變化，如何排解？
- A簡: 檢查路徑、權限、是否使用 IE、是否重啟、群組原則與 32/64 位相容性。
- A詳: 症狀：併發仍受限。原因：匯入到錯誤 hive、未重啟 IE、企業原則覆寫、實際用的是非 IE 瀏覽器。解決步驟：確認 HKEY_CURRENT_USER 路徑；以當前使用者執行；重啟 IE；在 gpedit 檢查原則；確認測試瀏覽器。預防措施：用腳本自動檢查設定並輸出當前值；記錄環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q1, C-Q2

D-Q10: 調高連線上限後下載變快但伺服器壓力大，如何平衡？
- A簡: 適度調整上限、使用壓測工具控制併發、優化伺服器非同步化並擴展資源。
- A詳: 症狀：前端快、後端 CPU/記憶體/佇列飆升。原因：同時請求過多放大瓶頸。解決步驟：降低客端上限到合理值；使用 ab 控制併發階梯測試；後端改非同步 I/O；加入快取與 CDN；擴展工作執行個體。預防措施：容量規劃與壓測基準化；雙端同步調參，避免單邊調高造成系統失衡。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q5, B-Q15, C-Q7

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是「ASP.NET 與執行緒搭配」的核心議題？
    - A-Q3: 什麼是瀏覽器「每伺服器連線上限」？
    - A-Q4: IE 對 HTTP/1.1 與 1.0 的連線上限有何差異？
    - A-Q5: 調整 MaxConnectionsPerServer 有何影響與風險？
    - A-Q7: 同步阻塞與非同步 I/O 在 Web 中有何差異？
    - A-Q15: 為何該範例需要調整 IE 連線數？
    - B-Q9: 瀏覽器同站連線上限與資源載入優先序如何運作？
    - B-Q10: Registry 設定機制與 IE 讀取時機是什麼？
    - C-Q1: 如何調整 IE 同站連線上限（匯入 .reg）？
    - C-Q2: 如何用 regedit 手動修改 MaxConnectionsPerServer？
    - C-Q6: 如何用瀏覽器同時觸發多個請求觀察併發？
    - C-Q7: 如何用 curl/ab 工具做併發測試，避開 IE 限制？
    - D-Q1: 瀏覽器只看到兩個同時請求，怎麼辦？
    - D-Q9: 匯入 .reg 後 IE 無變化，如何排解？
    - D-Q2: 併發測試結果不穩定或與他人不同，如何診斷？

- 中級者：建議學習哪 20 題
    - A-Q2: 為什麼在 ASP.NET 中直接建立 Thread 通常不建議？
    - A-Q6: ASP.NET 要求處理緒與 ThreadPool 的關係是什麼？
    - A-Q8: 為何測試頁可能出現與預期不同的併發結果？
    - A-Q9: 在 ASP.NET 何時應使用非同步頁面或處理常式？
    - A-Q11: ASP.NET Session 鎖對併發的影響是什麼？
    - B-Q2: HTTP/1.1 keep-alive 與連線重用如何影響併發？
    - B-Q3: ASP.NET 請求管線如何配置與使用執行緒？
    - B-Q4: ThreadPool 工作佇列與請求限額如何互動？
    - B-Q6: PageAsyncTask 在 Web Forms 中如何運作？
    - B-Q7: IHttpAsyncHandler 的執行流程是什麼？
    - B-Q15: 伺服器端與客戶端連線限制會如何疊加影響？
    - C-Q3: 如何建立模擬長工時的 ASP.NET 測試頁？
    - C-Q4: 如何在 Web Forms 使用 PageAsyncTask 實作非同步？
    - C-Q5: 如何寫一個 HttpTaskAsyncHandler 進行非同步處理？
    - C-Q9: 如何在 ASP.NET 觀測效能計數器診斷執行緒瓶頸？
    - D-Q3: 使用 Thread.Sleep 測試導致逾時或吞吐下降，怎麼辦？
    - D-Q5: 非同步頁面沒有回呼或永遠等待，如何處理？
    - D-Q6: 發現 HttpContext.Current 為 null，該怎麼辦？
    - D-Q7: 同一使用者多個請求互相等待，原因是什麼？
    - D-Q8: 503/逾時且 Requests Queued 飆高，怎麼診斷？

- 高級者：建議關注哪 15 題
    - A-Q10: 背景工作在網站中應如何設計與部署？
    - A-Q12: 應用程式集區回收對背景執行緒有何影響？
    - A-Q13: HttpContext 在背景執行緒中的可見性如何？
    - B-Q5: ASP.NET 的 SynchronizationContext 有什麼作用？
    - B-Q8: 造成 ThreadPool 飢餓的機制是什麼？
    - B-Q11: ASP.NET 背景工作與 AppDomain 卸載的關係？
    - B-Q12: SessionStateModule 如何序列化同一 Session 的請求？
    - B-Q13: HttpContext 與 AsyncLocal 在非同步中的傳遞機制？
    - B-Q14: 非同步 I/O 與 I/O 完成埠在 Windows 的角色？
    - C-Q8: 如何將背景工作移出網站改用服務/佇列？
    - C-Q10: 如何撰寫安全的 .reg 並能還原設定？
    - D-Q4: 背景執行緒在 IIS 回收後消失，任務遺失怎麼辦？
    - D-Q10: 調高連線上限後下載變快但伺服器壓力大，如何平衡？
    - A-Q14: 什麼是 per-host 連線上限與跨網域拆分？
    - B-Q1: IE 如何決定 MaxConnectionsPerServer 的使用？