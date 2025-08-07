# 原來是 IPv6 搞的鬼…

## 摘要提示
- IPv4/IPv6: Vista x64 + IIS 7 預設回傳 IPv6，導致以字串拆解方式偵測 IP 的舊程式失效。  
- 程式範例: 範例程式把 IPv4 切成四段做位元運算，判斷用戶是否位於特定內網。  
- 問題現象: 在 Trace 中看到 REMOTE_ADDR 變成 IPv6 表示法，引發字串 Split(‘.’) 失敗。  
- 臨時解法1: 直接以 http://<IPv4>/… 取代 http://localhost/ ，強迫走 IPv4。  
- 臨時解法2: 在 IIS 網站「繫結」只指定 IPv4 位址（作者測試成效有限）。  
- 臨時解法3: 修改 hosts 檔，移除 ::1 localhost 對應，讓 localhost 指向 127.0.0.1。  
- 臨時解法4: 乾脆在網路卡設定中停用 IPv6。  
- 正規做法: 使用 System.Net.IPAddress.Parse 與 AddressFamily 判斷 InterNetwork / InterNetworkV6，不用手動拆字串。  
- 教訓: 依賴字串格式處理 IP 在多協定環境易出錯，應交由 .NET 內建類別處理。  
- 經驗分享: 文章記錄排除過程，提醒開發者留意作業系統與伺服器預設值改變。

## 全文重點
作者過去撰寫了一段簡易函式庫，用來在 ASP.NET 中取得連入者的 IP 位址，並透過切分 IPv4 字串、轉成四個位元組再做位元運算，以判斷該位址是否落在指定子網。「多年來從未出錯」的程式碼在升級至 Vista x64 與 IIS 7 後突然失效，追查才發現 Request.ServerVariables["REMOTE_ADDR"] 回傳的不再是 192.168.x.x 這種 IPv4，而是 ::1 或 fe80:… 之類的 IPv6。Split(‘.’) 自然找不到點號，程式立即拋例外。

為了暫時在開發機上讓舊程式恢復運作，作者測試了四種方法：  
(1) 直接用 IPv4 位址取代 localhost 存取網站；  
(2) 在 IIS 網站繫結設定中僅對應 IPv4；  
(3) 編輯 C:\Windows\System32\drivers\etc\hosts，將 localhost 的 IPv6 對應 ::1 註解掉，使 ping localhost 重新指向 127.0.0.1；  
(4) 乾脆停用網路卡的 IPv6 協定。

然而真正徹底且可攜的解決方案是「不要再手動剖析 IP 字串」。.NET Framework 早已提供 System.Net.IPAddress.Parse 將任何合法的位址字串（不論 IPv4 或 IPv6）轉成 IPAddress 物件，再以 AddressFamily 屬性判斷 InterNetwork(IPv4) 或 InterNetworkV6。如此即可在支援雙協定的環境中正常運作，也避免日後隨作業系統預設值變動而崩潰。本文透過實際踩坑經驗，提醒開發者應依官方 API 處理網路位址，並記錄了以 hosts 檔或停用 IPv6 作為權宜之計的操作步驟。

## 段落重點
### 舊程式碼的背景與功能
作者多年以前編寫了一段簡易函式庫，在 ASP.NET 頁面內取得造訪者的 IP，再配合 Netmask 判斷是否屬於 192.168.2.0/24 內網；其作法是把「點分十進位」IPv4 轉成整數後做 AND 運算，若相符便顯示 Is Intranet? YES。

### 升級 Vista x64 + IIS 7 後程式失效
當開發環境換成 Vista x64 與 IIS 7 時，原本正常的網頁忽然拋出例外；Trace 紀錄顯示 REMOTE_ADDR 竟是 IPv6 格式。Split(‘.’) 無法解析「::1」，使程式整個掛掉。

### 問題原因：預設啟用 IPv6
Windows Vista 預設啟用 IPv6，IIS 7 與內建的開發伺服器（WebDev）也優先使用 IPv6 回應，導致以 localhost 存取時，自機位址變成 ::1 而非 127.0.0.1，進而觸發程式碼漏洞。

### 權宜解法一：直接使用 IPv4 位址
最簡單的繞道方式是放棄 localhost，改以 http://192.168.100.40/… 直接連線，強迫走 IPv4。但這一招對只接受 localhost 的 WebDev 無效。

### 權宜解法二：IIS 網站綁定指定 IPv4
嘗試在 IIS 管理員中把網站「繫結」到 192.168.100.40，理論上可避免 IPv6，但作者實測後 localhost 仍走不到該站，效果有限。

### 權宜解法三：修改 hosts 檔解除 ::1
在 hosts 中註解「::1 localhost」那行，保留「127.0.0.1 localhost」，讓解析結果回到 IPv4。Ping 驗證成功後，使用 http://localhost/ 訪問即可恢復舊程式的正常運作，並可同時支援 WebDev。

### 權宜解法四：停用網卡的 IPv6 協定
透過網路連線 → 內容，將「Internet Protocol Version 6」的勾選取消，可自整臺機器層級關閉 IPv6，徹底避免類似問題，但屬於「關掉就好」的粗暴手段。

### 正規解法：使用 System.Net.IPAddress
最終結論是應以 IPAddress.Parse 將字串轉物件，再透過 AddressFamily 判斷 InterNetwork 或 InterNetworkV6，如此即可同時處理兩種協定，不必再人為拆字串，也不會因平台預設更動而故障。本文藉由真實踩雷經驗，提醒開發者遵循框架 API 的最佳實踐。