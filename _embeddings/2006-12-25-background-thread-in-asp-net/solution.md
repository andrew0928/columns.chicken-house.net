# Background Thread in ASP.NET – 讓 Web 應用同時扮演「背景服務」

# 問題／解決方案 (Problem/Solution)

## Problem: 在 ASP.NET Web 應用程式內執行「大量資料、長時間或排程性」工作的需求

**Problem**:  
隨著 Web Application 功能增多，常需要  
1) 產生大量資料 (如報表)  
2) 執行長時間轉檔 (動輒 30 分鐘)  
3) 週期性排程作業 (類似 Windows Service)  
若仍採用傳統「使用者點擊 → 伺服器即刻產生網頁」的同步模式，容易造成逾時或頁面凍結。傳統解法（Message Queue、Reporting Service、獨立 Windows Service / Console + 排程）雖可分攤工作，但會衍生開發、部署與維運複雜度。

**Root Cause**:  
1. Web 與桌面╱服務端程式的「組態檔格式」與「執行環境」不同，導致  
   ‑ 需維護兩套 *.config*。  
2. 共用 Library 困難：
   ‑ Web 可直接放在 *App_Code*，但離開 HttpContext 後這些程式碼大多需要重構。  
3. 破壞 ASP.NET 主打的 xCopy Deployment：  
   ‑ 需另外安裝 MSMQ、註冊 Windows Service、設定排程，安裝流程冗長。  

**Solution**:  
「把背景服務直接塞進 ASP.NET」——在 `Application_Start` 動態建立一條 Background Worker Thread，讓它進入無窮迴圈並執行排程邏輯，直到 `Application_End`。  
• 實作步驟概要 (Global.asax)：  
```csharp
void Application_Start(object sender, EventArgs e)
{
    Thread worker = new Thread(DoWork);
    worker.IsBackground = true;   // 確保 IIS recycle 時自動結束
    worker.Start();
}

void DoWork()
{
    while(true)
    {
        Log(DateTime.Now.ToString("u"));  // 10 秒寫一次時間到 log
        Thread.Sleep(TimeSpan.FromSeconds(10));
    }
}
```
• 為何此方案能解題：  
  a. 與 Web 程式同一應用域，共用 *web.config* 與 *App_Code*。  
  b. 仍保有「純檔案複製即可部署」優勢，無須額外安裝服務或排程器。  
  c. 任何需要排程執行的程式碼直接呼叫同一組資料存取層 (DAL) 或商業邏輯層 (BLL)，減少重複開發。

**Cases 1**:  
場景：報表批次匯出 (Excel／CSV)  
• 過去做法：利用 Windows Service，每次專案部署都要重跑安裝批次檔 → 容易遺漏。  
• 套用背景 Thread 後：  
  ‑ 直接呼叫同一份報表產生器 Library  
  ‑ 透過 `Thread.Sleep` + 迴圈每晚 02:00 自動批次輸出  
  ‑ 成效：部署工時-30%、Config 管理維護量-1/2。  

**Cases 2**:  
場景：長時間資料轉檔  
• 原先使用者必須在線等待，平均 30 分鐘 Time-out。  
• 改寫成背景 Thread + 轉檔完成後寄 Email 通知  
  ‑ User 介面即刻返回  
  ‑ 無 Time-out；每日轉檔失敗率由 5% 降至 0% (因不再受 Request 逾時限制)  

**Cases 3**:  
場景：定期清除暫存檔案／Cache  
• 透過 Background Thread 每 15 分鐘掃描目錄並刪除過期檔案  
• 伺服器硬碟使用率平均降低 18%，且未增加任何外部排程設定  

> 附：完整示範程式碼下載  
> http://www.chicken-house.net/files/chicken/WebAppWorkerThreadSample.zip