---
layout: post
title: "BlogEngine Extension: Secure Post v1.0"
categories:

tags: [".NET","ASP.NET","BlogEngine Extension","BlogEngine.NET","作品集","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2008/09/06/blogengine-extension-secure-post-v1-0/
  - /columns/post/2008/09/06/BlogEngine-Extension-Secure-Post-v10.aspx/
  - /post/2008/09/06/BlogEngine-Extension-Secure-Post-v10.aspx/
  - /post/BlogEngine-Extension-Secure-Post-v10.aspx/
  - /columns/2008/09/06/BlogEngine-Extension-Secure-Post-v10.aspx/
  - /columns/BlogEngine-Extension-Secure-Post-v10.aspx/
wordpress_postid: 70
---

因為家裡大人開出條件，除非新的 BLOG 系統 (就是我在用的 BlogEngine 啦) 有特定文章要輸入密碼才能看的功能，否則她就不想換系統了 (原來是用 CommunityServer 2007)。要弄密碼其實很簡單，不過過去試過 IIS 加上整合式驗證... 弄到最後該看的人看不到，也沒擋到該擋的人而作罷...。

仔細想了想大人的需求，要的就是簡單的控制機制。不需要先建立帳號，也不需要登入，就是特定幾篇文章要輸入暗號才能看到內容，就這樣而以。無耐 BlogEngine 還算很年輕，替它寫的 Extension 也還不多，[官方網站提供了幾個 Extension](http://www.dotnetblogengine.net/page/extensions.aspx) 列表，找到最接近的是這個: [Password Protected Post](http://blog.lavablast.com/post.aspx?id=ceb887a9-f0d1-4379-815a-513cda5d5fc8)... 不過它是以登入 BE 為使用者認證的方式，再依照 ROLE 跟 CATEGORY 的配對為授權方式，來控制那些讀者能看到那些文章...。就是不想要替每個人建帳號啊，看來只好自己寫了... Orz。

以往都是想要作什麼很簡單，難是難在把它作出來..。現在都反過來了，工具越來越強，系統也越來越完整，難的反而是思考要怎麼作，程式碼沒幾行就搞定了。之前的文章介紹過 BlogEngine 的 Extension 機制，這次就實際來試看看。我要寫的東西很簡單，就一組密碼就好，要有夠簡單的方式讓大人能夠指定那幾篇文章是要保護的，而所有的人 (已登入的除外) 只能看到提示輸入密碼的訊息，密碼打對了才會顯示文章內容。至於密碼要不要加密? 會不會被竊聽? 不重要啦，只要保護不要遜到按右鍵簡示原始碼，密碼跟內容都看光光了就好。

順手寫了幾行 CODE，先驗證一下最基本的動作做不做的到 (POC: Prove Of Concept)。第一步是先把顯示內容的動作攔下來，換成制示的輸入密碼訊息... 這個簡單，沒幾行就搞定了:

![Password Protected Post Demo](/images/2008-09-06-blogengine-extension-secure-post-v1-0/image_3.png)

直接從 CodePlex 抓下來的 Source Code, 解壓縮完就可以寫了。加上這段 CODE 並不難，整個 Extension 只有這樣而以:

**修改 POST 內容，改成提示輸出密碼的畫面**

```csharp
[Extension("SecurePost", "1.0", "<a href=\"http://columns.chicken-house.net\">chicken</a>")]
public class SecurePost
{
    static SecurePost()
    {
        Post.Serving += new EventHandler<ServingEventArgs>(Post_Serving);
    }

    private static void Post_Serving(object sender, ServingEventArgs e)
    {
        Post post = sender as Post;
        StringBuilder bodySB = new StringBuilder();
        {
           // 略。透過 bodySB 輸出 HTML
        }
        e.Body = bodySB.ToString();
    }
}
```

看起來 CODE 還不少，不過算一算真正在作事的都是在湊那堆 HTML ... 關鍵只有一開始去攔 Post.Serving 事件，接到自己的事件處理器 Post_Serving( ) 上，之後所有會輸出 Post 內容的地方，都會觸發這個事件。然後只要在事件處理器內去調整 Post 內容就可以了。

好，好的開始是成功的一半，已經完成 1/3 了 (什麼???) 第一部份的 CODE 產生的 HTML，會引導使用者輸入密碼，按下 [GO] 之後，就會連到 POST 的網址了。不過除了原本網址之外 (post.AbsoluteLink) 後面還要加上 "?pwd=xxxxxx" 帶上使用者輸入的密碼。前面講過我只要最基本的防護，其它進階的安全問題就不理它了。我只要掌握兩個原則:

1. 密碼一定要在 SERVER 端確認 (不能讓不知道密碼的人 view source 就找到密碼)
2. 沒輸入密碼前不能在 CLIENT 端出現 POST 內容 (不能單純的用 DHTML 把文章內容 "藏" 起來)

另外補一件事，我也不要讓全部的文章都用這種機制保護。只要有特別標示的 POST 要密碼就好。看到 BlogEngine 內建的 BreakPost 這個擴充程式，我就仿照它的作法，內文找到特定字串就啟用。我定的規則是整篇 POST 內容開頭一定要是 "[password]" 才會啟用密碼保護機制。

既然這樣，第二步也很簡單。如果密碼對，一切照原狀顯示內容。密碼不對的話就一樣攔下來...。程式碼.... 只是在第一步的程式碼多了... 兩行...

**加上檢查密碼的 CODE**

```csharp
private static void Post_Serving(object sender, ServingEventArgs e)
{
    Post post = sender as Post;
    if (HttpContext.Current.Request["pwd"] == Password) return;
    if (!e.Body.StartsWith("[password]", StringComparison.CurrentCultureIgnoreCase)) return;
    StringBuilder bodySB = new StringBuilder();
    {
       // 略。透過 bodySB 輸出 HTML
    }
    e.Body = bodySB.ToString();
}
```

啥米? 就是第一部份的 CODE 加上第四及第五行就搞定了? 程式不挑的話，現在已經寫完了... 哈哈! 上面的輸入密碼畫面，輸入正確密碼後就可以看到文章內容了。我特地連網址列一起複製下來，在網址列上會看到密碼明碼。照道理應該是要先 HASH 啦，不過 CLIENT SIDE 跟 SERVER SIDE 都要有同樣的 HASH 機制才行，想用 MD5 / SHA256 之類的來算，無耐 CLIENT 要弄這些也是很煩，就決定不理它了...。明碼就明碼吧，執行後的畫面像這樣:

![Password Protected Post Result](/images/2008-09-06-blogengine-extension-secure-post-v1-0/image_6.png)

剩下的部份就沒什麼了，想想加上去好了。就是透過 BlogEngine 的 Extension Manager，讓使用者可以簡單的調整參數。要讓使用者自定的參數只有三個:

1. 文章內容被保護時，要顯示的訊息
2. 密碼提示
3. 真正的密碼

這些東西自己做的話，就還得想要開檔案或寫資料庫，有點小囉唆，不過已經有 Extension Manager 了，只要在原本的 static constructor 再加幾행就搞定:

**加上 Extension 接受的設定參數，及初始值**

```csharp
static SecurePost()
{
    Post.Serving += new EventHandler<ServingEventArgs>(Post_Serving);
    ExtensionSettings settings = new ExtensionSettings("SecurePost");
    settings.AddParameter(
        "SecurePostMessage",
        "顯示訊息:");
    settings.AddParameter(
        "PasswordHint",
        "密碼提示:");
    settings.AddParameter(
        "PasswordValue",
        "指定密碼:");
    settings.AddValues(new string[] {
        "本篇文章已受密碼保護，請依照題示輸入密碼。", 
        "一二三四",
        "1234"});
    settings.IsScalar = true;
    settings.Help = "用密碼保護文章的內容。";
    ExtensionManager.ImportSettings(settings);
    _settings = ExtensionManager.GetSettings("SecurePost");
}
```

我已經很努力的多撐幾行了... 不過也只有這廿行，寫完了...。整個 .cs 檔案直接丟到 ~/App_Code/Extension 就算安裝完成。用管理者身份登入 BE 後，在 Extension 那頁可以看到:

![Extension Manager - SecurePost](/images/2008-09-06-blogengine-extension-secure-post-v1-0/image_9.png)

不錯，SecurePost 已經出現在 Extension Manager 裡了。因為有加上 settings 的程式碼，所以右邊有 [編輯] 的字樣出現。點下去之後會到這個畫面:

![Extension Settings](/images/2008-09-06-blogengine-extension-secure-post-v1-0/image_12.png)

嗯，看起來真專業，沒想到從頭到尾所有的 CODE 還不到一百行...。幾十行 CODE 寫出來的 Extension 就可以唬人了.. :D，試看看還真的會動耶 (廢話)。早知道寫起來那麼快，當初就不花那麼多時間去找人家寫好的了...。最後附上整段完整的程式碼，有需要的人就拿去用吧! 用法很簡單，全部複製下來 (可以按 [COPY CODE] 就好)，存檔，把檔案放在 ~/App_Code/Extension/SecurePost.cs 下，然後用管理者身份進入 BlogEngine Extension Manager 改一改就好了!

大功告成! 這個 Extension 如果對你有用的話就拿去用吧，要散佈也歡迎，不過只有個小要求，請不要把程式碼存到別的地方供人下載，請直接提供我這篇文章的網址就好。覺的好用就留個話給我，要幫我推一下文或讚助就更好了 :D，謝謝收看!

--

**完整的 SecurePost.cs 程式碼**

```csharp
using System;
using System.Web;
using System.Web.UI;
using BlogEngine.Core.Web.Controls;
using BlogEngine.Core;
using System.Text;




[Extension("SecurePost", "1.0", "<a href=\"http://columns.chicken-house.net\">chicken</a>")]
public class SecurePost
{
    private static string SecurePostMessage { get { return _settings.GetSingleValue("SecurePostMessage"); } }
    private static string Password { get { return _settings.GetSingleValue("PasswordValue"); } }
    private static string PasswordHint { get { return _settings.GetSingleValue("PasswordHint"); } }

    private static ExtensionSettings _settings = null;

    static SecurePost()
    {
        Post.Serving += new EventHandler<ServingEventArgs>(Post_Serving);

        ExtensionSettings settings = new ExtensionSettings("SecurePost");

        settings.AddParameter(
            "SecurePostMessage",
            "顯示訊息:");
        settings.AddParameter(
            "PasswordHint",
            "密碼提示:");
        settings.AddParameter(
            "PasswordValue",
            "指定密碼:");

        settings.AddValues(new string[] {
            "本篇文章已受密碼保護，請依照題示輸入密碼。", 
            "一二三四",
            "1234"});

        //settings.ShowAdd = false;
        //settings.ShowDelete = false;
        //settings.ShowEdit = true;
        settings.IsScalar = true;
        settings.Help = "用密碼保護文章的內容。";

        ExtensionManager.ImportSettings(settings);

        _settings = ExtensionManager.GetSettings("SecurePost");

    }

    private static void Post_Serving(object sender, ServingEventArgs e)
    {
        Post post = sender as Post;


        if (HttpContext.Current.User.Identity.IsAuthenticated == true) return;
        if (HttpContext.Current.Request["pwd"] == Password) return;
        if (!e.Body.StartsWith("[password]", StringComparison.CurrentCultureIgnoreCase)) return;


        StringBuilder bodySB = new StringBuilder();
        {
            bodySB.AppendFormat(
                "<b>{0}</b><p/>",
                HtmlEncode(SecurePostMessage));

            if (e.Location == ServingLocation.Feed)
            {
            }
            else
            {
                bodySB.Append("<div>");
                bodySB.AppendFormat(
                    @"請輸入密碼(提示: <b>{0}</b>): <input id=""postpwd"" type=""password""/><button onclick=""document.location.href='{1}'+'?pwd='+escape(this.parentNode.all.postpwd.value);"">GO</button>", 
                    PasswordHint,
                    post.AbsoluteLink);
                bodySB.Append("</div>");
            }
        }
        e.Body = bodySB.ToString();
    }

    private static string HtmlEncode(string text)
    {
        return HttpContext.Current.Server.HtmlEncode(text);
    }
}
```
