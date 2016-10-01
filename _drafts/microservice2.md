---
layout: post
title: "微服務架構 #2, 按照架構，重構系統"
categories:
- "專欄"
- "系列文章: .NET + Windows Container, 微服務架構設計"
tags: []
published: true
comments: true
# redirect_from:
logo: 
---

上一篇說明了微服務架構的好處，這篇來談談該如何做。其實說穿了很簡單，不就把大型的單體式
應用程式，拆成幾個獨立的服務不就行了? 這樣講沒錯，不過關鍵就在於你這刀應該往哪邊切下去
才洽當? 切出來的服務能不能再繼續切? 有沒有哪些服務是切過頭的，需要重新合併成一個大的?

其實軟體開發的觀念，說穿了都很類似。當你的程式碼架構良好的時候，不僅 code 維護容易，要切割
出獨立的服務也會相對輕鬆。因此，不論你打算做甚麼架構調整，我通常會做的第一步就是 "程式碼重構" !!

# 程式碼重構 - 一定要做的事

重構的技巧，很多大師都說過了，應該也輪不到我來獻醜 XD，不過我這邊要講的不是技巧，而是你可以先
想清楚你現在做 *重構* 的目的是什麼?

舉個例子，如果後面會講到的重點你都掌握到了，你也許現在就能預想之後有哪些模組要變成服務切割出去，
那麼你現在重構的目標就很明確。沒有抓清楚目標的話，你的重構可能就是漫無目的地進行，盲目的 code review，
哪裡看不順眼就改一改.. 這樣是沒有幫助的，你只能做局部的最佳化，但是對整體架構而言沒有任何助益。

以我自己的習慣，我會這樣做。先構思我想要切割的服務有哪些，在那之前先把這些服務的邊界定義出來，然後
我重構的目的，就是將這些即將會被拆出來的服務，用 design pattern 裡提到的 Proxy 去改造他。只要我的
系統用到這模組，都會透過 Proxy 來進行的話，那將來這模組切出來變成獨立服務時，我只要改寫 Proxy 就可
以達成目標了。甚至是在切割出去的過程中，我可以不斷的用單元測試，或是同時使用兩種版本的技巧 (註)，隨時
確認我的動作沒有問題。

這樣講有點抽象，我寫一小段 code 來說明我的想法好了。就舉最常見的會員系統為例。大部分的系統，總是要
有個會員管理吧? 於是，你的系統可能到處都會出現這樣的 code:

```C#
        // your application code here...
        public void LoginCheck()
        {
            // user login, and get login token
            LoginToken token = this.UserLogin(
                "andrew",
                this.ComputePasswordHash("1234567890"));

            if (token == null)
            {
                // do something when login failure...
            }
            else
            {
                // login success.
                // ...
            }
        }


        private string ComputePasswordHash(string password)
        {
            // 
            return null;
        }

        public LoginToken UserLogin(string userid, string pwdhash)
        {
            // query membership database ...
            return null;
        }


        public class LoginToken
        {
            // token 的類別定義
        }

```

其實很多系統，一開始發展時並不重視架構，老闆可能認為 time to market 最重要，programmer 自然而然
就寫出這樣的 code 也不足為奇。但是若這套系統要持續發展，這些欠下的技術債總是要逐步償還的。若公司發展
下去，提供的服務變多了之後，架構師或是技術主管，自然會希望把會員機制切出來，在多套系統之間重複使用。
通常架構的演變都會按照這樣順序發展:

1. 只有一套系統使用會員機制時:  
會員機制直接藏在你的 application 內 (如上述 example code)。

2. 有幾套系統 (N < 5) 共用會員機制時:  
會將會員模組函式庫標準化 + 共用會員資料庫。

3. 更多服務共用會員機制時:  
會將會員機制獨立成專屬的服務，會員服務有自己的 service, 有自己的 database, 也會定義標準的 API，供
其他服務來使用會員機制。

# 重構目標: 模組化

上述的例子，大概就是停留在 (1) 的程度而已。若要進展到 (2), 其實要做的就是會員機制程式碼的重構。各種
架構上的原則都可以套用上來，例如這個模組要高內聚(對模組內)與低偶合(對其他模組)，單一責任原則，封閉開放
原則等等。我這邊假設架構師眼光夠遠，在為了 (2) 準備重構時，也顧慮到 (3) 的可能性。不需要在這時做過多
的預先準備，只要確保目前的決策是能延續到 (3) 來到的那天，不用到時得整個打掉重練。

這時重構的原則，我會把 "低偶合" 當作第一優先，同時我會採用 Factory + Proxy 設計模式，做好將來要擴展
到 (3) 的準備。上述的 code, 經過調整後，大概會長的像這樣:

系統主程式:
```C#
        public void LoginCheck()
        {
            LoginServiceBase lsb = LoginServiceBase.Create();

            // user login, and get login token
            LoginToken token = lsb.UserLogin("andrew", "1234567890");

            if (token == null)
            {
                // do something when login failure...
            }
            else
            {
                // login success.
                // ...
            }
        }
```

登入機制 library:
```C#
    public abstract class LoginServiceBase
    {
        public static LoginServiceBase Create()
        {
            // 目前只有 local database 的會員機制實作。預留將來擴充其他的登入機制，先在這邊
            // 採用 Factory Pattern.
            return new LocalDatabaseService();
        }

        protected string ComputePasswordHash(string password)
        {
            // 傳回 password 的 hash value, 做驗證用途。hash 的方式應該包括在 API 規格內，不應隨意更動
        }

        public virtual LoginToken UserLogin(string userid, string password)
        {
            string hash = this.ComputePasswordHash(password);
            if (this.VerifyPassword(userid, hash))
            {
                // 密碼驗證成功，應傳回正確的 login token
                return new LoginToken();
            }
            else
            {
                // 密碼驗證失敗
                return null;
            }
        }

        protected abstract bool VerifyPassword(string userid, string passwordHash);
    }


    public class LocalDatabaseService : LoginServiceBase
    {
        internal LocalDatabaseService()
        {

        }

        protected override bool VerifyPassword(string userid, string passwordHash)
        {
            // 查詢會員資料庫，確認 userid 與 password hash 的內容正確。
        }
    }


    public class LoginToken
    {
        // token 的類別定義
    }

```

這樣改變有幾個目的，第一就是引入 Factory 這設計模式。在可見的未來，架構師已經預期到會員資料庫總有獨立的
一天，因此現在先用 Factory 的方式，把取得對應的服務模組的過程抽離出來，交給 Factory 負責。另一個目的，
是將所有登入機制的相關邏輯，都集中到獨立的 DLL 內。DLL 內都是處理登入相關的動作，屬高內聚力的部分。而對
於需要呼叫登入機制的系統，則只能透過 LoginServiceBase 定義的抽象介面來使用，其他管道一律不准。這是透過
abstract class 實作出來的低耦合的設計。這部分在之後也會進一步演化成 interface 與 API 的定義。

實作到這個地方，基本上 (2) 的需求已經滿足了，同時這個架構將來也足以延伸到 (3) 的需求，同時目前也還不用
投入人力去為了 (3) 提供任何的實作。這樣也算是做到開放封閉原則了 - 對修改封閉，對擴充開放。


# 重構目標: 服務化

若公司的業務持續擴大，(3) 的需求已經需要去滿足他的一天到來，那麼這系統會如何進化? 首先，我們一定要有一個
獨立的會員服務，將所有會員機制相關的 server side code, 還有會員資料庫，都集中到這個服務身上。我就簡單的
用 ASP.NET MVC 的 webapi 來當作範例。我這邊省略一切我沒有要討論的實作細節，只針對重點的部分貼出 code, 
對應帳號密碼驗證的 api controller 應該長這樣:

```C#
using System;
using System.Net.Http.Formatting;
using System.Web.Http;

namespace WebApplication1.Controllers
{
    public class LoginController : ApiController
    {
        public string UserLogin(FormDataCollection parameters)
        {
            string userid = parameters["userid"];
            string passwordHash = parameters["passwordhash"];

            // validate userid + passwordHash
            // generate and return login token text
            
            return Guid.NewGuid().ToString("N");
        }

        // todo: 其他支援的 webapi here...
    }
}
```

雖然 ASP.NET MVC webapi 是跟平台無關的規格，任何平台都可以輕易的呼叫使用，不過每個平台都要自己去些一些 HTTP 
處理相關的 code 也是挺辛苦的，通常前端我會搭配開發一組 SDK，來簡化使用 API 的門檻。其實很多例子都這樣做，例如
Flickr 有很清楚的 HTTP API doc, 但是它也提供了 Flickr.Net, 包裝成 .net 原生的 class library 簡化你使用的步驟，
這就是 SDK 存在的目的。

對應我們改善後的 SDK (其實就是從上個例子的 class library 進化而來的)，code 長的會像這樣:

```C#
    public class RemoteLoginService : LoginServiceBase
    {
        private readonly Uri serviceBaseUri = null;
        internal RemoteLoginService(Uri serviceUri)
        {
            this.serviceBaseUri = serviceUri;
        }
        public override LoginToken UserLogin(string userid, string password)
        {
            using (var client = new HttpClient())
            {
                client.BaseAddress = this.serviceBaseUri;
                var content = new FormUrlEncodedContent(new[]
                {
                    new KeyValuePair<string, string>("userid", userid),
                    new KeyValuePair<string, string>("passwordHash", this.ComputePasswordHash(password))
                });
                var result = client.PostAsync("/api/login", content).Result;
                string resultContent = result.Content.ReadAsStringAsync().Result;
                return new LoginToken(resultContent);
            }
        }


        protected override bool VerifyPassword(string userid, string passwordHash)
        {
            // 不支援，這動作直接隱含在 server side api 內執行
            throw new NotSupportedException();
        }
    }
```

然而，這樣的改變，需要調整一下 Factory 的部分。其實只要改一行就好了:
```C#
    public abstract class LoginServiceBase
    {
        public static LoginServiceBase Create()
        {
            //return new LocalDatabaseService();
            return new RemoteLoginService(new Uri("http://localhost:50000"));
        }
        // ...
```

最後，真正要呼叫這些服務的 code, 完全不用改, 維持原樣，重新編譯 & 更新 SDK 後就能正常執行:
```C#
        public void LoginCheck()
        {
            LoginServiceBase lsb = LoginServiceBase.Create();

            // user login, and get login token
            LoginToken token = lsb.UserLogin("andrew", "1234567890");

            if (token == null)
            {
                // do something when login failure...
            }
            else
            {
                // login success.
                // ...
            }
        }
```

# 重構的技巧: 雙重驗證





# 總結: 切割為為服務的實作案例

NEXT: 怎麼決定要將那些模組，切割為獨立服務?


















# 按照業務流程切割服務



# 原則 1: 高內聚 + 低偶合

















# 拆解單體式系統

## 找出合適的模組邊界

## 圍繞著業務概念去塑模
## 自動化
## 封裝 - 隱藏內部細節
## 去中央化
## 可獨立部署
## 隔離失敗
## 高度可觀察

## Anti-Patterns: 何時不該用微服務?

## 拆解的目的

## 相依性

## 資料庫

## 交易邊界





# 部署

## 目標: 持續整合

## 目標: 持續交付

## IMMUTABLE SERVER

## 服務組態

## 服務與主機對應



# 測試

# 監控

# 資安