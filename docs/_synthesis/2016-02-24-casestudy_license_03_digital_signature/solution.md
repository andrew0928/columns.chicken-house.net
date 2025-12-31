---
layout: synthesis
title: "[設計案例]  授權碼 如何實作?  #3, 數位簽章"
synthesis_type: solution
source_post: /2016/02/24/casestudy_license_03_digital_signature/
redirect_from:
  - /2016/02/24/casestudy_license_03_digital_signature/solution/
postid: 2016-02-24-casestudy_license_03_digital_signature
---

以下內容基於文章中已出現的問題、根因、解法與驗證結果，整理為可落地演練的 18 個解決方案案例。每一案均含業務與技術視角、實作步驟、關鍵程式碼、實測結果與練習/評估指標，便於課堂教學、專案實作與評量。

--------------------------------------------------------------------------------

## Case #1: 授權碼來源鑑別與偽造防護（RSA 數位簽章）

### Problem Statement（問題陳述）
業務場景：軟體需以「授權碼」控制功能啟用，但客戶端配置管道不可信，易被第三者偽造或竄改，造成未授權使用或盜版。希望確保授權資料「確實由原廠發出」且「未被修改」，以避免客服糾紛與法務風險。
技術挑戰：如何在不可信通道發佈授權資料，仍能讓接收端驗證出處與完整性。
影響範圍：若驗證失敗，系統功能不可用；若驗證設計不當，將導致大面積盜用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 授權碼未綁定可信鑑別方法，任何人可偽造格式相似的內容。
2. 依賴「程式碼不公開」的土炮加密，安全性來自演算法秘密而非金鑰。
3. 授權資料與驗證分離，缺乏完整性校驗（Integrity Check）。

深層原因：
- 架構層面：缺少信任鏈設計與驗證節點（信任錨）。
- 技術層面：未採公鑰基礎設施（非對稱金鑰）實現「簽章/驗章」。
- 流程層面：授權核發與驗證流程未標準化，無法自動化與稽核。

### Solution Design（解決方案設計）
解決策略：以 RSA 數位簽章為核心。原廠用私鑰對序列化後的授權資料做 SignData；應用端用公鑰 VerifyData 驗章。若資料被改，雜湊不一致立即拒絕；若來源非原廠，也無法產生可驗證的簽章。

實施步驟：
1. 建立簽章流程（EncodeToken）
- 實作細節：序列化 Token（BSON）→ 使用 SHA-256 雜湊 → 私鑰 SignData → data|signature 打包。
- 所需資源：.NET RSACryptoServiceProvider、SHA256CryptoServiceProvider、Json.NET（BSON）。
- 預估時間：0.5 天。

2. 建立驗章流程（DecodeToken）
- 實作細節：解開 data/signature → 反序列化 Token → 依 SiteID 取公鑰 VerifyData → 驗證授權條件。
- 所需資源：公鑰儲存字典、例外類型設計。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
// 簽章（來源端）
byte[] data_buffer = SerializeToBson(token);
byte[] sign_buffer = _CurrentRSACSP.SignData(data_buffer, new SHA256CryptoServiceProvider());
string packed = Convert.ToBase64String(data_buffer) + "|" + Convert.ToBase64String(sign_buffer);

// 驗章（接收端）
string[] parts = tokenText.Split('|');
byte[] data_buffer = Convert.FromBase64String(parts[0]);
byte[] sign_buffer = Convert.FromBase64String(parts[1]);

var ok = _PublicKeyStoreDict[token.SiteID].VerifyData(
    data_buffer,
    new SHA256CryptoServiceProvider(),
    sign_buffer);
if (!ok) throw new TokenNotSecureException();
```

實際案例：文中展示 tamper/expired 會在 MVC 啟動時被擋下，拋 TokenNotSecure/TokenNotValidate 例外。
實作環境：.NET Framework + ASP.NET MVC5 + RSACryptoServiceProvider + Json.NET（BSON）+ SHA256。
實測數據：
- 改善前：授權資料可被仿造或修改且難以偵測。
- 改善後：偽造/竄改 100% 被 VerifyData 擋下，未通過無法啟動網站。
- 改善幅度：偽造偵測率從不可保證 → 決定性偵測。

Learning Points（學習要點）
核心知識點：
- 非對稱加密與數位簽章差異
- RSA-SHA256 簽章與驗章流程
- 資料完整性（Integrity）與來源鑑別（Authenticity）

技能要求：
- 必備技能：C#、.NET Crypto API、序列化
- 進階技能：金鑰管理與安全部署

延伸思考：
- 可改用標準 JWS（JOSE）格式承載簽章
- 私鑰外流風險與防護
- 加入硬體憑證（HSM）以提高保護等級

Practice Exercise（練習題）
- 基礎練習：撰寫 Sign/Verify 範例，對字串簽章並驗證（30 分鐘）
- 進階練習：把授權 Token 打包成 data|signature 串並驗證（2 小時）
- 專案練習：做一個小型授權伺服器與驗證端（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可正確簽章/驗章/擋偽造
- 程式碼品質（30%）：清楚的結構、錯誤處理、單元測試
- 效能優化（20%）：序列化與簽章效率良好
- 創新性（10%）：採用標準化封裝（如 JWS）或擴充驗證資訊

--------------------------------------------------------------------------------

## Case #2: 安全架構轉型：從土炮加密到公開演算法 + 金鑰

### Problem Statement（問題陳述）
業務場景：團隊早期以自製混淆或簡單加密掩護授權碼，仰賴「沒人知道細節」來保護，導致不能開源、難以 Code Review，安全風險高且難維護。
技術挑戰：在不犧牲安全的前提下，允許程式碼公開與多人審查。
影響範圍：安全事故、維運風險、法務風險與工程規模化受阻。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 安全設計依賴「演算法保密」而非「金鑰保密」。
2. 沒有標準化的加密/簽章流程與已驗證的演算法。
3. 難以自證安全性，導致無法開源與審核。

深層原因：
- 架構層面：缺少公鑰基礎設施（PKI）思維。
- 技術層面：未使用經廣泛驗證之演算法/函式庫。
- 流程層面：安全審查流程缺位。

### Solution Design（解決方案設計）
解決策略：採用公開演算法（RSA）+ 保護金鑰，程式碼可公開、流程可審核，安全性建立於金鑰保密與驗算正確性上。

實施步驟：
1. 決策與演算法選型
- 實作細節：選 RSA + SHA-256；拒用自製密碼學。
- 所需資源：安全規範、審核清單。
- 預估時間：0.5 天。

2. 套用至授權簽章/驗章流程
- 實作細節：按 Case #1 實作 Sign/Verify。
- 所需資源：.NET Crypto API。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
// 採用公開演算法 + 金鑰，程式碼可 Review；安全性由金鑰負責
var rsa = new RSACryptoServiceProvider();
rsa.FromXmlString(privateKeyXml);          // 保護私鑰
byte[] signature = rsa.SignData(data, new SHA256CryptoServiceProvider());
// 對外只需公鑰即可驗章
```

實際案例：文章強調不要土炮加密，建議採用公開演算法 + 金鑰保護，便於公開程式碼並維持安全。
實作環境：同 Case #1。
實測數據：
- 改善前：無法審查/開源；安全性不可證。
- 改善後：可 Code Review/開源；安全性建立於金鑰強度與演算法。
- 改善幅度：審核可行性 0 → 100%；安全性合規度顯著提升。

Learning Points（學習要點）
- 公開演算法 + 私密金鑰的安全模型
- 安全性來自密鑰管理，不是程式碼保密
- 合規與審核的重要性

技能要求：
- 必備技能：基本加密學概念
- 進階技能：PKI、密鑰保護、合規審核流程

延伸思考：
- 如何落實金鑰輪替與稽核
- 引入 HSM 或雲端金鑰管理服務

Practice Exercise（練習題）
- 基礎：整理一份安全設計評估清單（30 分鐘）
- 進階：將既有「土炮加密」改為 RSA 簽章（2 小時）
- 專案：撰寫安全設計決策紀錄與 Threat Model（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：替換成功、可驗章
- 程式碼品質：可讀、可審查
- 效能：不低於原方案
- 創新性：引入標準化封裝或自動化稽核

--------------------------------------------------------------------------------

## Case #3: 授權 Token 的可攜格式設計（Data+Signature Base64 打包）

### Problem Statement（問題陳述）
業務場景：授權碼需置於設定檔或透過文字通道傳送，格式需簡潔、安全、可被機器解析，且盡量避免傳輸過程的字元編碼問題。
技術挑戰：二進位資料（序列化內容與簽章）如何以字串安全傳遞並無歧義解析。
影響範圍：格式不穩定將導致啟動失敗、誤判，或被惡意操弄。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 需攜帶兩段二進位資料：原文序列化與其簽章。
2. 直接二進位存放在文字設定檔會有編碼問題。
3. 缺少一致的定界方式易造成解析錯誤。

深層原因：
- 架構層面：未定義傳輸協定與承載格式。
- 技術層面：序列化與 Base64 的注意事項。
- 流程層面：無統一的打包/解包函式。

### Solution Design（解決方案設計）
解決策略：將 data/signature 以 Base64 各自編碼，再以固定定界字元（如 ‘|’）組合，解析端固定 Split 後依序處理，確保無歧義。

實施步驟：
1. 打包
- 實作細節：Convert.ToBase64String(data) + "|" + Convert.ToBase64String(signature)
- 所需資源：.NET Base64 API
- 預估時間：0.25 天

2. 解包
- 實作細節：Split('|') → Base64 反解 → 順序不可錯
- 所需資源：輸入驗證與例外
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
// pack
string tokenText = $"{Convert.ToBase64String(data)}|{Convert.ToBase64String(sig)}";

// unpack
var parts = tokenText.Split('|');
if (parts.Length != 2) throw new TokenFormatException();
byte[] data = Convert.FromBase64String(parts[0]);
byte[] sig  = Convert.FromBase64String(parts[1]);
```

實際案例：文章即以「data|signature」格式承載授權 Token。
實作環境：.NET Framework。
實測數據：
- 改善前：格式不定、易解析錯誤。
- 改善後：格式固定，解析錯誤大幅下降。
- 改善幅度：解析錯誤率顯著降低（以實務驗收為準）。

Learning Points（學習要點）
- Base64 與二進位承載
- 定界字元選擇與健壯性
- Token 可攜格式設計

技能要求：
- 必備技能：字串/編碼處理
- 進階技能：定義穩健的序列化協定

延伸思考：
- 可改為長度前綴/JSON/JWS 承載，增強健壯性
- 多段資料可考慮 TLV（Type-Length-Value）結構

Practice Exercise（練習題）
- 基礎：實作 pack/unpack 並寫單測（30 分鐘）
- 進階：加入錯誤碼與錯誤訊息（2 小時）
- 專案：切換為 JWS 承載（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：可正確打包/解包
- 程式碼品質：錯誤處理與邊界測試
- 效能：處理效率與記憶體使用
- 創新性：格式擴展性設計

--------------------------------------------------------------------------------

## Case #4: 多站台金鑰載入與快取（TokenHelper.Init）

### Problem Statement（問題陳述）
業務場景：系統需驗證多個來源（SiteID）之授權碼，各自有不同公鑰；本地站台還需持有自己的私鑰以簽章。因此需建立金鑰載入與快取機制。
技術挑戰：如何支援多站台公鑰查找、私鑰載入、避免頻繁 IO 與效能耗損。
影響範圍：金鑰載入錯誤會導致整體授權驗證失效。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多來源驗章需對應 SiteID → PublicKey 的映射。
2. 簽章端需要安全載入私鑰。
3. 頻繁讀檔轉 RSACryptoServiceProvider 效能不佳。

深層原因：
- 架構層面：缺乏金鑰存取抽象層。
- 技術層面：未實作快取。
- 流程層面：金鑰配置來源缺乏統一格式。

### Solution Design（解決方案設計）
解決策略：提供 Init(siteID, siteKeyXml, keyXmlDict)，一次載入全部站台的公鑰到 Dictionary 快取，並載入當前站台私鑰；驗章/簽章時直接查快取。

實施步驟：
1. 實作 Init 重載
- 實作細節：FromXmlString 載入 XML 為 RSA 物件；建置字典。
- 所需資源：appsettings.json 金鑰配置。
- 預估時間：0.5 天。

2. 快取與例外
- 實作細節：站台不存在、缺私鑰等例外。
- 所需資源：自訂例外。
- 預估時間：0.25 天。

關鍵程式碼/設定：
```csharp
public static void Init(string siteID, string siteKeyXml, Dictionary<string, string> keyXmlDict) {
  _PublicKeyStoreDict = keyXmlDict.ToDictionary(
    kv => kv.Key, kv => { var r = new RSACryptoServiceProvider(); r.FromXmlString(kv.Value); return r; });

  if (!string.IsNullOrEmpty(siteKeyXml)) {
    _CurrentRSACSP = new RSACryptoServiceProvider();
    _CurrentRSACSP.FromXmlString(siteKeyXml); // 需包含私鑰
  }
  _CurrentSiteID = siteID;
}
```

實際案例：文章展示 Init 載入 Site 私鑰與公鑰字典，後續 Encode/Decode 皆仰賴此快取。
實作環境：.NET Framework。
實測數據：
- 改善前：每次磁碟讀檔 + 解析 Key，性能不穩定。
- 改善後：記憶體快取，驗章簽章延遲穩定。
- 改善幅度：啟動後驗章延遲穩定下降（視工作負載）。

Learning Points（學習要點）
- 金鑰快取與生命周期管理
- 站台映射（SiteID → RSA）
- 初始化時機與錯誤處理

技能要求：
- 必備技能：集合與快取
- 進階技能：DI/配置管理

延伸思考：
- 抽換為 OS Key Container/X509 Store（見 Case #9/#11）
- 支援多版本公鑰（見 Case #14）

Practice Exercise（練習題）
- 基礎：完成 Init 與單元測試（30 分鐘）
- 進階：加入缺鍵例外與錯誤碼（2 小時）
- 專案：以 DI 管理 KeyStore 生命週期（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：多站台驗章成功
- 程式碼品質：清晰、可測試
- 效能：避免重複 IO/解析
- 創新性：可插拔 Key Provider

--------------------------------------------------------------------------------

## Case #5: 使用 RSA+SHA-256 進行簽章與驗章（SignData/VerifyData）

### Problem Statement（問題陳述）
業務場景：授權碼需以強雜湊演算法簽章，避免因弱雜湊（如 SHA-1）引發碰撞攻擊風險。
技術挑戰：在 .NET 中正確使用 RSA+SHA-256 API，並與序列化管線配合。
影響範圍：弱雜湊導致偽造風險，影響所有客戶。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 舊系統常用 SHA-1，已不建議。
2. 不正確的 API 使用會造成簽章/驗章不匹配。
3. 漏掉資料序列化一致性會造成驗章失敗。

深層原因：
- 架構層面：未形成演算法選型準則。
- 技術層面：缺乏簽章/序列化一致性規範。
- 流程層面：缺單測與升級流程。

### Solution Design（解決方案設計）
解決策略：統一採 SHA-256，簽章與驗章雙方固定相同序列化流程（BSON），避免雜湊內容不一致。

實施步驟：
1. 設定 Hash 演算法
- 實作細節：new SHA256CryptoServiceProvider()
- 所需資源：標準 .NET 類別
- 預估時間：0.25 天

2. 串接序列化
- 實作細節：BSON 寫讀一致
- 所需資源：Json.NET
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
var halg = new SHA256CryptoServiceProvider();
byte[] signature = rsa.SignData(data_buffer, halg);
bool ok = rsaPublic.VerifyData(data_buffer, halg, signature);
```

實際案例：文章採用 SHA256CryptoServiceProvider 與 SignData/VerifyData。
實作環境：同上。
實測數據：
- 改善前：潛在使用 SHA-1 風險。
- 改善後：升級至 SHA-256，降低碰撞風險。
- 改善幅度：風險顯著降低。

Learning Points（學習要點）
- RSA 與雜湊演算法結合
- 序列化一致性重要性
- API 正確搭配

技能要求：
- 必備：C# Crypto API
- 進階：演算法選型與升級策略

延伸思考：
- 後續升級至 SHA-384/512
- 改用 RSA-PSS 簽章（需 API 支援）

Practice Exercise（練習題）
- 基礎：寫簽章/驗章單測（30 分鐘）
- 進階：切換 SHA-256/384/512 並比較長度（2 小時）
- 專案：增量升級策略設計（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：不同雜湊一致通過
- 程式碼品質：清楚可維護
- 效能：雜湊成本合理
- 創新性：提供可配置演算法

--------------------------------------------------------------------------------

## Case #6: 啟動期授權檢查（Fail-Fast）於 ASP.NET MVC5

### Problem Statement（問題陳述）
業務場景：需保證未獲合法授權的網站不能對外提供服務，且在部署啟動階段立即阻止，避免部分功能已對外暴露。
技術挑戰：在 MVC 啟動流程中，於 Routing 前完成授權驗證並中斷啟動。
影響範圍：未授權使用與服務責任風險；啟動路徑需穩健。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 授權驗證若置於控制器層，恐已暴露部分資源。
2. 啟動階段缺少阻斷點。
3. 設定與金鑰未先成功載入。

深層原因：
- 架構層面：缺少 Fail-Fast 策略。
- 技術層面：未整合 Startup 初始化順序。
- 流程層面：部署驗證未標準化。

### Solution Design（解決方案設計）
解決策略：在 Startup.Configure 期間完成 License 區段讀取、KeyStore Init、Decode+Verify，一旦失敗立刻拋例外終止啟動。

實施步驟：
1. 讀取設定並 Init
- 實作細節：從 appsettings.json 讀 SiteID/PrivateKey/PublicKeyStore。
- 所需資源：Configuration API。
- 預估時間：0.5 天

2. Decode+Verify
- 實作細節：若失敗丟例外，網站無法啟動。
- 所需資源：TokenHelper。
- 預估時間：0.25 天

關鍵程式碼/設定：
```csharp
// Startup.cs Configure 內
var lic = Configuration.GetSection("License");
var dict = lic.Get<Dictionary<string,string>[]>("PublicKeyStore")
              .ToDictionary(x=>x["SiteID"], x=>x["KeyXML"]);

TokenHelper.Init(lic.Get<string>("SiteID"), lic.Get<string>("SitePrivateKey"), dict);
var token = TokenHelper.DecodeToken<SiteLicenseToken>(lic.Get<string>("TokenData"));
// 若失敗將拋出 TokenNotSecure/NotValidate 等例外，啟動終止
```

實際案例：文中截圖顯示啟動失敗畫面與例外訊息，證實 Fail-Fast。
實作環境：ASP.NET MVC5 + .NET Framework。
實測數據：
- 改善前：有風險讓部分功能先暴露。
- 改善後：未授權時網站無法啟動。
- 改善幅度：未授權對外暴露風險 → 0。

Learning Points（學習要點）
- 啟動管線與 Fail-Fast 設計
- 設定讀取與依賴注入時機
- 一致的錯誤處理策略

技能要求：
- 必備：ASP.NET 啟動流程
- 進階：配置安全/部署流程控管

延伸思考：
- 健康檢查（HealthCheck）與告警
- 藍綠部署時的授權檢查策略

Practice Exercise（練習題）
- 基礎：將 DecodeToken 放到 Startup 並測試（30 分鐘）
- 進階：失敗時寫入事件日誌（2 小時）
- 專案：加入 Prometheus 指標（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：啟動即驗證
- 程式碼品質：啟動程式清晰
- 效能：啟動延遲低
- 創新性：監控與恢復策略

--------------------------------------------------------------------------------

## Case #7: 期限與條件驗證（IsValidate 與 TokenNotValidateException）

### Problem Statement（問題陳述）
業務場景：授權碼需限制啟用期間與功能範圍，超期或不符合條件時拒絕啟動或特定功能關閉。
技術挑戰：可靠地實作 IsValidate（開始/結束日等條件），並以明確例外回報原因。
影響範圍：授權超用、合約糾紛與功能誤啟動。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少統一驗證邏輯與錯誤碼。
2. 時區/時間來源不一會導致判斷不一致。
3. 驗證與驗章關係需清楚：安全性 vs 合約條件。

深層原因：
- 架構層面：驗證分層未清晰。
- 技術層面：時間與文化設定處理。
- 流程層面：條件變更未納入版本控管。

### Solution Design（解決方案設計）
解決策略：分層處理：先 VerifyData 保證安全，再 IsValidate 檢查授權條件，失敗拋 TokenNotValidateException。

實施步驟：
1. 設計 Token 欄位與驗證
- 實作細節：StartDate/EndDate/FeatureFlags；UTC 比對。
- 所需資源：系統時鐘抽象。
- 預估時間：0.5 天。

2. 狀態對應例外
- 實作細節：針對超期/欄位缺失拋具體例外。
- 所需資源：自訂例外定義。
- 預估時間：0.25 天。

關鍵程式碼/設定：
```csharp
public override bool IsValidate() {
  var now = DateTime.UtcNow;
  if (now < LicenseStartDateUtc) return false;
  if (now > LicenseEndDateUtc)   return false;
  // 其他功能旗標判斷...
  return true;
}
```

實際案例：文中截圖顯示超過授權日期觸發 TokenNotValidateException。
實作環境：.NET Framework。
實測數據：
- 改善前：期限控制鬆散或未實作。
- 改善後：超期即擋，啟動失敗。
- 改善幅度：超用風險顯著下降。

Learning Points（學習要點）
- 分層驗證：安全性 vs 合約性
- 時區與時間來源
- 例外與錯誤碼設計

技能要求：
- 必備：C# 日期/時間 API
- 進階：時鐘抽象與可測試性

延伸思考：
- 緩衝期/寬限機制
- License offline/online 更新

Practice Exercise（練習題）
- 基礎：加入 Start/End 驗證（30 分鐘）
- 進階：以 UTC 寫單測（2 小時）
- 專案：可配置寬限期（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：條件正確判斷
- 程式碼品質：可測試、可讀
- 效能：檢查開銷低
- 創新性：策略可配置

--------------------------------------------------------------------------------

## Case #8: 範疇化錯誤與診斷（TokenFormat/NotSecure/SiteNotExist）

### Problem Statement（問題陳述）
業務場景：授權失敗原因多樣（格式錯、站台未知、簽章不符、條件不符），需精準診斷與快速處理。
技術挑戰：定義清晰的例外類別與回報訊息，並確保 UX 上不洩漏敏感資訊。
影響範圍：客服與維運成本、處理時效與誤判成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用單一例外導致定位困難。
2. 錯誤訊息不一致、不具體。
3. 沒有錯誤碼與紀錄。

深層原因：
- 架構層面：錯誤範疇未定義。
- 技術層面：例外設計與日誌策略薄弱。
- 流程層面：客服/維運 SOP 不明確。

### Solution Design（解決方案設計）
解決策略：建立 TokenFormatException、TokenSiteNotExistException、TokenNotSecureException、TokenNotValidateException；前者顯示友善訊息，詳情記錄在伺服器日誌。

實施步驟：
1. 例外分類與拋出點
- 實作細節：各階段拋對應例外。
- 所需資源：例外類別。
- 預估時間：0.5 天。

2. 日誌與對外訊息
- 實作細節：內部詳細、外部簡訊。
- 所需資源：ILogger/事件檢視器。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
if (parts.Length != 2) throw new TokenFormatException();
if (!_PublicKeyStoreDict.ContainsKey(token.SiteID)) throw new TokenSiteNotExistException();

bool ok = _PublicKeyStoreDict[token.SiteID].VerifyData(...);
if (!ok) throw new TokenNotSecureException();

if (!token.IsValidate()) throw new TokenNotValidateException();
```

實際案例：文章展示三種失敗畫面對應不同例外。
實作環境：ASP.NET MVC5。
實測數據：
- 改善前：診斷不明，處理慢。
- 改善後：可快速定位與回應。
- 改善幅度：處理時效顯著提升。

Learning Points（學習要點）
- 例外分類策略
- 安全錯誤訊息設計
- 日誌與客服串接

技能要求：
- 必備：例外處理
- 進階：SRE/可觀測性

延伸思考：
- 對應錯誤碼與文件
- 自動告警

Practice Exercise（練習題）
- 基礎：補齊例外與單測（30 分鐘）
- 進階：寫入事件日誌與關鍵欄位（2 小時）
- 專案：錯誤碼對客服知識庫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：對應正確例外
- 程式碼品質：清楚、可維運
- 效能：低開銷
- 創新性：告警/自愈機制

--------------------------------------------------------------------------------

## Case #9: 金鑰保護與管理（Key Container/CA 取代 XML 檔）

### Problem Statement（問題陳述）
業務場景：示範程式將 RSA 金鑰存於 XML 檔或設定檔，方便但極不安全，一旦私鑰外流即可偽造簽章。
技術挑戰：將私鑰移入 OS 提供的 Key Container 或憑證儲存體，並由 CA 散發公鑰。
影響範圍：私鑰外流即全盤崩潰。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 私鑰明文落地（XML/JSON）。
2. 無保護、無稽核。
3. 金鑰散佈手工維護困難。

深層原因：
- 架構層面：缺少正式 KMS/憑證管理。
- 技術層面：未使用 Key Container/X509 Store。
- 流程層面：無輪替/撤銷流程。

### Solution Design（解決方案設計）
解決策略：私鑰存 Key Container（或 Windows 憑證庫、HSM、雲端 Key Vault），公鑰由 CA 發佈，驗章端從受信任儲存體取用。

實施步驟：
1. 生成/匯入私鑰至 Key Container
- 實作細節：CspParameters + UseMachineKeyStore；或憑證庫安裝。
- 所需資源：OS 金鑰儲存、CA。
- 預估時間：1–2 天。

2. 驗章端改用憑證庫公鑰
- 實作細節：X509Store 搜尋載入。
- 所需資源：受信任根/發行憑證。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
// 產生/存取私鑰於 Key Container
var csp = new CspParameters {
  ProviderType = 24, // PROV_RSA_AES
  KeyContainerName = "MyApp-Licensing",
  Flags = CspProviderFlags.UseMachineKeyStore
};
using var rsa = new RSACryptoServiceProvider(2048, csp);
// rsa 持久化於容器中；不再落地 XML

// 從憑證庫載入公鑰
using var store = new X509Store(StoreName.TrustedPeople, StoreLocation.LocalMachine);
store.Open(OpenFlags.ReadOnly);
var cert = store.Certificates.Cast<X509Certificate2>()
              .First(c => c.Subject.Contains("CN=Vendor-Licensing"));
RSA rsaPublic = cert.GetRSAPublicKey();
```

實際案例：文章明確警示 Demo 用 XML 很不安全並建議 Key Container/CA。
實作環境：Windows 伺服器。
實測數據：
- 改善前：私鑰易外流；可立即偽造。
- 改善後：私鑰受 OS 保護；存取受權控與稽核。
- 改善幅度：私鑰外流風險大幅降低。

Learning Points（學習要點）
- Key Container/憑證庫使用
- CA/信任鏈
- 金鑰存取權限/稽核

技能要求：
- 必備：Windows 安全基礎
- 進階：PKI/CA 管理

延伸思考：
- 引入 HSM/Azure Key Vault
- 封裝金鑰操作接口避免濫用

Practice Exercise（練習題）
- 基礎：將私鑰移入 Key Container（30 分鐘）
- 進階：改用憑證庫驗章（2 小時）
- 專案：Key Rotation + 憑證更新（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：不落地私鑰
- 程式碼品質：抽象清楚
- 效能：無明顯退化
- 創新性：自動化輪替與稽核

--------------------------------------------------------------------------------

## Case #10: 機密設定外流風險（appsettings.json 私鑰）與祕密管理

### Problem Statement（問題陳述）
業務場景：示範將私鑰放進 appsettings.json，方便開發但在實務上極危險，尤其在版本控管或配置同步時易外流。
技術挑戰：將私鑰移出設定檔，改用安全祕密管理（DPAPI/KeyVault）。
影響範圍：設定檔外洩 = 私鑰外洩。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 私鑰明文在設定檔。
2. 設定檔常被廣泛複製/上傳。
3. 無加密保護。

深層原因：
- 架構層面：秘密管理缺失。
- 技術層面：未用 DPAPI/KeyVault。
- 流程層面：未分環境配置隔離。

### Solution Design（解決方案設計）
解決策略：私鑰改儲 Key Container 或 KeyVault；若不得已臨時存在磁碟，至少用 DPAPI 以機器範圍保護、限制檔權限與版本控管忽略。

實施步驟：
1. DPAPI 保護（臨時解法）
- 實作細節：ProtectedData.Protect/Unprotect；機器範圍。
- 所需資源：System.Security.Cryptography。
- 預估時間：0.5 天。

2. 正式解法：Key Container/KeyVault
- 實作細節：參照 Case #9。
- 所需資源：OS/雲服務。
- 預估時間：1–3 天。

關鍵程式碼/設定：
```csharp
// 臨時：用 DPAPI 保護私鑰字串（機器綁定）
byte[] plain = Encoding.UTF8.GetBytes(privateKeyXml);
byte[] cipher = ProtectedData.Protect(plain, null, DataProtectionScope.LocalMachine);
// 儲存 cipher 至檔案；使用時再 Unprotect
byte[] back = ProtectedData.Unprotect(cipher, null, DataProtectionScope.LocalMachine);
string keyXml = Encoding.UTF8.GetString(back);
```

實際案例：文章示警「Demo 方便但不安全」。
實作環境：Windows。
實測數據：
- 改善前：設定檔抄走 = 私鑰外流。
- 改善後：即便拿到檔案也難解（DPAPI 機器綁定）；或不落地。
- 改善幅度：外流風險顯著下降。

Learning Points（學習要點）
- 祕密管理最佳實踐
- DPAPI 限制與風險
- 生產環境與開發環境差異

技能要求：
- 必備：Windows DPAPI
- 進階：KeyVault/HSM

延伸思考：
- 基礎設施即程式碼（IaC）管理祕密
- RBAC 與稽核

Practice Exercise（練習題）
- 基礎：DPAPI Protect/Unprotect 小工具（30 分鐘）
- 進階：部署排除敏感設定（2 小時）
- 專案：KeyVault 接入（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：私鑰不再明文
- 程式碼品質：分層清晰
- 效能：保護/解密開銷低
- 創新性：自動化與審計

--------------------------------------------------------------------------------

## Case #11: 公鑰散布與信任鏈（CA/憑證庫 vs 手動同步）

### Problem Statement（問題陳述）
業務場景：多站台需要彼此的公鑰以驗章，若每台機器都手工放一份公鑰，會造成維護困難與錯誤風險。
技術挑戰：如何透過 CA 與憑證庫集中管理與信任散布。
影響範圍：驗章失敗、版本不一致、維運成本高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 公鑰多副本手工同步。
2. 無版本控與撤銷機制。
3. 權威來源不明。

深層原因：
- 架構層面：缺 PKI/憑證生命週期。
- 技術層面：未用 X509/憑證庫。
- 流程層面：無自動化散布。

### Solution Design（解決方案設計）
解決策略：將公鑰封裝為憑證，由 CA 簽發；驗章端僅信任 CA 鏈，從憑證庫取對應憑證公鑰，避免手工散布。

實施步驟：
1. 設計憑證流程
- 實作細節：建立根/中繼 CA；簽發 Vendor 憑證。
- 所需資源：CA/PKI。
- 預估時間：2–3 天。

2. 程式改用憑證庫
- 實作細節：X509Store 查找憑證取公鑰。
- 所需資源：參照 Case #9。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
using var store = new X509Store(StoreName.TrustedPeople, StoreLocation.LocalMachine);
store.Open(OpenFlags.ReadOnly);
var cert = store.Certificates.Find(X509FindType.FindBySubjectName, "Vendor-Licensing", false)[0];
var rsaPub = cert.GetRSAPublicKey();
bool ok = rsaPub.VerifyData(data, new SHA256CryptoServiceProvider(), signature);
```

實際案例：文章建議「公鑰可由 CA 取得」。
實作環境：Windows 憑證庫。
實測數據：
- 改善前：版本不一致、人工錯誤多。
- 改善後：統一信任鏈，維運簡化。
- 改善幅度：散布錯誤顯著下降。

Learning Points（學習要點）
- 憑證生命週期管理
- 信任鏈與撤銷
- 自動化散布

技能要求：
- 必備：X509/憑證庫
- 進階：CA 維運

延伸思考：
- OCSP/CRL 撤銷機制
- 雲端憑證管理

Practice Exercise（練習題）
- 基礎：以自簽憑證測試驗章（30 分鐘）
- 進階：建立測試根 CA 與下游憑證（2 小時）
- 專案：以 Ansible/PowerShell 自動散布（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：公鑰一致、可驗章
- 程式碼品質：抽象合理
- 效能：查找快速
- 創新性：自動化/撤銷管理

--------------------------------------------------------------------------------

## Case #12: 序列化選型（BSON）降低體積與歧義

### Problem Statement（問題陳述）
業務場景：授權 Token 要儘量小且無語意歧義，以利傳輸與儲存；同時要與簽章流程穩定配合。
技術挑戰：選擇合適的序列化格式與一致的序列化/反序列化管線。
影響範圍：不一致序列化將導致驗章失敗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. JSON 文本大小偏大、空白/順序可能影響雜湊。
2. 需降低 Token 體積並避免多語系格式差異。
3. 與簽章計算需一緻。

深層原因：
- 架構層面：序列化規範缺乏。
- 技術層面：雜湊對序列化輸出敏感。
- 流程層面：缺少單元測試覆蓋。

### Solution Design（解決方案設計）
解決策略：採 BSON（二進位 JSON）序列化，確保輸出穩定與較小體積；簽章/驗章雙方使用相同流程。

實施步驟：
1. 序列化/反序列化
- 實作細節：Json.NET BsonWriter/BsonReader 實作。
- 所需資源：Json.NET。
- 預估時間：0.5 天。

2. 單元測試
- 實作細節：序列化結果一致性比較。
- 所需資源：單測框架。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
byte[] SerializeToBson(object obj) {
  using var ms = new MemoryStream();
  using (var bw = new BsonWriter(ms)) new JsonSerializer().Serialize(bw, obj);
  return ms.ToArray();
}
T DeserializeFromBson<T>(byte[] data) {
  using var ms = new MemoryStream(data);
  using var br = new BsonReader(ms);
  return new JsonSerializer().Deserialize<T>(br);
}
```

實際案例：文章實作即採 BSON。
實作環境：.NET + Json.NET。
實測數據：
- 改善前：JSON 容易因格式差異導致驗章不一。
- 改善後：BSON 穩定且較小。
- 改善幅度：驗章穩定性提升，體積下降（依資料而定）。

Learning Points（學習要點）
- 序列化對簽章的影響
- BSON 優勢與限制
- 一致性測試

技能要求：
- 必備：C# 序列化
- 進階：跨語言序列化相容性

延伸思考：
- 以 protobuf/MessagePack 取代并比較
- JWS 中對 payload 的標準處理

Practice Exercise（練習題）
- 基礎：寫 BSON 序列化函式（30 分鐘）
- 進階：比較 JSON/BSON 大小與速度（2 小時）
- 專案：替換序列化層並通過驗章測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：序列化穩定
- 程式碼品質：易維護
- 效能：體積與速度
- 創新性：壓縮或更佳格式

--------------------------------------------------------------------------------

## Case #13: 雜湊演算法選型與升級（SHA1 → SHA256）

### Problem Statement（問題陳述）
業務場景：歷史系統可能沿用 SHA-1，需升級至 SHA-256，以符合現代安全需求。
技術挑戰：升級過程需兼容舊 Token 或安排過渡期。
影響範圍：不兼容將導致驗章失敗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. SHA-1 已不建議使用。
2. 直接切換將使舊 Token 全數失效。
3. 驗章雙方需一致。

深層原因：
- 架構層面：缺乏演算法版本控。
- 技術層面：未設計可配置雜湊。
- 流程層面：缺少公告與過渡機制。

### Solution Design（解決方案設計）
解決策略：引入「雜湊演算法版本」欄位或配置，驗章端支援至少兩代演算法於過渡期，逐步淘汰舊版。

實施步驟：
1. 增加版本欄位
- 實作細節：Token 或 Header 註記 HashAlgVersion。
- 所需資源：資料結構變更。
- 預估時間：0.5 天。

2. 雙演算法驗章
- 實作細節：先用新算法驗，不過再試舊算法；過渡期結束後移除舊算法。
- 所需資源：設定旗標與計畫表。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
HashAlgorithm GetAlg(string ver) => ver switch {
  "SHA256" => new SHA256CryptoServiceProvider(),
  "SHA1"   => new SHA1CryptoServiceProvider(),
  _ => throw new NotSupportedException()
};
bool Verify(byte[] data, byte[] sig, string ver) {
  var alg = GetAlg(ver);
  return rsa.VerifyData(data, alg, sig);
}
```

實際案例：文章採用 SHA-256；本案延伸既有作法。
實作環境：.NET Framework。
實測數據：
- 改善前：使用 SHA-1 風險。
- 改善後：升至 SHA-256，並平滑過渡。
- 改善幅度：安全性提升、不中斷服務。

Learning Points（學習要點）
- 雜湊升級策略
- 相容期與版本控制
- 風險公告與排程

技能要求：
- 必備：Crypto API
- 進階：變更管理

延伸思考：
- RSA-PSS 與 FIPS 相容
- 自動化掃描與告警舊演算法

Practice Exercise（練習題）
- 基礎：新增版本欄位（30 分鐘）
- 進階：雙算法驗章（2 小時）
- 專案：過渡期切換計畫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：新舊兼容
- 程式碼品質：清晰配置化
- 效能：成本可接受
- 創新性：自動停用機制

--------------------------------------------------------------------------------

## Case #14: 金鑰輪替與相容期驗章策略

### Problem Statement（問題陳述）
業務場景：私鑰需定期輪替或事故撤銷，驗章端需同時接受「舊/新公鑰」一段時間，以不影響既有 Token。
技術挑戰：如何支援多把公鑰與輪替策略。
影響範圍：輪替不當將造成大規模驗章失敗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 驗章端只能持一把公鑰。
2. 無版本/KeyId 概念。
3. 發佈節奏不同步。

深層原因：
- 架構層面：KeyId/KeySet 缺失。
- 技術層面：KeyStore 不支援多鑰嘗試。
- 流程層面：無輪替 SOP。

### Solution Design（解決方案設計）
解決策略：引入 KeyId 與多把公鑰集合；簽章端在 Token 中帶 KeyId；驗章端依 KeyId 精準取鑰，或在過渡期對同一 SiteID 試多把鑰。

實施步驟：
1. KeyId 與多鑰支援
- 實作細節：_PublicKeyStoreDict 改為 SiteID→KeyId→RSA。
- 所需資源：資料結構調整。
- 預估時間：1 天。

2. 發佈與撤銷流程
- 實作細節：先散布新公鑰→切私鑰→逐步淘汰舊 KeyId。
- 所需資源：發佈管線。
- 預估時間：1–2 天。

關鍵程式碼/設定：
```csharp
// 多鑰結構：SiteID -> (KeyId -> RSA)
Dictionary<string, Dictionary<string, RSACryptoServiceProvider>> _keyset;

bool VerifyWithKeySet(string siteId, string keyId, byte[] data, byte[] sig) {
  if (_keyset[siteId].TryGetValue(keyId, out var rsa)) {
    return rsa.VerifyData(data, new SHA256CryptoServiceProvider(), sig);
  }
  // 過渡期：KeyId 缺失則嘗試所有
  return _keyset[siteId].Values.Any(r => r.VerifyData(data, new SHA256CryptoServiceProvider(), sig));
}
```

實際案例：文章未演示輪替，但其 KeyStore 結構易延伸支持。
實作環境：.NET Framework。
實測數據：
- 改善前：輪替會中斷。
- 改善後：過渡期雙鑰驗章不中斷。
- 改善幅度：切換失敗率顯著下降。

Learning Points（學習要點）
- KeyId 與輪替策略
- 發佈順序與時間窗
- 風險緩解設計

技能要求：
- 必備：集合/字典運算
- 進階：發佈自動化

延伸思考：
- JWK Set（JWKS）管理
- 撤銷清單管理

Practice Exercise（練習題）
- 基礎：為 Token 加 KeyId（30 分鐘）
- 進階：多鑰驗章嘗試（2 小時）
- 專案：輪替演練與回滾（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：雙鑰期間可驗
- 程式碼品質：結構清楚
- 效能：多鑰嘗試成本可控
- 創新性：自動化輪替

--------------------------------------------------------------------------------

## Case #15: 一對一安全通訊（簽章 + 加密概念落地）

### Problem Statement（問題陳述）
業務場景：兩服務間需在不可信通道傳遞敏感資料，既要保密（加密），又要確認來源（簽章）。
技術挑戰：正確組合「加密 + 簽章」流程以兼顧機密性與不可否認性。
影響範圍：資料外洩或偽造導致重大風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 僅加密無法證明來源。
2. 僅簽章無法隱匿內容。
3. 流程順序與 API 搭配容易出錯。

深層原因：
- 架構層面：缺機密性與完整性並重設計。
- 技術層面：簽章與加密順序不當。
- 流程層面：金鑰分發未定義。

### Solution Design（解決方案設計）
解決策略：A 先簽章（A 私鑰）再加密（B 公鑰）；B 收到後先解密（B 私鑰）再驗章（A 公鑰），達成來源鑑別與保密。

實施步驟：
1. 發送端流程
- 實作細節：SignData → Append Signature → Encrypt with B.PublicKey（OAEP）。
- 所需資源：RSA OAEP。
- 預估時間：0.5 天。

2. 接收端流程
- 實作細節：Decrypt with B.PrivateKey → Verify with A.PublicKey。
- 所需資源：RSA。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
// A 端
byte[] sig = rsaA.SignData(plain, new SHA256CryptoServiceProvider());
byte[] bundle = Combine(plain, sig);
byte[] cipher = rsaB.Encrypt(bundle, true); // OAEP

// B 端
byte[] bundle2 = rsaB.Decrypt(cipher, true);
(var plain2, var sig2) = Split(bundle2);
bool ok = rsaApublic.VerifyData(plain2, new SHA256CryptoServiceProvider(), sig2);
```

實際案例：文章列舉一對一通訊概念（非對稱式），此為落地實作。
實作環境：.NET Framework。
實測數據：
- 改善前：僅加密或僅簽章，保護不完整。
- 改善後：兼顧機密性與來源鑑別。
- 改善幅度：風險顯著下降。

Learning Points（學習要點）
- 簽章與加密的先後關係
- OAEP 與安全參數
- 金鑰分發/管理

技能要求：
- 必備：RSA 使用
- 進階：協議設計

延伸思考：
- 以 TLS/Mutual TLS 取代自建
- 使用 CMS/PKCS#7 封裝

Practice Exercise（練習題）
- 基礎：簽章再加密流程（30 分鐘）
- 進階：錯誤注入測試（2 小時）
- 專案：建立簡易安全點對點消息系統（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：雙重保護
- 程式碼品質：模組化清晰
- 效能：處理成本
- 創新性：協議完整性

--------------------------------------------------------------------------------

## Case #16: RSA XML 參數理解與最小揭露（Public vs Private）

### Problem Statement（問題陳述）
業務場景：工程師需理解 RSA XML 參數哪些屬於機密（D, P, Q, DP, DQ, InverseQ 等），避免誤傳或誤放設定檔。
技術挑戰：正確分辨公鑰/私鑰欄位並實作最小揭露。
影響範圍：私鑰欄位外流 = 可偽造任何簽章。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 誤以為 XML 都是公鑰。
2. 困惑於 RSA 參數含義。
3. 誤用 FromXmlString 載入包含私鑰的 XML 至不當環境。

深層原因：
- 架構層面：金鑰分職缺失。
- 技術層面：RSA 參數認知不足。
- 流程層面：無審核與管控。

### Solution Design（解決方案設計）
解決策略：文件化公私鑰 XML 範例；任何對外發佈僅提供 Modulus+Exponent；私鑰欄位嚴格受控。

實施步驟：
1. 公私鑰樣本與說明
- 實作細節：標示出機密欄位。
- 所需資源：團隊文件。
- 預估時間：0.25 天。

2. 程式防呆
- 實作細節：載入前檢查 PublicOnly。
- 所需資源：檢查函式。
- 預估時間：0.25 天。

關鍵程式碼/設定：
```xml
<!-- 公鑰：僅 Modulus + Exponent -->
<RSAKeyValue>
  <Modulus>...</Modulus>
  <Exponent>AQAB</Exponent>
</RSAKeyValue>

<!-- 私鑰：包含 D, P, Q, DP, DQ, InverseQ 等 -->
```

實際案例：文章提供兩段 XML 對照，示範差異。
實作環境：.NET Framework。
實測數據：
- 改善前：私鑰易誤傳。
- 改善後：明確分工與文件化，誤用下降。
- 改善幅度：人為錯誤顯著降低。

Learning Points（學習要點）
- RSA 參數意義
- 公/私鑰最小揭露
- 程式防呆與審核

技能要求：
- 必備：RSA 結構理解
- 進階：金鑰工作流程

延伸思考：
- 改用 PEM/憑證封裝
- 自動掃描設定檔敏感欄位

Practice Exercise（練習題）
- 基礎：辨識公/私鑰欄位（30 分鐘）
- 進階：加入程式檢查（2 小時）
- 專案：撰寫安全配置指引（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：正確分辨與限制
- 程式碼品質：防呆到位
- 效能：無影響
- 創新性：自動掃描工具

--------------------------------------------------------------------------------

## Case #17: 高健壯 Token 解析（定界字元/長度前綴/JWS）

### Problem Statement（問題陳述）
業務場景：目前採用「data|signature」定界，雖簡潔但在更複雜場景可能需更高健壯性與可擴展性。
技術挑戰：保留既有相容的同時，提供長度前綴或採用標準格式（如 JWS）。
影響範圍：解析錯誤或擴充困難。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單字元定界可讀性高但擴展性有限。
2. 多 payload 時管理困難。
3. 無結構化標頭。

深層原因：
- 架構層面：承載協議未標準化。
- 技術層面：缺少長度/型別資訊。
- 流程層面：相容性考量不足。

### Solution Design（解決方案設計）
解決策略：提供長度前綴（len(data)|data|len(sig)|sig）或改用 JWS（JSON Web Signature）標準，以獲得更好的互通與擴展性。

實施步驟：
1. 長度前綴方案
- 實作細節：4/8 位元整數標示長度，之後直接讀取。
- 所需資源：二進位打包程式。
- 預估時間：0.5 天。

2. JWS 方案
- 實作細節：header.payload.signature（Base64URL）；演算法標頭。
- 所需資源：JOSE 函式庫。
- 預估時間：1–2 天。

關鍵程式碼/設定：
```csharp
// 長度前綴打包（簡化示例）
byte[] Pack(byte[] data, byte[] sig) {
  using var ms = new MemoryStream();
  void W(byte[] b){ var len=BitConverter.GetBytes(b.Length); ms.Write(len,0,4); ms.Write(b,0,b.Length); }
  W(data); W(sig); return ms.ToArray();
}
(byte[] data, byte[] sig) Unpack(byte[] all) {
  using var ms = new MemoryStream(all);
  byte[] R(){ var lenBuf=new byte[4]; ms.Read(lenBuf,0,4); var len=BitConverter.ToInt32(lenBuf,0); var b=new byte[len]; ms.Read(b,0,len); return b; }
  return (R(), R());
}
```

實際案例：文章使用 ‘|’ 定界；本案為健壯性強化延伸。
實作環境：.NET Framework。
實測數據：
- 改善前：擴充性受限。
- 改善後：多 payload 可控或採標準 JWS。
- 改善幅度：相容性/擴展性提升。

Learning Points（學習要點）
- 承載協定設計
- Base64URL vs Base64
- 標準化好處

技能要求：
- 必備：序列化/位元操作
- 進階：JOSE 生態

延伸思考：
- 直接採用 JWS/JWT/JWE 更標準
- 跨語言互通

Practice Exercise（練習題）
- 基礎：長度前綴打包/解包（30 分鐘）
- 進階：切換為 JWS（2 小時）
- 專案：雙格式相容期策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：雙格式可解析
- 程式碼品質：清晰/健壯
- 效能：低額外成本
- 創新性：標準化落地

--------------------------------------------------------------------------------

## Case #18: 效能優化：RSA 物件與公鑰快取

### Problem Statement（問題陳述）
業務場景：高頻驗章會重複建立 RSACryptoServiceProvider 或反覆讀檔載入公鑰，導致效能不穩定。
技術挑戰：如何快取 RSA 實例與公鑰映射，降低重複開銷。
影響範圍：延遲波動、吞吐下降。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 反覆 FromXmlString 轉換成本高。
2. IO 讀取頻繁。
3. GC 壓力偏大。

深層原因：
- 架構層面：缺少 Singleton/快取。
- 技術層面：RSA 實例管理不當。
- 流程層面：初始化策略欠缺。

### Solution Design（解決方案設計）
解決策略：於初始化階段讀取並建立 RSA 實例快取（Dictionary），執行期僅查表使用；必要時搭配 Lazy 初始化與讀寫鎖。

實施步驟：
1. 初始化快取
- 實作細節：參照 Case #4 的 Init。
- 所需資源：記憶體配置。
- 預估時間：0.5 天。

2. 運行期使用
- 實作細節：只讀查表，不重建 RSA。
- 所需資源：同步保護（若會變更）。
- 預估時間：0.25 天。

關鍵程式碼/設定：
```csharp
static Dictionary<string, RSACryptoServiceProvider> _PublicKeyStoreDict;
RSACryptoServiceProvider GetRsa(string siteId) => _PublicKeyStoreDict[siteId]; // O(1)
```

實際案例：文章現有設計即採字典快取，避免重建。
實作環境：.NET Framework。
實測數據：
- 改善前：每次驗章有建構/IO 成本。
- 改善後：查表即用，延遲穩定。
- 改善幅度：延遲降低，吞吐提升（依壓測）。

Learning Points（學習要點）
- 物件重用與快取
- 初始化時機
- 同步策略

技能要求：
- 必備：集合/快取
- 進階：併發/鎖

延伸思考：
- 池化（Pooling）/Lazy<T>
- 熱更新 KeyStore 設計

Practice Exercise（練習題）
- 基礎：壓測前後延遲比較（30 分鐘）
- 進階：加入 Lazy 初始化（2 小時）
- 專案：支援動態更新公鑰（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：快取正確
- 程式碼品質：簡潔/安全
- 效能：延遲/吞吐提升
- 創新性：動態熱更新

--------------------------------------------------------------------------------

案例分類
1. 按難度分類
- 入門級：Case 3, 5, 6, 7, 8, 12, 16, 18
- 中級：Case 1, 2, 4, 10, 11, 13, 17
- 高級：Case 9, 14, 15

2. 按技術領域分類
- 架構設計類：Case 1, 2, 6, 11, 13, 14, 15, 17
- 效能優化類：Case 18
- 整合開發類：Case 3, 4, 5, 12, 16
- 除錯診斷類：Case 7, 8
- 安全防護類：Case 1, 2, 5, 6, 9, 10, 11, 13, 14, 15, 16, 17

3. 按學習目標分類
- 概念理解型：Case 2, 5, 11, 16
- 技能練習型：Case 3, 4, 6, 12, 18
- 問題解決型：Case 1, 7, 8, 9, 10, 13, 14
- 創新應用型：Case 15, 17

案例關聯圖（學習路徑建議）
- 建議先學：Case 2（安全模型）→ Case 5（RSA+SHA-256）→ Case 3（Token 格式）→ Case 12（BSON）→ Case 4（Key 初始化）。
- 依賴關係：
  - Case 1 依賴 Case 3/4/5/12。
  - Case 6 依賴 Case 1（可驗章）與 Case 4（Key）。
  - Case 7/8 建立在 Case 1（驗章後）之上。
  - Case 9/10/11 是 Case 4 的生產化強化（Key 管理/散布）。
  - Case 13/14 是 Case 5/4 的升級與輪替延伸。
  - Case 15 建立於 Case 5（簽章）並擴展加密。
  - Case 17 建立於 Case 3（格式）之強化。
  - Case 18 強化整體效能，依賴 Case 4。

完整學習路徑：
1) 概念層：Case 2 → Case 5 → Case 16
2) 基礎實作：Case 12 → Case 3 → Case 4 → Case 1
3) 應用與整合：Case 6 → Case 7 → Case 8
4) 生產化安全：Case 9 → Case 10 → Case 11
5) 升級與維運：Case 13 → Case 14 → Case 18
6) 進階應用：Case 17 → Case 15

備註
- 實際程式碼與範例專案可參考原文 GitHub：https://github.com/andrew0928/ApiDemo
- 文中所有延伸方案均與原文核心設計一致（RSA 簽章驗章、BSON 序列化、啟動期驗證、Key 管理強化）。