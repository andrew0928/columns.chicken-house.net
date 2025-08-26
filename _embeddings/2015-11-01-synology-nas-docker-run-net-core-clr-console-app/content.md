![Docker](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/synology_docker_thumb_256.png)

繼[上一篇](/2015/10/31/coreclr-helloworld-consoleapp/)講完我落落長的研究過程後，這篇補上昨天想寫最後卻沒加進去的內容，就是一樣的動作改用我自己的 NAS 所提供的 Docker 環境來做 ([官網](https://www.synology.com/zh-tw/dsm/app_packages/Docker))。試過之後只有一個感想... 果然買現成的實在輕鬆太多了 XD，如果不是很在意效能，只是想有個環境驗證看看，想避開整套 Linux 從無到有的 setup 過程的人可以試看看!

廢話上一篇都講過了，直接進入主題.. 這步驟跟昨天的比起來，實在是簡單太多了，這篇改一改就變成葉佩雯了，以後寫 ASPNET5 的人應該都去買台 NAS 才對... 不知以後會不會有 Visual Studio + NAS 同捆包? XD

以下是 step by step 的步驟:

# 開發環境準備: Core CLR 版 "Hello World !"

1. 開啟 Visual Studio 2015, 新增專案。這邊要留意的是專案類型，不知 RTM 後會不會改.. 我是找 Visual C# / Web / Console Application (Package) 才找到的, Console 歸類在 Web 下是有點怪.. 這邊的專案才是支援 Core CLR 的版本。建立名稱為 "HelloCoreCLR" 的新專案

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_563589e050a00.png)

2. 左上角 runtime 切到 DNX Core 5.0，補上一行印出訊息的 Code，按下 Ctrl-F5 執行

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56358bc0803ca.png)

3. 專案的設定頁面，記得勾選 "Produce outputs on build", 才看的到編譯好的輸出檔案.. 設定完之後存檔，BUILD，到 solution / artifacts / bin / 下可以看到編譯好的檔案

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56358c3594fc3.png)

   編譯後的輸出，目錄結構跟過去不大一樣:

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56358d04538dd.png)

# 事前準備: NAS + Docker

1. NAS 安裝 Docker 套件。我只有 Synology 的，Q 牌的用戶就抱歉了~

   裝這個套件:

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56358d6119b15.png)

2. 到 Docker / Registry 搜尋 image, keyword: microsoft/aspnet, 我是指定 tag: 1.0.0-beta8-coreclr

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56358df03680e.png)

3. image大小約 350mb, 完成後 DSM 會通知，到這邊準備動作就完成了

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56358eedbc0ef.png)

# 佈署與執行

1. Launch Container, 這動作等同於 docker run 這個指令。選取剛才下載的 image, 上方的 "launch" 按下去之後就有精靈引導你設定。

2. Step 1. Container Name: NetCoreCLR

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56358ffb04358.png)

3. Step 2, 資源限制跳過

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_5635903eddfbb.png)

4. 按下 "Advanced Settings", 加掛目錄到 container 內，等等可以簡化把檔案丟進去的過程。把 NAS 的 /docker/netcore 目錄，掛載到 container 內的 /home 目錄下，取消 ReadOnly 的選項。

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_563590c6f1c1e.png)

   完成後按下 Apply 完成設定

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_5635906e36809.png)

   最後記得，把剛才 Visual Studio 2015 編譯出來的檔案，COPY 到 NAS 的 /docker/netcore 目錄下。

5. 完成之後，Docker Container 清單應該就會多一項 NetCoreCLR, 右邊開關打開就可以啟動這個 container 了。

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_5635921d6ac0d.png)

6. 選取這個 container, 按上方的 "details", 可以看到這個 container 的運作情況，切到最後一個 tab, create new termainal, 進入終端機模式

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_56359288a4dad.png)

7. 好，到這邊之後，剩下的就跟昨天那篇講得一模一樣了，先切換工作目錄到 /home/dnxcore50:

   確認一下 .NET Core 版本:

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_5635964f0eb57.png)

8. 第一次執行，用 dnu restore 確認是否還有相依的 package 需要下載:

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_5635968ced9be.png)

9. 準備就緒，可以執行了! dnx HelloCoreCLR.dll

   ![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_563596bc4c7a3.png)

果然 NAS 包裝過的 Docker 簡單好用的多，省了很多腦細胞... 最後補張圖，大家猜猜這樣的 .NET Core CLR 環境需要吃多少記憶體? 很省啦，整個 container 才 6M ..

![](/images/2015-11-01-synology-nas-docker-run-net-core-clr-console-app/img_563597c80e76a.png)

看完別太興奮，馬上衝去買 NAS ...，如果真的是為了 Docker 想採購的話，務必先看一下支援清單.. 以 Synology 的來說，只有部分機種 (都是 intel cpu 為主) 才支援。詳細清單可以參考這裡:

https://www.synology.com/zh-tw/dsm/app_packages/Docker

#### 適用機種

| **16-系列 :** | **RS2416RP+,** **RS2416+,** **RS18016xs+** |
|---|---|
| **15-系列 :** | **RC18015xs+,** **DS3615xs,** **DS2415+,** **DS1815+,** **DS1515+,** **RS815RP+,** **RS815+,** **DS415+** |
| **14-系列 :** | **RS3614xs+,** **RS3614xs,** **RS3614RPxs,** **RS2414RP+,** **RS2414+,** **RS814RP+,** **RS814+** |
| **13-系列 :** | **DS2413+,** **RS3413xs+,** **RS10613xs+,** **DS1813+,** **DS1513+,** **DS713+** |
| **12-系列 :** | **DS3612xs,** **RS3412xs,** **RS3412RPxs,** **RS2212RP+,** **RS2212+,** **DS1812+,** **DS1512+,** **RS812RP+,** **RS812+,** **DS412+,** **DS712+** |
| **11-系列 :** | **DS3611xs,** **DS2411+,** **RS3411xs,** **RS3411RPxs,** **RS2211RP+,** **RS2211+,** **DS1511+,** **DS411+II,** **DS411+** |
| **10-系列 :** | **DS1010+,** **RS810RP+,** **RS810+,** **DS710+** |