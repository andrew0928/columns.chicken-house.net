# Thread Pipeline – 生產線模式的多執行緒應用

# 問題／解決方案 (Problem/Solution)

## Problem: 具有前後相依關係的大型工作，無法直接以「切成獨立小工作」的方式做多執行緒平行化

**Problem**:  
在批次處理大量照片時，每張圖片必須先轉為縮圖 (*.PNG)，再把所有縮圖壓成單一 ZIP 檔；兩個步驟彼此相依，無法同時進行。若仍然採用「把大量獨立工作丟給 ThreadPool」的水平切割法，第二步驟（壓 ZIP）只能等待第一步驟全部完成才開始，導致多核心 CPU 的效能被浪費。

**Root Cause**:  
1. 傳統 ThreadPool 平行化假設各工作彼此獨立。  
2. 縮圖 → 壓縮的流程有嚴格的先後順序，相依性破壞了「獨立」這個前提。  
3. 單執行緒按序處理會讓 CPU 使用率落在 30% 左右，四核心硬體被閒置。  

**Solution**:  
1. 以「生產線 / Pipeline」思維垂直切割流程：  
   • Stage 1 – 產生縮圖  
   • Stage 2 – 寫入 ZIP  
2. 每個 Stage 由專屬執行緒處理；兩 Stage 之間以 Queue 當輸送帶，PipeWorkItem 當半成品。  
3. 實作重點（摘錄）：  
   ```csharp
   // 半成品
   public class MakeThumbPipeWorkItem : PipeWorkItem {
       public override void Stage1() { /* 縮圖 */ }
       public override void Stage2() { /* 加入 ZIP */ }
   }
   // 生產線
   public class PipeWorkRunner {
       Queue<PipeWorkItem> _stage1_queue = new();
       Queue<PipeWorkItem> _stage2_queue = new();
       ManualResetEvent _notify_stage2 = new(false);
       /* 兩條執行緒：Stage1Runner / Stage2Runner */
   }
   ```
4. Pipeline 能同時讓「上一張圖在縮圖」與「前一張圖加入 ZIP」，兩階段時間重疊，整體作業時間縮短。  

**Cases 1**:  
硬體：Intel Q9300 (4 Core) / Vista x64  
- 單執行緒版本：251.4 sec，CPU util ≒ 27 %  
- Pipeline 版本：163.7 sec，CPU util ≒ 43 %  
→ 效能提升約 1.5 倍。

---

## Problem: Pipeline 中各階段速度不均，造成瓶頸與閒置

**Problem**:  
Stage 2（ZIP 壓縮）遠比 Stage 1（縮圖）快速，結果 Stage 2 經常等待半成品，產線利用率不佳。

**Root Cause**:  
1. Pipeline 效率受「最慢的 Stage」支配。  
2. Stage 1 每處理一張圖約慢 400 ms，Stage 2 執行完後進入 WaitOne() 被迫閒置。  

**Solution**:  
1. 在 Stage 1 加派人手 —— 將原本 1 條縮圖執行緒增加到 2 條 (或使用 ThreadPool，但需控管數量)。  
2. 以 lock 保護共用 Queue，確保 ThreadSafe。  
3. 修改重點：  
   ```csharp
   _stage1_thread1 = new Thread(Stage1Runner);
   _stage1_thread2 = new Thread(Stage1Runner);  // 新增
   _stage2_thread  = new Thread(Stage2Runner);
   ...
   lock(_stage1_queue){ /* dequeue */ }
   lock(_stage2_queue){ /* enqueue */ }
   ```
4. 調整後 Stage 2 幾乎無閒置（Idle ≒ 0–100 ms），CPU 利用率大幅提高。  

**Cases 1**:  
- 調整後總執行時間：98.8 sec  
- CPU util：75 %–78 %  
→ 相較初版 Pipeline 再縮短 40 %，整體約為原單執行緒實作的 2.5 倍效能。

---

## Problem: 階段過度切割或執行緒過多，反而拖慢整體效率

**Problem**:  
為了追求更高並行度，若把流程切成過多 Stage 或在單一 Stage 投入過多執行緒，可能導致啟動/收尾成本飆高與 CPU 競用、Context-Switch 等額外負擔，最後不增反減。

**Root Cause**:  
1. Pipeline 啟動時後段 Stage 必須等待前段產出首批半成品；停工時則相反，前段閒置。Stage 越多，兩端「空窗期」越長。  
2. 執行緒數量超過 CPU 核心，引發排程 & Lock 競爭；效能無法線性成長。  

**Solution**:  
1. 實務上需「負荷試算」以決定 Stage 數與各 Stage 執行緒數：  
   • 觀察各 Stage Idle 時間、CPU 使用率。  
   • 逐步增加/減少執行緒至瓶頸最小化。  
2. 維持「產能平衡」原則：任何 Stage 的處理速率 ≒ 其他 Stage。  
3. 小規模任務不宜切過細；大量長時間任務才值得維持較長的 Pipeline。  

**Cases 1** (概念性):  
- 若切成 100 個 Stage，單批照片處理反而變慢，因為啟動/收尾損耗抵消了 Stage 重疊帶來的好處。  
- 過量 ThreadPool 讓 CPU 100 % 滿載但上下文切換劇增，Stage 之間依舊塞車。  

---