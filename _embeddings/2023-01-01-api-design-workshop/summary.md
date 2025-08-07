# 架構師觀點 - API Design Workshop

## 摘要提示
- API First: 以規格為核心的開發流程，可同時驅動前後端、測試與文件撰寫。  
- OOP思維: 透過「物件-介面-封裝」將類別直接映射成 API Spec。  
- 狀態機: 先畫出生命週期，讓 API 操作與狀態轉移一一對應。  
- Contract First: 先確認合約正確，再進入實作以降低專案風險。  
- 安全設計: 角色、Scope、授權機制在設計階段即納入考量。  
- 行為分類: Static/Instance、影響與不影響狀態、單筆與多筆四類。  
- 事件驅動: 以 Event / Webhook 補足同步 API 難以覆蓋的需求。  
- 規格工具: OpenAPI 描述 REST 行為，AsyncAPI 描述 Event 通訊。  
- 流程驗證: 以「下棋」方式沿狀態機推演使用情境，快速驗證可行性。  
- 降級策略: 先以最小可行原型與 Mock 驗證，延後重框架與資料庫成本。  

## 全文重點
作者從「API First」與「Contract First」兩個角度切入，分享自己如何用極簡但核心的基礎功──特別是 OOP 與有限狀態機──來規劃一支真正可維運、可擴充又安全的 API。首先，以物件導向思考，先找出主體（Domain Entity）生命週期的所有狀態，再將能驅動狀態轉移的動作、不能轉移的查詢、外部可能偵聽的事件，以及參與者角色一併標在狀態圖。接著，將類別定義中的 Static/Instance Method 轉成 REST 介面的 URI；對於一次處理多筆或需要遮罩個資的操作，再另開資源路徑或 Scope，以免產生列舉攻擊。  
在流程面，API Spec 與可呼叫的 Mock 一旦確立，前端、後端、QA、技術文件與 SDK 可同步展開，縮短交付週期並提早暴露設計問題；作者更以會員註冊為例，展示如何靠狀態機沙盤推演，像玩大富翁般確認每一步皆符規則。  
安全性方面，文章示範如何將「誰」(Role) 與「能做什麼」(Scope) 抽象成 OAuth2 的權限模型，再用 ASP.NET Core 的 Middleware 與 Attribute 直接落實授權檢查。事件則以 Webhook 或 Message Bus 形式發布，並用 AsyncAPI 為外部開發者提供結構化文件。  
最後作者提醒：設計在前期應盡量「降級」——先用簡單的 Console、List、介面與單元測試驗證概念，再導入 ORM、資料庫和分散式框架，如此才能真正做到「把事情做對」與「把事情做好」。

## 段落重點
### 前言：習慣物件導向的思考方式
作者自述不迷信滿天方法論，而是依賴扎實基本功。面對任何需求，他先以 OOP 詮釋問題：找出類別、介面、狀態與動作，並把「介面先行」的思想投射到 API First。藉由類別對應 API 路徑（/api/{class}/{id}:{method}），他能把複雜設計簡化成熟悉的程式語言模型。若開發者尚未熟練 OOP，作者建議補強此基礎，因為它是開發職涯不可迴避的核心能力。

### 0. 正文開始
本段說明文章目的：延續先前演講，從 WHY 轉到 HOW，並揭示四大面向──規格優先流程、設計及標準化、先天考慮安全、避免過度設計。以 OAuth2 授權畫面為例，作者提醒 API 必須在設計階段就能讓使用者建立信任，包括傳輸安全、實作品質與可撤銷性；若自身是 API 提供者，更應藉由明確規格與品牌信譽雙重保證。

### 1. 開發流程上的改變
比較 Code First 與 Contract First。傳統作法先寫程式、再萃取 API，導致重工；Contract First 則先確立 Spec 與 Mock，使前後端、測試、文件寫作與 SDK 可並行。此作法不僅「把事情做好」（效率），更能「把事情做對」（方向）；作者以折扣計算引擎為例，示範如何用大量 Mock 與單元測試，在百餘行純 C# 內驗證抽象設計正確性，排除框架與資料庫干擾。

### 2. API Design Workshop
以會員註冊案例示範完整流程。步驟：  
2-1. 畫出狀態圖：Created→Unverified→Verified→Restricted→Banned→Deleted。  
2-2. 標記改變狀態的行為（Register、Verify、Restrict…）。  
2-3. 標記不改變狀態的查詢（Login、Get、Get-Masked…）。  
2-5. 標示角色 A~E，並將行為與身分對映，方便後續授權。  
2-6. 定義事件，分成狀態改變、動作前後兩類，決定何時發 Webhook。  
2-7. 轉成 API Spec：拆成 Entity、Action、Authorize、Event 四區，並示範 URI 命名與 Scope 列舉。  
2-8. 透過「下棋」式沙盤推演驗證使用情境，確保流程符合設計。  
2-9. 小結並談到 OpenAPI 描述 REST、AsyncAPI 描述 Event 的工具選擇，以及後續將在 ASP.NET Core 落地實作。

### （附錄）OpenAPI 與 AsyncAPI 簡介
作者引用 ChatGPT 回覆，說明 OpenAPI 適用於同步 REST，而 AsyncAPI 聚焦事件與訊息驅動系統；兩者可互補完成完整 API 文件。並簡述在 OpenAPI 中使用 Security Scheme 與 Scope 宣告的方法，以及如何在 Webhook 中附帶版本與簽章保障安全。