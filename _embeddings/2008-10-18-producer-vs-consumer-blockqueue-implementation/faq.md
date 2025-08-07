# 生產者 vs 消費者 - BlockQueue 實作

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是「生產者/消費者」(Producer-Consumer) 模式？何時適合採用這種設計？
生產者/消費者模式是一種將工作流程區分為兩大階段 (生產與消費) 的併行處理策略。  
當第一階段 (例如：下載、載入、初步運算) 與第二階段 (例如：壓縮、格式轉換、後續運算) 都各自適合用多執行緒加速，且兩階段需要透過共享資料進行銜接時，就很適合使用此模式。藉由在兩階段之間插入一個受控的佇列，可以同時平衡兩端速度，又能避免資源競爭。  

## Q: 為什麼內建的 Queue 不足以支援生產者/消費者模式？BlockQueue 解決了哪些問題？
標準 Queue 在「滿佇列」或「佇列為空」時只會拋出例外，無法讓執行緒自動等待；當生產者與消費者速度不一致時，程式就必須自行處理同步與例外。  
BlockQueue 針對此痛點做了三項改進：  
1. 可設定容量上限，若佇列已滿，EnQueue 會被「阻塞」而非拋例外。  
2. 若佇列為空，DeQueue 會被「阻塞」而非拋例外。  
3. 提供 Shutdown()，讓生產端結束後能通知消費端停止等待，避免「苦等」的窘境。  

## Q: BlockQueue 在佇列滿或空時，是如何讓執行緒暫停再繼續的？
BlockQueue 透過兩個 ManualResetEvent 物件來同步：  
• 佇列滿時，EnQueue 會呼叫 enqueue_wait.WaitOne() 進入等待；直到消費者取走資料後，由 DeQueue 觸發 enqueue_wait.Set() 喚醒生產者。  
• 佇列空時，DeQueue 會呼叫 dequeue_wait.WaitOne() 進入等待；當生產者放入新資料後，EnQueue 會觸發 dequeue_wait.Set() 喚醒消費者。  
這種設計讓阻塞行為取代例外拋出，並可自然地平衡前後兩階段的速度。