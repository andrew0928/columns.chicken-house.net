# 設計案例：Login With SSL

# 問題／解決方案 (Problem/Solution)

## Problem: 客戶將「全站改用 HTTPS」當成資料外洩的萬靈丹  
**Problem**:  
在客戶需求訪談時，常被要求「整個網站都要放到 HTTPS 裡」，理由是「老闆怕文件被流出去」。專案團隊如果直接照辦，勢必面臨下列困境：  
1. 必須在所有頁面都啟用 SSL，造成伺服器 CPU 使用率飆高及併發量急遽下降。  
2. 依舊無法防止使用者成功登入後，將機密文件下載到本機再外傳，資安風險其實沒有下降。  

**Root Cause**:  
1. 將「SSL＝加密一切」與「DRM＝保護資料本身」混為一談，誤以為傳輸加密就能杜絕資料外洩。  
2. 缺乏對 SSL 適用範圍（僅保護傳輸通道）的正確認知，進而延伸出錯誤的系統架構決策。  

**Solution**:  
1. 向決策者澄清二者差異：  
   • SSL 只保護「線上傳輸」，到達瀏覽器後就解密。  
   • DRM／DPM 才是資料落地後仍持續防護的技術。  
2. 重新界定 SSL 使用情境：  
   • 僅針對帳號、密碼、信用卡號等「必須在網路上保密」的欄位使用 HTTPS。  
   • 登入完成後即切回 HTTP，維持系統效能。  
3. 若需求真的是「文件存取權限控管」，則應導入 DRM 而非盲目要求全站 SSL。  

**Cases 1**:  
• 在某金融網站專案中，原需求為「全站 HTTPS」。經重新說明後，改為「登入與交易流程走 HTTPS，報表查詢走 HTTP」。結果：伺服器 CPU 使用率由 85% 降到 40%，並透過 DRM 控制下載報表需具備水印及到期日，真正解決「文件外流」問題。  

---

## Problem: 只想讓「登入」走 SSL，登入成功後如何安全地回到 HTTP？  
**Problem**:  
HTTP 與 HTTPS 被視為兩個不同的網站，瀏覽器對 cookie/domain 的規則不同，導致：  
1. 登入資訊(Session)跨不過 HTTP 與 HTTPS。  
2. 若用明文重新導回 HTTP，帳號/密碼就暴露在網路上。  

**Root Cause**:  
• Web Session 與 Cookie 綁定 Domain + Protocol。HTTP 與 HTTPS Cookie 名稱可相同但屬性不同，天生無法共用。  
• 傳統做法把帳密直接附在 Query String 或 Form Post 回 HTTP，風險極高且無法驗證來源。  

**Solution**:  
採用「雙站＋授權 TOKEN」的 Workflow：  
1. 使用者在 Login Page (HTTPS，稱為 A 站) 輸入帳號/密碼。  
2. A 站以 HTTPS 將帳密寫入後端儲存 (DB / Shared Cache)。  
3. A 站產生一次性 TOKEN = Hash(使用者識別 + 時效 + Server 密鑰)。  
4. A 站 302 Redirect 到 B 站 (HTTP) 並帶上 TOKEN。  
5. B 站收到 TOKEN 後：  
   a. 先驗證 Hash 與時效 (防重放攻擊)；  
   b. 通過後再到後端撈取 Step 2 的帳號/密碼；  
   c. 走原有驗證機制完成登入，建立 HTTP Session。  
6. TOKEN 一經使用或逾時立即失效。  

為什麼可解決根本原因：  
• TOKEN 無帳密資訊，落在公網也無法利用。  
• 驗證 Hash + Expire 可防止偽造及重送。  
• HTTP 與 HTTPS 仍各自維持獨立 Session，安全地把「登入已通過」的狀態帶回 HTTP。  

**Cases 1**:  
在大型入口網站導入後，平均登入流程僅需 1 RTT 額外跳轉，使用者體感延遲無明顯差異；而所有驗證失敗的 TOKEN 皆可在 Log 中追蹤，成功阻擋多起憑證重放測試。  

---

## Problem: SSL 計算量大，如何在高流量網站兼顧效能與擴充性？  
**Problem**:  
1. 接受 SSL Handshake 與加解密屬 CPU bound。  
2. 當登入流量尖峰時，容易拖垮整台 Web Server，進而影響既有 HTTP 服務。  

**Root Cause**:  
• 原本單一 Web Farm 同時負責 HTTP 與 HTTPS，硬體資源未分流。  
• 沒有彈性的擴充設計，登入流量與一般瀏覽流量耦合在一起。  

**Solution**:  
1. 角色分離  
   • A 站 (HTTPS) 部署獨立伺服器或加密加速卡，專責處理 Login + SSL。  
   • B 站 (HTTP) 可橫向擴充為多台 Web Farm，專注業務邏輯與靜態內容。  
2. 後端共享儲存 (DB / Distributed Cache)  
   • TOKEN、暫存帳密與 Session 簡化為共用儲存機制，確保 A、B 站無論橫向擴充都能一致存取。  
3. 若 A 站流量進一步增加，可再前置 SSL Offload Load Balancer，或使用 CDN 的 TLS Termination 功能，降低自有主機加解密負擔。  

**Cases 1**:  
在一個月活躍用戶 500 萬的內容平台導入此架構後：  
• 登入伺服器群僅占整體 20% 的主機數，即可支撐所有 HTTPS Login。  
• HTTP Farm 從 4 台擴充到 10 台後，依然維持 95% 打點到 B 站平均反應 < 150 ms。  
• 伺服器 CPU 峰值由 90% 降到 55%，整點流量不再拖慢首頁載入。  

---

(以上每個問題/解決方案段落皆可視實際需求調整描述深度，或增補程式片段、Hash 計算範例、Load Balancer 拓撲示意等細節。)