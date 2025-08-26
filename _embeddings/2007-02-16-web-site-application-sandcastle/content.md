這次要解決的問題, 跟上次想要[在 Web Application 裡執行單元測試](/post/e588a9e794a8-NUnitLite2c-e59ca8-App_Code-e4b88be5afabe596aee58583e6b8ace8a9a6.aspx)的問題類似, C# 有跟 Java 類似的 comment help, 可以把寫在註解的文字萃取出來, 製作成一份文件...

不過, 過去的 NDoc, 到現在新掘起的 [SandCastle](http://www.microsoft.com/downloads/details.aspx?FamilyID=E82EA71D-DA89-42EE-A715-696E3A4873B2&displaylang=en), 都要求兩個東西:

1. Assembly Files: 可以透過 reflection api, 取得 asm 的 metadata
2. Compiler 在 compile code 時匯出的 xml document

通常 help 製作工具都需要這兩種檔案才能制作 help, 不過 asp.net 2.0 引進的 web app, 正常情況下跟本拿不到這些東西, 因為 code 只要丟在 App_Code 就可以跑了, 跟本不需要 compile 成 dll, 更不用說 xml document 了.... 想到幾種可能可行的辦法, 今天就抽空試了一下:

## 在 web.config 裡加上 compiler option 輸出 xml

要產生 dll 倒不難, 有一堆方法, 可以用 [aspnet_compiler.exe](http://search.msdn.microsoft.com/search/Redirect.aspx?title=ASP.NET+Compilation+Tool+(Aspnet_compiler.exe)+&url=http://msdn2.microsoft.com/en-us/library/ms229863(VS.80).aspx) 這個工具, 直接 build web site, 可以輸出 DLL. 不過還缺 xml doc, 翻了翻 MSDN, 找到一條路, 就是在 web.config 裡可以加 compiler options.. 加上去之後, 就會產生 xml document...

```xml
<configuration>
    <system.codedom>
        <compilers>
            <compiler ...... compilerOptions="/doc:c:\sample.xml" />
...
```

簡單寫個 web app 試了一下可以 work, 但是放到 production site 就不行了, compile 的過程中, 你會看到這個 xml 檔案不斷的產生出來, 又被砍掉... 原來 App_Code 目錄下, aspnet engine compile 的方式是以目錄為單位, 每個目錄下的 *.cs 會被當成一個 project compile 一次, 換個目錄再來一次, 所以你指定的 xml document 檔會不斷的被覆蓋...

氣的是這個參數還一定得指定檔名, 不能指定 *.xml 或是不指定之類的... 所以除非你的 App_Code 目錄下只有一層, 不然就放棄吧..

## Web Deployment Project

Visual Studio 2005 有個附加的 [Web Deployment Project](http://msdn2.microsoft.com/en-us/asp.net/aa336619.aspx), 在 SP1 之後就直接內建了, 它大概的作法就是 aspnet_compiler.exe 先輸出一堆 assembly, 然後再用 asm merge tools 把它併成單一個 assembly dll file. 是可以很簡單的拿到 dll 了, 不過產生 xml document 的部份仍然一樣無解

## 寫 msbuild project file

在 google 查這個問題時, 看到有老美用的作法是自己寫一段 task, 把所有 *.cs 加到 [csc task](http://search.msdn.microsoft.com/search/Redirect.aspx?title=Csc+Task+&url=http://msdn2.microsoft.com/en-us/library/s5c8athz.aspx) 裡... 不過太麻煩了, 一來我整個 build 程序沒有用到 msbuild project file, 二來我也不熟, 寫起來有點辛苦..

## 手動下 CSC.exe 指令

來硬的, 我自己想辦法生個 dll + xml 總可以了吧, 反正我的目的只是要 help, dll 用完就丟也沒關係, 只要我不要寫兩份 code 就好. [查了一下指令](http://search.msdn.microsoft.com/search/Redirect.aspx?title=Working+with+the+C%23+2.0+Command+Line+Compiler+&url=http://msdn2.microsoft.com/en-us/library/ms379563(vs.80).aspx), 可以這樣用:

```
csc.exe /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs
```

哇哈哈, 這次就成功了, dll 跟 xml 都成功的產生出來, 之後就丟給 NDoc / Sandcastle 就解決了. 額外抱怨一下, 雖然 SandCastle 能夠處理 .net 2.0 額外的功能, 像 generic 等等, 不過速度真是爆慢... Orz, 以前用 NDoc 約 20 min 能夠 build 好 chm, 現在用 sandcastle 要跑 60 min ... 

雖然如此, 不過這個方法還是有幾個缺點.. 列一下我已經確定的:

1. App_Code 下可以包含 source code 以外的檔案.  
   除了 .cs 這種 source code 會被自動編譯之外, 還有其它型態的檔案也會自動被處理. 比如 wsdl 放著就會自動 gen web service proxy, xsd 放著就會自動 gen typed dataset 的 source code... 這些是單用 csc.exe 沒辦法解決的

2. 另外像 .ascx .aspx 對應的 cs, 也無法用 csc.exe 處理, 因為還有另一半的 partial class 是由 template file 會透過 asp.net engine 動態 parsing 後產生 .cs 再一起 compile, 這部份也沒有辦法單靠 csc.exe 處理掉

3. 理論上還是有辦法把這些動作加在 batch file 或是 msbuild task 裡, 不過這些通通做下來, 那等於你自己搞一個 aspnet_compiler.exe 了... 工程太大, 不划算...

最後我選擇放棄這些遺漏的部份. 因為 help file 主要就是為了能共用的 class library 能有對應的文件, 上面漏掉的三塊都不大會有 comment help 產出, 唯獨 .ascx 還是很需要 help, 不過在沒有更方便的工具之前就先不管它了... 哈哈