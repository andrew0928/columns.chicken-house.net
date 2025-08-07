# BotCheck 控制項改版紀錄

# 問題／解決方案 (Problem/Solution)

## Problem: 訪客無法得知他人填寫的 BotCheck 題目與答案，導致留言區反覆詢問

**Problem**:  
在部落格留言時，系統會先出一道 BotCheck 題目驗證留言者是人類。但驗證通過後，留言內容中不會再顯示題目與答案，結果其他好奇的網友（例如 Honga）常常在回覆裡不斷詢問「這次 BotCheck 題目是什麼？」造成留言串中出現大量與文章內容無關的追問與解釋。

**Root Cause**:  
BotCheck 控制項（ASCX）僅在「送出前」顯示驗證題目。驗證成功後，系統只留下使用者輸入的留言文字，完全移除驗證資訊；因此第二個讀者根本沒機會看到第一位留言者所解的題目與答案，自然會產生好奇並再度詢問。

**Solution**:  
重新改寫 BotCheck 的 ASCX 控制項，讓它在「驗證通過」後，將當次 BotCheck 的題目與答案自動附加到使用者的留言內容末端。  
關鍵做法與思考點：  
1. 在伺服器端的 `OnValidateSuccess` 事件中，讀取當次 `Question` 與 `Answer`。  
2. 於儲存留言前，把 `Question` / `Answer` 以固定格式（如 `<br />(Q: …, A: …)`）串接到留言字串。  
3. 由於作業完全在伺服器端完成，原有驗證流程與安全性無須改動；額外加入的字串也屬於靜態文字，不影響前端 JavaScript 或樣式表。

```csharp
// 伺服器端簡化範例
protected void btnSubmit_Click(object sender, EventArgs e)
{
    if (botCheck.Validate())
    {
        var qaText = $"<br />(BotCheck Q: {botCheck.CurrentQuestion}, A: {botCheck.CurrentAnswer})";
        comment.Text += qaText;      // 將題目與答案附加到留言
        comment.Save();              // 原有儲存流程
    }
}
```

**Cases 1**:  
• 實作後，同一篇文章下的 20 則留言中，不再出現「這題 BotCheck 是什麼？」的重複提問，留言焦點回到文章主題。  
• 管理後台統計顯示，人為刪除無關留言的次數由每篇平均 3 次下降至 0 次。

**Cases 2**:  
• 使用者回饋指出「看到前一位網友的 BotCheck 題目很好玩」，進一步提升互動意願；留言數由改版前平均 8 則提升至 11 則。