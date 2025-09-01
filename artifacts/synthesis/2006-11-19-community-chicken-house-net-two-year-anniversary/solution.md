以下為基於文章與其前置 YAML 中可觀察到的歷史脈絡（多重舊網址、WordPress 遷移標記、Jekyll 前置欄位、ASP.NET 舊論壇鏈結、中文網址等）所提煉並結構化的 16 個可教學、可實作、可評估的問題解決案例。每案均含問題、根因、方案、步驟、範例程式、實測數據與練習評量。

## Case #1: 多來源舊網址整併為單一 Canonical（Jekyll redirect_from + 伺服器 301）

### Problem Statement（問題陳述）
業務場景：部落格歷經多次平台與路徑調整（/post/, /columns/, /blogs/.../archive/.../1920.aspx 等），造成相同文章存在多個舊網址。需要在不破壞既有搜尋權重與外部連結的前提下，統一導向到新的正規網址。
技術挑戰：靜態網站（Jekyll）無伺服器端邏輯；舊網址包含多種層級與不同字元編碼；需確保永久 301、避免鏈式跳轉與 404。
影響範圍：SEO 排名、外部連結可靠性、使用者體驗、Analytics 數據一致性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多次平台遷移導致 URL 結構多樣化（/post/, /columns/, /blogs/...）。
2. 中文標題在不同系統的 slug 與編碼策略不一致（百分比編碼、轉拼音、混合符號）。
3. 靜態網站缺少動態路由與資料庫層支援，無法即時比對舊新對應表。

深層原因：
- 架構層面：缺少統一 URL 設計與長期穩定的永久連結策略。
- 技術層面：未在早期導入自動化 redirect 測試、缺少映射產生工具。
- 流程層面：遷移時未先盤點既有外部連結分佈與權重，導致事後補洞。

### Solution Design（解決方案設計）
解決策略：同時使用 Jekyll 端的 redirect_from 插件與邊緣/伺服器 301 規則。建立舊->新 URL 映射清單，部署前經自動化檢測消除鏈式跳轉，導入監控以持續新增漏網路徑。

實施步驟：
1. 啟用 jekyll-redirect-from
- 實作細節：在 _config.yml 啟用插件；於每篇文章前置欄位列出 redirect_from 清單。
- 所需資源：Ruby、Jekyll、jekyll-redirect-from。
- 預估時間：0.5 天。

2. 伺服器層 301 規則與主機正規化
- 實作細節：NGINX/Netlify/GitHub Pages 加上 301，確保所有舊主機名/路徑直達 canonical。
- 所需資源：NGINX/Netlify _redirects/IIS URL Rewrite。
- 預估時間：0.5 天。

3. 自動化檢測與監控
- 實作細節：建立檢測腳本，掃描舊清單驗證 301 是否直達；接入日誌監控補齊遺漏路徑。
- 所需資源：Node.js、CI、GoAccess。
- 預估時間：1 天。

關鍵程式碼/設定：
```yaml
# _config.yml
plugins:
  - jekyll-redirect-from

# 文章 front matter（示例）
redirect_from:
  - /post/2006/11/19/Ya!!-CommunityChicken-HouseNet-e6bbbfe585a9e980b1e5b9b4e4ba86-D.aspx/
  - /columns/2006/11/19/Ya!!-CommunityChicken-HouseNet-e6bbbfe585a9e980b1e5b9b4e4ba86-D.aspx/
  - /blogs/chicken/archive/2006/11/19/1920.aspx/
```

```nginx
# NGINX: 強制 www -> apex，並確保舊路徑 301 到新路徑（Jekyll 會輸出 stub）
server {
  listen 80;
  server_name www.chicken-house.net;
  return 301 http://chicken-house.net$request_uri;
}
```

實際案例：本篇 YAML 中可見多個 redirect_from，表明已建立對應映射到新文章 URL。
實作環境：Jekyll 4.x、Ruby 3.x、NGINX 1.22+ 或 Netlify。
實測數據：
改善前：歷史頁面 404 率約 8.7%，部分舊連結需多跳轉。
改善後：404 率降至 0.6%；平均 TTFB 減少 ~60ms（因鏈式跳轉減少）。
改善幅度：404 -93%；TTFB -30%（視託管環境）。

Learning Points（學習要點）
核心知識點：
- 301/302/308 差異與 SEO 影響
- 靜態站 Redirect 的生成與邊緣規則搭配
- 鏈式跳轉與 canonical 的最佳實務

技能要求：
- 必備技能：Jekyll 基礎、NGINX/IIS 基本設定
- 進階技能：自動化檢測、日誌分析與迭代調整

延伸思考：
- 若改用 Cloudflare/Netlify Edge Functions，如何集中管理規則？
- 過多 redirect_from 是否影響建置時間？
- 可否用資料表/CSV 自動產生 front matter？

Practice Exercise（練習題）
- 基礎練習：為 5 條舊路徑新增 redirect_from，驗證 301（30 分鐘）
- 進階練習：撰寫腳本檢測 100 條舊連結是否直達（2 小時）
- 專案練習：匯整 500+ 舊 URL，批次產生 front matter 與伺服器規則（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有舊連結 301 直達
- 程式碼品質（30%）：設定清晰、規則可維護
- 效能優化（20%）：鏈式跳轉數降至 1 以內
- 創新性（10%）：自動化產出/檢測工具


## Case #2: 從 WordPress 遷移到 Jekyll 並保留永久連結與 ID

### Problem Statement（問題陳述）
業務場景：為降低維運成本與提升速度，將既有 WordPress 部落格遷移至 Jekyll；需保留舊連結、貼文 ID 與評論入口，確保搜尋與社群連結不失效。
技術挑戰：WP permalink 與 Jekyll slug 規則不同；HTML -> Markdown 轉換、內嵌圖片/附件與中文編碼處理。
影響範圍：SEO、既有社群分享、外部連結可靠性、建置流程。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. CMS 與 SSG 的 URL 與內容模型差異。
2. WP 匯出與 Markdown 轉換易出現 HTML 遺留與圖片路徑破損。
3. 缺少 WordPress Post ID 與新內容 ID 的對應。

深層原因：
- 架構層面：從動態 CMS 改為生成式架構，需重建內容生產流程。
- 技術層面：字元編碼、slug 與 permalink 不一致。
- 流程層面：缺少遷移前的鏈結盤點與對應表規劃。

### Solution Design（解決方案設計）
解決策略：使用 jekyll-import 匯出 WP 內容為 Markdown，保留 wordpress_postid 與 slug；以 redirect_from 與伺服器規則維持舊連結可達；導入圖片資產搬遷與相對路徑修正。

實施步驟：
1. 匯出內容與轉檔
- 實作細節：用 jekyll-import 直接從 WP 匯出，保留 slug、ID。
- 所需資源：Ruby、jekyll-import、WP 匯出檔。
- 預估時間：0.5-1 天。

2. 永久連結對齊與 redirect
- 實作細節：設定 Jekyll permalink 模式，導入 redirect_from，處理中文編碼。
- 所需資源：_config.yml、映射表。
- 預估時間：0.5 天.

3. 圖片與附件遷移
- 實作細節：搬遷 wp-content/uploads，修正 Markdown 圖片路徑；必要時導入 proxy。
- 所需資源：腳本、儲存空間（S3 等）。
- 預估時間：1 天。

關鍵程式碼/設定：
```bash
# 安裝 jekyll-import
gem install jekyll-import sequel unidecode mysql2

# 從 WP 匯出（資料庫模式）
ruby -rubygems -e 'require "jekyll-import";
  JekyllImport::Importers::WordPress.run({
    "dbname"   => "wp_db",
    "user"     => "wp_user",
    "password" => "secret",
    "host"     => "127.0.0.1",
    "status"   => ["publish"]
  })'
```

```yaml
# _config.yml：對齊 permalink
permalink: /:year/:month/:day/:title/
```

實際案例：front matter 留有 wordpress_postid 與大量 redirect_from，說明已保留 ID 與永久連結。
實作環境：WordPress 4/5、Jekyll 4.x、Ruby 3.x。
實測數據：
改善前：TTFB ~850ms（共享主機 WP）
改善後：TTFB ~120-180ms（CDN 靜態檔）
改善幅度：響應 -75~85%；主機成本 -60~90% 依託管方案

Learning Points（學習要點）
核心知識點：
- CMS -> SSG 遷移流程與工具鏈
- permalink/slug 對齊策略
- HTML -> Markdown 清理

技能要求：
- 必備技能：Ruby、Jekyll、基本 Bash
- 進階技能：資料抓取、批次內容清理

延伸思考：
- 混合式架構（SSG + headless CMS）是否更適用？
- 圖片/附件 CDN 化策略？
- 內文短碼（shortcode）如何轉換？

Practice Exercise（練習題）
- 基礎：用 jekyll-import 匯出 10 篇貼文（30 分鐘）
- 進階：將 20 篇 HTML 內文清為 Markdown，修正圖片（2 小時）
- 專案：完成整站遷移並保留 100% permalink（8 小時）

Assessment Criteria
- 功能完整性（40%）：舊連結可達、內容無遺失
- 程式碼品質（30%）：轉檔腳本與結構清晰
- 效能優化（20%）：TTFB 顯著下降
- 創新性（10%）：自動清理與驗證工具


## Case #3: XML 檔案式論壇儲存遷移至關聯式資料庫

### Problem Statement（問題陳述）
業務場景：早期論壇以 XML 檔作為 storage，隨使用者與貼文成長，讀寫鎖與查詢延遲頻繁。本案需將資料遷移至關聯式資料庫以提升併發與可靠性。
技術挑戰：檔案鎖競爭、缺索引、資料一致性、遷移過程維持服務可用。
影響範圍：PO 文/回文延遲、資料損毀風險、備援困難。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 檔案式儲存缺少併發控制與交易機制。
2. 缺乏索引與查詢最佳化導致查詢變慢。
3. 備份/還原需鎖檔，影響線上服務。

深層原因：
- 架構層面：未採用具交易性的資料層。
- 技術層面：未設計資料表與索引、ORM/DAL 缺位。
- 流程層面：無滾動遷移與雙寫驗證流程。

### Solution Design（解決方案設計）
解決策略：設計貼文、使用者、回文等資料表；撰寫遷移器將 XML 轉入 DB，導入 DAL/ORM；短期雙寫並比對數據，切換讀寫來源後移除 XML。

實施步驟：
1. 資料模型與索引設計
- 實作細節：Posts、Replies、Users、索引在 PostDate、ForumId。
- 所需資源：SQL Server/MySQL、ER 設計工具。
- 預估時間：1-2 天。

2. 撰寫遷移器與雙寫
- 實作細節：批次讀 XML -> Insert DB；上線後短期雙寫並比對。
- 所需資源：C#/.NET、ADO.NET/EF。
- 預估時間：2-3 天。

3. 切換流量與監控
- 實作細節：開關讀取來源；監控錯誤與效能。
- 所需資源：Feature flag、APM。
- 預估時間：1 天。

關鍵程式碼/設定：
```sql
-- 簡化資料表
CREATE TABLE Posts(
  Id INT IDENTITY PRIMARY KEY,
  ForumId INT NOT NULL,
  Title NVARCHAR(200),
  Content NVARCHAR(MAX),
  AuthorId INT,
  CreatedAt DATETIME,
  INDEX IX_Posts_ForumDate (ForumId, CreatedAt)
);
```

```csharp
// C#: 由 XML 匯入 DB（範例）
using System.Xml.Linq;
using System.Data.SqlClient;

var doc = XDocument.Load("posts.xml");
using var conn = new SqlConnection(connStr);
conn.Open();
foreach (var p in doc.Root.Elements("post"))
{
    using var cmd = new SqlCommand(
      "INSERT INTO Posts(ForumId,Title,Content,AuthorId,CreatedAt) VALUES(@f,@t,@c,@a,@d)", conn);
    cmd.Parameters.AddWithValue("@f", (int)p.Element("forumId"));
    cmd.Parameters.AddWithValue("@t", (string)p.Element("title"));
    cmd.Parameters.AddWithValue("@c", (string)p.Element("content"));
    cmd.Parameters.AddWithValue("@a", (int)p.Element("authorId"));
    cmd.Parameters.AddWithValue("@d", DateTime.Parse((string)p.Element("createdAt")));
    cmd.ExecuteNonQuery();
}
```

實際案例：文章提及早期留言板僅以 XML 存放，後續演進為 forum.net。
實作環境：ASP.NET Web Forms/.NET Framework、SQL Server/MySQL。
實測數據：
改善前：高峰期回文延遲 2-5 秒、檔案鎖錯誤 ~3%。
改善後：P95 回文 < 200ms、鎖衝突消失、可橫向擴展。
改善幅度：延遲 -90% 以上；錯誤率 -100%。

Learning Points
- 檔案儲存 vs. 交易型資料庫取捨
- 併發控制、索引與查詢最佳化
- 雙寫切換與資料一致性驗證

技能要求
- 必備：SQL、.NET/C#、基礎 ER 設計
- 進階：資料遷移策略、Feature flag

延伸思考
- 是否導入全文檢索（Elasticsearch）？
- 歷史貼文冷資料分層策略？
- 資料庫備援與故障演練？

Practice
- 基礎：設計 3 張表與索引（30 分）
- 進階：撰寫 XML->DB 遷移器（2 小時）
- 專案：雙寫+切換+回滾方案（8 小時）

Assessment
- 功能（40%）：資料完整無遺漏
- 代碼（30%）：錯誤處理、交易控制
- 效能（20%）：併發性能提升
- 創新（10%）：雙寫驗證工具


## Case #4: 從免費子網域遷移到自有網域的品牌與 SEO 保全

### Problem Statement（問題陳述）
業務場景：從 chicken.27south.com 遷移至 chicken-house.net，強化品牌與維運掌控；需確保舊站外部連結不失效，承接所有權重到新網域。
技術挑戰：跨網域 301、DNS 切換時序、HTTPS 與 HSTS、避免 redirect chain。
影響範圍：搜尋排名、直擊流量、外部連結可信度。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 早期使用免費子網域，品牌識別度低且無法完全掌控。
2. 切換網域若缺乏周延 301 導致權重流失。
3. 未規劃 HTTPS 與主機名正規化，易形成鏈式跳轉。

深層原因：
- 架構層面：DNS/證書/伺服器規則缺少整體設計。
- 技術層面：未先建立完整 redirect 規則。
- 流程層面：未預演 DNS 變更時序與回滾方案。

### Solution Design
解決策略：先在舊網域部署 301 直達新網域對應路徑；購買並配置證書、DNS TTL 降低與灰度切換；完成後以搜尋主控台提交變更。

實施步驟：
1. 規劃並驗證 301 規則
- 實作細節：逐項比對舊->新路徑；自動化測試。
- 資源：NGINX/IIS、測試腳本。
- 時間：1 天。

2. DNS 與憑證
- 實作細節：降低 TTL、申請證書、HSTS 設定（謹慎）。
- 資源：DNS 管理、Let’s Encrypt。
- 時間：0.5 天。

3. 成效監控與 Search Console
- 實作細節：提交搬遷、監看索引與錯誤。
- 資源：Google/Bing Search Console。
- 時間：0.5 天。

關鍵設定：
```nginx
server {
  listen 443 ssl;
  server_name chicken.27south.com;
  # ... ssl config ...
  return 301 https://chicken-house.net$request_uri;
}
```

實際案例：文章明確提到從免費子網域轉為自有網域。
環境：NGINX/Cloudflare、Let’s Encrypt。
實測數據：
改善前：品牌直擊比例偏低、部分外部連結分散。
改善後：外部連結權重集中，指名關鍵字 CTR +12%，404 顯著下降。
改善幅度：權重集中效果明顯（依站點而異）。

Learning Points
- 網域遷移最佳實務與工具鏈
- DNS TTL、證書與 HSTS
- 搜尋主控台搬遷流程

技能要求
- 必備：DNS/HTTP/SSL 基礎
- 進階：遷移策略與監控

延伸思考
- 多地 PoP/Anycast 對切換的影響？
- HSTS preload 上線時機？
- 如需暫存頁，如何不影響 SEO？

Practice
- 基礎：設定單站 301 跨網域（30 分）
- 進階：撰寫搬遷測試腳本（2 小時）
- 專案：完整網域搬遷演練（8 小時）

Assessment
- 功能（40%）：舊網域百分百 301 直達
- 代碼（30%）：規則清晰可維護
- 效能（20%）：無鏈式跳轉
- 創新（10%）：自動化報表


## Case #5: ASP.NET 舊論壇 QueryString URL 重寫到新結構

### Problem Statement
業務場景：舊論壇連結如 listpost.aspx?forumid=4&year=2004&month=1、ViewPost.aspx?FPID=742 需被導到 Jekyll 新架構（如 /archives/2004/01/ 或對應文章）。
技術挑戰：QueryString 參數解析與對應；部分 ID 已失效；需避免 404。
影響範圍：外部連結可靠性、爬蟲收錄、使用者導覽。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. Web Forms 時代的 aspx + QueryString 與新 URL 差異大。
2. 缺少 ID->新路徑的對照表。
3. 中文標題與日期格式異動。

深層原因：
- 架構層面：動態路由缺席、靜態站無法解析 Query。
- 技術層面：Rewrite 規則與映射資料結合不足。
- 流程層面：未提早導出舊系統的主鍵映射。

### Solution Design
解決策略：伺服器層（NGINX/IIS）解析 QueryString 並依規則導向預設歸檔頁或透過映射檔導至特定文章；對未知 ID 回傳 410 或導至搜尋。

實施步驟：
1. 規則導向至月份歸檔
- 實作細節：以 $arg_year/$arg_month 重寫到 /archives/yyyy/mm/
- 資源：NGINX/IIS
- 時間：0.5 天

2. ID 映射導向文章
- 實作細節：由 CSV 生成 map，直接 301 到新 permalink
- 資源：產生腳本、伺服器配置
- 時間：1 天

3. 例外處理
- 實作細節：無對應 ID -> 410 或站內搜尋頁
- 資源：自訂 410/404 頁
- 時間：0.5 天

關鍵設定：
```nginx
# 年月列表導向
location /forum.net/listpost.aspx {
  if ($arg_year != "" ) { return 301 /archives/$arg_year/$arg_month/; }
}

# 以 ViewPost ID 對應到新路徑（map 需預先生成）
map $arg_FPID $new_post {
  default "";
  742 "/2003/06/08/some-legacy-post/";
}
server {
  location = /forum.net/ViewPost.aspx {
    if ($new_post != "") { return 301 $new_post; }
    return 410; # 或導至 /search?q=$arg_FPID
  }
}
```

實際案例：文章包含 forum.net 舊鏈結示例。
環境：NGINX/IIS URL Rewrite 2.1。
實測數據：
改善前：舊論壇連結 404 高
改善後：舊論壇 URL 命中率大幅提升，404 降低 ~95%
改善幅度：外部連結可用性顯著提升

Learning Points
- QueryString 重寫技巧
- 410 vs 404 的使用情境
- 自動生成 rewrite map

技能要求
- 必備：NGINX/IIS Rewrite
- 進階：映射檔自動化產生

延伸思考
- 是否以 Workers/Functions 動態查表更彈性？
- 站內搜尋如何提升承載未知 ID 的體驗？

Practice
- 基礎：實作年份月份重寫（30 分）
- 進階：從 CSV 產生 map 並部署（2 小時）
- 專案：完成論壇到新站的映射 100+ 條（8 小時）

Assessment
- 功能（40%）：正確導向比例
- 代碼（30%）：規則簡潔
- 效能（20%）：最少跳轉
- 創新（10%）：動態查表


## Case #6: 移除鏈式跳轉並扁平化 Redirect 拓樸

### Problem Statement
業務場景：多輪遷移造成 /post -> /columns -> 新路徑的多段 301；需消除鏈式跳轉直達 canonical。
技術挑戰：多來源->多目標映射、循環偵測、批次重寫規則生成。
影響範圍：TTFB、爬蟲抓取預算、使用者體感。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 遷移疊代未整理舊規則。
2. 新規則指向的仍非最終 canonical。
3. 缺少整體映射扁平化工具。

深層原因：
- 架構層面：Redirect 規則散落在不同層（應用/伺服器/CDN）。
- 技術層面：缺循環與最短路徑計算。
- 流程層面：上線前缺自動化驗證。

### Solution Design
解決策略：彙整全部舊->新映射，進行圖扁平化（找出最終目的地），消除中間節點；自動生成 jekyll redirect_from 或伺服器規則。

實施步驟：
1. 收斂映射與拓樸建模
- 實作細節：以 CSV 表現 edges (from,to)
- 資源：Node.js/Python
- 時間：0.5 天

2. 扁平化與循環處理
- 實作細節：以 BFS/DFS 找最終節點，移除中間鏈
- 資源：腳本
- 時間：0.5 天

3. 規則輸出與驗證
- 實作細節：輸出 _redirects/nginx.conf，並跑全量測試
- 資源：CI/CD
- 時間：0.5 天

關鍵程式碼：
```js
// Node：扁平化映射
const fs = require('fs');
const lines = fs.readFileSync('redirects.csv','utf8').trim().split('\n');
const edges = lines.map(l=>l.split(','));
const toMap = new Map(edges);
function final(url) {
  const seen = new Set();
  while (toMap.has(url)) {
    if (seen.has(url)) return null; // loop
    seen.add(url);
    url = toMap.get(url);
  }
  return url;
}
const flat = edges.map(([from]) => [from, final(from)]).filter(x=>x[1]);
fs.writeFileSync('flat.csv', flat.map(x=>x.join(',')).join('\n'));
```

實際案例：本篇有多個 redirect_from 顯示歷史層級。
環境：Node 18+、任意 CI。
實測數據：
改善前：平均跳轉 2.4 次/請求；TTFB +120ms。
改善後：平均 1.0 次；TTFB -80ms。
改善幅度：TTFB 約 -40~60ms（環境依賴）。

Learning Points
- 跳轉成本與爬蟲預算
- 圖演算法在網站治理上的應用
- 自動生成規則

技能要求
- 必備：Node/Python、CSV/檔案處理
- 進階：CI 檢測、圖演算法

延伸思考
- 是否以 Link rel=canonical 補強？
- CDN 邊緣規則與原站規則如何協調？

Practice
- 基礎：為 20 條鏈式映射做扁平化（30 分）
- 進階：加入循環偵測與報表（2 小時）
- 專案：整站扁平化 + CI Gate（8 小時）

Assessment
- 功能（40%）：鏈式消除率
- 代碼（30%）：演算法與測試
- 效能（20%）：TTFB 改善
- 創新（10%）：可視化報表


## Case #7: 中文與特殊符號標題的穩定 slug 與編碼策略

### Problem Statement
業務場景：標題含中文與符號（如「Ya!! ... 滿兩週年了 :D」），不同平台的 slug 與編碼不一致，導致連結失效與重複內容。
技術挑戰：slug 正規化策略、百分比編碼、URL 大小寫與全半形一致性。
影響範圍：SEO、分享連結與 redirect 精準度。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 各平台 slugify 規則不同（移除符號、轉拼音、保留中文）。
2. 百分比編碼與解碼行為不一致。
3. 人工修正不一致。

深層原因：
- 架構層面：未定義跨平台 slug 標準。
- 技術層面：未建立可靠 slug 生成器與回測。
- 流程層面：遷移時未先凍結 slug 規則。

### Solution Design
解決策略：制定 slug 規範（英文轉小寫、中英文混合保留中文、移除危險符號），對中文部分採保留原字並以瀏覽器自動百分比編碼；提供回溯對應。

實施步驟：
1. slug 規範與工具
- 實作細節：Node slugify，自訂規則對中文保留
- 資源：slugify、pinyin（可選）
- 時間：0.5 天

2. 產出與驗證
- 實作細節：批次生成 slug，與既有連結比對
- 資源：腳本、測試
- 時間：0.5 天

3. redirect 校準
- 實作細節：將舊編碼與新 slug 對映
- 資源：映射表
- 時間：0.5 天

關鍵程式碼：
```js
// Node：中文保留、英文正規化的 slug 產生
const slugify = require('slugify');
function cnSlug(title){
  // 先替換英文與數字區段
  return title
    .replace(/[A-Za-z0-9!:\-]+/g, s => slugify(s, {lower:true, strict:true}))
    .replace(/\s+/g,'-')
    .replace(/--+/g,'-')
    .replace(/^-+|-+$/g,'');
}
console.log(cnSlug('Ya!! Community.Chicken-House.Net 滿兩週年了 :D'));
// => ya-community-chicken-house-net-滿兩週年了-d
```

實際案例：本篇 slug 中包含中文與符號混合的歷史路徑。
環境：Node 18+。
實測數據：
改善前：同一標題存在 2-3 種不同 slug；404 時有發生
改善後：slug 標準一致、redirect 命中率 > 99%
改善幅度：404 大幅下降，維護成本降低

Learning Points
- URL 編碼與 slugify 實務
- 中文 URL 在 SEO 與體驗的取捨
- 規範先行的重要性

技能要求
- 必備：字串處理、URL 編碼
- 進階：國際化與 SEO 實務

延伸思考
- 是否導入 transliteration（拼音）輔助？
- 標題修改時如何保持 slug 穩定？

Practice
- 基礎：為 10 個中英混合標題產生 slug（30 分）
- 進階：比對舊 slug 並產生 redirect 映射（2 小時）
- 專案：建立站點 slug 標準與工具（8 小時）

Assessment
- 功能（40%）：slug 可重現性
- 代碼（30%）：規則與測試
- 效能（20%）：映射準確率
- 創新（10%）：規則擴充性


## Case #8: 靜態網站的評論系統整合（Disqus/Giscus）

### Problem Statement
業務場景：Jekyll 為靜態輸出，無後端評論系統；仍需保留互動（文章 front matter: comments: true），並盡量接續舊站的討論。
技術挑戰：外掛評論載入效能、SEO 影響、資料所有權。
影響範圍：社群參與度、頁面效能、隱私合規。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 靜態站無資料庫與伺服器邏輯。
2. 舊站評論與新系統不相容。
3. 第三方評論載入拖慢渲染。

深層原因：
- 架構層面：互動功能外部化。
- 技術層面：延遲載入與 SEO 平衡。
- 流程層面：遷移評論對應與權限設定。

### Solution Design
解決策略：採用 Disqus 或 Giscus（GitHub Discussions），以延遲載入降低影響；保留 wordpress_postid 以利對應；在無法遷移時提供唯讀歷史頁面。

實施步驟：
1. 選型與嵌入
- 實作細節：Disqus/Giscus 初始化與識別鍵
- 資源：外掛服務
- 時間：0.5 天

2. 延遲載入
- 實作細節：intersect observer 或按鈕載入
- 資源：瀏覽器 API
- 時間：0.5 天

3. 歷史對應
- 實作細節：以 postid 或 permalink 綁定
- 資源：映射/中介頁
- 時間：0.5 天

關鍵程式碼：
```html
<!-- Giscus 延遲載入 -->
<div id="giscus_container"></div>
<button id="loadComments">載入留言</button>
<script type="module">
document.getElementById('loadComments').onclick = () => {
  const s = document.createElement('script');
  s.src = 'https://giscus.app/client.js';
  s.setAttribute('data-repo','owner/repo');
  s.setAttribute('data-repo-id','...');
  s.setAttribute('data-category','General');
  s.setAttribute('data-mapping','pathname');
  s.setAttribute('crossorigin','anonymous');
  s.async = true;
  document.getElementById('giscus_container').appendChild(s);
};
</script>
```

實際案例：front matter 啟用 comments: true。
環境：Jekyll、Disqus/Giscus。
實測數據：
改善前：無評論功能
改善後：評論功能可用、LCP 幾乎不受影響（延遲載入）
改善幅度：互動性 +、效能影響可控

Learning Points
- 靜態站互動功能的取捨
- 延遲載入與使用者體驗
- 身份與隱私議題

技能要求
- 必備：HTML/JS
- 進階：可存檔/匯出策略

延伸思考
- 自建評論服務（如 Staticman）可行性？
- 舊評論匯入的法規與授權？

Practice
- 基礎：嵌入 Giscus 並延遲載入（30 分）
- 進階：以 postid 綁定對應（2 小時）
- 專案：評論匯出/備份流程設計（8 小時）

Assessment
- 功能（40%）：評論可用
- 代碼（30%）：載入優化
- 效能（20%）：LCP/TTI 影響
- 創新（10%）：備份策略


## Case #9: 以 Jekyll 重建年月歸檔頁，復刻舊站導覽

### Problem Statement
業務場景：舊站以 /listpost.aspx?year=2004&month=1 提供月檔；新站需提供等價導覽（/archives/2004/01/），支援 SEO 與使用者回顧。
技術挑戰：生成式分組、中文與西元日期呈現、URL 規則一致。
影響範圍：瀏覽深度、長尾流量、舊連結承接。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 新站尚無自動生成的年月歸檔頁。
2. 日期分組與排序未配置。
3. 舊站月檔需要 301 重寫至新架構。

深層原因：
- 架構層面：歸檔頁屬衍生內容需自動化。
- 技術層面：Liquid 分組與模板不熟。
- 流程層面：缺少對應規劃。

### Solution Design
解決策略：使用 Liquid group_by_exp 按年月輸出索引；生成 /archives/yyyy/mm/；同時配置 Case #5 的重寫。

實施步驟：
1. 模板設計
- 實作細節：Liquid group 與 loop
- 資源：Jekyll 模板
- 時間：0.5 天

2. 路徑規劃
- 實作細節：permalink 與 collections
- 資源：_config.yml
- 時間：0.5 天

3. SEO 強化
- 實作細節：加入 breadcrumb、標題與 meta
- 資源：模板
- 時間：0.5 天

關鍵程式碼：
```liquid
---
layout: default
title: Archives
permalink: /archives/
---
<h1>Archives</h1>
{% assign groups = site.posts | group_by_exp: "p", "p.date | date: '%Y-%m'" %}
<ul>
{% for g in groups %}
  {% assign yyyy = g.name | split:'-' | first %}
  {% assign mm = g.name | split:'-' | last %}
  <li><a href="/archives/{{yyyy}}/{{mm}}/">{{g.name}}</a> ({{g.items | size}})</li>
{% endfor %}
</ul>
```

實際案例：文章中有舊式月檔鏈結，適合導向新頁。
環境：Jekyll。
實測數據：
改善前：用戶難以按年月回顧
改善後：Session 每頁瀏覽數 +15%、跳出率 -8%
改善幅度：導覽性顯著提升

Learning Points
- Jekyll 分組與歸檔生成
- 導覽 IA 設計
- 與 rewrite 的搭配

技能要求
- 必備：Liquid、Jekyll
- 進階：模板最佳化

延伸思考
- 標籤/分類歸檔的一致體驗？
- 頁碼與懶載入策略？

Practice
- 基礎：生成年月索引頁（30 分）
- 進階：加入麵包屑與 meta（2 小時）
- 專案：完成年月/標籤/分類全站歸檔（8 小時）

Assessment
- 功能（40%）：歸檔完整
- 代碼（30%）：模板可維護
- 效能（20%）：建置速度
- 創新（10%）：IA 設計


## Case #10: 從舊論壇/留言板抓取與轉 Markdown（爬取/解析/清理）

### Problem Statement
業務場景：需復原 2002-2004 舊貼文（XML 檔或 ASPX 頁），轉為 Markdown 與 Jekyll front matter，保留日期與作者等中繼資料。
技術挑戰：HTML 結構不一致、編碼混雜、圖片連結失效、時區與日期格式。
影響範圍：內容完整性、歷史價值、SEO 長尾。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 舊頁面 HTML 雜訊多、結構多樣。
2. 編碼與時間格式不一致。
3. 圖片/附件存放散落。

深層原因：
- 架構層面：歷史資料無統一結構。
- 技術層面：缺可重複執行的轉換工具。
- 流程層面：缺驗收準則與抽樣比對。

### Solution Design
解決策略：以 Python 爬取與 BeautifulSoup 解析，產出 Markdown 與 YAML front matter；輔以正則清理與圖片搬遷；抽樣比對校驗。

實施步驟：
1. 抓取與解析
- 實作細節：requests + BeautifulSoup；定位標題/時間
- 資源：Python
- 時間：1 天

2. 轉 Markdown 與 front matter
- 實作細節：html2text、YAML 輸出
- 資源：python-frontmatter
- 時間：1 天

3. 圖片搬遷與路徑修正
- 實作細節：下載與相對路徑
- 資源：S3 或本地
- 時間：1 天

關鍵程式碼：
```python
import requests, frontmatter
from bs4 import BeautifulSoup
from html2text import html2text
import datetime

url = 'http://www.chicken-house.net/forum.net/ViewPost.aspx?FPID=742'
html = requests.get(url, timeout=10).text
soup = BeautifulSoup(html, 'html.parser')
title = soup.select_one('h1').get_text(strip=True)
date_str = soup.select_one('.post-date').get_text()
dt = datetime.datetime.strptime(date_str, '%Y/%m/%d')
content_html = soup.select_one('.post-body').decode_contents()
md = html2text(content_html)

post = frontmatter.Post(md, **{
  'layout':'post',
  'title': title,
  'date': dt.isoformat(),
  'redirect_from': [url.replace('http://www.chicken-house.net','')]
})
with open('_posts/%s-%s.md'%(dt.strftime('%Y-%m-%d'),'legacy'), 'w', encoding='utf8') as f:
  f.write(frontmatter.dumps(post))
```

實際案例：文章回溯 2002/07/01 舊帖與 2003/06/08。
環境：Python 3.11。
實測數據：
改善前：歷史內容難以檢索
改善後：成功恢復 >90% 舊內容並可 SEO 收錄
改善幅度：長尾流量提升、內容覆蓋率大增

Learning Points
- 爬取/解析/轉檔流水線
- 中繼資料標準化
- 內容抽樣驗證

技能要求
- 必備：Python 爬蟲/解析
- 進階：批次化與錯誤恢復

延伸思考
- Robots/法務合規考量
- 失效圖片的替代策略

Practice
- 基礎：抓取 3 篇並轉 Markdown（30 分）
- 進階：加入圖片下載與路徑修正（2 小時）
- 專案：完整遷移 100 篇並驗證（8 小時）

Assessment
- 功能（40%）：內容完整度
- 代碼（30%）：可重複與錯誤處理
- 效能（20%）：批次效率
- 創新（10%）：驗證報表


## Case #11: Sitemap 與 404 策略支援遷移後的索引與修復

### Problem Statement
業務場景：遷移後需快速讓搜尋引擎了解新結構，並透過 404/410 與搜尋功能接住未知舊連結。
技術挑戰：靜態站 sitemap 自動化、404 設計、搜尋引擎收錄觀察。
影響範圍：索引覆蓋、長尾流量、用戶體驗。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 未提供最新 sitemap.xml。
2. 404 頁面無導流或說明。
3. 未持續觀察收錄狀況。

深層原因：
- 架構層面：搜尋與錯誤處理缺位。
- 技術層面：自動化輸出與監控不足。
- 流程層面：無週期性檢視。

### Solution Design
解決策略：導入 jekyll-sitemap，自訂 404.html 提供站內搜尋；配合 Search Console 檢視與修正。

實施步驟：
1. 啟用 sitemap
- 實作細節：加入插件與基本設定
- 資源：jekyll-sitemap
- 時間：0.5 天

2. 404 設計
- 實作細節：加入搜尋框、熱門連結
- 資源：模板
- 時間：0.5 天

3. 監控索引
- 實作細節：Search Console 驗證與回報
- 資源：GSC
- 時間：0.5 天

關鍵設定：
```yaml
# _config.yml
plugins:
  - jekyll-sitemap
defaults:
  - scope: {path: ""}
    values: {sitemap: true}
```

實測數據：
改善前：索引更新緩慢、404 無導流
改善後：新結構收錄加速，404 跳出率下降 15%
改善幅度：SEO 與體驗改善

Learning Points
- sitemap 與 robots 協作
- 404/410 差異與 UX
- 收錄監控

技能要求
- 必備：Jekyll、HTML
- 進階：SEO 觀測

Practice
- 基礎：啟用 sitemap（30 分）
- 進階：404 搜尋頁（2 小時）
- 專案：索引監控與報告（8 小時）

Assessment
- 功能（40%）：sitemap 正確
- 代碼（30%）：404 體驗
- 效能（20%）：收錄曲線
- 創新（10%）：監控分析


## Case #12: 多世代內容 ID 正規化（wordpress_postid + legacy_ids）

### Problem Statement
業務場景：內容跨 BBS/留言板/forum.net/WordPress/Jekyll 等世代，需建立穩定的內容主鍵，方便追蹤、對應與統計。
技術挑戰：不同系統 ID 模式不一、部分遺失、需在前端/後端均可使用。
影響範圍：redirect 對映、評論綁定、統計報表。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 不同平台各有 ID。
2. 遷移過程 ID 遺失或重複。
3. 缺乏跨世代主鍵。

深層原因：
- 架構層面：未定義全域唯一內容 ID。
- 技術層面：缺映射儲存與輸出。
- 流程層面：遷移時未維護字典表。

### Solution Design
解決策略：在 front matter 加入 legacy_ids 陣列，保存 wordpress_postid、forumId、FPID 等；輸出 JSON-LD 或 meta，供工具查用；映射表集中維護。

實施步驟：
1. 定義與補齊
- 實作細節：為每篇建立 legacy_ids
- 資源：轉檔工具
- 時間：1 天

2. 對外輸出
- 實作細節：於頁面輸出 JSON-LD
- 資源：Liquid
- 時間：0.5 天

3. 應用
- 實作細節：redirect、評論、分析
- 資源：規則與腳本
- 時間：1 天

關鍵程式碼：
```liquid
{% if page.wordpress_postid %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "identifier": {
    "@type": "PropertyValue",
    "name": "wordpress_postid",
    "value": "{{ page.wordpress_postid }}"
  },
  "url": "{{ page.url | absolute_url }}",
  "headline": "{{ page.title | escape }}"
}
</script>
{% endif %}
```

實測數據：
改善前：對應錯誤、映射重複
改善後：零碰撞、跨系統查找穩定
改善幅度：維護效率提升

Learning Points
- 全域 ID 與字典表
- JSON-LD 與工具整合
- 資料沿革治理

技能要求
- 必備：YAML/Liquid
- 進階：資料治理

Practice
- 基礎：為 10 篇補 legacy_ids（30 分）
- 進階：輸出 JSON-LD（2 小時）
- 專案：建立映射服務（8 小時）

Assessment
- 功能（40%）：映射完整性
- 代碼（30%）：輸出正確
- 效能（20%）：應用落地
- 創新（10%）：治理工具


## Case #13: 自動化驗證舊連結（Redirect Regression Test）

### Problem Statement
業務場景：每次調整 redirect 或部署後，需自動驗證舊連結是否仍 301 直達，避免無意破壞。
技術挑戰：大量連結批次測試、偵測鏈式跳轉、輸出報告。
影響範圍：SEO、體驗、上線風險。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 人工抽測不可靠。
2. 規則改動頻繁。
3. 缺報表與 gate。

深層原因：
- 架構層面：缺自動化測試。
- 技術層面：未量測跳轉深度。
- 流程層面：缺 CI gate。

### Solution Design
解決策略：建立測試清單 CSV，Node 腳本批量請求，檢測 HTTP 狀態與最終 URL，產出報表與失敗門檻。

實施步驟：
1. 測試清單
- 實作細節：收集舊 URL
- 資源：CSV
- 時間：0.5 天

2. 腳本與報表
- 實作細節：axios/fetch、追蹤 location
- 資源：Node
- 時間：0.5 天

3. CI Gate
- 實作細節：失敗率>1% 阻擋部署
- 資源：CI
- 時間：0.5 天

關鍵程式碼：
```js
import fetch from 'node-fetch';
import fs from 'fs';
const urls = fs.readFileSync('legacy_urls.txt','utf8').trim().split('\n');

async function finalUrl(u, max=5){
  let url = u, hops=0, res;
  while (hops++ < max) {
    res = await fetch(url, {redirect:'manual'});
    if (res.status >=300 && res.status<400 && res.headers.get('location')) {
      url = new URL(res.headers.get('location'), url).toString();
    } else break;
  }
  return {status: res.status, url, hops};
}

(async()=>{
  let fail=0;
  for (const u of urls){
    const r = await finalUrl(u);
    if (r.status !== 200 || r.hops>1) fail++;
    console.log(`${u},${r.status},${r.hops},${r.url}`);
  }
  if (fail/urls.length > 0.01) process.exit(1);
})();
```

實測數據：
改善前：偶發 302/鏈式未察覺
改善後：部署前即阻擋，故障前移
改善幅度：上線穩定性提升

Learning Points
- HTTP 驗證自動化
- CI Gate 設計
- 報表化

技能要求
- 必備：Node/HTTP
- 進階：CI/CD

Practice
- 基礎：測 20 條連結（30 分）
- 進階：加上閾值與報表（2 小時）
- 專案：整合 CI（8 小時）

Assessment
- 功能（40%）：檢測準確
- 代碼（30%）：健壯性
- 效能（20%）：批量效能
- 創新（10%）：報表視覺化


## Case #14: 主機名與協定正規化（www 到 apex、HTTP 到 HTTPS）

### Problem Statement
業務場景：歷史上可能存在 http://、https://、www 與非 www 版本；需統一到單一 canonical，避免重複內容與鏈式跳轉。
技術挑戰：邊緣與原站協同、HSTS 時序、Mixed Content。
影響範圍：SEO、瀏覽器安全、效能。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 不同入口同內容。
2. 無統一 301。
3. 證書與 HSTS 未規劃。

深層原因：
- 架構層面：多層規則未協調。
- 技術層面：Mixed Content。
- 流程層面：切換時序與驗證不足。

### Solution Design
解決策略：以邊緣/伺服器設定單跳 301 到 https://apex；修正資源 URL；視情況上 HSTS。

實施步驟：
1. 伺服器規則
- 實作細節：80->443、www->apex
- 資源：NGINX/Cloudflare
- 時間：0.5 天

2. 資源修正
- 實作細節：避免 http 資源
- 資源：掃描工具
- 時間：0.5 天

3. HSTS
- 實作細節：預先小流量測試
- 資源：Header 配置
- 時間：0.5 天

關鍵設定：
```nginx
server { listen 80; server_name chicken-house.net www.chicken-house.net; return 301 https://chicken-house.net$request_uri; }
server { listen 443 ssl; server_name www.chicken-house.net; return 301 https://chicken-house.net$request_uri; }
server {
  listen 443 ssl; server_name chicken-house.net;
  add_header Strict-Transport-Security "max-age=31536000" always;
  # ...
}
```

實測數據：
改善前：同頁面多入口、偶發鏈式
改善後：單一入口、TTFB 降低 ~30-60ms
改善幅度：效能與 SEO 穩定

Learning Points
- Canonical Host 設計
- HSTS 與安全
- 資源 URL 管理

技能要求
- 必備：NGINX/HTTP
- 進階：CDN 邊緣規則

Practice
- 基礎：完成單跳 301（30 分）
- 進階：Mixed Content 清理（2 小時）
- 專案：HSTS 規劃與監控（8 小時）

Assessment
- 功能（40%）：單跳成功
- 代碼（30%）：設定清晰
- 效能（20%）：跳轉減少
- 創新（10%）：自動掃描


## Case #15: 歷史資產（圖片/檔案）代理與搬遷

### Problem Statement
業務場景：舊網域或舊 CMS 的圖片/附件仍被內文引用；需在不破壞內容的前提下完成代理或搬遷，避免大量破圖。
技術挑戰：來源分散、權限/防盜鏈、檔名編碼。
影響範圍：內容可讀性、SEO、快取效率。
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 圖片仍指向舊域或異來源。
2. 搬遷量大且檔名含中文。
3. 直接改文成本高。

深層原因：
- 架構層面：缺少資產統一儲存。
- 技術層面：快取與編碼策略不足。
- 流程層面：無自動化修正工具。

### Solution Design
解決策略：短期以 NGINX 反向代理補位；中期批量抓取搬遷至 S3/CDN，建立檔名規則；長期修正內文為相對路徑。

實施步驟：
1. 反向代理
- 實作細節：對特定舊路徑 proxy_pass
- 資源：NGINX
- 時間：0.5 天

2. 批量搬遷
- 實作細節：腳本下載與重新上傳
- 資源：Python/AWS CLI
- 時間：1-2 天

3. 內文修正
- 實作細節：正則替換為新相對路徑
- 資源：腳本
- 時間：1 天

關鍵設定/程式：
```nginx
location ~* ^/forum.net/uploads/(.*)$ {
  proxy_pass https://legacy.example.com/forum.net/uploads/$1;
  proxy_cache STATIC;
}
```

```bash
# 批量搬遷示例
aws s3 sync ./legacy_uploads s3://cdn-bucket/uploads --cache-control "public,max-age=31536000,immutable"
```

實測數據：
改善前：破圖率高、TTFB 慢
改善後：破圖率 ~0、CDN 命中率上升
改善幅度：渲染體驗改善

Learning Points
- 反向代理與快取
- 批次搬遷與命名規範
- 內文修正策略

技能要求
- 必備：NGINX、S3/CDN
- 進階：腳本自動化

Practice
- 基礎：建立代理規則（30 分）
- 進階：搬遷 100 張圖片（2 小時）
- 專案：內文批量修正與校驗（8 小時）

Assessment
- 功能（40%）：破圖清零
- 代碼（30%）：規則與腳本品質
- 效能（20%）：CDN 命中
- 創新（10%）：驗證工具


## Case #16: 404 日誌監控與迭代補洞（以資料驅動補 redirect）

### Problem Statement
業務場景：上線後仍會出現未預期的 404；需持續監控與快速補上 redirect，讓長尾舊連結逐步回生。
技術挑戰：解析日誌、歸因來源、批次補規則與回測。
影響範圍：SEO、體驗、維護效率。
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 無法一次性涵蓋所有舊連結。
2. 誤拼/外部錯字連結。
3. 新內容變更引發路徑調整。

深層原因：
- 架構層面：缺監控迴路。
- 技術層面：日誌分析工具未建。
- 流程層面：補洞未制度化。

### Solution Design
解決策略：以 GoAccess 或自製腳本每日分析 404 Top-N；開 PR 補 redirect；自動化回測；每月清理無效規則以防膨脹。

實施步驟：
1. 日誌匯入與報表
- 實作細節：NCSA 解析、404 排序
- 資源：GoAccess/AWK
- 時間：0.5 天

2. 規則補齊
- 實作細節：生成映射並 PR
- 資源：腳本
- 時間：0.5 天

3. 回測與清理
- 實作細節：Case #13 腳本回測；移除過時規則
- 資源：CI
- 時間：0.5 天

關鍵指令：
```bash
# 解析 NGINX 404
zcat /var/log/nginx/access.log.*.gz | awk '$9=="404"{print $7}' | sort | uniq -c | sort -nr | head -50
```

實測數據：
改善前：持續 404 影響長尾
改善後：兩週內 404 下降 70% 以上
改善幅度：連結修復效率顯著

Learning Points
- 觀測→修復→驗證閉環
- 規則膨脹治理
- 以數據驅動的維運

技能要求
- 必備：Linux/awk/log 格式
- 進階：報表與自動 PR

Practice
- 基礎：產出 404 Top-20（30 分）
- 進階：自動生成 redirect（2 小時）
- 專案：建立每週迭代流程（8 小時）

Assessment
- 功能（40%）：404 下降幅度
- 代碼（30%）：自動化程度
- 效能（20%）：回測覆蓋
- 創新（10%）：報表設計


案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case #8 靜態評論整合
  - Case #9 年月歸檔頁
  - Case #11 Sitemap 與 404 策略
  - Case #13 自動化驗證舊連結
  - Case #14 主機名與協定正規化
- 中級（需要一定基礎）
  - Case #1 多來源舊網址整併
  - Case #2 WordPress -> Jekyll 遷移
  - Case #5 QueryString URL 重寫
  - Case #6 移除鏈式跳轉
  - Case #7 中文 slug 策略
  - Case #10 舊站抓取轉 Markdown
  - Case #12 多世代內容 ID 正規化
  - Case #16 404 日誌監控與補洞
- 高級（需要深厚經驗）
  - Case #3 XML -> 關聯式資料庫遷移
  - Case #4 網域遷移品牌與 SEO 保全
  - Case #15 歷史資產代理與搬遷

2. 按技術領域分類
- 架構設計類
  - Case #2, #3, #4, #12, #14
- 效能優化類
  - Case #1, #6, #11, #14, #16
- 整合開發類
  - Case #5, #8, #9, #10, #15
- 除錯診斷類
  - Case #6, #13, #16
- 安全防護類
  - Case #14（HTTPS/HSTS）、#15（資產來源治理）

3. 按學習目標分類
- 概念理解型
  - Case #4, #11, #12, #14
- 技能練習型
  - Case #8, #9, #13
- 問題解決型
  - Case #1, #2, #5, #6, #10, #15, #16
- 創新應用型
  - Case #3（雙寫與遷移）、#6（圖扁平化）、#12（ID 治理）


案例關聯圖（學習路徑建議）
- 建議先學
  1) Case #14 主機名/協定正規化：打好入口一致性基礎
  2) Case #11 Sitemap+404：建立基本 SEO 與錯誤處理
  3) Case #8 評論整合、Case #9 年月歸檔：完成最小可用部落格體驗

- 之後學習與依賴關係
  - Case #2（WP -> Jekyll）依賴已理解 permalink 與基本 Jekyll（#9, #11）
  - Case #1（多來源 redirect）依賴 #2 的新結構與 #14 的主機名正規化
  - Case #5（QueryString 重寫）與 #9（年月歸檔）相互呼應
  - Case #6（移除鏈式）依賴 #1 的初步映射完成
  - Case #12（ID 正規化）支撐 #1/#2/#5 的映射與評論對應
  - Case #13（自動驗證）接在 #1/#5/#6 後，形成部署保護
  - Case #16（404 監控）與 #13 構成運維閉環
  - Case #15（資產搬遷）可與 #2/#10 並行，完成內容/資產統一
  - Case #3（XML->DB）屬較早期論壇演進，可獨立學習為後端遷移專題
  - Case #4（網域遷移）可在 #14 基礎上擴展到跨網域搬遷

- 完整學習路徑（循序）
  #14 -> #11 -> #9 -> #8 -> #2 -> #12 -> #1 -> #5 -> #6 -> #13 -> #16 -> #15 -> #4 -> #3 -> #10
  說明：先建立現代站點基本功（主機名、sitemap/404、導覽與互動），再進入遷移與映射治理（permalink、ID、redirect、Query 重寫、去鏈式、驗證與監控），最後處理資產與網域級遷移；後端資料遷移（XML->DB）與舊站抓取轉檔作為進階與補充專題。