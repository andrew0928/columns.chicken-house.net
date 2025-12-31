---
layout: synthesis
title: ".NET Core 跨平台 #3, 記憶體管理大考驗 - Windows Container (2016 TP)"
synthesis_type: solution
source_post: /2015/12/28/dnxcore50_03_windows_server_2016/
redirect_from:
  - /2015/12/28/dnxcore50_03_windows_server_2016/solution/
postid: 2015-12-28-dnxcore50_03_windows_server_2016
---

以下為依據文章內容所梳理出的 16 個教學型問題解決案例。每個案例均包含問題、根因、解法（含流程或指令）、實測或指標、學習要點與練習與評估。數據與觀察皆以原文所述為準，未提供數據之處以「定性指標」表述。

## Case #1: Windows Server 2012 R2 Server Core 記憶體碎片化基線測試與指標設計

### Problem Statement（問題陳述）
**業務場景**：在 Windows Server 2012 R2 Server Core 上驗證 .NET Core 應用於高記憶體壓力與碎片化場景的行為，建立可比較的基線，以利後續跨平台（Windows Container、Linux）對照。因 Server Core 無 GUI，所有動作偏向指令化，並以就地編譯、就地測試取得最接近實務的結果。
**技術挑戰**：如何在碎片化後仍能重獲大記憶體區塊、並以一致的方式衡量不同平台的可用度。
**影響範圍**：影響高記憶體負載服務（快取、批次計算、資料處理）穩定性與可擴充性評估。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 記憶體碎片化造成大型連續記憶體區塊難以重新配置。
2. 物理 RAM（1GB）快速耗盡，系統轉向使用 4GB pagefile 虛擬記憶體。
3. .NET Core（DNX 時期）運行時（dnx.exe）本身的記憶體佔用與 LOH（Large Object Heap）分配行為。
**深層原因**：
- 架構層面：應用採大物件分配策略，對 OS/CLR 的記憶體管理機制敏感。
- 技術層面：LOH 不壓縮、GC 對碎片化的回收策略有限。
- 流程層面：缺乏一致指標，難以跨平台客觀比較。

### Solution Design（解決方案設計）
**解決策略**：以固定步驟進行基準測試（重開機、還原套件、編譯、連續執行兩次取第二次），並自訂「記憶體利用率%」指標（Phase1 可取得量為分母，Phase3 可取得量為分子），將碎片化前後的可用記憶體能力量化，建立可比較基線。

**實施步驟**：
1. 測試前清潔環境
- 實作細節：重開 VM，避免背景程式干擾。
- 所需資源：Windows Server 2012 R2 Server Core VM。
- 預估時間：10 分鐘。

2. 就地編譯與雙次執行
- 實作細節：在受測機上下載套件、編譯，連續執行兩次取第二次。
- 所需資源：.NET Core（DNX 時期）工具鏈。
- 預估時間：20-30 分鐘。

3. 計算指標
- 實作細節：以 Phase1 作分母、Phase3 作分子計算利用率%。
- 所需資源：腳本或手動計算。
- 預估時間：5 分鐘。

**關鍵程式碼/設定**：
```powershell
# Windows Server Core 上的測試批次流程（概念示例）
# 1) 重開機由管理工具或手動進行
# 2) 還原/編譯/執行兩次，第二次結果為準
# 3) 以輸出記錄 Phase1/Phase3 的可用記憶體

# 假設應用會輸出 Phase1/Phase3 數值到 log
.\restore_packages.ps1
.\build.ps1

# 連續執行兩次
.\run_test.ps1 | Tee-Object -FilePath .\run1.log
.\run_test.ps1 | Tee-Object -FilePath .\run2.log

# 計算記憶體利用率 (以 run2.log 為準)
# Implementation Example（實作範例）
```

實際案例：在 2012 R2 Server Core 上以 DNX 執行測試並記錄 Phase1/Phase3。
實作環境：Windows Server 2012 R2 Server Core，RAM 1GB，pagefile 4GB，.NET Core（DNX）。
實測數據：
改善前：無統一指標，結果難比較。
改善後：Phase1=4416MB，Phase3=2888MB，利用率=65.40%。
改善幅度：可比較性從 0 提升至可量化（定性改善）。

Learning Points（學習要點）
核心知識點：
- 記憶體碎片化對大型配置的影響
- LOH 與 GC 行為對測試結果的影響
- 基準測試指標設計的重要性
技能要求：
必備技能：Windows Server Core 操作、基本 .NET Core 編譯與執行。
進階技能：記憶體分析與指標設計。
延伸思考：
- 指標可用於不同平台的對比分析。
- LOH/GC 行為在不同版本 CLR 的差異。
- 可加入更精細的統計（標準差）提升可靠性。

Practice Exercise（練習題）
基礎練習：在 Server Core 上以兩次執行法完成一次測試並算出指標（30 分鐘）。
進階練習：加入 log parser 自動化計算 Phase1/Phase3（2 小時）。
專案練習：打造完整基準測試框架（重開機、部署、執行、報表）（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：能完整跑到並輸出指標。
程式碼品質（30%）：腳本結構清晰、可重複執行。
效能優化（20%）：降低不必要的背景干擾。
創新性（10%）：指標設計/報表呈現具通用性。


## Case #2: Windows Server 2016 Nano Container 記憶體碎片化測試與近原生效能觀察

### Problem Statement（問題陳述）
**業務場景**：在 Windows Server 2016（TP4）上首次體驗 Windows Container，於容器中建立 .NET Core 測試環境，量測記憶體碎片化後的可用度，並與 2012 R2 Server Core 作對照。
**技術挑戰**：Windows 容器與 Host 共用 Kernel，需確保測試流程與度量標準一致且能反映近原生效能。
**影響範圍**：關係到在 Windows 容器中部署 .NET Core 記憶體密集型服務的可行性與預期表現。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器與 Host 共用 Kernel，行為應與原生接近。
2. 體驗版（TP4）可能有互動模式性能未優化的情況。
3. 基底映像需使用 Windows Server Core，自行建立環境。
**深層原因**：
- 架構層面：容器技術以 OS 層級隔離，不是 VM 完全隔離。
- 技術層面：Windows 容器不可使用 Linux 映像，需自建。
- 流程層面：需維持相同測試步驟避免測量偏差。

### Solution Design（解決方案設計）
**解決策略**：使用 Windows Server Core 作為容器基底，於容器內就地安裝運行時與依賴、就地編譯、並套用相同的雙次執行法與記憶體利用率指標，比對與原生 Server Core 的差異。

**實施步驟**：
1. 準備容器基底
- 實作細節：取得 Windows Server Core image，啟動互動模式。
- 所需資源：Windows Server 2016（TP4）、Docker for Windows（容器支援）。
- 預估時間：30 分鐘。

2. 建環境與測試
- 實作細節：在容器內安裝 DNX/.NET Core，下載套件、編譯，連續執行兩次。
- 所需資源：PowerShell、套件源。
- 預估時間：30-60 分鐘。

**關鍵程式碼/設定**：
```powershell
# 啟動 Windows Server Core 容器（示例命令）
docker pull windowsservercore
docker run -it --name memtest windowsservercore powershell

# 容器內建立測試環境、執行兩次
# Implementation Example（實作範例）
```

實際案例：於 Windows 2016 TP4 的容器中完成測試。
實作環境：Windows Server 2016（TP4）、Windows Container（Server Core 基底）、.NET Core（DNX）。
實測數據：
改善前：2012 R2 指標=65.40%。
改善後：容器 Phase1=4032MB，Phase3=2696MB，利用率=66.87%。
改善幅度：+1.47 個百分點（相較 2012 R2）。

Learning Points（學習要點）
核心知識點：
- Windows 容器與 Host 共用 Kernel 的行為
- 以容器重現近原生效能的測試方法
- 指標一致性在跨環境比較中的重要性
技能要求：
必備技能：Docker on Windows 基本操作、PowerShell。
進階技能：容器內部環境建置、自動化流程。
延伸思考：
- 後續版本（非 TP）互動模式效能可能提升。
- 是否需要為容器設定資源限制以防止過度分配。
- 指標能否擴展到 GC/LOH 更細緻分析。

Practice Exercise（練習題）
基礎練習：啟動一個 Windows Server Core 容器並成功執行測試（30 分鐘）。
進階練習：將測試流程容器化為 Dockerfile + Entrypoint（2 小時）。
專案練習：搭建 CI，自動建置容器並產出報表（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：容器內完成雙次測試。
程式碼品質（30%）：Dockerfile/腳本清晰。
效能優化（20%）：執行時間與資源使用合理。
創新性（10%）：報表與比較分析呈現。


## Case #3: 避免第一次執行偏差的基準測試流程

### Problem Statement（問題陳述）
**業務場景**：在各受測平台上，首次執行常伴有額外最佳化、JIT 編譯、快取建立等行為，導致數據偏差。需設計流程避免初次執行干擾，確保結果可重現且可比較。
**技術挑戰**：如何以簡單、穩定的方法排除初次啟動影響。
**影響範圍**：影響所有平台測試的可信度與決策品質。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 首次 JIT 編譯造成額外 CPU/記憶體活動。
2. 套件首次下載/還原造成 IO 與記憶體影響。
3. CLR 啟動與暫存建立的額外開銷。
**深層原因**：
- 架構層面：JIT/快取機制屬設計必然。
- 技術層面：測試工具/指標未排除初始噪音。
- 流程層面：缺少固定基準流程（重開機、雙次執行）。

### Solution Design（解決方案設計）
**解決策略**：固定化測試流程：重開機清場、下載套件與編譯、連續執行兩次取第二次結果，使初次啟動開銷不影響測量。

**實施步驟**：
1. 標準化測試前置
- 實作細節：重開 OS、清空暫存。
- 所需資源：VM/容器管理權限。
- 預估時間：10 分鐘。

2. 雙次執行法
- 實作細節：連續執行兩次、採第二次。
- 所需資源：批次腳本。
- 預估時間：20 分鐘。

**關鍵程式碼/設定**：
```powershell
# 將雙次執行法寫成批次（示意）
.\prepare.ps1   # 還原/編譯
.\run.ps1 | Tee-Object -FilePath .\first.log
.\run.ps1 | Tee-Object -FilePath .\second.log
# 後續僅分析 second.log
# Implementation Example（實作範例）
```

實際案例：原文於所有測試平台皆使用相同流程。
實作環境：Windows Server 2012 R2、Windows Server 2016 容器。
實測數據：
改善前：數據波動，受首次啟動影響（定性）。
改善後：以第二次結果為準，波動顯著降低（定性）。
改善幅度：定性提升（文章未提供量化）。

Learning Points（學習要點）
核心知識點：
- JIT/快取帶來的測試偏差
- 流程標準化提升信度
- 重開機與清潔環境的重要性
技能要求：
必備技能：撰寫批次腳本。
進階技能：統計方法評估穩定度（平均/標準差）。
延伸思考：
- 可延伸為「N 次執行取中位數」。
- 可用性能計數器補強觀測。
- 自動化報表顯示穩定度指標。

Practice Exercise（練習題）
基礎練習：寫一個雙次執行腳本（30 分鐘）。
進階練習：納入三次以上並計算中位數與變異（2 小時）。
專案練習：建立可參數化的基準測試管線（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：流程能重複執行。
程式碼品質（30%）：腳本易讀、可維護。
效能優化（20%）：縮短非必要等待。
創新性（10%）：加入統計與可視化。


## Case #4: Server Core 無 GUI 環境下的記憶體診斷（taskmgr.exe 小技巧）

### Problem Statement（問題陳述）
**業務場景**：在 Windows Server Core 無 GUI 的環境中，仍需即時觀察進程記憶體佔用與效能指標，以確認測試與應用行為（例如 dnx.exe 的佔用）。
**技術挑戰**：缺少常見 GUI 工具的入口，影響排查效率。
**影響範圍**：影響故障診斷、資源監控與測試佐證。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Server Core 以輕量化為目標，預設無 GUI。
2. 需要即時觀測但缺乏工具入口。
3. 測試需佐證進程與資源分配狀態。
**深層原因**：
- 架構層面：Server Core 的設計取捨。
- 技術層面：未熟悉可用替代指令或工具。
- 流程層面：測試流程缺少監控步驟。

### Solution Design（解決方案設計）
**解決策略**：直接在 Command Prompt/PowerShell 呼叫 taskmgr.exe 啟動工作管理員，觀測 dnx.exe 記憶體佔用與物理/虛擬記憶體使用情況，輔以效能分頁分析。

**實施步驟**：
1. 啟動 Task Manager
- 實作細節：cmd/PowerShell 執行 taskmgr.exe。
- 所需資源：本機系統工具。
- 預估時間：1 分鐘。

2. 觀測重點
- 實作細節：查看進程記憶體、效能分頁的 RAM 使用曲線。
- 所需資源：無。
- 預估時間：10 分鐘。

**關鍵程式碼/設定**：
```bat
REM 在 Server Core 中開啟工作管理員
taskmgr.exe

REM 搭配其他指令（選用）
typeperf "\Process(dnx)\Working Set - Private" -sc 10
REM Implementation Example（實作範例）
```

實際案例：觀測到 dnx.exe 約佔用 4548MB；物理 RAM 1GB 中約 800MB 被使用；效能頁顯示啟動時段物理記憶體瞬間被用滿。
實作環境：Windows Server 2012 R2 Server Core。
實測數據：
改善前：無法即時佐證測試期間資源使用（定性）。
改善後：取得 dnx.exe 記憶體 4548MB、RAM 800MB/1GB 的觀測值。
改善幅度：可觀測性由低提升至高（定性）。

Learning Points（學習要點）
核心知識點：
- Server Core 也可呼叫 GUI 工具
- 進程與系統層級指標交叉驗證
- 啟動期資源峰值解析
技能要求：
必備技能：基本指令操作。
進階技能：性能計數器與 log 對照分析。
延伸思考：
- 補充 PerfMon 或 ETW 事件追蹤。
- 自動化抓取指標與快照。
- 導出 CSV 以進行長期分析。

Practice Exercise（練習題）
基礎練習：在 Server Core 啟動 Task Manager 並截圖保存（30 分鐘）。
進階練習：用 typeperf 取樣 dnx 記憶體並與圖對照（2 小時）。
專案練習：建立監控腳本自動採樣與存檔（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：能開啟並讀取關鍵指標。
程式碼品質（30%）：指令腳本整潔。
效能優化（20%）：取樣頻率與負載平衡。
創新性（10%）：監控視覺化呈現。


## Case #5: Pagefile 對高記憶體壓力測試的影響與設定檢查

### Problem Statement（問題陳述）
**業務場景**：測試需申請超過物理 RAM 的記憶體以評估碎片化，需確認並利用系統 pagefile 的配置以避免測試失真或失敗。
**技術挑戰**：在 Server Core 檢查/確認虛擬記憶體設定並解讀測試影響。
**影響範圍**：影響可申請到的最大記憶體與測試可靠性。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 物理 RAM 僅 1GB，須依賴 pagefile 才能申請到 4GB+。
2. 預設 pagefile 為 4GB。
3. 測試設計需確認 pagefile 是否足以支撐。
**深層原因**：
- 架構層面：OS 虛擬記憶體管理影響大配置申請。
- 技術層面：忽略 pagefile 可能導致申請失敗。
- 流程層面：測試前置檢查未制度化。

### Solution Design（解決方案設計）
**解決策略**：在 Server Core 使用系統工具檢查 pagefile 設定、記錄，並將其納入測試報告，確保可用記憶體在 Phase1 能達 4GB+。

**實施步驟**：
1. 檢查設定
- 實作細節：使用 WMIC/PowerShell 查詢 pagefile 大小。
- 所需資源：系統工具。
- 預估時間：5 分鐘。

2. 佐證影響
- 實作細節：對照 Phase1 可用量與 pagefile 設定。
- 所需資源：測試輸出。
- 預估時間：10 分鐘。

**關鍵程式碼/設定**：
```powershell
# 查詢 Pagefile 設定
wmic pagefile get Name,AllocatedBaseSize,CurrentUsage
Get-WmiObject Win32_PageFileUsage | Select Name, AllocatedBaseSize, CurrentUsage
# Implementation Example（實作範例）
```

實際案例：在 1GB RAM、4GB pagefile 下，2012 R2 Phase1 可申請至 4416MB。
實作環境：Windows Server 2012 R2。
實測數據：
改善前：僅 1GB RAM，可能不足以測試。
改善後：確認 4GB pagefile，Phase1=4416MB。
改善幅度：可申請上限由 ~1GB 提升至 ~4.3GB（約 +330%）。

Learning Points（學習要點）
核心知識點：
- 虛擬記憶體與 pagefile 的角色
- Pagefile 對大型配置的影響
- 配置檢查流程
技能要求：
必備技能：WMIC/PowerShell 操作。
進階技能：將系統設定納入測試報告。
延伸思考：
- 調整 pagefile 對測試行為的影響。
- 監控 pagefile 使用率避免過度 paging。
- 在生產環境的最佳實務。

Practice Exercise（練習題）
基礎練習：查詢並截圖 pagefile 設定（30 分鐘）。
進階練習：修改 pagefile 大小並觀察 Phase1 變化（2 小時）。
專案練習：建立 pagefile 檢查/調整自動化腳本（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：能查詢/調整設定。
程式碼品質（30%）：腳本健壯。
效能優化（20%）：避免過度 paging。
創新性（10%）：報表整合與告警。


## Case #6: 以 Windows Server Core 影像自建容器環境並布署 .NET Core 測試

### Problem Statement（問題陳述）
**業務場景**：Windows 容器不能使用 Linux 映像，需從 Windows Server Core 映像起步，自建 .NET Core 測試環境以完成記憶體碎片化測試。
**技術挑戰**：容器內環境建置與依賴安裝需手動流程，TP4 階段回應速度偏慢。
**影響範圍**：影響開發/測試可重現性與效率。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器共用 Kernel，無法載入 Linux 映像。
2. 官方 Windows 映像內容精簡，需自建。
3. TP4 容器互動模式速度偏慢。
**深層原因**：
- 架構層面：容器與 OS Kernel 相依。
- 技術層面：映像內容需要依需求擴充。
- 流程層面：建置步驟未自動化。

### Solution Design（解決方案設計）
**解決策略**：以 Windows Server Core 映像為基底，在容器中安裝 .NET Core（DNX）與依賴、導入原始碼、就地編譯與測試；優先以非互動腳本方式執行，降低互動延遲影響。

**實施步驟**：
1. 建立容器
- 實作細節：拉取並啟動 windowsservercore，安裝必要工具。
- 所需資源：Docker、PowerShell。
- 預估時間：30-60 分鐘。

2. 非互動化測試
- 實作細節：用腳本執行 restore/build/run，輸出到 log。
- 所需資源：PowerShell 腳本。
- 預估時間：30 分鐘。

**關鍵程式碼/設定**：
```powershell
docker pull windowsservercore
docker run -d --name memtest windowsservercore powershell -Command "Start-Sleep -Seconds 3600"
docker exec memtest powershell -Command "& C:\setup\restore_build_run.ps1"
# Implementation Example（實作範例）
```

實際案例：完成容器內測試且得到 Phase1/Phase3。
實作環境：Windows Server 2016（TP4）、Windows Container。
實測數據：
改善前：手動互動操作慢，流程不一致（定性）。
改善後：非互動腳本執行，產出穩定結果（容器利用率=66.87%）。
改善幅度：可重現性與效率提升（定性）。

Learning Points（學習要點）
核心知識點：
- Windows 容器與映像選型
- 非互動腳本化執行提高穩定性
- 跨環境一致流程的重要
技能要求：
必備技能：Docker/PowerShell。
進階技能：容器 CI/CD 導入。
延伸思考：
- 建立 Dockerfile 將建置流程固化。
- 以 Hyper-V 隔離因應安全需求。
- 針對 TP4 的性能行為做風險控管。

Practice Exercise（練習題）
基礎練習：以 docker exec 非互動執行測試（30 分鐘）。
進階練習：撰寫 Dockerfile 完成映像自動建置（2 小時）。
專案練習：建立容器化基準測試 pipeline（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：容器內能完整執行。
程式碼品質（30%）：Dockerfile/腳本標準化。
效能優化（20%）：縮短互動等待時間。
創新性（10%）：自動化程度與報表整合。


## Case #7: 用 Host 工作管理員驗證容器與 Host 共用 Kernel

### Problem Statement（問題陳述）
**業務場景**：需確認 Windows 容器進程在 Host 的工作管理員可見，以佐證容器與 Host 共用同一 Kernel、非 VM 完全隔離，並解讀效能差異小的原因。
**技術挑戰**：如何快速、確定地驗證 Kernel 共用特性。
**影響範圍**：影響架構選型（容器 vs VM）與安全/效能判斷。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器與 Host 共用 Kernel。
2. 進程於 Host 可見。
3. 效能與原生相近。
**深層原因**：
- 架構層面：容器為 OS 層隔離。
- 技術層面：工作管理員能顯示容器內進程。
- 流程層面：需驗證以建立信任。

### Solution Design（解決方案設計）
**解決策略**：在 Host OS 打開工作管理員，觀察容器內執行的指令與進程，確認容器行為與 Kernel 共用，輔以指標比較解讀效能差異。

**實施步驟**：
1. 啟動容器並執行程式
- 實作細節：容器內執行測試。
- 所需資源：docker。
- 預估時間：20 分鐘。

2. Host 端觀測
- 實作細節：開工作管理員，查進程。
- 所需資源：Host OS。
- 預估時間：10 分鐘。

**關鍵程式碼/設定**：
```powershell
# Host 端打開工作管理員觀測容器內進程（GUI 操作）
# 也可用 Get-Process 觀測
Get-Process | Where-Object { $_.ProcessName -like "*dnx*" }
# Implementation Example（實作範例）
```

實際案例：於 Host 工作管理員看到容器內進程，證實共用 Kernel。
實作環境：Windows Server 2016 TP4。
實測數據：
改善前：對容器與 VM 的差異理解有限（定性）。
改善後：確認共用 Kernel、效能近原生（定性）。
改善幅度：理解與判斷能力提升（定性）。

Learning Points（學習要點）
核心知識點：
- 容器/VM 的本質差異
- Host 端監控容器進程
- 效能與隔離的取捨
技能要求：
必備技能：Windows 監控。
進階技能：進程/資源追蹤。
延伸思考：
- 需要內核級隔離時改用 Hyper-V 容器。
- 進程可見性對安全策略的影響。
- 監控與告警整合。

Practice Exercise（練習題）
基礎練習：在 Host 端列出容器進程（30 分鐘）。
進階練習：加入資源占用監控（2 小時）。
專案練習：統一監控 Host 與容器進程（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：能觀測到容器進程。
程式碼品質（30%）：監控腳本規範。
效能優化（20%）：低開銷監控。
創新性（10%）：圖表與報告整合。


## Case #8: TP4 容器互動模式操作緩慢的替代方案

### Problem Statement（問題陳述）
**業務場景**：Windows 2016 TP4 容器互動模式下（-it）回應偏慢，影響開發與測試效率。
**技術挑戰**：在 Preview 階段如何減少互動操作成本。
**影響範圍**：影響開發者體驗與交付速度。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. TP4 預覽版效能尚未調校完善。
2. 終端機 I/O 在容器環境下有額外延遲。
3. 多次互動造成累積等待。
**深層原因**：
- 架構層面：預覽版的設計尚在迭代。
- 技術層面：互動式 I/O 管線尚未最佳化。
- 流程層面：過度倚賴互動模式。

### Solution Design（解決方案設計）
**解決策略**：減少互動操作，改用非互動腳本與 docker exec 執行批次指令；一次性建立環境與執行測試，降低終端機往返成本。

**實施步驟**：
1. 將操作腳本化
- 實作細節：把 restore/build/run 合併為單一腳本。
- 所需資源：PowerShell。
- 預估時間：1 小時。

2. 非互動執行
- 實作細節：用 docker exec 非互動執行、收集 log。
- 所需資源：docker。
- 預估時間：30 分鐘。

**關鍵程式碼/設定**：
```powershell
docker exec memtest powershell -Command "& C:\setup\pipeline.ps1 -NoInteractive"
# pipeline.ps1 內含所有步驟，並輸出 log
# Implementation Example（實作範例）
```

實際案例：原文提及 TP4 互動模式偏慢，建議等更接近 release 再評估。
實作環境：Windows Server 2016 TP4。
實測數據：
改善前：互動模式慢，等待時間長（定性）。
改善後：改為非互動批次，整體體驗改善（定性）。
改善幅度：開發效率提升（定性）。

Learning Points（學習要點）
核心知識點：
- 預覽版效能特性
- 批次腳本化的價值
- 減少互動以提升效率
技能要求：
必備技能：PowerShell 腳本。
進階技能：容器管線設計。
延伸思考：
- 後續版本升級後回頭評估互動模式。
- 加入重試/容錯機制。
- 以任務排程器自動觸發。

Practice Exercise（練習題）
基礎練習：將一組互動指令改為腳本（30 分鐘）。
進階練習：整合 log 收集、錯誤處理（2 小時）。
專案練習：建立容器批次測試系統（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：腳本可替代互動。
程式碼品質（30%）：結構與錯誤處理完善。
效能優化（20%）：等待時間減少。
創新性（10%）：自動化與通知整合。


## Case #9: 記憶體利用率% 指標設計與跨平台比較方法

### Problem Statement（問題陳述）
**業務場景**：需在不同平台（2012 R2、2016 容器）以單一可比較指標衡量碎片化後的記憶體可用度，便於決策與報告。
**技術挑戰**：指標需簡單、可重複、具代表性。
**影響範圍**：影響跨平台效能解讀與溝通一致性。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不同平台的 Phase1/Phase3 絕對值不同。
2. 無統一指標難以比較。
3. 指標需與測試行為緊密對應。
**深層原因**：
- 架構層面：平台差異導致不同上限。
- 技術層面：分配與回收策略差異。
- 流程層面：報表缺乏標準化。

### Solution Design（解決方案設計）
**解決策略**：定義「記憶體利用率% = Phase3 / Phase1」，在每次測試輸出 Phase1/Phase3 並自動計算，作為跨平台可比的核心指標。

**實施步驟**：
1. 指標定義與輸出
- 實作細節：程式輸出 Phase1/Phase3；腳本計算比值。
- 所需資源：測試程式、腳本。
- 預估時間：30 分鐘。

2. 報表化
- 實作細節：繪製各平台利用率對比。
- 所需資源：報表工具。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```csharp
// C# 計算指標（示例）
long phase1Bytes = ReadMetric("phase1.txt");
long phase3Bytes = ReadMetric("phase3.txt");
double utilization = (double)phase3Bytes / phase1Bytes * 100.0;
// Console.WriteLine($"Utilization: {utilization:F2}%");
// Implementation Example（實作範例）
```

實際案例：2012 R2=65.40%；2016 容器=66.87%。
實作環境：Windows Server 2012 R2、Windows Server 2016 容器。
實測數據：
改善前：無統一指標。
改善後：具可比指標（65.40% vs 66.87%）。
改善幅度：指標化程度大幅提升（定性）。

Learning Points（學習要點）
核心知識點：
- 相對指標設計
- 指標可比性與穩健性
- 測試數據流程化
技能要求：
必備技能：小型工具開發。
進階技能：報表/可視化。
延伸思考：
- 加入誤差條與樣本數。
- 擴展到其他資源（CPU/IO）。
- 自動生成跨平台摘要。

Practice Exercise（練習題）
基礎練習：撰寫指標計算工具（30 分鐘）。
進階練習：生成圖表與報告（2 小時）。
專案練習：整合到 CI 報表（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：能自動算出指標。
程式碼品質（30%）：健壯、可維護。
效能優化（20%）：處理多樣本。
創新性（10%）：視覺化與洞見。


## Case #10: 在受測環境就地編譯與執行，避免跨環境差異

### Problem Statement（問題陳述）
**業務場景**：為避免跨環境（Host vs 容器、不同 OS）導致的運行時差異與最佳化影響，選擇將原始碼直接放入受測環境，就地編譯、就地執行。
**技術挑戰**：在不同環境安裝/配置工具鏈並確保相同流程。
**影響範圍**：影響數據可信度與偏差。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 跨環境編譯可能導致不同 JIT/最佳化。
2. 不同依賴版本可能造成差異。
3. 測試需最大限度地貼近實際。
**深層原因**：
- 架構層面：環境差異是系統性風險。
- 技術層面：工具鏈版本一致性重要。
- 流程層面：缺乏「就地」策略會引入偏差。

### Solution Design（解決方案設計）
**解決策略**：統一流程：原始碼直接到受測平台，就地下載套件、就地編譯，再執行雙次測試並計算指標。

**實施步驟**：
1. 工具鏈安裝
- 實作細節：於各環境安裝相同版本的運行時工具。
- 所需資源：套件源。
- 預估時間：30 分鐘。

2. 就地執行
- 實作細節：還原、編譯、執行兩次。
- 所需資源：腳本。
- 預估時間：30 分鐘。

**關鍵程式碼/設定**：
```powershell
# 就地還原與編譯（概念示例）
.\restore.ps1
.\build.ps1
.\run.ps1
.\run.ps1
# Implementation Example（實作範例）
```

實際案例：原文所有測試皆採就地編譯與就地執行。
實作環境：Windows Server 2012 R2、Windows 2016 容器。
實測數據：
改善前：跨環境編譯可能導致偏差（定性）。
改善後：就地執行提升一致性（定性）。
改善幅度：可信度提升（定性）。

Learning Points（學習要點）
核心知識點：
- 就地編譯的價值
- 工具鏈一致性
- 測試流程標準化
技能要求：
必備技能：基本建置腳本。
進階技能：版本鎖定與重現。
延伸思考：
- 以容器封裝工具鏈。
- 建立 reproducible builds。
- 引入版本快照。

Practice Exercise（練習題）
基礎練習：就地執行一次小型專案（30 分鐘）。
進階練習：建立跨環境一致的 build 腳本（2 小時）。
專案練習：打造可重現的測試容器（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：能就地編譯執行。
程式碼品質（30%）：腳本可移植。
效能優化（20%）：縮短建置時間。
創新性（10%）：版本與依賴管理。


## Case #11: 容器與原生差異極小的效能觀察與解讀

### Problem Statement（問題陳述）
**業務場景**：Windows 容器測試結果顯示記憶體利用率與原生 Server Core 相差不大，需要解讀原因與影響。
**技術挑戰**：從架構角度分析容器效能接近原生的原因並確認方向正確。
**影響範圍**：影響「是否採容器」的架構決策。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器與 Host 共用 Kernel。
2. 測試流程一致。
3. 容器本身開銷有限。
**深層原因**：
- 架構層面：OS 層隔離帶來近原生效能。
- 技術層面：TP4 雖預覽，但核心機制已具代表性。
- 流程層面：相同指標設計避免偏差。

### Solution Design（解決方案設計）
**解決策略**：用記憶體利用率（65.40% vs 66.87%）比較，結論為容器效能接近原生，後續以安全/隔離要求決定是否採容器或 Hyper-V 容器。

**實施步驟**：
1. 數據比較
- 實作細節：以同一指標比較兩平台。
- 所需資源：測試輸出。
- 預估時間：10 分鐘。

2. 架構決策建議
- 實作細節：依隔離需求選容器或 Hyper-V 容器。
- 所需資源：安全需求分析。
- 預估時間：1 小時。

**關鍵程式碼/設定**：
```powershell
# 簡單比較報表（示例）
$win2012 = 65.40
$win2016Container = 66.87
"{0} vs {1} (Δ {2} pp)" -f $win2012, $win2016Container, ($win2016Container - $win2012)
# Implementation Example（實作範例）
```

實際案例：兩平台利用率差距小。
實作環境：同上。
實測數據：
改善前：不確定容器效能。
改善後：容器=66.87%、原生=65.40%，差距 +1.47pp。
改善幅度：信心提升（定性與量化皆有）。

Learning Points（學習要點）
核心知識點：
- 容器效能接近原生的原因
- 指標比較的解讀方法
- 以需求驅動選型
技能要求：
必備技能：指標分析。
進階技能：架構決策文件撰寫。
延伸思考：
- 加入 CPU/IO 指標更完整。
- 長期觀察穩定度。
- 考慮多租戶場景隔離需求。

Practice Exercise（練習題）
基礎練習：產出比較圖表（30 分鐘）。
進階練習：撰寫一頁式架構建議（2 小時）。
專案練習：建立指標面板（dashboard）（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：完整比較與結論。
程式碼品質（30%）：報表清晰。
效能優化（20%）：資料處理高效。
創新性（10%）：洞見與建議品質。


## Case #12: 選用 Server Core 以降低背景資源開銷

### Problem Statement（問題陳述）
**業務場景**：為提升效能與減少干擾，測試與部署選用 Windows Server Core（無 GUI）以降低背景資源開銷。
**技術挑戰**：在無 GUI 的前提下仍需便利操作與監控。
**影響範圍**：影響基準測試純度與生產環境資源使用。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. GUI 會帶來額外資源負擔。
2. Server Core 輕量更適合測試。
3. 指令化操作可提高效率。
**深層原因**：
- 架構層面：輕量化平台更貼近服務型工作負載。
- 技術層面：工具需指令化。
- 流程層面：操作與監控流程需調整。

### Solution Design（解決方案設計）
**解決策略**：採 Server Core 作對照組，透過指令與小技巧（taskmgr.exe）補齊監控，維持低開銷環境以提昇測試純度。

**實施步驟**：
1. 部署 Server Core
- 實作細節：安裝最小化環境。
- 所需資源：安裝介質。
- 預估時間：1 小時。

2. 指令化操作
- 實作細節：所有動作用指令完成。
- 所需資源：cmd/PowerShell。
- 預估時間：持續。

**關鍵程式碼/設定**：
```bat
REM 在 Server Core 上的基本操作（示例）
powershell.exe -Command "& {Get-Process | Sort-Object WorkingSet -Descending | Select -First 10}"
taskmgr.exe
# Implementation Example（實作範例）
```

實際案例：測試期間 RAM 1GB 中 ~800MB 被使用（含 OS 開銷），環境純度高。
實作環境：Windows Server 2012 R2 Server Core。
實測數據：
改善前：GUI 可能增加背景開銷（定性）。
改善後：Server Core 減少干擾（觀測 RAM 使用低）。
改善幅度：環境純度提升（定性）。

Learning Points（學習要點）
核心知識點：
- Server Core 適用場景
- 指令化與監控技巧
- 減少環境噪音策略
技能要求：
必備技能：Windows 指令操作。
進階技能：自動化運維。
延伸思考：
- 生產環境是否適用 Server Core。
- 監控方案需配套。
- GUI 與無 GUI 的取捨。

Practice Exercise（練習題）
基礎練習：在 Server Core 完成一次部署（30 分鐘）。
進階練習：以指令完成完整測試流程（2 小時）。
專案練習：建立最小化部署手冊（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：可在 Server Core 完成操作。
程式碼品質（30%）：腳本清晰。
效能優化（20%）：資源開銷低。
創新性（10%）：操作技巧與經驗。


## Case #13: 物理記憶體被用光後改用虛擬記憶體的行為診斷

### Problem Statement（問題陳述）
**業務場景**：測試顯示啟動期物理記憶體快速被用光，隨後主要使用虛擬記憶體（pagefile），需理解行為並評估對性能的影響。
**技術挑戰**：如何判讀效能頁面曲線與分配行為。
**影響範圍**：影響應用在低 RAM 環境的可行性與調優方向。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 啟動期配置峰值大。
2. RAM 1GB 不足以支撐。
3. 系統切換到 pagefile。
**深層原因**：
- 架構層面：記憶體密集型設計。
- 技術層面：OS 虛擬記憶體機制。
- 流程層面：啟動期測試需特別觀測。

### Solution Design（解決方案設計）
**解決策略**：使用工作管理員效能頁面與進程監控，記錄啟動期的 RAM 與 pagefile 使用模式，將觀察納入測試報告與調優建議（例如延遲巨量分配）。

**實施步驟**：
1. 取樣監控
- 實作細節：持續監控 RAM 使用率曲線。
- 所需資源：Task Manager/typeperf。
- 預估時間：30 分鐘。

2. 行為解讀
- 實作細節：將啟動期峰值與分配策略對應。
- 所需資源：測試 log。
- 預估時間：30 分鐘。

**關鍵程式碼/設定**：
```powershell
# 監控記憶體使用（示例）
typeperf "\Memory\Available MBytes" -sc 30
typeperf "\Paging File(_Total)\% Usage" -sc 30
# Implementation Example（實作範例）
```

實際案例：效能頁顯示啟動期物理記憶體用光，後續以虛擬記憶體為主。
實作環境：Windows Server 2012 R2 Server Core。
實測數據：
改善前：未掌握啟動期行為（定性）。
改善後：掌握 RAM/pagefile 轉換行為（定性）。
改善幅度：診斷能力提升（定性）。

Learning Points（學習要點）
核心知識點：
- 啟動期行為特性
- RAM 與 pagefile 的動態關係
- 監控與解讀技巧
技能要求：
必備技能：性能計數器使用。
進階技能：行為分析與建議。
延伸思考：
- 延後大分配、分批分配的可能。
- 提升 RAM 對性能的影響評估。
- 加入 GC 計數器更完整。

Practice Exercise（練習題）
基礎練習：用 typeperf 取樣啟動期指標（30 分鐘）。
進階練習：生成曲線圖與解讀報告（2 小時）。
專案練習：提出啟動期調優方案（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：指標取樣完整。
程式碼品質（30%）：腳本可重用。
效能優化（20%）：提出可行建議。
創新性（10%）：解讀深度。


## Case #14: Windows 容器不能用 Linux 映像的因應策略

### Problem Statement（問題陳述）
**業務場景**：Windows 容器需使用 Windows 映像，不能直接沿用 Linux 映像，需調整建置策略與工具。
**技術挑戰**：重新建立基底映像與依賴環境。
**影響範圍**：影響跨平台容器策略與 CI/CD。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器共用 Host Kernel。
2. Kernel 不同導致映像不可互通。
3. 需自建 Windows 映像。
**深層原因**：
- 架構層面：容器設計與 Kernel 緊密耦合。
- 技術層面：工具鏈/依賴不同。
- 流程層面：建置管線需分支。

### Solution Design（解決方案設計）
**解決策略**：採 Windows Server Core 作基底、獨立維護 Windows 容器建置腳本與 CI；避免跨 OS 共享映像，改以跨 OS 共享「流程/指標」。

**實施步驟**：
1. 建立 Windows 基底
- 實作細節：準備 windowsservercore 映像。
- 所需資源：Docker on Windows。
- 預估時間：30 分鐘。

2. 流程分支
- 實作細節：Windows/Linux 各自建置管線。
- 所需資源：CI 系統。
- 預估時間：2-4 小時。

**關鍵程式碼/設定**：
```dockerfile
# Windows Dockerfile（概念示例）
FROM mcr.microsoft.com/windows/servercore
SHELL ["powershell", "-Command"]
# 安裝 .NET Core/DNX、複製測試程式、設定入口
# Implementation Example（實作範例）
```

實際案例：原文於 Windows 容器中自建環境完成測試。
實作環境：Windows Server 2016 TP4 容器。
實測數據：
改善前：試圖用 Linux 映像不可行（定性）。
改善後：採 Windows 映像成功建置（定性）。
改善幅度：跨平台一致性改為流程層一致（定性）。

Learning Points（學習要點）
核心知識點：
- Kernel 相依導致映像不可互用
- 流程層一致性的價值
- Windows 容器建置要點
技能要求：
必備技能：Dockerfile 編寫。
進階技能：CI 管線分支設計。
延伸思考：
- 跨 OS 的測試指標統一。
- Artifact 管理與版本化。
- 安全掃描與合規檢查。

Practice Exercise（練習題）
基礎練習：撰寫最小 Windows Dockerfile（30 分鐘）。
進階練習：完成 Windows 容器建置與執行測試（2 小時）。
專案練習：打造跨 OS 的容器 CI（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：映像可用且能測試。
程式碼品質（30%）：Dockerfile 清晰。
效能優化（20%）：建置時間合理。
創新性（10%）：管線設計。


## Case #15: 需要核心級隔離時採用 Hyper-V Container

### Problem Statement（問題陳述）
**業務場景**：在多租戶或安全要求高的情境，需要 Kernel 層級的隔離；Windows 2016 提供 Hyper-V Container，可在 VM 中承載容器，兼顧隔離與容器優勢。
**技術挑戰**：理解何時採用 Hyper-V 隔離，以及基本啟用方式。
**影響範圍**：影響安全合規與資源隔離策略。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 一般容器共用 Kernel，隔離有限。
2. 安全/合規需更強隔離。
3. Windows 提供 Hyper-V Container 作替代。
**深層原因**：
- 架構層面：VM 級隔離可滿足高安全。
- 技術層面：Hyper-V 作為隔離層。
- 流程層面：依需求決定隔離等級。

### Solution Design（解決方案設計）
**解決策略**：當隔離要求提升時，以 Hyper-V Container 啟動工作負載；評估效能與隔離的權衡，僅在必要時使用。

**實施步驟**：
1. 啟用 Hyper-V 隔離
- 實作細節：以 --isolation=hyperv 啟動容器（視版本支援）。
- 所需資源：Windows Server 2016、Hyper-V。
- 預估時間：30 分鐘。

2. 風險/效能評估
- 實作細節：對比一般容器的性能與隔離。
- 所需資源：測試與報告。
- 預估時間：2-4 小時。

**關鍵程式碼/設定**：
```powershell
# 啟動 Hyper-V 隔離容器（版本支援時）
docker run -it --isolation=hyperv windowsservercore powershell
# Implementation Example（實作範例）
```

實際案例：原文引用概念並留待後續研究。
實作環境：Windows Server 2016。
實測數據：
改善前：一般容器隔離不足（對高安全場景）。
改善後：Hyper-V 容器提供 Kernel 級隔離（定性）。
改善幅度：隔離能力顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- 容器隔離等級
- Hyper-V 容器原理
- 何時需要更強隔離
技能要求：
必備技能：Docker/Hyper-V 基本操作。
進階技能：安全評估與合規。
延伸思考：
- 性能開銷的可接受範圍。
- 與 VM/裸機的比較。
- 自動化啟用與策略化管理。

Practice Exercise（練習題）
基礎練習：以 Hyper-V 隔離啟動容器（30 分鐘）。
進階練習：量測與一般容器的性能差異（2 小時）。
專案練習：撰寫隔離選型準則文件（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：能啟動與運行。
程式碼品質（30%）：腳本與設定清晰。
效能優化（20%）：性能測試完整。
創新性（10%）：選型指南與洞見。


## Case #16: 測試自動化：重開機→下載套件→編譯→連續執行兩次

### Problem Statement（問題陳述）
**業務場景**：為確保各平台測試一致性，需將重開機、下載套件、編譯、雙次執行的流程自動化，降低人為誤差與時間成本。
**技術挑戰**：跨平台批次流程設計與容器/VM 的差異處理。
**影響範圍**：影響測試效率與資料品質。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 手動流程容易出錯。
2. 多平台操作繁瑣。
3. 測試一致性難保證。
**深層原因**：
- 架構層面：需有自動化管線支撐。
- 技術層面：腳本與工具鏈整合。
- 流程層面：標準化不足。

### Solution Design（解決方案設計）
**解決策略**：以 PowerShell/Bash 建立跨平台自動化流程，封裝重開機、套件還原、編譯與雙次執行，並產出標準化報表。

**實施步驟**：
1. 腳本化流程
- 實作細節：模組化每一步驟。
- 所需資源：PowerShell/Bash。
- 預估時間：2-4 小時。

2. 報表與驗證
- 實作細節：收集 log、計算指標、生成報表。
- 所需資源：報表工具。
- 預估時間：2 小時。

**關鍵程式碼/設定**：
```powershell
# 簡易自動化（示例）
.\reboot.ps1
Start-Sleep -Seconds 60
.\restore.ps1
.\build.ps1
.\run.ps1 | Tee-Object run1.log
.\run.ps1 | Tee-Object run2.log
.\compute_metrics.ps1 run2.log > report.txt
# Implementation Example（實作範例）
```

實際案例：原文流程標準化為四步驟並採用第二次結果。
實作環境：Windows 2012 R2、Windows 2016 容器。
實測數據：
改善前：手動流程易偏差（定性）。
改善後：自動化流程提升一致性與效率（定性）。
改善幅度：效率與品質提升（定性）。

Learning Points（學習要點）
核心知識點：
- 自動化帶來的一致性
- 報表與指標整合
- 跨平台腳本設計
技能要求：
必備技能：PowerShell。
進階技能：CI/CD 整合。
延伸思考：
- 觸發器與排程。
- 錯誤復原與告警。
- 擴展到多指標測試。

Practice Exercise（練習題）
基礎練習：寫一個兩次執行的自動化腳本（30 分鐘）。
進階練習：加入報表生成（2 小時）。
專案練習：打造完整測試管線（8 小時）。

Assessment Criteria（評估標準）
功能完整性（40%）：流程全自動完成。
程式碼品質（30%）：模組化、可維護。
效能優化（20%）：縮短無效等待。
創新性（10%）：報表與告警整合。


————————————

案例分類

1. 按難度分類
- 入門級（適合初學者）：Case 3, 4, 5, 7, 8, 9, 12, 13
- 中級（需要一定基礎）：Case 1, 2, 6, 10, 11, 14, 16
- 高級（需要深厚經驗）：Case 15

2. 按技術領域分類
- 架構設計類：Case 11, 14, 15
- 效能優化類：Case 1, 2, 3, 5, 9, 12, 13
- 整合開發類：Case 6, 10, 16
- 除錯診斷類：Case 4, 7, 8, 13
- 安全防護類：Case 15

3. 按學習目標分類
- 概念理解型：Case 7, 11, 14, 15
- 技能練習型：Case 3, 4, 5, 6, 8, 10, 16
- 問題解決型：Case 1, 2, 9, 12, 13
- 創新應用型：Case 11, 15, 16

————————————

案例關聯圖（學習路徑建議）
- 先學案例：Case 3（基準測試流程）、Case 4（監控技巧）、Case 5（pagefile 與記憶體基礎）、Case 9（指標設計）。這些為後續所有測試與分析的基礎。
- 依賴關係：
  - Case 1/2 依賴 Case 3、5、9（需要流程、設定與指標）。
  - Case 6 依賴 Case 14（映像選型）與 Case 10（就地編譯流程）。
  - Case 7 依賴 Case 6（需要容器環境）。
  - Case 11 依賴 Case 1/2/9（數據比較）。
  - Case 15 可由 Case 11 延伸（隔離等級決策）。
  - Case 16 貫穿所有案例（自動化可整合各步）。
- 完整學習路徑建議：
  1) Case 3 → 4 → 5 → 9（打基礎：流程、監控、設定、指標）
  2) Case 10 → 12（環境與操作策略）
  3) Case 1 → 2 → 6 → 7（在原生與容器中完成測試並驗證架構）
  4) Case 11（比較與解讀效能差異）
  5) Case 8（優化容器操作體驗）
  6) Case 14（跨 OS 容器策略）
  7) Case 15（高隔離需求的解法）
  8) Case 13（行為診斷）＋ Case 16（自動化整合）
  完成後具備跨平台記憶體測試與容器架構選型的完整能力。