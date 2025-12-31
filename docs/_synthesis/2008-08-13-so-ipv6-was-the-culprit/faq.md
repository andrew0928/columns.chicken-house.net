---
layout: synthesis
title: "原來是 IPv6 搞的鬼..."
synthesis_type: faq
source_post: /2008/08/13/so-ipv6-was-the-culprit/
redirect_from:
  - /2008/08/13/so-ipv6-was-the-culprit/faq/
postid: 2008-08-13-so-ipv6-was-the-culprit
---

# 原來是 IPv6 搞的鬼...

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 IPv6？
- A簡: IPv6 是 128 位元的新一代網際協定，採冒號十六進位表示，解決 IPv4 位址不足並增強自動組態與安全。
- A詳: IPv6（Internet Protocol version 6）使用 128 位元位址空間，以冒號分隔的十六進位表示（如 2001:db8::1），可提供極大量的位址。它內建無狀態自動組態（SLAAC）、多播、任播與更完整的安全支援（含 IPsec）。現代作業系統多為雙堆疊（Dual-Stack），能同時使用 IPv4/IPv6，名稱解析常優先回應 IPv6，對開發與部署流程影響重大。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q10, B-Q11

A-Q2: IPv4 與 IPv6 有何差異？
- A簡: 位址長度、表示法、子網標示與部署策略不同。IPv6 用前綴長度，不用點分遮罩。
- A詳: IPv4 為 32 位元，以點分十進位表示（如 192.168.2.1），子網以遮罩（如 255.255.255.0）或 /24 表示。IPv6 為 128 位元，以冒號十六進位表示（如 2001:db8::1），子網統一以前綴長度（如 /64）標示。IPv6 減少對 NAT 的依賴，恢復端對端連線理念，並於自動組態與安全上改良。兩者並存期常見雙堆疊環境與名稱解析優先級差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q9, A-Q10, B-Q2

A-Q3: 為什麼在 Vista x64 + IIS7 會拿到 IPv6 位址？
- A簡: 因系統預設啟用 IPv6，localhost 解析成 ::1，名稱解析優先回傳 IPv6。
- A詳: Windows Vista 預設啟用 IPv6，且名稱解析策略通常優先 AAAA 紀錄。當以 localhost 存取，本機名稱會先解析為 ::1（IPv6 迴路位址），IIS7 與開發伺服器因此回報 IPv6 位址於 REMOTE_ADDR/REMOTE_HOST。若程式僅支援 IPv4 字串處理，即會失效。此行為也可由 hosts 檔映射或解析順序進一步影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q11, A-Q6, A-Q17

A-Q4: AddressFamily 是什麼？常見類型有哪些？
- A簡: AddressFamily 表示通訊位址族。常見有 InterNetwork(IPv4) 與 InterNetworkV6(IPv6)。
- A詳: AddressFamily 是 .NET 中描述通訊位址類型的列舉，最常用的為 InterNetwork（IPv4）與 InterNetworkV6（IPv6）。可透過 System.Net.IPAddress.AddressFamily 取得實際位址族，並據以在程式中分支處理。例如先 Parse 位址為 IPAddress，再依 AddressFamily 決定採用 IPv4 子網遮罩或 IPv6 前綴長度的邏輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q3, C-Q1

A-Q5: System.Net.IPAddress.Parse 有什麼用途？
- A簡: 將字串 IP 轉為 IPAddress 物件，統一處理 IPv4/IPv6，避免人工拆字串。
- A詳: IPAddress.Parse 將字串形式的位址（包含 IPv4 與 IPv6）轉為 IPAddress 物件，方便透過 AddressFamily、GetAddressBytes、MapToIPv4/MapToIPv6 等成員做正規化處理。較新版本可用 TryParse 安全解析，避免例外。用 Parse 能同時支援 ::1、2001:db8::1、192.168.1.5 等多種格式，取代易錯的手工 split 與轉型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q3, C-Q1

A-Q6: localhost、127.0.0.1 與 ::1 的關係是什麼？
- A簡: 都是本機迴路位址，IPv4 為 127.0.0.1，IPv6 為 ::1，名稱解析可能優先 ::1。
- A詳: localhost 代表本機迴路介面；在 IPv4 使用 127.0.0.1/8，在 IPv6 使用 ::1/128。hosts 檔通常同時列出 ::1 與 127.0.0.1 的對應，但解析策略多優先 IPv6，導致 ping localhost 得到 ::1。修改 hosts 或調整 IPv6 優先順序可影響最終回應。了解三者關係有助於診斷本機開發時的 IP 版本差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q17, B-Q7

A-Q7: REMOTE_ADDR 與 REMOTE_HOST 有何差異？
- A簡: REMOTE_ADDR 是客戶端 IP；REMOTE_HOST 可能是主機名，牽涉逆向 DNS。
- A詳: 在 IIS/ASP.NET，REMOTE_ADDR 通常是 TCP 對端 IP；REMOTE_HOST 可能是 IP，也可能是經逆向 DNS 解析後的主機名。逆向 DNS 會造成延遲且未必可用，並可能返回不同格式。實務上建議以 REMOTE_ADDR 或框架提供的 UserHostAddress/RemoteIpAddress 為準，再視需要做 DNS 解析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, D-Q7

A-Q8: 為什麼不建議用拆字串判斷 IP？
- A簡: 只適用 IPv4，無法處理 IPv6 與變形格式，脆弱且易錯。
- A詳: 以 '.' 拆字串僅適用 IPv4，面對 IPv6 的冒號表示、壓縮規則與 IPv4-mapped IPv6 表示（如 ::ffff:1.2.3.4）會失效。不同系統還可能回傳主機名或含 scope 的 IPv6（fe80::1%lo0）。使用 IPAddress.Parse/TryParse 搭配 AddressFamily 與位元操作才是可維護、可擴充的作法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q2, D-Q1

A-Q9: 什麼是子網（subnet）與網路遮罩（netmask）？
- A簡: 子網透過遮罩分割網路；IPv4 用遮罩或 /前綴，做位元 AND 判斷隸屬。
- A詳: IPv4 以網路遮罩（如 255.255.255.0）或前綴長度（/24）界定子網。判斷一個 IP 是否屬於子網，將 IP 與遮罩做位元 AND，比對結果是否等於（網段位址 AND 遮罩）。例如 192.168.2.5 在 192.168.2.0/24 內，因 (192.168.2.5 & 255.255.255.0) == 192.168.2.0。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4, C-Q2

A-Q10: IPv6 的前綴長度（prefix length）是什麼？
- A簡: IPv6 以 /n 表示子網長度，如 /64；比較前 n 位元判斷是否同一網段。
- A詳: IPv6 不使用點分遮罩，統一用 /n 表示前綴位元數（如 2001:db8::/64）。判斷隸屬時，將兩個 128 位元位址的前 n 位元逐一比對是否相同。典型 LAN 常見 /64，路由或點對點鏈路可能用 /127 或 /128。程式須以位元級比較，不可沿用 IPv4 的 32 位整數法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q2, D-Q10

A-Q11: 什麼是 IPv4-mapped IPv6 位址？
- A簡: 格式為 ::ffff:a.b.c.d，於 IPv6 socket 上表示 IPv4 對端。
- A詳: 在雙堆疊環境，若伺服器以 IPv6 socket 接收，IPv4 客戶端可作為 IPv4-mapped IPv6 出現（如 ::ffff:192.168.1.5）。.NET 提供 IPAddress.IsIPv4MappedToIPv6、MapToIPv4/MapToIPv6 輔助判斷與轉換。忽略此情況可能導致重複判斷或子網比對錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q8, D-Q10

A-Q12: IIS 綁定（Binding）的意義是什麼？
- A簡: 綁定設定站台的 IP、連接埠與主機標頭，決定哪些請求會被該站處理。
- A詳: IIS 綁定將站台關聯到特定 IP（可為全部）、埠（如 80）與主機名稱（Host Header）。HTTP.sys 依綁定匹配請求。但綁定不影響名稱解析的結果，所以即使綁到 IPv4，若用 localhost 解析為 ::1，仍可能走 IPv6 迴路。需結合 hosts、iplisten 或具體 IP 存取來控制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q2, C-Q5

A-Q13: 什麼是 ASP.NET Trace？為何有用？
- A簡: Trace 顯示請求細節與伺服器變數，協助觀察 REMOTE_ADDR 等診斷資訊。
- A詳: ASP.NET Trace 可在頁面或全站層級啟用，輸出請求管線的關鍵資料，包括伺服器變數（REMOTE_ADDR、USER_AGENT）、控制項生命週期事件與自訂訊息。當遇到 IP 判斷異常時，開啟 Trace 能快速確認實際取得的 IP/主機資訊與格式，縮短問題定位時間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q6, D-Q1

A-Q14: 預設啟用 IPv6 有什麼影響？
- A簡: 本機名稱解析與連線優先走 IPv6，舊式只支援 IPv4 的程式可能失效。
- A詳: 在啟用 IPv6 的系統中，名稱解析對 localhost 與多數網域傾向回傳 AAAA 紀錄。HTTP 與 socket 連線亦可能以 IPv6 建立。因此硬編 IPv4 假設的程式（如拆字串、32 位元整數計算）會在新環境失效。最佳作法是採用 IPAddress 與 AddressFamily 正確處理雙協定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, D-Q4

A-Q15: 為何開發伺服器常只接受 localhost？
- A簡: 出於安全，限制僅本機迴路連線，避免未經授權的外部存取。
- A詳: 早期 ASP.NET Development Server（Cassini）與部分工具預設只綁定迴路介面，且可能僅接受 Host 為 localhost 的請求。此設計避免本機站台在開發期間暴露於區網。若需他機存取，建議改用 IIS Express 或本機 IIS，或以 hosts 映射達成測試需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q9, D-Q3

### Q&A 類別 B: 技術原理類

B-Q1: 文中以位元運算判斷 IPv4 子網如何運作？
- A簡: 將 IPv4 轉 32 位整數，以 (IP & Mask) 比對 (Network & Mask) 判斷隸屬。
- A詳: 流程為：以點分十進位字串（a.b.c.d）拆為四段，轉為 0–255 整數，依序乘 256 累加成 32 位整數。將目標網段、遮罩與客戶 IP 皆轉整數，分別與遮罩做位元 AND。若結果相等，即代表在同一子網。核心組件包括字串解析、32 位整數運算與遮罩邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q4, C-Q2

B-Q2: 為何上述方法在 IPv6 會失效？
- A簡: IPv6 為 128 位元且格式不同，無法以 IPv4 的 32 位元拆解與比對。
- A詳: IPv6 位址長度為 128 位元，採冒號十六進位表示，且允許零壓縮與 IPv4-mapped 等變形。以 '.' 分割與 32 位整數累加的作法完全不適用。此外，IPv6 使用前綴長度而非點分遮罩。需改用 IPAddress、位元陣列（16 位元組）與前綴位元逐位比對的流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q10, D-Q4

B-Q3: 正確辨識 IP 版本並分流處理的流程是什麼？
- A簡: 以 IPAddress.Parse 解析，再依 AddressFamily 分別走 IPv4/IPv6 邏輯。
- A詳: 步驟：1) 以 IPAddress.Parse/TryParse 將字串轉 IPAddress；2) 檢查 AddressFamily，若為 InterNetwork 走 IPv4 遮罩比對；若為 InterNetworkV6，走前綴比對；3) 必要時處理 IPv4-mapped IPv6（MapToIPv4）；4) 統一輸出布林或分類結果。核心組件：IPAddress、AddressFamily、GetAddressBytes 與位元操作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, C-Q1

B-Q4: 如何用位元組陣列判斷 IPv4 子網？
- A簡: 取 IP 與遮罩位元組，逐位 AND 後比對與網段位元組是否一致。
- A詳: 技術要點：以 IPAddress.GetAddressBytes 取 4 位元組，遮罩亦轉為 4 位元組（由遮罩字串或前綴長度生成），逐位做 AND，比對結果是否等於（網段位元組 AND 遮罩）。此法避免大小端序與整數溢位問題，比 32 位整數更安全。核心組件：位元組陣列運算、遮罩生成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, C-Q2, D-Q9

B-Q5: 如何以前綴位元比對 IPv6 子網？
- A簡: 將兩個 16 位元組的位址逐位比較前 n 位元是否相同。
- A詳: 流程：1) 取得目標網段位址與客戶 IP 的 16 位元組陣列；2) 依前綴長度 n，先比較整數個 8 位元組，再比較剩餘的餘數位（以遮罩 0xFF<<… 方式）；3) 全部相符即屬於該子網。核心組件：前綴長度計算、位移與位元 AND、逐位元組比較。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q2, D-Q10

B-Q6: REMOTE_ADDR/REMOTE_HOST 在伺服器如何取得？
- A簡: 由 HTTP.sys/伺服器填入 TCP 對端 IP，選配逆向 DNS 供 REMOTE_HOST。
- A詳: Windows 上的 HTTP.sys 會將連線的遠端端點 IP 提供給 IIS，IIS 再暴露為伺服器變數 REMOTE_ADDR。REMOTE_HOST 可能是同一 IP，或由伺服器嘗試逆向 DNS 得到的主機名。不同設定、代理與負載平衡器會影響這些值的來源與可信度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q3, D-Q7

B-Q7: Windows 名稱解析與 hosts 的生效機制是什麼？
- A簡: hosts 檔具高優先權，解析順序偏好 AAAA，再回退 A 記錄。
- A詳: Windows 名稱解析順序通常為：hosts 檔、本機快取、DNS、LLMNR/NetBIOS。當同名同時有 AAAA 與 A 記錄，預設依位址選擇策略（RFC 3484/6724）優先使用 IPv6。修改 hosts 直接覆寫該名稱，立即影響解析結果（可能需清快取）。核心組件：hosts、DNS、PrefixPolicy。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q17, D-Q5

B-Q8: IIS 綁定到 IPv4/IPv6 的運作與限制？
- A簡: HTTP.sys 依綁定接收請求，但不改變名稱解析或用戶端選擇路徑。
- A詳: IIS 使用 HTTP.sys 在核心態聆聽。綁定指定 IP、埠與主機標頭，決定哪些請求落到該站台。然而客戶端如何連入仍由其名稱解析與路由決定；若客戶端解析為 ::1，就會走 IPv6 進站。要控制行為，需綜合綁定、iplisten 清單、hosts 與實際存取位址。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q2, C-Q5

B-Q9: 開發伺服器僅接受本機連線的原理？
- A簡: 僅綁定迴路介面與受限主機標頭，拒絕外部來源請求。
- A詳: 早期開發伺服器（Cassini）執行於使用者態，預設只在 127.0.0.1/::1 上聆聽，並可能檢查 Host 頭必為 localhost，藉此防止未授權的區網存取。IIS Express 改善許多限制，但仍可透過 applicationhost.config 控制安全邊界與存取來源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q10, D-Q3

B-Q10: ASP.NET Trace 在管線中的作用？
- A簡: 於頁面/全站輸出請求與事件資訊，協助偵錯與稽核。
- A詳: Trace 可記錄 Page 生命週期事件、控制項載入、伺服器變數、Session 與自訂訊息。全站 Trace（trace.axd）可檢視近期請求清單與細節。開發者能藉此確認 REMOTE_ADDR/HTTP_X_FORWARDED_FOR 等值，定位與 IP 相關的錯誤來源。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q6, D-Q1

B-Q11: 位址選擇策略如何影響 localhost 解析？
- A簡: 作業系統依策略優先 IPv6，導致 localhost 解析為 ::1。
- A詳: RFC 3484/6724 規範位址選擇與排序。Windows 內建前綴政策偏好 IPv6，對同名的 localhost 會優先回傳 AAAA。因此即使同時有 127.0.0.1 與 ::1 映射，預設會選 ::1。可透過前綴策略調整工具或登錄值改變偏好，但不建議全域關閉 IPv6。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q6, C-Q7

B-Q12: .NET 如何辨識與處理 IPv4-mapped IPv6？
- A簡: 以 IsIPv4MappedToIPv6 判斷，MapToIPv4/MapToIPv6 做轉換。
- A詳: 當 AddressFamily 為 InterNetworkV6 時，可檢查 IPAddress.IsIPv4MappedToIPv6。若為真，表示底層對端是 IPv4，應視需求 MapToIPv4 後再做 IPv4 子網判斷或記錄。反之也可將純 IPv4 MapToIPv6 便於統一流程。此機制避免重複或錯誤判斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q8, D-Q10

B-Q13: 什麼是雙堆疊（Dual-Stack）與其行為？
- A簡: 同時支援 IPv4/IPv6，系統依策略選路，應用須能雙版本處理。
- A詳: 雙堆疊主機同時開啟 IPv4 與 IPv6 協定，socket 可能分別綁定或使用雙模式。名稱解析多優先 IPv6；若不可達再回退 IPv4。應用需考量位址版本、序列化與存取控制的相容性，並正確處理映射位址、前綴與防火牆規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q11, D-Q2

B-Q14: 為何綁定到 IPv4 仍可能看到 IPv6 連入？
- A簡: 客戶端解析與路由決定協定，且迴路/多綁定導致雙版本併存。
- A詳: 即使站台配置了 IPv4 綁定，若同時也在 ::/0 上有綁定或使用萬用位址，或客戶端使用 localhost（解析 ::1），連線仍會透過 IPv6。名稱解析與 HTTP.sys 的 iplisten/綁定組合共同影響結果。僅靠綁定不足以保證版本，需配合 hosts 或明確位址存取。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q12, D-Q2, C-Q5

B-Q15: 為何直接以字串比對 IP 危險？
- A簡: 不同格式與壓縮可能指同一位址，字串比對易出錯。
- A詳: IPv6 允許零壓縮與大小寫差異，IPv4 也可能有前導零或不同表示法。IPv4-mapped IPv6 與純 IPv4 代表同一對端時，字串不相等。應以 IPAddress 與位元組層級比較、正規化（MapToIPv4/IPv6）與子網演算法處理，避免安全與判斷錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q12, D-Q9

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 C# 正確辨識 IPv4/IPv6 並處理？
- A簡: 先 Parse，再以 AddressFamily 分流；必要時處理 IPv4-mapped。
- A詳: 實作步驟：1) 取得來源字串（UserHostAddress/RemoteIpAddress）；2) `IPAddress.TryParse(s, out var ip)`；3) `switch (ip.AddressFamily)` 分別走 IPv4 與 IPv6 邏輯；4) 若 `ip.IsIPv4MappedToIPv6` 則 `ip = ip.MapToIPv4()`。關鍵程式碼：IPAddress.Parse/TryParse、AddressFamily、IsIPv4MappedToIPv6。注意事項：避免字串 split；記錄原始來源以便稽核；對代理環境另行處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, B-Q3

C-Q2: 如何改寫 IsInSubNetwork 以同時支援 IPv4/IPv6？
- A簡: 用 IPAddress 與位元組比對；IPv4 用遮罩，IPv6 用前綴長度。
- A詳: 步驟：1) 解析來自與網段位址為 IPAddress；2) 若 IPv4，將遮罩轉 4 bytes，做逐位 AND 比對；3) 若 IPv6，接收 /n 前綴，對兩個 16 bytes 位址比較前 n 位元；4) 回傳布林。程式碼片段：使用 GetAddressBytes、位移與 AND（如 maskByte = (byte)(0xFF << (8 - r))）。注意：驗證輸入、處理 IPv4-mapped、避免整數溢位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, A-Q10

C-Q3: 如何在 ASP.NET 取得真實客戶 IP（含代理）？
- A簡: 先看受信任代理轉發標頭，再回退 REMOTE_ADDR。
- A詳: 步驟：1) 從 `X-Forwarded-For`/`X-Real-IP` 讀取；2) 僅在請求來自受信任的反向代理時採信；3) 解析首個非私有或符合策略的 IP；4) TryParse 驗證；5) 否則回退 `REMOTE_ADDR`/`UserHostAddress`。程式碼：拆分逗號清單，Trim，逐一 TryParse。注意：防止偽造標頭；記錄原始值與解析結果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q19, D-Q8

C-Q4: 如何設定 hosts 讓 localhost 走 IPv4？
- A簡: 以系統管理員編輯 hosts，將 ::1 對應註解或下移，加入 127.0.0.1。
- A詳: 步驟：1) 以管理員開啟 C:\Windows\System32\drivers\etc\hosts；2) 註解 `::1 localhost`，或確保 `127.0.0.1 localhost` 在前；3) 儲存後執行 `ipconfig /flushdns`；4) `ping localhost` 應回 127.0.0.1。注意：需管理員權限；避免副檔名錯誤；修改影響全系統，測試完成可還原。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, D-Q5, A-Q6

C-Q5: 如何在 IIS 限定只用 IPv4 接聽？
- A簡: 調整站台綁定與 HTTP.sys iplisten，並配合 hosts 或明確 IP 存取。
- A詳: 步驟：1) IIS 管理員中將站台綁定 IP 設為 127.0.0.1 或具體 IPv4；2) 以系統權限執行 `netsh http show iplisten` 確認；3) 視需求 `netsh http add iplisten ipaddress=127.0.0.1`；4) 使用 http://127.0.0.1/ 存取。注意：iplisten 影響全機 HTTP 接聽；需周全測試；名稱解析仍需搭配 hosts 控制。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q14, D-Q2

C-Q6: 如何啟用 ASP.NET Trace 檢視 REMOTE_ADDR？
- A簡: 在頁面或 web.config 啟用 Trace，於頁尾或 trace.axd 檢視變數。
- A詳: 步驟：1) 頁面上加屬性 `Trace="true"` 或 web.config `<trace enabled="true" pageOutput="false" />`；2) 佈署後瀏覽 /trace.axd 檢視；3) 搜尋 REMOTE_ADDR、REMOTE_HOST、HTTP_X_FORWARDED_FOR。注意：生產環境須限制存取 trace.axd；避免洩漏敏感資訊；測試後關閉。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q10, D-Q1

C-Q7: 如何調整 IPv6 偏好而非全停用？
- A簡: 使用前綴策略或登錄值，改為偏好 IPv4，保留 IPv6 功能。
- A詳: 作法：1) 以管理權限執行 `netsh interface ipv6 show prefixpolicies`，必要時調整優先順序；2) 或設定登錄 `HKLM\SYSTEM\CCS\Services\Tcpip6\Parameters\DisabledComponents=0x20`（偏好 IPv4）；3) 重開機。注意：不建議設為 0xFF 全停用；變更前備份；評估對其他應用影響。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, A-Q22, D-Q6

C-Q8: 如何在程式中處理 IPv4-mapped IPv6？
- A簡: 偵測 IsIPv4MappedToIPv6，必要時 MapToIPv4 再進行判斷。
- A詳: 步驟：1) `if (ip.AddressFamily==InterNetworkV6 && ip.IsIPv4MappedToIPv6) ip=ip.MapToIPv4();`；2) 之後以既有 IPv4 子網邏輯處理；3) 紀錄原始與轉換後位址。注意：僅在需要 IPv4 子網比對時轉換；若要統一 IPv6 處理，可 MapToIPv6。最佳實踐：所有輸入皆正規化後再進一步運算。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q12, D-Q10

C-Q9: 如何撰寫針對 IPv4/IPv6 的單元測試？
- A簡: 準備多組位址與子網案例，覆蓋邊界、映射與異常輸入。
- A詳: 步驟：1) 設計案例：IPv4 內外網、網段邊界（.0、.255）、IPv6 /64 內外、::1、IPv4-mapped；2) 為每案例呼叫判斷函式並斷言結果；3) 測試 TryParse 失敗路徑與例外；4) 建立 CI 自動化跑測。關鍵碼：xUnit/NUnit，資料驅動測試。注意：涵蓋大小寫與壓縮格式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q15, D-Q9

C-Q10: 如何用 IIS Express/本機 IIS 取代 Dev Server 限制？
- A簡: 在 Visual Studio 設為 IIS Express 或本機 IIS，彈性綁定與更像正式環境。
- A詳: 步驟：1) 專案屬性 Web 選擇 IIS Express 或 Local IIS；2) 設定應用程式 URL 與 Binding（127.0.0.1 或主機名）；3) 若用 Local IIS，建立應用程式集區與站台；4) 調整 hosts 與 SSL 憑證。注意：權限需求較高；確保相依模組配置一致；利於重現 IPv6/代理情境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, B-Q9, D-Q3

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 取得 ::1 或 IPv6 導致程式壞掉怎麼辦？
- A簡: 切換為 IPAddress.Parse 與 AddressFamily 判斷，移除手工拆字串。
- A詳: 症狀：以 '.' 拆字串或 32 位整數法解析 IP 時拋例外或判斷錯誤。原因：系統回傳 ::1/IPv6，舊法不相容。解法：改用 IPAddress.Parse/TryParse，依 AddressFamily 分支處理，必要時 MapToIPv4；以 ASP.NET Trace 驗證結果。預防：撰寫覆蓋 IPv4/IPv6 的單元測試，避免硬編 IPv4 假設。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q3, C-Q6

D-Q2: IIS 綁定 IPv4 仍回報 IPv6，要如何處理？
- A簡: 名稱解析仍選 IPv6；調整 hosts、iplisten 或以 IPv4 位址存取。
- A詳: 症狀：REMOTE_ADDR 顯示 IPv6，雖站台綁了 IPv4。原因：localhost 解析為 ::1 或同時有 IPv6 綁定。解法：用 127.0.0.1 存取；修改 hosts 讓 localhost 指向 127.0.0.1；檢查 `netsh http show iplisten` 並調整；確認無 :: 綁定。預防：設計程式支援雙堆疊，不依賴單一版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q8, C-Q5

D-Q3: Dev Server 只接受 localhost，不能用 IP，怎麼辦？
- A簡: 改用 IIS Express/Local IIS，或以 hosts 映射名稱至 127.0.0.1。
- A詳: 症狀：以 192.168.x.x 存取被拒。原因：開發伺服器僅綁定迴路與 localhost。解法：改用 IIS Express 或本機 IIS；或在 hosts 加入測試主機名指向 127.0.0.1，改以該名存取。預防：開發階段即使用貼近正式環境的伺服器與綁定設定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q9, C-Q10

D-Q4: 64 位元或新版 Windows 上子網判斷失效原因？
- A簡: 環境回傳 IPv6，舊法僅支援 IPv4，導致解析與比對錯誤。
- A詳: 症狀：在 Vista/Win10/IIS7+ 上判斷內外網邏輯錯誤。原因：系統預設 IPv6，程式用 '.' 拆分與 32 位運算。解法：採 IPAddress＋AddressFamily；IPv6 用前綴位元比對；加入映射位址處理。預防：單元測試覆蓋兩版本；不假設位址格式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q5, C-Q2

D-Q5: 修改 hosts 後不生效怎麼辦？
- A簡: 確認管理員權限、檔案正確、清快取並重啟相依服務。
- A詳: 症狀：仍解析為 ::1。原因：未以管理員儲存、存成 hosts.txt、路徑錯誤、DNS 快取未清。解法：以管理員編輯正確路徑；確保無副檔名；執行 `ipconfig /flushdns`；重啟瀏覽器/IIS。預防：變更前備份；記錄變更；測試後還原。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q4, A-Q6

D-Q6: 關閉 IPv6 後網路異常如何處理？
- A簡: 先改為偏好 IPv4而非停用；若已停用，還原設定並重啟。
- A詳: 症狀：某些服務失聯、共用列印失效。原因：全域停用 IPv6 影響系統相依元件。解法：將 DisabledComponents 改為偏好 IPv4（0x20）或還原（0）；重開機；檢查應用程式行為。預防：避免全停用；以程式正確支援雙堆疊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q11, A-Q22

D-Q7: 取得 REMOTE_HOST 為主機名導致失誤怎麼辦？
- A簡: 改讀 REMOTE_ADDR 或框架屬性，避免依賴逆向 DNS。
- A詳: 症狀：拿到主機名或不一致格式，無法做子網比對。原因：伺服器進行逆向 DNS。解法：改用 REMOTE_ADDR 或 Request.UserHostAddress/RemoteIpAddress；必要時自行做解析並快取。預防：不以 REMOTE_HOST 作判斷依據；禁用不必要的逆向查詢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q6, C-Q3

D-Q8: X-Forwarded-For 不可信或有多個值怎麼處理？
- A簡: 僅信任受控代理，取首個合法 IP，否則回退 REMOTE_ADDR。
- A詳: 症狀：被偽造或包含多 IP 導致誤判。原因：標頭可被客戶端任意設定。解法：檢查請求來源是否為信任代理；解析 XFF 清單，取第一個合法公共/策略允許的 IP；TryParse 驗證。預防：在反向代理端統一插入與清洗標頭；應用端白名單驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q6, B-Q19

D-Q9: 子網比對效能不佳或結果不穩定？
- A簡: 避免字串與整數轉換，改用位元組運算並快取遮罩。
- A詳: 症狀：高併發時 CPU 偏高或結果偶發錯誤。原因：頻繁 Parse、大小端混淆、遮罩生成錯誤。解法：預先快取已知網段的位元組遮罩；以 GetAddressBytes＋逐位運算；以單元測試覆蓋邊界與迴圈。預防：重用資料結構；避免文化區與格式依賴。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q9, B-Q15

D-Q10: 來源在內網卻被判定為外網的原因？
- A簡: 可能為 IPv6 未納入、映射位址、遮罩/前綴設錯或 NAT。
- A詳: 症狀：內部使用者被拒。原因：只比對 IPv4；忽略 IPv4-mapped；前綴長度錯誤；多層 NAT 或代理改變來源；混合路由。解法：納入 IPv6 前綴；處理映射；驗證與修正遮罩/前綴；於代理插入可信標頭並在應用端採信。預防：完整測試、記錄解析流程與來源鏈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, C-Q8

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 IPv6？
    - A-Q2: IPv4 與 IPv6 有何差異？
    - A-Q6: localhost、127.0.0.1 與 ::1 的關係是什麼？
    - A-Q3: 為什麼在 Vista x64 + IIS7 會拿到 IPv6 位址？
    - A-Q5: System.Net.IPAddress.Parse 有什麼用途？
    - A-Q4: AddressFamily 是什麼？常見類型有哪些？
    - A-Q9: 什麼是子網與網路遮罩？
    - A-Q10: IPv6 的前綴長度是什麼？
    - A-Q13: 什麼是 ASP.NET Trace？為何有用？
    - A-Q14: 預設啟用 IPv6 有什麼影響？
    - A-Q15: 為何開發伺服器常只接受 localhost？
    - C-Q1: 如何在 C# 正確辨識 IPv4/IPv6 並處理？
    - C-Q6: 如何啟用 ASP.NET Trace 檢視 REMOTE_ADDR？
    - D-Q1: 取得 ::1 或 IPv6 導致程式壞掉怎麼辦？
    - D-Q3: Dev Server 只接受 localhost，不能用 IP，怎麼辦？

- 中級者：建議學習哪 20 題
    - B-Q1: 文中以位元運算判斷 IPv4 子網如何運作？
    - B-Q2: 為何上述方法在 IPv6 會失效？
    - B-Q3: 正確辨識 IP 版本並分流處理的流程是什麼？
    - B-Q4: 如何用位元組陣列判斷 IPv4 子網？
    - B-Q5: 如何以前綴位元比對 IPv6 子網？
    - B-Q6: REMOTE_ADDR/REMOTE_HOST 在伺服器如何取得？
    - B-Q7: Windows 名稱解析與 hosts 的生效機制是什麼？
    - B-Q8: IIS 綁定到 IPv4/IPv6 的運作與限制？
    - B-Q10: ASP.NET Trace 在管線中的作用？
    - B-Q12: .NET 如何辨識與處理 IPv4-mapped IPv6？
    - B-Q15: 為何直接以字串比對 IP 危險？
    - A-Q7: REMOTE_ADDR 與 REMOTE_HOST 有何差異？
    - A-Q8: 為什麼不建議用拆字串判斷 IP？
    - A-Q11: 什麼是 IPv4-mapped IPv6 位址？
    - C-Q2: 如何改寫 IsInSubNetwork 以同時支援 IPv4/IPv6？
    - C-Q3: 如何在 ASP.NET 取得真實客戶 IP（含代理）？
    - C-Q8: 如何在程式中處理 IPv4-mapped IPv6？
    - C-Q9: 如何撰寫針對 IPv4/IPv6 的單元測試？
    - D-Q2: IIS 綁定 IPv4 仍回報 IPv6，要如何處理？
    - D-Q9: 子網比對效能不佳或結果不穩定？

- 高級者：建議關注哪 15 題
    - B-Q11: 位址選擇策略如何影響 localhost 解析？
    - B-Q13: 什麼是雙堆疊（Dual-Stack）與其行為？
    - B-Q14: 為何綁定到 IPv4 仍可能看到 IPv6 連入？
    - C-Q5: 如何在 IIS 限定只用 IPv4 接聽？
    - C-Q7: 如何調整 IPv6 偏好而非全停用？
    - D-Q6: 關閉 IPv6 後網路異常如何處理？
    - D-Q8: X-Forwarded-For 不可信或有多個值怎麼處理？
    - D-Q10: 來源在內網卻被判定為外網的原因？
    - A-Q12: IIS 綁定（Binding）的意義是什麼？
    - A-Q22:（對應於 C-Q7 的理念）為何不建議關閉 IPv6作為解法？ [提示：參考 C-Q7/D-Q6]
    - A-Q17: 為什麼修改 hosts 會影響連線結果？ [提示：參考 B-Q7]
    - B-Q8: IIS 綁定到 IPv4/IPv6 的運作與限制？
    - B-Q12: .NET 如何辨識與處理 IPv4-mapped IPv6？
    - C-Q10: 如何用 IIS Express/本機 IIS 取代 Dev Server 限制？
    - D-Q2: IIS 綁定 IPv4 仍回報 IPv6，要如何處理？

備註：學習路徑中的 A-Q22、A-Q17 為延伸概念，對應本FAQ的 C-Q7、B-Q7 與 D-Q6 的內容與觀念。