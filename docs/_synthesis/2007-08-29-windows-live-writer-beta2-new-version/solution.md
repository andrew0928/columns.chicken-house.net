---
layout: synthesis
title: "Windows Live Writer Beta2 ... (新版)"
synthesis_type: solution
source_post: /2007/08/29/windows-live-writer-beta2-new-version/
redirect_from:
  - /2007/08/29/windows-live-writer-beta2-new-version/solution/
---

以下內容是根據你提供的文章（含前置 metadata/front matter）所能明確抽取到的「問題—根因—解法—效益」資訊，並結合可複製的實作流程與程式碼，整理成15個具有教學價值的解決方案案例。重點聚焦於：部落格多次遷移後的連結維護（front matter 中大量 redirect_from）、多國語系 slug/編碼問題、WordPress → Jekyll 轉換與評論保留、Windows Live Writer（WLW）設定與輸入法問題等實務主題。

請注意：原文並未提供實測數據，我在每個案例中提供的是「可驗證的測試方法與示例數值範圍」，做為教學與評估用的參考標的。

## Case #1: 多平台遷移後的舊連結保留（大量 redirect_from 的正規化）

### Problem Statement（問題陳述）
**業務場景**：網站經歷多次平台與路徑變更（如 .aspx→WordPress→Jekyll），外部引用與搜尋引擎索引仍大量指向舊制URL。若不妥善導向，將產生404、流量流失與SEO損失。文章的 front matter 中出現多條 redirect_from（含 /2007/...、/columns/...、/blogs/chicken/archive/...aspx/），即反映出此問題場景。
**技術挑戰**：需一次性接住多套歷史路徑規則、避免重定向鏈與循環、同時支援區分大小寫、尾斜線、編碼差異等。
**影響範圍**：SEO排名、外部連結權重、用戶體驗（高404率、跳出率上升）、評論或社群回流斷鏈。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 多階段遷移導致路徑模式混雜（date-based、分類路徑、.aspx ID）
2. 舊平台URL大小寫、尾斜線策略不一致
3. 新舊平台對中文與符號的 slug 規則不同

**深層原因**：
- 架構層面：靜態站點缺乏動態路由層，需預先配置完整映射
- 技術層面：未統一 slug/編碼/大小寫規則，導致重複與缺漏
- 流程層面：缺乏遷移前的URL資產盤點與重導測試流程

### Solution Design（解決方案設計）
**解決策略**：以 jekyll-redirect-from 為主、伺服器/邊緣重寫為輔，建立「最小化重導鏈」的映射層。對每篇文章明確列出歷史URL，並以自動化測試工具驗證301→最終URL。持續透過404監控補齊漏網路徑。

**實施步驟**：
1. 啟用 jekyll-redirect-from 並補齊 front matter 映射
- 實作細節：在各文章front matter 增加 redirect_from 條目，確保所有歷史路徑都指向新URL
- 所需資源：Jekyll 4.x、jekyll-redirect-from
- 預估時間：0.5天（小站）；1-3天（有上千篇內容）

2. 加上伺服器/邊緣端容錯規則（大小寫、尾斜線）
- 實作細節：例如Cloudflare/Netlify/Nginx設定大小寫正規化、尾斜線統一
- 所需資源：Cloudflare Workers 或 Netlify Redirects 或 Nginx
- 預估時間：0.5天

3. 自動化導向驗證與404監控
- 實作細節：建立URL清單批量檢測301終點、部署404日誌告警
- 所需資源：Node.js/Python腳本、監控平台（GA4/Search Console/Cloudflare Logs）
- 預估時間：1天

**關鍵程式碼/設定**：
```yaml
# _config.yml
plugins:
  - jekyll-redirect-from

# 範例文章 front matter（摘自原文情境）
redirect_from:
  - /2007/08/29/windows-live-writer-beta2-新版/
  - /columns/post/2007/08/29/Windows-Live-Writer-Beta2-(e696b0e78988).aspx/
  - /blogs/chicken/archive/2007/08/29/2619.aspx/
```

```nginx
# Nginx：統一尾斜線與避免重導鏈
server {
  ...
  # 轉成尾斜線
  if ($request_uri ~* "^(.+[^/])$") {
    return 301 $scheme://$host$1/;
  }
}
```

實際案例：本文章 front matter 中列出多個 redirect_from（含 .aspx 與多層目錄），即為「多階段遷移連結保留」的實務案例。
實作環境：Jekyll 4.3.x、Ruby 3.x、Netlify/Cloudflare Pages 或 Nginx
實測數據：
- 改善前：日均404 ~ 80-150次（示例）
- 改善後：日均404 <= 5次（示例）
- 改善幅度：>= 90%（示例，可驗證）

Learning Points（學習要點）
核心知識點：
- jekyll-redirect-from 用法與限制
- 301/308 對SEO的影響與最佳實踐
- 重導鏈檢測與大小寫/尾斜線正規化策略

技能要求：
- 必備技能：Jekyll配置、HTTP狀態碼與SEO基礎
- 進階技能：Nginx/邊緣計算（Workers）規則編寫、自動化測試

延伸思考：
- 站上是否有尚未被前端重導規則涵蓋的深層頁面？
- 若未使用Jekyll，如何在CMS/框架層實現等效方案？
- 重導數量較大時，該如何避免部署性能問題？

Practice Exercise（練習題）
- 基礎練習：為3篇文章補齊各2條歷史URL的 redirect_from，並本機測試 30 分鐘
- 進階練習：在Nginx加上尾斜線與大小寫規則，驗證不產生重導鏈 2 小時
- 專案練習：匯總站上所有歷史URL→新URL映射並完成自動化檢測 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有歷史URL 301 到正確終點，無循環/多跳
- 程式碼品質（30%）：設定清晰、可維護、註解完備
- 效能優化（20%）：重導鏈最小化、伺服器規則高效
- 創新性（10%）：自動化生成與測試工具的設計與應用
```

## Case #2: 舊站的中文slug十六進位片段（e696...）與百分號編碼解讀

### Problem Statement（問題陳述）
**業務場景**：部分舊站將中文字串以UTF-8十六進位（無百分號）或百分號編碼形式寫入URL（如 e696b0e78988 代表「新版」）。新站slug策略不同，導致歷史連結無法自動匹配。
**技術挑戰**：需同時處理「無%十六進位」與「%XX百分號編碼」兩種變體，並批量生成對應的 redirect_from。
**影響範圍**：中文內容比例高的站點，將有大量歷史連結失效。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 舊平台儲存中文slug為十六進位字串
2. 新平台對slug採自動轉譯或移除非ASCII
3. 遷移時未對舊編碼進行對應解碼

**深層原因**：
- 架構層面：缺少統一的slug/編碼策略
- 技術層面：未建立編碼轉換工具鏈
- 流程層面：缺乏資料盤點（未提前萃取舊URL規則）

### Solution Design（解決方案設計）
**解決策略**：建立一個轉換器，將舊URL中的十六進位片段→Unicode→再生成百分號編碼與可讀slug，並將所有變體加入 redirect_from。

**實施步驟**：
1. 編寫解碼與變體生成腳本
- 實作細節：支援 bytes.fromhex 與 urllib.parse.quote/unquote
- 所需資源：Python 3
- 預估時間：0.5天

2. 匯入映射並更新 front matter
- 實作細節：批次寫入每篇文章的 redirect_from
- 所需資源：YAML/前置字串處理
- 預估時間：0.5天

3. 驗證導向與404監控
- 實作細節：用批量檢測工具驗證
- 所需資源：curl/Node/Python
- 預估時間：0.5天

**關鍵程式碼/設定**：
```python
# decode_hex_slug.py
from urllib.parse import quote, unquote
import re

def hex_to_text(hex_str):
    # e696b0e78988 -> "新版"
    return bytes.fromhex(hex_str).decode('utf-8', errors='strict')

def detect_hex_segment(path):
    # 粗略偵測連續偶數長度16進位片段
    m = re.search(r'([0-9a-f]{6,})', path)
    return m.group(1) if m else None

def variants(path):
    seg = detect_hex_segment(path)
    if not seg:
        return [path]
    text = hex_to_text(seg)
    with_percent = path.replace(seg, quote(text))     # %E6%96%B0%E7%89%88
    readable = path.replace(seg, text)                # 直接中文
    return list({path, with_percent, readable})

# 示例
old = "/post/Windows-Live-Writer-Beta2-(e696b0e78988).aspx/"
print(variants(old))
```

實際案例：原文的 redirect_from 出現 e696b0e78988（代表「新版」），屬典型舊站處理中文slug方式。
實作環境：Python 3.10+
實測數據：
- 改善前：含十六進位slug的URL命中率低（高404）
- 改善後：對應變體均301到新頁
- 改善幅度：該族群404接近歸零（示例）

Learning Points（學習要點）
核心知識點：
- URL 編碼/解碼（UTF-8、百分號編碼）
- slug生成策略差異與風險
- 批次處理字串與YAML更新

技能要求：
- 必備技能：Python字串/檔案處理
- 進階技能：批次映射與自動化測試

延伸思考：
- 當中文slug存在SEO利弊時，是否採用拼音/英文別名？
- 解碼失敗或部分字符不可見時如何回退？

Practice Exercise（練習題）
- 基礎練習：為3條含十六進位slug URL產生3種變體 30 分鐘
- 進階練習：將變體批量寫進front matter並驗證 2 小時
- 專案練習：套用於全站URL，產出覆蓋率報告 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：三種變體皆命中301→正確頁
- 程式碼品質（30%）：清楚註解、錯誤處理
- 效能優化（20%）：批次處理效率與IO次數
- 創新性（10%）：變體偵測與自動化整合
```

## Case #3: Slug 正規化避免「雙連字號/括號」導致的多版本URL

### Problem Statement（問題陳述）
**業務場景**：不同平台對括號、空白、特殊符號處理不同，容易產生 Windows-Live-Writer-Beta2--(新版) 與 Windows-Live-Writer-Beta2-(新版) 等差異，造成多個歷史URL版本。
**技術挑戰**：統一定義slug規則，避免新增內容再度產生新變體；同時為舊變體提供重導。
**影響範圍**：內容多為中英混排的技術部落格，常含括號與符號。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不同slug算法對符號處理不同（移除、替換、保留）
2. 空白轉換為連字號時與符號相鄰，引發「雙連字號」
3. 遷移未統一新舊策略

**深層原因**：
- 架構層面：缺少 slug 策略作為全站標準
- 技術層面：未在產出流程嵌入檢查/修正
- 流程層面：缺乏發布前的URL檢視檢查點

### Solution Design（解決方案設計）
**解決策略**：確立slug產生規則（移除括號、合併多連字號、轉小寫），全站套用；為舊變體提供 redirect_from；發佈流程中加入slug檢查。

**實施步驟**：
1. 確立slug規則與工具
- 實作細節：以 slugify 套件固定策略（remove/replace）
- 所需資源：Node.js slugify 或 Ruby plugins
- 預估時間：0.5天

2. 對舊文掃描並補齊 redirect_from
- 實作細節：比對現有/理想slug，產生差異列表
- 所需資源：腳本工具
- 預估時間：1天

3. 導入發布前slug檢查
- 實作細節：Pre-commit hook 或 CI 檢查
- 所需資源：Husky/Pre-commit/CI
- 預估時間：0.5天

**關鍵程式碼/設定**：
```javascript
// slugify-config.js
const slugify = require('slugify');
module.exports = (title) =>
  slugify(title, {
    lower: true,
    strict: true,     // 移除非字母數字符號
    remove: /[()]/g,  // 額外移除括號
    locale: 'zh'      // 本地化
  }).replace(/--+/g, '-'); // 合併多連字號
```

實際案例：原文標題含括號（新版），且 redirect_from 中可見多變體，屬此類問題的典型。
實作環境：Node.js 18+
實測數據：
- 改善前：相同內容存在2-3個slug變體
- 改善後：統一slug + 舊變體301
- 改善幅度：重複URL歸一化至1（示例）

Learning Points（學習要點）
核心知識點：
- slug策略設計與中文處理
- 發布流程中的品質門檻（pre-commit/CI）
- 舊變體兼容策略

技能要求：
- 必備技能：Node/Ruby基礎、正則處理
- 進階技能：CI/CD流程整合

延伸思考：
- 中文是否改採拼音或英文別名？
- 未來標題變動如何避免更換URL？

Practice Exercise（練習題）
- 基礎練習：用slugify為5個含符號標題產生規範slug 30 分鐘
- 進階練習：掃描內容庫找出slug變體並生成redirect 2 小時
- 專案練習：把slug檢查嵌入CI並攔截不合規提交 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：slug一致、舊變體可導向
- 程式碼品質（30%）：規則清晰、測試覆蓋
- 效能優化（20%）：批次處理效能
- 創新性（10%）：自動修正與報表化
```

## Case #4: 大小寫與尾斜線的全站正規化（避免重複內容與404）

### Problem Statement（問題陳述）
**業務場景**：歷史URL兼有大小寫混用與尾斜線不一致，靜態主機或雲邊緣對大小寫敏感，導致重複內容或404。
**技術挑戰**：不修改內容檔案的前提下，在邊緣層統一規則，且不引入重導鏈。
**影響範圍**：SEO（重複內容）、用戶體驗（404/多跳）
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 舊站對大小寫與尾斜線策略不一
2. 新站伺服器/儲存對大小寫敏感
3. 多層重導規則互相疊加

**深層原因**：
- 架構層面：未在邊緣統一規則
- 技術層面：規則順序與條件不完善
- 流程層面：缺乏整站自動化檢測

### Solution Design（解決方案設計）
**解決策略**：用邊緣或伺服器中介層一次性正規化（轉小寫、補尾斜線），確保直接301到最終URL；並在本地/CI驗證不產生二次跳轉。

**實施步驟**：
1. 部署Cloudflare Workers/Netlify Edge Function大小寫與尾斜線規則
- 實作細節：僅在路徑層處理，不動查詢字串
- 所需資源：Cloudflare/Netlify
- 預估時間：0.5天

2. 建立不產生重導鏈的測試清單
- 實作細節：以常見大小寫/尾斜線組合批量測
- 所需資源：Node腳本
- 預估時間：0.5天

3. 監控301/308比例與鏈長
- 實作細節：log/GA4/CF Logs
- 所需資源：監控平台
- 預估時間：0.5天

**關鍵程式碼/設定**：
```javascript
// Cloudflare Worker：lowercase + ensure trailing slash
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const orig = url.pathname;
    const lower = orig.toLowerCase();
    let target = lower.endsWith('/') ? lower : lower + '/';
    if (target !== orig) {
      url.pathname = target;
      return Response.redirect(url.toString(), 301);
    }
    return fetch(request);
  }
};
```

實際案例：原文redirect_from含大小寫差異與尾斜線版本，適合用此策略消弭差異。
實作環境：Cloudflare Workers/Netlify Edge
實測數據：
- 改善前：大小寫或尾斜線造成2跳
- 改善後：一次跳轉到位
- 改善幅度：平均跳轉次數降低至1（示例）

Learning Points（學習要點）
核心知識點：
- 邊緣計算重寫與SEO影響
- 重導鏈檢測方法
- 大小寫敏感主機的相容策略

技能要求：
- 必備技能：JS/HTTP 基礎
- 進階技能：邊緣運算部署與監控

延伸思考：
- 多語系路徑（/zh-TW/）是否需排除轉小寫？
- API路徑與靜態頁面是否分流處理？

Practice Exercise（練習題）
- 基礎練習：在Worker上部署lowercase+slash規則 30 分鐘
- 進階練習：建立100條URL測試鏈長 2 小時
- 專案練習：與既有redirect_from協作避免雙跳 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有大小寫/尾斜線變體一次301
- 程式碼品質（30%）：規則清晰、邊界條件齊備
- 效能優化（20%）：Worker響應延遲低
- 創新性（10%）：自動化鏈長報表
```

## Case #5: 多階段遷移映射整併（.aspx、/post/、/columns/ 一次到位）

### Problem Statement（問題陳述）
**業務場景**：舊站歷經多套路徑規則（如 /blogs/.../2619.aspx、/post/...、/columns/...），映射分散在各處且彼此衝突或重疊。
**技術挑戰**：需集中管理映射，避免互相覆蓋、循環，並利於後續維護。
**影響範圍**：大量歷史連結、SEO與實際用戶點擊路徑
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不同來源的映射檔未整併
2. 缺乏唯一「最終URL」的權威定義
3. 多層規則互相疊加產生意外結果

**深層原因**：
- 架構層面：沒有中心化路由/映射層
- 技術層面：規則表無優先級與去重機制
- 流程層面：遷移一次次累積技債

### Solution Design（解決方案設計）
**解決策略**：建立主映射表（CSV/JSON），每條舊URL唯一對應新URL；以此生成 front matter redirect_from 與伺服器層 map；加入去重與循環檢測。

**實施步驟**：
1. 聚合所有來源映射到一張主表
- 實作細節：合併CSV/抓取WordPress匯出、舊站Sitemap
- 所需資源：Python/Excel
- 預估時間：1-2天

2. 去重與循環檢測
- 實作細節：圖算法檢測路徑是否A→B→C→A
- 所需資源：NetworkX 或自寫檢查
- 預估時間：0.5-1天

3. 自動生成Jekyll與Nginx/Netlify規則
- 實作細節：模板化輸出
- 所需資源：Jinja2/字符串處理
- 預估時間：0.5天

**關鍵程式碼/設定**：
```python
# merge_redirects.py
import csv
from collections import defaultdict

# 讀入多個CSV：old_url,new_url
files = ["wp.csv", "aspx.csv", "columns.csv"]
mapping = {}
for f in files:
    with open(f) as fh:
        for old, new in csv.reader(fh):
            mapping[old.strip().lower()] = new.strip()

# 輸出 Nginx map
with open("map.conf", "w") as out:
    out.write("map $request_uri $redirect_to {\n")
    for old, new in mapping.items():
        out.write(f'  "{old}" "{new}";\n')
    out.write("}\n")
```

實際案例：原文同時出現 /post/、/columns/ 與 /blogs/.../aspx/，適合用主映射表整併。
實作環境：Python 3.x、Nginx/Netlify/Cloudflare
實測數據：
- 改善前：多條重疊規則導致雙跳或錯誤導向
- 改善後：所有舊URL唯一對應新URL
- 改善幅度：重導錯誤率趨近0（示例）

Learning Points（學習要點）
核心知識點：
- 中心化映射表設計
- 循環/鏈長檢測
- 多目標輸出（前端/伺服器）

技能要求：
- 必備技能：資料處理、Nginx/Netlify規則
- 進階技能：圖算法、資料清理

延伸思考：
- 當新URL再次變動時，如何保持主表單一真相來源？
- 是否需版控主表並審核變更？

Practice Exercise（練習題）
- 基礎練習：合併2個映射CSV並輸出map.conf 30 分鐘
- 進階練習：加入循環檢測並拒絕輸出有迴圈的項目 2 小時
- 專案練習：為全站生成Jekyll與伺服器兩套規則 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：主表唯一性、無循環
- 程式碼品質（30%）：結構清晰、可擴充
- 效能優化（20%）：大量規則輸出效率
- 創新性（10%）：工具自動化程度
```

## Case #6: 保留 WordPress 評論（使用 wordpress_postid 與 Disqus/Giscus 綁定）

### Problem Statement（問題陳述）
**業務場景**：遷移到Jekyll後，舊有WordPress評論無法自動對應新URL，導致評論遺失或掛錯文章。
**技術挑戰**：不同評論系統的識別鍵不同，URL改變後需以穩定ID（如 wordpress_postid）做綁定。
**影響範圍**：內容社會證明、SEO（UGC長文）、用戶互動
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 評論多以URL為鍵，URL遷移後失配
2. 未在模板中設定穩定識別鍵
3. 未完成URL→URL的評論映射

**深層原因**：
- 架構層面：評論系統與內容URL耦合
- 技術層面：未利用post_id等穩定鍵
- 流程層面：遷移時遺漏評論層規劃

### Solution Design（解決方案設計）
**解決策略**：將 wordpress_postid 注入評論嵌入腳本作為 page.identifier，確保變更URL仍能對應；同時使用評論系統的URL映射工具遷移舊URL。

**實施步驟**：
1. 模板注入識別鍵
- 實作細節：優先用 page.wordpress_postid，無則退回 page.url
- 所需資源：Jekyll模板
- 預估時間：0.5天

2. 匯入舊評論並建立URL映射
- 實作細節：Disqus URL mapper CSV 或 Giscus discussion mapping
- 所需資源：Disqus/Giscus 管控台
- 預估時間：0.5-1天

3. 驗證評論對應與數量
- 實作細節：隨機抽樣比對
- 所需資源：人工/腳本
- 預估時間：0.5天

**關鍵程式碼/設定**：
```html
<!-- Disqus embed -->
<script>
var disqus_config = function () {
  this.page.identifier = "{{ page.wordpress_postid | default: page.url }}";
  this.page.url = "{{ site.url }}{{ page.url }}";
};
</script>
```

實際案例：本文 front matter 帶有 wordpress_postid: 149，正是保留評論對應的穩定鍵。
實作環境：Jekyll、Disqus/Giscus
實測數據：
- 改善前：遷移後評論顯示率不穩定
- 改善後：以 postid 綁定後評論完整呈現
- 改善幅度：評論對應成功率接近100%（示例）

Learning Points（學習要點）
核心知識點：
- 評論識別鍵策略（URL vs ID）
- 第三方評論系統的遷移工具
- 模板變數與回退策略

技能要求：
- 必備技能：Jekyll模板、基本JS
- 進階技能：批量URL mapping與資料驗證

延伸思考：
- 若無 postid，可否用內容哈希作為穩定鍵？
- 評論系統供應商更換時的再遷移策略？

Practice Exercise（練習題）
- 基礎練習：把 page.wordpress_postid 注入Disqus配置 30 分鐘
- 進階練習：產出舊URL→新URL的Disqus CSV 2 小時
- 專案練習：抽樣驗證100篇文章評論對應 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：評論對應正確
- 程式碼品質（30%）：模板清楚、回退策略合理
- 效能優化（20%）：批量遷移效率
- 創新性（10%）：識別鍵設計創意（哈希等）
```

## Case #7: 評論與重導協同（避免URL識別漂移）

### Problem Statement（問題陳述）
**業務場景**：即使以ID綁定評論，部分評論系統仍將URL作為輔助鍵，重導與canonical未統一可能造成評論出現在非預期URL。
**技術挑戰**：需確保 canonical 與重導最終URL一致，並避免同一內容出現多個可存取URL。
**影響範圍**：UGC分裂、SEO重複內容
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. canonical標籤缺失或不一致
2. 多個URL皆可200而非301
3. 評論系統快取了非最終URL

**深層原因**：
- 架構層面：頁面層與伺服器層規則未統一
- 技術層面：漏加canonical/OG url
- 流程層面：缺乏整體檢查清單

### Solution Design（解決方案設計）
**解決策略**：在Head中加入canonical/og:url，伺服器層確保所有變體301至canonical；對評論系統提交URL mapping檔校正。

**實施步驟**：
1. 補上canonical/og:url
- 實作細節：模板注入 site.url + page.url
- 所需資源：Jekyll模板
- 預估時間：0.5天

2. 檢查200多版本頁面一律改為301
- 實作細節：Workers/Nginx規則
- 所需資源：同上
- 預估時間：0.5天

3. 對評論系統提交URL mapping並清快取
- 實作細節：Disqus URL mapper/管理後台清快取
- 所需資源：評論系統後台
- 預估時間：0.5天

**關鍵程式碼/設定**：
```html
<!-- head.html -->
<link rel="canonical" href="{{ site.url }}{{ page.url }}" />
<meta property="og:url" content="{{ site.url }}{{ page.url }}">
```

實際案例：本文多個 redirect_from 代表可能存在多版本URL，需要 canonical + 301 統一。
實作環境：Jekyll + 邊緣/伺服器重寫
實測數據（示例）：
- 改善前：相同內容2-3個200 URL
- 改善後：僅保留1個200 URL，其他301
- 改善幅度：重複內容數量降至0

Learning Points（學習要點）
核心知識點：
- canonical/og:url 與SEO/社群分享
- 200多版本風險
- 評論系統URL快取

技能要求：
- 必備技能：HTML模板
- 進階技能：伺服器/邊緣重寫

延伸思考：
- AMP/加速頁面是否另需canonical處理？
- RSS/聚合頁如何處理canonical？

Practice Exercise（練習題）
- 基礎練習：為模板加入canonical與og:url 30 分鐘
- 進階練習：移除一個可200的重複URL，改為301 2 小時
- 專案練習：全站掃描200重複頁面並整改 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：唯一200 URL
- 程式碼品質（30%）：模板通用性強
- 效能優化（20%）：最小重導
- 創新性（10%）：自動掃描報表
```

## Case #8: 批次驗證重導正確性與鏈長（自動化測試）

### Problem Statement（問題陳述）
**業務場景**：大批 redirect_from 與伺服器規則部署後，需快速驗證每條舊URL是否一次跳轉到最終URL，避免鏈長與錯向。
**技術挑戰**：高併發抓取、處理3xx/5xx、最終URL比對與報表化。
**影響範圍**：全站重導品質與SEO
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 手工測試無法覆蓋
2. 多層規則交互影響結果
3. 非預期的大小寫/尾斜線導致二跳

**深層原因**：
- 架構層面：缺乏自動化測試流程
- 技術層面：未收斂至單一終點
- 流程層面：缺少發佈前後驗收

### Solution Design（解決方案設計）
**解決策略**：使用Node腳本批量發送請求，追蹤重導直到200，統計鏈長與錯誤；將結果輸出CSV並設置失敗門檻斷言。

**實施步驟**：
1. 蒐集舊URL清單
- 實作細節：從front matter/CSV匯出
- 所需資源：腳本或grep
- 預估時間：0.5天

2. 編寫與執行檢測腳本
- 實作細節：跟隨重導、計算鏈長、核對終點
- 所需資源：Node.js
- 預估時間：0.5天

3. 報表與修復循環
- 實作細節：輸出CSV，修規則再跑
- 所需資源：表格工具
- 預估時間：0.5天

**關鍵程式碼/設定**：
```javascript
// check-redirects.js
import fetch from 'node-fetch';
import fs from 'fs';

async function follow(url, max=5) {
  let hops = 0, current = url;
  while (hops <= max) {
    const res = await fetch(current, { redirect: 'manual' });
    if (res.status >= 300 && res.status < 400 && res.headers.get('location')) {
      current = new URL(res.headers.get('location'), current).toString();
      hops++;
    } else {
      return { status: res.status, finalUrl: current, hops };
    }
  }
  return { status: 599, finalUrl: current, hops };
}

const urls = fs.readFileSync('old_urls.txt', 'utf8').trim().split('\n');
const out = [];
for (const u of urls) {
  const r = await follow(u);
  out.push([u, r.status, r.finalUrl, r.hops].join(','));
}
fs.writeFileSync('report.csv', out.join('\n'));
```

實際案例：可用原文的 redirect_from 清單做為old_urls.txt。
實作環境：Node.js 18+
實測數據（示例）：
- 改善前：平均鏈長 2.1
- 改善後：平均鏈長 1.0-1.1
- 改善幅度：鏈長下降約50%+

Learning Points（學習要點）
核心知識點：
- 3xx處理、鏈長概念
- 自動化驗收的必要性
- 結果報表化與修復閉環

技能要求：
- 必備技能：Node.js、HTTP
- 進階技能：批次測試與資料匯出

延伸思考：
- 是否需在CI觸發，作為阻擋條件？
- 大規模URL時如何限流與重試策略？

Practice Exercise（練習題）
- 基礎練習：檢測10條URL的鏈長 30 分鐘
- 進階練習：加入終點URL白名單斷言 2 小時
- 專案練習：全站測試並出具修復建議 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：鏈長/狀態碼準確
- 程式碼品質（30%）：結構清楚、錯誤處理
- 效能優化（20%）：限流與併發控制
- 創新性（10%）：自動報表與CI整合
```

## Case #9: 從 WXR（WordPress匯出）自動生成Jekyll文章與 redirect_from

### Problem Statement（問題陳述）
**業務場景**：手動搬運數百篇WP文章到Jekyll耗時易錯，尤其是保留舊URL的 redirect_from。
**技術挑戰**：解析WXR、處理HTML→Markdown、生成完整front matter（含wordpress_postid、redirect_from）。
**影響範圍**：整站遷移效率與品質
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 手動搬運出錯機率高
2. 舊URL映射容易遺漏
3. 格式轉換不一致

**深層原因**：
- 架構層面：無自動化遷移管線
- 技術層面：對WXR/XML解析不足
- 流程層面：缺乏可重複腳本

### Solution Design（解決方案設計）
**解決策略**：撰寫Python腳本解析WXR，輸出Markdown+front matter，將WP permalink與歷史變體寫進 redirect_from。

**實施步驟**：
1. 解析WXR取得必要欄位
- 實作細節：標題、內容、日期、permalink、post_id、分類標籤
- 所需資源：xmltodict
- 預估時間：1-2天

2. 轉換HTML→Markdown與slug生成
- 實作細節：html2text/自定策略
- 所需資源：python-frontmatter/markdownify
- 預估時間：1天

3. 寫入front matter與redirect_from
- 實作細節：加入 wordpress_postid、舊permalink、變體
- 所需資源：同上
- 預估時間：0.5天

**關鍵程式碼/設定**：
```python
# wxr_to_jekyll.py
import xmltodict, frontmatter, os
from markdownify import markdownify as md

with open('export.xml', 'r', encoding='utf-8') as f:
    data = xmltodict.parse(f.read())

items = data['rss']['channel']['item']
for it in items:
    title = it['title']
    content = md(it['content:encoded'] or '')
    post_id = it['wp:post_id']
    old_url = it['link']
    fm = {
        'layout': 'post',
        'title': title,
        'wordpress_postid': int(post_id),
        'redirect_from': [old_url.replace('https://old.com','')],
    }
    post = frontmatter.Post(content, **fm)
    slug = str(post_id) # 也可用自訂slug策略
    path = f"_posts/{it['wp:post_date'][:10]}-{slug}.md"
    with open(path, 'w', encoding='utf-8') as out:
        frontmatter.dump(post, out)
```

實際案例：本文存在 wordpress_postid 與多redirect_from，適合自動生成。
實作環境：Python 3.x
實測數據：
- 改善前：人工轉檔100篇需5-7天
- 改善後：自動化生成縮至數小時
- 改善幅度：工期縮短>80%（示例）

Learning Points（學習要點）
核心知識點：
- WXR結構、字段提取
- front matter與Markdown生成
- 自動化遷移流程

技能要求：
- 必備技能：Python/XML/Markdown處理
- 進階技能：slug/redirect策略與批次驗證

延伸思考：
- 如何保留WP短碼與自定欄位？
- 圖片/附件如何同步搬遷？

Practice Exercise（練習題）
- 基礎練習：解析WXR取得10篇標題與URL 30 分鐘
- 進階練習：生成含redirect_from的Markdown檔 2 小時
- 專案練習：全站自動化遷移與驗收 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：欄位齊全、redirect正確
- 程式碼品質（30%）：模組化、容錯
- 效能優化（20%）：大檔處理效率
- 創新性（10%）：圖片/短碼處理
```

## Case #10: Windows Live Writer 連線 WordPress（MetaWeblog/XML-RPC）設定

### Problem Statement（問題陳述）
**業務場景**：作者提到「跟我的 blog 搭起來還是可以用」，但實務上WLW常因XML-RPC設定或安全限制無法連線發文。
**技術挑戰**：正確配置MetaWeblog/WordPress XML-RPC端點、驗證協定握手，處理認證與防火牆。
**影響範圍**：寫作效率與離線編輯能力
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. WordPress XML-RPC被關閉或阻擋
2. 驗證或端點路徑錯誤
3. 安全外掛攔截

**深層原因**：
- 架構層面：後台安全策略未允許外部客戶端
- 技術層面：協定/端點不瞭解
- 流程層面：無連線測試與fallback

### Solution Design（解決方案設計）
**解決策略**：確認wp-xmlrpc端點開放，於WLW設定正確的blog type與網址；以curl測試 metaWeblog.newPost/ getRecentPosts，逐步排除問題點。

**實施步驟**：
1. 啟用XML-RPC並確認端點
- 實作細節：WordPress現已預設開啟；端點 /xmlrpc.php
- 所需資源：WP後台/伺服器日志
- 預估時間：0.5天

2. 在WLW新增部落格帳號
- 實作細節：選擇Other services → WordPress/MetaWeblog，填入站點URL、帳密
- 所需資源：WLW客戶端
- 預估時間：0.5天

3. curl 驗證協定
- 實作細節：以XML-RPC測試讀取/發文
- 所需資源：curl
- 預估時間：0.5天

**關鍵程式碼/設定**：
```bash
# 測試XML-RPC：getRecentPosts
curl -s https://yourblog.com/xmlrpc.php \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
<methodCall>
  <methodName>metaWeblog.getRecentPosts</methodName>
  <params>
    <param><value><string>1</string></value></param>   <!-- blogId -->
    <param><value><string>USER</string></value></param>
    <param><value><string>PASS</string></value></param>
    <param><value><int>5</int></value></param>
  </params>
</methodCall>'
```

實際案例：文章提到WLW與blog可用，對應此解法。
實作環境：WordPress 6.x、WLW Beta2/OWW
實測數據（示例）：
- 改善前：WLW連線測試失敗率高
- 改善後：能成功讀取/發文
- 改善幅度：連線成功率提升至~100%

Learning Points（學習要點）
核心知識點：
- MetaWeblog/XML-RPC 基本呼叫
- WLW設定重點
- 安全/防火牆調校

技能要求：
- 必備技能：HTTP、curl、WP基本管理
- 進階技能：協定除錯與日誌判讀

延伸思考：
- 若需OAuth/新版協定，如何替代？（如Micropub）
- 無XML-RPC環境如何改走REST API？

Practice Exercise（練習題）
- 基礎練習：以curl呼叫 getRecentPosts 30 分鐘
- 進階練習：用metaWeblog.newPost發一篇測試文章 2 小時
- 專案練習：建立完整WLW連線手冊與除錯流程 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：能讀取/發文
- 程式碼品質（30%）：XML符合協定
- 效能優化（20%）：連線穩定
- 創新性（10%）：自動化連線檢測
```

## Case #11: WLW 舊版輸入法（IME）叫不出來的問題修復

### Problem Statement（問題陳述）
**業務場景**：作者提到「之前輸入法常常叫不出來的問題現在還沒碰到」，顯示舊版WLW對中文IME支援不穩，Beta2修復後恢復正常輸入。
**技術挑戰**：Windows文字服務（TSF/ctfmon）與應用焦點/控制元件整合，特別是RichEdit/嵌入式編輯器。
**影響範圍**：非英語作者的寫作效率與可用性
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 舊版WLW未正確附掛IME上下文
2. TSF（ctfmon.exe）未啟動或被關閉
3. 輸入語言切換與焦點管理異常

**深層原因**：
- 架構層面：編輯器控件與IME整合瑕疵
- 技術層面：IME Context/TSF初始化不完整
- 流程層面：未覆蓋到多語輸入測試

### Solution Design（解決方案設計）
**解決策略**：升級WLW到Beta2或替代客戶端；確保Windows文字服務啟用（ctfmon），重建輸入法設定；必要時清除輸入法設定快取。

**實施步驟**：
1. 升級WLW/OWW並重啟
- 實作細節：使用新版修正；或Open Live Writer/Markdown客戶端
- 所需資源：安裝包
- 預估時間：0.5天

2. 啟動ctfmon與重建輸入法
- 實作細節：註冊表讓ctfmon隨登入啟動；移除/新增中文輸入法
- 所需資源：Windows管理權限
- 預估時間：0.5天

3. 測試焦點切換場景
- 實作細節：標題欄、文章區、對話框切換輸入
- 所需資源：手測腳本
- 預估時間：0.5天

**關鍵程式碼/設定**：
```powershell
# 啟用ctfmon開機自啟（需要管理員）
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v CTFMon /t REG_SZ /d "C:\Windows\System32\ctfmon.exe" /f

# 重新註冊文字服務
C:\Windows\System32\ctfmon.exe
```

實際案例：作者表示升級Beta2後未再遇到IME問題。
實作環境：Windows 10/11、WLW Beta2/替代客戶端
實測數據（示例）：
- 改善前：IME喚出失敗率高
- 改善後：可穩定切換輸入
- 改善幅度：IME可用性達~100%

Learning Points（學習要點）
核心知識點：
- Windows TSF/ctfmon 基礎
- 應用與IME整合重點
- 多語輸入測試要點

技能要求：
- 必備技能：Windows系統設定
- 進階技能：IME問題診斷

延伸思考：
- 替代編輯器是否更穩定？
- 是否需在發佈前自動化IME檢測？

Practice Exercise（練習題）
- 基礎練習：啟用ctfmon並測試WLW輸入 30 分鐘
- 進階練習：記錄多場景焦點切換IME行為 2 小時
- 專案練習：撰寫IME問題SOP 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：IME穩定可用
- 程式碼品質（30%）：設定可追溯
- 效能優化（20%）：問題復現與回歸測試
- 創新性（10%）：替代工具方案
```

## Case #12: Beta 版採用的風險控管（安全升級與回退）

### Problem Statement（問題陳述）
**業務場景**：作者「先裝再說」的行為在實務上需要風險控管，以免Beta造成發布中斷或內容丟失。
**技術挑戰**：建立測試環境、權限隔離、回退路徑、資料備份。
**影響範圍**：發布穩定性、資料安全、交付節奏
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. Beta功能未知風險
2. 無隔離測試流程
3. 缺乏回退策略

**深層原因**：
- 架構層面：無staging部落格/測試帳號
- 技術層面：備份/還原工具未標準化
- 流程層面：缺少升級SOP

### Solution Design（解決方案設計）
**解決策略**：建立staging連線與測試分類；備份設定/文章；預設回退版本；制定升級清單與驗收項目。

**實施步驟**：
1. 建立staging站與測試帳號
- 實作細節：WP-CLI建立用戶/權限/測試分類
- 所需資源：WP-CLI
- 預估時間：0.5天

2. 升級測試並驗證核心功能
- 實作細節：發草稿、插入圖片、發佈、重導檢查
- 所需資源：手測/腳本
- 預估時間：0.5天

3. 制定回退路徑
- 實作細節：保留舊版安裝包/設定備份
- 所需資源：備份工具
- 預估時間：0.5天

**關鍵程式碼/設定**：
```bash
# WP-CLI：建立測試使用者與分類
wp user create wlw_tester tester@example.com --role=author --user_pass=StrongPass!
wp term create category "WLW-Testing"
```

實際案例：對應作者升級Beta2的情境，提供安全實務做法。
實作環境：WordPress、WLW/OLW
實測數據（示例）：
- 改善前：升級造成發文中斷風險
- 改善後：staging驗證通過再上線
- 改善幅度：中斷風險顯著下降

Learning Points（學習要點）
核心知識點：
- Staging/回退策略
- 升級驗收清單
- 用戶/權限隔離

技能要求：
- 必備技能：WP-CLI、備份常識
- 進階技能：測試計畫編寫

延伸思考：
- 能否用容器/快照做一鍵回退？
- 自動化冒煙測試可否接入CI？

Practice Exercise（練習題）
- 基礎練習：建立staging用戶/分類 30 分鐘
- 進階練習：撰寫升級驗收清單 2 小時
- 專案練習：完成一次受控升級與回退演練 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：驗收清單覆蓋核心流程
- 程式碼品質（30%）：命令與腳本可追溯
- 效能優化（20%）：升級/回退耗時
- 創新性（10%）：自動化測試導入
```

## Case #13: 中文標題轉拼音/英文別名，兼顧可讀性與穩定性

### Problem Statement（問題陳述）
**業務場景**：使用中文slug在不同平台會遇到編碼/相容問題；需兼顧可讀性（拼音/英文別名）與穩定性。
**技術挑戰**：自動將中文轉拼音並生成安全slug，為舊中文URL提供redirect。
**影響範圍**：URL可分享性、跨平台相容、SEO
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 中文slug在某些主機或工具鏈支援不佳
2. 百分號編碼URL可讀性差
3. 不同時期轉換策略不一致

**深層原因**：
- 架構層面：未定義語言策略
- 技術層面：缺少轉換工具
- 流程層面：發佈標準未涵蓋slug要求

### Solution Design（解決方案設計）
**解決策略**：以pypinyin將中文轉拼音、結合slugify生成安全slug；舊中文URL保留在redirect_from。

**實施步驟**：
1. 構建中文→拼音工具
- 實作細節：pypinyin + slugify
- 所需資源：Python套件
- 預估時間：0.5天

2. 更新front matter並保留舊URL
- 實作細節：redirect_from寫入中文/百分號版本
- 所需資源：腳本
- 預估時間：0.5天

3. 驗證分享/SEO/平台相容
- 實作細節：不同瀏覽器/平台測試
- 所需資源：手測
- 預估時間：0.5天

**關鍵程式碼/設定**：
```python
from pypinyin import lazy_pinyin
import re

def zh_to_pinyin_slug(title):
    py = '-'.join(lazy_pinyin(title))
    slug = re.sub(r'[^a-z0-9-]+', '-', py.lower())
    return re.sub(r'-+', '-', slug).strip('-')

print(zh_to_pinyin_slug("Windows Live Writer Beta2 （新版）"))
# windows-live-writer-beta2-xin-ban
```

實際案例：本文標題含「新版」，可轉為 xin-ban 作為穩定別名。
實作環境：Python 3.x
實測數據（示例）：
- 改善前：分享鏈接含大量%編碼
- 改善後：短且可讀的拼音slug
- 改善幅度：分享點擊率提升（可A/B驗證）

Learning Points（學習要點）
核心知識點：
- 多語slug策略
- 拼音轉換與清洗
- 兼容舊URL的重導

技能要求：
- 必備技能：Python正則/字串
- 進階技能：SEO衡量與A/B測試

延伸思考：
- 是否需人工校正特殊詞彙的拼音？
- 多語站（繁/簡/英）的一致策略

Practice Exercise（練習題）
- 基礎練習：將5個中文標題轉拼音slug 30 分鐘
- 進階練習：把舊中文URL加入redirect_from 2 小時
- 專案練習：對比拼音與中文slug的點擊率 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：slug生成穩定
- 程式碼品質（30%）：轉換規則清楚
- 效能優化（20%）：批量處理速度
- 創新性（10%）：A/B與SEO度量
```

## Case #14: 中文標籤/分類頁的安全連結與索引頁生成

### Problem Statement（問題陳述）
**業務場景**：front matter 中存在中文 tags（如「作品集」、「有的沒的」），標籤索引頁在URL編碼與生成上需謹慎，避免導航與SEO問題。
**技術挑戰**：URI編碼、安全slug、標籤索引自動生成。
**影響範圍**：站內導覽、長尾流量
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 中文tag在URL中需編碼/slug化
2. 索引頁未自動生成導致404
3. 連結與實際頁面路徑不一致

**深層原因**：
- 架構層面：未規劃tag索引生成器
- 技術層面：URI編碼與slug化未統一
- 流程層面：無生成/驗證步驟

### Solution Design（解決方案設計）
**解決策略**：統一以slug化的tag路徑生成索引頁，頁面中顯示原中文；所有tag連結經過 URI encode 或 slug 化以避免404。

**實施步驟**：
1. 寫入tags索引模板
- 實作細節：遍歷 site.tags 生成索引
- 所需資源：Jekyll/Liquid
- 預估時間：0.5天

2. 對tag進行slug或URI encode
- 實作細節：對連結href做 encode
- 所需資源：Liquid filters
- 預估時間：0.5天

3. 驗證所有tag頁200
- 實作細節：批量抓取測試
- 所需資源：腳本
- 預估時間：0.5天

**關鍵程式碼/設定**：
```liquid
<!-- tags.html -->
<ul>
{% for tag in site.tags %}
  {% assign tag_name = tag[0] %}
  {% capture tag_slug %}{{ tag_name | slugify: 'latin' }}{% endcapture %}
  <li><a href="/tags/{{ tag_slug }}/">{{ tag_name }}</a> ({{ tag[1].size }})</li>
{% endfor %}
</ul>
```

實際案例：本文含中文tags，需生成安全的tag頁。
實作環境：Jekyll 4.x
實測數據（示例）：
- 改善前：點擊tag可能404或URL難讀
- 改善後：索引完整、URL安全
- 改善幅度：tag頁404降至0

Learning Points（學習要點）
核心知識點：
- Liquid遍歷與slugify
- 中文顯示vsURL安全分離
- 導覽與SEO關係

技能要求：
- 必備技能：Jekyll/Liquid
- 進階技能：批量驗證與生成

延伸思考：
- 是否須建立tag sitemap？
- 長尾流量如何藉由tag頁提升？

Practice Exercise（練習題）
- 基礎練習：建立tags索引頁 30 分鐘
- 進階練習：對中文tag生成slug子頁 2 小時
- 專案練習：全站tag清理與索引重建 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：所有tag頁可達
- 程式碼品質（30%）：模板清楚
- 效能優化（20%）：生成效率
- 創新性（10%）：tag頁資訊設計
```

## Case #15: DotNet aspx 舊路徑到新站的動態映射與容錯

### Problem Statement（問題陳述）
**業務場景**：redirect_from 中有 /blogs/chicken/archive/.../2619.aspx/ 等路徑，屬舊式以ID為主的ASP.NET部落格URL。需準確映射到新文章。
**技術挑戰**：aspx數字ID→新站slug/ID的映射與大規模規則管理。
**影響範圍**：歷史流量與外部引用
**複雜度評級**：中-高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 舊站以數字ID作為URL終端
2. 新站採日期+slug或其他規則
3. 無ID對應表

**深層原因**：
- 架構層面：資料庫ID與新站ID無同步
- 技術層面：缺乏ID映射輸出
- 流程層面：遷移前未抽取ID對照

### Solution Design（解決方案設計）
**解決策略**：建立ID→新URL對照表並生成伺服器級映射；無對應時回退至搜尋頁或相關列表，避免硬404。

**實施步驟**：
1. 建立ID映射表
- 實作細節：從舊DB/備份/抓取快取生成 (ID→標題/日期→新URL)
- 所需資源：資料存取/抓取
- 預估時間：1-2天

2. 產生伺服器級映射規則
- 實作細節：Nginx map 或 Workers 查表
- 所需資源：Nginx/Workers
- 預估時間：0.5-1天

3. 未匹配ID的容錯頁
- 實作細節：導向搜尋頁並攜帶關鍵詞
- 所需資源：搜尋頁模板
- 預估時間：0.5天

**關鍵程式碼/設定**：
```nginx
# Nginx：aspx ID對應映射（示例）
map $request_uri $legacy_new {
  default "";
  ~^/blogs/chicken/archive/\d{4}/\d{2}/\d{2}/(?<id>\d+)\.aspx/?$ $id;
}

map $legacy_new $to_url {
  default "";
  "2619" "/post/windows-live-writer-beta2-xin-ban/";
}

server {
  if ($to_url != "") { return 301 $to_url; }
  # fallback：送到搜尋頁
  if ($legacy_new != "") { return 302 /search/?q=$legacy_new; }
}
```

實際案例：本文redirect_from含2619.aspx，具體可映射至新頁。
實作環境：Nginx/Cloudflare Workers
實測數據（示例）：
- 改善前：aspx舊鏈接全404
- 改善後：匹配者301、未匹配者302到搜尋
- 改善幅度：舊鏈接流失顯著降低

Learning Points（學習要點）
核心知識點：
- 舊ID→新URL對照
- 伺服器級規則與fallback
- 測試與監控

技能要求：
- 必備技能：Nginx/正則
- 進階技能：資料蒐集與清理

延伸思考：
- Workers/KV儲存可否做更大規模映射？
- 搜尋頁關鍵詞如何最佳化？

Practice Exercise（練習題）
- 基礎練習：為3個aspx ID建立映射 30 分鐘
- 進階練習：加入fallback搜尋導向 2 小時
- 專案練習：批量匯入ID映射1,000筆 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：ID命中映射、未命中有fallback
- 程式碼品質（30%）：規則清楚
- 效能優化（20%）：大規模規則效率
- 創新性（10%）：KV/Workers應用
```

## Case #16: 版本更新偵測與通知（避免「落後太久」）

### Problem Statement（問題陳述）
**業務場景**：作者提到「落後太久」才發現Beta2已發布。需要自動化的更新偵測與通知，確保工具鏈維持最新。
**技術挑戰**：訂閱來源不穩、RSS/Release API解析、通知管道（桌面通知/Slack/Email）。
**影響範圍**：工具效能與穩定性更新的及時採用
**複雜度評級**：低-中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未訂閱官方更新通道
2. 缺少自動提醒
3. 依賴手動巡檢

**深層原因**：
- 架構層面：無更新監控服務
- 技術層面：缺少RSS/Release解析
- 流程層面：無例行檢查節奏

### Solution Design（解決方案設計）
**解決策略**：以PowerShell/Node定時抓取官方RSS/Release頁，偵測版本變更後觸發系統通知或Slack訊息。

**實施步驟**：
1. 訂閱來源與解析
- 實作細節：RSS/Atom/Release頁抓取diff
- 所需資源：PowerShell/Node
- 預估時間：0.5天

2. 通知通道整合
- 實作細節：Windows通知/Slack webhook
- 所需資源：Webhook/Toast
- 預估時間：0.5天

3. 排程自動化
- 實作細節：Windows工作排程器或CI cron
- 所需資源：系統排程器
- 預估時間：0.5天

**關鍵程式碼/設定**：
```powershell
# Check-Release.ps1：簡易偵測並桌面通知
$feed = "https://example.com/writer/releases.atom"
$out = "$env:LOCALAPPDATA\wlw_latest.txt"

try {
  $xml = [xml](Invoke-WebRequest -Uri $feed -UseBasicParsing).Content
  $latest = $xml.feed.entry[0].title
  if (!(Test-Path $out) -or (Get-Content $out) -ne $latest) {
    $latest | Set-Content $out
    # Windows 10+ Toast（需BurntToast模組）
    New-BurntToastNotification -Text "WLW Update", "New version: $latest"
  }
} catch { Write-Host "Check failed: $_" }
```

實際案例：對應作者晚發現新版的痛點。
實作環境：Windows 10/11、PowerShell 7
實測數據（示例）：
- 改善前：更新延遲週期不定
- 改善後：可在發布當日收到通知
- 改善幅度：延遲縮短至0-1天

Learning Points（學習要點）
核心知識點：
- RSS/Atom解析
- 系統通知/Slack整合
- 排程任務

技能要求：
- 必備技能：PowerShell或Node
- 進階技能：安全與錯誤處理

延伸思考：
- 可否整合多工具的統一更新中心？
- 如何過濾非穩定版？

Practice Exercise（練習題）
- 基礎練習：抓取RSS並輸出最新版本 30 分鐘
- 進階練習：加入Windows通知/Slack 2 小時
- 專案練習：打造團隊用更新儀表板 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確偵測與通知
- 程式碼品質（30%）：錯誤處理與日誌
- 效能優化（20%）：排程與資源使用
- 創新性（10%）：多來源整合
```

## Case #17: Netlify/GitHub Pages/Cloudflare Pages 各平台重導策略與取捨

### Problem Statement（問題陳述）
**業務場景**：不同靜態託管平台對重導支援差異大（_redirects、_headers、Workers、GH Pages原生支援插件白名單）。需選擇最適合的實現。
**技術挑戰**：平台特性不一、規則上限與效能差異、部署流程整合。
**影響範圍**：實作成本、效能與維運便利性
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 平台對插件/重導規則支援不同
2. 映射規模與性能要求不一
3. 現有流程限制

**深層原因**：
- 架構層面：未評估平台能力矩陣
- 技術層面：未抽象重導規則
- 流程層面：部署流程未統一

### Solution Design（解決方案設計）
**解決策略**：以中心化映射生成多套輸出（jekyll-redirect-from、_redirects、Nginx、Workers）；依平台選擇最小成本且性能合宜的方案。

**實施步驟**：
1. 能力評估與需求匹配
- 實作細節：映射數量、鏈長要求、是否需要動態查表
- 所需資源：平台文件
- 預估時間：0.5-1天

2. 規則輸出抽象化
- 實作細節：由主表模板化輸出多目標
- 所需資源：生成腳本
- 預估時間：1天

3. 測試與監控
- 實作細節：鏈長/狀態碼/延遲
- 所需資源：自動化工具
- 預估時間：1天

**關鍵程式碼/設定**：
```txt
# Netlify _redirects（片段）
/2007/08/29/windows-live-writer-beta2-新版/ /post/windows-live-writer-beta2-xin-ban/ 301
/columns/post/2007/08/29/Windows-Live-Writer-Beta2-(e696b0e78988).aspx/ /post/windows-live-writer-beta2-xin-ban/ 301
```

實際案例：原文多重歷史路徑，需跨平台考量。
實作環境：Netlify/GH Pages/Cloudflare
實測數據（示例）：
- 改善前：單一平台方案導致規則上限或性能瓶頸
- 改善後：選擇合適平台方案
- 改善幅度：構建時間/延遲下降

Learning Points（學習要點）
核心知識點：
- 平台重導能力比較
- 抽象輸出與模板化
- 監控與優化

技能要求：
- 必備技能：平台配置
- 進階技能：多目標輸出工具鏈

延伸思考：
- 未來平台切換的可攜性？
- 規則上萬筆時的策略？

Practice Exercise（練習題）
- 基礎練習：把主映射轉成 _redirects 30 分鐘
- 進階練習：同時輸出Nginx與Workers版本 2 小時
- 專案練習：比較三平台延遲與成功率 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：規則在三平台可用
- 程式碼品質（30%）：輸出模板清楚
- 效能優化（20%）：延遲與鏈長
- 創新性（10%）：自動選型建議
```

## Case #18: 站內附件/圖片上傳路徑與WLW發佈相容性

### Problem Statement（問題陳述）
**業務場景**：WLW/客戶端編輯器常自動上傳圖片到指定目錄（或FTP），遷移到靜態站後需調整上傳策略，以免引用斷裂。
**技術挑戰**：靜態站的存儲與CDN佈署、圖片路徑規範化、相對/絕對URL策略。
**影響範圍**：內容呈現完整性、構建流程
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. WLW預設上傳位置不再存在
2. 圖片URL與新站結構不符
3. 構建流程未接手附件佈署

**深層原因**：
- 架構層面：附件儲存從動態改為靜態CDN
- 技術層面：缺乏自動同步步驟
- 流程層面：發布前未驗證資產可達性

### Solution Design（解決方案設計）
**解決策略**：將WLW上傳關閉或改為本地資產夾，透過構建流程（如CI）把assets上傳至CDN並修正引用路徑；或改用Markdown/本地圖片管理。

**實施步驟**：
1. 調整WLW圖片配置
- 實作細節：改本地儲存，統一放 /assets/images/ 年/月/
- 所需資源：WLW設定
- 預估時間：0.5天

2. 構建佈署資產到CDN
- 實作細節：CI把 /assets/ 同步到S3/R2
- 所需資源：CI、雲儲存
- 預估時間：0.5-1天

3. 驗證資產引用
- 實作細節：檢查404與相對/絕對URL策略
- 所需資源：批量檢測
- 預估時間：0.5天

**關鍵程式碼/設定**：
```yaml
# netlify.toml：部署前執行資產同步（示例）
[build]
  command = "npm run build && node sync-assets.js"
```

實際案例：對應作者以WLW搭配blog使用的場景，遷移後常遇到圖片路徑問題。
實作環境：WLW/Jekyll/CI/CD/CDN
實測數據（示例）：
- 改善前：圖片404比例高
- 改善後：圖片可用率接近100%
- 改善幅度：404顯著下降

Learning Points（學習要點）
核心知識點：
- 靜態資產管線
- 客戶端編輯器相容設定
- CDN佈署策略

技能要求：
- 必備技能：CI/CD、雲儲存
- 進階技能：批量連結檢測

延伸思考：
- 是否改用Git LFS或圖床服務？
- 構建指紋（hash）與快取策略？

Practice Exercise（練習題）
- 基礎練習：將圖片統一置於 /assets/images/ 30 分鐘
- 進階練習：CI同步資產到CDN 2 小時
- 專案練習：全站資產404掃描並修復 8 小時

Assessment Criteria（評估標準）
- 功能完整性（40%）：圖片上線可達
- 程式碼品質（30%）：腳本與配置明確
- 效能優化（20%）：快取與指紋
- 創新性（10%）：自動修正引用
```

--------------------------------
案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case 4（邊緣正規化基礎）
  - Case 6（用postid保留評論）
  - Case 7（canonical與評論協同）
  - Case 10（WLW基本連線）
  - Case 12（Beta升級風險控管）
  - Case 14（tag索引頁）
- 中級（需要一定基礎）
  - Case 1（大量redirect_from）
  - Case 2（中文十六進位/百分號編碼）
  - Case 3（slug正規化）
  - Case 8（自動化重導測試）
  - Case 13（中文→拼音slug）
  - Case 17（多平台重導策略）
  - Case 18（資產/圖片佈署）
- 高級（需要深厚經驗）
  - Case 5（多階段映射整併）
  - Case 9（WXR→Jekyll自動遷移）
  - Case 15（aspx ID動態映射）

2. 按技術領域分類
- 架構設計類：Case 1、5、7、9、15、17
- 效能優化類：Case 4、8、17
- 整合開發類：Case 6、9、10、13、14、18
- 除錯診斷類：Case 2、3、8、11、15
- 安全防護類：Case 12（變更管理/風險控管）

3. 按學習目標分類
- 概念理解型：Case 4、7、12、17
- 技能練習型：Case 2、3、6、8、10、13、14、18
- 問題解決型：Case 1、5、9、11、15
- 創新應用型：Case 8、9、13、17

案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 4（大小寫與尾斜線正規化基礎）→建立URL正規化概念
  - Case 1（redirect_from核心）→學會保留舊URL主流程
  - Case 7（canonical與評論協同）→理解頁面層與伺服器層一致性
- 依賴關係：
  - Case 5（映射整併）依賴 Case 1/4 的基礎認知
  - Case 8（自動化測試）依賴 Case 1/4/5 的規則落地
  - Case 9（WXR自動遷移）依賴 Case 1/2/3 的slug/redirect策略
  - Case 15（aspx映射）依賴 Case 5（主表）與 Case 8（驗證）
  - Case 6/7（評論）依賴 Case 1（最終URL穩定）
- 完整學習路徑建議：
  1) Case 4 → 1 → 7（建立URL與頁面一致性基礎）
  2) Case 2 → 3 → 13 → 14（解決中文與slug/標籤問題）
  3) Case 5 → 15（高複雜度歷史映射整併）
  4) Case 8（自動化驗證）貫穿全程
  5) Case 9（自動遷移）將策略落實於工具鏈
  6) Case 6 → 10 → 11 → 12 → 18 → 17（編輯器整合、穩定性與平台選型）

以上15+案例皆直接或間接源自原文與其front matter中呈現的真實問題樣態（多重歷史URL、中文slug、WP→Jekyll遷移、WLW整合與IME問題），並補上可落地的程式碼、流程與評估方法，便於教學、實作與評量。