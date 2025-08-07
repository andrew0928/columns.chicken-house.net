# Fiddler 跟 TFS 相衝的問題解決 - II

## 摘要提示
- TFS 與 Fiddler 衝突: 同時開啟時，TFS 取檔常因 Fiddler 改寫 IE Proxy 而失效。  
- Proxy 自動切換: 目標是在 Fiddler 開始／結束擷取時，自動備份與還原 WinINET Proxy 設定。  
- Fiddler Script 機制: 透過修改 CustomRules.js 的 OnAttach 方法插入自定程式碼。  
- WinINETProxyInfo 類別: Fiddler 內建類別可讀寫 IE Proxy，但在 Script 域無法直接存取。  
- AppDomain 隔離: Fiddler 動態編譯 Script 並載入至獨立 AppDomain，造成型別無法解析。  
- Reflection 操作: 多次嘗試以反射跨域呼叫 Fiddler.WinINETProxyInfo 皆告失敗。  
- A/B/C/D 計劃: 作者依序提出四套解法，前三套因存取權限或 AppDomain 受阻。  
- 外掛 Console 程式: 最終以獨立 myproxycfg.exe 修改 Proxy，於 Script 中以 Process.Start 執行。  
- 成功還原 Proxy: Capture 結束即恢復原設定，VPN、無線網卡等情境亦可自動處理。  
- 懶人動機: “懶” 是技術進步的推手，終結手動切換 Proxy 的麻煩。

## 全文重點
作者延續上一篇，說明如何解決 Fiddler 與 TFS 在 Proxy 設定上的相衝問題。核心需求是讓 Fiddler 在開始擷取封包時自動改寫 IE Proxy 為 127.0.0.1:8888，停止擷取時再恢復原設定；同時在 Proxy 例外名單加上公司內部 TFS 伺服器網域，使 TFS 取檔不再被攔截。  
初步構想是直接於 Fiddler 的 CustomRules.js 中，在 OnAttach 事件呼叫內建類別 WinINETProxyInfo 完成四行設定。實作過程卻面臨多重技術障礙：  
1. 直攻 Fiddler 主程式 (A 計劃) 時，發現關鍵欄位為 private，無法外部存取。  
2. B 計劃改從 Script 呼叫 WinINETProxyInfo，但 Fiddler 於獨立 AppDomain 編譯 Script，導致類別解析失敗。  
3. C 計劃利用 Reflection 間接呼叫，同樣因跨域受限而失敗。  
最終 D 計劃採取「脫褲子放屁」的折衷做法：將修改 Proxy 的程式碼獨立成 console 應用 myproxycfg.exe，置於 Fiddler 目錄，再於 Script 中以 Process.Start( ) 執行。此法雖然多了一個可見的執行檔，但成功達成自動切換 Proxy 的目標，並且能同時解決 VPN、無線網路不同介面下 Proxy 未同步的老問題。作者以此案例自嘲「懶才是資訊科技進步的原動力」，並宣布問題圓滿落幕。

## 段落重點
### 問題與流程規劃
作者首先描述 Fiddler 改寫 IE Proxy 造成 TFS Get Latest 失敗的痛點，並規劃三步驟流程：①啟動時備份 Proxy；②改為本機 127.0.0.1:8888；③於 OnAttach 事件加掛自訂 Script。另指出在 VPN 或無線網卡下，Fiddler 只改「區域連線」的 Proxy 也常失效，因此更需自動化。

### A 計劃：直接存取 Fiddler 內部 Proxy 物件
透過 Reflector 追蹤 Fiddler 主程式 frmViewer，鎖定靜態欄位 oProxy，卻發現 WinINETProxyInfo 之 piPrior 與 piThis 皆為 private，無法藉反射修改，計劃宣告失敗。

### B 計劃：於 Script 呼叫 WinINETProxyInfo
改寫一段 console 程式驗證 WinINETProxyInfo 可成功改 Proxy，將相同程式碼貼進 CustomRules.js 卻因 Script 編譯時無法解析該型別而出現 Compilation Error，問題歸咎於 Fiddler 以獨立 AppDomain 載入 Script。

### C 計劃：以 Reflection 間接呼叫
為繞過型別解析問題，嘗試在 Script 內動態 Assembly.LoadFrom("Fiddler.exe")，並以反射呼叫 WinINETProxyInfo 成員，然而執行結果與 B 計劃相同，再次被 AppDomain 隔離攔下。

### D 計劃：外掛 EXE 強制改 Proxy（最終成功）
最終採取外掛策略：將修改 Proxy 的四行程式寫成 myproxycfg.exe，置於 Fiddler 目錄，Script 中僅以 Process.Start 啟動。Fiddler 開始擷取時自動執行 EXE 改 Proxy，停止時由 Fiddler 還原設定，VPN、無線網卡亦適用；雖多出一個檔案，卻徹底解決衝突。

### 結語：懶人驅動的技術解法
作者自嘲「懶」促使他走完四套方案、深入理解 AppDomain 與反射邊界，最終用最務實的方式完成自動切換 Proxy，也證明「能動就好」往往是開發者最真實的需求。