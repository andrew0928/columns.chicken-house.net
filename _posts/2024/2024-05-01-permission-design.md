---
layout: post
title: "架構面試題 #6: 權限管理機制的設計"
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

"權限管理" 的設計，算是經典問題了吧，這次架構面試題，就來聊聊這個主題。

只要你做過管理後台，就一定會碰到這議題: 隨著登入帳號的不同，要能開關對應的功能；而這些開關，通常都是在建立帳號時要按照某些 "規則" 來管理。如果沒有規則，要把所有可能的組合展開，那可不得了，除了你要管理的組合多到管理不來之外，你還很容易碰到權限衝突的狀況 (例如 CRUD，沒有 R 的權限卻有 U 的權限這種很瞎的授權組合)。

於是，業界就發展出了一系列通用的授權管理原則，最常見的就是 RBAC (Role Based Access Control, 角色為基礎的權限控制)，另外其他還有 PBAC (P: Policy)、ABAC (A: Attribute) 等等，我就一起用同樣的模型來說明吧。實際情況下，你不大需要從頭開始設計自己的安全機制，大部分個平台的 IAM，或是 SSO 的體系都自帶對應的功能了，不過即使沒這個需要，我仍然高度建議各位 (尤其是資深人員) 花點時間練過這題目，這不但能讓你更清楚這些機制的運作邏輯，更重要的是你也才清楚如何正確的 "規劃" 你的管理方式。

<!--more-->

## 基礎知識






權限管理，這個領域的 know-how 其實還真不少。我等等會把關鍵字先列一列。不過，我寫這篇的目的，不是要你學會這麼多技術名詞... (你不可能全部都精通的)。你該會的，是了解這些做法背後的精神，如果你能發揮抽象化思考的能力，把共通的部分淬鍊出來，同時還能找到理想的 "發展路徑"，那你就成功了。因為你開始有能力看到全貌，知道怎麼逐步發展，可以一路順利地走向最終的規模，而且過程中都沒有浪費 (走冤枉路)，這才是資深人員腦袋裡的經驗的最大價值。

好，我開始列關鍵字了，如果你有耐心把這篇看完，我期待你應該能理解這些關鍵字背後的關聯...

1. 管理方式: RBAC, ABAC, PBAC, ACL, SCOPE...
1. .NET / C#: IIdentity, IPrincipal, ClaimPrincipal
1. 角色, 群組, 選單, 功能, API
1. 合約授權, 功能開關, 功能授權
1. Session Tracking
1. Audit

我曾經想過，為何這類題目的討論度不高? 這些權限管理的設計方式，理論上在這產業應該很普遍很容易碰到才對，但是能找到有參考價值的說明少之又少 (所以我才會試著自己摸索看看)。我的觀察，我發現:

1. 擅長軟體開發或是設計的人，大都走向 application development。往商業領域發展其實更容易展現出成果，這類吃力不討好的題目，通常都被擺在第二或第三順位；或是做一做堪用就行。
1. 擅長做大規模的權限管理，有其他相關系統使用經驗的人，大都是 SRE，IT，MIS 等屬性的人。這類人都很熟悉這些機制的使用方式，但是他們的任務大都不是大型應用系統商業邏輯的開發角色...。

於是，這兩種屬性的經歷沒辦法湊在一起 (對使用的 domain 掌握不夠到位，對開發與抽象化的能力也不夠的話)，自然就不會產出我一直在尋找的內容了。其實除了 software develop, IT management 兩種角色之外，我覺得還有第三種的人也是，就是熟 operation system，熟 protocol design，或是熟 hardware / firmware design 的角色也是。還記得上一篇談 TCP 怎麼重新排列封包的案例嗎? 或是我更多過去寫的文章 (例如 pipeline, 或是 rate limit, QoS 等等) 這些想法，都是取材自 CPU，Networking，Firewall 等等硬體跟網路的設計。

也因為這樣，我才體會到我能把這些 know how 結合再一起，才能用高度整合的角度來解決這些題目。


## 權限管理的基本模型

{你被允許能做什麼} CheckPermission({你是誰}, {你的意圖範圍})


## 你需要的 interface

### 1. 基礎授權查詢:

bool CanExecuteAction(int clientId, int userId, int actionId);

缺點: 呼叫太頻繁，可能的 input / output 組合過多，高頻次呼叫的優化空間很有限
(10000 users, 5000 actions, 10000 clients, 3 possibility) => total 10000 x 5000 x 10000 x 3 = 1.5T 種可能的組合

### 2. 介面最佳化

將運算分散，盡可能地把組合從乘法變成加法，降級至合理的範圍，就容易靠計算與 Cache 加速

permission_sets CheckModulePermission(session_context, module_context);

session_context: 包含當前登入的使用者所有相關資訊。通常這些資訊在登入期間不會改變，適合用 JWT 來處理，每個 session 只需一份 (cache key 可用 session id)

module_context: 將相關的功能聚合成一個模組，同一個模組內的多個功能 (actions) 可能在同時間會被密集檢查 (ex: 同一段 code，或是 user 在操作該功能的那 5 min 時間內)。一次性的查詢直接傳回整組可能使用到的權限判定結果

(10000 users x 10000 clients, 5000 actions = 50 modules x 100 commands, 3 possibility) => 10000 x 10000 x 50, cache body: 100 x 3


### 3. 資料結構最佳化

如果你的邏輯更明確的定義 (例如 RBAC)，則可以進一步簡化。例如 session 直接先解析當前登入人員的一些授權資訊，例如群組或是角色等等

permission_sets CheckModulePermission((clientId, roleId[], groupId[]), module_context);


(10000 users -> 20roles, 20groups, ...)
=> 10000x20x20 x 50, cache body: 100 x 3



## 你需要的權限定義資料結構

### 1. 授權表

### 2. 用群組簡化管理

### 3. 從設計著手, 角色, ACL

### 4. Policy 簡化管理複雜度

### 5. 合約授權方案

## 資料層級的權限管理

### 1. Data Attribute

### 2. 從 Database Query 層級就支援權限過濾