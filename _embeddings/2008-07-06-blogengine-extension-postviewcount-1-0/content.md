這篇拖好久了，本來上禮拜要寫，結果正好碰到 [BlogEngine 1.4 RELEASE](http://www.codeplex.com/blogengine/Release/ProjectReleases.aspx?ReleaseId=9451)，就一直拖到現在...。之前找到一個給 BlogEngine 用的 [Counter Extension](http://mosesofegypt.net/?tag=/blogengine.net+extensions)，以功能來說還不錯用，不過用久了就開始不滿足了。正好翻到[這篇教學文章](http://rtur.net/blog/post/2008/07/04/Writing-extensions-for-BlogEngine-14-(part-1).aspx)，算是官方文章了吧 (BlogEngine 作者之一寫的教學文)? 所以就動起自己寫的念頭。舊的其實沒什麼不好，不過缺了這幾項我想要的功能:

1. 只有計 Total Count (謎: 不然你要 counter 記什麼?)
2. 資料檔的結構及 I/O 的設計有點 Orz...
   1. 讀寫 XML 的 CODE 寫的很... Orz
   2. 沒有處理同時讀寫的問題 (後面寫的資料可能會蓋掉前面的，我的點閱率不知道少了幾百次 :D)
   3. 要有 CACHE 來加速處理速度

既然要重寫，當然要寫個合用的. 底下是我對於新的 COUNTER 期望:

1. 要能記流水帳。  
   流水帳就是不只要記總數，我還要知道每次點閱的時間，來源 IP ... 等等  
   ( [darkthread](http://blog.darkthread.net/) 指示: 當你流量大的時後就不會去在意這個了... Orz, 真是一針見血... )
2. 要處理多執行緒下讀寫資料檔的問題，這部份 Code 必需為 ThreadSafe。
3. 妥善利用 CACHE，降低 (2) 的複雜度。
4. COUNTER COMPACT  
   配合 (1) 的需求，流水帳記錄太多的話也會造成問題，COUNTER要能適當的刪除舊的 HIT RECORD。

決定好後就動工了! 既然問題都圍繞在 data storage 上，先來看看原來的檔案格式:

**原有的 ~/App_Data/PostViews.xml 片段:**

```xml
<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<posts>
    <post id="b43ec49e-e9a2-4696-bcc7-2ba1667ecda9">781</post>
    <post id="f1411c11-11ed-4f35-b383-0c6c8b2b963a">603</post>
    <post id="e7b57492-652b-4247-bcd4-bc3ac2e56318">589</post>
    <post id="7e2c2c88-240c-40ea-8477-2c96880adc8e">556</post>
    <post id="0fda9c32-d294-4f09-85cd-41dab8e677cb">678</post>
    ......
</posts>
```

很普通的格式，配合我的需求，新的檔案結構我打算改成這樣:

**新的 ~/App_Code/counter/{post-id}.xml 檔的片段內容:**

```xml
<?xml version="1.0" encoding="utf-8"?>
<counter base="8828">
  <hit time="2008-06-29T12:42:51" referer="" remote-host="66.249.73.185" user-agent="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)" />
  <hit time="2008-06-29T13:04:15" referer="http://www.google.com.tw/search?complete=1&amp;hl=zh-TW&amp;cr=countryTW&amp;rlz=1B3GGGL_zh-TWTW237TW238&amp;q=%E9%A6%99%E6%B8%AFg9&amp;start=30&amp;sa=N" remote-host="124.10.1.162" user-agent="Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-TW; rv:1.9) Gecko/2008052906 Firefox/3.0" />
  <hit time="2008-06-29T13:04:20" referer="" remote-host="66.249.73.185" user-agent="Mediapartners-Google" />
  ......
</counter>
```

其中, /counter/@base 是給你作弊用的，這數字你填多少就是多少，然後再加上底下有幾筆 `<hit />` 記錄，總數就出來了。很簡單的格式，而流水帳就是記在 `<hit />` 這個 XML ELEMENT 的 ATTRIBUTES 上。目前記的有時間，IP，REFERRER 而以。等到網站人數暴增 (幻想嘛?)，COMPACT的動作就免不了了，預留的 /counter/@base 就派上用場了。COUNTER 在必要時就能刪掉多餘的 `<hit />` 記錄，再把刪掉的筆數加到 /counter/@base 上，讓最後點擊總數不變，又能控制記錄檔的大小。

邏輯確定後就可以開始動工了，不過另外要解決技術問題，就是 ThreadSafe 的部份。這部份讓我煩惱了一下，因為在 File System 就提供了 FILE LOCK 的機制可以用，不過取得 LOCK 失敗是會引發 EXCEPTION，而不是像其它的 THREAD 控制機制會 WAIT。因此最後我決定 FILE LOCK 的機制做第二層保障 ，主要的 LOCK 機制還是自己來，用基本的 Monitor 來實作。要實做 LOCK 的前題，是要有明確的 LOCK "對像"。兩個 thread lock 同一個物件，後面 lock 的 thread 會被 block 暫停執行，直到前一個先 lock 同一個物件的 thread 釋放之後才會被喚醒，因此要先解決兩個同 ID 的 COUNTER 能拿到同一個物件，才能實作 LOCK 機制。這物件就好幾位合適的候選人，第一種方法是 COUNTER 本身，第二種方法則是替每個 counterID 產生一個無用的物件，就單純拿來 LOCK 用。

要用 (1) 成本太高，一來就必需實作 [Flyweight](http://en.wikipedia.org/wiki/Flyweight_pattern) 這個 design pattern，這個設計模式並不難，只要實作 [factory pattern](http://en.wikipedia.org/wiki/Factory_method_pattern)再搭配個 Dictionary<string, Counter> 物件就可以搞定，但是我最後沒有選擇這個作法。因為最糟的情況下有可能會讓整個系統可能會用到的 counter 通通被放到這個 dictionary ，沒有被釋放回收的機會，因為沒有明確的時間點可以把這物件從 dictionary 移掉，移不掉的話永遠就會留著一個 object reference 指向這 COUNTER 物件，reference 只要存在，它就永遠不會被 GC 收掉...。不過這還是有解，只要用 [WeakReference](http://en.wikipedia.org/wiki/Weak_reference) 就可以解決了，不過我只是要作個簡單的 Counter，搬出這一堆東西會不會太過頭了?

因此我選擇了第二個方法。一樣用 [flyweight pattern](http://en.wikipedia.org/wiki/Flyweight_pattern)，只不過我放的是拿來 lock 的物件。我是直接 new object() 就拿來用了，物件很小我就不用耽心建立太多個又不能回收的問題...，而 counter 就讓它回歸最簡單的用法，需要就 new 一個出來，用完就丟著等著被回收。

每次都是講的話比 CODE 還多，來看看程式碼:

**COUNTER 物件的 SYNC 機制**

```csharp
// 所有 COUNTER 用的 SYNC 物件 DICTIONARY
private static Dictionary<string, object> _counter_syncroot = new Dictionary<string, object>();
// 取得這個 COUNTER 用的 SYNC 物件
private object SyncRoot
{
    get
    {
        return Counter._counter_syncroot[this._counterID];
    }
}
private Counter(string counterID)
{
    this._counterID = counterID;
    //
    //  建立 SYNC 物件 (如果沒有的話)
    //
    lock (Counter._counter_syncroot)
    {
        if (Counter._counter_syncroot.ContainsKey(this._counterID) == false)
        {
            Counter._counter_syncroot.Add(this._counterID, new object());
        }
    }
    //  略 ....
}
public void Hit()
{
    lock (this.SyncRoot)
    {
        //
        //  LOCK 後再開始更新檔案內容。 程式碼 略...
        //
    }
}
```

這問題解決掉後，剩下的就是單純把我要的邏輯實作出來，這部份我相信讀者的程度都不用我多講了，有需要的看 CODE 就看的懂。請直接[下載最後面的程式碼](/wp-content/be-files/PostViewCounter.cs)就好。

另外一個要提一下的是跟 BlogEngine 本身 Extension 相關的，這部份也花了點時間研究該怎麼寫。BlogEngine 的 Extension 寫法比較特別一點，一般這種外掛都是採 Provider 的方式實作 ( factory pattern 加上 abstract class )，先定義好這個 Provider 能作什麼事，然後每個寫 Extension 的人就自己繼承這類別來修改，再靠 Factory 動態的建立正確的 Extension 物件來使用。不過在這部份 BlogEngine 採用完全不同的作法來設計它的架構: Event Handler。

Provider 依賴的是事先定義好的 ProviderBase (abstract class) 類別。這個類別定義了多少東西給底下的人覆寫，就決定了寫外掛的人能處理多少事。好處是簡單，架構清楚。缺點是能讓你擴充的功能，在 DESIGN TIME 就決定了，要多一個能 "擴充" 的地方，就得改 ProviderBase 類別定義，這很有可能會讓現有的 Extension 不能跑...。換成 EVENT 的方式就沒有跟程式碼綁的那麼緊了。多了新的功能，多定義一些事件就夠了。BlogEngine 就是採這種方式來實作它的 Extension ..

另外比較特別的是，BlogEngine 替每個 Extension 規劃好存放設定的地方。 1.3 版是所有的 Extension 共用一個設定檔， 1.4 則是有獨立的設定檔可以用。不過這些改變倒是沒有影響到它提供的 API。對於 API 來說，設定檔提供每個 Extension 一個像是 DataTable 那樣的 data storage, 讓你自訂欄位名，型別，然後能讓你一筆一筆的加進去，可以有多筆資料，而 BlogEngine Runtime 會負責幫你管理好這些設定。

這部份帶入門就好，用法還是去查官方文件比較快。我簡單貼一下這部份 CODE 跟畫面上提供的設定頁面給大家看看:

**準備設定值的 SCHEMA 及載入目前的設定值**

```csharp
public PostViewCounter()
{
    Post.Serving += new EventHandler<ServingEventArgs>(OnPostServing);
    ExtensionSettings settings = new ExtensionSettings("PostViewCounter");
    settings.AddParameter(
        "MaxHitRecordCount", 
        "最多保留筆數:");
    settings.AddParameter(
        "HitRecordTTL", 
        "最長保留天數:");
    settings.AddValues(new string[] { "500", "90" });
    //settings.ShowAdd = false;
    //settings.ShowDelete = false;
    //settings.ShowEdit = true;
    settings.IsScalar = true;
    settings.Help = "設定 counter hit records 保留筆數及時間。只有在筆數限制內且沒有超過保留期限的記錄才會被留下來。";
    
    ExtensionManager.ImportSettings(settings);
    _settings = ExtensionManager.GetSettings("PostViewCounter");
}
```

對應的設定頁面:

![image](/images/2008-07-06-blogengine-extension-postviewcount-1-0/image_3.png)

最後講了半天，真正想自己動手寫的人應該不多吧 :D，只是想下載回去裝來用的人就不用聽我前面廢話一堆了，只要下載這檔案，放到 ~/App_Code/Extension 下，就安裝完成了... 咳咳，連安裝手冊都省了。檔案 COPY 好後就會在 Extension Manager 裡看到我寫的外掛，就可以開始用了。有任何意件歡迎留話給我 :D

檔案下載: [http://columns.chicken-house.net/wp-content/be-files/PostViewCounter.cs](http://columns.chicken-house.net/wp-content/be-files/PostViewCounter.cs)