---
layout: synthesis
title: "Thread Sync #1. 概念篇 - 如何化被動為主動?"
synthesis_type: faq
source_post: /2008/08/14/thread-sync-1-concept-how-to-turn-passive-into-active/
redirect_from:
  - /2008/08/14/thread-sync-1-concept-how-to-turn-passive-into-active/faq/
---

# Thread Sync #1. 概念篇 - 如何化被動為主動?

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是執行緒同步（Thread Sync）？
- A簡: 跨執行緒協調時序與共享資料一致性的機制，避免競態、死鎖與訊號遺失。
- A詳: 執行緒同步是一組用於協調多個執行緒順序與共享狀態一致性的機制。當兩個執行緒需要彼此傳遞資料或等待對方進度時，必須用同步原語（如 AutoResetEvent、ManualResetEvent、lock/Monitor）保證時序正確，避免同時讀寫造成競態，或雙方都在等對方造成死鎖。同步的本質是給準確的「時機」與「可見性」保證，讓邏輯能以直覺順序執行。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q8, B-Q1

A-Q2: 為什麼需要執行緒同步？
- A簡: 確保跨執行緒協作正確，避免邏輯錯亂、卡住、資料不一致與忙等浪費資源。
- A詳: 在多執行緒協作中，若沒有同步，每個執行緒各自進行會導致多種問題：共享變數可能被競爭更新，產生不一致；等待順序不明會互卡；用輪詢忙等則耗 CPU。同步機制提供阻塞等待、訊號喚醒與記憶體可見性，讓協作可控，提升正確性與可維護性。本文以 GameHost/Player 問答為例，展示同步如何讓雙方用直覺流程合作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q6, D-Q4

A-Q3: 文中「化被動為主動」是什麼意思？
- A簡: 讓被動被呼叫的邏輯改為主動掌控時序，借助執行緒與同步自行推進流程。
- A詳: 傳統單迴圈下，小角色只能被主程式定期呼叫，邏輯被迫拆片段。化被動為主動的思路是：各邏輯擁有自己的執行緒，依自然語意與順序前進；需要互動時，以同步原語交換訊號與資料。這樣每方都能主動決定何時等、何時進一步，既貼近心智模型又降低拆分負擔，進而讓複雜策略更易實作與維護。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1, B-Q3

A-Q4: 單一主迴圈設計與多執行緒設計有何差異？
- A簡: 單迴圈需拆邏輯成片段被輪詢；多執行緒讓各角色獨立前進，以同步精準對話。
- A詳: 單一主迴圈（refresh loop）模式中，畫面更新與輸入檢查綁在固定頻率迴圈，邏輯被拆成可重入的小段供輪詢。多執行緒則讓每個角色持有自己的「連續」流程，僅在需要資料交換時透過 Wait/Set 等同步交握。前者簡單但易變成狀態機碎片，後者接近真實互動、擴充性好，但需要正確的同步協定避免時序問題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q4, B-Q1

A-Q5: GameHost 與 Player 在文中分別扮演什麼角色？
- A簡: GameHost 主持流程並回應提問；Player 依策略主動提問與解讀答案。
- A詳: 在猜數字的架構中，GameHost 是「莊家」，負責出題與回覆玩家的提問（回傳 A/B 結果）；Player 是「玩家」，擬定策略、提出猜測、接收回覆並調整。傳統設計由 Host 持續呼叫 Player（被動），文中改以雙執行緒各自推進流程，以同步交換題目與答案，讓兩方的思路更直觀、角色清晰。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q1, C-Q1

A-Q6: 為何傳統遊戲邏輯需要被拆成片段？
- A簡: 因主迴圈固定頻率輪詢，邏輯須切成可重入小步以供每幀調度。
- A詳: 在固定幀率的主迴圈中，程式需在每次迴圈內完成更新與渲染。為避免卡頓，複雜邏輯不能長時間阻塞，只能拆成狀態導向的短步驟：讀輸入、移動一格、旋轉一次、檢查碰撞等。這讓原本一氣呵成的流程被迫斷裂、由狀態拼湊回去，增加維護複雜度。多執行緒能避免此碎片化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q4, C-Q4

A-Q7: 多執行緒如何簡化思路與流程？
- A簡: 讓邏輯連續表達，僅在需要互動時用同步交握，避免狀態機碎片化。
- A詳: 多執行緒允許每個角色以自然流程撰寫：推理、提出提問、等待回覆、更新假設、再提問。資料交換處由同步原語封裝成明確交握點，透過 Wait/Set 控制先後，避免無限輪詢。如此一來，策略設計更聚焦、本體邏輯更可讀，降低錯誤率，擴充也只需增加交握點或通道，不必重寫拆分邏輯。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, C-Q1

A-Q8: AutoResetEvent 的定義與用途是什麼？
- A簡: 一種一次性訊號事件；Set 喚醒單一等待執行緒後自動重置。
- A詳: AutoResetEvent 是 .NET 的同步原語。當狀態為非訊號時，WaitOne 會阻塞；當呼叫 Set 後，狀態變為訊號並喚醒一個等待者，且立即自動重置回非訊號。適合用於點對點交握，避免多個等待者同時通過。文中用它在 Host/Player 之間傳遞「資料已備妥」或「已接招」的時機控制。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q3, C-Q1

A-Q9: Wait() 與 Set() 在同步中扮演什麼角色？
- A簡: Wait 負責阻塞等待條件達成；Set 發出訊號喚醒等待的一方繼續執行。
- A詳: 在訊號/等待模型中，等待方在關鍵點呼叫 Wait（如 WaitOne），程式阻塞直到條件成立；對方完成準備工作後呼叫 Set，將事件設為訊號，喚醒等待的執行緒。此機制避免忙等，提供確定的時序控制。搭配共用變數傳遞資料，能形成清晰的交握協定，降低錯誤與資源浪費。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q3, C-Q6

A-Q10: 共用變數在執行緒通訊中的角色？
- A簡: 作為資料載體；配合同步事件保證先寫後讀與可見性一致。
- A詳: 雙方透過共用變數承載題目與答案本身，事件只承擔時序控制。寫方先更新共用變數，再發出 Set；讀方醒來後立即讀取。為避免競態與舊值，可搭配 lock、volatile 或記憶體屏障，並以序號或時間戳區分訊息次序，確保資料與訊號對齊，不致亂序或遺失。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q9, D-Q2

A-Q11: 使用執行緒是為了效能還是簡化問題？
- A簡: 本文重點是簡化設計與思考，而非追求平行化效能。
- A詳: 多執行緒常被視為效能工具，但本文用它減少設計複雜度：讓各角色保有自然流程，透過同步交握交換資料。即便不提升吞吐，此法仍能讓邏輯更直觀、易測試、可擴充。當思維負擔下降後，反而更容易導入更高明的策略或後續性能優化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q1, B-Q11

A-Q12: 多型（Polymorphism）在互動中的價值是什麼？
- A簡: 讓 Host 以抽象介面呼叫 Player，多種策略可替換、擴展與測試。
- A詳: Host 依賴抽象的 Player 介面（如 GuessNum），可注入不同實作而不改 Host。這將控制反轉到 Player 策略，利於測試與替換。若結合執行緒同步，Host 與 Player 甚至各自以主動流程驅動，互動僅依介面與同步協定，實現低耦合、高可維護的設計。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q8, B-Q13, A-Q5

A-Q13: 為何不以回呼（Callback）改變主從關係？
- A簡: 雙方都需主動推進與阻塞等待；僅回呼難以對稱且不利擴展到多方。
- A詳: 回呼可讓 Host 被動接受 Player 問題，但難以表述雙向同步等待，且會加深誰主誰從的耦合。若未來成為多玩家或對戰，回呼架構易爆炸。以對稱的執行緒 + 同步事件，雙方皆可主動推進與等待，協定清晰、擴展容易，避免主從僵化帶來的複雜度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q13, C-Q1

A-Q14: AutoResetEvent 與 ManualResetEvent 有何差異？
- A簡: Auto 一次喚醒單一等待者即自動重置；Manual 需手動重置可廣播多方。
- A詳: AutoResetEvent 適合點對點交握：Set 只放行一個 Wait 者並自動復位。ManualResetEvent 則像總閘門：Set 後所有等待者可通過，直到手動 Reset。前者用於 Host/Player 對稱握手；後者適合開始/暫停、初始化完成等廣播事件。選擇應依通過者數量與重置語意決定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q7, D-Q5

A-Q15: 同步機制的核心價值與限制是什麼？
- A簡: 提供可預測時序與可見性；代價是設計交握、避免死鎖並理解時序風險。
- A詳: 核心價值在於精準控制「何時等、何時喚醒、資料何時一致」。它讓複雜互動更可靠、邏輯貼近人類思考。限制在於需要妥善協定、正確實作，否則將引入死鎖、競態、訊號遺失與除錯困難。良好日誌、逾時、重試與測試策略是同步設計不可或缺的配套。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, D-Q1, D-Q3


### Q&A 類別 B: 技術原理類

B-Q1: 兩執行緒問答協作如何運作？
- A簡: 以兩個 AutoResetEvent 與共享變數，依序 Wait/Set 進行題目與答案交握。
- A詳: 原理說明：Host 與 Player 各跑在獨立執行緒。用 shared 問題/答案欄位承載資料，用兩個 AutoResetEvent（reqReady、respReady）表示「題目就緒」與「答案就緒」。流程：1) Player 寫入問題→Set(reqReady)；2) Host Wait(reqReady)→讀題→計算→寫答案→Set(respReady)；3) Player Wait(respReady)→讀答案→更新策略。核心組件：AutoResetEvent、共享資料、序號/時間戳。關鍵步驟：先寫資料再 Set，先 Wait 再讀資料，形成穩定交握。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q9, C-Q1

B-Q2: AutoResetEvent 的機制與訊號語意是什麼？
- A簡: 內部維護二元狀態；Set 釋放一個等待者並自動復位，避免廣播。
- A詳: 技術原理說明：AutoResetEvent 以核心事件物件維護「訊號/非訊號」狀態。WaitOne 在非訊號時阻塞，直到訊號化或逾時；Set 將狀態設為訊號，喚醒恰一個等待者，然後自動設回非訊號。關鍵步驟：Set 先於 Wait 可能造成訊號累積一次，後來的 Wait 可立即通過一次。核心組件：事件狀態、等待佇列。它特別適合一對一交握，保證單次通行。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q3, D-Q5

B-Q3: Wait/Set 交握協定的標準流程為何？
- A簡: 先寫入共享資料，再 Set；對方先 Wait 再讀取，雙方重複此序確保一致。
- A詳: 原理說明：交握由資料與訊號兩路構成。關鍵步驟：1) 產生方先更新共享變數與序號；2) 立即 Set 對應事件；3) 消費方先 Wait 對應事件；4) 醒來後檢查序號並讀取資料；5) 必要時回 Set 另一事件。核心組件：共享資料結構、兩個事件（req/resp）、序號避免亂序。此模式避免忙等與資料競爭，形成可證明的時序。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q2, C-Q6

B-Q4: 單一主迴圈（refresh loop）如何運作？
- A簡: 以固定頻率輪詢輸入、更新狀態、渲染畫面，邏輯拆成小步重入。
- A詳: 原理：主迴圈在每幀執行「處理輸入→更新世界→渲染」三步。為避免卡幀，每步須短小且可重入。關鍵步驟：狀態機驅動、時間片切分、事件佇列處理。核心組件：定時器/時鐘、畫面刷新、輸入緩衝。優點是簡單可預測；缺點是複雜策略需拆分，邏輯分散且難測。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, C-Q4, C-Q5

B-Q5: 如何用共享變數安全傳遞資料？
- A簡: 配合 lock/volatile 與事件順序，保證先寫後讀與記憶體可見性。
- A詳: 原理：共享資料需避免競態與舊值。關鍵步驟：1) 寫方於 lock 內更新資料與遞增序號；2) 發 Set；3) 讀方 Wait 後 lock 內讀資料並驗序號。核心組件：lock/Monitor、volatile 欄位、序號或時間戳。這確保寫入在邏輯上「先於」讀取，且多核心下可見性一致，避免讀到上一輪的值。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, D-Q2, D-Q6

B-Q6: 如何避免忙等（busy-waiting）？
- A簡: 以阻塞等待的 Wait/Set 設計交握，移除輪詢與 Thread.Sleep 依賴。
- A詳: 原理：忙等透過持續輪詢或短暫 Sleep 檢查條件，浪費 CPU 且不精準。改用事件：消費方 Wait 阻塞，產生方完成即 Set 喚醒。關鍵步驟：確認所有等待點以事件驅動；提供逾時防卡死。核心組件：AutoResetEvent/ManualResetEvent、逾時值。此法降低資源耗用並提升時序可控。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, C-Q6, D-Q4

B-Q7: ManualResetEvent 適用於哪些場景？
- A簡: 用於「廣播式」或「閘門式」同步，如開始、暫停、初始化完成。
- A詳: 原理：ManualResetEvent 在 Set 後保持訊號直到手動 Reset。關鍵步驟：在需要多個等待者同時通過時使用，例如系統完成初始化後釋放所有工作緒，或實作暫停/繼續。核心組件：事件狀態、Reset 時機控制。與 Auto 相比，它不是一對一交握，而是一次性開閘門給多方通過。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q7, D-Q5

B-Q8: 雙向資料流如何避免順序逆轉與亂序？
- A簡: 為每次交握加序號，固定「先寫後 Set、先 Wait 後讀」並分離通道。
- A詳: 原理：雙向同時發送易亂序。關鍵步驟：1) 問題與答案各用一個事件；2) 資料攜帶遞增序號；3) 寫→Set、Wait→讀順序嚴格一致；4) 若雙方可能同時發，約定誰先誰後或序號比較。核心組件：兩事件通道、序號、原子遞增。此法避免兩端互搶與覆蓋，確保交握可追蹤。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q3, D-Q2, C-Q9

B-Q9: 線程間記憶體可見性如何保障？
- A簡: 倚賴同步原語的記憶體屏障，或使用 lock/volatile 確認有序與可見。
- A詳: 原理：多核心下寫入不一定立即對他緒可見。Wait/Set、lock/Monitor 內建記憶體屏障，確保進入/離開臨界區的操作對他緒可見。關鍵步驟：在交握前後的讀寫包在同步操作內；對旗標用 volatile；避免無同步的讀寫。核心組件：記憶體屏障、cache coherency。這是避免讀到舊值的關鍵。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q5, D-Q6, C-Q1

B-Q10: 競態、死鎖與訊號遺失的機制是什麼？
- A簡: 競態源自未同步的同時存取；死鎖來自循環等待；訊號遺失因 Set/Wait 順序錯。
- A詳: 原理：競態在沒有原子性與順序保障時發生。死鎖多因雙方各持資源互等、或雙 Wait 無 Set。訊號遺失常見於先 Set 後 Wait 且事件不累積，導致後到的 Wait 永久卡住。關鍵步驟：建立總排序與固定交握；使用逾時與重試；紀錄時序。核心組件：事件、鎖、總序協定。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q1, D-Q5, C-Q6

B-Q11: Thread Pool 與專用執行緒的差異？
- A簡: 池化緒重用、管理成本低；專用緒時序可控、適合長期互動。
- A詳: 原理：Thread Pool 透過工作佇列與有限工作緒處理短任務，啟動快且節省資源。專用緒則綁定整段流程與狀態機，時序與生命週期更可控。關鍵步驟：若需持續交握與阻塞等待，偏向專用緒；若是短期計算或 I/O 回呼，使用池化緒。核心組件：工作佇列、排程器、執行緒生命週期。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, D-Q3

B-Q12: lock/Monitor 與 AutoResetEvent 的差異？
- A簡: lock 管理臨界區互斥；事件管理時序交握。常需兩者搭配。
- A詳: 原理：lock 保證同時只有一緒進入臨界區，解決互斥；AutoResetEvent 提供跨緒時序通知，解決先後。關鍵步驟：在寫/讀共享資料用 lock 確保一致；在資料就緒與消費完成用事件 Wait/Set。核心組件：Monitor.Enter/Exit、AutoResetEvent.Wait/Set。兩者互補，避免只鎖不通知或只通知不一致。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q1, D-Q2

B-Q13: 如何設計可擴充到多玩家的同步架構？
- A簡: 為每玩家建立獨立通道與事件，或以佇列+事件集中管理。
- A詳: 原理：多玩家共享一對事件會互相干擾。關鍵步驟：1) 每玩家一組 req/resp 事件與共享區；或2) 中央佇列承載請求，配合 AutoResetEvent 喚醒 Host；回覆以玩家專屬事件。核心組件：事件映射表、訊息佇列、玩家 ID。此設計隔離時序，避免訊號串音，利於彈性擴展。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q1, D-Q7, C-Q9

B-Q14: 非阻塞與逾時控制如何設計？
- A簡: 使用 WaitOne(timeout)、Try* 模式與重試策略，避免永久卡死。
- A詳: 原理：阻塞等待在異常時可能無限卡住。關鍵步驟：1) WaitOne 設逾時；2) 逾時後檢查狀態並重試或中止；3) 記錄告警與時序；4) 必要時採非阻塞嘗試（TryDequeue）。核心組件：逾時常數、重試次數、取消旗標。這讓系統在不確定環境下仍可控、可恢復。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q6, D-Q3, D-Q9

B-Q15: 如何用日誌與時序圖支援同步除錯？
- A簡: 對每次交握打時間戳與序號，繪製時序流追蹤 Wait/Set 與資料流。
- A詳: 原理：同步錯誤常是時序與狀態問題。關鍵步驟：每次寫/讀/Wait/Set 記錄時間、緒 ID、序號與資料摘要；遇到逾時與重試額外標註；離線重建時序圖檢視交握因果。核心組件：結構化日誌、關聯 ID、視覺化工具。這大幅提升定位競態、遺失訊號與死鎖根因的效率。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, D-Q9, B-Q10


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何用 AutoResetEvent 實作 Host-Player 互動？
- A簡: 建立問題/答案共享結構與兩事件，依寫→Set、Wait→讀流程交握。
- A詳: 實作步驟：1) 定義共享結構含序號、問題、答案；2) 建立 reqReady、respReady 兩個 AutoResetEvent；3) Player：填問題+遞增序號→Set(reqReady)→Wait(respReady)→讀答案；4) Host：Wait(reqReady)→讀問題→計算→填答案→Set(respReady)。程式碼片段:
  csharp
  class Bus { public int Seq; public string Q; public string A; }
  var bus=new Bus(); var req=new AutoResetEvent(false); var resp=new AutoResetEvent(false);
  // Player
  void PlayerLoop(){ int seq=0; while(true){ lock(bus){ bus.Seq=++seq; bus.Q=NextGuess(); } req.Set(); resp.WaitOne(); string ans; lock(bus){ ans=bus.A; } Consume(ans); } }
  // Host
  void HostLoop(){ while(true){ req.WaitOne(); string q; int s; lock(bus){ s=bus.Seq; q=bus.Q; bus.A=Judge(q); } resp.Set(); } }
  注意事項：先寫後 Set，先 Wait 後讀；資料存取用 lock；加入逾時與終止條件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, C-Q6

C-Q2: 如何以共享變數與 lock 傳遞問題與答案？
- A簡: 將資料存放在共享物件，讀寫皆以 lock 包裹並搭配序號驗證。
- A詳: 實作步驟：1) 定義 class Exchange{int Seq; string Q; string A;}；2) 寫入端 lock(ex){ ex.Seq++; ex.Q=...;} →Set；3) 讀取端 Wait→lock(ex){ if(localSeq+1==ex.Seq) Read }。程式碼片段:
  csharp
  class Exchange{ public int Seq; public string Q; public string A; }
  var ex=new Exchange(); var ev=new AutoResetEvent(false);
  void Producer(){ lock(ex){ ex.Seq++; ex.Q="1234"; } ev.Set(); }
  void Consumer(){ ev.WaitOne(); lock(ex){ Console.WriteLine(ex.Seq+":"+ex.Q); } }
  最佳實踐：以 lock 保證一致；序號防亂序；避免以多個鎖包同一資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q2, D-Q6

C-Q3: 如何設計雙方的執行緒生命週期？
- A簡: 明確啟動、運行、停止與釋放，搭配取消旗標與 Join 等待結束。
- A詳: 實作步驟：1) 建立 Thread hostT/playerT；2) 使用 volatile bool _stop；3) 迴圈內定期檢查 _stop；4) 停止時 Set 事件解鎖 Wait；5) Join 等待緒結束；6) Dispose 事件。程式碼片段:
  csharp
  volatile bool _stop=false; var req=new AutoResetEvent(false); var resp=new AutoResetEvent(false);
  var hostT=new Thread(HostLoop); var playerT=new Thread(PlayerLoop);
  hostT.Start(); playerT.Start();
  // 停止
  _stop=true; req.Set(); resp.Set(); hostT.Join(); playerT.Join(); req.Dispose(); resp.Dispose();
  注意：避免在終止時遺留阻塞；確保釋放事件；在迴圈中檢查取消。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q14, D-Q3

C-Q4: 如何在 C# 實作單一主迴圈的 Tetris？
- A簡: 使用固定步長迴圈，輪詢輸入、更新方塊、碰撞檢查與渲染畫面。
- A詳: 實作步驟：1) 設定目標幀率；2) while 迴圈內：讀鍵盤→根據狀態移動/旋轉→每隔 N 幀下降→檢查碰撞/消行→渲染；3) 控制迴圈節拍。程式碼片段:
  csharp
  var sw=Stopwatch.StartNew(); long next=0; while(running){
    HandleInput(); if(Frame()%10==0) DropOne(); CheckCollision(); Render();
    var now=sw.ElapsedMilliseconds; if(now<next) Thread.Sleep((int)(next-now)); next+=16;
  }
  注意：每步必須短小可重入；避免長阻塞；狀態機清晰可測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, A-Q6, C-Q5

C-Q5: 如何以兩執行緒重構 Tetris：掉落與輸入分離？
- A簡: 掉落緒定時下移；輸入緒處理按鍵；以事件或佇列協調狀態更新。
- A詳: 實作步驟：1) Thread dropT 以定時器/睡眠週期呼叫 DropOne；2) Thread inputT 監聽鍵盤，將動作佇列化；3) 以 lock 保護遊戲狀態；4) 用 AutoResetEvent 通知渲染緒。程式碼片段:
  csharp
  var actQ=new ConcurrentQueue<Action>(); var updateEv=new AutoResetEvent(false);
  void InputLoop(){ while(run){ var k=Console.ReadKey(true); actQ.Enqueue(()=>MoveByKey(k)); updateEv.Set(); } }
  void DropLoop(){ while(run){ Thread.Sleep(500); actQ.Enqueue(DropOne); updateEv.Set(); } }
  void RenderLoop(){ while(run){ updateEv.WaitOne(); while(actQ.TryDequeue(out var a)){ lock(state) a(); } Draw(); } }
  注意：避免兩緒直接改狀態；以序列化動作更新，防止競態。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q6, D-Q4

C-Q6: 如何加入逾時與重試避免卡死？
- A簡: WaitOne 設逾時；逾時時重試或中止；紀錄錯誤與釋放阻塞方。
- A詳: 實作步驟：1) const int TimeoutMs=2000；2) if(!ev.WaitOne(TimeoutMs)) { log; retries++; if(retries>max) Cancel(); else continue; }；3) 終止時 Set 對側事件解鎖。程式碼片段:
  csharp
  const int TO=2000; int retries=0, max=3;
  if(!resp.WaitOne(TO)){ Log("resp timeout"); if(++retries>max){ _stop=true; req.Set(); resp.Set(); } else continue; }
  最佳實踐：逾時要可調；記錄序號與緒 ID；避免無限等待。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, D-Q3, D-Q1

C-Q7: 如何用 ManualResetEvent 實作開始/暫停？
- A簡: 以 ManualResetEvent 當閘門；暫停 Reset、繼續 Set，工作緒 Wait 通過。
- A詳: 實作步驟：1) var gate=new ManualResetEvent(false)；2) 工作緒在重要步驟前 gate.WaitOne()；3) Start 時 gate.Set()；4) Pause 時 gate.Reset()。程式碼片段:
  csharp
  var gate=new ManualResetEvent(false);
  void Worker(){ while(run){ gate.WaitOne(); DoStep(); } }
  void Start()=>gate.Set(); void Pause()=>gate.Reset();
  注意：避免在持有鎖時 Wait；暫停應僅阻擋「步驟邊界」，避免卡在中途持鎖。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q1, D-Q5

C-Q8: 如何設計可測試的 IPlayer 介面與假物件？
- A簡: 以抽象介面定義提問/接收方法，測試以假 Host/Player 驗證交握。
- A詳: 實作步驟：1) 定義介面 IPlayer{ string NextGuess(string lastAnswer);}；2) Host 按交握協定呼叫；3) 實作 FakeHost/FakePlayer 注入固定回覆；4) 單元測試驗證序號與 Wait/Set 次序。程式碼片段:
  csharp
  public interface IPlayer{ string NextGuess(string lastAnswer); }
  public class Host{ public string Judge(string guess)=>"..."; }
  // 測試以假類別記錄呼叫順序與資料，斷言交握正確
  注意：介面要小而穩；以依賴注入替換實作；加入記錄以便驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q10, B-Q15

C-Q9: 如何記錄時序日誌以除錯同步？
- A簡: 為每次寫/讀/Wait/Set 記錄時間、序號、緒 ID，串接為時序流。
- A詳: 實作步驟：1) 設計 Log(EventType, Seq, ThreadId, Timestamp, DataHash)；2) 在所有交握點呼叫；3) 發生逾時重試時額外標示；4) 收集後可視覺化。程式碼片段:
  csharp
  void Log(string evt,int seq)=>Console.WriteLine($"{DateTime.UtcNow:o}|{Thread.CurrentThread.ManagedThreadId}|{seq}|{evt}");
  // 例：Log("WRITE_Q", seq); req.Set(); Log("SET_REQ", seq);
  最佳實踐：避免大量字串影響性能；必要時用 ETW 或結構化日誌。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, D-Q9, B-Q10

C-Q10: 如何撰寫單元測試驗證交握協定？
- A簡: 注入假 Host/Player，控制時序與逾時，斷言序號與 Wait/Set 順序。
- A詳: 實作步驟：1) 使用可注入的事件與時鐘；2) 以 FakePlayer 產生已知序列；3) FakeHost 延遲回覆模擬 Wait；4) 測試逾時路徑；5) 斷言：先寫後 Set、先 Wait 後讀、序號單調。程式碼片段（示意）:
  csharp
  [Fact] void Handshake_Order_Is_Correct(){ var trace=new List<string>(); // 注入記錄器
    // 執行互動… 最後 Assert.Contains("WRITE_Q->SET_REQ->WAIT_RESP->READ_A", Flatten(trace));
  }
  注意：測試需可重現；避免 Sleep，使用可控時鐘與手動觸發事件。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q8, B-Q14, B-Q15


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到兩端都在 Wait，程式卡死怎麼辦？
- A簡: 檢查交握協定是否缺少 Set；加入逾時、日誌與單向總序避免循環等候。
- A詳: 症狀：Host/Player 均阻塞不動、CPU 低。可能原因：雙方同時 Wait 無任何一方 Set；握手順序相反；持鎖後 Wait 導致對方無法 Set。解決步驟：1) 為 Wait 設逾時並記錄；2) 審視協定，固定先後與責任；3) 禁止在持鎖時 Wait；4) 終止流程時廣播 Set 解鎖。預防：以單元測試覆蓋逾時路徑，審查握手時序圖。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q6, B-Q15

D-Q2: 問題與答案亂序導致邏輯錯亂怎麼辦？
- A簡: 為訊息加序號/時間戳；讀取時驗證配對；必要時丟棄過期資料。
- A詳: 症狀：讀到上一輪答案或與當前問題不符。原因：多執行緒同時更新共享變數，或跨通道時序不一致。解法：1) 每次寫資料遞增 Seq；2) 讀取驗證 Seq 是否匹配；3) 使用 lock 保護讀寫；4) 如雙向同時發，定義優先順序或用佇列。預防：在日誌中記錄 Seq 串流，測試亂序情境。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q5, C-Q9

D-Q3: WaitOne 逾時頻繁發生的原因與解法？
- A簡: 可能因 Set 遺失、對方阻塞或時序錯；加逾時重試與解鎖策略。
- A詳: 症狀：大量逾時告警與重試。原因：Set 在 Wait 前發出且未累積；對方卡在持鎖耗時區；事件被錯誤重置。解法：1) 審查「寫→Set、Wait→讀」順序；2) 限制臨界區時間；3) 確認事件初始狀態與重置時機；4) 適當延長逾時。預防：壓力測試與時序日誌，加入健康檢查指標。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, B-Q10, C-Q6

D-Q4: CPU 佔用高的忙等行為如何排除？
- A簡: 用阻塞事件取代輪詢；移除無意義 Sleep；以事件驅動更新。
- A詳: 症狀：CPU 長時間高、卻無實際工作。原因：輪詢共享變數或過度短 Sleep。解法：1) 以 Auto/ManualResetEvent 改為 Wait；2) 僅在狀態變化 Set 喚醒；3) 調整架構成事件驅動管線。預防：程式碼審查尋找 while(true) 輪詢；加效能監控辨識忙等。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q5, C-Q6

D-Q5: 訊號提前 Set 造成遺失如何處理？
- A簡: 確保 Wait 先於 Set 建立；或使用狀態旗標與重入檢查補償。
- A詳: 症狀：明明 Set 過，對方仍永久等待。原因：Set 在 Wait 前發出，AutoResetEvent 只累積一次，後續 Wait 可能無對應訊號。解法：1) 調整流程保證 Wait 先建立；2) 使用「狀態變量+事件」雙保險，Wait 前先檢查已就緒；3) 必要時改用 ManualResetEvent。預防：以時序日誌驗證先後。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q2, B-Q7, B-Q10

D-Q6: 共享變數讀到舊值（可見性問題）怎麼解？
- A簡: 以 lock/volatile 與同步事件的記憶體屏障，確保寫入對他緒可見。
- A詳: 症狀：偶爾讀到上一輪資料。原因：CPU 快取/編譯器重排導致跨緒不可見。解法：1) 將共享欄位設 volatile；2) 所有讀寫包在同一把 lock；3) 依賴 Wait/Set/lock 的屏障語義。預防：避免無鎖跨緒存取；加入單元測試於高併發下檢驗。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, B-Q5, C-Q2

D-Q7: 多玩家擴展後訊號互相干擾怎麼辦？
- A簡: 為每玩家建立獨立事件或用佇列分流，避免共享事件串音。
- A詳: 症狀：A 的 Set 喚醒了 B；回覆串錯人。原因：多玩家共用同一事件通道。解法：1) 每玩家一組 req/resp 事件；2) 或集中式佇列+事件喚醒 Host，回覆用玩家專屬事件；3) 為訊息攜帶玩家 ID 與序號。預防：在設計時就隔離通道與命名清楚。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q9, C-Q1

D-Q8: UI 凍結因在 UI 執行緒 Wait 該怎麼辦？
- A簡: 切至背景緒進行等待與計算；UI 用事件回貼更新，避免阻塞訊息泵。
- A詳: 症狀：視窗無回應。原因：在 UI 執行緒直接 WaitOne 阻塞消息迴圈。解法：1) 將同步等待移到背景緒；2) UI 訂閱結果事件並回到 UI 執行緒更新；3) 或使用 async/await 與 Dispatcher。預防：規範 UI 執行緒只做短任務，不做阻塞等待。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q11, C-Q5

D-Q9: 同步問題偶現難重現，如何診斷？
- A簡: 啟用結構化時序日誌、序號與緒 ID，重建時序並縮小可疑區段。
- A詳: 症狀：偶發亂序/逾時，難以重現。解法：1) 在所有交握點打日誌（時間、序號、緒 ID）；2) 將事件與資料關聯；3) 於錯誤時保存核心快照；4) 用重播或模擬工具重建。預防：從一開始就植入可觀測性，為關鍵流程加測試鉤子。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15, C-Q9, C-Q10

D-Q10: 不同硬體/環境下行為差異如何穩定？
- A簡: 移除時間依賴，使用事件同步與逾時；避免 Sleep；以參數化設定調整。
- A詳: 症狀：在快/慢機器上呈現不同錯誤。原因：依賴 Sleep 時間、不可見性與調度差異。解法：1) 以事件驅動取代時間輪詢；2) 對 Wait 設合理逾時；3) 移除硬編碼 Sleep；4) 將時間/重試參數化。預防：跨平台壓測，建立可調監控與警示。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q14, C-Q6


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是執行緒同步（Thread Sync）？
    - A-Q2: 為什麼需要執行緒同步？
    - A-Q3: 文中「化被動為主動」是什麼意思？
    - A-Q4: 單一主迴圈設計與多執行緒設計有何差異？
    - A-Q5: GameHost 與 Player 在架構中的角色是？
    - A-Q6: 為何傳統遊戲邏輯需要被拆成片段？
    - A-Q7: 多執行緒如何簡化思路與流程？
    - A-Q8: AutoResetEvent 的定義與用途是什麼？
    - A-Q9: Wait() 與 Set() 在同步中扮演什麼角色？
    - B-Q4: 單一主迴圈（refresh loop）如何運作？
    - B-Q6: 如何避免忙等（busy-waiting）？
    - B-Q7: ManualResetEvent 適用於哪些場景？
    - C-Q4: 如何在 C# 實作單一主迴圈的 Tetris？
    - C-Q7: 如何用 ManualResetEvent 實作開始/暫停？
    - D-Q4: CPU 佔用高的忙等行為如何排除？

- 中級者：建議學習哪 20 題
    - B-Q1: 兩執行緒問答協作如何運作？
    - B-Q2: AutoResetEvent 的機制與訊號語意是什麼？
    - B-Q3: Wait/Set 交握協定的標準流程為何？
    - B-Q5: 如何用共享變數安全傳遞資料？
    - B-Q8: 雙向資料流如何避免順序逆轉與亂序？
    - B-Q9: 線程間記憶體可見性如何保障？
    - B-Q10: 競態、死鎖與訊號遺失的機制是什麼？
    - B-Q11: Thread Pool 與專用執行緒的差異？
    - B-Q12: lock/Monitor 與 AutoResetEvent 的差異？
    - B-Q14: 非阻塞與逾時控制如何設計？
    - B-Q15: 如何用日誌與時序圖支援同步除錯？
    - C-Q1: 如何用 AutoResetEvent 實作 Host-Player 互動？
    - C-Q2: 如何以共享變數與 lock 傳遞問題與答案？
    - C-Q3: 如何設計雙方的執行緒生命週期？
    - C-Q5: 如何以兩執行緒重構 Tetris：掉落與輸入分離？
    - C-Q6: 如何加入逾時與重試避免卡死？
    - C-Q9: 如何記錄時序日誌以除錯同步？
    - C-Q10: 如何撰寫單元測試驗證交握協定？
    - D-Q1: 遇到兩端都在 Wait，程式卡死怎麼辦？
    - D-Q3: WaitOne 逾時頻繁發生的原因與解法？

- 高級者：建議關注哪 15 題
    - A-Q14: AutoResetEvent 與 ManualResetEvent 有何差異？
    - A-Q15: 同步機制的核心價值與限制是什麼？
    - B-Q8: 雙向資料流如何避免順序逆轉與亂序？
    - B-Q9: 線程間記憶體可見性如何保障？
    - B-Q10: 競態、死鎖與訊號遺失的機制是什麼？
    - B-Q13: 如何設計可擴充到多玩家的同步架構？
    - B-Q14: 非阻塞與逾時控制如何設計？
    - B-Q15: 如何用日誌與時序圖支援同步除錯？
    - C-Q5: 兩執行緒重構 Tetris：掉落與輸入分離
    - C-Q6: 加入逾時與重試避免卡死
    - C-Q9: 加入時序日誌與追蹤 ID
    - D-Q2: 問題與答案亂序導致邏輯錯亂怎麼辦？
    - D-Q5: 訊號提前 Set 造成遺失如何處理？
    - D-Q6: 共享變數讀到舊值（可見性問題）怎麼解？
    - D-Q10: 不同硬體/環境下行為差異如何穩定？