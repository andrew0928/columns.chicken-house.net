以下內容基於原文的具體情境（使用 CodeFormatter 於部落格平台、以 Community Server 為例、希望提供「copy code」並在預覽避免安全警告），萃取並拆解為可教學、可實作、可評測的 15 個結構化案例。每個案例都包含問題、根因、解法、程式碼與練習／評估。

## Case #1: 啟用 CodeFormatter 的語法高亮（注入基礎 CSS）

### Problem Statement（問題陳述）
業務場景：在部落格文章中展示 C# 程式碼，作者採用一個輸出乾淨 HTML 的 CodeFormatter 函式庫，期望在網站前台顯示具備關鍵字上色、字型與行距等一致的閱讀體驗。因為該函式庫將樣式抽離至 CSS，若部落格主題未事先載入對應 CSS，前台顯示將失去語法高亮與可讀性。
技術挑戰：如何將 CodeFormatter 所需 CSS 快速、安全且全站一致地注入既有部落格平台（例：Community Server），又不破壞既有版型。
影響範圍：所有文章中的程式碼區塊顯示；讀者閱讀體驗；文章維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. CodeFormatter 產生的 HTML 不含內嵌樣式，僅以 class 命名控制外觀。
2. 部落格主題尚未包含 CodeFormatter 專用 CSS。
3. 若不加 CSS，語法色彩、行距、字型、行號等都無法呈現。
深層原因：
- 架構層面：樣式與內容分離的設計需要平台載入外部 CSS。
- 技術層面：現有主題未定義 .csharpcode 等類別的樣式。
- 流程層面：缺少對於第三方函式庫樣式導入的標準流程。

### Solution Design（解決方案設計）
解決策略：在不改動主題原始檔的前提下，利用 Community Server Dashboard 的「Custom Styles (Advanced)」集中注入 CodeFormatter 官方 CSS，確保全站文章統一呈現。此法快速、低風險、可回滾。

實施步驟：
1. 匯入官方 CSS
- 實作細節：複製下方 CSS 到 CS 的 Custom Styles (Advanced) 區塊
- 所需資源：Community Server 後台權限
- 預估時間：10 分鐘
2. 驗證前台呈現
- 實作細節：在測試文章中貼上示範程式碼，確認字型、色彩
- 所需資源：前台瀏覽器
- 預估時間：10 分鐘

關鍵程式碼/設定：
```css
.csharpcode, .csharpcode pre {
  font-size: small;
  color: black;
  font-family: Consolas, "Courier New", Courier, Monospace;
  background-color: #ffffff;
  /*white-space: pre;*/
}
.csharpcode pre { margin: 0em; }
.csharpcode .rem { color: #008000; }
.csharpcode .kwrd { color: #0000ff; }
.csharpcode .str { color: #006080; }
.csharpcode .op { color: #0000c0; }
.csharpcode .preproc { color: #cc6633; }
.csharpcode .asp { background-color: #ffff00; }
.csharpcode .html { color: #800000; }
.csharpcode .attr { color: #ff0000; }
.csharpcode .alt { background-color: #f4f4f4; width: 100%; margin: 0em; }
.csharpcode .lnum { color: #606060; }
```

實際案例：作者於 Community Server 的 Dashboard > 修改版面 > Custom Styles (Advanced) 直接貼上 CSS 後即生效。
實作環境：Community Server、CodeFormatter 函式庫、Windows Live Writer 投稿流程。
實測數據：
- 改善前：程式碼區塊無語法色彩、字型不一致。
- 改善後：語法高亮、字型一致、行號/備註顏色可辨。
- 改善幅度：可讀性顯著提升（質化指標）。

Learning Points（學習要點）
核心知識點：
- 內容與樣式分離的優點與落地方式
- 在不改主題檔的前提注入全站 CSS
- CodeFormatter 的 class 命名對應

技能要求：
- 必備技能：基本 CSS、網站後台操作
- 進階技能：樣式衝突排查

延伸思考：
- 此法亦可導入其他語法高亮方案的 CSS。
- 風險：與主題既有 CSS 名稱衝突。
- 優化：使用命名空間或更精準選擇器避免覆蓋。

Practice Exercise（練習題）
- 基礎練習：把上述 CSS 注入測試站並顯示一段 C# 程式碼（30 分鐘）
- 進階練習：調整配色與字型大小以符合自家主題（2 小時）
- 專案練習：建立多語言（C#, JS, HTML）語法高亮整合方案（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：語法色彩、字型、背景呈現正確
- 程式碼品質（30%）：選擇器精準、避免污染其他元素
- 效能優化（20%）：CSS 載入體積與快取策略
- 創新性（10%）：主題化、可切換樣式主題


## Case #2: 不改主題檔的快速介接（Community Server 的 Custom Styles）

### Problem Statement（問題陳述）
業務場景：多作者共用的部落格平台，沒有權限修改主題檔，但需要快速導入 CodeFormatter；管理者希望在不觸碰模板與部署流程的情況下完成整合並可隨時回滾。
技術挑戰：如何在 CS 平台不動程式、不重佈主題，即時讓全站程式碼區塊生效。
影響範圍：部署效率、風險可控性、與其他團隊的協作流程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 主題檔修改需要部署與審核流程，成本高。
2. 共用平台不一定提供檔案層級修改權限。
3. 需要全站套用，單篇手動嵌入不可行。
深層原因：
- 架構層面：平台提供樣式注入入口（Custom Styles）。
- 技術層面：CSS 能全域套用樣式，無需改 HTML。
- 流程層面：運維權限與審批流程限制。

### Solution Design（解決方案設計）
解決策略：使用「Custom Styles (Advanced)」作為全站樣式注入點，集中管理 CodeFormatter CSS；建立簡易 SOP（貼上、預覽、回滾）降低風險。

實施步驟：
1. 設置注入點
- 實作細節：文件化後台路徑，設定變更紀錄
- 所需資源：後台管理帳號
- 預估時間：10 分鐘
2. 驗證與回滾指引
- 實作細節：建立“套用/回退”雙向流程與影響清單
- 所需資源：測試帳號與文章
- 預估時間：30 分鐘

關鍵程式碼/設定：
```text
Community Server > Dashboard > 修改版面 > Custom Styles (Advanced)
貼入 Case #1 的 CSS 內容；保存後刷新前台檢視結果
```

實際案例：作者以此方式一次性完成全站導入。
實作環境：Community Server 多作者平台。
實測數據：
- 改善前：需改主題檔、風險大。
- 改善後：後台貼入即生效、可快速回滾。
- 改善幅度：導入時間由數小時降至數十分鐘（質化）。

Learning Points（學習要點）
核心知識點：
- 後台樣式注入的最佳實務
- 快速回滾與變更管理
- 與主題樣式衝突的檢核

技能要求：
- 必備技能：後台操作、基礎 CSS
- 進階技能：變更管理、影響分析

延伸思考：
- 可否建立多套樣式並以設定切換？
- 權限不足時的溝通與審批策略？
- 自動化導入（腳本化）可能性？

Practice Exercise（練習題）
- 基礎練習：在測試站用 Custom Styles 注入並回滾（30 分鐘）
- 進階練習：評估與現有主題的衝突並修正（2 小時）
- 專案練習：撰寫導入與回滾 SOP 文檔並演練（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：全站程式碼區塊都生效
- 程式碼品質（30%）：樣式隔離與命名
- 效能優化（20%）：避免重複與冗餘
- 創新性（10%）：導入與回滾自動化構想


## Case #3: 社群平台封鎖 <script>，導致「Copy Code」無法內嵌

### Problem Statement（問題陳述）
業務場景：文章希望提供「copy code」按鈕，一鍵將程式碼複製到剪貼簿；但平台（CS）會封鎖 <script>，無法在文章 HTML 內直接寫入 JavaScript，導致功能落空。
技術挑戰：如何在不修改平台安全策略（不動 communityserver.config）的情況下，仍讓頁面具備複製功能。
影響範圍：讀者體驗、功能可用性、安全合規。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. CS 過濾器預設封鎖 <script>，避免 XSS。
2. 文章內容內嵌腳本被移除，copy 功能失效。
3. 平台安全策略不易更動或需高權限。
深層原因：
- 架構層面：文章內容與腳本執行隔離。
- 技術層面：功能依賴事件處理程式無法注入。
- 流程層面：不允許每篇文章攜帶腳本。

### Solution Design（解決方案設計）
解決策略：改採 IE 專屬 HTC（HTML Component）與 CSS behavior:url 機制，用 CSS 附掛行為到 DOM 元素，繞開在文章內嵌 <script> 的限制，保留平台安全策略。

實施步驟：
1. 定義 copycode 樣式並掛上行為
- 實作細節：在全站 CSS 新增 .copycode，指向 HTC
- 所需資源：CSS 注入權限、HTC 檔
- 預估時間：20 分鐘
2. 佈署 HTC 檔案
- 實作細節：將 code.htc 放在 /themes/code.htc
- 所需資源：檔案上傳權限
- 預估時間：10 分鐘

關鍵程式碼/設定：
```css
/* 於全站 CSS（Custom Styles）加入 */
.copycode {
  cursor: hand;
  color: #c0c0ff;
  display: none;               /* 非 IE 或 HTC 未載入時隱藏 */
  behavior: url('/themes/code.htc'); /* 由 HTC 注入事件與顯示 */
}
```

實際案例：作者以 HTC 成功實作 copy 功能，且不需調整平台封鎖規則。
實作環境：Community Server、IE（HTC 僅 IE 支援）。
實測數據：
- 改善前：copy 按鈕無法工作（<script> 被移除）。
- 改善後：IE 上可一鍵複製。
- 改善幅度：功能可用性從 0 提升至可在 IE 正常運作（質化）。

Learning Points（學習要點）
核心知識點：
- 以 CSS behavior:url 附掛互動行為
- 內容安全策略下的替代技術
- 平台限制導致的前端策略調整

技能要求：
- 必備技能：CSS、基本 DOM 結構理解
- 進階技能：舊式 IE 技術（HTC）整合能力

延伸思考：
- 非 IE 瀏覽器如何優雅降級？
- 若平台允許外掛腳本，是否能以更通用的方式實作？
- 長期維護上，是否需汰換 HTC？

Practice Exercise（練習題）
- 基礎練習：加入 .copycode 與 HTC 指向（30 分鐘）
- 進階練習：讓同一 HTC 支援不同程式碼區塊（2 小時）
- 專案練習：在不改安全策略下設計一組互動工具列（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：IE 上 copy 可用
- 程式碼品質（30%）：清晰結構與注解
- 效能優化（20%）：行為掛載輕量
- 創新性（10%）：平台限制下的替代設計


## Case #4: 用 CSS behavior:url 掛載 HTC（無腳本內嵌仍可互動）

### Problem Statement（問題陳述）
業務場景：希望透過 CSS 直接讓「copy code」元素自帶互動行為，避免在文章注入 <script>；目標是在讀者端載入頁面時自動具備複製功能。
技術挑戰：如何用純 CSS 宣告行為並讓目標元素成為互動按鈕。
影響範圍：樣式與互動的關聯設計、跨瀏覽器支援。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不可在文章內寫 <script>。
2. 需要一種「樣式即行為」的替代途徑。
3. IE 支援 behavior:url 導入 HTC。
深層原因：
- 架構層面：分離內容、樣式、行為，但受平台限制。
- 技術層面：依賴 IE 專屬特性。
- 流程層面：以 CSS 通道發佈互動效果。

### Solution Design（解決方案設計）
解決策略：使用 .copycode class 統一賦予互動，將 HTC 行為封裝成可重用元件；讓樣式與行為緊密綁定，簡化作者端標記工作。

實施步驟：
1. 套用 class 到按鈕元素
- 實作細節：在程式碼區塊標題右側放置 [copy code] 並加上 class="copycode"
- 所需資源：文章編輯工具或外掛自動產生
- 預估時間：10 分鐘
2. 測試行為載入
- 實作細節：IE 測試是否自動顯示且可點擊
- 所需資源：IE 瀏覽器
- 預估時間：10 分鐘

關鍵程式碼/設定：
```html
<div class="csharpcode">
  <div class="toolbar">
    <span class="copycode">copy code</span>
  </div>
  <pre>// your code here</pre>
</div>
```

實際案例：作者在產生 HTML 時勾選選項，讓輸出包含原始碼與 [copy code] 鈕。
實作環境：Windows Live Writer 外掛輸出、Community Server 前台。
實測數據：
- 改善前：只有靜態文字。
- 改善後：[copy code] 自動具備點擊與複製行為。
- 改善幅度：互動性從無到有（質化）。

Learning Points（學習要點）
核心知識點：
- CSS 與行為的關聯（behavior:url）
- 封裝與重用的設計思維
- 前端降級策略規劃

技能要求：
- 必備技能：HTML 結構設計
- 進階技能：可用性與可達性考量

延伸思考：
- 非 IE 如何提供替代方案（例如顯示提示文字）？
- 是否需要提供鍵盤操作支援？

Practice Exercise（練習題）
- 基礎練習：為現有文章加入 [copy code] 並測試（30 分鐘）
- 進階練習：將 [copy code] 封裝為可重用的 HTML 片段（2 小時）
- 專案練習：定義 toolbar 元件（複製、展開、列號切換）（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：按鈕自動可用
- 程式碼品質（30%）：語意化、結構清晰
- 效能優化（20%）：最小化標記與資源
- 創新性（10%）：元件化設計


## Case #5: 只複製「純文字」程式碼，避免貼上帶格式

### Problem Statement（問題陳述）
業務場景：讀者常將文章中的程式碼複製到 IDE；若複製的是帶 HTML 樣式的內容，貼到 IDE 會混入標籤或不可見字元，導致編譯錯誤或需手動清理。
技術挑戰：如何保證複製的是純文字而非 innerHTML。
影響範圍：讀者貼上成功率、支援成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 預設複製 innerHTML 會帶入標籤。
2. 行號或裝飾可能被一併複製。
3. 不同瀏覽器對 textContent/innerText 支援差異。
深層原因：
- 架構層面：展示結構與原始碼文本共存。
- 技術層面：需選對節點並擷取純文字。
- 流程層面：外掛輸出需包含可取用的原始碼節點。

### Solution Design（解決方案設計）
解決策略：在 HTC 中尋找對應的 <pre> 或原始碼節點，使用 innerText 或 textContent 擷取純文字，透過 window.clipboardData 設定剪貼簿，確保貼上可直接編譯。

實施步驟：
1. 尋找對應程式碼節點
- 實作細節：從 copy 按鈕往上/下尋找第一個 <pre>
- 所需資源：HTC 事件處理
- 預估時間：30 分鐘
2. 複製純文字
- 實作細節：使用 innerText/textContent 取文本
- 所需資源：IE 剪貼簿 API
- 預估時間：20 分鐘

關鍵程式碼/設定：
```html
<!-- HTML 結構 -->
<div class="csharpcode">
  <div class="toolbar"><span class="copycode">copy code</span></div>
  <pre>
// C# code...
  </pre>
</div>
```

```html
<!-- /themes/code.htc -->
<PUBLIC:COMPONENT>
  <PUBLIC:ATTACH EVENT="onclick" ONEVENT="doCopy()" />
  <PUBLIC:ATTACH EVENT="oncontentready" ONEVENT="onReady()" />
  <SCRIPT LANGUAGE="JScript">
    function onReady() {
      // HTC 載入後才顯示 copy 按鈕（非 IE 仍為 display:none）
      element.style.display = 'inline';
    }
    function findPre(el) {
      var p = el.parentNode;
      while (p && p.tagName && p.tagName.toLowerCase() !== 'div') p = p.parentNode;
      if (p) {
        var pres = p.getElementsByTagName('pre');
        if (pres && pres.length) return pres[0];
      }
      return null;
    }
    function doCopy() {
      var pre = findPre(element);
      if (!pre) return;
      var text = pre.innerText || pre.textContent || '';
      if (window.clipboardData) {
        window.clipboardData.setData('Text', text);
        element.innerText = 'copied!';
        window.setTimeout(function(){ element.innerText = 'copy code'; }, 1500);
      }
    }
  </SCRIPT>
</PUBLIC:COMPONENT>
```

實際案例：作者強調按下後可直接貼用，避免格式干擾。
實作環境：IE、HTC、Community Server。
實測數據：
- 改善前：貼上常含樣式或雜訊。
- 改善後：貼上為純文字，可直接編譯。
- 改善幅度：貼上修正工時降為 0（質化）。

Learning Points（學習要點）
核心知識點：
- innerText vs textContent
- 剪貼簿 API（IE）
- 結構化標記查找策略

技能要求：
- 必備技能：DOM 操作
- 進階技能：跨瀏覽器文本擷取策略

延伸思考：
- 非 IE 如何實作純文字複製（execCommand('copy') 或 Clipboard API）？
- 是否要排除行號節點？

Practice Exercise（練習題）
- 基礎練習：修改 HTC 只複製 <pre> 文本（30 分鐘）
- 進階練習：支援排除行號或裝飾（2 小時）
- 專案練習：改寫為現代瀏覽器 Clipboard API 版本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：複製純文字成功率
- 程式碼品質（30%）：節點選取正確、邏輯清晰
- 效能優化（20%）：最少 DOM 查找
- 創新性（10%）：現代 API 兼容設計


## Case #6: 非 IE 瀏覽器的優雅降級（隱藏 copy code）

### Problem Statement（問題陳述）
業務場景：網站有多種瀏覽器使用者，但 HTC 僅支援 IE。為避免在非 IE 顯示無效按鈕，須提供優雅降級策略，確保介面一致性與不誤導使用者。
技術挑戰：判斷平台支援並動態控制 UI 呈現。
影響範圍：跨瀏覽器一致性、使用者信任。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. HTC 僅 IE 支援。
2. 非 IE 顯示按鈕會造成期待落差。
3. 平台安全限制無法改變。
深層原因：
- 架構層面：技術選型的兼容性邊界。
- 技術層面：以 CSS 控制呈現狀態。
- 流程層面：預期管理與文件化。

### Solution Design（解決方案設計）
解決策略：預設以 CSS 將 .copycode 設為 display:none，僅在 IE 成功載入 HTC 後於 oncontentready 顯示；非 IE 使用者不看到無效按鈕。

實施步驟：
1. 設定預設隱藏
- 實作細節：.copycode { display:none }
- 所需資源：CSS
- 預估時間：5 分鐘
2. HTC 啟用後顯示
- 實作細節：onReady 中 element.style.display='inline'
- 所需資源：HTC
- 預估時間：10 分鐘

關鍵程式碼/設定：
```css
.copycode { display: none; behavior: url('/themes/code.htc'); }
```

實際案例：原文 CSS 即採此策略。
實作環境：IE/非 IE 混用環境。
實測數據：
- 改善前：非 IE 顯示但不可用。
- 改善後：非 IE 隱藏，不誤導。
- 改善幅度：錯誤操作率趨近 0（質化）。

Learning Points（學習要點）
核心知識點：
- Progressive enhancement
- 可用性與預期管理
- CSS 控制互動可見性

技能要求：
- 必備技能：CSS 顯示控制
- 進階技能：跨瀏覽器 UX 規劃

延伸思考：
- 是否提供工具提示：「請用 IE 以啟用一鍵複製」？
- 是否加上替代快捷鍵（例如點擊自動全選）？

Practice Exercise（練習題）
- 基礎練習：在非 IE 隱藏按鈕（30 分鐘）
- 進階練習：非 IE 顯示提示文字或手動複製指引（2 小時）
- 專案練習：替代方案設計與 A/B 測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確隱藏/顯示
- 程式碼品質（30%）：簡潔、可維護
- 效能優化（20%）：無多餘偵測
- 創新性（10%）：友善提示設計


## Case #7: HTC 檔案部署與路徑對應（避免 404 與行為失效）

### Problem Statement（問題陳述）
業務場景：已在 CSS 設定 behavior:url('/themes/code.htc')，但 copy 功能仍未生效；疑似檔案路徑或部署位置錯誤導致 HTC 未載入。
技術挑戰：找出資源路徑、大小寫、部署位置等問題，確保行為檔被正確存取。
影響範圍：功能可用性、錯誤排查時間。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. HTC 檔未放置至 /themes/code.htc。
2. 行為路徑寫相對，導致子路徑解析錯誤。
3. 伺服器未正確回應資源（權限/遺失）。
深層原因：
- 架構層面：前端資源依賴的部署策略。
- 技術層面：URL 解析與大小寫敏感。
- 流程層面：缺少靜態資源部署清單。

### Solution Design（解決方案設計）
解決策略：採用站台根目錄的絕對路徑；建立部署清單與監控（404 日誌），驗證資源可取用；統一命名與大小寫。

實施步驟：
1. 放置與驗證
- 實作細節：將 code.htc 放在 /themes/ 下，使用瀏覽器直接請求測試
- 所需資源：FTP/檔案管理器、伺服器存取
- 預估時間：20 分鐘
2. 路徑穩定化
- 實作細節：CSS 使用絕對路徑 behavior:url('/themes/code.htc')
- 所需資源：CSS 編輯權限
- 預估時間：10 分鐘

關鍵程式碼/設定：
```css
.copycode { behavior: url('/themes/code.htc'); } /* 使用站台絕對路徑 */
```

實際案例：原文明確指出放置於 /Themes/Code.HTC（不分大小寫視伺服器而定）。
實作環境：Community Server、IIS。
實測數據：
- 改善前：copy 無反應（HTC 未載入）。
- 改善後：copy 正常。
- 改善幅度：功能可用性由 0 至可用（質化）。

Learning Points（學習要點）
核心知識點：
- 靜態資源部署與路徑策略
- 404 排查
- 大小寫敏感與平台差異

技能要求：
- 必備技能：Web 伺服器基本操作
- 進階技能：資源監控與日誌分析

延伸思考：
- 是否需設定正確 MIME（視伺服器）？
- 多環境部署（測試/正式）路徑統一策略？

Practice Exercise（練習題）
- 基礎練習：上傳 HTC 並驗證可存取（30 分鐘）
- 進階練習：導入 404 監控與告警（2 小時）
- 專案練習：建立前端資源佈署清單與檢查腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：HTC 成功載入
- 程式碼品質（30%）：路徑設定規範
- 效能優化（20%）：避免多次重試與錯誤請求
- 創新性（10%）：自動檢查工具


## Case #8: 預覽觸發 IE 安全警告，改用 HTA（HTML Application）

### Problem Statement（問題陳述）
業務場景：作者在本機預覽文章時，如果用 IE 直接開 HTML 會彈出多個安全警告，影響預覽效率與體驗。
技術挑戰：如何在 Windows/IE 生態下，提供低摩擦、無擾動（無警告）的預覽方案。
影響範圍：撰稿效率、開發體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 以本機檔案方式在 IE 開啟 HTML 觸發安全區域警告。
2. 需要存取剪貼簿等提升權限動作時更易警告。
3. 每次預覽都會重複干擾。
深層原因：
- 架構層面：IE 安全分區機制。
- 技術層面：本機檔存取權限不足。
- 流程層面：預覽流程未針對安全機制做優化。

### Solution Design（解決方案設計）
解決策略：將預覽改為 HTA（HTML Application），以受信任的應用程式宿主執行 HTML UI，避免安全彈窗與限制，專注於內容驗證。

實施步驟：
1. 建立 HTA 宿主
- 實作細節：撰寫 .hta 檔，設定視窗屬性
- 所需資源：Windows/IE 環境
- 預估時間：30 分鐘
2. 嵌入預覽內容
- 實作細節：以 iframe 或動態載入預覽 HTML
- 所需資源：HTA 腳本
- 預估時間：40 分鐘

關鍵程式碼/設定：
```html
<!-- preview.hta -->
<html>
<head>
<title>Post Preview</title>
<HTA:APPLICATION ID="PostPreview" SCROLL="yes" SINGLEINSTANCE="yes" SYSMENU="yes" />
<style>body { font-family: Segoe UI, Arial; }</style>
</head>
<body>
  <iframe id="preview" src="preview.html" width="100%" height="100%" frameborder="0"></iframe>
</body>
</html>
```

實際案例：作者改用 HTA 實作預覽以消除安全警告。
實作環境：Windows、IE、HTA。
實測數據：
- 改善前：每次預覽出現安全警告。
- 改善後：無安全警告，預覽順暢。
- 改善幅度：警告彈窗由多次/次降為 0（量化為次數）。

Learning Points（學習要點）
核心知識點：
- IE 安全分區與 HTA
- 本機預覽體驗優化
- 預覽宿主與內容分離

技能要求：
- 必備技能：HTML、基本 Windows 知識
- 進階技能：HTA 屬性配置

延伸思考：
- 現代環境可用本機伺服器或 Electron 等替代？
- 預覽是否需要與正式環境一致的資源載入？

Practice Exercise（練習題）
- 基礎練習：建立能載入靜態 HTML 的 HTA（30 分鐘）
- 進階練習：在 HTA 中注入自訂樣式切換（2 小時）
- 專案練習：打造完整貼文預覽工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：無警告、可預覽
- 程式碼品質（30%）：結構清晰
- 效能優化（20%）：載入迅速
- 創新性（10%）：預覽工具化設計


## Case #9: 預覽環境關閉「Copy Code」功能（避免干擾）

### Problem Statement（問題陳述）
業務場景：在預覽模式下不需要或不適合啟用 copy 功能（與本機安全策略互動、非正式內容），避免造成誤用或誤判。
技術挑戰：如何讓外掛在預覽輸出時不包含 copy 按鈕，正式發佈才包含。
影響範圍：內容審閱效率、誤用風險。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預覽與正式環境差異較大。
2. 本機安全限制會影響 copy 功能。
3. 開發者不希望預覽混入與審閱無關 UI。
深層原因：
- 架構層面：功能旗標控制。
- 技術層面：輸出管線可識別預覽模式。
- 流程層面：審閱流程聚焦內容。

### Solution Design（解決方案設計）
解決策略：在外掛產生 HTML 時根據模式開關按鈕；預覽不輸出 copy 元素，正式發佈才導入。

實施步驟：
1. 模式判定
- 實作細節：以參數或環境變數區分 preview/publish
- 所需資源：外掛設定
- 預估時間：20 分鐘
2. 條件式輸出
- 實作細節：preview 時不產生 span.copycode
- 所需資源：外掛模板
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
// 偽代碼：Live Writer 外掛輸出
bool isPreview = context.Mode == RenderMode.Preview;
if (!isPreview) {
  writer.Write("<span class=\"copycode\">copy code</span>");
}
```

實際案例：原文指出預覽時不加此功能。
實作環境：Windows Live Writer 外掛。
實測數據：
- 改善前：預覽混入多餘 UI。
- 改善後：預覽專注內容。
- 改善幅度：審閱干擾降為 0（質化）。

Learning Points（學習要點）
核心知識點：
- 功能旗標與模式切換
- 預覽與正式的責任分離
- 產出內容一致性控制

技能要求：
- 必備技能：外掛模板控制
- 進階技能：條件式渲染設計

延伸思考：
- 是否提供預覽模式可選啟用開關？
- A/B 審閱需要的輕量互動？

Practice Exercise（練習題）
- 基礎練習：為輸出加上模式判斷（30 分鐘）
- 進階練習：提供 UI 切換（2 小時）
- 專案練習：建立多旗標（行號、展開、複製）控制（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：模式行為正確
- 程式碼品質（30%）：邏輯清晰
- 效能優化（20%）：無多餘輸出
- 創新性（10%）：旗標設計


## Case #10: 不修改平台安全配置的取捨（不改 communityserver.config）

### Problem Statement（問題陳述）
業務場景：開發者可選擇修改 CS 設定允許 <script>，但這會提高維運成本與安全風險；需要一個不動平台設定的替代方案。
技術挑戰：在安全與功能間取得平衡。
影響範圍：平台安全、升級相容、維運風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 開放 <script> 可能引入 XSS。
2. 平台升級時自定義設定易被覆蓋。
3. 多作者平台管理難度提升。
深層原因：
- 架構層面：安全預設優先。
- 技術層面：腳本注入風險。
- 流程層面：權限與審批負擔。

### Solution Design（解決方案設計）
解決策略：採 HTC 替代方案，不改平台設定；若未來有必要調整設定，建立明確白名單與審核流程。

實施步驟：
1. 方案決策
- 實作細節：記錄不開啟 <script> 的決策依據
- 所需資源：決策文件
- 預估時間：30 分鐘
2. 替代方案實施
- 實作細節：落地 Case #3~#5
- 所需資源：CSS/HTC
- 預估時間：1 小時

關鍵程式碼/設定：
```text
策略文件：保持 communityserver.config 預設安全策略，不開放 <script> 直入
```

實際案例：作者明言不喜歡改 CS 設定，選 HTC。
實作環境：Community Server。
實測數據：
- 改善前：存在設定修改風險。
- 改善後：零設定變更、風險可控。
- 改善幅度：安全風險大幅降低（質化）。

Learning Points（學習要點）
核心知識點：
- 安全優先的取捨
- 白名單與審核流程
- 替代技術選型

技能要求：
- 必備技能：風險評估
- 進階技能：安全策略制定

延伸思考：
- 若必開放腳本，如何最小化攻擊面？
- 安全測試如何納入 CI？

Practice Exercise（練習題）
- 基礎練習：撰寫此決策的 ADR（30 分鐘）
- 進階練習：設計白名單審核表（2 小時）
- 專案練習：安全風險評估報告（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：清楚替代路徑
- 程式碼品質（30%）：N/A，著重文件
- 效能優化（20%）：決策效率
- 創新性（10%）：政策設計


## Case #11: jQuery 方案的取捨與限制（為何未採用）

### Problem Statement（問題陳述）
業務場景：jQuery 也能統一管理事件，理論上能實現 copy 功能；但平台限制無法輕易將 <script> 注入文章，且載入外部 JS 同樣需要可控注入點。
技術挑戰：在受限平台中如何實作 unobtrusive JS。
影響範圍：跨瀏覽器支援、技術負債。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. CS 過濾器阻擋內嵌腳本。
2. 外部 JS 注入也需平台允許。
3. 當下 HTC 在 IE 生態更直接。
深層原因：
- 架構層面：腳本載入策略受平台限制。
- 技術層面：事件委派可行但需載入管道。
- 流程層面：部署與權限限制。

### Solution Design（解決方案設計）
解決策略：短期採 HTC；若未來有外部 JS 注入管道（例如主題 head 可載入），再以 jQuery/原生事件委派提供跨瀏覽器 copy 功能。

實施步驟：
1. 短期落地
- 實作細節：沿用 HTC（見前案）
- 所需資源：CSS/HTC
- 預估時間：N/A
2. 中期規劃
- 實作細節：預留 .copycode class，未來以 JS 綁定 click 事件
- 所需資源：主題可載入外部 JS
- 預估時間：1~2 小時

關鍵程式碼/設定：
```js
// 未來可用的 unobtrusive 綁定（若平台允許外部 JS）：
document.addEventListener('click', function(e){
  if (e.target && e.target.classList.contains('copycode')) {
    const pre = e.target.closest('.csharpcode').querySelector('pre');
    if (!pre) return;
    const text = pre.textContent || pre.innerText || '';
    navigator.clipboard?.writeText(text).then(()=> {
      e.target.textContent = 'copied!';
      setTimeout(()=> e.target.textContent = 'copy code', 1500);
    });
  }
});
```

實際案例：原文說明 jQuery 亦可，但在 CS 上仍要「想辦法把 <script> 藏到 HTML 裡」較麻煩，故未採用。
實作環境：Community Server。
實測數據：
- 改善前：無法載入 JS。
- 改善後：規劃好未來替代路徑。
- 改善幅度：可演進性提升（質化）。

Learning Points（學習要點）
核心知識點：
- unobtrusive JS 與載入策略
- 事件委派
- 演進式改造

技能要求：
- 必備技能：JS 事件模型
- 進階技能：資產載入策略

延伸思考：
- 若可在主題 head 載入 JS，如何最小侵入？
- 是否以 Webpack/ESBuild 打包並快取？

Practice Exercise（練習題）
- 基礎練習：撰寫 unobtrusive 綁定（30 分鐘）
- 進階練習：加入 Clipboard API 與 fallback（2 小時）
- 專案練習：撰寫從 HTC 過渡到 JS 的改造方案（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可行替代路徑
- 程式碼品質（30%）：清晰與擴充性
- 效能優化（20%）：載入與執行效率
- 創新性（10%）：演進規劃


## Case #12: 樣式可讀性優化（字型、對比與行距）

### Problem Statement（問題陳述）
業務場景：程式碼閱讀需要良好字距與對比；預設主題可能導致字體不清晰或對比不足，影響讀者理解與眼睛負擔。
技術挑戰：在不破壞主題設計下提升程式碼區塊的易讀性。
影響範圍：閱讀體驗、停留時間。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設字型非最佳單寬字型。
2. 背景/前景對比不足。
3. 行距過密。
深層原因：
- 架構層面：主題對程式碼未特化。
- 技術層面：缺乏針對 code 的樣式覆寫。
- 流程層面：未進行可讀性驗收。

### Solution Design（解決方案設計）
解決策略：沿用官方建議字型串（Consolas, Courier New, Monospace），配置適度行距，確保對比；使用 .alt 與 .lnum 提升掃讀效率。

實施步驟：
1. 設置字型與對比
- 實作細節：強制 code 區塊使用單寬字型與淺背景
- 所需資源：CSS
- 預估時間：20 分鐘
2. 行距微調與行號樣式
- 實作細節：.lnum 灰階、.alt 交錯底色
- 所需資源：CSS
- 預估時間：20 分鐘

關鍵程式碼/設定：
```css
.csharpcode, .csharpcode pre {
  font-family: Consolas, "Courier New", Courier, Monospace;
  line-height: 1.35;
  background-color: #fff;
}
.csharpcode .lnum { color: #606060; user-select: none; }
.csharpcode .alt  { background-color: #f4f4f4; }
```

實際案例：原文 CSS 已提供字型與色彩建議。
實作環境：部落格前台。
實測數據：
- 改善前：閱讀吃力。
- 改善後：對比與字型優化，掃讀更易。
- 改善幅度：質化改善。

Learning Points（學習要點）
核心知識點：
- 單寬字型的重要性
- 對比與行距設計
- 行號與交錯底色

技能要求：
- 必備技能：CSS
- 進階技能：可讀性評估

延伸思考：
- 暗色系主題如何調整？
- 裝置字型可用性差異？

Practice Exercise（練習題）
- 基礎練習：替換字型與行距（30 分鐘）
- 進階練習：主題亮/暗雙配色（2 小時）
- 專案練習：可切換字型大小的控制元件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：各元素樣式到位
- 程式碼品質（30%）：選擇器精準
- 效能優化（20%）：最少覆寫
- 創新性（10%）：主題化設計


## Case #13: 外掛輸出原始程式碼節點（確保複製來源正確）

### Problem Statement（問題陳述）
業務場景：為了讓「copy code」取得乾淨文本，外掛在輸出時需包含原始程式碼（而非僅有加了格式的片段），否則 copy 會夾帶標籤或行號。
技術挑戰：輸出結構需要可被 HTC/JS 輕易定位。
影響範圍：複製成功率、貼上可用性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 若只有高亮後的 HTML，難以抽取純文字。
2. 行號/交錯底色會干擾文本擷取。
3. 外掛需明確輸出 <pre> 或專用節點。
深層原因：
- 架構層面：展示與資料源分離。
- 技術層面：選對節點方能擷取純文字。
- 流程層面：外掛輸出模板需規範。

### Solution Design（解決方案設計）
解決策略：外掛輸出包含 <pre> 內嵌原始程式碼；copy 行為專取該節點的 textContent/innerText。

實施步驟：
1. 定義輸出模板
- 實作細節：確保有 .csharpcode > pre 結構
- 所需資源：外掛模板
- 預估時間：30 分鐘
2. 綁定 copy 來源
- 實作細節：HTC/JS 從最靠近的 <pre> 取文本
- 所需資源：見 Case #5
- 預估時間：30 分鐘

關鍵程式碼/設定：
```html
<div class="csharpcode">
  <div class="toolbar"><span class="copycode">copy code</span></div>
  <pre>...原始碼...</pre> <!-- 作為純文字來源 -->
</div>
```

實際案例：原文截圖顯示外掛可勾選讓輸出包含原始程式碼。
實作環境：Windows Live Writer 外掛。
實測數據：
- 改善前：複製混入格式。
- 改善後：複製為乾淨文本。
- 改善幅度：貼上錯誤顯著降低（質化）。

Learning Points（學習要點）
核心知識點：
- 模板結構對互動功能的影響
- 展示層與資料源分離
- 可維護的標記規範

技能要求：
- 必備技能：模板輸出設計
- 進階技能：語意化標記

延伸思考：
- 是否需包含語言標示（data-lang）以利後續擴展？
- 大型片段如何分段與折疊？

Practice Exercise（練習題）
- 基礎練習：調整外掛輸出結構（30 分鐘）
- 進階練習：加入 data-* 屬性輔助選取（2 小時）
- 專案練習：多語言程式碼區塊模板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可順利擷取文本
- 程式碼品質（30%）：模板清晰
- 效能優化（20%）：最少 DOM 查找
- 講新性（10%）：擴展性設計


## Case #14: 以絕對 URL 指定 HTC 行為（跨層級可靠載入）

### Problem Statement（問題陳述）
業務場景：文章路徑層級不一（/post/、/columns/ 等），若 behavior:url 使用相對路徑，容易在不同層級解析錯誤。
技術挑戰：確保任意文章路徑都能正確載入 HTC。
影響範圍：功能一致性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 相對路徑受當前 URL 影響。
2. 不同文章可能在不同目錄層。
3. 造成行為載入失敗。
深層原因：
- 架構層面：路由多層級。
- 技術層面：URL 解析規則。
- 流程層面：缺少統一路徑策略。

### Solution Design（解決方案設計）
解決策略：使用以網站根為基準的絕對路徑（/themes/code.htc），避免層級問題。

實施步驟：
1. 修正 CSS
- 實作細節：將 behavior:url 改為絕對路徑
- 所需資源：CSS 編輯權限
- 預估時間：10 分鐘
2. 驗證多路徑文章
- 實作細節：測試不同 URL 下功能
- 所需資源：瀏覽器
- 預估時間：20 分鐘

關鍵程式碼/設定：
```css
.copycode { behavior: url('/themes/code.htc'); } /* 絕對路徑 */
```

實際案例：原文示例即使用絕對路徑。
實作環境：Community Server 多路徑內容。
實測數據：
- 改善前：部分 URL 下失效。
- 改善後：全站一致可用。
- 改善幅度：錯誤率降為 0（質化）。

Learning Points（學習要點）
核心知識點：
- 相對 vs 絕對路徑
- 多層級 URL 的資源載入
- 穩定性優先

技能要求：
- 必備技能：CSS/URL 基礎
- 進階技能：站台路徑規劃

延伸思考：
- 若有 CDN 或多子網域，如何處理？
- 本地與正式環境路徑一致策略？

Practice Exercise（練習題）
- 基礎練習：改為絕對路徑並驗證（30 分鐘）
- 進階練習：建立環境變數控制資源域名（2 小時）
- 專案練習：資產路徑抽象與自動替換（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：各路徑可用
- 程式碼品質（30%）：設定清晰
- 效能優化（20%）：避免重導
- 創新性（10%）：路徑管理策略


## Case #15: 發佈成效與使用者體驗驗證（質化指標）

### Problem Statement（問題陳述）
業務場景：導入語法高亮與 copy 功能後，需要驗證對讀者的實際效益，如貼上成功率、預覽流程順暢度、安全彈窗是否消除。
技術挑戰：平台未提供數據蒐集，需以質化與操作測試驗證。
影響範圍：功能驗收、後續優化決策。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無現成統計事件。
2. 功能影響屬於體驗層面。
3. 需人工測試與回饋。
深層原因：
- 架構層面：缺少事件追蹤。
- 技術層面：舊式技術不易加追蹤碼。
- 流程層面：驗收未標準化。

### Solution Design（解決方案設計）
解決策略：建立簡單驗收清單（語法色彩是否準確、IE copy 是否成功、非 IE 是否不顯示、預覽是否無警告），以質化結果做為里程碑；後續再考慮加入事件回報。

實施步驟：
1. 建立驗收清單
- 實作細節：列出 8~10 個可檢核項
- 所需資源：文件
- 預估時間：40 分鐘
2. 小組測試與回報
- 實作細節：不同瀏覽器、不同文章範例
- 所需資源：測試者
- 預估時間：1~2 小時

關鍵程式碼/設定：
```text
驗收項目（示例）：
- C# 程式碼顯示顏色正確
- Consolas/Monospace 字型生效
- IE 上 [copy code] 顯示且可用
- 非 IE 上 [copy code] 隱藏
- 預覽無安全警告
- 複製後貼到 IDE 可編譯
```

實際案例：原文描述 copy 可直接貼用、HTA 預覽無安全警告。
實作環境：多瀏覽器、多文章案例。
實測數據：
- 改善前：無色彩、copy 失效、預覽警告。
- 改善後：語法高亮、IE 可複製、預覽無警告。
- 改善幅度：質化合格率提升至 100%（驗收清單）。

Learning Points（學習要點）
核心知識點：
- 以質化驗收支持決策
- 驗收清單法
- 逐步引入量化指標

技能要求：
- 必備技能：測試設計
- 進階技能：使用者回饋整合

延伸思考：
- 日後是否加事件追蹤（copy 點擊次數）？
- 是否加入錯誤回報機制？

Practice Exercise（練習題）
- 基礎練習：撰寫驗收清單（30 分鐘）
- 進階練習：跨瀏覽器測試紀錄（2 小時）
- 專案練習：引入簡易事件紀錄（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：涵蓋核心場景
- 程式碼品質（30%）：N/A（文件）
- 效能優化（20%）：測試效率
- 創新性（10%）：指標設計


## Case #16: 下載與版本散佈溝通（風險與合規）

### Problem Statement（問題陳述）
業務場景：外掛有小改版並提供下載連結；需提示使用者下載並註明來源，確保尊重原作者與自家站點之引用。
技術挑戰：如何讓使用者獲得正確版本並理解必要的站台設定依賴（CSS/HTC）。
影響範圍：支援成本、版本一致性、授權。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用者未配置 CSS/HTC 導致功能失效。
2. 未註明來源造成引用爭議。
3. 外掛升級未同步資訊。
深層原因：
- 架構層面：外掛依賴站台設定。
- 技術層面：缺少安裝指引。
- 流程層面：發佈與說明未同步。

### Solution Design（解決方案設計）
解決策略：在下載頁提供安裝步驟（注入 CSS、放置 HTC、啟用按鈕）、相依條件與致謝說明；建立版本更新日誌。

實施步驟：
1. 安裝指引完善
- 實作細節：README、步驟與截圖
- 所需資源：文件
- 預估時間：1 小時
2. 版本資訊同步
- 實作細節：CHANGELOG 與相容性說明
- 所需資源：文件
- 預估時間：1 小時

關鍵程式碼/設定：
```markdown
安裝步驟摘要：
1) 後台 Custom Styles 貼入 CodeFormatter CSS
2) 上傳 /themes/code.htc
3) 發文時啟用「輸出包含原始程式碼」選項
4) 正式環境測試 IE 上 copy 功能
```

實際案例：原文提供下載連結並說明需配合站台設定。
實作環境：外掛散佈頁面。
實測數據：
- 改善前：安裝錯誤率高。
- 改善後：依指引成功安裝。
- 改善幅度：支援工單減少（質化）。

Learning Points（學習要點）
核心知識點：
- 發佈說明與依賴提示
- 版本與相容性管理
- 授權與致謝

技能要求：
- 必備技能：技術寫作
- 進階技能：用戶教育設計

延伸思考：
- 是否提供自動檢查腳本（檢測 CSS/HTC 是否到位）？
- FAQ 與常見故障排除條目？

Practice Exercise（練習題）
- 基礎練習：撰寫安裝 README（30 分鐘）
- 進階練習：整理 CHANGELOG（2 小時）
- 專案練習：製作安裝檢查器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：指引完整
- 程式碼品質（30%）：N/A（文件/工具）
- 效能優化（20%）：降低支援成本
- 創新性（10%）：安裝檢查器


--------------------------------
案例分類
--------------------------------

1) 按難度分類
- 入門級（適合初學者）
  - Case #1, #2, #6, #7, #12, #14, #15, #16
- 中級（需要一定基礎）
  - Case #3, #4, #5, #9, #10, #11
- 高級（需要深厚經驗）
  - （本組案例聚焦於平台限制與老技術整合，較少高級；若延伸至現代化改造與跨平台兼容，Case #11 可延伸為高級）

2) 按技術領域分類
- 架構設計類
  - Case #10, #11, #15, #16
- 效能優化類
  - （本系列主要為功能與可用性，效能影響較小）
- 整合開發類
  - Case #1, #2, #3, #4, #5, #7, #9, #14
- 除錯診斷類
  - Case #6, #7, #14, #15
- 安全防護類
  - Case #8, #10

3) 按學習目標分類
- 概念理解型
  - Case #1, #2, #6, #12, #14
- 技能練習型
  - Case #3, #4, #5, #7, #8, #9
- 問題解決型
  - Case #10, #11, #15
- 創新應用型
  - Case #16（也可延伸 #11 的現代化替代）

--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 建議先學：
  - Case #1（導入 CSS 基礎）→ Case #2（不改主題快速注入）
- 其後進入互動功能：
  - Case #3（平台限制與 HTC 策略）→ Case #4（behavior:url 實作）→ Case #5（複製純文字）
- 兼容與穩定性：
  - Case #6（優雅降級）→ Case #7（路徑與部署）→ Case #14（絕對路徑策略）
- 預覽體驗：
  - Case #8（HTA 預覽）→ Case #9（預覽關閉 copy）
- 安全與取捨：
  - Case #10（不改平台設定）→ Case #11（jQuery 方案取捨與演進）
- 體驗與可讀性：
  - Case #12（字型與可讀性）→ Case #13（輸出原始節點）
- 發佈與評估：
  - Case #15（成效驗收）→ Case #16（散佈與用戶教育）

依賴關係：
- Case #3 依賴 Case #1/#2（先有 CSS 與 class 才能掛行為）
- Case #5 依賴 Case #4（先能觸發事件再談純文字擷取）
- Case #9 依賴外掛輸出行為（Case #3~#5）
- Case #11 的現代化替代依賴平台可載入外部 JS

完整學習路徑總結：
1) 導入樣式（#1→#2）→ 2) 實作 copy 行為（#3→#4→#5）→ 3) 兼容與穩定（#6→#7→#14）→ 4) 預覽優化（#8→#9）→ 5) 安全與演進決策（#10→#11）→ 6) 體驗與結構完善（#12→#13）→ 7) 成效驗收與散佈（#15→#16）

以上 15 個案例完整覆蓋原文提及的問題、根因、解法與實際效益，並補足教學實作所需的關鍵程式碼與練習、評估規準。