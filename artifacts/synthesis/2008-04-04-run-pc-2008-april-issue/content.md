![IMG_6727 (Canon PowerShot G9)](/images/2008-04-04-run-pc-2008-april-issue/IMG_6727%20(Canon%20PowerShot%20G9).jpg).jpg)

沒錯，我的文章在四月號的 RUN! PC 刊出來了，之前花了些時間在研究執行緒跟 ASP.NET 搭配起來用的技術問題，有點小心得，就整理了一下投稿了，運氣還不錯，雜誌社也願意刊出。初次投稿花了不少時間，花在重新思考 sample code 怎麼寫比較能突顯主題，圖表要怎麼畫才清楚明瞭等等瑣事上面，原來當個專欄作家 (我沒有專欄啦，只是投稿而以) 也不是這麼簡單的...

文章的內容嘛，看雜誌就知道了，這篇是留著作個紀念，同時也是讓看了這篇文章有話要說的讀者們，有個留下 comments 的地方。

文章裡提到的 sample code 可以到 [這裡](http://demo.chicken-house.net/runpc/2008-04/2008-04.zip) 下載，懶的抓回去執行的人，也可以直接到 [這裡](http://demo.chicken-house.net/runpc/2008-04/) 試 RUN 看看文章裡提到的範例。

在執行這個範例程式之前，請先注意一下，IE預設只會對同一個網站建立兩個Http Connection，因此有可能會看到不一樣的測試結果。如果想要調大這個限制，請修改下列的註冊機碼，或是下載本文的範例程式，匯入[IE.reg](http://demo.chicken-house.net/runpc/2008-04/ie.reg)註冊機碼。

**調整IE同時連線數的註冊機碼**

```registry
[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Internet Settings]
"MaxConnectionsPerServer"=dword:00000008
"MaxConnectionsPer1_0Server"=dword:00000008
```

相關連結: [範例程式下載](http://demo.chicken-house.net/runpc/2008-04/2008-04.zip) [執行範例程式](http://demo.chicken-house.net/runpc/2008-04/) [下載調整IE連線上限的註冊檔](http://demo.chicken-house.net/runpc/2008-04/ie.reg)