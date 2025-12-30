---
layout: synthesis
title: "難搞的 Entity Framework - 跨越 Context 的查詢"
synthesis_type: faq
source_post: /2009/01/20/tricky-entity-framework-cross-context-queries/
redirect_from:
  - /2009/01/20/tricky-entity-framework-cross-context-queries/faq/
---

# 難搞的 Entity Framework - 跨越 Context 的查詢

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Entity Framework（EF）？
- A簡: EF 是 .NET 的 ORM，透過 .edmx（含 CSDL/SSDL/MSL）將關聯式資料庫映射為物件，支援 LINQ 與 eSQL 查詢與變更追蹤。
- A詳: Entity Framework 是微軟在 .NET 平台上的物件關聯對應（ORM）解決方案。它以 .edmx 模型描述概念模型（CSDL）、儲存模型（SSDL）與對應（MSL），讓開發者以物件方式操作資料庫。EF 提供 LINQ to Entities 與 eSQL 兩種查詢語言，並透過 ObjectContext（或 DbContext）進行物件狀態追蹤與交易管理。本文背景位於 EF v1（.NET 3.5 SP1），在大型資料庫與跨 Context 的情境下，有多項限制與對策需要理解。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, A-Q7, B-Q1

A-Q2: 什麼是 .edmx？
- A簡: .edmx 是 EF 的模型檔，封裝 CSDL、SSDL、MSL 與設計器資訊，支援視覺化設計與程式碼產生。
- A詳: .edmx 是 EF 的統一模型描述檔，內含三個關鍵片段：CSDL（概念模型）、SSDL（儲存模型）、MSL（對應），以及設計器所需的額外資訊。Visual Studio 設計器可由資料庫逆向產生 .edmx，再自動產生對應的 ObjectContext 與實體類別。大型資料庫常需將模型拆分為多個 .edmx，以降低單一模型的複雜度與建置壓力，但也會引入多個 Context 與跨模型查詢的限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q10, B-Q9

A-Q3: 什麼是 ObjectContext？
- A簡: ObjectContext 是 EF v1 的核心工作單元，負責查詢、追蹤、交易與 SaveChanges。
- A詳: 在 EF v1 中，ObjectContext 代表一個工作單元，封裝連線、MetadataWorkspace 與 ObjectStateManager，提供查詢（eSQL、LINQ）、物件變更追蹤與 SaveChanges 等能力。每個 .edmx 通常會產出一個衍生的 Context 類別。當模型拆為多個 .edmx 時，就會有多個 Context，需分別 SaveChanges，且無法跨 Context 查詢或導覽。本文的關鍵在於透過「單一 ObjectContext 載入多組 Metadata」化解這些限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q8, C-Q4

A-Q4: 什麼是 EntityConnectionString？
- A簡: 是 EF 的連線字串，含 Metadata（CSDL/SSDL/MSL 路徑）與底層資料庫連線，可合併多組 Metadata。
- A詳: EntityConnectionString 是 EF 建立 ObjectContext 所需的連線資訊，形式為「metadata=...;provider=...;provider connection string=...」。其中 metadata 參數指定 CSDL、SSDL、MSL 的位置（常見 res://*/Model.csdl|...），可引用內嵌資源或檔案。本文重點在於 metadata 支援「多組檔案」串接，讓單一 Context 同時載入多個 .edmx 的定義，以便進行跨模型的 eSQL JOIN 與統一變更管理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q5, C-Q3

A-Q5: CSDL、SSDL、MSL 的定義與差異？
- A簡: CSDL 描述概念模型，SSDL 描述儲存模型，MSL 定義兩者對應；三者合併支撐 ORM 運作。
- A詳: CSDL（Conceptual Schema Definition Language）定義實體、關聯與概念層型別；SSDL（Store Schema Definition Language）描述資料庫中的資料表、欄位與關聯；MSL（Mapping Specification Language）橋接 CSDL 與 SSDL，指定概念實體如何映射至資料表與欄位。EF 運作時以這三者構成的 MetadataWorkspace 作為查詢轉譯與物件物化的依據。理解三者是掌握跨模型、跨組件運作的基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q5

A-Q6: 什麼是 eSQL（Entity SQL）？
- A簡: eSQL 是 EF 的查詢語言，類似 SQL，對概念模型操作，支援跨 EntitySet 的 JOIN。
- A詳: eSQL 是針對 EF 概念模型設計的宣告式查詢語言。它以實體型別、實體集（EntitySet）與關聯為操作對象，可執行投影、篩選與 JOIN。本文的關鍵在於，當以單一 ObjectContext 載入多組模型 Metadata 後，eSQL 可以在同一個 MetadataWorkspace 內對不同 .edmx 來源的 EntitySet 進行 JOIN，化解原本跨 Context 不支援的限制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q4, C-Q5

A-Q7: 什麼是 LINQ to Entities？
- A簡: LINQ to Entities 以 C# 查詢語法操作 EF 模型，編譯期型別檢查，最終轉譯為查詢命令。
- A詳: LINQ to Entities 允許以 C# 的 LINQ 語法對 EF 模型進行查詢。一般情況依賴強型別 Context 上的 DbSet/EntitySet 屬性。但當以「單一 Context 載入多組 Metadata」時，強型別屬性可能不存在，需改用 ObjectContext.CreateQuery<T>("Container.Set") 產生查詢來源，再以 LINQ 組合查詢。這是本文對 LINQ 的關鍵點：仍可用，但需手動建立實體集。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q6, D-Q6

A-Q8: 什麼是 AssociationSet 與 Navigation Property？
- A簡: AssociationSet 表示關聯的實體集，Navigation Property 讓實體間可導覽；無法跨不同 Context。
- A詳: 在 EF，Association 定義實體間關聯，AssociationSet 是實體集層級的關聯集合；Navigation Property 以物件導覽的方式表達關聯存取。然而在 EF v1，這些關聯被限制在單一模型與 Context 的範圍內，跨 .edmx 的實體無法藉由 Navigation Property 直接導覽。本文的解方是以單一 ObjectContext 載入多組 Metadata，改用 eSQL JOIN 或手動查詢取代跨 Context 導覽。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5, D-Q4

A-Q9: 為什麼大型 Schema 會造成 ORM 的困難？
- A簡: 大量資料表與關聯使模型臃腫、建置慢、設計器不穩，跨模組協作與查詢也更複雜。
- A詳: 大型應用常有上百個資料表與檢視，加上歷史演進導致架構複雜。單一 .edmx 容納所有實體會使設計器緩慢、建置易失敗，維護困難。為降低複雜度，常拆分為多個 .edmx 與模組化封裝；但隨之而來的是多個 Context、跨 Context 查詢不支援、關聯與 SaveChanges 分散的問題，需要新的架構策略加以解決。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q11, D-Q2

A-Q10: 為什麼要把模型拆成多個 .edmx？
- A簡: 分拆降低單一模型複雜度，提升可維護性，支援模組化與獨立開發與部署。
- A詳: 將大型資料庫模型依業務模組或功能區隔拆為多個 .edmx，可讓各模組獨立演進、避免設計器過載、縮短建置時間、降低合併衝突。每個 .edmx 與其業務邏輯封裝在各別組件（assembly），利於邊界清晰與團隊協作。缺點是產生多個 Context，跨模型運算受限，需要透過單一 Context 載入多組 Metadata 的技術路徑彌補。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q9, C-Q1

A-Q11: 為什麼 EF v1 不支援跨 Context 的查詢與關聯？
- A簡: 因 Context 隔離其 Metadata 與物件追蹤範圍，跨界資訊不共享，導致查詢與導覽失效。
- A詳: EF v1 的 ObjectContext 是查詢轉譯與狀態追蹤的界線。每個 Context 擁有自己的 MetadataWorkspace 與 ObjectStateManager，僅認得自身載入的 CSDL/SSDL/MSL。不同 Context 的實體彼此不相容，無法直接JOIN或導覽，也必須各自 SaveChanges。這是跨 Context 操作報錯的根本原因。本文解法即是把多組 Metadata 合併到單一 Context 的範圍內。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q1

A-Q12: LINQ 與 eSQL 在跨 Context 上有何差異？
- A簡: 在多 Context 下兩者皆不支援；合併 Metadata 後，eSQL可直接 JOIN，LINQ須用 CreateQuery 建立來源。
- A詳: 若維持多個 Context，LINQ 與 eSQL 都無法跨 Context 查詢。當改為單一 Context 載入多組 Metadata，eSQL 可用完整容器.實體集名稱直接 JOIN；LINQ 仍可用，但需以 ObjectContext.CreateQuery<T>("Container.Set") 手動建立查詢來源，再用 LINQ 寫投影與條件。差異主要在入口方式與型別化支援程度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q7, C-Q5, C-Q6

A-Q13: 為什麼合併多組 Metadata 到連線字串能解決跨模型查詢？
- A簡: 單一 Context 載入多模型後，共用同一 MetadataWorkspace，跨模型的 EntitySet 得以同域查詢。
- A詳: 將多組 CSDL/SSDL/MSL 以 metadata 參數串接於 EntityConnectionString，使 ObjectContext 啟動時載入所有模型片段，匯聚成同一 MetadataWorkspace。如此，eSQL 與 LINQ 查詢時，所有 EntitySet 與型別位於同一語意空間，JOIN 與組合查詢自然可行。同時也統一物件追蹤與 SaveChanges，一次提交跨模組的變更。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q3, C-Q4

A-Q14: 什麼是「以模組封裝 .edmx 與邏輯」的做法？
- A簡: 每個業務模組各有 .edmx 與其邏輯，封裝成獨立組件，獨立開發、部署與維護。
- A詳: 模組化將功能域切分，每個模組擁有其 .edmx（含 CSDL/SSDL/MSL）與存取邏輯（Repository/Service），編譯為獨立 assembly。部署時，以 EntityConnectionString 的 metadata=res://*/... 通配載入多模組資源，不需重編其他模組。這兼顧大型系統的可維護性與跨模組查詢需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q8

A-Q15: 單一 ObjectContext 跨多模型的核心價值是什麼？
- A簡: 允許跨模型 eSQL JOIN、統一變更追蹤與提交，並維持模組獨立開發與部署。
- A詳: 將多組 Metadata 置於同一 ObjectContext 範圍，共享 MetadataWorkspace 與狀態管理。好處包括：跨模組 eSQL JOIN、LINQ 查詢可行；導入單次 SaveChanges；維持模組 .edmx 與邏輯獨立封裝、無需連動重編。此作法在大型 Schema、長期演進的系統中特別關鍵，能在可維護性與查詢能力間取得平衡。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q3, C-Q4

### Q&A 類別 B: 技術原理類

B-Q1: EF 的 O/R Mapping 背後機制是什麼？
- A簡: 以 MetadataWorkspace 載入 CSDL/SSDL/MSL，將查詢轉譯為資料提供者命令，物化為實體並追蹤。
- A詳: EF 啟動時載入三份模型描述：CSDL、SSDL 與 MSL，組成 MetadataWorkspace。查詢（eSQL/LINQ）被解析並轉換為命令樹，再交由對應的 ADO.NET Provider 產生 SQL 執行。查詢結果依 Mapping 規則物化為實體，ObjectStateManager 處理狀態與關聯。理解此流程，有助於掌握為何跨 Context 受限，以及合併 Metadata 為何有效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q12

B-Q2: res:// 路徑如何載入 .edmx 內的 CSDL/SSDL/MSL？
- A簡: res:// 指向組件內嵌資源，支援通配符搜尋，讓 EF 從已載入組件解析模型片段。
- A詳: 當 .edmx 片段（.csdl/.ssdl/.msl）設為 Embedded Resource，metadata=res://*/Model.csdl 讓 EF 透過組件資源流讀取。* 通配可跨已載入的 assemblies 搜尋相符資源，避免硬編名稱。這是實現「新增模組免重編其他模組」的關鍵，使連線字串能自動拾取新加入的模型資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q10, C-Q2

B-Q3: ObjectContext 以 EntityConnection 建構時如何運作？
- A簡: 以含多組 Metadata 的 EntityConnection 啟動，建立共享的 MetadataWorkspace 與狀態管理。
- A詳: ObjectContext 可接受 EntityConnection 或連線字串。當使用者提供含多組 CSDL/SSDL/MSL 的 metadata 參數時，EF 將載入所有片段並合併至單一 MetadataWorkspace。此 Context 之下的查詢與物件追蹤共享同一空間，從而可以在邏輯上視多個模型為一體運作，解鎖跨模型 eSQL 與統一 SaveChanges 的能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q13, C-Q4

B-Q4: eSQL 如何在單一 Context 中跨模型運作？
- A簡: eSQL 以「容器.實體集」為單位，在同一 MetadataWorkspace 內可直接 JOIN 不同模型的實體集。
- A詳: 當多組 Metadata 被載入同一 Context，模型會有多個 EntityContainer。eSQL 查詢可用全名（[Container].[EntitySet]）指定來源，再進行 JOIN。例如：FROM A.Orders o JOIN B.Customers c ON o.CustId=c.Id。因兩者共屬同一 MetadataWorkspace，查詢分析與轉譯能辨識並產生合適的命令樹與 SQL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q5, D-Q7

B-Q5: 多組 Metadata 的載入流程與關鍵步驟為何？
- A簡: 串接多個 csdl/ssdl/msl 路徑，建立 EntityConnection，再以該連線建構 ObjectContext。
- A詳: 步驟：1) 在連線字串的 metadata 參數中以 | 串接多組 csdl/ssdl/msl（可用 res://*/…）；2) 指定 provider 與其資料庫連線字串；3) 使用 EntityConnectionStringBuilder 或手組字串；4) new EntityConnection 並開啟；5) 以該連線建構 ObjectContext。完成後，Context 共享所有模型片段。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, C-Q3, C-Q4

B-Q6: 為何合併模型後 LINQ 需用 CreateQuery<T>()？
- A簡: 因缺少單一強型別 Context 的集合屬性，需以 CreateQuery 提供「容器.實體集」作為 LINQ 來源。
- A詳: 多模型合併通常不再使用單一 .edmx 自動生成的強型別 Context 屬性（如 Customers）。為查詢來源，需以 CreateQuery<T>("[Container].[Set]") 建立 IQueryable<T>，再應用 LINQ 運算子。這樣可保留型別安全與延遲查詢，同時跨模型組合來源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q6, D-Q6

B-Q7: 為什麼 AssociationSet 無法跨 Context？
- A簡: 關聯定義與解析以 Context 的 Metadata 為界，跨 Context 缺乏共享語意與追蹤，導覽失效。
- A詳: Association 與其 Mapping 存於 MetadataWorkspace，與 Context 綁定。跨 Context 的實體彼此不在同一關聯空間，EF 無法解析與維護其關聯一致性與外鍵同步，導致 Navigation Property 無法跨越。合併策略將關聯定義置於同一 Context，改以查詢（eSQL/LINQ）顯式結合資料，繞開此限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, D-Q4

B-Q8: 為何多 Context 需各自 SaveChanges？
- A簡: 每個 Context 有自己的 ObjectStateManager 與交易範圍，必須各自提交才能持久化。
- A詳: ObjectStateManager 負責追蹤實體新增、修改、刪除。不同 Context 的狀態追蹤與連線、交易互不相干。即便對同一資料庫，兩個 Context 的變更也不會彼此可見或自動協調，故需各自呼叫 SaveChanges。單一 Context 合併後可統一提交，降低一致性風險與程式複雜度。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q15, C-Q7

B-Q9: .edmx 內嵌資源與組件封裝如何設計？
- A簡: 將 csdl/ssdl/msl 設為 Embedded Resource，與模組邏輯同組件封裝，利於獨立部署。
- A詳: 在每個模組專案中，將從 .edmx 分離出的 csdl/ssdl/msl 標記為 Embedded Resource，並保留自動產生的實體類別與必要邏輯。部署時，各模組 DLL 皆攜帶自己的模型資源，主應用以 res://*/ 通配載入所有資源，實現模組化、可插拔的模型組合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q2, C-Q8

B-Q10: res:// 的通配符如何支援免重編擴充？
- A簡: 通配符會掃描已載入組件資源，新增模組只要載入其 DLL，即可被連線字串拾取。
- A詳: metadata=res://*/ModelX.csdl 的 * 會在 AppDomain 中已載入的 assemblies 內搜尋匹配資源。當加入新模組 DLL 並載入後，其內嵌的模型資源會自動符合通配規則，無需修改或重編其他模組。此特性是達成「新增模組免重編」的實務基礎。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, C-Q8, D-Q9

B-Q11: 多個 EntityContainer 名稱如何影響查詢解析？
- A簡: 多模型會有多個容器，查詢需以「容器.實體集」明確指名，避免同名衝突。
- A詳: 合併多模型後，可能存在多個 EntityContainer 與同名 EntitySet。eSQL 與 CreateQuery 需提供全名 [Container].[EntitySet] 才能正確綁定來源。命名規範與前綴是避免解析歧義的最佳實踐，否則易出現「無效的實體集名稱」錯誤。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q5, C-Q6, D-Q7

B-Q12: eSQL 的執行流程與核心組件？
- A簡: eSQL 解析為命令樹，經 Mapping 與 Provider 產生 SQL 執行，結果物化後由狀態管理追蹤。
- A詳: eSQL 查詢先經語法解析與語意綁定，形成命令樹；透過 MetadataWorkspace 與 MSL 完成概念至儲存的轉譯；交由 ADO.NET Provider 生成 SQL 並執行；回傳資料以 Mapping 物化為實體或匿名投影，ObjectStateManager 追蹤實體狀態。此管線在合併模型時同樣適用，差別在於 Workspace 收納了更多片段。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q1, B-Q4

B-Q13: 強型別 Context 與通用 ObjectContext 的差異？
- A簡: 強型別 Context 提供集合屬性與方法；通用 ObjectContext 靠 CreateQuery/AddObject 指名集合。
- A詳: 單一 .edmx 產生的強型別 Context 具備型別安全的實體集屬性與新增方法（如 AddToOrders）。但在多模型合併時，多以通用 ObjectContext 搭配 CreateQuery<T>("Container.Set") 與 AddObject("Container.Set", entity) 操作。前者易用，後者彈性高且適合跨模型組合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q6, C-Q7

B-Q14: 新增模組為何不需重編其他模組？
- A簡: 模型與邏輯封裝於獨立組件，主程式以通配 metadata 載入，僅需載入新 DLL 即可。
- A詳: 各模組將 csdl/ssdl/msl 內嵌於自身 DLL，主應用的連線字串使用 res://*/ 通配。當新增模組時，只要部署並載入該 DLL，EF 即能發現其資源並合併至 Workspace。既無 API 簽名變動，也無靜態相依，故不需重編其他模組。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, B-Q10, C-Q8

B-Q15: 合併模型的風險與限制是什麼？
- A簡: 可能引發命名衝突、載入時間增加、偵錯難度提升，需良好命名與測試策略。
- A詳: 將多組 Metadata 合併雖帶來跨模型查詢與統一追蹤，但也可能遇到：EntityContainer/EntitySet 同名衝突、模型載入時間與記憶體增加、錯誤定位分散、設計器操作分離。需建立命名規範、分層載入策略、完善的查詢測試與日誌，以平衡彈性與可維護性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q7, D-Q8, C-Q9

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何依模組拆分大型模型為多個 .edmx？
- A簡: 依業務邊界切分資料表/檢視，為每模組建立 .edmx，控制範圍小且責任清晰。
- A詳: 具體步驟：1) 按領域/模組分群資料表與檢視；2) 為每群建立獨立 .edmx，僅匯入必要物件；3) 移除跨域相依，改以鍵值或服務介面協作；4) 為每個 .edmx 產生對應類別；5) 驗證各自可建置與查詢。注意：避免表格重複映射；建立一致的命名與鍵策略；記錄容器名稱，供跨模型查詢時使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q9

C-Q2: 如何將 csdl/ssdl/msl 內嵌到各自的組件？
- A簡: 從 .edmx 分離三檔，設為 Embedded Resource，與模組 DLL 一同發佈。
- A詳: 步驟：1) 以設計器或工具分離出 Model.csdl/ssdl/msl；2) 在專案將三檔「Build Action=Embedded Resource」；3) 保留或自動產生的實體類別；4) 建置產出 DLL；5) 確認資源嵌入成功（ILSpy/Reflector 檢查）。最佳實踐：資源命名加上模組前綴；版本變更時更新檔名避免舊資源殘留。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q9

C-Q3: 如何建立「合併多組 Metadata」的連線字串？
- A簡: 在 metadata 參數以 | 串接多組 csdl/ssdl/msl 路徑，並指定 provider 與資料庫連線。
- A詳: 範例：metadata=res://*/A.csdl|res://*/A.ssdl|res://*/A.msl|res://*/B.csdl|res://*/B.ssdl|res://*/B.msl;provider=System.Data.SqlClient;provider connection string="..."; 亦可用 EntityConnectionStringBuilder 設定 Metadata 與 ProviderConnectionString。注意順序與檔名正確；若多模組資料庫相同，共用 provider 連線即可。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q4, A-Q13

C-Q4: 如何用合併連線初始化單一 ObjectContext？
- A簡: 以 EntityConnection 或連線字串建構 ObjectContext，形成共享 Workspace 的工作單元。
- A詳: 步驟：1) 建立 EntityConnectionString；2) var conn=new EntityConnection(connStr); conn.Open(); 3) var ctx=new ObjectContext(conn); 4) 設定 DefaultContainerName（選用）；5) 驗證 ctx.MetadataWorkspace 已包含多個容器。最佳實踐：集中管理 Context 的生命週期；以 using 或 IoC 容器控管範圍。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, A-Q15

C-Q5: 如何以 eSQL JOIN 跨兩個模組的實體集？
- A簡: 在 eSQL 使用 [容器].[實體集] 全名，於單一 Context 內直接 JOIN 與投影。
- A詳: 示意：var q=ctx.CreateQuery<DbDataRecord>("SELECT c.Name,o.Total FROM AContainer.Customers as c JOIN BContainer.Orders as o ON c.Id=o.CustomerId WHERE o.Total>1000"); foreach(var r in q){...} 注意容器/實體集名稱正確；用參數化避免注入；對大查詢加索引與篩選條件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q4, D-Q7

C-Q6: 如何用 LINQ + CreateQuery<T>() 進行跨模組查詢？
- A簡: 以 CreateQuery<T>("容器.實體集") 建立來源，再用 LINQ 運算子組合與 JOIN。
- A詳: 範例：var customers=ctx.CreateQuery<Customer>("AContainer.Customers"); var orders=ctx.CreateQuery<Order>("BContainer.Orders"); var q=from o in orders join c in customers on o.CustomerId equals c.Id where o.Total>1000 select new{c.Name,o.Total}; foreach(var x in q){...} 注意型別對應；確保兩型別來自已載入的 Metadata。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q6

C-Q7: 合併後如何新增、更新並 SaveChanges？
- A簡: 使用 AddObject/Attach 到指定「容器.實體集」，追蹤變更後一次 SaveChanges。
- A詳: 新增：ctx.AddObject("BContainer.Orders", new Order{...}); 更新：先查詢實體，修改屬性；或 AttachTo("AContainer.Customers", entity) 並設定狀態。最後 ctx.SaveChanges() 一次提交跨模組變更。注意：實體所屬的容器與集合名稱需正確；避免重複 Attach；控制交易邊界。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q13

C-Q8: 如何在不重編其他模組下加入新模組？
- A簡: 部署新模組 DLL（含內嵌模型），確保載入該組件，res://*/ 通配會自動拾取。
- A詳: 步驟：1) 為新模組建立 .edmx 並內嵌 csdl/ssdl/msl；2) 發佈 DLL 至主程式探查路徑；3) 於啟動時載入該 DLL（反射或自動載入）；4) 使用既有的合併 metadata 連線字串；5) 驗證容器已可見。預防：統一命名避免衝突；版本控管資源檔名。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q14, D-Q9

C-Q9: 如何測試與診斷合併模型的查詢問題？
- A簡: 檢查 ctx.MetadataWorkspace 容器/集合，驗證全名；記錄 eSQL/LINQ 與生成的 SQL。
- A詳: 步驟：1) 列出 MetadataWorkspace.GetItems<EntityContainer> 確認容器；2) 驗證 CreateQuery 的集合全名；3) 啟用 EF 日誌或 Profiler 觀察 SQL；4) 用最小可複現查詢縮小範圍；5) 檢視資源存在與命名。最佳實踐：建立檢核工具在啟動時列印可用集合清單。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q15, D-Q8

C-Q10: 何時應退回多 Context 並以其他機制協調？
- A簡: 當命名衝突嚴重或模型過大導致載入成本高，可採多 Context 並以交易/服務協調。
- A詳: 若合併引入大量命名衝突或超大 Workspace 造成啟動/記憶體壓力，可維持多 Context，避免跨 Context 查詢，改以應用層組合資料或資料庫端建立視圖；跨 Context 資料一致性以分散式交易或明確流程控制。此為權衡方案，依系統規模選擇。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, D-Q10

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到「不支援跨 Context 查詢」錯誤怎麼辦？
- A簡: 改用單一 ObjectContext 載入多組 Metadata，或重構為單一模型內查詢。
- A詳: 症狀：LINQ/eSQL 嘗試 JOIN 兩個不同 Context 的實體集時拋錯。原因：EF v1 將查詢與追蹤限定於 Context 範圍。解法：用合併 metadata 的連線字串建立單一 Context，將兩模型置於同一 Workspace；或改為資料庫端視圖。預防：規劃模型邊界，避免跨 Context 依賴。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, C-Q4

D-Q2: .edmx 設計器「重拉資料表後建置失敗」怎麼辦？
- A簡: 清理並重建模型，檢查重複對應與鍵，必要時手動編修 .edmx。
- A詳: 症狀：刪除再拉入資料表後編譯失敗。原因：設計器殘留對應、重複型別或鍵設定缺失。解法：移除殘留實體/對應，重新產生；或以 XML 編輯 .edmx 修正重複項與鍵。預防：小步更新模型、版本控管 .edmx、定期清理未使用的對應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q9

D-Q3: 將檢視（VIEW）加入模型後「鍵未設定或結果錯誤」如何處理？
- A簡: 明確指定檢視的主鍵欄位，必要時手動編修 CSDL/Mapping。
- A詳: 症狀：檢視無鍵導致物化或追蹤異常。原因：EF 需唯一鍵辨識實體。解法：在 CSDL 為檢視對應的實體指定鍵，或改以唯讀查詢；手動調整 MSL 對應。預防：設計檢視時輸出唯一鍵或 surrogate key；文件化鍵設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q1

D-Q4: 為何 Navigation Property 在跨模組實體間無效？
- A簡: 關聯被限制於 Context，跨 .edmx 無共享關聯，需改以查詢或合併模型處理。
- A詳: 症狀：從 A 模組的實體無法導覽到 B 模組的關聯實體。原因：AssociationSet 不跨 Context。解法：合併 metadata 以單一 Context 查詢；或以鍵值手動查詢關聯；必要時在資料庫層建立視圖整合。預防：跨模組不要依賴導航，使用服務或查詢邊界。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q7, C-Q5

D-Q5: 為何 SaveChanges 後部分模組變更未寫入？
- A簡: 變更在不同 Context 追蹤，僅提交其中一個；需統一 Context 或逐一提交。
- A詳: 症狀：只有部分資料持久化。原因：多個 Context 各自追蹤與提交。解法：改用單一 Context 合併模型，一次 SaveChanges；若維持多 Context，確保在同一交易內依序 SaveChanges。預防：明確設計工作單元邊界，避免隱性多 Context。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q7

D-Q6: 合併模型後 LINQ 查無集合屬性該怎麼查？
- A簡: 使用 CreateQuery<T>("容器.實體集") 建立 IQueryable 作為 LINQ 來源。
- A詳: 症狀：Context 無 Customers/Orders 等集合屬性。原因：非強型別 Context。解法：ctx.CreateQuery<T>("Container.Set") 取得來源，照常撰寫 LINQ；或建立輕量包裝提供集合屬性。預防：統一容器/集合命名，文件化對應表。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q6, C-Q6

D-Q7: 出現「實體集名稱無效」怎麼診斷？
- A簡: 確認容器與集合全名正確，大小寫與命名無衝突，並已載入對應資源。
- A詳: 症狀：CreateQuery/eSQL 報實體集無效。原因：容器名錯、集合名拼錯、同名衝突、資源未載入。解法：列出 MetadataWorkspace 中的 EntityContainer 與 EntitySet；改用全名；修正命名衝突。預防：規範命名與前綴；啟動時自動驗證集合清單。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q9

D-Q8: 「Unable to load the specified metadata resource」如何排除？
- A簡: 檢查資源是否內嵌、命名與路徑正確、組件已載入，並修正連線字串。
- A詳: 症狀：啟動或建 Context 時拋出無法載入資源。原因：資源非 Embedded、大小寫/命名空間不符、res:// 路徑錯、組件未載入。解法：確認 Build Action=Embedded Resource；用工具檢查資源名稱；確保 DLL 已載入；修正 metadata 路徑或改用通配。預防：建立啟動自檢，列印可用資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q2, C-Q9

D-Q9: 如何確保新增模組後無需重編舊模組仍可運作？
- A簡: 使用通配 metadata、模組自帶資源、動態載入組件並驗證容器可見。
- A詳: 症狀：加入新模組後舊模組需重編。原因：硬編資源路徑或靜態相依。解法：改用 res://*/ 通配，將模型內嵌於模組 DLL；於啟動時載入新 DLL；用 Workspace 驗證容器存在。預防：移除硬編資源名稱；以組態驅動模組清單。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q8

D-Q10: 何時不建議合併模型？若效能不佳怎麼辦？
- A簡: 模型過大或衝突多時不宜；可維持多 Context，以資料庫視圖或服務組合資料。
- A詳: 症狀：啟動慢、記憶體高、命名衝突頻繁。原因：Workspace 載入片段過多或規劃不當。解法：評估回退至多 Context；跨 Context 查詢以資料庫視圖或應用層 join；重要交易以流程或分散式交易協調。預防：模型合理切分、命名規約、逐步合併與基準測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, C-Q10

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Entity Framework（EF）？
    - A-Q2: 什麼是 .edmx？
    - A-Q5: CSDL、SSDL、MSL 的定義與差異？
    - A-Q3: 什麼是 ObjectContext？
    - A-Q4: 什麼是 EntityConnectionString？
    - A-Q6: 什麼是 eSQL（Entity SQL）？
    - A-Q7: 什麼是 LINQ to Entities？
    - A-Q9: 為什麼大型 Schema 會造成 ORM 的困難？
    - A-Q10: 為什麼要把模型拆成多個 .edmx？
    - B-Q5: 多組 Metadata 的載入流程與關鍵步驟為何？
    - B-Q8: 為何多 Context 需各自 SaveChanges？
    - C-Q1: 如何依模組拆分大型模型為多個 .edmx？
    - C-Q2: 如何將 csdl/ssdl/msl 內嵌到各自的組件？
    - C-Q3: 如何建立「合併多組 Metadata」的連線字串？
    - C-Q4: 如何用合併連線初始化單一 ObjectContext？

- 中級者：建議學習哪 20 題
    - A-Q8: 什麼是 AssociationSet 與 Navigation Property？
    - A-Q11: 為什麼 EF v1 不支援跨 Context 的查詢與關聯？
    - A-Q12: LINQ 與 eSQL 在跨 Context 上有何差異？
    - A-Q13: 為什麼合併多組 Metadata 到連線字串能解決跨模型查詢？
    - A-Q14: 什麼是「以模組封裝 .edmx 與邏輯」的做法？
    - A-Q15: 單一 ObjectContext 跨多模型的核心價值是什麼？
    - B-Q1: EF 的 O/R Mapping 背後機制是什麼？
    - B-Q2: res:// 路徑如何載入 .edmx 內的 CSDL/SSDL/MSL？
    - B-Q3: ObjectContext 以 EntityConnection 建構時如何運作？
    - B-Q4: eSQL 如何在單一 Context 中跨模型運作？
    - B-Q6: 為何合併模型後 LINQ 需用 CreateQuery<T>()？
    - B-Q11: 多個 EntityContainer 名稱如何影響查詢解析？
    - B-Q13: 強型別 Context 與通用 ObjectContext 的差異？
    - B-Q14: 新增模組為何不需重編其他模組？
    - C-Q5: 如何以 eSQL JOIN 跨兩個模組的實體集？
    - C-Q6: 如何用 LINQ + CreateQuery<T>() 進行跨模組查詢？
    - C-Q7: 合併後如何新增、更新並 SaveChanges？
    - C-Q8: 如何在不重編其他模組下加入新模組？
    - D-Q1: 遇到「不支援跨 Context 查詢」錯誤怎麼辦？
    - D-Q7: 出現「實體集名稱無效」怎麼診斷？

- 高級者：建議關注哪 15 題
    - B-Q12: eSQL 的執行流程與核心組件？
    - B-Q15: 合併模型的風險與限制是什麼？
    - C-Q9: 如何測試與診斷合併模型的查詢問題？
    - C-Q10: 何時應退回多 Context 並以其他機制協調？
    - D-Q2: .edmx 設計器「重拉資料表後建置失敗」怎麼辦？
    - D-Q3: 將檢視加入模型後「鍵未設定或結果錯誤」如何處理？
    - D-Q4: 為何 Navigation Property 在跨模組實體間無效？
    - D-Q5: 為何 SaveChanges 後部分模組變更未寫入？
    - D-Q6: 合併模型後 LINQ 查無集合屬性該怎麼查？
    - D-Q8: 「Unable to load the specified metadata resource」如何排除？
    - D-Q9: 如何確保新增模組後無需重編舊模組仍可運作？
    - D-Q10: 何時不建議合併模型？若效能不佳怎麼辦？
    - B-Q10: res:// 的通配符如何支援免重編擴充？
    - B-Q11: 多個 EntityContainer 名稱如何影響查詢解析？
    - A-Q15: 單一 ObjectContext 跨多模型的核心價值是什麼？