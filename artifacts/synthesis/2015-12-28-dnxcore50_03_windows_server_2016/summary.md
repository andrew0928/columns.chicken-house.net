# .NET Core 跨平台 #3, 記憶體管理大考驗 - Windows Container (2016 TP)

## 摘要提示
- 測試主題: 以 .NET Core 進行記憶體碎片化測試，對比 Windows 2012 R2 與 Windows Server 2016 容器環境
- 測試方法: 受測平台就地編譯與執行，重啟 VM、下載套件、編譯、連續跑兩次取第二次數據
- 對照組環境: Windows Server 2012 R2 Server Core，強調無 GUI、極簡組態
- 記憶體配置: VM RAM 1GB、系統預設 pagefile 4GB，觀察實體與虛擬記憶體使用
- 2012R2 結果: Phase 1 4416MB、Phase 3 2888MB，利用率 65.40%
- 實務觀察: dnx.exe 最高占用約 4548MB，實體 RAM 幾乎一開始用光，後續倚賴虛擬記憶體
- 2016 容器結果: Phase 1 4032MB、Phase 3 2696MB，利用率 66.87%
- Windows 容器特性: 與 Host 共享同一 kernel，效能接近原生，非 VM 式完全隔離
- Hyper-V Containers: 提供可選的 kernel 隔離，於 VM 中承載容器，兼顧隔離與容器優勢
- 整體結論: Windows 容器在記憶體回收與效率上與原生差距不大，顯示容器化可行性高

## 全文重點
本文延續 .NET Core 跨平台系列，聚焦「記憶體管理大考驗」，以相同測試程式在兩種 Windows 環境比對：Windows Server 2012 R2 Server Core 作為對照組，以及具容器能力的 Windows Server 2016（TP4）。測試流程統一：重啟 VM 後下載所需套件、就地編譯、連續執行兩次取第二次數據，藉由三階段手法製造記憶體碎片並測量可用記憶體，最後以「Phase 3/Phase 1」作為記憶體利用率指標。

2012 R2 Server Core 在 1GB RAM、系統預設 4GB pagafile 下，第一階段最多可取得 4416MB 記憶體；經碎片化再度索取時，第三階段僅得 2888MB，利用率 65.40%。從工作管理員觀察，dnx.exe 最高佔用約 4548MB，實體 RAM 幾乎在啟動初期即用滿，後續主要仰賴虛擬記憶體，符合預期且與測試數據一致。

轉向 Windows Server 2016 TP4 的 Windows 容器測試，第一階段可取得 4032MB，第三階段 2696MB，利用率 66.87%，與對照組相近。作者並從 Host OS 的工作管理員觀測到容器內程序，印證容器與 Host 共享同一 kernel，非 VM 式完全隔離，效能理當更接近原生。進一步指出微軟在容器與 Host 之間提供 Hyper-V Containers：於需要 kernel 隔離時，底層自動以預建映像建立 VM 並在其中承載容器，使得使用者可在隔離與性能之間取得平衡。

整體而言，Windows 容器於記憶體使用與碎片化後的回收效率上與原生 2012 R2 相差不大，顯示在 .NET Core 場景下容器化是可行且具備實用性的方案。雖然 2016 TP4 在互動模式體驗上仍略顯遲滯，但隨產品趨近正式版，微軟的效能調校值得期待。本文最後亦點出後續將進一步於 Ubuntu/Boot2Docker 上進行 Docker 測試與總結，完成跨平台對照。

## 段落重點
### 前言與系列脈絡
作者延續系列文章，將 .NET Core、Linux、Docker 的探索擴展到 Windows 容器。此回針對記憶體管理進行大考驗，著重在不同 Windows 環境下的行為差異。實驗精神是將相同 source code 直接搬到受測平台就地編譯與測試，以降低環境差異帶來的干擾。系列同時規劃對 Linux 與 Docker 的比較，以建立跨平台觀測基準。因為內容較長，作者分篇發布，並在文首列出系列導覽，方便讀者循序閱讀。

### #1. Windows 2012R2 Server Core (對照組)
選擇無 GUI 的 Server Core 作為對照組，目的在降低系統開銷並統一操作風格（以指令為主），也呼應 Linux 測試時的純命令列流程。測試步驟為：重啟 VM、下載套件、編譯、連續執行兩次取第二次數據。環境配置為 1GB RAM、系統預設 pagefile 4GB。測試結果：第一階段可取得 4416MB 記憶體，進行記憶體碎片化後，第三階段僅能取得 2888MB，換算記憶體利用率 65.40%。工作管理員顯示 dnx.exe 最高佔用約 4548MB，實體 RAM 在啟動初期即被吃滿，後續以虛擬記憶體為主；效能頁圖形亦同步反映此現象。整體表現中規中矩，回收並不特別突出，但符合在資源受限（1GB RAM）且有大 pagefile 的預期行為。

### #2. Windows Server 2016 Nano (Tech Preview 4)
Windows Server 2016 首次引入 Windows 容器，並提供與 Docker 相容的管理工具（亦有 PowerShell 版本）。由於容器需共用 Host kernel，無法直接使用 Linux 的映像，需從 Windows Server Core 映像自行建環境。TP4 操作體驗在互動模式下略慢，但預期接近正式版時會優化。測試數據：第一階段可取得 4032MB，第三階段 2696MB，記憶體利用率 66.87%，與 2012 R2 對照組接近。從 Host 的工作管理員可見容器內程序，證明其共享 kernel、非 VM 式完全隔離，使得資源使用更有效率、效能更貼近原生。微軟更進一步提供 Hyper-V Containers：當需要 kernel 隔離時，系統自動以預製映像啟動 VM，並在其中承載容器，使開發者可視需求在隔離與性能間取捨。作者此回未實測 Hyper-V Containers，但提供參考資料與後續研究方向。

### 後續與延伸
本文完成 Windows 平台（2012 R2 對照、2016 容器）之記憶體碎片化測試與觀察，顯示 Windows 容器在記憶體利用與回收上已相當接近原生環境，對 .NET Core 的容器化部署具正面意義。系列下一篇將轉往 Ubuntu 與 Boot2Docker 進行 Docker 實測並做整體總結，期望建立跨 OS、跨容器技術的系統性比較，為日後選型與部署提供實證依據。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本了解 .NET Core 與其執行時（dnx.exe）的運作方式
   - Windows Server 版本與版型（2012 R2 Server Core、2016 Nano/TP4）的差異
   - 容器技術基礎（Docker 概念、容器與 VM 的差異、同核共享）
   - 記憶體管理與分頁檔（RAM、Pagefile、記憶體碎片化）的基本概念
   - 指令列操作與基本監控工具（Task Manager、效能頁面觀察）

2. 核心概念：
   - 記憶體碎片化測試方法：重開機、抓取套件、就地編譯、重複執行兩次取第二次數據
   - 記憶體利用率指標：以 Phase 1 可取得記憶體為分母，Phase 3 重新申請可取得記憶體為分子
   - Windows Container：與 Host 共用同一 Kernel、與 Docker 工具相容但需使用 Windows 映像
   - Hyper-V Container：在需要 Kernel 隔離時，透過 Hyper-V 自動包 VM 再承載容器
   - 對照平台差異：2012 R2 Server Core（成熟、無 GUI） vs 2016 Nano（TP4、容器支援、互動模式較慢）

3. 技術依賴：
   - .NET Core CLR（dnx.exe）依賴目標 OS 的 Kernel 與記憶體管理
   - Windows Container 依賴 Host OS Kernel，共享資源，需 Windows 基底映像（如 Server Core）
   - Docker 工具鏈在 Windows 上的相容與管理（PowerShell/ Docker CLI）
   - Hyper-V 作為容器的 Kernel 隔離後盾（建立輕量 VM 容納容器）
   - OS 設定（Pagefile、RAM 配置）影響測試結果

4. 應用場景：
   - 在 Windows 平台驗證 .NET Core 應用的記憶體行為與碎片化影響
   - 評估容器與原生環境下的資源效率與隔離等級取捨
   - 針對雲端或資料中心部署，選擇 Windows Container 或 Hyper-V Container
   - 在低 GUI、指令為主的 Server Core 環境進行自動化建置與測試
   - 監控與故障診斷（利用 Task Manager/效能頁，確認容器與主機的關聯）

### 學習路徑建議
1. 入門者路徑：
   - 熟悉 .NET Core 專案基本結構與編譯流程
   - 了解 Windows Server 2012 R2/2016 Nano 差異與 Server Core 操作（無 GUI、純指令）
   - 學會 Docker 基本命令與在 Windows 上的使用方式
   - 練習使用 Task Manager/效能頁觀察程序與記憶體使用

2. 進階者路徑：
   - 實作記憶體碎片化測試：設計 Phase 1/3 的申請與釋放策略
   - 比較容器 vs 原生環境的記憶體利用率與效能差異
   - 探索 Windows Container 與 Hyper-V Container 的隔離差異與部署策略
   - 調整 OS 設定（Pagefile、RAM 配置），觀察對 .NET Core 進程的影響

3. 實戰路徑：
   - 建立兩套環境（2012 R2 Server Core、2016 Nano Container），就地編譯與執行測試
   - 以統一流程：重開機、抓套件、編譯、連跑兩次取第二次，收集數據並計算利用率
   - 以 Docker/PowerShell 管理容器，確認 Host 與 Container 共享 Kernel 的行為
   - 以任務管理員與效能頁建立監控基準，對比結果與程式 Overhead

### 關鍵要點清單
- 測試流程統一化：重開機、抓套件、就地編譯、連跑兩次取第二次數據，降低首啟最佳化影響 (優先級: 高)
- 記憶體利用率指標：以 Phase 1/Phase 3 記憶體取得量計算比例，衡量碎片化影響 (優先級: 高)
- 2012 R2 結果：Phase 1=4416MB、Phase 3=2888MB、利用率=65.40% (優先級: 高)
- 2016 Nano/Container 結果：Phase 1=4032MB、Phase 3=2696MB、利用率=66.87% (優先級: 高)
- Windows Container 核心性質：與 Host 共用同一 Kernel，非 VM 完全隔離，資源使用效率較高 (優先級: 高)
- Docker 相容性：Windows 上提供與 Docker 相容的管理工具，但映像需使用 Windows 基底（不可用 Linux 映像） (優先級: 高)
- Hyper-V Container：提供 Kernel 隔離需求時，底層自動以 VM 承載容器，兼具隔離與容器優勢 (優先級: 高)
- Server Core 操作方式：無 GUI，需純指令；可用 taskmgr.exe 呼叫任務管理員做監控 (優先級: 中)
- 記憶體配置影響：Pagefile 預設 4GB + RAM 1GB，影響 dnx.exe 可申請的總記憶體 (優先級: 中)
- 程式 Overhead 觀察：dnx.exe 實際使用量與測試數據相近，Overhead 小 (優先級: 中)
- 效能頁跡象：初始啟動時 RAM 用盡，後續主要使用虛擬記憶體，符合預期 (優先級: 中)
- TP4 狀態：Windows 2016 Nano (TP4) 互動模式回應較慢，預期正式版將改善 (優先級: 低)
- 就地編譯策略：在目標環境直接編譯與測試，避免跨環境差異影響結果 (優先級: 中)
- 容器與 VM 的辨識：任務管理員可看到容器內程序，驗證同 Kernel 而非 VM 隔離 (優先級: 中)
- 實務選型思路：依需求在效率（Container）與隔離等級（Hyper-V Container）間取捨 (優先級: 高)