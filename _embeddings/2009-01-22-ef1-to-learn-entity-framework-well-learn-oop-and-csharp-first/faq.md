# EF#1. 要學好 Entity Framework? 請先學好 OOP 跟 C# ...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼想學好 Entity Framework 之前要先學好 OOP 與 C#？
Entity Framework (EF) 是一套以物件導向為核心的 ORM 技術。只有在充分理解物件導向觀念（封裝、繼承、多型）以及 C# 的進階語法（reflection、attribute、partial class、extension methods、LINQ）後，才能真正掌握 EF 的用法並發揮其效益。

## Q: 影響一套 ORM 技術能否成功的關鍵因素有哪些？
作者列出了六項關鍵：
1. 優良的物件／關係對應機制與工具  
2. 充足的擴充性與自訂能力  
3. 能有效支援以物件角度思考的查詢方式  
4. 生成的「物件」必須看起來像物件，而非單純資料包  
5. 效能與便利性不能與直接操作資料庫差距過大  
6. 品牌與市佔（心理因素）

## Q: 相較於 NHibernate，目前的 Entity Framework 在成熟度上如何？
在成熟度方面 NHibernate 依然領先，但因 C# 與週邊技術（例如 LINQ）已趨成熟，使得目前的 Entity Framework 已邁入「可實用」的階段。

## Q: Entity Framework 與先前的 Typed DataSet 有何根本差異？
Typed DataSet 雖提供物件化存取，但資料操作過程仍處處可見 DataSet 的影子，血統不夠「純」。Entity Framework 結合新式 C# 語言特性，讓 Entity 真正像一般物件，並大幅改善以往 ORM 使用上的違和感。

## Q: Entity Framework 能夠實用的背後，C# 哪些語言機制功不可沒？
1. Reflection 及 Attribute：用來描述類別／屬性與資料庫的對應  
2. Partial Class：方便與程式碼產生器協作  
3. Extension Methods：讓既有類別更易擴充  
4. LINQ：提供強型別又具表達力的查詢語言

## Q: ORM 框架在「繼承對應」上通常提供幾種做法？
Entity Framework 與 NHibernate 均提供三種不同的繼承對應策略，開發者可依需求挑選最合適的方式。

## Q: 物件導向的三大核心特性是什麼？
封裝（Encapsulation）、繼承（Inheritance）、多型（Polymorphism）。

## Q: 讓 ORM 取代傳統 Data Access Layer 有何具體好處？
優秀的 ORM 能夠：
• 提供一致的封裝層，集中處理資料驗證與存取  
• 隱藏資料庫細節，減少重複且零散的 SQL 片段  
• 讓應用程式以物件方式操作資料，維持程式碼整潔並降低錯誤率