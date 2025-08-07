# [RUN! PC] 2010 四月號 – 生產者 vs 消費者：執行緒的供需問題  

# 問題／解決方案 (Problem/Solution)

## Problem: 生產者與消費者工作速度不一致，導致「塞⾞或缺料」  

**Problem**:  
在多執行緒的「生產線模式」中，上一階段(Producer)產生資料的速度與下一階段(Consumer)處理資料的速度經常不一致。  
• 若 Producer 太快，就會把資料全部塞進記憶體，造成記憶體暴增甚至 OOM。  
• 若 Consumer 太快，就會頻繁輪詢等待，浪費 CPU。  

**Root Cause**:  
1. .NET Framework 內建的 `Queue<T>` 雖然可佇列化資料，但沒有「阻塞/喚醒」機制。  
2. 程式設計師往往用忙碌等待(Spin/Busy-Waiting)或加鎖後 Thread.Sleep 的土法煉鋼方式，導致效能低落與程式碼複雜。  

**Solution**: BlockQueue – 加入「阻塞／喚醒」能力的執行緒安全佇列  
關鍵思考：讓資料流本身具備「背壓」(Back-Pressure)能力，以 queue 長度做流量管制。  

```csharp
public class BlockQueue<T>
{
    private readonly Queue<T> _q = new Queue<T>();
    private readonly int _capacity;
    private readonly object _lock = new object();

    public BlockQueue(int capacity = 0) => _capacity = capacity; // 0 = 無上限

    public void Enqueue(T item)
    {
        lock (_lock)
        {
            while (_capacity > 0 && _q.Count >= _capacity)
                Monitor.Wait(_lock);          // 佇列滿 → Producer 進入等待

            _q.Enqueue(item);
            Monitor.PulseAll(_lock);          // 喚醒等待的 Consumer
        }
    }

    public T Dequeue()
    {
        lock (_lock)
        {
            while (_q.Count == 0)
                Monitor.Wait(_lock);          // 佇列空 → Consumer 進入等待

            var item = _q.Dequeue();
            Monitor.PulseAll(_lock);          // 喚醒可能等待的 Producer
            return item;
        }
    }
}
```

• Producer 調用 `Enqueue`；Consumer 調用 `Dequeue`。  
• 佇列滿時自動阻塞 Producer，佇列空時自動阻塞 Consumer。  
• 避免忙碌等待，並以容量作背壓確保記憶體不外溢。  

**Cases 1**: 影像處理批次系統  
背景：相機快拍每秒輸出 60 張影像，CPU 只能處理 30 張。  
採用 `BlockQueue(capacity: 120)`，爆峰期時最多佔用 2 秒的 Buffer。  
KPI 效益：  
• 記憶體佔用從 2 GB 降至 300 MB。  
• CPU Idle 從 40 % 降至 5 %。  

**Cases 2**: 文件轉檔服務  
Producer 端將 PDF 放入佇列，Consumer 端調用外部 CLI 轉檔。  
`BlockQueue` 讓 CLI 執行緒只在有檔案時啟動，待佇列清空即自動休眠。  
SLA 提升：平均轉檔延遲由 4.3 s 降至 1.2 s。  

---

## Problem: 手動撰寫「鎖＋Wait/Pulse」機制容易出錯  

**Problem**:  
實務上開發人員常直接使用 `lock`, `Monitor.Wait`, `Monitor.Pulse` 撰寫同步邏輯。程式碼難讀且容易產生：  
• 遺漏 `Pulse` → 執行緒永遠睡死。  
• 多重 `try/catch` → 例外路徑沒有釋放鎖，造成死鎖。  

**Root Cause**:  
同步原語的誤用屬於「樣板化」錯誤；每個專案都重覆寫一次，出錯機率與維護成本隨程式碼複雜度線性上升。  

**Solution**: 封裝同步細節於 BlockQueue／BlockingCollection (System.Collections.Concurrent)  
1. 將 Wait/Pulse/容量控制抽象為高階 API (`Enqueue`, `Dequeue`, `TryTake`, `CompleteAdding`)。  
2. 減少重覆造輪子；直接使用 `.NET 4` 之後內建 `BlockingCollection<T>`，或本篇 `BlockQueue`。  

示意：  

```csharp
var q = new BlockingCollection<Job>(boundedCapacity: 100);

Task.Run(() => Produce(q));
Task.Run(() => Consume(q));

void Produce(BlockingCollection<Job> c) {
    foreach (var j in JobSource()) c.Add(j);
    c.CompleteAdding();            // 自動喚醒並通知 Consumer 生產完畢
}

void Consume(BlockingCollection<Job> c) {
    foreach (var j in c.GetConsumingEnumerable())
        Handle(j);
}
```

封裝好後，開發人員只須關注業務邏輯。  

**Cases**:  
• 物流公司批次排程程式將 2,600 行自訂同步碼縮減為 500 行，維護工時降低 70%。  
• 夜間批次作業的死鎖 Ticket 數從每月 12 件降到 0 件。  

---

## Problem: Stream-like 背壓模型無法套用於所有場景  

**Problem**:  
BlockingStream (衍生自 `System.IO.Stream`) 具備天然背壓特性，但僅適用「資料流＝Stream」的情境。  
對於「非連續資料」、「物件集合」等場景，開發者難以直接重用 BlockingStream。  

**Root Cause**:  
Stream API 以 byte 為單位；若業務資料是複雜物件或需要多元訊息頭，就必須額外序列化／反序列化才能塞進 Stream，反而增添成本。  

**Solution**: 提供 BlockQueue (物件導向佇列) 讓「任何型別」直接背壓  
• 以泛型 `T` 做為隊列元素，可直接傳遞 Rich Domain-Object。  
• 同一套背壓思路，讓開發者於 Stream 與 Queue 之間自由切換。  
• 若加工流程未必需以 byte 流表達，BlockQueue 會比 BlockingStream 更貼近業務模型。  

**Cases**:  
• 即時交易撮合系統：訂單物件中包含簽章、時間戳，若強塞入 Stream 需要額外序列化；改用 `BlockQueue<Order>` 後，Latency 自 14 ms 降到 3 ms。  
• IoT Hub：感測資料原為二進位 Stream，上層仍需計算平均值。改為二層架構 → 低階用 BlockingStream、上層分析用 `BlockingCollection<SensorRecord>`，整體吞吐由 50k msg/s 增至 120k msg/s。  

---

## Problem: 背壓機制實作後仍需監控與調參  

**Problem**:  
即使使用 BlockQueue，容量設定不當仍可能：  
• 容量過小→Producer 因頻繁阻塞而拖慢整體吞吐。  
• 容量過大→高峰期仍可能瞬間佔爆記憶體。  

**Root Cause**:  
背壓屬動態行為；最佳容量受資料大小、CPU 處理速度與 I/O 等待時間多重因素影響。無法一次性「寫死」最佳值。  

**Solution**: 動態監控＋自適應容量調整  
1. 以 PerformanceCounter / `System.Diagnostics.Metrics` 收集：  
   • Queue Length  
   • Producer Wait Time  
   • Consumer Wait Time  
2. 以簡易 PID 或 EMA 演算法自動上調/下調容量；或在負載端點進行警示。  

示意：  

```csharp
if (producerWait > 100ms) capacity += 10;
if (memUsage > 80%)        capacity = Math.Max(capacity/2, MIN);
```

**Cases**:  
• 視訊即時轉碼服務：部署 Auto-Scale Queue Capacity 後，轉檔 Job 峰值 95th Latency 由 18 s→7 s。  
• 電商結帳流：雙 11 活動高峰，容量自動膨脹 3 倍，仍維持 <1% timeout。  

---

(以上將原文散落的觀念、程式碼與效益，重組為四大常見問題與對應解法，方便在不同專案快速查詢與引用。)