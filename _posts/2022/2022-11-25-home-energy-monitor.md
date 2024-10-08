---
layout: post
title: "水電工日誌 #9. 監控全家用電神器, Emporia Vue 2"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "有的沒有的", "敗家"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: /wp-content/images/2022-11-25-home-energy-monitor/2022-11-18-01-47-59.png
---

![](/wp-content/images/2022-11-25-home-energy-monitor/2022-11-18-01-47-59.png)

水電工的技能又進階了，這次是 "真正" 的水電工, 我在家裡的電源總開關那邊動手腳，裝了能監控全家即時用電量的神器: Emporia Vue 2 - Energy Monitor. 這一切都要從天氣越來越熱, 開冷氣電費越來越貴, 然後台電今年還漲價等一連串惡夢開始...

平時在講 DevOps 都知道要先能量測，才能改善... (講到都會背了，果然是只出一張嘴的角色)，既然都被電費嚇到了，第一件事就是先要了解到底電費都花在那些地方開啊，於是過去幾個月，嘗試過很多種 solution, 都覺得不滿意... 我跟我家大人曾經嘗試過這些手段:

1. 每天看電表數字 (在大樓地下室)
1. 台電智慧電表 APP, 對照家人的作息交叉比對
1. 用智慧延長線，逐一測試每個家電耗電量
1. 換了有 APP 能監控用電量的除濕機
1. 認真研究日立冷氣的智慧家電模組 (最後沒買)

最後這些方法都太侷限，只能理解單一家電特定時間的耗電，但是就像抓 bug 一樣啊，沒有先縮小範圍持續觀察，一開始就逐一檢查每一行 code, 很難抓出 OOM 或是效能等等較不明顯的問題啊，直到最後看到 facebook 社團有人在分享 Emporia Vue 2 這好物.. 

<!--more-->


因為買了這些東西，我才發現原來我默默都為了這些不起眼的小地方繳了不少電費啊，包含待機的螢幕x2 (超意外)，待機的電視，除濕機都在榜上。得力於即時監控，我也終於搞清楚變頻冷氣的運作模式了，這也很意外，跟我以前想像的不大一樣啊；最後當作科普的題材，也因為要安裝這東西，我也搞懂了一些水電的基本知識 (該去考證照了嗎 XDD)，總算弄清楚家用的電力線路是怎麼配置的，火線跟零線該怎麼接等等，最後一段也來分享一下這些真正的水電工知識吧!



# 主角介紹: Emporia Vue 2

在講抓耗電元凶的過程之前，先來推坑吧! 我猜會對這篇有興趣的應該都是想看開箱文... 我就不弔胃口了。找來找去，繁體中文好像就只有這麼一篇開箱文:

[Emporia Vue Energy Monitor 全戶電源電流用電量監測器](https://wsmwason.com/blog/post/604)

這是直接裝在家裡電箱 (總開關) 的用電監控設備，我在 amazon.com 買 2 + 16 sensors 的套餐，其中 2 個 200A 的 sensor 可以直接監控總電源 (理論上就是對應到台電電表的數字才對)，另外 16 個 50A 的則是讓你監控個別的斷路器用的，我家有 17 個斷路器，我就把兩個合併成一個，花了一個周末整線，成功的把它塞進我家的電箱了。

想敗家的應該會對安裝過程有興趣，這個我後面再介紹。就先來展示成果好了。首先，他的電量計算還蠻精準的，數據取樣可以精準到秒。數據必須透過 wifi 上傳到雲端，再用他的 APP 或是官網登入帳號來看數據。他的服務可以讓你看到所有 sensor 的每秒數據，這點很棒，我靠他找到好幾個吃電怪獸... 我貼一張 APP 的截圖:

![](/wp-content/images/2022-11-25-home-energy-monitor/2022-11-19-02-23-11.png)

按照官網的說明，每秒的 sample 數據會保留三小時，每分鐘的數據保留七天，每小時以上的統計 (每天、每周、每月、每年) 就會替你永久保留了。台電的智慧電表 APP 的精確度就沒那麼好，最精確只有到 15 分鐘，而且只有全家耗電，數據也要等兩個小時後才看的到...。不過我好奇對照了一下，用前一天的數據對比:

![](/wp-content/images/2022-11-25-home-energy-monitor/2022-11-19-02-28-03.png)

精確度還蠻高的啊! 同樣是 2022/11/13 整天的耗電量，台電智慧電表顯示 24.26 度, 而我裝的電量監控回報 23.850 度, 誤差只有 1.69%, 而且能每秒回報, 還能分 16 個斷路器個別監控, 我已經很滿意了 :D

底下的數字，則是 16 個獨立 sensor 回報的數字，一樣都是即時數據，我就不一個一個列了。反而是 16 個 sensor 的耗電量跟總耗電量的誤差比較大，所以會多一項 Balance 數據，他是調整誤差用的而已。如果你是圖表控，你也可以切換成 Graphs 模式，看柱狀圖比較能視覺化的看到用電狀況:

![](/wp-content/images/2022-11-25-home-energy-monitor/2022-11-19-02-35-36.png)

這是我家變頻冷氣的使用狀況，老實說我直到這時刻，我才搞清楚開了冷氣之後的耗電曲線原來是長這個樣子啊，後面我也會補圖說明一下變頻冷氣開一整晚的狀況，到底 "變頻" 是在變什麼..。至於設備裝好後，實體長啥樣，先貼張照片讓各位瞧瞧:

![](/wp-content/images/2022-11-25-home-energy-monitor/2022-11-19-02-39-40.png)

這是我家的電箱，右上角那台就是主機了，小小一台巴掌大而已。一堆白色的線就是他的電流偵測器。不用擔心安裝是否很困難，還蠻容易的。各位有用過勾表量電流嗎? 大概就是那樣的東西，你用一個磁環框住電線，就能測量出通過那條電線的電流數值了。不需要接觸到銅線就能測量，所以還蠻安全的，只要把磁扣打開，用正確的方向框住電線，然後把這條線的另一頭插上主機就行了。最困難的地方就是電源，你要把電源正確地接到 +110v, -110v 火線, 中性線 就可以了。有基本水電常識的應該都能自己裝吧，擔心的話就請有經驗的人代勞就好。我家電箱沒有很大，最辛苦的其實都是拆拆裝裝，還有整理那堆線把它塞得漂亮一點而已...

搞得這麼亂一定會被我家大人嫌棄的啊，所以最後把面板鎖回去，用標籤機把編號標上去，雜亂的線就蓋在後面眼不見為淨就好:

![](/wp-content/images/2022-11-25-home-energy-monitor/2022-11-19-02-47-20.png)

最後就是 wifi, 其實他有一根天線 (只支援 2.4G, IoT 設備大概都是這樣, 如果你家只開 5G 記得要把 2.4G 訊號打開)，可以讓你拉到外面來的，不過我家電箱的位置離 UniFi AP 還蠻近的，就算蓋子蓋起來也收的到訊號，我就沒特別弄這個了，最後蓋起來完全看不出來，打完收工 :D




# 揪出耗電兇手的奮鬥過程


瓦時計

除濕機 (自帶能源監控)

冷氣機 智慧家電 APP

智慧延長線

智慧電表

家用能源監控

接入 Home Assistant

電氣知識



電冰箱
除濕機
變頻冷氣 (模式、噸數)
螢幕待機
機櫃
兒子的電腦 + 顯示卡



