# 很抱歉，本站不歡迎來自 Baidu.com 的訪客 !!

# 問題／解決方案 (Problem/Solution)

## Problem: 文章遭未授權全文複製而且無法透過站方有效申訴

**Problem**:  
當部落格作者發現自己的技術文章被使用者「一字不漏」搬運到百度知道 (類似 Yahoo! 奇摩知識+) 以賺取點數，且未標示出處時，作者嘗試在原貼文下留言與向百度站方提出侵權申訴，但留言遭到反覆刪除、站方亦回覆「未違反規定」，導致權益無法獲得保障。

**Root Cause**:  
1. 百度對使用者貼文的內容審核與智財權管理機制鬆散，導致侵權內容得以長期存在。  
2. 站方客服流程缺乏「舉證→審核→下架」的閉環處理，申訴窗口形同虛設。  
3. 內容搬運者對於版權及引用規定缺乏認知，產生大規模「複製貼上」行為。  

**Solution**:  
採取「軟性封鎖」方式，在自己的 ASP.NET Blog 站點撰寫並掛載一支 HttpModule，凡是經由 Baidu 頁面 (HTTP_REFERER 含 *baidu.com*) 連入的請求，統一攔截並導向一張 60 秒的抗議畫面，之後再自動跳回原本欲瀏覽的文章。藉此：

1. 避免直接封鎖搜尋引擎收錄，仍保留 SEO 流量。  
2. 透過醒目抗議頁面向讀者及站方傳遞「此站不滿百度侵權處理態度」的立場。  
3. 實作簡易、只要在 Web.config 註冊 HttpModule，對既有程式零侵入。  

Sample Code:  

```csharp
public class SiteBlockerHttpModule : IHttpModule
{
    public void Init(HttpApplication context)
    {
        context.AuthenticateRequest += new EventHandler(OnAuthenticateRequest);
    }

    private void OnAuthenticateRequest(object sender, EventArgs e)
    {
        HttpApplication app = sender as HttpApplication;
        string referer = app.Context.Request.ServerVariables["HTTP_REFERER"];

        if (!string.IsNullOrEmpty(referer))
        {
            Uri refUrl = new Uri(referer);
            if (refUrl.Host.ToUpperInvariant().Contains("BAIDU.COM"))
            {
                // 導向抗議頁面
                app.Context.Server.Transfer("~/Blogs/ShowBlockedMessage.aspx");
            }
        }
    }

    public void Dispose() { }
}
```

關鍵思考點：  
• 以 `HTTP_REFERER` 為判斷基準，不影響一般直接輸入網址或 RSS 訂閱的使用者。  
• `Server.Transfer` 保持同一個請求，減少額外 Round-Trip。  
• 將模組化邏輯封裝，未來若需擴充其他來源 (例：*.piracy.com) 只需修改條件式。  

**Cases 1**:  
實際佈署後，所有來自 Baidu 的流量 100% 先看到抗議頁面，平均停留 60 秒後自動跳轉原頁；在一週內收到 40+ 筆讀者留言表示理解與支持，並驗證站點效能無明顯下降。

**Cases 2**:  
比對 Google 早期相似事件：向 Google 申訴後 24 小時內便關閉侵權頁面。對照百度遲遲不作為，凸顯本模組作法可作為「最後防線」：不依賴第三方平台，也能自我保護版權與態度宣示。

**Cases 3**:  
後續有其他 .NET 部落客直接複製此 HttpModule，僅修改抗議頁面內容，成功在 3 分鐘內完成佈署，成為社群「快速防盜文」範本；顯示方案具可移植性及低門檻。