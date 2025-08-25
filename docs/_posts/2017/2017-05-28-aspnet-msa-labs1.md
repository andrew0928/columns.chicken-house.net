---
layout: post
title: "容器化的微服務開發 #1, IP查詢架構與開發範例"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps"]
published: true
comments: true
redirect_from:
logo: /images/2017-05-28-aspnet-msa-labs1/containerize-all-your-apps-meme.jpg
---

總算把包含架構與觀念的實際案例篇寫完了，前面也寫完了微服務化一定會面臨的 API 開發設計問題，那接下來可以開始
進入有趣一點的部分了。微服務架構是由很多獨立的小型服務組合而成的，這次我們直接來看看每一個服務本身應該怎麼開發。

![](/images/2017-05-28-aspnet-msa-labs1/containerize-all-your-apps-meme.jpg)
* 這張圖真是百搭啊...

這篇既然要講到實作，那就不能不提讓微服務可以實現的容器技術。我一直覺得很可惜的是，不管國內或國外的文章，以開發者的
角度來介紹容器技術的案例實在不多啊 (還是我關鍵字下的不對? @@) 過去的觀念裡面，都是強調 container 有多好用，但是
看來看去都是把現有的 apps 重新用 container 打包及部署。DockerCon 2017 正式介紹了 LinuxKit, Microsoft 也宣布了
Windows Container 要開始支援 Linux container 等等...，我想不用多久就是 container 滿天飛了。到時你還 **只是** 在考慮 
containerize (容器化) 而已嗎? 如果你的服務將來註定要在 container 環境下執行，在開發的當下，你會如何設計你的軟體架構?

介紹 docker 的文章，很少是以 pure developer 角度在寫得，如果領域換到 windows container + .net developer
就更少了。我從小就是靠 Microsoft Solution 吃飯長大的，C# 我也從當年還是 Visual J# 的年代，一路到 .NET framework 1.0 就
開始用到現在，既然 Windows Container 也都問世了，那這篇文章的示範內容，我就用 Windows Container + .NET Framework + Azure
來做吧! 

Container Driven Development (我自己亂掰的名詞，不過竟然還 google 的到東西 @@) 就是我這篇想寫的概念，從 container 的
角度來思考你的 application 該怎麼設計。其實方針前面這幾篇微服務的文章都講過了。這篇就直接看我如何用這樣的思維來規劃
開發架構吧。我這次挑選的主題，是前陣子我實際上碰到的 case: 用 IP 查詢來源國家的服務。

這功能很符合微服務的定義: "小巧，專心做好某一件事"，剛好前陣子 Darkthread 也寫了一篇 "[用 100 行 C# 打造 IP 所屬國家快速查詢功能](http://blog.darkthread.net/post-2017-02-13-in-memory-ip-to-country-mapping.aspx)"，我就沿用 Darkthread
貢獻的 [Source Code](https://github.com/darkthread/IP2C.NET), 把它包裝成微服務，用容器化的方式部署到 Azure ! 


<!--more-->

{% include series-2016-microservice.md %}



# 容器驅動開發 (Container Driven Development)

別以為一個 "IP 查詢服務"，就真的只是一個服務而已。既然微服務的設計準則包含這條: "能獨立自主運作的服務"，那麼你要開發
的就不只 webapi 這麼一個而已。我先把需求列一下:

1. High Availability + Scalability
1. Auto Update IP Database
1. Include Client SDK (with client side cache)
1. DX (Developer Experience, 要對使用我的服務的開發者友善)

綜合這些需求，我規劃了這樣的架構，如果都能實作出來，應該就能同時滿足上述這幾項了吧? 既然 container 這麼好用，能透過
容器化解決的事情我就不用自己做了。在能夠極度利用容器化的優點為前提，來看看這份設計圖:

![](/images/2017-05-28-aspnet-msa-labs1/2017-05-23-23-25-51.png)
* Deployment diagram of IP2C service

很典型的架構，前端用一組 reverse proxy, 來把流量平均分配到後端的多組 IP2C.WebAPI, 來達到 HA + Scale out 的要求。
然而 IP query 最重要的就是資料庫的更新，因此另外安排了一個 IP2C.Worker, 定期到官網的下載頁面定期更新資料檔。下載後會自動
解壓縮，同時先對這個資料檔做好基本的單元測試，通過後才會部署到 share storage，供其他的 IP2C.WebAPI 使用。同時為了
方便其他的 developer 充分使用我的 IP2C service, 我也打算提供一組 SDK, 方便他們直接呼叫我的服務。這 IP2C.SDK 除了方便呼叫
IP2C.WebAPI 之外，我也在 SDK 內部實作上加了 client side cache, 同一個 IP 在時間內查詢多次, 則會直接透過 cache 傳回。

微服務化的應用程式開發，總是會有很多獨立的 projects, 開發測試的過程中會不斷面臨部署，測試，修改，部署... 的循環。過程中
若沒有做好 DevOps 的搭配，生產力會大幅地降低。因此我自己對於 DevOps 的流程我也做了簡單的 CI / CD 需求規劃:

1. Code 修改完成 Push 到 Git Repository 之後，觸發 CI 進行編譯、單元測試
1. 通過測試與編譯的 code, 則將 IP2C.WebAPI 與 IP2C.Worker 先建置成 docker image, 放到 docker registry
1. SDK 則在編譯之後，自動進行 nuget package 與 nuget push ，將 SDK 包裝成 Nuget 套件，放上 nuget server 發行這份 SDK
1. 決定要上版的時候，就透過預先編好的 docker compose 定義檔，從 docker registry 更新部署的版本

這兩部分都完成後，各位可以盤點一下，是否原先的需求都已經達成了? 整個藍圖設計好之後，接下來就是一步一步完成他了。
DevOps 的部分，我實際是使用 GitLab 的 CI-Runner, 簡單好用, 複雜度跟功能的平衡做得還不錯。不過這部分我會略過，
先用一個簡單的 build script 替代。以後有機會的話再來介紹這段。這次就跳過 DevOps, 後面的示範會直接半自動的部署到
Azure 上面現成的環境，篇幅有限，請見諒 :D


# 建立微服務 Solution: IP2C


這篇既然是 Hands-On Labs, 就直接來寫 code 吧! 這次的 solution 裡面有這些東西，先說明一下:

![](/images/2017-05-28-aspnet-msa-labs1/2017-05-23-23-37-16.png)



**/build.cmd**  
build script, 用來完成整個 solution 的編譯與發行 (to docker registry & nuget server)。
若你有採用任何 CI 的系統，可以將 script 的內容搬過去。我自己是用 GitLab, 可以在 CI runner 內沿用這個 build script。
這次範例我把重點擺在 code 上面，CI/CD 就用 build script + 手動部署容器來替代。

**/docker-compose.yml**  
要部署到執行環境使用的 docker-compose 設定檔。

**/IP2C.NET**  
從 Darkthread GitHub 直接 fork 過來的 project, 搜尋 ip-database csv 用的高效率 C# library

**/IP2CTest**  
從 Darkthread GitHub 上提供的 [Source Code](https://github.com/darkthread/IP2C.NET) 直接 fork 過來的 project, IP2C.NET 的單元測試

**/IP2C.WebAPI**  
使用 IP2C.NET 開發的 WebAPI, 提供 REST API，可以使用 ~/api/ip2c/{ip value} 的格式來查詢 ip address 所屬的國家。

**/IP2C.Worker**  
.NET Console Application, 啟動之後會開始計時，每隔一段固定時間後就自動到 IP2C 官方網站下載新的資料檔，在更新檔案
前會自動解壓縮 + 測試檔案內容是否正確。

**/IP2C.SDK**  
透過 REST API 呼叫 IP2C.WebAPI 的 .NET class library, 除了簡化呼叫的程序之外，也加上了 cache (client side)。



這整個 solution 大致上就包含這些內容。對我寫的 Demo Code 有興趣的可以直接到 GitHub 參考我的 [Source Code](https://github.com/andrew0928/IP2C.NET.Service)。覺得不錯的就給個星星吧 :D

接下來逐一看看每個 project 做了什麼特別的動作...



## Project: IP2C.WebAPI

這是服務的主體，對外提供查詢 IP 的 REST API。用 ASP.NET WebAPI2 開發。這個專案專注的部分很單純，就是提供查詢 IP 所屬
國家的 REST API。查詢格式是: ```/api/ip2c/134744072``` (數字部分是 IPV4 的 4bytes 數值轉成 int, 範例是 8.8.8.8, 換成 int 是
0x08080808, 也就是十進位的 134744072)。

查詢的結果用 Json 傳回，格式如下:

```javascript
{
    "CountryName": "United States",
    "CountryCode": "US"
}
```

至於查詢的來源資料檔，直接放在 ~/App_Data/ipdb.csv, 大小約 12mb 左右。查詢的核心邏輯，直接採用 Darkthread 提供的 IP2C.NET
這個 .NET 含式庫。

規格講完了，Code 其實也沒啥值得一看的 XD。
主要的 code 就只有這段，```IP2CController```:

```csharp
public class IP2CController : ApiController
{
    // 傳回對應的 ip address 所屬的國家代碼與名稱 (json)
    public object Get(uint id)
    {
        IPCountryFinder ipcf = this.LoadIPDB();

        string ipv4 = this.ConvertIntToIpAddress(id);
        string countryCode = ipcf.GetCountryCode(ipv4);

        return new
        {
            CountryName = ipcf.ConvertCountryCodeToName(countryCode),
            CountryCode = countryCode
        };
    }

    // 將代表 ipv4 的 int value 轉成 ipv4 的 string value
    private string ConvertIntToIpAddress(uint ipv4_value)
    {
        return string.Format(
            "{0}.{1}.{2}.{3}",
            (ipv4_value >> 24) & 0x00ff,
            (ipv4_value >> 16) & 0x00ff,
            (ipv4_value >> 08) & 0x00ff,
            (ipv4_value >> 00) & 0x00ff);
    }

    private IPCountryFinder LoadIPDB()
    {
        string cachekey = "storage:ip2c";

        IPCountryFinder result = MemoryCache.Default.Get(cachekey) as IPCountryFinder;
        if (result == null)
        {
            string filepath = HostingEnvironment.MapPath("~/App_Data/ipdb.csv");

            var cip = new CacheItemPolicy();
            cip.ChangeMonitors.Add(new HostFileChangeMonitor(new List<string> { filepath }));

            result = new IPCountryFinder(filepath);
            MemoryCache.Default.Add(
                cachekey,
                result,
                cip);
        }

        return result;
    }
}
```

沒幾行 code, 解釋就省了，接著來看對應的 dockerfile:

```dockerfile
FROM microsoft/aspnet

WORKDIR c:/inetpub/wwwroot/
COPY . .

EXPOSE 80
VOLUME ["c:/inetpub/wwwroot/App_Data"]
```
Dockerfile 是 Docker Engine 替你建置專屬的 container image 參考的藍圖。只要你的程式內容有修正，透過這個 dockerfile
就能在短短幾秒內替你重新建立一份新的 container image。這流暢的建置過程，搭配公用的 registry (hub.docker.com) 服務，
是 docker 能夠成功推廣 immutable server 概念的主要原因。這 dockerfile 裡面定義了幾件事:

1. 建置 container image 時，用 microsoft/aspnet 這個 image 為基礎。  
這是 microsoft 預先準備好，包含 IIS + ASP.NET runtime 的 image。
1. docker build 的過程中, 用 COPY 指令將編譯好的 webapp 檔案，複製到 container 內的 c:/inetpub/wwwroot
1. 宣告這個 container 將會用到 port 80  
將來在部署時，IT人員可以自由將之對應到其他 port
1. 宣告這個 container 將允許將外部的 volume 掛載到 c:/inetpub/wwwroot/app_data  
將來在部署時，IT人員可以選擇將這個目錄對應到其他 storage 上


在這個專案內，我已經預先放了一份格式正確的 ipdb.csv 檔案了。如果你不介意這是不是最新的話，其實你只要這個 project 就可
已執行 IP 查詢服務的 WebAPI 了。我直接附上 build 的指令 (DOS Prompt 命令提示字元，非 powershell):

```dos
: build solutions in release mode
"c:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe" /p:Configuration=Release /p:DeployOnBuild=true

: build webapi docker image
pushd .
cd IP2C.WebAPI\obj\Release\Package\PackageTmp
docker build -t ip2c/webapi:latest .
popd
```

如果執行成功，就會完成 project 的編譯，也會完成 docker image 的建置。
用這道指令就可以啟用這個 container 了:

```docker
docker run -d -p 8000:80 ip2c/webapi
```

這時，別的電腦就能透過 8000 port 存取你 PC 內的 webapi 了。由於 winnat 的限制，不支援 nat loopback。你如果本機要使用
的話，得查詢這個 container 在 nat 後面取得的 ip address, 用這個 ip 的 80 port 就可以使用 webapi.

關於 winnat + windows container 的問題，我在這篇 "[掃雷回憶錄 - Windows Container Network & Docker Compose](/2017/01/15/docker-networks/)" 有說明，需要的可以參考!


到目前為止，我們已經完成 ASP.NET WebAPI 的容器化了。如果你的開發機器是 windows 10 pro / enterprise, 或是 windows server 2016,
同時也已經啟用 windows container 支援功能的話，你不需要安裝 IIS 或是 IIS express 就可以直接在本機測試了。
其實很簡單一行指令就可以完成了，不過實際最大的效益現在還看不出來。我們這個 lab 繼續做下去...



## Project: IP2C.Worker

這個專案的目的，就只有一個，負責定期更新 WebAPI 服務需要的 ipdb.csv 檔案內容。期望的功能有:

1. 排程啟動後能進入監控模式，在指定的時間到達時自動進行檔案更新  
(實際上是每天執行，這邊我為了方便測試是每三分鐘執行一次)
1. 更新的程序要確保檔案的正確性，別讓服務掛掉；
下載後需要解壓縮 ([官方](http://software77.net/faq.html#automated)提供 .gz 下載)，同時用 IP2C.NET 嘗試查詢幾筆 IP address 當作單元測試，通過之後備份原本的檔案，再替換上新的檔案。
1. 第一次執行，若找不到舊版的檔案，則立刻先用預先下載的檔案替代更新。
(隨 code 附上的 ipdb.csv, 非最新的檔案)
1. 能夠透過 logs 查詢執行的成果
1. (option) 能透過後臺管控系統，隨時接受指令立即更新  
(這功能其實我有實作，不過扯到後台有點囉嗦，這次範例我先跳過)


在過去，這類程式寫起來其實也不難，但是為了讓他定期自動執行，其實有點麻煩，很多瑣事要另外處理。舉例來說，專案類型
要嘛就 windows service, 寫好後要安裝時還要註冊到 server 上，透過 windows 的服務管理員啟動。不然就是寫成 console app, 透過
windows 工作排程器，時間到了啟動它。

不過不管用哪個方法，其實都有點麻煩... 這邊我要介紹的是，如果你要在 container 內做這件事，遠比你想像的簡單! 
container 本身就已經可以被當成一個服務了 (daemon), 因此你唯一要做的就是，寫個 console app, 啟動後就按照上述的需求。把他
安排到 dockerfile 內的 entrypoint, 讓 container 一啟動就執行它就可以了。實際部署之後，IT 人員只要控制這個 container 是否
啟動或是停止就好，完全不需要 developer 開發時花心思處理這些細節。

至於 logs ? 這就更容易了。過去我們都會用 [NLog](http://nlog-project.org/) 或是 Apache [Log4Net](https://logging.apache.org/log4net/) 這類 logging framework, 來簡化你的 log 程序。現在更無腦了，
你甚麼都不用管，只要用最古早的 printf 大法... 啊，不對，Console.WriteLine(...) 的方式輸出訊息到 stdout 就可以了。一樣，以後
IT人員想要調閱這些 logs 怎麼辦? 用 docker logs 這指令就可以了。

說到這裡，我想本部落格的讀者應該都知道怎麼寫吧? 一樣沒幾行的 code, 直接來看看:


```csharp
class Program
{
    static void Main(string[] args)
    {
        bool isWatchMode = true;
        string filepath = Path.Combine(
            Path.GetDirectoryName(Assembly.GetEntryAssembly().Location),
            "data\\ipdb.csv");

        if (isWatchMode)
        {
            // watch mode
            DateTime start = new DateTime(2000, 1, 1, 15, 40, 0);
            TimeSpan period = TimeSpan.FromMinutes(3.0);

            while (true)
            {
                TimeSpan wait = TimeSpan.FromMilliseconds(period.TotalMilliseconds - (DateTime.Now - start).TotalMilliseconds % period.TotalMilliseconds);
                Console.WriteLine("wait: {0} (until: {1})", wait, DateTime.Now.Add(wait));
                Task.Delay(wait).Wait();
                UpdateFile(@"http://software77.net/geo-ip/?DL=1", filepath);
            }
            
        }
        else
        {
            // update once
            UpdateFile(@"http://software77.net/geo-ip/?DL=1", filepath);
        }
    }


    static void UpdateFile(string url, string file)
    {
        Console.WriteLine("-update file: {0}", DateTime.Now);

        string temp = Path.ChangeExtension(file, ".temp");
        string back = Path.ChangeExtension(file, ".bak");

        if (Directory.Exists(Path.GetDirectoryName(file)) == false)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(file));
        }

        if (File.Exists(temp)) File.Delete(temp);

        if (DownloadAndExtractGZip(url, temp))
        {
            if (TestFile(temp))
            {
                if (File.Exists(back)) File.Delete(back);
                if (File.Exists(file)) File.Move(file, back);
                File.Move(temp, file);
            }
            else
            {
                // test file, file incorrect
            }
        }
        else
        {
            // download fail.
        }
    }

    static bool TestFile(string file)
    {
        IPCountryFinder finder = new IPCountryFinder(file);

        // add test case here
        if (finder.GetCountryCode("168.95.1.1") != "TW") return false;


        return true;
    }

    static bool DownloadAndExtractGZip(string url, string file)
    {
        using (var client = new HttpClient())
        {
            HttpResponseMessage rsp = client.GetAsync(url).Result;

            if (rsp.StatusCode == HttpStatusCode.OK)
            {
                Stream source = rsp.Content.ReadAsStreamAsync().Result;

                GZipStream gzs = new GZipStream(source, CompressionMode.Decompress);
                FileStream fs = File.OpenWrite(file);

                int count = 0;
                byte[] buffer = new byte[4096];
                while((count = gzs.Read(buffer, 0, buffer.Length)) > 0)
                {
                    fs.Write(buffer, 0, count);
                }
                gzs.Close();
                fs.Close();

                source.Close();

                return true;
            }
        }

        return false;
    }
}
```


程式碼稍長了一點，不過都很簡單。接著來看看對應的 dockerfile:

```dockerfile
FROM microsoft/dotnet-framework:latest

WORKDIR   c:/IP2C.Worker
COPY . .

VOLUME ["c:/IP2C.Worker/data"]
ENTRYPOINT IP2C.Worker.exe
```

dockerfile 也是簡單到爆，選定 base image, 複製檔案, 啟動檔案 (加上正確參數) 就結束了。

想要測試看看這個 container 是否能正常啟動? build 成功之後用這段指令啟動它 (互動模式):

```dos
docker run ip2c/worker
```

為了方便展示，我 source code 裡面定義的執行頻率比較密集，每三分鐘就會跑一次。你可以看到類似這樣的 message:

```console
D:\CodeWork\github.com\IP2C.NET.Service>docker run ip2c/worker
wait: 00:02:24.7680000 (until: 5/24/2017 1:01:00 AM)
-update file: 5/24/2017 1:01:00 AM
wait: 00:02:52.6580000 (until: 5/24/2017 1:04:00 AM)
-update file: 5/24/2017 1:04:00 AM
wait: 00:02:55.3320000 (until: 5/24/2017 1:06:59 AM)
```

在同個 container 用 ```docker exec ...``` 多開一個 shell (cmd.exe), 進去 container 的目錄，你可以看到檔案真的有下載成功:

```console

C:\IP2C.Worker>dir data
 Volume in drive C has no label.
 Volume Serial Number is AC75-48E4

 Directory of C:\IP2C.Worker\data

05/24/2017  01:04 AM    <DIR>          .
05/24/2017  01:04 AM    <DIR>          ..
05/24/2017  01:01 AM        12,449,488 ipdb.bak
05/24/2017  01:04 AM        12,449,488 ipdb.csv
               2 File(s)     24,898,976 bytes
               2 Dir(s)  88,298,643,456 bytes free

C:\IP2C.Worker>
```

不過實際執行，不能用互動模式啊! 只要啟動指令調整一下，加個 ```-d``` (--daemon) 就可以變成背景服務:

```dos
docker run -d ip2c/worker
```

背景模式就看不到輸出的訊息了... 這也很簡單，用 ```docker logs``` 指令就可以 (其中 5edf24fae8cf 是 container 的 ID):

```dos
D:\>docker ps -a
CONTAINER ID        IMAGE               COMMAND                   CREATED             STATUS                      PORTS                  NAMES
5edf24fae8cf        ip2c/worker         "cmd /S /C 'IP2C.W..."    47 hours ago        Exited (255) 46 hours ago                          kind_noyce
714dd0e424f7        ip2c/webapi         "C:\\ServiceMonitor..."   47 hours ago        Up 47 hours                 0.0.0.0:8000->80/tcp   tender_brown

D:\>docker logs 5edf24fae8cf
wait: 00:01:10.0480000 (until: 5/24/2017 1:19:00 AM)
-update file: 5/24/2017 1:19:00 AM
wait: 00:02:48.9170000 (until: 5/24/2017 1:22:00 AM)
-update file: 5/24/2017 1:22:00 AM
wait: 00:02:55.0310000 (until: 5/24/2017 1:24:59 AM)
-update file: 5/24/2017 1:25:00 AM
wait: 00:02:54.0370000 (until: 5/24/2017 1:28:00 AM)
-update file: 5/24/2017 1:28:00 AM
wait: 00:02:55.7030000 (until: 5/24/2017 1:30:59 AM)
-update file: 5/24/2017 1:31:00 AM
wait: 00:02:54.4140000 (until: 5/24/2017 1:33:59 AM)
-update file: 5/24/2017 1:34:00 AM
```


體會到了嗎? 容器的機制其實替你解決了不少麻煩事，從服務的開發，執行環境的控制，服務啟動及停止等等的控制，到 LOG 的收集
處理，甚至到所有不同應用程式的 image 建置與部署通通解決了，這些才是 developer 最討厭的部分啊! docker 能漂亮的搞定
這些問題，又把工具鏈跟生態圈弄得很好，才會在短短的四年就爆紅..

容器技術優異的地方在於，用通用一致的 image 格式，把你的程式與執行環境都放到裡面，精準地控制了執行環境，解決執行時
對環境的要求，工程師們以後不用再把 "在我電腦上是**好**的啊.." 這句話掛在嘴邊了 XD

封裝成 image 後，要執行時只要透過 ```docker run``` 就能啟動了。啟動時 docker 允許你調整 container 對外溝通的幾個
管道，這部分就是部署人員要接手的部分了。Docker 統一管控 container 的對外溝通管道有:

* network (ipaddress, ports)
* volume (folder, file)
* environment variable

舉例來說，HTTP REST 都會需要 TCP 80 port, 你在打包 container image 時不用擔心這個，實際部署時，```docker run``` 指令
允許你把實際的 port (ex: 8080) 轉接給 container 內的 port 80。

同樣的道理也可應用在 volume 的對應上。你可以把實際 host server 上的磁碟目錄 (ex: d:\data) 掛到 container 內 (ex: c:\inetpub\wwwroot\app_data)。對 container 內來說，他就只是個單純的 symbol link 而已。如果你把實體的目錄同時掛載
到多個 container 內的話，那這效用就相當於你開了共享目錄，同時給多個 container 使用。這遠比開網路芳鄰簡單太多了。這些
環境的控制，都只要交給部署的 IT 人員決定就夠了，完全不用勞煩 developer 。

這邊最巧妙的地方，就是容器本身就已經有 start / stop 等等狀態了，容器本身可以用 daemon (-d) 模式啟動，這時整個容器
就相當於標準的 windows service 了。你完全不需要替背景服務這件事寫任何額外的 code, 你只需要像這個例子一樣，單純寫個
console app 就夠了。這簡單的程度跟我們當年在學 hello world 差不多容易啊..

不過，跟前面 webapi 一樣。到目前為止用容器化部署的效益還看不大出來，後面完成後再來看...



## Test Run: IP2C Services (WebAPI + Worker) on Local PC

現在，我們要把兩個 container 一起啟動了。這邊啟動的方式有點不同，兩個 container 能共同合作的前提，是要有共享的目錄。
我的作法是兩個 container 都先定義了一個 volume 的掛載點，啟動的時候我在 docker engine host 上建立一個 folder, 把這個
folder 同時掛上兩個 container 就搞定了。

我準備拿 d:\codework\data 當作範例，依序執行下列指令:

```dos
D:\>md data

D:\>docker run -d -p 8000:80 -v d:\data:c:/inetpub/wwwroot/App_Data ip2c/webapi
714dd0e424f7b57996b5e62f0ef0b457bdf0280cdc9e8160b2f7862257717b1b

D:\>docker run -d -v d:\data:c:/IP2C.Worker/data ip2c/worker
5edf24fae8cf793736307344e84ec95b49c6deafc3c8a034ce5efadfdf54f409

D:\>
```

剛啟動時，要等一會兒，讓 worker 更新資料檔之後就可以使用了。簡單用瀏覽器測試:

![](/images/2017-05-28-aspnet-msa-labs1/2017-05-24-01-21-10.png)

我測試的是 Google DNS 的 IP (8.8.8.8)，用十六進位表示這 IP 對應的 int 數值是: 0x08080808, 拿小算盤敲一敲，
換成十進位就是 134744072 ... 湊成 URL 就可以直接丟給 webapi 查詢了。

我們先用 ```docker logs``` 這指令，看看 worker 執行的 logs (console app 顯示在 stdout 的訊息，都可以這樣查看):

```dos
D:\CodeWork\github.com\IP2C.NET.Service\IP2C.WebAPI\obj\Release\Package\PackageTmp>docker logs 5e
wait: 00:01:10.0480000 (until: 5/24/2017 1:19:00 AM)
-update file: 5/24/2017 1:19:00 AM
wait: 00:02:48.9170000 (until: 5/24/2017 1:22:00 AM)
-update file: 5/24/2017 1:22:00 AM
wait: 00:02:55.0310000 (until: 5/24/2017 1:24:59 AM)

D:\CodeWork\github.com\IP2C.NET.Service\IP2C.WebAPI\obj\Release\Package\PackageTmp>
```

看來更新的很順利。這時我們再多開個 cmd.exe 分別進去兩個 container 看看更新的狀況。先看 worker:
```dos
C:\IP2C.Worker>dir
 Volume in drive C has no label.
 Volume Serial Number is AC75-48E4

 Directory of C:\IP2C.Worker

05/24/2017  12:51 AM    <DIR>          .
05/24/2017  12:51 AM    <DIR>          ..
05/24/2017  01:17 AM    <SYMLINKD>     data [\\?\ContainerMappedDirectories\97D5871C-3BA8-4288-A465-6D2DE1164A85]
05/23/2017  11:34 PM               223 dockerfile
05/24/2017  12:35 AM             6,656 IP2C.Net.dll
05/24/2017  12:35 AM            13,824 IP2C.Net.pdb
05/24/2017  12:35 AM             7,168 IP2C.Worker.exe
05/21/2017  04:01 AM               189 IP2C.Worker.exe.config
05/24/2017  12:35 AM            13,824 IP2C.Worker.pdb
               6 File(s)         41,884 bytes
               3 Dir(s)  21,131,309,056 bytes free

C:\IP2C.Worker>dir data
 Volume in drive C has no label.
 Volume Serial Number is AC75-48E4

 Directory of C:\IP2C.Worker\data

05/24/2017  01:25 AM    <DIR>          .
05/24/2017  01:25 AM    <DIR>          ..
05/24/2017  01:22 AM        12,449,488 ipdb.bak
05/24/2017  01:25 AM        12,449,488 ipdb.csv
               2 File(s)     24,898,976 bytes
               2 Dir(s)  1,479,074,295,808 bytes free

C:\IP2C.Worker>
```


再來看看 webapi:

```dos
C:\inetpub\wwwroot>dir
 Volume in drive C has no label.
 Volume Serial Number is AC75-48E4

 Directory of C:\inetpub\wwwroot

05/24/2017  01:12 AM    <DIR>          .
05/24/2017  01:12 AM    <DIR>          ..
05/24/2017  01:12 AM    <SYMLINKD>     App_Data [\\?\ContainerMappedDirectories\8287B602-8FB3-460B-9405-BC1D770E9D5B]
05/24/2017  12:35 AM    <DIR>          bin
05/24/2017  01:12 AM               125 dockerfile
05/21/2017  03:59 AM               106 Global.asax
05/21/2017  02:18 PM               916 packages.config
05/24/2017  12:35 AM             1,633 web.config
               4 File(s)          2,780 bytes
               4 Dir(s)  21,123,481,600 bytes free

C:\inetpub\wwwroot>dir App_Data
 Volume in drive C has no label.
 Volume Serial Number is AC75-48E4

 Directory of C:\inetpub\wwwroot\App_Data

05/24/2017  01:25 AM    <DIR>          .
05/24/2017  01:25 AM    <DIR>          ..
05/24/2017  01:22 AM        12,449,488 ipdb.bak
05/24/2017  01:25 AM        12,449,488 ipdb.csv
               2 File(s)     24,898,976 bytes
               2 Dir(s)  1,479,074,295,808 bytes free

C:\inetpub\wwwroot>
```

看到了嗎? 跟前面不同的是，簡單的透過 volume 將 host 的 d:\data 目錄，分別掛上兩個 container 的 data folder，就完成
在兩個 container 之間共享目錄的功能了。這遠比正常的 server 要開分享目錄，再用網路磁碟，或是 iSCSI 等等機制掛上網路磁碟機，
然後還要再去搞定存取網路磁碟機的安全問題跟帳號設定... ，container 的做法簡單有效的多了。每次我搞分享目錄到這些服務上，都會
被帳號問題跟 ACL 搞得很毛... 現在這些問題都被容器技術解決了。

Container Driven Development 對開發人員最大的效益 (我自己觀點)，就是: 你會發現你幾乎不需要浪費力氣，寫不需要的 code, 因為
容器化的技術都極大化的替你解決這些瑣事了。在過去正式上線的系統遠遠不能這樣搞，有一堆其他的東西要寫，例如要寫成 windows service
就有上百行的 code 要先填好, 其他如安裝程式，或是要在 server 上設定排程等等，現在通通不用了。

容器化的部署，現在看到效益了嗎? 這還只是在開發機器上面自己測試而已。你會發現容器技術的精神在於，把所有的 application 都包成一樣的
格式，用一樣的方式啟動執行。因此開發人員只要想辦法把 image 準備好，剩下的部署任務就交給 IT 人員。部署人員只要按照架構圖，把容器
按照規劃的方式啟動 (掛上 network port, 掛上 volume, 指定 environment variables) 就可以了，可大可小。最小如現在在開發 PC
上面測試功能，最大可以用同樣方法部署到 docker swarm cluster 上，將 WebAPI 多開幾個 instance 做效能擴充 (scale out), 應付
大量的使用者。這些極端的使用狀況，使用的通通都是一樣的 code, 一樣的 image !


## 小結

看到這邊就很 high 要馬上動手寫 code 了嗎? 別急... 後面還有!
請期待續集 :D

下一篇要說明 SDK 的處理，Reverse Proxy 的設置，以及 docker compose 的應用。