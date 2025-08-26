![](/images/2016-10-10-microservice3/microservice-webapi-design.jpg)  
(圖片來源: [http://hamidarebai.blogspot.tw/2016/09/building-restful-api-with-aspnet-core.html](http://hamidarebai.blogspot.tw/2016/09/building-restful-api-with-aspnet-core.html))

這篇算是 "微服務架構" 系列文章的外傳... 所以標題稍微改一下 XD!

上一篇講到 "[重構](/2016/10/03/microservice2/)"，不斷的進行重構，直到能夠將模組切割為服務為止。
這篇就接續這個話題，展示一下服務化之後的 API / SDK / APP 之間的關係，以及設計上要顧慮到的細節。我用最常碰到的資料查詢 API 的分頁機制
當作案例來說明這些觀念。資料分頁是個很煩人的東西，不論是在 UI 或是在 API 層面上都是。尤其是 client 端要把
分頁後的資料重新組合起來，就會有越來越多的 **[義大利麵風格](https://zh.wikipedia.org/wiki/%E9%9D%A2%E6%9D%A1%E5%BC%8F%E4%BB%A3%E7%A0%81)** 的 dirty code 被加進來..

這時 SDK 扮演很重要的角色，善用 C# 的 yield return 就能很漂亮的解決這問題。這篇就來示範幾個 API / SDK
的實作技巧 (C#)，之後微服務講到這部份時，可以再回頭參考這篇的內容。

<!--more-->

{% include series-2016-microservice.md %}


# 範例 Data API Service: Server Side Data Paging

這篇的應用範例，我從內政部的 [政府資料開放平台](http://data.gov.tw/) 找了一個 [範例](http://data.gov.tw/node/8340) 來當資料庫，
示範這樣的 API service 該如何設計，以及能動之後，怎麼樣的設計才是良好的 API service ? 觀察過很多台灣的
團隊，往往在這些實作的層面沒有仔細考量，造成維護上的困難。

API 的生態，跟應用軟體的生態不大一樣。很多老闆都會講服務應該快速推出，快速驗證市場需求；這是對的。不過 API 這種東西
的訴求就完全不同，它的使用對象不是 End User, 而是 Developer. Developer 在意的不是 UX (User Experience, [使用者經驗](https://zh.wikipedia.org/wiki/%E4%BD%BF%E7%94%A8%E8%80%85%E7%B6%93%E9%A9%97)), 
而是 DX (Developer Experience - [開發者體驗](https://github.com/geo4web-testbed/topic3/wiki/Developer-Experience))
啊.. DX 講求的是文件、API、SDK、及你提供的服務在 developer 眼裡看起來是否夠優雅? 效能夠好? 穩定可靠? 這篇我主要就是
要探討 DX，因此重點會在 API 的定義跟 SDK 的包裝方式。

前面提到的 data service, 我想會 .NET 的人應該都沒問題吧? 開個 [ASP.NET MVC WebAPI](https://www.asp.net/web-api) 的專案就可以搞定了。這邊我就直接
跳到第一版，提供其他的開發人員查詢台灣鳥類生態觀察的資料。不多說，直接看 code:

> 接下來會有幾篇文章要延續這個範例，code 會不斷的修正。
> 若要參考這篇文章提到的 sample code, 請參考 [dev-API](https://github.com/andrew0928/SDKDemo/tree/dev-API) 這個分支。
> 不介意的話，請給我個 star 鼓勵一下 :D



## DATA FORMAT 說明

為了簡化問題，我沒有使用 database, 也沒使用 entity framework, 直接到政府的開放資料網站, 下載了這份 json 格式的
"特生中心102年繁殖鳥大調查資料集" 資料當作範例。檔案放在 ```~/App_Data/birds.json```, 我貼兩筆資料給大家看一下格式:

```javascript
[
  {
    "SerialNo": "40298",
    "SurveyDate": "2013-06-21",
    "Location": "玉山西峰下",
    "WGS84Lon": "120.939592",
    "WGS84Lat": "23.468244",
    "FamilyName": "Paradoxornithidae",
    "ScienceName": "Fulvetta formosana",
    "TaiBNETCode": "425189",
    "CommonName": "灰頭花翼",
    "Quantity": "1",
    "BirdId": "B0364",
    "SiteId": "C37-02-06"
  },
  {
    "SerialNo": "40297",
    "SurveyDate": "2013-06-21",
    "Location": "玉山西峰下",
    "WGS84Lon": "120.939592",
    "WGS84Lat": "23.468244",
    "FamilyName": "Fringillidae",
    "ScienceName": "Pyrrhula erythaca",
    "TaiBNETCode": "380359",
    "CommonName": "灰鷽",
    "Quantity": "1",
    "BirdId": "B0516",
    "SiteId": "C37-02-06"
  }
  // 後面還有 998 筆資料...
]
```


## API CODE (SERVER) 說明

我開了一個 "Azure Web APP" 類型的 ASP.NET Web Application, 其實就是拿掉大部分用不到的 code, 只保留 webapi 
需要的部份而已。它的好處除了輕快之外，能夠在一般的 windows server 上面執行，也可以直接當成 Azure 的 [API App](https://azure.microsoft.com/en-us/documentation/articles/app-service-api-apps-why-best-platform/) 
丟上雲端 Hosting。實際程式碼我有丟上 [GitHub](https://github.com/andrew0928/SDKDemo/tree/dev-API/) , 請參考 ```Demo.ApiWeb``` 這個 project. 其中關鍵的 ApiController: ```BirdsController.cs``` 內容如下:

```C#
public class BirdsController : ApiController
{
    protected override void Initialize(HttpControllerContext controllerContext)
    {
        BirdInfo.Init(File.ReadAllText(System.Web.HttpContext.Current.Server.MapPath("~/App_Data/birds.json")));
        base.Initialize(controllerContext);
    }

    public void Head()
    {
        System.Web.HttpContext.Current.Response.AddHeader("X-DATAINFO-TOTAL", BirdInfo.Data.Count().ToString());
        return;
    }

    private const int MaxTake = 10;

    public IEnumerable<BirdInfo> Get()
    {
        int start, take;
        if (int.TryParse(this.GetQueryString("$start"), out start) == false) start = 0;
        if (int.TryParse(this.GetQueryString("$take"), out take) == false) take = MaxTake;

        if (take > MaxTake) take = MaxTake;

        System.Web.HttpContext.Current.Response.AddHeader("X-DATAINFO-TOTAL", BirdInfo.Data.Count().ToString());
        System.Web.HttpContext.Current.Response.AddHeader("X-DATAINFO-START", start.ToString());
        System.Web.HttpContext.Current.Response.AddHeader("X-DATAINFO-TAKE", take.ToString());

        IEnumerable<BirdInfo> result = BirdInfo.Data;
        if (start > 0) result = result.Skip(start);
        result = result.Take(take);

        return result;
    }
    
    // GET api/values/5
    public BirdInfo Get(string id)
    {
        return BirdInfo.Get(id);
    }

    private string GetQueryString(string name)
    {
        foreach(var pair in this.Request.GetQueryNameValuePairs())
        {
            if (pair.Key == name) return pair.Value;
        }

        return null;
    }
}

```

## API 呼叫方式說明

我示範的 API service, 只提供兩個功能，傳回格式統一為 JSON:

1. URL: ```~/api/birds?$start={start}&$take={take}```
  **列舉所有的資料**:  
  每次最多傳回 10 筆資料。可用兩個選用的參數指定傳回資料的範圍:
  * ```$start``` 從第幾筆開始回傳 (預設值 0)
  * ```$take``` 傳回幾筆 (預設值 10, 最大值 10)
  除了傳回 JSON 格式的資料之外，也會在 HTTP response header 標註附加資訊:
  * ```X-DATAINFO-TOTAL```: 標示所有的資料共有幾筆
  * ```X-DATAINFO-START```: 標示傳回的資料是從第幾筆開始
  * ```X-DATAINFO-TAKE```:  標示傳回的資料最大筆數
  另外，除了 GET 之外，也支援 HEAD 這 verb, 不會傳回資料，但是會傳回 header, 這情況下只會傳回 ```X-DATAINFO-TOTAL```

2. ```URL: ~/api/birds/{birdid}```
  **直接傳回指定 ID 的那筆資料**:  
  其實這些功能，用 Entity Framework, 加上 [OData](http://www.odata.org/) 就全搞定了，不過這邊這樣做下去就沒意思了，所以我特地
  簡化問題，讓大家看看怎麼自己刻出這功能。研究可以，正式上線的系統還是採用 OData 比較合適..


## APP CODE 說明 (直接使用 HttpClient)

我寫了一個 Console Application, 請參考 ```Demo.Client.ConsoleApp``` 這個 project。 從 Server 用上面說明的 API，自己用 ```HttpClient``` 按照規格呼叫，寫了一個
把全部資料一頁一頁撈回來，自己過濾，只列出觀察地點是 "玉山排雲山莊" 的野生鳥類紀錄資料出來。由於沒有 server side
query support, 所以過濾機制是在 client 做的，每次都必須從頭到尾掃描所有的資料。

我從內政部抓來的資料，剛剛好有 1000 筆，client / server 都在我 local pc 上面 (server 用 iis-express) 執行，
跑出來約要 3000 msec 左右。先來看 code:


```C#
static void Main(string[] args)
{
    Stopwatch timer = new Stopwatch();
    timer.Start();

    // 方法1: 直接用 HttpClient 呼叫 web api
    ListAll_DirectHttpCall();
    
    Console.WriteLine($"* Total Time: {timer.ElapsedMilliseconds} msec.");
}

static Dictionary<string, string> _columns_name = new Dictionary<string, string>()
{
    { "SerialNo",       "流水號" },
    { "SurveyDate",     "調查日期" },
    { "Location",       "調查地點" },
    { "WGS84Lon",       "經度" },
    { "WGS84Lat",       "緯度"},
    { "FamilyName",     "科名"},
    { "ScienceName",    "學名" },
    { "TaiBNETCode",    "中研院學名代碼" },
    { "CommonName",     "鳥中名"},
    { "Quantity",       "數量"},
    { "BirdId",         "鳥名代碼" },
    { "SiteId",         "調查站碼"}
};

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

static void ShowBirdInfo(Dictionary<string, string> birdinfo)
{
    Console.WriteLine("[ID: {0}] -------------------------------------------------------------", birdinfo["BirdId"], birdinfo["CommonName"]);
    foreach (string name in _columns_name.Keys)
    {
        Console.WriteLine(
            "{0}: {1}",
            _columns_name[name].PadLeft(10, '　'),
            birdinfo.ContainsKey(name) ? (birdinfo[name]) : ("<NULL>"));
    }
    Console.WriteLine();
    Console.WriteLine();

}
```

主程式 ```ListAll_DirectHttpCall()``` 中，那個關鍵的 do while loop，共有 20 行，除了花 6 行是印出資料用的之外，其他其實都在處理
分頁的動作，以及篩選出符合條件的邏輯。老實說我最討厭這種 code style, 因為不同目的的 code 都被摻在一起了... 我不要做撒尿牛丸啊..


## APP CODE 說明 (使用 C# yield return)

不知還有沒有讀者記得我好幾年前寫的 "[C# yield, how it work?](/2008/09/18/c-yield-return-1-how-it-work/)" 的文章? 
Orz, 看看日期已經有八年了...  我一直覺的 C# 很多語法甜頭是很實用的，```yield return``` 就是
我最愛用的一個，不但可以解決多執行緒的一些困難，這次連這種遠端 server paging 的問題也能妥善處理.. 上述的主程式 
```ListAll_DirectHttpCall()``` 我換個方式重寫一次，來看看改寫過的 code:


```C#
static void ListAll_UseYield()
{
    // filter: 調查地點=玉山排雲山莊
    foreach (var item in (from x in GetBirdsData() where x["Location"] == "玉山排雲山莊" select x))
    {
        ShowBirdInfo(item);
    }
}

static IEnumerable<Dictionary<string, string>> GetBirdsData()
{
    HttpClient client = new HttpClient();
    client.BaseAddress = new Uri("http://localhost:56648");

    int current = 0;
    int pagesize = 5;

    do
    {
        Console.WriteLine($"--- loading data... ({current} ~ {current + pagesize}) ---");
        HttpResponseMessage result = client.GetAsync($"/api/birds?$start={current}&$take={pagesize}").Result;

        var result_objs = JsonConvert.DeserializeObject<Dictionary<string, string>[]>(result.Content.ReadAsStringAsync().Result);

        foreach (var item in result_objs)
        {
            //Console.WriteLine("ID: {0}", item["BirdId"]);
            yield return item;
        }

        if (result_objs.Length == 0) break;
        if (result_objs.Length < pagesize) break;

        current += pagesize;
    } while (true);

    yield break;
}
```

眼尖的讀者朋友們，看出差異了嗎? 用行數來看，其實沒省多少... 不過藉由 ```yield return```, 我能夠很漂亮的實作 iterator patterns,
把物件巡覽及物件處理的邏輯清楚的切開..，```GetBirdsData()``` 就只要專心負責取回所有的資料。然而資料該怎麼處理? 就留給
主程式 ```ListAll_UseYield()``` 就可以了。

主程式很簡短，只有一個 Linq Query, 查出符合條件的資料，然後用 for-each loop 印出來。乾淨又漂亮的 code，解決了同樣的問題。


改善過的 code, 一眼望去，看起來好像是先把所有資料傳回來，再去一筆一筆過濾? 事實上不是這樣，它依然是按照我們的期望，
一次讀 5 筆，讀完了也處理完了還有需要，才繼續讀後面五筆，直到完成為止。為了確認執行的順序，我做了幾個實驗:


## 結果觀察 - 觀察 API 呼叫與資料處理的交錯執行狀況

上述的 code 可以看到，在 ```GetBirdsData()``` 內每呼叫一次 server API, 就會印一次 "--- loading data ...", 然而前端查到
一筆符合的資料，就會印出一筆。我節錄這個 console app 的輸出結果給大家參考:

```TEXT
--- loading data... (75 ~ 80) ---
--- loading data... (80 ~ 85) ---
--- loading data... (85 ~ 90) ---
--- loading data... (90 ~ 95) ---
--- loading data... (95 ~ 100) ---
[ID: B0368] -------------------------------------------------------------
[ID: B0368] -------------------------------------------------------------
--- loading data... (100 ~ 105) ---
[ID: B0364] -------------------------------------------------------------
[ID: B0443] -------------------------------------------------------------
[ID: B0425] -------------------------------------------------------------
[ID: B0404] -------------------------------------------------------------
[ID: B0404] -------------------------------------------------------------
--- loading data... (105 ~ 110) ---
[ID: B0386] -------------------------------------------------------------
[ID: B0511] -------------------------------------------------------------
[ID: B0405] -------------------------------------------------------------
[ID: B0443] -------------------------------------------------------------
[ID: B0368] -------------------------------------------------------------
--- loading data... (110 ~ 115) ---
[ID: B0368] -------------------------------------------------------------
[ID: B0386] -------------------------------------------------------------
[ID: B0405] -------------------------------------------------------------
[ID: B0425] -------------------------------------------------------------
[ID: B0405] -------------------------------------------------------------
--- loading data... (115 ~ 120) ---
[ID: B0386] -------------------------------------------------------------
[ID: B0404] -------------------------------------------------------------
[ID: B0443] -------------------------------------------------------------
[ID: B0425] -------------------------------------------------------------
[ID: B0404] -------------------------------------------------------------
--- loading data... (120 ~ 125) ---
```

為了節省篇幅，我只節錄部分 (75 ~ 125 的資料區間)，同時我把顯示資料內容的部分都拿掉了，只顯示資料的 ID。
仔細看看這段 LOG:

```TEXT
--- loading data... (95 ~ 100) ---
[ID: B0368] -------------------------------------------------------------
[ID: B0368] -------------------------------------------------------------
--- loading data... (100 ~ 105) ---
```

我們可以看到，呼叫 API 跟處理資料，真的是交錯進行的。```GetBirdsData()``` 查詢到 95 ~ 100 筆的時候，這五筆資料就立即
傳回 for-each loop 處理了，結果其中有兩筆資料符合，被列印了出來。之後處理完畢，接著又繼續 loading 後面五筆 100 ~ 105 的資料..



## 結果觀察 - 中斷迴圈，資料載入狀況觀察

如果我程式調整一下，只搜尋到我要的那一筆之後就離開 for-each loop，那它會聰明的立即停止後續的 server API 呼叫嗎?

主程式改成這樣再測試一次看看:

```C#
static void ListAll_UseYield()
{
    // filter: ID = B0368，找到之後離開 for-each loop
    foreach (var item in (from x in GetBirdsData() where x["SerialNo"] == "40250" select x).Take(1))
    {
        ShowBirdInfo(item);
    }
}
```

執行的結果:

```TEXT
--- loading data... (0 ~ 5) ---
--- loading data... (5 ~ 10) ---
--- loading data... (10 ~ 15) ---
--- loading data... (15 ~ 20) ---
--- loading data... (20 ~ 25) ---
--- loading data... (25 ~ 30) ---
--- loading data... (30 ~ 35) ---
--- loading data... (35 ~ 40) ---
--- loading data... (40 ~ 45) ---
--- loading data... (45 ~ 50) ---
[ID: B0443] -------------------------------------------------------------
* Total Time: 266 msec.
Press any key to continue . . .
```

看起來的確很精確的，逐頁讀取資料，逐頁過濾後，我用 Linq 要求只取前面 1 筆 ( ```.Take(1)``` )，真的後面的 API 就不會再呼叫了。
這是否是因為我 Linq Query 下的好的關係? 如果我 Query 一樣是查詢所有資料，但是是用 C# code, 在適當時間 break for-each loop,
結果是否會不同?

很簡單，實驗一下就知道了:

```C#
static void ListAll_UseYield()
{
    // filter: ID = B0368，找到之後離開 for-each loop
    foreach (var item in (from x in GetBirdsData() where x["SerialNo"] == "40250" select x))
    {
        ShowBirdInfo(item);
        break;
    }
}
```

結果跟上一段一模一樣，也是達成目的後就退出，沒有絲毫多於的浪費:

```TEXT
--- loading data... (0 ~ 5) ---
--- loading data... (5 ~ 10) ---
--- loading data... (10 ~ 15) ---
--- loading data... (15 ~ 20) ---
--- loading data... (20 ~ 25) ---
--- loading data... (25 ~ 30) ---
--- loading data... (30 ~ 35) ---
--- loading data... (35 ~ 40) ---
--- loading data... (40 ~ 45) ---
--- loading data... (45 ~ 50) ---
[ID: B0443] -------------------------------------------------------------
* Total Time: 271 msec.
Press any key to continue . . .
```


## yield return 應用小結  

這邊的案例，我覺得是 ```C# yield return``` 的應用上，很經典的一個使用案例。這也是我刻意不用 [Microsoft OData](http://odata.github.io/)
那套做法的目的。通通都包起來的話，各位可能永遠都不曉得原來 ```C# 的 yield return``` 這麼好用。而且雖然 OData 是
個標準，但是我相信你也不是每次都能用的到的。有太多 data api, 並沒有按照 OData 的規範去實作，很多例子
就像這次 sample code 一樣，API 有提供分頁功能，但是沒有按照 OData 標準來進行，於是你得像這樣自己實作..

其實這次的實作，原理已經跟 Microsoft 對 OData 的作法很類似了。有差異的部份是，Microsoft 在 Server 端
用的是 [IQueryable](https://msdn.microsoft.com/en-us/library/bb351562(v=vs.110).aspx) interface, 
而不是 [IEnumerable](https://msdn.microsoft.com/zh-tw/library/system.collections.ienumerable(v=vs.110).aspx) interface. 
兩者的差別是，一個可以取得 QueryProvider,
直接給它更明確的查詢條件，而 IEnumerable 則很單純，只能單向的巡覽資料而已，不會有甚麼建立索引，或是查詢
最佳化的機會。

我找兩篇文章給大家參考一下，有這兩個 interface 能力上的差別:  
* [IEnumerable與IQuerya搞搞就懂](https://dotblogs.com.tw/wasichris/archive/2015/03/04/150633.aspx)
* [關於IQueryable特性的小實驗](http://blog.darkthread.net/post-2012-10-23-iqueryable-experiment.aspx)  - 黑暗執行緒

看的出來，實作 ```IEnumerable``` interface, 就只能 looping 掃描每一筆資料 (類似 SQL table scan)。而前端的 Linq, Microsoft 也有特別處理，
能夠把 Linq Query 的條件，透過 OData 定義的參數送到後端，直接在 server side query 就過濾掉不必要的
資料，連傳遞到前端都不用了，效率更佳! 因此要是你的使用環境能配合，有機會使用 OData, 不用考慮了, 用就對了!