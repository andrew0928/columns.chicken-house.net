---
layout: post
title: "利用 NUnitLite, 在 App_Code 下寫單元測試"
categories:

tags: [".NET"]
published: true
comments: true
redirect_from:
  - /2006/10/29/利用-nunitlite-在-app_code-下寫單元測試/
  - /columns/post/2006/10/29/e588a9e794a8-NUnitLite2c-e59ca8-App_Code-e4b88be5afabe596aee58583e6b8ace8a9a6.aspx/
  - /post/2006/10/29/e588a9e794a8-NUnitLite2c-e59ca8-App_Code-e4b88be5afabe596aee58583e6b8ace8a9a6.aspx/
  - /post/e588a9e794a8-NUnitLite2c-e59ca8-App_Code-e4b88be5afabe596aee58583e6b8ace8a9a6.aspx/
  - /columns/2006/10/29/e588a9e794a8-NUnitLite2c-e59ca8-App_Code-e4b88be5afabe596aee58583e6b8ace8a9a6.aspx/
  - /columns/e588a9e794a8-NUnitLite2c-e59ca8-App_Code-e4b88be5afabe596aee58583e6b8ace8a9a6.aspx/
  - /blogs/chicken/archive/2006/10/29/1903.aspx/
wordpress_postid: 215
---

繼上篇寫了些 543, 說 NUnitLite 可以用來測 Asp.Net 2.0 Web Application 後, 這次來個簡單的範例. 因為我公司主要開發的是 web based application, 因此常常碰到寫好的程式可能會被安裝到好幾個不同 site 的情況, 甚至安裝的人員也不見得是懂 coding 的人.. 因此確認 configuration 是否正確就是很重要的一環. 這個例子就來把 "configuration 是否正確" 這件事, 也當做 unit test 的一部份.

也許有人會講, 這是環境的測試, 而 unit test 主要是要測程式的最小單元 - function 是否正常, 話是沒錯, config 之類的問題應該用 trace / assert 也許較恰當, 或是整個 system initialization 時就應該自我檢查一番. 這樣沒錯, 不過我的看法較實際一點, 除非你的開發人員很多, 或是你的產品量已經大到值得你這麼做, 否則大部份的專案, 我想這部份都是被呼略掉的一環...

因此, 既然 NUnit Framework 已經讓測試這麼方便了, 為什麼不順便用這種機制來做些額外的檢查? 好, 不多說, 來看 sample project: NUnitLiteWebSite

首先, 你寫好的 test fixture, 總要有 test runner 來測試它. Nunit 有 gui / console mode runner, 但是 NUnitLite 沒有, 而且 App_Code 最簡單能執行的方式也只有 asp.net page (其實我實際應用的案例, 連 ASP.NET Hosting 都用上了, 不過這就有點偏離主題了). 所以...

Step 1. 先建立一個 Web Site Project.. [[download](http://www.chicken-house.net/files/chicken/NUnitLiteWebSite.zip)]

Step 2. Reference NUnitLite.dll, 請自行到 NUnitLite 網站下載 source code, 自己 build 吧.

Step 3. 實作 NUnitLiteTestRunner.aspx 這個網頁, 目標是 browser 開啟這網頁, 就能看到像 NUnitConsole 輸出的結果畫面... (當然醜一點沒關係... ) 主程式很短, 如下...

```csharp
public partial class NUnitLiteTestRunner : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        this.Response.ContentType = "text/plain";
        Console.SetOut(this.Response.Output);

        ConsoleUI.Main(new string[] {"App_Code"});
    }
}
```

應該沒啥需要說明吧?
第一行指定輸出的 content type 是純文字...
第二行把 Console.Output 導向到 Response.Output, 這樣 browser 才收的到輸出內容
第三行, 呼叫 NUnitLite 內建的 console test runner ...
第四行, 沒... 沒事做了

Step 4. 接下來就簡單了, 直接在 App_Code 下把你要的 TestFixture 通通丟進去... 我準備了一個例子, 主要做兩項測試. 一個是確認 session 有啟用, 另一個就是確認 configuration 裡指定的 temp folder 是否存在, 是否真的能夠 create / read / write / delete temp file.

```csharp
[TestFixture]
public class ConfigurationTest
{
    [Test]
    public void SessionEnableTest()
    {
        //
        // 確認session 是啟用的
        //
        Assert.NotNull(HttpContext.Current.Session);
    }

    [Test]
    public void TempFolderAccessTest()
    {
        //
        // 確認設定檔指定的temp folder 存在
        //
        Assert.True(Directory.Exists(ConfigurationManager.AppSettings["temp-folder"]));

        string filepath = Path.Combine(ConfigurationManager.AppSettings["temp-folder"], "test.txt");
        string content = "12345";

        //
        // 確認可以寫暫存檔
        //
        File.WriteAllText(
            filepath,
            content);

        //
        // 確認可讀, 且內容跟寫入的一樣
        //
        Assert.AreEqual(
            File.ReadAllText(filepath),
            content);

        //
        // 確認可刪除, 不會有exception
        //
        File.Delete(filepath);
    }
}
```

Step 5. Deploy Web, 調整好各項 configuration, 啟用前先點一下 NUnitLiteTestRunner.aspx, 看看結果如何... 但是我的 IE 很怪, 明明 Step 3 的 code 都已經把 content type 都標示為 text/plain 了, 我的 IE 硬要把它當 xml 來開, 然後才唉唉叫說 xml 有問題.... 結果就變這樣:

![NUnitLite Test Result](/images/2006-10-29-using-nunitlite-in-app-code-for-unit-testing/image010.png)

如果你剛好也碰到, 就直接按右鍵選 view source 就好...

<!--more-->

---
```
NUnitLite version 0.1.0
Copyright 2006, Charlie Poole

Runtime Environment -
    OS Version: Microsoft Windows NT 5.1.2600 Service Pack 2
  .NET Version: 2.0.50727.42

2 Tests : 0 Errors, 0 Failures, 0 Not Run
```
---

故意把 web.config 裡的 session 關掉看看...

哇哈哈, 真的如我預期的可以運作, 真是太好了. 同樣的例子大家可以換 NUnit 來試試, 一樣可以 run, 不過一來 NUnit 的 assembly 太多, 二來它會無法載入 App_Code 這個 assembly, 三來它會很嚴僅的另外建 AppDomain, 另外用獨立的 thread 來跑你的 test case, 這些動作都是非常不建議用在 web application 下的, 除非你很確定它對系統的影響... 所以, NUnit 還是留給更大規模更嚴僅的開發專案吧, 較簡單快速的 web application, NUnitLite 還是很好用的 [Y]

看完了, 對你有幫助的話, 來點掌聲吧 [H]
