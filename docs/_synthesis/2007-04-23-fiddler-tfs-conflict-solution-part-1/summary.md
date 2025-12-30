---
layout: synthesis
title: "Fiddler 跟 TFS 相衝的問題解決 - I"
synthesis_type: summary
source_post: /2007/04/23/fiddler-tfs-conflict-solution-part-1/
redirect_from:
  - /2007/04/23/fiddler-tfs-conflict-solution-part-1/summary/
---

# Fiddler 跟 TFS 相衝的問題解決 - I

## 摘要提示
- Fiddler 代理原理: 以本機代理攔截所有 HTTP 流量，便於除錯 AJAX 與一般網路請求
- VS2005 與 TFS 衝突: 啟用 Fiddler 後，Visual Studio 2005 的 TFS 連線會被卡住
- 401 驗證失敗: Fiddler 日誌顯示 HTTP 401，疑似驗證資訊未正確轉送至伺服器
- 錯誤訊息迷惑性: VS2005 顯示的錯誤訊息與實際 401 問題看似無關，增加排查難度
- 正規解法方向: 讓 VS2005 的驗證流程能順利穿過 Fiddler 代理
- 臨時解法有效: 將 TFS 網址加入 IE 的 Proxy Bypass 清單即可恢復正常
- 自動化需求: 希望由 Fiddler 自動設定代理時，同步把 TFS 網址加入忽略清單
- 設計流程三步: 儲存現況設定、設置 127.0.0.1:8888、在 OnAttach 腳本中追加忽略
- 腳本調整挑戰: 嘗試在 FiddlerScript 中改寫設定時遇到多重困難
- 系列文結尾: 問題待續，預告後續會分享細節與解法

## 全文重點
作者介紹 Fiddler 作為 HTTP 除錯代理工具的基本原理：啟動後將系統的 HTTP 流量導向本機代理（預設 127.0.0.1:8888），讓開發者能清楚觀察與伺服端的通訊，特別有助於 AJAX 等前端動態互動的除錯。不過在實務使用上，作者常與 Visual Studio 2005 及 Team Foundation Server（TFS）搭配，卻發現只要 Fiddler 啟用，VS2005 與 TFS 間的 HTTP 連線就會被卡住，無法正常工作。

從 Fiddler 日誌能看到 HTTP 401 的回應，顯示身分驗證未通過代理順利傳遞至伺服器，導致伺服器回應未授權。更棘手的是 VS2005 的錯誤訊息並未直指驗證或代理問題，造成診斷方向容易偏離。理想的標準解法是讓 VS2005 的驗證流程能「穿透」Fiddler 代理並被伺服器接受，但在時間與複雜度考量下，作者採取了一個務實的暫時方案：啟動 Fiddler 使其自動調整 IE 的 Proxy 設定後，將 TFS 網址加入「不使用代理伺服器的位址」清單（bypass host list），就能避免 TFS 流量被 Fiddler 攔截，連線恢復正常。

接著作者思考如何把這個手動步驟自動化：期望 Fiddler 在接管系統代理設定時，同步將 TFS 網址自動加入忽略清單。規劃流程為三步：先儲存現有 Proxy 設定、將 WinINET 代理改為 127.0.0.1:8888、最後在 Fiddler 的 OnAttach 事件腳本中重用設定程式碼並插入 TFS 的 bypass 值。雖然構想清晰，但實作過程遇到不少意外困難，作者於文末以「下期待續」收束，預告後續將分享更完整的技術細節與解決策略。

## 段落重點
### 問題背景與症狀：Fiddler 啟用後 TFS 連線被攔
作者說明 Fiddler 的工作機制：啟動後成為系統層級的 HTTP 代理，攔截並顯示所有流量，對偵錯 AJAX 相當關鍵。實務中，當作者同時使用 VS2005 與 TFS 時，只要 Fiddler 開著，VS 與 TFS 的連線就卡住不動。從 Fiddler 的記錄可見 HTTP 401 未授權，推測是 VS2005 發出的身分驗證資訊沒有透過代理正確傳到 TFS 伺服器，導致伺服器回應 401；然而 VS2005 給出的錯誤訊息看似與此無關，增加除錯成本。此現象揭示了「開發工具的背景連線」在被代理攔截時，若未妥善處理驗證轉交（如 NTLM/Negotiate/Kerberos 等），就可能出現權限錯誤。作者指出正規解法應該是調整設定或流程，使 VS2005 的驗證能穿過 Fiddler，但短期內並未採行此路徑。

### 臨時解法與自動化構想：bypass TFS 與 FiddlerScript 挑戰
作者採取的暫時解法是讓 TFS 連線不走 Fiddler：先啟動 Fiddler 讓其自動改寫 IE/WinINET 的 Proxy 設定，再把 TFS 網址加入「不使用代理伺服器」的清單（bypass host list）。如此 TFS 交通不會被 Fiddler 攔截，VS 與 TFS 連線恢復正常。為減少每次手動動作，作者規劃自動化流程：1) 由 Fiddler 儲存現有代理組態；2) 將 WinINET 代理改為 127.0.0.1:8888；3) 在 OnAttach 事件中以腳本重用第 2 步的設定碼並加上 TFS 的 bypass 值。此流程若能實作，將在啟用 Fiddler 的同時自動套用忽略條目，兼顧除錯與 TFS 使用。然而實作階段出現多重技術障礙（如如何在 FiddlerScript 介入 OS 代理設定、處理字串格式與多項 bypass、權限/API 限制等），進展不如預期。作者以「下期待續」作結，表示後續將分享遇到的具體問題與解方。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - HTTP/HTTPS 基本概念與狀態碼（特別是 401 Unauthorized）
   - Proxy/WinINET/IE 代理設定與 bypass 機制
   - Fiddler 的工作原理（本機代理 127.0.0.1:8888）
   - Visual Studio 2005 與 TFS 的 HTTP 連線與驗證流程

2. 核心概念：
   - Fiddler 作為系統 Proxy：Fiddler 會接管 WinINET 的代理設定，使所有 HTTP 流量經過 127.0.0.1:8888
   - VS2005 與 TFS 的連線衝突：Fiddler 開啟後，VS2005 對 TFS 的 HTTP 連線可能因驗證未正確透傳而回應 401
   - Proxy bypass 清單：將 TFS 網址加入 bypass 清單可讓 VS2005 直接連線 TFS、避開 Fiddler
   - 自動化調整：透過 Fiddler 腳本（OnAttach）或程式碼修改 WinINET 代理與 bypass 清單，實現自動化

3. 技術依賴：
   - VS2005/TFS 連線依賴 HTTP/WinINET
   - Fiddler 依賴系統（IE/WinINET）代理設定來攔截流量
   - bypass 清單影響是否經過 Fiddler 代理
   - 腳本自動化依賴 FiddlerScript/事件（如 OnAttach）來修改設定

4. 應用場景：
   - 使用 Fiddler 偵錯 AJAX 或一般 HTTP 請求時，仍需正常使用 VS2005 的 TFS 功能
   - 在偵錯環境中避免關閉 Fiddler又能讓 TFS 不被攔截
   - 以腳本或批次方式，啟用 Fiddler 時自動設定/還原代理與 bypass

### 學習路徑建議
1. 入門者路徑：
   - 了解 Fiddler 基本原理與介面操作（啟動、擷取、檢視請求/回應）
   - 熟悉 HTTP 狀態碼，特別是 401 的意義
   - 了解 IE/WinINET 代理設定與 bypass 清單的作用與設定位置
   - 嘗試在開啟 Fiddler 時，手動將 TFS 網址加入 bypass，驗證問題解決

2. 進階者路徑：
   - 研究 VS2005 與 TFS 的連線流程與常見驗證行為
   - 探索 Fiddler 的 Auto-Configure（自動改 IE Proxy）機制
   - 學習 FiddlerScript，理解 OnAttach/OnDetach 等事件
   - 練習用程式碼（或腳本）讀取/備份/修改 WinINET 代理與 bypass 清單

3. 實戰路徑：
   - 建立啟動 Fiddler 的自動化流程：
     1) 啟動前先儲存目前 Proxy 設定
     2) 設定代理為 127.0.0.1:8888
     3) 在 OnAttach 中加入 TFS 網址至 bypass 清單
   - 設計關閉/還原流程：Fiddler 關閉或需要停用代理時，自動還原原始 Proxy 設定
   - 以日誌驗證：使用 Fiddler/VS2005 驗證 TFS 連線不再出現 401

### 關鍵要點清單
- Fiddler 為本機 Proxy：啟動後會把系統代理改為 127.0.0.1:8888 攔截 HTTP 流量 (優先級: 高)
- VS2005 與 TFS 使用 HTTP：其連線可能受到系統代理與驗證傳遞影響 (優先級: 高)
- 401 Unauthorized 問題：表示驗證未通過或未被正確透傳至 TFS (優先級: 高)
- Proxy bypass 清單：將特定主機繞過代理，可避免 Fiddler 攔截該連線 (優先級: 高)
- 手動解法：在 Fiddler 啟動後，將 TFS 網址新增到 bypass 清單即可恢復 VS2005 與 TFS 連線 (優先級: 高)
- 自動化目標：讓 Fiddler 自動調整代理時，同步把 TFS 網址加入 bypass (優先級: 高)
- 設定保存：啟用 Fiddler 前先儲存現有 Proxy 設定，便於後續還原 (優先級: 中)
- WinINET/IE 代理關聯：VS2005 與一般應用多依賴 WinINET 設定，需從此處著手 (優先級: 中)
- FiddlerScript OnAttach：在附加事件中注入邏輯，自動調整代理與 bypass (優先級: 中)
- 設定順序重要：先設代理、再補上 bypass，避免過程中 TFS 連線被攔截 (優先級: 中)
- 驗證與回應觀察：用 Fiddler 觀察請求/回應，確認是否仍出現 401 (優先級: 中)
- 風險與困難：實作過程可能遇到 API/權限/時機等問題（文中指出「困難重重」）(優先級: 中)
- 還原機制：關閉 Fiddler 或完成偵錯後，應還原原始 Proxy 設定 (優先級: 中)
- 避免過度攔截：僅對需要偵錯的站點走代理，其他（如 TFS）走 bypass，降低副作用 (優先級: 低)
- 維運文件化：將自動化流程與逐步操作文件化，便於團隊成員套用 (優先級: 低)