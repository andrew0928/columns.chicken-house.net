---
layout: post
title: "API & SDK Design #3, API 的向前相容機制"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: API & SDK Design"
- "系列文章: 架構師觀點"
tags: ["API", "SDK", "系列文章", "ASP.NET", "架構師"]
published: true
comments: true
redirect_from:
logo: //wp-content/uploads/2016/10/apisdk-02-socket.jpg
---


上一篇意外的受歡迎，那麼續集就不富堅了，sample code 準備好就開始動工了。

講完 API / SDK 之間當下的約定，接下來來講講 API 跟 SDK 之間的承諾吧! 
當下的約定，會保證當下的 API 跟 SDK 可以搭配運作，然而承諾，則是保證當下的 API 能夠跟過去某個時間以後的所有版本 SDK 都能夠
搭配，這個很考驗架構師的功力了。一個不小心，過去某個不知名的版本就給你出問題了。負責開發維護 API 的人，該怎麼確保這種問題不會
發生?

<!--more-->

# 導讀


# 碎碎念: API 的版本策略

在講做法之前，一樣先把觀念釐清一下。相較於 library 的版本問題，API 的版本就複雜得多，尤其是全球就那麼一套的 service 型態 http API
更是如此。你可以每個版本都保留，也可以只保留最新版本。前者你會花費大量維護的成本，後者沒顧到向前相容的話，遲早會被開發者拋棄...

這篇對岸的文章，是我看過幾篇寫的比較到位的，貼給大家參考: 
[RESTful API版本控制策略](http://ningandjiao.iteye.com/blog/1990004)

文內提到了各種策略，包含:
1. 只保留最新版的 (The Knot) 無版本策略
2. Point-To-Point 點對點的策略，每個版本都同時存在，用戶端自行選擇適當版本
3. Compatible Versioning 相容性版本策略，同 (1), 但是他會保證新版會向前相容。

這邊我就不比較了，我採取的是 (3) 的策略，如這張圖所示，SERVER 隨著時間推進，不斷衍生新版本出來，每個新版本你都要保證能
跟就版本 Client 相容，這麼一來大家都用同一個版本就能相安無事:
![Compatible Versioning](/wp-content/uploads/2016/10/apisdk-03-compatible-versioning.png)

看起來不難嘛，只要相容就好了。說的簡單，實作起來挑戰可不小。想像一下你一但宣告了一個 class, 你寫過的 method 以後遠永不能
把它拿掉，也不能修改 signature, 那是很折磨人的一件事。有時一時手癢，想說先改一下測試看看，等等再改回來，結果就這麼忘掉，
接著就一連串的 commit 跟 push ... 然後這版就出去了! Oh my god..

為了確保這種悲劇不會發生，我把這件事拆成三個 check point，來確保這種問題不會發生 (我假設 client 都透過 SDK 呼叫 API，因此以下 client 我都用 SDK 替代):

1. API contracts, 配合獨立的版本控制權限管控，API 規格的異動，要很明確的能在版控系統中追蹤，也能控制特定人員才有資格異動
2. 要有明確的版本識別機制，確認目前的 API 版本號碼，以及 SDK 的要求最低的 API 版本號碼
3. 版本相容性策略。API 不可能無限期的維持向前相容。所以要明確定義向前相容的範圍及承諾。

這三項彼此之間是環環相扣的，(1) 確保了你的 API 只有再瘦管控的前提下才會被異動，而且有紀錄可循 (Orz, 好像在導 ISO)。(1)有異動
就要變更(2)的版本識別碼，藉著(2)，SDK 就能夠判定他現在能否 **安全** 的呼叫這個 API? 或是在釀成大錯之前，就直接回報 client
正確的訊息。(3)則是長久營運更重要的一環，你很難保證所有的 API 你都不會廢掉，但是要作廢 API 也要有作廢的程序，最重要的就是先宣告
報廢的年限或是規則，讓 client / SDK 有足夠的時間做準備...

接下來，就個別看看這三項應該怎麼進行吧!


# API Contracts

講到第一點 "**contracts**"，不禁就要懷念起 WCF ... WCF 完全就是個以 contracts 發展起來的 remote call 協定，完全可以套用
C# 的特性，你只要把定義 WCF service 的 contracts interface, 獨立成一個 DLL project 就結束了，只要這個 interface 沒有被修改，
你的 API 規格就絕對不會變動。

轉換到 ASP.NET MVC WebAPI 後，雖然程式架構漂亮很多，但是相對的 RESTful 就對 contracts 不是那麼的強調，反而在這邊要實作就有
點頭痛。先來看看延續上一篇的範例程式 (我只列出 signature, 略過實作, 略過非 public method):

```csharp
public class BirdsController : ApiController
{
    public void Head()
    {
        // 略
    }

    public IEnumerable<BirdInfo> Get()
    {
        // 略
    }
    
    public BirdInfo Get(string serialNo)
    {
        // 略
    }
}
```

當然，我可以把這三個會被公開呼叫的 method, 依樣畫葫蘆，定義一個 interface, 然後要求 controller 實作他就可以了。
但是這樣只做了一半，這個 interface 沒有辦法達到 contract 約束甲方乙方的功用。怎麼說? 我沒定義在 interface 上的
method, SDK 一樣可以呼叫啊! 這麼一來 contract 就沒約束力了，有誰會那麼無聊訂規矩限制自己? 這招在多人的團隊上就難以
實現了。

這約束力少了一大半，只約束乙方的合約應該沒人會去簽名吧? XDD

我試過不下十種方法，但是都不漂亮，所以這一段我一度想說跳過去別寫好了 XDD，這段主要的重點在於，尋找適合當作合約 (contract) 
的標的物，找的到的話，後面的管控都會容易許多。Data 的部分很好處理，按照上一篇的做法就夠了這邊我特別針對 API call
來說明。最終被我留下來，當作 API contract 使用的是這個做法，不過這做法其實還不夠無腦，各位參考就好...:

```csharp
/// <summary>
/// 識別是否為 Contract 用途的 interface
/// </summary>
interface IContract { }

/// <summary>
/// Birds API Controller Contract
/// </summary>
interface IBirdsContract : IContract
{
    void Head();

    IEnumerable<BirdInfo> Get();

    BirdInfo Get(string serialNo);
}

public class ContractCheckActionFilterAttribute : ActionFilterAttribute
{
    /// <summary>
    ///  檢查即將要被執行的 Action, 是否已被定義在 contract interface ?
    ///  若找不到 contract interface, 或是找不到 action name 對應的 method, 則丟出 NotSupportedException
    /// </summary>
    /// <param name="actionContext"></param>
    public override void OnActionExecuting(HttpActionContext actionContext)
    {
        Debug.WriteLine(
            "check contract for API: {0}/{1}",
            actionContext.ActionDescriptor.ControllerDescriptor.ControllerName,
            actionContext.ActionDescriptor.ActionName);


        //
        // 搜尋 controller 實作的 contract interface
        //
        System.Type contractType = null;
        foreach (var i in actionContext.ActionDescriptor.ControllerDescriptor.ControllerType.GetInterfaces())
        {
            if (i.GetInterface(typeof(IContract).FullName) != null)
            {
                contractType = i;
                Debug.WriteLine($"- contract interface found: {contractType.FullName}.");
                break;
            }
        }
        if (contractType == null) throw new NotSupportedException("API method(s) must defined in contract interface.");

        //
        // 搜尋 action method
        //
        bool isMatch = false;
        foreach(var m in contractType.GetMethods())
        {
            if (m.Name == actionContext.ActionDescriptor.ActionName)
            {
                isMatch = true;
                Debug.WriteLine($"- contract method found: {m.Name}.");
                break;
            }
        }

        if (isMatch == false) throw new NotSupportedException("API method(s) must defined in contract interface.");
    }
}

[ContractCheckActionFilter]
public class BirdsController : ApiController, IBirdsContract
{
    // 全都略過，同上個 example code
}
```

我的想法很簡單，我為了要嚴格控制 ApiController 一定要遵循 contract 的定義，那麼既然 compile time 無法執行這個檢查，那我就在
runtime 補上這個檢查。雖然不是很完美，不過總是第二道防線。搭配 unit test, 就更有機會抓出漏網之魚。

當然，把這種應該在 compile time 做的事情，搬來放在 runtime 才做，實在是有點 low... 不過接下來後面還會有些價值，有些檢查的確
是在 runtime 才有辦法進行的，這時這套機制就派上用場了。

不過老實說，就我實際的經驗來看，除非有很充足的理由，嚴格管控這件事非做不可，我才會把這套機制搬出來用。不然的話，一般情況下我只會
針對 Data 做這些動作，如同上一篇文章提到的 BirdInfo。畢竟在 runtime 做這件事的成本高很多，尤其是你的 API 如果一秒鐘會被呼叫
上萬次的話... 這部分的最佳化就很重要，加上 cache 是必要的，因為除非改 code, 否則 contract 跟 API 的關係不會改變，每次檢查的動作
若加上 cache, 那效益是很大的，因為 cache 幾乎不需要 expire, 除非 memory 不足自動被踢掉。不過這邊為了清楚表達目的，我
都把這些優化的動作省掉了... 

程式的動作很簡單，我先定義了空白的 interface IContract, 所有用來當作 contract 標示用途的 interface 都必須實做這個 interface.
在這個例子裡 IBirdsContract 就是個例子。

另外，我定義了 ContractCheckActionFilter, 藉這著個 action filter, 每次 webapi 被呼叫時就觸發一次 interface check 的動作。
我這邊只是很簡單的比對 interface name 以及 method name 是否符合而已，實際的 code 比這個複雜多了，我一樣簡化處理... 相信會看我
部落格的讀者應該都了解這些細節，我就偷個懶吧 :D


要確保 API 的相容性，另一個做法是單元測試。TDD 的精神，其中一條就是告訴你，用 test code 來表達你對於規格的認知。先寫出你認為
應該要能執行的 test code, 再來寫程式。等程式寫好後就看看測試會不會過，不論是 test 寫錯，或是程式本體有 bug, 總之修正到能通過
測試為準。

這時，如果你把所有需要被呼叫的 API 都寫成 unit test, 那麼 unit test 也可被當成 "合約" 的一種。不過這邊干擾就比較多。unit test
修正時，可能是 test code 寫錯，不一定每次都是 API 異動造成的。這時從版本異動紀錄要反映到 API 的規格異動紀錄，效果就差很多了。
我就說過我試過不下十種方式了 XD，不過都沒有我覺得較完美的做法，我甚至連 build 後的 check tools 都寫過了 XDDD。這些方法
再撩下去也沒甚麼意義，因此這段就先到此為止。各位可已挑選合適的做法，或是回到傳統的做法，靠文件及 code review 來要求這件事。

為何我要花那麼大的功夫去控制 API contract 這件事? 因為接下來的要求 "向前相容"，很簡單，就是你的 API 只能多不能少。你透過 HTTP 傳遞的
參數也是只能多不能少。原本就有的東西你通通都不能改，不能拿掉也不能改變型別。

這些限制如果放大到整套系統，那一定會有人疏忽掉，加上沒有式當的 review 機制或是檢查工具，靠人腦來做一定會出問題。因此我前面才會花那麼
大的功夫先把 contract 這件事情做好。當這些問題簡化成一個 interface, 那後面就很簡單了。你只要把握一個原則，改變這個 interface 就是
只增不減。


# API / SDK Versioning




# Compatible Policy


(版本 policy)




# References

[Web API 版本控制的几种方式](http://blog.csdn.net/hengyunabc/article/details/20506345)  
[RESTful API版本控制策略](http://ningandjiao.iteye.com/blog/1990004)
[An API Definition As The Truth In The API Contract](https://apievangelist.com/2014/07/15/an-api-definition-as-the-truth-in-the-api-contract/)
[swagger](http://swagger.io/)
[ASP.NET Web API Help Pages using Swagger](https://docs.asp.net/en/latest/tutorials/web-api-help-pages-using-swagger.html)