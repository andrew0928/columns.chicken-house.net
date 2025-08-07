# API & SDK Design #3：API 的向前相容機制

## 摘要提示
- 向前相容: 透過「只增不減」原則確保新 API 能服務舊版 SDK。  
- 版本策略: 採 Compatible Versioning，僅保留最新 API，並保證相容。  
- Contract 管控: 以 Interface + ActionFilter 檢查，讓 API 介面異動可追蹤。  
- 版本編碼: 沿用 Microsoft four‐part version (Major.Minor.Build.Revision)。  
- SDK 驗證: SDK 在初始化階段比對自身需求與 API 版本，避免不相容呼叫。  
- HTTP 標頭: 以 X-SDK-REQUIRED-VERSION 傳遞 SDK 需求至 Server 端。  
- Server 檢查: 以 ActionFilter 於 Runtime 驗證版本並回傳適當錯誤。  
- 測試與自動化: 善用 Unit Test、CI 及 AssemblyInfo 來維持版本一致性。  
- 優化考量: 高頻 API 需快取與優化，減少 Runtime 反射成本。  
- 長期營運: 宣告棄用流程與 Obsolete 標示，為下一版重大變動鋪路。  

## 全文重點
本文延續前篇，聚焦「API 向前相容」議題。作者採用 Compatible Versioning 策略：Server 端僅維持最新 API，但必須保證所有過去發行的 SDK 均可繼續呼叫。為達成此目標，他提出三大檢查點：  
1. API Contracts：先以 interface 描述可對外公開的方法，並用 ActionFilter 於執行時反射檢查，確保 controller 只暴露合約中的成員；同時保留 Data Contract 檢查。  
2. 明確版本識別：採四段式版本號，Major 不相容、Minor 向前相容，Build/Revision 視團隊流程而定。SDK 以程式碼寫死最低需求版本，而 API 透過 AssemblyInfo 或 Options 方法回報實際版本。  
3. 相容性政策：SDK 在初始化或每次呼叫時，比對自身需求與 API 版本；若 Major 不同或 Minor 不足即丟例外。對高存活期的 SDK，再以 HTTP Header（X-SDK-REQUIRED-VERSION）附帶版本資訊，由 Server 端 ActionFilter 檢查。  

文中提供完整 C# 範例，示範 Interface、ActionFilter、AssemblyVersion、HttpClient Header 設定與例外處理流程，並說明如何用 Unit Test 與 CI 工具持續監控 contract 變動。作者強調向前相容是 API 長期營運的關鍵，唯有嚴格控管合約、版本與棄用流程，才能避免「You shall not pass」災難。下一篇將探討在此基礎上進行 SDK 最佳化與 API 升級的實戰演練。

## 段落重點
### 碎碎念：API 的版本策略（約 500 字）
作者首先界定 API 版本管理的三種模式：無版本、點對點多版本並存、與 Compatible Versioning。為降低維護成本並保有開發者信任，他選擇第三種策略：Server 僅保留一版，但每次升級都必須保證向前相容。這種作法帶來嚴苛的設計挑戰：發佈後就不能刪減或改變 signature，因此需建立嚴格流程避免誤改。為此他提出三大檢查點：API contract 控管、版本識別機制與相容性策略，三者相互依存；若 contract 有異動，必須同步調整版本號，並透過 SDK 檢查規避不相容呼叫；同時要為不可避免的棄用行為訂定公告與寬限期。

### API Contracts（約 500 字）
在 ASP.NET Web API 缺乏如 WCF 自帶 Contract 機制之下，作者以 interface + ActionFilter 建立執行時檢查。首先定義 IApiContract 作為標記，再為每支 controller 寫專屬合約 interface，例如 IBirdsApiContract；controller 同時實作該 interface 並套上 ContractCheckActionFilter。Filter 在每次呼叫前反射比對 controller action 是否名列 contract，若缺漏即丟 NotSupportedException。此方法雖於 Run-time 檢查成本較高，但搭配快取與 Unit Test 可大幅降低風險。若系統呼叫量極大，亦可僅針對 Data Contract 施行，或藉文件與 Code Review 補強。

### API / SDK Versioning（約 500 字）
本段分兩部分：  
1. 版本編號意義：沿用 Major.Minor.Build.Revision 規則。Major 差異代表不相容；Minor 差異為可向前相容的擴充；Build 與 Revision 通常反映重新編譯或修補，不影響合約。當 contract 擴充但未破壞相容性，只增 Minor；若有破壞性變更則增 Major，舊 API 保留並標註 Obsolete。  
2. 呈現方式：a. 實作 Options API 讓 SDK 明確查詢版本；b. 將版本附在一般回傳包或 Header 中。範例中 controller 實作 Options 回傳「10.26.0.0」，SDK 於初始化呼叫並比對，若 Major 不同或 Minor 不足即拋 InvalidOperationException。版本字串亦可改從 AssemblyInfo 注入，利於 CI 產生一致 Build 與 Revision。

### 版本相容性政策（SDK init 時檢查）（約 500 字）
此段示範 SDK 在建立 Client 物件時自動取得 Server 版本，並以硬碼的 _require_API_version 進行判斷。規則簡單：Major 必須相等；Minor 必須大於等於需求值；Build/Revision 不檢查。若不符即拋例外，Caller 可依需求提示更新或降版。作者以修改 Server 版本為 12.x 範例，展示 SDK 於初始化即終止，避免後續錯誤呼叫。此模式適用於 SDK 生命週期短、每次建立都可重新驗證的情境。

### 版本相容性政策（呼叫 API 時檢查）（約 500 字）
若 SDK 可能長期存活（靜態單例、IoC 容器等），單次初始化驗證不足。作者改在每次 HTTP 呼叫加上 Header「X-SDK-REQUIRED-VERSION」，內容為 SDK 最低需求版號，並於 Server 端掛 SDKVersionCheckActionFilter：  
1. 解析 Header 中需求版號；2. 讀取 Assembly 版號；3. 判斷 Major 必須相等且 Minor≥需求；否則拋 InvalidOperationException。好處是檢查發生於 API 執行前，可依條件回傳客製錯誤或進行降級邏輯。範例展示當 SDK 要求 12.11 時，Server 立即拒絕並透過 Web API 錯誤格式回傳 JSON 例外訊息，SDK 端亦能捕捉並進一步解析。

### 結語（約 500 字）
文章總結：向前相容是 API 長期營運的命脈。唯有在 Contract、Version 與 Policy 三層同時上鎖，才能避免升級導致「You shall not pass」。實務上需配合 CI/CD、自動化測試及審核流程，將檢查點嵌入日常開發，並在重大變動前以 Obsolete、公告與 Sunset 機制給開發者緩衝。作者預告下一篇將聚焦 SDK 最佳化與 API 升級實戰，並於 GitHub dev-VER 分支提供全文範例程式碼，方便讀者追蹤與演練。