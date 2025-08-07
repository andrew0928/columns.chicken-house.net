```markdown
# 微服務基礎建設 ─ 線上購物排隊機制設計

# 問題／解決方案 (Problem/Solution)

## Problem: 高流量衝擊下，結帳服務瞬間被大量請求壓垮  

**Problem**:  
雙十一等促銷檔期，大量買家同時點擊「結帳」。後端在進行庫存、優惠、運費等複雜運算時 CPU / Memory / DB 都被塞爆，交易失敗、系統崩潰、使用者體驗極差。

**Root Cause**:  
沒有「流量入口控管」，所有 Request 直接打到結帳服務，遠超過服務可同時處理的 TPS 與系統資源上限。

**Solution**:  
1. 於最前端引入「排隊機制」，先限制同時間能進入結帳的使用者數 (checkoutWindowSize)。  
2. 其餘請求依序排隊 (queueWindowSize)。  
3. 以 4 個整數指標維持佇列狀態 (CurrentSeed, FirstCheckOutPosition, LastCheckOutPosition, LastQueuePosition)，所有動作皆為 O(1)。  
4. C# `CheckoutLine` 範例：  
   ```csharp
   public class CheckoutLine {
       public bool TryGetToken(ref long token);   // 取號
       public bool CanCheckout(long token);       // 是否輪到進場
       public void Remove(long token);            // 完成或放棄
       public void Recycle();                     // 清理失聯使用者
   }
   ```  
   透過 `TryGetToken → CanCheckout → Remove` 完成「入場->結帳->離開」完整流程，確保任何時刻同時進場人數 ≤ checkoutWindowSize。

**Cases 1**:  
• 2022 雙十一併發尖峰：後端結帳窗數設 500，系統觀測到「結帳中人數」穩定維持 400–480 (≈95% 利用率)，TPS 與服務 CPU 均保持穩定，無雪崩。  

**Cases 2**:  
• POC 模擬 10 k 併發使用者：經 Queue 控制後，後端僅需 500 條執行緒即可撐住高峰，避免傳統做法動輒數千條 thread 與 VM 資源。  



## Problem: 排隊狀態查詢造成 Storage IOPS 與成本爆炸  

**Problem**:  
大量排隊用戶每秒輪詢「我排第幾？」舊系統每查一次就掃描整個佇列，DB / Redis IOPS 飆高，雲端計費失控。

**Root Cause**:  
演算法以「搜尋整條隊伍」來計算順位，單次查詢 O(n)，當 N 位用戶每秒輪詢 → 總複雜度 O(n²)。

**Solution**:  
1. 排隊順位改為簡單減法：`token - LastCheckOutPosition`。  
2. 每筆查詢只讀取 4 個指標，完全 O(1)。  
3. 大部分指標寫入頻度低，可全部放入 In-Memory Cache，必要時再同步 DB。  

**Cases 1**:  
• 線上系統改版後，排隊查詢 IOPS 降 90%+，資料庫從 10 k IOPS 降到 <1 k IOPS，可降級儲存方案節省 60% 成本。  

**Cases 2**:  
• 模擬 300 人排隊、每人 1s 輪詢，CPU/IO 幾乎為常數時間；舊算法則隨人數二次成長。  



## Problem: 使用者中途離線／放棄，佔位造成座位浪費  

**Problem**:  
有些買家關閉瀏覽器或久候後離開，但系統仍保留其座位，導致後方用戶遲遲進不了結帳，整體吞吐下降。

**Root Cause**:  
Queue 缺乏「失聯檢測機制」，無法自動回收 Zombie Token。

**Solution**:  
1. 每張 Token 紀錄 `LastCheckTime`。  
2. 週期性 `Recycle()` Worker：若 `Now-LastCheckTime > Timeout` 則呼叫 `Remove()` 剔除。  
3. API 亦供維運手動 `Remove(token)` 立即踢人。

**Cases 1**:  
• 買家隨機 10% 忽然關閉瀏覽器，Recycle 週期 1s，Queue 長度仍穩定，不再因「掛線用戶」外溢至排隊極限。  

**Cases 2**:  
• 風控發現可疑帳號，維運 UI 直接按一下「Kick」，Token 即被移除，後方用戶秒進場，營運效率提升。  



## Problem: 維運端缺乏即時監控與動態參數調整能力  

**Problem**:  
Ops 需要即時看到「排隊人數、結帳人數、流失率」並隨時調大/調小窗口，但原系統無指標，決策盲飛。

**Root Cause**:  
開發階段未納入 DevOps 思維，Metrics 定義與收集缺席，導致上線後才臨時補監控。

**Solution**:  
1. 在 POC 即內建 Metrics：  
   * _queuing_count, _checking_count, _success_count  
   * _abort_queue_count, _abort_checkin_count, _no_entry_count  
   * 四大指標 CurrentSeed / FirstCheckOut / LastCheckOut / LastQueue  
2. 每 100–300 ms 以 CSV 輸出，可匯入 Excel / Grafana 做即時 Dashboard。  
3. 佇列大小與 Timeout 參數可熱調整，立即觀察圖表回饋。  

**Cases 1**:  
• Dashboard 顯示 Checkout 佔用率低於 80%，Ops 立刻把 checkoutWindowSize 從 500 調到 600，TPS 即時提升 15%。  

**Cases 2**:  
• 圖表發現 _abort_queue_count 異常升高，行銷即時推送補償券，有效降低棄單率。  

```