---
layout: post
title: "API & SDK Design #3, API 的向前相容機制"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: API & SDK Design"
- "系列文章: 架構師觀點"
tags: ["API", "SDK", "microservice", "系列文章", "ASP.NET", "架構師"]
published: true
comments: true
redirect_from:
logo: /wp-content/uploads/2016/10/apisdk-03-gandalf.jpg
---

上一篇意外的受歡迎，那麼續集就不富堅了，sample code 準備好就開始動工...

![You shall not pass](/wp-content/uploads/2016/10/apisdk-03-gandalf.jpg)

這篇要講向前相容，不知為何我就直覺的聯想到甘道夫對抗炎魔的場景了 XDD，如果你的 API 沒做好這件事，那麼使用你服務的 APP 結果就會...

## "You shall NOT pass!"

講完 API / SDK 之間當下的約定，接下來來講講 API 跟 SDK 之間的承諾吧! 
當下的約定，會保證當下的 API 跟 SDK 可以搭配運作，然而承諾，則是保證當下的 API 能夠跟過去某個時間以後的所有版本 SDK 都能夠
搭配，這個很考驗架構師的功力了。一個不小心，過去某個不知名的版本就給你出問題了。負責開發維護 API 的人，該怎麼確保這種問題不會
發生?

<!--more-->

# 導讀

一個很大的主題，被我分成好幾篇，我的主軸還是以微服務架構 (microservices) 為主軸，我會分三個主題陸續寫下去..
前面標示 (計畫) 的意思，代表這篇的內容還沒生出來... 請大家耐心等待的意思:

1. 微服務架構(概念說明)
  - [微服務架構 #1, WHY Microservices?](/2016/09/15/microservice-case-study-01/)
  - (計畫) 如何切割微服務的邊界?

2. 微服務架構(實做範例)
  - [微服務架構 #2, 按照架構，重構系統](/2016/10/03/microservice2/)

3. 實做微服務的必要技術: API & SDK Design
    1. [API & SDK Design #1, 資料分頁的處理方式](/2016/10/10/microservice3/)
    2. [API & SDK Design #2, 設計專屬的 SDK](/2016/10/23/microservice4/)
    3. (本篇) API & SDK Design #3, API 的向前相容機制
    4. (計畫) #4, case study, API 異動 & SDK 的最佳化
    5. (計畫) #5, case study, API hosting & API manager on Azure
    
4. (計畫) 微服務架構(部署流程)
  - (計畫) 容器化的部署
  - (計畫) 部署案例 - in place upgrade, using windows container

看來離全部完成還有很久，各位請耐心等待... :D 先來看這篇 API 的向前相容機制!

# 碎碎念: API 的版本策略

在講做法之前，一樣先把觀念釐清一下。相較於 library 的版本問題，API 的版本就複雜得多，尤其是全球就那麼一套的 service 型態 http API
更是如此。你可以每個版本都保留，也可以只保留最新版本。前者你會花費大量維護的成本，後者沒顧到向前相容的話，遲早會被開發者拋棄...

這篇對岸的文章，是我看過幾篇寫的比較到位的，貼給大家參考: 
[RESTful API版本控制策略](http://ningandjiao.iteye.com/blog/1990004)

文內提到了各種策略，包含:
1. 只保留最新版的 (The Knot) 無版本策略
2. Point-To-Point 點對點的策略，每個版本都同時存在，用戶端自行選擇適當版本
3. Compatible Versioning 相容性版本策略，同 (1), 但是他會保證新版會向前相容。

這邊我就不比較了，我採取的是 (3) 的策略，如這張圖所示，SERVER 隨著時間推進，不斷衍生新版本出來，每次都只保留新版本，同時要保證能
跟舊版本的 Client 相容，這麼一來大家都用同一個版本就能相安無事:
![Compatible Versioning](/wp-content/uploads/2016/10/apisdk-03-compatible-versioning.png)

看起來不難嘛，只要相容就好了。說的簡單，實做起來挑戰可不小。想像一下你一旦宣告了一個 class, 你寫過的 method 以後遠永不能
把它拿掉，也不能修改 signature, 那是很折磨人的一件事。有時一時手癢，想說先改一下測試看看，結果就這麼忘掉就 commit 跟 push 出去...

為了確保這種悲劇不會發生，我把這件事拆成三個 check point，來確保這種問題不會發生 (我假設 client 都透過 SDK 呼叫 API，
因此以下 client 我都用 SDK 替代):

1. **API contracts**,  
   配合版本控制權限，API 所有規格的異動，要很明確的能在版控系統中追蹤，也能控制特定人員才有資格異動規格

2. **要有明確的版本識別機制**，  
   偵測及確認目前的 API 版本號碼，以及 SDK 的最低要求 API 版本號碼

3. **版本相容性策略**。  
   API 不可能無限期的維持向前相容。所以要明確定義向前相容的範圍及承諾。

這三項彼此之間是環環相扣的，(1) 確保了你的 API 只有在受管控的前題下才會被異動，而且有紀錄可循 (Orz, 好像在導 ISO)。(1)有異動
就要變更(2)的版本識別碼，藉著(2)，SDK 就能夠判定他現在能否 **安全** 的呼叫這個 API? 或是在釀成大錯之前，就直接回報 client
正確的訊息。(3)則是長久營運更重要的一環，你很難保證所有的 API 你都不會廢掉，但是要作廢 API 也要有作廢的程序，最重要的就是先宣告
報廢的年限或是規則，讓 client / SDK 有足夠的時間做準備...

接下來，就個別看看這三項應該怎麼進行吧!


# API Contracts

講到第一點 "**contracts**"，不禁就要懷念起 WCF ... WCF 完全就是個以 contracts 發展起來的 remote call 協定，完全可以套用
C# 的特性，你只要把定義 WCF service 的 contracts interface, 獨立成一個 DLL project 就結束了，只要這個 interface 沒有被修改，
你的 API 規格就絕對不會變動。

轉換到 ASP.NET MVC WebAPI 後，雖然程式架構漂亮很多，但是相對的 RESTful 就對 contracts 不是那麼的強調，反而在這邊要實做就有
點頭痛。先來看看延續上一篇的範例程式 (我只列出 signature, 略過實做, 略過非 public method):

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

當然，我可以把這三個會被公開呼叫的 method, 依樣畫葫蘆，定義一個 interface, 然後要求 controller 實做他就可以了。
但是這樣只做了一半，這個 interface 沒有辦法達到 contract 約束甲方乙方的功用。怎麼說? 我沒定義在 interface 上的
method, SDK 一樣可以呼叫啊! 這麼一來 contract 就沒約束力了。這招在多人的團隊上就難以落實，這約束力少了一大半，只約束
乙方的合約應該沒人會去簽名吧? XDD

我試過不下十種方法，但覺得都不夠漂亮，沒辦法像 WCF contract 一樣，同一個 contract interface 能同時約束 API & SDK 
兩端的實做。所以這一段我一度想說跳過去別寫好了 XDD，這段主要的重點在於，尋找適合當作合約 (contract) 的標的物，找的到的話，
後面的管控都會容易許多。Data 的部分很好處理，按照上一篇的做法就夠了。這邊我特別針對 API call 來說明。最終被我
留下來，當作 API contract 使用的是這個做法，不過這做法其實還不夠無腦，有點複雜，各位參考就好。先看看 code:

```csharp
/// <summary>
/// 識別是否為 Contract 用途的 interface
/// </summary>
interface IApiContract { }

/// <summary>
/// Birds API Controller Contract
/// </summary>
interface IBirdsApiContract : IApiContract
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
        // 搜尋 controller 實做的 contract interface
        //
        System.Type contractType = null;
        foreach (var i in actionContext.ActionDescriptor.ControllerDescriptor.ControllerType.GetInterfaces())
        {
            if (i.GetInterface(typeof(IApiContract).FullName) != null)
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
public class BirdsController : ApiController, IBirdsApiContract
{
    // 全都略過，同上個 example code
}
```

我的想法很簡單，我為了要嚴格控制 ```ApiController``` 對外提供的 API 一定要遵循 contract 的定義，那麼既然無法在 compile time 
執行這個檢查，那我就在 runtime 補上。雖然差了一個層級，並不是很完美，不過總是補上了第二道防線。若再搭配 unit test, 就更
有機會用系統化的方式抓出漏網之魚。

當然，把這種應該在 compile time 做的事情，搬來放在 runtime 才做，實在是有點 low... 不過接下來後面還會有些價值，有些
檢查的確是在 runtime 才有辦法進行的，這時這套機制就派上用場了。

就我實際的經驗來看，除非有很充足的理由，嚴格管控這件事非做不可，我才會把這套機制搬出來用。不然的話，我只會
針對 Data 設計 contract，如同上一篇文章提到的 ```BirdInfo``` 一樣。畢竟在 runtime 做這件事的成本高很多，尤其是你的 API 如果
一秒鐘會被呼叫上萬次的話... 所以實際上戰場時，這部分的最佳化就很重要。加上 cache 是必要的，因為除非 code 有異動, 否則 
contract 跟 API 的關係不會改變，很多運算其實只要做第一次，結果放到 cache 就搞定了, 增加 cache 效益是很大的，因為 cache 完全
不需要 expire, 這邊為了清楚表達目的，我就把這些優化的動作省掉了... 

程式的動作很簡單，我先定義了空白的 interface ```IApiContract```, 所有用來當作 contract 標示用途的 interface 
(如 ```IBirdsApiContract```) 都必須實做這個 interface (```IApiContract```)。

另外，我定義了 ```ContractCheckActionFilter``` 來負責每次 API 被呼叫前的檢查，每被呼叫一次就會觸發一次檢查的動作。
我這邊只是很簡單的比對 interface name 以及 method name 是否符合而已，實際的 code 比這個複雜多了... 相信會看我
部落格的讀者應該都了解這些細節，我就偷個懶吧 :D

要確保 API 的相容性，另一個做法是單元測試。TDD 的精神，其中一條就是告訴你:  

> 用 test code 來表達你對於規格的認知。先寫出你認為
> 應該要能執行的 test code, 再來寫程式。等程式寫好後就看看測試會不會過，不論是 test code 寫錯，或是程式本體有 bug, 總之修正到能通過
> 測試為準。

這時，如果你把所有需要被呼叫的 API 都寫了對應的 unit test, 那麼 test suite 也可被當成 "contract" 的一種。不過這要追蹤的干擾就比較多。
每當 unit test 修正時 (可能是 test code 寫錯) 版本異動紀錄不一定每一筆都是反映到 API 的規格異動紀錄。
因此在控制 API 是否有未授權的異動這件事，效果就差很多了。

前面我就說過，我試過不下十種方式了 XD，不過都沒有我覺得較完美的做法，我甚至連 build 後的 check tools 都寫過了 XDDD。這些方法
再聊下去也沒甚麼意義，因此這段就先到此為止。各位可已挑選合適的做法，或是回到傳統的做法，靠文件及 code review 來要求這件事。

至於為何我要花那麼大的功夫去控制 API contract ? 因為接下來的要求 "向前相容" 的原則很簡單，就是你的 API 定義的介面只能多不能少。
你透過 HTTP 傳遞的參數也是只能多不能少。原本就有的東西你通通都不能改，不能拿掉也不能改變定義。唯有這樣才能確保舊的 SDK 都能
有正確規格的 API 可以呼叫，不會出現不相容的問題 (這邊只討論 API 的 "interface"，若新版的 API 行為不符，或是執行有 bug 則不在這邊
的討論範圍)。

這些限制如果放大到整套系統，那一定會有人疏忽掉，加上沒有式當的 review 機制或是檢查工具，靠人腦來做一定會出問題。因此我前面才會花那麼
大的功夫先把 contract 這件事情做好。當這些問題簡化成一個 interface, 那後面就很簡單了。你只要把握一個原則，改變這個 interface，method 跟
arguments 就是只增不減。


# API / SDK Versioning

接下來，就是版本控制的問題了。我們不大可能每次都逐一記錄每個 method 的 signature 是否有改變，就像版本控制系統一樣，應該都會有個
代號，來代表某一瞬間所有檔案的版本。例如 SVN 的 revision, TFS 的 changeset number, 或是 git 的 history SHA, 都有同樣的作用。
API 我們也可以替他定義版本，例如這是 10.26 版的 API，上個月的是 9.16 版等等。

這邊會討論兩部分，一個是版本編碼的意義，另一個是如何在 API 實際的傳輸過程中告知 SDK 目前被呼叫的 API 版本為何。



## 版本編號的意義

既然工作上都是靠 Microsoft 吃飯的，那我就用 Microsoft 的慣例來說明吧。Microsoft 的慣例是用四個數字，來組成一個版本號碼。
其實定義直接看 MSDN 對於 [System.Version](https://msdn.microsoft.com/zh-tw/library/system.version(v=vs.110).aspx) 
的說明就可以看的出來。以我現在在用的 Visual Studio 2015 為例:

![VS2015 ABOUT](/wp-content/uploads/2016/10/apisdk-03-vs2015-about.png)

14.0.25424.00 就是版本號碼，我節錄上面 MSDN 的一段說明:

> major.minor[.build[.revision]]  
>
> The components are used by convention as follows:  
> **Major**: Assemblies with the same name but different major versions are not interchangeable. A higher version number might indicate a major rewrite of a product where backward compatibility cannot be assumed.  
> **Minor**: If the name and major version number on two assemblies are the same, but the minor version number is different, this indicates significant enhancement with the intention of backward compatibility. This higher minor version number might indicate a point release of a product or a fully
> backward-compatible new version of a product.  
> **Build**: A difference in build number represents a recompilation of the same source. Different build numbers might be used when the processor, platform, or compiler changes.  
> **Revision**: Assemblies with the same name, major, and minor version numbers but different revisions are intended to be fully interchangeable. A higher revision number might be used in a build that fixes a security hole in a previously released assembly.  
>

其實裡面就把版本號碼的定義講得很清楚了。主版本號碼 (major) 不同的話，就代表這是不相容的版本，不用向前相容不同 Major 版號的版本。
而如果只有次版本號碼 (Minor) 不同，則代表兩者是相容的，較高(新)的版本會保證相容於較低(舊)的版本。

至於 Build 跟 Revision, 在這邊其實可以暫時忽略了，Build 不同，代表是同一份 source code, 在不同的環境、參數、設定等等情況下，編譯出來的不同版本。
而 Revision 的不同，則代表是規格上完全相容的兩個版本，差異只在修正內部的 bug, security hole 等等問題而已。這邊其實各位可以是自己的團隊
運作方式決定要不要使用這兩個號碼，不然保留 undefined 就可以了。

所以，回到前一段講的 API contract, contract 的異動該怎麼跟 version 搭配? 其實原則很簡單，只要遵守這幾條規則即可:

1. 如果 contract 不動，則 Major.Minor 通通維持原狀不改變  
2. 如果因為任何需求，異動了 contract, 修改的幅度是只擴充 API，而沒有任何不相容狀況時，Major 不變，Minor 增加  
3. 如果有必要造成不相容的異動，則 Major 必須增加。  
4. 如果發生 (2) 及 (3) 的衝突，例如 API 有某個部分必須廢除，但是又不想大費周章造成不相容的狀況，那通常會
保留要廢掉的 API，但是會標示 ```[Obsolete]```, 註記最快在下次 Major 異動時才能把他去除。  


## 標示 API 版本編號的方式 

前面的版本定義，那是紙上談兵，是團隊運作流程上的規範而已。但是對於 developer 來說，最後總是要反映到 code 上的。實際呈現版本號碼的方式
也是千百種，[這篇文章 "API Versioning"](https://apigility.org/documentation/api-primer/versioning)其實講的很到位，大家可以參考一下。

我自己慣用的方式有兩個，有時必要時會兩者並用:

1. 提供明確的 API，直接明確的取得 API 版本資訊。
2. 在正常的 API call，將版本資訊隨著 return value 一起傳回 SDK。

一般情況下，其實 (2) 就足夠了，如果你只是要參考而已的話。但是如果你想要在 SDK init 階段，還沒有開始呼叫任何 API 之前
就確認版本，那就要補上 (1) 的實做。當然 (1) 跟 (2) 是可以並行的。所以同樣的例子，來看看 sample code 該怎麼調整:

首先，```IBirdsApiContract``` 多加一個 ```Options```, 用來傳回 version string:

```csharp
interface IBirdsApiContract : IApiContract
{
    string Options();

    // 以下省略
}
```

接著，API control 補上實做:

```csharp
    [ContractCheckActionFilter]
    public class BirdsController : ApiController, IBirdsApiContract
    {
        public string Options()
        {
            return "10.26.0.0";
        }

        // 以下省略
```        

最後，對應的 SDK 可以在 constructor 內，直接讀取 version, 同時做必要的判斷 (這次先略過檢查):

```csharp
    public class Client : ISDKClient
    {
        private Client(Uri serviceURL)
        {
            // do init / check
            this._http = new HttpClient();
            this._http.BaseAddress = serviceURL;

            HttpResponseMessage result = _http.SendAsync(new HttpRequestMessage(
                HttpMethod.Options,
                $"/api/birds")).Result;
            var result_objs = JsonConvert.DeserializeObject<string>(result.Content.ReadAsStringAsync().Result);

            Debug.WriteLine($"API service version: {result_objs}");
        }

        // 以下略過
```

這邊我先不檢查 (檢查的規矩後面談)，只在 output window 那邊印出版本號碼。查看 Visual Studio 的 output window 可以看到:

![debug output](/wp-content/uploads/2016/10/apisdk-03-debug-output.png)


# 版本相容性政策 (SDK init 時檢查)

到目前為止一切順利，剩下最後一部分，就是版本的檢查邏輯。

既然要 "檢查" 版本是否相容，那就跟單元測試一樣，要有期望的結果，跟實際的結果。兩者比對就知道是否合乎期待。前面的實做，我們已經可以
取得 API service 實際的版本號碼了，那麼期待的版本號碼應該是什麼?

![Compatible Versioning](/wp-content/uploads/2016/10/apisdk-03-compatible-versioning.png)

最前面提到的 API 版本策略，這張圖要拿出來重新檢視一次。

我們開發的過程中，一定是 API 跟 SDK 同時進行的。由左到右是演進的順序。所以當我們 API 發展到 SV1 時，就會有對應的 SDK C1。
API 擴充新功能，來到 SV2, 對應的 SDK 就會更新到 C2，讓使用 SDK 的 client 可以用的到新功能。

OK, 所以這樣就清楚了，當 API 發展到 SVn 版本時，對應的 SDK Cn 版本也會同時 release。SDK Cn 版本要求的 API 最低版本就是 SVn。
當然可能有更早期發布出去的舊版 SDK C1 也還在運作中，而現在 API 已經升級到 SVn, 必須向前相容於 SV1。我們就可以按照前面講的，
Microsoft 對於版本號碼的定義來檢查。

因此，SDK 的 constructor 我又做了點調整:

```csharp
public class Client : ISDKClient
{
    private Version _require_API_version = new Version(10, 0, 0, 0);
    private Version _actual_API_version = null;

    private Client(Uri serviceURL)
    {
        // do init / check
        this._http = new HttpClient();
        this._http.BaseAddress = serviceURL;

        HttpResponseMessage result = _http.SendAsync(new HttpRequestMessage(
            HttpMethod.Options,
            $"/api/birds")).Result;
        this._actual_API_version = new Version(JsonConvert.DeserializeObject<string>(result.Content.ReadAsStringAsync().Result));

        // do API version check
        if (this._require_API_version.Major != this._actual_API_version.Major) throw new InvalidOperationException();
        if (this._require_API_version.Minor > this._actual_API_version.Minor) throw new InvalidOperationException();
    }
```        

這邊補上了 SDK 期望看到的 API 版本 _require_API_version, 期望的版本號碼直接在 source code 裡面維護。
在 SDK client 被建立起來時，SDK 會主動查詢 server API 的目前版本，然後按照上面的版本原則，確認目前的 SDK 與 API 是否相容? 若不相容
則會丟出 ```InvalidOperationException```，由 Client 決定要如何處理。

實際測試看看，若我把 Server 的 API 版本，從原本的 10.26.0.0 版，改為 12.11.0.0 版，無法跟 SDK 要求的 10.0.0.0 相容，
果然就掛掉了，會出現這 message: 

```
Unhandled Exception: System.InvalidOperationException: Operation is not valid due to the current state of the object.
   at Demo.SDK.Client..ctor(Uri serviceURL) in C:\Users\chicken\Source\Repos\SDKDemo\Demo.SDK\Client.cs:line 38
   at Demo.SDK.Client.Create(Uri serviceURL) in C:\Users\chicken\Source\Repos\SDKDemo\Demo.SDK\Client.cs:line 23
   at Demo.Client.ConsoleApp.Program.ListAll_UseSDK() in C:\Users\chicken\Source\Repos\SDKDemo\Demo.Client.ConsoleApp\Program.cs:line 25
   at Demo.Client.ConsoleApp.Program.Main(String[] args) in C:\Users\chicken\Source\Repos\SDKDemo\Demo.Client.ConsoleApp\Program.cs:line 17
Press any key to continue . . .
```

# 版本相容性政策 (呼叫 API 時檢查)

前面示範的是 SDK init 階段就先做好版本確認的範例。有些情況下，SDK 的 lifecycle 可能比你想像的還久 (例如: SDK Client Create 出來後
可能就被放在 static field，直到 service restart 才銷毀，可能存活的時間長達數個月)，這時在每次呼叫 API 時一起檢查就是必要的
動作了。

在繼續下去之前，我先做一點改變。HTTP 的傳輸過程，就是一次 request 與 response 往返的動作。如果有進一步的溝通，那就是要發動第二次
HTTP request. 如果像前一個例子一樣，等 server 傳回版本號碼回 SDK 後再檢查相容性，那不管結果如何，被呼叫的 API 早已執行過了，檢查
的結果其實已經沒有什麼意義。因此，這邊要改變作法，改為 SDK 直接把期望的版本號碼傳給 API server, 檢查的任務改交由 server 端執行。
甚至將來有可能的情況是，server 可根據 SDK 傳來的要求，做更進一步的相容性調整，決定是否要支援目前這個版本的 SDK。

這邊又再度改了幾個地方，先來看 code。SDK 的部分我們正好可以利用 ```HttpClient``` 設定預設的 ```Request Headers``` 來替每次
的 HTTP request 都加上固定的 header: ```X-SDK-REQUIRED-VERSION```, 告訴 server 這版的 SDK 要求的最低版本:

```csharp
public class Client : ISDKClient
{
    private HttpClient _http = null;

    /// <summary>
    /// 指定這個版本的 SDK，需要對應 API 的最低版本號碼
    /// </summary>
    private Version _require_API_version = new Version(10, 0, 0, 0);

    private Client(Uri serviceURL)
    {
        // do init / check
        this._http = new HttpClient();
        this._http.BaseAddress = serviceURL;
        this._http.DefaultRequestHeaders.Add("X-SDK-REQUIRED-VERSION", this._require_API_version.ToString());

        // 以下略過
```            

這麼一來，所有 SDK 對 server 送出的 HTTP request 就都會附上版本要求的資訊了。API server side 自然也要對應的檢查。
檢查如果要每個 method 都寫一段 check code 那未免也太 low 了，這邊我再度搬出 ```ActionFilter``` 出來用... (其實你願意的話，
把他合併到前面的 ```ContractCheckActionFilter``` 也可以)
所有的 request 對應到的 action 執行之前，都會經過這個 filter 的處理。若在這裡檢查版本就已經不符合的話，會直接丟出 
```InvalidOperationException```:

```csharp
public class SDKVersionCheckActionFilterAttribute : ActionFilterAttribute
{
    public override void OnActionExecuting(HttpActionContext actionContext)
    {
        // step 1, get SDK required version info from HTTP request header: X-SDK-REQUIRED-VERSION
        Version required_version = null;
        foreach(string hvalue in actionContext.Request.Headers.GetValues("X-SDK-REQUIRED-VERSION"))
        {
            required_version = new Version(hvalue);
            break;
        }

        // step 2, get current API version from Assembly metadata
        Version current_version = this.GetType().Assembly.GetName().Version;

        // step 3, check compatibility
        Debug.WriteLine($"check SDK version:");
        Debug.WriteLine($"- required: {required_version}");
        Debug.WriteLine($"- current:  {current_version}");

        if (current_version.Major != required_version.Major) throw new InvalidOperationException();
        if (current_version.Minor < required_version.Minor) throw new InvalidOperationException();
    }
}
```

我埋了點 code, 會在 visual studio 的 output window 留下訊息，等等可以來看看結果。剩下的動作很簡單，就把這個 ```ActionFilter```,
直接標記在 ```BirdsController``` 上面就可以啟用了。這邊補充一下，前面的例子版本號碼還是寫死在 code 上面，這邊我改掉了，直接讀取
這個 Assembly 的版本號碼。要設定版號的話，可以改這檔案 (```~/Properties/AssemblyInfo.cs```) 的內容:


```csharp
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

/*
*   前面的 code 都略過
*/

// Version information for an assembly consists of the following four values:
//
//      Major Version
//      Minor Version 
//      Build Number
//      Revision
//
// You can specify all the values or you can default the Revision and Build Numbers 
// by using the '*' as shown below:
[assembly: AssemblyVersion("10.26.*")]
[assembly: AssemblyFileVersion("1.0.0.0")]
```
這邊是指定 .NET assembly 的 metadata, 編譯出來的 DLL 按右鍵選內容也可以看的到這些資訊。透過這樣的方式，比自己寫死在 code
有額外的好處。通常 build process 都會去 overwrite 這邊的數值，由 build server 統一管控編譯出來的版本號碼。以這邊為例，
我是 development 階段就決定好現在的版本是 10.26 版。後面弄 * 的話，msbuild 會自動替我產生 build 跟 revision number，
就不用我自己傷腦筋了。當一次需要編譯出一整組 assembly 時，又想維持版本號碼是一致的話，從這邊會方便很多。

OK，code 都交代完了，那來看看執行結果。如果我在 SDK 設定 API 最低要求是 10.0.0.0, 而 API server 我指定版本是 10.26.*, 
版本判定是相容的，應該要順利執行才對。來看看執行結果:

```
[ID: B0443] -------------------------------------------------------------
        流水號: 40250
      調查日期: 2013-06-21
      調查地點: 玉山西峰下
     經度/緯度: 120.937047/23.468776
          科名: Reguliidae
          學名: Regulus goodfellowi
中研院學名代碼: 380442
        鳥中名: 火冠戴菊鳥
          數量: 1
      鳥名代碼: B0443
      調查站碼: C37-02-04


* Total Time: 1834 msec.
Press any key to continue . . .
```

程式可以正常執行沒有問題。看看 visual studio 的 output window:

```
check contract for API: Birds/Get
- contract interface found: Demo.ApiWeb.Controllers.IBirdsApiContract.
- contract method found: Get.
check SDK version:
- required: 10.0.0.0
- current:  10.26.6146.30587
```

看起來沒有問題，程式也通過檢查，正常執行。

如果我動一點手腳，我把 SDK 那邊要求的版本，從 10.0.0.0 改為 12.11.0.0 的話，SDK 就無法正常執行了，會直接在 console 上顯示這堆訊息:

```
Unhandled Exception: Newtonsoft.Json.JsonReaderException: Unexpected character encountered while parsing value: {. Path '', line 1, position 1.
   at Newtonsoft.Json.JsonTextReader.ReadStringValue(ReadType readType)
   at Newtonsoft.Json.JsonTextReader.ReadAsString()
   at Newtonsoft.Json.Serialization.JsonSerializerInternalReader.ReadForType(JsonReader reader, JsonContract contract, Boolean hasConverter)
   at Newtonsoft.Json.Serialization.JsonSerializerInternalReader.Deserialize(JsonReader reader, Type objectType, Boolean checkAdditionalContent)
   at Newtonsoft.Json.JsonSerializer.DeserializeInternal(JsonReader reader, Type objectType)
   at Newtonsoft.Json.JsonConvert.DeserializeObject(String value, Type type, JsonSerializerSettings settings)
   at Newtonsoft.Json.JsonConvert.DeserializeObject[T](String value, JsonSerializerSettings settings)
   at Newtonsoft.Json.JsonConvert.DeserializeObject[T](String value)
   at Demo.SDK.Client..ctor(Uri serviceURL) in C:\Users\chicken\Source\Repos\SDKDemo\Demo.SDK\Client.cs:line 39
   at Demo.SDK.Client.Create(Uri serviceURL) in C:\Users\chicken\Source\Repos\SDKDemo\Demo.SDK\Client.cs:line 26
   at Demo.Client.ConsoleApp.Program.ListAll_UseSDK() in C:\Users\chicken\Source\Repos\SDKDemo\Demo.Client.ConsoleApp\Program.cs:line 25
   at Demo.Client.ConsoleApp.Program.Main(String[] args) in C:\Users\chicken\Source\Repos\SDKDemo\Demo.Client.ConsoleApp\Program.cs:line 17
Press any key to continue . . .
```

打開 debug mode 開始 trace, 在 API server 端的 action filter 就已經觸發 exception 了:

[![server exception](/wp-content/uploads/2016/10/apisdk-03-exception-server.png)](/wp-content/uploads/2016/10/apisdk-03-exception-server.png)

這 Exception 會繼續傳遞到前端 SDK，SDK 會接收到 ```HttpClient``` 觸發的 exception:

[![client exception](/wp-content/uploads/2016/10/apisdk-03-exception-client.png)](/wp-content/uploads/2016/10/apisdk-03-exception-client.png)


(原諒我偷懶，寫太多 error handling 的 code, 看起來就會變很阿雜，不適合當 sample code XD)
直接進到 visual studio debug mode 看看 SDK 接到 server 傳回什麼資訊:

```javascript
{
  "Message": "An error has occurred.",
  "ExceptionMessage": "Operation is not valid due to the current state of the object.",
  "ExceptionType": "System.InvalidOperationException",
  "StackTrace": "
     at Demo.ApiWeb.Controllers.SDKVersionCheckActionFilterAttribute.OnActionExecuting(HttpActionContext actionContext) in C:\\Users\\chicken\\Source\\Repos\\SDKDemo\\Demo.ApiWeb\\Controllers\\BirdsController.cs:line 59\r\n
     at System.Web.Http.Filters.ActionFilterAttribute.OnActionExecutingAsync(HttpActionContext actionContext, CancellationToken cancellationToken)\r\n
     --- End of stack trace from previous location where exception was thrown ---\r\n
     at System.Runtime.CompilerServices.TaskAwaiter.ThrowForNonSuccess(Task task)\r\n
     at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)\r\n
     at System.Web.Http.Filters.ActionFilterAttribute.<ExecuteActionFilterAsyncCore>d__0.MoveNext()\r\n
     --- End of stack trace from previous location where exception was thrown ---\r\n
     at System.Runtime.CompilerServices.TaskAwaiter.ThrowForNonSuccess(Task task)\r\n
     at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)\r\n
     at System.Web.Http.Controllers.ActionFilterResult.<ExecuteAsync>d__2.MoveNext()\r\n
    --- End of stack trace from previous location where exception was thrown ---\r\n
    at System.Runtime.CompilerServices.TaskAwaiter.ThrowForNonSuccess(Task task)\r\n
    at System.Runtime.CompilerServices.TaskAwaiter.HandleNonSuccessAndDebuggerNotification(Task task)\r\n
    at System.Web.Http.Dispatcher.HttpControllerDispatcher.<SendAsync>d__1.MoveNext()"
}
```

ASP.NET MVC WebAPI 直接把 ```Exception```, 轉成 JSON 格式傳回 SDK 了，所以如果你想在 SDK 內更精確的處理這些 Error 的話，
知道該怎麼做了吧? 這些 code 我就省下來了 XD。



# 結語

SDK 跟 API 的相容性問題，寫到這裡告一段落。這些細節都處理好之後，其實你的 API / SDK 就有一定的成熟度，可以正式開放給其他
開發者使用了。有了版本相容性的管控機制之後，你的 API 也開始具備能長期營運及升級的挑戰了 :D

下一篇就來探討一下 SDK 要如何最佳化吧。最佳化的過程中可能會有 API 變更的需求，正好直接來演練一下過程中怎麼搭配相容性的機制
怎麼確保舊版 SDK 能順利度過升級的過渡期，看看這篇講的版本控制機制是不是真的能發揮作用吧!

下回預告: API upgrade & SDK optimization

這篇文章提到的所有 source code, 一樣都放在 GitHub, 這篇的進度請參考 dev-VER 這個分支，別跑去看 master 喔，下一篇文章
出來的時候 master 的內容就會跑掉了。我會確保 dev-VER 分支的內容跟這篇文章是同步的。

GitHub: [https://github.com/andrew0928/SDKDemo/tree/dev-VER](https://github.com/andrew0928/SDKDemo/tree/dev-VER)