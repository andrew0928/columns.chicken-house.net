---
layout: post
title: "Case Study: BlogEngine -> WordPress 大量(舊)網址轉址問題處理"
categories:

tags: ["技術隨筆","有的沒的"]
published: true
comments: true
permalink: "/2015/11/06/apache-rewritemap-urlmapping-case-study/"
redirect_from:
wordpress_postid: 507
---

# 前情提要:

起因很簡單，[上個月](/2015/10/13/docker-%e5%88%9d%e9%ab%94%e9%a9%97-synology-dsm-%e4%b8%8a%e9%9d%a2%e6%9e%b6%e8%a8%ad-wordpress-redmine-reverse-proxy/)才把我的 BLOG 從 BlogEngine 轉移到 WordPress... 這種轉換系統一定會碰到的問題，就是新舊系統的 URL 格式一定不一樣的，不過好不容易累積起一些文章連結 (別人連到我的文章) 不處理的話，這些連結就失效了。算算文章數量，約 400 篇.. 統計一下每篇文章可能連到的格式，有 6 種，若不放掉每個連結，則有 400 x 6 = 2400 個連結要轉換..

究竟，在 Apache 做這麼多網址轉換的動作，怎樣才是最理想的方法? 這就是這篇文章想探討的... 讓我們繼續看下去 :D

# 到底有多少舊網址要轉換?

人家說做事要講究事實，開始動工前，先來了解一下到底有哪些情況需要轉址? 我之前用的 Blog 系統是 ASP.NET 寫的 BlogEngine 1.6, 算是老字號的 .NET 部落格了，先從我知道的開始:

## **預設的格式:**

最基本的格式，按照日期 (年/月/日) 後面加上編碼過的文章標題。用我最常被引用的[這篇](/2008/09/27/%e8%a9%b2%e5%a6%82%e4%bd%95%e5%ad%b8%e5%a5%bd-%e5%af%ab%e7%a8%8b%e5%bc%8f/)當例子，像這樣:

http://columns.chicken-house.net/post/2008/07/10/GoodProgrammer1.aspx  (這是第一類)

不過，不知哪個版本開始，多了 multi-tenancy 的概念，所以系統允許多個部落格同時存在，有些網址就多了這層路徑:

http://columns.chicken-house.net/columns/post/2008/07/10/GoodProgrammer1.aspx  (這是第二類)

## **從 Google Search Console:**

本以為這樣就結束了，順手開啟 Google Search Console 看看新上線的 WordPress 被檢索的狀態... Ouch! 狀況還真不少...

![](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/img_563ca54e8f511.png)

Google WebMaster Tools 還真的是好工具，幫我挖出了很多想都沒想到的連結。這是列出來 Google 認為應該存在的網址，卻檢索不到的清單及統計。從統計圖看的到，10/10 換完系統之後檢索錯誤的狀況就暴增，很明顯地這些都是轉換系統後產生的問題... Google 提供下載 .CSV 清單，要確認就方便多了..

用肉眼逐條歸納，發現了好幾種我連想都沒想過的連結格式 @@，包括這種不包含日期的格式:

http://columns.chicken-house.net/post/GoodProgrammer1.aspx  (這是第三類)

http://columns.chicken-house.net/columns/post/GoodProgrammer1.aspx  (這是第四類)

再挖下去，竟然還有... @@，這是直接用 post id (GUID) 當參數的格式:

http://columns.chicken-house.net/post.aspx?id=52e998ee-ee02-4a66-bb27-af3f4b16c22e (這是第五類)

http://columns.chicken-house.net/columns/post.aspx?id=52e998ee-ee02-4a66-bb27-af3f4b16c22e (這是第六類)

更扯的是，最基本含日期格式的 (第一類)，竟然還找的到日期錯誤的 @@，這我就真的不知道怎麼來的了... Orz 這種無法預測的先當例外處理，晚點再說... 我算了一下，我總共有近 400 篇文章，如果不放過任何一類連結格式的話，共有這六種 URL format 得搞定:

```
http://columns.chicken-house.net/post/GoodProgrammer1.aspx
http://columns.chicken-house.net/columns/post/GoodProgrammer1.aspx
http://columns.chicken-house.net/post/2008/07/10/GoodProgrammer1.aspx
http://columns.chicken-house.net/columns/post/2008/07/10/GoodProgrammer1.aspx
http://columns.chicken-house.net/post.aspx?id=52e998ee-ee02-4a66-bb27-af3f4b16c22e
http://columns.chicken-house.net/columns/post.aspx?id=52e998ee-ee02-4a66-bb27-af3f4b16c22e
```

# 開始動手，設定 Apache 啟用 Redirect 轉址

在[之前的文章](/2015/10/13/docker-%e5%88%9d%e9%ab%94%e9%a9%97-synology-dsm-%e4%b8%8a%e9%9d%a2%e6%9e%b6%e8%a8%ad-wordpress-redmine-reverse-proxy/)就已經提到，我的架構是在 NAS 用 Docker 架設 WordPress, 前端用 NAS 內建的 Apache 擔任 Reverse Proxy 來負責前端。既然都有前端擋著了，轉址這件事也理所當然地讓 Apache 負責。由於實在對 Apache 不熟 @@，我就找了最簡單的方法，其他就... 勤能補拙，靠寫 code 產生正確的設定擋來搞定他，於是第一版就上線了!

[![NETWORK](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/NETWORK.png)](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/NETWORK.png)
圖: NAS 架設 WordPress + Reverse Proxy 架購說明

找到 apache 最簡單的轉址方式，就是寫 Redirect 指令，Apache 會用 http status code 301 來轉，於是.. 如果要搞定全部的6種格式，得寫 2400 條 rules... 這種時候就很慶幸我自己會寫 code，搬出 Visual Studio 2012, 自動替這 400 篇文章產生這樣的 redirect 指令:

```apache
    Redirect 301 /post/2008/07/10/GoodProgrammer1.aspx /?p=65
    Redirect 301 /columns/post/2008/07/10/GoodProgrammer1.aspx /?p=65
    Redirect 301 /post/GoodProgrammer1.aspx /?p=65
    Redirect 301 /columns/post/GoodProgrammer1.aspx /?p=65
    Redirect 301 /post.aspx?id=52e998ee-ee02-4a66-bb27-af3f4b16c22e /?p=65
    Redirect 301 /columns/post.aspx?id=52e998ee-ee02-4a66-bb27-af3f4b16c22e /?p=65

    # 以下略過
```

這方法 "暫時" 解決我的燃眉之急了，的確可以把大部分的文章轉到正確的內容，不過連我自己都看不下去了，這樣做的缺點還真不少:

1. **不好維護**: 沒錯，這根本沒辦法手動調整了，要異動就得重跑一次 config generator 後再貼上... 不過，舊文章也不會變多，再怎麼樣就是那400篇，除了麻煩一點也還好
2. **無法處理例外狀況**: (對，就是上面提到竟然有日期錯誤的文章連結) .. 只要錯一個字就連不到了，但是若 BlogEngine 還在線上的話，是看的到文章內容的...
3. **效能問題**: [我一向最講究演算法跟時間複雜度了](/2008/10/01/%e8%a9%b2%e5%a6%82%e4%bd%95%e5%ad%b8%e5%a5%bd-%e5%af%ab%e7%a8%8b%e5%bc%8f-2-%e7%82%ba%e4%bb%80%e9%ba%bc-programmer-%e8%a9%b2%e5%ad%b8%e8%b3%87%e6%96%99%e7%b5%90%e6%a7%8b/) XD，這 2400 條 rules, 我試著猜想看看 apache 會怎麼執行?  一定是每個 request 進來，就逐條判斷... 若第一條就 match 那還算簡單，要是每條都不 match 不就做了 2400 次白工? 何況沒 match 的一定是大多數..

有了這些想法，才有這篇文章的後續... 因此開始想其他解決辦法了 XD

# 改用 RewriteMap，用 RegExp 來判定格式, 解決例外狀況

Apache 有進階一點的轉址語法，是 [RewriteRule](https://httpd.apache.org/docs/2.4/rewrite/flags.html) .. 跟上一段 Redirect 不同的是，他可以靠 RegExp 來 Match, 之後可以替換出正確的網址... 比 Redirect 有彈性的多，於是上述 1 ~ 4 類格式，我可以用一條 regular expression 來 match:

^/?(columns\/)?(post\/)?(.+\/)?(.+\/)?(.+\/)(.*)\.aspx

看不懂嗎? 對，我也看不懂... Regular Expression 號稱 [Write Only](https://en.wikipedia.org/wiki/Write-only_language) 的語言實在不為過.. 這條正規運算式，可以檢測出上述第一 ~ 第四類的格式，還可以把編碼的標題 (slug) 給抓出來... 因此我只要寫這條 rules ，就可以取代上個例子的四條 redirect 指令:

RedirectMatch 301 ^/?(columns\/)?(post\/)?(.+\/)?(.+\/)?(.+\/)GoodProgramer1\.aspx /?p=65

不過，這樣改下來一樣有 400 條啊，三個問題裡，第一個維護問題沒解決，第二個例外處理有解決，第三個效能問題... 雖沒實測，但是我直覺告訴我，應該不會好到那裡去吧?

# 大量使用轉址指令的效能問題探討

於是我就開始 google 大量轉址的效能問題.. 效能應該都花在大量比對 rules 上，屬於 CPU 密集的運算，這種吃 CPU 效能的運算，我在 NAS 上貧弱的 CPU 跑起來，執行時的影響更大啊... 不解決不行，查了幾篇有關這種大量 redirect 的效能問題，[這篇](https://wiki.mozilla.org/Mozilla.com/2011-Rebranding-Project/Benchmarks)是我覺得最有說服力的一篇，直接貼一張圖來看就知道差別:

![Graph2.png](https://wiki.mozilla.org/images/3/33/Graph2.png)

先解釋一下這張圖怎麼看。測試案例裡面，用了 benchmark 不斷的去點擊大量的網頁。被測試的 apache 設定了 1500 條轉址，而不同顏色的線則是用了不同的方法來寫這些 rules.

圖表的 Y 軸代表點擊網頁的回應時間 (越短越好)，X 軸則代表有多少比例的點擊數回應時間最大值落在哪裡..  簡單的講，曲線越低的做法越好啦!

我用的第一招，就是 Apache Redirect, 慘不忍睹... RewriteRule 基本上也屬於同一層級的，也沒好到哪裡.. 看到還有另一招 RewriteMap ! 效能出奇的好，大約只花了 1/10 的回應時間... 這是甚麼? :D

# 改用 RewriteMap 來實作 Apache 轉址機制

終於看到一道曙光了! 研究了一下，果然這才是適合我用的好物! 先看看官方文件: [Using RewriteMap](https://httpd.apache.org/docs/2.4/rewrite/rewritemap.html) !

RewriteMap 就像是 C# 裡的 Dictionary<string, string> 一樣，提供你一個快速有效的 Hash Table 去查表。Hash Table 的時間複雜度是 O(1), 不受你的資料筆數影響，是很理想的做法。單純的 regular expression 就是沒辦法做這點，我才需要寫 400 條 rules 啊! 找到這做法之後，改寫果然簡單多了，改寫後變這樣:

```
  RewriteEngine ON
  
  RewriteMap slugmap "txt:/volume/slugmap.txt"
  RewriteRule "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*).aspx" "?p=${slugmap:$5}" [R=301,L]
```

真正的 match 比對，一行就搞定了。當然，要搭配他提供另一個文字檔當作對照表，像這樣把全部 400 篇的 slug-id v.s. wp post id 對照表列出來:

```
# blogengine post slug ==> wp post id
RUNPC-2008-11 52
VCR-e5b08fe79aaee887aae5b7b1e8b2b7e5a49ae5a49a 225
e6b0b4e99bbbe5b7a5e697a5e8aa8c-5-e9858de68ea5-cable-e7b79a 142
e58d87e7b49ae5a4b1e69597-Orz 201
e6adb8e6aa94e5b7a5e585b7e69bb4e696b0-CR2-Supported 197
e6adb8e6aa94e5b7a5e585b7e69bb4e696b0---CR2-Supported 197
Community-Server 281
x86-x64-e582bbe582bbe58886e4b88de6b885e6a59a 85
e58e9fe4be86-XmlWellFormedWriter-e4b99fe69c89-Bug- 48
e5808be4babae6aa94e6a188-2b-e78988e69cace68ea7e588b6 40
video-e5b08fe79aaee887aae5b7b1e59083e69db1e8a5bf-II 244
```

改用這個做法，原本的效能問題，就分兩個部份解決掉了。一來需不需要進行轉址，只需要進行一次 regular expression 計算就能知道。每一個 http reques 不會浪費太多時間去重複 400 次的運算。如果 match 成功需要轉址，用 hash table 查表也很快，完全不會受到 400 筆的影響..

繼續查下去，文字檔的效能還是稍差，所幸 apache 有提供工具，可以把它編譯為二進為 dbm 檔案，效能更好.. 細節我就不多說了，官方文件都有寫..

# 成效評估

![](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/img_563cb0e81195b.png)

其實效能到底有沒有改善很多，我是不曉得啦，但是光是衝著好維護這點就值得做了。我一樣從 google webmaster tools 抓了檢索的回應時間統計來看，我標上三個時間點，由左到右，依序是:

**10/11:** 將部落格從 GoDaddy Web Hosting (BlogEngine) 搬回家，用 HiNet 光世代 (PPPoE 取得的固定IP)，架在 Synology DS-412+ 上面架設的 WordPress. 這時間點之後很明顯地看到效能掉下來了，回應時間暴增，可能跟網路 & NAS 的效能較差有關。

**10/28:** 由於一直覺得搬回來之後 BLOG 跑很慢，於是下載了 [W3 Total Cache](https://www.w3-edge.com/products/w3-total-cache) 這個 WordPress 的 Cache 套件來用。啟用 Cache 之後效能就快速提升了

**11/01**: 進一步啟用這篇文章說明的 RewriteRules 改善及最佳化工程，回應時間繼續下降，到目前為止，已經降到跟 10/11 之前一樣的水準 :D

從結果來看，很明顯地搬回來後被 NAS 的效能給拖下來了，回應時間從原本的 1 秒左右飆到 4 秒.. Cache 啟用後看來大幅改善 NAS 效能問題，而改善 Apache Rules 寫法理論上又更進一步的改善效能.. 也讓 rules 好維護的多。更重要的是回應時間回復到之前放 GoDaddy 代管的水準... 其實能做到這樣，BLOG 搬回家其實也不錯啊... :D

這次改善計畫，唯一的缺憾就是，觀察的不夠久就開始改用 RewriteMap ，還沒有足夠的數據來看看改用 RewriteMap 實際上到底有多少改善... 我也無從判斷起11/01厚的效能改善，是 cache 還是 rewritemap... 不過這樣其實也夠了，光是能用更少的 rules, *理論上* 更好的效能，可以達到更好的舊網址相容性，降低檢索錯誤的數量，其實我也該滿足了 XD

看來這次的研究沒有白費，寫篇文章紀念一下，下個禮拜再來看看改善的狀況 :D

# 成效評估 (2015/11/09 更新):

補上 2015/11/09 從 google search console 看到的狀態，在轉移系統前 (2015/10/10 前)，Not Found 的網址穩定的維持在 25 筆，轉移後一直沒有好好的處理這個問題，直到處理完之後 (11/5) 才寫了這篇文章，將 google 回報的一千多筆 404 Not Found 網址全標記為 "已解決" 之後讓 google 重新檢索，目前只回報了仍然有 6 個網址檢索後仍是 404 ... 不過看了看網址內容，加上看了來源是哪裡來的，就決定不理她了 XD

![](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/img_563f897aa394e.png)

另外，再看看透過 google 檢索我的網站的回應時間。看來經過調整改善後，回應時間的水準也穩定下來，這水準已經跟當初 Hosting 在 GoDaddy 那邊的水準不相上下了，老實說我本來預期會慢上一截的，現在有這種表現，其實還不錯啦，可以接受 :D

![](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/img_563f8aa579587.png)

# 成效評估 (2015/11/13 更新):

Google Search Console 總算提供到 11/11 的統計資料了，離 RewriteMap 機制上線的時間 (11/06) 已經五天過去了，可以來檢視成果了 :D

![](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/img_5644cdd2c7b64.png)

一樣，先來看看 404 not found 的數量。跟 11/09 的統計差不多，略增加了幾筆，不過增加的就真的是應該回應 404 的錯誤連結了，看來這部分沒有問題，可以收工了。

![](/images/2015-11-06-apache-rewritemap-urlmapping-case-study/img_5644ce9385107.png)

接下來來看看回應時間的改善。由於之前才剛啟用過 WP cache plugins, 因此大部分的效能改善是來自 cache 的關係。多了五天的 LOG，其實是可以多看出一些端倪的。上圖我標了兩個紅點，由左至右，第一個是 11/6，就是改用 RewriteMap 機制的時間點。在那之前可以看到因為 cache 帶來的效能改善已經穩定下來了，開始持平。 11/6 ~ 11/11 還有些微的改善 (平均回應時間從 1130ms 下降到 907ms)，這部分除了 RewriteMap 之外就沒有任何其他異動了。看來 2400 條 rules 改寫之後，在 NAS 這種運算能力不高的系統上，改善還算明顯，約有 15% ~ 20% 的改善，算是超出預期的收穫了
