# 後端工程師必備: CLI + PIPELINE 開發技巧 FAQ

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 CLI（Command Line Interface）？
- A簡: 命令列介面工具，以參數與標準輸入輸出操作，便於自動化、批次處理與跨語言組合。
- A詳: CLI 是以命令列為互動方式的程式，透過參數與標準輸入（STDIN）、標準輸出（STDOUT）、標準錯誤（STDERR）完成資料傳遞與回報。相較 GUI，CLI 擅長自動化、可腳本化與大規模批次處理，支援以管線（pipe）將多個工具串接組合成流程。對後端工程而言，CLI 有高可測試性、可重複性高、易整合排程或 CI/CD，且可跨語言、跨平台（Windows/Linux）互操作，是建構可靠資料處理與運維工具鏈的核心方式。
- 難度: 初級
- 學習階段: 基礎
- 関聯概念: A-Q12, A-Q27, B-Q5

Q2: 為什麼後端工程師需要熟悉 CLI？
- A簡: 為自動化、長時程任務與大資料處理提供穩定、可組合、可觀測的工作流核心能力。
- A詳: 後端任務常面對批次匯入、轉檔、背景處理與排程運行，CLI 讓任務能以腳本自動化、可重複執行並便於監控。利用 STDIO 與管線可將不同語言的工具組合，快速構建資料處理流水線。與其直接寫長駐服務，先做成 CLI 再由排程或工作排程系統驅動，能更快迭代、更易除錯、部署與回收，並在壓力與失敗時有更好復原力（分段重跑）。因此 CLI 是後端工程師必備基本功。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q27, B-Q5, C-Q9

Q3: 什麼是批次處理（Batch Processing）？
- A簡: 一次收集大量資料，分階段整批處理，強調總吞吐；首筆回應慢、暫存需求大。
- A詳: 批次處理將資料累積到一定規模後再進行計算，流程按步驟整體處理：先全部跑完 P1，再跑 P2，再 P3。優點是易於維護與最佳化每階段邏輯，總吞吐穩定；缺點是首筆結果要等整批階段結束，回應時間隨資料量線性增加，且中間半成品大量堆積，記憶體或暫存需求高。適合離線報表、夜間排程、可接受延遲的場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q8, A-Q10

Q4: 什麼是串流處理（Stream Processing）？
- A簡: 一筆到一筆處理，持續輸入、即時輸出，首筆快、資源佔用固定。
- A詳: 串流處理以資料為主軸，資料到達便處理完整流程（P1→P2→P3），然後處理下一筆。首筆回應時間為各階段延遲總和，與總筆數無關；中間半成品固定為單筆，資源占用穩定。適合需快速回饋、有限記憶體、資料源不斷產出之情境。缺點是跨階段邏輯耦合在同一段流程內，維護複雜度可能高於批次。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q9, A-Q15

Q5: 什麼是管線處理（Pipeline Processing）？
- A簡: 將流程拆為多階段並行，像生產線接力，持續產出、吞吐提升。
- A詳: 管線處理是將任務拆為多個獨立階段，各階段並行且以緩衝相連：P1 處理第 n 筆時，P2 可能處理第 n-1 筆，P3 處理第 n-2 筆。理想下，整體完成時間近似 N×max(Mi)。它兼顧串流低延遲與批次高吞吐，且讓階段邏輯分離、易維護。應用見於 CPU 指令管線、資料 ETL、生產線。前提是各階段資源不互斥，且有合適緩衝與回壓。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q5

Q6: 批次、串流、管線三者的差異是什麼？
- A簡: 批次重整批、串流重首筆、管線以併行兼顧吞吐與延遲，各自對暫存與回壓不同。
- A詳: 批次：首筆與總完成時間都受 N 影響，中間半成品最多（可至 N）。串流：首筆時間固定為 M1+M2+M3，總時間仍隨 N 成長，但半成品固定為 1。管線：首筆與串流相當，總時間趨近 N×max(Mi)，半成品約等於階段數與緩衝容量。選擇取決於目標：快首筆（串流/管線）、最佳吞吐（管線）、或簡單維護與一致性（批次）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, A-Q5, A-Q8~A-Q10

Q7: 為什麼管線能兼顧批次與串流的優點？
- A簡: 階段解耦並平行運行，透過緩衝與回壓協調速度，既快首筆又高吞吐。
- A詳: 管線將複雜流程拆為單一職責階段，各階段獨立、可優化；藉由緩衝（OS pipe 或程式內部隊列）讓上游先行，下游補上，形成接力。首筆可像串流般快速完成（M1+M2+M3），總吞吐近似 N×max(Mi)。加上分工清晰，測試、部署與重跑更靈活。前提包含：階段間資源不衝突、序維正確、回壓有效。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q15, A-Q21

Q8: 三種模式的「首筆完成時間」如何比較？
- A簡: 批次隨 N 增加；串流與管線等於 M1+M2+M3，與 N 無關。
- A詳: 批次先跑完階段再產出結果，首筆需等 N×(M1+M2+M3)。串流按筆走全流程，首筆時間為 M1+M2+M3。管線首筆也為 M1+M2+M3，因階段接力完成。對需要早回應的情境（例如即時校驗）建議串流/管線。若僅重總吞吐且可接受延遲，批次亦可。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q7

Q9: 三種模式的「總完成時間」如何比較？
- A簡: 批次與串流皆為 N×(M1+M2+M3)；管線近似 N×max(Mi)。
- A詳: 批次與串流每筆都需所有階段序列完成，因此總時間線性取決於階段時間總和。管線可重疊階段，使瓶頸成為主時延，理想為 N×max(M1,M2,M3)。若階段時間均衡（M1=M2=M3），理論吞吐可近三倍提升。實務仍受緩衝、回壓與資源競爭影響。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q15

Q10: 三種模式的「最大半成品數」如何比較？
- A簡: 批次最高可達 N；串流固定約 1；管線約為階段數與緩衝容量之和。
- A詳: 批次因整批階段分離，半成品量可等於總筆數 N，對記憶體或儲存壓力高。串流每次處理單筆，半成品固定且容易釋放。管線有每階段的中間緩衝，數目取決於階段數與緩衝大小設定（含 OS 管線緩衝）。因此管線提升吞吐，要以空間換時間，需管理中間狀態與容量回壓。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, D-Q7

Q11: 何時應用「CLI + 排程」而非長駐服務？
- A簡: 當任務可離線、需高可重跑性、易部署、可分段時，CLI 更敏捷實用。
- A詳: 長駐服務適合持續性、高可用的線上需求，但開發/部署/維運成本高。若任務為定期批次、資料轉檔、報表、生產線式處理，選 CLI 可以：快速開發、可腳本化、容易觀測與重跑；分段產物可保存與回放；失敗可局部重試；資源釋放與隔離更明確（進程生命週期）。對敏捷迭代與可靠運作更有利。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q9

Q12: 什麼是 STDIN/STDOUT/STDERR？為何重要？
- A簡: 三個標準通道：輸入、輸出與錯誤。用以串接管線並區隔資料與日誌。
- A詳: STDIN（標準輸入）提供資料來源，STDOUT（標準輸出）輸出結果，STDERR（標準錯誤）輸出錯誤或日誌。管線將前一程式的 STDOUT 銜接至下一程式的 STDIN，形成資料流。將資料與日誌分離（資料走 STDOUT、日誌走 STDERR）可避免解析混亂、便於重導向與監控。這是撰寫可靠 CLI 的基本契約。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, D-Q4

Q13: 為什麼要把日誌輸出到 STDERR？
- A簡: 保持資料流純淨，避免污染 STDOUT，便於下游解析與重導向。
- A詳: 以 JSONL 等格式經由 STDOUT 進行資料串接時，若將日誌混入會造成解析錯誤與管線中斷。分離通道可同時監看日誌（顯示或重導向到檔案），又不影響資料流。這也是可測試與可組合的關鍵：資料可直接被下一階段消費，日誌可供除錯與稽核。實務上以 Console.Error.WriteLine() 寫出。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q4, C-Q4

Q14: 什麼是 JSONL（JSON Lines）？為何適合串流？
- A簡: 每行一個獨立 JSON，逐行讀寫，天生適合無限流與管線處理。
- A詳: JSONL 使用每行一個完整 JSON 物件，便於以流式方式讀寫與分行界定；不需整體陣列包裝，無需讀完整檔才能解析。適合大量資料與長時運行情境，下游可邊讀邊處理。對 CLI 而言，使用 JsonTextReader/Writer 逐筆序列化/反序列化，避免整批載入，降低記憶體壓力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, D-Q1

Q15: C# 的 yield return 是什麼？如何幫助串流？
- A簡: 以延遲產生（lazy）方式逐筆輸出列舉元素，避免整批載入。
- A詳: yield return 讓方法成為狀態機，逐次回傳下一筆元素，呼叫端以 foreach 驅動 MoveNext() 取值。這種懶加載可構建 IEnumerable<T>→IEnumerable<T> 的「函數式管線」，每層只處理當前元素，實現自然的流式處理，減少暫存與記憶體；同時將各階段邏輯解耦，改善維護性。注意不要在管線入口 ToArray()，以免破壞流式特性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2, D-Q2

Q16: 為何 ToArray() 容易造成記憶體暴增？
- A簡: ToArray 會一次載入全部元素，失去流式處理，導致高峰記憶體佔用。
- A詳: 流式處理依賴延遲產生與逐筆處理；ToArray() 會馬上展開並複製所有元素至連續陣列，若每筆對象龐大或數量很大，瞬間佔用記憶體爆增，引發 GC 壓力甚至 OOM。在示例中，5 筆×1GB 便造成 5GB 高峰，與逐筆串流的 1~2GB 穩定大相逕庭。建議保留 IEnumerable 管線，不要於入口展開。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, B-Q8

Q17: 什麼是 Push 與 Pull 管線模式？
- A簡: Pull 由消費端拉取（yield/foreach 驅動）；Push 由生產端推送（隊列/pipe 緩衝）。
- A詳: Pull 以迭代器為中心，上游在下游呼叫 MoveNext() 時才生產資料，簡單且資源可控。Push 由上游主動推送到緩衝（如 BlockingCollection 或 OS pipe），下游就緒時消費。Push 能提高階段重疊度與吞吐，但需要緩衝與回壓控制，否則記憶體膨脹。實務常混合：下游以 Pull 消費，上游以 Push 餵入共享緩衝。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q15, D-Q7

Q18: 為什麼 OS 提供的管線（pipe）常優於自行緩衝？
- A簡: 內建阻塞 I/O 與動態緩衝，提供回壓、跨進程連接與高可靠性，減少自管風險。
- A詳: Shell 會將前程式 STDOUT 連到後程式 STDIN，中間有 OS 管理的緩衝與阻塞機制：緩衝滿則阻塞上游寫入，實現回壓；緩衝可依資料大小動態容納多筆；跨進程隔離資源，釋放更徹底。相較自行以隊列管理，不必承擔執行緒逸散、邏輯錯誤與緩衝誤設的風險，且跨語言組合更容易。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q3

Q19: 什麼是 BlockingCollection？適用在何處？
- A簡: 具上限容量的執行緒安全集合，提供生產者-消費者與回壓控制。
- A詳: BlockingCollection<T> 封裝佇列並提供容量限制、阻塞/喚醒機制及 GetConsumingEnumerable()。用於各階段間緩衝：生產者 Add，滿了即阻塞；消費者取空則等待；完成後 CompleteAdding() 通知結束。適合單進程內管線，增進階段併行度。但容量過大會占用大量記憶體，需要謹慎調參。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q7

Q20: 什麼是回壓（Backpressure）？如何體現？
- A簡: 下游處理不及時，上游因緩衝滿而被迫放慢，系統自動穩定流量。
- A詳: 在管線中若下游慢，緩衝堆積，當達容量上限時，上游寫入被阻塞（OS pipe 或 BlockingCollection），形成回壓。這避免無限制堆積，維持整體穩定。正確運用回壓能避免 OOM，但會降低上游速率，因此需平衡容量、吞吐與延遲。用日誌觀察可見各階段「最大領先筆數」被限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, D-Q3

Q21: 為什麼強調各階段資源不互斥？
- A簡: 避免相互競爭導致瓶頸同化，確保管線併行真正帶來吞吐提升。
- A詳: 若 P1、P2、P3 都重度使用同一資源（如磁碟或同一 DB 集群），即使管線並行，實際仍在爭用同一瓶頸，無法提升。理想是各階段分別使用不同資源或交錯 I/O/CPU，互補以提升硬體利用率。設計時需剖析工作型態，避免將瓶頸聚集於單點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, D-Q8

Q22: 為什麼拆成多個 CLI 有助於釋放資源？
- A簡: 每階段為獨立進程，先完成者可先退出，OS 立即回收全部資源。
- A詳: 單進程管線即使 P1 完成，進程仍持有其資源；拆成 CLI 後，P1 完成即可結束，釋放記憶體、連線與檔案描述符，降低整體占用。當下游慢，OS pipe 提供回壓，避免無限制堆積。同時可更靈活地以檔案作為邊界，支持局部重跑、分機器運行與遠端串接。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, C-Q5

Q23: 何時採用「檔案作為中繼」而非純管線直串？
- A簡: 需重跑部分階段、降依賴、縮短停機或跨機器時，建議以檔案邊界切段。
- A詳: 將某階段的 STDOUT 重導向到檔案，可離線重複消費、分析或重跑下游，無需重做上游昂貴計算。當上游需停機（如占用 DB 或鎖表）而下游可線上處理，先全速產出中繼檔再逐步消化，可縮短關鍵窗口。同時便於跨機器搬運或作為稽核憑證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, B-Q18

Q24: async/await 在管線中的價值是什麼？
- A簡: 讓同一階段能重疊等待與計算，提前準備下一筆，提升階段併行度。
- A詳: 在單進程中，將階段工作包成 Task 非同步執行，可「邊等結果邊取下一筆」，使每階段最多同時處理兩筆（上一筆等待、下一筆運行），增強重疊度並改善吞吐。其本質仍屬 Pull，但因微型緩衝而更緊湊。需留意執行緒管理與例外處理，避免造成孤兒任務與順序錯亂。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q6

Q25: C# 8 Async Streams 解決了什麼痛點？
- A簡: 將「流式」與「非同步」合一，原生支援 await foreach，語義更自然。
- A詳: 過去需以 IEnumerable 搭配 Task 手工組合，維護成本高。C# 8 的 IAsyncEnumerable<T>/await foreach 允許非同步逐筆產出，讓各階段同時具備流式與非同步優勢，減少樣板與錯誤機率。對大型資料或 I/O 密集流程特別有效。雖然本文以傳統技巧示範，Async Streams 可讓設計更簡潔直觀。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, C-Q7

Q26: 大資料序列化時需注意什麼？
- A簡: 採流式序列化/反序列化，逐筆處理，避免整批載入與巨大字串。
- A詳: 對大物件（如 1GB 緩衝）應使用 JsonSerializer 與 TextReader/Writer 逐步讀寫；反序列化用 JsonTextReader 設 SupportMultipleContent 處理多筆 JSONL；避免 JsonConvert.SerializeObject 一次建字串，以免 OOM。必要時限制單筆大小或改用更適合的序列化格式。保持資料與日誌分離確保解析穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, D-Q1

Q27: 以 CLI 組合工具集的核心價值是什麼？
- A簡: 小而專的工具可藉管線自由拼裝，跨語言、可重用、可測試且易維運。
- A詳: 每個 CLI 專注單一職責（讀、轉、寫），以 STDIO 作契約，組合成靈活流程。更容易被腳本化、納入 CI/CD 與排程；遇錯可局部重跑；可替換任一階段而不影響其他；跨平台執行。團隊維度上，降低框架綁定與學習曲線，鼓勵用基礎技術解決問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q21, C-Q10

Q28: 管線的成本與風險有哪些？
- A簡: 以空間換時間，增加中間狀態管理、緩衝調參與失敗恢復複雜度。
- A詳: 管線提升吞吐，代價是：中間緩衝占用記憶體/磁碟；需設計回壓避免堆積；多階段錯誤診斷與重試策略複雜；序列化/反序列化成本；跨進程溝通開銷。設計時需度量目標（延遲/吞吐/資源），選擇合適容量、序列化格式與分段策略，並加入觀測與重跑手段。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, B-Q15

Q29: 什麼是生產者-消費者模式？與本文關聯？
- A簡: 以緩衝協調生產與消費速度的經典並行模式，是管線的基石。
- A詳: 生產者-消費者透過佇列/緩衝解耦兩端速率，常見於 BlockingCollection 與 OS pipe。生產者 Add，消費者取；容量限制與阻塞提供回壓，避免堆積。本文的各階段就是不同生產者/消費者，藉緩衝提升重疊度並維持穩定。此模式廣泛應用於 ETL、訊息處理與串流計算。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q6

Q30: 如何用本案例向面試官說明後端能力？
- A簡: 展示對批次/串流/管線差異、回壓、流式序列化與 CLI 組合的全盤理解。
- A詳: 可描述三種模式的延遲/吞吐/半成品量公式與取捨；闡述 IEnumerable（Pull）、BlockingCollection（Push）、OS pipe 的實作差異與回壓機制；說明 JSONL 與流式序列化實務；解釋為何日誌走 STDERR；最後展示以 CLI 分階段組合與以檔案切段重跑的復原力設計。面試者能清楚折衷、量化與觀測，即可展現架構素養。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: 全部

### Q&A 類別 B: 技術原理類

Q1: IEnumerable 管線（yield）如何運作？
- A簡: 每階段以 IEnumerable<T>→IEnumerable<T>，透過 yield 延遲逐筆產出，由外層 foreach 驅動。
- A詳: 原理說明：yield return 將方法編譯為狀態機，保留迭代狀態，呼叫端 MoveNext() 觸發內部運行直到下一個 yield。關鍵流程：外層 foreach 取得 P3 的 enumerator→P3 需要 P2 的下一筆→P2 再向 P1 要→P1 再向資料源要。核心組件：IEnumerable<T>/IEnumerator<T>、yield return。此模式維持低記憶體佔用、易解耦，但為純 Pull，重疊度受限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q2, C-Q6

Q2: 外層 foreach 如何「驅動」整條管線？
- A簡: foreach 執行 MoveNext() 觸發最末階段，逐層向上游拉取，直到各階段 yield。
- A詳: 技術原理：foreach 針對最末階段的 IEnumerator<T> 呼叫 MoveNext()，該階段為了生出一筆，會向上游要求下一筆，層層傳遞直到資料源。關鍵步驟：最末階段執行→上游階段執行→直到來源→各層處理→遇 yield 回傳。核心組件：IEnumerator.MoveNext/Current。好處是簡潔與低占用；限制是重疊度需透過非同步或緩衝加強。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q1

Q3: 非同步管線（previous_result 模式）如何運作？
- A簡: 以 Task 包裝處理，邊等待上一筆，邊啟動下一筆，提升階段重疊。
- A詳: 技術原理：每階段維護一個 previous_result（Task<T>）。流程：取到一筆→若前一筆 Task 存在則等待其完成並 yield→立刻以 Task.Run 啟動當前筆→迴圈結束後等待最後一筆。核心組件：Task、GetAwaiter().GetResult()、非同步/同步邊界。此模式仍保序、每階段最多兩筆在不同狀態，提高重疊度且保持小緩衝，但需謹慎管理執行緒與例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, C-Q7, D-Q6

Q4: BlockingCollection 管線的生產者/消費者架構是什麼？
- A簡: 背景任務生產並 Add 至有限隊列，下游以 GetConsumingEnumerable 消費。
- A詳: 技術原理：以 BlockingCollection<T>（具容量）承接上游輸出。流程：啟動 Task 讀取上游逐筆處理→result.Add(model) 推入→完成後 CompleteAdding()；方法立刻 return result.GetConsumingEnumerable() 供下游 foreach 消費。核心組件：BlockingCollection、Add/Take、GetConsumingEnumerable、CompleteAdding。此模式為 Push+Pull 混合，帶回壓與更高重疊，需控制容量避免記憶體膨脹。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, A-Q20, C-Q8

Q5: OS 管線如何將 STDOUT 接到 STDIN？背後機制是什麼？
- A簡: Shell 建立 pipe 緩衝，連接前程式 STDOUT 與後程式 STDIN，滿則阻塞。
- A詳: 原理說明：Shell fork/exec 兩程式，建立匿名 pipe，將前程式 STDOUT 重導向至 pipe 的寫端、後程式 STDIN 至讀端。關鍵步驟：配置 STDIO→建立 pipe buffer→執行程式→前者 write、後者 read。核心組件：STDIN/STDOUT、pipe 緩衝、阻塞 I/O。優點：天然回壓、跨進程、資源隔離。對 CLI 管線而言幾乎零代碼即可取得高可靠緩衝。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q18, D-Q3

Q6: PUSH 與 PULL 對執行順序與吞吐的影響？
- A簡: PULL 簡潔但重疊少；PUSH 提前生產增重疊，需靠容量與回壓穩定。
- A詳: 原理：PULL 由消費端節拍決定生產時機，資源使用平穩；PUSH 讓生產端不等下游即先填緩衝，提升重疊與吞吐。步驟與組件：PULL 用 yield/foreach；PUSH 用 BlockingCollection/OS pipe。在回壓良好時 PUSH 效益高，但不當容量會導致記憶體壓力。兩者常配合使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, A-Q20, B-Q15

Q7: DEMO1~DEMO5 的效能指標如何比較？
- A簡: 批次最慢；流式首筆快；yield 管線分工佳；async/BlockingCollection 提升總吞吐。
- A詳: 指標：首筆、總時間、半成品數。DEMO1（批次）首筆與總時間皆隨 N 增；DEMO2（串流）首筆快、總時間仍線性；DEMO3（yield 管線）結構佳、延遲如串流；DEMO4（async）重疊增、總時間顯著縮短；DEMO5（BlockingCollection）重疊更高，但記憶體隨容量提高。實測顯示 async/BlockingCollection 能逼近理論管線吞吐。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6~A-Q10, B-Q15

Q8: 記憶體行為：ToArray vs yield vs async vs BlockingCollection？
- A簡: ToArray 高峰隨 N 增；yield 平穩低；async 稍增；BlockingCollection 視容量上升。
- A詳: ToArray 一次展開導致峰值等於資料數×每筆大小。yield 僅保留當前（或少量上下游）資料，內存穩定。async 每階段最多兩筆在手，峰值略高於 yield。BlockingCollection 視容量設定，同時保留多筆半成品，吞吐高、記憶體也高。設計需平衡容量與資源限制，並觀測 GC 行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q2, D-Q7

Q9: 為何 JsonSerializer 優於 JsonConvert 用於大資料？
- A簡: JsonSerializer 支援流式寫入/讀取，避免一次建大字串造成 OOM。
- A詳: 原理：JsonConvert.SerializeObject 會先建完整字串，資料大時占用巨大堆記憶體；JsonSerializer 可直接對 TextWriter/Reader 流式操作，逐步序列化/反序列化。步驟：Create()→Serialize(Console.Out,obj)；反序列化用 JsonTextReader(Console.In)+SupportMultipleContent。核心組件：JsonSerializer、JsonTextReader/Writer。對 JSONL 與無限流尤其重要。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, D-Q1

Q10: JsonTextReader 的 SupportMultipleContent 有何作用？
- A簡: 允許連續多個 JSON 物件（JSONL）逐筆解析，不需外層陣列。
- A詳: 原理：預設 Reader 期待單一 JSON；開啟 SupportMultipleContent 後，Read() 可跨越多個相鄰 JSON。步驟：new JsonTextReader(Console.In)→SupportMultipleContent=true→while(reader.Read())→Deserialize<T>(reader)。核心：逐筆解析、邊界明確。若未開啟，將在第二筆開始解析失敗或卡住。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q5, C-Q2

Q11: 為何設計每階段為 IEnumerable<T>→IEnumerable<T>？
- A簡: 保持純函數式接口，易組合、測試與替換，支援流式與延遲計算。
- A詳: 原理：每階段只關心轉換邏輯，輸入/輸出型別一致，便於接力組裝與單元測試。步驟：StreamProcessPhaseX(IEnumerable<T>) 中 yield return。組件：IEnumerable/IEnumerator。帶來：耦合低、可重用；可替換單階段而不動全局；天然支援 Pull 與延遲，記憶體友好。後續可升級為 IAsyncEnumerable。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, A-Q15

Q12: 非同步與平行的差異？在本案例如何取用？
- A簡: 非同步重疊等待與計算；平行多工同時跑。案例以非同步增加重疊度。
- A詳: 非同步（async/await）主要節省等待時間（I/O、計時器），讓執行緒可做別事；平行（多執行緒/多核心）同時運算多工作。案例中每階段仍單工（保序），透過 Task 提前啟動下一筆，實現「非同步重疊」；若要提升更高吞吐，可將瓶頸階段開多實例並行（多進程或多消費者），但需維持順序與一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, B-Q3

Q13: 回壓事件鏈如何發生？
- A簡: 下游慢→緩衝滿→上游寫入阻塞→上游速率下降→系統達成穩態。
- A詳: 原理：OS pipe 或 BlockingCollection 的容量為上限，當消費端來不及，緩衝逐步填滿。一旦滿，上游 write/Add 阻塞，直至下游消費騰出空間。步驟：監測各階段領先筆數→看到最大差距穩定。核心：阻塞 I/O、容量限制。回壓是避免 OOM 與雪崩的機制，需透過日誌與監控可視化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, D-Q3

Q14: 為何要將資料與日誌通道分離（STDERR）？
- A簡: 確保資料流可機器解析，日誌不干擾管線與下游，提升可靠性。
- A詳: 原理：資料與日誌是不同語用，混雜會破壞語法（如 JSON）導致解析失敗。步驟：資料以 Console.Out/STDOUT；日誌以 Console.Error/STDERR；指令列可分別重導向。核心組件：STDOUT/STDERR、shell 重導向。好處：可測試、可觀測、易排錯。是 CLI 契約的基本要求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, D-Q4, C-Q4

Q15: 管線緩衝容量如何影響吞吐與記憶體？
- A簡: 容量越大重疊越多、吞吐提升，但同時佔用記憶體越高，需權衡。
- A詳: 原理：容量允許上游領先筆數更大，減少等待間隙，使階段更緊湊。步驟：設定 BlockingCollection(capacity) 或利用 OS pipe 預設；觀測最大領先筆數與內存曲線。核心：容量、回壓、GC。風險：過大導致 OOM；過小吞吐受限。建議：以度量調參、找最佳點；對大物件更謹慎。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, B-Q7

Q16: 首筆延遲與總吞吐的權衡是什麼？
- A簡: 串流/管線可低首筆延遲；高吞吐需更多重疊與緩衝，會提升資源使用。
- A詳: 原理：低延遲透過邊到邊處理（串流）與階段接力（管線）；高吞吐則靠重疊度與容量提升；兩者常需權衡。步驟：定義 SLA（首筆時間、總時間）、量測瓶頸、調整容量與階段並行度。核心：延遲、吞吐、資源三角。實務：常以管線滿足兩者，並在資源範圍內調優。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q6

Q17: 多進程（多 CLI）對資源釋放與復原力的影響？
- A簡: 階段完成即可退出並釋放，崩潰隔離，分段重跑更容易。
- A詳: 原理：每階段為獨立進程，完成後由 OS 收回所有資源，降低整體占用；若某階段崩潰，不影響已完成的上游。步驟：用管線串接，或以檔案切段；重導向 STDIO。核心：進程隔離、OS 回收、可觀測性。好處：可靠性與可維護性提升，便於藍綠替換與回放測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, C-Q5

Q18: 以檔案為邊界如何在批次與管線間切換？
- A簡: 將任一階段輸出重導向檔案，之後可用 pipe 或以檔案餵入下游。
- A詳: 原理：STDOUT > file 與 type/cat file | 下游。步驟：上游輸出到檔案→下游從檔案讀取；可反覆重跑無需重做上游。核心組件：shell 重導向、JSONL。應用：縮短停機窗口、斷點接續、跨機器搬運。這讓設計同時兼顧在線（pipe）與離線（檔案）工作流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, A-Q23

Q19: CPU 指令管線與資料處理管線有何類似？
- A簡: 都是分解階段、重疊執行，使每個時脈/時間片都有工作完成。
- A詳: 原理：CPU 將指令分取指/解碼/執行/回寫，資料管線將任務切 P1/P2/P3。步驟：每階段專注子任務→設計緩衝與回壓→使不同階段在任一時刻各自處理不同實例。核心：分工、重疊、瓶頸主導。啟發：拆得越合適，理想吞吐越高；但也要防止資源爭用與危險依賴。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q15

Q20: 錯誤處理與重試在管線的佈局原則？
- A簡: 錯誤要就近捕捉、分類並產出可重跑的中繼；支援局部重試與回放。
- A詳: 原理：將錯誤責任留在階段內，輸出失敗記錄與原因到 STDERR，成功產物仍保持純淨。步驟：為每階段定義錯誤類型與重試策略；必要時落地中繼檔；提供可重跑入口。核心：可觀測、可回放、可隔離。配合文件邊界可快速重跑失敗段落，縮短恢復時間。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q1, D-Q3, C-Q5

Q21: 如何透過 STDIO 實現跨語言/跨平台組合？
- A簡: 各工具遵循「資料走 STDOUT、輸入走 STDIN、日誌走 STDERR」，即可互通。
- A詳: 原理：STDIO 與 pipe 是 OS 通用抽象，忽略語言與平台差異。步驟：工具輸出 JSONL 至 STDOUT；下一工具從 STDIN 讀取；日誌固定 STDERR；用 | 與重導向組合。核心：協議一致、邊界清楚。好處：混合技術棧，按場景選最合適語言與庫，加速交付。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, A-Q27

Q22: 為何巨大 JSON 物件容易 OOM？實務怎麼做？
- A簡: 一次建構大字串或完整物件樹耗堆記憶體；改用流式處理並限制單筆大小。
- A詳: 原理：序列化/反序列化若一次性建字串或物件樹，對 100MB 級別就可能 OOM。步驟：採 JsonSerializer + TextReader/Writer 流式讀寫；拆分大欄位（如 Buffer）或限制單筆上限；必要時選擇更高效格式。核心：流式、分塊、背壓。實測中 64MB 以上已顯示瓶頸，需審慎設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, C-Q1, C-Q2

### Q&A 類別 C: 實作應用類

Q1: 如何實作 CLI-DATA 以 JSONL 輸出資料源？
- A簡: 使用 JsonSerializer 流式序列化 DataModel 至 Console.Out，每行一筆 JSON。
- A詳: 實作步驟：1) 建立資料模型；2) JsonSerializer.Create(); 3) 迴圈產生 DataModel，序列化到 Console.Out，逐行換行。程式碼片段：
  JsonSerializer json = JsonSerializer.Create();
  json.Serialize(Console.Out, model);
  Console.Out.WriteLine();
  注意事項：避免 SerializeObject 產生大字串；Buffer 大時改小測試；確保僅輸出 JSON 至 STDOUT。最佳實踐：每筆獨立、可持續輸出，利於下游串流接收。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, A-Q14

Q2: 如何在 CLI-P1 從 STDIN 流式讀取 JSONL？
- A簡: 用 JsonTextReader(Console.In) 並設 SupportMultipleContent，逐筆 Deserialize。
- A詳: 步驟：1) var reader=new JsonTextReader(Console.In){SupportMultipleContent=true}; 2) while(reader.Read()){ var d=json.Deserialize<DataModel>(reader); … } 3) 完成後輸出處理後 JSON 至 STDOUT。片段：
  var json = JsonSerializer.Create();
  var reader = new JsonTextReader(Console.In){SupportMultipleContent=true};
  while(reader.Read()){ var d=json.Deserialize<DataModel>(reader); … }
  注意：不可讀完整檔再解析；確保資料與日誌分離。最佳實踐：逐筆處理與釋放，保持低內存。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q5

Q3: 如何串接 CLI-P1→P2→P3 並驗證管線？
- A簡: 使用管線指令串接三個 CLI，將最終輸出丟棄或檔案，觀察 STDERR 日誌。
- A詳: 步驟：1) dotnet CLI-DATA.dll | dotnet CLI-P1.dll | dotnet CLI-P2.dll | dotnet CLI-P3.dll > nul；2) 觀察每階段 STDERR 時序；3) 驗證資料有序與完成。關鍵指令：Windows 用 type 檔案 | …；Linux 用 cat 檔案 | …。注意：資料走 STDOUT，日誌走 STDERR。最佳實踐：以小資料先驗證再擴大，並記錄首筆與總時間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q4

Q4: 如何正確輸出日誌到 STDERR？
- A簡: 使用 Console.Error.WriteLine()，避免污染 STDOUT，便於下游解析與重導向。
- A詳: 步驟：1) 將所有偵錯、時序與錯誤訊息改寫至 Console.Error；2) 留意第三方庫輸出；3) shell 中以 2> logfile 重導向錯誤輸出。程式碼：Console.Error.WriteLine($"[P1] start…"); 注意：資料要純粹走 STDOUT。最佳實踐：建立統一日誌格式與層級，便於監控與排錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, D-Q4

Q5: 如何以檔案作為中繼，支援重跑與縮短停機？
- A簡: 先將上游 STDOUT > 檔案，再以 type/cat 檔案 | 下游，支援局部重跑與離線處理。
- A詳: 步驟：1) 產生資料：dotnet CLI-DATA.dll > data.jsonl；2) 重播：type data.jsonl | dotnet CLI-P1.dll …；3) 只重跑下游：type p1.jsonl | dotnet CLI-P2.dll…。注意：使用 JSONL 保持逐行完整；記錄版本與輸出校驗。最佳實踐：在關鍵邊界落地中繼，提高復原力與可觀測性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, A-Q23

Q6: 如何實作 IEnumerable 管線（yield 版）？
- A簡: 每階段方法簽名 IEnumerable<T>→IEnumerable<T>，內部 foreach + yield return。
- A詳: 步驟：
  IEnumerable<T> Phase1(IEnumerable<T> xs){ foreach(var x in xs){ Process1(x); yield return x; } }
  主程式：foreach(var _ in Phase3(Phase2(Phase1(Get())))){}
  注意：不要在入口 ToArray()；程式碼結構清晰、低內存。最佳實踐：每階段只處理單責任，避免副作用，利於測試與替換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2

Q7: 如何實作 Async 管線以提升重疊度？
- A簡: 在階段內以 Task.Run 啟動當前筆，yield 先前 Task 的結果，最後等待尾筆。
- A詳: 步驟：
  IEnumerable<T> Phase1Async(IEnumerable<T> xs){
    Task<T> prev=null;
    foreach(var x in xs){
      if(prev!=null) yield return prev.GetAwaiter().GetResult();
      prev=Task.Run(()=>{Process1(x); return x;});
    }
    if(prev!=null) yield return prev.GetAwaiter().GetResult();
  }
  注意：避免 Task 泄漏、控制同步界線。最佳實踐：只在有等待/計時的場景使用，並保序處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q6

Q8: 如何實作 BlockingCollection 管線？
- A簡: 背景任務 Add 到 BlockingCollection，方法 return GetConsumingEnumerable 供下游。
- A詳: 步驟：
  IEnumerable<T> Phase1Q(IEnumerable<T> xs){
    var q=new BlockingCollection<T>(cap);
    Task.Run(()=>{
      foreach(var x in xs){ Process1(x); q.Add(x); }
      q.CompleteAdding();
    });
    return q.GetConsumingEnumerable();
  }
  注意：設定合理容量；確保 CompleteAdding；處理 Task 異常。最佳實踐：以日誌觀察最大領先筆數與記憶體曲線，平衡吞吐與資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q15

Q9: 如何以指令列測量首筆與總時間與資源？
- A簡: 以時間戳日誌於 STDERR，shell 重導向並觀測；搭配系統監視或 Profiler。
- A詳: 步驟：1) 階段起訖 Console.Error.WriteLine 時間與序號；2) 以管線組合並 > nul；3) 透過工作管理員/htop 觀察多進程記憶體；4) VS Profiler 量單進程記憶體；5) 比較首筆與第 N 筆時序。最佳實踐：固定量測基準（筆數、大小），以圖表視覺化對比。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q8

Q10: 如何包裝成 .NET 全域工具（global tool）？
- A簡: 打包為 NuGet 套件，定義 dotnet-tool.json 與命令入口，dotnet tool install 安裝。
- A詳: 步驟：1) 建立 CLI 專案，設定 PackAsTool=true；2) 指定 ToolCommandName；3) dotnet pack 生成 nupkg；4) dotnet tool install --global <pkg>；5) 直接以命令使用。注意：維持 STDIO 契約；語意化版本；產線前於多平台驗證。最佳實踐：將每階段各自發佈，組成可共享工具集。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q27

### Q&A 類別 D: 問題解決類

Q1: 反序列化大 JSON 時發生 OutOfMemoryException 怎麼辦？
- A簡: 改用流式 JsonSerializer/JsonTextReader，逐筆處理；限制單筆大小或分塊。
- A詳: 症狀：大物件或大量資料時崩潰於序列化/反序列化。原因：一次建構大字串或完整物件樹。解決：用 JsonSerializer + TextReader/Writer 流式處理；開啟 SupportMultipleContent；將超大欄位拆分或改格式；必要時降低單筆大小。預防：壓測不同資料量、加入記憶體警示、避免 SerializeObject。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q2

Q2: 使用 ToArray() 導致記憶體爆掉怎麼辦？
- A簡: 移除 ToArray，保持 IEnumerable 串流；避免一次載入全部資料。
- A詳: 症狀：峰值記憶體隨筆數暴漲。原因：ToArray 展開並複製所有元素。解決：以 foreach 直接串流處理；保留 yield 管線；必要時以檔案分段。預防：檢查入口是否有 ToList/ToArray；以效能工具量測高峰；審視每階段是否保持流式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q8

Q3: 管線卡住或速度異常變慢怎麼辦？
- A簡: 可能緩衝滿造成回壓或下游阻塞；確認消費端是否正常讀取與容量設定。
- A詳: 症狀：上游無輸出、程式未崩潰。原因：下游慢導致 pipe/隊列滿，上游寫入阻塞；下游未讀取或崩潰。解決：檢查下游狀態；調整容量；暫存為檔案再分批處理；拆多實例處理瓶頸階段。預防：監控最大領先筆數、加入健康檢查與超時、完善錯誤告警。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q13, B-Q15

Q4: JSON 資料被日誌污染導致解析失敗怎麼辦？
- A簡: 嚴格區分資料與日誌通道，資料走 STDOUT，日誌走 STDERR。
- A詳: 症狀：下游解析 JSON 錯誤或混入非 JSON 行。原因：將日誌寫到 STDOUT。解決：改用 Console.Error.WriteLine 輸出日誌；指令列 2> log.txt 重導向；回溯修正含雜訊輸出。預防：建立通道規範與檢查；加入輸出驗證（每行為合法 JSON）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q4

Q5: 無法解析多筆 JSON（只讀到第一筆）怎麼辦？
- A簡: 啟用 JsonTextReader.SupportMultipleContent，並以 Read() 逐筆讀取。
- A詳: 症狀：只解析到第一筆或停滯。原因：Reader 預設期待單一 JSON。解決：reader.SupportMultipleContent=true；while(reader.Read()) { json.Deserialize<T>(reader); }。預防：採 JSONL 格式、寫單元測試覆蓋多筆場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q2

Q6: 非同步版本出現順序錯亂或競態怎麼辦？
- A簡: 保持每階段單工保序，僅重疊等待；小心 Task 管控與例外傳遞。
- A詳: 症狀：資料狀態不合或順序亂。原因：誤用平行，或錯誤的 await/Task 管控。解決：遵循 previous_result 模式，確保一次只處理一筆、先產生前一筆結果再啟動下一筆；將共享狀態限制在單筆內；集中處理例外。預防：以 IAsyncEnumerable 或 TPL Dataflow 管理流程；寫序列化測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q7

Q7: BlockingCollection 容量過大導致記憶體佔用高怎麼辦？
- A簡: 調小容量、觀測回壓、平衡吞吐與內存；必要時採檔案中繼。
- A詳: 症狀：記憶體上升至高峰不下。原因：緩衝中堆積太多半成品。解決：下調容量；增加下游並行度；使用 OS pipe 或以檔案切段；對大物件不建議大容量緩衝。預防：以量測找最佳容量；加入高水位告警與自動降速。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, C-Q8

Q8: 整體吞吐沒有明顯提升的原因？
- A簡: 階段瓶頸與資源爭用未解，或緩衝/回壓設定不當，導致重疊受限。
- A詳: 症狀：管線化後總時間仍接近串流或批次。原因：瓶頸階段過慢、各階段爭用同資源、緩衝太小、序列化成本過高。解決：找出瓶頸（時間與 CPU/I/O 分析）、提高瓶頸階段並行或優化邏輯、調整緩衝容量、換更高效序列化格式。預防：持續觀測與基準測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q21

Q9: 跨平台或不同 shell 行為差異造成問題怎辦？
- A簡: 確保僅依賴 STDIO/pipe 基本特性，避免依賴特定 shell 的擴充。
- A詳: 症狀：在 Windows/Linux 或 bash/cmd/powershell 表現不同。原因：管線、重導向與字元處理差異。解決：將工具設計為純 STDIO；指令相容性測試（type/cat）；避免依賴特定內建指令輸出格式；提供範例腳本。預防：CI 中加入跨平台命令測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q9

Q10: 對 GC 與記憶體釋放行為感到困惑？
- A簡: CLR 回收非即時，高峰不等於洩漏；觀測需搭配 profiler 與長時間曲線。
- A詳: 症狀：已釋放物件但記憶體未立刻下降。原因：CLR 延遲回收與分配策略。解決：用 VS Profiler/Perf 工具觀測代數、分配與峰值；避免強制 GC 影響量測；以長時間曲線判斷是否穩定。預防：保持流式、減少暫存；以容量控制緩衝；對大物件謹慎設計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q9

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 CLI（Command Line Interface）？
    - A-Q2: 為什麼後端工程師需要熟悉 CLI？
    - A-Q3: 什麼是批次處理（Batch Processing）？
    - A-Q4: 什麼是串流處理（Stream Processing）？
    - A-Q5: 什麼是管線處理（Pipeline Processing）？
    - A-Q6: 批次、串流、管線三者的差異是什麼？
    - A-Q8: 三種模式的「首筆完成時間」如何比較？
    - A-Q9: 三種模式的「總完成時間」如何比較？
    - A-Q12: 什麼是 STDIN/STDOUT/STDERR？為何重要？
    - A-Q13: 為什麼要把日誌輸出到 STDERR？
    - A-Q14: 什麼是 JSONL（JSON Lines）？為何適合串流？
    - C-Q1: 如何實作 CLI-DATA 以 JSONL 輸出資料源？
    - C-Q2: 如何在 CLI-P1 從 STDIN 流式讀取 JSONL？
    - C-Q3: 如何串接 CLI-P1→P2→P3 並驗證管線？
    - D-Q4: JSON 資料被日誌污染導致解析失敗怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q15: C# 的 yield return 是什麼？如何幫助串流？
    - A-Q16: 為何 ToArray() 容易造成記憶體暴增？
    - A-Q17: 什麼是 Push 與 Pull 管線模式？
    - A-Q18: 為什麼 OS 提供的管線常優於自行緩衝？
    - A-Q19: 什麼是 BlockingCollection？適用在何處？
    - A-Q20: 什麼是回壓（Backpressure）？如何體現？
    - A-Q22: 為什麼拆成多個 CLI 有助於釋放資源？
    - B-Q1: IEnumerable 管線（yield）如何運作？
    - B-Q3: 非同步管線（previous_result 模式）如何運作？
    - B-Q4: BlockingCollection 管線的生產者/消費者架構是什麼？
    - B-Q5: OS 管線如何將 STDOUT 接到 STDIN？背後機制是什麼？
    - B-Q7: DEMO1~DEMO5 的效能指標如何比較？
    - B-Q8: 記憶體行為：ToArray vs yield vs async vs BlockingCollection？
    - B-Q9: 為何 JsonSerializer 優於 JsonConvert 用於大資料？
    - B-Q10: JsonTextReader 的 SupportMultipleContent 有何作用？
    - C-Q6: 如何實作 IEnumerable 管線（yield 版）？
    - C-Q7: 如何實作 Async 管線以提升重疊度？
    - C-Q8: 如何實作 BlockingCollection 管線？
    - D-Q2: 使用 ToArray() 導致記憶體爆掉怎麼辦？
    - D-Q3: 管線卡住或速度異常變慢怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q21: 為什麼強調各階段資源不互斥？
    - A-Q24: async/await 在管線中的價值是什麼？
    - A-Q25: C# 8 Async Streams 解決了什麼痛點？
    - A-Q28: 管線的成本與風險有哪些？
    - B-Q6: PUSH 與 PULL 對執行順序與吞吐的影響？
    - B-Q13: 回壓事件鏈如何發生？
    - B-Q15: 管線緩衝容量如何影響吞吐與記憶體？
    - B-Q16: 首筆延遲與總吞吐的權衡是什麼？
    - B-Q17: 多進程（多 CLI）對資源釋放與復原力的影響？
    - B-Q18: 以檔案為邊界如何在批次與管線間切換？
    - B-Q20: 錯誤處理與重試在管線的佈局原則？
    - C-Q9: 如何以指令列測量首筆與總時間與資源？
    - D-Q6: 非同步版本出現順序錯亂或競態怎麼辦？
    - D-Q7: BlockingCollection 容量過大導致記憶體佔用高怎麼辦？
    - D-Q8: 整體吞吐沒有明顯提升的原因？