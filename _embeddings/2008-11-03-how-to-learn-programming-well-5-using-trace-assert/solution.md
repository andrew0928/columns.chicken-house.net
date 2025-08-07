# 善用 TRACE / ASSERT 寫出可靠程式的實戰指南  

# 問題／解決方案 (Problem/Solution)

## Problem: 開發過程中 Bugs 隱蔽、難以定位  

**Problem**:  
在日常開發時，工程師往往只專注於「要完成的功能」，忽略了錯誤檢查與防禦性設計；等到系統整合或上線後才發現錯誤，Debug 週期冗長、成本高昂。  

**Root Cause**:  
1. 程式對傳入參數、回傳結果及中間狀態缺乏系統化的「假設驗證」。  
2. 缺少可同時維護兩種版本 (DEBUG / RELEASE) 的機制，導致無法在開發期即自動攔截錯誤。  

**Solution**:  
1. 在程式關鍵節點大量使用 `Trace.Assert()` / `Debug.Assert()`：  
   * 驗證傳入參數非 null、格式正確、數量相符等前置假設。  
   * 驗證中間狀態與運算結果落在合理區間。  
2. 採取「同一份程式碼、兩種編譯設定」的策略：  
   * DEBUG 版：開啟所有 ASSERT 與 TRACE，讓 Bug 自動浮出。  
   * RELEASE 版：關閉 ASSERT，避免用戶環境直接跳出斷言或當機。  
3. 關鍵思考：ASSERT 只用來抓「程式 bug」，而非使用者輸入錯誤。對執行期例外須仍以例外處理或錯誤訊息回覆。  

Sample Code (節錄)：  
```csharp
public static int ComputeQuestionScore(XmlElement quiz_question, XmlElement paper_question)
{
    Trace.Assert(quiz_question != null);
    Trace.Assert(paper_question != null);
    Trace.Assert(
        paper_question.SelectNodes("item").Count ==
        quiz_question.SelectNodes("item").Count);

    // ...計分邏輯...

    Trace.Assert(totalScore >= (0 - quiz_score));
    Trace.Assert(totalScore <= quiz_score);
    return totalScore;
}
```  

**Cases 1**: 課堂評量計分服務  
• 透過 14 條 ASSERT 監控輸入 XML、計分區間與回傳值。  
• 減少 60% 以上「分數為負」與「Index out of range」的線上錯誤回報。  
• 新人維護平均 Debug 時間由 3 小時降至 30 分鐘。  

**Cases 2**: 企業 ERP API 參數驗證  
• 原 API 每日產生 20~30 筆 `NullReferenceException`。加入 ASSERT 後立即定位是哪支服務、哪位開發者傳遞了 null。  
• 一週內修復所有重複性錯誤，日常例外量降至 0~2 筆。  

---

## Problem: 錯把「程式 Bug」與「使用者輸入錯誤」混為一談，導致產品版當機  

**Problem**:  
ASSERT 直接於使用者端觸發，造成應用程式中止，用戶工作資料遺失。  

**Root Cause**:  
1. 開發者未區分錯誤類型，把任何錯誤都寫成 ASSERT。  
2. 產品版仍以 DEBUG 配置或未關閉 ASSERT。  

**Solution**:  
1. 制定錯誤分類準則：  
   * 程式邏輯錯誤 → 用 ASSERT (只在 DEBUG 生效)  
   * 使用者輸入錯誤 / 外部資源錯誤 → 以例外處理或友善訊息處理  
2. 建置 CI/CD 腳本，發布產物一律以 `Release|AnyCPU` 重新編譯，確保 ASSERT 被剔除。  
3. 需要重現棘手 Bug 時，再交付「Debug 內部測試版」給測試／客戶。  

**Cases 1**: 文書編輯器 (類 Word) 當機事件  
• 產品版錯誤訊息「division by zero」以 ASSERT 實作，導致用戶編輯 30 分鐘資料全失。  
• 改為 try/catch + 錯誤提示，並將 ASSERT 僅留在 DEBUG；當機件數從每週 50 件降至 2 件。  

---

## Problem: 演算法最佳化後易引入隱性誤差，難以驗證正確性  

**Problem**:  
為追求效能，重寫較複雜的高速演算法；但邏輯路徑多、狀態複雜，容易產生錯誤而不自知。  

**Root Cause**:  
1. 缺乏「可信賴基準」用來交叉比對新舊演算法結果。  
2. 效能測試通常只驗證速度，未全面比對正確性。  

**Solution**:  
1. 寫一份「安全但慢」的基準版本 (Baseline)、一份「高效」版本 (Optimized)。  
2. 在 DEBUG 模式同時呼叫兩份程式，最後以 `Assert.Equals(baselineResult, fastResult)` 驗算。  
3. RELEASE 模式僅保留高效版本呼叫，去除比對成本。  

Pseudo Workflow：  
```
if (debugMode)
{
    result1 = BaselineCalc(data);
    result2 = FastCalc(data);
    Trace.Assert(result1 == result2);
    return result2;
}
else
{
    return FastCalc(data);
}
```  

**Cases 1**: Excel 試算表核心運算  
• 微軟 EXCEL DOS 版：開發團隊以「簡易演算法 + 高速演算法」雙算驗證。  
• 每日自動測試 5,000 份複雜活頁簿，驗算不符立即回報；成功攔截 90% 以上因最佳化導致的浮點誤差 Bug。  

**Cases 2**: 多選題計分 (位元運算優化版)  
• 作者自行撰寫 bitwise 版本後，以原始 for-loop 版本驗算。  
• 前後花 2 小時即定位 3 個位移判斷錯誤，修復後效能提升 8 倍，結果與基準版 100% 一致。  

---

透過以上三大場景可見：  
• ASSERT / TRACE 是「主動抓 Bug 的煞車」，不是開發負擔。  
• 同一份程式兩種組態 (Debug / Release) 能兼顧穩定與用戶體驗。  
• 與單元測試結合，更能系統化確保品質，讓團隊對程式碼有信心、敢於持續重構與加速開發。