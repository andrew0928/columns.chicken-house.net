---
layout: post
title: "Chat with My Blog!"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: false
comments: true
logo: 
---

這篇雖然是談 BLOG, 但其實寫文件都會碰到同樣的問題... 

過去這兩年, 我思考了好幾次這問題: "有了 AI 我還該不該自己手寫文章” ? 

在更早沒有 AI 困擾的年代，我就想過, 要不要寫一些受歡迎的工具文? 後來發現我非常不適合這麼做，因為我碰的東西不夠多，就不是這塊料啊啊啊。同樣各種能 "速成" 或 "量產" 的形式，我發現都不適合我，我只能慢慢磨特定的主題，把背後的原因都挖出來漂亮的解決掉，並且分享其中的脈絡。因此最後，我還是維持一年只產出個位數的文章，但是每篇都是我真正覺得有價值的心得內容。

時至今日，我還蠻慶幸我當年有這樣決定的 (沒有被流量追著跑，刻意去寫些有流量的內容)。有了這想法後, 我開始意識到 AI 也許能帶來一些改變, 

我沒做過統計 (我也不知道怎麼統計 XDDD), 我相信我寫的主題應該有踩到很多人的痛點, 但是因為我寫的形式 (文章太長) 可能導致這些人壓根沒機會看到這些資訊... 這種就是潛在用戶卻無法抓住的困擾啊, 不過現在有 AI 了, 處理文字的能力不再是系統的能力限制了, 我開始覺得, 這問題也許有機會解的掉。

於是, 背後一堆思考過程我先跳過, 最終的答案就是, 我想弄一個我部落格的 mcp server, 來協助讀者們解決這些問題。我希望有個神奇的 mcp 可以讓大家從 "閱讀" 我的部落格文章，變成跟我的部落格 "聊天"，這也是這篇的標題 "Chat with My Blog!" 要表達的意圖。現在有第一版可以給大家體驗看看了! 後面有示範的案例, 有興趣的可以繼續往下看。

<!--more-->

# TL;DR 


動機前言講過了, 接下來聊聊我到底做了什麼... 
上一次為我的部落格大改版, 已經是九年前的事情了 ( 2016/09, Blogging as Code ), 之後就沒有再大改版了, 當然也包含藏了一堆技術債沒處理...

這次改版我想做的, 就是 "讓我的部落格能被 AI agent 好好利用"，期待除了傳統的閱讀方式之外，還能有不同的應用型態。而這次的目標我就訂在要提供我自己的 MCP server, 讓大家能直接在 vscode / chatGPT / Claude Desktop 等工具內, 直接對話我的部落格, 來解決他們的問題。

為了達成我的期待, 我把這次施工範圍分成三個目標:

1. **內容服務化**, 服務要能接上主流的 Agent ( 手段: MCP )
關鍵是 mcp 該提供什麼樣的 tools 來輔助 agent 做好這情境。同時，我也重新調整了部落格的系統架構, 為了體驗一致性, 我希望原部落格網址加上 /api/mcp 就是對應的 mcp server endpoints, 動用了 Azure 上的服務 ( frontdoor + container apps ), 感謝 Microsoft 給 MVP 的使用額度 :D
2. **內容正規化**, 內容要預先轉換成易於使用的格式 ( 手段: LLM 生成新格式 )
目前我的文章都有我自己的思路, 從情境 → 問題定義 → POC → 形成解決方案等過程。這是我認為最大化知識含量的做法，但是不適合最終的應用方式 (有的人立刻就需要答案了)。因此針對應用情境預先整理成合適的型態是必要的，這也是我花最多時間 & Token ($$$) 處理的環節, 再次感謝 MVP 的 Azure 使用額度 XD
3. **流程效率化**, 重新整理工作流程，清除技術債 ( 手段: AI IDE 重構 Repo )
2016 年轉換到 GitHub Pages 時, 很多格式轉移的任務, 其實我都只做到 "可以動" 就好的地步，尤其是舊文章還有 70% 左右都還是 HTML, 圖檔連結壞了也沒有修正。這次為了能有效率的達成 (2), 藉助了 AI Agent + IDE 的幫助 ( 我用 GitHub Copilot ), 也順手把整個 GitHub repo 的內容都重構了一次，做好 (2) 有效率進行的工程基礎

每個目標，對我來說都是大工程啊啊啊啊, 也都各有不同的挑戰要克服。我寫下去一定是一大段，所以這裡先摘要一下，要達成這三個目標，每個目標背後的重點是甚麼:

(1) 用 MCP 來發布服務，關鍵在服務的介面設計。

如果你只把 MCP 當成是 API 的另一種形式，只是把 REST API 重新改成 MCP 發行的話，那就大錯特錯了，這部分算是這次 side project 我最大的收穫，過程中我看了 MCP 團隊成員分享設計理念，也花了點時間研究 Shopify 的 MCP，才算掌握到一些設計的要訣。如果你把 Agent 當作真人看待，MCP 就是你跟他的溝通方式，最好的 MCP 設計，就是以 Agent 要解決問題時順著他的思考脈絡 ( context ) 給予最大的支持，想通這點，我才終於搞懂為何 MCP 會取名為 MCP ( Model Context Protocol )。這後面會有一段專門來談這主題。

(2) 先將內容轉為應用的最合適的型態再做 RAG 的工程處理。

所有的服務中，怎麼 "應用" 永遠都是最重要的事情。如果你沒有對準 "應用" 的情境來挑選技術，那十之八九都會演變成 “為了技術而技術" 的窘境。我去年做過 "安德魯的部落格" GPTs, 當時就是無腦做 RAG，效果有了，但是還沒達到我的理想，感覺就是個書僮幫我找資料而已，還沒到能 "解決" 我的問題的程度。沒到這程度根本不夠格稱為 "Agent" 啊! 因此這次我的做法是對內容預先處理成 “合用" 的型態再進行 RAG (我三月直播談 Semantic Kernel 就示範過這想法了)。什麼叫 "合用” ? 你要先想清楚你要怎麼 "用”, 為了嘗試這些效果, 花了不少 token 來處理我的文章… 不過慶幸的是，這 token 花得很值得啊，這同樣會寫一段專門來談這主題。

(3) 流程的效率源自於基礎結構是否確實。盤點 "文件技術債"，善用 AI 工具逐一清除。

為了流程的效率化，把基礎結構打好是必要的 (不只寫 code, 即使是寫部落格也是如此)。文件的整理是必要的基礎，這影響到你有沒有能力對你的內容作各種後續應用。我的文章內容經過多次系統轉移 (九年前的文章有清楚記載這過程)，其實每次轉移都留下了一點技術債… 例如格式沒轉乾淨 (殘留 HTML 沒轉成 markdown, 殘留的 image 圖檔目錄沒有整理, 錯誤的連結沒有修正, 中文檔名導致各種編碼問題沒有處理…), 這些都是小問題, 睜一隻眼閉一隻眼就過去了, 但是當你希望內容有系統地被重新運用的時候, 這些狀況就都變成例外了。

我希望善用 AI 幫我處理內容，但是我也不希望把 token 花在這些鳥事身上啊! 雖然也是靠 AI 來處理，但是我選擇 "一次性" 的重構來搞定這些問題。我同時處理了 repo 的結構, 清理了不再需要的圖檔, 也把路徑跟驗證的環境 ( local run - github pages ) 通通都整理好了, 現在寫文章感覺舒暢多了, 這部分有很多實際操作的心得, 也包含 vibe coding, 這段我會當作心得分享的角度來寫。對實際操作或工作流程沒興趣的可以跳過這段。

好，簡介都寫完了，接下來就直接進入正題，來聊聊我這次的 side project - chat with my blog 吧~

—

## 1. 內容服務化 - MCP

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

“那我用我最原始的想法來寫文章，讓 AI 生成大家需要的型態來應用就好了”

所以第一次公開這觀點，是今年三月的直播，我在介紹 Semantic Kernel + Microsoft Kernel Memory 應用的時候，我提出來的看法:

“先把文章內容轉換成合適的視角，再進行 RAG 處理，檢索的成效會比直接無腦丟給 RAG 好的多”

我自己簡單嘗試了一下，的確效果很不錯，因此我就繼續往下一步:

我能否直接拿我的文章當基礎，加速其他文章 (文件) 的撰寫? (對應到: 觀點啟發)

我能否直接拿我的文章敘述到的情境，做法，流程等，當作 coding 的 instruction 加速寫出對應的 code ? (對應到: 技術應用)

我能否直接拿我的文章要傳達的概念與精神，做學習，訓練的應用? 例如編排學習計畫，生成訓練素材，生成課前、課後的測驗? 設計 Labs 驗證學習成效? (對應到: 經驗學習)

感覺好像可行，而這些應用的整合環節，不約而同地都指向: 我需要開發一個我自己的 MCP server.. 因為寫文章 (我都用 vscode 寫 markdown, 可以用 github copilot agent mode), 寫 code 我也都用 vscode (同上), 其他的應用我更習慣用 Claude Desktop / ChatGPT 這類 AI chatbot, 如果我能不離開這些工具, 直接整合我的內容完成這些任務, 這就是我想要的理想運用情境。

於是，我就開始動工了，開始打造我自己部落格的 MCP server ( 因此，去年試做的 “安德魯的部落格" GPTs, 還有今年初用 Dify 建立的 Agent, 我都關掉了, 把資源集中在這個 side project 上 )。

上個月，我在 Facebook 分享了這個研討會的錄影: MCP 201, Code w/ Claude, 由 Anthrop/c 提出 MCP 規範的團隊成員現身說法, 描述了它們想像 MCP 的願景, 看完這 20min 的影片，我才算真正搞懂 MCP 要解決的問題, 於是我大概想清楚我該做甚麼了:

MCP Tools, 用來檢索，取得特定條件的內容給 AI Agent, 變成 AI 的 context windows 之一，讓 Agent 生成最終的資訊給我

MCP Resources, 用來取得文章本文，以及生成的內容 ( vscode 甚至可以直接開啟編輯 )

MCP Prompts, 用來指引其他使用者，我應該最熟我的文章結構跟應用方式，與其教你怎麼下 prompt, 我可以透過 MCP 直接給你我預先寫好的 prompt

因此，經過幾版的嘗試與改進，我的 MCP 現在提供這些規格:

Tools:

- GetInstructions()
- GetPostContent(postid, synthesis, position, length)
- GetRelatedPosts(postid, limit)
- SearchChunks(query, synthesis, limit)
- SearchPosts(query, synthesis, limit)

Resources:

- posts://synthesis/{id}.summary.md
- posts://synthesis/{id}.faq.md
- posts://synthesis/{id}.solution.md
- posts://synthesis/{id}.metadata.md
- posts://{id}.md

接下來，與其解釋所有的東西 ( tools, resources ) 怎麼設計, 我更想示範一下使用情境 XDD, 因此後面我就直接示範了, 關鍵設計要點我會提一下…



### 案例 1, 直接對話的應用

一開始先來入門的應用方式就好。

這次的環境我用 Claude Desktop, 因為他的門檻最低 (雖然會看我文章的人應該都有 AI coding agent 能用吧), Claude Desktop 是我認定目前能使用 MCP 門檻最低的使用環境了, 雖然他要安裝 streamable http mcp server 有點囉嗦就是了..

安裝另外再說, 裝好了之後開始跟他聊:




// 問問題 ( Question ), 問解決方案 ( Problem ), 大範圍搜尋檢索 ( Summary ), 這些內容的 RAG 再應用

### 案例 3, 寫 code 的時候想參考我的做法

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

### 案例 2, 寫文章 / 文件的時候想引用我的觀點

接續上一個案例 (這是連續的操作): Code 寫完，我想補上一份說明程式碼架構的文件，於是我接續 agent 的對話，給了他這段要求:

```markdown
從安德魯的文章中，摘要這段程式碼用到的技巧
寫在 #file:ARCH.md 內

直接引用的部分, 請用 > ( quot ) 的方式來呈現, 並且務必附上原始網址
如果是引用後你重新寫的說明則不需要 quot, 但是請仍需要在段落最後，或是整份文件最後標記參考來源。
```

看起來，前面透過 MCP 查詢的內容還留在 context 內，這次寫文件就沒有再查詢一次了，所以沒看到 MCP 的調用紀錄。而按照要求，Agent 替我寫了這段敘述:

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
```csharp
// 輸出端：每筆資料一行
json.Serialize(Console.Out, model);
Console.Out.WriteLine();

// 接收端：逐行反序列化
while ((line = await reader.ReadLineAsync()) != null)
{
    var item = JsonSerializer.Deserialize<UserItem>(line);
}
```

## 架構組件

### 生產者-消費者模式

基於文章中的 BlockingCollection 概念，本程式使用現代的 `Channel<T>` 實現：

```csharp
var channel = System.Threading.Channels.Channel.CreateBounded<UserItem>(100);
```

這種設計提供了：
- 有界緩衝區避免記憶體無限制增長
- 非同步背壓控制
- 自然的生產者消費者解耦

### 平行處理策略

> DEMO 4, 管線處理 (async) 在每階段以 Task 將「等待當前」與「索取下一筆」並行化，讓階段間出現交錯、實現有限度平行。

程式實現了類似的平行策略：
- 單一生產者負責讀取資料
- 多個消費者平行處理資料
- 使用 async/await 實現非阻塞並行

### 錯誤處理與容錯性

> 逐筆處理便於跳過壞件與持續前進

實現了優雅的錯誤處理機制：
```csharp
try
{
    item = JsonSerializer.Deserialize<UserItem>(line);
}
catch (JsonException ex)
{
    Console.Error.WriteLine($"解析第 {lineNumber} 行 JSON 時發生錯誤: {ex.Message}");
    continue; // 跳過錯誤行，繼續處理
}
```

### 資源管理

> yield \[返回的資料\] 僅保留當前（或少量上下游）資料，內存穩定。

透過串流處理和適時的資源釋放，確保記憶體使用穩定：
- 使用 `yield return` 實現惰性求值
- 及時釋放已處理的資料
- 避免大量中間結果積累

## 效能特性

### 記憶體使用

> 串流處理: 單一 foreach 對每筆資料依序做 P1→P2→P3。第一筆回應快（ΣMi），總時間仍為 N x ΣMi。因逐筆生成與處理（yield return），記憶體占用接近常數。

本程式實現了 O(1) 的記憶體複雜度：
- Channel 緩衝區大小固定（100）
- 每個 Worker 同時最多處理一筆資料
- 處理完成後立即輸出並釋放

### 吞吐量優化

通過平行處理實現了接近理想的管線吞吐：
- 多個 Worker 同時處理不同資料
- 非同步 I/O 避免阻塞等待
- 管線化設計讓讀取、處理、輸出並行進行

## 與 Unix 哲學的整合

### 管線友善設計

> CLI 的處理方式: 將 P1~P3 拆為獨立 CLI，以 OS 的 STDIO 與管線管理緩衝與背壓，保留程式碼簡潔與職責分離。

雖然本程式將所有處理整合在單一 CLI 中，但仍遵循管線設計原則：
- 標準輸入輸出介面
- 可與其他 Unix 工具組合
- 支援重導向與管線操作

### 工具組合性

```bash
# 與壓縮工具組合
cat data.jsonl | dotnet run --project pipeline-cli/ | gzip > result.gz

# 與過濾工具組合  
grep "pattern" data.jsonl | dotnet run --project pipeline-cli/

# 遠端處理
ssh remote "dotnet run --project pipeline-cli/" < data.jsonl
```

## 設計權衡

### 複雜度 vs 效能

相比文章中展示的 DEMO 2（純串流）和 DEMO 5（BlockingCollection），本實作選擇了中等複雜度的方案：
- 比純串流複雜，但獲得了並行處理能力
- 比完整的多階段管線簡單，但仍保持了高吞吐量

### 一致性 vs 性能

使用 `SemaphoreSlim` 確保輸出順序的一致性，這會犧牲一些並行度，但確保了結果的可預測性。

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

### 案例 4, 在編輯器中直接取得文章 (包含生成) 的內容

### 案例 5, 生成訓練計畫, 測驗題 ( Quiz ), 實作題 ( Hands On Labs )

## 2. 內容正規化 - 生成特定格式的內容

## 3. 流程效率化 - 流程優化, 清除文件的技術債