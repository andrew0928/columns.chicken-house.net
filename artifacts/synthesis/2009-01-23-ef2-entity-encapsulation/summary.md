# EF#2. Entity & Encapsulation

## 摘要提示
- ORM 對應機制: 目標是讓物件狀態安全、正確且便利地對應到關聯式資料庫
- 兩條發展路徑: 串接物件與關聯資料庫的 ORM 與讓 RDBMS 具物件特性的 OODB 構想
- 評估面向: 以封裝、繼承、多型與查詢四面向檢視 Entity Framework
- 入門資源: 推薦 MSDN 朱明中系列文章作為 EF 入門參考
- 反例示範: 直接映射欄位導致外洩實作細節與邏輯分散
- 密碼處理問題: 直接公開 PasswordHash 暴露不必要細節與誤用風險
- 业务規則耦合: 台灣 SSN 與 Gender 存在相依性，易造成資料不一致
- SQL 限制: 以 trigger/view/constraint 難完整維護複雜規則與一致性
- 封裝解法: 以 EF partial class 封裝欄位、提供最小介面與不變條件維護
- 使用體驗提升: 封裝後 API 更精煉、錯誤更少、程式語意更清楚

## 全文重點
本文從一個簡單的會員資料範例切入，說明為何僅靠 ORM 的欄位對應並不足以寫出高品質的系統，並以 Entity Framework 展示如何藉由封裝把資料邏輯放回正確的地方。作者先指出：ORM 的共同目標是讓物件狀態可以保存到關聯式資料庫，但物件世界與關聯世界本質差異巨大，導致三層式中間層常出現斷層。現實可行的兩條路，一是以 ORM 負責對應；二是改造 RDBMS 成為具物件特性的資料庫。短期內 ORM 仍最實際，因此應從封裝、繼承、多型與查詢四個面向審視 EF 的價值。

範例以 Users 資料表為例。傳統做法是把資料表拉進 EDMX 後直接使用 Entity 類別，於是出現兩個設計缺陷：其一直接暴露 PasswordHash 使呼叫端得自行運算與比較，外洩實作細節並增加誤用風險；其二在台灣，SSN 與 Gender 有函數相依，卻被拆成兩個由前端維護的一致性，極易產生不一致資料。雖然可用 SQL trigger、constraint 或以 VIEW 計算，但複雜規則常超出 SQL 能力與效能邊界，且難以確保與應用程式一致。

作者主張把領域邏輯封裝回 Entity：將 PasswordHash 與 GenderCode 的 getter/setter 改為私有，對外只提供 Password 設值與 ComparePassword 方法，清楚表達「密碼可寫不可讀」與「只回答正不正確」。同時透過 EF 產生的 partial class，覆寫 SSN 的變更行為：在 OnSSNChanging 中同步計算 GenderCode，對外僅以列舉型別屬性 Gender（唯讀）呈現，避免直接寫入錯誤性別值。密碼雜湊計算則內聚於私有方法 ComputePasswordHash。

重寫後的建立/驗證程式碼更為精煉：新增使用者時僅設定 Password 與 SSN；驗證時只呼叫 ComparePassword。這種設計以最小公開介面滿足需求，封裝實作細節、集中不變條件維護，讓業務規則靠近資料，提升語意清晰度與正確性，減少因為資料不一致導致的 SqlException 與隱性錯誤。本文結尾預告後續將進一步探討 EF 如何支援繼承、多型與查詢，持續從物件導向核心能力檢視 EF 的實用性。

## 段落重點
### ORM 的目的與兩條路
作者回顧 ORM 的核心在於「對應」：把物件狀態安全且便利地存入關聯式資料庫。因物件技術與資料庫技術解決的問題已分道揚鑣，三層式架構在資料與行為的邊界易出現落差。解法要嘛強化 ORM 以橋接兩界，要嘛把 RDBMS 演進為具物件特性的資料庫（OODB）。短中期看，ORM 仍是主流務實方案。只要對應做得完善，等同在應用層實踐某種 OODB 願景：物件活在應用端，由 ORM 負責持久化。本文將以封裝、繼承、多型與查詢四面向檢視 EF 的支援度與投資價值，並先提供一組 MSDN 文章作為學習基礎。

### 反例：只用對應、忽略封裝
以 Users 表為例，許多人會把表直接拖入 EDMX 即用。在此做法下，建立帳號與檢查密碼需要於呼叫端直接計算 MD5 雜湊並逐位比較陣列，暴露 PasswordHash 欄位且使多處重複邏輯蔓延；同時 SSN 與 Gender 在台灣具有函數相依，由前端自行維護一致性，極易失誤。雖可用 trigger、constraint、VIEW 幫忙，但複雜規則難以完整表達，且效能與一致性無法保證，最終容易在不同層發生矛盾或例外，顯示單純欄位對應不足以承載業務邏輯。

### 封裝設計：以 EF partial class 內聚規則
改造策略是縮小公開介面並內聚實作：將 PasswordHash 與 GenderCode 的存取子改為私有，對外提供 Password（僅 setter）與 ComparePassword(password) 方法，明確傳達「密碼可設不可讀，只能驗證」。針對 SSN 與性別相依問題，保留 SSN 屬性並在 OnSSNChanging 中同步計算 GenderCode，不對外提供其 setter；對外僅以 Gender（列舉型別、唯讀）呈現。密碼計算集中在 ComputePasswordHash 私有方法。經此封裝後，建立與驗證流程更簡潔安全：新增使用者直接設 Password 與 SSN；驗證只呼叫 ComparePassword，避免重複與錯用。此設計用最小介面滿足需求，維持資料不變條件，提升可讀性與正確性，並減少資料層例外。文末預告後續將示範 EF 在繼承、多型與查詢面向的應用。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本物件導向觀念：封裝、屬性/方法、存取修飾詞、Enum
   - 關聯式資料庫基礎：Table、Primary Key、Constraint、View、Trigger
   - ADO.NET/Entity Framework 基礎：EDMX、Entity、ObjectContext、partial class、partial method
   - 基本加解密/雜湊觀念：Hash（例：MD5）、為何儲存雜湊而非明碼
   - C# 語法與 .NET 類別庫（HashAlgorithm、Encoding）

2. 核心概念：
   - ORM 的「對應」：物件世界與關聯式資料世界的橋接
   - 封裝（Encapsulation）：公開最小必要介面，隱藏實作細節與資料欄位
   - 實體行為內聚：將驗證邏輯（如密碼比對、身分證與性別聯動）放回 Entity
   - EF 擴充模型的方式：partial class/partial method 強化由 EDMX 產生的類別
   - 資料一致性策略：應放在程式端（Domain/Entity）或資料庫端（Trigger/Constraint/View）的取捨

3. 技術依賴：
   - EF EDMX 產碼 → 以 partial class 增補行為（封裝密碼與屬性轉換）
   - C# 屬性與方法 → 封裝資料欄位（private setter、只讀屬性）
   - HashAlgorithm/Encoding → 計算密碼雜湊
   - EF 實體事件掛點 → partial void On<Property>Changing(...) 實作聯動邏輯
   - RDB 特性 → 最終落盤仍是 Table/Relationship，需與程式端封裝互補

4. 應用場景：
   - 會員/帳號系統：密碼儲存雜湊、提供驗證介面而非讀取密碼
   - 領域規則與欄位聯動：如台灣身分證字號與性別碼的功能相依
   - 將無法（或不宜）在 SQL 中完整表達的複雜規則，移入 Entity 的封裝邏輯
   - 降低前端或應用層重複實作與出錯機率，集中一致性規則

### 學習路徑建議
1. 入門者路徑：
   - 了解 ORM 與關聯式資料庫基本概念
   - 建立簡單的 EF 專案：從資料表產生 EDMX 與 Entity
   - 練習以 ObjectContext 新增/查詢/儲存資料
   - 認識 C# 屬性、存取修飾詞與 Enum

2. 進階者路徑：
   - 使用 partial class/partial method 擴充由 EDMX 產生的實體
   - 實作封裝：隱藏欄位（private setter）、提供最小必要公開介面（方法或只寫屬性）
   - 在實體中實作領域規則（例如 SSN 變更時同步 GenderCode）
   - 比較程式端封裝 vs DB Trigger/Constraint/View 的優缺點與邊界

3. 實戰路徑：
   - 實作帳號系統：密碼設定（只寫屬性）、密碼比對（方法）、阻斷讀取雜湊
   - 封裝多個聯動欄位的規則，確保資料一致性（例如 SSN → GenderCodeEnum）
   - 撰寫自動化測試：覆蓋密碼驗證、欄位聯動與不可變更條件
   - 對照效能與維運需求，決定哪些規則進資料庫、哪些進實體

### 關鍵要點清單
- ORM 對應的本質：連結物件世界與關聯式資料世界的映射與同步（優先級: 高）
- 封裝原則：公開最小必要介面、隱藏實作細節與不該外露的資料（優先級: 高）
- 密碼雜湊儲存：永不儲存明碼，提供設定與驗證，而非讀取（優先級: 高）
- partial class 擴充 EF 產生碼：在不修改產生碼下為實體加入行為（優先級: 高）
- partial method On<Property>Changing：在屬性變更時注入領域規則（優先級: 中）
- 只寫屬性與私有存取器：以 Password setter/ComparePassword 取代 PasswordHash 暴露（優先級: 高）
- 欄位聯動與功能相依：以 SSN 推導 GenderCode，對外僅提供 Enum、只讀（優先級: 中）
- 程式端一致性 vs DB 限制：何時選擇 Trigger/Constraint/View，何時放到 Entity（優先級: 中）
- 例外與錯誤面：未封裝導致不一致資料或大量 SqlException（優先級: 中）
- 安全性邊界：不暴露雜湊與演算法細節，避免外部誤用（優先級: 高）
- 測試策略：針對密碼驗證與屬性聯動撰寫單元測試（優先級: 中）
- 可讀性與維護性：封裝讓使用端程式更短更清晰，錯誤率降低（優先級: 高）
- Enum 對外表達：以 Enum（GenderCodeEnum）封裝內部數值碼（優先級: 低）
- 演算法抽換考量：以方法封裝雜湊，未來可替換 MD5/鹽化等（優先級: 中）
- 與 OODB 願景的連結：完美對應加良好封裝，讓應用端近似物件資料庫體驗（優先級: 低）