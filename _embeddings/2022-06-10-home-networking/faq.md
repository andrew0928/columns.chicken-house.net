# 水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 UniFi OS Console？
- A簡: UniFi 生態系的管控中樞，整合路由、防火牆、交換器、AP、監控等服務。
- A詳: UniFi OS Console 是 Ubiquiti 提供的整合管理平台，常見機型如 UDM-PRO。它內建 Network 應用（VLAN、DPI、Threat Management、VPN、Policy Routing）、Protect（錄影）、以及集中式裝置控制。優勢在於單一介面整合多角色，降低跨設備設定門檻，適合中小型商用與進階家用，快速建設穩定、可視化的網路環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q11, B-Q5

A-Q2: 什麼是 UDM-PRO？扮演哪些角色？
- A簡: UniFi Dream Machine Pro，一體機路由器與控制器，兼顧錄影與網安。
- A詳: UDM-PRO 是 UniFi OS Console 的旗艦一體機，整合路由器、防火牆、DPI/Threat Management、VPN、雙WAN、內建控制器與 Protect 錄影（換裝硬碟即可）。具 10G SFP+ 與 1G 埠，適合整合家用/小辦公室的路由、交換、Wi-Fi、監控。強項在易用與整合，弱項是極致效能與高階細部網管彈性不及專業單機。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q8, B-Q5

A-Q3: 什麼是 VLAN？為何在家用網路需要？
- A簡: 虛擬區域網路，邏輯分段隔離流量，提高安全與品質管理。
- A詳: VLAN（Virtual LAN）在同一實體交換器上切分多個邏輯網段，使不同用途設備隔離。優點是控管廣播域、強化安全、防止不必要互訪，並可針對不同網段施作防火牆、QoS。家用可分家庭上網、NAS/LAB、訪客/IOT、骨幹等，保護關鍵資源、提升穩定與可視化管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q7, C-Q1

A-Q4: 家用網路為何要做「網段隔離」？
- A簡: 隔離降低風險，保障家人上網品質，保護 NAS/LAB 與內網資源。
- A詳: 家中設備多元且品質參差（IOT、訪客、孩童裝置），一旦同網段互通，易造成資安風險與廣播干擾。藉 VLAN 切分、路由與防火牆規則，能讓家人上網品質有保障、將 LAB 與 NAS 隔離又可控存取，並能針對不可信裝置限制內網資源，只放行上網與必要服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2, C-Q1

A-Q5: Guest Network 與一般 VLAN 有何差異？
- A簡: Guest Network 是預設強化隔離訪客流量的 VLAN 模板與入口。
- A詳: UniFi 的 Guest Network 以 VLAN 為基礎，搭配預設訪客隔離、防火牆與可選擇的入口頁（Portal）。一般 VLAN 需手動配置隔離與策略；Guest Network 則提供開箱即用的訪客/IOT 分離方案，預設阻擋內網，只允許上網，適合接待臨時裝置或不可信設備。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2

A-Q6: 什麼是 PoE？家用有何好處？
- A簡: 乙太供電，讓網路線同時傳資料與電力，簡化佈線。
- A詳: PoE（Power over Ethernet）透過網路線傳電，常見規格有 PoE/PoE+/PoE++。家用好處包括：AP、IP Cam、電話、IOT 省去電源插座布建；集中供電到 UPS 增加穩定度；異地裝設容易與美觀。選購 PoE 交換器應注意總供電瓦數與每埠額定功率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q13(延伸), A-Q22

A-Q7: SFP+ 與 RJ45（10GBase-T）差異？
- A簡: SFP+ 模組化、低延遲低功耗，RJ45 普及但發熱大距離受限。
- A詳: 10G 連線常見兩派：SFP+ 與 RJ45。SFP+ 可用 DAC（銅纜）或光纖模組，優點是功耗低、溫度低、延遲佳、距離可延展；RJ45（10GBase‑T）則相容既有銅線佈線，普及但發熱高，長距離與穩定性較受限。文中以 SFP+ DAC 串 UDM-PRO 與 USW、NAS，兼顧成本與可靠性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, C-Q10

A-Q8: CAT5E、CAT6A、DAC/光纖的取捨？
- A簡: CAT5E 可跑 2.5G；10G 建議 CAT6A 或 SFP+ DAC/光纖銜接。
- A詳: 老屋佈線多為 CAT5E，實測可支援 2.5G。若要全面 10G，建議新拉 CAT6A 或改走 SFP+，以 DAC（短距）或光纖（長距）避免 RJ45 10G 發熱與距離瓶頸。文中做法：骨幹採 SFP+ DAC 上 10G，終端先升級 2.5G，兼顧成本與實際需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q10

A-Q9: 什麼是 L3 Switch？與 L2 有何不同？
- A簡: L3 具路由能力，能在交換器層面執行跨 VLAN 轉送。
- A詳: L2 只做同網段交換；L3 內建路由功能，能在交換器內部完成不同 VLAN 的互通。優勢是就近處理東西向流量，減少路由器負載與瓶頸。文中使用 USW-Enterprise 24 PoE 啟用 L3，將跨 VLAN 檔案流量留在交換器，繞開 UDM-PRO 的 Threat Management 瓶頸。
- 難度: 中級
- 學習階段: 核心
- 還聯概念: B-Q7, D-Q1, C-Q10

A-Q10: 家用為何需要 L3 Switch？
- A簡: 跨 VLAN 流量大（NAS/備份）時，L3 減輕路由與DPI負載。
- A詳: 當內網大量東西向傳輸（如 PC↔NAS、備份、影像流）且跨 VLAN 時，經路由器（含威脅偵測）易成瓶頸，導致 2.5G/10G 跑不滿。改由 L3 交換器負責內部路由，可保留路由器資源給北向上網流量，速度更穩定，資安與效能兼顧。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q8, D-Q1

A-Q11: 什麼是 Traffic Rules（家長監護）？
- A簡: 以應用/類別、裝置、時段條件，允許或封鎖流量。
- A詳: UDM-PRO 新增 Traffic Rules（1.12.22 後），結合 DPI 的應用識別（L7），可用 App/群組/Domain/IP/區域作條件，再選目標裝置或群組，搭配排程，最後設 Action（Allow/Block）。家長可輕鬆限制孩童於特定時段使用社群、影音或遊戲，不用手動查端口與 IP。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q8, D-Q4

A-Q12: 什麼是 Traffic Routes？
- A簡: 以規則指定來源到目標的上網路徑（WAN1/WAN2）。
- A詳: Traffic Routes 是策略式路由（Policy Routing），可依來源裝置/網段、目標類型（Domain、IP、全部上網）指定走特定 WAN。文中把 NAS 對外統一走 WAN2（固定 PPPoE IP），其他裝置預設走 WAN1（浮動 IP），亦可針對單一網站改走特定 WAN。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q7, D-Q7

A-Q13: 為何要同時兩組 PPPoE（雙 WAN）？
- A簡: 分流用途不同；固定 IP 發布服務，浮動 IP 一般上網。
- A詳: HINET 支援多組 PPPoE 併行。將 WAN1 配浮動 IP 供家人上網，WAN2 配 PPPoE 固定 IP 對外發布自架服務（NAS 下載、Port Forward、DDNS），可分開管理、減少影響，且針對特定來源/目的以 Traffic Routes 指定走向，彈性大幅提升。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q5, C-Q7

A-Q14: 什麼是 Teleport VPN？和 L2TP 差在哪？
- A簡: Teleport 基於 WireGuard，零設定體驗；L2TP 較舊需手動配置。
- A詳: Teleport 是 UniFi 將 AMPLIFI 的零設定 VPN 帶入 UDM-PRO 的方案，底層採 WireGuard，透過 WiFiman App 點連結自動建立設定，適合行動裝置遠端返家。L2TP/IPsec 歷史悠久、相容性廣（含 Windows），但需手動設定伺服器參數，體驗較繁瑣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q6, D-Q3

A-Q15: WireGuard 與 OpenVPN 有何差異？
- A簡: WireGuard 輕量快速、易設定；OpenVPN 生態成熟、相容廣。
- A詳: WireGuard 使用較新加密與精簡代碼，效能與延遲表現佳，設定簡單；OpenVPN 陣容龐大、插件與平台支援完整，企業環境常見。家用若追求快速簡單可選 WireGuard（Teleport），若需跨平台含 Windows 傳統支持，L2TP/OpenVPN 仍有價值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q9

A-Q16: 什麼是 AdGuard Home？能做什麼？
- A簡: 本地 DNS 解析器，支援廣告/惡意阻擋與自訂重寫。
- A詳: AdGuard Home 是可自架的 DNS 服務，可攔截廣告與惡意域名，並提供 DNS Rewrite 將特定域名指向內網服務，其他查詢則轉發上游 DNS。搭配 NAS Docker 易部署；再結合 Reverse Proxy 與 SSL，內外一致的域名體驗與安全瀏覽就緒。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q3, C-Q4

A-Q17: 什麼是 DNS Rewrite？何時需要？
- A簡: 將域名覆寫至本地 IP，內網可直連服務避免繞外。
- A詳: DNS Rewrite 讓內網查詢指定域名時回覆私有 IP（而非公網 IP），用於本地直接連 NAS 上的 Web 服務，避免外出再回家（Hairpin NAT）造成繞路、憑證與延遲問題。常見在自架 Bitwarden、相簿、管理介面等，配合反向代理與憑證更完善。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, B-Q10, A-Q18

A-Q18: 什麼是反向代理（Reverse Proxy）？
- A簡: 以單一對外位址/埠轉發到多個內部服務主機。
- A詳: 反向代理接收外部請求，依域名/路徑轉到對應內部服務。Synology 內建 Application Portal 可輕鬆設定，讓多個服務共用 443 埠，集中憑證與安全控管。好處是簡化 NAT/Port 轉發、減少暴露面，並配合 DNS Rewrite 在內外網提供一致網址。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, A-Q17

A-Q19: Let’s Encrypt 憑證在家用有何價值？
- A簡: 提供免費可信 SSL 憑證，自動更新，避免瀏覽器警告。
- A詳: Let’s Encrypt 透過 ACME 協定自動簽發/續期憑證，Synology 可內建申請並綁定反向代理。對家用意義在於：內外訪問 HTTPS 不再跳「不安全」，對外開放服務（如 Bitwarden）必備，降低 MITM 風險並提升使用體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, A-Q18

A-Q20: NAS 自架服務與自組 PC 伺服器差異？
- A簡: NAS 優勢在儲存可靠（RAID/備份）、長時運行、易管理。
- A詳: 自組 PC 彈性與效能高，但資料可靠性與維護成本高。NAS 以儲存為核心，提供 RAID、備份、低耗能、靜音與友善介面，適合長時運行與家庭/個人服務（Docker、VM）。文中將 Bitwarden、AdGuard、開發工具放 NAS，關鍵資料更安心。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q5, A-Q21

A-Q21: 何謂自架 Bitwarden？適合誰？
- A簡: 在自家 NAS/Docker 架密碼保管庫，資料留在自己手裡。
- A詳: Bitwarden 提供開源伺服器映像，自架可讓密碼資料庫受自家 RAID 與備份保護，降低外部服務風險。對在意隱私與可控性的用戶適合；前提是穩定運行與備援機制完善。搭配 DNS/SSL/反代，能獲得與雲版相近的使用體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q5

A-Q22: 什麼是 UniFi Protect？與 NAS 錄影差異？
- A簡: UniFi 的整合錄影平台，攝影機生態完整，體驗流暢。
- A詳: UniFi Protect 內建於 UDM-PRO，插入硬碟即可錄影，介面與 App 使用體驗佳。但需使用 UniFi 相機，備份彈性較少。NAS（如 Synology Surveillance Station）支援多品牌攝影機與進階功能，授權與設定較繁。可用 RTSP 將 Protect 影像備份到 NAS，兼顧體驗與冗餘。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, C-Q13(延伸), D-Q8

A-Q23: Threat Management 是什麼？為何會降速？
- A簡: L7 IDS/IPS 分析流量偵測威脅，吃 CPU，易成瓶頸。
- A詳: UDM-PRO 的 Threat Management 進行深度封包檢測（DPI），以特徵與行為辨識威脅。跨 VLAN 大流量（如 PC↔NAS）若經由路由器處理，CPU 高負載導致吞吐下降。解法是將內部跨 VLAN 流量改由 L3 Switch 轉送，讓 Threat Management 專注在上網流量。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q1, A-Q10

A-Q24: 什麼是 iperf3？在家用網路怎麼用？
- A簡: 網路效能測試工具，量測端到端吞吐與瓶頸。
- A詳: iperf3 通過 TCP/UDP 產生可控流量，測試客戶端到伺服器的帶寬。文中以 NAS（Docker）為 Server、PC 為 Client 驗證 2.5G/10G 與跨 VLAN 效能。測試可配合不同路徑（直連、經路由、經 L3）排查瓶頸，搭配 CPU 使用率觀察更準確。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, C-Q9, D-Q1


### Q&A 類別 B: 技術原理類

B-Q1: UniFi 如何跨設備部署 VLAN？
- A簡: 以 Network 定義網段，透過 Port Profile 標註 Trunk/Access。
- A詳: UniFi Controller 先建立 Networks（VLAN ID、子網、DHCP），再以 Port Profile 標示交換器埠與 AP SSID 的 VLAN（Trunk/Tagged 與 Access/Untagged）。Router 介面對應子網並下發 DHCP。此整合讓多台交換器/AP 自動套用一致設定。核心組件：Controller、USW、AP、UDM-PRO。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q1

B-Q2: UniFi Guest Network 的隔離機制如何運作？
- A簡: 建立訪客 VLAN，預設阻擋內網，只放行上網。
- A詳: Guest Network 建立獨立 VLAN 與 SSID，套用預設防火牆策略（阻擋到 LAN/管理子網），可選擇 Portal 認證。Controller 會在路由器生成對應規則，並在交換器/AP 套用 VLAN 標記。關鍵步驟：建 VLAN、啟用 Guest、指定 SSID、檢查防火牆。核心組件：UDM-PRO、USW、UAP。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, C-Q2

B-Q3: Traffic Rules 背後的應用辨識（DPI）如何實現？
- A簡: 透過 L7 深度封包檢測與已知特徵，分類應用流量。
- A詳: UDM-PRO 進行 Deep Packet Inspection，解析封包標頭與內容行為，對照內建應用特徵庫（社群、影音、遊戲等）。Traffic Rules 將分類結果暴露為條件，供使用者用裝置/排程組合下達 Allow/Block。組件：DPI 引擎、分類資料庫、策略引擎、時間表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q4

B-Q4: Traffic Routes 的策略路由如何生效？
- A簡: 根據來源與目的規則，選擇指定 WAN 進行轉送。
- A詳: Controller 將 Traffic Routes 轉為路由與政策表，由 UDM-PRO 以 PBR（Policy Based Routing）針對匹配封包覆寫下一跳（WAN1/WAN2）。支援目的類型（Domain/IP/Any），來源（裝置/網段）。競合以規則優先序處理。組件：匹配器、路由策略表、雙 WAN 介面。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q7, D-Q2

B-Q5: UDM-PRO 1.12.22 的 Port Remapping 原理？
- A簡: 允許將特定實體埠重新指派為 LAN/WAN1/WAN2。
- A詳: 新版韌體開放 #8/#9（RJ45）與 #10/#11（SFP+）的角色映射，系統層將對應邏輯介面到實體埠，讓雙 WAN 與 10G LAN 更靈活。可不再強制以 SFP+ 做 WAN2，節省轉接成本並優化佈線。組件：介面映射層、雙 PPPoE、Controller 設定同步。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q7

B-Q6: PPPoE 雙連線如何取得兩個公共 IP？
- A簡: 以兩條獨立 PPPoE 會話向 ISP 認證，各自分配 IP。
- A詳: PPPoE 透過以太網封裝 PPP，建立撥接會話。HINET 允許多會話，UDM-PRO 分別在 WAN1/WAN2 發起認證，ISP 伺服器各自下發 IP。兩連線並行運作，互不影響，配合策略路由可分流應用。組件：PPPoE 客戶端、ISP BRAS、認證伺服器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q7

B-Q7: L3 Switch 的跨 VLAN 路由流程？
- A簡: 在交換器本地建立 SVI，封包就地轉送至目標 VLAN。
- A詳: L3 Switch 為每個 VLAN 建立介面（SVI）並啟用路由。跨網段封包進入交換器後，由硬體路由表就地決策，查 ARP/NDP 並轉發至目標 VLAN 埠。此法避免繞經路由器，提升東西向吞吐。組件：SVI、路由表、ARP/NDP、ACL（必要時）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q10, D-Q1

B-Q8: Threat Management 封包處理流程？
- A簡: 解析封包→特徵比對→風險判定→阻擋/放行與記錄。
- A詳: 流程含 DPI 解析（L7）、比對簽章與行為規則、評分與政策應用。啟用後所有經路由器的流量都需檢查，遇大量內網傳輸時 CPU 飆高，造成吞吐下降。最佳實務：將內部跨 VLAN 交給 L3 Switch，路由器專注北向流量與安全分析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, D-Q1

B-Q9: Teleport（WireGuard）如何穿越 NAT？
- A簡: 以 UDP 封包與現代穿越技術，快速建立隧道。
- A詳: WireGuard 使用 UDP 與固定公鑰，輕量握手快速；Teleport 由 Controller 產生邀請連結，WiFiman App 導入設定並嘗試 NAT 穿越，必要時輔助 STUN/中繼。相較 L2TP 需多參數與相容性考量，Teleport 省去使用者設定，適合行動端。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q15, C-Q6

B-Q10: AdGuard Home 的 DNS 工作流程？
- A簡: 收到查詢→黑/白名單判斷→重寫或轉發上游→回應。
- A詳: AdGuard 為遞迴解析器，先檢查攔截清單與 Rewrite 表；命中則阻擋或回覆本地 IP；未命中則轉發上游 DNS，再將結果快取。家用將路由器或 DHCP 指向 AdGuard，搭配 Rewrite 與反代，統一管理內外服務名稱。核心：Filter、Rewrite、Upstream、Cache。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, A-Q17, C-Q3

B-Q11: Synology 反向代理與憑證運作機制？
- A簡: 依 Host/Path 路由到容器或服務，ACME 自動簽發憑證。
- A詳: Application Portal 以 Hostname/Path 規則轉發到內部服務（container/主機埠）。憑證管理與 ACME 整合，自動完成域名驗證（HTTP-01）與續期。以單一 443 對外，減少 NAT 條目，集中 TLS 終止與安全管控。組件：Nginx 反代、ACME 客戶端、憑證儲存。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, A-Q19, C-Q5

B-Q12: NAS 上 Docker 的儲存與備份關鍵？
- A簡: Volume 掛載保存資料，搭配 RAID/備份確保可靠。
- A詳: 容器層與資料層分離，將應用資料（DB/設定）掛載至 NAS 共用資料夾，受 RAID 與備份保護。映像可重建、資料需妥善備援。對個人核心服務（Bitwarden、AdGuard）尤為重要。組件：Container Runtime、Volumes、RAID、備份排程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, A-Q21, C-Q3

B-Q13: iperf3 測試方法與數據解讀？
- A簡: 以 Server/Client 模式產生流量，觀察吞吐與穩定性。
- A詳: 在 NAS 起 iperf3 -s，PC 端 iperf3 -c <server>。可調整時間(-t)、並行(-P)、方向（-R）測試雙向。跨 VLAN 與直連比較可定位瓶頸；搭配路由器 CPU 監控判讀是否為 DPI/路由造成。注意 CDN/IP 多目標時測域名可能不準，建議精準指定 IP 測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, D-Q1, C-Q9

B-Q14: PoE 電力預算如何計算？
- A簡: 總供電瓦數≥所有受電埠預估消耗，預留裕度。
- A詳: 交換器標示 PoE Budget（總瓦數）與每埠上限（如 PoE+ 30W）。統計相機、AP、IOT 需求，總和不可超過 Budget，建議預留 20–30%。長線纜與品質亦影響供電效率。UniFi 控制器可監看每埠用電，避免過載引發不穩。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q8

B-Q15: UniFi Protect 錄影與 NAS 備份串接原理？
- A簡: Protect 儲存在 UDM-PRO；經 RTSP 餵給 NAS 同步錄影。
- A詳: Protect 以本機硬碟儲存錄影檔；若需備份，可開啟每支相機的 RTSP 串流，讓 NAS Surveillance Station 當作「自訂攝影機」再錄一份。此組合保留 Protect 使用體驗與行動 App 優勢，又以 NAS 建立冗餘。組件：Protect、RTSP、NAS NVR。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, D-Q8

B-Q16: SFP+ DAC 連結的優點與設計考量？
- A簡: 低延遲、低溫、成本佳，適合機櫃短距連接。
- A詳: DAC（直連銅纜）用於機櫃內短距 10G 連結（一般 0.5–3m）。相較 RJ45 10G 發熱高，DAC 更穩定省電；相較光纖成本低、免收光模組。注意：線長限制、設備兼容（建議原廠或相容模組）、彎折半徑。適合 UDM-PRO⇄USW、USW⇄NAS 骨幹。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q8, C-Q10


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 UniFi 建置家庭 VLAN（TRUNK/MODEM/NAS/HOME/GUEST）？
- A簡: 於 Controller 建 Networks 與 VLAN，設定 Port Profile 與 SSID 對應。
- A詳: 具體步驟：
  1) Networks 建立各網段與 VLAN ID（如 0/10/100/200/201，子網與 DHCP）。
  2) USW 以 Port Profile 設定 Trunk/Access；對 NAS/Router/AP/Camera 埠指派正確 VLAN。
  3) UAP 建 SSID 對應 VLAN（HOME/GUEST）。
  4) 驗證：DHCP 分配、跨段路由、防火牆規則。注意 Trunk 攜帶標籤、管理網段保護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q1, B-Q2

C-Q2: 如何打造訪客/IOT 網路並排程停用？
- A簡: 建立 Guest VLAN/SSID，使用 Scheduler 或 Traffic Rules 控制時間。
- A詳: 步驟：
  1) 新增 Guest Network（VLAN、隔離）。
  2) 建 SSID 綁 Guest VLAN。
  3) 若僅限 Wi-Fi，可用 SSID Scheduler 設定時段啟停。
  4) 需跨有線與 Wi-Fi，改用 Traffic Rules 以裝置群組+排程「封鎖網路」。
  注意 Portal 選項、內網阻擋策略、孩童裝置最好固定指派群組管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q11, B-Q2

C-Q3: 如何在 Synology 以 Docker 部署 AdGuard Home 並成為全網 DNS？
- A簡: 以容器啟動 AdGuard，路由 DHCP 指向其 IP 提供解析。
- A詳: 步驟：
  1) 建資料夾掛載 /config。
  2) 以映像 adguard/adguardhome 啟動容器，映射 53/3000 埠。
  3) 首登 Web 設定上游 DNS、過濾清單。
  4) 在 UDM-PRO 或 DHCP 將 DNS 指向 NAS:53。
  注意：避免與路由器本機 DNS 衝突、開放管理介面僅限內網、備份設定檔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q10

C-Q4: 如何設定 DNS Rewrite 讓內外一致訪問 NAS 服務？
- A簡: 在 AdGuard 建域名覆寫至內網 IP，配合反向代理。
- A詳: 步驟：
  1) 於 AdGuard → DNS Rewrites 新增例如 vault.example.com → 192.168.100.x。
  2) Synology 反向代理設定對應主機名到容器埠。
  3) 憑證管理將該域名 SSL 綁定到反向代理。
  注意：確保內外 DNS 設定一致；若外部解析到公網，內網應覆寫避免繞外。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, A-Q18, C-Q5

C-Q5: 如何在 Synology 設定反向代理與 Let’s Encrypt？
- A簡: 建轉發規則，申請憑證並綁定，統一以 443 對外。
- A詳: 步驟：
  1) 控制台→應用程式入口→反向代理：以 Hostname 建立規則，指到容器內部位址與埠。
  2) 安全性→憑證：新增→從 Let’s Encrypt 申請，填入域名與驗證方式。
  3) 將憑證綁定至該反代條目。
  注意：防火牆/NAT 開放 80/443；域名需指向公網 IP 才能自動驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, A-Q19

C-Q6: 如何啟用 Teleport VPN 並由手機連回家？
- A簡: 在 Controller 產生邀請，手機 WiFiman 開啟連結自動配置。
- A詳: 步驟：
  1) UDM-PRO → Teleport 開啟功能，產生連結 QR/URL。
  2) 將連結給手機，安裝 WiFiman 後點擊接受。
  3) App 內可一鍵連線/斷線。
  注意：目前無原生 Windows 客戶端；PC 可暫用 L2TP。建議搭配用戶權限與審核。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q9, D-Q3

C-Q7: 如何實作雙 PPPoE 並用 Traffic Routes 讓 NAS 走 WAN2？
- A簡: 以 Port Remapping 建 WAN1/2，建立路由規則指派 NAS→WAN2。
- A詳: 步驟：
  1) Internet 設定新增兩個 PPPoE 連線。
  2) Port Remapping：#8/#9 指為 WAN1/2，#10/#11 指為 LAN（10G）。
  3) 將兩線接小烏龜；完成撥接。
  4) Traffic Routes 新增規則：Source=NAs 裝置/網段，Category=Internet，Interface=WAN2。
  注意：Port Forward 可選 WAN2；DDNS 選擇對應 WAN。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q5, B-Q6

C-Q8: 如何用 Traffic Rules 做家長監護（時段封鎖社群）？
- A簡: 建規則選社群分類，套用孩童裝置與假日/平日時段。
- A詳: 步驟：
  1) 建裝置群組（Kids）。
  2) Traffic Rules：Category=Social Networks、Target=Kids、Schedule=自訂（如 22:00–24:00 平日）、Action=Block。
  3) 可依暑假/學期建立不同排程模板。
  注意：若 App 走 DoH/DoT 仍可因 L7 分類生效；必要時再加上 Domain/IP 規則。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q3, D-Q4

C-Q9: 如何在 NAS 佈署 iperf3 並測 2.5G/10G？
- A簡: 以容器啟用 iperf3 -s，PC 端 -c 連線測吞吐。
- A詳: 步驟：
  1) 以 networkstatic/iperf3 啟動容器並暴露 5201。
  2) PC 執行 iperf3 -c nas-ip -t 30，觀察穩定值；測雙向加 -R。
  3) 依路徑變更位置（跨 VLAN/同 VLAN），比較差異。
  注意：測試時觀察 UDM-PRO CPU；如因 Threat Management 抑制，考慮 L3 Switch。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, B-Q13, D-Q1

C-Q10: 如何用 SFP+ DAC 串 UDM-PRO、USW 與 NAS？
- A簡: 選擇相容 DAC 線長，SFP+ 直連，避免 10G RJ45 發熱。
- A詳: 步驟：
  1) 機櫃內量測距離，購買 0.5–2m DAC。
  2) UDM-PRO #10/#11 設為 LAN；USW 上 10G SFP+ 上行接 UDM-PRO，另一個接 NAS 10G。
  3) 驗證 SFP+ Link Up 與速率。
  注意：線彎折半徑、相容模組、溫度；終端 PC 若僅 2.5G，瓶頸會在端點速率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q16

C-Q11: 如何把 RJ11 電話佈線轉為 RJ45 網路使用？
- A簡: 若原先用 CAT5E 佈線，改換 RJ45 面板與配線盤即可。
- A詳: 步驟：
  1) 檢查牆內線材是否為 CAT5E。
  2) 牆面換 RJ45 模組，機櫃端改上配線盤，兩端重壓 T568A/B。
  3) 仍需市話時，利用 RJ45 兼容 RJ11（勿插到交換器），以配線跳線切換用途。
  注意：標示清楚，避免把電話插到網路交換器埠。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, D-Q10

C-Q12: 如何在 Synology 以 Docker 佈署 FileZilla（Web VNC）？
- A簡: 使用 jlesage/filezilla 映像，瀏覽器內嵌 VNC 操作 GUI。
- A詳: 步驟：
  1) 拉取 jlesage/filezilla 映像，映射 5800（Web VNC）。
  2) 掛載資料夾作為下載/上傳空間。
  3) 瀏覽器連 http://nas:5800 即可使用 GUI 版 FileZilla。
  注意：此為遠端桌面體驗，非原生 Web App；權限與速度取決 NAS 與網路。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12

C-Q13: 如何把 UniFi Protect 影像同步備份到 NAS？
- A簡: 啟用相機 RTSP，NAS Surveillance Station 當自訂攝影機。
- A詳: 步驟：
  1) Protect 介面取得每台相機的 RTSP URL。
  2) NAS 開啟 Surveillance Station，新增攝影機→自訂→填入 RTSP。
  3) 設定錄影保存與保留策略。
  注意：RTSP 為影像串流，非原檔案複製；網路負載需評估；雙錄影可提升冗餘。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, B-Q15, D-Q8

C-Q14: 如何在 NAS 上用 code-server 寫部落格並即時預覽？
- A簡: 以 code-server 容器提供 Web VSCode，搭配 GH Pages/Jekyll 容器預覽。
- A詳: 步驟：
  1) 佈署 linuxserver/code-server，掛載內容資料夾。
  2) 佈署 Jekyll/GitHub Pages 容器，監看資料夾變更即時建置。
  3) 利用反向代理與憑證提供 HTTPS 存取。
  注意：剪貼簿圖像自動貼上外掛相容性需測試；建議 VPN 後使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q12


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 跨 VLAN 只有約 1.4Gbps，效能不佳怎麼辦？
- A簡: 可能被 Threat Management 影響；改 L3 Switch 路由或關閉測試。
- A詳: 症狀：PC↔NAS 跨 VLAN 速度卡 1.x G，UDM-PRO CPU 70–85%。原因：跨段流量經路由器，DPI/IDS 造成 CPU 瓶頸。解法：啟用 L3 Switch（SVI）就近路由；或暫時關閉 Threat Management 驗證。預防：東西向流量走交換器，北向上網交給路由器與安全功能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, B-Q7, B-Q8, C-Q10

D-Q2: Traffic Routes 指定網域無效（如 myip.com）怎麼辦？
- A簡: 可能因 CDN/IP 變動或 DoH；改用固定 IP/CIDR 指派。
- A詳: 症狀：針對特定域名改走 WAN2 無效。原因：多 IP、Cloudflare、DNS 快取差異或端站名不同。解法：以 nslookup 解析出 IP 後在 Traffic Routes 用 IP/網段規則；或鎖定更上層域名段。預防：優先用 IP/範圍規則，並驗證實際出口（myip 測試）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q7

D-Q3: Teleport 沒有 Windows 客戶端，如何替代？
- A簡: 暫用 L2TP/IPsec 建置 PC 端 VPN；行動端用 Teleport。
- A詳: 症狀：電腦端無原生 Teleport。解法：同時啟用 L2TP/IPsec，於 Windows 建置傳統 VPN；行動裝置以 Teleport 獲得快速體驗。預防：關鍵存取仍建 SSH/VPN 金鑰控管；留意 L2TP 穿越防火牆與 NAT 設定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q9, C-Q6

D-Q4: 啟用 Traffic Rules 後某些網站或 App 被誤擋怎麼辦？
- A簡: 檢查 Category 命中，針對裝置或網站加 Allow 白名單。
- A詳: 症狀：社群/影音被意外封鎖。原因：L7 分類命中或排程生效。解法：檢視命中的 Rule 與時間，對特定 App/Domain/裝置加 Allow 覆寫；或調整時段。預防：先小規模測試，分批上線，定期檢視命中報表調整白名單。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q3, C-Q8

D-Q5: 部署 AdGuard 後部分網站解析異常？
- A簡: 檢查黑名單與 Rewrite，確認上游 DNS 與迴圈設定。
- A詳: 症狀：網站載入慢或無法解析。原因：過濾清單過嚴、Rewrite 錯誤、上游 DNS 無回應、路由器也在攔截。解法：關閉可疑過濾或加白名單，檢查 Rewrite 指向正確，改用穩定上游（如 1.1.1.1），確保僅一處做攔截。預防：逐步導入、保留備援 DNS。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q10, C-Q3

D-Q6: Guest 網路需要例外存取內網設備該如何設定？
- A簡: 於防火牆增加特定例外（來源=Guest→目的=特定 IP/埠）。
- A詳: 症狀：訪客無法存取投影/印表機。解法：新增防火牆規則允許 Guest VLAN 到特定內網資源（IP/Port），放在阻擋規則之前；或建立受控反向代理讓訪客以域名訪問。預防：嚴格最小權限，僅針對必要服務開孔並記錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q2

D-Q7: 雙 PPPoE 只有一條能撥成功怎麼辦？
- A簡: 檢查 ISP 同時會話限制、Port Remapping 與接線。
- A詳: 症狀：第二條 PPPoE 認證失敗或反覆斷線。原因：ISP 限制多會話數、接線錯誤、埠角色未指派、VLAN/撥號參數不正確。解法：確認方案允許多連線；檢視 Port Remapping 與物理接到小烏龜；逐步替換線材測試。預防：文件化撥接設定與實體配線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q5, B-Q6

D-Q8: PoE 相機不亮或不穩定如何排查？
- A簡: 先核對 PoE Budget/埠功率，再檢查線材與距離。
- A詳: 症狀：相機間歇離線或啟動失敗。原因：PoE 總功率不足、單埠供電不足、線材品質/長度、接頭壓接不良。解法：查看控制器每埠用電，臨時關閉非必要 PoE；更換短線測試；固件更新。預防：預留 20–30% 供電裕度，採用合格線材。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, A-Q22, C-Q13

D-Q9: Wi‑Fi 相機串流不穩該怎麼改善？
- A簡: 檢查 AP 覆蓋與干擾，優先 5GHz，必要時改用 PoE 有線。
- A詳: 症狀：影像卡頓斷線。原因：訊號弱、干擾多、上傳不足、相機與 AP 距離/遮蔽。解法：調整 AP 位置與功率、鎖定 5GHz、避免高干擾信道；若可行，改用 PoE 有線供電與傳輸。預防：部署前用 Wi‑Fi 測速與熱點圖勘查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q22

D-Q10: RJ11 插到 RJ45 面板真的可行嗎？需注意什麼？
- A簡: RJ11 可物理插入 RJ45，但勿連到交換器；透過配線盤切換用途。
- A詳: 說明：RJ11 插頭可插入 RJ45 面板，但僅能接到電話系統或分線器，切勿接交換器埠。若牆內是 CAT5E，兩端以 RJ45 重新終端，機櫃端用配線盤跳接，於需要時改為話務或網路用途。預防：清楚標示，避免誤插造成設備損壞。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q11, A-Q8


### 學習路徑索引

- 初學者：建議先學習 15 題
  - A-Q1: 什麼是 UniFi OS Console？
  - A-Q2: 什麼是 UDM-PRO？扮演哪些角色？
  - A-Q3: 什麼是 VLAN？為何在家用網路需要？
  - A-Q4: 家用網路為何要做「網段隔離」？
  - A-Q5: Guest Network 與一般 VLAN 有何差異？
  - A-Q6: 什麼是 PoE？家用有何好處？
  - A-Q11: 什麼是 Traffic Rules（家長監護）？
  - A-Q14: 什麼是 Teleport VPN？和 L2TP 差在哪？
  - A-Q16: 什麼是 AdGuard Home？能做什麼？
  - A-Q17: 什麼是 DNS Rewrite？何時需要？
  - A-Q18: 什麼是反向代理（Reverse Proxy）？
  - A-Q19: Let’s Encrypt 憑證在家用有何價值？
  - A-Q22: 什麼是 UniFi Protect？與 NAS 錄影差異？
  - A-Q24: 什麼是 iperf3？在家用網路怎麼用？
  - C-Q2: 如何打造訪客/IOT 網路並排程停用？

- 中級者：建議學習 20 題
  - B-Q1: UniFi 如何跨設備部署 VLAN？
  - B-Q2: UniFi Guest Network 的隔離機制如何運作？
  - C-Q1: 如何在 UniFi 建置家庭 VLAN（TRUNK/MODEM/NAS/HOME/GUEST）？
  - C-Q3: 如何在 Synology 以 Docker 部署 AdGuard Home 並成為全網 DNS？
  - C-Q4: 如何設定 DNS Rewrite 讓內外一致訪問 NAS 服務？
  - C-Q5: 如何在 Synology 設定反向代理與 Let’s Encrypt？
  - A-Q12: 什麼是 Traffic Routes？
  - B-Q4: Traffic Routes 的策略路由如何生效？
  - B-Q5: UDM-PRO 1.12.22 的 Port Remapping 原理？
  - B-Q6: PPPoE 雙連線如何取得兩個公共 IP？
  - C-Q7: 如何實作雙 PPPoE 並用 Traffic Routes 讓 NAS 走 WAN2？
  - C-Q8: 如何用 Traffic Rules 做家長監護（時段封鎖社群）？
  - B-Q10: AdGuard Home 的 DNS 工作流程？
  - B-Q11: Synology 反向代理與憑證運作機制？
  - B-Q12: NAS 上 Docker 的儲存與備份關鍵？
  - C-Q9: 如何在 NAS 佈署 iperf3 並測 2.5G/10G？
  - D-Q2: Traffic Routes 指定網域無效怎麼辦？
  - D-Q5: 部署 AdGuard 後部分網站解析異常？
  - D-Q6: Guest 網路需要例外存取內網設備？
  - C-Q6: 如何啟用 Teleport VPN 並由手機連回家？

- 高級者：建議關注 15 題
  - A-Q7: SFP+ 與 RJ45（10GBase-T）差異？
  - A-Q8: CAT5E、CAT6A、DAC/光纖的取捨？
  - A-Q9: 什麼是 L3 Switch？與 L2 有何不同？
  - A-Q10: 家用為何需要 L3 Switch？
  - A-Q13: 為何要同時兩組 PPPoE（雙 WAN）？
  - A-Q23: Threat Management 是什麼？為何會降速？
  - B-Q7: L3 Switch 的跨 VLAN 路由流程？
  - B-Q8: Threat Management 封包處理流程？
  - B-Q9: Teleport（WireGuard）如何穿越 NAT？
  - B-Q13: iperf3 測試方法與數據解讀？
  - B-Q14: PoE 電力預算如何計算？
  - B-Q15: UniFi Protect 錄影與 NAS 備份串接原理？
  - B-Q16: SFP+ DAC 連結的優點與設計考量？
  - C-Q10: 如何用 SFP+ DAC 串 UDM-PRO、USW 與 NAS？
  - D-Q1: 跨 VLAN 只有約 1.4Gbps，效能不佳怎麼辦？