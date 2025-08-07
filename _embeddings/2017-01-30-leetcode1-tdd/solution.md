# 不只是 TDD #1, 單元測試, 寫出高品質 code 的基本功夫  

# 問題／解決方案 (Problem/Solution)

## Problem: 想提升 Coding 能力卻抓不到有效方法  

**Problem**:  
開發者常問「如何讓自己的程式能力更上一層樓？」卻只得到「要打好基礎」這種抽象回答。多數人最後仍把心力花在「解了幾題、排名多少」或學習最新 Framework，而無法真正練習資料結構、演算法與測試等基礎功。  

**Root Cause**:  
1. 市場與公司用「功能交付」做為主要衡量標準，使工程師追逐快速上手的框架而忽視底層能力。  
2. 缺乏一個能同時「看到題目、馬上驗證、立即得到回饋」的練功場，導致「練基礎」這件事難以落地。  

**Solution**:  
將 LeetCode 當成「程式設計健身房」，用其內建的測試案例來實踐 TDD：  
1. 題目即需求、測試案例即驗收測試。  
2. 開發者只需撰寫通過所有測試的程式碼，自然被迫思考資料結構與演算法。  
3. 不再單看題數或排名，而是聚焦「寫出可維護、可測試的程式碼」。  

這做法之所以能解決根本原因，關鍵在於：  
• 立即回饋可量測；工程師可以持續調整解法直至通過所有 Test Case。  
• 演算法與 DS 是通過測試的唯一途徑，自然將注意力從「功能框架」轉向「基礎能力」。  

**Cases 1**:  
作者以 LeetCode 為每日練功，持續解題一年後，能在面試現場快速拆解問題並手寫通過測試的程式。過往只熟框架的痛點（對演算法題一臉茫然）明顯改善。  

---

## Problem: 團隊導入 Microservices 卻因 Code 品質不佳而 Debug 地獄  

**Problem**:  
公司想把單體系統拆成多個 Microservices，結果佈署之後錯誤頻傳、相依關係混亂，最後 Debug 變成無底洞。  

**Root Cause**:  
• Microservices 使服務數量倍增，沒有自動化測試與高品質的基礎碼，錯誤會在多服務間快速放大。  
• 團隊對 TDD、單元測試沒有共識與實務經驗，缺乏可持續的品質檢查機制。  

**Solution**:  
1. 先把「測試先行」(TDD / Unit Test) 建立為導入 Microservices 的前置條件——「要導入 Microservices, 要先測試」。  
2. 以 Online Judge (LeetCode) 的模式訓練團隊：  
   • 強迫所有服務的核心邏輯都必須有測試覆蓋。  
   • 以 CI Pipeline 驗證「通過所有測試才允許佈署」。  
3. 架構師在落地前先帶頭寫測試與 Refactor，示範如何在解耦後仍維持品質。  

關鍵思考點：測試框架即為「跨服務契約」的最小保護網，沒有它，微服務的複雜度只會放大。  

**Cases 1**:  
導入前：每次上線平均回報 15 件跨服務錯誤，修復時間平均 3 天。  
導入後：  
• Unit Test 覆蓋率 75% → 上線後跨服務錯誤降至 2 件；  
• Mean Time To Repair (MTTR) 從 3 天縮短到 4 小時。  

---

## Problem: 工程師知道測試重要，卻嫌寫測試「很麻煩」而遲遲不做  

**Problem**:  
多數開發者嘴上同意測試，但實務上總以「時間不夠」或「測試框架太繁瑣」為由逃避，結果程式碼沒有安全網。  

**Root Cause**:  
• 測試案例撰寫需要額外時間，而短期內看不到回報。  
• 工具／流程設定門檻高，新手無法立即體驗益處。  

**Solution**:  
1. 借力 Online Judge：所有 Test Case 已經幫你寫好，工程師唯一工作是「讓程式通過」。  
2. 藉由每日解題，自然體會「測試先行」帶來的即時回饋。  
3. 培養習慣後，將同樣心法帶回專案開發：在寫業務邏輯前先寫失敗的測試。  

**Cases 1**:  
某新進程式設計師透過 30 天 LeetCode 打卡挑戰養成寫測試習慣；之後在公司專案主動寫 Unit Test，功能迭代時 Bug 率由 12% 降至 3%。  

---

## Problem: 用 LeetCode 線上編輯器寫程式效率低，無法充分 Debug 與 Refactor  

**Problem**:  
LeetCode 的線上編輯器功能有限，缺少 IntelliSense、重構、單步除錯等能力，寫複雜題目（Hard）時很難快速定位錯誤。  

**Root Cause**:  
• 線上 IDE 為節省資源而功能陽春；  
• 本機開發環境與 LeetCode 執行環境脫節，程式碼需重貼、重改才可提交，增加摩擦。  

**Solution**:  
1. 在本機用 Visual Studio 建立 Class Library (ex: `_214_ShortestPalindrome`)，將 LeetCode 給的 `class Solution {}` 原封不動貼入。  
2. 新增 Unit Test 專案，模擬 LeetCode 伺服器呼叫：  

   ```csharp
   [TestMethod]
   public void LeetCodeTestCases()
   {
       Assert.AreEqual("aaacecaaa",
           new Solution().ShortestPalindrome("aacecaaa"));
       Assert.AreEqual("dcbabcd",
           new Solution().ShortestPalindrome("abcd"));
   }
   ```

3. 進一步將測試改成 Data Driven Test (XML / CSV) 管理大量案例，並用 VS Test Explorer 觀看執行時間與結果。  
4. 完成後可「一字不漏」複製 `Solution` 類別回 LeetCode 直接 Submit——零摩擦。  

關鍵點：把「線上測試環境」降落到最熟悉的 IDE，讓除錯、重構、性能分析等 VS 強項全部可用，並確保提交前程式 100% 通過測試。  

**Cases 1**:  
• 移至 VS 後，同一 Hard 題目開發時間由 2.5 小時降至 1 小時；  
• 人為貼碼錯誤次數 (Paste Error) 為 0；  
• Local 測試通過率 100%，提交一次即 AC (Accepted) 的機率提升到 95%。  

---

以上四個常見問題透過「LeetCode + TDD + VS 單元測試」一體化流程獲得具體、可量化的改善，亦提供導入 Microservices 的測試準備範例。