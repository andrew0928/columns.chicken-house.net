---
layout: post
title: "(TBD) 權限管理機制的設計"
categories:
- "系列文章: 架構師的修練"
tags: ["系列文章", "架構師的修練", "架構師觀點", "刻意練習", "抽象化"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---

這次在 .NET Conf 我分享了 RAG 的主題, 主要是運用 Microsoft Kernel Memory 這套服務的經驗分享。這套服務其實就是把 RAG 常用到的 "Retrieval" 的操作，封裝成獨立服務的開源專案。

<!--more-->

我之所以會分享這題目，因為這專案的文件，提到了一件我感興趣的小事，向量資料庫通常都不提供 record-level 的授權機制 (就算是關聯式資料庫也很少這樣用...)，不過官方卻正式的教你怎麼善用 tags + filter 來做到這需求 (ie: 向量檢索時，要如何在你被授權的範圍內找到相關性高的資訊)。

其實這是我先前一直在使用的技巧，但是這主題 (授權) 太硬，過去也都沒機會談，這次就趁著我在處理大量敏感資料的相似性檢索過程，聊一下該怎麼做好這件事吧。

> When designing for security, Kernel Memory recommends using Tags, applying to each document a User ID tag that your application can filter by.  
> Vector DBs like Azure AI Search, Qdrant, Pinecone, etc. don't offer record-level permissions and search results can't vary by user. Vector storages are optimized to store large quantity of documents indexed using embedding vectors, and to quickly find similar documents. Memory records stored in Vector DBs though can be decorated with metadata, and can be filtered when searching, applying some logical filters.

https://github.com/microsoft/kernel-memory/blob/main/docs/security/security-filters.md


# 1, 需求

// 儲存上萬份文件，每份文件、每個分類、都有預設特定的部門，角色，甚至是指定使用者才能閱讀。

// 對安全的要求，除了個別文件的 READ 管控之外，也不能將文件的片段內容，顯示在搜尋的結果，摘要，清單內

其實，這是很單純的需求 (正常的 user 都會這樣要求吧)，不過，對於內容檢索，搜尋引擎的服務來說，這是很頭痛的問題。因為這些處理 "相似" 內容的各種技巧，都需要大量的事前索引，分析，統計等等計算來加速，才能讓你很快地在 100ms 內就找出相關的內容。

然而越多的預先處理，就代表檢索的結果越無法滿足 "個人化" 的要求，包含資訊安全的期待，因為預先處理的過程中，你完全猜不到當下是 "誰" 會來找資料，尤其是不同人找到的資料都必須不同的時候 (資安相關的要求，更不能有錯，你要是洩漏了敏感的個資，那可是要吃上官司的)。

因此，不懂原理的話，你很難設計出合理的 database schema 來儲存跟運用這些資訊的，Relational Database 是如此，NoSQL Database 也是如此，就算到 AI 時代進階到 Vector Database 這問題仍然存在。

所以，我這篇的目的，就是要談談這些 "授權機制" 到底背後的原理是什麼，你該如何在資料庫層級來實作它。我決定跳遠一點，最後的應用案例，我就直接拿 RAG 的檢索服務: Microsoft Kernel Memory 當作案例來示範這該怎麼設計 & 實作。






# 2, 個人授權




# 2, 最常見的授權模型: RBAC

下面我會列舉幾種常見的授權管理模式，不過我先收斂一下最終能用的資料結構。各種資料檢索的技術，通常都能對 "有限" 的標記做 "過濾"，這類動作很容易標準化，也容易做索引 (有索引就代表效率跟成本)。困難的就是如何把各種複雜的組合，降低維度，變成多組標記的組合操作。

如果你能找到正確的標記定義方式，也能在資料產生時預先貼好標記，那你就能用很低的成本，在 runtime 按照你要求過濾資料了。精準的過濾就代表你不會有機會看到你 "不該看" 的資訊，就這麼簡單。

聽起來很抽象嗎? 這段話先留著，先看完這段 RBAC，再回頭你就看得懂了。

--

我常喜歡用 "最多總可能的組合" 來代表一個問題的複雜度。權限設計就是一種例子。如果一間公司有 100 人，共有 5000 份文件，每份文件都有可能有不同的可以閱讀清單.. 假設沒有任何規則，那你就需要有 100 x 5000 = 500000 個 boolean 數值需要紀錄，才能表達所有可能...

別說儲存空間了，光是設定這些授權，就夠搞死人了。因為複雜度來自兩個維度 (人數 跟 文件數) 的組合很驚人，如果都能分類降級，那就單純得多了。

例如:
1. 人分成 5 種角色，每種角色的授權內容都一樣
1. (option) 文件分成 20 種分類，每種分類的授權都一樣

如果這兩個都做得到，你需要管理的設定組合，就能從 500000 降低成 100 種

這些資訊怎麼儲存?

我定義角色有 R1 ~ R5, 文件分類有 C01 ~ C20..

每個人的資料表，都可以多一個 Role 的欄位:


每個文件的資料表，都可以多一個 CATEGORY 的欄位:


另外多一張設定表，紀錄 (R1 ~ R5) x (C1 ~ C20) 的組合 (打 O 或 X 而已):


通常，下查詢時，你都會知道你是代表 "誰" 來查詢，所以查詢條件可以簡化成:

select docs.*
from docs
where ( 原本查詢的條件 ) AND
 docs.category in ( ... )

 而 ... 代表上面那張表格列的結果，這張表格如果小到可以放進 RAM 內，其實程式產生就好了。

 如果你是用 nosql like 的資料結構，那更容易，標準化成 "tags" 的結構就夠了:

 documents:

 {
    // ...
    tags: {
        "mytags": [ ... ],
        "catalog": [ "C01", "C05" ]
    }
 }

而 API 化的查詢，也只要簡化成:

query: ...
filters: { "catalog": [ "C05" ] }




# 3, ABAC




# 4, PBAC




# 5, 降級成 Tag 的操作

## 5-1, 在 "資料" 上面貼標

## 5-2, 在 "人" 或是 "操作" 上面貼標

## 5-3, 查詢當下要用甚麼標籤過濾?


