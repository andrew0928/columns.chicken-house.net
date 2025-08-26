# 原來在家裝 SERVER 的魔人還真不少...

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是家用伺服器（Home Server）？
- A簡: 家用伺服器是放在住家內，提供儲存、媒體、網頁、VPN等服務的電腦設備。
- A詳: 家用伺服器是架設在住家環境、持續運作以提供各類網路服務的電腦主機。常見用途包括檔案分享與備份、影音串流、私有雲同步、下載、網站與應用服務、VPN與遠端存取等。它可使用一般PC、NAS或微型電腦（如NUC、樹莓派）搭建，依需求選擇作業系統與軟體堆疊。相較公有雲，家用伺服器的核心價值是可控性、隱私、自主學習與長期成本優化，但需要基本網路、安全與維運知識。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q16, B-Q4

Q2: 為什麼要在家裝伺服器？
- A簡: 為掌控資料隱私、整合家庭服務、學習技術並降低長期雲端費用。
- A詳: 在家裝伺服器的動機包括：1) 資料主權與隱私，自有硬體與網路儲存更可控；2) 服務整合，如影音、相片、備份、檔案共享與自架網站；3) 學習成長，熟悉系統、網路與自動化；4) 成本考量，在固定帶寬與電費條件下，長期運行比訂閱多項雲服務更具彈性；5) 離線場景，內網亦可運作。缺點包含維運成本、硬體噪音用電與安全風險，需權衡需求與能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, A-Q19, B-Q9

Q3: 家用伺服器與NAS有何差異？
- A簡: NAS偏重檔案與備份；家用伺服器更通用，能跑多種服務與應用。
- A詳: NAS（Network Attached Storage）以檔案儲存、備份、共享為核心，內建易用管理介面與套件，適合入門快速上線。家用伺服器則更像通用主機，能運行多樣服務（Docker、VM、Web、DB、媒體、VPN），彈性高但維運較複雜。NAS近年亦支援容器與虛擬化，但受限硬體規格與封裝生態。選擇關鍵在於：是否偏好省心省時（NAS）或高自由度客製（自建伺服器）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q8, C-Q5

Q4: 家用伺服器與企業伺服器差在哪裡？
- A簡: 企業伺服器重可靠與擴充；家用注重成本、靜音與簡化維運。
- A詳: 企業伺服器採高可用設計（雙電源、ECC記憶體、RAID控制器、冗餘網卡與散熱），部署在機房，強調SLA、擴充與集中控管。家用伺服器多以一般PC/NAS組建，追求安靜、省電、性價比與足夠的可靠性；可用度與備援通常較低。安全策略與監控在企業更嚴格，而家用多以輕量工具與良好習慣為主。若家用負載關鍵性高，可逐步導入企業級做法（UPS、ECC、RAID、監控）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q6, D-Q10

Q5: 家用伺服器常見用途有哪些？
- A簡: 檔案備份、相片雲、影音串流、下載、網站、VPN與智慧家庭。
- A詳: 家用伺服器的典型情境包括：1) NAS功能：SMB/NFS分享、Time Machine、版本化備份；2) 影音：Plex/Jellyfin/Emby串流、即時轉碼；3) 相片與筆記：Nextcloud/Photoprism；4) 下載：BT/aria2/Usenet；5) 網站與應用：Docker化服務、部落格、Home Assistant；6) 網路：VPN（WireGuard）、DNS、反向代理；7) 監控：Prometheus/Grafana或Netdata；8) 自動化與排程備份至雲端。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, C-Q4, C-Q10

Q6: 規劃家用伺服器硬體時的核心要點是什麼？
- A簡: 明確用途，估算CPU/RAM/儲存/網路，平衡功耗與噪音。
- A詳: 先盤點用途與同時負載（串流轉碼、容器數、VM、資料庫、備份窗），估算：1) CPU：多執行緒與轉碼支援；2) 記憶體：容器＋檔案系統（ZFS/btrfs）占用；3) 儲存：容量、IOPS與RAID策略；4) 網路：內外網頻寬、Wi-Fi或有線；5) 機殼與散熱：靜音、風道與硬碟托架；6) 電源與UPS；7) 擴充：SATA/NVMe/PCIe。先做小型MVP，再按需擴充。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q6, D-Q3

Q7: 家用伺服器需要獨顯（GPU）嗎？
- A簡: 僅需特定工作如轉碼、AI推論、硬解編碼才需GPU。
- A詳: 多數家用服務（檔案、網站、VPN、下載）不需GPU。若有影音即時轉碼（Plex/Jellyfin）、硬體解編碼、AI推論（Stable Diffusion/Llama）或硬體加密加速時，GPU能顯著提升效能與能效。選擇時考量解碼支援（NVENC/QuickSync）、驅動生態、耗電與散熱。若僅播放原生格式或直通播放，CPU即可勝任，無需獨顯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q7, A-Q6

Q8: 記憶體容量如何評估？
- A簡: 以工作集計算：系統+服務+ZFS/btrfs快取+未來預留。
- A詳: 記憶體估算從底層開始：OS與背景約1–2GB；每個容器/服務占用加總；如用ZFS/btrfs，ARC/metadata會吃RAM，建議16–32GB起步；VM需額外預留。考量峰值、快取與升級空間，留20–30%餘裕。若記憶體不足，系統易Swap導致效能抖動，需監控實際使用曲線後調整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q6, A-Q6

Q9: SSD、HDD與NVMe的差異與選擇？
- A簡: NVMe效能最佳適合系統/熱資料，HDD容量大適合冷資料。
- A詳: HDD成本低、容量大，適合媒體、備份；SATA SSD有高IOPS與低延遲，適合系統盤、資料庫或容器層；NVMe SSD提供最高併發與吞吐，適用快取、VM磁碟或高IO應用。混合策略常見：系統/應用用SSD或NVMe，媒體存放HDD；可用SSD作讀寫快取。評估TBW壽命、溫度與散熱，並搭配備份/RAID策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q5, D-Q4

Q10: RAID、JBOD與單碟的差異是什麼？
- A簡: RAID提供冗餘或效能，JBOD僅拼容量，單碟最簡但無容錯。
- A詳: RAID 1/5/6/10等提供不同程度的容錯與效能；RAID 1鏡像、5/6奇偶校驗、10兼具效能與冗餘。JBOD是多碟獨立，無校驗與容錯但彈性高；單碟最簡單也最風險。家用常用ZFS/btrfs的軟RAID（RAIDZ1/2、鏡像），管理方便並具快照與校驗。無論RAID如何，備份仍不可或缺（3-2-1原則）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, C-Q5

Q11: 內網、外網、NAT與家庭路由的關係？
- A簡: 家庭路由透過NAT連網，內網與外網須靠轉發或VPN互通。
- A詳: 家庭網路通常由ISP給一組對外IP，路由器透過NAT讓多台內網設備共享上網。內網（LAN）對外不可見，外網（WAN）無法直接訪問內網服務，需使用端口轉發、UPnP或VPN。若處於CGNAT，外部無法主動連入，需反向代理或中繼。理解NAT對布署外部可訪問服務至關重要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q6, D-Q1

Q12: 動態IP與靜態IP的差別與影響？
- A簡: 動態IP常變動需DDNS；靜態IP穩定但成本較高且需申請。
- A詳: 多數家用網路由ISP分配動態IP，重連或定期更新會更換，導致外部連線需要DDNS對應域名。靜態IP固定不變，易於對外服務與DNS設定，但通常需付費申請或升級商用方案。若受CGNAT限制，即使IP固定也無法直連，需替代方案如反向代理或VPN。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q6, D-Q8

Q13: 什麼是連接埠轉發（Port Forwarding）？
- A簡: 將外網特定埠導入內網主機，使服務可被外部存取。
- A詳: 連接埠轉發是路由器功能，將外部請求（如TCP 443）轉交至內網指定IP與埠，常用於公開自架網站、SSH或媒體服務。需注意固定內網IP（DHCP保留）、防火牆放行與避免暴露敏感服務。若ISP為CGNAT或封鎖常見埠，需改埠、使用反向代理、Cloudflare Tunnel或VPN替代。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q4, C-Q6

Q14: 什麼是DDNS，何時需要？
- A簡: DDNS將變動IP與域名綁定，自動更新解析紀錄供訪問。
- A詳: 動態DNS（DDNS）透過客戶端定期回報當前IP給DNS提供者，當IP變動時自動更新A/AAAA紀錄，讓外界以固定域名連入。若使用動態IP且要對外提供服務，就需要DDNS。常見服務商包含Cloudflare、DuckDNS、No-IP。結合憑證自動簽發與反向代理，可實現穩定對外服務。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q6, C-Q4

Q15: 虛擬化（VM）與容器（Docker）的差異？
- A簡: VM隔離完整OS較重；容器共享核心輕量，部署更快。
- A詳: VM透過Hypervisor（如KVM/ESXi）虛擬整個硬體與OS，隔離強但資源開銷大；容器共享宿主核心，打包應用與依賴，啟動快、占用小、易遷移。家用環境常以Docker為主、VM補足Windows或特殊OS需求；進階者會用Proxmox或ESXi集中管理與隔離。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q3, D-Q5

Q16: 家用伺服器常見作業系統選項？
- A簡: Linux（Ubuntu/Debian）、TrueNAS、Unraid、Windows Server等。
- A詳: Linux（Ubuntu/Debian）生態完整、社群資源多；TrueNAS（Core/Scale）聚焦ZFS與儲存；Unraid以易用UI與混合陣列著稱；Windows Server/Pro適合AD或Windows生態。選擇依用途、學習曲線與授權而定。多數自架採Linux + Docker；偏儲存者考慮TrueNAS/Unraid。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q5, B-Q7

Q17: 什麼是無頭（Headless）運行？有何好處？
- A簡: 無螢幕鍵盤運行，透過SSH/網頁遠端管理，省空間與電力。
- A詳: Headless是伺服器不接螢幕與周邊，以網路遠端（SSH、Web UI、IPMI）管理。好處：節省空間與能耗、便於集中管理與自動化；缺點是初次安裝或故障時要備妥替代存取方式（序列埠、救援U盤、IPMI）。建議搭配固定內網IP、mDNS或DHCP保留與啟用SSH金鑰登入。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q1, D-Q5

Q18: 家用伺服器的功耗、噪音與散熱如何取捨？
- A簡: 選低TDP平台、良好風道與靜音風扇，兼顧效能與耐用。
- A詳: 長時運行重視能效與噪音。挑選低TDP CPU、金牌以上電源、合適機殼與大直徑低轉速風扇；硬碟振動需避震與通風；SSD/NVMe留意控制器溫度。可用電源治理（C-states）、硬碟停轉策略，平衡耗電與回應速度。監控功耗與溫度，設定告警，預防熱降頻與故障。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, D-Q4, A-Q6

Q19: 家用伺服器的安全基礎有哪些？
- A簡: 最小暴露面、強認證、定期更新、備份與監控告警。
- A詳: 安全基本面包含：僅暴露必要服務；使用反向代理與WAF、Fail2ban；強密碼與多因素認證；SSH金鑰登入禁密碼；定期更新系統與容器；最小權限原則（分離帳號/網段）；備份與還原演練；監控登入與異常流量。對外服務首選HTTPS與可信憑證，敏感服務僅允許VPN內存取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q2, D-Q1

Q20: 架家用伺服器會違反ISP或法律嗎？
- A簡: 視ISP條款與地方法規而定，避免商用與侵權內容。
- A詳: 多數ISP住宅方案允許合理自用伺服器，但可能限制對外服務或封鎖常見埠（25/80/443）。需檢視合約與AUP，避免濫用頻寬與公開侵權內容。法律面注意版權、個資與資安責任；若收費提供服務，可能需商用方案或營業登記。建議採用加密、存取控制與良好審計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q12, D-Q8

### Q&A 類別 B: 技術原理類

Q1: DHCP在家庭網路中如何運作？
- A簡: DHCP自動分配IP、閘道與DNS；可綁MAC保留固定IP。
- A詳: DHCP伺服器（通常在路由器上）在裝置加入網路時，透過DISCOVER/OFFER/REQUEST/ACK流程分配IP、子網遮罩、閘道與DNS。可設定IP保留（根據MAC）讓伺服器固定內網IP，方便Port Forward與ACL管理。租期到期需續租。若多DHCP源易衝突，應確保單一來源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, C-Q6, D-Q1

Q2: NAT與端口轉發的機制是什麼？
- A簡: NAT改寫位址/埠，轉發將外部封包導向內網主機。
- A詳: NAT透過連線追蹤表將私網位址映射至公網位址/埠；SNAT用於出站、DNAT用於入站。Port Forward其實是DNAT規則的一種，匹配外部埠號後改寫目的IP/埠，並允許回程。需同時配置防火牆放行。UPnP/NAT-PMP可自動開埠，但有安全風險，建議改為手動或嚴格ACL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q6, D-Q1

Q3: DDNS與DNS解析更新背後如何運作？
- A簡: 客戶端定期上報IP，DNS提供者更新記錄TTL範圍內生效。
- A詳: DDNS客戶端定期呼叫API或以DNS更新協定（如RFC2136）回報最新IP；DNS提供者更新A/AAAA紀錄並受TTL控制快取時間。若使用代理（如Cloudflare Proxy），對外顯示代管IP並透過反向代理轉發，能隱藏真實IP與增加安全性。更新頻率與API安全需配置妥善。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6, C-Q4

Q4: 反向代理與負載平衡的原理是什麼？
- A簡: 代理接收外部請求，再路由至內部服務並可做TLS等。
- A詳: 反向代理（Nginx/Traefik/Caddy）位於前端終結TLS，根據Host/Path將請求分派至後端服務，並可做壓縮、快取、重寫與WAF。負載平衡則按演算法將流量分散至多個實例，提升可用性與擴充性。家用常用一前端多服務，以子網域或路徑分流，並自動簽發Let’s Encrypt證書。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q2, A-Q19

Q5: HTTPS/TLS握手與憑證驗證機制？
- A簡: 透過非對稱金鑰交換會話密鑰，用憑證鏈驗證身份。
- A詳: TLS握手使用伺服器憑證（由受信任CA簽發）提供身份驗證，協商加密套件並交換會話密鑰（ECDHE等）。客戶端驗證憑證鏈與主機名匹配。家用環境多以ACME（Let’s Encrypt）自動簽發與續約，反向代理統一終結TLS，後端以內網HTTP或mTLS視需求加強安全。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q2, A-Q19

Q6: 各RAID層級的技術差異與取捨？
- A簡: RAID1鏡像可靠、RAID5/6容錯與容量平衡、RAID10效能佳。
- A詳: RAID 1以鏡像提供簡單容錯；RAID 5用單奇偶校驗容忍1碟故障，RAID 6容忍2碟；RAID 10由鏡像條帶化兼具效能與容錯。ZFS/軟RAID避免傳統RAID卡的單點故障並提供端到端校驗。家用建議重視備份優先於高階RAID，且注意重建時間與URE風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q5, D-Q4

Q7: ZFS與btrfs等現代檔案系統的機制？
- A簡: 提供寫入時複製、快照、校驗與軟RAID，提升資料完整性。
- A詳: ZFS/btrfs支援COW（寫入時複製）與端到端校驗，能偵測並修復位腐；支援快照、複製、壓縮、配額與儲存池管理。ZFS有ARC快取與RAIDZ，btrfs支援subvolume與RAID模式。它們吃RAM較多，需規劃記憶體。適合家用備份、NAS與版本化管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q10, C-Q5

Q8: 虛擬化（KVM/ESXi）與容器（Docker）的架構差異？
- A簡: 虛擬化有Hypervisor隔離完整OS；容器共享核心更輕巧。
- A詳: KVM/ESXi等Hypervisor抽象硬體給VM，相互隔離強；容器透過namespaces/cgroups隔離進程與資源，共享宿主核心。家用常以Proxmox整合KVM+LXC或以Docker為主。安全上VM隔離較佳；運維上容器編排快捷。視需求混合使用可達靈活與穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q3, D-Q5

Q9: 監控與日誌收集的基本原理？
- A簡: 以Agent或拉取指標，集中存儲與視覺化並設告警。
- A詳: 監控可分拉取（Prometheus）與推送（Telegraf/StatsD），指標存進時序庫，圖表化（Grafana）觀察趨勢；日誌用集中式（ELK/EFK）或輕量（Loki/Promtail），並設定告警（Alertmanager）。家用宜先從Netdata或簡化的Exporter起步，逐步擴展。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, D-Q3, D-Q4

Q10: 3-2-1備份原則與快照/版本化如何保障資料？
- A簡: 三份、兩種媒介、一份異地；快照提供快速回溯。
- A詳: 3-2-1指至少3份資料，存於2種不同媒介，其中1份在異地（雲端/離線）。檔案系統快照（ZFS/btrfs）與版本化能快速回復被誤刪/勒索影響的檔案。家用可用定期冷備份、雲端同步（rclone/restic），並測試還原流程確保可靠。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q10, A-Q10

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何規劃家用伺服器的整體架構與需求？
- A簡: 盤點用途與負載，設計網段、服務清單、備援與安全策略。
- A詳: 
  - 具體步驟: 
    1) 列出用途與優先級；2) 預估CPU/RAM/儲存；3) 設計網段/VLAN與固定IP；4) 選擇OS與容器/VM策略；5) 規劃反向代理、DDNS、TLS；6) 設備擺放、散熱與UPS；7) 備份與監控計畫。
  - 關鍵設定: 架構圖與服務清單（YAML/Notion），IP規劃表，DNS紀錄表。
  - 注意事項: 從小規模MVP起步，分批上線，建立變更紀錄與還原點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q4, C-Q10

Q2: 如何安裝Ubuntu Server並啟用SSH無頭管理？
- A簡: 製作開機碟安裝，設定使用者與SSH，透過固定IP管理。
- A詳: 
  - 實作步驟: 下載Ubuntu Server ISO，用Rufus/Etcher製作U盤；安裝時建立使用者、勾選OpenSSH；完成後以ssh連線。設定DHCP保留或Netplan固定IP。
  - 關鍵設定: 
    ```
    # /etc/ssh/sshd_config
    PasswordAuthentication no
    PermitRootLogin no
    ```
    ```
    # /etc/netplan/01-net.yaml
    dhcp4: no; addresses: [192.168.1.10/24]; gateway4: 192.168.1.1
    ```
  - 注意事項: 使用SSH金鑰、更新系統、開啟UFW僅允許必要埠。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, D-Q5, B-Q1

Q3: 如何在家用伺服器部署Docker與docker-compose？
- A簡: 安裝Docker與Compose，建立compose檔管理多服務。
- A詳: 
  - 實作步驟: 安裝Docker Engine與Compose；新增使用者至docker群組；建立/opt/stack/compose.yml；docker compose up -d啟動。
  - 關鍵程式碼:
    ```
    sudo apt install docker.io docker-compose-plugin
    sudo usermod -aG docker $USER
    ```
    ```
    services:
      whoami:
        image: traefik/whoami
        ports: ["8000:80"]
    ```
  - 注意事項: 使用bind mount或named volume，設定資源限制，定期更新鏡像。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q8, D-Q5

Q4: 如何架設反向代理（Nginx/Traefik）與自動HTTPS？
- A簡: 以反向代理終結TLS，透過ACME自動簽發與續期憑證。
- A詳: 
  - 實作步驟: 部署Traefik/Nginx Proxy Manager；設定DDNS與DNS驗證；定義路由規則與服務目標；開放443埠。
  - 關鍵設定（Traefik labels示例）:
    ```
    - traefik.http.routers.app.rule=Host(`app.example.com`)
    - traefik.http.routers.app.tls.certresolver=letsencrypt
    ```
  - 注意事項: 優先DNS-01驗證避開CGNAT限制；啟用HSTS/安全header；後端只開內網。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, D-Q2

Q5: 如何用ZFS或btrfs建立家用NAS儲存池？
- A簡: 準備多顆硬碟，建立池與資料集，啟用快照與壓縮。
- A詳: 
  - 實作步驟: 安裝zfsutils或啟用btrfs；建立池（zpool create / mkfs.btrfs）；建立dataset/subvolume；設定共享（SMB/NFS）。
  - 重要指令:
    ```
    zpool create tank mirror sda sdb
    zfs create tank/media
    zfs set compression=zstd tank
    ```
  - 注意事項: 同容量硬碟、ECC可加分、定期scrub、快照與備份到異地。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q6, D-Q4

Q6: 如何設定DDNS與路由器端口轉發以公開服務？
- A簡: 申請DDNS，更新IP；路由器轉發443/80至內網代理。
- A詳: 
  - 實作步驟: 註冊DDNS（Cloudflare/DuckDNS）；部署更新客戶端；在路由器設Port Forward外部443->代理主機:443；測試外部連線。
  - 範例（cloudflared DDNS腳本）:
    ```
    cfcli update --zone example.com --record app --ip $(curl -s ifconfig.me)
    ```
  - 注意事項: CGNAT需改用Cloudflare Tunnel或自建VPN；限制來源、啟用TLS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, D-Q1

Q7: 如何部署Jellyfin/Plex做家庭影音中心？
- A簡: 用Docker部署，設定媒體目錄與硬解碼，透過代理對外。
- A詳: 
  - 實作步驟: 建立資料夾/media，docker部署Jellyfin；掛載媒體路徑；啟用硬體解碼（VAAPI/NVENC）。
  - docker-compose示例:
    ```
    services:
      jellyfin:
        image: jellyfin/jellyfin
        devices: ["/dev/dri:/dev/dri"]
        volumes:
          - /srv/media:/media
        ports: ["8096:8096"]
    ```
  - 注意事項: 直通播放優先、轉碼需GPU/QuickSync；限速上傳避免塞滿頻寬。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, D-Q7, C-Q4

Q8: 如何建立家用VPN（WireGuard）以安全遠端存取？
- A簡: 安裝WireGuard，產生金鑰與Peers，開放UDP埠並設路由。
- A詳: 
  - 實作步驟: 安裝wireguard；生成key pair；設定wg0.conf；在路由器轉發UDP 51820；手機/筆電導入peer設定。
  - 關鍵設定:
    ```
    [Interface]
    Address=10.0.0.1/24
    [Peer]
    PublicKey=...
    AllowedIPs=10.0.0.0/24
    ```
  - 注意事項: 使用DNS內網解析；限制AllowedIPs；若CGNAT可用反向端口映射或雲VPS中繼。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q11, D-Q1, D-Q8

Q9: 如何部署監控（Prometheus+Grafana或Netdata）？
- A簡: 以Exporter收集指標，Prometheus拉取，Grafana視覺化告警。
- A詳: 
  - 實作步驟: Docker部署Prometheus/Grafana與Node Exporter；設prometheus.yml targets；建立Dashboard與告警規則。
  - 設定片段:
    ```
    scrape_configs:
      - job_name: node
        static_configs: [{targets: ["server:9100"]}]
    ```
  - 注意事項: 優先監控CPU溫度、磁碟SMART、ZFS狀態、網路延遲；限制外部存取。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, D-Q3, D-Q4

Q10: 如何實作3-2-1備份到雲端（restic/rclone）？
- A簡: 本地快照+外接碟+雲端庫，定期同步並測試還原。
- A詳: 
  - 實作步驟: 啟用ZFS/btrfs快照；用restic初始化雲端儲存（Backblaze/Wasabi）；排程備份；定期演練還原。
  - 指令範例:
    ```
    restic -r b2:repo init
    restic backup /srv/data
    restic forget --keep-daily 7 --keep-weekly 4 --prune
    ```
  - 注意事項: 加密金鑰妥善保存；排程避開高峰；排除暫存與媒體快取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q10, A-Q10

### Q&A 類別 D: 問題解決類（10題）

Q1: 外部無法連上家用服務該怎麼排查？
- A簡: 檢查IP與DDNS、埠轉發與防火牆、CGNAT與服務狀態。
- A詳: 
  - 症狀: 外網連線逾時或拒絕，內網可用。
  - 可能原因: DDNS未更新、路由器未轉發、防火牆阻擋、ISP封鎖或CGNAT、服務未啟動。
  - 解決步驟: 用手機4G測試; 檢查DDNS/A紀錄; 路由器DNAT與WAN IP; 開放路由與主機防火牆; 檢查服務日誌; 若CGNAT改用Cloudflare Tunnel/VPN。
  - 預防: 監控DDNS、設定健康檢查與告警、文件化網路配置。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, C-Q6

Q2: 瀏覽器顯示憑證錯誤或HTTPS失效怎麼辦？
- A簡: 檢查域名解析、憑證有效期、主機名匹配與代理設定。
- A詳: 
  - 症狀: 鎖頭紅色或NET::ERR_CERT_*錯誤。
  - 原因: 憑證過期、主機名不符、ACME驗證失敗、時鐘錯誤、代理未終結TLS。
  - 解決: 檢查DNS與DDNS；同步NTP時間；檢視代理（Traefik/Nginx）TLS設定與憑證路徑；改用DNS-01驗證；重新簽發並重載服務。
  - 預防: 自動續期與告警，統一由代理管理憑證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q4, A-Q19

Q3: 伺服器CPU飆高或溫度過熱如何處理？
- A簡: 找出高負載程序，優化服務與散熱，設定告警與限速。
- A詳: 
  - 症狀: 風扇轉速高、降頻、響應慢。
  - 原因: 轉碼/壓縮高負載、爬蟲/惡意流量、容器洩漏、散熱不良。
  - 解決: htop/Glances定位process；限制容器資源；優化轉碼（硬解）；調整風道與更換散熱；封鎖異常IP。
  - 預防: 監控溫度/負載、設定告警、規劃良好散熱與功耗管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q9, A-Q7

Q4: 硬碟SMART警告或讀寫錯誤如何應對？
- A簡: 立即備份，檢查SMART與ZFS狀態，更換故障碟重建。
- A詳: 
  - 症狀: I/O錯誤、SMART重配置或壞軌上升、陣列降級。
  - 原因: 硬碟老化、震動/過熱、電源不穩。
  - 解決: smartctl -a檢查；zpool status；標記故障並更換；重建/ resilver；檢查線材與電源；校驗資料完整。
  - 預防: 良好散熱、UPS、防震、定期scrub與SMART自測、異地備份。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q7, C-Q10

Q5: Docker容器內部無法解析DNS或無法連線怎麼辦？
- A簡: 檢查容器DNS設定、主機防火牆、bridge網段與路由。
- A詳: 
  - 症狀: apt update失敗、依賴服務無法解析。
  - 原因: /etc/resolv.conf配置、bridge衝突、代理或防火牆阻擋。
  - 解決: 指定--dns 1.1.1.1；檢查docker0網段與LAN衝突；重啟Docker；檢視iptables/nft規則；使用自定義網路。
  - 預防: 規劃不重疊網段；為Compose設置明確dns。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q3, A-Q11

Q6: 家用NAS的SMB/AFP傳輸速度很慢，如何改善？
- A簡: 檢查網線與雙工、MTU、磁碟與快取、協定與加密。
- A詳: 
  - 症狀: 局域網拷貝不達千兆預期。
  - 原因: 網線/埠速率降至100M、雙工不匹配、Jumbo MTU不一致、磁碟瓶頸、SMB加密或小檔案多。
  - 解決: 確認千兆連線與雙工；統一MTU；啟用快取（SSD/NVMe）；調整SMB參數（aio、large MTU）；並行傳輸。
  - 預防: 定期測速（iperf3）、合理檔案系統與快取規劃。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q7, C-Q5

Q7: 媒體伺服器轉碼卡頓或CPU爆滿如何優化？
- A簡: 啟用硬解碼、優先直通、調整畫質與限制同時轉碼。
- A詳: 
  - 症狀: 播放卡頓、高CPU、風扇噪音。
  - 原因: 軟體轉碼耗資源、碼率過高、同時轉碼過多。
  - 解決: 啟用VAAPI/NVENC/QSV；預先轉檔成兼容格式；設最大轉碼數；開啟轉碼快取；升級網路/硬體。
  - 預防: 資料前處理、媒體整理與客戶端能力評估。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q7, A-Q6

Q8: ISP封鎖連接埠或CGNAT，如何對外提供服務？
- A簡: 使用Cloudflare Tunnel、反向代理或租用VPS中繼。
- A詳: 
  - 症狀: 無法開放80/443或無公網IP。
  - 原因: ISP策略或NAT444。
  - 解決: 使用Cloudflare Tunnel/Zero Trust暴露內部服務；或自租VPS做反向代理/反向SSH；或以WireGuard搭橋。
  - 預防: 選擇可開埠ISP方案；規畫DNS-01驗證與非標準埠策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, C-Q4, C-Q6

Q9: IP變更導致外部連線失效，怎麼避免？
- A簡: 啟用DDNS與健康檢查，自動更新DNS並告警。
- A詳: 
  - 症狀: 突然無法以域名連線。
  - 原因: 動態IP更新、路由器重啟、ISP換IP。
  - 解決: 部署DDNS客戶端；縮短TTL；在監控中加入對外HTTP檢查與通知；使用Cloudflare API自動校正。
  - 預防: 若服務關鍵，考慮升級靜態IP或VPS中繼。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q3, C-Q6

Q10: 斷電後服務異常或檔案受損，如何復原與預防？
- A簡: 啟用UPS與自動關機，使用快照與備份快速還原。
- A詳: 
  - 症狀: 檔案系統檢查、資料庫損毀、容器未正常啟動。
  - 原因: 非正常關機導致寫入中斷。
  - 解決: fsck檢查檔案系統；還原ZFS/btrfs快照；從restic異地備份復原；逐一檢視服務日誌。
  - 預防: 配置UPS與NUT自動關機；啟用日常快照與定期備份；測試還原流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q10, A-Q4

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是家用伺服器（Home Server）？
    - A-Q2: 為什麼要在家裝伺服器？
    - A-Q3: 家用伺服器與NAS有何差異？
    - A-Q5: 家用伺服器常見用途有哪些？
    - A-Q11: 內網、外網、NAT與家庭路由的關係？
    - A-Q12: 動態IP與靜態IP的差別與影響？
    - A-Q13: 什麼是連接埠轉發（Port Forwarding）？
    - A-Q14: 什麼是DDNS，何時需要？
    - A-Q16: 家用伺服器常見作業系統選項？
    - A-Q17: 什麼是無頭（Headless）運行？有何好處？
    - B-Q1: DHCP在家庭網路中如何運作？
    - B-Q2: NAT與端口轉發的機制是什麼？
    - C-Q2: 如何安裝Ubuntu Server並啟用SSH無頭管理？
    - C-Q3: 如何在家用伺服器部署Docker與docker-compose？
    - D-Q1: 外部無法連上家用服務該怎麼排查？

- 中級者：建議學習哪 20 題
    - A-Q6: 規劃家用伺服器硬體時的核心要點是什麼？
    - A-Q7: 家用伺服器需要獨顯（GPU）嗎？
    - A-Q8: 記憶體容量如何評估？
    - A-Q9: SSD、HDD與NVMe的差異與選擇？
    - A-Q10: RAID、JBOD與單碟的差異是什麼？
    - A-Q18: 家用伺服器的功耗、噪音與散熱如何取捨？
    - A-Q19: 家用伺服器的安全基礎有哪些？
    - B-Q3: DDNS與DNS解析更新背後如何運作？
    - B-Q4: 反向代理與負載平衡的原理是什麼？
    - B-Q5: HTTPS/TLS握手與憑證驗證機制？
    - B-Q6: 各RAID層級的技術差異與取捨？
    - B-Q7: ZFS與btrfs等現代檔案系統的機制？
    - B-Q8: 虛擬化（KVM/ESXi）與容器（Docker）的架構差異？
    - B-Q9: 監控與日誌收集的基本原理？
    - C-Q1: 如何規劃家用伺服器的整體架構與需求？
    - C-Q4: 如何架設反向代理（Nginx/Traefik）與自動HTTPS？
    - C-Q5: 如何用ZFS或btrfs建立家用NAS儲存池？
    - C-Q6: 如何設定DDNS與路由器端口轉發以公開服務？
    - C-Q7: 如何部署Jellyfin/Plex做家庭影音中心？
    - D-Q2: 瀏覽器顯示憑證錯誤或HTTPS失效怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q4: 家用伺服器與企業伺服器差在哪裡？
    - A-Q15: 虛擬化（VM）與容器（Docker）的差異？
    - A-Q20: 架家用伺服器會違反ISP或法律嗎？
    - B-Q4: 反向代理與負載平衡的原理是什麼？
    - B-Q7: ZFS與btrfs等現代檔案系統的機制？
    - B-Q9: 監控與日誌收集的基本原理？
    - B-Q10: 3-2-1備份原則與快照/版本化如何保障資料？
    - C-Q8: 如何建立家用VPN（WireGuard）以安全遠端存取？
    - C-Q9: 如何部署監控（Prometheus+Grafana或Netdata）？
    - C-Q10: 如何實作3-2-1備份到雲端（restic/rclone）？
    - D-Q3: 伺服器CPU飆高或溫度過熱如何處理？
    - D-Q4: 硬碟SMART警告或讀寫錯誤如何應對？
    - D-Q5: Docker容器內部無法解析DNS或無法連線怎麼辦？
    - D-Q8: ISP封鎖連接埠或CGNAT，如何對外提供服務？
    - D-Q10: 斷電後服務異常或檔案受損，如何復原與預防？