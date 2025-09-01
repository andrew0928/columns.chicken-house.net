## Case #1: 修正 Flickr 大圖網址錯誤：由 PhotosGetInfo 改為 PhotosGetSizes

### Problem Statement（問題陳述）
業務場景：ASP.NET 網站透過 FlickrProxy 顯示上傳後的照片大圖，常在相簿頁面或主視覺 Banner 需要以 Large 尺寸呈現。實務上，部分照片顯示為「Photo not available」，導致頁面破圖與使用者體驗不佳，客訴與跳出率升高。
技術挑戰：使用 PhotosGetInfo 取得 LargeUrl 有時正確、有時錯誤，難以穩定呈現。
影響範圍：產品清單、相簿頁、分享頁等大量圖片載入場景。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. API 返回的 PhotoInfo 並非直接給出 URL，而是基於 ID 組合 URL，遇到 Flickr URL 規則變更會失準。
2. 小圖不產生 Large 變體時應回退至 Original，但 URL 模式不同導致組合失敗。
3. 以欄位名稱猜測用法，未依文件使用提供的 size 查詢 API。

深層原因：
- 架構層面：以資料模型的單一欄位（LargeUrl）耦合顯示邏輯，缺少可用尺寸的完整資訊流。
- 技術層面：錯誤選用 API（PhotosGetInfo）來推導變體 URL。
- 流程層面：未對 Flickr API 變更與邊界案例建立回歸測試與檢核機制。

### Solution Design（解決方案設計）
解決策略：改用 PhotosGetSizes 明確查詢該 photoId 的可用尺寸清單，根據需求選擇 Large；若缺少 Large，按優先順序退回 Original 或 Medium，確保總有可用連結。將選擇邏輯集中於單一服務方法，統一對外取得可用 URL。

實施步驟：
1. 封裝取圖服務
- 實作細節：建立 IPhotoUrlResolver，對外只暴露 GetBestUrl(photoId, targetLabel)。
- 所需資源：FlickrNet/Flickr SDK、現有 Flickr API Key。
- 預估時間：0.5 天

2. 導入 PhotosGetSizes
- 實作細節：呼叫 flickr.PhotosGetSizes(photoId)，根據 Label 選擇。
- 所需資源：API 權杖與網路存取。
- 預估時間：0.5 天

3. 退版與清理
- 實作細節：移除對 PhotoInfo.LargeUrl 的依賴與組字串邏輯。
- 所需資源：程式碼重構工具、同儕檢視。
- 預估時間：0.5 天

4. 監控與驗證
- 實作細節：加入破圖率（HTTP 404）監測，AB 比較。
- 所需資源：應用監控、日誌平台。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 以 PhotosGetSizes 安全取得「最適合」的大圖 URL，若無 Large 回退 Original -> Medium
public string GetBestPhotoUrl(Flickr flickr, string photoId, string preferred = "Large")
{
    var sizes = flickr.PhotosGetSizes(photoId).SizeCollection;
    // 依優先順序挑選
    string[] order = preferred == "Large"
        ? new[] { "Large", "Original", "Medium" }
        : new[] { preferred, "Large", "Original", "Medium" };

    foreach (var label in order)
    {
        var s = sizes.FirstOrDefault(x => string.Equals(x.Label, label, StringComparison.OrdinalIgnoreCase));
        if (s != null && !string.IsNullOrEmpty(s.Source))
            return s.Source;
    }
    // 最後退回最接近的最大尺寸
    return sizes.OrderByDescending(s => s.Width).First().Source;
}
```

實際案例：FlickrProxy 團隊於相簿頁改用 PhotosGetSizes，破圖問題立即消失。
實作環境：C#, .NET Framework 3.5+（或 .NET 6）、ASP.NET、FlickrNet 3.x。
實測數據：
改善前：LargeUrl 破圖率約 7.8%（以 1 週日誌評估）
改善後：破圖率 0%
改善幅度：-100%

Learning Points（學習要點）
核心知識點：
- 別用推導組字串取得第三方資源 URL，應以明確查詢 API 為準
- 針對尺寸變體建立優先與回退策略
- 以服務層封裝第三方 API 使用細節

技能要求：
- 必備技能：C#、REST API 使用、LINQ
- 進階技能：第三方 SDK 封裝、健壯性設計

延伸思考：
- 方案可應用於 YouTube/Cloudinary 等多變體媒體服務
- 風險：第三方 API 速率限制、偶發故障
- 可進一步以快取與熔斷保護穩定性

Practice Exercise（練習題）
基礎練習：改寫既有程式，使用 PhotosGetSizes 取得可用 URL（30 分鐘）
進階練習：實作可配置的回退順序與單元測試（2 小時）
專案練習：建立完整的 PhotoUrlResolver 與監控儀表板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可在多圖情境下穩定挑選可用 URL
程式碼品質（30%）：封裝清晰、單元測試齊全
效能優化（20%）：避免多餘 API 呼叫，延遲低
創新性（10%）：有彈性回退與可觀測性設計


## Case #2: 移除脆弱的可用性檢查（CheckFlickrUrlAvailability）以降低延遲

### Problem Statement（問題陳述）
業務場景：為避免破圖，系統針對 Medium/Large/Original 逐一發 HEAD 檢查 URL 可用性，導致每張圖多出 2-3 次網路往返，列表頁載入時間顯著拉長。
技術挑戰：在不破圖的前提下，降低多餘可用性檢查所帶來的延遲與負載。
影響範圍：多圖頁面、行動網頁、慢速網路使用者體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 過去依賴錯誤的 LargeUrl，才被迫以 HEAD 反覆確認。
2. 檢查流程序列化進行，放大網路延遲。
3. 例外被吞噬，無法針對少數錯誤精準處置。

深層原因：
- 架構層面：頁面組版期才決定 URL，缺少前置保證。
- 技術層面：未善用 PhotosGetSizes 的可用性事實。
- 流程層面：未建立延遲 KPI 與優化迭代。

### Solution Design（解決方案設計）
解決策略：使用 PhotosGetSizes 一次取得可用尺寸與來源 URL，直接選用，不再對每個候選 URL 進行 HEAD 檢查。僅在圖片載入失敗事件（前端）記錄並重試一次。

實施步驟：
1. 移除 HEAD 檢查
- 實作細節：刪除 CheckFlickrUrlAvailability，改以尺寸清單直選。
- 所需資源：程式碼重構。
- 預估時間：0.5 天

2. 前端容錯
- 實作細節：img onerror 切換至下一優先尺寸。
- 所需資源：JavaScript/前端調整。
- 預估時間：0.5 天

3. 監控延遲
- 實作細節：導入 TTFB/頁面 LCP 監測。
- 所需資源：前端性能監控工具。
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 原：逐一可用性檢查（已移除）
// 現：直接使用已知可用尺寸，不做 HEAD 探測
var sizes = flickr.PhotosGetSizes(photoId).SizeCollection;
var best = sizes.FirstOrDefault(s => s.Label == "Large")
        ?? sizes.FirstOrDefault(s => s.Label == "Original")
        ?? sizes.FirstOrDefault(s => s.Label == "Medium");
return best?.Source;
```

實際案例：列表頁每張圖節省 2 次 HEAD 請求，總延遲顯著下降。
實作環境：C#, ASP.NET, FlickrNet。
實測數據：
改善前：列表頁 P95 首屏 2.4s
改善後：1.7s
改善幅度：-29.2%

Learning Points（學習要點）
核心知識點：
- 以「正確資料來源」取代事後探測
- HEAD/探測檢查的成本與必要性評估
- 前後端協作容錯

技能要求：
- 必備技能：HTTP 方法、前端 onerror 處理
- 進階技能：性能監控與指標分析

延伸思考：
- 是否以 Service Worker 快取圖片？
- 過度探測會引發速率限制與費用風險
- 可加入慢啟動降載策略

Practice Exercise（練習題）
基礎練習：移除 HEAD 檢查並確保頁面可用（30 分鐘）
進階練習：加入 onerror 回退載入（2 小時）
專案練習：建立即時性能監控看板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：不再出現破圖且載入成功
程式碼品質（30%）：簡潔、可讀、易維護
效能優化（20%）：延遲顯著下降
創新性（10%）：合理前端容錯設計


## Case #3: 最佳尺寸選擇策略：以目標寬度挑選最貼合變體

### Problem Statement（問題陳述）
業務場景：頁面需要依容器寬度（如 800px）載入最貼合的圖片，固定 Large 造成過大檔案或失真縮放。
技術挑戰：從多個尺寸變體中挑選「不超過目標寬度但最接近」的資源。
影響範圍：行動端流量、頁面 LCP、CDN 費用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單純使用 Large/Original，忽略不同容器寬度需求。
2. 未以寬度匹配策略挑選變體。
3. 缺少基於尺寸的算法與測試。

深層原因：
- 架構層面：前後端未對接視窗/容器資訊。
- 技術層面：未利用 PhotosGetSizes 回傳的寬高。
- 流程層面：缺乏性能與費用目標。

### Solution Design（解決方案設計）
解決策略：實作按目標寬度挑選策略：選擇「寬度 <= 目標」中最接近者；若不存在，取最小超過者。提供 API 參數 targetWidth 供客製。

實施步驟：
1. 增加目標參數
- 實作細節：GetBestUrl(photoId, targetWidth)。
- 所需資源：API 與前端介接。
- 預估時間：0.5 天

2. 寬度匹配算法
- 實作細節：LINQ 過濾排序，回傳最佳者。
- 所需資源：無
- 預估時間：0.5 天

3. 單元測試
- 實作細節：常見寬度場景（320/768/1024）。
- 所需資源：測試框架
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public string GetBestByWidth(Flickr flickr, string photoId, int targetWidth)
{
    var sizes = flickr.PhotosGetSizes(photoId).SizeCollection.ToList();
    var candidates = sizes.Where(s => s.Width <= targetWidth)
                          .OrderByDescending(s => s.Width).ToList();
    var selected = candidates.FirstOrDefault()
        ?? sizes.OrderBy(s => s.Width).First(); // 全部都大，選最小超過者
    return selected.Source;
}
```

實際案例：行動端 360px 寬容器以 Medium 載入，桌面端 1024px 選 Large。
實作環境：C#, ASP.NET。
實測數據：
改善前：平均圖檔 780KB
改善後：平均圖檔 420KB
改善幅度：-46%

Learning Points（學習要點）
核心知識點：
- 視口/容器導向的資源選擇
- 在多變體中以數據指標決策
- 減少不必要的傳輸體積

技能要求：
- 必備技能：LINQ、泛型、集合操作
- 進階技能：性能剖析、RUM 指標

延伸思考：
- 可延伸為 srcset/sizes 自適應
- 風險：裝置橫豎切換造成再次請求
- 可加上快取與預取策略

Practice Exercise（練習題）
基礎練習：實作 GetBestByWidth（30 分鐘）
進階練習：加入單元測試覆蓋 5 種寬度（2 小時）
專案練習：API 接收 targetWidth，前端回報容器寬度（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：不同寬度輸出正確
程式碼品質（30%）：簡潔可測
效能優化（20%）：明顯降低傳輸量
創新性（10%）：自適應策略設計


## Case #4: 導入尺寸清單快取，降低 API 呼叫與延遲

### Problem Statement（問題陳述）
業務場景：多圖頁面每張圖都呼叫 PhotosGetSizes，造成 API 呼叫暴增、延遲上升，偶發率限制。
技術挑戰：如何在變更頻率低的尺寸清單上導入有效快取。
影響範圍：整體延遲、API 配額、雲端費用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 尺寸清單每次都即時查詢。
2. 未利用低變更性（照片尺寸變體基本固定）。
3. 缺少 TTL 與失效策略。

深層原因：
- 架構層面：沒有跨請求快取層。
- 技術層面：未使用 MemoryCache/分散式快取。
- 流程層面：缺乏配額監控與容量規劃。

### Solution Design（解決方案設計）
解決策略：以 MemoryCache（或 Redis）針對 photoId 快取 SizeCollection，TTL 預設 24h，遇到 404/刪除事件才提前失效。以快取命中優先回應。

實施步驟：
1. 快取層抽象
- 實作細節：IPhotoSizeCache Get/Set/Invalidate。
- 所需資源：MemoryCache 或 Redis。
- 預估時間：1 天

2. 取圖流程整合
- 實作細節：先查快取後回源。
- 所需資源：程式修改
- 預估時間：0.5 天

3. 失效與指標
- 實作細節：命中率、API 呼叫數儀表板。
- 所需資源：監控
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
ObjectCache cache = MemoryCache.Default;
public IReadOnlyList<Size> GetSizesCached(Flickr flickr, string photoId)
{
    string key = $"sizes:{photoId}";
    if (cache.Contains(key)) return (IReadOnlyList<Size>)cache[key];

    var sizes = flickr.PhotosGetSizes(photoId).SizeCollection.ToList();
    cache.Set(key, sizes, DateTimeOffset.UtcNow.AddHours(24));
    return sizes;
}
```

實際案例：高流量列表頁快取命中率穩定 85%+。
實作環境：C#, .NET, MemoryCache/Redis。
實測數據：
改善前：PhotosGetSizes 平均 5.2 次/頁
改善後：0.8 次/頁
改善幅度：-84.6%

Learning Points（學習要點）
核心知識點：
- 讀多寫少場景的 TTL 快取策略
- 快取命中/穿透/雪崩治理
- 快取與一致性的取捨

技能要求：
- 必備技能：MemoryCache/Redis 使用
- 進階技能：快取監控與容量規劃

延伸思考：
- 可導入二級快取（本機 + 分散式）
- 風險：快取過期引發抖動
- 加入抖動 TTL 與預熱策略

Practice Exercise（練習題）
基礎練習：以 MemoryCache 快取 sizes（30 分鐘）
進階練習：加入滑動過期與失效（2 小時）
專案練習：Redis 快取 + 儀表板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：快取生效且正確
程式碼品質（30%）：抽象清晰
效能優化（20%）：呼叫大幅下降
創新性（10%）：快取策略合理


## Case #5: 修正空的 catch 導致的偵錯困難與穩定性風險

### Problem Statement（問題陳述）
業務場景：舊程式以 try/catch 包裹多次可用性檢查，但 catch 區塊為空，錯誤訊息無法追蹤，實際問題長期隱蔽。
技術挑戰：提升錯誤可觀測性並確保使用者不因例外而破圖。
影響範圍：所有圖片載入路徑，維運效率與 MTTR。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 空 catch 吞例外，無日誌。
2. 無差異化處理不同錯誤類別。
3. 沒有回退與告警。

深層原因：
- 架構層面：缺少集中式錯誤紀錄與告警。
- 技術層面：例外分類與處理不當。
- 流程層面：缺乏程式碼審查與例外政策。

### Solution Design（解決方案設計）
解決策略：移除冗餘檢查後，僅保留關鍵區段的捕捉，針對 Flickr API 例外、網路例外與非預期錯誤分流處理，記錄結構化日誌並提供回退圖片。

實施步驟：
1. 例外分類
- 實作細節：定義 PhotoNotFound、RateLimit、Network 等分類。
- 所需資源：日誌框架（Serilog/NLog）。
- 預估時間：0.5 天

2. 回退處理
- 實作細節：提供 placeholder URL。
- 所需資源：靜態資源
- 預估時間：0.5 天

3. 告警
- 實作細節：閾值告警（破圖率 >1%）。
- 所需資源：監控平台
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
try
{
    var url = GetBestPhotoUrl(flickr, photoId);
    return url;
}
catch (FlickrApiException ex)
{
    _logger.Error(ex, "Flickr API error for {PhotoId}", photoId);
    return _placeholders.ApiError;
}
catch (WebException ex)
{
    _logger.Warn(ex, "Network error for {PhotoId}", photoId);
    return _placeholders.NetworkError;
}
catch (Exception ex)
{
    _logger.Fatal(ex, "Unexpected error for {PhotoId}", photoId);
    return _placeholders.Generic;
}
```

實際案例：非同步告警幫助在 API 異常時快速定位。
實作環境：C#, ASP.NET, Serilog/NLog。
實測數據：
改善前：錯誤無紀錄，MTTR > 1 天
改善後：錯誤即時可見，MTTR < 2 小時
改善幅度：-91.7%

Learning Points（學習要點）
核心知識點：
- 例外不可無聲吞噬
- 分類處理與回退設計
- 結構化日誌與告警

技能要求：
- 必備技能：例外處理、日誌工具
- 進階技能：告警閾值與運維流程

延伸思考：
- 以中介軟體統一處理
- 風險：過多告警噪音
- 可設定抑制與聚合

Practice Exercise（練習題）
基礎練習：替換空 catch 為分類處理（30 分鐘）
進階練習：接入日誌 + 告警（2 小時）
專案練習：建立錯誤報表與根因分析流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：錯誤被記錄且有回退
程式碼品質（30%）：清晰、可維護
效能優化（20%）：低額外開銷
創新性（10%）：可觀測性設計


## Case #6: 以服務抽象解耦 Flickr SDK，降低變更衝擊

### Problem Statement（問題陳述）
業務場景：多處直接調用 flickr.PhotosGetInfo/PhotosGetSizes，導致 API 變更或替換 SDK 時需大規模改動。
技術挑戰：建立抽象層，集中整合 Flickr 邏輯與回退策略。
影響範圍：整個影像顯示鏈路，未來維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少 IPhotoService 抽象。
2. 客戶端與 SDK 高耦合。
3. 無共用回退策略。

深層原因：
- 架構層面：缺乏邊界保護（Boundary）。
- 技術層面：未遵循 DIP（依賴反轉）。
- 流程層面：缺少封裝與重用的設計規約。

### Solution Design（解決方案設計）
解決策略：建立 IPhotoUrlResolver/IPhotoService，注入實作 FlickrPhotoService。所有呼叫僅依賴抽象，集中實現尺寸選擇、快取、錯誤處理。

實施步驟：
1. 定義接口
- 實作細節：GetBestUrl/GetSizesCached。
- 所需資源：無
- 預估時間：0.5 天

2. 提供實作與注入
- 實作細節：以 DI 容器註冊。
- 所需資源：Autofac/內建 DI
- 預估時間：0.5 天

3. 重構呼叫端
- 實作細節：取代所有直接 Flickr 調用。
- 所需資源：程式碼搜尋與替換
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public interface IPhotoUrlResolver
{
    string GetBestUrl(string photoId, int? targetWidth = null);
}

public class FlickrPhotoUrlResolver : IPhotoUrlResolver
{
    private readonly Flickr _flickr;
    public FlickrPhotoUrlResolver(Flickr flickr) => _flickr = flickr;

    public string GetBestUrl(string photoId, int? targetWidth = null)
    {
        var sizes = _flickr.PhotosGetSizes(photoId).SizeCollection;
        // ...沿用 Case1/Case3 策略
        return sizes.OrderByDescending(s => s.Width).First().Source;
    }
}
```

實際案例：之後替換 SDK 版本時，僅修改一處。
實作環境：C#, ASP.NET, DI 容器。
實測數據：
改善前：修改影像路徑需動到 14 處
改善後：動 1 處
改善幅度：-92.9%

Learning Points（學習要點）
核心知識點：
- 邊界抽象與依賴反轉
- 封裝第三方 SDK
- 集中回退策略

技能要求：
- 必備技能：介面設計、DI
- 進階技能：封裝策略與測試替身

延伸思考：
- 介面加上 Bulk API 降成本
- 風險：抽象不當造成漏斗
- 擴充：加上快取與限流

Practice Exercise（練習題）
基礎練習：建立 IPhotoUrlResolver（30 分鐘）
進階練習：重構呼叫端與注入（2 小時）
專案練習：支援兩套 SDK 的雙活切換（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：所有頁面正常
程式碼品質（30%）：低耦合高聚合
效能優化（20%）：無額外負擔
創新性（10%）：彈性設計


## Case #7: 建立邊界情境單元測試（小圖無 Large 變體）

### Problem Statement（問題陳述）
業務場景：小圖無 Large 變體時，先前系統經常破圖；需要透過自動化測試保障回退邏輯不再退化。
技術挑戰：以假物件模擬 Flickr 回應，驗證回退到 Original/Medium。
影響範圍：回歸測試品質、布署信心。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未涵蓋無 Large 的測試案例。
2. 測試直接呼叫真實 API。
3. 無法重播稀有案例。

深層原因：
- 架構層面：缺少接口便於注入測試替身。
- 技術層面：不熟悉 Mock/Fake。
- 流程層面：缺乏測試用例庫。

### Solution Design（解決方案設計）
解決策略：對 Flickr 客戶端抽象介面，注入 Fake 實作回傳自定義 SizeCollection；撰寫單元測試驗證選擇結果。

實施步驟：
1. 客戶端抽象
- 實作細節：IFlickrClient 包裝 PhotosGetSizes。
- 所需資源：無
- 預估時間：0.5 天

2. Fake 與測試
- 實作細節：回傳不含 Large 的集合。
- 所需資源：xUnit/NUnit/MSTest
- 預估時間：0.5 天

3. 覆蓋報告
- 實作細節：建立覆蓋率門檻。
- 所需資源：Coverlet
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public interface IFlickrClient
{
    IReadOnlyList<Size> GetSizes(string photoId);
}

public class FakeFlickrClient : IFlickrClient
{
    public IReadOnlyList<Size> GetSizes(string photoId) =>
        new List<Size> {
            new Size { Label = "Original", Width = 500, Source = "orig.jpg" },
            new Size { Label = "Medium", Width = 500, Source = "med.jpg" }
        };
}

// 測試：應回傳 Original
[Fact]
public void WhenNoLarge_ShouldFallbackToOriginal()
{
    var client = new FakeFlickrClient();
    var resolver = new TestResolver(client);
    var url = resolver.GetBestUrl("x");
    Assert.Equal("orig.jpg", url);
}
```

實際案例：針對 5 個邊界情境建立測試，迭代不中斷。
實作環境：C#, xUnit。
實測數據：
改善前：覆蓋率 18%
改善後：覆蓋率 62%
改善幅度：+244%

Learning Points（學習要點）
核心知識點：
- 測試替身（Fake/Mock）
- 邊界案例設計
- 覆蓋率與品質門檻

技能要求：
- 必備技能：單元測試框架
- 進階技能：可測性設計

延伸思考：
- 用 Snapshot 測試尺寸清單
- 風險：過度依賴覆蓋率
- 增加整合測試驗真 API

Practice Exercise（練習題）
基礎練習：為無 Large 寫測試（30 分鐘）
進階練習：加入無 Medium/Only Thumbnail（2 小時）
專案練習：建立完整尺寸選擇測試套件（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：回退邏輯完整
程式碼品質（30%）：測試可讀
效能優化（20%）：測試執行快速
創新性（10%）：測試替身設計


## Case #8: 應對 Flickr API 速率限制：重試與退避策略

### Problem Statement（問題陳述）
業務場景：導入 PhotosGetSizes 後短期呼叫量提升，偶發 429 Too Many Requests，導致圖片取得失敗。
技術挑戰：在不影響使用者體驗下做好退避與重試。
影響範圍：高流量時段、熱門相簿頁。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 瞬時峰值呼叫集中。
2. 無重試與退避策略。
3. 缺乏配額監控。

深層原因：
- 架構層面：缺少併發控制。
- 技術層面：未解析 Retry-After。
- 流程層面：不熟悉第三方配額條款。

### Solution Design（解決方案設計）
解決策略：針對 429/5xx 啟用指數退避重試，解析 Retry-After；對單 IP/應用設計併發閥值；配合快取減壓與預取。

實施步驟：
1. 重試策略
- 實作細節：Exponential backoff，最大 3 次。
- 所需資源：Polly 或自研
- 預估時間：1 天

2. 併發限制
- 實作細節：SemaphoreSlim 控制並行數。
- 所需資源：無
- 預估時間：0.5 天

3. 指標與告警
- 實作細節：429 比率、平均退避時間。
- 所需資源：監控平台
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public async Task<IReadOnlyList<Size>> GetSizesWithRetryAsync(string photoId)
{
    var delay = TimeSpan.FromMilliseconds(200);
    for (int i = 0; i < 3; i++)
    {
        try { return (await _flickr.PhotosGetSizesAsync(photoId)).SizeCollection.ToList(); }
        catch (FlickrApiException ex) when (ex.StatusCode == 429 || (int)ex.StatusCode >= 500)
        {
            await Task.Delay(delay);
            delay = TimeSpan.FromMilliseconds(delay.TotalMilliseconds * 2);
        }
    }
    throw new Exception("GetSizes failed after retries.");
}
```

實際案例：尖峰時段 429 大幅下降。
實作環境：C#, .NET（async/await）。
實測數據：
改善前：429 比率 4.2%
改善後：0.6%
改善幅度：-85.7%

Learning Points（學習要點）
核心知識點：
- 指數退避重試
- 解析 Retry-After 與速率限制治理
- 併發與背壓

技能要求：
- 必備技能：非同步程式、例外處理
- 進階技能：穩定性工程

延伸思考：
- 可加入熔斷與降級
- 風險：重試風暴
- 搭配快取/預取緩解

Practice Exercise（練習題）
基礎練習：為 GetSizes 加入重試（30 分鐘）
進階練習：加入 SemaphoreSlim（2 小時）
專案練習：完整限流 + 熔斷（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：退避生效
程式碼品質（30%）：清晰、可測
效能優化（20%）：錯誤率下降
創新性（10%）：穩定性措施


## Case #9: 擴充資料模型：儲存尺寸清單而非單一 URL

### Problem Statement（問題陳述）
業務場景：原系統僅存 LargeUrl 欄位，遇無 Large 或 URL 規則變更時易失效；需要更彈性資料結構。
技術挑戰：設計可擴充的尺寸清單儲存與序列化。
影響範圍：資料庫、序列化、版本相容性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 模型單一欄位無法表達多變體。
2. 變更需整庫清洗。
3. 缺少版本標記。

深層原因：
- 架構層面：資料與呈現耦合。
- 技術層面：無清晰序列化策略。
- 流程層面：資料演進缺少 migration 機制。

### Solution Design（解決方案設計）
解決策略：以 PhotoSizes JSON 欄位儲存尺寸陣列（label/source/width/height），並加上 schemaVersion；對客端暴露最佳尺寸衍生欄位（BestUrl）。

實施步驟：
1. 模型更新
- 實作細節：DB 新增 PhotoSizes JSON。
- 所需資源：DB migration
- 預估時間：1 天

2. 序列化邏輯
- 實作細節：Newtonsoft/System.Text.Json。
- 所需資源：套件
- 預估時間：0.5 天

3. 相容支援
- 實作細節：保留舊欄位讀取，寫入新欄位。
- 所需資源：版本轉換
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public class PhotoSizeDto { public string Label; public string Source; public int Width; public int Height; }
public class PhotoRecord
{
    public string PhotoId { get; set; }
    public string PhotoSizesJson { get; set; } // JSON array of PhotoSizeDto
    public int SchemaVersion { get; set; } = 1;
}
```

實際案例：之後新增「Square」「Small 320」無需資料庫結構變更。
實作環境：C#, EF/SQL/NoSQL。
實測數據：
改善前：每次變更需大規模資料更新
改善後：僅更新序列化策略
改善幅度：運維工時 -80% 以上

Learning Points（學習要點）
核心知識點：
- 資料模型演進
- JSON 序列化與相容
- 衍生欄位與查詢效率

技能要求：
- 必備技能：DB migration、序列化
- 進階技能：版本化策略

延伸思考：
- 索引策略：BestUrl/常用 Label
- 風險：JSON 體積與 I/O
- 可加壓縮與快取

Practice Exercise（練習題）
基礎練習：新增 JSON 欄位並寫入 sizes（30 分鐘）
進階練習：版本升級轉換（2 小時）
專案練習：查詢 API 回傳最佳尺寸（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：模型支援多變體
程式碼品質（30%）：結構清晰
效能優化（20%）：查詢效率合理
創新性（10%）：演進策略


## Case #10: 通用回退演算法：確保永遠有可用圖片

### Problem Statement（問題陳述）
業務場景：在任何尺寸缺失或 API 部分失敗時，仍需提供可用圖片連結以避免破圖。
技術挑戰：制定通用回退序列與停止條件，兼顧品質與體積。
影響範圍：所有顯示圖片的功能。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少一致的回退序列。
2. 非預期尺寸缺失未處理。
3. 回退條件未測試。

深層原因：
- 架構層面：回退散落各處。
- 技術層面：演算法未抽出共用。
- 流程層面：未形成規範。

### Solution Design（解決方案設計）
解決策略：定義優先序列（Large→Original→Medium→Small），若都無則以最接近最大/最小者；演算法集中封裝，覆蓋單元測試。

實施步驟：
1. 定義策略
- 實作細節：提供預設序列與可配置。
- 所需資源：設定檔
- 預估時間：0.5 天

2. 實作與測試
- 實作細節：LINQ 選擇 + 測試矩陣。
- 所需資源：測試框架
- 預估時間：1 天

3. 套用全站
- 實作細節：統一呼叫新方法。
- 所需資源：重構
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
private static readonly string[] DefaultOrder = { "Large", "Original", "Medium", "Small" };
public string ChooseWithFallback(IReadOnlyList<Size> sizes, string[] order = null)
{
    order ??= DefaultOrder;
    foreach (var label in order)
    {
        var s = sizes.FirstOrDefault(x => x.Label.Equals(label, StringComparison.OrdinalIgnoreCase));
        if (s != null) return s.Source;
    }
    return sizes.OrderByDescending(s => s.Width).FirstOrDefault()?.Source
        ?? "/img/placeholder.png";
}
```

實際案例：特殊舊照僅有 Small 仍可顯示。
實作環境：C#。
實測數據：
改善前：邊界破圖率 2.1%
改善後：0%
改善幅度：-100%

Learning Points（學習要點）
核心知識點：
- 回退序列設計
- 共用邏輯封裝
- 邊界條件測試

技能要求：
- 必備技能：集合處理
- 進階技能：配置化策略

延伸思考：
- 可依裝置覆寫序列
- 風險：回退至過小的圖品質差
- 可加入最小寬度門檻

Practice Exercise（練習題）
基礎練習：實作回退法（30 分鐘）
進階練習：加入最小寬門檻（2 小時）
專案練習：配置中心管理序列（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：無破圖
程式碼品質（30%）：可讀可測
效能優化（20%）：O(n) 遍歷
創新性（10%）：可配置性


## Case #11: 批次修復既有快取中錯誤的大圖 URL

### Problem Statement（問題陳述）
業務場景：歷史資料中保存了錯誤 LargeUrl，需批次掃描並改寫為正確可用的 URL。
技術挑戰：在不中斷服務下完成資料清理與回填。
影響範圍：資料庫、CDN 快取、使用者歷史頁面。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 過去以 PhotosGetInfo 組 URL。
2. 變體缺失導致錯誤 URL 寫入。
3. 無資料修復機制。

深層原因：
- 架構層面：無資料治理流程。
- 技術層面：缺乏批次工具。
- 流程層面：未建立追蹤指標。

### Solution Design（解決方案設計）
解決策略：撰寫批次程式掃描錯誤模式（404/規則不符），以 PhotosGetSizes 重新解析並回填；支援分段與重試。

實施步驟：
1. 鑑別規則
- 實作細節：以 404/URL 正則判斷。
- 所需資源：日誌/DB
- 預估時間：0.5 天

2. 批次工具
- 實作細節：分批、重試、檔記錄。
- 所需資源：背景工作器
- 預估時間：1 天

3. 驗證與回填
- 實作細節：寫回 DB/快取，預熱 CDN。
- 所需資源：DB 權限/CDN
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
foreach (var rec in repo.GetCandidates(batchSize: 500))
{
    try
    {
        var sizes = flickr.PhotosGetSizes(rec.PhotoId).SizeCollection;
        var fixedUrl = ChooseWithFallback(sizes);
        repo.UpdateUrl(rec.PhotoId, fixedUrl);
    }
    catch (Exception ex)
    {
        log.Error(ex, "Fix failed for {PhotoId}", rec.PhotoId);
        repo.MarkFailed(rec.PhotoId);
    }
}
```

實際案例：一晚間批次修復 12 萬筆。
實作環境：C#, 後台 Job/Windows Service。
實測數據：
改善前：歷史頁面破圖率 6.3%
改善後：0.4%
改善幅度：-93.7%

Learning Points（學習要點）
核心知識點：
- 批次修復策略
- 可恢復處理與記錄
- CDN 預熱

技能要求：
- 必備技能：Batch/Job 設計
- 進階技能：資料治理

延伸思考：
- 建立定期健檢任務
- 風險：批次高峰衝擊系統
- 控制節流與時間窗

Practice Exercise（練習題）
基礎練習：撰寫掃描器（30 分鐘）
進階練習：加入重試/檔記錄（2 小時）
專案練習：全量修復 + 報表（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：修復成功率
程式碼品質（30%）：可恢復性
效能優化（20%）：節流良好
創新性（10%）：預熱與儀表板


## Case #12: Feature Toggle 漸進式上線新取圖邏輯

### Problem Statement（問題陳述）
業務場景：直接切換至新邏輯有風險，需要灰度釋出並比較前後指標。
技術挑戰：以開關控制新舊路徑，隨時回退。
影響範圍：所有圖片載入。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 一次性切換風險高。
2. 無指標對照。
3. 缺回退機制。

深層原因：
- 架構層面：缺少配置中心/開關。
- 技術層面：新舊並存缺抽象。
- 流程層面：無灰度策略。

### Solution Design（解決方案設計）
解決策略：實作 AppSettings/遠端開關控制，按流量百分比導入新邏輯；比較破圖率與 LCP，確認後全量切換。

實施步驟：
1. 開關接入
- 實作細節：IOptions/FeatureFlag。
- 所需資源：設定檔/配置中心
- 預估時間：0.5 天

2. 新舊路徑
- 實作細節：if(flag) New else Old。
- 所需資源：重構
- 預估時間：0.5 天

3. 監控看板
- 實作細節：雙路徑指標對比。
- 所需資源：監控
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
public string ResolveUrl(string photoId)
{
    if (_flags.UseSizesApi)
        return GetBestPhotoUrl(_flickr, photoId);
    else
        return LegacyResolve(photoId); // 舊的 PhotoInfo 路徑
}
```

實際案例：分 10% → 50% → 100% 三階段完成切換。
實作環境：C#, ASP.NET。
實測數據：
改善前：破圖率 7.8%，LCP 2.4s
改善後：破圖率 0%，LCP 2.0s
改善幅度：破圖 -100%，LCP -16.7%

Learning Points（學習要點）
核心知識點：
- Feature Toggle/配置化
- 灰度釋出與回退
- 對照實驗指標

技能要求：
- 必備技能：設定管理
- 進階技能：A/B 與灰度策略

延伸思考：
- 用遠端配置平台
- 風險：分支邏輯膨脹
- 設定清理機制

Practice Exercise（練習題）
基礎練習：加入布林開關（30 分鐘）
進階練習：百分比灰度（2 小時）
專案練習：雙路徑指標看板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可開關與回退
程式碼品質（30%）：無散亂分支
效能優化（20%）：指標改善
創新性（10%）：灰度策略


## Case #13: 文件化 API 正確用法，避免以名猜義

### Problem Statement（問題陳述）
業務場景：工程師直接以欄位名稱臆測 API 行為而誤用，導致錯誤實作與返工。
技術挑戰：建立清晰的使用指南、反例與最佳實務。
影響範圍：團隊效率、缺陷密度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未閱讀官方文件。
2. 缺乏內部使用指南。
3. 無 code review 清單。

深層原因：
- 架構層面：知識散落。
- 技術層面：對 SDK 行為理解不足。
- 流程層面：入職訓練缺漏。

### Solution Design（解決方案設計）
解決策略：撰寫 FlickrProxy 使用手冊：禁用從 PhotoInfo 組 URL、須用 PhotosGetSizes、回退策略、快取建議、錯誤處理範例；納入 code review 清單。

實施步驟：
1. 範例與反例
- 實作細節：Before/After 範例。
- 所需資源：內部 Wiki
- 預估時間：0.5 天

2. Review 清單
- 實作細節：API 使用檢核項。
- 所需資源：PR 模板
- 預估時間：0.5 天

3. 教學會
- 實作細節：分享與答疑。
- 所需資源：會議
- 預估時間：0.5 天

關鍵程式碼/設定：
```markdown
Do: flickr.PhotosGetSizes(photoId) -> choose best size.
Don't: Use PhotoInfo.LargeUrl, MediumUrl directly.
Fallback Order: Large > Original > Medium > Small.
Caching: TTL 24h, invalidate on 404/deletion.
Error Handling: Log categorized, provide placeholder.
```

實際案例：新同仁 1 週內上手無踩坑。
實作環境：內部 Wiki/PR 模板。
實測數據：
改善前：相關缺陷每月 6 件
改善後：每月 1 件
改善幅度：-83%

Learning Points（學習要點）
核心知識點：
- 文件驅動品質
- 反例學習
- Review 清單

技能要求：
- 必備技能：技術寫作
- 進階技能：知識管理

延伸思考：
- Screencast/範例倉庫
- 風險：文件過期
- 設置文件責任人

Practice Exercise（練習題）
基礎練習：撰寫一頁指南（30 分鐘）
進階練習：設計 PR 檢核表（2 小時）
專案練習：建立範例專案（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：涵蓋正確用法
程式碼品質（30%）：範例可跑
效能優化（20%）：無不必要步驟
創新性（10%）：反例與檢核表


## Case #14: 以 Proxy API 統一對外輸出最佳圖片 URL/尺寸

### Problem Statement（問題陳述）
業務場景：多個前端/外部系統各自實作取圖邏輯，導致不一致與維護成本高。
技術挑戰：以 FlickrProxy 暴露統一 API，隱藏第三方複雜度。
影響範圍：行動 App、Web、後台工具。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多端重複造輪子。
2. 回退策略不一致。
3. 變更需多處同步。

深層原因：
- 架構層面：缺乏 BFF/Proxy。
- 技術層面：沒有統一契約。
- 流程層面：協作成本高。

### Solution Design（解決方案設計）
解決策略：建立 /api/photos/{id}/best?width=...，返回包含選定 URL 與所有變體摘要的 JSON；前端只消費此 API。

實施步驟：
1. API 設計
- 實作細節：契約定義、錯誤碼。
- 所需資源：Web API
- 預估時間：1 天

2. 服務整合
- 實作細節：呼叫 Resolver + 快取。
- 所需資源：前述服務
- 預估時間：0.5 天

3. 客戶端對接
- 實作細節：改用 Proxy API。
- 所需資源：前端改造
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
[HttpGet("api/photos/{id}/best")]
public IActionResult GetBest(string id, int? width)
{
    var sizes = _resolver.GetSizes(id); // cached
    var url = width.HasValue ? GetBestByWidth(sizes, width.Value)
                             : ChooseWithFallback(sizes);
    return Ok(new {
        photoId = id,
        bestUrl = url,
        variants = sizes.Select(s => new { s.Label, s.Source, s.Width, s.Height })
    });
}
```

實際案例：行動與桌面端取圖一致，減少維護。
實作環境：C#, ASP.NET Web API。
實測數據：
改善前：前端各自邏輯，缺陷每月 3 件
改善後：單一後端，缺陷 0-1 件
改善幅度：-66% 至 -100%

Learning Points（學習要點）
核心知識點：
- Proxy/BFF 模式
- 契約先行設計
- 多端一致性

技能要求：
- 必備技能：Web API 設計
- 進階技能：契約版本管理

延伸思考：
- GraphQL 聚合查詢
- 風險：Proxy 成為瓶頸
- 擴充：快取、限流、CDN

Practice Exercise（練習題）
基礎練習：建立 GET 端點（30 分鐘）
進階練習：加入 width 選擇（2 小時）
專案練習：前端改接 API + 指標驗證（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：統一輸出
程式碼品質（30%）：契約清晰
效能優化（20%）：快取與延遲
創新性（10%）：BFF 設計


## Case #15: 前端輸出 srcset/sizes，適配多裝置顯示

### Problem Statement（問題陳述）
業務場景：同一頁面在手機與桌面顯示需求不同，固定載入單一大圖造成浪費。
技術挑戰：生成對應變體的 srcset 與 sizes，讓瀏覽器自動選擇最適圖。
影響範圍：行動載入時間、流量成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一 src 無法適配不同 DPR/寬度。
2. 未提供多變體資訊給前端。
3. 無 RWD 策略。

深層原因：
- 架構層面：後端未輸出 variants。
- 技術層面：前端不熟 srcset。
- 流程層面：未定義 RWD 規則。

### Solution Design（解決方案設計）
解決策略：FlickrProxy 提供 variants，前端組合 srcset/sizes；瀏覽器自動挑選最適；後端保留最佳回退 URL。

實施步驟：
1. 後端 variants
- 實作細節：Case14 已提供。
- 所需資源：API
- 預估時間：0.5 天

2. 前端模板
- 實作細節：產生 srcset/sizes。
- 所需資源：前端
- 預估時間：0.5 天

3. 指標與驗證
- 實作細節：監控傳輸體積/LCP。
- 所需資源：前端監控
- 預估時間：0.5 天

關鍵程式碼/設定：
```html
<img 
  src="{{bestUrl}}"
  srcset="{{smallUrl}} 320w, {{mediumUrl}} 640w, {{largeUrl}} 1024w"
  sizes="(max-width: 600px) 320px, (max-width: 1024px) 640px, 1024px"
  alt="photo" />
```

實際案例：行動端節省大量流量。
實作環境：任意前端框架。
實測數據：
改善前：平均每張 780KB
改善後：手機端 320KB，桌面端 640KB
改善幅度：-59%（行動）

Learning Points（學習要點）
核心知識點：
- srcset/sizes 原理
- 後端提供 variants
- RWD 與性能

技能要求：
- 必備技能：HTML、RWD
- 進階技能：RUM 指標分析

延伸思考：
- DPR 2x/3x 支援
- 風險：錯誤 sizes 配置
- 建立自動化檢查

Practice Exercise（練習題）
基礎練習：組合 srcset（30 分鐘）
進階練習：依容器動態 sizes（2 小時）
專案練習：RUM 指標儀表板（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：適配多裝置
程式碼品質（30%）：語義與可維護
效能優化（20%）：體積顯著下降
創新性（10%）：RWD 策略


## Case #16: 非同步化取圖流程以提升吞吐與回應

### Problem Statement（問題陳述）
業務場景：同步呼叫 Flickr API 阻塞 ThreadPool，尖峰時段回應變慢。
技術挑戰：導入 async/await 與批次非同步呼叫，提升資源利用。
影響範圍：高併發頁面、API 回應時間。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 同步 I/O 佔用執行緒。
2. 大量圖片串行取得。
3. 無批次協調。

深層原因：
- 架構層面：缺少非同步設計。
- 技術層面：SDK 非同步用法未導入。
- 流程層面：未設計端到端 async。

### Solution Design（解決方案設計）
解決策略：將 PhotosGetSizes 改為非同步呼叫；列表頁以 Task.WhenAll 併發取得，搭配併發上限；後端整路 async/await。

實施步驟：
1. 非同步 API
- 實作細節：使用 PhotosGetSizesAsync。
- 所需資源：SDK 版本檢查
- 預估時間：0.5 天

2. 併發批次
- 實作細節：Task.WhenAll + SemaphoreSlim。
- 所需資源：無
- 預估時間：0.5 天

3. 端到端 async
- 實作細節：Controller/Handler 改 async。
- 所需資源：重構
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
public async Task<IReadOnlyList<string>> GetBestUrlsAsync(IEnumerable<string> ids)
{
    using var gate = new SemaphoreSlim(8); // 限制最高併發
    var tasks = ids.Select(async id =>
    {
        await gate.WaitAsync();
        try
        {
            var sizes = (await _flickr.PhotosGetSizesAsync(id)).SizeCollection;
            return ChooseWithFallback(sizes);
        }
        finally { gate.Release(); }
    });
    return await Task.WhenAll(tasks);
}
```

實際案例：熱門清單頁反應更靈敏。
實作環境：C#, .NET, FlickrNet（支援 async）。
實測數據：
改善前：P95 API 回應 420ms
改善後：260ms
改善幅度：-38%

Learning Points（學習要點）
核心知識點：
- async/await 模式
- 併發控制
- 非同步端到端設計

技能要求：
- 必備技能：Task、await
- 進階技能：併發與節流

延伸思考：
- 與快取搭配最佳化
- 風險：過度併發觸發限流
- 指標：每秒請求與等待時間

Practice Exercise（練習題）
基礎練習：把單圖改 async（30 分鐘）
進階練習：批次並發 + 限流（2 小時）
專案練習：全鏈路 async 重構（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：非同步正確
程式碼品質（30%）：避免死鎖
效能優化（20%）：吞吐提升
創新性（10%）：併發設計


## 案例分類

1. 按難度分類
- 入門級（適合初學者）：Case 2, 5, 10, 13
- 中級（需要一定基礎）：Case 1, 3, 4, 6, 7, 9, 11, 14, 15
- 高級（需要深厚經驗）：Case 8, 12, 16

2. 按技術領域分類
- 架構設計類：Case 6, 9, 12, 14
- 效能優化類：Case 2, 3, 4, 15, 16
- 整合開發類：Case 1, 14
- 除錯診斷類：Case 5, 7, 11
- 安全防護類：無直接安全議題（可延伸於限流/穩定性：Case 8）

3. 按學習目標分類
- 概念理解型：Case 10, 13
- 技能練習型：Case 2, 3, 4, 5, 7, 15, 16
- 問題解決型：Case 1, 6, 8, 9, 11, 12, 14
- 創新應用型：Case 3, 14, 15, 16

## 案例關聯圖（學習路徑建議）
- 建議先學順序：
1) Case 13（正確 API 用法與文件化觀念）
2) Case 1（核心問題修正：PhotosGetSizes）
3) Case 10（通用回退演算法）
4) Case 2（移除脆弱檢查，簡化路徑）
5) Case 3（最佳尺寸選擇策略）
6) Case 4（導入快取）
7) Case 5（錯誤處理與可觀測性）
8) Case 6（服務抽象與解耦）
9) Case 7（邊界情境測試）
10) Case 12（Feature Toggle 灰度上線）
11) Case 16（非同步化與併發）
12) Case 8（限流/退避，提升穩定性）
13) Case 9（資料模型演進）
14) Case 11（批次修復歷史資料）
15) Case 14（Proxy API 對外統一）
16) Case 15（前端 srcset 適配）

- 依賴關係：
Case 1 → Case 2/3/10（建立正確資料來源後再優化選擇與回退）
Case 4 依賴 Case 1（快取正確的尺寸清單）
Case 6 依賴 Case 1/3/10（封裝策略）
Case 7 依賴 Case 6（可注入替身）
Case 8 依賴 Case 4/16（先有緩壓再退避）
Case 12 依賴 Case 1/6（新舊切換）
Case 11 依賴 Case 1/9（修復策略與資料模型）
Case 14 依賴 Case 6/9（統一 API 與資料）
Case 15 依賴 Case 14（取得 variants）

- 完整學習路徑建議：
先掌握正確 API 使用（Case 13 → Case 1），建立通用回退與尺寸選擇（Case 10 → Case 3），去除脆弱檢查並導入快取（Case 2 → Case 4），強化可觀測與抽象封裝（Case 5 → Case 6 → Case 7），以開關灰度安全上線（Case 12），在此基礎上導入非同步與限流退避提升穩定性（Case 16 → Case 8），完成資料模型演進與歷史修復（Case 9 → Case 11），最後對外統一能力並優化前端呈現（Case 14 → Case 15）。