![](https://d1lamhf6l6yk6d.cloudfront.net/uploads/2025/05/250430-Nine-Emerging-Patterns.-Yoast-G-1200x627-1.png)

忙完了我自己部落格的重構 (上一篇), 開始補一下還沒寫的文章了。這次是補之前只在 Facebook 分了多篇分享的創投趨勢報告讀後心得。趨勢報告都會用很客觀公正的資訊 & 數字來告訴你那些事正在發生。但是這樣看起來很冷冰冰，對這領域不夠深入研究的人，其實難以想像背後到底發生了什麼改變。

我的心得就著重在看懂背後發生的事情，並且舉了很多現在我觀察到正在改變的實際案例當作參考，等於是換個角度更具體地描繪了改變會怎麼發生，以及發生在哪裡。

在 Facebook 上的 PO 文限制蠻多的, 格式有限 (我怎麼都沒辦法用 markdown 貼文?), 還不能有連結... 貼到部落格後就順手補上這些細節問題了。這篇集合了我先前分散在 12 篇 Facebook PO 文的內容, 修正的格式等等部分我就不特別標註了，我在整理當下額外加上的註記則有特別標示。另外，在 Facebook 上仍有些值得參考的資訊, 例如其他朋友在底下的留言, 以及有些人分享我的 PO 文時會加上自己的觀點，這些都還蠻值得參考的。因此我特別把 Facebook PO 文的連結跟基本的統計數字也列出來，方便查閱。


<!--more-->


# 0, 寫在前面

其實我看過很多這類趨勢報告，不過就這篇我特別挑出來深讀，原因很簡單，這篇一開始在 Facebook 其實有好幾位大神轉貼，包括保哥 & iHower, 就吸引我注意了。仔細一看，他不是單純的比較趨勢或是市場占有率等等這些分析報告，而是具體的在談 "如何改變"。看的出來這些判斷，背後都有實際的研究跟專家的見解，不是隨便湊出來的內容。而這些預測趨勢，好幾個地方都跟我過去的想像跟推論一致。

因此我想，這主題我是有能力把這篇趨勢報告背後沒有提到的關連與發展說清楚的，這些推論都基於我過去兩年間做的研究，也都有其他發表的文章，實際案例或是演講內容可以對照著看。因此，就有了這陣子的 12 篇 PO 文，跟現在這篇彙整的文章。

## 我的心得與導讀

我把相關資訊跟連結都收集在這邊，以及我一小段導讀跟增補的心得，後面就是 PO 文轉貼。

A16Z 的趨勢報告是這篇: [Emerging Developer Patterns for the AI Era](https://a16z.com/nine-emerging-developer-patterns-for-the-ai-era), from Andreessen Horowitz (a16z)

這篇報告有九個主題，分別是:

- **AI-native Git**: Rethinking version control for AI agents
- **Dashboards -> Synthesis**: Dynamic AI-driven interfaces
- **Docs are evolving**: Docs are becoming a combination of tools, indices, and interactive knowledge bases
- **Templates to generation**: Vibe coding replaces create-react-app 
- **Beyond .env / secrets management**: Managing secrets in an agent-driven world
- **Accessibility as the universal interface**: Apps through the eyes of an LLM
- **The rise of asynchronous agent work**
- **MCP as universal standard**: MCP is one step closer to becoming a universal standard 
- **Abstracted primitives**: Every AI agent needs auth, billing, and persistent storage


之前我說過, 軟體開發產業站在 AI 海嘯的第一排, 這報告就是特別針對這產業的預測。到目前為止, AI 的發展主要是以 Agent 為主軸, 因為 Coding Agent 的普及, 整個軟體開發的流程開始左移, 過去人類主要負責 "撰寫" code 的角色逐漸偏移, 變成 "外包" 給 AI coding 跟 "驗收" 的角色了。人跟 AI 做這件事的效率不同，過去的瓶頸也因為 AI coding 效率遠超過人類，而整體的瓶頸開始改變，連帶的影響了接下來軟體開發的流程變革。

因此，這報告第一點就說 Git 會改變了。版控過去是為了解決 "人腦" 不擅長好好的追蹤管理 code 的異動過程而衍生出來的系統，而當 code 不再完全是人寫得之後，版控的意義就不同了。未來，人寫 code 的比例會降低，而寫 prompt, 文件, 測試案例等等的比例會拉高，真正需要被 "版控" 的，其實是人的產出。因此 Git 也應該會因應的結構調整才對。

軟體開發的領域，每個環節大致上都會有像 Git 這樣根本的變化, 因為過去的 "軟體工程", 其實都是圍繞著 "人腦" 處理 requirement / code 不夠精準地問題而發展出來的工程。被 AI 替代或強化的環節，就不再需要那麼多的工程技巧根留成了。人們的關注與發展就會轉向過去無法觸及的新領域。報告接下來的 UI (尤其是 Dashboard 這類複雜資訊呈現跟解讀的類型) 會開始出現動態生成的機制；而過去高度依賴 code generator / project template 生成專屬程式碼的工具, 也會快速被 coding agent 取代。Agent 開始能替你執行越來越多任務, 授權的管理也會越來越走向標準化的認證 / 授權獨立的機制。Agent 要代替你執行更多的任務，你就必須把你 "感知" 的資訊交給他，所以作業系統的 "無障礙" API ( 就是 Accessibility API ) 會變成這些 Agent 的感知來源，會有越來越多的 Agent 會配合這機制來開發。最終這些變化不斷的發展，非同步，以及 AI tools 的標準化 (MCP) 都是必然的方向。

我覺得這一系列的變化，串在一起解讀，是個很精彩的推論與整理。這環節剛好過去兩年間我都各別面對過，因此我用我的經驗跟想法來詮釋這些改變的過程，讓大家能更清楚這些改變會怎麼發生，以及發生在哪裡。

所以，我的結論就是先前 PO 的這 12 篇了。後面我花了點功夫 "整理" (就真的只有整理，沒有新的內容，已經看過 FB 的可以自己決定要不要重讀一次)，把保哥、iHower 的評論，以及我自己的解讀都收在後面。


## 相關的 Facebook PO 文整理:

**保哥** 2025/06/07 的 Facebook [PO 文](https://www.facebook.com/share/p/1BhsbUfiQg/) 介紹:
> 根據知名創投 Andreessen Horowitz 最新分析，AI 正在從根本上重塑軟體開發生態。這份報告揭示了九個關鍵趨勢，顯示開發者不再將 AI 視為輔助工具，而是軟體建構的新基礎。從版本控制系統 Git 的重新設計，到儀表板的智能化轉型，再到文件系統的互動化演進，每個環節都在經歷深刻變革。  
>  
> 最引人注目的是「氛圍程式設計」的興起——開發者只需描述需求，AI 就能建立完整的客製化專案架構，取代了傳統的靜態模板。這些變化預計將影響全球 3000 萬開發者的工作方式，不僅大幅提升開發效率，更從根本上改變了軟體開發的思維模式。隨著 AI 代理既成為協作者又成為消費者，整個開發工具鏈正在重新設計，以適應這個人機協同的新時代。  
>  
> a16z 的文章總是能一針見血，建議可以看看完整原文！👍


**iHower** 2025/06/07 的 Facebook [PO 文](https://www.facebook.com/share/p/1c6G5k51LC/) 介紹:
> 看到這篇 a16z 的 "Emerging Developer Patterns for the AI Era" 覺得有厲害，探討了 AI 正在重塑建構軟體的方式。
> 以下是作者提出的九種前瞻性開發模式，為開發者帶來新的 AI-first 思維:
> 1. AI-Native 的版本控制系統: Git 是為了追蹤手寫程式碼的精確歷史而設計的，現在用 AI Coding 的話，我會更想紀錄當時的生成意圖和 prompt 是什麼? 是用什麼模型哪個 Agent 等等脈絡資訊
> 2. Dashboards 改用 Generative UI: 讓 AI 根據用戶當下的需求，即時生成用戶需要的 UI 元件在前端顯示出來
> 3. 文件不止給人看，也要準備給 AI 看
> 4. Vibe Coding 取代 create-react-app 範本
> 5. 新的管理 secret key 方式而不是單純用 .env
> 6. 可及性 Accessibility 設計不只是為了用戶無障礙使用，而是能讓 AI 操作的通用介面
> 7. 非同步 Agent 工作流: 能像指派任務一樣丟給 Agent 在背景執行
> 8. MCP 標準化: Agent 與工具之間的標準協定
> 9. 專門針對 Agent 提供的 API 基礎服務，例如: 身份驗證、計費、資料庫等雲端服務


<!--

**以下則是我在 2025/06/12 ~ 07/24 之間的 12 篇 Facebook PO 文清單**, 數字統計至今天 (2025/09/28 為止):

| 日期 | 標題 (FB連結) | 按讚 | 留言 | 分享 | 儲存 |
| ---- | ------------- | ---- | ------- | ----- | ---- |
|2025/06/12| [AI Native Git 與版控演進](https://www.facebook.com/andrew.blog.0928/posts/1303100645158077)   | 592 | 19 | 164 | 176 |
|2025/06/13| [AI原生Git操作想像](https://www.facebook.com/andrew.blog.0928/posts/1303973295070812)          | 70 | 2 | 12 | 15 |
|2025/06/16| [AI驅動介面趨勢](https://www.facebook.com/andrew.blog.0928/posts/1306421161492692)          | 78 | 6 | 20 | 24 |
|2025/06/17| [AI介面架構設計](https://www.facebook.com/andrew.blog.0928/posts/1307388741395934)          | 311 | 8 | 100 | 125 |
|2025/06/19| [AI介面與UX比較](https://www.facebook.com/andrew.blog.0928/posts/1309122297889245)          | 92 | 1 | 15 | 21 |
|2025/06/20| [文件成AI流程關鍵](https://www.facebook.com/andrew.blog.0928/posts/1309855694482572)        | 95 | 3 | 17 | 18 |
|2025/06/26| [文件即程式實例](https://www.facebook.com/andrew.blog.0928/posts/1315125470622261)          | 87 | 2 | 28 | 24 |
|2025/07/21| [Context工程與文件](https://www.facebook.com/andrew.blog.0928/posts/1337243908410417)       | 177 | 2 | 25 | 65 |
|2025/06/27| [範本到生成轉變](https://www.facebook.com/andrew.blog.0928/posts/1315999790534829)             | 57 | 6 | 8 | 16 |
|2025/07/22| [無障礙設計即AI介面](https://www.facebook.com/andrew.blog.0928/posts/1338108878323920)         | 161 | 2 | 42 | 62 |
|2025/07/23| [非同步Agent崛起](https://www.facebook.com/andrew.blog.0928/posts/1338994928235315)            | 293 | 4 | 84 | 82 |
|2025/07/24| [MCP 邁向通用標準](https://www.facebook.com/andrew.blog.0928/posts/1340022954799179)           | 740 | 8 | 181 | 298 |

-->



# 1, AI-native Git

這段的完整標題是: AI-native Git: Rethinking version control for AI agents, 我在 FB 分了兩篇 PO 文來談這主題, 第一則是闡述我對這方向的看法，第二則則是具體的想像這改變發生後的使用場景。

- 2025/06/12, AI Native Git 與版控演進
- 2025/06/13, AI原生Git操作想像


## 2025/06/12, AI Native Git 與版控演進

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1303100645158077](https://www.facebook.com/andrew.blog.0928/posts/1303100645158077)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image.png)
圖: 想像支援 prompt 異動追蹤, 以及 evaluate 驗證的 Git 的使用方式


前幾天 (這年代，差幾天應該就算舊聞了吧) 各大神都在轉貼這篇知名創投的 A16Z 的 AI 趨勢報告:

A16Z, [Emerging Developer Patterns for the AI Era](https://a16z.com/nine-emerging-developer-patterns-for-the-ai-era), Yoko Li

當下我也看了，越看越符合我對未來的想像。文中列了九項趨勢, 想說就深入一點探討，一次來聊一題好了，逐項分幾篇 PO 文來分享我的看法跟觀察。

先來第一項: **AI native Git**

原文的大意是: Git 是精確追蹤 source code 異動的管理工具 (要能細緻到追出誰在哪一天，哪一行 code 加了一個分號讓編譯失敗這類蠢事 XD), 這種細緻度, 在 AI coding 的比例越來越大的情況下不再這麼重要了，因為 code 不再完全是 "人" 手工寫出來的。

我認同這觀點，不過說法不大一樣。前面談 AI 時代軟體工程 (例如: SOLID 原則) 是否還重要的 PO 文我也聊過，AI coding 能力越強，人的心力就會越會往需求端移動。屆時，AI 產生 code 的來源大部分是 document ( 跟當下 developer 下的 prompt )，這時比起 "source" code, 現在的 code 更像是由 document “build” (其實是 vibe coding) 出來的結果 (“artifacts”).

因此, 對比一下:

**過去**:  
source (code) 要進版控, (code) build 的結果 (binary, executable, container image) 要進 AM (artifact management).

**現在**:  
source (requirement, 通常是 document + prompt) 要進版控, vibe coding + build 的結果 ( code / executable / container image ) 要進 AM ( 可能是同一個 or 另一個部署用的 git repo, 以及真正儲存 binary 的 AM )

就 CI/CD 的觀點來看，其實流程是一樣的，只是通通都往 "左移” 了一階, 未來的 source code, 意義上更像是產出物，而不是手寫的原始碼了。

我都特別寫 “source” code 或是講 “原始” 碼，因為我認為文字上的意義，是強調 “source” 才對，那是人類意圖真正變成對機器有意義的第一個產出。關鍵是 source, 不是 code. AI 的進步，同樣意義的 source 逐漸變成 document, 原本代表 source 的 code 現在變成 AI 的產出物了, 自然會有這樣的平移。

所以，意義上真正需要被版控的，其實是 source 而不是 code. 現在的 Git 是為了 code 的版控而設計的系統，如果未來的 source 從 code 變成 document, 版控會有甚麼改變? 版控的目的，是讓你能夠追蹤 source 因為甚麼原因，做了甚麼改變，讓你能事後還原整個變化的過程跟意圖，也能讓你從實際運作中的系統 ( 通常是來自 AM 部署出去的系統) 往回追蹤這份運行中的 artifacts 是來自哪一版的 source..

所以，未來需要追蹤的，是需求文件及 prompt 的變化。這邊的 prompt 包含產生 code 用的 prompt ( vibe coding )，應該也包含實際在線上運作的 AI APP 內含的 prompt .. 這有點難區分，就像之前在 GenAI 年會講到的，用 AI 開發 AI 產品，兩邊用到的 prompt 其實都需要被管理。

所以，真正管理需求變更的 "Repo" 可能是以需求 (document) 跟意圖 (prompt) 為主的系統, Repo 的 Diff 操作，可能不再只是告訴你那些檔案有異動，而是類似 RAG 那樣，先找出 string 實際上的 Diff，再透過 LLM 彙整，告訴你兩個版本的 "意義" 上有哪些不同, 例如多的兩條需求，刪減三個需求等等… 現在有些 IDE 能自動產生 git comment message, 大概就像那樣的味道吧。

不過，即使如此，我覺得到時管理 code 的版控還是有存在必要，因為你還是需要 code review 等等任務，只不過在意義上更像是生產線後段的東西了，這些過程其實更像 build / pipeline 的過程，而不是在 "開發"。因此 code 我認為它更接近 Artifacts (”產出" 物) 這樣的存在, 而不是 Source Code (”原始" 碼)

AI Native Git, 大概就是這個意思吧。針對這項我花了點篇幅來聊聊，後面幾項我也會逐一深入探討。有興趣的歡迎追蹤我的粉專 😃



## 2025/06/13, AI原生Git操作想像

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1303973295070812](https://www.facebook.com/andrew.blog.0928/posts/1303973295070812)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image.png)
圖: 想像支援 prompt 異動追蹤, 以及 evaluate 驗證的 Git 的使用方式

延續昨天的 PO 文 ( AI Native Git ), 我少提了一段, 就是原文提到的 "模擬操作畫面”，今天就來補個 Part II 吧 (如下圖):
(為了方便閱讀, 我也把字都打出來了)

```

$ git gen-commit —prompt “Add a billing feature to my app” —tests “billing.spec.ts”
[O] Prompt saved
[O] Tests linked
[O] Code generated and validated

Agent: claude-3-7-sonnet-latest
Bundle: bndl_f92e8 ( prompt + tests )
Human review: required for `billing.ts`

```

花了點時間 "腦補" + 逆向工程, 推敲這段模擬畫面背後的想法, 看起來 repo 放的內容，仍然是現在以 code 為主的模式 ( 應該會包含相關的 markdown 文件 )，但是在 git 的操作上看來有些擴充。

以下是我看圖之後的想像:

首先，這是 "gen-commit", 不是單純的 "commit", 意思是要 commit 的內容異動, 是在這指令之後才產生出來。CLI 後面的參數給了 prompt 跟指定了 test, 而下方的回應傳回了:

```
prompt saved
tests linked
code generated and validated
```


意思是未來的 AI Native Git 在 commit 的管理上，除了 message, tags 之外，會額外標註這包 commit 對應的 prompt / tests, 並且在 pipeline / tools 整合上也會有對應。上面的模擬圖，想像上是下了指令後，對應的 agent 會在 git 紀錄好 prompt / tests 後, 真正執行 code generated ( 從 prompt + repo 的 context 生成 code )，以及執行 validate ( 應該就是自動執行指定的 test 並且確認有沒有 pass 吧 )

而後面的訊息，才是對應到現在大家熟知的 CI / CD, 有 artifacts ( bundle ), 也有 code review 的要求..

看到這邊，另一個聯想是，未來 AI coding 的戰場，會逐漸從 IDE + AI 的整合 ( 如 vscode, cursor, winsurf 這類工具 )，轉移到 CLI 型態，或是 server side 的 coding agent + 管理平台 + 基礎建設的生態系戰爭了，因為這樣才能整合在 pipeline 上面，或是在完全不需要人為介入的前提完成大部分任務。這是能大量 scale out coding 能量比較可行的作法。

相較於 IDE + AI，比較像是跟 AI pair programming, 搭配的 developer 影響還是很大 (至少占一半)。而 agent 的作法，人的影響就降低了，只剩下需求提供的速度與確認產出的速度會是瓶頸，中間的部分完全可以 scale out, 費用成長也是線性的 (相較真人，加班的薪資比平日高，例假日更貴，還有一例一休限制)。

不過, AI Agent 的門檻較 CLI 還要高一些，主要是多了要給 Agent Sandbox 環境讓他工作用。想像一下，當一個完全在 server side 的 coding agent 要幫你做事的話，他要準備什麼?
1. 至少要有 workspace, 能 git pull 把 repo 拉回來..
2. 在這 workspace 按照 ticket / prompt / issue 來改 code
3. 在這 workspace 要有足夠的 tools, 能順利完成 build
4. 在這 workspace 要有足夠的 infrastructure ( 例如 docker, k8s 等等), 能部署 + 測試 build 好的結果

如果你的 code 架構過度依賴 infra ( 例如一定要能存取 DB / Redis 才能跑 )，未來要推進到這環境會很辛苦。現在開始找時間逐步切斷這些依賴吧..  很多 CI/CD 的 best practice 都有談到這些，這跟 AI 沒直接關聯，你願意的話現在就可以做。

市面上看的到的這類 coding agent, 常見的有:
- GitHub Copilot Coding Agent ( Agent )
- Open AI Codex ( CLI, Agent )
- Claude Code ( CLI )

蠻有意思的想像, 我猜 A16Z 創投能寫出這樣的趨勢報告, 背後一定有更詳細的研究, 這份報告應該只是精簡摘要的內容而已。能從這些蛛絲馬跡推敲背後的研究團隊掌握到什麼訊息，其實也是挺有意思的 XDD

上面反推的這些技術，其實離現在沒有那麼遠啊，這些機制目前的系統也不是做不到, 頂多部分動作人工處理而已。不知道有沒有人已經是這樣調整你的工作流程了? 歡迎留言討論 😃



# 2, Dashboards -> Synthesis

這段在原文的標題是: Dashboards -> Synthesis: Dynamic AI-driven interfaces

這章節談的是 Dashboard 的改變, 但是背後談的其實是 AI APP 的 UI 設計改變。會拿 Dashboard 當作例子只是因為 Dashboard 是資訊特別複雜的一種 UI 類別，所以特別被拿出來探討而已，但是我覺得這段其實談的是未來 AI APP 的 UI / UX 課題。

因此這段我當時在 FB 花了比較多篇幅在談，我分了三則 PO 文:

- 2025/06/16, AI驅動介面趨勢  
UI 如何從設計師的設計, 進化到 AI 在當下動態生成的想像
- 2025/06/17, AI介面架構設計  
這段是我自己補充的開發經驗。去年初我發表安德魯小舖的時候，做過對談 + 傳統 UI 操作混用的結構，套用當時被 Microsoft 炒得火熱的名詞 "Copilot" 當作代表, 示範 MVC 的 controller 如何跟 LLM 協作, 協同做好 UI 與 Chat 同時跟使用者互動的設計案例
- 2025/06/19, AI介面與UX比較  
這段也是我補充的開發經驗。我在去年的 DevOpsDays Keynote 展示過這段，UX 的 feedback 好壞與否，過去是依靠數據統計來推論，而我示範了直接用 LLM 直接根據 context 來猜測使用者滿意度的作法。


## 2025/06/16, AI驅動介面趨勢

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1306421161492692](https://www.facebook.com/andrew.blog.0928/posts/1306421161492692)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-1.png)
圖: 傳統的 dashboard 設計, 資訊全都 "一覽無遺", 代表使用者必須懂得更多才能掌握。使用門檻高, 不容易找到你要的資訊


![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-2.png)
圖: 動態生成的 dashboard, 支援 AI agent 對話的結果呈現

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-3.png)
圖: Agent-Ready 的 dashboard, 同時提供 user (人) 以及 agent (AI) 必要的資訊



今天繼續來談談 A16Z 趨勢報告的第二個主題: **AI-driven interfaces**.

這題是很好討論的題目, UI 比起 Git (第一個主題: AI Native Git) 而言更具體了，要實現它的技術都已經出現，要 PoC 的話已經完全不是問題，只差在你多快能實現它，多快能運用在你的系統或產品身上而已。

我選擇用副標題 (AI-driven interfaces) 為主,  而不是原文的主標題 (Dashboards → Synthesis), 因為我更認同副標題的意念。而 Dashboard 變成合成 (Synthesis) 產生，則是理所當然的結果而已。為何用 Dashboard 來說明? 因為它最複雜, 理解的門檻很高, Dashboard 的設計用意是讓你一目了然某系統運作的全貌，但是你關注的重點往往高度跟你的腳色及意圖相關，而這是使用階段才決定的事，難以在設計階段決定，因此造就了這些使用落差..

談到 AI driven interfaces, 我正好有點經驗可以拿來說嘴 XDD, 在 2023 年底的時候，我嘗試 "安德魯小舖" 的過程中，就碰到這題目，當時我在思考 "對話" 的操作方式會取代 "UI" 嗎? 最後我的答案是 "不會"，因為 UI 仍然有他擅長發揮的場合，全部都變成對話也很怪。而去年我在 DevOpsDays 2024 的 Keynote 也聊了這個主題，我切入
的是 AI 帶來 UX 的改變，當時我是這麼說的:

>  "  
> 傳統 APP 的 UX 高度仰賴設計師大量的事前訪談，猜測使用者操作當下的情境，給予最合適的操作介面。猜對了就有好 UX。而 AI 走的是另一條路，藉由對話來掌握當下使用者的意圖，給予最合適的操作介面與資訊。這是降為打擊，設計階段永遠處理不了執行階段才發生的所有狀況 (尤其是少數特例)，但是有了意圖理解能力的 AI 可以 (只要模型持續進步)..  
> "


所以，未來的 UI 應該會模組化，不會像 Wizard 一樣從頭到尾都靠 UI，而是會變成模組化，切割成單一任務 (例如檢閱商品，結帳等等)，然後由 AI 來主控，引導你逐一完成每個步驟。UI 元件，會化身成 AI 可以調用的 tools, 當使用者需要時，AI 可以調整 UI (用 tools + parameters)，呈現出當下使用者需要的畫面內容。
而呈現的方式，這篇趨勢報告用了三張圖，很貼切的表達了我當時的想法 (我也很慶幸我的想法有在發展的主流軌道上 XDD)。這三張圖分別代表 過去 / 現在 / 未來 的可能樣貌:

圖1: **傳統** Traditional dashboards: complex and hard to search for information
圖2: **動態** Dynamic dashboards: AI agent Q&A and actions
圖3: **代理** Agent-ready dashboards: providing information for humans and agents at the same time

而這些背後需要的技術基礎，文章沒提到，不過我已經可以串起來了，接下來我花點篇幅來聊聊這部分我的看法，各位也可以想一想你未來需要累積或是準備什麼技能。

圖2 **動態** 的 dashboard, 其實跟傳統的沒兩樣，只是透過 agent 協助, 能幫你省掉一些操作, 幫你找到你該在 dashboard 看的資訊而已。LLM 的 tools use 技術早已成熟, 只是這些 tools 不是 API, 而是 dashboard 上面的 widget, LLM 透過對話掌握你的意圖後, 在允許的 tools (widget) 清單內挑出合適的項目，幫你設定好 (tool parameters) 呈現在你面前。現今的系統其實不需要大規模調整就足以實現。

圖3 **代理** 則層次更進階了。這已經不是 "預設" 的 widget 直接拿來用就好, 需要的可能是更細緻的元件, 讓 AI 能動態組成你現在想看的資訊。如果硬要跟現在成熟的技術當作對比，我覺得 markdown + mermaid 這類技術其實更貼近這樣的想像。試想你現在正在使用 cursor / vscode + github copilot 的工具，並且用 agent mode 讓 AI 幫你整理許多資料, 輸出成 markdown, 當下打開預覽…

文字的敘述，資訊的摘要與彙整，用 Markdown 來處理文字格式，表格，都已經不是問題。AI 對於 markdown 的理解能力也足夠。但是圖表呢? 我常用的技巧，就是讓 AI 產生 mermaid scripts, 並且放在 markdown 文件內，這時支援度夠好的 markdown viewer 就能在文件內嵌這些圖表。

這邊舉的例子: mermaid 只是其中一個案例, SVG 等等其他格式也都沒問題, 甚至你要自訂都可能。只要你的 viewer 認得, 只要你的 AI 懂得語法能替你把 "資訊" 翻譯成 "Script" 就沒問題。這時，你的意圖就能更精準的，用更合適的介面 (UI) 呈現在使用者面前。

要做到這樣的應用，你的系統需要更 “AI Ready” 才行。兩年前大家在談的是 RAG，談的是在 Agent 對話介面，如何整合後端搜尋檢索 (最常見的是向量資料庫)，動態生成文字訊息的回應。而這樣的 UI 對我來說，就是同樣的技術，但是整合更多元的技巧，協力完成的結果。

舉例來說 (我就按照圖三，看圖說話)，當我詢問了 Agent: ```今天的 API Gateway 系統運作狀況如何?```

- AI 會按照上下文，動態生成 Log Query ( 或是對應的 Log Query Tool Call ), 找到對應的查詢結果
- AI 會按照上下文，動態生成 Error Message Query , 找到對應的查詢結果
- AI 會按照上下文，Call Tools 查詢 Deployment 紀錄
- 這些蒐集到的資訊，都彙整到 context windows 中，讓 LLM 直接生成結果輸出

聊到這邊，我才發現，各家 LLM 都不約而同，早就拿 markdown 當作通用的輸出介面，真是有遠見。是巧合還是精心規劃設計的結果? 我猜這些跑在前面的人，早就料想到這些了，這一切其實都規化的很清楚，只要逐步推進，等待每個環節技術成熟，這件事就到位了。

一開始我就提到，就技術而言，現在已經完全可以實現這樣的能力了，我想這份趨勢報告講這點的用意，已經不是在講技術突破，而是在講，未來 UI 的演進方向會朝這方向邁進了。對於開發人員，我想你需要掌握的是，你是否有能力實現它? 它背後需要的系統架構會是甚麼?

對於產品設計人員，你需要掌握的是，你能否掌握這樣的使用習慣，替使用者規劃最合適的產品功能? 當你的開發團隊已經有這樣的實作能力時，你是否開得出夠好的規格讓它們發揮? 使用者給你的回饋，你是否能善用這樣的能力給它們更好的體驗?

AI-Driven UI 這主題，也是個很精彩的趨勢預測，令我更開心的是它也驗證了我過去在不同場合分享過的多個觀點。這次的參考資訊有點多，我統一收在第一個留言下的回覆。



## 2025/06/17, AI介面架構設計

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1307388741395934](https://www.facebook.com/andrew.blog.0928/posts/1307388741395934)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-4.png)
圖: 我在 "安德魯小舖" 的案例中說明過的 AI-Driven UI 架構設計圖 (MVC + LLM)


今天，繼續聊 **AI-driven Interface** 這題目, 今天不聊趨勢, 直接來聊聊這樣的系統的架構該如何設計。

如果你想設計具備 AI-driven UI 的系統，那麼在設計上有兩個環節一定要注意。一個是 controller 必須搭配專屬的 AI (推理能力要夠好，必須具備 function calling 的能力)，另一個是你必須安排讓 AI 能感知使用者操作情境的能力。

這是架構設計層面的問題, 我相信你找不到太多參考資料跟範例的, 昨天的重心沒放在這環節上, 今天就來補一下實作的想法。我們就從最基礎的 MVC 開始吧..


> 補充:
> 
> 我最早提出這架構, 是 2024/02/10 在這發表的 - [替你的應用程式加上智慧! 談 LLM 的應用程式開發](/2024/02/10/archview-int-app/#2-%E6%8E%A2%E7%B4%A2-llm-%E6%87%89%E7%94%A8%E7%9A%84%E7%B3%BB%E7%B5%B1%E6%9E%B6%E6%A7%8B%E8%88%87%E9%96%8B%E7%99%BC%E6%A1%86%E6%9E%B6))，之後在 DevOpsDays 2024 Keynote: [從 API First 到 AI First](/2024/07/20/devopsdays-keynote/#3-4-copilot-%E7%9A%84%E8%A8%AD%E8%A8%88%E6%9E%B6%E6%A7%8B), 也再次談過這個架構

--

MVC, Model / View / Control, 整個系統由中心的 Controller 來控制什麼樣的資料 (Model) 該如何對應到畫面 (View) 的架構。而這樣的結構，到了 AI 時代還是沒變。有變化的，就是 Controller 必須跟 AI 密切合作，來精準地控制 UI，回應使用者的需求了。

這時，AI 要能精準地回應使用者，讓 AI 充分感知使用者的一舉一動，是必要的條件。只有這樣，AI 才能 "生成" 使用者想要看到的內容跟介面。而 Controller 如何讓 AI "感知" 使用者的意圖? 

目前最常見的設計, 就是畫面旁邊懸浮著一個聊天室窗, 你可以在裡面用自然語言跟 AI 溝通，如同 Agent / Copilot 一般。不過，如果你不跟 Agent 聊天，AI 就完全不知道你要幹嘛了啊，這樣是遠遠不夠的，因此另一個關鍵就是: Controller 必須不斷地跟 AI 回報使用者現在正在做什麼事。

我在去年初發表了 copilot 版本的 "安德魯小舖"，就是這麼做的。換來的效果就是，你可以用正常的方式操作，也可以用聊天的方式，AI 都能知道你想幹嘛，適時的協助你完成任務。

舉例來說，使用者操作購物車，將五瓶可樂放進購物車，Controller 就會送這 message 給 AI:

"使用者在購物車中 [加入] [可樂] x 5"

而大部分情況下，AI 都只會回應 "OK" 這類確認訊息而已。但是當 system prompt 有提醒的注意事項發生時 (比如一直清空購物車的話, 店長就該出來關心一下之類的), AI 就能立即回應注意事項, 或是驅動 Controller 在 UI 上做出對應的反應。

順帶提一下，A16Z 這篇報告中，有提到另一個 AI 的發展趨勢:  "Accessibility as the universal interface", 意思是說未來應用程式開始會利用作業系統的 "輔助功能" (accssibility settings) 的功能來感知使用者的操作環境, 這時 AI 多了更精準的管道來得知使用者的操作狀態.. 也能做出更到位的回應...

總之，當 AI 理解你的意圖，而 AI 也有 function calling 的能力能選擇操作系統，這一切就串的起來了。這頁簡報是我去年在 DevOpsDays 2024 Keynote 講的內容, 要傳達的是當你想做出這樣的 UI 的話，你的系統架構該怎麼設計。核心就是 controller + AI, 以及暢通的使用者操作感知能力。

因此，若你想實作這樣的系統，好好看一下這張圖吧! 為了讓 LLM 表現能夠更個人化一點, Agent 必備的幾個要素自然也不可少 (chat history, instruction, knowledge base, personal information 等)。這些配置，都是為了建構 AI 更完整的 context windows 而設計的，當 context 的內容越貼近你個人喜好, 越貼近你現在的狀況 (聊天的上下文)，AI 的回應就會越精準地貼近你的期待

--


趨勢報告, 告訴了我們未來發展的方向。但是這份報告並沒有告訴你這些該如何實現。我去年的研究，正好補足了這塊。現在看到了報告，更進一步證實了去年我的想像。

因此，看到報告這樣寫，其實我還挺開心的 (因為我前年底就想通了，而且實作出來了啊 😃 )。藉著解構這份趨勢報告的同時，也把去年實作 copilot 版本的安德魯小舖的心得, 重新複習了一下。希望這些心得能對大家有幫助~

相關資訊，我留在第一則留言，歡迎大家討論，也歡迎給我回饋


## 2025/06/19, AI介面與UX比較

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1309122297889245](https://www.facebook.com/andrew.blog.0928/posts/1309122297889245)

--





**AI driven user interface** 最後一篇, 今天談 UX ( User Experience ) .. AI 主控的 UI, 到底是好是壞? 差別在哪裡? 如果用傳統方式做到極致的 UI, 會不會比 AI 驅動的 UI 帶來更好的體驗? 去年我花了不少時間再嘗試 AI APPs 的開發型態，也探討過這主題，正好趁這篇 PO 文來聊一下我的心得。

我先說我的看法，我覺得 AI 遲早會超車的，因為這是不同維度的技巧。長期來看 AI 驅動的 UI 會成為主流是沒有懸念的，就跟現在沒有人再談 AI 會不會取代搜尋引擎了一樣，談的只是 "何時"，跟 "誰" 會勝出而已..

先來觀察兩種路線的差異吧。目前的 APP 的 UI, UX 都是怎麼來的? 我覺得是 “設計" 出來的。

從現在的觀點來看，優秀的 UX Designer, 通常都必須是 Domain Expert, 同時也是 UI, Flow 的專家。透過跟使用者深度的訪談，了解需求。這時 UX Designer 精心設計的畫面及操作的流程，讓這些使用者當下能完美的解決他問題時 (在對的時間出現對的功能或資訊)，這就是好的 UX。

這路線很吃統計數據與客戶訪談，但總有例外。小眾使用者，非主流的流程，這時很容易就被忽略，因為資源有限，固定的設計才能產出需求規格讓 Developer 開發出實際的系統，這是目前工作方法的限制跟取捨。

換個角度看看未來的觀點，由 AI 驅動的 UI, UX 從何而來? 我覺得是來自 AI 精準地掌握使用者 "意圖" 而來的。

AI 驅動的 UI, 是從對話, context, 操作 / 環境的感知來了解使用者 "當下" 的狀況，AI 再搭配 system prompt, 以及我們賦予他使用的 "工具”，決定當下要給使用者什麼資訊與操作方式才是最合適的。如果做得到位，使用者就會覺得系統好像猜的到他在想什麼，好的體驗就從這邊發生了。

技術還在進步中，目前的 AI 還沒辦法做到 100% 完美，還有很大的進步空間，不過 AI 進步的速度也是有目共睹 (我覺得不用太久吧，一年變化就很大了)，等到發展成熟，推理能力與成本都大幅改善後，我認為 AI 驅動的 UI 這路線會狠狠輾壓傳統的技術。

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-5.png)

這是 "**設計師事前設計**" 與 "**AI 當下理解意圖**" 兩種路線的戰爭，不過倒也不用擔心誰會取代誰。我認為 UI 會趨向模組化，例如一個表單或是完成單純任務的一小組 UI 會變成獨立元件，這範圍內傳統 UX 設計技巧仍然會是主流；而把多個元件組成完整應用，掌控流程及資訊呈現的角色就會變成 AI 為主了 ( 還記得上一篇聊的嗎? 就是 Controller 開始會由 AI 主導的意思)。

接下來談談 UX 好壞的 "評估" 方式吧。現在講 AI 都會談到如何評估成效，UX 也得面對。UX 的評估，我認為也有傳統的做法，跟 AI 的作法。

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-6.png)

傳統做法，就是看 tracking 數據。我們透過 tracking 獲得的數據，來判定他是否滿意這設計。

舉例來說，新功能上線後都沒人點選，PO 就會知道這功能不受歡迎了。高明的 UX designer 會懂得要埋那些資訊，可以更精準的 "推敲" 使用者的想法。這是靠數據說話的基本能力，也是現代工程改善的基礎。

而 AI 時代這是唯一的路線嗎? 我去年在開發 "安德魯小舖" 時，我也思考過這問題。**AI 驅動的 UI 已經不是固定的流程了，我埋的 code 還有意義嗎**? 為了解決這問題，我在評估交易的滿意度時，額外 prompt 跟 tools 的參數多動了點手腳…。結帳成立訂單時，我要求 AI 多填了一組參數: 交易滿意度 ( 1 ~ 10 ), 以及滿意度的註記 ( Text )。我在 system prompt 簡單定義了 1 ~ 10 分的級別，之後就讓 AI 來判定分數，並且透過 tools 紀錄下來。

兩種方式，我都能量化使用者操作系統的滿意度，也能蒐集問題原因，這又是兩種路線的對比。透過 "**預先**" 設計的追蹤機制 v.s. 透過 AI "**當下**" 靠理解能力判斷使用者的滿意度，兩種路線哪種現在會比較有效? 發展到極致之後哪種路線的潛力會更大?

結果也跟前面一樣。AI 的做法能不能完全 "取代" 傳統追蹤的做法? 我覺得不行，但是 AI 能做到傳統作法做不到的情境 (例如: 如果 context 充足， AI 更有機會能捕捉到使用者的感受)。AI 會持續進步，屆時我們將會有更直接，更明確，更簡單的方式掌握 UX。

其實這整個過程，其實都包含在去年 DevOpsDays 2024 Keynote: 從 API First 到 AI First 這場的主題裡, 我就貼當時的一頁簡報當作代表，有興趣的可以直接參考第一則留言。

事前設計 vs 當下即時判斷；依靠統計數據 vs 依靠 LLM 推論使用者感受，我覺得這都是不同維度的解決方式，都是從不同的視角，完全不同的工程技術來解題的。我常說的 "降維打擊” 就是這麼一回事。

AI-Driven Interface 這題寫了三篇，總算告一段落，感謝各位的捧場! 下一個主題: Docs are evolving 是個硬題目，敬請期待 😃




# 3, Docs are evolving

這段我覺得是開發流程改變的結構核心: Document 的意義上實質的變化。

原文的完整標題是: Docs are evolving: Docs are becoming a combination of tools, indices, and interactive knowledge bases

文件，從單純的 "文件" 給人閱讀跟作為紀錄，到現在變成集合需求的所有必要資訊 (spec) 成為提供給 AI 主要的 context 來源，用於 AI coding 以及 Knowledge base 的主角，其實有不少觀念跟流程上的轉變。

這是最關鍵的一環，我在 FB 也是 PO 了三則才聊完這個主題。條列如下:

- 2025/06/20, 文件成為 AI 控制流程關鍵
- 2025/06/26, 文件即程式實例
- 2025/07/21, Context工程與文件



## 2025/06/20, 文件成為 AI 控制流程關鍵

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1309855694482572](https://www.facebook.com/andrew.blog.0928/posts/1309855694482572)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-7.png)

關於文件，這篇趨勢報告其實只有一小段的敘述而已, 但是我在實際的開發導入過程中, 我覺得 "文件" 才是 AI 推動整個流程改變的關鍵資源… 我把時間拉回兩年多以前 ( 2022/11 ) ChatGPT 首次發表的日子, 用一個簡單的演進過程來說明 "文件" 的重要性:

在 ChatGPT 剛開始吸引大家眼球的那一刻。當時大部分的人都這樣用:

> "  
> 請問 blah blah blah ..   
> "

當時的 ChatGPT, 能力有限, 只能依賴訓練資料來回答問題。沒有存取 internet 能力, 也無法上傳檔案, 唯一的 "input" 就是你問他的問題, 回答的好壞完全取決於模型能力以及提問的技巧。Prompt Engineering 在這時候被認為是個專門的技藝, ”AI溝通師" 這種職業也莫名其妙的流行起來 (結果現在完全消失了)..

後來，ChatGPT 在 GPT4 / GPTs 的年代 ( 2023/11 )，開放了 GPTs，也開放了眾多進階功能。你開始能在對話過程上傳檔案, 也能掛上 Custom Actions 有呼叫外部服務的能力, 這也代表 ChatGPT 有能力存取 Internet 了。這時你問的問題開始變成:

> "  
> 請參考我上傳的檔案, 參考 XXX 網站, 請問 blah blah blah, …  
> "

這時 AI 的 context 範圍開始變大了, 能力也提升了。輸入內容除了你的 message 之外, 也包括 tools, 以及 knowledge base. 在跟 AI 對話的世界裡, 資訊的 reuse 開始變的有效率了, 你不用一直不斷的複製貼上, 可以直接用 URL 或是 document 的形式 reuse 資訊 …

時間再來到 2024/07, GitHub Copilot 這類 AI Powered IDE 開始流行起來 (其實 GitHub Copilot 從 2021 就存在了), 內建在 IDE 的 Chat 也開始變成 Developer 跟 AI 對話的場合 (不再是打開 ChatGPT, 請他寫完 code 後再貼進 IDE)。這時操作方式整個翻轉過來了, 你可以以整個 Repo 為基礎來跟 Copilot 討論, 你可以直接 @ 要參考的檔案, AI 的回答也可以直接 Apply 到你編輯中的視窗, 不再需要你不斷的複製貼上

到了最近半年, 這些動作更高度收斂了, 甚至給 AI 的 instructions 都收錄到檔案了, 例如 ```/.github/instructions.md``` 這類檔案, 你不再需要每次開啟 Chat 就說: 

> "  
> 你是個 AI coding 助理, 你要 blah blah blah …  
> "


於是越來越多團隊發展出自己的工作流程, 把過去團隊的開發規範, 程式碼撰寫原則, 文件規則等等各式各樣的規範, 都放到 instructions 內了。你只要開啟 VSCode, GitHub Copilot 自然就讀懂你的開發規範了, 你問他的問題他都會配合你的開發規範來回答你…

這整串的發展過程 (不過兩年的時間), Prompt Engineering 已經從 "對談" 一路發展到 "文件" 了。現在文件的角色, 已經變成 "給人看" + "給 AI 看" 的交集了。以前寫文件是很痛苦的事情 (因為寫了也沒人看)，而現在寫文件是很開心的事情 (因為 AI 會看，而且會照做)，而且寫文件也不用你自己一個一個字打出來，也可以由 AI 代勞幫你把 80% 的內容都寫完。

之前在研討會跟幾個朋友聊過, AI 會大規模的改善 "軟體工程" 這件事。軟體工程其實有很多很棒的 practices, 例如寫文件, 寫測試, 開發規範等等。但是最終都礙於 "人力不足", 總有一堆理由說我程式都寫不完了哪有空寫文件這類 "理由"。AI 的出現, 一方面大幅降低這些 “文件" (也包含測試等等其他形式的產出) 的產生成本, 另一方面也大幅提升 "文件" 被 AI 使用的範圍。文件瞬間變成跟 AI 溝通最有力的管道, 文件變的 容易寫 (AI寫), 有人看(AI看), 有人用(AI會照做), 變成整個 AI 強化的工作流程的要角。

--


這演進過程, 是我對 AI 時代 "文件" 重要性的理解, 回頭來看 A16Z 的趨勢報告, 完全就是講這回事啊。不過沒有經歷這些過程的朋友可能無法體會它是怎麼發生的吧, 在實戰的過程中, 其實要綜合好幾個發展 (例如: 包含這報告後面提到的 MCP, Async, Template 等等)。等這系列後面我再舉幾個應用案例, 讓大家體驗看看, 文件實際上是怎麼演變成 AI 協作的關鍵角色的。




## 2025/06/26, 文件即程式實例

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1315125470622261](https://www.facebook.com/andrew.blog.0928/posts/1315125470622261)

--

前一篇談了這兩年大家用法的改變 (從 prompt 逐漸轉移到 document) 的過程, 再來我想舉個實際的使用案例來說明。這類案例我碰過好幾種，今天先談一個: document as code (對應到我九年前的文章: [Blogging as code](/2016/09/16/blog-as-code/)) ...

其實我推 “document as code” 的想法很久了, 簡單的說就是把文件當作 code 一樣處理。用寫 code 的工具跟流程來寫 document ( 工具挑 vscode 之類的, 格式用 markdown 首選 )；版控跟儲存則直接沿用 git ，文件的發行則直接用 ci/cd pipeline 發行靜態網站，一切都很合情合理。

不過在過去，這樣做的效益就是統一 code 跟 document 的工作流程與工具鏈而已，從效益來看也是有賺，大約可以達到 1 + 1 = 3 的效益，爆炸性成長就還不至於, 也因此 "document as code" 也還未成為 "must have" 的流程。

不過這兩年開始不同了，就是因為 AI coding。知道為何我上一篇要花時間聊 “document” 如何逐漸變成 prompt 的載體嗎? 因為越來越多資訊要餵給 AI (agent)。你一句話要跟別人說，你會用講的。你要跟 100 個人說，要說 100 次，你會寫文件叫對方看。把 AI 當作人來看待，這也是一樣的道理。LLM 的 context windows 不需要長期都放著整份文件內容，只要放 filename，搭配合適的機制 ( RAG or FileSystem MCP 之類的工具 )，LLM 就可以像虛擬記憶體般，在 LLM 有需要的時候再載入 (現在進階到 LLM 生成的資料也可以寫在 document 暫存了, 後面對話有需要再靠 MCP 拿出來..)。

於是，現今絕大部分的人，在使用 github copilot / cursor 這類 AI IDE 的時候都這麼做了，若算上 "虛擬記憶體" 的機制，整個 repo 邏輯上都可以當作 "virtual" context window 了。把常用的 prompt / rules 放在 repo 內 ( 當作跟著 repo 的設定 )，把開發相關的需求與規格文件放在 repo 的 /docs 下，把對應的程式碼放在 repo 的 /src 下，整份專案一起版控，一起發布。AI 就不斷的在 /docs 跟 /src 之間替你 "翻譯" 與驗證，逐步完成開發的任務。

當 AI 能有效處理 documents / source code 之間的對應時, 就開始有 1 + 1 = 10 的效益了。現今的 vibe coding 對應的 repo, 文件都占很重要的比例，因為日常開發的流程改變了，大致上變成這樣:

1. 我要開始開發一個功能，我先看文件，找出 requirement 在哪邊，告訴 coding agent 按照這需求來實作..
2. 文件沒說的，我用 agent mode 直接說 ( 或是 create issue ) 告訴 coding agent 該做什麼..
3. Agent 處理完之後，會直接產生文件或程式碼告訴你處理結果 ( report, issue, message 等 )
4. 你會先 review 文件，來確認結果是你要的，再來 review code 看看是否真的是那麼回事，沒問題並且通過 unit test, 就 merge / commit ..

過去很難整套都吞下來的軟體工程流程，尤其是大量的文件跟測試這部分，現在都垂手可得了, 要落實他不再是奢侈的行為 (人力很貴啊)。這改變我覺得回不去了，改變的速度只會越來越快而已。標準的軟體工程 (甚麼都要有文件，文件跟程式碼要維持一至) 會越來越普及，將來任何一個小團隊都有能力做得到。

如果文件開始能跟程式碼有效的 "翻譯" ( 叫 AI 按照需求文件寫成程式碼，我覺得就是在 "翻譯"，把 document 翻譯成 code 的過程就是 vibe coding )，逐漸的每個人就只會想講 "母語" (自然語言) 了。程式語言 對大部分的人來說都是外來語 / 外星語，那是機器世界的母語，不是人類的。當翻譯能力成熟到某個程度，文件就是溝通的工具了。跟 "誰" 溝通? 當然是 "真人" ( developer, user, product owner ), 以及 AI agent, 以及各式各樣的 tools ... 我想這才是這個 "趨勢" 想要表達的, "**docs are evolving**", "**documents are becoming a combination of tools, indices, and interactive knowledge bases**".

實際上, 我自己跟 AI 協作的方式就已經是這樣用了, 不知不覺文件的產生數量變多了, 心態上也改變了, 我不是為了 "要寫文件" 而寫, 而是為了 "要讓 AI 一次能讀懂我要什麼"，並且要重來的時候不用再從對話複製貼上一大串文字... 無形之間就變成這樣的結果: 靠文件溝通。


## 2025/07/21, Context工程與文件

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1337243908410417](https://www.facebook.com/andrew.blog.0928/posts/1337243908410417)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-9.png)

Document, 在 Vibe Coding 當道的年代 (也不過才半年) 突然之間變成顯學。兩年前 ChatGPT 爆紅, 當時大家談的是 Prompt Engineering, 現在談的是 Context Engineering, 差別在哪? 差別在於模型理解能力，跟使用工具的能力都變強了。Prompt 寫得好不好重要性越來越低，更重要的是 "對的資訊" 有沒有被放到 Context Windows 內? 跟 RAG 奮鬥過的各位應該知道我在講什麼 XDD

AI 要能處理越來越複雜的任務，相對你要給他的 context 就越來越多。你有可能在 “Prompt” 內把所有資訊都打完嗎? 對比人跟人的溝通，複雜度到某個層次，就會從跟你交代事情始末 (用講的)，變成給你看文件 (都寫在這裡了，你看完我們再討論)。於是，驅動 AI 完成任務的 context 來源，就從 prompt 逐漸轉移到 document.

所以，現今你看到大部分的 AI (尤其是 vibe coding) 工作流程，工作方法，都在強調 context 跟 document. 上禮拜 AWS 推出的 Kiro, 就是一套以文件驅動開發而設計的 IDE。

文件已經變成開發流程的 context 了, 有點像古董的作業系統會有的 "virtual memory", document 跟 context windows 的角色也類似。文件可以儲存無限的內容，而模型的 context window 有限，當下不重要的資訊就可以從 context windows 移除 (寫回檔案)；當後面步驟需要時可以再透過 (MCP) tools 把資訊從檔案放回 context, 因此你工作的每個步驟，如何精確的掌控這步驟要 "載入” 那些內容就很重要了，這也是 context engineering 在談的技巧。

而文件, 尤其是 markdown, 容易閱讀也容易編輯 (還方便版控), 就成為首選的格式了。你可以拿 document 當作 requirement, 也可以當作 design, 甚至可以當作 tasks ( todo list ), 當你決定變更設計，Agent 可以先幫你列出 100 個工作項目 ( 先存放在 tasks_md ) 就不會被忘掉了，之後 AI 不時來 tasks_md 查看，一個一個任務幫你完成後銷掉, 直到完成任務。這時 tasks_md 就能扮演 "長期記憶" 的角色，不但記得，而且目的很明確 (就是 todo list)。各種用途的文件, 組合起來讓 AI 能夠隨時讀取, 隨時修正任務目標。Agent 就能從過去只能依據 128k context window 的資訊給你答案，提升到 (體感) 能從幾百 mb 文件內的資訊給你答案。

實際上的應用，我看過同適用到爐火純青的案例… 有同事在 instructions_md 寫了這麼一段:

```

(濃縮內容)
當我工作到一個段落，或是有重大變更的時候，請幫我把時間，以及摘要資訊紀錄在 dev-notes_md 內。
(何謂 “告一段落" 或是 "重大變更"，他另外有定義，我就略過了)。

```

這時 cursor (其他 IDE 也一樣) 就搖身一變，變成開發祕書了，你改了一堆 code, 他就在背後默默的幫你摘要筆記下來了。這跟 Git Commit 不同，有時候我寫失敗的東西我不會 commit, 但是會留下工作日誌為何失敗，哪裡失敗，作為下次重來的參考…

分享一下他的某個 side project, 這些 [dev-notes](https://github.com/lis186/taiwan-holiday-mcp/blob/main/docs/dev-notes/README.md) 就是這樣來的:

GitHub Repo: [/lis186/taiwan-holiday-mcp](https://github.com/lis186/taiwan-holiday-mcp/)

(同事寫的 MCP, 台灣假日查詢..., 完整連結我放留言)

這類例子還有很多，例子舉不完，就點到為止就好。包含前陣子我提的 vibe testing, 也是用同樣概念把整個流程串起來的。”文件在進化 / Docs are Evolving… “ 確實如此。單純看趨勢報告，我的感受其實不會那麼強烈，而是實際經歷過這些變化，再來看報告整理，就會有一種突然想通的感覺，原來我一直在嘗試的就是這麼一回事啊..

看趨勢報告，是個很好的練習。如果你能找到一份你正在努力領域的趨勢報告，別看完就放掉了，好好地往下挖。趨勢報告描述的場景，你如果能一步一步拆解推演，直到跟你現在在做的事情連貫起來，那麼這領域你大概就能想的夠透徹了，這些經驗跟手感才會是你的。

這也是我為何看到這篇報告，會願意花時間，一項一項地把我自己經驗貼出來，因為想通了，這些累積的經驗就是我的了，希望留下這些訊息，也能讓更多人想通這些脈絡。

一樣，相關連結我放留言，文件在進化的主題就到這邊，請期待下個主題  😃




# 4, Templates to generation

原文標題: Templates to generation: Vibe coding replaces create-react-app 
我當時在 FB 談這主題的 PO 文:

- 2025/06/27, 範本到生成轉變


## 2025/06/27, 範本到生成轉變

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1315999790534829](https://www.facebook.com/andrew.blog.0928/posts/1315999790534829)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-8.png)

週五下班，先來談這題比較不燒腦的 templates to generation 好了, 過去起始一個新專案的基本動作: 從 project template 生成一個初始專案的作法，會完全被 AI coding 取代.. 。這點我完全認同，甚至覺得不只是 project template, 連帶的各種形式的 code generator, 各種 search & copy / paste code 的服務 ( stackoverflow... ) 都有一樣的命運。

這些工具或是服務，廣義上來說都是 code generation .. 而藉由 LLM 來 gen code 效果比起其他方式好太多, 最主要的原因就是 LLM 能理解你的意圖, 而這些能力讓你能用敘述，或是用文件，就足以產生夠精準品質夠好的程式碼，讓其他樣板類型技術完全沒有任何利用的價值..

文章的敘述則是更精確了，比起 project template 是給你一個 "通用"，並且搭配接受度高的 framework ( 泛指 tech stack 選擇 ) 的起始專案樣板，而透過 AI 生成，你可以自己選擇 framework / tech stack，精確自訂，符合你使用情境與需求的起始專案。兩者之間的差別只是幾分鐘的時間差，我想每個人都知道該選 AI coding …

繼續往下前，我摘要一段文章的內容:

> "  
> This unlocks a new distribution model in the ecosystem. **Instead of a few frameworks sitting at the head of the long tail, we may see a wider spread of composable, stack-specific generations** where tools and architectures are mixed and matched dynamically.  
> "

換了方法，你多了自主性。你不再會被 template 限制了你的技術選擇 ( 不會被迫選擇主流 framework, 對 tech stack 有選擇與替換的彈性 )。這些能力甚至放大到極致，如果你專案初期還無法決定 tech stack, 你甚至可以用很低的成本，把你專案需求用每種 framework / tech stack 都生一份出來驗證看看再決定… ( 反正就幾十分鐘的事情)。

看趨勢報告，對各位而言可不是選擇題，決定挑選 AI coding 就結束了，後半部我分享一下這主題延伸的經驗跟想法。過去我們團隊做了類似的事情: 自訂 project template ...，其中一個要解決的問題就是，每個新專案，都要申請一大堆 infra 服務，而這些服務很難懂 (一堆 naming rule 要遵守)，於是我們搭配開發了 SDK, 把部分規範寫在 SDK 內，另外留個 config, 把申請後的資訊填進去，SDK 就會自動轉譯那些難搞的部分，讓專案能 ASAP 就順利完成部署上線測試。

這樣的做法的確有效，而缺點是我們必須花費心力去維護這 project template.. 雖然從上面的結論來看，以後都改用 vibe coding 就好了，但是投資在 SDK 身上仍然是必要的，因為 SDK 封裝了很多複雜的規則，即使不需要 template，他仍然能精簡你的作業流程，也能讓 vibe coding 能少處理這些需求，少產了一大段 code，效率跟正確性也都會提升。

當你越依賴 AI 生成 code, 你就越需要花費心力來提高 AI coding 的成效，透過各種手段降低需要產生的程式碼數量，以及降低需要解決需求的複雜度，都是很有效的手段，不論你是不是用 AI coding。我覺得是看這類趨勢報告必要的思路。除了 SDK，如果流程上若也能對應調整 (我最推的是 TDD)，讓 vibe coding 過程能合理的分段產生 + 人工確認，則能在另一個面向大幅降低 AI 繞錯路的機會。

兩個月前我貼過[一篇 PO 文](https://www.facebook.com/share/1B73gnprc3/) ，大意是 vibe coding 的技巧, 講的就是搭配 TDD 的精神來引導 AI 寫出你要的 code. 先讓 AI 替你寫出 interface，你驗證 interface 是否如預期。再來則是針對 interface 產生測試 (同樣你要確認)，這時測試應該會失敗 (紅燈)。再來是讓 AI 把 code 寫完，過程中讓每個測試從紅燈變綠燈。這流程會有效，主要原因都是針對 vibe coding 的弱項 (其實也是人類 coding 的弱項啊)..

1. 一次寫越多 code 越容易錯，TDD 有系統有結構的切成多個步驟分別進行
2. 一次 review 越大包的 code 越難抓出問題，你越早準備好測試，TDD 就能分攤你 review 的負擔
3. TDD 的切法分成 interface, test code, test result .. 都能跟工具對應，每個階段都能 build / run test，你可以第一時間靠工具就抓出低級錯誤

如果你想知道我以前聊過什麼 SDK, 可以看這幾個研討會的簡報
- 前陣子的熱門話題: [vibe coding, where 2 engineers can now create the tech debt of at least 50 engineers](https://www.facebook.com/share/1B73gnprc3/)
- DevOpsDays Taipei 2021 簡報: [DevOpsDays Taipei 2021, 大型團隊落實 CICD 的挑戰](https://www.facebook.com/share/1FrPrLzcEC/)
- .NET Conf Taiwan 2019 簡報, [大規模微服務導入](https://www.facebook.com/share/1CQCsRneyV/)




# 6, Accessibility as the universal interface

原文標題: Accessibility as the universal interface: Apps through the eyes of an LLM
我當時在 FB 談這主題的 PO 文:

- 2025/07/22, 無障礙設計, AI 的通用介面



## 2025/07/22, 無障礙設計, AI 的通用介面

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1338108878323920](https://www.facebook.com/andrew.blog.0928/posts/1338108878323920)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-10.png)
圖片來源: [Playwright architecture simple breakdown](https://samedesilva.medium.com/playwright-architecture-simple-breakdown-69f64ea4de3d).


再來談談 UI 的設計, 這次是無障礙 ( Accessibility ) 設計的重要性…

過去我沒有那麼在意 "無障礙" 設計的重要性，但是最近這半年我改觀了，因為這是讓 AI 也能使用應用程式的關鍵設計。看到這趨勢報告的這段我很認同這觀點。這一切都要從我們期待 "Agent" 能做甚麼開始談起。

兩年前我在談 AI 的可讀性，你的服務 ( API ) 能否正確地被 AI 理解並加以運用? 以我實作安德魯小舖的經驗來看，良好的 API 設計 (符合邏輯)，明確的規格定義 (符合 OpenAPI Spec) 都是重點。而這兩年來的進步，AI 使用工具的能力，已經從 API 進步到 UI 了。例如 Anthropic 推出的 Computer Use 就是一例, 只要你願意, AI 可以像機器人一般代替你操作 / 使用 Application..

如同 API 有設計要點，能讓 AI 理解與運用，那麼 UI 呢? 看了這段，我覺得很貼切，那就是 "無障礙設計"。我先用幾句話，交代一下甚麼是 "無障礙設計" :

> "  
> 無障礙 ( Accessibility ) 設計的基本精神，就是讓所有使用者，包含視覺障礙、聽覺障礙、行動障礙、認知障礙的使用者都能順利操作的設計指南。具體一點來說，視障人員需要的是能放大 (若能去除雜訊更好) + 螢幕朗讀；聽障需要的是影片語音應該有替代文字或字幕，而操作障礙的人可能無法使用鍵盤或滑鼠，必須有更簡易或是可替代的操作方式等等…  
> "

這些設計，跟 AI 有何關聯? AI 各種領域的發展方向，都是要變成使用者的 "代理人"，替你處理所有事務。AI 必須理解你操作軟體時的 context。目前的 AI 還是純軟體，不是機器人，沒有真正的視覺跟觸覺，因此軟體形態存在的 AI Agent, 能理解操作軟體的管道，無障礙的設計就成了最佳的管道。

AI 無法真正 "看到" 操作畫面。即使已經有 Computer Use 的能力 (不斷的擷取螢幕畫面)，現今的運算能力其實還沒辦法到 100% 可用，對於視障人員的設計，就等於幫了 AI 的大忙。同樣的，各種面向的無障礙設計，等於都替沒手沒腳沒眼睛沒耳朵的 AI 開了一扇窗，讓他也能理解應用程式狀態。

所以，文章內舉了幾個例子，越來越多這類代理軟體，開始會要求作業系統的 Accessibility API 存取權限，就是這個原因。另外我舉一個例子，是工作上實際碰到的: UI automation:

應該很多人都用過 Playwright MCP 了。如果你對 Agent 自動操作的要求沒有擴及所有的 desktop app, 而只限定 browser 的話，那 Playwright MCP 是個好工具。不過當你認真使用時，你會發現畫面上明明 "登入" 按鈕就在那邊，但是 AI 就是找不到… 一個簡單的操作嘗試了好幾次才會成功..

我曾經挖過幾套類似工具的設計, 有的工具會傳回 HTML 讓 AI 判讀，這類的設計通常找得比較準，但是效率很糟糕，HTML 很容易就超過 context window .. 而 Playwright MCP 不同, Microsoft 會先精簡 HTML, 只轉出重要的節點變成 YAML, 但是很多資訊就此遺失, 導致 AI 無法找到網頁上的重要資訊…

過程中我越想越不對, Microsoft 應該不會做這種蠢事才對, 一定是我們忽略了什麼.. 結果強者我同事找到關鍵了, Microsoft 將 HTML 精簡成 YAML 的過程中，會參考網頁的 Accessibility 標記, 簡單的說，只要你的網頁有遵循 Accessibility 設計, Playwright MCP 就能精準還原結構, AI Agent 就能精確地按照你的語意操作網站。

這我覺得已經是個重要的趨勢了，AI 的趨勢真的會改變很多事情。我在查 Accessibility 資訊時，查到世界衛生組織 (WHO) 做過統計，全球的視障人數達 3.38 億，聽障 4.3 億.. 從這數字可能有些開發人員還不會把無障礙設計擺在第一位，但是如果每個使用者都同時會運用 1 ~ 5 個不同的 AI Agent 呢? 把這些都有無障礙設計需求的 "使用者" 算進去的話，這已經會變成未來設計的主流了。

如果你不希望未來 AI Agent 操作你的應用程式會碰到障礙的話，開始做好無障礙的設計吧。最後我用這段趨勢報告的標題做結尾:

**Accessibility as the universal interface, Apps through the eyes of an LLM.**



# 7, The rise of asynchronous agent work

## 2025/07/23, 非同步Agent崛起

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1338994928235315](https://www.facebook.com/andrew.blog.0928/posts/1338994928235315)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-11.png)
圖片來源: 這張圖的出處, 來自 Happy Lee 的部落格文章: [軟體產業的未來猜想](https://happylee.blog/rs/software-future/)

這類趨勢報告, 越看越覺得很考驗你的解讀能力… 這也是一個, async agent 的崛起…
今天要談的是 第七個趨勢預測:

(7) **The rise of asynchronous agent work**


如果只看報告的敘述，短短兩段文字，其實沒有帶到太多資訊。我看報告的方式就像是算命，報告告訴你未來會發生什麼事，而我會自己推敲試著解讀現在到未來的因果關係。如果想通了，那我就有判斷的能力了。因此這份趨勢報告，我每一段都試著用這樣角度解讀，在沒人可以給我標準答案的時候，我還能靠自己的判斷能力來評估一下可信度。

非同步 (async) 的作業模式，其實不管有沒有 AI 都是必然的結果啊。A16Z 把這發展趨勢寫在這裡，要點出的重點到底是什麼? 我覺得是 AI 的進步會 "如何" 影響我們使用工具的方法。

我還是從 vibe coding 當案例來切入這題吧，把實際的案例套進去之後, 你會發現你突然就能想通報告想表達的是什麼了。AI 發展至此，幻覺仍然無法完全避免，因此各種 AI 強化的工作流程，免不了在關鍵環節需要跟 "真人" 互動、協作、確認結果。這些互動，最吃 “真人" 的時間，這是最根本的瓶頸，人的專注時間是無法 scale 的.. 

因此，優化的方向就兩個極端，一個是加速，讓互動等待的時間越來越短；另一個是批次，讓處理流程不要是線性的，可以累積到一個程度一次確認。而隨著思維鏈，推理模型的發展，回應時間其實越來越長，但是相對地模型能力也越來越強，可以獨立處理的任務越來越大，也因此開始可以長時間獨立作業了 (例如: 有些 Agent 已經可以不需要人為介入，獨自處理超過 30min 的任務了)

模型能力的進步，朝向推理時間越來越長，思維鏈的過程越來越長，能負責的任務規模越來越大，Agent 的互動模式越來越往非同步發展。最近在幾場研討會，分別看到保哥跟董大偉老師各別 Demo 他們團隊的運作流程，不約而同的都是在 Azure DevOps 上面，整合各種不同身分的 Agent ，來完成日常任務:

兩位都示範了這樣的情境:

1. 在 Azure DevOps 建立了 task, 在裡面用詳細的 prompt 交代了要改什麼 code..
2. Create Task 的 webhook 觸發了 Agent 來接手任務, 這 Agent 在 Sandbox Pull Code 下來解 issue, 改完 code 跑完 test, 發 PR , 並且更新 issue, 花費 15 ~ 30 minutes
3. 同時間可能有多個 issue 被開出來, 在雲端有多個 agent 同時在執行任務, 隔天上班時負責人逐條 issue 確認能否 merge PR, 若不行就再重複一次, 直到完成為止。

這整個工作流，比起 AI coding IDE ( ex: Cursor ) 來說，更像你把開發任務 "外包" 了。高度互動的 AI coding IDE 比較像是 Pair Programming, 而模型能力越來越強，強到能獨立作業，互動模式就會變成這樣了。

我認為，與其說 "非同步" 是個趨勢，更貼切的說法應該是 "非同步" 會是未來必然的互動方式。在這必然的發展上，真正重要的不是 IDE + Agent, 而是像 GitHub, Azure DevOps 這樣的協作平台 + Agent 的組合。唯有有非同步協作的能力，你才 "養" 的起 (這裡的 "養" 不是指成本，而是指能否讓多個 Agent 有效率的協作) 多個 Agent 不眠不休替你工作。

所以，想通這趨勢是怎麼變化的，我歸納幾個關鍵點給大家參考:

1. 模型能力越強，你越需要一個外包任務給 Agent 的管理系統 ( 就是 issue + git 啊 )，集中管理文件、程式碼、任務。這管理系統讓這非同步的協作模式可以有效率運行
2. 工作方式改變，你要能累積足夠的 context 讓 Agent 能夠長時間獨立作業，資訊在傳遞或指派之前都要先儲存 （文件化），因此前兩天聊到的 " docs are evolving” 就是必要條件了，所有任務都是先更新文件，再要求按照文件執行
3. 降低互動的頻率, 最主要就是 review AI 產出, 不斷修正的往返次數。預先寫好合適的 coding guideline (預防 AI 寫出你不想要的 code)，盡可能在前期的階段 (建立需求) 就做好介面設計以及準備好 test case (寫這通常很快，用互動的方式當場驗證)，累積越多這類能讓 AI 自己檢驗自己的素材，你在非同步作業階段得到的產出物品執會越好。
4. 互動式的工具仍有存在價值，但是會越來越轉移到前後階段，前段在修飾需求文件的細節，後段在修正 agent 沒做好的小 bug 收尾。

當你能選擇時，優先選擇非同步的協作模式。除了最節省你的互動時間之外，非同步是最能 scale 的工作模式。你可以一次開出 10 x issues 讓 10 個 agent 同時工作，但是你難以一次跟 10 個 agent 進行 pair programming. 前面的 (1) (2) (3) 有沒有做好，就是你將來處理能力能不能 scale out 的關鍵

而這演進不會一夜之間發生，但是已經慢慢在進行了。就看這兩年 (尤其是 developer) 大家常用的工具跟使用方式變化，就能察覺這趨勢:

1. ChatGPT (GPT3.5 年代) 一開始什麼都是 "聊天"，完全互動的介面
2. ChatGPT Research, 開始要花上十幾分鐘, 因此也開始有了 Task 的通知 & 排程機制
3. GitHub Copilot / Cursor, 開始出現互動的 AI coding IDE
4. 開始出現 Claude Code, OpenAI Codex 等等各種 CLI 的 coding agent
5. ( 有了 CLI, 這些 coding agent 開始能被放在各種 Batch 作業的場合, 例如 create issue 的 callback )

逐漸的，每個團隊的開發平台 ( ex: Azure DevOps , or GitHub ) 開始會變成 "軟體開發" 的外包中心。從最基本的版控 ( 工廠生產內容的倉庫 )，變成需求管理 ( 下單與出貨管理 )，交付的管理 ( CI / CD, 就像是工廠的物流一樣 )，到外包人力的資源調度 ( Agent Auto Scaling, 有需求需要處理，馬上就能 allocate Agent 起來接單，處理完畢後就能釋放資源 )

這不就是未來理想的樣貌嗎? 這段原文沒有給圖，我用先前在 Generative AI 年會，我老闆的一頁投影片當作結尾，在闡述的就是這樣的場景。

如果你認同這樣的想法，其實現在就要開始準備，往主要發展路線移動了。



# 8, MCP as universal standard

原文標題: MCP as universal standard: MCP is one step closer to becoming a universal standard 

## 2025/07/24, MCP 邁向通用標準

Facebook 連結: [https://www.facebook.com/andrew.blog.0928/posts/1340022954799179](https://www.facebook.com/andrew.blog.0928/posts/1340022954799179)

--

![alt text](/images/2025-09-28-reading-a16z-emerging-developer-patterns-for-the-ai-era/image-12.png)


終於來到最後一段, 今天要聊的是 ( 8 ), **MCP is one step closer to becoming a universal standard**.

MCP 將會 (已經?) 成為 AI tools 的標準規格, 這句話現在應該沒人懷疑了吧? (既然這樣還寫在報告裡幹嘛 XD) 即使如此，我覺得還是有必要把背後的脈絡談清楚，這樣你會更清楚知道接下來該投資在那些地方..

MCP 的介紹，我就省了，多的是講的比我清楚的人。我想先談一下 MCP 在未來的定位到底是什麼。過去 20 年，業界的標準規範，大家談的是 API，從 2002 [貝佐斯對內的備忘錄](https://www.techbang.com/posts/88124-api-mandate-amazon) 要求全公司都要落實 API first 開始，API 一直是軟體產業的標準規範，雖然標準一直在進化，但是終究就是 API ( REST, SOAP, gRPC… )

在 Cloud / SaaS 年代, 建立生態系, 系統整合的要角是 API, 沒有開放 API 的系統終究是個孤島。只有開放 API 別人才有機會跟你深度整合。從 DX 到 EcoSystem, 這就是這產業的遊戲規則。現在到了 AI 時代，過去在談的 SaaS 逐漸變成談 Agent, 這時擴大影響力的方式, 除了讓自身的產品 ( Agent ) 更強大之外, 觸手往外申的管道也從 API 升級到 MCP 了。

簡單的說，串接 SaaS 的是 API，而現在串接 Agent 的則是 MCP。去年 DevOpsDays Taipei 我談了 "[從 API First 到 AI First](/2024/07/20/devopsdays-keynote/)", 內容談的就是 API 到了 AI 時代該做甚麼改變。當時 MCP 的規格還沒問世 (第一版是 2024/11, 由 Anthropic 提出)，而我提了幾點重大的改變:

1. 未來呼叫 API 的會是 AI, 而不是開發人員
2. AI 要能有效運用 API, 良好合理的設計 (合理 AI 才會用) + 清晰明確的規格 (規格文件就是用 API 的 Prompt) 會是最重要的關鍵

其實這些，後來都發生了，技術上的綜合結果，就是 MCP。未來的 Agent 就是聰明的代理人，有聰明的大腦 (LLM) + 給他精良的工具 (MCP)，他就能替你完成眾多任務。簡單的敘述一下 AI 執行任務的情境吧，AI 要能完成你交辦的任務，首先要有充足可靠的資訊來源。除了你直接給他的 Prompt 之外，剩下的就是依據這些線索，自己找工具 (例如: search engine, file system, … ) 去取得進一步的訊息。

資訊足夠，做出決策後，就要執行動作了，這邊也一樣，透過 MCP 跟外界接軌，開始輸出資訊，或是透過 MCP / API 來調用其他系統完成任務。只有聰明的大腦還不夠，還要有靈活的手腳才行，而 MCP 則是幫你把手腳接到大腦的標準規格。前陣子流行一張圖，就是拿 TYPE-C 來比喻 MCP 的圖，我自己覺得這圖不是很好理解，因為重點不是 USB，更不是 TYPE-C ，而是在 "大腦" (PC) 需要標準方式連接 "工具" (設備)，才能有效協作運用工具完成任務。因為需要，所以催生了 USB 這樣的標準連接規格來統一這一切。

因此，可預期的未來，整個生態系都是以 AI Agent 為主的時候，軟體市場就是這兩大主軸了: 一個是發展各種領域，或是各種高度個人化的 Agent, 另一個則是各式各樣給 Agent 使用的工具 MCP 了。軟體廠商不論是賣 Agent 或是賣 Tools, 都不能忽視 MCP 這標準規格。看到這邊，再回頭重看一次標題:

( 8 ), MCP is one steo closer to becoming a universal standard

有沒有覺得看起來更合理了? 既然趨勢都已定案，接著來看看該如何往 MCP 這路線邁進… 該考慮的不是該不該做, 而是該做什麼… 你要提供什麼樣的 MCP? 該用甚麼方式提供? 我從業務角度到技術角度，給大家幾個我的想法:

未來的市場，就是 Agent + Tools, 如果拿真人來比擬, 職場上有各種 "專家"，而這些專家也會用 "專業" 的工具來做事創造價值。因此:

1. 你的 MCP (工具) 必須符合 Agent (專業人士) 的需求來設計
2. 貼著業務流程的 context 來設計。越貼近 context 就越不需要複雜的操作, 對 Agent 而言就是花費越少的 Token
3. 威力越大的工具，越需要安全機制。工具在 "該做" 的範圍內越強大越好；而在 "不該" 做的範圍內則相反，完全不能做最好。該不該做，也一樣，貼近 context 是最好的設計。MCP 會採用 OAuth 不是沒道理的, OAuth 早已被證實是跨系統認證授權的最佳做法

現在，跨入 AI Agent 動作最快的 "專家" 們，就是 developer 了, 看看你們手上各式各樣強大的 coding agent 就是一例, MCP 也是最快從這個領域成長起來的, 而從 2025/Q2 開始, 也開始看到各種不同的領域 MCP 也出現了, 我就講一個我熟悉的電商: Shopify, 也推出了 [Storefront MCP](https://shopify.dev/docs/apps/build/storefront-mcp/servers/storefront), 兩年前我試做的實驗性專案: [安德魯小舖](/2024/01/15/archview-llm/#1-%E5%AE%89%E5%BE%B7%E9%AD%AF%E5%B0%8F%E8%88%96-gpts---demo), 現在已經完全可以使用了, 只要在支援 MCP 的 AI Chat 上安裝, 你馬上可以實現聊天購物的場景。

Shopify 的 MCP 設計還挺有意思的，是我目前為止看過設計最精巧的 MCP, 這個有機會我另外在 PO 文來挖一下他的做法 (更新: 已經有專文介紹了, [讓 Agent 懂我的部落格: MCP-first 的服務化設計 / 4, 參考 Shopify / Context7 的 MCP 設計](/2025/09/16/chat-with-my-blog/#4-%E5%8F%83%E8%80%83-shopify--context7-%E7%9A%84-mcp-%E8%A8%AD%E8%A8%88))。 回到這主題，代理人 + 工具 是個完美的搭配，兩者都會支撐對方的發展，缺一不可。這剛好帶出這篇報告，最後兩個我沒提到的主題，在這邊交代一下之間的關聯吧。這份 A16Z 趨勢報告最後兩段我沒提到的是:

( 5 ). Beyond .env: Managing secrets in an agent-driven world  
( 9 ). Abstracted primitives: Every AI agent needs auth, billing, and persistent storage

其實, (5) 就是在講安全機制, 為了更貼近 context , 更好的安全機制是像 OAuth 這種依照需要才取得授權的作法，而不是你拿到了工具就無條件獲取權限 (透過 .env 就沒這種彈性)。而 (9) 則是 Agent 越來越普及後的必然發展。就跟軟體跟網路成熟後，必然的發展就是 Cloud, 也因此衍生出 Public Cloud / PaaS 等生態, 所有你開發軟體需要的工具跟管理體系都會具備，而未來這一切也會發生在 Agent 身上。

—

最後，總算把這篇趨勢報告的解析寫完了。我想寫的不是 “翻譯" 或是 "摘要” 這篇報告給大家看，而是想把報告背後指引的脈絡想清楚，並且把它寫下來而已。想通這些，這報告才不會只是報告，而是能真正指引你發展或是投入心力的方向。

報告導讀到這篇為止告一段落，感謝大家的捧場，之後我會把這些 PO 文收成一篇文章。之後如果還有看到值得細細品味或是分享的文章，我會繼續用這種方式分享我的想法