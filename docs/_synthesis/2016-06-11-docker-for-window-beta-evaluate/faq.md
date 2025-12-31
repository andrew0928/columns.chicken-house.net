---
layout: synthesis
title: "專為 Windows 量身訂做的 Docker for Windows (Beta) !"
synthesis_type: faq
source_post: /2016/06/11/docker-for-window-beta-evaluate/
redirect_from:
  - /2016/06/11/docker-for-window-beta-evaluate/faq/
postid: 2016-06-11-docker-for-window-beta-evaluate
---

# 專為 Windows 量身訂做的 Docker for Windows (Beta) ！FAQ 精選

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Docker for Windows (Beta)？
- A簡: Docker 官方針對 Windows 的原生應用，內建 Hyper-V 虛擬機管理，簡化開發者於非 Linux 平台使用容器。
- A詳: Docker for Windows (Beta) 是 Docker 在 Windows 上的原生整合套件，內含 Docker CLI、Compose 等工具，並以 Hyper-V 建立 MobyLinuxVM 來運行 Linux 容器。它捨棄 VirtualBox 與 Boot2Docker，改用精簡的 Alpine Linux/BusyBox，提供原生設定介面、開機自動啟動、且支援本機資料夾掛載與自動更新，目標是改善 Windows 開發者的容器體驗與開發流程整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q8, B-Q1

Q2: 為什麼需要 Docker for Windows？
- A簡: 降低非 Linux 平台使用容器的門檻，優化開發體驗與 DevOps 前段流程整合。
- A詳: 多數容器技術以 Linux 為核心，Windows 或 Mac 需透過 VM 才能運行 Linux 容器。Docker for Windows 將 Hyper-V、Docker 引擎、工具與設定整合為原生應用，讓 Windows 開發者可直接用 PowerShell/命令列操作，不必手動管理 VM，並提供更快更穩定的檔案掛載與自動更新，以便在本機開發、測試與部署前整合作業流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q2, B-Q24

Q3: Docker for Windows 與 Docker Toolbox 有何差異？
- A簡: 前者用 Hyper-V 與原生應用，後者仰賴 VirtualBox；新版更快更穩，整合度高。
- A詳: Docker Toolbox 在 Windows 上使用 VirtualBox 與 Boot2Docker ISO，需 docker-machine 建 VM；Docker for Windows 改以 Hyper-V 建立 MobyLinuxVM，整合原生 UI、設定與自動更新，不再依賴 VirtualBox。兩者可共存，但新版不含 Kitematic；若要用 Kitematic 仍需 Toolbox。新方案並提供更佳的 Volume 掛載體驗與資源管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q12, B-Q18

Q4: 為何捨棄 VirtualBox，改用 Hyper-V？
- A簡: Hyper-V 整合度高、效能穩定，且 hypervisor 互斥，避免與 VirtualBox 衝突。
- A詳: 在 Windows 上，Hyper-V 與其他 hypervisor（如 VirtualBox）無法同時使用，常造成衝突。Docker for Windows 採用 Hyper-V 可達更緊密的 OS 級整合、穩定的 VM 管理與自動啟動，並簡化開發環境。加上 Microsoft 的密切協作，Hyper-V 與容器生態串接更順暢，讓開發者不必再手動改造虛擬化層。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, D-Q5

Q5: 什麼是 Hyper-V？
- A簡: Microsoft 的 Type-1 虛擬化技術，提供高效能虛擬機，Windows 內建。
- A詳: Hyper-V 是微軟在 Windows 平台提供的原生 Hypervisor，支援建立與管理虛擬機、虛擬網路與儲存。它以 Type-1 架構提供較低的開銷與穩定性，並與 Windows 內核深度整合。Docker for Windows 利用 Hyper-V 建立 MobyLinuxVM，承載 Docker Engine 執行 Linux 容器，提供一致與可靠的開發體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q9

Q6: 什麼是 Nested Virtualization（巢狀虛擬化）？
- A簡: 在 VM 內再啟動 VM 的技術，需 CPU 支援並正確設定 Hyper-V。
- A詳: Nested Virtualization 允許在第一層 VM 內部再建立第二層 VM（如在外層 Windows 10 VM 中啟動 Hyper-V，並建立 MobyLinuxVM）。它需要 Intel VT-x 等硬體支援，且有多項限制，如需關閉動態記憶體、啟用 MAC Spoofing、避免 checkpoint/live migration。用於在實驗或教學環境於 VM 內體驗 Docker for Windows。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, B-Q3, D-Q1

Q7: Docker for Windows 的系統需求是什麼？
- A簡: Windows 10 Pro/Enterprise 1511+，啟用 Hyper-V，足夠 CPU/RAM。
- A詳: 官方建議 Windows 10 Pro 或 Enterprise（1511，Build 10586 以上），並啟用 Hyper-V 功能。若在外層 VM 測試，外層與內層均需支援 Hyper-V 與 Nested Virtualization，建議至少 4GB 記憶體，關閉動態記憶體。Windows 10 Home 因無 Hyper-V 不支援。安裝時若未啟用 Hyper-V，Docker 會引導安裝並重啟。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q4

Q8: 什麼是 MobyLinuxVM？
- A簡: Docker for Windows 自動建立的 Hyper-V 虛擬機，跑 Alpine Linux 與 Docker Engine。
- A詳: MobyLinuxVM 是 Docker for Windows 安裝後由服務自動建立的 Hyper-V VM，使用精簡的 Alpine Linux/BusyBox 作業系統承載 Docker Engine。容器在此 VM 內運行，而 Windows 端以 Docker CLI 操作。其資源配置（CPU/記憶體）可在 Docker Settings 調整，並開機自動啟動以提供無縫體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q9, C-Q7

Q9: 為何以 Alpine Linux/BusyBox 取代 Boot2Docker？
- A簡: Alpine/BusyBox 更精簡安全、啟動快，改善整體效能與維護性。
- A詳: 早期 Windows 容器體驗採 Boot2Docker ISO，如今改用體積小、維運簡單的 Alpine Linux 搭配 BusyBox。Alpine 使用 musl 與 busybox 提供核心工具，安全性與啟動速度良好，能縮短 VM 啟動與映像下載時間，降低資源占用，提升 Docker for Windows 的整體穩定與更新效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, B-Q9

Q10: 什麼是 Share Drives（磁碟分享）？
- A簡: 允許將 Windows 磁碟透過 Docker for Windows 分享給容器掛載存取。
- A詳: Share Drives 是 Docker for Windows 的設定，用於授權哪些 Windows 磁碟可供 Docker Engine 透過 VM 內的機制掛載給容器。啟用後，系統在 Windows 建立 SMB 分享，MobyLinuxVM 以 CIFS 掛載，再將路徑 bind mount 至容器，使容器得以存取主機檔案，提供更自然的本地開發與資料持久化流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q5, D-Q2

Q11: 為何在 Windows 上跑 Linux 容器仍需 VM？
- A簡: 容器共用宿主核心，Linux 容器需 Linux 核心，故以 VM 提供環境。
- A詳: 容器透過共用宿主作業系統核心達到輕量化與隔離。因此 Linux 容器必須運行於 Linux 核心之上。Windows 本身不是 Linux，故需啟動一個 Linux VM（MobyLinuxVM）承載 Docker Engine 與容器。Docker for Windows 自動化這層 VM 的建立與管理，對使用者呈現原生操作體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q8

Q12: Mac 與 Windows 版 Docker 的架構有何不同？
- A簡: Mac 以 xhyve/HyperKit，Windows 以 Hyper-V；均用精簡 Linux VM 承載 Engine。
- A詳: 兩者皆以一台輕量 Linux VM 承載 Docker Engine，但 Mac 版使用 xhyve 類型的虛擬化，Windows 版採 Hyper-V。兩者同樣提供原生應用、整合工具與設定介面，目標一致地優化非 Linux 平台的容器體驗。差異主要在虛擬化技術堆疊與 OS 整合方式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q9

Q13: 什麼是 Docker Engine？
- A簡: Docker 的守護行程與 API 平台，負責建置、發佈與運行容器。
- A詳: Docker Engine 是容器平台核心元件，提供映像建置、容器生命週期管理、網路與儲存等能力，並以 REST API 對外服務。Docker for Windows 讓 Engine 跑在 MobyLinuxVM 中，Windows 端以 Docker CLI 與其互動。它也是與 Docker Compose、Registry 等生態系整合的基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q24

Q14: Windows Container 與 Hyper-V Container 的差異？
- A簡: Windows Container 為程序隔離；Hyper-V Container 以輕量 VM 提供核心隔離。
- A詳: 在 Windows 平台，容器有兩種型態。Windows Container 使用程序層級隔離（類似命名空間概念），共享宿主核心；Hyper-V Container 則以極輕量的 Hyper-V 分割區提供核心級隔離，安全邊界更強。兩者皆可用 Docker CLI 操作，差異透過 --isolation 選項指定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q13, B-Q14

Q15: 什麼是容器的隔離（Isolation）？
- A簡: 容器隔離指資源與安全邊界，含程序隔離與核心隔離兩層級。
- A詳: 隔離是容器安全與穩定的基礎，常見為程序/命名空間隔離（如 Linux namespaces）提供進程、檔案、網路等分離。在 Windows 上，另提供 Hyper-V 型容器，透過輕量 VM 建立更強的核心隔離，降低共用核心的風險。選擇何種隔離取決於安全需求與效能取捨。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13

Q16: docker run 的 --isolation 參數做什麼？
- A簡: 指定容器隔離技術；Windows 可選 default、process、hyperv。
- A詳: --isolation 用於指定容器隔離模式。在 Linux 上僅有 default（對應 namespaces）；在 Windows 可選 default（由 daemon 設定）、process（程序隔離）或 hyperv（Hyper-V 核心隔離）。例如 docker run -it --isolation=hyperv nanoserver cmd。選擇會影響安全邊界與啟動開銷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q9

Q17: 什麼是 Docker Volume 與 Volume Driver？
- A簡: Volume 為容器持久化儲存；Driver 負責掛載來源（本機/網路）。
- A詳: Volume 是容器的推薦持久化方式，與容器生命週期解耦。Volume Driver 提供掛載機制，如本機路徑、NFS、CIFS/SMB 等。Docker for Windows 的 Share Drives 即借助 SMB/CIFS 將 Windows 目錄掛入 MobyLinuxVM，再 bind 到容器，使主機與容器資料往返更流暢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q5, D-Q2

Q18: 為何要掛載本機資料夾給容器？
- A簡: 讓程式碼與資料即時同步，開發測試更快速、無需複製映像。
- A詳: 本機掛載能讓容器直接讀寫宿主機檔案，不需每次建置映像或額外開啟網芳，提升開發迭代速度。Docker for Windows 透過 Share Drives 將 Windows 目錄安全掛載，適用於程式碼、設定檔與測試資料的快速周轉。需留意路徑轉換與權限設定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q3

Q19: Docker for Windows 對 DevOps 有何價值？
- A簡: 打通桌面到雲端的開發流程，降低環境差異與操作摩擦。
- A詳: 它將引擎、工具與本機整合，讓開發者在 Windows 以相同 CLI 與配置運作容器，並可對接 Registry、Compose、Cloud 等，減少「在我電腦可運作」的落差。更可靠的 Volume、原生 UI 與自動更新，使前期開發、測試與交付更順暢，提升整體 DevOps 效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q24, A-Q20

Q20: 原生 UI 與自動更新的好處是什麼？
- A簡: 降低維運成本，讓設定、升級與資源調整更直覺一致。
- A詳: 原生 UI 提供集中設定入口（資源、磁碟分享、網路），並整合自動更新，避免版本漂移與手動維護成本。對團隊而言，可快速統一工具版本與行為；對個人而言，升級與回報問題更單純，縮短故障排除時間，提升生產力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q8

Q21: 多架構支援（x86/ARM）是什麼？
- A簡: 允許建置與運行多硬體架構映像，提升移植性與覆蓋面。
- A詳: Docker 可藉映像清單與建置策略支援多架構（如 x86、ARM），讓同一標籤在不同平台拉取對應映像。Docker for Windows 宣告 out-of-the-box 支援 Linux x86 與 ARM（Windows 專屬文件稍後提供），有助於跨裝置或 IoT 場景的一致性與測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11

Q22: Linux 容器與 Windows 容器有何差異？
- A簡: 核心與基底映像不同；工具相同但相容性與隔離選項差異。
- A詳: Linux 容器共享 Linux 核心，常用的映像與工具鏈成熟；Windows 容器則以 Windows 核心與基底映像（如 nanoserver）運行。Docker CLI 操作方式相似，但 Windows 容器可用 --isolation 選 process/hyperv。映像相容性、檔案系統與網路細節各自不同。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q25

Q23: 為何 Nested 環境需停用動態記憶體（Dynamic Memory）？
- A簡: 巢狀虛擬化對記憶體有嚴格需求，動態分配會導致內層 VM 啟動失敗。
- A詳: 啟用 Nested Virtualization 時，外層 VM 必須提供穩定的實體化記憶體給內層 Hypervisor。動態記憶體會在執行期調整配置，影響內層 VM 的穩定性與啟動流程，因此 Microsoft 要求停用動態記憶體，並固定分配足夠的 RAM（至少 4GB 以上較穩妥）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q8

Q24: 為何 Hyper-V 與其他 Hypervisor 無法共存？
- A簡: 虛擬化擴充指令獨佔，Hyper-V 啟用時其他 Hypervisor 無法使用。
- A詳: 多數 hypervisor 需獨佔 CPU 虛擬化功能（VT-x/AMD-V），一旦 Hyper-V 啟用，VirtualBox 等便無法正常使用同一套硬體資源，導致衝突與失敗。Docker for Windows 以 Hyper-V 為核心，建議避免同時依賴 VirtualBox 的工作流，或在需要時切換環境並了解其限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, D-Q5


### Q&A 類別 B: 技術原理類

Q1: Docker for Windows 的架構如何運作？
- A簡: Windows 原生服務管理 Hyper-V 上的 MobyLinuxVM，CLI 經服務與引擎溝通。
- A詳: 原理說明：Windows 上的 Docker 應用啟動一個管理服務，於 Hyper-V 建立 MobyLinuxVM（Alpine），在 VM 內啟動 Docker Engine。關鍵流程：安裝後啟用 Hyper-V、建立 VM、啟動引擎、提供 CLI 代理。核心組件：Windows 端服務與 UI、Hyper-V、MobyLinuxVM、Docker Engine、Docker CLI。用戶以 CLI 操作，服務轉發至 VM 內引擎處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q8, B-Q4

Q2: Docker for Windows 的安裝與啟動流程為何？
- A簡: 安裝 MSI、啟用 Hyper-V、重啟、輸入 Token、建立啟動 MobyLinuxVM。
- A詳: 原理說明：安裝程式部署 CLI/服務，檢查 Hyper-V。關鍵步驟：1) 執行 MSI；2) 若未啟用 Hyper-V，程序引導安裝並重開；3) 首次啟動輸入 Beta Token；4) 自動建立 MobyLinuxVM 並啟動 Docker Engine；5) 系統列圖示顯示狀態。核心組件：安裝器、Hyper-V、MobyLinuxVM、Docker 服務與 UI。完成後可直接用 PowerShell 執行 docker 指令。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q3

Q3: Nested Virtualization 在此案例的機制是什麼？
- A簡: 於外層 VM 暴露虛擬化擴充，允許內層再啟動 Hyper-V 與 VM。
- A詳: 原理說明：外層 VM 透過 Set-VMProcessor ExposeVirtualizationExtensions 將 VT-x 暴露給來賓系統。關鍵步驟：停用動態記憶體、啟用 MAC Spoofing、配置足夠 RAM/CPU、關閉 checkpoint/save 操作。核心組件：外層 Hyper-V、內層 Hyper-V、虛擬交換器。此設計讓在 VM 內安裝 Docker for Windows 成為可能。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, A-Q23, C-Q2

Q4: Windows 上 Docker CLI 與 Engine 如何通訊？
- A簡: CLI 調用本機 Docker 服務，服務轉發至 MobyLinuxVM 內的 Docker Engine。
- A詳: 原理說明：Windows 端 docker.exe 透過本機管道與 Docker 服務溝通，服務扮演代理，連入 MobyLinuxVM 內的 Docker daemon。關鍵步驟：CLI 發出 API 請求、服務轉發至 VM、Engine 執行並回傳。核心組件：Docker CLI、Windows 服務、Hyper-V VM、Docker daemon。此設計讓用戶無感 VM 存在，直接在 Windows 使用 CLI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, A-Q13

Q5: Share Drives 的 Volume 掛載背後機制是什麼？
- A簡: Windows 建 SMB 分享，MobyLinuxVM 以 CIFS 掛載，容器再 bind mount。
- A詳: 原理說明：勾選 Share Drives 後，Windows 建立對應磁碟分享；MobyLinuxVM 透過 CIFS 連線掛入該分享，再將掛載點綁定到容器目錄。關鍵步驟：授權磁碟→建立 SMB 分享→VM 內 CIFS 掛載→docker run -v 綁定。核心組件：SMB/CIFS、Hyper-V 網路、MobyLinuxVM、Docker Volume。此法兼顧簡單與通用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q5, D-Q2

Q6: Windows 路徑到容器路徑的映射流程為何？
- A簡: 將 Windows 路徑授權分享，VM 掛載後綁定到容器內的 Linux 路徑。
- A詳: 原理說明：路徑轉換包含平台差異（大小寫磁碟代號與反斜線）。關鍵步驟：1) 在 Settings 勾選 C:\ 或 D:\；2) docker run -v c:\path:/data；3) 引擎在 VM 鏈路上找到 CIFS 掛載點並綁定；4) 容器讀寫 /data。核心組件：路徑轉換器、CIFS 掛載、Docker Volume 綁定。需注意權限與路徑大小寫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q3

Q7: hello-world 容器的執行流程是什麼？
- A簡: 下載映像，建立容器，輸出訊息並退出，驗證引擎與網路正常。
- A詳: 原理說明：docker run 首次會從 Docker Hub 拉取 hello-world 映像，建立容器後執行主程序輸出訊息。關鍵步驟：pull 映像→create→start→stdout→exit。核心組件：Docker Hub、Engine、網路與儲存層。成功輸出即代表本機 CLI、VM、網路與引擎工作流正常。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q9

Q8: Docker Settings 的作用與原理？
- A簡: 以圖形介面集中管理 VM 資源、磁碟分享、更新與啟動行為。
- A詳: 原理說明：Settings 實際代理修改 Hyper-V VM 的 CPU/記憶體等資源，與 Windows 端的共享設定。關鍵步驟：用戶在 UI 調整→服務套用到 Hyper-V 與系統設定。核心組件：Docker 服務、Hyper-V 管理 API、Windows 分享。使資源調整與掛載授權更直觀一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q7

Q9: MobyLinuxVM 的建立與配置過程？
- A簡: 由 Docker 服務自動建立，載入 Alpine，配置網路與儲存並啟動 Engine。
- A詳: 原理說明：首次啟動時服務建立 VM，指定 CPU/RAM、虛擬磁碟與虛擬交換器，載入 Alpine 系統。關鍵步驟：建 VM→配置資源→網路接上虛擬交換器→啟動→daemon 開機自動啟動。核心組件：Hyper-V、虛擬交換器、Alpine Linux、Docker daemon。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q1

Q10: 調整 CPU/記憶體會如何影響容器？
- A簡: 影響 VM 可用資源上限，進而影響容器併發與效能。
- A詳: 原理說明：容器共享 VM 的資源池。關鍵步驟：變更 Settings→Hyper-V 更新 VM 規格→重啟 VM 生效。核心組件：Hyper-V 資源配置、Docker 調度。提高 CPU/RAM 可改善 build 與運行速度，但需平衡宿主機資源避免爭用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7

Q11: 多架構映像如何被選擇執行？
- A簡: 透過映像清單（manifest list）匹配平台，拉取對應架構映像。
- A詳: 原理說明：Docker Hub 可發布多架構映像清單，客戶端依平台自動選擇。關鍵步驟：pull 指令→解析 manifest list→選擇適配映像→下載執行。核心組件：Registry、manifest list、客戶端平台偵測。使相同標籤在不同平台取得合適版本。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21

Q12: Docker Toolbox 與 Docker for Windows 如何共存？
- A簡: 可共存；新版不含 Kitematic，切換時留意環境變數與端點設定。
- A詳: 原理說明：兩套工具可同機安裝，但端點不同。關鍵步驟：使用 Docker for Windows 時清空 DOCKER_HOST 等環境變數；使用 Toolbox 時以 docker-machine env 設定對應端點。核心組件：docker-machine、環境變數、Hyper-V/VirtualBox。Kitematic 暫未內建於新版。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, C-Q10

Q13: Windows Container 的隔離原理是什麼？
- A簡: 提供 process 與 Hyper-V 兩層隔離，後者以輕量 VM 強化邊界。
- A詳: 原理說明：process 模式提供命名空間級隔離；Hyper-V 容器以隔離的最小化 VM 提供核心與驅動獨立。關鍵步驟：docker run 時以 --isolation 指定；daemon 端可設定預設模式。核心組件：Windows 容器堆疊、Hyper-V、Docker CLI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q16

Q14: --isolation 在 Windows 上的執行差異？
- A簡: default 由 daemon 決定；process 輕量；hyperv 安全性更高但成本較高。
- A詳: 原理說明：Linux 僅 default；Windows 可選 process 或 hyperv。關鍵步驟：docker run --isolation=hyperv 显式指定；或在 daemon 用 --exec-opt 設定。核心組件：Docker CLI、daemon 配置。開銷與啟動時間因模式而異，需依安全需求選擇。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, A-Q16

Q15: Hyper-V NAT 與 MAC Spoofing 在巢狀網路的需求？
- A簡: 內層 VM 網通需啟用 MAC Spoofing；外層提供 NAT/交換器連線。
- A詳: 原理說明：外層 VM 的虛擬網卡預設封鎖來賓自訂 MAC；啟用 MAC Spoofing 允許內層 VM 正常通訊。關鍵步驟：Set-VMNetworkAdapter -MacAddressSpoofing On；使用虛擬交換器或 NAT。核心組件：Hyper-V vSwitch、網卡設定。未啟用會導致內層 VM 無法上網。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, D-Q7

Q16: 如何驗證 Nested 設定正確？
- A簡: 在外層 VM 內手動建立並啟動第二台 VM，確認能正常開機與上網。
- A詳: 原理說明：實際啟動第二層 VM 最具體。關鍵步驟：在外層 VM 開啟 Hyper-V 管理員→建立測試 VM→啟動，觀察是否遇錯。核心組件：外層 Hyper-V、MAC Spoofing、記憶體設定。若失敗，檢查 ExposeVirtualizationExtensions、Dynamic Memory、VBS/Device Guard 等。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q1

Q17: Docker for Windows 服務如何自動啟動與監控？
- A簡: 服務隨開機自啟，確保 MobyLinuxVM 與 daemon 存活，失敗時自動重試。
- A詳: 原理說明：Windows 服務設為自動啟動，開機後檢查 VM 狀態並啟動 daemon。關鍵步驟：啟動服務→檢查資源→啟動 VM→健康檢查→提供通知。核心組件：Windows 服務管理、Hyper-V API、健康監控。提升使用者無縫體驗與穩定性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q9

Q18: Boot2Docker 與 Alpine/BusyBox 有何技術差異？
- A簡: 兩者皆精簡；Alpine 更小、更安全、更新快，適合現代化基底。
- A詳: 原理說明：Boot2Docker 是早期最小化發行版；Alpine 以 musl 與 BusyBox 提供更小基底與硬化配置。關鍵特點：更小影像、較快啟動、維護活躍。核心組件：包管理、libc、核心工具。採用 Alpine 有助於縮短 VM 啟動與映像傳輸時間。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9

Q19: Hyper-V 與 VirtualBox 衝突的底層原因？
- A簡: 兩者需獨佔硬體虛擬化，啟用其中之一會讓另一個不可用。
- A詳: 原理說明：VT-x/AMD-V 等 CPU 擴充由 hypervisor 佔用。關鍵現象：啟動 Hyper-V 後，VirtualBox 無法獲得硬體權限導致虛擬機啟動失敗。核心組件：CPU VT 擴充、hypervisor 啟動序。解法是二選一或在特定情境停用某一方。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, D-Q5

Q20: Volume 資料的持久化位置與機制？
- A簡: 沒共享時存在 MobyLinuxVM（如 /var/lib/docker/volumes），共享時寫回 Windows。
- A詳: 原理說明：未啟用 Share Drives 時，-v 掛載實際綁定到 VM 內部路徑，資料持久化於 VM 磁碟。啟用分享並對應路徑時，透過 CIFS 寫回 Windows。關鍵步驟：判斷掛載來源→映射綁定→資料寫入。核心組件：Docker Volume、CIFS、VM 檔案系統。影響備份與可攜性策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, C-Q5

Q21: 與 Windows 批次或 PowerShell 的整合流程？
- A簡: 直接在 cmd/PowerShell 執行 docker 指令，融入既有腳本流程。
- A詳: 原理說明：docker.exe 安裝於 Windows 路徑，可被批次檔或 PowerShell 腳本呼叫。關鍵步驟：撰寫腳本→調用 build/run/compose→處理返回碼。核心組件：CLI、腳本環境、Docker 服務代理。實現 CI 本地模擬與自動化開發流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q5

Q22: 以 PowerShell 啟用 Nested 的關鍵指令是什麼？
- A簡: 設定暴露虛擬化、關閉動態記憶體、啟用 MAC Spoofing 等必要項。
- A詳: 原理說明：透過 Hyper-V PowerShell 指令調整 VM。關鍵步驟：Set-VMProcessor -ExposeVirtualizationExtensions $true；Set-VMMemory -DynamicMemoryEnabled $false；Set-VMNetworkAdapter -MacAddressSpoofing On。核心組件：Hyper-V PowerShell、VM 設定。這些是讓內層 VM 正常運作的必要條件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, D-Q1

Q23: Device Guard/VBS 為何會阻擋巢狀虛擬化？
- A簡: VBS 佔用虛擬化功能，無法再對來賓 VM 暴露虛擬化擴充。
- A詳: 原理說明：Device Guard/VBS 使用虛擬化技術保護 OS，導致宿主不能將 VT 擴充提供給來賓。關鍵步驟：需停用 VBS 才能預覽 nested。核心組件：VBS、Hypervisor 模式。否則內層 Hyper-V 無法啟動，導致 MobyLinuxVM 建立失敗。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q1, D-Q7

Q24: Docker 與 DevOps 串接的技術構件有哪些？
- A簡: Engine、CLI、Compose、Machine、Registry/Hub、Cloud，涵蓋建置到部署。
- A詳: 原理說明：以 Engine 與 CLI 為核心，Compose 編排多容器，Machine 管理多端點，Registry/Hub 發佈與分發映像，Cloud/Cluster 管理運行。關鍵步驟：本地開發→映像推送→測試→部署。核心組件：Docker 生態系整合。Docker for Windows 讓前段更順暢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, C-Q10

Q25: Linux 與 Windows 容器在映像與執行有何差異？
- A簡: 基底與 API 不同；Windows 需相容版本與映像（如 nanoserver）。
- A詳: 原理說明：Linux 映像基於 Linux 發行版；Windows 映像基於 Windows（nanoserver 等）。關鍵步驟：選擇平台對應映像；Windows 可選隔離模式。核心組件：Kernel、映像層次、系統 API。跨平台時需注意相容性與部署管線差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, C-Q9

Q26: Volume I/O 路徑與效能有何考量？
- A簡: I/O 經容器→VM→CIFS→Windows，較本機直寫多一層轉送開銷。
- A詳: 原理說明：掛載本機資料夾時，實際資料流跨越多層（容器→VM 內部→CIFS→Windows 主機）。關鍵影響：協定轉換與虛擬化網路導致延遲。核心組件：CIFS、虛擬交換器、Volume 綁定。適合開發迭代；重度 I/O 場景應評估架構或使用命名卷策略。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q18, B-Q5


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在宿主機上建立支援 Nested 的外層 VM？
- A簡: 宿主啟用 Hyper-V，建立外層 VM，停用動態記憶體並暴露虛擬化擴充。
- A詳: 步驟：1) 宿主為 Win10 Pro/Ent，啟用 Hyper-V；2) 建立外層 VM（WIN10），分配≥4GB RAM，關閉 Dynamic Memory；3) 啟用虛擬化擴充與 MAC Spoofing；4) 安裝 Windows 10 Enterprise 10586。關鍵指令：
  Set-VMProcessor WIN10 -ExposeVirtualizationExtensions $true
  Set-VMMemory WIN10 -DynamicMemoryEnabled $false
  Set-VMNetworkAdapter -VMName WIN10 -MacAddressSpoofing On
注意：避免使用 checkpoint/save；確保裝置安全功能未阻擋。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q1

Q2: 如何用 PowerShell 啟用 Nested Virtualization？
- A簡: 用 Set-VMProcessor、Set-VMMemory、Set-VMNetworkAdapter 等指令配置。
- A詳: 具體步驟與指令：
  1) 暴露虛擬化：Set-VMProcessor <VMName> -ExposeVirtualizationExtensions $true
  2) 關閉動態記憶體：Set-VMMemory <VMName> -DynamicMemoryEnabled $false
  3) 啟用 MAC Spoofing：Set-VMNetworkAdapter -VMName <VMName> -MacAddressSpoofing On
  4) 配置足夠 RAM/CPU，確保 Intel VT-x。
最佳實踐：建立前快照宿主；完成後以測試 VM 驗證網路可用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, D-Q7

Q3: 如何安裝 Docker for Windows (Beta)？
- A簡: 下載 MSI，執行安裝，啟用 Hyper-V，重啟後輸入 Token 初始化。
- A詳: 步驟：1) 下載官方 MSI；2) 執行安裝精靈；3) 若未啟用 Hyper-V，按 Install & Restart；4) 首次啟動輸入 Beta Token；5) 等待建立 MobyLinuxVM；6) 在系統列確認圖示綠燈。注意：防火牆與 Proxy 需允許；安裝後以 docker version 確認 CLI 可用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q4

Q4: 如何執行 hello-world 驗證環境？
- A簡: 打開 PowerShell，執行 docker run --rm hello-world，確認輸出訊息。
- A詳: 步驟：1) 開啟 PowerShell；2) docker run --rm hello-world；3) 首次執行會自動拉取映像；4) 看到歡迎訊息即成功。關鍵程式碼：
  docker run --rm hello-world
最佳實踐：接著執行 docker info 檢查 daemon 與 OS/Architecture；若失敗檢查服務與網路。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, D-Q9

Q5: 如何掛載 Windows 本機資料夾給容器？
- A簡: 在 Settings 勾選磁碟分享，使用 -v 映射 Windows 路徑到容器路徑。
- A詳: 步驟：1) Docker Settings→Share Drives 勾選 C:\；2) 建立測試資料夾 C:\Users\<you>\Docker\alpine-data；3) 執行：
  docker run -it --rm -v C:\Users\<you>\Docker\alpine-data:/data alpine /bin/ash
容器內 ls /data 應見檔案。注意：未分享磁碟時容器看不到主機檔案；大小寫與反斜線需正確；授權變更後重啟 Docker 服務。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q2

Q6: 如何在容器內建立檔案並回到 Windows 驗證？
- A簡: 容器內寫入 /data，退出後在 Windows 檔案總管確認檔案存在。
- A詳: 步驟：1) 以 C-Q5 的方式進入容器；2) 執行：
  cp /proc/version /data/alpine-version.txt
  cat /data/alpine-version.txt
3) 退出容器後在 Windows 目錄確認 alpine-version.txt 存在。注意：若看不到，檢查 Share Drives、路徑拼寫、權限授權是否有效；重試 docker run。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, D-Q3

Q7: 如何調整 MobyLinuxVM 的 CPU 與記憶體？
- A簡: 透過 Docker Settings 調整資源，或至 Hyper-V 管理員直接修改 VM。
- A詳: 步驟：1) Docker Settings→Resources 調整 CPU/RAM→套用並重啟；或 2) 在 Hyper-V 管理員關機後調整 VM 規格。注意：過低的 RAM 會使 build/啟動變慢；過高會壓迫宿主。最佳實踐：依專案需求逐步調整並監控 docker stats。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, D-Q8

Q8: 如何在外層 VM 內驗證 Nested 是否正常？
- A簡: 在外層 VM 用 Hyper-V 建一台測試 VM，啟動並確認網路與開機。
- A詳: 步驟：1) 外層 VM 打開 Hyper-V；2) 建立一台最小化測試 VM；3) 啟動並觀察是否報錯；4) 測試上網能力。若失敗，使用：
  Get-VMProcessor <VM> | fl ExposeVirtualizationExtensions
並檢查 MAC Spoofing 與 Dynamic Memory 設定。確保 VBS/Device Guard 已停用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, D-Q1

Q9: 如何使用 Windows 容器與 Hyper-V 隔離執行？
- A簡: 在支援 Windows 容器環境下，使用 --isolation=hyperv 運行映像。
- A詳: 步驟：1) 確保環境支援 Windows 容器（如 Windows 10/Server 2016 對應版）；2) 執行：
  docker run -it --isolation=hyperv mcr.microsoft.com/windows/nanoserver cmd
注意：此為 Windows 容器案例，與 Linux 容器不同；需切換至 Windows 容器模式並使用對應映像。最佳實踐：依安全需求選擇 process 或 hyperv。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q14, B-Q14

Q10: 如何讓 Docker Toolbox 與 Docker for Windows 共存並切換？
- A簡: 保留兩套工具，切換時調整 DOCKER_HOST 環境變數與端點設定。
- A詳: 步驟：1) 安裝兩套工具；2) 使用 Docker for Windows 時，確保未設定 DOCKER_HOST（或移除 env）；3) 使用 Toolbox 時執行：
  docker-machine env default | Invoke-Expression
注意：Kitematic 由 Toolbox 提供；避免同時啟用 VirtualBox 與 Hyper-V 工作流。最佳實踐：以不同終端視窗分離環境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q5


### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到 MobyLinuxVM 無法啟動怎麼辦？
- A簡: 檢查巢狀虛擬化、動態記憶體、MAC Spoofing 與 VBS，逐一修正。
- A詳: 症狀：Docker 提示無法啟動 MobyLinuxVM，或 Hyper-V 顯示啟動失敗。可能原因：未暴露虛擬化擴充、動態記憶體開啟、未啟用 MAC Spoofing、VBS/Device Guard 啟用或 RAM 不足。解決步驟：依 B-Q22 設定 PowerShell 指令、關閉 Dynamic Memory、啟用 MAC Spoofing、停用 VBS、分配≥4GB RAM。預防：建立外層 VM 樣板並固化設定。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, C-Q8

Q2: 容器看不到本機資料夾內容，怎麼處理？
- A簡: 啟用 Share Drives，重新授權磁碟分享，重啟 Docker 後再掛載。
- A詳: 症狀：-v 映射成功但容器內目錄為空。可能原因：未勾選 Share Drives 或授權過期。解決步驟：Settings→Share Drives 勾選對應磁碟→重新登入授權→重啟 Docker→重跑 docker run -v。預防：版本更新後檢查分享狀態；以小檔案測試掛載正確性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q5

Q3: 容器內寫入檔案但 Windows 看不到？
- A簡: 可能未指向已分享磁碟，或路徑拼寫錯誤，需更正並重試。
- A詳: 症狀：容器內可見新檔，Windows 主機無檔案更新。可能原因：未啟用分享、路徑大小寫或反斜線錯誤，實際寫到 VM 內部卷。解決步驟：確認 Share Drives、核對 -v 路徑、改用已分享磁碟；重跑容器並重測。預防：先從主機預置測試檔，再驗證容器可見，確保雙向。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q6

Q4: 安裝時提示需 Hyper-V，該怎麼辦？
- A簡: 依向導啟用 Hyper-V 並重啟，或手動開啟 Windows 功能。
- A詳: 症狀：首次啟動 Docker 提示需安裝 Hyper-V。可能原因：功能未啟用。解決步驟：按 Install & Restart 由安裝程式自動安裝；或至「啟用或關閉 Windows 功能」勾選 Hyper-V 後重啟。預防：安裝前先檢查系統版本與 BIOS 虛擬化開啟。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q7

Q5: VirtualBox 與 Hyper-V 衝突導致無法啟動？
- A簡: 兩者互斥，需選擇其一；使用 Docker for Windows 時避免啟用 VirtualBox。
- A詳: 症狀：VirtualBox VM 啟動失敗或錯誤碼；Docker Toolbox 無法使用。原因：Hyper-V 啟用後佔用虛擬化擴充。解決步驟：在需要 VirtualBox 的階段停用 Hyper-V 或以 Toolbox 獨立環境運行；建議採 Docker for Windows + Hyper-V 工作流。預防：規劃工具鏈，避免同時依賴兩套 hypervisor。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, C-Q10

Q6: 在外層 VM 套用 Checkpoint/Save 失敗？
- A簡: 巢狀虛擬化限制所致，需關閉內層 VM 或避免此操作。
- A詳: 症狀：套用檢查點或 Save 出錯。原因：外層 VM 啟用 nested 後，部分功能不相容（checkpoint、save、live migration）。解決步驟：關閉內層 VM（MobyLinuxVM 等）後再操作，或避免於托管其他 VM 的外層執行此類操作。預防：以文件化 SOP 限制操作行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3

Q7: 內層 VM 網路不通怎麼診斷？
- A簡: 檢查 MAC Spoofing、虛擬交換器與防火牆，必要時重建 vSwitch。
- A詳: 症狀：內層 VM 無法上網或無法解析。可能原因：未啟用 MAC Spoofing、虛擬交換器設定異常、防火牆阻擋。解決步驟：Set-VMNetworkAdapter -MacAddressSpoofing On；檢查 vSwitch 類型；調整防火牆規則；重建 vSwitch。預防：建立標準化 Nested 網路設定。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, C-Q2

Q8: 記憶體不足導致啟動遲緩或失敗怎麼辦？
- A簡: 提升外層 VM RAM 至≥4GB，關閉動態記憶體並調整 MobyLinuxVM 資源。
- A詳: 症狀：MobyLinuxVM 啟動慢或失敗、容器執行卡頓。原因：Nested 需要更多記憶體；動態記憶體造成波動。解決步驟：固定外層 VM RAM（≥4GB）、關閉 Dynamic Memory、在 Settings 調高 VM 資源。預防：依專案規模預估資源並預留餘裕。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q23, C-Q7

Q9: Docker CLI 顯示 cannot connect to the Docker daemon？
- A簡: 確認 Docker 服務與 MobyLinuxVM 已啟動，必要時重啟應用。
- A詳: 症狀：執行 docker 指令報連線失敗。可能原因：Docker for Windows 服務未啟動、VM 未就緒、端點環境變數殘留。解決步驟：從系統列重啟 Docker；等待 VM 啟動；清理 DOCKER_HOST 等環境變數；執行 docker info 驗證。預防：設定開機自啟，升級後重新登入確保權限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, C-Q4

Q10: 無法執行 ARM 或 Windows 映像的原因？
- A簡: 架構或平台不符；需使用對應映像與模式，或等待支援完善。
- A詳: 症狀：拉取/運行 ARM 或 Windows 映像失敗。原因：本機平台不符、Windows 容器模式未啟用、映像不相容。解決步驟：對 Linux 容器使用 x86_64 映像；欲用 Windows 容器先切換模式並選 nanoserver 等映像；ARM 依文件支援情況調整。預防：先確認映像平台與支援列表。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, B-Q11, C-Q9


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Docker for Windows (Beta)？
    - A-Q2: 為什麼需要 Docker for Windows？
    - A-Q3: Docker for Windows 與 Docker Toolbox 有何差異？
    - A-Q4: 為何捨棄 VirtualBox，改用 Hyper-V？
    - A-Q5: 什麼是 Hyper-V？
    - A-Q7: Docker for Windows 的系統需求是什麼？
    - A-Q8: 什麼是 MobyLinuxVM？
    - A-Q10: 什麼是 Share Drives（磁碟分享）？
    - A-Q11: 為何在 Windows 上跑 Linux 容器仍需 VM？
    - A-Q13: 什麼是 Docker Engine？
    - B-Q2: Docker for Windows 的安裝與啟動流程為何？
    - C-Q3: 如何安裝 Docker for Windows (Beta)？
    - C-Q4: 如何執行 hello-world 驗證環境？
    - C-Q5: 如何掛載 Windows 本機資料夾給容器？
    - D-Q4: 安裝時提示需 Hyper-V，該怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是 Nested Virtualization（巢狀虛擬化）？
    - A-Q9: 為何以 Alpine/BusyBox 取代 Boot2Docker？
    - A-Q14: Windows Container 與 Hyper-V Container 的差異？
    - A-Q15: 什麼是容器的隔離（Isolation）？
    - A-Q16: docker run 的 --isolation 參數做什麼？
    - A-Q17: 什麼是 Docker Volume 與 Volume Driver？
    - A-Q18: 為何要掛載本機資料夾給容器？
    - B-Q1: Docker for Windows 的架構如何運作？
    - B-Q4: Windows 上 Docker CLI 與 Engine 如何通訊？
    - B-Q5: Share Drives 的 Volume 掛載背後機制是什麼？
    - B-Q6: Windows 路徑到容器路徑的映射流程為何？
    - B-Q8: Docker Settings 的作用與原理？
    - B-Q9: MobyLinuxVM 的建立與配置過程？
    - B-Q12: Docker Toolbox 與 Docker for Windows 如何共存？
    - B-Q18: Boot2Docker 與 Alpine/BusyBox 有何技術差異？
    - C-Q1: 如何在宿主機上建立支援 Nested 的外層 VM？
    - C-Q2: 如何用 PowerShell 啟用 Nested Virtualization？
    - C-Q6: 如何在容器內建立檔案並回到 Windows 驗證？
    - D-Q1: 遇到 MobyLinuxVM 無法啟動怎麼辦？
    - D-Q2: 容器看不到本機資料夾內容，怎麼處理？

- 高級者：建議關注哪 15 題
    - A-Q21: 多架構支援（x86/ARM）是什麼？
    - A-Q22: Linux 容器與 Windows 容器有何差異？
    - A-Q23: 為何 Nested 環境需停用動態記憶體（Dynamic Memory）？
    - A-Q24: 為何 Hyper-V 與其他 Hypervisor 無法共存？
    - B-Q3: Nested Virtualization 在此案例的機制是什麼？
    - B-Q11: 多架構映像如何被選擇執行？
    - B-Q13: Windows Container 的隔離原理是什麼？
    - B-Q14: --isolation 在 Windows 上的執行差異？
    - B-Q15: Hyper-V NAT 與 MAC Spoofing 在巢狀網路的需求？
    - B-Q16: 如何驗證 Nested 設定正確？
    - B-Q19: Hyper-V 與 VirtualBox 衝突的底層原因？
    - B-Q20: Volume 資料的持久化位置與機制？
    - B-Q26: Volume I/O 路徑與效能有何考量？
    - C-Q9: 如何使用 Windows 容器與 Hyper-V 隔離執行？
    - D-Q7: 內層 VM 網路不通怎麼診斷？