---
date: 2025-12-04
datetime: 2025-12-04T11:06:39+08:00
timestamp_utc: 1764817599
title: "先推一下, Google Gemini API 也有 .NET SDK 了 🎉🎉🎉"
---

先推一下, Google Gemini API 也有 .NET SDK 了 🎉🎉🎉

這幾天踩了一個地雷, 記錄一下:

剛好有需求，要用 Google Gemini API - .NET SDK, 其中有一段範例, 用 gemini 做 text embedding:

```
using Google.GenAI;
using Google.GenAI.Types;

public class EmbedContentExample {
  public static async Task main() {
    // assuming credentials are set up in environment variables as instructed above.
    var client = new Client();

    var response = await client.Models.EmbedContentAsync(
      model: "text-embedding-004",
      contents: "What is the capital of France?"
    );

    Console.WriteLine(response.Embeddings[0].Values);
  }
}
```

這段我到 NuGet 抓 0.6.0 最新版, 怎麼 build 就是不會過, 說沒有 EmbedContentAsync( ) 這 method, 但是所有文件都有啊 XDD

最後才發現, 這是 0.7.0 新增的功能, 而這 PR 12/02 發出來還沒通過 review .. ( 我說那文件怎麼先跑出來了, 還沒標示哪個版本才開始支援 .. )

最後我發了 bug report, 很快就得到回應了, 這是即將發布的功能, 敬請期待 😂

所以, 在此時此刻, 不急的就等新版 （應該是 0.7.0）吧, 或是可以自己抓 source code 回來 build 撐一下...

--
2025/12/05 12:00 更新: 0.7.0 已經 released 了, 測試過後確認狀況解除 😍

![](/images/facebook-posts/facebook-posts-attachment-2025-12-04-001-001.png)
