# 後端工程師必備: 排程任務的處理機制練習

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼一般 Web Application 架構不擅長「預約某個時間點執行任務」？
Web Application 先天採用 Request / Response 的被動處理模式，必須等外部請求才會執行程式邏輯；排程任務則要求在沒有請求的情況下主動於指定時間啟動，兩者模型不同，因此 Web Application 本身不擅長處理此類「主動式、定時」工作。

## Q: 如果只能用輪詢 (polling) 機制來執行排程，必須同時滿足哪些核心需求？
1. 盡量降低對資料庫額外的負擔  
2. 任務啟動的時間誤差越小越好（延遲低且穩定）  
3. 支援分散式與高可用，排程服務可同時跑多套互相備援  
4. 任務在任何情況下都只能被執行一次

## Q: 資料表欄位 CreateAt、RunAt、ExecuteAt 與 State 各代表什麼意思？
• CreateAt：排程資料被寫入資料庫的時間  
• RunAt：預定要開始執行的時間  
• ExecuteAt：實際開始執行的時間 (初始為 NULL)  
• State：任務狀態（0: 未執行、1: 執行中、2: 已完成）

## Q: 最基本的「撈出該執行但尚未執行的任務」SQL 指令是？
```sql
select * from jobs 
where state = 0 and runat < getdate() 
order by runat asc
```

## Q: 為什麼「把一小時後的工作直接丟進 Message Queue」不是好做法？
Message Queue 會立即把訊息排入佇列並占用空間；若任務要延遲很久才執行，訊息會長時間佔位，既浪費資源又可能導致後面訊息阻塞，效能與可預測性都不好。

## Q: 什麼是 MinPrepareTime 與 MaxDelayTime？
• MinPrepareTime：排程資料一定會在「預定執行時間 – MinPrepareTime」之前寫入資料庫，例如 10 秒。  
• MaxDelayTime：任務最遲必須在「預定執行時間 + MaxDelayTime」之前啟動，例如 30 秒。

## Q: 成本評分 (Cost Score) 如何計算？
Cost Score =  
(查詢待執行清單的次數 × 100) +  
(嘗試鎖定任務的次數 × 10) +  
(查詢單筆任務狀態的次數 × 1)

## Q: 精確度評分 (Efficient Score) 如何計算？
Efficient Score =  
所有任務延遲時間的平均值 + 所有任務延遲時間的標準差  
(公式：Avg(ExecuteAt – RunAt) + Stdev(ExecuteAt – RunAt))

## Q: 測試可靠度 (HA test) 通過的必要條件有哪些？
1. 測試結束後，所有任務的 State 都必須是 2 (已完成)  
2. 每筆紀錄的 RunAt – CreateAt 必須 ≥ MinPrepareTime  
3. 每筆紀錄的 ExecuteAt – RunAt 必須 ≤ MaxDelayTime

## Q: 官方測試流程大致怎麼進行？
1. 先以測試程式重建資料庫並持續 10 分鐘寫入排程資料  
2. 同時啟動 5 個排程服務實例  
3. 測試過程中隨機中斷其中 3 個實例以驗證高可用  
4. 測試結束後統計成本分數與精確度分數，並檢查是否符合可靠度條件