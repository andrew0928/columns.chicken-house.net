---
layout: synthesis
title: "[RUN! PC] 2008 九月號"
synthesis_type: faq
source_post: /2008/09/03/run-pc-2008-september-issue/
redirect_from:
  - /2008/09/03/run-pc-2008-september-issue/faq/
---

# [RUN! PC] 2008 九月號（多執行緒與 ThreadPool 應用總結）

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是執行緒（Thread）？
- A簡: 作業系統排程的最小執行單位，承載程式指令流，與同程序其他執行緒共享記憶體。
- A詳: 執行緒是程序內的可被作業系統排程與執行的最小單位。同一程序的多個執行緒共享位址空間與資源，可同時處理不同任務以提高吞吐。多執行緒可縮短等待、提升互動性，但也帶來同步、死鎖與排程等複雜度，需適當的協調機制與正確使用模式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, B-Q1

A-Q2: 什麼是多執行緒？為什麼需要？
- A簡: 在同一程序同時運行多個執行緒，隱藏等待、提升吞吐與反應性，特別利於I/O密集工作。
- A詳: 多執行緒允許應用將工作分拆並平行進行。對I/O密集任務，可同時等待多個外部事件而不阻塞主執行緒；對CPU密集工作，可適度並行利用多核心。不當使用會導致競爭、切換成本與除錯困難，需透過同步原語、工作排程與限流策略來平衡效益與風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, A-Q5

A-Q3: 什麼是同步機制（Synchronization）？
- A簡: 管控多執行緒間存取時序與共享資源一致性，防止競爭條件與資料損壞。
- A詳: 同步機制涵蓋鎖（lock/Monitor）、事件（Auto/ManualResetEvent）、信號量與柵欄等。它們協助建立臨界區、等待/通知與限制併發數，確保多執行緒操作的一致性與可預期性。選擇原語需依工作型態與性能目標取捨，避免過度鎖定造成瓶頸與死鎖。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q6, B-Q7

A-Q4: 什麼是「旗標」（事件）？
- A簡: 以訊號控制執行緒進度的同步原語，常見為AutoResetEvent與ManualResetEvent。
- A詳: 事件型同步透過設定/重設訊號來喚醒或阻塞執行緒。AutoResetEvent 針對單一等待者釋放後自動復位；ManualResetEvent 可喚醒多個等待者並保持訊號直到手動重設。事件適合「等條件就緒」或「所有工作完成」等流程式控制，比鎖更偏向時序協調。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q8, B-Q6

A-Q5: 什麼是 .NET ThreadPool？
- A簡: 由執行階段管理的工作執行緒池，重複利用線程處理短工作，降低建立與切換成本。
- A詳: ThreadPool 維護一組背景工作執行緒與IOCP執行緒，提供佇列API（如QueueUserWorkItem）以派發工作。它具動態伸縮、工作竊取與最小/最大執行緒控制，適合大量、短暫且可並行的任務。優點是成本低與吞吐佳；限制是無法設定STA、長任務不宜、無專屬生命週期管理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q2

A-Q6: Thread 與 ThreadPool 的差異？
- A簡: Thread可細緻控制但建立昂貴；ThreadPool重用線程、排程效率高，較少控制權。
- A詳: 新建Thread可設定名稱、優先序、前景/背景與Apartment，但每次建立、銷毀與上下文切換代價高。ThreadPool重用既有線程、動態調整數量並進行工作排程，適合大量短工作。需長時間占用或需要特定執行緒特性（如STA）的情境應選Thread或TaskScheduler自定義。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q11, B-Q9

A-Q7: AutoResetEvent 是什麼？
- A簡: 一種事件，同步單一等待者，發出訊號後自動重設，適合一次喚醒一個執行緒。
- A詳: AutoResetEvent 初始為未訊號狀態；當Set()發出訊號，恰有一個等待者會被喚醒，然後狀態自動回到未訊號。適合序列化啟動或逐一釋放等待者。優點是控制精細；缺點是若Set時無等待者，訊號可能丟失，需小心設計時序。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q6, C-Q4

A-Q8: ManualResetEvent 是什麼？
- A簡: 可手動保持訊號開啟，喚醒多個等待者，直到呼叫Reset()才關閉。
- A詳: ManualResetEvent 維持訊號狀態；Set()後所有等待者將被釋放且後續Wait也立即通過，直到Reset()。適合「所有就緒後一起開始」或「完成旗標」的情境。比AutoResetEvent更易用於廣播式同步，但忘記Reset會造成流程錯誤或競爭。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q6, C-Q5

A-Q9: AutoResetEvent 與 ManualResetEvent 的差異？
- A簡: Auto喚醒單一並自動復位；Manual可喚醒多個且需手動復位，適用情境不同。
- A詳: AutoResetEvent 適合逐一釋放等待者與生產者-消費者節流；ManualResetEvent 適合同步起跑、完成旗標或多等待者廣播。前者訊號可能丟失需配合狀態檢查，後者需謹慎Reset避免永遠為訊號或未訊號導致邏輯錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, A-Q8, B-Q6

A-Q10: 為什麼使用 ThreadPool 能影響效能？
- A簡: 重用線程、減少建立與切換成本，配合動態伸縮與工作竊取提升吞吐。
- A詳: 建立Thread昂貴且過多會造成切換膨脹。ThreadPool透過重用背景線程與全域/本地佇列排程，並以演算法動態增加線程，降低平均等待時間。對短小、可並行任務能顯著提升每秒完成數；對長任務或阻塞用法反而可能壅塞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q3, C-Q6

A-Q11: 何時不適合使用 ThreadPool？
- A簡: 長時間阻塞、需要STA或專屬線程、需嚴格生命週期控制時，不宜使用。
- A詳: ThreadPool線程為背景且共用，不適合長時間阻塞I/O、等待UI COM STA、或需要固定優先序/親和性的工作。需持續運行的服務、需專屬清理與停止控制者宜用自建Thread或長存活Task+自訂排程器。大量同步阻塞亦會導致池飢餓。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q15, B-Q12

A-Q12: 什麼是工作（Work Item）與排程？
- A簡: 可獨立執行的小單元作業，由ThreadPool佇列與排程到工作線程執行。
- A詳: Work Item是可被排隊與執行的委派或Task。排程包含入列、選擇適當線程、執行與回收。良好的切分應短小、無共享或最小共享並支援取消。佇列策略（全域、本地、竊取）影響等待時間與公平性，是ThreadPool效能關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q2, C-Q1

A-Q13: Task（TPL）與 ThreadPool 的關係是什麼？
- A簡: Task是更高階抽象，預設以ThreadPool執行，並提供連續、取消與例外傳遞。
- A詳: TPL將工作表示為Task，預設由ThreadPool與TaskScheduler排程，可建立連續（ContinueWith）、合併、取消（CancellationToken）與例外處理。Task.Run簡化派發，亦可自訂排程器以控制執行環境。對應用層更安全與易用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q8, C-Q2

A-Q14: 什麼是工作執行緒與 I/O 執行緒？
- A簡: 工作執行緒處理CPU工作；I/O執行緒對應IOCP回調，處理非同步I/O完成事件。
- A詳: ThreadPool包含工作線程與I/O完成執行緒。前者從佇列取出工作委派執行；後者由IOCP在I/O完成時喚起處理回調。I/O非同步可避免阻塞工作線程，提升整體效率。區分兩者有助於選擇async/await而非阻塞等待。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q1, C-Q9

A-Q15: CPU-bound 與 I/O-bound 任務的差異與策略？
- A簡: CPU-bound應控制並行度等於核心數；I/O-bound應以非阻塞async，提高重疊等待。
- A詳: CPU-bound以計算為主，瓶頸為核心數，建議限制並行度至環境處理器數；I/O-bound以等待外部為主，應採用非同步I/O與async/await，減少線程阻塞。混合型工作需分離I/O與計算階段，各自用合適策略與ThreadPool資源。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q11, C-Q2

### Q&A 類別 B: 技術原理類

B-Q1: .NET ThreadPool 如何運作？
- A簡: 維護工作與I/O兩類線程，使用佇列與動態伸縮策略，將入列工作分派執行。
- A詳: 原理說明：ThreadPool持有全域與本地佇列，動態產生/回收線程處理工作，並分離IOCP線程處理I/O完成。流程：入列→選取佇列→工作竊取/彈性注入→執行→回收。核心組件：Worker Threads、IOCP Threads、Global/Local Queues、Hill-Climbing調整器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q2, B-Q4

B-Q2: ThreadPool 的工作排程流程是什麼？
- A簡: 入列工作、線程可用性檢查、必要時注入線程、執行並回收，並行度動態調整。
- A詳: 原理：佇列採本地優先、全域後援，減少爭用。步驟：Queue→檢查可用→無則依演算法注入→取出工作→執行→回推可用。核心組件：ThreadPoolWorkQueue、WorkStealingQueue、ThreadPoolMgr、ThreadRequest調整器，確保公平與吞吐平衡。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, B-Q10

B-Q3: ThreadPool 動態伸縮（Hill-Climbing）怎麼運作？
- A簡: 透過測量吞吐與延遲，週期性調整線程數，尋找近似最優並行度。
- A詳: 原理：以梯度上升方式嘗試增減線程，觀察吞吐/延遲變化決定方向。步驟：取樣→估計改變收益→調整→穩定化→重測。核心：採取抖動避免局部最小值、限制最大注入速率與退避，防止震盪與飢餓。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q2, B-Q12, A-Q10

B-Q4: ThreadPool 的工作竊取（Work-Stealing）是什麼？
- A簡: 每線程擁有本地佇列，空閒時可自他人佇列尾端竊取工作，提升快取局部性與平衡。
- A詳: 原理：採雙端佇列，工作者偏向處理自身佇列頭，空閒則竊取他人尾端，減少爭用與跨核心遷移。流程：入列到本地→處理→空閒竊取。核心：Local Deque、Global Queue協同，維持負載平衡與低延遲。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q2, B-Q8, A-Q13

B-Q5: I/O 完成埠（IOCP）與 I/O 執行緒如何運作？
- A簡: OS以IOCP匯集I/O完成事件，由執行緒取出回調處理，避免阻塞等待。
- A詳: 原理：非同步I/O提交後，OS在完成時將結果投遞到IOCP佇列。流程：提交→硬體/驅動→完成→IOCP佇列→I/O執行緒回調。核心：IOCP Handle、Completion Packet、回調委派。優點：以少量線程處理大量I/O，極大提升伸縮性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q9

B-Q6: AutoResetEvent/ManualResetEvent 背後機制是什麼？
- A簡: 以內核等待物件維持訊號狀態與等待佇列，喚醒等待者並根據型別復位。
- A詳: 原理：事件為內核同步物件，維護有序等待佇列與訊號旗標。流程：Wait將線程入列阻塞；Set將訊號置位並喚醒；Auto自動復位，Manual需Reset。核心：WaitHandle、內核調度、訊號語意，確保喚醒與可見性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q8

B-Q7: Monitor（lock）如何實作鎖定與喚醒？
- A簡: 以互斥擁有權與等待佇列，自旋後進入內核等待，Pulse/PulseAll喚醒。
- A詳: 原理：進入鎖以CAS自旋嘗試取得，失敗時轉入內核等待；離開解鎖並喚醒等待者。流程：Enter→擁有→Wait釋放鎖並等待→Pulse喚醒→Exit。核心：物件同步塊（OSB）、自旋-睡眠策略、條件變數語意，兼顧低延遲與公平性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q3, C-Q8

B-Q8: Task 與 TaskScheduler 在 ThreadPool 上如何運作？
- A簡: Task由Scheduler入列至ThreadPool，支援連續、親和性與自訂排程策略。
- A詳: 原理：Task表示工作圖；預設Scheduler映射到ThreadPool佇列。流程：Task.Run→排程→工作竊取→執行→延續。核心：Task、TaskScheduler、SynchronizationContext互動；可自訂Scheduler控制執行緒親和或限流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q1, C-Q2

B-Q9: MinThreads/MaxThreads 如何影響 ThreadPool？
- A簡: 設定最小與最大工作/IO線程，影響注入門檻、等待時間與避免過度並行。
- A詳: 原理：最小值決定可立即使用的線程數；最大值限制同時並行上限。流程：SetMin→減少冷啟延遲；Max防止過多線程導致切換膨脹。核心：ThreadPool.SetMinThreads/SetMaxThreads、注入節流、I/O與Worker分別配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q3

B-Q10: SynchronizationContext 在UI執行緒中扮演什麼角色？
- A簡: 抽象捕捉與轉送回UI執行緒的回呼/續延，確保執行緒親和操作安全。
- A詳: 原理：UI框架註冊特定SynchronizationContext，將Post/Send排入UI訊息迴圈。流程：背景執行→捕捉Context→續延回UI→安全更新。核心：WinForms/WPF Context、Dispatcher、訊息泵，避免跨執行緒操作UI引發例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q10, D-Q8

B-Q11: async/await 與 ThreadPool 如何交互？
- A簡: await釋放線程，續延由同步內容或ThreadPool排程，I/O型任務避免阻塞線程。
- A詳: 原理：await將狀態機拆分，未完成時返回；完成後由捕捉的Context或ThreadPool排續延。流程：I/O開始→await返回→完成→續延執行。核心：Task、SynchronizationContext、TaskScheduler；可ConfigureAwait控制續延回哪個Context。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q9

B-Q12: ThreadPool 飢餓（Starvation）偵測與緩解機制？
- A簡: 監測排隊延遲與完成率，必要時快速注入線程並退避阻塞來源。
- A詳: 原理：持續量測等待時間/吞吐；若延遲飆高則加速注入並觸發Hill-Climbing調整。流程：偵測→注入→觀察→穩定。核心：注入速率限制、阻塞警示、避免長任務占滿；建議改用async或拆分短工作。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q1, C-Q7

B-Q13: 如何正確評估 ThreadPool 效能（Stopwatch/基準）？
- A簡: 以代表性工作負載，暖機後多回合量測吞吐與延遲，避免JIT/GC干擾。
- A詳: 原理：Stopwatch基於高解析度計時器。流程：JIT預熱→多迭代→統計平均/分佈→對照Thread與ThreadPool。核心：Stopwatch、Benchmark設計、隔離GC與I/O、固定核數，確保結果可信且可重現。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6

B-Q14: .NET 記憶體模型與 volatile 對多執行緒的影響？
- A簡: 記憶體重排序可能致可見性問題；volatile/屏障確保讀寫順序與可見性。
- A詳: 原理：處理器與編譯器可重排序，跨執行緒讀寫需同步。volatile提供讀寫屏障，確保最新值可見；鎖內隱含更強屏障。流程：共享狀態→同步保護→讀寫可見。核心：內存屏障、可見性、原子性與有序性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q5

B-Q15: .NET Framework vs .NET Core/5+ 的 ThreadPool 有何差異？
- A簡: Core改進工作竊取、動態注入與效能，對async/I/O有更佳整合與預設配置。
- A詳: 原理：新版ThreadPool採更高效的Work-Stealing與Hill-Climbing，改善長尾延遲與注入策略。流程：更快入列/取出、更佳局部性。核心：更低鎖爭用、IOCP整合、預設MinThreads調校與Starvation緩解，整體吞吐與延遲表現提升。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q3

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 ThreadPool.QueueUserWorkItem 執行工作？
- A簡: 呼叫QueueUserWorkItem傳入委派與狀態，即可將短工作入列由ThreadPool執行。
- A詳: 步驟：1) 準備方法或lambda；2) ThreadPool.QueueUserWorkItem(state=>DoWork(state)); 3) 使用WaitHandle等等待完成。程式碼: ThreadPool.QueueUserWorkItem(_=>Console.WriteLine("Hi")); 注意事項：工作短小、避免阻塞；必要時傳遞CancellationToken與例外處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q2

C-Q2: 如何用 Task.Run 平行執行CPU工作？
- A簡: 將工作封裝為Task.Run並控制並行度，收集結果，適合CPU密集處理。
- A詳: 步驟：1) 分割工作；2) var tasks=items.Select(i=>Task.Run(()=>Work(i))); 3) await Task.WhenAll(tasks); 4) 合併結果。程式碼: Parallel.ForEach亦可。注意：限制並行度=Environment.ProcessorCount，避免超賣；避免在Task內阻塞I/O。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q8

C-Q3: 如何設定 ThreadPool 的最小/最大線程？
- A簡: 呼叫ThreadPool.SetMinThreads與SetMaxThreads調整Worker/IO上限與下限。
- A詳: 步驟：ThreadPool.GetMinThreads(out w,out io); ThreadPool.SetMinThreads(環境核心數, io); 視情況調整最大值。程式碼: ThreadPool.SetMinThreads(8,8); 注意：先量測再調整；過大會增加切換與GC壓力，過小會延遲注入導致等待。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q9

C-Q4: 如何用 AutoResetEvent 序列化多執行緒開始？
- A簡: 所有工作先WaitOne，主控在適當時機逐次Set釋放，實現逐一啟動。
- A詳: 步驟：var ev=new AutoResetEvent(false); 啟動N工作: Task.Run(()=>{ev.WaitOne(); Do();}); 主控: 重複ev.Set(); 程式碼: new AutoResetEvent(false); 注意：避免Set時無人等待造成訊號丟失；必要時先檢查狀態或設計握手協議。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q6

C-Q5: 如何用 ManualResetEvent 作為「全部就緒」旗標？
- A簡: 所有工作先WaitOne，主控待條件達成後Set一次，全部工作同時通過。
- A詳: 步驟：var ev=new ManualResetEvent(false); 工作: ev.WaitOne(); Do(); 當準備完成：ev.Set(); 結束重用需ev.Reset(); 程式碼: new ManualResetEvent(false); 注意：別忘Reset；避免Set過早導致未準備者誤通過，可配合CountdownEvent。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q6

C-Q6: 如何量測 Thread vs ThreadPool 的效能差異？
- A簡: 建立代表性短任務，用Stopwatch多回合比較吞吐/延遲與CPU使用率。
- A詳: 步驟：1) 暖機；2) N次短任務；3) Thread新建與ThreadPool入列各自量測；4) 統計均值與P95。程式碼: var sw=Stopwatch.StartNew(); 注意：隔離I/O、固定核心、關閉除錯器影響；以WhenAll完成等待，避免同步阻塞干擾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q13

C-Q7: 如何避免 ThreadPool Starvation（飢餓）？
- A簡: 避免長時間阻塞，改用async I/O與小工作；必要時提高MinThreads並限流。
- A詳: 步驟：1) 找出阻塞點→改用await；2) 將長任務拆小並可取消；3) ThreadPool.SetMinThreads適度提高；4) 控制併發（SemaphoreSlim）。程式碼: using var sem=new SemaphoreSlim(k); await sem.WaitAsync(); 注意：監控排隊時間與超時警示，避免同步Wait。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q12, D-Q2

C-Q8: 如何用 ThreadPool 實作 Producer-Consumer？
- A簡: 以ConcurrentQueue與信號（AutoResetEvent）協調，消費者由ThreadPool處理。
- A詳: 步驟：Queue入列→ev.Set(); 消費者：ThreadPool.QueueUserWorkItem(_=>{while(queue.TryDequeue(out x)){Handle(x);} ev.WaitOne();}); 程式碼: var q=new ConcurrentQueue<T>(); 注意：避免忙迴圈；用CancellationToken結束；大量消費者以SemaphoreSlim限流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, A-Q3

C-Q9: I/O 任務如何搭配 async/await 與 ThreadPool？
- A簡: 使用非同步API避免阻塞，await I/O完成，續延由ThreadPool或UI Context排程。
- A詳: 步驟：await HttpClient.GetAsync(); 解析後若需CPU工作用Task.Run封裝。程式碼: var s=await stream.ReadAsync(buf); 注意：勿在I/O中使用Result/Wait造成死鎖或飢餓；ConfigureAwait在非UI後端可用false減少切換。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q11

C-Q10: 從 ThreadPool 安全地更新 UI？
- A簡: 透過SynchronizationContext/Dispatcher將更新動作Post回UI執行緒後再操作。
- A詳: 步驟：var ctx=SynchronizationContext.Current（UI執行緒取得）；在工作中ctx.Post(_=>UpdateUI(),null); 或WPF用Dispatcher.InvokeAsync(UpdateUI)。程式碼: ctx.Post(_=>label.Text="OK",null); 注意：避免直接跨執行緒觸控UI；在背景工作捕捉例外並回報主執行緒。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q8

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到 ThreadPool 工作延遲很高怎麼辦？
- A簡: 檢查是否阻塞與併發過高，改async拆小工作，必要時提高MinThreads與限流。
- A詳: 症狀：入列後等待時間長、P95延遲飆升。原因：長任務占滿、同步I/O阻塞、MinThreads過低。解法：改用await I/O、拆分小工作、SetMinThreads、以SemaphoreSlim限流。預防：監測佇列延遲、避免同步Wait/Result。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q7

D-Q2: ThreadPool 已耗盡導致排程停滯怎麼處理？
- A簡: 找出占用線程的長阻塞，移除阻塞或改非同步，並降低並發量避免窒塞。
- A詳: 症狀：CPU低但工作不執行、ThreadPool可用為0。原因：同步I/O、外部鎖等待、死迴圈。解法：診斷dump/追蹤，改async I/O，限制併發或改用自建Thread處理長任務。預防：設計不可阻塞的工作與超時控制。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, C-Q3

D-Q3: AutoResetEvent 等待一直超時怎麼辦？
- A簡: 檢查Set時機與等待者是否存在，避免訊號丟失，必要時改用Manual或加狀態檢查。
- A詳: 症狀：WaitOne回傳超時。原因：Set在Wait前觸發導致丟失、未達成條件、事件未共享。解法：確保先註冊等待再Set、改用ManualResetEvent或加共享旗標判斷、排除競態。預防：建立握手機制與重試策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, B-Q6

D-Q4: ManualResetEvent 忘了 Reset 造成邏輯錯誤怎麼辦？
- A簡: 在Set後適時Reset或以CountdownEvent取代避免遺漏，加入測試覆蓋。
- A詳: 症狀：未準備工作卻通過Wait；多輪次測試偶發錯誤。原因：訊號保持打開。解法：完成一批後立即Reset；多等待者場景改用CountdownEvent/SemaphoreSlim。預防：以using封裝生命週期，寫出明確狀態轉移。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5

D-Q5: 如何診斷與修復死鎖？
- A簡: 擷取dump檢查等待圖，統一鎖順序、縮小臨界區，避免同步等待async。
- A詳: 症狀：CPU低、執行緒相互等待不前。原因：鎖順序循環、在UI/同步內容上Wait/Result、遞迴鎖不當。解法：規範鎖順序、以await替代同步等待、用超時與TryEnter。預防：減少共享狀態、以不可變資料與管道式設計。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q14

D-Q6: 多執行緒反而讓效能變慢的原因？
- A簡: 過度並行造成切換/快取失效率、鎖爭用，或任務太短導致排程成本主導。
- A詳: 症狀：吞吐下降、延遲升高。原因：並行度超過核心數、共享資源爭用、工作切得過細。解法：限制並行度、合併過短工作、降低共享與鎖定。預防：先量測，依CPU/I-O特性選策略，使用批次與無鎖結構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q6

D-Q7: CancellationToken 取消無效怎麼處理？
- A簡: 確認工作定期檢查token，I/O用支援取消的API，並避免吞掉OperationCanceled。
- A詳: 症狀：呼叫取消後工作仍持續。原因：未檢查IsCancellationRequested、使用不支援取消的阻塞API。解法：在迴圈與長操作插入檢查與ThrowIfCancellationRequested；I/O選擇可取消方法。預防：設計可中斷點與超時。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11

D-Q8: ThreadPool 背景執行緒的例外被「吞掉」怎麼辦？
- A簡: 在工作內捕捉記錄並回報，Task使用await/WaitAll收集，UI更新走同步內容。
- A詳: 症狀：程式無故中斷或靜默失敗。原因：背景工作未被await，例外未傳遞至呼叫端。解法：Task回傳並await、註冊TaskScheduler.UnobservedTaskException記錄、在UI Context統一處理。預防：約定所有背景工作皆返回Task。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q10

D-Q9: 事件/委派導致的記憶體洩漏如何解？
- A簡: 取消訂閱或用弱事件模式，避免長壽命物件持有短生命訂閱者。
- A詳: 症狀：物件無法回收、記憶體持續增加。原因：事件來源持有委派，訂閱者被意外延長存活。解法：適時-=取消、IDisposable模式自動解除；使用WeakEvent。預防：審視事件生命週期與擁有權。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14

D-Q10: 調整 Min/MaxThreads 後效能變差的原因？
- A簡: 上限過大造成切換與GC壓力；下限過高造成多餘線程；設置與負載不匹配。
- A詳: 症狀：CPU高、吞吐不升或延遲上升。原因：線程過多導致快取失效率與搶佔；過低則注入緩慢。解法：回到預設、逐步調校並量測；配合限流與分離I/O/CPU路徑。預防：只在證據支持下調整，保留基準數據。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q3

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是執行緒（Thread）？
    - A-Q2: 什麼是多執行緒？為什麼需要？
    - A-Q3: 什麼是同步機制（Synchronization）？
    - A-Q4: 什麼是「旗標」（事件）？
    - A-Q5: 什麼是 .NET ThreadPool？
    - A-Q6: Thread 與 ThreadPool 的差異？
    - A-Q7: AutoResetEvent 是什麼？
    - A-Q8: ManualResetEvent 是什麼？
    - A-Q9: AutoResetEvent 與 ManualResetEvent 的差異？
    - A-Q10: 為什麼使用 ThreadPool 能影響效能？
    - A-Q11: 何時不適合使用 ThreadPool？
    - A-Q12: 什麼是工作（Work Item）與排程？
    - C-Q1: 如何用 ThreadPool.QueueUserWorkItem 執行工作？
    - C-Q5: 如何用 ManualResetEvent 作為「全部就緒」旗標？
    - C-Q6: 如何量測 Thread vs ThreadPool 的效能差異？

- 中級者：建議學習哪 20 題
    - A-Q13: Task（TPL）與 ThreadPool 的關係是什麼？
    - A-Q14: 什麼是工作執行緒與 I/O 執行緒？
    - A-Q15: CPU-bound 與 I/O-bound 任務的差異與策略？
    - B-Q1: .NET ThreadPool 如何運作？
    - B-Q2: ThreadPool 的工作排程流程是什麼？
    - B-Q5: I/O 完成埠（IOCP）與 I/O 執行緒如何運作？
    - B-Q6: AutoResetEvent/ManualResetEvent 背後機制是什麼？
    - B-Q8: Task 與 TaskScheduler 在 ThreadPool 上如何運作？
    - B-Q9: MinThreads/MaxThreads 如何影響 ThreadPool？
    - B-Q10: SynchronizationContext 在UI執行緒中扮演什麼角色？
    - B-Q11: async/await 與 ThreadPool 如何交互？
    - B-Q13: 如何正確評估 ThreadPool 效能（Stopwatch/基準）？
    - C-Q2: 如何用 Task.Run 平行執行CPU工作？
    - C-Q3: 如何設定 ThreadPool 的最小/最大線程？
    - C-Q4: 如何用 AutoResetEvent 序列化多執行緒開始？
    - C-Q7: 如何避免 ThreadPool Starvation（飢餓）？
    - C-Q8: 如何用 ThreadPool 實作 Producer-Consumer？
    - C-Q9: I/O 任務如何搭配 async/await 與 ThreadPool？
    - C-Q10: 從 ThreadPool 安全地更新 UI？
    - D-Q1: 遇到 ThreadPool 工作延遲很高怎麼辦？

- 高級者：建議關注哪 15 題
    - B-Q3: ThreadPool 動態伸縮（Hill-Climbing）怎麼運作？
    - B-Q4: ThreadPool 的工作竊取（Work-Stealing）是什麼？
    - B-Q7: Monitor（lock）如何實作鎖定與喚醒？
    - B-Q12: ThreadPool 飢餓（Starvation）偵測與緩解機制？
    - B-Q14: .NET 記憶體模型與 volatile 對多執行緒的影響？
    - B-Q15: .NET Framework vs .NET Core/5+ 的 ThreadPool 有何差異？
    - D-Q2: ThreadPool 已耗盡導致排程停滯怎麼處理？
    - D-Q3: AutoResetEvent 等待一直超時怎麼辦？
    - D-Q4: ManualResetEvent 忘了 Reset 造成邏輯錯誤怎麼辦？
    - D-Q5: 如何診斷與修復死鎖？
    - D-Q6: 多執行緒反而讓效能變慢的原因？
    - D-Q7: CancellationToken 取消無效怎麼處理？
    - D-Q8: ThreadPool 背景執行緒的例外被「吞掉」怎麼辦？
    - D-Q9: 事件/委派導致的記憶體洩漏如何解？
    - D-Q10: 調整 Min/MaxThreads 後效能變差的原因？