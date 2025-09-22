---
layout: post
title: "Chat with My Blog #1, 內容服務化的 MCP 設計"
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

時隔[九年](), 我 "又" 想為我的部落格做一些改變了。這次不是換系統, 而是想換一下內容的使用方式。AI 改變了很多事情, 但是對於部落格來說, 最大的改變就是文字的處理與理解能力了。我想試試看未來的部落格會變成什麼樣子? 於是就捲起袖子自己嘗試看看。

也因此, 這個 side project 花了我兩三個月的空閒時間嘗試 & 思考, 有些內容我想記錄下來。我想分兩篇來寫這些心得:

- (第一篇, 就是這篇文章) 談 Agent 時代, 軟體服務的設計與使用方式的改變, 以及可能的應用案例
- (第二篇) 談工程上的做法, 包含內容的預先處理, 原本部落格的重構, 工作流程的改善等

雖然我拿我的部落格當例子, 不過我覺得文件類型的應用, 其實都有同樣的問題。最初有這念頭，我最早想的是:

"以後有了 AI, 我還該不該自己手寫文章 ? 尤其是這種花時間的長文 ? ”

<!--more-->

最後我的答案是 "當然要!"

不過，重點跟使用技巧應該都會有變化了。AI 改變大家的使用習慣，因此像 stackoverflow.com 這種網站, 這兩年的流量腰斬, 大家不再到上面問問題, 也不到上面找答案了, 因為上面匯聚的內容已經高度被 AI 替代。AI 時代需要的是有獨特價值 & 見解的內容，並且能被 AI 妥善運用的內容。我這次的 side project 就是要做這件事, 如果做得到, 那我應該不用擔心以後沒人看我的部落格 (咦? 。過去最多的 feedback, 就是很多人跟我抱怨過我文章太長看不完 (XDD)，我覺得重點不是文章長度, 而是從 "看完" 文章，到消化理解我的想法，再到實戰 & 問題解決，這過程太長了。我想善用 AI 來縮短這過程。

如果我能準備一個我部落格的代理人，直接找他聊天，若這樣能順利解決你的問題，能用我的文章完成你的 code，那 AI 等於大大提升我文章的附加價值了。這時你就可以 "Chat with My Blog!" ，這就是我這次改版想要嘗試的。


於是, 背後一堆思考過程我先跳過, 後面再慢慢聊。我最終的答案就是, 我想弄一個我部落格的 mcp server, 同時好好的把我的文章整理一下, 發布時就做好各種內容的處理, 做好 RAG 這件事, 來協助讀者們解決這些問題。我希望有個神奇的 mcp 能掛上大家自己的 AI agent ( ex: ChatGPT ), 大家就可以從 "閱讀" 我的部落格文章，變成跟我的部落格 "聊天"，你的難題不再是自己讀完文章再動手處理, 而是透過你的 agent + mcp 來連結我的文章, 來完成你的任務 (不管是回答問題, 寫 code, 或是學習都一樣)。

這就是我想做的事情，而實現他的 MCP server, 現在有第一版可以給大家體驗看看了! 後面有示範的案例, 有興趣的可以繼續往下看。







# TL;DR , 我該做什麼才能實現目標?

動機前面講過了, 接下來聊聊我到底做了什麼... 

上一次為我的部落格大改版, 已經是九年前的事情了 ( 2016/09, Blogging as Code ), 之後就沒有再大改版了, 當然也包含當時轉移系統藏了一堆沒處理的技術債...

這次改版我想做的, 首要目標就是 "讓我的部落格文章能充分被 AI agent 好好利用"，這是所有 AI 應用的基礎，而其中的關鍵就是要做好 RAG，要正確找出對的內容不是件容易的事啊，這邊花掉我最多的研究時間。為了達成我的期待, 我把這次施工範圍分成三個目標:

1. **內容服務化**, 服務要能用主流的型態接上 Agent ( 手段: MCP )  
關鍵是 mcp 該提供什麼樣的 tools 來輔助 agent 做好這情境。同時，我也重新調整了部落格的系統架構, 為了體驗一致性, 我希望原部落格網址加上 /api/mcp 就是對應的 mcp server endpoints, 動用了 Azure 上的服務 ( frontdoor + container apps ), 感謝 Microsoft 給 MVP 的使用額度 :D

2. **內容正規化**, 內容要預先轉換成易於使用的格式 ( 手段: LLM 預先生成 )  
目前我的文章都有我自己的思路, 從情境 → 問題定義 → POC → 形成解決方案等過程。而這種有思路順序的長文章，是非常不適合用 RAG 處理的，因為切斷後的內容 ( max: 8kb ) 都不是個完整的主題, 被檢索出來無法有效應用, 效果就不理想。我認為理想的做法是: 先用 LLM 精煉這些內容，轉成適合被 RAG 應用的型態，再作後續處理。最花時間跟最花錢 (token) 的就屬這部份了, 再次感謝 MVP 的 Azure 使用額度 XD

3. **流程效率化**, 重新整理工作流程，清除技術債 ( 手段: AI IDE 重構 Repo )  
2016 年轉換到 GitHub Pages 時, 很多格式轉移的任務, 其實我都只做到 "可以動" 就好的地步，尤其是舊文章還有 70% 左右都還是 HTML, 圖檔連結壞了也沒有修正。這次為了能有效率的達成 (2), 藉助了 AI Agent + IDE 的幫助 ( 我用 GitHub Copilot ), 也順手把整個 GitHub repo 的內容都重構了一次，做好 (2) 有效率進行的工程基礎。

每個目標，對我來說都是大工程啊啊啊啊, 也都各有不同的挑戰要克服。我寫下去一定是一大段，所以這裡先摘要一下，要達成這三個目標，每個目標背後的重點是甚麼:

**(1) 用 MCP 來發布服務，關鍵在 Tools 的介面設計**

MCP 並不是 API, 如果只是把 REST API 包裝成 MCP 的話，那就大錯特錯了。特地為了 Agent 來設計 MCP 是最理想的做法, 這也是我這次 side project 最大的收穫。我看了 MCP 團隊成員分享設計理念，也花了點時間研究 Shopify 的 MCP，才算掌握到一些設計的要訣。最好的 MCP 設計，就是以 Agent 要解決問題時順著他的思考脈絡 ( context ) 給予最大的支持，想通這點，我才終於搞懂為何 MCP 會取名為 MCP ( Model Context Protocol )。這後面會有一段專門來談這主題。

**(2) 文章內容的預處理，先將內容轉為應用的最合適的型態**

所有的服務中，怎麼 "應用" 永遠都是最重要的事情，千萬別陷入 "為了技術而技術" 的窘境。我去年做過 "安德魯的部落格" GPTs, 當時就是無腦做 RAG，功能有了，但是效果還沒達到我的理想，感覺就是個書僮幫我查資料而已，還沒到能幫我 "解決" 問題的程度。

這次我的做法是對內容預先處理成 “合用" 的型態再進行 RAG (我三月直播談 Semantic Kernel 就示範過這想法了)。為了嘗試這些效果, 花了不少 token 來處理我的文章… 不過慶幸的是，這 token 花得很值得啊，這同樣會寫一段專門來談這主題 (下一篇)。

**(3) 善用 AI 工具來清理基礎結構的問題, 簡化整體的運作流程**

這段講白了就是清掉以前欠的技術債而已。為了這次的 side project, 花點時間還債是必要的, 包含殘留的 HTML (我有 60% 的文章還是 HTML, 沒轉成 Markdown), 以及其它很惱人的小問題 (中文檔名, 圖檔路徑亂七八糟等等), 這些問題不解決, 會影響以後文章發行的 pipeline。

因此，我選擇用 AI "一次性" 的重構來搞定這些問題。除了內容，我同時也處理了 repo 的結構, 清理了不再需要的圖檔, 也把路徑跟驗證的環境 ( local run - github pages ) 通通都整理好了, 現在寫文章感覺舒暢多了, 這部分有很多實際操作的心得, 也包含 vibe coding, 這段我會當作心得分享的角度來寫。對實際操作或工作流程沒興趣的可以跳過這段。



好，簡介都寫完了，接下來就直接進入正題 (有三個主題)，我預計拆成兩篇來談，第一篇 (這篇) 要談談我想要把部落格轉化成什麼樣的 "服務"? 主題以 "服務的設計為主"，轉化的主角則是 MCP server 以及使用的示範案例。第二篇我則想談談做到這件事背後的準備，包含內容的重新生成，以及原本部落格做了多少重構才能達到這目標。







—

# 1. 內容服務化 - 開發專屬的 MCP server

我啟動這 side project 的主要意圖, 就是想摸索 “部落格" 未來可能的應用模式。我的想像是 “部落格” 會更貼近資訊的來源，但是 "閱讀" 不一定是資訊最終被應用的方式。雖然最終，我決定的形式是 "開發 MCP 給大家使用"，不過使用的場景跟方式，我倒是做了一番研究。過去其實我一直在關注別人都怎麼引用我的文章的? 只要我有 PO 文，或是公開演講，我都會定期看看這些回饋:

1. 看看誰分享了我的 PO 文? 尤其是那些分享時還會加上自己看法的人
1. 看看有那些部落格, 引用我的文章當作參考聯結的人
1. 演講問券, 願意給我評分 + 回饋的人

會專注這些, 因為這些都是 "明確" 對我想法的第一手回饋資訊。觀察這些回饋，大致上都有幾種模式:

1. 觀點啟發，我可能講了一些他們從未想過的可能性
2. 技術應用，原來 OOO 的東西可以這樣子做出來，原來我常用的 ZZZ 背後是這個原理
3. 經驗學習，碰到 XXX 的問題，原來需要這樣子解決才會到位，原來解 YYY 這問題能夠解的這麼漂亮

這些，都是別人看我文章得到的價值。我想的是: 如果知道這樣對大家幫助最大, 我能否一開始就提供這樣的管道呢? 於是, 很多念頭就是這樣形成的:

> “  
> 那我用我最原始的想法來寫文章，讓 AI 生成大家需要的型態來應用就好了  
> ”

我不想改變我寫文章的思緒跟脈絡 (因為那是表達我想法最有效率的方式)，但是我可以靠 LLM 的幫助，在寫完文章後同時用合適的型態發布。所以我在今年三月的直播，第一次提出這作法。我在介紹 Semantic Kernel + Microsoft Kernel Memory 應用的時候提到:


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

這一連串思考 + 簡單的用 ChatGPT 驗證過後，感覺好像可行，而這些應用的整合環節，不約而同地都指向:

> "  
> 我需要開發一個我自己的 MCP server..  
> "  

因為寫文章 (我都用 vscode 寫 markdown, 可以用 github copilot agent mode), 寫 code 我也都用 vscode (同上), 其他的應用我更習慣用 Claude Desktop / ChatGPT 這類 AI chatbot, 如果我能不離開這些工具, 直接整合我的內容完成這些任務, 這就是我想要的理想運用情境。

於是，我就開始動工了，開始打造我自己部落格的 MCP server ( 因此，去年試做的 “安德魯的部落格" GPTs, 還有今年初用 Dify 建立的 Agent, 我都關掉了, 把資源集中在這個 side project 上 )。


而 MCP, 是個新穎的課題, 只把它當作 API 來看待會吃大虧的, 於是我也開始關注 Agent "Tools" 的設計議題 (MCP 就是個 Tools 的通用協定)。在上個月，我在 Facebook 分享了這個研討會的錄影: MCP 201, Code w/ Claude, 由 Anthrop/c 提出 MCP 規範的團隊成員現身說法, 描述了它們想像 MCP 的願景, 看完這 20min 的影片，我才算真正搞懂 MCP 這協定設計的初衷。使用者跟 Agent 互動, 大致上有三種互動型態, 一種是 "使用者" 要懂得如何對 Agent 下 "Prompt"? 一種是 "Agent (LLM)" 如何將需求轉換成 "Tools" 的使用來完成任務? 最後一種則是 "Agent (APP)" 如何有系統的取得後端的 "Resources" (例如文章內容，資料庫的紀錄等等) 有效率的回應使用者 (download) 或是再運用 (add to context) ?

看懂 MCP 想要標準化的三大原語 ( Premitives ), 對應到我想做的服務, 我應該提供這些設計:

**1. MCP Tools**,  
用來檢索，取得特定條件的內容給 AI Agent, 變成 AI 的 context windows 之一，讓 Agent 生成最終的資訊給我

**2. MCP Resources**,  
用來取得文章本文，以及生成的內容 ( vscode 可以直接開啟編輯, 或是直接 add context 進行後續操作 )

**3. MCP Prompts**,  
用來指引其他使用者寫出正確的 prompt。我應該是最熟我的文章結構跟應用方式的人，由我來提供 prompt 應該是最合理的選擇。MCP 提供給我一個標準做法，透過 MCP server 將這些 prompt 推送給 user 的管道。


因此，經過幾版的嘗試與改進，我的 MCP 現在提供這些規格:

**1. Tools**:
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

**2. Resources**:
- ```posts://{id}.md```, (原始文章內容)
- ```posts://synthesis/{id}.summary.md``` (文章摘要, 適合用來做觀點啟發)
- ```posts://synthesis/{id}.faq.md``` (文章常見問答, 適合用來做名詞解釋等有明確答案的問題回應)
- ```posts://synthesis/{id}.solution.md``` (文章解決方案, 適合用來做技術應用方式說明, 無標準做法的問題解決方案引導)
- ```posts://synthesis/{id}.metadata.md``` (文章 metadata, 包含標籤, 分類, 發表日期等資訊)

**3. Prompts**:
(這版本暫時不提供, 後續版本再來追加)


第一版就這樣問世了, 有興趣的可以試試這個公開測試的 URL: https://columns-lab.chicken-house.net/api/mcp/ , 等到我認為滿意了之後, 我會把它搬到正式的部落格網址下。

如果你想看使用示範，請繼續往下看~


# 2, MCP 的使用案例

看完規格, 我相信你還沒辦法想像 "這東西能幹嘛" 對吧? 接下來我花點篇幅, 拿幾個我自己應用這 MCP 的案例來示範用法。我相信用法絕對不只如此而已，如果你有其他不錯的使用方式，歡迎留言給我參考，當作我改善的依據

接下來，與其解釋所有的東西 ( tools, resources ) 怎麼設計, 我更想示範一下使用情境 XDD, 因此後面我就直接示範了, 關鍵設計要點我會提一下…

這部分我會截錄很多對談的案例以及畫面。如果你沒興趣的話可以先跳到下一段。



## 案例 1, 直接對話的應用 (Claude)

一開始先來入門的應用方式就好。MCP 現在的支援還有點混亂, 截至目前為止, 原生支援 http streamable 的 MCP , 我有在用的有 ChatGPT Plus, 還有 vscode + github copilot. 而 Claude Desktop 動一點手腳, 可以用 mcp-remote 這套件把他轉成 stdio 就能安裝了 (否則你要請你組織的管理者替你啟用)。安裝方式先跳過, 確認安裝完成 + 已啟用必要的 tools 之後就可以開始跟他聊。

第一個案例我示範 Claude Desktop / ChatGPT Plus 兩個版本讓大家比較一下。後面的範例我就挑一個有代表性的 Client 來測試就好。

首先, 來看看 Claude Desktop (使用 Sonnet4) 的表現:

<!--
https://claude.ai/share/783a94df-2410-4a6c-810c-045ee1e553fd
-->

```
安德魯的部落格 您好,

開發分散式的系統, 想要實作微服務架構
面臨到跨服務的交易問題

身為開發人員，我有哪些基礎的底層知識需要具備?
```

Claude 看到關鍵字 "安德魯的部落格"，跟 tools description 上面敘述的一致, 就能聯想到要回答這些問題, 應該要來用我的 MCP tools 了。在回答我的過程中 (我用的版本無法 Publish Share 對話, 我截第一段的回應畫面):

![alt text](/images/2025-09-16-chat-with-my-blog/image.png)


其中, AI 呼叫了兩次 tools:

- GetInstructions, 不需要參數
- SearchChunks, 帶了下列查詢要求


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

這次輸出的對照結果如下:

![alt text](/images/2025-09-16-chat-with-my-blog/image-1.png)


之後，我還出了題目 (我確定我沒寫過的主題 XDD)，就是訂票 (需要劃位) 類型的交易。這要鎖定控制的是每個座位的狀態，遠比單純鎖定交易金額，或是可賣數量的情境複雜得多。面對這種問題，AI 仍然能按照我文章的脈絡，用同樣原則，回答我沒有寫過的主題 (最後 AI 給了說明跟 PoC code)..

內容很長，我就貼我問的問題就好。我接著問了這段話:

```
我想從案例中學習這些 design concept 的運用
如果我的交易較複雜, 除了金額庫存等數據必須完全一致之外, 在演唱會購票的場景中, 甚至需要精確到特定的座位是否已經賣掉的問題

安德魯的哪幾篇文章有提到相關問題? 給我網址連結與相關的片段資訊

另外，我看過他文章都會用架構面試題，用很精準到位的 POC 來貫穿整個核心想法，能否用同樣方式給我一段 sample code 來說明分散式交易，處理演唱會購票的 POC ?
```

回應如下:

![alt text](/images/2025-09-16-chat-with-my-blog/image-2.png)

展示先到這邊為止，其實就 "chat with my blog" 的要求來說, 這結果其實很不錯啊, 某種程度來說你真的用 
slack 來問我一樣的問題, 我的回答也就差不多是這樣而已 (要我真的現場寫一段 code 給你的話，我大概只會寫 psuedo code ...然後給你一堆參考連結讓你自己去看我寫過的東西)。



## 案例 2, 直接對話的應用 (ChatGPT)

同樣的案例, 我用了 ChatGPT Plus 也測了一次。會多測這個，因為我在寫這段文章時, ChatGPT 才開始支援 MCP (beta) 而已, 我自己也是第一次使用, 就順手貼上來比較一下。

對比 Claude Sonnet 4 回應的版本, 我在 ChatGPT Plus 上使用的是 GPT5 + Thinking, 比較起來, Claude 回答的比較一板一眼, 這樣好處是不大有模糊或想像空間, 不過讀起來就吃力了點。而 ChatGPT 在文字潤飾感覺花了不少功夫, 讀起來輕鬆一點, 但是即使我自己是原作者, 我都得花點心思才能確認是不是我寫的。還好內容都算正確, 並沒有發現幻覺或是亂掰的現象, 附上的引用連結也都正確, 能正確的連回我的部落格文章。

我都用同樣的問題來測試 (同上, 我再貼一次):

```
安德魯的部落格 您好,

開發分散式的系統, 想要實作微服務架構
面臨到跨服務的交易問題

身為開發人員，我有哪些基礎的底層知識需要具備?
```


觀察回答第一段的過程, 兩者都呼叫了我的 MCP, 可以看到兩個模型的思考過程差異很大, Claude 很直線的思考, 按照我的要求先 call: GetInstructions 之後, 就接著 call: SearchChunks, 執行了主要的查詢 (如下):

```
{
  "limit": 10,
  "query": "分散式交易 distributed transaction saga 兩階段提交 2PC 微服務 跨服務交易",
  "synthesis": [
    "origin",
    "solution",
    "faq"
  ]
}
```

緊接著就開始生成答案 (略). 從 AI 下的 Query, 你大致上可以猜得出來他的思考方向。同樣的問題, ChatGPT 則是分成兩次 call: SearchChunks, 我把兩次的參數都貼出來 (回應太長, 略):

```
{"query":"微服務 分散式 交易 跨服務 一致性 Saga Outbox 兩階段提交 TCC 事件驅動 可靠投遞 基礎 知識","synthesis":"summary","limit":8}
```

```
{"query":"Saga 兩階段提交 TCC Outbox 分散式 交易 一致性 微服務","synthesis":"summary","limit":8}
```

也許這就是啟動 thinking 的差異吧, 看起來 GPT5 會根據第一次查詢結果, 來微調查詢的範圍再進行第二次查詢。查完之後才生成最終的結果。

回覆的結構我也貼一下, 基本上都算正確, 但是風格各有不同:

![alt text](/images/2025-09-16-chat-with-my-blog/image-3.png)


完整的回應內容, 我直接分享 [對話紀錄](https://chatgpt.com/share/68d02d3f-742c-800d-82eb-2d173c9da4cd), 有興趣的可以直接看參考



## 案例 3, 拿文章來 vibe coding


接下來這個測試的場景是:

> "  
> 當我 (讀者) 看完文章後, 想要按照文章的介紹來實作看看文章裡介紹的案例, 我希望能藉由這個 MCP, coding agent 就能直接給我對應的 code ...  
> "

因為目的是 coding, 這次就不用 ChatGPT 了, 我直接改用 vscode + github copilot 來測試。我拿我還挺自豪的文章當案例, 用 C# 實作 pipeline 的 CLI:

Reference: [後端工程師必備: CLI + PIPELINE 開發技巧](/2019/06/15/netcli-pipeline/)

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

簡單的說一下心得, 這段 code 的確滿足我的要求, 作法也有按照我文章內提到的重點來設計。而跟我期待不同的是, 我沒有很認真追 C# 的新語法, 以及 .NET Basic Class Library 的新功能, 加上這篇文章是六年多以前寫的 (2019/06), 同樣的目的現在也許都有更好的寫法了。

而 LLM 替我生成的 code, 一來符合架構設計上的要求, 而來語法與函式庫也都跟上當今主流的做法了 (例如過去我用 blocking collection, AI 則改用 reader / writer channel 來改寫), 這種體驗單純看舊文章是無法得到的啊，算是另一個拿 AI 當書僮的好案例。


而為了方便測試, AI 也把能測試 pipeline 的假資料 ( json line ) 也生出來了:


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

最後, 執行測試的 shell script 也生出來了 (我只節錄片段):

```bash
# 範例 1: 基本用法
echo "=== 範例 1: 基本用法 (平行度 2) ==="
cat test-data.jsonl | dotnet run --project src/pipeline-cli/ -- 2 2>/dev/null | head -n 3
echo ""
```


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



## 案例 4, 整理我的部落格演進史

既然都能 vibe coding 了, 反正我寫部落格文章, 也都是用 vscode... 第四個案例就來示範一下 vibe writing 好了。寫這篇文章的時候，我就回想到九年前寫 Blog as Code 這篇文章時, 當時我花了一番功夫, 才把我歷年來對部落格做過幾次改造的內容整理好，才有這些內容。

本來，這篇我還要再來一次的，不過都有 AI + MCP 了, 我就邊示範邊寫這段好了, 對我而言這是單純的資料蒐集跟整理, 由 AI 來代勞很合理，就來試試成果好了。

我想要按照時間序，把我過去提及的部落格系統改版的重點摘要列出來。整個系統更換當作主項目並標上年份，該系統的客製化調整當作子項目..., 於是我在 agent mode 下這樣要求:

```markdown

請幫我填上這段 markdown 區段
幫我整理 "安德魯的部落格" 歷年來移轉系統的記錄當作主要項目清單

每個系統安德魯自己做過的客製化項目摘要當作子項目

按照時間順序排序, 每個項目敘述請控制在 100 字以內，同時附上參考文章標題 + 連結。用下列格式提供:

(2004) 自行開發 .NET Forum
- 新增 RBAC 權限控制機制
- 新增 RBAC 權限控制機制
- 新增 RBAC 權限控制機制
- 參考文章: [article title here](article url here)
(2005) 系統移轉: 改用 .TEXT
(2005) 系統移轉: 改用 Community Server

```

等了一分鐘後, 得到的結果如下 (我列 2008 以後的就好, 前面改的很頻繁, 略):


--

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

其實還蠻正確的啊, 即使是九年前, 我也還記得寫那段的過程。就算是我自己寫的文章, 在當時我仍然得透過 Google 來找我自己的部落格文章, 花了些時間才能整理出這樣的內容。現在，透過 agent, 短短一分鐘就搞定這問題了。看到科技的進步了，生成式 AI 在處理文字資訊上真的是不同世代的技術，過去要花一個晚上的事情，現在兩三分鐘就能完成。

雖然我一開始就說, 我不會放棄自己寫文章的習慣, 也不會改用 AI 替我生成文章。但是, 靠 AI 幫我整理資訊, 這類任務本來就是我不喜歡做的，因為不會表達出太多我要傳達的心法，但是為了論述過程卻又不得不做的苦工，這種任務交給 AI 最合適了啊..., 諸如此類的應用，在寫文章或寫文件應該很常碰到，我就示範到這裡，其餘延伸的應用就交給各為自己去挖掘。



## 案例小結

其實，還有其他的應用，但是礙於篇幅 (實在太多了) 我就賣個關子，之後當作零星的主題，直接在 FB 上面 PO 文探討吧! 其他有 resource 的應用 ( 直接在 vscode 用 post uri 就能叫出文章原始內容 ), 或是在 agent mode 下直接將文章加入 ( add context ) 附件參考。

另外我也試了從部落格當作知識庫，產生整份學習計畫，甚至生成測驗考題，以及生成實作題的 Handson Labs 講義等等，這些都很有趣，而且都能精準地抓到當時我寫這些文章的核心概念，這些案例大家可以自己試試看，我就不一一示範了。





# 3, MCP 的介面設計心得

這段, 其實是我整個 side project 過程中, 花最多時間思考的地方。MCP 要讓他 "能動" 其實很簡單，但是要 "理想" 就有很多設計議題要考量了。MCP 就是把 Tools (還有很少人談的 Resources & Prompts) 暴露給 Agent 使用的通訊協定, 只要符合協定 Agent 就能用。但是要期待 Agent 用的好，則你的 Tools 設計就要針對 Agent 的使用情境來設計才行。

這跟 API 很類似啊，大家一定都看過規格開的好的 API，跟開的爛的 API 的差別有多大，MCP 也一樣。只是 MCP 實在太新了 (2024/11 才問世)，要談設計，說真的能參考的案例也不多，因此我也想把我摸索嘗試的過程跟心得記錄一下。

如果把問題範圍擴大一點，不限於談 MCP，而是來談 tool use 的 tool 該怎麼設計, 那案例就多得多了。2023 年年底我在談 "安德魯小舖" 的時候，就是在談給 AI 用的 API 在設計上要注意的地方。回顧一下，以下是我過去兩年談論相關問題的摘要:

(有開發這個 MCP 實在是太棒了, 以下也是靠 agent + mcp 整理的)

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

## 按照工作流程來設計 MCP

當時我還沒辦法講得很清楚，因此我還是沒有完全脫離 API 的影子，不過這半年來都在關注這題，我覺得越來越能抓住重點了。看了很多 MCP 的設計案例跟研討會錄影，我會用這句話當結論:

> "  
> 別用 API 的角度來設計 MCP，要從工作流程來設計。
> "

有興趣的可以參考這段:
- [iHower 電子報 #31](https://ihower.tw/blog/13197-aie-openai-gpt-5)
- 原始文章 - [Block's Playbook for Designing MCP Servers](https://engineering.block.xyz/blog/blocks-playbook-for-designing-mcp-servers)

我會這樣理解，未來就是人跟 Agent (AI) 的互動為主要的操作方式。而 MCP 則是使用者 "授權" (安裝) 給 Agent 使用的工具。想像 Agent 收到使用者要求後會怎麼執行任務，你的工具如果能配合這執行方式 (就是工作流程) 來設計，那麼這個工具 (MCP) 對於使用者來說，就是個好的設計。

這邊我直接針對部落格的 MCP 設計來探討: 何謂 "使用部落格的工作流程" ?? 前面有提到，我設想過大家會怎麼使用我的部落格? 不外乎:

> - **訂閱**, 當作雜誌來看, 我寫什麼就看什麼。這個現在就做得很好了，不大需要額外處理。
> - **新知**, 有特定問題 ( question ) 時想要來我部落格找相關資訊。例如幾個我長期關注的主題, 像是分散式系統、平行處理、微服務架構、AI 應用開發等主題, 有時只有模糊的印象, 想要來我這邊找到明確且專業的說明
> - **解題**, 有特定的難題 ( problem ), 想要來我的部落格找找有無合適的解決方案。例如我常常寫的架構師觀點，或是架構面試題就屬於這類。我都會定義常見但是很棘手的情境，然後分析背後關鍵因素，並且提供範例跟整個開發過程來示範如何解題。
> - **學習**, 想要學習怎樣才能當個架構師，想要學好特定的主題，或是某個特定的技術或是概念, 例如我寫過一系列的 .NET CLI + Pipeline 的文章, 以及平行處理的文章, 這些都是針對特定技術的學習內容

上面的每一項需求，展開來都是一個完成任務的工作流程 ( workflow )。如果都把 AI 當作 "真人" 看待，因此很多工作流程的設計，我會先思考 "如果是真人會怎麼做" ? 然後再把這些工作流程寫進 Prompt 引導 Agent 照著執行。

我就拿 "解題" 這需求當作案例吧，同時拿一篇我覺得經典的文章來示範:

> "  
> "微服務的排程處理", 這是我實際在工作上碰到的問題。假設時間回溯再來一次，我還不懂這題怎麼解，而當時如果有個懂得這技巧的 "前輩" 在身邊，那我會怎麼做?  
> "

我腦袋中會開始 "敘述" 這個過程，而 ( ) 中間則是抽出來的關鍵，稍後會對應到 MCP 的三大原語 ( Primitives ) - Prompts, Tools, Resources, 最後就變成我實作 MCP 的規格草案。

--

首先，我一定會先了解這前輩的工作習性，喜好，以及他的專長等等 ( GetInstructions )。簡單的說我會先了解怎麼跟他溝通。如果有人寫好 "如何好好運用前輩" 的使用說明書，那就太好了。其實這不是我瞎掰的，當年在做 HR 系統，就有這樣的概念, 工作說明書 - Job Description, 職能說明 - Competency 等等, 這些都是在描述一個角色該怎麼工作, 以及該怎麼被運用。

接下來，我應該不夠專業，因此我只能跟前輩尋求指點 ( Search Chunks ), 我會把問題描述 (query) 給他聽, 如果需要, 我會額外交代清楚我是在什麼前提或是情境下 ( context ) 碰到這問題的。我期待這位前輩，在我尋求協助 ( Search Chunks ) 之後，能盡量給我任何對我有幫助的線索，即使是片段資訊都沒關係 ( chunks ) ，對我來說都可能是能救命的浮木。

有了線索之後，我可以開始逐步找到對我有用的原始資訊 (通常都是第一手資訊)。前輩如果有自己的筆記跟知識庫的話 (部落格?)，能給我 (GetPostDetails) 原始的文章資訊 (PostId, Metadata) 就再好不過了。有了文章連結，我也會希望多看看有沒有類似主題，或是相關的其他文章等 (GetRelatedPosts)。

--

當我對問題已經有眉目了，代表我對問題的脈絡 ( context ) 已經有所掌握，接下來就可以真正來解決我的問題 ( problem, solution ) 了。我生再有 AI coding 工具的年代, 我只需要跟 coding agent 說明清楚我的需求, 我要的結果, 更重要的是處理的問題脈絡 ( context ) 的第一手資訊都來自前輩的提點, 上面那些資訊都應該當作我給 coding agent 的參考資訊 ( add context ) 才對, 於是 coding agent 就能幫我完成任務。

( 接下來就是一連串 coding agent 的使用技巧跟操作過程了，略過 )

以上，就是一連串的 "工作流程" 啊! 跟這位前輩的互動過程中，我在敘述中都標記了一些關鍵字，這些都是互動過程中要執行的 "動作"，或是要取得運用的 "資源"。而這位前輩，如果是個知識庫，並且有個對應的 MCP 能夠提供這些動作跟資源，那我就能順利地完成我的任務了。

因此，按照上面描述的 Workflow, 我的 MCP 若能提供這些一一對應的 Tools, 對 Agent 來說就很直覺，符合常理，不需要再經過其他轉換就能執行。我重新貼一段前面提及的 MCP 設計規格 (再貼一次):


**Tools**:
- ```GetInstructions()```, 使用說明書, 給 agent 參考的 instructions. 因為需要包含動態資訊, 同時也參考了 Shopify 的 MCP 設計方法, 因此我特地做成 Tool, 而不是只放在 Description 裡。
- ```GetPostContent(postid, synthesis, position, length)```,   查詢指定文章 (須提供 postid) 的資訊
- ```GetRelatedPosts(postid, limit)```,  查詢指定文章的相關文章清單 (須提供 postid)
- ```SearchChunks(query, synthesis, limit)```,  按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文字片段
- ```SearchPosts(query, synthesis, limit)```,  按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文章清單

這的確就是我第一版 MCP 運作中的規格。有興趣的人不要只是安裝我的 MCP server 直接使用, 你也可以用 MCP 官方的 MCP 測試工具 - @modelcontextprotocol/inspector 來實際測試一下 MCP server, 你會更清楚的掌握他背後做了什麼事情。

// 圖: MCP inspactor


而 MCP, 只是把上面的流程, 用標準協定轉變成可執行的規範而已。



## MCP 應用的想像 - 下個世代的 API

視角拉遠一點，我覺得在未來的世界，MCP 會是 Agent 時代的 API。過去風行 10 年的 SaaS, 標榜的是軟體服務開箱即用, 除了有 APP / Web UI 之外，規模大的 SaaS 也會強調跨服務的整合, 培養自己的 EcoSystem, 依靠的都是暴露自身服務的 API 來達成。

因為當時強調的都是 "軟體即服務"，服務就像水電一樣，管線鋪好水龍頭打開就能用。管線就是 API ...，鋪設過程就是整合 (串接 API)。而現在 Agent 時代，AI 自己會去讀懂 Tools Spec, 自己會執行 Tool call, 整合這段的工程省掉了, 而要被呼叫的 Tools ( API ) 的提供方式就變成更適合 Agent 的 MCP。未來的 SaaS, 關鍵不再是有沒有 API (這要等別人來串接)，而是有沒有 MCP，對方有 Agent 只要設定好就能直接使用。

我覺得這轉變，已經看的到方向了，MCP 也 (意外的) 獲得各大廠的支持，看來變成標準規範已經沒有懸念了。未來，我覺得最關鍵的就是軟體產業的轉型。我最近在幾個場合, 都在聊這個想法。軟體發展, 從 "套裝軟體" (工具買斷，安裝使用)，進展到 "服務訂閱" (工具訂閱，立即可用)，而未來會是什麼? 我大膽亂猜一下，我會覺得是 "工作流程訂閱" (賦能使用者的 AI Agent，立即可用)。

這改變的前提是使用者的習慣，已經轉移成 Agent 導向的工作方式了。到目前為止 ( 2025/09 ), 這變革在軟體開發領域已經發生了, 其他領域還沒這麼徹底。我舉幾個事實來說明軟體產業已經走到什麼地步了，正好也可以當作其他領域未來發展的預測基礎:

開發工具的快速轉移:
直到兩三年前，不管你是不是 Microsoft 生態系的使用者，這句話大概都有聽過: 

> Visual Studio 是地表最強的 IDE, 沒有之一

不過，這一年完全沒有人在談論 Visual Studio 了, 大家都在談 AI IDE ( vscode + github copilot, cursor, windsurf 等等 )。大家的開發方式, 談論主題已經不是怎麼寫，用哪個工具或套件了，談的是怎麼 vibe coding, 怎麼讓 agent 能正確的替你工作...

然而 cursor 紅了一年, 最近又開始有新的工具冒出來了, 開發者的社群都在討論各種 CLI 版本的 coding agent. 這趨勢其實很明顯, 從大型的 IDE (visual studio) -> 小型且靈活的 IDE (vscode + extensions, 以及各種 IDE 的變形, 例如 cursor / winsurf) -> 更進一步的 IDE 消失了, 只剩下 CLI 版本的 coding agent ( Claude Code, Codex ...)。短短這一年多的演進過程，其實就是 Software Developer 已經越來越能接受 Agent 的使用方式了，也連帶的帶來工作流程的改變 (一瞬間，因為寫好文件能讓 Agent 有效率的工作，過去大家很討厭的寫文件，現在突然變成顯學了... 看看 Kuro / Spec Kit ...)


我認為其他產業的主流生產力工具，遲早也會往這方向進展，只是軟體開發領域是海嘯第一排，最早發生而已。身處這個產業，正好讓我親眼見證她的轉移過程，可以當作其他領域會怎麼變化的參考。而 Agent 為主流的使用型態, 除了這些軟體大廠之外, 其他特定領域的服務怎麼跟這些 Agent 共存? 答案就是提供 MCP, 讓使用者能無縫的透過 Agent 使用你的服務。

--


因此，最後來回顧一下我在 Facebook 貼的這兩篇 PO 文, 講的是同一件事, 只是在 FB 我沒有空間談前面這些觀察，只是講出我的看法。現在我把這些心得補在這裡，正好交代完整個思考脈絡:

// 2025/08/20 post
// 2025/09/04 post






## MCP 設計參考: Shopify.Dev MCP

最後，談 MCP 的設計，來聊聊這段期間我一直在關注的 Shopify 推出的 MCP: Shopify.Dev MCP。

其實這套 MCP 出來很久了，到現在至少有半年了，規格也大翻了很多次，但是使用起來都無痛轉移... 我沒特地去翻規格的話還不會發現，只是覺得跑起來效果變好了。最近有個很紅的 MCP: Context7, 你可以把 Shopify.Dev MCP 想像成他是 Shopify 的專屬版本。





整個改版的過程中 ( 大約兩個月, 2025/07 ~ 2025/09 ), 其實我花了不少時間, 用 vibe coding 寫了很多很雜亂無章的 code, 目的就是 prototype 實際體驗一下效果, 不滿意就砍掉重來。這過程中我嘗試過不少設計方式, 也看了很多設計的 guidelines, 但是最後回頭看, 最有用的還是直接參考其他優良的 MCP 設計。以我的案例來說，我找了個不錯的範例, 就是 Shopify.Dev MCP。

這段，我先來聊聊 Shopify 的作法。當初我看完 Shopify 的設計之後，突然領悟到 "MCP 不是 API" 這回事，也才真正領悟到 "要對著 workflow 設計" 這句話背後的意義。對 Shopify.Dev MCP 有興趣的可以直接看官網介紹，網址在 [這邊](https://shopify.dev/docs/apps/build/devmcp), 我直接摘要前面的簡介:

>
> **Shopify Dev MCP server**
>
> Connect your AI assistant to Shopify's development resources. The Shopify Dev Model Context Protocol (MCP) server enables your AI assistant to search Shopify docs, explore API schemas, build Functions, and get up-to-date answers about Shopify APIs.
>
>
> **How it works**
> 
> Your AI assistant uses the MCP server to read and interact with Shopify's development resources:
> 
> 1. Ask your AI assistant to build something or help with Shopify development tasks.
> 1. The assistant searches Shopify documentation and API schemas based on your prompt.
> 1. The MCP server gives your AI assistant access to Shopify's development resources, so it can provide accurate code, solutions, and guidance based on current APIs and best practices.
> 

實際上我用 MCP Inspector 來看他的 Tools 定義, 寫這段的當下 (2025/09/06) 它提供了這些 tools:

- learn_shopify_api(api, conversationId)
- search_docs_chunks (conversationId, prompt, max_num_results)
- fetch_full_docs(conversationId, paths)
- introspect_graphql_schema(conversationId, query, filter, api, version)
- validate_graphql_codeblocks(conversationId, api, version, codeblocks)

其中特別說明一下 api 這個參數, 它代表的是你想要開發 shopify 哪種形式的應用? 可用的數值有: admin, functions, hydrogen, storefront-web-components. 這算是 shopify-dev 的最上層分類, 包含文件, 規格, 應用範圍等等都有所差異。而這 MCP, 你可以想像成他的開發資源網站 https://shopify.dev 的 MCP 版本。過去是開發人員自己要來這網站查資料回去自己寫 code, 而現在都由 coding agent 代勞, 而這 MCP 就是 agent 時代的開發資源服務了。

直接來看看第一個 tool: learn_shopify_api(api, conversationId). 很有意思的設計, 過去我看的都是工具類型的 MCP, 大概就是 API 套殼的應用, 沒有甚麼特別的, 而第一次看到這種設計, 算是讓我大開眼界。在 MCP tools description 上, 它是這樣描述這 tools 的用途的 (內容很長，我只擷取頭尾):



```markdown

🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.

⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.
This tool generates a conversationId that is REQUIRED for all subsequent tool calls. After calling this tool, you MUST extract the conversationId from the response and pass it to every other Shopify tool call.

🔄 MULTIPLE API SUPPORT: You MUST call this tool multiple times in the same conversation when you need to learn about different Shopify APIs. THIS IS NOT OPTIONAL. Just pass the existing conversationId to maintain conversation continuity while loading the new API context.

// 中間略過

```

看完這些敘述, 加上過程中我踩過的各種坑, 我開始佩服 Shopify 的設計了, 我踩過的坑, Shopify 都漂亮的閃避過去了, 我相信背後應該花了比我更多功夫才對。我解讀一下這些 description 背後的意圖:


如何讓 Agent 照你想要的方式使用工具?  

這邊 Shopify 就做了個示範, 軟硬兼施。一方面 tool description 很明確地敘述他的規則 (一定要先 call learn_shopify_api), 同時工具的設計也強制要求必須帶上 conversationId, 若沒照做 shopify 的 tools 會拒絕提供服務。而更厲害的設計是, conversationId 也刻意藏在 markdown 內 (要是我我應該會直接放 json 用結構化的方式輸出)，隱含了要從文字抽取內容的不確定性，但是一旦能成功抽取，就代表 agent 真正的把這段內容放進 context window 了。簡單的設計，一次解了三個難題:

- 確保 agent 聽你的流程
- 拒絕行為不良, 不按照指示操作的 agent
- 確保 agent 將 instruction 放進 context window



明確告知 agent 服務範圍

前面提到 api 是個很關鍵的上層分類, shopify 直接在 description 明確的列舉了所有的分類跟使用情境 (我列在下方), 這敘述不放在 argument 說明, 而是選擇往上提到 description, 代表這是更廣域的敘述。我覺得這麼做的意義, 已經不只是參數的列舉而已了, 也把整個規則跟情境交代清楚了。

節錄片段敘述 (就是上面省略的部分):

```markdown

🔄 MULTIPLE API SUPPORT: You MUST call this tool multiple times in the same conversation when you need to learn about different Shopify APIs. THIS IS NOT OPTIONAL. Just pass the existing conversationId to maintain conversation continuity while loading the new API context.

For example, a user might ask a question about the Admin API, then switch to the Functions API, then ask a question about polaris UI components. In this case I would expect you to call learn_shopify_api three times with the following arguments:

- learn_shopify_api(api: "admin") -> conversationId: "123"
- learn_shopify_api(api: "functions", conversationId: "123")
- learn_shopify_api(api: "polaris", conversationId: "123")

This is because the conversationId is used to maintain conversation continuity while loading the new API context.

🚨 Valid arguments for `api` are:
    - admin: The Admin GraphQL API lets you build apps and integrations that extend and enhance the Shopify admin.
- functions: Shopify Functions allow developers to customize the backend logic that powers parts of Shopify. Here are all the available APIs: Discount, Cart and Checkout Validation, Cart Transform, Pickup Point Delivery Option Generator, Delivery Customization, Fulfillment Constraints, Local Pickup Delivery Option Generator, Order Routing Location Rule, Payment Customization
- hydrogen: Shopify Hydrogen store feature implementation guides. Here are all the available feature guides: Bundles, Subscriptions, Combined Listings, Markets. Always use this tool first when implementing one of these features in a Hydrogen store. Keywords: hydrogen, localization, markets, subscriptions, selling plans, combined listings, bundles. 
- storefront-web-components: How to create storefronts using Storefront Web Components. Storefront Web Components let you bring Shopify-powered commerce capabilities to any website. Shopify Storefront Web Components are a set of web components that enable developers to build customizable storefronts using only HTML and Shopify's APIs. Keywords: web components, html, shopify-store, shopify-context, shopify-list-context, shopify-data, shopify-media, shopify-money, shopify-cart, shopify-variant-selector

```

前段說明了使用規則, learn_shopify_api 一次只能取得一種 api 的使用授權, 你要用全部的 api, 那請照規矩來, agent 請務必每種 api 都先好好學習過一次 XDDD (真的像是老師在教學生一樣)。

而後段，則是單純的列舉所有 api 可用的數值, 以及使用說明。



最後，則是工作流程說明。這段 description 直接告訴 agent 明確的步驟跟規矩:

```markdown


🔄 WORKFLOW:
1. Call learn_shopify_api first with the initial API
2. Extract the conversationId from the response
3. Pass that same conversationId to ALL other Shopify tools
4. If you need to know more about a different API at any point in the conversation, call learn_shopify_api again with the new API and the same conversationId

DON'T SEARCH THE WEB WHEN REFERENCING INFORMATION FROM THIS DOCUMENTATION. IT WILL NOT BE ACCURATE.
PREFER THE USE OF THE fetch_full_docs TOOL TO RETRIEVE INFORMATION FROM THE DEVELOPER DOCUMENTATION SITE.

```



看完 learn_shopify_api 的設計後, 剩下另外四個 tools 的用意就明確的多，這邊我摘要重點就好。對於特定技術規格的功能開發，我們通常會:

1. 先 google 找看看相關資訊 (片段), 從中間找尋是否有需要的線索
1. 找到對的方向後, 接下來就會從特定主題去找完整說明文件來參考，決定該怎麼寫出程式碼

這些事前的研究作業, 正好就對應了這兩個 tools, 名稱都取的夠直接清楚, 說明我就略過了 (直接貼 tool description):

- search_docs_chunks (conversationId, prompt, max_num_results)
> This tool will take in the user prompt, search shopify.dev, and return relevant documentation and code examples that will help answer the user's question.
- fetch_full_docs(conversationId, paths)
> Use this tool to retrieve a list of full documentation pages from shopify.dev.

同樣的，看了文件後，你應該能將需求寫出第一版 source code 了 ( coding agent 的工作 )。而其中最複雜的 code, 大概就屬於要寫出 GraphQL 的查詢了吧。寫查詢，最煩的就是弄清楚來源資料有哪些欄位可以用 ( schema ), 以及要滿足使用者的要求, 到底該挑出那些欄位才對?

而要讓 agent 弄清楚這些資訊, Shopify 提供了這個 tool:

- introspect_graphql_schema(conversationId, query, filter, api, version)
> This tool introspects and returns the portion of the Shopify Admin API GraphQL schema relevant to the user prompt. Only use this for the Shopify Admin API, and not any other APIs like the Shopify Storefront API or the Shopify Functions API.

細節我就不往下挖了, 基本上 MCP 提供了文件, 這個 tools 又進一步提供了 schema 的查詢, 這些資訊都能讓 agent 有足夠的 context 來寫出符合需求的 query 了。


最後一步, 需要有方法來檢驗寫出來的 code / query 是否 "合格"? 要能驗證 "是否正確" 是很困難的，但是要驗證是否能執行或編譯就簡單得多。這點我覺得很重要，讓 agent 能對自己的輸出有基本驗證能力的話，明顯的問題就不需要使用者介入，agent 自己能按照錯誤訊息重新調整。然而在 shopify mcp 的案例內，這些東西都只存在文件上，因此 shopify 也額外提供了基本的驗證機制:

- validate_graphql_codeblocks(conversationId, api, version, codeblocks)  
> This tool validates GraphQL code blocks against the Shopify GraphQL schema to ensure they don't contain hallucinated fields or operations. If a user asks for an LLM to generate a GraphQL operation, this tool should always be used to ensure valid code was generated.
>
>    It returns a comprehensive validation result with details for each code block explaining why it was valid or invalid. This detail is provided so LLMs know how to modify code snippets to remove errors.

如此一來，我覺得流程上必要的要素都完備了。一開始交代好這組工具 (MCP) 的遊戲規則，告訴 agent 必須先學好才能開始使用 tools, 而查完文件, 查完規格, 寫了 code / query 後, 檢驗看看是否符合規範。這整個過程，以 agent 現在的能力，其實是能夠完全自己處理的。不得不說 Shopify.Dev MCP 的設計者很懂 developer 的流程與需要, 這 MCP 完全就是按照 workflow 而設計出來的。

看完這個案例，清楚什麼叫做 "依照 workflow 設計 MCP" 了吧? 我自己的 MCP, 使用場景其實跟 Shopify.Dev MCP 類似, 我也參考了不少他的做法, 才能完成上面的案例。我自己的 MCP tools 就不多說明了, 基本上很類似, 有興趣的朋友可以拿 MCP Inspector 來看我的 MCP server 的 tools 定義。












給了明確的步驟，也清楚交代了別上網搜尋 (只能透過 tools 來取得資訊)。看完之後，你會發現，Shopify 根本不是在設計一個 "服務"，或是一個 "API"，而是在設計 agent 該如何配合 shopify mcp 完成開發者任務的 "工作流程"。從理想的開發流程中，逐步分解 + 推導，最終落實到 MCP 的規格設計。







<!-- 
# 2. 內容正規化 - 生成特定格式的內容

# 3. 流程效率化 - 流程優化, 清除文件的技術債

# 結論 -->