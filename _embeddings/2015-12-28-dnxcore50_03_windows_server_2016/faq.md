# .NET Core 跨平台 #3：記憶體管理大考驗 – Windows Container (2016 TP)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在對照組中選擇 Windows Server 2012 R2 Server Core？
作者希望所有測試組態盡量一致且精簡，Server Core 省去 GUI 可減少干擾與資源消耗，同時與 Linux 測試一樣必須以指令操作，方便比較。

## Q: .NET Core 記憶體碎片化測試在 Windows Server 2012 R2 Server Core 上的結果如何？
第一階段最多可分配 4416 MB，經刻意碎片化後第三階段僅能取得 2888 MB，記憶體利用率為 65.40%。執行期間實體 1 GB RAM 幾乎被用完，其餘則落到 4 GB pagefile 上，顯示回收效果普通。

## Q: Windows Server 2016 Nano (Windows Container) 上的測試結果是什麼？
在 Windows Container 內，第一階段可分配 4032 MB，第三階段可用 2696 MB，整體利用率 66.87%，與原生 Server Core 表現相近。

## Q: Windows Container 與傳統虛擬機 (VM) 的差異為何？
Windows Container 與 Host OS 共用同一套 Kernel，容器內的行程可在主機的工作管理員中看到，沒有完整的 OS 隔離層，因此資源使用更有效率；傳統 VM 則是完全獨立的 OS 與 Kernel。

## Q: 什麼是 Hyper-V Container？它與一般 Windows Container 有什麼不同？
Hyper-V Container 是 TP4 首次曝光的功能，當使用者需要 Kernel 層級隔離時，系統會自動以 Hyper-V 啟動一個輕量 VM，並在其中執行 Container，兼具 VM 的隔離與 Container 的輕量優勢。

## Q: 作者在每個測試平台上執行程式的流程為何？
1. 重新啟動 VM  
2. 下載所需套件  
3. 編譯原始碼  
4. 連續執行兩次程式並取第二次結果，避免首次啟動的最佳化影響數據

## Q: 在 Windows Server Core 沒有 GUI 的情況下，如何快速開啟工作管理員？
可直接在命令提示字元輸入 `taskmgr.exe`，依然能呼叫出工作管理員介面。