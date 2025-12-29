---
date: 2023-02-22
datetime: 2023-02-22T22:22:02+08:00
timestamp_utc: 1677075722
title: "幾個月前看到這篇，剛好前天補了 API Design Workshsop 的文章，就順手也分享這篇聊"
---

幾個月前看到這篇，剛好前天補了 API Design Workshsop 的文章，就順手也分享這篇聊聊裡面我看到的幾個觀點..

這篇是 Netflix 自己人，介紹他們內部自行開發的 Queueing System .. 想分享這篇有幾個原因:

1. 文內有張圖，介紹他們的 workloads 狀態轉移 (對，就是狀態機)，其中狀態轉移的路徑就直接對應到它們開出來的 API, 同時也標示出 event 觸發.. 雖然沒有明講，但是背後就完全是我前天介紹的 API Design Workshop 要說明的理念不謀而合

2. 這篇介紹的 Queueing System, 跟我自己在公司內部負責的某個系統很雷同，看了它們的設計就覺得.. 

"啊，我構思的架構就算對上 Netflix 也是能打的啊 XDD"

想起當年某個場合，我在介紹 message queue, 就被問到放進 queue 的 message 怎麼被查詢 & 管理 (例如刪除)，當下我還真的回答不出來，只想說...

"啊 queue 就是 first in first out 啊, 怎麼可能讓你隨便刪除.."

不過，越看越多需求與應用後，我開始想通這件事了，這也是為何 message queue 這麼成熟了，就算是 Netflix 這樣規模的公司，也得自己 "重新發明" (後來我才想通並不是) 輪子，自己幹一套 queue + database 的系統出來...

message queu 要解決的是分配 workload, 避免瞬間併發的需求衝到 workload 的緩衝。解決的是一瞬間 (秒級) 的問題，但是 Netflix 這套 queueing system 解決的是長時間的排程 (它們用來排隊影片轉檔的 workloads)... 這種層級的 workloads, 的確是需要更精準地控制能力，要能刪除，調整順序... etc..

所以合理的作法，用時間切割。在排定時間到了的那瞬間才把 workloads 從 database 轉移到 message queue .. 在那之前就乖乖地待在 database 內。因此這整套系統就須要有精準地從 DB 撈出指定時間執行任務的能力...

(對，就是我寫的這篇: 排成任務的處理機制練習)
https://columns.chicken-house.net/2019/08/30/scheduling-practices/

丟到 message queue 後，就需要有效率處理多個 workloads 的能力...

(對，就是我寫的這篇: Process Pool 的設計與應用)
https://columns.chicken-house.net/2020/02/09/process-pool/

每個任務，都有它的狀態轉移與生命週期。要控制這些任務的 API 設計方式，就需要配合狀態機來設計..

(對，就是最近這幾篇 API First 系列的文章，我舉前天那篇當作代表: API Design Workshop)
https://columns.chicken-house.net/2023/01/01/api-design-workshop/

都透過 message queue 處理任務，雖然你可以射後不理，反正他終究會被執行... 但是你總得關心一下處理時間有沒有延遲到超出預期吧? 這些控制每個 workloads 服務水準的方式...

(對，就是我寫的這篇: 非同步系統的服務水準保證；非同步系統的 SLO 設計)
https://columns.chicken-house.net/2021/06/04/slo/

好吧，好像捧自己捧過頭了 XDD, 不過, 這也呼應了我這篇講職涯發展的文章... 知識能彼此串聯起來應用，你就能發揮別人所追不上的影響力..

(對，又是我寫的... 刻意練習，打好基礎)
https://columns.chicken-house.net/2021/03/01/practice-01/

最後就用這篇結尾吧，你學了很多技能，直到你真正能靈活應用，把你熟悉的知識組合起來應用，就能達到不同的境界創造出價值。這時你就不再是碼農，而是有解決問題能力的工程師。

被我拿來貫穿我這麼多篇文章的主軸，是這篇 (大推):

Timestone: Netflix’s High-Throughput, Low-Latency Priority Queueing System with Built-in Support for Non-Parallelizable Workloads

https://netflixtechblog.com/timestone-netflixs-high-throughput-low-latency-priority-queueing-system-with-built-in-support-1abf249ba95f

--
這篇我用排程發文，單純要湊時間而已，紀念一下 XDDD
發文時間排在 2023/02/22 22:22 ..
