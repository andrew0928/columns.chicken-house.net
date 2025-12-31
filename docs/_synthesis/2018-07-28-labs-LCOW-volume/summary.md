---
layout: synthesis
title: "使用 LCOW 掛載 Volume 的效能陷阱"
synthesis_type: summary
source_post: /2018/07/28/labs-LCOW-volume/
redirect_from:
  - /2018/07/28/labs-LCOW-volume/summary/
postid: 2018-07-28-labs-LCOW-volume
---

# 使用 LCOW 掛載 Volume 的效能陷阱

## 摘要提示
- LCOW 掛載 Volume: 透過 LCOW 掛載到主機檔案系統時 I/O 效能明顯下滑，甚至出現寫入錯誤。
- Jekyll 實測差異: 大量小檔讀寫下，container→container 約 12s，而 volume 參與時最高達 135s，差距懸殊。
- Docker for Windows 對比: 同為跨 VM，DfW 透過 SMB 掛載的 volume 在大量 I/O 上普遍比 LCOW 穩定且較快。
- Hyper-V 隔離影響: 隔離層級從 process 轉為 hyper-v 時，寫入 container 的延遲成長數倍。
- Volume 寫入差異: Windows container 對 volume 有較佳優化；LCOW 寫 volume 表現最差。
- 實驗工具與方法: 以 dd 從 /dev/urandom 寫 1GB，對 container/volume 5 次取平均，比較不同平台與隔離層級。
- 環境組合多元: 實測涵蓋 Win Server、Win10、LCOW、Docker for Windows、Azure VM（含 nested virtualization）。
- Azure 上的啟示: 雲端 VM 再套 Hyper-V 測試偏離實務且效能劣化，無參考價值。
- 定位與建議: LCOW 適合開發測試混合環境，不宜依賴於大量 I/O/volume 場景。
- 實務抉擇: 釐清容器引擎與掛載模式特性，避開 LCOW+volume 的大 I/O，或改以 container 內部路徑與對應編排策略。

## 全文重點
作者以自身 Jekyll 部落格建站流程為範例，對比 LCOW 與 Docker for Windows 在不同檔案放置與掛載策略下的效能。LAB1 以實務工作流測量 jekyll build 時間，將來源與目的地分別放在 volume/container 組合，結果顯示：container→container 的效能最佳（約 12 秒）；只要牽涉到 volume，時間大幅拉長，尤其在 LCOW 下 volume→container 要 135 秒，volume→volume 甚至多次失敗（隨機無法寫入）。Docker for Windows 在相同情境下雖變慢，但仍顯著優於 LCOW。作者推測兩者跨越 Windows host 與 Linux VM 的 volume 實作有所差異，影響鎖定、同步與 I/O 途徑。

為更純化觀察，LAB2 改用 dd 寫入 1GB 基準測試，分別在 Windows/Linux、process/hyper-v 隔離，以及寫入 container/volume 的不同組合進行。結果顯示：在 process 隔離與原生環境中，寫 container 與寫 volume 差異很小，接近原生；而一旦採 Hyper-V 隔離，寫入 container 的時間成倍增加。Windows container 在寫 volume 上有明顯優化，延遲增加幅度較小；LCOW 在寫 volume 的表現最差，出現數倍到數十倍的時間膨脹。Windows 10 實測額外加入 Docker for Windows，透過 SMB 掛載的 volume 在大量 I/O 下優於 LCOW。Azure VM 上再開 Hyper-V 的 nested virtualization 實驗則顯示效能嚴重劣化，不具實務參考價值；雲端環境應以調度將容器派往適合其 OS 的節點，用 process 隔離獲得較佳表現。

綜合兩階段實驗，作者認為 LCOW 不該被以單一效能數字否定，而應回到定位：它的價值在於讓 Windows 開發者無縫並存 Windows/Linux 容器、共用網路與 Compose，快速建立混合開發測試環境。若工作流涉及大量小檔 I/O 或需高頻 volume 操作，應避開 LCOW+volume 組合，改用 container 內部目錄、分層建置、或改以 Docker for Windows/原生 Linux；在雲端則以編排讓工作落在對應 OS 的節點上。最後，作者強調選型重點在搞清楚不同引擎與掛載模式的特性與限制，以達到場景最適化，而非陷入「效能數字即信仰」的爭論。

## 段落重點
### LAB1, 測試不同環境下 jekyll 建置時間
以 Jekyll 官方映像為基準，將 source/destination 分別放在 volume 與 container 的三種組合測試。結果：container→container 兩引擎皆約 12 秒、最佳；volume 參與時即大幅惡化。LCOW 的 volume→container 需 135 秒，volume→volume 多次隨機寫入失敗，中斷於不同檔案；Docker for Windows volume→volume 約 120 秒、volume→container 約 36 秒。顯示跨 Windows host 與 Linux VM 的 volume 通道在兩引擎上差異極大，牽涉檔案鎖與同步實作。對開發者的體感差距明顯：迭代從十多秒暴增至數分鐘，迫使作者深入以 I/O 基準測試釐清差異來源。

### LAB2, 不同組態下 container 的 I/O 效率
採用 dd 由 /dev/urandom 寫 1GB 至 container/volume，以 Windows/Linux、process/hyper-v 隔離與 Docker for Windows/LCOW 多組合對照。目標是剝離應用複雜度，直接觀察 I/O 通道本質差異：原生、process 隔離接近原生；Hyper-V 隔離跨 OS 邊界後影響顯著。搭配多台實體機與 Azure VM（nested virtualization）驗證趨勢一致性。特別對比 LCOW 與 Docker for Windows 的底層差異：LinuxKit vs MobyLinux、每容器專屬 VM vs 共用 VM，以及與 Windows 容器的並存能力，說明其在掛載與網路路徑上的不同，形成實測結果分歧的基礎。

### 測試方式
以相同映像與參數控制變因：dd if=/dev/urandom of=./largefile bs=1M count=1024，5 次取平均。記錄 platform（windows/linux）、isolation（none/process/hyperv）、寫入位置（container/volume）。硬體分三組：兩台實體 PC 與一台 Azure DS4 v3 VM。為避免跨機比較誤差，僅在同組硬體內比較數據，跨組僅作參考。補充 Windows 隔離模式差異：process 低開銷、hyper-v 高隔離；Windows 10 對 process 支援受限；Docker for Windows 以專用 Linux VM 執行 Linux 容器並經 SMB 掛載。

### LAB2-1, Windows Server 1803 (實體PC)
在 Windows Server 上，原生寫入約 1.57s。Windows container（process）寫 container/volume 分別約 1.57/1.64s，與原生幾乎一致。切換 hyper-v 隔離後，寫 container 膨脹至 5.90s（+276%），寫 volume 為 2.21s（溫和增幅）。LCOW（linux/hyper-v）寫 container 為 4.85s（較佳於 Win hyper-v），但寫 volume 暴跌至 21.33s（約 13 倍），凸顯 LCOW 在跨 host volume 路徑上缺乏優化，與 Windows container 在 volume 上的最佳化形成強烈對比。

### LAB2-2, Windows 10 1803 (實體PC)
Windows 10 因限制無 process 隔離對照；Windows hyper-v 寫 container/volume 約 4.58/5.60s。LCOW（hyper-v）寫 container 6.38s、寫 volume 高達 41.14s，延續在 volume 的劣勢。Docker for Windows（hyper-v 共用 VM）寫 container 6.22s、寫 volume 9.10s，雖慢於原生，但遠優於 LCOW 的 volume 成績；SMB 掛載帶來可預期但可接受的遞減。此組數據強化觀察：LCOW 的 volume 通道是主要瓶頸，而 DfW 的設計在大量小檔 I/O 上更穩定。

### LAB2-3, Azure D4S VM
在雲 VM 上再開 Hyper-V 的 nested virtualization，數據整體異常偏慢：Windows hyper-v 寫 container 達 66.82s，Linux hyper-v 寫 container/volume 亦高。雲端磁碟層多為遠端儲存或抽象層，疊加虛擬化開銷，導致結果不具實務參考性。作者建議在雲端應以編排（Swarm/K8s）將 Windows/Linux 工作負載派至對應 OS 的節點，使用 process 隔離以保有接近原生的 I/O 表現，避免 nested 虛擬化的非必要懲罰。

### 測試結果解讀
關鍵洞見：在不跨越 OS 邊界（原生或 process 隔離）時，寫入 container/volume 幾乎無差；一旦跨 OS 並採 Hyper-V，寫 container/volume 均有不同程度懲罰。Windows container 在寫 volume 上具優化，增幅較小；LCOW 在寫 volume 表現最差，亦與 LAB1 的 Jekyll 大量檔案生成結果吻合。Docker for Windows 的 SMB 掛載在大量小檔情境下比 LCOW 更可用。總之，影響主因包含：跨 VM 的檔案系統路徑、鎖定/flush 時機、實作差異（LinuxKit vs MobyLinux）、獨立 VM vs 共用 VM。

### 結論
LCOW 不該被單一效能數字抹煞，其價值在於：讓 Windows 環境可同時運行 Windows/Linux 容器、共用網路與 Compose，極適合開發測試混合場景與 .NET 開發者體驗。然而在大量 I/O 或重度仰賴 volume 的工作流，應避免 LCOW+volume 組合，改以 container 內部路徑、分層產出、中繼快取，或改用 Docker for Windows/原生 Linux 執行；雲端以調度落位至對應 OS 節點並偏好 process 隔離。核心建議：先釐清容器引擎與掛載模式的邊界，再做場景化選擇，而非陷入「效能即信仰」的誤區。附錄提供完整 LAB1/Jekyll 與 Azure 系統資訊，以供重現與參考。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 容器基本概念：Image/Container、Union FS（如 AUFS/OverlayFS）、Volume
   - Windows 與 Linux 容器差異：Windows Container 的 process/hyper-v 隔離模式
   - Hyper-V、VM 與「跨 Host-VM I/O」的基本理解（SMB/9P/虛擬磁碟）
   - 基本 I/O 測試工具與方法（dd、block size、count 概念）

2. 核心概念（3-5 個）及關係：
   - LCOW（Linux Container on Windows）：在 Windows 上以 Hyper-V 啟動 LinuxKit VM 來跑 Linux 容器；每個容器可對應獨立 VM
   - Docker for Windows（Linux 模式）：以單一 MobyLinux VM 承載所有 Linux 容器；Windows 與 VM 之間多透過 SMB 分享檔案
   - 隔離層級（process vs hyper-v）：process 高效、hyper-v 隔離更強但 I/O 成本更高
   - Volume I/O 路徑：容器內部 FS vs 掛載 Host Volume，跨越 Host—VM 邊界會顯著拉低效能，且在 LCOW 尤劇
   - 工作負載模式：大量小檔/檔案產生（如 Jekyll build）對跨 VM 的 Volume I/O 特別敏感

   關係：隔離層級與執行架構（LCOW vs Docker for Windows）決定 I/O 路徑；I/O 路徑決定 Volume 的效能與穩定性；工作負載模式放大或緩解此效能差距。

3. 技術依賴：
   - LCOW 依賴 Hyper-V 與 LinuxKit；每容器一 VM 的模型
   - Docker for Windows（Linux 模式）依賴 Hyper-V 與 MobyLinux 單一 VM、SMB 分享
   - Windows Container 的 process/hyper-v 隔離機制
   - 檔案系統與共享機制：AUFS/OverlayFS、SMB、虛擬磁碟
   - 平台與硬體：Windows Server/Windows 10、Azure VM（Nested Virtualization 的限制）

4. 應用場景：
   - 本機開發與測試：同時需要 Windows 與 Linux 容器的混合環境（LCOW 優勢）
   - I/O 密集但可放在容器內部檔案系統的建置流程（容器→容器最佳）
   - 需透過 Volume 與 Host 互動但 I/O 量不大的情境
   - 生產環境：以編排（Swarm/K8s）將 Windows/Linux 容器派到對應 OS 的節點（避免跨 OS/VM I/O）

### 學習路徑建議
1. 入門者路徑：
   - 了解容器與 Volume 基礎、Windows 與 Linux 容器差異
   - 安裝 Docker for Windows/設定 LCOW，跑第一個 Windows 與 Linux 容器
   - 練習容器內部與 Volume 間的檔案操作，觀察基本差異

2. 進階者路徑：
   - 深入理解隔離層級（process/hyper-v）對 I/O 的影響
   - 學習 LCOW 與 Docker for Windows 的架構差異（LinuxKit vs MobyLinux、單/多 VM）
   - 使用 dd/Jekyll 這類實際負載進行基準測試，分析瓶頸點（容器→容器 vs Volume）

3. 實戰路徑：
   - 將 I/O 密集操作盡可能置於容器內部檔案系統（避免跨 VM/Host 的 Volume）
   - 若必用 Volume，依工作負載選擇合適執行架構（例如 Linux 容器走 Docker for Windows 的 SMB 分享比 LCOW 寫 Volume 更穩健）
   - 在雲端以編排器將工作派送到對應 OS 的節點，避免 Nested Virtualization 與跨 VM Volume I/O
   - 建立自動化腳本：開發時複製（sync）來源到容器內建置，建置結果再回寫 Host（僅少量回傳）

### 關鍵要點清單
- 容器→容器 I/O 最快: 同一容器內或容器內部檔案系統的操作，效能接近原生 (優先級: 高)
- Volume 跨越 Host—VM 成本高: 尤其在 LCOW，對大量小檔 I/O 特別不友善 (優先級: 高)
- 隔離層級影響巨大: process 快、hyper-v 因跨 VM 代價 I/O 顯著變慢 (優先級: 高)
- LCOW 與 Docker for Windows 架構差異: LCOW 每容器一 VM、DfW 單 VM；I/O 行為與效能不同 (優先級: 高)
- Jekyll 實測結果指引: 容器→容器約 12s，LCOW volume→container 可達 135s，差距懸殊 (優先級: 高)
- LCOW volume 寫入不穩定案例: volume→volume 發生「Operation not permitted」隨機錯誤 (優先級: 高)
- Windows Container 在 process 模式表現佳: 寫入 container/volume 與原生差距小 (優先級: 中)
- Docker for Windows 的 Volume 走 SMB: 在某些工作負載下比 LCOW 寫 Volume 穩定與較優 (優先級: 中)
- Azure Nested Virtualization 不宜基準測試: 雙層虛擬化與遠端儲存使 I/O 效能無參考價值 (優先級: 中)
- 開發者為 LCOW 最佳對象: 混合 Windows/Linux 容器、共用網路與 Compose 的便利性高 (優先級: 高)
- 生產部署建議以原生 OS 節點承載: 透過編排把容器派到對應 OS，避免跨 VM I/O (優先級: 高)
- 大量檔案建置策略: 將原始碼複製到容器內建置，結果再小量回寫，縮短 Volume 熱點 (優先級: 中)
- 測試方法學: 使用 dd 控制 bs/count 與目標（container/volume），多次取平均 (優先級: 中)
- 文件系統與共享機制理解: AUFS/OverlayFS、SMB、LinuxKit/MobyLinux 對 I/O 行為的影響 (優先級: 中)
- 正確認知與選型: 依任務與場景選 LCOW 或 Docker for Windows，不以單一數字做結論 (優先級: 高)