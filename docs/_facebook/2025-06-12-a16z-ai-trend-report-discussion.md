---
date: 2025-06-12
datetime: 2025-06-12T21:37:32+08:00
timestamp_utc: 1749735452
title: "前幾天 (這年代，差幾天應該就算舊聞了吧) 各大神都在轉貼這篇知名創投的 A16Z 的 AI 趨勢報"
---

前幾天 (這年代，差幾天應該就算舊聞了吧) 各大神都在轉貼這篇知名創投的 A16Z 的 AI 趨勢報告 (連結我放第一則留言):

"Emerging Developer Patterns for the AI Era, Yoko Li"

當下我也看了，越看越符合我對未來的想像。文中列了九項趨勢, 想說就深入一點探討，一次來聊一題好了，逐項分幾篇 PO 文來分享我的看法跟觀察。

先來第一項: AI native Git

原文的大意是: Git 是精確追蹤 source code 異動的管理工具 (要能細緻到追出誰在哪一天，哪一行 code 加了一個分號讓編譯失敗這類蠢事 XD), 這種細緻度, 在 AI coding 的比例越來越大的情況下不再這麼重要了，因為 code 不再完全是 "人" 手工寫出來的。

我認同這觀點，不過說法不大一樣。前面談 AI 時代軟體工程 (例如: SOLID 原則) 是否還重要的 PO 文我也聊過，AI coding 能力越強，人的心力就會越會往需求端移動。屆時，AI 產生 code 的來源大部分是 document ( 跟當下 developer 下的 prompt )，這時比起 "source" code, 現在的 code 更像是由 document “build” (其實是 vibe coding) 出來的結果 (“artifacts”).

因此, 對比一下:

過去: source (code) 要進版控, (code) build 的結果 (binary, executable, container image) 要進 AM (artifact management).

現在: source (requirement, 通常是 document + prompt) 要進版控, vibe coding + build 的結果 ( code / executable / container image ) 要進 AM ( 可能是同一個 or 另一個部署用的 git repo, 以及真正儲存 binary 的 AM )

就 CI/CD 的觀點來看，其實流程是一樣的，只是通通都往 "左移” 了一階, 未來的 source code, 意義上更像是產出物，而不是手寫的原始碼了。

我都特別寫 “source” code 或是講 “原始” 碼，因為我認為文字上的意義，是強調 “source” 才對，那是人類意圖真正變成對機器有意義的第一個產出。關鍵是 source, 不是 code. AI 的進步，同樣意義的 source 逐漸變成 document, 原本代表 source 的 code 現在變成 AI 的產出物了, 自然會有這樣的平移。

所以，意義上真正需要被版控的，其實是 source 而不是 code. 現在的 Git 是為了 code 的版控而設計的系統，如果未來的 source 從 code 變成 document, 版控會有甚麼改變? 版控的目的，是讓你能夠追蹤 source 因為甚麼原因，做了甚麼改變，讓你能事後還原整個變化的過程跟意圖，也能讓你從實際運作中的系統 ( 通常是來自 AM 部署出去的系統) 往回追蹤這份運行中的 artifacts 是來自哪一版的 source..

所以，未來需要追蹤的，是需求文件及 prompt 的變化。這邊的 prompt 包含產生 code 用的 prompt ( vibe coding )，應該也包含實際在線上運作的 AI APP 內含的 prompt .. 這有點難區分，就像之前在 GenAI 年會講到的，用 AI 開發 AI 產品，兩邊用到的 prompt 其實都需要被管理。

所以，真正管理需求變更的 "Repo" 可能是以需求 (document) 跟意圖 (prompt) 為主的系統, Repo 的 Diff 操作，可能不再只是告訴你那些檔案有異動，而是類似 RAG 那樣，先找出 string 實際上的 Diff，再透過 LLM 彙整，告訴你兩個版本的 "意義" 上有哪些不同, 例如多的兩條需求，刪減三個需求等等… 現在有些 IDE 能自動產生 git comment message, 大概就像那樣的味道吧。

不過，即使如此，我覺得到時管理 code 的版控還是有存在必要，因為你還是需要 code review 等等任務，只不過在意義上更像是生產線後段的東西了，這些過程其實更像 build / pipeline 的過程，而不是在 "開發"。因此 code 我認為它更接近 Artifacts (”產出" 物) 這樣的存在, 而不是 Source Code (”原始" 碼)

AI Native Git, 大概就是這個意思吧。針對這項我花了點篇幅來聊聊，後面幾項我也會逐一深入探討。有興趣的歡迎追蹤我的粉專 :D

![](/images/facebook-posts/facebook-posts-attachment-2025-06-12-001-001.png)
