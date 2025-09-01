# [設計案例] 授權碼 如何實作? #3, 數位簽章

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是數位簽章？
- A簡: 數位簽章以公開演算法加私有金鑰驗證資料來源與完整性，確保未被竄改與不可否認。
- A詳: 數位簽章是一種基於非對稱式密碼學的驗證技術。簽署者用私鑰對資料的雜湊值進行簽署，驗證者用對應公鑰驗證簽章，藉此確認資料確實由持有私鑰者發出且傳輸過程未被修改。其特點是不可偽造、可驗證來源、具備完整性保障與不可否認性。常見應用包括軟體授權碼、文件簽署、API 消息簽章與更新包驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q7, B-Q1

A-Q2: 數位簽章與電子簽章有何差異？
- A簡: 電子簽章泛指電子形式之簽署，數位簽章是其實現方式之一，強調密碼學驗證。
- A詳: 電子簽章是法律與實務上對電子形式簽署的廣泛稱呼，用於辨識簽署人身分與意願。數位簽章則是以公私鑰與數學演算法實現電子簽章的一種技術手段，著重於透過雜湊與私鑰加密達成來源鑑別與完整性驗證。在法遵落地中，電子簽章可由數位簽章技術支撐其真偽驗證能力，但兩者範疇不同。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1

A-Q3: 為什麼授權碼需要數位簽章？
- A簡: 防止授權碼偽造與竄改，驗證確為原廠發出，保障功能啟用決策正確。
- A詳: 授權碼承載可啟用功能與期限等關鍵設定，若被偽造或竄改，將造成不當使用與資安風險。透過數位簽章，應用程式可以公鑰驗證該授權碼確為原廠持私鑰簽發、且內容未被修改，從而在啟動時放心依授權指示啟用功能。此作法降低序號外流、破解與回填無效資料的風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q5, D-Q2

A-Q4: 對稱式與非對稱式加密有何差異？
- A簡: 對稱用同一把金鑰加解密；非對稱用公鑰與私鑰成對，支援簽章與身分驗證。
- A詳: 對稱式加密（如 AES）使用同一把金鑰加解密，速度快但金鑰分發困難。非對稱式加密（如 RSA）使用公鑰/私鑰配對，公鑰可公開、私鑰需保密，適合用於密鑰交換、身份鑑別與數位簽章。數位簽章仰賴非對稱技術：用私鑰簽、用公鑰驗，兼顧可公開驗證與無須共享私密。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q6, B-Q12

A-Q5: 什麼是公鑰與私鑰？各自用途是什麼？
- A簡: 私鑰保密用於簽章或解密；公鑰公開用於驗章或加密，兩者成對對應。
- A詳: 在非對稱密碼學中，一組金鑰包含私鑰與公鑰。私鑰僅簽署者或接收方持有，用於資料簽章（或接收方解密）；公鑰可公開分發，供驗證簽章或向持私鑰者加密。安全性建立在私鑰不外流且難以由公鑰反推出私鑰。授權碼簽章即是以私鑰簽署、以公鑰驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q6

A-Q6: 什麼是 RSA？為何常用於簽章？
- A簡: RSA是非對稱演算法，基於大數因式分解困難，廣用於簽章與密鑰交換。
- A詳: RSA 依賴大質數因式分解困難性，生成公私鑰對。其數學特性讓以私鑰加密（簽章）之資料可被對應公鑰驗證，反之亦可進行加密傳遞。優點是標準成熟、工具與庫支援廣泛（如 .NET RSACryptoServiceProvider），易於與現有系統整合，故常用於軟體授權與檔案簽章。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q6

A-Q7: 什麼是 Hash（雜湊）？在簽章中扮演何角色？
- A簡: Hash將資料映射為固定長度摘要，供簽章與完整性驗證，常用 SHA-256。
- A詳: 雜湊函式將任意長度資料映射為固定長度的雜湊值，具抗碰撞與不可逆特性。在數位簽章中，先對原文計算雜湊，再以私鑰對雜湊簽署，驗證時重算雜湊並驗章對比，效率高且可檢知任何細微改動。文中使用 SHA256CryptoServiceProvider 作為雜湊演算法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q3

A-Q8: 為什麼不應自行發明加密演算法？
- A簡: 自製演算法缺乏公開審視，安全倚賴保密性，無法經得起開源與審核。
- A詳: 安全設計應遵循「演算法公開、金鑰保密」原則。自行發明的加密常倚賴「別人不知道細節」維持防護，一旦原始碼開放或團隊審查，即暴露風險；且缺乏密碼學社群長期驗證。採用公開成熟演算法與可靠函式庫，將安全性建立在金鑰管理與正確實作，才是上策。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q15

A-Q9: 公開演算法 + 私有金鑰的核心價值是什麼？
- A簡: 讓安全性建立在金鑰保護與數學強度，支持審核與開源而不犧牲安全。
- A詳: 公開演算法經社群長期驗證，安全性來自數學困難度；私有金鑰則是唯一的「秘密」。即便演算法與程式碼公開，攻擊者沒有私鑰依然難以偽造簽章或解密。此模式利於團隊協作、程式審核、開源與合規，也便於藉由 CA 分發與信任管理公鑰。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q10

A-Q10: 數位簽章能保障哪些安全性屬性？
- A簡: 來源鑑別、完整性、不可否認；不等同機密性，需配合加密另行實現。
- A詳: 數位簽章核心保障三項：來源鑑別（確知持私鑰者簽發）、完整性（任何改動可被偵測）、不可否認（簽署人事後無法否認）。但簽章不提供機密性，內容仍為明文可讀；若需保密，需另以加密搭配。授權碼場景重視來源與完整性，因此簽章即可滿足關鍵需求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q1

A-Q11: 數位簽章與資料加密的差別？
- A簡: 簽章驗證來源與完整性；加密保護機密性；兩者可分別或搭配使用。
- A詳: 簽章流程為「雜湊→私鑰簽署→公鑰驗證」，目的在鑑別與防竄改。加密則是「公/私鑰或對稱金鑰加密→持對應金鑰解密」，重點在保密。授權碼常為明文可解析的設定，但藉簽章防偽；若包含敏感資料，則可先加密再簽章，或簽章後再加密傳輸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q12

A-Q12: 授權碼在網站中的角色是什麼？
- A簡: 授權碼載明可用功能與期限，啟動時驗章與驗效後據此啟用或拒絕。
- A詳: 授權碼是網站或系統啟動時的權限來源，包含站點 ID、啟用功能、起訖日期等。系統先驗證簽章確保來源與完整性，再由授權碼本身的驗證邏輯（如 IsValidate）檢查有效性，如是否過期或功能集合理。通過後才啟用對應功能，否則中斷啟動。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q5, D-Q2

A-Q13: Key Container 與 XML 存檔有何差異？
- A簡: Key Container由OS防護與存取控制；XML檔易外流，僅適合示範或暫用。
- A詳: XML 方式匯出金鑰雖方便，但一旦檔案外流即導致私鑰暴露，缺乏 OS 隔離。Key Container 由作業系統管理，提供存取控制、加密與程式介面，搭配 CA 散佈公鑰更安全、可維運。實務須以 Key Container 取代 XML 檔，僅於開發或 DEMO 使用 XML。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q8, D-Q10

A-Q14: CA 在金鑰與簽章體系中扮演什麼角色？
- A簡: CA簽發與管理憑證，建立公鑰信任鏈，協助公鑰散布與驗章可信度。
- A詳: 憑證機構（CA）負責驗證實體身分並簽發憑證，將主體的公鑰與身分綁定。使用者驗章時可信任由 CA 簽署的公鑰來源，避免中間人替換公鑰問題。在多站台或分散式系統，透過 CA 分發與撤銷機制（CRL/OCSP）管理公鑰生命週期。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q15

A-Q15: 什麼是 Token 的「安全性」與「有效性」？
- A簡: 安全性指簽章可驗證未被偽造；有效性指業務規則（如未過期）通過。
- A詳: 在文中 Token 驗證同時關注兩層：安全性（VerifyData 驗章成功，判斷來源正確且未被竄改）與有效性（IsValidate 檢查業務規則，如日期範圍、功能集合、站點一致性）。兩者缺一不可：安全性不保就不可信，有效性不保則不授權。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q3, D-Q2

### Q&A 類別 B: 技術原理類

B-Q1: 數位簽章如何運作？整體流程為何？
- A簡: 先雜湊原文、以私鑰簽雜湊、附簽章傳遞；驗證端重算雜湊並用公鑰驗章比對。
- A詳: 技術原理說明：以 Hash 函式（如 SHA-256）計算原文摘要，再以私鑰對摘要簽署產生簽章。關鍵步驟或流程：1) 計算雜湊 2) 私鑰簽署 3) 打包原文+簽章 4) 驗證端重算雜湊 5) 以公鑰驗章並比對摘要。核心組件介紹：HashAlgorithm、私鑰與公鑰、簽章與驗章 API（如 RSACryptoServiceProvider.SignData/VerifyData）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q7, B-Q3

B-Q2: RSA 簽章的內部機制是什麼？步驟為何？
- A簡: RSA用私鑰對雜湊做數學運算產生簽章，公鑰逆向驗證與雜湊比對確認真偽。
- A詳: 技術原理說明：RSA 基於大數模指數運算，以私鑰 d 對雜湊 H(m) 做 s = H(m)^d mod n；驗證用公鑰 e 計算 v = s^e mod n 與 H(m) 比對。關鍵步驟：1) 選擇雜湊 2) RSASSA-PKCS1 v1.5 或 PSS 填充 3) 私鑰簽署 4) 公鑰驗證。核心組件：模數 n、指數 e/d、填充規範、RSACryptoServiceProvider 封裝上述流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q6, B-Q11

B-Q3: VerifyData 是如何驗證簽章的？
- A簡: 以同雜湊重算摘要，公鑰還原簽章摘要，比對兩者一致則通過。
- A詳: 技術原理說明：VerifyData 接收原資料、雜湊演算法與簽章，先用指定 Hash 重算摘要，再以公鑰與填充規範還原簽章得到摘要，兩者一致即為真。關鍵步驟：1) 重算 Hash 2) 公鑰驗章 3) 比對。核心組件：RSACryptoServiceProvider.VerifyData、HashAlgorithm（如 SHA256CryptoServiceProvider）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q15, C-Q2

B-Q4: SignData 需要哪些輸入？產出什麼？
- A簡: 輸入原始資料與雜湊演算法，由含私鑰的 RSA 物件產出簽章位元組。
- A詳: 技術原理說明：SignData 對輸入資料先雜湊，再以私鑰與選定填充演算法產生簽章。關鍵步驟：1) 餵入原文位元組 2) 設定 HashAlgorithm 3) 以私鑰簽署 4) 回傳簽章。核心組件：RSACryptoServiceProvider（須含私鑰）、SHA256CryptoServiceProvider、簽章結果為 byte[] 可後續 Base64。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q11

B-Q5: 為何只含 Public Info 的 XML 無法進行簽章？
- A簡: 簽章需私鑰，僅含公鑰的 RSA 物件無法執行 SignData，只能 VerifyData。
- A詳: 技術原理說明：簽章動作使用私鑰做模指數運算。只含 Modulus+Exponent 的公鑰無法推得私鑰，故 API 僅允許驗證。關鍵步驟：匯入 XML 後，RSACryptoServiceProvider 會標記 PublicOnly，SignData 會失敗。核心組件：RSAKeyValue 的 D、P、Q、DP、DQ、InverseQ 為私密欄位，缺失即無簽章能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q6

B-Q6: RSAKeyValue XML 各欄位代表什麼？
- A簡: Modulus/Exponent為公鑰；D、P、Q、DP、DQ、InverseQ 為私密參數。
- A詳: 技術原理說明：RSAKeyValue 中 Modulus(n) 與 Exponent(e) 定義公鑰；D 為私鑰指數，P、Q 為質因數，DP、DQ、InverseQ 用於 CRT 加速。關鍵步驟：FromXmlString 解析這些參數建立金鑰物件。核心組件：RSACryptoServiceProvider 與 XML 格式映射，PublicOnly= true 代表僅公鑰，含 D/P/Q 等則具簽章能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q6

B-Q7: 為何選用 BSON 序列化 Token？影響是什麼？
- A簡: BSON為二進位高效格式，序列化後便於簽章與傳輸，降低解析成本。
- A詳: 技術原理說明：先將 Token 物件以 BSON 序列化為 byte[]，再對該 byte[] 進行簽章，確保物件狀態完整受保護。關鍵步驟：使用 JsonSerializer+BsonWriter/Reader 轉換；簽章與驗章皆針對同一序列化結果。核心組件：MemoryStream、BsonWriter/BsonReader、JsonSerializer，確保一致性與性能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q3

B-Q8: Token 的打包與傳輸如何設計？
- A簡: 將data與signature 分別 Base64，使用分隔符拼接為可儲存傳輸的字串。
- A詳: 技術原理說明：序列化後的 data_buffer 與簽章 sign_buffer 分別 Base64 編碼，並用固定分隔字元拼接，形成可放入設定檔與環境變數的字串。關鍵步驟：1) Serialize 2) Sign 3) Convert.ToBase64String 4) string.Format 拼接 5) 解析時 Split+FromBase64String。核心組件：Base64、分隔符、例外處理（格式錯誤拋 TokenFormatException）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q3

B-Q9: TokenHelper.Init 內部做了什麼？
- A簡: 載入站點私鑰與各站公鑰，建立 RSA 快取與雜湊設定，作為簽章基礎。
- A詳: 技術原理說明：Init 從檔案或參數匯入 RSA XML，建立當前站點的 RSACryptoServiceProvider（含私鑰）與各站公鑰的字典快取，設定 HashAlgorithm。關鍵步驟：1) 掃描目錄或讀取 JSON 2) FromXmlString 建立 RSA 3) 設定 _CurrentRSACSP、_PublicKeyStoreDict 4) 檢查站點 ID。核心組件：RSACryptoServiceProvider、Dictionary<string, RSACryptoServiceProvider>、SHA256。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q6

B-Q10: PublicKeyStore 設計的作用與好處？
- A簡: 集中保存多站台公鑰，支援跨站驗章與信任管理，便於擴展與維護。
- A詳: 技術原理說明：PublicKeyStore 以 SiteID→RSACryptoServiceProvider 對應，允許針對不同來源驗章。關鍵步驟：啟動時載入站台清單與公鑰 XML，建立字典；驗章時依 Token.SiteID 取得對應公鑰驗證。核心組件：字典快取、SiteID 索引、憑證來源（CA/設定檔），提升多伺服器互通能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q6

B-Q11: HashAlgorithm（如 SHA256）選擇對簽章的影響？
- A簡: 雜湊強度決定抗碰撞性與驗章可靠度，應使用安全演算法如 SHA-256。
- A詳: 技術原理說明：簽章保護的是雜湊值，若雜湊演算法弱（易碰撞），攻擊者可能構造不同原文產生相同雜湊而繞過驗章。關鍵步驟：選擇 SHA-256 或以上強度；在 SignData/VerifyData 明確指定相同 Hash。核心組件：SHA256CryptoServiceProvider、演算法生命週期與棄用清單，需跟隨最佳實務更新。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q4

B-Q12: 一對多與一對一安全通訊的差異是什麼？
- A簡: 對稱適合廣播需共用祕密；非對稱適合點對點或身份鑑別與簽章。
- A詳: 技術原理說明：一對多（廣播）用對稱金鑰同組態可快速解密，但金鑰分發與輪換不易；一對一用非對稱以對方公鑰加密或以私鑰簽章驗證身份。關鍵步驟：選擇合適模式，對稱用同密鑰；非對稱用 A 私鑰+B 公鑰加密/簽章。核心組件：對稱金鑰管理、非對稱金鑰對、公私鑰分發。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q11

B-Q13: 為什麼 RSA 適合身分鑑別與防偽？
- A簡: 私鑰獨占、驗證可公開，能證明簽發者身份且難以偽造，支持不可否認。
- A詳: 技術原理說明：只有私鑰持有者能產生對應簽章，任何人持公鑰即可驗證，且數學上從公鑰推私鑰難度極高。關鍵步驟：簽發端持私鑰簽署，驗證端持公鑰驗證；可配合 CA 建信任。核心組件：RSA 金鑰對、填充規範、驗章 API，支撐防偽與審計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q10

B-Q14: ASP.NET MVC 啟動時的授權驗證流程是什麼？
- A簡: 讀取設定→Init 金鑰與公鑰庫→Decode+驗章→驗效→未通過則中斷啟動。
- A詳: 技術原理說明：在 Startup.Configure 早期階段載入 appsettings.json 的 License 區段，初始化 TokenHelper 與公鑰庫；再 DecodeToken 進行驗章與有效性檢查。關鍵步驟：1) 解析 JSON 2) Init 金鑰 3) Decode+VerifyData 4) IsValidate 5) 失敗丟例外。核心組件：IConfiguration、TokenHelper、RSACryptoServiceProvider、例外導致網站無法啟動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q2

B-Q15: 金鑰管理與 Key Container 的架構建議？
- A簡: 改用 OS Key Container、CA 發布公鑰、權控與審計，避免 XML 檔外流風險。
- A詳: 技術原理說明：由 OS 管理金鑰的產生、儲存與使用，避免私鑰平面化落地；公鑰透過 CA 發布與撤銷。關鍵步驟：1) 以 Key Container 建鑰 2) 權限控制執行帳戶 3) 審計存取 4) 定期輪替 5) 暗管祕密。核心組件：CSP/CNG Key Storage、憑證鏈、CRL/OCSP、祕密管理系統（如 HSM 或安全憑證存放區）。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q13, C-Q8, D-Q6

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 .NET 使用 RSACryptoServiceProvider 產生簽章？
- A簡: 序列化資料為位元組，指定 SHA-256，用含私鑰的 RSA 物件呼叫 SignData。
- A詳: 具體實作步驟：1) 將物件序列化為 byte[]（如 BSON）2) 建立含私鑰之 RSACryptoServiceProvider 3) 指定 SHA256CryptoServiceProvider 4) 執行 SignData 得到簽章 5) 需考慮 Base64 與封裝。關鍵程式碼片段:
```csharp
var rsa = new RSACryptoServiceProvider();
rsa.FromXmlString(sitePrivateKeyXml);
byte[] sig = rsa.SignData(dataBytes, new SHA256CryptoServiceProvider());
```
注意事項：私鑰只在安全環境使用；一致的序列化與雜湊選型；避免將私鑰硬編碼於程式碼。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q7

C-Q2: 如何驗證簽章並還原 Token？
- A簡: 分離Base64後復原資料與簽章，用公鑰 VerifyData，再反序列化為物件。
- A詳: 具體實作步驟：1) 以分隔符 Split 字串 2) 將兩段 Base64 還原為 data/sign 3) 憑 Token.SiteID 取公鑰 4) VerifyData 驗章 5) 驗章通過後反序列化。關鍵程式碼:
```csharp
var parts = tokenText.Split('|');
var data = Convert.FromBase64String(parts[0]);
var sign = Convert.FromBase64String(parts[1]);
bool ok = pubRsa.VerifyData(data, new SHA256CryptoServiceProvider(), sign);
```
注意：先驗章再信任資料；處理 TokenFormatException 與來源站台查核。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q8

C-Q3: 如何設計 Token 資料模型與 IsValidate 規則？
- A簡: 定義SiteID、功能與日期等欄位，IsValidate檢查期限與一致性等業務規則。
- A詳: 具體實作步驟：1) 設計 TokenData: SiteID、EnableAPI、LicenseStart/End、TypeName… 2) IsValidate 檢查當前時間在有效區間、SiteID 合法、功能集不為空等 3) 序列化時包含 TypeName 便於反序列化。關鍵程式碼：在 Token 類別實作 bool IsValidate()。注意：確保時間使用可信來源、避免時區誤差、明確失敗訊息。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q2

C-Q4: 如何將授權資訊放入 appsettings.json？
- A簡: 在 License 區段配置 TokenData、SiteID、SitePrivateKey、PublicKeyStore。
- A詳: 具體實作步驟：1) 新增 appsettings.json 的 "License" 節點 2) 放入 Base64 的 TokenData 3) 配置 SiteID 與私鑰 XML 4) PublicKeyStore 為站點公鑰陣列。設定片段：
```json
"License": {
  "TokenData": "<Base64...>",
  "SiteID": "ORCA",
  "SitePrivateKey": "<RSAKeyValue>...</RSAKeyValue>",
  "PublicKeyStore": [{ "SiteID": "GLOBAL", "KeyXML": "<RSAKeyValue>...</RSAKeyValue>"}]
}
```
注意：私鑰不宜長期放設定檔，實務改用 Key Container 或祕密管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, B-Q9

C-Q5: 如何在 Startup 中載入授權並阻擋未授權啟動？
- A簡: Configure 讀取 License 設定→TokenHelper.Init→DecodeToken，失敗即拋例外中止。
- A詳: 具體實作步驟：1) IConfiguration 取得 "License" 2) 建 PublicKeyStore 字典 3) TokenHelper.Init(siteId, privateKey, dict) 4) TokenHelper.DecodeToken<SiteLicenseToken>() 5) 例外即阻擋啟動。關鍵程式碼：
```csharp
var lic = Configuration.GetSection("License");
TokenHelper.Init(lic["SiteID"], lic["SitePrivateKey"], dict);
var token = TokenHelper.DecodeToken<SiteLicenseToken>(lic["TokenData"]);
```
注意：此段應置於路由前；記錄錯誤日誌；避免把錯誤細節曝露給終端使用者。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, D-Q2

C-Q6: 如何建置 PublicKeyStore 以支援多站台驗章？
- A簡: 以SiteID為鍵建立字典，啟動時載入各站公鑰 XML，驗章依 Token.SiteID 選取。
- A詳: 具體實作步驟：1) appsettings.json 配置 PublicKeyStore 陣列 2) 啟動時轉為 Dictionary<string,string> 3) FromXmlString 建立 RSACryptoServiceProvider 4) 以 SiteID 索引驗章。關鍵程式碼：
```csharp
foreach (var item in conf.Get<Dictionary<string,string>[]>("PublicKeyStore"))
  dict.Add(item["SiteID"], item["KeyXML"]);
```
注意：公鑰來源應由 CA 或受信通道散布；新增或輪替公鑰需有版本管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q4

C-Q7: 如何安全地匯入/匯出 RSA XML 金鑰？
- A簡: 開發期可 From/ToXmlString；實務避免匯出私鑰，限制權限並清除暫存。
- A詳: 具體實作步驟：1) 開發 DEMO 可用 rsa.FromXmlString(xml) 2) 需匯出時僅匯出公鑰（不含 D、P、Q…）3) 清除含私鑰檔案，限制檔案與程序存取。關鍵程式碼：
```csharp
var rsa = new RSACryptoServiceProvider();
// rsa.ToXmlString(includePrivateParameters: false) 只匯出公鑰
```
注意：避免將私鑰放版控或日誌；實務以 Key Container/HSM 管理私鑰。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q5

C-Q8: 如何改用 Key Container 管理金鑰？
- A簡: 使用 OS 金鑰儲存與存取 API，設定容器名稱與權限，避免私鑰落地。
- A詳: 具體實作步驟：1) 建立/載入金鑰容器（CspParameters/CngKey）2) 以容器產生 RSACryptoServiceProvider 3) 移除 XML 私鑰依賴 4) 設定服務帳戶存取權。關鍵程式碼（範例）：
```csharp
var csp = new CspParameters { KeyContainerName = "SiteKey" };
var rsa = new RSACryptoServiceProvider(csp);
```
注意：佈署前建立容器；權限最小化；搭配憑證與 CA 管理公鑰發佈。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, D-Q10

C-Q9: 如何記錄授權驗證日誌與告警？
- A簡: 記錄驗章結果、站點、時間與異常細節，失敗觸發告警並避免曝露敏感資訊。
- A詳: 具體實作步驟：1) 在 Decode/Verify 周邊加日誌 2) 記錄 SiteID、雜湊演算法、例外型別 3) 對 Token 資料避免落地明文 4) 整合監控（Email/Slack/SIEM）。關鍵程式碼：try-catch 捕捉 TokenNotSecure/Validate/Format 等。注意：錯誤訊息對外模糊化，對內詳盡；避免將 Base64 原文長期留存。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q1, D-Q2

C-Q10: 如何撰寫單元測試覆蓋授權驗證？
- A簡: 測試正常驗章、過期無效、簽章不符與格式錯誤，模擬多站公鑰情境。
- A詳: 具體實作步驟：1) Arrange: 準備私鑰、公鑰與樣本 Token 2) Act: Encode→Decode 流程 3) Assert: 驗證通過與例外拋出（TokenNotSecure、TokenNotValidate、TokenFormat）4) Mock PublicKeyStore。關鍵程式碼：以測試框架（xUnit/NUnit）與固定測試向量。注意：避免使用真實私鑰；測試涵蓋時區、邊界日期、SiteID 不存在情境。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, D-Q3

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 TokenNotSecureException 怎麼辦？
- A簡: 表示簽章驗證失敗，檢查公鑰、資料與簽章是否一致與未被竄改。
- A詳: 問題症狀：啟動時丟出 TokenNotSecureException。可能原因：公鑰錯誤或缺失、Token 被改動、簽章雜湊不一致、序列化差異。解決步驟：1) 核對 Token.SiteID 對應的公鑰 2) 重新發送未被修改的 Token 3) 確認簽章與資料成對 4) 一致的雜湊與序列化設定。預防：公鑰由 CA 散布、Token 不允許手動編輯、加強傳輸與存放完整性保護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q2

D-Q2: 遇到 TokenNotValidateException 如何處理？
- A簡: 代表業務規則不通過，如過期或站點不符，更新合法授權或校正規則。
- A詳: 問題症狀：驗章通過但 IsValidate 為 false。可能原因：授權過期、尚未生效、SiteID 不符、功能集不允許。解決步驟：1) 檢查授權日期區間 2) 比對 SiteID 與部署環境 3) 重新發授權碼 4) 檢視 IsValidate 邏輯與時間來源。預防：加入到期前告警、校正時鐘、明確版本化授權條件。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q5

D-Q3: 為何會拋 TokenFormatException？怎麼解？
- A簡: 字串格式或 Base64 解析失敗，多因分隔符錯誤或資料破損，需重新發送。
- A詳: 問題症狀：Split 後段數不為 2、Base64 解碼錯誤、反序列化失敗。可能原因：分隔字元不符、傳輸截斷、編碼被改動、非對應的序列化格式。解決步驟：1) 確認分隔符設定一致 2) 驗證 Base64 字串完整 3) 保持序列化器一致（BSON）4) 重新生成 Token。預防：使用穩定傳輸通道、加入完整性檢查、避免人工編輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q10

D-Q4: TokenSiteNotExistException 的排查與修復？
- A簡: 公鑰庫缺少該 SiteID，需補登公鑰或修正 Token.SiteID。
- A詳: 問題症狀：驗章前查詢 _PublicKeyStoreDict 不存在該站台。可能原因：設定遺漏、SiteID 拼錯、授權碼發給不同站。解決步驟：1) 檢查 appsettings.json 的 PublicKeyStore 2) 補充對應公鑰 3) 確認 SiteID 一致 4) 若跨站，改由 CA 發布公鑰。預防：站台清單版本控、部署前檢核、以憑證鏈管理信任。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q6, B-Q10

D-Q5: VerifyData 回傳 false 但格式看似正確？
- A簡: 多半是雜湊或序列化不一致、公鑰不對或資料被改動，需逐一對照環境。
- A詳: 問題症狀：Split/Base64/反序列化成功，但 VerifyData 為 false。可能原因：簽章時與驗章時使用不同 Hash、不同序列化版本、公鑰非對應、資料微改。解決步驟：1) 檢查 HashAlgorithm 2) 確認序列化器與版本固定 3) 公鑰來源正確 4) 比對來源與驗證端 data_buffer 是否一致。預防：固定與宣告雜湊與序列化策略、加上版本欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q7

D-Q6: 私鑰外洩時如何應急與復原？
- A簡: 立即撤銷舊金鑰、重發授權、輪換公鑰並清查影響，導入更安全的金鑰管理。
- A詳: 問題症狀：發現可偽造簽章或私鑰檔流出。可能原因：XML 檔外流、權限控管鬆散、日誌外洩。解決步驟：1) 立刻停用與撤銷對應公鑰 2) 生成新金鑰對 3) 更新 PublicKeyStore/CA 發布 4) 重簽並重發所有授權 5) 稽核與通報。預防：改用 Key Container/HSM、最小權限、定期輪替、祕密管理與監控告警。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, C-Q7

D-Q7: 系統時鐘錯誤導致授權誤判怎麼辦？
- A簡: 校正時間來源，避免 IsValidate 因時差判為過期或未生效。
- A詳: 問題症狀：部分機器判定過期/未生效，實際仍在有效期。可能原因：NTP 未同步、時區誤設、應用使用本地時間。解決步驟：1) 啟用 NTP 同步 2) 統一時區或使用 UTC 3) 在 IsValidate 改用標準化時間來源 4) 加入容錯時間窗。預防：部署前時間健檢、營運監控時間漂移。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q3, C-Q5

D-Q8: 金鑰長度太短造成風險與遷移方案？
- A簡: 低位元數易被破解，應升級到足夠長度（如 ≥2048-bit）並計畫輪替。
- A詳: 問題症狀：安全稽核警示 RSA 位元數不足。可能原因：舊系統遺留、預設值過低。解決步驟：1) 生成新長度金鑰（>=2048）2) 發布新公鑰 3) 雙簽過渡或版本欄位 4) 更新客戶端公鑰庫。預防：遵循密碼學建議、定期安全檢視、在 Token 增加金鑰/簽章版本以便升級。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, C-Q6

D-Q9: appsettings.json 被竄改怎麼辦？
- A簡: 導致 Token 或公鑰庫異常，應加完整性保護、限制權限並簽章設定。
- A詳: 問題症狀：啟動失敗或驗證錯誤頻發。可能原因：惡意修改 TokenData、替換公鑰。解決步驟：1) 比對檔案雜湊或簽章 2) 從可信來源還原 3) 強化檔案 ACL 與唯讀 4) 將敏感設定移至祕密管理。預防：CI/CD 供應鏈安全、設定檔簽章與校驗、最小權限。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q4, C-Q9

D-Q10: 使用 Key Container 時簽章失敗如何診斷？
- A簡: 多為權限或容器不存在，檢查容器名稱、帳戶存取與憑證可用性。
- A詳: 問題症狀：改用 Key Container 後 SignData/VerifyData 擲例外。可能原因：容器未建立、執行帳戶無權、FIPS/Provider 不相容。解決步驟：1) 確認容器存在 2) 調整服務帳戶權限 3) 選對 Provider（CSP/CNG）4) 驗證憑證鏈完整。預防：部署腳本建立容器、文件化權限需求、整合前測試環境驗證。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q8, B-Q15

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是數位簽章？
    - A-Q2: 數位簽章與電子簽章有何差異？
    - A-Q3: 為什麼授權碼需要數位簽章？
    - A-Q4: 對稱式與非對稱式加密有何差異？
    - A-Q5: 什麼是公鑰與私鑰？各自用途是什麼？
    - A-Q6: 什麼是 RSA？為何常用於簽章？
    - A-Q7: 什麼是 Hash（雜湊）？在簽章中扮演何角色？
    - A-Q10: 數位簽章能保障哪些安全性屬性？
    - A-Q11: 數位簽章與資料加密的差別？
    - A-Q12: 授權碼在網站中的角色是什麼？
    - B-Q1: 數位簽章如何運作？整體流程為何？
    - B-Q3: VerifyData 是如何驗證簽章的？
    - B-Q4: SignData 需要哪些輸入？產出什麼？
    - C-Q1: 如何在 .NET 使用 RSACryptoServiceProvider 產生簽章？
    - C-Q2: 如何驗證簽章並還原 Token？

- 中級者：建議學習哪 20 題
    - A-Q13: Key Container 與 XML 存檔有何差異？
    - A-Q14: CA 在金鑰與簽章體系中扮演什麼角色？
    - A-Q15: 什麼是 Token 的「安全性」與「有效性」？
    - B-Q2: RSA 簽章的內部機制是什麼？步驟為何？
    - B-Q6: RSAKeyValue XML 各欄位代表什麼？
    - B-Q7: 為何選用 BSON 序列化 Token？影響是什麼？
    - B-Q8: Token 的打包與傳輸如何設計？
    - B-Q9: TokenHelper.Init 內部做了什麼？
    - B-Q10: PublicKeyStore 設計的作用與好處？
    - B-Q11: HashAlgorithm（如 SHA256）選擇對簽章的影響？
    - B-Q14: ASP.NET MVC 啟動時的授權驗證流程是什麼？
    - C-Q3: 如何設計 Token 資料模型與 IsValidate 規則？
    - C-Q4: 如何將授權資訊放入 appsettings.json？
    - C-Q5: 如何在 Startup 中載入授權並阻擋未授權啟動？
    - C-Q6: 如何建置 PublicKeyStore 以支援多站台驗章？
    - C-Q9: 如何記錄授權驗證日誌與告警？
    - C-Q10: 如何撰寫單元測試覆蓋授權驗證？
    - D-Q1: 遇到 TokenNotSecureException 怎麼辦？
    - D-Q2: 遇到 TokenNotValidateException 如何處理？
    - D-Q3: 為何會拋 TokenFormatException？怎麼解？

- 高級者：建議關注哪 15 題
    - B-Q12: 一對多與一對一安全通訊的差異是什麼？
    - B-Q13: 為什麼 RSA 適合身分鑑別與防偽？
    - B-Q15: 金鑰管理與 Key Container 的架構建議？
    - C-Q7: 如何安全地匯入/匯出 RSA XML 金鑰？
    - C-Q8: 如何改用 Key Container 管理金鑰？
    - D-Q4: TokenSiteNotExistException 的排查與修復？
    - D-Q5: VerifyData 回傳 false 但格式看似正確？
    - D-Q6: 私鑰外洩時如何應急與復原？
    - D-Q7: 系統時鐘錯誤導致授權誤判怎麼辦？
    - D-Q8: 金鑰長度太短造成風險與遷移方案？
    - D-Q9: appsettings.json 被竄改怎麼辦？
    - D-Q10: 使用 Key Container 時簽章失敗如何診斷？
    - C-Q5: 如何在 Startup 中載入授權並阻擋未授權啟動？
    - B-Q9: TokenHelper.Init 內部做了什麼？
    - B-Q11: HashAlgorithm（如 SHA256）選擇對簽章的影響？