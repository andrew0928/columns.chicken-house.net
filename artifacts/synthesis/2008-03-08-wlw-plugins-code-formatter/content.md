最近常常貼一些需要附上程式碼的文章, 我都借助 [c# code format](http://manoli.net/csharpformat/) 這網站幫忙轉, 轉成好看一點的 HTML code.. 然後 Live Writer 切到原始碼的模式去改 HTML, 然後再切回來際續編... 

人果然是懶惰的動物, 之前久久寫一篇還好, 最近就開始不耐煩了... 試了一套 Syntax Highlight 的 WLW plugins, 畫面不錯, 不過中文會亂掉.. 想說 c# code format 這網站的主人有 share source code, 我就把它拿來包成 Windows Live Writer Plugins 好了... 

就是這念頭開始寫這個 project, 蠻好寫的, 兩三個小時過去就堪用了, 經過幾天試用慢慢改成現在的樣子, 先現寶一下, 放幾張圖: 

[圖 1] 編輯畫面
![image](/images/2008-03-08-wlw-plugins-code-formatter/image_5.png)

[圖 2] 預覽畫面 (底下當然要加點廣告... )
![image](/images/2008-03-08-wlw-plugins-code-formatter/image3.png)

結果就不用貼圖了, 底下這段就是用這 plugins 貼進來的... 

**[程式 1] 這是測試程式**

```csharp
using System;
using System.IO;
using System.Threading;

public class Program {
  public static void Main(string[] args) {
    Console.WriteLine("Hello!!" );
  }
}
```

看起來效果還不錯, 雖然跟之前差不多, 不過手工的部份少很多, 貼上, 按 OK, 就收工了! 這個 c# code format 提供的 library 還不賴, 效果也是我試用幾種 lib 後比較滿意的, 滿意的地方是: 

1. Pure C# 開發的, 程式很短, 不過看的出作者功力不錯, 架構啥都棒. 
2. 用習慣了, 之前都用它網站版本的. 很熟悉它轉出來的格式. 
3. 轉出來的 code 比較乾淨. 不過它需要另外搭配它的 CSS. 
4. Unicode, 沒有什麼中文亂碼的問題.

當初最主要用它的原因就是 (3), 其它捨棄 CSS 的結果, 就是產生出來的 HTML 參著一大堆 color code, 老實說這種 HTML code 看起來就很痛苦. 我是不想看啦, 不過我必需切到 HTML view 去貼上這堆字啊...  c# code format 雖然要另外補上 .css, 不過看起來就清爽多了. 我直接把它附的 CSS 貼到我用的 community server 的 custom themes 裡 (部落格管理裡面就可以直接加, 不用改檔案), 用起來就很輕鬆愉快了 :D 

要來看 code 嗎? 其實 code 就沒什麼好看的了, 需要的直接抓回去看吧. 倒是不常寫 WinForm 的我, 竟然被內建的 ComboBox 小整了一下... WinForm 內建的 ComboBox 功能很完整, Items 可以放 object, 然後再指定 ValueMember, DisplayMember... blah blah. 當然也有直接提供最簡單的 Text Editor, 一行字就是一個 Item ... 

![image](/images/2008-03-08-wlw-plugins-code-formatter/image_8.png)

不過, 我要的是很簡單的 Value / Display 分別指定就好, 就是這個 plugins 讓 user 選擇格式的地方 (如上圖), 我希望第一項的 Value 是 "HTML", 而顯示的是 "HTML / XML / ASP.NET", 這樣簡單的要求, 我心裡想... 這麼簡單, 一定可以直接用 Designer 填一填就搞定, 不用再去寫 code, 就可以 init 完成.. 

沒想到找了半天還真的找不到! :@ 翻了 MSDN, Microsoft community 等等技術支援網站通通都沒有. 教的都是一堆我覺的拖褲子放屁的作法... 不過是五個固定的選單而以啊... 

到最後, 宣告放棄, 妥協了... 我這個功能最後是用這幾行 code 搞定的... ㄨ!!! 本來一行 code 都不想寫的... 

**替 ComboBox 設定初始值的程式碼片段:**

```csharp
comboBox1.DisplayMember = "Value";
comboBox1.ValueMember = "Key";
comboBox1.Items.Add(new KeyValuePair<string, string>("HTML",  "HTML / XML / ASP.NET"));
comboBox1.Items.Add(new KeyValuePair<string, string>("CS",    "C#"));
comboBox1.Items.Add(new KeyValuePair<string, string>("VB",    "Visual Basic.NET"));
comboBox1.Items.Add(new KeyValuePair<string, string>("MSH",   "MSH (PowerShell)"));
comboBox1.Items.Add(new KeyValuePair<string, string>("SQL",   "T-SQL"));
comboBox1.SelectedIndex = 1;
```

哈, 最後這邊收的不大漂亮, 不過不管了, 還好沒幾行. 這個 plugins 需要的就自己抓去用吧, 以後可能會不定時更新. 有啥改進意見可以留話給我, 不過嘛, 當然是有空 & 想改才有動力去開 visual studio .. [H] 

--
下載: [code formatter plugins](http://www.chicken-house.net/files/chicken/ChickenHouse.LiveWriterAddIns.zip)