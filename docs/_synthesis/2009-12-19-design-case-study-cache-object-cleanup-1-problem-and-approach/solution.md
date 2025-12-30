---
layout: synthesis
title: "[設計案例] 清除Cache物件 #1. 問題與作法"
synthesis_type: solution
source_post: /2009/12/19/design-case-study-cache-object-cleanup-1-problem-and-approach/
redirect_from:
  - /2009/12/19/design-case-study-cache-object-cleanup-1-problem-and-approach/solution/
---

以下內容基於原文的實際場景與方法，將所有可辨識的問題—根因—解法整理為可教學、可實作的 16 個案例。每個案例皆附有示意程式碼與練習/評估建議，便於教學與專案演練。

## Case #1: 已知 Key 的單筆 Cache 移除

### Problem Statement（問題陳述）
業務場景：ASP.NET 應用把遠端下載的資源先放進 HttpRuntime.Cache，加速後續存取。當某筆資料確認過期或錯誤，需要讓營運人員或程式在不重啟服務的前提下立刻移除目標快取項目，以避免使用舊資料。
技術挑戰：如何正確、立即、且線上進行單筆快取移除。
影響範圍：若移除失敗或遲滯，會造成用戶看到過期資料與記憶體浪費。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 需要能以唯一鍵值定位到目標 cache item。
2. 需要可在應用運行時進行的 API。
3. 移除後無需等待到期時間或依賴掃描機制。

深層原因：
- 架構層面：缺乏統一的快取 Key 命名與存取介面。
- 技術層面：誤將 Cache 視為一般字典，忽略其過期/逐出時機。
- 流程層面：缺乏運維「立刻清除單筆」的操作指引。

### Solution Design（解決方案設計）
解決策略：以 HttpRuntime.Cache.Remove(key) 實作單筆即時移除；建立 KeyBuilder 與 CacheService 包裝，集中 Key 規約與日誌，避免散落呼叫與鍵值漂移。

實施步驟：
1. 建立 Key 規約與包裝服務
- 實作細節：定義 Key 命名規則（如前綴、版本），提供 RemoveByKey 與 TryGet 方法。
- 所需資源：C#、System.Web.Caching
- 預估時間：0.5 天

2. 導入日誌與操作面板
- 實作細節：在移除成功/失敗時記錄事件；提供簡易管理介面輸入 Key 進行移除。
- 所需資源：記錄框架、管理頁
- 預估時間：0.5-1 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static class CacheService
{
    public static bool RemoveByKey(string key)
    {
        if (string.IsNullOrWhiteSpace(key)) return false;
        HttpRuntime.Cache.Remove(key);
        return true;
    }
}
```

實際案例：原文情境中以 Remove("cache-key") 單行達成移除。
實作環境：ASP.NET（System.Web）、.NET Framework 2.0–4.8、C#
實測數據：
改善前：需等待 Expiration 或重啟應用
改善後：呼叫後即時生效
改善幅度：文章未提供；可用「移除至不可命中延遲」(ms) 測量

Learning Points（學習要點）
核心知識點：
- HttpRuntime.Cache.Remove 的即時性
- Key 規約的重要性
- 包裝服務的可維護性

技能要求：
- 必備技能：C#、ASP.NET Cache API
- 進階技能：日誌與管理面板設計

延伸思考：
- 如何避免硬編碼 Key？
- 如何審計誰在何時移除了什麼？

Practice Exercise（練習題）
- 基礎練習：實作 RemoveByKey 並加上成功/失敗日誌（30 分鐘）
- 進階練習：為 RemoveByKey 加上權限驗證與操作記錄（2 小時）
- 專案練習：完成一個快取管理頁（查詢/移除）（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：是否能即時移除目標
- 程式碼品質（30%）：封裝、命名、日誌
- 效能優化（20%）：移除延遲與最小化副作用
- 創新性（10%）：友善的操作介面或審計報表


## Case #2: 取得所有存在 Cache 的 Key 清單

### Problem Statement（問題陳述）
業務場景：運維或除錯時需要知道目前快取內有哪些項目，以檢視佔用、命名是否一致、或進行批次清除。
技術挑戰：Cache 不像一般 Dictionary 提供 Keys 屬性，如何正確列舉全部鍵值。
影響範圍：無法掌握現況將導致管理困難與誤殺項目。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Cache 未暴露 Keys 屬性。
2. 需透過 GetEnumerator 巡覽。
3. 巡覽過程中條目可能被逐出。

深層原因：
- 架構層面：缺乏可觀測性設計與儀表板。
- 技術層面：忽略 Cache 的非穩定性（可能隨時變更）。
- 流程層面：沒有既定的巡覽/清查流程。

### Solution Design（解決方案設計）
解決策略：使用 GetEnumerator 建立鍵值快照（複製到 List），後續操作均基於快照，避免迭代時被修改造成錯誤。

實施步驟：
1. 安全列舉與快照
- 實作細節：使用 IDictionaryEnumerator 迭代並複製 Key 至 List<string>
- 所需資源：C#、System.Collections
- 預估時間：0.5 天

2. 快照檢視與輸出
- 實作細節：將清單輸出至頁面或日誌，支援篩選
- 所需資源：前端頁/CLI
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static List<string> SnapshotCacheKeys()
{
    var keys = new List<string>();
    IDictionaryEnumerator e = HttpRuntime.Cache.GetEnumerator();
    while (e.MoveNext())
    {
        keys.Add(e.Key as string);
    }
    return keys;
}
```

實際案例：原文指出「它藏在 GetEnumerator」，並示意 foreach 巡覽。
實作環境：ASP.NET、.NET Framework、C#
實測數據：
改善前：無法取得 Key 清單
改善後：可取得鍵值快照
改善幅度：文章未提供；可用「清查完成時間」與「快照鍵數」觀測

Learning Points（學習要點）
核心知識點：
- Cache.GetEnumerator 的用法
- 為避免競態先建立快照
- 觀測性的重要

技能要求：
- 必備技能：C# 集合操作
- 進階技能：可視化與報表

延伸思考：
- 如何避免列舉巨大快取造成延遲？
- 是否應限制列舉頻率？

Practice Exercise（練習題）
- 基礎練習：列出所有鍵至日誌（30 分鐘）
- 進階練習：加入前綴/正則過濾與分頁（2 小時）
- 專案練習：做一個快取巡覽頁面（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能穩定取得鍵清單
- 程式碼品質（30%）：異常處理與可測試性
- 效能優化（20%）：避免阻塞
- 創新性（10%）：靈活過濾與導出


## Case #3: 安全地在列舉後移除匹配的 Cache 項目

### Problem Statement（問題陳述）
業務場景：需要批次移除符合條件的快取項目（例如字首、網域），但列舉到的 Key 在操作下一秒可能已被逐出。
技術挑戰：如何在動態變動的快取中，安全且不拋例外地批次刪除。
影響範圍：粗暴操作恐導致例外、錯刪或重試成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Cache 非穩定資料集。
2. 列舉與移除存在時間差。
3. 缺少再驗證存在性的流程。

深層原因：
- 架構層面：批次操作未抽象化。
- 技術層面：忽略二次檢查與防護性程式。
- 流程層面：沒有既定移除規則或限速。

### Solution Design（解決方案設計）
解決策略：先快照鍵清單，再針對快照逐一嘗試移除，移除前先嘗試讀取確認存在；失敗不視為錯誤，記錄即可。

實施步驟：
1. 快照與過濾
- 實作細節：取快照後用 predicate 過濾目標鍵
- 所需資源：C#
- 預估時間：0.5 天

2. 安全移除與記錄
- 實作細節：TryGet 再 Remove，捕捉並吞噬已不存在的情況
- 所需資源：日誌
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static int SafeRemove(Func<string, bool> predicate)
{
    var keys = SnapshotCacheKeys();
    int removed = 0;
    foreach (var key in keys)
    {
        if (!predicate(key)) continue;
        var val = HttpRuntime.Cache.Get(key);
        if (val != null)
        {
            HttpRuntime.Cache.Remove(key);
            removed++;
        }
    }
    return removed;
}
```

實際案例：原文提醒「風險蠻高，下一秒可能不在」。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：批次刪除易拋例外或錯刪
改善後：移除流程穩定且可觀測
改善幅度：文章未提供；可觀測「移除成功率/錯誤率」

Learning Points（學習要點）
核心知識點：
- 快照—再驗證—移除三段式
- 容錯與記錄
- 動態資料集操作

技能要求：
- 必備技能：C# 委派、例外處理
- 進階技能：操作審計

延伸思考：
- 是否需要節流（Rate Limit）避免阻塞？
- 如何可重入與重試？

Practice Exercise（練習題）
- 基礎練習：實作 predicate 過濾（30 分鐘）
- 進階練習：加入限速與統計（2 小時）
- 專案練習：封裝批次移除服務與頁面（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：安全刪除符合條件項目
- 程式碼品質（30%）：可讀、可測
- 效能優化（20%）：控制批次大小
- 創新性（10%）：統計與報表


## Case #4: 依網域批次清除（天真做法：正則/解析 URL + 列舉）

### Problem Statement（問題陳述）
業務場景：模擬瀏覽器快取，需提供「清除特定網站下載內容」功能（例如 columns.chicken-house.net）。
技術挑戰：如何快速找出屬於某網域的 URL 快取項目並清除。
影響範圍：若效率低，清除時間過長；若判斷錯誤，可能誤刪。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 快取鍵為 URL，需要解析取得 Host。
2. 無現成依網域索引。
3. 只能列舉全部 Key 再過濾。

深層原因：
- 架構層面：缺少分群與索引設計。
- 技術層面：過濾為 O(n) 掃描。
- 流程層面：未定義清除策略與頻率。

### Solution Design（解決方案設計）
解決策略：以列舉 + Uri 解析/正則過濾匹配 Host，匹配成功者再安全移除；雖可行，但 O(n) 掃描，僅適合小量快取或偶爾操作。

實施步驟：
1. 快照並過濾網域
- 實作細節：new Uri(key).Host == targetHost
- 所需資源：C#
- 預估時間：0.5 天

2. 安全移除
- 實作細節：參考 Case #3 的再驗證移除
- 所需資源：日誌
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static int ClearByDomain(string targetHost)
{
    return SafeRemove(key =>
    {
        if (Uri.TryCreate(key, UriKind.Absolute, out var uri))
            return string.Equals(uri.Host, targetHost, StringComparison.OrdinalIgnoreCase);
        return false;
    });
}
```

實際案例：原文列出需求 1「刪除某特定網站的資料」。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：無法選網域清除
改善後：可按網域清除（O(n)）
改善幅度：文章未提供；可觀測「掃描時間/刪除數」

Learning Points（學習要點）
核心知識點：
- URL 解析
- O(n) 扫描的代價
- 安全批次移除

技能要求：
- 必備技能：C# Uri API
- 進階技能：效能分析

延伸思考：
- 如何避免每次 O(n) 掃描？
- 是否需要網域索引或分群？

Practice Exercise（練習題）
- 基礎練習：實作 ClearByDomain（30 分鐘）
- 進階練習：加入通配子網域（2 小時）
- 專案練習：管理頁面支援網域清除（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #5: 依傳輸協定批次清除（https/http，天真做法）

### Problem Statement（問題陳述）
業務場景：提供「清除所有 https 下載內容」的運維功能，以利針對安全內容做快速刷新。
技術挑戰：從 URL 鍵值判定協定並清除。
影響範圍：掃描大量 Key 影響效能。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 需從 URL 解析 Scheme。
2. 無協定索引，只能全掃。
3. 快取項目變動頻繁。

深層原因：
- 架構層面：缺乏協定分群。
- 技術層面：無增量索引，導致 O(n)。
- 流程層面：清除頻率未規劃。

### Solution Design（解決方案設計）
解決策略：列舉鍵值後以 Uri.Scheme 過濾 https，再按 Case #3 邏輯移除；短期可用，長期應改用分群依賴。

實施步驟：
1. 快照並過濾 https
- 實作細節：Uri.TryCreate + uri.Scheme == Uri.UriSchemeHttps
- 所需資源：C#
- 預估時間：0.5 天

2. 移除與記錄
- 實作細節：逐一 Remove、統計刪除數
- 所需資源：日誌
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static int ClearByScheme(string scheme)
{
    return SafeRemove(key =>
    {
        return Uri.TryCreate(key, UriKind.Absolute, out var uri) &&
               string.Equals(uri.Scheme, scheme, StringComparison.OrdinalIgnoreCase);
    });
}
```

實際案例：原文需求 3「刪除特定 protocol（如 https）」。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：無法按協定清除
改善後：可按協定清除（O(n)）
改善幅度：文章未提供；觀測「刪除數/耗時」

Learning Points（學習要點）
核心知識點：
- Uri.Scheme 過濾
- O(n) 全掃的限制
- 需求到設計的對應

技能要求：
- 必備技能：C# Uri API
- 進階技能：效能監測

延伸思考：
- 如何從設計避免全掃？
- 是否需要協定標籤化？

Practice Exercise（練習題）
- 基礎練習：完成 ClearByScheme（30 分鐘）
- 進階練習：同時支援多協定（2 小時）
- 專案練習：將協定清除接入管理介面（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #6: 依 Content-Type 批次清除（天真做法）

### Problem Statement（問題陳述）
業務場景：提供「清除所有 image/jpeg」功能，快速針對圖片類資源刷新。
技術挑戰：Key 只有 URL，Content-Type 不在鍵中，需要能在快取值內取得。
影響範圍：如果無法判斷型別，將無從下手或誤刪。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 快取值未保存 Content-Type 中繼資料。
2. 只能透過值物件判斷。
3. 仍需全掃與過濾。

深層原因：
- 架構層面：快取值缺中繼資料設計。
- 技術層面：值物件強型別化不足。
- 流程層面：未定義寫入快取時的結構規約。

### Solution Design（解決方案設計）
解決策略：定義強型別封裝（含 Url、ContentType、Payload），寫入時保存型別；清除時列舉 Key 後取值判斷 ContentType，再安全移除。

實施步驟：
1. 定義封裝類別
- 實作細節：CachedResponse { Url, ContentType, Bytes }
- 所需資源：C#
- 預估時間：0.5 天

2. 全掃過濾移除
- 實作細節：Get(key) as CachedResponse 判斷後 Remove
- 所需資源：日誌
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public class CachedResponse
{
    public string Url { get; set; }
    public string ContentType { get; set; }
    public byte[] Content { get; set; }
}

public static int ClearByContentType(string targetType)
{
    var keys = SnapshotCacheKeys();
    int removed = 0;
    foreach (var key in keys)
    {
        var val = HttpRuntime.Cache.Get(key) as CachedResponse;
        if (val != null && string.Equals(val.ContentType, targetType, StringComparison.OrdinalIgnoreCase))
        {
            HttpRuntime.Cache.Remove(key);
            removed++;
        }
    }
    return removed;
}
```

實際案例：原文需求 2「刪除特定類型資料（如 image/jpeg）」。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：無法按 Content-Type 清除
改善後：可按型別清除（O(n)）
改善幅度：文章未提供；觀測「刪除數/耗時」

Learning Points（學習要點）
核心知識點：
- 值物件封裝中繼資料
- 先設計再清除
- 以型別為維度的操作

技能要求：
- 必備技能：C# 類別設計
- 進階技能：序列化與記憶體控制

延伸思考：
- 是否用標籤/分群降低掃描成本？
- 如何避免大物件反序列化的成本？

Practice Exercise（練習題）
- 基礎練習：實作 CachedResponse 封裝（30 分鐘）
- 進階練習：加入大小/建立時間欄位（2 小時）
- 專案練習：完成 Content-Type 清除與報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #7: 以外部索引管理 URL 清單（可行但沉重）

### Problem Statement（問題陳述）
業務場景：為加速批次清除，嘗試在應用中維護「網域/協定/型別 → Key 集合」索引，直接精準定位需清除的鍵。
技術挑戰：索引與快取生命週期不一致，項目可能先被逐出。
影響範圍：索引膨脹、不同步導致錯刪/漏刪。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 額外資料結構需維護一致性。
2. 快取逐出時索引需同步刪除。
3. 初始化/重啟需重建索引。

深層原因：
- 架構層面：非必要重造快取機制。
- 技術層面：缺少與快取事件的鉤子。
- 流程層面：重建策略未定義。

### Solution Design（解決方案設計）
解決策略：建立索引字典與寫入/移除雙寫邏輯；搭配 CacheItemRemovedCallback 維持同步。可行但成本高，僅適用快取規模可控的場景。

實施步驟：
1. 索引與雙寫
- 實作細節：Dictionary<string, HashSet<string>> domain→keys 等
- 所需資源：C#
- 預估時間：1-2 天

2. 移除回呼同步
- 実作細節：CacheItemRemovedCallback 中從索引刪除
- 所需資源：事件鉤子
- 預估時間：0.5-1 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
static readonly Dictionary<string, HashSet<string>> DomainIndex = new();

public static void Put(string url, object value)
{
    var host = new Uri(url).Host;
    lock (DomainIndex)
        (DomainIndex.TryGetValue(host, out var set) ? set : (DomainIndex[host] = new())).Add(url);

    HttpRuntime.Cache.Insert(
        url, value, null,
        Cache.NoAbsoluteExpiration, Cache.NoSlidingExpiration,
        CacheItemPriority.Normal,
        (k, v, r) => { lock (DomainIndex) DomainIndex[host].Remove(k); });
}
```

實際案例：原文將此法列為可行但不漂亮，維護代價大。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：全掃 O(n)
改善後：定向 O(k)（k 為匹配集合大小）
改善幅度：文章未提供；可比較「掃描鍵數」

Learning Points（學習要點）
核心知識點：
- 外部索引與一致性
- 移除回呼用途
- 成本與收益分析

技能要求：
- 必備技能：集合/同步
- 進階技能：一致性維護設計

延伸思考：
- 如何持久化索引？
- 是否值得為快取做二級索引？

Practice Exercise（練習題）
- 基礎練習：實作 DomainIndex（30 分鐘）
- 進階練習：加入協定索引與清除 API（2 小時）
- 專案練習：完成三維度索引與一致性測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #8: 用 CacheDependency + 檔案標籤實作「按網域」群組失效

### Problem Statement（問題陳述）
業務場景：需要高效清除某網域下「一整組」快取，不想每次全掃。
技術挑戰：如何以一個動作讓該群組的快取自動逐出。
影響範圍：效能、可維護性與操作簡潔度皆受影響。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無現成群組機制。
2. 需要關聯共用依賴。
3. 清除時觸發依賴失效。

深層原因：
- 架構層面：缺少分群設計。
- 技術層面：未善用 CacheDependency。
- 流程層面：缺乏標籤檔管理與權限配置。

### Solution Design（解決方案設計）
解決策略：為每個網域建立一個「標籤檔」並在寫入快取時設為 CacheDependency；清除時 touch 該檔案，一整組項目自動逐出。

實施步驟：
1. 建立標籤檔與關聯
- 實作細節：App_Data/tags/domain.{host}.tag
- 所需資源：檔案系統寫入權限
- 預估時間：0.5-1 天

2. 觸發清除（touch）
- 實作細節：File.SetLastWriteTimeUtc / Append
- 所需資源：I/O
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
static string DomainTagPath(string host) =>
    HttpContext.Current.Server.MapPath($"~/App_Data/tags/domain.{host}.tag");

static void EnsureTagFile(string path)
{
    if (!File.Exists(path))
        Directory.CreateDirectory(Path.GetDirectoryName(path)!);
    using (var _ = File.Open(path, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.ReadWrite)) { }
}

public static void PutWithDomainTag(string url, object value)
{
    var host = new Uri(url).Host;
    var tag = DomainTagPath(host);
    EnsureTagFile(tag);
    var dep = new CacheDependency(tag);
    HttpRuntime.Cache.Insert(url, value, dep);
}

public static void InvalidateDomain(string host)
{
    var tag = DomainTagPath(host);
    EnsureTagFile(tag);
    File.SetLastWriteTimeUtc(tag, DateTime.UtcNow);
}
```

實際案例：原文提出此解法「用檔案依賴一鍵清群組」，但憂慮 I/O。
實作環境：ASP.NET、.NET Framework；IIS 帳號需寫入 App_Data
實測數據：
改善前：O(n) 全掃
改善後：O(1) 觸發群組失效
改善幅度：文章未提供；可比較「清除耗時」

Learning Points（學習要點）
核心知識點：
- CacheDependency 基礎
- 群組失效設計
- I/O 權限與目錄規劃

技能要求：
- 必備技能：檔案 I/O、Cache API
- 進階技能：運維權限配置

延伸思考：
- 標籤檔大量時如何管理？
- 觸發頻率過高的影響？

Practice Exercise（練習題）
- 基礎練習：完成 PutWithDomainTag（30 分鐘）
- 進階練習：實作 InvalidateDomain API 與管理頁（2 小時）
- 專案練習：加上審計與節流控制（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #9: 用檔案標籤實作「按 Content-Type」群組失效

### Problem Statement（問題陳述）
業務場景：要一鍵清掉所有 image/jpeg 快取。
技術挑戰：將相同 Content-Type 的項目掛上同一檔案依賴。
影響範圍：避免全掃，大幅改善清除效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 需要 Content-Type → 標籤檔映射。
2. 寫入時帶上 CacheDependency。
3. 清除時 touch 對應檔。

深層原因：
- 架構層面：中繼資料驅動群組化。
- 技術層面：封裝寫入流程。
- 流程層面：管理標籤命名與權限。

### Solution Design（解決方案設計）
解決策略：以 content-type 字串標準化為檔名，所有該型別的值都依賴此檔；清除時觸發檔案變更。

實施步驟：
1. 檔名生成與寫入封裝
- 實作細節：如 ~/App_Data/tags/ctype.image_jpeg.tag
- 所需資源：I/O 權限
- 預估時間：0.5-1 天

2. 清除 API
- 實作細節：File.SetLastWriteTimeUtc
- 所需資源：I/O
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
static string CtypeTagPath(string contentType)
{
    var safe = contentType.Replace('/', '_').Replace('+', '_');
    return HttpContext.Current.Server.MapPath($"~/App_Data/tags/ctype.{safe}.tag");
}

public static void PutWithCtypeTag(CachedResponse resp)
{
    var tag = CtypeTagPath(resp.ContentType);
    EnsureTagFile(tag);
    var dep = new CacheDependency(tag);
    HttpRuntime.Cache.Insert(resp.Url, resp, dep);
}

public static void InvalidateContentType(string contentType)
{
    var tag = CtypeTagPath(contentType);
    EnsureTagFile(tag);
    File.SetLastWriteTimeUtc(tag, DateTime.UtcNow);
}
```

實際案例：原文提出「依 Content-Type 批次清除」需求。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：全掃 + 值檢查
改善後：O(1) 清除該型別
改善幅度：文章未提供；可比較「刪除耗時/命中率變化」

Learning Points（學習要點）
核心知識點：
- 以中繼資料分群
- 安全檔名生成
- 依賴觸發

技能要求：
- 必備技能：字串處理、I/O
- 進階技能：檔名碰撞防護

延伸思考：
- 一個項目屬於多型別時怎麼辦？
- 是否需要複合標籤？

Practice Exercise（練習題）
- 基礎練習：完成 CtypeTag 封裝（30 分鐘）
- 進階練習：加入白名單驗證（2 小時）
- 專案練習：複合標籤（ctype+domain）清除（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #10: 用檔案標籤實作「按協定」群組失效

### Problem Statement（問題陳述）
業務場景：一鍵清除所有 https 內容，支援多種協定。
技術挑戰：寫入時為不同協定建立對應依賴，清除時觸發。
影響範圍：運維效率、清除粒度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 需從 URL 解析 scheme。
2. 建立 scheme→tag 檔映射。
3. 寫入關聯、清除觸發。

深層原因：
- 架構層面：以協定分群。
- 技術層面：封裝寫入流程。
- 流程層面：不同協定的清除頻率管理。

### Solution Design（解決方案設計）
解決策略：依 scheme（http/https）產生標籤檔並設依賴，清除時 touch 對應檔案。

實施步驟：
1. 寫入與依賴
- 實作細節：Uri.Scheme 判斷；依賴 scheme tag
- 所需資源：I/O
- 預估時間：0.5 天

2. 清除 API
- 實作細節：InvalidateScheme
- 所需資源：I/O
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
static string SchemeTagPath(string scheme) =>
    HttpContext.Current.Server.MapPath($"~/App_Data/tags/scheme.{scheme.ToLowerInvariant()}.tag");

public static void PutWithSchemeTag(string url, object value)
{
    var uri = new Uri(url);
    var tag = SchemeTagPath(uri.Scheme);
    EnsureTagFile(tag);
    HttpRuntime.Cache.Insert(url, value, new CacheDependency(tag));
}

public static void InvalidateScheme(string scheme)
{
    var tag = SchemeTagPath(scheme);
    EnsureTagFile(tag);
    File.SetLastWriteTimeUtc(tag, DateTime.UtcNow);
}
```

實際案例：原文提出「依協定清除」需求。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：O(n) 全掃
改善後：O(1) 清除
改善幅度：文章未提供；觀測「清除耗時」

Learning Points（學習要點）
核心知識點：
- 協定分群
- 寫入封裝
- 依賴觸發

技能要求：
- 必備技能：Uri API、I/O
- 進階技能：標籤管理

延伸思考：
- 自訂協定（如 data:）的處理？
- 多協定內容的合規性？

Practice Exercise（練習題）
- 基礎練習：完成 PutWithSchemeTag（30 分鐘）
- 進階練習：支援多協定同時清除（2 小時）
- 專案練習：加入審計與錯誤回報（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #11: Tag 檔觸發器的可靠 Touch 設計

### Problem Statement（問題陳述）
業務場景：群組清除依賴檔案變更；需確保可重複、可靠觸發，不受檔案鎖定與不存在影響。
技術挑戰：在高併發/多次操作下避免 I/O 例外。
影響範圍：觸發失敗會導致無法清除。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 檔案可能不存在。
2. 檔案可能被鎖。
3. 權限不足導致無法寫入。

深層原因：
- 架構層面：未設計健壯的 touch 流程。
- 技術層面：忽略 FileShare/重試。
- 流程層面：未在部署設權限。

### Solution Design（解決方案設計）
解決策略：封裝 EnsureTagFile + SetLastWriteTimeUtc，使用 OpenOrCreate 與寬鬆 FileShare，必要時 fallback 到 Append 一個字元再刪除以確保變更通知。

實施步驟：
1. 封裝 Ensure + Touch
- 實作細節：OpenOrCreate、FileShare.ReadWrite、重試
- 所需資源：I/O
- 預估時間：0.5 天

2. 部署權限校驗
- 實作細節：IIS AppPool 身分對 App_Data 具寫入權
- 所需資源：運維
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static void Touch(string path)
{
    EnsureTagFile(path);
    try
    {
        File.SetLastWriteTimeUtc(path, DateTime.UtcNow);
    }
    catch
    {
        // Fallback: append a byte then truncate
        using (var fs = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite))
        {
            fs.Seek(0, SeekOrigin.End);
            fs.WriteByte(0);
            fs.SetLength(Math.Max(0, fs.Length - 1));
        }
    }
}
```

實際案例：原文指出 I/O 是最慢且可能是愚蠢之處，需謹慎。
實作環境：Windows + NTFS、IIS
實測數據：
改善前：偶發觸發失敗
改善後：觸發成功率提升
改善幅度：文章未提供；可觀測「觸發成功率/失敗原因分布」

Learning Points（學習要點）
核心知識點：
- Touch 模式
- FileShare 與鎖
- 權限設定

技能要求：
- 必備技能：檔案 I/O
- 進階技能：運維權限

延伸思考：
- 多機部署共用檔案是否安全？
- 是否需改用其他依賴機制？

Practice Exercise（練習題）
- 基礎練習：實作 Touch（30 分鐘）
- 進階練習：加入重試與回退策略（2 小時）
- 專案練習：做一個標籤健康檢查工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #12: 以「快取鍵依賴」實現群組失效（免檔案 I/O）

### Problem Statement（問題陳述）
業務場景：避免檔案 I/O，仍要達成一鍵清除一組快取的能力。
技術挑戰：如何利用 CacheDependency 的「鍵依賴」觸發連鎖失效。
影響範圍：清除效率、部署簡化（免權限）。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 檔案依賴存在 I/O 開銷與權限。
2. Cache 支援鍵依賴。
3. 需有「標籤鍵」作為依賴根。

深層原因：
- 架構層面：內部化依賴，消除外部副作用。
- 技術層面：掌握 CacheDependency 建構子（cacheKeys）。
- 流程層面：標籤鍵生成與生命週期管理。

### Solution Design（解決方案設計）
解決策略：先放入一個「標籤鍵」（如 tag:domain:xxx），所有要分群的項目 Insert 時指定 CacheDependency(null, new[] { tagKey })；清除時 Remove 標籤鍵即可連鎖移除。

實施步驟：
1. 建立標籤鍵
- 實作細節：Insert(tagKey, sentinel) 不過期
- 所需資源：Cache API
- 預估時間：0.5 天

2. 依賴與清除
- 實作細節：new CacheDependency(null, new[] { tagKey }); Remove(tagKey)
- 所需資源：Cache API
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
static string DomainTagKey(string host) => $"tag:domain:{host.ToLowerInvariant()}";

public static void EnsureTagKey(string tagKey)
{
    if (HttpRuntime.Cache.Get(tagKey) == null)
        HttpRuntime.Cache.Insert(tagKey, new object());
}

public static void PutWithDomainTagKey(string url)
{
    var host = new Uri(url).Host;
    var tagKey = DomainTagKey(host);
    EnsureTagKey(tagKey);
    var dep = new CacheDependency(null, new[] { tagKey });
    HttpRuntime.Cache.Insert(url, /*value*/ new object(), dep);
}

public static void InvalidateDomainByKey(string host)
{
    HttpRuntime.Cache.Remove(DomainTagKey(host));
}
```

實際案例：原文批評檔案 I/O 慢，此法為針對該痛點的改良方案。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：檔案 I/O 觸發
改善後：純記憶體鍵觸發
改善幅度：文章未提供；可觀測「清除耗時/CPU 使用率」

Learning Points（學習要點）
核心知識點：
- CacheDependency 鍵依賴
- 標籤鍵設計
- I/O vs 記憶體取捨

技能要求：
- 必備技能：Cache API 熟悉
- 進階技能：群組生命週期管理

延伸思考：
- 標籤鍵被意外逐出怎麼辦？
- 是否需要版本化標籤鍵？

Practice Exercise（練習題）
- 基礎練習：實作 EnsureTagKey（30 分鐘）
- 進階練習：用鍵依賴完成三種分群（2 小時）
- 專案練習：比較檔案 vs 鍵依賴效能（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #13: 群組標籤鍵的「版本化」以避免競態與殘留

### Problem Statement（問題陳述）
業務場景：在高併發下，清除與新增同時發生，剛被移除的標籤鍵又被新項目依賴，導致新老項目混雜。
技術挑戰：如何在清除後建立「新世代」標籤鍵，避免把新項目依附到舊世代。
影響範圍：資料一致性與預期行為。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 清除與新增同時進行。
2. 標籤鍵名稱固定導致競態。
3. 缺乏世代概念。

深層原因：
- 架構層面：需世代化群組。
- 技術層面：原子切換世代。
- 流程層面：清除與寫入時序未協調。

### Solution Design（解決方案設計）
解決策略：標籤鍵加入版本號（tag:domain:xxx:vN），清除時先移除舊世代鍵，再立即建立新世代鍵並切換寫入端使用的版本。

實施步驟：
1. 版本鍵生成與切換
- 實作細節：Interlocked.Increment 全域版本；或時間戳
- 所需資源：同步原語
- 預估時間：1 天

2. 寫入端讀取當前版本
- 實作細節：從共享配置取得 current version
- 所需資源：記憶體共享
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
static int _domainVer = 0;
static string DomainTagKey(string host, int v) => $"tag:domain:{host}:v{v}";

public static void RotateDomainTag(string host)
{
    var v = Interlocked.Increment(ref _domainVer);
    HttpRuntime.Cache.Remove(DomainTagKey(host, v - 1)); // invalidate old gen
    EnsureTagKey(DomainTagKey(host, v));                 // create new gen
}

public static void PutWithDomainGen(string url)
{
    var host = new Uri(url).Host;
    var v = Volatile.Read(ref _domainVer);
    var tag = DomainTagKey(host, v);
    EnsureTagKey(tag);
    HttpRuntime.Cache.Insert(url, new object(), new CacheDependency(null, new[] { tag }));
}
```

實際案例：延伸自原文分群清除需求，解競態問題。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：清除/新增競態導致混淆
改善後：世代分明、行為可預期
改善幅度：文章未提供；可觀測「錯綁比率」

Learning Points（學習要點）
核心知識點：
- 版本化與世代管理
- 原子操作
- 一致性設計

技能要求：
- 必備技能：多執行緒同步
- 進階技能：一致性模型

延伸思考：
- 多台機器如何同步版本？
- 是否需使用分散式儲存版本？

Practice Exercise（練習題）
- 基礎練習：加入版本號鍵（30 分鐘）
- 進階練習：多執行緒壓力測試（2 小時）
- 專案練習：多機版本同步設計（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #14: 使用 CacheItemRemovedCallback 觀測與維持外部結構一致性

### Problem Statement（問題陳述）
業務場景：當項目被逐出（過期或手動移除）需要同步更新外部索引或記錄，可追蹤清除效果。
技術挑戰：如何在移除時可靠獲取回呼。
影響範圍：外部索引一致性、審計。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無回呼則無從同步。
2. 清除來源多樣（過期/依賴/手動）。
3. 需獲得移除原因。

深層原因：
- 架構層面：觀測性不足。
- 技術層面：未使用回呼 API。
- 流程層面：無審計策略。

### Solution Design（解決方案設計）
解決策略：Insert 時指定 CacheItemRemovedCallback；回呼中根據 CacheItemRemovedReason 同步外部索引與寫入審計。

實施步驟：
1. 設定回呼
- 實作細節：Insert key 時加入回呼委派
- 所需資源：C#
- 預估時間：0.5 天

2. 同步與審計
- 實作細節：清外部結構、寫入日誌
- 所需資源：日誌
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static void PutWithCallback(string key, object value)
{
    HttpRuntime.Cache.Insert(
        key, value, null,
        Cache.NoAbsoluteExpiration, Cache.NoSlidingExpiration,
        CacheItemPriority.Normal,
        (k, v, reason) => LogRemoval(k, reason));
}

static void LogRemoval(string key, CacheItemRemovedReason reason)
{
    // TODO: 審計/更新外部索引
    System.Diagnostics.Trace.WriteLine($"Removed {key} by {reason}");
}
```

實際案例：原文提到外部索引方案需要同步；回呼可助一致性。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：外部結構易不同步
改善後：回呼同步降低不一致
改善幅度：文章未提供；可觀測「不同步事件數」

Learning Points（學習要點）
核心知識點：
- CacheItemRemovedCallback
- 移除原因辨識
- 一致性維護

技能要求：
- 必備技能：委派、事件
- 進階技能：審計設計

延伸思考：
- 回呼阻塞的風險？
- 是否需非同步處理？

Practice Exercise（練習題）
- 基礎練習：打印移除原因（30 分鐘）
- 進階練習：將審計寫入資料庫（2 小時）
- 專案練習：外部索引同步 + 重建（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #15: 檔案依賴的權限與部署安全

### Problem Statement（問題陳述）
業務場景：使用檔案標籤時，IIS 應用程序池帳號需具備 App_Data/tags 的寫入權限；部署時常因權限不足導致清除失敗。
技術挑戰：兼顧最小權限與可運行。
影響範圍：清除功能不可用、錯誤難以察覺。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 應用帳號無寫入權限。
2. 目錄不存在。
3. 錯誤未妥善記錄。

深層原因：
- 架構層面：對環境依賴未宣告。
- 技術層面：缺少啟動期自檢。
- 流程層面：部署腳本未設權限。

### Solution Design（解決方案設計）
解決策略：在應用啟動時執行自檢（目錄、權限、touch 測試）；提供部署腳本設定 ACL；所有 I/O 失敗明確記錄與告警。

實施步驟：
1. 啟動自檢
- 實作細節：確保 tags 目錄存在並測試 touch
- 所需資源：I/O
- 預估時間：0.5 天

2. 部署腳本與告警
- 實作細節：icacls/PowerShell 設置寫入權；加上健康檢查端點
- 所需資源：運維腳本
- 預估時間：0.5-1 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static bool VerifyTagFolder()
{
    try
    {
        var path = HttpContext.Current.Server.MapPath("~/App_Data/tags");
        Directory.CreateDirectory(path);
        var probe = Path.Combine(path, "probe.tag");
        Touch(probe);
        return true;
    }
    catch (Exception ex)
    {
        // TODO: 記錄並告警
        return false;
    }
}
```

實際案例：原文提到 I/O 是慢且有風險；部署權限是常見痛點。
實作環境：IIS、Windows ACL
實測數據：
改善前：偶發/常態清除失敗
改善後：啟動即檢出問題、可快速修復
改善幅度：文章未提供；可觀測「部署後故障率」

Learning Points（學習要點）
核心知識點：
- 最小權限原則
- 啟動期健康檢查
- 可觀測性

技能要求：
- 必備技能：Windows 權限
- 進階技能：自動化腳本

延伸思考：
- 容器化部署時的目錄掛載？
- 多機集群如何一致？

Practice Exercise（練習題）
- 基礎練習：實作 VerifyTagFolder（30 分鐘）
- 進階練習：寫出 icacls 設權腳本（2 小時）
- 專案練習：健康檢查與告警整合（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）


## Case #16: 封裝「瀏覽器式快取」服務（URL→值 + 三維群組依賴）

### Problem Statement（問題陳述）
業務場景：實作簡易 web 瀏覽器式快取，支援 URL 快取、並可依網域/協定/Content-Type 一鍵清除。
技術挑戰：需一致的寫入封裝、分群依賴、清除 API 與觀測性。
影響範圍：整體可維護性與效能。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 零散的寫入/清除易錯。
2. 缺乏統一 API。
3. 無統計與日誌。

深層原因：
- 架構層面：服務化封裝缺失。
- 技術層面：依賴與回呼未整合。
- 流程層面：沒有可運維的界面。

### Solution Design（解決方案設計）
解決策略：實作 BrowserCacheService：寫入時同時掛上三種群組依賴（選檔案或鍵依賴）；提供對應 Invalidate API 與觀測統計；管理頁面一鍵操作。

實施步驟：
1. 服務與 API
- 實作細節：Put/Get/InvalidateDomain/InvalidateScheme/InvalidateContentType
- 所需資源：C#
- 預估時間：1-2 天

2. 觀測與管理頁
- 實作細節：統計數、最近清除事件
- 所需資源：前後端
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
// Implementation Example（實作範例）
public static class BrowserCacheService
{
    public static void Put(CachedResponse resp)
    {
        var deps = new List<CacheDependency>();
        // 建議使用鍵依賴（避免 I/O）
        var domainTag = $"tag:domain:{new Uri(resp.Url).Host}";
        var schemeTag = $"tag:scheme:{new Uri(resp.Url).Scheme}";
        var ctypeTag = $"tag:ctype:{resp.ContentType.Replace('/', '_')}";
        EnsureTagKey(domainTag); EnsureTagKey(schemeTag); EnsureTagKey(ctypeTag);
        var dep = new CacheDependency(null, new[] { domainTag, schemeTag, ctypeTag });
        HttpRuntime.Cache.Insert(resp.Url, resp, dep);
    }

    public static CachedResponse Get(string url) =>
        HttpRuntime.Cache.Get(url) as CachedResponse;

    public static void InvalidateDomain(string host) =>
        HttpRuntime.Cache.Remove($"tag:domain:{host}");

    public static void InvalidateScheme(string scheme) =>
        HttpRuntime.Cache.Remove($"tag:scheme:{scheme}");

    public static void InvalidateContentType(string contentType) =>
        HttpRuntime.Cache.Remove($"tag:ctype:{contentType.Replace('/', '_')}");
}
```

實際案例：原文瀏覽器快取情境 + 三種分群清除需求。
實作環境：ASP.NET、.NET Framework
實測數據：
改善前：分散、重複、O(n) 扫描
改善後：服務化、O(1) 清群組
改善幅度：文章未提供；可觀測「平均清除耗時/命中率」

Learning Points（學習要點）
核心知識點：
- 服務化封裝
- 多重依賴
- 管理與觀測

技能要求：
- 必備技能：C# 設計
- 進階技能：運維介面

延伸思考：
- 如何落地到分散式快取（超出 HttpRuntime.Cache）？
- 是否要限流防誤操作？

Practice Exercise（練習題）
- 基礎練習：完成 Put/Get（30 分鐘）
- 進階練習：完成三種 Invalidate（2 小時）
- 專案練習：做一個完整管理頁與統計（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）
- 程式碼品質（30%）
- 效能優化（20%）
- 創新性（10%）



案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case #1, #2
- 中級（需要一定基礎）
  - Case #3, #4, #5, #6, #14, #15
- 高級（需要深厚經驗）
  - Case #7, #8, #9, #10, #11, #12, #13, #16

2. 按技術領域分類
- 架構設計類
  - Case #7, #8, #9, #10, #12, #13, #16
- 效能優化類
  - Case #3, #4, #5, #6, #8, #9, #10, #12
- 整合開發類
  - Case #1, #2, #14, #15, #16
- 除錯診斷類
  - Case #2, #3, #14, #15
- 安全防護類
  - Case #11, #15

3. 按學習目標分類
- 概念理解型
  - Case #1, #2, #3
- 技能練習型
  - Case #4, #5, #6, #14
- 問題解決型
  - Case #7, #8, #9, #10, #11, #15
- 創新應用型
  - Case #12, #13, #16



案例關聯圖（學習路徑建議）
- 入門順序（先學）
  1) Case #1（單筆移除基礎）
  2) Case #2（取得鍵清單）
  3) Case #3（安全批次移除）
- 需求驅動（天真法到優化）
  4) Case #4、#5、#6（以列舉過濾達成三種清除需求）
  5) Case #7（外部索引：可行但代價大，理解其限制）
- 分群失效（推薦方案）
  6) Case #8、#9、#10（檔案標籤分群）
  7) Case #11（可靠 touch 與權限）
- 進階優化（免 I/O 與一致性）
  8) Case #12（鍵依賴分群，最佳化）
  9) Case #13（版本化，解決競態）
  10) Case #14（回呼觀測與一致性）
  11) Case #15（部署安全與健康檢查）
- 收斂封裝（完成度）
  12) Case #16（服務化封裝，整合所有能力）

依賴關係：
- Case #3 依賴 #2
- Case #4/#5/#6 依賴 #2、#3
- Case #8/#9/#10 依賴群組需求認知（#4-#6）
- Case #11 依賴 #8-#10（檔案方案）
- Case #12 取代/優化 #8-#10（選其一）
- Case #13 依賴 #12（鍵依賴）
- Case #14 可輔助 #7 或 #16
- Case #15 輔助 #8-#10
- Case #16 彙整前述能力

完整學習路徑建議：
- 基礎（#1→#2→#3）→ 天真解（#4-#6）→ 認識索引取捨（#7）→ 分群依賴（檔案：#8-#11 或 鍵依賴：#12-#13）→ 觀測與部署（#14-#15）→ 封裝實作（#16）。此路徑由易至難，涵蓋概念、實作、優化與運維，最終能落地一套可用的快取清除方案。