---
date: 2025-05-21
datetime: 2025-05-21T22:34:13+08:00
timestamp_utc: 1747838053
title: "今天來貼一則關於 MCP 的冷知識..  (真的很冷)"
---

今天來貼一則關於 MCP 的冷知識..  (真的很冷)

有人留意到 MCP 官方提供的幾個 MCP Server 之一: filesystem, 有各種 file / directory 的操作, 但是唯獨沒有 copy 嗎?

上個禮拜, 某場合 Sam Altman 提到, 年輕人用 AI 的方式是把 ChatGPT 當作作業系統來用, 說實在話我也常常這樣用 XDD, 其中一個案例就是我貼的這張圖...

前陣子我都在研究 api test 的那個 site project, 其中一個過程, 我想把我建立的測試案例換個目錄結構... 原本的結構是一個目錄一個資料夾, 然後裡面固定擺一個名為 testcase.md 的檔案。後來我想簡化，改成在同一個資料夾內，一個測試案例一個檔案，檔名用固定編號當作開頭，後段我想依據測試案例內容來命名..

假如沒有命名這件事，我就寫個 shell script 來處理了，不過我只做一次，而且有命名這件麻煩事 (對我來說要處理自然語言都是麻煩事)，我就搬出 Claude Desktop + File System MCP 出來..., 用這段 prompt 讓他幫我搬...

某種程度上，AI 替代了檔案總管，幫我完成了這件事。不過我留意到 AI 的處理過程不大對勁啊... 每個檔案都讀取就算了 (因為要讀檔案內容來決定命名)，為什麼寫入也要 LLM 讀進去後在一個一個字吐出來再寫入檔案啊? (如果我是用 APIKEY，檔案多大就吃掉兩倍 token 啊啊啊啊) 這需求不是直接 copy 就好了嗎?

於是，翻了一下 File System 定義的 tools 清單 (如圖)，還真的沒有 copy 這個 tool.. 連 move 都有了, 沒有提供 copy 還真的怪怪的, 真的要省的話也是省 move 啊, 至少 copy + delete 可以涵蓋 move 的需求, 但是反過來卻做不到..

問了 Claude, 回答的支支吾吾的, 我就改問 ChatGPT 了。我得到了個冠冕堂皇的答案，但是我覺得只是在硬湊回答給我而已... 我截錄一段 ChatGPT (o3) 給我的回應:

----

在專案 issue 與社群討論中（例如 Reddit 貼文 “file server … which doesn't have file copying capabilities for whatever reason”）也有人提出同樣疑問。官方並未給出正式聲明，但從提交紀錄與討論可以推測：

1. 安全／隱私:
copy_file 讓 LLM 能一次性把大型或敏感檔案複製到新位置，意外洩露或放大破壞範圍的風險較高。

2. Token 效率
read_file → write_file 至少受模型上下文長度限制（幾 MB 就會失敗），而真正的 copy_file 沒此限制，容易讓 LLM 在無監督下翻倍儲存空間。

3. 跨平台行為差異
Node 核心 API 直到 v16 才有穩定的 fs.cp；在較舊環境要自行遞迴複製並處理權限／符號連結，實作量不小。

4. 設計哲學
官方 server 強調「LLM 做內容級操作，結構性批次動作留給外部腳本」，因此先把 rename (move_file) 當 MVP，複製功能交由使用者自行擴充。

----

其實解決方法很簡單, 我就沒有繼續追究下去了, 你會 node.js 的話, 自己補上去就好了 ( file copy 不會太難寫吧 ).. 或是換一套支援 copy 的 file-system mcp server 就好了

只是，我壓根沒想到，這麼基礎的功能，全世界那麼多人關注的 MCP 相關專案，我竟然會踩到這麼入門的洞... 啊是沒人在用這個 MCP server 嗎? XDD

以上就是今天的冷知識一枚... 如果你跟我一樣常常把 AI 當作作業系統使用的話 ( Sam Altman 認證年輕人 )，下次用的時候留意一下 XDD

--
留言 #1, Sam Altman 接受專訪的影片 (中文字幕)
留言 #2, 我詢問 ChatGPT 的對談紀錄

![](/images/facebook-posts/facebook-posts-attachment-2025-05-21-001-001.png)
