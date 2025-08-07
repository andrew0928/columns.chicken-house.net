# [設計案例] 清除Cache物件 #1. 問題與作法  

# 問題／解決方案 (Problem/Solution)

## Problem: 無法「乾淨地」手動移除單一 Cache Item

**Problem**:  
在 ASP.NET 專案中，開發者常需要於執行期間「手動」將某個快取物件從 HttpRuntime.Cache 中移除。但在實務情境裡，程式必須先「記得」正確的 cache key，才能呼叫 HttpRuntime.Cache.Remove("key")。專案規模一旦增大，key 數量多且來源分散，開發者難以確保隨時都能正確取得該 key。

**Root Cause**:  
1. Cache 類型類似 Dictionary 卻未實作 IDictionary，開發者無現成 Keys 屬性可列舉所有 key。  
2. 系統缺乏集中式 key 管理機制，造成「取得 key」與「移除物件」兩件事在程式碼中被硬生生拆開。  

**Solution**:  
1. 統一以「可預期」字串格式（如 `{Feature}:{Id}`）產生 key。  
2. 在每個模組中封裝 `RemoveCacheXXX()` 方法，將組 key 與呼叫 `HttpRuntime.Cache.Remove(key)` 的責任關在同一處。  

```csharp
public static class BrowserCache
{
    private static string GetUrlKey(string url) => $"URL:{url}";

    public static void RemoveByUrl(string url)
    {
        HttpRuntime.Cache.Remove(GetUrlKey(url));
    }
}
```
此作法的關鍵思考：藉由封裝，讓外部呼叫端「只知道自己要清掉什麼邏輯物件」，而不用知道實體 cache key 長什麼樣。

---

## Problem: 想列舉 Cache 內所有 Key 卻無對應 API

**Problem**:  
在需要進行「有條件批次刪除」之前，我們往往得先盤點目前 Cache 裡到底有哪些 key。然而 Cache 類別沒有 Keys 屬性，僅能透過 `GetEnumerator()` 逐筆迭代。

**Root Cause**:  
1. Cache 的 non-generic enumerator 回傳的是隱含的 `DictionaryEntry`，沒有型別安全。  
2. Enumerate 期間，其他執行緒可能同時把物件踢出 Cache，導致「迭代到的 key 下一秒就不見」，存在高並發風險。  

**Solution**:  
1. 以 `foreach (DictionaryEntry de in HttpRuntime.Cache){ … }` 方式快取 key snapshot 至 List，再進行商業邏輯判斷，避免邊迴圈邊刪除造成的 InvalidOperationException。  
2. 若專案允許，可再搭配 `CacheLock`（自訂 lock）確保 enumerator 期間不會有其它執行緒刪 key。  

```csharp
List<string> snapshot;
lock(CacheLock)
{
    snapshot = HttpRuntime.Cache.Cast<DictionaryEntry>()
                                .Select(de => de.Key.ToString())
                                .ToList();
}
foreach (var key in snapshot)
{
    // 依條件挑選再移除
}
```

---

## Problem: 需要「批次」清除符合條件的一群 Cache 物件 (依網域/Content-Type/Protocol…)

**Problem**:  
如同瀏覽器快取情境：  
1. 刪除所有來自 `columns.chicken-house.net` 的資源  
2. 刪除所有 `image/jpeg` 的檔案  
3. 刪除所有透過 `https` 下載的內容  
使用 `Remove(key)` 只能一次砍一筆，而先 `foreach` 掃所有 cache 再用 Regex 比對不僅程式醜且效率差。

**Root Cause**:  
1. HttpRuntime.Cache 天生只支援「單一 key」刪除，缺乏群組概念。  
2. 以 Regex 篩選或自行維護 Dictionary 的方法，效能常受限於大量迴圈與資料同步問題。  

**Solution**: 利用 CacheDependency「群組式」失效機制**  
1. 先把同一分類的快取物件，都與同一個「監控檔案」繫結 (`new CacheDependency(filePath)`)。  
2. 當需要整批移除時，只要 `File.SetLastWriteTime(filePath, DateTime.Now)` (或 touch 檔案)；ASP.NET 偵測到檔案變動後，會自動把所有依賴該檔案的 Cache 物件整批趕出去。  
3. 不需自行 enumerate 也不需再記任何 key。  

關鍵思考：  
把「群組相依」這件事交回給 ASP.NET 內建的依賴失效機制（Dependency-Based Invalidation），就能同時解決  
• 怎麼找到同一群物件  
• 如何在高併發下一次性清掉  
而不額外付出昂貴的字典掃描成本。

```csharp
// 寫入時
string depFile = HostingEnvironment.MapPath("~/App_Data/domain.columns.cache.flag");
var dep = new CacheDependency(depFile);
HttpRuntime.Cache.Insert("URL:https://columns.chicken-house.net/logo.jpg",
                         imageBytes,
                         dep,             // ← 關鍵
                         DateTime.Now.AddHours(1),
                         Cache.NoSlidingExpiration);

// 清空該群組時
File.SetLastWriteTime(depFile, DateTime.Now);   // 觸發 dependency, 整批失效
```

**Cases 1**:  
• 背景：大型企業後台系統需要「一鍵清除 staging domain 快取」以利 UI 測試。  
• 作法：把所有 `staging.company.com` 產生的 cache item 全綁 `~/App_Data/staging.flag`。測試人員按「清除 staging cache」即觸發 touch 檔案。  
• 效益：清除時間從原本的 5–10 秒字典掃描 => < 100ms，且程式碼僅 1 行。

**Cases 2**:  
• 背景：圖片伺服器每日有批次替換，同時有大量頁面引用 `image/jpeg`。  
• 作法：所有 image/jpeg cache 綁 `~/App_Data/jpeg.flag`。  
• 效益：每日批次只需 touch 檔案即可同步全部前端快取，無需迴圈刪 key，部署腳本簡化 70% 以上。

**Cases 3**:  
• 背景：因安全考量，需要在 SSL 憑證更新後，清掉所有 `https` 快取資源。  
• 作法：將 https 資料統一依賴 `~/App_Data/https.flag`，觸發即可。  
• 效益：憑證換發流程腳本自動執行 touch，避免使用者持續拿到舊內容；無需停站或重啟 IIS。