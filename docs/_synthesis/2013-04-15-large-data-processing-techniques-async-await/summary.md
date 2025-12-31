---
layout: synthesis
title: "處理大型資料的技巧 – Async / Await"
synthesis_type: summary
source_post: /2013/04/15/large-data-processing-techniques-async-await/
redirect_from:
  - /2013/04/15/large-data-processing-techniques-async-await/summary/
postid: 2013-04-15-large-data-processing-techniques-async-await
---

# 處理大型資料的技巧 – Async / Await

## 摘要提示
- 問題背景: 從 Azure Blob 讀取大型檔案並透過 Web 回傳時效能僅約直接下載的一半。
- 瓶頸原因: 同步 while 迴圈串行執行 Read/Process/Write，導致 CPU、Disk、Network 無法同時被有效利用。
- 範例模型: 以 Read/Process/Write 分別 200/300/500ms 的延遲模擬大型資料處理流程。
- 多執行緒既有作法: 可用生產者/消費者與管線化提升併行度，但實作複雜、程式結構易碎。
- Async/Await 觀念: 以非同步任務與 await 控制相依點，讓可重疊的工作同時進行。
- 核心改造: 讓 Write 非同步，並與下一輪 Read+Process 重疊，僅在必要時 await 前一個 Write。
- 成效驗證: 總時間由約 10 秒降至約 5.66 秒，接近理論上重疊後的 5 秒。
- 實務條件: 效能取決於 Read/Process/Write 的相對時間與頻寬；重疊空檔越多，收益越大。
- 效益區間: 當 Write 時間≈Read+Process（約 80 Mbps）時改善最大；頻寬越低改善越不明顯。
- 適用時機: 當系統在 I/O 等待多、資源彼此輪流閒置時，用 async/await 比 thread 更易維護且高效。

## 全文重點
本文源自一個看似單純的需求：Web 伺服器需從 Azure Blob 讀大型檔案，處理授權並轉碼後直接回應前端。然而實測吞吐僅約 3.5 Mbps，只有直接從 Blob 下載（7.3 Mbps）的一半。檢視 CPU、頻寬等資源均非滿載，顯示瓶頸不是單一硬體，而是流程設計的低效率。

作者以簡化的範例呈現問題：傳統同步 while 迴圈依序執行 Read、Process、Write，造成任一階段進行時，其餘資源等待，導致 Disk/Network/CPU 無法同時忙碌，整體時間等於三者相加。範例中 Read/Process/Write 分別延遲 200/300/500ms，10 次迭代總共耗時約 10 秒，完全符合串行總和。

過往可藉多執行緒與生產線管線化（producer-consumer、pipeline）讓不同階段重疊執行，縮短總時間，但代價是程式結構割裂、維護成本高。C# 5 與 .NET 4.5 引入 async/await，將非同步模型以語法糖包裹，方法回傳 Task/Task<T>，呼叫可立即返回，需要結果時以 await 等待，使程式仍保持線性結構與可讀性。

本文核心改造極其簡潔：僅將 Write 改為非同步，並在主流程保留前一次 Write 的 Task，於下一次迭代開始前僅在必要時 await 前一次 Write，讓 Write 與下一輪 Read+Process 重疊。由於 Write 與下一次 Read 並無相依性，重疊能最大化管線利用率。實測結果總時間降至約 5.66 秒，其中多出的 ~660ms，來自首輪 Read+Process 與末輪 Write 無法重疊的邊界成本與少量額外負擔，與預期相符。

在實務情境中，Read 受 VM–Storage 頻寬限制（200 Mbps），Process 受 CPU 能力限制，Write 受 Client–VM 網路限制（2–20 Mbps 變動）。作者以不同 client 端頻寬模擬比較，發現當 Write 時間約等於 Read+Process 時（約 80 Mbps），改善效益最高；頻寬降低使 Write 支配總時間，重疊空間縮小，改善幅度遞減，低於約 10% 時可視為體感「無感」提升。

總結來看，async/await 適合解決「等待過多、資源彼此輪流閒置」的效能問題，能以最低侵入的程式改動，讓可重疊的 I/O 與計算並行，縮短總工時；若需求是大規模平行計算，thread/Task 並行仍更合適。關鍵在於辨識流程相依關係與可重疊區段，將 await 放在真正必要的同步點，即可在可讀性與效能間取得良好平衡。

## 段落重點
### 問題背景與症狀
作者在 Web 服務中，需自 Azure Blob 讀取約 100MB 影片，經授權與編碼後直接回應用戶端。整體吞吐僅 3.5 Mbps，較直接下載的 7.3 Mbps 少一半。監控顯示 CPU、頻寬等皆未飽和，代表非單點硬體瓶頸，而是流程導致資源利用不均，造成效率低落。

### 單執行緒瓶頸與序列化流程
為釐清問題，作者用簡化模型：while 迴圈序列執行 Read→Process→Write。因為沒有非同步或多執行緒，任一階段執行時，其他階段必須等待，導致 Disk/Network/CPU 無法同時工作。以時間軸觀察，等同公司三個人卻總是一人工作、兩人等待，效率自然對折。

### 基準程式與同步結果
示範程式以 Task.Delay 模擬 Read 200ms、Process 300ms、Write 500ms，迭代 10 次。結果總時間約 10,000ms，分別對應 2,000ms、3,000ms、5,000ms 的階段累加，驗證純同步串行的特徵：總工時為所有步驟總和，無任何重疊。

### 相關多執行緒經驗與傳統解法
作者回顧過去曾以 MSDN 的 Stream Pipeline、生產者/消費者、以及生產線模式等多執行緒技巧解決類似問題。這些方法核心相同：將流程分段並以管線重疊執行，縮短總時間。然而傳統多執行緒代碼較為繁瑣，需撰寫隊列、同步、協調邏輯，且常破壞原程式的直覺結構。

### Async/Await 概念與時間線重排
隨 .NET 4.5 與 C# 5 出現 async/await，非同步流程得以以「同步風格」撰寫，方法回傳 Task/Task<T>，呼叫可立即返回，必要時以 await 等待結果。作者以時間軸示意：將 Write 設為非同步且不阻塞主流程，並且只在下一次 Write 前 await 上一次 Write 完成；因 Write 與下一輪 Read 無相依，二者可重疊，形成高效管線。

### 改寫重點與執行成果
程式僅將 Write() 改為 async，DoWork() 中保存上一個 Write 的 Task，下一輪開始前若存在則 await，然後立刻發出新的 Write，讓 Read+Process 與 Write 重疊。除首輪與末輪的邊界無法重疊外，其餘大幅重疊，實測總時間約 5.66 秒，接近理論上 5 秒的下限，證明小改動即可帶來顯著效益且維持高可讀性。

### 實務參數與效能比較
在真實環境中，Read 受 VM–Storage 頻寬（200 Mbps）限制，Process 受 CPU 限制，Write 受 Client–VM 頻寬（2–200 Mbps）限制。作者列出不同頻寬下原始與 async 後的耗時與改善百分比。當 Write≈Read+Process（約 80 Mbps）時，改善幅度最大；頻寬愈低，Write 成為主宰，重疊空間減少，效益逐步趨緩。

### 適用場景、限制與結論
可由觀測發現：若 Network/CPU/Disk 等資源皆未滿載但效能不佳，多半是等待過多、步驟相依安排不佳所致。此時應重排流程，讓可重疊的 I/O 與計算並行。async/await 特別適合「片段任務非同步、精準在相依點等待」的情境，代碼簡潔、維護容易；若需求是大規模平行計算，再考慮 thread/並行框架。关键在辨識相依與空檔，將 await 放在正確的同步點。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
   - 同步與非同步的差異、阻塞與非阻塞概念
   - C#/.NET 任務模型：Task、async/await 基本語法（C# 5, .NET Framework 4.5）
   - I/O 與 CPU 資源特性（磁碟、網路、CPU 的瓶頸與併發）
   - Pipeline/生產者-消費者模式的基本概念
   - Azure Storage Blob、ASP.NET 回應串流（Response streaming）的基本流程

2. 核心概念：本文的 3-5 個核心概念及其關係
   - 單執行緒串行流程的資源閒置問題：Read → Process → Write 串行導致 I/O 與 CPU 不能同時工作
   - 非同步重疊（overlap）：用 async/await 讓「Read+Process」與「Write」重疊，提升整體吞吐
   - 正確的等待點：以 await 控制僅在必要的相依點（例如連續 Write）才等待，避免不必要阻塞
   - 效能受限於資源最慢者：頻寬/CPU 決定可重疊幅度；改善效果取決於各段時間的對齊
   - Thread vs Async：大規模平行用 threads；片段任務重疊、精準等待用 async/await 更合適

3. 技術依賴：相關技術之間的依賴關係
   - C# async/await 依賴 .NET Task-based Asynchronous Pattern（Task/Task<T>）
   - 非同步 I/O（Task.Delay 代表 I/O 等待）與計時（Stopwatch）用以量測與模擬
   - Web 串流場景依賴 ASP.NET Response 寫出、Azure Blob 讀取
   - Pipeline 思維指導 async/await 的切點設計（讀/處理/寫的相依分析）

4. 應用場景：適用於哪些實際場景？
   - 大型檔案的串流與轉碼/轉封裝：邊讀 Blob、邊處理、邊回應給用戶端
   - 伺服器端檔案複製/搬移：讀取與寫入儘量重疊
   - 任何包含 I/O 等待且可分段的工作流（網路 I/O、磁碟 I/O 與 CPU 混合）
   - 帶寬與 CPU 可預估、可控的批次資料處理

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
   - 了解同步 vs 非同步、阻塞 vs 非阻塞的概念
   - 寫最小範例：同步版 Read-Process-Write（用 Task.Delay 模擬），量測總時間
   - 將 Write 改為 async，並在迴圈中以 Task 保存上次 Write、await 確保順序，觀察時間改善
   - 用 Stopwatch 量測各段花費時間，理解重疊帶來的總時間下降

2. 進階者路徑：已有基礎如何深化？
   - 導入完整 pipeline：如 ReadAsync、Process、WriteAsync 三段的相依與緩衝策略
   - 針對真實 I/O：以 Blob 讀取、網路回應寫出取代 Delay，觀察瓶頸轉移
   - 研究不同頻寬與 CPU 設定下的改善幅度，建立效能模型（找出 Read+Process ≈ Write 的甜蜜點）
   - 加入錯誤處理與可觀測性：例外傳播、日誌、計量（計時、佔用率）

3. 實戰路徑：如何應用到實際專案？
   - 在 Web 介面層：授權通過後即啟動 Blob 串流讀取，處理邏輯盡量串流化避免整體緩存
   - 將寫出（Response）非同步化，僅在需要維持順序（例如分塊輸出）時 await 前一次寫出
   - 以實測數據驅動調整：根據實際頻寬與 CPU 使用率，調整每次處理的塊大小與併發度
   - 設計回退機制：若改善幅度不足（<10%）則評估是否改用其他策略（多執行緒或結構性改造）

### 關鍵要點清單
- 串行流程的低效率：同步 Read→Process→Write 會讓資源交替閒置，總時間為各段相加 (優先級: 高)
- 非同步重疊的核心：讓「Read+Process」與「Write」同時進行，縮短總時間到兩者較大值附近 (優先級: 高)
- 正確的等待策略：只在真正相依的地方（例如上一個 Write 完成）使用 await (優先級: 高)
- 任務模型（Task/Task<T>）：async 方法回傳 Task；呼叫立即返回、可稍後 await (優先級: 高)
- 效能甜蜜點：當 Write 時間 ≈ Read+Process 時間時，改善幅度最大 (優先級: 中)
- 瓶頸識別：頻寬（Network/Storage）與 CPU 才是決定極限的主因，async 只是重疊等待 (優先級: 高)
- 實測與量化：用 Stopwatch 度量各段時間與總時間，觀察重疊前後變化 (優先級: 中)
- 適用條件：流程中存在大量等待（I/O 等待、網路/磁碟）且可切割為可重疊片段 (優先級: 高)
- 不適用情況：單一段明顯壓倒其他段（例如寫出遠大於其他段）時，重疊收益有限 (優先級: 中)
- 與多執行緒的取捨：大規模平行計算用 threads；片段式非同步協調用 async/await 更簡潔 (優先級: 中)
- Web 串流實務：讀 Blob、處理、寫 Response 以串流方式進行，避免整體緩存 (優先級: 中)
- 範例結果導向：同步約 10s；改為 async 重疊約 5.6s，顯示近倍數改善 (優先級: 中)
- 相依管理：維持寫出順序可透過保存上一個 Write 的 Task 並在下次前 await (優先級: 高)
- 費用與負載觀察：改善後 CPU/Network/Disk 同期更忙碌，反映資源利用率上升 (優先級: 中)
- 實務調參：依頻寬與 CPU 能力，調整分塊大小與處理步驟以最大化重疊 (優先級: 低)