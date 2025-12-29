---
date: 2025-06-13
datetime: 2025-06-13T22:04:55+08:00
timestamp_utc: 1749823495
title: "延續昨天的 PO 文 ( AI Native Git ), 我少提了一段, 就是原文提到的 模擬操"
---

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

---
prompt saved
tests linked
code generated and validated
---

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

上面反推的這些技術，其實離現在沒有那麼遠啊，這些機制目前的系統也不是做不到, 頂多部分動作人工處理而已。不知道有沒有人已經是這樣調整你的工作流程了? 歡迎留言討論 :D

![](/images/facebook-posts/facebook-posts-attachment-2025-06-13-001-001.png)
