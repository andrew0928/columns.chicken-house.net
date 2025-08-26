這次為了能順利的學好 Entity Framework，花了不少工夫在研究它的作法。不過有一大半不是在 Entity Framework 本身，而是在 C# 的一些特別的語法跟 LINQ 身上...。也因為這樣，我深切的體認到一個 ORM 技術能不能成功，其實都是在 Hosting 這個 Framework 的環境夠不夠成熟...。

不過在摸索的過程中，找到的資訊都是片斷的，每一篇都是講實作，範例程式，操作步驟... 等等，而當時我最需要的反而是幫助我決定，Entity Framework 到底值不值得我押在上面投資五年開發計劃使用的 ORM 技術? 它跟 NHibernate (考慮中的另一項 ORM framework) 的優缺點為何? 未來發展的優缺點又是什麼? 架構上的差異在那? 另外 Linq to SQL 呢? 這些較偏架構性跟本質的討論及比較資訊，反而少之又少...。

雖然最後還是研究了些心得出來，不過實在是不想寫那些到處都看的到的實作，就來寫點不一樣的吧。第一篇會先寫寫 ORM 的背景知識，還有 Entity Framework 跟 C# 的語法是如何魚幫水，水幫魚，如何解決了過去 ORM 用起來都不大對勁的問題...。

繼續長篇大論前，先老王賣瓜一下。雖然我碰過的 ORM framework 不多，不過相關的理論跟技術則碰了不少。撇開大學就在研究的 OOP 不談，研究所的指導教授就從 [SmallTalk](http://en.wikipedia.org/wiki/Smalltalk) 開使教... 兩年的專題研究都是 [OODB](http://en.wikipedia.org/wiki/OODB) (物件導向資料庫)，相關論文也看了一堆。出來工作後又有幸用了幾年的 [TAMINO](http://www.softwareag.com/Corporate/products/wm/tamino/default.asp) (一套 native xml database), 之後又花了很多時間，在 SQL 2000 上面建立起一套 Object <-> XML <-> Database，類似 ORM 的 Framework ...

不過這麼一路下來，都沒有覺的簡單又可行的方案。除了上面講的是我親自參與過的之外， Microsoft 其實也發表過幾個類似的技術，像是 [Typed DataSet](http://msdn.microsoft.com/en-us/library/esbykkzb(VS.71).aspx) 就是個較接近的產物。 Typed DataSet 其實有點接近現在的 Entity Framework 了。DataSet 就等同於 Entity Container / ObjectContext, DataTable 大致就等同於 EntitySet, 而 DataRow 則等同於 Entity, Relation 則大致等同於 Entity Framework 的 Navigation Property.... 不過用起來還是到處都看的到 DataSet 的影子，感覺血統還不夠純正...

不過現在的 Entity Framework 不一樣了，感覺就已經往實用的領域邁進了一大步! 並不是說 Entity Framework 做的很好 (以成熟度來說, NHibernate 比目前的 Entity Framework 好的多), 而是跟 Entity Framework 搭配的技術都成熟了。一套 ORM 要成功，必要的條件很多啊... 實作上的角度看來，我覺的重要的有這幾項:

1. 要有優良的 Object / Relationship Mapping 機制、作法、工具等等
2. Framework 本身的擴充及自訂的能力要夠
3. 要有效的解決以物件角度思考的查詢 (QUERY) 問題
4. "物件" 要看起來像 "物件"，不是 "資料"
5. 處理資料庫典型的問題，效能跟便利性不能跟直接操作 DB 差太多
6. 你的牌子夠不夠響亮... (這是心理因素而已... 哈哈)

這些是深切的體認。不然的話 ORM 的東西跟本不難啊，以功能來說，Typed DataSet 其實就解決一大半實際的問題了。先來看看物件導向幾個關鍵的核心技術是啥?

1. 封裝 ( Encapsulation )，抽像化型別 (ADT, Abstract Data Type)，資料 (Data) 跟行為 (Behavior) 能夠綁在一起
2. 繼承 ( Inheritance )
3. 多型 ( Polymorphism )

以這樣 "物件" 的關點來看，Microsoft 在 Entity Framework 之前的資料庫技術其實都不合格。先來看看資料庫存取技術，如果能搭配這些物件技術，能有什麼樣的改進?

**[封裝]**  
這就沒啥好講的了。物件技術有很好的封裝機制，public / protected / private 等等 scope modifier 就能提供很棒的封裝機制。不過資料庫很難做的好，資料庫的那套頂多叫作安全機制 (security) 或是授權機制 (authorization), 不是封裝 (encapsulation) ... 真正的封裝不是看你是那個帳號決定能不能讀資料? 而是你是那個 SCOPE 的程式，能不能存取封裝起來的內部資訊。DBMS 對於資料的控制能力很有限，不外呼 Key, Constraint, Relationship / Foreign Key 等等。像加解密，正規運算式 (regular expression) 等等，對 DBMS 來說就太複雜了。更複雜的封裝機制單靠 DB 就很不實際... 無奈在沒有 ORM 的前題下，這些問題則是直接曝露在你的程式碼每個地方...。換句話說，如果 ORM 能提供良好的封裝機制，ORM 就能取代掉目前的 Data Access Layer ，成為 APP 存取 DBMS 的主要 API 。

順便吐個苦水，也因為 DBMS 對於資料的控制能力有限，維護的 APP 總是碰到這種問題，就是錯誤的資料總是有辦法鑽進資料庫裡面。不為什麼，只因為 DBMS 本身擋不下來，而 Data Access Layer 又不夠爭氣到足以扛下這重責大任，最後只能靠 APP 自身的開發人員，靠紀律跟自律，還有良心來作好這層把關的動作... -_- 如果有套像樣的 ORM 能夠卡在這個位置，光是資料內容的把關，就是一大進步了。

**[繼承]**  
繼承跟資料庫有什麼關係? 其實 ORM 如果能有效的把繼承的功能跟資料庫整合起來，也是很嚇人的。舉例來說，部落格支援文章，相片等等不同的內容，但是它們都要有一致的抽像行為，如新的內容要能夠訂閱 (rss subscription)，要能夠有標簽 (tagging) 等等共通的功能，在物件技術我們會很直覺的用繼承來做到。定義 BlogContent 類別，把這些邏輯擺上去。之後再分別衍生出 ArticleContent / PhotoContent 等類別，把差異的實作補上去就完成了。不過同樣的概念別想直接套用在資料庫上，你的腦袋得負責這兩者之間的對應。

懂的這麼多的工程師很難找啊... 去那裡找這種人來寫 APP ? 其實搞懂這些也不難，C++ / C# 在解決這類問題，只是很簡單的利用到 virtual table 就搞定了。換到 DBMS，就把 virtual table 的資料結構套到 database schema 就可以。不過說來簡單，能夠搞懂這些，還能精確的實作出來的人不多... 真的作出來還會被嫌:

"它ㄨ的，誰設計的 table schema ? 亂切一通害我 T-SQL query 這麼難寫..."

嗯，沒事，藉機吐吐苦水。主要要表達的就只有一個，繼承關係要對應到資料庫上面，也是挺麻煩的一件事。Entity Framework / NHibernate 就都提供了三種對應的方法。這三種切割對應的方式，要選那一種? 這又是門學問... Orz, 以後再說。

**[多型]**  
這個就更玄了。多型是建立在繼承的基礎上，不管你是什麼類別的 instance, 多型的機制可以在父類別的角度，對所有各種衍生類別的物件，一視同仁的操作。而在這統一的前題下，每種類別的物件又可以一國兩制的各自為政... (咳，這不是政治版...)。這樣的抽像程度就是資料庫遠遠所不及的。延序前面講的部落格內容的例子，你能想像這個 store procedure 該怎麼寫嗎?

"要寫一個 sp_update_blogcontent 的 store procedure, 如果 ID 指向的是 blog, 則要執行更新 HTML 的 code，如果是 photo, 則要更新存放圖檔的 BLOB 欄位..."

天那，在 DB 這個層次，寫這種 CODE 只能用很醜的 IF ELSE 一層一層堆起來...，跟物件技術比起來，程式碼的描述及抽像化能力實在差太遠，在這層次能解決的問題複雜度很有限...。你如果是個聰明人，最好還是別在 DBMS 搞這些物件技術，會死人的...。比較好的作法是移到 APP 那層去作比較實際。

不錯，ORM 存在的原因又多了一個...。

所以，再回頭來看看，ORM真的要發揮它的效益的話，絕對不是只有用 "物件" 來代替 "資料" 而已 (還是老話一句，這樣的話用 Typed DataSet 就夠了)。至少對應出來的 "物件"，還能有效的應用到這些物件導向的特性，同時 ORM framework 還能替你維持這些跟資料庫的對應關係，這樣 ORM 技術才能真正發揮它的效益，那些被講到爛的三層式架構才不會在 DBMS 這層就破功了。

來看看比較具體的部份。這些物件技術的特點，C# 早在 2000 年，JAVA 早在 199X 年就有了，沒什麼了不起。不過當年的 ORM 實在難用的很。當時的 OOPL 就是缺了些東西，ORM 的程式寫起來限制一堆... 對應到資料庫的物件，用起來就是跟一般的物件差很多，這也不能用，那也不能用。

現在的 C# 就不一樣了，進化到足以解決這些語言的限制。來看看:

1. reflection, attribute:  
   這個讓物件 (Entity) 可以寫的更簡潔，reflection + attribute 可以解決很多過去得繞一大圈才做的到的事。如 class 對應到那個 table, property 對應到那個 column 等等。

2. partial class:  
   ORM 免不了有些 code generator 的搭配。有 partial class 可以讓程式搭配 code generator 更容易一點。

3. extension methods:  
   現有的物件技術很難讓你在現有的 class 上去作擴充，而 extension methods 可以。

4. Linq  
   這可是一大進步。過去 ORM 的目的就是想把 DB 的細節藏起來，無奈碰到 QUERY 的話什麼都藏不住，往往淪落到要嘛都直接用 SQL, 不然就是只剩幾種基本的 API 可以用，無法完全取代直接用 SQL 的查詢。不過 Linq 出現之後這情況就改觀了，雖然像報表那樣複雜大型的 QUERY 還是得直接下 SQL，不過一般 AP 內的查詢都可以直接用 Linq 搞定了

其它當然還有別的，不過我自己覺的這幾點是關鍵，至少可以讓現在的 Entity Framework 在使用 Entity 時，不會再跟一般的物件有什麼不同。大部份你可以應用在一般物件的技巧，也都能套用在 Entity 身上。第一篇碎碎唸的部份就先寫到這裡。後面會示範一下幾種打造你專屬的 Entity 用到的技巧。想看後面的讀者們請耐心等待 :D