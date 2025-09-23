---
layout: post
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: 
---

過去，我在寫部落格文章的時候, 總是有個難題: 當題目我越挖越深入的時候, 即使我有能力交代清楚來龍去脈, 但是對讀者而言, 從 "看完" 到能理解並且能 "運用" 的過程往往都很漫長，中間隔著好幾道門檻。

我曾經暗地嘗試過幾種做法，包含:

- 不要寫那麼長的文章 (結果是最重要的心法沒交代到位)
- 只寫操作步驟跟範例 (沒交代原理, 太複雜的問題讀者沒辦法應用)
- 拆成好幾篇分開寫 (結果是讀者不一定每篇都看, 時間間隔太久, 看了後面忘了前面)

不過，現在我看到曙光了。我隱約覺得 AI 應該能漂亮的解決這題才對，於是我就開始嘗試各種方案。我的想法是: 嘗試開發一個專屬的 MCP, 把我的部落格重構成一套可以被 Agent 充分運用的 "工具與素材"，按照讀者使用我部落格的方式來設計 tools, resources, prompts 來與 Agent 互動。我覺得軟體服務的未來, 一定是走向使用者高度與 Agent 互動，因此軟體服務開始提供 MCP, 就跟過去軟體服務提供 API 一樣，是個必然的發展路線了。

因此，我挑了這個題目: "Chat with My Blog" 當作目標, 來啟動這個 MCP 開發，跟部落格重構的 Side Project. 正好呼應九年前我部落格系統大改版的紀錄 "[Blogging as Code!!](/2016/09/16/blog-as-code/)" (2016/09/16), 做個對照。九年前是完全放棄 "系統"，改以靜態內容為主的改版；現在則是把重心放在 Agent 身上的服務化 + 重構。


<!--more-->

這個主題，我會分兩個部分來談:

1. (這篇) 我想談談 "服務化" 本身，主角是 MCP 的設計，將我部落格的資源掛上 Agent 的設計過程
2. (下一篇) 我想談談 "重構" 的過程，主角是內容的預處理，如何在發布文章時預先用 LLM 處理，最大化 MCP + Agent 效益的做法跟流程

其實這兩篇的事情我都做完了, 才會有這個 MCP 可以使用 (MCP 使用方式我放在最後的段落)，不過文章要整理一下，各位可以先看這篇 (服務化) 的部分，下一篇我整理好就會貼上來，敬請期待。

在開始之前, 如果你迫不急待想體驗一下我的 MCP (安裝與使用步驟請看最後一段的使用說明), 只要你的 MCP Host 支援 streamable http 協定的 MCP server, 那麼輸入這個網址 ( https://columns-lab.chicken-house.net/api/mcp/ ) 就可以啟用了。如果你裝了很多 MCP, 問的時候特別說明一下 "安德魯的部落格"， 你的 Agent 應該都能正確的呼叫我提供的服務。



# 為什麼要把部落格做成 MCP?

<!--
從「把文章變成能直接被 Agent 使用的材料」這個痛點出發；同時在開頭明確切分兩篇的邊界（本篇＝服務設計與驗證；下篇＝內容處理流水線）。
-->

這次改版我想做的, 首要目標就是 "讓我的部落格文章能充分被 Agent 好好利用"，這是所有 AI 應用的基礎，而其中的關鍵就是要做好內容的檢索，同時要優雅的整合 Agent。要正確找出對的內容不是件容易的事啊，這邊花掉我最多的研究時間。為了達成我的期待, 我把這次施工範圍分成三個目標:

1. **內容服務化**, 服務要能用主流的型態接上 Agent ( 手段: MCP )  
關鍵是 MCP 該提供什麼樣的 tools 來輔助 agent 做好這情境。同時，我也重新調整了部落格的系統架構, 為了體驗一致性, 我希望原部落格網址加上 /api/mcp 就是對應的 MCP server endpoints, 動用了 Azure 上的服務 ( frontdoor + container apps ), 感謝 Microsoft 給 MVP 的使用額度 :D

2. **內容正規化**, 內容要預先轉換成易於使用的格式 ( 手段: LLM 預先生成 )  
目前我的文章都有我自己的思路, 從情境 → 問題定義 → POC → 形成解決方案等過程。而這種有思路順序的長文章，是非常不適合用 RAG 處理的，因為切斷後的內容 ( max: 8kb ) 都不是個完整的主題, 被檢索出來無法有效應用, 效果就不理想。我認為理想的做法是: 先用 LLM 精煉這些內容，轉成適合被 RAG 應用的型態，再作後續處理。最花時間跟最花錢 (token) 的就屬這部份了, 再次感謝 MVP 的 Azure 使用額度 XD

3. **流程效率化**, 重新整理工作流程，清除技術債 ( 手段: AI IDE 重構 Repo )  
2016 年轉換到 GitHub Pages 時, 很多格式轉移的任務, 其實我都只做到 "可以動" 就好的地步，尤其是舊文章還有 70% 左右都還是 HTML, 圖檔連結壞了也沒有修正。這次為了能有效率的達成 (2), 藉助了 AI Agent + IDE 的幫助 ( 我用 GitHub Copilot ), 也順手把整個 GitHub repo 的內容都重構了一次，做好 (2) 有效率進行的工程基礎。

每個目標，對我來說都是大工程啊啊啊啊, 也都各有不同的挑戰要克服。前言就提到，我打算分兩篇來寫，這一篇就先聊聊 MCP 的部分，而在 MCP 背後做的其他努力，我在下一篇說明。這段落就當作全貌好了，我先聊聊這三個目標背後的設計重點:

**(1) 用 MCP 來發布服務，關鍵在 Tools 的介面設計**

MCP 並不是 API, 如果只是把 REST API 包裝成 MCP 的話，那就大錯特錯了。特地為了 Agent 來設計 MCP 是最理想的做法, 這也是我這次 side project 最大的收穫。我看了 MCP 團隊成員分享設計理念，也花了點時間研究 Shopify 的 MCP，才算掌握到一些設計的要訣。最好的 MCP 設計，就是以 Agent 要解決問題時順著他的思考脈絡 ( context ) 給予最大的支持，想通這點，我才終於搞懂為何 MCP 會取名為 MCP ( Model Context Protocol )。

**(2) 文章內容的預處理，先將內容轉為應用的最合適的型態**

所有的服務中，怎麼 "應用" 永遠都是最重要的事情，千萬別陷入 "為了技術而技術" 的窘境。我去年做過 "安德魯的部落格" GPTs, 當時就是無腦做 RAG，功能有了，但是效果還沒達到我的理想，感覺就是個書僮幫我查資料而已，還沒到能幫我 "解決" 問題的程度。

這次我的做法是對內容預先處理成 “合用" 的型態再進行 RAG (我三月直播談 Semantic Kernel 就示範過這想法了)。為了嘗試這些效果, 花了不少 token 來處理我的文章… 不過慶幸的是，這 token 花得很值得啊，這同樣會寫一段專門來談這主題 (下一篇)。

**(3) 善用 AI 工具來清理基礎結構的問題, 簡化整體的運作流程**

這段講白了就是清掉以前欠的技術債而已。為了這次的 side project, 花點時間還債是必要的, 包含殘留的 HTML (我有 60% 的文章還是 HTML, 沒轉成 Markdown), 以及其它很惱人的小問題 (中文檔名, 圖檔路徑亂七八糟等等), 這些問題不解決, 會影響以後文章發行的 pipeline。

因此，我選擇用 AI "一次性" 的重構來搞定這些問題。除了內容，我同時也處理了 repo 的結構, 清理了不再需要的圖檔, 也把路徑跟驗證的環境 ( local run - github pages ) 通通都整理好了, 現在寫文章感覺舒暢多了, 這部分有很多實際操作的心得, 也包含 vibe coding, 這段我會當作心得分享的角度來寫 (下一篇)。


# MCP != API, MCP 要用工作流程的角度設計

<!--
先講你把 MCP 三個原語（Tools/Resources/Prompts）對映到讀者的「典型任務」與你背後的理由；這裡強調關係與因果，不是列點而已。

在列出工具與資源時，同步交代「為何需要它」「不用會怎樣」「它和其他元件的互文關係」；例如 GetInstructions 為何獨立成 tool、SearchChunks 為何跟 synthesis 綁在一起。
-->

架構師的角色當久了, 很多事情都習慣從 TOP -> DOWN 的角度著手了。既然確定最終服務要用 MCP server 的方式呈現, 那第一件事就是決定 MCP 的規格設計吧。這邊我特別提一下，如果講 MCP, 其實這標準出來不到一年 ( 2024/11 由 Anthropic 推出第一版 )，沒有太多成熟的案例可以參考 (後面我挑了兩個我覺得設計很棒的案例)，不過如果把範圍擴大一點，LLM + Function Calling 都算進來的話, 其實能參考的資源還不少。

我先把最終我設計的 MCP 規格貼在這邊, 各位讀者心裡有個譜, 可能看後續的討論能更快進入狀況:

- GetInstructions, 取得使用說明
- SearchChunks, 依條件查詢符合的文字片段
- SearchPosts, 依條件查詢符合的文章清單
- GetPostContent, 取得指定文章的內容
- GetRelatedPosts, 取得指定文章的相關文章清單

接下來，就從這些參考資訊開始吧...

## 參考1: 從 API First 到 AI First

首先, 我去年在談 "從 API First 到 AI First" 這場演講裡 (還有文章)，其實都提到這個觀點。我順手整理一下:

(有開發這個 MCP 實在是太棒了, 以下是靠 GitHub Copilot + 我自己的 MCP 整理的)

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


## 參考2: iHower 電子報 #31

其實這邊都是介面設計的原則，不過當時我的理解只到 "探討給 AI 使用的 API，有什麼地方要注意" 這種層次而已，基本上仍然是我們認知範圍內的 API ... 不過，隨著越看越多 MCP 的設計原則，我發現不完全是這麼回事。另一個更激進的想法，則是 "Workflow First" 的設計:

> "  
> 別用 API 的角度來設計 MCP，要從工作流程來設計。  
> "

這邊我大推 iHower 的粉專, 他是少數幾個對 AI 軟體開發很專精的人, 他篩選出來的內容都很值得閱讀, 我列舉幾個他分享的參考素材:

- [電子報 #31](https://ihower.tw/blog/13197-aie-openai-gpt-5), 總篇集, 這期包含很多 MCP 設計相關主題
- 推薦文章 - [Block's Playbook for Designing MCP Servers](https://engineering.block.xyz/blog/blocks-playbook-for-designing-mcp-servers)

其實，把 Agent 擬人化的話, 未來就是使用者 (人) 跟 Agent (人) 互動為主的操作方式。而 MCP 則是使用者授權給 Agent 使用的 "工具"，讓經過訓練 ( 已包含正確的 instructions ) 的 Agent 能更有效率的用使用者的 "工作流程" 來替他完成任務。工作流程基本上都跟使用者自己操作一樣，但是換成 Agent + MCP, 會有 10 ~ 100 倍的效率，如此而已。

因此，我抓兩個重點，一個是 使用者 要 "授權" 指定的 MCP 給 user, 這是重要的步驟；而 MCP 的設計也必須符合工作流程的要求，這樣 prompt 才會直覺不需要額外轉換邏輯，操作會更直接精確，不會有幻覺或是意料之外的行為發生，這才是個好的設計。



## 參考 3: Workflow First, 實際使用情境分析

即使看完這些文章或是指引，我相信大部分的人還是搞不懂什麼叫 "Workflow First" 的設計吧? 別在意，我自己也是想半天才想通的。接下來這段，我就用我自己部落格使用的情境當作範例，說明一下我的 "工作流程" 是什麼，以及如何從中 "判別" 出需要的 "工具" 是什麼，進一步把他變成 MCP tools 的規格的過程。

其實過程很簡單, 把實際的使用過程攤開來看就好了。設想大家會怎麼使用我的部落格? 不外乎這幾種需求:

1. **訂閱**, 把我部落格當作雜誌來看, 我寫什麼就看什麼。這個現在就做得很好了，不大需要額外處理。
2. **解答**, 有特定問題 ( question ) 時想要來我部落格找相關資訊。例如幾個我長期關注的主題, 像是分散式系統、平行處理、微服務架構、AI 應用開發等主題, 有時只有模糊的印象, 想要來我這邊找到明確且專業的說明
3. **解題**, 有特定的難題 ( problem ), 想要來我的部落格找找有無合適的解決方案。"解答" 跟 "解題" 很容易搞混，用英文來說就是 question vs problem. 對於 question 就是有很明確的答案 (answer) 的情況，而對於 problem 則需要因地制宜的找出合適的解決方案 (solution)。所以 "解題" 這情境，就如我常常寫的架構師觀點，或是架構面試題就屬於這類。我都會定義常見但是很棘手的情境，然後分析背後關鍵因素，並且提供範例跟整個開發過程來示範如何解題。
4. **學習**, 想要學習怎樣才能當個架構師，想要學好特定的主題，或是某個特定的技術或是概念, 例如我寫過一系列的 .NET CLI + Pipeline 的文章, 以及平行處理的文章, 需要有系統的從動機 => 問題 => 學習目標 等循序學習，針對特定技術的學習內容

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

這段 "分析" 過程中，我刻意把一些動作抽取出來了，上文的 ( ) 就是這些動作。如果整段工作流程我都希望讓 Agent 來代勞，那麼 ( ) 內的動作就是我需要授權給 Agent 使用的工具，Agent 有了這些工具就能直接執行必要的動作。工具的設計越貼近這工作流程，Agent 要負擔的 "操作工具" 的障礙就越小 (相對的就是 Agent 的應變能力越好)。

因此，按照上面描述的 Workflow, 我的 MCP 很直覺的就該提供這些 Tools 的規格了，我條列如下:

**MCP Tools**:
- ```GetInstructions()```  
使用說明書, 給 agent 參考的 instructions. 因為需要包含動態資訊, 同時也參考了 Shopify 的 MCP 設計方法, 因此我特地做成 Tool, 而不是只放在 Description 裡。
- ```GetPostContent(postid, synthesis, position, length)```  
查詢指定文章 (須提供 postid) 的資訊
- ```GetRelatedPosts(postid, limit)```  
查詢指定文章的相關文章清單 (須提供 postid)
- ```SearchChunks(query, synthesis, limit)```  
按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文字片段
- ```SearchPosts(query, synthesis, limit)```  
按照條件 (query), 指定應用方式 (synthesis) 查詢符合的文章清單


這的確就是我第一版 (目前版本) MCP 運作的規格。有興趣的可以裝起來試用看看，大部分的 Agent 都能看到過程中呼叫了那些 Tools, 你可以實際體驗看看使用的感受跟成果。

在繼續深入挖掘 Tools 設計技巧前, 我就拿這設計規格，實際跑幾個使用情境給大家看成果吧。看完我相信你會更有感，之後再來繼續往下探討設計方法。




# DEMO: 三個實際的案例示範

<!--
個案例用一致的質化模板（見下一節），以「觀察→推論→修正→再觀察」來記錄 Agent 互動與你介入的判斷；像 Claude 的例子可展示它如何先讀 GetInstructions 再呼叫 SearchChunks，以及你如何用交叉對照檢核。
-->

這段我就用我實際操作 Agent + MCP 解決的三種類型的任務示範吧。我簡單說明一下這三個 demo 個別在做什麼:

**問答對話 (chat with my blog)**:
就是最單純的情境, 你把 Agent 當作一個熟背我每篇文章的書僮, 你想找什麼就直接用問的, 他都能回答你。基本的 question / answer 需求應該能能滿足。這個案例我用 ChatGPT plus 來示範，你可以直接問要掌握微服物分散式交易，有哪些開發人員需要具備的能力?

**整理我的部落格演進史**:
我部落格從 2004 寫了第一篇開始，第一個版本就是我自己用 ASP.NET 開發的 side project, 從這時開始我就不斷重複 "改系統" -> "寫心得" -> "改系統" ... 的循環。過程中我換過五六套部落格的系統了，每次都有幾篇文章在說明過程跟心得，也散落在好幾篇文章內。這次是 20 周年紀念 (咦?)，我想從多篇文章之中按照時間續把過程列出來，這種任務找 Agent 來代勞最合適了。這個案例我用 vscode + github copilot 來示範, 整理好的內容就直接替我編輯這篇文章的 markdown 了，整個操作一氣呵成，效率大增。對比九年前，我做這件事得自己 Google 自己的文章，然後再花一段時間自己編排整理...

**按照我文章敘述的架構來寫 code (vibe coding)**:
我的文章都會分享我自己在實際工作上碰到的 case study, 我都會把問題濃縮, 只保留核心的關鍵, 並且完整的用 PoC project 的方式實作出來證明問題能被解決。我覺得這些過程跟範例，正好是 vibe coding 必要的規格跟敘述素材。這段我就是直接拿我談某個主題的文章，直接透過 MCP + Coding Agent 來把這 solution 應用在實際的開發專案上。這段我用 vscode + github copilot 來示範。



## 案例 1, 直接對話的應用 (ChatGPT)

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



## 案例 2, 整理我的部落格演進史

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

(2008) **系統移轉: 改用 BlogEngine.NET**
- 因 Community Server 商業化限制決定轉移
- 採用 BlogML 格式進行資料轉移
- 解決圖片連結、站內連結、站外連結等轉址問題
- 開發自訂匯入程式補齊缺漏資料
- 新增 View Count Extension 與 Secure Post Extension
- 參考文章: [換到 BlogEngine.Net 了!](https://columns.chicken-house.net/2008/06/17/switched-to-blogengine-net/)

(2008-2015) **BlogEngine.NET 客製化與擴充**
- 開發 Secure Post Extension (密碼保護文章)
- 整合 Google Ads 廣告系統
- 整合 FunP 推推王社交分享功能
- 開發 PostViewCounter Extension
- 客製化版面設計與 CSS 調整
- 參考文章: [BlogEngine Extension: Secure Post v1.0](https://columns.chicken-house.net/2008/09/06/blogengine-extension-secure-post-v1-0/)

(2015) **短期嘗試: WordPress**
- 測試 WordPress 作為替代方案
- 處理大量舊網址轉址問題 (Apache RewriteMap)
- 因維護成本考量最終放棄
- 參考文章: [Case Study: BlogEngine -> WordPress 大量(舊)網址轉址問題處理](https://columns.chicken-house.net/2015/11/06/apache-rewritemap-urlmapping-case-study/)

(2016) **系統移轉: 改用 Jekyll + GitHub Pages**
- 採用最低科技路線，改用靜態檔案
- 選擇 GitHub Pages 作為 Hosting 方式
- 實現 "Blogging as Code" 概念
- 大幅降低維護成本與系統複雜度
- 改用 Markdown 撰寫文章
- 參考文章: [Blogging as code !!](https://columns.chicken-house.net/2016/09/16/blog-as-code/)

--

其實還蠻正確的啊, 即使是九年前, 我也還記得寫那段的過程。就算是我自己寫的文章, 在當時我仍然得透過 Google 來找我自己的部落格文章, 花了些時間才能整理出這樣的內容。現在，透過 agent, 短短一分鐘就搞定這問題了。看到科技的進步了，生成式 AI 在處理文字資訊上真的是不同世代的技術，過去要花一個晚上的事情，現在兩三分鐘就能完成。

雖然我一開始就說, 我不會放棄自己寫文章的習慣, 也不會改用 AI 替我生成文章。但是, 靠 AI 幫我整理資訊, 這類任務本來就是我不喜歡做的，因為不會表達出太多我要傳達的心法，但是為了論述過程卻又不得不做的苦工，這種任務交給 AI 最合適了啊..., 諸如此類的應用，在寫文章或寫文件應該很常碰到，我就示範到這裡，其餘延伸的應用就交給各為自己去挖掘。


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




## 案例小結

其實，還有其他的應用，但是礙於篇幅 (實在太多了) 我就賣個關子，之後當作零星的主題，直接在 FB 上面 PO 文探討吧! 其他有 resource 的應用 ( 直接在 vscode 用 post uri 就能叫出文章原始內容 ), 或是在 agent mode 下直接將文章加入 ( add context ) 附件參考。

另外我也試了從部落格當作知識庫，產生整份學習計畫，甚至生成測驗考題，以及生成實作題的 Handson Labs 講義等等，這些都很有趣，而且都能精準地抓到當時我寫這些文章的核心概念，這些案例大家可以自己試試看，我就不一一示範了。




# 參考 Shopify / Context7 的 MCP 設計規格
<!--
用 Shopify.dev 與 Context7 做「有/沒有」的反事例對照，說明為何你要在自己 MCP 中引入 gating / validation 與「先 chunks、再拉原文」的節奏。
-->


最後，談 MCP 的設計，我想談談兩個我覺得做的很棒的案例, 一個是我一直在關注的 Shopify.Dev MCP, 另一個是開發社群討論度很高的 Context7 MCP.

其實這兩套 MCP 都出來有一陣子了，規格也都經過調整，但是使用起來都無痛轉移... MCP 不像 API 有 "必須" 向前相容的壓力啊，使用起來很無痛 (無感)，你只會覺得改版後好像效果變好了而已。這兩套都是面對開發人員，都是改善開發文件的檢索與使用方式，跟我想做的領域很接近，因此我才拿這兩個 MCP 當作研究學習的對象。我在 Shopify.Dev 這個 MCP 的設計方式, 看到很多其他大神分享的 best practice 實際應用的方式, 也算是一種觀摩。


再次引用 iHower 的 PO 文: https://www.facebook.com/share/p/1CpGR9kMUx/ :

節錄其中兩段:

--

**工具太多成為核心挑戰**  
當你有幾百甚至幾千個工具時，AI 會選擇困難。各家提出不同解法:
- **Block 的洋蔥式架構**: 把工具分成三層 - 發現層、規劃層、執行層。先用一個工具來探索有哪些 API 可用，再用另一個工具取得詳細參數，最後才執行。有點像是「先問有什麼菜 → 再問怎麼做 → 最後才點菜」的概念。

相關演講:
- Too Many Tools? How LLMs Struggle at Scale - MCP Talk w/ Matthew Lenhard
- Full Spec MCP: Hidden Capabilities of the MCP spec - Harald Kirschner, Microsoft / VSCode

**從工具思維到 Agent 思維**  
這是重要的開發典範轉移: 不要只是把 API 端點一對一變成 MCP工具！你會有三個用戶: 終端用戶、client app 開發者，還有 AI 本身。要思考使用者會問什麼問題，然後設計適合的工具介面。

MCP-first 開發: 與其先做 REST API 再包裝成 MCP，不如一開始就為 AI 設計。當 AI 成為主要使用者時，系統設計的思維要完全改變。

相關演講:
- Scaling Enterprise MCP: Best Practices, Nexuses, and Security with Pat White
- MCP Is Not Good Yet — David Cramer, Sentry

--

這邊提到兩個概念, 發現 / 規劃 / 執行分層, 以及思考使用者會問什麼問題, 然後設計合適的工具給 Agent 使用。我覺得 Shopify 完全做到這些原則, 這是我用 MCP Inspector 逆向工程看了幾次才體悟出來..., 原來 MCP 不是 API, 指的是這麼一回事。

接著，就開始來看看實際的設計案例吧! 看看 Shopify.Dev MCP / Context7 MCP 是怎麼設計的


## MCP 設計參考 1: Shopify.Dev MCP

對 Shopify.Dev MCP 有興趣的可以直接看官網介紹，網址在 [這邊](https://shopify.dev/docs/apps/build/devmcp), 我直接摘要前面的簡介:

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

其中, ```learn_shopify_api``` 很明顯, 就是發現層的設計。他其實沒做什麼事情, 就是傳回一段 instruction 給你而已, 但是你一定要做這動作, 因為傳回的 instruction 裡面藏了一個 conversationId... 這就類似 session id 的設計, 往後你帶著這個 id, 其他 tools 就會知道你 **已經照規矩學習過了** ...。

這樣設計，除了 "引導" Agent 要先取得 instruction 之外, 用更強硬的手段要求 Agent 一定要這樣做。某種程度已經可以擋掉亂來的 Agent 了。確保 Shopify 官方的 instruction 已經保留在 context window 內, 就更能預期後續的行為了。來看一下這個 MCP tools description 怎麼寫的 (內容很長，我只擷取頭尾):


```markdown

🚨 MANDATORY FIRST STEP: This tool MUST be called before any other Shopify tools.

⚠️  ALL OTHER SHOPIFY TOOLS WILL FAIL without a conversationId from this tool.
This tool generates a conversationId that is REQUIRED for all subsequent tool calls. After calling this tool, you MUST extract the conversationId from the response and pass it to every other Shopify tool call.

🔄 MULTIPLE API SUPPORT: You MUST call this tool multiple times in the same conversation when you need to learn about different Shopify APIs. THIS IS NOT OPTIONAL. Just pass the existing conversationId to maintain conversation continuity while loading the new API context.

// 中間略過

```


實際呼叫一次看看, 會得到這樣的回應 (我只節錄 text 的部分):

```markdown

🔗 **IMPORTANT - SAVE THIS CONVERSATION ID:** 5f53b794-e408-4346-9915-55699d92f68e
⚠️  CRITICAL: You MUST use this exact conversationId in ALL subsequent Shopify tool calls in this conversation.
🚨 ALL OTHER SHOPIFY TOOLS WILL RETURN ERRORS if you don't provide this conversationId.
---
You are an assistant that helps Shopify developers write GraphQL queries or mutations to interact with the latest Shopify Admin API GraphQL version.

(以下略)

```

再次看到, Shopify 很巧妙的把 conversationId 藏在 markdown 裡面, 因此唯一能順利運作的條件是:
1. agent 有正確呼叫 learn_shopify_api tools
1. (1) 的回應有被放進 context window, 並且 LLM 有 "認真看", 正確的抽取出這段 id
1. 往後呼叫其他 tools 時, agent 有照規矩帶上這個 id

看起來, 這設計已經很巧妙地閃過不少地雷了。我如果沒看到這作法，我可能還在傻傻的寫更多 prompt 來 **跪求** LLM 拜託照著我的要求做 XDDD (這不是都反過來了嗎)

第一步做對之後, 剩下的就容易的多。接下來的 tools 設計也有他的巧思, 我接著介紹跟查文件相關的這兩個 tools:

- search_docs_chunks (conversationId, prompt, max_num_results)
- fetch_full_docs(conversationId, paths)

顧名思義, 第一個 tool: search_docs_chunks 是用來查文件, 下了條件後會傳回符合的片段 (chunks) 內容。如果你感興趣的話, 下一個 tool: fetch_full_docs 則可以根據文件名稱 (path) 來取得完整的文件內容 (用 markdown, 而非 HTML)

這種做法, 讓 agent 能更靈活的操作 Shopify.Dev 的官方文件。一來看的出來 search_docs_chunks 背後是向量搜尋, 不需要依賴外部的 search engine, 能更精準的執行 RAG, 二來 fetch_full_docs / search_docs_chunks 都是傳回 markdown, 這種格式的資訊密度遠高於 HTML, 少掉很多 "格式" 上面的雜訊干擾, LLM 解讀也更精確。


再來看第三組 tools:

- introspect_graphql_schema(conversationId, query, filter, api, version)
- validate_graphql_codeblocks(conversationId, api, version, codeblocks)

這兩個 tools 是針對 GraphQL API 的設計, 這是 Shopify 的核心服務, 也是開發者最常用的服務。introspect_graphql_schema 是用來查詢 GraphQL schema 的, 可以根據你的要求 (query) 及其他附加參數, MCP 就會將符合你要求的 "結果" schema 回給你。這結果等於已經先幫你把查詢的 select 部分先準備好了, 不管查詢怎麼寫, 至少傳回的欄位已經先替你準備好了。

拿到 schema 後, 接下來應該會有一段 developer 跟 agent 的往返對話, 這標準的 graphql 語法, 大部分的 LLM 應該都能勝任。而 Shopify 則在最後加了一到防護, 就是最後一個 tool: validate_graphql_codeblocks。這個 tool 是用來驗證 agent 產生的 GraphQL code block 是否正確的。這樣設計, 就能確保 agent 產生的 code block 一定符合規範, 不會亂寫一通。


## MCP 設計參考 2: Context7

這是另一個最近討論度很高的 MCP: Context7, 它的作用是通用的 "開發文件" 檢索資料服務。因為討論度很高，大家可以直接 Google 看其他人怎麼運用他的心得跟感想，我這邊就單純挖掘他的 MCP 本身設計精神就好。

// context7 討論

https://github.com/upstash/context7

我節錄官網介紹:


--

**❌ Without Context7**
LLMs rely on outdated or generic information about the libraries you use. You get:
- ❌ Code examples are outdated and based on year-old training data
- ❌ Hallucinated APIs that don't even exist
- ❌ Generic answers for old package versions

**✅ With Context7**
Context7 MCP pulls up-to-date, version-specific documentation and code examples straight from the source — and places them directly into your prompt.

Context7 fetches up-to-date code examples and documentation right into your LLM's context.

1️⃣ Write your prompt naturally  
2️⃣ Tell the LLM to use context7  
3️⃣ Get working code answers  

No tab-switching, no hallucinated APIs that don't exist, no outdated code generation.

--

以上是官網的介紹，實際上大家的使用心得也是一片好評，他是真的有做到他敘述的使用場景。然而這些神奇的功能背後，Context7 提供了那些 tools? 意外的 (看完 Shopify 的設計之後我就不意外了) 其實只有兩個很簡單的 tools, 我一樣截錄官網的說明:

--

Context7 MCP provides the following tools that LLMs can use:

**resolve-library-id**:
Resolves a general library name into a Context7-compatible library ID.
- libraryName (required):  
The name of the library to search for

**get-library-docs**:
Fetches documentation for a library using a Context7-compatible library ID.
- context7CompatibleLibraryID (required):  
Exact Context7-compatible library ID (e.g., /mongodb/docs, /vercel/next.js)
- topic (optional):  
Focus the docs on a specific topic (e.g., "routing", "hooks")
- tokens (optional, default 5000):  
Max number of tokens to return. Values less than 1000 are automatically increased to 1000.

--

翻成白話，只有兩個 tools, 一個 resolve-library-id 是讓你查詢文件庫 ID 用的, 另一個則是到指定的文件庫找你要的主題, 會傳回官方文件特定的部分。其實這是很標準的 RAG 檢索結構。基於好奇，我把這個 MCP 掛上 MCP Inspector 來測試一下:

我先用 resolve-library-id 來查詢: "shopify functions" .. 得到這樣的回應:

```markdown
Available Libraries (top matches):

Each result includes:
- Library ID: Context7-compatible identifier (format: /org/project)
- Name: Library or package name
- Description: Short summary
- Code Snippets: Number of available code examples
- Trust Score: Authority indicator
- Versions: List of versions if available. Use one of those versions if and only if the user explicitly provides a version in their query.

For best results, select libraries based on name match, trust score, snippet coverage, and relevance to your use case.

----------
- Title: Shopify Functions
- Context7-compatible library ID: /websites/shopify_dev_api_functions
- Description: Shopify Functions allow developers to customize Shopify's backend logic during checkout by running custom code for specialized features like custom delivery options, new discount types, and cart/checkout validation.
- Code Snippets: 643
- Trust Score: 7.5
----------
- Title: Shopify Function Examples
- Context7-compatible library ID: /shopify/function-examples
- Description: This repository contains public examples of Shopify Functions, used by the CLI for generating extensions and demonstrating various functionalities.
- Code Snippets: 117
- Trust Score: 9.2

(以下略)
```

再次印證了這是為了 "工作流程" 而設計的 "工具"，跟傳統認知的 "API" 重新封裝成 MCP 的意圖完全不同。比起 API 偏好的 Json 結構化資訊, 給 Agent 看的訊息更偏好用 LLM 容易理解的 Markdown, 雖然結構化的程度不如 Json, 但是 markdown 的各種標示, 更有助於讓 LLM 理解他的意圖與重要性。

上面的回應，其實傳達了兩個部分的意圖:
- 就地傳回 "使用規則" (instructions), 讓 Agent 知道這個工具應該怎麼被使用
- 傳回 "符合查詢的結果" (results), 讓 Agent 知道有哪些 ID 可用, 以及這些 ID 與查詢的相關性 ( trust score )

我想，這就是 "為了 workflow 設計" 的最大差別了。如果是資料庫檢索的 API 我絕對不會這樣設計，對 API 而言，使用規則這件事根本不用每次都傳回，而是寫在文件上讓開發人員看的資訊啊，開發人員看懂了之後，自然要用 "合適" 的方式呼叫 API。

然而這 tools 不是 "API", 是個要直接讓 Agent 使用的 "工具"，Agent 擁有比人類還高的資訊處理能力, 可以在一瞬間看到回應的 instruction, 理解後馬上處理後面的任務。在 tool response 內直接夾帶 instruction, 在各種 MCP 的設計上都很常見。因為 MCP 是為了讓 "工作流程" 能順利執行的 "工具"，不是單純的 "API"。


緊接著, 用第一次呼叫取得的資訊, 繼續呼叫第二個 tool: get-library-docs...

我帶入的參數:
- context7CompatibleLibraryID: /shopify/function-examples
- topic: 用 admin api (graphql) 查詢商品 (product) 資料, 要包含 admin 身分認證
- tokens: (略)

得到的回應:

```
================
CODE SNIPPETS
================

TITLE: Authenticate Admin and Query Products with GraphQL
DESCRIPTION: Demonstrates how to authenticate an admin request using the Shopify API and query product data using GraphQL. It fetches the first 25 products and extracts their titles and descriptions.

SOURCE: https://github.com/shopify/function-examples/blob/main/sample-apps/delivery-customizations/README.md#_snippet_6

LANGUAGE: javascript
CODE:

--
export async function loader({ request }) {
  const { admin } = await shopify.authenticate.admin(request);

  const response = await admin.graphql(`
    {
      products(first: 25) {
        nodes {
          title
          description
        }
      }
    }`);

  const {
    data: {
      products: { nodes },
    },
  } = await response.json();

  return nodes;
}
--

(以下略)

```

第二個工具，根據我提供的 library id + query, 就檢索出符合我要求的 example code 了。其實這就是把過去我們 "真人" developer 在查文件寫 code 的過程。你會先 google 看看某個套件或開發框架的官網在哪邊，然後再用它的 search 找到你要的主題。找到文件或 sample code 後, 會直接複製貼上, 或是理解看懂後改成自己要的樣子。

而這一切過程，就是當今 coding agent 想要代替你執行的工作流程。Agent 依靠背後的 LLM 有強大的 coding 與理解能力, 這些 Tools 則扮演了 Agent 的手腳, 有效率的協助 Agent 完成任務。





## MCP 應用的想像 - 下個世代的 API

視角拉遠一點，我覺得在未來的世界，MCP 會是 Agent 時代的 API。過去風行 10 年的 SaaS, 標榜的是軟體服務開箱即用, 除了有 APP / Web UI 之外，規模大的 SaaS 也會強調跨服務的整合, 培養自己的 EcoSystem, 依靠的都是暴露自身服務的 API 來達成。**對於 SaaS 來說, API 是必要的武器, API 的品質也是 SaaS 能否長遠發展的重要指標。**

因為當時強調的都是 "軟體即服務"，服務就像水電一樣，管線鋪好水龍頭打開就能用。管線就是 API ...，鋪設過程就是整合 (串接 API)。而現在 Agent 時代，AI 自己會去讀懂 Tools Spec, 自己會執行 Tool call, 整合這段的工程省掉了, 而要被呼叫的 Tools ( API ) 的提供方式就變成更適合 Agent 的 MCP。未來的 SaaS, 關鍵不再是有沒有 API (這要等別人來串接)，而是有沒有 MCP，對方有 Agent 只要設定好就能直接使用。

我覺得這轉變，已經看的到方向了，MCP 也 (意外的) 獲得各大廠的支持，看來變成標準規範已經沒有懸念了。未來，我覺得最關鍵的就是軟體產業的轉型。我最近在幾個場合, 都在聊這個想法。軟體發展, 從 "套裝軟體" (工具買斷，安裝使用)，進展到 "服務訂閱" (工具訂閱，立即可用)，而未來會是什麼? 我大膽亂猜一下，我會覺得是 "工作流程訂閱" (賦能使用者的 AI Agent，立即可用)。


**因此，對於未來軟體公司 (是否還是 SaaS ?) 而言，我覺得 MCP 會跟過去的 API 一樣，也是 SaaS 的必要武器了。MCP 的品質也會是 SaaS 能否長遠發展的重要指標。**

這改變的前提是使用者的習慣，已經轉移成 Agent 導向的工作方式了。到目前為止 ( 2025/09 ), 這變革在軟體開發領域已經發生了, 其他領域還沒這麼徹底。我舉幾個事實來說明軟體產業已經走到什麼地步了，正好也可以當作其他領域未來發展的預測依據。

先來看看，在開發工具的領域，過去兩年發生了什麼變化?


直到兩三年前，不管你是不是 Microsoft 生態系的使用者，這句話大概都有聽過: 

> "
> Visual Studio 是地表最強的 IDE, 沒有之一  
> "


不過，從世人發現 AI 能夠替你寫 code 之後，接下來的這兩年，已經沒有人在談論 Visual Studio 了, 大家都在談 AI IDE ( vscode + github copilot, cursor, windsurf 等等 )。大家的開發方式, 談論主題已經不是怎麼寫，用哪個工具或套件了，談的是怎麼 vibe coding, 怎麼讓 agent 能正確的替你工作... 過去盛行的 project template, code generator 快速地被 AI coding 取代, 還有像是 stackoverflow.com 這種提供大量 code snippet 的問答網站流量雪崩式的跌落, 都是典範轉移的證據...

然而 cursor 這類 vscode 輕量化的 IDE + AI coding agent 的 IDE 紅了一年, 最近又開始有新的工具冒出來了, 開發者的社群開始轉向純粹的 CLI 版本的 coding agent. 這趨勢其實很明顯, 從大型的 IDE (visual studio) -> 小型且靈活的 IDE (vscode + agent) -> 更進一步的 CLI 版本的 coding agent，代表著手動處理程式碼 (IDE) 的比重快速下降，而透過 Agent 處理程式碼的比重則快速拉升，才造就這樣的現象。這兩年的變化，代表的是 Software Developer 已經完全能接受 Agent 的使用方式了，因此也帶來工作流程的改變 (一瞬間，因為寫好文件能讓 Agent 有效率的工作，過去大家很討厭的寫文件，現在突然變成顯學了... 看看 Kuro / Spec Kit ...)

軟體開發領域，是站在 AI 發展的海嘯第一排，其他領域遲早也會走上這條路的。因此現在在軟體開發工具市場發生的事情，其實可以當作借鏡，讓大家可以具體的想像軟體業的未來樣貌。未來 Agent 會是主流的使用型態, 因此各大軟體服務都會面對怎麼跟這些 Agent 共存? 我覺得答案就是提供 MCP 了, 各大軟體業者都必須想盡辦法，讓使用者能無縫的透過 Agent 使用你的服務。

--

因此，最後來回顧一下我在 Facebook 貼的這兩篇 PO 文, 講的是同一件事, 只是在 FB 我沒有空間談前面這些觀察，只是講出我的看法。現在我把這些心得補在這裡，正好交代完整個思考脈絡:


* 2025/08/20: [Code w/ Claude - MCP201, The power of the protocol](https://www.facebook.com/share/p/1XNstkb18f/) Part 1
* 2025/09/04: [Code w/ Claude - MCP201, The power of the protocol](https://www.facebook.com/share/p/1ZeTmqxJMu/) Part 2


"工欲善其事，必先利其器"，這句話放在 Agent 身上, 我覺得一樣適用。挑選 / 開發合適的 MCP, 這廣大的 "工具" 市場，我相信是未來軟體發展的重要方向。




# 總結
<!-- 
將公開測試 URL 前移，並以「第一次成功體驗」為主軸（而不是安裝步驟），讓讀者先感覺到關係變短。
-->

<!--
寫到這邊，我的心得是: 

我總算理解前面提到, 要 "按照工作流程來設計工具" 的意思了。寫這段的時候，正好在 FB 看到 iHower 的這篇 PO 文:

https://www.facebook.com/share/p/17CwzL46FZ/

內文提到 (截錄片段):

>  
> 看到 LangChain 團隊分享了一個很實際場景的實驗: 如何讓 Claude Code 變成專精特定領域的 coding agent。
> 現在的 coding agents 對主流框架很熟悉，但碰到公司內部 API、小眾框架或新版本的函式庫就gg了。作為 LangGraph 和 LangChain 的開發者，他們當然希望 AI 能寫出高品質的 LangGraph 程式碼。
> 於是他們做了個實驗，測試四種配置:
> 1. 原版 Claude Code (什麼都不加)
> 2. Claude + MCP 文件工具 (指 LangChain 自己出的 mcpdoc 工具)
> 3. Claude + Claude.md (精心撰寫的 LangGraph 指引文件)
> 4. Claude + MCP + Claude.md 全套組合
> 效果排名: 4 > 3 > 2 > 1
> 這個 mcpdoc 工具提供兩個功能: list_doc_sources 抓取 llms.txt 文件的網址目錄，fetch_docs 根據網址抓取文件內容。  
>

看起來也是類似的作法, 透過 MCP 有效率的按照情境讀取對應的文件, 讓 coding agent 能更精準地回應開發者的期待。各種特定領域的 coding agents 若有個能熟知該領域的開發資源 MCP 輔助, 即使不是那麼普及的領域, AI Agent 也能夠勝任。

我自己擅長的文章主題，也算是某個 "冷門領域" 吧? 所以我自己設計一個 MCP server 來用也是很合理的 XDD

寫到這邊, 不得不佩服 Shopify 的工程師設計 MCP 的功力。短短的五個 tools, 就把整個 Dev Site 的工作流程都變成 MCP 了。前面提到的發現 / 規劃 / 執行三層架構, 這邊也完全體現了，如果有在開發 Shopify 的朋友，推薦試試看，你會發現搭配 coding agent 的開發體驗完全是另一個層次。

-->

交代完 side project 的動機, 應用示範也講了, 業界的案例研究也講了, 最後我來說明一下你可以怎麼使用我的 MCP server!


## 我的 MCP 使用說明

首先, 我的 MCP 發布資訊很單純, 只有一個網址:

Transport: Streamable HTTP
URL: https://columns-lab.chicken-house.net/api/mcp/ (結尾的 / 請不要省略)

這個版本不需要登入, 也不需要 APIKEY, 只要支援 HTTP 的 MCP Host 都可以使用。如果你是 developer, 我推薦你用 vscode, 如果不是 developer, 我推薦你使用 ChatGPT Plus (要訂閱用戶才支援, 目前 MCP 支援是 Beta, 要手動開啟)

在 vscode 要安裝 MCP server 很簡單:

F1 -> MCP: Add Server... -> HTTP -> 輸入上面的 URL -> 取名字 -> OK

這樣就完成了。如果你想強制 Agent 先 call tool: GetInstruction 來正確啟用 MCP 的話 (正常情況下 Agent 會自己判斷)，可以這樣要求:

/mcp GetInstruction

![alt text](/images/2025-09-16-chat-with-my-blog/image-4.png)

Agent 就會照辦了. 而呼叫過這個 tool 後, Agent 就等同 "閱讀過 MCP 的使用說明書了", 後續你可以直接問他，提到安德魯的問題，應該都會觸發 MCP 來回答。

你可以測試這兩個問題:

> 安德魯的文章中, 提到那些微服務處理交易的重要技巧?









## Side Project 的觀察與心得

雖然這次我的部落格改造，這篇只交代了前半段，不過至少把 MCP 相關的部分寫完了。

這段我總結一下我的心得:

目前 Agent 的最大罩門, 就是 context window 的大小限制了。模型能否處理是一件事, 過大的 context 是否還能抓到重點則是另一件事 (我有 PO 過研究報告)。有時候工作效率的好壞，就在於過程中是否有 "爆量" 的資訊跑進來需要處理? 如果你的流程跟工具都控制得當沒有這種狀況發生，你就能有很好的工作效率。

這回，我在 MCP 的設計上，也看到了這樣的設計巧思。從 Shopify 的案例看到, learn_shopify_api 扮演流程管控的角色，避免了 Agent 走錯路；而 search_docs_chunks / fetch_full_docs 則代表了先檢索再讀取的步驟，其實這過程都是要精準的掌控 "只有必要的資訊才會被帶入 context window" 的思維。其實這不就是 Context Engineering 的極致表現嗎? 將 Context 管理的工作流程做到極致，甚至落實到 MCP 的設計，大概就是這個樣子。

我得到的收穫很多，一個是我開始想通 MCP 的設計手感了；另一個更大的收穫是，我也從這個 side project 看清楚軟體產業未來發展的樣貌 (API First -> MCP First)，這些心得都不是單純看很多文章就能學到的，只有你親自做過一次才能真正體會。

這些體會，還有一大半，就是在內容的處理。要做到極致的 context management, 有時候你必須 "壓縮" 內容。壓縮的手法有很暴力的把十句話濃縮成一句話，也有按照結構重新生成不同型態的應用結構。我採用了把文章轉換成一連串的 FAQ, Solutions 等等型態, 我發現這樣的作法, 遠比單純的壓縮內容來的更精確有效。

如何把這些應用，精巧的整合在一起，這些都是設計上的巧思。下半部，就來談談內容的處理吧! 我覺得 MCP 的設計，跟 Context 的管理，兩者是相輔相成的，在未來 Agent 的時代，兩者都是必要的技巧，缺一不可。

這篇就先到這邊，也請各位期待下一篇!

