現在 CPU 廠商大打 "多核心" 的口號, 讓大家都知道多核心的好處了, 不過每個評論的人也都會補上一句, "要有專為多核心設計的軟體才能發恢效能". 到底什麼叫作專為多核設計的軟體?

簡單的說, 就是程式不能再以單一流程來思考, 必需引用平行處理的概念. 就像工作分派一樣, 有十個人幫你做事, 一定比一個人好. 不過這也是考驗你分派及管理的能力. 做的不好, 可能工作還是都只有一個人在做, 另外九個在偷懶, 更糟的是還造成溝通的問題, 比只有一個人還糟.

在程式設計的領域裡, 實現平行處理, 它的困難有幾個:

1. 並行的流程控制
2. 多個程序之間的資料交換
3. Critial Section 問題 (某些絕對不能同時執行的程式片段)
4. 資料 Lock 及 Racing condition 的問題

早期的 Unix 提供的 fork( ) 就是個典型的例子, 呼叫後有兩份一模一樣的程式一起執行, 你要自己想辦法分出誰是誰, 然後讓它們各自執行. 兩個程式怎麼溝通? 只能靠 IPC (Inter-Process Communication), 方式不外呼開 socket 或是 share memory, 互相等待要靠 signal( )... 總之你大概會有 80% 以上的精力是在解決這些問題, 不是在解決你要處理的問題.

後來較新的 OS 紛紛引入了 thread 的關念, 解決了部份 IPC 問題, 其它的還是一樣困難. 直到 Java 出來, 寫 multi-threading 程式就簡單多了. 到了 .net 3.5, 又更進一步, 就是我這篇要講的主題.

在 MSDN Magazine 看到一篇文章, 覺的還不錯, 就貼上來跟大家分享一下心得. 原文在此:  
為多重核心電腦最佳化 Managed 程式碼  
[http://msdn.microsoft.com/msdnmag/issues/07/10/Futures/default.aspx?loc=zx](http://msdn.microsoft.com/msdnmag/issues/07/10/Futures/default.aspx?loc=zx)

細節我就不多討論了, 那篇文章裡面都說明的非常清楚, 很棒的一篇文章. 主要的重點是, 即使用了 Java / .NET 這樣的開發環境, 你仍然要面對許多 threading 的問題, 像是 thread 如何開始, 如何結束, 這個 thread 如何去通知另一個 thread 完成的問題. 但是大部份的情況下, 我只不過是有一堆工作, 想要丟給電腦處理, 最好就是所有可用 CPU 通通叫來幫忙...

這篇文章介紹的 TPL ( Task Parallel Library ) 很巧妙的利用 delegate, 把整套 Library 包裝的像一個 for loop 一樣簡單. 基本的觀念就是, 只要用它提供的類似 for loop 寫法改寫你的程式, 原本 loop 裡要執行 100 次的工作, 現在就會自動的分配到你所有的 CPU 一同執行. 聽起來很酷, 真的用起來也是如此. 我簡單貼一下內文兩段 sample code:

```csharp
// 一般的迴圈
for (int i = 0; i < 10; i++) {
    a[ i ] = a[ i ] * a[ i ];
}

// 改用 TPL 的迴圈
Parallel.For(0, 100, delegate(int i) {
    a[ i ] = a[ i ] * a[ i ];
});
```

上面兩段 code 做的事情都一樣, 就是把陣列 a 的內容, 每一筆都算平方, 再寫回來. 差別在於第一段程式會在同一個 thread 裡依序完成每一筆計算, 而第二個例子則利用 anonymous delegate, 讓 code 看起來像迴圈, 實際上每圈都是執行一次 delegate. 而這個 delegate 會自動透過 task manager 分配到合適的 thread 執行. 它跟 thread pool 有許多不同, 文章內有一些說明... 如此一來就能享用的到多核心 CPU 的好處, 你的每一個核心都會被充份的利用.

其實這樣的作法, 並不是 Microsoft 或是 .NET 特有的創新, 早在更重視效能的 C/C++ 就有了. Intel 就大力的支持了這個 open source project: [http://threadingbuildingblocks.org/](http://threadingbuildingblocks.org/) 裡面提供了大量的 C++ template, 也是用類似的方式替 C++ 加入了平行處理的支援.

ZD Net 上面有一系列的 video ([http://www.zdnet.com.tw/white_board/intel/video-8.htm](http://www.zdnet.com.tw/white_board/intel/video-8.htm)), 講的相當不錯, 我很認同裡面的幾個觀念, 主講人 James Reinders 提到, 平行處理你第一個應該要想到的是函式庫, 或是編譯器等等, 讓你的程式不自覺就能自動享用到平行處理的好處, 第二是用這類 library, 針對各種的 loop 去調整, 讓他能適用平行處理, 最後也是最不建議的作法, 才是大家常聽到的 multi-threading. 原因很簡單, threading 必需是你設計軟體架構就考慮進去的東西, 相對之下開發不易, 效能也不見得比較好, 更糟的是你可能會設計用 4 threads 來處理問題, 結果就是你的程式在超過四核的系統上就沒有明顯的效能增強了.

昨天晚上仔細的看完這幾篇文章, 果然科技的進步真是神速啊, 過去寫到翻掉的 Multi-Process 程式, 如今一個 For Loop 就解決掉, 沒走過這一段的人應該不能體會吧. 不過也因為這樣, 更能體會這些技術的價值在那裡. TPL 真的是個好東西, 強力推薦大家學一學!!

---

文中題到的 TPL 已經有 Tech Preview 可以下載了. 感謝 Unicorn 提供資訊.  
[http://www.microsoft.com/downloads/details.aspx?FamilyID=e848dc1d-5be3-4941-8705-024bc7f180ba&DisplayLang=en](http://www.microsoft.com/downloads/details.aspx?FamilyID=e848dc1d-5be3-4941-8705-024bc7f180ba&DisplayLang=en)

---

這篇是寫了貼在別的地方, 當然自己的 blog 也要貼一份... [H]