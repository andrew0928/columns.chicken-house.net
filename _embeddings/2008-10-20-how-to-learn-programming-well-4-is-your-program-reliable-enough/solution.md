# 該如何學好「寫程式」#4 ─ 你的程式夠「可靠」嗎？

# 問題／解決方案 (Problem/Solution)

## Problem: 線上測驗計分錯誤，導致分數高低不準

**Problem**:  
在開發線上測驗系統時，第一版 `ComputeQuizScore` / `ComputeQuestionScore` 只用「天才滿分答案卷」做測試，結果遇到「部分作答」或「全答錯」時出現 1. 不該得分卻加分、2. 負分無下限 等問題，最終讓考生拿到錯誤分數。

**Root Cause**:  
1. 僅以單一 Happy Path 測試（全對答案卷）。  
2. 缺少對「未作答」「選項數不符」「負分下限」等異常情境的防禦性驗證。  
3. 缺少能在開發階段即暴露錯誤狀態的機制。

**Solution**:  
1. 在所有「假設必須成立」的地方插入 `Trace.Assert(...)`：  
   • 題目與答案卷皆存在。  
   • 題目與答案卷的選項數量一致。  
   • 最終分數不得低於零、不得高於題目配分。  
2. 使用 `System.Diagnostics.Trace` / `Debug` 讓這些 Assert 僅在 DEBUG 組態啟動，RELEASE 組態完全不影響效能。  
3. 透過多份測試答案卷（全對、只答一題、全錯）驗證 Assert 可即時偵測異常，並將演算法修正為：  
   • 放棄題目（未作答）不加也不扣。  
   • 倒扣到零為止（負分下限）。  
4. 如下精簡版核心程式碼：  
```csharp
public static int ComputeQuizScore(XmlDocument quizDoc, XmlDocument paperDoc)
{
    Trace.Assert(quizDoc != null);
    Trace.Assert(paperDoc != null);
    Trace.Assert(quizDoc.SelectNodes("/quiz/question").Count ==
                 paperDoc.SelectNodes("/quiz/question").Count);

    int total = 0;
    foreach (var (q,p) in quizDoc.ZipQuestionsWith(paperDoc))
        total += ComputeQuestionScore(q,p);

    total = Math.Max(0, total);
    Trace.Assert(total >= 0);
    return total;
}
```
(※ `ZipQuestionsWith` 為示意 helper)

為何能解決 Root Cause?  
• Assert 直接把「錯誤假設」在 Debug 階段炸出來，開發者第一時間修正。  
• Release 版自動剔除 Assert，維持效能。  
• 多情境測試覆蓋邊界案例，確保演算法完整。  

**Cases 1**:  
• 輸入 PAPER-NORMAL1（只答對第一題）；舊程式得 40 分，新程式得 20 分，符合預期。  

**Cases 2**:  
• 輸入 PAPER-NATIVE（全錯）；舊程式得 −40 分，新程式 Assert 先偵測「分數 < 0」並在 Debug 時中斷，修正後正式版輸出 0 分。  


## Problem: 在程式中大量硬塞 `if / throw / Console.WriteLine`，導致程式難讀又慢

**Problem**:  
為了避免各種錯誤，工程師把所有檢查與除錯訊息硬塞在主要邏輯中，程式充滿 `if (...) throw ...`、`Console.WriteLine`，讀者看不到核心流程，效能也因不必要的 runtime 分支與 I/O 下降。

**Root Cause**:  
1. 把「防禦性驗證」與「商業邏輯」混在一起。  
2. 未區分 Debug 與 Release 行為。  
3. 缺乏可以「只在開發/測試期啟動」的除錯基礎建設。

**Solution**:  
1. 採用 .NET 內建 `Trace.WriteLine` 與 `Trace.Assert`，在程式碼中宣告假設，而非內嵌大量 if/throw。  
2. 這些 Trace/Assert 於 Release 版預設被移除或可透過 `app.config` 切換，不影響正式效能。  
3. 保留少量「對外可預期」的例外（如無法載入檔案），其餘內部一致性以 Assert 處理。  

**Cases 1**:  
• 以原始「硬塞檢查程式」與「Trace/Assert 精簡版」比較：  
  – 行數由 120 行降到 80 行，可讀性大幅提升。  
  – Release 版效能回復到原本 99% 水準（Console I/O 移除）。  

**Cases 2**:  
• Code Review 時新進人員能在 5 分鐘內看懂精簡版流程，相較舊版平均需 15 分鐘。  


## Problem: 錯誤直到上線後才被發現，維護成本高

**Problem**:  
若程式缺乏「Fail Fast」設計，錯誤只能在正式環境、甚至客戶回報時才顯現，導致修復時間長、客訴風險高。

**Root Cause**:  
1. Release 組態下完全移除所有檢查，錯誤被「吞」掉。  
2. 測試流程只跑 Happy Path，未涵蓋邊界或例外情境。  

**Solution**:  
1. 在 Debug/測試階段全面開啟 Assert，使違反假設的情況立即中斷並顯示 Call Stack。  
2. 建立多份測試資料（滿分、零分、部分得分、資料格式錯誤）自動化回歸測試。  
3. 對正式環境保留可選擇的 Trace Listener（例如檔案或 EventLog），當需要遠端診斷時再啟用。  

**Cases 1**:  
• 將上述 Assert 與單元測試整合到 CI：  
  – 30 筆邊界測試資料，每次 Commit 60 秒內跑完。  
  – 發現負分 Bug 的時間由上線後 3 天 → 上線前 5 分鐘。  

**Cases 2**:  
• 上線後三個月內零客戶回報「分數計算錯誤」，相較上一版本平均每月 5 筆工單，維運工時下降 80%。