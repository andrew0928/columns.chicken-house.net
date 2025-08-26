---
layout: post
title: "[CODE] 可以輸出到 TextBox 的 TextWriter: TextBoxWriter!"
categories:

tags: [".NET","ASP.NET","C#","多執行緒","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2011/01/03/code-可以輸出到-textbox-的-textwriter-textboxwriter/
  - /columns/post/2011/01/03/CODE-e58fafe4bba5e8bcb8e587bae588b0-TextBox-e79a84-TextWriter-TextBoxWriter!.aspx/
  - /post/2011/01/03/CODE-e58fafe4bba5e8bcb8e587bae588b0-TextBox-e79a84-TextWriter-TextBoxWriter!.aspx/
  - /post/CODE-e58fafe4bba5e8bcb8e587bae588b0-TextBox-e79a84-TextWriter-TextBoxWriter!.aspx/
  - /columns/2011/01/03/CODE-e58fafe4bba5e8bcb8e587bae588b0-TextBox-e79a84-TextWriter-TextBoxWriter!.aspx/
  - /columns/CODE-e58fafe4bba5e8bcb8e587bae588b0-TextBox-e79a84-TextWriter-TextBoxWriter!.aspx/
wordpress_postid: 12
---

吃葡萄不吐葡萄皮... 對，這不是繞口令... 哈哈...。

先祝各位 2011 新年快樂!! 這幾個月忙翻了, 一方面系統要移轉到 windows azure, 另一方面要改善原本系統的排程 (原本是 console app + scheduler task service), 現在要用 windows service 來取代, 突然之間之前覺的工作上用不到的 multi-threading 技巧, 現在都派上用場了...

題外話先扯一下, 在 azure 因為架構上就已經把 web role (presentation layer) / worker role (business logic layer) / azure storage (data layer) 分的很清楚, 相對的每一層之間的 communication 時間就拉長了, 我們碰到的狀況就是 worker role 對 azure storage 有大量的 I/O 的話, 效能就很糟糕... 在這邊用了[生產線](/post/RUN!PC-e7b2bee981b8e69687e7aba0-e7949fe794a2e7b79ae6a8a1e5bc8fe79a84e5a49ae59fb7e8a18ce7b692e68789e794a8.aspx)的模式, 結果效能提升了十幾倍... 果然[前輩](http://ruddyleemsblog.wordpress.com/)說的沒錯: 架構對了，什麼事都變簡單了...

另一個案例則是把原本靠 windows task scheduler 執行的排程，改成用自行開發的 windwos service ... 不過開發成 service 實在是不大好除錯, 再加上多執行緒先天也是除錯不易... 因此開發階段都寫成windows form, 提供 START / STOP / PAUSE / CONTINUE 等控制的功能，簡化前段的開發作業。

azure / service 都用到了不少多執行緒的技巧, 改寫成 service 也用了老字號的 Cassini 解決另一部份的問題，這些都是值得介紹一下的部份，不過今天主題不在這，改天另起專欄再說。在改寫成 windows service 的過程中，需要把過去寫成 Console application 的 code 移到 service ，而過去這些程式都直接用 Console.Out 這個 TextWriter 輸出訊息到 DOS command prompt / log file, 移到 windows form 之後, 要輸出到 TextBox 就變的麻煩了點, 本來不想理它, 後來發現不好好處理這個問題還不行...

如果不講究 code 好不好看，其實改一下程式就可以了，把原本的 Console.Out.WriteLine( ) 改成 [TextBox.AppendText( )](http://msdn.microsoft.com/en-us/library/system.windows.forms.textboxbase.appendtext(v=VS.90).aspx) 就好，但是...

1. 原程式得改寫，不能直接用 TextWriter ... 另外, 很多現有的函式庫都接受 TextWriter, 不能靠 TextWriter 輸出的話程式會變很雜
2. 只有 create control 的 UI thread 可以呼叫 AppendText( ) ...
3. thread-safe 的問題: 輸出的訊息會交錯輸出, 無法閱讀
4. 長時間連續執行，TextBox 的訊息會太多, 得要有 recycle 的機制
5. 最好可以順便寫 LOG 檔...

老實說，除了 (1) 之外，其它點都是自己寫個專用的 OutputLog method 就可以解決。不過考量到程式未來真正執行時，是在 service 的環境, 在那邊是沒有 TextBox 這種 UI control 的, 最終還是要透過 TextWriter 輸出到 log file, 或是透過 socket 輸出... 何況用 TextWriter 輸出 log 也比較符合抽象化的原則, 不需要去碰到太多輸出方式的細節...

問題跟目的都搞清楚之後，接下來就是實作了。這次實作目標就是要想個辦法，用 TextWriter 的方式輸出 LOG 訊息，而這些訊息要自動呈現在 WebForm 的 TextBox control 上, 就好像在 DOS command prompt 裡執行 console application 一樣。先來想像一下 code 寫起來跟看起來是什麼樣子:

```csharp
private TextWriter output;
public Form1()
{
    InitializeComponent();
    this.output = TextWriter.Synchronized(new TextBoxWriter(this.textBox1));
}

private void Form1_Load(object sender, EventArgs e)
{
    for (int i = 0; i < 300; i++)
    {
        this.output.WriteLine("{0}. Hello!!!", i);
    }
}
```

建立好 TextWriter 之後，後面只管用這 writer 輸出訊息，對應的 TextBox 自然就會像 terminal 般，不斷的跑出訊息出來...

![image](/images/2011-01-03-code-textwriter-that-outputs-to-textbox-textboxwriter/image_11.png)

基本要求達到了，這就是我要的功能。其實這東西上網 [GOOGLE](http://www.google.com.tw/search?hl=zh-TW&source=hp&biw=1024&bih=1219&q=textboxwriter&aq=f&aqi=g2&aql=&oq=&gs_rfai=) 一下, 類似的例子也有, 不過一來寫起來沒幾行, 二來功能跟我要的有點出入... 想想還是自己寫一個。先來看看這個 writer 是怎麼實作的?

TextWriter 要實作並不難，不過不熟悉的話，也是得花些時間才能搞定。主要是 TextWriter 的 [Writer( )](http://msdn.microsoft.com/en-us/library/system.io.textwriter.write(v=VS.90).aspx) 跟 [WriterLine( )](http://msdn.microsoft.com/en-us/library/system.io.textwriter.writeline(v=VS.90).aspx) 就共有 35 種不同的多載... HELP 沒有清楚的寫到這堆 method 之間的關係，一時也不知 override 那一個的效果是最好的...。一開始我是從最基本的 void TextWriter.Write(char value) 下手, 結果效能慘不忍睹... 輸出一行字就要一秒鐘, 好像回到了當年DOS時代加上倚天中文後, 按個DIR字是一行一行跑出來的光景... Orz, 後來花了點時間追蹤這卅幾個 method 的先後關係，才改了這個效能 OK 的版本:

```csharp
public class TextBoxWriter : TextWriter
{
    private TextBox _textbox;
    public TextBoxWriter(TextBox textbox)
    {
        this._textbox = textbox;
    }

    public override void Write(char value)
    {
        this.Write(new char[] { value }, 0, 1);
    }

    public override void Write(char[] buffer, int index, int count)
    {
        if (this._textbox.InvokeRequired)
        {
            this._textbox.Invoke((Action<string>)this.AppendTextBox, new string(buffer, index, count));
        }
        else
        {
            this.AppendTextBox(new string(buffer, index, count));
        }
    }

    private void AppendTextBox(string text)
    {
        this._textbox.AppendText(text);
    }

    public override Encoding Encoding
    {
        get { return Encoding.UTF8; }
    }
}
```

其中補充說明一下, 在 line 14 ~ 21 為何要大費周章的, 把要呼叫 AppendTextBox( ) 的動作, 放到 delegate, 再交由 TextBox 控制項自行 Invoke 呼叫 ? 這是源自 windows form 的一條規範, 要是你寫的程式有多執行緒的應用，一定要知道這鐵律:

> *UI thread 的限制: 只有 create control 的 thread 可以更動 control 的狀態。*

如果不遵守這個規則，執行時就會被警告:

![image](/images/2011-01-03-code-textwriter-that-outputs-to-textbox-textboxwriter/image_12.png)

解法就參考 line 14 ~ 21 的部份就好，說明的話 darkthread 這篇講的很清楚, 我就不客氣直接引用了 :D

[http://blog.darkthread.net/blogs/darkthreadtw/archive/2007/09/29/tips-about-ui-thread-limitation.aspx](http://blog.darkthread.net/blogs/darkthreadtw/archive/2007/09/29/tips-about-ui-thread-limitation.aspx)

不過，這樣只是達到基本需求而已，還有其它的問題... (3 ~ 5), 太久沒寫文章了，沒想到一篇寫不完... 請待下回分解 :D
