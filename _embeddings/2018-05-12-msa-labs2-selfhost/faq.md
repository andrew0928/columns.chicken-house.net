# 容器化的微服務開發 #2, IIS or Self Host ?

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Self Host？
- A簡: 以 Console/自帶進程承載 Web API，直接成為容器 entrypoint，精準掌控啟停。
- A詳: Self Host 指應用以自行啟動的進程承載 Web API（常見為 OWIN Console 程式），不依賴 IIS 或 Windows Service。其作為容器的 entrypoint，容器啟動即啟動服務，結束即終止進程，可精準掌握 Application Start/End，便於整合 Service Discovery（註冊/反註冊）與 Health Check（心跳）。在微服務與容器編排下，Self Host 更貼近容器生命週期，避免 IIS App Pool 的間接管理帶來的時機點難題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q2

A-Q2: 什麼是 IIS Host？
- A簡: 以 IIS/W3SVC+App Pool 承載 ASP.NET，透過 ServiceMonitor 連動容器。
- A詳: IIS Host 是以 Windows 服務（W3SVC）與 App Pool 管理 ASP.NET 應用之模式。官方 IIS 容器映像以 ServiceMonitor.exe 監測 IIS 狀態，間接連動容器生命週期。IIS 提供記錄、節流、併發站台、部署與預熱等功能。然而在微服務/容器化下，這些多由編排器與 Reverse Proxy 接手，且 App Pool 延遲啟動與回收會干擾服務註冊/反註冊時機控制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, B-Q3

A-Q3: Self Host 與 IIS Host 的差異？
- A簡: 執行宿主、生命週期掌控、附加功能與整合難度不同。
- A詳: Self Host 由應用自行承載，容器 entrypoint 單一進程，啟停時機可控；IIS Host 由 W3SVC+App Pool 間接管理，需靠 ServiceMonitor 串接容器生命週期。IIS 提供豐富平台功能，但帶來重疊與複雜度；Self Host 輕量、可預期，特別適合需精準註冊/心跳/反註冊的微服務。效能上 Self Host 減少中介層開銷，常具優勢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, A-Q12

A-Q4: 為什麼在容器中優先考慮 Self Host？
- A簡: 與容器 entrypoint 一致，掌控啟停，簡化整合與部署。
- A詳: 容器生命週期依附 entrypoint 進程，Self Host 直接成為該進程，讓服務啟動即能註冊、關停能反註冊，並插入心跳流程；同時無 App Pool 多實例與延遲啟動的干擾。IIS 模式需 ServiceMonitor 桥接，控制分層增加不確定性。在微服務中，編排器接管平台功能，Self Host 更貼近「一進程一容器」理念。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q16, A-Q12

A-Q5: 什麼是容器驅動開發（CDD）？
- A簡: 假設必用容器部署，設計時即為容器最佳化，移除多餘。
- A詳: CDD 主張從架構設計起即假設最終會以容器部署，因而優先採用與容器契合的做法（如 Self Host、單一進程、環境無狀態、以編排器提供平台功能），並移除對容器重疊的機制（如 IIS App Pool 管理）。如此可簡化開發與運維邊界，降低部署與整合複雜度，讓團隊專注在核心業務邏輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q13, B-Q16

A-Q6: 為何微服務與容器是絕佳組合？
- A簡: 微服務細粒度、容器輕量隔離與自動化高度契合。
- A詳: 微服務將系統拆為可獨立部署的服務，要求快速擴縮、失效隔離與自動化。容器輕量、可攜、啟停快，搭配編排器提供調度、擴縮、健康檢查、服務發現與部署管理，恰與微服務需求吻合。兩者結合能提高交付效率、隔離風險、簡化運維，並實現彈性擴展與可靠性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, A-Q17, B-Q18

A-Q7: 什麼是容器的生命週期與 entrypoint？
- A簡: 容器由 entrypoint 進程啟動至結束，進程終止即容器止。
- A詳: 容器啟動會執行指定的 entrypoint/command，該進程存活則容器存活；進程結束，容器轉為停止狀態。故設計時應讓服務主進程即為 entrypoint，便於準確掌控啟動、心跳與關停清理。IIS Host 需 ServiceMonitor 監看 W3SVC 轉換為容器生命週期；Self Host 天然符合此模型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, B-Q17

A-Q8: 什麼是 ServiceMonitor.exe？
- A簡: 用於 IIS 容器的監視器，將 W3SVC 狀態映射到容器。
- A詳: ServiceMonitor.exe 是微軟提供給 IIS 容器的入口程式。它啟動並監控 W3SVC服務，當服務狀態由運行轉為停止/暫停等，ServiceMonitor 也隨之結束，使容器停止。此設計解決 IIS 為 Windows 服務、非容器 entrypoint 的落差，但也引入額外層級，讓啟停控制較 Self Host 間接。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, A-Q2

A-Q9: IIS App Pool 與編排器的功能有何重疊？
- A簡: App Pool 管理生命周期與資源；編排器亦提供對等能力。
- A詳: App Pool 負責 Web 應用延遲啟動、空閒回收、並行 Worker、資源限制與回收策略；而容器編排器提供健康檢查、重啟策略、伸縮、資源配額與滾動升級。微服務場景下，這些平台性功能由編排側統一治理，比在每個容器內再疊 IIS 機制更一致也更易管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q15, B-Q16

A-Q10: 什麼是 Service Discovery？為何與啟停時機耦合？
- A簡: 用於發現可用服務實例；需在啟動註冊、關停反註冊。
- A詳: Service Discovery 維護服務實例清單，供 Gateway/客戶端查詢路由。服務啟動後需立即註冊，並在運行中以心跳/健康檢查保持可用狀態；關停前須先反註冊並保留緩衝時間，避免流量導向已下線實例。IIS 延遲啟動與 App Pool 回收使註冊時機難以精準控制，Self Host 更合適。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q12, C-Q5

A-Q11: 為何 IIS 延遲啟動與 Service Discovery 互斥？
- A簡: IIS 等首個請求才啟動，但註冊需先於請求發生。
- A詳: 預設 IIS 需在第一個 HTTP 請求到來才啟動 App，才會觸發 Application_Start。然服務發現要求先註冊，Gateway 才能把流量導向該實例。兩者形成雞生蛋問題。雖可改為預熱或調整設定，但違背微服務將平台功能外移之精神，亦增加複雜度與不確定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q1, B-Q21

A-Q12: Self Host 的核心價值是什麼？
- A簡: 單進程、可控時機、輕量高效，與容器契合度高。
- A詳: Self Host 讓應用自身成為容器 entrypoint，啟動後即可註冊服務並啟動心跳；接收關機訊號時可反註冊並留緩衝，流程可預期。無 App Pool 疊代與延遲啟動，減少重疊平台機制開銷，提升效能與可觀測性。對微服務而言，能顯著降低整合與運維成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q2, B-Q8

A-Q13: 在微服務下 IIS 的哪些功能可被替代？
- A簡: 記錄、節流、預熱、負載平衡、部署多由編排/代理承接。
- A詳: 微服務基礎設施與編排器常提供集中式記錄與度量、節流配額、健康檢查與預熱、服務發現與負載均衡、遠端部署與回滾等能力。前端 Reverse Proxy 亦負責多站台路由與 TLS 終止。故在容器中每個實例內不必再引入 IIS 提供這些平台功能，避免重複與複雜。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q18, A-Q14

A-Q14: Reverse Proxy 與 IIS 的角色差異？
- A簡: 反向代理負責路由與匯聚；IIS 側重站台承載與平台功能。
- A詳: Reverse Proxy（如 API Gateway/Nginx/Envoy）面向前端，提供路由、TLS 終止、聚合、節流與觀測；背後由編排側發現服務。IIS 傳統上承載站台與 Web 應用並提供平台特性。微服務中多以代理+編排替代 IIS 的多站台與管理，個別服務採 Self Host 更輕量。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q15, B-Q18

A-Q15: ASP.NET 應用程式生命週期是什麼？
- A簡: 經 App Pool 管理，啟動於首次請求，具 Start/End 事件。
- A詳: 在 IIS 中，ASP.NET 受 App Pool 管理，通常於首個請求時載入並觸發 Application_Start；因資源策略或回收而結束時觸發 Application_End。可能同時存在多個 Worker 並行，或因空閒而回收重建。此模型對註冊/反註冊時機與一致性造成挑戰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q21, A-Q11

A-Q16: 什麼是 AppDomain 與 IAssembliesResolver？
- A簡: AppDomain 載入組件邊界；Resolver 決定 Web API 掃描範圍。
- A詳: AppDomain 表示應用的隔離與組件載入範圍。Web API 透過 IAssembliesResolver 取得要掃描的組件以發現 Controller。Self Host 時若 Controller 所在組件尚未被載入，預設 Resolver 可能找不到類型，需透過引用型別強制載入或實作自訂 Resolver 以補足。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, C-Q3

A-Q17: 什麼是健康檢查與心跳（Heartbeats）？
- A簡: 定期上報存活狀態或由外部探測，維持服務可用性。
- A詳: 心跳是服務定期向註冊中心報告存活；健康檢查可為主動回報或外部探測（HTTP/TTL）。當心跳中止或檢查失敗，實例會被標記為不健康，編排器/網關停止導流。Self Host 容易在主程序中啟動背景心跳工作並於關停時優雅結束，確保清單準確。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8, A-Q10

A-Q18: Self Host 在效能上為何可能更好？
- A簡: 減少 IIS 中介與平台功能開銷，管線更短更輕。
- A詳: IIS 提供額外平台功能，會引入額外層次與資源消耗。Self Host 以輕量 OWIN 管線直接承載 Web API，避免 App Pool 管控與模組開銷。實測（舊數據）顯示請求吞吐提升、延遲下降。微服務分工下平台功能外移，Self Host 能以相同資源擷取更多效能。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q5, B-Q24

A-Q19: Kestrel 與 IIS、Self Host 的定位？
- A簡: Kestrel 是 ASP.NET Core 伺服器，屬自託管路線，常與反代併用。
- A詳: Kestrel 是 ASP.NET Core 內建跨平台伺服器，性質接近 Self Host。其可單獨承載或配合反向代理。本文將此類方案歸為 Self Host 範疇思考：以應用進程直接承載，與容器 entrypoint 一致。IIS 仍可作反代或整合，但微服務中非必要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, A-Q14

A-Q20: Windows Service 與 Console App 在容器中的取捨？
- A簡: 容器原生以 Console 進程為宜；Service 多此一舉。
- A詳: Windows Service 為服務型工作設計，但容器以 entrypoint 進程主導生命週期，編排器管理啟停與重啟。用 Console 應用即可達成自動啟動、關停與監控；再配合 --restart 策略即如同服務。於容器內再加 Service+監控程式（如 ServiceMonitor）屬重複包裝。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q16, B-Q17, A-Q4

### Q&A 類別 B: 技術原理類

B-Q1: 容器中 IIS Host 的啟動與關閉流程如何？
- A簡: ServiceMonitor 啟動 W3SVC，首次請求載入 App，回收觸發 End，停止即容器停。
- A詳: 容器啟動後，ENTRYPOINT 是 ServiceMonitor.exe，負責啟動並監控 W3SVC。IIS 接管站台與 App Pool，於第一個請求才載入 ASP.NET 應用，觸發 Application_Start。App Pool 因空閒/回收/配額導致重啟時觸發 Application_End。當 W3SVC 停止，ServiceMonitor 結束，容器隨之停止。此多層管理使註冊/反註冊時機不易精準。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q11, B-Q3

B-Q2: Self Host 在容器內的執行流程為何？
- A簡: ENTRYPOINT 即應用進程；啟動自註冊、執行心跳；捕捉關機後反註冊。
- A詳: 容器 ENTRYPOINT 直接啟動 Self Host（如 OWIN Console）。Main 中啟動 WebApp.Start，完成路由/初始化後進行服務註冊；另啟心跳背景工作定期上報。同時註冊 Console/OS 關機事件，收到訊號後先停止心跳、反註冊，保留緩衝再優雅停止進程。流程單一且時機可控，契合容器生命週期。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q12, B-Q8

B-Q3: 為何需要 ServiceMonitor.exe 串接容器與 IIS？
- A簡: IIS 為服務，非容器進程；需監控其狀態以映射容器存亡。
- A詳: 容器以 ENTRYPOINT 進程決定存亡，而 IIS 是 Windows 服務（W3SVC），不能直接作為容器進程。ServiceMonitor 啟動並監測 W3SVC 狀態，當服務終止或暫停時退出自身，導致容器停止，間接建立容器與 IIS 的生命週期關聯。此橋接雖可行，但引入額外層次與控制延遲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q1, A-Q20

B-Q4: App Pool Recycle 對註冊/反註冊有何影響？
- A簡: 可能多次啟停、平行執行，導致重複註冊與時機錯位。
- A詳: App Pool 可因空閒/資源限制/更新而回收或重啟，且可能平行啟動多個 Worker。ASP.NET 的 Application_Start/End 會被多次觸發，易導致重複註冊與不一致。若依賴這些事件控制 Service Discovery，會出現註冊早於流量、重複/遺漏反註冊等問題。Self Host 則可消除此間接層。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q11, B-Q1, B-Q8

B-Q5: OWIN 下如何啟動 Web API？
- A簡: 使用 WebApp.Start<Startup>()，於 Startup 設定路由與中介管線。
- A詳: 以 Microsoft.Owin.Hosting 的 WebApp.Start<Startup>(url) 啟動自託管 HTTP 伺服器。Startup.Configuration 接收 IAppBuilder，建立 HttpConfiguration、註冊路由（MapHttpRoute），最後 appBuilder.UseWebApi(config)。此模式將 Web API 承載於 Console 進程，實作 Self Host。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q24, C-Q1

B-Q6: 為何會出現「No type was found that matches the controller」？
- A簡: 自託管時 Controller 組件未載入，預設 Resolver 找不到型別。
- A詳: Web API 預設以 DefaultAssembliesResolver 讀取 AppDomain 內已載入組件來搜尋 Controller。Self Host 若僅參考但尚未觸發對 Controller 類型的使用，組件可能未載入，導致找不到控制器。需在啟動階段以 typeof(Controller) 強制載入，或以自訂 IAssembliesResolver 明確提供掃描清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q3, C-Q4

B-Q7: 如何確保 Controller 組件被載入？
- A簡: 在啟動時參考型別以觸發載入，或替換 AssembliesResolver。
- A詳: 最簡單做法是在 Startup.Configuration 加上 Console.WriteLine($"{typeof(MyController)}") 等語句，強制 CLR 載入該組件。更嚴謹則實作自訂 IAssembliesResolver 並以 config.Services.Replace 取代，回傳明確的組件清單。兩者皆能避免因延遲載入導致的控制器解析失敗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, C-Q4

B-Q8: 如何擷取註冊/反註冊的精準時機？
- A簡: 啟動後（Start 之後）註冊，攔截關機訊號後反註冊並延遲收尾。
- A詳: 在 WebApp.Start 成功後即進行服務註冊與啟動心跳；同時註冊 Console 與 OS 關機事件。收到訊號時先停心跳、執行反註冊，再等待緩衝（如 5 秒）讓既有請求完成與客戶端清單更新，最後關閉進程。此序可保清單一致與優雅下線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q9, C-Q5

B-Q9: 如何攔截 Console 的終止事件？
- A簡: 透過 SetConsoleCtrlHandler 監聽 CTRL_C/BREAK/CLOSE 訊號。
- A詳: 使用 Win32 API SetConsoleCtrlHandler 註冊處理常式，可接收使用者按下 Ctrl-C/Break、關閉視窗、登出或系統關機等訊號。於處理常式中設定 ManualResetEvent 觸發，喚醒主執行緒進入清理流程。處理常式應快速返回，避免 OS 視為無回應而強制終止。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, B-Q11, D-Q3

B-Q10: 為何需要 Hidden Window 與 WM_QUERYENDSESSION？
- A簡: Console 模式對關機訊息支援有限，需用隱藏視窗接收。
- A詳: 在部分 Windows/容器版本，Console 控制處理常式未必能可靠接收到系統關機/登出訊號。建立一個 HiddenForm，啟動 message loop，於 WndProc 攔截 WM_QUERYENDSESSION，設定事件通知主流程執行反註冊與收尾，提升對 OS 關機的兼容性。需注意 OS 容許處理時間上限。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q7, B-Q11, D-Q7

B-Q11: WaitHandle.WaitAny 與 ManualResetEvent 在關機流程扮演何角色？
- A簡: 用事件模型合併多來源訊號，喚醒主流程進行清理。
- A詳: 以兩個 ManualResetEvent 分別代表 Console（Ctrl 信號）與 OS（WM_QUERYENDSESSION）事件，主執行緒呼叫 WaitHandle.WaitAny 等待任一事件被 Set 即喚醒。此模式統一處理多來源訊號，避免阻塞於 Console.ReadLine，確保在容器/OS 關機時能執行反註冊與優雅停止。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q5

B-Q12: 心跳背景工作應如何設計？
- A簡: 啟動獨立 Task 迴圈定期上報，靠 stop 旗標優雅終止。
- A詳: 註冊成功後啟動 Task，於迴圈中以固定間隔（如 1s）上報心跳。主流程收到關機事件時設定 stop=true，心跳任務檢測旗標後結束，主流程 heartbeats.Wait() 等待收尾。避免在關機處理使用 Thread.Sleep/Task.Wait，改用非阻塞延遲或微短暫等待以減少被 OS 砍掉風險。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q8, D-Q4

B-Q13: OS 關機時的時間限制與版本差異是什麼？
- A簡: 容許處理時間有限（約數秒），1709/1803 行為不同。
- A詳: 測試顯示 Windows Server 1709 約可爭取 ~10 秒，1803 約 ~5 秒；且 docker stop -t 不影響 OS 強制結束的上限。若在處理常式內阻塞（Sleep/Wait），常在 ~1 秒左右遭 OS 中止，宜採忙等或短暫 SpinWait 以最大化可用時間。行為依版本有差異，需實測調整。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q3, D-Q7, B-Q10

B-Q14: 為何避免在關機處理中使用 Sleep/Wait？
- A簡: 可能被 OS 視為無回應而提早終止，清理不完整。
- A詳: 關機處理常式若呼叫 Thread.Sleep/Task.Wait/ManualResetEvent.Wait 等阻塞 API，OS 可能認定應用無回應並提前結束進程，導致未反註冊或心跳未停止。改採非阻塞延遲、短循環輪詢或微量 SpinWait，更能在有限時間內完成必要清理步驟。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, D-Q3, C-Q8

B-Q15: 為何在容器中不再需要 IIS 的多站台/部署能力？
- A簡: 多站台與部署由反向代理與編排器負責，服務單職責。
- A詳: 容器與微服務提倡「一進程一容器」，每個服務單職責、獨立部署。多站台路由、TLS、藍綠/回滾、滾動升級等由反向代理與編排器統一處理。將這些平台性功能從每個容器內剝離，能降低影像複雜度與運維成本，避免 IIS 與編排功能重疊。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, A-Q14, B-Q18

B-Q16: 如何以 docker run 取代 Windows Service？
- A簡: 以 -d 與 --restart 策略背景執行，等價於服務自動重啟。
- A詳: 將 Console Self Host 設為 ENTRYPOINT，執行 docker run -d --restart always 映像即可達成開機自啟、異常自重啟、手動 start/stop 等行為，對應 Windows Service 之生命周期管理。配合容器停止訊號攔截，即可完成優雅關停與清理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q10, B-Q17

B-Q17: Dockerfile 中 ENTRYPOINT 與 EXPOSE 的意義？
- A簡: ENTRYPOINT 定義主進程；EXPOSE 標示容器聆聽埠供映射。
- A詳: ENTRYPOINT 決定容器啟動時執行的主進程（Self Host 可直接指定 .exe）。該進程結束容器即停止。EXPOSE 宣告容器內服務使用的埠，供運行時 -p 映射到宿主。正確設定兩者，可使容器按預期啟停並對外提供服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, C-Q10, B-Q2

B-Q18: 微服務中的記錄、節流、擴縮由誰負責？
- A簡: 由編排器與反向代理/平台統一治理，非每個容器內。
- A詳: 在微服務與容器編排體系，集中式記錄（sidecar/代理）、節流與配額（代理/網關）、自動伸縮（HPA/指標驅動）與健康檢查皆由基礎設施統一提供。應用容器聚焦業務與 API，避免引入 IIS 內建平台功能造成重疊與配置分散。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, A-Q14, B-Q15

B-Q19: 與 Consul 整合的註冊與心跳應放在哪？
- A簡: WebApp.Start 後註冊；背景 Task 發送心跳；關停前反註冊。
- A詳: 在 Self Host 啟動成功後（WebApp.Start 之後）向 Consul 註冊服務，包含服務 ID、位址、埠與健康檢查設定。以獨立 Task 定期上報心跳（或提供健康檢查端點）。攔截關機訊號時先停止心跳、發起反註冊，等待緩衝再停止進程，確保清單一致。本文示範留出插點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q12, C-Q5

B-Q20: 為何說 App Pool 像 IIS 的「小型容器」？
- A簡: 皆管理進程、資源與回收；但 App Pool 僅限 Web 應用。
- A詳: App Pool 為 IIS 內的進程與資源管理單元，負責啟停、回收與隔離，類似容器管理。但其範圍僅限 IIS/Web 應用，功能不如容器通用。容器編排在更高層面提供一致治理，將 App Pool 的職責外移，避免雙重管理與時機不一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q1, B-Q15

B-Q21: Application_Start/End 的觸發條件與限制？
- A簡: 首請求載入觸發 Start；回收/關停觸發 End；可能多次。
- A詳: Application_Start 在 App 首次載入時觸發，通常由第一個請求驅動；Application_End 在 App Pool 回收或應用卸載時觸發。多 Worker 或回收策略下可能被多次觸發，且時機受 IIS 管控，難作為 Service Discovery 等外部整合的唯一依據。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q11, B-Q4

B-Q22: 為何「先註冊再有流量」是必要順序？
- A簡: Gateway 依註冊清單路由；未註冊即無法導流。
- A詳: API Gateway 或服務端點解析需先在註冊中心找到健康實例才能路由請求。若應用等待首個請求才啟動並註冊，等於無法被發現，造成冷啟動困境。故應用啟動即註冊，確保在第一個外部請求來臨前可被發現並導流，避免雞生蛋問題。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q1, B-Q19

B-Q23: 預熱（Warm-up）應由誰負責？
- A簡: 由編排/健康檢查策略處理，比 IIS 預熱更通用。
- A詳: 微服務下預熱可由編排器透過就緒/存活探針、啟動延遲與滾動策略完成；反向代理僅在就緒通過後導流。相比依賴 IIS 預熱，編排側更通用、可觀測，且能跨語言與運行時一致治理，避免平台耦合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q15, B-Q18

B-Q24: Self Host 中的路由配置重點？
- A簡: 建立 HttpConfiguration，定義多組路由，最後 UseWebApi。
- A詳: 在 Startup.Configuration 建立 HttpConfiguration，透過 MapHttpRoute 設定如 "api/{controller}/{id}" 或含動作/參數的路由，必要時設定預設值與可選參數。完成後 appBuilder.UseWebApi(config) 掛載管線。自託管與 IIS 下相同 API 設計皆適用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q2, C-Q1

B-Q25: Windows 容器版本（1709/1803）對訊號的影響？
- A簡: 不同版本對關機訊號可見性與容許時間不同，需實測。
- A詳: 實測顯示 1709 多依賴 Hidden Window 攔截 WM_QUERYENDSESSION；1803 可由 SetConsoleCtrlHandler 捕捉 CTRL_SHUTDOWN_EVENT。兩版容許清理時間也不同（約 10s vs 5s），且 docker stop -t 不影響此上限。設計時應兼容兩種方式並預留緩衝。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q13, D-Q7

### Q&A 類別 C: 實作應用類

C-Q1: 如何將現有 ASP.NET Web API 專案改為 Self Host？
- A簡: 建立 Console 專案，安裝 OWIN 套件，呼叫 WebApp.Start 啟動。
- A詳: 步驟：1) 新建 Console 專案並參考原 Web API 專案；2) 安裝 Microsoft.Owin.Hosting、Microsoft.AspNet.WebApi.Owin；3) 建立 Startup 類，於 Configuration 設定 HttpConfiguration 與路由；4) Main 使用 WebApp.Start<Startup>(url) 啟動；5) 實作關機攔截與註冊/心跳骨架。注意：測試時勿阻塞於 ReadLine，改用事件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q2, C-Q5

C-Q2: 如何在 Startup.Configuration 設定路由？
- A簡: 建立 HttpConfiguration，MapHttpRoute 多組規則，UseWebApi 掛載。
- A詳: 代碼：在 Configuration 中 new HttpConfiguration；使用 config.Routes.MapHttpRoute 設定如 name="QueryApi", routeTemplate="api/{controller}/{id}"；另可添加含 action 的路由 "api/{controller}/{action}/{text}"；最後 appBuilder.UseWebApi(config)。注意路由順序與參數預設值，避免衝突。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q24, C-Q1, D-Q1

C-Q3: 如何強制載入 Controller 組件避免找不到型別？
- A簡: 在啟動時以 typeof(Controller) 參考，促使 CLR 載入。
- A詳: 在 Startup.Configuration 開頭加入 Console.WriteLine($"{typeof(MyController)}") 等語句，確保包含控制器的組件載入至 AppDomain，使 DefaultAssembliesResolver 能解析。或於 Main 提前引用任一 Controller 類型。注意：此為簡便作法，生產環境可搭配自訂 Resolver 更穩健。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, D-Q1

C-Q4: 如何自訂 IAssembliesResolver？
- A簡: 繼承並回傳明確組件清單，Replace 內建服務。
- A詳: 建類別繼承 IAssembliesResolver，覆寫 GetAssemblies 回傳包含控制器定義之 Assembly 集合；於啟動時呼叫 config.Services.Replace(typeof(IAssembliesResolver), new MyResolver())。可精準控制掃描範圍，避免延遲載入問題。注意維持與部署版本一致，減少反射負擔。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q3, D-Q1

C-Q5: 如何在 Self Host 中實作註冊/反註冊骨架？
- A簡: Start 後註冊；WaitAny 等待事件；反註冊並延遲停止。
- A詳: 範例：WebApp.Start 成功→使用 ConsulClient 註冊服務；啟動心跳 Task。建立 ManualResetEvent close、form.shutdown；Main 呼叫 WaitHandle.WaitAny(new[]{close, form.shutdown}) 等待；被喚醒後先 stop 心跳並 heartbeats.Wait()，呼叫反註冊 API；Task.Delay(5000) 緩衝後退出。注意處理例外與重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q12, B-Q11

C-Q6: 如何攔截 CTRL-C、CTRL-BREAK、關閉視窗事件？
- A簡: 呼叫 SetConsoleCtrlHandler 註冊處理常式，Set 事件通知主流程。
- A詳: 在 Main 初始階段呼叫 SetConsoleCtrlHandler(ShutdownHandler, true)；於處理常式內根據 CtrlType（CTRL_C_EVENT/CTRL_BREAK/CTRL_CLOSE）呼叫 close.Set()；主線程以 WaitAny 等待。注意：處理常式應快速返回，不要執行耗時清理；於結束前移除處理器並關閉資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q11, D-Q8

C-Q7: 如何攔截系統關機 WM_QUERYENDSESSION？
- A簡: 啟動 HiddenForm，覆寫 WndProc 攔截 0x11 訊息。
- A詳: 建立 HiddenForm，於 Program 以 Task.Run 啟動 Application.Run(form)；在 WndProc 檢測 m.Msg==0x11（WM_QUERYENDSESSION），設定 form.shutdown.Set() 通知主流程。可用旗標控制 OnClosing 完成後才返回，盡可能爭取時間。注意：不要長時間阻塞 WndProc，避免被視為無回應。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q13, D-Q7

C-Q8: 如何實作心跳背景工作並優雅停止？
- A簡: 啟動 Task 迴圈 Delay 上報；停機時設 stop 並 Wait 完成。
- A詳: 啟動 Task.Run(() => { while(!stop){ await Task.Delay(1000); SendHeartbeat(); } });；關機事件發生時設 stop=true，等待 heartbeats.Wait()。注意在關機期間避免阻塞等待，採短延遲與錯誤抑制；上報失敗採退避重試但尊重停機旗標，確保能及時退出。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q4, B-Q14

C-Q9: 如何撰寫 Dockerfile 打包 Self Host 並提供 80 埠？
- A簡: 基底 dotnet-framework runtime，COPY 程式，EXPOSE 80，ENTRYPOINT exe。
- A詳: 範例：FROM microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709；WORKDIR c:/selfhost；COPY . .；EXPOSE 80；ENTRYPOINT IP2C.WebAPI.SelfHost.exe。注意：基底版本需與主機 OS 相容（1709/1803），EXPOSE 只宣告埠，實際需 docker run -p 映射；確保程式使用對應埠綁定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, B-Q25, D-Q9

C-Q10: 如何用 docker 指令啟動、查看、停止並驗證清理？
- A簡: run 啟動、logs 查看、stop 停止；觀察註冊/反註冊日誌。
- A詳: 指令：docker run -d --name demo image；docker logs -t demo 觀察啟動/心跳；docker stop demo 觸發關機；再 logs 確認「Deregister」與「Stop Heartbeats」等訊息；必要時 sleep 間隔以讓緩衝完成。注意：在不同 OS 版本清理時間不同，應調整緩衝並加入重試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, B-Q16, D-Q2

### Q&A 類別 D: 問題解決類

D-Q1: 出現「No type was found that matches the controller」怎麼辦？
- A簡: 強制載入控制器組件，或替換 AssembliesResolver。
- A詳: 症狀：Self Host 啟動後呼叫 API 回報找不到控制器。原因：DefaultAssembliesResolver 僅掃描已載入組件，控制器組件尚未載入。解法：在 Startup.Configuration 引用 typeof(Controller) 促載入，或自訂 IAssembliesResolver 並 Replace。預防：啟動清單中明確載入關鍵組件，建立啟動測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, C-Q4

D-Q2: 容器停止時未執行反註冊，如何排除？
- A簡: 檢查關機事件攔截、清理順序與時間窗口。
- A詳: 症狀：docker stop 後註冊中心仍存在舊實例。原因：未攔截到關機訊號、清理流程阻塞、OS 時間上限過短。解法：同時實作 SetConsoleCtrlHandler 與 HiddenForm；在事件中僅觸發旗標，清理在主線程；反註冊完成後保留緩衝（如 5s）。預防：加日誌、在不同 OS 版本實測時間上限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, B-Q13

D-Q3: 為何 docker stop 沒等我清理完就結束？
- A簡: OS 對關機處理有上限；阻塞呼叫易被提前終止。
- A詳: 症狀：尚未反註冊就被中止。原因：Windows 對關機清理時間有限（~5-10s），且 Sleep/Wait 阻塞導致被視為無回應。解法：避免阻塞，採忙等或短輪詢；精簡清理步驟；必要時縮短心跳停止與反註冊流程。預防：根據 1709/1803 實測調整緩衝，勿依賴 docker stop -t。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q14, B-Q25

D-Q4: 心跳背景工作未停止造成例外，怎麼修？
- A簡: 以 stop 旗標控制，Wait 完成後再退出進程。
- A詳: 症狀：關機時背景 Task 仍嘗試上報或存取釋放資源。原因：未以共享旗標協調、主程序過早退出。解法：設計 stop=true 並 heartbeats.Wait()；在心跳迴圈判斷 stop 優先；上報包裝 try/catch 抑制錯誤。預防：在整合測試驗證關停次序與競態條件。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8, C-Q5

D-Q5: 在 IIS Host 下註冊資訊重複或錯亂怎麼辦？
- A簡: 啟用唯一實例保障困難；建議改用 Self Host。
- A詳: 症狀：多筆相同服務 ID 或註冊/反註冊次序錯亂。原因：App Pool 多 Worker/回收導致 Application_Start/End 多次觸發，難保唯一時機。解法：如仍用 IIS，需加鎖與去重邏輯；更佳方案是改 Self Host，縮短控制路徑。預防：避免依賴 App 事件控制外部註冊流程。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q4, A-Q11, A-Q12

D-Q6: 服務啟動後沒有流量導致未註冊，如何解？
- A簡: 嚴格遵循「先註冊再導流」，勿等首請求。
- A詳: 症狀：Gateway 查無實例，服務未接到請求。原因：IIS 預設首請求才啟動，註冊遲於流量導引。解法：Self Host 啟動即註冊；若不得不 IIS，需啟用預熱與自啟動。預防：以健康檢查與就緒探針保證導流僅發生在可用實例。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q22, B-Q23, A-Q11

D-Q7: 1709 與 1803 關機訊號不一致，怎麼因應？
- A簡: 同時實作 Console 與 Hidden Window，動態適配。
- A詳: 症狀：某版本攔不到訊號。原因：不同 Windows 版本對 Console/WM 訊號行為不同。解法：同時使用 SetConsoleCtrlHandler 與 HiddenForm 兩路徑；以日誌辨識實際觸發來源；調整清理時間與策略。預防：CI 針對多版本測試，封裝平台相依層。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q25, B-Q10, B-Q9

D-Q8: Console 應用在關閉時卡住，如何診斷？
- A簡: 檢查處理常式是否阻塞、死鎖與未釋放資源。
- A詳: 症狀：關機卡住或被 OS 強殺。原因：在處理常式中進行耗時操作、等待 UI 執行緒、死鎖、或心跳仍運作。解法：處理常式僅設定事件；清理在主線程；避免等待 UI；用 Timeout 與日誌定位卡點。預防：引入 watchdog 計時與冪等清理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q6, C-Q7

D-Q9: Port 被占用導致 Self Host 無法啟動，怎麼處理？
- A簡: 更換綁定埠或關閉佔用者，記錄清楚綁定位址。
- A詳: 症狀：啟動 WebApp.Start 失敗，提示位址已在使用。原因：同機已有服務監聽該埠或綁定位址不正確。解法：以 netstat/PortQry 查佔用，調整 baseAddress（例如改用動態埠或容器內 80 並以 -p 映射），確保僅綁定容器 IP。預防：在 Dockerfile/設定明確定義埠與映射策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, B-Q17, C-Q10

D-Q10: 日誌無法看見心跳或關機訊息，如何調校？
- A簡: 加入關鍵節點日誌，使用 docker logs 驗證序列。
- A詳: 症狀：難以確認啟停與心跳是否正確執行。原因：缺少關鍵節點日誌或緩衝未刷新。解法：在「啟動完成」「註冊成功」「心跳開始/停止」「接收訊號」「反註冊完成」「延遲結束」等節點輸出；確保輸出到 Console（無緩衝或及時 Flush）。預防：建立啟停流程檢核清單與自動化測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q10, B-Q8, B-Q12

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Self Host？
    - A-Q2: 什麼是 IIS Host？
    - A-Q3: Self Host 與 IIS Host 的差異？
    - A-Q4: 為什麼在容器中優先考慮 Self Host？
    - A-Q5: 什麼是容器驅動開發（CDD）？
    - A-Q6: 為何微服務與容器是絕佳組合？
    - A-Q7: 什麼是容器的生命週期與 entrypoint？
    - A-Q12: Self Host 的核心價值是什麼？
    - A-Q18: Self Host 在效能上為何可能更好？
    - A-Q19: Kestrel 與 IIS、Self Host 的定位？
    - B-Q5: OWIN 下如何啟動 Web API？
    - B-Q24: Self Host 中的路由配置重點？
    - C-Q1: 如何將現有 ASP.NET Web API 專案改為 Self Host？
    - C-Q2: 如何在 Startup.Configuration 設定路由？
    - C-Q10: 如何用 docker 指令啟動、查看、停止並驗證清理？

- 中級者：建議學習哪 20 題
    - A-Q9: IIS App Pool 與編排器的功能有何重疊？
    - A-Q10: 什麼是 Service Discovery？為何與啟停時機耦合？
    - A-Q11: 為何 IIS 延遲啟動與 Service Discovery 互斥？
    - A-Q13: 在微服務下 IIS 的哪些功能可被替代？
    - A-Q14: Reverse Proxy 與 IIS 的角色差異？
    - A-Q16: 什麼是 AppDomain 與 IAssembliesResolver？
    - A-Q17: 什麼是健康檢查與心跳（Heartbeats）？
    - B-Q1: 容器中 IIS Host 的啟動與關閉流程如何？
    - B-Q2: Self Host 在容器內的執行流程為何？
    - B-Q3: 為何需要 ServiceMonitor.exe 串接容器與 IIS？
    - B-Q6: 為何會出現「No type was found...」？
    - B-Q7: 如何確保 Controller 組件被載入？
    - B-Q8: 如何擷取註冊/反註冊的精準時機？
    - B-Q11: WaitHandle.WaitAny 與 ManualResetEvent 的角色？
    - B-Q12: 心跳背景工作應如何設計？
    - B-Q16: 如何以 docker run 取代 Windows Service？
    - B-Q17: Dockerfile 中 ENTRYPOINT 與 EXPOSE 的意義？
    - C-Q3: 如何強制載入 Controller 組件避免找不到型別？
    - C-Q5: 如何在 Self Host 中實作註冊/反註冊骨架？
    - D-Q1: 出現「No type was found...」怎麼辦？

- 高級者：建議關注哪 15 題
    - B-Q4: App Pool Recycle 對註冊/反註冊有何影響？
    - B-Q10: 為何需要 Hidden Window 與 WM_QUERYENDSESSION？
    - B-Q13: OS 關機時的時間限制與版本差異是什麼？
    - B-Q14: 為何避免在關機處理中使用 Sleep/Wait？
    - B-Q20: 為何說 App Pool 像 IIS 的「小型容器」？
    - B-Q22: 為何「先註冊再有流量」是必要順序？
    - B-Q23: 預熱（Warm-up）應由誰負責？
    - B-Q25: Windows 容器版本對訊號的影響？
    - C-Q4: 如何自訂 IAssembliesResolver？
    - C-Q7: 如何攔截系統關機 WM_QUERYENDSESSION？
    - D-Q2: 容器停止時未執行反註冊，如何排除？
    - D-Q3: 為何 docker stop 沒等我清理完就結束？
    - D-Q5: 在 IIS Host 下註冊資訊重複或錯亂怎麼辦？
    - D-Q7: 1709 與 1803 關機訊號不一致，怎麼因應？
    - D-Q8: Console 應用在關閉時卡住，如何診斷？