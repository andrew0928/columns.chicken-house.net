# [設計案例] 授權碼 如何實作? #2, 序列化

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這套授權碼機制想解決哪些核心問題？
1. 在無法連上 Internet 的環境下，仍能根據一段授權資料判斷使用者購買的版本與可啟用功能。  
2. 授權資料的格式要簡單、結構清楚、易於擴充與維護。  
3. 必須具備足夠的安全強度，能驗證授權碼確實由原廠發出，避免被偽造。

## Q: 授權碼由哪兩個部分組成？
授權碼被設計為「設定資訊」+「數位簽章」兩大部分：  
1. 設定資訊：描述要啟用的功能、授權期限等內容，本身不是機密，可公開。  
2. 數位簽章：用來驗證上述資訊確實出自原廠並且在傳輸過程中未被篡改。

## Q: TokenData 與 TokenHelper 在系統中扮演什麼角色？
• TokenData：  
  ‑ 代表一張授權的「設定資訊」。  
  ‑ 可被繼承以加入自訂欄位，並透過覆寫 IsValidate() 實作個別的授權驗證邏輯。  
• TokenHelper（static class）：  
  ‑ Factory 角色，集中負責 TokenData 的 Create / Encode / Decode。  
  ‑ Init() 會先載入金鑰庫，之後才能進行簽章或驗證。

## Q: 如何自訂一種新的授權資料 (TokenData)？
1. 宣告一個類別繼承 TokenData。  
2. 在欄位或屬性上加上 [JsonProperty]，表示要被序列化進授權碼。  
3. 覆寫 IsValidate() 方法，撰寫自己的授權有效性檢查（例如授權期限、使用人數上限等）。

## Q: 驗證一段授權碼 (Decode) 需要哪些步驟？
1. 先呼叫 TokenHelper.Init() 載入公鑰/私鑰與網站 SiteID。  
2. 把授權字串交給 TokenHelper.DecodeToken<T>()。  
3. TokenHelper 會：  
   a. 以 ‘|’ 分隔資料區與簽章區，並將兩段 BASE64 轉回 byte[]。  
   b. 反序列化資料區成對應的 TokenData 物件。  
   c. 呼叫 token.IsValidate() 檢查自訂授權邏輯。  
   d. 以公鑰驗證簽章，確認資料未被竄改且確實由原廠發出。  
4. 全部通過後，回傳 TokenData 供程式直接取值使用；任何一步失敗皆擲出例外。

## Q: 產生一段新的授權碼 (Encode) 的流程是什麼？
1. TokenHelper.CreateToken<T>() 建立一個空白 TokenData 物件。  
2. 程式填入各項授權設定值 (SiteTitle, EnableAPI, LicenseStartDate …)。  
3. 呼叫 TokenHelper.EncodeToken(token) 產生最終授權碼：  
   a. 使用 BSON(JSON) 將 TokenData 轉成 data_buffer。  
   b. 以私鑰對 data_buffer 進行 SignData() 產生 sign_buffer。  
   c. 將兩段 buffer 各自 BASE64 編碼後，用 ‘|’ 串起來成為授權字串。  
注意：沒有原廠的私鑰無法完成第 3b 步，所以外部無法自行偽造合法授權碼。

## Q: 為什麼選擇 JSON/BSON 作為序列化格式？
JSON：易讀、跨語言、工具與函式庫豐富；  
BSON：JSON 的二進位表示，可減少字串長度、省去 escape 處理並保留結構資訊。使用 Newtonsoft.Json 可以在兩者之間輕鬆切換，毋須自行撰寫序列化邏輯。

## Q: 授權碼最終字串的格式是什麼？
BASE64(Data) + ‘|’ + BASE64(Signature)。  
由於 BASE64 只會用到 65 個字元 (a–z, A–Z, 0–9, +, /, =) ，因此額外選擇 ‘|’ 作為不會出現在 BASE64 內文中的分隔符號，簡化了解碼實作。