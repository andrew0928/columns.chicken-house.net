---
layout: post
title: "網路搶票小幫手 - 遠端網站時鐘, WebServerClock v1.0"
categories:

tags: ["有的沒的", ".NET", "C#", "Tips"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2017/01/webserverclock-logo.png
---

![LOGO](/wp-content/uploads/2017/01/webserverclock-logo.png)
圖片來源: [http://blog.mixflavor.com/2013/12/ticket.html](http://blog.mixflavor.com/2013/12/ticket.html)


很多線上訂票，或是限時搶購等等的應用，都會碰到一個困擾:

*我的電腦時鐘跟網站的時鐘有誤差，我怎樣才能在網站的 00:00 整按下訂購的按鈕??*

如果你有這種困擾，哈哈哈，那你看這篇就對了 :D


> 如果你以為這是自動搶票的機器人，那你可以關掉瀏覽器了 XD
> 這篇文章不會教你任何後門，用非正當手段搶到票，只是個輔助工具，讓你能更精確掌握 server 的時鐘，可以
> 更準確的在那關鍵的一秒按下訂購的按鈕而已..

<!--more-->

我們家常愛往花東跑，每次訂車票都是個挑戰... 所以才會有這念頭寫了這個小工具，現在 [release 1.0](https://github.com/andrew0928/WebServerClock)，
同時 open source 出來，有需要的朋友盡量拿去用別客氣 :D

# 運作原理

其實這個小工具沒什麼了不起的，寫的程式碼不到 100 行就搞定了。主要就是透過 HttpClient, 從訂票網站
的 http response header 得知 server side 的時間，跟本地的時間相比，得到兩邊時鐘的落差，想辦法
模擬遠端 server 的時間，讓訂票者能更容易地掌握按下按鈕的那一秒...。

其實要做對時這件事，比較正規的做法是 [NTC](http://fangpeishi.com/ntp_problem.html)，不過這點
不大實際，因為:

1. 目標網站本身不會架設 NTP server 啊  
(真的有架而且還對外開放的話，維運人員可以回家吃自己了)
2. 目標網站本身可能沒有啟用網路對時 (NTP client)

我就碰過那種 server 跟標準時間的誤差大到用分鐘為單位的，我也碰過 web 跟 db 的時差大到用小時為單位的，
導致 ```select ... from ... where createdate > getdate();``` 這種 query 都會跑出很誇張的結果...

所以，唯一確定能用的對時資訊，就只有 Http/1.1 定義的 date 這個 response header 了。看一下 [RFC2616](https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html) 的定義:

> 14.18 Date
>
> The Date general-header field represents the date and time at which the message was originated, having the same semantics as orig-date in RFC 822. The field value is an HTTP-date, as described in section 3.3.1; it MUST be sent in RFC 1123 [8]-date format.
> 
> Date  = "Date" ":" HTTP-date
>
> An example is
> 
> Date: Tue, 15 Nov 1994 08:12:31 GMT
>
> Origin servers MUST include a Date header field in all responses, except in these cases:
> 
> 1. If the response status code is 100 (Continue) or 101 (Switching Protocols), the response MAY include a Date header field, at the server's option.
> 2. If the response status code conveys a server error, e.g. 500 (Internal Server Error) or 503 (Service Unavailable), and it is inconvenient or impossible to generate a valid Date.
> 3. If the server does not have a clock that can provide a reasonable approximation of the current time, its responses MUST NOT include a Date header field. In this case, the rules in section 14.18.1 MUST be followed.
>
> A received message that does not have a Date header field MUST be assigned one by the recipient 
> if the message will be cached by that recipient or gatewayed via a protocol which requires a Date. 
> An HTTP implementation without a clock MUST NOT cache responses without revalidating them on every 
> use. An HTTP cache, especially a shared cache, SHOULD use a mechanism, such as NTP [28], to 
> synchronize its clock with a reliable external standard.

有兩個重點，除了上面描述的幾種例外之外，Server 是必須要在 response headers 裡送出 date 這個 header 的。
另外雖然最後也標示了這機制的精確度不足，校時的目的應該改用 NTP，不過... 就是沒得用啊 T_T...

不管怎樣，做完這些研究，大致上可以確認用 header 來對時的可用性了。網站一定會支援，只是精確度你要自己拿捏...


# 程式碼說明

OK，接下來就是實作了。我找張現成的圖，比較好解釋:

![時序圖](/wp-content/uploads/2017/01/webserverclock-operate.gif)
圖片來源: [http://ccnet.ntu.edu.tw/ntp/operate.html](http://ccnet.ntu.edu.tw/ntp/operate.html)

實作上的困難還不少。這張圖把 NTP server 換成 WEB server，回傳的 Date header 時間點應該落在 T1 ~ T2
之間某個時間點，我就假定他是 T1' 好了。困難的點在於:

1. client side 除了 T0 跟 T3 之外，其他通通無法確定
2. 網路環境差異很大，傳輸時間 (T1 - T0) 跟 (T3 - T2) 不一定相同
3. (T1' - T1) 跟 (T2 - T1') 也不一定相同，一樣完全無法預測

所以... 既然通通都不知道，那就用猜的就好了 XD，我就假設 T1' 的時間點，就是 T0 + (T3 - T0)/2 了...
按照這樣的原則，就可以得知 PC 端的時間是 T0 + (T3 - T0)/2 時，Server 端的時間就是 Date header 標示
的時間，計算出兩端的時間差 (Offset), 然後用本地的時鐘，加上時間差，每 30 ms 更新一次時間，來模擬遠端
的時鐘。最大可能的誤差，就是 (T3 - T0) / 2 了。

廢話講一堆，寫成程式碼就是這段 code:

```csharp
    private async void button1_Click(object sender, EventArgs e)
    {
        HttpClient client = new HttpClient();
        client.BaseAddress = new Uri(this.textWebSiteURL.Text);

        HttpRequestMessage req = new HttpRequestMessage(HttpMethod.Head, "/");

        DateTime t0 = DateTime.Now;
        HttpResponseMessage rsp = await client.SendAsync(req, HttpCompletionOption.ResponseHeadersRead);
        DateTime t3 = DateTime.Now;
        TimeSpan duration = t3 - t0;

        DateTime t1p = DateTime.Parse(rsp.Headers.GetValues("Date").First());
        this.Offset = t1p - t0.AddMilliseconds(duration.TotalMilliseconds / 2);

        this.labelOffset.Text = string.Format(
            @"時間差: {0} msec, 最大誤差值: {1} msec", 
            this.Offset.TotalMilliseconds,
            duration.TotalMilliseconds / 2);
    }
```

T0, T1P (就是指 T1'), T3 就是按照上面那張時序圖來命名的，這段 code 最終的 result 是要算出
兩端的時間差 Offset。這動作只在你設定網站時計算一次，不是每分每秒都在抓 server side 時間，不用擔心
造成網站 loading 或是害你被 band IP。

整段 code 包裝進 windows form 後，執行起來像這樣:

![app](/wp-content/uploads/2017/01/webserverclock-capture01.png)

使用方法很簡單，填好網址, 按下 [同步] 就會執行上面那段 code, 同時底下的時鐘就會自動搭配 offset 來修正結果。
左下方會有小字顯示相關資訊，其實不大需要管他，看時鐘就好..

# Release Notes

昨天幫我家大人訂票時，試用過一次，效果還不錯，結果我訂到票了，他沒訂到... 哈哈哈哈...
這個版本只是我自己用的，所以很多防呆措施通通都沒做，比如網站沒有填，或 URL 格式不對 (例如: 沒有打 http://)
或是 date header 找不到或是格式不對... 等等的低級錯誤都沒有處理。

所以，我就直接把 source code release 出來了，有需要的可以自己 clone 回去用啊, 會看我的部落格的讀者們，
應該都有能力自己 build, 我就不提供 binary 了! 你願意 pull request, 或是用 issue 回報問題或建議都歡迎 :D

GitHub: [https://github.com/andrew0928/WebServerClock](https://github.com/andrew0928/WebServerClock)






