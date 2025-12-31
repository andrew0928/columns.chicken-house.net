---
date: 2025-09-24
datetime: 2025-09-24T19:30:05+08:00
timestamp_utc: 1758713405
title: "先前談到 MCP 的設計, 有提到 Shopify 的 MCP 設計的很有巧思… 正好昨天寫完一篇把"
---

先前談到 MCP 的設計, 有提到 Shopify 的 MCP 設計的很有巧思… 正好昨天寫完一篇把我部落格轉成 MCP 的文章, 就順手把這題也分享一下..

會研究 Shopify 的 MCP, 起因是我在研究 MCP 的設計, 正好參考到 Shopify.Dev MCP 的做法。Shopify 是個電商的平台, 在他的平台上也衍生了很多開發套件，包含 API, 包含 GraphQL, 包含他自己的前端套件, 甚至有自己的 Shopify Functions ( 類似 Azure Function, AWS Lambda )..

各位可以想像, 發展出這麼多體系的 Shopify, 他需要多大規模的知識庫才能支撐起這樣的開發者生態系。而吸引我目光的是, Shopify 能把這整個 Site 濃縮成一個只有 5 個 tools 的 MCP, 讓你把整個開發資源者和進你的 Coding Agent .. 而且意外的是, 效果還不錯。

我覺得最厲害的, 是 Shopify 的做法, 對 Developer / Coding Agent 的工作流程掌握很精準，MCP 就完全貼著這流程設計。我這邊就摘要一下就好，有興趣的可以直接看我文章的這個段落 (**# 4, 參考 Shopify / Context7 的 MCP 設計**)

歸納起來，我覺得 Shopify 作對三件事:

❶ 流程管控的很好:
所有的動作都要先從 call: learning_shopify_api 這個 tool 開始。這個 tool 會回應對應的 instructions, 同時給你一個 conversation id, 其他的 tool 都要認這 id 才會給結果。意思就是強迫 Agent "使用前請詳閱公開說明書" 的意思。而這 id 就是閱讀過 ( instruction 已經被放進 context window ) 的證明

❷ Context 管理得很好:
存取文件的動作拆解成兩段來執行, 一段是 call: search_docs_chunks 從 query → 取得符合的文件片段 ( chunks ), 另一段則是靠 call: fetch_full_docs, 靠找到的 id 來取得完整的文件內容。這種作法比起暴力 RAG , 對 context window 的使用精準的多, 不會有多餘不必要的資訊塞爆有限的 context window.

❸ 開發流程掌控得很好:
尤其是在輔助 developer 寫出正確的 GraphQL. 不知道大家有沒有寫過 GQL? 寫這個對我來說很痛苦 XDDD, 雖然目前 LLM 都有能力寫出七分像的 GraphQL 了，不過要是 LLM 給的不對，你也沒辦法改了，只能叫他重寫。Shopify 採取了另一個做法，把寫 GraphQL 的動作再拆解，並且提供 tools 支援，輔助 Agent 一次寫對。這兩個 tools 就是為此而生: introspect_graphql_schema, validate_graphql_codeblocks。一個在事前, 先替 Agent 決定好傳回結果的 schema 應該長怎樣 ( Shopify 自己最清楚他的 data schema 了吧 )，另一個在事後替 Agent 驗證整個 Query 的語法是否真正卻。如何驗證我無從得知，不過我相信 Shopify 一定是最有能力做好這件事的人吧?

看到 Shopify 這樣拆解工作流程，變成 MCP Tools 的設計，令我大開眼界。看到這邊我才算搞懂 MCP 要按照 Workflow 來設計的精神。

看不過癮的話, 其實 Shopify 還有另一個也是做得很棒的 MCP: Shopify Storefront MCP, 那是另一個領域 (購物) 的用途了, 拆解他的設計也是相當精彩，這個我另外再找機會分享。

這些心得，是看完很多文章跟親自實驗湊起來才得到的，有興趣的可以參考，我把我的文章，還有讀過的參考資訊，都放在留言內

![](/images/facebook-posts/facebook-posts-attachment-2025-09-24-001-001.png)
