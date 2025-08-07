# 微服務基礎建設：斷路器前的「服務負載控制」全攻略

# 問題／解決方案 (Problem/Solution)

## Problem: 微服務沒有流量保護機制，整體系統容易因雪崩效應而全面崩潰

**Problem**:  
在高併發的微服務環境中，某一個服務（例如下單 API）如果突然被大量請求打滿，呼叫端會不斷 Retry，導致其它服務也被拖垮，最後形成「服務雪崩效應」，整個系統停擺。

**Root Cause**:  
1. 缺乏「服務量」(Throughput) 的量化與可觀測指標。  
2. 沒有在「超載之前」就切斷過量要求的機制。  
3. 開發團隊把限流完全視為 infra 工作，缺少在程式碼層自行治理流量的能力。

**Solution**:  
在真正啟用斷路器之前，先引入「服務量管控」(Throttle/Rate-Limit)；藉由程式層面精準定義「單位時間內能受理多少 request」，提前拒絕或緩衝過量流量。核心做法包含四種演算法／實作範本：

1. CounterThrottle (固定時間視窗計數)  
2. StatisticEngineThrottle (滑動視窗計數 ‑ 改良版)  
3. LeakyBucketThrottle (漏桶演算法)  
4. TokenBucketThrottle (令牌桶演算法)

```csharp
public abstract class ThrottleBase {
    protected double _rate_limit = 100;
    protected ThrottleBase(double rate) { _rate_limit = rate; }
    public abstract bool ProcessRequest(int amount, Action exec = null);
}
```

**Cases 1**:  
• 模擬流量 600 RPS + 700 RPS 瞬間尖峰，不加任何 Throttle 時，後端被打爆，Error Rate > 80%，系統雪崩。  
• 加入任一 Throttle 之後，Error Rate 降為 0%~10%，整體系統可持續服務 20 分鐘壓力測試不中斷。

---

## Problem: 固定時間視窗計數 (CounterThrottle) 仍會產生短暫尖峰，無法真正平滑流量

**Problem**:  
CounterThrottle 透過「每 N 秒歸零一次的 Counter」來限流。但在視窗切換瞬間會放行 2 個視窗總量的 Request，產生瞬間 2×RPS 的高峰，依舊可能打爆後端。

**Root Cause**:  
固定視窗有明顯邊界，視窗交界時沒有任何 Overlap，導致突波 (Edge Burst)。

**Solution**:  
改用「滑動視窗統計」(StatisticEngineThrottle)。核心邏輯：  
1. 使用 In-Memory Sliding Window（或分散式 Sliding Window）隨時統計「過去 N 秒」平均 RPS。  
2. 每進來一筆 Request 先查詢 Sliding Window 平均值，若未超標才受理。  

此法將固定視窗「鋸齒狀曲線」變為「較平滑曲線」，突波明顯下降。

```csharp
public override bool ProcessRequest(int amount, Action exec = null) {
    if (_average_engine.AverageResult < _rate_limit) {
        _average_engine.CreateOrders(amount);
        Task.Run(exec);
        return true;
    }
    return false;
}
```

**Cases 1**:  
• rate = 500 RPS、window = 1 秒時，Executed RPS 由 0~1175 大幅波動，改善成 450~550 間小幅波動。  
• Fail Request 下降 35%，Average Execute Time 保持在 0~10 ms 之間。

---

## Problem: 既要平滑流量，又要保證「最大等待時間」，Counter/Sliding Window 仍不足以支撐業務 SLA

**Problem**:  
若後端雖能吃下 500 RPS，但每秒會有短暫 1000 RPS 尖峰；單純 Reject 會浪費可用吞吐，又無法告知前端最長等待時間，難以簽 SLA。

**Root Cause**:  
1. 沒有「緩衝池」吸收尖峰。  
2. 沒有辦法精準預估 Request 最長等待時間。

**Solution**:  
採用「漏桶演算法」(Leaky Bucket)。概念：  
• Request 進入固定大小 Bucket (Queue)。  
• 由後端工作者以固定速率「漏水」處理 Request。  
• Bucket 滿則立即回拒，確保處理佇列長度 ≤ timeWindow × rate。  

關鍵程式片段：

```csharp
// Producer: 嘗試倒水
public override bool ProcessRequest(int amount, Action exec = null) {
    lock(_syncroot){
        if(_current_bucket + amount > _max_bucket) return false;
        _current_bucket += amount;
        _queue.Enqueue((amount, exec));
        return true;
    }
}
// Consumer: 固定速率漏水
double step = _rate_limit * _interval / 1000;   // interval=100ms
```

**Cases 1**:  
• rate = 500 RPS、timeWindow = 5 秒 → Bucket 最大等待時間即 5 秒。AverageExecuteTime 在尖峰期最高 4800-5000 ms，之後回落，符合預期 SLA。  
• Executed RPS 幾乎成為完美水平線 500 RPS，後端 CPU 利用率穩定在 70%-80%，無雪崩。  

---

## Problem: 後端仍有餘力但 Leaky Bucket 固定「漏速」造成吞吐浪費，無法充分利用資源並允許可控 Burst

**Problem**:  
Leaky Bucket 把執行速率鎖死在 _rate_limit，當後端瞬間釋放資源後仍只能以固定速率慢慢處理；且「延遲執行」會一直佔用前端連線。

**Root Cause**:  
缺乏「動態提早配額」的能力，導致後端閒置資源無法即時用於處理新流量。

**Solution**:  
使用「令牌桶演算法」(Token Bucket)。  
• 後端以固定速率向桶子投放 Token，桶子滿後停止投放。  
• Request 進來時先嘗試索取 Token；取到立即處理，取不到才拒絕。  
• 如此既能限制平均速率，又能在「桶子尚有 Token」時瞬間處理 Burst。

```csharp
// 每 100ms 投放 token
double step = _rate_limit * _interval / 1000;
_current_bucket = Math.Min(_max_bucket, _current_bucket + step);

// Request 嘗試消耗 token
if(_current_bucket > amount){
    _current_bucket -= amount;
    Task.Run(exec);
    return true;
}
```

**Cases 1**:  
• rate = 500 RPS、timeWindow = 5 秒 → 每次尖峰可瞬間處理約 2500 Request，Fail Rate 從 18% 降到 5%。  
• Executed RPS 在有 Token 時可瞬間拉高至 900-1000，Token 耗盡後自動降回 500；整體平均 RPS 提升 15%。  
• AverageExecuteTime 幾乎為 0 ms（無排隊），前端連線不被長期佔用。

---

# 結論與延伸

1. 引入 Throttle 是「啟用斷路器前」不可或缺的基礎工程，先量化並控制服務量，才能決定何時真正跳閘。  
2. 四種演算法的選擇對應不同業務場景：  
   • Counter/Sliding Window：簡易配額或計費。  
   • Leaky Bucket：保證最大等待時間，後端保護性高。  
   • Token Bucket：允許短時 Burst、提升資源使用率。  
3. 搭配 Service Discovery、Health Check、Auto Scaling，可進一步做到：  
   • 依執行緒或實例數即時調整 _rate_limit。  
   • 不同 Service Group / VIP 用戶配置不同 Bucket 大小與速率，實現 QoS 與 SLA。  

掌握上述模式後，即使沒有現成 Gateway / Middleware，也能以最少的程式碼量在客戶端或中介層自行完成流量治理，真正落實「微服務的自癒能力」。