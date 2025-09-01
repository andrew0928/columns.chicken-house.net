# 後端工程師必備: 平行任務處理的思考練習 (FAQ)

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是本文的「平行任務處理練習」？
- A簡: 以三步驟任務 MyTask 為題，實作 Runner 在限制併發下完成大量任務，並以多項效能與資源指標評估。
- A詳: 本練習以類別 MyTask 表示單一任務，須依序呼叫 DoStepN(1)、(2)、(3) 才算完成。每步有不同耗時與併發上限，且每步開始即配置記憶體，結束才釋放。考題是撰寫 TaskRunner 完成大量 MyTask（例：1000 筆），並用 WIP、記憶體峰值、TTFT、TTLT、平均等待時間等指標檢驗「精準」掌控與效能。重點不在框架，而在如何以最少資源、最佳順序與正確節奏完成任務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, A-Q7, B-Q2

A-Q2: 為什麼要強調「精準控制」？
- A簡: 精準控制能對齊預期執行路徑、資源耗用與效能指標，避免盲目堆疊並行與浪費。
- A詳: 精準控制代表你能清楚預期程式的執行序、併發、資源與指標，並驗證結果符合預期。它能避免「多開執行緒就會快」的迷思，兼顧 WIP 與記憶體，降低成本與失敗風險。在現代雲端環境，效能與成本高度相關，僅 1% 效能差距都會反映於每月費用。精準控制也是有效調參、定位瓶頸與判斷是否已達理論極限的基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q16, D-Q9

A-Q3: MyTask 是什麼？有何規則？
- A簡: 模擬任務的類別，必須依序執行 Step1→2→3，各步有不同耗時、併發上限與記憶體配置。
- A詳: MyTask 代表單一工作單位。每個任務需依序呼叫 DoStepN(1)、DoStepN(2)、DoStepN(3) 才算完成。每步有不同時間成本與最大併發限制，並在步驟開始配置、結束釋放記憶體。這些約束讓你必須規劃併發與排程策略，平衡吞吐與資源，避免 WIP 與記憶體暴增，同時兼顧 TTFT/TTLT/AVG_WAIT 等品質指標。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q12, C-Q1

A-Q4: 為何 MyTask 的步驟必須依序執行？
- A簡: 依序性保證資料流程與生命週期正確，避免資源錯用與邏輯錯亂。
- A詳: 三步驟形成明確資料流與資源生命週期：Step1 產出中間成果並占用資源，Step2 消費並轉換，Step3 收斂並釋放。若不依序，會造成錯誤依賴、資源未釋放或非法狀態。依序性使題目具備 pipeline 特徵，促使你設計正確移交、背壓與節奏控制，以達到最佳吞吐與穩定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q14, C-Q3

A-Q5: 什麼是 WIP（Work In Progress）？
- A簡: 指當下已開始但尚未完成所有步驟的任務數量，反映同時持有資源的「半成品」量。
- A詳: WIP 是同一瞬間處於執行中（Step1 已啟動，Step3 尚未完成）任務的數量。它等於系統同時握有多少「尚未釋放資源」的半成品。WIP 越高，記憶體、暫存與上下文切換壓力越高；過低則吞吐不足。WIP 是平衡吞吐與資源成本的關鍵，常以「最大 WIP」作為品質指標之一。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q10, D-Q5

A-Q6: 為什麼要關注 WIP 與記憶體？
- A簡: 高 WIP 代表更多同時占用記憶體與資源，可能導致峰值暴衝與失敗。
- A詳: 每步驟開始就配置記憶體，直到 Step3 結束才釋放。若 WIP 過高，記憶體峰值會大幅上升，可能造成 GC 壓力、換頁或 OOM。反之若 WIP 太低會降低吞吐，延長交期。正確的併發與背壓控制能將 WIP 維持在恰當區間，兼顧 TTLT 與資源成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, D-Q4, D-Q5

A-Q7: 什麼是 TTFT（Time To First Task）？
- A簡: 自 Runner 啟動到第一個任務全部步驟完成的時間，反映使用者首次回饋速度。
- A詳: TTFT 是啟動後第一個完整任務出現所需時間，與互動體驗高度相關。良好的排程會優先「就近」推進同一任務跨步驟完成，縮短第一個結果。TTFT 受初始排程延遲、序列化程度與步驟串接緊密度影響，常用於衡量「第一個可用輸出」的快慢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, B-Q13, D-Q1

A-Q8: 什麼是 TTLT（Time To Last Task）？
- A簡: 自 Runner 啟動到最後一個任務完成的時間，代表整體處理效率與吞吐。
- A詳: TTLT 衡量整批任務全部完成所需時間，常用於批次或後台作業的整體效率評估。它受制於整體瓶頸步驟的吞吐量，對本題而言常由 Step1 決定。最佳化整體 TTLT 的策略是對準最慢步驟（瓶頸）與其上下游節奏與緩衝的協調。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q18, D-Q2

A-Q9: 什麼是平均等待時間（Average Waiting/Lead Time）？
- A簡: 所有任務從啟動到完成的時間平均，介於 TTFT 與 TTLT 之間。
- A詳: 平均等待時間計算每個任務自 Runner 啟動起到 Step3 完成的時間並取平均。它綜合反映整體排程公平性與資源分配效率，能避免僅以 TTFT 或 TTLT 評估造成的偏誤。降低平均等待時間的關鍵是平衡每步速率、減少排隊等待與上下游阻塞。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q3, A-Q7

A-Q10: Max Memory Usage（記憶體峰值）代表什麼？
- A簡: 執行期間最高的記憶體配置量，通常隨 WIP 增加而增加。
- A詳: 由於每步驟開始即配置記憶體、結束才釋放，最大記憶體使用量往往和同時在途任務（WIP）成正比。峰值過高會導致 GC 頻繁、分配失敗或 OOM。藉由控制併發與背壓、合理設計緩衝容量、縮短步驟持有時間，可有效抑制峰值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q10, D-Q4

A-Q11: 什麼是生產者-消費者模式？
- A簡: 上游生產資料、下游消費處理，透過緩衝區與通知協調速率的並行架構。
- A詳: 生產者-消費者將工作分為階段，上游產生項目放入緩衝（queue/buffer），下游從緩衝取出處理。關鍵在背壓與同步機制：滿時阻擋生產、空時阻擋消費，避免溢出與乾涸。適合本題三步驟的串接，能精準控制每步併發與 WIP。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, C-Q3

A-Q12: 本題中的「Pipeline」是什麼？
- A簡: 將三步驟分段、各自並行處理並以緩衝移交，形成串流式的生產線。
- A詳: Pipeline 將 Step1/2/3 分別以工作者群處理，彼此以有界緩衝移交，並受各步併發限制控制。好處是精準節奏控制、抑制 WIP、最大化吞吐與縮短 TTFT。缺點是需設計合適的背壓與通知，否則易造成卡住或效能不佳。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q14, C-Q3

A-Q13: BlockingCollection 與 Channel 有何差異？
- A簡: 前者以同步阻塞呼叫提供背壓；後者以非同步 await/async 提供背壓與更高彈性。
- A詳: BlockingCollection 以 TryAdd/Take 與阻塞行為簡化同步背壓，易懂好用；Channel 屬於非同步管道，透過 WaitToWrite/ReadAsync 提供可 await 的背壓，延展性與效能在特定場景更佳。兩者本質皆為緩衝與節流機制，取決於程式風格與需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q4

A-Q14: Thread、ThreadPool、Task 差異為何？
- A簡: Thread 最低階可控；ThreadPool 管理重用；Task 提供高階抽象與排程整合。
- A詳: Thread 由開發者直接建立與管理，控制最精確；ThreadPool 提供重用與排程，減少建立成本；Task 為計算抽象，交由排程器在 ThreadPool 執行，並支援連續作業、取消與例外匯流。選擇取決於精準度與維護性之權衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q6, C-Q5

A-Q15: 為什麼要先估算理論極限？
- A簡: 明確目標上限，避免無效優化與錯誤判斷，指引投資方向與停損點。
- A詳: 先估理想 TTFT/TTLT/AVG_WAIT，可衡量當前解法距離上限的差距，判斷是否值得繼續優化。接近極限時，再砸大量成本只換來微小收益應及時止損，改從架構或參數面尋求突破。這是高效工程師評估與決策的重要方法論。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q2

A-Q16: 為何 Step1 常成為瓶頸？
- A簡: 因為耗時長且併發上限相對低，單位時間吞吐最小，主導整體 TTLT。
- A詳: 題目的步驟耗時與併發上限為：Step1=867ms/5，Step2=132ms/3，Step3=430ms/3。換算吞吐，Step1 每毫秒可處理最少，故成為瓶頸。整體 TTLT 近似被瓶頸速率主導，故優化 Step1 或與上下游節奏匹配是關鍵。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q2, C-Q3

A-Q17: TTFT 與使用者體驗有何關係？
- A簡: TTFT 越低，越快看到第一個可用結果，體感速度更佳。
- A詳: 在互動性情境（如 API 回應、首屏渲染或管線下一階段依賴前一輸出）中，TTFT 影響後續能否提前啟動與回饋速度。縮短 TTFT 的策略是讓同一任務跨步驟「緊密銜接」與避免無謂排隊，而不是盲目擴大整體併發。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q1, C-Q5

A-Q18: 為何「在 Task 內控制 Semaphore」效果有限？
- A簡: 任務已排進排程才被限流，已經太晚，無法避免排隊與資源爭用。
- A詳: 若在 Task 內部才以 SemaphoreSlim.Wait 限制，任務早已被建立並交給排程，增加排隊、上下文切換與記憶體。正確作法是於排入工作前就實施節流或利用有界緩衝讓不合時機的提交被阻擋，避免「先塞隊再被擋」的浪費。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q8, C-Q7

A-Q19: CSV 日誌的 TS、MEM 代表什麼？
- A簡: TS 是自啟動的毫秒時間戳；MEM 是當下模擬記憶體使用量。
- A詳: TS（毫秒）為整體時間軸，便於將各欄位數據畫成時間序列；MEM 是該時刻累積配置的記憶體，可觀測峰值與波動。配合 WIP 與 THREADS_COUNT，可分析資源與排程關係；配合 T1~T30 可還原每執行緒活動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, C-Q9, D-Q4

A-Q20: CSV 的 THREADS_COUNT 與 T1~T30 表示什麼？
- A簡: THREADS_COUNT 為同時工作的執行緒數；T1~T30 為每執行緒當下處理的任務與步驟。
- A詳: THREADS_COUNT 可判斷實際並發度；T1~T30 以「任務#步驟」顯示各執行緒在做什麼。觀察空白區塊可識別 idle 時段與排程空洞；觀察同一任務跨步驟的相鄰性，可判斷 TTFT 是否可再降與移交是否流暢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q6, C-Q9

---

### Q&A 類別 B: 技術原理類

B-Q1: Runner 的執行流程如何運作？
- A簡: ExecuteTasks 產生任務，呼叫自訂 Run 驅動，過程記錄度量，完成後輸出 console/csv。
- A詳: 執行時，框架建立一批 MyTask（例：100/1000），呼叫你的 TaskRunnerBase.Run(IEnumerable<MyTask>)。Run 內依你的策略分派與串接步驟。框架同時監控 WIP、MEM、THREADS_COUNT、ENTER/EXIT 等指標，定期寫入 CSV，並在結束後輸出摘要（TTFT、TTLT、AVG_WAIT、峰值等）。設計重點在 Run 內部的排程與背壓。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q8, A-Q1

B-Q2: 三步驟 Pipeline 的技術架構如何設計？
- A簡: 每步建立工作者群與有界緩衝串接，按步驟上限決定並發，靠背壓協調節奏。
- A詳: 架構包含三段：Step1→(Buffer1)→Step2→(Buffer2)→Step3。每段有固定工作者數量（等於併發上限），從前一段緩衝取任務處理，完成後放入下一段。緩衝採 BlockingCollection/Channel 等，提供滿/空時的阻塞或 await，形成背壓。此設計可精準控制 WIP 與吞吐，並確保步驟順序。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q3, B-Q14

B-Q3: BlockingCollection 的背後機制是什麼？
- A簡: 以同步阻塞提供有界緩衝，滿時阻擋生產、空時阻擋消費，內含 thread-safe 容器。
- A詳: BlockingCollection 包裝 thread-safe 集合（預設 ConcurrentQueue），提供 Add/Take 與 GetConsumingEnumerable。當容量達上限 Add 會阻塞；當集合為空 Take 會阻塞。CompleteAdding 通知不再生產，消費端迭代自然結束。此同步機制簡單可靠，代價是阻塞式等待。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q3, D-Q7

B-Q4: Channel 的非同步背壓如何運作？
- A簡: 以 WaitToWrite/ReadAsync 提供可 await 的寫入/讀取，支援有界與單寫單讀等最佳化。
- A詳: Channel 提供 Writer/Reader 分離，BoundedChannelOptions 可設定容量、單寫單讀與允許同步延續等。滿時 WaitToWriteAsync 讓生產端 await；空時 WaitToReadAsync 讓消費端 await。相較 BlockingCollection，Channel 避免阻塞 thread，適合大量 async 流程與更低延遲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q4, D-Q7

B-Q5: RX 與 ContinueWith 如何形成串流管線？
- A簡: 以 Observable 將任務序列化為事件流，步驟以 Task/ContinueWith 串接，同步 Semaphore 限流。
- A詳: 將 IEnumerable 轉 Observable，透過 Select/SelectMany 投遞 Task.Run 執行步驟，並以 ContinueWith 緊接下一步，再配合 Semaphore 控制每步併發。此模式以資料流思維表達管線，順接性好；需留意限流位置與避免過度拆分 Task 造成排程抖動。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q12, C-Q5, D-Q1

B-Q6: PLINQ/Partitioner 如何切分工作與控制並行度？
- A簡: 以 Partitioner 建立分區並行處理，WithDegreeOfParallelism 可限制最大併發。
- A詳: 以 Partitioner.Create 將序列分割為多個分區，交由 Task/PLINQ 並行遍歷，減少鎖競爭。透過 AsParallel/WithDegreeOfParallelism 控制整體併發，ForAll 在各分區內處理工作。適合不需跨步驟精準編排的場景，換取簡潔與穩健的效能。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q6, A-Q14

B-Q7: 如何估算理論 TTFT/TTLT？
- A簡: TTFT 近似三步總和；TTLT 受瓶頸步驟吞吐主導，再加尾端收斂時間。
- A詳: TTFT≈Step1+Step2+Step3（若初始無爭用）。TTLT 先以瓶頸步驟計算批量時間：批數=任務數/瓶頸併發，總時≈批數×瓶頸耗時，再加上下游收斂（Step2→Step3 的最後幾批處理時間）。題例估約 174,392ms。此估算提供上限目標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q2, C-Q10

B-Q8: 如何估算平均等待時間（近似法）？
- A簡: 將批次按瓶頸節奏推進，估各批任務完成時間並取平均，可得合理近似。
- A詳: 假設穩態後由瓶頸主導，組成批次，每批完成時間約為 N×瓶頸耗時＋尾端步驟時間。對每批計算單任務完成時間，累加並除以總任務數得到平均。題中近似為約 87,868ms（文中保守估算）。此方法有誤差但足供方向判斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q7, D-Q3

B-Q9: 如何從 CSV 還原執行序列與找出空洞？
- A簡: 用 TS 對齊 T1~T30 觀察每線程當下任務；空白為 idle；檢查同任務跨步驟相鄰度。
- A詳: 將 TS 作 X 軸，在 T1~T30 欄位追蹤「任務#步驟」。相同任務跨步驟若緊鄰，TTFT 較佳；若出現長空白或步驟被插隊，代表排程空洞或背壓不當。配合 WIP/THREADS_COUNT 圖可定位是限流不足還是過排程造成的資源競爭。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q20, C-Q9, D-Q6

B-Q10: WIP 與記憶體峰值的關係是什麼？
- A簡: 每在途任務持有配置，WIP 與單任務記憶體相加近似構成峰值上界。
- A詳: 因步驟開始配置、結束釋放，任務在管線中每停留一刻都佔用記憶體。總峰值≈Σ(各步在途數×該步配置)。降低 WIP、縮短步驟佔用時間與減少中間資料，均能抑制峰值；任務分佈越平均，峰值越平滑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q4, C-Q3

B-Q11: ThreadPool SetMin/SetMaxThreads 的影響？
- A簡: 下限保障可用執行緒，避免冷啟延遲；上限避免過量排程與切換風暴。
- A詳: SetMinThreads 可在尖峰前預熱執行緒，降低首波排程延遲；SetMaxThreads 限制總並發，避免在等待型工作中造成過多上下文切換與記憶體膨脹。需與每步驟併發、緩衝設計協同調整，以免限制不一致造成窒礙。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, D-Q8, A-Q14

B-Q12: 每步併發的正確管控位置與流程為何？
- A簡: 應在提交到該步的入口處限流，而非 Task 啟動後再限流。
- A詳: 正確做法是在「放入該步緩衝前」或「取出準備處理前」就限制，確保沒有不必要的已啟動任務在排隊，避免造成排程、記憶體與切換浪費。可用有界緩衝、專屬工作者數量固定化來達成。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q3, D-Q2

B-Q13: 為何大量建立 Task 會拉高 TTFT？
- A簡: 前置建立與分派成本、插隊與重排造成首個任務跨步驟無法緊密銜接。
- A詳: 一次性產生大量 Task 丟入排程，首批任務常被後續 Task 的 Step1 插隊，導致該任務的 Step2/3延後，TTFT 拉長。最佳化是「就近推進」：盡量讓同一任務跨步驟連續處理，減少等待與上下文切換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q5, D-Q1

B-Q14: 什麼是背壓（Backpressure）？本題如何體現？
- A簡: 讓下游的處理能力反饋給上游，避免過量生產導致資源爆量或飢餓。
- A詳: 以有界緩衝與阻塞/await 讓上游在滿載時停產，待下游騰出空間再恢復。此機制將 WIP 控制在可承受範圍，防止記憶體峰值過高，也讓各步驟節奏匹配，避免 TTLT 因失衡而增長。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q3, B-Q4

B-Q15: Context Switch 計數與效能的關聯？
- A簡: 切換次數多會增加調度開銷，降低有效工作時間並影響快取與延遲。
- A詳: 過度並發或大量微小任務使切換變頻繁，CPU 時間被切換與同步消耗。觀察 Context Switch 計數可評估是否並發過度。降低方法：控制 Task 粒度、限制併發、就近推進同任務跨步驟與減少鎖競爭。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q8, C-Q5, A-Q10

B-Q16: 何時選擇「泛用排程」與「精準控制」？
- A簡: 未知負載選泛用穩健；邊界受限與目標苛刻時採精準、可控的管線。
- A詳: 若需求變化大、步驟特性未知、維護成本敏感，Task/ThreadPool/PLINQ 等泛用方案能以少量程式碼達到不錯成效。若需控制 WIP、TTFT 逼近理論極限或資源昂貴，改採 BlockingCollection/Channel+專屬工作者的精準管線較佳。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q2, C-Q3, C-Q5

B-Q17: 緩衝容量設計有哪些策略？
- A簡: 有界為主，容量貼近速率差；過大浪費資源，過小易抖動或阻塞。
- A詳: 先估步驟速率差與波動，設定小而夠用的容量平滑尖峰。觀察 WIP/MEM 與 T1~T30 空洞調整容量；必要時分層緩衝或動態調整。避免無界緩衝讓上游失控，造成記憶體峰值與 TTLT 惡化。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q7, C-Q3, C-Q4

B-Q18: 為何 TTLT 受瓶頸步驟主導？
- A簡: 系統吞吐等於最慢階段吞吐；其他階段再快也只能等待瓶頸。
- A詳: 在穩態大量任務下，系統每單位時間能完成的數量由最小吞吐的步驟決定。非瓶頸步驟若過快，只會在緩衝處等待；若過慢，則整體降速。改善 TTLT 必須提高瓶頸吞吐或平衡上下游節奏。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q2, C-Q10

B-Q19: TTFT、TTLT、AVG_WAIT 的取捨與應用？
- A簡: 互動取 TTFT；批次取 TTLT；整體公平與體感取 AVG_WAIT。
- A詳: TTFT 關注首個回應，適用互動/串接場景；TTLT 代表整體生產力，適用批次作業；平均等待反映全體使用者體驗與排程公平。實務上依產品目標權衡，並於架構與參數上做對應優化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8, A-Q9

B-Q20: 如何用 PracticeSettings 參數化問題並定位瓶頸？
- A簡: 調整步驟耗時與併發上限，觀察指標變化，找出主導效能的關鍵因素。
- A詳: 修改 PracticeSettings 中各步耗時與限制，重新執行並比對 TTFT/TTLT/AVG_WAIT、WIP、MEM 與 THREADS_COUNT。若調高某步併發/縮短耗時能大幅改善 TTLT，該步即為主要瓶頸；反之則是其他步或背壓錯位。以實驗驅動定位瓶頸。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q10, D-Q2, B-Q18

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何建立專案與 TaskRunner 骨架？
- A簡: 新建 Console 專案，引用 Core，繼承 TaskRunnerBase，覆寫 Run，Main 呼叫 ExecuteTasks(N)。
- A詳: 步驟：1) 建立 .NET Console 專案並引用 ParallelProcessPractice.Core；2) 宣告 class MyRunner: TaskRunnerBase，override Run(IEnumerable<MyTask> tasks)；3) 在 Main 內 new MyRunner() 並呼叫 ExecuteTasks(1000)。程式碼範例：class MyRunner: TaskRunnerBase { public override void Run(IEnumerable<MyTask> tasks){ /*策略*/ } }；Main: new MyRunner().ExecuteTasks(1000); 注意：Run 內需滿足步驟依序與併發限制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q3

C-Q2: 如何寫出最基礎的串行 Runner？
- A簡: 逐筆任務依序呼叫 DoStepN(1→2→3)，無並行，作為基準。
- A詳: 實作：foreach(var t in tasks){ t.DoStepN(1); t.DoStepN(2); t.DoStepN(3);} 優點：最簡單、易驗證；缺點：吞吐低、TTLT/AVG_WAIT 極差。用途：作為功能正確與效能基線，用以比較後續優化的收益。注意：雖通過規則，實務不建議上線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q7, D-Q2

C-Q3: 如何用 BlockingCollection + 專屬執行緒實作三段管線？
- A簡: 三個緩衝、三群工作者，各群數量=步驟併發上限，完成即移交，最後收斂。
- A詳: 步驟：1) 建立 queues[1..3]=BlockingCollection<MyTask>(); 2) 為步驟1/2/3各啟動工作者數量=5/3/3 的 Thread，從對應 queue 取出處理 DoStepN(step)，非最後一步則 Add 到下一 queue；3) 將 tasks 逐一 Add 到 queue1，完成後 CompleteAdding 並 Join 工作者。程式片段：workersStep1=5; workersStep2=3; workersStep3=3; 注意：用有界容量時可更嚴控 WIP；避免在 Task 內再用 Semaphore 限流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, D-Q7

C-Q4: 如何用 Channel 實作非同步生產者-消費者？
- A簡: 建立有界 Channel，Writer await WaitToWrite，Reader await WaitToRead，步驟間串接。
- A詳: 步驟：1) ch1=Channel.CreateBounded<MyTask>(cap); ch2 同理；2) 啟動 Task 處理 Step1：while(await ch1.Writer.WaitToWriteAsync()){ ch1.Writer.TryWrite(t);}；Step2 從 ch1.Reader.ReadAllAsync 取出後處理再寫入 ch2；Step3 從 ch2.Reader 取出處理。完成生產端後調用 Complete。注意：設定 SingleWriter/SingleReader 與容量，減少鎖競爭與控制 WIP。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q7, B-Q17

C-Q5: 如何用 PLINQ + ContinueWith 簡潔並行三步？
- A簡: AsParallel+WithDegreeOfParallelism 控制並行度，Task.Run 後以 ContinueWith 串接步驟。
- A詳: 步驟：tasks.AsParallel().WithDegreeOfParallelism(11).ForAll(t=>{ Task.Run(()=>t.DoStepN(1)).ContinueWith(_=>t.DoStepN(2)).ContinueWith(_=>t.DoStepN(3)).Wait();}); 關鍵：用 ContinueWith 確保同任務跨步驟「就近推進」，有助降低 TTFT；並用 WithDegreeOfParallelism 粗控整體併發。注意：此作法泛用性高，但精度與可預測性不及專屬管線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q13, D-Q1

C-Q6: 如何用 ThreadPool 並設置 Min/MaxThreads？
- A簡: 預熱與上限控制 ThreadPool，建立工作者將步驟工作排入池中執行。
- A詳: 步驟：ThreadPool.SetMinThreads(K,K); SetMaxThreads(K,K)，K≈各步上限總和+少量裕度；建立三個 JobWorker，分別消費各步緩衝並以 ThreadPool.QueueUserWorkItem 或 Task.Run 提交執行，完成後投遞至下一步，最終以事件（ManualResetEvent）通知完成。注意：上限勿大幅超出需求，避免切換風暴與記憶體峰值。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, D-Q8, B-Q2

C-Q7: 如何正確控制每步驟的並發上限？
- A簡: 在「交付至該步」前限流：固定工作者數量或用有界緩衝，而非在 Task 內用 Semaphore。
- A詳: 推薦兩法：1) 每步固定數量工作者＝上限（5/3/3），從對應緩衝取出處理；2) 使用有界緩衝（BlockingCollection/Channel）容量≈少量倍數，上游 Add/Write 時自然被阻擋。避免「先建立 Task 再 Wait」的延後限流，減少排程開銷與記憶體。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q18, D-Q2

C-Q8: 如何讀懂 console output 的效能摘要？
- A簡: 核對 PASS、Max WIP、Memory Peak、TTFT、TTLT、Average 等指標，與理想值比較。
- A詳: Console 顯示執行是否通過、最大 WIP（總/各步）、記憶體峰值、Context Switch、TTFT、TTLT、Total/Average Waiting 等。以理論值或最佳跑分作基準判斷差距與優化空間。若 TTFT 偏高，檢查初期排程；若 TTLT 偏高，檢查瓶頸步驟吞吐與背壓；若平均偏高，檢查公平性與排隊。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q8, D-Q1

C-Q9: 如何用 CSV 產生 Excel 圖表掌握執行情況？
- A簡: 用 TS 為 X 軸，分別繪製 MEM、WIP、THREADS_COUNT 曲線，觀察峰谷與趨勢。
- A詳: 將 CSV 匯入 Excel：1) TS→X 軸；2) MEM→記憶體曲線，觀察峰值與回落；3) WIP_ALL/WIP1~3→在製數量曲線；4) THREADS_COUNT→執行緒使用量；5) 以條件式格式化 T1~T30 檢視排程空洞與跨步驟銜接。藉此對照 console 指標，定位問題區。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q19, D-Q6

C-Q10: 如何調整 PracticeSettings 做壓測對比？
- A簡: 修改各步耗時與併發上限，重跑記錄指標，分析瓶頸位置與策略成效。
- A詳: 在 PracticeSettings 調整 TASK_STEPS_DURATION 與 TASK_STEPS_CONCURRENT_LIMIT，分別測試不同組合；每次執行對比 TTFT/TTLT/AVG_WAIT、WIP、MEM、THREADS_COUNT 與 T1~T30 分佈。尋找：哪個參數變動帶來最大改善、是否轉移瓶頸、緩衝容量是否需跟著調整。用資料驅動優化決策。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q20, D-Q2, B-Q18

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: TTFT 過高怎麼辦？
- A簡: 優先就近推進同一任務跨步驟、減少一次性大量排程、預熱資源。
- A詳: 症狀：第一個完成時間明顯晚。原因：初期建立大量 Task 導致插隊、步驟銜接鬆散；ThreadPool 冷啟；限流在 Task 內部。解法：以管線方式讓同一任務 Step1→2→3 緊密銜接；限制前置建立量；SetMinThreads 預熱；將節流移到提交前。預防：以 CSV 檢查同任務跨步驟相鄰性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q5, B-Q11

D-Q2: TTLT 遠大於理論值如何處理？
- A簡: 檢查瓶頸步驟是否未並行、背壓錯位或緩衝設計不當。
- A詳: 症狀：TTLT 接近某步耗時×任務數（未並行）。原因：未按每步上限開工、不當限流（如在 Task 內）、緩衝容量導致阻塞。解法：改用每步專屬工作者（5/3/3）、有界緩衝實作背壓、調整容量匹配速率差。預防：以 THREADS_COUNT、WIP1~3 驗證各步並行達標。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q3, B-Q18

D-Q3: 平均等待時間過高如何降低？
- A簡: 平衡各步速率、避免長隊尾、提升排程公平與緊密銜接。
- A詳: 症狀：AVG_WAIT 明顯高於 TTFT 與理論。原因：某步嚴重排隊、分派不均、插隊造成「餓死」。解法：調整緩衝容量與限流策略、採公平取出、避免一次性塞滿大量任務、強化就近推進。預防：以 T1~T30 與 WIP 分佈檢查長尾與空洞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q17, C-Q9

D-Q4: 記憶體峰值過高怎麼辦？
- A簡: 降低 WIP、縮短步驟持有時間、採有界緩衝與合理併發。
- A詳: 症狀：MEM 峰值接近或超過限制、GC 頻繁。原因：WIP 過高、無界緩衝、步驟佔用過久。解法：降低並發、改有界緩衝、優化步驟內分配與釋放；必要時分批處理。預防：將峰值監控納入 CI 壓測，設定告警閾值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, A-Q6, C-Q3

D-Q5: WIP 飆高導致風險，如何預防？
- A簡: 以背壓限制在製品、遵守每步併發上限、避免無界累積。
- A詳: 症狀：WIP_ALL 極高，MEM 同步上升。原因：未實施背壓、過度提交、無界緩衝。解法：有界緩衝（容量貼近速率差）、固定工作者數、動態調整容量與併發。預防：建立 WIP 上限守門與壓測，確保尖峰下不失控。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q14, B-Q17, C-Q4

D-Q6: T1~T30 呈現大量空白（閒置）如何改善？
- A簡: 提升工作分配均衡、擴充分派來源、檢查背壓與鎖競爭。
- A詳: 症狀：多執行緒長時間 idle。原因：過嚴限流、分區不均、單一來源瓶頸、鎖競爭。解法：均衡分割（Partitioner 調整）、適度提高緩衝容量、減少同步鎖、確保各步實際有足夠工作。預防：以 THREADS_COUNT 與 WIP 對照檢查配置是否合理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, C-Q9, B-Q17

D-Q7: 發生 Deadlock 或管線卡住怎麼診斷？
- A簡: 檢查 Complete/CompleteAdding 時機、寫讀不匹配、緩衝容量與通知機制。
- A詳: 症狀：執行停滯、無進度。原因：緩衝已滿且上游未被喚醒、Complete 早發、讀寫端彼此等待。解法：審視各步完成訊號順序、使用 GetConsumingEnumerable 或 ReadAllAsync 正確結束、避免雙重鎖。預防：對齊各步驟的關閉流程與例外處理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q4, C-Q3

D-Q8: Context Switch 過高導致效能差怎麼辦？
- A簡: 降低任務粒度與總併發、減少不必要 Task、改就近推進與固定工作者。
- A詳: 症狀：切換計數高、CPU 忙於切換非計算。原因：過多 Task、微任務鏈、ThreadPool 上限過大。解法：合併任務、固定每步工作者數、限制整體併發、減少跨步驟的重新排程。預防：持續監控切換指標，設定合適上限。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q15, C-Q6

D-Q9: 用 CPU 核心數作為併發限制導致效能不佳，怎麼修正？
- A簡: 依步驟併發上限與速率設計，而非硬套 CPU 核心數。
- A詳: 症狀：併發限制與題目規則不匹配，TTLT/AVG_WAIT 不佳。原因：任務非純 CPU-bound，核心數無法反映每步規則。解法：以步驟上限（5/3/3）與背壓為主設計；整體併發≈各步工作者總和或略小。預防：先估理論極限，依規則校準限流策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q12, C-Q7

D-Q10: 步驟秩序錯亂導致 TTFT 波動，如何穩定？
- A簡: 保持同任務跨步驟連續性，避免插隊；用緩衝+固定工作者。
- A詳: 症狀：第一個完成時間不穩定。原因：排程讓新任務 Step1 插隊，舊任務 Step2/3 延後。解法：管線化，完成 Step1 立即推送 Step2；Step2 完即入 Step3；減少一次性大量提交。預防：常態檢視 T1~T30 的跨步驟相鄰性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q3, C-Q5

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是本文的「平行任務處理練習」？
    - A-Q2: 為什麼要強調「精準控制」？
    - A-Q3: MyTask 是什麼？有何規則？
    - A-Q4: 為何 MyTask 的步驟必須依序執行？
    - A-Q5: 什麼是 WIP（Work In Progress）？
    - A-Q6: 為什麼要關注 WIP 與記憶體？
    - A-Q7: 什麼是 TTFT（Time To First Task）？
    - A-Q8: 什麼是 TTLT（Time To Last Task）？
    - A-Q9: 什麼是平均等待時間（Average Waiting/Lead Time）？
    - A-Q10: Max Memory Usage（記憶體峰值）代表什麼？
    - B-Q1: Runner 的執行流程如何運作？
    - C-Q1: 如何建立專案與 TaskRunner 骨架？
    - C-Q2: 如何寫出最基礎的串行 Runner？
    - C-Q8: 如何讀懂 console output 的效能摘要？
    - C-Q9: 如何用 CSV 產生 Excel 圖表掌握執行情況？
- 中級者：建議學習哪 20 題
    - A-Q11: 什麼是生產者-消費者模式？
    - A-Q12: 本題中的「Pipeline」是什麼？
    - A-Q13: BlockingCollection 與 Channel 有何差異？
    - A-Q14: Thread、ThreadPool、Task 差異為何？
    - A-Q15: 為什麼要先估算理論極限？
    - A-Q16: 為何 Step1 常成為瓶頸？
    - A-Q17: TTFT 與使用者體驗有何關係？
    - A-Q18: 為何在 Task 內控制 Semaphore 效果有限？
    - B-Q2: 三步驟 Pipeline 的技術架構如何設計？
    - B-Q3: BlockingCollection 的背後機制是什麼？
    - B-Q4: Channel 的非同步背壓如何運作？
    - B-Q6: PLINQ/Partitioner 如何切分工作與控制並行度？
    - B-Q7: 如何估算理論 TTFT/TTLT？
    - B-Q8: 如何估算平均等待時間（近似法）？
    - B-Q12: 每步併發的正確管控位置與流程為何？
    - B-Q14: 什麼是背壓（Backpressure）？本題如何體現？
    - C-Q3: 如何用 BlockingCollection + 專屬執行緒實作三段管線？
    - C-Q4: 如何用 Channel 實作非同步生產者-消費者？
    - D-Q1: TTFT 過高怎麼辦？
    - D-Q2: TTLT 遠大於理論值如何處理？
- 高級者：建議關注哪 15 題
    - B-Q5: RX 與 ContinueWith 如何形成串流管線？
    - B-Q9: 如何從 CSV 還原執行序列與找出空洞？
    - B-Q10: WIP 與記憶體峰值的關係是什麼？
    - B-Q11: ThreadPool SetMin/SetMaxThreads 的影響？
    - B-Q15: Context Switch 計數與效能的關聯？
    - B-Q16: 何時選擇「泛用排程」與「精準控制」？
    - B-Q17: 緩衝容量設計有哪些策略？
    - B-Q18: 為何 TTLT 受瓶頸步驟主導？
    - B-Q19: TTFT、TTLT、AVG_WAIT 的取捨與應用？
    - B-Q20: 如何用 PracticeSettings 參數化問題並定位瓶頸？
    - C-Q5: 如何用 PLINQ + ContinueWith 簡潔並行三步？
    - C-Q6: 如何用 ThreadPool 並設置 Min/MaxThreads？
    - C-Q7: 如何正確控制每步驟的並發上限？
    - D-Q7: 發生 Deadlock 或管線卡住怎麼診斷？
    - D-Q8: Context Switch 過高導致效能差怎麼辦？