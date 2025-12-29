---
date: 2025-03-24
datetime: 2025-03-24T20:00:08+08:00
timestamp_utc: 1742817608
title: ", 開發 MCPserver, 整合 Kernel Memory Service 與 Claude"
---

#7, 開發 MCPserver, 整合 Kernel Memory Service 與 Claude Desktop

今天沒有簡報了 (因為是全新的內容 XDD)，只有 demo 的螢幕截圖..

前面聊了很多 function calling 的應用，但是主要的 demo 方式都是透過 SK + Plugins. 實際上 LLM 的 function calling 能力有很多種不同管道都能使用的，按照不同的 LLM 應用程式來區分，有這些用法:

1. 透過 Chat GPT (plus):
我在部落格文章, 還有 DevOpsDays Taipei 2024 介紹的是用 GPTs + Custom Action ( 透過 OpenAPI Specs + OAuth )

2. 透過 No Code Platform:
我在 .NET Conf 2024 介紹的是用 Dify + Custom Tools ( 也是透過 OpenAPI Specs )

3. 透過 MCP Server 整合 Claude Desktop 等 MCP Client:
(這次會示範) 用 ModelContextProtocol 官方的 csharp-sdk, 將 MSKM 封裝成 MCPServer 使用

4. 自己 coding:
透過 Semantic Kernel 將 MSKM 掛上 Kernel, 讓 LLM 來驅動並且進行本地端的 (Native) Function Calling

這些方式，背後運作的流程其實都一樣。你都需要在一開始告知 LLM 有哪些 function 可以使用 (說明規格，參數)。而 LLM 在對話過程中會推論要完成任務需要依賴那些 function,  藉著回應這些 function calling 的要求跟取得的回應, 來逐步完成任務。而這些不同的工具跟手段，說穿了只是用不同的方式在跟 LLM 溝通而已。

攤開來看，每種方式都巧妙地提供了兩件事:

1. 告知 LLM 可用的 function specs
2. Host 能有統一的方式代替 LLM 來執行指定的 function 並回傳 function result

回頭看看, OpenAPI Spec ( swagger ), 不就是用靜態檔案 ( json / yaml ) 來做到第一件事嗎? 知道規格後寫個通用的 Http Client 來呼叫也不是難事。這種作法，Chat GPT, 跟 Semantic Kernel 都支援 ( SK 支援直接注入 Swagger ). 藉著這次機會，我也研究了一下 MCP 這標準規範，他用實體通訊協定的作法，規範了這些操作:

- initialize
- noticication
- tools/list, tools/invoke
- resources/list, ...
- prompts/list, ...

而這 protocol, 內建支援兩種通訊方式, 一個是 stdio, 另一個是 http ( based on SSE, server side event, 單向的串流機制 )。這樣的設計，讓你可以用任何語言, 任何平台, 任何通訊方式, 來跟 LLM 進行通訊。所以也有人說 MCP 就是 AI 的 USB-C 也不為過。

這次的主題，我最後就 demo 一下 MCP 官方的 csharp-sdk 來實作 MCPserver, 整合 Claude Desktop 跟 MSKM 來做 RAG 的應用... 不過，只要你要 live demo 就會有魔咒...  XDD, 這次的 demo 有兩個地方要注意:

1. MSKM 官方 docker image 請退版退到 0.96.x, 2025/02 release 的版本重寫過 chunking 的程式碼, 按照 token 將內容分段, 結果中文的部分沒處理好, 會變成 "晶晶體" XDD (會有疊字)。我已經發了 issue, 不過還沒解決掉...

2. MCP/csharp-sdk 也是, 回應的 json-rpc 包含中文的 json 資料, 直接讀取沒問題, 但是 Cloud Desktop 似乎無法很好的處理帶中文字的 json data, 必須將編碼轉為 \u1234\u1234 這樣的方式才能動... 同樣的我也發 issue 了，還沒解決。

因此這次 demo 我先自己 build sdk, 暫時手動換掉 JsonSerializationOption 後暫時能解決, 各位可以等官方 SDK 的修正... 搞定 MCPServer 後，我會用兩種方式展示:

1. 直接用 console + stdio 來操作 MCP server, 讓大家了解 json-rpc 通訊過程
2. 我也會真的拿 Claude Desktop 來示範, 實際使用 RAG 的感受

明天的直播，我就不再準備簡報了。我會直接搭配這七天的 PO 文，直接開 Visual Studio 給大家看 code, live demo, 讓大家實際體驗怎麼用 code 來讓 AI 幫你解決問題..

--
所以，這是最後一篇葉佩雯了 :D
實際 demo 跟 code 請參加明天 03/25 的直播
直播連結我放在第一則留言

![](/images/facebook-posts/facebook-posts-attachment-2025-03-24-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-03-24-001-002.png)
