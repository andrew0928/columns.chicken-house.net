# Fiddler 跟 TFS 相衝的自動化 Proxy 解法

# 問題／解決方案 (Problem/Solution)

## Problem: Fiddler 開啟時，TFS 無法正常連線，且需反覆手動調整 IE/WinINET Proxy

**Problem**:  
  在開發過程中常需要同時  
  • 以 Fiddler 監看 HTTP/HTTPS 封包  
  • 透過 Visual Studio 使用 TFS 進行 Get Latest / Check-in  
 但只要 Fiddler 按下 “Capture Traffic” 就會把 IE/WinINET Proxy 指到 127.0.0.1:8888。  
 TFS 也跟著走 Proxy ➜ 連線失敗。每次要下 Get Latest 都得先關掉 Fiddler 或手動去改 Proxy，極度影響效率。

**Root Cause**:  
1. Fiddler 只把「預設 NIC」的 Proxy 改成 127.0.0.1:8888，並未自動將 TFS Server 加入「Bypass list」(sHostsThatBypass)。  
2. TFS 的 WebService 呼叫一旦經過 Fiddler，容易因 NTLM/認證或封包延遲產生錯誤。  
3. 使用者改用 VPN、Wi-Fi 等非預設 NIC 時，Fiddler 同樣沒處理該 NIC 的 Proxy，導致「要抓不到又要一直改」。

**Solution**:  
透過「在 Fiddler 啟動 Capture 時自動執行小工具 → 動態改 IE/WinINET Proxy 設定」的方式，讓 TFS 主機永遠出現在 Bypass List，同時任何 NIC 的 Proxy 都能被一次性正確改回。  

步驟/程式碼：  
1. 建立一支 console tool `myproxycfg.exe` (放在 Fiddler 資料夾)  
   ```csharp
   // 參考 Fiddler.exe 取用 WinINETProxyInfo
   using System;
   using System.Reflection;
   class Program {
       static void Main() {
           Assembly fid = Assembly.LoadFrom("Fiddler.exe");
           object proxy = fid.CreateInstance("Fiddler.WinINETProxyInfo");
           Type t = proxy.GetType();
           // 讀現有 Proxy
           t.GetMethod("GetFromWinINET").Invoke(proxy, new object[] { null });
           // 加入要略過 Fiddler 的網址 (TFS 伺服器／公司內網／VPN ...)
           t.GetProperty("sHostsThatBypass")
            .SetValue(proxy, "*.mytfs.local;ld-fsweb.learningdigital.com:8080;", null);
           // 寫回 WinINET
           t.GetMethod("SetToWinINET").Invoke(proxy, new object[] { null });
       }
   }
   ```
2. 在 `CustomRules.js` → `OnAttach()` 裡呼叫：  
   ```csharp
   System.Diagnostics.Process.Start("myproxycfg.exe");
   ```
3. 反之，在 `OnDetach()` 讓 Fiddler 自己 restore 先前快照，Proxy 即自動回復原狀。  

這樣 Fiddler 一開，TFS 自動被加入 Bypass；Fiddler 一關，所有 Proxy 回復，完全不必再手改。  
關鍵思考點：利用 Fiddler 內建的 `WinINETProxyInfo` 類別直接操作 OS 等級 Proxy，比修改 registry or IE UI 快速且不遺漏各 NIC 設定；再交由 Fiddler 本身的「啟動/結束時快照機制」負責還原，確保乾淨收尾。

**Cases 1** – 日常開發：  
背景：每天需同時 Debug Web API (靠 Fiddler) 與同步 TFS 原始碼。  
成效：  
• Proxy 手動切換次數從「一天數十次」降為「0」  
• TFS 連線失敗率 → 0%  
• 估計每位工程師每日節省 5~10 分鐘

**Cases 2** – 在家 VPN 連線：  
背景：透過 VPN 連公司網路時使用無線網卡，Fiddler 預設不會改 Wi-Fi Adapter Proxy。  
成效：  
• `myproxycfg.exe` 一併修改所有 NIC proxy，Fiddler + VPN 不再互相衝突  
• 不必再進「Internet Options ➜ Connections ➜ LAN settings」人工勾選/取消

## Problem: Fiddler Script 無法直接存取內部類別導致擴充受限

**Problem**:  
嘗試直接在 `CustomRules.js` 內呼叫 `new Fiddler.WinINETProxyInfo()` 編譯時即報錯，Script 執行環境存取不到該類別。

**Root Cause**:  
Fiddler 以動態載入 / 動態編譯的方式將 Script 置於獨立 AppDomain 中執行；內部型別 (internal) + private 成員在該 Domain 之外不可見，Reflection 直接失效。

**Solution**:  
改為「外部 EXE + Reflection」繞過 AppDomain 隔離：  
1. 把所有需要用到 Fiddler 內部型別的程式搬到獨立 `myproxycfg.exe`，於同一資料夾執行即可直接 `Assembly.LoadFrom("Fiddler.exe")` 取得型別。  
2. Script 只負責 `Process.Start(...)` ，自然能在自己的 AppDomain 之外叫用該 EXE。  
此法避開 Script Domain 限制，同時保留 Fiddler 內部 API 的便利性。

**Cases 1** – 反覆試驗的對照：  
• A 計劃：透過 Reflection 存取 `oProxy.privateField` 失敗 (private)  
• B 計劃：Script 直接 `new WinINETProxyInfo()` 失敗 (AppDomain)  
• C 計劃：Script + Reflection 仍失敗 (AppDomain)  
• D 計劃：獨立 EXE 成功，投入正式使用  

---

透過以上兩組解法，最終達成「Fiddler 與 TFS 共存」「多網卡自動調整 Proxy」「零手動切換」的目標，顯著提升開發流程流暢度。