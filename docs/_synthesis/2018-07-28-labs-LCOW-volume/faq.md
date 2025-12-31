---
layout: synthesis
title: "使用 LCOW 掛載 Volume 的效能陷阱"
synthesis_type: faq
source_post: /2018/07/28/labs-LCOW-volume/
redirect_from:
  - /2018/07/28/labs-LCOW-volume/faq/
postid: 2018-07-28-labs-LCOW-volume
---

# 使用 LCOW 掛載 Volume 的效能陷阱

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 LCOW（Linux Containers on Windows）？
- A簡: LCOW 是在 Windows 上原生啟動 Linux 容器的技術，每個容器對應獨立輕量 VM，底層以 LinuxKit 運作，可與 Windows 容器並存與互通。
- A詳: LCOW（Linux Containers on Windows）是 Microsoft 在 Windows 平台提供的 Linux 容器執行能力。其核心做法是為每個 Linux 容器啟動一個極精簡的 Linux VM（以 LinuxKit 為基底），容器實際在該 VM 上運行。相較於傳統 Docker for Windows 的單一 VM 承載多容器，LCOW 以「每容器一 VM」提高隔離度與相容性，並能與 Windows 容器共存於同一台主機，同享網路與管理面板（例如共用 Docker daemon、Compose 場景）。LCOW 的價值在於讓開發者於 Windows 端同時整合 Windows/Linux 容器與工具鏈，加速混合技術堆疊的開發測試。但其跨 Host volume I/O 效能目前相對不理想，需正確認知定位與使用場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q13, B-Q1

Q2: LCOW 與 Docker for Windows 有何差異？
- A簡: LCOW 為 Microsoft 原生方案，每容器一 VM、用 LinuxKit；Docker for Windows 用單一 MobyLinux VM，透過 SMB 掛載主機檔案。
- A詳: LCOW 與 Docker for Windows的主要差異在架構與掛載方式。LCOW採「每個 Linux 容器一個極精簡 VM（LinuxKit）」的模型，優點是隔離度高、與 Windows 容器共存、共用網路與工具；Docker for Windows則是在 Hyper-V 中啟動一台固定的 MobyLinux VM，所有 Linux 容器共用該 VM。就檔案掛載而言，Docker for Windows常透過主機 SMB Share 將 Windows 檔案系統暴露給 Linux VM 使用，某些情境下比 LCOW 的 volume 表現穩定；而 LCOW 在跨 Host volume I/O 上目前效能偏弱，且在大量 I/O 場景與檔案鎖釋放時機等細節可能存在差異。選擇上，LCOW偏向開發便利與混合容器整合；Docker for Windows利於傳統單機 Linux 容器開發流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q2, B-Q8

Q3: 什麼是 Windows Container 的隔離層級（process 與 hyper-v）？
- A簡: process 為較輕量隔離，效能佳；hyper-v 在專屬 VM 內執行，隔離強但 I/O 成本較高，特別在跨 OS 邊界時更明顯。
- A詳: Windows 容器支援兩種 isolation。process 隔離將容器視為主機同一核心內的隔離進程，因少層次轉換與 I/O 路徑短，效能最佳，但隔離強度較弱；hyper-v 隔離則為容器啟動專屬 VM，在該 VM 中運作容器，隔離更完整，適合安全需求高或相容性要求嚴格的情境。然而 hyper-v 會引入 VM 邊界，I/O 會跨越虛擬化層，效能與延遲常高於 process 隔離，特別是大量小檔操作、元資料更新頻繁的工作負載。Windows 10 僅支援 hyper-v 隔離；Windows Server 可使用 process 與 hyper-v，故在生產端若 I/O 效能優先，常優先選用 process 隔離。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, D-Q5

Q4: 為什麼在容器中掛載 volume 會影響 I/O 效能？
- A簡: volume 常跨越主機與 VM 邊界，涉及網路或虛擬化轉譯，元資料與小檔操作成本增加，效能明顯下降。
- A詳: 容器 volume 在跨 OS 或虛擬化層時，I/O 路徑會被拉長。以 Docker for Windows 為例，Windows 主機以 SMB 分享資料，再由 Linux VM 掛載；LCOW 則需透過 VM 與宿主間的檔案轉譯機制。這些路徑增加了系統呼叫的封送、權限與鎖處理、元資料同步與快取管理的成本，尤其在大量小檔與頻繁 stat/chmod/rename 的建置流程（如 Jekyll）更為明顯。相較之下，直接寫入容器內部層（container filesystem）通常路徑短、快取有效，效能更佳。因此規劃 I/O 密集工作負載時，需審慎評估 volume 的跨邊界成本，並考量使用容器內部暫存或其他策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q8, C-Q1

Q5: AUFS/Union FS 對容器 I/O 有何影響？
- A簡: 分層檔案系統帶來便利與覆寫機制，但寫入會觸發 Copy-on-Write，元資料變更較多時有額外成本。
- A詳: 多數容器映像採用 Union/Overlay 檔案系統，如 AUFS、OverlayFS。它以多層唯讀層疊加在可寫入層之上，提供輕量映像與快速佈署。當容器寫入檔案時，會觸發 Copy-on-Write 將唯讀層檔案複製到可寫層再修改，帶來額外元資料與 I/O 負擔。對於大量小檔生成、重複掃描或頻繁修改（例如靜態網站編譯、相依套件展開），這些成本會放大。雖然 volume 旨在避開 CoW 成本，但跨 Host/VM volume 又會引入另一種延遲，因此實務上常折衷：大量中間產物寫入容器內暫存、最終輸出視需求決定是否同步到 volume，以兼顧速度與持久化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, A-Q4, C-Q5

Q6: 為何 LCOW 適合開發者而非所有生產場景？
- A簡: LCOW 擅長混合 Windows/Linux 容器整合與開發便利，但跨 Host volume I/O 尚未優化，不宜承載重 I/O 生產工作。
- A詳: LCOW 的最大價值在於「開發便利與整合」。它讓 Windows 開發機可同時運行 Windows 與 Linux 容器、共用網路與工具鏈（如 Compose），對需要混用 .NET Framework、Linux 工具、跨平台服務的團隊極具吸引力。然在本文實驗中，LCOW 在「跨主機 volume I/O」的表現顯著落後（例如 Jekyll volume→container 135s vs container→container 12s），甚至 volume→volume 有不穩定錯誤。因此在生產環境，特別是 I/O 密集型工作負載（大量小檔、頻繁元資料操作）不建議依賴 LCOW 的 volume 路徑；較佳做法是於 Linux 節點原生運行，或以 orchestration 定位到合適節點，避免跨 OS 邊界。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, B-Q11, D-Q3

Q7: Jekyll 在容器中的建置流程概述？
- A簡: Jekyll 讀取 source，渲染為靜態檔輸出到 destination；特性是大量小檔與頻繁元資料操作，對 I/O 延遲敏感。
- A詳: Jekyll 是 Ruby 靜態網站產生器，流程為讀取 Markdown/HTML、套版、產生資產與目錄結構，將結果輸出到 destination（_site 或指定資料夾）。此過程包含大量小檔案的建立、更新與搬移，並頻繁進行 stat、rename、chmod 等元資料操作，對底層檔案系統延遲極為敏感。本文以官方 jekyll/jekyll:2.4.0 容器為基準，在多種組態比較：source/destination 位於 volume 或 container 內。結果顯示 container→container 最快（約 12s），volume→container 變慢（LCOW 135s；Docker for Windows 35s），volume→volume 更可能不穩定（LCOW 出錯）。由此可見，Jekyll 類型工作負載更適合減少跨邊界 I/O，善用容器內暫存以獲得最佳表現。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q1, D-Q7

Q8: volume→volume、volume→container、container→container 三種組態差異？
- A簡: container→container 路徑最短最快；volume→container 跨邊界一次，較慢；volume→volume 跨兩次邊界，最慢且不穩定風險高。
- A詳: 三種組態代表 I/O 路徑的不同長度與轉譯層數。container→container 完全在容器環境內進行，I/O 路徑最短、快取命中高、延遲最低；volume→container 需從宿主 volume 進入容器，穿越一次 VM/網路/檔案協定邊界，延遲上升；volume→volume 則同時在來源與目的端均穿越邊界，對大量小檔、元資料密集工作尤其不利。本文實驗顯示 Jekyll 在 container→container 約 12 秒完成，volume→container 變為十倍以上（LCOW 135 秒），volume→volume 在 LCOW 下更可能遇錯。實務建議優先以 container→container 進行中間產物處理，僅在必要時同步到 volume。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q5, D-Q2

Q9: 為何 container→container 通常最快？
- A簡: I/O 完全留在同一 VM/容器層，省去跨 VM/SMB/轉譯開銷，快取與排程友善，延遲最低。
- A詳: container→container 將讀寫都限制在容器內部檔案系統之中，避免了跨越宿主 OS、網路共享或虛擬化層的轉譯。這意味著更短的系統呼叫路徑、更少的權限與檔案鎖轉換、更高的快取命中率。對 Jekyll、相依套件解壓、CI 中間檔產生等「大量小檔 + 高 metadata 操作」場景，這些優勢乘數放大，帶來最直覺的體感加速。相對地，一旦涉及跨邊界，如 SMB、virtio、9p 或其他轉譯層，延遲會急遽上升。故常見實務是：source 先複製到容器暫存，編譯與生成全在容器內完成，再把最終成果（少量大檔）同步回 volume。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q1, C-Q5

Q10: LCOW 掛載 volume 的已知限制或風險？
- A簡: 跨邊界 I/O 效能低、在大量 I/O 場景不穩定（曾出現 Operation not permitted），不適合高壓持久化輸出。
- A詳: 實測顯示 LCOW 在 volume I/O 上表現不佳，特別是大量小檔生成的場景。以 Jekyll 為例，volume→container 需 135 秒（container→container 僅約 12 秒），volume→volume 更在測試中多次出現「Operation not permitted」錯誤，停在不同檔案點，推定可能與檔案鎖釋放時機、權限/屬性轉譯或底層檔案共享機制相關。雖然並非所有應用都會遇到，但在高並發 I/O、頻繁 metadata 變動與跨平台屬性差異情境下風險升高。建議在 LCOW 下避免以 volume 承載高壓 I/O，改以容器內暫存完成主要工作，再擇要同步成果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q3, C-Q7

Q11: Docker for Windows 的 volume 是如何工作的（SMB）？
- A簡: 透過在 Windows 主機開 SMB 分享，Linux VM 掛載使用。路徑清晰、行為穩定，但延遲受 SMB 與網路堆疊影響。
- A詳: Docker for Windows 以 Hyper-V 啟動一台 MobyLinux VM，並將主機磁碟以 SMB 分享給該 VM 掛載。容器在 VM 中看到的是 Linux 檔案系統路徑，但背後透過 SMB 與 Windows 主機互動。此設計使行為相對可預期，權限與檔案屬性跨平台轉換由 SMB 協定處理；在本文實測下，Jekyll volume→container 約 35 秒，雖慢於 container→container，仍較 LCOW 佳。不過 SMB 帶來固定延遲，遇到大量 metadata 操作仍會明顯放大成本。若需更佳效能，宜減少經 SMB 的小檔 I/O，把繁重工作移入容器內部暫存。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q8, C-Q3

Q12: 什麼是 LinuxKit 與 MobyLinux？
- A簡: LinuxKit 是可組裝的極簡 Linux 發行版；MobyLinux 是 Docker for Windows 使用的固定 VM OS，各自支援不同容器路徑。
- A詳: LinuxKit 是一套以元件化方式打造極簡 Linux 系統的工具集，可用於建構容器執行所需的最小 OS。LCOW 採用 LinuxKit 為每個 Linux 容器提供專屬輕量 VM。MobyLinux 則是 Docker 社群發展出的 Linux 映像（Moby 專案），Docker for Windows 以單一 MobyLinux VM 承載所有 Linux 容器。兩者皆目標輕量、適配容器，差異在於運行模型：LinuxKit 配合 LCOW 採每容器一 VM 的高隔離模式，MobyLinux 走單 VM 多容器的共享模式，對 volume 掛載、I/O 路徑與效能表現造成不同特徵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, B-Q1

Q13: LCOW 與 Windows/Linux 容器共存的價值？
- A簡: 在同一 Windows 主機同時啟動 Windows 與 Linux 容器，網路與管理統一，適合混合技術堆疊的開發測試。
- A詳: LCOW 讓 Windows 主機上可同時管理與運行 Windows 容器與 Linux 容器，且可共享網路、Compose 描述與開發者工具。對微服務團隊常見的混合技術堆疊（例如部分 .NET Framework Windows 服務、部分 Linux 基礎設施如 Nginx、Jekyll、各類 CLI）非常友善，可在單機迅速搭建整體測試環境、降低上下文切換與重構成本。加上容器本身的高相容性，開發完成後可將 Linux 容器部署到原生 Linux 節點，Windows 容器則到 Windows 節點，由編排系統負責調度，達成從開發到上線的順暢銜接。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q6, A-Q6

Q14: 為什麼 Nested Virtualization（雲上再開 Hyper-V）不建議？
- A簡: 雲 VM 已虛擬化，再開 Hyper-V 疊加層次，I/O 路徑過長且存儲多為網路後端，效能與成本皆不划算。
- A詳: 公雲供應的計算資源本身即為 VM，磁碟多採用後端儲存（如網路式 Premium SSD）。若在 VM 內再啟動 Hyper-V（Nested Virtualization），容器 I/O 需穿越多重虛擬化與網路存儲路徑，延遲大增、吞吐下降。本文在 Azure DSv3 測得 hyper-v 模式下寫入 container/volume 明顯偏慢，顯示此組合缺乏經濟效益。對需要混合容器的叢集，建議在編排系統層面將 Windows 容器派遣到 Windows 節點、Linux 容器派遣到 Linux 節點，避免在單 VM 上堆疊多層虛擬化導致嚴重效能損失。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q8, D-Q4

Q15: dd 測試的基本原理與用途？
- A簡: dd 以指定區塊大小與次數從來源讀取並寫入目的，衡量順序 I/O 與元資料影響，常用於跨環境 I/O 對比。
- A詳: dd 是 Unix 系統常見的位元層拷貝工具，可藉由 if（來源）、of（目的）、bs（區塊大小）、count（次數）設定 I/O 模式，例如從 /dev/urandom 讀取隨機資料，以 1MB 區塊連續寫入 1024 次，產生 1GB 檔案並記錄耗時。雖偏重順序寫入，但能反映不同檔案系統、虛擬化層、volume 掛載方式的 I/O 成本差異。本文在多組 OS 與容器隔離模式下以 dd 進行對比，觀察到寫入容器層與寫入跨 Host volume 的顯著落差，是理解架構差異最直接、可重現的方式之一。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, C-Q2, D-Q2

Q16: Windows 10 與 Windows Server 在容器支援上的差異？
- A簡: Windows Server 支援 process 與 hyper-v 隔離；Windows 10 僅 hyper-v。對 I/O 效能與測試選項有實質影響。
- A詳: 在容器隔離層級上，Windows Server 可選擇 process（效能佳）與 hyper-v（隔離強）兩種模式，適合生產環境依需求取捨；Windows 10 僅支援 hyper-v 隔離，導致 I/O 路徑較長，效能不如 Server 上的 process 隔離。本文測試亦反映此差異：Server 上 process 與原生執行耗時相當，hyper-v 明顯較慢；Windows 10 因受限於 hyper-v，無法做 process 對比。此外，Windows 10 可安裝 Docker for Windows 以單 VM 模式跑 Linux 容器，行為與效能特徵也與 LCOW 有所不同。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q2, C-Q4

Q17: 在混合 Windows/Linux 微服務中應如何佈局？
- A簡: 於編排層將 Windows 容器派至 Windows 節點、Linux 容器至 Linux 節點，避免跨 OS volume；中間產物留在容器內。
- A詳: 混合微服務最關鍵是正確放置工作負載。建議使用 Docker Swarm 或 Kubernetes，為節點打上 OS 標籤，將 Windows 容器（如 .NET Framework）派遣到 Windows 節點，Linux 容器派遣到 Linux 節點，避免跨 OS 邊界 I/O。建置過程的大量中間產物盡量留在容器內部（container→container），最終成果才同步到持久化儲存。於開發機可用 LCOW 快速搭環境，但上線時以原生 OS 節點承載，以確保穩定與效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8, D-Q10

Q18: 什麼情況下應避免跨 Host 的 volume？
- A簡: 大量小檔、頻繁 metadata 更新、需要高吞吐與低延遲的建置/打包流程，及不容忍不穩定風險時，應避免。
- A詳: 跨 Host volume（如 SMB、VM 文件轉譯）會提高延遲與元資料操作成本。若你的工作負載屬於靜態網站生成、相依套件展開、資產打包、單元測試產物收集等大量小檔與高頻 stat/rename/chmod 的流程，效能會顯著下滑，且在某些平台（如 LCOW）還可能遇到稀有錯誤。這些情境建議採 container→container 完成主要 I/O，於流程尾端僅同步最終成果至 volume，或改用物件儲存/工件倉儲。當你需要確定性與穩定性時，避免跨邊界 volume 尤為重要。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q7, D-Q2


### Q&A 類別 B: 技術原理類

Q1: LCOW 的技術架構如何運作？
- A簡: 以 LinuxKit 為基底，為每個 Linux 容器啟動輕量 VM，容器在該 VM 內運行，與 Windows 容器共存並共享管理。
- A詳: 原理說明：LCOW 於 Windows 上透過 Hyper-V 啟動一個極簡 Linux VM（LinuxKit），並將 Linux 容器載入該 VM。與 Docker for Windows 的單 VM 不同，LCOW傾向每容器一 VM，提高隔離與相容性。關鍵流程：容器建立時，啟動對應 LinuxKit VM、配置網路與儲存轉譯、載入映像、啟動容器進程；I/O 若經 volume，需經由宿主與 VM 的轉譯通道。核心組件：LinuxKit OS、Hyper-V、容器執行時（containerd/moby 相關）、檔案轉譯層與網路橋接。此架構讓 Windows 同時管理 Linux/Windows 容器，利於開發整合，但在跨邊界 volume I/O 仍有代價。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q2, B-Q4

Q2: Docker for Windows 的架構與檔案掛載機制如何設計？
- A簡: 以單一 MobyLinux VM 承載所有 Linux 容器，由 Windows 主機以 SMB 分享檔案供 VM 掛載，行為穩定可預期。
- A詳: 原理說明：Docker for Windows 在 Hyper-V 啟動一台固定 MobyLinux VM，Docker daemon 位於該 VM。所有 Linux 容器共用此 VM。關鍵流程：Windows 主機將磁碟路徑以 SMB 分享；MobyLinux 透過網路掛載 SMB；容器在 VM 內看到對應路徑。核心組件：MobyLinux VM、Hyper-V、SMB 伺服器（Windows）與客戶端（Linux）、Docker Engine。此設計簡化多容器管理，掛載行為由 SMB 協定處理，權限與屬性轉譯相對清楚。代價是 SMB 帶來固定延遲與在大量 metadata 操作中的成本放大，但在本文實測下，某些 volume 場景仍優於 LCOW。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q11, B-Q8

Q3: Windows Container 的 process 與 hyper-v 隔離如何影響 I/O？
- A簡: process 路徑短，I/O 幾近原生；hyper-v 需跨 VM 邊界，寫入 container 層與 volume 皆增加延遲，尤其小檔與 metadata。
- A詳: 原理說明：process 隔離共用主機核心，系統呼叫與檔案 I/O 幾乎直達宿主檔案系統；hyper-v 隔離在專屬 VM 中，I/O 需穿越虛擬化邊界。關鍵步驟：hyper-v 模式下，寫入 container 層需經虛擬磁碟與虛擬裝置驅動；寫入 volume 則還要經過共享機制（SMB/轉譯）。核心組件：Hyper-V、虛擬磁碟/控制器、檔案共享通道。本文測得在 Windows Server 上，寫 container 層由約 1.57s 增至 5.90s，而寫 volume 由 1.64s 增至 2.21s，顯示 process 在 I/O 密集工作負載更具優勢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q16, D-Q5

Q4: 寫入容器層與寫入 volume 的 I/O 路徑有何差異？
- A簡: 容器層在同一 VM/OS 內，路徑短；volume 需經共享協定或轉譯，跨邊界導致延遲與元資料成本提升。
- A詳: 原理說明：容器層（writable layer）位於容器所在 OS/VM 的本地檔案系統，I/O 路徑包含 UnionFS 寫入與 CoW；volume 則通常代表一個外部掛載點，可能透過 SMB、virtio、9p 或宿主特殊轉譯通道。關鍵步驟：容器層寫入會在本地完成，受 CoW 與快取策略影響；volume 寫入需封包化經共享協定送到宿主，再落盤。核心組件：Union/OverlayFS、共享協定、虛擬裝置/通道。本文實測顯示 container→container 最快，volume→container 變慢，volume→volume 最差且風險高，印證了路徑差異的成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q8, B-Q10

Q5: Jekyll 的 I/O 模式為何容易放大差異？
- A簡: 大量小檔產生與頻繁 metadata 操作（stat/rename/chmod），對延遲極敏感，跨邊界成本被快速累積。
- A詳: 原理說明：Jekyll 透過掃描與渲染內容，產生成千上萬的小檔與目錄結構。每個檔案涉及多次 metadata 操作。關鍵步驟：讀取 source、渲染模板、寫入多個輸出、更新索引與資產、觀察檔案變更。核心組件：Ruby runtime、Jekyll pipeline、底層 FS 與共享協定。當路徑跨越 VM 或 SMB，單次延遲雖小，但在數千回合中被放大，導致 volume→container/volume→volume 成績落後。反之，container→container 受益於本地路徑與快取，最為快速。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q1, D-Q7

Q6: dd 指令 if/of/bs/count 如何影響測試？
- A簡: if 指來源、of 指目的；bs 是區塊大小、count 是次數。區塊越大越傾向吞吐，越小越體現系統呼叫成本。
- A詳: 原理說明：dd 透過指定來源（if=/dev/urandom）與目的（of=路徑）進行拷貝。bs 決定單次 I/O 的大小，count 決定重複次數。關鍵步驟：每回合讀 if、寫 of、更新偏移與統計。核心組件：來源裝置、目的檔案系統、頁快取、虛擬化通道。較大的 bs 測吞吐較多，較小的 bs 更能反映系統呼叫與元資料開銷。本文採 bs=1M、count=1024 模擬 1GB 寫入，主要觀察跨邊界吞吐差異。若要測出 metadata 影響，需搭配大量小檔測試或使用檔案產生器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, C-Q2, D-Q2

Q7: 為何 LCOW volume I/O 較差的可能原因？
- A簡: 跨 VM 轉譯層、權限與檔案鎖處理差異、共享機制尚未優化，導致延遲與不穩定性在高壓 I/O 中放大。
- A詳: 原理說明：LCOW 的 volume 需在宿主與 LinuxKit VM 間轉譯，涉及屬性/權限/鎖的跨平台處理。關鍵步驟：容器寫入 volume 時，請求需封送至宿主、轉為宿主可理解的檔案操作，再回傳狀態。核心組件：LinuxKit 檔案共享通道、Hyper-V 裝置、權限/鎖轉換層。當發生大量小檔與頻繁 metadata 操作時，這些轉譯成本疊加，若鎖釋放時序與平台語意不同，可能出現「Operation not permitted」等不穩定錯誤。此為本文觀察與推論，實際機制取決於實作版本。結論是避免讓 LCOW volume 承擔高壓 I/O。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q10, D-Q1, D-Q3

Q8: Docker for Windows 透過 SMB 帶來哪些延遲特性？
- A簡: SMB 將本機 I/O 變為網路檔案協定，多一次封包與伺服端處理，延遲可預期但在小檔場景成本被放大。
- A詳: 原理說明：SMB 是網路檔案協定，對每個檔案操作進行封包化並由伺服端（Windows）處理，再回傳結果。關鍵步驟：容器（於 MobyLinux VM）發起檔案操作、經 SMB 客戶端送至主機 SMB 伺服端、主機落盤、回傳狀態。核心組件：SMB 客戶端/伺服端、MobyLinux VM、Hyper-V、Windows 檔案系統。優點是行為成熟、語意清楚，跨平台屬性處理一致；缺點是延遲固定存在，特別在高頻 metadata 操作下被放大。本文看到 volume→container 約 35s，顯示在穩定與可預期下仍有相對可接受的成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, D-Q6

Q9: Azure DSv3 嵌套虛擬化的 I/O 路徑與瓶頸為何？
- A簡: VM 內再開 VM，I/O 經多層虛擬磁碟與網路儲存，路徑冗長，造成寫入 container/volume 皆嚴重退化。
- A詳: 原理說明：公雲 VM 使用虛擬化與遠端儲存；在其內部再啟動 Hyper-V，容器 I/O 需穿越客體 VM → 內部 VM → 儲存層。關鍵步驟：應用層 I/O 呼叫經內部 VM 的虛擬磁碟/裝置、出內部 VM 到外部客體 VM，再由外部 VM 的虛擬磁碟/網路通道到後端儲存。核心組件：兩層 Hyper-V、虛擬磁碟、雲端儲存通道。此路徑天然高延遲、低吞吐，本文數據顯示 hyper-v 寫入 container/volume 都遠高於裸機，缺乏實務價值。建議透過編排系統選擇原生 OS 節點運行容器。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q14, C-Q8, D-Q4

Q10: AUFS/UnionFS 分層寫入的具體步驟是什麼？
- A簡: 讀多層唯讀疊加於可寫層；寫入時觸發 CoW 複製至可寫層再修改，帶來額外元資料與 I/O 成本。
- A詳: 原理說明：UnionFS 將多個唯讀層（映像層）疊合成單一檢視，再加上一個可寫層。關鍵步驟：讀取時自上而下尋找檔案；寫入時若目標在唯讀層，先將檔案複製到可寫層（CoW）、再套用變更；新檔案直接建立於可寫層。核心組件：Overlay/AUFS 驅動、目錄白名/黑名標記、層合併邏輯。此設計讓映像重複使用、佈署快速，但在大量修改與 metadata 繁多的場景增加成本。若改寫到 volume，避免 CoW 成本，但會受跨邊界共享協定的延遲影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q4, C-Q5

Q11: 容器跨 OS 邊界的 I/O 與編排如何協同？
- A簡: 以編排系統標記節點與工作約束，確保容器於原生 OS 執行，避免跨邊界 volume，維持效能與穩定。
- A詳: 原理說明：在 Swarm/Kubernetes 中，節點可標記 OS/架構/能力，工作以 label selector 或 nodeSelector/taints 決定落點。關鍵步驟：為 Windows/Linux 節點標記、定義部署策略、限制工作僅在相符節點執行、設計持久化卷在同 OS 區域內提供。核心組件：K8s Scheduler、Node Labels、StorageClass、CSI/volume plugins。此法避免容器跨 OS 邊界 I/O，降低延遲與不穩定性。開發期可用 LCOW 方便整合，上線則由編排負責正確國土化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q8, D-Q10

Q12: 為何 container→container 測試中 LCOW 與 Docker for Windows 表現相近？
- A簡: 兩者皆在 VM 內部完成 I/O，未經跨主機共享，差異主要來自 VM 層與 FS 驅動，總體接近。
- A詳: 原理說明：container→container 完全發生於容器所在的 VM/OS 內，I/O 不需走 SMB 或宿主轉譯通道。關鍵步驟：應用於容器內讀寫、經 UnionFS 與 VM 的本地虛擬磁碟處理。核心組件：LinuxKit 或 MobyLinux VM、容器 FS、虛擬磁碟。本文 Jekyll 測出 LCOW 與 Docker for Windows 皆約 12 秒，顯示在不經 volume 的情況下兩者基礎延遲相近。這也支持最佳實踐：盡可能將 I/O 密集步驟留在容器內完成，再視需求同步成果至外部。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q1, C-Q5


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 LCOW 上執行 Jekyll 並以 container→container 加速建置？
- A簡: 先將 source 複製到容器暫存，destination 也指向容器內路徑，避免跨 volume 邊界，大幅縮短建置時間。
- A詳: 具體步驟：1) 啟用 LCOW（確保 Windows 上 Linux 容器功能可用）。2) 啟動容器時，僅掛入少量必要 volume（或不掛），將 source 以 docker cp 複製到容器內 /tmp/source，destination 設 /tmp/site。3) 容器內執行 jekyll build 或 serve。示例：
  docker run --rm -it jekyll/jekyll:2.4.0 sh
  jekyll build -s /tmp/source -d /tmp/site
  關鍵程式碼片段：
  docker cp ./site-src <containerId>:/tmp/source
  注意事項：避免在 LCOW 下直接將 source/dest 指向 host volume；大量小檔會拖慢或出錯。最佳實踐：中間產物留在容器內，僅將最終結果（/tmp/site）透過 docker cp 取回。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q9, D-Q2

Q2: 如何用 dd 在 Windows/Linux/容器中做 I/O 基準測試？
- A簡: 在 Linux 用 dd 從 /dev/urandom 寫入 1GB；Windows 可用 dd.exe 類似測法，比較 to container 與 to volume 耗時。
- A詳: 具體步驟：Linux/容器內執行：
  dd if=/dev/urandom of=./largefile bs=1M count=1024
  Windows 可使用 dd for Windows（dd.exe）模擬。關鍵程式碼：同上。設定：bs=1M、count=1024 代表 1GB 寫入，觀察不同平台/隔離/掛載組態的耗時。注意事項：dd 偏重順序寫入，對小檔 metadata 不敏感；但足以反映跨邊界吞吐差異。最佳實踐：每組環境執行 5 次取平均；同硬體作對比；將 to container 與 to volume 分開記錄；避免背景干擾（關閉重負載程序）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q6, D-Q2

Q3: 如何在 Docker for Windows 掛載 volume 並改善 Jekyll 建置時間？
- A簡: 使用單 VM（MobyLinux）模式，透過 SMB 掛載 source；destination 指向容器內路徑，減少一次跨邊界 I/O。
- A詳: 具體步驟：1) 安裝 Docker for Windows，啟用 Linux 容器。2) 在設定中分享需要的磁碟（C:/D:）。3) 執行容器並將 source 綁定掛載到 /srv/jekyll（唯讀可選），destination 指容器內 /tmp：
  docker run --rm -v C:\site-src:/srv/jekyll:ro jekyll/jekyll:2.4.0 jekyll build -s /srv/jekyll -d /tmp/out
  關鍵程式碼片段：-v C:\site-src:/srv/jekyll:ro。注意事項：避免將 destination 也指到 volume（volume→volume），以免加倍跨邊界成本。最佳實踐：成功後用 docker cp 從 /tmp/out 取回成果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q2, A-Q8

Q4: 如何在 Windows Server 使用 process 隔離啟動 Windows 容器？
- A簡: 在 Windows Server 指定 --isolation=process 啟動，獲得近原生 I/O 效能，適合 I/O 敏感工作負載。
- A詳: 具體步驟：1) 使用 Windows Server（支援 process 模式）。2) 啟動容器時加入：
  docker run --isolation=process mcr.microsoft.com/windows/servercore:ltsc2019 powershell -c "..."
  關鍵程式碼片段：--isolation=process。注意事項：Windows 10 不支援 process；確保映像與主機版本相容。最佳實踐：I/O 密集流程優先以 process 隔離執行；必要時再以 hyper-v 取代以提升隔離。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q16, D-Q5

Q5: 如何佈局 source/destination 以平衡便利與效能？
- A簡: 將大量中間產物寫在容器內（destination=container），僅將 source 或成果以最小量經過 volume。
- A詳: 具體步驟：1) source 可用 -v 掛載（唯讀）或先 docker cp 進容器；2) destination 指向 /tmp 或容器內路徑；3) 建置完成後再 docker cp 成果回主機。關鍵程式碼：
  docker cp ./src <cid>:/tmp/src
  jekyll build -s /tmp/src -d /tmp/out
  docker cp <cid>:/tmp/out ./dist
  注意事項：避免 volume→volume；避免在 LCOW 下長時間寫入 volume；保持 destination 在容器內。最佳實踐：以容器內暫存加速流水線，只在邊界同步最小成果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q9, B-Q4

Q6: 如何用 docker-compose 混合 Windows 與 Linux 容器（LCOW）？
- A簡: 在同一 Compose 檔定義兩類服務，於 Windows 主機啟用 LCOW，即可同時啟動並共用網路與相依。
- A詳: 具體步驟：1) 在 Windows 啟用 LCOW。2) 撰寫 docker-compose.yml，定義 linux/windows 服務（分別使用對應映像）。3) docker compose up 啟動。關鍵程式碼片段（示意）：
  services:
    web: image: jekyll/jekyll:2.4.0
    api: image: mcr.microsoft.com/dotnet/framework/aspnet:4.8
  注意事項：確認路徑掛載對應平台語意（Windows 路徑與 Linux 路徑），減少跨邊界 volume；用網路相依而非共享檔案。最佳實踐：在開發機用 LCOW 快速整合，上線交由編排系統分派至原生節點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q11, D-Q10

Q7: 如何在本機避免 LCOW volume I/O 瓶頸（資料同步策略）？
- A簡: 採「內建置、外同步」：容器內編譯產生，成果最後用 docker cp/rsync 出來，避免長時間寫 volume。
- A詳: 具體步驟：1) 啟動容器不掛或最少掛 volume；2) 將 source 複製入容器暫存；3) 在容器內完成重 I/O；4) 以 docker cp 將成果取回；5) 需要雙向同步可定期 rsync/腳本化。關鍵程式碼：docker cp 與 jekyll build 指令。注意事項：避免用 LCOW 直接寫入大量小檔到 volume；控制同步頻率與粒度；將 volume 用於少量輸入或成果輸出。最佳實踐：將此策略融入 Makefile/NPM Script/PowerShell，形成一鍵化開發流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q5, D-Q3

Q8: 如何在 Kubernetes/Swarm 避免 nested virtualization 效能損失？
- A簡: 使用節點標籤與排程約束，確保 Windows 容器上 Windows 節點、Linux 容器上 Linux 節點，避免 VM 內再 VM。
- A詳: 具體步驟（K8s）：1) kubectl label nodes 加上 os=windows/linux；2) 在 Pod/Deployment 使用 nodeSelector 或 nodeAffinity 指定 os；3) 為不同 OS 使用對應 StorageClass；4) 驗證排程落點。Swarm 類似以 constraints 實現。關鍵設定片段（K8s）：
  nodeSelector:
    kubernetes.io/os: windows
  注意事項：避免在雲 VM 內啟動 Hyper-V 再跑容器；持久化卷需與節點 OS 相容。最佳實踐：以編排層治理放置策略，確保 I/O 路徑最短與穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q9, D-Q4

Q9: 如何診斷 volume I/O 低落的瓶頸？
- A簡: 先比較 container 與 volume 寫入耗時，再檢視檔案數量與 metadata 操作，縮小為共享協定或虛擬層問題。
- A詳: 具體步驟：1) 以 dd 比較 to container 與 to volume；2) 以實際任務（Jekyll）度量終端耗時；3) 觀察檔案數與操作模式（小檔多則受延遲影響）；4) 在宿主監看 CPU/IO/網路；5) 檢視 SMB 設定（Docker for Windows）或 LCOW 版本；6) 嘗試改為 container→container 驗證是否改善。關鍵指令：dd、計時工具、docker stats。注意事項：避免同時變更多個維度；記錄硬體差異。最佳實踐：建立可重現腳本，做 A/B 測試，形成組態準則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q2, D-Q6

Q10: 如何在 Windows 10 使用 Docker for Windows 開發、在 Server/雲端執行生產？
- A簡: 本機以 Docker for Windows 快速開發與整合；生產以原生 Windows/Linux 節點部署，透過 CI/CD 對齊映像。
- A詳: 具體步驟：1) 開發機安裝 Docker for Windows，使用 Linux/Windows 容器開發；2) 建立 CI 產出不可變映像；3) 在生產叢集（K8s/Swarm）依服務 OS 派送到對應節點；4) 避免跨邊界 volume，使用原生持久化。關鍵設定：多 stage Dockerfile、標籤與節點選擇。注意事項：Windows 10 僅 hyper-v 隔離，不代表生產效能；上線應以 Server 的 process 隔離（若可）或原生 Linux 節點承載。最佳實踐：同一映像貫穿環境，差異僅在部署拓撲與節點 OS。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, A-Q17, B-Q11


### Q&A 類別 D: 問題解決類（10題）

Q1: LCOW volume→volume 出現「Operation not permitted」怎麼辦？
- A簡: 先避免 volume→volume；改以 container→container 完成，再以 docker cp 輸出；更新 LCOW/系統並減少小檔寫入。
- A詳: 問題症狀描述：在 LCOW 下，Jekyll 以 volume→volume 建置，隨機在不同檔案點報「Operation not permitted」。可能原因分析：跨平台權限/屬性/鎖語意轉譯差異、共享機制尚未優化、大量 metadata 操作導致時序問題。解決步驟：1) 立即改為 destination 在容器內；2) 使用 docker cp 將成果取回；3) 更新 Windows/LCOW 與 Docker 版本；4) 減少 volume 上的小檔操作；5) 驗證於 Docker for Windows 或原生 Linux 是否可重現。預防措施：避免高壓 I/O 寫入 LCOW volume；制定容器內暫存策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q1, C-Q7

Q2: 容器建置極慢（超過 100 秒）如何排查？
- A簡: 確認是否寫入 volume；改為 container→container 測試；用 dd 與實際任務 A/B 對比，定位在共享或虛擬層。
- A詳: 問題症狀描述：Jekyll 或類似流程耗時遠超預期（如 120–135s）。可能原因分析：跨 Host volume 導致延遲、高 metadata 操作累積、hyper-v 隔離額外開銷。解決步驟：1) 改 destination 至容器內重測；2) 以 dd 對比 to container/volume；3) 若 Docker for Windows，評估 SMB 設定；4) 若 LCOW，改採容器內暫存與 docker cp；5) 檢視宿主 I/O 與 CPU。預防措施：建立預設佈局（container→container）、文件化規範、納入 CI 腳本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, C-Q2, C-Q5

Q3: 使用 LCOW volume I/O 極差的對策是什麼？
- A簡: 避免直接寫 volume；將重 I/O 留在容器內，僅同步結果；必要時改用 Docker for Windows 或原生 Linux。
- A詳: 問題症狀描述：LCOW 下 volume→container/volume→volume 極慢或不穩。可能原因分析：LCOW 共享通道延遲、權限/鎖轉譯成本。解決步驟：1) 採 container→container；2) 用 docker cp 交付成果；3) 如需 volume，僅掛 source（唯讀）；4) 大型流程拆分，減少小檔；5) 改以 Docker for Windows（SMB）或原生 Linux 執行重 I/O。預防措施：在專案模板納入容器內暫存與同步腳本；規劃落地節點避免跨 OS volume。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q7, B-Q7

Q4: 在 Azure DSv3 nested virtualization I/O 極差如何改善？
- A簡: 避免 VM 內再開 VM；改以原生 OS 節點運行容器；以編排排程至對應 OS 節點，縮短 I/O 路徑。
- A詳: 問題症狀描述：雲 VM 中啟動 Hyper-V 後，容器 I/O 成績大幅退化。可能原因分析：多層虛擬化與網路儲存路徑疊加。解決步驟：1) 關閉 nested 模式，改在雲端直接使用 Windows 節點跑 Windows 容器、Linux 節點跑 Linux 容器；2) 使用 K8s nodeSelector 派送；3) 檢視儲存層，改用對應 StorageClass。預防措施：架構設計避免 nested；以 IaC 固化節點標籤與排程規則，確保正確部署。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q8, B-Q9

Q5: Hyper-V 隔離導致寫入 container 層很慢怎麼辦？
- A簡: 能用 process 就不用 hyper-v；必要時將中間產物寫容器內並減少頻繁寫入；升級硬體與調整分層策略。
- A詳: 問題症狀描述：相對 process 隔離，hyper-v 寫 container 層耗時明顯增加。可能原因分析：虛擬磁碟與裝置層增加延遲、CoW 成本疊加。解決步驟：1) 若在 Windows Server，改用 --isolation=process；2) 在 hyper-v 下縮減寫入次數與小檔數量；3) 佈局改以容器內暫存並合併寫入；4) 確保宿主與虛擬磁碟放在高性能儲存。預防措施：預先在設計上限制 metadata 密集操作，將重 I/O 留在單一階段集中處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q10, C-Q4

Q6: Docker for Windows volume 透過 SMB 不穩如何處理？
- A簡: 檢查磁碟分享權限與防火牆；重設共享；改將 destination 放容器內；必要時轉為 docker cp 流程。
- A詳: 問題症狀描述：掛載路徑無法訪問、間歇性超時、建置卡頓。可能原因分析：SMB 權限、防火牆、網卡設定或 VM 內憑證狀態。解決步驟：1) 在 Docker Desktop 設定中重新分享磁碟；2) 檢查 Windows 憑證與 SMB 連線狀態；3) 重啟 Docker for Windows；4) 改為 destination 在容器內並用 docker cp；5) 評估路徑是否含特殊字元。預防措施：固定專案路徑、建立測試腳本驗證掛載；在 CI 使用原生 Linux 節點避免 SMB。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q3, A-Q11

Q7: Jekyll Auto-regeneration 緩慢或無反應如何排查？
- A簡: 確認監控路徑是否在 volume；改監控容器內路徑；減少監控檔案數；提升檔案事件機制可靠性。
- A詳: 問題症狀描述：jekyll serve --watch 變更不觸發或延遲大。可能原因分析：跨邊界檔案事件轉譯不穩、監控量過大、權限差異。解決步驟：1) 將 source 放容器內；2) 將監控目標縮小；3) 以 docker cp 同步變更；4) 檢查時區/時戳差異；5) 測試在純容器內是否正常。預防措施：建立同步腳本，只在保存時批次同步；降低對跨邊界檔案事件的依賴。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q1, C-Q7

Q8: Windows 10 無法使用 process 隔離怎麼辦？
- A簡: 接受 hyper-v 隔離成本，調整 I/O 佈局（container→container），或改在 Windows Server/原生 Linux 測試。
- A詳: 問題症狀描述：指定 --isolation=process 無效。可能原因分析：Windows 10 僅支援 hyper-v 隔離。解決步驟：1) 在本機採容器內暫存策略；2) 若需 process 效能，改在 Windows Server 測試；3) I/O 密集的 Linux 工作負載改在原生 Linux 節點或 WSL2（視情況）測試；4) 保持映像一致以利移轉。預防措施：在團隊規範中說明 Windows 10 的限制與替代流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, C-Q4, A-Q9

Q9: 容器內檔案鎖導致寫入失敗如何調整？
- A簡: 減少並行小檔操作；在容器內完成主要寫入；更新平台版本；必要時加入重試與等待鎖釋放。
- A詳: 問題症狀描述：操作大量小檔時偶發 Permission/Operation not permitted。可能原因分析：跨平台鎖語意不一致、釋放時序差異、共享通道延遲。解決步驟：1) 降低並行；2) 改為容器內暫存再一次性輸出；3) 升級 Docker/LCOW；4) 對敏感動作加入重試與退避；5) 在非關鍵場景使用唯讀 volume 降低爭用。預防措施：設計流程時避免同時多點寫同一 volume；工具鏈加入鎖偵測與重試機制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, D-Q1, C-Q7

Q10: 混合 Windows/Linux 容器的網路與存儲整合問題如何診斷？
- A簡: 先分層驗證單一 OS 正常，再測跨容器通訊；volume 儘量各自本地化，跨 OS 用 API 而非檔案共享。
- A詳: 問題症狀描述：跨 OS 服務互通不穩、共享檔案掛載錯誤。可能原因分析：不同網路驅動與 DNS 行為、檔案協定語意差異。解決步驟：1) 驗證每類容器在原生 OS 節點運行正常；2) 檢查服務發現與 DNS；3) 盡量以 API 耦合而非共用檔案；4) 若必須共享，選擇雙方支援良好的協定（SMB/NFS）並評估延遲；5) 使用編排系統管理網路與卷。預防措施：分離責任邊界、最小化跨邊界檔案共享、在 CI 中做整合測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q11, C-Q6


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 LCOW（Linux Containers on Windows）？
    - A-Q2: LCOW 與 Docker for Windows 有何差異？
    - A-Q3: 什麼是 Windows Container 的隔離層級（process 與 hyper-v）？
    - A-Q7: Jekyll 在容器中的建置流程概述？
    - A-Q8: 三種組態差異（volume→volume/volume→container/container→container）？
    - A-Q9: 為何 container→container 通常最快？
    - A-Q11: Docker for Windows 的 volume 是如何工作的（SMB）？
    - A-Q12: 什麼是 LinuxKit 與 MobyLinux？
    - A-Q15: dd 測試的基本原理與用途？
    - A-Q16: Windows 10 與 Windows Server 在容器支援上的差異？
    - B-Q2: Docker for Windows 的架構與檔案掛載機制如何設計？
    - B-Q6: dd 指令 if/of/bs/count 如何影響測試？
    - C-Q2: 如何用 dd 在 Windows/Linux/容器中做 I/O 基準測試？
    - C-Q3: 如何在 Docker for Windows 掛載 volume 並改善 Jekyll 建置時間？
    - D-Q2: 容器建置極慢（超過 100 秒）如何排查？

- 中級者：建議學習哪 20 題
    - A-Q4: 為什麼在容器中掛載 volume 會影響 I/O 效能？
    - A-Q5: AUFS/Union FS 對容器 I/O 有何影響？
    - A-Q6: 為何 LCOW 適合開發者而非所有生產場景？
    - A-Q10: LCOW 掛載 volume 的已知限制或風險？
    - A-Q14: 為什麼 Nested Virtualization 不建議？
    - A-Q17: 混合 Windows/Linux 微服務佈局建議
    - A-Q18: 何時應避免跨 Host volume？
    - B-Q1: LCOW 的技術架構如何運作？
    - B-Q3: Windows Container 隔離如何影響 I/O？
    - B-Q4: 寫容器層與寫 volume 的 I/O 路徑差異？
    - B-Q5: Jekyll 的 I/O 模式為何容易放大差異？
    - B-Q8: SMB 延遲特性與優劣？
    - B-Q11: 跨 OS I/O 與編排如何協同？
    - B-Q12: 為何 container→container 成績相近？
    - C-Q1: 在 LCOW 上以 container→container 加速 Jekyll
    - C-Q5: 佈局 source/destination 平衡便利與效能
    - C-Q6: 用 docker-compose 混合 Windows 與 Linux 容器
    - C-Q7: 避免 LCOW volume 瓶頸的同步策略
    - C-Q8: 編排中避免 nested virtualization 效損
    - D-Q1: LCOW volume→volume 出錯的處理

- 高級者：建議關注哪 15 題
    - B-Q7: 為何 LCOW volume I/O 較差的可能原因？
    - B-Q9: Azure 嵌套虛擬化的 I/O 路徑與瓶頸
    - B-Q10: AUFS/UnionFS 分層寫入的具體步驟
    - D-Q3: LCOW volume I/O 極差的對策
    - D-Q4: 雲上 nested virtualization 的改善
    - D-Q5: Hyper-V 隔離導致寫入慢的處理
    - D-Q6: Docker for Windows SMB 不穩的排查
    - D-Q7: Jekyll Auto-regeneration 緩慢排查
    - D-Q9: 檔案鎖導致寫入失敗的調整
    - D-Q10: 混合容器網路與存儲整合診斷
    - A-Q13: LCOW 與 Windows/Linux 容器共存的價值
    - A-Q18: 避免跨 Host volume 的情境
    - C-Q4: Windows Server 使用 process 隔離
    - C-Q9: 診斷 volume I/O 低落瓶頸的方法
    - C-Q10: Win10 開發、Server/雲端生產的一致性策略