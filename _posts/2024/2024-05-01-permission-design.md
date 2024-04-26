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

於是，業界就發展出了一系列通用的授權管理原則，最常見的就是 RBAC (Role Based Access Control, 角色為基礎的權限控制)，另外其他還有 PBAC (P: Policy)、ABAC (A: Attribute) 等等，我就一起用同樣的模型來說明吧。實際情況下，你不大需要從頭開始設計自己的安全機制，大部分個平台的 IAM，目錄服務 (LDAP, AD) 或是 SSO 的體系 (OAuth, OpenID 等等) 都自帶對應的功能了，不過即使沒這個需要，我仍然高度建議各位 (尤其是資深人員) 花點時間練過這題目，這不但能讓你更清楚這些機制的運作邏輯，更重要的是你也才清楚如何正確的 "規劃" 你的管理方式。

<!--more-->

# 1. 定義 "權限管理" 機制是什麼?

幾乎所有 "架構面試題" 的第一步，都是先定義問題該透過什麼介面 (interface) 來處理，然後才來探討這介面背後該怎麼實作 (implement)，最後用案例或是指標，來評估成效如何。

權限機制的介面應該是什麼? 其實這件事 Microsoft 做得不錯，早在當年 .NET 1.1 的年代就已經存在的兩個介面，大概就能回答這個問題了。Microsoft 定義了這兩個介面，分別處理認證跟授權:

- IIdentity
- IPrincipal

IIdentity 告訴所有開發人員，不管你怎麼管理權限，你就是透過這個介面得知現在是 "誰" 在使用你的系統 (這就是認證的範圍)。而 IPrincipal, 則是回答你這個 "人" 被賦予什麼 "身分"，這兩個加起來，大致上就是所謂的 "認證" 了。而若這個 "身分" 可以直接對應到 "允許做什麼事" 的話，那他就是授權的源頭了。

至於 "授權"，通常有其他延伸的機制來配合，來定義這個被認證的 "人"，能夠被 "授權" (允許) 做那些事。這會牽涉到背後的授權管理機制，授權資料庫，以及判斷是否符合授權的邏輯。先不管你是怎麼被授權的，你可以用這段 code 取得目前執行你程式碼的 "身分"。如果是 console application (來源可能是 windows 整合式認證), 你可以從綁定目前執行緒的環境取得這兩個介面實作:

//

如果你是 ASP.NET MVC, 那可能是來自各式各樣 user login 機制取得的身分，這時 MVC 已經幫你處理好了，你可以這樣取得這兩個介面實作:

//


而真正執行 "授權" 的地方則更後面一點。我舉兩個例子，一個是老掉牙的 CAS ( code access security ), 只存在 .NET Framework。下面這段程式碼代表: 只有符合 "Admin" 角色的人，才能呼叫這個 Method

//

另一個，我拿比較常見的 ASP.NET MVC, 你可以直接用 AuthorizeAttribute 很方便的 "宣告" 授權行為，整套機制就會連動起來了。下面這段程式碼代表: 只有符合 "Admin" 角色的人，才能執行這個 Controller 定義的 Action

//



為了方便示範，後面的程式碼我都會這樣簡化，統一用這兩個介面為基礎, 用 console application 當作範例。分別來探討:

1. 應用程式該怎麼利用這些介面來開發功能?
1. 權限管理機制應該怎麼規劃與管理授權資訊?

在這邊，我自己做了一層抽象化，所有的權限管控問題，用一張圖就能夠說明:


// https://docs.google.com/presentation/d/1ROOGUMrVnSzYiJcUt_KPeLtjnYFxy-pcnCDDNssYtWk/edit#slide=id.g2cff021dc9b_0_0   , P2


翻成白話，就是 "授權機制" 必需不斷的回答這個問題:

> 問題: 告訴我 (某個人) 依據目前的 (權限設定) 規範，能不能夠執行 (某個功能) ?

這邊我用括號圈起來的，就是關鍵的資訊:

(某個人) -> 就是認證，通過認證的結果，你可以直接相信他就是代表真實世界的某人。通常會是某個 ID，或是 JWT。
(某個功能) -> 要做的事情，通常是應用程式的授權管理單位。例如能不能
(權限設定) -> 就是安全機制，包含設定的資料庫，也包含檢查的規則，這兩個通常是一整套的，也就是常見的 RBAC, PBAC, ABAC 等等方法。

如果把 "權限設定" 的部分抽象化成 C# interface:  IPermission, 那大概會是這個樣子:

// 
```csharp
interface IPermissionManager
{
    bool HasPermission(IPrincipal who, IAppFunction dowhat);
}
```

其實，who / dowhat 都可以極度簡化成只有一個 ID 就夠了，不過那樣會犧牲很多彈性與效率，因此我介面定義還是保留用 interface 的方式來呈現。認證部分我直接沿用 .NET 內建的 IPrincipal, 而功能我自己定一個 IAppFunction, 用介面而不用 ID，因為我希望把部分判斷的職責，歸類在認證機制 (例如確認你的身分) 來負責。適度的分攤責任，可以降低整體的複雜度。如果認證被過度簡化成只是個 ID，那麼確認身分 (角色) 就得由授權機制一起處理，那你會創造出一個很肥大的複雜機制出來..


> 所謂的 "複雜度", 我很愛用 "乘法" 跟 "加法" 來對比。
> 
> 實際情況下，如果我們最終的需求，是需要組合出 100 種可能的組態的話，你也許可以拆成 10 x 10 種規則來設計，或是 1 x 100 種規則都能達到同樣目的。
> 不過，10 x 10 的設計，你會需要開發 10 + 10 = 20 個規則來組合；
> 然而 1 x 100 的設計，你就得開發 1 + 100 個規則。
> 很明顯的就開發的複雜度來說，10 x 10 要容易的多，而在應用時你就要有能力把你的情境正確的拆解才能實現。RBAC 就是典型的這類應用，這看到後面你就理解我的用意了




實際拿例子 + 程式碼來說明會比較清楚。如果我想實作一個銷售系統，只允許主管的帳號可以查閱機密資訊 (例如業績，統計資料，每筆訂單資訊)，而操作員只能輸入資料 (已知訂單 ID 的 CRUD)，那麼這段 code 寫起來大概像這樣:

```csharp
public void QueryOrders( )
{
    var who = GetCurrentUser();
    var dowhat = GetAppFunction("query-orders");

    bool canRunAction = security.CheckPermission(who, dowhat);
    if (canRunAction == false) throw new SecurityException("no permission");

    // do something ...
}
```



如果你要用在 Web API 上面，你的 controller 大概會長這個樣子:

```csharp

[Authorization(roles = "manager")]
public void QueryOrders( )
{
    // do something ...
}

```




不過，開發 App 是後面的事情，既然訂了 interface, 應該先寫 test 才對。我打算用 unit test 來呈現，那麼寫成單元測試後，大概會是這樣:


```csharp

[TestCase]
public void Test1()
{
    var user = GetCurrentUser("andrew", new string[] {"manager"});
    var action = GetAppFunction("query-orders", "manager");

    Assert.IsTrue(security.CheckPermission(user, action));
}




```




接下來的任務就很明確了，我會在後面的章節，用同樣的方式，來說明幾種常見的權限機制運作原理 & 設計方式。大家常聽到的作法，不外乎這幾種:

- RBAC
- PBAC
- ABAC
- Claim


每一種機制，我都會擴充測試案例，說明每個情境下我預期的結果。接著我會說明結構，並且補上實作，讓單元測試都通過，來證明可行，最後 (如果有的話) 我會補充一下實際廠商或是服務提供的作法是什麼。通常，如果前面都看得懂，最後你看到這些廠商提供的 API 或是文件，大概一看就懂了。理解原理才是我期待的結果，因為安全機制不是個好懂的東西，比起寫對 code, 更難的是正確的管理。你不懂原理的話，就很難靈活的運用它來解決你的問題。

看到這邊，如果準備好了，就繼續往下看吧!








// 怎麼做 -> 權限管控要做什麼 (認證 & 授權)
// 怎麼管 -> 資料怎麼處理, 背後的定義與結構 (管理機制, RBAC / PBAC / ABAC / Claim )



# 2. RBAC

# 3. PBAC

# 4. ABAC

# 5. Claim

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