# 很抱歉，本站不歡迎來自 Baidu.com 的訪客 !!

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼本站要阻擋所有透過百度連入的訪客？
作者的文章被人完整複製貼到「百度知道」賺取點數且未標示出處。作者多次留言抗議卻一再被刪除，向百度官方反映也被告知「並未違反規定」，遲遲得不到妥善處理。相較於 Google 先前迅速下架盜文部落格的作法，百度的漠視讓作者極度不滿，因此決定以技術手段阻擋所有從 Baidu.com 連入的流量，並在 60 秒的抗議畫面後才讓使用者進入原頁面，以示抗議。

## Q: 之前 Google 遇到相同情況時是如何處理的？百度的做法又有什麼不同？
幾個月前有人在 Blogger.com 盜用作者文章，作者用英文向 Google 申訴後，Google 立即將該使用者網頁關閉；而本次在百度發生盜文事件時，作者的留言屢次被刪，百度官方回覆「未違反規定」而拒絕處理，導致問題遲遲無解。兩者相比，Google 採取積極下架行動，百度則選擇不作為。

## Q: 作者是如何透過 ASP.NET HttpModule 技術來實作「百度訪客阻擋」的？
作者撰寫了一個名為 SiteBlockerHttpModule 的自訂 HttpModule，並在 Web.config 註冊。模組於 AuthenticateRequest 階段取得 HTTP_REFERER，如果 Referer 網址中含有「BAIDU.COM」，便使用 Server.Transfer 將請求導向 「~/Blogs/ShowBlockedMessage.aspx」的抗議頁面。該頁面先顯示 60 秒的抗議內容，之後再自動跳回原始目標頁。

```csharp
public class SiteBlockerHttpModule : IHttpModule
{
    public void Init(HttpApplication context)
    {
        context.AuthenticateRequest += context_AuthenticateRequest;
    }

    void context_AuthenticateRequest(object sender, EventArgs e)
    {
        HttpApplication app = (HttpApplication)sender;
        string referer = app.Context.Request.ServerVariables["HTTP_REFERER"];

        if (!string.IsNullOrEmpty(referer) &&
            new Uri(referer).Host.ToUpperInvariant().Contains("BAIDU.COM"))
        {
            app.Context.Server.Transfer("~/Blogs/ShowBlockedMessage.aspx");
        }
    }

    public void Dispose() { }
}
```

## Q: 如果讀者想支持這次的抗議，可以怎麼做？
作者希望讀者能在文章下方留言表達支持，或透過「推推王」等社群平台幫忙轉貼、推文，一同對百度漠視智慧財產權的態度提出抗議。