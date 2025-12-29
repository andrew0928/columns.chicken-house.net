---
date: 2025-03-22
datetime: 2025-03-22T19:52:43+08:00
timestamp_utc: 1742644363
title: ", RAG as a Service, Microsoft Kernel Memory"
---

#5, RAG as a Service, Microsoft Kernel Memory

鋪了四天的梗, 第五天終於來到正題, 今天就直接來聊聊 Microsoft Kernel Memory 這個 open source project 吧~

Microsoft Kernel Memory ( 以下簡稱 MSKM ), 背後的開發團隊跟 Semantic Kernel ( 以下簡稱 SK ) 是同一個團隊，因此有幾個地方, 是 .NET 人員可以期待的。不但架構設計上格局夠大，可以橫向擴充到極大的規模，也可以小到像 SQLite 那樣內嵌在你的應用程式內。而軟體功能的擴充性也很棒，除了有各種 AI service 的連接器之外，文件匯入 MSKM 的 pipeline, 你也可以完全自訂自己的 handler, 將自己的邏輯內建在 MSKM 內..

這次我截了兩頁簡報，分別代表了 MSKM 的兩種應用方式。第一個是 as web service, 你可以透過 http api 來存取 MSKM, 或是你也可以用 serverless 的模式, 直接把整套 MSKM 核心機制直接內嵌在你的應用內 (不是跑個 localhost 再用 http api 的做法喔)，基本上已經顧及到各種規模跟應用的方式了。

回到 MSKM 這專案本身，他要解決的環節，主要就是 AI APP 最棘手的 " long term memory " 的管理問題。在 SK 內，短期記憶是用 Chat History 來處理的，而長期記憶只是定義了 Memory ( Vector Store ) 來處理。不過，仔細看他的說明，你會發現 Memory 其實比較像是抽象化的向量資料庫，有點像 EF (Entity Framework) 之於關聯式資料庫，Vector Store 就是讓你定義你的 Vector Store 結構，方便你 CRUD，並且直接定義好相似性檢索的 interface ..

但是如果你理解 RAG ( 尤其是 document ingestion ) 怎樣匯入文件內容的話，你會發現，從內容的文字化，內容的分段，合成，貼標籤，向量化，寫入，查詢... 這一大段的流程，SK Memory 只處理了最後一小段而已

所以，MSKM 這專案就因為這樣，被獨立出來了。由於你要做大量文字的處理，通常也很吃你的長時間任務處理的機制是否成熟 (大概就式分散式任務處理那類的問題)，因此與其像是 SK 那樣用 Framework 的方式發行，MSKM 則選擇用了 "獨立服務" + SDK 的方式來發行。你可以直接拿 source code ( 從 github clone ) 來使用，你也可以直接從 docker hub 拉 image 回來直接部署 ( 不用寫 code )，在呼叫端你可以直接用他的 NuGet Package ... 都是為了這個目的而設計的

而被當成獨立服務來看待，那 MSKM 跟 SK 就算是同一個團隊開發的，好像也沒有什麼特別的關聯... 這樣想你就錯了，我在這邊特別提兩個地方，特別適合兩者搭配使用的情境:

1. MSKM 內建支援 SK 的 Memory Plugin
MSKM 已經在他的 NuGet package 內準備好 SK 使用的 Memory Plugins 了，你可以直接將他掛上 SK Plugins 內使用的。一旦掛上去之後，其實你就等於替 AI 追加了一組能直接操作 MSKM 的 tools 了。前面聊到的 Function Calling, 你可以想像 MSKM 支援的功能也都能被 AI 判斷與呼叫使用了

2. MSKM 本身也同樣是用 SK 開發的，SK 支援的各種 connector 你都不用擔心，都可以在 MSKM 上直接使用。例如 LLM / Embedding 的 AI 服務 ( openai, azure openai, ollama, claude ... 等等 ) 通通都支援

這一切這樣組合起來，我覺得是目前 .NET 領域最成熟的組合了，MSKM 不適合那種開箱即用，需要配套的 UI 跟管理工具的終端服務，她更適合的是給開發人員使用的獨立服務。既然對象是 Developer, 那麼先具備基礎的 AI APP 開發知識是必要的。這也是為何我會先安排 #1 ~ #4, 花了些篇幅先介紹前面的基礎知識，因為你掌握了這些，才能充分體會 MSKM 設計的精妙之處

--
同樣又來到葉配時間 XDD

這些設計的精妙，很多巧思你沒真正看到 code 其實很難體會的，03/25 的直播我就不大再重複簡報的內容了，直接帶大家看滿滿的 sample code. 有興趣的請記得參加 03/25 的直播, 連結我放在第一個留言

--
預告 #6, 如果你這些技能都備齊了, 明天我要來聊聊用 SK + MSKM 示範一些進階的 RAG 應用方式, 請期待明天的葉佩文 :D

![](/images/facebook-posts/facebook-posts-attachment-2025-03-22-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-03-22-001-002.png)
