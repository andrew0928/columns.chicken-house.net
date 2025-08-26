# .NET Core 跨平台 #3, 記憶體管理大考驗 - Windows Container (2016 TP)

## 摘要提示
- 測試目的: 比較 .NET Core 在不同 Windows 平台上的記憶體管理表現，特別關注碎片化後的可用記憶體比例
- 測試方法: 每次以全新啟動、拉取套件、就地編譯，連續執行兩次取第二次數據，並以「Phase1/Phase3」計算利用率
- 對照組環境: Windows Server 2012 R2 Server Core，最小化安裝、無 GUI，以指令作業
- 2012 R2 結果: Phase1 可得 4416MB、Phase3 剩 2888MB，記憶體利用率 65.40%
- 2012 R2 觀察: dnx.exe 佔用約 4548MB，實體 RAM 1GB 幾乎吃滿，後續由分頁檔支撐
- 2016 Nano + Container: 首度體驗 Windows Container，使用與 Docker 相容的管理介面於 Windows 上建立容器
- 2016 Nano 結果: Phase1 可得 4032MB、Phase3 剩 2696MB，記憶體利用率 66.87%
- Container vs VM: 透過工作管理員可見容器內程序，證明與主機共用同一 Kernel，效能接近原生
- Hyper-V Container: 新增 Kernel 隔離選項，必要時以 Hyper-V 建 VM 承載容器，兼顧隔離與容器優勢
- 實務體驗: TP4 還在預覽，互動模式反應稍慢；期待正式版優化與更完整生態

## 全文重點
本文延續前一篇的記憶體碎片化測試，將焦點放在 Windows 平台，選取兩個環境：成熟的 Windows Server 2012 R2 Server Core 作為對照組，以及首次支援容器技術的 Windows Server 2016 Nano (Tech Preview 4)。作者以統一流程實驗：每次在受測平台以原始碼就地編譯，從系統重開機開始，依序拉取套件、編譯，連續執行兩次取第二次，以避開首啟最佳化干擾。評估指標為記憶體利用率，即 Phase1 能取得的最大記憶體為分母，經過碎片化後 Phase3 能再次取得的記憶體為分子。

在 2012 R2 Server Core 上，系統分頁檔預設為 4GB，加上實體 RAM 1GB。測試顯示 Phase1 可拿到 4416MB，碎片化後 Phase3 仍可拿到 2888MB，利用率 65.40%。從工作管理員觀察，執行 .NET Core 的 dnx.exe 最高佔用約 4548MB；效能圖顯示啟動初期實體記憶體很快用盡，後續主要依賴虛擬記憶體與分頁檔，符合預期。整體表現穩定，無顯著額外開銷。

接著在 Windows Server 2016 Nano 進行 Windows Container 測試。2016 引入與 Docker 相容的管理工具與操作模型，但容器映像需使用 Windows 基底（如 Server Core），無法共用 Linux 映像。作者以互動模式進行容器內建置與測試，雖然 TP4 的互動體驗偏慢，但功能可用。結果顯示 Phase1 可取得 4032MB，Phase3 為 2696MB，利用率 66.87%，與 2012 R2 相近甚至略優。

進一步以主機的工作管理員觀察容器內的程序，證實容器與主機共享同一 Kernel，與 VM 的完全隔離不同，因此資源使用更有效率、效能更貼近原生。除了標準 Windows Container，2016 亦新增 Hyper-V Container 概念：當需要達到 Kernel 等級隔離時，系統會以 Hyper-V 啟動輕量 VM 作為容器宿主，讓使用者在安全隔離與容器效率間取得平衡。本文未深入實測 Hyper-V Container，但提供參考資料以利後續探索。

總結而言，.NET Core 在 Windows 2012 R2 與 2016 Nano Container 的記憶體回收與再配置行為相當接近，碎片化後的可用記憶體仍維持約 65%–67% 的水準，顯示容器模式下幾乎沒有顯著的額外負擔。TP4 雖有互動延遲，但預期正式版將改善。對追求部署一致性與資源效率的 .NET 團隊而言，Windows Container 與未來的 Hyper-V Container 提供了靈活的選擇與演進方向。

## 段落重點
### Windows 2012R2 Server Core（對照組）
作者選用最精簡的 Server Core 作為對照，所有操作以指令完成，並保持各平台測試流程一致：重啟、抓套件、編譯，連跑兩次取第二次。環境預設分頁檔 4GB，實體 RAM 1GB。測試顯示 Phase1 最大可取得 4416MB 記憶體，經刻意製造碎片化後，Phase3 可再取得 2888MB，換算記憶體利用率 65.40%。從工作管理員觀察，dnx.exe 峰值約 4548MB，實體記憶體在啟動初期即被吃滿，之後主要倚賴虛擬記憶體，曲線與預期一致。整體而言，2012 R2 在記憶體回收與再配置的表現中規中矩，無明顯額外開銷；Server Core 無 GUI 有助減少干擾，利於客觀比較。

### Windows Server 2016 Nano（TP4）與 Windows Container
Windows Server 2016 首度引入 Windows Container，提供與 Docker 相容的管理體驗，但由於容器需共用主機 Kernel，影像需使用 Windows 基底（如 Server Core），無法直接用 Linux 映像。作者以互動模式在容器內建置 .NET Core 測試，TP4 反應略慢但可用。結果 Phase1 最大可取得 4032MB，Phase3 為 2696MB，利用率 66.87%，與 2012 R2 接近甚至略優。透過主機工作管理員可見容器內程序，證明容器與主機共用 Kernel，並非 VM 等級的完全隔離，因而資源使用更有效率、效能接近原生。另介紹 Hyper-V Container：在需要 Kernel 隔離時，由 Hyper-V 啟動輕量 VM 作為容器宿主，兼顧安全與效率。本文未實測此模式，但提供延伸閱讀並期待後續版本在效能與體驗上的優化。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - .NET Core 基礎與執行模型（當時為 DNX 執行時）
   - 記憶體管理概念：實體記憶體、虛擬記憶體、Pagefile、記憶體碎片化
   - 容器基礎概念：Docker CLI、生態與 Image、Container 與 Host Kernel 的關係
   - Windows Server 版本與模式：2012 R2 Server Core、2016 Nano/TP4、Windows Containers、Hyper-V Containers

2. 核心概念：
   - 記憶體管理測試方法：三階段（重開機→下載套件→編譯→連跑兩次取第二次），以 Phase1/Phase3 比值為「記憶體利用率」
   - Windows Server 2012 R2 Server Core 作為對照組（原生、成熟、無 GUI）
   - Windows Server 2016 Nano + Windows Containers：Docker 相容工具、共用 Host Kernel 的隔離模式
   - Hyper-V Containers：在需要 Kernel 隔離時以 VM 包覆 Container，兼顧隔離與 Container 體驗
   - 效能觀察：Container 與原生差異小；Preview 版互動延遲偏高

3. 技術依賴：
   - .NET Core（DNX 時期）在 Windows 上的執行
   - Windows Containers 需依賴與 Host 相同的 Windows Kernel
   - Docker/PowerShell 管理工具在 Windows 上的相容層
   - Pagefile 設定影響可用虛擬記憶體上限與測試結果

4. 應用場景：
   - 比較不同宿主（原生 vs 容器）下 .NET Core 記憶體使用與回收效率
   - 選型決策：在 Windows 上部署 .NET Core 時，評估使用原生、Windows Containers 或 Hyper-V Containers
   - 監控與診斷：利用 Task Manager/效能監視來觀察容器內程序行為
   - 針對碎片化工況的壓力測試與容量規劃

### 學習路徑建議
1. 入門者路徑：
   - 了解 .NET Core 與基本記憶體概念（RAM/Virtual Memory/Pagefile）
   - 認識容器基本概念與 Docker 常用指令
   - 在 Windows 2012 R2/2016 環境建立最小可行測試：拉程式碼→編譯→執行→以 Task Manager 觀察

2. 進階者路徑：
   - 在 Windows Server 2016 Nano 上建置 Windows Container，手動建立基底 Image（Server Core）與相依環境
   - 實作三階段記憶體碎片化測試，量測 Phase1/Phase3 與利用率
   - 比較原生 vs Windows Container 的差異，加入 Pagefile、RAM 配置與 GC 設定的敏感度分析

3. 實戰路徑：
   - 將現有 .NET Core 服務封裝為 Windows Container，建立重現性測試 Pipeline
   - 加入 Hyper-V Containers 測試情境（需 Kernel 隔離時），評估啟動、效能與隔離性
   - 擴充到 Linux/Docker 平台作跨平台比較，產出部署與資源規劃指引

### 關鍵要點清單
- 測試流程設計：重開機→拉套件→編譯→連跑兩次取第二次，降低冷啟動偏差（優先級: 高）
- 記憶體利用率指標：利用率 = Phase3 可得記憶體 / Phase1 可得記憶體（優先級: 高）
- 2012 R2 結果：Phase1=4416MB、Phase3=2888MB、利用率=65.40%（優先級: 高）
- 2016 Nano+Container 結果：Phase1=4032MB、Phase3=2696MB、利用率=66.87%（優先級: 高）
- Pagefile 影響：預設 4GB Pagefile + 1GB RAM 對可分配記憶體上限影響顯著（優先級: 中）
- 碎片化效應：刻意碎片化後 Phase3 可得記憶體顯著下降，驗證碎片化對配置能力的影響（優先級: 高）
- 容器與 Kernel 關係：Windows Containers 與 Host 共用 Kernel，非 VM 級完全隔離（優先級: 高）
- 效能觀察：容器下效能接近原生，Preview 期間互動性可能較差（優先級: 中）
- 管理工具：Windows 提供 Docker 相容 CLI 與 PowerShell 管理容器（優先級: 中）
- Task Manager 驗證：可於 Host 看到容器內程序，佐證共用 Kernel 模式（優先級: 中）
- Hyper-V Containers：需 Kernel 隔離時，以 VM 包覆容器以提升隔離性（優先級: 中）
- 部署取捨：原生 vs Windows Containers vs Hyper-V Containers，依效能、隔離、管理便利性選擇（優先級: 高）
- DNX 背景：文中 .NET Core 為早期 DNX 時期，數值具相對比較價值，概念仍適用（優先級: 低）
- 實務建議：以容器化建立可重現的壓力測試，並納入 RAM/Pagefile/GC 設定變因（優先級: 高）
- 監控方法：結合 Task Manager/效能監視器觀測記憶體曲線與分配行為（優先級: 中）