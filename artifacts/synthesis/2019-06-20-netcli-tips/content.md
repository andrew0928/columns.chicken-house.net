![](/images/2019-06-20-netcli-tips/2019-06-20-23-35-14.png)

延續[前一篇](/2019/06/15/netcli-pipeline/)，在寫 demo code 的時候想到的小技巧，但是文章內容時在塞不下了，所以另外補了個番外篇，就當作日常開發的小技巧分享吧 (搞不好這種短篇的還比較受歡迎 T_T)。[前一篇](/2019/06/15/netcli-pipeline/)介紹的是 CLI + PIPELINE 的開發技巧。我就以這為主軸，分享一下幾個相關的開發技巧吧。其中一個就是如何透過 pipeline 傳遞物件，另一個就是善用 LINQ 來處理 pipeline 傳來的物件。

<!--more-->


# 透過 PIPELINE 傳遞物件 (Json)

一般的 CLI, 都只能透過 STDIN / STDOUT 傳遞純文字訊息，不論輸入或輸出，都要經過一堆文字的處理，相當麻煩。不過，其實這是個誤解啊! 以 .NET 的觀點來看，STDIN / STDOUT 其實是 Stream 層級的東西啊，不是 ```TextReader``` / ```TextWriter``` 層級的東西...，因此你其實可以拿來處理 binary data 的，只是你無法確定 PIPELINE 的下一關會是誰 (要看下 shell command 的人怎麼用)，直接把 binary data 輸出到 terminal 會搞得一團亂，如此而已。

Windows 陣營的 developer 也許不一定熟悉 linux shell script, 但是 powershell 總應該不陌生吧? *nix 的 shell script 其實已經有 20 年以上的歷史了，當年的卻都還是以文字為主的處理方式。powershell 年輕的多, 總是要有些比人強的特色才行，其中一個特色就是: powershell script 裡的物件，能夠直接透過 PIPELINE 傳遞到下一個 powershell script 繼續使用。

乍看之下這是個很神奇的功能 (如果你懶得自己搞，這也真的很神奇)，不過如果 PIPELINE 前後段的 CLI 都是你開發的，其實這件事一點都不難啊! 善用物件的序列化即可。

我直接把[上一篇](/2019/06/15/netcli-pipeline/) 文章的例子拿來示範，最簡單的方式，就是透過 Json 序列化物件, 輸出到 STDOUT, 讓 PIPELINE 轉到下個 CLI 的 STDIN...。這是 CLI-DATA, 產生物件的 console app, 我稍微調整一下程式碼，產生物件的來源用 ```IEnumerable<DataModel>``` 封裝起來:

```csharp
class Program
{
    static void Main(string[] args)
    {
        var json = JsonSerializer.Create();
        foreach(var model in GenerateData())
        {
            json.Serialize(Console.Out, model);
            Console.Out.WriteLine();
        }
    }

    static IEnumerable<DataModel> GenerateData()
    {
        for (int seed = 1; seed <= 1000; seed++)
        {
            yield return new DataModel()
            {
                ID = $"DATA-{Guid.NewGuid():N}",
                SerialNO = seed,
                Buffer = AllocateBytesBuffer(16)
            };
        }
    }

    static Random rnd = new Random();
    static byte[] AllocateBytesBuffer(int size)
    {
        byte[] buf = new byte[size];
        rnd.NextBytes(buf);
        return buf;
    }
}
```

我刻意一筆物件就輸出一次 JSON, 最上層不用物件或是陣列包起來, 我不希望下一關要完整的 parsing 所有的 data 才能使用。

接著看接收端，同樣的我把前一篇文章的例子 CLI-PI 稍微重構一下:

```csharp

static void Main(string[] args)
{
    var json = JsonSerializer.Create();
    foreach(var model in ReceiveData())
    {
        DataModelHelper.ProcessPhase1(model);
        json.Serialize(Console.Out, model);
    }
}

static IEnumerable<DataModel> ReceiveData()
{
    var json = JsonSerializer.Create();
    var jsonreader = new JsonTextReader(Console.In);
    jsonreader.SupportMultipleContent = true;

    while (jsonreader.Read())
    {
        yield return json.Deserialize<DataModel>(jsonreader);
    }

    yield break;
}


```

想當然爾，一定能執行的啊... 直接執行 CLI-DATA 可以得到這樣的輸出 (只列前 10 行):

```text

C:\> dotnet CLI-DATA.dll

{"Buffer":"fLsyOUWNz8Mz+YLqr3/6/g==","ID":"DATA-5266baddb924470887b8cd82dc33069a","SerialNO":1,"Stage":0}
{"Buffer":"1iuGrkCwHItSvW9OU7gwrw==","ID":"DATA-06054528b9be4d1a99be60e2c840b046","SerialNO":2,"Stage":0}
{"Buffer":"egRCltFRx7Mr5BpCbWEy9g==","ID":"DATA-6471139f8cec40b3a5036a4b7e7857ab","SerialNO":3,"Stage":0}
{"Buffer":"9uGKSjzStcyfpueIHoFweg==","ID":"DATA-d24a9ceebeb740718bc03d3aec5c5aa4","SerialNO":4,"Stage":0}
{"Buffer":"yNNvqj1kLIVk0oJcldke8A==","ID":"DATA-6cbc81ac039b40689b8c5f9817a651d6","SerialNO":5,"Stage":0}
{"Buffer":"i3lYcS3mc6hPdvcqaj6Vqg==","ID":"DATA-c1e3082975b848c1b4a58a60a813006b","SerialNO":6,"Stage":0}
{"Buffer":"c595mvGHuZK0BeVpT1g2xQ==","ID":"DATA-d0b57736d5784f05aaa373c52e4aca1c","SerialNO":7,"Stage":0}
{"Buffer":"iPb8pCj+TeJfxlvGbAIaJQ==","ID":"DATA-644e1d54d9b041a7a886292e79aae8b8","SerialNO":8,"Stage":0}
{"Buffer":"Pdjo9mCD/gPAxb0oAApZ9g==","ID":"DATA-1afb3e6d00794fa0a22cdf271c548241","SerialNO":9,"Stage":0}
{"Buffer":"PzGic0LwgXVSlzorLPIlsg==","ID":"DATA-0256ac71307d4319862df26f3aece1aa","SerialNO":10,"Stage":0}

(以下略)

```

串在一起的結果，有 LOG 的輸出，證明資料有被 CLI-P1 吃進去處理了:

```text

C:\> dotnet CLI-DATA.dll | dotnet CLI-P1.dll > nul

[P1][2019/6/21 上午 12:31:36] data(1) start...
[P1][2019/6/21 上午 12:31:37] data(1) end...
[P1][2019/6/21 上午 12:31:37] data(2) start...
[P1][2019/6/21 上午 12:31:38] data(2) end...
[P1][2019/6/21 上午 12:31:38] data(3) start...
[P1][2019/6/21 上午 12:31:39] data(3) end...
[P1][2019/6/21 上午 12:31:39] data(4) start...
[P1][2019/6/21 上午 12:31:40] data(4) end...
[P1][2019/6/21 上午 12:31:40] data(5) start...
[P1][2019/6/21 上午 12:31:41] data(5) end...

(以下略)

```

我刻意把 CLI-DATA 的 ```GenerateData()``` 跟 CLI-P1 的 ```ReceiveData()``` 都抽出來，統一用 ```IEnumerable<DataModel>``` 來當作傳回值，目的就是像 RPC 一般，我期望透過某種標準機制，讓跨越 CLI 的資料傳遞過程抽象化，原始程式 CLI-DATA 產生的 ```IEnumerable<DataModel>``` 物件，可以原封不動的在 CLI-PI 也用一樣的模式還原回來。

這個例子簡單的證明可以透過 PIPELINE 傳遞物件了，這小技巧好好運用，可以寫出很多很方便的 CLI tools.


# 透過 PIPELINE 傳遞物件 (Binary)

如果你看不過去序列化成 Json 太佔空間或沒效率的話，我們也可以來試試 Binary Serialization. 剛才的抽象畫現在派上用場了。我們兩端做一點調整。CLI-DATA 只改序列化的部分，改成 .NET 內建的 ```BinaryFormatter``` 來序列化，其他不變:

```csharp
        
static void Main(string[] args)
{
    var formatter = new BinaryFormatter();
    var os = Console.OpenStandardOutput();

    foreach (var model in GenerateData())
    {
        formatter.Serialize(os, model);
    }
}

```

接收的部分一樣，CLI-P1 只改這段:

```csharp

static IEnumerable<DataModel> ReceiveData()
{
    var formatter = new BinaryFormatter();
    var istream = Console.OpenStandardInput();

    while (istream.CanRead)
    {
        yield return formatter.Deserialize(istream) as DataModel;
    }

    yield break;
}

```

二進位的輸出，有點難閱讀，反正大家知道輸出格式改過就好了 (喂):

```text

C:\> dotnet CLI-DATA.dll

              OAndrew.PipelineDemo.Core, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null   "Andrew.PipelineDemo.Core.DataModel   <ID>k__BackingField<SerialNO>k__BackingField<Stage>k__BackingFieldBuffer +Andrew.PipelineDemo.Core.DataModelStageEnum         %DATA-2a43a499a91947fd98e0f71ab4967e18   ?+Andrew.PipelineDemo.Core.DataModelStageEnum   value__                   b?3Q歋?:`b?              OAndrew.PipelineDemo.Core, Version=1.0.0.0, Culture=neutral, PublicKeyToken=null   "Andrew.PipelineDemo.Core.DataModel   <ID>k__BackingField<SerialNO>k__BackingField<Stage>k__BackingFieldBuffer +Andrew.PipelineDemo.Core.DataModelStageEnum         %DATA-d8bed3ac2a3a4a58af9376defc765cd2   ?+Andrew.PipelineDemo.Core.DataModelStageEnum   value__

(以下略)

```


想也知道，一樣可以執行 (茶):

```text

C:\> dotnet CLI-DATA.dll | dotnet CLI-P1.dll > nul

[P1][2019/6/21 上午 12:48:52] data(1) start...
[P1][2019/6/21 上午 12:48:53] data(1) end...
[P1][2019/6/21 上午 12:48:53] data(2) start...
[P1][2019/6/21 上午 12:48:54] data(2) end...
[P1][2019/6/21 上午 12:48:54] data(3) start...
[P1][2019/6/21 上午 12:48:55] data(3) end...
[P1][2019/6/21 上午 12:48:55] data(4) start...
[P1][2019/6/21 上午 12:48:56] data(4) end...
[P1][2019/6/21 上午 12:48:56] data(5) start...
[P1][2019/6/21 上午 12:48:57] data(5) end...

(以下略)

```



# 透過 PIPELINE 傳遞物件 (Binary + GZip)

我就先暫時當作 binary 的效率一定比 json 快好了 (其實不一定), 上一篇有提到，如果你的 shell (例如 ssh) 幫你搞定了跨網路傳遞 STDIO 的話, 其實你的 CLI 很容易跨越網路用 PIPELINE 串起來的，這時你也許會更在意傳輸資料的大小。同樣 1000 比資料，我特地把 CLI-DATA 輸出的結果導向到檔案，來看看總輸出大小。其中:

* Json 序列化的結果是: 108893 bytes
* BinaryFormatter 序列化: 430000 bytes

大小實在差距有點大啊... 過程中我能不能壓縮啊? 當然可以。不過你可別犯了 "手上有槌子，看到東西就想拿槌子敲下去" 的毛病啊! 都用 CLI 了，很多東西有現成的...。在 windows 的世界, gzip 沒有內建 T_T, 所幸我自己電腦上有裝了 Git, 裡面就包含了 ```gzip.exe``` 可以用...

我先把動作切兩段，先來看看怎麼把 CLI-DATA 產生的 data 壓縮:

```shell

C:\> dotnet CLI-DATA.dll | gzip.exe -9 -c -f > data.gz

```

順利產生名為 ```data.gz``` 檔案了。一樣 1000 筆資料的序列化內容，不過這次只有 47064 bytes


不過這個檔案內容真的可以用嗎? 同樣用 gzip 串起來執行看看:


```shell

C:\> type 3.gz | gzip.exe -d | dotnet CLI-P1.dll

[P1][2019/6/21 上午 01:19:18] data(1) start...
[P1][2019/6/21 上午 01:19:19] data(1) end...
[P1][2019/6/21 上午 01:19:19] data(2) start...
[P1][2019/6/21 上午 01:19:20] data(2) end...
[P1][2019/6/21 上午 01:19:20] data(3) start...
[P1][2019/6/21 上午 01:19:21] data(3) end...
[P1][2019/6/21 上午 01:19:21] data(4) start...
[P1][2019/6/21 上午 01:19:22] data(4) end...
[P1][2019/6/21 上午 01:19:22] data(5) start...
[P1][2019/6/21 上午 01:19:23] data(5) end...

(以下略)

```

還真的可以... 那我們最後在整個串起來執行一遍吧 (雖然這樣看起來很蠢，自己壓縮又立馬解壓縮):


```shell

C:\> dotnet CLI-DATA.dll | gzip.exe -9 -c -f | gzip.exe -d | dotnet CLI-P1.dll > nul

[P1][2019/6/21 上午 01:14:27] data(1) start...
[P1][2019/6/21 上午 01:14:28] data(1) end...
[P1][2019/6/21 上午 01:14:28] data(2) start...
[P1][2019/6/21 上午 01:14:29] data(2) end...
[P1][2019/6/21 上午 01:14:29] data(3) start...
[P1][2019/6/21 上午 01:14:30] data(3) end...
[P1][2019/6/21 上午 01:14:30] data(4) start...
[P1][2019/6/21 上午 01:14:31] data(4) end...
[P1][2019/6/21 上午 01:14:31] data(5) start...
[P1][2019/6/21 上午 01:14:32] data(5) end...

```

執行過程中，用工作管理員列出來看看，是不是真的有四個 process 執行中? (dotnet x 2, gzip x 2)

```text

Image Name                     PID Session Name        Session#    Mem Usage
========================= ======== ================ =========== ============
gzip.exe                     28192 Console                    1      6,540 K
gzip.exe                     10480 Console                    1      5,372 K
dotnet.exe                   21200 Console                    1     15,888 K

```

我按的速度不夠快，看來 CLI-DATA 那個 process 一瞬間就結束了，其他資料都卡在 pipeline buffer 等著後面慢慢消化中...

既然都要聊 CLI Tips, 我就附帶一個小技巧吧! 你知道 windows 內建 ```clip.exe``` 這個 CLI 小工具嗎? 他是個可以把 STDOUT 丟到剪貼簿的小工具。這可以怎麼用? 像上面的例子，我是下指令 ```tasklist.exe``` 得到的，我很懶得滑鼠整個選取再複製，這時我只要:

```shell

C:\> tasklist | clip

```

執行結束後，```tasklist.exe``` 執行的結果就直接放剪貼簿了，我只要 CTRL-V 就能貼上... 相當好用的小技巧。附上 help 說明，有興趣的朋友可以自己看:

```
C:\>clip /?

CLIP

Description:
    Redirects output of command line tools to the Windows clipboard.
    This text output can then be pasted into other programs.

Parameter List:
    /?                  Displays this help message.

Examples:
    DIR | CLIP          Places a copy of the current directory
                        listing into the Windows clipboard.

    CLIP < README.TXT   Places a copy of the text from readme.txt
                        on to the Windows clipboard.

```


# 使用 LINQ 過濾來自 PIPELINE 的物件

接下來再送上另一個小技巧。如果前一關傳過來的物件不是全都我要的怎麼辦? 標準做法是用 grep, 或是 find 這類指令來過濾就好了啊，就像前面例子要壓縮一樣，用其他命令列工具 ```gzip.exe``` 來處理就好。不過我們面對的是比較複雜的 "物件" 啊! 何況又是 binary (而且還壓縮過!!), 有些地方還是我們自己的程式碼來處理會好一點。

知道為何前一篇文章的範例，我要花上大半篇幅講 source code 內的處理方式嗎? 串流處理的原則，不管自己寫 code 或是用 CLI 都一樣，關鍵的原則就是取得一筆資料，就處理一筆資料。處理完一筆資料，就輸出一筆資料。只要每個過程都遵守這運作模式，你的動作就會像汽車工廠的生產線一樣，產物不斷的再產線上流動，不斷的會有成果輸出。

Pipeline 是在 OS 的層面做串流處理，C# 的 ```yield return``` 就是透過 ```IEnumerable<T>``` 介面當媒介，讓 foreach 也能用串流方式取得資料 (pull)。因此，我才會特地把 STDIN 反序列化後的東西，繼續用 ```yield return``` 傳出去，讓我的程式碼內也能繼續的用串流處理方式來消化資料。

這時，如果你熟悉 LINQ 的話就知道該怎麼用了。LINQ 是一組套用在 ```IEnumerable<T>``` 及 ```IQueryable<T>``` 介面上的 Extension, 能幫你用語言內建的 query 機制來處理內容。不過我們這次用的是 ```IEnumerable<T>``` 只提供 ```MoveNext()```, 只能單向巡覽一次, 因此別指望他有很好的 Query 效能 (背後也是一筆一筆過濾)，但是好處是當你 ```foreach``` 跑一半，中途就 ```break``` 離開迴圈的話，後面就不會再搜尋下去了。

繼續下去前，我們先複習一下這次處理資料的 Model 長啥樣:

```csharp

[Serializable]
public class DataModel
{
    public string ID { get; set; }
    public int SerialNO { get; set; }
    public DataModelStageEnum Stage { get; set; } = DataModelStageEnum.INIT;
    public byte[] Buffer = null;
}

```    

我們就加工一下，只挑出 ```SerialNO``` 是 7 的倍數, 只挑符合條件的前五筆處理! 來看看這樣的 code 可以怎麼改。先看看 CLI-P1 修改前:

```csharp

static void Main(string[] args)
{
    foreach(var model in ReceiveData())
    {
        DataModelHelper.ProcessPhase1(model);
    }
}

```

放心，我都很體貼讀者的，會貼上來給大家看得 code 都不會太長...，我們修改一下這段 code, 加上我們期望的過濾條件:

```csharp

static void Main(string[] args)
{
    foreach(var model in (from x in ReceiveData() where x.SerialNO % 7 == 0 select x).Take(5))
    {
        DataModelHelper.ProcessPhase1(model);
    }

}

```

有沒有覺得，除了多了一層反序列化的 code 之外，處理起來都跟正常的 code 沒兩樣啊! 結果當然如我們預期:

```shell

C:\> dotnet CLI-DATA.dll | gzip.exe -9 -c -f | gzip.exe -d | dotnet CLI-P1.dll > nul

[P1][2019/6/21 上午 01:46:11] data(7) start...
[P1][2019/6/21 上午 01:46:12] data(7) end...
[P1][2019/6/21 上午 01:46:12] data(14) start...
[P1][2019/6/21 上午 01:46:13] data(14) end...
[P1][2019/6/21 上午 01:46:13] data(21) start...
[P1][2019/6/21 上午 01:46:14] data(21) end...
[P1][2019/6/21 上午 01:46:14] data(28) start...
[P1][2019/6/21 上午 01:46:15] data(28) end...
[P1][2019/6/21 上午 01:46:15] data(35) start...
[P1][2019/6/21 上午 01:46:16] data(35) end...

```

看到封裝後的威力了嗎? 一行就搞定我們的需求了。體會到我前面講的了嗎? 花點心思妥善處理好 CLI 的輸入輸出規範，你會發現，你即使透過 CLI, 你也能夠很容易地用你熟悉的技能來處理資料。有時 CLI 就能搞定的問題，我就直接用 C# 處理掉了，不需要動用到 powershell, 也能解決我的問題。當然更複雜的狀況下，也許你開發 powershell cmdlet 會更方便，不過重要的是，你多了一種選擇，你可以更精準地挑選最適合你狀況的 solution. 如果你是 linux + .net core, 那搭配的 shell script, 一樣能運用這篇講的技巧。


# 小結

難得最近能有這種一個晚上就寫完的內容 XDD, 我還是同樣的論點，很多問題都不需要搬出大部頭的框架或是工具出來，只要你邏輯清楚，基礎知識有札實的打好，很多問題只要靈活的運用手邊現成的技巧就能漂亮解決的。這篇分享的 tips 就屬於這類, 各位就當我野人獻曝, 分享我覺得還不錯用的小技巧。有任何意見歡迎再我的粉絲團留言討論 :)