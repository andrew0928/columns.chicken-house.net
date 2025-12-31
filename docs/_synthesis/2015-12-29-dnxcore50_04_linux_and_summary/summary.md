---
layout: synthesis
title: ".NET Core 跨平台 #4, 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker"
synthesis_type: summary
source_post: /2015/12/29/dnxcore50_04_linux_and_summary/
redirect_from:
  - /2015/12/29/dnxcore50_04_linux_and_summary/summary/
postid: 2015-12-29-dnxcore50_04_linux_and_summary
---

# .NET Core 跨平台 #4, 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker

## 摘要提示
- 測試目標: 比較 .NET Core 在 Linux（Ubuntu、Boot2Docker）上的記憶體配置與回收行為
- SPARSE 文件/記憶體: 未初始化記憶體在 Linux 可能採類似 SPARSEMEM 策略，導致「誇張」可配置量
- 程式修正: 以亂數初始化陣列，避免「未初始化」造成的錯誤觀察
- Ubuntu 測試: 調整 swap 後可配置與回收表現接近完美（4864MB/4808MB，98.85%）
- 交換空間影響: Ubuntu 預設僅 1GB swap，與 Windows 預設 4GB pagefile 造成初期誤判
- Boot2Docker 特性: 輕量、RAM 運行、預設無持久 swap，非為高負載設計
- Boot2Docker 表現: 易遇寫入 swap 錯誤與隨機失敗，成功時回收率約 88.46%
- 例外處理差異: Linux 上偶見進程被 OS 直接 Killed，未拋出 OOM 例外
- 整體比較: Ubuntu 記憶體管理最佳、Linux 回收效率高於 Windows、Boot2Docker 僅宜測試
- 待解問題: Linux 初始化記憶體機制、CLR 在 OOM 情境穩定性、Windows gcServer 參數效應

## 全文重點
本文延續先前在 Windows 家族上的 .NET Core CLR 記憶體測試，轉向 Linux 環境，選用 Ubuntu Server 15.10 與 Boot2Docker（Docker Toolbox 內的精簡 Linux）進行容器化測試。初測在 Linux 上出現「超大可配置記憶體」的離奇結果，作者回想起作業系統中 Sparse file 概念，進而推測 Linux kernel 存在類 SPARSEMEM 策略：未初始化的記憶體區塊實際並未被真正配置。為驗證此點，將測試程式調整為對新配置的陣列以亂數填充，避免「未初始化」最佳化，使量測回到現實。

在 Ubuntu 下，初期僅能配置到約 2GB，後發現關鍵在交換空間（swap）預設值差異：Windows 預設約 4GB 的 pagefile，而 Ubuntu 安裝程式預設只建立 1GB /swapfile。將 Ubuntu swap 調整至 4GB 後重測，得到 4864MB 可配置、第三階段回收後仍可配置 4808MB，回收效率達 98.85%，代表在碎片化後仍能近乎完全回收大區塊記憶體。不過，Linux 版 CLR 在壓力場景偶見被 OS 直接 Killed 的狀況，連 OOM 例外都無法丟出，顯示在極端壓力下穩定性與 Windows 有別。

Boot2Docker 部分，因其設計為超輕量、RAM 運行、非持久化磁碟且預設不強依賴 swap，測得行為更受限制。未初始化時同樣出現「超大可配置量」，改用初始化版本後，常見寫入 swap 錯誤與隨機失敗；少數成功案例顯示第一階段 832MB、第三階段 736MB，回收率 88.46%。整體來看，Boot2Docker 適合快速拉起 Docker 環境作測試與開發驗證，但不宜作為高負載或正式環境基礎。

綜合比較顯示：Ubuntu 的記憶體管理與回收表現最佳；Linux 整體在碎片化後的可回收比例普遍高於 Windows；Boot2Docker 因產品定位而偏保守，資源調度受限。文末列出待查議題，包括 Linux 的初始化記憶體策略、CLR 在被 OOM 觸發時的行為差異，以及 Windows gcServer（compact collection）對碎片化的潛在改善，留待後續深入。

## 段落重點
### 前言與問題啟發：從 Windows 轉進 Linux，遇上「超大記憶體」
作者將 .NET Core 記憶體測試從 Windows 延伸至 Linux，選定 Ubuntu Server 15.10 與 Boot2Docker。初測在 Linux 出現「1GB RAM 卻能配置數百 GB」的詭異數據，聯想到作業系統課中的 Sparse file 概念，推測 Linux kernel 對未初始化記憶體採行類 SPARSEMEM 策略：在程式尚未寫入內容前，實際硬體或交換空間並未真正配置，因而導致測得的「可配置量」失真。為修正觀測偏差，作者修改程式在配置後以亂數初始化陣列，強制實配記憶體，避免因全零或未寫入而被壓縮或延遲配置。此舉讓測試更貼近真實行為；同時也觀察到在 Linux 壓力場景中，CLR 有時會被 OS 直接 Killed，連 OOM 例外都來不及丟出，與過往在 Windows 環境中通常能收到例外的經驗不同，顯示平台在極端記憶體壓力下的防護與錯誤傳遞路徑有差異。

### #3. Ubuntu Server 15.10 + Microsoft .NET Core CLI Container
Ubuntu 採標準安裝，只加 SSH 與 Docker Engine，拉取 Microsoft 提供的 dotnet CLI 映像後即測。以初始化版本程式重跑後，起初結果約 1.7GB～2GB，可疑。深究發現癥結在 swap 預設值：Windows Server 預設有約 4GB 的 pagefile，Ubuntu 安裝預設僅建立 1GB /swapfile。調整 Ubuntu swap 至 4GB 後再測，成績躍升：第一階段可配置 4864MB，經碎片化釋放再配置後仍達 4808MB，回收效率 98.85%，幾近完美。此結果顯示在容器情境下，Linux 的記憶體回收與碎片化抵抗力非常強，只要底層交換空間配置合理，.NET Core 在 Linux 上的 GC 與配置策略就能展現良好表現。不過過程中仍偶見進程被 OS Killed 的狀況，推測在 OOM 風險與 cgroup/容器限制觸發時，Linux 會直接終止進程，導致無法如 Windows 般穩定地拋出 OOM 例外，這對需精準錯誤處理的服務有實務影響。

### #4. Boot2Docker + Microsoft .NET Core CLI Container
Boot2Docker 以 .iso 形式發布、極輕量、開機即用，預先內建 Docker Engine。其設計強調 RAM 運行與快速啟動，非針對高負載或長期運作，因此預設不倚賴持久化磁碟與 swap。測試中同樣出現未初始化導致「可配置數百 GB」的假象，改用初始化版本後，常見與 swap 寫入相關的錯誤訊息與隨機失敗，顯示在資源緊縮與 I/O 限制下其穩定性不足。少數成功案例顯示第一階段可配置 832MB、第三階段 736MB，回收率約 88.46%，遠遜於 Ubuntu。綜觀其產品定位與打包方式（~27MB、全 RAM、5 秒開機），結論是非常適合在本機與 CI 環境快速拉起容器做功能與流程驗證，但不宜承擔高記憶體壓力或正式上線任務；若要在類似環境追求穩定表現，需自行設計持久化儲存與交換空間策略，或改用更完整的 Linux 發行版作為宿主。

### #5. 綜合比較與結論（含 Boot2Docker 補充與待解問題）
整合四平台（含前文 Windows 系列）的三階段記憶體配置量與碎片化後回收比例可知：Ubuntu Server 在可配置量與回收效率上表現最佳，達 4864MB/4808MB 與 98.85%，幾近理想；Linux 整體在碎片化後的可回收比例普遍高於 Windows，顯示 GC 與 OS 記憶體管理在此場景更有利。不過 Linux 版 CLR 在壓力極限時偶會被 OS 直接終止，缺乏可預期的例外通報；相比之下，Windows 的例外傳遞較可依賴。Boot2Docker 則因設計取向（輕量、RAM 運作、非持久 swap）而資源使用受限、錯誤較多，建議僅作測試用途。作者並列出待解議題：一是 Linux 對未初始化記憶體的實際策略與 SPARSEMEM 的關聯；二是 CLR 在 Linux OOM 情境下的終止與例外行為；三是 Windows 的 gcServer（compact collection）是否能改善碎片化並提升回收率。總結來看，若以正式環境穩定與可觀測性為優先，Windows Server 2012 R2 仍具優勢；若著眼於記憶體回收效率與高效配置，妥善設定交換空間的 Ubuntu Server 表現亮眼；Boot2Docker 則維持其「快速、輕量、開發測試友善」的定位。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 了解 .NET Core/CLI 與 CLR 的基本概念與記憶體配置行為
   - Linux 基本操作（Ubuntu、swapfile、/proc、dmesg）
   - Docker 基礎（image、container、資源限制與虛擬化環境）
   - 作業系統記憶體管理概念（虛擬記憶體、swap、OOM）
2. 核心概念：
   - 記憶體初始化與 SPARSEMEM：未初始化的已配置記憶體在 Linux 可能不實際占用物理/交換空間，導致誇張的「可配置」數字；透過初始化（填入資料）才能反映真實占用
   - swapfile 配置對測試結果的影響：不同 OS 預設 swap 容量影響最大可配置記憶體與穩定性
   - Docker/Container 與主機資源的關係：container 受限於主機（RAM、swap），以及發行版的設計取向（如 boot2docker 主打輕量與 RAM 運行）
   - CLR/GC 行為差異：Linux 與 Windows 的 CLR 在高壓記憶體情境下表現與例外處理不同；Windows 可見 GC 參數（如 gcServer）可能影響碎片回收
   - OOM 與強制終止：在 Linux 上可能在例外拋出前被 OS 直接 Killed，需從系統層面觀察
3. 技術依賴：
   - .NET Core CLI Container 依賴 Docker Engine 與基礎 Linux/Windows 主機
   - 記憶體測試程式依賴 CLR 配置策略與 OS 的記憶體/交換空間管理
   - swapfile 設定（大小與啟用）影響容器內實際可用虛擬記憶體
   - 初始化行為（亂數填入）依賴 OS 是否實作稀疏記憶體對應機制
4. 應用場景：
   - 在不同平台上評估 .NET Core 容器化服務的記憶體使用上限與碎片回收效率
   - 調校 Linux 主機（Ubuntu）之 swap 配置，以提升容器內高記憶體壓測的穩定性
   - 選擇合適的容器基底（如 Ubuntu vs boot2docker）以符合正式環境或測試環境需求
   - 釐清 OOM 行為與監控策略，避免生產環境中服務被直接 Killed

### 學習路徑建議
1. 入門者路徑：
   - 安裝 Docker Toolbox 或在本機安裝 Docker Engine，拉取 Microsoft .NET Core CLI image
   - 在 Ubuntu（或 WSL/VM）上練習檔案與 swapfile 管理（建立/調整/啟用）
   - 撰寫簡單記憶體配置程式（byte[] 配置與初始化）觀察 top/free/swap 使用
   - 熟悉查看系統訊息（dmesg、/var/log、容器日誌）以理解 OOM/Killed 訊息
2. 進階者路徑：
   - 比較不同容器基底（Ubuntu Server vs boot2docker）的資源行為與限制
   - 研究 CLR/GC 設定（如 Server GC、compact collection）對碎片化與回收比例的影響
   - 引入資源配額（Docker 的 memory/swap 限制）做壓力測試與穩定性驗證
   - 建立監控告警（cgroups、oom_score、Prometheus）以捕捉異常終止前的徵兆
3. 實戰路徑：
   - 在 Ubuntu 主機設定足夠的 swapfile（與生產標準一致），部署 .NET Core 容器服務
   - 進行記憶體壓測與碎片化測試，記錄可用量、回收比例、異常情況
   - 根據結果調整 GC 與容器資源限制，並撰寫復原與重啟策略
   - 明確區分測試與生產用基底映像（避免以 boot2docker 作為生產基底）

### 關鍵要點清單
- Linux 的稀疏記憶體（SPARSEMEM）現象：未初始化的記憶體配置可能顯示超大可用量，需初始化才反映真實占用（優先級: 高）
- 記憶體初始化策略：以亂數填充（而非 0）可避免被最佳化或壓縮影響測試結果（優先級: 中）
- swapfile 尺寸對測試結果的關鍵影響：Ubuntu 預設 1GB 可能導致低可配置量/不穩；調至 4GB 後大幅改善（優先級: 高）
- Windows 與 Ubuntu 設定差異：Windows 預設 pagefile 較大，Linux 須自行調整，直接影響壓測可用記憶體（優先級: 高）
- OOM 與 Killed 行為：Linux 上容器/CLR 可能被 OS 直接終止而無法拋出例外，需用系統層面監控（優先級: 高）
- Ubuntu 在記憶體回收效率的表現：在正確設定下，碎片化後回收比例可達約 98.85%，整體表現最佳（優先級: 中）
- boot2docker 的定位：輕量、RAM 運行、非為正式環境設計，記憶體/交換空間資源保守（優先級: 高）
- 容器基底選型：正式環境建議使用完整發行版（如 Ubuntu Server）而非 boot2docker（優先級: 高）
- CLR/GC 參數影響：Server GC、compact collection 等設定可能改善碎片化回收，需進一步驗證（優先級: 中）
- 資源配額與壓測：對 Docker 設定 memory/swap 限制，結合壓測以驗證穩定性（優先級: 中）
- 監控與日誌：使用 dmesg、容器日誌、cgroups 指標監控 OOM/寫入 swap 錯誤（優先級: 高）
- 程式層面的測試設計：分階段配置/釋放記憶體以量測碎片化影響與回收比例（優先級: 中）
- 平台差異認知：同為 Linux，Ubuntu 與 boot2docker 在資源與行為上仍有顯著差異（優先級: 中）
- 生產穩定性考量：Linux CLR 在極端壓力下的例外行為需風險緩解策略（優先級: 高）
- 實驗結論運用：在調整 swap 與初始化後，Ubuntu 為本測試中表現最佳的平台（優先級: 中）