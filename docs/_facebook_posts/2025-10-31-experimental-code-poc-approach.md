---
date: 2025-10-31
datetime: 2025-10-31T19:30:58+08:00
timestamp_utc: 1761910258
title: "我現在寫的 code, 都是實驗性質的居多, 最多的是各種應用的可行性驗證 (PoC)..."
---

我現在寫的 code, 都是實驗性質的居多, 最多的是各種應用的可行性驗證 (PoC)...

對應的 DB 類型選擇也是一環, 如果有 embedding 的選擇 ( in-memory, in-filesystem, in-process ) 我通常都會選這種, 因為達成驗證的目的了, 還省掉部署的麻煩... 如果有 .NET 的版本我通常都優先採用

例如:
- Relation database 我會挑 SQLite
- NoSQL 我會挑 LiteDB
- Knowledge Search 我會挑 Microsoft Kernel Memory

唯獨 Vector DB 還沒有合適的, 不過, 現在這個缺口終於補齊了。兩年前曾經發 issue 建議過的 LiteDB 加入向量檢索, 沒想到已經有好心人士做出來並且 merged / release 了 :D

九月底 released 的，現在還在 6.0 preview 階段, 有興趣的可以試試, 連結我放留言

![](/images/facebook-posts/facebook-posts-attachment-2025-10-31-001-001.png)
