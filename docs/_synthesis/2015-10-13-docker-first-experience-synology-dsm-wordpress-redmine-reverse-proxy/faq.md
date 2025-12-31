---
layout: synthesis
title: "Docker 初體驗 - Synology DSM 上面架設 WordPress / Redmine / Reverse Proxy"
synthesis_type: faq
source_post: /2015/10/13/docker-first-experience-synology-dsm-wordpress-redmine-reverse-proxy/
redirect_from:
  - /2015/10/13/docker-first-experience-synology-dsm-wordpress-redmine-reverse-proxy/faq/
postid: 2015-10-13-docker-first-experience-synology-dsm-wordpress-redmine-reverse-proxy
---

# Docker 初體驗 - Synology DSM 上面架設 WordPress / Redmine / Reverse Proxy

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Docker？
- A簡: Docker 是一種容器化技術，提供輕量、可移植、快速啟動的應用執行環境，不需要虛擬整個作業系統。
- A詳: Docker 是基於作業系統層級的虛擬化技術（容器化），透過映像檔（Image）與容器（Container）分離「建置」與「執行」兩個階段。容器共享宿主機核心，省略虛擬機器的完整 OS 開銷，因此啟動快、資源使用低、部署一致性高。它用於打包應用及其依賴，確保「在任何地方跑起來都一樣」，特別適合 NAS、雲端、CI/CD、微服務與個人自架站。與傳統 VM 相比（見 A-Q2），容器更輕巧，較符合個人或小型環境的硬體資源限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, A-Q15, B-Q9

A-Q2: Docker 與傳統 VM 有何差異？
- A簡: Docker 共用主機核心、啟動快、資源占用少；VM 需完整虛擬硬體與 OS，啟動慢、較耗資源。
- A詳: 傳統虛擬機（VM）透過 Hypervisor 虛擬硬體，來執行完整 OS，再在 OS 上跑應用；Docker 容器直接共用宿主機核心，僅隔離檔案系統、網路、行程與資源配額。結果是：容器啟動秒級、映像檔小、密度高、遷移容易；VM 更隔離、相容性廣，但啟動慢、資源開銷大。家用 NAS 資源有限，容器的高效率更適合在 DSM 上部署 WordPress/Redmine 等服務（見 A-Q3、A-Q16），也容易做反向代理整合（見 A-Q10）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, A-Q15

A-Q3: 為什麼在 Synology DSM 上使用 Docker？
- A簡: DSM 搭配 Docker 可快速部署多服務、資源占用低、管理統一、遷移容易，解決套件中心選擇少與更新慢的問題。
- A詳: DSM 的套件中心雖然便利，但更新節奏與選擇有限；Docker Hub 上則有大量官方/社群映像，能快速建立 WordPress、Redmine、MySQL 等常見服務。容器的輕量特性特別適合資源有限的 NAS；DSM 的 Docker 管理員提供 CPU/RAM/磁碟掛載、Port 映射等統一管理。以反向代理整合（見 A-Q10、C-Q4）更能在 Port 80（被 DSM 佔用）下，對外發布多個服務與網域。後續遷移到雲端也順暢（見 A-Q16），因此在 DSM 上用 Docker 具彈性與長期維護優勢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, A-Q22, B-Q8

A-Q4: 什麼是 Synology DSM？
- A簡: DSM 是 Synology NAS 的作業系統與管理介面，提供檔案、網頁、資料庫與套件管理等功能。
- A詳: DiskStation Manager（DSM）是 Synology 的 NAS 作業系統，提供圖形化管理介面與套件中心。用戶可透過 Web Station 架設網站、建立虛擬主機、管理反向代理；也可安裝 Docker 套件部署容器化服務。DSM 預設佔用 80/443 等服務 Port（見 A-Q12），故常需以反向代理與虛擬主機結合，將不同容器後端服務以不同網域對外發布（見 C-Q3、C-Q9）。DSM 的設計偏簡化，某些手動調整（如 vhost 檔案）會被介面覆蓋（見 A-Q19、D-Q3）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q3, D-Q3

A-Q5: 什麼是 Docker Image 與 Container？
- A簡: Image 是唯讀模板，包含執行所需的檔案與設定；Container 是 Image 的執行實例，可多個與獨立。
- A詳: Image（映像檔）是建置好的應用快照，包含檔案系統與相依套件，通常分層組成並可從 Docker Hub 下載；Container（容器）是執行該 Image 的實例，有自己的可寫層、網路命名空間與資源限制。可同一 Image 同時跑多個容器，各自獨立、相互隔離。對 DSM 而言，選對 Image（建議官方優先，見 A-Q14）再啟動 Container，進行 Port 映射、Volume 掛載（見 A-Q23、C-Q1），即可快速布署 WordPress+MySQL 或 Redmine 等服務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q14, A-Q23

A-Q6: Docker Hub 是什麼？為何重要？
- A簡: Docker Hub 是公共映像倉庫，提供官方與社群維護的映像，讓部署常見應用變得即取即用。
- A詳: Docker Hub 是最常用的映像倉庫，聚集了官方與社群維護的眾多 Image，例如官方 MySQL、社群 Nginx+PHP-FPM WordPress 等。其價值在於豐富選擇、快速布署、版本標記與更新追蹤；但社群品質不一，需評估來源可信度、維護活躍度與安全性（見 A-Q14）。在 DSM 上，Hub 讓你不受限於套件中心，直接挑選合適 Image 建構多個服務，配合反向代理對外發布（見 C-Q2、C-Q4）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q1, C-Q2

A-Q7: 什麼是 Nginx？與 Apache 有何差異？
- A簡: Nginx 是輕量高效的 Web 伺服器，事件驅動、資源占用低；Apache 模組豐富、相容性高但相對較重。
- A詳: Nginx 採事件驅動與非同步 I/O，適合處理高併發與靜態檔案；常與 PHP-FPM 分工處理 PHP。Apache 採多程序/執行緒模型，模組豐富（如 mod_proxy），設定彈性高。家庭 NAS 資源有限，Nginx 較省記憶體與 CPU（見 A-Q15），適合作為 WordPress 前端（C-Q2）；但 DSM 內建 Apache + Web Station 在反向代理與虛擬主機上則更整合（C-Q3、C-Q4）。實務上可用 Apache 做 Reverse Proxy，後端容器使用 Nginx+PHP-FPM 跑 WordPress。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q7, C-Q2, C-Q4

A-Q8: 什麼是 PHP-FPM？為何與 Nginx 搭配？
- A簡: PHP-FPM 是管理 PHP FastCGI 程序的服務，將 PHP 執行與 Web 伺服器分離，利於效能與資源控制。
- A詳: PHP-FPM（FastCGI Process Manager）負責管理 PHP Worker（數量、生命週期、重啟），以 FastCGI 協定讓 Nginx 將 .php 請求轉交給 PHP 處理。這種分離式架構比 Apache mod_php 更省資源、可細緻調教（如 pm、max_children），在輕量的 NAS 上尤其合適。WordPress 常以 Nginx+PHP-FPM 組合部署（見 C-Q2），具備良好效能與穩定性，亦便於容器化與擴展。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q2, D-Q10

A-Q9: 什麼是 WordPress？與 BlogEngine 有何差異？
- A簡: WordPress 是最普及的 PHP 部落格/CMS，生態龐大；BlogEngine 多為 .NET/Windows 環境，生態較小。
- A詳: WordPress 是開源 CMS，以 PHP+MySQL 為基礎，擁有海量主題、外掛、文件與社群支援，部署環境廣泛（Linux/Nginx/Apache）。BlogEngine.NET 使用 .NET 技術，偏向 Windows/IIS，擴充與主機選擇相對少。本文將 BlogEngine 資料轉移到 WordPress，搭配 Docker（A-Q1）部署於 DSM 上，透過反向代理（A-Q10）對外發布，既利用 NAS 資源也保有擴展性與可攜性（A-Q16）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, A-Q16

A-Q10: 什麼是 Reverse Proxy？與 Forward Proxy 差異？
- A簡: Reverse Proxy 代表內部服務對外，轉發外部用戶請求；Forward Proxy 代表用戶對外存取網路。
- A詳: Reverse Proxy 位於伺服器側，接收外部請求，基於路徑/網域/埠轉發至內部服務，再將回應返回用戶；常用於多站點發布、SSL 終結、快取、負載均衡與內部服務保護。Forward Proxy 位於客戶端側，代理用戶存取外部網路（如公司 Proxy）。在 DSM 上，因 80 Port 常被系統佔用（A-Q12），借由 Apache 的反向代理模組（B-Q2）可將多個容器綁定不同網域對外發布（C-Q4、C-Q9）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, C-Q4

A-Q11: 為什麼家庭 NAS 環境適合用 Reverse Proxy？
- A簡: 它可在單一 80/443 對外埠下，發布多個內部容器服務，簡化路由與管理，避免端口衝突。
- A詳: 家庭/小型環境中，路由器通常只對外開放少數固定埠（80/443），且 DSM 自身也佔用 80/443。Reverse Proxy 能將外部同一埠的不同網域/路徑，轉發到內部不同容器（WordPress、Redmine、WebSVN 等），避免多服務搶同埠問題（A-Q12、A-Q17）。同時可集中處理 SSL、Header 安全與快取，簡化管理。若併用內外 DNS（A-Q21），也能優化內網訪問路徑與體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q9, B-Q1

A-Q12: 為何 80 Port 常被佔用？如何面對？
- A簡: DSM 內建 Web/管理服務佔用 80，無法直接映射容器。可用反向代理與虛擬主機統一對外。
- A詳: DSM 啟用 Web Station/管理介面時，會佔用 80（與可能的 443）；因此在 Docker 中無法再直接把多個服務映射到 80。解法是：將容器各自映射到不同內部埠（如 8012），由 DSM 的 Apache 反向代理將外部 80 請求導向相對應後端（C-Q4）。此法同時解決多服務與同埠衝突（A-Q17），亦集中 SSL 與安全控制（A-Q25）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q4, A-Q17

A-Q13: 什麼是 Virtual Host？在 DSM Web Station 有何角色？
- A簡: 虛擬主機用於同一伺服器服務多個網域或站點。DSM Web Station 提供圖形化建立與管理。
- A詳: 虛擬主機（Virtual Host）讓同一 IP/埠透過 Hostname（或路徑）對應不同網站根目錄或代理規則。DSM Web Station 可建立綁定特定網域的 VHost（C-Q3），搭配 Apache 模組（mod_proxy）將該網域的外部請求反向代理到內部容器（C-Q4）。此機制是多站點整合的基礎，亦與 DNS 設定緊密相關（A-Q20、A-Q21）。注意：Web Station 介面調整可能覆蓋手動編輯的 vhost 檔（D-Q3）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, C-Q4, D-Q3

A-Q14: 為什麼優先選用官方映像？社群映像風險？
- A簡: 官方映像維護穩定、更新可期；社群映像品質參差，需評估維護狀態與安全。
- A詳: 官方映像（如 MySQL）通常有明確版本策略、安全修補與文件；社群映像（如特定 Nginx+WordPress）雖提供便利整合，但需檢視 Dockerfile、維護頻率、下載數與 Issue 狀態。本文實務中也曾遇官方 WordPress 映像在 DSM 上開 terminal 導致崩潰（D-Q1），改採穩定的 Nginx+PHP-FPM 組合映像解決（C-Q2）。因此建議：後端核心服務選官方；前端整合映像需評估可信度與是否易於自行維護。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q2, D-Q1

A-Q15: Docker 在 NAS 上的資源優勢是什麼？
- A簡: 容器共享核心、啟動快、密度高，可在有限 CPU/RAM 的 NAS 上同時運行多服務。
- A詳: NAS 硬體資源通常有限（CPU 低耗能、RAM 較小）。Docker 容器化讓每個服務只攜帶必要依賴，避免完整 OS 的額外負擔；DSM Docker 管理員可設定 CPU/記憶體限制（B-Q8）與磁碟掛載，提升穩定性。相較 VM，容器更適合跑多個站點（WordPress、Redmine、WebSVN）並以反向代理統一發布（A-Q11）。如遇性能瓶頸，再評估 RAM 擴充或服務分拆到外部雲端（A-Q16）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q10, A-Q3

A-Q16: 為什麼不用 DSM 套件中心的 WordPress？缺點？
- A簡: 套件中心版受限安裝路徑、URL 帶子目錄、僅能單實例、遷移困難，彈性低於 Docker。
- A詳: DSM 套件版 WordPress 通常部署在特定目錄（URL 會多一段，如 /wordpress），對 SEO 與連結相容性不利；亦不易同時安裝多份站點，且資料遷移至雲端或他處較複雜。Docker 則可多實例、自由映射 Port/Volume、統一管理與易於遷移（匯出/匯入映像與資料卷）。透過反向代理，每個站點可有獨立網域與根路徑（C-Q9），更符合長期維護與擴展需求。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q2, C-Q9

A-Q17: 為何無法讓多個容器都映射到 80？
- A簡: 一個埠一次只能被一個程序綁定。需以 Reverse Proxy 在 80 接入，再分流至不同後端容器。
- A詳: TCP 埠由單一程序獨占（除非 SO_REUSEPORT 等特殊配置，且仍需進程協作）。因此多容器直接綁定 80 不可行。解法：後端容器各自對內綁定不同埠（如 8012、8020），DSM 的 Apache 在 80 接收請求，按 Hostname/路徑將請求 Proxy 到對應後端（C-Q4、C-Q9）。此模式同時適用於 443（SSL），集中處理安全與快取（A-Q25）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q4, C-Q9

A-Q18: ProxyPreserveHost、ProxyPass、ProxyPassReverse 分別是什麼？
- A簡: 它們是 Apache 反向代理設定：保留原始 Host、設定代理目標、修正回應中重寫用的 URL。
- A詳: ProxyPreserveHost On 會將用戶的原始 Host header 傳給後端，利於 WordPress 等依 Host 判斷 URL；ProxyPass 定義請求應被轉發到哪個後端（如 http://nas:8012/）；ProxyPassReverse 會重寫後端回應中的 Location/Content-Location/URI，讓用戶端看到的仍是外部網域與路徑。三者搭配確保代理透明，避免重導向或資源連結錯亂（D-Q5）。設定細節見 C-Q4、B-Q4。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q4, C-Q4, D-Q5

A-Q19: 為何要備份 httpd-vhost.conf-user？
- A簡: DSM Web Station 介面調整虛擬主機時，可能覆蓋手動加入的代理設定，需備份以便還原。
- A詳: DSM 為簡化管理，會以圖形介面設定生成 Apache vhost 檔。當你於 /etc/httpd/httpd-vhost.conf-user 手動加入代理區塊後，若再透過 Web Station 修改虛擬主機或新建站點，系統可能重寫該檔，導致先前代理規則消失。建議：修改前備份；變更後比對差異再合併；或採用 Include 外部檔的方式降低覆蓋風險（若環境允許）。若遭覆蓋，依備份快速還原（D-Q3）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q3, C-Q4

A-Q20: 什麼是 DNS A 記錄與 CNAME？本文如何使用？
- A簡: A 將網域指向 IP；CNAME 將網域別名指向另一網域。外網用 A 或 CNAME，內網可設本地 DNS 直接到 NAS。
- A詳: 對外 DNS：若有固定 IP，將主網域或子網域設 A 記錄到你的對外 IP；若使用動態 DNS，對外可用 CNAME 指到 DDNS 提供的網域。對內 DNS（路由器內建或本地 DNS）：加靜態紀錄，讓相同網域解析為 NAS 內部 IP，避免「出國再回來」（省延遲）。此內外分工讓你在手機 4G 與家中 Wi-Fi 都能順暢存取（B-Q12，C-Q7）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, B-Q12, D-Q7

A-Q21: 什麼是內網 DNS 與外網 DNS 分工？
- A簡: 外網 DNS 解析到路由器對外 IP；內網 DNS 指向 NAS 內部 IP，優化內網訪問與穩定性。
- A詳: 外網 DNS 為公開解析，服務全球用戶；內網 DNS 為家庭/辦公室自有解析，服務內網設備。將相同網域在外網指向對外 IP，在內網指向 NAS 內部 IP，可避免 NAT 迴圈限制、降低延遲、提升可用性。若路由器不支援本地 DNS，可考慮 hosts 或支援 hairpin NAT（B-Q12）。本文採「外 A/CNAME、內靜態 DNS」模式（C-Q7）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q12, D-Q7

A-Q22: 什麼是 Port Mapping？在 DSM Docker 如何使用？
- A簡: 將容器內部埠映射到宿主機埠，供外部或本機訪問；DSM Docker 介面可設定對應。
- A詳: 容器內應用通常聆聽在固定埠（如 80/9000）。透過 Port Mapping，可將宿主機某埠（如 8012）轉送到容器埠（80），使宿主或外部能透過該埠存取服務。DSM Docker UI 提供簡易映射設定。考量 DSM 已佔用 80/443，應避免與系統衝突，並搭配反向代理在外部統一使用 80/443（A-Q12、C-Q2、C-Q4）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q4, D-Q2

A-Q23: 什麼是資料持久化（Volume）？對 WordPress/MySQL 有何重要性？
- A簡: 將容器資料路徑映射到 NAS 儲存空間，確保更新/重建容器不丟資料，是生產部署關鍵。
- A詳: 容器的可寫層是短暫的，刪除容器即失。因此需將應用資料（如 WordPress wp-content、上傳檔、Nginx conf、MySQL 資料目錄）映射到宿主 NAS 路徑或命名 Volume。如此無論更新映像或重建容器，資料仍保留。DSM Docker 提供資料夾掛載管理；也可做快照與備份。未持久化常導致升級或誤操作後資料遺失（D-Q9）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, D-Q9

A-Q24: 什麼是 Load Balancer？與 Reverse Proxy 關係？
- A簡: 負載均衡在多後端間分流流量；Reverse Proxy 常兼具此功能，用於擴展與高可用。
- A詳: 負載均衡器可依輪詢、最少連線等策略，將請求分配至多個後端節點，並進行健康檢查。許多 Reverse Proxy（如 Nginx、HAProxy、Apache mod_proxy_balancer）內建此能力。在 DSM 家用場景，通常單一後端已足夠；若將來要擴展 WordPress 多實例或分離靜態/動態，可於反向代理層加入簡單的 LB 規則（B-Q18）。但需留意持久性連線、Session 與快取一致性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q18, C-Q9, D-Q6

A-Q25: 為何常在 Reverse Proxy 上做 HTTPS 終結？
- A簡: 集中 SSL 憑證與 TLS 設定，簡化後端服務，提升管理性與安全一致性。
- A詳: 將 TLS 終結在反向代理上，可用單一位置管理憑證、啟用 HSTS/安全標頭，並減少後端容器的憑證部署與更新負擔。後端以 HTTP 溝通，降低複雜度與資源開銷。若未來加入多服務或換機，僅需在代理層處理 SSL（B-Q21）。DSM 也有憑證管理工具，可搭配虛擬主機使用。注意：內網連線若有安全需求，可維持端到端加密，但成本較高。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q21, C-Q4, C-Q9

A-Q26: 什麼是 ARR？在 Windows IIS 的 Reverse Proxy 方案？
- A簡: IIS 的 Application Request Routing 模組，提供反向代理、負載均衡與快取功能。
- A詳: ARR 是微軟為 IIS 提供的擴充，能將 IIS 作為反向代理層，支援 URL Rewrite、健康檢查、負載均衡與快取。對於 Windows Server 用戶，ARR 是常見方案。本文則在 DSM（Linux/Apache）環境下，採用 Apache mod_proxy 實作相同功能（B-Q2、C-Q4）。若將來容器搬遷到 Windows/雲端 IIS 環境，ARR 有助延續既有反向代理架構與管理習慣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q2, C-Q4

A-Q27: 為什麼容器啟動快？
- A簡: 容器共用宿主核心、僅載入應用與依賴，省去 OS 開機流程，通常數秒即就緒。
- A詳: 容器不需 Hypervisor 與完整 OS，啟動時只建立命名空間、掛載檔系統層、啟動程序，故速度極快且資源負擔小。這讓在 NAS 上操作多服務與快速迭代非常實用（A-Q15）。同時，映像層可快取，拉取更新也較節省頻寬。需要注意的是首次拉取映像仍可能耗時（本文亦提及），建議選擇輕量映像與合理分層。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q9, C-Q2

A-Q28: NAS 作為 Personal Server 的核心價值是什麼？
- A簡: 集中化、低功耗、長時間運作，搭配 Docker 與反向代理，能承擔多站點與服務的穩定運行。
- A詳: NAS 天生設計為長時間穩定運作，具備 RAID/快照/備份能力、低耗能與靜音特性。結合 Docker，可在同一台設備上運行多個網站與工具（WordPress、Redmine、WebSVN、DB），以反向代理統一對外發布；集中管理憑證、安全與資源限制，維護成本低。當容量或性能不足時，再考慮擴 RAM 或將部分服務遷移至雲端，仍保留一致的容器化部署模式（A-Q16）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q11, C-Q9


### Q&A 類別 B: 技術原理類

B-Q1: 在 DSM 上，Reverse Proxy 從外網到容器的請求流程如何運作？
- A簡: 外部請求至 DSM:80 → 虛擬主機匹配 Host → Apache mod_proxy 轉發到容器內部埠 → 回應經 ProxyPassReverse 重寫返回。
- A詳: 原理說明：路由器將外部 80 轉發至 NAS；DSM 的 Apache 接收，根據虛擬主機 ServerName/Host header 決定站點；反向代理模組（mod_proxy、mod_proxy_http）將請求轉送至內部目標（如 http://nas:8012）。關鍵步驟：1) NameVirtualHost/VirtualHost 配對；2) ProxyPreserveHost 保留 Host；3) ProxyPass 設定後端；4) ProxyPassReverse 重寫回應中的 Location 等標頭與 URL。核心組件：Apache、mod_proxy、Docker 容器中的 Web（Nginx/PHP-FPM）。此流程讓多個容器可共享外部 80/443（參見 C-Q4、C-Q9）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q13, C-Q4

B-Q2: Apache 的 mod_proxy 與 mod_proxy_http 背後機制是什麼？
- A簡: mod_proxy 提供通用代理框架；mod_proxy_http 以 HTTP 協定轉發請求，支援 Header 重寫與連線管理。
- A詳: 技術原理：mod_proxy 是 Apache 的代理核心，透過子模組支援各種協定（http、ajp、fcgi 等）。mod_proxy_http 實作 HTTP/1.1 轉發，處理連線重用、Chunked 傳輸、Keep-Alive、標頭過濾與重寫。關鍵流程：1) 代理前置檢查與 ACL（ProxyRequests Off）；2) 上游連線建立（連接容器）；3) 轉送請求與回應；4) ProxyPassReverse 重寫回應標頭。核心組件：Apache 主程序、代理模組、後端 Web。搭配虛擬主機可實現多站點分流（B-Q1）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q4, D-Q6

B-Q3: DSM 的 Web Station 與 httpd-vhost.conf-user 如何互動？
- A簡: Web Station 以圖形介面生成與更新 vhost 檔；手動編輯可能在介面變更時被覆蓋。
- A詳: 原理說明：DSM 管理虛擬主機的設定檔模板，使用者在 Web Station 調整站點時，系統會重寫 /etc/httpd/httpd-vhost.conf-user 等檔案。若你直接在該檔加入反向代理設定區塊，後續任何透過 UI 的變更都可能覆蓋掉。關鍵步驟：1) 先在 UI 建立 VHost（C-Q3）；2) 再 SSH 手工加入 proxy 區塊（C-Q4）；3) 變更前備份（C-Q8）；4) 覆蓋後人工合併。核心組件：DSM Web Station、Apache 設定檔。這是 DSM 易用性與可客製間的取捨（D-Q3）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, C-Q3, C-Q8

B-Q4: ProxyPass 與 ProxyPassReverse 如何協同處理 URL 與重導？
- A簡: ProxyPass 定義轉發目標；ProxyPassReverse 將後端回應中的重導 URL 改回外部網域與路徑。
- A詳: 原理說明：用戶請求 / 進來，ProxyPass http://nas:8012/ 轉送到後端。若後端回應 301/302 與 Location:http://backend/...，ProxyPassReverse 會將該 URL 重寫為 http://外部網域/...，避免用戶被導向內部位址或錯誤主機名。關鍵步驟：1) 設定對應路徑前綴；2) 開啟 ProxyPreserveHost 確保應用產生正確 URL；3) 測試多種重導情境。核心組件：mod_proxy_http、Header/Location。若不正確，見 D-Q5 的診斷與修正。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q4, D-Q5

B-Q5: DSM 上 Docker 網路在橋接模式下如何通訊？
- A簡: 預設 bridge 模式下，容器有私有 IP；透過宿主埠映射與主機名解析（如 nas）供外部訪問。
- A詳: 原理說明：Docker bridge 建立虛擬交換器，容器獲得內部 IP。外部訪問依賴宿主埠映射（宿主 8012→容器 80）。在 Apache 內部以 http://nas:8012 存取後端，需確保 nas 解析到宿主 IP（內網 DNS 或 hosts）。關鍵步驟：1) 設定 Port Mapping（C-Q2）；2) 在 vhost 使用可解析名稱或直接 IP；3) 測試連線。核心組件：Docker bridge、NAT、DSM 主機名解析。若解析錯誤，會導致 502/連線失敗（D-Q6）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q4, D-Q6

B-Q6: WordPress 與 MySQL 容器的連線機制是什麼？
- A簡: WordPress 透過 DB 主機、帳密、資料庫名環境變數連向 MySQL；DSM UI 需手動填寫並確保容器互通。
- A詳: 原理說明：WordPress 需 DB_HOST/DB_NAME/DB_USER/DB_PASSWORD 等設定，連線至 MySQL 容器。DSM UI 沒有 docker-compose 連結語法，通常以宿主 IP + MySQL 暴露的埠（如 3306 或對外映射）連線，或採用 bridge 同網段路由。關鍵步驟：1) 啟 MySQL 容器（C-Q1）；2) 設定安全帳密；3) 啟 WordPress 容器（C-Q2），以 DB_HOST 指向 MySQL；4) 測試安裝流程。核心組件：環境變數、網路路由、權限。常見錯誤見 D-Q8。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, D-Q8

B-Q7: Nginx + PHP-FPM 的請求處理流程？
- A簡: Nginx 接收 HTTP→靜態檔直接回→動態 .php 交給 PHP-FPM→FPM 回應給 Nginx→傳回用戶。
- A詳: 原理說明：Nginx 按 location 規則區分靜/動內容。靜態檔案直接讀取並回傳；.php 請求透過 FastCGI 協定傳給 PHP-FPM。PHP-FPM 管理 Worker（數量、超時），執行 PHP 應用（如 WordPress）產生回應，回交給 Nginx。關鍵步驟：1) FastCGI 參數（SCRIPT_FILENAME、DOCUMENT_ROOT）；2) 缓存與壓縮；3) 安全性限制。核心組件：Nginx、PHP-FPM、WordPress。此架構在容器中資源效率高（A-Q8）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, C-Q2

B-Q8: DSM Docker 管理的資源限制如何生效？
- A簡: DSM 設定的 CPU/記憶體等限制，透過 cgroups/namespace 套用到容器，控制資源占用。
- A詳: 原理說明：Docker 利用 Linux cgroups 設定 CPU shares、memory limits、blkio 等；namespace 隔離 PID、NET、MNT、UTS。DSM Docker UI 的限制設定會轉化為對應 Docker 參數，落地於 cgroups。關鍵步驟：1) 評估服務資源需求；2) 設定限制避免互相影響；3) 監控利用率。核心組件：Docker Engine、Linux cgroups。對 NAS 很重要，確保多服務共存與穩定（A-Q15、D-Q10）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, D-Q10, C-Q2

B-Q9: 映像下載與容器建立的生命週期為何？
- A簡: 拉取映像→建立容器（設定環境、映射）→啟動→運行→停止→刪除；資料應由 Volume 持久化。
- A詳: 原理說明：首次使用需從託管倉庫拉取映像（可能較耗時）；建立容器時指定環境變數、Port、Volume；啟動後即提供服務；停止不刪除資料卷；刪除容器不影響已綁定的 Volume。關鍵步驟：1) 確認映像來源與版本；2) 設定 Volume（A-Q23）；3) 啟動順序（先 DB、後 App）；4) 備份與升級策略。核心組件：Image、Container、Volume、Registry。DSM UI 具象化上述流程（C-Q1、C-Q2）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q23, C-Q1

B-Q10: 在 DSM 上執行 httpd -k restart 代表什麼？
- A簡: 透過 Apache 控制指令，優雅重啟主程序，使配置變更生效並儘量不中斷現有連線。
- A詳: 原理說明：httpd -k restart 會讓 Apache 主程序重讀設定檔，重啟子程序。優雅重啟盡量保留現有連線，避免長時間中斷。關鍵步驟：1) 完成 vhost/proxy 設定；2) 檢查語法（若可用 httpd -t）；3) 重啟；4) 驗證站點。核心組件：Apache 主程序、設定檔。DSM 環境下請注意權限與命令位置。若重啟後無效或報錯，檢查語法與錯誤日誌（D-Q6）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, D-Q6, D-Q4

B-Q11: NameVirtualHost 與 ServerName 的匹配機制是什麼？
- A簡: NameVirtualHost 指定名稱型虛擬主機綁定埠；ServerName/ServerAlias 與 Host header 比對以選站點。
- A詳: 原理說明：在 Apache 2.2 時代使用 NameVirtualHost；2.4 起不再需要。虛擬主機依請求中的 Host header 與各 VirtualHost 的 ServerName/ServerAlias 比對選擇目標，若無匹配則使用第一個宣告的預設站（可能是 DSM 預設 404）。關鍵步驟：1) 正確設定 ServerName；2) 確保 DNS 解析與 Host header 一致；3) 驗證預設站是否合理。核心組件：Apache vhost、DNS。若只看到 404，見 D-Q4 排查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q4, A-Q20

B-Q12: 內外網 DNS 與 NAT 迴圈（hairpin NAT）如何影響訪問？
- A簡: 若路由器不支援 hairpin NAT，內網以外部網域訪問會失敗；內部 DNS 可解決。
- A詳: 原理說明：Hairpin NAT 允許內網客戶端透過路由器的對外 IP 訪問內網服務。若不支援，內網設備無法用外部網域連回內部。解法是在內部 DNS 將網域直接解析到 NAS 內部 IP（A-Q21、C-Q7）。關鍵步驟：1) 測試內外解析差異；2) 設定內網 DNS 靜態紀錄；3) 驗證手機 4G/家中 Wi-Fi。核心組件：DNS、NAT、路由器能力。若訪問不一致，常見於 D-Q7 的現象。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q7, D-Q7

B-Q13: 多站點多容器的反向代理設計原理？
- A簡: 以不同網域/子網域對應不同後端容器，統一由 80/443 接入，按 Host header 分流。
- A詳: 原理說明：在 Apache 中為每個站點建立 VirtualHost，設定 ServerName 對應網域；各站內配置 ProxyPass 至對應容器。可擴展至 Redmine、WebSVN 等。關鍵步驟：1) DNS 準備；2) VHost 建立（C-Q3）；3) 代理規則（C-Q9）；4) 測試跨站連結。核心組件：Apache vhost、mod_proxy、容器服務。若需要 SSL，於代理層終結（A-Q25）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, A-Q11, A-Q25

B-Q14: 端口佔用與資源衝突如何被系統檢測？
- A簡: 綁定埠時若已被佔用會報錯；容器/Apache 啟動失敗或跳過綁定，需調整配置。
- A詳: 原理說明：當程序嘗試 bind() 已被佔用的埠，系統返回 EADDRINUSE 導致啟動失敗或功能受限。Docker Port Mapping 或 Apache 設定錯誤都可能觸發。關鍵步驟：1) 檢查埠使用情況（netstat/ss）；2) 避免和 DSM 系統埠衝突；3) 統一由代理層對外提供 80/443。核心組件：TCP/IP 栈、服務啟動腳本。見 D-Q2 的應對策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q2, C-Q2

B-Q15: 容器崩潰時如何收集診斷資訊？
- A簡: 查看 docker logs、檢查容器事件、資源限制、對應應用日誌，定位崩潰原因。
- A詳: 原理說明：Docker logs 蒐集容器 stdout/stderr；搭配 docker inspect/events、應用自身日誌（如 Nginx/WordPress）、系統 dmesg/cgroups OOM 訊息，綜合分析。關鍵步驟：1) 重現崩潰；2) 查看 logs；3) 檢查資源限制與映射；4) 嘗試替代映像或版本回退。核心組件：容器日誌、應用日誌、資源監控。本文曾遇官方 WordPress 映像在 DSM Terminal 觸發崩潰（D-Q1），改用穩定映像解決（C-Q2）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q1, B-Q8, C-Q2

B-Q16: Volume 映射與檔案權限的原理？
- A簡: Volume 將宿主目錄掛入容器；權限由宿主檔案系統與容器內 UID/GID 決定。
- A詳: 原理說明：Volume 映射時，容器內程序以其 UID/GID 讀寫宿主掛載的路徑；若宿主權限不匹配，會導致讀寫失敗。關鍵步驟：1) 選擇合適的宿主資料夾；2) 需要時調整宿主端目錄的權限/擁有者；3) 避免以 root 運行應用。核心組件：Linux 檔案權限、Docker Volume。權限錯誤常導致資料無法保存或應用異常（D-Q9）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q23, D-Q9, C-Q1

B-Q17: 使用 Nginx 作為 Reverse Proxy 與 Apache 有何原理層差異？
- A簡: Nginx 事件驅動、配置精簡；Apache 模組豐富、語法靈活。兩者都能勝任反向代理。
- A詳: 原理說明：Nginx 以非同步事件模型處理連線，低資源消耗；Apache 以 MPM（多程序/執行緒/事件）模型並透過模組擴展功能。反向代理方面，Nginx 用 proxy_pass；Apache 用 mod_proxy + ProxyPass。關鍵步驟：在 DSM 情境下，因 Web Station 整合 Apache，採用 Apache 實作代理較順暢（C-Q4）；若完全以容器提供反向代理，也可用 Nginx Proxy Manager 等方案（非本文範圍）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q4, A-Q25

B-Q18: Reverse Proxy 層的負載均衡策略有哪些？
- A簡: 常見有輪詢、最少連線、權重；需加上健康檢查與故障切換。
- A詳: 原理說明：反向代理可配置 upstream 多目標，策略包含 round-robin、least_conn、加權分配；搭配健康檢查自動摘除故障節點。關鍵步驟：1) 規劃多容器/多節點；2) 設定策略與檢查；3) 驗證 session/快取一致性。核心組件：代理模組、健康檢查、監控。家用場景通常不必，但擴展時可逐步導入（A-Q24）。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q24, C-Q9, D-Q6

B-Q19: Apache ErrorDocument 的錯誤頁面配置原理？
- A簡: 透過 ErrorDocument 將 403/404/500 等錯誤導向特定頁面，改善用戶體驗。
- A詳: 原理說明：在 vhost 中以 ErrorDocument 404 "/webdefault/error.html" 指定錯誤對應頁。當無匹配資源或權限問題時，Apache 將回應該頁。關鍵步驟：1) 指定對應檔案路徑；2) 確保權限與存在；3) 測試錯誤情境。核心組件：Apache 配置、錯誤處理。DSM 預設也提供基本 404 頁面，在虛擬主機準備完成前可能先看到（D-Q4）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q4

B-Q20: 手機 4G 測試與 Wi-Fi 測試路徑有何差異？
- A簡: 4G 經外部 DNS 與路由器公網入口；Wi-Fi 可能走內網 DNS 或 hairpin NAT，行為不同需分別驗證。
- A詳: 原理說明：4G 測試能驗證外部 DNS、ISP 路由、路由器 Port Forward 是否正常；Wi-Fi 測試則檢驗內網 DNS 與 hairpin NAT 能力。關鍵步驟：1) 先 4G 測試外部路徑；2) 再 Wi-Fi 測試內部解析；3) 確認兩者一致（A-Q21、B-Q12）。核心組件：DNS、NAT、Port Forward。本文亦以手機 4G 驗證站點可用性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q21, C-Q7, D-Q7

B-Q21: 反向代理的安全考量有哪些？
- A簡: 集中 TLS、限制來源、設定安全標頭、隱藏內部拓撲、過濾危險標頭，降低攻擊面。
- A詳: 原理說明：在代理層終結 TLS（A-Q25），可啟用 HSTS、TLS 版本限制與安全密碼套件；限制 ProxyRequests Off 防止開放代理；加上 X-Forwarded-Proto/Host 等標頭供後端判斷；設定安全標頭（X-Frame-Options、X-Content-Type-Options、Content-Security-Policy）。核心組件：Apache/Nginx 安全配置、憑證管理。家用站點雖風險較低，但仍建議最小曝露面與定期更新映像與套件。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q25, C-Q4, D-Q6

B-Q22: 反向代理對效能的影響與優化方向？
- A簡: 多一道轉發有微小開銷；透過快取、壓縮、連線重用與靜態資源優化可降低影響。
- A詳: 原理說明：代理層增加一次網路鏈路與處理，耗用 CPU/記憶體；但在 NAS 上通常開銷可控。優化：啟用 gzip/br 壓縮、靜態資源快取、Keep-Alive、合理超時；在後端使用 Nginx+PHP-FPM（B-Q7）提升動態處理效率。若瓶頸在硬體（RAM/CPU），可提升硬體或將部分服務外移（D-Q10）。監控日誌與資源占用以持續調整。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, D-Q10, C-Q2


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 DSM 上安裝 MySQL 官方映像並設定資料持久化？
- A簡: 下載 MySQL 官方映像，建立容器時設定帳密與 Volume 掛載資料目錄，確保資料持久化。
- A詳: 
  - 實作步驟:
    1) 在 DSM Docker 搜尋 mysql，選官方映像並下載。
    2) 建立容器，環境變數設定：MYSQL_ROOT_PASSWORD、MYSQL_DATABASE、MYSQL_USER、MYSQL_PASSWORD。
    3) Volume 掛載：將 /var/lib/mysql 映射到 NAS 資料夾（如 /volume1/docker/mysql）。
    4) 設定 Port 映射：主機 3306→容器 3306（可保留內部使用）。
  - 關鍵設定:
    - 環境變數與 Volume 掛載。
  - 程式碼/設定:
    ```
    MYSQL_DATABASE=wpdb
    MYSQL_USER=wpuser
    MYSQL_PASSWORD=strongpass
    MYSQL_ROOT_PASSWORD=strongrootpass
    ```
  - 注意/最佳實踐: 使用強密碼；限制外部 3306 暴露；定期備份資料夾。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, A-Q23, D-Q8

C-Q2: 如何以 Nginx+PHP-FPM 的 WordPress 映像部署前端並映射埠？
- A簡: 拉取 Nginx+WordPress 映像，建立容器時設定 DB 連線、Volume、將主機 8012 映射容器 80。
- A詳:
  - 實作步驟:
    1) 在 DSM Docker 搜尋並拉取 Nginx+PHP-FPM 的 WordPress 映像（如 amontaigu/wordpress）。
    2) 建立容器：環境變數設定 DB_HOST、DB_NAME、DB_USER、DB_PASSWORD 指向 C-Q1 的 MySQL。
    3) 掛載 Volume：/var/www/html（或映像文件指示的 wp-content 路徑）到 NAS 資料夾。
    4) Port 映射：主機 8012→容器 80。
  - 關鍵設定:
    ```
    DB_HOST=nas:3306
    DB_NAME=wpdb
    DB_USER=wpuser
    DB_PASSWORD=strongpass
    ```
  - 注意/最佳實踐: 確保 nas 能解析到宿主 IP；資料持久化；限制資源（B-Q8）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, A-Q22, D-Q1

C-Q3: 如何用 DSM Web Station 建立綁定網域的虛擬主機？
- A簡: 在 Web Station 新增虛擬主機，設定 Server Name 為你的網域並指向站點目錄，作為代理入口。
- A詳:
  - 實作步驟:
    1) 開啟 DSM 控制台→Web Station→虛擬主機→新增。
    2) 輸入網域（如 columns.chicken-house.net），選擇文件根目錄（可用空白占位目錄）。
    3) 套用後先以瀏覽器測試，應看到預設 404 頁。
  - 關鍵設定: ServerName 與文件根目錄。
  - 注意/最佳實踐: 僅作代理入口，稍後會以手動編輯加入代理規則（C-Q4）；UI 調整可能覆蓋手動設定（C-Q8）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q4, A-Q13

C-Q4: 如何在 Apache 加入 Reverse Proxy 設定並重啟生效？
- A簡: SSH 編輯 /etc/httpd/httpd-vhost.conf-user，於對應 VirtualHost 加入 ProxyPass 等，重啟 httpd。
- A詳:
  - 實作步驟:
    1) SSH 進 NAS，編輯 /etc/httpd/httpd-vhost.conf-user。
    2) 在對應 VirtualHost *:80 ServerName 為你的網域處加入：
       ```
       ProxyPreserveHost On
       ProxyRequests Off
       <Location />
         ProxyPass http://nas:8012/
         ProxyPassReverse http://columns.chicken-house.net/
         Order allow,deny
         Allow from all
       </Location>
       ```
    3) 執行 httpd -k restart。
    4) 瀏覽器測試網域。
  - 注意/最佳實踐: 確保 nas 可解析；ProxyPassReverse 需符合你的外部網域；備份檔案（C-Q8）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q4, A-Q18

C-Q5: 如何驗證 Reverse Proxy 是否正確？
- A簡: 以網域訪問應見 WordPress；檢查重導、資源 URL、Header 與 HTTP 狀態，確認無內部位址曝露。
- A詳:
  - 實作步驟:
    1) 用瀏覽器開啟 http://你的網域，確認頁面正常。
    2) 開發者工具檢查 Network：資源 URL 使用外部網域、HTTP 200/301 正常。
    3) 檢查回應 Header 的 Location 是否為外部網域。
  - 關鍵設定: ProxyPreserveHost、ProxyPassReverse。
  - 注意/最佳實踐: 若出現 404/502/循環重導，參考 D-Q4/D-Q6/D-Q5 排查；手機 4G 與 Wi-Fi 皆測試（B-Q20）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q5, D-Q6, B-Q20

C-Q6: 如何設定路由器 Port Forward 將 80 導向 NAS？
- A簡: 在路由器 NAT/Port Forwarding 將外部 TCP 80 映射到 NAS 內部 IP 的 80。
- A詳:
  - 實作步驟:
    1) 取得 NAS 內部固定 IP。
    2) 登入路由器，開啟 Port Forwarding，新增規則：WAN TCP 80→NAS IP:80。
    3) 若有 HTTPS，亦設定 443。
  - 關鍵設定: 靜態 DHCP 保留 NAS IP。
  - 注意/最佳實踐: 避免重複映射；確認 ISP 未封鎖 80；測試外部可達性（B-Q20）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q12, B-Q20

C-Q7: 如何設定內外 DNS 以優化存取？
- A簡: 外網 DNS 設 A 或 CNAME 到對外 IP/DDNS；內網路由器設靜態 DNS，將同網域指向 NAS 內部 IP。
- A詳:
  - 實作步驟:
    1) 外網 DNS：有固定 IP 設 A 記錄；否則用 CNAME 指到 DDNS。
    2) 內網 DNS：在路由器 DNS 服務加靜態紀錄，將你的網域解析到 NAS 內部 IP。
    3) 測試 4G（外網）和 Wi-Fi（內網）解析與存取。
  - 關鍵設定: A/CNAME 記錄、內網 DNS。
  - 注意/最佳實踐: 若路由器不支援本地 DNS，確認 hairpin NAT（B-Q12）或用 hosts 作替代。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, A-Q21, B-Q12

C-Q8: 如何備份並避免 vhost 設定被 DSM 覆蓋？
- A簡: 備份 vhost 檔，介面調整後以備份合併；可考慮 Include 外部檔，降低覆蓋風險。
- A詳:
  - 實作步驟:
    1) 複製 /etc/httpd/httpd-vhost.conf-user 為備份。
    2) 每次用 Web Station 調整虛擬主機後，檢查是否被覆蓋。
    3) 將 Proxy 區塊重新合併回檔案，重啟 httpd。
  - 關鍵設定: 備份管理、變更流程。
  - 注意/最佳實踐: 維持變更紀錄；大變更前先備份；考慮使用 Include 指向自訂檔（依 DSM 版本可行性）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q3, D-Q3

C-Q9: 如何同時對外發布多個容器（如 WordPress 與 Redmine）？
- A簡: 為每個網域建立虛擬主機，分別配置 ProxyPass 至相對容器埠，統一從 80/443 導入。
- A詳:
  - 實作步驟:
    1) 準備多個容器：WordPress 映射 8012、Redmine 映射 8020。
    2) 在 DSM 建立對應虛擬主機：blog.domain 與 redmine.domain。
    3) 在各 vhost 中加入：
       ```
       <Location />
         ProxyPass http://nas:8012/
         ProxyPassReverse http://blog.domain/
       </Location>
       <Location />
         ProxyPass http://nas:8020/
         ProxyPassReverse http://redmine.domain/
       </Location>
       ```
    4) 重啟 httpd、測試。
  - 注意/最佳實踐: DNS 準備、資源限制、SSL 集中於代理層（A-Q25）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, A-Q17, A-Q25

C-Q10: 如何備份/搬遷容器與資料到其他平台？
- A簡: 匯出映像/重建同映像版本，複製 Volume 資料夾，在新環境重建容器並掛載原資料。
- A詳:
  - 實作步驟:
    1) 記錄映像版本與容器參數（Port、Env、Volume）。
    2) 備份 Volume 資料夾（如 wp-content、/var/lib/mysql）。
    3) 在新平台拉取同版本映像，還原 Volume，重建容器。
  - 關鍵設定: 一致的映像版本、資料一致性（停機備份）。
  - 注意/最佳實踐: 先在測試環境演練；搭配反向代理/SSL 設定同步移轉；變更 DNS 生效視 TTL 而定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, A-Q23, B-Q9


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 官方 WordPress 映像在 DSM 打開 Terminal 就崩潰，怎麼辦？
- A簡: 先檢視日誌與資源限制，若為映像相容性問題，改用 Nginx+PHP-FPM 的穩定映像或版本回退。
- A詳:
  - 症狀: 在 DSM Docker 管理員中開啟容器終端導致容器 Crash。
  - 可能原因: 映像與 DSM Docker 版本相容性、資源不足、終端互動觸發 bug。
  - 解決步驟: 1) docker logs 檢視錯誤；2) 降低終端互動，改用 Shell 直接連接；3) 調整資源限制；4) 改用替代映像（如 Nginx+PHP-FPM 組合）；5) 回退到穩定標籤。
  - 預防: 優先官方/活躍維護映像；在測試環境驗證；保留版本鎖定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q2, B-Q15

D-Q2: 80 埠被 DSM 佔用，容器無法映射到 80，如何處理？
- A簡: 使用 DSM 的 Apache Reverse Proxy：容器映射到非 80 內部埠，再由代理層統一對外提供 80。
- A詳:
  - 症狀: Docker 容器映射 80 失敗；或服務可用但外網無法直達 80。
  - 可能原因: DSM 內建服務佔用 80/443；端口衝突。
  - 解決步驟: 1) 將容器改映射非 80（如 8012）；2) 建立虛擬主機（C-Q3）；3) 加入 ProxyPass 設定（C-Q4）；4) 重啟 httpd。
  - 預防: 統一由反向代理承擔 80/443；避免容器對外直綁 80/443。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q4, B-Q14

D-Q3: DSM 介面調整後，手動加入的 vhost 代理設定被覆蓋了，怎麼辦？
- A簡: 用備份檔還原或合併差異，重啟 httpd。日後變更前先備份，或採 Include 外部檔。
- A詳:
  - 症狀: 反向代理失效，回到預設 404 或直接顯示靜態頁。
  - 可能原因: Web Station 更新虛擬主機時重寫 vhost 檔。
  - 解決步驟: 1) 還原備份至 /etc/httpd/httpd-vhost.conf-user；2) httpd -k restart；3) 測試站點。
  - 預防: 每次 UI 變更前備份；建立變更流程；考慮 Include 外部檔案以降低覆蓋風險。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q19, C-Q8, C-Q4

D-Q4: 透過網域訪問只看到 Synology 預設 404，怎麼排查？
- A簡: 檢查虛擬主機 ServerName/DNS 解析是否一致，確認 vhost 生效與代理設定正確。
- A詳:
  - 症狀: 訪問網域顯示 DSM 預設 404。
  - 可能原因: DNS 指向錯誤、Host 不匹配、vhost 未正確配置或順序、代理區塊遺漏。
  - 解決步驟: 1) 檢查 DNS（A/CNAME、內網）；2) 確認 vhost ServerName 與網域一致；3) 檢查 vhost 檔是否包含代理設定；4) 重啟 httpd。
  - 預防: 設定前先以 ping/nslookup 確認解析；保留正確的 vhost 範本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q3, C-Q4

D-Q5: Reverse Proxy 後 WordPress 重導或資源 URL 錯亂，怎解？
- A簡: 開啟 ProxyPreserveHost，正確設定 ProxyPassReverse；檢查 WordPress 網站 URL 設定。
- A詳:
  - 症狀: 被導向內部位址、圖片/JS 404、混合使用外部/內部主機名。
  - 可能原因: 未保留 Host header、未重寫回應 Location、WP 站點 URL 設置錯誤。
  - 解決步驟: 1) 在 vhost 設 ProxyPreserveHost On；2) 正確配置 ProxyPassReverse；3) 檢查 WP 一般設定的 WordPress Address/Site Address；4) 清除快取。
  - 預防: 依 B-Q4 的範式配置；部署前確認站點 URL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q4, C-Q4

D-Q6: Reverse Proxy 回 502/503，如何診斷？
- A簡: 檢查後端容器狀態/埠、vhost 目標可達性、日誌錯誤、資源是否耗盡，逐層定位。
- A詳:
  - 症狀: 代理層返回 502/503。
  - 可能原因: 後端未啟動或端口錯誤、主機名 nas 不可解析、資源不足、ACL 限制。
  - 解決步驟: 1) docker ps、logs 檢查後端；2) 在 NAS 上 curl http://nas:8012 測試；3) 檢查 Apache error_log；4) 調整資源限制（B-Q8）；5) 修正 DNS/hosts。
  - 預防: 啟動順序（先 DB 後 App）、健康檢查、資源監控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q5, C-Q5

D-Q7: 手機 4G 能訪問但 Wi-Fi 不行（或反之），可能原因？
- A簡: 內外 DNS/路由不同導致；檢查 hairpin NAT 支援或設置內網 DNS 靜態紀錄。
- A詳:
  - 症狀: 外網可用，內網失敗；或相反。
  - 可能原因: 內網未解析到 NAS 內部 IP；路由器不支援 hairpin NAT；DNS 緩存。
  - 解決步驟: 1) 檢查 4G 與 Wi-Fi 解析 IP；2) 設定內網 DNS 靜態紀錄（C-Q7）；3) 檢查 Port Forward；4) 清理 DNS 快取。
  - 預防: 規劃內外 DNS 分工（A-Q21）；測試多路徑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, A-Q21, C-Q7

D-Q8: WordPress 連不上 MySQL，怎排查？
- A簡: 核對 DB 主機/帳密、MySQL 狀態與埠、網路路由，查看容器與應用日誌。
- A詳:
  - 症狀: WordPress 安裝或運行時提示 DB 連線失敗。
  - 可能原因: DB_HOST 錯誤、MySQL 未啟動/埠未開、帳密錯、權限不足。
  - 解決步驟: 1) 檢查 MySQL 容器運行與 Port；2) 從 WP 容器 ping/curl DB_HOST；3) 檢查環境變數與 wp-config.php；4) 查看 MySQL 日誌權限錯誤。
  - 預防: 使用固定配置、先啟 DB 再啟 WP、強密碼與最小權限。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q1, C-Q2

D-Q9: 容器重建後資料不見了，如何挽救與避免？
- A簡: 若未做 Volume 持久化，資料可能丟失；平時應映射資料資料夾並定期備份。
- A詳:
  - 症狀: 重建容器後 WordPress 內容/上傳/設定消失，或 DB 資料丟失。
  - 可能原因: 未使用 Volume 映射；映射到錯誤目錄；權限錯誤導致未寫入。
  - 解決步驟: 1) 搜尋是否有舊容器層備份/快照；2) 從備份還原 Volume；3) 重建容器並正確掛載。
  - 預防: 依 A-Q23 規劃 Volume；建立備份策略；定期驗證還原流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q23, B-Q16, C-Q1

D-Q10: 網站效能不佳或 RAM 不足，如何優化？
- A簡: 調整容器資源限制、採輕量映像、優化 Nginx/PHP-FPM、反向代理快取，必要時升級硬體或外移服務。
- A詳:
  - 症狀: 響應慢、Swap 頻繁、偶發 5xx。
  - 可能原因: RAM/CPU 資源不足、PHP-FPM 參數不當、無快取。
  - 解決步驟: 1) 監控資源使用；2) 限制非關鍵容器資源（B-Q8）；3) 優化 Nginx/PHP-FPM（B-Q7）；4) 啟用 gzip/快取（B-Q22）；5) 升級 RAM 或將次要服務移到外部。
  - 預防: 事先容量規劃；持續監控與調參；使用輕量映像。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q22, C-Q2


### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Docker？
    - A-Q2: Docker 與傳統 VM 有何差異？
    - A-Q4: 什麼是 Synology DSM？
    - A-Q3: 為什麼在 Synology DSM 上使用 Docker？
    - A-Q5: 什麼是 Docker Image 與 Container？
    - A-Q6: Docker Hub 是什麼？為何重要？
    - A-Q7: 什麼是 Nginx？與 Apache 有何差異？
    - A-Q9: 什麼是 WordPress？與 BlogEngine 有何差異？
    - A-Q10: 什麼是 Reverse Proxy？與 Forward Proxy 差異？
    - A-Q12: 為何 80 Port 常被佔用？如何面對？
    - A-Q13: 什麼是 Virtual Host？在 DSM Web Station 有何角色？
    - A-Q22: 什麼是 Port Mapping？在 DSM Docker 如何使用？
    - C-Q1: 如何在 DSM 上安裝 MySQL 官方映像並設定資料持久化？
    - C-Q2: 如何以 Nginx+PHP-FPM 的 WordPress 映像部署前端並映射埠？
    - C-Q3: 如何用 DSM Web Station 建立綁定網域的虛擬主機？

- 中級者：建議學習哪 20 題
    - A-Q15: Docker 在 NAS 上的資源優勢是什麼？
    - A-Q16: 為什麼不用 DSM 套件中心的 WordPress？缺點？
    - A-Q17: 為何無法讓多個容器都映射到 80？
    - A-Q18: ProxyPreserveHost、ProxyPass、ProxyPassReverse 分別是什麼？
    - A-Q19: 為何要備份 httpd-vhost.conf-user？
    - A-Q20: 什麼是 DNS A 記錄與 CNAME？本文如何使用？
    - A-Q21: 什麼是內網 DNS 與外網 DNS 分工？
    - A-Q23: 什麼是資料持久化（Volume）？對 WordPress/MySQL 有何重要性？
    - B-Q1: 在 DSM 上，Reverse Proxy 從外網到容器的請求流程如何運作？
    - B-Q2: Apache 的 mod_proxy 與 mod_proxy_http 背後機制是什麼？
    - B-Q4: ProxyPass 與 ProxyPassReverse 如何協同處理 URL 與重導？
    - B-Q5: DSM 上 Docker 網路在橋接模式下如何通訊？
    - B-Q6: WordPress 與 MySQL 容器的連線機制是什麼？
    - B-Q7: Nginx + PHP-FPM 的請求處理流程？
    - C-Q4: 如何在 Apache 加入 Reverse Proxy 設定並重啟生效？
    - C-Q5: 如何驗證 Reverse Proxy 是否正確？
    - C-Q6: 如何設定路由器 Port Forward 將 80 導向 NAS？
    - C-Q7: 如何設定內外 DNS 以優化存取？
    - D-Q2: 80 埠被 DSM 佔用，容器無法映射到 80，如何處理？
    - D-Q5: Reverse Proxy 後 WordPress 重導或資源 URL 錯亂，怎解？

- 高級者：建議關注哪 15 題
    - A-Q24: 什麼是 Load Balancer？與 Reverse Proxy 關係？
    - A-Q25: 為何常在 Reverse Proxy 上做 HTTPS 終結？
    - B-Q8: DSM Docker 管理的資源限制如何生效？
    - B-Q12: 內外網 DNS 與 NAT 迴圈（hairpin NAT）如何影響訪問？
    - B-Q13: 多站點多容器的反向代理設計原理？
    - B-Q17: 使用 Nginx 作為 Reverse Proxy 與 Apache 有何原理層差異？
    - B-Q18: Reverse Proxy 層的負載均衡策略有哪些？
    - B-Q21: 反向代理的安全考量有哪些？
    - B-Q22: 反向代理對效能的影響與優化方向？
    - C-Q8: 如何備份並避免 vhost 設定被 DSM 覆蓋？
    - C-Q9: 如何同時對外發布多個容器（如 WordPress 與 Redmine）？
    - C-Q10: 如何備份/搬遷容器與資料到其他平台？
    - D-Q1: 官方 WordPress 映像在 DSM 打開 Terminal 就崩潰，怎麼辦？
    - D-Q6: Reverse Proxy 回 502/503，如何診斷？
    - D-Q10: 網站效能不佳或 RAM 不足，如何優化？