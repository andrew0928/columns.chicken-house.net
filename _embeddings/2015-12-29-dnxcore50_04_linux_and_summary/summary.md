# .NET Core 跨平台 #4, 記憶體管理大考驗 – Docker @ Ubuntu / Boot2Docker

## 摘要提示
- 測試環境: 以 Ubuntu Server 15.10 與 Boot2Docker 兩種 Linux 容器環境測試 .NET Core CLR 記憶體配置表現
- SPARSE 行為: 未初始化記憶體在 Linux 上呈現類似 sparse file/SPARSEMEM 的虛擬配置現象，導致誇張的可配置數字
- 程式修正: 以亂數初始化配置到的 byte 陣列，避免因未初始化而出現虛胖的記憶體統計
- OOM Killed: Linux 容器下偶發直接被 OS 終止（Killed）而非丟出 .NET OOM 例外
- Swap 關鍵: Ubuntu 預設 swap 僅 1GB，調到 4GB 後可配置量與回收率大幅改善
- Ubuntu 成績: 修正 swap 後可配置 4864MB、回收後 4808MB，回收率 98.85%
- Boot2Docker 特性: 輕量、RAM 運作、預設不依賴 HDD 與 swap，測試中易出現 swap I/O 錯誤與不穩定
- Boot2Docker 成績: 第一階段 832MB、第三階段 736MB，回收率 88.46%
- 跨平台對照: Linux 整體記憶體回收效率（%）普遍優於 Windows，但穩定性上 Windows 較成熟
- 結論建議: 正式環境建議用 Ubuntu/Windows；Boot2Docker 僅適合測試與快速體驗

## 全文重點
本文延續 .NET Core 跨平台系列，針對 Linux 家族在容器情境下的記憶體管理進行壓力測試，選用兩種環境：標準安裝的 Ubuntu Server 15.10（搭配 Microsoft .NET Core CLI 容器）與 Boot2Docker（Docker Toolbox 內的極輕量 Linux）。作者原本在 Ubuntu 測得極高的可配置數字（數百 GB），意識到是 Linux 對未初始化記憶體的「虛擬配置」行為，類似檔案系統的 sparse file；於是修改程式，在每次配置後以亂數初始化，排除 SPARSEMEM 類效應，以取得實際可用的配置上限。

測試過程中，Linux 容器偶發在高壓下被 OS 直接終止（Killed），來不及拋出 .NET 的 OutOfMemoryException，顯示在某些緊繃情況下 Linux 端 CLR/容器的保護或回報機制仍有改進空間。另一個關鍵誤判是 swap 設定：Ubuntu 預設只有 1GB swap，與 Windows Server 預設 4GB pagefile 不等，導致早期數據偏低。調整 Ubuntu swap 至 4GB 後，重新測得第一階段配置 4864MB、碎片化回收後仍有 4808MB、回收率 98.85%，展現極佳表現。

相較之下，Boot2Docker 由於設計即為輕量、RAM 運作、以 .iso 快速啟動、檔案體積小（~27MB），並非為高負載設計，缺省不依賴 HDD 與 swap，測試中出現寫入 swap 相關錯誤與不穩定，最終在成功一次的結果裡，第一階段僅 832MB，第三階段 736MB，回收率 88.46%。此結果不代表 Linux Kernel 能力不足，而是 Boot2Docker 的產品定位與組態所致。

綜合比較顯示：Ubuntu（調整後）在可配置記憶體與碎片後回收兩方面皆接近滿分；Linux 在回收效率百分比上普遍優於 Windows，但穩定性與例外處理成熟度目前 Windows 仍佔優。Boot2Docker 非正式環境之選，適合教學與快速驗證。作者將待釐清的議題列為後續研究，包括 Linux 未初始化記憶體的具體機制（SPARSEMEM）、Linux CLR 在 OOM 下的行為、以及 Windows Server GC 參數（如 gcServer、compaction）對碎片化的影響。

## 段落重點
### #3. Ubuntu Server 15.10 + Microsoft .NET Core CLI Container
作者以最小化的 Ubuntu Server（僅裝 SSH 與 Docker Engine）拉下 Microsoft .NET Core CLI 映像進行測試。初測出現誇張的可配置記憶體（數百 GB），推論為 Linux 對未初始化記憶體的「稀疏分配」行為，類似檔案系統的 sparse file，記憶體真實未被實體化。為矯正，修改程式在每次配置後以亂數初始化，逼迫實際佔用。隨後在多次測試中偶發出現「Killed」訊息，顯示在極端記憶體壓力時，Linux 可能直接終止程序而非讓 CLR 拋出 OOM 例外，暴露容器環境下的穩定性差異。進一步檢查發現 Ubuntu 預設 swap 僅 1GB，與 Windows Server 的 4GB pagefile 不一致，導致早期結果保守。調整 swap 至 4GB 後再測，取得 4864MB 配置、回收後 4808MB、回收率 98.85%，顯示 Ubuntu 在記憶體回收與抗碎片上非常優秀。

### #4. Boot2Docker + Microsoft .NET Core CLI Container
Boot2Docker 為極輕量、以 RAM 運作的 Linux 發行版，提供 .iso 即開即用，並預裝 Docker Engine，部署迅速。但由於其設計並非面向高負載，預設不依賴硬碟與 swap，因此在相同測試下，若未初始化記憶體亦出現類似 SPARSE 行為，初看可配置數字膨脹。改為初始化後，系統在第一階段常就不穩定終止，虛擬主控台也出現疑似 swap I/O 錯誤訊息。多次嘗試後取得一次完整結果：第一階段 832MB、第三階段 736MB、回收率 88.46%。作者強調此結果反映的是 Boot2Docker 的定位與預設組態，而非 Linux 核心實力；它適合教學與快速測試，不建議作為正式環境承載高記憶體壓力工作負載。

### #5. 綜合比較 & 結論
作者以表格與圖表統整各平台三階段可配置量與碎片化後回收比率。歸納結論：1) Ubuntu（修正 swap 後）是記憶體管理表現最佳的平台，無論配置上限或碎片後回收都近乎完美，但 Linux 端偶發的「Killed」終止現象提醒其在極端 OOM 情境的穩定度與錯誤回報仍需實務驗證；2) Linux 的回收效率（%）整體優於 Windows，可能涉及 CLR 實作或 OS 差異；3) Boot2Docker 因輕量化設計、RAM 運作、無預設 swap 與保守資源配置，僅適合測試用途。最後列出待研究題目：Linux 未初始化記憶體的 SPARSEMEM 具體行為與條件、Linux 上 CLR 在 OOM 下為何有時來不及丟例外、以及 Windows 端 GC 參數（如 gcServer、compact collection）對碎片化的改善效果，留待日後延伸實驗。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本作業系統概念：虛擬記憶體、Swap、OOM Killer、Sparse file/sparse memory
   - .NET/CLR 與 GC 概念：記憶體配置、碎片化、回收策略
   - 容器基礎：Docker image/container、容器與主機資源關係
   - Linux 與 Windows 在記憶體管理的差異概念

2. 核心概念：
   - .NET Core 在 Linux/Docker 下的記憶體配置行為：CLR 分配策略、碎片化後再分配能力
   - Linux 的「未初始化記憶體不實佔用」行為：類 Sparse 的配置，需初始化才能反映真實使用
   - Swap 配置對測試結果的決定性影響：Swap 大小直接影響可分配總量與穩定性
   - OOM/Killed 行為與例外處理差異：Linux 下可能被 OS 直接殺掉而非丟出 .NET 例外
   - Boot2Docker 的定位與限制：RAM-only/輕量，不適合高負載記憶體測試或正式環境

3. 技術依賴：
   - .NET Core CLI 容器映像（Microsoft 提供的 dotnet CLI image）
   - Docker Engine（於 Ubuntu、Boot2Docker 上執行）
   - Linux Kernel 記憶體特性（SPARSEMEM、Swap、OOM）
   - 主機/VM 設定（RAM、虛擬磁碟、Swapfile/pagefile 大小）

4. 應用場景：
   - 交叉平台記憶體管理行為驗證（Windows vs Linux）
   - 容器化環境下的記憶體壓力測試與碎片化觀察
   - 雲端/容器部署前的資源配置指引（Swap、限制與行為預期）
   - 選型與環境建議（正式環境用 Ubuntu/Windows Server，Boot2Docker 僅用於開發測試）

### 學習路徑建議
1. 入門者路徑：
   - 了解虛擬記憶體與 Swap 的基本概念
   - 安裝 Docker 與拉取 Microsoft .NET Core CLI 映像
   - 在 Ubuntu/Boot2Docker 上執行簡單 .NET Core 程式

2. 進階者路徑：
   - 撰寫記憶體壓力測試程式，觀察初始化與未初始化的差異（rnd.NextBytes 強制實佔）
   - 調整 Linux Swapfile（如由 1GB 改為 4GB）並比較影響
   - 觀察 OOM/Killed 行為、記錄日誌與系統訊息（dmesg、/var/log）

3. 實戰路徑：
   - 建立自動化壓測腳本於 CI/CD 中，於多環境（Windows/Ubuntu/Docker）回報可用記憶體與回收率
   - 對正式環境制定 Swap 與容器資源限制（memory/cpu 限制、swap accounting）
   - 針對 .NET GC 參數（如 Server GC、compact/工作站模式）進行 A/B 測試與監控

### 關鍵要點清單
- Linux 未初始化記憶體的「類 Sparse」行為：未初始化的分配不會真實佔用，需寫入初始化才能反映（優先級: 高）
- 強制初始化技巧：以 rnd.NextBytes 對 buffer 寫入，避免誤判可用記憶體（優先級: 高）
- Swap 大小的關鍵性：Ubuntu 預設 1GB swap 會限制可分配量；調至 4GB 後大幅改善（優先級: 高）
- Ubuntu 成績與穩定性：調整後可達約 4864MB/98.85% 再分配效率，整體最佳（優先級: 高）
- OOM/Killed 行為：Linux 在嚴重不足時可能直接 kill 進程，例外拋出不一定可見（優先級: 高）
- Boot2Docker 定位：輕量、從 RAM 執行、預設無/弱化 swap，不適合高負載或正式環境（優先級: 高）
- 環境差異的重要性：同為 Linux，不同發行版/組態（Ubuntu vs Boot2Docker）表現差異大（優先級: 中）
- GC 與碎片化影響：碎片化後的再分配效率是觀察重點，Linux 多數情況可達 90%+（優先級: 中）
- Windows 對照：Windows Server 在 CLR 穩定性（例外可見）經驗較成熟，但本文主體為 Linux 面（優先級: 中）
- 測試方法學：需控制變因（RAM、磁碟、Swap、同一版本 CLI/映像）以獲得可比較結果（優先級: 中）
- 監控與診斷：善用系統訊息（swap 寫入錯誤、dmesg）協助定位隨機失敗（優先級: 中）
- 容器資源限制：Docker 預設可能不限制記憶體，建議明確設定並與主機 swap 策略協同（優先級: 中）
- Boot2Docker 實測結果：成功案例約 832MB/736MB、88.46%，且常見隨機失敗（優先級: 低）
- Sparse file 概念延伸到記憶體：檔案系統的 Sparse 思維可類比到記憶體行為（優先級: 低）
- 未解之處與後續研究：SPARSEMEM 實作細節、Linux CLR 在 OOM 場景的行為、GC 參數影響（優先級: 低）