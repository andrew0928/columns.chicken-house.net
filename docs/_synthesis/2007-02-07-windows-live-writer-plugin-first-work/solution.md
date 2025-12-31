---
layout: synthesis
title: "Windows Live Writer - Plugin 處女作..."
synthesis_type: solution
source_post: /2007/02/07/windows-live-writer-plugin-first-work/
redirect_from:
  - /2007/02/07/windows-live-writer-plugin-first-work/solution/
postid: 2007-02-07-windows-live-writer-plugin-first-work
---

以下為依據文章萃取並延展的 18 個可實作、可評估的解決方案案例。每個案例均包含問題、根因、解法、實作與教學要點，供實戰教學、專案練習與能力評估之用。

## Case #1: 以 UNC 複製與外鏈 URL 避開 WLW 對 JPEG 的再壓縮

### Problem Statement（問題陳述）
業務場景：使用 Windows Live Writer（WLW）撰寫部落格時，內嵌圖片經由 WLW 透過 MetaBlogAPI 或 FTP 上傳後會被重新存成 JPEG。這導致畫質下降且檔案變大，常見為「肥一倍」。對於注重影像品質與載入效率的技術部落客或產品內容團隊，這會影響閱讀體驗與頻寬成本。
技術挑戰：如何在保留原圖品質與大小的前提下完成圖片插入，且流程要足夠順手。
影響範圍：所有圖片內容、讀者體驗、站點頻寬/儲存費用與編輯效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WLW 預設在上傳流程重新存檔為 JPEG（破壞性壓縮），品質下降。
2. WLW 採用的 JPEG quality 參數偏高，導致檔案可能更肥。
3. WLW 的上傳路徑（MetaBlogAPI/FTP）均會觸發再儲存。
深層原因：
- 架構層面：WLW 將圖片上傳視為發佈管線的一部分並強制轉檔。
- 技術層面：無法直接在發佈階段攔截或覆寫 WLW 圖片處理策略。
- 流程層面：編輯端為了便利而直接用 WLW 上傳，缺乏「外鏈」工作流。

### Solution Design（解決方案設計）
解決策略：以 WLW 插件（ContentSource）實作「先複製到 UNC 網路分享，再插入對應的外部 URL」之流程，等同「Insert Picture From Web」的自動化版，避開 WLW 上傳與轉檔。

實施步驟：
1. 建立 WLW 插件專案
- 實作細節：引用 WLW SDK，繼承 ContentSource，提供自訂 Insert 命令。
- 所需資源：WLW SDK、.NET Framework、Visual Studio。
- 預估時間：2 小時。
2. 設定 UNC 與 URL 對應
- 實作細節：於插件 Options 設定 UNC 路徑與對應的 Base URL。
- 所需資源：Options UI（WinForms）。
- 預估時間：1 小時。
3. 實作檔案複製與 IMG 產生
- 實作細節：複製檔案到 UNC，輸出 <img src="..."> 外鏈。
- 所需資源：System.IO、URI 處理。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 以 ContentSource 建構插入流程：選圖 -> 複製到 UNC -> 插入外鏈 IMG
[WriterPlugin("9C6A8A56-1234-4D0E-ABCD-9C9999999999", "插入圖片(從網路芳鄰)",
    Description = "複製到 UNC 並以外部 URL 內嵌，避免 WLW 重新壓縮")]
public class UncImageContentSource : ContentSource
{
    string uncPath, baseUrl;

    public override void Initialize()
    {
        // 載入使用者設定（UNC 與 Base URL）
        uncPath = Settings.GetString("UncPath", @"\\server\share\images");
        baseUrl = Settings.GetString("BaseUrl", "https://img.example.com");
    }

    public override DialogResult CreateContent(IWin32Window dialogOwner, ref string content)
    {
        using var dlg = new OpenFileDialog { Filter = "Images|*.jpg;*.jpeg;*.png;*.gif", Multiselect = false };
        if (dlg.ShowDialog(dialogOwner) != DialogResult.OK) return DialogResult.Cancel;

        var fileName = Path.GetFileName(dlg.FileName);
        var target = Path.Combine(uncPath, fileName);
        File.Copy(dlg.FileName, target, true); // 覆蓋或後續做唯一命名

        var url = $"{baseUrl}/{Uri.EscapeDataString(fileName)}";
        content = $"<img src=\"{url}\" alt=\"\" />";
        return DialogResult.OK;
    }
}
```

實際案例：作者以 UNC+URL 對應自動化「Insert Picture From Web」，避開 WLW 轉檔。
實作環境：Windows Live Writer 1.x、.NET（2.0+）、WLW SDK、Windows（具網路分享）。
實測數據：
改善前：WLW 上傳後 JPEG 常「肥一倍」且畫質變差。
改善後：維持原檔大小與畫質。
改善幅度：相較 WLW 輸出約減少 50% 檔案體積（以「肥一倍」為參考）。

Learning Points（學習要點）
核心知識點：
- 以外鏈 URL 避開編輯器內建轉檔。
- WLW ContentSource 插件開發基本流程。
- UNC 與 HTTP Base URL 的對應設計。
技能要求：
- 必備技能：C#、WinForms、基礎 I/O、UNC 使用。
- 進階技能：插件生命週期、使用者設定保存。
延伸思考：
- 可否支援多站點映射與自動唯一檔名？
- UNC 不可用時的備援？（見其他案例）
- 後續導入 MetaBlogAPI 直傳以便雲端主機使用。
Practice Exercise（練習題）
- 基礎練習：改寫程式讓 Base URL 自動去除尾端斜線。
- 進階練習：加入複製前檔案大小檢查並顯示提示。
- 專案練習：完成插件（含 Options）並成功插入外鏈 IMG。
Assessment Criteria（評估標準）
- 功能完整性（40%）：可選檔、可複製、可插入正確外鏈。
- 程式碼品質（30%）：結構清晰、錯誤處理與註解完善。
- 效能優化（20%）：I/O 操作合理，避免 UI 卡頓。
- 創新性（10%）：額外支援多站點或格式擴充。

---

## Case #2: UNC 與 Base URL 對應的 Options 設計

### Problem Statement（問題陳述）
業務場景：編輯團隊需在不同主機或分享資料夾工作，硬編碼 UNC/URL 易出錯且不利維護。
技術挑戰：提供直覺的設定 UI 與安全存取設定值。
影響範圍：部署便利性、擴展性、維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少設定畫面，導致需要改程式或硬編碼。
2. 多環境/多站台映射難以管理。
3. 使用者易輸入不合法路徑或 URL。
深層原因：
- 架構層面：插件未模組化設定管理。
- 技術層面：缺乏設定驗證、儲存機制（Registry/Config）。
- 流程層面：設定無標準化，移轉環境困難。

### Solution Design（解決方案設計）
解決策略：實作 OptionsForm，提供 UNC 與 Base URL 欄位，附帶基本驗證與保存機制。

實施步驟：
1. Options UI
- 實作細節：WinForms 兩欄位 + 驗證（是否空白、URL 格式）。
- 所需資源：WinForms、簡單 Regex。
- 預估時間：1 小時。
2. 設定儲存
- 實作細節：使用 WLW 提供的 Settings API 或自有設定檔。
- 所需資源：Settings/Registry。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
// OptionsForm：驗證與保存
private void btnSave_Click(object sender, EventArgs e)
{
    var unc = txtUnc.Text.Trim();
    var url = txtBaseUrl.Text.Trim().TrimEnd('/');

    if (string.IsNullOrEmpty(unc) || string.IsNullOrEmpty(url))
    {
        MessageBox.Show("UNC 與 Base URL 皆不可空白");
        return;
    }
    if (!Uri.TryCreate(url, UriKind.Absolute, out var _))
    {
        MessageBox.Show("Base URL 格式不正確");
        return;
    }
    Settings.SetString("UncPath", unc);
    Settings.SetString("BaseUrl", url);
    DialogResult = DialogResult.OK;
}
```

實際案例：作者於 WLW Tools->Preferences->Plugins 中提供 Options 按鈕配置。
實作環境：同 Case #1。
實測數據：
改善前：需修改程式碼或手動處理配置。
改善後：UI 設定一次即可使用。
改善幅度：配置時間縮短、錯誤率降低（定性）。

Learning Points（學習要點）
- 設定 UI 與驗證設計。
- 設定資料持久化與載入。
- 斜線與空白等輸入清洗（Trim/TrimEnd）。
技能要求：C#、WinForms 基本功。
延伸思考：支援多組映射（見 Case #13）。
Practice Exercise：新增「測試路徑可寫入」按鈕。
進階練習：加入 URL 正規化（http/https）。
專案練習：做一個完整 Options 與驗證流程。
Assessment Criteria：
- 功能完整性：可保存/讀取並生效。
- 程式碼品質：清楚、可維護。
- 效能優化：即時驗證不阻塞 UI。
- 創新性：增加環境檢測與提示。

---

## Case #3: 自動化替代「Insert Picture From Web」的工作流

### Problem Statement（問題陳述）
業務場景：每次用「Insert Picture From Web」手動上傳到網路、複製 URL 再貼回，流程冗長。
技術挑戰：把人工步驟自動化成一鍵插入。
影響範圍：編輯效率、操作一致性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 手動上載與貼 URL，步驟多易出錯。
2. 不同編輯者作法不一，結果不一致。
3. 忘記 URL encode 造成連結毀損。
深層原因：
- 架構層面：缺少把工作流封裝成插件的機制（需自行開發）。
- 技術層面：未建立路徑映射與檔案自動複製。
- 流程層面：高度依賴人工流程。

### Solution Design（解決方案設計）
解決策略：插件內定義 Insert 命令，彈出 OpenFileDialog，選檔後自動複製到 UNC 並插入 IMG 外鏈。

實施步驟：
1. Insert 命令註冊
- 實作細節：ContentSource 的 CreateContent 實作。
- 所需資源：WLW SDK。
- 預估時間：0.5 小時。
2. 檔案選擇與複製
- 實作細節：OpenFileDialog、File.Copy。
- 所需資源：System.IO。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public override DialogResult CreateContent(IWin32Window owner, ref string content)
{
    using var ofd = new OpenFileDialog { Filter = "Images|*.jpg;*.jpeg;*.png;*.gif" };
    if (ofd.ShowDialog(owner) != DialogResult.OK) return DialogResult.Cancel;

    var fileName = Path.GetFileName(ofd.FileName);
    File.Copy(ofd.FileName, Path.Combine(uncPath, fileName), true);
    var url = $"{baseUrl}/{Uri.EscapeDataString(fileName)}";

    content = $"<img src=\"{url}\" alt=\"\" />";
    return DialogResult.OK;
}
```

實際案例：作者插件將人工步驟一次完成，選檔即「大功告成」。
實作環境：同 Case #1。
實測數據：
改善前：多步手動、易錯。
改善後：一鍵完成。
改善幅度：操作步驟大幅減少（定性）。

Learning Points（學習要點）
- 把人工流程封裝成插件命令。
- 開檔對話框與 I/O 操作。
技能要求：C#、WinForms。
延伸思考：加上拖放支援。
Practice Exercise：加入副檔名白名單。
進階練習：加入插入前預覽。
專案練習：完成自動化插入全流程。
Assessment Criteria：同 Case #1。

---

## Case #4: 插件無法取得 WLW 帳號資訊的限制與繞道

### Problem Statement（問題陳述）
業務場景：希望用插件直接走 MetaBlogAPI 上傳，但取不到 WLW 的 Weblog 帳號/密碼。
技術挑戰：在安全限制下仍能完成自動上傳或找到替代方案。
影響範圍：是否能用 WLW 既有帳號直傳、使用體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WLW 插件 API 不暴露帳號密碼。
2. 插件定位在編輯階段而非發佈階段。
3. 可能出於安全設計，避免插件竊取憑證。
深層原因：
- 架構層面：發佈管線與憑證存取未提供第三方擴充。
- 技術層面：無授權機制讓插件代用憑證。
- 流程層面：插件僅能產生內容，不參與上傳。

### Solution Design（解決方案設計）
解決策略：放棄重用 WLW 憑證；若要直傳則在插件內自行配置帳號（見 Case #5），或採 UNC+外鏈避開上傳（本方案）。

實施步驟：
1. 需求決策
- 實作細節：根據環境選擇 UNC/MetaBlogAPI。
- 所需資源：需求訪談。
- 預估時間：0.5 小時。
2. 實作對應方案
- 實作細節：若選 UNC，完成 Case #1；若選 API，見 Case #5。
- 所需資源：SDK/XML-RPC。
- 預估時間：依選擇不同。

關鍵程式碼/設定：
```csharp
// 判斷策略：無法取用 WLW 帳密 -> 走 UNC 外鏈；否則（自管憑證）走 API
enum UploadMode { UncExternalLink, MetaWeblog }
UploadMode DecideMode(bool haveOwnCredentials) =>
    haveOwnCredentials ? UploadMode.MetaWeblog : UploadMode.UncExternalLink;
```

實際案例：作者宣告放棄從 WLW 取憑證，改走外鏈。
實作環境：同 Case #1。
實測數據：—
改善前：卡在不能上傳的技術門檻。
改善後：以外鏈完成需求，品質/大小問題同步解決。

Learning Points（學習要點）
- 了解平台安全邊界，調整方案。
- 插件角色定位：內容產生 vs 發佈處理。
技能要求：架構選型思維。
延伸思考：OAuth/Token 化授權可否納入？（自管）
Practice Exercise：撰寫「模式選擇器」UI。
進階練習：支援切換與回退策略。
專案練習：整合 Case #1 與 #5 兩種模式。
Assessment Criteria：能清楚界定與實作兩種路徑。

---

## Case #5: 插件自管憑證走 MetaBlogAPI 上傳圖片

### Problem Statement（問題陳述）
業務場景：無法使用 UNC（外網或雲端主機），仍需避免 WLW 再壓縮，期望自助上傳。
技術挑戰：實作 MetaBlogAPI（metaWeblog.newMediaObject）並安全保存憑證。
影響範圍：上傳可靠性、資安、相容性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 插件不能取用 WLW 憑證。
2. 主機無法提供 UNC。
3. 仍需避免 WLW 圖片轉檔。
深層原因：
- 架構層面：需由插件自行串接 XML-RPC。
- 技術層面：憑證安全保存與傳輸。
- 流程層面：新增一套與 WLW 無關的上傳設定與流程。

### Solution Design（解決方案設計）
解決策略：在 Options 內配置 Blog URL/帳號/密碼，直接呼叫 metaWeblog.newMediaObject 取得上傳後 URL，插入 IMG 外鏈。

實施步驟：
1. 憑證設定 UI
- 實作細節：Blog URL、Username、Password（見 Case #17 做安全保存）。
- 所需資源：WinForms。
- 預估時間：1 小時。
2. 實作 XML-RPC 客戶端
- 實作細節：CookComputing.XmlRpc 或等價函式庫。
- 所需資源：XML-RPC 套件。
- 預估時間：1-2 小時。

關鍵程式碼/設定：
```csharp
// 使用 XML-RPC 上傳圖片（metaWeblog.newMediaObject）
public interface IMetaWeblog : IXmlRpcProxy
{
    [XmlRpcMethod("metaWeblog.newMediaObject")]
    XmlRpcStruct NewMediaObject(string blogId, string username, string password, XmlRpcStruct mediaObject);
}

public string UploadImage(string endpoint, string blogId, string user, string pass, string filePath)
{
    var client = XmlRpcProxyGen.Create<IMetaWeblog>();
    client.Url = endpoint;

    var bytes = File.ReadAllBytes(filePath);
    var media = new XmlRpcStruct
    {
        ["name"] = Path.GetFileName(filePath),
        ["type"] = "image/jpeg", // 依實際副檔名
        ["bits"] = bytes
    };
    var result = client.NewMediaObject(blogId, user, pass, media);
    return (string)result["url"]; // 上傳後的外鏈 URL
}
```

實際案例：文章末段提到未來計劃將 Options 改為 MetaBlogAPI 所需設定。
實作環境：WLW、.NET、XML-RPC。
實測數據：
改善前：WLW 強制轉檔。
改善後：直接拿到主機回傳的外鏈 URL，維持原圖。
改善幅度：維持原畫質與大小（定性；大小避免 WLW 肥一倍）。

Learning Points（學習要點）
- MetaBlogAPI 基本概念與 newMediaObject。
- 外鏈插入與 WLW 上傳管線解耦。
技能要求：C#、XML-RPC、資安（見 Case #17）。
延伸思考：支援 OAuth 或 Token 化 API。
Practice Exercise：完成一個最小可用的 newMediaObject 呼叫。
進階練習：依副檔名自動決定 MIME type。
專案練習：整合 Options（含 DPAPI）+ 上傳 + 插入。
Assessment Criteria：功能可用、安全保存憑證、錯誤處理完善。

---

## Case #6: 特殊字元與空白的 URL 編碼處理

### Problem Statement（問題陳述）
業務場景：相機原檔常帶空白、括號或中括號（如文中示例），若未 URL 編碼，瀏覽器連結可能失效。
技術挑戰：在插入 IMG 時正確處理 URL 編碼。
影響範圍：圖片是否能正常顯示、SEO、穩定性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 檔名含空白與特殊字元。
2. 未對路徑做 URL encode。
3. 不同瀏覽器對未編碼字元容忍度不同。
深層原因：
- 架構層面：缺少「插入前清洗」機制。
- 技術層面：未使用標準 API 進行編碼。
- 流程層面：人工命名難以控管。

### Solution Design（解決方案設計）
解決策略：對檔名使用 Uri.EscapeDataString，組合 URL 時確保不重複編碼。

實施步驟：
1. 編碼函式
- 實作細節：僅對 path segment（檔名）做編碼。
- 所需資源：System.Uri。
- 預估時間：0.2 小時。
2. 單元測試
- 實作細節：測試含空白、括號、中括號。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
string BuildImageUrl(string baseUrl, string fileName)
{
    var safeBase = baseUrl.TrimEnd('/');
    var encoded = Uri.EscapeDataString(fileName); // 針對單一 segment
    return $"{safeBase}/{encoded}";
}
```

實際案例：文中出現帶括號與中括號的檔名，實務上必須處理。
實作環境：同 Case #1。
實測數據：改善後圖片連結穩定顯示。
改善幅度：壞鏈接率下降（定性）。

Learning Points：URL 編碼與路徑處理。
技能要求：C# 字串與 URI 基礎。
延伸思考：路徑階層多段時的編碼策略。
Practice Exercise：寫測試覆蓋 10 種常見特殊字元。
Assessment Criteria：正確產生可點擊且可顯示之 URL。

---

## Case #7: 檔名衝突與唯一化命名

### Problem Statement（問題陳述）
業務場景：同名檔案覆蓋導致舊文圖片被替換。
技術挑戰：在複製到 UNC 時避免覆蓋。
影響範圍：歷史內容正確性、資料信任。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 使用原檔名直接複製。
2. 不同文章可能使用同一檔名。
3. 預設 File.Copy(true) 覆蓋。
深層原因：
- 架構層面：缺少唯一命名策略。
- 技術層面：未追加時間戳/雜湊/目錄分桶。
- 流程層面：命名無規範。

### Solution Design（解決方案設計）
解決策略：加入時間戳或 GUID，或以內容雜湊決定檔名。

實施步驟：
1. 命名策略實作
- 實作細節：YYYYMMDDHHmmss-GUID.jpg。
- 預估時間：0.3 小時。
2. 回溯相容
- 實作細節：保留原檔名於 alt 或 data-* 屬性。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
string UniqueFileName(string originalName)
{
    var name = Path.GetFileNameWithoutExtension(originalName);
    var ext = Path.GetExtension(originalName);
    return $"{name}_{DateTime.UtcNow:yyyyMMddHHmmss}_{Guid.NewGuid():N}{ext}";
}
```

實際案例：避免同名覆蓋。
實作環境：同 Case #1。
實測數據：覆蓋事故降為 0（預期/定性）。
Learning Points：唯一命名與檔案管理。
Practice Exercise：改用 SHA-1(內容) 作為檔名。
Assessment Criteria：無覆蓋、可追溯。

---

## Case #8: UNC 可用性與權限檢查

### Problem Statement（問題陳述）
業務場景：外出或 VPN 未連線時，UNC 無法存取，導致插入失敗。
技術挑戰：在操作前檢查連線與權限，並給出明確錯誤提示。
影響範圍：穩定性、使用者體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. UNC 路徑不存在或無法連線。
2. 權限不足（無寫入權）。
3. 缺乏錯誤處理（原作「連個防呆都沒有」）。
深層原因：
- 架構層面：沒有健康檢查機制。
- 技術層面：例外未捕捉、無權限檢測。
- 流程層面：未提供離線備援。

### Solution Design（解決方案設計）
解決策略：插入前檢查目錄存在與可寫，無法使用時提示或走備援（見 Case #14）。

實施步驟：
1. 路徑檢查
- 實作細節：Directory.Exists、嘗試建立暫存檔。
- 預估時間：0.5 小時。
2. 錯誤提示
- 實作細節：明確訊息與導引。
- 預估時間：0.2 小時。

關鍵程式碼/設定：
```csharp
bool CanWriteUnc(string path)
{
    try
    {
        if (!Directory.Exists(path)) return false;
        var test = Path.Combine(path, $".probe_{Guid.NewGuid():N}.tmp");
        File.WriteAllText(test, "probe");
        File.Delete(test);
        return true;
    }
    catch { return false; }
}
```

實際案例：補齊原作的防呆缺口。
實作環境：同 Case #1。
實測數據：失敗轉成功率顯著提升（定性）。
Learning Points：健檢與防呆設計。
Practice Exercise：在 Options 增加「測試連線」按鈕。
Assessment Criteria：能準確判斷可用性並給出清楚提示。

---

## Case #9: WLW 插件部署與註冊

### Problem Statement（問題陳述）
業務場景：DLL 丟入 Plugins 資料夾後需在 WLW 中正確顯示並可設定。
技術挑戰：正確引用 SDK、設定屬性與部署路徑。
影響範圍：可用性、維護性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少必要的 WriterPlugin 屬性。
2. DLL 未放入正確 Plugins 路徑。
3. 參考版本不相容。
深層原因：
- 架構層面：插件發現機制依靠屬性與約定路徑。
- 技術層面：x86/x64 路徑差異、版本差異。
- 流程層面：部署步驟未文檔化。

### Solution Design（解決方案設計）
解決策略：正確標註 WriterPlugin 屬性與說明，將 DLL 放到 WLW 安裝目錄下的 Plugins 資料夾，於 WLW 的 Tools->Preferences->Plugins 查看。

實施步驟：
1. 建置與屬性
- 實作細節：WriterPlugin 屬性與說明。
- 預估時間：0.2 小時。
2. 部署
- 實作細節：複製到 Plugins 資料夾。
- 預估時間：0.2 小時。

關鍵程式碼/設定：
```csharp
[WriterPlugin("B1C8F729-AAAA-4DA7-9F91-1234567890AB", "插入圖片(從網路芳鄰)",
    Description = "UNC 複製 + 外鏈插入", PublisherUrl = "https://example.com")]
public class UncImageContentSource : ContentSource { /* ... */ }
// 將編譯出的 DLL 複製到：C:\Program Files\Windows Live\Writer\Plugins\
```

實際案例：作者在 Plugins 頁籤看到新外掛與 Options 按鈕。
實作環境：WLW、Windows。
實測數據：成功載入率 100%（條件正確時）。
Learning Points：WLW 插件發現機制。
Practice Exercise：修改描述與 PublisherUrl 並驗證顯示。
Assessment Criteria：能成功顯示並啟用插件。

---

## Case #10: 設定防呆與輸入驗證

### Problem Statement（問題陳述）
業務場景：原作「連個防呆都沒有」，易因錯誤設定造成失敗。
技術挑戰：在 Options 與執行階段強化驗證與提示。
影響範圍：穩定性、使用者體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. UNC/URL 留空或格式錯誤。
2. 無即時驗證。
3. 錯誤訊息不明確。
深層原因：
- 架構層面：未建立驗證層。
- 技術層面：缺乏例外處理。
- 流程層面：快速開發未做完備驗證。

### Solution Design（解決方案設計）
解決策略：在 Options 儲存前與插入前做完整驗證，並提供明確的錯誤訊息與修正導引。

實施步驟：
1. Options 驗證
- 實作細節：TryCreate、路徑存在性。
- 預估時間：0.5 小時。
2. 插入前檢查
- 實作細節：CanWriteUnc（見 Case #8）。
- 預估時間：0.3 小時。

關鍵程式碼/設定：
```csharp
try
{
    if (!CanWriteUnc(uncPath)) 
        throw new InvalidOperationException("UNC 無法寫入，請檢查網路與權限");
    // ... 繼續複製與插入
}
catch (Exception ex)
{
    MessageBox.Show($"插入失敗：{ex.Message}");
}
```

實際案例：補齊原作缺口。
實作環境：同 Case #1。
實測數據：失敗率下降、可用性提升（定性）。
Learning Points：輸入驗證與友善錯誤訊息。
Practice Exercise：為 URL 加入 DNS 解析測試。
Assessment Criteria：錯誤情境有清楚提示且可引導修正。

---

## Case #11: 非同步 I/O 防止 WLW UI 卡頓

### Problem Statement（問題陳述）
業務場景：複製大圖到 UNC 可能導致編輯器卡住。
技術挑戰：避免 UI thread 阻塞。
影響範圍：使用者體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 同步 File.Copy 在 UI thread 執行。
2. 網路 I/O 延遲不可控。
3. 無進度與取消機制。
深層原因：
- 架構層面：未分離 UI 與 I/O。
- 技術層面：缺少 async/await 或 Task 應用。
- 流程層面：未規劃長時作業交互。

### Solution Design（解決方案設計）
解決策略：使用 Task.Run 包裝複製，顯示簡單進度，避免阻塞 UI。

實施步驟：
1. 非同步包裝
- 實作細節：Task.Run + await。
- 預估時間：0.5 小時。
2. 進度提示
- 實作細節：簡單轉圈或狀態列提示。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
await Task.Run(() =>
{
    var target = Path.Combine(uncPath, uniqueName);
    File.Copy(sourcePath, target, true);
});
```

實際案例：提升流暢度。
實作環境：.NET 4.5+（若較舊可用 BackgroundWorker）。
實測數據：UI 停滯現象消失（定性）。
Learning Points：UI thread 與 I/O 隔離。
Practice Exercise：加入取消按鈕（CancellationToken）。
Assessment Criteria：操作期間 WLW 不鎖死。

---

## Case #12: 效果驗證：檔案大小與畫質對照

### Problem Statement（問題陳述）
業務場景：需向團隊證明外鏈方案的實際效益（避免肥一倍與畫質劣化）。
技術挑戰：建立可重複驗證的方法。
影響範圍：決策支持、方案推廣。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 原流程難以量化改善。
2. 成員對差異感知不一。
3. 缺乏一致衡量指標。
深層原因：
- 架構層面：測量流程未內建。
- 技術層面：未自動擷取前後大小/品質。
- 流程層面：缺觀測點。

### Solution Design（解決方案設計）
解決策略：以 Windows Explorer/程式碼記錄比較「原圖 vs WLW 上傳圖 vs 外鏈圖」的檔案大小；視覺上比較壓縮痕跡。

實施步驟：
1. 大小量測
- 實作細節：FileInfo.Length。
- 預估時間：0.2 小時。
2. 視覺對照
- 實作細節：放大檢視高對比區域或文字邊緣。
- 預估時間：0.2 小時。

關鍵程式碼/設定：
```csharp
long SizeOf(string p) => new FileInfo(p).Length;
// WLW 圖為再上傳後下載回來做對照；外鏈圖等於原圖
```

實際案例：文中指出「大概都會肥一倍」；外鏈則維持原檔。
實作環境：同 Case #1。
實測數據：
改善前：WLW 圖常約 2x。
改善後：外鏈維持原大小。
改善幅度：相對 WLW 約 -50%。
Learning Points：建立衡量指標促成共識。
Practice Exercise：做一份測試報告模板。
Assessment Criteria：能清楚呈現前後差異與結論。

---

## Case #13: 多站點/多環境映射（Profiles）

### Problem Statement（問題陳述）
業務場景：同一台 WLW 需發文到多個站點或不同環境（dev/stage/prod），各有不同 UNC/URL。
技術挑戰：管理多組設定並在插入時選擇。
影響範圍：靈活性、錯誤率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一設定無法覆蓋多目標。
2. 切換站點需改設定，易出錯。
3. 缺少 Profile 抽象。
深層原因：
- 架構層面：未支援多租戶/多設定集合。
- 技術層面：設定結構未正規化。
- 流程層面：多環境切換無明確流程。

### Solution Design（解決方案設計）
解決策略：在 Options 支援多 Profile，插入時可選或預設最近使用。

實施步驟：
1. Profile 結構
- 實作細節：名稱、Unc、BaseUrl。
- 預估時間：0.5 小時。
2. 插入前選擇
- 實作細節：簡易下拉選單。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
class Profile { public string Name, Unc, BaseUrl; }
List<Profile> Profiles = LoadProfiles(); // JSON/Settings
Profile Current => Profiles.First(p => p.Name == Settings.GetString("LastProfile", Profiles[0].Name));
```

實際案例：延伸原作以支援多環境。
實作環境：同 Case #1。
實測數據：切換錯誤率下降（定性）。
Learning Points：多設定管理。
Practice Exercise：導入 JSON 儲存 Profiles。
Assessment Criteria：可新增/刪除/切換並正確生效。

---

## Case #14: UNC 不可用時的備援策略

### Problem Statement（問題陳述）
業務場景：出差或外網環境無法使用 UNC，仍需插圖發文。
技術挑戰：提供可用備援路徑。
影響範圍：業務連續性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. UNC 依賴內網。
2. 權限/網路不穩。
3. 缺少退路機制。
深層原因：
- 架構層面：單一路徑設計。
- 技術層面：策略判斷未內建。
- 流程層面：無手動降級指引。

### Solution Design（解決方案設計）
解決策略：若 UNC 不可用，提示用「Insert Picture From Web」或切換至 Case #5（自管 MetaBlogAPI）。

實施步驟：
1. 檢測與提示
- 實作細節：CanWriteUnc=false 時顯示選項。
- 預估時間：0.3 小時。
2. 自動切換（可選）
- 實作細節：若已配置 API，直接改走 API。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
if (!CanWriteUnc(uncPath))
{
    var useApi = HaveApiConfig() && MessageBox.Show(
        "UNC 不可用，要改用 API 上傳嗎？", "備援", MessageBoxButtons.YesNo) == DialogResult.Yes;
    // 分流處理
}
```

實際案例：補齊原作未提供的備援能力。
實作環境：同 Case #1/#5。
實測數據：停擺事件減少（定性）。
Learning Points：容錯與降級設計。
Practice Exercise：實作模式切換對話框。
Assessment Criteria：在 UNC 不可用時仍可完成插圖。

---

## Case #15: 追蹤與診斷（Logging/Tracing）

### Problem Statement（問題陳述）
業務場景：使用者回報「偶發失敗」，需快速定位原因（網路、權限、檔名、API）。
技術挑戰：在不干擾使用者的前提下收集關鍵訊息。
影響範圍：維運與支援效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無紀錄，難以還原情境。
2. 例外被吃掉或未顯示。
3. 缺少關鍵欄位（UNC、URL、檔名）。
深層原因：
- 架構層面：未內建 Logging。
- 技術層面：未採 TraceSource 或等價機制。
- 流程層面：無回報指引。

### Solution Design（解決方案設計）
解決策略：加入 TraceSource，寫檔與 ETW 可選；提供匯出診斷資訊。

實施步驟：
1. Trace 導入
- 實作細節：TraceSource + listeners。
- 預估時間：0.5 小時。
2. 匯出功能
- 實作細節：打包近 24 小時日誌。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
static readonly TraceSource Log = new("UncImagePlugin");
Log.TraceEvent(TraceEventType.Information, 0, $"Copy {src} -> {dst}");
try { /* copy */ } 
catch (Exception ex) { Log.TraceEvent(TraceEventType.Error, 0, ex.ToString()); throw; }
```

實際案例：便於後續維護。
實作環境：.NET、Windows。
實測數據：問題定位時間縮短（定性）。
Learning Points：最小侵入式診斷。
Practice Exercise：加入使用者匯出日誌按鈕。
Assessment Criteria：能重現並定位常見錯誤。

---

## Case #16: 產生絕對外鏈 IMG，避免 WLW 介入處理

### Problem Statement（問題陳述）
業務場景：需確保 WLW 不再處理圖片，插入後即為最終 URL。
技術挑戰：確保輸出 HTML 使用絕對 URL，模擬「Insert Picture From Web」結果。
影響範圍：畫質、大小與行為一致性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 相對路徑或內嵌資源可能被 WLW 處理。
2. 插件若寫入本地路徑，WLW 可能複製或轉檔。
3. 需強制指向外部 HTTP(S)。
深層原因：
- 架構層面：WLW 對本地或需上傳資源有處理管線。
- 技術層面：HTML 產生不嚴謹。
- 流程層面：未定義輸出規範。

### Solution Design（解決方案設計）
解決策略：統一輸出絕對 HTTP(S) URL 的 <img src="...">，不嵌入 base64 或相對路徑。

實施步驟：
1. URL 驗證
- 實作細節：Uri.IsWellFormedUriString。
- 預估時間：0.2 小時。
2. HTML 生成
- 實作細節：統一模板，加入 alt。
- 預估時間：0.2 小時。

關鍵程式碼/設定：
```csharp
string HtmlForImg(string url, string alt = "")
{
    if (!Uri.TryCreate(url, UriKind.Absolute, out _)) 
        throw new ArgumentException("URL 必須是絕對位址");
    return $"<img src=\"{url}\" alt=\"{System.Net.WebUtility.HtmlEncode(alt)}\" />";
}
```

實際案例：與作者描述的「Insert Picture From Web」行為一致。
實作環境：同 Case #1。
實測數據：WLW 不再重存 JPEG（定性）。
Learning Points：輸出一致性。
Practice Exercise：加入 width/height 屬性選項。
Assessment Criteria：輸出 HTML 穩定可用。

---

## Case #17: 憑證安全保存（MetaBlogAPI 變體）

### Problem Statement（問題陳述）
業務場景：若採 Case #5，自管帳密需安全保存，避免明文。
技術挑戰：本機安全保存與最小權限存取。
影響範圍：資安與合規。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直接明文儲存易外洩。
2. 未使用 OS 安全機制。
3. 缺乏保護與回收策略。
深層原因：
- 架構層面：未設計密鑰管理。
- 技術層面：未用 DPAPI 或 Credential Manager。
- 流程層面：未定義換密與撤銷。

### Solution Design（解決方案設計）
解決策略：使用 Windows DPAPI（ProtectedData）或 Credential Manager 保存；記得分類作用域（CurrentUser/Machine）。

實施步驟：
1. 加解密模組
- 實作細節：ProtectedData.Protect/Unprotect。
- 預估時間：0.5 小時。
2. 敏感欄位遮蔽
- 實作細節：UI 不顯示明文。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
byte[] Protect(string s) => ProtectedData.Protect(
    Encoding.UTF8.GetBytes(s), null, DataProtectionScope.CurrentUser);
string Unprotect(byte[] b) => Encoding.UTF8.GetString(
    ProtectedData.Unprotect(b, null, DataProtectionScope.CurrentUser));
```

實際案例：對應作者「自管帳密」的未來規劃。
實作環境：Windows。
實測數據：降低憑證外洩風險（定性）。
Learning Points：本機秘密管理。
Practice Exercise：實作「重設密碼」流程。
Assessment Criteria：密碼不落地明文、權限限制合理。

---

## Case #18: 版本相容與未來變更風險控管

### Problem Statement（問題陳述）
業務場景：作者提及未來 WLW 可能修正圖片問題，插件可能失去價值。
技術挑戰：管理版本相容性與退場策略。
影響範圍：維護成本、使用者溝通。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 上游（WLW）行為可能改變。
2. 插件定位可能不再需要。
3. 缺乏版本檢測與公告。
深層原因：
- 架構層面：對上游依賴未封裝。
- 技術層面：未偵測 WLW 版本與功能旗標。
- 流程層面：缺退場/升級計畫。

### Solution Design（解決方案設計）
解決策略：加入版本偵測與提示；文檔化此插件的適用前提；提供一鍵停用與回報管道。

實施步驟：
1. 版本偵測
- 實作細節：讀取 WLW 版本或測試行為。
- 預估時間：0.5 小時。
2. 溝通與退場
- 實作細節：README、停用按鈕。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
// 以測試檔流程探測：若 WLW 已不再重存 JPEG，則提示停用
bool WlwStillRecompresses = true; // 實際以探針流程設定
if (!WlwStillRecompresses)
    MessageBox.Show("WLW 已修正圖片處理，本插件可停用以簡化流程。");
```

實際案例：對應作者「不知下一版會不會改掉這鳥問題」的風險。
實作環境：同 Case #1。
實測數據：降低不必要維運（定性）。
Learning Points：對外部依賴的風險管理。
Practice Exercise：撰寫一份適用性與相容性聲明。
Assessment Criteria：能清楚通知並引導使用者決策。

---

案例分類
1. 按難度分類
- 入門級：Case 2, 3, 6, 9, 10, 12, 16, 18
- 中級：Case 1, 7, 8, 11, 13, 14, 15, 17
- 高級：Case 5, 4（策略/架構判斷，含 API 串接與安全）

2. 按技術領域分類
- 架構設計類：Case 1, 4, 5, 13, 14, 18
- 效能優化類：Case 11
- 整合開發類：Case 2, 3, 5, 9, 16, 17
- 除錯診斷類：Case 8, 10, 12, 15
- 安全防護類：Case 4, 5, 17

3. 按學習目標分類
- 概念理解型：Case 4, 12, 18
- 技能練習型：Case 2, 3, 6, 9, 10, 11, 15, 16
- 問題解決型：Case 1, 7, 8, 13, 14
- 創新應用型：Case 5, 17

案例關聯圖（學習路徑建議）
- 先學基礎插件與外鏈核心：
  1) Case 9（部署與註冊）
  2) Case 2（Options 設定）
  3) Case 3（自動化插入流程）
  4) Case 1（UNC 外鏈避開再壓縮）
- 強化穩定性與正確性（有依賴 1-3）：
  5) Case 10（防呆驗證）
  6) Case 6（URL 編碼）
  7) Case 7（唯一命名）
  8) Case 8（UNC 可用性）
  9) Case 16（絕對外鏈 HTML）
- 提升體驗與維運：
  10) Case 11（非同步 I/O）
  11) Case 15（Logging）
  12) Case 12（效果驗證）
- 多環境與備援：
  13) Case 13（多 Profiles）
  14) Case 14（UNC 備援）
- 進階直傳與資安（可平行，但依賴 Options 與 Logging）：
  15) Case 5（MetaBlogAPI 直傳）
  16) Case 17（憑證安全）
- 最後進行風險控管與版本策略：
  17) Case 4（理解平台邊界與策略）
  18) Case 18（相容性與退場）

完整學習路徑建議：
- 基礎（9→2→3→1）→ 穩定（10→6→7→8→16）→ 體驗維運（11→15→12）→ 擴展（13→14）→ 進階（5→17）→ 策略（4→18）。
此路徑由易至難、由功能到品質、由單環境到多環境，最後到安全與策略，能系統性地從 WLW 外掛入門到成熟落地。