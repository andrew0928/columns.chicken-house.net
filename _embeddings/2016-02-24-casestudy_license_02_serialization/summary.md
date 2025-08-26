# [設計案例] 授權碼 如何實作?  #2, 序列化

## 摘要提示
- 授權碼目標: 在離線情境下以一段授權資料同時攜帶功能設定並可驗證來源真偽。
- 設計拆分: 將問題分為資料封裝（序列化）與安全驗證（數位簽章）兩部分。
- TokenData: 抽象基底類別承載授權設定並提供 IsValidate 可覆寫以定義驗證邏輯。
- TokenHelper: 使用靜態工廠建立/編碼/解碼 Token，集中控制序列化與簽章流程。
- JSON/BSON 序列化: 以 Newtonsoft.Json 的 BSON 格式序列化，僅 [JsonProperty] 成員參與。
- 多形與驗證: 解碼後自動呼叫 IsValidate，讓各子類自訂過期、配額等驗證。
- 解碼流程: Base64 拆段→反序列化→IsValidate→以站台公鑰驗簽確認未被偽造。
- 編碼流程: 物件序列化→以私鑰簽章→兩段 Base64 用分隔字元 ‘|’ 打包成授權碼。
- 資料結構: Token 內含 SiteID 與 TypeName，確保類型一致與金鑰對應。
- 金鑰依賴: 產生簽章需私鑰、驗章需公鑰；初始化 keystore 是整體安全前提。

## 全文重點
本文聚焦「授權碼」在離線場景的資料封裝與驗證來源設計，目標是讓軟體不需上網便能從一段字串判定購買版本與可啟用功能，且避免被偽造。作者以兩類別協作達成：TokenData 負責描述授權內容與邏輯驗證；TokenHelper 則負責建立、編碼、解碼與簽章/驗章，採工廠模式集中外部操作介面。資料序列化選用 Newtonsoft.Json 的 BSON 格式，並以 [JsonProperty] 精準控制參與序列化的成員，避免多餘資訊外洩。

TokenData 定義 SiteID 與 TypeName 等共通欄位，並提供虛擬方法 IsValidate，子類可覆寫以加入如起訖日期、功能限制等驗證。示例 SiteLicenseToken 展示常見欄位（站台標題、API 開關、授權起迄）與過期判斷。TokenHelper 的 DecodeToken 流程為：以 ‘|’ 分隔取得兩段 Base64，前段為序列化後的 BSON，後段為其簽章；先反序列化為 Token 物件，呼叫 IsValidate 進行商業邏輯驗證，再依 SiteID 從 keystore 取對應公鑰進行簽章驗證，確保來源真實且資料未被竄改。成功則還原為原始 Token 類別供讀取。

產生授權碼則相反：CreateToken 建立具 SiteID/TypeName 的 Token 物件，填入設定後 EncodeToken 進行 BSON 序列化並以私鑰簽章，最後以 Base64 編碼後用 ‘|’ 串接為單一可發佈字串。作者解釋 BASE64 僅包含特定 65 個字元，因此選擇 ‘|’ 作為可靠不衝突的分隔符。安全關鍵在於 keystore 初始化：沒有私鑰無法生成有效簽章，防止他人僅憑類庫偽造授權；公鑰則用於驗章。數位簽章與金鑰管理細節將於下一篇展開。整體設計兼顧可擴充（自訂 TokenData 與驗證邏輯）、可維護（工廠封裝流程）與安全性（簽章驗證來源）。

## 段落重點
### 前言與系列脈絡
作者鎖定離線授權的典型需求：以一段「外星文」授權碼攜帶啟用資訊並可確認來源真偽，避免竄改與偽造；同時要求資料結構清楚易擴充、實作維護成本低。整體拆分為兩大面向：資料如何封裝（序列化）與如何保證其來源與完整性（數位簽章）。本文為系列第 2 篇，專注介紹序列化與授權碼打包方式，數位簽章與金鑰保護將於後續篇章補充。核心設計導入 TokenData 與 TokenHelper 兩類別：前者承載授權內容並可覆寫驗證邏輯，後者以靜態工廠統一負責建立、編碼、解碼及與簽章/驗章的協作，既切分責任也簡化使用體驗。

### 資料的封裝: 序列化
TokenData 與 TokenHelper 是兩大主角。TokenData 僅定義最小共通欄位（SiteID、TypeName）與可覆寫的 IsValidate 方法；TokenHelper 則提供 Init 與 Create/Encode/Decode 的靜態介面，採用類工廠模式將物件生成與序列化/簽章等細節外移集中管理。序列化格式選用 JSON 技術棧下的 BSON，以 Newtonsoft.Json 實現；為避免非必要資訊被轉出，要求欄位以 [JsonProperty] 明確標註才參與序列化。這樣的設計讓授權內容不是密文而是可公開資料，但完整性與來源真偽透過後續數位簽章把關。

### 自訂 TokenData: SiteLicenseToken
示例 SiteLicenseToken 繼承 TokenData，定義站台標題、API 啟用、授權起迄等欄位，並覆寫 IsValidate 實作「未到起始日或已過到期日即視為無效」的邏輯。自訂步驟僅三點：繼承基底類別、以 [JsonProperty] 標注所需欄位、覆寫 IsValidate。多形機制保證解碼後自動執行子類的驗證邏輯，讓各產品情境可靈活擴充如人數上限、模組白名單等規則，同時不影響外部使用方式。

### 驗證授權碼 (解碼 + 驗證)
使用端先以 TokenHelper.Init 設定 keystore 與當前 SiteID。DecodeToken 的流程為：以分隔字元 ‘|’ 分出資料與簽章兩段 Base64；將資料段解成位元組後以 BSON 反序列化還原為具體 Token 類型；立即呼叫 token.IsValidate 執行商業規則檢查；再依 token.SiteID 取對應公鑰驗證簽章，確保資料未被偽造且確實由原廠發出。若格式錯誤、站台不存在或驗章失敗將擲出對應例外。成功後即可直接讀取授權設定值。此流程同時處理資料有效性與來源完整性兩件事。

### 產生授權碼 (編碼 + 簽章)
建立流程分三步：CreateToken 生成具 SiteID 與 TypeName 的 TokenData；填入自訂設定；EncodeToken 進行序列化與簽章並打包字串。EncodeToken 會將物件以 BSON 序列化成 data_buffer，使用私鑰對該資料進行簽章得到 sign_buffer，兩者分別做 Base64 後以 ‘|’ 串接成授權碼。作者說明選 ‘|’ 作分隔的依據在於 BASE64 僅使用固定 65 字元集合，不會與 ‘|’ 衝突。安全性關鍵在 keystore：沒有原廠私鑰無法產生有效簽章，即使取得類庫也難以偽造；驗證端則以公鑰驗章。數位簽章與金鑰管理細節將在下一篇深入說明。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 物件導向基礎（繼承、覆寫、多型）
   - 序列化/反序列化（JSON/BSON 與屬性標註）
   - 數位簽章與公私鑰概念（RSA、雜湊演算法）
   - Base64 編碼與資料打包
   - .NET/C# 基本語法與例外處理

2. 核心概念：
   - TokenData：授權資料的抽象模型，負責攜帶授權設定與內部驗證（IsValidate）
   - TokenHelper：工廠/協助類別，集中處理 Init、Create、Encode、Decode 與簽章驗證
   - 序列化格式：使用 Newtonsoft.Json 的 BSON/JSON，僅序列化標注 [JsonProperty] 的欄位
   - 授權碼結構：Base64(data) | Base64(signature)，以自訂分隔符號組合
   - 安全信任鏈：以私鑰簽章、以對應站點 SiteID 的公鑰驗證，確保來源不可偽造
   彼此關係：TokenData 定義資料與驗證規則 → TokenHelper 以工廠方式建立/封裝 → 以 JSON/BSON 序列化後簽章 → 以 Base64 打包 → Decode 時先反序列化再驗簽與內部驗證。

3. 技術依賴：
   - Newtonsoft.Json（JsonSerializer、BsonReader/BsonWriter）
   - .NET 加密（RSACryptoServiceProvider.SignData/VerifyData，雜湊演算法 HALG）
   - Base64（Convert.ToBase64String / FromBase64String）
   - 金鑰儲存（Key Store：站點對應公鑰、原廠私鑰；Init 時載入）
   依賴關係：KeyStore 初始化 → CreateToken/Encode 需私鑰 → Encode 產出（序列化→簽章→打包）→ Decode（拆包→反序列化→IsValidate→公鑰驗簽）。

4. 應用場景：
   - 離線授權驗證（無網路環境下啟用功能）
   - 站點或產品版本功能開關（EnableAPI 等）
   - 時效性授權（開始/結束日期）
   - 可擴充的授權模型（不同產品線自訂 TokenData 派生類）

### 學習路徑建議
1. 入門者路徑：
   - 了解授權碼需求與目標（來源可驗、內容可讀、離線可用）
   - 熟悉 JSON/BSON 與 [JsonProperty] 序列化最小化策略
   - 先實作 SiteLicenseToken：欄位標註、覆寫 IsValidate（日期檢核）
   - 用 TokenHelper.DecodeToken 讀取範例字串並列印欄位

2. 進階者路徑：
   - 實作 TokenHelper.Create/Encode/Decode 全流程，觀察 Base64 打包格式與分隔字元
   - 加入例外情境處理（格式錯誤、站點不存在、公鑰不符、驗簽失敗）
   - 擴展 TokenData（加入人數上限、模組授權等），強化 IsValidate 規則
   - 了解工廠模式在建立與封裝中的角色，分離建構與初始化

3. 實戰路徑：
   - 設計 Key Store 格式與初始化流程（Init：載入私鑰/公鑰、指定 _CurrentSiteID）
   - 封裝發證（原廠）與驗證（客戶端）兩套流程與部署腳本
   - 規劃授權碼輪換、過期處理與審計日誌
   - 壓測與安全測試（篡改 data、錯誤 SiteID、公鑰缺失、重放等）

### 關鍵要點清單
- TokenData 抽象模型: 以抽象類別承載授權欄位與 IsValidate 的自訂驗證入口（多型） (優先級: 高)
- [JsonProperty] 最小序列化: 僅標注欄位會被序列化，降低洩漏風險與格式漂移 (優先級: 高)
- SiteID 與 TypeName: 內建欄位，綁定站點與型別一致性（TypeName 比對） (優先級: 高)
- IsValidate 規則覆寫: 於派生類定義業務驗證（如日期區間、人數上限） (優先級: 高)
- TokenHelper 工廠職責: 集中 Init/Create/Encode/Decode，解耦建構與序列化/簽章細節 (優先級: 高)
- 序列化為 BSON: 使用 Newtonsoft.Json 的 BsonWriter/Reader 優化體積與處理 (優先級: 中)
- Base64 打包格式: 將 data 與 signature 以 “|” 分隔的 Base64 串聯，易於傳輸 (優先級: 中)
- RSA 簽章與驗證: 私鑰簽章、以站點公鑰 VerifyData，確保來源與不可否認性 (優先級: 高)
- KeyStore 初始化: 在 Encode/Decode 前載入私鑰/公鑰並設定當前 SiteID (優先級: 高)
- 例外處理類型: TokenFormatException、TokenSiteNotExistException 等明確錯誤回報 (優先級: 中)
- 型別安全還原: 反序列化後自動呼叫 IsValidate，確保資料與規則同時被驗證 (優先級: 高)
- SplitChar 選擇: 使用 Base64 保證不出現的分隔字元（如“|”）避免解析歧義 (優先級: 低)
- Hash 演算法設定: 簽章時需一致 HALG 參數，否則驗簽失敗 (優先級: 中)
- 私鑰保護前提: 發證端必須持有私鑰；若無私鑰不可產生有效授權碼 (優先級: 高)
- 可擴充授權欄位: 透過繼承 TokenData 新增功能旗標/限制，維持介面穩定 (優先級: 中)