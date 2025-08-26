Web Application 越做越大, 就會多了一堆不是網頁型態就能解決的功能需求... 舉例來說, 一般網頁就是你點了某個功能, server就會想盡辦法把結果輸出成網頁給你看. 但是這幾種型態的功能就非常不適合用這種模式來開發...

1. 會輸出大量資料的功能 (像報表之類的, 或是列出一堆資料, 又不想分頁)
2. 會長時間執行的 (像資料轉檔, 一跑就要半小時)
3. 需要定期執行, 一直躲在後面偷偷的執行的程式

web application越作越完整的時後, 難免會碰到這種需求. 這些需求其實是有很多方式解決的, 例如用 message queue, 用 reporting service, 另外寫 windows service, 或是另外寫 window form / console application 搭配排程使用等等. 這些作法都會造成開發及安裝的不便... 隨便舉就是好幾個缺點:

1. configuration 無法共用. 除非你另外花力氣去做 application configuration management, 否則, web 的 web.config 跟 app 的 app.exe.config 設定檔的方式就不一樣了
2. library 也要另外設計. web 環境下用的 lib 可以直接以 source code 型態存在於 app_code 目錄下, 同時 web 用的 lib 也有 HttpContext 執行環境的支援, 這些東西都是離開 web 環境下就用不到的
3. asp.net 強調的就是 xcopy 就能完成 deployment, 如果再用到這些額外的開發方式, 很好... 你的程式安裝仍然是個惡夢, 要裝 MSMQ, 要註冊成 windows service, 要排定排程... etc...

看來看去, 如果可以在 asp.net web app 裡把這些問題搞定, 就簡單多了. 找到的 solution 就是用些技巧, 偷偷建立一個 thread 在 web server 裡躲著, 利用這個 thread 來執行這些動作, 讓它用起來好像是 windows service 一樣. 挖了 community server 的 source code 來研究, 發現它的作法是這樣, 在 application_start 時把 background worker thread 建起來, 之後這個 thread 就進入無窮迴圈, 直到 application shutdown ..

自己試了一下, 優喜參半... 解決了一些問題, 不過也有些新的問題... 整理如下:

1. 整個機制一定要 web app 有人連線進來後才會啟用. 假如 server power on 後一段時間都沒有人開網頁, 那麼所有的動作在這段時間內都不會執行. 而 windows service 就不會有這問題.
2. 類似 (1) 的狀況, 如果 IIS 因為各種原因判定要 unload application, 則結果一樣背景作業就會被中斷. worker thread 的生命周期控制沒辦法像 windows service 那樣精確.
3. 效能影響, asp.net 會嚴格監控所用的 thread 數量, 拿一條 thread 做別的事對效能影響不小. 除非你特別去調整 thread 數量上限, 否則至少就少了一條 thread 來處理 http request, 一般預設記得是 20 or 25
4. 因為 thread 執行的環境, 也不是搭配某個 http request, 因此一樣拿不到大部份的 asp.net 特有物件, 像 request / response / session 等... 不過 configuration 機制倒是還正常, 比另外準備一套 library 好一些, 用到的 code 也可以丟 app_code 下就好..

看起來還是有不少的問題待解決, 不過至少對於簡單的 scheduler task 有辦法處理了. 只要你對基本的 thread 控制有概念的話, 寫起來應該不是什麼大問題. 簡單寫了個 sample code, 沒做什麼事, 就是 web application 啟動之後, 會每隔十秒把現在的時間寫在 log file ...

sample source code download: [HERE](http://www.chicken-house.net/files/chicken/WebAppWorkerThreadSample.zip)