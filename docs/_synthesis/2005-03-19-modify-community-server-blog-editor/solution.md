---
layout: synthesis
title: "修改 Community Server 的 blog editor"
synthesis_type: solution
source_post: /2005/03/19/modify-community-server-blog-editor/
redirect_from:
  - /2005/03/19/modify-community-server-blog-editor/solution/
---

以下內容根據原文所描述的實際情境（Community Server 使用 FreeTextBox，卻被自研 Editor Wrapper 擋住，且缺少 wrapper 原始碼，導致無法把自訂圖片/表情工具整合進原生工具列）進行系統化重組，產出 15 個完整且可操作的教學案例。每個案例均含問題、根因、解法、實作步驟、關鍵程式、學習要點與練習與評估建議。實測數據部分以可驗收的目標指標呈現，供教學/專案練習使用。

## Case #1: 無法將自訂圖片/表情工具整合進 FTB 工具列（被 CS Wrapper 阻隔）

### Problem Statement（問題陳述）
- 業務場景：團隊部署 Community Server 作為部落格平台，作者希望在編輯器內快速「貼圖、貼表情」，但預設工具列不足；且因 CS 以自有 Wrapper 包住 FreeTextBox，導致新增的工具列無法嵌回原 FTB 工具列，只能額外浮在頁面上方，體驗割裂。
- 技術挑戰：找不到 Wrapper 原始碼，無法直接修改；需在不改動核心程式的前提下，把自訂工具按鈕注入 FTB 工具列。
- 影響範圍：編輯效率下降、UI 不一致、使用者學習成本高；維護成本增加。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. CS 未暴露 Wrapper 原始碼，無法在伺服器端擴充工具列。
  2. FTB 工具列節點在 Wrapper 內部，外部新增按鈕無法置入正確容器。
  3. 頁面生命週期中，注入時機與控制項尚未完成初始化產生衝突。
- 深層原因：
  - 架構層面：編輯器被強耦合封裝，缺少官方擴充介面。
  - 技術層面：FTB 與外部 DOM 隔離（iframe/命名容器），跨界操作困難。
  - 流程層面：未建立「無侵入式擴充」技術基線與規範。

### Solution Design（解決方案設計）
- 解決策略：以無侵入方式注入。於頁面載入後以 JS 掃描 FTB 工具列容器，將自訂按鈕 DOM 節點動態插入既有工具列內；按鈕事件調用「在游標處插入 HTML」的 API，達到原生整合效果與一致 UI。

- 實施步驟：
  1. 探測工具列容器
     - 實作細節：等待 FTB 初始化完成後，透過 querySelector/ID 規則找到 toolbar 節點。
     - 所需資源：瀏覽器 DevTools；頁面腳本區
     - 預估時間：0.5 天
  2. 動態建立按鈕並注入事件
     - 實作細節：建立 <button> 節點，掛上 onclick 導向插入邏輯；支援圖片與表情。
     - 所需資源：原始圖示檔、圖庫
     - 預估時間：0.5 天
  3. 插入 API 封裝
     - 實作細節：封裝跨瀏覽器的 insertHTML（execCommand/Range）支援。
     - 所需資源：測試瀏覽器矩陣
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```html
<!-- 工具列注入腳本 -->
<script>
(function() {
  function findToolbar() {
    // 假設 FTB 在 wrapper 內，toolbar 有可識別 class 或 ID
    return document.querySelector('.ftb-toolbar, #FreeTextBox1___Toolbar');
  }
  function insertAtCaret(html) {
    // 嘗試標準 execCommand，再回退 Range 操作
    var iframe = document.getElementById('FreeTextBox1___Frame');
    var doc = iframe ? iframe.contentDocument : document;
    iframe && iframe.contentWindow.focus();
    if (doc && doc.execCommand) {
      if (doc.execCommand('insertHTML', false, html)) return;
    }
    var sel = (iframe ? iframe.contentWindow : window).getSelection();
    if (sel && sel.rangeCount) {
      var range = sel.getRangeAt(0);
      var el = doc.createElement('div'); el.innerHTML = html;
      var frag = doc.createDocumentFragment(), node;
      while ((node = el.firstChild)) frag.appendChild(node);
      range.deleteContents(); range.insertNode(frag);
    } else if (doc.selection && doc.selection.createRange) { // IE
      doc.selection.createRange().pasteHTML(html);
    }
  }
  function addButton(icon, title, onClick) {
    var tb = findToolbar(); if (!tb) return;
    var btn = document.createElement('button');
    btn.type='button'; btn.title=title; btn.innerHTML=icon;
    btn.onclick = onClick; tb.appendChild(btn);
  }
  window.addEventListener('load', function() {
    addButton('🖼️', '插入圖片', function() {
      var url = prompt('圖片 URL'); if (url) insertAtCaret('<img src="'+url+'" alt="">');
    });
    addButton('😊', '插入表情', function() {
      insertAtCaret('<img src="/emotes/smile.png" alt=":)" />');
    });
  });
})();
</script>
```

- 實際案例：出自本文場景：CS 以 Wrapper 隔絕 FTB，導致自訂工具列無法整合；本解法以 DOM 注入方式與插入 API 取得一致體驗。
- 實作環境：ASP.NET WebForms（.NET 2.0+）、Community Server 1.x/2.x、FreeTextBox 3.x、IIS 6/7
- 實測數據（驗收目標）：
  - 改善前：插入圖片需 4-6 次點擊與切換視窗
  - 改善後：1-2 次點擊完成插入
  - 改善幅度：操作步驟下降 ≥60%

- Learning Points（學習要點）
  - 核心知識點：無侵入式 DOM 注入；跨 iframe 游標插入；工具列一致性
  - 技能要求：
    - 必備技能：JavaScript DOM、基本跨瀏覽器相容
    - 進階技能：內容編輯器 API、可用性與交互設計
  - 延伸思考：若 FTB 結構變動如何防脆弱？是否需版本檢測？如何記錄插入歷史以支援撤銷？

- Practice Exercise（練習題）
  - 基礎練習：為工具列增加「水平線」按鈕並插入 <hr>（30 分鐘）
  - 進階練習：實作圖片 URL 驗證與預覽（2 小時）
  - 專案練習：做一個可配置的工具列注入器（JSON 配置）（8 小時）

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：按鈕出現並可插入 HTML，支援圖片/表情
  - 程式碼品質（30%）：模組化、無全域汙染、相容性處理清晰
  - 效能優化（20%）：最小化 DOM 操作，懶載入圖示
  - 創新性（10%）：良好 UX、可配置性

---

## Case #2: 缺少 Editor Wrapper 原始碼的掛鉤與擴充（反射/尋控）

### Problem Statement（問題陳述）
- 業務場景：在無法取得 CS Editor Wrapper 原始碼的前提下，仍需在伺服器端配置 FTB 屬性或添加子控制項（如上傳對話框觸發器），否則只能以前端修補，維護成本高且脆弱。
- 技術挑戰：在 WebForms 控制項樹中定位到 Wrapper 內部的 FTB 實例，並於 Page Lifecycle 正確時機加以設定或注入。
- 影響範圍：功能擴充受阻；每次升級或改版需重工。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 缺少 Wrapper 原始碼與擴充點。
  2. FTB 被命名容器包裹，ID 難以預測。
  3. 在不當生命週期時點動態注入導致 Null/Override 失效。
- 深層原因：
  - 架構層面：缺乏明確的介面/事件管線。
  - 技術層面：控件樹查找、反射與生命周期知識不足。
  - 流程層面：未建立元件級客製的標準流程與測試。

### Solution Design（解決方案設計）
- 解決策略：封裝一個「尋控工具」於 OnInit/OnPreRender 階段遞迴 FindControl/反射讀取內部欄位，以非侵入方式抓到 FTB 實例並施加配置或附加子控件。

- 實施步驟：
  1. 控制樹遞迴搜尋
     - 實作細節：撰寫工具方法 TraverseFind<T>(root, predicate) 尋找目標型別。
     - 資源：C# 擴充方法
     - 時間：0.5 天
  2. 反射安全存取
     - 實作細節：若 FTB 被 private 欄位持有，使用 BindingFlags 非公開取值。
     - 資源：System.Reflection
     - 時間：0.5 天
  3. 生命週期掛點
     - 實作細節：在 OnPreRender 完成注入，避免 ViewState 與事件問題。
     - 資源：Page 生命週期知識
     - 時間：0.5 天

- 關鍵程式碼/設定：
```csharp
// 尋找 Wrapper 內部的 FreeTextBox 實例
public static T FindControlRecursive<T>(Control root) where T : Control {
    if (root is T) return (T)root;
    foreach (Control c in root.Controls) {
        var found = FindControlRecursive<T>(c);
        if (found != null) return found;
    }
    return null;
}

protected override void OnPreRender(EventArgs e) {
    base.OnPreRender(e);
    var ftb = FindControlRecursive<Control>(this.Page)
              ?.FindControl("FreeTextBox1") as Control;
    if (ftb == null) {
        // 回退：用型別名判斷
        ftb = FindControlRecursive<Control>(this.Page)
              ?.Controls.Cast<Control>()
              .FirstOrDefault(x => x.GetType().FullName.Contains("FreeTextBox"));
    }
    if (ftb != null) {
        // 反射設置屬性，如 EnableHtmlMode
        var prop = ftb.GetType().GetProperty("EnableHtmlMode");
        prop?.SetValue(ftb, true, null);
    }
}
```

- 實際案例：本文情境的 Wrapper 導致無法直接配置 FTB；透過遞迴尋控與反射，於不改源碼前提下實現伺服器端控制。
- 實作環境：ASP.NET WebForms（.NET 2.0/3.5）、FreeTextBox 3.x
- 實測數據（驗收目標）：
  - 成功定位率：≥ 99%（跨版位與母板頁）
  - 生命週期錯誤：0 次（CI 自動測試）

- Learning Points：控件樹與生命週期、反射風險控制、回退策略
- 技能要求：C# 反射、WebForms 生命周期；進階：診斷控件樹、健壯性設計
- 延伸思考：如何避免反射脆弱性？是否可用 Adapter 取代？如何監測升級破壞？

- Practice Exercise：撰寫泛型 Traverse；加上型別白名單；建立單元測試
- Assessment Criteria：功能找到並設置屬性；代碼健壯；對錯誤處理完善；可測試性

---

## Case #3: 以適配器替換 CS Wrapper，直連 FTB 並保持外部介面

### Problem Statement（問題陳述）
- 業務場景：希望長期維護與功能擴充時不再受限於 Wrapper，計畫以自建 Adapter 控制項替換（或假裝為）原 Wrapper，外部契約不變，內部直接承載 FTB 與自訂工具列。
- 技術挑戰：維持既有頁面與程式對 Wrapper 的相容 API（Text、Html、Events），同時導入 FTB 與新功能。
- 影響範圍：影響整體編輯功能、既有頁面與事件流程。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. Wrapper 封裝強且不可改。
  2. FTB 提供充分 API，但被阻隔。
  3. 技術債累積，導致再修補成本高於重構。
- 深層原因：
  - 架構層面：缺少抽象層與可替換性設計。
  - 技術層面：契約穩定性、事件/狀態同步難。
  - 流程層面：缺乏重構風險控管與回退計畫。

### Solution Design
- 解決策略：定義 IEditorAdapter 介面，實作新控制項 EditorAdapter：對外暴露與原 Wrapper 等效屬性/事件；內部以 FTB 實現，並提供自訂工具列擴充點；透過 web.config/控件庫替換。

- 實施步驟：
  1. 介面設計與對齊
     - 細節：比對原 Wrapper 公開契約；建立 IEditorAdapter
     - 資源：反編譯工具（ILSpy）
     - 時間：1 天
  2. 控制項實作
     - 細節：CompositeControl 承載 FTB；轉拋事件與屬性
     - 資源：FTB 套件
     - 時間：2 天
  3. 灰度替換與回退
     - 細節：以配置切換；A/B 測試
     - 資源：web.config、自製 Feature Flag
     - 時間：1 天

- 關鍵程式碼/設定：
```csharp
public interface IEditorAdapter {
    string Html { get; set; }
    event EventHandler TextChanged;
    void Focus();
}

[ToolboxData("<{0}:EditorAdapter runat=server></{0}:EditorAdapter>")]
public class EditorAdapter : CompositeControl, IEditorAdapter {
    private FreeTextBoxControls.FreeTextBox _ftb;
    public string Html { get => _ftb.Text; set => _ftb.Text = value; }
    public event EventHandler TextChanged;
    protected override void CreateChildControls() {
        _ftb = new FreeTextBoxControls.FreeTextBox { ID = "FTB" };
        _ftb.TextChanged += (s,e)=> TextChanged?.Invoke(this,e);
        Controls.Add(_ftb);
        // TODO: 注入自訂工具列
    }
    public void Focus() => _ftb.Focus();
}
```

- 實際案例：針對本文問題，建立可替換的 Adapter 控制項，長期消除 Wrapper 限制。
- 實作環境：ASP.NET WebForms、C#、FTB 3.x
- 實測數據（驗收目標）：
  - 相容性：既有頁面零修改即可切換
  - 稳定性：回退開關可即時切換且無錯誤
  - 擴充性：新增工具列功能工期縮短 ≥50%

- Learning Points：契約設計、CompositeControl、灰度發佈
- 技能要求：WebForms 自訂控件；進階：介面穩定性與測試
- 延伸思考：如何封裝上傳/表情為擴充點？如何支援未來更換為 Quill/TinyMCE？

- Practice：設計 IEditorAdapter；以配置切換兩種實作；寫 UI 測試
- 評估：相容 API 覆蓋；切換安全；文件與測試完整

---

## Case #4: 建立客製工具按鈕與命令（FTB Custom Toolbar）

### Problem Statement
- 業務場景：需要提供「貼圖/表情」等快捷功能，直接以 FTB 的自訂按鈕機制擴充，避免維護純前端注入的脆弱性。
- 技術挑戰：了解 FTB 擴充點、命令與對話框交互，將新命令加入原生工具列。
- 影響範圍：提高一致性，降低長期成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：未使用 FTB 內建擴充機制；改以外掛工具列；缺少命令綁定。
- 深層原因：對編輯器擴充框架認知不足；文檔缺失。

### Solution Design
- 解決策略：使用 FTB 的 CustomToolbarButton（或設定 ToolbarLayout）註冊自訂命令，按鈕事件呼叫插入邏輯或開啟對話框回填 HTML。

- 實施步驟：
  1. 確認 FTB 版本與擴充文檔
     - 細節：列出支持的 ToolbarLayout/CustomButton
     - 時間：0.5 天
  2. 設定工具列與命令
     - 細節：在後端設置 Toolbars；前端命令呼叫 JS 插入
     - 時間：0.5 天
  3. 對話框整合
     - 細節：開窗選擇表情/圖片，回填 HTML
     - 時間：1 天

- 關鍵程式碼/設定：
```aspx
<FTB:FreeTextBox ID="FTB" runat="server" ToolbarLayout="Bold;Italic;|;InsertImage;|;Custom_Emote" />

<script>
function FTB_Command_Custom_Emote(ftbId) {
  // FTB 按鈕命令命名規則：FTB_Command_{Name}
  var url = prompt('選擇表情(輸入檔名)：'); if(!url) return;
  var html = '<img src="/emotes/'+url+'.png" alt="emote" />';
  // 使用與 Case#1 相同插入封裝
  insertAtCaret(html);
}
</script>
```

- 實際案例：將「表情」作為 FTB 自訂按鈕，按鈕出現在原生工具列，體驗一致。
- 實作環境：FTB 3.x、ASP.NET WebForms
- 實測數據（驗收目標）：
  - UI 一致性：100% 同一列呈現
  - 任務效率：插入操作時間 < 3 秒

- Learning Points：FTB 自訂命令、工具列配置、事件命名規則
- 技能要求：WebForms 控制項屬性；進階：編輯器命令模型
- 延伸思考：如何把命令改為插件化載入？如何權限控制？

- Practice：新增「插入程式碼區塊」按鈕；支持語法高亮
- 評估：命令可用；UI 一致；代碼結構清晰

---

## Case #5: 以 JavaScript 在游標處插入 HTML（跨 iframe/IE/標準）

### Problem Statement
- 業務場景：無論使用自訂按鈕或對話框，關鍵能力是「在當前游標處插入圖片/表情或 HTML 片段」，需支援 FTB 的 iframe 與舊版 IE。
- 技術挑戰：跨瀏覽器選取範圍與 execCommand 相容性。
- 影響範圍：功能可用性、資料正確性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：FTB 使用 contentEditable iframe；不同瀏覽器選區 API 差異大。
- 深層原因：缺少通用插入封裝；對舊版 IE 未提供回退。

### Solution Design
- 解決策略：封裝 insertAtCaret，優先使用 execCommand('insertHTML')，回退 Range API/IE pasteHTML，並處理焦點切換到 iframe。

- 實施步驟：
  1. 焦點控制與 iframe 文件獲取（0.5 天）
  2. 標準 API 優先 + 回退策略（0.5 天）
  3. 單元測試：常見片段（圖片、表情、連結）（1 天）

- 關鍵程式碼/設定：
```javascript
function insertIntoFTB(frameId, html) {
  var iframe = document.getElementById(frameId);
  var win = iframe.contentWindow, doc = win.document;
  iframe.contentWindow.focus();
  if (doc.execCommand && doc.execCommand('insertHTML', false, html)) return true;
  var sel = win.getSelection && win.getSelection();
  if (sel && sel.rangeCount) {
    var range = sel.getRangeAt(0);
    var el = doc.createElement('div'); el.innerHTML = html;
    var frag = doc.createDocumentFragment();
    while (el.firstChild) frag.appendChild(el.firstChild);
    range.deleteContents(); range.insertNode(frag);
    return true;
  } else if (doc.selection && doc.selection.createRange) {
    doc.selection.createRange().pasteHTML(html); return true;
  }
  return false;
}
```

- 實際案例：所有插入功能（圖片、表情、連結）共用該封裝，降低重複與相容性問題。
- 實作環境：IE 8+/現代瀏覽器、FTB 3.x
- 實測數據（驗收目標）：
  - 成功插入率 ≥ 99%（跨瀏覽器）
  - 插入耗時 < 50ms（平均）

- Learning Points：選區 API、iframe 焦點管理、回退策略
- 技能要求：JS DOM/Selection；進階：跨瀏覽器測試策略
- 延伸思考：如何支援撤銷/重做？如何處理貼上純文字？

- Practice：加入「包裹選區」功能，為選中文本加 <strong>
- 評估：功能正確；跨瀏覽器通過；有單元測試

---

## Case #6: 圖片上傳服務與插入對話框整合

### Problem Statement
- 業務場景：作者需要直接上傳圖片並自動插入文章；需驗證權限、限制檔案大小、生成縮圖、回傳 URL 供插入。
- 技術挑戰：安全、效能與 UX 的端到端設計。
- 影響範圍：資安風險、磁碟壓力、上傳體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：缺少統一上傳 API 與回填機制。
- 深層原因：未納管檔案儲存路徑與存取控制；圖片處理無標準。

### Solution Design
- 解決策略：建立 /upload.ashx 上傳端點，驗證登入與 MIME/大小，儲存至使用者目錄並生成縮圖；回傳 JSON（URL、寬高）。前端對話框完成後調用 insertIntoFTB 插入 <img>。

- 實施步驟：
  1. 上傳端點與驗證（1 天）
  2. 影像處理與縮圖（0.5 天）
  3. 前端對話框與回填（0.5 天）

- 關鍵程式碼/設定：
```csharp
// /upload.ashx
public class UploadHandler : IHttpHandler {
  public void ProcessRequest(HttpContext ctx) {
    if (!ctx.User.Identity.IsAuthenticated) { ctx.Response.StatusCode=401; return; }
    var file = ctx.Request.Files[0];
    if (file==null || file.ContentLength==0) { ctx.Response.StatusCode=400; return; }
    if (file.ContentLength > 2*1024*1024) { ctx.Response.StatusCode=413; return; }
    // 簡單 MIME 檢查
    if (!file.ContentType.StartsWith("image/")) { ctx.Response.StatusCode=415; return; }
    var folder = $"/uploads/{ctx.User.Identity.Name}/";
    var path = ctx.Server.MapPath(folder); Directory.CreateDirectory(path);
    var fname = Path.GetFileName(file.FileName);
    var full = Path.Combine(path, fname); file.SaveAs(full);
    // TODO: 生成縮圖 thumbFull
    var url = folder + fname;
    ctx.Response.ContentType="application/json";
    ctx.Response.Write("{\"url\":\""+url+"\"}");
  }
  public bool IsReusable => false;
}
```

- 實際案例：依本文需求讓「貼圖」一鍵完成：上傳→回填插入。
- 實作環境：ASP.NET/IIS、System.Drawing
- 實測數據（驗收目標）：
  - 上傳成功率 ≥ 99%
  - 平均上傳時間（<1MB）< 1s
  - 不合規檔案阻擋率 100%

- Learning Points：上傳安全、目錄規劃、前後端協作
- 技能要求：HTTP 處理程式、圖片處理；進階：CDN/快取策略
- 延伸思考：如何去除 EXIF？如何防止同名覆寫？版本化 URL？

- Practice：加入參數自動插入寬高/alt；生成多尺寸
- 評估：安全檢查完善；回填正確；例外處理完備

---

## Case #7: 表情符號選單元件與佈景同步

### Problem Statement
- 業務場景：提供一個表情選單面板，顯示所有可用表情，點擊即插入；隨佈景主題切換不同表情集。
- 技術挑戰：資源管理與清單維護；插入體驗順暢。
- 影響範圍：使用者滿意度與主題一致性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：表情資源散落、缺少 manifest 與動態載入。
- 深層原因：主題與功能未整合；無統一配置。

### Solution Design
- 解決策略：建立 emotes.json 作為清單，依主題載入；以懶載入圖片與容器委派事件，點擊插入對應 <img>。

- 實施步驟：
  1. 建立 Manifest 與資料夾結構（0.5 天）
  2. 前端面板渲染與事件處理（0.5 天）
  3. 主題切換載入不同清單（0.5 天）

- 關鍵程式碼/設定：
```json
// /themes/default/emotes.json
{ "base": "/themes/default/emotes/",
  "items": ["smile.png","sad.png","wink.png"] }
```
```javascript
fetch('/themes/default/emotes.json').then(r=>r.json()).then(cfg=>{
  const box = document.getElementById('emoteBox');
  cfg.items.forEach(f=>{
    const img = new Image(); img.loading='lazy';
    img.src = cfg.base + f; img.alt = f.replace('.png','');
    img.onclick = ()=> insertIntoFTB('FreeTextBox1___Frame','<img src="'+img.src+'" alt="'+img.alt+'">');
    box.appendChild(img);
  });
});
```

- 實際案例：本文的「貼表情」以清單化、主題化方式維護，避免硬編碼。
- 實作環境：靜態 JSON、前端 JS
- 實測數據（驗收目標）：
  - 面板首次渲染 < 200ms
  - 圖片懶載入命中率 ≥ 90%

- Learning Points：資源清單、懶載入、主題切換
- 技能要求：基礎 JS；進階：資源組織與可配置化
- 延伸思考：可否使用 Sprite 降請求？是否需搜尋/分類？

- Practice：加入搜尋框；鍵盤導航
- 評估：操作流暢；主題切換正確；碼規一致

---

## Case #8: 工具列 UX 統一與版位衝突解法

### Problem Statement
- 業務場景：自訂工具列被迫置於頁面上方，與 FTB 工具列分離，導致 UI 不一致；需要將外部工具列整合或「視覺上」無縫拼接。
- 技術挑戰：不破壞現有 DOM 的前提下，將外部工具列併入原列或靠齊。
- 影響範圍：可用性、審美與學習成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：Wrapper 擋住內嵌；外部工具列只能浮動。
- 深層原因：未定義 UI 對齊規範與樣式變數；缺乏彈性容器。

### Solution Design
- 解決策略：尋找 FTB 工具列容器，將外部工具列節點 append 進入；若不可行，使用 CSS Flex 對齊與同樣式變數實現視覺拼接。

- 實施步驟：
  1. DOM 移位注入（0.5 天）
  2. 樣式抽象與變數統一（0.5 天）
  3. 響應式調整（0.5 天）

- 關鍵程式碼/設定：
```css
.ftb-toolbar, .ext-toolbar { display:flex; gap:6px; align-items:center; }
.ext-toolbar button { background:var(--tb-bg); border:1px solid var(--tb-bd); }
```
```javascript
var tb = document.querySelector('.ftb-toolbar');
var ext = document.getElementById('extToolbar');
if (tb && ext) tb.appendChild(ext); // 併入原列
```

- 實際案例：把現有外掛工具列 DOM 直接移入 FTB 工具列容器，視覺與交互一致。
- 實作環境：CSS/JS
- 實測數據（驗收目標）：
  - 視覺差異 0（設計驗收）
  - 多瀏覽器呈現一致性 ≥ 99%

- Learning Points：DOM 併入、樣式系統、響應式工具列
- 技能要求：CSS/JS；進階：設計系統 tokens
- 延伸思考：溢出處理？小螢幕折疊策略？

- Practice：加入「更多」溢出菜單
- 評估：一致性、可用性、易維護

---

## Case #9: HTML 安全與消毒：防 XSS/危險屬性

### Problem Statement
- 業務場景：允許貼入 HTML（圖片/表情/連結），需防止惡意腳本、事件屬性或危險 URL 協定。
- 技術挑戰：白名單策略、效能與相容的平衡。
- 影響範圍：資安、平台信譽與法規遵循。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：FTB 允許輸入 HTML；使用者可貼入惡意內容。
- 深層原因：未啟用消毒；缺少白名單與測試。

### Solution Design
- 解決策略：後端保存前以 HTML Sanitizer 白名單清洗；允許基本格式與 img/src/http(s)/data:image 白名單；剝除 on* 事件、javascript:、style 中的表達式。

- 實施步驟：
  1. 選擇 Sanitizer（Microsoft AntiXSS/HtmlAgilityPack）（0.5 天）
  2. 依需求配置白名單（0.5 天）
  3. 加入單元測試與惡意樣本（1 天）

- 關鍵程式碼/設定：
```csharp
public static string Sanitize(string html) {
  var whitelist = new HashSet<string>{"b","i","u","a","img","p","br","ul","ol","li","code"};
  var doc = new HtmlAgilityPack.HtmlDocument(); doc.LoadHtml(html);
  void CleanNode(HtmlAgilityPack.HtmlNode node) {
    if (!whitelist.Contains(node.Name.ToLower())) { node.ParentNode.RemoveChild(node, true); return; }
    foreach (var a in node.Attributes.ToList()) {
      var name = a.Name.ToLower();
      if (name.StartsWith("on")) { node.Attributes.Remove(a); continue; }
      if (node.Name=="a" && name=="href" && a.Value.StartsWith("javascript:")) node.Attributes.Remove(a);
      if (node.Name=="img" && name=="src" && !(a.Value.StartsWith("http")||a.Value.StartsWith("data:image"))) node.Attributes.Remove(a);
    }
    foreach (var child in node.ChildNodes.ToList()) if (child.NodeType==HtmlAgilityPack.HtmlNodeType.Element) CleanNode(child);
  }
  foreach (var n in doc.DocumentNode.ChildNodes.ToList()) if (n.NodeType==HtmlAgilityPack.HtmlNodeType.Element) CleanNode(n);
  return doc.DocumentNode.InnerHtml;
}
```

- 實際案例：貼圖/表情功能同時導入清洗，保障內容安全。
- 實作環境：.NET、HtmlAgilityPack
- 實測數據（驗收目標）：
  - OWASP XSS 測試樣本阻擋率 100%
  - 平均清洗耗時 < 10ms/篇

- Learning Points：白名單策略、常見 XSS 向量、效能
- 技能要求：C# 後端；進階：安全測試
- 延伸思考：如何與 CSP 搭配？是否需不同群組白名單？

- Practice：加入 CSP 標頭與 img-src 白名單
- 評估：安全通過；效能合格；配置可維護

---

## Case #10: 瀏覽器相容性與降級策略（FTB 失效改用 textarea）

### Problem Statement
- 業務場景：在某些環境或舊版瀏覽器 FTB 可能無法正確載入，需要保底的可編輯體驗與功能降級。
- 技術挑戰：偵測失敗與自動切換 UI。
- 影響範圍：可用性與支援成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：FTB 依賴 iframe contentEditable；部分瀏覽器/企業環境阻擋。
- 深層原因：缺乏健壯的降級設計。

### Solution Design
- 解決策略：載入後心跳檢查 FTB 是否可編輯；失敗則隱藏 FTB、顯示 textarea 並保留基本插入（以 BBCode 或 Markdown）與伺服器端轉換。

- 實施步驟：
  1. 可用性檢測腳本（0.5 天）
  2. 降級 UI 與提示（0.5 天）
  3. 伺服器端轉換器（1 天）

- 關鍵程式碼/設定：
```javascript
function editorHealthy(frameId) {
  try {
    var doc = document.getElementById(frameId).contentDocument;
    var editable = doc && doc.body && doc.body.isContentEditable !== false;
    return !!editable;
  } catch(e){return false;}
}
window.addEventListener('load', function(){
  if(!editorHealthy('FreeTextBox1___Frame')){
    document.getElementById('FTBContainer').style.display='none';
    document.getElementById('FallbackTextarea').style.display='';
  }
});
```

- 實際案例：在客戶端阻擋腳本的環境仍可發文（降級）。
- 實作環境：JS/C#
- 實測數據（驗收目標）：
  - 降級命中時仍可完成所有必需欄位
  - 失敗回報率下降 ≥ 80%

- Learning Points：降級設計、健康檢查、回退渲染
- 技能要求：JS 基礎；進階：格式轉換
- 延伸思考：如何同步兩種模式的草稿？如何提示升級瀏覽器？

- Practice：實作 Markdown→HTML 伺服端轉換
- 評估：降級可用；提示清楚；錯誤處理完善

---

## Case #11: 靜態資源負載優化：圖示懶載與快取

### Problem Statement
- 業務場景：工具列圖示與表情資源較多，初次載入耗時與請求數過高。
- 技術挑戰：在不破壞功能的前提下降低初次成本。
- 影響範圍：LCP、互動延遲、伺服器負載。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：一次載入全部圖示與表情；缺少快取策略。
- 深層原因：未做資源分割與延遲策略；缺 CDN/長快取。

### Solution Design
- 解決策略：表情採懶載入；工具列圖示合併 Sprite 或 Icon Font；設定長快取與版本化；開啟 GZip/Deflate。

- 實施步驟：
  1. 懶載入與 IntersectionObserver（0.5 天）
  2. 版本化資源與 Cache-Control（0.5 天）
  3. 圖示合併與體積優化（1 天）

- 關鍵程式碼/設定：
```http
# IIS web.config 片段（靜態資源快取）
<staticContent>
  <clientCache cacheControlMode="UseMaxAge" cacheControlMaxAge="365.00:00:00" />
</staticContent>
```
```javascript
// 懶載入回退
document.querySelectorAll('img[data-src]').forEach(img=>{
  if('IntersectionObserver' in window){
    new IntersectionObserver((es,ob)=>es.forEach(e=>{
      if(e.isIntersecting){ e.target.src=e.target.dataset.src; ob.unobserve(e.target); }
    })).observe(img);
  } else { img.src = img.dataset.src; }
});
```

- 實際案例：表情面板從 100+ 張圖改為視窗內懶載，首屏更快。
- 實作環境：IIS/Web.config、前端 JS
- 實測數據（驗收目標）：
  - 首屏請求數下降 ≥ 60%
  - LCP 改善 ≥ 30%

- Learning Points：快取策略、懶載入、資源版本化
- 技能要求：前端性能；進階：CDN 與壓縮
- 延伸思考：能否使用 HTTP/2 Push/Preload？是否切換成 SVG？

- Practice：將工具列圖示改為 SVG Sprite
- 評估：指標改善；相容性良好；可回退

---

## Case #12: 升級與維護：以 ControlAdapter/HttpModule 降低侵入性

### Problem Statement
- 業務場景：對編輯器的修改希望在 CS 升級時最小衝擊，避免直接改第三方檔案。
- 技術挑戰：以 ASP.NET 的 ControlAdapter 或 HttpModule 在外部注入行為。
- 影響範圍：維護成本、升級風險。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：直接改動第三方程式導致升級困難。
- 深層原因：未使用框架提供的擴充管線。

### Solution Design
- 解決策略：定義指定型別的 ControlAdapter，於 Render 前注入自訂腳本/工具列 DOM；或以 HttpModule 注入頁面尾段腳本。

- 實施步驟：
  1. 建立 .browser 對應與 Adapter 類（1 天）
  2. 測試多頁面注入效果（0.5 天）
  3. 升級回歸測試（0.5 天）

- 關鍵程式碼/設定：
```xml
<!-- App_Browsers/Editor.browser -->
<browsers>
  <browser id="Default">
    <controlAdapters>
      <adapter controlType="FreeTextBoxControls.FreeTextBox"
               adapterType="MyApp.FTBAdapter, MyApp" />
    </controlAdapters>
  </browser>
</browsers>
```
```csharp
public class FTBAdapter : System.Web.UI.Adapters.ControlAdapter {
  protected override void Render(HtmlTextWriter writer) {
    base.Render(writer);
    // 追加自訂腳本
    writer.Write("<script>/* 注入工具列或命令 */</script>");
  }
}
```

- 實際案例：所有 FTB 控制項統一注入自訂功能，無需改第三方檔案。
- 實作環境：ASP.NET WebForms
- 實測數據（驗收目標）：
  - 升級衝突 0
  - 新版接入工時下降 ≥ 70%

- Learning Points：ControlAdapter、HttpModule、非侵入式注入
- 技能要求：ASP.NET 管線；進階：跨頁注入策略
- 延伸思考：如何精準篩選頁面？如何做版本檢測與降級？

- Practice：以 HttpModule 在 </form> 前注入初始化腳本
- 評估：注入穩定；升級友好；影響面可控

---

## Case #13: 多語系與在地化資源支援工具列與對話框

### Problem Statement
- 業務場景：平台面向多地區用戶，工具列按鈕與對話框需根據文化設定顯示本地化文字與日期/校驗訊息。
- 技術挑戰：資源管理、文化切換、格式化。
- 影響範圍：使用者體驗與國際化合規。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：按鈕標籤與提示硬編碼。
- 深層原因：未使用 .resx 與文化設定。

### Solution Design
- 解決策略：將文案遷移到 .resx；於 Page.UICulture 切換；JS 端以後端輸出字串或載入 JSON 資源。

- 實施步驟：
  1. 建立 Resources 與鍵值（0.5 天）
  2. Page 設定 UICulture/Culture（0.5 天）
  3. 對話框載入本地化字串（0.5 天）

- 關鍵程式碼/設定：
```csharp
// Page 指定文化
protected override void InitializeCulture() {
  UICulture = Culture = Request.UserLanguages?[0] ?? "zh-TW";
  base.InitializeCulture();
}
// 使用資源
btnInsert.Text = Resources.Editor.InsertImage;
```

- 實際案例：插入圖片對話框文案隨瀏覽器語言切換。
- 實作環境：.NET 資源系統、JS
- 實測數據（驗收目標）：
  - 語系覆蓋率 ≥ 95%
  - 切換延遲 ≈ 0（載入前置）

- Learning Points：.resx、文化設定、JS 國際化
- 技能要求：.NET 資源；進階：I18N 流程
- 延伸思考：是否需 RTL 支援？如何管理翻譯版本？

- Practice：為表情面板新增多語系提示
- 評估：文案可切換；無硬編碼；維護方便

---

## Case #14: 無障礙與鍵盤操作：ARIA/快捷鍵/焦點管理

### Problem Statement
- 業務場景：提升編輯器可及性，支援無障礙規範；提供鍵盤快捷鍵插入圖片/表情。
- 技術挑戰：ARIA 標註、焦點循環、快捷鍵衝突。
- 影響範圍：法規遵循與使用者覆蓋。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：工具列按鈕缺 aria-label；對話框焦點陷阱未處理。
- 深層原因：無障礙未納入設計標準。

### Solution Design
- 解決策略：工具列 role="toolbar"、button aria-label；對話框加焦點陷阱；定義快捷鍵（如 Alt+I 插入圖片）並可在設定中關閉。

- 實施步驟：
  1. ARIA 與語意標記（0.5 天）
  2. 焦點管理與陷阱（0.5 天）
  3. 快捷鍵實作與提示（0.5 天）

- 關鍵程式碼/設定：
```html
<div class="ftb-toolbar" role="toolbar" aria-label="編輯工具列">
  <button type="button" aria-label="插入圖片" id="btnInsertImg">🖼️</button>
</div>
<script>
document.addEventListener('keydown', function(e){
  if (e.altKey && e.key.toLowerCase()==='i') {
    e.preventDefault(); document.getElementById('btnInsertImg').click();
  }
});
</script>
```

- 實際案例：常用操作均有鍵盤路徑，對話框可鍵盤關閉與循環。
- 實作環境：HTML/JS
- 實測數據（驗收目標）：
  - 鍵盤可達率 100%
  - WAI-ARIA linter 無嚴重錯誤

- Learning Points：ARIA、焦點管理、快捷鍵設計
- 技能要求：前端基礎；進階：A11y 測試
- 延伸思考：衝突鍵位管理？螢幕閱讀器相容？

- Practice：為表情面板加鍵盤導航（左右上下）
- 評估：無障礙分數提升；快捷鍵清晰可配

---

## Case #15: 自動化測試與驗收腳本：Selenium 驗證編輯流程

### Problem Statement
- 業務場景：避免回歸時編輯器功能被破壞；建立自動化 UI 測試覆蓋圖片/表情插入與發佈流程。
- 技術挑戰：跨 iframe 操作、等待條件、環境資料隔離。
- 影響範圍：品質、發佈信心。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：手動回歸成本高且易遺漏。
- 深層原因：缺乏可執行的 UI 測試基礎設施。

### Solution Design
- 解決策略：以 Selenium WebDriver 建立端對端測試：登入→開啟編輯→插入圖片/表情→發佈→斷言內容包含 <img> 與 alt。

- 實施步驟：
  1. 測試環境與帳號資料（0.5 天）
  2. 測試腳本與選擇器穩定化（1 天）
  3. CI 整合（0.5 天）

- 關鍵程式碼/設定：
```csharp
[Test]
public void InsertImage_Emote_AndPublish() {
  var d = new ChromeDriver();
  d.Navigate().GoToUrl("https://cs.local/login"); // ...登入略
  d.Navigate().GoToUrl("https://cs.local/new-post");
  // 切到 FTB iframe
  d.SwitchTo().Frame("FreeTextBox1___Frame");
  d.FindElement(By.CssSelector("body")).Click();
  d.SwitchTo().DefaultContent();
  d.FindElement(By.Id("btnInsertImg")).Click();
  // 模擬上傳或輸入 URL 後插入
  // 發佈並驗證
  d.FindElement(By.Id("btnPublish")).Click();
  Assert.IsTrue(d.PageSource.Contains("<img"));
  d.Quit();
}
```

- 實際案例：確保每次發佈流程可插入多媒體且成功呈現。
- 實作環境：Selenium、CI（Azure DevOps/GitHub Actions）
- 實測數據（驗收目標）：
  - 測試穩定通過率 ≥ 95%
  - 單輪測試 < 2 分鐘

- Learning Points：iframe 測試、穩定選擇器、CI 一體化
- 技能要求：測試框架；進階：測試資料管理
- 延伸思考：如何 Mock 上傳？如何做視覺回歸比較？

- Practice：新增 XSS 攻擊樣本自動化測試
- 評估：覆蓋率、穩定性、報告清晰

--------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 7（表情選單）、Case 8（工具列 UX）、Case 10（降級策略）、Case 11（資源優化）、Case 13（多語系）
- 中級（需要一定基礎）
  - Case 1（工具列注入）、Case 2（尋控/反射）、Case 4（FTB 客製命令）、Case 5（插入 API）、Case 6（上傳整合）、Case 14（無障礙）、Case 15（自動化測試）
- 高級（需要深厚經驗）
  - Case 3（Adapter 替換）、Case 12（ControlAdapter/HttpModule 非侵入式架構）、Case 9（安全消毒策略）

2) 按技術領域分類
- 架構設計類：Case 3, 12
- 效能優化類：Case 11
- 整合開發類：Case 1, 4, 6, 7, 8, 10, 13, 14
- 除錯診斷類：Case 2, 5, 15
- 安全防護類：Case 9, 6（上傳驗證也涉資安）

3) 按學習目標分類
- 概念理解型：Case 10, 11, 13, 14
- 技能練習型：Case 1, 4, 5, 7, 8
- 問題解決型：Case 2, 6, 9, 12, 15
- 創新應用型：Case 3（Adapter）、Case 12（無侵入式注入）

--------------------------------
案例關聯圖（學習路徑建議）

- 建議先學順序（由淺入深）：
  1) Case 7（表情選單）→ 2) Case 8（工具列 UX）→ 3) Case 1（工具列注入）
  4) Case 5（插入 API）→ 5) Case 4（FTB 客製命令）→ 6) Case 6（上傳整合）
  7) Case 10（降級策略）→ 8) Case 11（資源優化）→ 9) Case 13（多語系）
  10) Case 14（無障礙）→ 11) Case 2（尋控/反射）→ 12) Case 9（安全消毒）
  13) Case 12（非侵入式注入）→ 14) Case 3（Adapter 替換）→ 15) Case 15（自動化測試）

- 依賴關係：
  - Case 1 依賴 Case 5（插入 API 基礎）
  - Case 4 依賴 Case 5（命令最終插入）
  - Case 6 依賴 Case 1/4/5（對話框插入）、並關聯 Case 9（安全）
  - Case 12 可受益於 Case 2（尋控策略）經驗
  - Case 3 在完成 Case 12 的非侵入式思維後再進行
  - Case 15 覆蓋前述所有功能的驗收

- 完整學習路徑建議：
  - 第一階段（基礎功能）：Case 7 → 8 → 1 → 5 → 4
  - 第二階段（端到端整合）：Case 6 → 10 → 11 → 13 → 14
  - 第三階段（穩定與安全）：Case 2 → 9 → 12
  - 第四階段（架構與品質）：Case 3 → 15

說明：以上案例均以原文的真實困境為核心（CS 使用 FTB 並被 Wrapper 阻隔，導致無法把貼圖/表情整合進原工具列），延展出可操作的解決方案與實作練習，便於實戰教學、專案練習與能力評估。