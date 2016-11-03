---
layout: post
title: "API & SDK Design #2, 設計專屬的 SDK"
categories:
- "專欄"
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: API & SDK Design"
- "系列文章: 架構師觀點"
tags: ["API", "SDK", "系列文章", "ASP.NET", "架構師"]
published: true
comments: true
redirect_from:
logo: //wp-content/uploads/2016/10/apisdk-02-socket.jpg
---
[上一篇](/2016/10/10/microservice3/)出來後，才發現，原來不是每個人都清楚 API 跟 SDK 的差別... 接下去之前我就花點篇幅來說明一下。
這個分不清楚的話實在有點囧啊，以前在本機上，這可能幾乎是一樣的東西，但是到了分散式的環境就不是那麼一回事..。

我這系列打算從 [上一篇](/2016/10/10/microservice3/) 介紹 client side 如何用 C# 呼叫 Http API 的技巧，延續到如何開發搭配的 SDK 設計，
以及 web api 在正式上線時必須考量的安全、效能、確保介面的相容性，可靠性等等設計。不過當你的 API 要正式
發布給其他人使用時，要面臨的就遠遠不止設計跟開發層面而已，還會有線上維運等問題，這邊我也會介紹一下 Azure
上的 [API App Service](https://azure.microsoft.com/zh-tw/services/app-service/api/), 
還有 [API Management](https://azure.microsoft.com/en-us/services/api-management/)。

範例程式: 請從 GitHub 下載，本篇的內容對應到 [dev-SDK 分支](https://github.com/andrew0928/SDKDemo/tree/dev-SDK)

![](/wp-content/uploads/2016/10/apisdk-02-socket.jpg)  
(sorry, 這圖找不到原圖出處, 知道的請通知我，我再補上~)

<!--more-->

{% include series-2016-microservice.md %}


# 什麼是 "API"?

**API**: Application Programming Interface 的縮寫，我把重點擺在第三個字 "I" (interface) 上面。
真的要嚴謹的定義的話，API 只是告訴你某個服務，或是某個元件，提供甚麼樣的 "方式" 讓你去取用他的功能或服務。
因此他只是個溝通方式的定義而已。跟誰溝通? 跟你的程式 (Application)。用甚麼方式溝通? 透過你的程式撰寫 (Programming)
所使用的溝通介面 (Interface)。

這樣聽起來有點抽象，要具體說明的話，我常愛舉一個例子，介面定義這件事，在硬體的領域用的比軟體早太多了。因為硬體比軟體
更難更改及更新，因此事先定義嚴謹的規範及介面定義是很重要的。舉凡我們家裡到處都有的插座，到電腦的 USB，HDMI，網路用
的 RJ45 等等都是 "Interface"。

這些 "Interface" 通常都會由廠商，或是有公信力的第三方組織，如 IEEE 等來制定規範。拿最簡單的電源插座來說，台灣政府
會規範台灣地區的標準，包含插座的規格，還有輸送的電壓等等。有了這樣的規範，台電就知道要輸送什麼規格的電力到每一戶家裡。
建商也知道要安裝甚麼樣的插座，而電器廠商也知道要配置什麼規格的插頭，取得什麼規格的電力，來驅動電器。

另一個常見的例子就是 USB。按照規格，主機板廠就能提供符合 USB interface 的主機板，而周邊設備廠商，如滑鼠，就能
生產 USB 規格的滑鼠，只要插上電腦就能使用。在這邊若拿軟體開發來對應，API 就像是 USB 的規範一樣，只是個紙上的定義。
而主機板就像是 API 後面提供服務的 SERVER，而周邊設備廠商就像開發團隊，滑鼠就像它們開發出來的應用程式 (APP)。



# 什麼是 "SDK"?

**SDK**: Software Development Kit 的縮寫，一樣重點我擺在最後的 "K" (Kit) 上面。
SDK 的意思就是指讓你能順利開發軟體使用的套件。為何會跟 API 扯在一起? 通常 SDK 都是提供 API 的開發者，為了方便
其他的開發者使用他的 API 所提供的對應套件 SDK。

在過去都是單機的時代，API 除了早已存在 OS 內的 System API 之外，其他的 API 通常都需要你先在本機上安裝某些套件
之後才能使用，以 Microsoft 為例，就會有 XXXX redistributed 套件讓大家下載安裝 (一般使用者)。而如果你是開發者，
就會有 XXXX SDK 可以下載安裝。SDK 除了 redistributed 套件的內容之外，還會附上文件，vs template, sample code,
甚至搭配一些配套的工具。

現在雲端時代，就不大一樣了。API 可能已經是泛指某個雲端上提供的 HTTP API / REST API。服務老早就存在那邊，甚至文件
也都放在網站上了，所以單純的 "使用者" 不需要安裝任何東西，只要你看的懂文件，熟悉 HttpClient 就可以呼叫使用了。這時
SDK 的存在目的就有點不同了，他可能是為了讓你更方便的使用 API 而包裝的 LIBRARY，當然也可能搭配其他的工具及 sample code
等。

既然 SDK 可能會包含某些 Library, 那麼他就會是跟你使用的 OS, 程式語言，開發平台等等有關聯。舉個例子來說:

## Microsoft Azure SDK

Microsoft 在 Azure 上面提供了相當多的 PaaS (Platform As A Service) 的服務，自然也有很多的 API 給所有開發者使用。
不過寫過 HttpClient 的人就知道，看完 API DOC 後，你光是要成功的呼叫 API，可能就要寫十幾行 code 了，SDK 裡面附上的
Library 就能讓你簡化這些千篇一律的呼叫動作。其他有些 client 端就能完成的運算或是檢查，效能的最佳化，甚至有些動作可以
在 client side 先行 cache 的部分，都有可能在 SDK 就處理掉。

看看 Azure SDK 的[下載網址](https://azure.microsoft.com/zh-tw/downloads/)吧! 幾種主流的開發環境都有提供了 (.NET, Java, Node.js ... 等等)。

## Flickr SDK

再看第二個例子 Flickr。Flickr 是廣受使用者歡迎的相片服務，他也提供了完整的 API。在他的 API [說明頁面](https://www.flickr.com/services/api/)
下方就有個 "API 開發工具" 專區，放的就是各個平台的 SDK，包含 Flash (Action Script), C, Go, Java, .NET ... 等等。
這些 SDK 甚至不是由 Flickr 官方維護的，很多連結都是連到 GitHub 上面的 open source project.


# YOUR FIRST SDK!

定義搞清楚後，接下來就繼續延續[上一篇](/2016/10/10/microservice3/)文章的範例程式了。

> Source Code 一樣可以直接從 GitHub 上面拉下來看，不過這篇的進度
> 請參考 [dev-SDK 分支](https://github.com/andrew0928/SDKDemo/tree/dev-SDK). 隨著文章一路寫下去，Source Code 也會隨著一直修改，如果你一直抓最新版的，應該會跟文章內容對不起來..
> 請特別留意。

上次的 Source Code 有兩個 projects, 分別是:
1. ```Demo.ApiWeb```  
  提供 API service 的 Web App
2. ```Demo.Client.ConsoleApp```  
  呼叫 API 的 console application

(2) 的部分，我只列片段就好，全列實在太長了... @@

```csharp
/// <summary>
/// 一般寫法，直接呼叫 HttpClient 分多次讀取資料分頁
/// </summary>
static void ListAll_DirectHttpCall()
{
    HttpClient client = new HttpClient();
    client.BaseAddress = new Uri("http://localhost:56648");
    
    int current = 0;
    int pagesize = 5;

    do
    {
        Console.WriteLine($"[info] loading data... ({current} ~ {current + pagesize}) ---");
        HttpResponseMessage result = client.GetAsync($"/api/birds?$start={current}&$take={pagesize}").Result;

        var result_objs = JsonConvert.DeserializeObject<Dictionary<string, string>[]>(result.Content.ReadAsStringAsync().Result);


        foreach (var item in result_objs)
        {
            // filter: 調查地點=玉山排雲山莊
            if (item["Location"] != "玉山排雲山莊") continue;
            ShowBirdInfo(item);
        }

        if (result_objs.Length == 0) break;
        if (result_objs.Length < pagesize) break;

        current += pagesize;
    } while (true);
}
```

這段 code, 其實都在處理呼叫的細節, 而不是針對真正的問題處理。一開始為了準備 HttpClient 呼叫 API 的細節，就花了好幾行
做準備。成功呼叫後為了順利解析 JSON 的格式，又定義了 class 來讓 Json library 做反序列化的動作。最後為了有效率的分批
取回資料，又搭配了 server paging API + C# yield return, 做了額外的包裝，讓主程式可以用 for-each loop 或是 linq 來
使用資料。這一切就花掉了 150 行的 code.

想像一下，如果你的服務實在太紅了，全球有上萬個不同的開發者，都在使用你的 API。那麼上面的這些 code, 是不是每個人都要做
一次? 也許每個人做的不大一樣，但是應該也都大同小異吧! 我寫軟體最不能忍受的，就是存在兩份以上的 code 做一樣的事情...。
解決方法很單純，不過就是寫個 library, 然後讓大家共用他。

因此，這個 solution, 我就在切出第三個 project, 當作我們的 SDK, 也就是呼叫這個 API 共用的 library. 我做了一些調整，
先進行重構，把我想區隔開的邏輯切開，接著把它拆成獨立的 class library project。 調整後你的 APP 主程式會長的像這個樣子:

```csharp
using Demo.SDK;
using System;
using System.Diagnostics;
using System.Linq;

namespace Demo.Client.ConsoleApp
{
    class Program
    {
        static void Main(string[] args)
        {
            Stopwatch timer = new Stopwatch();
            timer.Start();
            
            // 方法3: 使用 SDK
            ListAll_UseSDK();
            
            Console.WriteLine($"* Total Time: {timer.ElapsedMilliseconds} msec.");
        }
        
        static void ListAll_UseSDK()
        {
            Demo.SDK.Client client = new Demo.SDK.Client(new Uri("http://localhost:56648"));
            foreach(var item in (from x in client.GetBirdInfos() where x.SerialNo == "40250" select x))
            {
                ShowBirdInfo(item);
                break;
            }
        }

        static void ShowBirdInfo(BirdInfo birdinfo)
        {
            Console.WriteLine($"[ID: {birdinfo.BirdId}] -------------------------------------------------------------");
            Console.WriteLine($"        流水號: {birdinfo.SerialNo}");
            Console.WriteLine($"      調查日期: {birdinfo.SurveyDate}");
            Console.WriteLine($"      調查地點: {birdinfo.Location}");
            Console.WriteLine($"     經度/緯度: {birdinfo.WGS84Lon}/{birdinfo.WGS84Lat}");
            Console.WriteLine($"          科名: {birdinfo.FamilyName}");
            Console.WriteLine($"          學名: {birdinfo.ScienceName}");
            Console.WriteLine($"中研院學名代碼: {birdinfo.TaiBNETCode}");
            Console.WriteLine($"        鳥中名: {birdinfo.CommonName}");
            Console.WriteLine($"          數量: {birdinfo.Quantity}");
            Console.WriteLine($"      鳥名代碼: {birdinfo.BirdId}");
            Console.WriteLine($"      調查站碼: {birdinfo.SiteId}");
            Console.WriteLine();
            Console.WriteLine();
        }
    }
}
```

主程式現在看起來就乾淨多了。程式裡面看到的，都是使用 APP 的人應該要處理的細節，包括從 server 取回資料後的篩選動作 (Linq),
以及篩選出來的資料顯示動作。

至於要連線 SERVER 的過程，全部被濃縮成這一行:

```csharp
Demo.SDK.Client client = new Demo.SDK.Client(new Uri("http://localhost:56648"));
```

就好像我們使用 SQL server 一樣，建立好 connection 物件後就可以開始查詢了。至於 SDK project 的部分，來看看 SDK Client:

```csharp
using Demo.SDK;
using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace Demo.SDK
{
    public class Client
    {
        private HttpClient _http = null;

        public Client(Uri serviceURL)
        {
            // do init / check
            this._http = new HttpClient();
            this._http.BaseAddress = serviceURL;
        }

        public IEnumerable<BirdInfo> GetBirdInfos()
        {
            int current = 0;
            int pagesize = 5;

            do
            {
                //Console.WriteLine($"--- loading data... ({current} ~ {current + pagesize}) ---");
                HttpResponseMessage result = _http.GetAsync($"/api/birds?$start={current}&$take={pagesize}").Result;

                var result_objs = JsonConvert.DeserializeObject<BirdInfo[]>(result.Content.ReadAsStringAsync().Result);

                foreach (BirdInfo item in result_objs)
                {
                    yield return item;
                }

                if (result_objs.Length == 0) break;
                if (result_objs.Length < pagesize) break;

                current += pagesize;
            } while (true);

            yield break;
        }

        public BirdInfo GetBirdInfo(string serialNo)
        {
            HttpResponseMessage result = _http.GetAsync($"/api/birds/{serialNo}").Result;
            var result_obj = JsonConvert.DeserializeObject<BirdInfo>(result.Content.ReadAsStringAsync().Result);
            return result_obj;
        }
    }
}
```

我的目的是先讓開發者建立 client 物件後，其餘存取 SERVER 的動作都透過這個 client 來進行，所以 SDK 這個 project 就把
BirdInfo 物件的定義, 還有 HttpClient 使用的細節都封裝了起來，也把 server side paging 的細節用 C# 的 yield return
方式轉譯封裝起來，第一版的 SDK 就完成了。

效果如你所見，使用上不再需要 APP 開發者處理呼叫 API 的細節了。所有想要用我 API 的人，只要拿 SDK 去使用就可以了。當然
前提是你也要用 .NET, 如果你用其他語言 (如 Java), 那如上篇文章類似的動作你還是得照做一次。





# SDK / API 的更新及維護問題?

問題到這邊就結束了嗎? 如果以第一版來說，的確結束了。接下來我們來看看 API 或是 SDK 改版會面臨的問題。我先用一張圖來
描述 APP / SDK / API 三者之間的關係:

![架構圖](/wp-content/uploads/2016/10/apisdk-02-arch.png)

這裡面有四個部分，分別是 APP, SDK, API, SERVER。其中由於到目前為止，API 都只是紙上的 "定義"，所以我用虛線表示。

專案    | 誰負責維護? | 更新時間
-------|-------------|-----------
API    | 原廠        | 立即更新
SERVER | 原廠        | 立即更新
SDK    | 原廠        | 原廠立即發行，開發者決定何時更新至APP
APP    | 開發者      | 開發者決定

好，問題開始浮現出來了。萬一 API 已經不敷使用，或是 API 設計存在問題，需要修正的時候... SERVER 跟 API 是原廠可以
立即處理的，沒有問題。如果對應的 SDK 也需要修改，原廠也可以立即發行，沒有問題。

問題在於 APP 開發者啊，如果他沒辦法立即跟上最新版，則會有一段時間，有使用者用的 APP，是用舊版的 SDK，呼叫新版的 API SERVER。
會造成什麼結果，其實是無法預期的。既然有這種風險，就該在他真的發生之前想辦法去控制他才對。

我舉個例子，假設這次的修正，是調整 BirdInfo 的一個欄位名稱，把 SerialNo 改成 BirdNo, 我們只改 SERVER，但是不改 SDK，看看
會發生什麼事情?

修改前: Demo.ApiWeb/Models/BirdInfo.cs

```csharp
public class BirdInfo
{
    public string SerialNo { get; set; }
    public string SurveyDate { get; set; }
    public string Location { get; set; }
    // 以下略過
}
```

修改後: Demo.ApiWeb/Models/BirdInfo.cs

```csharp
public class BirdInfo
{
    public string BirdlNo { get; set; }
    public string SurveyDate { get; set; }
    public string Location { get; set; }
    // 以下略過
}
```

真糟糕，雖然不會有錯誤，但是程式執行結果也不正確了。一筆資料都查不出來...

```LOG
* Total Time: 1932 msec.
Press any key to continue . . .
```

這個問題直到 SDK 對應的 BirdInfo 定義也跟著更新後才解決:

```LOG
[ID: B0443] ----------------------
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


* Total Time: 295 msec.
Press any key to continue . . .
```

如果這是 real case, 那麼緊急解決線上的問題，到這裡應該告一段落了。不過更新的問題一定會碰到，要徹底解決
這問題的話，還是得從架構設計上著手。這過程我抓了兩個關鍵的原因，需要從架構設計面解決:

1. API 的定義，必須有具體 (code 化) 的表達方式，來確保兩端的定義是一致的
2. 向前相容的問題處理，在 API 定義異動時，sdk 要有能力偵測並且正確的回應

接下來就針對這兩點，我們來看看怎麼持續改進 SDK 的 implementation



# API: APP 與 Service 之間簽訂的合同

不知各位有無留意到這細節? 前面的案例調整了 BirdInfo 這資料格式的定義，導致 service 端 (```Demo.ApiWeb```) 與 SDK 端 (```Demo.SDK```),
都需要 **手動** 的調整 code 去配合。手動調整事小，沒有一個機制來約束，確保這件事正確無誤完成事大。這邊我很愛用的機制，就是以前
使用 [WCF](https://msdn.microsoft.com/en-us/library/ms731082(v=vs.110).aspx) (windows communication foundation) 學來的技巧: 制定合約 (contract)

對比到現實世界，接案子時都會簽合約，雙方約定的事項條列在上面，之後一切按照合約條款進行，這是現實世界的規矩。
套用到這邊也一樣，API 的定義也是講一樣的事情。在 .NET 裡面，你可以用 interface, 或是定義 data object 之類的方法
讓前後端共用，編譯器就能幫你做完後面的檢查及驗證等等苦工。只要編譯能通過，就代表雙方是符合合約規範的。

後面的例子，我會把 API 定義的部分，再拆成獨立的 project: ```Demo.Contracts``` 。將來，除非你的 API 要正式異動，否則
就不要去改這個 project. 在板控系統上的紀錄，這個 project 的任何異動，就視同 API 的修訂。在我們團隊實際的運作也是如此，
因此這個 project 通常會限定異動的權限，必須是 architect, 或是 team leader, product owner 之類的角色才有權限調整。

原本的架構，調整後變成這樣，前後端都必須依照 contracts 的約定，來進行溝通:

![API service contract](/wp-content/uploads/2016/10/apisdk-02-contracts.png)


首先，在整個 solution 內新增 ```Demo.Contracts``` 這個 class library project, 每個其他的 project 加入 reference. 
接著就把需要統一規範的 interface or data contract 搬過來。

第一個要搬移的，就是前面案例碰到的 ```BirdInfo.cs```，分享一下我調整的過程，可以最輕鬆的完成這件事:

1. 由於改專案，我希望同時調整 namespace. 因此我先個別在兩個專案內把 BirdInfo 這 class 的 namespace 改成 Demo.Contracts, 
透過 refactory 功能可以自動修正所有使用到他的 code
2. 完成 (1) 之後，再把它搬到 Demo.Contracts project 內，由於 namespace 早就先改好了，所以只要單純的搬移 code
3. 調整 projects 之間的 reference, 原本的 project 都加上 Demo.Contracts 的參考，重新編譯確認無誤後就完成了。

這個過程中，能夠善用 refactory 的話，可以替你節省不少力氣，否則你就要搬完 code, 改完 reference 後，編譯看看有多少 error
再一條一條修改。修正後的 solution 結構，長的像這樣:

![](/wp-content/uploads/2016/10/apisdk-02-solution-structure.png)



# SDK client interface: APP 與 SDK 之間簽訂的合同

接下來，很容易被忽略掉的一點，就是 APP 與 SDK 的相容性。還記得前面的表格嗎? SDK 是原廠維護的，而 APP 是開發者維護的。
原本 APP 應該直接按照 API 規範來使用 SERVICE 的，所以之間的合約只要處理 API 就夠了。但是 SDK 替 APP 解決了這段問題，
因此 APP 開發者真正要面對的規範，就往前提到 APP 與 SDK 之間了。

講具體一點，就是 SDK 有任何異動，是否能維持 APP 的相容性? 這邊的相容性，我分成幾個情況來說明:

1. APP 只要更新 SDK DLL，APP 不需要重新編譯
2. APP 需要更新 SDK 及重新編譯，不需要改 Code
3. SDK 大版本更新，APP 需要配合 SDK 重新調整 Code

一樣，我們用同樣的技巧，訂定 SDK contracts, 來解決 APP 跟 SDK 之間的問題。架構圖再調整一下，變成這樣:
 
![sdk contract](/wp-content/uploads/2016/10/apisdk-02-sdk-contracts.png)

Demo.Contracts 我也增加了 SDK Client interface:

```csharp
namespace Demo.Contracts
{
    public interface ISDKClient
    {
        IEnumerable<BirdInfo> GetBirdInfos();
        BirdInfo GetBirdInfo(string serialNo);
    }
}
```

原本的 Demo.SDK.Client 配合調整，同時我也改成 Factory Pattern, 控制 SDK Client 產生的過程

```csharp
namespace Demo.SDK
{
    public class Client : ISDKClient
    {
        private HttpClient _http = null;

        public static ISDKClient Create(Uri serviceURL)
        {
            return new Client(serviceURL);
        }

        private Client(Uri serviceURL)
        {
            // do init / check
            this._http = new HttpClient();
            this._http.BaseAddress = serviceURL;
        }

        public IEnumerable<BirdInfo> GetBirdInfos()
        {
            // 略
        }

        public BirdInfo GetBirdInfo(string serialNo)
        {
            // 略
        }
    }
}
```

最後 APP 呼叫端的 Code, 只改了取得 client 的部分。原本是:

```csharp
Demo.SDK.Client client = new Demo.SDK.Client(new Uri("http://localhost:56648"));

// Do something...
```

修改後變成:

```csharp
ISDKClient client = Demo.SDK.Client.Create(new Uri("http://localhost:56648"));

// Do something...
```

一樣，這樣以後就有一樣的效果了。除非這個 interface 內容有任何異動，否則你就再也不需要擔心 interface 異動造成問題了。


# 結論

到目前為止，整個 API service 的開發及部署架構已經出來了。除了 Demo.Client.ConsoleApp 之外，其他都是原廠的
API service 開發團隊負責的。隨著 API 的版本推進，不斷的 build solution, 不斷的 deployment, 做好 CI / CD
就沒問題了。

SDK 到這邊就結束了嗎? 還沒有... 下一篇要接著來講 API 的版本控制，及如何做好向前相容的版本管理。敬請期待 :D

----
>
> 最後補充一下，這邊說明的作法，我都已不需要太多外加的 framework, 或是套件為主，盡可能的自己實作。原因很簡單，倒不是
> 說要自己發明輪子，而是不經過這樣的過程，你 (尤其是有打算朝架構師發展的朋友) 很難徹底理解為什麼要這樣做的原因。理解之後
> 你可以在適當的領域，挑選適合的 framework 來使用。  
>
> 比如這篇提到的 API 規範，我用 .NET 的 interface 來實作，實際上有其它的技術已經可以做好這件事了 (如 [swagger](http://swagger.io/) 等)。
> [上一篇](/2016/10/10/microservice3/)講的 server side paging + yield return, 你一樣也可以找到現成的 ODATA 來取代。甚至更早的一系列文章，講到 API key，
> 我用了 AES 數位簽章的方式來實作也是。實際使用時，你可以選擇一樣觀念做出來的 JWT... 這些案例很多，我就不一一細說。
> 如果你是實際上的專案需要，可以考慮使用這些現成的框架。成熟的框架可以解決很多實際上會碰到的問題，但是自己土炮一次則可以
> 讓你了解框架為何耀這要做的原因跟理由。  
>
> 之前在 facebook 上面曾經分享過，現在的技術發展太快了，不論做什麼事都有一堆框架 (framework) 可以選擇。年輕的工程師
> 沒有足夠的時間跟經驗，從基礎開始學起，一開始就得面對龐大的框架，往往分不出甚麼是基礎，什麼是 platform / language, 什麼
> 是 framework (舉例來說，javascript engine / dom / jquery / react / vue ... 之間的關係你說的清楚嗎?)。當面臨
> framework 的世代交替時，換到下一個新的 framework 能留下的經驗跟能力就很有限了，碰到 framework 不足的部分，或是根本
> 都還沒有適合的 framework 時就會束手無策。  
>
> 我這種年紀的傢伙比較幸運一點，當年還沒這麼多 framework, 我還有機會把基礎學好再來研究 framework, 因此現在看到不同的
> framework, 我還能保有選擇跟理解的能力，碰到不足的部分我也有能力找出解法。我希望把這些經驗整理下來，分享給需要的朋友們。
>
