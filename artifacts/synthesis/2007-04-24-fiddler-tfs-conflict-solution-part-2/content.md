II.aspx/
  - /post/2007/04/24/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---II.aspx/
  - /post/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---II.aspx/
  - /columns/2007/04/24/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---II.aspx/
  - /columns/Fiddler-e8b79f-TFS-e79bb8e8a19de79a84e5958fe9a18ce8a7a3e6b1ba---II.aspx/
  - /blogs/chicken/archive/2007/04/24/2353.aspx/
wordpress_postid: 165
---

<<續上篇>>

計劃好之後, 我打算的流程是這樣:

1. Fiddler 存下目前的 Proxy Config 
2. Fiddler 把 WinINET 的 Proxy 改為 127.0.0.1:8888 
3. 在 OnAttach 裡加上自定的 Script, 就抄 (2) 的 CODE 改一改再把我要的值加上去

作法想好後, 連放 CODE 的地方都弄好了. Fiddler 直接用現成的 .net language 當成 script 使用, 就是直接修改 CustomRules.js 這個檔案. 裡面已經定義好 Method: OnAttach( ), 會在 Fiddler 開始 Capture Traffic 後被呼叫, 看來我要做的事 (3) 只要放在裡面就好, (1) 及 (2) 是 Fiddler 自己本來就會做的部份.

而 Fiddler 不再 Capture Traffic 時, 我什麼都不必作, 因為 Fiddler 預設的動作就是把 (1) 存下來的東西再填回 IE 的 Proxy 設定...

其實這方法還可以解決附帶的幾個問題, 像我在家用 VPN, 或是在公司用無線網路, Fiddler 也常常失效, 因為它預設都只改 [區域連線] 的 Proxy 設定... 不過 IE 又很貼心的讓每個 network adapter 都可以有自己的 proxy settings, 你只要不是用預設的 NIC 就沒救了. 雖然手動把你用的網路連線 proxy 改為 127.0.0.1:8888 就可以動, 不過每次都改也是很煩人...

好, 有足夠的誘因了, 開始動手...

**A 計劃:**

開始用 Reflector 追 Fiddler 的程式, Bingo... 主程式是 Fiddler.frmViewer, 我要的東西就藏在 oProxy 這個 static field 裡. 看了 oProxy 的型別是 Fiddler.Proxy, 繼續追下去... My God.... 截到宣告如下:

```csharp
internal WinINETProxyInfo piPrior;
private WinINETProxyInfo piThis;
```

piPrior 放的是存起來的設定, piThis 則是被 Fiddler 填入的設定, 沒救, private field... 連用 reflection 的機會都沒有, 只好放棄, 想第二條路...

**B 計劃:**

碰到鐵板, 繼續鑽別條路. 我先自己開個 console application 做簡單的測試, 先把 Fiddler.exe 改成 Fiddler.dll, 然後設定 project 參考這個 .dll, 依照 Fiddler 主程式的用法測了一下這段 code:

```csharp
static void Main(string[] args)
{
    WinINETProxyInfo proxy = new WinINETProxyInfo();
    proxy.GetFromWinINET(null);
    proxy.sHostsThatBypass = "*.chicken-house.net;*.hinet.net;";
    proxy.SetToWinINET(null);
    return;
}
```

哇哈哈, 真的有效, Run 過之後開控制台的 Internet Options 裡的 PROXY 設定, 真的被改過來了, 心想太好了, 這段 code 貼到 CustomRule.js 就一切搞定...

對, 這麼順利的話就不會分兩篇了, 誰曉得貼上去後 Fiddler 就給我唉這段 message:

![Fiddler script error](/images/2007-04-24-fiddler-tfs-conflict-solution-part-2/image04.png)

按了 [確定] 後就變這樣:

![Fiddler script compilation error](/images/2007-04-24-fiddler-tfs-conflict-solution-part-2/image09.png)

真是嘖嘖嘖... 大概猜的出問題在那, 這種外掛的 script 多半動態 Load Script, 動態 compile, 同時會載入到另一個獨立的 AppDomain, 看起來在 script 可用的範圍內, 是存取不到 Fiddler.WinINETProxyInfo 這個類別... 

AppDomain 真是讓人恨的牙癢癢的, 不過它還真是個很棒的設計. 在 .net 的世界, AppDomain 可以在不降低效能的前題下, 達到如傳統 OS Process 的安全隔離層級, 而且又有 thread 的快速 share data 方式... 可以說有 process 的好處, 又無 process 的負耽.

講那麼多幹嘛? 問題還是無解... 不過有了上面 console application 試驗後, 至少讓我證明這條路是可行的, 只不過 script 得再繞一條路試看看...

**C 計劃:**

我的目的只是要在 CustomRule.js 的 OnAttach 裡執行那四行 code 而以, 只好脫褲子放屁了, 四行可以搞定的事多花幾行來寫, 把之前搭配 Attribute 寫 Library 學到的那套 Reflection 搬出來用, 原本的這四行 code:

```csharp
WinINETProxyInfo proxy = new WinINETProxyInfo();
proxy.GetFromWinINET(null);
proxy.sHostsThatBypass = "*.chicken-house.net;*.hinet.net;";
proxy.SetToWinINET(null);
```

改寫為:

```csharp
System.Reflection.Assembly fiddler = System.Reflection.Assembly.LoadFrom(@"Fiddler.exe");

object proxy = fiddler.CreateInstance("Fiddler.WinINETProxyInfo");
Type proxyType = fiddler.GetType("Fiddler.WinINETProxyInfo");

proxyType.GetMethod("GetFromWinINET").Invoke(proxy, new object[] { null as string });
proxyType.GetProperty("sHostsThatBypass").SetValue(proxy, "http://ld-fsweb.learningdigital.com:8080;", null);
proxyType.GetMethod("SetToWinINET").Invoke(proxy, new object[] { null as string });
```

很好, 繞了一大圈, 結果還是不行... [:@], 結果跟 B 計劃一樣, 我就不貼了...

**D 計劃:**

好, 最後一招了, 別轉台... 實在是受不了了, 最沒品的那招拿出來用... 把 B 計劃寫的 Console App 拿來用, 東西都寫好丟在 Fiddler 的目錄, 檔名叫 myproxycfg.exe, 然後在 CustomRules.js 裡呼叫它...

```csharp
System.Diagnostics.Process.Start("myproxycfg.exe");
```

嗯, Fiddler 啟用 Capture Traffic 後, 果然就 OK 了, 這招都出了還不行就沒辦法了.. 吊個 .exe 在那邊看了實在很礙眼, 不過眼不見為淨啦, 可以 work 就好...

IE Proxy 的設定真的如我所料, Fiddler 啟動後就改掉了, Fiddler 停掉後就一切揮復原狀, [Y][Y][Y], 以後不用為了 TFS 要 Get Latest Version 還得去關 Fiddler ....

果然懶才是資訊科技進步的原動力啊, 哈哈.., 謝謝收看.