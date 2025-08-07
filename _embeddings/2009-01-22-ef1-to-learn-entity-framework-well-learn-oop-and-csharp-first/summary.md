# EF#1. 要學好 Entity Framework？請先學好 OOP 跟 C#…

## 摘要提示
- Entity Framework：ORM 的效果好壞，取決於承載它的整體 .NET／C# 生態是否成熟。
- OOP 核心：封裝、繼承、多型決定了 ORM 能否真正做到「以物件思考」。
- Typed DataSet：雖已具備 ORM 雛形，但血統不純，仍看得到大量資料導向痕跡。
- 成功條件：良好對應機制、擴充性、查詢能力、物件感、效能與品牌缺一不可。
- 封裝落差：DBMS 僅有安全機制，無法像物件一樣將行為與資料真正封裝。
- 繼承難題：資料表切分與維護複雜度高，ORM 需提供多種策略對應。
- 多型困境：SP 層難以優雅處理多型，應交由 ORM 於 APP 層統一抽象。
- C# 演進：Reflection/Attribute、Partial Class、Extension Methods、LINQ 解決過去 ORM 語法限制。
- LINQ 價值：讓查詢語意貼近物件世界，大幅降低直接撰寫 SQL 的需求。
- 系列方向：本文先談背景與關鍵，後續將示範實作技巧與實戰經驗。

## 全文重點
作者回顧自己研究 OOP、OODB 與多種資料庫技術的經驗，指出 ORM 是否實用，關鍵不單在 Framework 本身，而在整個開發語言與周邊技術是否已足夠成熟。過去如 Typed DataSet 雖能把資料包成物件，卻因封裝不完全、查詢能力不足而難以全面取代 SQL。今日的 Entity Framework 借助 C# 新語言特性與 LINQ，終於能在「看起來就是物件」的前提下處理資料庫工作，並以 Reflection、Partial Class、Extension Methods 提升程式可維護性。作者列出六項 ORM 成功必要條件，並從封裝、繼承與多型三大 OOP 特性切入，分析 DBMS 無法滿足的痛點，以及 ORM 如何補位：封裝層可成為資料進出唯一 API；繼承需靠 Mapping 策略將階層對映到關聯式模型；多型則避免在 Stored Procedure 裡寫成一堆複雜判斷。藉由這些改善，三層式架構才能真正保持「資料存取層」與上層邏輯的分離。本文作為系列開端，奠定後續示範與比較 NHibernate 的基礎。

## 段落重點
### 1. ORM 學習動機與資訊缺口
作者為五年開發計畫評估 ORM，發現網路多為零散實作文章，少有架構層面的優缺點比較，因此決定撰寫系列文，先談背景與本質，再談實作。

### 2. 自身經驗與歷代技術嘗試
從大學研究 OOP、研究所接觸 Smalltalk 與 OODB，到職場使用 TAMINO、XML-DB、自製 XML-ORM Framework，作者一路體會到「簡單又可行」方案之稀少。

### 3. Typed DataSet 與 Entity Framework 差異
Typed DataSet 早有 Container、Table、Row 與關聯等對應，但仍暴露資料導向血統；EF 則透過純物件模型往實用邁進，只是成熟度暫遜 NHibernate。

### 4. 成功 ORM 的六大要素
良好 Mapping、擴充能力、物件式查詢、物件完整性、效能與心理層面的「品牌」是作者歸納的必要條件，缺一即難以落地。

### 5. 物件導向三核心回顧
封裝、繼承、多型是 OOP 讓程式抽象化與重用的基礎，但傳統 DBMS 難以直接支援，造成程式與資料層落差，ORM 正是彌補手段。

### 6. 封裝：DBMS 與 ORM 的職責分工
DBMS 只能靠權限、鍵值維護資料正確；若 ORM 於 APP 層提供強封裝，可成為唯一存取入口，減少錯誤資料滲入，亦可取代自寫 DAL。

### 7. 繼承：資料表映射策略挑戰
以部落格內容為例，同一抽象型別在 DB 需分拆多表；EF 與 NHibernate 提供三種對映策略，開發者需評估維護成本與查詢複雜度。

### 8. 多型：Stored Procedure 的惡夢
若在資料庫層硬塞多型邏輯，只剩繁複 IF-ELSE；將多型抽象留在 ORM 與程式層，才能維持簡潔與延展性。

### 9. C# 語言進化對 ORM 的助益
Reflection/Attribute 用於對映標註，Partial Class 方便產生器與手寫程式共存，Extension Methods 可擴充現有型別，LINQ 則將查詢融入語言，成為 EF 成熟的關鍵。

### 10. 結語與後續預告
現代 C# 技術已解決早期 ORM 受限的語法問題，使 EF 能與一般物件無縫整合；後續文章將展示自定 Entity 技巧與實務經驗，敬請期待。