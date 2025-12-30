---
layout: synthesis
title: "Thread Sync #2. 實作篇 - 互相等待的兩個執行緒"
synthesis_type: summary
source_post: /2008/08/15/thread-sync-2-implementation-two-threads-waiting-for-each-other/
redirect_from:
  - /2008/08/15/thread-sync-2-implementation-two-threads-waiting-for-each-other/summary/
---

# Thread Sync #2. 實作篇 - 互相等待的兩個執行緒

## 摘要提示
- 呼叫模式對比: 以 GameHost 主導的被動式呼叫與以 Player 主導的主動式呼叫，呈現兩種截然不同的設計思維。
- DummyPlayer 限制: 被動流程導致邏輯被拆散，只能靠狀態變數與多次回呼拼湊解題過程。
- AsyncPlayer 核心: 以執行緒與 AutoResetEvent 建立問答同步點，將被動回呼轉化為主動思考。
- Think 迴圈: Player 在獨立執行緒中以 while 迴圈推進策略，適時向 GameHost 詢問提示。
- WaitHandle 同步: _host_return 與 _host_call 負責雙向喚醒，確保題目與提示的交握秩序。
- 介面不變、行為轉換: 對 GameHost 而言仍是 StartGuess/GuessNext/Stop，內部則以 AsyncPlayer 橋接主動式流程。
- thread-safety 設計: GameHost_AskQuestion 以 lock 保護共享緩衝，避免競態與資料殘留。
- 完整收尾: Stop 與 _host_end 確保 Player 執行緒結束與主控流程對齊。
- 效能取捨: 主動同步帶來更清晰邏輯，但由於同步開銷，示例效能落後隨機型 DummyPlayer。
- 設計啟示: 當問題過於複雜時，先用同步與結構化執行流簡化思考，再追求效能最佳化。

## 全文重點
本文延續前文的概念，從實作層面展示如何把一個「由 GameHost 主導、以回呼驅動」的被動式 Player，重構為「由 Player 主導、持續思考」的主動式架構。原始設計中，GameHost 以 StartGuess 與 GuessNext 不斷驅動 Player，導致 Player 的解題策略被拆散在多個回呼之中。以 DummyPlayer 為例，每次呼叫只隨機回傳一組數字，看似簡單，卻暴露了被動模式的缺點：若要加入分階段策略，只能以龐大的 switch 與實例狀態記錄上一次進度，程式閱讀與維護不易。

為改善此問題，作者引入 AsyncPlayer，讓 Player 在自己的執行緒中執行 Init 與 Think，將解題邏輯寫成自然的連續流程：用 while 迴圈推進階段，於需要時呼叫 GameHost_AskQuestion 取得提示，直到猜中或終止。這種轉換的關鍵在於「互相等待的兩個執行緒」：GameHost 一側仍使用 StartGuess/GuessNext/Stop，不需理解內部變化；Player 一側透過 AutoResetEvent 與暫存欄位，實作雙向的同步與資料交握。具體而言，StartGuess 啟動 ThinkCaller 執行緒後，等待 _host_return 被喚醒以取得首次猜測；Think 端在 GameHost_AskQuestion 中設定 _temp_number 並 Set _host_return，然後 Wait _host_call，待 GameHost 透過 GuessNext 回寫 _temp_hint 後續再繼續推進。Stop 則以特定 Hint 觸發收尾，並以 _host_end 確保背景執行緒妥善結束。

此設計使 Player 的策略表達變得直觀：多階段推理不必分割在多個回呼中，也不需大量狀態復原；而資料同步則被封裝於 AsyncPlayer，避免 GameHost 與 Player 相互耦合。作者並以時序圖說明雙向喚醒的順序與等待點，強調「若一方動作較快，會在等待點暫停，直到另一方進度跟上」，從而保證資料交握一致性。雖然此做法因同步開銷導致示例效能落後單純隨機的 DummyPlayer，但設計層面大幅簡化複雜問題的表達與維護，對處理需要多步推理與適時互動的情境更具可讀性與可擴充性。文章最後以輕鬆口吻總結：能先把問題簡化，才有餘裕解決複雜挑戰；而多執行緒的價值，常在於用正確的同步模型把複雜度收斂到可掌握的範圍內。

## 段落重點
### 前言與上下文
作者承接前一篇關於執行緒同步的概念文，回應讀者希望看到程式碼的期待，並以黑暗大魔王 GameHost 的題目為例，說明整體呼叫流程如何運作。本文目標是從「勞工 Player」的角度重新思考實作，展示如何把被動式回呼改造成主動式思考，使邏輯更貼近人類解題的自然流程。

### GameHost 呼叫 Player 的片段
GameHost 以老闆角色驅動 Player：先呼叫 StartGuess 取得第一個猜測，接著在 while 迴圈中以 GuessNext 持續要求下一個猜測，直到答案 A 命中所有位數後才呼叫 Stop。此設計對 GameHost 友善，但對 Player 而言，解題策略被切割到不同回合中，必須配合主控流程回應。

### Player 實作的範例 (DummyPlayer)
DummyPlayer 展示最簡單的被動實作：StartGuess 與 GuessNext 每次都隨機產生不重複數字作答。雖然程式短小易懂，但一旦要加入階段性策略，必須在 GuessNext 中以狀態變數與多分支控制進行「拼接式」邏輯。由於呼叫節奏由 GameHost 掌控，Player 只能被動回應，導致策略表達分散且脈絡不連續，閱讀與維護成本高。

### 換 PLAYER 的角度思考的邏輯: AsyncDummyPlayer
AsyncDummyPlayer 採主動式模型：Init 負責準備資源，Think 以無窮迴圈驅動解題，每輪先產生猜測，接著呼叫 GameHost_AskQuestion 取得提示，若 A 等於位數即結束。這讓「何時猜、怎麼猜、何時詢問提示」都集中在 Player 自身流程中，能自然表達多階段策略，不需把上下文拆散到多個回呼點。邏輯清晰，與人類思考相近。

### 被動 vs 主動的差異與隱喻
作者以勞工與老闆的隱喻強調差異：被動勞工每次只做被指派的一步，還得用筆記記住上次做到哪；主動勞工接下任務後自我驅動、需要資源時主動請求協助。對應到程式上，DummyPlayer 被呼叫驅動且需大量狀態管理；AsyncDummyPlayer 則由自身流程推進，GameHost 只在問答交握時提供必要資訊，降低耦合與心智負擔。

### 類別關係與關鍵類別 AsyncPlayer
圖示說明 AsyncPlayer 為架構轉換的關鍵：它維持 Player 的既有介面，內部以執行緒與同步原語橋接兩種呼叫模式。GameHost 毫無感知地使用同樣的 StartGuess/GuessNext/Stop；Player 子類別專注於 Init/Think 的策略邏輯；資料交換與同步細節則集中在 AsyncPlayer 封裝，形成清晰的職責切分。

### AsyncPlayer 實作: 化被動為主動
AsyncPlayer 以三個 AutoResetEvent 管理同步：_host_return 負責通知主控「猜測已備妥」、_host_call 負責通知 Player「提示已回來」、_host_end 用於終止協調。還有暫存欄位 _temp_number/_temp_hint 作為交握緩衝。ThinkCaller 包裝 Init 與 Think，並在例外時確保正確收尾。此層將同步複雜度隱藏，讓子類專注策略。

### StartGuess(...) 的時序與行為
StartGuess 啟動 ThinkCaller 新執行緒後，立即等待 _host_return。當 Player 端首次提出猜測並 Set _host_return，GameHost 得以從 _temp_number 取得結果返回。如此保證 GameHost 與 Player 的首次交握順序正確，即使一方較快，另一方仍能在等待點準確對齊，避免錯位與資料競爭。

### GameHost_AskQuestion(...) 的時序與行為
GameHost_AskQuestion 由 Player 執行緒呼叫：寫入 _temp_number，Set _host_return 喚醒主控取得猜測，接著 Wait _host_call 等待提示，最後回傳 _temp_hint。以 lock 確保交握區的線程安全，finally 區塊清理暫存，避免殘留狀態污染後續回合。Stop 流程亦以相同機制對齊結束時點。

### 結語與設計思考
作者指出此同步模型在示例中效能不如單純隨機解（約慢四到五倍），但換來策略表達的清晰性與可維護性，對於需要多步推理與階段性決策的情景更具價值。多執行緒的妙處在於用正確的等待與喚醒點把複雜互動轉為可控的順序，先讓問題變簡單，才更容易正確、穩定地解決複雜需求。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- C# 基礎與物件導向（繼承、抽象類別、polymorphism）
- .NET 多執行緒基礎（Thread、委派、例外處理）
- 同步原語（AutoResetEvent、WaitHandle、lock）
- 基本同步模式概念（請求/回應握手、producer–consumer、狀態機 vs 迴圈邏輯）

2. 核心概念：本文的 3-5 個核心概念及其關係
- 被動式呼叫流 vs 主動式工作流：由 GameHost 主導的多型呼叫（StartGuess/GuessNext/Stop）轉為 Player 主導的 Think 迴圈
- 執行緒間握手同步：以 AutoResetEvent 實作「呼叫/回傳」雙向等待（_host_call、_host_return）
- 共享狀態的受控交換：以暫存欄位（_temp_number/_temp_hint）與 lock 區段配合事件進行資料交接
- 執行緒生命週期管理：ThinkCaller 啟動背景執行緒、Stop 結束、_host_end 收斂
- 設計封裝：AsyncPlayer 將同步細節封裝，讓衍生類別只關注 Init/Think 的「如何猜」策略

3. 技術依賴：相關技術之間的依賴關係
- Player 抽象介面 ←(繼承)– AsyncPlayer（封裝同步） ←(覆寫)– AsyncDummyPlayer（策略實作）
- Thread 啟動 ThinkCaller → 在 Think 中呼叫 GameHost_AskQuestion → 透過 AutoResetEvent/lock 與 GameHost 的 StartGuess/GuessNext/Stop 做雙向同步
- AutoResetEvent WaitOne/Set 與 lock 配合，確保資料交接的原子性與執行緒順序

4. 應用場景：適用於哪些實際場景？
- 將「回呼驅動、分段回合式」流程改造成「背景主動運算、必要時互動」的模式
- 互動式演算法（反覆詢問外部系統獲得提示/回饋）例如搜尋/推理/規劃
- 以封裝好的同步模板，簡化複雜協作流程（避免在外層堆疊大量狀態機或 switch-case）
- 需要清晰邏輯的背景任務，偶爾與主執行緒交換資料的場景

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 先理解 GameHost 與 Player 的多型呼叫介面（StartGuess/GuessNext/Stop）
- 學會 Thread 基本用法與 AutoResetEvent 的 WaitOne/Set 行為
- 觀察 DummyPlayer 的被動式流程，對照 AsyncDummyPlayer 的主動式 Think 迴圈

2. 進階者路徑：已有基礎如何深化？
- 研讀 AsyncPlayer 的封裝：事件、lock、暫存欄位如何配合達成雙向同步
- 分析握手時序圖，驗證在不同呼叫順序下不會死鎖或遺失訊號
- 思考如何在 Think 中拆分多階段策略，避免外部狀態機

3. 實戰路徑：如何應用到實際專案？
- 將現有回呼式或輪詢式流程重構為「主動工作者 + 問答握手」模板
- 抽象出 Init/Think 讓業務邏輯聚焦，將同步細節收斂在基底類別
- 增加取消/逾時機制、資源釋放（CancellationToken、using/Dispose）以提升穩健性

### 關鍵要點清單
- 被動式 vs 主動式控制流轉換: 用背景執行緒與握手同步，讓工作者主導流程而非被呼叫驅動 (優先級: 高)
- AsyncPlayer 模式: 以抽象類別封裝同步細節，衍生類只需實作 Init/Think (優先級: 高)
- 雙向握手機制: _host_call 與 _host_return 以 AutoResetEvent 實現請求/回應同步 (優先級: 高)
- GameHost_AskQuestion 契約: 在 Think 中以此方法向主機提問並等待回覆 (優先級: 高)
- 暫存變數交接: _temp_number/_temp_hint 作為資料交換的共享區，配合事件與 lock 使用 (優先級: 高)
- lock 的必要性: 確保交接期間的原子性，避免競態條件與交錯讀寫 (優先級: 高)
- 執行緒生命週期: ThinkCaller 啟動、Stop 發送終止訊號、_host_end 收斂結束 (優先級: 中)
- 完成旗標 _host_complete: 防止在已停止狀態下繼續互動（拋出例外）(優先級: 中)
- try/finally 清理: 問答後重設暫存欄位，確保狀態一致性與記憶體安全 (優先級: 中)
- 時序一致性: 以事件順序保證先後步驟，避免先到先服務造成的邏輯錯位 (優先級: 高)
- 例外處理策略: ThinkCaller 捕捉並記錄例外，確保 _host_end 仍會被 Set (優先級: 中)
- 效能取捨: 同步開銷使 Async 版本可能慢於被動版本，但換得更清晰的邏輯 (優先級: 中)
- 可測性與可維護性: 主動式迴圈讓演算法分段清楚，降低外部狀態機複雜度 (優先級: 中)
- API 正確用法: Thread.Start、AutoResetEvent.WaitOne/Set、lock 範圍設計 (優先級: 高)
- 可擴充考量: 可加入取消/逾時（如 CancellationToken、WaitHandle.WaitAny）與資源釋放 (優先級: 低)