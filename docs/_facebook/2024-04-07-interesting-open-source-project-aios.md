---
date: 2024-04-07
datetime: 2024-04-07T00:11:23+08:00
timestamp_utc: 1712419883
title: "看到有人分享這個 open source project, 覺得有點意思.. 所以我也來分享了 :D"
---

看到有人分享這個 open source project, 覺得有點意思.. 所以我也來分享了 :D

今年一月，我寫了篇文章 ("開發人員該如何看待 AI 帶來的改變")，也自己試做了個 "安德魯小舖" 助理店長 GPTs，體驗 AI 如何透過對話來決定該怎麼呼叫線上購物系統的 API 完成購物。

文章裡面提到 LLM 持續發展下去，開始會有能力成為應用程式的核心控制邏輯了。過去從 UI 到 controller 到 API / DB，都是開發者控制的，而這 "controller" 的角色，LLM 開始會佔有一席之地..

我也預測，LLM 開始會從雲端落到本地，而統合這些 LLM 必要資源的角色，也會從 framework ( 我文章提到的 Semantic Kernel / Lang Chain )，逐步轉往 OS 來提供。

沒想到才隔兩個月，就已經看到類似的專案出現了，在  GitHub 看到這個 "AIOS" 專案的野心，就是成為我上述講的 AI 違和新的作業系統.. 不過，我看了一下，這專案離真正的 "OS" 還很遠，基本上他只算是個開發 AI Agent 共用的 runtime 而已。不過，比起 SK 讓你開發 "一個" APPs, 這專案已經讓你可以建立 "多個" agent 的底層共用服務了。

README 有張架構圖，仔細看了看，其實跟我三個月前寫那篇文章的想法很一致啊，對我來說，代表我的想法也在世界的趨勢上，以我這後來才加入的門外漢，方向沒走偏對我才是最重要的。

我就把這張架構圖貼出來了，有興趣的朋友可以花點時間看一看。相關連結我一起附上:

AIOS:
https://github.com/agiresearch/AIOS

文章連結:
https://columns.chicken-house.net/2024/01/15/archview-llm/

安德魯小舖 GPTs:
https://chat.openai.com/g/g-Bp79bdOOJ-an-de-lu-xiao-pu-v5-0-0

![](/images/facebook-posts/facebook-posts-attachment-2024-04-07-001-001.png)
