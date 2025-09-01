說明
原文篇幅極短，僅清楚描述一個實際改版情境：在 ASP.NET WebForms 的 BotCheck 驗證通過時，自動把本次 BotCheck 的題目與答案附加在留言後面，以免每次人工貼上。文中未提供實作碼與量化成效數據。以下據此整理為 1 個完整且可教學落地的案例；如需延展出更多實戰案例，請提供更多素材或允許我基於此情境進行擴充推演。


## Case #1: BotCheck 驗證通過後自動附加題目與答案至留言

### Problem Statement（問題陳述）
業務場景：[部落格留言系統使用 BotCheck 作防機器人驗證。讀者常對當次驗證題目感到好奇，作者過去需在留言中手動補充「這次的 BotCheck 是什麼」。此做法費時且容易遺漏或格式不一致，影響互動與閱讀體驗。需求是讓系統在驗證通過時，自動把當次 BotCheck 題目與回答附加到留言末端，完全免除人工貼上。]
技術挑戰：在 ASCX 控制中找到「驗證通過」的時間點，安全地取得當次題目與使用者答案，並於留言儲存流程只在驗證成功時插入資訊，還需避免 XSS、格式錯亂與與既有流程的耦合風險。
影響範圍：手動作業時間、留言一致性、讀者體驗、日後稽核（可追溯該次驗證的挑戰內容）。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. BotCheck 控制未對外暴露「已驗證的題目/答案」資料，留言層拿不到需要的資訊。
2. 留言提交流程缺少「驗證成功後後置處理（post-validation hook）」可插入附加內容。
3. 過去以人工補充為主，無自動化機制，造成重工與不一致。

深層原因：
- 架構層面：留言儲存與驗證控制之間無事件/介面整合點，導致跨層傳遞驗證上下文困難。
- 技術層面：ASCX 未提供公開屬性或事件（如 Validated）來輸出本次挑戰與答案；資料狀態未妥善保存（ViewState/HiddenField）。
- 流程層面：需求未制度化至開發流程，缺少對「驗證上下文」的標準化記錄與呈現規範。

### Solution Design（解決方案設計）
解決策略：擴充 BotCheck 的 ASCX，新增公開屬性（CurrentQuestion、AcceptedAnswer、IsValid）與 Validated 事件，於 Validate 成功後設定值並觸發事件；在留言提交事件中先檢查驗證成功，再以安全方式（HTML Encode、長度限制）把題目/答案附加至留言內容，最後儲存。確保只有通過時才附加，並不改動既有 UI/版面大結構。

實施步驟：
1. 擴充 BotCheck 控制（暴露驗證上下文）
- 實作細節：新增 CurrentQuestion、AcceptedAnswer、IsValid 公開屬性；於 Validate 通過時觸發 Validated 事件；使用 ViewState/HiddenField 保存問題，避免 PostBack 流失。
- 所需資源：ASP.NET WebForms、C#、現有 BotCheck 題庫/校驗邏輯。
- 預估時間：0.5 天

2. 調整留言提交流程（插入後置處理）
- 實作細節：在 btnSubmit_Click 內呼叫 BotCheck.Validate()；若失敗則回報錯誤並中止儲存；若成功，將題目/答案以 HtmlEncode 後附加至留言內容末端。
- 所需資源：現有留言儲存服務/Repository。
- 預估時間：0.5 天

3. 安全與格式化處理
- 實作細節：對題目/答案做 HtmlEncode、防長度過長（DoS 風險）、統一標記格式（如 [BotCheck] 前綴）；可為答案做遮罩策略（若題型重複可能降低驗證強度）。
- 所需資源：安全檢視清單、單元測試。
- 預估時間：0.5 天

4. 相容與回歸測試
- 實作細節：測試多語系、不同瀏覽器、驗證失敗場景、重複提交與快取/回上一頁再提交等情境。
- 所需資源：測試案例、測試帳號。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 注意：以下為示意性實作（原文未附程式碼），以 ASP.NET WebForms 為例。
// Controls/BotCheck.ascx
// <asp:Label ID="lblQuestion" runat="server" />
// <asp:TextBox ID="txtAnswer" runat="server" />
// <asp:HiddenField ID="hfQuestion" runat="server" />

public partial class Controls_BotCheck : System.Web.UI.UserControl
{
    public string CurrentQuestion
    {
        get => (string)ViewState["Q"];
        private set { ViewState["Q"] = value; lblQuestion.Text = value; hfQuestion.Value = value; }
    }

    public string AcceptedAnswer { get; private set; }
    public bool IsValid { get; private set; }
    public event EventHandler Validated;

    protected void Page_Load(object sender, EventArgs e)
    {
        if (!IsPostBack)
        {
            // 取得新題目（可接題庫/隨機器制）
            CurrentQuestion = GenerateQuestion();
        }
    }

    public bool ValidateNow()
    {
        var ok = CheckAnswer(hfQuestion.Value, txtAnswer.Text);
        IsValid = ok;
        if (ok)
        {
            AcceptedAnswer = txtAnswer.Text.Trim();
            Validated?.Invoke(this, EventArgs.Empty);
        }
        return ok;
    }

    private string GenerateQuestion()
    {
        // 範例：簡單算術（實務中請改為正式題庫/圖片/字串）
        int a = new Random().Next(1, 9);
        int b = new Random().Next(1, 9);
        // 可將正確答案存在 Session/Cache 與題目關聯
        Session["BC_Ans_" + ClientID] = (a + b).ToString();
        return $"{a} + {b} = ?";
    }

    private bool CheckAnswer(string question, string userAnswer)
    {
        var key = "BC_Ans_" + ClientID;
        var expected = Session[key] as string;
        return !string.IsNullOrEmpty(userAnswer)
               && !string.IsNullOrEmpty(expected)
               && string.Equals(userAnswer.Trim(), expected, StringComparison.Ordinal);
    }
}

// 留言頁面（Comment.aspx.cs）
protected void btnSubmit_Click(object sender, EventArgs e)
{
    if (!BotCheck1.ValidateNow())
    {
        lblError.Text = "驗證失敗，請再試一次。";
        return;
    }

    string commentBody = txtComment.Text.Trim();
    string q = System.Web.HttpUtility.HtmlEncode(BotCheck1.CurrentQuestion);
    string a = System.Web.HttpUtility.HtmlEncode(BotCheck1.AcceptedAnswer);

    // 可視需求遮罩 a，例如顯示前一兩字
    string appended = $"<br/><span class='botcheck-info'>[BotCheck] Q: {q} | A: {a}</span>";

    // 長度保護
    if (appended.Length > 256) appended = appended.Substring(0, 256);

    SaveComment(commentBody + appended); // 既有儲存流程
    Response.Redirect(Request.RawUrl + "#comments");
}
```

實際案例：作者於部落格將 BotCheck 的題目與答案在驗證通過時自動附加至留言，避免每次手動貼「這次 BotCheck 是什麼」。
實作環境：文中僅提及 ASP.NET 與 ASCX；上述示例以 ASP.NET WebForms（.NET Framework）示意。
實測數據：
- 改善前：需人工在留言附上本次題目，易遺漏且不一致（原文未量化）。
- 改善後：驗證通過即自動附加，無需人工（原文未量化）。
- 改善幅度：未提供（原文無數據）。

Learning Points（學習要點）
核心知識點：
- 在 WebForms 中以 UserControl 暴露狀態與事件（屬性、Validated 事件）。
- 驗證流程的正確插入點（先驗證、後附加、再儲存）與只在成功時執行。
- 輸入/輸出安全（HtmlEncode、長度限制）與對 UX 的格式一致性。

技能要求：
- 必備技能：C#、ASP.NET WebForms 基本事件生命週期、ViewState/Session 使用、基本 HTML/JS。
- 進階技能：控制與頁面的鬆耦合設計（事件/介面）、XSS 防護、安全審視與單元測試。

延伸思考：
- 應用場景：其它驗證（簡答題、問卷）通過後附加上下文、工單系統附加審核摘要。
- 限制/風險：公開答案或可降低簡單題型的防機器人強度；建議題庫多樣化或只公開題目不公開答案。
- 優化方向：國際化（多語系題目）、遮罩答案、記錄驗證元資料（不在前端顯示）、支援 MVC/Razor 或前後端分離架構。

Practice Exercise（練習題）
- 基礎練習（約 30 分鐘）：在現有 WebForms 頁面加入一個簡易 BotCheck 控制，通過後將「Q/A」以純文字附加到 TextBox 內容並顯示。
- 進階練習（約 2 小時）：完成上述完整流程（事件、HtmlEncode、長度限制、失敗提示），並撰寫 5 個單元測試（成功、失敗、空值、重複提交、回上一頁再提交）。
- 專案練習（約 8 小時）：將 BotCheck 模組化（獨立組件 + 介面 IBotChallenge），支援可插拔題庫與記錄驗證元資料到資料庫，並提供管理頁面查詢最近 100 筆驗證。

Assessment Criteria（評估標準）
- 功能完整性（40%）：驗證成功才附加；附加格式一致；失敗有明確提示；不影響既有留言流程。
- 程式碼品質（30%）：控制與頁面低耦合；清楚的公開介面；適當的例外處理與註解；單元測試覆蓋。
- 效能優化（20%）：不增加明顯延遲；題庫/校驗邏輯具可快取性；無過度 Session/ViewState 膨脹。
- 創新性（10%）：合理的答案遮罩策略、可組態的附加格式、支援多語系或可插拔驗證引擎。


案例分類
1) 按難度分類
- 入門級（適合初學者）：Case #1

2) 按技術領域分類
- 整合開發類：Case #1
- 安全防護類（輸入/輸出安全、XSS 防護）：Case #1

3) 按學習目標分類
- 技能練習型：Case #1
- 問題解決型：Case #1


案例關聯圖（學習路徑建議）
- 先學案例：Case #1（唯一案例）
- 依賴關係：無
- 完整學習路徑建議：先理解 WebForms UserControl 的事件與狀態保存（ViewState/Session）→ 練習在提交流程中插入驗證與後置處理 → 加入安全與格式一致性 → 最後進行模組化與測試。若後續擴展到 MVC/前後端分離，建議再學習相對應的驗證中介層與 API 設計。

補充
若您希望我基於此情境擴充出 15-20 個可訓練/考核的實戰案例（例如：安全強化、國際化、事件驅動重構、題庫抽象化、資料持久化、異常處理、回歸測試策略等），請告知是否接受在不違反原文事實的前提下進行合理推演與延伸。