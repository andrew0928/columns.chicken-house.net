# Policy Injection Application Block 小發現

## 摘要提示
- Enterprise Library: 作者因工作需求研究 Enterprise Library 中的 Policy Injection Application Block (PIAB)。
- 宣告式安全: 先回顧 .NET 內建 CAS/Role-Based Security 只需 Attribute 即可在執行期做權限檢查。
- 客製化困難: 內建安全機制被 CLR 固定，無法插入自訂 Log 或驗證流程。
- AOP 概念: 作者曾尋求 AOP 方案，但覺得現有工具與 .NET Remoting 實務落差大而擱置。
- PIAB 範例: 在方法前加 AuthorizationCallHandler Attribute，可於呼叫前執行授權邏輯。
- RealProxy 代理: PIAB 其實在本機利用 .NET Remoting 的 RealProxy 產生包裝物件，實現攔截。
- 建立方式: 物件必須透過 PIAB 的 Create/Wrap 產生，之後呼叫就能被攔截並附加行為。
- 內建 Handler: 提供 Authorization、Caching、Logging、Exception Handling、Performance Counter、Validation 等常用攔截器。
- 開發效益: 以宣告式方式就能新增快取或效能統計，省去大量樣板程式碼。
- 後續計畫: 作者解開多年疑惑，計畫深入研究 PIAB 並撰寫更多文章分享。

## 全文重點
作者因專案需要閱讀 Microsoft Enterprise Library，意外發現 Policy Injection Application Block 可用極簡的 Attribute 方式，於方法呼叫前後插入自訂邏輯，有效解決過去無法在 CLR 內建 Role-Based 安全檢查中追加行為的痛點。文章先回顧 .NET Code Access Security 的範例，說明透過 PrincipalPermissionAttribute 雖可檢查角色但難以擴充。為了加入自訂授權、日誌或快取機制，作者曾探索 AOP 與 .NET Remoting Proxy 技術卻覺得實務性不足，最終在 PIAB 重新看到熟悉的程式碼形態。PIAB 的核心原理是於本機動態產生 RealProxy，攔截 IMessage 後依 Pipeline 逐一執行 CallHandler，再轉送至實際目標物件。只要以 PolicyInjection.Create 或 .Wrap 建立物件，隱含的代理就能自動完成授權、快取、例外處理、效能計數與驗證等橫切需求，且對既有呼叫端語法幾乎零侵入。作者列舉各種內建 Handler 的用途，感嘆自己多年來為快取與統計寫過的大量重複程式如今只需宣告即可完成。文末說明若讀者想深入，可直接參考官方文件與 QuickStart 範例；本文主要作為作者解除多年技術疑惑的紀念。

## 段落重點
### 研究背景與動機
作者因工作接觸 Enterprise Library 的 Patterns & Practices，開始研究其中多個 Application Block；在查閱 Policy Injection 相關資料時，發現它能優雅地把橫切邏輯（安全、日誌等）透過 Attribute 宣告方式注入到方法呼叫流程中，引發強烈興趣。

### CAS 與 AOP 自訂需求瓶頸
回顧早期使用 .NET PrincipalPermissionAttribute 進行角色檢查的經驗，雖然程式碼簡潔，但無法插入額外流程；作者想以 AOP 解決卻苦於現有工具或必須依賴 .NET Remoting，覺得與日常開發脫節，因此一直未能落地。

### Policy Injection 初體驗與範例
在官方文件與範例中，作者看到 AuthorizationCallHandler Attribute 的寫法與熟悉的 CAS 很像，只要在目標方法上加上 Attribute，呼叫前就會觸發授權檢查；這證明橫切邏輯可以自訂並以宣告式方式啟用，而不受 CLR 固定限制。

### 核心原理：.NET Remoting Proxy
深入研究後發現 PIAB 背後仍然利用 System.Runtime.Remoting.Proxies.RealProxy 於本機動態建立代理；呼叫端其實透過 IMessage 管道與 Proxy 溝通，Proxy 依序執行 CallHandler Pipeline，最後再 Reflection 呼叫真實物件，達成攔截效果。

### 內建 CallHandler 功能概覽
PIAB 隨附多個常用 Handler：
1. Authorization – 細緻授權檢查  
2. Caching – 自動快取與重用結果  
3. Exception Handling – 封裝或轉譯例外  
4. Logging – 執行前後寫入 Log  
5. Performance Counter – 更新 Windows PerfMon 計數  
6. Validation – 套用 Validation Block 規則  
7. Custom – 開發者自訂 Pipeline  
這些 Handler 讓開發者省去重複樣板程式，只需宣告即可取得橫切支援。

### 心得與後續研究方向
作者感嘆多年前因缺乏工具而錯過的技巧，如今在 PIAB 已被優雅封裝；除了改變物件建立方式之外，程式幾乎不用修改即可享有攔截功能。未來將持續鑽研 PIAB 的進階用法及 Enterprise Library 其他 Block，並計畫撰文分享更深入的心得。