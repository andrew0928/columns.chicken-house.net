```markdown
# [架構師的修練] - 從 DateTime 的 Mock 技巧談 PoC 的應用

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在單元測試或 PoC 中直接使用 `DateTime.Now` 會遇到什麼問題？
`DateTime.Now` 是 `System.DateTime` 的 static property，呼叫時會直接回傳系統目前時間，開發者既無法透過 DI 或 wrapper 注入替代實作，也無法預測執行當下的時間值，因此測試結果難以重現與驗證。

## Q: Mock `DateTime.Now` 常見的做法有哪些？
1. 自行撰寫替代類別（例如 `SystemTime.Now`）  
2. 以 Interface（如 `IDateTimeProvider`）包裝日期時間邏輯後注入  
3. 使用 Microsoft Fakes 在 runtime 攔截呼叫  
4. Ambient Context 作法 (或將 DateTime 當成類別屬性)  
前三項是網路上最常見的分類，第四項可視為對前兩項的封裝技巧。

## Q: 為什麼作者沒有採用 Microsoft Fakes？
雖然 Microsoft Fakes 不必改動原始碼，但它需 Visual Studio Enterprise 版、影響效能且侷限於 Unit Test。對作者同時要做 PoC、Demo 的需求而言不夠俐落。

## Q: 作者最終採用的解決方案是什麼？
作者自製了 `DateTimeUtil`（屬於 “Ambient Context” 策略的變形），以 Singleton 方式提供 Instance，可  
• 透過 `Init()` 把「現在」固定在可控制的時間點  
• `Now` 屬性會跟著實際時間流動（保持 offset）  
• 以 `TimePass` / `GoNextHours` / `GoNextDays` 進行「時光快轉」  
• 當時間跨越日期時觸發 `RaiseDayPassEvent`，方便驗證排程或定期任務

## Q: `DateTimeUtil` 如何維持時間流動並偵測跨日事件？
內部保存兩個欄位：  
1. `_realtime_offset`：啟動時計算的期望時間減去真實系統時間的差值  
2. `_last_check_event_time`：最後一次檢查跨日的時間點  
每次讀取 `Now` 或執行 `TimePass` 都呼叫 `Seek_LastEventCheckTime`，比對是否跨越 00:00:00；若跨越則逐日發出 `RaiseDayPassEvent`。

## Q: 使用 `DateTimeUtil` 的基本步驟是什麼？
1. 在程式進入點呼叫 `DateTimeUtil.Init(期望啟動時間)`  
2. 以 `DateTimeUtil.Instance.Now` 取代 `DateTime.Now`  
3. 若需模擬時間推進，呼叫 `TimePass`、`GoNextHours`、`GoNextDays`  
4. 如需偵測跨日，對 `RaiseDayPassEvent +=` 加掛處理函式

## Q: 難道每次要展示月底或定時流程都要真的等到那個時間嗎？
不用。借助 `DateTimeUtil` 的 `TimePass` / `GoNext…` 方法，可瞬間把系統時間快轉到指定時刻，甚至在 UI 上放按鈕就能操作，避免等待或手動調整系統時鐘。

## Q: `DateTimeUtil` 除了單元測試還能帶來什麼價值？
它解決了與「時間」有關的可控性後，非常適合 Proof of Concept (PoC) 階段：  
• 可快速驗證涉及定時任務或時間序列的設計  
• Demo 或溝通時可視化時間流動，降低抽象概念的理解難度  
• 配合「降維打擊」思維，先在單機驗證核心概念再推回真實環境

## Q: 什麼是作者口中的「降維打擊」PoC 作法？
把原需分散式、跨機或大量基礎建設的複雜情境，先降一個維度到同一 Process / Thread / 語言特性（如 event、Linq）來驗證關鍵概念 (Concept)。概念成立後再回推至真實環境，可大幅降低思考與實作成本。
```