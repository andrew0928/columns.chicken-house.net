---
layout: synthesis
title: ".NET Core 跨平台 #5, 多工運算效能大考驗 – 計算圓周率測試"
synthesis_type: summary
source_post: /2016/01/15/dnxcore50_05_compute_pi_test/
redirect_from:
  - /2016/01/15/dnxcore50_05_compute_pi_test/summary/
---

# .NET Core 跨平台 #5, 多工運算效能大考驗 – 計算圓周率測試

## 摘要提示
- 測試目的: 以 CPU-bound 的圓周率計算與平行任務，評估 .NET Core 在不同平台/核心數的多工效能與執行緒調度差異。
- 指標設計: 以 Total Execute Time、Average Execute Time 與 Efficiency Rate 三指標觀察單執行效率與平行擴展性。
- 平台組合: 比較 Windows Server 2012 R2、Windows Server 2016 TP4 (Nano + Container)、Ubuntu 15.10 + Docker、Boot2Docker，另有 Windows 10 實體機對照。
- 核心變因: VM 以 1/2/4/8 核心配置反覆測試，並以 1/2/4/8/16/32/64 個 Task 執行同等運算量。
- 調度機制: 採 .NET Task 預設排程，不另行控制 ThreadPool 或自訂並行模型，以貼近平台預設行為。
- Windows 優勢: Windows 家族在運算速度與平行效率上整體領先，2016 TP4 在 4/8 核心尤為亮眼。
- Linux 表現: Ubuntu + Docker 在本測試中落後於 Windows，Boot2Docker 僅在 1 核心場景表現突出。
- 超執行緒影響: 4 核心/8執行緒下效率提升趨緩，顯示實體核心與超執行緒在平行加速上的差異。
- 效率比例: Windows 2016 的 Efficiency Rate 最高（約 531%），顯示極度輕量化與平台最佳化兼具成效。
- 實務建議: 若以 C# 追求運算效能，選 Windows Server 較有利；但平台選擇仍須兼顧維運與生態成本。

## 全文重點
本文延續先前的記憶體管理測試，將焦點轉向 CPU-bound 場景，以計算 10000 位圓周率為工作負載，透過 System.Threading.Tasks 同步啟動 1/2/4/8/16/32/64 個 Task，比較不同平台在 1/2/4/8 核心配置下的 .NET Core 多工效能與調度成效。測試指標包含整體完成時間（Total Execute Time）、單任務平均時間（Average Execute Time）與平行效率提升率（Efficiency Rate）。Total 衡量整體速度，Average 反映單任務效能與執行緒開銷，Efficiency Rate 評估平行化帶來的實際加速比例。

測試環境涵蓋 Windows Server 2012 R2、Windows Server 2016 TP4 Nano（以 Windows Container 執行）、Ubuntu 15.10 + Docker、Boot2Docker 1.9 + Docker，並提供 Windows 10 實體機作對照。硬體以同一台 PC 的 VM 控制資源，確保比較一致性。程序採 Task 預設排程，不加入自訂多執行緒策略，重點在觀察平台與 CLR/執行緒管理的內建最佳化差異。

結果顯示，隨核心增加，Total 與 Average 的下降趨勢符合預期，ThreadPool 有效避免過度建立執行緒而導致額外負擔；在 1 核心時，任務數倍增幾乎等比例拉長時間；在多核心時，Total 在核心未飽和前接近持平。綜觀平台，Windows 家族整體領先，尤其 Windows Server 2016 TP4 在 4/8 核心的表現最佳；2012 R2 穩定但略遜。Boot2Docker 在 1 核心場景最快，但在多核心遭 Windows 超越。Ubuntu + Docker 在本輪測試中落後，顯示 .NET Core 在 Windows 上的 JIT/Native 與執行緒管理仍具優勢。

Efficiency Rate 顯示平行效能近似隨核心數成正比提升，但在 4 核心/8 執行緒（超執行緒）時增益趨緩，符合超執行緒非等同實體核心的認知。Windows 2016 的效率提升可達約 531%，領先 2012 R2 的約 470%，顯示在輕量化（Nano/Container）與平台最佳化上具體成效。作者也提醒，雖然效能差距存在（2016 與 Ubuntu 約 10.4%），實務選型仍需考量維運成本、工具鏈與生態系整合，不宜僅以效能定奪。本文最後指出，從記憶體到 CPU 的兩輪測試揭示平台差異確實可觀，未來將再整理其他研究心得。

## 段落重點
### 前言與測試目的
作者延續前幾篇對記憶體的研究，轉向 CPU 運算效能的比較，選用計算 10000 位圓周率作為 CPU-bound 工作負載。與其純粹「比分數」，更希望藉由跨平台測試理解 .NET Core 在不同 OS 上的 JIT、執行緒與資源管理差異，並從結果反推平台機制。前次記憶體試驗已揭示 Linux 與 Windows 在預設行為上的顯著差異，促成本次針對多工與調度的延伸觀察。

### 測試方法與指標
以 System.Threading.Tasks 啟動 1/2/4/8/16/32/64 個等量任務，測量在 1/2/4/8 核心 VM 上的表現。三個指標：Total Execute Time 衡量整體完成時間、Average Execute Time 衡量單任務平均耗時（可觀察單核效能與執行緒/排程成本）、Efficiency Rate 反映平行化帶來的整體效率提升比例（以 1 核心、1 任務作為基準）。採用 Task 預設排程，不施加自訂多執行緒或生產者/消費者等模式，目的是讓平台與 CLR 本身的預設最佳化自然顯現，便於跨平台公平比較。

### 測試平台與環境
平台包含 Windows Server 2012 R2（Server Core 原生執行 .NET Core）、Windows Server 2016 TP4（Nano + Windows Container + CoreCLR）、Ubuntu 15.10 + Docker 1.9.1、Boot2Docker 1.9.1 + Docker，以及 Windows 10 實體機（對照）。硬體以同一台 i7-2600K/24GB/SSD 的主機建置 VM，統一 RAM/Swap/HDD 額度並以 1/2/4/8 核心分別測試。Windows 10 實體機無法關閉核心，僅提供 8 邏輯執行緒之參考數據。此設計確保不同 OS 在近似資源條件下比對其 CLR、JIT、執行緒與排程機制的差別。

### Windows Server 2012 R2 結果
以圖表解讀可發現：在 1 核心時任務數倍增，Total 幾乎等比例拉長；當核心數增加，Total 在核心未飽和前相對平穩，顯示 ThreadPool 控制了執行緒並行度以避免排程/搶占成本過高。Average 隨任務數上升而成長幅度趨緩，也呈現排程與併發度控制有效。Efficiency Rate 大致隨核心數上升而成比例改善；然在 i7-2600K 的 4C/8T 架構下，擴展到 8 執行緒的邊際效益下降，呼應超執行緒非等同實體核心的特性。

### Windows Server 2016 TP4 (Nano + Container) 結果
2016 TP4 在少核心（1/2）時表現不甚突出，但在 4/8 核心時明顯竄升至最佳，顯示當並行度上升、系統排程與 CLR/JIT 最佳化可發揮時，輕量化 Nano 與容器環境帶來的低干擾、低負擔優勢浮現。這也暗示 Windows 對 .NET Core 的底層支援與最佳化正在成熟，即便為 TP 版本，仍能在多核心場景展現顯著效率。

### Ubuntu 15.10 + Docker 結果
在本輪測試中，Ubuntu + Docker 並未如預期般以輕量取勝，無論是 Total 或 Average，整體落後於 Windows 家族。可能原因包含 JIT/Native 與執行緒調度在 Linux 版 CoreCLR 的最佳化程度仍有差距，加上容器層的細微開銷與 OS 調度策略差異，使 CPU-bound 任務的平行化收益未能完全釋放。不過差距約莫在一成上下，對一般應用不一定具體可感。

### Boot2Docker 1.9 + Docker 結果
Boot2Docker 在 1 核心時因極度精簡的環境而表現出色，但當核心數增加，Windows 的最佳化優勢開始顯現並反超。這反映輕量化對低並行度時的好處明確，但在高並行度下，CLR 與 OS 對執行緒、排程、快取親和性與記憶體子系統的整體最佳化，對最終效能的影響更為關鍵。

### 對照組：Windows 10 實體機
實體機僅提供 8 邏輯執行緒之參考數據，未能逐核關閉。數據顯示在無虛擬化干擾的前提下，.NET Core 的 CPU-bound 任務具良好穩定性；但因測試條件不同（非 VM 控管），可作為趨勢參考，不宜直接與 VM 場景逐點比較。

### 綜合比較—Total Execute Time
整體來看，Windows 平台在多核心場景下維持領先；2016 TP4 在 4/8 核心名列前茅，2012 R2 緊隨其後。Boot2Docker 在 1 核心最快，但隨核心增加優勢轉弱。Ubuntu 在此輪測試落於末位。作者推測 Windows 在 JIT/Native 與執行緒管理上的深度最佳化是關鍵，特別是高並行度下，調度與排程更能拉開差距。

### 綜合比較—Average Execute Time
Average 的趨勢與 Total 類似，反映單任務執行效率與排程成本在 Windows 上較有優勢。Windows Server 2016 的輕量化（Nano/Container）與平台級最佳化同時發揮，使單任務耗時在高任務數下仍能維持相對穩定。Ubuntu 則在此指標敬陪末座，顯示 Linux 下 CoreCLR/JIT 與執行緒切換的平均開銷仍待優化。

### 綜合比較—Efficiency Rate
Efficiency Rate 隨核心數上升而提升，2016 TP4 最高，達約 531%，顯著領先 2012 R2 的約 470%。雖然 2016 在 1 核心表現較弱，但在多核心時的強勢使整體效率比例被放大。4C/8T 的邊際效益下降亦再次印證超執行緒的限制。此指標綜合反映了平台在平行化、排程、Context Switch 與快取使用等面向的整體協同能力。

### 結論與實務建議
若重視以 C# 進行 CPU-bound 運算的效能，Windows Server 家族仍是首選；Windows Server 2016（即便為 TP）在多核心下展現最佳 Total、Average 與 Efficiency Rate，顯示 .NET Core 與 Windows 的結合在 JIT、排程與輕量化面均已成熟。不過效能差距約一成，實務選型仍需綜合維運成本、現有生態、工具鏈與相容性考量。本文兩階段（記憶體/CPU）實驗顯示，OS 對 .NET Core 的底層行為具有實質影響；未來作者將整理更多研究過程中的細節與心得。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 .NET/.NET Core 與 C# 語法
   - Task Parallel Library（System.Threading.Tasks）與執行緒/執行緒池概念
   - CPU-bound vs I/O-bound 的差異
   - 虛擬化與容器的基本觀念（Hyper-V/VM、Docker、映像與容器）
   - 基本效能量測方法與指標解讀（時間、平均、加速比/效率）

2. 核心概念：
   - 平行運算模型：以 Task 為單位，交由執行緒池與 OS 調度
   - 三大指標：Total Execute Time、Average Execute Time、Efficiency Rate（平行效率）
   - 測試設計：固定 CPU-bound 工作（計算圓周率 10000 位），改變任務數與核心數觀察
   - 平台差異：同為 .NET Core，因 OS 執行緒/排程與 JIT/原生編譯差異而出現效能落差
   - 真核心 vs 超執行緒：實體核心的效能改善高於 Hyper-Threading 的線程

3. 技術依賴：
   - .NET Core CLR 與 JIT/（可選）native 編譯行為
   - Task Parallel Library 依賴 OS 執行緒與排程器
   - 虛擬機（VM）與容器（Docker）層的開銷與資源配置影響
   - OS 層（Windows/Ubuntu/Boot2Docker）對記憶體、執行緒、排程的實作差異

4. 應用場景：
   - 需要跨平台部署的 CPU-bound 後端服務評估
   - 多核心環境下平行化策略驗證與參數調校
   - 比較 VM、容器與裸機部署下的效能差異
   - 對 .NET Core 在不同 OS 的最佳化程度作決策依據（例如選 OS/容器基底）

### 學習路徑建議
1. 入門者路徑：
   - 了解 CPU-bound vs I/O-bound 與多執行緒基本觀念
   - 練習使用 Task 與 ThreadPool，撰寫簡單 CPU 密集程式（如計算任務）
   - 學會量測基礎三指標（Total、Average、Efficiency）並能解讀

2. 進階者路徑：
   - 以同一程式在不同核心數、不同任務數做系統化測試
   - 在不同平台（Windows/Ubuntu/Boot2Docker）與不同部署型態（VM/Container）進行對照
   - 探索 JIT 與可能的 native 編譯差異、GC 模式、ThreadPool 設定對效能的影響

3. 實戰路徑：
   - 建立自動化基準測試腳本，統一硬體資源配置（VM/容器）
   - 對服務關鍵路徑抽出可重複的 CPU-bound 測試案例，持續追蹤版本差異
   - 依量測結果調整部署策略（選 OS、核心數、容器基底），形成 SLO 與容量規劃指引

### 關鍵要點清單
- 測試目標明確化: 以 CPU-bound（圓周率 10000 位）排除 I/O/記憶體干擾，比較跨平台純運算效能 (優先級: 高)
- 三大效能指標: Total、Average、Efficiency Rate 的定義與解讀方法 (優先級: 高)
- 任務與核心設計: 任務數（1/2/4/8/16/32/64）x 核心數（1/2/4/8）矩陣設計可觀察伸縮性 (優先級: 高)
- Task/ThreadPool 機制: 預設排程即可有效控制執行緒數，避免過度排程反致退化 (優先級: 高)
- 真核心 vs 超執行緒: 4 核心進步顯著，8「執行緒」改善有限，HT 不等於加倍效能 (優先級: 高)
- 平台表現排序: 整體 Windows 家族領先，Windows Server 2016 在 4/8 核心特別亮眼 (優先級: 高)
- 單核心反差: 1 核時 Boot2Docker 最快，2016 在 1/2 核偏慢但多核擴展後反超 (優先級: 中)
- Ubuntu 表現: 此測試中平均落後於 Windows 家族，顯示 .NET Core 在 Windows 上最佳化較成熟 (優先級: 中)
- 效率率最高值: Windows 2016 Efficiency Rate 約 531%，顯示多工效益最佳 (優先級: 中)
- 設備與環境一致性: 用相同宿主與 VM 規格控變，確保比較公平 (優先級: 高)
- 指標選擇策略: 想看單執行緒/JIT效能看 Total；想看多核平行效益看 Efficiency (優先級: 高)
- 容器/VM 影響: 輕量容器並非處處領先，OS 與 CLR 最佳化程度更關鍵 (優先級: 中)
- 實務決策平衡: 效能差距約 10% 等級時，維運成本、相容性、工具鏈更需納入考量 (優先級: 高)
- 原始碼重現: 公開 GitHub 專案可自取重跑，驗證在自家環境的實測差異 (優先級: 中)
- 後續優化方向: 探索 GC 模式、ThreadPool 參數、native 編譯與 OS 調度對 CPU-bound 的影響 (優先級: 中)