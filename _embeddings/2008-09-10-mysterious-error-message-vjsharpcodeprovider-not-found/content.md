話說前陣子處理了 [BlogEngine.NET 升級到 1.4.5.0](/post/upgrade-to-be1450.aspx)，另外也寫了[ SecurePost.cs](/post/BlogEngine-Extension-Secure-Post-v10.aspx) 這個 extension, 其時都碰過這個鳥問題，只是一直沒去理它而以。接下來為了要改 [PostViewCounter](/post/BlogEngine-Extension-PostViewCount-10.aspx).cs (BE extension, too), 又碰到... 於是就認真的研究了一下...。

過程是這樣，為了建立 BlogEngine 的開發環境，首先我從[官方網站](http://www.codeplex.com/blogengine)下載了 source code, 解開後編譯都沒問題，OK。

接下來 WEB 的部份我把[網站](/)上的 source code 搬過來 (不包含 ~/App_Data，太大了)，編譯也 OK。

不過我要改 Counter 的 Code 啊，沒有一些 SAMPLE DATA 很難測試，只好把資料檔也搬過來.. 結果 Visual Studio 2008 就冷冷的回了這訊息給我:

**<font color="#0080ff">(0): Build (web): The CodeDom provider type "Microsoft.VJSharp.VJSharpCodeProvider, VJSharpCodeProvider, Version=2.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a" could not be located.</font>** 

 

我沒有漏貼前面的訊息... 的確是沒有檔名，也沒有行號(0)。我最不能忍受的就是沒頭沒尾的 ERROR MESSAGE 了。除了告訴你 "掛掉了" 之外，無頭無腦的對於追查問題實在沒什麼幫助。只好靠自己了...。雖然這是個 compile error message，不過我要 RUN 的畢竟是個 web site, 不編譯也是可以跑，除了那個惱人的錯誤訊息之外，要執行倒是沒問題。只不過編譯失敗，我就不能設中斷點，直接 F5 執行測試。雖然可以另外手動 Attach Process 的方式來除錯，不過每次都要這樣搞實在是很煩..

 

仔細想了想，沒錯，我是沒裝 Visual J#。不過我的確沒要用 Visual J# 啊，如果真的用到 J# 的話，出這訊息是應該的。訊息沒有原始檔? 也沒有錯誤行號? 那問題應該是 Global 的範圍，第一個想到的就是 web.config 是不是定義了 CodeDom 或是指定了相關的 CodeProvider ? 無奈查了一遍沒看到，VS2008 的 PROJECT 設定也沒看到引用任何 J# 相關的 LIB...

 

已經到了死馬當活馬醫的地步... 開始亂找一通碰碰運氣。搜尋了一下有沒有 *.java 的檔? OUCH，還真的有... 在 ~/App_Data/files 下找到我古董檔案，研究所時代寫的 Java Applet .... 順手試一下，刪掉後還真的就過了? 這個無頭無腦的問題，就在不知不覺中找到 solution, case closed!

 

怒... 這樣也算? 找到 .java 的程式碼，去找 VJ# 來編譯還說的過去，不過找 "source code" 找到 ~/App_Data 實在是太超過了一點... 好歹也列個要編譯那個檔案，然後找不到對應的 CodeProvider，這樣要排除問題也簡單一點...

 

結論是: 各位別太鐵齒，看來 ~/App_Data 下的檔案也是不能亂塞的...