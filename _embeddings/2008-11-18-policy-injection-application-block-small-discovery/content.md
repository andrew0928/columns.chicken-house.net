因為工作的關係，最近正在研究 [Enterprise Library](http://msdn.microsoft.com/en-us/library/dd203099.aspx) 裡整合的 [Patterns & Practices](http://msdn.microsoft.com/en-us/library/ms998572.aspx) 介紹的各式 Application Block... 撇開其它的發現，有個東西一定要提一下，就是 [Policy Injection](http://msdn.microsoft.com/en-us/library/dd139982.aspx) ...

介紹文章我就不多說了，一樣網路一大堆，有興趣的可以看 [MSDN 官方的說明](http://msdn.microsoft.com/en-us/library/dd139982.aspx)。比較特別的是它的用法。當年剛開始研究 .NET 內建的 Role Based Security Control，才在讚嘆它的 code 寫起來真漂亮，只要加個 attribute, 就可以在 runtime 自動檢查呼叫時的身份是否滿足 attribute 的宣告，如下:

**CAS範例程式:**

```csharp
[PrincipalPermissionAttribute(SecurityAction.Demand, Role="Supervisor")]
public void Foo() {
    // ... 
}
```

不管你的 code 在那裡，只要呼叫這個 Foo method, 當時的身份 ( principal ) 如果不屬於 "Supervisor" 這個角色的話，就會引發 Security Exception... 當初看到這真是太棒了，我可以用宣告的方式來作安全控制，不需要在主程式裡加一堆囉哩叭唆的 code 來查權限...

不過當我開始研究如何 "自定" 這個行為，除了加上自己的安全機制之外，想更進一步的加上 Log 或是其它的檢查... 我才發現跟本辦不到。因為... 這行為是直接在 CLR 裡支援的啊，我可以加上一堆自定的 Attribute 掛上去，但是呼叫時完全不會觸發我的 code ...

之後研究過 [AOP](http://en.wikipedia.org/wiki/Aspect-oriented_programming)，發現 AOP 正是解決我這類問題的 Solution, 無奈那些 solution 都不大實際，就沒深入研究了。之後找到篇 MSDN 的文章，裡面提到 .NET Remoting 時，遠方會產生 Proxy, 同時 Client / Server 之間的溝通會介著中間傳輸層傳遞 IMessage 介面封裝的 message, 到另一端才會由 Proxy 解讀，然後用 Reflection 還原呼叫的動作... 利用 Proxy 在還原呼叫動作時，你就有機會插入你要的邏輯 (IMessageSink)，做到跟上面例子類似的功能。

還是很不實際啊啊啊啊，我沒事也不會去用 .NET Remoting 啊，用不到的話這招對我也沒啥用 (大錯特錯!! 當年的我真是太過自信了 :~~~~) ... 這事就一直擱著了，直到...

最近在研究 [Policy Injection Application Block](http://msdn.microsoft.com/en-us/library/dd139982.aspx) 時，讓我看到了似曾相識的 code:

**Policy Injection Sample Code #1**

```csharp
[AuthorizationCallHandler("operation-name")]
public void Deposit(decimal depositAmount)
{
  balance += depositAmount;
}
```

這段 CODE 跟前面 CAS 的範例作用差不多，一樣是在 method 被呼叫前作一次權限的檢查。不同的是 AuthorizationCallHandlerAttribute 是自定的 (由 Security Application Block 提供的)，它的作用比 ROLE 更進一階，是直接檢查授權的。之間的差別就如同 windows 大家都知道把 USER 加入 Administrators 角色的話，"預設" 就可以做大部份的事，但是你要在某個有 ACL 的物件 (如 NTFS 的檔案) 拒絕 Administrators 的存取也是可行的。前面 CAS 的例子就只是判定你是不是某角色的人，而這例子則是判定某個授權的定義允不允許你執行。

扯遠了，重點不在安全，重點是自定的 Code / Attribute 也可以這樣用啊! 由於我多年心裡的疑惑，挖出這段作法比研究 Policy Injection 更積極一點 (老闆對不起...) 哈哈，沒想到答案就在前文...

**它ㄨ的!! 原來只是在 Local 使用 .NET Remoting ...**

說穿了不值錢，你用的物件標上 Attribute 後，要透過它的建立方式 ( Create or Wrap ) 取得加料過的物件，再呼叫它就會有你預期的效果了。這加料過的物件，就是 System.Runtime.Remoting.Proxies.RealProxy 下的某類別啊啊啊啊... 意思是我拿這加料過的物件，就會透過 .NET Remoting 的方式去呼叫到我真正的物件，而 Policy Injection Application Block 正好就替我把我要作的動作給補上去...。

雖然心裡有被擺了一道的感覺，不過它的 code 包裝的真漂亮啊... 除了 Create 的方式由原本的 new .ctor( ) 改成它的 Create( ... ) 之外，其它就通通一樣了。更猛的是它還提供了幾個真的很實用的 CallHandler (就是呼叫時會加料的動作啦):

- Authorization Handler
- Caching Handler
- Exception Handling Handler
- Logging Handler
- Performance Counter Handler
- Validation Handler
- Custom Pipeline Handlers

大部份的 Handlers 都望文生義，像是 Logging 就是呼叫時替你加一段 LOG，而 Performance Counter 則是呼叫時就替你戳一下 windows 內建的 performance counter, 讓你可以透過 performance monitor 看相關統計 (如你的 method 被呼叫過幾次... )，更神奇的是 Caching, 如果你的 method 跑的很慢，加上去之後甚至是 cache 裡已經有了上次的結果，這次呼叫就直接 return 了... (你還記得你寫過多少次資料不在 cache 內就 insert 進去的 code 嗎?) @_@

如果你看這篇期望看到啥 [Enterprise Library / Policy Injection Application Block](http://msdn.microsoft.com/en-us/library/dd139982.aspx) 的深入介紹的話，很抱歉... 我還沒那本事，哈哈... 再過陣子研究出心得，可能會寫幾篇吧...。 這類文章如果你不介意看英文的，官方的說明還有 QuickStart 的範例就夠你看了，可以參考看看，我就不獻醜了...。 這篇純粹是為了這 AB 解除了我多年來的遺憾，特地留下篇記念用的... :D