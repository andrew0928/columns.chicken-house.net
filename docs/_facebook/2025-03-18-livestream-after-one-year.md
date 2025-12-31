---
date: 2025-03-18
datetime: 2025-03-18T02:32:41+08:00
timestamp_utc: 1742236361
title: "這場直播，欠了一年多了 XDD"
---

這場直播，欠了一年多了 XDD
從 Kernel Memory 還在 0.2.x 版的時候, 到現在都 0.9.7 了。

不過，會跟保哥合開這場直播，倒也還有其他原因。其實在去年底的 .NET Conf 2024, 我已經講過這主題了。但是畢竟是 Conf, 能用的時間有限，能講的 code 也有限 (那天幾乎沒有 show code)...

Kernel Memory, 是 Microsoft 開發 Semantic Kernel 同一個團隊的作品，仔細觀察這兩個 repo, 你會發現 owner 是同一位, 就是這團隊的架構師。KM 的定位，是能靈活運用調配的服務，能獨立運作 (只靠 API)，可大可小 (單機 + 橫向擴充)，如果你願意，甚至能小到像 SQLite 那樣 serverless mode ...

即使你使用 API, 他也緊密地跟 Semantic Kernel 整合，內建 SK plugins, 整套設計下來，其實就是為了跟 SK 一起使用的服務啊! 這種主題怎麼能不 show code ..

因此，這次保哥說可以講到半夜 XDDD，我就決定，這次主題我不準備投影片了 (我還是會介紹一下，就直接沿用 .NET Conf 那場的簡報)。相對的，我會從 LLM 常見的幾個基本動作 ( chat completion, structured output, function calling, agent ) x 幾種不同的實作方式 ( openai api, openai .net sdk, semantic kernel ) 的組合, 挖掘一下這些 AI 操作的基本動作

搞懂這些，最後我再 demo KM plugins 的整合應用，示範一下 LLM + KM plugins 來做 RAG 的威力。如果你嫌使用方式還不夠靈活，最後還有一個直接把 KM 封裝成 MCP server 的案例... 你可以直接在 claude desktop, cursor .... 等等支援 MCP 的 Host 上面使用他

有興趣的先把時間留下來吧，接下來的幾天我再逐步釋出這些我想聊的 topic. 大家下週線上見 :D
