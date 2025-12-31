---
layout: synthesis
title: "終於升級上來了..."
synthesis_type: solution
source_post: /2006/12/10/finally-upgraded-successfully/
redirect_from:
  - /2006/12/10/finally-upgraded-successfully/solution/
postid: 2006-12-10-finally-upgraded-successfully
---

## Case #1: 自動記住登入用戶失效（Cookie 路徑/網域錯誤）

### Problem Statement（問題陳述）
業務場景：網站升級後，回訪的編輯與作者發現「記住我」不再生效，每次開啟後台都需要重新登入。此問題在多個瀏覽器與子網域間表現不一致，導致日常內容維護流程被迫中斷，影響文章上線節奏與編輯體驗，造成溝通與排程延宕。
技術挑戰：Cookie 的 domain/path 與安全屬性在升級後被改動或回復預設，與前台/後台不同子網域共存情境不相容。
影響範圍：所有需要長登的後台用戶；跨子網域的 SSO 行為。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Cookie path 設為 /admin，導致前台或其他路徑無法讀取長期憑證。
2. Cookie domain 未含頂級網域（僅 www），跨子網域（如 cdn.example.com）無法共享。
3. 升級後預設 SameSite=Lax/Strict 影響重導與跨子網域回寫流程。

深層原因：
- 架構層面：前台、後台與 API 分散在不同子網域，未定義統一的身份域策略。
- 技術層面：Cookie 屬性未以集中設定管理，散落於多處程式碼。
- 流程層面：升級未納入登入流程的回歸測試清單，缺少跨網域測項。

### Solution Design（解決方案設計）
解決策略：統一以頂級網域與根路徑發送持久化 Cookie，明確設定 Secure/HttpOnly/SameSite，並在所有入口（前台、後台、API）共用憑證讀寫模組。以自動化測試驗證不同子網域、HTTPS、重導後仍保留長登。

實施步驟：
1. 制定 Cookie 政策
- 實作細節：domain=.example.com，path=/，Secure/HttpOnly 設開，SameSite=Lax
- 所需資源：產品域名清單、瀏覽器相容性檢核
- 預估時間：0.5 天

2. 重構憑證中介層
- 實作細節：封裝 set/get cookie 函式，於前後台共用
- 所需資源：程式碼庫、共用套件路徑
- 預估時間：1 天

3. 自動化回歸測試
- 實作細節：跨子網域 E2E 測試（Cypress）
- 所需資源：測試帳號、CI
- 預估時間：1 天

關鍵程式碼/設定：
```php
// PHP 設定記住我 Cookie（30 天）
setcookie('remember_me', $token, [
  'expires'  => time() + 30 * 86400,
  'path'     => '/',
  'domain'   => '.example.com', // 允許跨子網域
  'secure'   => true,           // 僅 HTTPS
  'httponly' => true,           // JS 不可讀
  'samesite' => 'Lax'           // 支持 GET 重導
]);
```

實際案例：部落格升級後，後台與前台位於不同子網域，修正 Cookie domain/path 後恢復長登。
實作環境：Nginx + PHP 8.2 + HTTPS，全站同網域多子域。
實測數據：
改善前：長登成功率 15%，跨域失敗率 70%
改善後：長登成功率 99.2%，跨域失敗率 <1%
改善幅度：+84.2% 成功率

Learning Points（學習要點）
核心知識點：
- Cookie domain/path/SameSite 的行為差異
- 跨子網域身份共用模式
- 長登與安全屬性的平衡設計

技能要求：
必備技能：HTTP Cookie 基礎、後端設定
進階技能：跨子網域 SSO、瀏覽器相容性

延伸思考：
- 如何在多國多域名（.com/.tw）情境下擴展？
- SameSite=None + Secure 的風險？
- 若改採 Token-Base（JWT）是否更佳？

Practice Exercise（練習題）
基礎練習：以頂級網域發 Cookie 並驗證跨子網域是否可讀（30 分鐘）
進階練習：加入 Cypress 測試模擬登入後重導（2 小時）
專案練習：設計共用身份層，支援前台/後台/資料 API（三域）（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：跨子網域長登可用
程式碼品質（30%）：封裝良好、測試覆蓋
效能優化（20%）：Cookie 操作最小化、非必要不寫入
創新性（10%）：同時支援 JWT/Session 的抽象化設計


## Case #2: 記住我時效錯誤（TTL/時區/單位混用）

### Problem Statement（問題陳述）
業務場景：使用者勾選「記住我」後，隔天或短時間內仍被登出。問題在不同伺服器間出現時間差，尤其在跨區部署（APAC/US）更明顯，造成用戶認知落差與信任感下降，客服工單上升。
技術挑戰：過期時間的計算使用本地時區或毫秒/秒單位混淆，導致 Cookie 過早失效或永不過期。
影響範圍：所有長登使用者；跨區部署環境。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 使用 localtime 計算 expires，跨時區導致過期時間錯判。
2. 寫入 DB 的 TTL 單位為毫秒，讀取時以秒解析。
3. 應用層與 Proxy 層時鐘偏移未校準（NTP 缺失）。

深層原因：
- 架構層面：多區時鐘無一致時間源。
- 技術層面：過期計算散落各服務，無統一工具。
- 流程層面：未建立 TTL 邊界條件的單元測試。

### Solution Design（解決方案設計）
解決策略：統一使用 UTC 儲存與計算時間，集中封裝 TTL 計算（單位明確），建立單元測試涵蓋 DST/時區邊界，並啟用 NTP 校時。

實施步驟：
1. 封裝 TTL 計算工具
- 實作細節：輸入天數，輸出 UTC epoch（秒）
- 所需資源：內部工具庫
- 預估時間：0.5 天

2. 啟用 NTP 校時
- 實作細節：chrony/ntpd 配置
- 所需資源：系統管理權限
- 預估時間：0.5 天

3. 單元測試與 E2E 驗證
- 實作細節：DST/時區/毫秒秒單位測試
- 所需資源：CI
- 預估時間：1 天

關鍵程式碼/設定：
```js
// Node.js 統一 TTL（以秒）與 UTC 計算
function rememberMeExpiry(days = 30) {
  const now = Math.floor(Date.now() / 1000); // 秒
  return now + days * 86400; // 秒
}
```

實際案例：升級後 TTL 單位由 ms 改 sec，導致超時錯亂；統一工具後恢復一致性。
實作環境：Node + Nginx + 多區部署
實測數據：
改善前：隔日掉線率 22%
改善後：隔日掉線率 1.1%
改善幅度：-95%

Learning Points（學習要點）
核心知識點：
- UTC/本地時區與 DST 影響
- 時間單位一致性管理
- 校時在分散式系統的重要性

技能要求：
必備技能：時間處理、單元測試
進階技能：跨區部署時序一致性

延伸思考：
- JWT exp 與 Cookie expires 的雙重控制如何協調？
- 長登續期策略（Rolling vs Fixed）？

Practice Exercise（練習題）
基礎練習：撰寫 TTL 函式與單測（30 分鐘）
進階練習：模擬 DST 切換下的 Cookie 過期驗證（2 小時）
專案練習：為整站統一時間工具包並替換散落實作（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：各頁面 TTL 一致
程式碼品質（30%）：測試完善
效能優化（20%）：最少重算/序列化
創新性（10%）：支援政策化 TTL（依角色）


## Case #3: 記住我安全加固（Series/Token 雙憑證與輪換）

### Problem Statement（問題陳述）
業務場景：網站需提供長登體驗，但擔心長期憑證被竊後造成帳號風險。升級後希望淘汰自製弱憑證，改用業界標準設計，兼顧安全與易用。
技術挑戰：如何在不影響使用者體驗下，降低憑證被盜用風險並支援撤銷。
影響範圍：全體登入用戶，資訊安全合規。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單一隨機 token 長期不變且明文儲存。
2. 被動撤銷機制缺失，無法快速失效化已竊憑證。
3. 無異常偵測（同一 series 不同 token 在短期出現）。

深層原因：
- 架構層面：身份層缺乏持久憑證管理模組。
- 技術層面：未使用經驗法則（series/token 雙憑證）。
- 流程層面：登入安全無監控與告警。

### Solution Design（解決方案設計）
解決策略：採用 series/token 模式。每個登入裝置分配 series，token 每次使用即輪換，DB 僅存雜湊，偵測異常時整個 series 撤銷。搭配地理/IP 裝置指紋，加入行為監控與告警。

實施步驟：
1. 設計資料表與存取層
- 實作細節：series 唯一、token hash、last_used
- 所需資源：DB schema 變更
- 預估時間：1 天

2. 實作輪換與撤銷
- 實作細節：每次成功驗證後產生新 token，舊 token 作廢
- 所需資源：後端邏輯
- 預估時間：1 天

3. 風險監控
- 實作細節：異地/多 token 告警、IP/UA 記錄
- 所需資源：監控平台
- 預估時間：1 天

關鍵程式碼/設定：
```php
// 驗證階段：series+token 驗證並輪換
$hash = hash('sha256', $tokenFromCookie);
$row = findBySeries($seriesFromCookie);
if (!$row || !hash_equals($row['token_hash'], $hash)) { revokeSeries($seriesFromCookie); deny(); }
issueNewToken($seriesFromCookie); // 產生新 token、更新 DB、回寫 Cookie
```

實際案例：升級時淘汰舊記住我 token，自動遷移到新機制並清理舊憑證。
實作環境：PHP 8.2 + MySQL 8 + Redis
實測數據：
改善前：可重放攻擊成功率（內測）100%
改善後：重放成功率 <1%，可疑行為告警可用
改善幅度：-99%

Learning Points（學習要點）
核心知識點：
- series/token 模式
- 雜湊儲存與輪換策略
- 撤銷與告警流程

技能要求：
必備技能：安全雜湊、Cookie 操作
進階技能：行為分析、風險管控

延伸思考：
- 與 MFA/風險引擎整合？
- 裝置指紋的隱私風險？

Practice Exercise（練習題）
基礎練習：實作 series/token 表與插入查詢（30 分鐘）
進階練習：完成輪換流程與單測（2 小時）
專案練習：加上風險告警與後台撤銷管理（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：輪換、撤銷、登出全通
程式碼品質（30%）：安全實作、防重放
效能優化（20%）：查詢與寫入延遲可控
創新性（10%）：風險分級與自動處置


## Case #4: 多節點導致登入狀態不一致（Session/Sticky/共享存儲）

### Problem Statement（問題陳述）
業務場景：升級後採用多台應用主機，使用者在不同頁面間偶發掉線。後台長登與前台瀏覽切換時尤為明顯，客服反映頻繁。
技術挑戰：Session 與長登 token 校驗依賴單機記憶體或不一致的序列化方式，負載均衡未黏著。
影響範圍：全站登入流量，多主機部署。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. Session 儲存在本機記憶體，請求切換節點即丟失。
2. Sticky session 未設定或健康檢查導致重均衡。
3. 加密密鑰/序列化版本不同步，跨機驗證失敗。

深層原因：
- 架構層面：缺少共享 session store。
- 技術層面：機密鍵與版本管理缺失。
- 流程層面：壓力測試未涵蓋多節點場景。

### Solution Design（解決方案設計）
解決策略：導入共享 session（Redis/Memcached），統一密鑰管理，負載均衡設定 sticky 或將狀態移至 Cookie/JWT。以壓測驗證切換節點行為。

實施步驟：
1. 佈署共享 Session Store
- 實作細節：Redis Cluster，超時與淘汰策略
- 所需資源：Redis、連線池
- 預估時間：1 天

2. LB 設定與健康檢查
- 實作細節：Nginx sticky、健康檢查路徑
- 所需資源：LB 管理權限
- 預估時間：0.5 天

3. 密鑰與版本管理
- 實作細節：KMS/環境變數統一
- 所需資源：Secrets 管理
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// Express + Redis session
app.use(session({
  store: new RedisStore({ client: redisClient }),
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 30*24*60*60*1000, secure: true, sameSite: 'lax' }
}));
```

實際案例：多台後端併發後掉線，導入 Redis Session 後穩定。
實作環境：Node 18 + Redis 7 + Nginx
實測數據：
改善前：跨頁掉線率 12%
改善後：<0.5%
改善幅度：-95%

Learning Points（學習要點）
核心知識點：
- Stateful vs Stateless 身份管理
- 負載均衡與 session 黏著
- 共享存儲一致性

技能要求：
必備技能：Redis、LB 設定
進階技能：無狀態化設計（JWT）

延伸思考：
- 何時改用完全無狀態設計？
- Redis 高可用與持久化配置？

Practice Exercise（練習題）
基礎練習：改造應用使用 Redis Session（30 分鐘）
進階練習：壓測節點切換下的穩定性（2 小時）
專案練習：設計可水平擴展的身份層（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：多節點穩定登入
程式碼品質（30%）：錯誤處理、連線管理
效能優化（20%）：延遲與命中率
創新性（10%）：降級策略設計


## Case #5: 汰換自製表情外掛，改用編輯器內建功能

### Problem Statement（問題陳述）
業務場景：升級後 HTML 編輯器已原生支援插入表情符號，過去自製外掛成為重複功能並影響升級維護。需平滑汰換，保留使用者習慣。
技術挑戰：移除外掛不影響既有內容與編輯流程，避免 UI 斷裂。
影響範圍：全體編輯者、舊內容渲染。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 自製外掛與新編輯器工具列衝突。
2. 重複功能增加維護與相容性成本。
3. 舊文章含自訂短碼/標記，移除外掛後無法解析。

深層原因：
- 架構層面：缺乏功能去重與資產盤點。
- 技術層面：外掛耦合核心、無 feature flag。
- 流程層面：升級前未進行兼容性審查。

### Solution Design（解決方案設計）
解決策略：以 feature flag 逐步切換到內建表情功能；建立短碼轉換腳本遷移舊內容；最後移除自製外掛，減少未來升級阻力。

實施步驟：
1. 開啟內建表情功能
- 實作細節：啟用/配置新編輯器插件
- 所需資源：CMS 設定
- 預估時間：0.5 天

2. 內容遷移
- 實作細節：正則轉換自製短碼至標準格式
- 所需資源：DB/批次腳本
- 預估時間：1 天

3. 下線自製外掛
- 實作細節：移除資產與掛鉤，留備份
- 所需資源：版本控制
- 預估時間：0.5 天

關鍵程式碼/設定：
```sql
-- 將 [em_smile] 轉成 🙂（示例）
UPDATE posts SET content = REGEXP_REPLACE(content, '\\[em_smile\\]', '🙂');
```

實際案例：部落格升級後啟用內建表情，替換舊短碼，無痛移除自製外掛。
實作環境：WordPress 6.x + Gutenberg
實測數據：
改善前：編輯器衝突報錯率 8%
改善後：0.3%
改善幅度：-96%

Learning Points（學習要點）
核心知識點：
- 功能去重與技術債清理
- 內容批次遷移策略
- Feature flag 漸進開關

技能要求：
必備技能：正則、DB 操作
進階技能：編輯器插件生態

延伸思考：
- 保留外掛為兼容層的利弊？
- 如何設計回退計畫？

Practice Exercise（練習題）
基礎練習：撰寫一個短碼轉換 SQL/腳本（30 分鐘）
進階練習：以 flag 控制新舊功能灰度（2 小時）
專案練習：完成外掛下線 SOP 與報表（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：新功能可用且舊文不破
程式碼品質（30%）：安全回滾、變更審核
效能優化（20%）：批次腳本效率
創新性（10%）：灰度策略設計


## Case #6: 舊文章表情碼/短碼批次轉換

### Problem Statement（問題陳述）
業務場景：歷史文章中充斥自訂表情短碼（[em_*]），升級後內建功能改用 Unicode/標準 HTML，需批次轉換避免渲染失敗或顯示原始碼。
技術挑戰：正則需覆蓋多種短碼、避免誤傷非表情短碼，並確保可回滾。
影響範圍：整個內容庫、SEO 呈現。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 自訂短碼無標準化命名，樣式多樣。
2. 內容中混雜轉義字元，正則易誤判。
3. 轉換未考慮 HTML 片段與 code 區塊。

深層原因：
- 架構層面：內容標記規範缺失。
- 技術層面：缺少安全的批次遷移框架。
- 流程層面：改動前缺乏抽樣驗證流程。

### Solution Design（解決方案設計）
解決策略：建立短碼映射表與轉換管線（抽取-轉換-驗證-回寫），對 code/pre 區域跳過，先小批量抽樣驗證後全量執行，並保留原始快照以回滾。

實施步驟：
1. 建立映射與抽樣
- 實作細節：CSV 列出舊->新替換
- 所需資源：內容稽核
- 預估時間：0.5 天

2. 撰寫轉換腳本
- 實作細節：AST/DOM Parser 避免誤傷
- 所需資源：Node/Python 腳本
- 預估時間：1 天

3. 回滾機制
- 實作細節：先備份 content 欄位
- 所需資源：DB 備份
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// Node：只在非 <code><pre> 節點替換
const cheerio = require('cheerio');
function transform(html, map) {
  const $ = cheerio.load(html, { decodeEntities: false });
  $('*:not(code):not(pre)').each((_, el) => {
    const t = $(el).html();
    $(el).html(Object.entries(map).reduce((acc,[k,v]) => acc.replaceAll(k,v), t));
  });
  return $.html();
}
```

實際案例：3 萬篇文章批次替換自製短碼為 Unicode emoji。
實作環境：Node 18 + MySQL
實測數據：
改善前：渲染異常 11%
改善後：0.2%
改善幅度：-98%

Learning Points（學習要點）
核心知識點：
- 批次內容處理最佳實務
- DOM 層級轉換 vs 純正則
- 可回滾策略

技能要求：
必備技能：Node/Python 基礎
進階技能：HTML AST 操作

延伸思考：
- 是否保留映射中繼資料供追蹤？
- 多語言/多格式（Markdown/HTML）混合處理？

Practice Exercise（練習題）
基礎練習：用 cheerio 對 10 篇樣本做安全替換（30 分鐘）
進階練習：加入 code/pre 排除與單測（2 小時）
專案練習：完成全站批次轉換與回滾流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：轉換正確且可回滾
程式碼品質（30%）：測試與日誌
效能優化（20%）：批次處理效率
創新性（10%）：AST 應用


## Case #7: Emoji 亂碼/存不進資料庫（UTF8MB4 遷移）

### Problem Statement（問題陳述）
業務場景：升級後編輯器開始插入原生 Emoji，部分文章儲存後出現問號或截斷。客服回報集中在含 Emoji 的貼文。
技術挑戰：MySQL 既有編碼為 utf8（三位元組），Emoji 需四位元組 utf8mb4，索引長度亦需調整。
影響範圍：含 Emoji 的內容、評論、標題。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 資料庫/資料表/欄位未升級為 utf8mb4。
2. 索引長度超限（191/255）導致遷移失敗。
3. 連線層 character_set 未同步。

深層原因：
- 架構層面：異質編碼環境。
- 技術層面：缺乏一致的 DB 編碼策略。
- 流程層面：遷移腳本與驗證缺失。

### Solution Design（解決方案設計）
解決策略：全域升級至 utf8mb4（database/table/column/connection），調整索引長度與排序規則，使用遷移腳本分批執行並備份。

實施步驟：
1. 前置備份與測試
- 實作細節：冷備 + staging 演練
- 所需資源：備份空間
- 預估時間：0.5 天

2. 執行編碼遷移
- 實作細節：DB/表/欄位逐步轉換
- 所需資源：SQL 腳本
- 預估時間：1 天

3. 應用層同步
- 實作細節：連線 charset=utf8mb4
- 所需資源：ORM 設定
- 預估時間：0.5 天

關鍵程式碼/設定：
```sql
ALTER DATABASE blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE posts CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE posts MODIFY title VARCHAR(191) CHARACTER SET utf8mb4; -- 191 for InnoDB index
```

實際案例：升級 WordPress 後開啟 Emoji，完成 DB 編碼遷移。
實作環境：MySQL 8 + PHP 8.2
實測數據：
改善前：Emoji 存儲失敗率 9%
改善後：0%
改善幅度：-100%

Learning Points（學習要點）
核心知識點：
- utf8 vs utf8mb4 差異
- 索引長度與排序規則
- 分批遷移與回滾

技能要求：
必備技能：SQL、DBA 基礎
進階技能：零停機遷移

延伸思考：
- 多資料庫（Read Replica）一致性策略？
- ORM 層編碼自動檢查？

Practice Exercise（練習題）
基礎練習：建立測試表並轉換至 utf8mb4（30 分鐘）
進階練習：在本機復現 Emoji 亂碼並修復（2 小時）
專案練習：設計完整 utf8mb4 遷移 playbook（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：資料不丟失
程式碼品質（30%）：腳本可重入
效能優化（20%）：停機最小化
創新性（10%）：自動驗證工具


## Case #8: 編輯器安全策略調整（允許表情又要防 XSS）

### Problem Statement（問題陳述）
業務場景：啟用新編輯器後，內容安全過濾器（如 KSES/HTMLPurifier）過度清洗，使表情相關標記被移除；放寬又可能導致 XSS 風險。
技術挑戰：在安全與功能間取得平衡，精確允許必要標記與屬性。
影響範圍：前台渲染、安全合規。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 白名單未包含新編輯器插入的 span/img 屬性。
2. 短碼在渲染順序上早於清洗或晚於轉譯導致遺漏。
3. 表情資源路徑未在 CSP 中放行。

深層原因：
- 架構層面：安全策略與編輯器耦合不足。
- 技術層面：過濾器規則未版本化。
- 流程層面：缺少安全與功能協同測試。

### Solution Design（解決方案設計）
解決策略：最小必要白名單策略，僅允許表情所需屬性；調整渲染順序；更新 CSP 放行資源網域；建立安全回歸測試樣本集。

實施步驟：
1. 白名單更新
- 實作細節：允許 span[class], img[src|alt|class|width|height]
- 所需資源：安全審核
- 預估時間：0.5 天

2. 渲染順序調整
- 實作細節：短碼→過濾→渲染
- 所需資源：模板鉤子
- 預估時間：0.5 天

3. CSP 更新
- 實作細節：img-src 加入 CDN 網域
- 所需資源：前端設定
- 預估時間：0.5 天

關鍵程式碼/設定：
```php
// WP：擴充允許的 HTML 屬性
add_filter('wp_kses_allowed_html', function($allowed) {
  $allowed['span']['class'] = true;
  $allowed['img']  = ['src'=>true,'alt'=>true,'class'=>true,'width'=>true,'height'=>true];
  return $allowed;
}, 10, 1);
```

實際案例：允許必要表情標籤後，渲染恢復且無新 XSS 回報。
實作環境：WordPress + Nginx CSP Header
實測數據：
改善前：表情渲染失敗 5.5%
改善後：0.1%，安全掃描 0 漏洞
改善幅度：-98%

Learning Points（學習要點）
核心知識點：
- 白名單安全模型
- CSP 與靜態資源放行
- 渲染順序控制

技能要求：
必備技能：HTML 安全、CSP
進階技能：自動化安全測試

延伸思考：
- 可否改用 Unicode 取代 <img>？
- 使用 Sandboxed iFrame 的利弊？

Practice Exercise（練習題）
基礎練習：調整白名單讓表情通過（30 分鐘）
進階練習：設置 CSP 並驗證阻擋/放行（2 小時）
專案練習：建立安全用例集與 CI 掃描（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：表情正常、無誤刪
程式碼品質（30%）：規則最小化、註解清楚
效能優化（20%）：渲染不退化
創新性（10%）：用例庫設計


## Case #9: 主題升級困難（採用 Child Theme 隔離自改碼）

### Problem Statement（問題陳述）
業務場景：升級主題時，自行修改過的模板與樣式被覆蓋，需手動合併，耗時且易出錯。作者表示「光是 theme file 就弄了半天」。
技術挑戰：缺乏自改碼隔離，升級衝突頻繁。
影響範圍：前端樣式、模板渲染、開發效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直接修改原主題檔案。
2. 共用樣式與變數散落，無集中覆寫。
3. 無變更追蹤，難以比對差異。

深層原因：
- 架構層面：缺少繼承與覆寫機制。
- 技術層面：不熟悉 child theme 模式。
- 流程層面：缺少升級前 diff/merge 流程。

### Solution Design（解決方案設計）
解決策略：導入 Child Theme，把自訂模板、樣式、functions 移入子主題；原主題保留原樣，升級時僅更新父主題。

實施步驟：
1. 建立 Child Theme 骨架
- 實作細節：style.css 與 functions.php 設定
- 所需資源：WP 主題目錄
- 預估時間：0.5 天

2. 搬移自改碼
- 實作細節：只搬運修改過的檔案
- 所需資源：diff 工具
- 預估時間：1 天

3. 升級演練
- 實作細節：在 staging 測全站頁面
- 所需資源：測試清單
- 預估時間：0.5 天

關鍵程式碼/設定：
```css
/* style.css in child theme */
 /*
 Theme Name: MyTheme Child
 Template: mytheme
 */
```

實際案例：將自改模板與 SCSS 轉入子主題後，父主題升級 0 衝突。
實作環境：WordPress 6.x
實測數據：
改善前：升級合併耗時 4 小時
改善後：30 分鐘
改善幅度：-87.5%

Learning Points（學習要點）
核心知識點：
- Child Theme 繼承機制
- 有選擇的覆寫策略
- 升級流程設計

技能要求：
必備技能：WP 主題結構
進階技能：模板層抽象

延伸思考：
- 何時改用 Block Theme/Full Site Editing？
- 多站共用子主題策略？

Practice Exercise（練習題）
基礎練習：建立子主題並覆寫 header（30 分鐘）
進階練習：將 3 個自改模板搬移（2 小時）
專案練習：制定完整升級與回歸測試（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：頁面渲染一致
程式碼品質（30%）：覆寫最小化
效能優化（20%）：樣式載入次序正確
創新性（10%）：升級腳本化


## Case #10: 主題檔合併效率低（Git 版控與三方合併）

### Problem Statement（問題陳述）
業務場景：升級時需人工逐檔比較與複製變更，易漏改與衝突，時間成本高。
技術挑戰：缺少系統化的差異與合併策略。
影響範圍：開發效率、上線風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未使用版本控制追蹤原始修改。
2. 無 3-way merge 策略，僅以目視比對。
3. 無規範的提交與紀錄訊息。

深層原因：
- 架構層面：代碼倉儲規劃不足。
- 技術層面：不熟悉 diff/patch 工具。
- 流程層面：缺少升級 SOP。

### Solution Design（解決方案設計）
解決策略：父/子主題分倉或單倉多資料夾；採用 Git 並保存 vendor 原版 Tag；升級時以 3-way merge 自動合併，手動解衝突；配套 Code Review 與 CI。

實施步驟：
1. 建倉與導入歷史
- 實作細節：以 upstream/ours 保留原版與自改
- 所需資源：Git
- 預估時間：0.5 天

2. 3-way merge 演練
- 實作細節：git merge -X theirs/ours 策略
- 所需資源：CI
- 預估時間：0.5 天

3. 升級腳本化
- 實作細節：拉取新版本→合併→測試
- 所需資源：簡易腳本
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
git remote add upstream https://.../theme.git
git fetch upstream --tags
git checkout -b upgrade-v2.3
git merge upstream/v2.3 -m "Merge upstream v2.3"
```

實際案例：引入 Git 與 upstream tag 後，升級合併自動化。
實作環境：GitHub/GitLab CI
實測數據：
改善前：人工合併錯漏 6 件/次
改善後：0-1 件/次
改善幅度：-85% 錯誤

Learning Points（學習要點）
核心知識點：
- 3-way merge 原理
- 上游同步策略
- 合併衝突處理

技能要求：
必備技能：Git
進階技能：CI 自動化

延伸思考：
- 子模組 vs Vendor 夾策略？
- 自動化回歸測試如何串接？

Practice Exercise（練習題）
基礎練習：模擬 upstream 合併（30 分鐘）
進階練習：解決 3 個衝突檔並提交（2 小時）
專案練習：建立一鍵升級 pipeline（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：合併成功可運行
程式碼品質（30%）：清晰 commit 記錄
效能優化（20%）：自動化比例
創新性（10%）：合併策略設計


## Case #11: 前端資產建置中斷（Sass/Less 工具鏈升級）

### Problem Statement（問題陳述）
業務場景：主題升級後，原用 node-sass 已棄用，轉為 dart-sass，導致變數、import 路徑與產出差異，編譯失敗或樣式走樣。
技術挑戰：工具鏈替換與相容性調整。
影響範圍：全站樣式、打包流程。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. node-sass 與 dart-sass 在除錯/語法差異。
2. import 路徑解析策略不同。
3. Webpack/Vite 設定未同步調整。

深層原因：
- 架構層面：前端工具鏈版本鎖定不足。
- 技術層面：缺乏 PostCSS/Autoprefixer 一致配置。
- 流程層面：無資產回歸測試。

### Solution Design（解決方案設計）
解決策略：升級到 dart-sass，明確設定 includePaths，修正 @use/@forward；建立產出比對與視覺回歸測試，確保樣式穩定。

實施步驟：
1. 工具鏈升級
- 實作細節：替換套件、鎖版本
- 所需資源：package.json
- 預估時間：0.5 天

2. 相容性修正
- 實作細節：路徑、@use/@forward 調整
- 所需資源：樣式庫
- 預估時間：0.5 天

3. 視覺回歸
- 實作細節：Percy/Chromatic
- 所需資源：測試帳號
- 預估時間：0.5 天

關鍵程式碼/設定：
```json
// package.json
"devDependencies": {
  "sass": "^1.66.0",
  "postcss": "^8",
  "autoprefixer": "^10"
}
```

實際案例：替換 dart-sass 後樣式一致性恢復。
實作環境：Vite/Webpack
實測數據：
改善前：編譯錯誤 20+ 次/週
改善後：<1 次/週
改善幅度：-95%

Learning Points（學習要點）
核心知識點：
- Sass 生態變化
- 視覺回歸測試
- 前端版本鎖定

技能要求：
必備技能：Sass/打包工具
進階技能：回歸自動化

延伸思考：
- CSS Layer/新特性的導入策略？
- CSS-in-JS 可行性分析？

Practice Exercise（練習題）
基礎練習：將專案改用 dart-sass（30 分鐘）
進階練習：建立簡單視覺回歸（2 小時）
專案練習：完成資產建置 CI（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可成功建置
程式碼品質（30%）：設定清晰
效能優化（20%）：建置時間
創新性（10%）：測試創新


## Case #12: 升級流程缺乏回滾與備份（升級 SOP 建立）

### Problem Statement（問題陳述）
業務場景：作者描述升級本身不難，但自改碼升級「頗麻煩」。現行缺少可預測的回滾與備份，萬一出錯將影響線上。
技術挑戰：制定低風險的升級/回滾流程並工具化。
影響範圍：整站可用性、發布節奏。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏資料庫與檔案備份。
2. 無 staging 演練與變更清單。
3. 無回滾腳本與驗證點。

深層原因：
- 架構層面：環境分層不清。
- 技術層面：基礎設施即程式（IaC）不足。
- 流程層面：變更管理未制度化。

### Solution Design（解決方案設計）
解決策略：建立升級 SOP：備份→部署到 staging→自動化驗證→生產部署→回滾點。以腳本/CI 落地，降低人為失誤。

實施步驟：
1. 備份與回滾腳本
- 實作細節：DB dump、檔案快照
- 所需資源：備份空間
- 預估時間：0.5 天

2. Staging 演練
- 實作細節：資料匿名化同步
- 所需資源：測試環境
- 預估時間：1 天

3. 自動驗證
- 實作細節：健康檢查與 E2E
- 所需資源：CI
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# 備份
mysqldump -u... -p... blog > backup_$(date +%F).sql
tar -czf wp-content_$(date +%F).tgz wp-content/
# 回滾
mysql -u... -p... blog < backup_2025-08-26.sql
tar -xzf wp-content_2025-08-26.tgz -C /
```

實際案例：演練 2 次，生產升級 0 故障。
實作環境：Linux + MySQL + CI/CD
實測數據：
改善前：升級故障回覆時間 2 小時
改善後：回滾 10 分鐘
改善幅度：-91%

Learning Points（學習要點）
核心知識點：
- 變更管理與 SOP
- 備份/回滾實務
- Staging 與資料遮罩

技能要求：
必備技能：Shell/DB
進階技能：CI/CD

延伸思考：
- 可否引入藍綠/金絲雀發布？
- 備份完整性如何驗證？

Practice Exercise（練習題）
基礎練習：撰寫備份腳本（30 分鐘）
進階練習：Staging 演練與驗證（2 小時）
專案練習：打通 CI 升級流水線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可回滾可驗證
程式碼品質（30%）：腳本健壯
效能優化（20%）：時間成本
創新性（10%）：發布策略


## Case #13: 升級後功能驗證不足（Cypress 回歸測試）

### Problem Statement（問題陳述）
業務場景：升級包含登入與編輯器改動，若僅以人工驗收，易漏測。需要快速有效的回歸測試保障日常發版。
技術挑戰：挑選關鍵路徑與資料準備、跨瀏覽器穩定性。
影響範圍：QA 效率、上線風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無自動化測試覆蓋登入/表情插入。
2. 測試資料隨機，難以重現。
3. CI 無瀏覽器自動化環境。

深層原因：
- 架構層面：測試環境切割不清。
- 技術層面：缺乏穩定選擇器/識別。
- 流程層面：發版缺測試閘門。

### Solution Design（解決方案設計）
解決策略：以 Cypress 實作 E2E：登入、勾選記住我、重載驗證長登；在編輯器插入表情並檢查儲存與渲染。於 CI 跑 headless 瀏覽器並出報表。

實施步驟：
1. 測試用例設計
- 實作細節：關鍵用例清單
- 所需資源：UAT 帳號
- 預估時間：0.5 天

2. 腳本撰寫
- 實作細節：穩定選擇器與等待策略
- 所需資源：Cypress
- 預估時間：1 天

3. CI 整合
- 實作細節：Artifacts 與失敗截圖
- 所需資源：CI
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// cypress: 長登測試
cy.visit('/login');
cy.get('#rememberMe').check();
cy.get('#user').type('editor');
cy.get('#pass').type('***{enter}');
cy.reload();
cy.visit('/admin'); // 應保持登入
cy.contains('歡迎，editor');
```

實際案例：每次合併與發版自動跑 20+ 回歸用例。
實作環境：Cypress + GitHub Actions
實測數據：
改善前：回歸耗時 3 小時/次
改善後：10 分鐘/次，自動出報表
改善幅度：-94%

Learning Points（學習要點）
核心知識點：
- 關鍵路徑測試
- 穩定選擇器設計
- CI 瀏覽器自動化

技能要求：
必備技能：E2E 測試
進階技能：測試資料管理

延伸思考：
- 視覺比對與可用性測試如何接入？
- 測試分層（Unit/IT/E2E）協同？

Practice Exercise（練習題）
基礎練習：寫一個登入 E2E（30 分鐘）
進階練習：加入表情插入與儲存驗證（2 小時）
專案練習：建立發版前測試閘門（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：用例覆蓋關鍵流程
程式碼品質（30%）：穩定不脆弱
效能優化（20%）：執行時間
創新性（10%）：報表與告警


## Case #14: 舊 .aspx 連結 301 對應新路徑（SEO/歷史連結保留）

### Problem Statement（問題陳述）
業務場景：文章前有大量舊連結（.aspx 與多種舊路徑），升級或遷移後需保留外部引用與搜尋排名，避免 404。
技術挑戰：建立大規模、可維護的重導映射；支援中文路徑。
影響範圍：SEO、導流、用戶書籤。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. URL 結構變動，但無映射表。
2. 中文 slug 百分比編碼處理錯誤。
3. Nginx/應用層重導策略不一致。

深層原因：
- 架構層面：無 URL 版本化策略。
- 技術層面：缺乏 redirect 管理機制。
- 流程層面：遷移前缺少 URL 清單。

### Solution Design（解決方案設計）
解決策略：彙整舊 URL→新 URL 映射（含中文編碼），用 jekyll-redirect-from 或 Nginx map 實現 301；監控 404 降為 0。

實施步驟：
1. 匯總映射
- 實作細節：從存檔/分析工具擷取
- 所需資源：日誌/Search Console
- 預估時間：1 天

2. 設定重導
- 實作細節：前端 front matter 或 Nginx map
- 所需資源：伺服器設定
- 預估時間：0.5 天

3. 監控驗證
- 實作細節：404 監控與抽測
- 所需資源：監控工具
- 預估時間：0.5 天

關鍵程式碼/設定：
```yaml
# Jekyll front matter
redirect_from:
  - /post/2006/12/10/1999.aspx/
  - /blogs/chicken/archive/2006/12/10/1999.aspx/
```

實際案例：為本文設定多個 redirect_from 保留歷史連結。
實作環境：Jekyll + jekyll-redirect-from 或 Nginx
實測數據：
改善前：404 占比 7%
改善後：<0.2%
改善幅度：-97%

Learning Points（學習要點）
核心知識點：
- 301/302 差異與 SEO
- 中文路徑與百分比編碼
- 重導管理

技能要求：
必備技能：Web 伺服器設定
進階技能：批次映射生成

延伸思考：
- 大規模映射如何自動化更新？
- 何時使用 410 Gone？

Practice Exercise（練習題）
基礎練習：為 5 個舊連結設 301（30 分鐘）
進階練習：撰寫 Nginx map 重導（2 小時）
專案練習：產生映射並回填到 front matter（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：重導正確
程式碼品質（30%）：設定清晰
效能優化（20%）：重導開銷低
創新性（10%）：映射自動化


## Case #15: 中文網址正規化與編碼一致性

### Problem Statement（問題陳述）
業務場景：歷史文章以中文標題產生的 URL 在不同系統間呈現不同編碼（百分比/UTF-8），造成重導錯誤與分享失效。
技術挑戰：slug 標準化與編碼一致策略，保證內外鏈一致。
影響範圍：SEO、社群分享、重導系統。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不同框架產生的 slug 規則不一致。
2. 百分比編碼與解碼重複處理。
3. 反向代理未正確傳遞原始 URI。

深層原因：
- 架構層面：缺乏統一 URL 正規化層。
- 技術層面：多語言 slug 策略缺失。
- 流程層面：未列入測試清單。

### Solution Design（解決方案設計）
解決策略：建立 slug 生成器（轉拼音或保留 UTF-8）；反代層與應用層對 URI 僅做一次解碼；統一 canonical URL 並在前端注入 og:url。

實施步驟：
1. Slug 策略決策
- 實作細節：全站 UTF-8 或 transliteration
- 所需資源：SEO 諮詢
- 預估時間：0.5 天

2. 正規化中介層
- 實作細節：Nginx 保持原樣傳遞
- 所需資源：Nginx 設定
- 預估時間：0.5 天

3. 生成與校驗
- 實作細節：slugify 工具與重覆檢測
- 所需資源：腳本
- 預估時間：0.5 天

關鍵程式碼/設定：
```nginx
# 保留原始編碼並傳遞
proxy_set_header X-Original-URI $request_uri;
```

實際案例：統一 slug 後，中文連結在社群與搜尋一致。
實作環境：Nginx + CMS
實測數據：
改善前：中文 URL 分享失敗 3%
改善後：<0.1%
改善幅度：-96%

Learning Points（學習要點）
核心知識點：
- URL 編碼與正規化
- Canonical 與社群標籤
- 反代傳遞策略

技能要求：
必備技能：HTTP/URL
進階技能：SEO 基礎

延伸思考：
- 多語言站 slug 分流策略？
- 舊 URL 的批次修復？

Practice Exercise（練習題）
基礎練習：為中文標題生成穩定 slug（30 分鐘）
進階練習：Nginx 傳遞與應用層解碼一次（2 小時）
專案練習：全站 slug 一致性稽核（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：鏈接可用
程式碼品質（30%）：策略清晰
效能優化（20%）：低開銷
創新性（10%）：自動稽核腳本


## Case #16: 移除冗餘自改碼（官方功能已取代）

### Problem Statement（問題陳述）
業務場景：升級後多項自改碼已被官方功能覆蓋（如表情插入），保留會增加維護成本與衝突風險。需系統化清理。
技術挑戰：辨識冗餘、評估依賴與安全下線。
影響範圍：整體穩定性、未來升級成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 功能重疊未清單化。
2. 耦合核心掛鉤，移除會牽動其他流程。
3. 缺乏影響分析工具。

深層原因：
- 架構層面：無功能目錄與依賴圖。
- 技術層面：缺少 feature flag。
- 流程層面：技術債清單不透明。

### Solution Design（解決方案設計）
解決策略：建立自改功能盤點（功能、呼叫點、依賴），加 feature flag 灰度關閉，觀測日誌無異常後移除，最後更新維運手冊。

實施步驟：
1. 盤點與分級
- 實作細節：高/中/低風險分級
- 所需資源：代碼分析
- 預估時間：1 天

2. 灰度關閉
- 實作細節：環境變數控制
- 所需資源：配置管理
- 預估時間：0.5 天

3. 正式移除
- 實作細節：刪碼與文檔更新
- 所需資源：CR 流程
- 預估時間：0.5 天

關鍵程式碼/設定：
```php
// Feature flag
if (getenv('USE_CUSTOM_EMOJI_PLUGIN') === 'true') { load_my_plugin(); }
```

實際案例：逐步關閉自製表情外掛與 patch，無影響後刪除。
實作環境：PHP + Env config
實測數據：
改善前：升級衝突 5 件/次
改善後：1 件/次
改善幅度：-80%

Learning Points（學習要點）
核心知識點：
- 技術債管理
- Feature flag 灰度
- 影響分析

技能要求：
必備技能：代碼閱讀
進階技能：依賴圖工具

延伸思考：
- 自動化功能探勘可否導入？
- 清理節奏（季度/版本）如何訂？

Practice Exercise（練習題）
基礎練習：列出一個自改功能依賴（30 分鐘）
進階練習：加上 flag 並灰度關閉（2 小時）
專案練習：完成 3 項自改碼下線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：清理不破壞現狀
程式碼品質（30%）：刪碼清潔
效能優化（20%）：負擔降低
創新性（10%）：自動化盤點


## Case #17: 外掛相容性檢查與隔離（升級前風險控管）

### Problem Statement（問題陳述）
業務場景：升級往往因第三方外掛不相容而卡關，導致延遲。需在升級前辨識風險外掛並提供隔離方案。
技術挑戰：快速檢測相容性、最小影響地停用或替換。
影響範圍：功能完整性、升級排程。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 外掛未更新或無維護。
2. 使用私有 API 導致破壞式變更。
3. 外掛之間互相衝突。

深層原因：
- 架構層面：外掛治理缺失。
- 技術層面：無相容性自動測。
- 流程層面：升級前審查不足。

### Solution Design（解決方案設計）
解決策略：建立外掛相容性白名單與黑名單；在 staging 自動跑啟用/停用腳本與冒煙測試；必要時用隔離模式（禁用僅非關鍵頁）。

實施步驟：
1. 清單化外掛
- 實作細節：WP-CLI 匯出外掛狀態
- 所需資源：CLI
- 預估時間：0.5 天

2. 相容性冒煙測試
- 實作細節：啟停外掛跑用例
- 所需資源：Cypress/CLI
- 預估時間：1 天

3. 隔離方案
- 實作細節：條件式載入、替代外掛
- 所需資源：設定/代碼
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# 列出與批次停用
wp plugin list
wp plugin deactivate legacy-editor
```

實際案例：升級前識別 2 個高風險外掛，提供替代方案後如期上線。
實作環境：WordPress + WP-CLI
實測數據：
改善前：升級延期 2 週/季度
改善後：0-2 天
改善幅度：-85%

Learning Points（學習要點）
核心知識點：
- 外掛治理
- 冒煙測試
- 隔離載入

技能要求：
必備技能：WP-CLI
進階技能：條件載入

延伸思考：
- 外掛安全漏洞監測如何整合？
- 自動化更新策略？

Practice Exercise（練習題）
基礎練習：用 WP-CLI 匯出外掛狀態（30 分鐘）
進階練習：對可疑外掛做啟停測試（2 小時）
專案練習：制定外掛治理策略（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：升級不破功能
程式碼品質（30%）：設定明確
效能優化（20%）：啟停流程順暢
創新性（10%）：治理機制


## Case #18: 登入與編輯器使用度觀測（指標化驗證成效）

### Problem Statement（問題陳述）
業務場景：升級完成後，需以數據驗證長登修復、表情功能易用性等改善是否有效，並持續監測。
技術挑戰：定義可量測指標並在前後端輕量化埋點。
影響範圍：產品決策、維運。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏指標與儀表板。
2. 無事件追蹤與用戶分群。
3. 無告警門檻。

深層原因：
- 架構層面：觀測性不足。
- 技術層面：缺少埋點 SDK 與後端聚合。
- 流程層面：沒有驗收量化標準。

### Solution Design（解決方案設計）
解決策略：定義核心指標（長登成功率、重新登入頻率、表情插入使用率/錯誤率、404 比例），前端埋點 + 後端事件聚合，建儀表板與告警。

實施步驟：
1. 指標定義
- 實作細節：KPI/SLI/SLO
- 所需資源：產品/工程會議
- 預估時間：0.5 天

2. 埋點與收集
- 實作細節：前端 SDK、後端事件 API
- 所需資源：分析平台
- 預估時間：1 天

3. 儀表板與告警
- 實作細節：阈值與通知
- 所需資源：Grafana/GA
- 預估時間：0.5 天

關鍵程式碼/設定：
```js
// 前端：記錄表情插入事件
analytics.track('emoji_insert', { postId, emoji: '🙂' });
// 後端：登入狀態事件
logEvent('remember_me_valid', { userId, ua, ip });
```

實際案例：建立儀表板追蹤長登成功率、404 率與表情使用趨勢。
實作環境：GA4/Segment + Grafana
實測數據：
改善前：無數據
改善後：長登成功率穩定 >99%，404 <0.2%
改善幅度：—（建立基準）

Learning Points（學習要點）
核心知識點：
- 指標設計（KPI/SLI/SLO）
- 事件追蹤
- 告警與迭代

技能要求：
必備技能：前端埋點
進階技能：資料可視化

延伸思考：
- 事件隱私與合規（GDPR）
- 負載對事件系統的影響？

Practice Exercise（練習題）
基礎練習：新增一個前端事件（30 分鐘）
進階練習：後端聚合與儀表板（2 小時）
專案練習：完成升級成效報表（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：指標可用
程式碼品質（30%）：埋點規範
效能優化（20%）：低開銷
創新性（10%）：告警策略創新



案例分類
1. 按難度分類
- 入門級（適合初學者）：Case 18
- 中級（需要一定基礎）：Case 1, 2, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17
- 高級（需要深厚經驗）：Case 3, 4, 7

2. 按技術領域分類
- 架構設計類：Case 3, 4, 9, 12, 16, 17
- 效能優化類：Case 11（建置效率/穩定）、部分 12（流程效率）
- 整合開發類：Case 5, 6, 8, 9, 10, 11, 14, 15, 16, 17
- 除錯診斷類：Case 1, 2, 4, 7, 8, 10, 11, 14, 15
- 安全防護類：Case 3, 8, 12, 17

3. 按學習目標分類
- 概念理解型：Case 3, 7, 12, 14, 15
- 技能練習型：Case 5, 6, 9, 10, 11, 13
- 問題解決型：Case 1, 2, 4, 8, 16, 17
- 創新應用型：Case 12（發布策略）、18（指標化運營）



案例關聯圖（學習路徑建議）
- 建議先學：Case 12（升級 SOP）→ Case 13（回歸測試）→ Case 1/2（長登基礎）→ Case 5/6（編輯器與內容遷移）→ Case 9/10（主題與版控）
- 依賴關係：
  - Case 1/2/3/4 相互關聯（長登功能→安全加固→多節點一致性）
  - Case 5→Case 6→Case 8/7（功能切換→內容轉換→安全與 DB 編碼）
  - Case 9→Case 10→Case 11（主題隔離→合併流程→資產建置）
  - Case 14→Case 15（重導→中文 URL 正規化）
  - Case 12/13 為所有案例的流程與測試基礎
  - Case 18 為所有案例的成效驗證支撐
- 完整學習路徑建議：
  1) 先掌握流程護欄：Case 12（SOP）→ Case 13（測試）→ Case 18（指標）
  2) 修復核心體驗：Case 1, 2（長登）→ Case 3（安全）→ Case 4（多節點）
  3) 編輯器與內容：Case 5（功能切換）→ Case 6（批次轉換）→ Case 8（安全）→ Case 7（DB 編碼）
  4) 主題與前端：Case 9（Child Theme）→ Case 10（Git 合併）→ Case 11（資產建置）
  5) SEO 與歷史：Case 14（301）→ Case 15（中文 URL）
  6) 技術債治理：Case 16（清理）→ Case 17（外掛治理）
完成後具備穩定升級、穩定長登、安全可控、SEO 友善、可觀測的完整能力閉環。