---
layout: post
title: "Blogging as code !!"
categories:
- "有的沒的"
tags: ["Jekyll", "Liquid", "Wordpress", "Blogging", "GitHub", "VSCode"]
published: true
comments: true
logo: /wp-content/uploads/2016/09/blog-as-code-workflow.png
---

# TL;DR 

想想我開始寫 blog 的這十幾年 (Orz, 這麼久了)，用的部落格系統也換了不少套了, 從最早我自己土炮寫的 asp.net 1.1 blog 開始算, 中間光是系統就換了 5 套, 還不包括
同一套系統的版本升級... 這些 post 都還能留下來也真算是奇蹟了.. 不過再怎麼換, 終究是有套 "系統" 需要去維護，不管是自己管還是代管都一樣，開始想走純樸路線，省點
運算資源，好好照顧一下北極熊...

於是就決定改採最低科技的路線，丟掉所有的 "系統"，直接採用最單純的靜態檔案。至於 Hosting 的方式，就用最宅的 GitHub 附屬的服務: GitHub Pages... 
現在流行什麼都冠上 xxxx as code, 那就來個 blogging as code 吧 XD

<!--more-->

先回顧一下，我到底換過幾套 BLOG 系統 ...

1. **2002** - 土炮 blog (asp.net 1.1 + sql server)  
2. **2004** - .Text  
3. **2005** - Community Server  
4. **2008** - Blog Engine  
5. **2015** - Word Press 
  
  
看來 Blog Engine 是最長壽的一套系統啊，有很大的原因是因為他維護很方便 (不需要 database). 這些系統一路用過來，總覺得少了點什麼... 雖然功能強大，
但是對於 developer 來說其實都有更多好用的工具可以取代，例如 Blog System 提供的版本控制遠遠不如 developer 常用的 github, TFS, subversion 等等
 (用過就知道差別，完全是兩個檔次), 另一個主要 HTML editor 也是，寫文章還是 [markdown](https://guides.github.com/features/mastering-markdown/) 最好用啊，不過就算我換到 wordpress, 對於 markdown 的支援度
 仍然跟 github 比起來差一大截.. 需要的功能沒得用，不需要的功能卻又太多，同時為了維護他也需要花費對等的心力...

所以這次就興起一個念頭，打算全部拋掉這些 "系統" ... 養一個用不到 5% 功能的系統，卻要顧好他的 SLA 也是挺煩人的. 這次我打算反璞歸真，改用完全靜態
的網站來取代，會這樣決定，其實我已經想過這幾個問題了:

1. **沒有權限及會員管理的問題**  
只要你願意看，我的文章都歡迎你 XD, 對於讀者來說不需要會員管理。對於發文者來說也只有我一個人。額外要為了一個帳號，搞一整套會員管理機制實在有點多餘。  

2. **沒有後台管理問題**    
如果我用靜態網站，發布的部分就不需要後台了，只要要給 user 看的內容才需要上傳。撰寫的環境可以接受只在 PC 端。我文章都不算短，根本沒機會在手機上面寫。
在 web 上寫是有機會，通常是改改錯字或是片段的編輯而以。真正幾句話，或是分享資訊，交給 facebook 粉絲專頁就夠了。  

3. **版本控制問題**  
如果都變成靜態檔案，版本控制直接丟 git 啊，版本控制，備份，還原一次解決。你願意的話還可以 branch / merge, or pull request..  

4. **內容編輯問題**
其實我一直覺得 HTML based HTML editor 是個很 OOXX 的東西。一來文章一長，編輯效率很糟糕，二來所謂的 WYSIWIG 也是很雞肋，只要樣式 CSS
換掉後，可能你編排半天的格式都變了樣。文章內容其實不需要太多編排啊，基本的文字、引用CODE、還有標題、斜體、黑體等等就夠了。用 markdown 
對我來說是最好也最有效率的選擇，用 HTML editor, 或是額外的 blogging tools (ex: live writer) 其實都有點多餘..  

5. **讀者互動問題**  
如 comments, 按讚等等, 都有第三方服務可以 plugin 啊, 靜態 html 插一段 HTML code 就能解決  


查了一下，其實有同樣想法的人不少耶，不過跟我一樣用 **"blogging as code"** 的方式來說明這個理念，我只 google 到一篇 
[The Journey to GitHub Pages](http://allthelayers.com/blogging/The-Journey-to-GitHub-Pages/) 
老外講話就是比較簡潔明快，他講的很有道理啊，developer 就是都在跟 text mode 奮鬥, 靠的是 version control 來管理工作成果，所以
會愛用 markdown + github 是理所當然的啊 XD

從更根本的角度來看，關鍵在於你的 web site 是否真的有 "runtime process" 的需要? 如果沒有任何內容或是訊息 100% 需要在當下才能決定的話，那代表
你的 web site 其實是可以事先把所有內容都先產生出來的。我的 blog 有沒有需要? 文章內容，文章清單，分類、標籤、分頁等等都可以是靜態的。回應、按讚、
網站流量統計等等則必須是動態的，但是這些都可以直接嵌入第三方服務 (ex: facebook social plugins, google analystic, disqus...) 就能搞定，所以
對我來說只要產生正確的 html code, 這些功能也算是靜態的。 

越想越覺得可行，既然現在很流行 **xxx as code**, 那這種用法就給他個名稱, 就叫他 **"blogging as code"** 吧! 背後的涵義也剛好代表, 這是逐步轉為
以 developer 為中心的思考方式。要就徹底一點，現在都講求 open source, 既然 blogging 都要 as code 了，把整個 blog 都 open source, 也是個改變。
通通都放上 github, 如果有人願意取用我的文章，不違反我的授權原則我通通都歡迎!


# Solution: GitHub Pages Service + Visual Studio Code

GitHub Pages 是 GitHub 在 Repository 上面提供的附加服務，原本目的只是讓 open source project 能有個簡單的 project site 可以使用。
這些 site 用途跟 blog 很類似，就是發佈一些消息跟文章。背後的架構是 github repository 要指定某個 branch 的內容就是要給大家看的內容。
當這個 branch 內容有所異動的時候，就會觸發靜態網站產生器 (github 用的是 jekyll) 更新網站內容。

上面這些其實都是全自動的，我要做什麼? 除了第一次把網站的 template 跟 config 弄好, push 上去 github 之外，剩下的就是用 markdown 寫好
文章 push 上去正確的 branch, 就完成了。

很簡單吧? 真的很簡單，其實我已經參考了很多別人的經驗談，這些參考資料我就列在這邊了:

* [Is Jekyll Better Than Joomla! and WordPress?](http://digitalshore.io/jekyll-better-choice-than-joomla-wordpress/)
* [Which is a better platform for a blog, WordPress or Jekyll+GitHub?](https://www.quora.com/Which-is-a-better-platform-for-a-blog-WordPress-or-Jekyll+GitHub)
* [Blogging: WordPress or Jekyll](https://www.sitepoint.com/blogging-wordpress-or-jekyll/)
* [WordPress vs. Jekyll: Why You Might Want to Switch](https://www.sitepoint.com/wordpress-vs-jekyll-might-want-make-switch/)
* [5 reasons you should use Jekyll](http://cloudcannon.com/jekyll/2015/03/04/5-reasons-you-should-use-jekyll.html)



當然，也有人用過後，又回頭去用 wordpress 的例子:

* [Why I switched from Jekyll back to WordPress](http://vitobotta.com/switched-jekyll-back-wordpress/)



主要的服務決定用 GitHub Pages 之後, 我自己 local 好歹也要有個像樣的 tools. 
雖然下 git 指令對我沒什麼障礙, 但是有時還是想偷懶一點... 想找個好用的 local tools 方便管理網站的 template 跟 data.. 需求不多，只要這幾個:  

1. **能管理整個 git local repository**  
可以隨時 commit, push, pull ... 等等 git 基本操作  

2. **要能編寫 .md, .html, yml 等常見的格式**:  
我需要直接編寫 source code, 最好能有 syntax highlight, 能有 intelligent sense 更好, 能有 live preview 更好  

3. **小巧，簡單，快速**:  
我不想要安裝一大包工具...  


這不就是 [visual studio code](http://code.visualstudio.com/) 嗎? 看來太完美了，都是 for developer 用的黃金組合... github + vscode
用過的就知道了，不用我多介紹啦~ 貼張 vscode 寫 markdown 的圖意思一下就好:  

[![用 visual studio code 編輯 markdown, 同步預覽](/wp-content/uploads/2016/09/blog-as-code-vscode.PNG)](/wp-content/uploads/2016/09/blog-as-code-vscode.PNG)  





## Workflow: How to create a new post ?

既然要認真轉移系統，那麼平常寫作的方式，還有搭配的環境跟設施，就要好好的來規劃一下。我還是習慣在 windows 下工作，不過這些
solution 並非 windows 的原住民, 總是有些小地方要處理.. 這邊紀錄一下我的作法:

[![blogging as code workflow](/wp-content/uploads/2016/09/blog-as-code-workflow.png)](/wp-content/uploads/2016/09/blog-as-code-workflow.png)

流程很簡單，就是按照圖上的標示，由 1, 2, 3, 4, 2, 3, 4, 2, 3, 4 ...., 5 的順序不斷重複而以。這邊 GitHub Pages 跟 VS Code
都不會有什麼大問題，裝了就是了。問題最大在 local 要架設 jekyll 的話會是個大工程 (尤其是在 windows 下) ... 我試過這三種作法，
給大家參考看看

1. **install jekyll on linux**  
這是最佳的解決方案，效能, 相容性, 支援程度都是最好的, 連 vscode 也有 for linux 的版本。不過... 我主要工作環境是 windows ... 暫時不考慮 XDD

2. **install jekyll on windows**  
這是 for windows 效能最佳的方案, 不過相容性也是最糟糕... 對 ruby 沒經驗的人 (就是我 T_T) 會很痛苦

3. **using jekyll on docker (using [docker for windows](/2016/06/11/docker-for-window-beta-evaluate/))**  
這是 for windows 最讚的解決方案了，犧牲一些效能, 換來幾行指令就可搞定一切的方案。


## Running Jekyll on docker-for-windows

這個很無腦，裝好 docker for windows 後就幾乎完成了。在 dos command prompt 下輸入這段指令:

```
docker run -ti --rm -p 4000:4000 -v D:\Blog:/srv/jekyll jekyll/jekyll:pages jekyll s --watch --force_polling
```

要留意的是，```D:\Blog``` 是你自己 local 的 git repository 路徑，需要把他掛上 docker, 掛在 ```/srv/jekyll``` 下面。
```--watch``` 這參數是告訴 jekyll 要不斷監控 ```D:\Blog``` 這目錄是否有異動? 若有檔案變更會立即更新產生出來的網站。

不過，docker volume 有個老問題, 底層的 file system change notification, 經過 docker volume 的包裝, 這些 notification
沒辦法正確的傳遞到 container 內，[這邊有類似的例子](https://github.com/boot2docker/boot2docker/issues/652)。這個問題
並不大，jekyll 提供額外的參數: ```--force_polling``` 改用 polling 的方式，不斷檢查每個檔案有沒有異動，可以解決這問題。

不過，polling 是要付出代價的，I/O 跟 CPU 效能影響還蠻大的，回應速度也比 notification 慢，尤其你的檔案數量不少時更明顯。只是
至少是個解決方案。以我的例子，更新了檔案至少要 15 sec 後才會有反應 (正常情況下，不到 1 sec 就偵測到了)。Polling 的效能應該會跟你的
檔案數量大小有直接關聯吧，我的 blog 文章約 400 篇, CPU: i7-2600k, 24GB RAM, Intel 730 SSD 240GB + Seagate 5TB 7200RPM Enterprise HDD.. 這樣的配備
跟執行效能，可以給各位參考一下

貼張圖就結束這回合了 XD, 以我的 case, build 一次 website 約需要 70 sec, 效能受限於我分配給 docker 的資源 (2 cpu, 2048 mb ram).
偵測到異動後的 rebuild 則要花上近 20 min...
[![jekyll on docker-for-windows, screenshot](/wp-content/uploads/2016/09/blog-as-code-dfw-screenshot.png)](/wp-content/uploads/2016/09/blog-as-code-dfw-screenshot.png)

執行時間的 CPU usage 果然也慘不忍睹..
[![jekyll on docker-for-windows, docker stats](/wp-content/uploads/2016/09/blog-as-code-dfw-stats.png)](/wp-content/uploads/2016/09/blog-as-code-dfw-stats.png)

如果你想省事，打算採用 docker for windows 來執行 jekyll 的話，給你一個良心的建議... 別用 ```--watch``` 模式了，有異動的話手動 restart container
會比較簡單，或是你有辦法的話，用 powershell 寫段簡單的 script, 在檔案有異動時 restart container ..

## Running Jekyll on windows

有鑑於效能差異實在不小 (jekyll for windows, build 一次要 30 sec, 快了一倍), 實際在改文章時半分鐘的延遲還可接受，而且 file system
notification 的機制也能正常運作, rebuild 時間跟正常 build 的也一樣大約半分鐘，所以正常情況下我還是用 for windows 版本的 jekyll,
儘管有很多障礙需要克服...

* [Windows下用jekyll写博客所需要的环境](http://www.badnotes.com/2014/04/13/win_install_ruby/)

不過實際使用上的障礙還真的不少，雖然都是小問題。我踩過這幾個地雷，真的要實作的讀者們請小心:  

1. **ruby runtime version**:  
jekyll 需要安裝 ruby, 不過要用到的套件有些指定不相容最新的 2.3 版 ruby, 搞了半天搞不定，最後我裝 2.2 ..  

2. **webserver**:  
jekyll 本身自帶 web server, 在 windows 下不支援中文檔名, 所以我最後用 jekyll s, 開 --watch 持續監控檔案異動, 負責 port: 4000, 然後另外開 iisexpress 負責 port: 4001, 我自己視需要決定要連哪個 site..  

3. **IIS vs GitHub Pages 檔名大小寫差異問題**:
不同系統存在著根本的差異，這種小問題找了半天才找出來 @@, 檔名大小寫是有差別的，比如我 MD 插入圖檔 URL 寫 a.png, 實際檔名 a.PNG,
在 IIS 上面看都一切正常, 放上 GitHub Pages 後就會掉圖 T_T，氣的是如果已經 push, 我在 local 改掉檔名大小寫, vscode 認不出來要跟
git push 這項異動...  

4. **IIS .aspx http module problem**:  
由於我的文章的舊網址包含 .aspx 這樣的路徑, 我設定 jekyll 可以幫我產生 xxx.aspx/index.html 這樣的靜態網站, 若有 user 點了
舊的網址格式，web server 只要把 .aspx 當成目錄，自動引導到該目錄下的 index.html 就可以相容了。可是 iisexpress 看到 .aspx 就會
交給 asp.net hosting module 去執行，這種靜態網頁在 iisexpress 會跑出404。我不大想解決這種衍生問題，所以這種時候就再切回 jekyll ..  


基本上最麻煩的就是安裝了 (我足足搞了幾個晚上)，剩下的其實改變一下習慣就好。只要我要開始寫文章，我現在的標準動作就是這幾個:
1. **開啟 visual studio code**:  
```
code d:\blog
```
2. **啟動 jekyll serve**, 並持續監控檔案異動:  
```
jekyll s --draft -w
```
3. **啟動 iisexpress**:  
```
"c:\Program Files\IIS Express\iisexpress.exe" /port:4001 /path:d:\blog\_site
```

沒啥畫面，就是這兩個程式執行的 console 訊息而以:
[![jekyll on windows screenshot](/wp-content/uploads/2016/09/blog-as-code-win-screenshot.png)](/wp-content/uploads/2016/09/blog-as-code-win-screenshot.png)

畫面上可以看到，Jekyll for Windows 的效能明顯好很多 (其實 docker 版也不差，只是敗在 polling, 還有平常使用的模式，我不想開太多 CPU / RAM 的資源給 docker for window), 初次 build 大約在 40 sec 上下
異動後的 rebuild 也在 30 sec 上下就能完成。這邊我啟用了 ```--drafts``` 參數，因此 jekyll 會替我把未發布的 drafts post 也產生出來。
這種模式方便我自己測試，不用擔心還沒寫好的 POST 不小心就發佈出去..
[![Jekyll Preview](/wp-content/uploads/2016/09/blog-as-code-local-preview.png)](/wp-content/uploads/2016/09/blog-as-code-local-preview.png)


## Wordpress to GitHub Pages Migration

最後就是來聊聊我怎麼把 wordpress 的資料轉移到 github pages? 其實網路上很多同好分享過，我實在也沒力氣慢慢寫 XD
先貼一下我參考過的作法:

* [Jekyll 官方提供的 Jekyll-Import 模組及說明](https://import.jekyllrb.com/docs/home/)
* [Import your old & busted site or blog for use with Jekyll. - Offical Site](http://import.jekyllrb.com/)
* [Wordpress Plugin - Jekyll Exporter](https://wordpress.org/plugins/jekyll-exporter/)
* [How to migrate programming blog from Wordpress to Jekyll](http://www.codingpedia.org/ama/how-to-migrate-programming-blog-from-wordpress-to-jekyll/)
* [將Wordpress轉移到Jekyll及Disqus - 大貓共和國](http://blog.miaout17.net/2011/05/08/convert-wordpress-to-jekyll-and-disqus/)

其實這幾篇看下來，大概都有共同點，就是:
1. 官方提供的對於中文網址支援不良，會編碼成一堆 %00%00%00 這種 url escape 過的 unicode characters. 網址我可以無視，可是實際匯出放在 /_post 的檔名也長這樣
2. 有的只支援 category, 有的只支援 tags ...
3. 大都不支援 comments, 要另外自己處理
4. comments 一致推薦 disqus 的服務，反而我原本用的 facebook comments 沒人推薦

接下來我列一下我解決過的幾個問題，讓大家知道一下有啥地雷要注意，如果你真的碰過這些問題，在這邊留話吧，我再補上來 :D

* 解決 URL 及檔名的中文問題
* 解決 comment 與 url 對應的問題
> *Hint*: wordpress 匯出的 xml 中文網址就是 %00%00, 如果只解決上面那項中文網址問題，結果會變成留言都看不到了。
> 因此 wordpress 匯出的 XML 本身就需要先處理中文網址問題了。可參考我寫的 C# 匯入工具
* 解決分類及標籤問題
> *Hint*: 挑對 themes ，找個支援 categories / tags cloud 的 template 就夠了，剩下就是匯出時標上正確的分類跟標籤
* 解決舊網站的轉址問題
> *Hint*: 不只 wordpress, 還有更早 blogengine, community server 的連結.. 可參考我[這篇文章](/2015/12/03/casestudy-nginx-as-reverseproxy/)要解決的問題, 很多外來的連結都是這種
> 解決方式，加裝 [jekyll-redirect-from](https://help.github.com/articles/redirects-on-github-pages/) 模組，然後在匯出的 post 內標示這篇文章可能從哪幾個 URL 轉址過來。同樣的可以參考我的 C# 匯入工具
> 舉個例子，只要是舊文章，我都會匯出像這樣的 post header (請注意 **redirect_from** 的部分)  
>各位可以直接試試看，這些舊網址，是不是真的會動 :D  
>  * link: [/columns/post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx](/columns/post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx)
>  * link: [/post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx](/post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx)
>  * link: [/post/e7b582e696bce58d87e9809fe4ba86!.aspx](/post/e7b582e696bce58d87e9809fe4ba86!.aspx)
>  * link: [/columns/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx](/columns/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx)
>  * link: [/columns/e7b582e696bce58d87e9809fe4ba86!.aspx](/columns/e7b582e696bce58d87e9809fe4ba86!.aspx)
>  * link: [/?p=59](/?p=59) => 這比較特別，static web site 沒辦法處理 ? 後面的 query string, 這有搭配一點點前端 javascript 配合處理
>
> ```
> ---
> layout: post
> title: "終於升速了!"
> categories:
> - "敗家"
> - "有的沒的"
> tags: ["敗家","有的沒的"]
> published: true
> comments: true
> permalink: "/2008/10/10/終於升速了/"
> redirect_from:
>   - /columns/post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx/
>   - /post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx/
>   - /post/e7b582e696bce58d87e9809fe4ba86!.aspx/
>   - /columns/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx/
>   - /columns/e7b582e696bce58d87e9809fe4ba86!.aspx/
> wordpress_postid: 59
> ---
> ```


* 補上 google analystics
* 補上 google adsense
* 補上 facebook open graph meta tags
* 補上 facebook like / share button  

> 上面這四項，通通都是把 google / facebook 提供的 HTML 貼到正確位置而已，頂多有些關鍵的地方要用 Liquid 的語法填進去。
> Liquid 做這種事情實在太適合了，他就是個 template engine 啊，語法熟悉後真是輕而易舉.. 比用 wordpress plugins 還容易


有些好心人，用 ruby 寫了自己的匯出工具，解決 tags / category / 中文檔名問題，不過 ruby 我不會寫啊，加上要處理的問題也不難，
所以我自己也貢獻了一個 C# 版的 :D 有需要請自行取用。

Clone Code Here: [ImportWordpressToJekyll](https://github.com/andrew0928/ImportWordpressToJekyll)


# Conclusion

過程中還有很多沒沒角角我沒寫的，包含怎麼轉資料，怎麼匯入 comments，還有如何用 Liquid template engine 的語法打造自己的 template 等等。
這邊純做個架構介紹，告訴大家這樣用的優缺點。我用的環境算是比較怪的，一般會用 jekyll 這類 solution 的都是熟 linux / open source 的人，
這些應該都不成問題，我這種算是特例 XD

不過整體而言，我覺得這方案算是一大進步，完全顛覆了過去的做法。光是用 github 做版本控制，我認為就值回票價了。因為他能控制的，不再是 **單一一篇文章**
的版本而已，他能一次控制多篇文章內容及屬性(是否發布等等)，還有你網站的設定，一次 push 上去。另外網站改版時，也能讓你用另一個 branch 測到
好之後，再 merge 回來上線。說穿了就跟你寫 code 控制一堆 source code 一模一樣，只是你的 language 是 HTML + MD, 你的編譯器變成 jekyll ..
如此而已

最後來點平衡報導吧! 全部放到 github 也不全然是好處。其中一個風險就是，別人要把你的網站拿走就更容易了，只要下個 git clone 就好了 XDDD
這點我是想通了，我寫 BLOG 的目的本來就是分享，有人要 clone 去拿走我的文章，我會覺得你是在幫我宣傳，只要你按照我要求的 CC 授權，標記
出處就好。過去碰過太多盜文的事件，只要是公開的東西，我相信就算不是放在 github 上，也一樣會很容易的被複製.. XD

我的架站經過 & 心得就整理到這裡，趁著中秋假期，在這特別的日子就讓新網站上線吧! 請各位繼續支持 :D