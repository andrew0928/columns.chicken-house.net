# Canon Raw Codec + WPF #2, ThreadPool

## 摘要提示
- XP Resize Powertoy停用: Vista 之後原有 Image Resizer Powertoy 因 GDI+→WPF 不相容而失效  
- 自製批次縮圖工具: 以上一集完成的影像 Library 為基礎，模仿 Powertoy 功能  
- Canon RAW Codec效能差: 同尺寸轉檔需 60~80 秒，成為整體瓶頸  
- 多核心利用不足: 內建 ThreadPool 僅約 50~60％ CPU 使用率  
- ThreadPool 缺點: 無法指定 Priority、執行緒數固定、任務難以分流  
- 自建 SimpleThreadPool: 提供固定執行緒數、多組 Pool、可調 Priority 及 WaitAll  
- 雙 Pool 策略: 1 Thread 高優先權處理 RAW，4 Threads 低優先權處理 JPEG  
- 成效: 同批 147 張圖，處理時間由 110 秒降至 90 秒，UI 也更順暢  
- 改善心得: 單靠 ThreadPool 不如編譯器／函式庫內建平行化，但仍可大幅優化  
- 後續計畫: 完成歸檔程式與 Video Encoder，並分享更多經驗  

## 全文重點
作者因 Vista 不支援 XP 時期的 Image Resizer Powertoy，決定自行以 .NET 3.0 WPF 與前篇完成的影像處理 Library 編寫批次縮圖工具。實作過程中碰到四大問題：Canon RAW Codec 解碼極慢、CPU 僅 50% 左右、ThreadPool 無法提升效能且拖慢 UI、UI Thread 受其他工作影響。

實驗顯示，Canon RAW 轉 4000×3000 JPEG 需 60 秒，而縮為 800×600 只要 5 秒，可見 Codec 內部對縮圖有最佳化，但仍屬 CPU bound。為充分利用雙核心，作者嘗試多執行緒並行，卻因 Canon Codec 內部鎖定導致效益不彰。內建 ThreadPool 又無法設定 Priority 與分流，造成 UI 卡頓及資源浪費。

因此作者回到「重新發明輪子」，以 Java 課堂上學到的概念用 C# 寫出僅百行的 SimpleThreadPool。功能包括：自定執行緒數、設定優先權、多 Pool 併用、簡易 WaitAll。實際運用時將 RAW 任務丟入 1 Thread 的高優先權 Pool，JPEG 任務丟入 4 Thread 的低優先權 Pool。結果顯示 CPU 佔用更平均，147 張（125 JPEG＋22 RAW）從 110 秒縮短為 90 秒，且預覽影像可即時更新，UI 更流暢。

作者最後指出，ThreadPool 調校雖有效，但最佳平行化仍應寄望於編譯器或函式庫層級（如 Intel 並行工具或 Microsoft Parallel Extensions）。現階段解決了 Thread、Metadata 等障礙，Image Resizer 已可用，接下來將整合歸檔與 Video Encoder 功能。

## 段落重點
### 1. 背景：失去的 Powertoy 與自製需求
Windows XP 的 Image Resizer Powertoy 在 Vista 失效，作者因工作流程依賴批次縮圖，被迫自行動手實作替代方案。

### 2. 初版工具與四大瓶頸
用前篇 Library 快速打造 WPF 介面後，實測發現效能低落：RAW 轉檔慢、多核心利用率低、ThreadPool 不給力、UI 受阻塞。

### 3. Canon RAW Codec 行為分析
比較 4000×3000 與 800×600 轉檔時間，推論 Canon Codec 於解碼階段已對縮圖優化，但其內部鎖定使並行化難以奏效。

### 4. 思考：Thread 排程策略
目標是讓耗時的 RAW 與快速的 JPEG 能同時占用 CPU，又不影響 UI，因而需要可控的 ThreadPool 以分流與設優先權。

### 5. 實作 SimpleThreadPool
參考早年 Java 範例，用 C# 寫出百行左右的 ThreadPool：固定 Thread 數、可調 Priority、多 Pool、簡易等待機制，並維持與內建 ThreadPool 相近介面。

### 6. 雙 Pool 應用與效能比較
建立 1 Thread（High）處理 RAW、4 Threads（BelowNormal）處理 JPEG 的結構；測試 147 張圖 CPU 利用率與完成時間，90 秒優於原 110 秒，UI 即時回饋。

### 7. 心得與後續
適度調整 Thread 數與 Priority 能解決多數瓶頸，但真正高效仍需函式庫級並行化。現階段 Image Resizer 已完成，下一步將整合影片編碼與檔案歸檔功能。