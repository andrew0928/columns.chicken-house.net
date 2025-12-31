---
layout: synthesis
title: "EF#3. Entity & Inheritance"
synthesis_type: summary
source_post: /2009/03/03/ef3-entity-inheritance/
redirect_from:
  - /2009/03/03/ef3-entity-inheritance/summary/
postid: 2009-03-03-ef3-entity-inheritance
---

# EF#3. Entity & Inheritance

## 摘要提示
- 繼承核心: 繼承是 OOP 的核心特性，ORM 必須處理關聯式資料如何對應物件的繼承關係。
- 虛擬表概念: 以 virtual table 理解繼承，映射到資料庫時可視為 table schema 與資料列的一一對應。
- ORM重點: ORM 只需處理資料層的對應，較不涉及語言層面的虛擬機制細節。
- 對應直覺: 子類別擁有父類別欄位，對應到資料庫即關乎正規化與表格切割策略。
- 三種策略: EF/NH 均支援 TPH、TPT、TPC 三種繼承對應模型。
- TPC定義: Table per Concrete Type 將父類欄位複製到每個具體子類的表中。
- TPT定義: Table per Type 以 FK 將子類表連到父類表，透過 join 重組完整實體。
- TPH定義: Table per Hierarchy 以單一表承載整個繼承家族，非用欄位留空。
- 名稱對照: EF 與 NH 對三種策略命名不同但概念一致，可互相對照理解。
- 優缺點權衡: 三種對應在查詢性能、約束能力、維護複雜度與 schema 演進上各有取捨。

## 全文重點
本文從 OOP 的繼承談起，指出繼承是物件技術的核心，而在 ORM 的情境下，關鍵在於如何讓關聯式資料庫的結構合理對應到物件的繼承層次。作者以 C++/CLR 背景中的 virtual table 作為比喻：在物件世界裡，子類別繼承父類的資料與方法；映射到資料庫時，可將 virtual table 類比為資料表的 schema，而物件的實例對應為資料表中的一筆資料。此觀點讓我們在資料層面理解：子類別理應擁有父類別的所有欄位，於是資料建模會落在正規化與反正規化的選擇之間。

基於此，ORM 在面對繼承對應時，主流框架（Entity Framework 與 NHibernate）皆歸納出三種通行策略。其一是 Table per Concrete Type（TPC）：每個具體子類各有一張表，並將父類欄位完整複製進來，查詢單一子類時最直觀、mapping 也簡單，但父類欄位異動會影響所有子類表，且跨子類彙總查詢需要多表合併。其二是 Table per Type（TPT）：父子類各自一張表，子表以外鍵指向父表，查出完整實體需多表 join；優點是 schema 嚴謹、各表可分別施加約束，類別變動影響面較小，但層級深時查詢成本上升、表數量亦隨類別增長。其三是 Table per Hierarchy（TPH）：整個繼承家族共用單一表，以鑑別欄位區分型別，欄位全集在一張表內，未用欄位則留空；優勢是實作最簡單、跨類型單一查詢容易、欄位調整快，但當實例數量龐大或需要嚴格的 schema 檢查時，效能與資料完整性驗證都可能受限。

文中亦提供 EF 與 NH 的命名對照：EF 的 Table per Hierarchy 對應 NH 的 Table per class hierarchy；EF 的 Table per Type 對應 NH 的 Table per subclass；EF 的 Table per Concrete Type 對應 NH 的 Table per concrete class。最後以比較表概括三種策略適用與不適用的情境：TPH 適合簡單繼承與 moderate 資料量的單表查詢需求；TPT 適合需要嚴謹約束且易於類別獨立演進的情境；TPC 則在 mapping 簡便與強約束之間取得平衡，但承擔跨表彙總不易與父類變更波及的代價。整體而言，選擇策略需基於資料量、查詢模式、schema 嚴謹度與演進成本綜合評估。

## 段落重點
### 繼承在 OOP 與 ORM 中的重要性
作者開宗明義指出繼承是 OOP 的精髓，若無繼承，OOP 的魅力大減。延伸到 ORM 的主題，必須回答 R（關聯式資料庫）如何對映到 O（物件）並妥善處理繼承。由於 RDBMS 不支援物件導向，理解繼承機制本身有助於把握 ORM 對應的核心問題。

### 以 virtual table 類比資料庫 schema 的映射思維
文中回顧 C++ 以 virtual table 實作繼承的概念，並將其轉化為資料庫觀點：virtual table 類比資料表 schema，物件實例等同資料列。子類別承襲父類欄位的直覺，對應到資料庫就是要思考正規化與反正規化的取捨：是將欄位切開用 PK/FK 關聯，或直接在多張表重複定義。由此引出三種主要策略。

### 三種繼承對應策略概述
以示例說明：若 class A 對應 table A，而 class B 對應 table B，B 應包含 A 的欄位。據此有三法：1) TPC：在 B 表複製 A 的欄位；2) TPT：B 表僅留 FK 指向 A 的 PK，查詢時 join；3) TPH：建立一張共享表承載家族所有欄位，不用的欄位留空。三者對應不同的正規化程度與維護、查詢成本。

### EF 與 NH 名稱對照與一致性
EF 與 NHibernate 對三種策略命名不同但概念一致：EF 的 Table per Hierarchy（NH: Table per class hierarchy）、Table per Type（NH: Table per subclass）、Table per Concrete Type（NH: Table per concrete class）。處理方式大同小異，皆為繼承對應的標準手法；參考連結可深入技術細節。

### 三種策略的適用情境與限制比較
作者以表格總結優劣：TPH 實作最簡單，適合實體數量不大、需單一查詢涵蓋所有子型別、繼承層次簡單且欄位常調整的情境，但在大量資料與嚴格 schema 檢查上不利。TPT 能清楚映射繼承、允許各類型表施加嚴謹約束、易於個別變動，但查單一實體需多層 join 且表數隨類型暴增。TPC 綜合兩者優點也承擔缺點：mapping 簡單、可對各類型施加表約束，但跨全家族單一查詢困難，且父類欄位調整需同步修改所有子表。

### 小結與預告
文章以「未完待續」作結，暗示後續將延伸實作或更深入的比較。核心訊息是：選擇 TPH、TPT、TPC 必須基於資料量、查詢需求、約束強度與 schema 演進成本綜合權衡，沒有放諸四海皆準的答案。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 物件導向基本觀念：類別、物件、繼承、多型
   - RDBMS 基礎：表格、主鍵/外鍵、正規化與反正規化、JOIN
   - ORM 概念：物件與資料表的對應、實體與屬性對應
   - EF/NHibernate 基本使用：模型定義、Mapping、查詢
2. 核心概念：
   - 物件繼承到關聯式資料的對應：將 Is-A 關係映射到表結構
   - 三種繼承對應策略：TPH（Table per Hierarchy）、TPT（Table per Type）、TPC（Table per Concrete Type）
   - 取捨與條件：效能、查詢複雜度、Schema 嚴謹度、維護成本
   - 正規化與反正規化在繼承映射中的角色與影響
   - 多型查詢與單一查詢聚合的需求判斷
3. 技術依賴：
   - EF/NHibernate 提供的繼承 Mapping 支援（EF: TPH/TPT/TPC；NH：命名略有差異）
   - DB Schema 設計與約束能力（PK/FK、Constraint、Index）
   - 查詢層的 JOIN 與聚合（尤其 TPT 的多層 JOIN）
   - 遷移與版本控制工具（Schema 變更對不同策略的影響）
4. 應用場景：
   - TPH：階層簡單、實體數量不大、常需要一次查出所有子類別、多型查詢頻繁、希望快速落地
   - TPT：需要嚴謹表結構與約束、各子類別差異顯著、變動隔離、也常需要多型查詢
   - TPC：想兼顧各類別各自嚴謹的約束且 Mapping 簡單，但願意承擔跨表聚合與父類別欄位變更成本
   - 高實體數量與深層繼承：避免 TPH；多層 JOIN 敏感：避免深度 TPT

### 學習路徑建議
1. 入門者路徑：
   - 從 OOP 繼承、多型概念與 RDBMS 正規化基礎開始
   - 了解 ORM 基本對應（類別⇄資料表、屬性⇄欄位、關聯⇄FK）
   - 在 EF 中先實作 TPH：單一表、Discriminator 欄位、基本 CRUD 與多型查詢
   - 練習比較單一查詢撈取父類型集合與具體子類型集合的差異
2. 進階者路徑：
   - 探索 TPT 與 TPC 的 Schema 設計、查詢、約束設置與效能差異
   - 基於資料量、繼承深度、查詢模式，建立選型準則
   - 練習索引策略、讀寫分離、查詢優化（特別是 TPT 多表 JOIN）
   - 熟悉 Schema 演進：父類別欄位新增/調整對 TPH/TPT/TPC 的影響與遷移腳本撰寫
3. 實戰路徑：
   - 選定一個實際的繼承階層（如產品/數位產品/實體產品）同時用 TPH/TPT/TPC 各做一次
   - 用 EF 實作三種 Mapping，撰寫聚合查詢、多型查詢與過濾條件
   - 壓測不同資料量與繼承深度，量化查詢延遲、JOIN 數、計劃複雜度
   - 制定團隊規範：策略選型 checklist、Schema 變更流程、回滾與測試策略

### 關鍵要點清單
- 物件繼承對應的核心問題: 將 Is-A 階層轉換為關聯式表格並兼顧查詢與一致性 (優先級: 高)
- TPH（Table per Hierarchy）定義: 單一表含所有屬性並用 Discriminator 區分子類別 (優先級: 高)
- TPH 優點: 實作最簡單、單一查詢可取回所有子類別、多型查詢自然 (優先級: 高)
- TPH 缺點: 大量資料時效能風險、無法做嚴格的欄位/約束、稀疏欄位多 (優先級: 高)
- TPT（Table per Type）定義: 父/子類別各有表，以 PK/FK 垂直切分並以 JOIN 聚合 (優先級: 高)
- TPT 優點: 正規化好、能對每類別施加嚴格約束、類別變動影響面可控 (優先級: 高)
- TPT 缺點: 繼承深時需要多層 JOIN、表數量隨子類別成長、查詢計劃複雜 (優先級: 高)
- TPC（Table per Concrete Type）定義: 各具體子類別各有表，重複父類別欄位、無跨表父表 (優先級: 中)
- TPC 優點: Mapping 簡單、各表可有嚴格約束、避免多層 JOIN (優先級: 中)
- TPC 缺點: 多型聚合查詢不易、父類別欄位變更需同步多表、資料重複 (優先級: 中)
- 正規化與反正規化取捨: TPT 偏正規化、TPH/TPC 可能引入反正規化以換取實作與查詢便利 (優先級: 中)
- 多型查詢需求判斷: 若常以父型取回所有子類別，TPH/TPT 友善，TPC 成本高 (優先級: 高)
- 資料量與效能: 大量 instance 時避免 TPH；深階層 TPT 注意 JOIN 成本與索引 (優先級: 高)
- Schema 嚴謹度與約束: 需嚴格表層級約束時傾向 TPT/TPC；TPH 受限於單表與稀疏欄位 (優先級: 中)
- 變更與維護成本: 父類別欄位變動 TPC 成本最高、TPT 次之、TPH 最低但整表影響大 (優先級: 中)
- EF 與 NH 名稱對照: EF: TPH/TPT/TPC；NH: Table per class hierarchy/subclass/concrete class (優先級: 低)
- 選型準則清單: 依據繼承深度、資料量、查詢模式、約束需求、演進頻率綜合評估 (優先級: 高)