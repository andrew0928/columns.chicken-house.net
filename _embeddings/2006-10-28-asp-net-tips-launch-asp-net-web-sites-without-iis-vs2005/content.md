恩, 題目定的很偉大的樣子.. 其實只是個不起眼的小技巧而以.. 以往開發網站程式都要裝 IIS, 到 visual studio 2005 後就有內建的 Develop Web Server 可以用.

不過還是很麻煩, 比方說我另外一篇文章講到 NUnitLite 在 Web Application 上的應用, 我有提供 sample code, 抓下來後, 你可能會把它放到 iis 做些設定跑看看, 或是直接用 visual studio 2005 開 web site 後按 f5 跑看看... 兩種方式看來都很麻煩, 尤其我用 notebook, 開個 visual studio 2005 要等半天, 不是很有吸引力的 code 我可能就懶的開了, 哈哈..

<!--more-->

因為懶, 所以才有這 tips .. 我自己寫了個簡單的 batch file, 然後把它的捷徑放到 c:\Documents and Settings\{your account name}\SendTo 下, 就大功告成了.

以下是批次檔的內容:

---

```batch
set DEVWEB_PORT=%random%
start /min /low c:\Windows\Microsoft.NET\Framework\v2.0.50727\WebDev.WebServer.EXE /path:%1 /port:%DEVWEB_PORT%
start http://localhost:%DEVWEB_PORT%/
@set DEVWEB_PORT=
```

---

用的時後怎麼用? 以我前面舉的例子來說:

1. 把下載的檔案解開
2. 在檔案總管裡找到這個目錄
3. 目錄上按右鍵, 選 "傳送到" --> "Dev ASP.NET Web" (就是剛才拉的捷逕)

好, 大功告成... 這個動做就會像 visual studio 2005 一樣, 幫你把 dev web server 開起來, 同時幫你把 browser 也開起來..

enjoy it :D