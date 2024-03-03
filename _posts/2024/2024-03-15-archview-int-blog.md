---
layout: post
title: "替你的知識庫加上智慧! 談 RAG 的檢索與應用"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆", "AI", "Semantic Kernel"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: 
---

這篇，我想聊一聊 "資料搜尋" 在 AI 時代的做法會有那些變化。典型的應用程式，不論領域，不外乎就是 UI / Logic / Data 三個層次的設計。UI 會因為 AI 的改變，在於 LLM 透過自然語言，能更精準的猜到使用者的 "意圖"，因而會有一連串的改變；而聊到 API 呼叫，也會因為 LLM 能解讀自然語言，解析背後的意圖，精確的轉為對應的一連串 API + 參數的操作，讓代理程式的設計大為簡化，變成以 LLM  為核心的結構。而資料的處理，也有相同的結構改變。資料的查詢，會像 API 呼叫這樣，也被 AI 做根本結構性的改變嗎? 這篇我就是想聊聊這個題目，當作計畫中三篇文章的收尾。

<!--more-->

前面我都用典型的線上購物 (安德魯小舖) 當作案例來說明 UI / AP 之間的改變，而這篇既然要談 Data, 我就換個以內容為主的題目吧! 想到這裡，一個我做了多年的  side project: 我的部落格 (對，就是這裡: "安德魯的部落格" ), 自然就是最理想的選擇了。

我的部落格從開張到現在，都是我自己維護的。我沒有選擇類似 medium.com 這類外部的平台，而是選擇自主性高的自行架設方案，有很多原因。其中最主要的，就是我把自己的部落格當作我的 side project, 是個我自己嘗試各種應用的試驗場所。從 2000 開始，當時為了研究 ASP.NET 的 RBAC, 寫了第一版 Forum.NET, 在 MSSQL + IIS 的組合開始，到 Community Server，換 BlogEngine，再換 Word Press，到現在的 GitHub Pages 為止，都是同樣的過程。

目前跟 LLM 搭配最理想的資料查詢方式，就屬 RAG 了。既然要談 RAG，拿自己的部落格當案例是最適合不過的了。算算這些年來，我有公開張貼的文章已經有 328 篇了。數量上來看不算多，但是我的文章通常都很長，算上內容量來看就有一定的份量了。這些內容，往往多到連我自己，都不記得某些想法是在哪篇文章的哪一個段落? 連我自己都要靠 Google 來找我自己的文章.. 不過關鍵字的檢索，對於複雜的內容有時也不是那麼好用，這問題困擾了我很久.. 



# 1. "安德魯的部落格" GPTs - Demo

於是，在我做完 "安德魯小舖 GPTs" 之後，開始研究 RAG 之際，我就想到，如果能有個 "安德魯的部落格 GPTs" 來協助我，檢索、彙整、摘要、翻譯，甚至是基於我的文章內容來給設計建議或是回答問題等等，不是很棒嗎? 於是就有了這篇文章，也有了第三個應用示範: "[安德魯的部落格 GPTs](https://chat.openai.com/g/g-F3ckJut37-an-de-lu-de-bu-luo-ge)"。

也許不是所有的朋友都知道我換過那些部落格系統，做過哪些自訂的調整跟擴充，我就列出相關文章跟摘要.. 各位體會一下就知道我這個 "side project" 的範圍有多廣了。以下內容有興趣再點進去看就好，體會到了也可以略過繼續往下看。


1. [Blogging as code !!](/2016/09/16/blog-as-code/)  
摘要: 安德魯分享了他從2002年開始維護部落格至今的經歷，包括更換了多套部落格系統，從最早的自製asp.net 1.1 blog到WordPress等。最後決定採用最簡單的靜態檔案，並使用GitHub Pages作為Hosting方式。文章中還討論了靜態檔案帶來的好處以及使用markdown的方便性。
標籤: Jekyll, Liquid, Wordpress, Blogging, GitHub, VSCode
發布時間: 2016-09-16

2. [[BlogEngine.NET] 改造工程 - CS2007 資料匯入](/2008/06/21/blogengine-net-改造工程-cs2007-資料匯入/)  
摘要: 安德魯描述了他如何將舊有的CS2007資料成功匯入到BlogEngine.NET的過程，包括處理資料庫和檔案的轉移、解決中文網址問題和分類標籤的對應等技術挑戰。
標籤: .NET, ASP.NET, BlogEngine.NET, Community Server, 技術隨筆, 有的沒的
發布時間: 2008-06-21

3. [[架構師的修練] #1, 刻意練習 - 打好基礎](/2021/03/01/practice-01/)  
摘要: 安德魯談到了自己在維護部落格過程中，透過學習新技術並將其應用到部落格的每一次改版中，從中獲得刻意練習的機會。文章回顧了他從2002年使用自製的blog系統開始，到後來使用GitHub Pages的歷程。
標籤: 系列文章, 架構師的修練, 刻意練習
發布時間: 2021-03-01

4. [Case Study: BlogEngine -> WordPress 大量(舊)網址轉址問題處理](/2015/11/06/apache-rewritemap-urlmapping-case-study/)  
摘要: 文章中安德魯分享了從BlogEngine遷移到WordPress過程中遇到的大量舊網址轉址問題，以及如何使用Apache的RewriteMap來解決這一問題的經驗。
標籤: 技術隨筆, 有的沒的
發布時間: 2015-11-06

5. [水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路](/2022/06/10/home-networking/)  
摘要: 安德魯在這篇文章中分享了他如何整合家用網路設備，包括使用UniFi產品和NAS進行升級的經驗。他講述了在這過程中學到的技術知識以及實際操作的心得。
標籤: 水電工, 有的沒有的, 敗家, UniFi
發布時間: 2022-06-10

6. [換到 BlogEngine.Net 了!](/2008/06/17/換到-blogengine-net-了/)  
摘要: 安德魯分享了他從Community Server轉移到BlogEngine.NET的過程，包括轉移的動機和轉換過程中遇到的挑戰。
標籤: .NET, BlogEngine.NET, Community Server, 技術隨筆
發布時間: 2008-06-17

7. [BlogEngine Extension: Secure Post v1.0](/2008/09/06/blogengine-extension-secure-post-v1-0/)  
摘要: 安德魯開發了一個BlogEngine的擴展，使得特定文章可以設置密碼保護，並分享了開發過程和思路。
標籤: .NET, ASP.NET, BlogEngine Extension, BlogEngine.NET, 作品集, 技術隨筆
發布時間: 2008-09-06

8. [[BlogEngine.NET] 改造工程 - 整合 FunP 推推王](/2008/06/29/blogengine-net-改造工程-整合-funp-推推王/)  
摘要: 安德魯描述了如何將BlogEngine.NET和FunP推推王進行整合，以增強社交分享功能的過程。
標籤: .NET, ASP.NET, BlogEngine.NET, 有的沒的
發布時間: 2008-06-30

9. [CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)](/2015/12/03/casestudy-nginx-as-reverseproxy/)  
摘要: 這篇文章中，安德魯分享了他如何使用NGINX作為反向代理來重構他的網站架構，並處理大量文章連結的轉址問題。
標籤: BlogEngine.NET, Docker, Tips
發布時間: 2015-12-04

10. [FlickrProxy #1 - Overview](/2008/05/16/flickrproxy-1-overview/)  
摘要: 安德魯介紹了他開發的FlickrProxy項目，該項目旨在解決部落格上圖片存儲和頻寬問題，通過將圖片自動上傳至Flickr並在部落格中使用。
標籤: .NET, ASP.NET, 作品集
發布時間: 2008-05-16

11. [換新系統了!! CS 2.0 Beta 3](/2006/02/03/換新系統了-cs-2-0-beta-3/)  
摘要: 安德魯分享了他將部落格系统从Community Server 1.0升级到CS 2.0 Beta 3的经验，包括遇到的问题和如何解决它们。
标签: 有的沒的
发布时间: 2006-02-03

12. [網站升級: CommunityServer 2007.1](/2007/11/12/網站升級-communityserver-2007-1/)  
摘要: 文章中，安德魯讨论了将他的网站从CommunityServer 2007升级到2007.1版本的过程，包括他采取的步骤和遇到的挑战。
标签: Community Server, 技術隨筆, 有的沒的, 水電工
发布时间: 2007-11-12

13. [升級到 BlogEngine.NET 1.4.5.0 了](/2008/08/29/升級到-blogengine-net-1-4-5-0-了/)  
摘要: 安德魯描述了他将部落格系统从旧版本升级到BlogEngine.NET 1.4.5.0的简便过程。
标签: BlogEngine.NET, 有的沒的
发布时间: 2008-08-29

14. [終於升級上來了...](/2006/12/10/終於升級上來了/)  
摘要: 安德魯分享了他升级部落格系统到最新版本的经验，以及他自定义功能的重新实施。
标签: 有的沒的
发布时间: 2006-12-10

15. [搭配 CodeFormatter，網站須要配合的設定](/2008/04/04/搭配-codeformatter，網站須要配合的設定/)  
摘要: 文章中，安德魯讨论了他如何为他的部落格集成CodeFormatter插件，并详细描述了需要进行的网站配置。
标签: .NET, 作品集, 技術隨筆
发布时间: 2008-04-04


當你已經寫了 327 篇文章，總共文字內容 ( markdown, html ) 有 4,201,364 bytes 時... (一個字一個字敲，要敲到 4mb 而且還是精修過校正過有意義的內容) 也是很龐大的資料量的... 當你隔了 20 年 (我部落格第一篇文章是 2004 年寫的) 還要整理出上面的清單，而且關鍵字還不同，分類跟標籤也沒有對齊的時候，我每次做這件事時我都在想..

"如果有 AI 幫我處理這些事就好了..."

"如果我的部落格聰明一點，可以直接跟他說我的目的，就幫我整理好內容就好了..."

"如果能替我的部落格加一點智慧..."

對，可以回收標題了 (很硬要)，所以我寫這個 Demo 的用意就是如此。而破梗一下，上面的內容就是 "安德魯部落格 GPTs" 整理出來的 (我才不要自打嘴巴，明明寫 RAG 的介紹，結果還自己土炮整理內容)。附上原始的 chat gpt [對話紀錄](https://chat.openai.com/share/27c8b5f2-69a7-45c7-b0a9-cac88d727964)，證明這不是我瞎掰的...


破題用的 demo 就點到為止就好了。現在已經是 2024 年，Chat GPT 的威力我已經不需要多做說明，demo 到這邊大家應該已經能想像一個熟悉我 327 篇文章內容的 Chat GPT 能做多少事了。檢索、摘要彙整、問答、翻譯等應該都不是問題了。接著就直接進入主題: RAG, 以及我是怎麼實做過程。



# 2, RAG 的原理與操作流程


RAG (Retrieval-Augmented Generation, 檢索增強生成) 的概念很簡單，我用上一篇的這張圖來說明:



LLM 基本上沒有 "記憶" 能力，只會對一段文字輸入做出反應，產生一段文字回應。要讓 LLM 看起來有 "記憶"，最直接的做法就是每次都把之前聊過的內容再餵給他一次，他就會 "好像" 記得過去的內容，而給你最精準的回答了。

不過這樣有很大的限制啊，你聊得越久，過去的紀錄就越長。你終究不可能無限制的帶上所有的紀錄 (短期記憶是有限制的)。LLM 吃的是 token, 無限制的帶上過去所有聊天紀錄，只會讓 input token 爆表而已 (費用參考: 2024/03 的 Open AI 報價, GPT4 turbo 的費用是每 1000 個 input token 收費 $0.01 USD, 相當於台幣 0.3 元  )

而 RAG, 則是用了其他檢索的技術 (  embedding, 後面說明 )，先用有效率的方式檢索出相近的文字片段，再把這些已經有相關的內容餵給 LLM 加工 (修飾、彙整、解讀上下文) 再產生答案。這過程可以大幅降低 LLM 檢索內容需要的 token 數量，搭配得當的話，你檢索的範圍，可以從上下文的限制 ( 8000 token 以內 ) 一下擴大到整個資料庫，不論效率、費用都有大幅改善。

因此，RAG 有幾個關鍵 (我從結果的順序往回推):

1. LLM 從對談過程中抽出 "問題"，以這 "問題" 來檢索相關資料
1. 用 embedded model 將問題轉換為 vector (向量)
1. 到資料庫內，找出跟問題向量相近的其他文字片段向量 ( cosine 相似度 )
1. 將相關的文字片段，交給 LLM 彙整成回答

然而，這些資料庫的內容該怎麼來?

1. 將各種格式的內容轉成文字
1. 將文字做有意義的分段, 每個段落都丟給 embedded model 轉成對應的向量
1. 將這些向量存進資料庫, 資料庫必須有能力做相似度的檢索 ( cosine simility )

至於什麼是 embedded model? 什麼是 vector? 這邊說明一下:







這整段流程串起來，就完成了整個 RAG 的流程了。


# 3. 技術選擇
不過，實做上好多元件跟技術需要解決啊，要站在巨人的肩膀上，其實有很多方便的選擇:

1. PaaS 的選擇
Azure Search
Open AI

1. SDK 
SK
Lang Chain

不過一個太貴，會被綁定，自己刻又太麻煩，對於不熟 AI 的門外漢來說 (就是我)，每個步驟的技術門檻都很高。本來我打算自己用 SK + MSSQL 做完這整個案例再來寫文章的，後來放棄...，因為，我找到了一個好東西: Kernel Memory.


先說明一下，SK 的框架下，怎麼處理這種 "長期記憶" 問題，就是 Memory (或是 Semantic Memory)






然而，我開始在想，Memory 背後那一連串處理，其實大家都差不多，LLM App 跟 Vector DB 之間的空白，應該大家需要的都差不多，應該有現成 open source project / service 存在的空間吧? Microsoft 果然沒讓人失望，我找到了這個 project: Kernel Memory



API: KernelMemory (service), open api spec ( docker / service + pipeline / serverless )
Query: SimpleVectorDB (database), IMemoryDatabase ( loop / ... )
Storage: SimpleFileStorage (storage), IMemoryStorage ( disk / memory )




# 4. 打造部落格檢索服務

## 4-1, 建立資料庫


## 4-2, 建立查詢服務


## 4-3, 建立 GPTs



# 5. 總結



