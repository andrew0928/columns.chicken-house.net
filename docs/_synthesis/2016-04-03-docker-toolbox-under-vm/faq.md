---
layout: synthesis
title: "如何在 VM 裡面使用 Docker Toolbox ?"
synthesis_type: faq
source_post: /2016/04/03/docker-toolbox-under-vm/
redirect_from:
  - /2016/04/03/docker-toolbox-under-vm/faq/
---

# 如何在 VM 裡面使用 Docker Toolbox ?

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Docker Toolbox？
- A簡: Docker 在 Windows 的工具箱，整合 VirtualBox、Docker Machine、Kitematic，快速建好 Docker 環境。
- A詳: Docker Toolbox 是官方在 Windows 提供的一套安裝包，將多個必備元件一次安裝完成：Oracle VirtualBox 供建立 Linux VM、Docker Machine 負責用一致指令建立/管理 Docker 主機、Kitematic 提供 GUI 管理容器。因 Windows 無法直接使用 Linux Kernel，Toolbox 會在本機建立一台 boot2docker Linux VM 來承載 Docker Daemon，適合開發者快速上手。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q6, A-Q7, B-Q1, B-Q7

Q2: 為什麼在 Windows 需要透過 VM 才能跑 Docker？
- A簡: Docker 依賴 Linux 核心特性，Windows 需先啟動 Linux VM 才能運行 Docker Daemon。
- A詳: Docker 的容器隔離與資源控制依賴 Linux Kernel 機制。於純 Windows 環境無原生 Linux 核心可用，因此需先透過虛擬化啟動一台 Linux 主機（如 boot2docker），再在其上運行 Docker Daemon。Docker Toolbox 便是自動完成這台 Linux VM 的建立與配置，讓 Windows 用戶能順利執行與管理容器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q9, B-Q5, B-Q6

Q3: 什麼是 Nested Virtualization（巢狀虛擬化）？
- A簡: 讓在 Hyper‑V 中的來賓 VM 也能啟動虛擬化，於 VM 內再建立 VM 的技術。
- A詳: Nested Virtualization（巢狀虛擬化）是指在一台虛擬機器內再執行另一層虛擬化。以 Hyper‑V 為例，主機會將硬體虛擬化指令集暴露給來賓 VM，使其 vCPU 具備啟動 Hypervisor 的能力。啟用後，來賓 VM 即可安裝與啟動自己的虛擬化平台，建立第二層 VM。這對在 VM 內研究容器、雲平台或教學演練特別有用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q12, B-Q2, B-Q3

Q4: 為何在 VM 內無法再建立 VM？
- A簡: 多數 vCPU 不暴露 VT‑x/AMD‑V，來賓 VM 缺少硬體輔助虛擬化，無法再開 VM。
- A詳: 在未啟用巢狀虛擬化時，第一層虛擬化平台為了簡化與隔離，通常不會把硬體虛擬化擴充（如 VT‑x/AMD‑V）提供給來賓 VM。少了這些指令，來賓中的 VirtualBox 或 Hyper‑V 無法初始化第二層虛擬機器，常見錯誤是提示不支援 VT‑x。要解法就必須在第一層 Hyper‑V 上為目標 VM 開啟巢狀虛擬化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, D-Q1, D-Q2

Q5: 什麼是 VT‑x/AMD‑V？
- A簡: x86 硬體輔助虛擬化指令集，提供指令與模式支援高效安全地跑 VM。
- A詳: Intel VT‑x 與 AMD‑V 是處理器提供的硬體輔助虛擬化擴充，讓 Hypervisor 能高效處理特權指令、位址轉換與中斷，降低陷入開銷並提升隔離性。若來賓 VM 未獲得此能力，二層虛擬化幾乎不可行。本文案例中，Hyper‑V 的巢狀虛擬化會將這些擴充暴露給來賓，解鎖 VM 內再開 VM 的可能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q4, B-Q2, D-Q1

Q6: 什麼是 Hyper‑V？以及本文中的角色？
- A簡: Microsoft 的 Hypervisor。本文透過其巢狀虛擬化支援，讓 VM 內再跑 VM 成為可能。
- A詳: Hyper‑V 是 Windows 的原生虛擬化平台，負責管理虛擬 CPU、記憶體與虛擬網路。Windows 10/Server 2016 起提供巢狀虛擬化預覽，使指定來賓 VM 可取得虛擬化擴充。文中先於主機層對目標 VM 啟用該功能，之後在來賓內改採 Hyper‑V 驅動建立 boot2docker 主機，避開 VirtualBox 在巢狀環境的相容性問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q11, B-Q2, C-Q1

Q7: 什麼是 Docker Machine？
- A簡: 跨環境建立 Docker 主機的 CLI，支援多種 driver，如 Hyper‑V、VirtualBox、雲端。
- A詳: Docker Machine 提供一組一致的命令介面，透過不同 Driver 將 VM 建立與設定流程一般化。它能在本機虛擬化軟體（Hyper‑V、VirtualBox、VMware）或公有雲（AWS、Azure）上自動建立 boot2docker 主機，並配置網路、憑證與遠端存取。本文使用 -d hyperv Driver 成功於來賓 Windows VM 建立 Docker 主機。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q16, B-Q4, C-Q5

Q8: 什麼是 Kitematic？
- A簡: Docker 的圖形化介面，像 App Store 瀏覽、下載並管理容器，Toolbox 內建。
- A詳: Kitematic 是 Docker 提供的桌面 GUI，讓使用者以搜尋、點選的方式發現映像、建立與管理容器，降低命令列門檻。Toolbox 安裝會一併提供 Kitematic，但其預設假設 VirtualBox 為後端。在巢狀環境中 VirtualBox 可能失敗，需修改其底層設定讓它改用 docker‑machine 的 Hyper‑V 流程，或先以命令列替代。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q11, C-Q9, D-Q9

Q9: 什麼是 Boot2Docker？
- A簡: 針對 Docker 主機最佳化的輕量 Linux ISO，可光碟開機、免安裝。
- A詳: boot2docker 是極精簡的 Linux 發行版，專為承載 Docker Daemon 而設計。它以 ISO 形式開機，磁碟依賴最小，開機後由 docker‑machine 自動注入 SSH 憑證與網路設定，讓 Windows 客戶端能安全地遠端操控。適合快速建立暫用的 Docker 開發/測試主機。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q5, C-Q5, C-Q7

Q10: 什麼是 Docker Quickstart Terminal？
- A簡: Toolbox 提供的一鍵初始化終端，預設以 VirtualBox 建立並連線 Docker 主機。
- A詳: Docker Quickstart Terminal 會自動呼叫 docker‑machine 建立名為 default 的 boot2docker VM（預設 Driver 為 VirtualBox），完成後設定環境變數並開啟與主機的連線。在巢狀虛擬化場景，這個預設流程常因 VirtualBox 不支援而失敗，需手動改用 Hyper‑V Driver。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q11, B-Q7, D-Q2

Q11: 為什麼本文改用 Hyper‑V 取代 VirtualBox？
- A簡: 在巢狀虛擬化預覽期，VirtualBox 在 VM 內啟動失敗；改用 Hyper‑V 成功。
- A詳: 文中實測在來賓 Windows VM 內，使用 VirtualBox 啟動 boot2docker 會出錯（無法取得 VT‑x）。改走 docker‑machine 的 -d hyperv 後，成功建立與啟動 VM，包含網路與憑證設定皆自動完成。這說明於 Hyper‑V 的巢狀架構下，仍以 Hyper‑V 來承載第二層 VM 最相容。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q4, C-Q5, D-Q1

Q12: 啟用 Nested Virtualization 的先決條件是？
- A簡: Windows 10565+、Intel VT‑x、至少 4GB RAM、預覽功能不建議生產用。
- A詳: 要在 Hyper‑V 啟用巢狀虛擬化，軟硬體須齊備：Windows 版本需為 10565 以上（含 10586）、CPU 為 Intel 且支援 VT‑x、為來賓 VM 預留至少 4GB 記憶體。該功能仍為 Preview，僅供學習與測試，不建議用於生產工作負載。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q13, C-Q1, D-Q10

Q13: 啟用 Nested Virtualization 的限制有哪些？
- A簡: 不支援動態記憶體與檢查點，需啟用 MAC 位址欺騙等設定，預覽階段。
- A詳: 巢狀虛擬化預覽期有若干限制：來賓 VM 不支援 Dynamic Memory，需改為固定配額；Checkpoints 功能不可用；網路端需開啟 MAC Address Spoofing 以讓第二層 VM 正常交換封包。以上限制需在建立前規劃，避免中途更動造成中斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q21, D-Q7, D-Q5

Q14: 微服務與 Docker 有何關聯？
- A簡: 微服務推動容器落地；學習 Docker 常需先在 VM 中試驗與模擬環境。
- A詳: 微服務架構主張將系統切分為小型自治服務，容器提供快速啟動、隔離與便攜等特性，契合微服務需求。為在不影響實體環境前提下學習與驗證，常在 VM 中先搭起 Docker 環境。文中即展示如何於 VM 內建立 Docker 主機以進行研究與實驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q15, B-Q1

Q15: 為什麼要在 VM 裡使用 Docker Toolbox？
- A簡: 方便在隔離環境練習與研究，不動實體機；但需解決巢狀虛擬化問題。
- A詳: 研究新技術通常需要可重置、可隔離的環境。將 Docker Toolbox 置於 VM 內，可隨時重建或丟棄，避免污染主機系統；亦便於在筆電或共享環境中做課程與演示。限制是需處理巢狀虛擬化相容性與資源需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q13, D-Q2

Q16: Docker Machine 的 Driver 是什麼？
- A簡: 抽象不同虛擬化/雲端平台的介面，如 Hyper‑V、VirtualBox、AWS、Azure 等。
- A詳: Docker Machine Driver 是一層適配器，實作目標平台的 VM 生命週期與網路設定。例如 hyperv、virtualbox、vmware、amazonec2、azure 等。使用者僅需切換 -d 參數，即可把同一套建置流程搬到不同基礎設施，維持一致體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q14, C-Q5, C-Q8

Q17: Docker Client 與 Docker Host 如何溝通？
- A簡: 透過環境變數指定遠端位址與憑證，與 Host 的 Docker Daemon 通訊。
- A詳: docker‑machine env 會輸出一組環境變數（如主機位址、CA 與 client 憑證路徑）。設定後，docker 命令便不再連本機，而是經由網路連至該 boot2docker VM 上的 Docker Daemon。這種模式讓用戶端與主機解耦，便於在多台主機之間切換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q25, B-Q6, C-Q6

Q18: 什麼是 Docker Hub？
- A簡: 官方映像倉庫，Docker 客戶端可從此拉取如 hello‑world 的映像執行。
- A詳: Docker Hub 是公共的容器映像託管服務，收錄官方與社群維護的映像。執行 docker run hello‑world 時，若本地未快取對應映像，Docker 會連線至 Hub 下載（pull），完成後建立並啟動容器，輸出測試訊息以驗證端到端流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q12, B-Q16, C-Q7

Q19: 為何 Docker Quickstart Terminal 失敗？
- A簡: 因其預設走 VirtualBox，於 VM 內缺少可用 VT‑x，導致建立/啟動失敗。
- A詳: Quickstart Terminal 走的是 VirtualBox 流程，在 VM 內這條路經常因二層虛擬化不被支援而中斷，常見訊息為無法啟用 VT‑x 或啟動失敗。建議改用 docker‑machine -d hyperv 於來賓內建立主機，以符合 Hyper‑V 巢狀的支援狀態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q11, D-Q2

Q20: 什麼是 Hyper‑V 虛擬交換器（Virtual Switch）？
- A簡: Hyper‑V 的網路虛擬化元件，讓 VM 取得網路；建立 Docker Host 前須設定。
- A詳: Hyper‑V 透過虛擬交換器將 VM 接上實體或 NAT 網路。若來賓內未先建立 Virtual Switch，docker‑machine 建起來的 boot2docker VM 可能無網路。文中做法是在 Hyper‑V 管理員先建立一個交換器，再由 docker‑machine 自動掛接。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q4, D-Q3

Q21: 什麼是 MAC Address Spoofing？為何要開啟？
- A簡: 允許 VM 發送非自身 MAC 的封包。巢狀虛擬化網路拓撲下需開啟才能通。
- A詳: MAC Address Spoofing 是 Hyper‑V 虛擬網卡的安全選項。在巢狀虛擬化架構，第二層 VM 的封包會經由第一層來賓發出，常見情況需允許來賓轉發不同 MAC 的封包以讓下層 VM 正常通訊。MSDN 指南亦要求在啟用巢狀時開啟此設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q10, C-Q10, D-Q3

Q22: 什麼是「預覽（Preview）」功能？
- A簡: 尚在測試的功能，特性未穩定，不建議用於生產環境，有相容性風險。
- A詳: Preview（預覽）代表功能仍在開發與驗證中，介面與行為未完全定型。Hyper‑V 巢狀虛擬化於本文情境屬預覽，因此官方不建議上生產，實測也顯示與第三方如 VirtualBox 的相容性不足。應評估風險、做好備份，僅用於學習研究。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q13, D-Q10

Q23: VirtualBox 與 Hyper‑V 的主要差異（本文脈絡）？
- A簡: 本文情境下，VirtualBox 在巢狀環境常失敗；Hyper‑V 原生支援巢狀功能。
- A詳: 兩者皆為桌面虛擬化主流，但在 Hyper‑V 巢狀預覽階段，VirtualBox 於來賓內啟動第二層 VM 時常因缺少 VT‑x 而失敗；換用 Hyper‑V Driver 建立 VM 則運作良好。選擇時可依底層 Hypervisor 的支援度與相容性決定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q9, C-Q5, D-Q1

Q24: boot2docker 的特點與適用場景？
- A簡: 輕量、免安裝、隨開即用，適合快速建立 Docker Host 作開發與測試。
- A詳: boot2docker 以輕量化為核心，透過 ISO 掛載直接開機，開機流程會載入必要模組並由 docker‑machine 注入設定。其設計讓 VM 建置時間縮短、盤面影響小，十分適合開發與教學場景；不過如需長期生產使用，仍建議採更完整的 Linux 發行版。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q5, C-Q5

Q25: 為何要用 docker‑machine env 設定環境變數？
- A簡: 讓客戶端指向正確的 Docker 主機與證書，確保後續指令作用在目標 VM。
- A詳: 執行 docker‑machine env <name> 會輸出一組設定命令，內容包含 DOCKER_HOST、DOCKER_CERT_PATH 等。套用後，後續 docker run/ps 等命令才會對準剛建起的 boot2docker VM。若未設定，命令可能打到本機或其他主機，導致誤判。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, C-Q6, D-Q2

Q26: 替 VM 啟用 Nested Virtualization 的腳本做什麼？
- A簡: 檢查並設定該 VM 參數，開啟巢狀虛擬化所需的 Hyper‑V 選項與網路配置。
- A詳: Enable‑NestedVm.ps1 是 Microsoft 提供的輔助腳本。以管理員身分在 Hyper‑V 主機執行，輸入 -VmName 指定目標 VM。腳本會檢查版本、CPU 與 Hyper‑V 設定，調整包含 MAC Spoofing、記憶體配置等必要選項，最後啟用巢狀虛擬化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q1, D-Q4

Q27: -VmName 參數的意義是什麼？
- A簡: 指定要啟用巢狀虛擬化的目標 VM 名稱，逐台套用而非全域。
- A詳: 巢狀虛擬化並非全域開關，而是針對選定 VM 開啟。-VmName 參數讓腳本定位到正確的 VM 物件，僅對該 VM 調整設定與啟用能力。這樣的設計讓管理者能精準控制哪些 VM 可在內部再開 VM。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q26, C-Q1

Q28: Windows 版本需求為何？
- A簡: Windows 10/Server 2016 的 10565 以上版本才支援巢狀虛擬化。
- A詳: 依 MSDN，巢狀虛擬化需求至少為 Windows Insider build 10565。文中示範以 Windows 10 Enterprise 10586 實測成功。若版本過舊，請升級 OS 或改用支援版本，以免腳本或功能無法啟用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q10

Q29: 為何不先討論效能影響？
- A簡: 功能仍在預覽，實作細節與效能數據未公開，優先解決可用性問題。
- A詳: 文中聚焦於解法與可行性驗證。巢狀虛擬化內部實作（完全模擬或指令轉發）與效能折損未在官方文章詳述，且目前仍為預覽。待功能成熟再評估效能，現階段先確保在學習與測試中可用即可。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, A-Q22

Q30: 成功驗證 Docker 的最小步驟是？
- A簡: 建立主機、設定 env，執行 docker run hello‑world，看到成功訊息即通。
- A詳: 最小驗證路徑為：1) 以 docker‑machine create -d hyperv 建立 boot2docker；2) 依 docker‑machine env <name> 設定環境變數；3) 執行 docker run hello‑world。若能看到 hello‑world 輸出，代表客戶端成功連線主機並從 Docker Hub 拉取映像後啟動容器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q6, C-Q7, B-Q16

### Q&A 類別 B: 技術原理類

Q1: Docker Toolbox 如何在 Windows 上運作？
- A簡: 以 VirtualBox 建立 boot2docker VM，再透過 Docker Machine 配置與連線。
- A詳: 技術原理說明：Toolbox 集成 VirtualBox、Docker Machine 與 Kitematic。關鍵步驟或流程：Quickstart 觸發 docker‑machine 建立 default VM、下載 boot2docker.iso、啟動 VM 並注入憑證、輸出環境變數供客戶端使用。核心組件介紹：VirtualBox（虛擬化）、docker‑machine（生命週期管理）、boot2docker（OS）、Kitematic（GUI）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q10, B-Q7

Q2: Hyper‑V 巢狀虛擬化的機制是什麼？
- A簡: Hyper‑V 將硬體虛擬化擴充暴露給來賓，使其可再啟動 Hypervisor。
- A詳: 技術原理說明：L0 Hyper‑V 允許來賓 vCPU 使用 VT‑x，讓 L1 來賓可扮演 Hypervisor。關鍵步驟或流程：在主機為指定 VM 啟用巢狀、重啟來賓；來賓便可安裝 Hyper‑V 或其他 Hypervisor。核心組件介紹：L0 Hyper‑V、vCPU、VT‑x 指令集、L1 來賓 Hypervisor 與 L2 VM。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q5, B-Q15

Q3: 啟用巢狀虛擬化的執行流程為何？
- A簡: 於主機下載並以管理員執行腳本，對指定 VM 套用必要設定後啟用。
- A詳: 技術原理說明：由 PowerShell 腳本檢查 OS 版本、CPU、Hyper‑V 參數。關鍵步驟或流程：1) 下載 Enable‑NestedVm.ps1；2) 以 -VmName 指向目標 VM；3) 設定固定記憶體、開啟 MAC Spoofing；4) 套用巢狀功能。核心組件介紹：Hyper‑V 管理 API、PowerShell 腳本、VM 組態。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q1, D-Q5

Q4: Docker Machine 使用 Hyper‑V Driver 建立主機的流程？
- A簡: 建立 VHD 與 VM、掛接虛擬交換器、啟動 ISO、注入憑證，完成配置。
- A詳: 技術原理說明：Driver 把平台差異封裝為統一流程。關鍵步驟或流程：1) 建立 VM 與虛擬磁碟；2) 掛接 boot2docker.iso；3) 連結虛擬交換器；4) 開機後透過 SSH 注入鍵與設定；5) 註冊機器資訊。核心組件介紹：hyperv driver、boot2docker、虛擬交換器、SSH 憑證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q5, B-Q6

Q5: boot2docker 的開機與自動配置機制？
- A簡: ISO 載入核心與模組，開機後由 docker‑machine 注入 SSH 憑證與設定。
- A詳: 技術原理說明：以 ISO 載入精簡 Linux 到記憶體運行。關鍵步驟或流程：1) BIOS/UEFI 從 ISO 開機；2) 載入 Kernel 與 init；3) 啟動網路；4) docker‑machine 經 SSH 傳送憑證與 docker 設定；5) Docker Daemon 開始服務。核心組件介紹：boot2docker.iso、init、SSH、Docker Daemon。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q4, C-Q5

Q6: docker‑machine env 背後做了什麼？
- A簡: 產生並輸出連線所需環境變數與憑證路徑，供 shell 套用。
- A詳: 技術原理說明：docker‑machine 維護每台機器的連線設定。關鍵步驟或流程：1) 讀取機器的主機名/IP 與憑證位置；2) 以 shell 相容格式輸出環境變數；3) 使用者於 shell 套用後即指向該主機。核心組件介紹：機器目錄、憑證檔、DOCKER_HOST/DOCKER_CERT_PATH 與相關變數。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q6

Q7: Quickstart Terminal 的初始化流程與限制？
- A簡: 呼叫 docker‑machine 建立 default（VirtualBox），設定 env，巢狀下常失敗。
- A詳: 技術原理說明：Quickstart 封裝了建立 default VM 與環境設定。關鍵步驟或流程：1) 檢查/建立 default；2) 設定環境變數；3) 開啟終端。核心組件介紹：VirtualBox driver、boot2docker、環境變數。限制：巢狀環境多因缺 VT‑x 失敗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q19, D-Q2

Q8: Hyper‑V 虛擬交換器在網路連線中的角色？
- A簡: 提供 VM 上網的虛擬交換網橋；docker‑machine 會掛接在此。
- A詳: 技術原理說明：虛擬交換器把 VM 的 vNIC 接到實體或虛擬網路。關鍵步驟或流程：1) 建立 External/內部等交換器；2) VM 連結該交換器取得 IP；3) 第二層 VM 流量透過第一層轉發。核心組件介紹：Virtual Switch、vNIC、外部實體 NIC。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q4, D-Q3

Q9: 為何 VirtualBox 在巢狀環境可能無法啟動？
- A簡: 來賓未獲得 VT‑x/AMD‑V，或預覽期相容性不足，啟動第二層 VM 失敗。
- A詳: 技術原理說明：二層虛擬化需硬體輔助；若 L1 未提供，L2 無法啟動。關鍵步驟或流程：VirtualBox 啟動時檢測 VT‑x 失敗而中止。核心組件介紹：VirtualBox Hypervisor、VT‑x/AMD‑V、Hyper‑V 巢狀支援現況（預覽）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q1, D-Q2

Q10: MAC Address Spoofing 在巢狀網路裡如何工作？
- A簡: 允許第一層 VM 轉發第二層 VM 的 MAC 封包，確保流量可通達。
- A詳: 技術原理說明：Hyper‑V 預設阻擋非本機 MAC 的封包以防偽造。關鍵步驟或流程：在 L1 VM 的網卡啟用 MAC Spoofing 後，L2 VM 的封包可攜原 MAC 經 L1 轉發。核心組件介紹：vSwitch 轉發規則、vNIC 安全選項、L2 VM 流量路徑。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21, C-Q10, D-Q3

Q11: 為何禁止動態記憶體與檢查點？
- A簡: 避免 Hyper‑V 內部狀態變動干擾來賓 Hypervisor，維持穩定。
- A詳: 技術原理說明：L1 VM 的記憶體彈性調整/快照會影響 L2 Hypervisor 的時間與狀態假設。關鍵步驟或流程：改用固定記憶體、停用 Checkpoints，提供穩定基礎。核心組件介紹：Dynamic Memory、Checkpoints、來賓 Hypervisor 的穩定性需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q7

Q12: Docker Hub 的拉取與快取機制？
- A簡: 若本地無映像則從 Hub 下載，之後重用本地快取加速啟動。
- A詳: 技術原理說明：Docker 依據映像名稱查詢本地快取；缺少則連 Hub 下載各層。關鍵步驟或流程：解析名稱→檢查快取→下載層→驗證→組裝映像→啟動容器。核心組件介紹：Registry、Layer、Local Cache、Content Hash。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q7, B-Q16

Q13: Docker 主機的憑證與連線保護如何配置？
- A簡: docker‑machine 建立時生成憑證，注入主機並保存在本機，透過環境變數使用。
- A詳: 技術原理說明：以憑證保護客戶端至主機的遠端 API。關鍵步驟或流程：1) 產生 CA 與客戶端憑證；2) 將伺服端憑證安裝於主機；3) 本機保存連線資訊；4) env 輸出變數供 shell 使用。核心組件介紹：CA/Client/Server 憑證、DOCKER_CERT_PATH、DOCKER_TLS_VERIFY。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q17, B-Q6

Q14: Docker Machine Driver 架構如何設計？
- A簡: 以可插拔介面實作不同平台的 VM 生命週期與網路操作。
- A詳: 技術原理說明：Driver 透過統一接口實作 create/start/stop/remove 等操作。關鍵步驟或流程：依 Driver 初始化平台 API→建立 VM→設定網路/憑證→回傳連線參數。核心組件介紹：Driver 介面、平台 API（Hyper‑V、VirtualBox、雲端）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q4

Q15: L0/L1/L2 Hypervisor 與 VM 的層次關係？
- A簡: 實體層為 L0 Hypervisor；來賓內啟動的為 L1；其上再跑 VM 為 L2。
- A詳: 技術原理說明：巢狀虛擬化將虛擬化層級擴展。關鍵步驟或流程：L0 授權 L1 使用虛擬化擴充→L1 啟動自己的 Hypervisor→L2 VM 在 L1 上運作。核心組件介紹：L0 Hyper‑V、L1 Guest Hypervisor、L2 Guest VM、vCPU 擴充。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q3, B-Q2

Q16: hello‑world 容器的執行時序為何？
- A簡: 拉取映像、建立容器、執行程式並輸出訊息後退出。
- A詳: 技術原理說明：docker run 觸發映像檢查與容器生命週期。關鍵步驟或流程：1) 檢查本地是否有 hello‑world 映像；2) 若無則到 Hub 拉取；3) 建立容器並執行入口程式；4) 輸出測試訊息；5) 容器退出。核心組件介紹：映像、容器、入口點、日誌輸出。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q30, C-Q7, B-Q12

Q17: 在主機、來賓與第二層主機間資源如何分配與協調？
- A簡: 主機分配固定資源給來賓；來賓再切給第二層 VM，需預留足夠記憶體。
- A詳: 技術原理說明：巢狀結構中的資源逐層分配。關鍵步驟或流程：L0 為 L1 配置固定 CPU/RAM→L1 再配置給 L2；若 L1 記憶體不足，L2 建立/啟動將受影響。核心組件介紹：固定記憶體、CPU 配額、虛擬交換器帶寬。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q13, D-Q6

Q18: boot2docker 的無碟（diskless）設計如何達成？
- A簡: 以 ISO 開機載入系統於記憶體，最小化磁碟依賴，靠工具注入設定。
- A詳: 技術原理說明：以只讀 ISO 與內存檔系統提供系統檔，狀態由外部工具注入。關鍵步驟或流程：載入核心→掛載 RAMFS→網路啟動→注入設定→啟動 Docker。核心組件介紹：ISO、initrd/ramfs、SSH 注入流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, B-Q5

Q19: Kitematic 為何預設 VirtualBox，如何換用 Hyper‑V 的思路？
- A簡: 其底層呼叫 docker‑machine 以 VirtualBox Driver；可改成使用 hyperv。
- A詳: 技術原理說明：Kitematic 透過底層命令建立連線與主機。關鍵步驟或流程：找到其呼叫 docker‑machine 的位置，將 driver 從 virtualbox 改為 hyperv；確保已有 Hyper‑V 交換器與可用主機。核心組件介紹：Kitematic 設定、docker‑machine、hyperv driver。實作細節請參考專文。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, C-Q9, D-Q9

Q20: 使用雲端 Driver 建立主機的高階流程？
- A簡: 換用相對應 Driver，提供憑證與網路參數，遠端建立並連線主機。
- A詳: 技術原理說明：Driver 將雲端 API 抽象成相同步驟。關鍵步驟或流程：以 -d 選定 amazonec2/azure 等→提供帳密/金鑰/網路選項→遠端建立 VM 並配置 Docker→輸出連線變數。核心組件介紹：雲端 Driver、雲 API 憑證、遠端主機。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, C-Q8

### Q&A 類別 C: 實作應用類

Q1: 如何在 Hyper‑V 主機上為指定 VM 啟用巢狀虛擬化？
- A簡: 以管理員執行 Enable‑NestedVm.ps1，指定 -VmName，調整設定後啟用。
- A詳: 具體實作步驟：1) 以系統管理員開啟 PowerShell；2) 下載腳本：Invoke-WebRequest https://raw.githubusercontent.com/Microsoft/Virtualization-Documentation/master/hyperv-tools/Nested/Enable-NestedVm.ps1 -OutFile ~/Enable-NestedVm.ps1；3) 執行：~/Enable-NestedVm.ps1 -VmName "你的VM名"。注意事項：來賓記憶體≥4GB、關閉動態記憶體、啟用 MAC Spoofing。本功能為預覽，勿用於生產。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q26, D-Q5

Q2: 如何在來賓 Windows VM 內安裝 Docker Toolbox？
- A簡: 下載並以預設值安裝；注意 Quickstart 會用 VirtualBox，先準備改用 Hyper‑V。
- A詳: 具體實作步驟：1) 於來賓 VM 下載 Docker Toolbox 安裝程式；2) 以預設選項安裝（含 Docker Machine、Kitematic）；3) 暫勿使用 Quickstart（預設 VirtualBox 會失敗），改走手動流程。注意事項：安裝完成後將改用 hyperv driver 建立主機，避免 VirtualBox 相容性問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q11, C-Q5

Q3: 如何移除 VirtualBox 並啟用 Hyper‑V？
- A簡: 控制台移除 VirtualBox，啟用 Windows 功能中的 Hyper‑V，重開機生效。
- A詳: 具體實作步驟：1) 於「程式與功能」解除安裝 Oracle VirtualBox；2) 開啟「開啟或關閉 Windows 功能」，勾選「Hyper‑V」；3) 重開機。注意事項：Hyper‑V 與某些虛擬化同時啟用可能衝突；巢狀情境下由 Hyper‑V 提供第二層 VM 能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q11, D-Q1

Q4: 如何建立 Hyper‑V 虛擬交換器供 Docker 主機使用？
- A簡: 在 Hyper‑V 管理員建立 External Switch，連到實體網卡，供 VM 使用。
- A詳: 具體實作步驟：1) 開啟 Hyper‑V 管理員→Virtual Switch Manager；2) 新增 External 型交換器，選擇對應實體 NIC；3) 套用後供後續 VM 使用。注意事項：若無交換器，docker‑machine 建立主機可能無網路；切換網卡時需重新連結。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q8, D-Q3

Q5: 如何用 Hyper‑V Driver 建立 boot2docker 主機？
- A簡: 執行 docker‑machine create -d hyperv <name>，等待自動配置完成。
- A詳: 具體實作步驟：1) 開啟命令列；2) 執行 docker-machine create -d hyperv boot2docker；3) 等待建立 VM、掛接交換器、注入憑證完成。關鍵程式碼：docker-machine create -d hyperv boot2docker。注意事項：若有多個交換器，請確保預設交換器正確；建立需數分鐘。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q4, C-Q4

Q6: 如何設定 Docker 客戶端連到剛建立的主機？
- A簡: 執行 docker‑machine env <name>，依提示套用環境變數，再操作 docker。
- A詳: 具體實作步驟：1) 執行 docker-machine env boot2docker；2) 依終端提示設定環境變數（將輸出的命令貼回執行）；3) 驗證 docker ps 是否成功回應。關鍵指令：docker-machine env boot2docker。注意事項：每次開新終端需重設；確認變數指向正確主機。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q17, A-Q25, B-Q6

Q7: 如何以 hello‑world 驗證整體環境？
- A簡: 執行 docker run hello‑world，觀察提示訊息確認拉取與執行成功。
- A詳: 具體實作步驟：1) 在已設定 env 的終端執行 docker run hello-world；2) 首次會從 Docker Hub 拉取映像；3) 成功後輸出教學訊息。關鍵指令：docker run hello-world。注意事項：若拉取逾時，檢查網路與交換器；若找不到主機，重設 env。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, A-Q30, B-Q16

Q8: 如何用 Docker Machine 切換到雲端 Driver（範例）？
- A簡: 把 -d 換成雲端名稱並提供憑證與參數；例如 azure、amazonec2。
- A詳: 具體實作步驟：1) 準備雲端帳戶金鑰與網路設定；2) 以 docker-machine create -d azure <name> 或 -d amazonec2 <name> 建立；3) 依指引提供必要參數。關鍵指令：docker-machine create -d <driver> <name>。注意事項：雲端參數繁多，此處僅示意，實務請依官方文件配置。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q20

Q9: 如何修改 Kitematic 讓它在 Windows 10 使用 Hyper‑V？
- A簡: 依參考文章調整其底層 docker‑machine 呼叫，把 VirtualBox 換成 hyperv。
- A詳: 具體實作步驟：1) 參考專文說明定位 Kitematic 呼叫 docker‑machine 的區段；2) 將 Driver 設為 hyperv；3) 確認已建立可用的 Hyper‑V 主機；4) 測試 Kitematic 是否能連線。關鍵變更：driver 從 virtualbox → hyperv。注意事項：變更需自行承擔風險；參考文：http://agup.tech/2015/08/14/hacking-at-kitematic-with-hyper-v-on-windows-10/
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q19, D-Q9

Q10: 如何在 Hyper‑V 啟用 MAC Address Spoofing？
- A簡: 於目標 VM 的網路介面「進階功能」中勾選 MAC 位址欺騙。
- A詳: 具體實作步驟：1) 關閉目標 VM；2) 在 Hyper‑V 管理員選該 VM→網路介面→進階功能；3) 勾選「啟用 MAC 位址欺騙」；4) 儲存並重開 VM。注意事項：此設定對巢狀網路通訊必要；變更需停機進行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, B-Q10, D-Q3

### Q&A 類別 D: 問題解決類

Q1: 遇到「VT‑x/AMD‑V 不可用」或 VirtualBox 啟動失敗怎麼辦？
- A簡: 改用 Hyper‑V 方案：在主機啟用巢狀，來賓內以 -d hyperv 建主機。
- A詳: 問題症狀描述：VirtualBox 啟動第二層 VM 失敗，提示未支援 VT‑x/AMD‑V。可能原因分析：巢狀支援未啟用、VirtualBox 與預覽期 Hyper‑V 相容性不足。解決步驟：1) 在主機以腳本啟用巢狀；2) 來賓內移除 VirtualBox、啟用 Hyper‑V；3) 用 docker-machine -d hyperv 建立主機。預防措施：巢狀場景優先選用 Hyper‑V Driver。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q11, C-Q3

Q2: Docker Quickstart Terminal 建立 default 失敗怎麼處理？
- A簡: 跳過 Quickstart，改手動用 docker‑machine 的 Hyper‑V Driver 建立。
- A詳: 問題症狀描述：Quickstart 卡在建立/啟動 default 階段或報錯。可能原因分析：預設走 VirtualBox，巢狀環境無 VT‑x。解決步驟：1) 關閉 Quickstart；2) 以 docker-machine create -d hyperv <name> 建立；3) docker-machine env <name> 設定；4) 驗證。預防措施：於來賓僅裝 Toolbox CLI，不使用 Quickstart 預設流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q19, C-Q5

Q3: 第二層 Docker 主機無法上網或無法拉取映像？
- A簡: 建立 Hyper‑V 虛擬交換器並啟用 MAC Spoofing，確保網路暢通。
- A詳: 問題症狀描述：docker run hello‑world 無法拉取、ping 不通。可能原因分析：未建立虛擬交換器、未啟用 MAC Spoofing 導致封包被阻擋。解決步驟：1) 建立 External Switch；2) 在 L1 VM 啟用 MAC Spoofing；3) 重啟 L2 主機。預防措施：建機前先配置交換器並檢查連線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, A-Q21, C-Q4, C-Q10

Q4: 執行 Enable‑NestedVm.ps1 提示權限不足或找不到命令？
- A簡: 以系統管理員開啟 PowerShell，確保可執行腳本，再重試。
- A詳: 問題症狀描述：執行腳本遭拒或無效。可能原因分析：未以系統管理員執行、腳本執行權限限制。解決步驟：1) 以管理員身分開啟 PowerShell；2) 確認路徑正確並重新執行下載與啟用命令。預防措施：在主機以管理權限操作，並確認網路可下載腳本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q26, C-Q1

Q5: 啟用巢狀後仍無法建立第二層 VM，該檢查什麼？
- A簡: 確認記憶體≥4GB、關閉動態記憶體、開啟 MAC Spoofing，符合需求。
- A詳: 問題症狀描述：建立 L2 VM 仍失敗或啟動不穩。可能原因分析：資源不足、動態記憶體干擾、網路安全設定未開。解決步驟：1) 將 L1 VM 調為固定記憶體≥4GB；2) 開啟 MAC Spoofing；3) 重新建立 L2 主機。預防措施：建置前依需求檢查清單逐項確認。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q13, C-Q10

Q6: 來賓 VM 記憶體不足導致建立或啟動緩慢/失敗？
- A簡: 提高來賓 VM 記憶體配額（≥4GB），並避免同時啟太多 VM。
- A詳: 問題症狀描述：建機緩慢、啟動逾時或 OOM。可能原因分析：L1 VM 記憶體不足以容納 L2。解決步驟：1) 提升 L1 VM 記憶體至 4GB 以上；2) 關閉不必要的 VM；3) 重試建立。預防措施：規劃資源配額並保留餘裕。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q17

Q7: 開啟動態記憶體造成第二層 VM 不穩定或異常？
- A簡: 停用動態記憶體，改用固定記憶體配置，重啟再試。
- A詳: 問題症狀描述：L2 主機偶發失聯或性能抖動。可能原因分析：L1 記憶體動態調整造成 L2 Hypervisor 行為不可預期。解決步驟：1) 關閉 L1 VM；2) 停用 Dynamic Memory；3) 設定固定大小；4) 重啟並重試。預防措施：巢狀場景固定記憶體。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q11

Q8: docker‑machine 建立失敗找不到可用 Hyper‑V 交換器？
- A簡: 先建立交換器，或在建立命令中指定目標交換器名稱後重試。
- A詳: 問題症狀描述：建機失敗與網路相關錯誤。可能原因分析：系統中沒有可用交換器。解決步驟：1) 於 Hyper‑V 管理員建立 External Switch；2) 再執行 docker‑machine create -d hyperv；3) 如有多個交換器，確保預設正確。預防措施：建機前先建交換器並驗證網路。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q4, C-Q5

Q9: Kitematic 一直使用 VirtualBox，無法用 Hyper‑V？
- A簡: 暫不用 Kitematic 或參考文修改其設定，改走 Hyper‑V。
- A詳: 問題症狀描述：Kitematic 啟動 default（VirtualBox）失敗。可能原因分析：預設綁定 VirtualBox。解決步驟：1) 先用命令列與 hyperv driver 操作；2) 依參考文修改 Kitematic 的底層呼叫；3) 驗證連線。預防措施：在巢狀環境避免依賴 Kitematic 預設流程。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q19, C-Q9

Q10: Windows 版本過舊，無法啟用巢狀虛擬化？
- A簡: 升級至 10565+ 或 Windows 10 10586；不符合者暫無法使用。
- A詳: 問題症狀描述：腳本報版本不支援或功能不存在。可能原因分析：OS 版本低於需求。解決步驟：1) 查詢版本；2) 升級至 Windows 10/Server 2016 支援版本（如 10586）；3) 再次啟用。預防措施：規劃前先確認版本與 CPU 條件（Intel VT‑x）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q28

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Docker Toolbox？
    - A-Q2: 為什麼在 Windows 需要透過 VM 才能跑 Docker？
    - A-Q3: 什麼是 Nested Virtualization（巢狀虛擬化）？
    - A-Q4: 為何在 VM 內無法再建立 VM？
    - A-Q5: 什麼是 VT‑x/AMD‑V？
    - A-Q6: 什麼是 Hyper‑V？以及本文中的角色？
    - A-Q7: 什麼是 Docker Machine？
    - A-Q9: 什麼是 Boot2Docker？
    - A-Q10: 什麼是 Docker Quickstart Terminal？
    - A-Q18: 什麼是 Docker Hub？
    - B-Q1: Docker Toolbox 如何在 Windows 上運作？
    - B-Q6: docker‑machine env 背後做了什麼？
    - C-Q5: 如何用 Hyper‑V Driver 建立 boot2docker 主機？
    - C-Q6: 如何設定 Docker 客戶端連到剛建立的主機？
    - C-Q7: 如何以 hello‑world 驗證整體環境？

- 中級者：建議學習哪 20 題
    - A-Q11: 為什麼本文改用 Hyper‑V 取代 VirtualBox？
    - A-Q12: 啟用 Nested Virtualization 的先決條件是？
    - A-Q13: 啟用 Nested Virtualization 的限制有哪些？
    - A-Q20: 什麼是 Hyper‑V 虛擬交換器（Virtual Switch）？
    - A-Q21: 什麼是 MAC Address Spoofing？為何要開啟？
    - B-Q2: Hyper‑V 巢狀虛擬化的機制是什麼？
    - B-Q3: 啟用巢狀虛擬化的執行流程為何？
    - B-Q4: Docker Machine 使用 Hyper‑V Driver 建立主機的流程？
    - B-Q5: boot2docker 的開機與自動配置機制？
    - B-Q8: Hyper‑V 虛擬交換器在網路連線中的角色？
    - B-Q9: 為何 VirtualBox 在巢狀環境可能無法啟動？
    - B-Q11: 為何禁止動態記憶體與檢查點？
    - B-Q12: Docker Hub 的拉取與快取機制？
    - C-Q1: 如何在 Hyper‑V 主機上為指定 VM 啟用巢狀虛擬化？
    - C-Q3: 如何移除 VirtualBox 並啟用 Hyper‑V？
    - C-Q4: 如何建立 Hyper‑V 虛擬交換器供 Docker 主機使用？
    - D-Q1: 遇到「VT‑x/AMD‑V 不可用」或 VirtualBox 啟動失敗怎麼辦？
    - D-Q2: Docker Quickstart Terminal 建立 default 失敗怎麼處理？
    - D-Q3: 第二層 Docker 主機無法上網或無法拉取映像？
    - D-Q5: 啟用巢狀後仍無法建立第二層 VM，該檢查什麼？

- 高級者：建議關注哪 15 題
    - A-Q22: 什麼是「預覽（Preview）」功能？
    - A-Q23: VirtualBox 與 Hyper‑V 的主要差異（本文脈絡）？
    - A-Q24: boot2docker 的特點與適用場景？
    - A-Q29: 為何不先討論效能影響？
    - B-Q10: MAC Address Spoofing 在巢狀網路裡如何工作？
    - B-Q13: Docker 主機的憑證與連線保護如何配置？
    - B-Q14: Docker Machine Driver 架構如何設計？
    - B-Q15: L0/L1/L2 Hypervisor 與 VM 的層次關係？
    - B-Q16: hello‑world 容器的執行時序為何？
    - B-Q17: 在主機、來賓與第二層主機間資源如何分配與協調？
    - B-Q18: boot2docker 的無碟（diskless）設計如何達成？
    - B-Q19: Kitematic 為何預設 VirtualBox，如何換用 Hyper‑V 的思路？
    - B-Q20: 使用雲端 Driver 建立主機的高階流程？
    - C-Q8: 如何用 Docker Machine 切換到雲端 Driver（範例）？
    - C-Q9: 如何修改 Kitematic 讓它在 Windows 10 使用 Hyper‑V？