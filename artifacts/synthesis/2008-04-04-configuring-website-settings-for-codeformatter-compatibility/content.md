題外話，這個 plugins 又有小改版了，原網址可以 [下載](http://www.chicken-house.net/files/chicken/ChickenHouse.LiveWriterAddIns.zip).. 

到這邊差不多告一個段落了，歡迎各位下載回去用。只不過有些功能，你的BLOG SERVER要配合調整才會有效。統一說明一下: 

## 1. **CSS** 

我喜歡用這個函式庫的主要原因，是因為它長出來的HTML很乾淨，因為樣式的部份都拆出來到CSS了。不過缺點也是你必需另外想辦法把CSS放上去... 附上原廠提供的CSS內容，看你的BLOG SERVER可以怎麼改就怎麼改。以我用的CommunityServer為例，只要進入DashBoard，到修改版面的地方，它提供 "Custom Styles (Advanced)" 頁面，把 CSS 貼進去就搞定了! 

**C# Code Formatter CSS** [copy code]

```css
.csharpcode, .csharpcode pre
{
  font-size: small;
  color: black;
  font-family: Consolas, "Courier New", Courier, Monospace;
  background-color: #ffffff;
  /*white-space: pre;*/
}
.csharpcode pre { margin: 0em; }
.csharpcode .rem { color: #008000; }
.csharpcode .kwrd { color: #0000ff; }
.csharpcode .str { color: #006080; }
.csharpcode .op { color: #0000c0; }
.csharpcode .preproc { color: #cc6633; }
.csharpcode .asp { background-color: #ffff00; }
.csharpcode .html { color: #800000; }
.csharpcode .attr { color: #ff0000; }
.csharpcode .alt 
{
  background-color: #f4f4f4;
  width: 100%;
  margin: 0em;
}
.csharpcode .lnum { color: #606060; }
```

不過別急著貼!!! 如果你想要下一個功能的話，CSS 還要再多貼一段... 

## 2. **COPY CODE** 

這個功能不難，就透過 JavaScript 把一段文字放到剪貼簿就完成了。不過麻煩的是這些 CODE 怎樣偷渡到文章內容裡... 我用的 CS 預設會把 `<SCRIPT>` 給檔掉，直接在HTML裡加SCRIPT是行不通的。當然可以改communityserver.config，不過這樣有點麻煩，不喜歡這樣改... 於是我搬出了 HTC.. 

HTC 的原理很簡單，CSS是統一管理各種樣式，而DHTML的一堆事件，像 `onclick="..."` `onload="..."` 等等事件為什麼不能像CSS一樣統一管理呢? 可以的，只不過這就要靠 IE 才支援的 HTC (HTML Component) 才辦的到。後起之秀JQuery其實也有差不多的功能，不過要搭配 CS 的話，一樣得想辦法把 `<SCRIPT>` 給藏到HTML裡有點麻煩... 所以最後我還是選用 HTC 的方式來實作這個功能。 

設定很簡單，CSS 再加一段就好: 

**加上HTC支援的CSS** [copy code]

```css
.copycode {cursor:hand; color:#c0c0ff; display:none; behavior:url('/themes/code.htc'); }
```

再來就是把這個 [HTC](/themes/code.htc) 檔案放到 CSS 裡指定的目錄，以上面的CSS來說，你應該把HTC放在 /Themes/Code.HTC 

SERVER 的部份這樣就大功告成了。未來在插入CODE時，只要勾選這個選項 [產生出來的HTML會包含原始程式碼]: 

![image](/images/2008-04-04-configuring-website-settings-for-codeformatter-compatibility/image_9.png)

最後輸出的成果就會像這樣，標題右方的 [copy code] 功能就正常了。按下去之後，SAMPLE CODE 就會自動複製到剪貼簿，不會因為加了一堆格式，讓你複製下來的 CODE 不能直接使用... 

**MSDN Sample Code** [copy code]

```csharp
using System;

public class Sample {
    void Method() {
    Object Obj1 = new Object();
    Object Obj2 = new Object();
    Console.WriteLine(Obj1.Equals(Obj2)); //===> false
    Obj2 = Obj1;
    Console.WriteLine(Obj1.Equals(Obj2)); //===> true
    }
}
```

這個功能，在預覽的時後就沒加上去了。另外預覽的畫面也做了點調整，一方面不是直接用IE開啟HTML檔，因為這樣會有一堆安全警告的訊息，我改用HTA (HTML APPLICATION)來實作預覽的功能。為了感謝提供這個LIB的原作者，我也在預覽的畫面裡加上他的首頁了。最後，當然也要讚助一下我自己的網站... 哈哈 :D 

![image](/images/2008-04-04-configuring-website-settings-for-codeformatter-compatibility/image_8.png)

好，這個PLUGINS大概就告一個段落，未來大概就修正BUG了，需要的人歡迎下載使用。如果要散佈請注明出處。 

[下載位置](http://www.chicken-house.net/files/chicken/ChickenHouse.LiveWriterAddIns.zip)