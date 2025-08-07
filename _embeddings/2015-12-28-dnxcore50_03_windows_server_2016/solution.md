# .NET Core 跨平台：記憶體管理大考驗（Windows Container 2016 TP）

# 問題／解決方案 (Problem/Solution)

## Problem: 在不同 Windows 平台（傳統 VM 與 Container）上驗證 .NET Core 記憶體管理成效

**Problem**:  
在跨平台推廣 .NET Core 的過程中，開發與維運團隊想確認「傳統 Windows VM」與「Windows Container」兩種執行模式，對記憶體配置／回收的實際影響；若無量化資料，就無法決定日後上線時要採 VM、Container，還是進一步採用 Hyper-V Container。

**Root Cause**:  
1. .NET Core 本身仍屬新版本，GC（Garbage Collection）策略在不同 OS／執行環境下是否一致，尚缺乏可參考的公開數據。  
2. Container 與 VM 雖同樣跑在 Windows Kernel 上，但資源分配機制、Page File 策略迥異，直接將 VM 的經驗套到 Container 可能導致錯誤估算。  
3. 若不先量測，在正式環境才發現「高碎片率導致可用記憶體急遽下降」，將影響 SLA 與成本評估。

**Solution**:  
建立一致化「記憶體碎片化壓力測試」工作流程，並在 VM (Windows Server 2012 R2 Server Core) 與 Container (Windows Server 2016 Nano TP 4 Container) 上各自執行，量化比較。

Workflow / Script (Pseudo-code):  
```powershell
# 每種平台都採相同 4 步驟
1. Reset-VM            # 重新啟動 VM 或 Container Host
2. git clone / restore packages
3. dotnet build
4. For (i=1; i -le 2; i++) {           # 連續執行兩次
       dotnet run MemoryFragmentTest   # 第 2 次數據才記錄
   }
```
測試程式流程：  
a. Phase 1：持續配置 64 MB Block，直到失敗，記錄 `MaxAllocatePhase1`  
b. Phase 2：釋放偶數序號 Block，製造碎片  
c. Phase 3：再持續配置 64 MB Block，直到失敗，記錄 `MaxAllocatePhase3`  
d. 計算 Memory Utilization % = `MaxAllocatePhase3 / MaxAllocatePhase1`

關鍵思考：  
• 同一支 Source 直接在目標平台「就地編譯／執行」，排除編譯器差異。  
• 透過 Phase 1/3 差值觀察「碎片對再次配置的影響」，即 GC 與底層分配器的綜合表現。  
• 容器模式與傳統 VM 同時測，可直接衡量 Container 帶來的資源重用效率。

**Cases 1 – Windows Server 2012 R2 Server Core (對照組)**  
• Host RAM: 1 GB, Page File: 4 GB (預設)  
• Phase 1 可配置：4 416 MB  
• Phase 3 可配置：2 888 MB  
• Memory Utilization：65.40 %  
• 觀察：Task Manager 顯示實體 RAM 很快被耗盡，後續全靠 Page File；GC 在碎片化後無法回收全部可用區塊。

**Cases 2 – Windows Server 2016 Nano TP4 (Windows Container)**  
• 基底 Image: `microsoft/windowsservercore`  
• Phase 1 可配置：4 032 MB  
• Phase 3 可配置：2 696 MB  
• Memory Utilization：66.87 %  
• 觀察：Host OS 的 Task Manager 能看見 Container 內的 `dnx.exe`，證明共享同一 Kernel；效能曲線與對照組接近，但因少了 VM Layer，配置／回收延遲略低，最終利用率多 1.4 %。

**Cases 3 – Hyper-V Container（預研、尚未實測）**  
• 若業務需要「Kernel 級隔離」，可啟用 Hyper-V Container：Windows 會自動以輕量化 VM 包住 Container，再執行同套測試流程，即可比較「完全隔離」對 GC 與記憶體配置的額外成本。  

---

透過此一可重製的測試流程，團隊已能：

1. 以量化數據佐證「Container 不會明顯犧牲記憶體利用率，且具備更佳啟動與配置速度」，為日後上線平台選型提供依據。  
2. 將記憶體利用率 (Phase 3 / Phase 1) 納入 CI Pipeline 的回歸指標，持續監控 .NET Core 版本升級對 GC 的影響。