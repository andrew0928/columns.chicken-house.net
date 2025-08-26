有在寫 .net / java 的人, 大概都聽過這套很有名的 framework ... JUnit / NUnit. NUnit 是從 JUnit 那套移過來的, 用法觀念大同小異, 不過 porting 到 .net 卻是充份的應用到了 .net 提供的優點...

Microsoft 在 ASP.NET 2.0 提供了一個很有用的機制, 就是在你的 web application 下, ~/App_Code 目錄下的所有 code 都會被視為 source code, 在 ASP.NET Hosting 環境下會自動的編譯及執行. 意思就是 source code 丟進去這目錄就 ok 了, 不需要手動執行 compile 的動作.

這便民的機制卻引來不少困擾, 最大的問題就是某些一定要找的到 assembly (.dll) 檔案的情況下, 少掉 dll 就變成是件麻煩事. 我自己碰到的情況就是這樣, 我想要依賴 App_Code 帶來的好處, 但是我又希望能替 App_Code 下的程式碼寫單元測試案例, 問題來了:

1. App_Code 沒有對應的實體 *.dll  
   雖然在 c:\Windows\Microsoft.NET\Framework\Temporary ASP.NET Files\ 下找的到, 但是目錄編碼過, 每次都有可能不一樣, 就算找的到也很不方便 

2. App_Code 下的程式大都仰賴 ASP.NET Hosting 提供的環境才能執行  
   比如 HttpContext ... NUnit 提供的 Test Runner 會另外用獨立的 AppDomain 下執行, 結果是跟 Hosting 環境相關的 code 就沒機會測試了

試了半天, 宣告放棄, 實在是找不到好方法完成這任務... Microsoft 自己的 Unit Test Framework 出局, NUnit 也出局, 我甚至去挖了 NUnit 的 source code 來看, 看的臉都綠了...

NUnit Test Runner 做的非常嚴謹, core 裡就把每個 test 執行的環境準備好了獨立的 AppDomain, 從指定的 assembly 載入 class 後就會丟到獨立的 AppDomain 下開始跑 test ... 本來想改掉, trace 了一陣子後就放棄了, 我只是要跑單元測試啊, 我不想要有我自己改過的 NUnit Framework 啊啊啊啊...

後來 google 找了一堆相關網站, 總算找到救星了... [NUnitLite](http://www.codeplex.com/Wiki/View.aspx?ProjectName=NUnitLite). 看了它的 [vision](http://www.codeplex.com/Wiki/View.aspx?ProjectName=NUnitLite&title=NUnitLite%20Vision), 不錯, 正好是我需要的...

---

**The NUnitLite Vision**

NUnitLite is a lightweight test framework for .Net, implementing a limited subset of NUnit's features. It will use minimal resources and be suitable for execution on various classes of devices.

**NUnit itself is fairly full-featured and becomes more so with each release. As a result, it is difficult to use in certain projects, such as embedded applications and testing add-ins for other software products**.

NUnitLite is delivered as source code only, for inclusion directly in the users' test projects. It will not suffer the weight of NUnit features like extensibility, a gui, multi-threading, use of separate AppDomains, etc. **All these features have their place but they can generally be dispensed with in resource-limited situations or when the tests must run in some special environment**.

The NUnitLite codebase is completely separate from NUnit, although obviously inspired by it. Features added to one pof the two products will not automatically be incorporated in the other.

NUnitLite will initially support Microsoft .Net, Mono and the .Net compact framework.

---

我標紅字的地方, 就是我最需要 NUnitLite 的原因. ASP.NET web sites 正好運作方式就像 IIS 的 add-ins 一樣, 本來就很難獨立的運作, 本來就很難把要測試的部份抽出來. 就算硬抽出來, 能測的程式碼函蓋率一定也不高. 想想看, 你的 ASP.NET code, 都不用到 HttpContext (Application, Session, Request, Response... ) 的部份, 佔了多少比重? 剩下的那部份完全不會出錯嘛?

總之現在已經找到滿意的 solution 了 [:D], 雖然 NUnitLite 只有 0.1.0.0 而以, 而且最新的 release 還不能 build...  =.= 不過至少也能很有效的解決我問題了 [:D]

實際的用法, 下次再改貼另一篇...