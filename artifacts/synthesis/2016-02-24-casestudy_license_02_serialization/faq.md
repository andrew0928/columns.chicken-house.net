# [設計案例] 授權碼 如何實作? #2, 序列化

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是離線授權碼？
- A簡: 離線授權碼是一段可攜帶的編碼字串，含授權資料與簽章，讓系統在無網路狀態驗證來源並啟用功能。
- A詳: 離線授權碼是一段可複製的字串，內含兩部分：授權設定的序列化資料與對該資料的數位簽章。其目的是在無需連網的環境，透過驗章確認資料來源未被偽造，並讀取其中的功能開關、授權效期等設定，以決定系統啟用哪些特性。此設計強調資料結構清楚、易擴充，同時具備足夠的完整性與來源驗證能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q2, B-Q5

A-Q2: 授權碼包含哪些核心部分？
- A簡: 授權碼由序列化的授權資料與其數位簽章組成，以分隔符連接後整體以 Base64 表示。
- A詳: 授權碼由「資料」與「簽章」兩部分構成。資料段是將授權物件 TokenData 以 JSON/BSON 方式序列化後的二進位再 Base64 化；簽章段則是使用私鑰對資料段進行簽章，產生不可偽造的數位指紋。兩段以不屬於 Base64 字元集合的分隔符（如 |）連接，形成單一可傳遞字串。解碼時先拆分，再驗證與還原。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1, B-Q2

A-Q3: 為什麼授權內容可公開但仍需驗證來源？
- A簡: 授權內容非機密，但須確保來源真實與資料未被竄改，數位簽章提供此保障。
- A詳: 授權內容（如功能開關、效期）本身可公開，重點在「信任」。若無來源驗證，攻擊者可竄改內容（如延長效期）。數位簽章用私鑰對資料計算簽章，驗證方以公鑰驗章，能確認資料確由原廠簽發且未被更動。此模型將「機密性」與「完整性/來源」分離，符合離線場景的實際需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q5, B-Q16

A-Q4: 什麼是序列化？本案採用什麼格式？
- A簡: 序列化是將物件轉為可儲存傳輸的資料，本案採 JSON 模型並以 BSON 輸出為二進位。
- A詳: 序列化是把物件狀態（欄位）轉成資料表示（字串或位元組），便於儲存與傳輸。本案以 Newtonsoft.Json 的序列化能力，採 JSON 模型對欄位進行控制（以 [JsonProperty] 標註），實際輸出使用 BSON（二進位 JSON）寫入記憶體串流，再 Base64 編碼，兼具清晰資料結構與緊湊載荷，利於跨平台解析與後續驗章。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q3, B-Q15

A-Q5: JSON 與 BSON 在本文中的角色與差異？
- A簡: JSON提供欄位控制與語意，BSON作為二進位承載更緊湊，兩者以同一序列化框架協同。
- A詳: 本文以 Newtonsoft.Json 提供的 JSON 序列化模型管理欄位與相容性（[JsonProperty] opt-in）。為了便於打包與傳遞，實際輸出採 BSON（二進位 JSON）寫入 MemoryStream，再轉 Base64。JSON 重可讀性與語意一致性；BSON 重緊湊與高效載入。兩者相輔相成，既易於擴充，也適合作為簽章的輸入位元組。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q3, B-Q14

A-Q6: TokenData 是什麼？核心責任為何？
- A簡: TokenData 是授權資料的抽象基底，定義欄位與驗證接口，供自訂授權模型繼承。
- A詳: TokenData 為抽象基底類別，封裝授權資料的核心欄位（如 SiteID、TypeName），並提供可覆寫的 IsValidate() 以實作授權邏輯（如效期檢查）。任何自訂授權型別（例如網站授權）皆繼承之，並以 [JsonProperty] 控制序列化欄位。此設計將資料結構與驗證行為聚焦於同一抽象，利於擴充與維護。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q9, B-Q4

A-Q7: TokenHelper 是什麼？提供哪些介面？
- A簡: TokenHelper 是負責建立、編碼、解碼授權的靜態工廠輔助類別，集中處理簽章與序列化。
- A詳: TokenHelper 是 static 類別，提供 Init（金鑰存放初始化）、CreateToken<T>（以工廠模式生成 Token）、EncodeToken（序列化+簽章）、DecodeToken（解包+驗章+反序列化）。它將金鑰、簽章、序列化等橫切關注集中，讓 TokenData 專注於資料與邏輯。此分工提升測試性與安全邏輯的一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q1, B-Q2, B-Q12

A-Q8: 為何要用 Factory 模式建立 Token？
- A簡: 工廠集中控制 Token 初始化與組態，避免分散 new，便於一致性與封裝安全。
- A詳: 以 TokenHelper.CreateToken<T>() 取代直接 new，可在建立時統一填入 SiteID、TypeName 等欄位，並將金鑰依賴、組態載入與生命週期控制集中。這降低外部誤用風險，維持建構前置條件一致，也為後續加入審計或版本控制預留掛點，是典型工廠方法的好處。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q12

A-Q9: 什麼是 IsValidate？何時會被呼叫？
- A簡: IsValidate 為授權邏輯檢查接口，反序列化後自動執行，用以驗證資料語意正確性。
- A詳: IsValidate() 是 TokenData 可覆寫方法，用於檢查授權語意，如效期、配額等。解碼流程中，資料反序列化為具體 Token 後即呼叫它，以回報語意層的有效性（例如未過期）。此檢查與簽章驗證互補：前者驗資料內容合法，後者保證來源與完整性，兩者須同時通過。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q4

A-Q10: SiteID 的意義與用途？
- A簡: SiteID 識別授權目標站台，亦用於選擇對應公鑰以完成驗章與金鑰路由。
- A詳: SiteID 是授權目標的唯一識別，用於區分不同部署或客戶。驗章時，系統依 Token.SiteID 從公鑰存放區查找對應公鑰，完成 VerifyData。產生授權時，亦會將當前 SiteID 嵌入 Token，形成完整憑證鏈。若找不到對應 SiteID，驗章必然失敗，避免跨站偽用。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q5

A-Q11: TypeName 欄位的目的？
- A簡: TypeName 紀錄具體類別名稱，解碼時比對型別，防止類型混淆與還原錯誤。
- A詳: TokenData 會記錄衍生類別的完整型別名稱至 TypeName。反序列化後，IsValidate 會檢查當前物件型別與 TypeName 一致，避免攻擊者構造不同的型別或利用型別不符造成語意混淆。此步驟屬於資料語意防護，與簽章完整性檢查共同提升安全性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7

A-Q12: 為何採用 [JsonProperty] 明確標註？
- A簡: 採 Opt-In 僅序列化標註欄位，避免漏出多餘內部狀態，強化資料最小暴露。
- A詳: 以 [JsonObject(MemberSerialization.OptIn)] 配合 [JsonProperty]，只有顯式標註的欄位才會被序列化。好處是控制輸出契約，避免意外將內部欄位、暫存狀態或安全敏感資料寫入授權碼，造成相容或安全問題。此策略也讓版本演進更可控。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q15

A-Q13: 什麼是金鑰存放區 Key Store？
- A簡: 金鑰存放區保存各站台所需公私鑰，供產生簽章與驗章時查找與使用。
- A詳: Key Store 是保存 RSA 金鑰的資料庫或檔案集合。產生授權需私鑰簽章，驗證授權需公鑰驗章；兩者依 SiteID 路由至正確金鑰。系統啟動時以 TokenHelper.Init 指定私鑰檔與公鑰目錄，建構金鑰快取以供後續 Encode/Decode 使用。妥善管理是安全的基石。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q11, D-Q2

A-Q14: 為什麼使用 Base64 與 '|' 分隔？
- A簡: Base64 可攜帶二進位，'|' 不在其字元集合內，做分隔避免內容衝突。
- A詳: 授權碼需以純文字安全傳遞二進位資料，採 Base64 編碼。Base64 僅使用 64 種字元與 '=' 補位，故選擇不在集合中的 '|' 作為資料與簽章的分隔符，可避免解析歧義。此簡單規格便於穩定拆分與跨通道傳遞（如剪貼、配置）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q14, D-Q7

A-Q15: 驗證來源與保密加密的差異？
- A簡: 本案重點在完整性與來源驗證（簽章），非對內容加密保密，兩者目標不同。
- A詳: 數位簽章確保資料未被竄改且來自持有私鑰的原廠；而加密則是隱藏內容避免他人讀取。本案授權內容可公開，故不需加密；但必須驗章以防偽造與篡改。若同時要保密，可再加入對稱加密，但將增加金鑰分發與相容性成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q5, D-Q2

A-Q16: 範例 SiteLicenseToken 代表什麼授權？
- A簡: SiteLicenseToken 表示網站授權，含標題、API 開關、起迄效期等設定並內建效期驗證。
- A詳: SiteLicenseToken 繼承 TokenData，定義網站層級的授權欄位：SiteTitle、EnableAPI、LicenseStartDate、LicenseEndDate。覆寫 IsValidate 檢查現在時間介於起訖間，並沿用基底型別一致性驗證。此範例展示如何以最少步驟自訂授權模型且即插即用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q1


### Q&A 類別 B: 技術原理類

B-Q1: EncodeToken 的流程如何運作？
- A簡: 先以 BSON 序列化資料，再用私鑰簽章，最後兩段各自 Base64 後以 '|' 串接。
- A詳: EncodeToken 先以 JsonSerializer 與 BsonWriter 將 TokenData 寫入 MemoryStream，取得 data_buffer。接著以 RSA 的 SignData 與指定雜湊演算法（_HALG）對 data_buffer 簽章，得 sign_buffer。最後將兩者分別 Base64，使用分隔符 '|' 連接，形成單一授權碼字串。此流程確保內容可復原且不可偽造。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, C-Q3

B-Q2: DecodeToken 的流程與關鍵檢查？
- A簡: 先拆分並 Base64 還原，再反序列化物件，執行 IsValidate，最後以公鑰驗章確保完整性。
- A詳: DecodeToken 先以分隔符拆兩段，分別 Base64 解碼為 data/sign 位元組。以 BsonReader 與 JsonSerializer 反序列化 data 成具體 Token 型別，呼叫 IsValidate 檢查語意。再依 Token.SiteID 自 Key Store 取公鑰，VerifyData 驗證簽章。任一環節失敗即拋出對應例外，避免使用不可信資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, C-Q4

B-Q3: 怎麼用 Newtonsoft.Json 做 BSON 序列化？
- A簡: 以 MemoryStream 配合 BsonWriter/Reader 與 JsonSerializer，即可輸出入二進位 BSON。
- A詳: 建立 MemoryStream，序列化時以 BsonWriter 包裹串流，JsonSerializer.Serialize 寫入；反序列化時則以 BsonReader 包裹資料串流，JsonSerializer.Deserialize<T> 還原。BSON 維持 JSON 結構語意，且輸出為緊湊位元組，利於後續 Base64 與簽章操作。同時可透過 [JsonProperty] 精準控制欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, C-Q8

B-Q4: 反序列化後如何自動觸發驗證？
- A簡: 反序列化成具體 Token 型別後呼叫多形 IsValidate，執行各型別自訂語意檢查。
- A詳: TryDecode 過程中，JsonSerializer 會依泛型參數 T 產生具體物件。完成後立即呼叫 token.IsValidate()，由各衍生型別實作其規則（如效期、配額）。此多形機制讓驗證邏輯與資料模型同聚合，避免外部忘記檢查，並提升擴充型別的可測試性與一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, D-Q4

B-Q5: RSA 簽章/驗章在流程中的位置？
- A簡: 簽章在序列化後，驗章在反序列化前檢核，以保障資料完整性與來源真實。
- A詳: 先序列化 TokenData 得到確定位元組序列，再以私鑰對該位元組簽章。驗證時，先取得位元組資料，依 SiteID 取公鑰驗章。通過後才信任還原的物件與其語意檢查結果。此順序確保任何位元組變動都會導致驗章失敗，從而無法繞過來源驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q15, D-Q2

B-Q6: 字串格式設計如何確保可解析？
- A簡: 採定長字元集合 Base64 並用集合外分隔符，拆分後再按固定順序處理兩段。
- A詳: Base64 僅含英數與 + /，以及 '=' 補位。選擇 '|' 作為不衝突的分隔符，保證拆分穩定。解析流程固定：split → Base64 decode → 反序列化/驗章。規格簡單、降風險、易除錯，也降低跨語言實作的成本，提升可移植性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, D-Q1

B-Q7: TypeName 比對如何預防型別偽造？
- A簡: 反序列化後比對物件實際型別全名與 TypeName，一致才視為合法資料。
- A詳: 攻擊者可能嘗試用相同欄位但不同語意的型別來混淆流程。將 TypeName 寫入資料，還原後檢查 this.GetType().FullName == TypeName，能阻斷型別替換攻擊與錯誤還原，確保資料「語意契約」不被破壞。此為語意層的補強。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, D-Q3

B-Q8: Init 初始化要做哪些事？
- A簡: 設定目前 SiteID、載入私鑰檔、載入公鑰目錄建快取，為簽章與驗章作準備。
- A詳: TokenHelper.Init(currentSiteId, privateKeyPath, publicKeyDir) 會記錄當前站台識別，載入 RSA 私鑰供 SignData 使用，並掃描公鑰存放建立以 SiteID 為鍵的字典快取，用於 VerifyData。未正確初始化將無法產生或驗證授權碼，屬系統啟動關鍵步驟。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q2

B-Q9: 泛型約束 T: TokenData, new() 的用意？
- A簡: 限制只接受 TokenData 衍生型別，且可由工廠建立實例，保障型別正確性。
- A詳: CreateToken<T>() 與 DecodeToken<T>() 以 where T : TokenData, new() 限定 T 必為授權模型且可建立無參數實例。此設計在編譯期防錯，確保流程中可安全初始化與還原，並且能呼叫 TokenData 定義的共同介面（如 IsValidate）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q1

B-Q10: internal setter/constructor 的封裝意義？
- A簡: 限制外部隨意變更關鍵欄位或基底建立，搭配工廠維持不變式與安全。
- A詳: TokenData 的關鍵屬性（SiteID、TypeName）使用 internal set，避免外部在建立後任意修改；基底可限制直接建構，引導透過工廠建立並自動填入必要欄位。此封裝強化不變式控制，降低誤用與被動注入風險。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q6, A-Q7

B-Q11: 多站台金鑰查找與 SiteID 的關係？
- A簡: 以 SiteID 作為公鑰字典鍵，驗章時據此選擇正確公鑰，避免跨站冒用。
- A詳: 驗章流程依 Token.SiteID 到 _PublicKeyStoreDict 查找對應公鑰，若不存在則拋 TokenSiteNotExistException。此設計支持多租戶或多環境金鑰隔離，確保授權只對應其所屬站台，避免跨站台移植授權碼而仍可驗過的風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, D-Q5

B-Q12: 為什麼選用 static TokenHelper？
- A簡: 將簽章、序列化與金鑰快取集中於單一服務入口，易於一致性與全域初始化。
- A詳: static 類別便於全域初始化（Init）與集中管理金鑰、雜湊、分隔符等設定，避免多處實例狀態不同步。也利於提供一致的 Encode/Decode API，降低使用門檻。不過需注意執行緒安全與測試隔離（可用包裝介面或 DI 進一步抽象）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q7, C-Q5

B-Q13: TokenException 類別在錯誤流程中扮演角色？
- A簡: 代表授權相關錯誤，如格式錯、站台不存在、驗章失敗，用於中斷流程與告警。
- A詳: 解碼與驗章過程中，若拆分錯誤、Base64 無效、SiteID 未註冊、簽章驗證失敗或反序列化異常，會拋出對應 TokenException（含子類 TokenFormatException、TokenSiteNotExistException）。呼叫端應捕捉並回報，避免使用不可信授權，並可記錄審計。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q2, D-Q3

B-Q14: Base64 的 65 字元集合與分隔符選擇原理？
- A簡: Base64 僅用英數與 +/ 及 '=' 補位，選其外字元（如 '|'）做分隔最穩妥。
- A詳: Base64 會將每 3 bytes 編成 4 個可列印字元，只使用 26 大寫、26 小寫、10 數字、+、/ 與 '=' 補位。分隔符應選不在集合內且易於輸入的符號（如 '|'），以確保拆分可靠並降低通道轉碼風險。此原理支撐本文的打包/拆包設計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, D-Q7

B-Q15: 序列化欄位選擇策略與相容性？
- A簡: 採 Opt-In 僅輸出必要欄位，新增欄位向後相容，減少破壞性變更。
- A詳: 以 [JsonProperty] 控制輸出契約，新增欄位預設不影響舊端解析；舊端忽略未知欄位仍可工作。移除或更名欄位需謹慎，建議保留兼容映射。此策略兼顧演進與穩定，適合長期維護的授權模型。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, C-Q7

B-Q16: 如何防止他人偽造授權碼？
- A簡: 產生簽章需私鑰，驗章用公開公鑰；無私鑰者無法產生可驗過的授權。
- A詳: 授權碼的不可偽造性依賴私鑰僅在原廠掌握。EncodeToken 用私鑰 SignData；任何未持有私鑰者無法產生對應簽章。驗章端僅需公鑰即可 VerifyData。只要私鑰不外流，竄改資料或自造授權都會驗章失敗，因此攻擊無法成功。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何實作自訂 TokenData（如加入人數上限）？
- A簡: 繼承 TokenData，為欄位加上 [JsonProperty]，覆寫 IsValidate 實作邏輯。
- A詳: 具體實作步驟
  - 建類別 class MyToken : TokenData。
  - 為新欄位加 [JsonProperty]（如 int MaxUsers）。
  - 覆寫 IsValidate 檢查效期與 MaxUsers > 0，再呼叫 base.IsValidate()。
  關鍵程式碼
  - public override bool IsValidate(){ if(MaxUsers<=0) return false; return base.IsValidate(); }
  注意事項
  - 僅標註必要欄位；避免敏感資料序列化；確保無參數建構子可用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q3, B-Q9

C-Q2: 如何初始化 TokenHelper 與金鑰存放區？
- A簡: 啟動時呼叫 Init，傳入 SiteID、私鑰檔路徑與公鑰目錄，建立金鑰快取。
- A詳: 具體實作步驟
  - 在應用啟動（如 Main 或 Web 啟動）呼叫 TokenHelper.Init("GLOBAL", @"D:\KEYDIR\_PRIVATE\GLOBAL.xml", @"D:\KEYDIR").
  關鍵程式碼片段
  - TokenHelper.Init("GLOBAL", @"D:\KEYDIR\_PRIVATE\GLOBAL.xml", @"D:\KEYDIR");
  注意事項
  - 私鑰檔限權限、不可隨部署對外散布；公鑰可隨站台更新；異常時應中止啟動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, A-Q13

C-Q3: 如何產生授權碼（編碼＋簽章）？
- A簡: 以 CreateToken 建立實例、填入欄位，呼叫 EncodeToken 取得授權碼字串。
- A詳: 具體實作步驟
  - var t = TokenHelper.CreateToken<SiteLicenseToken>();
  - 設定 t.SiteTitle/EnableAPI/LicenseStartDate/LicenseEndDate。
  - var text = TokenHelper.EncodeToken(t);
  關鍵程式碼
  - var t = TokenHelper.CreateToken<SiteLicenseToken>(); var s = TokenHelper.EncodeToken(t);
  注意事項
  - 必須已 Init 並可讀私鑰；填完欄位再編碼；避免在非受控環境保存私鑰。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q5

C-Q4: 如何驗證授權碼並讀取授權資訊？
- A簡: 呼叫 DecodeToken 驗章與反序列化，捕捉例外；成功後直接讀取欄位使用。
- A詳: 具體實作步驟
  - var token = TokenHelper.DecodeToken<SiteLicenseToken>(text);
  - 使用 token.SiteID/SiteTitle/EnableAPI 等。
  關鍵程式碼
  - try { var t=TokenHelper.DecodeToken<SiteLicenseToken>(text); } catch(TokenException) {}
  注意事項
  - 先 Init；驗章失敗會丟 TokenException；解後仍檢查 t.IsValidate 結果或效期。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, D-Q2

C-Q5: 如何在網站啟動時自動載入與檢驗授權？
- A簡: 於應用啟動初始化金鑰並嘗試 Decode，失敗中止啟動或降級功能。
- A詳: 具體實作步驟
  - Global/Startup 中呼叫 TokenHelper.Init(...)。
  - 從設定來源讀入授權碼字串，DecodeToken。
  - 將授權結果緩存於記憶體供全站使用。
  關鍵程式碼
  - var token = TokenHelper.DecodeToken<SiteLicenseToken>(licenseText);
  注意事項
  - 啟動即驗章；失敗採 fail-fast；避免每請求重複驗章，採快取配合變更通知。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12

C-Q6: 如何記錄驗證結果與審計事件？
- A簡: 捕捉 TokenException 與驗證結果，記錄站台、原因、時間與授權摘要。
- A詳: 具體實作步驟
  - try/catch 包裹 Decode，於 catch 記錄例外類型與訊息。
  - 成功時記錄 SiteID、TypeName、效期區間與雜湊摘要。
  關鍵程式碼
  - catch(TokenException ex){ logger.Warn(ex,...); }
  注意事項
  - 日誌不可落地私鑰或完整授權碼；可記錄部分遮罩；配合告警與運維流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13

C-Q7: 如何為既有 Token 新增欄位並保持相容？
- A簡: 使用 [JsonProperty] 新增欄位，給預設值；舊版本忽略未知欄位即可。
- A詳: 具體實作步驟
  - 於 Token 類別新增 [JsonProperty] 欄位（如 int FeatureLevel）。
  - IsValidate 中為 null/預設情況給合理 fallback。
  關鍵程式碼
  - [JsonProperty] public int FeatureLevel {get;set;} = 1;
  注意事項
  - 避免重命名或移除既有欄位；必要時保留兼容映射；更新文件與測試樣本。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15

C-Q8: 如何切換輸出純 JSON 而非 BSON（若需人讀）？
- A簡: 以 JsonTextWriter 寫入字串，再轉 Base64；但載荷較大、易被誤改。
- A詳: 具體實作步驟
  - 使用 StringWriter + JsonTextWriter，JsonSerializer.Serialize 寫入字串。
  - Encoding.UTF8.GetBytes(json) → Base64 → 照樣簽章/打包。
  關鍵程式碼
  - var sw=new StringWriter(); var jw=new JsonTextWriter(sw); js.Serialize(jw, token);
  注意事項
  - 可讀性↑但長度↑；仍必須簽章；注意換行/空白不可變更，否則驗章失敗。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q6

C-Q9: 如何安全管理私鑰檔？
- A簡: 私鑰僅存於原廠安全環境，部署端僅有公鑰；限制檔案權限與存取審計。
- A詳: 具體實作步驟
  - 私鑰置於受保護伺服器或 HSM，簽章服務離線或最小暴露。
  - 部署站台只配置公鑰目錄。
  關鍵設定
  - 檔案 ACL 最小化、免備份外帶；版本輪替與吊銷機制。
  注意事項
  - 絕不將私鑰隨程式散布；定期審計與輪換；測試用與正式用密鑰分離。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q16

C-Q10: 如何支援多站台授權與金鑰？
- A簡: 以 SiteID 為鍵配置多把公鑰，授權內含 SiteID，驗章時據此路由。
- A詳: 具體實作步驟
  - 公鑰目錄下以 SiteID 命名或索引。
  - 產生授權時設定 token.SiteID 為目標站台。
  關鍵程式碼
  - _PublicKeyStoreDict[siteId].VerifyData(...)
  注意事項
  - 確保 SiteID 唯一；避免跨站台複用私鑰；在移轉或分拆時同步更新公鑰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 TokenFormatException 怎麼辦？
- A簡: 代表格式或拆分/解碼錯誤，檢查分隔、Base64、資料長度與傳輸是否破損。
- A詳: 問題症狀
  - Split 得到的段數錯誤或 Base64 轉位元組拋例外。
  可能原因
  - 分隔符被更動、貼上時被換行/轉碼、字串截斷。
  解決步驟
  - 驗證含 '|' 並恰兩段；檢查 Base64 是否有效；確保未經 URL/HTML 轉碼。
  預防措施
  - 使用固定傳輸管道；必要時封裝為檔案；在 UI 上加入格式檢測。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q13

D-Q2: 驗章失敗（來源不可信）如何排查？
- A簡: 檢查公鑰是否匹配 SiteID、資料是否被改、私鑰是否錯用、雜湊演算法一致。
- A詳: 症狀
  - VerifyData 回傳 false 或丟出驗章相關例外。
  可能原因
  - SiteID 不存在/公鑰錯；授權遭改動；產生端用錯私鑰或 _HALG。
  解決步驟
  - 確認 Init 目錄與 SiteID；重新取得授權碼；確保簽章環境一致。
  預防
  - 嚴管私鑰；簽章服務固定化；在日誌中記錄 SiteID 與金鑰版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q16

D-Q3: 反序列化後得到 null 或型別不符？
- A簡: 可能欄位未標註、JSON 結構不符、TypeName 不一致，需檢查模型與資料契約。
- A詳: 症狀
  - js.Deserialize<T>(...) 回傳 null 或 IsValidate 型別比對失敗。
  可能原因
  - 未加 [JsonProperty]；欄位重命名；TypeName 不匹配。
  解決步驟
  - 比對現行 Token 類別與舊資料欄位；保留相容欄位；修正 TypeName。
  預防
  - 採 Opt-In；版本控制；回溯測試樣本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q3, B-Q15

D-Q4: IsValidate 回傳 false 如何處理？
- A簡: 表示授權語意不成立，如未啟用或過期，應中止相關功能並提示使用者。
- A詳: 症狀
  - Decode 成功但 IsValidate 為 false。
  可能原因
  - 效期不符（未開始/已結束）、配額或條件不滿足。
  解決步驟
  - 檢視授權欄位；同步伺服器時間；更新授權。
  預防
  - 在授權發放側加入語意檢查；消費端啟動時先驗證與緩存結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9

D-Q5: TokenSiteNotExistException 代表什麼？
- A簡: 表示授權中的 SiteID 在公鑰存放區不存在，無法找到對應公鑰驗章。
- A詳: 症狀
  - 解碼過程拋 TokenSiteNotExistException。
  可能原因
  - 未部署該 SiteID 公鑰；SiteID 拼寫錯；環境錯置。
  解決步驟
  - 確認 Init 指向正確公鑰目錄；部署正確公鑰；校對 SiteID。
  預防
  - 公鑰與 SiteID 管理制度化；打包時自動檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, A-Q10

D-Q6: 時區或時間誤差導致誤判過期怎麼辦？
- A簡: 統一使用系統 UTC 或一致的本地時間來源，並於 IsValidate 容忍微小偏差。
- A詳: 症狀
  - 不同環境對效期判斷不一致。
  可能原因
  - 時區設定不同、NTP 不同步、DST 影響。
  解決步驟
  - 統一時間來源；IsValidate 使用 DateTime.UtcNow 或加入緩衝。
  預防
  - 部署前時間校準；文件化時間要求；在授權中明確時區語意。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16

D-Q7: 分隔符衝突或傳輸被轉碼如何處置？
- A簡: 使用不在 Base64 集合的分隔符；傳輸時避免轉碼，必要時使用封裝容器。
- A詳: 症狀
  - Split 得到錯誤段數；Base64 解碼失敗。
  可能原因
  - 分隔符被替換；URL/HTML 轉碼；換行插入。
  解決步驟
  - 僅接受 '|'；輸入做預檢；清理空白與換行。
  預防
  - 用檔案或 QR 封裝；通道明確標示不可轉碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, B-Q6

D-Q8: 版本升級新增欄位導致舊端失敗？
- A簡: 採 Opt-In 與相容策略，舊端忽略未知欄位；必要時保留映射與預設值。
- A詳: 症狀
  - 舊版反序列化失敗或語意判斷異常。
  可能原因
  - 欄位重命名/移除；預設值未處理。
  解決步驟
  - 恢復相容欄位；在 IsValidate 加預設；滾動升級雙向相容。
  預防
  - 訂版控規約；提供相容性測試集。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, C-Q7

D-Q9: static TokenHelper 的執行緒安全如何保證？
- A簡: Init 僅一次；金鑰快取唯讀；Encode/Decode 無共享可變狀態即為 thread-safe。
- A詳: 症狀
  - 併發下偶發錯誤或狀態競爭。
  可能原因
  - 重複初始化、共享暫存修改。
  解決步驟
  - 以一次性鎖定 Init；金鑰字典建後改為唯讀；避免靜態可變字段。
  預防
  - 啟動流程單執行緒；加入健康檢查。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12

D-Q10: 驗證效能不佳的原因與優化？
- A簡: 反序列化與驗章較耗時；可快取結果、減少重複驗章、優化序列化與金鑰存取。
- A詳: 症狀
  - 高頻驗證造成延遲。
  可能原因
  - 重複讀檔載鍵；每請求重簽章/驗章；BSON/JSON 轉換頻繁。
  解決步驟
  - 啟動時載入金鑰；結果快取（含 TTL）；僅在變更時重驗。
  預防
  - 批次驗證工具；監控與容量規劃；必要時使用硬體加速或非同步處理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q6, C-Q5


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是離線授權碼？
    - A-Q2: 授權碼包含哪些核心部分？
    - A-Q3: 為什麼授權內容可公開但仍需驗證來源？
    - A-Q4: 什麼是序列化？本案採用什麼格式？
    - A-Q6: TokenData 是什麼？核心責任為何？
    - A-Q7: TokenHelper 是什麼？提供哪些介面？
    - A-Q9: 什麼是 IsValidate？何時會被呼叫？
    - A-Q10: SiteID 的意義與用途？
    - A-Q11: TypeName 欄位的目的？
    - A-Q12: 為何採用 [JsonProperty] 明確標註？
    - A-Q14: 為什麼使用 Base64 與 '|' 分隔？
    - B-Q6: 字串格式設計如何確保可解析？
    - B-Q13: TokenException 類別在錯誤流程中扮演角色？
    - C-Q2: 如何初始化 TokenHelper 與金鑰存放區？
    - C-Q4: 如何驗證授權碼並讀取授權資訊？

- 中級者：建議學習哪 20 題
    - B-Q1: EncodeToken 的流程如何運作？
    - B-Q2: DecodeToken 的流程與關鍵檢查？
    - B-Q3: 怎麼用 Newtonsoft.Json 做 BSON 序列化？
    - B-Q4: 反序列化後如何自動觸發驗證？
    - B-Q5: RSA 簽章/驗章在流程中的位置？
    - B-Q7: TypeName 比對如何預防型別偽造？
    - B-Q8: Init 初始化要做哪些事？
    - B-Q9: 泛型約束 T: TokenData, new() 的用意？
    - B-Q11: 多站台金鑰查找與 SiteID 的關係？
    - B-Q12: 為什麼選用 static TokenHelper？
    - B-Q15: 序列化欄位選擇策略與相容性？
    - B-Q16: 如何防止他人偽造授權碼？
    - C-Q1: 如何實作自訂 TokenData（如加入人數上限）？
    - C-Q3: 如何產生授權碼（編碼＋簽章）？
    - C-Q5: 如何在網站啟動時自動載入與檢驗授權？
    - C-Q6: 如何記錄驗證結果與審計事件？
    - C-Q7: 如何為既有 Token 新增欄位並保持相容？
    - D-Q1: 遇到 TokenFormatException 怎麼辦？
    - D-Q2: 驗章失敗（來源不可信）如何排查？
    - D-Q3: 反序列化後得到 null 或型別不符？

- 高級者：建議關注哪 15 題
    - A-Q8: 為何要用 Factory 模式建立 Token？
    - A-Q15: 驗證來源與保密加密的差異？
    - B-Q10: internal setter/constructor 的封裝意義？
    - B-Q12: 為什麼選用 static TokenHelper？
    - C-Q8: 如何切換輸出純 JSON 而非 BSON（若需人讀）？
    - C-Q9: 如何安全管理私鑰檔？
    - C-Q10: 如何支援多站台授權與金鑰？
    - D-Q4: IsValidate 回傳 false 如何處理？
    - D-Q5: TokenSiteNotExistException 代表什麼？
    - D-Q6: 時區或時間誤差導致誤判過期怎麼辦？
    - D-Q7: 分隔符衝突或傳輸被轉碼如何處置？
    - D-Q8: 版本升級新增欄位導致舊端失敗？
    - D-Q9: static TokenHelper 的執行緒安全如何保證？
    - D-Q10: 驗證效能不佳的原因與優化？
    - B-Q14: Base64 的 65 字元集合與分隔符選擇原理？