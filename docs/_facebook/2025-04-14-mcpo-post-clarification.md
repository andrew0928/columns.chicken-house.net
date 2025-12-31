---
date: 2025-04-14
datetime: 2025-04-14T22:49:28+08:00
timestamp_utc: 1744642168
title: "昨天 PO 文貼太快, 今天幾個朋友看到 mcpo 都敲我問問題, 我才發現昨天貼的內容實在沒什麼條"
---

昨天 PO 文貼太快, 今天幾個朋友看到 mcpo 都敲我問問題, 我才發現昨天貼的內容實在沒什麼條理, 決定重貼一次這篇 .. XDD

主題是: open-webui, 跟 ollama 搭配的好搭檔, 月初推出了一個開源專案: mcpo, 可以將 mcp server, 轉為支援 open api spec 的 rest api server ( 你可以把它當作 mcp 版本的 api gateway )...

這東西能幹嘛? 同時 open-webui 為何要開源這專案? 其實是有原因的。先來看看這東西的作用..。

(1) 最主要的作用，就是把 mcp 轉成 rest api...

我如果把 mcp filesystem 掛上 mcpo ( 可以直接用 claude desktop 的 json config, 參考圖一 ), 你就可以從 http://....../filesystem/docs 看到 swagger UI (圖二), 整個 /filesystem 就是一個可以正常運作的 rest api server 了..

(2) 不過，這能幹嘛? 有點多此一舉.. 接著就是 open-webui 的主要目的了，可以當作 open-webui 的 tool server ...

原本 open-webui 走的 tools 擴充機制, 跟 chatgpt 一樣, 押寶在 open api 身上。大家如果還記得前年底我推出的 "安德魯小舖" 的話，當時就是用 GPTs + Custon Action ( open api spec ) 把 LLM + API 串成一個虛擬店長的。

而 open-webui 也走這路線, 在 settings 畫面你可以直接指定 api endpoint, 只要符合 open api spec 就能掛上去使用。我猜 open-webui 本來也是跟著 open ai 走, 結果三月底 open ai 宣布要支援 mcp, 於是也跟著倒戈了 XDD, 我猜 mcpo 就是這樣來的。

所以，如圖三，把 mcpo 的網址填進去，你的 mcp server 就能正常地在 open-webui 下使用了。你選擇的模型如果支援 function calling, 就能正常地使用 ( 如圖四 )

--

簡介到此為止，接下來是技術評論。

不是我自誇, 我大概研究過這 30 年來各種主流的 "RPC" 協定了。從唸書時代就在碰的 CORBA, Apple 的 OpenDoc, Microsoft 的 OLE / COM / DCOM, Java RMI, 一路到 SOAP, Web Service 等等, 算不完了。所有的 RPC 協定，都會做兩件事:

1. Discovery, 查詢你這 end pont 到底支援那些 " function " ?
以 COM 為例, IUnknown 就有一個 QueryInterface(), 就是做這件事。在 mcp 裡面, 有個 tools/list 指令就是做這件事。對應到 open api, 就是 open api spec 本身 (也就是 swagger 定義檔)

2. Invoke, 直接呼叫指定的 " function ". 在 mcp 裡面, 就是 tools/call, 在 COM 裡, 你透過 QueryInterface 拿到真正的 Interface 後，就能呼叫那個 interface 實作的 method 了。在 open api, 你讀懂 open api spec 的規格後, 直接按照規格呼叫 api 就可以了..

而 mcpo 說穿了, 就是即時翻譯兩種不同的 protocol 而已, 換湯不換藥... 只是規格換衣換而已。

不過，幹嘛脫褲子放屁啊? 說實在話，去年底 mcp 出來的時候，我不是很看好它。他就真的只是另一個版本的 RPC 協定而已。我覺得 open api spec 已經很夠用了 ( chat gpt 支援, open-webui 支援, 連我之前介紹的 microsoft semantic kernel 也直接支援 open api spec 當作 plugins )，實在不必要再生出一種版本，搞得所有軟體開發人員都要佈署兩種協定，真的很麻煩。

不過事情總是出乎意料，mcp 突然爆紅了.... @@, 我唯一能理解的原因是: 他支援 stdio 這種 transport... stdio 是很古老卻又很實用的技術, 我不需要開 port 就能建立穩定可靠的連線。要啟動 process 也很容易, 啟動之後標準的 stdin / stdout / stderror 就建立起來了, 相較於 TCP/IP 還要先啟動 daemon, 設定防火牆等等, 對 desktop application 來說友善太多了。

於是, 隨著 cursor / windsurf, claude desktop 這些支援 mcp 的桌面應用風行起來, mcp 也被拱起來了。不過，stdio 是優點也是缺點。本地端部署很容易，遠端部署就很困難了。

雖說 mcp 也支援 http, 不過只有 SSE ( server send event ), 支援度也不算很普及, 會希望用 http 的, 通常是希望架一套可以多人共用, 而 mcp 也缺乏穿透 desktop application, 直達 user 端的個人化認證機制。這些雖然在 2025/03/26 的更新規格中已經標準化了 ( 開始支援 http, 也支援 oauth2 ), 但是這些都跟目前最多人使用的部署方式 stdio 沾不上邊啊...

所以, mcpo 這開源專案... 你就當作方便使用的小工具就好了。如果你真的有愛不釋手的 mcp server 想把它搬到 open-webui + ollama, 那這是個好解決方案。但是, 如果你的 open-webui 要給多人同時使用, 你就要留意了, 請只使用不需要個人化的 mcp server .. ( 例如我舉例的 file system, 請勿連線到個人目錄, 或是你得替每個仁部署一套專屬的 mcp server, 並且設定成 private tool server ..)

如果你原生的服務, 本身就是 rest api, 為了當紅的 mcp 才特地封裝個 mcp server 的話, 就更不需要用 mcpo 了, 直接讓你的 rest api 就地符合 open api spec, 直接掛上 open-webui 還更直接一點..

mcp 終究是個為了 LLM application 特化的通訊協定, 大規模的服務, 還是以 open api 為主軸才是好方法。

多補充這段技術說明, 是希望大家正確的使用它, 有需要就用, 但是不用刻意。你的服務想掛上 open-webui, 別忘了它原生支援的是 open api spec, 而不是 mcp 啊... 看起來 open-webui 出個 api gateway 型態的 mcpo 來支援 mcp, 應該就是 "應付用途" 吧。我支援 mcp 了, 但是沒把你當主流看待的意思 XDD, 大家也別衝昏頭了, 看到 mcp 很紅就拚了命把什麼東西都往上面掛, 請小心它目前的技術限制 (尤其是安全問題)，敏感的應用請別胡亂部署上去啊，會出大事的。

![](/images/facebook-posts/facebook-posts-attachment-2025-04-14-001-001.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-04-14-001-002.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-04-14-001-003.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-04-14-001-004.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-04-14-001-005.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-04-14-001-006.png)
![](/images/facebook-posts/facebook-posts-attachment-2025-04-14-001-007.png)
