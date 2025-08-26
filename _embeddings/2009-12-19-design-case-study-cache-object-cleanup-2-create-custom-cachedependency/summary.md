# [設計案例] 清除Cache物件 #2. Create Custom CacheDependency

## 摘要提示
- CacheDependency: 透過自訂 CacheDependency 機制，統一讓一組 cache item 同步失效而不需逐一以 key 移除。
- Tagging: 以 tags 的概念標註 cache item，達成以「標籤」為單位的快取管理與清除。
- 範例場景: 針對 50 組網址下載資料並快取，後續可一鍵使特定網域的快取失效。
- 實作結構: 使用靜態 Dictionary<string, List<TaggingCacheDependency>> 維護 tag 與依賴物件對應。
- 失效觸發: 呼叫 DependencyDispose(tag) 會針對該 tag 相關的依賴逐一通知失效。
- 使用方式: Cache.Add 時以 new TaggingCacheDependency(tags...) 指定多個 tag（例：Host、Scheme）。
- 回呼驗證: 設定 CacheItemRemoved 回呼，觀察被移除的 cache key 與原因以驗證效果。
- 優點: 不需記錄或搜尋所有 key，即可快速清空同一類型或同來源的快取資料。
- 擴充彈性: tag 可自訂多種維度（如網域、協定、類別），也能延伸為其他 Domain-specific 依賴。
- 附件資源: 提供 URL 清單與 VS2008 專案供讀者下載與實測。

## 全文重點
本文延續清除 Cache 的系列主題，提出以自訂 CacheDependency 實作「標籤化」的快取管理。核心思路是讓每個放入快取的物件都綁上一或多個 tag，日後只要針對某個 tag 發出失效指令，與之綁定的 cache items 就會被統一移除，不需要再逐一掌握或搜尋 cache key，簡化清除流程並降低維護負擔。

範例程式模擬一次性下載 50 個網址資料並存入快取。每筆快取的 key 為完整 URL 字串，並在加入快取時建立 TaggingCacheDependency，使用 URL 的 Host 與 Scheme 作為標籤。如此一來，當需要清空某一來源（例如特定網域 funp.com）的所有快取時，只要呼叫 TaggingCacheDependency.DependencyDispose("funp.com")，即可讓該網域相關的快取在同一時間失效。為了驗證效果，程式也設定了移除回呼，將被移除的 key 印出，可清楚看到全部來自 funp.com 的項目被清除。

TaggingCacheDependency 的實作相當精簡：繼承 CacheDependency，內部以靜態 Dictionary<string, List<TaggingCacheDependency>> 維護「tag → 依賴物件清單」的映射。建構時將自己註冊到每個對應 tag 清單中；當外部呼叫 DependencyDispose(tag) 時，迴圈逐一對清單中的依賴呼叫 NotifyDependencyChanged，即可觸發快取框架將相依的 cache items 視為已變更而予以移除。最後清空並移除該 tag 的清單，避免重複通知。

使用方式簡單直觀：在 Cache.Add 時以 new TaggingCacheDependency(host, scheme) 之類的方式賦予多個 tag；需要清除時，直接以 tag 為單位呼叫 DependencyDispose。此設計的好處是把移除條件抽象成業務上有意義的分類或維度（如網域、協定、類型、租戶、語系等），不必耦合到零碎且難管理的 key。此外，這種模式也易於擴展：可替換或新增不同的標籤策略，甚至在現有架構上再包裝更複雜的失效規則。

文章最後提供了 URL 清單與 VS2008 範例專案，方便讀者直接下載測試。整體來說，這個自訂 CacheDependency 的方法以極少的程式碼，就實現了可控、可讀、可擴充的快取批次失效機制，特別適合需要按來源或分類快速清空快取的情境。

## 段落重點
### 透過 tags 來控制 cache items 的範例程式
作者以下載 50 組網址為例，將下載結果存入 ASP.NET Cache。加入快取前先檢查是否已有資料；若無才進行下載（下載細節略）。每筆快取在 Cache.Add 時，建立 TaggingCacheDependency，並以 URL 的 Host 與 Scheme 作為標籤，形成「同網域、同協定」的分組。主程式最後呼叫 TaggingCacheDependency.DependencyDispose("funp.com")，預期讓所有來自 funp.com 的快取項目同時過期。程式亦設定 CacheItemRemoved 的回呼方法 Info，以便在控制台輸出被移除的 key 與原因，直觀驗證清除效果。執行結果顯示，確實只有 funp.com 來源的快取被移除，證明以 tag 為單位操作快取失效的可行性與便利性。

### TaggingCacheDependency 的實作
自訂類別 TaggingCacheDependency 繼承自 CacheDependency，並以一個靜態 Dictionary<string, List<TaggingCacheDependency>> 維護標籤到依賴實例的對應關係。建構子接收可變參數的多個 tag：逐一檢查並新增清單，然後將自身加入對應的 List；最後調用 SetUtcLastModified 與 FinishInit 完成初始化。核心 API DependencyDispose(tag) 用來「下令」讓特定標籤的依賴全部觸發失效：若字典包含該 tag，便迴圈對每個依賴呼叫 NotifyDependencyChanged，觸發快取機制將相關快取項目視為已變更並移除，最後清空與移除該 tag 的清單。整體不到 30 行，邏輯直接、耦合度低，充分利用 CacheDependency 既有的通知機制達成群組化失效。

### 把物件加進 Cache, 配上 TaggingCacheDependency ...
使用方式上，當呼叫 HttpRuntime.Cache.Add 時，將第三個參數設為 new TaggingCacheDependency(sourceURL.Host, sourceURL.Scheme) 即可一次賦予多個標籤。這讓快取項目與多個維度的分類建立鬆耦合的關聯：未來無論要依「網域」或「協定」進行清除，都能透過相同的 DependencyDispose 介面完成，不再受限於 key 名稱或搜尋規則。此模式有助於將快取策略與業務語意對齊，例如以租戶、功能模組、資料類別或語系為 tag，讓清除行為更符合實際維護需求，也降低日後重構或調整 key 命名所帶來的成本與風險。

### 將標為 "funp.com" 的 cache item 設為失效的 cache item
要讓所有標記為 "funp.com" 的快取項目失效，只需呼叫 TaggingCacheDependency.DependencyDispose("funp.com")。這行指令會喚起對應 tag 的所有依賴物件，進而通知快取框架將其相依的快取資料移除。從示範輸出可見，被移除的項目皆來自 funp.com，達成以單一條件快速批次清除的目的。與傳統遍歷 key 或維護大量 key 名單相比，這種做法顯著簡化操作與邏輯，且可輕鬆擴充更多 tag 維度，形成可重複使用且具可讀性的快取失效策略。文末並提供 URL 清單與 VS2008 範例專案，方便讀者下載測試與延伸應用。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C# 與 .NET Framework 基礎（class、static、集合、委派/事件）
   - ASP.NET/HttpRuntime Cache 基本操作（新增、移除、過期策略）
   - System.Web.Caching.CacheDependency 概念與生命週期

2. 核心概念：
   - CacheDependency：以依賴關係驅動的快取失效機制
   - Tagging 概念：以一個或多個 tag 將多個 cache items 分群管理
   - 自訂 CacheDependency：以自訂類別集中管理依賴，主動觸發失效
   - 集中失效通知：透過 DependencyDispose(tag) 讓同群項目一鍵失效
   - Cache callback：移除回呼（CacheItemRemovedCallback）協助記錄/補償

   關係：自訂 CacheDependency 以 Tagging 方式建立 Cache 與 Tag 的關聯，當集中失效通知發生時，透過 CacheDependency 的通知機制使該 Tag 所屬的所有 Cache Items 同步失效，並透過 callback 進行後續處置。

3. 技術依賴：
   - System.Web.Caching.Cache 與 HttpRuntime.Cache
   - System.Web.Caching.CacheDependency 的衍生與覆寫（SetUtcLastModified、FinishInit、NotifyDependencyChanged）
   - .NET 集合（Dictionary<string, List<TaggingCacheDependency>>）
   - 委派/事件機制與回呼（CacheItemRemovedCallback）

4. 應用場景：
   - 以網域/主機名為單位的快取群組失效（例如同一 Host 的下載結果）
   - 功能模組或租戶（tenant）級別的快取失效
   - 依資源類型（scheme、API 版本、資料分類）群組化的快取管理
   - 後台任務或發佈流程一鍵清除某類快取

### 學習路徑建議
1. 入門者路徑：
   - 了解 Cache 的基本操作（新增、取得、移除、到期時間）
   - 認識 CacheDependency 的用途與基本範例（檔案/Key 依賴）
   - 練習加入 CacheItemRemovedCallback 觀察移除時機

2. 進階者路徑：
   - 實作自訂 CacheDependency：覆寫初始化與通知方法
   - 設計以 Tag 分群的快取策略（單一/多重 tag）
   - 加入執行緒安全與記憶體管理（鎖定、弱參考、清理）

3. 實戰路徑：
   - 將現有系統中依 Key 移除的流程改為基於 Tag 的群組失效
   - 設計集中化的清除介面（DependencyDispose/多條件清除）
   - 監控快取命中率與清除影響，調整過期策略與群組粒度

### 關鍵要點清單
- CacheDependency 基礎：以依賴關係驅動快取失效的官方機制，能避免逐一以 Key 移除的麻煩 (優先級: 高)
- Tagging 思維：用一個或多個 tag 將多筆快取資料分群，便於一次性清理 (優先級: 高)
- 自訂 CacheDependency 類別：繼承 CacheDependency，包裝自定義的群組失效邏輯 (優先級: 高)
- NotifyDependencyChanged：關鍵 API，用於主動通知快取該依賴已變更，觸發失效 (優先級: 高)
- FinishInit 與 SetUtcLastModified：自訂依賴初始化流程需正確呼叫，確保依賴狀態一致 (優先級: 中)
- 靜態字典管理：以 Dictionary<string, List<TaggingCacheDependency>> 維護 tag 與依賴實例的對應 (優先級: 高)
- 多重標籤支持：在建構子中接受 params string[] tags，使同一快取項可屬於多個群組 (優先級: 中)
- 集中清除介面：DependencyDispose(tag) 提供一鍵清除該 tag 關聯快取的能力 (優先級: 高)
- CacheItemRemovedCallback：在移除時記錄與後續補償（重新預熱、觀測行為） (優先級: 中)
- 使用情境設計：以 Host、Scheme、資料分類、租戶等作為 tag 以因應不同清除需求 (優先級: 中)
- 執行緒安全：靜態集合操作應加鎖避免競態條件與不一致（範例未實作，實務必加） (優先級: 高)
- 記憶體管理：注意 List 暫存依賴實例的生命週期，清理/移除避免洩漏 (優先級: 高)
- 多應用程式域/多台伺服器：此作法僅限單一 AppDomain，分散式需外部訊號（如 Redis、MSDTC、訊息匯流排） (優先級: 中)
- 優先級與到期策略：搭配 CacheItemPriority、Absolute/Sliding Expiration 以取得最佳命中與更新時機 (優先級: 中)
- 可觀測性：加入日誌/度量以衡量清除頻率、命中率與效能影響 (優先級: 低)