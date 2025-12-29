---
date: 2018-07-24
datetime: 2018-07-24T01:31:37+08:00
timestamp_utc: 1532367097
title: "LCOW Docker Volume 效能測試：差距超乎想像"
---

純發牢騷... 雖然早就知道 docker volume 對效能有影響，但是實際測了才發現效能落差比我想像的還大啊...

果然 hyper-v 層級的 isolation 不是白吃的午餐... 看來可以再寫一篇 LCOW 踩雷記了..

用 LCOW 跑同樣版本的 Jekyll (3.8.1), Build 我自己的部落格...  差別是我的部落格檔案，一個是透過 volume 掛載，另一個是直接 copy 到 container 內...

跑出來的成績分別是 11.185 sec v.s. 77.538 sec ...

#LCOW #JEKYLL #GITPAGES

![](/images/facebook-posts/facebook-posts-attachment-2018-07-24-001-001.png)
