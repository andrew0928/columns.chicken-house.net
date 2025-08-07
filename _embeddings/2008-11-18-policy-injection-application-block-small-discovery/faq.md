# Policy Injection Application Block 小發現...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Policy Injection Application Block（PIAB）？
Policy Injection Application Block 是 Microsoft Enterprise Library 中的一個應用程式區塊。透過在方法上套用 Attribute，再以 PolicyInjection.Create 或 Wrap 方式產生物件，PIAB 會在方法被呼叫前後自動插入（Inject）額外的行為，例如權限檢查、快取、例外處理、記錄 (Log) 等，讓開發者用宣告式的方式即可為既有程式加入橫切面（AOP）功能。

## Q: 它和 .NET 內建的 Role Based Security（PrincipalPermissionAttribute）最大的差異是什麼？
內建的 Role Based Security 完全由 CLR 支援，只能判斷呼叫端是否屬於指定角色，且行為無法被自訂；開發者就算再寫自己的 Attribute 也不會被執行。  
PIAB 則可套用**自訂**或內建的 CallHandler，除了做角色／授權檢查外，還能加入快取、例外處理、記錄、效能計數等多種行為，且可自行擴充。

## Q: 為什麼自訂的 Attribute 無法像 PrincipalPermissionAttribute 一樣被 CLR 觸發？
因為 Role Based Security 的判斷邏輯是寫死在 CLR 內部，只有 CLR 所認得的幾個安全性 Attribute（例如 PrincipalPermissionAttribute）會在執行時被解析並觸發安全性 Demand，自訂 Attribute 不在其列，自然不會被執行。

## Q: PIAB 背後是用什麼技術攔截方法呼叫的？
PIAB 在本機利用 .NET Remoting 的 System.Runtime.Remoting.Proxies.RealProxy 產生 Proxy 物件。當程式呼叫 Proxy 的方法時，實際上會先經過一連串 CallHandler，再轉送到真實物件，達到攔截與加料（Injection）的效果。

## Q: 使用 PIAB 時，如何取得能被攔截的「加料」物件？
不要直接 new 物件，而是使用  
```csharp
var obj = PolicyInjection.Create<Foo>();
```  
或是  
```csharp
var obj = PolicyInjection.Wrap<Foo>(realFoo);
```  
取得的 obj 其實是一個 RealProxy 產生的代理物件，呼叫其方法才會經過設定好的 CallHandler。

## Q: PIAB 內建提供了哪些常用的 CallHandler？
1. Authorization Handler  
2. Caching Handler  
3. Exception Handling Handler  
4. Logging Handler  
5. Performance Counter Handler  
6. Validation Handler  
7. 以及可自行實作的 Custom Pipeline Handler

## Q: Caching Handler 可以帶來什麼效益？
若方法執行時間較長且結果可被重複使用，Caching Handler 會在第一次呼叫後把結果存入快取；之後相同輸入值的呼叫便直接回傳快取結果，不再真正執行方法，顯著提升效能並減少資源消耗。