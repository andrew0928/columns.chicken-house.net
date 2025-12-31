---
date: 2018-10-07
datetime: 2018-10-07T23:11:40+08:00
timestamp_utc: 1538925100
title: ".NET Conf 2018 Message Queue Based RPC 演講重製影片"
---

感謝 Study4.TW 邀請，這次在台中逢甲大學舉辦的 .NET Conf 2018, 難得有機會上台講這場 Message Queue Based RPC :)

這場我省略了很多架構的介紹，把重點專注在如何實作好的 RPC Client / Server 的技巧。要寫這東西，多執行緒的控制技巧是省不掉的啊! 寫這個 project 時很慶幸，當年練過自己寫 thread pool .. 因此這個 project 還難不倒我，不過如何讓 Message Queue Consumer 能夠正確的關機 (Graceful Shutdown) 不是件容易的事啊! 我也竟然成功的在 50 分鐘內介紹完這個實作的架構 :D

重製過的影片 (聲音是現場錄製的) 我就搶先大會直接公布了! 其它相關連結我就列在下方，有需要的可以直接取用:

1. Sample Code: https://github.com/andrew0928/Meetup/tree/master/20180929.dotNetConf/MQRPCDEMO

2. Slide Share:  https://www.slideshare.net/chickenwu/net-conf-2018-message-queue-based-rpc

3. HackMD 共筆: https://hackmd.io/th8VT7sLR8CdYzypmqTkyQ

不過有點烏龍的是，這次螢幕錄影誤踩到錄影軟體的 bug, 沒有錄下來... 最後是我事後看著大會的錄影，自己看著自己講的影片，重新操作一次 PPT 後製的，如果有點不同步就請多包涵啦..

#感覺像是以前幫老闆在後面操作PPT一樣..
