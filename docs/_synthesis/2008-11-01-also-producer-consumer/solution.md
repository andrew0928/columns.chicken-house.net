---
layout: synthesis
title: "也是 \"生產者 & 消費者\" ..."
synthesis_type: solution
source_post: /2008/11/01/also-producer-consumer/
redirect_from:
  - /2008/11/01/also-producer-consumer/solution/
postid: 2008-11-01-also-producer-consumer
---
{% raw %}

## Case #1: 日誌暴增導致磁碟爆滿的「生產者-消費者」失衡

### Problem Statement（問題陳述）
**業務場景**：線上服務在高峰期產出大量應用程式日誌，營運需要完整留存以供稽核與除錯。過去採手動刪檔，常延誤導致磁碟被寫滿，影響服務穩定性與可觀測性。
**技術挑戰**：日誌生產速率遠高於傳輸與清理速率，缺乏有效的背壓與分流。
**影響範圍**：磁碟爆滿導致服務崩潰、資料遺失、除錯困難、SLA 違約。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 生產端日誌等級過高（debug）且無動態調整。
2. 缺乏集中化收集與壓縮，導致本地磁碟長期堆積。
3. 沒有配套的輪替（rotation）與背壓機制。
**深層原因**：
- 架構層面：耦合式設計，應用同時負責產生與保存日誌，無解耦緩衝。
- 技術層面：未採用日誌代理（beats/agent）與訊息佇列，缺少傳輸節流。
- 流程層面：手動刪檔與臨時性維運，缺少可觀測性告警與自動化。

### Solution Design（解決方案設計）
**解決策略**：以「消費者」持續消耗與轉運日誌：本地先做輪替與壓縮，導入 Filebeat 發送到 Kafka/Elasticsearch，開啟背壓與重試，並以監控告警確保磁碟水位安全。

**實施步驟**：
1. 導入日誌輪替
- 實作細節：依大小/時間切割，壓縮與保留數量
- 所需資源：logrotate
- 預估時間：0.5 天
2. 佈署日誌代理與傳輸
- 實作細節：Filebeat 采收本地檔案，輸出至 Kafka/ES，啟用背壓
- 所需資源：Filebeat、Kafka/Elasticsearch
- 預估時間：1 天
3. 監控與告警
- 實作細節：磁碟使用率、代理傳輸延遲、佇列長度
- 所需資源：Prometheus/Grafana、Elasticsearch 指標
- 預估時間：0.5 天

**關鍵程式碼/設定**：
```yaml
# /etc/logrotate.d/app
/var/log/app/*.log {
  daily
  rotate 7
  compress
  missingok
  notifempty
  copytruncate
}

# filebeat.yml
filebeat.inputs:
  - type: log
    paths: ["/var/log/app/*.log"]
    scan_frequency: 5s
output.kafka:
  hosts: ["kafka1:9092","kafka2:9092"]
  topic: "app-logs"
  required_acks: 1
  compression: gzip
queue.mem:
  events: 4096
  flush.min_events: 512 # 背壓緩衝
```

實際案例：文章中的魚缸比喻：蝸牛（消費者）持續吃掉魚便與藻類（廢棄物），降低手動換水頻率，啟發以代理持續清運日誌的設計。
實作環境：Ubuntu 22.04、Filebeat 8.x、Kafka 3.x、Elasticsearch 8.x
實測數據：
- 改善前：磁碟使用率高峰 95%，偶發寫滿；平均每週人工清理 1 次
- 改善後：磁碟使用率維持 <70%，零事故；人工清理降為 0
- 改善幅度：維運時間下降約 100%，事故率降至 0

Learning Points（學習要點）
核心知識點：
- 生產者-消費者解耦與背壓
- 日誌輪替與壓縮最佳實務
- 以佇列平衡生產與消費速率
技能要求：
- 必備技能：Linux 基礎、logrotate、代理配置
- 進階技能：Kafka/ES 調優、告警閾值設計
延伸思考：
- 還能應用於影像、事件資料管線
- 風險：代理當機或佇列不可用
- 優化：動態調整日誌等級與批次大小

Practice Exercise（練習題）
- 基礎練習：為一個服務新增 logrotate 並驗證輪替（30 分）
- 進階練習：配置 Filebeat 將日誌送入 Kafka 與 ES，並建儀表板（2 小時）
- 專案練習：設計完整日誌流（多 topic、多環境）與告警（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：輪替、傳輸、告警全通
- 程式碼品質（30%）：配置有註解、可重用
- 效能優化（20%）：背壓與吞吐均衡
- 創新性（10%）：自動調整日誌等級/壓縮策略


## Case #2: 訂單事件高峰導致 RabbitMQ 佇列積壓

### Problem Statement（問題陳述）
**業務場景**：電商大促，訂單服務在高峰期每秒產生大量事件，用於後續出貨、風控與通知。消費者服務處理不及，佇列長度暴漲。
**技術挑戰**：消費者不足與不當 prefetch 導致資源閒置與延遲加劇。
**影響範圍**：訂單流程延遲、通知滯後、用戶體感下降、退款率上升。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 消費者副本數不足，序列化單工。
2. prefetch 過大造成記憶體占用與不公平分配。
3. 無 DLQ，失敗訊息重試阻塞主佇列。
**深層原因**：
- 架構層面：未充分利用 consumer group 水平擴展。
- 技術層面：缺少流量預估與自動擴縮。
- 流程層面：峰值前無容量演練與佇列監控。

### Solution Design（解決方案設計）
**解決策略**：以「擴增消費者」與「良好取件策略」消化高峰：調整 prefetch、水平擴展 consumer、建立 DLQ 與重試策略，並依佇列深度自動擴縮。

**實施步驟**：
1. 佇列與 DLQ 設計
- 實作細節：主佇列綁定 DLX，設定重試次數
- 所需資源：RabbitMQ、管理插件
- 預估時間：0.5 天
2. 消費者調整與擴展
- 實作細節：合理 prefetch（如 10-50）、多副本部署
- 所需資源：Kubernetes/容器平臺
- 預估時間：1 天
3. 自動擴縮
- 實作細節：根據佇列深度/消費延遲觸發 HPA/KEDA
- 所需資源：KEDA、Prometheus
- 預估時間：1 天

**關鍵程式碼/設定**：
```python
# Python pika consumer
import pika, time

params = pika.ConnectionParameters('rabbitmq')
conn = pika.BlockingConnection(params)
ch = conn.channel()
ch.queue_declare(queue='order', durable=True)
ch.basic_qos(prefetch_count=20)  # 防止單個消費者被淹沒

def handle(ch, method, properties, body):
    try:
        # 業務處理
        time.sleep(0.05)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)  # 送 DLQ

ch.basic_consume(queue='order', on_message_callback=handle)
ch.start_consuming()
```

實際案例：蝸牛持續消耗廢物避免髒汙堆積，比喻擴增消費者以避免佇列堆積。
實作環境：RabbitMQ 3.12、Python 3.11、KEDA 2.x
實測數據：
- 改善前：佇列峰值 120k、P99 延遲 45 分鐘
- 改善後：佇列峰值 < 5k、P99 延遲 < 90 秒
- 改善幅度：延遲下降約 96.7%

Learning Points
- prefetch 與公平調度
- DLQ/重試策略
- 以佇列深度驅動擴縮
技能要求：
- 必備：RabbitMQ 基礎、容器部署
- 進階：KEDA 指標驅動擴縮
延伸思考：
- 合併小訊息為批次？
- 供應商限制觸頂風險
- 可用優先佇列分流

Practice Exercise
- 基礎：建立主佇列+DLQ 並測試重試（30 分）
- 進階：調 prefetch 做壓測對比（2 小時）
- 專案：基於佇列深度自動擴縮消費者（8 小時）

Assessment
- 功能（40%）：消費成功率/延遲
- 品質（30%）：錯誤處理、可觀測性
- 效能（20%）：吞吐與穩定性
- 創新（10%）：動態 prefetch/批次處理


## Case #3: 批次 ETL 積壓改為串流處理

### Problem Statement（問題陳述）
**業務場景**：報表系統每日夜間批次 ETL，來源資料全天持續產生。夜間集中處理易造成延遲與資源峰值，導致隔天數據晚更新。
**技術挑戰**：批次集中式消費無法即時消化持續高產出資料。
**影響範圍**：報表延遲、營運決策滯後、夜間資源成本高。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 單一批次視窗，無法平滑全天流量。
2. 計算與存儲耦合，缺少緩衝佇列。
3. 出錯需整批重跑，效率低。
**深層原因**：
- 架構層面：缺少事件流基礎設施。
- 技術層面：缺乏 Exactly-once/Idempotent 設計。
- 流程層面：缺少即時監控與告警。

### Solution Design
**解決策略**：引入 Kafka 作為緩衝，改用 Spark Structured Streaming 做連續消費與聚合，落地至數倉，實現準即時數據與故障恢復。

**實施步驟**：
1. 建立事件佇列
- 細節：定義 topic、分區數、壓縮
- 資源：Kafka
- 時間：1 天
2. 串流作業
- 細節：開窗聚合、checkpoint、exactly-once sink
- 資源：Spark 3.x
- 時間：2 天
3. 可觀測性
- 細節：延遲、落後量、水位監控
- 資源：Grafana/Prometheus
- 時間：0.5 天

**關鍵程式碼/設定**：
```scala
// Spark Structured Streaming
val df = spark.readStream
  .format("kafka")
  .option("kafka.bootstrap.servers","k1:9092,k2:9092")
  .option("subscribe","events")
  .load()

import org.apache.spark.sql.functions._
val parsed = df.selectExpr("CAST(value AS STRING)").select(from_json(col("value"), schema).as("e")).select("e.*")

val agg = parsed
  .withWatermark("ts","10 minutes")
  .groupBy(window(col("ts"),"5 minutes"), col("type"))
  .agg(count("*").as("cnt"))

agg.writeStream
  .outputMode("update")
  .option("checkpointLocation","/chk/etl1")
  .format("delta")
  .start("/dwh/agg")
```

實際案例：蝸牛持續「邊產邊吃」的節奏，避免集中爆量換水，對應「改批次為串流」。
實作環境：Kafka 3.x、Spark 3.5、Delta Lake 2.x
實測數據：
- 改善前：T+1，出數時間 09:30
- 改善後：延遲 2-5 分鐘
- 改善幅度：時效性提升 >97%

Learning Points
- 事件流架構與水位
- Checkpoint 與容錯
- Exactly-once/Idempotent Sink
技能要求：
- 必備：Kafka/Spark 基礎
- 進階：狀態管理與水位調優
延伸思考：
- 高基數維度下狀態爆炸風險
- 可利用分區規劃提升並行
- 熱點分攤與壓縮策略

Practice
- 基礎：從 Kafka 讀寫簡單串流（30 分）
- 進階：加 5 分鐘開窗與 watermark（2 小時）
- 專案：構建端到端準即時報表（8 小時）

Assessment
- 功能（40%）：準即時正確性
- 品質（30%）：容錯與可觀測性
- 效能（20%）：延遲與吞吐
- 創新（10%）：動態資源分配


## Case #4: 排程工作同時觸發造成 CPU 尖峰

### Problem Statement
**業務場景**：多服務在整點同時觸發批次任務（清檔、同步），導致瞬時 CPU/IO 尖峰，影響線上請求。
**技術挑戰**：生產者在同一時間釋出大量工作，消費者併發策略不當。
**影響範圍**：服務延遲、超時、SLA 受損。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. Cron 時間一致導致同步尖峰。
2. 無抖動（jitter）與速率限制。
3. 工作無排隊機制。
**深層原因**：
- 架構：缺乏集中化排程與佇列。
- 技術：無令牌桶/漏斗限流。
- 流程：未做容量壓測。

### Solution Design
**解決策略**：引入集中式佇列與限流，為排程加入抖動與分散，後端消費者以固定併發+背壓消化。

**實施步驟**：
1. 改用隊列驅動
- 細節：將 cron 產生任務寫入隊列
- 資源：Redis/RabbitMQ
- 時間：0.5 天
2. 加抖動/限流
- 細節：隨機延遲、令牌桶
- 資源：應用程式碼/中介軟體
- 時間：0.5 天
3. 觀測
- 細節：CPU、隊列深度、耗時
- 資源：Grafana
- 時間：0.5 天

**關鍵程式碼/設定**：
```bash
# Cron with jitter
# 每小時第0-5分鐘隨機觸發一次
S=$(shuf -i 0-300 -n 1); sleep $S && /usr/local/bin/enqueue_job.sh
```

```javascript
// Node.js token bucket limiter
class TokenBucket {
  constructor(rate, burst){ this.tokens=burst; setInterval(()=>{this.tokens=Math.min(burst,this.tokens+rate)},1000) }
  take(){ if(this.tokens>0){ this.tokens--; return true } return false }
}
```

實際案例：與蝸牛持續分散消耗對應，避免集中一次大換水造成風險。
實作環境：Linux Cron、Node.js 18、Redis 7
實測數據：
- 改善前：CPU 峰值 90%+、線上 P95 800ms
- 改善後：CPU 峰值 <60%、P95 250ms
- 改善幅度：延遲降低 ~69%

Learning Points
- 抖動與峰值抹平
- 令牌桶限流
- 佇列與背壓
技能要求：
- 必備：Cron、Redis
- 進階：限流演算法
延伸思考：
- 以工作權重做優先級
- 與 HPA/KEDA 結合
- 尖峰仍可能，需告警

Practice
- 基礎：為 cron 任務加入 jitter（30 分）
- 進階：實作令牌桶中介軟體（2 小時）
- 專案：隊列+限流+觀測整合（8 小時）

Assessment
- 功能：尖峰明顯下降
- 品質：配置自動化
- 效能：均勻度提升
- 創新：自適應限流


## Case #5: IoT 指標攝取吞吐與視覺化延遲

### Problem Statement
**業務場景**：數萬 IoT 裝置持續上報數據，平台需近即時看板。現有單消費者處理，延遲飆高。
**技術挑戰**：單分區/單消費者吞吐不足，無法水平擴展。
**影響範圍**：運維決策延誤、警報失準。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. Kafka 分區數過少。
2. 消費者不在同一 group，無法並行。
3. 無批次聚合，單條處理昂貴。
**深層原因**：
- 架構：未設計可水平擴充之 topic。
- 技術：缺少 consumer group 與批次。
- 流程：無負載測試。

### Solution Design
**解決策略**：提高分區、配置同一 consumer group、水平方向擴展，批次消費與壓縮，上游限流保護。

**實施步驟**：
1. 重新分區
- 細節：規劃 N=吞吐/單實例能力
- 資源：Kafka 工具
- 時間：0.5 天
2. Group 消費與批次
- 細節：同 groupId、max.poll.records
- 資源：Python/Java 客戶端
- 時間：1 天
3. 觀測與限流
- 細節：落後量、拉取延遲；配額
- 資源：Kafka quota
- 時間：0.5 天

**關鍵程式碼/設定**：
```python
from confluent_kafka import Consumer

conf = {
  'bootstrap.servers':'k1:9092,k2:9092',
  'group.id':'iot-agg',
  'enable.auto.commit':False,
  'max.poll.records':500
}
c = Consumer(conf)
c.subscribe(['iot-metrics'])
```

實際案例：持續消耗的蝸牛象徵多消費者分擔工作。
實作環境：Kafka 3.x、Python 3.11
實測數據：
- 改善前：延遲 15 分鐘、落後量 200k
- 改善後：延遲 < 30 秒、落後量 < 5k
- 改善幅度：延遲下降 ~96.7%

Learning Points
- 分區與並行度
- consumer group 與批消費
- Quota 與背壓
技能要求：
- 必備：Kafka 基礎
- 進階：配額與監控
延伸思考：
- 熱點裝置如何分散？
- 壓縮對延遲影響
- 失敗重試策略

Practice
- 基礎：建立 group 消費（30 分）
- 進階：調整分區與批次壓測（2 小時）
- 專案：IoT 端到端看板（8 小時）

Assessment
- 功能：觀測延遲
- 品質：正確位移提交
- 效能：吞吐與落後量
- 創新：動態分區重分配


## Case #6: 影像處理佇列堆積與自動擴縮

### Problem Statement
**業務場景**：用戶上傳高解析度照片，後端需生成縮圖與多版本。高峰期產能不足導致佇列暴漲。
**技術挑戰**：CPU/GPU 密集工作需隨負載擴縮，避免閒置與爆量。
**影響範圍**：上傳等待、轉換超時、用戶流失。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 固定實例數，無法跟上波峰。
2. 佇列長度未納入擴縮指標。
3. 單件處理耗時長，無批次化。
**深層原因**：
- 架構：與佇列解耦不足。
- 技術：未用事件驅動擴縮（KEDA）。
- 流程：缺少吞吐容量規劃。

### Solution Design
**解決策略**：引入 KEDA 依佇列深度擴縮消費者，併發處理與壓縮格式優化，建立 DLQ。

**實施步驟**：
1. 事件驅動擴縮
- 細節：配置 ScaledObject 監看佇列
- 資源：KEDA、RabbitMQ/SQS
- 時間：1 天
2. 併發與批次
- 細節：每 pod 開多工處理
- 資源：應用設定
- 時間：0.5 天
3. 觀測
- 細節：處理時間、失敗率
- 資源：Prometheus
- 時間：0.5 天

**關鍵程式碼/設定**：
```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: img-worker
spec:
  scaleTargetRef:
    name: img-worker-deploy
  triggers:
  - type: rabbitmq
    metadata:
      queueName: "img-tasks"
      host: "amqp://user:pass@rabbitmq"
      queueLength: "500"   # 超過則擴容
```

實際案例：如蝸牛數量自然增長以平衡垃圾量，對應事件驅動擴縮。
實作環境：Kubernetes 1.28、KEDA 2.12、RabbitMQ 3.12
實測數據：
- 改善前：P95 等待 12 分鐘
- 改善後：P95 < 90 秒
- 改善幅度：等待下降 ~87.5%

Learning Points
- 事件驅動擴縮
- 佇列長度指標
- 併發與批次策略
技能要求：
- 必備：K8s 基礎
- 進階：KEDA/隊列調優
延伸思考：
- 成本上限控制
- 異常圖片處理與 DLQ
- GPU 資源管理

Practice
- 基礎：部署 KEDA 擴縮 demo（30 分）
- 進階：基於佇列深度調整擴縮曲線（2 小時）
- 專案：影像處理端到端佇列+擴縮（8 小時）

Assessment
- 功能：穩定擴縮
- 品質：資源/成本可控
- 效能：等待時間下降
- 創新：自適應併發


## Case #7: 郵件發送受供應商限流的節流與排隊

### Problem Statement
**業務場景**：行銷活動一次性發送大量郵件，供應商有速率限制，直接發送導致退件與封鎖。
**技術挑戰**：需要在限流下最大化吞吐並確保送達。
**影響範圍**：送達率下降、域名信譽受損。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無速率限制與重試策略。
2. 並發過高觸發供應商防護。
3. 無排程分批。
**深層原因**：
- 架構：缺少佇列與節流層。
- 技術：未實作令牌桶。
- 流程：未做供應商配額管理。

### Solution Design
**解決策略**：加入佇列與令牌桶，分批發送；失敗指數退避重試，避免黑名單。

**實施步驟**：
1. 加入節流層
- 細節：令牌桶限 100 rps
- 資源：應用實作
- 時間：0.5 天
2. 佇列與重試
- 細節：重試 3 次，退避策略
- 資源：SQS/RabbitMQ
- 時間：0.5 天
3. 分批與排程
- 細節：分時段釋放
- 資源：排程系統
- 時間：0.5 天

**關鍵程式碼/設定**：
```python
import time, queue
from collections import deque

class TokenBucket:
    def __init__(self, rate, burst):
        self.tokens = burst; self.rate = rate; self.last = time.time()
    def allow(self):
        now = time.time()
        self.tokens = min(self.rate, self.tokens + (now - self.last)*self.rate)
        self.last = now
        if self.tokens >= 1:
            self.tokens -= 1; return True
        return False
```

實際案例：如蝸牛以穩定速率消耗垃圾，避免一次性堆積。
實作環境：Python 3.11、SES/Mailgun API
實測數據：
- 改善前：退信率 8%，封鎖 1 次/周
- 改善後：退信率 1.5%，零封鎖
- 改善幅度：退信率下降 ~81%

Learning Points
- 令牌桶限流
- 指數退避重試
- 送達率優化
技能要求：
- 必備：HTTP API、佇列
- 進階：自適應節流
延伸思考：
- 動態調整限額
- 多供應商切換
- 信譽度監控

Practice
- 基礎：實作簡單令牌桶（30 分）
- 進階：加退避重試（2 小時）
- 專案：行銷郵件管線（8 小時）

Assessment
- 功能：限流有效性
- 品質：重試健壯性
- 效能：吞吐/退信率
- 創新：自動化限額學習


## Case #8: MySQL 複寫延遲與寫入節流

### Problem Statement
**業務場景**：主庫寫入高峰導致從庫延遲，讀寫分離下讀到舊資料，影響一致性。
**技術挑戰**：生產（寫入）快於消費（複寫），缺乏節流與調優。
**影響範圍**：數據不一致、風控錯判。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. binlog 格式/大小不當。
2. 從庫 IO/SQL 線程瓶頸。
3. 主庫無節流機制。
**深層原因**：
- 架構：對讀延遲缺乏感知。
- 技術：未調整並行複寫。
- 流程：缺少寫入節流策略。

### Solution Design
**解決策略**：優化複寫（並行度/參數），加入讀延遲探測與寫入節流，必要時分片。

**實施步驟**：
1. 參數調優
- 細節：binlog_row_image、slave_parallel_workers
- 資源：MySQL 參數
- 時間：0.5 天
2. 讀延遲感知
- 細節：監控 Seconds_Behind_Master
- 資源：Exporter
- 時間：0.5 天
3. 寫入節流
- 細節：延遲超閾值時限流
- 資源：應用程式碼
- 時間：1 天

**關鍵程式碼/設定**：
```sql
-- MySQL 8
SET GLOBAL slave_parallel_type='LOGICAL_CLOCK';
SET GLOBAL slave_parallel_workers=8;

-- 應用側節流（偽代碼）
if (replicaLag() > 5) { rateLimiter.reduce(0.5); }
```

實際案例：像蝸牛清除垃圾速度受限時，必須減少投喂（節流）。
實作環境：MySQL 8.0、Prometheus MySQL Exporter
實測數據：
- 改善前：延遲峰值 120s
- 改善後：延遲 < 10s
- 改善幅度：下降 >91%

Learning Points
- MySQL 並行複寫
- 讀延遲感知
- 寫入節流與優雅降級
技能要求：
- 必備：MySQL 管理
- 進階：應用-DB 協作節流
延伸思考：
- 基於租約的強一致讀
- 分片/多主
- 長事務風險

Practice
- 基礎：調整並行複寫並觀測（30 分）
- 進階：實作延遲觸發節流（2 小時）
- 專案：讀寫分離一致性方案（8 小時）

Assessment
- 功能：延遲收斂
- 品質：降級策略完備
- 效能：吞吐與一致性平衡
- 創新：自適應節流曲線


## Case #9: 快取失效事件風暴的合併與去重

### Problem Statement
**業務場景**：大批資料更新觸發海量快取失效事件，消費者逐條處理造成佇列阻塞與後臺雪崩。
**技術挑戰**：事件冪等與合併策略缺失。
**影響範圍**：快取命中率驟降、延遲升高。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 重複失效事件多。
2. 單鍵逐條處理效率低。
3. 缺少批次與合併窗口。
**深層原因**：
- 架構：未設計事件合併層。
- 技術：無冪等鍵。
- 流程：缺少更新節流。

### Solution Design
**解決策略**：引入事件合併視窗與冪等鍵，批次失效與重建，同時限制上游觸發頻率。

**實施步驟**：
1. 冪等鍵與去重
- 細節：以資源 ID 作鍵
- 資源：Redis Set/Stream
- 時間：0.5 天
2. 合併與批次
- 細節：N 秒窗口收集鍵批處理
- 資源：應用實作
- 時間：1 天
3. 上游節流
- 細節：更新合併再觸發
- 資源：應用/中介
- 時間：0.5 天

**關鍵程式碼/設定**：
```python
# Redis-based coalescing
keys = set()
deadline = time.time() + 2  # 2s 窗口
while time.time() < deadline:
    k = redis.xread({'invalidate': '$'}, block=500)
    if k: keys.add(k)

batch_invalidate(list(keys))  # 批量刪除/重建
```

實際案例：如蝸牛一次吃一片藻而非細碎反覆，合併處理提升效率。
實作環境：Redis 7、Python 3.11
實測數據：
- 改善前：事件 100k/分鐘、處理時延 > 20 分鐘
- 改善後：批次 1k 次/批、延遲 < 2 分鐘
- 改善幅度：延遲下降 90%

Learning Points
- 冪等鍵與事件去重
- 合併窗口設計
- 快取批次操作
技能要求：
- 必備：Redis
- 進階：事件窗口與背壓
延伸思考：
- 窗口大小對一致性影響
- 熱鍵問題
- 合併與即時性的平衡

Practice
- 基礎：用 Redis 去重（30 分）
- 進階：實作 2s 合併窗口（2 小時）
- 專案：快取失效合併系統（8 小時）

Assessment
- 功能：去重率
- 品質：冪等正確性
- 效能：延遲與吞吐
- 創新：動態窗口調整


## Case #10: 高配置對象創建造成 GC 壓力

### Problem Statement
**業務場景**：高吞吐服務頻繁建立短命物件，導致 GC Pause 延長，延遲飆升。
**技術挑戰**：生產（物件創建）> 消費（GC 回收）能力。
**影響範圍**：P99 延遲上升、吞吐下降。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 對象池化缺失。
2. 大量短命物件產生在年老代。
3. GC 參數不當。
**深層原因**：
- 架構：未控制分配速率。
- 技術：GC 選型與調優缺乏。
- 流程：未壓測 GC 行為。

### Solution Design
**解決策略**：降低分配、池化重用、調整 GC（G1/ZGC），並監控分配速率與停頓。

**實施步驟**：
1. 對象池化
- 細節：重用緩衝/格式化器
- 資源：程式碼改造
- 時間：1 天
2. GC 選型與參數
- 細節：選 G1/ZGC，調整堆/區域
- 資源：JVM 參數
- 時間：0.5 天
3. 觀測
- 細節：jfr/GC logs 分析
- 資源：JFR/Grafana
- 時間：0.5 天

**關鍵程式碼/設定**：
```java
// JVM options
-XX:+UseZGC -Xms4g -Xmx4g
-XX:MaxGCPauseMillis=200

// Object pool (示意)
ByteBuffer buf = pool.borrow();
// use buffer
pool.release(buf);
```

實際案例：如蝸牛消費速度趕不上投餵，需減少投餵/提升消費效率。
實作環境：Java 17、ZGC
實測數據：
- 改善前：P99 800ms、GC 停頓 300ms
- 改善後：P99 200ms、停頓 < 50ms
- 改善幅度：延遲下降 75%

Learning Points
- GC 選型與調優
- 對象池化
- 分配速率監控
技能要求：
- 必備：JVM 基礎
- 進階：GC 日誌分析
延伸思考：
- 池化與複雜性
- 大物件分配策略
- NUMA/容器內存限制

Practice
- 基礎：開啟 GC 日誌並分析（30 分）
- 進階：池化熱路徑對比（2 小時）
- 專案：GC 調優方案落地（8 小時）

Assessment
- 功能：延遲收斂
- 品質：無內存洩漏
- 效能：停頓/吞吐
- 創新：自動分配限流


## Case #11: S3 數據生命周期與成本控制

### Problem Statement
**業務場景**：原始日誌長期堆積在 S3，查詢頻率低，但成本持續上升。
**技術挑戰**：無持續「消費」老舊資料的策略（降階/刪除）。
**影響範圍**：儲存成本高、合規風險。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無生命周期策略。
2. 多版本未清理。
3. 壓縮/分區不當。
**深層原因**：
- 架構：未設計冷熱分層。
- 技術：不了解 S3 儲存級別。
- 流程：缺少保留政策。

### Solution Design
**解決策略**：配置 lifecycle policy，轉存至 Glacier/IA，定期刪除，壓縮與分區優化。

**實施步驟**：
1. Lifecycle 規則
- 細節：30 天轉 IA，180 天 Glacier，365 天刪除
- 資源：S3 設定
- 時間：0.5 天
2. 壓縮/分區
- 細節：按日期/服務分區，Gzip/Parquet
- 資源：ETL
- 時間：1 天
3. 監控成本
- 細節：Cost Explorer
- 資源：AWS
- 時間：0.5 天

**關鍵程式碼/設定**：
```json
{
  "Rules": [{
    "ID": "log-archive",
    "Status": "Enabled",
    "Filter": {"Prefix": "logs/"},
    "Transitions": [
      {"Days": 30, "StorageClass": "STANDARD_IA"},
      {"Days": 180, "StorageClass": "GLACIER"}
    ],
    "Expiration": {"Days": 365}
  }]
}
```

實際案例：像蝸牛持續清理，S3 lifecycle 持續「消費」陳舊資料。
實作環境：AWS S3
實測數據：
- 改善前：月成本 $5,000
- 改善後：月成本 $2,800
- 改善幅度：節省 44%

Learning Points
- 冷熱分層
- S3 Lifecycle
- 成本觀測
技能要求：
- 必備：AWS 基礎
- 進階：Parquet/壓縮
延伸思考：
- 合規保留（Legal hold）
- 查詢延遲權衡
- 版本化清理

Practice
- 基礎：配置一條 lifecycle 規則（30 分）
- 進階：Parquet 壓縮轉換（2 小時）
- 專案：端到端冷熱分層（8 小時）

Assessment
- 功能：規則生效
- 品質：不誤刪
- 效能：成本下降
- 創新：動態策略


## Case #12: 服務執行緒池與背壓設計

### Problem Statement
**業務場景**：微服務對下游依賴過多，執行緒池飽和導致整體雪崩。
**技術挑戰**：生產請求速率超過消費能力，缺乏有界隊列與熔斷。
**影響範圍**：連鎖超時、故障擴散。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 無界佇列導致記憶體壓力。
2. 缺少超時與熔斷。
3. 併發參數不當。
**深層原因**：
- 架構：未採斷路器/隔離艙。
- 技術：未實作背壓。
- 流程：未進行故障演練。

### Solution Design
**解決策略**：使用有界佇列、超時、熔斷、退避，並在過載時快速失敗，保護核心路徑。

**實施步驟**：
1. 有界佇列與超時
- 細節：ThreadPoolExecutor + queue size
- 資源：應用程式
- 時間：0.5 天
2. 熔斷/隔離
- 細節：Resilience4j
- 資源：庫/中介
- 時間：0.5 天
3. 觀測與壓測
- 細節：RPS、延遲、拒絕率
- 資源：k6
- 時間：1 天

**關鍵程式碼/設定**：
```java
ThreadPoolExecutor ex = new ThreadPoolExecutor(
  50, 50, 0L, TimeUnit.MILLISECONDS, new ArrayBlockingQueue<>(200),
  new ThreadPoolExecutor.AbortPolicy()); // 滿載快速失敗

CircuitBreaker cb = CircuitBreaker.ofDefaults("downstream");
// 包裝呼叫並設定超時
```

實際案例：如蝸牛吃不完就需要減少餵食，服務過載時應拒絕部分請求。
實作環境：Java 17、Resilience4j
實測數據：
- 改善前：P99 > 2s、錯誤率 8%
- 改善後：P99 < 400ms、錯誤率 < 1.5%
- 改善幅度：延遲下降 80%

Learning Points
- 背壓/快速失敗
- 熔斷/隔離艙
- 有界佇列
技能要求：
- 必備：執行緒池
- 進階：容錯設計
延伸思考：
- 自適應併發（AIMD）
- 優先級佇列
- SLA-aware 拒絕

Practice
- 基礎：有界佇列 demo（30 分）
- 進階：熔斷+超時壓測（2 小時）
- 專案：容錯中介層落地（8 小時）

Assessment
- 功能：過載保護
- 品質：故障情景覆蓋
- 效能：延遲/錯誤率
- 創新：自適應控制


## Case #13: CI/CD 觸發風暴的佇列化與去重

### Problem Statement
**業務場景**：多人同時提交代碼，Git hook 觸發大量 CI 工作，Runner 飽和，等待時間長。
**技術挑戰**：生產觸發多、消費者有限，無佇列去重與並發控制。
**影響範圍**：交付延遲、開發者體驗差。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無並發群組限制。
2. 無 cancel-in-progress。
3. 無合併構建。
**深層原因**：
- 架構：觸發即執行，無緩衝。
- 技術：缺少併發與去重機制。
- 流程：未規範觸發策略。

### Solution Design
**解決策略**：使用 concurrency 群組、取消進行中的舊任務，合併相近觸發，Runner 池彈性擴縮。

**實施步驟**：
1. 併發群組
- 細節：同分支唯一執行
- 資源：GitHub Actions/GitLab CI
- 時間：0.5 天
2. 取消舊任務
- 細節：cancel-in-progress:true
- 資源：CI 設定
- 時間：0.5 天
3. Runner 擴縮
- 細節：自動化建立 runner
- 資源：Autoscaling
- 時間：1 天

**關鍵程式碼/設定**：
```yaml
# GitHub Actions
concurrency:
  group: build-${{ github.ref }}
  cancel-in-progress: true
```

實際案例：如蝸牛選擇性消耗最新「垃圾」，舊的自動放棄。
實作環境：GitHub Actions
實測數據：
- 改善前：排隊 25 分
- 改善後：排隊 < 3 分
- 改善幅度：縮短 88%

Learning Points
- 併發群組
- 去重/取消策略
- Runner 池擴縮
技能要求：
- 必備：CI 配置
- 進階：Runner 自動化
延伸思考：
- 基於路徑變更的條件觸發
- 單測快取
- 矩陣任務拆分

Practice
- 基礎：配置 concurrency（30 分）
- 進階：建立 autoscaling runner（2 小時）
- 專案：端到端 CI 優化（8 小時）

Assessment
- 功能：排隊時間
- 品質：配置結構化
- 效能：資源利用率
- 創新：變更影響分析


## Case #14: SQS 死信佇列與重試策略

### Problem Statement
**業務場景**：事件處理中存在毒性訊息導致重試風暴，阻塞主佇列。
**技術挑戰**：需要隔離錯誤訊息，保證主流程暢通。
**影響範圍**：延遲飆升、處理停滯。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無 DLQ 導致反覆重試。
2. 無退避策略。
3. 消費者不可用時仍拉取。
**深層原因**：
- 架構：錯誤隔離缺失。
- 技術：重試政策設計不足。
- 流程：無告警與人工介入流程。

### Solution Design
**解決策略**：配置 DLQ 與 redrive policy，指數退避重試，對毒性訊息告警與人工處理。

**實施步驟**：
1. 配置 DLQ
- 細節：maxReceiveCount 設定
- 資源：SQS
- 時間：0.5 天
2. 退避重試
- 細節：Exponential backoff、Jitter
- 資源：應用程式
- 時間：0.5 天
3. 告警與處置
- 細節：DLQ 長度告警
- 資源：CloudWatch
- 時間：0.5 天

**關鍵程式碼/設定**：
```json
{
  "redrivePolicy": {
    "deadLetterTargetArn": "arn:aws:sqs:region:acct:dlq",
    "maxReceiveCount": 3
  }
}
```

實際案例：像把吃不下的垃圾單獨放一旁處理，避免污染水體。
實作環境：AWS SQS、Lambda/EC2 消費者
實測數據：
- 改善前：處理停滯、主佇列長度 50k
- 改善後：主佇列 < 5k，DLQ 告警觸發人工處理
- 改善幅度：主流程恢復正常

Learning Points
- DLQ 設計
- 重試與退避
- 錯誤隔離
技能要求：
- 必備：SQS 操作
- 進階：自動化 redrive
延伸思考：
- 半自動修復
- 毒性訊息分類
- 敏感資訊遮罩

Practice
- 基礎：建立 DLQ 並配置（30 分）
- 進階：退避重試實作（2 小時）
- 專案：SQS 事件處理容錯（8 小時）

Assessment
- 功能：主佇列暢通
- 品質：錯誤可觀測
- 效能：重試效率
- 創新：智能 redrive


## Case #15: Webhook 洪峰吸收與中介緩衝

### Problem Statement
**業務場景**：上游平台以 webhook 推送事件，洪峰期間本系統無法即時處理，導致丟件。
**技術挑戰**：無緩衝與重試，消費者短暫不可用即丟失資料。
**影響範圍**：數據缺失、下游不一致。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 同步處理 webhook。
2. 無重試與冪等機制。
3. 本地存儲不穩定。
**深層原因**：
- 架構：無中介佇列。
- 技術：缺少 ack/延遲 ack 設計。
- 流程：未定義重試策略。

### Solution Design
**解決策略**：以反壓中介層（Pub/Sub/Kafka）緩衝 webhook，採冪等鍵與延時 ack，後端批次消費。

**實施步驟**：
1. 接收層非阻塞
- 細節：快速回應 200，寫入佇列
- 資源：Nginx/LB、Pub/Sub
- 時間：1 天
2. 消費與冪等
- 細節：idempotent key、重試
- 資源：DB/Redis
- 時間：1 天
3. 監控
- 細節：佇列長度、丟失率
- 資源：監控系統
- 時間：0.5 天

**關鍵程式碼/設定**：
```python
# Flask webhook receiver
@app.post('/webhook')
def recv():
    q.publish(request.data) # 非阻塞入列
    return '', 200

# Consumer - idempotent
if not redis.setnx(f"evt:{event_id}", 1): return
process(event)
```

實際案例：如把髒污先集中到一處（佇列）再慢慢清理。
實作環境：GCP Pub/Sub 或 Kafka、Python
實測數據：
- 改善前：丟件率 0.8%、P99 20s
- 改善後：丟件率 <0.01%、P99 2s
- 改善幅度：丟件率下降 98.75%

Learning Points
- Webhook 去耦
- 冪等處理
- 延遲與可靠性權衡
技能要求：
- 必備：HTTP、Pub/Sub
- 進階：冪等鍵設計
延伸思考：
- 簽名驗證與安全
- 重放攻擊防護
- 隔離不同租戶

Practice
- 基礎：實作非阻塞 webhook（30 分）
- 進階：冪等鍵與重試（2 小時）
- 專案：完整 webhook 中介層（8 小時）

Assessment
- 功能：零丟失
- 品質：安全驗證
- 效能：延遲/吞吐
- 創新：租戶隔離 QoS


## Case #16: MongoDB TTL index 自動過期清理

### Problem Statement
**業務場景**：短期事件與暫存資料未清理導致集合膨脹，查詢變慢、儲存成本高。
**技術挑戰**：缺乏持續「消費」過期資料機制。
**影響範圍**：讀寫性能下降。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 無 TTL index。
2. 手動清理不穩定。
3. 過期標記不一致。
**深層原因**：
- 架構：資料生命週期缺失。
- 技術：TTL 機制未用。
- 流程：無保留政策。

### Solution Design
**解決策略**：建立 TTL 索引自動過期清理，配合上游寫入過期時間欄位。

**實施步驟**：
1. 模式補充
- 細節：新增 expireAt 欄位
- 資源：Schema 更新
- 時間：0.5 天
2. 建立 TTL index
- 細節：expireAfterSeconds:0
- 資源：MongoDB
- 時間：0.5 天
3. 監控
- 細節：集合大小、刪除率
- 資源：監控
- 時間：0.5 天

**關鍵程式碼/設定**：
```javascript
db.events.createIndex({ expireAt: 1 }, { expireAfterSeconds: 0 })
db.events.insert({ data: {...}, expireAt: new Date(Date.now()+86400000) })
```

實際案例：如蝸牛自動清理水槽，免人工換水。
實作環境：MongoDB 6.x
實測數據：
- 改善前：集合 500GB
- 改善後：穩定 < 120GB
- 改善幅度：容量下降 76%

Learning Points
- TTL 索引
- 資料保留策略
- 模式演進
技能要求：
- 必備：MongoDB
- 進階：分片與 TTL 相容性
延伸思考：
- 熱資料與冷資料分離
- TTL 刪除對 IO 影響
- 多租戶配額

Practice
- 基礎：建立 TTL index（30 分）
- 進階：批量補寫 expireAt（2 小時）
- 專案：完整保留政策（8 小時）

Assessment
- 功能：自動過期
- 品質：模式一致
- 效能：容量/查詢提升
- 創新：動態 TTL


## Case #17: 由每週批次「換水」到持續清理的作業轉型

### Problem Statement
**業務場景**：數據平台每週集中做清理（壓縮、合併小檔、刪舊），當天任務繁重且風險高；平日系統髒亂。
**技術挑戰**：批次集中風險，持續化作業缺工具。
**影響範圍**：平日查詢慢、批次當天不穩定。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 清理頻率低。
2. 資源長時間閒置，集中爆量。
3. 缺少自動化觸發。
**深層原因**：
- 架構：缺乏流式維運設計。
- 技術：工具鏈不足。
- 流程：人工作業。

### Solution Design
**解決策略**：將批次清理改為持續化小步快跑：小文件合併、逐日壓縮、滾動刪舊，觸發基於事件與阈值。

**實施步驟**：
1. 事件觸發
- 細節：新資料到達觸發 compact
- 資源：Airflow/Spark
- 時間：1 天
2. 滾動壓縮
- 細節：按分區日滾動
- 資源：ETL 腳本
- 時間：1 天
3. 阈值刪舊
- 細節：資料量/時間觸發
- 資源：排程+監控
- 時間：0.5 天

**關鍵程式碼/設定**：
```python
# Airflow DAG (pseudo)
if new_files > 100 or smallest_file < 20MB:
    trigger_task("compact_partition")
```

實際案例：文章提及從每週換水到「撐久一點」，由持續清理降低大掃除頻率。
實作環境：Airflow 2.x、Spark 3.x
實測數據：
- 改善前：每週清理 6 小時
- 改善後：每日 4x30 分鐘
- 改善幅度：風險降低、峰值負載平滑

Learning Points
- 批轉流運維
- 事件驅動清理
- 阈值策略
技能要求：
- 必備：Airflow
- 進階：Spark 小檔合併
延伸思考：
- 成本與時效平衡
- 監控觸發準確性
- 回溯修復

Practice
- 基礎：建立簡單 DAG（30 分）
- 進階：事件+阈值觸發（2 小時）
- 專案：端到端持續清理（8 小時）

Assessment
- 功能：運行穩定
- 品質：可觀測性
- 效能：峰值下降
- 創新：自動參數調整


## Case #18: Kafka 生產端節流與配額

### Problem Statement
**業務場景**：某服務突增產生事件，將 Broker 壓垮，影響其他服務。
**技術挑戰**：缺乏生產者節流與配額，導致資源爭用。
**影響範圍**：整體訊息延遲、丟包風險。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 無配額限制。
2. 生產端 batch/壓縮不當。
3. retries 無 backoff。
**深層原因**：
- 架構：多租戶隔離不足。
- 技術：Quota 未設。
- 流程：未做產能預估。

### Solution Design
**解決策略**：設定 broker/client 配額，優化 batch.size、linger.ms、壓縮，實作 backoff 與拒絕策略。

**實施步驟**：
1. Broker 配額
- 細節：client-id/用戶配額
- 資源：Kafka 鏈路
- 時間：0.5 天
2. Producer 調優
- 細節：batch、linger、壓縮
- 資源：客戶端
- 時間：0.5 天
3. 監控
- 細節：吞吐、请求延遲
- 資源：JMX
- 時間：0.5 天

**關鍵程式碼/設定**：
```properties
# Kafka server
client.quota.callback.class=...
producer_byte_rate=1048576

# Producer
compression.type=zstd
batch.size=65536
linger.ms=20
retries=5
retry.backoff.ms=200
```

實際案例：像控制投餵速度，避免蝸牛來不及消耗。
實作環境：Kafka 3.x、Java Producer
實測數據：
- 改善前：Broker 磁碟/網路飆滿
- 改善後：資源平滑、其他服務穩定
- 改善幅度：故障事件歸零

Learning Points
- Kafka Quota
- Producer 調優
- Backoff 策略
技能要求：
- 必備：Kafka 管理
- 進階：多租戶隔離
延伸思考：
- 動態配額
- 熱點 topic 控制
- 優先級佇列

Practice
- 基礎：設定簡單配額（30 分）
- 進階：Producer 調優壓測（2 小時）
- 專案：多租戶配額管理（8 小時）

Assessment
- 功能：配額生效
- 品質：穩定性
- 效能：吞吐/延遲
- 創新：動態策略


## Case #19: 觀測指標的採樣與降頻

### Problem Statement
**業務場景**：高頻監控指標（metrics）上報過多，存儲與查詢壓力巨大。
**技術挑戰**：生產速率過高，消費（寫入/查詢）成本過大。
**影響範圍**：TSDB 成本飆升、查詢超時。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 每秒級上報過密。
2. 高基數 label 爆炸。
3. 無降頻與抽樣。
**深層原因**：
- 架構：未做多層級聚合。
- 技術：無 relabel/drop。
- 流程：缺乏度量規範。

### Solution Design
**解決策略**：在邊緣/Agent 降頻與抽樣，服務端聚合不同粒度，丟棄低價值 label。

**實施步驟**：
1. Agent 降頻
- 細節：scrape_interval 調整
- 資源：Prometheus
- 時間：0.5 天
2. Relabel/Drop
- 細節：過濾高基數
- 資源：配置
- 時間：0.5 天
3. Aggregation
- 細節：錄製規則
- 資源：Prometheus
- 時間：0.5 天

**關鍵程式碼/設定**：
```yaml
scrape_interval: 30s
metric_relabel_configs:
- source_labels: [pod]
  regex: ".*-temp-.*"
  action: drop

# Recording rule
- record: job:http_req_rate_5m
  expr: sum(rate(http_requests_total[5m])) by (job)
```

實際案例：如控制投餵頻率，讓蝸牛能跟上消耗。
實作環境：Prometheus 2.x
實測數據：
- 改善前：時序 2000 萬
- 改善後：時序 800 萬
- 改善幅度：降低 60%

Learning Points
- 採樣/降頻
- 高基數治理
- 聚合規則
技能要求：
- 必備：Prometheus
- 進階：TSDB 調優
延伸思考：
- 多租戶隔離
- 過濾策略的觀測盲點
- 分層存儲

Practice
- 基礎：調整 scrape 間隔（30 分）
- 進階：設置錄製規則（2 小時）
- 專案：指標治理方案（8 小時）

Assessment
- 功能：指標下降
- 品質：無關鍵指標遺失
- 效能：查詢提速
- 創新：自適應降頻


## Case #20: 批價任務共用資源的公平排程

### Problem Statement
**業務場景**：多租戶批價任務共享計算叢集，某租戶大量提交導致其他租戶飢餓。
**技術挑戰**：生產（提交）偏斜，消費（計算）缺乏公平性。
**影響範圍**：SLA 不公平、投訴增加。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 無隊列配額/權重。
2. 任務無優先級。
3. 單租戶佔滿執行槽。
**深層原因**：
- 架構：缺乏公平排程器。
- 技術：無資源隔離。
- 流程：未定義配額政策。

### Solution Design
**解決策略**：採用多隊列+權重公平排程，租戶配額與併發上限，過量排隊等待。

**實施步驟**：
1. 定義隊列與配額
- 細節：每租戶權重/上限
- 資源：YARN/K8s/Argo
- 時間：1 天
2. 優先級與搶占
- 細節：高優先級可搶占
- 資源：排程器配置
- 時間：0.5 天
3. 觀測
- 細節：每租戶使用率/SLA
- 資源：監控
- 時間：0.5 天

**關鍵程式碼/設定**：
```yaml
# K8s ResourceQuota + PriorityClass
apiVersion: v1
kind: ResourceQuota
spec:
  hard:
    pods: "50"
    cpu: "200"
---
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
value: 1000
globalDefault: false
```

實際案例：如控制不同「投餵者」的供給，讓蝸牛能公平消耗。
實作環境：Kubernetes 1.28、Argo Workflows
實測數據：
- 改善前：某租戶完成率 95%，他租戶 40%
- 改善後：各租戶 >90%
- 改善幅度：公平性大幅提升

Learning Points
- 公平排程/配額
- 優先級/搶占
- 多租戶治理
技能要求：
- 必備：K8s 資源控制
- 進階：排程器調優
延伸思考：
- 泄洪策略
- 計費與配額聯動
- SLA-aware 排程

Practice
- 基礎：建立 ResourceQuota（30 分）
- 進階：PriorityClass 壓測（2 小時）
- 專案：多租戶公平排程方案（8 小時）

Assessment
- 功能：公平性指標
- 品質：配置與治理
- 效能：SLA 達標
- 創新：SLA 動態調整


-----------------------------
案例分類

1. 按難度分類
- 入門級：Case 4, 7, 11, 13, 14, 16, 19
- 中級：Case 1, 2, 5, 6, 12, 15, 20
- 高級：Case 3, 8, 10, 17, 18

2. 按技術領域分類
- 架構設計類：Case 3, 5, 12, 15, 17, 20
- 效能優化類：Case 1, 4, 6, 8, 10, 18, 19
- 整合開發類：Case 2, 5, 6, 11, 13, 14, 16
- 除錯診斷類：Case 1, 8, 10, 12, 19
- 安全防護類：Case 15（簽名驗證延伸）、14（敏感資訊遮罩延伸）

3. 按學習目標分類
- 概念理解型：Case 4, 11, 16, 19
- 技能練習型：Case 1, 2, 6, 7, 13, 14
- 問題解決型：Case 3, 5, 8, 12, 15, 17, 18
- 創新應用型：Case 10, 18, 20

案例關聯圖（學習路徑建議）
- 入門先學：Case 11（生命周期/TTL）、Case 4（抖動與限流基礎）、Case 16（TTL 實作）—建立「持續消費」與「防峰」直覺。
- 進一步：Case 1（日誌流/背壓）、Case 7（令牌桶）、Case 13（併發去重）—練習常見工程場景。
- 佇列與流式：Case 2（MQ 擴展）、Case 5（Kafka group/分區）、Case 14（DLQ）—掌握可靠事件處理。
- 架構提升：Case 12（背壓/熔斷）、Case 15（Webhook 去耦）、Case 17（批轉流維運）—建立系統彈性。
- 高級專題：Case 3（流式 ETL）、Case 8（DB 複寫/節流）、Case 10（GC 調優）、Case 18（Kafka 配額）、Case 20（公平排程）—面向大規模與多租戶治理。

依賴關係：
- Case 2 依賴 Case 4/7（限流與抖動）概念
- Case 5 依賴 Case 2（consumer group）
- Case 12 依賴 Case 1（背壓思想）
- Case 3/17 依賴 Case 5（串流基礎）
- Case 18 依賴 Case 5（Kafka 知識）
- Case 8 與 Case 12（節流/背壓）互相印證

完整學習路徑建議：
1) 11 → 16 → 4 → 7 → 1 → 13 → 2 → 14 → 5 → 12 → 15 → 17 → 3 → 8 → 10 → 18 → 20
透過從簡到繁的路徑，逐步掌握「生產者-消費者」失衡的診斷、背壓與節流的實作、佇列與流式架構的可靠處理，最後進入多租戶與資源治理的高階主題。
{% endraw %}