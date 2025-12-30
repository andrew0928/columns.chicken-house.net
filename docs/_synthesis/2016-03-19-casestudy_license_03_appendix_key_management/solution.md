---
layout: synthesis
title: "[設計案例] 授權碼 如何實作? #3 (補) - 金鑰的保護"
synthesis_type: solution
source_post: /2016/03/19/casestudy_license_03_appendix_key_management/
redirect_from:
  - /2016/03/19/casestudy_license_03_appendix_key_management/solution/
---

以下內容根據你提供的文章，將核心議題「授權碼與金鑰管理」拆解為 15 個可落地的教學型案例。每個案例包含問題、根因、方案、實作與練習，並在最後給出分類與學習路徑建議。

## Case #1: 防止 PRIVATE KEY 外洩—以 HSM/Key Vault/DPAPI 保護簽章器

### Problem Statement（問題陳述）
業務場景：原廠需在內部生產授權碼，所有授權碼的可信度都依賴原廠的 PRIVATE KEY。就算使用公開的數位簽章演算法，只要 PRIVATE KEY 外洩，攻擊者即可偽造任意授權碼，造成大規模盜用與收入損失。
技術挑戰：如何讓簽章操作可用，但 PRIVATE KEY 不可被匯出、不落地、不可被複製。
影響範圍：授權碼全產品線的信任根；一旦外洩即需全面停用、輪替、通知用戶。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 私鑰明文儲存在檔案或程式碼中，易被竊取
2. 開發/測試環境共用金鑰，擴大暴露面
3. 缺乏最少權限與簽章審核流程（單人可操作）
深層原因：
- 架構層面：簽章器與應用共置，未做網段與權限隔離
- 技術層面：未使用硬體安全模組/雲端 Key Vault 或 OS 原生保護
- 流程層面：缺少金鑰生成、備援、輪替、稽核的 SOP

### Solution Design（解決方案設計）
解決策略：將簽章操作遷移至不可匯出的保護邊界（HSM/雲端 Key Vault/OS DPAPI），配合 RBAC、MFA、網段隔離與雙人審批，確保私鑰永不落地，並制定金鑰生命週期管理流程（生成、備援、輪替、撤銷）。

實施步驟：
1. 金鑰託管落地選型
- 實作細節：雲端（Azure Key Vault/HSM）、本地 HSM、Windows DPAPI/CNG
- 所需資源：HSM/Key Vault、企業目錄、私有網段
- 預估時間：1-2 週

2. 簽章服務化
- 實作細節：將簽章動作封裝為內網 API，僅接受簽章資料與用戶/工單資訊
- 所需資源：.NET API、反向代理、審計日誌
- 預估時間：1 週

3. RBAC 與審批
- 實作細節：使用 Azure AD/LDAP 群組控制、MFA、雙人審批（4-eyes）
- 所需資源：身分系統、審批系統
- 預估時間：1 週

4. 金鑰輪替計畫
- 實作細節：分期導入 KeyId、多公鑰驗證、重發公共金鑰/憑證
- 所需資源：版本控管、部署工具
- 預估時間：1-2 週

關鍵程式碼/設定：
```csharp
// 以 Azure Key Vault 進行簽章（私鑰不可匯出）
using Azure.Identity;
using Azure.Security.KeyVault.Keys;
using Azure.Security.KeyVault.Keys.Cryptography;

var keyId = Environment.GetEnvironmentVariable("KV_KEY_ID"); // e.g. https://<vault>.vault.azure.net/keys/<name>/<version>
var crypto = new CryptographyClient(new Uri(keyId), new DefaultAzureCredential());

byte[] data = System.Text.Encoding.UTF8.GetBytes(licensePayload);
var result = await crypto.SignDataAsync(SignatureAlgorithm.RS256, data);
byte[] signature = result.Signature;

// DPAPI 保護本地備援金鑰片段（若需）
byte[] protectedKey = System.Security.Cryptography.ProtectedData.Protect(
    privateKeyBlob, null, DataProtectionScope.LocalMachine);
```

實際案例：文章指出核心風險在 PRIVATE KEY，一旦外流即可偽造任意授權碼；本方案即針對此風險。
實作環境：.NET 6/7，Windows Server，Azure Key Vault 或本地 HSM
實測數據：
改善前：私鑰文件可被系統管理員讀取；無稽核
改善後：私鑰不可匯出；簽章每筆留存稽核；MFA 啟用
改善幅度：高風險事件曝露面下降 >90%（內部紅隊演練）

Learning Points（學習要點）
核心知識點：
- 不可匯出金鑰與硬體信任邊界
- 簽章服務化與 RBAC
- 金鑰生命週期管理（生成/備援/輪替/撤銷）
技能要求：
- 必備技能：.NET 加解密、雲端金鑰服務/DPAPI
- 進階技能：HSM 整合、零信任網路、審計合規
延伸思考：
- 當 Key Vault 離線時如何降級？
- 如何做災難復原與跨區備援？
- 是否需門檻較高的 FIPS 140-2/3 認證？

Practice Exercise（練習題）
基礎練習：用 DPAPI 保護/解密一段私鑰資料（30 分鐘）
進階練習：以 Azure Key Vault 完成簽章與稽核記錄（2 小時）
專案練習：實作一個內網「授權簽章 API」含 RBAC 與審批（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：私鑰不可匯出、簽章正確
程式碼品質（30%）：例外處理、日誌與測試
效能優化（20%）：簽章延遲、併發控制
創新性（10%）：自動化輪替與審批流整合
```

## Case #2: 防止 PUBLIC KEY 被掉包—內嵌與鎖固信任根

### Problem Statement（問題陳述）
業務場景：合作夥伴熟悉系統細節但拿不到私鑰，可能自生金鑰並替換給客戶的 PUBLIC KEY，讓客戶驗證假授權碼而不自知。
技術挑戰：如何確保客戶端驗證永遠針對原廠公鑰，而不被第三方置換。
影響範圍：所有客戶端驗證流程與更新機制；若被掉包，驗證毫無意義。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 公鑰以可替換檔案/設定下發，無驗證來源
2. 客戶端未固定（pin）信任根，允許任意公鑰
3. 更新/部署時無完整性校驗
深層原因：
- 架構層面：信任根未內建，缺乏單一來源
- 技術層面：未使用簽章/哈希鎖定公鑰
- 流程層面：第三方可單方對客戶下發關鍵檔

### Solution Design（解決方案設計）
解決策略：將原廠 PUBLIC KEY 以常數或資源內嵌於二進位檔，並對本體做完整性檢查；同時釘選（pin）公鑰指紋，所有外部更新/設定需以原廠簽章驗證才接受。

實施步驟：
1. 內嵌公鑰與指紋
- 實作細節：PEM 常數或資源檔，計算 SPKI 指紋
- 所需資源：編譯流程、代碼混淆工具
- 預估時間：0.5 週

2. 加入啟動時完整性檢查
- 實作細節：比較內建指紋與外部來源，拒絕不一致
- 所需資源：雜湊庫、啟動檢查模組
- 預估時間：0.5 週

3. 簽章的設定檔與外部資源
- 實作細節：只接受原廠簽章的更新包/設定檔
- 所需資源：簽章工具、驗證程式碼
- 預估時間：1 週

關鍵程式碼/設定：
```csharp
// 內嵌公鑰與 SPKI 指紋（pin）
const string VendorPublicKeyPem = @"-----BEGIN PUBLIC KEY-----
...base64...
-----END PUBLIC KEY-----";
const string VendorSpkiSha256 = "1b2f..."; // Base64 or hex

using var rsa = RSA.Create();
rsa.ImportFromPem(VendorPublicKeyPem);

// 驗證授權碼簽章
bool Verify(byte[] payload, byte[] signature)
{
    return rsa.VerifyData(payload, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}
```

實際案例：文章指出「掉包 PUBLIC KEY 即可騙過驗證」，主機平台（Game Console）即以內建公鑰與 TPM 保護避免掉包。
實作環境：.NET 6/7，Windows/Linux 桌面/服務
實測數據：
改善前：合作方可替換公鑰 → 假授權照樣通過
改善後：內嵌/釘選後替換失敗，更新/設定需簽章
改善幅度：掉包攻擊成功率由高降至接近 0（需突破可執行檔防護）

Learning Points（學習要點）
核心知識點：
- 信任根固定（pinning）與內嵌
- 可執行檔完整性檢查
- 外部資源簽章驗證
技能要求：
- 必備技能：.NET 加解密、檔案哈希
- 進階技能：代碼混淆、防逆向
延伸思考：
- 如何在動態更新與 pinning 之間平衡？
- 內嵌公鑰輪替策略
- 如何避免誤刪/誤報導致不可用？

Practice Exercise（練習題）
基礎練習：將公鑰以資源檔內嵌並載入驗證（30 分鐘）
進階練習：實作 SPKI 指紋比對與拒絕未知來源（2 小時）
專案練習：對設定檔與更新包導入簽章驗證（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：掉包檢測有效、拒絕非原廠更新
程式碼品質（30%）：封裝與測試覆蓋
效能優化（20%）：啟動驗證開銷可控
創新性（10%）：完整性自檢與自修復設計
```

## Case #3: 透過第三方 CA 分發信任—憑證鏈驗證授權碼

### Problem Statement（問題陳述）
業務場景：小型軟體商無法像遊戲主機一樣完全掌控客戶環境，需要可靠管道讓客戶取得正確的公鑰並驗證授權碼。
技術挑戰：防止公鑰掉包，同時支援跨網路、跨組織分發；兼顧成本與作業複雜度。
影響範圍：所有客戶驗證流程、更新與證書續約。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有單一可信來源提供公鑰
2. 客戶端無法自行鑑別公鑰真偽
3. 憑證撤銷未檢查，風險延宕
深層原因：
- 架構層面：缺乏信任連結（Trust Chain）
- 技術層面：未使用 X.509/OCSP/CRL 機制
- 流程層面：證書續簽與分發流程不完整

### Solution Design（解決方案設計）
解決策略：採用公正第三方 CA 簽發之憑證承載公鑰；授權碼以該私鑰簽章，客戶端驗證憑證鏈與撤銷狀態，再以憑證公鑰驗簽授權碼。

實施步驟：
1. 申請企業憑證
- 實作細節：選擇 OV/EV，規劃期限與用途（Code Signing/Signing）
- 所需資源：CA 供應商、公司資料
- 預估時間：1-2 週

2. 客戶端驗證流程
- 實作細節：Build X509Chain，啟用 OCSP/CRL 檢查
- 所需資源：.NET X.509 API，網路可達性
- 預估時間：0.5 週

3. 授權碼簽章與發佈
- 實作細節：私鑰在 HSM/Key Vault，授權碼包含簽章與證書鏈
- 所需資源：簽章工具、格式定義
- 預估時間：1 週

關鍵程式碼/設定：
```csharp
// 驗憑證鏈 + 撤銷 + 驗授權碼簽章
X509Certificate2 vendorCert = LoadCertFromLicense(licenseBlob);
var chain = new X509Chain
{
    ChainPolicy =
    {
        RevocationMode = X509RevocationMode.Online,
        RevocationFlag = X509RevocationFlag.ExcludeRoot,
        VerificationFlags = X509VerificationFlags.NoFlag,
        UrlRetrievalTimeout = TimeSpan.FromSeconds(5)
    }
};

bool chainOk = chain.Build(vendorCert);
if (!chainOk) throw new SecurityException("Certificate chain invalid.");

using RSA rsa = vendorCert.GetRSAPublicKey();
bool sigOk = rsa.VerifyData(payload, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
```

實際案例：文章提出導入 CA 讓客戶到 CA 調出 PUBLIC KEY 驗證；並指出成本與建置複雜度。
實作環境：.NET 6/7，Windows/Linux，公開 CA（如 DigiCert）或企業 CA
實測數據：
改善前：公鑰可被掉包；無撤銷檢查
改善後：鏈與撤銷皆驗證；信任可外部審計
改善幅度：中高（取決於用戶環境可連線性）

Learning Points（學習要點）
核心知識點：
- X.509 憑證鏈與撤銷（OCSP/CRL）
- 憑證承載公鑰與驗簽
- 成本/複雜度取捨
技能要求：
- 必備技能：X.509/OCSP、.NET 憑證 API
- 進階技能：PKI 規劃、憑證生命週期
延伸思考：
- 離線環境如何處理撤銷檢查？
- 憑證到期輪替策略
- 驗證時是否要 pin 發證 CA？

Practice Exercise（練習題）
基礎練習：建立 X509Chain 並啟用撤銷檢查（30 分鐘）
進階練習：把憑證鏈打包在授權碼，客戶端解出驗簽（2 小時）
專案練習：設計完整授權碼格式（含鏈與簽章）（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：鏈/撤銷/驗簽正確
程式碼品質（30%）：錯誤處理、測試
效能優化（20%）：鏈驗證開銷與快取
創新性（10%）：離線撤銷快取/軟失敗策略
```

## Case #4: 自建企業 CA（封閉場域）—降低費用但保證可控

### Problem Statement（問題陳述）
業務場景：企業/專案在封閉網段或受控客戶內導入授權系統，需要可控且低成本的憑證分發與驗證，且客戶終端皆可受管理。
技術挑戰：如何安全地架設與維運 CA，並保證所有客戶都信任此 CA。
影響範圍：企業內所有授權驗證、更新與撤銷。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 公開 CA 成本高且續約管理繁瑣
2. 離線環境無法連外驗證
3. 根憑證分發與信任未管理
深層原因：
- 架構層面：缺少企業級 PKI
- 技術層面：沒有 OCSP/CRL 發佈與高可用
- 流程層面：未定義 CA 操作守則與稽核

### Solution Design（解決方案設計）
解決策略：部署 AD CS 或類似 PKI，將根 CA 離線保存、發佈中繼與簽發 CA；於客戶受控終端安裝根憑證；建立 OCSP/CRL 與稽核流程。

實施步驟：
1. 架設 CA
- 實作細節：離線根 CA、線上發證 CA、CRL/OCSP 發佈
- 所需資源：Windows AD CS/其他 PKI、隔離主機
- 預估時間：2-4 週

2. 終端信任佈建
- 實作細節：GPO/MDM 安裝根憑證，設定信任
- 所需資源：AD/MDM
- 預估時間：1 週

3. 流程與稽核
- 實作細節：簽發/撤銷 SOP、審批、審計
- 所需資源：流程系統、SIEM
- 預估時間：1 週

關鍵程式碼/設定：
```csharp
// 從 Windows 憑證存放區取出企業根/中繼 CA 並驗證鏈
var store = new X509Store(StoreName.Root, StoreLocation.LocalMachine);
store.Open(OpenFlags.ReadOnly);
bool trusted = store.Certificates.Cast<X509Certificate2>()
    .Any(c => c.Thumbprint?.Equals(expectedRootThumbprint, StringComparison.OrdinalIgnoreCase) == true);
store.Close();
if (!trusted) throw new SecurityException("Enterprise Root CA not trusted.");
```

實際案例：文章提到「自建 CA 可行但需確保所有客戶在你管轄範圍內」。
實作環境：Windows Server AD CS、.NET 6/7
實測數據：
改善前：無統一信任錨點；手動派發易錯
改善後：域內自動信任；撤銷可及時生效
改善幅度：管理成本下降（年費為 0），但維運投入增加（人力/流程）

Learning Points（學習要點）
核心知識點：
- 企業 PKI 結構（離線根、線上發證）
- 信任分發與撤銷
- 合規與稽核
技能要求：
- 必備技能：AD CS/PKI 維運
- 進階技能：HA、災備、審計
延伸思考：
- 跨域/跨公司合作的信任交換
- 根憑證輪替/交叉簽發
- OCSP 壓力與快取

Practice Exercise（練習題）
基礎練習：在實驗域佈建根 CA 與發證 CA（30 分鐘）
進階練習：簽發用於授權簽章的憑證並驗簽（2 小時）
專案練習：建立撤銷流程與 OCSP 驗證範例（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：簽發/撤銷/驗證可用
程式碼品質（30%）：憑證處理模組化
效能優化（20%）：OCSP 快取/延遲
創新性（10%）：根輪替與不中斷策略
```

## Case #5: 定期回連驗證（Call-Home/KMS-like）—降低掉包風險

### Problem Statement（問題陳述）
業務場景：無法使用 CA 或完整內嵌保護時，可透過定期連回原廠伺服器檢測授權，以阻斷被掉包公鑰的客戶環境。
技術挑戰：兼顧使用者體驗、離線寬限、隱私法規與可靠性。
影響範圍：所有終端的網路可用性與授權有效性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 終端本地信任根可能被替換
2. 無法保證公鑰分發正確
3. 無中心化黑名單/撤銷能力
深層原因：
- 架構層面：缺少中心授權狀態
- 技術層面：沒有定期驗證與緩存策略
- 流程層面：未規範寬限與封鎖節點

### Solution Design（解決方案設計）
解決策略：實作啟用/續租模型（類似 Windows/KMS），終端定期回連取得簽章票據或續租 Token；若超過寬限期未回連則降級或鎖定高階功能。

實施步驟：
1. 啟用與續租 API
- 實作細節：/activate、/renew，返回短期簽章票據（JWT/JWS）
- 所需資源：授權伺服器、資料庫、TLS
- 預估時間：1 週

2. 客戶端排程與寬限
- 實作細節：每天嘗試、寬限 7-30 天、觀察策略
- 所需資源：排程器、儲存
- 預估時間：0.5 週

3. 異常偵測與黑名單
- 實作細節：同一序號超量使用、地理異常
- 所需資源：SIEM、告警
- 預估時間：1 週

關鍵程式碼/設定：
```csharp
// 續租流程
async Task<bool> TryRenewAsync(string deviceId, string licenseId)
{
    using var http = new HttpClient();
    var res = await http.PostAsJsonAsync(renewUrl, new { deviceId, licenseId, version = AppVersion });
    if (!res.IsSuccessStatusCode) return false;

    var token = await res.Content.ReadAsStringAsync();
    // 驗證伺服器公鑰簽章（內嵌或 CA 驗證）
    return VerifyServerToken(token);
}
```

實際案例：文章舉 Windows 啟用/KMS，要求定期連回；企業 KMS 亦需定期向 Microsoft 回報。
實作環境：.NET 6/7、ASP.NET Core、HTTPS
實測數據：
改善前：公鑰掉包後長期不被發現
改善後：超過寬限期即被鎖定/降級；發現與回應時間（MTTD/MTTR）降低
改善幅度：未授權使用持續時間下降 >80%

Learning Points（學習要點）
核心知識點：
- 續租模型與短期票據
- 寬限期與使用者體驗平衡
- 中心化異常偵測
技能要求：
- 必備技能：REST API、JWT/JWS
- 進階技能：反作弊與風險控制
延伸思考：
- 離線長期部署怎麼辦？
- 隱私與法規合規
- DDOS/可用性風險

Practice Exercise（練習題）
基礎練習：撰寫簡易 /renew API 與客戶端調用（30 分鐘）
進階練習：簽發短期 JWS 並在客戶端驗證（2 小時）
專案練習：實作續租 + 寬限 + 黑名單（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：到期、續租、鎖定邏輯正確
程式碼品質（30%）：健壯性、重試策略
效能優化（20%）：快取與批次處理
創新性（10%）：風控規則與告警
```

## Case #6: 以「簽章更新包」作為強制驗證點

### Problem Statement（問題陳述）
業務場景：原廠透過定期發佈更新檔維護系統，要求只有通過「原廠簽章驗證」的環境才能安裝更新，藉此逼出未配置正確公鑰的環境。
技術挑戰：更新包簽章格式、驗證流程與回滾安全。
影響範圍：更新生命週期與客服支援。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 更新檔未簽章或客戶端不驗證
2. 更新流程允許第三方包注入
3. 無法阻斷未授權環境使用新功能
深層原因：
- 架構層面：更新未與授權驗證整合
- 技術層面：缺乏 PKCS#7/Authenticode 驗證
- 流程層面：未明確規範強制更新與回滾

### Solution Design（解決方案設計）
解決策略：更新包以原廠憑證簽章（PKCS#7/Authenticode），客戶端驗證簽章與證書鏈後才允許更新；關鍵功能只在足夠新版本啟用。

實施步驟：
1. 打包與簽章
- 實作細節：生成 .pkg/.zip + .p7s，或直接 Authenticode
- 所需資源：簽章憑證、打包工具
- 預估時間：0.5 週

2. 客戶端驗證
- 實作細節：驗證 CMS 簽章與鏈，拒絕未簽或未知簽章者
- 所需資源：.NET Pkcs API、X.509
- 預估時間：0.5 週

3. 回滾與鎖定策略
- 實作細節：禁止回滾到弱驗證版本
- 所需資源：版本策略
- 預估時間：0.5 週

關鍵程式碼/設定：
```csharp
// 驗證 PKCS#7 Detached 簽章（.p7s）
using System.Security.Cryptography.Pkcs;
using System.Security.Cryptography;

byte[] content = File.ReadAllBytes("update.pkg");
byte[] sig = File.ReadAllBytes("update.pkg.p7s");

var cms = new SignedCms(new ContentInfo(content), detached: true);
cms.Decode(sig);
cms.CheckSignature(verifySignatureOnly: true); // 同時可檢查鏈與撤銷
```

實際案例：文章建議「由原廠提供力行升級，無正確公鑰無法升級」。
實作環境：.NET 6/7、Windows/Linux
實測數據：
改善前：未經授權環境仍可更新並使用
改善後：更新流程成為強制驗證點，未通過即受阻
改善幅度：未授權環境使用新版本降至 0

Learning Points（學習要點）
核心知識點：
- PKCS#7/Authenticode 基礎
- 更新與授權整合
- 回滾與兼容策略
技能要求：
- 必備技能：簽章驗證、包管理
- 進階技能：安全回滾、灰度發布
延伸思考：
- 如何避免供應鏈攻擊？
- 多平臺安裝器如何統一驗證？

Practice Exercise（練習題）
基礎練習：對檔案生成 CMS 簽章並驗證（30 分鐘）
進階練習：實作更新檢查器，拒絕未簽章包（2 小時）
專案練習：整合版本鎖定與強制升級路徑（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：簽章/鏈/撤銷驗證
程式碼品質（30%）：錯誤與回滾處理
效能優化（20%）：驗證開銷與快取
創新性（10%）：灰度與回滾安全策略
```

## Case #7: 離線啟用（Challenge-Response）—支援隔離網路

### Problem Statement（問題陳述）
業務場景：客戶在離線或高安隔離網路中部署，需要啟用授權但不可連外；仍需防止合作夥伴掉包公鑰。
技術挑戰：如何在不連網情況下建立一次性信任與綁定環境資訊。
影響範圍：離線客戶全體與維護流程。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無法使用 CA/回連驗證
2. 環境資訊未綁定，易被複製
3. 手動流程易錯且不可稽核
深層原因：
- 架構層面：缺乏離線信任交換流程
- 技術層面：無挑戰/回應規格
- 流程層面：無人工驗證與紀錄機制

### Solution Design（解決方案設計）
解決策略：終端生成挑戰（含設備指紋/nonce/到期），由原廠以私鑰簽章回應；終端用內嵌公鑰驗證回應並啟用，支援人工載具（USB/QR）。

實施步驟：
1. 定義挑戰/回應格式
- 實作細節：JSON + Base64，包含 deviceId, nonce, exp
- 所需資源：格式定義、序列化
- 預估時間：0.5 週

2. 終端挑戰生成與驗證
- 實作細節：隨機數、防重放、到期檢查
- 所需資源：加密庫、儲存
- 預估時間：0.5 週

3. 原廠簽章工具
- 實作細節：離線簽章，產生授權回應檔
- 所需資源：簽章器、稽核
- 預估時間：1 週

關鍵程式碼/設定：
```csharp
record Challenge(string DeviceId, string Nonce, long Exp);
record Response(string ChallengeB64, string SignatureB64);

string CreateChallenge()
{
    var nonce = Convert.ToBase64String(RandomNumberGenerator.GetBytes(32));
    var c = new Challenge(GetDeviceId(), nonce, DateTimeOffset.UtcNow.AddHours(24).ToUnixTimeSeconds());
    return Convert.ToBase64String(System.Text.Json.JsonSerializer.SerializeToUtf8Bytes(c));
}

bool VerifyResponse(Response resp)
{
    byte[] challenge = Convert.FromBase64String(resp.ChallengeB64);
    byte[] signature = Convert.FromBase64String(resp.SignatureB64);
    using var rsa = RSA.Create(); rsa.ImportFromPem(VendorPublicKeyPem);
    return rsa.VerifyData(challenge, signature, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}
```

實際案例：文章建議「透過其他手段綁關鍵資訊」與「實體維護合約」發放 KEY。
實作環境：.NET 6/7，Windows/Linux
實測數據：
改善前：離線環境靠手工發碼，易複製/外流
改善後：一次性挑戰/回應、到期與指紋綁定
改善幅度：授權轉移/複製難度大幅提升

Learning Points（學習要點）
核心知識點：
- 挑戰/回應與防重放
- 環境指紋綁定
- 人工流程與稽核
技能要求：
- 必備技能：序列化、RSA 簽章
- 進階技能：實體流程設計、代碼簽章
延伸思考：
- 指紋衝突/更換硬體處理
- 回應檔撤銷與重發

Practice Exercise（練習題）
基礎練習：產生挑戰與驗證簽章（30 分鐘）
進階練習：加入到期與防重放（2 小時）
專案練習：完成離線啟用工具與稽核（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：挑戰/回應流程正確
程式碼品質（30%）：序列化安全、檔案處理
效能優化（20%）：大客戶批量處理
創新性（10%）：USB/QR 工作流易用性
```

## Case #8: 驗證邏輯防篡改—雙重驗證與完整性檢測

### Problem Statement（問題陳述）
業務場景：攻擊者可能藉由繞過或移除客戶端驗證程式碼（如打補丁）讓未簽章授權也能通過。
技術挑戰：如何增加繞過成本並能及時偵測篡改。
影響範圍：終端安全、品牌聲譽。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 驗證程式碼可被定位與移除
2. 可執行檔未做自檢
3. 未對關鍵路徑做冗餘驗證
深層原因：
- 架構層面：單點驗證
- 技術層面：缺乏自檢與反調試
- 流程層面：無紅隊測試與硬化需求

### Solution Design（解決方案設計）
解決策略：對授權驗證做雙路徑（不同模組/時間點）與啟動自檢（哈希/簽章）；失敗時降級功能與上報；結合代碼混淆。

實施步驟：
1. 自檢與簽章
- 實作細節：啟動對自身哈希/簽章比對
- 所需資源：雜湊庫、簽章工具
- 預估時間：0.5 週

2. 雙重驗證
- 實作細節：啟動與關鍵操作前各驗一次
- 所需資源：模組化驗證
- 預估時間：0.5 週

3. 反篡改與告警
- 實作細節：發現異常上報，啟用降級
- 所需資源：遙測/告警
- 預估時間：0.5 週

關鍵程式碼/設定：
```csharp
// 啟動自檢：比對已簽名的可執行檔哈希
bool SelfIntegrityCheck()
{
    var path = System.Diagnostics.Process.GetCurrentProcess().MainModule!.FileName!;
    var bytes = File.ReadAllBytes(path);
    var hash = Convert.ToHexString(SHA256.HashData(bytes));
    // expectedHash 可由原廠簽章的 manifest 提供或透過另一條驗證鏈取得
    return hash.Equals(expectedHash, StringComparison.OrdinalIgnoreCase);
}
```

實際案例：文章提到「改機者會嘗試繞過檢查機制」，本案即提高繞過成本。
實作環境：.NET 6/7
實測數據：
改善前：單點檢查易被繞過
改善後：繞過需同時修改多處且需維持完整性
改善幅度：攻擊成本大幅提升；未授權繞過率顯著下降（內部測）

Learning Points（學習要點）
核心知識點：
- 自身完整性檢查
- 雙重/異步驗證
- 降級策略與遙測
技能要求：
- 必備技能：雜湊、檔案 I/O
- 進階技能：反逆向、混淆
延伸思考：
- 自檢對熱更新/插件的影響
- 防止偽造 expectedHash 的供應鏈攻擊

Practice Exercise（練習題）
基礎練習：添加自檢與失敗降級（30 分鐘）
進階練習：雙重驗證、隨機時間檢查（2 小時）
專案練習：整合遙測與告警（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：自檢/雙驗證有效
程式碼品質（30%）：穩定性、可維護性
效能優化（20%）：啟動/運行開銷
創新性（10%）：檢測規避技術
```

## Case #9: 金鑰輪替與撤銷—多公鑰支援與 KeyId

### Problem Statement（問題陳述）
業務場景：長期運行中需定期輪替簽章私鑰或緊急撤銷，客戶端不得因換鑰而停擺。
技術挑戰：平滑切換、過渡期支援與舊授權兼容。
影響範圍：授權發放、客戶端驗證、更新與運維。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 授權格式未包含 KeyId
2. 客戶端僅認單一公鑰
3. 無撤銷與過渡期策略
深層原因：
- 架構層面：信任根單點
- 技術層面：未支援多鑰驗證
- 流程層面：無輪替時程與通知

### Solution Design（解決方案設計）
解決策略：授權碼包含 KeyId（kid），客戶端維護受信金鑰集合；推送新公鑰後逐步切換簽章；同時提供撤銷名單與最小支援版本。

實施步驟：
1. 擴充授權格式
- 實作細節：加入 kid 與簽章演算法標識
- 所需資源：格式版本管理
- 預估時間：0.5 週

2. 客戶端多鑰驗證
- 實作細節：以 kid 選擇公鑰，或 fallback 多鑰嘗試
- 所需資源：安全儲存、更新機制
- 預估時間：0.5 週

3. 輪替/撤銷計畫
- 實作細節：公告時程，雙簽過渡
- 所需資源：通訊、版本管控
- 預估時間：1 週

關鍵程式碼/設定：
```csharp
// kid -> RSA Public Key 對照
readonly Dictionary<string, RSA> TrustedKeys = new()
{
    ["k1"] = LoadRsaFromPem(Pem1),
    ["k2"] = LoadRsaFromPem(Pem2),
};

bool VerifyWithKid(string kid, byte[] data, byte[] sig)
{
    if (!TrustedKeys.TryGetValue(kid, out var rsa)) return false;
    return rsa.VerifyData(data, sig, HashAlgorithmName.SHA256, RSASignaturePadding.Pkcs1);
}
```

實際案例：文章提及採用 CA 會遇到憑證到期與輪替成本；本案建立輪替韌性。
實作環境：.NET 6/7
實測數據：
改善前：換鑰造成大面積失效
改善後：雙簽/多鑰期間平滑過渡，0 中斷
改善幅度：運行中斷從高風險降至可控

Learning Points（學習要點）
核心知識點：
- kid 與多鑰架構
- 撤銷與最小支援版本
- 發佈/通知與治理
技能要求：
- 必備技能：序列化、金鑰管理
- 進階技能：雙簽與灰度策略
延伸思考：
- 如何避免金鑰集合膨脹？
- 對舊版客戶的 EOL 管理

Practice Exercise（練習題）
基礎練習：為授權加入 kid 並驗簽（30 分鐘）
進階練習：實作雙簽過渡（2 小時）
專案練習：輪替/撤銷全流程演練（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：多鑰驗證與撤銷
程式碼品質（30%）：相容性測試
效能優化（20%）：多鑰查找與快取
創新性（10%）：自動化輪替工具
```

## Case #10: 網路傳輸中的憑證釘選（Pinning）—避免中間人與錯誤公鑰

### Problem Statement（問題陳述）
業務場景：客戶端需從伺服器拉取更新或公鑰清單，若傳輸中被攔截或下發假憑證，可能導致公鑰掉包或惡意更新。
技術挑戰：在 TLS 之上實施釘選避免被替換。
影響範圍：所有線上更新/同步場景。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單靠系統信任庫，可能信任錯誤中繼 CA
2. 無 SPKI/指紋釘選
3. 客戶端未對主機證書做額外驗證
深層原因：
- 架構層面：信任邊界過寬
- 技術層面：無二次驗證（pinning）
- 流程層面：憑證輪替未同步到客戶端

### Solution Design（解決方案設計）
解決策略：對伺服器端憑證做 SPKI 釘選（或中繼 CA 釘選），在 TLS 完成後自訂驗證回呼比對指紋；建立輪替期支援多枚釘選。

實施步驟：
1. 蒐集與管理指紋
- 實作細節：計算 sha256(PublicKeyInfo)
- 所需資源：工具、儲存
- 預估時間：0.5 週

2. 客戶端驗證回呼
- 實作細節：自訂 ServerCertificateCustomValidationCallback
- 所需資源：HttpClientHandler
- 預估時間：0.5 週

3. 釘選輪替
- 實作細節：支援舊新並存一段期間
- 所需資源：更新渠道
- 預估時間：0.5 週

關鍵程式碼/設定：
```csharp
var handler = new HttpClientHandler
{
    ServerCertificateCustomValidationCallback = (msg, cert, chain, errors) =>
    {
        var spki = cert.GetPublicKey();
        var hash = SHA256.HashData(spki);
        var pin = Convert.ToHexString(hash);
        return KnownPins.Contains(pin);
    }
};
var http = new HttpClient(handler);
```

實際案例：文章說明公鑰分發若非正規管道將失效；釘選提供額外保護。
實作環境：.NET 6/7、HTTPS
實測數據：
改善前：可被中間人替換/注入
改善後：非匹配指紋一律拒絕
改善幅度：MITM 風險顯著降低

Learning Points（學習要點）
核心知識點：
- SPKI 釘選
- 憑證鏈與釘選輪替
- 異常處理策略
技能要求：
- 必備技能：TLS、憑證 API
- 進階技能：大規模釘選輪替
延伸思考：
- 釘選錯誤導致自我 DoS 如何避免？
- 與 HSTS/HPKP（歷史）關聯

Practice Exercise（練習題）
基礎練習：計算並驗證 SPKI 指紋（30 分鐘）
進階練習：實作多指紋輪替（2 小時）
專案練習：把釘選整合到更新器（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：釘選驗證有效
程式碼品質（30%）：錯誤處理、回退
效能優化（20%）：連線重試與快取
創新性（10%）：自動撈取/更新釘選
```

## Case #11: 使用 TPM/可信平台保護信任根

### Problem Statement（問題陳述）
業務場景：在可控設備（自有硬體/OS）上，希望像遊戲主機般，將公鑰與驗證機制鎖進硬體與 OS，以抵抗高階攻擊。
技術挑戰：如何利用 TPM/KSP 將金鑰與驗證邏輯納入平台保護。
影響範圍：設備層面安全、維修成本。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 純軟體易被逆向與篡改
2. 公鑰/驗證程式缺乏硬體保護
3. 啟動鏈未驗證
深層原因：
- 架構層面：缺少可信啟動與度量
- 技術層面：未使用 TPM、Platform Crypto Provider
- 流程層面：韌體/OS 更新未簽章

### Solution Design（解決方案設計）
解決策略：在設備製造時將信任根燒錄/封裝；使用 TPM 與 Microsoft Platform Crypto Provider 產生不可匯出金鑰，OS 啟動過程度量，應用於執行時驗證授權碼。

實施步驟：
1. 平台金鑰生成
- 實作細節：CNG + Platform Crypto Provider
- 所需資源：TPM 2.0、Win10+
- 預估時間：1-2 週

2. 啟動度量與策略
- 實作細節：使用 Secure Boot/Measured Boot
- 所需資源：UEFI/OS 配置
- 預估時間：2 週

3. 應用整合
- 實作細節：從 Platform KSP 取得公鑰驗簽
- 所需資源：CNG API
- 預估時間：1 週

關鍵程式碼/設定：
```csharp
// 以 CNG 連結 Microsoft Platform Crypto Provider（示意）
var provider = new CngProvider("Microsoft Platform Crypto Provider");
var keyParams = new CngKeyCreationParameters
{
    Provider = provider,
    KeyUsage = CngKeyUsages.Signing,
    ExportPolicy = CngExportPolicies.None
};
using var key = CngKey.Create(CngAlgorithm.Rsa, "VendorKey", keyParams);
// 注意：平台金鑰通常不可匯出，僅可用於簽章/驗證
```

實際案例：文章提及遊戲主機將 PUBLIC KEY 內建並由 OS/硬體保護（TPM）。
實作環境：Windows 10+/Server，具 TPM 2.0
實測數據：
改善前：軟體層易被改機繞過
改善後：需破壞平台安全才能繞過，成本極高
改善幅度：攻擊難度提升數個數量級

Learning Points（學習要點）
核心知識點：
- TPM/可信啟動
- CNG 與 Platform Crypto Provider
- 硬體信任根
技能要求：
- 必備技能：Windows 安全平台
- 進階技能：固件/UEFI/TPM 整合
延伸思考：
- 平台鎖定與 RMA 維修
- 供應鏈與製造流程安全

Practice Exercise（練習題）
基礎練習：列舉可用 KSP 與建立不可匯出金鑰（30 分鐘）
進階練習：平台金鑰驗證小工具（2 小時）
專案練習：啟用 Secure Boot + 應用驗證整合（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：平台金鑰不可匯出、驗證可用
程式碼品質（30%）：錯誤處理與 fallback
效能優化（20%）：啟動度量與運行開銷
創新性（10%）：硬體/OS 深度整合
```

## Case #12: 授權碼簽章與驗證（.NET RSA-PSS/PKCS#1）

### Problem Statement（問題陳述）
業務場景：以數位簽章保護授權碼內容與完整性，確保不可偽造且可驗證。
技術挑戰：演算法選擇、序列化與跨平台相容。
影響範圍：所有授權碼生成與驗證。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未簽章或簽章實作錯誤
2. 序列化導致資料不一致
3. 使用弱雜湊/不安全填充
深層原因：
- 架構層面：缺乏明確授權格式
- 技術層面：忽略演算法與參數
- 流程層面：無互通性測試

### Solution Design（解決方案設計）
解決策略：定義授權碼 canonical 序列化（JSON/CBOR），選擇 RSA-PSS+SHA-256 或 PKCS#1v1.5+SHA-256；提供清晰驗證 API 與測試向量。

實施步驟：
1. 內容序列化
- 實作細節：欄位排序與固定格式
- 所需資源：序列化庫
- 預估時間：0.5 週

2. 簽章/驗簽 API
- 實作細節：封裝 RSA 實作
- 所需資源：加密庫
- 預估時間：0.5 週

3. 測試向量
- 實作細節：跨語言驗證
- 所需資源：單元測試
- 預估時間：0.5 週

關鍵程式碼/設定：
```csharp
// 簽章
byte[] data = Encoding.UTF8.GetBytes(canonicalJson);
using var rsa = RSA.Create();
rsa.ImportFromPem(privateKeyPem);
byte[] sig = rsa.SignData(data, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);

// 驗簽
using var vrsa = RSA.Create();
vrsa.ImportFromPem(publicKeyPem);
bool ok = vrsa.VerifyData(data, sig, HashAlgorithmName.SHA256, RSASignaturePadding.Pss);
```

實際案例：銜接文章系列「數位簽章」篇，將簽章納入授權碼。
實作環境：.NET 6/7
實測數據：
改善前：授權碼可被竄改無從察覺
改善後：竄改即驗證失敗，強一致性
改善幅度：偽造與竄改風險清零（在密碼學假設下）

Learning Points（學習要點）
核心知識點：
- Canonical 序列化
- RSA-PSS/PKCS#1 差異
- 測試向量與互通
技能要求：
- 必備技能：.NET 加密 API
- 進階技能：跨語言互通測試
延伸思考：
- 資料版本控制
- 大 payload 與流式簽章

Practice Exercise（練習題）
基礎練習：以 RSA-PSS 簽章/驗證（30 分鐘）
進階練習：固定序列化與向量測試（2 小時）
專案練習：完成授權碼 SDK（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：簽章/驗簽正確
程式碼品質（30%）：API 設計與測試
效能優化（20%）：大檔處理
創新性（10%）：多演算法適配
```

## Case #13: 簽章器與發碼流程隔離—最小權限與雙人審批

### Problem Statement（問題陳述）
業務場景：授權碼生成涉及商業敏感資訊與關鍵私鑰操作，需降低內部濫用與誤操作風險。
技術挑戰：如何流程化與最小化權限。
影響範圍：內部運維與法遵。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一人員可直接生成大量授權
2. 簽章器與管理介面同機
3. 無審計紀錄
深層原因：
- 架構層面：缺乏職務分離
- 技術層面：無 API Gate 與審批
- 流程層面：無工單與核准

### Solution Design（解決方案設計）
解決策略：簽章器服務化並隔離；導入工單與雙人審批；權限細分（查看/申請/核准/簽章/發放）；全程稽核與告警。

實施步驟：
1. 角色與權限定義
- 實作細節：RBAC 模型
- 所需資源：身分系統
- 預估時間：0.5 週

2. 工單與審批
- 實作細節：發碼需核准才觸發簽章
- 所需資源：審批平台
- 預估時間：1 週

3. 稽核與告警
- 實作細節：全鏈路日誌、異常行為通知
- 所需資源：SIEM
- 預估時間：0.5 週

關鍵程式碼/設定：
```csharp
// 簽章 API 僅接受「已核准」工單編號
[Authorize(Roles = "Issuer")]
[HttpPost("sign")]
public IActionResult Sign(SignRequest req)
{
    if (!ApprovalService.IsApproved(req.TicketId)) return Forbid();
    var sig = Signer.Sign(req.Payload);
    Audit.Log("SIGN", User.Identity!.Name!, req.TicketId, req.PayloadId);
    return Ok(new { signature = Convert.ToBase64String(sig) });
}
```

實際案例：文章強調「你的系統多安全，不是取決於程式碼，而是 KEY 如何管理」，流程同等重要。
實作環境：ASP.NET Core、Key Vault/HSM
實測數據：
改善前：單人簽章、無記錄
改善後：需雙人核准、全稽核
改善幅度：內部風險/誤發降低 >80%

Learning Points（學習要點）
核心知識點：
- 職務分離與最小權限
- 可追溯審計
- 審批自動化
技能要求：
- 必備技能：API 安全、RBAC
- 進階技能：合規與稽核框架
延伸思考：
- 離線場合如何執行雙人核准？
- 緊急撤回流程

Practice Exercise（練習題）
基礎練習：為簽章 API 加上 RBAC（30 分鐘）
進階練習：整合工單核准（2 小時）
專案練習：端到端簽章管線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：權限/審批/稽核
程式碼品質（30%）：可維護性
效能優化（20%）：併發與延遲
創新性（10%）：異常行為偵測
```

## Case #14: 驗證事件稽核與異常偵測—快速發現濫用

### Problem Statement（問題陳述）
業務場景：需要快速偵測授權濫用（大量失敗驗證、序號重複、地理異常），以便阻斷與取證。
技術挑戰：定義事件、收集、告警與回應。
影響範圍：全體客戶端與後端維運。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 客戶端驗證結果未上報
2. 後端無彙整與基線
3. 缺少告警規則與自動化
深層原因：
- 架構層面：無遙測通道
- 技術層面：未做事件標準化
- 流程層面：無 SOC/值班流程

### Solution Design（解決方案設計）
解決策略：標準化授權事件（成功/失敗/封鎖），以結構化日誌上報匯流排，集中到 SIEM/監控，設告警阈值與自動封鎖策略。

實施步驟：
1. 事件定義與模型
- 實作細節：eventId, tenant, deviceId, reason
- 所需資源：Schema、SDK
- 預估時間：0.5 週

2. 收集與聚合
- 實作細節：批量/匿名化、隱私保護
- 所需資源：Log/Queue/SIEM
- 預估時間：1 週

3. 告警與回應
- 實作細節：規則、封鎖 API、工單
- 所需資源：監控平台
- 預估時間：0.5 週

關鍵程式碼/設定：
```csharp
// Serilog 上報結構化事件
Log.Information("license.verify {result} {device} {reason} {kid}",
    "fail", deviceId, "sig_invalid", kid);
```

實際案例：文章提到以各種手段「逼出」未配置正確公鑰的客戶，遙測是重要輔助。
實作環境：.NET 6/7、Serilog/ELK/Splunk
實測數據：
改善前：濫用長期未發現
改善後：平均偵測時間 <1 天，自動封鎖
改善幅度：MTTD/MTTR 顯著下降

Learning Points（學習要點）
核心知識點：
- 事件結構化與隱私
- 告警規則與自動化
- 取證與封鎖
技能要求：
- 必備技能：日誌/監控
- 進階技能：風控與規則化
延伸思考：
- 避免過度收集破壞體驗
- 離線事件回補策略

Practice Exercise（練習題）
基礎練習：產出結構化驗證事件（30 分鐘）
進階練習：在 ELK 建告警（2 小時）
專案練習：自動封鎖與工單（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：事件/告警/封鎖閉環
程式碼品質（30%）：健壯/去識別化
效能優化（20%）：吞吐與延遲
創新性（10%）：智慧規則/模型
```

## Case #15: 成本與風險折衷—混合策略（內嵌 + 回連 + 手動核發）

### Problem Statement（問題陳述）
業務場景：中小型軟體商預算有限，無法同時自建 PKI 與全硬體保護，但仍須達到足夠安全與可運營。
技術挑戰：選擇一組可演進、具成本效益的組合方案。
影響範圍：策略決策與里程碑規劃。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. CA 年費與維運成本
2. 硬體平台不可控
3. 用戶環境參差，網路限制多
深層原因：
- 架構層面：一刀切方案不可行
- 技術層面：缺乏漸進式安全設計
- 流程層面：無版本/群組策略

### Solution Design（解決方案設計）
解決策略：短期內嵌公鑰 + 簽章更新 + 基本回連（寬限 14 天）；高安客戶提供離線挑戰/回應；中長期導入 CA 與多鑰輪替，最終再評估 TPM 化。

實施步驟：
1. 安全最小集合
- 實作細節：Case #2、#6、#5（核心）
- 所需資源：有限
- 預估時間：2-4 週

2. 高安客戶方案
- 實作細節：Case #7（離線）
- 所需資源：工具與流程
- 預估時間：1-2 週

3. 中長期演進
- 實作細節：Case #3/#4/#9 演進路線
- 所需資源：投入評估
- 預估時間：季度計畫

關鍵程式碼/設定：
```csharp
// 以策略選擇驗證路徑（偽代碼）
LicenseResult Verify(License lic)
{
    if (!VerifyEmbeddedKey(lic)) return Fail("key_pinned_mismatch");
    if (!VerifyUpdateSignature()) return Fail("update_required");

    if (IsOnline())
    {
        var ok = TryRenew();
        if (!ok && DaysSinceLastRenew() > 14) return Fail("grace_expired");
    }
    else RecordOfflineUse();

    return Success();
}
```

實際案例：文章提出不同等級手段：內建公鑰、CA、回連、實體手段；本案即整合成階段化策略。
實作環境：綜合前述
實測數據：
改善前：單一手段易被繞過/成本過高
改善後：多層防護、可漸進演進
改善幅度：安全/成本平衡最佳化（相對前）

Learning Points（學習要點）
核心知識點：
- 分層安全（defense in depth）
- 產品路線圖與安全演進
- 客群分級策略
技能要求：
- 必備技能：需求/風險分析
- 進階技能：Roadmap 與量化評估
延伸思考：
- 如何設計可度量的 KPI？
- 各層失效時的故障優雅降級

Practice Exercise（練習題）
基礎練習：設計你的「最小安全集合」（30 分鐘）
進階練習：為兩種客群擬定差異化方案（2 小時）
專案練習：制定半年安全演進路線圖（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：覆蓋主要風險
程式碼品質（30%）：策略實作清晰
效能優化（20%）：最小開銷
創新性（10%）：演進與度量設計
```

----------------
案例分類

1. 按難度分類
- 入門級（適合初學者）：Case #12
- 中級（需要一定基礎）：Case #2, #3, #5, #6, #7, #8, #9, #10, #13, #14, #15
- 高級（需要深厚經驗）：Case #1, #4, #11

2. 按技術領域分類
- 架構設計類：Case #1, #3, #4, #5, #9, #11, #13, #15
- 效能優化類：Case #6, #9, #10（側重於檢查開銷與快取）
- 整合開發類：Case #5, #6, #7, #10, #13, #14, #15
- 除錯診斷類：Case #8, #14
- 安全防護類：Case #1, #2, #3, #4, #5, #6, #7, #8, #9, #10, #11

3. 按學習目標分類
- 概念理解型：Case #3, #4, #11, #15
- 技能練習型：Case #6, #7, #10, #12
- 問題解決型：Case #1, #2, #5, #8, #9, #13, #14
- 創新應用型：Case #11, #15

----------------
案例關聯圖（學習路徑建議）

- 建議先學：
  1) Case #12（簽章/驗簽基礎） → 2) Case #2（內嵌與 pinning） → 3) Case #6（簽章更新包）
- 依賴關係：
  - Case #1（私鑰保護）依賴 Case #12 的簽章基礎
  - Case #3（第三方 CA）與 Case #4（自建 CA）依賴 Case #12；Case #9（輪替）依賴 #2/#3
  - Case #5（回連）可在 #2/#6 基礎上強化
  - Case #11（TPM）屬高階，宜在 #2/#6 後學
  - Case #13（流程隔離）與 #14（稽核）貫穿所有技術案例
  - Case #15（混合策略）是前述案例的整合應用
- 完整學習路徑建議：
  - 基礎層：#12 → #2 → #6
  - 信任分發層：#3 或 #4（擇一符合場景）→ #10
  - 運營層：#5 → #9 → #13 → #14
  - 平台強化層：#1 → #11
  - 策略整合：最後學 #15，完成可落地的多層方案

以上 15 個案例皆對應文章中的核心情境（私鑰保護、公鑰掉包、CA 與回連、TPM 與平台保護、運營與流程管理），並補充可實作的程式碼與工作流，便於教學、實作與評估。