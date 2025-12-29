---
date: 2025-12-10
datetime: 2025-12-10T19:00:56+08:00
timestamp_utc: 1765364456
title: "前天 PO 了 devcontainer 可以當作安全的 sandbox 來跑 coding age"
---

前天 PO 了 devcontainer 可以當作安全的 sandbox 來跑 coding agent, 其實使用的門檻比你想的低很多 (很多人聽到要在 container 裡面開發, 直覺覺得很困難就縮手了), 我就示範最簡單的起手勢, 用 vscode 來跑就好..

會挑 vscode 有兩個原因, 一個是高度整合你需要的所有東西了 ( 內建 terminal, 內建 workspace file expore / editor ), 而這些東西都會統一幫你 redir 到指定的開發環境, 你不用擔心 terminal 看到的跟執行的是其他環境的, 你也不必擔心開出其他環境的 source code / document ... 只要你在 vscode 連線到 devcontainer, 所有開出來的東西都是同一個環境, 使用上完全沒有差別｡

最簡單的環境, 只要一個檔案, 放一行設定就夠了, 大力推薦所有還不熟悉 coding 的人當作入門使用. 這行會用預先建立的 container image, 替你準備一個 dotnet 10 的開發環境 (包含 .net sdk). 我只需要在工作目錄下, 建立 .devcontainer.json 這檔案, 內容如下:

```
{
  "image": "mcr.microsoft.com/devcontainers/dotnet:10.0"
}
```

然後在這目錄啟動 vscode, 他會問你要不要 "Reopen in Containers?" , 同意之後, 第一次會花點時間 pull image / create container, 然後... 然後就完成了. 你已經可以在你準備的 sandbox 內安全的跑 coding agent 了

截個圖感受一下, terminal 內可以看到 ~/ 實際上是 /home/vscode, 很明顯的不是你真正本機的 home dir ( 所以砍了也沒事 ), 右邊的 agent 我讓 AI 幫我寫了段 code 來計算圓周率, 也順利完成了, 左邊專案的目錄結構, 也清楚列出你的工作目錄了.

這背後, 其實 vscode + docker 幫你做了很多事情, vscode 用 remote 連線到 container 內, 而 container 則用你指定的 image, mount 你的工作目錄到 /workspace/demo, 其他都是 container 內的東西...

當然 devcontainer 的功能很多, 我就不多做介紹了, 網路上太多參考資訊了｡ 操作已經這麼簡單了, 應該找不到什麼理由不用他了吧, 尤其你要用的是威力強大的 agent ... 不建立一個 sandbox 放心的用他嗎? :D

![](/images/facebook-posts/facebook-posts-attachment-2025-12-10-001-001.png)
