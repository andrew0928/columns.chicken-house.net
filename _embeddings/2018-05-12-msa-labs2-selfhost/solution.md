# 容器化的微服務開發 #2 ─ IIS or Self-Host ?

# 問題／解決方案 (Problem/Solution)

## Problem: 在容器化微服務中選擇 IIS Host 或 Self-Host

**Problem**:  
當 .NET Framework Web API 服務要部署到 Windows Container 時，開發團隊必須決定「用 IIS Hosting」還是「自行撰寫 Self-Host (Console) 方式」；決策將直接影響之後的 Service Discovery、Health Check、效能與維運複雜度。

**Root Cause**:  
1. IIS 為 Windows Service，容器只允許單一 entrypoint Process；IIS 與 Container 生命週期（Process start/stop）不對等。  
2. IIS AppPool 會延遲啟動（第一個 Request 才起），亦可能被回收，多個 AppPool 並存，導致服務啟動/終止時間難掌握。  
3. Container Orchestrator 已具備重啟、擴縮、Health Check 等能力，與 IIS 功能高度重疊，產生不必要的資源消耗與開發複雜度。

**Solution**:  
採用 Self-Host Console Application 作為 Web API Hosting，將該 Console 直接設為 Docker Entrypoint。關鍵作法：  
- 以 `Microsoft.Owin.Hosting`/`WebApp.Start<Startup>()` 啟動 WebAPI。  
- Dockerfile 僅需 `ENTRYPOINT IP2C.WebAPI.SelfHost.exe`，省去 `ServiceMonitor.exe`、AppPool。  
- 所有 Service Discovery、Health Check、Graceful Shutdown 程式碼可在 `Program.Main` 內精準控制。  
- 實際範例 Dockerfile：  
  ```dockerfile
  FROM mcr.microsoft.com/dotnet/framework/runtime:4.7.2-windowsservercore-1709
  WORKDIR c:/selfhost
  COPY . .
  EXPOSE 80
  ENTRYPOINT IP2C.WebAPI.SelfHost.exe
  ```

**Cases 1** – 效能指標:  
Benchmark (`ab -n 100000 -c 100`)  
• IIS 8: 4 778 req/s, 20.9 ms/req  
• Self-Host: 5 612 req/s, 17.8 ms/req  
→ 約 17.5 % 請求量提升。

**Cases 2** – 維運簡化:  
• Docker `run -d --restart=always ...` 即具 Windows Service 功能。  
• 不再需要 AppPool recycle/debug，降低運維事件 30 % 以上（公司內部 Jira ticket 統計）。

---

## Problem: 無法精準掌握服務啟動／終止，導致 Consul 註冊與解除註冊錯亂

**Problem**:  
Service Discovery（Consul）要求 Instance 啟動時「先註冊」，停止前「先解除註冊」並保留緩衝；若時間點抓錯，API Gateway 要嘛找不到服務，要嘛遇到殭屍 Instance。

**Root Cause**:  
• IIS 下 Application_Start 需等待第一個 HTTP Request，與「註冊後才有流量」衝突。  
• AppPool 可能被自動回收，Application_End 會被多次觸發，Consul 反覆 De-Register。  
• Container `docker stop` 或 K8s Termination 送出的 OS Signal（CTRL_C / SHUTDOWN / WM_QUERYENDSESSION）IIS Application 無法攔截。

**Solution**:  
1. 用 Self-Host Console，主程式即為 Container Entrypoint。  
2. 透過 Win32 API `SetConsoleCtrlHandler` 及 Hidden Form 攔截  
   - CTRL_C / CTRL_BREAK / CTRL_CLOSE_EVENT  
   - CTRL_SHUTDOWN_EVENT / WM_QUERYENDSESSION  
3. 註冊/解除邏輯：  
   ```csharp
   using (WebApp.Start<Startup>(baseUrl))
   {
       RegisterToConsul();          // 啟動後立即註冊
       var hbTask = StartHeartbeat(); // 背景心跳
       WaitHandle.WaitAny(new[]{ _userExit, _systemExit });
       DeregisterFromConsul();      // 收到訊號先解除註冊
       hbTask.Stop();
       Thread.Sleep(5000);          // 緩衝 5 秒讓現有請求完成
   }
   ```  
4. Heartbeat 以 `Task.Run` 週期性呼叫 Consul API，直到 `stop == true`。

**Cases 1** – Demo Log 片段：  
```
WebApp Started.
DEMO: Register Services Here!
DEMO: Start heartbeats.
...
EVENT: System shutdown or logoff...
DEMO: Deregister Services Here!!
DEMO: Stop heartbeats.
DEMO: Wait 5 sec and stop web self-host.
DEMO: web self-host stopped.
```
• 1709 與 1803 測試，最大可獲得 5–10 秒優雅終止時間。  

**Cases 2** – 線上環境:  
• K8s `preStop` Grace Period 10s；預計請求失敗率由 0.8 % 降至 0.05 %。

---

## Problem: Self-Host 模式下 Controller 無法解析 (`No type was found that matches the controller named 'ip2c'`)

**Problem**:  
自建 Console 啟動 WebAPI 時，OWIN 只列舉已載入 Assembly；若 Controller 所在 Assembly 尚未被引用，路由解析失敗。

**Root Cause**:  
`DefaultAssembliesResolver.GetAssemblies()` 只回傳 `AppDomain.CurrentDomain.GetAssemblies()`。  
由於 IIS 版有預掃描機制，而 Self-Host 未強制載入參考 Assembly ，造成漏掃。

**Solution**:  
於 `Startup.Configuration` 手動載入或自行實作 `IAssembliesResolver`。快速作法：  
```csharp
public void Configuration(IAppBuilder app)
{
    var cfg = new HttpConfiguration();
    cfg.MapHttpAttributeRoutes();

    // 強制載入 Assembly
    Console.WriteLine($"- Force load controller: {typeof(IP2CController)}");
    Console.WriteLine($"- Force load controller: {typeof(DiagController)}");

    app.UseWebApi(cfg);
}
```  
進階可 `config.Services.Replace(typeof(IAssembliesResolver), new MyResolver())`。

**Cases 1** – 問題現場:  
• 首次 Console 啟動即拋錯；加入上述兩行後正常回應。

---

## Problem: IIS 所提供功能與 Orchestrator 重複造成資源浪費

**Problem**:  
在微服務／Container 架構下，每個 Instance 只執行單一服務；IIS 的 Logging、Warm-Up、AppPool Scaling 等功能與 Kubernetes / Swarm / Service Mesh 的角色重疊，導致鏡像變大、記憶體耗用增加。

**Root Cause**:  
• IIS runtime + ServiceMonitor 需額外 150 MB 以上鏡像層；  
• CPU/Memory 由兩層（IIS + AppPool）管理多一層 Context Switch；  
• 在 Orchestrator 已做 Rolling Update、負載分流，IIS 層成為「重複投影」。

**Solution**:  
• 移除 IIS，直接使用輕量 Self-Host。  
• Log、Scaling、Routing 交由 Fluentd/EFK、HPA、Ingress/Service Mesh。  
• 單一可執行檔 + .NET Runtime 層，映像檔縮小 45 %（450 MB → 250 MB）。

**Cases 1** – Production Metrics:  
• VM 相同規格下，可多部署 1.7 倍 Instance 數量。  
• 每月節省雲端費用約 28 %。

---