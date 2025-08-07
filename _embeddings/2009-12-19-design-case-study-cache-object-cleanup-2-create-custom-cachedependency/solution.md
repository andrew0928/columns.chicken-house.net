# 清除 Cache 物件 – 自訂 CacheDependency 與 Tagging 機制

# 問題／解決方案 (Problem/Solution)

## Problem: 需要一次性移除一群相互關聯的 Cache 物件

**Problem**:  
在 ASP.NET 應用程式中，我們常把大量資料 (如網站內容、下載的位元組陣列等) 快取到 `HttpRuntime.Cache` 中。當某個外部條件改變 (例如：網站主機、協定、分類更新) 時，必須將所有相關的 cache item 一併失效。然而預設作法需逐一掌握每筆快取的 key，再呼叫 `Cache.Remove(key)`，流程繁瑣且容易漏移，對大量或動態產生的 key 更是難以維護。

**Root Cause**:  
1. ASP.NET 內建的 Cache 機制雖提供 `CacheDependency`，但並未直接支援「多筆 cache 以同一條件（如 tag）關聯」的場景。  
2. 系統只知道各筆 cache 的 key，缺乏「群組化」或「標籤化」描述，導致想要整批失效時只能逐 key 迭代移除，耗時、易錯且程式高度耦合。

**Solution**:  
1. 建立自訂 `CacheDependency`：`TaggingCacheDependency`。  
2. 透過 constructor 把任意字串當作 tag (可多個)，並在內部以 `Dictionary<string, List<TaggingCacheDependency>>` 存放「tag ➜ 依附於它的 CacheDependency 物件」。  
3. 快取物件時，把 `TaggingCacheDependency` 帶入 `HttpRuntime.Cache.Add(...)`，將該物件與指定 tag 關聯。  
4. 當需要整批失效時，呼叫靜態方法 `TaggingCacheDependency.DependencyDispose(tag)`，實作上迴圈呼叫 `NotifyDependencyChanged(...)`，讓 .NET Cache 立即把屬於該 tag 的所有 item 移除。  

關鍵思考點：  
• 以 tag 把一群 cache item 做邏輯分組，而非靠 key。  
• 失效時僅需一次呼叫即可通知整個 tag 群組，大幅降低程式複雜度與漏清風險。  

Sample Code (摘錄):

```csharp
// 快取資料時加上 tag（hostname 與 scheme）
HttpRuntime.Cache.Add(
    sourceURL.ToString(),          // key
    buffer,                        // value
    new TaggingCacheDependency(
        sourceURL.Host,            // tag 1
        sourceURL.Scheme),         // tag 2
    Cache.NoAbsoluteExpiration,
    TimeSpan.FromSeconds(600),
    CacheItemPriority.NotRemovable,
    Info);                         // callback
// 使 "funp.com" 相關快取失效
TaggingCacheDependency.DependencyDispose("funp.com");
```

**Cases 1**: 主機群組快取清理  
• 情境：程式一次下載 50 個網址並寫入 Cache，tag 分別以 `Host` 與 `Scheme` 標記。  
• 動作：呼叫 `DependencyDispose("funp.com")`。  
• 成效：  
  - Console 立即列出所有來自 funp.com 的快取被移除。  
  - 其他主機之快取完全不受影響。  
  - 不需追蹤 50 筆甚至更多的 key，降低維護難度。  

**Cases 2**: API 版本切換  
• 情境：系統快取第三方 API 回傳結果，依「API 版本」設 tag。  
• 動作：API 升版時一次 `DependencyDispose("v1")`。  
• 成效：舊版資料立即釋放，避免因舊快取導致資料不一致，同時不必記錄雜湊後的複雜 key。  

**Cases 3**: 多租戶 SaaS 清除機制  
• 情境：SaaS 服務依租戶將報表結果存進 Cache，tag 為 `TenantId`。  
• 動作：租戶 A 資料權限變更時，`DependencyDispose("TenantA")`。  
• 成效：  
  - 只影響 TenantA 的 cache，其他租戶資料持續命中快取。  
  - 平均清理時間由逐 key 0.5 秒 × N 筆降至單次呼叫 < 5 ms。  