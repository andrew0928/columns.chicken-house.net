---
layout: synthesis
title: "Azure Labs: Mixed-OS Docker Swarm"
synthesis_type: faq
source_post: /2017/07/25/wc-swarm-labs2/
redirect_from:
  - /2017/07/25/wc-swarm-labs2/faq/
postid: 2017-07-25-wc-swarm-labs2
---

# Azure Labs: Mixed-OS Docker Swarm

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Docker Swarm？
- A簡: Docker 原生的容器編排引擎，提供叢集管理、調度、自我修復與服務發布。
- A詳: Docker Swarm 是 Docker 內建的叢集編排模式，將多台節點（Manager/Worker）組成單一邏輯叢集，透過 service 定義期望狀態，調度器將 task 分派到節點執行，並具備自我修復、滾動更新、服務發佈與內建 overlay 網路與 DNS 能力。開發到生產可一致化，簡化部署與運維，特別適合微服務架構與混合 OS 場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, A-Q10, B-Q1

A-Q2: 什麼是 Mixed-OS Docker Swarm？
- A簡: 同一 Swarm 叢集中同時包含 Windows 與 Linux 節點，協同運行各自容器。
- A詳: Mixed-OS Swarm 指在同一個 Docker Swarm 叢集中，加入不同作業系統的節點（如 Windows Server 容器節點與 Linux 節點），再以標籤與調度約束控制服務只能在相容的 OS 上執行。此法可在單一叢集中運行 ASP.NET（Windows）與 Nginx（Linux）等最佳化技術組合，降低多叢集維運成本，符合「用最適合的技術解決特定領域問題」的架構理念。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q12, B-Q2, C-Q1

A-Q3: 為什麼需要混合 Windows 與 Linux 的容器環境？
- A簡: 讓每個領域使用最佳技術，支援既有 .NET 與開源生態，提升彈性與效率。
- A詳: 實務上團隊會同時面對 Legacy .NET Framework 與 Linux 生態（如 Nginx、各類 OSS）。Mixed-OS 讓你在一個叢集內就能部署 Windows 與 Linux 容器，各自承載最適解，避免被單一 OS 或 Framework 侷限。好處包括：更貼近真實生產架構、降低多環境同步成本、加速 CI/CD 與團隊協作、逐步走向微服務以降低全面重寫風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q16, B-Q14, C-Q10

A-Q4: Swarm 節點角色（Manager/Worker）是什麼？
- A簡: Manager 負責控制與調度，Worker 負責執行 task；可多 Manager 容錯。
- A詳: Swarm 中節點分為 Manager 與 Worker。Manager 維護叢集狀態、接收使用者指令、執行排程與 Raft 共識；Worker 接收指派的 task 實際運行容器。Manager 可多台容錯，選出 Leader，其餘為 Reachable。加入節點時用不同 join token 指定角色。小叢集可單一 Manager，大叢集建議奇數多 Manager 提升可用性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q10, C-Q2, D-Q7

A-Q5: 什麼是 Swarm 的 Join Token？worker/manager 有何差異？
- A簡: 加入叢集的認證憑證；worker 與 manager 各自使用不同 token。
- A詳: docker swarm join-token 會產生角色專屬 token 與加入指令。新節點執行對應命令後，經由 TCP 2377 與 Manager 建立信任並加入叢集。使用 worker token 只能成為 Worker，manager token 才能成為 Manager。為安全，token 可輪換。誤用角色會造成風險或資源浪費，務必管理好分發與過期。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q22, C-Q2, D-Q9

A-Q6: 什麼是節點標籤（Node Labels）與調度約束（Constraints）？
- A簡: Labels 為節點加註屬性；Constraints 用於限制服務只在符合條件節點運行。
- A詳: 透過 docker node update --label-add key=value 可為節點加上可查詢的標籤，常見如 os=windows/linux。建立服務時用 --constraint 'node.labels.os==linux' 等語法，讓調度器只在相符節點放置 task。這是 Mixed-OS 中避免 OS 不相容失敗重試的關鍵機制，也可用於資源池隔離、區域化部署與硬體特徵定向調度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q3, C-Q4, D-Q1

A-Q7: 什麼是 Routing Mesh？文中 Windows 支援現況為何？
- A簡: 讓節點對外同一入口分流至任一副本；文中指出 Windows 尚未完整支援。
- A詳: Routing Mesh 是 Swarm 的服務發布機制之一，對外在所有節點公開相同服務埠，流量由內部虛擬 IP 與負載分配導至任一副本。文中時間點，Windows 容器側對 routing mesh 與網路能力支援不足，導致作者以 Nginx 在 Linux 上示範負載平衡，並觀察官方示範以外部 Nginx 靜態配置動態埠的折衷做法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q8, D-Q6, A-Q13

A-Q8: 什麼是 Docker 原生 DNS（127.0.0.11）？
- A簡: Docker 內建的容器 DNS 伺服器，提供服務名與容器名解析。
- A詳: 每個容器的 /etc/resolv.conf 會指向 127.0.0.11，透過 Docker 內建 DNS 解析同網路內的服務名稱與別名。Swarm 中可解析到服務 VIP（VIP 模式）或多個 A 記錄（DNSRR 模式）。文中以 BusyBox 測試在 Linux 容器能查到伺服器位址但服務名解析失敗，指出可能配置或平台支援差異需進一步診斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q6, B-Q5, D-Q3

A-Q9: 什麼是 DNSRR（DNS Round Robin）端點模式？
- A簡: 以 DNS 提供多個 A 記錄，客戶端自行輪詢分流至各副本。
- A詳: 建立服務加上 --endpoint-mode dnsrr 時，不再使用 VIP 轉發，而是讓內建 DNS 回應多筆副本 IP，客戶端採輪詢或隨機選擇。此模式可避開某些 VIP/routing mesh 限制，但要求客戶端具備連線重試與多目標能力。文中測試在 Linux 上仍查不到服務名，指向 DNS 設定/支援有落差，需結合日誌與網路檢查追因。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q3, D-Q4, A-Q8

A-Q10: 服務（Service）、任務（Task）、副本（Replica）的關係？
- A簡: Service 定義期望狀態；Replica 為副本數；Task 為具體執行單元。
- A詳: 在 Swarm 中，Service 定義映像、環境與副本數（replicas），調度器據此創建多個 Task，分派至節點實際運行容器。service ps 可觀察每個 Task 的目標/目前狀態與錯誤訊息。縮放服務會增減 Task 數。理解三者關係有助診斷失敗重試、擴縮容與資源分配行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q4, D-Q2, A-Q6

A-Q11: 什麼是 Overlay 與 ingress 網路？
- A簡: Overlay 跨主機虛擬網路；ingress 為預設負載分流/服務發布網路。
- A詳: Overlay 網路透過 VXLAN 等技術在多節點間建立 L2/L3 覆蓋，提供容器跨主機互通與服務發現。ingress 是 Swarm 預設用於服務發布與（在支援平台上）routing mesh 的特殊 overlay。服務連到 ingress 可被節點上的代理接收再分發至副本。正確理解網段與連線路徑，有助於多 OS 通訊與除錯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q4, A-Q8

A-Q12: Windows 容器與 Linux 容器在 Swarm 中的差異？
- A簡: 映像相容性、網路堆疊與功能支援度不同，需以標籤與約束隔離。
- A詳: Windows 與 Linux 容器映像不可互通；網路與 DNS、routing mesh、iptables 等底層機制有差異。文中觀察 Windows 在原生 DNS 與 mesh 支援不足，導致服務名解析與負載分流受限。因此必須用 node labels 與 constraints 精準調度，並針對平台限制設計替代方案（如外部 Nginx 或直連副本）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, B-Q12, D-Q6

A-Q13: Nginx 在文中示範扮演什麼角色？
- A簡: 作為 Linux 上的反向代理與負載平衡，分流到多個 Web 副本。
- A詳: 由於 Windows 容器側 routing mesh 能力不足，文中以 Linux 節點上的 Nginx 服務示範負載平衡，發布在 ingress 網路與 80 埠，再反向代理至多個 Web 副本。作者也評析官方示範使用外部 Nginx 靜態配置動態埠的做法，指出在擴縮或重啟時需頻繁改檔並重載，維運成本高。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q4, D-Q8, A-Q7

A-Q14: 什麼是 Swarm 的自我修復機制？利與弊？
- A簡: 監控期望與實際狀態，失敗即重建；若條件不符會無限重試耗資源。
- A詳: Swarm 維持 service 的期望狀態，當容器失敗、節點離線或健康檢查不通時會自動重排或重啟 Task。優點是提高可用性與自動復原；缺點是在條件根本不符（如 Linux 映像排到 Windows 節點）時會持續重試，造成資源浪費與雜訊。因此要搭配 labels/constraints 與健康檢查正確配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q11, D-Q2, D-Q10

A-Q15: 在 Azure 上部署 Swarm 有哪些網路考量？
- A簡: 節點需在同一虛擬網路/VNet 子網，開放管理與疊加網路必要埠。
- A詳: 文中在 Azure 建立多台 VM，必須確保皆位於同一 VNet/子網，避免誤建於 Classic 或不同 VNet 導致互 ping 不通。需開放 2377（swarm 管理）、7946/TCP+UDP（節點通訊）、4789/UDP（overlay VXLAN）等埠。網段規劃與 NSG 設置正確，才能讓跨節點 overlay 正常運作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q1, D-Q7, A-Q11

A-Q16: 微服務如何幫助異質系統共存？
- A簡: 以服務為邊界，讓不同技術獨立演進並透過標準協議協作。
- A詳: 微服務將系統拆成小型自治服務，以 API/消息等標準協議整合。這讓 .NET Framework、.NET Core、Linux 生態可在同一架構共存，各自選擇最適合的 OS/Runtime。容器化進一步統一部署單位與運行環境，降低改寫成本，允許漸進式演進，適合面對未來 5-10 年 Windows 與 Linux 並存的現實。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, C-Q10, B-Q25(延伸), D-Q8

### Q&A 類別 B: 技術原理類

B-Q1: 節點加入 Swarm 的流程如何運作？
- A簡: 透過 join-token 與 TCP 2377 與 Manager 建立信任並註冊角色。
- A詳: 叢集初始化後，Manager 生成 worker/manager 兩種 token。新節點以 docker swarm join --token ... 10.0.0.x:2377 向 Manager 與 Raft 狀態機註冊，完成 TLS/憑證交換與角色設定。成功後 node ls 可見新節點。這依賴可達的管理埠與正確 VNet 路由，否則會卡在握手階段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, C-Q2, D-Q7

B-Q2: 為何未加約束時 Linux 服務會被排到 Windows 節點？
- A簡: 調度器預設僅依資源與健康度，不辨識映像 OS，相容性需自行管控。
- A詳: Swarm 調度器不會解析映像 OS 屬性，若無 constraints，會依資源可用、散佈策略與親和性等因素分派 task。Linux 映像排到 Windows 節點會拉取失敗，task 進入 Rejected 並觸發自我修復重試。這凸顯在 Mixed-OS 必須以 labels/constraints 明確限定可用節點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q1, D-Q2

B-Q3: 加上 Labels 與 Constraints 後調度流程有何變化？
- A簡: 調度器先過濾符合約束的節點，再依資源與策略選擇放置。
- A詳: 建立服務時指定 --constraint 'node.labels.os==linux'，調度器先以此條件過濾節點池，僅在符合標籤的節點中考量 CPU/記憶體、散佈、親和/反親和等，最終決定 task 放置位置。這將 OS 相容性納入硬限制，避免不必要的重試與跨 OS 拉取錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q4, D-Q10

B-Q4: Routing Mesh 的原理與限制是什麼？
- A簡: 以 VIP 與節點代理在所有節點公開埠並分流至任一副本；平台支援度關鍵。
- A詳: Swarm 為服務設置一個虛擬 IP（VIP），在所有節點上開啟對應埠，流量由內核或代理轉發至背後任一副本（不論副本在哪一節點）。此仰賴底層網路堆疊、iptables/HNS 能力。文中指出 Windows 當時支援不足，導致實測需以外部 Nginx 或直連方式替代。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q8, D-Q6

B-Q5: DNSRR 模式背後機制與解析流程為何？
- A簡: 內建 DNS 回傳多 A 記錄，客戶端自選目標；無 VIP/代理轉發。
- A詳: 啟用 --endpoint-mode dnsrr 時，服務名解析回應多個容器 IP，客戶端直接連各副本。此模式簡化轉發層、降低單點，但要求客戶端處理連線失敗重試與分流策略。若解析失敗，需檢查容器的 resolv.conf、Docker DNS 進程與網路命名域是否一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q8, D-Q3

B-Q6: Docker 原生 DNS 如何提供服務發現？
- A簡: 在容器內監聽 127.0.0.11，解析服務/容器名至 VIP 或多 IP。
- A詳: Docker 在每個 network namespace 啟動內建 DNS 轉譯層，收集 network 內的服務與容器記錄。VIP 模式回應服務 VIP；DNSRR 回應多 IP。它也會處理 search domain 與別名。平台實作差異（如 Windows HNS）可能影響可用性，需要以 nslookup/dig 驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, D-Q3, D-Q5

B-Q7: Overlay 網路跨節點通訊的機制是什麼？
- A簡: 以 VXLAN 封裝 L2/L3 流量穿越底層網路，節點以控制面同步拓撲。
- A詳: 建立 overlay 後，Docker 在節點間透過 gossip/控制面維護網路狀態，資料面以 VXLAN（UDP 4789）封裝容器間封包。需開放對應埠、節點可互通且在同一 VNet/路由可達。否則會出現 ping 不通或單向可達的問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q15, D-Q7

B-Q8: 服務發布埠與 ingress 的協作機制？
- A簡: -p 對外開埠綁到 ingress；支援平台上由 mesh 代理分流至副本。
- A詳: docker service create -p 80:80 會在 ingress 上公開 80 埠。支援 routing mesh 的平台會在所有節點開埠並轉發；否則需在有副本的節點連線或以外部代理。需留意安全組態、碰撞與動態埠策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q5, D-Q6

B-Q9: service ps 的狀態欄位表示什麼？
- A簡: Desired 期望、Current 目前狀態、Error 顯示失敗原因與回合歷史。
- A詳: docker service ps <svc> 列出每個 task 的節點、期望狀態（如 Running）、目前狀態（含時間）、以及 Error 訊息。Rejected/Failed 表示拉取或啟動失敗；Shutdown 往往是重試輪替。此輸出是定位 OS 不相容、映像不存在或授權失敗的首要線索。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, D-Q2, C-Q8

B-Q10: Manager 的 Leader/Reachable 與 Raft 的關係？
- A簡: 多 Manager 以 Raft 共識選 Leader；其他為 Reachable 以容錯。
- A詳: Swarm 使用 Raft 儲存叢集狀態，奇數台 Manager 維持多數決。Leader 接受寫入指令；Reachable 為可參與投票的追隨者，Leader 故障時自動選舉新 Leader。部署上建議 3/5 台 Manager 分散不同可用區，避免單點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, D-Q7, C-Q2

B-Q11: 自我修復（reconciliation loop）如何運作？
- A簡: 週期性比對期望與實際，發現偏差即重建/遷移 Task。
- A詳: Swarm 監控節點心跳與 Task 狀態，當容器退出、健康檢查失敗、節點失聯，會將 Task 標記不符並觸發重新排程。若根因未解（如 OS 不相容），會持續重試。可透過限制重試、調整健康檢查、正確約束降低無謂循環。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q2, A-Q6

B-Q12: 不同 OS 節點拉取映像的行為與限制？
- A簡: 節點僅能拉取同 OS/架構映像；異 OS 會報映像不存在或不相容。
- A詳: docker pull 會解析 manifest 與平台資訊，Windows 節點無法拉 Linux 映像，反之亦然。service ps 會顯示 "No such image" 或類似錯誤。需在建立服務時加上 OS 約束，或為不同 OS 分別建立服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q1, C-Q4

B-Q13: endpoint-mode 對連線與負載分配的影響？
- A簡: vip 模式透過代理/轉發，dnsrr 由客戶端直連多目標，行為差異大。
- A詳: endpoint-mode=vip 為預設，以 VIP 與節點代理共同分流，對客戶端透明；endpoint-mode=dnsrr 讓 DNS 回多 IP，客戶端負責選擇與重試。選擇取決於平台支援與應用特性。文中測到 dnsrr 解析失敗，顯示需驗證 DNS 與網路配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q6, D-Q3

B-Q14: 外部 Nginx 靜態配置動態埠的風險原理？
- A簡: 服務擴縮/重啟導致埠改變，需人工改檔重載，易出錯且不可持續。
- A詳: 官方示範以叢集外 Nginx 反向代理直連每個副本的動態主機埠。當 Swarm 重排或副本擴縮時，埠改變將使 Nginx 配置失效，必須同步更新並重載。此耦合增加運維負擔，與動態擴縮理念衝突，僅可暫作權宜之計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, D-Q8, A-Q7

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Azure 建立 Windows Swarm 並新增 Linux 節點？
- A簡: 於同一 VNet 建立多 VM，初始化 Swarm，再以 join-token 加入 Linux。
- A詳: 步驟：1) 在 Azure 建立 Windows VM（wcs1-3）與 Linux VM（lcs4），同一 VNet/子網。2) 在 wcs1 初始化 Swarm。3) 開通 2377、7946 TCP/UDP、4789 UDP。4) 在 wcs1 查 worker token；於 lcs4 執行 docker swarm join --token ... 10.0.0.4:2377。5) node ls 驗證四節點。注意：避免 Classic/不同 VNet，否則互通失敗。最佳實踐：以 IaC 管控網路與安全組態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, A-Q15, D-Q7

C-Q2: 如何使用 join-token 將 Linux 節點加入為 worker？
- A簡: 在 Manager 取得 worker token，於 Linux 節點執行 join 指令即可。
- A詳: 步驟：1) Manager 執行 docker swarm join-token worker 取得命令與 token。2) 在 lcs4 貼上指令：docker swarm join --token SWMTKN-... 10.0.0.4:2377。3) 回到 Manager 執行 docker node ls 確認狀態為 Ready/Active。注意：IP 應指向 Manager；防火牆與 NSG 開通。安全：避免將 token 外洩，必要時 rotate。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q1, D-Q9

C-Q3: 如何為節點加上 os 標籤並驗證？
- A簡: 使用 docker node update --label-add os=windows/linux，node inspect 驗證。
- A詳: 步驟：1) 在 Manager 執行：docker node update --label-add os=windows wcs1/2/3；docker node update --label-add os=linux lcs4。2) 以 docker node inspect <node> 檢查 Spec.Labels。3) 若大量節點，使用命名空間化標籤如 os.type=linux。最佳實踐：標籤規範化、版本控管與自動化套用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q3, D-Q10

C-Q4: 如何建立只在 Linux 節點上運行的 Nginx 服務？
- A簡: service create 搭配 --constraint 'node.labels.os==linux' 指定放置。
- A詳: 指令示例：docker service create --name web --network ingress --replicas 3 -p 80:80 --constraint 'node.labels.os==linux' nginx。步驟：1) 先完成節點標籤。2) 建立服務並發布埠。3) service ls、service ps 驗證副本與節點。注意：若 Windows 不支援 mesh，流量應直連 Linux 節點或前置 Nginx。最佳實踐：加健康檢查與資源限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q8, A-Q7

C-Q5: 如何在 ingress 網路上發布多副本並開放 80 埠？
- A簡: 以 -p 80:80 與 --network ingress 建立 replicated 服務。
- A詳: 指令：docker service create --name web --replicas 3 --network ingress -p 80:80 nginx。步驟：1) 確認 ingress 存在。2) 建立服務。3) 透過節點 IP:80 測試。注意：Windows mesh 限制時，請測試在運行副本的節點上；或使用外部 LB。最佳實踐：以雲端 LB/Nginx 前置，配合健康檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, A-Q11, D-Q6

C-Q6: 如何在 Linux 服務中啟用 DNSRR 端點模式？
- A簡: 建立服務時添加 --endpoint-mode dnsrr，客戶端需支援多目標。
- A詳: 指令：docker service create --name ssh --endpoint-mode dnsrr --network ingress --constraint 'node.labels.os==linux' busybox sleep 86400000。步驟：1) 用 BusyBox 建示範服務。2) 進容器 nslookup 服務名驗證。注意：需確認 127.0.0.11 可用；應用端需具重試分流能力。最佳實踐：監控失敗率並評估是否改用 VIP。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q5, D-Q3

C-Q7: 如何用 BusyBox 驗證容器間連通與 DNS 狀態？
- A簡: docker exec 進入 BusyBox，使用 ping/nslookup 測試 IP 與服務名。
- A詳: 步驟：1) 找到 BusyBox 容器 ID（docker ps）。2) 執行 docker exec -ti <id> busybox ping <容器IP> 驗證 L3 通。3) 執行 busybox nslookup <服務名> 測 DNS。注意：確保相同 overlay 網路；檢查 resolv.conf 指向 127.0.0.11。最佳實踐：腳本化健康檢查，並紀錄結果排錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q6, D-Q4

C-Q8: 如何檢視 task 失敗與重試記錄以判斷 OS 不相容？
- A簡: 使用 docker service ps <svc> 檢視 CURRENT STATE 與 ERROR 欄位。
- A詳: 步驟：1) docker service ps <svc> 查看節點、Desired/Current、Error。2) 遇 "No such image: nginx@sha256..." 或 Rejected 多次，即疑似 OS 不相容或映像不存在。3) 驗證節點標籤與 constraints。最佳實踐：將 ps 輸出導入監控；設定告警門檻避免無限重試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, A-Q14, D-Q2

C-Q9: 如何規劃 labels 與 constraints 的長期治理？
- A簡: 設計命名規範、集中管理與自動化套用，避免配置漂移。
- A詳: 步驟：1) 制定標籤規範（如 os.type、role.zone、hw.gpu）。2) 以 IaC/腳本為節點套標籤。3) 服務模板統一定義 constraints。4) 定期審視標籤使用與清理。注意：避免臨時手動修改破壞一致性。最佳實踐：在 CI/CD 中驗證約束與標籤存在。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q3, D-Q10

C-Q10: 如何在混合叢集上部署 .NET 與 Nginx 的示範架構？
- A簡: Windows 節點佈署 .NET Web；Linux 節點佈署 Nginx，以 constraint 分流。
- A詳: 步驟：1) 為節點加上 os 標籤。2) 建立 .NET Web 服務：--constraint 'node.labels.os==windows'。3) 建立 Nginx：--constraint 'node.labels.os==linux' -p 80:80 --network ingress。4) 以外部 LB/反代接入。注意：Windows mesh 限制下，避免依賴 VIP；評估 DNSRR。最佳實踐：加健康檢查與資源限制，並自動化部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q13, B-Q8, D-Q8

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 新增 Linux 服務卻被排到 Windows 節點怎麼辦？
- A簡: 加上節點標籤並以 constraints 限定 OS，相容性由調度強制保證。
- A詳: 症狀：service ps 顯示被排到 Windows 節點，ERROR 顯示映像不存在或 Rejected。原因：未使用約束，調度器不辨 OS。解法：為節點加 os=windows/linux 標籤，重建服務加 --constraint 'node.labels.os==linux'。預防：建立服務模板與 CI 驗證，強制要求約束。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q2, C-Q4

D-Q2: Service 一直重試失敗的原因與處理？
- A簡: 常因 OS 不相容、映像不存在或埠/權限問題；檢視 ps 與日誌定位。
- A詳: 症狀：短時間多次 Rejected/Failed。原因：OS 不相容、私有 Registry 認證失敗、映像標籤錯誤、埠占用。解法：service ps 讀 ERROR；驗證 constraints、登入 registry、修正映像標籤、調整埠。預防：加健康檢查、資源限制、預先拉取映像與映像掃描。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q14, C-Q8

D-Q3: 容器內 nslookup 查不到服務名如何診斷？
- A簡: 檢查 127.0.0.11、所在網路、endpoint-mode 與平台支援差異。
- A詳: 症狀：nslookup <svc> 返回 can't resolve。原因：容器不在同 overlay、Docker DNS 未運作、Windows 平台支援不足、endpoint-mode 與期望不符。解法：檢查 resolv.conf 是否 127.0.0.11、docker network inspect、改用 VIP 模式測試。預防：部署前以 BusyBox 驗證網路與 DNS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q9, C-Q7

D-Q4: Ping 同網段 IP 成功但 DNS 不通的原因？
- A簡: L3 連通正常，DNS 服務或記錄缺失；需檢查內建 DNS 與網路定義。
- A詳: 症狀：ping 容器 IP OK，nslookup 失敗。原因：Docker DNS 未產生記錄、容器未連至相同網路、平台 DNS 綁定異常。解法：確認服務與測試容器在同 overlay；查看 docker logs、重建服務。預防：統一使用網路別名與標準化 network 鏡像配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, C-Q7

D-Q5: Windows 容器無法使用 127.0.0.11 的可能原因？
- A簡: 平台 HNS/DNS 實作限制或綁定異常；需改用 VIP/外部 DNS。
- A詳: 症狀：ping 127.0.0.11 可達但無法 nslookup。原因：Windows 原生 DNS 綁定未就緒或不支援對內建 DNS 查詢。解法：升級平台、改用 VIP 模式或外部 DNS/代理；在設計上避免依賴內建 DNS 行為。預防：在 PoC 階段完成平台相容性驗證並記錄差異。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q6, A-Q12

D-Q6: 無法透過 routing mesh 存取 Windows 服務怎麼辦？
- A簡: 直連副本節點或置前外部 Nginx/LB；評估 DNSRR 替代。
- A詳: 症狀：對任意節點的公開埠連線不通或不分流。原因：Windows 對 mesh 支援不足。解法：在運行副本的節點測試；以外部 Nginx/LB 代理；或用 DNSRR 讓客戶端直連副本。預防：在平台規格未完善前避免依賴 mesh，並設置監控自動切換策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q4, B-Q8

D-Q7: 節點加入失敗或不同 VNet 導致互通問題如何處理？
- A簡: 確認同一 VNet/子網與必要埠開放；修正路由與 NSG 規則。
- A詳: 症狀：join 卡住、節點互 ping 不通。原因：建立於 Classic/不同 VNet、NSG/防火牆阻擋 2377/7946/4789。解法：重建於同 VNet；開通必要埠；驗證私網 IP 與路由可達。預防：以 IaC 固化網路架構並檢查清單化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q7, C-Q1

D-Q8: 動態埠變動致外部 Nginx 配置失效怎麼辦？
- A簡: 改以服務名/VIP 或服務發現自動渲染配置，避免手動維護。
- A詳: 症狀：擴縮或重啟後 Nginx 指向的上游端口失效。原因：副本動態映射埠。解法：改用 ingress/VIP；或整合 Consul/etcd/Docker API 自動生成 upstream；部署模板化配置與熱重載。預防：避免硬編碼動態埠，選定穩定入口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, A-Q13, B-Q8

D-Q9: Join Token 洩漏或角色錯用如何緩解？
- A簡: 旋轉 token、最小權限分發、審計與自動化管理。
- A詳: 症狀：未知節點加入、權限過高。原因：token 洩漏或錯發 manager token。解法：docker swarm join-token --rotate；換發新 token；審計 node ls；撤銷可疑節點。預防：安全存放、過期策略、分發流程最小化；CI/CD 管理敏感資訊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q22(延伸), C-Q2

D-Q10: Label/Constraint 使用錯誤導致資源閒置如何修正？
- A簡: 檢查標籤正確性與一致性，修正約束後滾動更新服務。
- A詳: 症狀：服務無法部署或副本過少。原因：約束過嚴/拼寫錯、標籤未套用。解法：node inspect 驗證標籤；service inspect 檢查約束；修正後以 service update 滾動更新。預防：制定標籤規範、CI 驗證與變更記錄。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q3, C-Q9

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Docker Swarm？
    - A-Q2: 什麼是 Mixed-OS Docker Swarm？
    - A-Q3: 為什麼需要混合 Windows 與 Linux 的容器環境？
    - A-Q4: Swarm 節點角色（Manager/Worker）是什麼？
    - A-Q5: 什麼是 Swarm 的 Join Token？worker/manager 有何差異？
    - A-Q10: 服務（Service）、任務（Task）、副本（Replica）的關係？
    - A-Q11: 什麼是 Overlay 與 ingress 網路？
    - A-Q13: Nginx 在文中示範扮演什麼角色？
    - B-Q1: 節點加入 Swarm 的流程如何運作？
    - B-Q9: service ps 的狀態欄位表示什麼？
    - C-Q2: 如何使用 join-token 將 Linux 節點加入為 worker？
    - C-Q3: 如何為節點加上 os 標籤並驗證？
    - C-Q4: 如何建立只在 Linux 節點上運行的 Nginx 服務？
    - D-Q1: 新增 Linux 服務卻被排到 Windows 節點怎麼辦？
    - D-Q7: 節點加入失敗或不同 VNet 導致互通問題如何處理？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是節點標籤（Node Labels）與調度約束（Constraints）？
    - A-Q7: 什麼是 Routing Mesh？文中 Windows 支援現況為何？
    - A-Q8: 什麼是 Docker 原生 DNS（127.0.0.11）？
    - A-Q9: 什麼是 DNSRR（DNS Round Robin）端點模式？
    - A-Q12: Windows 容器與 Linux 容器在 Swarm 中的差異？
    - A-Q14: 什麼是 Swarm 的自我修復機制？利與弊？
    - A-Q15: 在 Azure 上部署 Swarm 有哪些網路考量？
    - B-Q2: 為何未加約束時 Linux 服務會被排到 Windows 節點？
    - B-Q3: 加上 Labels 與 Constraints 後調度流程有何變化？
    - B-Q4: Routing Mesh 的原理與限制是什麼？
    - B-Q5: DNSRR 模式背後機制與解析流程為何？
    - B-Q6: Docker 原生 DNS 如何提供服務發現？
    - B-Q7: Overlay 網路跨節點通訊的機制是什麼？
    - B-Q8: 服務發布埠與 ingress 的協作機制？
    - C-Q5: 如何在 ingress 網路上發布多副本並開放 80 埠？
    - C-Q6: 如何在 Linux 服務中啟用 DNSRR 端點模式？
    - C-Q7: 如何用 BusyBox 驗證容器間連通與 DNS 狀態？
    - C-Q8: 如何檢視 task 失敗與重試記錄以判斷 OS 不相容？
    - D-Q2: Service 一直重試失敗的原因與處理？
    - D-Q3: 容器內 nslookup 查不到服務名如何診斷？

- 高級者：建議關注哪 15 題
    - B-Q10: Manager 的 Leader/Reachable 與 Raft 的關係？
    - B-Q11: 自我修復（reconciliation loop）如何運作？
    - B-Q12: 不同 OS 節點拉取映像的行為與限制？
    - B-Q13: endpoint-mode 對連線與負載分配的影響？
    - B-Q14: 外部 Nginx 靜態配置動態埠的風險原理？
    - C-Q9: 如何規劃 labels 與 constraints 的長期治理？
    - C-Q10: 如何在混合叢集上部署 .NET 與 Nginx 的示範架構？
    - D-Q4: Ping 同網段 IP 成功但 DNS 不通的原因？
    - D-Q5: Windows 容器無法使用 127.0.0.11 的可能原因？
    - D-Q6: 無法透過 routing mesh 存取 Windows 服務怎麼辦？
    - D-Q8: 動態埠變動致外部 Nginx 配置失效怎麼辦？
    - D-Q9: Join Token 洩漏或角色錯用如何緩解？
    - D-Q10: Label/Constraint 使用錯誤導致資源閒置如何修正？
    - A-Q16: 微服務如何幫助異質系統共存？
    - A-Q7: 什麼是 Routing Mesh？文中 Windows 支援現況為何？