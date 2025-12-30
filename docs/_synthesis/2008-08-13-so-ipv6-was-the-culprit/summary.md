---
layout: synthesis
title: "原來是 IPv6 搞的鬼..."
synthesis_type: summary
source_post: /2008/08/13/so-ipv6-was-the-culprit/
redirect_from:
  - /2008/08/13/so-ipv6-was-the-culprit/summary/
---

# 原來是 IPv6 搞的鬼...

## 摘要提示
- IPv6 回傳: Vista x64 + IIS7 預設啟用 IPv6，導致 ASP.NET 取到的 REMOTE_ADDR 是 IPv6 格式
- 舊有程式假設 IPv4: 以拆字串與位元運算方式處理 IPv4，遇到 IPv6 直接失效
- 問題症狀: 以子網判斷是否為內網範圍的程式在新環境上不動作
- Trace 診斷: ASP.NET Trace 顯示 REMOTE_ADDR/REMOTE_HOST 為 IPv6 位址
- 臨時解法-改用 IPv4 連線: 以 http://IPv4/ 取代 localhost 能取回 IPv4（但 DevWeb 受限於 localhost）
- 臨時解法-IIS 綁定: 嘗試 IIS 綁定到 IPv4 不一定如預期，localhost 解析仍走 IPv6
- 臨時解法-編輯 hosts: 將 localhost 映射到 127.0.0.1，確保本機測試走 IPv4
- 臨時解法-停用 IPv6: 直接關閉 IPv6 可解，但屬於破壞性且非最佳解
- 正確作法: 使用 System.Net.IPAddress.Parse 與 AddressFamily 判斷並支援 IPv4/IPv6
- 教訓與最佳實務: 不要手拆 IP 字串與硬編碼，應以 .NET 標準類別與 API 進行通用處理

## 全文重點
作者早年寫了一段 ASP.NET 範例，用來判斷用戶端 IP 是否落在指定內網（例如 192.168.2.0/24）內，做法是把 IPv4 位址以字串切分成四段，再以位元運算和 netmask 比對，以決定是否顯示「Is Intranet? YES」。這段程式在舊環境一直正常，但換到 Vista x64 + IIS7 後突然不動了。打開 ASP.NET Trace 一看，才發現 REMOTE_ADDR/REMOTE_HOST 回傳的是 IPv6 格式，原因是新環境預設開啟 IPv6，IIS7/開發伺服器因此回傳 IPv6 位址，導致原先只支援 IPv4 解析與運算的邏輯崩潰。

為了快速解決，作者測試了幾個臨時方案。第一，改用 IPv4 位址直接連線，例如以 http://192.168.100.40/default.aspx 取代 http://localhost/，可讓伺服器回傳 IPv4；但此法對只接受 localhost 的開發伺服器（DevWeb）不適用。第二，嘗試在 IIS 綁定只綁 IPv4 位址，不過實測仍可能因 localhost 解析優先走 IPv6 而無效。第三，編輯 C:\Windows\System32\drivers\etc\hosts，移除將 localhost 指向 ::1 的 IPv6 對應，改保留 127.0.0.1，讓 localhost 解析回到 IPv4，此法對 DevWeb 亦有效。第四，乾脆停用 IPv6，雖能解決，但屬於粗暴且不建議的手段。

本文的關鍵教訓是：不要以硬拆字串與手工位元運算來處理 IP 位址，因為一旦遇到 IPv6 便失效。正確作法應使用 .NET 中的 System.Net.IPAddress 類別，例如以 IPAddress.Parse 將字串轉為 IPAddress 物件，再以 AddressFamily 判斷類型（InterNetwork/InterNetworkV6），並在比對邏輯上支援兩種協定或明確限制使用 IPv4。若需做子網比對，應採用支援 IPv4 與 IPv6 前綴長度的標準算法或現成函式庫，避免自己實作易錯的字串切割與位元乘加邏輯。總結來說，問題表面像是「Vista/IIS7 的怪現象」，本質是程式只針對 IPv4 設計而未考量 IPv6 的不可避免，隨著系統預設啟用 IPv6，早期寫法自然翻車。短期可以用 hosts 或固定 IPv4 連線權宜處理，長期應改寫為協定無關、以框架 API 為核心的實作。

## 段落重點
### 問題背景與原始程式
作者早期為了在網頁中辨識是否為公司內網使用者，寫了一段 ASP.NET 程式：從 Request 的 REMOTE_HOST 取得用戶端 IP，將其以「.」分割成四段，逐段換算成 32 位元整數，搭配 netmask 做位元 AND 來判斷是否命中子網（例如 192.168.2.0/24）。頁面載入時，若命中則顯示 Is Intranet? YES。這類程式在過去以 IPv4 為主的環境中簡單有效，且作者當時以「拆字串+位元運算」為主要實作方式，並未考慮未來 IPv6 的情境。

### 在 Vista x64 + IIS7 出現的異常
環境升級到 Vista x64 搭配 IIS7 之後，原本一向正常的程式突然不動了。頁面沒有如預期顯示內網結果。由於邏輯單純，初看之下不像是演算法出錯，作者開始懷疑取得用戶端 IP 的來源或格式有變化，或是伺服器端設定導致 Request 內容異常。這類「在新系統上才出現」的問題，往往與預設協定、網路堆疊設定或伺服器回應格式的變更有關，因此作者決定打開 Trace 深入確認取得的原始資料。

### 追查：Trace 顯示 IPv6 導致失效
開啟 ASP.NET Trace 後，赫然發現 REMOTE_ADDR/REMOTE_HOST 回傳的不是熟悉的 IPv4，而是 IPv6 位址。這揭示了關鍵：Vista 預設啟用 IPv6，IIS7 與開發伺服器（DevWeb）會優先以 IPv6 進行連線，導致頁面程式拿到 IPv6 位址。原本以「拆 4 個字節、乘 256 再位元運算」的 IPv4 專用邏輯完全不適用於 IPv6，故而出錯。此時的問題屬於資料格式與協定版本不相容，並非程式碼細節瑕疵。換言之，問題根源是「程式只支援 IPv4 假設」在新環境下不成立。

### 臨時解法四則
為了繼續開發與測試，作者試了幾種權宜之計。1) 以 IPv4 位址直接連線網站（如 http://192.168.100.40/），能迫使回傳 IPv4，不過對限制只接受 localhost 的 DevWeb 不適用。2) 在 IIS 站台綁定指定的 IPv4 位址，理想上應能固定走 IPv4，但實測因為 localhost 解析仍會走 IPv6，導致效用有限。3) 編輯 hosts 檔，移除將 localhost 指向 ::1 的 IPv6 映射，保留 127.0.0.1，讓 localhost 解析回 IPv4；此法對 DevWeb 有效且影響面可控，是相對實用的臨時方案。4) 直接關閉系統的 IPv6，雖可一勞永逸，但屬於粗暴且可能影響其他應用的做法，不建議作為長期解。

### 正確作法與教訓
從維護性與未來相容性來看，正解是改寫程式碼，使用 .NET 的 System.Net.IPAddress 與相關 API 來處理 IP。具體而言：用 IPAddress.Parse 將字串轉為 IPAddress 物件，以 AddressFamily 判斷 InterNetwork（IPv4）或 InterNetworkV6（IPv6），並基於協定類型進行適當的子網比對。對 IPv4 可用位元遮罩比對；對 IPv6 則需使用前綴長度（CIDR）並按 128 位元位址進行比較，或採用支援 IPv4/IPv6 的現成函式庫。更重要的是，避免自行拆字串與硬編碼演算法，因為 IPv6 的表示法與位元長度都不同，手工實作極易出錯。總結：短期可用 hosts 修正或固定走 IPv4 解燃眉之急，長期務必升級為協定無關、以框架 API 為核心的實作，才能在現今預設啟用 IPv6 的環境中穩定運作。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
   - 基礎網路概念：IPv4/IPv6 差異、子網路與 Netmask/Prefix 的概念
   - Windows 與 IIS/ASP.NET 請求流程：Request.ServerVariables、UserHostAddress、Trace
   - 名稱解析與 hosts 檔案作用、回送位址 127.0.0.1 與 ::1
   - C#/.NET 網路 API：System.Net.IPAddress、AddressFamily、Parse/TryParse

2. 核心概念：本文的 3-5 個核心概念及其關係
   - IPv6 預設啟用：在 Vista + IIS7/Dev Web 下，REMOTE_ADDR 可能回傳 IPv6（::1），導致只處理 IPv4 的程式失效
   - 錯誤做法：以字串分割「.」轉 uint 只適用 IPv4，遇到 IPv6 會失敗
   - 正確做法：使用 System.Net.IPAddress 與 AddressFamily，根據位址家族正規處理
   - 臨時解法：強制走 IPv4（改 URL、IIS綁定、hosts 映射、關閉 IPv6）
   - 長久解法：讓程式雙協定相容（protocol-agnostic），避免依賴位址格式

3. 技術依賴：相關技術之間的依賴關係
   - 瀏覽器/客戶端 → 名稱解析（DNS/hosts）→ Windows 網路堆疊（IPv4/IPv6 選路）→ IIS/ASP.NET → Request 物件（ServerVariables/UserHostAddress）
   - .NET 應用程式 → System.Net.IPAddress（Parse/TryParse, AddressFamily, GetAddressBytes）→ 自訂或外部工具進行子網比對

4. 應用場景：適用於哪些實際場景？
   - 內網/外網訪問控制（依子網判斷是否為內部使用者）
   - 依來源 IP 觸發差異化行為（權限、功能開關、風險控管）
   - 記錄與稽核（正確記錄雙協定的來源 IP）
   - 測試/開發環境的行為一致性（localhost 解析、IIS 綁定策略）

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
   - 了解 IPv4 與 IPv6 基本概念與表示法（dotted decimal vs. colon-hex）
   - 學習 ASP.NET 如何取得客戶端 IP（Request.UserHostAddress、ServerVariables["REMOTE_ADDR"]）
   - 使用 IPAddress.Parse/TryParse 解析位址，讀取 AddressFamily 判斷 IPv4/IPv6
   - 打開 ASP.NET Trace 檢視實際收到的位址，觀察 localhost 在不同設定下的值

2. 進階者路徑：已有基礎如何深化？
   - 實作通用的 IP 子網判斷工具：IPv4 使用 mask 比對；IPv6 使用 prefix 長度比對
   - 熟悉 IPAddress.GetAddressBytes、位元運算與大端序比較
   - 研究 IIS 綁定、hosts 解析與 Dev Web（僅允許 localhost）的差異
   - 撰寫單元測試涵蓋 IPv4/IPv6、迴圈位址（127.0.0.1, ::1）、私有位址與公網位址

3. 實戰路徑：如何應用到實際專案？
   - 封裝一個 GetClientIPAddress 方法：正確處理反向代理/Forwarded Headers，回退到 UserHostAddress
   - 封裝 IsInSubnet 支援 IPv4/IPv6（輸入網段可接受 192.168.2.0/24 或 2001:db8::/32）
   - 以設定檔定義允許/拒絕的網段清單，部署於開發/測試/生產環境驗證行為
   - 監控與記錄雙協定來源，加入健全的 fallback 與錯誤處理（TryParse）

### 關鍵要點清單
- 問題癥結：IPv6 預設啟用導致 REMOTE_ADDR 回傳 ::1 等 IPv6 位址，使僅支援 IPv4 的字串解析失效 (優先級: 高)
- 不當作法：以「.」分割字串並組 uint 僅適用 IPv4，遇到 IPv6 一定壞 (優先級: 高)
- 正規 API：使用 System.Net.IPAddress.Parse/TryParse 解析字串到 IPAddress (優先級: 高)
- 位址家族判斷：透過 AddressFamily（InterNetwork/InterNetworkV6）決定後續流程 (優先級: 高)
- 子網比對（IPv4）：以 uint/ulong 與 netmask 進行 AND 比對或使用位元比較 (優先級: 高)
- 子網比對（IPv6）：以位元前綴長度（/64 等）對位元陣列進行前綴比較 (優先級: 高)
- 本機解析差異：localhost 可能解析到 ::1（IPv6）或 127.0.0.1（IPv4），影響開發測試結果 (優先級: 中)
- 臨時解法1：以 IPv4 位址直接連線（http://127.0.0.1/... 或 實際 IPv4）可強制走 IPv4 (優先級: 中)
- 臨時解法2：調整 hosts，將 localhost 指到 127.0.0.1，避免解析到 ::1 (優先級: 中)
- 臨時解法3：IIS 綁定到特定 IPv4；效果依環境而異，需測試驗證 (優先級: 低)
- 臨時解法4：關閉 IPv6 可「解問題」但不建議作為長期方案 (優先級: 低)
- 記錄與除錯：啟用 ASP.NET Trace 或記錄 Request.ServerVariables 以判斷實際位址 (優先級: 中)
- 兼容性原則：以協定無關（protocol-agnostic）方式處理 IP，不依賴位址字串格式 (優先級: 高)
- 安全與維運：在反向代理/負載均衡環境下，需處理 X-Forwarded-For/Forwarded 標頭以取得真實來源 IP (優先級: 中)
- 測試覆蓋：為 IPv4/IPv6、本機位址、私網、公網與無效字串建立單元測試 (優先級: 中)