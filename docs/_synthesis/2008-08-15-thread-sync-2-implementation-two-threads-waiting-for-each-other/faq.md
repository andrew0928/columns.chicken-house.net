---
layout: synthesis
title: "Thread Sync #2. 實作篇 - 互相等待的兩個執行緒"
synthesis_type: faq
source_post: /2008/08/15/thread-sync-2-implementation-two-threads-waiting-for-each-other/
redirect_from:
  - /2008/08/15/thread-sync-2-implementation-two-threads-waiting-for-each-other/faq/
postid: 2008-08-15-thread-sync-2-implementation-two-threads-waiting-for-each-other
---

# Thread Sync #2. 實作篇 - 互相等待的兩個執行緒

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是「兩個執行緒互相等待」的同步？
- A簡: 兩執行緒以握手協定交替前進，各以事件通知與等待，確保彼此在正確時點交換資料且不競賽。
- A詳: 所謂「互相等待」即雙向握手（rendezvous）同步。兩個執行緒透過同步原語（如 AutoResetEvent）形成請求-回應的節奏：一方準備好資料後 Set 喚醒對方，自己 WaitOne 等待回覆；另一方收到訊號後取資料、處理並反向 Set 回覆。此方式能確保交換動作有嚴格先後次序，避免出現競態或取到不一致的狀態。文中以 GameHost 與 Player 的問答往返為例，透過 _host_return、_host_call、_host_end 三個事件協調起始、往返與結束，形成清晰的雙向同步骨架。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q2, A-Q8

A-Q2: AsyncPlayer 的核心理念是什麼？
- A簡: 化被動為主動：讓 Player 以自有執行緒與迴圈思考，主動向 GameHost 提問，再等回覆。
- A詳: AsyncPlayer 將原先由 GameHost 驅動的「被動回呼」模式，轉換為 Player 背後啟動一條思考執行緒（Think），在合適時機呼叫 GameHost_AskQuestion 主動提問。它以事件與共享暫存變數臨時傳遞資料：_temp_number 與 _temp_hint 串接問與答，_host_return 與 _host_call 負責雙向喚醒，_host_end 統一收尾。此設計把「解題策略」集中在 Think 內，不再被切碎散落於 StartGuess/GuessNext，讓邏輯自然、可分階段迭代思考。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, B-Q5

A-Q3: DummyPlayer 與 AsyncDummyPlayer 有何差異？
- A簡: DummyPlayer 被 GameHost 驅動，被動逐次回應；AsyncDummyPlayer 自主思考，主動提問並以事件握手。
- A詳: DummyPlayer 嚴格遵循 GameHost 的呼叫點：StartGuess/GuessNext/Stop，必須以成員狀態記錄「做到哪」，邏輯被切散；AsyncDummyPlayer 則在 Think 內迴圈思考，決定何時產生猜測與詢問 Host，形成「策略主導、Host 協助」的架構。Async 版本較易表達多階段推理，雖多了同步開銷（事件、上下文切換），效能相對慢，但可讀性與演算法演進彈性更佳。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q4, B-Q14

A-Q4: 為何要將被動呼叫轉為主動思考？
- A簡: 讓策略集中、易表達多階段邏輯，減少狀態分散與複雜的呼叫回憶負擔。
- A詳: 被動模式下每次只解一小步，策略需跨多次呼叫維持上下文，邏輯分裂、可讀性差；主動模式將策略收斂於 Think 迴圈，依自然語意安排階段、變數與控制流程，降低外部呼叫的干預頻率。對需漸進式試探、反覆提問的問題（如猜數字）尤為合適。代價是同步元件與執行緒管理開銷，但換得維護性、可擴充性、除錯性顯著提升。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, B-Q22

A-Q5: GameHost 與 Player 的職責應如何劃分？
- A簡: Host 管理流程與評分；Player 專注策略與提問；以握手協定協作資料交換與節奏。
- A詳: GameHost 負責出題、比對（compare）、維持比賽生命週期；Player 負責從題目空間與提示中推進策略。兩者以既定介面與雙向同步協定互動：Host 提供 StartGuess/GuessNext/Stop；Player 在 Async 方案中以 GameHost_AskQuestion 主動取得提示。清晰職責減少耦合，便於替換策略或擴充為多玩家、多局賽制。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q5, A-Q6

A-Q6: StartGuess、GuessNext、Stop 的語意是什麼？
- A簡: StartGuess 初始化並給第一猜；GuessNext 以上次提示續猜；Stop 結束清理並同步收尾。
- A詳: StartGuess 接收題目範圍（maxNum, digits），準備策略狀態並提交第一個猜測；GuessNext 依據上一個 Hint 精進策略產生下一猜；Stop 表示比賽完結或認輸，Player 應釋放資源、終止思考執行緒並與 Host 完成最後握手。AsyncPlayer 用這三點將主動思考與被動介面橋接，兼容原 Host 邏輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q5, C-Q4

A-Q7: GameHost_AskQuestion 的角色是什麼？
- A簡: 它是 Player 對 Host 的主動提問入口，封裝雙向握手與暫存資料交換。
- A詳: GameHost_AskQuestion 接收 Player 的猜測數列，將其暫存於 _temp_number，Set _host_return 喚醒 Host 路徑，隨後 WaitOne 等待 _host_call，再回傳 _temp_hint。它以 lock 保護暫存欄位、以 finally 清理暫存，確保一次只處理一筆問答，避免資料外洩或交錯。這是把主動策略注入既有 Host 呼叫序的關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q8, A-Q1

A-Q8: AutoResetEvent 是什麼？適用於何時？
- A簡: 一種自動復位事件；釋放單一等待者後自動回復非訊號，適合一對一握手。
- A詳: AutoResetEvent 初始為非訊號；呼叫 Set 時喚醒一個等待者，隨即自動回復非訊號狀態。多等待者時僅一人被喚醒。它適合點對點的「請求-回覆」同步，避免 ManualResetEvent 必須手動 Reset 的誤用風險。文中以三個 AutoResetEvent 區分三種節點：回傳第一猜（_host_return）、回傳提示（_host_call）、宣告結束（_host_end）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, A-Q1, A-Q9

A-Q9: WaitOne/Set 在同步中的作用是？
- A簡: WaitOne 使執行緒阻塞等待事件；Set 將事件設為訊號以喚醒等待者，推進時序。
- A詳: WaitOne 會使當前執行緒直到事件被 Set 才繼續，避免忙等耗 CPU；Set 將事件置為訊號，喚醒一位等待者（AutoResetEvent），保證兩端的步驟在既定點交會。透過在合適位置放置 WaitOne/Set，可構築嚴謹的往返節奏，防止資料讀寫交錯與早/晚到的競態問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q2, B-Q7

A-Q10: 為何需要 lock？
- A簡: 序列化對共享暫存欄位的進出，確保一次僅有一個問答在關鍵區內進行。
- A詳: _temp_number 與 _temp_hint 是兩執行緒共享的資料槽。若無 lock，可能同時寫入/讀取導致錯位或撕裂讀。lock(this) 包住「寫入猜測、發訊號、等待回覆、讀回提示」的原子流程，並在 finally 清理暫存，確保關鍵區的完整性與可預期性。這同時提供記憶體柵欄，強化可見性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q21, D-Q6

A-Q11: WaitHandle 是什麼？有哪些常見種類？
- A簡: 跨執行緒同步基類；常見有 AutoResetEvent、ManualResetEvent、Semaphore 等。
- A詳: WaitHandle 提供 Wait/Signal 抽象，.NET 以各種衍生型別實作不同同步語義。AutoResetEvent 適合一對一喚醒，ManualResetEvent 適合一對多廣播（需手動 Reset），Semaphore 控制同時通行數量。選擇正確型別與初始化狀態，是設計握手與併發流量的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q6, B-Q15

A-Q12: 同步與非同步的差異是什麼？
- A簡: 同步呼叫在同執行緒上序列化；非同步將工作交他執行緒並以事件回合協作。
- A詳: 同步模式下，呼叫端等待被呼叫端完成才繼續，簡單但耦合較強。非同步將工作放入另一執行緒，由等待/訊號協調進度，能讓策略在自己的節奏中前進。文中以 AsyncPlayer 將策略移至 Think 執行緒，與 Host 以雙向事件往返，使邏輯自然、互動明確。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, B-Q22

A-Q13: Think 方法中的「思考迴圈」是什麼？
- A簡: 策略主迴圈，反覆產生猜測、提問、根據提示修正，直到達成條件或結束。
- A詳: 在 AsyncDummyPlayer，Think 使用 while(true) 產生猜測、呼叫 GameHost_AskQuestion 取得 Hint，若 A 等於位數即完成。真實策略可分多階段：初探、縮小範圍、最後驗證。這讓策略與時間序列一致，避免跨呼叫狀態管理的負擔。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, C-Q3

A-Q14: 何謂「兩段式」Init/Think 設計？
- A簡: Init 做一次性初始化；Think 執行主策略迴圈，互不干擾、責任明確。
- A詳: ThinkCaller 先呼叫 Init 準備資料結構（如配置陣列），再進入 Think 的策略流程。此分離使初始化副作用可控，策略碼更專注於推理。若需在多局中重用物件，也易於重置狀態。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q2, C-Q1

A-Q15: 多型（Polymorphism）在此設計中的角色？
- A簡: GameHost 依 Player 抽象介面運作，實作差異由各 Player 子類決定。
- A詳: Host 僅認得 Player 的抽象方法（StartGuess/GuessNext/Stop）。DummyPlayer 與 AsyncPlayer/AsyncDummyPlayer 以不同方式實作契約，Host 無須改動即可替換策略。這是里氏替換與開放封閉的實踐，利於演算法實驗與行為切換。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, A-Q2, B-Q26

A-Q16: 為何 AsyncDummyPlayer 可能比 DummyPlayer 慢？
- A簡: 多了一條思考執行緒與事件等待，增加上下文切換與同步成本。
- A詳: 雙向握手需多次 Set/WaitOne 與鎖定，且跨執行緒有記憶體同步與排程開銷。若策略本身很輕（如隨機猜），這些固定成本會主導耗時，使同步版本反而較快。若策略計算重或需多階段推演，Async 風格的表達優勢與可維護性往往更重要。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, D-Q10, C-Q7

A-Q17: 文章中的時序圖傳達了什麼觀念？
- A簡: 用時間軸標示兩執行緒事件順序，誰先到誰等待，對齊握手點。
- A詳: 時序圖顯示 StartGuess 啟動 Think 執行緒，Player 提問時 Set _host_return，Host 取到後回應 Set _host_call。若任一端先行抵達對應 WaitOne，則會阻塞至另一端跟上。圖像化有助掌握「先/後達」與「誰喚醒誰」的關係，避免編碼時誤置事件時機。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q2, D-Q8

A-Q18: 何謂「任務交付模式與自主管理」的對比？
- A簡: 主動勞工自主管理流程，只在需要時向老闆請求資源；對比被動等待指令。
- A詳: 被動模式像「一步一指令」，需要頻繁外部驅動；主動模式像委託任務後「自我推進」，只在依賴點（提問、結束）互動。這反映在 AsyncPlayer 用 Think 主導節奏，Host 提供必要服務。好處是策略內聚、外部耦合低；代價是同步機制設計需嚴謹。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1, C-Q1

A-Q19: 什麼是雙向通道/握手協定？
- A簡: 雙事件配對傳遞請求與回覆，形成一來一往的嚴格節奏與資料對齊。
- A詳: 在文中，_host_return 表示「有猜測可取」，_host_call 表示「有提示可回」。Player 先 Set _host_return 等待，Host 取後 Set _host_call 回覆。這是最小化的雙向通道；再加 _host_end 負責收尾事件，構成完整協定。正確配對可防止訊號遺失與亂序。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, D-Q8

A-Q20: Host 完成旗標 _host_complete 的用途？
- A簡: 標示遊戲已終止，防止 Player 在已結束後再提問，避免非法狀態。
- A詳: Stop 中在完成最終握手後設為 true。GameHost_AskQuestion 首先檢查該旗標，若已完成則丟 InvalidOperationException，阻止後續互動。這避免在收尾時仍有殘留提問造成未知行為或懸掛等待。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q5, C-Q6

A-Q21: 共用暫存變數為何設計成 _temp_number/_temp_hint？
- A簡: 作為一次性問與答的暫存槽，配合事件與 lock 實現安全的資料交接。
- A詳: 因 Host 與 Player 並非直接呼叫回傳，而是跨執行緒交接，需有中繼容器存放目前一筆猜測與回覆。寫入-喚醒-等待-讀取在同一鎖中執行，finally 立即清空防止資料殘留。這種「一次一物」設計與 AutoResetEvent 的單一喚醒語義相匹配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q8, D-Q3

A-Q22: 何謂競態條件？此設計如何避免？
- A簡: 多執行緒搶奪順序導致非預期；透過事件時序與鎖定保證先後與互斥避免。
- A詳: 競態在於「誰先做」影響結果。此設計用 WaitOne/Set 對齊關鍵先後（誰先到誰等），以 lock 確保同一時刻只交握一筆資料，並用 finally 清理。正確的事件配對避免遺失訊號，旗標阻止結束後動作，形成完整的競態防線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q7, D-Q8

A-Q23: 為何選 AutoResetEvent 而非 ManualResetEvent？
- A簡: AutoReset 自動復位適合一對一握手，減少忘記 Reset 造成廣播誤喚醒風險。
- A詳: ManualResetEvent 適合一對多通知，但須小心 Reset 時機，否則可能喚醒多個等待者或造成持續為訊號狀態。文中只有單一 Player 與單一 Host 的點對點往返，AutoResetEvent 正合需求且 API 更直覺，降低時序錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q15, D-Q8

A-Q24: 什麼是阻塞等待？與忙等差異？
- A簡: 阻塞等待釋放 CPU 直到被喚醒；忙等持續輪詢耗 CPU，效率差且易抖動。
- A詳: WaitOne 屬阻塞等待，系統排程讓出時間片，直到事件被 Set 才繼續。忙等（spin/loop）則不停檢查狀態，對輕量短期等待可用，但長等待將浪費 CPU。文中以事件阻塞，避免 Think 迴圈成為高佔用的無效輪詢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q22, D-Q4, C-Q7

A-Q25: 文章中的比喻（勞工/老闆）啟示了什麼設計思維？
- A簡: 把控制權交給靠近問題的人（策略），外部僅在依賴點協助，提升內聚與效率。
- A詳: 「被動勞工」代表外控碎片化邏輯；「主動勞工」強調內控、階段式推進。將解題核心放回策略單元，能自然表達多步驟思考，降低外部協調成本。這與 CQRS/Actor 思想相通：分離責任、減少交錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q26, C-Q1

A-Q26: 什麼是兩執行緒的 Rendezvous Pattern？
- A簡: 雙方在協議點會合交換資料，各自等對方抵達，確保同步與正確次序。
- A詳: Rendezvous 是一種雙向同步手法，常用兩個事件（或通道）建構請求/回覆的會合點。每次會合只處理一筆交易，會合後各自前進至下一次會合。本文即以 AutoResetEvent 和共享暫存形成最小會合原語，安全地驅動問答回合到完成。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q1, B-Q7, C-Q5

### Q&A 類別 B: 技術原理類

B-Q1: AsyncPlayer 整體如何運作？
- A簡: Host 仍用舊介面；AsyncPlayer 背後啟動 Think 執行緒，以事件與暫存槽橋接雙向問答。
- A詳: StartGuess 啟動 ThinkCaller 執行緒，呼叫 Init 後進入 Think；Think 於策略節點呼叫 GameHost_AskQuestion，把猜測存入 _temp_number，Set _host_return，WaitOne _host_call 等提示。Host 呼叫 GuessNext 將 Hint 放入 _temp_hint，Set _host_call 喚醒 Player；Stop 則送終局 Hint 並等待 _host_end。三事件劃分三階段：初答、往返、終結，lock 與 finally 確保單筆原子交握與清理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q2, B-Q5

B-Q2: StartGuess 與 Think 如何銜接？
- A簡: StartGuess 啟動 ThinkCaller，並 Wait _host_return 取得第一猜；Think 內首次提問即喚醒 Host。
- A詳: StartGuess 建立 Thread(ThinkCaller).Start() 後立即 WaitOne(_host_return)，直到 Think 首次呼叫 GameHost_AskQuestion 將 _temp_number 填入並 Set _host_return。如此 Host 得以從同步介面拿到第一猜，同時策略已在背景迴圈運行，後續回合改走 GuessNext。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q3, A-Q17

B-Q3: GameHost_AskQuestion 的執行流程為何？
- A簡: 寫入猜測→Set _host_return→Wait _host_call→讀出提示→finally 清理。
- A詳: 進入 lock 後，把 number 指派給 _temp_number，Set _host_return 通知 Host 有猜測可取，接著 WaitOne(_host_call) 等待 Host 把 Hint 放回 _temp_hint 並喚醒；取回 Hint 後 return，finally 清掉兩個暫存以防殘留。lock 確保整段交換為原子過程，不會與其他回合交疊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, A-Q10, B-Q4

B-Q4: GuessNext 如何喚醒 Player Thread？
- A簡: 將 lastHint 放入 _temp_hint，Set _host_call 喚醒正在 Wait 的 Player，Wait _host_return 收下一猜。
- A詳: Host 在 GuessNext 收到先前 Hint 後，先寫入 _temp_hint，再 Set _host_call 通知 Player；隨後 WaitOne(_host_return) 直到 Player 算出下一猜、填入 _temp_number 並 Set。這樣完成一次回合的往返同步，資料不會亂序或交錯。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, A-Q9, A-Q19

B-Q5: Stop 如何終止雙方？
- A簡: 寫入終局 Hint、Set 喚醒 Player、Wait _host_end，最後設 _host_complete 防後續提問。
- A詳: Host 呼叫 Stop 時，先 new Hint(digits,0) 放入 _temp_hint，Set _host_call 喚醒 Player 讓 Think 得以察覺結束；ThinkCaller 的 finally 會 Set _host_end 告知 Host 背景已收尾。Host WaitOne(_host_end) 後再將 _host_complete 設為 true，禁止後續提問。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, D-Q5, C-Q6

B-Q6: 為何需要三個 AutoResetEvent？各自用途是？
- A簡: _host_return 傳回猜測，_host_call 傳回提示，_host_end 通知結束，分工清晰避免混線。
- A詳: 單一事件難以表達方向性與狀態。以兩個事件分離請求與回覆，防止訊號誤配；再加一個結束事件避免與往返訊號混淆。這樣每個 Wait/Set 都具有明確語義，降低遺失訊號與跨回合干擾的風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, A-Q23, D-Q8

B-Q7: 如何以事件順序防止競賽與遺失訊號？
- A簡: 固定「寫入→Set→Wait→讀取」序；雙向分離事件；遇先到先等，確保會合對齊。
- A詳: 在每個方向上，寫入資料後立即 Set，對端在 Wait 中被喚醒再讀取；反向回覆亦同。兩個方向各有事件，避免同事件亂序配對。即使任一端先抵達 Wait，都會阻塞至對方 Set。配合 lock 與 finally，能避免早/晚 Set、殘留資料與交錯讀取。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q22, D-Q8, B-Q3

B-Q8: lock 範圍內的核心組件有哪些？
- A簡: _temp_number、_temp_hint 的寫讀、對應 Set/Wait、以及 finally 的清除。
- A詳: 關鍵區涵蓋「寫入猜測→Set→等待回覆→讀取提示→清理」的完整閉環。這確保共享狀態在單回合內不被外部並行動作打斷；也借由 lock 的記憶體柵欄保證可見性與順序性，避免指令重排影響結果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q21, D-Q6

B-Q9: 為什麼在 finally 清除暫存欄位？
- A簡: 確保無論正常或例外都不殘留上回合的資料，避免污染下一回合。
- A詳: finally 具保證執行性；在任何路徑（含例外）都會清空 _temp_number/_temp_hint，防止 Host/Player 在下一次交握看到舊資料。這是多執行緒中常見的狀態衛生做法，降低難以重製的錯位問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, B-Q3, A-Q21

B-Q10: _host_complete 何時與如何影響流程？
- A簡: Stop 收尾後設為 true；AskQuestion 首先檢查並阻止已結束的互動。
- A詳: 當 Host 完成終結握手（收到 _host_end）後，設 _host_complete 為 true。GameHost_AskQuestion 初始即檢查該旗標，避免 Player 在收尾階段發起新請求，導致 Wait 無人回應或順序扭曲。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, D-Q5, C-Q6

B-Q11: 若 Player 先 AskQuestion 但 Host 還未就緒會發生什麼？
- A簡: Host 在 StartGuess 中 Wait，Player Set _host_return 即喚醒，雙方自動對齊。
- A詳: 本設計允許先後不定；誰先到誰等待。Player 在 AskQuestion Set _host_return 後 Wait _host_call；Host 若仍在 Wait _host_return，會被喚醒，取走猜測並回覆。這確保順序不影響正確性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, B-Q2, B-Q7

B-Q12: 若 Host 先 GuessNext 但 Player 未提問呢？
- A簡: Host Wait _host_return，直到 Player 下次提問 Set 後才繼續，仍能對齊。
- A詳: Host 在將 Hint 準備好後 Wait _host_return，Player 下一步提問即 Set 之，喚醒 Host 交換資料。這防止 Host 提前推進導致資料丟失，維持回合完整性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, A-Q17, D-Q8

B-Q13: 如何用時序圖描述此握手？
- A簡: 兩泳道（Host/Player）標序列：寫→Set→Wait→讀；雙向對稱；尾端加結束事件。
- A詳: 橫軸為主體，縱軸時間向下。標示 StartGuess 啟動 Think、AskQuestion Set _host_return、Host 取後 Set _host_call、Player 讀後迭代。Stop 時 Host Set _host_call，Player 收尾 Set _host_end。圖形化驗證沒有未配對的 Wait 或交錯路徑。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q17, B-Q2, B-Q5

B-Q14: 此設計與 Producer-Consumer 佇列有何差異？
- A簡: 這是雙向一對一「回合制」；佇列是單向多對多流水化，語義與需求不同。
- A詳: Producer-Consumer 側重解耦與批量吞吐；此處重在「一次一問一答」的嚴格配對與會合點，避免跨回合交錯。若需多筆排隊或多玩家，才考慮佇列或 Channel；但需額外帶上關聯 ID 確保配對。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q26, C-Q9, D-Q6

B-Q15: AutoResetEvent 與 ManualResetEvent 差異與取捨？
- A簡: 前者喚醒單一等待者後自動復位；後者廣播需手動 Reset；本例選前者。
- A詳: 單客單伺的一問一答更適合 AutoResetEvent，避免 ManualResetEvent 忘記 Reset 造成多重喚醒或長期為訊號狀態帶來亂序。若真要廣播狀態（如全部終止），Manual 類型更合適。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q23, B-Q6, D-Q8

B-Q16: Thread 與 ThreadPool/Task 的差異與影響？
- A簡: Thread 明確建執行緒；Task/ThreadPool 管理資源與排程；本例用 Thread 簡單直觀。
- A詳: Task 提供更高階抽象、取消/延續與例外傳遞；Thread 手控生命週期較繁瑣。本文偏重教學與透明時序，採 Thread 易於對照時序圖；實務可用 Task.Run 搭配 async/await 與同步元件替代。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, D-Q9, A-Q12

B-Q17: ThinkCaller 的 try/catch/finally 有何作用？
- A簡: 捕捉策略例外避免無聲失敗；finally 一定送出 _host_end，保證收尾。
- A詳: 背景執行緒若未捕捉例外將靜默終止且可能遺漏事件，造成 Host 永久等待。try/catch 記錄例外，finally Set _host_end 確保 Host 不會卡死在 Stop 的 Wait。這是握手協定的健全性要件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q9, B-Q5, C-Q6

B-Q18: WaitOne 是否應加 Timeout？為何？
- A簡: 加 Timeout 可避免永久等待，利於偵錯與容錯；需處理逾時路徑。
- A詳: 無限等待在訊號遺失或例外時會僵死。將 WaitOne(true) 改為 WaitOne(timeout) 並檢查回傳值，可在逾時時中止流程、記錄日誌、觸發補償或取消。代價是複雜度上升，需定義逾時策略。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q5, D-Q1, D-Q8

B-Q19: lock(this) 有何影響？有替代選擇嗎？
- A簡: 可能被外部也鎖住造成死鎖風險；可改用私有 object 作為鎖。
- A詳: 鎖定公開可取得的 this 增加與外部鎖相互作用的機率。用 private readonly object _gate = new(); 並 lock(_gate) 可降低耦合與風險。雖本文示範簡化，但實務建議專用鎖物件。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q6, C-Q7, B-Q8

B-Q20: 此設計是否可重入？如何避免？
- A簡: GameHost_AskQuestion 非重入；以 lock 限制一次單回合，呼叫端勿並行呼叫。
- A詳: 若 Think 在未完成一次問答前再次呼叫 AskQuestion，會在 lock 外等候。Host 端也應確保不並行呼叫 GuessNext。必要時可加入狀態機或斷言，防止誤用導致重入錯誤與時序混亂。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q6, B-Q8, C-Q10

B-Q21: 記憶體可見性如何被保障？
- A簡: lock 與 WaitHandle 皆建立記憶體柵欄，確保寫入在喚醒前被看見。
- A詳: 進入/離開 lock 會有 Acquire/Release semantics；Wait/Signal 也有同步邊界。這使得 _temp_number/_temp_hint 的寫入在喚醒對方前可見，避免看到舊值。這是多執行緒正確性的關鍵。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, A-Q22, D-Q6

B-Q22: 忙等 vs 事件阻塞的效率比較？
- A簡: 忙等高 CPU、回應快但浪費；事件阻塞低 CPU、可擴充，適合大多數情境。
- A詳: 忙等適合極短等待且需微秒級響應；事件阻塞適合一般互動，系統調度更友善。本文採事件阻塞避免 Think 造成不必要負載。效能瓶頸可用批次、減少回合數或併合多步提問來優化。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q24, D-Q4, C-Q7

B-Q23: 如何支援單一 Player 多局比賽？
- A簡: 在 StartGuess/Stop 之間重置狀態；Init 負責每局初始化，Think 避免跨局殘留。
- A詳: 將局部狀態（陣列、候選集）在 Init 中重建；在 Stop 確保收尾事件已對齊。若需復用物件，避免使用靜態共享。可加入世代計數防止過時訊號誤配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q2, D-Q7

B-Q24: 如何擴充到多玩家並行？
- A簡: 為每位 Player 各自維護事件與暫存，避免共享；Host 以玩家實例分流。
- A詳: 每個 Player 擁有自身 _host_call/_host_return/_host_end 與暫存槽，Host 各自呼叫對應介面。若 Host 要集中管理，可用集合追蹤狀態，避免共用靜態事件導致交叉喚醒。必要時採用佇列/Channel 與關聯 ID。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q7, B-Q14, C-Q4

B-Q25: 若以事件/委派取代 AskQuestion 呼叫？
- A簡: 可用回呼或 observer 風格，但仍需同步原語確保時序與一次一筆。
- A詳: 將 AskQuestion 轉為事件不會自動解決同步問題，仍需在回呼邊界設計等待/訊號，並避免重入與競態。事件化可改善耦合，但需更多狀態機管理。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q20, C-Q9

B-Q26: AsyncPlayer 如何抽象化「思考」策略？
- A簡: 以抽象方法 Init/Think 讓子類專注策略；底層握手由基底類封裝。
- A詳: AsyncPlayer 抽走通訊與同步細節，子類只需在 Think 中安排策略步驟、何時提問與何時結束。這種分離讓策略演進不牽動基礎通訊，提升可測試性與替換性，體現策略模式精神。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q15, C-Q1

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何將 DummyPlayer 改造成 AsyncDummyPlayer？
- A簡: 新增 AsyncPlayer 基底，將策略搬至 Think，改以 GameHost_AskQuestion 互動。
- A詳: 步驟：1) 讓類別繼承 AsyncPlayer；2) 將原 StartGuess/GuessNext 的策略移入 Think 迴圈；3) 在 Init 建立所需陣列與變數；4) 在 Think 中產生猜測並呼叫 GameHost_AskQuestion；5) 以 Hint 決定何時 break。程式碼片段：protected override void Init(...){_curr=new int[digits];} protected override void Think(){while(true){randomGuess();var h=GameHost_AskQuestion(_curr);if(h.A==_digits)break;}} 注意：勿直接存取 Host 內部；避免在 Think 中同步阻塞以外的長期 I/O。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, C-Q2

C-Q2: 如何實作 Init 與 Think 的骨架？
- A簡: Init 做一次性狀態配置；Think 以 while 迴圈：產生→提問→判斷→迭代或結束。
- A詳: 實作步驟：1) Init：配置陣列、清空候選集、重置亂數；2) Think：for/while 產生猜測，呼叫 GameHost_AskQuestion，檢查 h.A==_digits 則 break；3) 適度抽出子方法維持可讀性。程式：Init(){_ans=new int[digits];} Think(){for(;;){MakeGuess();var h=GameHost_AskQuestion(_ans);if(h.A==_digits)break;RefineWith(h);}} 注意：避免在 Think 內丟出未捕捉例外；必要時 try/catch 局部處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q17, C-Q3

C-Q3: 如何在 Think 中迭代詢問直到答對？
- A簡: 在迴圈內每次產生新猜測，呼叫 GameHost_AskQuestion，收到滿足條件的提示即結束。
- A詳: 步驟：1) 設計停止條件（如 h.A==_digits）；2) 每回合更新策略狀態；3) 避免忙等。程式：while(true){var guess=NextGuess();var h=GameHost_AskQuestion(guess);if(h.A==_digits)break;UpdateState(h);} 注意：保持每回合原子性，勿在回合之間共享未受保護狀態；必要時鎖住內部資料結構。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q3, B-Q22

C-Q4: 如何在不改 GameHost 的情況接入 AsyncPlayer？
- A簡: 維持 Player 介面不變，由 AsyncPlayer 在內部橋接同步呼叫與主動策略。
- A詳: 步驟：1) 保持 GameHost 仍呼叫 StartGuess/GuessNext/Stop；2) 在 AsyncPlayer.StartGuess 啟動 ThinkCaller，Wait _host_return 回傳第一猜；3) 在 GuessNext 寫入 Hint、Set 喚醒、Wait 下一猜；4) Stop 完成終局握手。這樣 Host 不需改動即可搭配主動策略 Player。注意：確保 Player 子類只透過基底公開的 AskQuestion 互動。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q1, B-Q2

C-Q5: 如何加入 Timeout 避免死等？
- A簡: 將 WaitOne 改為 WaitOne(timeout)，檢查結果並實作逾時中止與日誌。
- A詳: 實作：if(!_host_return.WaitOne(ms)){Log("timeout");CancelOrThrow();} 於 GuessNext/AskQuestion/Stop 的 Wait 加入逾時；策略：逾時時可丟擲 TimeoutException、嘗試重試、或標記中斷。注意：避免 Timeout 太短造成誤判；加入可調參數；在 finally 仍清理暫存並釋放事件。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q18, D-Q1, D-Q8

C-Q6: 如何安全停止 Think 執行緒？
- A簡: 以 Stop 注入終局 Hint 喚醒，Think 觀察條件退出；禁止強制中止。
- A詳: 避免 Thread.Abort。流程：Host.Stop() 寫入終局 Hint、Set _host_call；Think 收到後 break；ThinkCaller finally Set _host_end；Host Wait _host_end 後設 _host_complete。若策略有額外迴圈，應檢查取消旗標或條件，確保盡快退出。必要時搭配 CancellationToken。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q20, D-Q5

C-Q7: 如何記錄時序日誌便於除錯？
- A簡: 在每次寫入/Set/Wait 前後記錄含回合號、執行緒 ID、事件名稱的日誌。
- A詳: 步驟：1) 定義回合計數器；2) 在 AskQuestion 寫入前、Set 後、Wait 前後 Log；Host 端同理；3) 於逾時與例外加告警。程式：Log($"[t{ThreadId}] R{n} Set _host_return"); 注意避免過多 I/O 阻塞；可使用環形緩衝或等批寫出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, B-Q18, D-Q9

C-Q8: 如何以 ManualResetEventSlim 取代 AutoResetEvent？
- A簡: 手動 Reset 的輕量事件需小心廣播語義與 Reset 時機，並確保一次一喚醒。
- A詳: 實作：以兩個 ManualResetEventSlim 分離方向，Set 後 Host 取到立即 Reset；確保不存在第二等待者同時覺醒。片段：_ret.Set(); Wait(); _ret.Reset(); 風險：忘記 Reset 會導致誤喚醒；多等待者需額外鎖或序號以防交錯。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q23, B-Q15, D-Q8

C-Q9: 如何使用 Task 取代 Thread？
- A簡: 將 ThinkCaller 包成 Task.Run，並以 async/await 與 SemaphoreSlim/Channel 輔助同步。
- A詳: 範例：_thinkTask = Task.Run(ThinkCaller); 等待處改為 await evt.WaitAsync(token) 或使用 Channel 建雙向通道。注意：Task 的例外可觀察；停止用 CancellationToken 傳遞；避免同步阻塞造成執行緒匱乏。保持介面兼容，Host 端仍為同步呼叫。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, D-Q9, B-Q14

C-Q10: 如何撰寫單元測試驗證握手協定？
- A簡: 模擬 Host/Player 互動，斷言每回合序與資料一致，加入逾時保護。
- A詳: 測試：1) 驗證第一猜在 StartGuess 後可用；2) 迭代數回合：餵入 Hint，斷言 Player 確實提出下一猜；3) 模擬 Stop 後 AskQuestion 應丟例外；4) 故意晚到/先到檢驗不死等。使用 Stopwatch + Timeout，並在日誌中抓取事件序列比對。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, D-Q8, C-Q7

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 等待卡死（無限阻塞）怎麼辦？
- A簡: 檢查 Wait/Set 配對、加入 Timeout 與日誌，定位遺失訊號與例外路徑。
- A詳: 症狀：程式無回應，CPU 低；堆疊停在 WaitOne。可能原因：遺漏 Set、例外未捕捉導致對方未送訊號、鎖死。解法：為每個 WaitOne 加 Timeout，逾時記錄誰在等、等哪個事件；審視寫入→Set→Wait→讀取順序是否一致；檢查 ThinkCaller 是否丟例外並確實 Set _host_end。預防：以測試覆蓋先/後到情境，維持日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, B-Q7, C-Q7

D-Q2: 出現跨執行緒存取或 ObjectDisposedException？
- A簡: 確保事件與暫存物件生命週期內使用，停止後勿再提問，避免提前 Dispose。
- A詳: 症狀：在 Stop 後仍呼叫 AskQuestion；或清理過早。原因：生命週期界線不清、_host_complete 未檢查。解法：在 AskQuestion 第一行檢查 _host_complete；Stop 流程完成後再釋放；將 Dispose 與停止握手解耦。預防：以狀態機管理生命週期，單元測試覆蓋終止後動作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q5, C-Q6

D-Q3: 偶發 NullReference 出現在 _temp_hint/_temp_number？
- A簡: 檢查 finally 是否過早清空、讀寫是否在 lock 範圍內、是否有重入。
- A詳: 症狀：偶而讀到 null。原因：未在鎖內一致地寫/讀/清；或另一回合重疊。解法：確保整段交換在 lock 中；清空在 finally，且僅於回傳後；避免非預期重入。預防：加 Debug.Assert 檢查狀態、以回合序號輔助追蹤一致性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, B-Q20

D-Q4: CPU 飆高但無進展，如何診斷？
- A簡: 檢查是否忙等或緊密迴圈無阻塞；以事件或 sleep 降負載。
- A詳: 症狀：CPU 高佔用、進度停滯。原因：Think 迴圈未等待就重複計算；或日誌過量 I/O。解法：用事件阻塞等待回覆；限速或批次；降低日誌同步 I/O。預防：為長迴圈設計等待點，並以效能計數器監控。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, B-Q22, C-Q7

D-Q5: Host 停止後 Player 仍持續提問怎麼辦？
- A簡: 檢查 _host_complete 與終局 Hint 流程；在 AskQuestion 嚴格阻擋。
- A詳: 症狀：Stop 後仍看到 AskQuestion 呼叫。原因：Think 未依提示退出；_host_complete 未檢查。解法：Stop 注入可辨識的終局 Hint；Think 收到即 break；AskQuestion 開頭檢查 _host_complete 後丟例外。預防：策略在迴圈中定期檢查終止條件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q20, B-Q5, C-Q6

D-Q6: 答案錯置或順序錯亂（競態）如何解？
- A簡: 強化「寫→Set→Wait→讀」順序與鎖定；避免跨回合並行與重入。
- A詳: 症狀：拿到前一回合的 Hint。原因：未清理暫存、未鎖住整段交換、重入造成交疊。解法：在 lock 內完成整段流程；finally 清空暫存；於外層加序號比對；檢查呼叫端不並行呼叫。預防：以測試覆蓋快/慢端交錯情境。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q22, B-Q8, B-Q20

D-Q7: 多玩家並行互相干擾，怎麼排查？
- A簡: 確認各玩家不共享事件與暫存；避免使用靜態欄位；以實例隔離。
- A詳: 症狀：某玩家收到他人提示。原因：共用靜態 WaitHandle 或暫存變數。解法：將事件/暫存改為實例欄位；Host 以實例對應；必要時加上唯一 ID。預防：在設計期避免靜態共享；壓力測試驗證隔離性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q24, B-Q14, C-Q4

D-Q8: Set/Wait 順序競賽導致「遺失訊號」？
- A簡: 分離方向事件、固定順序、允許先到先等並加入 Timeout 與日誌確認。
- A詳: 症狀：偶發卡死；分析顯示 Set 早於對方 Wait。解法：維持固定時序與雙事件；即使早 Set，對方 Wait 時狀態仍為訊號，AutoResetEvent 將喚醒一人；若仍發生，檢查 Set 後是否立刻 Reset 或清空。預防：加 Timeout 與事件狀態檢查；以序號追蹤回合。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q15, B-Q18

D-Q9: 子執行緒例外未被發現，如何處理？
- A簡: 在 ThinkCaller 加 try/catch，記錄例外並以事件告知 Host 收尾。
- A詳: 症狀：Host 永久等待；背景已崩潰。原因：未捕捉的例外中斷流程且未送訊號。解法：在 ThinkCaller 捕捉所有例外並 Log；finally Set _host_end。若採 Task，監視 task.Exception。預防：單元測試注入例外路徑；加逾時。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, C-Q7, C-Q10

D-Q10: 效能不佳的原因與優化方向？
- A簡: 同步成本、上下文切換與頻繁握手；可減回合數、批次提問、或用 Task/Channel。
- A詳: 原因：多次 Set/Wait 和排程；策略太輕導致同步開銷占比高。優化：1) 改善猜測策略，減少回合；2) 批次傳遞資訊；3) 合併小步為大步；4) 使用 Task 與高效同步原語；5) 減少日誌 I/O；6) 調整事件/鎖的粒度。量測：以 Stopwatch 與 ETW/Profiler 觀察熱點。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q22, C-Q9

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是「兩個執行緒互相等待」的同步？
    - A-Q2: AsyncPlayer 的核心理念是什麼？
    - A-Q3: DummyPlayer 與 AsyncDummyPlayer 有何差異？
    - A-Q4: 為何要將被動呼叫轉為主動思考？
    - A-Q5: GameHost 與 Player 的職責應如何劃分？
    - A-Q6: StartGuess、GuessNext、Stop 的語意是什麼？
    - A-Q8: AutoResetEvent 是什麼？適用於何時？
    - A-Q9: WaitOne/Set 在同步中的作用是？
    - A-Q12: 同步與非同步的差異是什麼？
    - A-Q13: Think 方法中的「思考迴圈」是什麼？
    - A-Q14: 何謂「兩段式」Init/Think 設計？
    - A-Q15: 多型（Polymorphism）在此設計中的角色？
    - B-Q1: AsyncPlayer 整體如何運作？
    - B-Q2: StartGuess 與 Think 如何銜接？
    - B-Q3: GameHost_AskQuestion 的執行流程為何？

- 中級者：建議學習哪 20 題
    - B-Q4: GuessNext 如何喚醒 Player Thread？
    - B-Q5: Stop 如何終止雙方？
    - B-Q6: 為何需要三個 AutoResetEvent？各自用途是？
    - B-Q7: 如何以事件順序防止競賽與遺失訊號？
    - A-Q10: 為何需要 lock？
    - A-Q19: 什麼是雙向通道/握手協定？
    - A-Q20: Host 完成旗標 _host_complete 的用途？
    - A-Q21: 共用暫存變數為何設計成 _temp_number/_temp_hint？
    - B-Q8: lock 範圍內的核心組件有哪些？
    - B-Q9: 為什麼在 finally 清除暫存欄位？
    - B-Q10: _host_complete 何時與如何影響流程？
    - C-Q1: 如何將 DummyPlayer 改造成 AsyncDummyPlayer？
    - C-Q2: 如何實作 Init 與 Think 的骨架？
    - C-Q3: 如何在 Think 中迭代詢問直到答對？
    - C-Q4: 如何在不改 GameHost 的情況接入 AsyncPlayer？
    - D-Q1: 等待卡死（無限阻塞）怎麼辦？
    - D-Q3: 偶發 NullReference 出現在 _temp_hint/_temp_number？
    - D-Q5: Host 停止後 Player 仍持續提問怎麼辦？
    - D-Q6: 答案錯置或順序錯亂（競態）如何解？
    - A-Q16: 為何 AsyncDummyPlayer 可能比 DummyPlayer 慢？

- 高級者：建議關注哪 15 題
    - B-Q14: 此設計與 Producer-Consumer 佇列有何差異？
    - B-Q15: AutoResetEvent 與 ManualResetEvent 差異與取捨？
    - B-Q16: Thread 與 ThreadPool/Task 的差異與影響？
    - B-Q17: ThinkCaller 的 try/catch/finally 有何作用？
    - B-Q18: WaitOne 是否應加 Timeout？為何？
    - B-Q19: lock(this) 有何影響？有替代選擇嗎？
    - B-Q20: 此設計是否可重入？如何避免？
    - B-Q21: 記憶體可見性如何被保障？
    - B-Q22: 忙等 vs 事件阻塞的效率比較？
    - B-Q24: 如何擴充到多玩家並行？
    - C-Q5: 如何加入 Timeout 避免死等？
    - C-Q8: 如何以 ManualResetEventSlim 取代 AutoResetEvent？
    - C-Q9: 如何使用 Task 取代 Thread？
    - D-Q8: Set/Wait 順序競賽導致「遺失訊號」？
    - D-Q10: 效能不佳的原因與優化方向？