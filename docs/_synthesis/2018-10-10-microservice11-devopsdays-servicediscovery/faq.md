---
layout: synthesis
title: "DevOpsDays 專刊: Service Discovery, 微服務架構的基礎建設"
synthesis_type: faq
source_post: /2018/10/10/microservice11-devopsdays-servicediscovery/
redirect_from:
  - /2018/10/10/microservice11-devopsdays-servicediscovery/faq/
---

# DevOpsDays 專刊: Service Discovery, 微服務架構的基礎建設

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Service Discovery？
- A簡: 在動態環境自動定位服務實例，提供即時可用性、位址與中繼資料，供客戶端精準路由與容錯。
- A詳: Service Discovery 是在動態基礎設施中，自動登記、查詢與監控服務實例的機制。它維護服務名稱到可用實例（IP/Port）的映射，並附帶健康狀態與中繼資料（tags）。在容器、雲原生與微服務場景中，實例數量龐大且常變動，傳統靜態設定難以維護。Service Discovery 讓客戶端在呼叫前即時查詢可用節點，結合健康檢查、逾時與重試策略，以提高可靠性與擴展性，並為後續進階能力（分級路由、金絲雀、服務網格）奠定基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q4, B-Q1

A-Q2: 微服務為何需要 Service Discovery？
- A簡: 實例多且常變動，需動態尋址、健康過濾與細緻路由，避免靜態配置成為可靠性與效率瓶頸。
- A詳: 微服務將單體拆為多個獨立部署的服務，數量與變動頻率大幅提升。服務實例會隨擴縮容、發布與故障上下線，IP/Port 不再穩定。若仍依賴靜態設定，呼叫者無法即時知悉可用性，導致長逾時、錯誤與低效率。Service Discovery 提供動態註冊與查詢，結合健康檢查、流量策略，使呼叫端自適應環境變化。它也能承載描述性中繼資料，用於版本、SLA 層級、區域與合規等條件路由，支撐更進階的運營模式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q7, B-Q4

A-Q3: DNS+ELB 與 Service Discovery 有何差異？
- A簡: DNS+ELB偏基礎傳輸與集中式轉發；Discovery 提供細緻實例視圖、健康資訊與客戶端智能路由。
- A詳: DNS+ELB 以網路層負載平衡為主，對後端實例的可見性與控制有限，決策多在 LB 端；變更粒度多倚賴運維設定。Service Discovery 則建立服務層的登錄庫，含健康狀態與中繼資料，讓呼叫端或資料平面做條件式選擇（如版本、SLA、區域）。它可減少對集中式 LB 的依賴，避免單點與隱藏過多內部資訊。兩者可互補：外部流量走 ELB，內部流量用 Discovery 實現更彈性的服務到服務路由。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, A-Q8, B-Q4

A-Q4: 什麼是 Service Registry？
- A簡: 保存服務名稱到實例位址、健康狀態與標籤的資料庫，是發現與路由決策的權威來源。
- A詳: Service Registry 是 Service Discovery 的核心組件，存放每個服務實例的名稱、位址（IP/Port）、健康狀態、檢查方法與中繼資料（如版本、SLA、區域）。註冊可由服務自行、代理或外部控制器完成。呼叫方在發送請求前查詢 Registry，取得即時可用實例清單並應用策略（負載均衡、標籤過濾、權重分配）。一個高可用 Registry 需具備一致性、廣播/訂閱、狀態變更推送與 ACL 安全機制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q8, B-Q20

A-Q5: 健康檢查在 Service Discovery 的角色是什麼？
- A簡: 健康檢查提供實例可用性與狀態信號，供路由過濾與故障隔離，降低逾時與錯誤。
- A詳: 健康檢查透過 HTTP/TCP/腳本或 TTL 心跳，定期驗證實例的存活與就緒。結果寫回 Registry，讓呼叫端在選擇實例時能排除不健康節點，並搭配重試、熔斷降低故障放大。健康檢查可分為存活（liveness）與就緒（readiness），前者判斷需否重啟，後者判斷是否可接請求。良好的健康檢查設計應快速、輕量、可配置，避免誤判與震盪，並提供除錯訊息以助定位問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, D-Q2, D-Q10

A-Q6: Client-side 與 Server-side Discovery 的差異？
- A簡: 客戶端決策 vs 中介者決策；前者靈活細緻，後者集中易控。常內部用前者，外部用後者。
- A詳: Client-side Discovery 由呼叫者查 Registry 自行選節點，實作負載均衡、重試與標籤過濾，提供最大彈性與可見性。Server-side 則將決策下放至中介（如 LB/代理），呼叫端只知固定端點，集中治理較簡單。實務上常混用：內部服務間為細緻控制採 Client-side；對外流量或遺留系統經由 API Gateway/LB 做 Server-side，以簡化外部整合並統一入口安全。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q13, A-Q3

A-Q7: 為何僅用應用程式設定（Config）不足？
- A簡: 靜態設定無法反映實例變動與健康，難以做條件路由；維運成本高且易造成長逾時。
- A詳: Config 適合描述相對穩定的參數，對高動態的實例資訊（位址、健康、版本、SLA）表現不佳。當服務上下線頻繁，靠人工或部署流程改設定會延遲且易出錯。更進階的需求如分級路由、金絲雀、區域就近，也難在純設定中維持一致與可操作性。Service Discovery 將這些易變資訊從配置中抽離，成為查詢式資料，讓呼叫端每次呼叫前做最新決策，顯著降低逾時與錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, D-Q3

A-Q8: 為什麼傳統 LB 可能成為單點或瓶頸？
- A簡: 集中式轉發易成單點、限制吞吐與可見性；內部微服務流量更適合分散決策。
- A詳: 單一或少數集中式 LB 對內部服務間高頻互調可能形成效能與可靠性風險。它們對後端細節不可見，難以做細粒度路由（SLA、版本、租戶）。當 LB 故障或升級，可能衝擊面大；而每次路由策略調整需運維介入，降低開發敏捷。以 Client-side Discovery 或 Sidecar/Service Mesh 分散決策點，能提升整體韌性與彈性，同時保留 LB 對外入口與邊界控制之長處。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q4, D-Q4

A-Q9: 什麼是 SLA？與 Service Discovery 有何關聯？
- A簡: SLA 定義可靠度與支援水準；Discovery 以標籤與路由策略實現不同層級的服務體驗。
- A詳: 服務等級協議（SLA）描述可用性、響應時間與支援承諾。對多層方案（免費/標準/進階），差異常在可靠度與資源隔離，而非 API 功能本身。透過在 Registry 標記實例屬性（PLUS_ONLY、AZ、硬體級別），客戶端可依租戶上下文動態選路，將高價方案導向更高冗餘或隔離的實例群組，實現差異化交付與成本控制，並支援賠償與合規證明。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q6, D-Q8

A-Q10: 服務標籤（Tags/Metadata）是什麼？有何價值？
- A簡: 為實例附加可篩選屬性，用於版本、區域、SLA、合規等條件式路由與治理。
- A詳: 標籤或中繼資料是附掛於服務實例的鍵值訊息，典型含版本（v1、canary）、環境（prod/dev）、區域（az-a）、SLA（plus）與合規（pci）。Client-side 或 Mesh 可據此做過濾與權重配置，達成藍綠切換、金絲雀、就近路由、多租戶與差異化交付。標籤策略需標準化、可觀測且受 ACL 控制，避免錯誤標記影響路由與客戶體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q7, D-Q7

A-Q11: 什麼是 Sidecar 模式？
- A簡: 將網路/觀測等基礎能力抽成附屬進程，與業務程式同部署，實現無侵入治理。
- A詳: Sidecar 是與應用相伴的輔助代理，負責連線管理、服務發現、重試熔斷、度量、安全等橫切關注。它攔截出入流量，與控制面通訊以取得配置與證書，讓業務程式專注功能。Sidecar 降低語言綁定與侵入成本，促進跨團隊一致治理，是服務網格資料平面的基礎實體。從純 Client-side SDK 演進至 Sidecar，可更快落地團隊級治理能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q14, C-Q9

A-Q12: 什麼是 Service Mesh？
- A簡: 以 Sidecar 為資料平面、控制面統一治理的服務間通訊基礎設施。
- A詳: 服務網格將服務間通訊抽象為基礎設施，使用 Sidecar 代理處理流量，控制面下發路由、金絲雀、超時重試、mTLS、觀測與策略。它內建服務發現整合，能基於標籤與上下文做細緻決策。相較 SDK 式方案，Mesh 提供跨語言的一致能力與集中治理，適合規模化團隊。導入需考量複雜度、效能開銷與組織成熟度，通常循序從 Discovery/Sidecar 演進。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, B-Q15, C-Q9

A-Q13: API Management 與 Service Discovery 的差異與互補？
- A簡: APIM 聚焦對外 API 流量與商業治理；Discovery 聚焦內部服務尋址與路由，兩者可協同。
- A詳: API Management 提供對外入口的認證授權、金鑰、配額、分析、開發者入口等；多部署在邊界。Service Discovery 則面向內部服務到服務的尋址、健康與條件路由。隨內外流量界線模糊，APIGW 亦可整合 Discovery 取得後端實例與狀態，實現更智慧的轉發；內部服務也可能經由 Gateway 暴露。兩者關注點不同但非取代，協同可涵蓋全鏈路。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q13, C-Q8

A-Q14: 為何開發與運維都需理解 Service Discovery？
- A簡: 它是 Dev 與 Ops 的中介層；開發落地策略，運維保障平台與可用性，協作創造新能力。
- A詳: Discovery 涵蓋平台與應用交互：運維負責高可用 Registry、健康檢查基礎與安全；開發設計標籤策略、客戶端選路、重試與業務上下文（如租戶、SLA）映射。僅由一方主導會限制能力或增加摩擦。雙方共識可催生差異化交付、金絲雀、就近路由等以往難以實現的功能，對雲原生轉型至關重要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q9, C-Q6

A-Q15: Cloud Native 與 Service Discovery 的關聯？
- A簡: 雲原生強調彈性與動態調度；Discovery 是支撐動態尋址與自動恢復的核心能力。
- A詳: 雲原生應用運行於彈性基礎設施，容器、調度與自動擴縮讓拓撲持續變化。Service Discovery 提供名稱解析到健康實例的即時映射，支援自動恢復、滾動更新與彈性伸縮。它與生命週期管理、可觀測性、配置中心、服務網格共同構成雲原生運行時基礎。缺乏 Discovery，雲原生優勢將難以發揮，導致脆弱與人工作業負擔。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q11, C-Q1


### Q&A 類別 B: 技術原理類

B-Q1: Service Discovery 整體如何運作？
- A簡: 服務註冊至 Registry，健康回報維持狀態；客戶端查詢、選路並發送請求，失敗時重試與降級。
- A詳: 原理說明：1) 註冊：服務啟動時將名稱、位址、健康檢查與標籤寫入 Registry；2) 健康：週期檢查或 TTL 心跳更新狀態；3) 查詢：呼叫端在每次請求或快取過期時查詢可用實例；4) 選路：應用負載均衡、標籤過濾與權重；5) 執行：發送請求並套用逾時、重試、熔斷；6) 觀測：上報度量與追蹤。關鍵步驟或流程：註冊/反註冊、健康變更事件、客戶端快取與失敗處理。核心組件：Registry（HA 集群）、健康檢查器、客戶端 SDK/Sidecar、控制面（選配）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q3, B-Q4

B-Q2: 服務如何註冊到 Registry？
- A簡: 透過靜態配置、API 呼叫或代理/控制器自動註冊，附上健康檢查與標籤。
- A詳: 原理說明：註冊方式包括（1）靜態檔案：由運維撰寫服務定義檔；（2）動態 API：服務啟動時呼叫 Registry API 註冊；（3）自動註冊：sidecar/daemon 監控進程或容器自動註冊。關鍵步驟：產生唯一 ServiceID、填入 Name、Address、Port、Tags、Checks、DeregisterPolicy；完成後驗證可見。核心組件：服務進程、Registry API、代理/控制器（如 registrator）、部署工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q20, C-Q2, C-Q4

B-Q3: 健康檢查機制與狀態流轉是什麼？
- A簡: 以 HTTP/TCP/Script/TTL 驗證存活與就緒，狀態影響路由；需避免誤判與震盪。
- A詳: 原理說明：健康檢查類型包括 HTTP 200、TCP 連線、腳本回傳碼、TTL 心跳。Checks 定期執行，狀態從 passing→warning→critical。關鍵步驟：設定間隔、超時、重試與 flapping 抑制；狀態變更觸發事件，客戶端或控制面調整路由。核心組件：檢查執行器、狀態儲存、事件推送、可觀測儀表板。注意分離 liveness/readiness，對外與對內健康檢查可分流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, D-Q10, C-Q3

B-Q4: Client-side Discovery 的請求流程為何？
- A簡: 查詢可用實例→套用標籤/權重→選負載均衡→設逾時重試熔斷→發送請求。
- A詳: 原理說明：客戶端維護本地快取，定期或事件驅動更新。收到呼叫時按上下文過濾（tags、版本、SLA、區域），選擇 LB 策略（round robin、least request），設置逾時、重試與最大嘗試次數；失敗觸發重試或熔斷，並記錄度量。關鍵步驟：快取一致性、失敗分類（可重試 vs 不可重試）、回退策略。核心組件：客戶端 SDK/Sidecar、Registry 客戶端、LB 模組、容錯模組。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q5, D-Q3

B-Q5: 如何以標籤實現 SLA 分級路由？
- A簡: 以租戶上下文選擇對應標籤的實例群組，確保高階客戶導向高冗餘資源。
- A詳: 原理說明：在 Registry 對實例加上 SLA 標籤（如 plus_only、std），並為高階群組配置更高冗餘或獨立資源。客戶端於身份驗證/租戶解析後附帶 SLA，查詢時過濾匹配標籤的實例，權重可偏向高可用區。關鍵步驟：租戶到 SLA 映射、標籤治理、策略測試與回退。核心組件：租戶服務、Registry、策略引擎（在 SDK/Sidecar/Mesh）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q6, D-Q8

B-Q6: 版本導向的藍綠/金絲雀路由如何運作？
- A簡: 以版本標籤與權重分流流量，逐步擴大新版本比例並監控指標回退。
- A詳: 原理說明：在實例標籤標記版本（v1、v2、canary）與權重，路由策略按比例分配流量。金絲雀初期小比例，監控延遲、錯誤率與業務指標，達標擴容至全量；異常時自動回退。關鍵步驟：定義監控門檻、配置權重、觀測自動化、回退流程。核心組件：Registry、路由控制面（mesh 或配置系統）、度量平台。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q8, B-Q4

B-Q7: 逾時、重試與熔斷如何與 Discovery 協同？
- A簡: 以即時健康與拓撲決策，設定合理逾時與重試，熔斷故障實例避免放大效應。
- A詳: 原理說明：Discovery 提供健康與延遲資訊，客戶端據此設定請求逾時與重試策略（次數、間隔、退避）。熔斷在連續錯誤時短路請求，過一段時間半開嘗試恢復。關鍵步驟：區分 idempotent 與非冪等請求、限制總重試時間、與標籤過濾結合。核心組件：客戶端容錯庫、度量系統、Registry 健康事件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, C-Q5, B-Q3

B-Q8: 註冊中心的高可用與一致性如何設計？
- A簡: 以多節點集群與共識協議確保一致，邊緣快取與回退保障讀寫在異常時退化可用。
- A詳: 原理說明：多數 Registry 採用共識（如 Raft）確保寫入一致，並以 Gossip 傳播成員與健康狀態。關鍵步驟：部署奇數節點、跨可用區、監控選舉與複寫延遲；客戶端採快取與過期策略，在暫時不可用時允許使用 stale 讀。核心組件：Registry Server 集群、共識模組、客戶端快取、健康探測。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q5, D-Q6, B-Q1

B-Q9: Consul 的架構與關鍵組件？
- A簡: Server 節點以 Raft 共識，Client 代理與 Gossip 成員管理，提供 KV、服務註冊與健康檢查。
- A詳: 原理說明：Consul 由 Server（存放狀態、選舉）與 Client（輕量代理）組成。Server 使用 Raft 保證一致性，Serf/Gossip 處理成員與故障偵測；內建服務註冊、健康檢查、DNS 介面與 HTTP API，亦提供 KV 儲存及多資料中心。關鍵步驟：規劃 Server 數量與容錯域、Agent 模式、ACL 與加密。核心組件：consul server/client、catalog、health、dns、acl。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, D-Q6

B-Q10: 在容器與動態 IP 環境中如何做 Discovery？
- A簡: 以代理或控制器監控生命週期自動註冊，使用服務名稱抽象動態位址。
- A詳: 原理說明：容器啟停頻繁且 IP 動態，透過 Sidecar/Daemon 或編排器事件（Docker/K8s）自動註冊與反註冊，使用固定的服務名解析到當前實例。關鍵步驟：對齊容器生命週期、健康檢查與去註冊、避免殘留紀錄。核心組件：註冊控制器、Registry、健康檢查器、編排器整合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q1, D-Q6

B-Q11: 多資料中心/可用區感知路由如何設計？
- A簡: 優先同區就近路由，跨區作為回退；權重與失效切換需可配置與監控。
- A詳: 原理說明：註冊實例時標記 DC/AZ，路由策略優先選當地健康實例，當全部失效才跨區。跨區需考量延遲與成本。關鍵步驟：拓撲標記、權重與失效判定閾值、黑名單/白名單、監控跨區流量。核心組件：Registry 標籤、路由策略引擎、度量與告警。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q9, B-Q5, C-Q6

B-Q12: Discovery 與 DNS 的整合方式？
- A簡: 以內建 DNS 介面或 SRV 記錄暴露服務，供傳統客戶端解析健康實例。
- A詳: 原理說明：許多 Registry 提供 DNS 介面，服務以 name.service.consul 暴露，SRV 記錄含目標與權重。傳統應用可透過系統解析器使用。關鍵步驟：設定 DNS 轉發、TTL、stale 讀；結合健康檢查保證回應可用節點。核心組件：Registry DNS、上游 DNS、應用解析器。限制：僅靠 DNS 難實作複雜重試與細緻路由，常需搭配 SDK/Sidecar。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q8, D-Q1

B-Q13: 反向代理/NGINX/HAProxy 如何與 Discovery 協作？
- A簡: 以模板或 API 動態更新後端清單，達成 Server-side 的健康導流與權重控制。
- A詳: 原理說明：透過 consul-template、nginx-plus API 或 HAProxy Runtime API 從 Registry 拉取健康實例，生成或熱更新 upstream。關鍵步驟：建立模板、設置刷新與最小變更、灰度測試。核心組件：反向代理、模板渲染器/控制器、Registry。適用於需要集中式入口治理或無法改動客戶端的場景。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, A-Q6, D-Q4

B-Q14: 從 Discovery 演進到 Sidecar/Service Mesh 的路徑？
- A簡: 先建註冊與健康，再引入 SDK/Sidecar 實作路由容錯，最後以 Mesh 集中策略與安全。
- A詳: 原理說明：Phase1 建 Registry/健康檢查，替代靜態設定；Phase2 導入客戶端 SDK 或 Sidecar，增加重試、熔斷、標籤路由；Phase3 引入 Mesh 控制面，集中金絲雀、mTLS、策略與觀測。關鍵步驟：能力漸進、風險隔離、觀測先行、與組織協作同步。核心組件：Registry、SDK/Sidecar、控制面、度量/追蹤。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, A-Q12, C-Q9

B-Q15: Discovery 與安全（ACL、mTLS）如何結合？
- A簡: 用 ACL 控制註冊與讀取權限，mTLS 保護流量與身份，策略由控制面下發。
- A詳: 原理說明：Registry 以 ACL/Token 限制誰可註冊/查詢，避免污染；Sidecar/Mesh 以 mTLS 做雙向驗證與加密，證書生命週期由控制面管理。關鍵步驟：定義最小權限、自動發放與輪換證書、審計存取。核心組件：ACL/KMS、CA/證書代理、控制面。此結合在多租戶與合規要求場景尤為關鍵。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q8, C-Q9, B-Q8


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 Docker Compose 快速建立本機 Consul 叢集？
- A簡: 建立 1-3 台 server 與 1 台 client 的 compose，開啟 UI/DNS/API 供測試與整合。
- A詳: 具體實作步驟：1) 建立 docker-compose.yml；2) 啟動 3 server（bootstrap_expect=3）與 1 client；3) 開放 8500/8600/8300 埠；4) 檢查 UI/成員。關鍵設定：
  ```
  services:
    consul-server:
      image: consul
      command: agent -server -bootstrap-expect=3 -ui -client=0.0.0.0
      ports: ["8500:8500","8600:8600/udp"]
    consul-client:
      image: consul
      command: agent -client=0.0.0.0 -retry-join=consul-server
  ```
  注意事項與最佳實踐：使用固定網路、掛載資料卷保存狀態、設定 ACL 與加密於非開發環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, D-Q6, B-Q8

C-Q2: 如何以靜態檔案在 Consul 註冊服務？
- A簡: 撰寫服務定義 JSON，含名稱、位址、埠、標籤與健康檢查，放置於 consul.d 目錄重載。
- A詳: 具體實作步驟：1) 建 service.json；2) 包含 Name/ID/Address/Port/Tags/Checks；3) 放入 /consul/config；4) 重新載入 agent。設定範例：
  ```
  {
    "service": {
      "name": "notify",
      "id": "notify-1",
      "address": "10.0.0.5",
      "port": 8080,
      "tags": ["tier:plus"],
      "checks": [{"http":"http://10.0.0.5:8080/health","interval":"5s","timeout":"1s"}]
    }
  }
  ```
  注意：ServiceID 唯一、健康檢查輕量、設定 deregister_critical_service_after 清理殘留。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q3, D-Q1

C-Q3: 在 .NET 如何實作 HTTP 健康檢查端點？
- A簡: 暴露 /health 與 /ready，回傳 200/非 200 代表存活/就緒，供 Consul 定期探測。
- A詳: 具體實作步驟：1) ASP.NET Core 新增健康端點；2) 區分 liveness/readiness；3) 整合內部依賴檢查。程式碼：
  ```
  app.MapGet("/health", () => Results.Ok("OK"));
  app.MapGet("/ready", async () => await deps.Ok() ? Results.Ok() : Results.StatusCode(503));
  ```
  注意事項：避免重檢查昂貴操作；設定檢查超時<服務逾時；導入快取減少壓力。最佳實踐：在 UI 顯示狀態、將錯誤原因記錄於日誌。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, D-Q2, B-Q7

C-Q4: 如何在 .NET 透過 Consul API 動態註冊服務？
- A簡: 啟動時呼叫 ConsulCatalog/Agent API 註冊，關閉時反註冊，並維護 TTL 心跳或 HTTP 檢查。
- A詳: 具體步驟：1) 引入 Consul 客戶端套件；2) 啟動時註冊；3) 維持健康檢查；4) Stop 時反註冊。程式碼：
  ```
  var consul = new ConsulClient();
  await consul.Agent.ServiceRegister(new AgentServiceRegistration {
    ID="notify-1", Name="notify", Address=ip, Port=port,
    Tags=new[]{"tier:plus"}, Check=new AgentServiceCheck{HTTP=$"http://{ip}:{port}/health", Interval=TimeSpan.FromSeconds(5)}
  });
  // On shutdown:
  await consul.Agent.ServiceDeregister("notify-1");
  ```
  注意：處理失敗重試、ID 唯一、與容器生命週期對齊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q10, D-Q1

C-Q5: 如何在 .NET 實作 Client-side Discovery 與重試？
- A簡: 查詢 Consul 取得健康實例，套用標籤過濾與輪詢，設定逾時/退避重試與熔斷。
- A詳: 具體步驟：1) 查詢服務健康：
  ```
  var res = await consul.Health.Service("notify", "tier:plus", passingOnly:true);
  var targets = res.Select(x=>x.Service);
  ```
  2) 自建 LB 選擇；3) 使用 HttpClient 設逾時；4) Polly 設重試/熔斷。注意：僅對冪等請求重試；合併短時間內相同查詢；快取與過期。最佳實踐：記錄指標（成功率、延遲）、超時分層（連線/總逾時）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q7, D-Q3

C-Q6: 如何以 Tags 實作不同 SLA 客群的路由？
- A簡: 以租戶資料取得 SLA，查詢時過濾對應標籤（如 tier:plus），確保高階客戶用高冗餘群組。
- A詳: 具體步驟：1) 資料庫維護 tenant→SLA；2) 註冊實例加標籤 tier:free/std/plus；3) 呼叫前解析租戶 SLA，查詢相符標籤；4) 權重偏向多 AZ。程式碼參考 C-Q5 查詢時加第二參數標籤。注意：預設回退策略（plus 落到 std 時告警）、標籤治理與審核流程。最佳實踐：與計費/合約系統對齊，監控 SLA 兌現率與例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q5, D-Q8

C-Q7: 如何用權重與標籤做金絲雀發布？
- A簡: 標記新版本為 canary，逐步提高權重，監控指標不佳即回退到穩定版本。
- A詳: 具體步驟：1) 註冊 v1（stable）與 v2（canary）實例；2) 在 Mesh/Sidecar/SDK 設定權重（5%→25%→50%→100%）；3) 實作自動監控門檻觸發回退。設定示例（概念）：
  ```
  route: service=notify
    match: tags.canary=true
    weight: 10
  ```
  注意：選取冪等路徑先行、分批租戶、灰度時間充分。最佳實踐：觀測指標要業務導向（轉換率、錯誤），自動化回退。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, D-Q8, B-Q14

C-Q8: 如何用 consul-template 為 NGINX 產生 upstream？
- A簡: 渲染模板為 NGINX 後端清單，動態跟隨 Consul 健康變更並熱更新。
- A詳: 具體步驟：1) 安裝 consul-template；2) 撰寫模板 upstream.ctmpl；3) 啟動監控服務目錄並渲染；4) 透過命令熱加載 NGINX。模板片段：
  ```
  upstream notify {
    {{range service "notify"}}
      server {{.Address}}:{{.Port}} max_fails=3 fail_timeout=10s;
    {{end}}
  }
  ```
  命令：
  ```
  consul-template -template "upstream.ctmpl:/etc/nginx/conf.d/upstream.conf:nginx -s reload"
  ```
  注意：節流重載、過濾標籤、設定健康檢查與超時一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, A-Q3, D-Q4

C-Q9: 如何用 Envoy Sidecar 與 Consul 整合？
- A簡: 以 Consul/控制面提供服務清單與證書，Envoy 作資料平面實作路由、重試與 mTLS。
- A詳: 具體步驟：1) 部署 Consul/或整合控制面；2) 每服務旁佈 Envoy Sidecar；3) 配置 CDS/EDS 從 Registry 拉取；4) 設置路由與重試。Envoy 片段（概念）：
  ```
  clusters:
  - name: notify
    type: EDS
    connect_timeout: 0.25s
    lb_policy: ROUND_ROBIN
  ```
  注意：證書與 mTLS 生命週期、資源限制、觀測導入（stats、tracing）。最佳實踐：以基礎路由先行，逐步開啟熔斷與金絲雀。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q11, A-Q12, B-Q15

C-Q10: 如何建立服務健康與 SLA 監控告警？
- A簡: 以 Consul 健康狀態與請求指標輸出至 Prometheus，設定 SLA 門檻告警與報表。
- A詳: 具體步驟：1) 啟用 Consul/Sidecar 指標輸出；2) Prometheus 抓取 metrics；3) 設定 Recording Rules 計算可用性；4) 建立 Alertmanager 告警；5) Grafana 可視化 SLA。設定示例（概念）：
  ```
  alert: ServiceDown
  expr: sum(rate(http_requests_total{status!="2xx"}[5m])) > 0 and on(service) consul_health{status="critical"}==1
  ```
  注意：定義 SLA 規則（99.9/99.99）、屏蔽維護窗口、區分租戶層級。最佳實踐：將 SLA 兌現與賠償流程連動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q3, D-Q8


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 服務沒有出現在發現清單怎麼辦？
- A簡: 檢查註冊流程、ServiceID 唯一性與 ACL；確認 Agent/Server 正常與配置目錄正確。
- A詳: 問題症狀：查詢不到服務、DNS 無解析、UI 無紀錄。可能原因：未註冊/註冊失敗、ServiceID 重複、ACL 拒絕、Agent 未連線。解決步驟：1) 檢查註冊日誌與 API 回應；2) 驗證 Agent 成員狀態；3) 確認 ACL Token；4) 修正 ServiceID 與名稱；5) 重新載入/註冊。預防措施：啟動健康檢查前置驗證、CI/CD 自動化註冊測試、監控註冊失敗率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2, C-Q4

D-Q2: 健康檢查長期 critical/unhealthy 怎麼處理？
- A簡: 檢查端點可用性、超時與間隔；排查依賴失敗，調整檢查策略避免誤判與震盪。
- A詳: 症狀：UI 顯示 critical、流量被切離。原因：健康端點錯誤、超時太短、依賴失效、TTL 未送心跳。解決：1) 直連測試/日誌；2) 放寬超時與間隔；3) 區分就緒與存活；4) 修復依賴或降級；5) 恢復 TTL 心跳。預防：標準化健康端點、監測 flapping、設定 deregister 清理殘留、預先演練故障。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q3, D-Q10

D-Q3: 呼叫端常卡在 30 秒逾時，如何診斷與改善？
- A簡: 落實客戶端逾時/重試/熔斷，使用 Discovery 過濾不健康節點，縮短長等待。
- A詳: 症狀：用戶端長等待、執行緒耗盡。原因：靜態設定、不健康節點仍被選、無逾時或過長、盲目重試。解決：1) 導入 Discovery 與健康過濾；2) 設連線/讀寫/總逾時；3) 針對冪等請求設定退避重試；4) 熔斷連續失敗。預防：端到端逾時策略、指標驅動調參、壓測校正、避免多層重試疊加。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q7, C-Q5

D-Q4: LB 故障造成全站不可用，如何降低單點風險？
- A簡: 內部流量導入 Client-side/Sidecar 分散決策，LB 僅作邊界；多實例並設健康探活。
- A詳: 症狀：LB 掛掉或配置錯誤導致大面積故障。原因：集中式單點、無熱備、過度依賴。解決：1) LB 雙活與健康檢查；2) 內部服務採 Client-side 或 Mesh；3) 災難切換演練；4) 配置變更審核。預防：設計去中心化架構、限縮 LB 職責於外部入口、以模板與自動化減少誤配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q13, C-Q8

D-Q5: 註冊中心延遲高或過載怎麼處理？
- A簡: 擴充叢集、優化快取與事件、降低查詢頻率；使用 stale 讀與退化模式。
- A詳: 症狀：查詢慢、超時、選路延遲。原因：讀寫壓力大、事件風暴、資源不足。解決：1) 水平擴充與調優；2) 啟用客戶端快取與觀察者；3) 設定查詢退避與合併；4) 允許短時間 stale 讀。預防：容量規劃、分區與多 DC、限制不必要的查詢、監控 QPS 與延遲。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q1, B-Q12

D-Q6: 叢集選舉失敗或 split-brain 如何面對？
- A簡: 檢查網路分區與節點數，確保奇數節點跨可用區，手動降級與恢復共識。
- A詳: 症狀：無法寫入、狀態不一致。原因：網路分區、節點不足、時鐘漂移。解決：1) 檢查網路與防火牆；2) 確保過半節點可通訊；3) 重啟有問題節點；4) 暫停寫入至恢復。預防：奇數節點跨 AZ、時鐘同步、健康監控與自動告警、混沌演練。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q9, C-Q1

D-Q7: 維護或下線節點仍被導流，如何排除？
- A簡: 使用標籤或維護旗標暫停流量，設 deregister 與就緒檢查，完成後再下線。
- A詳: 症狀：維護節點仍接請求。原因：未下調就緒、快取滯後、deregister 未配置。解決：1) 將 readiness 置為失敗；2) 設維護模式或移除標籤；3) 等待 TTL/快取過期；4) 確認 deregister_critical_service_after。預防：藍綠切換流程、運維控制面一鍵維護、部署前後檢查清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q2

D-Q8: 錯誤的 SLA 標籤導致客訴，如何修正？
- A簡: 建立標籤審核與自動驗證，回退錯誤導流，補償並修補流程與監控。
- A詳: 症狀：高階客戶被導至低冗餘節點、體驗下降。原因：標記錯誤、映射邏輯缺陷、變更未審核。解決：1) 立即回退標籤或策略；2) 重新計算租戶映射；3) 溝通賠償；4) 增加自動驗證（測試流量校驗）。預防：標籤治理規範、雙人審核、灰度策略變更、SLA 監控告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q6, C-Q10

D-Q9: 跨區路由造成高延遲，如何診斷與優化？
- A簡: 啟用區域感知，優先同區；分析延遲來源，僅在本區失效時跨區回退。
- A詳: 症狀：RTT 升高、錯誤率上升。原因：未標記區域、權重配置不當、跨區作為常態。解決：1) 為實例標記 AZ/DC；2) 改策略優先同區；3) 設跨區為回退；4) 監控跨區佔比與延遲。預防：就近路由默認、容量冗餘、路由測試與壓測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q6, B-Q5

D-Q10: 健康檢查震盪（flapping）如何處置？
- A簡: 增加抖動抑制、調整間隔與超時、拆分就緒與存活，避免頻繁上下線。
- A詳: 症狀：狀態頻繁在健康/不健康之間切換。原因：閾值過嚴、依賴抖動、網路波動。解決：1) 增加重試與抑制；2) 放寬超時或間隔；3) 就緒與存活分離；4) 針對依賴做快取與降級。預防：壓測校準檢查、觀測趨勢、在高峰前凍結變更。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q2, C-Q3


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Service Discovery？
    - A-Q2: 微服務為何需要 Service Discovery？
    - A-Q3: DNS+ELB 與 Service Discovery 有何差異？
    - A-Q4: 什麼是 Service Registry？
    - A-Q5: 健康檢查在 Service Discovery 的角色是什麼？
    - A-Q7: 為何僅用應用程式設定（Config）不足？
    - A-Q8: 為什麼傳統 LB 可能成為單點或瓶頸？
    - A-Q9: 什麼是 SLA？與 Service Discovery 有何關聯？
    - A-Q10: 服務標籤（Tags/Metadata）是什麼？有何價值？
    - B-Q1: Service Discovery 整體如何運作？
    - B-Q2: 服務如何註冊到 Registry？
    - B-Q3: 健康檢查機制與狀態流轉是什麼？
    - C-Q1: 如何用 Docker Compose 快速建立本機 Consul 叢集？
    - C-Q2: 如何以靜態檔案在 Consul 註冊服務？
    - C-Q3: 在 .NET 如何實作 HTTP 健康檢查端點？

- 中級者：建議學習哪 20 題
    - A-Q6: Client-side 與 Server-side Discovery 的差異？
    - A-Q11: 什麼是 Sidecar 模式？
    - A-Q13: API Management 與 Service Discovery 的差異與互補？
    - A-Q14: 為何開發與運維都需理解 Service Discovery？
    - A-Q15: Cloud Native 與 Service Discovery 的關聯？
    - B-Q4: Client-side Discovery 的請求流程為何？
    - B-Q5: 如何以標籤實現 SLA 分級路由？
    - B-Q6: 版本導向的藍綠/金絲雀路由如何運作？
    - B-Q7: 逾時、重試與熔斷如何與 Discovery 協同？
    - B-Q9: Consul 的架構與關鍵組件？
    - B-Q10: 在容器與動態 IP 環境中如何做 Discovery？
    - B-Q11: 多資料中心/可用區感知路由如何設計？
    - B-Q12: Discovery 與 DNS 的整合方式？
    - B-Q13: 反向代理/NGINX/HAProxy 如何與 Discovery 協作？
    - C-Q4: 如何在 .NET 透過 Consul API 動態註冊服務？
    - C-Q5: 如何在 .NET 實作 Client-side Discovery 與重試？
    - C-Q6: 如何以 Tags 實作不同 SLA 客群的路由？
    - C-Q7: 如何用權重與標籤做金絲雀發布？
    - C-Q8: 如何用 consul-template 為 NGINX 產生 upstream？
    - D-Q3: 呼叫端常卡在 30 秒逾時，如何診斷與改善？

- 高級者：建議關注哪 15 題
    - B-Q8: 註冊中心的高可用與一致性如何設計？
    - B-Q14: 從 Discovery 演進到 Sidecar/Service Mesh 的路徑？
    - B-Q15: Discovery 與安全（ACL、mTLS）如何結合？
    - C-Q9: 如何用 Envoy Sidecar 與 Consul 整合？
    - C-Q10: 如何建立服務健康與 SLA 監控告警？
    - D-Q4: LB 故障造成全站不可用，如何降低單點風險？
    - D-Q5: 註冊中心延遲高或過載怎麼處理？
    - D-Q6: 叢集選舉失敗或 split-brain 如何面對？
    - D-Q7: 維護或下線節點仍被導流，如何排除？
    - D-Q8: 錯誤的 SLA 標籤導致客訴，如何修正？
    - D-Q9: 跨區路由造成高延遲，如何診斷與優化？
    - D-Q10: 健康檢查震盪（flapping）如何處置？
    - B-Q5: 如何以標籤實現 SLA 分級路由？
    - B-Q6: 版本導向的藍綠/金絲雀路由如何運作？
    - B-Q11: 多資料中心/可用區感知路由如何設計？