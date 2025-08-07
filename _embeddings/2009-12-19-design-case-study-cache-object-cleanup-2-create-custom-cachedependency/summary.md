# [設計案例] 清除Cache物件 #2 ─ Create Custom CacheDependency

## 摘要提示
- Tag 概念: 以「標籤」(tags) 方式替 Cache 物件建立多對一關聯，方便群組移除。
- CacheDependency: 自訂 TaggingCacheDependency 繼承自 .NET 的 CacheDependency，負責監控與通知失效。
- Dictionary 管理: 以靜態 Dictionary< string, List< TaggingCacheDependency > > 維護 tag 與依附物件的對應表。
- 群組失效: 呼叫 DependencyDispose(tag) 即可一次讓所有帶有該 tag 的 Cache item 強制過期。
- 範例應用: 下載 50 個網址資料並快取，依 host/scheme 為 tag，示範「funp.com」一聲令下全部移除。
- Callback 監聽: 透過 CacheItemRemovedCallback 回報被移除的 key 與理由，方便除錯。
- 易於擴充: 同樣思路可針對業務需求另行設計其他型別的 CacheDependency。
- 相對優勢: 省去逐一持有 Cache Key 並呼叫 Cache.Remove 的繁瑣流程，提高維護與效能。
- 範例完整: 內附 URL 測試清單與 Visual Studio 2008 專案供讀者下載練習。
- 實務意義: 適用 Web/Service 大量快取資料但需一次性更新的情境，例如新聞站、電商促銷等。

## 全文重點
本文延續前篇「清除 Cache 物件」主題，示範如何利用 .NET CacheDependency 自訂機制，透過「tags」同時綁定多筆 Cache item，並於需要時一次性使其失效。作者首先藉 50 筆網址資料的下載範例說明傳統做法的侷限：必須保留所有 Cache Key，逐一呼叫 Cache.Remove，流程冗長且難以維護。為解決此痛點，文中實作 TaggingCacheDependency 類別，繼承自 CacheDependency，並以靜態 Dictionary 保存「tag → 依附物件清單」。物件放入 Cache 時直接在建構子傳入多組 tag，系統即自動將 Cache item 與 TaggingCacheDependency 關聯。當資料來源（如網站 host）需要更新時，只須在任一位置呼叫 TaggingCacheDependency.DependencyDispose(tag)，類別內部會遍歷對應清單，透過 NotifyDependencyChanged 觸發 .NET 快取框架，將所有相關項目標記為過期並自動從 Cache 移除；若有設定回呼，即可同步列印被移除項目供觀察。整體程式不足 30 行便達成群組式快取控制，具備簡潔、低耦合、可重用三大優點。最後作者提醒讀者，除 tag 方式外，亦可依不同業務需求衍生其他自訂 CacheDependency 實作；文末並提供完整範例專案與測試 URL 供下載練習。

## 段落重點
### 前言：從逐一移除到群組失效
作者回顧前篇討論的「拿著 Cache Key 一個一個移除」困擾，指出在實際專案中經常需要一次刷新相同來源或類型的大批快取資料，因此提出「用 tag 對應一組 Cache item，並透過 CacheDependency 機制讓其自動失效」的構想，期望提升效率與可維護性。

### 範例程式：50 個網址下載與快取
示範程式準備 50 筆 URL 清單，逐一呼叫 DownloadData。該方法先嘗試從 HttpRuntime.Cache 取值，若未命中就下載並快取；放入 Cache 時建構 TaggingCacheDependency，把 sourceURL.Host、sourceURL.Scheme 兩段字串作為 tag。主程式最後分別按 Enter 停止與呼叫 DependencyDispose("funp.com")，並透過 Info callback 觀察哪些項目被移除，可見帶有 funp.com 的網址全部過期。

### TaggingCacheDependency 實作解析
核心類別不足 30 行。建構子逐一掃描傳入 tags：若 Dictionary 尚無該鍵即建立新 List，再把自身加入。為符合 CacheDependency 初始化流程，最後呼叫 SetUtcLastModified 與 FinishInit。靜態方法 DependencyDispose(tag) 先檢查 Dictionary 是否含該鍵，若有則走訪 List，對每個實例呼叫 NotifyDependencyChanged 通知 .NET 快取系統，完成後清空並移除該鍵，確保記憶體整潔。

### 實際呼叫：加入 Cache 與集中失效
放入 Cache 的程式碼行包含：key、value、TaggingCacheDependency、Absolute/Sliding Expiration、Priority 與 Callback 等標準參數。若需集中失效，只要在任何程式區塊呼叫 TaggingCacheDependency.DependencyDispose(tag) 即可，範例中對 "funp.com" 執行後相關下載資料立即清空，相較逐 Key 移除省時且不易遺漏。

### 結語與下載資源
作者強調 tag 只是其中一種設計，可依業務維度（例：商品分類、會員群組）自由擴充，自訂 CacheDependency 不但簡化程式，也提升大規模快取應用的可靠度。文末提供測試用 URL 清單與 Visual Studio 2008 範例專案，鼓勵讀者實際下載操練，加深對 .NET 快取機制與自訂依賴的理解。