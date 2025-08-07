# 難搞的 Entity Framework ‑ 跨越 Context 的查詢

## 摘要提示
- Entity Framework 1.0: 第一版功能尚未成熟，與其他成熟 ORM 相比仍有落差。  
- 設計工具缺陷: .edmx 拖拉或重建容易導致 build 失敗，VIEW 無法正確指定 Key。  
- 大型資料庫難題: schema 龐大時無法把所有 Table/View 放在同一張 ER Model。  
- 分割 .edmx 後遺症: 會衍生多個 ObjectContext，SaveChanges 與查詢都被限制在各自 Context 中。  
- 跨 Context 查詢限制: LINQ 與 eSQL 都不支援跨越不同 ObjectContext 的 JOIN。  
- 模組化需求: .edmx 與商業邏輯需封裝於各自 Assembly，且新增模組不應影響既有編譯。  
- 微軟官方文章: “Working With Large Models In EF” 系列提供拆分模型的思路與 API。  
- 關鍵解法: 在 EntityConnectionString 的 metadata 區段列出多組 *.csdl/*.ssdl/*.msl。  
- 單一 ObjectContext: 透過合併後的連接字串即可存取多份模型並在 eSQL 中自由 JOIN。  
- LINQ 使用方式: 需自行以 CreateQuery<T>() 產生 EntitySet，其他操作與原來無異。  

## 全文重點
作者花了兩個月研究 Entity Framework (EF) 與 Enterprise Library，發現 EF 雖然背負微軟龐大的技術藍圖，但第一版功能與工具仍顯粗糙，尤其在處理大型、結構複雜的資料庫時問題特別多。  
為了避免把上百張資料表全部塞進一個 .edmx，作者採取「多 .edmx、模組化」的方式；然而，這個做法馬上遇到三大瓶頸：  
1) 產生多個 ObjectContext，必須分別呼叫 SaveChanges；  
2) LINQ 與 eSQL 都不能跨越 Context JOIN；  
3) AssociationSet 不能跨檔案，Navigation Property 無法跨模組使用。  

作者徵詢各種資料後，從 ADO.NET 團隊的官方部落格系列文章得到關鍵線索：在 Runtime 其實可以手動建立「包含多組模型定義」的 EntityConnectionString。只要把多個 .csdl、.ssdl、.msl 路徑用「|」串起來放進 metadata 參數，再以此字串構造 ObjectContext，就能把過去拆開的各 .edmx 在邏輯上縫合成「單一 Context」。  
eSQL 立即可對跨模組 EntitySet 做 JOIN；LINQ 雖無法直接使用自動產生的屬性，但可透過 ObjectContext.CreateQuery<T>() 取回想要的集合，其他 CRUD 與交易控制流程皆與原本相同。  
這個小技巧徹底解決了作者在大型系統模組化下「跨 Context 查詢」的痛點，既保留拆分 .edmx 的可維護性，又免除了多 Context 帶來的限制，也符合「新增模組無須重新編譯其他模組」的目標。

## 段落重點
### 一、研究近況與工具抱怨
作者兩個月都在研究 EF 與 Enterprise Library；前者比後者難纏。EF 設計工具在拖拉 Table/View 時常出現 Key 不明、重複加入導致編譯錯誤的問題，迫使開發者直接修改 .edmx。

### 二、大型資料庫的 OR Mapping 困境
大型企業系統往往有數百張 Table/View，單一 .edmx 不易維護也造成效能與視覺化困難。常見做法是將資料模型切割為多個 .edmx，以符合模組化與團隊分工需求。

### 三、多 .edmx 所衍生的跨 Context 障礙
切割雖然易管理，但 EF 會為每份 .edmx 生成獨立 ObjectContext：  
1) 每邊要各自 SaveChanges；  
2) eSQL 與 LINQ 不允許跨 Context JOIN；  
3) Navigation Property 受限於 AssociationSet，只能在單一模型內使用。這些限制在大型系統中難以接受。

### 四、需求列舉與官方文章探索
作者列出四大需求：模組封裝、跨模組 JOIN、基本 LINQ 支援、增刪模組免重編。搜尋過程中發現 ADO.NET 團隊的 “Working With Large Models In EF” 系列，文章建議在 Runtime 以自訂 EntityConnectionString 合併多組 schema。

### 五、關鍵技巧與實作成效
實作方法是在 metadata=res://*/… 參數後面依序加入多個 .csdl|.ssdl|.msl，再用此連接字串建立 ObjectContext。結果：  
1) eSQL 能對多個 EntitySet 自由 JOIN；  
2) LINQ 透過 CreateQuery<T>() 可取得集合；  
3) 仍保持模組與程式碼分離，新增或修改 .edmx 不影響其他模組編譯。作者終於解決困擾已久的跨 Context 查詢問題，宣告任務完成。