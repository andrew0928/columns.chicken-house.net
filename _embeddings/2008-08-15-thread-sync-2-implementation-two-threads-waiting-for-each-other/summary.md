# Thread Sync #2. 實作篇─互相等待的兩個執行緒

## 摘要提示
- 同步模型: 文章以猜數字遊戲為例，說明 GameHost 與 Player 之間的同步呼叫模式與問題。  
- DummyPlayer: 示範傳統「被動式」Player 實作，必須依賴 GameHost 逐步驅動。  
- 主動思考: 改寫為 AsyncDummyPlayer，讓 Player 自行開執行緒、主動控制解題流程。  
- AsyncPlayer 抽象層: 引入 AsyncPlayer 基底類別，封裝被動/主動轉換與執行緒管理。  
- WaitHandle 機制: 利用 AutoResetEvent 實作兩執行緒互相等待與喚醒的同步機制。  
- StartGuess 流程: GameHost 呼叫 StartGuess 時建立 ThinkThread，並以 _host_return 等待結果。  
- GameHost_AskQuestion: Player 透過此方法將猜測送出並等待 GameHost 傳回 Hint。  
- GuessNext 與 Stop: 反向同步流程與結束訊號，確保雙方資源安全釋放。  
- 效能比較: AsyncDummyPlayer 架構較優雅，但執行速度約為 DummyPlayer 的四分之一。  
- 心得反思: 作者強調「先簡化問題再解決」的重要性，並分享使用 Thread 帶來的成就感。  

## 全文重點
作者延續前一篇概念文，以「猜數字」比賽的程式碼作為範例，實際展示兩個執行緒（GameHost 與 Player）如何「互相等待」並同步溝通。首先回顧黑暗執行王提供的基礎範例：GameHost 採老闆角色，逐步呼叫 Player.StartGuess、Player.GuessNext、Player.Stop 來推動流程，而一般的 DummyPlayer 只能被動回應，每次被喚起都得靠成員變數與 switch 流程記住先前狀態，導致邏輯破碎且閱讀困難。

為了讓「勞工」(Player) 擁有主動權，作者改寫出 AsyncDummyPlayer，並新增基底類別 AsyncPlayer。AsyncPlayer 於 StartGuess 時自行啟動一條 ThinkThread，將真正的解題邏輯寫在 Think 方法內，以 while 迴圈持續猜測；當需要向 GameHost 詢問結果時，Player 直接呼叫 GameHost_AskQuestion，此方法透過 AutoResetEvent 與共享變數 _temp_number/_temp_hint 將資料安全交換，同時確保執行緒的先後順序符合需求。整個過程不再依賴龐大的 switch 或狀態機，而是讓開發者以最自然的程式流程描述「先做 A、再做 B、最後完成」的思考過程。

同步細節上，StartGuess 建立 ThinkThread 後即 WaitOne 等待 _host_return；Player Thread 準備好第一組猜測後 Set 該事件，喚醒 GameHost。往後每一次猜題都在 GuessNext 與 GameHost_AskQuestion 間重複「Set/Wait」鐵三角：Player 把數字放進 _temp_number → Set _host_return → Wait _host_call；GameHost 在 GuessNext 收到數字後計算 Hint → 放入 _temp_hint → Set _host_call。Stop 亦以相同手法結束。整體設計可無痛搬移到真實、較複雜的「分階段策略」Player 上，只需把思路寫在 Think 即可。

雖然多開一條執行緒與多次同步造成效能下降（作者實測慢 4~5 倍），但可讀性與維護性大幅提升，足以應付較具策略或 AI 性質的 Player。最後作者分享開發感想：透過 Thread 與同步原語將被動呼叫化為主動流程，能大幅簡化複雜度；他樂於用圖解與比喻呈現概念，雖然程式碼不多、圖文甚多，但目的在於讓讀者抓到精隨，期許大家在面對多執行緒時，也能先把問題拆小、再用正確工具解決。

## 段落重點
### 引言與上篇回顧  
作者回顧前篇僅談概念與時序圖，受到讀者反映「太深奧」，故本篇改以完整程式碼示範；並以黑暗魔人賽的猜數字範例，說明多執行緒同步實戰需求。

### GameHost 呼叫 Player 片段解析  
GameHost 站在「老闆」角度：先呼叫 StartGuess 取得首猜，再不斷呼叫 GuessNext 直到答對後才 Stop。此結構讓 Player 完全被動、邏輯被拆成數段。

### DummyPlayer 實作與被動缺陷  
DummyPlayer 實例展示被動寫法：StartGuess 與 GuessNext 均亂數猜，雖邏輯簡單卻因被迫配合 GameHost 流程而導致程式分割、不易閱讀且須靠成員變數維持狀態。

### AsyncDummyPlayer 主動模型  
作者提出「若勞工成老闆」的觀點，改寫為 AsyncDummyPlayer：重心轉到 Think 方法，Player 透過自有迴圈掌控流程，只在需要 Hint 時主動呼叫 GameHost_AskQuestion，邏輯一氣呵成。

### AsyncPlayer 類別—轉換核心  
AsyncPlayer 封裝被動/主動的轉換：  
1. StartGuess 建立 ThinkThread、等待 _host_return。  
2. GuessNext 透過共享變數與 AutoResetEvent 把 Hint 傳回 Player Thread。  
3. Stop 送出結束訊號並等待 ThinkThread 收尾。  
同時定義 Init 與 Think 為抽象方法，留給子類實作。

### StartGuess→ThinkCaller 流程  
GameHost 呼叫 StartGuess 時，ThinkThread 立即執行 ThinkCaller：先跑 Init 做準備，再進入 Think 進行真正的猜數字迴圈。完成第一筆猜測後 Set _host_return 喚醒 GameHost，完成首輪同步。

### GameHost_AskQuestion 同步細節  
GameHost_AskQuestion 以 lock 保護共享區域：先寫入 _temp_number、Set _host_return 喚醒 GameHost，再 WaitOne 等待 _host_call；GameHost 計算 Hint 後寫入 _temp_hint、Set _host_call，喚醒 Player 取回資料，達成雙向同步。

### 結尾心得與效能比較  
作者自嘲圖文多於程式碼，但強調 Thread 模式能優雅簡化複雜問題。雖然 AsyncDummyPlayer 效能落後，但其可讀性與可維護性足以在更複雜場景中發揮價值；最後鼓勵讀者先拆解問題，再選擇合適的同步工具。