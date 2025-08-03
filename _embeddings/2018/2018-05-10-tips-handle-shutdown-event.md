---
source_file: "_posts/2018/2018-05-10-tips-handle-shutdown-event.md"
generated_date: "2025-08-03 14:15:00 +0800"
version: "1.0"
tools:
  - github_copilot
model: "github-copilot"
---

# Tips: 在 .NET Console Application 中處理 Shutdown 事件 - 生成內容

## Metadata

### 原始 Metadata
```yaml
layout: post
title: "Tips: 在 .NET Console Application 中處理 Shutdown 事件"
categories:
tags: ["microservice", "Docker", "Windows Container", ".NET", "Container", "Tips", "作業系統"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2018-05-10-tips-handle-shutdown-event/2018-05-12-03-39-50.png
```

### 自動識別關鍵字
keywords:
  primary:
    - Console Application
    - Shutdown Event
    - Windows Container
    - CDD 容器驅動開發
    - Service Discovery
  secondary:
    - SetConsoleCtrlHandler
    - WndProc
    - P/Invoke
    - Windows Message
    - Docker Stop

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - Win32 API
  frameworks:
    - .NET Framework
    - Windows Forms
  tools:
    - Docker
    - Visual Studio
    - Windows Container
  platforms:
    - Windows 10
    - Windows Server
    - Container Runtime

### 參考資源
references:
  internal_links:
    - CDD 容器驅動開發影片
    - 微服務系列文章
  external_links:
    - https://docs.microsoft.com/en-us/windows/console/setconsolectrlhandler
    - https://docs.microsoft.com/en-us/windows/console/handlerroutine
    - https://msdn.microsoft.com/en-us/library/microsoft.win32.systemevents.sessionending.aspx
    - https://msdn.microsoft.com/en-us/library/microsoft.win32.systemevents.aspx
    - https://www.consul.io/
  mentioned_tools:
    - Consul
    - Docker
    - Kernel32.dll
    - P/Invoke

### 內容特性
content_metrics:
  word_count: 3100
  reading_time: "16 分鐘"
  difficulty_level: "中級"
  content_type: "教學"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)
作者在開發微服務架構時，採用 CDD（Container Driven Development，容器驅動開發）的理念，希望將所有服務簡化為 Console Application 模式。然而在實作 Service Discovery 功能時，遇到了如何在 Console Application 中正確處理 Shutdown 事件的技術難題。作者詳細記錄了解決這個問題的完整過程，從最初嘗試使用 Win32 API 的 SetConsoleCtrlHandler 函數，到發現該方法在 Windows Container 環境下無效，最終透過建立隱藏的 Windows Form 並處理 WndProc 訊息來解決問題。文章不僅提供了具體的程式碼實作，還包含了完整的 Docker 測試流程，展示了如何在容器化環境中驗證 Shutdown 事件的處理機制。作者的解決方案雖然需要引入 Windows Forms 依賴，但成功實現了在 Console Application 中捕捉 OS 關機事件的需求。

### 關鍵要點 (Key Points)
- CDD 理念強調使用 Console Application 簡化微服務開發
- SetConsoleCtrlHandler API 在 Windows Container 中無法正常工作
- 系統關機事件只能透過 Windows Message 機制處理
- 需要建立隱藏 Windows Form 來接收 WM_QUERYENDSESSION 訊息
- Docker Stop 指令可以正確觸發應用程式的 Shutdown 處理流程
- 解決方案雖引入額外依賴但能滿足 Service Discovery 的實際需求

### 段落摘要 (Section Summaries)

1. **背景與動機**：作者闡述了採用 CDD（容器驅動開發）理念的原因，以及為何選擇 Console Application 作為微服務的主要開發模式。透過容器技術，開發者可以省去 Windows Service 或 IIS Host 的複雜配置，專注於業務邏輯的實作。作者的目標是讓所有服務都能透過 Docker 的 orchestration 功能自動管理生命週期，包括背景執行、自動重啟等功能。然而在實作 Service Discovery 機制時，發現必須能夠捕捉程式終止事件，以便在服務關閉前主動從服務清單中移除，避免服務註冊資訊殘留。這個看似簡單的需求，卻引出了 Console Application 在 Windows 環境下處理 Shutdown 事件的技術挑戰。

2. **第一次嘗試：SetConsoleCtrlHandler API**：作者首先嘗試使用 Win32 API 的 SetConsoleCtrlHandler 函數來處理各種終止事件。這個 API 理論上能夠處理 CTRL-C、CTRL-BREAK、關閉視窗、使用者登出、系統關機等多種事件類型。作者透過 P/Invoke 機制呼叫 Kernel32.dll，實作了一個看似完整的事件處理器。在一般的 Windows 環境下測試時，這個方法能夠正確攔截 CTRL-C 和關閉視窗等事件，讓作者以為找到了正確的解決方案。然而這個方法有個致命的盲點：作者沒有仔細測試所有的事件類型，特別是系統關機事件，這為後續在容器環境中的失敗埋下了伏筆。

3. **Windows Container 測試失敗**：當作者將應用程式部署到 Windows Container 中進行測試時，發現 SetConsoleCtrlHandler 完全無法攔截 Docker Stop 指令觸發的關機事件。作者設計了一套完整的測試流程：建立 Container Image、啟動容器並觀察輸出、停止容器並檢查是否有正確的 Shutdown 訊息。測試結果顯示容器直接終止，沒有執行任何 Shutdown 處理邏輯。作者嘗試了多種 Windows 版本（Windows 10 1709/1803、Windows Server 2016/1709）都得到相同的結果，確認這個方法在容器環境下完全無效。這個發現迫使作者重新審視解決方案，並深入研究 Windows API 的文件細節。

4. **發現問題根源與新解決方案**：透過深入研究 Microsoft 文件，作者發現了問題的根本原因：SetConsoleCtrlHandler API 的 CTRL_LOGOFF_EVENT 和 CTRL_SHUTDOWN_EVENT 事件只對 Windows Service 類型的應用程式有效，Console Application 無法接收這些事件。這解釋了為什麼容器測試會失敗。作者進一步研究發現，Windows 的事件通知機制主要建立在 Windows Message 體系之上，只有具備視窗句柄的程式才能接收系統級的訊息。因此作者採用了一個巧妙的解決方案：建立一個隱藏的 Windows Form，透過覆寫 WndProc 方法來攔截 WM_QUERYENDSESSION 訊息。這個方法雖然引入了 Windows Forms 的依賴，但成功解決了 Console Application 無法處理系統關機事件的問題。

## 問答集 (Q&A Pairs)

### Q1: 什麼是 CDD（容器驅動開發）？
Q: CDD 的核心理念是什麼？
A: CDD（Container Driven Development，容器驅動開發）是作者提出的開發理念，主張將所有服務簡化為 Console Application 模式，透過容器技術來解決傳統的部署和管理問題。開發者可以專注於業務邏輯，而將背景執行、自動重啟、生命週期管理等交由 Docker 的 orchestration 功能處理。

### Q2: 為什麼選擇 Console Application 而非 Windows Service？
Q: Console Application 相比 Windows Service 有什麼優勢？
A: Console Application 更適合容器化部署，因為它可以直接在 Shell Script 或容器內執行，不需要複雜的服務安裝和配置。透過 Docker 的 run -d --restart always 等參數，可以實現與 Windows Service 相同的背景執行和自動重啟功能，同時簡化了開發和部署流程。

### Q3: SetConsoleCtrlHandler API 為什麼無法處理系統關機事件？
Q: SetConsoleCtrlHandler 在處理 Shutdown 事件時有什麼限制？
A: 根據 Microsoft 文件，SetConsoleCtrlHandler API 的 CTRL_LOGOFF_EVENT 和 CTRL_SHUTDOWN_EVENT 事件只對 Windows Service 類型的應用程式有效。Console Application 無法接收這些系統級的關機事件，這是 Windows 作業系統的設計限制。

### Q4: 為什麼需要使用 Windows Forms 來解決這個問題？
Q: 使用隱藏的 Windows Form 有什麼技術原理？
A: Windows 的事件通知機制主要建立在 Windows Message 體系之上，系統關機事件會透過 WM_QUERYENDSESSION 訊息通知有視窗句柄的程式。因此需要建立一個隱藏的 Windows Form 來接收這些訊息。雖然這引入了額外的依賴，但這是在 Console Application 中處理系統級事件的唯一可行方案。

### Q5: 如何在容器環境中測試 Shutdown 事件處理？
Q: 測試容器中的 Shutdown 事件處理需要哪些步驟？
A: 測試流程包括：1) 將應用程式打包成 Container Image；2) 使用 docker run -d 啟動容器並用 docker logs -f 觀察輸出；3) 在另一個終端執行 docker stop 指令停止容器；4) 檢查 logs 輸出是否包含完整的啟動和關機訊息，確認 Shutdown 處理邏輯是否正確執行。

### Q6: WndProc 方法如何處理關機訊息？
Q: 在 WndProc 中如何攔截和處理 WM_QUERYENDSESSION 訊息？
A: 在覆寫的 WndProc 方法中，檢查訊息代碼是否為 0x11（WM_QUERYENDSESSION），如果是則設定返回值為 1 表示同意關機，同時觸發 AutoResetEvent 通知主程式開始執行關機處理邏輯，最後呼叫 base.WndProc 讓系統繼續處理其他訊息。

### Q7: 這個解決方案對 Service Discovery 有什麼重要性？
Q: 正確處理 Shutdown 事件對微服務架構有什麼意義？
A: 在 Service Discovery 機制中，服務必須在關閉前主動從服務註冊中心移除自己的註冊資訊，避免其他服務仍然嘗試呼叫已關閉的服務。正確處理 Shutdown 事件能確保服務在容器停止時，能夠優雅地完成清理工作，提高整個微服務系統的穩定性。

### Q8: P/Invoke 在這個解決方案中扮演什麼角色？
Q: 為什麼需要使用 P/Invoke 呼叫 Win32 API？
A: P/Invoke 讓 .NET 程式能夠呼叫原生的 Windows API，在第一次嘗試中，作者使用 P/Invoke 呼叫 Kernel32.dll 的 SetConsoleCtrlHandler 函數。雖然這個方法最終無效，但 P/Invoke 仍然是在 .NET 中存取低階系統功能的重要機制。

### Q9: 這個問題在傳統 Windows 開發中為什麼不常見？
Q: 為什麼很少有人遇到 Console Application 處理 Shutdown 事件的問題？
A: 在容器化之前，大多數需要處理系統事件的應用程式都採用 Windows Service 或 Windows Forms 架構，很少有人嘗試在 Console Application 中處理系統關機事件。Windows Container 的普及讓這個問題浮現，但使用 Windows Container 的開發者仍然相對較少。

### Q10: 這個解決方案有什麼限制或注意事項？
Q: 使用隱藏 Windows Form 的方案有哪些缺點？
A: 主要限制是引入了 Windows Forms 的依賴，增加了應用程式的複雜度和記憶體使用量。此外，這個方案仍然依賴於 Windows 平台特有的訊息機制，無法移植到其他作業系統。不過對於 Windows Container 環境下的微服務開發，這是目前唯一可行的解決方案。

## 解決方案 (Solutions)

### P1: Console Application 無法處理系統關機事件
Problem: .NET Console Application 需要在程式終止前執行清理工作，但無法攔截到 Docker Stop 或系統關機事件。
Root Cause: Console Application 不具備接收系統級事件通知的能力，Windows 的關機事件主要透過 Windows Message 機制傳遞，而 Console Application 沒有視窗句柄無法接收這些訊息。
Solution:
- 建立隱藏的 Windows Form 來接收系統訊息
- 覆寫 WndProc 方法攔截 WM_QUERYENDSESSION 訊息
- 透過 AutoResetEvent 同步主程式與訊息處理
- 確保 Form 設定為不可見且不顯示在工作列
Example:
```csharp
var hiddenForm = new Form() 
{
    ShowInTaskbar = false,
    Visible = false,
    WindowState = FormWindowState.Minimized
};

// 在 Form 中覆寫 WndProc 方法
protected override void WndProc(ref Message m)
{
    if (m.Msg == 0x11) // WM_QUERYENDSESSION
    {
        m.Result = (IntPtr)1;
        shutdownEvent.Set(); // 通知主程式開始關機處理
    }
    base.WndProc(ref m);
}
```

### P2: SetConsoleCtrlHandler API 在容器環境中失效
Problem: 使用 Win32 API SetConsoleCtrlHandler 雖然能處理 CTRL-C 等事件，但無法處理容器停止事件。
Root Cause: SetConsoleCtrlHandler 的 CTRL_LOGOFF_EVENT 和 CTRL_SHUTDOWN_EVENT 只對 Windows Service 有效，Console Application 無法接收這些特定的系統事件。
Solution:
- 放棄使用 SetConsoleCtrlHandler 處理系統關機事件
- 改用 Windows Message 機制處理系統級事件
- 可保留 SetConsoleCtrlHandler 處理 CTRL-C 等使用者操作
- 綜合使用多種事件處理機制確保完整覆蓋
Example:
```csharp
// 錯誤的做法 - 無法處理系統關機
SetConsoleCtrlHandler(handler, true);

// 正確的做法 - 使用 Windows Message
protected override void WndProc(ref Message m)
{
    if (m.Msg == 0x11) // 系統關機事件
    {
        // 處理關機邏輯
    }
}
```

### P3: 容器化應用程式的生命週期管理
Problem: 微服務在容器環境中需要優雅地處理啟動和關閉，特別是 Service Discovery 的註冊和反註冊。
Root Cause: 容器的生命週期管理依賴於應用程式能正確響應停止信號，如果應用程式無法處理這些信號，就會導致服務註冊資訊殘留或資源清理不完整。
Solution:
- 實作完整的應用程式生命週期管理
- 在啟動時進行服務註冊和資源初始化
- 在接收到關機信號時執行反註冊和清理
- 設計合適的超時機制避免無限等待
Example:
```csharp
// 應用程式啟動
Console.WriteLine("# Service Started.");
registerToServiceDiscovery();

// 等待關機信號
shutdownEvent.WaitOne();

// 執行清理工作
unregisterFromServiceDiscovery();
cleanupResources();
Console.WriteLine("# Service Stopped.");
```

### P4: Windows Container 中的事件處理驗證
Problem: 需要有效的測試方法來驗證容器中的應用程式是否能正確處理關機事件。
Root Cause: 容器環境的測試比較複雜，需要透過 Docker 指令和 logs 來觀察應用程式行為，傳統的除錯方法不適用。
Solution:
- 建立標準化的容器測試流程
- 使用 Docker logs 監控應用程式輸出
- 設計清楚的日誌訊息標示不同的生命週期階段
- 透過 Docker stop 模擬真實的關機情境
Example:
```bash
# 建立並啟動容器
docker build -t test-app .
docker run -d --name test-container test-app

# 監控應用程式輸出
docker logs test-container -f

# 在另一個終端停止容器
docker stop test-container

# 檢查完整的生命週期日誌
docker logs test-container
```

### P5: 跨平台相容性與技術債務管理
Problem: 使用 Windows Forms 解決方案引入了額外的依賴，可能影響應用程式的輕量化和跨平台能力。
Root Cause: Windows 平台特有的事件處理機制限制了解決方案的通用性，必須在功能需求和架構簡潔性之間做出權衡。
Solution:
- 將事件處理邏輯封裝成獨立的模組
- 使用條件編譯來隔離平台特定的程式碼
- 建立清楚的抽象介面供不同平台實作
- 定期評估是否有更好的替代方案
Example:
```csharp
#if WINDOWS
// Windows 特定的實作
public class WindowsShutdownHandler : IShutdownHandler
{
    // Windows Forms + WndProc 實作
}
#endif

#if LINUX
// Linux 特定的實作
public class LinuxShutdownHandler : IShutdownHandler 
{
    // Signal handling 實作
}
#endif
```

### P6: CDD 理念的實踐與最佳實務
Problem: 如何在採用容器驅動開發理念時，平衡簡化開發和滿足技術需求之間的矛盾。
Root Cause: 理想的簡化目標與實際的技術限制之間存在差距，需要在保持 CDD 理念的同時解決具體的技術問題。
Solution:
- 接受必要的技術複雜度來滿足核心需求
- 建立可重用的基礎設施來簡化重複工作
- 將複雜的實作細節封裝在框架或基底類別中
- 提供清楚的文件和範例讓其他開發者可以快速上手
Example:
```csharp
// 提供基底類別封裝複雜的事件處理
public abstract class ContainerizedService
{
    protected abstract void OnServiceStart();
    protected abstract void OnServiceStop();
    
    // 內部處理所有複雜的 Windows 事件邏輯
    private void SetupEventHandling() { /* 複雜實作 */ }
}

// 開發者只需繼承並實作業務邏輯
public class MyService : ContainerizedService
{
    protected override void OnServiceStart() { /* 業務邏輯 */ }
    protected override void OnServiceStop() { /* 清理邏輯 */ }
}
```

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本，基於原始文章生成 embedding content
- 包含完整的 metadata、摘要、問答對和解決方案
- 遵循 embedding-structure.instructions.md 規範
