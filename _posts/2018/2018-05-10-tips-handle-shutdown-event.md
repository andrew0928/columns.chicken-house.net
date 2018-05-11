---
layout: post
title: "Tips: 在 .NET Console Application 中處理 Shutdown 事件"
categories:
tags: []
published: true
comments: true
redirect_from:
logo: 
---

會寫這篇實在有點意料之外，原本我只是想寫 service discovery 使用 consul 的應用案例啊，為了配合我之前推廣的 CDD (Container Driven Development, 容器驅動開發) 的想法，所有的服務開發，只要搭配 container 就都能簡化成 console application 模式就好，結果過程就碰到這個坑...。解決的過程中，也意外挖出不少 google 不到的細節，想想應該值得寫成一篇文章，於是就多了這篇...

Windows 畢竟是個以 GUI 竄起來的 OS, 有很多東西還是根深蒂固的綁在 windows 上。這次碰到的問題最後還是搬出 windows message, 視窗的運作基礎才解決掉的, 感覺繞了點遠路, 我也擔心跟這些機制綁住了，會不會產生不必要的相依性? 如果你知道有更好的做法，麻煩留個言指點一下~ :)



<!--more-->

回到原本的問題，問題很簡單，我要開發的 project type 是 .net framework / console application, 而在這程式哩，必須攔截程式結束的通知，讓開發者有機會做關閉前的處理。

windows program 常用的型態有三種: 

1. windows service
1. windows form
1. console application

我的目標鎖定在 console application 的原因很簡單，因為我希望開發出來的服務，能直接用在 shell script, 或是 container 內使用。透過 container 就能幫我解決一堆問題了，包括背景執行 (docker run -d --restart always, 也能有 start / stop / pause / unpause 等操作) 及各種部署與擴充性的簡化, windows service 模式或是 IIS host 就不再是絕對必要的了；沒有 GUI 的需求，因此 windows form 也不需要了。開發人員可以集中全力，用最單純的 console application 模式來開發，專注在問題本身即可。

然而，能夠讓 console application 結束的方式，大致上有這幾種:

1. 程式自行結束
1. 按下 CTRL-C / CTRL-BREAK
1. 使用者關閉視窗，或是工作管理員按下 End Task
1. 使用者登出 (log off)
1. 系統關機
1. 其他不可預期的程式終止 (如強制終止，或是強迫關機，或是斷電等等)

其實我本來心裡一直覺得這問題很簡單，只要查一查哪個 API 可以搞定這件事就結束了... 找了半天，找到一個我認為最適用的方式，一來夠低階 (用 kernel32 的 win32 api), 支援的事件型態也完全包含上面講的幾種 (ctrl-c, ctrl-break, log off, shutdown)... 雖然要動用到 P/Invoke, 但是也沒幾行, 搞定一次就沒事了... 於是就有 [方法1] 出現了...


# 方法 1, (Win32API) SetConsoleCtrlHandler

中間搜尋跟嘗試的過程我就跳過了，我直接跳到我 **一度** 認為可以使用的解決方案: [SetConsoleCtrlHandler](https://docs.microsoft.com/en-us/windows/console/setconsolectrlhandler) function, 底下是我第一版的 code:


```csharp
    class Program1
    {
        static void Main(string[] args)
        {
            // reg shutdown handler
            SetConsoleCtrlHandler(ShutdownHandler, true);

            {
                Console.WriteLine("# Service Started.");
                // do something...
                shutdown.WaitOne();
                Console.WriteLine("# Service Stopped.");
            }

            // un-reg shutdown handler
            SetConsoleCtrlHandler(ShutdownHandler, false);
        }


        #region shutdown event handler
        private static AutoResetEvent shutdown = new AutoResetEvent(false);

        [DllImport("Kernel32")]
        static extern bool SetConsoleCtrlHandler(EventHandler handler, bool add);

        delegate bool EventHandler(CtrlType sig);

        enum CtrlType
        {
            CTRL_C_EVENT = 0,
            CTRL_BREAK_EVENT = 1,
            CTRL_CLOSE_EVENT = 2,
            CTRL_LOGOFF_EVENT = 5,
            CTRL_SHUTDOWN_EVENT = 6
        }
        private static bool ShutdownHandler(CtrlType sig)
        {
            shutdown.Set();
            Console.WriteLine($"# Shutdown Program...");
            return true;
        }
        #endregion

    }

```

程式並不難，雖然動用到 P/Invoke 來呼叫 Kernel32 提供的 API .. 簡單的說 Windows 會在發生特定 event 時 (上面有定義的那幾個: CTRL+C, CTRL+Break, Close Window, Log Off, Shutdown), 會呼叫 Handler Routine, 你可以註冊你自己定義的版本，如果沒有就會用預設的, 照正常程序, 中斷 process 的運行。

我自己定義的 handler: ShutdownHandler(), 被通知到的話只會印一行訊息 "# Shutdown Program", 之後就會通知主程式的 shutdown.WaitOne(), 可以醒過來做後面要收尾的部分了。

其實程式看起來都沒問題，真正 run 起來也都正常。你可以親自試試，按下 CTRL-C 可以看到程式正常結束，你關掉視窗的那瞬間，也可以看到正確的訊息有印出來，代表有成功執行 (看不到的話，可以把 console output 改成檔案輸出)。我犯的最大錯誤在於，試到這邊都正常，我認定我使用這 API 的方式是正確的 (的確也是)，剩下的狀態我就沒有很認真的測試了，真正關機要觀察起來沒那麼方便，就被我擱著繼續去解決其他問題...


# 搬到 windows container 內測試

不過，把戰場轉移到我們真正要套用的情境: windows container, 是看看是否真的能夠攔截的到 container stop 的事件? 上述被我忽略掉的 test case 才又浮現出來... 我直接把他放到 container, 用這樣的程序去測試:

1. 先把編譯好的 console application 打包成 image
1. 啟動 container, 觀察 stdout (或是 logs) 確認程式已啟動
1. 停止 container, 觀察 stdout (或是 logs) 確認 shutdown 的動作是否正確的進行?

如果一切如計畫，我預期的結果是我對 container 下達的 docker stop 指令，應該能被 console application 偵測到並且做出反應。如果我下的指令是 docker rm -f, 那偵測不到我可以理解。因此上述程序做完後，我預期 container 應該會在 logs 輸出完整執行週期的訊息才對:

```log
# Service Started.
# Shutdown Program...
# Service Stopped.
```

上述的步驟，對應的指令與說明，我直接列在下方。這邊的步驟後面都一樣，我只在這裡交代一次詳細步驟，後面步驟都一樣，比照辦理即可。

## 1, 打包 container image

我用這個 dockerfile 來封裝這個 console application:

```dockerfile

FROM microsoft/dotnet-framework:4.7.2-runtime-windowsservercore-1709

WORKDIR   c:/test
COPY . .

ENTRYPOINT ConsoleApplication2.exe

```

接著用這道指令來 build container image, 如果你測試的環境是在別台 server, 那你 build 完之後要追加 docker push , 把 container image 推送到 registry 上面。

```

docker build -t wcshub.azurecr.io/demo.console .
docker push wcshub.azurecr.io/demo.console

```



## 2, 啟動 container, 觀察 stdout

接著啟動看看, 因為用 -d (daemon mode) 丟到背景執行了, 看不到 stdout 輸出。因此必須另外調出 logs :

```

docker run -d --name demo.console wcshub.azurecr.io/demo.console
docker logs demo.console -f

```

正確的話，應該會看到這樣的畫面:

![](wp-content/images/2018-05-10-tips-handle-shutdown-event/2018-05-11-01-59-31.png)


## 3, 停止 container, 觀察 stdout

我們開另一個 dos prompt 視窗，停掉這個 container, 藉此觀察看看, 我們的 console application 是否能偵測到 container 要被停掉的事件，印出對應的訊息?

在第二個 dos prompt 視窗輸入這指令:

```

docker stop demo.console

```

結果第一個 dos prompt (執行 container 的那個):

![](wp-content/images/2018-05-10-tips-handle-shutdown-event/2018-05-11-02-00-43.png)

原本 -f (follow, 會持續輸出 logs) 的狀態，因為 container 已經被 stopped 了, 因此直接就跳出來了。再結束前沒有看到程式攔截到關機訊號的輸出。

結果很不幸的，實驗結果證實，這個做法沒有辦法攔截到 docker stop 的事件。我試了好幾次 (前前後後大概有上百次了吧)，測試環境包含 windows 10 1709, 1803, windows server 2016, windows server 1709 ... (windows server 1803 的網卡 driver 還搞不定沒辦法測 T_T) 結果通通一樣。

可以確定這方式不可行了，逼的我繼續膜拜 google 大神跟 stack overflow 大神... 看來 SOD (**S**tack **O**verflow **D**eveloper) 這條路並不好走...







# 方法 2, (WinForm) Windows Message Pump

其實中間追查的過程曲折離奇，各種你想不到的方法我都嘗試過了...，我直接跳到結果就好。Microsoft 也很會藏文件，上一篇都說可以，點進去挖到這段我才恍然大悟。這是說明前面 SetConsoleCtrlHandler API 裡面點出去的 link:

[HandlerRoutine callback function](https://docs.microsoft.com/en-us/windows/console/handlerroutine)

![](wp-content/images/2018-05-10-tips-handle-shutdown-event/2018-05-10-23-01-02.png)



...

搞了半天，原來都是誤會一場。看起來很美好的東西，說明文字底下一定有幾行不顯眼的小字啊... 原來我一直期待的 CTRL_LOGOFF_EVENT 跟 CTRL_SHUTDOWN_EVENT 都只針對 window services 型態的 application 才有作用，所以我們做半天是白做的了。然而我需要的是 console application. 無奈找半天都找不到，stack overflow 很多人在問, 卻沒有任何一個答案...

看來，三種我能掌握的執行檔類型 (service, winform, console), 唯獨就是 console application 沒辦法。Window service 可以用上面的作法，而 windows form 則在 windows 的 message pump 體系裡面本來就包含了這些 message.. 果然 windows 是從 windows 3.1 發跡的, 所有功能都能在視窗模式下找的到，只有有視窗的才是第一公民啊，接著我又找到這篇:

[SystemEvents.SessionEnding Event](https://msdn.microsoft.com/en-us/library/microsoft.win32.systemevents.sessionending.aspx)

這篇吸引我的，是下列這段說明:

> This event is only raised if the message pump is running. In a Windows service, unless a hidden form is used or the message pump has been started manually, this event will not be raised. For a code example that shows how to handle system events by using a hidden form in a Windows service, see the SystemEvents class.

範例提到的 API，在 notes 裡面交代到, 如何在非 windows form 的環境下使用它? 做法是 create hidden window 專門負責接收對應的 message 就好了啊...。原來還有這招! 走 windows message 這條路的，只有有 create window handle 的程式才辦的到啊. 所幸 Microsoft 沒有限制 windows service / console application 不能 create window form ... 

他的範例程式在這篇，下方的 example 2:

[SystemEvents Class](https://msdn.microsoft.com/en-us/library/microsoft.win32.systemevents.aspx?f=255&MSPPError=-2147217396)

範例程式雖然是針對 service, 但是 console 也可以這樣搞啊! 他的範例程式我就不說明了，我直接依樣畫葫蘆 (砍了很多 code), 把剛才的 POC 改了一版:

```csharp
    class Program5
    {
        static void Main(string[] args)
        {
            var f = new Form1()
            {
                ShowInTaskbar = false,
                Visible = false,
                WindowState = FormWindowState.Minimized
            };

            Task.Run(() => 
            {
                //Application.EnableVisualStyles();
                //Application.SetCompatibleTextRenderingDefault(false);
                Application.Run(f);
            });

            Console.WriteLine("application startted");
            f.shutdown.WaitOne();
            Console.WriteLine("application stopped");
        }
    }
```

另外，我自己 create 的 Form1.cs 的內容 (visual studio 幫我產生的 Form1.Designer.cs 完全沒改):

```csharp

    public partial class Form1 : Form
    {
        public Form1()
        {
            InitializeComponent();
        }
        
        public AutoResetEvent shutdown = new AutoResetEvent(false);

        protected override void WndProc(ref Message m)
        {
            if (m.Msg == 0x11) // WM_QUERYENDSESSION
            {
                m.Result = (IntPtr)1;
                Console.WriteLine("winmsg: WM_QUERYENDSESSION");
                this.shutdown.Set();
            }

            //Console.Write('.');
            base.WndProc(ref m);
        }

    }

```

基本上結構跟前面的一樣，只是把 handler routine 搬到 form1 的 WndProc 這個 message 處理中心而已。一樣透過 AutoResetEvent 來跟主程式進行同步。改好 code 之後 (這版我沒有處理 CTRL-C, CLOSE-WINDOW 這些，我只處理 OS Shutdown)，我一樣用前面的方式，打包成 docker container 之後測試看看。這是 container stop 後的畫面:


![](wp-content/images/2018-05-10-tips-handle-shutdown-event/2018-05-11-02-05-29.png)

真是太神奇了，這樣就可以成功的攔截到關機事件了。


# 總結

搞到這邊，總算告一段落! 我終於能妥善的處理好 console application 在 container 內如何處理 shutdown 的事件了。令我很納悶的是，這種問題怎麼會是我第一個碰到? 幾乎都 google 不到相關資訊啊 (只有查到問題沒查到解答) ! 也許不用 windows container 之前，根本沒人打算用 console application 來處理 shutdown event 吧；也許 windows container 大家都是用 service 而非 console；也許 windows container 用的人還不夠多...

這就是我在私人 facebook 上面發的牢騷:

> 為了搞定 .net framework + windows container 某個功能, 竟然還要動用到 windows form ....

我講的就是這篇文章要搞定的問題。其實這件事困擾我很久了，幾個月前我讓同事幫忙處理這個問題 (我知道你有在看，就是你 XD)，但是當時的進度只到第一個做法就沒繼續挖下去了，直到最近我有點空檔，親自花了些時間研究，才挖出這堆東西。雖然身為資深的 Microsoft 陣營開發人員，但是還是不免抱怨幾句 XD

其實為了充分發揮 windows container 的成效，實作的過程中碰到的地雷還蠻多的，我寫這篇文章已經閃開好幾個我踩過的雷了... 其他沒寫在文章裡的小雷，隨便列舉就好幾個:

1. deamon mode 下 (docker run -d 啟動的模式), Console.ReadLine() 這行程式會引發 I/O Exception, interactive mode (docker run -t -i 啟動的模式) 則正常。
1. 只有在 daemon mode 下, hidden window 才能接收 message (原因: 黑人問號???), 同樣的 container, 你在 interactive mode 下面怎麼測都是失敗的。

其它類似狀況還有很多，不過跟主題不相關我就跳過去了。雖然如此我還是要讚嘆一下 windows container. 其實 microsoft 揹著這麼多年 windows 的包袱，能夠在 Linux 上原生發展出來的 docker 做到這樣的相容性，其實已經不簡單了。Windows 的整套系統就是跟 Win32 API 綁在一起的，OS Kernel 在設計概念上跟 Linux 就有很大的差別，但是卻要在最終部署的這個層次，做到 docker 架構的相容性，其實相當的不容易... 

看這次的案例，console application 程式也是得 create hidden windows 才能處理 shutdown event，在 windows 下有太多東西離不開 window (我在講什麼 @@). 這些設計在 server side 要完全拿乾淨反而很不容易，也因此可以想像，microsoft 在搞 container, 或是完全沒有 UI 的 nano server 過程中到底遭遇多少困難... 也難怪 Microsoft 要積極跟 Linux 靠攏，拿掉 Windows 部門，.NET Core 要能在 linux 上面執行等等，這些戰略看來都是為了加速丟開過去的包袱啊，否則 linux 的 container image 都是 MB 這種等級，而 windows 的 container image 都是 GB 等級...



// reference:

// docker run -d 可以, docker run -t -i 不行

// console / winform 兩用



















問題很單純，為了配合 windows container, 我希望用 .net console application 開發服務, 可以在 dockerfile 指定 entrypoint, 以便能在 container 啟動時一起啟動。同時也能偵測 container stop (查過文件，視同 OS shutdown), 讓 console application 在關閉前能有機會收尾 (另一篇講 service discovery, de-register 會用到)。一定要是 console application, 不能是 windows form, 也不能是 windows service，原因我稍後說明。


