# 原來是 IPv6 搞的鬼...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼原本在 XP/2003 上運作良好的「判斷是否在指定網段」程式，一搬到 Vista x64 + IIS 7 就失效？
因為 Vista 預設啟用了 IPv6，IIS 7 及內建的開發伺服器 (WebDev) 會直接將用戶端位址以 IPv6 形式回傳到 `REMOTE_ADDR`。原本只會把 IPv4 位址字串「切成四段」來計算的程式，遇到 IPv6 格式就無法解析，自然整段邏輯失效。

## Q: 透過 ASP.NET Trace 查看 `REMOTE_ADDR` 時，實際拿到的位址長什麼樣子？
Trace 會顯示一段 IPv6 位址 (例如 `::1`)，而不是傳統的 IPv4 格式 (`127.0.0.1` 或 `192.168.x.x`)。

## Q: 如果暫時只想用 IPv4，開發環境中有哪些做法可以繞過 IPv6？
作者實測有四種做法：
1. 直接以 IPv4 位址連線，例如把 `http://localhost/` 改成 `http://192.168.100.40/`。  
2. 嘗試在 IIS 綁定站台時指定 IPv4 位址 (效果有限)。  
3. 編輯 `C:\Windows\System32\drivers\etc\hosts`，移除 `::1 localhost` 這行，確保 `localhost` 只對應 `127.0.0.1`。  
4. 乾脆在網路卡設定中停用 IPv6 協定。  

其中做法 3 同時適用於只接受 `localhost` 的開發伺服器 (WebDev)。

## Q: 修改 hosts 檔案時，應保留與移除哪一行才能讓 `localhost` 回到 IPv4？
保留 `127.0.0.1 localhost`  
移除或註解 `::1 localhost`  
如此再 `ping localhost` 時就會得到 IPv4 的 `127.0.0.1`。

## Q: 從根本解決此類問題，程式碼上應該如何正規處理 IP 位址？
避免手動切字串，改用 .NET 內建的 `System.Net.IPAddress.Parse(string)` 取得 `IPAddress` 物件，再透過其 `AddressFamily` 屬性判斷是 `InterNetwork` (IPv4) 還是 `InterNetworkV6` (IPv6)。如此同時支援雙協定，也不怕日後 IP 形式改變。