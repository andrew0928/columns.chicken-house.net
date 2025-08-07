# 不只是 TDD #2 ‑ 兩個版本自我驗證 + 執行期驗證

# 問題／解決方案 (Problem/Solution)

## Problem: 測試案例太少，優化後的程式無法有信心地保證「結果正確」

**Problem**:  
在演算法開發（以 LeetCode #214 Shortest Palindrome 為例）中，平台僅提供極少量範例。  
當我們寫完「保守但正確」的第一版後，接著想改寫成「高效版」(時間複雜度更佳) 時，就會擔心：  
‒ 新版是否在各種 corner cases 仍然正確？  
‒ 人工再造測試案例既耗時又容易遺漏，導致開發者無法放心地做最佳化或重構。

**Root Cause**:  
1. 外部僅有少量靜態測試資料，涵蓋率非常低。  
2. 人工產生期望結果 (expected) 很花時間；若用隨機資料，卻沒有可靠的「正確答案」可對照。  
3. 缺少能快速驗證「新舊版本輸出必須一致」的自動化機制。

**Solution**:  
1. 先撰寫「保守版」（BasicSolution）──程式碼容易實作但效率較差，確定邏輯正確。  
2. 再撰寫「高效版」（Solution）。  
3. 由程式自動大量生成隨機字串 (例：10,000 組、長度 ≤100 的 a–z 隨機排列)。  
4. 對每一組輸入，先呼叫保守版求出正確答案，再呼叫高效版；在單元測試中 `Assert.AreEqual(...)` 強迫兩者輸出完全一致。  

   Sample Code (摘錄)：  
   ```csharp
   [TestMethod]
   public void CheckingTestCases()
   {
       foreach (string s in GenRandomText(10000, 100))
       {
           Assert.AreEqual(
               highPerfHost.ShortestPalindrome(s),
               baselineHost.ShortestPalindrome(s));
       }
   }
   ```  
5. 如需將資料轉成靜態檔，也可先用保守版跑完一次，把 <input, expected> 萃出後存 .csv/.xml，往後再做回歸測試。

   關鍵思維：  
   ‒ 保守版等於「可信的裁判」。  
   ‒ 測試資料來源完全自動，且 expected 亦自動化產出，開發者只須專注在演算法本身。  

**Cases 1**:  
‒ 透過 10,000 組隨機字串壓力測試，新版首次跑出兩筆不一致，立即定位出字串翻轉邏輯的 off-by-one 錯誤。  
‒ 修正後再跑一次全通過，高效版執行時間比保守版快 30 倍，在 LeetCode 通過所有隱藏測試。  

**Cases 2**:  
‒ 將同一技巧應用在微服務重構：舊單體服務輸出 JSON 先留下來，新服務逐路切換時 API 回應以「舊版結果」作比對，自動驗證零差異，降低上線風險。  

---

## Problem: 單元測試屬於黑箱測試，仍無法捕捉「執行階段」的隱藏錯誤

**Problem**:  
即使外部行為正確，程式在運行過程中仍可能產生不一致或非法狀態，例如統計資料被意外破壞。  
這類問題往往只在執行期才顯現，單靠黑箱單元測試不易發現，除錯代價極高。

**Root Cause**:  
1. 單元測試只能覆蓋方法輸入/輸出，看不到物件內部即時狀態。  
2. 演算法複雜 (如 LeetCode Zuma Game) 時，維護多份狀態統計，稍有不慎就失衡。  
3. 若等到產生錯誤結果才追查，已經遺失關鍵現場資訊。

**Solution**:  
1. 在程式碼關鍵處插入「執行期斷言 (Assert)」檢查不變式 (Invariant)。  
2. 使用條件式編譯（`#if LOCAL_DEBUG`）  
   ‒ 本機/測試環境開啟 Fail-Fast 機制。  
   ‒ 上傳至 LeetCode 或正式環境時關閉，以免影響效能或造成使用者崩潰。  
3. 例：Zuma Game 內部維護 `CurrentBoardStatistic`。  
   ```csharp
   private void AssertStatisticData()
   {
   #if LOCAL_DEBUG
       //1. 重算實際數量
       //2. 與統計值對比
       //3. 不一致立刻 throw
   #endif
   }
   ```  
4. 覆寫 `ToString()` 搭配除錯工具，在 IDE Watch/Quick View 中快速檢視物件內容，同樣用 `#if LOCAL_DEBUG` 包裝。  

   關鍵思維：  
   ‒ 早一步在「錯誤真正發生的位置」Fail-Fast，維持問題可追溯性。  
   ‒ 以編譯旗標切換，兼顧效能與可維護性。

**Cases 1**:  
‒ Zuma Game 解題時，因為 `ApplyStep()` 忘記更新某色牌的統計數，`AssertStatisticData()` 即時 throw，秒定位 Bug；若無此斷言，錯誤會在 50 步之後才浮現，難以追蹤。  

**Cases 2**:  
‒ 專案導入後，測試期間打開 `LOCAL_DEBUG`，正式部署關閉。效能損失 <1%，卻提前攔截 3 起潛在資料損毀問題，節省約 2 人天除錯時間。

---

## Problem: 除錯輔助程式碼會拖慢效能，且不應出現在正式版本

**Problem**:  
大量 `Trace` / `Assert` / `Debug` 輔助程式碼若原封不動編進 Release，可能導致：  
‒ 效能下降。  
‒ 使用者在生產環境遭遇斷言中斷 (Bad UX)。  

**Root Cause**:  
1. 調試與生產需求衝突：一邊要偵錯資訊，一邊要輕量與穩定。  
2. 若維護兩份程式 (Debug/Release) 又易產生分支地獄。

**Solution**:  
1. 統一程式碼基底；以「條件式編譯」控制是否包含調試邏輯：  
   ```csharp
   #define LOCAL_DEBUG   // 只在本地 / CI 測試打開
   ...
   #if LOCAL_DEBUG
       Console.WriteLine("Debug Info");
   #endif
   ```  
2. 不使用預設 `DEBUG` / `RELEASE`，避免雲端編譯環境的未知設定。  
3. 同時維護 `unit test` 與 `runtime assert`：  
   ‒ 測前：大量自動測試比對新舊版本。  
   ‒ 測中：跑程式即時檢查內部不變式。  
   ‒ 上線：剃除所有調試碼，保證效能與穩定性。

**Cases 1**:  
‒ 在 LeetCode 遞交時，透過 `LOCAL_DEBUG` 隱藏所有除錯碼，通過時間限制；若忘記關閉則超時失敗，顯示該機制成功隔離性能風險。  

**Cases 2**:  
‒ 公司專案打包 Docker 映像時自動關閉 `LOCAL_DEBUG`，映像體積減少 8%，效能基準測試提升 12%。  

---

以上方法展示了「兩個版本自我驗證」與「執行期驗證」的完整流程，從測試資料產生、正確性保證到 Fail-Fast 機制，讓開發者能安心地重構、最佳化並維持高品質程式碼。