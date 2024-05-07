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

只要你做過管理後台，就一定會碰到這議題: 隨著登入帳號的不同，要能開關對應的功能；而這些開關，通常都是在建立帳號時要按照某些 "規則" 來管理。於是，業界就發展出了一系列通用的授權管理原則，最常見的就是 RBAC (Role Based Access Control, 角色為基礎的權限控制)，另外其他還有 PBAC (P: Policy)、ABAC (A: Attribute) 等等，我就一起用同樣的模型 + 簡單的 PoC 實做範例來說明吧。

大部分情況下，你不大需要從頭開始設計自己的安全機制，現成的就很好用了。不過我看過太多不清楚原理，結果就亂用一通的反例。安全問題最介意的就是: 你沒掌握核心機制，又自己土炮，沒有系統的加上一大堆需求，而沒有理論基礎你也無法判定需求是否合理，結果最不安全的就是安全機制本身 XDD。

因此，我會花一些篇幅，用 PoC 的程式碼來說明原理，最後一段在來補充這些想法跟市面上成熟的 solution 如何對應。先花點時間練過這題目是值得的，除了更清楚背後的原理之外，你才清楚如何正確的 "規劃" 你的管理方式。

<!--more-->


# 0. 權限管理是在做什麼?

基本上，我把 "權限管理" 當作商業需求來看待，而不是當成技術需求。我先用一個例子來表達 什麼叫 "權限管理"，同時定義一下 "好" 的權限管理機制是 "好在哪裡"。有定義才能量化，你想出各種方法時才有比較基準。

我就拿銷售系統當作案例好了。某零售商 (B2B)，每天可能有上百筆交易紀錄，每個月累計下來會有上千筆紀錄，每年會有上萬筆。這些訂單都是由 10+ 個業務助理輸入維護，有 5 位左右的管理階層人員，需要透過訂單的統計數字來做管理決策。有 1 ~ 2 位系統管理人員，負責調整這些安全相關設定。

老闆對權限管理的期待 (商業上的期待) 是:  
希望業務助理能負責繁重的訂單輸入，確認，修改等等任務；對助理而言，操作越簡便越好，但是要避免太方便的操作 (例如批次匯出)，讓基層人員過度容易就偷走業務機密 (業績，客戶清單)。而管理階層則要能掌握業績與趨勢，操作各種統計報表；要避免的是管理人員造假訂單內容。系統管理人員必須解決各種操作上的問題，不過他們不是業務單位，不該修改訂單，也不該看到任何業績相關的統計資訊。

而管理這些訂單的系統，則有多個功能讓這些人使用。我們要探討的就是: 這個系統該規劃什麼樣的權限管理機制，來管理每個人能做什麼，不能做什麼。


從這個例子，大概就可以展開一些系統化的做法了。一般來說，各種系統分析的人，都會用他的方法，盤點或是推導出這些資訊:

1. 使用者設定:
1. 系統可操作的功能 (選單、按鈕、報表等):
1. 管理的規則或方法

我們要探討的，就是 (3) 了，而先不管 (3) 怎麼做，最終能得到的結果，就是明確的指出每一個使用者，能用那些功能。

以這個例子，就當作總共有 20 人好了，系統相關功能 (以功能選單，功能按鈕等這些必須被控制的操作點) 有 50 個地方，最多就有 20 x 50 = 1000 種組合。你可以用一個 20 x 50 的表格來管理，理論上這 1000 種組合你都辦得到 (系統都能設定的出來)，最有彈性的設計。你也可以把使用者分成三類 (業助、主管、系統管理員)，而功能分成五類 (訂單輸入、訂單批次處理、訂單處理、業績統計、安全設定)，那麼你要管理的組合就變成 3 x 5 = 15 種組合了。

這些多出來的分類定義 (過程先省略，有點複雜)，最後結果其實就是常聽到的:
1. 使用者的分類: 角色 (Role)
1. 功能的分類: 權限 (Permission)

至於，好壞怎麼定義?
方法 1 有 1000 種可被設定的組合，這數字代表管理的困難度。而這些組合非常精細，只要你肯花時間設定，應該能完美滿足老闆的期待。所謂精確度，就是指系統實際給使用者的權限，跟老闆期望使用者能否操作的結果是一制的，若有不醫治就歸類在非預期的組合。我就先當作這案例的精確度是 100% ( 非預期的組合 / 全部的組合 x 100% )

方法 2 如果規劃不當，例如角色定義不對，或是某些功能設計互相衝突，無法正確分類，導致相關權限要求，系統設定不出來 (例如批次處理的功能，包含了訂單處理，而你無法分開設定，要嘛就一起開，要嘛就一起關)，你可能賺到困難度的分數，但是失掉精確度的分數。

這案例到這邊為止，大家大概對於 "權限管理" 有個明確的理解了吧? 我特地把 SA 分兩段來看，因為第一段是呈現結果，不管你怎麼設計安全機制，都會有第一段的結果，你可以用它來評斷好不好管理，以及管理的精不精確。

第二段展開 role / permission, 這就不一定每個方式都得這樣做，他已經屬於某種管理方法必要的設計了，是屬於不團管理機制設計發揮的空間。定義的越好，就越能兼顧精確度與好不好管理。大家發揮的空間就在這邊。

這段完全沒有牽涉任何技術或是理論，我單純就系統設計的目的來看權限管理。如果你看懂了，就繼續往下吧!






# 1. 權限基礎: 認證與授權

幾乎所有 "架構面試題" 的第一步，都是先定義問題該透過什麼介面 (interface) 來處理，然後才來探討這介面背後該怎麼實作 (implement)，最後用案例或是指標，來評估成效如何。

前面的簡介，已經先把概念說明過一輪了，接下來我就進一步把系統的介面 ( code interface ) 定義出來。我寫這主題的第一件事，就是先建立解題的模型。

案例的第一段，就是講 "使用者"，以及衍生出來的 "角色"。雖說 "角色" 是特定管理方式的設計，不過它實在太普遍了，所以我就直接放進來說明。權限管控的基礎建設，就是認證與授權，而 認證 就是處理 使用者 的部分。

我直接從 .NET 處理這件事的基本介面開始看吧，我從 .NET 1.1 那個年代就開始寫 C# 了，我想能比我還清楚這些歷史的人應該不多了吧? 不得不說 Microsoft 在這件事的設計上相當漂亮，早在當年 .NET 1.1 的年代就已經存在的兩個介面，大概就能回答這個問題了。這兩個介面分別是:

- IIdentity
- IPrincipal

我挖了 .net source code 來看，這兩個 interface 的定義長這樣:

// ref: https://github.com/microsoft/referencesource/tree/master/mscorlib/system/security/principal

```csharp

[System.Runtime.InteropServices.ComVisible(true)]
public interface IIdentity {
    // Access to the name string
    string Name { get; }

    // Access to Authentication 'type' info
    string AuthenticationType { get; }

    // Determine if this represents the unauthenticated identity
    bool IsAuthenticated { get; }
}


[System.Runtime.InteropServices.ComVisible(true)]
public interface IPrincipal {
    // Retrieve the identity object
    IIdentity Identity { get; }

    // Perform a check for a specific role
    bool IsInRole (string role);
}

```

IIdentity, 代表目前登入的人是 "誰" ? 從這 interface 可以看得出他的意圖。這介面會告訴你這人的名字 (Name)，是否已經通過認證 (IsAuthenticated)? 以及這人是通過哪一種認證機制確認過的 (AuthenticationType, 例如 windows 認證)。而 IPrincipal 則進一步，告訴你這個人是否被授予某個指定的角色 (IsInRole(role))? 基本上，這兩個介面組合起來，可以滿足絕大部分的認證機制，甚至基本的角色檢查就能搞定的場合都能 cover 了，可以說 IPrincipal 也已經替更完整的授權機制做好準備了。

接下來我簡單示範一下這兩個介面的用法，如果你的情境很單純，只要確認目前使用者的角色，就足以做好權限管控的話，那靠這兩個介面就夠了。基本流程是這樣:

0. 在正常的登入過程中，將成功通過驗證的使用者資訊 (IPrincipal) 放進 Thread.CurrentPrincipal
1. 當你要檢查角色時，取得 Thread.CurrentPrincipal
1. 用 IPrincipal.IsInRole(string role) 來檢驗身分，你的應用程式就能做好對應的判斷

如果你要用 console app 的話，大概就像這樣:

// sample code
```csharp
        static void Main(string[] args)
        {
            // deom: run query orders function
            Sales_Report();
        }

        static void Sales_Report()
        {
            var user = Thread.CurrentPrincipal;

            if (user.IsInRole("manager"))
            {
                // query orders
                Console.WriteLine("Query orders: ......");
            }
            else
            {
                // no permission
                Console.WriteLine("No permission to query orders.");
            }
        }
```

複雜一點的開發情境，我們換到 ASP.NET MVC, 寫起來更簡單了，只要標上 AuthorizeAttribute 就夠了:

Ref: https://learn.microsoft.com/zh-tw/aspnet/core/security/authorization/roles?view=aspnetcore-8.0

```csharp
[Authorize(Roles = "manager")]
public class ControlPanelController : Controller
{
    public IActionResult Sales_Report() =>
        Content("query orders: ......");
}
```

其實背後的作法一模一樣，只是 MVC 的框架都幫你藏起來了。首先，驗證的結果 (不論是放在 cookie, 或是其他地方) 透過 middleware 處理後，會放在 HttpContext.Current.User (這就是 IPrincipal 的物件)，而後續 request 轉送到 controller 的過程中，就會按照 controller / action 上面的 AuthorizeAttribute 做對應的處理了。處理方式一樣是透過 IPrincipal.IsInRole( ) 來判定，只是整個過程除了標上 AuthorizeAttribute 之外，其他都被藏在 MVC 框架內了。


請先記好這兩個基本介面的用途，後面會不斷地看到它。準備好了就繼續往下看吧~




## 抽象化授權機制

如果只靠前面的範例，檢查角色就能搞定一切的話，就不會有這篇文章了。首先，為了方便後面的討論，我先定義解題的模型。這模型我會談兩個意圖:

1. 應用程式該怎麼檢查權限?
1. 這些權限如何運作與儲存 (必要的話會涉及 database schema)?

你可以想像一個是前台 (end user) 的處理邏輯，另一個事後端設定 (admin) 的處理邏輯，兩者必須互相搭配才能發揮作用。我用這張圖來解釋:

// https://docs.google.com/presentation/d/1ROOGUMrVnSzYiJcUt_KPeLtjnYFxy-pcnCDDNssYtWk/edit#slide=id.g2cff021dc9b_0_0   , P2

框起來的部分就是上面那兩點，也就是各種不同的授權機制要探討的範圍；而外圍的每個元件就是我所謂的解題框架。

以 (1) 來說，授權檢查機制需要幾個輸入資訊，才能判定當下狀況能否允許執行? 需要的資訊有:

1. 你是誰: 是誰要執行這功能? 
1. 要做什麼: 現在要執行的這個功能相關資訊為何?
1. 權限設定: 哪裡找的到管理者調整好的權限設定 (資料庫)?

(1) 就是前面談到的 IPrincipal, 而 (2) 則是現在要談的 Permission, 定義了要被授權的最小單位，例如資料的 CRUD 可能就是一組 Permission，你可以個別設定誰能夠執行他。這邊提到的 "設定"，就是指 (3) 了。判定的結果，可能是 Allow or Deny，根據這結果，你的應用程式就能做出正確的反應。

講到這邊，我先挑最廣為人知的 RBAC 來切入吧! 先借用 RBAC Wiki 的名詞解釋，以及一張對應的結構圖來說明上面這堆東西的關係，跟正式的名詞定義:

參考資訊: Wikipedia: RBAC

![](https://upload.wikimedia.org/wikipedia/en/1/19/Role-based_access_control.jpg)

> wiki: RBAC, https://en.wikipedia.org/wiki/Role-based_access_control

這張圖是整個 RBAC 的關鍵，整個權限控制的體系，就是圍繞在 "Role" 跟 "Permission" 之間的對應關係，也就是中間那條線上面標示的 "permission assignment". 把圖上的所有元件都展開，其實就是 wiki 上講的這幾項:

```
S = Subject = A person or automated agent
R = Role = Job function or title which defines an authority level
P = Permissions = An approval of a mode of access to a resource
SE = Session = A mapping involving S, R and/or P
SA = Subject Assignment
PA = Permission Assignment
```

這些名詞雖然生硬一點，但是搞懂他是件好事，各種相關的技術，文件大概都會用這些名詞來說明，而且會跨多個領域 (例如會牽扯到單一登入等等)，你不先搞懂觀念的話，很難單靠文件說明就把那麼多領域的技術串在一起。

- S (Subject): 其實就是對應到 IPrincipal
- R (Role): 角色定義, IPrincipal 的 IsInRole( ) 就是在檢查 S - R 之間的關聯
- P (Permission): 就是指權限，授權的最小單位
- O (Operation): 最終呈現在使用者端能操作的功能。要能執行這些操作，可能需要取得 0 ~ n 個不同的 permission 才能執行

我這邊就先定義這幾個 interface, 後面就開始用 code 來討論了。我補上這幾個 .NET 沒有定義的介面，把整個解題的模型補齊:

P: ICustomPermission, 要被管理的權限的最小單位
O: ICustomOperation, 最終要呈現在你應用程式上操作的功能

舉例來說，訂單管理系統的 permission 可能有: 訂單的 Create, Read, Update, Delete, 以及所有訂單的 Query。
至於 operation, 就是指對使用者而言可以操作的功能，通常一個功能都包含一系列的操作，例如統計報表，或是批次匯入訂單。每個 operation 可能都需要多個 permission 才能執行。

我先補上在這模型上必要的幾個 interface, 除了 .NET 原本就提供的 IPrincipal (包含 IIdeneity) 之外，對應模型，我補上這幾個 interface:

- IPrincipal (對應: Subject)
- ICustomRole (對應: Role)
- ICustomPermission (對應: Permission)
- ICustomOperation (對應: Operation)

我沒有特別說明的:
- Organisation: 實際上 role 的組成可能更為複雜, 包含階層關係 (role hierarchy), 甚至直接跟組織的部門或是職稱對應 (organization, 或是常見的 LDAP 提到的 OU), 也有可能允許管理者自訂群組 (簡化的會員管理機制，都會存在的 group)
- Session: 認證機制通常伴隨著登入那瞬間的檢驗 (例如: 帳號密碼驗證)，以及將檢驗的結果持續一段時間的機制 (例如: 將認證結果放在 cookie 持續 20 min)。持續的載體通常就稱作 session. 會特別提這個是因為, 通常認證的來源都是 session 機制提供的, 他負責管控認證結果的生命週期。簡單的來說，認證有效期限就是從登入到登出這段時間為止，因此代表 session 的物件，往往就包含了認證的必要資訊 (例如: IPrincipal)

其他沒有直接對應到的，我放在這邊:

- ICustomAuthorization (對應 圖一，封裝整個授權檢查機制, 包含資料庫的存取 )

最後，補上這幾個 interface 定義，除了基本的 Name 之外，每個介面都有定義他主要的任務，這我就直接寫在註解上面了:

```csharp

    public interface ICustomRole
    {
        string Name { get; }
    }

    public interface ICustomPremission
    {
        string Name { get; }

        // 回答目前的 user 是否已獲得這權限的許可?
        bool IsGranted(IPrincipal user);
    }

    public interface ICustomOperation
    {
        string Name { get; }

        // 列舉要執行這個操作 (operation) 必須被許可的權限有哪些?
        IEnumerable<ICustomPremission> RequiredPermissions { get; }
    }

    public interface ICustomAuthorization
    {
        // 綜合判斷: 指定的使用者 (user) 是否滿足要執行指定的操作 (operation) 的必要條件?
        bool IsAuthorized(IPrincipal user, ICustomOperation operation);
    }

```




# 2. RBAC, Role based access control

基礎都交代完了，直接來看第一個機制: RBAC，最廣為人知, 以角色為基礎的權限控制。

前面先貼過了，這邊正式再交代一次。為了寫這段，我還特地查了 wiki 確認我每個環節的認知都沒錯誤... Wiki 對 RBAC 的解釋與說明:
> wiki: RBAC, https://en.wikipedia.org/wiki/Role-based_access_control

其中，這張圖貫穿了整份說明，他清楚地闡述了 RBAC 背後的結構:
![](https://upload.wikimedia.org/wikipedia/en/1/19/Role-based_access_control.jpg)

而要說明 RBAC 的結構，有幾個重要的基本用語需要先弄清楚 (這前面也貼過了)。我截錄 wiki 上面的說明:

```
S = Subject = A person or automated agent
R = Role = Job function or title which defines an authority level
P = Permissions = An approval of a mode of access to a resource
SE = Session = A mapping involving S, R and/or P
SA = Subject Assignment
PA = Permission Assignment
```

先講 Role, 在結構上, 很多人會把 Role 跟 Group 搞混, 認為他們是同一件事。從操作上他們很像沒錯，主要的差別在他們的定義。上面這段替 Role 下的定義是:

>  Role = Job function or title which defines an authority level

Role 代表了能執行某個任務的授權，意思是他背後的涵義已經包含了某種 "授權"。因此你不能只是把它當成 Group 使用，你指派了某個 Role 給 User，就代表你已經授權他有執行某些任務的身分了。而 Group 則單純是分類，你可以自由地替 User 做群組分類，除非你後續拿 Group 做進一步的應用，否則單純將 User 加入 Group 是沒有任何影響的。


也因為有這層關係，一般而言，系統有那些 Role, 應該是設計階段就應該確定的 (絕對不是讓管理人員隨便愛開幾個 Role 就開)。系統設計之初，就應該規劃好運作流程上該區分哪幾種角色，那些功能必須有那些角色的身分才能執行。這些關係可以直接在系統開發階段就實做，交付給 user 使用後，只需要開放 user assignment 的機制 (指派 role 給 user) 就足以完成整個授權管理任務了。

這段很重要，你沒有從這角度來考量的話，可能整個設計跟用法就歪掉了... (這種案例我看過很多)。隨便舉一個大家耳熟能詳的例子: windows 的帳號管理。

最簡單的 desktop OS, 就內建這三個 role:

- Users
- Power Users
- Administrators

如果你有加入 AD, 則會再多這些 role:

- Domain Users
- Domain Adminstrators

如果你有安裝其他 Microsoft Backoffice 的服務 (年代久遠，現在是不是改名了?)，例如 SQL server, Exchange server 等等，可能都還會增加其他的 roles, 我就不一一列舉。

這個案例，就是我所說的，角色的定義應該對準你的 business process, 而不是單純工程問題, 你把機制開出來給使用者自己設定就好了, 這是包含你的應用程式對於流程跟使用者職責的想法對應的規格，應該在開發階段就弄清楚才對。

回到這個案例，訂單管理系統，我們該定義那些角色 (Role)? 該定義那些權限 (Permission)? 該定義那些操作 (Operation)?

Role: 按照使用者如何操作這系統，需要參與的角色來區分。這邊完全是產品設計與業務相關，分析的過程我沒辦法掌握得那麼清晰，我就直接貼結果了。通常這些角色都會跟組織圖，還有職務說明 (job description) 對應，即使沒有經過分析，你從這角度來推敲也不會偏離太遠。相關的角色有:

- 系統管理員 (system-admin), 會負責建立帳號, 調整授權相關設定。不過這屬於系統基底共通的，後面的案例我都會跳過這部分。
- 業務主管 (sales-manager), 能查閱全域的訂單資料，訂單的統計，業績統計與其他各種查詢功能與報表調閱。
- 業務專員 (sales-operator), 能負責輸入訂單, 更新訂單處理狀態。大範圍的查詢與統計功能受到限制，只能處理例行資料更新作業


Permission: 這部分困難一點，基本上 permission 最好對應到工程上的基本操作，方便系統在最核心的地方就統一控管。如果你不知道怎麼規劃 permission, 抓出主要的實體 (entity, 在這邊主要是訂單 - orders), 然後套上 CRUD / Query, 大致上就有本的架構出來了。還記得前幾篇我都在強調 API First, 裡面提到透過狀態轉移的分析與操作過程嗎? 如果你有做這樣的分析，那麼狀態圖上面的轉移清單 (箭頭)，會比 CRUD 來的更合適。

忘記的人可以看一下這篇:

至於這個案例，我先用簡單的 CRUD / Query 當案例，方便我繼續討論下去。訂單管理系統應該有這些 permissions:

- 新增訂單 (order-create)
- 讀取訂單 (order-read)
- 更新訂單 (order-update)
- 刪除訂單 (order-delete)
- 查詢訂單 (orders-query)

Operation: 這部分，主要是看你的產品或是服務設計，最終包裝成那些功能? 通常會是系統的功能選單，或是側欄，指令清單等等。應由產品設計的角度來提出。一樣，這邊我先直接照我的想像列舉。假設訂單管理系統登入後，左側測攔有這些功能讓業務點選:

- 業績查詢 (Sales_Report)
- 當日訂單總覽 (Sales_DailyReport)
- 輸入訂單 (Orders_Create)
- 訂單狀態更新維護 (Orders_Process)
- 訂單批次作業 (匯入) (Orders_BatchImport)
- ... (以下略)

好，當產品開發團隊的工程師 (定義 permission)、設計師 (定義 operation)、產品經理 (定義流程中需要的角色 role) 之後，如何把它們串起來，就是 RBAC 發揮的地方了。我列兩張表格，分別代表前面 wiki 說明 RBAC 的那張關聯圖的 permission assignment, 以及 permission - operation 之間的對應 (圖上沒給名字, 我自己取名叫 operation assignment):

permission assignment: 試著想像，每種角色拿到對應的權限，是否有可能組合出他不該碰到的資訊? 以這為原則，來填這張表

| Permission \ Role | system-admin | sales-manager | sales-operator |
|--------------------|-----------------|------------------|-----------------|
|order-create          |                        |                           | O                     |
|order-read            |                       | O                         | O                     |
|order-update        |                         |                          | O                      |
|order-delete          |                        |                           | O                     |
|orders-query        |                         |O                       |                           |



operation assignment: 試著推演，每個功能需要哪些權限才能組合的出來? 這表可以讓負責開發的工程師來填。其實這可以跟開發的程式碼對應的。

|Permission \ Operations| sales report | sales daily-report | orders-create | orders-process | orders-batchimport |
|--------------------------|--------------|--------------------|-----------------|-----------------|-----------------------|
|order-create                 |                   |                               |                       |                      |  |
|order-read                    |                    |       ||||
|order-update                ||||||
|order-delete                 ||||||
|orders-query                ||||||


理論上，有這兩張表，你應該能試算 Role \ Operation 的對照表的。這邊我先用人腦來展開，後面我可以示範怎麼用 code 來展開。先展開的目的是驗證設計有無疏失，最終結果可以讓產品經理或是客戶來確認，是否對應的角色能執行的功能都如預期?

| Role \ Operation |
(待補)

切記，展開的這張表是 "結果"，如果不對的話不是直接改這張表就好，而是要調整前面兩個來源的表格。結果不對可能隱含的問題是，業務需求跟系統設計就有衝突了。例如某角色不應該有建立訂單的能力，但是他卻意外地被授予批次匯入訂單的能力。雖然麻煩點，但是他只要匯入時的檔案只準備一筆資料，他還是可以達成目的。這就是系統權限機制設計上的漏洞。

這些都確認好了之後，就可以動手開發了。RBAC 的優點就是簡單直覺，而且最大的好處是: 正確的規劃設計的話，幾乎不需要依賴資料庫就能讓安全機制順利的運作。唯一需要資料庫的地方是，你必須儲存 role assignment (紀錄每個 user 的所屬 role 有哪些)，並且在適當時機 (例如登入時) 載入他，同時將它存放在你的 session 機制內，直到 session 結束為止，都可以不需要再到 DB 查詢一次。

在 OrdersAuthorization 的實做中，只有一個必要的 method: IsAuthorized(IPrincipal user, ICustomOperation operation) 而已，主要任務就是回覆 Subject 與 Operation 是否存在授權的關聯。這邊的路徑: Subject -> Role -> Permission -> Operation, 只有 Subject -> Role 這段是必須存在資料庫的，其他關連 (其實就是上面分析過程中要產生的兩張表格) 都是設計 & 開發階段就能決定好的資訊，因此若沒有其他考量，這對照資訊寫死在 code 內，或是存放於 config 內就已經足夠了。要放到 DB 不是不行，沒有必要的話只是加重 DB init 與 maintainess 的負擔而已

最後，我示範的版本 source code 如下 (請參考: AndrewDemo.OrdersRBAC 專案)


```csharp


```















用我前面的例子，訂單管理來說，R 就是替人的角色做歸納，主要是以 job function 的角度來歸類 (例如: 主管、操作人員
)；而 P 就是存取資源的核准方式 (好繞舌)，舉例來說每筆訂單都必須被核准，你才能對他做 CRUD 的操作，而對於所有的訂單，則需要被核准才能查詢 (Query)。

而那些角色 (R) 能被指派到那些權限 (P)，就是權限指派 (PA)。以我這個案例來說，訂單查詢系統的 PA 的清單應該長這樣:

| Role \ Permission | Order Create | Order Read | Order Update | Order Delete | Orders Query |
| Manager         | --  | O | -- | --  | O |
| Operator         | O | O | O | O | -- |

而實際的系統開發，不大可能那麼死板，就是開發 CRUD/Q 這些功能而已。每個功能應該背後都會組合這些動作，主管看的報表應該是由各種 Query + R 組合開發出來的，而操作人員在輸入訂單，只能單筆操作，對已知  ID 的訂單內容進行維護等等。操作人員不被允許大範圍查閱所有訂單資料，避免機密資料 (例如年度業績) 外洩。

你可能會問: 我 Create 訂單，可能要檢查一些條件是否衝突，不能 Query 就不能做啊... 如果真的有這種需求，應該包含在訂單的 "Create" function 內，而不是讓 Application 直接在每個需要 Create Order 的地方都處理 Query .. (最常見的是手動輸入，還有批次匯入，要寫兩次 create 的邏輯)

這樣設計的好處，就是邏輯非常明確，而且能從最源頭就開始管控。只要每個人的 CRUD/Q 都有精確管理好，那麼 Product Owner / Develop 即使做了不洽當的設計，也不能違背這些原則，錯誤設計導致不應該發生的意外機率就降低很多，能避免很多基本原則的衝突。

很多工程師會踩進來的誤區就在這裡。工程師會開發非常 "彈性" 的介面，例如讓客戶還能有介面自訂 R / P / PA 的設定，讓他能自由的更新或調整。我認為這不應該是 runtime 該調整的規則，這是 service design 階段就該確認的事情才對。你讓客戶自己調整，最後的結果就是每個角色什麼都能做了，最後權限控制機制淪為虛設..

既然開發設計階段這些設計就該定案，系統有多少角色(R)、權限(P)、權限指派(PA) 都應變成產品規格的一部分，他應該是整套系統背後運作的憲法才對，你可以設計各式各樣的功能，但是所有功能都不能直接或是間接違背 R/P/PA 的關係。若有發生，通常是設計越權了，你正在設計一個有安全隱憂的功能，或是你該檢討 R/P/PA 的設計是否不合適。

舉一個大家都耳熟能詳的案例: windows 的帳號管理機制。

windows 一安裝完成, 就會有預設的 Adminstrations / Power Users / Users 角色，這些角色能做哪些事情 (例如安裝/移除軟體，開啟軟體，特定目錄的讀寫權限等等) 早就有一組預設的設計了，背後就是這道理，windows 的產品團隊早就把他們都規劃好，並且內建在整個安全體系內。

不過 windows 的安全機制遠不只 RBAC, 他當然也允許進一步的調整 (PA 在 windows 安全機制內是允許 administrators 調整的), 但是就大部分人的使用經驗來看，這結構已經滿足主要需求了，剩下的是你要有效管理外圍的對應，例如那些帳號該屬於那些角色。


接下來就到了 coding 時間，來看一下對訂單管理系統，我該怎麼實做這權限控制機制?

我會 "刻意" 拿掉不必要的彈性 (就上面講的)，在設計階段要確定的事情我會直接寫死在 code 內來強調，當這樣的設計能夠通過所有主要情境的測試時，代表你的設計已經能正確的描述這業務領域的原則了。我放棄 "通用" 的 IAuthorization 實做: GenericAuthorization, 專為訂單管理系統設計一個授權管理機制: OrdersAuthorization
















<!-- 


為了方便示範，後面的程式碼我都會這樣簡化，統一用這兩個介面為基礎, 用 console application 當作範例。分別來探討:

1. 應用程式該怎麼利用這些介面來開發功能?
1. 權限管理機制應該怎麼規劃與管理授權資訊?



翻成白話，就是 "授權機制" 必需不斷的回答這個問題:

> 問題: 告訴我 (某個人) 依據目前的 (權限設定) 規範，能不能夠執行 (某個功能) ?

這邊我用括號圈起來的，就是關鍵的資訊:

(某個人) -> 就是認證，通過認證的結果，你可以直接相信他就是代表真實世界的某人。通常會是某個 ID，或是 JWT。
(某個功能) -> 要做的事情，通常是應用程式的授權管理單位。例如能不能
(權限設定) -> 就是安全機制，包含設定的資料庫，也包含檢查的規則，這兩個通常是一整套的，也就是常見的 RBAC, PBAC, ABAC 等等方法。



要繼續往下，我得先把整個安全機制的模型先建立起來。這邊我就併到第一個機制 RBAC 一起談吧。










如果把 "權限設定" 的部分抽象化成 C# interface:  IAuthorization, 那大概會是這個樣子:

// 
```csharp

    public interface IAuthorization
    {
        bool HasPermission(IPrincipal user, IAppFunction action);
    }

```

其實， user / action 都可以極度簡化成只有一個 ID 就夠了，不過那樣會犧牲很多彈性與效率，因此我介面定義還是保留用 interface 的方式來呈現。認證部分我直接沿用 .NET 內建的 IPrincipal, 而功能我自己定一個 IAppFunction, 用介面而不用 ID，因為我希望把部分判斷的職責，歸類在認證機制 (例如確認你的身分) 來負責。適度的分攤責任，可以降低整體的複雜度。如果認證被過度簡化成只是個 ID，那麼確認身分 (角色) 就得由授權機制一起處理，那你會創造出一個很肥大的複雜機制出來..

因此，Microsoft 除了在 IIdentity 把基本身分識別 ( id, 是否通過認證, 認證類型 ) 封裝起來後，往外擴大一步，把這身分識別綁定的角色也一起綁進來，就是 IPrincipal. 不過他不列舉所有的 Role 給你，只開放 "詢問" 而已，就是 .IsInRole(roleName) 這個 method 而已。

因此，依樣畫葫蘆，要被控制能不能使用的 "功能"，我也往前跨一點，除了功能本身之外，我也往身分識別靠近一階，如果把授權拆成幾個基本的 permission, 那麼每個功能應該是要求多個 permission 的組合。例如基本的授權有訂單的 CRUD + Query, 那麼輸入訂單的功能就應該是 C + R + U 的組合。這麼一來需要定義的 permission 應該會大幅降低，從一個系統可能有上百個功能，降為 1 ~ 20 左右的 permission 組合就夠了。

所以我也定義了一個 interface 來描述要被管控的功能:

```csharp

    public interface IAppFunction
    {
        string Name { get; }
        string[] RequiredPermissions { get; }
    }

```


> 所謂的 "複雜度", 我很愛用 "乘法" 跟 "加法" 來對比。
> 
> 實際情況下，如果我們最終的需求，是需要組合出 100 種可能的組態的話，你也許可以拆成 10 x 10 種規則來設計，或是 1 x 100 種規則都能達到同樣目的。
> 不過，10 x 10 的設計，你會需要開發 10 + 10 = 20 個規則來組合；
> 然而 1 x 100 的設計，你就得開發 1 + 100 個規則。
> 很明顯的就開發的複雜度來說，10 x 10 要容易的多，而在應用時你就要有能力把你的情境正確的拆解才能實現。RBAC 就是典型的這類應用，這看到後面你就理解我的用意了




實際拿例子 + 程式碼來說明會比較清楚。如果我想實作一個銷售系統，只允許主管的帳號可以查閱機密資訊 (例如業績，統計資料，每筆訂單資訊)，而操作員只能輸入資料 (已知訂單 ID 的 CRUD)，那麼這段 code 寫起來大概像這樣:

```csharp


    internal class Program
    {
        private static readonly IAuthorization authorization = new GenericAuthorization();


        static void Main(string[] args)
        {
            // query orders
            QueryOrders();
        }

        static void QueryOrders()
        {
            var user = GetCurrentUser();
            var function = GetAppFunction("query-orders");

            var hasPermission = authorization.HasPermission(user, function);

            if (hasPermission)
            {
                // query orders
                Console.WriteLine("Query orders: ......");
            }
            else
            {
                // no permission
                Console.WriteLine("No permission to query orders.");
            }
        }



        static IPrincipal GetCurrentUser()
        {
            return new GenericPrincipal(
                new GenericIdentity("Andrew"), 
                new[] { "Manager" });
        }

        static IAppFunction GetAppFunction(string functionName)
        {
            switch (functionName)
            {
                case "query-orders":
                    return new GenericAppFunction(
                        "query-orders", 
                        new[] { "Manager" });

                case "create-order":
                    return new GenericAppFunction(
                        "create-order", 
                        new[] { "Assistant" });
            }

            throw new ArgumentOutOfRangeException($"function ({functionName}) not found.");
        }
    }


```



如果你要用在 Web API 上面，你的 controller 大概會長這個樣子:

```csharp

[Authorize(Roles = "Manager")]
public IEnumerator<Order> QueryOrders(QueryOrderRequest request)
{
    // 略
}

```

MVC 的開發框架，會在背後處理掉一堆瑣事，包含從 HttpContext 取得 Current User ( 就是 IPrincipal ), 同時會用 Reflection 呼叫 Action: QueryOrders 前，先按照上面標記的 Attribute 比對 Role 是否符合 IPrincipal 的比對，符合才會 Invoke Action, 不符合預設就丟回 403 告知沒有權限。雖然程式碼簡化很多，只剩下一行 Attribute 標記，但是背後的規則完全不變。

不過，開發 App 是很後面的事情，既然訂了 interface, 就應該先寫 test 才對。我打算用 unit test 來呈現，那麼寫成單元測試後，大概會是這樣:


```csharp

// 測試案例 01:
// 登入使用者是 andrew, 所屬角色清單為 [Manager]
// 執行的功能 [query-orders], 要求的角色清單為 [Manager]
// 檢測是否有足夠權限執行功能，預期的結果是 "允許"
[TestCase]
public void Test1()
{
    var user = GetCurrentUser("andrew", new string[] {"Manager"});
    var action = GetAppFunction("query-orders", "Manager");

    Assert.IsTrue(security.CheckPermission(user, action));
}

```

到這邊，題目的定義，包含介面定義，預期的行為應該都算完成了，接下來我就要開始展開幾種常見的權限管理巧 (清單如下)，並且用這介面來敘述案例，最後補上實做直到通過所有測試為止。很典型的 TDD 流程，正好讓大家從怎麼使用，往回推敲到如何設計背後機制的過程。

大家常聽到的權限管理作法，不外乎這幾種:

- RBAC (Role Based Access Control). 角色權限控制
- PBAC (Policy Based Access Control). 策略權限控制
- ABAC (Role Based Access Control). 屬性權限控制
- Claim (抱歉，這我不知道怎麼翻，維持原文)
- ACL (Access Control List)

我會先用 PoC 的角度，完全自己實做，捨棄所有不重要的細節，只看結構。理解原理後，我會再補充一下實際廠商或是服務提供的作法是什麼。通常，如果前面都看得懂，最後你看到這些廠商提供的 API 或是文件，大概一看就懂了。理解原理才是我期待的結果，因為安全機制是個不好懂的東西，原廠的文件我其實都沒耐心看完，不過因為我懂這些原理，所以大部分情況下，我看完 overview 後就可以直接看 API spec 了，因為道理都懂了之後，你看 code 就知道該怎麼用了。有了這層掌握，你才有餘力去思考如何進一步靈活的運用安全機制，而不是花費大部分的力氣在搞懂該怎麼正確的使用他 (這只是最低的基本要求)。

看到這邊，如果準備好了，就繼續往下看吧!
 -->



# xxx 2. RBAC, Role based access control

首先，來談最廣為人知的 RBAC, 以角色為基礎的權限控制。

我為了寫這段，還特地查了 wiki 確認我每個環節的認知都沒錯誤... 簡單的概念寫成文件就是這樣，想通了看文件都很簡單，沒想通看起來就像天書一樣... 

![](https://upload.wikimedia.org/wikipedia/en/1/19/Role-based_access_control.jpg)

> wiki: RBAC, https://en.wikipedia.org/wiki/Role-based_access_control

這張圖是整個 RBAC 的關鍵，整個權限控制的體系，就是圍繞在 "Role" 跟 "Permission" 之間的對應，也就是中間那條線上面標示的 "permission assignment". 

節錄 wiki 上面的說明:

```
S = Subject = A person or automated agent
R = Role = Job function or title which defines an authority level
P = Permissions = An approval of a mode of access to a resource
SE = Session = A mapping involving S, R and/or P
SA = Subject Assignment
PA = Permission Assignment
```

用我前面的例子，訂單管理來說，R 就是替人的角色做歸納，主要是以 job function 的角度來歸類 (例如: 主管、操作人員
)；而 P 就是存取資源的核准方式 (好繞舌)，舉例來說每筆訂單都必須被核准，你才能對他做 CRUD 的操作，而對於所有的訂單，則需要被核准才能查詢 (Query)。

而那些角色 (R) 能被指派到那些權限 (P)，就是權限指派 (PA)。以我這個案例來說，訂單查詢系統的 PA 的清單應該長這樣:

| Role \ Permission | Order Create | Order Read | Order Update | Order Delete | Orders Query |
| Manager         | --  | O | -- | --  | O |
| Operator         | O | O | O | O | -- |

而實際的系統開發，不大可能那麼死板，就是開發 CRUD/Q 這些功能而已。每個功能應該背後都會組合這些動作，主管看的報表應該是由各種 Query + R 組合開發出來的，而操作人員在輸入訂單，只能單筆操作，對已知  ID 的訂單內容進行維護等等。操作人員不被允許大範圍查閱所有訂單資料，避免機密資料 (例如年度業績) 外洩。

你可能會問: 我 Create 訂單，可能要檢查一些條件是否衝突，不能 Query 就不能做啊... 如果真的有這種需求，應該包含在訂單的 "Create" function 內，而不是讓 Application 直接在每個需要 Create Order 的地方都處理 Query .. (最常見的是手動輸入，還有批次匯入，要寫兩次 create 的邏輯)

這樣設計的好處，就是邏輯非常明確，而且能從最源頭就開始管控。只要每個人的 CRUD/Q 都有精確管理好，那麼 Product Owner / Develop 即使做了不洽當的設計，也不能違背這些原則，錯誤設計導致不應該發生的意外機率就降低很多，能避免很多基本原則的衝突。

很多工程師會踩進來的誤區就在這裡。工程師會開發非常 "彈性" 的介面，例如讓客戶還能有介面自訂 R / P / PA 的設定，讓他能自由的更新或調整。我認為這不應該是 runtime 該調整的規則，這是 service design 階段就該確認的事情才對。你讓客戶自己調整，最後的結果就是每個角色什麼都能做了，最後權限控制機制淪為虛設..

既然開發設計階段這些設計就該定案，系統有多少角色(R)、權限(P)、權限指派(PA) 都應變成產品規格的一部分，他應該是整套系統背後運作的憲法才對，你可以設計各式各樣的功能，但是所有功能都不能直接或是間接違背 R/P/PA 的關係。若有發生，通常是設計越權了，你正在設計一個有安全隱憂的功能，或是你該檢討 R/P/PA 的設計是否不合適。

舉一個大家都耳熟能詳的案例: windows 的帳號管理機制。

windows 一安裝完成, 就會有預設的 Adminstrations / Power Users / Users 角色，這些角色能做哪些事情 (例如安裝/移除軟體，開啟軟體，特定目錄的讀寫權限等等) 早就有一組預設的設計了，背後就是這道理，windows 的產品團隊早就把他們都規劃好，並且內建在整個安全體系內。

不過 windows 的安全機制遠不只 RBAC, 他當然也允許進一步的調整 (PA 在 windows 安全機制內是允許 administrators 調整的), 但是就大部分人的使用經驗來看，這結構已經滿足主要需求了，剩下的是你要有效管理外圍的對應，例如那些帳號該屬於那些角色。


接下來就到了 coding 時間，來看一下對訂單管理系統，我該怎麼實做這權限控制機制?

我會 "刻意" 拿掉不必要的彈性 (就上面講的)，在設計階段要確定的事情我會直接寫死在 code 內來強調，當這樣的設計能夠通過所有主要情境的測試時，代表你的設計已經能正確的描述這業務領域的原則了。我放棄 "通用" 的 IAuthorization 實做: GenericAuthorization, 專為訂單管理系統設計一個授權管理機制: OrdersAuthorization


















# 3. PBAC

# 4. ABAC

# 5. Claim

# 6. ACL

# 6. 應用

audit log

login session

application definition, api scope

contrat (合約) / configuration / feature flag




<!-- 

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

### 2. 從 Database Query 層級就支援權限過濾 -->