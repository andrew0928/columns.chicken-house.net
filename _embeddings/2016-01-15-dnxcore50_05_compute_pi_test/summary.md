# .NET Core 跨平台 #5 ─ 多工運算效能大考驗：計算圓周率

## 摘要提示
- 測試目標: 以 10000 位圓周率的 CPU Bound 工作評估 .NET Core 在不同平台的多工運算效能。
- 測試指標: 透過 Total Execute Time、Average Execute Time 及 Efficiency Rate 三項量化整體與個別 Task 表現。
- 平台組合: Windows Server 2012 R2、Windows Server 2016 TP4 Nano+Container、Ubuntu 15.10+Docker、Boot2Docker 1.9+Docker、實體 Windows 10 對照組。
- 硬體配置: 以同一台 PC 開 VM，1/2/4/8 Core、1 GB RAM、固定 Swap 與磁碟，確保環境可比。
- Thread Pool 行為: 觀察 Total/Average 隨 Core 增加趨緩，證實 Task 調度能抑制過度排線。
- Hyper-Threading: 4 Core 8 Thread 時效益不如 4 真核心，顯示邏輯執行緒仍有瓶頸。
- Windows 優勢: 除單核心外，Win Server 系列總體效能領先，2016 Nano 在 4/8 Core 衝上第一。
- Linux 表現: Ubuntu 與 Boot2Docker 效能落後，Average Time 尤其顯著。
- 最佳化推論: 微軟在 JIT、執行緒管理與 Nano Server 輕量化上投入最佳化，成效明顯。
- 平台建議: 若極度重視 C# 計算效能，首選 Windows Server 2016；但仍須綜合維運、工具與相容性成本評估。

## 全文重點
本文為「.NET Core 跨平台」系列的第五篇，聚焦在多核心 CPU 運算效能差異。作者選擇計算 10000 位圓周率做為典型 CPU-Bound 工作，並利用 System.Threading.Tasks 同時執行 1/2/4/8/16/32/64 個計算 Task，在 1/2/4/8 核心的硬體設定下測出三組指標：1) Total Execute Time 代表所有 Task 完成所需總時間；2) Average Execute Time 為單 Task 平均完成時間；3) Efficiency Rate 量化平行處理相對單工的整體效益。  
測試環境涵蓋 Windows Server 2012 R2、Windows Server 2016 TP4 Nano（Container 內）、Ubuntu 15.10 + Docker、Boot2Docker 1.9 + Docker，以及作者實體機 Windows 10 做對照。為排除 I/O 與記憶體影響，VM 統一配置 1 GB RAM、固定 Swap 與相同磁碟。  
結果顯示：  
1. Thread Pool 調度有效，核心未用盡前 Total/Average 幾乎固定；  
2. 隨真核心數增加 Efficiency Rate 近線性上升，而 Hyper-Threading 僅帶來有限增益；  
3. Windows Server 2016 Nano 在 4/8 Core 的 Total、Average 及 Efficiency 均拔得頭籌，Efficiency 高達 531%；  
4. Ubuntu 與 Boot2Docker 數據普遍墊底，尤其 Average Time 顯示單 Task 執行速度較慢；  
5. Windows Server 2012 R2 雖在多核心表現略遜 2016，但仍明顯優於兩組 Linux；  
6. 結論指出 .NET Core 仍在 Windows 上擁有最佳化優勢，特別是對 JIT 與執行緒管理的深度掌控，而 Nano Server 的極度精簡更進一步釋放效能。  
作者最後提醒，效能並非唯一考量，Linux 在部署成本與生態系亦具吸引力；兩者差距僅約一成，實務上應同時衡量維運便利與系統需求。

## 段落重點
### 測試動機與設計
作者承襲前篇記憶體實驗，改以 CPU Bound 工作探討多工效能差異。透過計算圓周率排除 I/O 與記憶體因素，並設定三大指標評分，期望比較不同 OS 與容器對 .NET Core 平行運算的影響，同時觀察 Thread Pool 與 OS 調度細節。

### 指標說明與評估方式
Total Execute Time 衡量整體耗時；Average Execute Time 反映單 Task 效率；Efficiency Rate 則以單核基準推算平行效益。指標可分別用於評估 JIT、原生編譯差異及 OS 對多工最佳化的貢獻。

### 測試環境與硬體配置
所有平台皆在同一台 i7-2600K PC 中以 VM 執行，核心數分別設定 1/2/4/8，記憶體 1 GB、Swap 4 GB、32 GB VHDX，確保除 OS 以外的軟硬體條件一致。對照組則為未虛擬化的 Windows 10 實機。

### Windows Server 2012 R2 成果
1 Core 下 Task 數越多耗時近線性增加；多核心後 Total 幾乎持平，顯示 Thread Pool 排程成功。Efficiency 最多可達 470%，表現穩定但在 8 Core 時略受 Hyper-Threading 限制。

### Windows Server 2016 TP4 Nano 成果
1/2 Core 成績落後，但進入 4/8 Core 後大幅領先，Total 與 Average 均為四平台最佳，Efficiency 創 531% 高點，顯示 Nano Server 輕量化與新一代排程最佳化效果顯著。

### Ubuntu 15.10 + Docker 成果
整體耗時與單 Task 耗時皆居末，Efficiency 雖隨核心增加但斜率較低。顯示目前 .NET Core 在 Linux 上的 JIT 與執行緒管理仍有優化空間。

### Boot2Docker 1.9 + Docker 成果
在單核心時以極輕量 OS 取得微幅領先，其餘多核心場合仍略遜 Windows；Average 與 Efficiency 介於 Ubuntu 與 Windows 之間，證實極小化鏡像僅能帶來有限好處。

### 綜合比較與結論
跨平台圖表顯示 Windows Server 系列全面領先，其中 2016 Nano 在多核心環境最優。Linux 雖落後約 10%，但考慮部署、維運與生態系仍具吸引力；最終平台選擇應在效能與總擁有成本間取得平衡。