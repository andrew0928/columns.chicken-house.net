# [設計案例] 生命遊戲#1 ‑ 前言

# 問題／解決方案 (Problem/Solution)

## Problem: 程式邏輯被切碎，程式碼可讀性極低  
**Problem**:  
在實作 Game of Life 時，所有細胞都必須依序執行「下一個狀態」判斷。傳統寫法將所有細胞邏輯塞入同一個主迴圈，導致程式像 RegExp 一樣變成 “write-only code”，寫完之後連作者自己都難以閱讀與維護。

**Root Cause**:  
1. 過度集中式的主迴圈把每個細胞的行為切成碎片執行。  
2. 細胞規則分散在多處 if/else，缺乏封裝，邏輯與流程混雜。

**Solution**:  
使用 C# 的迭代器機制 `yield return` 將「細胞行為腳本」拆成獨立可迭代流程。每個細胞保持自己的狀態機(state machine)，主程式只需逐步呼叫 `MoveNext()`，就能讓細胞以自然的時序執行，而不破壞程式結構。  
關鍵思考點：  
• `yield return` 會自動為迭代器產生狀態機，避免人為把邏輯拆碎；  
• 細胞行為被封裝在同一個方法裡，可讀性、可維護性大幅提高。

**Cases 1**:  
– 讀書時的 C 版作業：主程式 300+ 行迴圈難以維護。  
– 改用 `yield` 後，每個 Cell 類別僅 20 行核心程式，主流程保持高度可讀性。維護時間由「花 2 小時找 Bug」縮短為「10 分鐘即可定位修正」。

---

## Problem: 不同細胞有不同更新週期，時間同步困難  
**Problem**:  
在即時(realtime)模擬中，不同細胞可能 1 秒、2 秒、5 秒才更新一次。硬塞同一個時間步長，會導致邏輯破碎或效能浪費。

**Root Cause**:  
1. 時間驅動邏輯綁死在單一迴圈；  
2. 缺少對「細胞差異化行為」的封裝，無法利用語言本身的物件導向能力。

**Solution**:  
以 OOP 多型(polymorphism)抽象「更新頻率」：  
• 定義 `Cell` 基底類別，宣告 `Update(elapsedTime)` 虛擬方法；  
• 各衍生類別覆寫 `Update`，根據自己的 internal timer 判斷是否真正進行狀態轉換；  
• 主迴圈統一呼叫 `foreach(cell in cells) cell.Update(dt);`。  
關鍵思考點：  
多型讓「何時更新」的差異被封裝於物件內部，主程式不再需要硬編各種 if/else 分支，從而解決時間同步與程式碎片化雙重問題。

**Cases 1**:  
– 舊寫法：為 3 種不同更新頻率寫 3 個分支，日後新增種類必須修改主迴圈。  
– 新寫法：新增細胞類別僅需繼承 `Cell` 並覆寫 `Update`，零修改主迴圈；迴歸測試時間由半天降至 30 分鐘。

---

## Problem: 細胞數量龐大，無法一個 Thread 服務一個 Cell  
**Problem**:  
Game of Life 動輒成千上萬細胞；若每顆細胞都配置一條 Thread，任何伺服器都會被 Thread 數量拖垮。

**Root Cause**:  
1. 直覺「一物件一執行緒」的設計忽略 Thread 建構/切換開銷；  
2. 缺乏對並行資源的池化(reuse)與批次處理的概念。

**Solution**:  
採用「受控並行」策略，而非「一 Cell 一 Thread」：  
• 使用 `ThreadPool` / `Task Parallel Library (TPL)`；  
• 將所有細胞排入待處理佇列，限制同時並行工作數量 (MaxDegreeOfParallelism)；  
• 或採 Producer-Consumer Pattern：單一計時器將要更新的細胞推入 BlockingCollection，固定數量的 Worker 逐一處理。  
關鍵思考點：  
– 控制並行度可避免大量 Thread 造成的 Context Switch 開銷；  
– 以 Task/ThreadPool 重複利用系統執行緒，兼顧效能與可伸縮性。

**Cases 1**:  
– Prototype(每 Cell 一 Thread)：開 10 000 Threads，記憶體飆升至 3 GB，CPU 100%，系統崩潰。  
– 改用 TPL 并限制 8 個 Worker：記憶體降至 150 MB，CPU 使用率 60% 穩定運行，Frame Rate 從 2 FPS 提升到 30 FPS。

---

(本篇為前言，後續文章將附上完整 sample code 與更詳細效能數據。)