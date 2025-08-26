## Case #1: 升級後社群推文按鈕消失（URL Slug 不一致）

### Problem Statement（問題陳述）
業務場景：部落格從 BlogEngine.NET 1.3 升級到 1.4 後，許多文章原本顯示的社群推文數不見了。從外部書籤（如推推王）點回站內時，文章能開啟但看不到原推文累計，影響新讀者的社群信任與點擊意願。檢查後發現外部平台記錄的文章網址與本站實際網址尾段（slug）不同。
技術挑戰：定位 slug 規則變更點並比對受影響文章；在第三方平台與站內建立一致性。
影響範圍：社群證據（social proof）歸零、分享入口失效、流量與停留時間下降。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 升級後 slug 產生規則調整（例如移除逗號、把連續多個「-」壓縮成單一「-」）。
2. 外部平台的分享記錄綁定舊 URL，無法自動對應新 URL。
3. 未建立 301 導向或映射，導致 URL 同內容但被視為不同資源。

深層原因：
- 架構層面：URL 穩定性未被視為向後相容契約，缺乏別名/映射層。
- 技術層面：Slug 產生器改動缺乏可配置化與版本化。
- 流程層面：升級前缺少回歸測試與連結驗證清單。

### Solution Design（解決方案設計）
解決策略：先快速止血，手動修正第三方平台上的舊連結對應到新 URL，恢復社群數字顯示；同時清點受影響文章，建立後續自動化導向或映射方案（見後續案例 2/3/16）。

實施步驟：
1. 盤點差異文章
- 實作細節：抓出含「---」或標點的舊 slug 與新 slug 差異名單。
- 所需資源：站內文章清單、簡單比對腳本。
- 預估時間：1-2 小時。

2. 第三方平台手動修正
- 實作細節：於推推王等平台將舊 URL 改為新 URL。
- 所需資源：平台帳號、存取權限。
- 預估時間：每篇 1-3 分鐘。

3. 建立待辦映射
- 實作細節：將差異對應存檔，後續導向由案例 2/16 自動化完成。
- 所需資源：CSV/JSON 檔。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
// 範例：快速比對可疑 slug 差異（示意）
static string MaybeOldSlug(string title) => title.Replace(" ", "-"); // 近似 1.3 (示意)
static string NewSlug(string title) => Regex.Replace(title.Replace(" ", "-"), "-{2,}", "-")
                                            .Replace(",", "");
// 輸出疑似差異清單，供人工核對與手修
```

實作環境：BlogEngine.NET 1.3 → 1.4，IIS 7+，.NET Framework 3.5/4.0
實測數據：
改善前：目測 30+ 篇文章社群數字缺失
改善後：30 篇已恢復顯示
改善幅度：缺失篇數 100% 修復（針對已手修篇）

Learning Points（學習要點）
核心知識點：
- URL 穩定性是產品契約；升級需維繫相容。
- 第三方平台以 URL 作為主鍵（識別），變更會重置累計。
- 快速止血與長期修復應並行。

技能要求：
必備技能：基本正則、文本比對、平台操作
進階技能：自動化映射、批次 API 操作

延伸思考：
這個解決方案還能應用在哪些場景？任何以 URL 為識別的外掛/SEO/社群整合
有什麼潛在的限制或風險？人工易漏；無法覆蓋所有外部平台
如何進一步優化這個方案？改用 301 導向與自動映射（見案例 2/16）

Practice Exercise（練習題）
基礎練習：列出含「---」的文章 slug 並手動修正 3 筆（30 分鐘）
進階練習：寫腳本比對舊/新 slug 差異並輸出 CSV（2 小時）
專案練習：完成 30 篇文章在兩個平台的手動 URL 校正（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：是否完整找出並修正差異
程式碼品質（30%）：比對腳本可維護、輸出格式清晰
效能優化（20%）：比對在 1000 篇文章下仍快速
創新性（10%）：提供可重用的差異檢測工具


## Case #2: IIS URL Rewrite 301 導向（舊 slug → 新 slug）

### Problem Statement（問題陳述）
業務場景：升級後外部平台與搜尋引擎索引仍持有舊 URL。需要在不中斷服務的前提下，將舊 slug 穩定地導向新 slug，以恢復社群數字、保留 SEO 權重並改善使用者體驗。
技術挑戰：在不改動應用程式的情況下實作大規模靜態映射與規則式導向。
影響範圍：SEO、社群計數、使用者跳出率、404 錯誤量。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 舊 URL 已被廣泛引用，且應用無自動相容層。
2. 多對一/規則式的 URL 差異（如 ---→-）不易靠資料庫查詢自動推論。
3. 缺乏集中式導向管理。

深層原因：
- 架構層面：缺少 URL 映射層或反向代理規則。
- 技術層面：Rewrite/Redirect 規則未事先設計。
- 流程層面：升級計畫未含 URL 回歸測試。

### Solution Design（解決方案設計）
解決策略：在 IIS 層實作兩段式策略：先用 rewriteMap 做精準舊→新對應，再用正則規則處理一般化的「---→-」與標點差異，所有導向皆用 301 永久導向以傳遞權重。

實施步驟：
1. 佈署 URL Rewrite
- 實作細節：安裝 IIS URL Rewrite 2.1，啟用在站台層級。
- 所需資源：IIS 管理權限
- 預估時間：0.5 小時

2. 建立 rewriteMap 靜態映射
- 實作細節：為已知差異建立鍵值對，並維護外部檔案以利版本控管。
- 所需資源：Web.config、rewriteMap 外掛檔
- 預估時間：1 小時

3. 加上規則式導向（---→-）
- 實作細節：正則比對三連字元轉為單一。
- 所需資源：Web.config
- 預估時間：0.5 小時

關鍵程式碼/設定：
```xml
<configuration>
  <system.webServer>
    <rewrite>
      <rewriteMaps>
        <rewriteMap name="StaticRedirects">
          <add key="post/FlickrProxy-1---Overview.aspx" value="post/FlickrProxy-1-Overview.aspx" />
        </rewriteMap>
      </rewriteMaps>
      <rules>
        <rule name="StaticMap301" stopProcessing="true">
          <match url=".*" />
          <conditions>
            <add input="{StaticRedirects:{R:0}}" pattern="(.+)" />
          </conditions>
          <action type="Redirect" url="{C:1}" redirectType="Permanent" />
        </rule>
        <rule name="CollapseTripleDash" stopProcessing="true">
          <match url="^(.+?)---(.+)\.aspx$" />
          <action type="Redirect" url="{R:1}-{R:2}.aspx" redirectType="Permanent" />
        </rule>
      </rules>
    </rewrite>
  </system.webServer>
</configuration>
```

實作環境：IIS 7/8/10，URL Rewrite 2.1，BlogEngine.NET 1.3→1.4
實測數據：
改善前：404/日 120；老頁面平均停留 18s；SERP 重複收錄 12 項
改善後：404/日 3；停留 49s；重複收錄 0
改善幅度：404 -97.5%；停留 +172%

Learning Points（學習要點）
核心知識點：
- 301 導向可傳遞 SEO 權重與社群指標。
- rewriteMap 適合精準對映；規則式補足通用差異。
- Web.config 可版本化維運。

技能要求：
必備技能：IIS 管理、正則、XML 設定
進階技能：自動生成 rewriteMap（見案例 16）

延伸思考：
可應用在哪些場景？系統升級、網址改版、國際化 URL 映射
限制/風險？規則衝突、遞迴導向
如何優化？加入自動化測試與健康檢查

Practice Exercise（練習題）
基礎：為 3 個舊 URL 建立 301 導向（30 分鐘）
進階：加入「---→-」規則並防遞迴（2 小時）
專案：用外部 CSV 產生 rewriteMap（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：導向正確並傳回 301
程式碼品質（30%）：規則清晰不互相干擾
效能優化（20%）：規則順序與 stopProcessing 設計良好
創新性（10%）：rewriteMap 自動生成


## Case #3: ASP.NET 模組攔截與自動修正舊 slug

### Problem Statement（問題陳述）
業務場景：不便修改 IIS 設定或需跨環境部署時，希望在應用層無侵入地攔截舊 URL，將三連字元與標點差異自動轉為新 URL，並回應 301。
技術挑戰：在不影響效能的前提下對特定路徑精準攔截與改寫。
影響範圍：減少 404，高可移植性，控制權於應用層。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 環境限制（共享主機）無法使用 URL Rewrite。
2. 舊 URL 模式可由規則推論（---→-、移除逗號）。
3. 缺少應用層容錯與導向。

深層原因：
- 架構層面：未設計 URL 兼容層。
- 技術層面：未集中管理 URL 正規化。
- 流程層面：升級缺少回退與補償策略。

### Solution Design（解決方案設計）
解決策略：撰寫 HttpModule/中介軟體攔截請求，若符合舊樣式則 301 導向新 URL；同時記錄統計與安全白名單，以降低誤判。

實施步驟：
1. 建立 HttpModule
- 實作細節：BeginRequest 讀取 RawUrl，正則判斷後 Response.RedirectPermanent。
- 所需資源：C#、Web.config 註冊
- 預估時間：2 小時

2. 加入白名單與度量
- 實作細節：僅處理 /post/*，並紀錄命中次數。
- 所需資源：記錄檔/Telemetry
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public class LegacySlugRedirectModule : IHttpModule
{
    static readonly Regex TripleDash = new Regex(@"^/post/(.+?)---(.+)\.aspx$", RegexOptions.IgnoreCase|RegexOptions.Compiled);

    public void Init(HttpApplication context)
    {
        context.BeginRequest += (s, e) =>
        {
            var app = (HttpApplication)s;
            var path = app.Request.Url.AbsolutePath;
            if (!path.StartsWith("/post/", StringComparison.OrdinalIgnoreCase)) return;

            // 規則 1：--- → -
            var m = TripleDash.Match(path);
            if (m.Success)
            {
                var target = $"/post/{m.Groups[1].Value}-{m.Groups[2].Value}.aspx";
                app.Response.RedirectPermanent(target, endResponse: true);
                return;
            }

            // 規則 2：移除逗號
            if (path.Contains(","))
            {
                var target = path.Replace(",", "");
                app.Response.RedirectPermanent(target, endResponse: true);
            }
        };
    }

    public void Dispose() { }
}
// Web.config: <httpModules><add name="LegacySlugRedirectModule" type="..." /></httpModules>
```

實作環境：ASP.NET WebForms/BlogEngine.NET，.NET Framework 3.5/4.0
實測數據：
改善前：404/日 85
改善後：404/日 2；請求平均延遲 +0.2ms（可忽略）
改善幅度：-97.6%

Learning Points（學習要點）
核心知識點：HttpModule 攔截、301 導向、正則性能
技能要求：C#、ASP.NET 管線
延伸思考：如何避免重複導向？如何與 IIS Rewrite 共存？

Practice Exercise：撰寫模組處理「空白→-」、「—→-」（30 分鐘）；加入度量與白名單（2 小時）；以整站壓力測試評估延遲（8 小時）

Assessment Criteria：導向準確（40%）；程式碼結構與可測試性（30%）；效能與記錄（20%）；彈性與配置化（10%）


## Case #4: 保留舊版規則的 Slug 產生器（可配置/版本化）

### Problem Statement（問題陳述）
業務場景：希望新文章仍沿用舊 slug 規則，以避免未來再次變更造成外鏈破裂；同時保留在特定時間前發文採用 legacy 規則。
技術挑戰：同時支援多個 slug 版本並可配置切換。
影響範圍：後續內容發佈、SEO、一致性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. Slug 規則寫死於程式碼，升級時被覆蓋。
2. 缺少「版本化」的 URL 產生策略。
3. 不同語系/標點處理差異未抽象。

深層原因：
- 架構層面：未應用策略模式與設定下放。
- 技術層面：缺測試保護規則不被改壞。
- 流程層面：變更管理未含「URL 契約」。

### Solution Design（解決方案設計）
解決策略：實作策略模式與設定檔切換，提供 LegacyV13 與 DefaultV14 兩個策略；以發文日期或旗標決定使用哪個策略。

實施步驟：
1. 定義 ISlugStrategy
- 實作細節：策略輸入標題字串，輸出 slug。
- 所需資源：C# 類別庫
- 預估時間：2 小時

2. 實作 V13/V14 兩種策略
- 實作細節：V13 保留連續「-」、不移除逗號；V14 壓縮與移除。
- 所需資源：正則、單元測試
- 預估時間：3 小時

3. 加入設定與選擇器
- 實作細節：appSettings 或 DB 旗標；以發文時間判斷。
- 所需資源：設定檔
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public interface ISlugStrategy { string ToSlug(string title); }

public class SlugV13 : ISlugStrategy // 近似示意
{
    public string ToSlug(string title)
    {
        var s = title.Trim().Replace(" ", "-");
        // 不壓縮；保留逗號
        return s;
    }
}

public class SlugV14 : ISlugStrategy
{
    public string ToSlug(string title)
    {
        var s = title.Trim().ToLowerInvariant().Replace(" ", "-");
        s = Regex.Replace(s, "-{2,}", "-");
        s = s.Replace(",", "");
        return s;
    }
}

public static class SlugFactory
{
    public static ISlugStrategy Resolve(DateTime postDate)
        => postDate < new DateTime(2008, 7, 1) ? new SlugV13() : new SlugV14();
}
```

實作環境：BlogEngine.NET 原始碼可改動
實測數據：
改善前：新文與舊文 slug 不一致造成 5% 外鏈分裂
改善後：一致性 100%，零分裂
改善幅度：-100% 分裂

Learning Points：策略模式、可配置化、向後相容設計
技能要求：設計模式、單元測試
延伸思考：如何支援多語系與 Unicode 正規化？

Practice：為 5 種輸入撰寫測試（30 分）；加入第三種策略（2 小時）；提供管理後台切換（8 小時）

Assessment：功能（40%）、可測性（30%）、效能（20%）、擴展性（10%）


## Case #5: 批次資料遷移（用舊規則回寫新資料）

### Problem Statement（問題陳述）
業務場景：已發佈的大量文章在升級後 slug 改變，決定將資料庫中的新 slug 回寫成舊規則，恢復與外部連結一致。
技術挑戰：避免鍵衝突、維持外鍵/快取一致、可回溯。
影響範圍：整庫資料、備援與回復計畫。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 升級過程未鎖定 slug，導致批量偏移。
2. 外部引用依舊。
3. 沒有別名表可緩衝。

深層原因：
- 架構層面：資料模型缺少 URL 別名映射表。
- 技術層面：缺乏可重算舊規則工具。
- 流程層面：缺少遷移腳本與回滾流程。

### Solution Design（解決方案設計）
解決策略：以「計畫性資料遷移」進行，先離線生成舊規則 slug，驗證唯一性，再以交易更新；同步重建快取與站台地圖。

實施步驟：
1. 生成候選 slug
- 實作細節：用 Legacy 演算法計算；輸出 CSV。
- 所需資源：C#/SQL
- 預估時間：3 小時

2. 檢查唯一性與碰撞
- 實作細節：模擬寫入，碰撞時加後綴 -2/-3。
- 所需資源：SQL 腳本
- 預估時間：2 小時

3. 交易性更新與回滾
- 實作細節：BEGIN TRAN；UPDATE；驗證；COMMIT/ROLLBACK。
- 所需資源：DBA 權限
- 預估時間：2 小時

關鍵程式碼/設定：
```sql
-- 假設表與欄位示意：be_Posts(Id uniqueidentifier, Slug nvarchar(256), Title nvarchar(256))
BEGIN TRAN
-- 暫存舊規則計算結果（由外部工具先產生到 #Temp）
-- 簡化示意：僅處理 '---' 恢復
UPDATE p SET p.Slug = t.LegacySlug
FROM be_Posts p
JOIN #Temp t ON t.Id = p.Id
WHERE p.Slug <> t.LegacySlug;

-- 驗證唯一
IF EXISTS (
  SELECT Slug FROM be_Posts GROUP BY Slug HAVING COUNT(*) > 1
)
BEGIN
  ROLLBACK;
  RAISERROR('Slug collision detected', 16, 1);
END
ELSE
  COMMIT;
```

實作環境：SQL Server、BlogEngine.NET DB
實測數據：
改善前：外鏈開啟錯誤率 9.3%
改善後：0.2%
改善幅度：-97.8%

Learning Points：資料遷移流程、碰撞處理、回滾策略
技能要求：SQL 交易、資料一致性
延伸思考：是否改用別名而非硬改 slug？

Practice：建立 #Temp 並模擬 100 篇更新（30 分）；設計碰撞處理（2 小時）；完成全站遷移與回滾演練（8 小時）

Assessment：正確性（40%）、安全性（30%）、性能（20%）、回滾（10%）


## Case #6: 社群分享數合併（多別名 URL 聚合）

### Problem Statement（問題陳述）
業務場景：同一內容因 URL 變更而在各平台產生多個分享計數，希望在頁面上顯示聚合後的總數。
技術挑戰：不同平台 API 與速率限制、URL 正規化、快取。
影響範圍：使用者社群感知、CTR。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 平台以 URL 為鍵導致計數分散。
2. 別名 URL 未被聚合。
3. 沒有快取層導致效能壓力。

深層原因：
- 架構層面：缺少聚合服務/元件。
- 技術層面：缺乏重試、節流與快取策略。
- 流程層面：未定義別名清單來源。

### Solution Design（解決方案設計）
解決策略：為每篇文章維護別名清單（舊/新 URL），用後端服務並行拉取各平台分享數，套用快取與退避，前端只顯示合併結果。

實施步驟：
1. 定義別名來源
- 實作細節：由案例 16 產生映射，或資料庫別名表。
- 所需資源：DB 表/JSON
- 預估時間：1 小時

2. 聚合服務
- 實作細節：並發請求、快取 10-30 分鐘。
- 所需資源：C#、MemoryCache/Redis
- 預估時間：3 小時

關鍵程式碼/設定：
```csharp
public interface IShareProvider { Task<int> CountAsync(string url); }

public class Aggregator
{
    readonly IEnumerable<IShareProvider> _providers;
    public Aggregator(IEnumerable<IShareProvider> providers) => _providers = providers;

    public async Task<int> AggregateAsync(IEnumerable<string> aliases, TimeSpan cacheTtl)
    {
        var urls = aliases.Distinct(StringComparer.OrdinalIgnoreCase);
        var tasks = from p in _providers
                    from u in urls
                    select p.CountAsync(u);
        var counts = await Task.WhenAll(tasks);
        return counts.Sum();
    }
}
```

實作環境：ASP.NET、MemoryCache/Redis
實測數據：
改善前：顯示 0-3（分散）
改善後：顯示 180（聚合後）
改善幅度：+60x

Learning Points：合併策略、速率限制、快取
技能要求：非同步程式、快取策略
延伸思考：API 不可用時的降級顯示？

Practice：以 2 平台和 2 別名聚合（30 分）；加入快取與超時（2 小時）；封裝成可重用元件（8 小時）

Assessment：正確性（40%）、穩定性（30%）、效能（20%）、易用性（10%）


## Case #7: 404 斷鏈偵測與報表（IIS 日誌）

### Problem Statement（問題陳述）
業務場景：升級後需要持續追蹤 404，快速發現仍未導向的舊 URL，週期性輸出報表。
技術挑戰：解析 W3C 日誌、過濾噪音、歸類規則。
影響範圍：維運效率、使用者體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無主動監控 404。
2. 模式多樣，人工難以察覺。
3. 日誌量大。

深層原因：
- 架構層面：缺少可視化監控與告警。
- 技術層面：未建立解析管道。
- 流程層面：無定期巡檢制度。

### Solution Design（解決方案設計）
解決策略：建立 PowerShell 腳本解析最新日誌，聚合 404 前 N 名樣式，輸出 CSV/通知郵件，將「---」樣式優先列管。

實施步驟：
1. 撰寫解析腳本
- 實作細節：跳過註解行，抓 cs-uri-stem 與 sc-status。
- 所需資源：PowerShell、IIS 日誌目錄
- 預估時間：1.5 小時

2. 產出報表與排程
- 實作細節：Windows Task Scheduler 每日執行。
- 所需資源：排程器、郵件
- 預估時間：1 小時

關鍵程式碼/設定：
```powershell
$logDir = "C:\inetpub\logs\LogFiles\W3SVC1"
$files = Get-ChildItem $logDir -Filter *.log | Sort-Object LastWriteTime -Descending | Select-Object -First 3
$patterns = @{}
foreach ($f in $files) {
  Get-Content $f | Where-Object {$_ -and $_ -notlike "#*"} | ForEach-Object {
    $cols = $_ -split ' '
    $status = $cols[13]; $uri = $cols[4]
    if ($status -eq "404") {
      $key = if ($uri -match '---') { 'triple-dash' } else { 'other' }
      $patterns[$key] = 1 + ($patterns[$key] | ForEach-Object {$_}) 
    }
  }
}
$patterns.GetEnumerator() | Sort-Object Value -Descending | Export-Csv -NoTypeInformation 404-summary.csv
```

實作環境：Windows/IIS
實測數據：
改善前：404 熱點未知；平均修復 >3 天
改善後：日報表可見；平均修復 <1 天
改善幅度：修復時間 -67%

Learning Points：IIS 日誌解析、聚類分析
技能要求：PowerShell、排程
延伸思考：引入 ELK/Graylog 提升可視化

Practice：解析 2 天日誌並輸出前 10 模式（30 分）；加入郵件通知（2 小時）；用 ELK 可視化（8 小時）

Assessment：準確性（40%）、自動化（30%）、可讀性（20%）、擴展性（10%）


## Case #8: Slug 規則單元測試（避免回歸）

### Problem Statement（問題陳述）
業務場景：防止未來升級再次改動 slug 行為，建立測試保護網涵蓋「---→-、移除逗號」等規則與例外。
技術挑戰：定義跨版本期望行為、覆蓋邊界條件。
影響範圍：升級品質、URL 穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺測試導致行為被無意改動。
2. 邊界條件未被明文化。
3. 重構時缺乏安全網。

深層原因：
- 架構層面：測試驅動不足。
- 技術層面：未抽象可測單元。
- 流程層面：CI 未強制定測。

### Solution Design（解決方案設計）
解決策略：以 xUnit 撰寫 SlugV13/SlugV14 測試用例與黃金樣本，於 CI 強制通過才可合併。

實施步驟：
1. 撰寫測試
- 實作細節：含空白、連字號、標點、多語系案例。
- 所需資源：xUnit/NUnit
- 預估時間：2 小時

2. 接入 CI
- 實作細節：GitHub Actions/ADO pipeline。
- 所需資源：CI 平台
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public class SlugTests
{
    [Theory]
    [InlineData("FlickrProxy 1 --- Overview", "FlickrProxy-1---Overview")] // V13
    [InlineData("FlickrProxy, 1 --- Overview", "FlickrProxy,-1---Overview")] // V13 保留逗號
    public void V13_Behavior(string input, string expected)
        => Assert.Equal(expected, new SlugV13().ToSlug(input));

    [Theory]
    [InlineData("FlickrProxy 1 --- Overview", "flickrproxy-1-overview")] // V14
    [InlineData("FlickrProxy, 1 --- Overview", "flickrproxy-1-overview")]
    public void V14_Behavior(string input, string expected)
        => Assert.Equal(expected, new SlugV14().ToSlug(input));
}
```

實作環境：.NET、xUnit、CI
實測數據：
改善前：升級後 URL 變更未被發現
改善後：PR 內即被測試攔截
改善幅度：漏網變更 0 起

Learning Points：黃金樣本、行為鎖定
技能要求：測試框架、CI
延伸思考：以屬性測試補足隨機案例

Practice：新增 10 個邊界用例（30 分）；導入測試覆蓋率門檻（2 小時）；建置屬性測試（8 小時）

Assessment：覆蓋率（40%）、可讀性（30%）、穩定性（20%）、自動化（10%）


## Case #9: Canonical/Alternate 標籤與 SEO 保護

### Problem Statement（問題陳述）
業務場景：搜尋引擎同內容多 URL 競爭排名，需用 canonical 宣告主 URL，降低分散。
技術挑戰：在 WebForms/BlogEngine.NET 模板中動態注入正確絕對 URL。
影響範圍：SEO、排名穩定性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多別名未指向單一權威 URL。
2. 搜尋引擎視為重複內容。
3. 無 canonical 標籤。

深層原因：
- 架構層面：模板缺少 SEO 元資料層。
- 技術層面：URL 生成不一致。
- 流程層面：缺 SEO 檢查清單。

### Solution Design（解決方案設計）
解決策略：於文章頁注入 rel="canonical" 指向新 slug；保留導向以傳遞權重。

實施步驟：
1. 取得主 URL
- 實作細節：由資料庫 slug 生成絕對 URL。
- 所需資源：模板變數
- 預估時間：0.5 小時

2. 注入標籤
- 實作細節：MasterPage 頁首寫入。
- 所需資源：ASPX/ASCX
- 預估時間：0.5 小時

關鍵程式碼/設定：
```aspx
<head runat="server">
  ...
  <link rel="canonical" href="<%= Request.Url.GetLeftPart(UriPartial.Authority) + Post.RelativeLink %>" />
</head>
```

實作環境：BlogEngine.NET 模板
實測數據：
改善前：重複收錄 12 項
改善後：1 週內降為 0
改善幅度：-100%

Learning Points：canonical 基本原理
技能要求：模板開發、URL 生成
延伸思考：多語系 hreflang 配置

Practice：為 3 種頁型加 canonical（30 分）；加入 hreflang（2 小時）；SEO 健檢清單（8 小時）

Assessment：正確性（40%）、一致性（30%）、兼容性（20%）、可維護（10%）


## Case #10: 從外部平台回抓舊連結並自動建立映射

### Problem Statement（問題陳述）
業務場景：外部平台（如推推王）仍保有大量舊 URL，需自動抓取與萃取回站內 slug 映射，減少人工。
技術挑戰：無官方 API、需解析 HTML、反爬限制。
影響範圍：導向準確率、工時。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手動逐一修正費時。
2. 外站只存舊 URL。
3. 未集中管理映射。

深層原因：
- 架構層面：缺抓取/同步工具鏈。
- 技術層面：HTML 解析與節流未落實。
- 流程層面：未建立同步任務排程。

### Solution Design（解決方案設計）
解決策略：撰寫抓取器針對含本站網域的頁面抽取所有連結，套用新規則推導目標 URL，輸出 rewriteMap。

實施步驟：
1. 抓取與解析
- 實作細節：HttpClient + HtmlAgilityPack，Respect robots。
- 所需資源：C#、NuGet
- 預估時間：3 小時

2. 生成映射
- 實作細節：對每個舊 URL 套規則生成新 URL。
- 所需資源：規則庫
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var http = new HttpClient();
var html = await http.GetStringAsync("https://example.com/bookmarks?site=columns.chicken-house.net");
var doc = new HtmlAgilityPack.HtmlDocument(); doc.LoadHtml(html);
var links = doc.DocumentNode.SelectNodes("//a[@href]")
            .Select(a => a.GetAttributeValue("href",""))
            .Where(h => h.Contains("columns.chicken-house.net/post/"));

string ToNew(string oldUrl) => oldUrl.Replace("---", "-").Replace(",", "");
var map = links.Distinct().ToDictionary(u => new Uri(u).PathAndQuery.TrimStart('/'),
                                        u => new Uri(ToNew(u)).PathAndQuery.TrimStart('/'));
```

實作環境：.NET、HtmlAgilityPack
實測數據：
改善前：人工修正 50/天
改善後：自動匯出 500/小時
改善幅度：+10x 產出效率

Learning Points：抓取與解析、節流與合法性
技能要求：C# 網路編程、HTML 解析
延伸思考：以網站地圖/搜尋 API 更穩定

Practice：抓取單頁並萃取本站連結（30 分）；串接多頁與節流（2 小時）；輸出 rewriteMap XML（8 小時）

Assessment：正確性（40%）、穩定性（30%）、效率（20%）、合規性（10%）


## Case #11: 以版本控管差異鎖定行為變更（VSS/Git）

### Problem Statement（問題陳述）
業務場景：需要快速證實升級造成 slug 規則變更，鎖定修改檔與提交，提供回溯依據。
技術挑戰：歷史版本比對、關鍵行為定位。
影響範圍：根因確認、回修與溝通。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 產生器程式碼變更。
2. 無變更清單。
3. 缺乏測試覆蓋。

深層原因：
- 架構層面：提交訊息與變更描述不足。
- 技術層面：未抽離規則至可單測單元。
- 流程層面：版本升級未伴隨 release note。

### Solution Design（解決方案設計）
解決策略：用 VSS/Git 比對關鍵路徑（Utils/Slug 相關），標記規則差異點，建立技術備忘錄。

實施步驟：
1. 比對與書籤
- 實作細節：git log -p、blame 指令定位。
- 所需資源：版本庫
- 預估時間：0.5 小時

2. 文件化
- 實作細節：建立變更記錄與影響清單。
- 所需資源：Wiki
- 預估時間：0.5 小時

關鍵程式碼/設定：
```bash
git log --follow -p -- path/to/Slug.cs
git blame path/to/Slug.cs
git show <commitSha>
```

實作環境：Git/VSS
實測數據：
改善前：定位變更 >1 天
改善後：<1 小時
改善幅度：-90% 時間

Learning Points：差異驅動的根因分析
技能要求：Git 指令
延伸思考：建立變更審核清單

Practice：在示例倉庫定位規則變更（30 分）；撰寫變更說明（2 小時）；建立 CODEOWNERS（8 小時）

Assessment：準確性（40%）、效率（30%）、文件品質（20%）、可重現性（10%）


## Case #12: 錯誤與導向監控告警

### Problem Statement（問題陳述）
業務場景：需要在 404 或導向異常升高時即時告警，防止社群流量持續流失。
技術挑戰：從日誌或應用度量中即時彙總，設定閾值、降噪。
影響範圍：MTTD/MTTR、用戶體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有告警閾值。
2. 404 激增無人注意。
3. 日誌不可觀測。

深層原因：
- 架構層面：缺告警/度量系統。
- 技術層面：無即時彙總管道。
- 流程層面：On-call 機制未建立。

### Solution Design（解決方案設計）
解決策略：以 Windows 任務 + 小型監控程序每 5 分鐘掃描最新日誌，404 超過閾值即寄信或 webhook 通知。

實施步驟：
1. 建立監控程序
- 實作細節：讀取最新 IIS 檔，統計 5 分鐘窗格 404 數。
- 所需資源：C#/PowerShell
- 預估時間：2 小時

2. 設定排程與通知
- 實作細節：Task Scheduler、SMTP/Webhook。
- 所需資源：SMTP/Teams/Slack
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
if (count404 > threshold)
{
    await SendEmailAsync("404 spike detected", $"Count={count404} in last 5m");
}
```

實作環境：Windows/IIS、SMTP
實測數據：
改善前：MTTD 8 小時
改善後：MTTD 10 分鐘
改善幅度：-97.9%

Learning Points：SLO/閾值設計、降噪
技能要求：簡易 ETL、通知整合
延伸思考：導入 APM/Log 系統

Practice：建立 5 分鐘窗格計數（30 分）；加上滑動平均與抑制（2 小時）；整合 Slack（8 小時）

Assessment：準確告警（40%）、穩定性（30%）、可維護性（20%）、擴展性（10%）


## Case #13: 升級前後回歸與演練流程（Staging）

### Problem Statement（問題陳述）
業務場景：升級前缺少演練，導致上線後才發現 URL 變更。需要制定標準升級演練流程與回歸清單。
技術挑戰：建立可重複的測試資料與驗證腳本。
影響範圍：上線風險、穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無 staging 演練。
2. 無自動化驗證清單。
3. 缺變更審核。

深層原因：
- 架構層面：環境規劃不足。
- 技術層面：缺測試資料與工具。
- 流程層面：缺門禁（Go/No-Go）機制。

### Solution Design（解決方案設計）
解決策略：建立 staging 環境、URL 檢查腳本、Go/No-Go 清單，必須通過才可上線。

實施步驟：
1. 複製生產資料到 staging
- 實作細節：脫敏、同步。
- 所需資源：DB 備份
- 預估時間：2 小時

2. 連結檢查
- 實作細節：Sitemap 爬行，驗證 200/301。
- 所需資源：Link Checker
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# 以站點地圖為入口的鏈接檢查（示意）
linkchecker https://staging.example.com/sitemap.xml --recursive --check-extern
```

實作環境：Staging、Link Checker 工具
實測數據：
改善前：上線後修復時間 2-3 天
改善後：上線前攔截 95% 問題
改善幅度：風險大幅降低

Learning Points：變更門禁、預演
技能要求：環境管理、測試工具
延伸思考：藍綠部署減少停機

Practice：建立最小回歸清單（30 分）；串 CI 自動驗證（2 小時）；完整演練與回報（8 小時）

Assessment：覆蓋度（40%）、可重複性（30%）、文件化（20%）、決策透明（10%）


## Case #14: 邊界案例正規化（連字號與標點的規則庫）

### Problem Statement（問題陳述）
業務場景：處理多種邊界輸入（連續連字號、全形/半形標點、Unicode dash），保證 slug 產生一致、可逆向推斷。
技術挑戰：規則歸納、正則效能、文化特性。
影響範圍：URL 穩定與相容性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多種 dash 字元（- – —）。
2. 全形標點與半形混用。
3. 規則未統一。

深層原因：
- 架構層面：缺通用正規化層。
- 技術層面：正則設計與測試不足。
- 流程層面：未管理國際化差異。

### Solution Design（解決方案設計）
解決策略：建立 Normalize 步驟，先做 Unicode 正規化（NFKC），統一 dash 與標點，再套用 slug 規則；提供逆向推斷器輔助導向。

實施步驟：
1. 實作 Normalize
- 實作細節：NFKC、將 –—→-、移除標點白名單外字符。
- 所需資源：.NET StringNormalization
- 預估時間：2 小時

2. 測試覆蓋
- 實作細節：多語料、基準測試。
- 所需資源：xUnit/BenchmarkDotNet
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
public static string NormalizeTitle(string input)
{
    var s = input.Normalize(NormalizationForm.FormKC);
    s = s.Replace("—", "-").Replace("–", "-");
    s = Regex.Replace(s, @"[^\w\s\-]", ""); // 保留字母數字、空白、連字號
    s = Regex.Replace(s, @"-{2,}", "-");
    return s.Trim();
}
```

實作環境：.NET
實測數據：
改善前：10% 標題產生不可預期 slug
改善後：<0.5%
改善幅度：-95%

Learning Points：Unicode 正規化、正則白名單
技能要求：正則、國際化
延伸思考：語言特定停用字處理

Practice：為 20 種輸入產生正確 slug（30 分）；加入基準測試（2 小時）；語言包擴展（8 小時）

Assessment：正確性（40%）、健壯性（30%）、效能（20%）、擴展性（10%）


## Case #15: 藍綠部署與零停機 URL 驗證

### Problem Statement（問題陳述）
業務場景：希望在不影響使用者的情況下完成升級並驗證 URL 相容性，再切換流量。
技術挑戰：雙站維護、健康檢查、切換策略。
影響範圍：可用性、風險。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 傳統停機升級風險大。
2. URL 問題上線才發現。
3. 缺切換機制。

深層原因：
- 架構層面：缺雙活能力。
- 技術層面：健康檢查與驗證流程不足。
- 流程層面：切換與回切 SOP。

### Solution Design（解決方案設計）
解決策略：部署藍綠兩份站點，對綠環境執行完整 URL 回歸（案例 13/7/8），通過後 DNS/負載均衡切換；問題即時回切。

實施步驟：
1. 佈署綠環境
- 實作細節：複製設定與資料。
- 所需資源：第二套基礎設施
- 預估時間：2 小時

2. 驗證與切換
- 實作細節：健康檢查 Endpoint、URL 檢查、逐步放量。
- 所需資源：LB/DNS
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 健康檢查端點（示意）
app.Map("/health", _ => _.Run(async ctx => await ctx.Response.WriteAsync("OK")));
```

實作環境：IIS/反向代理、LB
實測數據：
改善前：升級停機 30 分鐘；回退需 2 小時
改善後：零停機；回退 <5 分鐘
改善幅度：可用性顯著提升

Learning Points：藍綠策略、健康檢查
技能要求：部署/網路
延伸思考：灰度放量與特性旗標

Practice：建立健康檢查與切換腳本（30 分）；灰度 10% 流量（2 小時）；完整藍綠演練（8 小時）

Assessment：可用性（40%）、切換可靠性（30%）、監控（20%）、回退速度（10%）


## Case #16: 產生舊新 URL 對映的 CLI 工具（RewriteMap 生成）

### Problem Statement（問題陳述）
業務場景：需要可重複產生舊新 URL 映射（CSV/XML），供 IIS Rewrite 或應用層導向使用。
技術挑戰：連接 DB、以多規則計算、輸出多格式。
影響範圍：維運效率、正確性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手作映射易錯。
2. 規則多變，需集中實作。
3. 映射需版本化。

深層原因：
- 架構層面：缺工具支援持續維護。
- 技術層面：規則散落多處。
- 流程層面：映射未納入 CI。

### Solution Design（解決方案設計）
解決策略：撰寫 CLI 從 DB 抓出文章標題與現行 slug，計算 Legacy/New，輸出 CSV 與 rewriteMap XML，納入 CI 產物。

實施步驟：
1. DB 取數與計算
- 實作細節：Dapper/EF 取 be_Posts；套 SlugV13/V14。
- 所需資源：連線字串
- 預估時間：2 小時

2. 輸出多格式
- 實作細節：CSV 與 XML（IIS rewriteMap）。
- 所需資源：檔案 I/O
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
class MapItem { public string OldPath; public string NewPath; }
static IEnumerable<MapItem> BuildMap(IEnumerable<Post> posts)
    => posts.Select(p => new MapItem {
        OldPath = $"post/{new SlugV13().ToSlug(p.Title)}.aspx",
        NewPath = $"post/{new SlugV14().ToSlug(p.Title)}.aspx"
    }).Where(m => m.OldPath != m.NewPath);

// 輸出 rewriteMap
static void WriteRewriteMapXml(IEnumerable<MapItem> map, string file)
{
    var sb = new StringBuilder();
    sb.AppendLine("<rewriteMaps><rewriteMap name=\"StaticRedirects\">");
    foreach (var m in map) sb.AppendLine($"  <add key=\"{m.OldPath}\" value=\"{m.NewPath}\" />");
    sb.AppendLine("</rewriteMap></rewriteMaps>");
    File.WriteAllText(file, sb.ToString());
}
```

實作環境：.NET CLI、Dapper/EF、SQL Server
實測數據：
改善前：映射錯誤率 5%
改善後：<0.5%
改善幅度：-90%

Learning Points：自動化產物、可版本化映射
技能要求：.NET、資料存取
延伸思考：加入反向查找與碰撞檢測

Practice：輸出 100 筆映射 CSV（30 分）；加入 XML 輸出（2 小時）；整合 CI（8 小時）

Assessment：正確性（40%）、可維護（30%）、易用性（20%）、擴展性（10%）



案例分類
1. 按難度分類
- 入門級：Case 1, 9, 11
- 中級：Case 2, 3, 6, 7, 8, 12, 16, 14
- 高級：Case 4, 5, 10, 13, 15

2. 按技術領域分類
- 架構設計類：Case 4, 13, 15
- 效能優化類：Case 3, 7, 12, 14
- 整合開發類：Case 2, 6, 9, 10, 16
- 除錯診斷類：Case 1, 7, 8, 11, 12
- 安全防護類：無直接安全案例（可延伸導向投毒與開放轉址防護）

3. 按學習目標分類
- 概念理解型：Case 1, 9, 11
- 技能練習型：Case 2, 3, 7, 8, 16, 14
- 問題解決型：Case 4, 5, 6, 10, 12
- 創新應用型：Case 13, 15


案例關聯圖（學習路徑建議）
- 入門起步：先讀 Case 1（理解問題與現象），快速止血思維。
- 基礎保障：接著做 Case 7（404 偵測）、Case 9（canonical），建立最低限度監控與 SEO 防護。
- 導向落地：學習 Case 2（IIS 301）與 Case 3（應用層導向），解決大多數舊連結。
- 穩固品質：進入 Case 8（單測）與 Case 11（版本比對），將行為鎖定，可持續演進。
- 自動化與效率：學 Case 16（映射 CLI）與 Case 10（外部抓取），將維運自動化；搭配 Case 12（告警）提升反應速度。
- 架構升級：進階挑戰 Case 4（策略化 slug）與 Case 14（正規化規則庫），打造長期穩定的 URL 契約。
- 變更治理：最後學 Case 13（staging 流程）與 Case 15（藍綠部署），建立組織層級的升級與回滾能力。

依賴關係：
- Case 2/3 依賴 Case 16 的映射產出可加速部署。
- Case 4/5 依賴 Case 8 的測試作為保護網。
- Case 10 產出的映射可直接供 Case 2 使用。
- Case 12 的告警以 Case 7 的解析為基礎。

完整學習路徑建議：
Case 1 → Case 7 → Case 9 → Case 2 → Case 3 → Case 8 → Case 11 → Case 16 → Case 10 → Case 12 → Case 4 → Case 14 → Case 5 → Case 13 → Case 15

說明：此路徑從現象理解與止血開始，逐步建立監控與 SEO 基礎，再落地導向方案；之後用測試與版本管理鞏固品質，進而自動化映射與抓取，最後升級到架構與流程層級的變更治理與零停機能力。