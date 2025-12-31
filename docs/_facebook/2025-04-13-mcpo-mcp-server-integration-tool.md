---
date: 2025-04-13
datetime: 2025-04-13T18:07:52+08:00
timestamp_utc: 1744538872
title: "介紹一個來自 open-webui 的專案: mcpo, 可以將市面上眾多的 mcp server"
---

介紹一個來自 open-webui 的專案: mcpo, 可以將市面上眾多的 mcp server 立即轉成符合 open api 規範的 rest http api

這專案由 open-webui 來發動, 其實一點也不奇怪, 原理後面再講, mcpo 轉換後的規格, 完全就符合 open-webui 對 tools server 的要求啊 ( open-webui 本身直接支援 open api 規範的 api server, 當作 tools 給 LLM 使用)。講白話一點，你可以架設 ollama + open-webui + mcpo, 這樣的組合你能完全用本地端的資源架設類似 ChatGPT 的服務, 同時還可以在上面啟用 MCP server...

參考我貼的螢幕截圖，就是我拿 docker 版本的 mcpo 試玩的結果, 架設還挺容易的, 其實寫個 docker-compose.yaml 就搞定了, 我在本機跑了 LLAMA 3.3 ( 70B ) 來試試看, 支援 function calling 的 LLM, 果然能順利的叫用 filesystem, 來回答我的問題..

--
介紹完畢, 想了解背後在幹嘛的可以繼續看:

回到 mcpo 這專案到底做了什麼, 先聊聊 MCP 是什麼東西吧.. MCP (Model Context Protocol) 是 Anthropic ( 推出 Claude 的那家公司 ) 推動的標準通訊協定，讓 MCP Host 能替 LLM 無痛使用 ( MCP Client ) Tools ( MCP Server ) 的通訊協定.

這通訊協定，意外的因為各種 AI coding 的 IDE 而爆紅 ( ex: Cursor, Windsurf .. ). 我認為爆紅主要原因之一是: 他支援 stdio 當作傳輸的通道, 這好處是你完全不用搞定網路問題, 你不用預先跑一個 server, 設定 port ... 這種架構對於 desktop application 而言是很麻煩的事情。

換成 stdio 的話, server 的角色就退化成一個 CLI 就好了, request 當成 standard input, response 當成 standard output, 中間的傳輸結構直接用 jsonrpc 2.0, 只需要設定正確, 必要時由 MCP Host 主動 create process, 透過 stdio 傳輸, 不需要時 kill process 就可以了, 完全是適合 desktop app 的應用方式..

因此，搭配 Cursor, 一瞬間 MCP 就變成顯學了。不過骨子裡這 protocol 其實就是眾多 RPC 的一種而已。所有成熟的 RPC 協定，大概都處理兩件事:

1. discovery, 告訴對方你提供那些 api service?
2. invoke, 按照規格呼叫指定的 api ( 要提供 name + parameters )

如果不管傳輸通道 ( transport ) 是 http or stdio 的話, 其實大家都一樣。MCP 支援了 tools/list, 跟 tools/call 指令可以完成這些任務。反觀如果我重點在 http, 其實老早就存在 Open API ( 前身就是 swagger ) 了啊，Open API 靠 Spec ( swagger file ) 來描述支援的 API 規格, 而你理解這規格後直接發出對應的 Http Request 就可以呼叫 API 了。我一年半前在 Chat GPT 上面實作 "安德魯小舖"，當時 Chat GPT 就是用 Open API + OAuth2.0 的協定來串連 LLM 跟 API 的。好處都是成熟的技術，有高機率你既有的標準 API 不用修改就能符合要求了。

透過 stdio 有很多便利的好處, 不過我覺得這也是它發展的瓶頸, 首先, 這運作方式完全跨不出 "desktop" 的範圍，到了行動端，或是 server 端就行不通了。MCP 支援 http / sse, 但是大部分通行的都還是 stdio 為主...

另一個隱憂是 MCP 沒有規範 "使用者" 端的認證機制 ( 2025/03/26 的修訂規格開始支援了，不過限定 http + oauth2.1, stdio 仍然不支援 )，這也綁住了你的 server 就只能給特定的 user 使用。如果 tools 處理的資訊包含 "個人化" 的訊息，那你勢必得替不同的 user 個別安裝一套 server ( 至少要有不同的 access token 吧 )，這些都是影響資訊安全的結構問題，先天閃開這些問題的 MCP, 發展會受限。這是為何在非 desktop 的應用，還沒有看到很大量的使用 MCP 的原因。

而 Open WebUI 這套 LLM 的 Web 聊天介面，也是老早就支援 Open API 規範的 Tools 了，面對突然爆紅的 MCP，他的對應方式不是 "立馬支援"，而是開發 protocol 轉換的服務，即時的把 MCP 轉成 Open API 就結束了。他從一開始的出發點，就是典型的 server 端應用的思維, 架設好了你只要連過來使用就好。整合都透過 API，不需要在 Chat Server 本機安裝任何外部的服務。取而代之的是要設定外部的 service end point + api key 等資訊。

因此，你只要在 Open WebUI 上設定 "manage tool servers" 就好了。而 MCPO 本身的安裝也很容易，最無腦的做法是餵給他 Claude Desktop 的 json 設定檔就可以啟動 MCPO 了。

蠻有意思的小工具，有興趣在本地端架設類似 Chat GPT 的服務，同時還想掛上一堆 MCP tools 來玩玩的朋友可以試試~

![](/images/facebook-posts/facebook-posts-attachment-2025-04-13-001-001.png)
