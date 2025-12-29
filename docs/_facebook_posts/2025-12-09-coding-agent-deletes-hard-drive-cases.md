---
date: 2025-12-09
datetime: 2025-12-09T02:04:03+08:00
timestamp_utc: 1765217043
title: "看到兩則硬碟被 coding agent 無情刪除的慘案... 看來不是特定環境的問題, 這兩個案例"
---

看到兩則硬碟被 coding agent 無情刪除的慘案... 看來不是特定環境的問題, 這兩個案例分別是:

1. antigravity, 被 agent 刪掉了整個 d:\ ( windows )
2. claude code, 被 agent 刪掉了整個 home 目錄 ( macos )

回頭翻了我貼的舊 PO 文, 其實兩個月前才 PO 過, 執行 coding agent  最佳的環境就是 development container ..  只不過當時我舉的例子都是軟體工程上的好處 ( 環境控制, CI/CD 友善, 遠端部署等等 ), 沒有特別提到 sandbox 對自己本機的防護...

大約快兩年前, 我開始大規模的把我主要工作環境, 從 windows 轉移到 WSL2, 使用的 IDE 也開始從 Visual Studio 轉移到 VSCode, 理所當然的就用了 WSL Remote 的方式來跑我的 side project ..

這樣的好處是, 所有的開發環境, 都被控制在 WSL 的範圍內, 即使 Agent 暴走, 我損失的就是還沒 commit 的 code 而已 ( 我 WSL 主要都開發用途, 沒有擺其他有個資或是沒備份的重要資料 )

過程中因為還有些麻煩的環境要控制 ( 就是我在寫 BLOG MCP 那段時間 ), 我需要在本機跑好幾個 container 來控制 MCP 的執行環境, 包含 Kernel Memory Service, Qdrant 向量資料庫等等, 同時有筆電, 桌機, 還有遠端 Azure Container Apps 要同步, 所以我開始更近一步地把工作環境轉移到 devcontainers 上了

原本是拿 WSL ( 高度跟 windows host os 整合的 linux vm ) 當作開發工作環境, 而 devcontainers 則是讓你拿 container 當作工作環境的技術, 在 VSCode 下啟用相當方便, 只要你的 workspace 有正確設定, 每次啟動 VSCode 就會問你要不要啟動 devcontainer, 把你配置好的工作環境跑起來後, 再用 remote 的方式啟動 VSCode, 於是你的 workspace, 你的 terminal, 連同 debugger, extensions 等等通通都在你指定的 container 內執行..

也因為我做了這些動作, 兩個多月前我開始把我的主要工作環境, 從 windows 轉移到 macos 上, 開發環境的轉移意外地順利, 對我來說其實都是在 Linux 上工作, 只是這環境原本是 WSL2 提供的, 現在換成 MacOS 下的 colima 提供的, 如此而已

如果你正確的配置你的開發環境的話, 那你先天就有個安全的 sandbox 可以讓 coding agent 發揮了... 如果你的 agent 不巧也暴走了的話, 毀掉的 ~/ 只是 container 內的目錄 (通常不會有甚麼太重要的東西).. 如果你不手癢把 D:\ 也掛到 container 上的話, coding agent 暴走應該也碰不到你的 D:\

這類技術, devcontainer 算是支援度很棒的選擇了, 他是 Microsoft / GitHub 推動的規格, Microsoft 官方早就替你準備好必要的 container image / features 了, GitHub 的 CodeSpace 也直接支援, VSCode 支援度也很棒 (包含衍生的 IDE), 而幾套主流的 coding agent CLI 也都沒問題, 基本上只要你想用, 都可以放心的開下去...

雖然這是馬後炮, 不過很多事情都一樣, 你有養成好習慣把環境跟架構都控制好的時候, 你先天就會免疫很多無妄之災的... AI 的甜頭來的太快, 快到很多這些基本動作都沒做好, 就有許多人一頭熱鑽進來了... 在享用這些樂趣的時候, 別忘了也把基本動作先顧好...

即使現在 vibe coding 的門檻低到不行了, 至少入門的時候, 還是找個有經驗的 developer 帶你入門吧, 至少有經驗的人有很多這類 "慘痛"
 的教訓, 可以讓你少走很多冤枉路 :D

文內提到的兩個案例, 還有我兩個月前的 PO 文連結, 我都放在留言

![](/images/facebook-posts/facebook-posts-attachment-2025-12-09-001-001.png)
