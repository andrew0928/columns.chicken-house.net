以下內容僅能從提供的文章與其 front matter 資訊中擷取與推論。文章本體雖無技術討論，但 front matter 顯示了多個舊網址 redirect_from、含 .aspx 舊路徑、含中文與十六進位 slug、多來源舊平台路徑與 wordpress_postid 等，能明確反映出「部落格/內容系統遷移」的技術問題與做法。下列 16 個案例均以此為依據進行結構化整理，提供完整的教學與實作價值；數據面因原文未提供，改以可量測指標與測試方法描述。

## Case #1: 統一舊網址到新永久連結的 301 導向策略

### Problem Statement（問題陳述）
業務場景：網站多次由舊平台遷移，新舊網址格式並存（含中文 slug、.aspx、不同目錄層級等）。為保留歷史外部連結與搜尋引擎權重，需要將所有舊網址穩定導向至單一新永久連結，避免 404 與權重分散。
技術挑戰：在靜態站（例如 Jekyll）缺乏集中式路由器的情況下，如何以低成本維護大量導向規則，且確保皆為 301 永久導向。
影響範圍：SEO 排名、社群與外部站點既有連結、使用者體驗與轉換率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 歷史平台多樣（.NET/.aspx、WordPress、靜態站）造成多種舊網址樣式並存。
2. 中文 slug、十六進位 slug、目錄差異（/columns、/post、/blogs/...）導致路徑不一致。
3. 缺乏集中式路由層，難以「一次來源，多處收斂」。

深層原因：
- 架構層面：由動態轉靜態後，少了應用層路由集中協調機制。
- 技術層面：缺少統一的 rewrite/redirect 策略與工具鏈。
- 流程層面：遷移前未建立網址規格與映射清單的盤點流程。

### Solution Design（解決方案設計）
解決策略：在內容前言以 jekyll-redirect-from 定義逐條映射，並輔以伺服器或代管層（Nginx/Netlify）做全站通用規則（如 .aspx 去除），所有舊網址一跳直達新 canonical URL，並以自動化測試驗證。

實施步驟：
1. 建立舊→新網址映射清單
- 實作細節：從資料庫/匯出清單/站內搜尋收集所有舊路徑。
- 所需資源：CSV/Spreadsheet
- 預估時間：4-8 小時（依規模）

2. 啟用 jekyll-redirect-from
- 實作細節：在 _config.yml 啟用插件，於文章 front matter 填寫 redirect_from。
- 所需資源：jekyll-redirect-from
- 預估時間：0.5 小時

3. 伺服器層通用規則
- 實作細節：以 Nginx/Netlify 針對 .aspx、尾斜線等制訂一律重寫。
- 所需資源：Nginx/Netlify
- 預估時間：1-2 小時

4. 驗證與監控
- 實作細節：以 curl/站點健康檢查驗證 301 並量測跳數。
- 所需資源：curl、腳本
- 預估時間：1-2 小時

關鍵程式碼/設定：
```yaml
# _config.yml
plugins:
  - jekyll-redirect-from

# 文章 front matter（摘自本文）
redirect_from:
  - /2005/03/29/優秀青年-329-不放假/
  - /columns/post/2005/03/29/e584aae7a780e99d92e5b9b42c-329-e4b88de694bee58187.aspx/
  - /blogs/chicken/archive/2005/03/29/459.aspx/
```

實際案例：本文 front matter 出現多個 redirect_from 明確示範多舊址匯流至新頁的做法。
實作環境：Jekyll 4.x、Ruby 3.x、jekyll-redirect-from、Nginx/Netlify 任一。
實測數據：
改善前：可能存在多條舊鏈結 404 或多跳導向。
改善後：所有舊鏈結以 1 次 301 直達新頁。
改善幅度：以「404 次數」「平均導向跳數」作為衡量（目標：404 ≈ 0、平均跳數 = 1）。

Learning Points（學習要點）
核心知識點：
- 301/302 差異與 SEO 影響
- 靜態站導向策略與 jekyll-redirect-from
- 以映射清單控管遷移風險

技能要求：
必備技能：YAML/HTTP 狀態碼/基本伺服器設定
進階技能：Nginx rewrite/Netlify _redirects 策略化管理

延伸思考：
- 可用於任何 CMS→SSG 遷移場景
- 風險：規則散落多處、人工作業出錯
- 進一步優化：集中生成映射、導向自動化測試

Practice Exercise（練習題）
基礎練習：為 3 條舊網址設定 redirect_from 並用 curl 驗證 301。
進階練習：加入 Nginx/.aspx 通用規則並確保不與頁內映射衝突。
專案練習：撰寫腳本從清單自動生成 redirect_from 與 _redirects。

Assessment Criteria（評估標準）
功能完整性（40%）：所有舊網址 301 直達新頁
程式碼品質（30%）：規則清晰、重複最小化
效能優化（20%）：無導向鏈、低延遲
創新性（10%）：自動化映射生成或檢測工具

---

## Case #2: 兼容中文網址與十六進位化 Slug 的路由映射

### Problem Statement（問題陳述）
業務場景：歷史文章同一標題曾用中文 slug 與十六進位字串 slug（如 e584aa...）兩種形式發佈。不同外部站點與收藏都可能保留其一，需要同時相容並導回新網址。
技術挑戰：如何識別並解碼十六進位 slug、避免誤判，並批量為兩種舊格式建立映射。
影響範圍：歷史收藏連結、SEO、內部舊文章互鏈。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 過去平台對非拉丁字元 slug 的處理方式不同（中文直出 vs 十六進位串）。
2. 工具與瀏覽器對編碼支援不一，導致路徑多樣。
3. 遷移時未統一轉換策略。

深層原因：
- 架構層面：缺乏 slug 正規化層。
- 技術層面：編碼/轉碼規則未內建於部署流程。
- 流程層面：缺少遷移前的編碼策略與清單。

### Solution Design（解決方案設計）
解決策略：建立檢測與轉換流程，自動將十六進位 slug 還原為 Unicode 進行匹配，再生成對應 redirect_from；中文 slug 亦納入對照表，保障雙路徑導向。

實施步驟：
1. 偵測十六進位 slug
- 實作細節：以正則比對路徑片段是否為 hex 序列。
- 所需資源：正規表達式、腳本語言
- 預估時間：2 小時

2. 解碼與對照
- 實作細節：將 hex pair 轉 UTF-8 字串，與標題匹配。
- 所需資源：Ruby/Node 腳本
- 預估時間：2 小時

3. 生成 redirect_from
- 實作細節：更新前言或集中 _redirects。
- 所需資源：jekyll-redirect-from/Netlify
- 預估時間：1 小時

關鍵程式碼/設定：
```ruby
# detect_and_decode_hex_slug.rb
def hexslug_to_utf8(hex)
  [hex].pack('H*').force_encoding('UTF-8')
end

path = "/post/2005/03/29/e584aae7a7..."
hex = path[%r{/([0-9a-f]{6,})}, 1]
title = hexslug_to_utf8(hex) if hex
```

實際案例：本文 redirect_from 同時含中文 slug 與 e584aa... 形式。
實作環境：Jekyll、Ruby/Node 腳本、jekyll-redirect-from。
實測數據：
改善前：十六進位 slug 連結 404
改善後：兩種舊形式均 301 到新頁
改善幅度：404 事件目標趨近 0

Learning Points
核心知識點：URL 編碼差異、slug 正規化、批量映射
技能要求：正規表達式、字元編碼、腳本開發
延伸思考：可擴充至拼音轉寫與多語系 slug 對照；注意誤判與安全檢核

Practice Exercise
基礎：撰寫函式將 e58f... 轉回 UTF-8
進階：對資料集檢測並產生映射清單
專案：自動掃描站內所有路徑生成 redirect_from

Assessment Criteria
功能完整性：雙格式皆導向成功
程式碼品質：轉碼正確、單元測試齊備
效能優化：批處理時間可接受
創新性：自動提取與比對邏輯

---

## Case #3: 去除 .aspx 副檔名的 URL 重寫

### Problem Statement（問題陳述）
業務場景：舊站為 .NET 引擎，網址以 .aspx 結尾；新站改為靜態、無副檔名的永久連結。大量外部連結仍指向 .aspx，造成 404 或重複內容。
技術挑戰：在不改動內容檔的情況下，以伺服器/代管層統一去除 .aspx 且 301 到對應新路徑。
影響範圍：SEO、使用者體驗、分析歸因。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 平台切換造成 URL 形態差異。
2. 缺乏通用的副檔名重寫規則。
3. 以頁內映射維護成本高。

深層原因：
- 架構層面：未在邊界層抽象 URL 規格。
- 技術層面：rewrite 規則缺失。
- 流程層面：遷移未建立「副檔名策略」。

### Solution Design（解決方案設計）
解決策略：以 Nginx/Netlify 設定通用規則，將所有 *.aspx 以 301 導到去副檔名後的對應路徑；對個別不規則案例再用 redirect_from 補強。

實施步驟：
1. 設定伺服器規則
- 實作細節：正則抓取 .aspx 前的路徑並 301。
- 所需資源：Nginx/Netlify
- 預估時間：1 小時

2. 例外清單補強
- 實作細節：前言 redirect_from 補特殊案例。
- 所需資源：jekyll-redirect-from
- 預估時間：1 小時

關鍵程式碼/設定：
```nginx
location ~ ^(.+)\.aspx/?$ {
  return 301 $1/;
}
```

或 Netlify:
```conf
# _redirects
/*.aspx   /:splat  301!
```

實際案例：本文多條 redirect_from 為 .aspx 舊路徑。
實作環境：Nginx/Netlify + Jekyll
實測數據：以 404 降幅、導向跳數為衡量（目標 1 跳）

Learning Points：rewrite 與 redirect 差異、正則重寫技巧
技能要求：基本 Nginx/Netlify 設定
延伸思考：避免與頁內導向互相打架

Practice Exercise：寫出去 .php/.html 的等效規則
進階：混用伺服器規則與頁內 redirect_from
專案：為全站生成 _redirects 並自動測試

Assessment Criteria：規則正確率、相容性、效能與可維護性

---

## Case #4: 以舊系統數字 ID 對應新 Slug 的導向生成

### Problem Statement（問題陳述）
業務場景：舊站使用數字 ID（如 /archive/.../459.aspx）標識文章，新站採用日期+slug。需將以 ID 為主的連結導回新永久連結。
技術挑戰：缺少資料庫可查詢 ID→新 permalink，且數量龐大。
影響範圍：外部引用、RSS 歷史項目、內部連結。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 標識方式變更（ID→slug）。
2. 無中央查詢層。
3. 無 ID 與新路徑的對照表。

深層原因：
- 架構層面：資料拆離應用（靜態）
- 技術層面：缺乏生成器自動產出導向頁
- 流程層面：匯出對照前置作業不足

### Solution Design（解決方案設計）
解決策略：建立 ids.yml 對照表，由 Jekyll Generator 插件在 build 期自動產出對應導向頁或 _redirects 條目，維持單一真相來源。

實施步驟：
1. 準備對照表
- 實作細節：蒐集舊 ID 與新 URL
- 所需資源：ids.yml
- 預估時間：8 小時（依量）

2. 撰寫 Generator
- 實作細節：讀取 ids.yml，自動輸出重定向頁或清單
- 所需資源：Jekyll plugin
- 預估時間：3 小時

3. 測試與部署
- 實作細節：抽樣驗證、全量測試
- 所需資源：腳本/CI
- 預估時間：2 小時

關鍵程式碼/設定：
```ruby
# _plugins/id_redirects.rb
module Jekyll
  class IdRedirects < Generator
    safe true
    priority :low
    def generate(site)
      ids = site.data['ids'] || {}
      ids.each do |old_id, new_url|
        site.pages << RedirectPage.new(site, site.source, "legacy/#{old_id}", new_url)
      end
    end
  end

  class RedirectPage < Page
    def initialize(site, base, dir, dest)
      @site, @base, @dir, @name = site, base, dir, "index.html"
      self.process(@name)
      self.data = { "layout" => nil, "redirect_to" => dest }
      self.content = "<!doctype html><meta http-equiv='refresh' content='0;url=#{dest}'>"
    end
  end
end
```

實際案例：本文 redirect_from 含 /archive/2005/.../459.aspx 類型。
實作環境：Jekyll、Ruby、自訂 Generator
實測數據：以隨機抽樣 100 條導向成功率為衡量（目標 ≈ 100%）

Learning Points：資料驅動的導向生成、Jekyll 擴展
技能要求：Ruby/Jekyll 插件、資料對照管理
延伸思考：亦可輸出 Netlify _redirects 以提升效能

Practice Exercise：建立 ids.yml 並生成 10 條導向
進階：加上單元測試、處理 404 fallback
專案：製作 CLI 將 CSV 轉 ids.yml 與 _redirects

Assessment Criteria：自動化程度、正確率、可維護性

---

## Case #5: 規範結尾斜線與 Canonical，消除重複內容

### Problem Statement（問題陳述）
業務場景：舊網址存在有無尾斜線兩種版本，搜尋引擎可能同時收錄，導致重複內容與權重分散。
技術挑戰：以最少規則達成單一政策（全加或全去），並加上 canonical 標記。
影響範圍：SEO、收錄品質、爬蟲配額。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：歷史連結生成不一致、伺服器預設不同。
深層原因：
- 架構：無全站 URL 正規化策略
- 技術：缺少 canonical 與 rewrite
- 流程：未在發佈流程校驗

### Solution Design（解決方案設計）
解決策略：伺服器層規範尾斜線，前端模板加入 canonical，確保所有舊連結 301 到單一版本。

實施步驟：
1. 制定尾斜線政策
- 實作細節：選擇「全加/全去」
- 所需資源：規範文件
- 預估時間：0.5 小時

2. Nginx 重寫
- 實作細節：將非標準形式 301 到標準
- 所需資源：Nginx
- 預估時間：1 小時

3. 模板加 canonical
- 實作細節：head.html 注入 canonical
- 所需資源：Liquid
- 預估時間：0.5 小時

關鍵程式碼/設定：
```liquid
<link rel="canonical" href="{{ page.url | absolute_url }}" />
```

實際案例：本文提供多個尾斜線/不同層級路徑示例可歸一化。
實作環境：Jekyll + Nginx/Netlify
實測數據：重複收錄量下降、平均導向跳數 = 1（目標）

Learning Points：URL 正規化、canonical 的 SEO 作用
技能要求：Nginx/Liquid
延伸思考：配合 sitemap 只輸出 canonical

Practice Exercise：為 3 個頁面加入 canonical 並測試
進階：Nginx 實作尾斜線規則
專案：產生 canonical+_redirects 的整合方案

Assessment Criteria：收斂策略正確、規則簡潔、驗證充分

---

## Case #6: 修正絕對資源路徑在子路徑部署的圖片 404

### Problem Statement（問題陳述）
業務場景：圖片使用以 / 開頭的絕對路徑，若部署於子目錄（如 GitHub Pages 專案頁 /repo），將導致資源 404。
技術挑戰：兼顧根域與子路徑部署，避免重寫所有文章。
影響範圍：媒體顯示、內容可讀性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：以站根為基準的絕對路徑。
深層原因：
- 架構：多部署目標未考量
- 技術：未使用 baseurl/relative_url
- 流程：無資源連結檢測

### Solution Design（解決方案設計）
解決策略：以 Liquid relative_url 或 prepend site.baseurl 產生資源路徑，模板層統一處理，不改動內容。

實施步驟：
1. 設定 baseurl
- 實作細節：_config.yml 設定 baseurl
- 所需資源：Jekyll
- 預估時間：0.5 小時

2. 改模板 helper
- 實作細節：以 filter 產出正確 URL
- 所需資源：Liquid
- 預估時間：1 小時

關鍵程式碼/設定：
```liquid
<img src="{{ '/images/2005-03-29-excellent-youth-no-holiday-329/emotion-39.gif' | relative_url }}" alt="表情圖示">
```

實際案例：本文圖片路徑為 /images/...，適用此修正。
實作環境：Jekyll、Liquid
實測數據：子路徑部署下圖片 404 減為 0

Learning Points：baseurl/relative_url 機制
技能要求：Jekyll 配置、Liquid 基礎
延伸思考：建立圖片 URL helper include

Practice Exercise：改 3 處圖片為 relative_url
進階：寫 include: image.html 自動處理
專案：掃描並批次替換站內資源路徑

Assessment Criteria：子路徑可用性、模板抽象程度、無副作用

---

## Case #7: 非拉丁標題的資產目錄命名與 Slugify

### Problem Statement（問題陳述）
業務場景：中文標題對應的資產目錄需要穩定的 ASCII 命名，避免跨平台/雲端儲存的字元相容問題。
技術挑戰：建立一致的 slug 規則與自動生成流程。
影響範圍：CDN 快取、部署、備份。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：不同系統對非拉丁字元支援差異。
深層原因：
- 架構：缺乏命名策略
- 技術：未使用 slugify
- 流程：無標準化產生工具

### Solution Design（解決方案設計）
解決策略：使用 Liquid 的 slugify: "latin" 將標題轉為 ASCII，或在前言加入 assets_slug，統一資產目錄命名。

實施步驟：
1. 制定命名規範
- 實作細節：slugify 模式選擇
- 所需資源：規範文件
- 預估時間：0.5 小時

2. 模板改造
- 實作細節：image path 使用 page.assets_slug 或 slugify(title)
- 所需資源：Liquid
- 預估時間：1 小時

關鍵程式碼/設定：
```liquid
{% assign assets_dir = page.assets_slug | default: page.title | slugify: "latin" %}
<img src="{{ '/images/' | append: assets_dir | append: '/emotion-39.gif' | relative_url }}" alt="表情">
```

實際案例：本文圖片目錄為英文化的 excellent-youth-no-holiday-329。
實作環境：Jekyll、Liquid
實測數據：跨平台路徑相容性問題顯著降低

Learning Points：slugify 模式與可重複命名
技能要求：Liquid/前端模板
延伸思考：將 assets_slug 作為前言欄位標準化

Practice Exercise：為 3 篇文章生成 assets_slug
進階：寫 CI 檢查 assets_slug 缺失
專案：把既有資產目錄自動重命名並改連結

Assessment Criteria：一致性、可維護性、對舊連結影響最小

---

## Case #8: 靜態站點開放留言：用 comments: true 驅動外掛整合

### Problem Statement（問題陳述）
業務場景：文章 front matter 以 comments: true 標示可留言，但靜態站需整合第三方（Disqus、Giscus、Utterances、Staticman）提供互動。
技術挑戰：在不影響載入效能與隱私前提下，實現可控的留言切換。
影響範圍：互動率、隱私合規、頁面效能。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：靜態站無後端留言系統。
深層原因：
- 架構：前端載入第三方腳本
- 技術：條件載入與 SEO 影響
- 流程：GDPR/隱私告知未規劃

### Solution Design（解決方案設計）
解決策略：建立 comments.html include，依 page.comments 與環境變數載入指定供應商，延遲載入腳本並顯示同意提示。

實施步驟：
1. 選擇供應商
- 實作細節：評估隱私/效能
- 所需資源：比較表
- 預估時間：1 小時

2. 建置 include
- 實作細節：根據 front matter 條件渲染
- 所需資源：Liquid、供應商腳本
- 預估時間：1 小時

3. 效能與隱私
- 實作細節：延遲載入、同意彈窗
- 所需資源：JS
- 預估時間：2 小時

關鍵程式碼/設定：
```liquid
{% if page.comments %}
  {% include comments.html provider=site.comments.provider %}
{% endif %}
```

實際案例：本文 front matter 有 comments: true。
實作環境：Jekyll、選定第三方留言外掛
實測數據：互動率、首屏 LCP/JS 載入延遲（以 Web Vitals 監測）

Learning Points：條件載入、隱私與效能權衡
技能要求：Liquid/前端整合
延伸思考：以 Edge Functions 注入、或自建 API

Practice Exercise：接入一種留言服務並條件載入
進階：加入同意管理與延遲載入
專案：可切換的多供應商留言模組

Assessment Criteria：功能可用、效能影響最小、隱私提示完善

---

## Case #9: 中文標籤（tags）索引頁自動化與編碼處理

### Problem Statement（問題陳述）
業務場景：tags: ["有的沒的"] 等中文標籤需要索引頁與列表頁，且需處理 URL slug 與排序。
技術挑戰：中文標籤的 slug 化、產生靜態索引頁、避免編碼陷阱。
影響範圍：導航體驗、SEO、站內檢索。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：Jekyll 預設不會自動生成 tag 頁。
深層原因：
- 架構：缺少標籤索引生成器
- 技術：中文 slug 與排序
- 流程：標籤規格未統一

### Solution Design（解決方案設計）
解決策略：撰寫 Tag Generator 以 slugify 生成路徑，建立 tags/:slug/ 頁面並輸出對應文章列表。

實施步驟：
1. 設定標籤規範
- 實作細節：中文保留 or 轉寫策略
- 所需資源：規格文件
- 預估時間：1 小時

2. Generator 插件
- 實作細節：遍歷 site.tags，自動產頁
- 所需資源：Jekyll 插件
- 預估時間：2 小時

關鍵程式碼/設定：
```ruby
# _plugins/tags.rb
module Jekyll
  class TagPage < Page; end
  class TagGenerator < Generator
    safe true
    def generate(site)
      site.tags.each do |tag, posts|
        slug = Utils.slugify(tag, mode: "latin")
        # 產生 /tags/slug/index.html
      end
    end
  end
end
```

實際案例：本文含中文 tag。
實作環境：Jekyll、Ruby
實測數據：tags 頁面可導覽、404 為 0

Learning Points：Jekyll tag 機制、slugify 模式
技能要求：Ruby、Liquid
延伸思考：多語系標籤、標籤權重與熱門排序

Practice Exercise：生成 3 個 tag 頁
進階：tag 頁支援分頁
專案：標籤雲與 SEO schema 標記

Assessment Criteria：生成正確、URL 乾淨、可擴展

---

## Case #10: 最小化導向跳數：避免導向鏈

### Problem Statement（問題陳述）
業務場景：多次遷移造成舊→較新→最新的導向鏈，導致耗時、可能丟失 referrer 與權重稀釋。
技術挑戰：建立「所有舊址一跳直達」原則並驗證。
影響範圍：效能、SEO、追蹤準確度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：疊加導向規則未整併。
深層原因：
- 架構：導向分散於多層
- 技術：缺乏跳數檢測工具
- 流程：變更未回寫至來源映射

### Solution Design（解決方案設計）
解決策略：以集中清單重新生成「源→終」導向，並用自動化工具量測 num_redirects，持續化在 CI。

實施步驟：
1. 匯總所有導向來源
- 實作細節：爬取/整理 redirect_from、伺服器規則
- 所需資源：清單與腳本
- 預估時間：3 小時

2. 生成直達規則
- 實作細節：去除中間層，直接映射到 canonical
- 所需資源：_redirects 或前言
- 預估時間：2 小時

3. 自動化檢測
- 實作細節：curl -I -L 測 num_redirects
- 所需資源：CI
- 預估時間：2 小時

關鍵程式碼/設定：
```bash
while read url; do
  curl -s -o /dev/null -w "%{num_redirects}\n" -I -L "$url"
done < old_urls.txt
```

實際案例：本文多來源舊路徑適合合併為直達。
實作環境：任何代管 + CI
實測數據：平均跳數→1；耗時降低

Learning Points：導向鏈危害、量測方法
技能要求：shell/curl、CI
延伸思考：以邊緣層（CDN）實現更快導向

Practice Exercise：檢測 20 條舊址跳數
進階：自動回寫直達規則
專案：導向健康儀表板

Assessment Criteria：跳數降幅、規則可讀性、持續化檢測

---

## Case #11: Sitemap 與 Canonical 同步，避免多路徑被收錄

### Problem Statement（問題陳述）
業務場景：舊路徑仍可被爬取導向至新頁，若 sitemap 未同步 canonical，搜尋引擎可能混淆。
技術挑戰：只輸出 canonical URL 至 sitemap，同時 head 注入 canonical。
影響範圍：收錄效率、權重集中。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：sitemap 預設輸出所有可見頁。
深層原因：
- 架構：缺少 canonical 標準化
- 技術：sitemap 模板未過濾
- 流程：SEO 工單缺失

### Solution Design（解決方案設計）
解決策略：使用 jekyll-sitemap 或自定模板只輸出 page.canonical_url，並在模板加入 rel=canonical。

實施步驟：
1. 啟用 jekyll-sitemap
- 實作細節：依官方建議配置
- 所需資源：插件
- 預估時間：0.5 小時

2. 模板 canonical
- 實作細節：以 absolute_url 生成
- 所需資源：Liquid
- 預估時間：0.5 小時

關鍵程式碼/設定：
```yaml
plugins:
  - jekyll-sitemap
```

實際案例：本文映射眾多舊路徑，需確保 sitemap 單一路徑。
實作環境：Jekyll
實測數據：GSC 重複內容警示下降

Learning Points：sitemap 與 canonical 互補
技能要求：Jekyll 插件、Liquid
延伸思考：配合 hreflang、多語系 sitemap

Practice Exercise：啟用並檢查 sitemap.xml
進階：自定義 sitemap 過濾草稿/非 canonical
專案：建立 SEO 檢查清單

Assessment Criteria：sitemap 正確性、收錄效率

---

## Case #12: 時區設定與日期型永久連結的一致性

### Problem Statement（問題陳述）
業務場景：永久連結採用 /年/月/日/ 樣式（如 2005/03/29），若建置時區不同可能產生日期偏移，導致連結不一致。
技術挑戰：各環境（本機、CI、伺服器）必須使用同一時區。
影響範圍：URL 正確性、導向規則匹配、RSS。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：預設使用 UTC 或系統時區。
深層原因：
- 架構：未設定站點時區
- 技術：CI 與本機不一致
- 流程：缺乏環境標準化

### Solution Design（解決方案設計）
解決策略：在 _config.yml 設定 timezone（例：Asia/Taipei），並於 CI 指定 TZ 環境變數。

實施步驟：
1. 設定站點時區
- 實作細節：_config.yml timezone
- 所需資源：Jekyll
- 預估時間：0.5 小時

2. CI 對齊
- 實作細節：在 workflow 設定 TZ
- 所需資源：CI
- 預估時間：0.5 小時

關鍵程式碼/設定：
```yaml
# _config.yml
timezone: Asia/Taipei
```

實際案例：本文路徑為 2005/03/29，需與時區一致。
實作環境：Jekyll、CI
實測數據：不同環境 build URL 一致

Learning Points：時間與 URL 的耦合
技能要求：Jekyll 配置、CI 變數
延伸思考：跨時區作者協作時的規範

Practice Exercise：在 CI 設定 TZ 並驗證輸出
進階：RSS/Atom 日期驗證
專案：時間/日期一致性的 E2E 測試

Assessment Criteria：一致性、測試覆蓋

---

## Case #13: 中文標題 SEO Slug 生成（拼音/轉寫）

### Problem Statement（問題陳述）
業務場景：中文標題若直接作為 URL 可能遇到編碼與分享相容性，需生成 SEO 友善的 ASCII slug（如拼音、翻譯）。
技術挑戰：建立穩定、可重現的轉寫規則並避免歧義。
影響範圍：分享可用性、國際化 SEO。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：不同工具對中文轉寫不一。
深層原因：
- 架構：缺乏 slug 生成策略
- 技術：轉寫庫差異、繁簡轉換
- 流程：人工調整未被記錄

### Solution Design（解決方案設計）
解決策略：引入轉寫庫（Ruby pinyin 或外部服務）生成拼音 slug，並提供 front matter 手動覆蓋欄位 slug 以處理歧義。

實施步驟：
1. 引入轉寫庫
- 實作細節：Gemfile 加入 chinese_pinyin
- 所需資源：Ruby
- 預估時間：1 小時

2. 寫 slug 過濾器
- 實作細節：自訂 Liquid filter：title_to_slug
- 所需資源：Jekyll 插件
- 預估時間：2 小時

3. 手動覆蓋
- 實作細節：front matter slug 欄位
- 所需資源：內容規範
- 預估時間：0.5 小時

關鍵程式碼/設定：
```ruby
# _plugins/slug.rb
require 'chinese_pinyin'
module Jekyll
  module Slug
    def title_to_slug(str)
      Pinyin.t(str, splitter: '-').downcase.gsub(/[^a-z0-9\-]/, '')
    end
  end
end
Liquid::Template.register_filter(Jekyll::Slug)
```

實際案例：本文圖片目錄已英文化，可延伸為 URL slug 策略。
實作環境：Jekyll、Ruby
實測數據：分享成功率提高（以點擊/錯誤回報衡量）

Learning Points：i18n slug 與 SEO
技能要求：Ruby、文本處理
延伸思考：多語系路徑與 hreflang 配合

Practice Exercise：為 5 個中文標題產出拼音 slug
進階：加入停用詞/縮短規則
專案：全站 slug 再生成與導向自動化

Assessment Criteria：可讀性、穩定性、可覆蓋策略

---

## Case #14: 圖片替代文字與無障礙校驗流程

### Problem Statement（問題陳述）
業務場景：歷史文章圖片 alt 文字可能為佔位（如 “emotion”），不利可及性與 SEO。
技術挑戰：在不重寫內容的前提下提升 alt 品質，並建立檢測流程。
影響範圍：無障礙合規、搜尋可見性、使用者體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：舊平台匯入時未帶入語義化 alt。
深層原因：
- 架構：模板未強制 alt
- 技術：缺乏靜態檢測
- 流程：發布未設計檢查項

### Solution Design（解決方案設計）
解決策略：建立圖片 include，要求 alt 為必填；引入 html-proofer 在 CI 檢測缺失，逐步補齊。

實施步驟：
1. include 改造
- 實作細節：若缺 alt 則報警或提供自動填入策略
- 所需資源：Liquid
- 預估時間：1 小時

2. CI 檢測
- 實作細節：html-proofer 檢查 alt
- 所需資源：Ruby/CI
- 預估時間：1 小時

關鍵程式碼/設定：
```liquid
{% include image.html src=img_path alt=page.image_alt %}
```

實際案例：本文圖片 alt “emotion” 可作為改善目標示例。
實作環境：Jekyll、html-proofer
實測數據：alt 缺失告警數下降

Learning Points：a11y 基礎、SEO 與可及性關聯
技能要求：模板工程、CI
延伸思考：以 AI/標題自動生成 alt 初稿

Practice Exercise：替換 5 張圖為 include 並完善 alt
進階：CI 封鎖 alt 缺失 PR
專案：掃描全站生成 alt 任務清單

Assessment Criteria：alt 覆蓋率、流程固化程度

---

## Case #15: 建置 CI 斷鏈與導向驗證（html-proofer）

### Problem Statement（問題陳述）
業務場景：遷移後易出現 404、圖片失連、導向跳數過多。需要在建置階段即攔截。
技術挑戰：CI 自動檢測內外部連結與圖片、導向是否過多。
影響範圍：上線品質與風險控制。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：缺少自動化檢測。
深層原因：
- 架構：無品質門檻
- 技術：未導入檢測工具
- 流程：缺乏失敗準則

### Solution Design（解決方案設計）
解決策略：以 html-proofer 驗證站點輸出，結合 curl 腳本檢測導向跳數，設為 PR 檢查與 build gate。

實施步驟：
1. 安裝工具
- 實作細節：bundle add html-proofer
- 所需資源：Ruby
- 預估時間：0.5 小時

2. CI 工作流程
- 實作細節：GitHub Actions 配置
- 所需資源：.github/workflows
- 預估時間：1 小時

關鍵程式碼/設定：
```yaml
# .github/workflows/ci.yml
- name: HTMLProofer
  run: |
    bundle exec htmlproofer ./_site --check-external-hash --http-status-ignore "999" --url-ignore "/localhost/"
```

實際案例：本文多導向與圖片路徑特徵適合納入檢測。
實作環境：GitHub Actions、Ruby
實測數據：PR 失敗率因早期攔截上升、上線 404 降低

Learning Points：CI 驗收門檻設計
技能要求：CI、Ruby 工具
延伸思考：加入 Lighthouse、Webhint 等

Practice Exercise：為專案新增 HTMLProofer 檢查
進階：加入導向跳數檢查腳本
專案：完整的靜態站品質檢查工作流

Assessment Criteria：檢測覆蓋、誤報率、可維護性

---

## Case #16: 大量導向規則的效能優化（Nginx map/Netlify _redirects）

### Problem Statement（問題陳述）
業務場景：導向規則數量龐大且分散於各文章，建置與請求處理效率受影響。
技術挑戰：集中化規則、以高效資料結構處理匹配，縮短回應時間。
影響範圍：首字節時間、伺服器負載、可維護性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：規則分佈多處、重複與覆蓋。
深層原因：
- 架構：無集中導向層
- 技術：逐條比對效率低
- 流程：缺乏定期去重與壓縮

### Solution Design（解決方案設計）
解決策略：將散落的 redirect_from 彙整輸出為伺服器層映射（Nginx map 或 Netlify _redirects），規則去重、合併相同模式以 regex 壓縮。

實施步驟：
1. 聚合與去重
- 實作細節：腳本掃描所有 front matter，輸出唯一清單
- 所需資源：Node/Ruby 腳本
- 預估時間：2 小時

2. 生成 map/_redirects
- 實作細節：優先精確匹配，再用規則化
- 所需資源：Nginx/Netlify
- 預估時間：2 小時

3. 壓力測試
- 實作細節：ab/wrk 量測回應時間
- 所需資源：壓測工具
- 預估時間：2 小時

關鍵程式碼/設定：
```nginx
map $request_uri $new_uri {
  default "";
  /blogs/chicken/archive/2005/03/29/459.aspx/  /2005/03/29/slug/;
  # ... more generated entries
}
server {
  if ($new_uri != "") { return 301 $new_uri; }
}
```

實際案例：本文示例顯示跨多層級舊路徑，適合集中化。
實作環境：Nginx/Netlify + 生成腳本
實測數據：TTFB 降低、命中率提高（以壓測數據為準）

Learning Points：規則壓縮與映射資料結構
技能要求：Nginx、腳本自動化、壓測
延伸思考：搬到 CDN Edge 以近端回應

Practice Exercise：合併 100 條導向為 _redirects
進階：Nginx map 寫入自動化
專案：壓測比較前後 TTFB

Assessment Criteria：規則規模縮減、效能提升、風險控制

---

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 6, 7, 11, 12, 14
- 中級（需要一定基礎）
  - Case 1, 3, 5, 8, 9, 10, 15
- 高級（需要深厚經驗）
  - Case 2, 4, 13, 16

2) 按技術領域分類
- 架構設計類：Case 1, 5, 11, 12, 16
- 效能優化類：Case 10, 16, 6
- 整合開發類：Case 8, 9, 13, 7
- 除錯診斷類：Case 10, 14, 15
- 安全防護類：本篇未直接涵蓋（可延伸至開放導向防護與隱私合規）

3) 按學習目標分類
- 概念理解型：Case 5, 11, 12
- 技能練習型：Case 6, 7, 8, 9, 14, 15
- 問題解決型：Case 1, 2, 3, 4, 10
- 創新應用型：Case 13, 16

案例關聯圖（學習路徑建議）
- 入門起點（基礎環境與規格）
  1) 先學 Case 12（時區與日期 URL 一致性）→ Case 6（baseurl/relative_url）→ Case 11（canonical 與 sitemap）
- 核心導向與正規化
  2) 再學 Case 1（總體導向策略）→ Case 3（.aspx 重寫）→ Case 5（尾斜線與 canonical）
- 品質保證與診斷
  3) 接著 Case 15（CI 斷鏈）→ Case 10（導向鏈最小化）→ Case 14（a11y 與 alt）
- 內容整合與導航
  4) 進一步 Case 8（留言整合）→ Case 9（標籤索引）→ Case 7（資產命名）
- 進階與國際化
  5) 高階 Case 2（中文/十六進位 slug 映射）→ Case 4（ID 對應）→ Case 13（中文轉寫 SEO slug）
- 效能與規模化
  6) 最後學 Case 16（集中與壓縮導向規則）

依賴關係
- Case 1 依賴基礎 URL 正規化（Case 5, 11, 12）
- Case 10 依賴已建立導向（Case 1, 3）
- Case 16 依賴導向清單完備（Case 1, 2, 3, 4）
- Case 13 建議先完成 slug/編碼概念（Case 2, 7）

完整學習路徑（建議）
Case 12 → 6 → 11 → 1 → 3 → 5 → 15 → 10 → 14 → 8 → 9 → 7 → 2 → 4 → 13 → 16

說明
- 本整理完全依據文章 front matter 與可觀察到的遷移跡象（redirect_from 多來源、.aspx、中文與十六進位 slug、數字 ID、comments/tags 等）推導出教學型案例；未臆造文章原始未提及的具體數據。實測數據欄位改以可量測指標與驗證方法呈現，供實戰落地時填入。