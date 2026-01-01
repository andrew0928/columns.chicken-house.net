---
layout: synthesis
title: "掃雷回憶錄 - Windows Container Network & Docker Compose"
synthesis_type: faq
source_post: /2017/01/15/docker-networks/
redirect_from:
  - /2017/01/15/docker-networks/faq/
postid: 2017-01-15-docker-networks
---
{% raw %}

# 掃雷回憶錄 - Windows Container Network & Docker Compose

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Windows Container Networking？
- A簡: Windows 上以 HNS/WinNAT 提供容器網路，預設使用 NAT，並透過 DNS 讓容器以名稱互通。
- A詳: Windows Container Networking 由 HNS 管理網路與端點，預設使用 WinNAT 建立 NAT 網路，為容器分配內部 IP、配置路由與防火牆。容器間的服務探索可用 DNS，以服務或容器名稱互相解析。在較新版本亦支援多 NAT 與 overlay（依版本而定），常見應用為單機開發、測試與以 compose 管理多服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q5

A-Q2: 什麼是 WinNAT？
- A簡: Windows 原生 NAT 實作，為容器提供位址轉換與轉送，限制是不支援 NAT loopback。
- A詳: WinNAT 是 Windows 的原生 Network Address Translation 元件，負責容器與外部網路之間的位址與連線轉換。它為預設 NAT 網路提供子網、閘道與端口轉發，且在新版本會自動建立對應的防火牆規則。不過 WinNAT 不支援 NAT loopback，導致主機無法透過自身映射端口回連容器服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, B-Q1

A-Q3: 什麼是 NAT loopback？
- A簡: 由主機用自身公網位址或映射端口回連內部服務的能力，WinNAT 不支援。
- A詳: NAT loopback（hairpin NAT）指內部用戶端以 NAT 之對外位址與端口，回連同一個 NAT 內部服務的能力。在許多家用路由器與 Linux iptables 可以啟用，但 Windows 的 WinNAT 尚未支援。因此主機上以 localhost:外部埠 或 自身對外 IP:外部埠 無法打回容器，需改用容器內部 IP 與原始埠或改由遠端主機測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q5, D-Q1

A-Q4: 為何在主機上無法用 localhost:port 存取容器？
- A簡: 因 WinNAT 不支援 NAT loopback，主機需用容器內部 IP 測試。
- A詳: 容器對外端口映射後，遠端主機以「主機IP:映射埠」可通。但在容器主機本機，因 WinNAT 不支援 loopback，localhost 或主機 IP 的映射端口不會被「髮夾」回送至容器。正確作法是使用 docker inspect 取得容器內部 IP，改以「容器IP:容器原始埠」測試；或改用其他遠端電腦以映射端口測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q1, C-Q2, D-Q1

A-Q5: 容器端點在主機上可如何連線？
- A簡: 以容器內部 IP 與原始服務埠連，或於遠端用主機IP:映射埠測試。
- A詳: 在主機上無法使用映射埠連入容器，需改：1) docker inspect 查容器內部 IP，使用「容器IP:容器埠」；2) 於遠端電腦使用「主機IP:映射埠」。Windows 14300 以上版本，對映射埠會自動建立防火牆規則，無須手動開孔，但僅適用於從外部存取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q1

A-Q6: Windows 上的 overlay network 支援狀態？
- A簡: 文章時點 Windows Server 2016 不成熟；後續 Windows 10 CU 開始支援 overlay。
- A詳: 文中時點（2017/01）Windows Server 2016 上 overlay 尚未可用，導致 Swarm 模式與跨主機網路受限。之後 Windows 10 Creators Update 新增 overlay 與多 NAT 支援，改善叢集能力。實務仍需確認系統版本、Docker 與 HNS 能力，再決定是否採用 overlay 與 Swarm。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q6, D-Q7

A-Q7: Docker Swarm 與 overlay 的關係是什麼？
- A簡: Swarm 以 overlay 建立跨主機虛擬網路，讓不同主機上的容器互通。
- A詳: Docker Swarm 需要 overlay driver 在多台主機間建立邏輯網路，容器連上同一 overlay 後可用服務名或 VIP 互通。缺少 overlay 意味著僅能單機或靠其他網路方案。Windows 早期不成熟，使得 Swarm 難以落地；新版本開始支援，但仍需測試兼容與穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q7

A-Q8: 什麼是 container linking？為何不建議？
- A簡: 舊式容器連線機制，Windows 不支援（或僅部分），已被網路與 DNS 取代。
- A詳: Linking 是早期 Docker 以 --link 建立容器間通道與環境變數的方式。Windows 官方標示不支援，實測僅部分功能似可通（例如某些連線），但 DNS 並未可靠運作。現代替代為使用網路與內建 DNS 解析服務名，或採用服務探索機制。建議不要依賴 --link。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, D-Q8

A-Q9: Windows 容器的 DNS 服務探索是什麼？
- A簡: 透過內建 DNS，將服務或容器名稱解析為容器內部 IP，供互通。
- A詳: 在預設 NAT 網路下，Docker 會將加入同一網路的容器名稱註冊進內部 DNS，彼此可用服務名直連。Compose 中服務名會對應多個容器 IP（多筆 A 紀錄），可被上游代理如 NGINX 用於負載平衡。需留意 Windows DNS 客戶端快取可能產生負面或過期快取，影響解析一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q2, D-Q2

A-Q10: nslookup 與 ping 在 DNS 上有何差異？
- A簡: nslookup直接詢問DNS伺服器，ping經過本機DNS快取，常見行為差異。
- A詳: nslookup 多半直接查詢指定 DNS 伺服器並回應紀錄；ping 則透過系統的 DNS Resolver，會先參考本機 DNS 快取。當快取存在「Name does not exist」等負面或過期紀錄時，ping 會失敗而 nslookup 可能成功，造成「查得到卻 ping 不到」的現象。Windows 可用 ipconfig /displaydns 與 /flushdns 檢視與清除。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q2, B-Q7, B-Q13

A-Q11: 為什麼會出現 DNS 負面快取（Name does not exist）？
- A簡: 服務未就緒時的查詢結果被快取，無 TTL 或長時間存在，導致後續解析失敗。
- A詳: 容器啟動階段若服務名尚未在 DNS 註冊完成，首次查詢回應「Name does not exist」，該結果會被本機快取保存。部分情況快取無顯示 TTL，導致長期保留，讓後續以 ping 或應用解析時持續失敗。需在應用啟動前加入等待或重試，並在必要時清除 DNS 快取以確保最新紀錄生效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q6, D-Q2

A-Q12: Docker Compose 的服務名稱解析有何特點？
- A簡: 服務名解析為多筆 A 紀錄對應多容器，但在 Windows 上受快取影響大。
- A詳: 當使用 docker-compose scale 擴充服務時，內部 DNS 會將同一服務名解析為多個 IP，供上游代理實現簡易負載。但在 Windows 上，DNS 客戶端的快取可能僅保留單一紀錄或留存舊結果，導致流量不平均或解析錯誤。需透過重載代理或清快取來與實際拓撲同步。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q5, B-Q14

A-Q13: 為何需要在 NGINX 處理 DNS 重新解析？
- A簡: 後端實例數變動時，上游需刷新解析結果，否則只打到舊 IP。
- A詳: 當後端服務經 scale 增減，服務名對應的 A 紀錄會改變。NGINX 預設會依 TTL 快取解析結果，Windows 的 DNS 與快取行為又可能不一致。因此若不在變更後重新解析，流量可能集中到少數或舊 IP。可採用 reload 設定檔、在啟動/變更後清快取、或使用 resolver 指令（依平台支持）降低不一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, C-Q7, D-Q3, D-Q5

A-Q14: 為什麼需要「等待服務就緒」而不只依賴 depends_on？
- A簡: depends_on 只保證啟動順序，不保證服務已健康可用。
- A詳: docker-compose 的 depends_on 僅確保容器啟動順序，並不等待應用程式完成初始化或 DNS 註冊，因此上游容器可能在後端尚未可用時啟動並解析失敗，造成負面快取。建議增加等待邏輯、健康檢查或重試機制，確保服務與 DNS 解析已就緒再啟動相依服務。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q6, D-Q4

A-Q15: NAT 與 overlay 在用途上的差異？
- A簡: NAT 適合單機與對外映射；overlay 適合跨主機叢集內部互通。
- A詳: NAT 將容器置於私有子網，透過主機端口映射提供外部存取，適合單機開發與簡單部署；overlay 在多主機間建立邏輯二層網路，容器可跨主機用服務名互通，適合 Swarm 或叢集。Windows 早期僅 NAT 成熟，overlay 後續版本才逐步可用，採用時需確認版本相容性與穩定性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, B-Q6

A-Q16: 什麼是 docker-compose 的 external network？
- A簡: 使用主機上已存在的 Docker 網路，例如預設 nat，而非由 compose 建立。
- A詳: 在 compose.yml 的 networks 設定中，若定義 default.external.name: nat，即指示使用主機現有名為 nat 的網路。這讓多個 compose 場景共享同一網路策略，也避免重複建立。若預設 nat 不可用，可先手動 docker network create 再由 compose 引用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q10, B-Q15

A-Q17: 為何 Windows 會自動建立映射埠的防火牆規則？
- A簡: WS2016 TP5/Build 14300 之後，Docker 為 NAT 映射自動加 inbound 規則。
- A詳: 自 Windows 10/Server 構建 14300 起，對 NAT 網路的端口映射，系統會全域性地新增對應防火牆 inbound 允許規則，無需手工開孔。這簡化了對外暴露服務的配置。不過僅影響外部連入，主機本機的 loopback 限制仍存在，測試方式仍需依規避方法進行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q9, B-Q12

A-Q18: Windows 10 Creators Update 對容器網路的影響？
- A簡: 新增 overlay 與多 NAT 支援，但可能導致既有 nat 網路失效需重建。
- A詳: Creators Update 帶來 overlay 與多 NAT 能力，擴大 Windows 容器網路彈性。然而升級後可能出現既有預設 nat 網路異常，表現為容器無法上網或路由失靈。實務解法是建立新 NAT 網路並將容器連上，問題即消失。顯示升級對既有 HNS 組態有潛在相容性風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, B-Q10

A-Q19: 為何建立新 NAT 網路可解決升級後連線問題？
- A簡: 新網路以乾淨設定重建 HNS/NAT 資源，避開舊組態殘留。
- A詳: 升級後，原 nat 可能因 HNS 狀態、IPAM 或 vSwitch 綁定出現不一致。新建 NAT 網路會以預設或指定子網重建驅動與端點，重新分配閘道與 DNS，避免舊資源殘留導致的路由或轉送故障。將新容器或既有服務改掛新網路後，連線即可恢復。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, B-Q10, D-Q6

A-Q20: docker network inspect 可看哪些關鍵資訊？
- A簡: 可見名稱、驅動、IPAM 子網與閘道、HNS id、已連容器等。
- A詳: docker network inspect 顯示網路詳細：Name/Id、Driver（nat/overlay）、IPAM 設定（Subnet/Gateway）、是否 Internal、已連容器清單、以及 Windows 專屬的 HNS id 與 networkname。發生連線問題時，對照子網、閘道與容器端點資訊，有助快速定位設定錯誤或資源不一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, B-Q10

A-Q21: 主機與遠端測試容器的差異？
- A簡: 遠端可用主機IP:映射埠；主機需用容器IP:原始埠或改用遠端測。
- A詳: 遠端測試遵循 NAT 典型外連入流程，映射埠通行；主機本機因不支援 loopback，映射埠不可用。正確本機測試方法是使用容器內部 IP 與服務原始埠，或改由另一台電腦透過主機IP:映射埠測試。此差異是 Windows 上最易誤解的測試陷阱。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, C-Q2

A-Q22: Windows 與 Linux 在容器網路成熟度差異？
- A簡: 文中時間點 Linux 較成熟；Windows 有 DNS 快取與功能缺口需繞路。
- A詳: 文中實測顯示 Linux 上 link/overlay/解析與代理的互動較穩定；Windows 容器在 NAT loopback、不完整的 link、DNS 快取行為與 overlay 可用性方面仍有限制。實務需以腳本等待、重載代理、或手工重建網路等方式繞過，待後續版本逐步完善。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q4, D-Q5

### Q&A 類別 B: 技術原理類

B-Q1: WinNAT 如何運作？為何不支援 loopback？
- A簡: WinNAT 以 HNS 管理 NAT 轉送與端口映射，缺 loopback 髮夾路徑處理。
- A詳: 技術原理說明: WinNAT 在主機建立 NAT 子網與閘道，透過端口映射將主機入站轉發至容器。關鍵流程: 1) HNS 建立 NAT 網路與端點；2) 分配容器 IP 與 DNS；3) 建立防火牆與轉發規則。核心組件: HNS、WinNAT、Windows 防火牆。因缺乏髮夾（hairpin）處理，主機對自身映射端口不回送至內部，故無 loopback。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q3, D-Q1

B-Q2: Windows 容器的 DNS 解析流程是什麼？
- A簡: 容器向指定 DNS 詢問，Windows 內建 DNS 客戶端會快取結果並影響解析。
- A詳: 技術原理說明: 容器加入網路後獲得 DNS 位址（多為 NAT 閘道或主機代理）。查詢流程: 應用→Windows DNS Client→（快取命中則返回）→DNS 伺服器→回應。核心組件: Windows DNS Client、Docker 提供的內部 DNS、HNS。快取層可能保存負面紀錄，導致 ping 失敗而 nslookup 成功的差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q10, D-Q2

B-Q3: docker-compose 的服務探索在 Windows 如何運作？
- A簡: 服務名對應多個容器 IP（A 紀錄），但受本機快取與代理重載影響。
- A詳: 技術原理說明: compose 建立服務時，每個副本在網路內註冊 A 紀錄。關鍵流程: 1) 服務啟動與 DNS 註冊；2) 查詢服務名得到多 IP；3) 上游代理輪詢或隨機選取。核心組件: Docker DNS、Windows DNS Client、代理（如 NGINX）。Windows 快取可能只留單一 IP，需透過 reload 或 flushdns 同步。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q7, D-Q5

B-Q4: 為何 --link 在 Windows 不可靠？
- A簡: Windows 官方不支援 link；實測僅部分路徑可通，DNS 不完整。
- A詳: 技術原理說明: link 依賴 Docker 於容器間注入環境與特定路由。關鍵流程: 啟動時解析連結目標、建立規則。核心組件: Docker Engine、HNS。Windows 端並未完整實作此機制與 DNS 整合，出現能 nslookup 卻 ping 不通等反常，建議改用網路與 DNS 的標準機制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, D-Q8

B-Q5: 端口映射在 Windows 的轉送流程？
- A簡: 外部連入主機埠，經防火牆允許後轉發至容器IP:容器埠，主機本機不 loopback。
- A詳: 技術原理說明: 1) 建立 mapping（hostPort→containerIP:containerPort）；2) 自動加防火牆 inbound 規則；3) WinNAT 將封包轉送。核心組件: HNS、WinNAT、Windows 防火牆。限制: 主機本機不做 hairpin，僅遠端可用映射埠，主機測試需以容器 IP 直連。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, D-Q1

B-Q6: Windows 上 overlay network 的設計概念？
- A簡: 以 HNS 提供跨主機虛擬網路，讓不同主機容器互通，需對應版本支持。
- A詳: 技術原理說明: overlay 在多主機間建立覆疊網路，隔離租戶並提供服務名解析。關鍵流程: 1) 建立 overlay 網路；2) 節點加入；3) 容器連線；4) 跨主機路由。核心組件: HNS overlay driver、Docker（Swarm mode）。Windows 版本演進中，部署前需確認驅動與叢集支持。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, A-Q7, D-Q7

B-Q7: DNS 負面快取對應用的影響與處理？
- A簡: 會讓應用長期解析失敗；需等待、重試或清除快取來復原。
- A詳: 技術原理說明: DNS Client 會快取 NXDOMAIN/Name not exist。關鍵流程: 應用啟動早於服務註冊→首次查詢失敗→負面快取生效。核心組件: Windows DNS Client、應用 resolver。處理: 延遲啟動與重試、加入啟動等待腳本、手動或自動 flushdns。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q6, D-Q2

B-Q8: NGINX 的 DNS 行為與 resolver 指令原理？
- A簡: 預設依 TTL 快取；resolver 可設定 DNS 與快取有效期，動態刷新上游。
- A詳: 技術原理說明: NGINX 在啟動或第一次解析上游主機名後快取結果，依 TTL 更新。關鍵流程: 解析→快取→依 TTL 重新解析。核心組件: NGINX 解析器、OS DNS。可用 resolver 指定 DNS 與 valid= 時間，減少對 OS 快取依賴。但在 Windows 上實測與範例較少，需驗證行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q5, D-Q3

B-Q9: ipconfig /displaydns 與 /flushdns 的作用機制？
- A簡: displaydns 顯示本機 DNS 快取；flushdns 清除它以迫使重新解析。
- A詳: 技術原理說明: Windows DNS Client 維護快取表，包含正面與負面紀錄。displaydns 列出快取內容與 TTL；flushdns 清空，讓下一次解析直詢 DNS 伺服器。核心組件: Windows DNS Client。此機制對容器內的 Windows 基底映像同樣適用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q2, C-Q8

B-Q10: docker network create -d nat 的行為？
- A簡: 建立新的 NAT 網路與 HNS 資源，配置子網與閘道，供容器掛載使用。
- A詳: 技術原理說明: 指令請求 HNS 建立一個新的 NAT 網路，分配子網與預設閘道。關鍵流程: 建網→生成 HNS id→IPAM 生效→容器連線。核心組件: Docker Engine、HNS、IPAM。創建新 NAT 可繞過舊網路的殘留或異常，常用於升級後的連線故障修復。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, C-Q9, D-Q6

B-Q11: depends_on 與「服務就緒」的差別？
- A簡: depends_on 僅序啟動，不等待健康或 DNS 註冊完成。
- A詳: 技術原理說明: compose 啟動流程依 depends_on 決定容器順序，但不檢查應用 readiness。關鍵流程: 容器起→應用初始化→健康可用。核心組件: docker-compose、應用自身健康。需要以 healthcheck、等待腳本或重試把關，避免上游先啟造成負面快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q6, D-Q4

B-Q12: 為何端口映射會自動新增防火牆規則？
- A簡: Docker 與 HNS 在建立映射時同步配置 Windows 防火牆入口規則。
- A詳: 技術原理說明: 當創建 -p host:container 映射，Windows 後端會在對應介面加入 inbound allow 規則。關鍵流程: 建映射→生成防火牆規則→允許入站。核心組件: Docker Engine、HNS、Windows 防火牆。減少手動配置，但仍不解決本機 loopback 限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, D-Q9

B-Q13: 為何 displaydns 會看到「Name does not exist」且無 TTL？
- A簡: 這是負面快取項；無 TTL 可能長期存在，需 flush 才更新。
- A詳: 技術原理說明: Windows 可能保存 NXDOMAIN 為一筆負面快取，作為快速回應來源。關鍵流程: 首次失敗→寫入負面項→後續解析命中快取。核心組件: Windows DNS Client。因少見顯示 TTL 行為，建議在應用啟動期間主動清除或採重試邏輯以避免卡死。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q2

B-Q14: 為何 scale 後服務名解析會有多筆 A 紀錄？
- A簡: 每個副本各有一個 IP，服務名解析回傳多 IP 供上游負載平衡。
- A詳: 技術原理說明: Docker DNS 會將同服務的副本端點都註冊到同一名稱。關鍵流程: scale N→產生 N 端點→DNS 以多 A 回應。核心組件: Docker DNS、HNS/IPAM。上游需支持多 IP 輪詢或重新解析，以達到均衡。Windows 快取可能破壞預期，需要 reload。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q5

B-Q15: compose 使用 external network 的運作？
- A簡: 直接掛接既有 Docker 網路，不由 compose 創建或刪除。
- A詳: 技術原理說明: external 指向主機已存在的網路名稱。關鍵流程: compose 啟動→查找外部網路→將容器加入。核心組件: docker-compose、HNS。適用於統一管理網路策略或繞開預設 nat 異常的情境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, C-Q10

B-Q16: 為何 nslookup 能解析但 ping 失敗？
- A簡: nslookup 直查 DNS；ping 先查本機快取，命中負面或過期項會失敗。
- A詳: 技術原理說明: 工具使用的解析路徑不同。關鍵流程: nslookup→DNS 伺服器；ping→本機快取→可能不進行外查。核心組件: OS 解析器、DNS。解法是清快取、等待再試或改用 IP 測通，以區分 DNS 與連通性問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, D-Q2

B-Q17: 為何在 Windows 上 NGINX 啟動失敗會立刻退出？
- A簡: command/CMD 啟動程序結束即容器退出，導致除錯不易。
- A詳: 技術原理說明: 容器以主程序存活，主程序終止容器即退出。關鍵流程: NGINX 啟動→解析失敗報錯→進程退出→容器停止。核心組件: 容器主進程、docker run/compose command。改用循環腳本包裹啟動，便於重試與調試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, D-Q3

B-Q18: 「等待 DNS 就緒」腳本的原理？
- A簡: 透過循環清快取並嘗試啟動，直至解析成功後常駐。
- A詳: 技術原理說明: 以迴圈執行 flushdns→啟動應用→若失敗 sleep 重試。關鍵流程: 負面快取清理→解析再嘗試→成功後常駐。核心組件: OS 命令（ipconfig、sleep）、應用二進位。能有效應對短暫的註冊延遲與快取污染。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, D-Q4

B-Q19: 為何 reload NGINX 能納入新副本？
- A簡: reload 會重讀設定與重新解析上游主機名，取得最新 A 紀錄。
- A詳: 技術原理說明: NGINX 接受信號或指令後，平滑重啟 worker，重新載入 conf 並解析 upstream 名稱。關鍵流程: 發送 reload→讀檔→解析 DNS→更新 upstream。核心組件: NGINX master/worker、DNS。能將 scale 後的多筆 IP 帶入輪詢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, D-Q5

B-Q20: docker inspect 取得容器 IP 的模板原理？
- A簡: 使用 Go 模板讀取 NetworkSettings.Networks.<net>.IPAddress 欄位。
- A詳: 技術原理說明: inspect 回傳 JSON，Go 模板可路徑存取欄位。關鍵流程: 生成 JSON→套用模板→輸出 IP。核心組件: docker CLI、Go template。典型用法為 docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" 容器名。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q1

B-Q21: 為何用 IP 能通而用名稱不通？
- A簡: 名稱解析被快取污染；直連 IP 不依賴 DNS 故可通。
- A詳: 技術原理說明: 連 IP 不經 DNS，純連通性測試。關鍵流程: ping/連線→IP 目標→回應；名稱→DNS→快取命中失敗。核心組件: OS DNS、應用。用以區分 DNS 與連線層問題的有效手段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q2, C-Q8

B-Q22: TTL 與快取對動態拓撲的影響？
- A簡: TTL 過長會使代理長期持有舊 IP，需要 reload 或降低快取。
- A詳: 技術原理說明: 解析結果依 TTL 緩存，拓撲變更需等 TTL 過期才更新。關鍵流程: 變更→舊紀錄仍生效→流量偏斜或失敗。核心組件: DNS 伺服器、OS/應用快取。建議在變更後做 reload，或設定較短有效期（視平台支持）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q7

B-Q23: NAT IPAM 設定中的 0.0.0.0/0 代表什麼？
- A簡: 代表由系統自動決策子網與閘道，實際分配值可於 inspect 觀察。
- A詳: 技術原理說明: 不指定子網時，HNS/IPAM 會分配可用私網段與閘道。關鍵流程: 建網→IPAM 自動挑選→套用至端點。核心組件: HNS、IPAM。若需可控的地址規劃，建議明確指定 subnet/gateway。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, A-Q20

B-Q24: 容器停止後名稱註冊如何處理？
- A簡: 停止容器後其端點會移除，DNS 名稱不再包含其 IP。
- A詳: 技術原理說明: HNS 解除端點註冊，Docker DNS 更新對應 A 紀錄。關鍵流程: 容器停止→端點刪除→DNS 更新。核心組件: HNS、Docker DNS。OS 快取仍可能保留舊 IP，需等待 TTL 或清快取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q22, D-Q5

B-Q25: compose 中 ports: - "80" 與 "80:80" 差異？
- A簡: "80" 只暴露容器埠不綁主機埠；"80:80" 纔對映主機固定埠。
- A詳: 技術原理說明: 不指定 host 部分時，由 Docker 分配隨機主機埠或僅暴露給連網容器使用。關鍵流程: 無映射→外界不可從主機固定埠連入。核心組件: docker-compose。文中 webapp 僅定義容器埠，外部需透過 proxy 服務訪問。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, C-Q5

B-Q26: 為何以腳本包裹 CMD/command 便於偵錯？
- A簡: 腳本可循環與打印錯誤，不致主程序退出導致容器關閉。
- A詳: 技術原理說明: 主程序退出容器即結束；腳本可捕捉失敗並重試。關鍵流程: 啟動→失敗→sleep→重試。核心組件: 批次/PowerShell、應用二進位。適用於等待 DNS 就緒或依賴順序敏感的情境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, D-Q4

B-Q27: 為何建立新 NAT 後容器立即恢復上網？
- A簡: 新 NAT 提供正確的路由/閘道/DNS，避開舊資源綁定問題。
- A詳: 技術原理說明: 舊 NAT 可能與 vSwitch 綁定或 IPAM 狀態損壞。關鍵流程: 新建→新閘道/DNS→新端點→路由恢復。核心組件: HNS、IPAM、vSwitch。這是快速恢復策略之一。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, C-Q9

B-Q28: 以容器 IP 測試可避開哪些問題？
- A簡: 可避開 DNS 與上游代理問題，專注驗證網路與服務存活。
- A詳: 技術原理說明: 直連 IP 減少變數。關鍵流程: 取得 IP→直連服務埠→判斷連通。核心組件: docker inspect、應用服務。用於分層定位：IP 可通→檢查 DNS/代理；IP 不通→檢查路由/NAT/防火牆。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q1, D-Q2

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何啟動 IIS 容器並映射到主機 8000 埠？
- A簡: 使用 docker run -d -p 8000:80 啟動 microsoft/iis 映像。
- A詳: 實作步驟: 1) docker run -d --name demo-iis -p 8000:80 microsoft/iis；2) docker ps 確認映射。程式碼:
```
docker run -d --name demo-iis -p 8000:80 microsoft/iis
```
注意: 本機不可用 localhost:8000 測試；需用遠端主機IP:8000，或在本機用容器IP:80。最佳實踐: 記錄容器名與端口映射以利除錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q2, C-Q3

C-Q2: 如何在本機與遠端測試容器服務是否可達？
- A簡: 遠端用主機IP:映射埠；本機用容器IP:原始埠進行測試。
- A詳: 實作步驟: 1) 遠端瀏覽 http://<host-ip>:8000；2) 本機 docker inspect 取容器 IP，瀏覽 http://<container-ip>:80。指令:
```
docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" demo-iis
```
注意: localhost:8000 在本機無效。最佳實踐: 優先遠端測映射埠，再本機測容器埠，分層定位。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, C-Q3

C-Q3: 如何快速取得容器的內部 IP？
- A簡: 使用 docker inspect 與 Go 模板擷取 nat 網路的 IPAddress。
- A詳: 實作步驟: 1) 確認容器名；2) 執行:
```
docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" <container>
```
關鍵片段: NetworkSettings.Networks.nat.IPAddress。注意: 若使用自訂網路，將 nat 改為該網路名。最佳實踐: 封裝成腳本以便常用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q20, A-Q20

C-Q4: 如何用 compose 建立 webapp、proxy 與 console？
- A簡: 撰寫 docker-compose.yml 定義三服務與網路，proxy 暴露 80 埠。
- A詳: 實作步驟: 1) 建 compose.yml；2) 設定 webapp、proxy、console；3) 指定 external nat。片段:
```
version: "2.1"
services:
  webapp:
    image: andrew0928/mvcdemo:1.0
    ports: ["80"]
  proxy:
    build: ./mvcproxy
    command: start-nginx.cmd
    ports: ["80:80"]
  console:
    image: microsoft/windowsservercore
    command: ping -t localhost
networks:
  default:
    external:
      name: nat
```
注意: webapp 未對映主機埠。最佳實踐: 加上 depends_on 與健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q16

C-Q5: 如何撰寫 nginx.conf 以服務名作為 upstream？
- A簡: 使用 upstream 指向 webapp 服務名，server 端口 80 反向代理。
- A詳: 步驟: 1) 建 conf；2) upstream 指 webapp；3) proxy_pass 指向 upstream。片段:
```
http {
  upstream production { server webapp; }
  server {
    listen 80;
    location / { proxy_pass http://production/; }
  }
}
```
注意: Windows 上 NGINX DNS 刷新需特別處理。最佳實踐: 規劃 reload 流程或使用 resolver 減少快取依賴。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q7

C-Q6: 如何以批次檔等待 DNS 就緒後啟動 NGINX？
- A簡: 編寫迴圈腳本 flushdns 後啟動 nginx，失敗則 sleep 重試。
- A詳: 步驟: 1) 建 start-nginx.cmd；2) 迴圈清快取並啟動。腳本:
```
cd /d c:\nginx
:loop
ipconfig /flushdns
nginx.exe
powershell /c sleep 1
goto loop
```
注意: 初期解析可能失敗，需重試。最佳實踐: 加入日誌輸出與最大重試次數以便監控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q4

C-Q7: 如何在 scale 後重載 NGINX 以納入新實例？
- A簡: 建 reload.cmd 清快取並執行 nginx -s reload，藉 docker exec 觸發。
- A詳: 步驟: 1) 建腳本:
```
cd /d c:\nginx
ipconfig /flushdns
nginx -s reload
```
2) 執行:
```
docker exec <proxy-container> reload.cmd
```
注意: 可能需多次重載才成功。最佳實踐: 自動化於 CI/CD 或 scale 完成後的 hooks。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, D-Q5

C-Q8: 如何用 docker exec 進入容器診斷 DNS？
- A簡: 進入 console 容器，使用 nslookup、ping、ipconfig /displaydns 檢查。
- A詳: 步驟: 1) 進入:
```
docker exec -it <console> cmd.exe
```
2) 檢查:
```
nslookup webapp
ping webapp
ipconfig /displaydns
```
注意: 若見 Name does not exist 須 flushdns。最佳實踐: 建置常用診斷腳本，縮短排錯時間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, D-Q2

C-Q9: 如何於 Windows 10 CU 後建立新 NAT 網路並使用？
- A簡: 使用 docker network create -d nat 新建，容器以 --network 指定連線。
- A詳: 步驟: 1) 建立:
```
docker network create -d nat andrew-nat
```
2) 驗證:
```
docker network inspect andrew-nat
```
3) 啟動容器指定:
```
docker run --rm -it --network andrew-nat microsoft/windowsservercore cmd.exe
```
注意: 舊 nat 若壞掉，改用新網路可恢復。最佳實踐: 規畫子網與命名。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q10, D-Q6

C-Q10: 如何在 compose 指定使用既有 nat 網路？
- A簡: 在 networks.default.external.name 設為 nat 或自建網路名。
- A詳: 步驟: 1) compose.yml 增加:
```
networks:
  default:
    external:
      name: nat
```
2) 若使用新建 NAT，將 name 改為其名稱。注意: external 網路需先存在。最佳實踐: 多專案共享一致網路策略，利於維運。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, A-Q16

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到主機 localhost:port 無法連容器怎麼辦？
- A簡: 這是 NAT loopback 限制；改用容器IP:原始埠或遠端用主機IP:映射埠。
- A詳: 症狀: 主機 localhost:8000 連不到，遠端卻可。原因: WinNAT 不支援 loopback。解法: 1) docker inspect 取容器 IP，連容器IP:容器埠；2) 於遠端主機IP:映射埠測試。預防: 測試腳本預設採遠端模式或內部 IP 測試，避免誤判。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q5, C-Q2

D-Q2: nslookup 有回應但 ping 服務名失敗？
- A簡: 本機 DNS 快取含負面/過期項，清除快取並重試或用 IP 測試。
- A詳: 症狀: nslookup webapp 有 IP，ping webapp 失敗。原因: Windows DNS 快取命中負面或舊紀錄。解法: 1) ipconfig /displaydns 檢視；2) ipconfig /flushdns 清除；3) 重試；4) 臨時用 IP 驗證。預防: 啟動時加入等待/重試，降低產生負面快取機率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q9, C-Q8

D-Q3: NGINX 報「host not found in upstream ‘webapp’」怎麼辦？
- A簡: 後端名未解析或快取污染；採等待腳本與重載設定解決。
- A詳: 症狀: NGINX 啟動或 reload 時找不到 upstream 名稱。原因: 服務未註冊完成或 DNS 快取仍舊。解法: 1) 啟動用循環腳本 flushdns 後再啟動；2) 變更拓撲後執行 reload 腳本；3) 驗證 nslookup 與顯示快取。預防: 以 healthcheck 或等待機制確保就緒。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, C-Q7, B-Q8

D-Q4: compose up 後服務時好時壞如何診斷？
- A簡: 多為 DNS 就緒與快取時序問題；加入等待重試與快取清理。
- A詳: 症狀: 前端偶爾報連不到後端。原因: depends_on 不等就緒、負面快取持續。解法: 1) 以 start 腳本循環啟動；2) 檢視/清理快取；3) 加健康檢查延遲上游啟動。預防: 將等待/重試標準化，避免人為干預。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q11, C-Q6

D-Q5: scale 後流量只打到第一個副本怎麼辦？
- A簡: 代理仍持舊解析或快取單一 IP；執行 reload 並清快取。
- A詳: 症狀: scale N 後只有單一實例吃到流量。原因: 上游代理或 OS 快取未更新多 A 紀錄。解法: 1) 對代理執行 reload；2) 清 OS 快取；3) 驗證 nslookup 多 IP。預防: 在 scale 流程中加入自動 reload 與健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q7

D-Q6: Windows 10 CU 後容器無法上網怎麼辦？
- A簡: 既有 nat 可能壞掉；建立新 NAT 網路並讓容器掛上即可恢復。
- A詳: 症狀: 容器 ping 8.8.8.8 不通。原因: 升級造成舊 NAT/HNS 組態損壞。解法: 1) docker network create -d nat 新建；2) 將容器以 --network 新網路啟動；3) 檢查網路 inspect。預防: 升級前匯出設定，避免手動刪改預設 nat。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q9, B-Q27

D-Q7: 無法建立 overlay 網路或 Swarm 叢集？
- A簡: 版本或平台尚未支援；需升級到支援 overlay 的 Windows/Docker。
- A詳: 症狀: 建立 overlay 失敗或 Swarm 無法跨主機互通。原因: Windows Server 2016 早期版本未完全支援。解法: 1) 確認 OS 版本與 Docker 版本；2) 在支援 overlay 的環境測試；3) 暫以 NAT 單機方案。預防: 上線前完成相容性驗證。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, B-Q6

D-Q8: 使用 --link 後 DNS 不生效怎麼辦？
- A簡: Windows 不支援 link；改用標準網路與 DNS 的服務名解析。
- A詳: 症狀: --link 後偶爾查得到名卻無法連通。原因: link 在 Windows 不受支援或不完整。解法: 1) 移除 --link；2) 改在同網路內以服務名互通；3) 以 compose 管理依賴與網路。預防: 不使用過時機制，統一走 DNS 服務探索。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q4

D-Q9: 端口映射仍被防火牆擋住？
- A簡: 舊版本未自動加規則；手動新增 inbound 允許或升級系統。
- A詳: 症狀: 遠端連主機映射埠被拒。原因: 14300 前未自動創建規則或策略阻擋。解法: 1) 檢查 Windows 防火牆；2) 手動加入允許規則；3) 升級到支援自動規則的版本。預防: 發佈前納入安全與網路例外審核。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, B-Q12

D-Q10: depends_on 存在但上游仍早於後端啟動失敗？
- A簡: depends_on 不等就緒；加入健康檢查或等待腳本解決。
- A詳: 症狀: 前端啟動即退出或連不到後端。原因: 只保證啟動序不保證健康。解法: 1) 在後端加入 healthcheck；2) 前端以腳本等待健康再啟；3) 若使用 NGINX，搭配循環啟動與重試。預防: 將健康檢查與等待納入標準模板。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q11, C-Q6

### 學習路徑索引
- 初學者：建議先學習 15 題
    - A-Q1: 什麼是 Windows Container Networking？
    - A-Q2: 什麼是 WinNAT？
    - A-Q3: 什麼是 NAT loopback？
    - A-Q4: 為何在主機上無法用 localhost:port 存取容器？
    - A-Q5: 容器端點在主機上可如何連線？
    - A-Q9: Windows 容器的 DNS 服務探索是什麼？
    - A-Q10: nslookup 與 ping 在 DNS 上有何差異？
    - A-Q16: 什麼是 docker-compose 的 external network？
    - A-Q17: 為何 Windows 會自動建立映射埠的防火牆規則？
    - B-Q5: 端口映射在 Windows 的轉送流程？
    - B-Q9: ipconfig /displaydns 與 /flushdns 的作用機制？
    - C-Q1: 如何啟動 IIS 容器並映射到主機 8000 埠？
    - C-Q2: 如何在本機與遠端測試容器服務是否可達？
    - C-Q3: 如何快速取得容器的內部 IP？
    - D-Q1: 遇到主機 localhost:port 無法連容器怎麼辦？

- 中級者：建議學習 20 題
    - A-Q11: 為什麼會出現 DNS 負面快取（Name does not exist）？
    - A-Q12: Docker Compose 的服務名稱解析有何特點？
    - A-Q13: 為何需要在 NGINX 處理 DNS 重新解析？
    - A-Q14: 為什麼需要「等待服務就緒」而不只依賴 depends_on？
    - A-Q15: NAT 與 overlay 在用途上的差異？
    - A-Q18: Windows 10 Creators Update 對容器網路的影響？
    - A-Q19: 為何建立新 NAT 網路可解決升級後連線問題？
    - B-Q1: WinNAT 如何運作？為何不支援 loopback？
    - B-Q2: Windows 容器的 DNS 解析流程是什麼？
    - B-Q3: docker-compose 的服務探索在 Windows 如何運作？
    - B-Q7: DNS 負面快取對應用的影響與處理？
    - B-Q8: NGINX 的 DNS 行為與 resolver 指令原理？
    - B-Q11: depends_on 與「服務就緒」的差別？
    - B-Q14: 為何 scale 後服務名解析會有多筆 A 紀錄？
    - B-Q19: 為何 reload NGINX 能納入新副本？
    - C-Q4: 如何用 compose 建立 webapp、proxy 與 console？
    - C-Q5: 如何撰寫 nginx.conf 以服務名作為 upstream？
    - C-Q6: 如何以批次檔等待 DNS 就緒後啟動 NGINX？
    - C-Q7: 如何在 scale 後重載 NGINX 以納入新實例？
    - D-Q5: scale 後流量只打到第一個副本怎麼辦？

- 高級者：建議關注 15 題
    - A-Q6: Windows 上的 overlay network 支援狀態？
    - A-Q7: Docker Swarm 與 overlay 的關係是什麼？
    - A-Q22: Windows 與 Linux 在容器網路成熟度差異？
    - B-Q6: Windows 上 overlay network 的設計概念？
    - B-Q10: docker network create -d nat 的行為？
    - B-Q22: TTL 與快取對動態拓撲的影響？
    - B-Q23: NAT IPAM 設定中的 0.0.0.0/0 代表什麼？
    - B-Q24: 容器停止後名稱註冊如何處理？
    - B-Q27: 為何建立新 NAT 後容器立即恢復上網？
    - B-Q28: 以容器 IP 測試可避開哪些問題？
    - C-Q9: 如何於 Windows 10 CU 後建立新 NAT 網路並使用？
    - C-Q10: 如何在 compose 指定使用既有 nat 網路？
    - D-Q6: Windows 10 CU 後容器無法上網怎麼辦？
    - D-Q7: 無法建立 overlay 網路或 Swarm 叢集？
    - D-Q10: depends_on 存在但上游仍早於後端啟動失敗？
{% endraw %}