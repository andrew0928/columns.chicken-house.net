---
source_file: "_posts/2018/2018-05-12-msa-labs2-selfhost.md"
generated_date: "2025-08-03 14:30:00 +0800"
version: "1.0"
tools:
  - github_copilot
model: "github-copilot"
---

# 容器化的微服務開發 #2, IIS or Self Host ? - 生成內容

## Metadata

### 原始 Metadata
```yaml
layout: post
title: "容器化的微服務開發 #2, IIS or Self Host ?"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps", "Service Discovery", "Consul"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2018-05-12-msa-labs2-selfhost/how_would_you_solve_the_icing_problem.jpg
```

### 自動識別關鍵字
keywords:
  primary:
    - Self Host vs IIS Host
    - Container Driven Development
    - ASP.NET WebAPI 容器化
    - 微服務生命週期管理
    - Service Discovery 整合
  secondary:
    - OWIN Self Host
    - Container Orchestration
    - App Pool 管理
    - Windows Container
    - Health Checking

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - PowerShell
  frameworks:
    - ASP.NET WebAPI
    - OWIN
    - .NET Framework
  tools:
    - Docker
    - IIS
    - Visual Studio
    - ServiceMonitor.exe
  platforms:
    - Windows Container
    - Windows Server
    - Azure

### 參考資源
references:
  internal_links:
    - /2017/05/28/aspnet-msa-labs1/
    - /2018/05/10/tips-handle-shutdown-event/
    - Container Driven Development 影片
  external_links:
    - https://github.com/Microsoft/IIS.ServiceMonitor
    - https://forums.asp.net/t/1908235.aspx
    - https://stackify.com/kestrel-web-server-asp-net-core-kestrel-vs-iis/
    - https://github.com/andrew0928/IP2C.NET.Service
  mentioned_tools:
    - Consul
    - Kestrel
    - Cassini Dev Server
    - Nancy FX

### 內容特性
content_metrics:
  word_count: 8500
  reading_time: "43 分鐘"
  difficulty_level: "高級"
  content_type: "教學"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)
作者深入探討在微服務容器化部署中，選擇 IIS Host 還是 Self Host 的重要決策問題。從架構、環境、效能三個面向分析，作者發現在容器環境下，IIS 的許多傳統優勢（如 App Pool 管理、負載平衡、資源管理）都被 Container Orchestration 機制所取代，反而增加了不必要的複雜度。特別是在 Service Discovery 的整合上，IIS Host 模式難以精準控制服務的啟動和終止時機，影響服務註冊和反註冊的準確性。作者提出 Container Driven Development (CDD) 的理念，建議在確定使用容器部署的前提下，應該優先考慮 Self Host 模式。文章詳細示範了如何使用 OWIN 建立 Self Host 的 ASP.NET WebAPI 服務，處理 Controller 載入問題，並整合系統關機事件處理機制，實現完整的服務生命週期管理。最後透過實際的 Docker 容器測試，驗證了 Self Host 方案在不同 Windows 版本下的穩定性和可靠性。

### 關鍵要點 (Key Points)
- 容器環境下 IIS 的傳統優勢被 Orchestration 機制取代
- Self Host 模式能更精準控制服務生命週期，適合 Service Discovery 整合
- CDD 理念強調簡化架構，移除容器能替代的功能組件
- OWIN Self Host 需要手動處理 Controller Assembly 載入問題
- 系統關機事件處理對微服務優雅關閉至關重要
- 不同 Windows 版本的關機事件處理機制存在差異

### 段落摘要 (Section Summaries)

1. **架構考量分析**：作者從容器生命週期管理的角度，分析了 IIS Host 和 Self Host 的根本差異。IIS 作為 Windows Service 運行，與容器的 EntryPoint Process 模式存在架構上的不匹配。容器的生命週期直接依附於指定的 Process，而 IIS 需要透過 ServiceMonitor.exe 來橋接這種差異。更嚴重的問題在於 IIS 的 App Pool 管理機制會導致應用程式多次啟動和終止，且啟動時機依賴外來的 HTTP Request，這與 Service Discovery 的註冊需求形成矛盾：服務必須先註冊才能被發現，但 App Pool 卻要等到請求進來才啟動。相較之下，Self Host 模式提供了單一 Process 的簡潔架構，讓開發者能精準掌握服務的啟動和終止時機，完美契合容器和 Service Discovery 的需求。

2. **環境與功能考量**：作者詳細分析了 IIS 提供的各種功能在微服務架構下的必要性。傳統上 IIS 提供的日誌記錄、應用程式池擴展、節流控制、負載平衡、虛擬目錄管理等功能，在微服務容器化環境下大多有更適合的替代方案。Container Orchestration 能夠提供更好的擴展性管理、Health Checking、負載平衡等功能，而且是在整個叢集層級進行管理，而非單一容器內部。微服務架構強調一個容器一個 Process 的設計理念，多個服務透過 Reverse Proxy 在前端組合，因此 IIS 的多站點管理功能變得多餘。作者強調，在微服務化和容器化的前提下，IIS 不再是容器內絕對必要的組件，選擇 Self Host 能夠獲得更簡潔和高效的架構。

3. **應用程式生命週期管理**：作者深入探討了 IIS App Pool 機制在微服務環境下的限制和問題。App Pool 的延遲啟動、自動回收、多 Worker 管理等功能，雖然在單機環境下能夠優化資源使用和提升可靠度，但在容器環境下卻與 Service Discovery 的需求產生衝突。開發者只能控制 App Pool 內的 Application Events，無法掌握更高層級的容器生命週期。這種控制範圍的限制導致服務註冊和反註冊的時機難以準確掌握，可能造成服務清單的不一致。更重要的是，App Pool 本身就是 IIS 的容器化機制，當外部已經有更成熟的容器 Orchestration 時，繼續使用 App Pool 就成了重複的架構設計，增加了不必要的複雜度。

4. **效能比較與實證**：通過引用第三方的效能測試數據，作者證明了 Self Host 模式在效能上的優勢。測試結果顯示 Self Host 相比 IIS 8 能夠提升 17.5% 的效能，主要原因是移除了 IIS 額外的功能層帶來的開銷。在微服務架構中，由於分工更加細緻，IIS 提供的許多功能都有專門的服務或設備來處理，因此移除 IIS 這一層能夠在相同的硬體資源下獲得更高的處理能力。作者強調，當系統的其他部分已經提供了 IIS 的功能時，保留 IIS 只會帶來效能損耗而沒有實際價值。這個效能差異在高負載的微服務環境下會被進一步放大，因此選擇 Self Host 是明智的決策。

5. **Self Host 實作詳解**：作者提供了完整的 OWIN Self Host 實作方案，詳細說明了各個技術細節的處理方法。首先解決 Controller Assembly 載入問題，通過在 Startup 階段強制引用 Controller 類型來確保 IAssembliesResolver 能夠找到所需的 Controller。接著整合系統關機事件處理機制，結合 SetConsoleCtrlHandler API 和隱藏 Windows Form 的 WndProc 訊息處理，確保能夠攔截各種終止事件。作者特別設計了 Health Checking 的 Background Task 機制，能夠在服務運行期間持續發送心跳訊號，並在收到關機信號時優雅地停止所有背景工作。整個實作展現了從服務啟動、註冊、運行、到優雅關閉的完整生命週期管理。

6. **容器環境測試驗證**：作者在多個 Windows 版本（Windows 10 1803、Windows Server 1709、1803）下進行了全面的容器測試，驗證 Self Host 方案的穩定性和可靠性。測試結果顯示，不同 Windows 版本在關機事件處理上存在微妙差異：1709 版本需要依賴隱藏 Form 的 WM_QUERYENDSESSION 訊息，而 1803 版本則可以透過 SetConsoleCtrlHandler 攔截 CTRL_SHUTDOWN_EVENT。這些差異影響了優雅關閉的處理時間限制，從 10 秒到 5 秒不等。儘管存在這些版本差異，整體的 Self Host 架構都能夠正確運作，成功實現了服務的優雅啟動和關閉，為後續的 Service Discovery 整合奠定了堅實的基礎。

## 問答集 (Q&A Pairs)

### Q1: 為什麼在容器環境下不建議使用 IIS Host？
Q: 容器化部署時，使用 IIS Host 有什麼問題？
A: IIS 作為 Windows Service 與容器的 EntryPoint Process 模式不匹配，需要 ServiceMonitor.exe 來橋接。更嚴重的是 App Pool 的生命週期管理會導致應用程式多次啟動終止，且依賴外來 HTTP Request 才啟動，這與 Service Discovery 的註冊需求形成矛盾。

### Q2: 什麼是 Container Driven Development (CDD)？
Q: CDD 的核心理念是什麼？
A: CDD 是假設將來一定會用容器化方式部署，在架構設計時就對容器進行最佳化。重點不是多做什麼，而是思考哪些功能可以由容器或 Orchestration 來替代，適度簡化讓 Operation 團隊更容易維護，Developer 更專注於核心業務。

### Q3: Self Host 模式如何解決 Controller 載入問題？
Q: OWIN Self Host 找不到 Controller 該如何處理？
A: 預設的 IAssembliesResolver 會搜尋 AppDomain 已載入的 Assemblies，但 Controller Assembly 可能尚未被載入。解決方法是在 Startup Configuration 階段，透過 typeof(ControllerClass) 強制引用 Controller 類型，確保 Assembly 被載入到 AppDomain 中。

### Q4: 為什麼需要處理系統關機事件？
Q: 微服務中處理關機事件有什麼重要性？
A: 微服務需要在關閉前主動從 Service Discovery 中反註冊，避免其他服務嘗試呼叫已關閉的服務。正確處理關機事件能確保服務優雅關閉，完成必要的清理工作，提高整個微服務系統的穩定性和可靠性。

### Q5: 不同 Windows 版本的關機事件處理有什麼差異？
Q: Windows 1709 和 1803 在處理容器關機事件上有何不同？
A: Windows 1709 需要透過隱藏 Form 的 WM_QUERYENDSESSION 訊息來攔截關機事件，最多有 10 秒處理時間。Windows 1803 則可以用 SetConsoleCtrlHandler 攔截 CTRL_SHUTDOWN_EVENT，但處理時間限制約 5 秒。

### Q6: IIS 相比 Self Host 的效能差異有多大？
Q: Self Host 在效能上比 IIS Host 好多少？
A: 根據第三方測試數據，Self Host 相比 IIS 8 能夠提升約 17.5% 的效能。主要原因是移除了 IIS 額外功能層的開銷，在微服務架構下，這些功能通常有專門的服務來處理，因此 IIS 變成不必要的負擔。

### Q7: 如何實作微服務的 Health Checking 機制？
Q: Self Host 模式下如何實作心跳檢測？
A: 在服務註冊完成後啟動獨立的 Background Task，持續監控 stop flag 並定期發送心跳訊號。當收到關機信號時設定 stop flag 為 true，等待 heartbeats task 完成後再進行服務反註冊和優雅關閉。

### Q8: 容器環境下 App Pool 管理還有必要嗎？
Q: 為什麼說 App Pool 機制在容器環境下是多餘的？
A: App Pool 本身就是 IIS 的容器化機制，負責應用程式的生命週期管理。當外部已經有更成熟的 Container Orchestration 來處理相同的功能時，App Pool 就成了重複的架構設計，增加複雜度卻沒有額外價值。

### Q9: ServiceMonitor.exe 的作用是什麼？
Q: Microsoft 為什麼要提供 ServiceMonitor.exe？
A: ServiceMonitor.exe 的目的是橋接 Windows Service 和容器生命週期的差異。它監控 IIS (w3svc) 服務狀態，當服務停止時 ServiceMonitor 也會終止，讓容器跟著進入 stop 狀態。這是為了相容性而設計的中間層解決方案。

### Q10: 微服務架構下 IIS 的哪些功能被其他機制取代？
Q: Container Orchestration 如何取代 IIS 的功能？
A: IIS 的負載平衡被 Reverse Proxy 取代，擴展性管理被 Container Scaling 取代，Health Checking 被 Orchestration 的健康檢查取代，多站點管理被前端路由取代，資源管理被容器資源限制取代。這些功能在叢集層級處理比在單一容器內處理更有效率。

## 解決方案 (Solutions)

### P1: 容器環境下的架構選型問題
Problem: 在微服務容器化部署中，需要選擇合適的 Host 模式來確保服務能與 Container Orchestration 和 Service Discovery 良好整合。
Root Cause: IIS Host 模式與容器生命週期管理機制存在架構上的不匹配，App Pool 的管理邏輯與微服務的註冊需求產生衝突，難以精準控制服務的啟動和終止時機。
Solution:
- 採用 Self Host 模式實現單一 Process 架構
- 使用 OWIN 框架建立輕量化的 Web Host
- 移除 IIS 相關的依賴和複雜性
- 讓容器直接管理服務的生命週期
Example:
```csharp
// OWIN Self Host 基本架構
using (WebApp.Start<Startup>("http://localhost:9000/"))
{
    Console.WriteLine("WebApp Started.");
    // 服務註冊邏輯
    RegisterToServiceDiscovery();
    
    // 等待關機信號
    shutdownEvent.WaitOne();
    
    // 服務反註冊邏輯
    UnregisterFromServiceDiscovery();
}
```

### P2: Controller Assembly 載入失敗問題
Problem: OWIN Self Host 環境下，ASP.NET 找不到定義在其他 Assembly 中的 Controller，出現 "No type was found that matches the controller" 錯誤。
Root Cause: 預設的 IAssembliesResolver 只搜尋 AppDomain 中已載入的 Assemblies，但 Controller Assembly 可能因為延遲載入而尚未被加載到 AppDomain 中。
Solution:
- 在 Startup Configuration 階段強制引用 Controller 類型
- 確保相關 Assembly 在 Resolver 執行前被載入
- 或自訂 IAssembliesResolver 實作更精準的載入邏輯
- 使用 typeof() 操作符觸發 Assembly 載入
Example:
```csharp
public void Configuration(IAppBuilder appBuilder)
{
    HttpConfiguration config = new HttpConfiguration();
    
    // 強制載入 Controller Assembly
    Console.WriteLine($"Force load: {typeof(IP2CController)}");
    Console.WriteLine($"Force load: {typeof(DiagController)}");
    
    // 設定路由
    config.Routes.MapHttpRoute(/* ... */);
    appBuilder.UseWebApi(config);
}
```

### P3: 系統關機事件攔截問題
Problem: Console Application 需要能夠攔截各種系統關機事件（CTRL-C、關閉視窗、系統關機），以便執行優雅關閉流程。
Root Cause: Console Application 預設只能處理基本的使用者操作，對於系統級的關機事件（如 OS shutdown）無法透過標準 API 攔截，特別是在容器環境下。
Solution:
- 結合 SetConsoleCtrlHandler API 處理使用者操作事件
- 使用隱藏 Windows Form 的 WndProc 處理系統級事件
- 透過 WaitHandle.WaitAny 等待多種事件源
- 針對不同 Windows 版本採用相應的處理策略
Example:
```csharp
// 設定多種關機事件處理
SetConsoleCtrlHandler(ShutdownHandler, true);

var hiddenForm = new HiddenForm();
Task.Run(() => Application.Run(hiddenForm));

// 等待任一關機事件
int eventIndex = WaitHandle.WaitAny(new WaitHandle[]
{
    userShutdownEvent,  // CTRL-C 等使用者操作
    systemShutdownEvent // 系統關機事件
});
```

### P4: 微服務生命週期精準控制問題
Problem: 微服務需要精準控制啟動、運行、關閉各階段的處理邏輯，特別是與 Service Discovery 的註冊和反註冊時機。
Root Cause: 傳統的 IIS Host 模式下，開發者對服務生命週期的控制權有限，App Pool 的管理機制會干擾正確的註冊時機，且可能發生多次重複註冊。
Solution:
- 建立清晰的生命週期管理流程
- 在服務啟動完成後立即進行註冊
- 實作 Background Task 負責持續的健康檢查
- 在接收關機信號後優雅地執行反註冊和清理
Example:
```csharp
// 完整的生命週期管理
using (WebApp.Start<Startup>(baseAddress))
{
    // 1. 服務啟動完成，進行註冊
    string serviceID = RegisterService();
    
    // 2. 啟動背景健康檢查
    bool shouldStop = false;
    var healthTask = Task.Run(() => {
        while (!shouldStop) {
            SendHeartbeat(serviceID);
            Task.Delay(1000).Wait();
        }
    });
    
    // 3. 等待關機信號
    shutdownEvent.WaitOne();
    
    // 4. 執行優雅關閉
    shouldStop = true;
    UnregisterService(serviceID);
    healthTask.Wait();
    Task.Delay(5000).Wait(); // 緩衝時間
}
```

### P5: 容器環境差異適配問題
Problem: 不同 Windows 版本的容器環境在關機事件處理上存在差異，影響服務優雅關閉的實現。
Root Cause: Windows Container 的實作在不同版本間有所變化，1709 和 1803 版本在事件傳遞機制和時間限制上存在差異，需要適配不同的處理方式。
Solution:
- 實作版本檢測和適配邏輯
- 同時支援多種事件攔截機制
- 設計彈性的超時處理策略
- 建立全面的測試覆蓋不同版本
Example:
```csharp
// 版本適配的事件處理
private void SetupShutdownHandling()
{
    // 支援多種事件攔截方式
    SetConsoleCtrlHandler(ConsoleHandler, true);
    
    // 隱藏 Form 用於系統級事件
    var hiddenForm = new HiddenForm();
    Task.Run(() => Application.Run(hiddenForm));
    
    // 根據版本調整超時時間
    var timeout = GetTimeoutByWindowsVersion();
    // Windows 1709: 10秒, Windows 1803: 5秒
}
```

### P6: 效能最佳化與架構簡化問題
Problem: 在微服務架構下，如何移除不必要的中間層以獲得最佳效能，同時保持架構的簡潔性。
Root Cause: IIS 提供的許多功能在微服務環境下被其他專門的服務取代，但仍然消耗系統資源。Container Orchestration 已經提供了更好的替代方案，繼續使用 IIS 只是增加不必要的開銷。
Solution:
- 分析並識別可由容器機制替代的功能
- 採用 Self Host 減少中間層開銷
- 將負載平衡、健康檢查等功能交給 Orchestration
- 專注於核心業務邏輯的最佳化
Example:
```csharp
// 簡化的服務架構
public class MicroserviceHost
{
    public void Start()
    {
        // 只保留核心的 Web API 功能
        using var webApp = WebApp.Start<Startup>(bindingUrl);
        
        // 生命週期管理交給容器
        // 負載平衡交給 Orchestrator  
        // 健康檢查交給服務發現機制
        // 日誌記錄交給集中式日誌系統
        
        WaitForShutdownSignal();
    }
}
```

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本，基於原始文章生成 embedding content
- 包含完整的 metadata、摘要、問答對和解決方案
- 遵循 embedding-structure.instructions.md 規範
