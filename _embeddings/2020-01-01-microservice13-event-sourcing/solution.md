# 微服務架構設計 ‑ Event Sourcing

# 問題／解決方案 (Problem/Solution)

## Problem: 無法回溯與修正錯誤資料，導致帳務或領域狀態無法被正確重建

**Problem**:  
在金融或高稽核需求的場域（如銀行帳戶、保單、醫療紀錄），若日後發現計價或業務規則錯誤，需要將「過去所有異動」重新計算，但傳統 CRUD 系統只保留最新狀態，難以回溯任何時間點的正確餘額或狀態。

**Root Cause**:  
1. 資料僅保存最終結果，導致歷史細節遺失。  
2. Log 與正式資料分離，Log 雖可查閱、卻缺乏可程式化重播能力。  
3. 更新（Update）操作覆寫舊值，使修正演算法或政策時需人工作業，風險與成本極高。

**Solution**:  
採用 Event Sourcing + CQRS。  
• Domain Command → 產生不可變 Event → 只做 Append，保留完整時序。  
• 使用 `EventStore`(NoSQL/KV) 保存事件，重建 Aggregate 時用「事件重播」。  
• Query 端以 Projection 轉成讀模型（Materialized View）。  
關鍵思考：事件成為「唯一真相 (Single Source of Truth)」，任何時間點皆可 `Replay(events, asOf)` 取得正確狀態，修正利息或商業規則只需「補一顆更正事件」而非異動歷史。

```csharp
// Sample – 追加利息更正事件
public class InterestAdjusted : IEvent
{
    public Guid AccountId {get; init;}
    public decimal Delta {get; init;}   // + / - 差額
    public DateTime TxnTime {get; init;}
}

_eventBus.Publish(new InterestAdjusted {
    AccountId = id, Delta = diff, TxnTime = now
});
```

**Cases 1**:  
銀行帳務平台將 12 個月利率算法錯誤，切換 Event Sourcing 後：  
• 僅撰寫「InterestAdjusted」事件重播，全行 600 萬帳戶 4 小時完成補差；  
• 程式碼無需 `UPDATE Balance SET…`，避免鎖表與人工介入，稽核一次通過。

**Cases 2**:  
保險公司理賠計價錯誤，透過歷史事件重播，30 年保單資料重算成功率 100%，比傳統手工調帳流程縮短 3 週 → 2 天。

---

## Problem: 傳統資料庫 Join 架構遇到雲端規模時，效能與可擴充性急遽下滑

**Problem**:  
線上服務從單機 DB 演變到 PB 級資料量，多維度查詢與分析時，Join + Index 仍發生效能瓶頸，難以橫向擴充；單點故障率亦隨節點數量爆增而上升。

**Root Cause**:  
1. 「運算集中」模型：把資料搬到少數 DB 伺服器計算，I/O 掛瓶頸。  
2. 依賴高階硬體 (RAID/Storage) 來提升可靠度，雲端大規模下硬體故障變常態。  
3. 關聯式正規化過度聚焦一致性，削弱水平擴充能力 (Scale-out)。

**Solution**:  
導入 Cloud Native 架構：  
a. 資料寫入即轉為 Event → Streaming → 多份 Projection (KV/Column/Graph)。  
b. 查詢端僅做 Key/Value 查找，時間複雜度 O(1)。  
c. Storage 三副本 + 自我修復 (如 BigTable / Cassandra)，容忍節點故障。  
d. Deployment 採 K8s + Service Discovery，服務天然容錯。

```text
Write Flow
Command -> EventBus -> EventStore (Append) -> StreamProcessor ->
   -> KV Projection
   -> Analytics Projection
Query Flow
API -> KV Store (Get by Key) => O(1)
```

**Cases 1**:  
廣告平台原每日 ETL 需 9 小時；改成 Event Streaming + Lambda Projection 後，單筆處理 < 100ms，批量報表從「隔夜」縮到「T+15 分鐘」，節點可水平擴充至 500+。

**Cases 2**:  
IoT 企業解析 3,000 萬條/秒感測資料，傳統 RDB cluster 垮機；切換 K8s + Kafka + Event Sourcing，集群故障自動漂移，SLA 由 99.5% 提升到 99.99%。

---

## Problem: 即時報表需求與資料延遲（校正回歸）衝突，造成決策錯誤或輿論質疑

**Problem**:  
業務線上交易可秒級進帳，實體通路／檢體檢驗等則延遲數小時到數天。決策者與大眾要求「即時數字」，導致報表先行發布、後續再大幅修正，引發混亂（#校正回歸）。

**Root Cause**:  
1. 收集流程（人工作業、盤點、化驗）無法即時數位化。  
2. 系統僅提供單一視角的「即時累加」，缺乏延遲資料補繳機制。  
3. 未設定資料延遲 SLA 與關帳策略，導致修正流程臨時拼湊。

**Solution**:  
• 事件流 (Event Sourcing) 紀錄「發生時間」與「收到時間」。  
• CQRS 為不同關注點建立多重 View：  
  ‑ Realtime View：只顯示已到達事件。  
  ‑ Daily Consolidated View：T+1 聚合（延遲可修正）。  
  ‑ Adjustment Alert：若事件超過 SLA 仍未到，觸發通知並進例外流程。  
• 以 Sliding-Window Projection 重算統計，並用 `Version` 或 `Revision` 標示報表。

```pseudo
if (now - event.OccurredAt > MAX_DELAY)
    Notify("DelayedEvent", event.Id);
projectionRealtime.Apply(event);          // 不回填
projectionDaily.Replay(date = event.OccurredAt.Date); // 回填重算
```

**Cases 1**:  
連鎖零售：線上即時＋門市 D+1 上傳  
• 實施後日營收初報正確率 65%→98%，最終營收關帳時間固定 D+3。  
• 管理層可同時查看「當日速報」與「最終確認」，避免錯誤採購決策。

**Cases 2**:  
COVID 篩檢後送系統：  
• 每日 14:00 公布速報，並於 48hr 內自動回填正確日期。  
• 社群輿情從大量質疑下降，公信力指標 (Survey NPS) +21。

---

## Problem: 微服務之間跨域交易需保持資料一致，兩段式提交 (2PC) 不可行

**Problem**:  
訂單服務、付款服務、庫存服務彼此獨立，整體流程須確保「要嘛全部成功，要嘛全部回滾」。傳統分散式交易 (2PC) 因鎖資源、效能低與跨語言限制，在 Cloud/K8s 環境難以落地。

**Root Cause**:  
1. Microservice 天然去中心化，無共享資料庫，2PC 需協調器造成耦合。  
2. 雲端網路延遲＋節點易彈性擴張，鎖定外部資源常 timeout。  
3. 失敗補償流程若散落於各服務，易出現「部分完成」的骯髒資料。

**Solution**:  
採 SAGA Pattern + Event Sourcing。  
• 每個 Local Transaction 完成後發出事件 (e.g., `PaymentCompleted`)。  
• SAGA 協調器 (Orchestrator) 監聽事件並觸發下一步 Command。  
• 若任何步驟失敗，發布補償命令 (e.g., `CancelShipment`, `RefundPayment`)。  
• 使用事件儲存 + Outbox Pattern 保證「事件與本地更新」同原子性。

```csharp
// Order Service
public async Task PlaceOrder(...)
{
   using var tx = _db.BeginTransaction();
   _db.Insert(order);
   _outbox.Add(new OrderPlaced(order.Id));
   tx.Commit();          // CR + Outbox 同步
}

// Payment Saga – Orchestrator
Subscribe<OrderPlaced>(msg => Execute(new PayCommand(msg.OrderId)));
Subscribe<PaymentFailed>(msg => Execute(new CancelOrder(msg.OrderId)));
```

**Cases 1**:  
電商平台全年 4,500 萬筆交易：  
• 以前 2PC 故障復原需 1~2 小時人工對帳；  
• 改用 SAGA + Event Sourcing，平均補償時間 < 5 秒，交易成功率 99.997%。

**Cases 2**:  
食品外送服務：流量尖峰 10 倍，透過事件重播自動補發失敗券，客服抱怨量降低 70%，系統擴容不再受全域鎖定影響。

---

