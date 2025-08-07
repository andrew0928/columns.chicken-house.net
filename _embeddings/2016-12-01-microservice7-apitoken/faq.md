# 微服務架構 #4, 如何強化微服務的安全性? API Token / JWT 的應用

# 問答集 (FAQ, frequently asked questions and answers)

## Q: API Token 在微服務架構中要解決的核心難題是什麼？
API Token 主要用來讓彼此「無法即時通訊」的多個服務，能在不直接交握的情況下驗證對方的身分與請求內容是否被竄改。藉由數位簽章機制，任何服務都可以離線地確認：  
1. 請求確實出自可信任的服務 (身分驗證, authentication)  
2. 請求內容在傳輸過程中未被修改 (內容完整性, integrity)  
從而降低服務之間反覆同步或查詢授權資料所帶來的成本與風險。

## Q: RSA 數位簽章用在哪些步驟？為什麼能證明資料未被竄改？
流程如下：  
1. 發送端 (A) 先對「原始資料」計算 Hash。  
2. 使用自己的 Private Key 對 Hash 做加密，形成 Signature。  
3. 將「原始資料 + Signature」一起送到接收端 (B)。  
4. B 用 A 的 Public Key 解開 Signature 得到 Hash1，再自己對收到的「原始資料」重算 Hash2。  
5. 若 Hash1 == Hash2，則可確認資料必為 A 發出且內容未改動。  
因為只有擁有 Private Key 的 A 才能產生對應可被 Public Key 解開的 Signature，故具備不可否認性與防竄改特性。

## Q: 記名式的 SessionToken 如何抵禦 Replay Attack？
在 Token 內容 (TokenData) 中額外記錄「UserHostAddress」(或裝置唯一碼等)。  
驗證時除了檢查簽章與有效期限，還要比對目前來源 IP／裝置 ID 是否與 Token 內紀載一致。即使攻擊者攔截到合法 Token，也必須同時偽造來源 IP／裝置資訊才可通過，難度大幅提高，可有效阻擋大部分 Replay 攻擊。

## Q: JWT (Json Web Token) 跟「土炮版 Token」最大的差異與優點是什麼？
JWT 依 RFC 規範將 Token 切為 Header / Payload / Signature 三段，以 base64url 編碼；並已在多數語言與框架有成熟的 Library。  
優點：  
1. 標準格式與演算法聲明 (Header) 可互通多語言、平台。  
2. 生態系完整，前後端與行動裝置均有現成套件。  
3. 支援多種演算法 (HS256, RS256…)，可依需求調整安全層級。  
若只是 Demo 或 POC，「土炮版」較易閱讀；正式環境則建議使用 JWT 以減少維護與相容性風險。

## Q: 為何有時說「Public Key 加密 / Private Key 解密」；文中卻使用「Private Key 加密 / Public Key 解密」？
RSA 規則是「用其中一把 Key 加密，就必須用另一把對應的 Key 解密」。  
‧ 當目的是「保密」(只有指定收件者能讀)，要用收件者的 Public Key 加密。  
‧ 當目的是「簽章」(證明訊息來源)，就由發送者以自己的 Private Key 加密 Hash，收件者用發送者 Public Key 驗證。  
Token 屬於簽章情境，因此使用 Private Key 加密、Public Key 驗證完全正確。

## Q: 軟體啟用序號可以直接用 Token 機制來實作嗎？
可以。將授權資訊 (使用者、到期日、功能清單…) 當成 TokenData，利用 Private Key 簽章後組成序號。  
軟體啟動時：  
1. 內建 Public Key 驗證序號簽章。  
2. 依 TokenData 啟用相對功能或期限。  
只要 Private Key 未外洩，序號本身難以偽造；若再配合對執行檔做 Code Signing，可同時避免序號與程式被竄改。

## Q: 在雲端分散式或微服務環境，如何利用 Token 同時解決「身分驗證」與「服務授權」？
做法：  
1. 每個 Service Site 配發一組「SiteToken」(紀錄 SiteID、SiteUrl)，其他服務可驗證呼叫者是否為合法節點。  
2. 服務對服務之間的呼叫，再附帶一組「ServiceToken」(紀錄 CallerID、CalleeID、ServiceID、權限等)。  
當收到請求時先驗 SiteToken 驗身分，再驗 ServiceToken 決定是否授權呼叫。兩種 Token 皆由中心方以 Private Key 簽發即可，不必保持即時連線或查表，比集中式授權伺服器更具彈性。

## Q: 「去中心化」的微服務為什麼更需要標準化安全機制而非自創？
微服務通常由多個獨立部署、獨立生命週期的服務組成，若使用臨時或自製的加解密方案：  
1. 每個團隊需各自維護、修補漏洞，成本高且易出錯。  
2. 無法與外部服務或跨語言組件互通。  
3. 安全強度難以驗證，潛藏未知風險。  
採用經過社群驗證的標準演算法 (如 RS256) 與框架 (JWT、OAuth2 等) 能統一治理、降低開發與維運複雜度，也較易被外部審計。

## Q: 若 Private Key 洩漏，使用 Token 的整體安全會怎樣？如何補救？
一旦 Private Key 洩漏，任何人都能生成看似合法的 Token，整個信任鏈即告失效。補救步驟：  
1. 立即停用舊的 Key，更新所有服務端 Public Key。  
2. 重新簽發必要的 Token (SiteToken / ServiceToken / SessionToken)。  
3. 建立 Key Rotation 機制，定期更換並佈署新金鑰，降低單一金鑰失效的影響範圍。  
4. 考慮將私鑰存放於 HSM 或雲端 Key Vault，並限制操作權限與審計。

## Q: 在實務上，要多久更新一次 SessionToken 的有效期限較合理？
視風險與使用情境而定。常見做法：  
1. Web 前後端：15~60 分鐘 (短存活)，並可搭配 Refresh Token 機制延長登入狀態。  
2. 後端服務對服務：幾分鐘到數小時不等，若頻繁呼叫，也可改用長效 ServiceToken。  
原則是「越敏感的資源，Token 壽命越短」；同時須配合 Replay Attack 防範 (如記名、防重放 nonce、TLS) 以提升整體安全。