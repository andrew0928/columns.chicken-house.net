---
layout: post
title: "容器化的服務開發 #1, 架構與概念"
categories:
- "系列文章: .NET + Windows Container, 微服務架構設計"
- "系列文章: 架構師觀點"
tags: ["microservice", "系列文章", "ASP.NET", "架構師", "Docker", "Windows Container", "DevOps"]
published: true
comments: true
redirect_from:
logo: 
---

總算把包含架構與觀念的實際案例篇寫完了，前面也寫完了微服務化一定會面臨的 API 開發設計問題，那接下來可以開始
進入有趣一點的部分了。微服務架構是由很多獨立的小型服務組合而成的，這次我們直接來看看每一個服務本身應該怎麼開發。

既然要講到實作，那就不能不提讓微服務可以實現的容器技術。我一直覺得很可惜的是，不管國內或國外的文章，以開發者的
角度來介紹容器技術的案例實在不多啊 (還是我關鍵字下的不對? @@) 大部分的文章都是在強調容器在架構面的好處 (微服務)，
不然就是一堆操作技巧，教你怎樣把既有的 application 包裝成容器，再者就是容器的管理技巧等等。但是當容器已經普及了
之後，你的服務開發方向，是否能夠針對容器做最佳化?

介紹 docker 的文章，很少是以 pure developer 角度在寫得，如果領域換到 windows container + .net developer
就更少了。我從小就是靠 Microsoft Solution 吃飯長大的，C# 我也從當年還是 Visual J# 的年代，一路到 .NET framework 1.0 就
開始用到現在，既然 Windows Container 也都問世了，那這篇文章的示範內容，我就用 Windows Container + .NET Framework + Azure
來做吧! 

我這次挑選的主題，就用前陣子我實際上碰到的 case: 用 IP 查詢來源國家的服務當作例子。這功能很符合微服務的定義: 
"小巧，專心做好某一件事"，剛好前陣子 Darkthread 也寫了一篇 "[用 100 行 C# 打造 IP 所屬國家快速查詢功能](http://blog.darkthread.net/post-2017-02-13-in-memory-ip-to-country-mapping.aspx)"，我就沿用 Darkthread
貢獻的 Source Code, 把它包裝成微服務，用容器化的方式部署到 Azure ! 


<!-- more -->


## IP查詢服務，該有哪些元件?

別以為一個 "IP 查詢服務"，就真的只是一個服務而已。既然微服務的設計準則包含這條: "能獨立自主運作的服務"，那麼你要開發
的就不只 webapi 這麼一個而已。我先把需求列一下:

1. High Availability + Scalability
1. Auto Update IP Database
1. Include Client SDK (with client side cache)
1. DX (Developer Experience, 要對使用我的服務的開發者友善)

綜合這些需求，我規劃了這樣的架構，如果都能實作出來，應該就能同時滿足上述這幾項了吧? 來看看設計圖:

![](/wp-content/uploads/2017/05/2017-05-23-23-25-51.png)
> Deployment diagram of IP2C service

很典型的架構，前端用一組 reverse proxy, 來把流量平均分配到後端的多組 IP2C.WebAPI, 來達到 HA + Scale out 的要求。
然而 IP query 最重要的就是資料庫的更新，因此另外安排了一個 IP2C.Worker, 定期到官網的下載頁面定期更新資料檔。下載後會自動
解壓縮，同時先對這個資料檔做好基本的單元測試，通過後才會部署到 share storage，供其他的 IP2C.WebAPI 使用。同時為了
方便其他的 developer 充分使用我的 IP2C service, 我也打算提供一組 SDK, 方便他們直接呼叫我的服務。這 IP2C.SDK 除了方便呼叫
IP2C.WebAPI 之外，我也在 SDK 內部實作上加了 client side cache, 同一個 IP 在時間內查詢多次, 則會直接透過 cache 傳回。

除了營運環境的部分之外，對於我自己的 DevOps 流程我也做了簡單的 CI / CD 需求規劃:

1. Code 修改完成 Push 到 Git Repository 之後，觸發 CI 進行編譯、單元測試
1. 通過測試與編譯的 code, 則將 IP2C.WebAPI 與 IP2C.Worker 先建置成 docker image, 放到 docker registry
1. SDK 則在編譯之後，自動進行 nuget package 與 nuget push ，將 SDK 包裝成 Nuget 套件，放上 nuget server 發行這份 SDK
1. 決定要上版的時候，就透過預先編好的 docker compose 定義檔，從 docker registry 更新部署的版本

這兩部分都完成後，各位可以盤點一下，是否原先的需求都已經達成了? 整個藍圖設計好之後，接下來就是一步一步完成他了。

> 這次主要重點在開發，因此 DevOps 環境的建置過程我會略過，直接用 Azure 上面現成的環境，篇幅有限，請見諒 :D


## 建立微服務 solution

![](/wp-content/uploads/2017/05/2017-05-23-23-37-16.png)

這篇既然是 Hands-On Labs, 就直接來寫 code 吧! 這次的 solution 裡面有這些東西，先說明一下:

**/build.cmd**  
build script, 用來完成整個 solution 的編譯與發行 (to docker registry & nuget server)。
若你有採用任何 CI 的系統，可以將 script 的內容搬過去。我自己是用 GitLab, 可以在 CI runner 內沿用這個 build script。

**/docker-compose.yml**  
要部署到執行環境使用的 docker-compose 設定檔。

**/IP2C.NET**  
從 Darkthread GitHub 直接 fork 過來的 project, 搜尋 ip-database csv 用的高效率 C# library

**/IP2CTest**  
從 Darkthread GitHub 直接 fork 過來的 project, IP2C.NET 的單元測試

**/IP2C.WebAPI**  
使用 IP2C.NET 開發的 WebAPI, 提供 REST API，可以使用 ~/api/ip2c/{ip value} 的格式來查詢 ip address 所屬的國家。

**/IP2C.Worker**  
.NET Console Application, 啟動之後會開始計時，每隔一段固定時間後就自動到 IP2C 官方網站下載新的資料檔，在更新檔案
前會自動解壓縮 + 測試檔案內容是否正確。

**/IP2C.SDK**  
透過 REST API 呼叫 IP2C.WebAPI 的 .NET class library, 除了簡化呼叫的程序之外，也加上了 cache (client side)。

這整個 solution 大致上就包含這些內容。接下來逐一看看每個 project 做了什麼特別的動作...



## IP2C.WebAPI

這是主要的服務，用 ASP.NET WebAPI2 開發。主要的 code 就只有這段，```IP2CController```:

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

這 dockerfile 內容也很簡單。dockerfile 是用來描述怎麼建置你的 application 專屬的 container image 的定義檔。

這裡定義了幾件事:
1. 用 microsoft/aspnet 這個 image 為基礎。這是 microsoft 預先準備好，包含 IIS + ASP.NET runtime 的 image。
1. docker build 的過程中, COPY 編譯好的 project webapp 到 container 內的 c:/inetpub/wwwroot
1. 宣告這個 container 將會用到 port 80
1. 宣告這個 container 將會需要掛載外部的 volume 到 c:/inetpub/wwwroot/app_data


在這個專案內，我已經預先放了一份格式正確的 ipdb.csv 檔案了。如果你不介意這是不是最新的，其實你已經可以自己試看看了。
我直接附上 build 的指令:

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


到目前為止，我們已經完成 ASP.NET WebAPI 的容器化了。其實很簡單就可以完成了。不過效益現在還看不出來。我們這個 lab 繼續做下去...



## IP2C.Worker

接著來看看，自動更新資料檔案的 code 怎麼寫吧! 在過去，這類程式寫起來其實也不難，但是為了讓他定期自動執行，其實有點麻煩。
要嘛就寫成 windows service, 安裝時要註冊到 server 上，透過 windows 的服務管理員啟動。不然就是寫成 console app, 透過
windows 工作排成器，時間到了啟動它。

不過不管用哪個方法，其實都有點麻煩... 這邊我要介紹的是，如果你要在 container 內做這件事，遠比你想像的簡單! 我先講做法，
後面在來解釋... 在 container 的世界內，你只要寫個 script, 或是寫個 console app, 程式啟動後就 sleep, 直到預定執行的時間
到了再醒來就可以了。

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

code 複雜的部份都是在下載 + 解壓縮，還有解壓縮後會用 IP2C.NET 簡單的測試一下下載的檔案是好是壞?
都沒問題的話，會備份原本的舊檔案，用新的檔案替代。


```dockerfile
FROM microsoft/dotnet-framework:latest

WORKDIR   c:/IP2C.Worker
COPY . .

VOLUME ["c:/IP2C.Worker/data"]

ENTRYPOINT IP2C.Worker.exe --watch c:\IP2C.Worker\data\ipdb.csv
```

dockerfile 也是簡單到爆，選定 base image, 複製檔案, 啟動檔案 (加上正確參數) 就結束了。

想要測試看看這個 container 是否能正常啟動? build 成功之後用這段指令啟動它:

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

進去 container 的目錄，你可以看到檔案真的有下載成功:

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

現在回過頭來說明一下，容器能幫你簡化甚麼事情吧! 容器技術只是把你的 application 包裝成固定的 image 格式，同時定義
你的容器需要對外溝通的幾個地方，包含 network (ipaddress, ports), volume, entrypoint, environment variable 等等。

這邊最巧妙的地方，就是容器本身就已經有 start / stop 等等狀態了，容器本身可以用 daemon (-d) 模式啟動，這時整個容器
就相當於標準的 windows service 了。你完全不需要替背景服務這件事寫任何額外的 code, 你只需要像這個例子一樣，單純寫個
console app 就夠了。這簡單的程度跟我們當年在學 hello world 差不多容易啊..

不過，跟前面 webapi 一樣。到目前為止用容器化部署的效益還看不大出來，後面完成後再來看...



## Run IP2C Services (WebAPI + Worker) on Local PC

// dev-env, no scale out, no HA, use docker only, not docker-compose

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

![](/wp-content/uploads/2017/05/2017-05-24-01-21-10.png)

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

看到了嗎? 簡單的透過 volume 就完成兩個 container 之間的 share folder 機制。遠比正常的 server 要用網路磁碟，或是 iSCSI 等等機制
容易得多了。網路磁碟機還會搞出一堆 ACL 的設定問題，每次我搞到這些都會被帳號問題搞得很毛... 現在這些問題都被容器技術解決了。

容器化的部署，現在看到效益了嗎? 這還只是在開發機器上面自己測試而已。你會發現容器技術的精神在於，把所有的 application 都包成一樣的
格式，用一樣的方式啟動執行。因此開發人員只要想辦法把 image 準備好，剩下的部署任務通通都不用擔心了。部署人員只要按照架構圖，把容器
按照規劃的方式啟動 (掛上 network port, 掛上 volume, 指定 environment variables) 就可以了。










## IP2C.SDK

// webapi wrapper

// performance turning, 別指望其他 developer 會替你最佳化 (cache)

// DX



## Summary

// 看看你寫了那些 code ? 都只是必要的
// 其他都省略了 (尤其是 worker)

// next step?


