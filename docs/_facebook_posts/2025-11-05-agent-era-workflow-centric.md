---
date: 2025-11-05
datetime: 2025-11-05T19:21:40+08:00
timestamp_utc: 1762341700
title: "Agent 的年代, 果然一切都還是以 workflow 為主軸, 而 workflow 執行的過程"
---

Agent 的年代, 果然一切都還是以 workflow 為主軸, 而 workflow 執行的過程就是靠有效的管理 context 來引導每個步驟的執行

前天貼的 vibe coding: testkit 的示範影片, 我把我想像 AI Native Testing 的流程示範了一次, 分成三段:

* gentest
把需求展開成 decision table, 輸出多個 testcase (md)

* run
我做了個能按照 openapi spec 執行 testcase 的 MCP, 逐步呼叫驗證流程, 留下 log (就像你寫 API test code 前會先拿 postman 跑一次一樣)

* gencode
拿 testcase, openapi spec, 以及 http logs 當作素材, 生成最終的測試程式

雖然成效不錯, 但是我對最後產生的 test code 並不是很滿意, 每次產生的都有不同的風格.. 我試著調整幾次 instructions 後, 我突然想到..

既然我都有了完美的 spec(s) 素材了, 為什麼我還要自己寫 gen code 的instructions 呢?

這裡所謂完美的 spec:

1. openapi spec
2. 實際可行的呼叫紀錄 (like postman collection)
3. 對應的商業情境 testcase (given when then)

其實用 speckit 最難的就是要能決定 「規格」。而對 api auto test 這目的來說，有了完整的這三項資料背書，我已經不缺規格了啊

於是, 花了點時間, 把 gencode 的步驟, 改用 spec-kit 來替代, 果然輸出結果穩定可靠多了

果然這年代, 不再是什麼都自己來了 (就算是 prompt 也是), 善用別人的 best practices 才是王道. 拜 AI 所賜, 這樣的整合不再有什麼規格限制, 就是放在一起, 下對 prompt 就可以了

這次錄影有 70min, 應該沒人想看吧 XDD
我先貼張圖當作代表, 詳細過程等我整理好再發表

圖說:
- 左: 整個 API test 的開發專案 workspace
- 中: 最終透過 speckit 開發出來的 test code (c#, xunit)
- 右: 用我的 testkit, 透過 vibe testing 流程產生的 test case

結論: 看起來 測試案例完全對應測試程式碼, 有達成我的期待 :D

![](/images/facebook-posts/facebook-posts-attachment-2025-11-05-001-001.png)
