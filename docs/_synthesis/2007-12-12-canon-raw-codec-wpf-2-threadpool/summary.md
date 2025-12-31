---
layout: synthesis
title: "Canon Raw Codec + WPF #2, ThreadPool"
synthesis_type: summary
source_post: /2007/12/12/canon-raw-codec-wpf-2-threadpool/
redirect_from:
  - /2007/12/12/canon-raw-codec-wpf-2-threadpool/summary/
postid: 2007-12-12-canon-raw-codec-wpf-2-threadpool
---

# Canon Raw Codec + WPF #2, ThreadPool

## 摘要提示
- 目標工具: 以自製 Image Resizer 取代 Vista 上無法使用的 Resize Pictures Power Toy
- 效能瓶頸: Canon RAW 解碼耗時嚴重，單張同尺寸轉檔需 60–80 秒
- 多核利用: 內建 ThreadPool 難以有效動用多核，CPU 使用率停在約 50–60%
- ThreadPool 侷限: 無法設定執行緒優先權，易干擾 UI thread 回應
- 解碼特性: Canon RAW 在縮圖輸出時明顯較快，推測 decode 階段具降尺度特化
- 任務排程策略: RAW 解碼以高優先權單執行緒，JPEG 以多執行緒分擔剩餘 CPU
- 自製 ThreadPool: 實作固定數量、可設定優先權、多池、可等待完成的 SimpleThreadPool
- 實測結果: 以自製 ThreadPool 將總耗時從 110 秒降至 90 秒，且 UI 回應改善
- UI 流暢性: 調整優先權後，轉檔完成即時更新預覽，避免進度列與影像不同步
- 後續方向: 真正高效平行化應在函式庫/編譯器層，關注 .NET 平行程式庫未來發展

## 全文重點
作者想在 Vista 環境重現 Windows XP 時期的 Resize Pictures Power Toy 便捷批次縮圖體驗，遂以先前完成的 WPF + Canon RAW Codec 專案為基礎，開發簡單的 Image Resizer。實作過程卻遇到四大障礙：Canon RAW 解碼極慢（同尺寸轉檔 60–80 秒）、多核心利用不足（雙核僅 50% 多的 CPU 使用率）、內建 ThreadPool 無法進一步提升 RAW 解碼效能、且 ThreadPool 的背景工作會干擾 UI thread 使預覽不即時。觀察發現：若輸出縮圖（如 800x600），RAW→JPEG 較快（約 5 秒），顯示解碼階段對降尺度有最佳化；但 JPEG→JPEG 的速度差距不如 RAW→JPEG 明顯，指出瓶頸主要在 RAW 解碼。

為兼顧效能與介面回應，作者提出任務排程策略：Canon RAW 解碼應保持單執行緒、高優先權，確保慢工先跑並穩定餵資料；JPEG 編解碼則以多執行緒填滿剩餘 CPU，發揮多核心優勢，同時避免過度並行導致 RAW 任務被稀釋、整體完工時間拉長。由於 .NET 內建 ThreadPool 不支援設定優先權、難以區分不同任務池、且等待完成需要自行處理 WaitHandle，同時也無法避免 RAW Codec 的內部限制，故決定自製 SimpleThreadPool：固定執行緒數、可設優先權、支援多個池並行，並提供簡易的等待完成 API。使用方式刻意貼近內建 ThreadPool，降低導入成本。

測試情境為 125 張 JPEG + 22 張 RAW 混合批次。使用內建 ThreadPool，任務序列化偏向前段 JPEG，CPU 一度 100%，後段 RAW 解碼則降至約 50–60%，總耗時 110 秒；且 UI 預覽常延遲。切換到 SimpleThreadPool，RAW 與 JPEG 強制並行、RAW 稍高優先權，CPU 利用率更平滑且更長時間接近滿載，總耗時降至 90 秒；同時每張完成即時顯示預覽，UI 回應良好。作者指出，得益於適度控制執行緒數量與優先權，才能避免資源爭奪與排程不當，改善整體吞吐與互動體驗。然而從更高層面來看，最佳做法仍是採用函式庫或編譯器層級的平行化（例如 .NET 平行程式庫），其比手工以 ThreadPool 分派任務更智慧與高效，但因仍在社群預覽階段而暫緩採用。

最終，作者完成自製 ThreadPool 與 Metadata 的處理，Image Resizer 已達實用水準，剩餘的歸檔程式待整合影片編碼後即可收尾，預告之後將分享。

## 段落重點
### 動機與目標：重現 Power Toy 的批次縮圖體驗
作者長期愛用 Microsoft 的 Resize Pictures Power Toy，其在 XP 上透過檔案總管右鍵即可批次縮圖，JPEG 品質也足夠。但該工具在 Vista 失效，推測與 GDI+ 向 WPF 過渡有關，因而動念自製一款簡單的 Image Resizer。基於前文已完成的 Canon RAW Codec 與 WPF 整合，估計 WinForms/WPF 快速拉介面即可，但實作後發現效能與多執行緒互動問題遠比預期複雜。

### 問題盤點：效能、多核、ThreadPool、UI 回應
四大問題浮現：一是效能，Canon RAW 解碼極慢，同尺寸轉檔需 60–80 秒；二是多處理器利用不足，雙核僅 50% 多的使用率；三是即使丟入 ThreadPool 並行，RAW Codec 仍卡在約 60% CPU，顯示其內部限制使多執行緒無助；四是 UI 受干擾，JPEG 任務可並行但 ThreadPool 無法調整優先權，導致背景工作爭用資源，進度列雖動但預覽圖常卡住，影響互動體驗。

### 行為觀察：RAW 縮圖較快，瓶頸在解碼
實驗顯示，RAW 直接輸出縮圖（例如 800x600）耗時大幅下降（約 5 秒），而非縮圖時超慢（60 秒）。對照 JPEG→JPEG 的縮圖耗時差距不大，推論 Canon RAW Codec 在 decode 階段對降尺度做了特化；因此若策略上能優先讓 RAW 解碼穩定輸出，再用 JPEG 編解碼填補空檔，整體時間可顯著縮短。

### 設計策略：以排程分流 RAW 與 JPEG
核心策略是讓 RAW 與 JPEG 任務「同時」執行，但以不同資源池與優先權處理：RAW 解碼採單執行緒高優先權，避免平行化反而拖慢個別任務週期；JPEG 任務則用多執行緒攤平剩餘 CPU，於 RAW 空檔高速完成，並避免壓垮 UI。理想排程圖是 RAW 穩定跑、JPEG 穿插填滿運算空檔，最大化 CPU 積分利用率並縮短尾端長拖。

### 自製 SimpleThreadPool：補齊內建缺口
內建 ThreadPool 不支援設定優先權、難以多池隔離、等待完成也繁瑣。作者據此實作 SimpleThreadPool，主張固定執行緒數（避免過度平行）、可設定優先權（CPU bound 工作降低對整體回應的衝擊）、允許多池（RAW 一池 1 執行緒、JPEG 一池 4 執行緒以對應多核）、並提供簡單的 End/Wait API。介面貼近 .NET ThreadPool 的 QueueWorkItem 以降低改動成本，示例程式展現基本用法與行為。

### 實測與對比：110 秒降至 90 秒，UI 同步改善
測試資料為 125 JPEG + 20 G9 RAW + 2 G2 RAW。使用內建 ThreadPool 時，前段 JPEG 擁擠導致 CPU 一度 100%，後段 RAW 解碼限制造成 CPU 僅 50–60%，總耗時 110 秒，且 ImageBox 預覽常延遲。切換到 SimpleThreadPool 後，RAW 與 JPEG 強制併行、RAW 稍高優先權，CPU 更長時間維持高載，總耗時降為 90 秒；每張完成即時顯示預覽，UI 回應顯著改善。結論是適度控制執行緒數與優先權，勝過單純堆疊 ThreadPool 任務。

### 反思與展望：庫與編譯器層平行化更聰明
作者指出，手工排程雖能有效改善，但最佳方案仍是函式庫或編譯器層的平行化工具，能在更細粒度自動化地將迴圈與任務拆解並行，通常比 ThreadPool 任務分派更有效率。文中提到 Intel 的平行化影片與 Microsoft .NET 的平行程式庫（當時仍為社群預覽）作為未來方向。就當前專案而言，ThreadPool 與 Metadata 已完成，Image Resizer 可用，後續只需整合影片編碼以完成歸檔工具，預計再撰文分享。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C#/.NET 基礎與委派/回呼（Thread, ThreadPool, WaitCallback）
   - WPF UI 模型與單執行緒原則（Dispatcher、UI thread 與背景工作互動）
   - 影像處理基礎與編解碼差異（RAW 解碼 vs JPEG 編/解碼）
   - 多核心與效能觀念（CPU-bound vs I/O-bound、CPU 利用率、排程與優先序）

2. 核心概念：
   - 異質工作負載特性：Canon RAW 解碼不易平行化、JPEG 編解碼易平行化
   - UI 響應性與背景工作隔離：避免 ThreadPool 影響 UI thread
   - ThreadPool 限制與自訂池設計：固定執行緒數、可設定優先序、多池並行
   - 工作排程策略：以高優先序處理瓶頸任務，利用剩餘 CPU 給可平行的小任務
   - 效能量測與驗證：CPU 使用率曲線、總運算量（面積）與完成時間的關係

3. 技術依賴：
   - .NET 內建 ThreadPool 與 WaitHandle（可用但難以滿足優先序/多池）
   - 自訂 SimpleThreadPool（固定執行緒數、優先序、QueueWorkItem、Start/End）
   - Canon RAW Codec 與 JPEG Codec（不同可平行性與 CPU 使用型態）
   - WPF 與 Dispatcher（回到 UI thread 更新預覽與進度）

4. 應用場景：
   - 批次影像縮圖工具（RAW→小尺寸 JPEG）
   - 桌面應用的多核心最佳化（混合長任務與短任務）
   - 需維持順暢 UI 的後台批次處理（進度列、縮圖預覽即時更新）
   - 多種編解碼/過濾管線的排程（視訊/影像處理工作分池並行）

### 學習路徑建議
1. 入門者路徑：
   - 了解 CPU-bound 與 UI thread 基本觀念，試用 .NET ThreadPool 跑簡單影像任務
   - 學習 WPF Dispatcher 與在背景工作完成後回主執行緒更新 UI
   - 建立小型批次縮圖範例（僅 JPEG），觀察 CPU 利用率與 UI 響應

2. 進階者路徑：
   - 量測不同編解碼工作負載（RAW vs JPEG）的 CPU 利用率與可平行性
   - 實作自訂 ThreadPool：固定執行緒數、可設定 ThreadPriority、支援多池與等待全部完成
   - 設計排程策略：瓶頸任務高優先序、短任務併行填滿剩餘 CPU

3. 實戰路徑：
   - 在 WPF 批次轉檔工具整合：一池處理 RAW（1 條執行緒，高優先序）、一池處理 JPEG（多執行緒，較低優先序）
   - 增加進度、預覽即時更新、取消/錯誤處理與完成等待
   - 以實測圖表比較不同策略（內建 ThreadPool vs 自訂池）對總時間與 UI 體驗的影響

### 關鍵要點清單
- 異質負載辨識：RAW 解碼難平行、JPEG 易平行，先分清任務特性再排程 (優先級: 高)
- UI thread 保護：避免背景工作壓垮 UI，使用 Dispatcher 回主執行緒更新 (優先級: 高)
- 內建 ThreadPool 侷限：無法設優先序、不易多池管理、等待需靠 WaitHandle (優先級: 高)
- 自訂 ThreadPool 設計：固定執行緒數、可設定 ThreadPriority、支援多池與收斂等待 (優先級: 高)
- 多池策略：RAW 專用單執行緒池（高優先序）+ JPEG 多執行緒池（低優先序） (優先級: 高)
- CPU 利用率思維：總面積等於總運算量，應讓可平行任務填滿瓶頸之外的空檔 (優先級: 高)
- 測試與量測：以任務組合、時間、CPU 曲線驗證策略有效性（110s→90s） (優先級: 中)
- 工作切分粒度：讓短任務（JPEG）充當填充，避免長任務（RAW）獨占造成閒置 (優先級: 中)
- ThreadPriority 應用：瓶頸任務略高優先序，確保整體完成時間最佳化與 UI 即時性 (優先級: 中)
- 固定執行緒數益處：避免過多執行緒上下文切換與資源爭用 (優先級: 中)
- 等待所有工作完成：提供簡化的 End/Wait 介面收斂處理（優於手動 WaitHandle） (優先級: 中)
- WPF 與背景工作：確保影像預覽與進度列流暢更新，不被背景任務飢餓 (優先級: 高)
- 編解碼策略：RAW 直接縮小尺寸輸出更快（解碼階段已優化子取樣） (優先級: 中)
- 擴展與替代：未來可評估 TPL/平行迴圈/管線化，但需考量穩定度與異質負載 (優先級: 低)
- 相容性背景：XP PowerToys 在 Vista 不可用，促成自製工具與架構思考 (優先級: 低)