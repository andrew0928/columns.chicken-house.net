---
date: 2025-08-14
datetime: 2025-08-14T20:23:45+08:00
timestamp_utc: 1755174225
title: "今天是抱怨文, 抱怨一下 Claude Desktop 對 MCP 的支援程度… 有在開發 MCP"
---

今天是抱怨文, 抱怨一下 Claude Desktop 對 MCP 的支援程度… 有在開發 MCP server, 有想要加入 Resources 支援的可以關注一下..

有人認真用過 MCP Resource 嗎? 有人在 Claude Desktop 上面用過嗎? (我沒有 XDD), 我本來很天真的想, MCP 是 Anthropic 提出來的標準, Claude Desktop 是 Anthropic 的主力用戶端產品, 支援度應該是最好的吧 (咦?  於是很開心自己寫了個 MCP server, 在 MCP Inspector 測試 OK 就掛上 Claude Desktop 用了..

接下來，我就逐一介紹 Resources 的功能, 然後一一戳一下支援程度好了 XDDD, MCP 定義了三種主要的服務類型是有原因的, 分別是 Prompts, Resources, Tools .. 想像一下你在用 AI 聊天都在做甚麼? 第一, 你要學會怎麼下 Prompt, AI 回應才會有效率。再來, 要告訴 AI 的事情多了，你開始會想上傳檔案給他看, 再來 AI 越來越強，你希望它代替你做更多事情，你開始會啟用一些 tools (例如 web search .. ), 授權給 AI 讓他直接用你的 tools 幫你做事

MCP 就是希望服務端能自己準備好這三件事, 封裝成 MCP Server, 就像 Extension 一般, 讓使用者裝上去, 就能無縫的在 Agent 上使用你的服務，這就是 “Protocol” 最主要的目的。因此 Resources 這件事, 就是想要你在用 AI Agent 時, 不用再去網站自己 copy / paste, 有哪些 "Resources", 能夠事先串接好, 讓使用者操作上直接選用就好。

第一個吐槽點:

原來 Claude Desktop 需要使用者 "自己去" 選附加檔案, 然後才選的到 resource 啊… (我還以為按 @ 就能自動選 XDD) 。我把我部落格每篇文章都當成是一個 resource, 共有 400 個, 實作了分頁機制, 每頁 50 筆.. 結果 Claude Desktop 這樣呈現 (圖一)

啊啊啊，只有第一頁, 永遠不會觸發 loading 下一頁的動作.. 我不知道黨名的話就選不到後面的文章了啊... 看了一下 Google Drive 的怎麼就可以? Google Drive 的內容, 我打字都會找到正確的, 明顯不是預先載入的清單… 而是真的會偵測我輸入的內容當場查詢..

再看看 GitHub 的 integration, 更過分了, 有專屬的 UI 票漂亮亮的啊 (圖2), ChatGPT 跟我說這是 Anthropic 客製化的 UI (無從查證，我就暫時信了)… 這很糟糕, 因為我不是 GitHub, 所以我再努力也做不出這樣的 UI 給使用者用… 因為這是專屬功能…

再來看第二個吐槽點:

Resource Template + Parameters, 像這樣: post://{post-id}/summary 的 uri 格式定義。你可以自訂 Resource Uri 的格式 （同上）, 中間挖出參數 （就是 post-id）, 操作上你可以用類似 auto complete 那樣的方式補上 ID, 然後按照 template 補成完整的 Uri, 就可以存取這 resource 了。在 Claude Desktop 上我試半天試不出來，官方文件沒有說，但是國外鄉民好幾個 issue / reddit 都在反映這問題，看來就是不 (還沒) 支援了… 所以我辛辛苦苦刻了半天的 CompleteHandlers 等於白做了 XDD

第三個吐槽點:

對 MCP 各種能力的支援，第三方其實做的好太多了啊啊啊啊… 換掉 Claude Desktop, 改用 VSCode + GitHub Copilot, 狀況就完全不一樣了… 當我在 Agent 那邊點選 Add Context, 來源選 MCP Resources … 不但每篇文章的 Uri + Title 正常顯示, Auto Complete 也正常運作, Resource Template 也正常支援.. Orz (影片3)

往好處想, 我如果在 GitHub Copilot 跟 Agent 對談時, 要插入網站的資源當作 context 時, 有 MCP 的支援是很方便的, 我不用把文章下載下來或是複製貼上, 直接透過 MCP 把整個流程都簡化了, 這是挺誘人的功能。但是這很吃 Client 端的支援啊, 目前看來就 AI IDE 這系列的支持完整一點，官方的 Claude Desktop 嘛.… Orz

好，抱怨完畢，我還是會繼續弄完我的 side project, 等到告一個段落再來分享開發心得 XD

![](/images/facebook-posts/facebook-posts-attachment-2025-08-14-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-08-14-001-002.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-08-14-001-003.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-08-14-001-004.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-08-14-001-005.png)
