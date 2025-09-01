## Case #1: 建立跨平台記憶體測試一致流程（重開機/下載/編譯/雙次執行）

### Problem Statement（問題陳述）
業務場景：團隊需要比較 .NET Core 在不同 Windows 平台（Windows Server 2012 R2 Server Core、Windows Server 2016 Nano Container）上的記憶體管理表現，並量化記憶體碎片化對可用記憶體的影響。現有測試流程不一致、容易受第一次啟動最佳化影響，導致數據不可比。
技術挑戰：如何制定跨平台一致、可重現的測試流程，排除第一次啟動（JIT、快取建置）等干擾。
影響範圍：錯誤解讀碎片化影響、跨平台結論失真、優化方向誤判。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 首次執行帶有 JIT 與相依套件還原開銷，造成測量偏差。
2. 測試前系統快取與可用記憶體狀態不一致。
3. 不同平台的下載/編譯步驟不同，導致流程差異。
深層原因：
- 架構層面：缺乏跨平台一致的測試管線設計。
- 技術層面：未考慮 .NET Core 首次啟動效應與依賴快取。
- 流程層面：測試步驟未標準化（重開機、套件還原、重複執行規則）。

### Solution Design（解決方案設計）
解決策略：建立標準化測試流程：統一先重開機清空快取，再下載/還原相依、同機編譯，連續執行兩次採第二次數據，確保跨平台可比與可重現性；同時固定輸出格式，方便後續自動彙整。

實施步驟：
1. 定義測試腳本與輸出規格
- 實作細節：規範重開機後的動作順序、輸出 JSON/CSV 格式。
- 所需資源：PowerShell、.NET SDK、Git/封存碼檔。
- 預估時間：0.5 天

2. 建立「雙次執行」規則
- 實作細節：連跑兩次，記錄兩次數據，取第二次為正式數據。
- 所需資源：PowerShell 腳本、logger。
- 預估時間：0.5 天

3. 自動化封裝
- 實作細節：將下載/還原/編譯/執行/收集數據整合為一鍵腳本。
- 所需資源：CI/本機批次腳本。
- 預估時間：1 天

關鍵程式碼/設定：
```ps1
# run-test.ps1
param(
  [string]$RepoDir = "C:\memtest",
  [string]$Log = "C:\memtest\result.json"
)

# 1) 還原/編譯（就地）
Set-Location $RepoDir
dotnet restore
dotnet build -c Release

# 2) 連續執行兩次
$first = & .\bin\Release\netX\memtest.exe --json
$second = & .\bin\Release\netX\memtest.exe --json

# 3) 取第二次數據
$second | Out-File -Encoding utf8 $Log
Write-Host "Saved to $Log"
```
實際案例：文中採用「重開機 → 下載套件 → 編譯 → 連續執行兩次取第二次」流程來確保一致性。
實作環境：Windows Server 2012 R2 Server Core、Windows Server 2016 TP4（Windows Container）
實測數據：
改善前：單次執行，第一次啟動含最佳化干擾（定性）
改善後：雙次執行取第二次，波動顯著降低（定性）
改善幅度：定性提升（數據穩定性提升，便於跨平台比較）

Learning Points（學習要點）
核心知識點：
- 首次啟動效應（JIT/快取）對測量的影響
- 測試流程標準化的重要性
- 以固定輸出格式支援後續自動報表

技能要求：
必備技能：PowerShell、自動化腳本、.NET 基本建置
進階技能：CI/CD 腳本化、跨平台測試編排

延伸思考：
- 流程可套用至效能/IO/網路測試
- 風險：忽略實務工作負載可能與測試負載不同
- 可進一步使用容器/VM快照清場

Practice Exercise（練習題）
基礎練習：撰寫腳本實作雙次執行並輸出 JSON（30 分）
進階練習：加入錯誤處理與重試機制（2 小時）
專案練習：打造跨 OS 的一鍵測試工具（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可自動執行全流程並產出標準輸出
程式碼品質（30%）：結構清晰、具備錯誤處理/日誌
效能優化（20%）：執行時間合理、無多餘步驟
創新性（10%）：可擴充、易整合其他測試模組


## Case #2: 設計「記憶體利用率%」指標以量化碎片化影響

### Problem Statement（問題陳述）
業務場景：團隊需要用單一數字衡量記憶體碎片化後的實際可用度，方便跨平台比較。僅看峰值或最終值無法反映碎片化程度。
技術挑戰：如何定義簡潔、穩健且可重現的指標，跨平台皆適用。
影響範圍：若無統一指標，會誤判平台差異與優化成效。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有統一標尺比較不同平台。
2. 單看可用記憶體峰值無法反映碎片化後的衰退。
3. 測量方式不一致導致結論不一致。
深層原因：
- 架構層面：缺乏量化層的設計與資料模型。
- 技術層面：未統一取得 Phase 1/3 的定義。
- 流程層面：測後彙整缺標準化工具。

### Solution Design（解決方案設計）
解決策略：定義「記憶體利用率% = Phase3 可取得記憶體 / Phase1 可取得記憶體 × 100%」，以 Phase1 為基準，Phase3 反映碎片化後可用性，並提供自動計算腳本。

實施步驟：
1. 規範數據輸出字段
- 實作細節：統一輸出 phase1Bytes、phase3Bytes
- 所需資源：小改測試程式輸出
- 預估時間：0.5 天

2. 建立計算工具
- 實作細節：用 PowerShell/Python 計算比值、格式化
- 所需資源：腳本環境
- 預估時間：0.5 天

3. 報表化
- 實作細節：輸出 CSV/Markdown，便於對比
- 所需資源：模板
- 預估時間：0.5 天

關鍵程式碼/設定：
```ps1
# calc-util.ps1
param([long]$Phase1,[long]$Phase3)
$util = [math]::Round(($Phase3*100.0)/$Phase1,2)
"{0} / {1} => Utilization: {2}%" -f $Phase3,$Phase1,$util
```
實際案例：文中據此計算 Windows 2012 R2 為 65.40%，Windows 2016 Container 為 66.87%。
實作環境：同上
實測數據：
改善前：無統一指標（無法直接比較）
改善後：有統一%指標（65.40% vs 66.87%）
改善幅度：跨平台比較效率與可解讀性明顯提升（定性）

Learning Points（學習要點）
核心知識點：
- 指標設計與可比性
- 碎片化前後的基準選取
- 自動化計算與報表輸出

技能要求：
必備技能：基本腳本、資料處理
進階技能：資料可視化/報表自動化

延伸思考：
- 可加權引入 Phase2（碎片化過程）資訊
- 風險：不同工作負載型態可能需多指標
- 可延伸至 GC/LOH 專屬指標

Practice Exercise（練習題）
基礎練習：用腳本計算三組 Phase1/3 的利用率（30 分）
進階練習：輸出比較圖表（2 小時）
專案練習：製作指標儀表板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可正確計算/輸出
程式碼品質（30%）：可維護與可擴充
效能優化（20%）：處理大量數據效率
創新性（10%）：可視化呈現創新度


## Case #3: Windows Server 2012 R2 Server Core 記憶體碎片化測試與解讀

### Problem Statement（問題陳述）
業務場景：在 Windows Server 2012 R2 Server Core（1GB RAM+4GB pagefile）上，需評估 .NET Core（dnx）於碎片化後可再取得的大記憶體空間，以作為後續容器對照組基準。
技術挑戰：在無 GUI 的 Server Core 上完成就地編譯與測試、蒐集碎片化前後的可用記憶體。
影響範圍：此基線直接影響跨平台比較與優化目標設定。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無 GUI 工具，觀測困難。
2. 首次啟動偏差需排除。
3. RAM 嚴重不足（1GB），高度依賴 pagefile。
深層原因：
- 架構層面：Server Core 精簡化導致觀測手段受限。
- 技術層面：大記憶體配置易導致 LOH/虛擬記憶體碎片。
- 流程層面：需流程化測試與數據收集。

### Solution Design（解決方案設計）
解決策略：遵循標準流程（重開機、下載、編譯、雙次執行取第二次），輸出 Phase1/Phase3 數據，並以 Task Manager/PowerShell 驗證；建立此組合的「碎片化利用率」基準。

實施步驟：
1. 編譯與雙次執行
- 實作細節：就地還原/編譯，執行兩次取第二次
- 所需資源：PowerShell/.NET SDK
- 預估時間：1 小時

2. 數據蒐集與驗證
- 實作細節：輸出 JSON/CSV，輔以 Task Manager/PowerShell 觀測
- 所需資源：taskmgr、Get-Process
- 預估時間：0.5 小時

3. 建立基準
- 實作細節：計算利用率%，記錄為對照組
- 所需資源：calc-util 腳本
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
// MemoryFragmentTest.cs
// 三階段：Phase1 連續配置、Phase2 製造碎片、Phase3 再次配置
using System;
using System.Collections.Generic;

class Program {
  static void Main() {
    List<byte[]> blocks = new();
    long total1 = AllocUntilFail(blocks, 64 * 1024 * 1024); // 64MB 塊
    // Phase2: 釋放部分製造碎片
    for (int i = 0; i < blocks.Count; i += 2) blocks[i] = null;
    GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();
    // Phase3: 再次配置
    long total3 = AllocUntilFail(new List<byte[]>(), 64 * 1024 * 1024);
    Console.WriteLine($"{{\"phase1MB\":{total1/1024/1024},\"phase3MB\":{total3/1024/1024}}}");
  }

  static long AllocUntilFail(List<byte[]> keep, int chunk) {
    long sum = 0;
    try {
      while (true) { var b = new byte[chunk]; keep.Add(b); sum += chunk; }
    } catch (OutOfMemoryException) { }
    return sum;
  }
}
```
實際案例：Phase1 可取得 4416MB，Phase3 可取得 2888MB
實作環境：Windows Server 2012 R2 Server Core，RAM 1GB，pagefile 4GB
實測數據：
改善前：無基準
改善後：利用率 65.40%（2888/4416）
改善幅度：建立可比較基準（定性）

Learning Points（學習要點）
核心知識點：
- LOH/虛擬記憶體碎片概念
- Server Core 環境下的觀測方法
- 基準（baseline）的重要性

技能要求：
必備技能：C#、PowerShell、Server Core 操作
進階技能：記憶體壓測設計、GC 觀念

延伸思考：
- 欲提高 Phase3，策略有哪些（重用、大塊連續配置等）
- Pagefile 政策對結果影響
- 分塊大小與碎片化程度關係

Practice Exercise（練習題）
基礎練習：調整塊大小觀察結果（30 分）
進階練習：加入不同釋放策略（2 小時）
專案練習：自動出圖比較多次測試（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：三階段測試/輸出數據
程式碼品質（30%）：結構清晰、錯誤處理
效能優化（20%）：避免非必要配置
創新性（10%）：可擴充測試維度


## Case #4: 無 GUI 的 Server Core 上進行記憶體觀測（taskmgr 與 PowerShell）

### Problem Statement（問題陳述）
業務場景：Server Core 無傳統 GUI，需監控 dnx.exe 的記憶體使用（Working Set、Commit、RAM/頁檔互動）以輔助測試解讀。
技術挑戰：缺少熟悉的圖形工具；需使用命令列/內建工具觀測。
影響範圍：無法佐證測試結果、錯誤判讀實體/虛擬記憶體比例。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Server Core 無完整 GUI。
2. 不熟悉命令列觀測工具。
3. 單看程式輸出不足以理解系統層面行為。
深層原因：
- 架構層面：精簡化 OS 組件。
- 技術層面：缺少標準觀測手冊。
- 流程層面：未將觀測納入測試 SOP。

### Solution Design（解決方案設計）
解決策略：使用 taskmgr.exe（可啟動的精簡工作管理員）、PowerShell Get-Process/typeperf/Get-Counter 輔助觀測，建立最小可用的觀測標準。

實施步驟：
1. 啟用最小 GUI 視窗
- 實作細節：在 cmd 輸入 taskmgr.exe 開啟工作管理員
- 所需資源：Server Core 內建
- 預估時間：10 分鐘

2. 命令列觀測
- 實作細節：Get-Process、typeperf 取得數據
- 所需資源：PowerShell
- 預估時間：20 分鐘

3. 納入 SOP
- 實作細節：編寫觀測步驟與截圖/輸出樣板
- 所需資源：文件
- 預估時間：0.5 天

關鍵程式碼/設定：
```ps1
# 觀測進程記憶體
Get-Process dnx | Select Name,Id,WorkingSet,PM,VM | Format-List

# 觀測系統記憶體
typeperf "\Memory\Available MBytes" "\Memory\Committed Bytes" -si 1 -sc 30
```
實際案例：dnx.exe Working Set 約 4548MB；1GB RAM 被使用約 800MB
實作環境：Windows Server 2012 R2 Server Core
實測數據：
改善前：缺乏可視化/數據佐證
改善後：可量化觀測（4548MB、800MB）
改善幅度：觀測可得性顯著提升（定性）

Learning Points（學習要點）
核心知識點：
- Server Core 仍可啟動 taskmgr.exe
- Working Set/Private Bytes/Commit 意義
- typeperf/Get-Counter 用法

技能要求：
必備技能：PowerShell、Windows 記憶體計數器
進階技能：建立觀測自動化腳本

延伸思考：
- 可整合到報表自動化
- 在容器環境如何觀測
- 避免觀測行為影響被測進程

Practice Exercise（練習題）
基礎練習：輸出 dnx.exe 記憶體三指標（30 分）
進階練習：以 typeperf 收集 1 分鐘樣本（2 小時）
專案練習：撰寫觀測與報表一體化腳本（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能輸出關鍵指標
程式碼品質（30%）：腳本穩定
效能優化（20%）：收集頻率合理
創新性（10%）：易用性/可視化改善


## Case #5: Windows Server 2016（TP4）Windows Container 設定與記憶體碎片測試

### Problem Statement（問題陳述）
業務場景：在 Windows 容器（Windows Server 2016 TP4）中重現 .NET Core 記憶體碎片測試，並與對照組（Server Core）比較差異。
技術挑戰：TP 階段回應遲緩、需從 windowsservercore 映像建立環境、就地編譯/執行。
影響範圍：若無法在容器重現，無法完成跨平台比較與容器效能判讀。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. TP4 相容性/效能未完全優化。
2. 無法使用 Linux 映像，需從 Windows Server Core 起步。
3. 容器內互動式操作延遲。
深層原因：
- 架構層面：Windows Container 與 Docker 工具鏈整合初期。
- 技術層面：基底鏡像體積大、相依安裝繁瑣。
- 流程層面：缺少容器內建置與測試 SOP。

### Solution Design（解決方案設計）
解決策略：以 windowsservercore 作為 base image，容器內準備 .NET Core/測試程式碼，採非互動式自動化執行並輸出 Phase1/Phase3，與對照組以統一指標比較。

實施步驟：
1. 建立 Dockerfile
- 實作細節：FROM windowsservercore，安裝 .NET、放入測試程式。
- 所需資源：Docker for Windows（支援 Windows 容器）
- 預估時間：0.5-1 天

2. 自動執行測試
- 實作細節：ENTRYPOINT 執行測試並輸出 JSON
- 所需資源：PowerShell
- 預估時間：0.5 天

3. 收集並比較
- 實作細節：docker logs/檔案輸出，計算利用率
- 所需資源：calc-util 腳本
- 預估時間：0.5 天

關鍵程式碼/設定：
```dockerfile
# Dockerfile (Windows Container)
FROM mcr.microsoft.com/windows/servercore:ltsc2016
SHELL ["powershell","-Command"]

# 假設已將測試程式編譯好或容器內編譯
WORKDIR C:\app
COPY .\bin\Release\netX\ .\

ENTRYPOINT ["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe","-Command","./memtest.exe --json > result.json; Get-Content result.json"]
```
實際案例：Phase1 4032MB，Phase3 2696MB，利用率 66.87%
實作環境：Windows Server 2016 TP4 Windows Container
實測數據：
改善前：無法在容器中量測
改善後：容器完成量測（66.87%）
改善幅度：具備與對照組可比性

Learning Points（學習要點）
核心知識點：
- Windows Container 與 Docker 工具鏈
- Windows Base Image 的限制與建置
- 容器中非互動式量測模式

技能要求：
必備技能：Docker（Windows）、PowerShell
進階技能：容器內建置/最佳化

延伸思考：
- 改用多階段建置縮小鏡像
- 在新版本 Windows Server 測試差異
- 結合 CI 在容器跑壓測

Practice Exercise（練習題）
基礎練習：Build/Run Dockerfile 並取得 result.json（30 分）
進階練習：在容器內編譯測試程式（2 小時）
專案練習：自動比較容器與對照組（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：容器可跑測試並輸出數據
程式碼品質（30%）：Dockerfile 清晰可維護
效能優化（20%）：鏡像體積/執行時間
創新性（10%）：自動化/整合程度


## Case #6: 驗證 Windows Container 與 Host 共享 Kernel（Host 上觀測容器內程序）

### Problem Statement（問題陳述）
業務場景：需確認 Windows Container 與 Host 共用同一 Kernel，避免將容器誤解為 VM，正確解讀資源使用與效能。
技術挑戰：如何在 Host 直接觀測到容器內的進程證據。
影響範圍：錯誤認知會導致錯誤資源規劃與隔離策略。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 容器與 VM 混淆。
2. 缺少證據鏈支撐結論。
3. 工具使用不熟悉。
深層原因：
- 架構層面：容器共享 Kernel 的設計認知缺口。
- 技術層面：Windows 容器觀測方法未制度化。
- 流程層面：未將觀測納入驗證步驟。

### Solution Design（解決方案設計）
解決策略：在 Host 上使用 Task Manager/PowerShell 觀察容器內程序，並與容器內 ps 對照，確認兩者一致，作為共用 Kernel 的可視化證據。

實施步驟：
1. 容器內觀測
- 實作細節：docker exec 列出程序
- 所需資源：Docker CLI
- 預估時間：10 分

2. Host 觀測
- 實作細節：taskmgr / Get-Process 結對觀測
- 所需資源：PowerShell
- 預估時間：10 分

3. 紀錄證據
- 實作細節：截圖/輸出程序清單存檔
- 所需資源：文件
- 預估時間：10 分

關鍵程式碼/設定：
```ps1
# 容器內
docker exec <cid> powershell "Get-Process | Sort WS -desc | Select -First 5"

# Host
Get-Process | Sort WS -desc | Select -First 20
# 對照程序名稱/參數，驗證可見性
```
實際案例：文中以 Host Task Manager 可見容器內命令，證明共用 Kernel
實作環境：Windows Server 2016 TP4 Host + Windows Container
實測數據：
改善前：不確定容器與 Host 關係
改善後：以觀測佐證共用 Kernel（定性）
改善幅度：認知正確性提升

Learning Points（學習要點）
核心知識點：
- 容器 vs VM 的核心差異
- Windows 上的容器觀測技巧
- 觀測與驗證的證據鏈

技能要求：
必備技能：Docker 基本操作、PowerShell
進階技能：系統觀測與追蹤

延伸思考：
- 加入 ETW/PerfCounter 深化觀測
- Hyper-V 容器與 Windows 容器可見性差異
- 安全/隔離設計影響

Practice Exercise（練習題）
基礎練習：在 Host/容器分別列出前 5 大記憶體程序（30 分）
進階練習：寫腳本自動對照（2 小時）
專案練習：產生容器/Host 對照報表（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能佐證共用 Kernel
程式碼品質（30%）：對照自動化腳本品質
效能優化（20%）：收集效率
創新性（10%）：可視化呈現


## Case #7: 容器 vs 對照組記憶體利用率比較與結論產出

### Problem Statement（問題陳述）
業務場景：需將 Windows 容器（2016 TP4）與 Server Core（2012 R2）記憶體碎片化利用率以統一指標比較，產出可溝通結論。
技術挑戰：確保比較基準一致、數據正確。
影響範圍：影響是否採用容器的技術選型。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無統一的比較框架。
2. 容器內互動式延遲可能影響測試方式。
3. 各平台環境差異。
深層原因：
- 架構層面：缺乏跨平台對照設計。
- 技術層面：計量與抽樣未標準化。
- 流程層面：報表與結論表述缺流程。

### Solution Design（解決方案設計）
解決策略：以 Case #2 定義的利用率%計算兩平台結果，對齊流程（Case #1），以簡明結論表述差異（pp/相對差）。

實施步驟：
1. 取數與計算
- 實作細節：讀入兩平台 Phase1/3 值，計算 %
- 所需資源：calc-util 腳本
- 預估時間：10 分

2. 對照/結論
- 實作細節：計算差值、生成文字結論
- 所需資源：模板
- 預估時間：20 分

3. 報表化
- 實作細節：輸出表格/圖
- 所需資源：Excel/腳本
- 預估時間：30 分

關鍵程式碼/設定：
```ps1
# compare.ps1
$w2012 = @{phase1=4416; phase3=2888}
$w2016 = @{phase1=4032; phase3=2696}
function rate($h){ [math]::Round(($h.phase3*100.0)/$h.phase1,2) }
"{0}% vs {1}% (Δ={2}pp)" -f (rate $w2012),(rate $w2016),((rate $w2016)-(rate $w2012))
```
實際案例：2012 R2 = 65.40%；2016 容器 = 66.87%；差異 +1.47pp（相對約 +2.25%）
實作環境：同上
實測數據：
改善前：缺少可讀結論
改善後：產出可比結論（容器與原生差距極小）
改善幅度：決策效率提升

Learning Points（學習要點）
核心知識點：
- 使用 pp（百分點）表述差異
- 相對差與絕對差的意義
- 報表溝通的重要性

技能要求：
必備技能：基本資料處理
進階技能：可視化/文字表述技巧

延伸思考：
- 加入更多平台或版本比較
- 引入統計檢定（穩定性）
- 自動匯整多 run 結果

Practice Exercise（練習題）
基礎練習：計算兩組數據的 pp 差（30 分）
進階練習：輸出圖表（2 小時）
專案練習：多平台比較報告（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：正確計算與結論
程式碼品質（30%）：簡潔與可維護
效能優化（20%）：處理多組數據
創新性（10%）：表達與視覺化


## Case #8: 預覽版容器互動延遲的繞道（非互動與遠端執行）

### Problem Statement（問題陳述）
業務場景：在 Windows 容器 TP4 下使用互動式終端（-it）延遲明顯，影響測試操作效率。
技術挑戰：如何在不影響測試準確性的前提下，提高操作回應。
影響範圍：測試耗時增加、操作體驗差。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. TP 版本效能未優化。
2. 互動式終端造成額外開銷。
3. 容器與 Host 的互動管道延遲。
深層原因：
- 架構層面：通訊路徑/IO 管線仍在調整。
- 技術層面：互動式 shell 開銷高。
- 流程層面：過度倚賴互動操作。

### Solution Design（解決方案設計）
解決策略：改為非互動式命令（docker exec/ENTRYPOINT 腳本化）、使用 PowerShell Remoting 到容器，將互動步驟自動化，降低人機交互延遲。

實施步驟：
1. 以 docker exec 執行命令
- 實作細節：exec 非互動命令並收集輸出
- 所需資源：Docker CLI
- 預估時間：10 分

2. PowerShell Remoting
- 實作細節：Enter-PSSession -ContainerId（支援時）
- 所需資源：PowerShell
- 預估時間：20 分

3. 腳本化 ENTRYPOINT
- 實作細節：容器啟動即執行測試與輸出
- 所需資源：Dockerfile
- 預估時間：30 分

關鍵程式碼/設定：
```ps1
# 非互動式執行測試
docker run --rm my/memtest:win powershell -Command "./memtest.exe --json > C:\out\result.json"
docker cp $(docker ps -alq):C:\out\result.json .

# 或對既有容器
docker exec <cid> powershell "Start-Process -Wait .\memtest.exe -ArgumentList '--json'"
```
實際案例：文中提及互動式模式明顯較慢，採非互動/腳本化可繞過
實作環境：Windows Server 2016 TP4 容器
實測數據：
改善前：互動式延遲明顯（定性）
改善後：非互動/腳本化，操作回應提升（定性）
改善幅度：體感大幅改善（定性）

Learning Points（學習要點）
核心知識點：
- 互動式 vs 非互動式容器操作
- Remoting 的應用
- 腳本化降低人機交互

技能要求：
必備技能：Docker、PowerShell
進階技能：自動化管線設計

延伸思考：
- 後期版本效能改善後策略是否調整
- 日誌/輸出收集標準化
- 結合 CI 容器化測試

Practice Exercise（練習題）
基礎練習：用 exec 執行命令並擷取輸出（30 分）
進階練習：建置 ENTRYPOINT 腳本（2 小時）
專案練習：整合到 CI（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能非互動式完成操作
程式碼品質（30%）：腳本可靠
效能優化（20%）：操作時間可感縮短
創新性（10%）：Remoting/自動化整合


## Case #9: 低 RAM + 預設 Pagefile 的測試條件校準

### Problem Statement（問題陳述）
業務場景：測試 VM 僅 1GB RAM，需依賴 pagefile（預設 4GB），以確保 Phase1 能達到數 GB 的配置；需可按需校準。
技術挑戰：不同 VM/OS 的 pagefile 政策差異導致可配置上限不同。
影響範圍：Phase1 上限與碎片化結果受影響，跨平台不可比。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未明確設定 pagefile 大小。
2. 系統自動管理可能導致上限不同。
3. RAM 太小，依賴虛擬記憶體。
深層原因：
- 架構層面：記憶體與儲存策略耦合。
- 技術層面：Commit/Working Set 交互作用。
- 流程層面：測試前置條件未標準化。

### Solution Design（解決方案設計）
解決策略：顯式設定固定大小的 pagefile，或紀錄系統預設值；將 pagefile 配置納入測試報告欄位，確保可比性。

實施步驟：
1. 查詢現狀
- 實作細節：wmic pagefile/list，Get-CimInstance
- 所需資源：PowerShell
- 預估時間：10 分

2. 設定固定 pagefile
- 實作細節：關閉自動管理，建立/調整大小
- 所需資源：系統權限
- 預估時間：20 分

3. 重開機與確認
- 實作細節：Restart-Computer 後再查詢
- 所需資源：PowerShell
- 預估時間：10 分

關鍵程式碼/設定：
```ps1
# 查詢
wmic pagefile list /format:list
# 設定
wmic computersystem set AutomaticManagedPagefile=False
wmic pagefileset where name="C:\\pagefile.sys" delete
wmic pagefileset create name="C:\\pagefile.sys"
wmic pagefileset where name="C:\\pagefile.sys" set InitialSize=4096,MaximumSize=4096
```
實際案例：文中在 1GB RAM + 4GB pagefile 的情境下，Phase1 可達 4416MB
實作環境：Windows Server 2012 R2 Server Core
實測數據：
改善前：pagefile 未明確/不可比
改善後：有明確 pagefile 設定/紀錄（Phase1=4416MB）
改善幅度：數據可比性提升

Learning Points（學習要點）
核心知識點：
- Pagefile 對 Commit 上限影響
- RAM 與虛擬記憶體的互動
- 測試前置條件的紀錄

技能要求：
必備技能：PowerShell、系統管理
進階技能：容量規劃與壓測設計

延伸思考：
- 不同 pagefile 大小對 Phase3 的影響
- SSD/HDD 對效能的影響
- 生產環境政策與測試政策差異

Practice Exercise（練習題）
基礎練習：查詢/輸出 pagefile 設定（30 分）
進階練習：自動套用設定並重開（2 小時）
專案練習：多 VM 一致化設定工具（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可設定/查詢成功
程式碼品質（30%）：安全與回滾
效能優化（20%）：最少重開機影響
創新性（10%）：一鍵標準化


## Case #10: 在 Server Core 上以命令列打造最小觀測套件

### Problem Statement（問題陳述）
業務場景：Server Core 環境需建立最小化但足夠的觀測能力以支援測試解讀與故障排查。
技術挑戰：僅能使用命令列與內建工具。
影響範圍：降低誤判與節省除錯時間。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少 GUI 工具。
2. 操作人員對命令列工具不熟。
3. 無標準觀測步驟。
深層原因：
- 架構層面：精簡化 OS
- 技術層面：工具使用門檻
- 流程層面：SOP 缺失

### Solution Design（解決方案設計）
解決策略：選定 typeperf/Get-Counter/Wevtutil 等內建工具，形成一頁式觀測 SOP，支援測試前中後的關鍵訊號收集。

實施步驟：
1. 指標清單
- 實作細節：可用記憶體/Committed Bytes/Process 記憶體
- 所需資源：內建計數器
- 預估時間：30 分

2. 腳本化
- 實作細節：單檔腳本一鍵收集
- 所需資源：PowerShell
- 預估時間：1 小時

3. 文檔化
- 實作細節：ReadMe/SOP 圖示步驟
- 所需資源：文件
- 預估時間：0.5 天

關鍵程式碼/設定：
```ps1
typeperf "\Memory\Available MBytes" "\Memory\Committed Bytes" -si 1 -sc 60 > mem.csv
Get-Process | Sort WS -desc | Select -First 10 | Out-File top.txt
wevtutil qe System /c:50 /rd:true /f:text > syslog.txt
```
實際案例：文中以工作管理員與記憶體曲線輔助解讀（右半飆高為啟動期）
實作環境：Windows Server 2012 R2 Server Core
實測數據：
改善前：觀測不足
改善後：最小觀測套件可用（定性）
改善幅度：除錯效率提升（定性）

Learning Points（學習要點）
核心知識點：
- Windows 計數器與事件查詢
- 最小可用觀測集合
- 觀測與測試結合

技能要求：
必備技能：PowerShell、Windows 管理
進階技能：資料後處理與可視化

延伸思考：
- 將結果上傳至中央儲存
- 加入 CPU/IO 計數器
- 時間同步確保資料對齊

Practice Exercise（練習題）
基礎練習：收集 1 分鐘計數器（30 分）
進階練習：合併多個輸出為單一報告（2 小時）
專案練習：打包成 Toolkit（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可完整收集所需訊號
程式碼品質（30%）：易用/註解完整
效能優化（20%）：最少侵入
創新性（10%）：整合與自動化


## Case #11: 就地編譯以避免跨平台組建差異

### Problem Statement（問題陳述）
業務場景：需確保測試程式在受測平台上就地編譯，避免跨機器/跨 OS 組建差異影響結果。
技術挑戰：在 Server Core/Container 內完成還原/編譯。
影響範圍：提高測試公信力與可重現性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 不同環境產生的二進位差異。
2. 相依套件版本不一致。
3. 編譯選項差異導致表現差異。
深層原因：
- 架構層面：缺少組建一致性策略。
- 技術層面：相依管理與工具鏈差異。
- 流程層面：未規範就地編譯。

### Solution Design（解決方案設計）
解決策略：在每個受測平台執行 dotnet restore/build（或 dnu/dnx 時代對應命令），以同一來源碼、同版本 SDK 完成就地編譯。

實施步驟：
1. 準備 SDK
- 實作細節：平台內安裝 .NET SDK
- 所需資源：離線安裝包/網路
- 預估時間：0.5 天

2. 還原/編譯
- 實作細節：dotnet restore/build -c Release
- 所需資源：NuGet
- 預估時間：30 分

3. 鎖定版本
- 實作細節：global.json/Sdk 版本鎖定
- 所需資源：版本管理
- 預估時間：30 分

關鍵程式碼/設定：
```ps1
dotnet --info
dotnet restore
dotnet build -c Release
# 若為舊版 DNX 時代，使用 dnu restore / dnx build
```
實際案例：文中明載「拿 source code 直接到受測平台，就地編譯就地測試」
實作環境：Windows Server 2012 R2 / Windows 2016 容器
實測數據：
改善前：跨平台編譯，結果可疑
改善後：就地編譯，結果可信（定性）
改善幅度：數據可信度提升

Learning Points（學習要點）
核心知識點：
- 就地編譯的重要性
- 套件版本鎖定
- 平台工具鏈一致性

技能要求：
必備技能：.NET SDK、NuGet
進階技能：多平台組建策略

延伸思考：
- 以容器封裝組建工具鏈
- 鎖定 hash/清單保障可再現
- 與 CI 整合

Practice Exercise（練習題）
基礎練習：在 VM 內做 dotnet build（30 分）
進階練習：鎖定 SDK 版本與還原來源（2 小時）
專案練習：多平台組建 pipeline（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可就地編譯成功
程式碼品質（30%）：版本鎖定/文件完整
效能優化（20%）：編譯時間合理
創新性（10%）：封裝/自動化


## Case #12: 從 windowsservercore 基底打造 .NET 測試容器映像

### Problem Statement（問題陳述）
業務場景：Windows 容器無法使用 Linux 映像，需自 windowsservercore 起步打造可運行 .NET 測試的映像。
技術挑戰：安裝/配置 .NET 與相依，控制鏡像體積與可維護性。
影響範圍：影響容器建置成本與測試效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 容器必須依賴 Host Kernel，不可混用 Linux 映像。
2. Windows Base Image 體積大。
3. 安裝路徑/相依複雜。
深層原因：
- 架構層面：Windows Container 與 Docker 架構差異。
- 技術層面：安裝 .NET 的步驟繁瑣。
- 流程層面：缺少可重用 Dockerfile 模板。

### Solution Design（解決方案設計）
解決策略：使用官方 windowsservercore 基底，撰寫 Dockerfile 腳本化安裝 .NET 與測試程式；可加入多階段建置或外部掛載 artifacts，減少體積與建置時間。

實施步驟：
1. 撰寫 Dockerfile
- 實作細節：下載/安裝 .NET、清理暫存
- 所需資源：離線安裝包或網路
- 預估時間：0.5-1 天

2. 建置與驗證
- 實作細節：docker build/run，確認 dotnet --info
- 所需資源：Docker
- 預估時間：1 小時

3. 最佳化
- 實作細節：分層/清理/快取
- 所需資源：Docker 多階段
- 預估時間：1 天

關鍵程式碼/設定：
```dockerfile
FROM mcr.microsoft.com/windows/servercore:ltsc2016
SHELL ["powershell","-Command"]

# 安裝 .NET Runtime（示意）
RUN Invoke-WebRequest https://download.visualstudio.microsoft.com/.../dotnet-runtime.exe -OutFile dotnet-runtime.exe; \
    Start-Process .\dotnet-runtime.exe -ArgumentList '/quiet','/norestart' -Wait; \
    Remove-Item .\dotnet-runtime.exe

WORKDIR C:\app
COPY .\publish\ .\
ENTRYPOINT ["dotnet","memtest.dll"]
```
實際案例：文中說明無法使用 Linux 映像，需從 Windows Server Core 起步。
實作環境：Windows Server 2016 TP4 容器
實測數據：
改善前：無法直接使用 Linux 映像
改善後：成功建置 Windows 基底映像（定性）
改善幅度：可執行測試於容器

Learning Points（學習要點）
核心知識點：
- Windows Container 與映像選型
- Dockerfile 在 Windows 上的差異
- 體積與快取最佳化

技能要求：
必備技能：Dockerfile、PowerShell
進階技能：多階段建置與快取策略

延伸思考：
- 使用 Nano Server 基底（適用性）
- 以外掛檔案減低層次寫入
- 以私有 Registry 管理版本

Practice Exercise（練習題）
基礎練習：Build/Run 基本映像（30 分）
進階練習：加入清理/快取（2 小時）
專案練習：打造可重用 .NET 測試基底映像（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：映像可執行測試
程式碼品質（30%）：Dockerfile 可維護
效能優化（20%）：層數/體積控制
創新性（10%）：建置策略創新


## Case #13: 何時選擇 Hyper-V Container：Kernel 隔離需求與切換方法

### Problem Statement（問題陳述）
業務場景：某些場景需要 Kernel 隔離（合規/安全），需在 Windows 容器與 Hyper-V 容器間選擇並切換。
技術挑戰：在維持容器優點（映像/工具鏈）的前提下提供 VM 等級隔離。
影響範圍：安全/合規/多租戶隔離策略。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Windows 容器共享 Kernel，無法滿足某些隔離需求。
2. 需要在相同工具鏈中提供隔離選項。
3. 缺少簡便切換方法。
深層原因：
- 架構層面：Hyper-V 容器以輕量 VM 提供隔離。
- 技術層面：映像/管理需相容。
- 流程層面：選型準則缺失。

### Solution Design（解決方案設計）
解決策略：基於相同映像與 Docker 工具鏈，透過 --isolation=hyperv 啟動 Hyper-V 容器，於需要時提供 Kernel 隔離；建立選型準則（性能 vs 隔離）。

實施步驟：
1. 驗證支援
- 實作細節：docker info 檢查 isolation 支援
- 所需資源：Windows Server 2016+ 與 Hyper-V
- 預估時間：10 分

2. 切換啟動
- 實作細節：docker run --isolation=hyperv
- 所需資源：Docker CLI
- 預估時間：10 分

3. 文件化準則
- 實作細節：何時用 Windows Container/Hyper-V Container
- 所需資源：文件
- 預估時間：0.5 天

關鍵程式碼/設定：
```ps1
docker run --isolation=hyperv --rm my/memtest:win powershell -Command "./memtest.exe --json"
```
實際案例：文中引用 TP4 首現 Hyper-V Container 並說明其定位
實作環境：Windows Server 2016/TP4
實測數據：
改善前：僅有共享 Kernel 的容器選項
改善後：在需要時可用 Hyper-V Container 提供隔離（定性）
改善幅度：隔離能力提升

Learning Points（學習要點）
核心知識點：
- Windows Container vs Hyper-V Container
- 隔離/效能取捨
- 實際切換方法

技能要求：
必備技能：Docker/Windows 容器
進階技能：安全與合規規劃

延伸思考：
- Hyper-V 容器效能成本量測
- 與 K8s on Windows 整合策略
- 映像共用最佳實踐

Practice Exercise（練習題）
基礎練習：啟動 Hyper-V 容器（30 分）
進階練習：比較兩種模式啟動時間（2 小時）
專案練習：選型指南與範例庫（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可成功切換與運行
程式碼品質（30%）：命令與腳本清晰
效能優化（20%）：啟動時間合理
創新性（10%）：選型指南完整


## Case #14: 以計數器追蹤 Phase 啟動/碎片化/再配置三階段走勢

### Problem Statement（問題陳述）
業務場景：需將三階段（啟動期、碎片化、再配置）的記憶體走勢以計數器視角記錄，以輔助結果解讀（例如右半段飆高）。
技術挑戰：選取合適計數器與採樣間隔，避免過度入侵。
影響範圍：提升對 GC/Commit/WS 變化的理解。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單次數值不足以說明過程。
2. 無連續時間序列數據。
3. 無標準採樣與對齊方法。
深層原因：
- 架構層面：測試程式與系統觀測缺整合。
- 技術層面：計數器選型與採樣策略。
- 流程層面：資料對齊/命名缺乏規範。

### Solution Design（解決方案設計）
解決策略：定義計數器清單（Available MBytes、Committed Bytes、Process WS/Private Bytes），以 1s 採樣，對齊三階段事件點，輸出 CSV 並圖表化。

實施步驟：
1. 計數器設定
- 實作細節：typeperf 清單與頻率
- 所需資源：PowerShell
- 預估時間：20 分

2. 事件對齊
- 實作細節：在程式輸出 Phase 標記時間
- 所需資源：程式改版
- 預估時間：1 小時

3. 圖表化
- 實作細節：Excel/腳本產圖
- 所需資源：工具
- 預估時間：30 分

關鍵程式碼/設定：
```ps1
typeperf "\Memory\Available MBytes" "\Memory\Committed Bytes" "\Process(dnx)\Working Set" -si 1 -sc 120 > trend.csv
```
實際案例：文中圖示啟動期實體記憶體快速吃滿，其後多用虛擬記憶體
實作環境：Windows Server 2012 R2 Server Core
實測數據：
改善前：缺少過程曲線
改善後：有曲線可解讀（定性）
改善幅度：分析深度提升

Learning Points（學習要點）
核心知識點：
- 計數器選型與意義
- 採樣頻率與入侵性
- 事件點對齊方法

技能要求：
必備技能：typeperf、資料分析
進階技能：自動化圖表與報表

延伸思考：
- 關聯 GC 事件（ETW）
- 對比不同塊大小/策略
- 多次 run 疊圖比較

Practice Exercise（練習題）
基礎練習：收集 2 分鐘曲線（30 分）
進階練習：加上事件標記（2 小時）
專案練習：自動產圖管線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能收集與輸出
程式碼品質（30%）：腳本可靠
效能優化（20%）：適當採樣頻率
創新性（10%）：圖表設計


## Case #15: 一鍵測試與報告輸出（比值計算、表格化與結論模板）

### Problem Statement（問題陳述）
業務場景：多平台/多次測試需自動彙整 Phase1/3、利用率%、差異 pp，輸出報表與簡明結論，供決策者快速理解。
技術挑戰：異質輸出整合、格式標準化、模板化結論。
影響範圍：節省人力、降低錯誤、提升決策效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手動彙整易出錯。
2. 缺少標準輸出模板。
3. 比較指標計算不一致。
深層原因：
- 架構層面：缺報表層模組。
- 技術層面：資料清洗與轉換。
- 流程層面：報表製作未自動化。

### Solution Design（解決方案設計）
解決策略：統一結果為 JSON/CSV，撰寫 PowerShell 解析與比值計算，匯出彙總表與結論段落；模板包含平台、Phase1/3、利用率%、pp 差。

實施步驟：
1. 格式統一
- 實作細節：規範輸出字段與路徑
- 所需資源：測試程式改版
- 預估時間：0.5 天

2. 解析與匯總
- 實作細節：讀入多檔、計算、合併
- 所需資源：PowerShell
- 預估時間：0.5-1 天

3. 輸出模板
- 實作細節：Markdown/CSV/HTML
- 所需資源：模板
- 預估時間：0.5 天

關鍵程式碼/設定：
```ps1
# summarize.ps1
$files = Get-ChildItem . -Filter *.json
$rows = foreach($f in $files){
  $o = Get-Content $f | ConvertFrom-Json
  [pscustomobject]@{
    Platform = $f.BaseName
    Phase1MB = $o.phase1MB
    Phase3MB = $o.phase3MB
    Util = [math]::Round(($o.phase3MB*100.0)/$o.phase1MB,2)
  }
}
$rows | Export-Csv summary.csv -NoTypeInformation
```
實際案例：文中已計算 65.40% 與 66.87%，可由工具自動產出報表
實作環境：Windows Server 平台
實測數據：
改善前：人工彙整
改善後：一鍵輸出報表（含利用率與差異）
改善幅度：效率與正確性提升（定性）

Learning Points（學習要點）
核心知識點：
- 資料格式與清洗
- 批次解析與彙總
- 模板化結論

技能要求：
必備技能：PowerShell、資料處理
進階技能：報表自動化/HTML 輸出

延伸思考：
- 加入圖表與趨勢
- 發布至 Wiki/Portal
- 整合 CI 作為 artifacts

Practice Exercise（練習題）
基礎練習：合併兩份結果輸出 CSV（30 分）
進階練習：輸出 Markdown 表格（2 小時）
專案練習：完整報告產生器（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能正確匯總
程式碼品質（30%）：結構清晰
效能優化（20%）：處理多檔效率
創新性（10%）：輸出表現力


--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #2（指標設計）
  - Case #4（Server Core 觀測）
  - Case #6（容器共享 Kernel 驗證）
  - Case #7（比較與結論）
  - Case #11（就地編譯）
- 中級（需要一定基礎）
  - Case #1（一致流程）
  - Case #3（2012 R2 測試）
  - Case #5（Windows 容器測試）
  - Case #9（Pagefile 校準）
  - Case #10（最小觀測套件）
  - Case #12（Windows 基底映像）
  - Case #14（三階段走勢）
  - Case #15（一鍵報表）
- 高級（需要深厚經驗）
  - Case #8（TP 互動延遲繞道與自動化）
  - Case #13（Hyper-V Container 選型）

2. 按技術領域分類
- 架構設計類
  - Case #1, #2, #7, #13, #15
- 效能優化類
  - Case #3, #5, #8, #9, #14
- 整合開發類
  - Case #11, #12
- 除錯診斷類
  - Case #4, #6, #10, #14
- 安全防護類
  - Case #13

3. 按學習目標分類
- 概念理解型
  - Case #2, #6, #7, #13, #14
- 技能練習型
  - Case #4, #10, #11, #12, #15
- 問題解決型
  - Case #1, #3, #5, #8, #9
- 創新應用型
  - Case #7, #13, #15


案例關聯圖（學習路徑建議）
- 建議先學：
  - Case #2（指標設計）→ 了解如何量化
  - Case #1（一致流程）→ 確保後續測試可比
  - Case #11（就地編譯）→ 保證工件一致
- 依賴關係：
  - Case #3、#5 依賴 Case #1/#2（流程與指標）
  - Case #7（比較）依賴 #3、#5 的結果
  - Case #6（共享 Kernel 驗證）可與 #5 並行
  - Case #8（互動延遲繞道）依賴 #5 的容器環境
  - Case #9（Pagefile 校準）支撐 #3 的前置條件
  - Case #10、#14（觀測與走勢）可強化 #3/#5 的解讀
  - Case #12（映像打造）支援 #5 的建置
  - Case #13（Hyper-V Container）在理解 #6 後選型
  - Case #15（報表）整合 #3/#5/#7 等輸出
- 完整學習路徑建議：
  1) 指標與流程：#2 → #1 → #11
  2) 建置與觀測：#12 → #5 → #6 → #10 → #14
  3) 量測與比較：#3 → #9 → #7 → #15
  4) 進階與選型：#8 → #13

此學習路徑由基礎量化方法起，逐步建立可重現的測試流程與環境，進入實測與觀測，再到跨平台比較與報表輸出，最後涵蓋預覽期環境的實務繞道與隔離選型，完成從方法、建置、量測到決策的全閉環實戰。