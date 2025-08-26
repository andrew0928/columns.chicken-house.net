升級 Vista 第四天, 來講幾個令我超不爽的地方.... 

1. 內建的工具列, 現在竟然不能拉出工作列了... [:@] 
2. 內建陽春的注音輸入法大改一通... 這一天終於來了 [:'(] 
3. Console 不再能直接拉檔案過去, 代表直接輸入完整路逕了, ouch... 
4. 兩個影像相關的 PowerToys 不能用... ( Image Resizer, RAW Image Viewer) 
5. UAC 真囉唆...

看起來沒什麼大不了, 不過這些都佔了我平常用電腦的大多數動作... 真是晴天霹靂... 還好是家裡的電腦, 愉樂用途居多, 如果是工作用的電腦, 我大概會抓狂... 比較起來, (2) 跟 (4) 對我影響最大, (2) 只要輸入中文的地方, 打起來都覺的怪怪的... 因為這幾個地方都不一樣了:

- 最陽春的注音已經沒有底下一排的那種模式了 
- 從 DOS 時代就能用的 ALT+KEYPAD 輸入 ASCII 碼的功能也被拿掉了  
  (我常習慣打 ALT-4, ALT-4 代表 ASCII 碼為 44 的字元: 逗號, 因為這樣不用切回英數模式) 
- 中文模式下按住SHIFT是可以輸入英文沒錯, 不過以前這樣打是小寫, 現在變大寫... [:@]... 
- 注音還停在選字的時後 (就字底下有虛線的狀態) 不能按 BACKSPACE 取消  
  (打慣的我常因為這, 玩 WOW 邊打邊聊天就卡住, 法術按不出來就趴了... [:@])

真是太讚了 [:@], 打到這邊已經打錯好幾個字, 十幾年來養成的習慣, 不知道要啥時才有可能習慣... Orz, 之前從windows2000就在耽心, 傳統的笨注音何時會被拿掉, 看來 vista 已經是第一步了... [:'(]

而 (4), 不能裝 RAW Image Viewer, 連帶的讓我自己寫的[歸檔](/wp-content/be-files/archive/2006/12/23/cr2-supported.aspx)程式都不能用 (因為我是靠它的 wrapper 才能讀取 canon raw file)... 真是... 查了一下 MicrosoftDN, 原來 vista 裡已經全面改用 WPF 處理, 因此原本內建的 image 相關軟體都換過了, 以 .NET 來說, 就是從原本的 GDI+ (System.Draw) 改到 WIC (Windows Imaging Component, System.Media.Imaging). 像 video 一樣, 針對各種不同的 image file 也改用 codec 的方式來處理了. 這也是 Microsoft 在 HD Photo 計劃裡重要的一環, 藉著 WPF 首次引入 [HD Photo](http://en.wikipedia.org/wiki/HD_Photo) ( Windows Media Photo ), 目標是把 JPEG 換掉, 不過應該有好一段路要走.... 看起來以後會有較正式的 API 可以存取 RAW file, 不用像我之前一樣要走旁門... 不過, Nikon 已經提供了 NFE 檔的 WIC codec 下載, Canon 的 CRW 咧? [:'(] 看起來是該把歸檔程式用 WIC 改一下了... 只要 Canon Codec 快點出來...

(5) 則是大名鼎鼎的 [UAC](http://technet.microsoft.com/en-us/windowsvista/aa906021.aspx), 可以預防管理者不知不覺做了啥危險的動作. 只要你執行的程式要做較危險的動作, 就會跳出來跟你確認一下... 用意很好, 不過實在有點煩人, 感覺好像以前用 AntiVirus, 我自己有一些 script 用 FileSystemObject 在做事, Norton AV 老跳出來警告我, 認為我寫的 script 是病毒... 現在又是一樣的感覺, 真是... 不過隨便 GOOGLE 查了一下, 沒想到賽門鐵克 (就是賣 AntiVirus 的公司) 還會[放話說 UAC 不好](http://cpro.com.tw/channel/news/content/index.php?news_id=53758), 真是, 要嘲笑鱉沒尾巴也不是這樣笑的....

大概我碰 UNIX 比碰 window 來的早, 我還是比較習慣 sudo 的作法. sudo 是在你需要時, 才主動透過 sudo 暫時取得 root 的身份來做事. 平常用的帳號本來就不該有太大的權限. 從 NT 以來, 不用 administrator 登入, 跟本很難做事, 我曾經自己很安份的用 Power Users 身份的帳號工作了一陣子, 後來實在是受不了又換回來... 到了 2000 / xp 情況就好多了, 有很類似 sudo 的 runas 指令可以用, 也可以在捷徑上先指定好 runas 執行身份... ( 沒錯, 我把 DOS prompt 還有 MMC 拉了捷逕, 設成 administrator 身份開啟 ), 用 PowerUsers 身份就用的很快樂...

不過碰到 UAC 真是一肚子火, 嘖嘖, 對知道的人是幫倒忙, 對不知道的人他也只會通通按 YES -_-, 就像所有的精靈都是按下一步一樣, 哈哈... 不過至少還是有進步, 畢竟不是每個人都有嫌工夫像我一樣設 RUNAS ..., 不過不習慣就是不習慣, 試沒多久就把 UAC 給關了.. [:$]

牢騷發完了, 謝謝收看 [:D], 下回來寫點正面的...