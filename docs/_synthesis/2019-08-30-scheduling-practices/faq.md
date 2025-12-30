---
layout: synthesis
title: "後端工程師必備: 排程任務的處理機制練習 (12/01 補完)"
synthesis_type: faq
source_post: /2019/08/30/scheduling-practices/
redirect_from:
  - /2019/08/30/scheduling-practices/faq/
---

# 後端工程師必備: 排程任務的處理機制練習

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是資料庫輪詢式排程服務？
- A簡: 以資料庫儲存排程，排程器定期輪詢查詢到期工作，鎖定後執行，並記錄實際執行時間與狀態。
- A詳: 輪詢式排程服務將預約任務寫入資料庫，由排程器以固定頻率查詢「已到預定時間且尚未執行」的工作，嘗試鎖定成功後執行，最後更新實際執行時間與狀態。它不依賴資料庫主動通知，適合在無法使用事件或訊息總線延時機制時自建，核心是「少查詢、準時啟動、不重複執行、可高可用」。常見於 Web App 需由伺服器在未來特定時間執行動作的場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, B-Q3

Q2: 為何 Web App 的 Request/Response 模型不擅長預約排程？
- A簡: 因為屬被動處理，有請求才有回應，無法自動在未來時間點主動執行工作。
- A詳: 傳統 Web 應用多採 Request/Response 模式，伺服器只在收到請求時才運作，並回應後結束流程。排程任務需要在無外部請求的情況下「主動」於特定時間點觸發，與被動響應模型天然不相容。因此需另建長執行服務或背景工作者，負責監看資料庫、判斷任務到期並啟動執行，以補足 Web 層的不足。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q9

Q3: 排程任務表 Jobs 的欄位與意義是什麼？
- A簡: CreateAt 建立時間、RunAt 預定時間、ExecuteAt 實際時間、State 狀態(0未執行/1執行中/2完成)。
- A詳: Jobs 表含核心欄位：CreateAt 表示任務資料建立時間；RunAt 為預計執行時間；ExecuteAt 記錄實際觸發執行的時間；State 表示狀態（0：未執行、1：執行中、2：已完成）。以此能計算前置時間（RunAt-CreateAt）與延遲（ExecuteAt-RunAt），同時配合鎖定機制避免重複執行，是評估精確與成本的重要依據。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q3, B-Q11

Q4: 什麼是 MinPrepareTime 與 MaxDelayTime？
- A簡: 最小準備時間與最大容許延遲，規定任務最晚入庫與最慢啟動的邊界。
- A詳: MinPrepareTime 表示任務排入資料庫時，距離預定執行時間至少保留的準備時間（例：10 秒），確保排程器能提前看到任務；MaxDelayTime 表示任務可接受的最大延遲（例：30 秒），若超出視為不合格。兩者為排程精確度與可靠度的約束前提，也是輪詢頻率與策略設計的根據。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q6, B-Q11

Q5: 為何不直接用 Message Queue 延遲消費實現預約？
- A簡: 訊息隊列適合即時排隊，不適合長時間占位延遲，會占用資源且難以精準控制。
- A詳: Queue 天生是即時消費模型，訊息入列後應盡速消費；若用來「佔位」等待數分鐘甚至數小時，會造成佇列資源與可見性問題、難管理重試與撤回，也不易動態調整時間。改以資料庫儲存 RunAt，排程器輪詢精準到秒並提前鎖定更可控，亦易做統計與審計。Queue 可搭配短延遲或工作分發，但不適合長延時預約。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q17, A-Q1

Q6: 輪詢頻率、精確度與成本的關係？
- A簡: 輪詢越頻繁越精準也越耗 DB；從分到秒成本乘以 60 倍，需權衡。
- A詳: 將輪詢間隔由分鐘縮至秒，能降低平均延遲與標準差，但也讓資料庫查詢次數成倍增加。文章以 COST_SCORE 度量查清單、鎖定、查單筆的權重成本；EFFICIENT_SCORE 衡量延遲平均與標準差。設計需在精確與成本間折衷，並用預抓、提前鎖定、抖動、退避等策略同時兼顧。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q10, B-Q7

Q7: 本題對高可用/分散式的要求是什麼？
- A簡: 允許同時跑多個實例互為備援，遇中斷可續跑且不重複執行。
- A詳: 排程服務需支援同時啟動多個 instance，互相競爭/協作處理任務；任意實例被中斷或重啟，系統仍能完成所有任務且不重複執行。實作上需用資料庫鎖定機制（如 AcquireJobLock）保證唯一執行，並正確處理優雅關機、重啟後續接，通過 HATEST 模擬反覆啟停檢驗韌性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, D-Q4

Q8: 為何「同一 Job 不能執行兩次」很重要？
- A簡: 重複執行會造成副作用或重複出貨扣款，破壞資料一致性。
- A詳: 多實例併發環境下，若同一任務被多次執行，可能導致重複寄送、重複修改狀態、金流重複扣款等嚴重後果。因此必須在資料層或應用層採用強鎖定與狀態機控（如 0→1→2），保證僅一實例能從未執行轉為執行中，再轉完成。這是分散式排程最關鍵的正確性要求。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q4

Q9: 什麼是 COST_SCORE（成本評分）？
- A簡: 以查清單、鎖定、查單筆的次數乘權重加總，越低代表對 DB 負擔越小。
- A詳: 成本評分用三項統計反映對 DB 的壓力：查詢清單次數×100、嘗試鎖定次數×10、查詢單筆次數×1。分數越低越好。設計時可藉由預抓、先查再鎖、減少空輪詢、退避等技巧降低該分數，與 EFFICIENT_SCORE 共同衡量方案優劣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q7

Q10: 什麼是 EFFICIENT_SCORE（精確度評分）？
- A簡: 所有任務延遲平均值加標準差，越低代表越準時且穩定。
- A詳: 精確度評分為 Avg(ExecuteAt-RunAt)+Stdev(ExecuteAt-RunAt)，兼顧準時程度與穩定性。平均越小表示越準時，標準差越小代表波動越低。可透過更精準等待點、提前鎖定、抖動避碰與適度平行化提升；但需避免 EARLY_EXEC（早於 RunAt 執行）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q18

Q11: 為何本題不採用資料庫主動通知？
- A簡: 題目限制為純輪詢解，假設 DB 僅能被動查詢，不含通知基礎設施。
- A詳: 實務上有 SQL Notification 等主動通知機制，但並非所有環境與版本具備，且跨雲/自管 DB/多語言整合成本高。本練習刻意限制只用輪詢，訓練在通用、低依賴場景下仍能達到高可用與高精確的能力，亦利於評估與對照現成解法優劣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q1

Q12: 什麼是 Busy Waiting？缺點是什麼？
- A簡: 以迴圈不斷檢查條件等待，造成 CPU 空轉、能耗高、干擾其他任務。
- A詳: Busy waiting 指以短迴圈輪詢時間或狀態來等待某時刻，CPU 反覆醒來檢查，不做實際工作。缺點是持續占用 CPU、無法被精準中斷、在多工作環境下干擾其他運行，且不易配合優雅關機。應改為事件/定時器/Task.Delay 等阻塞式或非同步等待方式。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q6

Q13: BlockingCollection 與 Channel 差異是什麼？
- A簡: 前者同步友善、生消封裝簡單；後者原生非同步、效能好、控制更細緻。
- A詳: BlockingCollection 提供 thread-safe 同步佇列，簡易解決生產者-消費者問題；但若需端到端 async，常需再包 Task。Channel 為高效非同步資料通道，支援單讀/單寫優化、背壓與 async API，適合極端吞吐與低延遲場景。兩者皆可用於分派 job，選擇取決於風格與效能需求。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q2, C-Q3

Q14: ThreadPool 與自管 Thread 的差異？
- A簡: ThreadPool 適合短任務多量；長時間常駐任務宜自管 Thread 避免資源枯竭。
- A詳: ThreadPool 針對大量短小工作的重複建立/回收最優；但長時間常駐 worker 會佔住池中執行緒，影響系統其他任務產生飢餓或死鎖。自管 Thread 適合固定、長時間的後台輪詢/等待，成本可控且可明確終止，避免汙染全域池資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, D-Q5

Q15: 提前鎖定（EARLY_LOCK）與準時鎖定有何差異？
- A簡: 提前鎖可降低延遲但提升風險；準時鎖安全但可能多併發碰撞。
- A詳: 提前在 RunAt 前一小段時間 AcquireJobLock，可把「建連/查詢/鎖定」耗時排除在延遲之外，提升 EFFICIENT_SCORE；但會增加關機時「鎖後未處理」風險。準時鎖則較安全，卻易在多實例同時爭鎖下造成多次失敗與成本升高。可用抖動分散碰撞、限制提前時間上限、關機排空等折衷。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q20, D-Q4

Q16: 什麼是 HATEST？驗證哪些能力？
- A簡: 高可用測試腳本，反覆啟停多實例，驗證不中斷、不重複且無超時執行。
- A詳: HATEST 以腳本在 10 分鐘測試窗內啟動多個實例，隨機在 10~30 秒間對每個實例反覆 Stop/Start，結束後檢查：建立數=成功數、無 EARLY_EXEC、無超時、無例外。用以驗證優雅關機、恢復、正確鎖定與不重複執行，確保方案具韌性與可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, D-Q5

Q17: .NET Generic Host/BackgroundService 的價值？
- A簡: 提供長時服務骨架，支援 systemd/Windows Service、優雅關機與 DI。
- A詳: .NET Generic Host 抽象長時間服務的生命週期，BackgroundService 可簡潔實作 ExecuteAsync，並與 DI、Logging 整合；支援在容器、systemd、Windows Service 部署。可攔截關閉訊號，協調優雅關機，搭配 CancellationToken 停止輪詢與工作分派，提升 HA 測試通過率。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q1, B-Q9

Q18: 合格的通過條件有哪些？
- A簡: 任務全完成、前置時間皆≥MinPrepare、延遲皆≤MaxDelay。
- A詳: 驗證完賽需同時滿足：1) 所有任務 State=2（完成）；2) 每筆 RunAt-CreateAt ≥ MinPrepareTime；3) 每筆 ExecuteAt-RunAt ≤ MaxDelayTime。若違反則不計分。其上再評比 COST_SCORE 與 EFFICIENT_SCORE，綜合衡量解法成本與準時穩定性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, A-Q10, B-Q11

---

### Q&A 類別 B: 技術原理類

Q1: 輪詢式排程整體如何運作？
- A簡: 週期抓未來短窗任務，提前鎖定，到點執行並更新狀態記錄。
- A詳: 原理為：1) 以固定節奏（依 MinPrepareTime 設計）呼叫 GetReadyJobs(duration) 取得到期與即將到期工作；2) 視策略先查單筆狀態再 AcquireJobLock，避免重複執行；3) 使用阻塞或非同步等待至 RunAt；4) 呼叫 ProcessLockedJob 寫入 ExecuteAt 與狀態；5) 全程紀錄查詢/鎖定/完成以供計分與追蹤。核心組件：JobsRepo（Dapper SQL）、分派佇列（BlockingCollection/Channel）、工作執行緒、時間控制器與關機協調器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, C-Q2

Q2: GetReadyJobs(duration) 的使用流程？
- A簡: 取得到期與未來短時間內需執行的清單，供分派與提前處理。
- A詳: 呼叫 GetReadyJobs() 可抓取「已到 RunAt 且未執行」的工作；帶入 duration（例 10 秒）可預抓未來短窗任務，用以提前鎖定與排序。常見流程：抓清單→依 RunAt 排序→分派至佇列/通道→後續工作者等待與執行。配合索引（RunAt, State）可降低掃描成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q4

Q3: AcquireJobLock 與 ProcessLockedJob 的機制？
- A簡: 先搶唯一鎖避免重複，鎖成後再執行並寫入 ExecuteAt/完成狀態。
- A詳: AcquireJobLock 以資料庫層面原子操作嘗試將 Job 由未執行轉為執行中（0→1），只允許一個實例成功，避免重入。ProcessLockedJob 僅接受已鎖定工作，執行模擬處理（有延遲/併行上限），並更新 ExecuteAt 與狀態完成（1→2）。此兩步構成「唯一執行」與「完成記錄」的核心。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, D-Q4

Q4: 如何避免同一 Job 被多實例重複執行？
- A簡: 以狀態機+原子鎖定，僅允許一次 0→1→2 的合法轉換。
- A詳: 透過資料庫層面鎖定（UPDATE with conditions 或等效原子操作）確保只有一個執行緒將 State 由 0 改為 1。其他執行緒會鎖定失敗而放棄。完成後再將 1 設為 2。搭配提前查單筆（GetJob）可減少無謂的鎖定嘗試以節省 COST_SCORE。多實例下此設計是線性化保護關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, D-Q4

Q5: 提前鎖定與「抖動」(jitter)的原理？
- A簡: 在 RunAt 前小窗鎖定，加入隨機偏移分散同時碰撞。
- A詳: 提前鎖定可把建構/連線/鎖定耗時移出延遲計算；但多實例可能同時搶鎖，造成大量無效嘗試。加入隨機抖動（例如 RunAt 前 300–1700ms 隨機）可錯開實例搶鎖時間，降低鎖碰撞與 COST_SCORE，同時仍保留足夠緩衝避免 EARLY_EXEC。關機時需保證已鎖定工作能被處理或回收。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q20, C-Q5

Q6: 如何將延遲精準控制到秒級？
- A簡: 使用非同步等待到 RunAt、提前鎖定、減少臨界前開銷。
- A詳: 先以 GetReadyJobs 預抓，再在 RunAt 前小窗 AcquireJobLock，之後使用 Task.Delay/計時器等阻塞或非同步等待至 RunAt，立即 ProcessLockedJob。避免在臨界點才做昂貴操作（連線、查詢），並優化分派與執行緒數量，消化同時到期的多筆任務。必要時用專屬執行緒避免 ThreadPool 干擾。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, C-Q9

Q7: 如何降低 COST_SCORE？權重設計的意義？
- A簡: 減少清單掃描與鎖定嘗試，先查單筆、退避與預抓小窗。
- A詳: 因清單掃描權重最高（×100），應拉長查詢間隔至 MinPrepare 範圍、預抓短窗避免頻繁空掃。鎖定權重其次（×10），可先 GetJob 判斷需不需要鎖，並用抖動減少「同時搶鎖」。查單筆（×1）成本低，可用以取代無效鎖定。此權重讓方案朝「少掃、多判斷、精準鎖」收斂。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q8

Q8: 多實例高可用如何協作而不互踩？
- A簡: 以資料庫鎖保唯一，抖動+錯開輪詢，關機時完成收尾。
- A詳: 所有實例都可輪詢與搶鎖，但只有一個會成功。為避免同時掃描/搶鎖造成成本與碰撞，加入抖動與不同 sleep 設定錯開時間；關機以 CancellationToken 統一中止抓取與等待，並在佇列完成後結束，防止鎖後未處理。HATEST 以隨機啟停驗證整體韌性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q7, B-Q5, B-Q9

Q9: 優雅關機（graceful shutdown）流程是什麼？
- A簡: 接收停止訊號→停止輪詢→排空佇列→處理已鎖任務→安全退出。
- A詳: 以 Generic Host 捕捉關閉事件，用 CancellationToken 傳遞停止信號。步驟：1) 停止新一輪 GetReadyJobs；2) 等待或提早完成已鎖任務（避免遺漏）；3) 標記佇列 CompleteAdding，讓消費者讀完即停；4) Join 工作執行緒；5) 釋放資源與紀錄。避免 TaskCanceledException 泄漏，必要時縮短「提前鎖」窗口以控最長關機時間。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q5, C-Q7

Q10: 測試程式如何產生負載與統計？
- A簡: 先清庫後連續 10 分鐘插入多種節奏任務，收尾統計延遲與成本。
- A詳: 測試含多軌道：每 3 秒 1 筆、每 13 秒 20 筆突發、每 1~3 秒 1 筆，以及實時每隔 1~3 秒預約 10 秒後的任務；執行 10 分鐘後再等 30 秒收斂，計算所有延遲平均與標準差、狀態正確性、以及查詢/鎖定次數等成本指標，得出 COST_SCORE 與 EFFICIENT_SCORE。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, A-Q10

Q11: 評分如何計算？意義是什麼？
- A簡: 成本=清單×100+鎖定×10+單筆×1；精確=延遲均值+標準差。
- A詳: COST_SCORE 反映 DB 壓力，清單>鎖定>查單筆；EFFICIENT_SCORE 反映準時與穩定的綜合。兩者對立需折衷：高精準常意謂更頻繁輪詢與鎖定；低成本可能帶來更大延遲與波動。用分數化量測，幫助比較不同策略（如提前鎖、抖動、退避、平行度）的效果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q9, A-Q10

Q12: 為何引入隨機化輪詢/等待有幫助？
- A簡: 錯開多實例同時行為，降低鎖碰撞與清單同時掃描。
- A詳: 多實例若同步啟動且固定節奏，容易同時掃描、同時搶鎖，造成成本與延遲波動。對輪詢間隔與提前鎖時間注入抖動（jitter），讓時間線分散，提升 GetJob 判斷有效性並降低 Acquire 失敗。需注意抖動幅度不能超過 MinPrepareTime 窗，避免遺漏。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q8

Q13: 如何消化瞬時多筆同時到期的任務？
- A簡: 提前分派佇列、適度平行處理、控制每執行緒等待點。
- A詳: 預抓排序後把任務放入生消佇列，由多個 worker 執行緒各自阻塞等待到 RunAt。搭配 ProcessLockedJob 的並行上限，調整 worker 數量以達吞吐與延遲平衡。避免在單一通道串行處理導致排隊延遲擴散。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q2, C-Q9

Q14: Producer-Consumer 架構在此的角色？
- A簡: 生產者抓任務分派，消費者等待到點執行，彼此解耦。
- A詳: 生產者負責 Query/鎖定/分派；消費者專注等待至 RunAt 並執行。中介以 BlockingCollection 或 Channel 承接，提供背壓、完成通知、同步/非同步 API。這使抓取頻率與執行平行度可各自優化，提升總體 EFFICIENT_SCORE 並穩定成本。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q3

Q15: 忙/閒偵測與退避（backoff）如何設計？
- A簡: 有任務時快速循環，無任務時延長等待，減少空輪詢。
- A詳: 若一次抓到任務，直接再次檢查以縮短延遲；若為空，則等 MinPrepareTime 或動態延長，降低清單查詢成本（COST_SCORE）。過程需尊重 CancellationToken，以便關機即時生效。亦可根據歷史負載自適應調整，以兼顧成本與精準。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, B-Q7

Q16: 索引 IX_Table_Column 對查詢有何影響？
- A簡: 在 RunAt, State 上建非聚簇索引，加速掃描即將到期的未執行任務。
- A詳: 索引建立於 (RunAt, State) 可讓 WHERE state=0 AND runat<now 或 runat<now+duration 的查詢走索引範圍掃描，大幅降低 I/O 與 CPU，對高頻輪詢至關重要。搭配覆蓋欄位可再減少回表，實務上亦可考慮過期/完成任務歸檔減輕熱表壓力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q7

Q17: 與 Message Queue 的整合邊界為何？
- A簡: DB 管「何時執行」，Queue 管「如何分發執行」，職責分離。
- A詳: 長延時預約由 DB 儲存與輪詢控制，時間到後可將工作發佈到 MQ 讓下游工作者擴散處理，或直接由排程器執行。此時 DB 是時程權威來源，MQ 提供彈性擴展與跨服務分發，但不建議用 MQ 承擔長時間延遲責任。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q5, C-Q4

Q18: 為什麼延遲標準差是重要指標？
- A簡: 反映穩定性；即使平均小，抖動大仍影響體驗與 SLA。
- A詳: 平均延遲低不代表穩定，若標準差大，代表有不少任務偏離過多。對使用者或下游依賴者，穩定可預期比偶而提早/延後更重要。故 EFFICIENT_SCORE 同時計入平均與標準差，促使設計兼顧穩定性（如抖動、退避、平行度）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q11

Q19: 單機多執行緒與多實例擴展的差異？
- A簡: 前者提升單機吞吐，後者提供容錯與水平擴展，兩者互補。
- A詳: 單機增加 worker threads 可改善同時到期任務的處理速度；多實例能對抗單點故障並水平擴展輪詢與執行能力。多實例需以抖動與鎖策略避免碰撞；單機多執行緒則需避免 ThreadPool 飢餓。綜合使用可在 HATEST 中表現堅韌。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, C-Q2

Q20: 提前鎖定的關機風險與緩解原理？
- A簡: 鎖後未執行可能遺漏；縮短提前窗、關機排空佇列可緩解。
- A詳: 若在 RunAt 前很早鎖定，關機時可能留下已鎖未處理工作，其他實例無法介入。緩解方式：將提前鎖時間限制在小窗（如 300–1700ms 抖動）、關機時停止新抓取，標記佇列完成並等待已鎖任務處理完，或設計鎖超時/回滾機制（題目未提供，概念上可行）。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q9, D-Q5

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何用 .NET Generic Host 建立長時間排程服務？
- A簡: 建立 HostBuilder 註冊 BackgroundService，於 ExecuteAsync 執行輪詢與分派。
- A詳: 步驟：1) 建立 HostBuilder().ConfigureServices(...)；2) 註冊自訂 BackgroundService；3) 在 ExecuteAsync 接收 CancellationToken；4) 內部迴圈執行 GetReadyJobs 分派與等待；5) 支援優雅關機。範例程式碼：var host=new HostBuilder().ConfigureServices(s=>s.AddHostedService<MyWorker>()).Build(); host.Start(); host.WaitForShutdown(); 注意事項：勿在 ExecuteAsync 阻塞主緒；所有等待以 Task.Delay+token，可跨平台部署 systemd/Windows Service。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q9, A-Q17

Q2: 如何用 BlockingCollection 實作生產者-消費者分派？
- A簡: 生產者抓清單入列，消費者多執行緒取出等待到點並執行。
- A詳: 步驟：1) 建立 BlockingCollection<JobInfo> queue；2) 生產者：foreach(repo.GetReadyJobs(d)) queue.Add(job)；3) 消費者：多個 threads foreach(var job in queue.GetConsumingEnumerable()) { 等待到 RunAt；ProcessLockedJob(job.Id);}；4) 關機時呼叫 CompleteAdding 並 Join 線程。注意：避免長期佔用 ThreadPool，建議專屬 Thread；等待用 Task.Delay/Thread.Sleep 精準控制，配合 token。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, A-Q13

Q3: 如何用 Channel 實作純非同步分派？
- A簡: 建立 Channel，生產者 await writer.WriteAsync，消費者 await reader.ReadAsync 執行。
- A詳: 步驟：1) var ch=Channel.CreateBounded<JobInfo>(new BoundedChannelOptions(n){SingleWriter=true,SingleReader=false}); 2) Producer：await writer.WriteAsync(job, token)；3) Consumers：while(await reader.WaitToReadAsync(token)) { while(reader.TryRead(out var job)){ await 等至 RunAt；ProcessLockedJob(job.Id);} }；4) 關機：writer.Complete()。注意：避免多 Channel 錯誤分配導致串行化；善用 SingleWriter/Reader 優化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q14

Q4: 如何實作「先查再鎖」降低成本？
- A簡: 先 GetJob(job.Id) 判斷未執行再 AcquireJobLock，減少無效鎖定。
- A詳: 步驟：1) 抓清單後，對每個 job 先 repo.GetJob(job.Id)；2) 若 State==0 再嘗試 repo.AcquireJobLock(job.Id)；3) 鎖到才入佇列或等待到點執行。程式片段：var j=repo.GetJob(id); if(j.State==0 && repo.AcquireJobLock(id)){ ... } 注意：多實例下仍可能競爭，配合抖動降低碰撞；避免過度查單筆導致反效果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q3

Q5: 如何實作「提前鎖定+jitter」？
- A簡: 在 RunAt 前小窗鎖定，時間加入隨機偏移分散搶鎖。
- A詳: 步驟：1) 預抓清單排序；2) 計算提前窗（例如 300~1700ms 隨機）：var early=TimeSpan.FromMilliseconds(rnd.Next(300,1700)); 3) 若 RunAt-Now>early，await Task.Delay(RunAt-Now-early, token)；4) 檢查 State 再 AcquireJobLock；5) 若還未到點再等剩餘；6) 入佇列或直接執行。注意：避免超過 MinPrepare 窗；配合優雅關機以限制最長停止時間。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q5, B-Q20

Q6: 如何設計輪詢間隔自適應？
- A簡: 有工作時立即重查，無工作時等待 MinPrepareTime 或退避。
- A詳: 實作：在抓清單後，若取到任務則 continue（不延遲）；若為空，await Task.Delay(JobSettings.MinPrepareTime, token)。亦可引入動態退避（空轉次數越多，延遲略增），或基於上一輪抓取耗時：await Task.Delay(Max(MinPrepareTime-Elapsed,0))。注意：尊重 token，避免忙轉；記錄統計以觀察效果。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, B-Q7

Q7: 如何正確處理優雅關機避免「鎖後未處理」？
- A簡: 停止抓取→完成佇列→等已鎖任務處理完→再退出。
- A詳: 步驟：1) 接到停止信號設定 flag；2) 立即停止新一輪 GetReadyJobs 與新鎖定；3) 對已鎖任務：若已入佇列，等待消費者處理完；4) queue.CompleteAdding()；5) Join 工作執行緒；6) 統一處理 TaskCanceledException，不當成錯誤。若採提前鎖，應確保提前窗小於可接受關機時間。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q20, D-Q5

Q8: 如何優化 COST_SCORE？
- A簡: 減少清單查詢、先查再鎖、抖動分散、空時延長等待。
- A詳: 策略：1) 以 MinPrepare 為週期預抓小窗，避免秒級無效掃描；2) 先 GetJob 判斷再 Acquire，降低 10× 的鎖定成本；3) 鎖定時間加抖動分散；4) 空時退避等待；5) 回收完成任務，避免熱表過大。程式片段：var jobs=repo.GetReadyJobs(JobSettings.MinPrepareTime); if(repo.GetJob(id).State==0 && repo.AcquireJobLock(id)) ...
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q4

Q9: 如何提升 EFFICIENT_SCORE（準時與穩定）？
- A簡: 提前鎖+精準等待、適度平行、減少臨界前額外開銷。
- A詳: 作法：1) 將連線、查詢、鎖定移到 RunAt 前小窗完成；2) 使用阻塞/非同步精準等待至 RunAt；3) 增加 worker threads 消化同時到期任務；4) 避免單通道串行導致排隊；5) 用抖動避開碰撞。以短程式片段：if(early) await Delay(...); if(Acquire...) await Delay(RunAt-Now); ProcessLockedJob(id)。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q13, C-Q5

Q10: 如何整合 HATEST 腳本進行自動驗證？
- A簡: 建 Runner 同步啟動多實例，週期 Stop/Start，測完驗證統計。
- A詳: 實作：1) 建 SubWorkerRunner，透過 Generic Host 程式化控制 Start/Stop；2) 同步啟動 N 個實例；3) 每實例隨機 10~30 秒停止再啟動，持續至測試結束；4) 測後檢查：建立=完成、無 EARLY_EXEC 與超時、無例外或忽略可控取消例外。注意：ConsoleApp 難模擬 Ctrl-C，建議用 Host Stop 介面實作。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, B-Q9, A-Q16

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 延遲超過 MaxDelayTime 怎麼辦？
- A簡: 降低臨界前開銷、提前鎖、增加平行度、調整輪詢節奏。
- A詳: 症狀：ExecuteAt-RunAt 常>MaxDelay。可能原因：臨界點才連線/鎖定、單通道串行消化、輪詢太慢。解法：1) 提前鎖定移除臨界開銷；2) 增加 worker threads，使用 BlockingCollection/Channel；3) 有工作時即刻重查、無工作退避；4) 檢視索引與硬體資源。預防：以 EFFICIENT_SCORE 持續監控均值與標準差。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q9

Q2: DB 負載過高（COST_SCORE 高）如何降低？
- A簡: 減少清單掃描、先查再鎖、退避與抖動分散搶鎖。
- A詳: 症狀：QUERYLIST/ACQUIRE 次數高。原因：秒級輪詢、同步搶鎖。解法：1) 以 MinPrepare 為基礎預抓小窗，空時延長等待；2) 先 GetJob 再 Acquire；3) 鎖定前加抖動；4) 批次處理與排序。預防：持續觀測 COST_SCORE、調整 duration 與退避策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q8

Q3: 出現 EARLY_EXEC（提早執行）怎麼修？
- A簡: 僅允許到 RunAt 才執行，提前僅鎖定與等待，嚴禁偷跑。
- A詳: 症狀：ExecuteAt<RunAt。原因：判斷漏寫、以到手即執行。解法：1) 僅在 RunAt 前小窗 AcquireJobLock，不執行；2) 判斷 if(now<RunAt) 等待剩餘時間；3) 加入測試覆蓋此情境。預防：在 HATEST 與統計中加入 EARLY_EXEC 檢查，違規直接 fail。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q6

Q4: 發生重複執行/雙重觸發的原因與解法？
- A簡: 缺乏原子鎖定與狀態轉換；改用 AcquireJobLock 強一致流程。
- A詳: 症狀：同一 Job 多次 ExecuteAt。原因：無原子鎖定、執行流程未檢查狀態。解法：1) 嚴格 0→1→2 流程，只有鎖成功才能執行；2) 先查單筆再鎖；3) 防重入機制。預防：壓力測試多實例、紀錄 ACQUIRE_SUCCESS/FAILURE 分佈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4

Q5: 關機時 TaskCanceledException 滿天飛怎麼辦？
- A簡: 正常取消流程，統一攔截處理，確保排空佇列再退出。
- A詳: 症狀：Stop 過程拋 TaskCanceledException。原因：等待 Task.Delay/通道取消。解法：1) 以 token 傳遞取消；2) try/catch(TCE/OperationCanceled) 視為正常；3) 呼叫 CompleteAdding，等待消費者結束；4) Join 線程。預防：設計最長關機時間（縮短提前鎖窗），避免鎖後未處理。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q7

Q6: CPU 高居不下，疑似 Busy Waiting？
- A簡: 移除自轉輪詢，改用 Task.Delay/WaitHandle/Channel 等阻塞等待。
- A詳: 症狀：無工作時 CPU 仍高。原因：以 while+Sleep(短) 不斷檢查時間。解法：1) 使用 Task.Delay 精準等待 RunAt；2) 生消者以阻塞列/通道讀取；3) 空時退避長等待；4) 專屬執行緒替代 ThreadPool。預防：以分析器觀察醒來頻率。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q2

Q7: 錯過 10~15 秒內新插入的任務怎處理？
- A簡: 預抓窗與查詢節奏需覆蓋 MinPrepareTime，且有工作時即時重查。
- A詳: 症狀：某些臨近 RunAt 的任務延遲大。原因：預抓窗過大或重查太晚。解法：1) 將抓取節奏對齊 MinPrepareTime；2) 有取到任務時不等待立即重查；3) 排序後分派避免晚到被擠到更後；4) 多實例錯開時序。預防：以統計檢視尾端延遲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q15

Q8: Acquire 失敗過多怎麼辦？
- A簡: 加入抖動分散搶鎖，先查單筆減少無謂鎖定，調整實例/執行緒數。
- A詳: 症狀：ACQUIRE_FAILURE 高。原因：多實例同時搶、臨界點高碰撞。解法：1) 在提前窗加入 300–1700ms 抖動；2) 先 GetJob 再鎖；3) 稍微錯開輪詢時間；4) 適度減少實例或鎖定頻率。預防：監看失敗率，持續調整抖動幅度。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, C-Q5

Q9: 延遲標準差過高如何改善？
- A簡: 提前鎖定穩定臨界耗時，提升並行度，減少串行瓶頸。
- A詳: 症狀：Stdev 高、尾端延遲大。原因：臨界點作業不穩定、單通道串行、ThreadPool 飢餓。解法：1) 將重成本移入提前窗；2) 增加 worker threads；3) 專屬執行緒；4) 調整輪詢退避。預防：以 EFFICIENT_SCORE 做持續回歸測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q13

Q10: 佇列堵塞或記憶體暴增如何診斷？
- A簡: 檢查生消速率不匹配、消費阻塞、Channel/BlockingCollection 設定。
- A詳: 症狀：佇列長度升高、GC 頻繁。原因：消費者處理慢、僅單一讀者、等待點放錯位置。解法：1) 增加消費者數；2) 改為每消費者各自等到 RunAt；3) 調整 Channel 容量與 SingleReader/Writer；4) 監控 ProcessLockedJob 耗時。預防：壓測瞬時多筆，觀察佇列長度曲線。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q2, C-Q3

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是資料庫輪詢式排程服務？
    - A-Q2: 為何 Web App 的 Request/Response 模型不擅長預約排程？
    - A-Q3: 排程任務表 Jobs 的欄位與意義是什麼？
    - A-Q4: 什麼是 MinPrepareTime 與 MaxDelayTime？
    - A-Q5: 為何不直接用 Message Queue 延遲消費實現預約？
    - A-Q9: 什麼是 COST_SCORE（成本評分）？
    - A-Q10: 什麼是 EFFICIENT_SCORE（精確度評分）？
    - A-Q11: 為何本題不採用資料庫主動通知？
    - A-Q12: 什麼是 Busy Waiting？缺點是什麼？
    - A-Q17: .NET Generic Host/BackgroundService 的價值？
    - A-Q18: 合格的通過條件有哪些？
    - B-Q2: GetReadyJobs(duration) 的使用流程？
    - B-Q3: AcquireJobLock 與 ProcessLockedJob 的機制？
    - C-Q1: 如何用 .NET Generic Host 建立長時間排程服務？
    - C-Q2: 如何用 BlockingCollection 實作生產者-消費者分派？

- 中級者：建議學習哪 20 題
    - A-Q6: 輪詢頻率、精確度與成本的關係？
    - A-Q7: 本題對高可用/分散式的要求是什麼？
    - A-Q8: 為何「同一 Job 不能執行兩次」很重要？
    - A-Q13: BlockingCollection 與 Channel 的差異是什麼？
    - A-Q14: ThreadPool 與自管 Thread 的差異？
    - A-Q15: 提前鎖定（EARLY_LOCK）與準時鎖定有何差異？
    - A-Q16: 什麼是 HATEST？驗證哪些能力？
    - B-Q1: 輪詢式排程整體如何運作？
    - B-Q6: 如何將延遲精準控制到秒級？
    - B-Q7: 如何降低 COST_SCORE？權重設計的意義？
    - B-Q8: 多實例高可用如何協作而不互踩？
    - B-Q9: 優雅關機（graceful shutdown）流程是什麼？
    - B-Q14: Producer-Consumer 架構在此的角色？
    - B-Q15: 忙/閒偵測與退避（backoff）如何設計？
    - B-Q16: 索引 IX_Table_Column 對查詢有何影響？
    - C-Q3: 如何用 Channel 實作純非同步分派？
    - C-Q4: 如何實作「先查再鎖」降低成本？
    - C-Q6: 如何設計輪詢間隔自適應？
    - D-Q1: 延遲超過 MaxDelayTime 怎麼辦？
    - D-Q2: DB 負載過高（COST_SCORE 高）如何降低？

- 高級者：建議關注哪 15 題
    - B-Q5: 提前鎖定與「抖動」(jitter)的原理？
    - B-Q12: 為何引入隨機化輪詢/等待有幫助？
    - B-Q13: 如何消化瞬時多筆同時到期的任務？
    - B-Q18: 為什麼延遲標準差是重要指標？
    - B-Q19: 單機多執行緒與多實例擴展的差異？
    - B-Q20: 提前鎖定的關機風險與緩解原理？
    - C-Q5: 如何實作「提前鎖定+jitter」？
    - C-Q7: 如何正確處理優雅關機避免「鎖後未處理」？
    - C-Q8: 如何優化 COST_SCORE？
    - C-Q9: 如何提升 EFFICIENT_SCORE（準時與穩定）？
    - C-Q10: 如何整合 HATEST 腳本進行自動驗證？
    - D-Q3: 出現 EARLY_EXEC（提早執行）怎麼修？
    - D-Q4: 發生重複執行/雙重觸發的原因與解法？
    - D-Q8: Acquire 失敗過多怎麼辦？
    - D-Q9: 延遲標準差過高如何改善？