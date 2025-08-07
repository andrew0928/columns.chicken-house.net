# EF#3. Entity & Inheritance

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 ORM / Entity Framework 中，針對物件的繼承關係，一共有哪三種常見的資料表映射策略？
Table per Hierarchy (TPH)、Table per Type (TPT) 與 Table per Concrete Type (TPC) 三種。EF 與 NHibernate 都提供對應的設定（TPH/TPC/TPT 分別對應 NH 的 Table per class hierarchy、Table per subclass、Table per concrete class）。

## Q: 什麼情況下應該考慮使用 Table per Hierarchy (TPH)？
TPH 適用於：
1. 想要最簡單的實作方式  
2. 同一繼承階層的實體數量不多  
3. 需要用單一查詢 (single query) 取得所有子類別物件  
4. 繼承階層結構相對簡單  
5. 欄位（schema）變動頻率較高，需要容易調整  

但若 instance 數量龐大或希望在資料表層即加上嚴格約束，TPH 就不合適。

## Q: Table per Type (TPT) 的適用場景與限制為何？
適用場景：  
1. 想讓繼承關係在資料庫 schema 中清楚呈現  
2. 同樣需要用單一查詢就能抓回所有子類別資料  
3. 與 TPH 不同，可針對各子類別資料表加上嚴謹的約束 (constraint)  
4. 個別類別的欄位變動容易維護  

限制：  
1. 當繼承層次深或複雜時，取得單一實體資料需多層 JOIN，效能受影響  
2. 資料表數量會跟類別數量一同增長

## Q: 何時會選擇 Table per Concrete Type (TPC)？它有何優缺點？
TPC 綜合了 TPH 與 TPT 的優點，也繼承兩者部份缺點。  
優點：  
1. 各子類別皆可有自己的資料表並加上專屬 constraint  
2. ORM 映射設定相對簡單  

缺點：  
1. 若要以單一查詢一次撈回所有子類別資料，必須把所有子類別資料表 JOIN 起來，複雜且效能較差  
2. 父類別欄位若調整，必須同步修改所有子類別資料表

## Q: 為什麼關聯式資料庫（RDBMS）需要這些映射策略來支援物件導向的「繼承」？
因為 RDBMS 本身既不支援物件 (Object Base) 更不支援物件導向的繼承機制，必須透過 ORM 把「子類別擁有父類別所有欄位」的 Is-A 關係轉換成資料表結構。不同的轉換方式就形成了 TPH、TPT、TPC 三種策略，藉此在資料層模擬並保存物件世界的繼承結構。