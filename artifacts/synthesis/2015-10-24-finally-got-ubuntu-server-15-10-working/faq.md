# 終於搞定 Ubuntu Server 15.10：舊筆電變 Docker 主機

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 NAS？為什麼家用環境常用 NAS？
- A簡: NAS 是網路附加儲存設備，提供集中化檔案分享、備份與多用戶存取，家用常見於影音、資料同步與私有雲。
- A詳: NAS（Network Attached Storage）是連上區域網路的儲存設備，核心價值是集中化檔案管理與跨裝置存取。它通常內建檔案服務（SMB/NFS）、使用者權限、快照與備份，並常附應用套件如相簿、影音伺服器。家用環境中，NAS可作為私有雲、串流媒體中心與備份節點。部分 NAS（如 Synology/QNAP）支援 Docker，能以輕量方式部署服務，適合 24/7 低功耗運行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q14, B-Q22

Q2: 什麼是 Docker？它解決了什麼問題？
- A簡: Docker 是容器化平台，將應用與依賴封裝，實現可攜、隔離與一致部署，提升效率與可移植性。
- A詳: Docker 使用 Linux 的 namespaces 與 cgroups 將應用及其依賴打包成映像，運行於隔離的容器中。相較 VM，容器共享主機核心、更輕量、啟動快、密度高。Docker 解決「在我機器上可用」的環境不一致問題，透過不可變映像與標準化生命週期（build、ship、run）實現跨機器一致部署。對資源有限設備（如 NAS、舊筆電）特別有利。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q7, D-Q7

Q3: 什麼是 Ubuntu Server？與 Ubuntu Desktop 有何不同？
- A簡: Ubuntu Server 是無桌面版 Ubuntu，預設服務導向、資源占用低；Desktop 含 GUI，面向互動使用。
- A詳: Ubuntu Server 去除了桌面環境，預設安裝伺服器套件（如 OpenSSH、各類服務選單），以 CLI 管理為主，資源占用更低，適合 24/7 服務。Ubuntu Desktop 則提供圖形介面（GNOME 等），包含桌面應用與硬體驅動，有較佳互動體驗。對舊硬體或想集中資源於服務的場景，Server 版更合適；若需現場操作或顯卡支援，Desktop 版較友善。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, B-Q21, C-Q1

Q4: Ubuntu LTS 與非 LTS（如 15.10）有何差異？
- A簡: LTS 提供長期支援與穩定性；非 LTS 更新較新、支援週期短但硬體與軟體較新。
- A詳: LTS（Long Term Support）版本（如 14.04、16.04）提供 5 年安全維護與穩定性，適合生產環境。非 LTS（如 15.10）支援週期約 9 個月，內含較新 kernel 與驅動、較新軟體堆疊，對解決新硬體相容性有利。文中改用 15.10 成功安裝，即展現非 LTS 對新硬體/驅動的即時支援優勢，但長期運行仍建議選 LTS。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q1, D-Q2

Q5: 什麼是 Reverse Proxy（反向代理）？適用情境為何？
- A簡: 反向代理位於用戶與後端間，轉發請求、隱藏後端、可做 TLS 終止、緩存、負載平衡與路由。
- A詳: Reverse Proxy（如 Nginx/Apache）接收外部請求，依規則轉發至一或多個後端服務。它可統一處理 TLS 終止、壓縮、快取、路由（基於路徑/主機名）、負載平衡，並保護後端不直接暴露。家中多服務（Blog、API、NAS Apps）時，用一個公開入口搭配反向代理可簡化連線與憑證管理。文中作者用反向代理整合多服務。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q9, D-Q8

Q6: 什麼是 ASP.NET 5（現 .NET 7/8 的前身）？為何可在 Linux 上跑？
- A簡: ASP.NET 5（後更名 .NET Core）是跨平台框架，依賴 Kestrel 與自託管模式，能於 Linux 容器運行。
- A詳: ASP.NET 5 是 .NET Core 的早期名稱，設計為模組化、跨平台與開源。使用 Kestrel 作為跨平台網路伺服器，通常以前端反向代理（Nginx）承接公開流量，再轉發至 Kestrel。因其自託管與跨平台 runtime，搭配 Docker 可在 Linux 上部署。文章即預備在 Ubuntu/Docker 上運行 ASP.NET 服務。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q8, C-Q9

Q7: 用舊筆電當家用伺服器的優點是什麼？
- A簡: 低成本、低功耗、內建電池當簡易 UPS、含鍵盤網路卡；適合 24/7 小型服務。
- A詳: 舊筆電具備整合電源管理與低功耗 CPU，整機成本近零。內建電池可在短暫停電時維持運行，避免資料損毀，扮演簡易 UPS。鍵盤、觸控板與網卡一應俱全，快速上手。對 Docker 小型服務、檔案分享、學習測試非常合適。需注意散熱、硬碟健康與安全更新。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q21, C-Q10, D-Q7

Q8: 為何在 NAS 上使用 Docker？
- A簡: Docker 提供輕量隔離與快速部署，讓 NAS 在資源有限下仍可靈活跑多種應用。
- A詳: 多數 NAS 硬體資源有限（文中 DS-412+ 僅 Atom+1GB RAM），傳統 VM 開銷大。Docker 容器共享核心、資源足跡小，適合在 NAS 上以多容器方式部署 Blog、反向代理、資料處理等。容器化可快速回滾與備援，讓 NAS 不僅是儲存，更是應用平台。但需控制容器數量與記憶體使用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q19, D-Q7

Q9: 什麼是 Hyper-V？與 Docker 有何不同？
- A簡: Hyper-V 是類型一虛擬化平台，提供完整 VM；Docker 是 OS 層級容器，共享核心更輕量。
- A詳: Hyper-V 在硬體之上建立虛擬層，運行完整客體 OS 的 VM，隔離強、相容性佳但資源開銷高。Docker 使用 OS 內核隔離（namespaces/cgroups），容器共享主機核心，啟動快、密度高，但隔離層級較 VM 低。開發測試可用 Hyper-V；資源有限與快速部署偏向 Docker。文中提及 PC+Hyper-V 簡單，但選擇低功耗常開實體主機。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q11, A-Q27

Q10: 什麼是 Net Install？何時會被要求使用？
- A簡: Net Install 是透過網路抓套件的安裝模式，需可用網路與驅動；常見於精簡啟動媒體。
- A詳: Net Install 提供小型啟動映像，啟動後經由網路倉庫下載套件完成安裝。優點是映像小、軟體新；缺點是需可用的網路與相對應驅動。文中因錯用 USB 工具造成只支援 Net Install，卻又無法偵測網卡，導致卡關。選擇正確映像或製作工具可避免被迫 Net Install。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2, D-Q1

Q11: 製作開機 USB 的工具為何重要？
- A簡: 工具需正確寫入引導器與映像格式，避免安裝媒體損壞或意外變成 Net Install。
- A詳: 不同發行版/映像（ISOHybrid、UEFI/BIOS）需要對應的寫入模式（dd/raw、syslinux、GRUB）。錯誤工具或模式會導致引導錯誤、檔案系統不完整或無法偵測安裝來源，甚至被誤導成 Net Install。選擇支援目標映像與平台的工具與模式，並於寫入後驗證檔案與啟動性，能大幅降低安裝失敗率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q2, D-Q9

Q12: 為何伺服器建議設靜態 IP？
- A簡: 靜態 IP 確保服務位址穩定，避免 DHCP 變動導致 SSH、Samba、反向代理目標失聯。
- A詳: 伺服器通常提供固定端點（例如內網的 Samba 或外網反向代理），若使用 DHCP，IP 可能變更，造成連線中斷與 DNS 解析錯誤。設定靜態 IP（或 DHCP 保留租約）確保位址穩定，便於防火牆、路由與憑證設定。文中在安裝後即配置 SSH 與靜態 IP，以利 24/7 運行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q5, D-Q5

Q13: 什麼是 SSH Server？為何首要安裝？
- A簡: SSH 提供加密終端與檔案傳輸，允許無頭管理伺服器，是遠端維運的基礎。
- A詳: SSH（Secure Shell）透過金鑰/密碼認證建立加密連線，提供遠端 shell、埠轉發與檔案傳輸（SCP/SFTP）。對無螢幕的伺服器或放角落的主機，SSH 是主要管理方式。啟用後可無需實體螢幕進行設定、部署與故障排除，安全性高且彈性大。文中裝好 Ubuntu 後先設定 SSH，屬最佳實務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q4, D-Q4

Q14: 什麼是 Samba？與 NFS 有何差異？
- A簡: Samba 實作 SMB/CIFS，與 Windows 相容；NFS 為 Unix 傳統協定。前者跨平台友好，後者效能輕量。
- A詳: Samba 讓 Linux/Unix 提供 SMB 檔案與列印服務，Windows/macOS 皆可使用，適合混合環境與使用者驗證。NFS 原生於 Unix/Linux，協定簡單、延遲低、效能佳，權限模型偏 POSIX。家用與 Windows 客戶端多時選 Samba更便利；純 Linux 環境與高效能需求可考慮 NFS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q22, C-Q6

Q15: 拔除無線網卡為何可能讓安裝成功？
- A簡: 問題網卡可能因驅動/韌體/IRQ 衝突卡住偵測；移除後安裝程式繞過錯誤正常進行。
- A詳: 某些舊無線網卡需非自由韌體或驅動不成熟，安裝程式嘗試載入時可能卡住或造成內核錯誤。硬體探測也可能引發 IRQ 衝突或超時。實體移除可避免載入問題模組，讓安裝流程順利。待系統完成並更新內核/韌體，再插回測試更穩妥。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, D-Q10

Q16: 安裝時出現「CDROM 內容不對」代表什麼？
- A簡: 表示安裝來源驗證失敗，可能因 ISO 寫入錯誤、掛載問題或來源與版本不匹配。
- A詳: 安裝器會檢查安裝來源內容與目錄結構（pool、dists 等），若媒體損壞、嘗試從錯誤裝置讀取或使用了不相容的寫入工具，會報該錯。也可能是 UEFI/BIOS 模式不一致導致讀取異常。重做 USB、確認校驗碼與正確啟動模式通常可解決。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q2, D-Q2

Q17: 什麼是 MD5 校驗？為何要驗證映像檔？
- A簡: MD5 用於檔案完整性檢查，確保下載未損壞；但非強安全用途，僅驗證一致性。
- A詳: MD5 將檔案映射為摘要，下載後比對發行方提供的 MD5 值，可檢測傳輸錯誤或損毀。然而 MD5 已有碰撞風險，不適合作為安全簽章。對安裝映像，驗證 SHA256 或簽章（GPG）更佳。文中即比對 MD5 確認非下載損毀，改從工具與驅動面排查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q16, C-Q2, D-Q2

Q18: 為何需要 24/7 低功耗主機？
- A簡: 長時運行降低電費與噪音，確保服務穩定可用，適合家庭與小型自架應用。
- A詳: 家用或實驗性服務（Blog、雲端備份、媒體串流）需全天候可用。低功耗主機（NAS、舊筆電）在待機和負載下的能耗低，散熱簡單、噪音小，總持有成本更低。與傳統桌機或雲端租用相比，對輕量需求更經濟。在資源有限下，容器化能提升利用率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q8, C-Q10

Q19: Docker Engine 與容器的關係是什麼？
- A簡: Docker Engine 負責管理與運行容器，容器是基於映像的隔離執行單元。
- A詳: Docker Engine 提供 API、守護程序與 CLI，負責拉取映像、建立/啟動容器、網路與儲存管理。容器由映像層加上可寫層構成，使用 Linux 核心隔離與資源控制。Engine 是控制平面與資料平面樞紐，映像與容器則是部署單位。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q7, D-Q7

Q20: 反向代理與負載平衡的差異？
- A簡: 反向代理聚合與轉發請求；負載平衡則著重在分散流量。多數代理能同時擔任 LB。
- A詳: 反向代理是前置入口，處理 TLS、快取與路由；負載平衡關注在多後端間分配請求、健康檢查與容錯。Nginx/HAProxy 既可作反向代理也可做負載平衡。家用多服務常先從反向代理開始，流量上升再引入多實例與 LB 策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q9, D-Q8

Q21: 以筆電電池作為簡易 UPS 的概念？
- A簡: 筆電在停電時可短暫續航，讓服務平順關機，降低資料損毀風險。
- A詳: 筆電內建電池可在市電中斷時立即提供電力，OS 亦能偵測電量，設定臨界電量自動安全關機或暫停。對家用伺服器，這提供了基本的不斷電緩衝，避免突然斷電造成檔案系統損毀或資料遺失。仍建議搭配自動備份與定期測試電池健康。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q20, C-Q10, D-Q7

Q22: GoDaddy 共享主機與自架主機的差異？
- A簡: 共享主機管理簡單但受限多；自架主機彈性大、需自行維運與安全管理。
- A詳: 共享主機提供托管平台、簡易管理與支援，適合靜態網站與一般需求；限制在於自訂性、資源隔離與性能可預期性。自架（NAS/舊筆電）能高度自訂、部署容器與代理，但需負責更新、監控、備份與安全。文中作者將 Blog 自架於 NAS，獲得彈性並整合反向代理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q9, D-Q8, A-Q28

Q23: 在 Linux 上跑 ASP.NET 是否可行？
- A簡: 可行。ASP.NET Core 跨平台，透過 Kestrel 與 Docker 容器在 Linux 穩定運行。
- A詳: 自 .NET Core 起，ASP.NET 即支援 Linux/macOS。以 Kestrel 作為內嵌伺服器，並建議以前端代理承接 TLS 與公開端口。官方映像（mcr.microsoft.com/dotnet/aspnet）提供容器環境，CI/CD 易於整合。文章場景就是規畫於 Ubuntu/Docker 上跑 ASP.NET。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q8, C-Q9

Q24: Ubuntu Desktop 與 Server 在安裝體驗的差異？
- A簡: Desktop 著重圖形及驅動便利；Server 精簡、命令列導向，對舊硬體更友好。
- A詳: Desktop 安裝器常自動載入圖形驅動與固件，安裝後即用；但在舊硬體或特定顯卡上可能卡住。Server 安裝體驗偏 CLI，少載入 GUI 驅動與組件，減少相容風險。文中 Desktop 開到桌面就不動，改用 Server 成功完成安裝。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q21, C-Q1, D-Q3

Q25: 為何選擇 Ubuntu 15.10 解決安裝問題？
- A簡: 15.10 的較新核心與驅動改善硬體相容性，避開舊版的驅動缺失。
- A詳: 舊 LTS（12.04/14.04）使用較舊 kernel 與驅動，對某些網卡或晶片支援不足。非 LTS 的 15.10 匯入較新硬體支援，安裝器亦更穩定。文中多版失敗後，移除問題 Wi-Fi、選 15.10 終於成功，顯示新內核的相容優勢。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q10, C-Q1

Q26: 舊硬體對 Linux 相容性會遇到什麼挑戰？
- A簡: 可能缺驅動/韌體、IRQ 衝突、顯示相容性差、安裝媒體啟動困難等。
- A詳: 舊機種可能使用老舊或少見晶片，社群維護度低，導致驅動缺失或固件需手動安裝。顯卡可能不支援新 X/Wayland，或需特定參數。存儲控制器/USB 控制器也可能不穩。解法含：換版本、更新 BIOS、移除問題硬體、使用 Server 安裝、禁用某些模組。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q21, D-Q10

Q27: Docker 與虛擬機的差異與取捨？
- A簡: 容器輕量啟動快、共享核心；VM 隔離強、相容性高。依安全與資源需求選擇。
- A詳: 容器適合微服務、高密度、快速交付；VM 適合異質 OS、強隔離、需 kernel 級自訂。資源有限設備多選容器；需 Windows 客體或強隔離時選 VM。也可混用：用 VM 隔離宿主，再在 VM 內跑容器。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q12, A-Q9

Q28: 家庭環境導入反向代理的核心價值？
- A簡: 單一入口管理多服務、集中 TLS、簡化路由與外網暴露，提升安全與維運性。
- A詳: 以一個公開網域/埠承接請求，基於路徑或子網域轉發到各內部服務（Blog、API、NAS Apps）。集中憑證更新（Let's Encrypt）、同源策略處理、存取控制與頻率限制，亦可加快回應（快取/壓縮）。家用架構清晰、擴展容易。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q9, D-Q8

Q29: 24 小時常開主機的安全重點有哪些？
- A簡: 持續更新、最小暴露面、強認證、備份、監控與資源限制，降低入侵風險。
- A詳: 關閉不必要服務、只暴露反向代理端口、啟用防火牆；SSH 使用金鑰與非預設埠；系統與容器定期更新；定期備份與異地保存；導入 Fail2ban、日誌與監控工具；容器資源限制避免資源枯竭。家庭網路亦需路由器更新與強密碼。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q4, C-Q9, D-Q8

Q30: 低階 CPU 與 1GB RAM 對 Docker 部署的限制？
- A簡: 容器數量與類型受限，需選輕量映像、限制記憶體、避免重度資料庫與編譯工作。
- A詳: Atom 等低階 CPU 多核心少、單核性能弱，1GB RAM 易因快取/GC 導致 swap。部署上採用 Alpine/Distroless 映像、限制容器 memory/cpu、以反向代理前置、關閉不必要功能。資料庫與搜尋等重服務盡量外部化或雲端化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, C-Q7, D-Q7


### Q&A 類別 B: 技術原理類

Q1: Ubuntu 安裝流程如何運作？
- A簡: 由 BIOS/UEFI 啟動至引導載入器，載入安裝核心與 initrd，偵測硬體、掛載來源、安裝套件。
- A詳: 安裝從 BIOS/UEFI 選擇 USB 啟動，GRUB/syslinux 載入 Linux kernel 與 initrd。安裝器（如 debian-installer/subiquity）偵測儲存/網路/顯示，掛載安裝來源（USB/CD/Net），設定分割與檔案系統，選擇套件集合，複製系統檔至目標磁碟，安裝引導程式，重開機。核心組件：引導載入器、kernel+initrd、安裝器、套件管理器與目標系統。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q5, D-Q2

Q2: Net Install 的機制與流程是什麼？
- A簡: 使用精簡啟動映像，透過網路倉庫下載套件，需驅動、DHCP/DNS 與穩定連線。
- A詳: Netboot 映像啟動後載入網路驅動，透過 DHCP 獲取 IP/DNS，選定鏡像站，下載套件列表與必要映像，進行分割與套件安裝。關鍵步驟：網卡偵測、鏡像設定、下載/校驗、安裝核心與基本系統。若網卡無驅動或鏡像無法連通即失敗。核心組件：netboot kernel、initrd、debian-installer、APT。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, D-Q1, C-Q3

Q3: Linux 如何偵測並載入網路卡驅動？
- A簡: 內核透過 PCI/USB 掃描識別裝置，比對驅動，載入模組並可載入外部韌體。
- A詳: 開機時，kernel 掃描總線取得裝置 ID，透過模組別名比對相符驅動（.ko），載入後初始化裝置，若需韌體則由 udev 載入檔案。關鍵步驟：裝置枚舉、模組解析、韌體檔載入、網卡命名與連線。固件缺失、模組錯誤或 IRQ 衝突會導致失敗。核心組件：udev、modprobe、/lib/firmware。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, D-Q1, D-Q10

Q4: 為何移除 Wi-Fi 卡可繞過安裝卡住？
- A簡: 移除有問題硬體避免驅動或韌體載入失敗，使安裝器跳過該裝置正常進行。
- A詳: 問題網卡在安裝階段可能觸發內核 BUG、韌體載入超時或 PCI IRQ 衝突，使安裝器停滯。物理移除讓內核不再枚舉該裝置，避免載入問題模組。安裝完成後更新 kernel/firmware 再嘗試安裝，可降低風險。核心組件：PCI 熱插拔、udev 規則、模組黑名單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q10, C-Q1

Q5: 「CDROM 內容不對」的技術原因與判斷？
- A簡: 安裝來源結構或校驗不符；可能是 USB 寫入方式錯誤、掛載錯裝置或 UEFI/BIOS 模式不匹配。
- A詳: 安裝器會檢查來源目錄（/pool,/dists）與 Release 檔校驗。若使用不支援的 USB 寫入工具（改變引導/檔案結構）、或以 Netboot 啟動卻指向錯誤來源，會出錯。UEFI/BIOS 啟動路徑不同也會影響。步驟：重製 USB（dd/正確模式）、檢查 SHA256/GPG、確認啟動模式一致。核心：引導載入器、檔案系統、APT 來源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, A-Q11, D-Q2

Q6: USB 製作工具差異的技術面？
- A簡: 有 raw/dd 寫入、syslinux 與 GRUB 三類，需配合 ISOHybrid 與 UEFI/BIOS 支援。
- A詳: dd/raw 將 ISO 位元對位元寫入，最忠實；syslinux 需萃取檔案並配置引導；GRUB 模式可支援多 ISO 與 UEFI。ISOHybrid 支援 dd；若 ISO 需特殊引導，syslinux/GRUB 必須正確配置。錯誤模式會導致引導失敗或來源不識別。核心：MBR/GPT、El Torito、UEFI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q2, D-Q9

Q7: 為何新版 Ubuntu 對硬體支援更好？
- A簡: 新版內核、驅動與韌體集合更完整，修補相容性與穩定性問題。
- A詳: Linux kernel 每版加入新驅動、修復 BUG，配套的 firmware 與使用者空間工具也更新。相較舊 LTS，新版常能即時支援新/舊裝置問題。文中 15.10 成功安裝即反映新堆疊改善。核心：kernel、linux-firmware、Mesa/X。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q25, D-Q10, C-Q1

Q8: SSH 的運作機制是什麼？
- A簡: 透過握手協商演算法與金鑰，建立加密通道，支援遠端指令與檔案傳輸。
- A詳: 客戶端與伺服端協商加密/完整性演算法，伺服端提供主機鍵，客戶端驗證後進行使用者認證（密碼/公鑰）。建立會話通道後，傳輸 shell、埠轉發或 SFTP。核心步驟：演算法協商、主機鍵驗證、使用者認證、通道多路復用。組件：OpenSSH server/client、authorized_keys、sshd_config。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q4, D-Q4

Q9: 靜態 IP 設定在網路中的原理？
- A簡: 以固定配置替代 DHCP，手動指定 IP/遮罩/閘道/DNS，確保可預期路由。
- A詳: DHCP 自動分配參數，但可能變動。靜態設定直接寫入網卡介面，維持不變。需確保子網與閘道正確，避免與 DHCP 範圍衝突。核心步驟：設定地址、路由、DNS 解析。組件：ifupdown/systemd-networkd、resolv.conf、路由表。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q5, D-Q5

Q10: Samba/SMB 的協議與元件？
- A簡: SMB 為檔案分享協議，Samba 實作伺服端，含 smbd/nmbd/winbind，支援 ACL 與整合 AD。
- A詳: SMB 提供檔案/印表分享、鎖定、通知等。Samba 作為開源實作，smbd 處理檔案服務，nmbd/WS-Discovery 提供探索，winbind 整合 AD/LDAP。支援 NTFS ACL、離線快取與簽章。核心：協議版本（SMB1/2/3）、共享設定、使用者驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6, D-Q6

Q11: Docker 的核心技術原理？
- A簡: 基於 namespaces/cgroups 進行隔離，AUFS/OverlayFS 分層檔案，守護程序管理生命周期。
- A詳: namespaces 隔離 PID/NET/MNT/UTS/IPC；cgroups 控制 CPU/記憶體；儲存採用分層文件系統（Overlay2 等）；網路由 bridge/veth/NAT 管理。docker daemon 提供 API，CLI 操作映像與容器。步驟：build 映像、run 容器、網路與卷掛載。組件：containerd、runc、shim。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q2, A-Q19, C-Q7

Q12: Hyper-V 的虛擬化架構？
- A簡: 類型一 hypervisor，將硬體虛擬化供 VM 使用，透過 VMBus 與整合服務提升效能。
- A詳: Hyper-V 直接運行於硬體之上，分 root/parent 分割與子 VM。VMBus 提供裝置虛擬化通道，整合服務（時間同步、心跳、檔案複製）提升體驗。支援動態記憶體、快照、虛擬交換器。與容器不同，VM 有完整內核與 OS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q27, D-Q7

Q13: Reverse Proxy 的工作機制？
- A簡: L7 代理接收請求，基於主機名/路徑路由，支援 TLS 終止、緩存、壓縮與健康檢查。
- A詳: 代理解析 HTTP 要求頭與 SNI，選擇上游；可終止 TLS、重寫頭、快取靜態、Gzip。健康檢查確保只轉發至健康實例。關鍵步驟：接收、匹配、轉發、回應。組件：Nginx/HAProxy、憑證與上游池。家用可統一入口與憑證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q9, D-Q8

Q14: Nginx 與 Apache 作為反向代理的差異？
- A簡: Nginx 事件驅動、記憶體足跡小；Apache 模組豐富、相容性高。小型場景常選 Nginx。
- A詳: Nginx 使用非阻塞事件迴圈，適合靜態與高併發；Apache 有 Prefork/Worker/Event，多功能模組。代理能力兩者皆強，選擇依資源與熟悉度。家用低資源偏 Nginx。核心：處理模型、配置語法、模組生態。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q9, A-Q28, D-Q8

Q15: Linux 的開機流程與常見卡關點？
- A簡: 從 BIOS/UEFI 到引導載入器，載入 kernel/initramfs，再切換 root；驅動與檔案系統常是關鍵。
- A詳: BIOS/UEFI 初始化硬體，移交引導載入器（GRUB），載入 kernel 與 initramfs，初始化驅動、掛載根檔案系統，啟動 systemd。卡關常在驅動載入、檔案系統檢查、圖形堆疊啟動。日誌與 kernel 參數（nomodeset）是排障關鍵。組件：GRUB、systemd、dracut/initramfs-tools。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, D-Q10, C-Q1

Q16: MD5/SHA 校驗與簽章的原理與限制？
- A簡: 雜湊驗完整性，簽章驗來源與未篡改；MD5 弱，建議 SHA256+GPG 簽章。
- A詳: 雜湊將資料映成固定長度值，用於檢查傳輸損壞；數位簽章使用私鑰簽、公開鑰驗，確保來源與完整性。MD5 已有碰撞攻擊可能；SHA256 更安全。最佳做法：驗 SHA256，並驗 GPG 簽章。組件：sha256sum、gpg。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q2, D-Q2

Q17: Linux 韌體（firmware）載入的流程？
- A簡: 驅動請求韌體檔，udev 從 /lib/firmware 載入交給裝置初始化。
- A詳: 部分裝置需使用者空間提供韌體二進位。驅動呼叫 request_firmware，udev 偵測後讀取對應檔案，傳給核心驅動以完成裝置初始化。缺失會導致裝置不可用或不穩。解法：安裝 linux-firmware 或供應商套件。組件：udev、firmware 檔、內核 API。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, D-Q10, A-Q15

Q18: ASP.NET 在 Linux 的運作與代理整合？
- A簡: Kestrel 自託管處理 HTTP，前置 Nginx 代理做 TLS 與路由，容器化便於部署。
- A詳: ASP.NET Core 應用內嵌 Kestrel，負責 HTTP 處理。Nginx 作反向代理與 TLS 終止，轉發至 Kestrel（127.0.0.1:5000）。容器化用官方映像執行，掛載設定與環境變數達成 12factor。組件：Kestrel、systemd/容器、Nginx。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q8, C-Q9

Q19: Docker 在 NAS/低資源裝置的資源隔離？
- A簡: 利用 cgroups 限制 CPU/記憶體/IO，bridge 網路隔離，卷掛載管理存儲。
- A詳: cgroups 設定限額避免單容器耗盡資源；網路以 linux bridge + iptables NAT 提供獨立網段；卷將資料持久化至宿主或外接磁碟。核心：--memory、--cpus、storage driver（Overlay2）。對 NAS 必須謹慎設定限額與 IO 優先順序。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q30, C-Q7, D-Q7

Q20: 筆電電池作為 UPS 的保護機制？
- A簡: 透過充放電控制與電量回報，系統可監控並在臨界時安全關機。
- A詳: 智慧電池提供電量/健康資訊，ACPI 匯報給 OS。系統守護行程（upower/systemd-logind）可在低電量觸發動作（休眠/關機）。充電控制避免過充，延長壽命。搭配腳本可在停電自動關閉服務。組件：ACPI、upower、systemd。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q10, D-Q7

Q21: 桌面環境啟動（X/Wayland）為何會卡死？
- A簡: 顯卡驅動/模組不相容、Kernel Mode Setting 問題或韌體缺失導致圖形堆疊失效。
- A詳: 啟動圖形需 KMS、驅動（nouveau/amdgpu/i915 或廠商）、Mesa/GL 堆疊。舊顯卡或不相容組合會造成黑屏或卡死。可用 nomodeset、安全圖形模式、或改 Server 安裝避開 GUI。組件：kernel 驅動、Xorg/Wayland、DRM/KMS。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, D-Q3, C-Q1

Q22: Windows 如何探索到 Samba 分享？
- A簡: 透過 NetBIOS/WS-Discovery 或 DNS 名稱解析，經 SMB 協議驗證後列出共享。
- A詳: Windows 用 NetBIOS 與現代 WS-Discovery/LLMNR 發現區網服務，或直接以 \\hostname 存取。連線時使用 SMB 協議談判版本，提供認證資訊（本機/AD）。防火牆與 SMB1 停用會影響探索。組件：nmbd/WS-Discovery、smbd、DNS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6, D-Q6


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何選擇適合舊筆電的 Ubuntu 版本？
- A簡: 優先選 LTS；若驅動相容性差，嘗試較新中繼版；以 Server 無 GUI 降低相容風險。
- A詳: 具體實作步驟
  - 先試最新 LTS Server 版；若安裝卡住，改用較新中繼版測試驅動。
  - 啟動參數加入「nomodeset」或拔除問題周邊（如 Wi-Fi）。
  - 更新 BIOS 後再嘗試；成功後可考慮升級至對應 LTS HWE。
  關鍵程式碼片段或設定
  - 開機時於 GRUB 編輯 kernel 參數加上「nomodeset」。
  注意事項與最佳實踐
  - 優先 Server 版；成功後再最小化安裝服務，降低資源占用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, A-Q25, B-Q7

Q2: 如何正確製作 Ubuntu 可開機 USB？
- A簡: 下載官方 ISO，驗證 SHA256/GPG，使用支援 ISOHybrid 的工具以 dd/raw 模式寫入。
- A詳: 具體實作步驟
  - 下載 ISO 並驗證：`sha256sum ubuntu.iso`；必要時 `gpg --verify`。
  - 於 Linux：`sudo dd if=ubuntu.iso of=/dev/sdX bs=4M status=progress oflag=sync`
  - 於 Windows：選擇支援 ISOHybrid 的工具，使用「DD/Raw」模式。
  關鍵程式碼片段或設定
  - dd 命令如上；完成後安全移除再開機選 USB。
  注意事項與最佳實踐
  - 確認 UEFI/BIOS 模式與目標一致；避免舊工具破壞引導結構。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q6, D-Q9

Q3: 如何避免被迫使用 Net Install？
- A簡: 使用完整安裝映像與正確工具製作 USB，確保本地來源可用且網卡非必需。
- A詳: 具體實作步驟
  - 下載「完整」或「Live Server」映像，不用 netboot 版。
  - 製作 USB 時採 dd/raw；啟動選擇正確項目。
  - 若安裝器要求網路，選擇跳過或手動設定離線。
  關鍵程式碼片段或設定
  - 無需特別代碼；重點在映像與製作模式。
  注意事項與最佳實踐
  - 若需網路再安裝韌體，準備另一支 USB 存放 firmware。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q2, D-Q1

Q4: Ubuntu 安裝後如何設定 SSH 伺服器？
- A簡: 安裝 openssh-server，開放防火牆，配置金鑰登入與基本安全設定。
- A詳: 具體實作步驟
  - 安裝：`sudo apt update && sudo apt install -y openssh-server`
  - 啟用：`sudo systemctl enable --now ssh`
  - 建立金鑰：在客戶端 `ssh-keygen`，上傳 `ssh-copy-id user@host`
  關鍵程式碼片段或設定
  - 編輯 `/etc/ssh/sshd_config`：`PasswordAuthentication no`、`PermitRootLogin no`
  注意事項與最佳實踐
  - 變更預設埠、啟用防火牆 `ufw allow <port>/tcp`，備份金鑰。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q8, D-Q4

Q5: 如何在 Ubuntu 15.10 設定靜態 IP？
- A簡: 編輯 `/etc/network/interfaces` 指定地址/閘道/DNS，重啟網路服務或系統。
- A詳: 具體實作步驟
  - 編輯：`/etc/network/interfaces`
    - `auto eth0`
    - `iface eth0 inet static`
    - `address 192.168.1.10/24`
    - `gateway 192.168.1.1`
    - `dns-nameservers 1.1.1.1 8.8.8.8`
  - 套用：`sudo systemctl restart networking`
  關鍵程式碼片段或設定
  - 如上；Desktop 版可能需停用 NetworkManager 管理該介面。
  注意事項與最佳實踐
  - 避免與 DHCP 範圍衝突；或在路由器做 DHCP 保留綁定 MAC。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q9, D-Q5

Q6: 如何安裝並設定 Samba 分享資料夾？
- A簡: 安裝 samba，建立共享目錄與使用者，編輯 smb.conf 定義分享，重啟服務。
- A詳: 具體實作步驟
  - 安裝：`sudo apt install -y samba`
  - 建立資料夾：`sudo mkdir -p /srv/share && sudo chown -R user:user /srv/share`
  - 使用者：`sudo smbpasswd -a user`
  - 配置：`/etc/samba/smb.conf` 增加
    - `[share] path=/srv/share read only=no browsable=yes`
  - 重啟：`sudo systemctl restart smbd`
  關鍵程式碼片段或設定
  - 防火牆：`ufw allow 445/tcp`
  注意事項與最佳實踐
  - 設定有效的 Unix 權限/ACL；限制可見性與只給必要帳號。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q10, D-Q6

Q7: 如何在 Ubuntu 15.10 安裝 Docker？
- A簡: 使用套件庫安裝 docker.io 或官方 repo，加入使用者至 docker 群組並啟動服務。
- A詳: 具體實作步驟
  - `sudo apt update && sudo apt install -y docker.io`
  - 啟用：`sudo systemctl enable --now docker`
  - 權限：`sudo usermod -aG docker $USER` 後重新登入
  關鍵程式碼片段或設定
  - 測試：`docker run --rm hello-world`
  注意事項與最佳實踐
  - 低資源系統限制 `--memory`、使用輕量映像；15.10 已 EOL，建議升 LTS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q11, D-Q7

Q8: 如何用 Docker 部署 ASP.NET 範例服務？
- A簡: 以官方 .NET 映像建置，Expose 端口，docker run 啟動；搭配環境變數設定。
- A詳: 具體實作步驟
  - 建立 Dockerfile：
    - `FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base`
    - `WORKDIR /app; COPY ./publish .; EXPOSE 5000`
    - `ENTRYPOINT ["dotnet","YourApp.dll"]`
  - 建置與執行：`docker build -t myapp .`；`docker run -d -p 5000:5000 myapp`
  關鍵程式碼片段或設定
  - 環境：`-e ASPNETCORE_URLS=http://0.0.0.0:5000`
  注意事項與最佳實踐
  - 使用多階段建置分離 SDK/Runtime；寫健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q18, C-Q9

Q9: 如何設定 Nginx 反向代理至 Docker 內的 ASP.NET？
- A簡: 安裝 Nginx，設定 server 區塊 proxy_pass 至容器，處理標頭與 TLS。
- A詳: 具體實作步驟
  - 安裝：`sudo apt install -y nginx`
  - 設定 `/etc/nginx/sites-available/app`：
    - `server { listen 80; server_name your.domain;`
    - `location / { proxy_pass http://127.0.0.1:5000;`
    - `proxy_set_header Host $host; proxy_set_header X-Forwarded-For $remote_addr; } }`
  - 啟用：`ln -s ../sites-available/app /etc/nginx/sites-enabled/ && nginx -t && systemctl reload nginx`
  關鍵程式碼片段或設定
  - TLS：用 certbot 配置 `listen 443 ssl;`
  注意事項與最佳實踐
  - 啟用 Proxy Protocol/Forwarded headers；限制緩慢連線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q13, D-Q8

Q10: 如何將舊筆電優化為 24/7 低功耗伺服器？
- A簡: 關閉螢幕與不必要硬體、啟用省電策略、清理啟動服務並確保散熱與監控。
- A詳: 具體實作步驟
  - BIOS 關閉未用設備（BT/指紋/讀卡）。
  - OS 關閉螢幕背光、禁休眠；設定 `powertop --auto-tune`。
  - 移除 GUI、停用不必要服務；清理啟動項。
  關鍵程式碼片段或設定
  - `systemctl disable <service>`、`tlp` 套件
  注意事項與最佳實踐
  - 定期清理灰塵、更換散熱膏；監控溫度與 SMART 健康，避免硬碟過熱。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q7, A-Q18, B-Q20


### Q&A 類別 D: 問題解決類（10題）

Q1: 安裝程式要求網路但網卡偵測不到怎麼辦？
- A簡: 避免 Net Install、改用完整映像；或載入對應韌體、改用 USB 有線網卡。
- A詳: 問題症狀描述
  - 安裝器停在網路設定，無法列出網卡或取得 DHCP。
  可能原因分析
  - 無對應驅動/韌體、使用 netboot 影像、USB 工具製作錯誤。
  解決步驟
  - 用完整安裝映像，dd/raw 製作 USB；嘗試移除問題 Wi-Fi；改接 USB LAN。
  - 若需韌體，於第二支 USB 放 firmware，安裝時載入。
  預防措施
  - 先以 Live 檢查硬體；選擇對硬體友善版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q2, C-Q3

Q2: 安裝出現「CDROM 內容不對」如何排查？
- A簡: 重做 USB（dd/raw）、驗證 SHA256/GPG、確認 UEFI/BIOS 模式一致與正確啟動項目。
- A詳: 問題症狀描述
  - 安裝器報來源不正確或找不到套件。
  可能原因分析
  - USB 製作工具破壞引導/檔案結構、ISO 損壞、掛載錯誤。
  解決步驟
  - 重新下載驗證；以 dd/raw 重寫；改用不同 USB 埠；切換 UEFI/Legacy。
  預防措施
  - 一律驗證校驗碼與簽章；保留備援安裝媒體。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q5, C-Q2

Q3: Ubuntu Desktop Live 進桌面就卡住怎麼處理？
- A簡: 嘗試 nomodeset、安全圖形模式；或改用 Server 版再裝最小組件。
- A詳: 問題症狀描述
  - 進桌面黑屏/不動、滑鼠鍵盤無反應。
  可能原因分析
  - 顯卡驅動/KMS 問題、舊 GPU 與新版堆疊不相容。
  解決步驟
  - GRUB 參數加 nomodeset；安全圖形模式；或改以 Server 版安裝。
  預防措施
  - 安裝前查硬體相容性；保留替代顯卡或走無頭 SSH。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, A-Q24, C-Q1

Q4: 安裝後 SSH 連不上怎麼辦？
- A簡: 檢查服務狀態、防火牆、網路與認證設定；查看日誌排查錯誤。
- A詳: 問題症狀描述
  - `ssh: connect to host ... port ...: Connection refused/timeout`
  可能原因分析
  - sshd 未啟動、防火牆阻擋、IP 錯誤、金鑰/設定錯誤。
  解決步驟
  - `systemctl status ssh`；開放 `ufw allow 22/tcp`；確認 IP/端口；檢查 `/etc/ssh/sshd_config`；查 `journalctl -u ssh`
  預防措施
  - 安裝時啟用 OpenSSH；使用 DHCP 保留或靜態 IP。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q8, C-Q4

Q5: 設定靜態 IP 後無法上網怎麼解？
- A簡: 檢查遮罩/閘道/DNS 是否正確，避免與 DHCP 衝突，確認路由表與連通性。
- A詳: 問題症狀描述
  - 可 ping 本機/區網，無法上網或解析 DNS。
  可能原因分析
  - 錯誤網段/閘道、DNS 未設、IP 衝突。
  解決步驟
  - 檢查 `/etc/network/interfaces` 或 netplan；`ip route`、`resolvectl status`；修正設定並重啟網路。
  預防措施
  - 使用路由器 DHCP 保留；規劃不重疊的靜態範圍。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q9, C-Q5

Q6: Samba 分享在 Windows 看不到或無法存取？
- A簡: 確認 smbd 運行、共享配置與權限、開放 445 埠，使用正確帳密與 SMB 版本。
- A詳: 問題症狀描述
  - 網路上看不到主機、或存取提示拒絕。
  可能原因分析
  - 探索協議受限、共享未定義或權限錯誤、防火牆阻擋。
  解決步驟
  - `systemctl status smbd`；檢查 smb.conf；`testparm`；開放防火牆；在 Windows 直接輸入 `\\host\share`，使用 `smbpasswd` 建帳戶。
  預防措施
  - 固定主機名與靜態 IP；禁用 SMB1 的同時提供 DNS 與直接連線指引。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q22, C-Q6

Q7: Docker 在 1GB RAM 上效能不佳怎麼辦？
- A簡: 限制容器資源、使用輕量映像、禁用不必要服務、啟用 swap 並監控。
- A詳: 問題症狀描述
  - 容器啟動慢、OOM Killed、系統變慢。
  可能原因分析
  - 記憶體不足、映像過重、過多容器。
  解決步驟
  - `--memory` 限制；改用 Alpine/Distroless；減少容器；調整 swappiness；關閉不必要 daemon。
  預防措施
  - 規劃資源預算；將重服務外部化；使用監控告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q30, B-Q19, C-Q7

Q8: 反向代理出現 502 Bad Gateway 如何排查？
- A簡: 檢查上游服務狀態/埠、代理設定、健康檢查與超時，查看 Nginx 與應用日誌。
- A詳: 問題症狀描述
  - 瀏覽器顯示 502，後端容器可能當機。
  可能原因分析
  - 上游未啟動、地址錯誤、超時過短、TLS/明文錯配。
  解決步驟
  - 確認 `curl 127.0.0.1:5000`；修正 `proxy_pass`；增加 `proxy_read_timeout`；檢查容器日誌。
  預防措施
  - 健康檢查、重啟策略、啟用監控與告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q13, C-Q9

Q9: 開機 USB 無法啟動或變成 Net Install？
- A簡: 使用 dd/raw 重製，確認下載完整、選擇正確啟動項、關閉舊 USB 相容模式。
- A詳: 啀題症狀描述
  - 無法從 USB 開機或進入 Netboot/要求網路。
  可能原因分析
  - 製作工具/模式錯誤、BIOS 設定、映像為 netboot。
  解決步驟
  - 重做 dd；更新 BIOS；切換 UEFI/Legacy；用完整映像。
  預防措施
  - 永遠驗證校驗；保留兩種啟動模式媒體。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q6, C-Q2

Q10: 安裝卡在硬體偵測（Wi-Fi/顯示）怎麼辦？
- A簡: 拔除可疑硬體、黑名單模組、使用 nomodeset、安全圖形或改 Server 安裝。
- A詳: 問題症狀描述
  - 安裝過程長時間停滯或黑屏。
  可能原因分析
  - 問題驅動/韌體、IRQ 衝突、圖形堆疊不相容。
  解決步驟
  - 物理移除或在 kernel 參數加 `modprobe.blacklist=<driver>`；nomodeset；Server 版；安裝後更新 firmware。
  預防措施
  - 先以 Live 測試；準備 USB LAN 與第二顯示輸出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q3, B-Q21


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q2: 什麼是 Docker？它解決了什麼問題？
    - A-Q3: 什麼是 Ubuntu Server？與 Ubuntu Desktop 有何不同？
    - A-Q5: 什麼是 Reverse Proxy（反向代理）？適用情境為何？
    - A-Q6: 什麼是 ASP.NET 5（現 .NET 7/8 的前身）？為何可在 Linux 上跑？
    - A-Q7: 用舊筆電當家用伺服器的優點是什麼？
    - A-Q8: 為何在 NAS 上使用 Docker？
    - A-Q11: 製作開機 USB 的工具為何重要？
    - A-Q12: 為何伺服器建議設靜態 IP？
    - A-Q13: 什麼是 SSH Server？為何首要安裝？
    - A-Q14: 什麼是 Samba？與 NFS 有何差異？
    - A-Q24: Ubuntu Desktop 與 Server 在安裝體驗的差異？
    - C-Q2: 如何正確製作 Ubuntu 可開機 USB？
    - C-Q4: Ubuntu 安裝後如何設定 SSH 伺服器？
    - C-Q5: 如何在 Ubuntu 15.10 設定靜態 IP？
    - D-Q4: 安裝後 SSH 連不上怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q4: Ubuntu LTS 與非 LTS（如 15.10）有何差異？
    - A-Q10: 什麼是 Net Install？何時會被要求使用？
    - A-Q16: 安裝時出現「CDROM 內容不對」代表什麼？
    - A-Q25: 為何選擇 Ubuntu 15.10 解決安裝問題？
    - A-Q28: 家庭環境導入反向代理的核心價值？
    - A-Q29: 24 小時常開主機的安全重點有哪些？
    - A-Q30: 低階 CPU 與 1GB RAM 對 Docker 部署的限制？
    - B-Q1: Ubuntu 安裝流程如何運作？
    - B-Q6: USB 製作工具差異的技術面？
    - B-Q7: 為何新版 Ubuntu 對硬體支援更好？
    - B-Q8: SSH 的運作機制是什麼？
    - B-Q9: 靜態 IP 設定在網路中的原理？
    - B-Q10: Samba/SMB 的協議與元件？
    - B-Q13: Reverse Proxy 的工作機制？
    - B-Q18: ASP.NET 在 Linux 的運作與代理整合？
    - C-Q6: 如何安裝並設定 Samba 分享資料夾？
    - C-Q7: 如何在 Ubuntu 15.10 安裝 Docker？
    - C-Q9: 如何設定 Nginx 反向代理至 Docker 內的 ASP.NET？
    - D-Q2: 安裝出現「CDROM 內容不對」如何排查？
    - D-Q8: 反向代理出現 502 Bad Gateway 如何排查？

- 高級者：建議關注哪 15 題
    - B-Q3: Linux 如何偵測並載入網路卡驅動？
    - B-Q4: 為何移除 Wi-Fi 卡可繞過安裝卡住？
    - B-Q11: Docker 的核心技術原理？
    - B-Q12: Hyper-V 的虛擬化架構？
    - B-Q15: Linux 的開機流程與常見卡關點？
    - B-Q16: MD5/SHA 校驗與簽章的原理與限制？
    - B-Q17: Linux 韌體（firmware）載入的流程？
    - B-Q19: Docker 在 NAS/低資源裝置的資源隔離？
    - B-Q20: 筆電電池作為 UPS 的保護機制？
    - B-Q21: 桌面環境啟動（X/Wayland）為何會卡死？
    - C-Q8: 如何用 Docker 部署 ASP.NET 範例服務？
    - C-Q10: 如何將舊筆電優化為 24/7 低功耗伺服器？
    - D-Q1: 安裝程式要求網路但網卡偵測不到怎麼辦？
    - D-Q7: Docker 在 1GB RAM 上效能不佳怎麼辦？
    - D-Q10: 安裝卡在硬體偵測（Wi-Fi/顯示）怎麼辦？