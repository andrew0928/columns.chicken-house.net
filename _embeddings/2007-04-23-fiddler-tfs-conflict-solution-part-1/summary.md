```markdown
# Fiddler 跟 TFS 相衝的問題解決 - I

## 摘要提示
- Fiddler: 以 Proxy 方式攔截 HTTP 流量、利於偵錯 AJAX 之類隱形封包。  
- VS2005 + TFS 衝突: 只要 Fiddler 開啟，Visual Studio 2005 的 TFS 功能常被卡住。  
- 401 錯誤: 從 Fiddler Log 可見 vs2005 對 TFS 的驗證請求在 Proxy 端被擋下。  
- 錯誤訊息模糊: VS2005 報錯內容與實際 401 驗證失敗互不對應，增加排除難度。  
- 正規解法: 應讓 VS2005 的驗證封包順利通過 Fiddler，但設定繁複。  
- 懶人解法: 開啟 Fiddler 後，將 TFS 網址加入 IE proxy bypass list 即可恢復正常。  
- 自動化構想: 在 Fiddler OnAttach 事件中自動修改 WinINET Proxy 與 bypass 清單。  
- 流程設計: 先存原 Proxy、改成 127.0.0.1:8888、再動態插入 TFS 網址至 bypass。  
- 開發難點: 實際撰寫腳本時遇到多重權限與 API 呼叫限制，進度受阻。  
- 待續: 系列文將於下一篇深入說明問題破解細節及程式碼。

## 全文重點
作者經常同時使用 Fiddler 與 Visual Studio 2005 進行 Web 與 TFS 開發。由於 Fiddler 採用「自架 Proxy」方式攔截 HTTP 封包，當它被啟動後，系統 (WinINET) 會被自動設定成走 127.0.0.1:8888 這支本地端 Proxy。  
然而 VS2005 與 Team Foundation Server 溝通時，需透過 Windows 驗證 (NTLM/Kerberos)。該驗證封包在經過 Fiddler 轉送時未能完整傳遞，造成 Server 端回應 HTTP 401 Unauthorized，導致所有 TFS 功能停擺。VS2005 所呈現的錯誤訊息卻與真正原因無明顯關聯，使得排查更加困難。  

理想做法是調整 Fiddler 或 WinINET 使認證封包能被完整轉送，但作者偏好「快速可行」的替代方案：啟動 Fiddler 讓它自動改 Proxy 後，立即把 TFS 伺服器網址加入 IE「不使用 Proxy 的主機」(bypass list)，於是 VS2005 對 TFS 的流量就能直接繞過 Fiddler，不再出現 401。  

為了避免每次手動修改，作者設計一套自動化流程：  
1. Fiddler 啟動時先儲存現有 Proxy 設定。  
2. 由 Fiddler 將 WinINET Proxy 改成 127.0.0.1:8888 (內建動作)。  
3. 在 Fiddler 的 OnAttach 事件撰寫自訂腳本，複製第 2 步的程式碼並插入額外邏輯，將 TFS 網址同步寫入 Proxy bypass 清單。  

概念看似單純，實作時卻遇到權限、API 相容與腳本語言限制等問題，進度意外受阻。本篇先描述衝突背景與解題思路；真正的腳本細節與錯誤排除過程，將於下一篇揭曉。

## 段落重點
### Fiddler 與 AJAX 偵錯簡介
作者先說明 Fiddler 的工作原理：透過在本機建立 Proxy，將所有 HTTP 流量攔截、記錄與重送，非常適合檢視 AJAX 在瀏覽器背後傳遞的隱藏封包。這部分為文章鋪陳背景，說明為何開發者常需同時開啟 Fiddler 與 VS2005。

### 衝突情境：VS2005 + TFS 功能停擺
當 Fiddler 開啟後，Visual Studio 2005 只要呼叫 Team Foundation Server（如 Check-in、Get Latest）就會無限等待；Fiddler Log 顯示多筆 HTTP 401 回應，而 VS2005 畫面給出的錯誤訊息看似與 Proxy 無關，讓問題診斷變得曲折。

### 初步判讀：驗證封包被阻
經比對，判定是 NTLM/Kerberos 驗證封包在 Fiddler Proxy 端未能被完整處理，而被 TFS 認定為未授權。若讓驗證順利「穿 Proxy」即為正規解，但相關設定與測試流程繁瑣。

### 懶人工法：手動加入 bypass list
作者發現只要在 Fiddler 自動修改 Proxy 之後，立即打開 IE 設定，把 TFS 伺服器網址登錄於「不使用 Proxy 的主機」，VS2005 即可恢復正常。此做法雖不夠優雅，卻能瞬間解決工作卡關。

### 自動化構想與流程設計
為省去每次手動操作，作者計畫利用 Fiddler 的 OnAttach 事件：  
1) 先把原始 Proxy 設定存檔；2) 由 Fiddler 內建機制改成 127.0.0.1:8888；3) 在腳本中呼叫同樣 API，外加修改 bypass list，插入 TFS 網址。如此即能在啟動 Fiddler 的同時，自動完成繞過設定。

### 實作阻礙與伏筆
動手寫腳本後，卻碰到權限不足、COM 介面呼叫差異、腳本語言限制等多項技術障礙。本篇以「下回待續」收尾，預告後續將公開除錯紀錄與最終程式碼。
```
