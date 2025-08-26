以下內容基於原文中實際提及的問題、原因、解法與效益，萃取並延伸為可教學、可實作的完整案例。每個案例皆可獨立練習與評估，並相互組成學習路徑。

## Case #1: c720w 出廠預設值後預載軟體缺失的恢復流程

### Problem Statement（問題陳述）
業務場景：使用者對 Dopod c720w 進行恢復出廠設定後，發現語音命令、字典、附贈遊戲與 RSS reader 等預載軟體消失。透過客服往返多封信後，官方才釋出需手動安裝的配套軟體，使用者需要一套標準化的恢復流程確保裝置回復到購入時狀態。
技術挑戰：缺乏集中式的 OEM 軟體包與自動化安裝程序；手動安裝順序、相依性與授權問題。
影響範圍：功能缺失、使用體驗下降、維運成本提高、客服量增加。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 官方未及時提供 c720w 專用的恢復安裝包，導致使用者無法快速復原。
2. 缺乏自動化安裝機制，需逐一安裝多個 OEM CAB。
3. 相依性與順序未文檔化，容易出錯。
深層原因：
- 架構層面：未設計開機自動佈署（Extended ROM/Provisioning）機制。
- 技術層面：安裝包缺乏條件化與簽章管理，難以一次到位。
- 流程層面：客服與官網釋出缺乏 SLA 與標準作業程序。

### Solution Design（解決方案設計）
解決策略：建立 c720w 專用「恢復套件 + 自動安裝腳本」，包含版本檢查、順序化安裝、失敗回滾與驗證清單。並提供明確文件與下載入口，讓使用者在硬重置後能一鍵復原。

實施步驟：
1. 收集與打包
- 實作細節：彙整 Voice Command、Dictionary、Games、RSS reader 等 OEM CAB 與授權檔；標註版本與相依性。
- 所需資源：OEM CAB、校驗工具、版本清單（CSV）。
- 預估時間：0.5 天
2. 自動化安裝
- 實作細節：使用 MortScript 或 Provisioning XML 實作安裝順序與驗證；加入記錄與錯誤提示。
- 所需資源：MortScript、ActiveSync
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# MortScript: restore_c720w.mscr
# 依序安裝並檢查回傳碼
InstallCab("\Storage Card\OEM\VoiceCmd.cab")
If (ErrorLevel <> 0) Message ("VoiceCmd 安裝失敗")
InstallCab("\Storage Card\OEM\Dictionary.cab")
InstallCab("\Storage Card\OEM\Games.cab")
InstallCab("\Storage Card\OEM\RSSReader.cab")
Message ("c720w 預載軟體已恢復。請重新開機。")
```

實際案例：原文指 c720w 硬重置後需安裝官方釋出的套件，安裝後語音命令、字典、遊戲、RSS reader 等功能恢復。
實作環境：Dopod c720w（Windows Mobile 5/6 Smartphone）、ActiveSync、MortScript。
實測數據：
改善前：功能不全，需逐一尋找安裝包。
改善後：一鍵恢復，安裝順序與依賴可重複。
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- Windows Mobile 自動化佈署（MortScript/Provisioning）
- OEM CAB 相依性管理
- 使用者恢復流程 SOP
技能要求：
必備技能：基本安裝與腳本編輯
進階技能：佈署自動化與日誌分析
延伸思考：
可應用於其他型號或 Android/企業裝置佈署；風險在於授權與版本漂移；可延伸加入校驗碼與離線備援。
Practice Exercise（練習題）
基礎練習：編寫一段 MortScript 安裝 2 個 CAB 并提示完成（30 分鐘）
進階練習：加入安裝失敗回滾與日誌（2 小時）
專案練習：製作完整恢復套件與說明文件（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：可完整恢復所有預載軟體
程式碼品質（30%）：腳本結構清晰、錯誤處理完整
效能優化（20%）：安裝步驟最少、時間合理
創新性（10%）：加入版本檢查、UI 引導

---

## Case #2: 安裝 595 版 RSS reader 造成 90 度旋轉 UI 異常

### Problem Statement（問題陳述）
業務場景：使用者於 c720w 上安裝來源於 595 機型的 RSS reader，出現螢幕旋轉 90 度时的畫面錯位與操作不便。更換為正確機型版本後，介面問題消失且速度更快。
技術挑戰：異機型/異解析度/異方向的 UI 適配與資源載入不一致。
影響範圍：閱讀體驗差、按鈕點擊誤差、功能誤用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 安裝了 595 機型的客製版，資源與佈局不適配 c720w 橫向 QVGA。
2. UI 佈局未監聽方向變化與重算尺寸。
3. 位圖/字型在橫向時縮放錯誤。
深層原因：
- 架構層面：缺乏跨機型資源分離與條件載入。
- 技術層面：未使用方向感知控制與自適應佈局。
- 流程層面：測試覆蓋不足（僅單機型）。

### Solution Design（解決方案設計）
解決策略：提供 c720w 專用 build，並在程式中加入方向變化事件處理、自適應佈局與資源按螢幕方向載入策略。

實施步驟：
1. 正確建置與佈署
- 實作細節：下載 c720w 專版；替換錯誤資源；清理舊 Cache。
- 所需資源：正確 CAB、裝置管理工具
- 預估時間：0.5 天
2. 方向感知與佈局
- 實作細節：在 .NET CF 監聽 Resize，根據寬高切換佈局與字型。
- 所需資源：.NET CF、測試裝置
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// .NET Compact Framework: 自適應佈局
using Microsoft.WindowsCE.Forms;

public Form1() {
  InitializeComponent();
  this.Resize += (_, __) => ApplyLayout();
  ApplyLayout();
}

void ApplyLayout() {
  bool isLandscape = this.ClientSize.Width > this.ClientSize.Height;
  titleLabel.Font = new Font("Tahoma", isLandscape ? 9 : 10, FontStyle.Bold);
  listView.Columns[0].Width = isLandscape ? 220 : 180;
  listView.Columns[1].Width = isLandscape ? 80  : 60;
  // 針對橫向/直向調整按鈕與邊距
}
```

實際案例：原文提到改用對應機型版本後，UI 正常且速度變快。
實作環境：Dopod c720w、.NET CF/原生 Win32、Qvga 橫向螢幕。
實測數據：
改善前：旋轉時 UI 錯位、操作不便
改善後：方向適配正常、操作流暢
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- 橫向/直向 UI 適配策略
- 裝置專版 build 與資源管理
- 測試矩陣設計
技能要求：
必備技能：UI 佈局、事件處理
進階技能：資源條件載入與佈局框架
延伸思考：
可應用於平板/車機方向切換；風險在於資源碎片化；可用配置中心統一管理。
Practice Exercise（練習題）
基礎練習：實作 Resize 事件下的列表寬度調整（30 分鐘）
進階練習：建立兩套佈局並自動切換（2 小時）
專案練習：將既有 RSS reader 改造為方向自適配（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：方向切換無 UI 破版
程式碼品質（30%）：佈局抽象與可維護性
效能優化（20%）：切換無卡頓
創新性（10%）：自動字型/密度調整

---

## Case #3: 語音命令 Hotkey/Icon 失效的修復（鍵位映射與註冊）

### Problem Statement（問題陳述）
業務場景：硬重置後，語音命令的快捷鍵與桌面圖示異常或消失。更換為正確套件後恢復，但需要方法確保未來重置亦能穩定映射。
技術挑戰：硬體鍵對應、Shell 快捷註冊與圖示關聯。
影響範圍：關鍵功能不可用、使用效率下降。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未安裝對應版本的語音命令程式。
2. 硬體鍵對應的註冊表鍵值缺失。
3. 圖示路徑/資源錯誤。
深層原因：
- 架構層面：鍵位映射未納入佈署腳本。
- 技術層面：不同機型鍵碼值差異未處理。
- 流程層面：恢復流程缺少驗收清單。

### Solution Design（解決方案設計）
解決策略：安裝正確語音命令 CAB，並利用註冊表統一配置硬體鍵映射與圖示，納入恢復腳本。

實施步驟：
1. 安裝與驗證
- 實作細節：安裝 OEM 語音命令；確認 exe 路徑與 CLSID。
- 所需資源：語音命令 CAB、Registry 編輯器
- 預估時間：0.5 天
2. 映射與圖示修復
- 實作細節：寫入 Shell\Keys 鍵位；建立 .lnk 與 Icon 映射。
- 所需資源：.reg 檔、檔案總管
- 預估時間：0.5 天

關鍵程式碼/設定：
```reg
; 將硬體鍵映射到語音命令
[HKEY_LOCAL_MACHINE\Software\Microsoft\Shell\Keys\40C6]
"Name"="Voice Command"
"Icon"="\\Windows\\VoiceCmd.exe,0"
"Open"="\\Windows\\VoiceCmd.exe"

; 建立開始功能表快捷
[HKEY_LOCAL_MACHINE\Software\Microsoft\Shell\StartItems\VoiceCommand]
"Icon"="\\Windows\\VoiceCmd.exe,0"
"Open"="\\Windows\\VoiceCmd.exe"
```

實際案例：原文指 hotkey/icon 在正確安裝後恢復正常。
實作環境：Dopod c720w、WM5/6、RegEdit。
實測數據：
改善前：熱鍵無反應、圖示缺失
改善後：一鍵啟動語音命令、圖示正確
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- Windows Mobile 鍵位映射
- Shell 快捷與圖示關聯
- 佈署與還原的一致性
技能要求：
必備技能：註冊表編輯
進階技能：恢復腳本自動寫入映射
延伸思考：
可應用於其他常用鍵位；風險是鍵碼差異；可加入機型檢測。
Practice Exercise（練習題）
基礎練習：用 .reg 映射任一鍵到自訂 App（30 分鐘）
進階練習：以腳本自動修復映射（2 小時）
專案練習：做一鍵還原鍵位的工具（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：鍵位功能正確
程式碼品質（30%）：註冊表鍵值清楚
效能優化（20%）：啟動迅速
創新性（10%）：動態檢測機型鍵碼

---

## Case #4: 字典與附贈遊戲遺失的自動化回裝（Extended ROM/開機腳本）

### Problem Statement（問題陳述）
業務場景：硬重置後，原本隨機附贈的字典與兩款遊戲消失。使用者希望像出廠一樣，重置後開機即可自動回裝，不需逐一手動點選。
技術挑戰：啟動自動安裝、順序控制、安裝狀態驗證。
影響範圍：功能缺失、回裝時間成本高。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏 Extended ROM 或等效的開機自動安裝策略。
2. 未統一安裝來源與目錄。
3. 沒有安裝完成檢查機制。
深層原因：
- 架構層面：佈署通道未設計。
- 技術層面：未使用 config.txt/provisioning。
- 流程層面：缺少重置後自檢清單。

### Solution Design（解決方案設計）
解決策略：建立開機自動安裝清單（config.txt 或 MortScript），將字典、遊戲 CAB 納入固定目錄並序列化安裝，安裝後記錄完成旗標。

實施步驟：
1. 目錄與清單
- 實作細節：建立 \Extended_ROM（或 \Storage Card\OEM）；編寫 config。
- 所需資源：CAB、檔案系統權限
- 預估時間：0.5 天
2. 自動化與旗標
- 實作細節：開機執行腳本，安裝完成寫入 Registry/檔案旗標避免重複。
- 所需資源：MortScript、啟動目錄
- 預估時間：0.5 天

關鍵程式碼/設定：
```ini
; config.txt（示意）
CAB: \Storage Card\OEM\Dictionary.cab
CAB: \Storage Card\OEM\Game1.cab
CAB: \Storage Card\OEM\Game2.cab
RST: Reset
```

實際案例：原文提到字典與兩款遊戲在安裝官方套件後回來。
實作環境：Dopod c720w、檔案系統、MortScript/Extended ROM。
實測數據：
改善前：需手動逐一安裝
改善後：重置後自動回裝
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- 開機自動化安裝設計
- 安裝旗標與重入控制
- 安裝清單維護
技能要求：
必備技能：腳本與檔案管理
進階技能：安裝狀態檢測
延伸思考：
可擴充到企業 MDM；需注意授權與檔案簽章。
Practice Exercise（練習題）
基礎練習：寫出兩個 CAB 的 config（30 分鐘）
進階練習：加入旗標避免重複安裝（2 小時）
專案練習：完整自動化回裝方案（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：自動安裝成功
程式碼品質（30%）：清單與旗標邏輯
效能優化（20%）：安裝時間合理
創新性（10%）：安裝失敗回復策略

---

## Case #5: RSS reader 效能不佳的優化（正確版本 + 網路與解析調整）

### Problem Statement（問題陳述）
業務場景：原本安裝錯誤版本的 RSS reader 在 c720w 上速度緩慢；更換為正確版本後速度明顯改善，但仍需進一步優化網路連線與解析策略以提升體驗。
技術挑戰：網路延遲、解析效率、Cache 策略與裝置效能限制。
影響範圍：載入時間長、操作卡頓、電量消耗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 錯誤版本導致未針對橫向 QVGA 與 CPU 最佳化。
2. HTTP 連線未復用（Keep-Alive），握手過多。
3. 未使用增量更新與快取。
深層原因：
- 架構層面：缺乏快取層。
- 技術層面：串流解析與 UI 更新未分離。
- 流程層面：效能指標未定義。

### Solution Design（解決方案設計）
解決策略：採用正確機型版本，開啟 Keep-Alive、實作本地快取與增量更新，使用背景執行緒解析並批次更新 UI。

實施步驟：
1. 網路與快取
- 實作細節：設定 KeepAlive、ETag/Last-Modified；檔案快取。
- 所需資源：.NET CF、檔案系統
- 預估時間：0.5 天
2. 背景解析
- 實作細節：使用 ThreadPool；UI invoke 最小批次更新。
- 所需資源：.NET CF
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 簡化的 HTTP 下載與快取
HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url);
req.KeepAlive = true;
if (File.Exists(cacheMeta)) {
  req.Headers["If-None-Match"] = ReadEtag(cacheMeta);
  req.IfModifiedSince = ReadLastModified(cacheMeta);
}
using (var resp = (HttpWebResponse)req.GetResponse()) {
  if (resp.StatusCode == HttpStatusCode.NotModified) return LoadFromCache();
  using (var s = resp.GetResponseStream())
    SaveAndParseStream(s); // 背景解析
  SaveCacheMeta(resp.Headers["ETag"], resp.LastModified);
}
```

實際案例：原文指出改用正確版本後「速度變快」。
實作環境：Dopod c720w、.NET CF、HTTP。
實測數據：
改善前：載入緩慢（主觀）
改善後：載入明顯加速（主觀）
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- HTTP 增量更新（ETag/Last-Modified）
- 快取與背景解析
- UI 批次更新
技能要求：
必備技能：.NET CF 網路程式
進階技能：快取策略設計
延伸思考：
可加上壓縮（GZip）與預取；風險在儲存空間。
Practice Exercise（練習題）
基礎練習：實作 If-Modified-Since（30 分鐘）
進階練習：加入本地快取與回退（2 小時）
專案練習：完整 RSS 加速方案（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：支援增量更新
程式碼品質（30%）：非同步與 UI 安全
效能優化（20%）：顯著縮短載入
創新性（10%）：預取與排程

---

## Case #6: 導航時螢幕保護自動啟動的防休眠守護

### Problem Statement（問題陳述）
業務場景：使用 PaPaGo 導航時，螢幕保護啟動造成導航畫面中斷與操作危險。需求是在導航啟用期間防止裝置進入待機或關閉背光。
技術挑戰：系統閒置計時器與電源管理控制。
影響範圍：導航中斷、行車安全風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 電源策略在閒置一定時間後觸發螢幕保護/背光關閉。
2. 導航程式未持續重置閒置計時器。
3. 未偵測外接電源狀態調整超時。
深層原因：
- 架構層面：缺少 App 級電源守護。
- 技術層面：未調用 SystemIdleTimerReset。
- 流程層面：未建立行車場景的電源設定。

### Solution Design（解決方案設計）
解決策略：建立「防休眠守護程式」，於導航執行期間週期性呼叫 SystemIdleTimerReset，並在外接電源時鎖定背光常亮。

實施步驟：
1. 守護程式
- 實作細節：計時器每 20–30 秒呼叫 API；啟停與導航綁定。
- 所需資源：.NET CF/原生 C、計時器
- 預估時間：0.5 天
2. 啟動與自動化
- 實作細節：放入啟動資料夾或由導航 App 啟動；加入 UI 提示。
- 所需資源：捷徑、啟動腳本
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// .NET CF 防休眠守護
[System.Runtime.InteropServices.DllImport("coredll.dll")]
static extern void SystemIdleTimerReset();

System.Threading.Timer t;
void StartGuard() {
  t = new System.Threading.Timer(_ => SystemIdleTimerReset(), null, 0, 20000);
}
void StopGuard() { t?.Dispose(); }
```

實際案例：原文提到導航沒多久螢幕保護即啟動，造成干擾。
實作環境：Dopod c720w、WM5/6、PaPaGo。
實測數據：
改善前：導航被螢幕保護中斷
改善後：導航期間螢幕保持常亮
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- Windows CE/WM 電源管理
- SystemIdleTimerReset 的使用
- 行車場景的 UX 與安全
技能要求：
必備技能：.NET CF/原生 API 呼叫
進階技能：守護程式設計
延伸思考：
可加入偵測車充與自動啟停；注意電量消耗。
Practice Exercise（練習題）
基礎練習：製作簡單守護程式（30 分鐘）
進階練習：偵測前景為導航 App 時才啟用（2 小時）
專案練習：整合 UI 控制與電源策略（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：導航時不休眠
程式碼品質（30%）：資源釋放與穩定性
效能優化（20%）：低耗電
創新性（10%）：智慧啟停策略

---

## Case #7: 行車中觸控不便的無手操作與大按鍵 UI

### Problem Statement（問題陳述）
業務場景：行車導航過程中，觸控操作不便且不安全。使用者希望改為熱鍵或語音操作，並以大按鍵/高對比 UI 提升可達性。
技術挑戰：鍵位事件處理、語音觸發與 UI 無障礙設計。
影響範圍：安全風險與誤操作。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 控件尺寸小，駕駛時難觸控。
2. 未提供熱鍵或語音替代路徑。
3. UI 對比度與可視性不足。
深層原因：
- 架構層面：缺少無障礙模式。
- 技術層面：未處理硬鍵事件與語音 SDK。
- 流程層面：未針對行車情境測試。

### Solution Design（解決方案設計）
解決策略：加入語音控制（如系統語音命令）、支援硬體鍵切換常用功能，以及切換至大按鍵模式（字型放大、對比提升）。

實施步驟：
1. 熱鍵與語音
- 實作細節：映射方向/OK 鍵切換頁面；整合語音命令關鍵字。
- 所需資源：語音 SDK、本機鍵碼表
- 預估時間：0.5 天
2. 大按鍵模式
- 實作細節：提供「行車模式」切換樣式，放大控件與對比。
- 所需資源：UI 樣式、設定頁
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 以方向鍵操作核心功能
protected override void OnKeyDown(KeyEventArgs e) {
  switch (e.KeyCode) {
    case Keys.Up:    ZoomIn();  break;
    case Keys.Down:  ZoomOut(); break;
    case Keys.Left:  PrevTurn();break;
    case Keys.Right: NextTurn();break;
    case Keys.Enter: ToggleMenu(); break;
  }
  e.Handled = true;
}
```

實際案例：原文指出行車中不便觸控，建議改用更適合的操作方式或專用機。
實作環境：Dopod c720w、.NET CF、語音命令。
實測數據：
改善前：駕駛時難以操作
改善後：使用熱鍵/語音，操作更安全
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- 無障礙與情境化 UI
- 硬體鍵事件處理
- 語音命令整合
技能要求：
必備技能：UI 與事件處理
進階技能：語音介面設計
延伸思考：
可用車載藍牙按鍵；注意誤觸與誤觸發。
Practice Exercise（練習題）
基礎練習：為 4 向鍵綁定功能（30 分鐘）
進階練習：設計一個行車模式樣式（2 小時）
專案練習：整合語音與熱鍵的導航控制（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：主要功能鍵全覆蓋
程式碼品質（30%）：事件處理簡潔穩定
效能優化（20%）：切換無延遲
創新性（10%）：誤觸防護

---

## Case #8: 智慧型手機不適合長時導航的專機化決策

### Problem Statement（問題陳述）
業務場景：使用者發現手機作為導航設備時受螢幕休眠、觸控難度與來電干擾等因素影響，決定改用舊 PDA 當專用 GPS。企業或個人需決策何時採專機化、何時整合於手機。
技術挑戰：可靠性、續航、穩定性評估與決策。
影響範圍：使用效率、成本、維護策略。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 手機多任務與通訊干擾導航可靠性。
2. 電源管理不符長時常亮需求。
3. UI 與操作不適合行車。
深層原因：
- 架構層面：未隔離關鍵任務負載。
- 技術層面：缺乏持續供電與散熱設計。
- 流程層面：場景評估不足。

### Solution Design（解決方案設計）
解決策略：建立評估矩陣（穩定性/續航/操作/成本/維護），達不到門檻時採專機化；若整合，則加入電源守護、無手操作與干擾抑制策略。

實施步驟：
1. 評估與門檻
- 實作細節：定義 SLO（不中斷、續航 N 小時）；試航測試。
- 所需資源：評估表、真實路測
- 預估時間：0.5 天
2. 決策與落地
- 實作細節：選擇專機或加強方案；文件化操作規範。
- 所需資源：專機設備/設定文件
- 預估時間：0.5 天

關鍵程式碼/設定：
（本案以決策流程為主，無需程式碼）

實際案例：原文最終改用舊 PDA 作為 GPS 專用機。
實作環境：c720w + 舊 PDA 對比評估。
實測數據：
改善前：導航易中斷與操作不便
改善後：專機更穩定、操作集中
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- 系統角色分工
- SLO/SLA 制定
- 場景化決策
技能要求：
必備技能：測試與評估報告撰寫
進階技能：成本/可靠性分析
延伸思考：
可延伸至企業裝置與 BYOD；風險為設備管理複雜度增加。
Practice Exercise（練習題）
基礎練習：撰寫導航場景評估表（30 分鐘）
進階練習：完成一次路測與結論（2 小時）
專案練習：提出整合或專機化方案建議書（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：評估面向全面
程式碼品質（30%）：不適用
效能優化（20%）：決策合理
創新性（10%）：替代方案多元

---

## Case #9: App 方向變化導致版面錯亂的 OAC（Orientation Aware Control）實作

### Problem Statement（問題陳述）
業務場景：在橫向的 c720w 上，方向變化造成既有 App 版面錯亂。需導入 OAC 或等效框架，自動為不同方向載入對應配置。
技術挑戰：多方向 UI 管理、重用與維護。
影響範圍：體驗不一致、維護成本高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一佈局硬撐多方向。
2. 控件定位用絕對座標。
3. 缺乏方向專屬資源。
深層原因：
- 架構層面：無 UI 抽象層。
- 技術層面：未使用 OAC/佈局容器。
- 流程層面：測試未覆蓋方向切換。

### Solution Design（解決方案設計）
解決策略：使用 OAC 或自建方向感知容器，為 Portrait/Landscape 提供不同配置檔，切換時自動套用。

實施步驟：
1. 建置 OAC
- 實作細節：為兩種方向建立配置；控件綁定 ID。
- 所需資源：OAC 程式庫
- 預估時間：0.5 天
2. 切換與測試
- 實作細節：監聽 Resize，套用配置；回歸測試。
- 所需資源：測試案例
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 假設已有 OAC 類別，載入兩份佈局
OrientationAwarePanel panel = new OrientationAwarePanel();
panel.LoadLayout("layout_portrait.xml", Orientation.Portrait);
panel.LoadLayout("layout_landscape.xml", Orientation.Landscape);
this.Resize += (_, __) => panel.Apply(CurrentOrientation());
```

實際案例：原文提及旋轉 90 度時的 UI 問題。
實作環境：Dopod c720w、.NET CF。
實測數據：
改善前：方向切換破版
改善後：自動切換佈局
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- 方向感知 UI 模式
- 佈局抽象與資源配置
- 測試策略
技能要求：
必備技能：UI 模型設計
進階技能：框架封裝
延伸思考：
可以擴充到 DPI/語言；注意資源量增加。
Practice Exercise（練習題）
基礎練習：做兩份佈局切換（30 分鐘）
進階練習：抽象成可重用控件（2 小時）
專案練習：重構既有 App 以支援 OAC（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：切換正確
程式碼品質（30%）：架構清晰
效能優化（20%）：切換即時
創新性（10%）：佈局自動生成

---

## Case #10: 多機型安裝包的條件式安裝（setup.dll 檢測）

### Problem Statement（問題陳述）
業務場景：同一 App 需支援 595 與 c720w，現行做法常誤裝錯版本導致問題。需在安裝時自動辨識機型與螢幕方向，選擇正確資源。
技術挑戰：安裝階段條件判斷與資源分發。
影響範圍：裝置相容性、客服工單。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單一 CAB 打包多版本資源未分流。
2. 無安裝時機型檢測。
3. 缺乏 setup.dll。
深層原因：
- 架構層面：安裝流程缺少智慧化分流。
- 技術層面：未利用 WinCE 安裝 Hook。
- 流程層面：發佈治理不足。

### Solution Design（解決方案設計）
解決策略：為 CAB 提供 setup.dll，在 Install_Init 檢測螢幕解析/方向/是否觸控，將對應資源拷貝並寫註冊表，避免誤裝。

實施步驟：
1. 檢測與分流
- 實作細節：用 GetSystemMetrics 或 Registry 取得寬高/方向。
- 所需資源：Native C、CE Setup API
- 預估時間：1 天
2. 打包測試
- 實作細節：CAB 打包並在 2 機型驗證。
- 所需資源：CabWiz、測試機
- 預估時間：1 天

關鍵程式碼/設定：
```c
// setup.dll 節選
BOOL Install_Init(HWND hwndParent, BOOL fFirstCall, BOOL fPrev, LPCTSTR pszDir) {
  int cx = GetSystemMetrics(SM_CXSCREEN);
  int cy = GetSystemMetrics(SM_CYSCREEN);
  BOOL landscape = cx > cy;
  if (landscape) CopyFile(TEXT("\\App\\res\\land\\*"), TEXT("\\Program Files\\App\\res\\"), FALSE);
  else          CopyFile(TEXT("\\App\\res\\port\\*"), TEXT("\\Program Files\\App\\res\\"), FALSE);
  return TRUE;
}
```

實際案例：原文顯示誤用 595 版導致問題，條件式安裝可避免。
實作環境：WM5/6、CabWiz、Visual C++。
實測數據：
改善前：誤裝導致 UI/效能問題
改善後：安裝自動分流無誤
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- WinCE 安裝流程 Hook
- 機型/螢幕檢測
- 資源條件分發
技能要求：
必備技能：C/Win32 API
進階技能：Cab 打包與測試
延伸思考：
可加入 CPU/語言檢測；注意安裝權限。
Practice Exercise（練習題）
基礎練習：於 setup.dll 取得螢幕大小（30 分鐘）
進階練習：分流拷貝不同資源（2 小時）
專案練習：打造智慧 CAB（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：正確分流
程式碼品質（30%）：健壯與錯誤處理
效能優化（20%）：安裝時間可接受
創新性（10%）：更多條件辨識

---

## Case #11: 售後支援溝通與釋出流程（SLA 與升級路徑）

### Problem Statement（問題陳述）
業務場景：使用者與客服往返十封郵件與多通電話，才等到官方釋出恢復套件。需設計清晰的支援溝通模板與 SLA，並建立公開下載與版本公告。
技術挑戰：跨部門協調、版本管理與公告機制。
影響範圍：客訴、維護成本、品牌信任。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有公開下載入口。
2. 案件處理缺 SLA。
3. 變更/版本未公告。
深層原因：
- 架構層面：缺產品支援入口網站。
- 技術層面：發佈管線缺少自動化。
- 流程層面：SOP 與回饋不完整。

### Solution Design（解決方案設計）
解決策略：建立支援入口、SLA（回覆與解決時限）、版本公告頁與訂閱機制，並提供完整恢復文件與 FAQ。

實施步驟：
1. 文件與入口
- 實作細節：建立知識庫頁面與下載；FAQ。
- 所需資源：Wiki/官網 CMS
- 預估時間：1 天
2. SLA 與追蹤
- 實作細節：客服系統設定 SLA、模板化回覆與升級流程。
- 所需資源：Helpdesk 系統
- 預估時間：1 天

關鍵程式碼/設定：
（流程/內容配置，無需程式碼）

實際案例：原文描述需多次聯繫才拿到安裝包。
實作環境：客服系統、官網。
實測數據：
改善前：等待時間長
改善後：自助下載、一次到位
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- SLA 設計
- 發佈與版本訊息
- 自助服務入口
技能要求：
必備技能：流程設計
進階技能：知識庫維運
延伸思考：
可接 API 通知；風險在版本散佈控制。
Practice Exercise（練習題）
基礎練習：寫一份客服回覆模板（30 分鐘）
進階練習：建立版本公告頁（2 小時）
專案練習：設計完整支援流程（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：流程覆蓋需求
程式碼品質（30%）：不適用
效能優化（20%）：縮短解決時間
創新性（10%）：自動通知

---

## Case #12: 硬重置前後的資料與設定備份還原策略

### Problem Statement（問題陳述）
業務場景：硬重置易導致連絡人、簡訊、App 設定與捷徑遺失。需在重置前完成完整備份，重置後快速還原，降低停機時間。
技術挑戰：系統資料（PIM）、App 設定與檔案備份。
影響範圍：資料遺失與效率降低。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未預先備份 PIM 與 App 設定。
2. 不同 App 的設定散落。
3. 沒有一鍵還原。
深層原因：
- 架構層面：缺少統一備份策略。
- 技術層面：某些資料庫（pim.vol）處理複雜。
- 流程層面：缺 SOP 與檢核表。

### Solution Design（解決方案設計）
解決策略：使用專用備份工具（如 PIM Backup/Sprite Backup）與手動匯出 App 設定；建立檢核表與還原腳本。

實施步驟：
1. 備份
- 實作細節：備份 PIM、SMS、通話紀錄、我的文件；匯出 App 設定。
- 所需資源：備份工具、檔案管理
- 預估時間：0.5 天
2. 還原
- 實作細節：重置後先恢復 PIM，再恢復 App 與設定；驗收。
- 所需資源：工具與清單
- 預估時間：0.5 天

關鍵程式碼/設定：
（使用工具操作為主，可另行提供批次複製腳本）

實際案例：對應原文的重置情境。
實作環境：WM5/6、ActiveSync。
實測數據：
改善前：資料與設定丟失
改善後：快速還原
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- PIM/檔案備份
- 還原順序
- 檢核表
技能要求：
必備技能：工具使用
進階技能：自動化腳本
延伸思考：
可結合雲端同步；注意隱私與加密。
Practice Exercise（練習題）
基礎練習：製作重置檢核表（30 分鐘）
進階練習：半自動化還原腳本（2 小時）
專案練習：端到端備份還原方案（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：資料完整
程式碼品質（30%）：腳本清晰
效能優化（20%）：縮短停機時間
創新性（10%）：加密與驗證

---

## Case #13: Start Menu 快捷與圖示恢復（.lnk 與資料夾結構）

### Problem Statement（問題陳述）
業務場景：重置後某些 App 不出現在 Start Menu 或圖示錯誤，需手動建立快捷與圖示映射，確保使用者可快速找到功能。
技術挑戰：.lnk 語法、圖示索引與資料夾佈局。
影響範圍：可用性降低、學習成本上升。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 安裝過程未建立 Start Menu 快捷。
2. 圖示資源路徑/索引錯誤。
3. 快捷放在錯誤目錄。
深層原因：
- 架構層面：安裝腳本未覆蓋 UI 入口。
- 技術層面：.lnk 規格不熟悉。
- 流程層面：缺少驗收。

### Solution Design（解決方案設計）
解決策略：建立正確 .lnk 檔並放入 \Windows\Start Menu\Programs，指定圖示與參數；將此步驟納入自動化安裝。

實施步驟：
1. 建立快捷
- 實作細節：製作 46# 語法 .lnk；測試啟動。
- 所需資源：文字編輯器、檔案總管
- 預估時間：0.5 天
2. 納入腳本
- 實作細節：安裝完成複製 .lnk；檢查圖示。
- 所需資源：MortScript/Setup.dll
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
; Voice Command.lnk 內容（示意）
46#\Windows\VoiceCmd.exe? -min
; 將此檔放入 \Windows\Start Menu\Programs\
```

實際案例：原文提及語音命令 icon 恢復，對應快捷與資源修復。
實作環境：WM5/6 檔案系統。
實測數據：
改善前：找不到 App
改善後：開始功能表可見且圖示正確
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- .lnk 語法（WinCE）
- Start Menu 結構
- 安裝後動作
技能要求：
必備技能：檔案與路徑管理
進階技能：安裝自動化
延伸思考：
可本地化命名與分類；注意圖示資源索引。
Practice Exercise（練習題）
基礎練習：為任一 App 建立 .lnk（30 分鐘）
進階練習：安裝後自動放置快捷（2 小時）
專案練習：Start Menu 結構化配置（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：快捷可用
程式碼品質（30%）：路徑正確
效能優化（20%）：啟動迅速
創新性（10%）：分類與本地化

---

## Case #14: 外接電源時保持常亮的電源管理與註冊表設定

### Problem Statement（問題陳述）
業務場景：行車導航時需外接電源並保持螢幕常亮，避免中斷。現行預設會在閒置後關閉背光或鎖定。
技術挑戰：電源/背光超時與外接電源狀態切換。
影響範圍：導航中斷、體驗下降。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Battery/AC 模式超時設定不當。
2. 未區分外接電源行為。
3. 導航 App 未覆蓋系統設定。
深層原因：
- 架構層面：缺乏情境化電源設定。
- 技術層面：註冊表與控制面板未調整。
- 流程層面：行車場景缺 SOP。

### Solution Design（解決方案設計）
解決策略：在外接電源時將背光與螢幕超時設為「永不」，並在電池模式下維持合理時間；結合防休眠守護提升穩定性。

實施步驟：
1. 調整註冊表
- 實作細節：設定 HKCU\ControlPanel\Backlight 的 ACTimeout=0。
- 所需資源：Reg 編輯器/腳本
- 預估時間：0.5 天
2. 驗證與回退
- 實作細節：切換 AC/電池狀態測試；保留還原腳本。
- 所需資源：測試與文件
- 預估時間：0.5 天

關鍵程式碼/設定：
```reg
; 背光與螢幕超時（示意，數值單位依機型）
[HKEY_CURRENT_USER\ControlPanel\Backlight]
"ACTimeout"=dword:00000000   ; 外接電源時永不關閉
"BatteryTimeout"=dword:0000001E ; 電池模式 30 秒（示意）
```

實際案例：原文指出導航時觸發螢幕保護，需常亮。
實作環境：c720w、WM5/6。
實測數據：
改善前：外接電源仍會熄屏
改善後：外接時常亮
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- Backlight 設定鍵
- AC/電池模式差異
- 配合守護程式
技能要求：
必備技能：註冊表調整
進階技能：場景化配置
延伸思考：
可做一鍵切換行車模式；注意螢幕老化與耗電。
Practice Exercise（練習題）
基礎練習：用 .reg 調整超時（30 分鐘）
進階練習：行車模式切換腳本（2 小時）
專案練習：整合 UI 的電源管理面板（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：外接電源常亮
程式碼品質（30%）：設定正確可回退
效能優化（20%）：耗電可控
創新性（10%）：情境自動切換

---

## Case #15: 機型差異下的資源封裝與載入（多解析度/多語系）

### Problem Statement（問題陳述）
業務場景：因 595 與 c720w 差異導致 UI 與效能問題。需將圖形、字串與佈局資源依機型/方向/語言分離，於執行時動態載入正確版本。
技術挑戰：資源版本管理與載入條件判斷。
影響範圍：相容性、維護成本、使用體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一資源包混用多機型。
2. 缺乏條件化載入邏輯。
3. 未分離語言與解析度資源。
深層原因：
- 架構層面：資源管理未模組化。
- 技術層面：未使用衛星組件/資源檔。
- 流程層面：打包策略缺失。

### Solution Design（解決方案設計）
解決策略：建立資源命名規約（land/port/zh-TW/en-US），使用執行時環境偵測載入對應資源；字串用 resx，圖片/佈局用目錄分層。

實施步驟：
1. 資源分離
- 實作細節：移動圖片與佈局到 land/port；字串用 resx。
- 所需資源：專案重構
- 預估時間：1 天
2. 動態載入
- 實作細節：開機偵測螢幕與文化資訊，設定資源根目錄。
- 所需資源：.NET CF/Win32
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 動態決定資源目錄
string dir = (Screen.PrimaryScreen.Bounds.Width > Screen.PrimaryScreen.Bounds.Height) ? "land" : "port";
var bmp = new Bitmap($@"\Program Files\App\res\{dir}\header.png");

// 多語系字串
ResourceManager rm = new ResourceManager("App.Strings", Assembly.GetExecutingAssembly());
string title = rm.GetString("Title");
```

實際案例：原文顯示不同機型資源混用導致問題。
實作環境：.NET CF、c720w/595。
實測數據：
改善前：資源錯配
改善後：資源對應正確
改善幅度：未量化

Learning Points（學習要點）
核心知識點：
- 衛星組件/Resx
- 方向/解析度資源分離
- 執行時偵測
技能要求：
必備技能：資源管理
進階技能：打包與載入策略
延伸思考：
可支援 DPI、深色模式；注意包體大小。
Practice Exercise（練習題）
基礎練習：用 resx 做雙語（30 分鐘）
進階練習：land/port 資源切換（2 小時）
專案練習：重構專案資源體系（8 小時）
Assessment Criteria（評估標準）
功能完整性（40%）：資源正確載入
程式碼品質（30%）：結構清晰
效能優化（20%）：載入快速
創新性（10%）：動態快取

---

## 案例分類

1. 按難度分類
- 入門級（適合初學者）：#4, #8, #11, #12, #13
- 中級（需要一定基礎）：#1, #2, #3, #5, #6, #7, #9, #14, #15
- 高級（需要深厚經驗）：#10

2. 按技術領域分類
- 架構設計類：#1, #8, #9, #10, #11, #15
- 效能優化類：#2, #5
- 整合開發類：#1, #3, #4, #9, #10, #13, #15
- 除錯診斷類：#2, #3, #5, #6, #14
- 安全防護類（行車安全/可用性）：#6, #7, #14

3. 按學習目標分類
- 概念理解型：#8, #11
- 技能練習型：#3, #4, #12, #13, #14
- 問題解決型：#1, #2, #5, #6, #7, #9
- 創新應用型：#10, #15

## 案例關聯圖（學習路徑建議）

- 入門起步（裝置恢復與基本操作）：#12（備份還原） → #1（恢復套件） → #4（自動回裝） → #13（快捷修復）
- UI/裝置適配主線：#2（方向適配） → #9（OAC 框架） → #15（資源封裝）
- 導航場景優化線：#6（防休眠） → #14（電源管理） → #7（無手操作） → #8（專機化決策）
- 安裝與分流進階線：#3（鍵位/圖示註冊） → #10（條件式安裝）
- 支援與治理：#11（SLA 與釋出）輔助所有路徑

依賴關係與先後順序：
- #12 → #1/#4：先備份再恢復/自動化
- #2 → #9/#15：先解決方向適配，再上升到框架與資源體系
- #6 → #14 → #7：先確保不休眠，再優化電源，最後改善操作
- #3 與 #13 可並行，完善使用入口
- #10 屬高階，需先完成 #2/#9/#15 的資源與適配能力

完整學習路徑建議：
1) 先掌握資料與系統恢復（#12 → #1 → #4 → #13）
2) 進入 UI 與裝置適配（#2 → #9 → #15）
3) 深化導航場景穩定與安全（#6 → #14 → #7 → #8）
4) 進階安裝治理與分流（#3 → #10）
5) 最後建立支援與發佈治理能力（#11）

上述 15 個案例均源於原文提及的實際問題與改善線索，並擴充為可重複、可評估的實作練習。