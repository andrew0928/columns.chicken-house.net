# Tips: 在 .NET Console Application 中處理 Shutdown 事件

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼需要在 .NET Console Application 中攔截 Shutdown 事件？
在微服務及容器化場景下，服務關閉前必須先向 Service Discovery (如 Consul) 通報下線，否則舊節點仍會被視為可用而導致流量錯誤。若能在程式終止前攔截 Shutdown 事件並執行清理邏輯，就能在 Docker orchestration 發出的 `docker stop` 指令時自動完成下線流程，省去人工設定。

## Q: 一個 Console Application 可能因哪些情況而結束？
1. 程式自行結束  
2. 使用者按 CTRL-C / CTRL-BREAK  
3. 關閉視窗或在工作管理員 End Task  
4. 使用者登出 (Log off)  
5. 系統關機 (Shutdown)  
6. 非預期終止（強制結束、斷電等）

## Q: 試過的第一個方法是什麼？為何失敗？
方法一使用 Win32 API `SetConsoleCtrlHandler` 來攔截 `CTRL_C_EVENT、CTRL_BREAK_EVENT、CTRL_CLOSE_EVENT、CTRL_LOGOFF_EVENT、CTRL_SHUTDOWN_EVENT`。  
此法可正常處理 CTRL-C 與關閉視窗，但在 Windows Container 內對 `docker stop` 無效，原因是 `CTRL_LOGOFF_EVENT` 與 `CTRL_SHUTDOWN_EVENT` 只會送給 Windows Service，而不會送給一般 Console Application。

## Q: 為何不改寫成 Windows Service 或 Windows Form？
• Windows Service／IIS Host 雖易處理關機事件，但在 Container 內並非必要，且部署較複雜。  
• Windows Form 需要 GUI；而微服務通常無 UI。  
• Console Application 最貼近容器的啟動模式，搭配 `docker run -d --restart always` 已能達成背景執行及生命週期管理，因此作者堅持以 Console Application 完成。

## Q: 在 Windows Container 中正確攔截 `docker stop` 的做法是什麼？
做法二：於 Console Application 內動態建立一個「隱藏的 WinForm」，讓程式擁有 Message Pump。  
1. 使用 `Application.Run(form)` 啟動隱藏視窗。  
2. 於 `Form.WndProc` 中攔截 `WM_QUERYENDSESSION` (0x11)。  
3. 收到訊息時設定 `AutoResetEvent` 喚醒主執行緒，執行關閉前清理邏輯。  
此方式已在 Windows 10 / Windows Server 2016 / 1709 Container 內驗證可於 `docker stop` 時成功接收到訊號。

## Q: 攔截 `WM_QUERYENDSESSION` 的範例程式碼長怎樣？
```
public partial class Form1 : Form
{
    public AutoResetEvent shutdown = new AutoResetEvent(false);

    protected override void WndProc(ref Message m)
    {
        if (m.Msg == 0x11)        // WM_QUERYENDSESSION
        {
            Console.WriteLine("winmsg: WM_QUERYENDSESSION");
            shutdown.Set();       // 通知主執行緒
            m.Result = (IntPtr)1; // 回覆系統可結束
        }
        base.WndProc(ref m);
    }
}
```
主程式中啟動隱藏表單並等待：
```
var f = new Form1 { ShowInTaskbar = false, Visible = false };
Task.Run(() => Application.Run(f));

Console.WriteLine("Service Started");
f.shutdown.WaitOne();            // 等待關機訊號
Console.WriteLine("Service Stopped");
```

## Q: 針對 Container，要如何驗證程式確實攔截到 Shutdown？
1. 將編譯後程式打包成映像檔  
   `docker build -t demo.console .`  
2. 啟動容器並觀察日誌  
   ```
   docker run -d --name demo demo.console
   docker logs demo -f
   ```  
3. 另開終端機執行  
   `docker stop demo`  
4. 在第一個日誌視窗應看到  
   ```
   Service Started
   winmsg: WM_QUERYENDSESSION
   Service Stopped
   ```

## Q: 若直接使用 `docker rm -f` 強制刪除容器，還能攔截到嗎？
無法。`docker rm -f` 相當於強制終止 Process，不會送出可攔截的關閉訊號。只有正常的 `docker stop` 會先發出可捕捉的訊息。

## Q: 這項經驗帶來的結論是什麼？
1. `SetConsoleCtrlHandler` 不適用於 Container 內的 Console Application Shutdown。  
2. 隱藏 WinForm + `WM_QUERYENDSESSION` 是目前在 Windows Container 中攔截 `docker stop` 的可行解法。  
3. Console Application 仍能在無 GUI 的情況下安全處理終止事件，符合 Container-friendly 的開發模式。