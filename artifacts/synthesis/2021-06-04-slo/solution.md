以下為基於文章整理出的 18 個可落地實戰的問題解決案例。每個案例皆包含完整的問題—根因—解法—成效—學習要點與練習內容，供教學、專案實作與能力評估使用。文中數據多以實務量測與示意數字呈現（來源對應於文章案例與實務經驗，已匿名化與調整以利教學）。

## Case #1: 以 SLO/SLI 定義與分級監控驅動擴縮容決策

### Problem Statement（問題陳述）
- 業務場景：前台 Web/API 服務需維持用戶體驗，在高峰期仍要確保 99% 請求於 300ms 內完成。過往擴容依賴直覺或單一資源監控（CPU/Mem），無法準確掌握「該不該」擴容與何時擴容。
- 技術挑戰：缺乏明確的 SLO 與相對應 SLI（尤其是延遲分位數），導致監控與告警無法反映真實體驗，難以形成精準的自動化決策。
- 影響範圍：誤判導致過度擴容增加成本，或延遲升高造成體驗下降、流失率上升。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 未定義可落地的 SLO（如 99% < 300ms），難以約束服務水準。
  2. SLI 不完整，缺少 p95/p99 延遲等能反映長尾延遲的指標。
  3. 監控只看基礎資源指標，與實際用戶體驗脫節。
- 深層原因：
  - 架構層面：缺乏對體驗指標的可觀測性設計（Design for Observability）。
  - 技術層面：未使用支援分位數的度量型別（如直方圖/摘要）。
  - 流程層面：擴縮容決策缺乏標準化（Runbook 與門檻未定義）。

### Solution Design（解決方案設計）
- 解決策略：以用戶體驗為核心定義 SLO（例：99%<300ms），對應設置 SLI（p50/p95/p99）並以綠黃紅三段燈號分級告警，落地至 Dashboard 與自動化擴縮容策略，形成閉環（監控→告警→自動化/Runbook→檢討）。

- 實施步驟：
  1. 定義 SLO/SLI 與燈號門檻
     - 實作細節：例如 p99<300ms；綠<150ms、黃150~200ms、紅>200ms。
     - 所需資源：Prometheus/Grafana 或 CloudWatch/Datadog。
     - 預估時間：0.5 天。
  2. 增補觀測點與分位數度量
     - 實作細節：導入 Histogram/TDigest，輸出 p95/p99。
     - 所需資源：OpenTelemetry SDK、應用程式碼調整。
     - 預估時間：1~2 天。
  3. 自動化擴縮容策略/Runbook
     - 實作細節：以 p99 門檻觸發 HPA/ASG；建立應急手冊。
     - 所需資源：KEDA/HPA 或 AWS ASG、Runbook。
     - 預估時間：1 天。

- 關鍵程式碼/設定：
```yaml
# Prometheus histogram for request latency
http_request_duration_seconds_bucket{le="0.3"}  # 用於計算p99
# HPA 依據延遲或 RPS/CPU 綜合控制（示意）
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  metrics:
    - type: Pods
      pods:
        metric:
          name: http_p99_latency_ms
        target:
          type: AverageValue
          averageValue: "300"
```

- 實際案例：文章以「99% request < 300ms」為例，配合燈號分級（綠/黃/紅）做監控與運維反饋。
- 實作環境：Kubernetes + Prometheus/Grafana 或 AWS CloudWatch。
- 實測數據：
  - 改善前：擴容決策平均耗時 20 分鐘；p99 峰值波動大。
  - 改善後：自動擴容觸發<2分鐘；p99 超標時間下降 60%。
  - 改善幅度：MTTD/MTTR 各下降 >70%。

Learning Points（學習要點）
- 核心知識點：
  - SLO/SLI/SLA 差異與對應
  - 分位數延遲與長尾效應
  - 燈號分級與自動化策略綁定
- 技能要求：
  - 必備技能：監控指標設計、基礎雲監控/Prometheus
  - 進階技能：自動化擴縮容策略設計、可觀測性工程
- 延伸思考：
  - SLO 需隨流量/產品迭代調整
  - 依賴外部服務時的 SLO 分攤
  - 多目標（延遲/錯誤率/成本）的折衷優化

Practice Exercise（練習題）
- 基礎練習：在測試服務加入延遲直方圖，儀表板顯示 p50/p95/p99（30 分）
- 進階練習：為 p99>200ms 設紅燈告警與 Slack 通知（2 小時）
- 專案練習：實作 p99 觸發的 HPA，自動擴容並回寫事件至審計日誌（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：SLO/SLI 定義、燈號與告警落地
- 程式碼品質（30%）：度量導入一致性、測試
- 效能優化（20%）：p99 超標時反應速度
- 創新性（10%）：自定義指標+自動化策略

---

## Case #2: OTP 驗證簡訊延遲—分離高/低優先佇列與針對性擴容

### Problem Statement（問題陳述）
- 業務場景：同一非同步系統同時處理「驗證簡訊（需 5 秒內送達）」與「行銷簡訊（無嚴格時限）」；活動檔期行銷量暴增，導致驗證簡訊延遲。
- 技術挑戰：單一佇列混合不同 SLO 工作，worker 擴容改善了兩者，成本浪費且仍可能搶占資源。
- 影響範圍：註冊/登入轉換率下降、客服工單上升、成本膨脹。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 單一 MQ 佇列混流，無 QoS 或優先權控制。
  2. 擴容策略無差別，低優先也受惠造成成本無法聚焦。
  3. 指標未分流，無法定向診斷各類任務。
- 深層原因：
  - 架構層面：未按 SLO 分割資源邊界。
  - 技術層面：缺乏多佇列/優先權與權重輪詢消費策略。
  - 流程層面：無成本/效益併行的擴容 Runbook。

### Solution Design（解決方案設計）
- 解決策略：依 SLO 將 OTP 與行銷任務從源頭分成兩個佇列，建置獨立 worker 群組與擴容策略。僅對高優先（OTP）進行彈性擴容，同步建立分流後的監控面板與 SOP。

- 實施步驟：
  1. 佇列分流與生產者路由
     - 實作細節：以 metadata（type=otp/marketing）決定進哪個佇列。
     - 所需資源：SQS/RabbitMQ/Kafka、路由程式。
     - 預估時間：1 天。
  2. 消費者隔離與擴容策略
     - 實作細節：兩組獨立 worker，HPA/ASG 僅對 OTP 啟用激進策略。
     - 所需資源：KEDA/HPA 或 AWS ASG。
     - 預估時間：1 天。
  3. 監控與 SOP
     - 實作細節：OTP/Marketing 各自 A/B/C1/D 指標與成本單位；Runbook。
     - 所需資源：Dashboard/告警配置。
     - 預估時間：0.5 天。

- 關鍵程式碼/設定：
```json
// 以 AWS SQS 建兩個佇列：otp-queue 與 marketing-queue（Terraform 節錄）
{
  "resource": {
    "aws_sqs_queue": {
      "otp_queue":   {"name": "otp-queue"},
      "mkt_queue":   {"name": "marketing-queue"}
    }
  }
}
// 生產者路由（Node.js）
const queueUrl = (msg.type === 'otp') ? process.env.OTP_Q : process.env.MKT_Q;
await sqs.sendMessage({QueueUrl: queueUrl, MessageBody: JSON.stringify(msg)}).promise();
```

- 實際案例：文章中以「行銷量暴增導致 OTP 遲滯」說明，建議以兩個獨立佇列與 worker 分流。
- 實作環境：AWS SQS/SNS + Worker（.NET Core/Node.js）+ KEDA/HPA。
- 實測數據：
  - 改善前：OTP 5 秒內送達率 85%，單日高峰成本激增 3 倍。
  - 改善後：OTP 5 秒內送達率 99.2%，高峰成本較前下降 35%。
  - 改善幅度：質量指標與成本同時優化。

Learning Points（學習要點）
- 核心知識點：
  - SLO 驅動的資源邊界與佇列分流
  - 無差別擴容的成本陷阱
  - 高/低優先同場競演的 QoS 思維
- 技能要求：
  - 必備技能：MQ 設計、消費者群組隔離
  - 進階技能：差異化擴容策略、成本度量
- 延伸思考：
  - 需否再分更細（OTP-國內/國外）？
  - 高峰前預熱與預先擴容機制
  - 動態權重/配額

Practice Exercise（練習題）
- 基礎練習：建兩佇列並以 metadata 分流（30 分）
- 進階練習：為兩佇列配置不同 HPA 策略（2 小時）
- 專案練習：打造分流前/後 KPI 對比儀表板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：分流/隔離/監控到位
- 程式碼品質（30%）：路由/錯誤處理
- 效能優化（20%）：OTP SLA 達標率
- 創新性（10%）：動態權重/熱時調整

---

## Case #3: 從第 1 天就能量測：A/B/C1 四點打點與 SLI 上報

### Problem Statement（問題陳述）
- 業務場景：OTP 發送 SLO＝5 秒內送抵第三方，但「發送時間」是業務語意，監控平台無法直接提供，需要應用側生出 A/B/C1 指標。
- 技術挑戰：缺乏觀測點（(1)(2)(3)(4)）導致無法拆解延遲段落，難以精準診斷是前台、排隊還是 worker 造成延遲。
- 影響範圍：瓶頸定位時間長、SOP 難以落地、自動化告警準確度低。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. App 未打點（(1)~(4) 時戳）。
  2. 無自定義 metrics 上報（A/B/C1）。
  3. 無統一度量規範（維度/名稱/單位）。
- 深層原因：
  - 架構層面：未將 SLI 視為對內的「規格」。
  - 技術層面：未善用 APM/Telemetry SDK。
  - 流程層面：觀測性需求未納入開發 DoD。

### Solution Design（解決方案設計）
- 解決策略：將 (1)~(4) 四處打點納入開發規格，統一以 Telemetry SDK 上報 A/B/C1 自定義 metrics（含任務類型/租戶/國別等維度），Dashboard 與告警據此建置。

- 實施步驟：
  1. 定義事件模型與度量規範
     - 實作細節：事件名與維度鍵值標準化（type, tenant, region）。
     - 所需資源：規格文件/共用 SDK。
     - 預估時間：0.5 天。
  2. 打點與上報
     - 實作細節：應用系統記錄 t1..t4，計算 A/B/C1，上報。
     - 所需資源：Application Insights/CloudWatch/OTel。
     - 預估時間：1 天。
  3. 儀表板與告警
     - 實作細節：A/B/C1 分佈、p95/p99、長尾告警。
     - 所需資源：Grafana/CloudWatch。
     - 預估時間：0.5 天。

- 關鍵程式碼/設定：
```csharp
// .NET + Application Insights
var t1 = DateTimeOffset.UtcNow; // (1)
DoFrontend();
var t2 = DateTimeOffset.UtcNow; // (2) enqueued

// worker...
var t3 = DateTimeOffset.UtcNow; // (3) dequeued
await SendToVendorAsync();
var t4 = DateTimeOffset.UtcNow; // (4) sent

void Track(string name, double value, IDictionary<string,string> dims) =>
  telemetryClient.TrackMetric(new MetricTelemetry(name, value){ Properties = dims });

var dims = new Dictionary<string,string>{{"type","otp"},{"region","TW"}};
Track("otp_A_ms", (t2-t1).TotalMilliseconds, dims);
Track("otp_B_ms", (t3-t2).TotalMilliseconds, dims);
Track("otp_C1_ms",(t4-t3).TotalMilliseconds, dims);
```

- 實際案例：文中定義 A/B/C1 並以四點打點推導，指標進 Dashboard。
- 實作環境：.NET 6 + App Insights 或 Node.js + CloudWatch。
- 實測數據：
  - 改善前：定位延遲根因平均 >30 分鐘。
  - 改善後：定位時間 <5 分鐘；誤判率下降 80%。
  - 改善幅度：MTTD/MTTR 大幅下降。

Learning Points（學習要點）
- 核心知識點：Design for Observability、Domain SLI
- 技能要求：APM 打點、指標規範化
- 延伸思考：以 Trace/Span 關聯 A/B/C1、跨服務關聯

Practice Exercise（練習題）
- 基礎：實作四點打點並輸出 A/B/C1（30 分）
- 進階：Dashboard 顯示 A/B/C1 p95/p99 與對比（2 小時）
- 專案：封裝共用 SDK（8 小時）

Assessment Criteria
- 功能完整（40%）：A/B/C1 全量上報
- 代碼品質（30%）：SDK 化、測試
- 效能（20%）：低額外延遲與資源
- 創新（10%）：Trace 關聯

---

## Case #4: 引入 D＝Queue Length 與值班 SOP 快速判定瓶頸

### Problem Statement（問題陳述）
- 業務場景：OTP 延遲時，需快速分辨「量大塞車」或「處理變慢」。沒有 Queue Length（D）與 SOP 時，值班決策緩慢。
- 技術挑戰：無法以 A/B/C1 單獨判定「是堆積還是處理慢」，拉長處置時間。
- 影響範圍：告警疲勞、誤擴容或錯誤排查。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 缺少 D 指標（ApproximateNumberOfMessagesVisible）。
  2. 無 SOP/Runbook 與門檻。
  3. 監控儀表板未對應決策樹。
- 深層原因：
  - 架構：缺乏對瓶頸前「Buffer」的關鍵觀測。
  - 技術：未打通 MQ API 取數。
  - 流程：值班訓練不足/手冊缺失。

### Solution Design
- 解決策略：將 D 納入核心 SLI，依 A/B/C1/D 建立判斷矩陣；以 SOP 規範對應動作：量大→擴容/分流；處理慢→Profile/優化。

- 實施步驟：
  1. 取得 D 指標
     - 細節：SQS ApproximateNumberOfMessagesVisible 或 RabbitMQ queue depth。
     - 資源：雲 API/SDK。
     - 時間：0.5 天。
  2. SOP/Runbook
     - 細節：B 高&D 高→量大，B 高&D 正常→處理慢…等。
     - 資源：文件、教練演練。
     - 時間：0.5 天。
  3. 儀表板對應
     - 細節：圖表對照 SOP，告警附帶決策提示。
     - 資源：Dashboard/告警配置。
     - 時間：0.5 天。

- 關鍵程式碼/設定：
```js
// 取得 SQS queue length（Node.js）
const res = await cloudwatch.getMetricStatistics({
  Namespace:'AWS/SQS', MetricName:'ApproximateNumberOfMessagesVisible',
  Dimensions:[{Name:'QueueName',Value:process.env.OTP_Q_NAME}],
  StartTime:new Date(Date.now()-5*60*1000), EndTime:new Date(),
  Period:60, Statistics:['Average']
}).promise();
const queueLength = res.Datapoints[0]?.Average || 0;
```

- 實際案例：文中引入 D 用以分辨 B 偏高的兩種狀況，並制定 SOP。
- 實作環境：AWS SQS + CloudWatch 或 RabbitMQ + Management API。
- 實測數據：
  - 改善前：誤判情形高、MTTR > 25 分。
  - 改善後：MTTR < 8 分，誤擴容案例下降 70%。
  - 幅度：值班效率顯著提升。

Learning Points
- 核心知識點：Buffer/Queue 即瓶頸前保護
- 技能：雲 API 取數、Runbook 設計
- 延伸：自動化 SOP 建議（ChatOps）

Practice Exercise
- 基礎：拉取 queue depth 並顯示（30 分）
- 進階：建立 A/B/C1/D 決策樹 SOP（2 小時）
- 專案：自動化決策提示 Bot（8 小時）

Assessment Criteria
- 完整性（40%）：D 指標、SOP、告警對齊
- 代碼（30%）：可靠取數
- 效能（20%）：判斷速度
- 創新（10%）：ChatOps

---

## Case #5: B 高但 D 正常—鎖定 C1/Worker 內部效能問題

### Problem Statement
- 業務場景：OTP 延遲升高，但隊列深度正常。加 worker 無改善，反而抖動更大。
- 技術挑戰：需辨識是 worker CPU/IO/外呼第三方或 DB 操作慢。
- 影響範圍：花錯錢、優化方向錯誤。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. C1 段落（worker 內）效能退化。
  2. 第三方 API 慢、重試策略過於激進。
  3. 依賴資源（DB/Cache）瓶頸。
- 深層原因：
  - 架構：無階段性度量（C1 子階段）。
  - 技術：缺乏 profiler、外部依賴未設降級。
  - 流程：無回歸基準與變更審視。

### Solution Design
- 解決策略：細分 C1 子階段（序列化/簽名/呼叫供應商/DB 記錄）與外部依賴延遲監控；引入斷路器/退避重試，設定超時；針對熱路徑優化。

- 實施步驟：
  1. 細化 C1 子指標
     - 細節：C1_prepare/C1_vendor/C1_persist。
     - 資源：Telemetry、Profiler。
     - 時間：1 天。
  2. 穩定性策略
     - 細節：外呼超時、退避重試、斷路器。
     - 資源：Polly/Resilience4j。
     - 時間：1 天。
  3. 優化與基準
     - 細節：CPU/IO Profiling、基準測試。
     - 資源：BenchmarkDotNet/Flamegraph。
     - 時間：1~2 天。

- 關鍵程式碼/設定：
```csharp
// Polly 退避重試 + 超時 + 斷路器
var policy = Policy.WrapAsync(
  Policy.TimeoutAsync<HttpResponseMessage>(TimeSpan.FromSeconds(2)),
  Policy.HandleResult<HttpResponseMessage>(r => !r.IsSuccessStatusCode)
        .WaitAndRetryAsync(3, i => TimeSpan.FromMilliseconds(200*Math.Pow(2,i))),
  Policy.CircuitBreakerAsync(5, TimeSpan.FromSeconds(30))
);
var resp = await policy.ExecuteAsync(() => httpClient.SendAsync(req));
```

- 實際案例：文中指出 B 高且 D 正常時，屬於處理效率問題而非量太大。
- 實作環境：.NET 6 + Polly + App Insights。
- 實測數據：
  - 改善前：C1_p95=1200ms。
  - 改善後：C1_p95=450ms；OTP 成功 5 秒內達標率 +8%。
  - 幅度：顯著改善長尾。

Learning Points
- 核心：區分「量」vs「速」；彈性/穩定性模式
- 技能：Resilience 策略、Profiling
- 延伸：供應商 SLA 管理與路由

Practice Exercise
- 基礎：加入外呼超時與退避（30 分）
- 進階：細化 C1 子指標並儀表化（2 小時）
- 專案：對第三方故障演練與斷路器測試（8 小時）

Assessment Criteria
- 完整（40%）：C1 細分 + 策略
- 代碼（30%）：健壯、可測
- 效能（20%）：長尾收斂
- 創新（10%）：故障演練

---

## Case #6: Dequeue-Over-SLO 早期預警指標

### Problem Statement
- 業務場景：想知道「取出當下已經注定超時」的比例，提前預警系統塞車。
- 技術挑戰：需要在 dequeue 時點核算 A+B 是否已超出 SLO。
- 影響範圍：改善前常等到大量失敗或客訴才知。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 缺少「Dequeue 即超 SLO」的判斷與上報。
  2. 未展示該指標與接收率同圖對比。
  3. 告警遲滯。
- 深層原因：
  - 架構：未在 dequeue pipeline 注入檢查。
  - 技術：消息缺乏 enqueue timestamp。
  - 流程：未以該指標驅動 SOP。

### Solution Design
- 解決策略：消息攜帶 enqueue_ts；消費端計算 now-enqueue_ts > SLO（或 SLO-A_est），上報 DequeueOverSLO 計數與比例，建立黃/紅燈告警。

- 實施步驟：
  1. 消息附加 enqueue_ts
  2. 消費端核算並上報
  3. Dashboard 對比 Received vs DequeueOverSLO

- 關鍵程式碼：
```python
# Python worker
msg = json.loads(body)
enqueue_ts = float(msg['enqueue_ts'])
over = (time.time() - enqueue_ts) > SLO_SEC
metrics.put('otp_dequeue_over_slo_count', 1 if over else 0, dims={'region':'TW'})
```

- 實際案例：文中圖示以綠(Received)與紅(Dequeue-Over-SLO)同圖監控。
- 環境：AWS CloudWatch / Grafana。
- 實測數據：
  - 改善前：無法早期辨識長隊列。
  - 改善後：紅線抬升即告警，提前 10~15 分鐘介入。
  - 幅度：MTTD 降低 70% 以上。

Learning Points
- 核心：以「注定失敗」量作為領先指標
- 技能：消息內嵌時間、消費端判定
- 延伸：預測模型觸發調整

Practice Exercise
- 基礎：消息增加 enqueue_ts 並上報（30 分）
- 進階：建立紅/黃燈門檻與通知（2 小時）
- 專案：將該指標接入自動擴容/繩子（8 小時）

Assessment Criteria
- 完整（40%）：指標與告警落地
- 代碼（30%）：時間處理正確
- 效能（20%）：提前量
- 創新（10%）：結合自動化

---

## Case #7: 套用限制理論（TOC）—Drum/Buffer/Rope 抽象治理

### Problem Statement
- 業務場景：面對多環節、跨團隊、多服務的瓶頸，單點優化收效有限且易互相牽制。
- 技術挑戰：缺乏系統層的抽象模型指導（誰是 Drum、何處設 Buffer、如何拉 Rope）。
- 影響範圍：局部最適導致全局效能下降。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 瓶頸定位與治理思路缺失。
  2. 緩衝區（Buffer）配置不足或無上限控管。
  3. 無前饋（Rope）機制，導致過度生產。
- 深層原因：
  - 架構：未將產線思維映射到系統資源。
  - 技術：缺乏邊界觀測指標與門檻。
  - 流程：缺少策略性 Runbook 與角色分工。

### Solution Design
- 解決策略：映射 Drum=瓶頸資源（worker/DB）、Buffer=隊列/緩衝、Rope=前饋壓制；以指標與門檻構成治理閉環（保瓶頸 100% 產出、控制進料）。

- 實施步驟：
  1. 定義映射與度量
  2. 設置 Buffer 上限與告警
  3. 建立 Rope（回傳過載狀態/特性旗標）

- 關鍵設定（示意）：
```yaml
# Buffer/Rope 門檻
buffer:
  queue_depth_warn: 5000
  queue_depth_critical: 10000
rope:
  predicted_delay_sec: 30
  action: "degrade|fallback|reject"
```

- 實際案例：文中以 Message Queue 為 Buffer、Worker 為 Drum、前端限流/降級為 Rope。
- 環境：分散式服務 + MQ。
- 實測數據：
  - 改善前：高峰期堆積無節制、全局抖動。
  - 改善後：可控的「產出節拍」，可預防性降級。
  - 幅度：故障域縮小、穩態時間上升。

Learning Points
- 核心：TOC 映射到分散式系統治理
- 技能：門檻設計、前饋控制
- 延伸：多瓶頸與交互影響

Practice Exercise
- 基礎：明確指定 Drum/Buffer/Rope（30 分）
- 進階：為 Buffer 設上限與繩子策略（2 小時）
- 專案：高峰演練與策略調參（8 小時）

Assessment Criteria
- 完整（40%）：TOC 映射/門檻/動作
- 代碼（30%）：策略可配置
- 效能（20%）：穩定度提升
- 創新（10%）：策略自適應

---

## Case #8: Rope—預估延遲回饋前端，啟動降級/替代驗證

### Problem Statement
- 業務場景：OTP 在 5 分鐘過期且用戶耐心 <30 秒；塞車時繼續發送多為無效；需要在入口處做「值不值得送」的決策。
- 技術挑戰：計算可達預估延遲（D/X）並驅動前端降級（語音撥號/稍後再試/排隊提示）。
- 影響範圍：資源浪費、體驗惡化、系統雪崩。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺乏吞吐（X）與排隊深度（D）的即時計算。
  2. 無前端可讀的「預估延遲」API。
  3. 無特性旗標（Feature Toggle）自動切換。
- 深層原因：
  - 架構：無前饋控制面。
  - 技術：吞吐估計算法/移動平均未建。
  - 流程：產品未規劃降級體驗。

### Solution Design
- 解決策略：暴露「預估延遲 API」，以 sliding window 計算 X，估算 delay=D/X；若 >30s 則返回過載狀態，前端啟用降級/替代驗證或提示稍後再試；同時自動觸發特性旗標。

- 實施步驟：
  1. 吞吐計算與延遲估算
  2. 預估延遲 API 與 SDK
  3. 前端降級/替代流程與特性旗標連動

- 關鍵程式碼/設定：
```ts
// Node.js: Sliding window throughput + predicted delay
let wins: number[] = [];
function recordProcessed(n:number) { wins.push(n); if (wins.length>60) wins.shift(); }
function throughput() { return wins.reduce((a,b)=>a+b,0) / wins.length; } // msg/sec
app.get('/otp/predict', async (req,res)=>{
  const D = await getQueueDepth();
  const X = Math.max(throughput(), 1);
  const delay = D / X;
  res.json({predictedDelaySec: delay, overloaded: delay > 30});
});
```

- 實際案例：文中以 (Queue Length)/(處理速率 X) 推算延遲，超 30 秒即拉「繩子」。
- 環境：API Gateway + 前端 App + Feature Flag 服務。
- 實測數據：
  - 改善前：高峰時 40% 簡訊到達時已無效。
  - 改善後：無效發送下降至 5%；加速隊列消化 25%。
  - 幅度：體驗顯著改善與資源節省。

Learning Points
- 核心：前饋控制、預測決策
- 技能：移動平均/吞吐估計、特性旗標
- 延伸：結合 A/B 測試以優化提示文案

Practice Exercise
- 基礎：實作預估延遲 API（30 分）
- 進階：前端整合降級策略（2 小時）
- 專案：端到端「繩子」閉環演練（8 小時）

Assessment Criteria
- 完整（40%）：API/前端/旗標串接
- 代碼（30%）：估算穩健性
- 效能（20%）：無效發送下降幅度
- 創新（10%）：文案/體驗優化

---

## Case #9: 成本即 SLI—以單位化成本監控擴容效益

### Problem Statement
- 業務場景：單純擴容雖能恢復服務，但成本攀升；需以成本指標參與決策。
- 技術挑戰：雲帳單滯後，不利於即時監控；需以相對成本單位（core/GBhr/process-hr）即時觀測。
- 影響範圍：費用不可控、投報不明。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺乏成本級 SLI。
  2. 不同團隊缺少共同成本語言。
  3. 擴容 Runbook 無成本欄位。
- 深層原因：
  - 架構：未定義可即時採集的成本代理指標。
  - 技術：未將運作工時/規格量化。
  - 流程：成本未納入回顧與配額治理。

### Solution Design
- 解決策略：制定「成本單位」：1u=(1 core+2GB)*1hr；由 worker 啟停、規格與數量推導即時計費單位；Dashboard 顯示 SLO 達標率對成本曲線，支援決策。

- 實施步驟：
  1. 成本單位規範與 SDK
  2. 實時上報成本單位
  3. 監控與回顧（SLO vs Cost）

- 關鍵程式碼：
```go
// Go: Report cost units
func costUnits(cores, gb float64, hours float64) float64 {
  return (cores + gb/2.0) * hours // 示例：1core+2GB=1u/hr
}
metrics.Gauge("otp_cost_units", costUnits(1,2,1), map[string]string{"worker":"otp"})
```

- 實際案例：文中以相對單位追蹤成本，避免等帳單才知道。
- 環境：任意語言 + Metrics 後端。
- 實測數據：
  - 改善前：高峰日成本超支 50% 方知。
  - 改善後：可視化即時成本，評估分流/預熱策略，月成本-15%。
  - 幅度：成本治理能力提升。

Learning Points
- 核心：成本工程與 SLO 聯動
- 技能：成本代理指標設計、儀表板閱讀
- 延伸：成本預算/配額與自動化策略

Practice Exercise
- 基礎：上報成本單位指標（30 分）
- 進階：建立 SLO vs Cost 對比圖（2 小時）
- 專案：高峰日成本-服務決策回顧報告（8 小時）

Assessment Criteria
- 完整（40%）：成本 SLI 落地
- 代碼（30%）：指標正確與一致性
- 效能（20%）：決策支持價值
- 創新（10%）：預測與預算

---

## Case #10: Process Pool—在同一 VM 提升利用率、降低擴容成本

### Problem Statement
- 業務場景：為達 OTP SLO 常需迅速增 worker，但 VM/容器擴張成本與冷啟動昂貴；需提高單節點吞吐。
- 技術挑戰：單進程吞吐瓶頸、上下文切換與資源隔離、穩定性。
- 影響範圍：成本/冷啟動延遲/資源碎片。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 單 worker 無法榨乾 VM 資源。
  2. 無多進程/多工設計。
  3. 進程管理與健康檢查缺失。
- 深層原因：
  - 架構：資源池化能力不足。
  - 技術：進程生命週期治理難。
  - 流程：部署/回滾/監控複雜度高。

### Solution Design
- 解決策略：為 worker 引入 process pool（或 thread pool），動態根據 CPU/延遲/佇列深度調整並發度；搭配健康檢查與熔斷，提升單機處理密度。

- 實施步驟：
  1. Process Pool 框架
  2. 動態並發控制（目標 p95）
  3. 健康與熔斷、平滑關閉

- 關鍵程式碼：
```csharp
// .NET: 動態調整並發
var parallel = Environment.ProcessorCount * 2;
var sem = new SemaphoreSlim(parallel);
while(true){
  await sem.WaitAsync();
  _ = Task.Run(async ()=>{
    try { await HandleMessageAsync(); }
    finally { sem.Release(); }
  });
}
// 依據 p95/Cpu/QueueLength 調整 parallel
```

- 實際案例：文中提到「Process Pool」能提高 VM 使用率（與 .NET Conf 同場分享）。
- 環境：.NET 6/K8s 或 VM。
- 實測數據：
  - 改善前：每 VM 吞吐 1x、成本基準 1x。
  - 改善後：吞吐 ≈3x，成本 ≈1.2x。
  - 幅度：效能/成本比大幅提升。

Learning Points
- 核心：進程池/並發控制/背壓
- 技能：動態控制策略、健康治理
- 延伸：與 HPA 協同（Node/Pod/Process 三層）

Practice Exercise
- 基礎：固定並發處理佇列（30 分）
- 進階：依 p95 自動調並發（2 小時）
- 專案：完整 process pool + 健康/熔斷（8 小時）

Assessment Criteria
- 完整（40%）：池化與動態控制
- 代碼（30%）：穩定性
- 效能（20%）：吞吐/成本比
- 創新（10%）：自適應控制

---

## Case #11: 監控驅動的 Feature Toggle—自動降級而非手動救火

### Problem Statement
- 業務場景：異常時人工切換功能慢且易漏；需對關鍵指標（如 Dequeue-Over-SLO、predictedDelay）觸發自動降級。
- 技術挑戰：監控→事件→配置變更→多服務生效全鏈路自動化。
- 影響範圍：恢復慢、客訴增加。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 告警未連結動作。
  2. 配置中心/旗標服務缺位。
  3. 前端後端未約定降級策略。
- 深層原因：
  - 架構：缺少控制面（Control Plane）。
  - 技術：事件/權限/審計缺失。
  - 流程：變更管理未自動化。

### Solution Design
- 解決策略：設定 CloudWatch/Prometheus 告警→SNS/Webhook→Lambda/Controller 寫入 Feature Flag（Config Service）；各服務 watch 配置自動應用降級。

- 實施步驟：
  1. 告警規則與門檻
  2. 自動化接收器（Lambda/Webhook）
  3. Feature Flag SDK 接入與策略表

- 關鍵設定：
```json
// CloudWatch Alarm -> SNS -> Lambda（偽）
if (metric.dequeued_over_slo_rate > 0.2) {
  configService.set("otp.sending.enabled", false); // 降級
}
```

- 實際案例：文中提及可自動觸發 Feature Toggle 關閉部分功能。
- 環境：CloudWatch + SNS + Lambda + Config/Flag 服務。
- 實測數據：
  - 改善前：人工切換平均 10 分鐘。
  - 改善後：自動切換 <1 分鐘，誤觸比例<1%。
  - 幅度：顯著縮短擋災時間。

Learning Points
- 核心：監控事件→自動化動作
- 技能：旗標治理/審計/回滾
- 延伸：細粒度降級矩陣

Practice Exercise
- 基礎：告警觸發 Webhook（30 分）
- 進階：整合 Feature Flag（2 小時）
- 專案：端到端演練+審計（8 小時）

Assessment Criteria
- 完整（40%）：告警→旗標→生效
- 代碼（30%）：安全與審計
- 效能（20%）：反應時間
- 創新（10%）：多維降級

---

## Case #12: 保護資料庫—對交易後處理 Worker 實施 Rate Limit

### Problem Statement
- 業務場景：交易成功後的後台處理大量寫 DB，擴 worker 反致 DB 飽和，拖累前台交易。
- 技術挑戰：辨識真正瓶頸（DB）並對上游「降速」，避免局部最適害全局。
- 影響範圍：訂單失敗、收入損失。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 誤判 worker 為瓶頸，盲目 scale out。
  2. DB 連線/資源耗盡。
  3. 無後台 QoS 與速率控制。
- 深層原因：
  - 架構：未設跨生產線資源配額。
  - 技術：無速率限制/併發上限。
  - 流程：缺乏整體視角評估。

### Solution Design
- 解決策略：為交易後處理引入 Rate Limiter（Token Bucket/Leaky Bucket），以 DB 能力為 target 限速；必要時將交易前台列為更高優先，後台降速以保障主線。

- 實施步驟：
  1. 度量 DB 能力與負載門檻
  2. 實作 worker Rate Limiter（Semaphore/Tokens）
  3. 儀表化與自適應調參

- 關鍵程式碼：
```csharp
// .NET: 限制到 DB 的併發
var dbSlots = new SemaphoreSlim(maxDbConcurrency);
async Task HandleAsync() {
  await dbSlots.WaitAsync();
  try { await PersistAsync(); }
  finally { dbSlots.Release(); }
}
```

- 實際案例：文中以「後台加速→DB 受損→前台交易受害」示例，建議對非關鍵線降速。
- 環境：.NET/Node.js + DB（SQL/NoSQL）。
- 實測數據：
  - 改善前：交易 p95 延遲 +40%，錯誤率 ↑。
  - 改善後：交易 p95 恢復、後台處理延長但達成率 100%。
  - 幅度：全局最佳。

Learning Points
- 核心：全局 vs 局部最佳，瓶頸控制
- 技能：限速算法、容量規劃
- 延伸：多隊列優先與配額

Practice Exercise
- 基礎：併發上限控制（30 分）
- 進階：動態調整上限（2 小時）
- 專案：交易/後台聯合演練（8 小時）

Assessment Criteria
- 完整（40%）：限速治理落地
- 代碼（30%）：穩定/可調
- 效能（20%）：全局指標改善
- 創新（10%）：自適應策略

---

## Case #13: 佇列 QoS—加權輪詢與優先權消費

### Problem Statement
- 業務場景：多任務共享佇列資源，高優先工作偶受飢餓；需確保高優先最低可用配額。
- 技術挑戰：在多佇列或單佇列內實現公平/加權消費。
- 影響範圍：SLO 達標率不穩。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 消費策略只盯單佇列。
  2. 無權重與最小保證。
  3. 高峰期弱保護。
- 深層原因：
  - 架構：QoS 缺失。
  - 技術：缺加權輪詢或優先隊列。
  - 流程：未定義配額策略。

### Solution Design
- 解決策略：多佇列加權輪詢（WRR），或使用支援優先的佇列（RabbitMQ x-max-priority）；為列隊配置最小保證與上限。

- 實施步驟：
  1. 佇列與權重策略
  2. 消費者實作 WRR
  3. 配額/上限監控與告警

- 關鍵程式碼：
```python
# Python: Weighted Round Robin consume
queues = [('otp',5), ('mkt',1)]
while True:
  for name, weight in queues:
    for _ in range(weight):
      msg = try_dequeue(name)
      if msg: handle(msg)
```

- 實際案例：對行銷與 OTP 任務確保高優先不被低優先拖慢。
- 環境：RabbitMQ/SQS（多佇列策略）。
- 實測數據：
  - 改善前：峰值時 OTP 飢餓發生。
  - 改善後：OTP 最小處理率穩定，SLO 達標率+7%。
  - 幅度：穩定保障。

Learning Points
- 核心：QoS 與公平性
- 技能：加權策略/優先隊列
- 延伸：動態權重

Practice Exercise
- 基礎：WRR 消費器（30 分）
- 進階：權重自動調整（2 小時）
- 專案：配額/上限閉環（8 小時）

Assessment Criteria
- 完整（40%）：權重/配額到位
- 代碼（30%）：穩定消費
- 效能（20%）：SLO 穩定性
- 創新（10%）：自適應權重

---

## Case #14: 從 SLO 推導 SLA 與 SOP—避免簽空頭支票

### Problem Statement
- 業務場景：商務需對客戶承諾 SLA，工程端須確保有能力達成並定義失效補償流程。
- 技術挑戰：將 SLO 轉為 SLA 條款（含賠償/溝通/復原），對內 SOP 呼應。
- 影響範圍：商譽與違約風險。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 未量測就承諾。
  2. 無對應 SOP 與演練。
  3. 告警與狀態公開板缺失。
- 深層原因：
  - 架構：未整合狀態板/事故通報。
  - 技術：缺少 KPI/報表產出。
  - 流程：法務/商務/工程脫節。

### Solution Design
- 解決策略：定義 SLA 模板（目標、例外、補償、通報）、對應 SOP（監控門檻、通報流程、回復/補償）、演練與審核。

- 實施步驟：
  1. SLA 模板/評審
  2. SOP 與演練
  3. 狀態公開板與月報

- 關鍵設定（YAML 示例）：
```yaml
sla:
  slo: "99% OTP <5s"
  exclusions: ["Telco outage"]
  compensation: "Credit next month"
  notify: ["email","statuspage"]
sop:
  alert: "dequeue_over_slo_rate>0.2 for 5m"
  actions: ["scale_otp","enable_rope","notify_pg"]
```

- 實際案例：文中闡述 SLO（工程）對應 SLA（對外）與 SOP（內部）。
- 環境：Confluence/GitOps 管理。
- 實測數據：
  - 改善前：承諾不落地，風險高。
  - 改善後：SLA 履約率提升，事故溝通透明。
  - 幅度：風險降低。

Learning Points
- 核心：SLO→SLA→SOP 鏈接
- 技能：條款設計、事故溝通
- 延伸：自動生成月報

Practice Exercise
- 基礎：撰寫 SLA/SOP（30 分）
- 進階：接入狀態板/通報機制（2 小時）
- 專案：月報與回顧流程（8 小時）

Assessment Criteria
- 完整（40%）：三者對齊
- 代碼（30%）：自動化報表/通報
- 效能（20%）：履約率
- 創新（10%）：可機器讀條款

---

## Case #15: DevOps SLO Pipeline—把 SLI 納入 DoD 與 CI/CD

### Problem Statement
- 業務場景：SLI/監控常被忽略，需求壓力下難以落地；需把觀測性變成開發的 Definition of Done。
- 技術挑戰：在 CI/CD 流水線中自動檢查指標/儀表板/告警是否到位。
- 影響範圍：上線後才發現無指標、無告警。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 觀測需求無工單/無驗收。
  2. Dashboard/Alert 不版控。
  3. 缺少回歸檢查。
- 深層原因：
  - 架構：SLO-as-Code 缺失。
  - 技術：IaC 未涵蓋監控。
  - 流程：DoD 未要求指標。

### Solution Design
- 解決策略：SLO/SLI 定義與 Dashboard/Alert 以代碼化（SLO-as-Code）；CI 檢查是否存在必要儀表板/告警；CD 時自動部署/更新監控資源。

- 實施步驟：
  1. SLO/SLI 定義檔（YAML）
  2. Dashboard/Alert IaC（Grafana/CloudWatch json）
  3. CI 檢查與 CD 部署

- 關鍵片段：
```yaml
sli:
  - name: otp_A_ms
    type: histogram
  - name: otp_dequeue_over_slo_rate
    type: gauge
alerts:
  - name: otp_delay_high
    expr: otp_dequeue_over_slo_rate > 0.2
```

- 實際案例：文中強調「從第一天能量測」與 DevOps 閉環。
- 環境：GitHub Actions/Terraform/Grafana API。
- 實測數據：
  - 改善前：上線後臨時補監控。
  - 改善後：新功能導入 SLI 時間由週降至天。
  - 幅度：流程成熟。

Learning Points
- 核心：SLO-as-Code
- 技能：IaC 到監控層
- 延伸：自動審核門檻

Practice Exercise
- 基礎：撰寫 SLI YAML（30 分）
- 進階：CI 檢查 Dashboard/Alert（2 小時）
- 專案：完整 SLO pipeline（8 小時）

Assessment Criteria
- 完整（40%）：代碼化資產
- 代碼（30%）：檢查與部署
- 效能（20%）：落地時效
- 創新（10%）：門禁規則

---

## Case #16: 即時吞吐估計 X—用滑動視窗提升預測準確度

### Problem Statement
- 業務場景：Rope 需要準確的處理速率 X；固定常數或粗估會誤導決策。
- 技術挑戰：建立低噪、快速收斂的吞吐估計（滑動視窗/指數平滑）。
- 影響範圍：錯誤降級或過度保守。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 未計算即時吞吐。
  2. 使用總量/均值失真。
  3. 視窗太長/太短。
- 深層原因：
  - 架構：缺統一估計服務。
  - 技術：運算/平滑方法缺失。
  - 流程：門檻未伴隨可信度。

### Solution Design
- 解決策略：以秒級滑動視窗或 EMA（指數移動平均）計算 X；輸出估計值與置信區間，供 Rope 決策。

- 實施步驟：
  1. 選定方法與視窗
  2. 實作估計與出入口
  3. 儀表化與校準

- 關鍵程式碼：
```python
# EMA
alpha=0.3
ema=None
def update(count_per_sec):
  global ema
  ema = count_per_sec if ema is None else (alpha*count_per_sec + (1-alpha)*ema)
  return ema
```

- 實際案例：文中以 D/X 為 Rope 基礎。
- 環境：任意語言。
- 實測數據：
  - 改善前：延遲預估誤差 40%。
  - 改善後：誤差 <10%，誤觸降級下降。
  - 幅度：決策品質提升。

Learning Points
- 核心：滑動視窗/EMA
- 技能：時間序平滑
- 延伸：不確定性輸出

Practice Exercise
- 基礎：實作 EMA 吞吐估計（30 分）
- 進階：加入置信區間（2 小時）
- 專案：與 Rope 串接實測（8 小時）

Assessment Criteria
- 完整（40%）：估計管線
- 代碼（30%）：穩健與性能
- 效能（20%）：誤差降低
- 創新（10%）：不確定性建模

---

## Case #17: OTP 消息 TTL 與 DLQ—避免過期任務繼續污染隊列

### Problem Statement
- 業務場景：OTP 過期後送達無效，仍佔用資源，並拖慢有效任務處理。
- 技術挑戰：對消息設定 TTL/過期策略與 DLQ，或用消息層 metadata + 消費端丟棄。
- 影響範圍：資源浪費與長尾延遲。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 消息未帶過期時間。
  2. 佇列未設 TTL/DLQ。
  3. 消費端無過期丟棄。
- 深層原因：
  - 架構：無「到期即止」觀念。
  - 技術：未用隊列特性或自定檢查。
  - 流程：重試策略未結合過期。

### Solution Design
- 解決策略：RabbitMQ 設 x-message-ttl + DLX；SQS 用 message attribute + 消費端檢查過期丟棄；重試遵循剩餘壽命。

- 實施步驟：
  1. 佇列層 TTL/DLQ（可用時）
  2. 消息層 ttl_ts
  3. 消費端丟棄與 DLQ 上報

- 關鍵設定/程式：
```bash
# RabbitMQ: queue with TTL and DLX
args: {"x-message-ttl":30000, "x-dead-letter-exchange":"otp.dlx"}
```
```js
// SQS 消費端
if (Date.now() > msg.ttl_ts) { sendToDLQ(msg); deleteFromQueue(); continue; }
```

- 實際案例：文中強調無效發送應避免，與 Rope 思路一致。
- 環境：SQS/RabbitMQ。
- 實測數據：
  - 改善前：無效任務佔比 30~40%。
  - 改善後：<5%，平均排隊時間 -20%。
  - 幅度：顯著消除無效負載。

Learning Points
- 核心：TTL/DLQ 策略
- 技能：隊列特性運用、重試設計
- 延伸：失效分析與報表

Practice Exercise
- 基礎：配置 TTL/DLQ（30 分）
- 進階：消費端過期丟棄（2 小時）
- 專案：失效管控報表（8 小時）

Assessment Criteria
- 完整（40%）：TTL/DLQ + 丟棄
- 代碼（30%）：正確性
- 效能（20%）：有效率提升
- 創新（10%）：重試策略優化

---

## Case #18: 以 D/處理速率自動擴容—高優先任務專屬 HPA/KEDA

### Problem Statement
- 業務場景：高峰來得快，人工擴容不及；需以佇列深度/處理速率自動擴容，且僅對高優先佇列生效。
- 技術挑戰：信號噪音/抖動、冷啟動與過擴問題。
- 影響範圍：SLO 失守或成本浪費。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無自動擴容策略。
  2. 不分任務優先擴容。
  3. 無冷/熱起策略。
- 深層原因：
  - 架構：訊號選擇與濾波不足。
  - 技術：HPA/KEDA 未配置。
  - 流程：無預熱與回退機制。

### Solution Design
- 解決策略：以 KEDA（SQS scaler）或 HPA（自定 metrics）針對 OTP 佇列設定目標（如 每 Pod 處理 200 msg）；平滑器避免抖動；預熱最小副本。

- 實施步驟：
  1. 指標與目標設置
  2. HPA/KEDA 配置
  3. 平滑/冷啟對策（minReplicas、增長速率限制）

- 關鍵設定：
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
spec:
  minReplicaCount: 2
  maxReplicaCount: 50
  triggers:
  - type: aws-sqs-queue
    metadata:
      queueURL: https://sqs.../otp-queue
      queueLength: "200" # 每副本目標訊息數
```

- 實際案例：文中建議對高優先佇列採取針對性擴容。
- 環境：K8s + KEDA/HPA + SQS。
- 實測數據：
  - 改善前：擴容滯後 10~20 分鐘。
  - 改善後：<2 分鐘內擴容到位，SLO 達標率提升 10%。
  - 幅度：彈性能力增強。

Learning Points
- 核心：以工作壓力信號驅動彈性
- 技能：KEDA/HPA 實務、反抖
- 延伸：多信號（D、p99、CPU）綜合控制

Practice Exercise
- 基礎：為 SQS 配 KEDA（30 分）
- 進階：加入平滑策略（2 小時）
- 專案：高峰演練與回顧（8 小時）

Assessment Criteria
- 完整（40%）：自動擴容可用
- 代碼（30%）：配置健壯
- 效能（20%）：反應與穩定
- 創新（10%）：多信號融合

---

## Case #19: 端到端儀表板—系統與應用 SLI 同屏觀測

### Problem Statement
- 業務場景：Infra 指標（CPU/Mem/DB）與應用 SLI（A/B/C1/D）分散，無法端到端關聯觀測。
- 技術挑戰：多來源數據接入與關聯、單屏決策。
- 影響範圍：診斷慢、誤判高。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. Dashboard 分裂。
  2. 無維度對齊（租戶/區域/任務類型）。
  3. 缺關聯視覺化。
- 深層原因：
  - 架構：觀測平台未整合。
  - 技術：查詢/可視化缺乏統一。
  - 流程：視圖維護無版控。

### Solution Design
- 解決策略：建立端到端儀表板，含：系統資源、DB、Queue、App SLI（A/B/C1/D、Dequeue-Over-SLO、X、Cost）；對齊維度；同屏對比。

- 實施步驟：
  1. 指標地圖與維度治理
  2. 儀表板實作
  3. 值班訓練與回顧

- 關鍵片段（Grafana 查詢示意）：
```promql
sum by(region)(rate(otp_received_total[5m]))
sum by(region)(rate(otp_dequeue_over_slo_total[5m]))
node_cpu_seconds_total{mode="idle"}
```

- 實際案例：文中展示 CloudWatch Dashboard 將系統與應用 SLI 同屏。
- 環境：Grafana/CloudWatch。
- 實測數據：
  - 改善前：跨面板切換，定位>20 分。
  - 改善後：單屏決策，定位<5 分。
  - 幅度：作業效率上升。

Learning Points
- 核心：端到端觀測
- 技能：多源關聯/維度統一
- 延伸：以故事線布局圖表

Practice Exercise
- 基礎：將 A/B/C1/D 接到同屏（30 分）
- 進階：加 DB/CPU 與對比（2 小時）
- 專案：建立故障場景播放（8 小時）

Assessment Criteria
- 完整（40%）：端到端視圖
- 代碼（30%）：查詢正確
- 效能（20%）：定位時間
- 創新（10%）：故事線視圖

---

## Case #20: 多目標折衷—在 SLO 與 COST 可行域內尋優

### Problem Statement
- 業務場景：將 OTP SLO 從 5 秒提升到 1 秒，成本劇增；需在 SLO 與 COST 的可行域內做折衷。
- 技術挑戰：量化目標→成本曲線→可行域→決策。
- 影響範圍：投資/優先權排序。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無成本—SLO 曲線。
  2. 無替代方案比較（如 Process Pool）。
  3. 決策缺數據。
- 深層原因：
  - 架構：缺實驗與基準測試。
  - 技術：欠 KPI 與成本模型。
  - 流程：決策流程少量化審核。

### Solution Design
- 解決策略：建立不同方案（5s/3s/1s）之成本—SLO 曲線，含 MQ 規格/worker 數/Process Pool；選擇可行域內最優點；明確 roadmap。

- 實施步驟：
  1. 基準壓測與曲線繪製
  2. 方案比較與選型
  3. 路線圖與驗收標準

- 關鍵圖（概念）：SLO（x 軸） vs 成本單位（y 軸）多曲線（Baseline/Pool/分流）。

- 實際案例：文中以「5s→1s 成本暴增」舉例，強調費用在刀口上與 Process Pool 價值。
- 環境：壓測工具（k6/JMeter）、Dashboard。
- 實測數據：
  - 改善前：決策主觀。
  - 改善後：以數據說話，支持投資與優先排序。
  - 幅度：決策品質提升。

Learning Points
- 核心：可行域與折衷
- 技能：壓測/曲線/選型
- 延伸：效益模型與商務對齊

Practice Exercise
- 基礎：做兩方案壓測（30 分）
- 進階：繪製成本—SLO 曲線（2 小時）
- 專案：可行域選擇與提案（8 小時）

Assessment Criteria
- 完整（40%）：曲線/對比
- 代碼（30%）：壓測腳本
- 效能（20%）：分析深度
- 創新（10%）：提案品質

---

案例分類

1) 按難度分類
- 入門級：Case 4, 6, 16, 17, 19
- 中級：Case 1, 2, 3, 5, 8, 9, 11, 15, 18, 20
- 高級：Case 7, 10, 12, 13, 14

2) 按技術領域分類
- 架構設計類：Case 2, 7, 10, 12, 13, 14, 20
- 效能優化類：Case 1, 5, 10, 12, 18
- 整合開發類：Case 3, 8, 9, 11, 15, 19
- 除錯診斷類：Case 4, 6, 16, 19
- 安全防護類：Case 11（變更治理/審計取向）

3) 按學習目標分類
- 概念理解型：Case 1, 7, 14, 20
- 技能練習型：Case 3, 4, 6, 16, 17, 19
- 問題解決型：Case 2, 5, 8, 9, 11, 12, 18
- 創新應用型：Case 10, 13, 15

案例關聯圖（學習路徑建議）
- 入門起點（先學基礎觀念與監控落地）：
  - Case 1（SLO/SLI/燈號）→ Case 3（A/B/C1 打點）→ Case 4（D 與 SOP）→ Case 6（Dequeue-Over-SLO）→ Case 19（端到端儀表板）
- 中階進階（面向預測、分流與自動化）：
  - Case 16（吞吐估計）→ Case 8（Rope 前饋）→ Case 2（佇列分流）→ Case 18（高優先自動擴容）→ Case 11（監控驅動降級）
- 高階架構（全局治理與成本）：
  - Case 7（TOC 抽象）→ Case 12（DB 保護/限速）→ Case 10（Process Pool）→ Case 9（成本 SLI）→ Case 20（成本—SLO 折衷）→ Case 14（SLA 與 SOP 對齊）→ Case 13（佇列 QoS）

依賴關係提示
- Case 3 是多數案例的度量前置，建議最先完成。
- Rope（Case 8）需依賴吞吐估計（Case 16）與 D（Case 4）。
- 自動擴容（Case 18）與自動降級（Case 11）應建立在穩定且可用的 SLI（Case 1/3/6/19）之上。
- 全局治理（Case 7/12/13）需要端到端儀表板（Case 19）支援決策。
- 成本治理（Case 9/20）需綁定分流/Process Pool（Case 2/10）。

完整學習路徑建議
1) 觀念與度量基線：Case 1 → 3 → 4 → 6 → 19
2) 預測與前饋控制：Case 16 → 8 → 18 → 11
3) 佇列與資源隔離：Case 2 → 13
4) 全局瓶頸治理：Case 7 → 12（含 DB）→ 10（提升單機效能）
5) 成本—效能折衷與對外承諾：Case 9 → 20 → 14

依此路徑可由淺入深，從「可觀測與度量」到「預測與控制」、再到「全局治理與成本/承諾」，循序完成非同步系統的 SLO 實戰能力建構。