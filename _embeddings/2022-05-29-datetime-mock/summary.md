```markdown
# [架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用

## 摘要提示
- DateTime.Now Mock: 靜態屬性難以注入，須以替代方案提高測試可控性。  
- C#技術: 透過自製 DateTimeUtil 單例類別統一取得「現在」時間。  
- Ambient Context: 採用 Ambient Context Approach，避免大量 DI 侵入並保留擴充彈性。  
- TimePass & Event: 提供 TimePass 快轉與 RaiseDayPassEvent 事件，模擬時間流逝與跨日動作。  
- Unit Test: 範例測試 TimePass、事件觸發與實際時間推進場景，兼顧誤差容忍。  
- PoC需求: 可在 Demo 或 Prototype 中自由操控時序，不必修改系統時鐘或等待真實時間。  
- 降維打擊: 以「降維」方式簡化分散式情境，專注驗證核心概念與演算法。  
- Microsoft Fakes: 雖可攔截靜態呼叫但需 Enterprise 版且有效能負擔，不符 PoC 彈性。  
- Interface設計: 以 offset 紀錄真實時間差並在 Now 計算，兼顧流動性與可快轉性。  
- 用例應用: 在原型 UI 嵌入時光控制按鈕，提升跨日排程與流程展示的說明效率。

## 全文重點
作者以常見的「DateTime.Now 無法預期」問題切入，說明單元測試及 Proof of Concept 開發時若直接呼叫靜態 DateTime.Now，將導致測試不穩定、無法快轉以及 Demo 時間受制於真實時鐘。市面上常見做法包含自訂靜態替代品、介面抽換與 Microsoft Fakes 等；其中 Fakes 能零修改攔截但需 Enterprise 版且僅適用測試，無法滿足作者 PoC 情境。  
因此作者自行實作 DateTimeUtil 類別，採 Singleton + Ambient Context 思想：  
1. Init 指定啟動基準時間、Reset 重新初始化。  
2. Now 屬性回傳「基準時間 + offset」，隨真實時間流動；TimePass/GoNext* 方法則在不等待的情況下快轉指定時間。  
3. 透過 RaiseDayPassEvent 於每次跨過午夜時自動觸發，方便模擬排程或報表等日界事件。  
內部僅紀錄 offset 與上次檢查時間，呼叫 Now 或 TimePass 時再比對並補發遺漏事件。  
作者以三組單元測試驗證：  
‧TimePassTest 檢查快轉後 Now 是否正確；  
‧TimePassWithEventTest 驗證快轉跨日時事件觸發次數；  
‧RealtimeEventTest 驗證在真實時間流逝及讀取 Now 時事件能正確補發。  
最後，作者闡述自己在大型微服務設計時常以 PoC「降維打擊」：將跨機器通訊降至執行緒、將 Message Bus 降至 C# event、將資料庫查詢降至 Linq 等方式，快速驗證核心概念而不受基礎設施束縛；DateTimeUtil 便是其中一個輔助時序驗證的小工具。文章並列出多篇相關 API、基礎建設及演算法舊文，鼓勵讀者以同樣思維檢視並練習。

## 段落重點
### 前言：DateTime.Now 的問題
DateTime.Now 為 static 屬性，無法以傳統 DI 或 wrapper 注入替換，導致單元測試與 Demo 难以控制時間；Google 可找到三種主流解法，自製靜態替代品、介面抽換與 Microsoft Fakes，後者雖免改程式碼但需 VS Enterprise 且效能受限，不利 PoC；作者因此尋求同時兼具「可控」「流動」「支援排程事件」的新方案。

### 設計：DateTimeUtil 介面定義
DateTimeUtil 採 Singleton，提供 Init/Reset 管理生命週期，Now 讀取當前時間，TimePass、GoNextHours/Days 快轉時光並維持流動性；另定義 RaiseDayPassEvent 與 TimePassEventArgs，於跨日時通知系統任務，並利用 offset 計算真實與虛擬時間差，不直接凍結時間，以滿足 PoC 需在展示中看見時間前進的需求。

### 實作：Code Review
核心實作僅數十行：使用 _realtime_offset 儲存差值、_last_check_event_time 追蹤上次事件檢查點；Now 及 TimePass 都呼叫 Seek_LastEventCheckTime，在迴圈中補發跨日事件；TimePass 只允許正向跳躍，若需倒退須 Reset；此策略避免背景執行緒複雜度，並容許事件觸發有微小延遲，足敷測試與原型之用。

### 使用情境
作者撰寫三組單元測試驗證功能：1) TimePassTest 檢驗 Init 後多次快轉與 Thread.Sleep 對 Now 的影響，允許 1 秒誤差；2) TimePassWithEventTest 透過快轉 35 天 15 小時，確認跨日事件觸發 36 次；3) RealtimeEventTest 於接近午夜時睡眠與讀取 Now，比對事件補發邏輯。實務上只需在程式啟動呼叫 Init，再以 += 訂閱事件即可於 UI、排程或 Log 中使用。

### 延伸思考：PoC 的應用
作者說明 PoC 重要性及「降維打擊」手法：將分散式、跨機器、資料庫與訊息匯流排等高維度問題化約至單機 thread、Linq、C# event 等低維表徵，以加速概念驗證；DateTimeUtil 讓時間相關流程也能降維處理。最後列出多篇舊文示範相同思維，如 API 設計、負載控制、排隊、RPC、Process Pool 與演算法題，強調累積理論與工具可大幅提升系統架構設計效率。
```
