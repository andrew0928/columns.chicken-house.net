---
layout: post
title: "微服務架構 - API 的安全管控模型"
categories:
- "系列文章: 微服務架構"
tags: ["系列文章", "架構師的修練", "microservices"]
published: false
comments_disqus: false
comments_facebook: false
comments_gitalk: false
redirect_from:
logo: /images/2022-07-15-microservices17-api-security-model/2022-07-31-19-27-53.png
---

![](/images/2022-07-15-microservices17-api-security-model/2022-07-31-19-27-53.png)
> 照片出處: https://blog.techbridge.cc/2016/11/05/web-security-tutorial-introduction/


前面寫了兩篇 API 設計的文章，有帶到一點點授權的管控方法的設計，這篇就好好的來聊一聊微服務架構下，大量地使用 API 時，你到底該怎麼 "設計" API 的安全機制吧。一般而言 API 都是靠 KEY 或是 TOKEN 這種方式來管控的，一組 API，給一個服務呼叫，就核發一把 KEY 搭配對應的授權與限制就搞定。這方法對外開放 API 很合適，而且各大雲服務也都有對應的 PaaS 可以選用 (例如 Azure 的 API management)。不過既然要聊微服務架構，那你有想過對內的管控該怎麼做嗎?

API 的管理, 其實沒那麼容易。越封閉的系統安全問題越容易把關，以往我那個年代的系統 ( client server )，大概系統 console 的登入，還有 file system 管好就差不多了，現在系統儲存的資料越來越多，系統間開放的 API 越來越多，既要開放互通有彈性，又要同時兼顧安全越來越困難了。這也帶出一個問題，安全問題越來越不能單純交給 "管理" 端來做就好，需要系統開發的設計階段，就跟需求規格一樣列在第一線考量才行。

需求功能都會做各種分析，安全機制也是。我寫了一系列的微服務架構的文章，試想看看這個問題你是不是都回答的出來? 你的服務開放的 API，有哪些功能? 你要管控的是 "功能"? 還是 "資料"? 還是 "指令"? 你要管控的對象是內部的服務 (或是團隊)? 還是外部的合作廠商 (3rd party)? 還是直接訂購你服務的客戶? 或是更複雜一點，是你的客戶的 IT 團隊 / 客戶的合作廠商? 最後我再追加一個維度，管理這些授權的 "人" 是誰? 是每個服務自己管理? 還是公司一起管理? 是開發團隊 (Developer) 管理，還是 Product Manager (或是 PO, Product Owner) 管理? 或是客戶服務人員 ( Service Team ) 來管理? 抑或是全部自助，讓客戶自己管理就好?

這一連串問題問下來，你開始體會我講的安全機制為何是 "設計" 題了嗎? 如果你抱持的 code 寫好，安全問題交給 infrastructure 的人來負責的心態的話，那你的安全機制是沒辦法跟上這個年代的需求的 (光是上述的維度，基本上都不是 infrastructure 的角度能掌握的)。你非得在系統設計階段就納入考量不可。安全機制的模型 & 設計定義好之後，接下來才是尋找適合的工具或是服務來實做，這時才有你需要那些基礎建設來支撐 (例如你要用 Oauth2 來實做, 或是自己用 JWT 來設計? 或是你要整合 AzureAD 等等這類 PaaS 的認證管理機制)，或是要用那些框架來開發的技術棧的選擇。這篇我就想來聊聊這個主題，各位可以回頭審視看看自己的系統，漏了那些環節。


<!--more-->

{% include series-2016-microservice.md %}



# 前言: API 的安全性要管理什麼?

現在的服務越來越講究整合，同系統的不同功能講求整合 (讓使用者在同個介面上專注他要解決的問題，不是讓他自己去操作散落在四處的功能)，不同的服務也講求整合 (最典型的就 Google 提供的眾多服務了，帳號登入，文件編輯，資料儲存 分別散落在 Google Account, Google Docs, Google Drive.. 甚至文件編輯還有外部的服務, 例如 Draw.io)。因為整合程度越來越高，所以 API 的重要性也越來越大。真正能被整合的，其實是 API，而不是你在 API 上面實做出來的功能。

也因此，過去安全管控問題，過去往往都從頁面的角度做好管控即可，隨著 API 越來越重要，API 的管控也越來越不能忽視。一不小心，別人透過你的 API 把資料都拿走了的話，那個嚴重程度是遠遠超過網站功能的漏洞的。我直接拿前面兩篇 API 的設計文章用的案例: 會員服務 當作示範，來說明一下安全管理的問題。

複習一下，直接面對會員服務的 domain, 最貼近的就是 Core Service 了。直接用上一篇的範例程式碼來代表:

> MemberService.cs

```csharp

public class MemberService
{
    public event EventHandler<MemberServiceEventArgs> OnStateChanged;
    public MemberService(MemberServiceToken token, MemberStateMachine fsm, MemberRepo repo) { ... }

    // major API(s), 執行後狀態會因而改變
    public bool Activate(int id, string validateNumber) { ... }
    public bool Lock(int id, string reason) { ... }
    public bool UnLock(int id, string reason) { ... }
    public bool SoftDelete(int id, string reason) { ... }
    public bool Delete(int id, string reason) { ... }


    // domain / aggraton API(s), 會因為狀態決定能否執行，不會直接改變狀態 (除非內部呼叫了 major APIs)
    public string GenerateValidateNumber(int id) { ... }
    public bool CheckPassword(int id, string password) { ... }
    public bool ResetPasswordWithCheckOldPassword(int id, string newPassword, string oldPassword) { ... }
    public bool ResetPasswordWithValidateNumber(int id, string newPassword, string validateNumber) { ... }
    public bool ForceResetPassword(int id, string newPassword) { ... }

    public MemberModel Register(string name, string password, string email) { ... }
    public MemberModel Import(MemberModel member) { ... }
    public MemberModel GetMember(int id) { ... }
    public MemberModel GetMemberByName(string name) { ... }
    public MemberModel GetMemberByEmail(string email) { ... }

    public IQueryable<MemberModel> GetMembers() { ... }
}

```

這是直接拿前面的案例，MemberService 這類別的公開簽章，其實就可以代表他對外的 API 了。把前面的問題一個一個套進來思考，看看你是否都回答得出來?


你要管控 **什麼**:

1. 這服務有 "多少" API? 我需要怎麼控管? 每個 method 都要能獨立設定是否可以呼叫嗎? 是否彼此間有相依關係需要考慮? (例如能夠呼叫 GetMembers 是否代表一定能呼叫 GetMember)


你要管控 **誰**:



你要交給 **誰** 來管控:




// API 管理，要管蛇什麼?
// 給誰呼叫? 自己人，內部團隊，合作廠商，客戶，客戶的合作廠商，終端消費者
// 給呼叫甚麼 "功能" ?
// 給使用甚麼 "資料" 或是 "行為" ?
// 有哪些額外限制? 時間? 流量? 次數? IP?

// 給誰管? RD? PO? IT? SRV? 客戶?




細節先不往下挖了，我先從這案例來說明一下到底有那些潛在的安全風險? 帶出你該如何管控授權才合理? 資安風險除了駭客入侵等等這些基礎建設層次的問題之外，更重要的是商業規則設計的漏洞啊，前者要面對的是有惡意的駭客入侵的風險，後者要面對的是連正常守規矩的 API 使用者都有可能造成的風險啊。上述的 MemberService 服務，我大致把要提供的功能分成這幾類:

1. 基本的單筆會員資料操作
1. 從無到有 (註冊、建立)，或是從有到無 (刪除) 的操作
1. 一次面對多筆的資料操作 (匯入、查詢)

試想這些不同的情境，如果你的 API 允許正規的開發人員這樣呼叫會發生什麼事:

1. 如果消費者 A 登入後，能透過公開的 API 存取消費者 B 的個人資料...
1. 如果廠商 X 的 server 拿到的權限，能夠透過 API 存取廠商 Y 的所有資料...
1. 如果廠商 X 找了外包的團隊 Z，想要委託團隊 Z 呼叫 API 來開發客製化的功能，如何避免 Z 把重要的資料通通偷走...



















前面寫了兩篇 API 設計的文章，也寫了一篇 PoC 的心得，接下來就延續 API 這個議題，來聊聊 API 的安全機制設計吧。資訊安全，通常都是要從下到上，每個環節都能顧到才算安全，只要你有一個環節沒做好，就會有人從你最弱的一環來入侵。這篇我不談基礎建設層面的資訊安全 (例如防火牆，DDoS 等等這些 infrastructure 層面的安全機制)，我想聊的是你設計 API 時如何融入你要的安全管理模型。

安全議題有很多層面。從 APIKEY 驗證，到鎖定來源 IP，到資源的授權 (可以個別控制 CRUD)，到更進階的多租戶架構下的授權與資源管理等等都是。這篇我想整理一下我過去面對過的各種情境，並且整理一下這些情境各該用哪種模型來看待他。從架構設計的角度來看，我很強調挑選正確的模型，模型對了你的解法才會貼近你的使用情境。挑對模型，再來挑選平台或工具。從 code 的角度 (套件)，或是平台的角度，應該都有不少成熟的解決方案可以選擇。

過去這些資安相關，以及 API 設計相關的主題，我也零星寫過幾篇了。我就用這篇來整理一下我曾經使用過的幾種類型給各位參考，同時也說明一下背後選擇的想法。現在這行的技術跟工具進步的太快了，你不可能摸完市面上所有的 solution, 要能跟得上潮流的進步，你得掌握原理才行。唯有理解這些架構背後的概念，你才能在不熟悉的情況下做出正確的決策。

<!--more-->

我會在最開始提到另一篇談 PoC 的文章是有原因的，這些架構或規格的設計，我自己很講求要先找對模型，用對模式來解決問題；之後才是根據你的規模跟實際使用的 tech stack 或是 hosting environment, 再來找合適的解決方案。規模小的情況下可以找找合適的 package, 直接在你的 application 使用的框架內來做好安全機制 (例如 ASP.NET Core 的 Middleware, 上一篇實做我就是用這技巧) 即可。如果你必須面對大流量，將安全機制 offloading 在進入你的服務前就解決掉，你就得找能在 API Gateway / Reverse Proxy 這層次注入你的判定邏輯的解決方案。Azure 的 API Manager + Azure Functions, 或是自己在 reverse proxy 外掛你的檢查邏輯 ( Ocelot, YARP 等等這類你能掌控 source code 的 open source project ) 來做到 offloading 都是不錯的解法。

不過，要做到這樣靈活的彈性，你必須先想清楚安全模型才行 (甚至你必須定義出 protocol)，抽象化到這個層次，你才有可能達到這樣的靈活程度。甚至是初期使用開發框架，後期改用基礎建設，而這些轉變都要能滿足同樣商業需求的安全管控機制。如果你的設計能有這樣的彈性，那恭喜你，你開始能肩負起你團隊的架構設計責任了。


# 前言

// 示範案例



# 系統規模

## 單一服務 (1)

## 微服務 (N)

## 對外公開服務 (N x M)

## 多租戶對外公開服務 ( N x M x O)



# 領域複雜度

## by (domain) method

## by (domain) scope

## by (client) environment

// IP, time, rate limit, ...

## by role



# 管理模式

## by permission ( key, token )

## by role ( client id, certification )

## by intention ( client -> 3rd party )

## 設計階段決定 vs 授權階段決定


# 大亂鬥, 挑選適合的授權管理模式



# 延伸應用: market place, automation