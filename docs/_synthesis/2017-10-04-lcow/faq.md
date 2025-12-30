---
layout: synthesis
title: "LCOW Labs: Linux Container On Windows"
synthesis_type: faq
source_post: /2017/10/04/lcow/
redirect_from:
  - /2017/10/04/lcow/faq/
---

# LCOW Labs: Linux Container On Windows

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 LCOW（Linux Containers on Windows）？
- A簡: LCOW 讓 Windows 透過 Hyper-V 容器與 LinuxKit 執行原生 Linux 容器，達成單機混合 OS 開發與測試。
- A詳: LCOW 是 Microsoft 與 Docker 合作的能力，讓 Windows 以 Hyper-V 容器啟動一個精簡 Linux 環境（常以 LinuxKit/Ubuntu 作為 Utility VM），在其中原生執行 Linux 容器。對開發者而言，一台 Windows 機能直接跑 Linux 映像，無需傳統完整 VM。它強調更好的相容性與維運簡化，並擴大容器支援範圍，便於混合 OS 架構的單機實驗與持續整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q4, B-Q1

A-Q2: LCOW 的核心價值是什麼？
- A簡: 降低混合 OS 開發摩擦，提升相容性與啟動效率，簡化 Windows 對 Linux 工作負載的支援。
- A詳: 核心價值在於「一台 Windows，原生跑 Linux 容器」。透過 Hyper-V 容器隔離與 LinuxKit 提供的最小化 Linux 環境，LCOW 兼顧相容性與啟動效率。對團隊而言，無需切換雙機或笨重 VM，能在同機驗證 Linux 與 Windows 工作負載，縮短回饋周期，並為之後接軌 Swarm/Kubernetes 等多平台編排做好準備。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q17, B-Q3

A-Q3: 為什麼 Microsoft 推出 LCOW？
- A簡: 為縮小 Windows 與 Linux 界線，強化跨平台相容，支援混合容器場景，提升開發與營運效率。
- A詳: 微軟目標是讓開發者在 Windows 平台上無縫操作 Linux 工作負載，減少跨 OS 帶來的工具鏈與環境差異。相較於先前僅透過 VM 或 WSL 的方式，LCOW 以 Hyper-V 容器承載 LinuxKit，提供更一致、可維運的容器體驗，也利於 Windows 容器在企業情境與編排器中的整合與擴展。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1, B-Q5

A-Q4: LCOW 與 WSL（Windows Subsystem for Linux）有何差異？
- A簡: WSL 轉譯系統呼叫，LCOW 以 Hyper-V 啟 Linux 環境；LCOW 相容性與容器整合更佳。
- A詳: WSL 透過 Windows 核心的系統呼叫轉譯層執行 Linux 應用，非完整 Linux 核心；LCOW 則在 Hyper-V 容器內啟動最小 Linux（LinuxKit/Ubuntu），以原生容器方式運行。因而 LCOW 對 Linux 映像與容器工作流相容性更高，亦利於與 Docker 生態與編排器結合；WSL 偏向工具與使用者空間體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q14, B-Q5

A-Q5: LCOW 與傳統在 Windows 上以 VM 跑 Linux 的差別？
- A簡: 傳統 VM 較重且慢；LCOW 以 Hyper-V 容器啟動精簡 Linux，啟動更快、整合度更高。
- A詳: 傳統 VM 需啟整套 Linux 作業系統，資源與啟動時間較大；LCOW 用 Hyper-V 容器啟一個最小 Linux Utility VM，專為容器執行設計，啟動秒級且與 Docker 堆疊緊密整合。對開發者，LCOW 可直接用 Docker CLI 管理 Linux 容器，而非改切換至完整 VM 的另套管理與網路堆疊。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q3, B-Q5

A-Q6: 什麼是 Hyper-V Container？
- A簡: 一種以 Hyper-V 供給每個容器專屬 VM 隔離的容器執行模式，增強隔離與相容性。
- A詳: Hyper-V 容器透過虛擬化為容器提供專屬 Utility VM，容器進程在其內執行，與主機核心隔離。對 Windows 容器是提升隔離、對 LCOW 則使 LinuxKit 能在 Windows 上原生跑 Linux 容器。它兼顧容器的管理介面與 VM 的隔離與相容性優勢，啟動速度較傳統 VM 快。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q6, B-Q13

A-Q7: LinuxKit 是什麼？為何用在 LCOW？
- A簡: LinuxKit 是可組裝的最小 Linux 發行版，用以打造容器專用的精簡系統。
- A詳: LinuxKit 由 Docker 推出，用 YAML 組裝可重現的、容器友好的最小 Linux 系統，採組件化、不可變設計。LCOW 借助 LinuxKit 提供體積小、啟動快且安全的 Utility VM 作為 Linux 核心環境，讓 Windows 能原生跑 Linux 容器，同時減少維運負擔與攻擊面。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, B-Q1, A-Q5

A-Q8: LCOW 與 Windows Container 的關係？能同時支援嗎？
- A簡: LCOW 讓 Windows 跑 Linux 容器；預覽期同一 daemon 暫不並行支援兩者。
- A詳: LCOW 是在 Windows 上支援 Linux 容器的能力；Windows Container 是以 Windows 基底映像的容器。文章所述預覽階段，同一個支援 LCOW 的 Docker daemon 尚不能同時跑 Windows 映像，需用預設 daemon 跑 Windows Container，或連 LCOW daemon 跑 Linux 容器，兩者分開運行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, D-Q1, C-Q5

A-Q9: Docker for Windows 的多引擎情境是什麼？
- A簡: 預設 daemon 可切換 Linux/Windows 模式；另可增設一個 LCOW daemon 供 Linux 容器。
- A詳: 文章環境同時有三套：Docker for Windows 預設 daemon（在 UI 於 Linux 容器模式時，背後是 Moby VM；切至 Windows 模式則為 Windows 容器），以及額外手動啟動的支援 LCOW 的 dockerd。使用者需藉由 -H 指定連線目標 daemon，依需求在不同引擎上運行相對應容器工作負載。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q8, B-Q15

A-Q10: 為什麼要用 -H 指定 npipe 來連 LCOW daemon？
- A簡: 因為 LCOW daemon 另開在自定 Named Pipe，需要用 -H 指向正確端點。
- A詳: 在 Windows 上，Docker Remote API 可透過 Named Pipe 提供。LCOW 測試環境的 dockerd 以 npipe://./pipe/docker_lcow 提供服務，與預設 daemon 不同。故需以 -H npipe:////./pipe//docker_lcow 或設定 DOCKER_HOST 指向該管道，讓 Docker CLI 與 LCOW daemon 通訊並操作 Linux 容器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, B-Q10, C-Q2

A-Q11: Nano Server 與 Server Core 基底映像有何差異？
- A簡: Nano 更精簡、無 GUI，適合 .NET Core 等；Server Core 功能較全，體積較大。
- A詳: Nano Server 面向雲原生，移除 GUI 與多數元件，體積極小、啟動快，適合 .NET Core、微服務；Server Core 保留較多 Win32 與系統元件，適合需較廣 API 的應用。文章指 Nano 由約 330MB 降至 80MB，Server Core 亦縮小 20%，有助於傳輸、啟動與部署效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q12, D-Q10

A-Q12: 為何減少基底映像大小很重要？
- A簡: 降低拉取時間與儲存成本，縮短部署啟動時間，提升交付效率。
- A詳: 映像越小，CI/CD 拉取與佈署越快，網路壓力與儲存消耗更低；啟動時間亦受益。文章示例 Nano Server 大幅縮小至 ~80MB，Server Core 減少 20%，實務上可明顯縮短新節點預熱與迭代周期，增進開發體驗與生產環境滾動更新效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q10, B-Q3, B-Q12

A-Q13: 什麼是 SMB Volume 掛載？好處是什麼？
- A簡: 直接把 SMB 共用掛入容器作 volume，便於存取共用檔案與資料。
- A詳: SMB 是 Windows 常見檔案分享協定。容器支援 SMB volume 後，可直接將 \\server\share 掛載到容器檔案系統，便捷地取得共用設定、日誌或資料。對 Demo、跨節點共用與資料外掛特別實用，不再受限於僅能掛主機本地資料夾的尷尬情境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, D-Q9, B-Q11

A-Q14: 為什麼不同 daemon 的容器仍可互 ping？
- A簡: 因為都連至同主機的虛擬交換器與 NAT 網段，IP 層仍可路由與互通。
- A詳: 雖由不同 daemon 管理，兩者都在同台 Windows 主機上，背後由 HNS/Hyper-V vSwitch 建立 NAT 網路，通常分配同一或路由可達的私網段。故以 IP 互 ping 可通。但因不屬同一 Docker 網路/daemon，無共享 Docker DNS/服務發現，名稱解析與 --link 無法跨 daemon 使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q3

A-Q15: 為何不同 daemon 間無法用 --link 或 DNS 互找？
- A簡: Docker 服務發現只作用於同一 daemon 與其網路堆疊，跨 daemon 無共享控制平面。
- A詳: --link 與 Docker 內建 DNS/服務發現由該 daemon 的網路控制面維護，僅對其管理的容器生效。不同 daemon 擁有獨立網路命名與記錄，不會相互同步。因此跨 daemon 需以 IP、固定 host 檔或外部 DNS/服務註冊機制協調，而非仰賴內建連結功能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q4, C-Q6

A-Q16: hello-world 測試有何意義？
- A簡: 驗證拉取與執行管線與權限無誤，檢視容器啟動時間與 LCOW 可用性。
- A詳: hello-world 是最小化測試映像，確認客戶端到 daemon 的連線、Registry 拉取、鏡像展開、容器啟動與輸出皆正常。文章示約五秒完成，顯示 LCOW 透過 Hyper-V + LinuxKit 的啟動效率。做為初學與環境健檢，能快速識別網路、存儲或虛擬化層是否配置正確。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, B-Q3, D-Q5

A-Q17: LCOW 對混合 OS 開發機的價值是什麼？
- A簡: 一機同時開發驗證 Linux/Windows 工作負載，簡化測試與整合，節省硬體與時間。
- A詳: 對需整合 Linux NGINX 與 Windows .NET 的團隊，LCOW 使 Windows 開發機直接跑 Linux 容器，減少多機/VM 切換與網路複雜度。雖預覽期有同 daemon 限制，但已可藉多 daemon 單機驗證跨 OS 通訊與行為，縮短回饋，提升 PoC 與教學展示效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, A-Q9, B-Q16

A-Q18: Docker for Windows Edge 版與 LCOW 有何關聯？
- A簡: 文章測試採 Edge 版與自建 LCOW daemon，Edge 提供實驗功能較新。
- A詳: Edge（現稱 Experimental/Preview）通道較快提供新功能，利於嘗試 LCOW 等特性。文中使用 Docker for Windows Edge 作為預設 daemon，再另行從 GitHub 取得支援 LCOW 的 dockerd，兩者並存。此組合適合實驗，但非穩定生產設定，需留意兼容性與崩潰風險。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q9, B-Q24

A-Q19: Windows 10 Insider 1709 與 LCOW 的關聯？
- A簡: 文中於 1709 預覽上實測 LCOW，顯示該版本開始提供所需基礎能力。
- A詳: LCOW 涉及 Hyper-V、HNS 與容器堆疊的改動，需對應的 Windows 版本支援。文章在 1709（OS Build 16299）Insider 上以 Edge 與 LCOW dockerd 驗證基本可行性。此時仍屬預覽，功能如同 daemon 混跑限制與偶發崩潰，待後續正式版完善。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, D-Q1, B-Q21

A-Q20: 什麼是 Named pipe 映射支援？
- A簡: 讓容器存取主機 Named Pipe，利於某些 Windows IPC 場景整合。
- A詳: Named pipe 是 Windows 的進程間通訊通道。容器支援映射 named pipe 後，能將主機 pipe 暴露至容器，協助需要與主機服務互動的應用（如 Docker in Docker、某些代理程式）。此為 Windows 容器生態的重要互通能力之一，與 SMB 掛載同屬增進實務可用性的增強項。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q19, C-Q7

A-Q21: 強化對編排器（Swarm/Kubernetes）有何意義？
- A簡: 改善網路與基礎功能，讓 Windows 容器更易納入主流編排器與混合集群。
- A詳: 文中提到對編排器的基礎建設、Kubernetes 網路增強等，表示 Windows 容器逐步補齊與 Linux 等價的網路與存儲能力。這有助於在異質集群中佈署 Windows 工作負載，使服務發現、負載均衡、Volume 等與 Linux 節點更一致，減少運維差異。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q20, C-Q10, A-Q17

A-Q22: 為什麼 LCOW 被視為可能取代 WSL（當時）？
- A簡: 因 LCOW 以原生 Linux 內核運行容器，兼具相容性與維運簡潔，覆蓋更廣場景。
- A詳: 文中指出秋季更新將以 LCOW 取代 WSL 的方向（當時觀察）。理由是 LCOW 不靠系統呼叫轉譯，而以最小 Linux 實體環境運作，對容器、雲原生工具鏈相容度高且便於維護。實務上覆蓋從應用到容器化部署的更多場景，故被期待成為更通用的方案。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q14, A-Q1

A-Q23: BusyBox 是什麼？為何常用來測試？
- A簡: BusyBox 是超精簡 Linux 工具箱映像，體積小、啟動快，適合環境驗證。
- A詳: BusyBox 將常用 Unix 工具整合於單一可執行檔，映像極小。於容器世界中常作為「萬用瑞士刀」用於網路測試、目錄檢查、快速互動 shell。文中用 busybox sh 進入容器，簡單驗證 LCOW 的拉取與互動性，並作跨 daemon 網路測試之基礎工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, A-Q16, B-Q22

A-Q24: Windows Insider Docker Hub repo 的新 base images 是什麼？
- A簡: 釋出新版 Nano/Server Core 等預覽映像，體積更小，便於測試與採用。
- A詳: 微軟於 Insider 通道提供更新後的 Windows 基底映像（如 Nano Server、Server Core），包含大幅瘦身與相容性調整。開發者可在預覽期間提前驗證應用與容器效能影響，並為生產升級做準備。文章強調體積縮減對日常拉取與部署的正面影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, A-Q12, D-Q10

---

### Q&A 類別 B: 技術原理類

B-Q1: LCOW 整體架構如何運作？
- A簡: Docker CLI 連 LCOW daemon，透過 Hyper-V 啟 LinuxKit Utility VM，在其中啟動 Linux 容器。
- A詳: 技術原理說明：LCOW 由 Docker 客戶端與支援 LCOW 的 dockerd 協作。關鍵步驟或流程：1) CLI 以 npipe 連 LCOW daemon；2) daemon 由 Hyper-V 啟動精簡 LinuxKit Utility VM；3) 在該 VM 內展開 Linux 映像層並啟動容器進程。核心組件介紹：Docker Engine、Hyper-V、LinuxKit、HNS（網路）、存儲驅動共同完成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q13, B-Q6

B-Q2: 連線至 LCOW Docker daemon 的流程為何？
- A簡: 以 -H 指向 docker_lcow named pipe，CLI 與該 daemon 協商 API 後執行指令。
- A詳: 技術原理說明：Windows 上 Docker Remote API 可走 Named Pipe。關鍵步驟或流程：1) CLI 加上 -H npipe:////./pipe//docker_lcow（或設 DOCKER_HOST）；2) 進行 API 版本協商；3) 傳遞 run/pull 等請求給 LCOW daemon。核心組件介紹：Docker CLI、Named Pipe、LCOW dockerd、API negotiation。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, C-Q8, B-Q24

B-Q3: LCOW 啟動 hello-world 的執行流程與效率來源？
- A簡: 利用精簡 LinuxKit 與 Hyper-V 容器，少量元件與快啟機制，使啟動約數秒完成。
- A詳: 技術原理說明：Utility VM 使用最小化 Linux 與不可變設計，縮短啟動路徑。關鍵步驟或流程：1) 拉取映像；2) 展開層；3) 啟 Utility VM；4) 執行容器命令並輸出。核心組件介紹：LinuxKit 基礎服務、Hyper-V 啟動優化、Docker 層快取皆貢獻秒級啟動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, A-Q12, B-Q1

B-Q4: 為何 LCOW 模式不能使用 windowsfilter graphdriver？
- A簡: windowsfilter 僅適用 Windows 映像；LCOW 需要 Linux 相容層，混用會觸發一致性錯誤。
- A詳: 技術原理說明：Windows 與 Linux 映像層格式與檔案系統機制不同。關鍵步驟或流程：當 LCOW daemon 試圖以 windowsfilter 建立層時會檢測並 panic。核心組件介紹：graphdriver（windowsfilter vs Linux 驅動）、層存儲 API；錯誤「windowsfilter…not be used when in LCOW mode」即此檢核。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, B-Q23, B-Q26

B-Q5: LCOW 與 Docker for Windows 預設 Linux 模式（Moby VM）差異？
- A簡: 前者每容器以 Hyper-V Utility VM 跑 Linux；後者在單一 Moby VM 內跑 Linux 容器。
- A詳: 技術原理說明：Moby VM 是常駐單一 VM，內跑 dockerd 與 Linux 容器；LCOW 則由 Windows dockerd 以 Hyper-V 啟用 LinuxKit Utility VM。關鍵步驟或流程：LCOW 由 Windows 控制面統一管理；Moby 模式則轉向 VM 內的 Linux 引擎。核心組件介紹：Moby VM、Hyper-V、LinuxKit、兩種網路與存儲路徑差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q9, B-Q1

B-Q6: Hyper-V Container 的隔離機制如何設計？
- A簡: 以硬體虛擬化建立每容器獨立核心空間，避免與宿主核心共享。
- A詳: 技術原理說明：容器進程不直接跑在宿主核心，而在 Utility VM 的客體核心。關鍵步驟或流程：1) 為容器配置 Utility VM；2) 啟客體核心與最小服務；3) 容器進程在 VM 內執行。核心組件介紹：Hyper-V、Utility VM、HCS（容器宿主計算服務）提供進程生命週期管理與隔離。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q1, B-Q13

B-Q7: LCOW 的網路如何建立？
- A簡: 透過 HNS 與 Hyper-V vSwitch 建 NAT 網段，為容器與 Utility VM 分配虛擬 NIC 與 IP。
- A詳: 技術原理說明：Windows HNS 管理虛擬交換器、NAT 與端點。關鍵步驟或流程：1) 建立 NAT 網路；2) 為 Utility VM/容器附加 vNIC；3) 分配私網 IP；4) 透過 NAT 出口與主機互通。核心組件介紹：HNS、vSwitch、NAT、端點策略（端口轉發/DNAT）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q8, B-Q8

B-Q8: 多 daemon 並存時網路互通的原理？
- A簡: 共享主機網路基礎（vSwitch/NAT），IP 層可路由；控制面則彼此獨立。
- A詳: 技術原理說明：雖不同 daemon 建立自行的 HNS 網路物件，但在同主機上可透過 vSwitch 與路由互達。關鍵步驟或流程：各自分配 IP；視網段與路由策略允許互 ping。核心組件介紹：HNS 網路、NAT、路由表與防火牆規則共同影響可達性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q8, A-Q15

B-Q9: 為何不同 daemon 間無法用 Docker 內建 DNS？
- A簡: 內建 DNS 與服務發現由單一 daemon 維護，跨 daemon 無共享資料平面。
- A詳: 技術原理說明：Docker DNS 記錄儲於該 daemon 的網路與服務資料結構。關鍵步驟或流程：容器加入網路時註冊名稱；查詢由同 daemon 解析。跨 daemon 無同步，故名稱解析失效。核心組件介紹：libnetwork/HNS、內建 DNS、服務發現表均限定於單一引擎域。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q3, C-Q6

B-Q10: Windows 上以 Named Pipe 傳輸 Docker API 的原理？
- A簡: 以本機管道提供 RPC 通道，替代 TCP socket，強化本機通訊安全與便利。
- A詳: 技術原理說明：Named Pipe 是 Windows IPC，支援權限控管與本機高速傳輸。關鍵步驟或流程：dockerd 監聽 npipe；CLI 以 -H 連線並協商 API；後續以該通道收發 JSON API。核心組件介紹：Named Pipe、ACL 權限、Docker API negotiation 機制。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, C-Q8, B-Q24

B-Q11: SMB Volume 掛載到容器的機制是什麼？
- A簡: 透過本機掛載或直接映射 UNC 路徑，讓容器存取 SMB 分享資源。
- A詳: 技術原理說明：Windows 容器可將主機對 \\server\share 的掛載（或直接 UNC）映射入容器檔案系統。關鍵步驟或流程：驗證憑證；建立掛載點；以 -v 映射至容器路徑。核心組件介紹：SMB/CIFS、憑證管理、HCS 檔案系統映射策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q9, A-Q13

B-Q12: Nano/Server Core 映像縮小的技術觀點？
- A簡: 移除不必要元件，採用精簡 API 面，優化層內容以降低體積。
- A詳: 技術原理說明：藉裁剪組件、改用 .NET Core/PowerShell 6 等精簡堆疊，並優化影像層布局。關鍵步驟或流程：清理未用功能、壓縮與重組層，減少基底負擔。核心組件介紹：映像層管理、相依關係最小化、雜湊層快取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, D-Q10

B-Q13: LCOW 如何以 LinuxKit 提供 Utility VM？
- A簡: 以 YAML 組裝最小 Linux，打包為可啟動映像，供 Hyper-V 啟動並承載容器。
- A詳: 技術原理說明：LinuxKit 定義核心、init 與基礎服務容器。關鍵步驟或流程：1) 產生映像（vhd/vhdx）；2) Hyper-V 啟動作為 Utility VM；3) 內部 dockerd/shim 管理容器進程。核心組件介紹：LinuxKit 元件、Hyper-V 啟動、容器 runtime/shim 溝通機制。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q1, A-Q7, B-Q6

B-Q14: 為何 LCOW 較 WSL 有更好相容性？
- A簡: LCOW 跑在真實 Linux 核心上；WSL 依賴系統呼叫轉譯，覆蓋度有限。
- A詳: 技術原理說明：WSL 模擬或轉譯 Linux 系統呼叫至 Windows 內核接口，部分行為或功能受限；LCOW 直接以 Linux 核心執行容器，遵循 Linux ABI。關鍵步驟或流程：容器標準 runtime 與 kernel 特性完整可用。核心組件介紹：Linux kernel、容器 runtime、系統呼叫層差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q22, B-Q1

B-Q15: 如何從 docker version 分辨當前連線引擎？
- A簡: 查看 Server 欄位的 Version/OS/Arch 與 API 版本，或切換 -H 驗證。
- A詳: 技術原理說明：CLI 會顯示 Client 與 Server 資訊。關鍵步驟或流程：執行 docker version；檢查 Server Version（如 master-dockerproject-2017-10-03）與 OS/Arch（windows/amd64），以及 API version（1.34 vs 1.32）。核心組件介紹：版本協商、Server 欄位辨識實際連線目標。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q8, A-Q9

B-Q16: LCOW 與 Windows 容器混跑的限制（預覽）為何？
- A簡: 同一 LCOW daemon 無法跑 Windows 映像；須用預設 daemon 啟 Windows 容器。
- A詳: 技術原理說明：LCOW daemon 以 Linux 路徑處理映像層與 runtime，與 windowsfilter 等不相容。關鍵步驟或流程：嘗試拉 Windows 映像會引發一致性檢查錯誤並崩潰。核心組件介紹：graphdriver 差異、Runtime 與 image 嚴格匹配要求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, A-Q8, C-Q5

B-Q17: 鏡像拉取流程中的 foreign URL 有何意義？
- A簡: Windows 基底層常透過 Microsoft 提供的外部 URL 下載，屬官方分發機制。
- A詳: 技術原理說明：Docker Hub 會引用外部來源（如 go.microsoft.com）分發特定層。關鍵步驟或流程：daemon 解析 manifest，對 foreign layer 使用外部連結拉取。核心組件介紹：Docker distribution、manifest、foreign layer 來源與授權策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q2, B-Q24, A-Q24

B-Q18: LCOW 啟動快的技術因素有哪些？
- A簡: 精簡 Kernel/用戶空間、層快取、Hyper-V 快啟、容器最小化進程。
- A詳: 技術原理說明：LinuxKit 最小化映像與不可變層減少 IO；Hyper-V 提供快速啟動路徑。關鍵步驟或流程：重用快取層、避免多餘服務、容器只執行單一目標命令。核心組件介紹：層快取、init 節點、Hyper-V 啟動優化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q16, D-Q5

B-Q19: 什麼是 Named Pipe 映射（容器內）？
- A簡: 將主機的 \\.\pipe\xxx 映射到容器，供應用與主機進程交談。
- A詳: 技術原理說明：HCS 允許將主機 IPC 資源映射進容器命名空間。關鍵步驟或流程：建立映射，容器內以相同或別名 pipe 名稱存取。核心組件介紹：Named Pipe、ACL、容器檔案/命名空間映射，常見於代理/驅動整合。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q20, C-Q7, D-Q3

B-Q20: 編排器網路增強對 Kubernetes 的影響？
- A簡: 提供更完整的 HNS 特性與策略，使 Windows 節點能加入 K8s 並行使核心網路能力。
- A詳: 技術原理說明：K8s 依賴 CNI 與網路策略；Windows 需提供等價功能。關鍵步驟或流程：HNS 提供端點、NAT/Overlay 支援與策略下發。核心組件介紹：HNS、CNI、策略引擎，共同讓 Windows 工作負載在多平台集群中可互通與管控。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q21, C-Q10, D-Q3

B-Q21: LCOW daemon 崩潰時的行為與原因？
- A簡: 會立即退出，常見因誤用 windowsfilter 或拉取不支援映像導致 panic。
- A詳: 技術原理說明：一致性檢查觸發 panic，dockerd 進程退出。關鍵步驟或流程：日誌出現「windowsfilter…not be used when in LCOW mode」後崩潰；需手動重啟。核心組件介紹：dockerd 錯誤處理、graphdriver 檢查、服務監控/重啟策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2, C-Q9

B-Q22: 為何 BusyBox 能在 LCOW 上直接執行？
- A簡: 因 LCOW 供應真實 Linux 核心與使用者空間，BusyBox 相容度高且靜態/小體積。
- A詳: 技術原理說明：BusyBox 不需複雜 kernel 特性，且通常靜態連結，依賴少。關鍵步驟或流程：拉取 busybox；在 Utility VM 內展開層並啟動 sh。核心組件介紹：Linux kernel ABI、容器 runtime、最小使用者空間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q23, C-Q3, B-Q1

B-Q23: Windows 與 Linux 映像層格式差異導致的限制？
- A簡: 層格式、檔案系統與驅動器不同，不能互相混用或在錯誤 daemon 上展開。
- A詳: 技術原理說明：Windows 層使用 windowsfilter/VFS，Linux 層使用 overlay2/aufs 等；權限和檔案語義不同。關鍵步驟或流程：錯用驅動會在層註冊時失敗。核心組件介紹：graphdriver、層索引與元資料、OS 特定語義。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q1, A-Q8

B-Q24: Docker API 版本協商如何影響 LCOW？
- A簡: CLI/daemon 會協商 API 版本；LCOW daemon 可能較新，需相容區間滿足。
- A詳: 技術原理說明：Client/Server 遵循最小共同版本進行通訊。關鍵步驟或流程：查看 docker version 的 API version 與 minimum version；不相容會導致功能不可用。核心組件介紹：API negotiation、功能閘（feature-gates）、向後相容策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, C-Q2, D-Q6

B-Q25: LCOW 的資源使用特性？
- A簡: 每容器有 Utility VM 成本，但精簡化設計降低開銷，換取隔離與相容性。
- A詳: 技術原理說明：Hyper-V 容器提供 VM 級隔離，成本高於同核心容器；LinuxKit 最小化減輕負擔。關鍵步驟或流程：按需啟動 Utility VM、釋放資源。核心組件介紹：Hyper-V 資源調度、LinuxKit 組件、層快取重用。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q13, D-Q5

B-Q26: 多 daemon 並存時的資料根目錄與快取隔離？
- A簡: 各 daemon 有獨立 data-root 與 graphdriver，映像與層快取互不共享。
- A詳: 技術原理說明：dockerd 以 data-root 管理映像層與容器資料，依 graphdriver 決定格式。關鍵步驟或流程：不同 daemon 使用不同路徑/驅動；拉取需各自進行。核心組件介紹：data-root、graphdriver（windowsfilter/LCOW 專用）、內容可尋址存儲。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, B-Q4, D-Q2

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Windows 10 Insider 1709 準備 LCOW 環境？
- A簡: 安裝 Docker for Windows Edge，下載支援 LCOW 的 dockerd 與 LinuxKit 映像，啟動額外 daemon。
- A詳: 具體實作步驟：1) 安裝 Docker for Windows（Edge）；2) 依官方文下載支援 LCOW 的 dockerd（master-dockerproject-2017-10-03）；3) 下載/準備 LinuxKit 映像；4) 以 npipe 啟 LCOW daemon。關鍵程式碼片段或設定：
```
dockerd -D -H npipe:////./pipe//docker_lcow --experimental
```
注意事項與最佳實踐：啟用 Hyper-V；使用預覽功能前備份；與預設 daemon 並存，注意連線端點切換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q2, C-Q8

C-Q2: 如何檢查 CLI 目前連到哪個 Docker daemon？
- A簡: 執行 docker version 檢視 Server 欄位，或用 -H 顯式指定並比對。
- A詳: 具體實作步驟：1) 執行 docker version；2) 檢查 Server Version/API version/OS；3) 若用 LCOW，Server 可能顯示 master-dockerproject 與 API 1.34。關鍵程式碼片段或設定：
```
docker version
docker -H npipe:////./pipe//docker_lcow version
```
注意事項與最佳實踐：將 DOCKER_HOST 設定為對應 npipe 以避免誤連；動手前先確認目標 daemon。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, C-Q8, D-Q7

C-Q3: 如何在 LCOW 上執行 BusyBox 並進入 shell？
- A簡: 使用 -H 指向 LCOW daemon，執行 run -ti busybox sh 進入容器。
- A詳: 具體實作步驟：1) 連線 LCOW daemon；2) 拉取並啟動 BusyBox。關鍵程式碼片段或設定：
```
docker -H "npipe:////./pipe//docker_lcow" run -ti busybox sh
```
注意事項與最佳實踐：首次拉取需時間；結束可 exit；用於快速驗證網路/檔案系統等基本功能。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q23, B-Q22, C-Q4

C-Q4: 如何在 LCOW 測試 hello-world 與啟動時間？
- A簡: 執行 run hello-world，並以 PowerShell Measure-Command 量測時間。
- A詳: 具體實作步驟：1) 連 LCOW；2) 執行 hello-world；3) 用計時指令。關鍵程式碼片段或設定：
```
Measure-Command { docker -H "npipe:////./pipe//docker_lcow" run hello-world }
```
注意事項與最佳實踐：確保網路可拉取映像；多次執行觀察快取效果；對比 SSD/HDD 差異與 Hyper-V 啟動時間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q3, D-Q5

C-Q5: 如何同機運行 Windows 與 Linux 容器？
- A簡: 用預設 daemon 跑 Windows 容器；用 LCOW daemon 跑 Linux 容器，兩者分開。
- A詳: 具體實作步驟：1) Docker for Windows 切至 Windows 模式；2) 啟 Windows 容器；3) 另連 LCOW daemon 跑 Linux 容器。關鍵程式碼片段或設定：
```
docker run -ti mcr.microsoft.com/windows/nanoserver cmd
docker -H "npipe:////./pipe//docker_lcow" run -ti busybox sh
```
注意事項與最佳實踐：預覽期同 daemon 不支援混跑；小心端口衝突；善用 docker context/環境變數切換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q16, D-Q3

C-Q6: 如何測試跨 daemon 容器的網路互通？
- A簡: 取得兩端 IP 後互相 ping，驗證 HNS/NAT 路由是否可達。
- A詳: 具體實作步驟：1) 在 Windows 容器內 ipconfig；2) 在 BusyBox 內 ifconfig/ip addr；3) 互 ping。關鍵程式碼片段或設定：
```
docker exec -it <win-id> cmd /c ipconfig
docker -H "npipe:////./pipe//docker_lcow" exec -it <bb-id> sh -c "ip addr; ping -c 3 <win-ip>"
```
注意事項與最佳實踐：關閉主機防火牆限制、避免重疊網段、記錄網段以便服務規劃。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q7, D-Q8

C-Q7: 如何在 Windows 容器掛載 SMB 共享？
- A簡: 以 -v 映射 UNC 路徑或先 net use 掛載後再映射到容器路徑。
- A詳: 具體實作步驟：1) 先在主機驗證憑證並掛載；2) 以 -v 將路徑映射入容器。關鍵程式碼片段或設定：
```
net use \\server\share /user:domain\user *
docker run -v \\server\share:C:\data mcr.microsoft.com/windows/servercore powershell
```
注意事項與最佳實踐：確保權限與路徑格式正確；必要時使用認證管理；生產建議集中控管憑證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q11, D-Q9

C-Q8: 如何方便地切換至 LCOW daemon？
- A簡: 設定 DOCKER_HOST 為 LCOW 的 named pipe，或使用 docker context 管理端點。
- A詳: 具體實作步驟：1) 設定環境變數或 context。關鍵程式碼片段或設定：
```
setx DOCKER_HOST npipe:////./pipe//docker_lcow
:: 或
docker context create lcow --description "LCOW" --docker "host=npipe:////./pipe//docker_lcow"
docker context use lcow
```
注意事項與最佳實踐：避免與預設 daemon 混用造成誤部署；指令前先 docker version 確認。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q2, D-Q7

C-Q9: 如何收集 LCOW daemon 日誌與診斷？
- A簡: 以 -D 啟動 dockerd 並重導輸出；發生 panic 時檢視關鍵訊息定位原因。
- A詳: 具體實作步驟：1) 使用 -D 開啟 debug；2) 重導日誌至檔案；3) 觀察 panic 與 stack。關鍵程式碼片段或設定：
```
dockerd -D -H npipe:////./pipe//docker_lcow > lcow.log 2>&1
```
注意事項與最佳實踐：保留重現步驟；附上 docker version 與系統版本；用最小案例（如 hello-world）縮小問題面。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, D-Q2, D-Q6

C-Q10: 混合 OS 架構如何過渡到編排器？
- A簡: 先分離 Windows/Linux 節點，待網路/卷等功能齊備再整合至 Swarm/K8s。
- A詳: 具體實作步驟：1) 分別建 Windows/Linux 節點池；2) 測試基本網路/存儲能力；3) 以最小服務驗證；4) 逐步導入 K8s/Swarm。關鍵程式碼片段或設定：依官方 CNI/網路範本配置。注意事項與最佳實踐：預覽功能勿上生產；善用小型 PoC；明確劃分責任域與資源配額。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q21, B-Q20, D-Q3

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 出現「windowsfilter graphdriver should not be used when in LCOW mode」怎麼辦？
- A簡: 誤在 LCOW daemon 拉/跑 Windows 映像；改用預設 Windows daemon，並重啟 LCOW。
- A詳: 問題症狀描述：拉取 nanoserver/servercore 時 panic，daemon 退出。可能原因分析：LCOW 模式下誤用 windowsfilter/Windows 映像。解決步驟：1) 停止 LCOW；2) 切回預設 daemon 跑 Windows 容器；3) 重啟 LCOW daemon。預防措施：明確分流映像類型與目標 daemon，使用 docker context 管理端點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q16, C-Q5

D-Q2: 拉取 nanoserver 後出現 docker: unexpected EOF，如何排查？
- A簡: 可能 daemon 崩潰或網路中斷；檢查日誌，重啟 daemon，改在預設 daemon 操作。
- A詳: 問題症狀描述：拉取完成部分層即 EOF。可能原因分析：LCOW daemon 因 graphdriver 一致性 panic 退出；或網路不穩。解決步驟：1) 查 lcow.log；2) 重啟 LCOW；3) 使用預設 daemon 拉 Windows 映像。預防措施：分清 Windows/Linux 工作負載；先以 hello-world 驗證連線穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, B-Q17, C-Q9

D-Q3: 為何兩邊 docker ps 看不到對方容器？如何跨 daemon 發現服務？
- A簡: 控制面獨立；改用 IP、外部 DNS/服務註冊或合併至同 daemon/編排網路。
- A詳: 問題症狀描述：各自 ps 僅見自身容器，--link/DNS 失效。可能原因分析：不同 daemon 的名稱/網路空間不共享。解決步驟：1) 以 IP 直連；2) 外部 DNS/Consul 註冊；3) 若需內建解析，改同 daemon。預防措施：在設計時決定統一控制面，或採編排器提供的服務發現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q9, C-Q6

D-Q4: 跨 daemon 名稱解析失敗，如何處理？
- A簡: 使用靜態 hosts、外部 DNS 或服務註冊；避免依賴內建 Docker DNS。
- A詳: 問題症狀描述：容器彼此以名稱連線失敗。可能原因分析：Docker DNS 僅在同 daemon 網路生效。解決步驟：1) 在容器/映像加入 hosts；2) 建外部 DNS 記錄；3) 使用服務註冊/發現機制。預防措施：規劃網路命名策略，盡量統一控制面。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q9, C-Q6

D-Q5: hello-world/BusyBox 啟動慢或失敗的原因？
- A簡: 硬碟較慢、快取未命中、Hyper-V 未啟，或網路拉取不穩；優化硬體與快取。
- A詳: 問題症狀描述：首次執行很慢或超時。可能原因分析：HDD IO 慢；映像未快取；Hyper-V 未開；DNS/網路不穩。解決步驟：1) 確認 Hyper-V；2) 重試以快取層；3) 改良網路/代理；4) 優先 SSD。預防措施：預拉常用映像；保持 Docker/Windows 更新。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q18, C-Q4

D-Q6: LCOW daemon 崩潰後無法連線，如何恢復？
- A簡: 以 -D 模式重新啟動並收集日誌；釐清是否誤跑 Windows 映像導致。
- A詳: 問題症狀描述：-H 指定 LCOW 端點無回應。可能原因分析：先前指令觸發 panic。解決步驟：1) 重啟 dockerd（-D 開 debug）；2) 檢視日誌；3) 修正操作（改用預設 daemon 跑 Windows 容器）。預防措施：分流 context；加啟程式監控自動重啟。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, C-Q9, D-Q1

D-Q7: 無法正確切換 Linux/Windows/LCOW 三種引擎，怎麼辦？
- A簡: 明確使用 docker context 或 -H；透過 docker version 驗證 Server 端點。
- A詳: 問題症狀描述：指令落到錯誤 daemon。可能原因分析：環境變數/上下文混亂。解決步驟：1) 建立 context（預設、lcow）；2) docker context use 切換；3) 執行 docker version 確認。預防措施：腳本化上下文切換；命名清晰避免誤操作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, C-Q2, B-Q15

D-Q8: 跨容器互 ping 不通的可能原因與解法？
- A簡: 網段重疊、防火牆阻擋、vSwitch 異常；調整 HNS 網路與防火牆規則。
- A詳: 問題症狀描述：不同 daemon/容器間 ping 超時。可能原因分析：NAT 網段衝突；主機防火牆阻擋 ICMP；vSwitch 配置問題。解決步驟：1) 重新建立非重疊網段；2) 放行 ICMP；3) 重啟 HNS/虛擬交換器。預防措施：規劃私網段；使用基準腳本建立一致網路。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, C-Q6

D-Q9: 掛載 SMB volume 失敗的原因與解決？
- A簡: 權限或路徑格式錯誤、憑證沒授權；先 net use 驗證再映射容器。
- A詳: 問題症狀描述：-v 映射 UNC 失敗。可能原因分析：匿名存取被拒；域/使用者憑證未設；UNC 格式錯誤。解決步驟：1) 主機 net use 驗證；2) 確認帳密與 ACL；3) 正確使用 \\server\share 格式。預防措施：集中管理憑證；測試讀寫權限；避免在不可信網段裸露共享。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q11, A-Q13

D-Q10: 映像過大導致拉取慢，如何改善？
- A簡: 改用瘦身基底（Nano/Server Core 新版）、預熱快取、使用近端 Registry。
- A詳: 問題症狀描述：拉取時間長、頻寬吃緊。可能原因分析：映像層體積大；網路延遲。解決步驟：1) 換新版 Nano/Server Core；2) 預拉常用映像；3) 設 Registry Mirror 或本地倉庫。預防措施：最佳化 Dockerfile 分層；定期清理多餘層與未用映像。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q24, B-Q12

---

### 學習路徑索引

- 初學者：建議先學習 15 題
    - A-Q1: 什麼是 LCOW（Linux Containers on Windows）？
    - A-Q2: LCOW 的核心價值是什麼？
    - A-Q5: LCOW 與傳統在 Windows 上以 VM 跑 Linux 的差別？
    - A-Q6: 什麼是 Hyper-V Container？
    - A-Q7: LinuxKit 是什麼？為何用在 LCOW？
    - A-Q11: Nano Server 與 Server Core 基底映像有何差異？
    - A-Q12: 為何減少基底映像大小很重要？
    - A-Q13: 什麼是 SMB Volume 掛載？好處是什麼？
    - A-Q16: hello-world 測試有何意義？
    - A-Q23: BusyBox 是什麼？為何常用來測試？
    - B-Q3: LCOW 啟動 hello-world 的執行流程與效率來源？
    - C-Q2: 如何檢查 CLI 目前連到哪個 Docker daemon？
    - C-Q3: 如何在 LCOW 上執行 BusyBox 並進入 shell？
    - C-Q4: 如何在 LCOW 測試 hello-world 與啟動時間？
    - D-Q5: hello-world/BusyBox 啟動慢或失敗的原因？

- 中級者：建議學習 20 題
    - A-Q4: LCOW 與 WSL（Windows Subsystem for Linux）有何差異？
    - A-Q8: LCOW 與 Windows Container 的關係？能同時支援嗎？
    - A-Q9: Docker for Windows 的多引擎情境是什麼？
    - A-Q10: 為什麼要用 -H 指定 npipe 來連 LCOW daemon？
    - A-Q14: 為什麼不同 daemon 的容器仍可互 ping？
    - A-Q15: 為何不同 daemon 間無法用 --link 或 DNS 互找？
    - A-Q17: LCOW 對混合 OS 開發機的價值是什麼？
    - A-Q18: Docker for Windows Edge 版與 LCOW 有何關聯？
    - B-Q1: LCOW 整體架構如何運作？
    - B-Q2: 連線至 LCOW Docker daemon 的流程為何？
    - B-Q4: 為何 LCOW 模式不能使用 windowsfilter graphdriver？
    - B-Q5: LCOW 與 Docker for Windows 預設 Linux 模式差異？
    - B-Q7: LCOW 的網路如何建立？
    - B-Q8: 多 daemon 並存時網路互通的原理？
    - B-Q15: 如何從 docker version 分辨當前連線引擎？
    - C-Q5: 如何同機運行 Windows 與 Linux 容器？
    - C-Q6: 如何測試跨 daemon 容器的網路互通？
    - C-Q8: 如何方便地切換至 LCOW daemon？
    - D-Q1: 出現 windowsfilter 與 LCOW 衝突怎麼辦？
    - D-Q3: 為何兩邊 docker ps 看不到對方容器？如何跨 daemon 發現服務？

- 高級者：建議關注 15 題
    - A-Q21: 強化對編排器（Swarm/Kubernetes）有何意義？
    - A-Q22: 為什麼 LCOW 被視為可能取代 WSL（當時）？
    - B-Q6: Hyper-V Container 的隔離機制如何設計？
    - B-Q10: Windows 上以 Named Pipe 傳輸 Docker API 的原理？
    - B-Q11: SMB Volume 掛載到容器的機制是什麼？
    - B-Q12: Nano/Server Core 映像縮小的技術觀點？
    - B-Q13: LCOW 如何以 LinuxKit 提供 Utility VM？
    - B-Q14: 為何 LCOW 較 WSL 有更好相容性？
    - B-Q17: 鏡像拉取流程中的 foreign URL 有何意義？
    - B-Q20: 編排器網路增強對 Kubernetes 的影響？
    - B-Q21: LCOW daemon 崩潰時的行為與原因？
    - B-Q24: Docker API 版本協商如何影響 LCOW？
    - B-Q25: LCOW 的資源使用特性？
    - B-Q26: 多 daemon 並存時的資料根目錄與快取隔離？
    - C-Q10: 混合 OS 架構如何過渡到編排器？