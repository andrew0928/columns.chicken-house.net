---
layout: post
title: "Chat with My Blog #1, 內容服務化的設計(MCP)"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: 
---

這篇雖然是談 BLOG, 但其實寫文件都會碰到同樣的問題... 

過去這兩年, 我思考了好幾次這問題: "有了 AI 我還該不該自己手寫文章” ? 

如果是工作或是開發, 必須要寫符合規範的文件, 或是資料查詢 + 彙整等 "整理" 性質的內容，我會豪不考慮用 AI 輔助來完成... 但是寫自己的想法, 心得, 經驗分享的部落格文章, 尤其是其中包含過去沒有寫過的思考脈絡或想法時，這類內容我不會用 AI 來寫，因為這樣的話我總是覺得會少掉了一些關鍵的要素..., 遲遲沒有改變作法。

在更早沒有 AI 困擾的年代，我就想過, 要不要寫一些受歡迎的工具文? 後來發現我非常不適合這麼做，因為我碰的東西不夠多，就不是這塊料啊啊啊。同樣各種能 "速成" 或 "量產" 的形式，我發現都不適合我，我只能慢慢磨特定的主題，把背後的原因都挖出來漂亮的解決掉，並且分享其中的脈絡。因此最後，我還是維持一年只產出個位數的文章，但是每篇都是我真正覺得有價值的心得內容。

時至今日，我還蠻慶幸我當年有這樣決定的，沒有被流量追著跑而改變作法。我開始意識到 AI 也許能帶來一些改變, 但是改變的不是 "生產內容" 的方式, 而是擴大 "應用內容" 的方式。

我沒做過統計 (我也不知道怎麼統計 XDDD), 我相信我寫的主題應該有踩到很多人的痛點, 但是因為我寫的形式 (文章太長) 可能導致這些人壓根沒機會看到這些資訊... 但是要交代這些脈絡就是有這麼大的資訊量..., 資訊太少不足以形成完整的解決方案, 資訊太多則提高了接觸使用者的門檻, 平衡實在很難拿捏, 於是我開始想, 有能力掌握使用者意圖, 有能力處理文字訊息能力的 LLM, 也許會有解答。

於是, 背後一堆思考過程我先跳過, 後面再慢慢聊, 有興趣的自己看。我最終的答案就是, 我想弄一個我部落格的 mcp server, 來協助讀者們解決這些問題。我希望有個神奇的 mcp 可以讓大家從 "閱讀" 我的部落格文章，變成跟我的部落格 "聊天"，你的難題不再是自己讀完文章再動手處理, 而是透過你的 agent + mcp 來連結我的文章, 來完成你的期待 (不管是回答問題, 寫 code, 或是學習都一樣)。

標題 "Chat with My Blog!" 就是我想做的事情，而實現他的 MCP server, 現在有第一版可以給大家體驗看看了! 後面有示範的案例, 有興趣的可以繼續往下看。

<!--more-->

# TL;DR , 我該做什麼才能實現目標?


動機前言講過了, 接下來聊聊我到底做了什麼... 
上一次為我的部落格大改版, 已經是九年前的事情了 ( 2016/09, Blogging as Code ), 之後就沒有再大改版了, 當然也包含當時轉移系統藏了一堆沒處理的技術債...

這次改版我想做的, 就是 "讓我的部落格文章能充分被 AI agent 好好利用"，期待除了傳統的閱讀方式之外，還能有不同的應用型態。而這次的實現方式，我就訂在要提供我自己的 MCP server, 讓大家能直接在 vscode / chatGPT / Claude Desktop 等工具內, 直接對話我的部落格, 來解決他們的問題。

為了達成我的期待, 我把這次施工範圍分成三個目標:

1. **內容服務化**, 服務要能接上主流的 Agent ( 手段: MCP )  
關鍵是 mcp 該提供什麼樣的 tools 來輔助 agent 做好這情境。同時，我也重新調整了部落格的系統架構, 為了體驗一致性, 我希望原部落格網址加上 /api/mcp 就是對應的 mcp server endpoints, 動用了 Azure 上的服務 ( frontdoor + container apps ), 感謝 Microsoft 給 MVP 的使用額度 :D

2. **內容正規化**, 內容要預先轉換成易於使用的格式 ( 手段: LLM 生成新格式 )  
目前我的文章都有我自己的思路, 從情境 → 問題定義 → POC → 形成解決方案等過程。這是我認為最大化知識含量的做法，但是不適合最終的應用方式 (有的人立刻就需要答案了)。因此針對應用情境預先整理成合適的型態是必要的，這也是我花最多時間 & Token ($$$) 處理的環節, 再次感謝 MVP 的 Azure 使用額度 XD

3. **流程效率化**, 重新整理工作流程，清除技術債 ( 手段: AI IDE 重構 Repo )  
2016 年轉換到 GitHub Pages 時, 很多格式轉移的任務, 其實我都只做到 "可以動" 就好的地步，尤其是舊文章還有 70% 左右都還是 HTML, 圖檔連結壞了也沒有修正。這次為了能有效率的達成 (2), 藉助了 AI Agent + IDE 的幫助 ( 我用 GitHub Copilot ), 也順手把整個 GitHub repo 的內容都重構了一次，做好 (2) 有效率進行的工程基礎

每個目標，對我來說都是大工程啊啊啊啊, 也都各有不同的挑戰要克服。我寫下去一定是一大段，所以這裡先摘要一下，要達成這三個目標，每個目標背後的重點是甚麼:

(1) 用 MCP 來發布服務，關鍵在 Tools 的介面設計。

如果你只把 MCP 當成是 API 的另一種形式，只是把 REST API 重新改成 MCP 發行的話，那就大錯特錯了，這部分算是這次 side project 我最大的收穫，過程中我看了 MCP 團隊成員分享設計理念，也花了點時間研究 Shopify 的 MCP，才算掌握到一些設計的要訣。如果你把 Agent 當作真人看待，MCP 就是你跟他的溝通方式，最好的 MCP 設計，就是以 Agent 要解決問題時順著他的思考脈絡 ( context ) 給予最大的支持，想通這點，我才終於搞懂為何 MCP 會取名為 MCP ( Model Context Protocol )。這後面會有一段專門來談這主題。

(2) 將內容轉為應用的最合適的型態, 再做 RAG 的工程處理。

所有的服務中，怎麼 "應用" 永遠都是最重要的事情。如果你沒有對準 "應用" 的情境來挑選技術，那十之八九都會演變成 “為了技術而技術" 的窘境。我去年做過 "安德魯的部落格" GPTs, 當時就是無腦做 RAG，效果有了，但是還沒達到我的理想，感覺就是個書僮幫我找資料而已，還沒到能 "解決" 我的問題的程度。沒到這程度根本不夠格稱為 "Agent" 啊! 因此這次我的做法是對內容預先處理成 “合用" 的型態再進行 RAG (我三月直播談 Semantic Kernel 就示範過這想法了)。什麼叫 "合用” ? 你要先想清楚你要怎麼 "用”, 為了嘗試這些效果, 花了不少 token 來處理我的文章… 不過慶幸的是，這 token 花得很值得啊，這同樣會寫一段專門來談這主題。

(3) 善用 AI 工具來清理基礎結構的問題, 簡化整體的運作流程。

為了流程的效率化，把基礎結構打好是必要的 (不只寫 code, 即使是寫部落格也是如此)。文件的整理是必要的基礎，這影響到你有沒有能力對你的內容作各種後續應用。我的文章內容經過多次系統轉移 (九年前的文章有清楚記載這過程)，其實每次轉移都留下了一點技術債… 例如格式沒轉乾淨 (殘留 HTML 沒轉成 markdown, 殘留的 image 圖檔目錄沒有整理, 錯誤的連結沒有修正, 中文檔名導致各種編碼問題沒有處理…), 這些都是小問題, 睜一隻眼閉一隻眼就過去了, 但是當你希望內容有系統地被重新運用的時候, 這些狀況就都變成例外了。

我希望善用 AI 幫我處理內容，但是我也不希望把 token 花在這些鳥事身上啊! 雖然也是靠 AI 來處理，但是我選擇 "一次性" 的重構來搞定這些問題。我同時處理了 repo 的結構, 清理了不再需要的圖檔, 也把路徑跟驗證的環境 ( local run - github pages ) 通通都整理好了, 現在寫文章感覺舒暢多了, 這部分有很多實際操作的心得, 也包含 vibe coding, 這段我會當作心得分享的角度來寫。對實際操作或工作流程沒興趣的可以跳過這段。

好，簡介都寫完了，接下來就直接進入正題 (有三個主題)，來聊聊我這次的 side project - chat with my blog 吧~

—

# 1. 內容服務化 - 開發專屬的 MCP server

我啟動這 side project 的主要意圖, 就是想摸索 “部落格" 未來可能的應用模式。我的想像是 “部落格” 會更貼近資訊的來源，但不一定是資訊最終被應用 (閱讀) 的方式。舉例來說，傳統的模式就是我寫文章，到處分享連結，然後有興趣的人會點過來看，或是靠 search engine 來看到我的內容。不管管道為何，最終看到的內容，就是我寫的內容。

但是未來不見得再是這樣了，我的內容可能被:

1. 當作 AI 訓練的素材, 被應用的是模型的輸出
2. 被 search engine 挑出來, 但是最終變成 AI overview 的內容, 或是 AI agent 的輸出結果
3. 被 AI 摘要、彙整、生成其他形式 ( ex: 報告 )
4. 被 AI 當作知識的來源，或是 prompt / instruction 的一部分，生成 code 等其他型態輸出 ..

不過, 我能做什麼? (1) (2) 應該我管不了, 但是 (3) (4) 我應該有機會介入, 如果我知道 (或我想要) 大家都怎麼使用我的文章, 我也許可以主動提供更好的素材或工具來做這件事。也許 (3) (4) 再過幾年也變普及，我也管不了了，但是掌握的經驗是無價的，到時我也會更清楚資訊應該如何被運用才是有價值的。

因此，雖然最後的結論是很技術導向的 MCP server 開發, 但是我的目的很單純，就是內容的應用。我特地看了一下別人都怎麼引用我的文章的? 我特別留意了:

1. 分享我的 PO 文，但是有加上自己看法才 share 的人
2. 自己的部落格文章講述特定主題，會引用我的文章的人
3. 其他 SNS 的貼文，會特別 tag 我粉專的人
4. 其他實體演講等場合的問券回饋

在這些 "意圖很明確" 的回饋之間，大致上都有幾種模式:

1. 觀點啟發，我可能講了一些他們從未想過的可能性
2. 技術應用，原來 OOO 的東西可以這樣子做出來，原來我常用的 ZZZ 背後是這個原理
3. 經驗學習，碰到 XXX 的問題，原來需要這樣子解決才會到位，原來解 YYY 這問題能夠解的這麼漂亮

但是跟其他量產的部落客比，我的流量少的可憐啊 ( 雖然我也沒有很認真在拚這個 )，不過實際上很多 "需要" 這些資訊的人錯過了我的文章，總覺得我可以再努力點什麼.. 於是，我就開始想，我能多做點什麼，可以讓這些人更直接的應用我的心得跟經驗分享?

念頭就是這樣形成的，不只一個人對我的評價是: 很棒的觀點，很札實的內容，就是字太多了 (啊資訊量就是那麼多啊)，而我也堅持用這樣的形態來累積文章不想改變，因此…

> “  
> 那我用我最原始的想法來寫文章，讓 AI 生成大家需要的型態來應用就好了  
> ”

所以第一次公開這觀點，是今年三月的直播，我在介紹 Semantic Kernel + Microsoft Kernel Memory 應用的時候，我提出來的看法:


> “  
> 先把文章內容轉換成合適的視角，再進行 RAG 處理，檢索的成效會比直接無腦丟給 RAG 好的多  
> ”

我自己簡單嘗試了一下，的確效果很不錯，因此我就繼續往下一步:

> "  
> 我能否直接拿我的文章當基礎，加速其他文章 (文件) 的撰寫? (對應到: 觀點啟發)  
> "

接著...

> "  
> 我能否直接拿我的文章敘述到的情境，做法，流程等，當作 coding 的 instruction 加速寫出對應的   code ? (對應到: 技術應用)
> "

然後...

> "  
> 我能否直接拿我的文章要傳達的概念與精神，做學習，訓練的應用? 例如編排學習計畫，生成訓練素材，生成課前、課後的測驗? 設計 Labs 驗證學習成效? (對應到: 經驗學習)  
> "

這一連串思考 + 簡單的用 ChatGPT 驗證過後，感覺好像可行，而這些應用的整合環節，不約而同地都指向: 我需要開發一個我自己的 MCP server.. 因為寫文章 (我都用 vscode 寫 markdown, 可以用 github copilot agent mode), 寫 code 我也都用 vscode (同上), 其他的應用我更習慣用 Claude Desktop / ChatGPT 這類 AI chatbot, 如果我能不離開這些工具, 直接整合我的內容完成這些任務, 這就是我想要的理想運用情境。

於是，我就開始動工了，開始打造我自己部落格的 MCP server ( 因此，去年試做的 “安德魯的部落格" GPTs, 還有今年初用 Dify 建立的 Agent, 我都關掉了, 把資源集中在這個 side project 上 )。

上個月，我在 Facebook 分享了這個研討會的錄影: MCP 201, Code w/ Claude, 由 Anthrop/c 提出 MCP 規範的團隊成員現身說法, 描述了它們想像 MCP 的願景, 看完這 20min 的影片，我才算真正搞懂 MCP 要解決的問題, 於是我大概想清楚我該做甚麼了:

**MCP Tools**,  
用來檢索，取得特定條件的內容給 AI Agent, 變成 AI 的 context windows 之一，讓 Agent 生成最終的資訊給我

**MCP Resources**,  
用來取得文章本文，以及生成的內容 ( vscode 甚至可以直接開啟編輯 )

**MCP Prompts**,  
用來指引其他使用者，我應該最熟我的文章結構跟應用方式，與其教你怎麼下 prompt, 我可以透過 MCP 直接給你我預先寫好的 prompt


因此，經過幾版的嘗試與改進，我的 MCP 現在提供這些規格:

**Tools**:
- ```GetInstructions()```,  
給 AI 看得 MCP 使用說明書, 包含部分動態生成的資訊在內, 因此特地獨立成一個 tool
- ```GetPostContent(postid, synthesis, position, length)```,  
查詢指定文章 (須提供 postid) 的資訊
- ```GetRelatedPosts(postid, limit)```,  
查詢指定文章的相關文章清單 (須提供 postid)
- ```SearchChunks(query, synthesis, limit)```,  
按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文字片段
- ```SearchPosts(query, synthesis, limit)```,  
按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文章清單

**Resources**:
- ```posts://{id}.md```, (原始文章內容)
- ```posts://synthesis/{id}.summary.md``` (文章摘要, 適合用來做觀點啟發)
- ```posts://synthesis/{id}.faq.md``` (文章常見問答, 適合用來做名詞解釋等有明確答案的問題回應)
- ```posts://synthesis/{id}.solution.md``` (文章解決方案, 適合用來做技術應用方式說明, 無標準做法的問題解決方案引導)
- ```posts://synthesis/{id}.metadata.md``` (文章 metadata, 包含標籤, 分類, 發表日期等資訊)



# 2, MCP 的使用案例

看完規格, 我相信你還沒辦法想像 "這東西能幹嘛" 對吧? 接下來我花點篇幅, 拿幾個我自己應用這 MCP 的案例來示範用法。我相信用法絕對不只如此而已，如果你有其他不錯的使用方式，歡迎留言給我參考，當作我改善的依據

接下來，與其解釋所有的東西 ( tools, resources ) 怎麼設計, 我更想示範一下使用情境 XDD, 因此後面我就直接示範了, 關鍵設計要點我會提一下…



## 案例 1, 直接對話的應用

一開始先來入門的應用方式就好。我把 MCP 裝到 Claude Desktop 上面來使用。會挑 Claude Desktop, 因為他的使用門檻最低 (雖然會看我文章的人應該都有 AI coding agent 能用吧), 雖然他還不直接支援 http streamable MCP...。安裝方式先跳過, 確認安裝完成 + 已啟用必要的 tools 之後就可以開始跟他聊:

```
安德魯的部落格 您好,

開發分散式的系統, 想要時作微服務架構
面臨到跨服務的交易問題

身為開發人員，我有哪些基礎的底層知識需要具備?
```

Claude 看到關鍵字 "安德魯的部落格"，跟 tools description 上面敘述的一致, 就能聯想到要回答這些問題, 應該要來用我的 MCP tools 了。在回答我的過程中, AI 呼叫了兩次 tools:

GetInstructions, 不需要參數

SearchChunks, 帶了下列查詢要求:

```

{
  `limit`: 10,
  `query`: `分散式交易 distributed transaction saga 兩階段提交 2PC 微服務 跨服務交易`,
  `synthesis`: [
    `origin`,
    `solution`,
    `faq`
  ]
}

```

之後果然 AI 就給了我有模有樣的回應。結果有一大段，我就不全部貼出來了，我有全程錄影，有興趣的可以看這段 demo 錄影檔。我沒有一一去查核，但是看完之後都有印象，是我寫過的內容沒錯 (不過都不是一字不差，而是 AI 自己彙整過重寫的答案)。為了驗證 AI 是不是瞎掰，通常我會多下一個 prompt 來方便 review, 那就是叫 AI 把他給我的答案，跟實際上的參考資訊對照列出來:

```
上面這些主題, 出自安德魯的哪幾篇文章?
給我文章標題, 網址對照表
```

不管你用哪一家的模型，這樣做的效果都還不錯。這次輸出的對照結果如下:

```

根據剛才的搜尋結果，以下是相關主題在安德魯部落格的文章對照表：

## 分散式交易與 Saga Pattern

| 主題 | 文章標題 | 網址 |
|------|---------|------|
| Saga Pattern 實作 | 微服務架構設計 - Event Sourcing | https://columns.chicken-house.net/2020/01/01/microservice13-event-sourcing/ |
| 分散式交易處理 | 微服務架構設計 - 資料庫的選擇, RDBMS or NOSQL? | https://columns.chicken-house.net/2020/07/01/microservice14-database/ |
| 微服務轉移經驗 | 架構師觀點 - 轉移到微服務架構的經驗分享 (Part 3) | https://columns.chicken-house.net/2017/07/11/microservice8-case-study-p3/ |

## 交易正確性與一致性

| 主題 | 文章標題 | 網址 |
|------|---------|------|
| 線上交易正確性 | 架構面試題 #1, 線上交易的正確性 | https://columns.chicken-house.net/2018/03/25/interview01-transaction/ |

## 關於安德魯

| 主題 | 文章標題 | 網址 |
|------|---------|------|
| 背景介紹 | 安德魯是誰? | https://columns.chicken-house.net/2000/01/01/about-me/ |

這些文章涵蓋了：

1. **Saga Pattern 與補償交易** - 在 Event Sourcing 文章中詳細介紹了如何用 Saga 取代 2PC，包含實作範例
2. **Outbox Pattern** - 在資料庫選擇文章中說明了如何確保事件與資料變更的原子性
3. **分散式交易的 2PC 思維** - 在轉移經驗分享中解釋了傳統 2PC 的運作方式
4. **訊息順序與冪等性** - Event Sourcing 文章提到了使用 Kafka 的 Partition Key 保證順序
5. **CQRS 與讀寫分離** - 資料庫選擇文章討論了 Polyglot Persistence 策略

建議您可以從這幾篇文章開始深入閱讀，特別是 Event Sourcing 和資料庫選擇這兩篇，有較完整的解決方案與程式碼範例。

```

之後，我還出了題目 (我確定我沒寫過的主題 XDD)，就是訂票 (需要劃位) 類型的交易。這要鎖定控制的是每個座位的狀態，遠比單純鎖定交易金額，或是可賣數量的情境複雜得多。面對這種問題，AI 仍然能按照我文章的脈絡，用同樣原則，回答我沒有寫過的主題 (最後 AI 給了說明跟 PoC code)..

內容很長，我就貼我問的問題就好，其他輸出請看影片。我接著問了這段話:

```
我想從案例中學習這些 design concept 的運用
如果我的交易較複雜, 除了金額庫存等數據必須完全一致之外, 在演唱會購票的場景中, 甚至需要精確到特定的座位是否已經賣掉的問題

安德魯的哪幾篇文章有提到相關問題? 給我網址連結與相關的片段資訊

另外，我看過他文章都會用架構面試題，用很精準到位的 POC 來貫穿整個核心想法，能否用同樣方式給我一段 sample code 來說明分散式交易，處理演唱會購票的 POC ?
```

展示先到這邊為止，其實就 "chat with my blog" 的要求來說, 這結果其實很不錯啊, 某種程度來說你真的用 slack 來問我一樣的問題, 我的回答也就差不多是這樣而已 (要我真的現場寫一段 code 給你的話，我大概只會寫 psuedo code ...然後給你一堆參考連結讓你自己去看我寫過的東西)。



## 案例 2, 參考我的文章來 vibe coding

第一個拿 vibe coding 示範的案例，我就說明完整一點好了。我拿一篇我還挺自豪的文章當案例, 我曾經寫過一系列平行處理的文章, 也包含用 code 怎麼做好生產者消費者的控制。而講了那麼多，最經典的案例是用 pipeline 來實作, OS 的 stdio 跟 pipeline 幾乎都替你解掉絕大部分這些通訊問題, 剩下的部分簡單到在 shell script 用 pipeline 就能搞定的案例..

於是我打開 vscode, 建立了一個 console app, 除了預先給一個 UserItem 的 class 之外, 其他都沒給。這樣當作初始環境，安裝了我自己的 MCP server, 我給了 agent 這段要求:

```markdown
參考安德魯寫的 pipeline cli 文章
我要用他的技巧, 在 cli 用 stdio 接收 jsonl 當作輸入 (type: UserItem)

並且平行處理每一筆 json
請替我完成程式碼框架, 每一筆的處理動作我會自己填
```

總共花了大約 1 min, 程式碼就替我產生好了, 後面都是在補充 shell script ( 測試用 ), 以及產生驗證用的 jsonl file, 並且執行測試驗證結果的過程 (全部大約 5min), 錄影檔案跟最終的 repo 我放在最後面, 我把幾個關鍵的輸出貼上來。

我給 agent 的要求, 是從 stdio 接收 jsonl ( json line, 一行一筆 json, 可以包含多筆 )。而我期待的是接到一筆 (一行) 就開始處理一筆，在允許的狀況下 (有指定平行度上限) 盡可能的平行處理。外圍的 code 我就不貼了, 有興趣自己看 repo, 我貼主要處理邏輯:

```csharp
    static async Task ProcessDataInParallel(int parallelism)
    {
        // 使用 Channel 作為生產者-消費者模式的橋樑
        var channel = System.Threading.Channels.Channel.CreateBounded<UserItem>(100);
        var reader = channel.Reader;
        var writer = channel.Writer;

        // 生產者 Task - 從 STDIN 讀取 JSONL
        var producerTask = Task.Run(async () =>
        {
            try
            {
                await foreach (var item in ReadFromStdin())
                {
                    await writer.WriteAsync(item);
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine($"讀取資料時發生錯誤: {ex.Message}");
            }
            finally
            {
                writer.Complete();
            }
        });

        // 消費者 Tasks - 平行處理資料
        var consumerTasks = Enumerable.Range(0, parallelism)
            .Select(workerId => Task.Run(async () =>
            {
                await foreach (var item in reader.ReadAllAsync())
                {
                    try
                    {
                        // 處理每筆資料的地方 - 你可以在這裡填入具體的處理邏輯
                        var processedItem = await ProcessSingleItem(item, workerId);
                        
                        // 輸出處理結果到 STDOUT（JSON格式）
                        await OutputResult(processedItem);
                    }
                    catch (Exception ex)
                    {
                        Console.Error.WriteLine($"Worker {workerId} 處理資料 {item.Id} 時發生錯誤: {ex.Message}");
                        // 可以選擇跳過或重新處理
                    }
                }
            }))
            .ToArray();

        // 等待所有任務完成
        await Task.WhenAll(new[] { producerTask }.Concat(consumerTasks));
    }
```

前半段用 channel 物件來控制所有的任務, 並且開出一對 reader / writer 來操作 channel, 並且一開始就開了 async task, 盡可能地把 input 寫進 channel ( 背後的機制: 超過 channel 容量就會 blocked writer, 而容量空了就會 blocked reader, 這 channel 可以擔任生產者消費者的 buffer 來協調兩端的處理速度)

後段就單純的多, 按照宣告的平行處理上限 ( 沒指定就照 CPU 核心數 ), 開出指定個數的 worker, 來平行處理透過 reader 讀取任務來消化，直到通通結束為止。

接著來看看外面用了什麼樣的 shell script 來執行這段 code ?  首先, 為了方便測試, agent 替我生成了這樣的測試檔案 ( jsonl ):

```json
{"id": 1, "name": "Alice", "email": "alice@example.com", "created_at": "2024-01-01T10:00:00Z", "updated_at": "2024-01-01T10:00:00Z"}
{"id": 2, "name": "Bob", "email": "bob@example.com", "created_at": "2024-01-01T11:00:00Z", "updated_at": "2024-01-01T11:00:00Z"}
{"id": 3, "name": "Charlie", "email": "charlie@example.com", "created_at": "2024-01-01T12:00:00Z", "updated_at": "2024-01-01T12:00:00Z"}
{"id": 4, "name": "David", "email": "david@example.com", "created_at": "2024-01-01T13:00:00Z", "updated_at": "2024-01-01T13:00:00Z"}
{"id": 5, "name": "Eve", "email": "eve@example.com", "created_at": "2024-01-01T14:00:00Z", "updated_at": "2024-01-01T14:00:00Z"}
{"id": 6, "name": "Frank", "email": "frank@example.com", "created_at": "2024-01-01T15:00:00Z", "updated_at": "2024-01-01T15:00:00Z"}
{"id": 7, "name": "Grace", "email": "grace@example.com", "created_at": "2024-01-01T16:00:00Z", "updated_at": "2024-01-01T16:00:00Z"}
{"id": 8, "name": "Henry", "email": "henry@example.com", "created_at": "2024-01-01T17:00:00Z", "updated_at": "2024-01-01T17:00:00Z"}
{"id": 9, "name": "Iris", "email": "iris@example.com", "created_at": "2024-01-01T18:00:00Z", "updated_at": "2024-01-01T18:00:00Z"}
{"id": 10, "name": "Jack", "email": "jack@example.com", "created_at": "2024-01-01T19:00:00Z", "updated_at": "2024-01-01T19:00:00Z"}

```

看了一下，符合我在 source code 內指定的 json property name 的要求.. 接著來看 shell script, 其中有這麼一段指令:

```bash
# 範例 1: 基本用法
echo "=== 範例 1: 基本用法 (平行度 2) ==="
cat test-data.jsonl | dotnet run --project src/pipeline-cli/ -- 2 2>/dev/null | head -n 3
echo ""
```

用 cat 指令讀出 test-data.jsonl, 並且用 pipeline 轉發給這次主程式 pipeline-cli, 就驅動了整個我要求的程式碼結構。

案例示範到此為止，回頭看看，我總共輸入了哪些資訊?

1. 我對 agent 要求查詢 "安德魯的部落格" 提到的 pipeline-cli 文章
2. 我要求了我自訂的資料結構 UserItem
3. 我要求了程式碼的目的 ( 透過 stdin 接收，並且平行處理 )

而中間 MCP 其實幫我正確的找出相關內容。從對話紀錄可以看到 MCP 總共做了這些操作:

1. call: SearchPosts( query: "pipeline CLI stdio jsonl parallel processing” )
2. call: GetPostContent ( postid: "2019-06-15-netcli-pipeline”, synthesis: “solution” )
3. call: SearchChunks ( query: "stdio stdin Console.ReadLine IEnumerable yield JsonSerializer JSONL parallel processing async” )

AI agent 透過 MCP 拿到這三段資訊放入 context 後, 後面就都是 coding 輸出的部分了。我期待理想的結構就是這樣，如果我告訴一個新進工程師同樣的要求，他應該也會打開 google search 做類似的事情吧? 找文章, 然後看內容, 最後 find 相關的片段解讀後依照印象寫出程式碼.. 而我想清楚了這樣的期待，設計出對應的 Tools 介面，引導了 Agent 按照這流程完成任務。

從結果來看，的確有達到我期待的效果。用了很短的輸入，就能完成極大的產出。而這些產出背後的推手，是我過去累積的文章，留下的心得，歸納的原則，以及範例的程式碼。這些訊息通通匯集到 agent 對話的 context 內，才能創造出這樣的成果。

最後，再來看看 agent 產生的 README.md 吧.. 文件的最後面有這麼一段說明:

```markdown

## 架構特點

- **生產者-消費者模式**: 使用 `Channel<T>` 解耦讀取與處理
- **非同步串流**: 避免阻塞，提高吞吐量
- **資源友善**: 記憶體使用量穩定，適合大資料處理
- **Pipeline 友善**: 符合 Unix 哲學，易於組合

## 參考資料

- [後端工程師必備: CLI + PIPELINE 開發技巧](https://columns.chicken-house.net/2019/06/15/netcli-pipeline/)
- [CLI 傳遞物件的處理技巧](https://columns.chicken-house.net/2019/06/20/netcli-tips/)

```

其實技術細節都交代的蠻清楚的 (廢話，都照著我文章的提示寫的)，更重要的是兩篇直接相關的文章，也很精準的附上參考連結。如果每個讀我文章的人最後都能這樣使用的話，我應該可以在各大 GitHub Repo 看到有文件參考我的部落格才對 XDDD, 我期待的是我寫的內容真正對大家有幫助，而這參考註記只是個證明而已。

## 案例 3, 寫文章時引用我的觀點

接續上一個案例 (這是連續的操作): Code 寫完，我想補上一份說明程式碼架構的文件，於是我接續 agent 的對話，給了他這段要求:

```markdown
從安德魯的文章中，摘要這段程式碼用到的技巧
寫在 #file:ARCH.md 內

直接引用的部分, 請用 > ( quot ) 的方式來呈現, 並且務必附上原始網址
如果是引用後你重新寫的說明則不需要 quot, 但是請仍需要在段落最後，或是整份文件最後標記參考來源。
```

看起來，前面透過 MCP 查詢的內容還留在 context 內，這次寫文件就沒有再查詢一次了，所以沒看到 MCP 的調用紀錄。而按照要求，Agent 替我寫了這段敘述 (內容太長，我只截錄片段):

```markdown

# Pipeline CLI 架構說明

本專案基於安德魯「CLI + PIPELINE 開發技巧」文章的設計理念，實現了一個高效的串流資料處理框架。

## 核心設計理念

### 串流處理優於批次處理

> 任何串流處理的原則都一樣，你要預期你的資料筆數是無限大，從頭到尾每個環節都需要接受這種處理模式 (接收一部份，處理一部份，輸出一部份)。

本程式採用 `IAsyncEnumerable` 實現真正的串流處理，避免了批次處理可能造成的記憶體暴增問題。每筆資料讀取後立即進入處理流程，而非等待全部載入。

### STDIN/STDOUT 作為 Stream 處理

> 以 .NET 的觀點來看，STDIN / STDOUT 其實是 Stream 層級的東西啊，不是 TextReader / TextWriter 層級的東西...，因此你其實可以拿來處理 binary data 的。

程式將標準輸入輸出視為資料流，而非單純的文字介面：
- 使用 `Console.OpenStandardInput()` 直接操作 Stream
- 支援二進位資料傳遞（透過 JSON 序列化）
- 資料與日誌分離：資料走 STDOUT，日誌走 STDERR

### JSONL 格式的串流友善性

> 我刻意一筆物件就輸出一次 JSON, 最上層不用物件或是陣列包起來, 我不希望下一關要完整的 parsing 所有的 data 才能使用。

採用 JSONL (JSON Lines) 格式實現逐行處理：

// 輸出端：每筆資料一行
json.Serialize(Console.Out, model);
Console.Out.WriteLine();

// 接收端：逐行反序列化
while ((line = await reader.ReadLineAsync()) != null)
{
    var item = JsonSerializer.Deserialize<UserItem>(line);
}

---

## 參考來源

- [後端工程師必備: CLI + PIPELINE 開發技巧](https://columns.chicken-house.net/2019/06/15/netcli-pipeline/)
- [後端工程師必備: CLI 傳遞物件的處理技巧](https://columns.chicken-house.net/2019/06/20/netcli-tips/)

```

內容長了點, 不過我仔細一行一行的看過，我會給他這些評價:

1. 真的有按照我要求, 一字不漏的引用我文章時有把原文 quot 起來, 符合期待
2. 我原文其實沒有用到 IAsyncEnumerable ( 2019 那個年代我只會用 IEnumerable ...  XDD ), 而 AI 生成的 code 有, 而且他也有特別說明, 這算是超出期待的部分
3. 細節都有掌握到, 例如 JSONL 一次讀一行就立即處理一筆, 程式碼有照做, 文件也有說明, 產生的範例也正確
4. 生產者消費者的機制，我文章用的是古老的 BlockingCollection, 而 AI agent 替我換成較現代的機制 Channel 替代, 文件內也有說明
5. 其餘生成的 code 背後的意圖 ( 包含策略，特性等等 ) 也都有說明到位
6. 應用的方式也補充了 Unix 使用 pipeline 的慣例，這些都是正確且超出我原本文章範圍的資訊



## 案例 4, 直接替我整理部落格的演進史

寫這篇文章的時候，我就回想到九年前寫 Blog as Code 這篇文章時, 當時我花了一番功夫, 才把我歷年來對部落格做過幾次改造的內容整理好，才有這些內容。

本來，這篇我還要再來一次的，不過想想，這不就是 AI 最擅長的嗎? 於是我特地等 MCP 都上線了才來寫這段，以下內容主要是資訊整理，不包含太多觀點或心得，我就放心交給 AI 處理了。

我想要按照時間，把我過去提及的部落格系統改版的重點摘要列出來。系統更換標上年份，該系統的客製化調整當作子項目..., 於是我在 github copilot 的 agent mode 下，給了他這段要求:

```markdown

請幫我填上這段 markdown 區段
幫我整理 "安德魯的部落格" 歷年來移轉系統的記錄當作主要項目清單

每個系統安德魯自己做過的客製化項目摘要當作子項目

按照時間順序排序, 每個項目敘述請控制在 100 字以內，同時附上參考文章標題 + 連結。用下列格式提供:

(2004) 自行開發 .NET Forum

新增 RBAC 權限控制機制
新增 RBAC 權限控制機制
新增 RBAC 權限控制機制
參考文章: [article title here](article url here)
(2005) 系統移轉: 改用 .TEXT
(2005) 系統移轉: 改用 Community Server

```


而以下結果, 則是 agent + mcp 替我完成的內容:

--

(2002) 自行開發 .NET Forum/Blog 系統
- 使用 ASP.NET 1.1 土炮開發的部落格系統
- 實作基本的文章發布與管理功能
- 整合 Forum 討論區功能
- 參考文章: [關於安德魯](https://columns.chicken-house.net/2000/01/01/about-me/)

(2005) 系統移轉: 改用 .TEXT
- 從自製系統轉移到 .TEXT 引擎
- 採用 FreeTextBox 作為編輯器
- 新增圖片上傳與管理功能
- 參考文章: [.Text Upgrade](https://columns.chicken-house.net/2005/03/18/text-upgrade/)

(2005) 系統移轉: 改用 Community Server 1.0
- .TEXT 作者與 ASPNET Forum、nGallery 合併成 Community Server
- 整合 Blog、Forum、Gallery 三合一功能
- 新增會員管理與權限控制機制
- 參考文章: [Community Server](https://columns.chicken-house.net/2005/02/12/community-server/)

(2005-2006) Community Server 大幅客製化改造
- 改進 TextEditor Wrapper，啟用 FreeTextBox 3.0 進階編輯功能
- 新增表情符號插入工具列
- 開發批次上傳相片功能與 Web Service API
- 客製化首頁與 Blog 版面配置
- 開發 Recent Comments 顯示控制項
- 參考文章: [community server 改造工程](https://columns.chicken-house.net/2005/04/04/community-server-customization-project/)

(2006) 系統升級: Community Server 2.0 Beta 3
- 因 64 位元 Windows 相容性問題被迫升級
- 解決 ASP.NET 1.1 與 2.0 在 64 位元系統的執行問題
- 暫時犧牲之前的客製化功能以使用官方版本
- 參考文章: [換新系統了!! CS 2.0 Beta 3](https://columns.chicken-house.net/2006/02/03/community-server-2-0-beta-3-upgrade/)

(2007) 系統升級: Community Server 2007
- 升級到 ASP.NET 2.0 標準架構 (Master Page + Config)
- 改用 Provider Model 資料存取方式
- 將自訂 User Control 改寫為 .ascx + .cs 形式
- 簡化部署流程
- 參考文章: [偷偷升級到 CS2007](https://columns.chicken-house.net/2007/05/05/secretly-upgraded-to-cs2007/)

(2008) 系統移轉: 改用 BlogEngine.NET
- 因 Community Server 商業化限制決定轉移
- 採用 BlogML 格式進行資料轉移
- 解決圖片連結、站內連結、站外連結等轉址問題
- 開發自訂匯入程式補齊缺漏資料
- 新增 View Count Extension 與 Secure Post Extension
- 參考文章: [換到 BlogEngine.Net 了!](https://columns.chicken-house.net/2008/06/17/switched-to-blogengine-net/)

(2008-2015) BlogEngine.NET 客製化與擴充
- 開發 Secure Post Extension (密碼保護文章)
- 整合 Google Ads 廣告系統
- 整合 FunP 推推王社交分享功能
- 開發 PostViewCounter Extension
- 客製化版面設計與 CSS 調整
- 參考文章: [BlogEngine Extension: Secure Post v1.0](https://columns.chicken-house.net/2008/09/06/blogengine-extension-secure-post-v1-0/)

(2015) 短期嘗試: WordPress
- 測試 WordPress 作為替代方案
- 處理大量舊網址轉址問題 (Apache RewriteMap)
- 因維護成本考量最終放棄
- 參考文章: [Case Study: BlogEngine -> WordPress 大量(舊)網址轉址問題處理](https://columns.chicken-house.net/2015/11/06/apache-rewritemap-urlmapping-case-study/)

(2016) 系統移轉: 改用 Jekyll + GitHub Pages
- 採用最低科技路線，改用靜態檔案
- 選擇 GitHub Pages 作為 Hosting 方式
- 實現 "Blogging as Code" 概念
- 大幅降低維護成本與系統複雜度
- 改用 Markdown 撰寫文章
- 參考文章: [Blogging as code !!](https://columns.chicken-house.net/2016/09/16/blog-as-code/)

--

其實還蠻完整正確的啊 XDD, 自己寫部落格, 其實最頭痛的就是問題整理。九年前為了寫這些文章，我自己本機其實很難處理，最後我是用 google search, 找我公開的部落格文章, 找到相關資訊後好後再逐步編輯變成最後的內容。

即使用上 google search, 也只是省去 "找到" 資訊的功夫, 彙整摘要仍然是手動。有時候連我自己都在傷腦筋，怎麼當年寫這麼多字? 害我現在好難整理.. (咦?) 不過這些動作，不就是 AI 最擅長，而且最可靠的部分嗎? 當然要好好利用一下。

現在我看到科技的進步了，生成式 AI 在處理文字資訊上真的是不同世代的技術，過去要花一個晚上的事情，現在兩三分鐘就能完成。


## 案例 5, 直接取得文章內容 (resources)

有時候 AI 輸出的東西也會看膩的 (咦?)，有時候就是想直接拿到原始內容就好。透過部落格可能是個好方式，但是如果我操作的不是瀏覽器 而是 IDE，透過 MCP 可能是另一個整合度更高的作法。

// demo: home

## 案例 6, 生成訓練計畫, 測驗題 ( Quiz ), 實作題 ( Hands On Labs )

// demo: home


## 案例小結



# 3, MCP 的設計

看完整個部落格的服務方式想像，也看完這些事情做好後能運用的情境，現在可以回過頭來看看這樣的 MCP 是怎麼被設計出來的了。這邊我大推 iHower 的電子報, 還有他的粉專, 如果你沒時間去追一堆第一手資料來源, 那看他的整理就對了, 很多 Agentic 的設計理念, MCP 的發展資訊, 我都是從這邊找到對我有用的第一手資訊。

前年年底我在談 "安德魯小舖" 的時候，當時我談的是 API 的設計是否對 AI 友善? 所謂的 "友善"，談的是以後 API 是讓 AI 呼叫的，你的設計是不是簡單易懂? 你的 API 設計是否夠穩固可靠，即使 AI 用了錯的方式呼叫，你都能阻止他做錯事等等...

(有開發這個 MCP 實在是太棒了, 以下這段由 github copilot + 安德魯的部落格 mcp 聯合提供, 這些 prompt 我應該要收錄進 prompts / copilot-instructions.md 才對)


以下是我過去兩年談論相關問題的摘要:

--

**參考來源**:

**1. API 設計的兩大核心要求（「從 API First 到 AI First」）**

> 「如果你要認真為了下個世代的基礎做準備，請好好看待你的 API。有兩個面向一定要注意：
> 
> 1. **做到合情合理**: 做到你的 API 規格讓 AI 一看就懂 ( LLM 都是由一堆 "常理" 訓練出來的，你設計邏輯越符合 "常理" 越不會出錯)。
> 
> 1. **做到足夠 "可靠"**: 做到 API 即使被胡亂呼叫，該守住的邊界一定要守住，要做到不容許有任何例外的狀況 (難保你不會被 AI 找到漏洞)。」

**來源**：[從 API First 到 AI First](/2024/07/20/devopsdays-keynote/)

**2. API 必須精準對應領域問題（「開發人員該如何看待 AI 帶來的改變」）**

> 「**架構師必須清楚，API 該如何對應領域的問題，用統一並解精準的設計開放服務介面，掛上 LLM 的擴充機制**... 因為，掛上 LLM 後的 API ( Plugins ), 呼叫你 API 的不再是其他開發者了, 會變成 AI 來呼叫你的 API。你已經無法 "預測" 或是 "約束" 對方該怎麼呼叫。這時你只剩兩條路可以選擇，一個是把你的 API 設計的合情合理，完全符合現實世界的運作邏輯... 另一個就是把你的 API 做到邏輯無懈可擊，滴水不漏。」

**來源**：[開發人員該如何看待 AI 帶來的改變](/2024/01/15/archview-llm/)

**3. 避免檯面下溝通與 UI 導向的壞習慣（「從 API First 到 AI First」）**

> 「第一個壞習慣, **"檯面下的溝通"**... 再來，**"API 設計過度向目前的使用案例偏斜"**: 典型的就是 UI 跟 API 的戰爭... API 該做的是把你的 domain service 用 API 型態開放出來，而不是把你現在的 Application UI 能做的事情開放出來。兩者不完全重疊，但是沒分清楚就足以讓你的 API 完全沒達到他該發揮的效益... 這些壞習慣，其實都建立在用 "檯面下的溝通" 來迴避設計或架構問題。我要很直接地告訴各位，這些做法在 AI 都行不通。」

**來源**：[從 API First 到 AI First](/2024/07/20/devopsdays-keynote/)

--

當時我還沒辦法講得很清楚 (當時連要做出來都有點困難了 XDD)，不過現在對照這些大師們歸納的原則，再回頭對照著看我當時寫的敘述，其實我都踩在對的軌道上啊，果然這些累積都沒有浪費。當時我都還把關注點擺在: 如何設計對 AI 友善的 API (當時我心裡想的還是 API), 而現在 MCP 出現了, MCP (尤其是 tools) 不必要再跟 API 畫上等號, 兩者可以正式脫鉤了 (當然你要做那種套 API 殼的 MCP 也不是不行, 沒必要而已)。現在的原則是: 

> "  
> 別從 API 端點開始設計，而是從工作流程來設計 ( MCP )
> "

有興趣的可以參考這段:
- [iHower 電子報 #31](https://ihower.tw/blog/13197-aie-openai-gpt-5)
- 原始文章 - [Block's Playbook for Designing MCP Servers](https://engineering.block.xyz/blog/blocks-playbook-for-designing-mcp-servers)

文章導讀跟介紹我就不寫在這邊了, 我在 FB 也 PO 了一篇讀書心得。這邊我直接針對部落格的 MCP 設計來探討: 何謂 "使用部落格的工作流程" ??

前面有提到，我設想過大家會怎麼使用我的部落格? 不外乎:

- 訂閱, 當作雜誌來看, 我寫什麼就看什麼。這個現在就做得很好了，不大需要額外處理。
- 新知, 有特定問題 ( question ) 時想要來我部落格找相關資訊。例如幾個我長期關注的主題, 像是分散式系統、平行處理、微服務架構、AI 應用開發等主題, 有時只有模糊的印象, 想要來我這邊找到明確且專業的說明
- 解題, 有特定的難題 ( problem ), 想要來我的部落格找找有無合適的解決方案。例如我常常寫的架構師觀點，或是架構面試題就屬於這類。我都會定義常見但是很棘手的情境，然後分析背後關鍵因素，並且提供範例跟整個開發過程來示範如何解題。
- 學習, 想要學習怎樣才能當個架構師，想要學好特定的主題，或是某個特定的技術或是概念, 例如我寫過一系列的 .NET CLI + Pipeline 的文章, 以及平行處理的文章, 這些都是針對特定技術的學習內容

而我先前也常常比喻，我現在都把 AI 當作 "真人" 看待，因此很多工作流程的設計，我會先思考 "如果是真人會怎麼做" ? 而 AI，我只是把這些工作流程寫進 Prompt 而已。我就拿 "解題" 當作案例吧，同時拿一篇我覺得經典的文章來示範:

"排程處理", 這是我實際在工作上碰到的問題。假設時間回溯再來一次，我還不懂這題怎麼解，而當時有懂得這技巧的前輩在身邊，那我會怎麼做?

首先，我一定會先了解這前輩的工作習性，喜好，以及他的專長等等 ( GetInstructions )。簡單的說我會先了解怎麼跟他溝通。如果有人寫好 "如何好好運用前輩" 的使用說明書，那就太好了。其實這不是我瞎掰的，當年在做 HR 系統，就有這樣的概念, 工作說明書 ( Job Description ), 職能說明 ( Competency ) 等等, 這些都是在描述一個角色該怎麼工作, 以及該怎麼被運用。

接下來，我應該不夠專業，因此我只能敘述 (query) 我碰到的問題。若再完整一點，我會多敘述一些我碰到的問題的背景 (context)。我期待這位前輩，能給我一些指點 ( Search Chunks ) ，任何相關的資訊，即使只有片段 ( chunks ) 也可以，對我來說都可能是能救命的浮木。

有了線索之後，我會期待逐步找到原始的第一手資訊。前輩有自己的筆記跟知識庫的話 (部落格?)，能給我 (GetPostDetails) 原始的文章資訊 (PostId, Metadata) 就再好不過了。有了文章連結，我也會希望多看看有沒有類似主題，或是相關的其他文章等 (GetRelatedPosts)。

--

當我對問題已經有眉目了，代表我對問題的脈絡 ( context ) 已經有所掌握，接下來就可以真正來解決我的問題 ( problem ) 了。我生再有 AI coding 工具的年代, 我只需要跟 coding agent 說明清楚我的需求, 我要的結果, 更重要的是處理的問題脈絡 ( context ) 的第一手資訊都來自前輩的提點, 上面那些資訊都應該當作我給 coding agent 的參考資訊 ( add context ) 才對, 於是 coding agent 就能幫我完成任務。

( 接下來就是一連串 coding agent 的使用技巧跟操作過程了，略過 )

以上，就是一連串的 "工作流程" 啊! 跟這位前輩的互動過程中，我在敘述中都標記了一些關鍵字，這些都是互動過程中要執行的 "動作"，或是要取得運用的 "資源"。而這位前輩，如果是個知識庫，並且有個對應的 MCP 能夠提供這些動作跟資源，那我就能順利地完成我的任務了。

因此，我重新貼一段前面提及的 MCP 設計規格 (再貼一次):


**Tools**:
- ```GetInstructions()```,  
給 AI 看得 MCP 使用說明書, 包含部分動態生成的資訊在內, 因此特地獨立成一個 tool
- ```GetPostContent(postid, synthesis, position, length)```,  
查詢指定文章 (須提供 postid) 的資訊
- ```GetRelatedPosts(postid, limit)```,  
查詢指定文章的相關文章清單 (須提供 postid)
- ```SearchChunks(query, synthesis, limit)```,  
按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文字片段
- ```SearchPosts(query, synthesis, limit)```,  
按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文章清單

**Resources**:
- ```posts://{id}.md```, (原始文章內容)
- ```posts://synthesis/{id}.summary.md``` (文章摘要, 適合用來做觀點啟發)
- ```posts://synthesis/{id}.faq.md``` (文章常見問答, 適合用來做名詞解釋等有明確答案的問題回應)
- ```posts://synthesis/{id}.solution.md``` (文章解決方案, 適合用來做技術應用方式說明, 無標準做法的問題解決方案引導)
- ```posts://synthesis/{id}.metadata.md``` (文章 metadata, 包含標籤, 分類, 發表日期等資訊)

這不就是原封不動的把我想像的工作流程，跟擬人化的 "前輩" 互動過程，實際透過 MCP 的銜接，讓我想像的情境能真實發生在現在已經可以使用的 AI Agent 了嗎?

這的確就是我第一版 MCP 運作中的規格。有興趣的人不要只是安裝我的 MCP server 直接使用, 你也可以用 MCP 官方的 MCP 測試工具 - @modelcontextprotocol/inspector 來實際測試一下 MCP server, 你會更清楚的掌握他背後做了什麼事情。

// 圖: MCP inspactor

所以，有了基本概念後，我推薦大家可以來看這段影片，他很清楚的交代了 MCP 為何會設計出這些協定?

Anthropic 今年 (2025/05/22) 的研討會 - Code w/ Claude, MCP201 這場, 短短的 25min 影片, 值得一聽。你很少有機會看到第一手資訊 (講者就是 MCP 團隊的一員)。

如果你覺得內容太硬了，我在 Facebook 也有貼了一則心得評論:







## MCP 應用的想像

## Tools

## Resources

## Prompts


<!-- 
# 2. 內容正規化 - 生成特定格式的內容

# 3. 流程效率化 - 流程優化, 清除文件的技術債

# 結論 -->