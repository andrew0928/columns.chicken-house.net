# Fiddler 跟 TFS 相衝的問題解決 - I

# 問題／解決方案 (Problem/Solution)

## Problem: 同時開啟 Fiddler 與使用 Visual Studio 2005 之 TFS 功能時，VS 與 TFS 之間的連線被阻斷

**Problem**:  
在開發過程中，工程師習慣同時開啟 Fiddler 觀察 HTTP 流量，並透過 Visual Studio 2005 使用 Team Foundation Server (TFS) 相關功能（Check-in、Get Latest、Work Item 等）。然而，只要 Fiddler 開啟，VS2005 與 TFS 之間的 HTTP 連線就會被卡住，導致所有 TFS 操作失敗。

**Root Cause**:  
1. Fiddler 以「本機 Proxy (127.0.0.1:8888)」方式攔截所有 WinINET 流量。  
2. VS2005 與 TFS 透過 NTLM/Integrated Authentication 交握。  
3. 當身份驗證封包經過 Fiddler Proxy 時，憑證未被正確轉發，TFS 伺服器因此回應 HTTP 401 (Unauthorized)。  
4. VS2005 收到 401 後僅顯示無關錯誤訊息，難以定位問題。

**Solution**:  
將 TFS 網址加入「Proxy Bypass List」，使 VS2005 與 TFS 的流量不經 Fiddler；開發過程仍可讓其他網站流量透過 Fiddler 進行偵錯。為避免每次手動設定：

Workflow (自動化步驟)：  
1. 啟動 Fiddler 時，Fiddler 會自動修改 WinINET Proxy 設定為 `127.0.0.1:8888`。  
2. 在 Fiddler `OnAttach` 事件中加入自定 Script：  
   ```js
   // FiddlerScript 片段 (CustomRules.js)
   static function OnAttach() {
       // Step 1: 讀取當前 Proxy 設定
       var oProxy = Fiddler.Application.Prefs.GetStringPref(
           "Microsoft.Windows.Proxy", "");

       // Step 2: 設定全域 Proxy
       FiddlerApplication.UI.actSetProxyServer("127.0.0.1:8888");

       // Step 3: 取出原 bypass list，加入 TFS 網域
       var bypass = FiddlerApplication.Prefs.GetStringPref(
           "Microsoft.Windows.ProxyBypassList", "");
       if(bypass.Length > 0) bypass += ";";
       bypass += "tfs.mycompany.com";   // ← TFS 網域／IP

       // Step 4: 寫回 bypass list
       FiddlerApplication.Prefs.SetStringPref(
           "Microsoft.Windows.ProxyBypassList", bypass);
   }
   ```
3. 每次 Fiddler `Attach` 時自動完成：  
   • 保存原 Proxy 設定 → 設定 Fiddler Proxy → 追加 TFS 網址到 bypass list。  
4. 關閉 Fiddler 時，WinINET Proxy 會還原，完全不影響其他工具。

此解法讓「VS2005 ↔ TFS」流量直接連線，繞過 Fiddler；其他網站仍被 Fiddler 攔截，兼得偵錯與正常 TFS 運作。

**Cases 1**:  
• 情境：開發人員需 Debug AJAX 呼叫並同時在 VS2005 送出程式碼。  
• 問題：送出程式碼時出現「TF31002: Unable to connect to this Team Foundation Server」。  
• 採用上述腳本後：  
  – Debug 功能正常，可擷取所有前端 HTTP 流量。  
  – TFS 操作 100% 成功率，連線失敗率從原本 100% → 0%。  
  – 時間節省：每日減少 5~10 分鐘手動調 Proxy 或重新登入 TFS 的時間。