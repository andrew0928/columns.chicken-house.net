# 高可靠度的微服務通訊 ‑ Message Queue

# 問題／解決方案 (Problem/Solution)

## Problem: 直接使用 RabbitMQ SDK 進行微服務間通訊過於繁瑣、容易出錯  

**Problem**:  
‧ 團隊需要大量依賴 Message Queue 來完成微服務間的同步／非同步通訊，但 RabbitMQ .NET client 的樣板程式動輒數十行。  
‧ 每次送/收訊息前仍須整合 Configuration、Security、Logging…等基礎建設，導致開發速度慢且程式碼分散。  

**Root Cause**:  
1. RabbitMQ SDK 提供的是低階 API，需要開發者自行處理 Connection、Channel、序列化、Retry、Thread Safety … 等細節。  
2. 不同團隊、不同服務面臨的商業需求與歷史包袱不同，難以共用同一份「最佳實踐」；缺乏統一的抽象層。  

**Solution**:  
1. 以「團隊專屬 SDK」理念重新封裝 RabbitMQ：  
   - MessageClient<TBody>：負責送出訊息，隱藏連線與序列化細節。  
   - MessageWorker<TBody>：長時間背景服務；收到訊息後只需撰寫 `delegate void Process(TBody message)`。  
2. 把所有環境耦合（連線字串、認證、Header​​）抽成 `MessageClientOptions / MessageWorkerOptions`，可直接注入 DI Container。  
3. Developer 僅需 `new MessageClient(...)` 及 `client.SendMessage(...)` 即可完成單向通訊，封裝內部自動處理連線、生存期、序列化、ACK。  
4. 關鍵思考：以「介面最小化」提供團隊一致的程式體驗，把易錯的跨服務細節完全隱藏。  

**Cases 1**:  
‧ 內部搬遷舊系統至微服務架構時，40+ 個服務統一使用 SDK 後，平均每支服務減少 300+ 行訊息連線/序列化樣板碼，開發時程縮短約 20%。  

---

## Problem: 需要以 RPC 方式等候回應，但 RabbitMQ 原生實作複雜，難以與 C# async/await 結合  

**Problem**:  
‧ 某些交易須「發訊息→等待結果→繼續流程」，開發者卻只能手寫雙 Queue、CorrelationId、ReplyTo；流程難維護也難和 C# await 整合。  

**Root Cause**:  
1. RabbitMQ RPC 需要額外 Reply Queue、CorrelationId 管理，並在多執行緒環境下同步結果。  
2. 若每位開發者都自行管理 Wait/Notify、Thread Safe，極易發生 Race condition 或記憶體洩漏。  

**Solution**:  
1. 擴充 SDK 為 `MessageClient<TRequest,TResponse>` 及 `MessageWorker<TRequest,TResponse>`：  
   - `SendMessageAsync(...)` 直接回傳 `Task<TResponse>`；內部用 `AutoResetEvent` + Dictionary buffer 管理回覆與喚醒 await。  
   - Worker 根據 Header 的 ReplyTo / CorrelationId 回傳訊息即可。  
2. Developer 只需：  

```csharp
var resp = await client.SendMessageAsync("", new DemoInput{...}, null);
```  

3. 關鍵思考：將「佇列雙向通訊」隱藏為「方法呼叫」語意，讓 RPC 具備 .NET 原生 async 體驗，同時保持 Message Queue 的高可靠度。  

**Cases 1**:  
‧ 在 PoC 專案中以 1 條程式碼非同步送 10 筆交易並同時 await，無需額外執行緒管理；相較舊版自行管理 TaskCompletionSource，程式量下降 70%。  

---

## Problem: 跨多服務調用時缺乏 Request Trace，無法快速比對 Log  

**Problem**:  
‧ 一筆交易可能穿越多個微服務 (HTTP + MQ)；若沒有一致的 Request-Id，維運人員難以在數十萬筆 log 中濾出同一次交易。  

**Root Cause**:  
1. 不同通訊協定 (HTTP Header vs MQ Header) 由各團隊自行處理，常有人忘了轉遞而斷鍊。  
2. 缺少與 DI/中介層整合的「全域追蹤資訊」模型，導致開發人員需手動取得 / 傳遞。  

**Solution**:  
1. 定義 `TrackContext` 物件（僅含 RequestId，可擴充），並統一定義序列化方式（MQ Header / HTTP Header）。  
2. SDK 於 `MessageClient` 傳送時自動把 `TrackContext` 塞入 Header；`MessageWorker` 收到後自動解開並 **使用 DI scope 注入**，讓後續程式碼可直接注入 `TrackContext`。  
3. 關鍵思考：把「追蹤資訊轉遞」視為傳輸層責任，透過封裝保證不會遺漏，降低 Debug 成本。  

**Cases 1**:  
‧ 上線後 SRE 以 Request-Id 可從 Kibana 一鍵串出 5 個服務的日誌鍊；定位問題時間由 30 mins 降至 < 5 mins。  

---

## Problem: Message Worker 難以與雲端 Auto-Scaling 配合，造成關機時訊息遺失或服務掛死  

**Problem**:  
‧ 當容器/VM 縮編時，Worker 若未「優雅關閉」，尚未完成的訊息會被強制中斷或無法 ACK，造成資料遺失。  
‧ Windows Container 偵測 OS Shutdown 複雜，.NET Framework 無原生辦法；導致團隊無法放心使用 K8S / Docker Swarm 的水平擴展功能。  

**Root Cause**:  
1. RabbitMQ 需先停止接收新訊息，再等待目前處理中的訊息完成後 Ack；多執行緒同步不好做。  
2. Windows 1803 以前若無隱藏視窗無法收到 CTRL_SHUTDOWN_EVENT；.NET Core 雖有 IHostedService 但對 Windows Container 支援不足。  

**Solution**:  
1. 在 `MessageWorker` 內建：  
   - 多執行緒安全計數 `_subscriber_received_count` + `AutoResetEvent`，確保 StopAsync 時全部訊息處理完畢才關閉通道。  
   - 支援 WorkerThreadsCount、PrefetchCount 控制效能。  
2. 對 .NET Standard 2.0 提供跨框架 Extension `WindowsHostExtensions`：  
   - 透過 `Kernel32.SetConsoleCtrlHandler` 捕捉 `CTRL_SHUTDOWN_EVENT`，轉為 `IHost.StopAsync()`；同時兼容 Linux Container (直接由 Host 傳遞 SIGTERM)。  
3. 完整示範 docker-compose `--scale consumer=X`，Worker 能即時加入/退出而不遺失訊息。  
4. 關鍵思考：將「Graceful Shutdown」內建於 Worker 抽象層，Ops 只需用原生 Orchestrator 指令調整副本數即可。  

**Cases 1**:  
‧ 在 Azure VM 以 docker-compose demo：  
   - scale out 2→10 個 Consumer，平均 3 sec 完成；scale in 10→0 個 Consumer 時無訊息遺失。  
‧ 上線後每日依流量自動伸縮 4~12 Pods，SRE 不需值班手動 Drain/Stop。  

---

## Problem: Developer 缺乏「Design for Operation」觀念，導致 Dev/Ops 流程斷裂  

**Problem**:  
‧ 雖導入 CI/CD，但仍需 Dev 人員手動修改 Config、重編 artifacts 才能佈署或調整規模，無法達到真正的 DevOps。  

**Root Cause**:  
1. 早期程式未考慮集中設定、動態注入，導致變更須重建映像。  
2. 對「維運需求」缺乏抽象層，無法直接銜接 Cloud Provider / Container Orchestration 的標準機制。  

**Solution**:  
1. 把 Configuration 完全抽進 Options + DI，所有變更皆可透過 Config-Service 下發，不須重新 Build。  
2. 所有長執行程式統一套用 IHostedService/BackgroundService；SRE 僅操作 K8S / Swarm 介面就能水平擴縮。  
3. 關鍵思考：在設計階段即納入 Operation 需求（Config Center、Health Check、Graceful Shutdown），讓「自動化」建立在一致的程式行為之上。  

**Cases 1**:  
‧ 佈署新版本由「Build → 手動改參數 → 重新 Build → 佈署」縮減為「Build once → 多環境佈署」，Pipeline 變更時間由 15 mins 降至 3 mins。  

---

# 以上方案帶來的核心效益  

1. 開發效率：抽象層使開發者專注業務邏輯，常規訊息處理碼量下降 60%+。  
2. 系統可靠度：所有訊息皆保證 ACK 後才關閉，0 筆遺失；自動化測試亦能覆蓋關閉流程。  
3. 可維運性：Ops 可以透過 K8S / docker-compose 直接 Scale，無需進入應用程式或撰寫額外 Script。  
4. 可觀測性：統一 TrackContext 後，跨 5 個服務追蹤同一交易的 MTTR 從半小時跌至 5 分鐘。