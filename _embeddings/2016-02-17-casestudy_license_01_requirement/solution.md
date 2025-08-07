# 設計案例 –「授權碼」如何實作？#1 需求與問題

# 問題／解決方案 (Problem/Solution)

## Problem: 離線環境中仍須有效控管網站授權

**Problem**:  
商用系統採 Install-Based 模式部署在客戶資料中心（Service #B、#C）。現場常處於無法連上 Internet 的封閉網路，但仍必須：
1. 依照 Service Administrator（原廠）所發的「授權碼」決定哪些功能可被啟用。  
2. 防止客戶 IT 或系統整合廠商直接修改設定檔、繞過授權機制。

**Root Cause**:  
• 現有授權驗證流程高度依賴線上授權伺服器；離線時無替代機制。  
• 授權資訊存放於純文字或易於修改的設定檔，缺乏加密與簽章保護。  
• 工程師對安全性（對稱／非對稱加解密、數位簽章）的理解不足，導致架構鬆散，程式碼易演變成 spaghetti code。

**Solution**:  
• 引入「離線可驗證」的 License Token：  
  - 以非對稱加密產出序列化後的 License Payload（功能清單、到期日…）。  
  - Payload 以私鑰產生數位簽章並寫入授權檔，系統端僅需公鑰即可驗證。  
• 授權讀取與驗證封裝成獨立元件 (LicenseProvider)；任何功能在啟用前呼叫 `LicenseProvider.IsFeatureEnabled("FeatureX")`。  
• 不需要連線即可驗證簽章 → 解決離線場域需求。  
• 即使掌握設定檔格式，沒有私鑰仍無法竄改或偽造授權。

---

## Problem: 內部服務之間呼叫 API 時，需要僅憑 API Key 判斷權限

**Problem**:  
Service #B 需呼叫位於雲端或 Intranet 的 Service #A 之 API。呼叫過程必須只藉由 API Key 便能決定開放哪些端點與操作，且此機制同樣要可離線部署。

**Root Cause**:  
• 權限判斷與 API 驗證邏輯寫死在程式碼，或倚賴線上授權伺服器。  
• 沒有標準化 Key 產生／輪替流程。  
• 缺乏對稱 vs. 非對稱機制的正確選型，造成 API Key 易被仿造。

**Solution**:  
• 將 API Key 設計為 JWT / JWS 類型的簽章 Token：  
  - Header 指定演算法 (e.g., RS256)。  
  - Payload 含客戶代碼、可用 API 列表、到期日等欄位。  
  - 由原廠私鑰簽章， Service #A 僅需公鑰驗證。  
• Service #A 收到請求時：  
  1. 解析 Token → 驗證簽章。  
  2. 讀取 Payload → 決定授權 API。  
• Token 為文字字串，易於透過 HTTP Header 傳遞；離線部署亦無須即時聯外。

---

## Problem: 授權需自動隨合約期限失效並可替換

**Problem**:  
每張授權需符合商業合約；合約到期後系統應自動停止服務，續約後再匯入新授權即可恢復。

**Root Cause**:  
• 現有機制只驗證「是否存在授權」，未驗證「授權期限」。  
• 沒有安全模式的日期欄位，易被手動修改。  
• 缺乏「快速換證」流程，造成更新作業人工成本高。

**Solution**:  
• 在 License Payload 與 API Key Payload 內加入 `exp` (expiration) 欄位並簽章保護。  
• 系統開機或定期 Job 皆呼叫 `LicenseProvider.Validate()`；若當前時間 > exp，立即停用授權。  
• 更新流程：原廠重新簽發新 Token，客戶匯入即可；無需重啟整個系統，降低維運成本。

---

## Problem: 需抵禦熟悉程式架構的工程師的惡意操作

**Problem**:  
攻擊者等級提升到「懂程式、懂設定檔」的系統整合工程師，故安全機制必須達到業界可接受的強度（保護私鑰、抗竄改、抗重放）。

**Root Cause**:  
• 自行設計或自行實作的加解密演算法常有漏洞。  
• 私鑰散落開發或測試環境，易被複製。  
• 無版本化或金鑰輪替機制，攻擊面持續擴大。

**Solution**:  
• 僅使用業界標準演算法：RSA/ECDSA 簽章、AES-256 對稱加密。  
• 私鑰存放於 HSM / KMS；建置 CI/CD 時以簽名服務注入，不落地。  
• 加入 Key Version 與 Token ID；系統可拒絕過期或重複使用的 Token，減少重放風險。

---

## Problem: 機制需易於擴充並提供良好的 Developer Experience (DX)

**Problem**:  
未來會持續新增服務／功能模組，開發者應能直接沿用同一套授權基底，而不須重新實作加解密細節。

**Root Cause**:  
• 過往安全驗證邏輯散落於各服務，沒有統一的 SDK / Library。  
• 缺少物件導向封裝，導致複製貼上、難以維護。  
• DX 不佳 → 開發者容易繞過或錯誤使用安全機制。

**Solution**:  
• 提供集中式 `LicenseSDK`：  
  - `LicenseProvider`：讀取/驗證 License 檔。  
  - `ApiKeyValidator`：驗證來自外部呼叫之 Token。  
  - `FeatureGate`：以 AOP / Attribute 方式標示受保護的 API, 例如：  

    ```csharp
    [FeatureGate("Reporting")]
    public IActionResult GetReport() { ... }
    ```  
• 透過 NuGet 發佈並版本化；文件示範 DX 使用情境，降低誤用率。  
• 新服務只需引入 SDK、標示 Feature 名稱，即可取得同等防護與授權流程。

---

（本篇為「需求與問題」；具體實作細節將於系列文 #2「授權碼序列化」、#3「數位簽章」及「金鑰保護」中逐步說明。）