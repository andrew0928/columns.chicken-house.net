---
layout: synthesis
title: "EF#2. Entity & Encapsulation"
synthesis_type: faq
source_post: /2009/01/23/ef2-entity-encapsulation/
redirect_from:
  - /2009/01/23/ef2-entity-encapsulation/faq/
postid: 2009-01-23-ef2-entity-encapsulation
---

# EF#2. Entity & Encapsulation

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 ORM（物件關聯對應）？
- A簡: ORM 將物件狀態對應至關聯式資料表，讓程式以物件操作資料，由框架處理 SQL 與存取細節，縮小物件與資料庫落差。
- A詳: ORM（Object-Relational Mapping）是一種將物件模型與關聯式資料庫結構互相映射的技術。開發者用物件與屬性表達資料與行為，ORM 框架負責把物件變更轉成 SQL，並將查詢結果還原成物件。其特點是提升生產力、減少重複樣板程式、集中資料存取規則。適用場景包含三層式應用、需要持久化的商業物件、以及想將資料存取關注點與領域邏輯分離時。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, B-Q1

Q2: 為何需要 ORM 的對應機制？
- A簡: 物件技術發展與 RDBMS 差異大，三層式架構出現斷層；ORM 用對應機制銜接兩個世界，簡化資料持久化。
- A詳: 物件導向能表達豐富的狀態與行為，但主流資料庫仍多為關聯式，僅以表格與關聯表達資料。兩者關注點不同，導致開發者常在程式與 SQL 之間來回切換。ORM 的價值在於建立穩健的對應層：用物件操作資料，框架負責查詢、更新與關聯處理，降低阻抗不匹配與重複樣板程式，讓領域邏輯聚焦於業務本身。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, B-Q1

Q3: 什麼是 Entity Framework？
- A簡: Entity Framework 是 .NET 的 ORM 框架，透過 EDMX 進行模型與資料庫對應，並以物件化方式操作資料。
- A詳: Entity Framework（EF）是微軟在 .NET 平台提供的 ORM 技術。它以 EDMX 描述概念模型、儲存模型與對應，並自動產生實體類別與物件內容（Object Context）。開發者透過 LINQ 或 API 操作實體，EF 處理查詢翻譯、變更追蹤、關聯載入與持久化。其特點是降低資料層複雜度、支援物件導向特性擴充（如以 partial class 封裝行為），適用一般商務系統與三層式架構。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, C-Q5

Q4: EF 的核心目標是什麼？
- A簡: 讓物件更貼近一般物件使用方式，同時能安全、簡單地存入關聯式資料庫，降低對應與存取負擔。
- A詳: EF 的核心目標是「以物件操作資料」。它希望實體像一般領域物件一樣表達狀態與行為，而資料存取細節（SQL、關聯、交易）由框架代管。EF 透過模型對應、變更追蹤與 SaveChanges 提交來落實。當結合封裝、部分類別與事件勾點時，能把敏感欄位與不必要細節隱藏，對外提供最小化介面，提升正確性與可維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q8, C-Q1

Q5: 什麼是 Entity（實體）？
- A簡: Entity 是對應資料表列的物件，包含欄位對應的屬性與可被擴充的行為，是 EF 操作的核心單位。
- A詳: 在 EF 中，實體代表資料庫中一筆或多筆資料表列的概念模型。實體類別通常由 EDMX 產生，包含屬性對應欄位、關聯對應導覽屬性。透過 partial class，實體可加入領域行為（如驗證、計算、封裝敏感資料）。開發者對實體的新增、修改與刪除由內容物件追蹤，最後呼叫 SaveChanges 寫回資料庫。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q5

Q6: 什麼是封裝（Encapsulation）？
- A簡: 封裝是隱藏實作細節、僅暴露必要介面，保護不變條件，降低外部耦合，提升正確性與維護性。
- A詳: 封裝是物件導向核心概念，強調將資料與行為包成整體，對外只提供滿足需求的最小介面，實作細節與內部狀態對外隱藏。它能維護不變條件，避免外部繞過規則亂改資料。在 EF 實務中，將敏感欄位（如 PasswordHash）私有化，改以方法或寫入式屬性提供功能，並用部分類別放入驗證邏輯，即是封裝的具體運用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q3, D-Q3

Q7: 為什麼在 EF 中需要強調封裝？
- A簡: 未封裝會暴露敏感細節、增加前端誤用風險，造成資料不一致與例外；封裝能集中規則與保護資料。
- A詳: EF 讓資料以物件呈現，若直接暴露所有屬性，前端可能繞過必要規則（如直接設定 PasswordHash、手動填錯性別），導致不一致與錯誤。強化封裝可把「怎麼做」留在實體內部，例如提供 ComparePassword、在設定 SSN 時同步性別碼，對外不開放敏感 Getter。如此集中規則、減少重複驗證，讓程式碼更簡潔、安全且可測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q10, C-Q4

Q8: 直接暴露 PasswordHash 有何風險？
- A簡: 暴露 Hash 泄漏實作細節、易被誤用或外洩；正確作法是提供設定密碼與驗證方法，不提供讀取 Hash。
- A詳: PasswordHash 是內部安全細節。若公開 Getter/Setter，呼叫端可能直接取用或錯誤賦值，破壞安全流程，也增加被記錄、傳輸外洩的風險。封裝的作法是：只提供 Password 寫入屬性來計算與存放 Hash，並提供 ComparePassword 執行檢核，不讓任何端讀取或操作 Hash 本體，維護安全與不變條件的一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q3, D-Q3

Q9: 密碼處理應提供哪些最小介面？
- A簡: 提供寫入式 Password 屬性與 ComparePassword 方法即可，拒絕讀取 Hash 或明碼，避免不必要暴露。
- A詳: 最小介面原則要求只暴露需求必須的操作。對於密碼領域，需求是「能設定新密碼」與「能驗證使用者輸入」。因而提供一個僅 Setter 的 Password 屬性觸發 Hash 計算與存放；另提供 ComparePassword(string) 回傳布林結果。這樣避免明碼或 Hash 的讀取介面，既清楚表達意圖，也降低安全風險與誤用機率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q1, C-Q3

Q10: 台灣 SSN 與性別（Gender）為何是相依欄位？
- A簡: 依規則，性別可由身份證字號推導，屬功能相依；若分開維護易不一致，需用程式或資料庫機制同步。
- A詳: 依台灣身份證編號規則，可從字號的特定位判斷性別，因此 Gender 對 SSN 屬功能相依。若兩者皆開放自由設定，前端一不注意即造成不一致。解法可用資料庫約束、觸發器或視圖計算，但當規則複雜、效能或一致性考量下，將邏輯封裝於實體：在 SSN 變更時同步 GenderCode，並僅對外提供唯讀的 Gender 介面，能有效避免錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, A-Q12, A-Q13

Q11: 什麼是功能相依（Functional Dependency）？
- A簡: 當一屬性值能由另一屬性決定，即形成功能相依；例如性別可由 SSN 依規則推導得出。
- A詳: 功能相依描述屬性間的決定性關係，記為 X → Y，意指給定 X 的值可唯一決定 Y。在實務中，台灣 SSN 與性別呈現此關係。模型設計應避免讓使用者同時任意編輯 X 與 Y，以免違反不變條件。可用程式封裝在設定 X 時自動計算 Y，或以視圖、計算欄位呈現 Y，確保一致性與維護性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q4

Q12: 用觸發器/約束與在程式封裝，差異為何？
- A簡: 資料庫側保障寫入正確性；程式封裝同時提升可用性與意圖清晰。兩者可互補，但程式更貼近領域行為。
- A詳: 資料庫觸發器與約束能阻止錯誤資料寫入，是最後防線；但表達複雜規則較受限，且不易與應用層邏輯完全一致。程式封裝則在操作發生當下就強制正確流程，介面更容易表達意圖（如 ComparePassword）。最佳實務常是兩者搭配：關鍵不變條件於資料庫受制約，流程與使用性則在實體封裝內達成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q4

Q13: 以視圖（VIEW）導出 Gender 的優缺點？
- A簡: 優點是一致性好、不需重複存放；缺點是規則複雜時 SQL 難表達，效能與維護可能受限。
- A詳: 視圖可依 SSN 即時計算 Gender，避免兩地維護與不一致。其優點是資料庫端單一事實來源。但當規則較複雜或需與應用層共享相同運算時，SQL 表達與效能可能成為瓶頸；且應用端仍需合成型別（如 enum）。若邏輯跨越多層，將推導邏輯封裝於實體屬性或事件（如 OnSSNChanging）可讓程式更直覺，並保有一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q4

Q14: Partial class 在 EF 中扮演什麼角色？
- A簡: 部分類別讓你在不改動產生碼下擴充實體行為，加入封裝、驗證與輔助方法，維持代碼生成穩定。
- A詳: EF 會產生對應的實體與內容類別。透過 C# 的 partial class，你可於另一檔案為同名類別新增成員，如寫入式 Password 屬性、ComparePassword、或 enum 封裝屬性。這避免直接改動產生碼造成重生覆蓋風險，讓模型更新與自訂行為能各自演進。亦可利用部分方法（如 OnSSNChanging）掛入欄位變更時機。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q1, C-Q4

Q15: Getter/Setter 權限如何影響封裝？
- A簡: 將敏感屬性 Getter/Setter 設為私有，改用公開方法或替代屬性，能限制誤用並維護不變條件。
- A詳: 屬性的可見性決定外界可否任意讀寫。對於敏感或衍生欄位（如 PasswordHash、GenderCode），應避免公開存取，防止外部破壞規則。藉由 private setter、只讀公開屬性、或改以寫入式替代屬性（Password）的組合，表達清楚的意圖與合法操作邊界。這是將資料正確性移到類別內部守護的關鍵手段。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q8, A-Q6

Q16: 為何說 EF 部分達成 OODB 的願景？
- A簡: 當對應做到好，物件行為與狀態由應用端掌控，資料持久化無縫銜接，體驗接近物件資料庫。
- A詳: 物件資料庫（OODB）強調以物件為中心的持久化。EF 雖以關聯式為基礎，但若對應與封裝成熟，開發者幾乎只和物件互動，資料庫成為實作細節。當實體內涵行為（封裝、驗證、計算）且 SaveChanges 穩定同步，整體體驗與 OODB 類似，只是物件存於應用端、關聯持久於資料庫端。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, A-Q4

Q17: 三層式架構中的「斷層」是什麼？
- A簡: 物件導向與關聯式資料庫關注點不同，導致模型與存取方式落差，增加開發與維護負擔。
- A詳: 表現層、商務邏輯層、資料存取層的三層式常見。但物件模型擅長表達行為與抽象，關聯式則以表、關聯與 SQL 為主。兩者語意與操作差異造成「阻抗不匹配」。未妥善處理，容易充斥轉換樣板碼與邏輯分散。ORM（如 EF）正是為縮小此斷層而生。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2

Q18: 範例中的 Object Context 扮演何種角色？
- A簡: 內容物件管理實體的查詢、變更追蹤與提交，提供 Add、GetObjectByKey、SaveChanges 等操作。
- A詳: 在範例中使用 Membership 作為 EF 的內容物件。它負責連線管理、實體物件集合的存取、變更追蹤與交易提交。建立新實體後呼叫 AddToUserSet 加入內容的集合，呼叫 SaveChanges 將變更寫回資料庫；透過 EntityKey 可用主鍵查回對應的實體。這是 EF 應用的基本操作面向。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q8, C-Q5

Q19: Gender 與 GenderCode 在模型中的關係為何？
- A簡: GenderCode 為內部整數碼，隱藏不公開；Gender 對外以 enum 唯讀屬性呈現，值由 SSN 推導同步。
- A詳: 模型中保留 GenderCode 以整數儲存性別，並把其 Getter/Setter 隱藏。對外公開的 Gender 屬性回傳 enum 型別，提升語意清晰並避免任意寫入。當 SSN 改變時，在 OnSSNChanging 中同步計算 GenderCode，確保一致性與防止前端誤用，這是封裝與功能相依落實的例子。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q7

Q20: 什麼是「最小公開介面」原則？
- A簡: 僅暴露完成需求必要的最少方法與屬性，隱藏其餘細節，以降低耦合並保護不變條件。
- A詳: 最小公開介面主張 API 只提供使用者真正需要的能力，其他內部實作與中間結果都不應公開。在實體設計上，像 Password 提供寫入與 ComparePassword 驗證即可；Hash 與演算法名稱屬內部細節。透過此原則，呼叫端更難做錯事，實作也能在不破壞相容性的前提下演進。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q9, C-Q10

### Q&A 類別 B: 技術原理類

Q1: EF 的對應與運作流程是什麼？
- A簡: 以 EDMX 定義模型與對應，產生實體與內容類別；執行時追蹤變更，轉譯查詢與提交到資料庫。
- A詳: EF 透過 EDMX 描述概念模型、儲存模型與對應。設計階段產生實體與 ObjectContext。執行時，內容物件管理連線與實體集合，追蹤屬性變更與關聯。查詢可由 LINQ 或 API 建立，由 EF 翻譯成 SQL；對實體的新增、更新、刪除於 SaveChanges 時轉為相應命令提交。核心組件包含 Entity（資料模型）、ObjectContext（內容）、Mapping（對應）、Change Tracker（變更追蹤）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q18

Q2: 自動產生實體與 partial class 如何協作？
- A簡: 產生碼提供欄位對應與基本行為；partial class 追加封裝、驗證與輔助方法，避免改動產生碼。
- A詳: EF 產生的類別負責屬性對應、關聯與基本生命週期。C# 的 partial class 機制允許在另一檔案為同一類別擴充成員。流程是：保留產生碼不動；在 partial 檔加入寫入式密碼屬性、ComparePassword、enum 包裝屬性，或掛接部分方法（如 OnSSNChanging）。這種分離讓模型重生不會覆蓋自定邏輯，維持穩定演進。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q1

Q3: 在 EF 中封裝敏感欄位的機制為何？
- A簡: 透過私有 Getter/Setter、替代公開屬性與方法、與部分方法攔截變更，將敏感資料隱藏於類別內。
- A詳: 敏感欄位如 PasswordHash 應避免公開。作法包括：將其 Getter/Setter 設私有；提供寫入式 Password 屬性負責計算與存放；提供 ComparePassword 執行檢核；在 On<Property>Changing 勾點實作相依欄位同步（SSN→GenderCode）。核心是以類別內部的步驟封裝流程，對外暴露語意清晰且安全的介面。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q1, C-Q4

Q4: ComparePassword 的運算流程是什麼？
- A簡: 將輸入密碼計算 Hash，與儲存 Hash 逐位比對，長度不同即失敗，相等即驗證通過。
- A詳: 流程包含：1) 以固定演算法（例：HashAlgorithm.Create("MD5")）對輸入字串以特定編碼（例：Unicode）計算位元組陣列；2) 若儲存 Hash 為空或長度不同則失敗；3) 逐位比對每個 byte，不相等即失敗；4) 全數相等則通過。核心組件是 Hash 算法、編碼與位元組陣列比對步驟，封裝在實體方法中避免重複實作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q1

Q5: On<Property>Changing 部分方法的機制是什麼？
- A簡: EF 在屬性變更時呼叫對應部分方法，讓你插入自訂邏輯，如在 SSN 改變時同步性別碼。
- A詳: EF 產生的實體支援部分方法 OnXxxChanging(value)。當屬性被設定，框架會在指派前呼叫此方法（若已實作），可用來驗證或推導相依屬性。範例在 OnSSNChanging 中解析身分證字號並同步 GenderCode。關鍵步驟：辨識目標屬性、在 partial class 中提供同名簽章、於方法內實作推導或檢核邏輯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, A-Q11

Q6: 以 enum 包裝整數欄位的原理是什麼？
- A簡: 以只讀屬性將 int 轉型為 enum 提供語意化存取，避免任意寫入，內部仍以原始碼儲存。
- A詳: 資料庫中常以整數存放代碼。實體可對外公開一個 Getter：return (MyEnum)this.CodeInt；如此呼叫端看到的是語意化型別，降低錯用風險。若需禁止外部改動，僅提供 Getter。這種包裝兼顧儲存效率與程式語意清楚，是封裝的一環。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, A-Q19

Q7: EntityKey 與 GetObjectByKey 如何定位實體？
- A簡: 以實體集名稱與主鍵值組成 EntityKey，再由內容物件的 GetObjectByKey 取回對應實體。
- A詳: 在未使用 LINQ 的情境下，可直接建立 EntityKey（包含容器名.實體集、鍵名與鍵值），呼叫 ObjectContext.GetObjectByKey 取回已追蹤或從資料庫載入的實體。流程：構建鍵→查找內容的快取→必要時查庫載入→回傳實體。這是依鍵快速定位的基礎 API。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, C-Q6

Q8: SaveChanges 的改動追蹤與提交流程？
- A簡: 內容物件追蹤新增/修改/刪除狀態，SaveChanges 將其轉為對應 SQL 指令提交至資料庫。
- A詳: ObjectContext 追蹤實體狀態與屬性變更。當呼叫 SaveChanges，框架會為每個狀態產生適當命令（INSERT/UPDATE/DELETE），依關聯與順序處理提交。成功後更新實體狀態為 Unchanged。這個流程讓開發者專注於物件操作，提交交給 EF 處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q5

Q9: 為什麼選擇在程式而非 SQL 計算密碼 Hash？
- A簡: 邏輯集中於實體封裝，避免依賴資料庫函數，維持一致與可測試性，並清楚表達安全流程。
- A詳: 雖然資料庫也能提供雜湊函數，但把運算放於程式端的實體方法有幾個好處：與 ComparePassword 一致封裝；易於單元測試；避免多處語言實作造成不一致；減少資料庫邏輯耦合。當資料流經實體即完成合法化與驗證，能在進入資料庫前先把關。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2

Q10: 以屬性 Setter 觸發內部邏輯的設計原理？
- A簡: 寫入屬性不直接暴露欄位，改由 Setter 執行驗證與推導流程，確保狀態一致與不變條件。
- A詳: 屬性 Setter 是插入不變條件檢查與相依欄位同步的自然入口。例如 Password 的 Setter 進行 Hash 計算與儲存；設定 SSN 的 Setter 觸發 OnSSNChanging 以同步性別碼。如此對外仍是簡單 API，對內則集中流程，讓狀態在寫入時即被合法化，減少錯誤傳遞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q4

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 EF 實體中實作寫入式的 Password 屬性？
- A簡: 在實體的 partial class 加入僅 Setter 的 Password，Setter 內計算 Hash 並寫入私有欄位。
- A詳: 步驟：1) 確認產生碼中的 PasswordHash Getter/Setter 設為私有（或僅內部使用）；2) 建立同名實體的 partial class；3) 新增 public string Password { set { this.PasswordHash = ComputePasswordHash(value); } }；4) 在類別內提供私有 ComputePasswordHash 方法。程式碼片段：public string Password { set { this.PasswordHash = ComputePasswordHash(value); } }。注意：避免公開 Hash；更新模型時勿覆蓋自訂檔；保持演算法與編碼一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q2, D-Q3

Q2: 如何在 partial class 中封裝 Hash 計算邏輯？
- A簡: 以私有方法 ComputePasswordHash 接收明碼，使用 HashAlgorithm 計算並回傳位元組陣列。
- A詳: 實作步驟：1) 在 partial class 添加 private byte[] ComputePasswordHash(string password)；2) 若字串為空，回傳 null；3) 使用 HashAlgorithm.Create("MD5") 與 Encoding.Unicode.GetBytes(password) 計算；4) 由 Password Setter 與 ComparePassword 共同呼叫。程式碼：private byte[] ComputePasswordHash(string p){ if (string.IsNullOrEmpty(p)) return null; return HashAlgorithm.Create("MD5").ComputeHash(Encoding.Unicode.GetBytes(p)); }。注意：統一演算法與編碼，避免不同端不一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, D-Q1

Q3: 如何撰寫 ComparePassword 方法並進行驗證？
- A簡: 比對輸入密碼的 Hash 與儲存 Hash，先檢查長度，再逐位比較，全部相等表示通過。
- A詳: 實作步驟：1) public bool ComparePassword(string text){ var hash = ComputePasswordHash(text); if (this.PasswordHash == null) return false; if (hash.Length != this.PasswordHash.Length) return false; for (int i=0;i<hash.Length;i++){ if (hash[i]!=this.PasswordHash[i]) return false; } return true; }；2) 從內容物件取回使用者後呼叫 user.ComparePassword(input)。注意：避免外部直接接觸 Hash；確保 ComputePasswordHash 與 Setter 用相同演算法與編碼；必要時處理 null。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, D-Q1

Q4: 如何同步 SSN 與 GenderCode 並公開唯讀 Gender？
- A簡: 在 OnSSNChanging 推導性別碼寫回 GenderCode，並以 enum Gender 只讀屬性回傳轉型結果。
- A詳: 實作步驟：1) 在 partial class 加入 partial void OnSSNChanging(string value){ this.GenderCode = int.Parse(value.Substring(1,1)); }；2) 將 GenderCode Getter/Setter 設為私有；3) 定義 enum GenderCodeEnum；4) public GenderCodeEnum Gender { get { return (GenderCodeEnum)this.GenderCode; } }。注意：確保字串格式檢查；Gender 只提供 Getter，避免外部改動；統一推導規則集中於此。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q10, A-Q19

Q5: 如何建立新使用者帳號並保存至資料庫？
- A簡: 使用內容物件建立實體、設定屬性（含 Password 與 SSN）、加入集合並呼叫 SaveChanges。
- A詳: 步驟：1) using(var ctx=new Membership()){ var u=new User(); u.ID="andrew"; u.PasswordHint="My Password: 12345"; u.Password="12345"; u.SSN="A123456789"; ctx.AddToUserSet(u); ctx.SaveChanges(); }；關鍵點：使用寫入式 Password 執行 Hash；SSN 觸發同步性別碼；確保主鍵唯一。注意：內容物件生命週期用 using；避免直接操作 PasswordHash。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, B-Q8

Q6: 如何驗證使用者密碼是否正確？
- A簡: 以 EntityKey 取得使用者實體，呼叫 ComparePassword(input) 回傳布林結果並處理。
- A詳: 步驟：1) using(var ctx=new Membership()){ var key=new EntityKey("Membership.UserSet","ID","andrew"); var user=ctx.GetObjectByKey(key) as User; string input="123456"; bool ok=user.ComparePassword(input); }；關鍵：以 ComparePassword 集中驗證；不要外部比對 Hash。注意：確保鍵值正確、處理找不到的情況；必要時包裝服務方法回傳清楚的驗證結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q4, D-Q1

Q7: 如何公開 enum 型別的 Gender 屬性提升語意？
- A簡: 定義 GenderCodeEnum，實作只讀 Gender 屬性回傳 (GenderCodeEnum)GenderCode，隱藏整數欄位。
- A詳: 步驟：1) public enum GenderCodeEnum:int{ FEMALE=0, MALE=1 }；2) 在 partial class 定義 public GenderCodeEnum Gender { get { return (GenderCodeEnum)this.GenderCode; } }；3) 將 GenderCode 對外隱藏。好處：呼叫端不再碰整數代碼，語意清楚且難以誤設。注意：保持 enum 與資料庫碼一致；如需顯示字串，於 UI 或轉換層處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, A-Q19

Q8: 如何將敏感欄位的 Getter/Setter 設為私有？
- A簡: 於產生碼調整屬性存取子為 private，或以替代公開屬性避免外部使用原屬性，並維持產生碼不改動。
- A詳: 作法一：直接將產生碼中屬性 Getter/Setter 設為 private（需注意重生覆蓋）；作法二：保留公開但不在外使用，改以 partial class 暴露替代屬性與方法，並以檔案規範與程式碼分析避免誤用。最佳實務是盡量不改產生碼，集中於 partial class 包裝。注意：若修改產生碼，更新模型需再行調整。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q2, D-Q6

Q9: 如何組織 EF 專案檔案，利於擴充與維護？
- A簡: 將 EDMX 與產生碼分開，為每個實體建立對應 partial 檔，集中封裝、驗證與輔助方法。
- A詳: 建議：1) 將 Model.edmx 與產生的 .cs 放於資料層；2) 為 User 等實體建立 User.Partial.cs，加入 Password、ComparePassword、OnSSNChanging 等；3) 以檔名規約與命名空間分隔產生與自訂碼；4) 撰寫單元測試驗證封裝邏輯。注意：避免在產生碼中加入業務邏輯，降低重生風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q1

Q10: 如何以最小介面對外暴露領域邏輯？
- A簡: 用方法與寫入式屬性表達需求（設定、驗證），隱藏資料欄位與中間細節，維持介面穩定。
- A詳: 實作：1) 寫入式 Password 代表「設定密碼」；2) ComparePassword 表達「驗證密碼」；3) Gender 為唯讀推導屬性；4) 隱藏 PasswordHash、GenderCode 等實作細節。這樣外部只能做對的事，內部可自由演進（改演算法、加驗證）而不破壞呼叫端。注意：文件清楚說明可用介面與禁用的直接欄位。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, C-Q3

### Q&A 類別 D: 問題解決類（10題）

Q1: 密碼驗證總是失敗，如何診斷？
- A簡: 檢查編碼與演算法一致、Hash 長度與 null 狀態、ComparePassword 實作是否逐位比對正確。
- A詳: 症狀：ComparePassword 一律回傳 false。可能原因：1) 計算 Hash 的 Encoding 與演算法不一致；2) 儲存 Hash 為 null；3) 比對邏輯錯誤或長度未檢查；4) 外部直接操作 Hash 造成污染。解決：統一使用 HashAlgorithm.Create("MD5") 與 Encoding.Unicode；在 ComparePassword 先檢查 null 與長度，再逐位比對；將 Hash Getter/Setter 私有化。預防：集中計算於 partial class，撰寫單元測試覆蓋正常與異常案例。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, C-Q2, C-Q3

Q2: SSN 與 Gender 不一致，怎麼處理？
- A簡: 利用 OnSSNChanging 同步 GenderCode，對外只提供唯讀 Gender，避免手動設定造成不一致。
- A詳: 症狀：資料顯示與 SSN 規則不符。原因：直接設定 GenderCode、缺少同步邏輯、或未觸發 OnSSNChanging。解決：在 partial class 實作 OnSSNChanging 推導 GenderCode；隱藏 GenderCode Setter，刪除對外設定入口；重新儲存一遍以觸發同步。預防：將 Gender 對外唯讀；在建立或更新時僅設定 SSN 觸發規則，並撰寫測試確保規則一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q4, A-Q11

Q3: PasswordHash 對外暴露導致安全風險，如何修補？
- A簡: 將 Hash 屬性存取私有化，改以 Password Setter 與 ComparePassword 對外提供設定與驗證。
- A詳: 症狀：外部程式能讀取/寫入 Hash。風險：Hash 泄漏、被誤設或跳過流程。解決：調整屬性存取為 private；提供 Password 寫入與 ComparePassword；全面改用新介面；掃描程式碼移除對 Hash 的直接引用。預防：以 partial class 集中封裝；加上程式碼規範與檢查；撰寫測試防回歸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q8, A-Q8

Q4: SaveChanges 擲 SqlException，可能原因與對策？
- A簡: 常見為違反約束或不一致資料；檢查必填欄位、相依欄位同步、與資料庫約束規則。
- A詳: 症狀：SaveChanges 失敗，拋出資料庫例外。原因：NULL/長度超限、鍵值重複、SSN/Gender 不一致等。對策：確保建立與更新時使用封裝介面（Password、SSN→GenderCode 同步）；檢查主鍵與必填欄位；回看資料庫約束訊息定位欄位。預防：在實體層加入驗證；資料庫側保留必要約束作為最後防線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q5

Q5: GetObjectByKey 找不到或擲例外，怎麼診斷？
- A簡: 確認實體集名稱、鍵名與鍵值正確，內容物件狀態有效，必要時改用查詢或檢查模型對應。
- A詳: 症狀：GetObjectByKey 回傳 null 或擲例外。原因：鍵名拼錯、容器/實體集名稱不符、鍵值不存在、內容已釋放。對策：檢查 new EntityKey("Membership.UserSet","ID",value) 參數；確認內容物件 using 範圍；必要時以 LINQ 或其他 API 查找。預防：封裝查找邏輯於存取層，避免魔字串散落。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q6

Q6: 重新產生 EDMX 後私有 Setter 變回公開，如何避免？
- A簡: 避免改動產生碼；將封裝邏輯放於 partial class，並以規範禁止直接使用敏感屬性。
- A詳: 症狀：模型更新導致存取子回復預設。原因：改了產生碼被重生覆蓋。對策：把封裝邏輯全部移到 partial class；原屬性即便公開，也不要在外部使用，提供替代 API；以程式碼審查與分析工具防止誤用。預防：不修改產生碼；若必要，記錄變更並在重生後套用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, B-Q2

Q7: ComparePassword 效能不佳時如何優化？
- A簡: 避免重複轉碼與建立演算法實例，重用方法封裝，僅在必要時計算與比較。
- A詳: 症狀：大量驗證時延遲。原因：反覆建立 HashAlgorithm、重複編碼轉換、無條件執行比對。對策：封裝 ComputePasswordHash，避免重複程式；集中建立與處理；在流程上先檢查長度再逐位比對。預防：撰寫效能測試，確保在需求量下仍達標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q2, C-Q3

Q8: 視圖計算與程式封裝邏輯不一致時怎麼辦？
- A簡: 以單一事實來源為準，建議統一在實體封裝推導，移除或同步更新視圖邏輯。
- A詳: 症狀：不同層得到不同性別值。原因：視圖與程式推導規則不一致。對策：決定單一來源（建議實體封裝）；更新或移除視圖中的重複邏輯；建立對應測試確保一致。預防：規劃規則的唯一實作地點，其他層只消費結果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q4

Q9: 若要更換密碼 Hash 演算法，如何不破壞介面？
- A簡: 保持 Password 與 ComparePassword 介面不變，在 partial class 內替換 ComputePasswordHash 實作。
- A詳: 症狀：需替換雜湊演算法。風險：外部相依介面變更。作法：維持 Password Setter 與 ComparePassword 方法簽章不變，僅於 ComputePasswordHash 內改變演算法實作；更新相關測試確保相容。預防：從一開始即封裝實作細節，對外只暴露意圖明確的操作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, A-Q20

Q10: 如何預防前端寫出違反封裝的程式碼？
- A簡: 以替代 API 封裝行為，限制原屬性使用，配合程式碼審查、測試與文件明確規範。
- A詳: 症狀：前端直接設定 Hash 或 GenderCode。原因：缺乏清楚 API 與規範。對策：提供明確方法（Password Setter、ComparePassword、唯讀 Gender），並在程式碼審查與靜態分析中禁止敏感屬性使用；以單元測試與文件強化規範。預防：從設計起即落實最小介面原則，減少可誤用的開口。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 ORM（物件關聯對應）？
    - A-Q2: 為何需要 ORM 的對應機制？
    - A-Q3: 什麼是 Entity Framework？
    - A-Q4: EF 的核心目標是什麼？
    - A-Q5: 什麼是 Entity（實體）？
    - A-Q6: 什麼是封裝（Encapsulation）？
    - A-Q7: 為什麼在 EF 中需要強調封裝？
    - A-Q8: 直接暴露 PasswordHash 有何風險？
    - A-Q9: 密碼處理應提供哪些最小介面？
    - A-Q14: Partial class 在 EF 中扮演什麼角色？
    - A-Q15: Getter/Setter 權限如何影響封裝？
    - A-Q18: 範例中的 Object Context 扮演何種角色？
    - B-Q4: ComparePassword 的運算流程是什麼？
    - C-Q5: 如何建立新使用者帳號並保存至資料庫？
    - C-Q6: 如何驗證使用者密碼是否正確？

- 中級者：建議學習哪 20 題
    - A-Q10: 台灣 SSN 與性別（Gender）為何是相依欄位？
    - A-Q11: 什麼是功能相依（Functional Dependency）？
    - A-Q12: 用觸發器/約束與在程式封裝，差異為何？
    - A-Q13: 以視圖（VIEW）導出 Gender 的優缺點？
    - A-Q19: Gender 與 GenderCode 在模型中的關係為何？
    - B-Q1: EF 的對應與運作流程是什麼？
    - B-Q2: 自動產生實體與 partial class 如何協作？
    - B-Q3: 在 EF 中封裝敏感欄位的機制為何？
    - B-Q5: On<Property>Changing 部分方法的機制是什麼？
    - B-Q6: 以 enum 包裝整數欄位的原理是什麼？
    - B-Q7: EntityKey 與 GetObjectByKey 如何定位實體？
    - B-Q8: SaveChanges 的改動追蹤與提交流程？
    - C-Q1: 如何在 EF 實體中實作寫入式的 Password 屬性？
    - C-Q2: 如何在 partial class 中封裝 Hash 計算邏輯？
    - C-Q3: 如何撰寫 ComparePassword 方法並進行驗證？
    - C-Q4: 如何同步 SSN 與 GenderCode 並公開唯讀 Gender？
    - C-Q7: 如何公開 enum 型別的 Gender 屬性提升語意？
    - C-Q9: 如何組織 EF 專案檔案，利於擴充與維護？
    - D-Q1: 密碼驗證總是失敗，如何診斷？
    - D-Q2: SSN 與 Gender 不一致，怎麼處理？

- 高級者：建議關注哪 15 題
    - A-Q16: 為何說 EF 部分達成 OODB 的願景？
    - A-Q17: 三層式架構中的「斷層」是什麼？
    - A-Q20: 什麼是「最小公開介面」原則？
    - B-Q9: 為什麼選擇在程式而非 SQL 計算密碼 Hash？
    - B-Q10: 以屬性 Setter 觸發內部邏輯的設計原理？
    - C-Q8: 如何將敏感欄位的 Getter/Setter 設為私有？
    - C-Q10: 如何以最小介面對外暴露領域邏輯？
    - D-Q3: PasswordHash 對外暴露導致安全風險，如何修補？
    - D-Q4: SaveChanges 擲 SqlException，可能原因與對策？
    - D-Q5: GetObjectByKey 找不到或擲例外，怎麼診斷？
    - D-Q6: 重新產生 EDMX 後私有 Setter 變回公開，如何避免？
    - D-Q7: ComparePassword 效能不佳時如何優化？
    - D-Q8: 視圖計算與程式封裝邏輯不一致時怎麼辦？
    - D-Q9: 若要更換密碼 Hash 演算法，如何不破壞介面？
    - D-Q10: 如何預防前端寫出違反封裝的程式碼？