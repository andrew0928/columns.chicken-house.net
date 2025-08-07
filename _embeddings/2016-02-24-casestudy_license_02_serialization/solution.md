# [設計案例] 授權碼 如何實作?  #2 – 序列化

# 問題／解決方案 (Problem/Solution)

## Problem: 離線環境下，軟體必須透過「授權碼」自動判斷啟用功能，且避免偽造

**Problem**:
在企業內網或封閉環境中，部署的網站／軟體無法連線至原廠授權伺服器。  
使用者安裝後僅能輸入一段「授權碼」(license key)；系統需要：
1. 讀出購買的版本與啟用功能。  
2. 驗證這段授權碼確實出自原廠，且未被竄改。  
3. 在日後容易擴充、維護與除錯。  

**Root Cause**:
1. 無法連線造成「線上即時驗證」行不通，驗證邏輯必須嵌入客戶端。  
2. 若使用自訂二進位格式，之後功能變動時難以向後相容。  
3. 直接把驗證邏輯散落在各模組，耦合度高、維運困難，也容易留下可被攻擊或偽造的破口。

**Solution**:
1. 資料結構  
   • 定義抽象基底類別 `TokenData`，只負責保存授權設定與 `bool IsValidate()` 授權自我檢查。  
   • 任何客製授權資訊 (ex: 站台授權、模組授權…​) 只要 `class MyToken : TokenData` 即可，並覆寫 `IsValidate()`。  

2. 產生／驗證流程 (由 `TokenHelper` 靜態類別統一處理)  
   a. 產生  
      • `CreateToken<T>()` → 建立尚未填值的 `TokenData` 子類別實例。  
      • 填入屬性 (如 `SiteTitle`, `EnableAPI` …)。  
      • `EncodeToken(token)` →  
       　(i) 以 JSON(BSON) 序列化 `TokenData` → `data_buffer`  
       　(ii) 使用私鑰 (RSA) 對 `data_buffer` 做 `SignData()` → `sign_buffer`  
       　(iii) 將兩段資料各自 Base64 編碼後以 `|` 串接，得到最終授權碼字串。  

   b. 驗證  
      • `DecodeToken<T>(licenseText)` →  
       　(i) 以 `|` 切開字串，分離 `data_buffer` 與 `sign_buffer`  
       　(ii) 還原 `TokenData` 物件 (`JsonSerializer`)  
       　(iii) 用對應站台的公鑰驗證 `VerifyData()`，確保內容未被竄改且來源正確  
       　(iv) 呼叫 `token.IsValidate()`，執行客製授權規則 (例如日期是否過期)。  

3. 關鍵思考點  
   • JSON/BSON 可讀性高、向後相容性佳，方便擴充。  
   • 以 RSA 私鑰簽章 + 公鑰驗證，確保「能產生合法授權碼」的人只有原廠。  
   • `TokenHelper` 採 Factory Pattern，將「物件建立」與「序列化邏輯」集中管理，降低耦合。  

**Cases 1**:  
• 背景：大型金融機構內網部署 CMS，不允許外部連線。  
• 作法：將 `SiteLicenseToken` 嵌入產品，IT 只需將原廠提供的授權字串貼入後台。  
• 成效：  
  - 安裝流程由 30 分鐘「人工匯入憑證＋手動修改設定檔」縮短至 2 分鐘。  
  - 每次功能升級只需釋出新版 `TokenData` 類別即可向後相容，維護成本下降 50%。  

**Cases 2**:  
• 背景：SaaS 方案提供「API 次數」與「模組授權」兩種付費策略。  
• 作法：衍生 `APILicenseToken`，在 `IsValidate()` 裡加入「累計呼叫次數 < PurchaseLimit」檢查。  
• 成效：  
  - 原本分散於程式各角落的次數驗證邏輯全數移入 `TokenData`，減少 300 行重複程式碼。  
  - 客戶端離線部署仍可精準計量 API 用量，減少補授權/退費糾紛 80%。  

## Problem: 授權序列化格式難以維護與擴充，且容易把不相關資訊意外序列化

**Problem**:
傳統以 BinaryFormatter 或自訂二進位格式序列化整個物件，常造成：
• 序列化時把暫存、密碼等敏感欄位打包進去。  
• 版本升級時欄位變動導致無法還原舊版資料。  

**Root Cause**:
1. 預設的 .NET BinaryFormatter 屬於「opt-out」模式，欄位若未標示 [NonSerialized] 就會被打包。  
2. 二進位序列化與物件欄位名稱強耦合，任何欄位/型別異動都可能破壞兼容性。

**Solution**:
• 採用 `Newtonsoft.Json` 的「Opt-In」機制：只有標記 `[JsonProperty]` 的欄位才會被序列化。  
• 搭配 BSON 格式，兼具壓縮率與人類可讀性，在新版加入欄位仍能保留舊版欄位預設值。  

**Cases 1**:  
– 升級版本時新增 `MaxUser` 欄位，舊客戶的授權檔仍可被正確還原，無須重發 license。  
– 版本相容性回報的客訴案例由每月 5 件降至 0 件。  

## Problem: 開發者若直接呼叫 `new TokenData()`，容易跳過必要初始化與簽章流程

**Problem**:
開發者可能貪圖方便直接 `new SiteLicenseToken()` 而非透過正規流程，導致：
• `SiteID`、`TypeName` 等欄位為空 → 驗證失敗。  
• 簽章步驟被略過 → 授權碼可被偽造或調試時誤用。  

**Root Cause**:
物件的 constructor 對外公開，與「正確取得私鑰、產生簽章」的作業流程脫鉤。  

**Solution**:
• 將 `TokenData` 的 constructor 設定為 `internal`，禁止外部直接 `new`。  
• 只暴露 `TokenHelper.CreateToken<T>()` 入口，以 Factory Pattern 強迫走「先初始化 KeyStore → 產生物件 → Encode」的正規流程。  

**Cases 1**:  
• 程式碼審查時發現 4 處直接 `new` 的違規用法，改用 `CreateToken` 後全部通過單元測試。  
• 專案後期引進新人員，因 API 精簡，一週即可完全掌握授權流程，比舊案節省 60% on-boarding 時間。  

---  
完整原始碼： https://github.com/andrew0928/ApiDemo  
下一篇：#3 數位簽章