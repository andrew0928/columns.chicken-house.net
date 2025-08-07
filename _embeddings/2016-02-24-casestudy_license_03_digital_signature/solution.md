# [設計案例] 授權碼 如何實作? ‑ 數位簽章

# 問題／解決方案 (Problem/Solution)

## Problem: 無法保證授權碼確實出自原廠，且在傳遞過程中未被竄改  

**Problem**:  
在 SaaS / On-Premise 軟體交付情境中，系統必須讀取一段「授權碼」(license token) 來決定啟用哪些功能。若攻擊者能偽造、修改這段授權碼，就能繞過授權檢查或擴大可用功能，造成營收與資安風險。

**Root Cause**:  
1. 傳統做法常以「自創加密」或「遮蔽演算法」(Security by Obscurity) 方式保護資料，實際上僅依賴程式碼不被看見，一旦程式碼開源、被逆向或被團隊同仁審查，演算法即裸露，授權碼易被偽造。  
2. 資料本身與授權發行者身分沒有強綁定，接收方無法驗證「誰」發的，以及「內容」是否被修改。  

**Solution**:  
採用公開且經過驗證的 RSA 非對稱式加密，實作「數位簽章」。  
1. 發行端 (原廠)  
   • 產生 RSA KeyPair。  
   • 以 Private Key 對授權碼序列化結果做 SignData，得到 Signature。  
   • 將 {LicenseData, Signature} 打包給客戶。  

2. 接收端 (客戶網站)  
   • 只持有 Public Key。  
   • 重新計算 LicenseData 的 Hash，並以 Public Key 驗證 Signature。  
   • 雜湊一致 → 來源可信且內容未被修改；否則拒絕啟動。  

關鍵程式碼 (摘錄)：  

```csharp
// 簽章 (發行端)
byte[] signBuffer = privateRsaCsp.SignData(dataBuffer, new SHA256CryptoServiceProvider());

// 驗章 (接收端)
bool isSecure = publicRsaCsp.VerifyData(dataBuffer,
                                        new SHA256CryptoServiceProvider(),
                                        signBuffer);
```  

此方案的關鍵思考：  
• 以「金鑰」而非「演算法」保護資料。  
• 非對稱加密讓 “驗證” 行為無須暴露私鑰，天然支援一對多散布。  

**Cases 1 – 正常授權**:  
網站啟動時呼叫 `TokenHelper.DecodeToken` 驗章成功，MVC5 應用順利載入。  

**Cases 2 – 授權過期**:  
`token.IsValidate()` 回傳 false → 觸發 `TokenNotValidateException`，Startup 中斷；網站無法啟動。  

**Cases 3 – 授權遭篡改**:  
Signature 與資料雜湊比對失敗 → `TokenNotSecureException` 被拋出；偽造授權立即被阻擋。  



## Problem: 私鑰儲存與管理不當，導致整體簽章機制失效  

**Problem**:  
Sample Code 為求 Demo 便利，把 Private Key 以 XML 檔案方式硬存於指定資料夾。實務環境若沿用此做法，一旦檔案被複製或版本管控外流，攻擊者就能偽造任意授權碼。

**Root Cause**:  
1. 私鑰存放於檔案系統缺乏 OS Layer 防護 (ACL、加密、存取稽核)。  
2. 缺乏 Key Lifecycle 管理 (產生、備份、到期、撤銷)。  
3. 應用程式得以直接讀取私鑰內容，增大外洩面。  

**Solution**:  
1. 於 Windows 平台使用 CNG / CryptoAPI 之 Key Container 或憑證庫 (Certificate Store) 儲存私鑰；Linux 可使用 OpenSSL + HSM/TPM。  
2. 私鑰存取權限僅限授權簽章服務帳號 (non-interactive)。  
3. 以 CA/內部 PKI 散布 Public Key，支援憑證撤銷 (CRL/OCSP)。  
4. 將程式中的 `RSACryptoServiceProvider.FromXmlString()` 改為讀取 Container：  

```csharp
CngKey key = CngKey.Open("MySigningKey", CngProvider.MicrosoftSoftwareKeyStorageProvider);
RSACng rsa = new RSACng(key);
```  

此調整消除了「把 Key 當檔案帶著走」的風險點。  

**Cases**:  
• 專案導入 HSM 後，滲透測試無法再匯出私鑰；多雲部署環境只需同步 Public Key。  
• Key Rotation 每年一次，僅需在 HSM 內完成重新產生並發布新憑證，應用程式端零程式碼變動。  



## Problem: Web 應用在啟動後才發現授權異常，造成違規執行風險  

**Problem**:  
若授權驗證流程延遲到功能點被呼叫時才檢查，網站已經對外提供服務，可能導致在非法授權狀態下仍有部份功能運作，甚至產生帳務資料。

**Root Cause**:  
缺乏「啟動前總驗證」機制；授權碼有效性與應用程式生命週期解耦，導致控制面向過晚。  

**Solution**:  
1. 在 `Startup.cs` → `Configure(IApplicationBuilder app, …)` 最前段注入授權檢查。  
2. 利用前述 `TokenHelper.Init()` + `DecodeToken<T>()`，在 Routing 與 DI Container 註冊之前完成驗證。  
3. 驗證失敗直接 throw，以 `UseExceptionHandler` 或預設失敗頁面呈現授權錯誤，避免後續 Middleware 執行。  

核心程式碼：  

```csharp
// Startup.cs
var licConf = Configuration.GetSection("License");
TokenHelper.Init(licConf["SiteID"],
                 licConf["SitePrivateKey"],
                 LoadPublicKeyDict(licConf));

try
{
    var licToken = TokenHelper.DecodeToken<SiteLicenseToken>(licConf["TokenData"]);
}
catch(Exception ex)
{
    logger.LogCritical(ex, "License check failed, aborting start-up.");
    throw;  // ASP.NET Core 直接停止啟動
}
```  

**Cases**:  
• 當 CI/CD Pipeline 部署到測試站但忘記置換測試授權時，站台於啟動階段即失敗，避免「測試站跑在正式授權」的合規問題。  
• 產品外包商嘗試複製整個網站到未授權域名，啟動即中斷，減少盜版風險。  



---  
以上將文章零散的經驗整理為三組核心「Problem / Root Cause / Solution / Cases」，協助讀者快速瞭解數位簽章在授權碼場域的價值及實作細節。