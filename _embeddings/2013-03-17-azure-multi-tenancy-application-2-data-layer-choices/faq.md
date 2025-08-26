# [Azure] Multi-Tenancy Application #2, 資料層的選擇

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Multi-Tenancy 應用？
- A簡: 單一應用服務多個租戶，共享基礎資源，但在資料與設定上隔離。
- A詳: Multi-Tenancy 是指一個應用實例同時服務多個獨立租戶（Tenants）。它透過共享運算、儲存與網路資源降低成本，同時以邏輯或物理方式隔離各租戶的資料與設定。常見場景如 SaaS 平台，對不同公司、部門或團隊提供相同功能但各自獨立的資料視圖。關鍵價值在於規模經濟、維運簡化與快速上線，同時確保安全與隱私。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, A-Q7

A-Q2: 何謂「租戶」（Tenancy/Tenant）？
- A簡: 租戶是被服務的獨立客體，可是一家公司、部門或團隊。
- A詳: 在多租戶架構中，Tenant 指使用同一應用個體的獨立客體。以 SalesForce 為例，一家公司是一個租戶，公司下的多個帳號共享該租戶的資料邊界。租戶通常對應到隔離策略的主鍵（如 TenantId），用來區分資料、設定與資安邊界。租戶粒度可大可小，從公司到家庭或社團皆可，粒度選擇會影響資料模型、容量與擴展策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q7, B-Q7

A-Q3: 多租戶的資料層為何是關鍵？
- A簡: 資料層決定隔離方式、容量上限、效能與擴展能力。
- A詳: 多租戶資料層牽涉隔離強度（物理/邏輯）、可支撐租戶數量、資料量與查詢負載，進而影響成本與維運。不同設計（Separated DB/Schema/Shared Schema）在容量上限、共用資料處理、Scale Out 難易與最佳化空間上差異巨大。選擇資料層方案前，須以預期租戶規模與查詢模式評估，避免初期省事、後期面臨不可逆的擴展瓶頸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q8, B-Q8

A-Q4: 什麼是 Separated DB？
- A簡: 以獨立資料庫隔離每個租戶，物理隔離最強但數量受限。
- A詳: Separated DB 是為每個租戶開一個獨立資料庫，達成最強的物理隔離，便於資料搬遷與租戶級別備援。優點是隔離清晰、容易做租戶級別的 Scale Out；缺點是 SQL Server 每實例最多 32767 個資料庫，上線後受限於數量、維運成本與資源浪費（租戶多但每戶小）。共用資料與跨租戶分析也將變得困難。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q11, B-Q8

A-Q5: 什麼是 Separated Schema？
- A簡: 以同庫不同 Schema 切租戶，隔離中等、可容納更多租戶。
- A詳: Separated Schema 在單一資料庫中以不同 Schema 分租戶，隔離性較 Separated DB 弱但優於純邏輯隔離。其可容納上限由資料庫物件總數決定（SQL Server 每庫約 20 億物件），實務估算可接近數十萬租戶。優點是管理較集中、成本較低；缺點是共用資料仍難處理，且單庫成長至極大規模時的效能與維運複雜度上升。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q13, B-Q9

A-Q6: 什麼是 Shared Schema？
- A簡: 所有租戶共用表結構，以欄位（如 TenantId）實現邏輯隔離。
- A詳: Shared Schema 採單一表結構，所有租戶資料同表儲存，靠 TenantId 等欄位識別與隔離。優點是最節省資源、無 DB/Schema 數量上限、共用資料最易處理；缺點是單表資料量極大，索引與查詢最佳化要求高。適用於租戶數量龐大且可接受邏輯隔離的情境，需良好索引與分割策略以維持效能。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q14, B-Q7

A-Q7: Separated DB、Separated Schema 與 Shared Schema 有何差異？
- A簡: 差於隔離強度、可擴展上限、共用資料處理與維運成本。
- A詳: Separated DB 隔離最強、易租戶級擴展，但有限 32767 DB、維運重。Separated Schema 物件數上限高，可達數十萬租戶，但單庫龐大管理難。Shared Schema 無 DB/Schema 數量上限、共享資料最容易，但單表巨大導致索引與查詢須謹慎設計。選擇取決於租戶規模、隔離需求、共用資料比例與成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, A-Q6

A-Q8: 為何作者認為 Shared Schema 最能「搬上台面」？
- A簡: 容量上限與維運可持續，能支撐大規模租戶並處理共用資料。
- A詳: 文中指出，若租戶規模遠超數十個，Separated DB/Schema 的數量上限與維運負擔將浮現。Shared Schema 藉無上限的邏輯隔離與統一結構，避免 DB/Schema 數量限制，且共用資料處理簡單；缺點是需面對單表超大所帶來的索引與查詢最佳化挑戰。對於成長型 SaaS，Shared Schema 的可持續性更佳。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q14, A-Q28

A-Q9: 何時 Separated DB/Schema 才適用？
- A簡: 租戶數量小、強隔離需求或短期過渡時較適用。
- A詳: 文中將兩者視為「過渡」作法：當租戶僅數十、強調資料物理隔離或需快速將傳統系統改造為多租戶時，Separated DB/Schema 可降低改造成本。但一旦租戶數與資料量成長，數量上限、資源浪費與跨租戶資料難題將變成瓶頸，需考慮過渡到 Shared Schema 或 NoSQL。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, A-Q30

A-Q10: 為何不建議執行時動態建立 DB/TABLE？
- A簡: 動態建庫/表難控維運與一致性，易放大上限與管理風險。
- A詳: 在系統執行期間動態建立資料庫或資料表，會造成部署與版本控管混亂、監控與備援難度升高，也加速觸碰 DB/Schema 數量上限。文中將此視為設計禁忌，建議以穩定的資料模型與邏輯隔離（如 TenantId）取代，或採用能自動分片的儲存（如 Azure Table Storage）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, B-Q15

A-Q11: SQL Server 哪些上限會影響多租戶？
- A簡: 每實例最多 32767 資料庫、連線上限 32767、物件上限約 20 億。
- A詳: 依 SQL Server 2012 官方資料：Databases per instance 為 32767、User connections 32767、每庫資料庫物件總數上限約 2,147,483,647。採 Separated DB 會受 DB 數量上限限制；採 Separated Schema 則受物件總數上限影響。規劃時須以預估租戶數與每租戶物件數粗估可持續性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q5, B-Q9

A-Q12: 以 50000 租戶，Separated DB 會遇到什麼限制？
- A簡: 超出 32767 DB 上限，含測試/試用戶更難容納。
- A詳: 文中以 50000 租戶評估，Separated DB 每租戶一庫，單實例最多 32767 庫會成為硬限制。即便多實例分攤，維運、備份、監控與共用資料查詢極其複雜，並可能造成大量閒置資源。對熱門應用，此限制很快出現，不利長期擴展。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q8, D-Q1

A-Q13: 以 50000 租戶，Separated Schema 的理論上限為何？
- A簡: 由資料庫物件上限決定，約可支撐數十萬租戶。
- A詳: SQL Server 以資料庫物件總數計算上限（約 20 億物件）。若每租戶約產生數十至數百物件，理論上可支撐約 40 萬租戶等級。相較 Separated DB 較寬鬆；但若以部門、家庭等更細粒度作為租戶，負載仍可能逼近上限，且單庫龐大帶來管理與效能風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q11, B-Q9

A-Q14: Shared Schema 為何較不受物理上限影響？
- A簡: 無需為每租戶建立 DB/Schema，受限主要在儲存與效能。
- A詳: Shared Schema 不新增資料庫或 Schema 數量，因而避開數量上限問題。限制轉為單表資料量與索引維護成本，以及查詢優化的挑戰。只要儲存空間足夠、查詢設計妥當，較能長期支撐大規模租戶，適合成長型 SaaS 與需要頻繁跨租戶分析的情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q28, B-Q10

A-Q15: 多租戶下的共用資料應如何思考？
- A簡: 共用資料需集中管理，避免跨多 DB/Schema 的分散查詢。
- A詳: 即使是多租戶，仍有必須全域共用的資料（如系統設定、產品目錄）。在 Separated DB/Schema 下，這類資料橫跨多資料庫查詢困難；Shared Schema 或中央共用表較易處理。選擇資料層方案時，應預先規劃共用資料的存放與查詢路徑，避免後期難以整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q4, D-Q6

A-Q16: 為何資料庫比 Web 層難以 Scale Out？
- A簡: 關聯一致性與事務限制增加橫向擴展與分片複雜度。
- A詳: Web 層多為無狀態服務，易於水平擴展；資料庫需維持一致性、關聯與索引，跨節點分片會牽涉事務、查詢重寫與資料搬遷。RDBMS 常以 Partition 或分片減輕壓力，但設計、成本與維運門檻高。NoSQL（如 Azure Table Storage）藉簡化模型提升分散能力，是另一取徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q1, B-Q11

A-Q17: 什麼是資料庫 Partition？
- A簡: 將大表依鍵區段切成多分割區，分散存取與維護成本。
- A詳: Partition 是將一張大表依特定鍵（如日期、範圍、雜湊）拆分為多個邏輯分割區，以改善查詢範圍掃描與索引維護效率。對超大表（億級資料）特別有效。實作需規劃分割函數與方案，並配合查詢條件使用對應分割鍵，才能獲得效益。成本在於設計與維運複雜度。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q28, B-Q11, C-Q10

A-Q18: RDBMS 與 NoSQL 的核心差異是什麼？
- A簡: RDBMS 重一致性與關聯；NoSQL 重簡化結構與可擴展性。
- A詳: RDBMS 透過嚴謹 Schema、約束與 SQL 提供強查詢能力與一致性，但受限於橫向擴展。NoSQL（如 Key-Value）弱化關聯與 Schema，以鍵存取換取大規模分散能力。Table Storage 將 NoSQL 儲存與表格式資料存取方式結合，犧牲排序、Join、Count 等特性，換取高擴展性與成本效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, A-Q24, B-Q4

A-Q19: 什麼是 Azure Table Storage？
- A簡: Azure 的 NoSQL Key-Value 資料服務，透過 Partition/RowKey 擴展。
- A詳: Azure Table Storage 是結構化但非關聯的 Key-Value 儲存。每筆資料以 PartitionKey 與 RowKey 組成唯一索引，平台會依 Partition 將資料分布至多節點，並自動負載均衡。優點是易於水平擴展、成本低；限制包括僅針對 Partition/RowKey 有索引、無 Join/Count、排序受限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q21, B-Q1, B-Q4

A-Q20: 為何說 Azure Table Storage 適合多租戶？
- A簡: 以 PartitionKey 自然切租戶，平台自動分散負載與擴展。
- A詳: 文中指 PartitionKey/RowKey 對多租戶近乎「完美」。將 TenantId 設為 PartitionKey，可把每租戶資料聚集在同分割區，查詢高效；平台又能依 Partition 熱度自動分散至多節點，對租戶數與流量成長具高度彈性。因此特別適合租戶眾多、資料量巨大的 SaaS。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q21, B-Q2, C-Q1

A-Q21: 什麼是 PartitionKey 與 RowKey？
- A簡: 兩者構成唯一鍵與叢集索引，決定資料分布與查詢效率。
- A詳: 在 Table Storage 中，PartitionKey 決定實體屬於哪個分割區，RowKey 決定該分割區內的唯一鍵與排序。平台依 PartitionKey 做橫向分散與負載均衡；查詢若能以 PartitionKey 篩選，可精準定位資料與提升效能。兩者的組合提供唯一性，因此設計需貼合主要查詢路徑。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q2

A-Q22: PartitionKey/RowKey 為何決定查詢效能？
- A簡: 只有這組鍵受索引與排序支援，查詢須圍繞其設計。
- A詳: Table Storage 僅對 PartitionKey/RowKey 提供叢集索引與排序。若查詢不含 PartitionKey 篩選，平台難以定位分割區，效能會大幅下降；若需依其他欄位篩選或排序，通常需重塑 RowKey、做去正規化副本或改以離線計算。正確的鍵設計可換得橫向擴展下的穩定效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3, D-Q2

A-Q23: Azure Table Storage 有哪些查詢限制？
- A簡: 無 Join、無 Count、排序僅限 Partition/RowKey，分頁具挑戰。
- A詳: 官方文章與實務經驗指出：不可任意排序，僅支援按 PartitionKey+RowKey 順序；無內建 Join 與 Count，複合查詢需靠應用層拼接或預先彙總；分頁需依鍵範圍與續傳標記控制。這些限制是為了換取極高的可擴展性與成本效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, C-Q5

A-Q24: 使用 Table Storage 的取捨為何？
- A簡: 犧牲豐富查詢功能，換取高擴展性、成本與效能。
- A詳: Table Storage 放棄 RDBMS 的多欄索引、Join、Count 與自由排序，以 Partition/RowKey 為核心，達成極大規模的水平擴展與自動均衡。適用場景是租戶多、資料量巨與查詢模式可被規劃者；若需大量即席查詢與複雜報表，需搭配 RDBMS 或離線數據管線補足。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, A-Q23, B-Q12

A-Q25: 為什麼報表/聚合在 Table Storage 困難？
- A簡: 無 Count/SUM 等原生聚合與多欄索引，只能掃描或預彙總。
- A詳: Table Storage 不支援內建聚合與多欄索引，且跨分割區的聚合需掃描大量資料，成本高昂。因此常見策略是：預先彙總到計數表、使用去正規化副本、或將數據匯入可聚合的分析系統。這是以弱化查詢換取擴展性與成本的典型權衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q18, C-Q6

A-Q26: NoSQL 可如何彌補查詢不足？
- A簡: 以去正規化、預計算、平行查詢與離線處理補齊。
- A詳: 常見補法包括：建立多張以不同鍵為導向的副本表（次級索引）、預先計算彙總值、利用鍵範圍做平行查詢，或將資料匯入專用報表/分析管線（如倉儲/大數據系統）。這些策略配合正確的 Partition/RowKey 設計，可在限制下達成實務可用的查詢效能。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q18, C-Q6

A-Q27: 為何大型服務正遠離傳統關聯模型？
- A簡: 為了規模化與成本，改以簡化結構與分散式設計。
- A詳: 文中引用產業趨勢，指出大型網服（Twitter、Facebook、Bing、Google 等）以 NoSQL/分散式儲存支撐爆炸性資料量，犧牲部分查詢便利，換取可水平擴展與高可用。這並非淘汰 RDBMS，而是按需求分工：交易型使用 RDBMS，海量儲存與擴展用 NoSQL。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, A-Q24, B-Q12

A-Q28: 在 Shared Schema 下，單表過大有何風險？
- A簡: 索引維護昂貴、查詢變慢、Join 易退化，需嚴謹最佳化。
- A詳: 單表若達億級筆數，任何 Insert/Update/Delete 觸發索引維護成本，查詢稍有不慎便退化為巨量掃描；Join 對超大表影響更劇。需綜合索引設計、查詢改寫、分區與歸檔策略，並以租戶鍵做過濾與分流，維持可接受的延遲。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q11, C-Q10

A-Q29: 何謂資料本地性（Data Locality），有何價值？
- A簡: 把相關資料放近同處理節點，提升快取與查詢效率。
- A詳: 文中引用，平台會把同 Partition 的資料存放在同一節點，增進快取命中與 I/O 效率。若將租戶資料聚集在一個 Partition，可大幅提升查詢表現。設計時需在本地性（聚攏）及擴展性（多分割）間取得平衡，避免形成熱分割區。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q20, C-Q7

A-Q30: 本文的總結與推薦策略為何？
- A簡: 大規模場景選 Shared Schema 或 Table Storage，嚴謹設計鍵與查詢。
- A詳: 作者總結：Separated DB/Schema 適合過渡或小規模；大規模推薦 Shared Schema，並嚴格最佳化單表效能。若追求高擴展與自動分散，Azure Table Storage 極具優勢，需以 Partition/RowKey 驅動資料模型與查詢，並以去正規化與預彙總彌補查詢限制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q20, A-Q24

---

### Q&A 類別 B: 技術原理類

B-Q1: Azure Table Storage 如何運作？
- A簡: 以 PartitionKey 劃分資料，分散到多節點並自動負載均衡。
- A詳: 原理說明：Table Storage 以 PartitionKey 決定分割區，平台將不同分割區分配至多個儲存節點，並依使用模式自動重新平衡。關鍵流程：寫入以 PartitionKey 路由；同分割區內以 RowKey 排序；查詢依 PartitionKey 篩選提升定位效率。核心組件：分割區管理、索引（PartitionKey+RowKey）、續傳分頁機制。優勢是水平擴展與成本；限制在查詢多樣性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, A-Q21, B-Q2

B-Q2: Partition 負載均衡如何自動化？
- A簡: 監測分割區熱度，將 Partition 動態分佈至多節點。
- A詳: 原理說明：系統持續監測各 Partition 的流量與容量，將熱門分割區分散到多節點，冷分割區合併或集中，確保資源利用均衡。關鍵流程：監測→評估→重平衡→路由更新。核心組件：分割區監控、動態路由表、節點管理。開發者責任是設計良好 PartitionKey，避免形成單一熱點導致單節點瓶頸。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, A-Q29, C-Q7

B-Q3: PartitionKey/RowKey 如何構成唯一索引？
- A簡: 兩者組合為主鍵，提供叢集索引與自然排序。
- A詳: 原理說明：每筆實體需有唯一的 PartitionKey+RowKey 組合，平台據此建立叢集索引與排序序列。關鍵步驟：定義鍵→寫入→依鍵定位與排序→範圍查詢。核心組件：鍵結構、叢集索引、鍵範圍掃描。設計時 RowKey 常加入時間戳或前綴，以配合查詢順序與分頁。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q21, B-Q4, C-Q2

B-Q4: Table Storage 的索引與排序規則？
- A簡: 僅對 PartitionKey/RowKey 建叢集索引，排序亦依此兩鍵。
- A詳: 原理說明：除 PartitionKey/RowKey 外，其他屬性無索引。查詢必須盡量包含 PartitionKey，並以 RowKey 範圍達成有序讀取。關鍵流程：鍵匹配→分割區定位→基於 RowKey 的順序讀。核心組件：叢集索引、鍵範圍、續傳標記。規則導向的設計迫使開發者在資料模型階段埋好取用順序。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, A-Q23, C-Q5

B-Q5: 為何 Table Storage 不支援 Join 與 Count？
- A簡: 為提升擴展性，捨棄跨分割區的複雜查詢與全表聚合。
- A詳: 原理說明：Join 與 Count 需跨多分割區掃描與合併，會破壞系統的線性擴展與低延遲目標。關鍵步驟（替代）：以去正規化避免 Join；以預彙總避免 Count。核心組件：副本表、計數表、離線管線。這是分散式儲存的典型設計取捨。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, A-Q25, B-Q18

B-Q6: 查詢設計的關鍵步驟是什麼？
- A簡: 先定義主要查詢，反推 PartitionKey 與 RowKey 形狀。
- A詳: 原理說明：以「查詢導向建模」。步驟：盤點高頻查詢→決定 PartitionKey（縮小範圍）→設計 RowKey（排序與分頁）→必要時建立去正規化副本。核心組件：鍵策略、索引行為、分頁機制。如此可將查詢投射到平台最擅長的鍵範圍讀取。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, C-Q2, C-Q5

B-Q7: Shared Schema 如何用 TenantId 達到隔離？
- A簡: 在所有表加 TenantId，並以索引與程式過濾強制隔離。
- A詳: 原理說明：以 TenantId 作為邏輯隔離鍵，所有查詢必帶 TenantId 過濾，並建立覆合索引（TenantId, 常用條件）。關鍵步驟：模型統一化→索引設計→程式層防呆（必帶租戶條件）→稽核。核心組件：TenantId 欄、覆合索引、ORM 規則。此作法資源最省，但高度仰賴最佳化與測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q28, C-Q9

B-Q8: Separated DB 的 Scale Out 原理與限制？
- A簡: 以租戶為單位分散到多實例，易擴展但上限與維運重。
- A詳: 原理說明：每租戶一庫，跨 SQL 實例或伺服器水平擴展。關鍵流程：租戶路由→資料庫配置→跨實例監控。核心組件：連線路由、集中登錄表、備份與部署自動化。限制在 DB 數量上限、資源浪費與共用資料難題；適合租戶少且隔離要求高者。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q4, A-Q12, D-Q6

B-Q9: Separated Schema 的上限如何估算？
- A簡: 以每租戶物件數乘租戶量，受單庫物件上限約 20 億限制。
- A詳: 原理說明：SQL Server 對表、檢視、觸發器、函式等皆計入物件總數。關鍵步驟：預估每租戶物件量→乘以租戶數→對比上限→預留安全係數。核心組件：物件計數、部署規範、清理流程。理論可達數十萬租戶，但需注意單庫維運與效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q11, A-Q13

B-Q10: 單表筆數過大對索引維護有何影響？
- A簡: 資料異動成本升高，查詢與寫入延遲顯著增加。
- A詳: 原理說明：叢集與非叢集索引都需維護 B-Tree 結構；億級表異動會觸發大量頁分裂與重建。關鍵步驟（緩解）：精簡索引→批次寫入→分區表→歷史歸檔。核心組件：索引策略、分區函數、維護排程。Shared Schema 常面臨此議題，需綜合調優。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q28, C-Q10, D-Q5

B-Q11: RDBMS Partition 的原理與限制？
- A簡: 以鍵分區改善查詢與維護，但設計與成本較高。
- A詳: 原理說明：透過範圍或雜湊將表拆分；查詢帶分區鍵可精準掃描。關鍵步驟：選鍵→定義函數/方案→索引對齊→應用改寫。核心組件：分區表、分區索引、維護策略。限制在設計複雜與跨分區查詢成本，需和歸檔搭配。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q17, A-Q28, C-Q10

B-Q12: Table Storage 與 RDBMS 的分工邏輯？
- A簡: Table 存巨量高擴展資料，RDBMS 處理複雜查詢與交易。
- A詳: 原理說明：以用途分工。Table Storage 承載高寫入量與大表；RDBMS 承擔交易一致性、複雜查詢與報表。關鍵步驟：界定資料域→選擇儲存→設計同步或管線。核心組件：資料同步、去正規化表、分析匯入。此混合能取兩者之長。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q24, A-Q25, C-Q6

B-Q13: 如何在 Table Storage 實現二級索引？
- A簡: 以去正規化建立多張以不同鍵為主的副本表。
- A詳: 原理說明：為替代多欄索引，依查詢維度建立副本，每張表有各自的 Partition/RowKey。關鍵步驟：盤點查詢→定義副本鍵→寫入時同步多表→確保最終一致。核心組件：副本表、寫入管線、重試補償。可顯著提升查詢但增加寫入成本。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q26, C-Q6, D-Q9

B-Q14: 多租戶共用資料在三種架構如何處理？
- A簡: Separated DB/Schema 困難；Shared Schema/集中表最簡。
- A詳: 原理說明：Separated DB/Schema 下共用資料分散，各庫查詢整合成本高；Shared Schema 可放全域 Partition 或共用表集中管理。關鍵步驟：識別共用域→集中化→提供租戶無關 API。核心組件：全域資料表、快取層、版本控管。可顯著簡化查詢與維運。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q4, D-Q6

B-Q15: 為何動態建 DB/TABLE 被視為禁忌？
- A簡: 造成版本散逸、監控與備援破碎、觸碰上限更快。
- A詳: 原理說明：執行期動態建庫表使結構難以一致，部署與資料遷移複雜，監控與備份策略無法標準化。關鍵影響：維運不可預測、擴展上限更快遇到。核心建議：採邏輯隔離、穩定模型、基礎設施即程式（IaC）統一管理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q8, C-Q8

B-Q16: 查詢模式如何反推 PartitionKey 設計？
- A簡: 以最高頻、最高成本查詢為主，確保含 PartitionKey 篩選。
- A詳: 原理說明：分析前 80% 查詢，確保都能以 PartitionKey 精準定位，RowKey 提供排序與範圍。關鍵步驟：查詢盤點→鍵候選設計→壓力測試→調整。核心組件：查詢日誌、鍵評估矩陣、基準測試。此法可最大化鍵索引優勢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q1, D-Q2

B-Q17: 分頁在 Table Storage 的原理與挑戰？
- A簡: 依 RowKey 有序讀取並用續傳標記；跨條件排序受限。
- A詳: 原理說明：結果依 PartitionKey+RowKey 排序，SDK 返回 continuation token 作為下一頁起點。關鍵步驟：固定排序鍵→保存續傳標記→避免插入導致頁漂移。核心組件：RowKey 設計、ContinuationToken、範圍查詢。挑戰是無法依任意欄位排序與穩定分頁。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, C-Q5, D-Q8

B-Q18: 報表/統計在 NoSQL 的策略性原理？
- A簡: 以預彙總、事件驅動更新與離線批處理達成。
- A詳: 原理說明：將聚合轉為寫入時或排程任務更新；以事件（新增/刪除）驅動計數表；大型分析以離線批處理完成。關鍵步驟：定義指標→設計聚合表→寫入同步→校正機制。核心組件：計數表、事件總線、ETL/ELT。避免昂貴的全表掃描。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q25, C-Q6, D-Q4

B-Q19: 多租戶資料隔離的安全面向？
- A簡: 物理隔離最強，邏輯隔離需程式與索引強制與稽核。
- A詳: 原理說明：Separated DB 提供物理邊界；Shared Schema 以 TenantId 邏輯隔離，須在應用層強制帶條件、資料庫層建立覆合索引，並透過稽核與測試驗證。關鍵步驟：強制過濾→最小權限→審計。核心組件：TenantId 規範、權限模型、日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q9, C-Q9

B-Q20: 何謂熱分割區（Hot Partition），如何避免？
- A簡: 單一 Partition 流量過高成瓶頸；以分散鍵或哈希避免。
- A詳: 原理說明：同一 Partition 由單節點服務，熱租戶或熱門鍵集中將限縮吞吐。關鍵步驟：檢測熱度→鍵重設（如加上哈希前綴）→流量切分。核心組件：鍵設計策略、監控告警、資料重分布。需在本地性與分散性間權衡。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q29, C-Q7, D-Q2

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 Table Storage 建模多租戶（PartitionKey=TenantId）？
- A簡: 將 TenantId 作為 PartitionKey，RowKey 作唯一鍵或排序鍵。
- A詳: 
  - 實作步驟: 
    1) 定義資料實體含 PartitionKey=TenantId。2) 規劃 RowKey（如 GUID 或 time-based）。3) 建立表與 CRUD。 
  - 程式碼:
    ```csharp
    public class OrderEntity : ITableEntity {
      public string PartitionKey { get; set; } // TenantId
      public string RowKey { get; set; }       // OrderId
      public DateTimeOffset? Timestamp { get; set; }
      public ETag ETag { get; set; }
      public string Status { get; set; }
    }
    var client = new TableClient(conn, "Orders");
    await client.AddEntityAsync(new OrderEntity { PartitionKey=tenantId, RowKey=orderId, Status="New" });
    ```
  - 注意: 所有查詢必帶 PartitionKey；規劃 RowKey 以支援排序/分頁。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q20, A-Q21, B-Q6

C-Q2: 如何設計 RowKey 支援排序與範圍查詢？
- A簡: 使用可比較字串，如「yyyyMMddHHmmss_序號」或複合鍵。
- A詳:
  - 步驟: 1) 明確排序需求（時間、狀態）。2) 將排序欄位編碼到 RowKey 前綴。3) 使用範圍查詢。
  - 程式碼:
    ```csharp
    // 以時間排序
    var rowKey = $"{createdAt:yyyyMMddHHmmss}_{orderId}";
    // 範圍查詢
    var filter = TableClient.CreateQueryFilter($"PartitionKey eq {tenantId} and RowKey ge {startKey} and RowKey lt {endKey}");
    var rows = client.Query<OrderEntity>(filter);
    ```
  - 注意: RowKey 要保持固定長度/可比較；避免含不可排序片段在前綴。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, B-Q4, B-Q17

C-Q3: 如何查詢單一租戶資料避免全表掃描？
- A簡: 查詢條件必含 PartitionKey；再以 RowKey 範圍縮小。
- A詳:
  - 步驟: 1) 以 PartitionKey=TenantId 篩選。2) 加入 RowKey 範圍或屬性過濾。3) 以分頁讀取。
  - 程式碼:
    ```csharp
    var filter = TableClient.CreateQueryFilter($"PartitionKey eq {tenantId}");
    Pageable<OrderEntity> page = client.Query<OrderEntity>(filter, maxPerPage: 1000);
    ```
  - 注意: 其他屬性過濾會在伺服端/用戶端進行，效率不及鍵範圍；先用鍵縮小集合。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q22, B-Q6, D-Q2

C-Q4: 如何實作跨租戶的共用資料？
- A簡: 使用固定 PartitionKey（如 "global"）集中儲存與快取。
- A詳:
  - 步驟: 1) 建立 Global 表或在同表使用 PartitionKey="global"。2) 定義 RowKey 為類型/代碼。3) 查詢時不帶租戶鍵。 
  - 程式碼:
    ```csharp
    var entity = new ConfigEntity { PartitionKey="global", RowKey="ProductCatalogVersion", Value="v123" };
    await client.UpsertEntityAsync(entity);
    ```
  - 注意: 結合快取層降低讀放大；權限控管與版本管理要明確。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q14, D-Q6

C-Q5: 如何在 Table Storage 做分頁？
- A簡: 依 PartitionKey+RowKey 順序讀，使用 continuation token。
- A詳:
  - 步驟: 1) 固定鍵排序。2) 呼叫 Query 並保存 ContinuationToken。3) 以 token 取得下一頁。 
  - 程式碼:
    ```csharp
    var pages = client.Query<OrderEntity>(filter, maxPerPage: 100).AsPages();
    foreach (var page in pages) {
      var token = page.ContinuationToken; // 保存以取下一頁
    }
    ```
  - 注意: 不支援任意欄位排序；資料插入可能導致頁漂移，需以鍵或時間窗口穩定頁面。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, B-Q17, D-Q8

C-Q6: 如何實作統計/計數（Count）？
- A簡: 維護計數表或預彙總，避免全表掃描。
- A詳:
  - 步驟: 1) 設計 CounterEntity（PartitionKey=TenantId, RowKey=Metric）。2) 寫入/刪除時同步增減。3) 週期校正。 
  - 程式碼:
    ```csharp
    public class CounterEntity : ITableEntity { /* PK: tenantId, RK: "Orders.Count" */ public int Value {get;set;} }
    // 原子增量：先讀後寫，失敗重試（樂觀併發）
    ```
  - 注意: 處理重試與併發；可用離線批次重新彙總校正。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q25, B-Q18, D-Q4

C-Q7: 如何避免熱分割區（Hot Partition）？
- A簡: 將熱門鍵分散，採哈希前綴或時間分片設計鍵。
- A詳:
  - 步驟: 1) 監控 Partition 熱度。2) 調整 PartitionKey（如 $"{tenantId}-{hash(userId)%16}"）。3) 讀時合併多分割結果。 
  - 程式碼:
    ```csharp
    string pk = $"{tenantId}-{userId.GetHashCode() & 0x0F}";
    ```
  - 注意: 平衡本地性與分散性；必要時僅熱租戶採分散策略。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q29, B-Q20, D-Q2

C-Q8: 如何從 Separated DB/Schema 遷移到 Shared Schema 或 Table Storage？
- A簡: 盤點模型與查詢，重構鍵與索引，分批遷移與雙寫驗證。
- A詳:
  - 步驟: 1) 盤點實體與查詢模式。2) 設計 TenantId 與索引（Shared Schema）或 Partition/RowKey（Table）。3) 建立雙寫與校驗流程。4) 分租戶/分表遷移與回切計畫。 
  - 注意: 嚴格資料對帳、壓測與回復預案；先遷移共用與低風險模組。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q9, B-Q12

C-Q9: Shared Schema 下如何設計 TenantId 索引與安全過濾？
- A簡: 建複合索引（TenantId, 常用條件），強制 ORM 帶租戶條件。
- A詳:
  - 步驟: 1) 所有表加入 TenantId。2) 常用查詢建立覆合索引（TenantId, CreatedAt/Status）。3) ORM/儲存層攔截器強制附加 TenantId 條件。4) 稽核異常查詢。 
  - 注意: 測試中注入遺漏租戶條件用例；整體查詢計畫需以租戶鍵為前導。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q9, A-Q28

C-Q10: 如何規劃 RDBMS 分區或分割表支撐超大表？
- A簡: 以日期/租戶鍵分區，索引對齊並搭配歸檔與維護。
- A詳:
  - 步驟: 1) 選擇分區鍵（如日期）。2) 建立分區函數/方案。3) 建立對齊分區索引。4) 設置滾動歸檔與維護排程。 
  - 注意: 查詢必帶分區鍵；避免跨分區 Join；監控分區傾斜與維護時間窗。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, A-Q28, D-Q5

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: Separated DB 遇到 32767 資料庫上限怎麼辦？
- A簡: 合併為 Shared Schema 或改 NoSQL；以租戶分片多實例分流。
- A詳:
  - 症狀: 新租戶無法配置 DB，維運爆炸。 
  - 原因: SQL Server 每實例 DB 上限；資源浪費。 
  - 解決步驟: 1) 規劃轉 Shared Schema 或 Table Storage。2) 臨時以多實例與租戶分片分流。3) 設定共用資料集中化。 
  - 預防: 初期以可擴展架構設計，避免每租戶一庫。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q8, C-Q8

D-Q2: 查詢效能差，未使用 PartitionKey 過濾怎麼辦？
- A簡: 重寫查詢與模型，確保以 PartitionKey 篩選、RowKey 範圍。
- A詳:
  - 症狀: Table Storage 查詢延遲高、吞吐低。 
  - 原因: 未使用 PartitionKey 篩選，導致跨分割區掃描。 
  - 解決步驟: 1) 重寫查詢加入 PartitionKey。2) 以 RowKey 範圍限定。3) 必要時建立去正規化副本。 
  - 預防: 鍵導向建模與查詢審查。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q22, B-Q6, C-Q3

D-Q3: 需要按非 RowKey 欄位排序怎麼辦？
- A簡: 將排序欄位編碼進 RowKey，或用副本表與客端排序。
- A詳:
  - 症狀: 需依金額/名稱排序的查詢變慢。 
  - 原因: 僅支持 PartitionKey+RowKey 排序。 
  - 解決步驟: 1) 重設 RowKey 前綴含排序欄位。2) 建立以該欄位為鍵的副本表。3) 小集合用客端排序。 
  - 預防: 需求盤點時先決定排序鍵，避免事後重構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q2, B-Q13

D-Q4: 報表需要 Count/SUM，Table Storage 怎麼辦？
- A簡: 預先維護計數/彙總表，或離線批次計算再查詢。
- A詳:
  - 症狀: 即時計數掃描慢、費用高。 
  - 原因: 無原生 Count/SUM、跨分割區聚合昂貴。 
  - 解決步驟: 1) 設計 Counter/Aggregate 表。2) 寫入路徑同步更新。3) 定期校正與回填。 
  - 預防: 指標驅動設計，避免臨時性全表掃描。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q25, B-Q18, C-Q6

D-Q5: 單表破億筆，寫入/查詢變慢怎麼辦？
- A簡: 精簡索引、批次寫入、分區/歸檔與查詢重寫。
- A詳:
  - 症狀: DML 延遲高、索引維護時間長、查詢計畫差。 
  - 原因: 索引繁多、表過大、無分區/歸檔。 
  - 解決步驟: 1) 刪冗餘索引。2) 批次/延遲寫入。3) 分區與歷史歸檔。4) 以租戶鍵/日期改寫查詢。 
  - 預防: 成長預估與容量規劃，建立維護排程。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q28, B-Q10, C-Q10

D-Q6: 跨上千 DB 查詢共用資料很痛怎麼辦？
- A簡: 將共用資料集中化或改 Shared Schema/NoSQL 持有。
- A詳:
  - 症狀: 多庫 Join/聚合不可行，查詢與維運失控。 
  - 原因: Separated DB 天生難處理共用資料。 
  - 解決步驟: 1) 建立共用資料中心庫/表。2) 改為 Shared Schema 全域 Partition。3) 暫以同步管線維持一致。 
  - 預防: 初期即識別共用域並集中化設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q14, C-Q4

D-Q7: 動態建立 DB/TABLE 導致維運混亂如何補救？
- A簡: 凍結結構、回收合併、導入 IaC 與邏輯隔離遷移。
- A詳:
  - 症狀: 結構版本不一致、備份與監控難。 
  - 原因: 執行期動態建庫表無治理。 
  - 解決步驟: 1) 停止動態建表。2) 合併至 Shared Schema。3) 以 IaC 管控基礎設施。4) 補齊版本與遷移腳本。 
  - 預防: 設計禁用動態建庫表，流程化變更管理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q15, C-Q8

D-Q8: Table Storage 分頁出現亂跳或重複怎麼辦？
- A簡: 使用 continuation token 與穩定 RowKey，避免中途插入干擾。
- A詳:
  - 症狀: 使用者翻頁資料重複或遺漏。 
  - 原因: 分頁依鍵排序，新寫入改變集合；未正確使用 token。 
  - 解決步驟: 1) 固定 RowKey 排序（時間窗口）。2) 僅用 continuation token 取得下一頁。3) 大資料集使用快照標記。 
  - 預防: 設計可重入分頁流程與鍵策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, C-Q5, A-Q23

D-Q9: 多租戶需要 Join 怎麼辦？
- A簡: 去正規化預計算關聯，或將該用例改用 RDBMS。
- A詳:
  - 症狀: Table Storage 查詢需跨多表關聯，效能差。 
  - 原因: 無 Join 支援。 
  - 解決步驟: 1) 建立關聯視圖表（副本表）。2) 寫入時同步填充。3) 對高複雜 Join 場景，改 RDBMS 執行。 
  - 預防: 以查詢導向建模，避免線上臨時 Join。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q13, C-Q9

D-Q10: Separated DB 數量多但每租戶人少造成資源浪費？
- A簡: 整併為 Shared Schema 或租戶池化，提升密度。
- A詳:
  - 症狀: 記憶體/連線耗費在大量小 DB，成本高。 
  - 原因: 每租戶一庫導致固定開銷放大。 
  - 解決步驟: 1) 盤點低活躍租戶整併。2) 導入 Shared Schema。3) 以多租戶連線路由池化。 
  - 預防: 初期評估租戶活躍分布，避免過度切割。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q8, C-Q8

---

### 學習路徑索引
- 初學者：建議先學習 15 題
    - A-Q1: 什麼是 Multi-Tenancy 應用？
    - A-Q2: 何謂「租戶」（Tenancy/Tenant）？
    - A-Q3: 多租戶的資料層為何是關鍵？
    - A-Q4: 什麼是 Separated DB？
    - A-Q5: 什麼是 Separated Schema？
    - A-Q6: 什麼是 Shared Schema？
    - A-Q7: 三種資料層方案有何差異？
    - A-Q8: 為何 Shared Schema 更可持續？
    - A-Q11: SQL Server 哪些上限會影響多租戶？
    - A-Q14: Shared Schema 為何較不受物理上限影響？
    - A-Q18: RDBMS 與 NoSQL 的核心差異是什麼？
    - A-Q19: 什麼是 Azure Table Storage？
    - A-Q21: 什麼是 PartitionKey 與 RowKey？
    - A-Q23: Azure Table Storage 有哪些查詢限制？
    - A-Q24: 使用 Table Storage 的取捨為何？

- 中級者：建議學習 20 題
    - B-Q1: Azure Table Storage 如何運作？
    - B-Q2: Partition 負載均衡如何自動化？
    - B-Q3: PartitionKey/RowKey 如何構成唯一索引？
    - B-Q4: Table Storage 的索引與排序規則？
    - B-Q5: 為何 Table Storage 不支援 Join 與 Count？
    - B-Q6: 查詢設計的關鍵步驟是什麼？
    - C-Q1: 如何用 Table Storage 建模多租戶？
    - C-Q2: 如何設計 RowKey 支援排序與範圍查詢？
    - C-Q3: 如何查詢單一租戶資料避免全表掃描？
    - C-Q5: 如何在 Table Storage 做分頁？
    - C-Q6: 如何實作統計/計數（Count）？
    - A-Q15: 多租戶下的共用資料應如何思考？
    - B-Q14: 多租戶共用資料在三種架構如何處理？
    - D-Q2: 查詢效能差，未使用 PartitionKey 過濾怎麼辦？
    - D-Q3: 需要按非 RowKey 欄位排序怎麼辦？
    - D-Q4: 報表需要 Count/SUM，Table Storage 怎麼辦？
    - A-Q28: Shared Schema 單表過大風險？
    - B-Q10: 單表筆數過大對索引維護影響？
    - B-Q7: Shared Schema 如何用 TenantId 隔離？
    - C-Q9: Shared Schema 索引與安全過濾

- 高級者：建議關注 15 題
    - B-Q11: RDBMS Partition 的原理與限制？
    - C-Q10: 如何規劃分區或分割表支撐超大表？
    - B-Q13: 如何在 Table Storage 實現二級索引？
    - B-Q18: 報表/統計在 NoSQL 的策略性原理？
    - B-Q20: 何謂熱分割區與避免原理？
    - C-Q7: 如何避免熱分割區？
    - C-Q8: 從 Separated DB/Schema 遷移到 Shared Schema/Table？
    - D-Q1: Separated DB 遇到上限怎麼辦？
    - D-Q5: 單表破億筆，寫入/查詢變慢怎麼辦？
    - D-Q6: 跨上千 DB 查詢共用資料怎麼辦？
    - D-Q8: Table Storage 分頁亂跳或重複怎麼辦？
    - D-Q9: 多租戶需要 Join 怎麼辦？
    - A-Q26: NoSQL 如何彌補查詢不足？
    - A-Q29: 何謂資料本地性，其價值？
    - A-Q30: 本文總結與推薦策略為何？