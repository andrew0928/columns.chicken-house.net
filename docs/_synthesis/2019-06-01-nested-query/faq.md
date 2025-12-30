---
layout: synthesis
title: "架構面試題 #3, RDBMS 處理樹狀結構的技巧"
synthesis_type: faq
source_post: /2019/06/01/nested-query/
redirect_from:
  - /2019/06/01/nested-query/faq/
---

# 架構面試題 #3, RDBMS 處理樹狀結構的技巧

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是樹狀資料結構？在RDBMS中如何對應？
- A簡: 樹由節點與父子關係構成。RDBMS以表格記錄節點與關聯，但需額外設計與索引才能高效處理層級與遞迴關係。
- A詳: 樹狀資料結構由節點、邊及父子層級組成，如檔案系統的資料夾/檔案。RDBMS以表格存行、列，天生不擅長層級遞迴，需要設計對應的模式，例如以父節點ID表達相對關係（Adjacency List）、預展開階層欄位（Path Enumeration）、或以左右界（Nested Set）標記包含範圍。不同方案在查詢、搬移、刪除等操作有明顯優劣，選擇關鍵在業務以查詢為主或異動為主，以及可否接受維護成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, A-Q5

A-Q2: 為何樹狀結構在RDBMS中「不自然」？
- A簡: 關聯表是扁平資料，遞迴需多次自連接或特殊語法；標準SQL缺乏一致遞迴支持，跨DBMS移植困難。
- A詳: RDBMS以集合與連接（Join）處理扁平資料。樹的「不限層級」查詢需遞迴，傳統SQL需多次Self Join，層級不定時難以寫死；CTE/CONNECT BY等為廠商擴充、可讀性佳但效能受限於多次關聯與掃描，且跨DBMS不相容。這使樹在RDBMS中有語意落差與效能挑戰，需藉由資料模型與索引（如Path欄位、左右界）來彌補。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q15, B-Q2

A-Q3: 什麼是方案一：Adjacency List（上一層ID）？
- A簡: 以每節點記錄PARENT_ID表達父子關係。查直屬子節點簡單，遞迴查詢依賴CTE或多層自連接。
- A詳: Adjacency List在DIRINFO表以(ID, PARENT_ID, NAME)表示樹，FILEINFO以(DIR_ID)連到目錄。列直屬子項簡單；遞迴查後代需CTE（Base + Recursive Member）或多層Self Join；搬移更新單筆PARENT_ID即完成；刪除子樹需先找全後代再刪。優點是結構直觀、異動便宜；缺點是深層遞迴查詢效能差且跨DBMS語法差異大。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, D-Q2

A-Q4: 什麼是方案二：Path Enumeration（開欄位記錄各層ID）？
- A簡: 以ID01…IDN依層級存放祖先鏈。後代查詢改為簡單條件過濾，速度快，但搬移與維護代價高。
- A詳: 每列記錄從根到自身的祖先ID序列（如ID01=root, ID02=windows, ID03=system32）。查直屬子項過濾下一層ID與其餘為NULL；查全後代只需篩選特定層ID等於某值。優勢是查詢快與可索引；劣勢是schema綁死最大層數、SQL需動態生成、搬移要整列「右移」欄位，維護成本高且易出錯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q6, D-Q4

A-Q5: 什麼是方案三：Nested Set Model（左右索引）？
- A簡: 對每節點以深度優先走訪標記LEFT/RIGHT。後代查詢變為範圍查詢，遞迴快；新增/搬移需重算索引。
- A詳: Nested Set以DFS對節點首次到達標LEFT、回溯標RIGHT，父節點的(LEFT,RIGHT)嚴格涵蓋子孫。查全後代→WHERE LEFT BETWEEN P.LEFT AND P.RIGHT；子孫數=(RIGHT-LEFT-1)/2。優點是不限層級、查詢幾近Range Scan，易封裝成SP。劣勢是插入/搬移需批次位移索引，需謹慎更新與鎖控。常與PARENT_ID或DEPTH輔助取得直屬子項。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q11, D-Q6

A-Q6: 什麼是CTE（Common Table Expression）？
- A簡: 由WITH定義的暫時結果集，可遞迴自參考。適合表達層級查詢，但效能仍受多次Join影響。
- A詳: CTE是可命名的臨時查詢視圖，語法WITH cte AS (...)。遞迴CTE包含「起始集」與「遞迴成員（UNION ALL）」反覆展開，直至無新行或達MAXRECURSION。優點是語法清晰、易讀；缺點是非標準跨DBMS差異、且計算仍需多次連接與掃描，對深度與資料量敏感。常用於Adjacency List實現後代查詢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q15

A-Q7: 什麼是Self Join（自我連接）？
- A簡: 同一表自我連接以比對不同層級的關聯。樹結構常用來串接父子節點或連續祖先。
- A詳: Self Join是將同一表以不同別名在同一查詢中連接，常見於Adjacency List把父行與子行接起來，或多層串接取得特定路徑（如c:\→windows→system32）。優點是容易表達相對關係；缺點是層數固定時可行，層數不定需CTE或動態生成連接，對效能與維護不利。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q3

A-Q8: 什麼是深度優先走訪（DFS）？為何用於Nested Set編號？
- A簡: DFS沿子節點一路到底再回溯。用它能為每節點標LEFT/RIGHT，保證父區間涵蓋子區間。
- A詳: DFS從節點出發，先探入最深子孫後回溯。Nested Set以「首次到達」時記LEFT、「回到節點」時記RIGHT，對所有節點產生連續整數區間，父區間必然包含子孫區間。如此將「包含」轉為數線區間判斷，使不限層級的後代查詢變成簡單範圍比對與索引掃描，極大化RDBMS的集合操作優勢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q7

A-Q9: 什麼是SQL Server的hierarchyid？何時採用？
- A簡: hierarchyid是SQL Server的階層資料型別，提供API操作樹。適合純SQL環境，但非通用標準。
- A詳: 自SQL Server 2008起提供hierarchyid，支援如GetAncestor、GetDescendant等方法，可省去自建CTE與索引。優點是開發快速、API豐富；缺點是專屬MSSQL、移植性差，與跨DBMS系統或ORM整合受限。在跨平台或需與其他方案混用時，建議用通用模式（Adjacency/Nested Set）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q6, B-Q13

A-Q10: RDBMS與NoSQL在處理樹結構的差異？
- A簡: NoSQL原生儲存層級文件較直觀；RDBMS需模式設計與索引彌補，但能善用關聯與交易。
- A詳: NoSQL（如文件/圖資料庫）自然支援巢狀或邊關係，樹操作直觀；RDBMS需透過Adjacency、Path、Nested Set等模型與索引來實現，查詢與維護取捨較多。不過RDBMS在強一致交易、跨表關聯、成熟工具上佔優。選擇取決於資料特性、查詢型態、既有基礎與維運能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q15

A-Q11: 為何要「預先維護索引」來加速樹查詢？
- A簡: 將遞迴成本前置到更新期，如Path或LEFT/RIGHT，讓查詢降為簡單的過濾或範圍掃描。
- A詳: 樹的瓶頸在「不限層級」遞迴。若在寫入/變更時計算Path欄位或LEFT/RIGHT，查詢時即可用普通條件或索引範圍完成，避免大量Join與遞迴。代價是搬移/新增需維護索引，可能批次更新較多列。這是以空間與更新成本換取極致查詢效能與通用SQL可移植性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, B-Q10

A-Q12: 三種方案的核心價值與選擇考量？
- A簡: 方案一異動友善、查詢遞迴慢；方案二查詢極快、維護難；方案三查詢快且通用、異動需重算索引。
- A詳: Adjacency（PARENT_ID）直觀，搬移只改一列，但遞迴查詢慢且仰賴CTE；Path欄位查詢最快、索引好用，但schema綁層數，搬移要大量欄位位移與動態SQL；Nested Set不限層級、後代查詢快且可用純SQL封裝，新增/搬移需批次位移索引。依據「查詢占比」「層級變動頻率」「跨DBMS需求」綜合選擇，亦可混用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, D-Q10

A-Q13: 方案一與方案二有何差異？
- A簡: 方案一以相對關係表達，遞迴查詢困難；方案二以展開路徑存欄位，查詢快但更新維護複雜。
- A詳: 方案一只存PARENT_ID，查詢直屬子項簡單，後代需CTE；搬移便宜。方案二預先展開ID01..IDN，後代查詢直接比對特定層欄位，效能出色；但層數受schema限制，搬移需整列欄位右移，且難以用固定SQL封裝，常需動態SQL並有注入風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q6

A-Q14: 方案二與方案三有何差異？
- A簡: 方案二靠固定層位相等過濾，查詢極快但不彈性；方案三靠範圍比對，通用性高，異動要重算。
- A詳: 方案二以欄位對層級，查詢等值比對＋索引非常快，但層數固定、SQL依場景不同不易泛化。方案三用LEFT/RIGHT範圍，後代查詢為單一條件，易封裝與移植；新增/搬移需位移索引，需小心鎖與一致性。綜合來看，方案三較均衡、易維運。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, B-Q11

A-Q15: 什麼是MAXRECURSION？何時使用？
- A簡: MAXRECURSION限制遞迴CTE的展開層數，避免無窮遞迴或極深樹造成資源耗盡。
- A詳: 在SQL Server中，可於查詢後加OPTION (MAXRECURSION n)限制CTE最大遞迴層級。當資料存在環或邏輯錯誤、或層級過深時，可避免長時間運行甚至阻塞。與資料約束（避免回路）與良好索引搭配，是使用CTE時的安全網與效能護欄。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q1

A-Q16: 為何「CTE好寫」不代表「效能好」？
- A簡: CTE僅是語法糖；底層仍多次連接與掃描。資料量大或層級深時，成本顯著。
- A詳: 遞迴CTE將複雜邏輯簡化，但執行仍會反覆產生中間集、Join與掃描，計算量與層數、分支度成比例。索引不足、過濾弱、還要Join其他表或Update/Delete時，效能更受限。CTE解決可讀性，不自動解決時間/空間複雜度問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q2, B-Q13

A-Q17: 樹狀資料常見操作有哪些？為何重要？
- A簡: 包含列直屬子項、查全後代、建立、搬移、刪除。實務如商品類別、檔案系統頻繁使用。
- A詳: 常見操作有（1）列出指定節點直屬子項（類似dir）；（2）遞迴查全後代符合條件（如副檔名）；（3）建立新節點（mkdir）；（4）搬移子樹（move）；（5）刪除子樹（rm）。大量網站、檔案、分類、郵件系統都強烈依賴這些操作，模型選擇需以實際操作分佈與性能目標為依歸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q7

A-Q18: 方案二為何常需要動態SQL？風險是什麼？
- A簡: 不同層級需不同欄位條件，靜態SQL難泛用；動態組字易導致SQL Injection風險。
- A詳: 方案二查詢時需指定特定層的ID欄位（如ID03=某值），層級不同會改變欄位，難以一支SP涵蓋所有情境，因此常以字串拼接出查詢。若未使用參數化/白名單，將引入注入風險；此外可維護性差、測試成本高。可透過產生式程式碼、視圖或包裝API降低風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q5, C-Q7

A-Q19: 什麼是SQL的「集合操作」思維？與樹查詢關係？
- A簡: SQL擅長以集合過濾與連接處理資料。將遞迴轉為範圍或等值過濾能發揮其強項。
- A詳: SQL的強項是以集合為單位的選擇、投影、連接與排序。樹若以LEFT/RIGHT轉為範圍過濾，或以Path欄位轉為等值過濾，便可避免逐層遞迴，讓查詢落在索引掃描、合併或Seek的範疇，性能與可預測性顯著提升。模型設計的核心是在更新期預處理，換得查詢期的集合友善。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q8

A-Q20: 左右索引的「包含」意義與節點數怎麼算？
- A簡: 子孫節點的LEFT/RIGHT必位於父節點(L,R)區間內；子孫數=(R-L-1)/2，能O(1)取得。
- A詳: 於Nested Set，若節點P的(LEFT,RIGHT)=(L,R)，則任一後代C滿足L<C.LEFT且C.RIGHT<R。因每節點佔兩格，子孫總數=(R-L-1)/2。此設計使包含測試與統計不需遞迴或Join，直接透過範圍比對與算術取得，極適合報表與快速聚合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q8

---

### Q&A 類別 B: 技術原理類

B-Q1: 方案一（Adjacency List）如何運作？核心組件與流程？
- A簡: 用DIRINFO(PARENT_ID)表達父子；以Self Join/CTE取子孫，FILEINFO以DIR_ID連結檔案。
- A詳: 技術原理說明：每個目錄行記錄自身ID與PARENT_ID，形成相對關係。關鍵步驟/流程：直屬子項→WHERE PARENT_ID=@id；特定路徑→多次Self Join；子孫→遞迴CTE展開。核心組件介紹：DIRINFO(ID,PARENT_ID,NAME)、FILEINFO(DIR_ID,NAME,EXT,SIZE)與必要索引。優點：異動簡單；缺點：遞迴查詢效能差、跨DBMS語法差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2

B-Q2: 遞迴CTE如何展開樹的子孫？執行流程與限制？
- A簡: 用WITH CTE定義起始集與遞迴集UNION ALL，不斷展開直到無新行或達MAXRECURSION。
- A詳: 技術原理：WITH CTE AS (Base SELECT WHERE PARENT_ID=@id UNION ALL Recursive SELECT JOIN CTE)。流程：1)以子層為Base；2)每輪用上一輪結果JOIN父子關係取得下一層；3)終止條件為無新增列或達MAXRECURSION。關鍵組件：CTE、索引(PARENT_ID)、MAXRECURSION。限制：層深或分支大會放大成本，還需防止環狀關聯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q15

B-Q3: 如何找特定路徑的目錄ID（多層Self Join）？
- A簡: 依固定層級以DIRINFO多次自連接，逐層比對Name，取得最後一層的ID。
- A詳: 原理：路徑明確且層級固定時，可用多層Self Join。例如根→windows→system32三層，D1→D2→D3依PARENT_ID連接，WHERE D1.NAME='c:\' AND D2.NAME='windows' AND D3.NAME='system32'。流程：自上而下逐層比對。組件：DIRINFO索引(NAME,PARENT_ID)。適用：層級已知時；不適合層數不定的動態路徑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, C-Q2

B-Q4: 方案二（Path Enumeration）如何運作？核心欄位與索引？
- A簡: 以ID01..IDN記祖先鏈；查全後代比對對應層欄位；建立複合索引提升Seek效率。
- A詳: 原理：每節點記錄自根到自身的各層ID。流程：直屬子項→IDk=父ID且IDk+1 IS NULL；全後代→IDk=父ID即可。核心組件：DIRINFO(ID01..IDN)、索引（常用層位上索引）。優點：篩選轉等值比對，速度快；缺點：schema固定層數、維護/搬移須「欄位右移」，易需動態SQL。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q6

B-Q5: 方案二如何查詢某節點所有後代檔案？
- A簡: 用DIRINFO於對應層欄位過濾，再JOIN FILEINFO；如D.ID03=@id，且F.DIR_ID=D.ID且F.EXT過濾。
- A詳: 原理：把遞迴化為等值過濾。流程：1)選擇層位k使IDk=@node；2)JOIN FILEINFO ON DIR_ID=ID；3)WHERE EXT=目標副檔名。核心組件：DIRINFO層位索引、FILEINFO(DIR_ID,EXT)索引。效能：高選擇性索引＋Seek查詢，常為毫秒級。注意：需正確選擇層欄位，避免掃描多層。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, A-Q11

B-Q6: 方案二搬移子樹為何需「欄位右移」？流程是什麼？
- A簡: 搬移會改變祖先鏈，故需將每列的ID欄位整體右移一層，再填新祖先，成本高。
- A詳: 原理：節點從A移至B，路徑長度+1且祖先序列改變。流程：1)找出源子樹的所有列；2)對每列IDN→IDN+1右移，釋出ID01..IDk；3)填入新祖先ID；4)更新FILEINFO不變。核心組件：批次UPDATE、嚴格事務控制。風險：SQL冗長、錯位易引發資料不一致；建議以SP/程式封裝。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q7, D-Q4

B-Q7: Nested Set如何標記LEFT/RIGHT？流程為何？
- A簡: 以DFS走訪節點，首次到達標LEFT，回到節點標RIGHT，產生父含子範圍。
- A詳: 原理：深度優先遍歷樹。流程：1)全域遞增計數器；2)進入節點→LEFT=counter++；3)遞迴處理子節點；4)回溯節點→RIGHT=counter++。核心組件：DIRINFO(LEFT,RIGHT)、遍歷程序（SQL或應用程式）。結果：父(L,R)嚴格涵蓋子孫；可O(1)計算子孫數與範圍查詢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q9

B-Q8: 用Nested Set查詢所有後代與混合列出目錄/檔案？
- A簡: 後代→WHERE C.LEFT BETWEEN P.LEFT AND P.RIGHT；再JOIN FILEINFO與UNION顯示目錄、檔案。
- A詳: 原理：包含轉範圍查詢。流程：1)取父(L,R)；2)選C WHERE C.LEFT BETWEEN L AND R；3)JOIN FILEINFO篩EXT；4)UNION加上目錄列，ORDER BY NAME。核心組件：LEFT/RIGHT索引、FILEINFO(DIR_ID)索引。效能：範圍掃描＋索引連接，適合大量後代過濾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q10

B-Q9: Nested Set如何計算子孫數、深度與包含關係？
- A簡: 子孫數=(R-L-1)/2；包含判斷用區間；深度可在建模時額外儲存DEPTH或以祖先數推得。
- A詳: 原理：每節點占兩個計數位，父包子。步驟：子孫數=常數時間算式；包含→C在P內即L<C.LEFT且C.RIGHT<R；深度→可在DFS時同時計數DEPTH或於查詢時用祖先數+1計出。核心組件：LEFT/RIGHT、（選用）DEPTH/PARENT_ID。可滿足快速報表與範圍統計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, C-Q8

B-Q10: Nested Set新增節點（mkdir）流程與代價？
- A簡: 在插入點右側「騰位」：所有>插入LEFT的LEFT/RIGHT+2，最後插入(L+1,L+2)。
- A詳: 原理：維持整數序列與區間不重疊。步驟：1)計算插入父節點LEFT；2)UPDATE所有RIGHT>父LEFT加2；3)UPDATE所有LEFT>父LEFT加2；4)INSERT新節點(LEFT=父LEFT+1, RIGHT=父LEFT+2)。核心組件：兩次批次UPDATE、一筆INSERT、索引鎖。代價：寫入放大，需交易隔離與鎖策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q7

B-Q11: Nested Set搬移子樹三步驟是什麼？
- A簡: 1)源子樹移至暫存區（負值位移）；2)目的地騰位；3)將暫存子樹平移回新位置。
- A詳: 原理：避免區間互相卡位。流程：1)將源子樹全部LEFT/RIGHT位移到負區間；2)縮小源區間、擴展目的區間以騰出足夠空間；3)將暫存區的節點整體偏移到目的區間。核心組件：三段批次UPDATE與精確位移值計算。優點：可控與安全；缺點：寫入多且需嚴謹事務。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q10, D-Q6

B-Q12: 如何取得「直屬子節點」？用Nested Set與PARENT_ID兩法？
- A簡: 法一：NOT EXISTS夾層排除；法二：額外存PARENT_ID以等值過濾，效能更直觀。
- A詳: 原理：Nested Set本質是「包含」，直屬需過濾掉中繼。流程：方法一用NOT EXISTS找在父(L,R)內、且不存在將父與它之間的中介M；方法二在模型中同時存PARENT_ID，查直屬改用WHERE PARENT_ID=@id。核心組件：LEFT/RIGHT、（選用）PARENT_ID。權衡：法二簡潔與快，代價是更新時多維護一欄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q8

B-Q13: CTE在SQL Server的執行計畫與效能關鍵？
- A簡: 遞迴CTE多次展開，索引選擇與過濾性決定成本；控制MAXRECURSION與避免跨大表Join。
- A詳: 原理：遞迴CTE每輪產生新結果集再Join，若PARENT_ID無索引將退化掃描。流程：為遞迴鍵建索引、縮小Base集、於CTE內早過濾、避免再Join大表。核心組件：適當索引、MAXRECURSION、查詢提示。觀察：Estimated/Actual計畫、子樹成本，留意Hash Join/Spill。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, A-Q16

B-Q14: 表結構與索引設計建議（DIRINFO/FILEINFO）？
- A簡: DIRINFO：主鍵、PARENT_ID/LEFT/RIGHT/Path列索引；FILEINFO：DIR_ID、EXT索引，常用查詢覆蓋索引。
- A詳: 原則：為主路徑加索引。Adjacency→PARENT_ID、ID索引；Path→各熱點層位索引；Nested Set→LEFT/RIGHT（常用LEFT為起點），可加(LEFT,RIGHT)複合。FILEINFO→(DIR_ID,EXT)複合索引、可能覆蓋(EXT,DIR_ID,NAME,SIZE)。保持統計資訊新鮮、避免過度索引造成寫入成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q8

B-Q15: 三種方案的性能觀察與典型瓶頸？
- A簡: 方案一遞迴慢；方案二查詢快但搬移重；方案三遞迴快、更新批次多。依查詢/異動分佈選擇。
- A詳: 觀察：大範圍後代查詢→方案三通常最佳；大量搬移→方案一更新最省；報表與統計→方案三O(1)/範圍有優勢；固定層級且受控→方案二可極速。瓶頸：方案一在遞迴；方案二在維護與schema限制；方案三在批次位移與鎖。建議：以實務操作比例決策，必要時混用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q10

B-Q16: 方案二為何查詢快？代價在哪？
- A簡: 把遞迴改成等值過濾＋索引Seek；代價是固定層級、搬移需欄位右移、SQL無法泛用。
- A詳: 原理：固定層欄位使查詢可走高選擇性索引，避免展開。代價：異動需大量更新列、動態SQL風險、層級超限需改表與程式。適用：層數固定、幾乎不搬移、查詢極端頻繁的場景。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q4

B-Q17: 方案三為何在大範圍遞迴查詢仍快？
- A簡: 後代查詢降為單一範圍條件，配合索引可高效掃描或Seek，避免層層展開。
- A詳: 原理：包含關係被編碼進LEFT/RIGHT的數線區間，WHERE LEFT BETWEEN L AND R即可涵蓋所有後代。索引策略使掃描局限於連續區間；JOIN FILEINFO亦以DIR_ID對應。避免多輪遞迴與Join，故在大量子孫過濾時仍表現優異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q8

B-Q18: 如何限制遞迴與避免無窮循環？
- A簡: 設定MAXRECURSION、資料層加唯一性與防環約束；查詢中早過濾、避免多表遞迴。
- A詳: 原理：遞迴影響指數級，需硬/軟限制。步驟：用OPTION(MAXRECURSION n)、建立檢查避免PARENT_ID形成環（可由觸發器或應用層防呆）、維護索引；遞迴CTE先縮小Base集。核心組件：約束、索引、提示。預防：定期校驗樹的拓撲合法性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q3

B-Q19: 如何輸出「目錄+檔案」清單並排序？
- A簡: 以UNION ALL合併兩查詢，目錄行補型別欄；ORDER BY名稱。可套用至三種方案。
- A詳: 原理：目錄與檔案來自不同表（或相同ID範圍），需組合。流程：子查詢1選DIRINFO補type='<DIR>'; 子查詢2選FILEINFO補type=''；UNION ALL合併後ORDER BY name。核心組件：兩表JOIN策略、型別欄一致化。此法不依賴模型，通用於各方案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, C-Q6

B-Q20: 為何混用多種索引可互補不足？
- A簡: 同時保留PARENT_ID與LEFT/RIGHT可兼顧直屬查詢與遞迴範圍；以空間換效能與彈性。
- A詳: 原理：不同任務最適索引不同。直屬子項→PARENT_ID最直觀；全後代→LEFT/RIGHT最佳；報表→LEFT/RIGHT + DEPTH；少量特定層→Path欄位。混用可讓SP選最佳路徑。代價是異動需同步維護多欄，需嚴謹事務與測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, D-Q10

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何實作方案一（Adjacency List）的表結構與索引？
- A簡: 建立DIRINFO(ID,PARENT_ID,NAME)與FILEINFO(DIR_ID...)，為PARENT_ID、DIR_ID加索引。
- A詳: 步驟：1)建表DIRINFO(ID PK, PARENT_ID FK NULL, NAME)；FILEINFO(ID PK, DIR_ID FK, NAME, EXT, SIZE)。2)索引：DIRINFO(PARENT_ID)、FILEINFO(DIR_ID,EXT)。程式碼片段：CREATE INDEX IX_DIR_PARENT ON DIRINFO(PARENT_ID)；IX_FILE_DIR_EXT ON FILEINFO(DIR_ID,EXT)。注意事項：避免環狀關聯、加外鍵；常用查詢欄位建立覆蓋索引。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q14

C-Q2: 如何用CTE列出指定目錄下所有子目錄與特定副檔名檔案？
- A簡: 以遞迴CTE展開後代，再JOIN FILEINFO過濾EXT並輸出清單。
- A詳: 步驟：1)WITH CTE AS (SELECT直屬 UNION ALL SELECT 子→CTE)；2)SELECT F.* FROM CTE JOIN FILEINFO F ON CTE.ID=F.DIR_ID WHERE F.EXT='.ini'；3)UNION ALL合併目錄列。程式碼片段：;WITH DIR_CTE(ID,NAME) AS (...UNION ALL...) SELECT ...。注意：設定MAXRECURSION、索引PARENT_ID、DIR_ID以提速。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q19

C-Q3: 方案一如何實作「搬移目錄」？
- A簡: 先查出來源與目的ID，UPDATE來源節點的PARENT_ID為目的ID即可。
- A詳: 步驟：1)用Self Join或CTE取來源ID(@src)、目的ID(@dest)；2)UPDATE DIRINFO SET PARENT_ID=@dest WHERE ID=@src；3)驗證：列出目的下直屬子項或用CTE檢查。SQL片段：UPDATE DIRINFO SET PARENT_ID=@dest WHERE ID=@src。注意：禁止將節點移入其子孫（需前置驗證），以免形成環。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, D-Q3

C-Q4: 方案一如何實作「刪除子樹」？
- A簡: 以CTE取得全後代ID，先刪FILEINFO，再刪DIRINFO；最後刪根節點。
- A詳: 步驟：1)CTE展開根節點所有後代；2)DELETE FILEINFO WHERE DIR_ID IN(SELECT ID FROM CTE)；3)DELETE DIRINFO WHERE ID IN(SELECT ID FROM CTE)；4)DELETE根節點。程式碼片段：;WITH CTE AS(...) DELETE ...。注意：使用交易與批次刪，防止長交易；建立適當外鍵與ON DELETE CASCADE（謹慎評估）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q8, B-Q13

C-Q5: 如何建置方案二（Path）表結構與索引？
- A簡: 建立ID01..IDN欄位存祖先鏈，針對常用層位加索引；維護資料一致性。
- A詳: 步驟：1)DIRINFO(ID, NAME, ID01..ID20)；2)索引：如IX_DIR_ID03 ON DIRINFO(ID03)等；3)INSERT/UPDATE時計算各層ID填入。程式碼片段：CREATE INDEX IX_DIR_ID03 ON DIRINFO(ID03)。注意：層數上限要足夠；多欄位一致性需SP/程式維護；避免過多索引影響寫入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q14

C-Q6: 方案二如何查詢節點下所有副檔名為.dll的檔案？
- A簡: 以對應層ID等值過濾DIRINFO，再JOIN FILEINFO過濾EXT='.dll'。
- A詳: 步驟：1)確定層位k使IDk=@node；2)SELECT F.* FROM DIRINFO D JOIN FILEINFO F ON F.DIR_ID=D.ID WHERE D.IDk=@node AND F.EXT='.dll'。程式碼片段：WHERE D.ID03=@id AND F.EXT='.dll'。注意：確保IDk與EXT上有索引；避免掃描未用層位欄。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q11

C-Q7: 方案二如何實作「搬移子樹」（欄位右移）？
- A簡: 將源子樹各列ID欄位整體右移一格，再填新祖先ID；以交易保護。
- A詳: 步驟：1)找出源子樹所有ID；2)UPDATE將ID20=ID19,...,ID04=ID03；3)填ID03..ID01為新祖先；4)驗證結果。程式碼片段：UPDATE DIRINFO SET ID20=ID19,... WHERE ID02=@srcParent。注意：SQL冗長且易錯，務必SP封裝、加測試；防止層數溢出。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q6, D-Q4

C-Q8: 如何建置方案三（Nested Set）的表與索引，並產生左右值？
- A簡: 建立LEFT/RIGHT欄位；以DFS（程式或SQL）走訪賦值；建立索引(LEFT,RIGHT)。
- A詳: 步驟：1)DIRINFO(ID, NAME, LEFT, RIGHT[, PARENT_ID, DEPTH])；2)DFS：進入節點給LEFT，回溯給RIGHT；3)索引：IX_DIR_LEFT(LEFT), IX_DIR_LEFT_RIGHT(LEFT,RIGHT)。程式碼片段：UPDATE節點SET RIGHT=@counter++於回溯。注意：用交易包覆、避免並發寫入；可在應用層產生再寫入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q14

C-Q9: 方案三如何實作「新增節點」（mkdir）？
- A簡: 於父LEFT右側騰兩格：批次UPDATE所有LEFT/RIGHT>父LEFT加2，再INSERT(L+1,L+2)。
- A詳: 步驟：1)取父(L,R)；2)UPDATE DIRINFO SET RIGHT=RIGHT+2 WHERE RIGHT>父LEFT；3)UPDATE DIRINFO SET LEFT=LEFT+2 WHERE LEFT>父LEFT；4)INSERT新節點(LEFT=父LEFT+1, RIGHT=父LEFT+2)。程式碼：見B-Q10。注意：高寫入成本，建議批次、低峰時間執行；鎖策略與索引更新要注意。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q7

C-Q10: 方案三如何實作「搬移子樹」？
- A簡: 三步：源子樹負區暫存、目的地騰位、將暫存子樹平移回新區間。
- A詳: 步驟：1)計算源子樹寬度w=(R-L+1)，將其LEFT/RIGHT整體位移至負區（OFFSET負值）；2)壓縮源區、擴展目的區以騰出w空間；3)將暫存子樹整體位移到目的地，恢復正值。程式碼片段：三段UPDATE，OFFSET精確計算。注意：全程單一交易；測試位移量與邊界；避免長時間鎖。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, D-Q6

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到「遞迴層級超出MAXRECURSION」怎麼辦？
- A簡: 降低遞迴深度、設MAXRECURSION、加索引與過濾；檢查是否存在環或異常結構。
- A詳: 症狀：CTE查詢報錯或耗時過久。原因：層級太深、資料有環、索引不足導致放大成本。解法：1)OPTION(MAXRECURSION n)；2)先以條件縮小Base集；3)索引PARENT_ID；4)資料檢查與修復環。預防：建立約束防環、監控遞迴層級分佈。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q18

D-Q2: 方案一遞迴查詢效能很差，如何改善？
- A簡: 用索引與早過濾、減少JOIN、必要時改用Nested Set或Path以範圍/等值查詢取代。
- A詳: 症狀：遞迴CTE毫秒級變秒級甚至更慢。原因：多次Join與掃描、索引缺失、資料量大。解法：1)索引PARENT_ID、ID；2)CTE內先過濾條件；3)避免CTE內JOIN大表；4)將熱路徑改Nested Set或Path。預防：根據查詢特性選擇模型與索引。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q13

D-Q3: 方案一發生「環狀關聯」導致無窮遞迴，如何診斷與防治？
- A簡: 利用檢查例程找回路、在應用與DB層加約束，禁止將節點移到其子孫之下。
- A詳: 症狀：CTE不收斂或報錯。原因：更新錯誤導致PARENT_ID形成環。解法：1)寫檢查例程找循環（如沿PARENT_ID向上追溯）；2)移除錯誤關聯；3)在SP中檢查移動合法性；4)建立約束/觸發器。預防：所有搬移操作經由SP與交易管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q18

D-Q4: 方案二搬移後出現「欄位錯位/遺漏」怎麼辦？
- A簡: 回溯交易或備份，重新以程式逐列重建ID01..IDN；加強封裝與測試避免人為錯誤。
- A詳: 症狀：路徑欄位對不上或NULL錯置。原因：手寫SQL冗長易錯、交易中途中斷。解法：1)回復備份或重跑封裝SP逐列修復；2)以程式生成與驗證欄位移位；3)補齊缺欄。預防：集中SP封裝、全面測試、引入產生式程式碼避免手工錯誤、加事務與重試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q7, B-Q6

D-Q5: 方案二需用動態SQL，如何避免SQL Injection？
- A簡: 嚴格使用參數化、欄位白名單、模板化生成；禁用直接拼接使用者輸入。
- A詳: 症狀：安全掃描或外部輸入導致異常查詢。原因：層位欄位名與值以字串拼接。解法：1)白名單選層位欄位；2)值使用參數；3)封裝API/視圖；4)審計與測試。預防：不信任任何輸入、使用ORM或SP參數化、代碼審查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q6

D-Q6: 方案三搬移子樹後LEFT/RIGHT錯置，如何修正？
- A簡: 以校驗程序檢查區間連續與包含關係，重新計算或回滾，再重跑搬移流程。
- A詳: 症狀：區間重疊或斷裂、查詢異常。原因：位移量計算錯、並發更新干擾。解法：1)驗證(L<R、整體連續、父含子)；2)回滾或批次重算整樹DFS；3)重新執行三步驟搬移。預防：單交易執行、鎖策略、離線批次、充足測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, C-Q10

D-Q7: 方案三新增/刪除導致大量更新與鎖競爭，如何處理？
- A簡: 以批次/離峰執行、縮小更新範圍、適當索引與鎖設定，必要時混用索引分攤負載。
- A詳: 症狀：INSERT/DELETE卡住或整庫緩慢。原因：騰位/回收位需大量UPDATE，鎖競爭。解法：1)小批多次、離峰；2)僅更新必要範圍；3)適當隔離級別與鎖提示；4)混存PARENT_ID供直屬查詢。預防：容量規劃、作業排程、觀測鎖等待。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q9

D-Q8: 刪除大量檔案/目錄I/O過高，如何優化？
- A簡: 先選集再批次刪、使用索引縮小掃描，控制交易大小，必要時邏輯刪除。
- A詳: 症狀：長交易、I/O飆升。原因：一次性DELETE過大、全掃描。解法：1)先以模型高效選集（CTE/LEFT/RIGHT/Path）；2)分批刪除（TOP N迴圈）；3)適當索引；4)可考慮標記刪除。預防：刪除策略標準化、監控資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q10

D-Q9: 跨DBMS移植CTE/CONNECT BY語法不相容怎麼辦？
- A簡: 改以通用模型（Nested Set/Path）與純標準SQL封裝SP，減少廠商特性依賴。
- A詳: 症狀：由Oracle遷至MySQL/MSSQL後查詢無法運行或性能不穩。原因：階層語法差異。解法：1)改用Nested Set或Path，後代查詢為標準條件；2)SP/視圖封裝；3)在新DBMS重建對應索引。預防：設計期避免綁特性、保留抽象層。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q20

D-Q10: 如何選擇三種方案？有沒有決策準則？
- A簡: 查詢占比高選Nested Set；異動搬移多選Adjacency；層級固定且可控選Path；可混用互補。
- A詳: 症狀：性能與維護拉扯。分析：若以遞迴查詢/報表為主→Nested Set；若搬移/新增頻繁→Adjacency；若層級固定、查詢極端密集→Path。解法：可同存PARENT_ID與LEFT/RIGHT，直屬用前者，後代用後者。預防：以實際負載與團隊維運能力評估，不迷信單一方案。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q15

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是樹狀資料結構？在RDBMS中如何對應？
    - A-Q2: 為何樹狀結構在RDBMS中「不自然」？
    - A-Q3: 什麼是方案一：Adjacency List（上一層ID）？
    - A-Q6: 什麼是CTE（Common Table Expression）？
    - A-Q7: 什麼是Self Join（自我連接）？
    - A-Q17: 樹狀資料常見操作有哪些？為何重要？
    - B-Q1: 方案一（Adjacency List）如何運作？核心組件與流程？
    - B-Q2: 遞迴CTE如何展開樹的子孫？執行流程與限制？
    - B-Q3: 如何找特定路徑的目錄ID（多層Self Join）？
    - C-Q1: 如何實作方案一（Adjacency List）的表結構與索引？
    - C-Q2: 如何用CTE列出指定目錄下所有子目錄與特定副檔名檔案？
    - D-Q1: 遇到「遞迴層級超出MAXRECURSION」怎麼辦？
    - A-Q15: 什麼是MAXRECURSION？何時使用？
    - A-Q16: 為何「CTE好寫」不代表「效能好」？
    - B-Q19: 如何輸出「目錄+檔案」清單並排序？

- 中級者：建議學習哪 20 題
    - A-Q4: 什麼是方案二：開欄位記錄各層ID（Path Enumeration）？
    - A-Q5: 什麼是方案三：Nested Set Model（左右索引）？
    - A-Q11: 為何要「預先維護索引」來加速樹查詢？
    - A-Q12: 三種方案的核心價值與選擇考量？
    - A-Q14: 方案二與方案三有何差異？
    - A-Q19: 什麼是SQL的「集合操作」思維？與樹查詢關係？
    - A-Q20: 左右索引的「包含」意義與節點數怎麼算？
    - B-Q4: 方案二（Path Enumeration）如何運作？核心欄位與索引？
    - B-Q5: 方案二如何查詢某節點所有後代檔案？
    - B-Q7: Nested Set如何標記LEFT/RIGHT？流程為何？
    - B-Q8: 用Nested Set查詢所有後代與混合列出目錄/檔案？
    - B-Q9: Nested Set如何計算子孫數、深度與包含關係？
    - B-Q10: Nested Set新增節點（mkdir）流程與代價？
    - B-Q14: 表結構與索引設計建議（DIRINFO/FILEINFO）？
    - B-Q17: 方案三為何在大範圍遞迴查詢仍快？
    - C-Q5: 如何建置方案二（Path）表結構與索引？
    - C-Q6: 方案二如何查詢節點下所有副檔名為.dll的檔案？
    - C-Q8: 如何建置方案三（Nested Set）的表與索引，並產生左右值？
    - C-Q9: 方案三如何實作「新增節點」（mkdir）？
    - D-Q2: 方案一遞迴查詢效能很差，如何改善？

- 高級者：建議關注哪 15 題
    - B-Q11: Nested Set搬移子樹三步驟是什麼？
    - B-Q12: 如何取得「直屬子節點」？用Nested Set與PARENT_ID兩法？
    - B-Q13: CTE在SQL Server的執行計畫與效能關鍵？
    - B-Q15: 三種方案的性能觀察與典型瓶頸？
    - B-Q16: 方案二為何查詢快？代價在哪？
    - B-Q18: 如何限制遞迴與避免無窮循環？
    - B-Q20: 為何混用多種索引可互補不足？
    - C-Q7: 方案二如何實作「搬移子樹」（欄位右移）？
    - C-Q10: 方案三如何實作「搬移子樹」？
    - D-Q3: 方案一發生「環狀關聯」導致無窮遞迴，如何診斷與防治？
    - D-Q4: 方案二搬移後出現「欄位錯位/遺漏」怎麼辦？
    - D-Q6: 方案三搬移子樹後LEFT/RIGHT錯置，如何修正？
    - D-Q7: 方案三新增/刪除導致大量更新與鎖競爭，如何處理？
    - D-Q9: 跨DBMS移植CTE/CONNECT BY語法不相容怎麼辦？
    - D-Q10: 如何選擇三種方案？有沒有決策準則？