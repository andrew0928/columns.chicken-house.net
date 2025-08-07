# 微服務架構設計 ─ 資料庫的選擇：RDBMS or NoSQL?

# 問題／解決方案 (Problem/Solution)

## Problem: 微服務化後，團隊無法判斷應該選 RDBMS 還是 NoSQL

**Problem**:  
團隊在將單體系統拆分成微服務後，發現「該用 RDBMS 還是 NoSQL？」成為最常被問、卻最難回答的問題。技術選型的遲疑直接導致專案卡關：  
• 架構審查無法定案  
• 開發排程延宕  
• 難以說服業務端此決策能支撐預期的流量成長

**Root Cause**:  
1. 欠缺「資料治理」視角，只把問題簡化成二選一。  
2. 對資料結構、交易模型、服務邊界、整合策略缺乏整體規劃，導致無法把商業需求映射到技術選型。  
3. 不理解兩種資料庫的核心強項：  
   • RDBMS – Index/Join/ACID，適合結構化關聯資料；  
   • NoSQL – Key-Value、文件導向、水平切分，適合巨量物件與彈性 Schema。

**Solution**:  
以「問題導向」與「整合導向」的思路重構決策流程：  
1. 先盤點最棘手的業務場景（高併發、巨量歷史資料、版本管理…）。  
2. 將資料問題拆分成四大面向：  
   • 資料一致性與交易處理  
   • 舊資料封存  
   • 異動紀錄／快照  
   • Cache 正確性  
3. 針對不同面向各自挑選最擅長的技術：可同時併用 RDBMS + NoSQL，再以程式碼層面的 Saga / CQRS / Event 進行同步。  
4. 最終只在「同質資料庫」裡做品牌/成本比較，而非在 RDBMS 與 NoSQL 間強行二選一。

**Cases 1**:  
• 旅遊電商平台：核心訂單交易仍置於 PostgreSQL，使用 Kafka＋MongoDB 做訂單快照與搜尋。  
• 成效：在高峰期 (5k req/s) 資料仍可於 200 ms 內回應，RDBMS TPS 僅原來 60%。

---

## Problem: 資料一致性與分散式交易

**Problem**:  
服務切庫後，一筆跨服務流程（下單 → 扣庫存 → 刷卡）不再落於單一資料庫，Two-Phase Commit 不可行，如何確保「最終一致」？

**Root Cause**:  
• 原有 ACID 交易依賴單體 RDBMS。  
• 微服務拆分後，交易被拆成多個本地交易，需要協調機制。  
• 若無妥善補償機制，任何一步失敗都會造成資料不一致或人工作業回補。

**Solution**:  
1. 採 Saga Pattern：  
   - 本地交易成功後送出 `OrderCreated` 事件  
   - 其他服務（庫存、請款）各自完成本地交易，再分別送出 `OrderCompleted` / `OrderFailed`  
   - 若失敗則發布補償事件 (`RollbackInventory` …)。  
2. 讀寫分離（CQRS）：  
   - Command 端保留關鍵交易於 RDBMS  
   - Query 端透過事件轉拋至 NoSQL / Search Engine 供高併發查詢。  
3. 事件匯流排 (Kafka／RabbitMQ) 負責保證順序與重撥 (Replay)。

```csharp
// 範例：下單 Service 的本地交易 + 事件發布
using (var tx = db.BeginTransaction()) {
    db.Orders.Add(order);
    db.SaveChanges();
    tx.Commit();
}
await eventBus.PublishAsync(new OrderCreated(order.Id, order.Total));
```

**Cases 1**:  
• FinTech 錢包系統導入 Saga 後，跨三服務交易失敗率由 0.4% 降至 0.02%，且全自動補償，無須人工對帳。  

---

## Problem: 舊資料封存（Archive Mass Data）

**Problem**:  
RDBMS 隨時間累積數億筆歷史交易，索引膨脹、日常查詢明顯變慢，備份視窗超過營運允許時間。

**Root Cause**:  
• 將「查詢熱度已低」的資料仍同置於熱表。  
• RDBMS B-Tree index 需維持 `O(log n)` 搜尋，n 過大導致效能衰退。  
• 缺乏分層儲存策略。

**Solution**:  
1. 熱／冷資料切分策略：  
   - 最近一年資料留在 RDBMS（熱）  
   - 舊資料用批次 Job 搬遷至 NoSQL / 物件儲存（冷）  
2. 查詢閘道：API 先查熱表，若 miss 再查冷層。  
3. 使用 Partition Table 或分庫分表降低單表大小。  

```bash
# 範例：以 Airflow 批次遷移
python migrate_old_order.py --from 2022-01-01 --to 2022-06-30
```

**Cases 1**:  
• 遊戲營運平台：封存後 MySQL 單表由 2 TB 降至 200 GB，日常報表查詢由 8 min → 35 sec。  

---

## Problem: 異動紀錄與快照管理（Multi-Version）

**Problem**:  
需要保存「商品資料」每一次變更，並能回溯任意時間點；傳統做法在 RDBMS 以 History Table + Join，維運複雜且查詢慢。

**Root Cause**:  
• 關聯式設計天生優化「最新狀態」，對「時間軸」查詢不友善。  
• 若用 Trigger 寫 History Table，Join 筆數爆炸。  

**Solution**:  
1. 使用「Copy-On-Write + RefCount」模型，類似 Git：  
   - 每次修改建立新 Document，舊版本僅存差異指標 (delta)。  
2. 採文件型 NoSQL (MongoDB / DynamoDB)：  
   - 以 `ProductId + Version` 當複合 Key，可 `O(1)` 直取任意版。  
3. 報表或比較需求，批次 Job 預先展開至 OLAP（BigQuery, Redshift）。

**Cases 1**:  
• SaaS CMS：多版本商品頁面查詢平均 15 ms，以往 RDBMS Join 需 300 ms；月儲存成本減 35%。  

---

## Problem: Cache 命中率與資料正確性的平衡（Immutable Data Pattern）

**Problem**:  
高流量 API 依賴 Redis 佔存，惟更新頻繁，導致 Cache 常被淘汰或髒讀；命中率僅 60%。

**Root Cause**:  
• Key 與資料狀態耦合；資料一改 Key 就失效。  
• 無法同時保證「高命中」與「最新狀態」。  

**Solution**:  
1. 將關鍵資料設計為 Immutable：  
   - 主 Key 永不變，內容若需修改就生成新版本並回寫。  
2. Cache 存放 Immutable Document，Cache Invalidate 僅針對「版本指標」(pointer)。  
3. 讀取流程：  
   - 先抓 `LatestPointer:{Id}` → 取得版本號  
   - 再抓 `Entity:{Id}:{Version}`  
   - 更新時僅刷新 Pointer，舊版本可緩存至 TTL 到期，提高命中率。  

```pseudo
GET LatestPointer:123   # ➜ v42
GET Product:123:v42     # immutable
```

**Cases 1**:  
• 影音串流服務導入 Immutable Cache 後，Redis 命中率由 60% 升至 92%，回源 (miss) QPS 降 70%，同時保證播放列表不出現髒資料。  

---

