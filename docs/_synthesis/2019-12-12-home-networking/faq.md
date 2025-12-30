---
layout: synthesis
title: "水電工日誌 #7. 事隔 12 年的家用網路架構大翻新"
synthesis_type: faq
source_post: /2019/12/12/home-networking/
redirect_from:
  - /2019/12/12/home-networking/faq/
---

# 水電工日誌 #7. 事隔 12 年的家用網路架構大翻新

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是家用網路架構翻新？
- A簡: 以新設備與新拓撲重整家庭網路，改善 WiFi 穩定、分段安全、供電佈線與效能瓶頸。
- A詳: 家用網路架構翻新指的是依據目前與可預見需求，重新選型與配置路由器、交換器、無線 AP、佈線與供電方式，並調整網段規劃與安全策略。常見目的包括：提升 WiFi 覆蓋與漫遊體驗、用 VLAN 隔離不同設備或用途、以 PoE 簡化部署、以 LACP 提升 NAS 連線效能、藉硬體 offloading 提升吞吐並降低 CPU 負載。翻新也會搭配管理平台（如 UniFi Controller）統一監控管理，讓後續擴充維護更容易。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, A-Q6, B-Q1

A-Q2: 為何要分離 Router 與 WiFi AP 的角色？
- A簡: 角色分離讓 Router 專注路由與安全，AP 專注無線覆蓋，便於最佳位置安裝與獨立升級。
- A詳: 將路由器（NAT、防火牆、VLAN、PPPoE 等）與無線 AP 職責拆開，有三大好處：1) 放置位置最佳化：Router 可留於機櫃內、散熱穩定；AP 可吸頂或高處，以最佳位置覆蓋全屋。2) 管理維護：兩者可獨立升級、汰換；AP 可多台擴充、統一管控。3) 效能與穩定性：避免一機多用導致的取捨，Router 專注有線與安全，AP 專注無線性能與漫遊。長期看，角色分離更有彈性與可維運性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, B-Q19

A-Q3: 什麼是 UniFi AP？核心價值是什麼？
- A簡: UniFi 是企業級 AP 系列，強調多點部署、統一管理、穩定連線與良好漫遊體驗。
- A詳: UniFi AP（如 AC Lite）是 Ubiquiti 企業級無線基地台，特色包括：集中式管理（UniFi Controller）、多 AP 單一 SSID 漫遊、吸頂式設計、PoE 供電、良好穩定性與可視化監控。對家用進階玩家，自建多台 AP 以單一 SSID 覆蓋各區，讓裝置自動連到最佳 AP，避免手動切換。搭配 Controller，可統一配置 SSID、射頻、VLAN 映射與韌體，形成「先規劃再擴充」的低痛點管理體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q17, B-Q5

A-Q4: 什麼是 UniFi Controller 與 Cloud Key 的差異？
- A簡: Controller 是管理軟體；Cloud Key 是專用硬體主機。也可用 Docker 自架，節省成本。
- A詳: UniFi Controller 是管理整套 UniFi 網通設備的軟體，可安裝於 PC、NAS 或 Docker。Cloud Key 則是官方販售的 Controller 專用硬體，開箱即用但需額外成本。自架 Controller 的好處是可用現有 NAS/伺服器與 Docker 環境，降低花費、易備份與升級；Cloud Key 的優點則在於簡便與穩定。兩者提供相同控制能力（採納設備、下發設定、統計監控），選擇取決於成本與維運偏好。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q12

A-Q5: 什麼是 PoE？為什麼需要它？
- A簡: PoE 透過網路線供電與傳輸資料，簡化佈線、利於吸頂與遠距設備安裝。
- A詳: PoE（Power over Ethernet）允許以一條網路線同時提供電力與資料連線，常見於無線 AP、IP 攝影機與 VoIP 電話。好處包括：佈線簡化（少一顆變壓器）、安裝位置彈性（吸頂、牆角）、集中供電（利於 UPS 保護），且利於整潔與維護。選擇設備時需留意 PoE 標準（如 802.3af/at）或是否為專有/被動 PoE，避免不相容造成供電失敗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q9

A-Q6: 什麼是 VLAN？核心觀念是什麼？
- A簡: VLAN 以邏輯方式分割二層網路，隔離廣播域與流量，提升安全與可管理性。
- A詳: VLAN（Virtual LAN）透過 802.1Q 標記在乙太框架上加上 VLAN ID，讓同一實體交換器可切出多個邏輯網段（廣播域）。它能在相同線路與交換設備上隔離不同用途（如家用、伺服器、IPTV），並透過 trunk 連結跨設備延伸，降低佈線與設備數量。配合路由器的三層介面（SVI）與 ACL/防火牆，可精細控管跨 VLAN 的通行策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2, B-Q4

A-Q7: 管理型交換器與非管理型交換器有何差異？
- A簡: 管理型可做 VLAN、QoS、LAG 等設定；非管理型僅單純轉發，功能單一。
- A詳: 非管理型交換器屬於即插即用，只有資料轉發與基本自動協商，適合單純網段。管理型（或智慧型）交換器可設定 VLAN、QoS、LAG/LACP、鏡像、風暴控制等，能隔離流量、整合頻寬、優化語音影音體驗。家用若需多網段隔離（NAS/家用/PPPoE 測試等）或 IPTV（如 MOD）就需要管理型交換器來標記/轉發 VLAN 與設定 trunk/Access。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q13, C-Q3

A-Q8: Trunk 與 Access 埠有何不同？
- A簡: Trunk 攜帶多個 VLAN（標記幀）；Access 僅屬單一 VLAN（去標記幀）。
- A詳: 在 VLAN 環境中，Trunk 埠會傳送帶有 802.1Q 標記的幀，可同時承載多個 VLAN，常用於交換器間或交換器到路由器/路由器內部交換模組。Access 埠則指定到單一 VLAN，接終端裝置（PC、NAS、一般 AP）。設計時通常將交換器間、至路由器的上行設為 Trunk，終端則 Access。若 AP 需對不同 SSID 對應不同 VLAN，連到交換器的一端通常也設成 Trunk。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q3, C-Q4

A-Q9: 什麼是 LACP（802.3ad）？何時需要？
- A簡: LACP 將多條實體連線聚合為單一邏輯鏈路，提升備援與總吞吐。
- A詳: LACP 是 Link Aggregation Control Protocol 的標準，能將兩條或多條乙太連線捆綁成一個邏輯通道（LAG），提供負載分擔與備援。對家用 NAS，很適合用兩埠聚合至支援 LACP 的交換器，讓多用戶同時存取時總吞吐提高（單連線仍受單埠速率限制）。需在 NAS 與交換器兩端設定為 802.3ad，並留意雜湊策略與 VLAN 整合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5

A-Q10: 什麼是 PPPoE？家中為何會用到？
- A簡: PPPoE 是以太網上的撥號協定，常用於寬頻上網認證與計費。
- A詳: PPPoE（Point-to-Point Protocol over Ethernet）在以太網上建立點對點連線，提供使用者名稱與密碼的認證與連線管理，廣泛用於電信寬頻。家中路由器通常在 WAN 介面上發起 PPPoE 與 ISP 連結，取得公共 IP。為測試或除錯，也可在 PC 直接建 PPPoE 撥號，繞過路由器核對 ISP 端狀態、帳密與線路品質。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q4

A-Q11: 什麼是硬體 Offloading？為何重要？
- A簡: 將路由/NAT 等資料平面工作交由 ASIC/SoC 加速，顯著提升吞吐。
- A詳: 硬體 offloading 是把路由器上的封包轉發、NAT 等操作由專用硬體（交換晶片、SoC）處理，降低 CPU 負載，讓 LAN↔LAN、LAN↔WAN 的吞吐接近介面極限。以 EdgeRouter X SFP 為例，啟用 offload 後常見可達近 1Gbps；但某些功能（如特定 QoS）可能需關閉 offload，吞吐下降。規劃時需在效能與進階功能間取捨。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q7

A-Q12: 什麼是 EdgeRouter X SFP？適合誰用？
- A簡: Ubiquiti 的小型路由器，含硬體交換模組、支援 VLAN、PPPoE 與 PoE，性價比高。
- A詳: EdgeRouter X SFP 屬 EdgeMAX 系列，採 SoC 內建 5 埠交換器硬體、支援 per-port VLAN、PPPoE、靜態與動態路由、基本防火牆與硬體 offload，且部分埠支援 PoE 輸出；並有一個 SFP 做光纖/模組擴充。它不受 UniFi Controller 管理（不同產品線），適合希望角色分離、玩 VLAN/PPPoE/LACP 並追求高性價比與低溫、低功耗的用戶。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, B-Q25

A-Q13: UniFi 多 AP 漫遊與 WiFi Mesh 有何不同？
- A簡: 多 AP 漫遊靠同 SSID 與控制策略；Mesh 強調無線回程。兩者目的不同。
- A詳: 多 AP 漫遊在同一有線骨幹下，以相同 SSID/安全設定與控制策略（可含 802.11r/k/v）讓客戶端在多台 AP 間平順切換。Mesh 網路則特別強調 AP 間以無線回程連接，適合無法拉線的場景。若可佈有線回程，建議用多 AP + 有線上行方式，效能與穩定性較高；Mesh 適合難以佈線的環境。UniFi 在兩者皆有方案，但本文聚焦多 AP 漫遊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q4

A-Q14: 2.4GHz 與 5GHz WiFi 有何差別？
- A簡: 2.4GHz 穿牆佳、速度較慢；5GHz 速度高、干擾少、穿牆較差。
- A詳: 2.4GHz 頻段通道少且擁擠，干擾多但覆蓋遠、穿牆較強；5GHz 通道多、帶寬與調變能力更高，整體速度佳、干擾少，但高頻穿牆衰減大。家庭部署建議雙頻並行：靠近 AP 優先用 5GHz 取高速，遠距或多牆面以 2.4GHz 保連線。配合多 AP 佈點與漫遊，可在家中維持穩定體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q22, C-Q4

A-Q15: 為什麼要預佈網路線與機櫃？
- A簡: 提升可靠性與擴充性，便於設備集中、散熱與維護，為未來升級預留空間。
- A詳: 預佈網路線（含足夠資訊孔位）與採用機櫃集中設備，能讓關鍵連線走有線、降低無線不確定性，並讓設備布置、線材整潔與散熱更佳；集中電源也方便 UPS 保護。多留幾對管線與端口，未來想增加 AP、攝影機或升級速率（如 10GbE）會更從容，避免二次施工成本與干擾。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, A-Q24

A-Q16: NAT 與 Routing 有何不同？
- A簡: Routing 在不同網段間轉送；NAT 轉換內外位址以共享公網與隱匿內網。
- A詳: Routing（路由）根據路由表將封包導向正確網段；NAT（位址轉換）將私網位址映射為公網位址，讓多裝置共享少量公網 IP，同時一定程度上隱匿內網結構。LAN↔LAN 僅需路由；LAN↔WAN 常伴隨 NAT。啟用硬體 offload 可讓這些操作在 ASIC/SoC 完成，提升效能。規劃防火牆時需兼顧二者，控制跨段與對外通行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10

A-Q17: 什麼是 SSID 與漫遊體驗？
- A簡: SSID 是無線網路名稱；多 AP 用同 SSID 讓裝置在訊號最佳點間切換。
- A詳: SSID（Service Set Identifier）是 WiFi 網路顯示名稱。多 AP 環境中，若使用相同 SSID/加密設定並搭配控制策略，客戶端可在 AP 間自動轉移（漫遊），維持連線品質。控制器可提供功率/頻道優化、最低 RSSI、快漫遊等功能，進一步改善切換延遲與體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q4

A-Q18: 為何 AP 建議用 PoE 吸頂安裝？
- A簡: 吸頂可最佳化覆蓋；PoE 簡化供電與佈線，並利於 UPS 與集中管理。
- A詳: 無線訊號向下扇形與視距敏感，吸頂能減少遮蔽物與人體阻擋，讓覆蓋更均勻。PoE 讓一條線就解決網路與供電，免變壓器、外觀整潔，長距離安裝也不受插座限制。把 PoE 供應端接到 UPS，可在停電時維持關鍵無線連通。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, C-Q9

A-Q19: 為何用 Docker 部署 Controller？
- A簡: 快速、可攜、易備份升級；與 NAS 整合降低成本，免長開 PC。
- A詳: Docker 容器化讓 Controller 的安裝與升級變得輕量、可重現，搭配卷（Volumes）存放設定與備份，不綁特定硬體。若已有 NAS/主機，直接容器化即可持續運轉，無需購買額外 Cloud Key。也便於監控與自動化維護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, B-Q12

A-Q20: EdgeRouter 與 UniFi 為何不能同一控制器管理？
- A簡: 屬不同產品線；EdgeOS 與 UniFi OS/Controller 架構不同，管理面分離。
- A詳: Ubiquiti 分兩大產品線：EdgeMAX（EdgeRouter/EdgeSwitch）走傳統網管與 CLI 為主；UniFi（AP/Switch/Gateway）走 Controller 集中管理架構。EdgeRouter 不受 UniFi Controller 管理，設定需在其 WebUI/CLI 進行；UniFi AP/Switch/USG 則由 Controller 統一採納與下發設定。可並存運作，但管理界面需分開。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q25, A-Q4

A-Q21: 為何要多網段與防火牆隔離？
- A簡: 降低風險與干擾，保護 NAS/伺服器，限制 IoT 與訪客僅取所需資源。
- A詳: 以 VLAN 區隔家用、伺服器、IoT/訪客等流量，再以路由器上的防火牆/ACL 管制跨段通行，可有效控管存取範圍，避免單點被攻陷後橫向移動；也能降低廣播風暴、提升穩定度。這對含 NAS、攝影機、智慧家電的現代家庭尤為重要。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q7

A-Q22: 停電會害設備壞掉嗎？UPS 就一定安全嗎？
- A簡: 停電不一定是主因；電容老化鼓起更常見。UPS 僅降風險，非萬靈丹。
- A詳: 停電、突波確實會縮短壽命，但若設備長期高溫運轉，電容老化鼓起常是致命原因。UPS 可緩和供電品質、容錯與有序關機，但無法改變高溫與元件老化。應重視散熱、選擇低溫設計設備、定期檢測與預防性汰換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q21, D-Q1

A-Q23: LAN↔LAN 與 LAN↔WAN 吞吐差異在哪？
- A簡: LAN↔LAN 多為交換/路由；LAN↔WAN 還含 NAT/PPPoE。Offload 決定實效。
- A詳: LAN↔LAN 走二層交換或三層路由，路由器與交換晶片的加速影響大；LAN↔WAN 一般需 NAT/PPPoE 認證，流程更多。若啟用硬體 offload，兩者皆可接近 1Gbps；受限於 ISP 速率時，外網測速受合約上限與網際品質左右。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q10

A-Q24: 何時應考慮升級 10GbE？
- A簡: 當 NAS/工作站間常傳大檔、多用戶同時存取且 SSD 阵列能跟上時。
- A詳: 若內外部瓶頸來自 1GbE，且應用包含 4K/8K 視訊剪輯、虛擬機大量遷移、多名使用者同時高頻寬讀寫，且儲存子系統（SSD RAID）可提供 1GB/s 以上吞吐，就值得導入 10GbE。也評估佈線（Cat6a/光纖）、交換器與網卡成本、發熱與功耗。可先升級骨幹與關鍵節點。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, B-Q16

A-Q25: 802.3af/at 與被動 PoE 有何差異？
- A簡: 802.3af/at 為握手協議標準；被動 PoE 無協商。混用恐損壞或無法供電。
- A詳: 802.3af（PoE）/at（PoE+）為標準化供電，會與受電端協調功率與安全；被動 PoE（如 24V）直接上電，無協商。選型與佈署須匹配標準，避免供電不足或供錯電壓。若路由器僅支援被動 PoE，而 AP 需 802.3af，須以 PoE 轉換器或支援標準 PoE 的交換器/注入器配合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q8


### Q&A 類別 B: 技術原理類

B-Q1: VLAN（802.1Q）如何運作？
- A簡: 以 VLAN ID 標記乙太幀，分割廣播域；交換器依標記轉發，路由器跨 VLAN 三層轉送。
- A詳: 802.1Q 在乙太框加入 4 bytes 標記，含 VLAN ID（12 bits）與優先權（PCP）。交換器 Trunk 埠保留標記轉發多 VLAN；Access 埠將終端所屬 VLAN 的幀去標記。跨交換器以 Trunk 延伸，跨 VLAN 需路由器提供 SVI（switch virtual interface）並以路由/ACL 控制。核心組件：VLAN 表、Trunk/Access 埠配置、SVI、ACL/防火牆。流程：標記→交換→（需要時）路由→策略管制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q2, B-Q4

B-Q2: 一台交換器上 VLAN 的基本配置流程是什麼？
- A簡: 建立 VLAN→設定 Trunk/Access→指定成員→必要時建立 SVI→測試與存檔。
- A詳: 流程：1) 建立 VLAN ID（如 10/20/30）。2) 規劃 Trunk（交換器上行/至路由器）與 Access（終端）埠。3) 設定各埠 VLAN 成員與 PVID（預設 VLAN）。4) 若交換器三層能力不足，於路由器建立對應 SVI。5) 驗證端口 VLAN 標記、終端互通性。核心組件：VLAN 表、埠成員表（Tagged/Untagged/Excluded）、PVID、Trunk 策略、測試工具（如 ping、VLAN 探測）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q13

B-Q3: EdgeRouter X SFP 上的 VLAN 與 SVI 如何運作？
- A簡: SoC 內建 switch0 進行二層 VLAN；switch0.vifX 作為三層介面路由與防火牆端點。
- A詳: ER-X SFP 以內建交換晶片組成 switch0，支援 per-port VLAN-aware 模式；在 switch0 上設定各 eth 埠的 PVID 與可通過的 VLAN VIDs。三層互通用 SVI（例如 switch0.10/switch0.20），各自配置閘道 IP、DHCP 與防火牆規則。流程：啟用 VLAN-aware→設定埠 VLAN→建立 SVI→設路由/DHCP→綁定防火牆。核心組件：switch0、SVI、DHCP server、防火牆/ACL、Offloading。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q10, B-Q25

B-Q4: 路由器與交換器之間的跨設備 VLAN 如何協作？
- A簡: 以 Trunk 承載多 VLAN 至路由器 SVI；交換器 Access 服務終端。
- A詳: 交換器至路由器上行設為 Trunk，允許多個 VLAN 標記幀通過；路由器對應建立每個 VLAN 的 SVI（閘道），提供三層轉送與策略控制。終端（PC/NAS/AP）經 Access（或 AP 用 Trunk）接入，幀在交換器去/加標記。核心：Trunk 對齊的 VLAN 列表、SVI 與 DHCP、對應防火牆規則。流程一致才能避免黑洞或誤通。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2, C-Q3

B-Q5: UniFi Controller 如何採納與管理 AP？
- A簡: AP 透過 L2/L3 發現被 Controller 採納，統一下發 SSID、射頻、VLAN 與韌體。
- A詳: 採納流程：AP 啟動後透過 L2 連線或設 inform URL 與 Controller 溝通；管理者在 Controller 內 Approve，AP 進入 Adopt→Provision→Connected 狀態。之後可統一配置 SSID、無線參數、VLAN 映射、排程、韌體更新。核心組件：Controller、AP inform 機制、站台設定、Provision 任務。流程化管理支撐多 AP 大規模部署與漫遊優化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q4

B-Q6: WiFi 快速漫遊（802.11r/k/v）的機制是什麼？
- A簡: r 簡化重新認證、k 提供鄰居地圖、v 協助導引，降低切換延遲。
- A詳: 802.11r 將部分認證前置，建立 PMK-R0/R1，切換時免完整四次握手；802.11k 讓 AP 向客戶提供鄰 AP 列表（RRM），客戶端可更快做掃描與決策；802.11v 提供網路引導（如 BSS Transition），協助客戶端切換到更佳 AP。核心：控制器統一配置、AP 間協調、終端支援度。效果依終端與控制策略而異。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, A-Q17

B-Q7: LACP 聚合的原理與限制是什麼？
- A簡: 透過 LACP 協調建立 LAG，依雜湊將連線分散於多鏈路，單連線仍受單埠速率限。
- A詳: 802.3ad 使用 LACPDU 協商聚合成一條邏輯鏈路，連線分配依雜湊（源/目的 MAC/IP/Port）至各實體埠，達到多流量併行與備援。限制：單 TCP 連線限於單埠速率、多用戶才見總吞吐提升；雙端設備須同為 802.3ad，且 VLAN 與 LAG 配置一致。適用多客戶端同時讀寫 NAS 的情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q5

B-Q8: PPPoE 撥接的工作流程為何？
- A簡: 發起 PADI→ISP 回應 PADO→建立會話 PADR/PADS→認證→取得 IP。
- A詳: 客戶端以 PADI 廣播尋找接入集中器（AC），AC 以 PADO 回應；客戶端發 PADR 請求建立，AC 回 PADS 確認，接著進行 PPP LCP 與認證（PAP/CHAP），最後建立 IPCP 分配 IP。核心：乙太傳輸上的 PPP 封裝、MTU 常為 1492、認證帳密、連線維持（Keepalive）。路由器或 PC 均可作為發起端。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, D-Q4

B-Q9: NAT 與狀態型防火牆如何協同工作？
- A簡: NAT 轉位址，狀態防火牆追蹤連線狀態，依策略允許或丟棄封包。
- A詳: 出向流量先套 NAT（如源 NAT），將內網來源映射公網；防火牆保持連線表（state table），對已建立/相關封包放行，對新連線依規則集判斷。入向需 DNAT/Port-Forward 開通服務且有相應策略才可進入。核心：NAT 規則順序、conntrack、策略方向（in/out/local）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q7

B-Q10: EdgeRouter 的硬體 Offload 背後機制是？
- A簡: 將轉發/NAT 交由交換 ASIC/SoC 快路徑處理，旁路 CPU，提升線速。
- A詳: EdgeOS 支援 HWNAT/Offload，建立資料平面快路徑規則，將符合條件的流量交由交換晶片直接處理；CPU 僅處理初次封包與控制面。某些功能（複雜 QoS、鏡像等）會迫使流量回 CPU（慢路徑）。核心設定包含開啟 offload 類型（例如 IPv4、pppoe）、檢視快路徑統計，並平衡與功能需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q8, D-Q7

B-Q11: PoE 供電與標準協商機制是什麼？
- A簡: 802.3af/at 以簽名電阻/類別協商功率；被動 PoE 無協商直接上電。
- A詳: 標準 PoE 供電端（PSE）先偵測 PD（受電端）簽名，再以類別協商所需功率，確保安全。PoE+（802.3at）提供更高功率，適配高耗能設備。相對地，被動 PoE 直接輸出固定電壓（常見 24V），需設備匹配。核心：PSE、PD、功率類別、線對分配（Mode A/B）。部署需確保標準一致，避免損壞或供電不足。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q25, D-Q8

B-Q12: Docker 化 UniFi Controller 的架構與資料持久化？
- A簡: 以容器執行應用，將資料目錄對映為 volume，映射必要埠進行管理與採納。
- A詳: Controller 容器需開放 3478/UDP（STUN）、8080/TCP（採納）、8443/TCP（GUI）等埠，並將 /unifi 資料目錄映射到宿主，以保留設定與備份。容器更新僅重啟新版映像，資料無縫延續。核心：容器映像、埠映射、卷（volume）、備份策略。與 NAS 整合可長期運作且易維護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, A-Q19

B-Q13: Netgear GS116E 的 VLAN 標記模型如何實作？
- A簡: 以 VLAN 成員表設定每埠狀態（Tagged/Untagged/Excluded）與 PVID，達成隔離。
- A詳: GS116E 屬智慧型交換器，透過 WebUI 建立 VLAN，為每埠指定在各 VLAN 的成員狀態：Tagged（Trunk 承載）、Untagged（Access 所屬）、Excluded（排除）。再設定每埠 PVID 決定未標記入向幀的歸屬。核心：VLAN 表、埠成員表、PVID、Trunk 對齊。雖無完整三層，但能完成大多數家用分段需求。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q2

B-Q14: Trunk 與 Access 的設計策略有哪些重點？
- A簡: 上行設 Trunk、終端設 Access；AP/伺服器視需求可用 Trunk 對應多 VLAN。
- A詳: 設計原則：交換器間/至路由器採 Trunk 承載多 VLAN；PC/NAS 預設 Access 落單一 VLAN；需要多 VLAN 的設備（AP 的多 SSID、虛擬化主機）採 Trunk 並由設備端標記。確保兩端 Trunk 的 VLAN 列表一致、避免 PVID 混淆，並用管理 VLAN 避免鎖死管理介面。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q4

B-Q15: 家用多網段的安全策略如何設計？
- A簡: 以「預設拒絕、按需放行」原則，限定跨段僅通行必要服務。
- A詳: 針對 IoT/訪客 VLAN 採限制政策，僅允許到網際網路與被明確允許的資源（如 DNS/DHCP/GW），禁止進入 NAS/伺服器 VLAN；管理 VLAN 僅供管理端使用。核心：分區分權、最小權限、防火牆規則順序、日誌與監控。這能有效降低橫向移動風險。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q7, D-Q3

B-Q16: SFP 埠在家用架構中的角色是？
- A簡: 提供光纖/模組化上行，利於遠距連線與未來升級（如 1G 光/媒體轉換）。
- A詳: SFP（Small Form-factor Pluggable）允許以光模組或銅模組延伸與上行，跨距遠、抗干擾佳。家用可用於機櫃間連線、長距離 AP/交換器上行，或作為介面彈性（光轉銅）。雖未必立即用到，但作為升級預留很實用。
- 難度: 初級
- 學習階段: 進階
- 關聯概念: A-Q24, C-Q9

B-Q17: 為何啟用 QoS 會影響硬體 Offload？
- A簡: 複雜隊列與分類需 CPU 介入，迫使流量離開快路徑，吞吐下降。
- A詳: 硬體 offload 走固定轉發規則；進階 QoS（多層分類、整形）需要軟體處理與動態決策，無法完全在 ASIC 上完成，導致回到 CPU 慢路徑。設計時應權衡：若 WAN 速率較低（如百兆），可接受關閉 offload 換取精細 QoS；若追求千兆線速，應簡化 QoS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q7

B-Q18: 如何定位家用網路的效能瓶頸？
- A簡: 分層測試：LAN↔LAN（NAS 檔案）、LAN↔WAN（測速）、AP↔有線（WiFi），觀察哪層卡住。
- A詳: 先測 NAS↔PC 大檔傳輸（排除 ISP 上限），再測 PC↔網際測速（對照合約），再測 WiFi↔有線（AP/頻段/距離）。觀察 CPU/溫度、offload 狀態、線材品質、連線類型（全雙工）、NAT/QoS。逐層縮小範圍，找出瓶頸環節（磁碟、網卡、交換器、路由器、ISP）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q7, C-Q8

B-Q19: Bridge、Switch 與 Router 的差異？
- A簡: Bridge/Switch 處理二層（MAC），Router 處理三層（IP）；功能與性能定位不同。
- A詳: Switch 以 MAC 學習與交換表進行二層轉發；Bridge 為二層邏輯橋接概念；Router 依路由表於三層導流並施作 NAT/ACL。高階路由器可內建硬體交換模組處理二層（如 ER-X 的 switch0）。理解層次有助正確設計 VLAN、SVI 與跨段政策。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q3

B-Q20: 交換器埠數選擇與佈線規劃原則？
- A簡: 依固定與預留需求選擇；核心位置集中，減少交叉線與不必要跳接。
- A詳: 先盤點固定用量（NAS、PC、AP、攝影機）與預留（擴充/客座），在合理空間內選擇合適埠數。可選擇桌上型放入機櫃節省空間。若需多網段，建議管理型以 VLAN 聚合，減少交換器數量與跨線，並保留上行 Trunk 擴展彈性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q9

B-Q21: 熱設計如何影響設備壽命？
- A簡: 高溫加速電容老化與焊點疲勞；低溫設計與通風可顯著延壽。
- A詳: 長期高溫會使電容內部蒸發與鼓起，焊點熱循環疲勞導致故障。選購低功耗、低溫設備（如 SoC 交換方案）、提供良好通風與避開密閉空間，搭配 UPS 穩定電力，能提升可靠度。定期除塵、觀察異常噪音與鼓起跡象，必要時預防性更換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, D-Q1

B-Q22: AP 位置與天線取向如何影響訊號？
- A簡: 視距、遮蔽物與高度影響大；吸頂靠近活動區，多 AP 分區覆蓋更佳。
- A詳: 無線信號與牆面、金屬與人體交互會產生衰減與多路徑；AP 放置越居中越高，覆蓋越均勻。指向性天線需針對使用區域指向；雙頻需避開相互干擾。多 AP 用 Controller 做功率與頻道規劃提升整體體驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q4

B-Q23: 家用 NAS 吞吐的主要瓶頸有哪些？
- A簡: 磁碟/RAID、網卡/聚合、交換器性能、並發用戶數與協定開銷。
- A詳: 若磁碟陣列吞吐不足（HDD 隨機/併發弱），即使網路升級也難以拉高；單連線受單埠限制，LACP 在多連線併發下才發揮。交換器需支援 LACP 與足夠背板；SMB/NFS 與 CPU 加密也會影響速率。整體調校需端到端考量。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, C-Q5

B-Q24: IPTV/MOD 為何常需 VLAN？
- A簡: 業者用專用 VLAN 提供多播與服務隔離；家用需交換器支援對應 VLAN。
- A詳: 電信業者在同一對線路上承載網際、VoIP、IPTV，多以 VLAN 區分，且 IPTV 常用多播。家中交換器需將機上盒的埠設為對應 VLAN Access，上行 Trunk 放行該 VLAN 至路由器或直接旁路。錯誤配置會造成無法收視或影響其他網段。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q3

B-Q25: EdgeRouter 的 WebUI 與 CLI 如何分工？
- A簡: WebUI 便於基礎設定與監控；CLI 提供完整細節與自動化腳本化能力。
- A詳: WebUI 友善進行基本 WAN/LAN、PPPoE、DHCP、防火牆與流量監看；進階設定（細緻 VLAN、策略路由、複雜 ACL、Offload 調校）多仰賴 CLI。CLI 可批次、可版本控管，利於複製環境。建議養成「WebUI 打底、CLI 精修」的習慣。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q8


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 NAS 上用 Docker 部署 UniFi Controller？
- A簡: 使用官方常用映像，映射必需埠與資料卷，啟動後以瀏覽器登入設定。
- A詳: 實作步驟：1) 在 NAS 啟用 Docker。2) 建立資料夾存放 /unifi。3) 執行容器（例）：docker run -d --name unifi -p 3478:3478/udp -p 8080:8080 -p 8443:8443 -p 8880:8880 -p 8843:8843 -v /nas/unifi:/unifi jacobalberty/unifi:latest。4) 以 https://nas-ip:8443 進入初始精靈。注意：開放埠、防火牆允許、定期備份 /unifi、升級前先快照。最佳實踐：固定容器版本、使用反向代理與憑證管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, A-Q4

C-Q2: 如何在 EdgeRouter X SFP 建立三個 VLAN 並跨交換器連通？
- A簡: 啟用 switch0 VLAN-aware，設定埠 PVID/VIDs，建立 switch0.10/20/30，配置 DHCP 與防火牆。
- A詳: 步驟：1) 啟用 VLAN-aware：set interfaces switch switch0 switch-port vlan-aware enable。2) 設 trunk 埠（對外交換器）：set interfaces switch switch0 switch-port interface eth0 vlan vids 10,20,30。3) 設 Access 埠（終端）：set interfaces switch switch0 switch-port interface eth1 vlan pvid 10（依需求）。4) 建立 SVI：set interfaces switch switch0 vif 10 address 192.168.10.1/24（20/30 類推）。5) 啟用 DHCP（每 VLAN 一組）。6) 設防火牆策略。注意：兩端 Trunk VLAN 列表一致；存檔與備份設定。最佳實踐：命名標註、避免管理 VLAN 誤鎖。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, B-Q25

C-Q3: 如何在 Netgear GS116E 設定 Trunk 與 Access 埠？
- A簡: WebUI 建立 VLAN，設定各埠在 VLAN 的成員（Tagged/Untagged），設 PVID 於 Access 埠。
- A詳: 步驟：1) 登入 WebUI→VLAN→802.1Q→建立 VLAN ID 10/20/30。2) 在「VLAN Membership」設定 port1 為 Tagged（Trunk，允許 10/20/30），port2-6 為 VLAN10 Untagged（Server LAN），port7-15 為 VLAN20 Untagged（Home LAN），port16 為 VLAN30 Untagged（如 Modem 段）。3) 於「PVID」設定對應 Access 埠的 PVID。注意：Trunk 埠不得同時設 Untagged 多 VLAN；保存設定避免重啟遺失。最佳實踐：標籤貼紙與文件化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, B-Q2

C-Q4: 如何讓 UniFi AP 的多 SSID 對應不同 VLAN？
- A簡: Controller 建立多 SSID，於每 SSID 設 VLAN ID；AP 上行連到 Trunk 埠。
- A詳: 步驟：1) 在 Controller→Settings→WiFi 建立如「Home」（VLAN 20）、「Guest」（VLAN 30）。2) 於每個 SSID 的 Network/VLAN 欄位填入對應 VLAN。3) 確保 AP 連到交換器的埠為 Trunk，允許 20/30 等 VLAN。4) 更新/採納 AP。注意：管理流量（AP 管理 VLAN）與使用者流量可分開；確保路由器 SVI 和 DHCP 已就緒。最佳實踐：對訪客啟用隔離與限速。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q5, B-Q14

C-Q5: 如何在 NAS 與交換器上設定 LACP？
- A簡: NAS 建立 802.3ad 聚合，交換器建立對應 LAG，兩端 VLAN 設定一致。
- A詳: 步驟：1) NAS（Synology）控制台→網路→網路介面→建立→鏈路聚合→選 802.3ad→勾選兩埠→完成。2) 交換器（GS116E）→LAG→啟用 LAG1→加入對應兩埠→將 LAG1 設為 VLAN 的 Tagged/Untagged 成員。3) 驗證 LACPUP。注意：不可混用靜態聚合與 LACP；兩端 VLAN 一致；同速率線材。最佳實踐：用高品質網線、合理命名、監看 NAS 負載。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q23

C-Q6: 如何在 Windows/macOS 建立 PPPoE 測試連線？
- A簡: 新增「寬頻（PPPoE）」連線，輸入 ISP 帳密，連接至 Modem 所在網段的埠。
- A詳: Windows：設定→網路與網際網路→撥號→設定新連線→連至網際→寬頻（PPPoE）→輸入帳密→連線。macOS：系統設定→網路→＋→介面選 PPPoE→以乙太網作服務→輸入帳密→連線。注意：PC 需接在 Modem 直通的 VLAN/埠上；可能需調整防火牆允許 PPPoE 封包；MTU 1492。最佳實踐：測完關閉連線避免與路由器衝突。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q4

C-Q7: 如何在 EdgeRouter 設定跨 VLAN 防火牆隔離？
- A簡: 建立每 VLAN 的防火牆規則集，採預設拒絕，按需放行 DNS/DHCP/特定服務。
- A詳: 步驟：1) 建立規則集如 IOT_IN：預設 drop；允許至 GW、DNS、DHCP。2) 將規則集套用在對應 VLAN 的入向（in）介面（如 switch0.30）。3) 對管理或伺服器 VLAN 規則較嚴，禁止 IOT→Server。注意：規則順序從上到下，早匹配先動作；log 量適中。最佳實踐：最小權限、白名單、建立描述與備份。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, B-Q9

C-Q8: 如何啟用 EdgeRouter 的硬體 Offload 並驗證？
- A簡: 在 CLI 啟用 IPv4/NAT/PPPoE offload，重啟資料平面，觀察統計與吞吐。
- A詳: 步驟（示例）：configure→set system offload hwnat enable→set system offload ipsec enable（如需）→commit；視版本啟用 pppoe offload。以 show ubnt offload 或 show hardware offload 檢視狀態；用 iperf/檔案傳輸驗證吞吐。注意：某些 QoS/鏡像會停用 offload；升級韌體後複核設定。最佳實踐：記錄前後性能、保留變更紀錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q7

C-Q9: 如何規劃關鍵線路直連路由器與 PoE 佈線？
- A簡: 將 AP/NAS/上行等關鍵連線直掛 Router/核心交換器，PoE 集中供電接 UPS。
- A詳: 實務：1) 將 AP 以 PoE 直連路由器 PoE 埠或 PoE 交換器，減少中間點。2) 將 NAS/伺服器接近核心交換器或直連 Router 以降低延遲。3) 佈線走線槽、留餘量、標籤管理。4) PoE 供應集中於 UPS 迴路，重要設備可持續供電。注意：避免多層菊鍊、保持良好彎曲半徑、壓接品質。最佳實踐：文件化拓撲與編號。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q15

C-Q10: 如何從舊設備平滑移轉到新架構並預留回復方案？
- A簡: 平行架設、新網段測試、逐步切換、維持回退計畫與設定備份。
- A詳: 步驟：1) 先在離線環境完成新設備設定（VLAN/DHCP/防火牆/AP）。2) 改接少數測試端驗證功能。3) 排程切換窗口，逐段轉接到新交換器/路由器。4) 觀察與調整；保留舊設備與線路可快速回退。注意：記錄 IP 規劃、避免與舊 DHCP 衝突、通知家人影響時段。最佳實踐：完整備份設定、拍照記錄佈線。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q3, B-Q18


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 停電後路由器不開機怎麼辦？（電容鼓起）
- A簡: 先檢查電容與供電，可能因長期高溫導致電容老化。維修或更換設備並改善散熱。
- A詳: 症狀：按電源無反應、或間歇性啟動。可能原因：電容鼓起/漏液、供應器故障、主板焊點疲勞。處置：1) 目測電容、異味、鼓包。2) 換電源測試。3) 送修更換電容或汰換新品。預防：選低溫設備、留通風空間、定期除塵，關鍵設備接 UPS 但勿過度依賴。長期建議：監看溫度與運轉年限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q22, B-Q21

D-Q2: UniFi AP 無法被 Controller 採納怎麼辦？
- A簡: 確認網路可達、重設 AP、設置 inform URL，開放採納必要埠，重試採納。
- A詳: 症狀：AP 顯示 Pending/Disconnected。可能原因：L2/L3 隔離、STUN/採納埠被擋、AP 綁定其他 Controller。步驟：1) AP 恢復原廠（Reset）。2) 確認 Controller 埠 8080/TCP、3478/UDP 開放。3) SSH 進 AP 設置 set-inform http://controller:8080/inform。4) 在 Controller Approve→Provision。預防：固定 Controller IP/DNS、記錄站台資訊、避免多 DHCP 池干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q1

D-Q3: 設了 VLAN 之後某些網段互通或不通，如何診斷？
- A簡: 檢查 Trunk/Access 與 PVID、兩端 VLAN 清單、路由/SVI 與防火牆規則。
- A詳: 症狀：終端拿不到 IP、跨段不通、管理頁消失。原因：成員表錯、PVID 錯、Trunk VLAN 清單不一致、SVI 未啟用、ACL 阻擋。步驟：1) 驗證該埠 VLAN 成員與 PVID。2) 檢查路由器 SVI/DHCP。3) 對照防火牆規則。4) 以帶 VLAN 的測試筆電驗證 Trunk。預防：文件化、命名規範、保留管理 VLAN 的直連後門。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q14, C-Q3

D-Q4: PPPoE 撥接不上網如何處理？
- A簡: 檢查帳密、MTU、連接埠 VLAN/拓撲，嘗試 PC 直撥以排除路由器設定問題。
- A詳: 症狀：認證失敗、連上無法上網。原因：帳密錯、PPPoE 未到 AC、MTU/封包被擋、WAN 埠 VLAN 錯。步驟：1) PC 直連 Modem 建立 PPPoE 驗證帳密。2) 檢查 MTU（1492）。3) 檢視路由器撥接介面來源埠與 VLAN。4) 測 ISP 線路。預防：備存帳密、保留測試路徑、文件化 WAN VLAN。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q6

D-Q5: LACP 無法啟動或速度不增，怎麼辦？
- A簡: 確認雙端皆為 802.3ad、成員埠一致、VLAN 設定相符，多用戶情境才能見效。
- A詳: 症狀：LAG Down、單埠速率。原因：一端靜態聚合、一端 LACP、埠速率不一致、VLAN 不符。步驟：1) 雙端皆設 802.3ad。2) 成員埠速率/雙工一致。3) VLAN 在 LAG 介面上一致。4) 以多連線/多用戶測試。預防：使用同廠線材、清晰命名、監看 LACP 狀態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5

D-Q6: WiFi 不能自動切換到訊號更好的 AP？
- A簡: 確保 SSID/加密一致、開啟漫遊優化，適度調整功率與最低 RSSI，減少黏著。
- A詳: 症狀：裝置黏在遠端 AP。原因：SSID 差異、終端黏著性高、AP 功率過強。步驟：1) 同站台同 SSID/加密。2) 開啟 11k/v/r（視裝置支援）。3) 降低 AP 功率、設定最小 RSSI。4) 重新連線。預防：控制器統一管理，定期勘測與調整。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q4

D-Q7: NAT/路由效能不佳怎麼診斷？
- A簡: 檢查硬體 offload、QoS/鏡像、CPU 占用、流量路徑，視需要調整功能取捨。
- A詳: 症狀：LAN↔WAN 吞吐低、CPU 飆高。原因：offload 關閉、QoS 啟用、鏡像或封包檢查。步驟：1) 查 offload 狀態並啟用。2) 暫停複雜 QoS 驗證差異。3) 排除鏡像/IDS。4) 測速定位瓶頸。預防：記錄變更、根據速率選擇合適 QoS 策略、定期韌體更新。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q8

D-Q8: PoE 供電不起來或 AP 不亮，如何處理？
- A簡: 檢查 PoE 標準/電壓相容、線材品質與長度、PSE 功率是否足夠。
- A詳: 症狀：AP 不上電或不穩。原因：PSE/PD 標準不匹配（802.3af/at vs 被動）、供電瓦數不足、線材/接頭不良、過長。步驟：1) 確認 AP 與供電端標準一致。2) 測試短線與替換線材。3) 檢視 PSE 是否多設備過載。4) 必要時用 PoE 注入器。預防：選相容設備、標示清楚、定期檢測。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q25, B-Q11

D-Q9: EdgeRouter 溫度過高如何改善？
- A簡: 提供良好通風、避免堆疊積熱、降低不必要功能負載，必要時外接散熱。
- A詳: 症狀：外殼燙手、當機。原因：密閉機櫃、堆疊設備、環境溫度高、CPU 長期滿載。步驟：1) 改善通風、加風扇。2) 清理灰塵。3) 啟用 offload 降 CPU。4) 檢查韌體。預防：選低溫設備、合理佈置、溫度監測。長期看，硬體選型與散熱設計最關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q21, A-Q12

D-Q10: 設錯 VLAN 導致無法登入 GS116E 管理頁怎麼辦？
- A簡: 嘗試從管理 VLAN 的 Access 埠接入；不行則按復位鍵恢復出廠並重設。
- A詳: 症狀：管理頁無法存取。原因：管理 VLAN 被換至無法到達的 VLAN、PVID 變更、Trunk 列表錯。步驟：1) 查手冊預設管理 VLAN（常為 VLAN1），從該 VLAN Access 埠連入。2) 以備用筆電設定相同 VLAN 標記測試 Trunk。3) 仍無解→硬體復位、重新規劃再設定。預防：先建立管理 VLAN 後門、逐步變更、文件化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q3


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是家用網路架構翻新？
    - A-Q2: 為何要分離 Router 與 WiFi AP 的角色？
    - A-Q3: 什麼是 UniFi AP？核心價值是什麼？
    - A-Q4: 什麼是 UniFi Controller 與 Cloud Key 的差異？
    - A-Q5: 什麼是 PoE？為什麼需要它？
    - A-Q6: 什麼是 VLAN？核心觀念是什麼？
    - A-Q7: 管理型交換器與非管理型交換器有何差異？
    - A-Q8: Trunk 與 Access 埠有何不同？
    - A-Q10: 什麼是 PPPoE？家中為何會用到？
    - A-Q14: 2.4GHz 與 5GHz WiFi 有何差別？
    - A-Q15: 為什麼要預佈網路線與機櫃？
    - A-Q17: 什麼是 SSID 與漫遊體驗？
    - D-Q2: UniFi AP 無法被 Controller 採納怎麼辦？
    - D-Q4: PPPoE 撥接不上網如何處理？
    - D-Q6: WiFi 不能自動切換到訊號更好的 AP？

- 中級者：建議學習哪 20 題
    - B-Q1: VLAN（802.1Q）如何運作？
    - B-Q2: 一台交換器上 VLAN 的基本配置流程是什麼？
    - B-Q3: EdgeRouter X SFP 上的 VLAN 與 SVI 如何運作？
    - B-Q4: 路由器與交換器之間的跨設備 VLAN 如何協作？
    - B-Q5: UniFi Controller 如何採納與管理 AP？
    - B-Q7: LACP 聚合的原理與限制是什麼？
    - B-Q8: PPPoE 撥接的工作流程為何？
    - B-Q9: NAT 與狀態型防火牆如何協同工作？
    - B-Q10: EdgeRouter 的硬體 Offload 背後機制是？
    - B-Q11: PoE 供電與標準協商機制是什麼？
    - B-Q13: Netgear GS116E 的 VLAN 標記模型如何實作？
    - B-Q14: Trunk 與 Access 的設計策略有哪些重點？
    - B-Q18: 如何定位家用網路的效能瓶頸？
    - C-Q1: 如何在 NAS 上用 Docker 部署 UniFi Controller？
    - C-Q2: 如何在 EdgeRouter X SFP 建立三個 VLAN 並跨交換器連通？
    - C-Q3: 如何在 Netgear GS116E 設定 Trunk 與 Access 埠？
    - C-Q4: 如何讓 UniFi AP 的多 SSID 對應不同 VLAN？
    - C-Q5: 如何在 NAS 與交換器上設定 LACP？
    - C-Q7: 如何在 EdgeRouter 設定跨 VLAN 防火牆隔離？
    - C-Q8: 如何啟用 EdgeRouter 的硬體 Offload 並驗證？

- 高級者：建議關注哪 15 題
    - A-Q11: 什麼是硬體 Offloading？為何重要？
    - A-Q21: 為何要多網段與防火牆隔離？
    - A-Q24: 何時應考慮升級 10GbE？
    - A-Q25: 802.3af/at 與被動 PoE 有何差異？
    - B-Q6: WiFi 快速漫遊（802.11r/k/v）的機制是什麼？
    - B-Q15: 家用多網段的安全策略如何設計？
    - B-Q16: SFP 埠在家用架構中的角色是？
    - B-Q17: 為何啟用 QoS 會影響硬體 Offload？
    - B-Q23: 家用 NAS 吞吐的主要瓶頸有哪些？
    - B-Q24: IPTV/MOD 為何常需 VLAN？
    - B-Q25: EdgeRouter 的 WebUI 與 CLI 如何分工？
    - C-Q9: 如何規劃關鍵線路直連路由器與 PoE 佈線？
    - C-Q10: 如何從舊設備平滑移轉到新架構並預留回復方案？
    - D-Q3: 設了 VLAN 之後某些網段互通或不通，如何診斷？
    - D-Q7: NAT/路由效能不佳怎麼診斷？