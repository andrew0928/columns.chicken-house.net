---
date: 2024-11-24
datetime: 2024-11-24T01:43:10+08:00
timestamp_utc: 1732383790
title: "WSL 用的兇的朋友，還有用 MacOS 的朋友應該都可以跳過這篇了, 這只是拿 WSL 當主要開發"
---

WSL 用的兇的朋友，還有用 MacOS 的朋友應該都可以跳過這篇了, 這只是拿 WSL 當主要開發環境的心得文而已..

以前我都有其他選項避開文內的問題, 直到開始弄 AI 相關, 想在本機跑 LLM 才開始認真面對...

--
果然決定丟掉 docker desktop for windows 後就一路順暢... 雖然 disk i/o 效能糟其實是 WSL2 的鍋, 不過過度依賴 docker for windows 實在太累贅又綁手綁腳, 會讓人不想直接碰 WSL2, 衍生了一堆問題..

我 還是繼續用 docker，只是改成直接進 wsl 安裝 docker, 也順便避開難搞的授權問題 (爽)。解決掉離譜的 disk i/o 問題, 解決掉 docker 內跑 CUDA 問題, 也體驗了 vscode remote develop 的威力, vscode 的 ui 留在 windows, 但是整個骨子裡都是在 linux, 完全就是理想的後端開發環境啊..

我算後知後覺，這些好東西出來了兩三年才發現，還沒用過的歡迎參考我的心得.. :D

這 PO 文我只是要秀圖, 趕流行, 讓 ChatGPT 畫出我的工作環境, 文章連結請看第一則留言..

![](/images/facebook-posts/facebook-posts-attachment-2024-11-24-001-001.png)
