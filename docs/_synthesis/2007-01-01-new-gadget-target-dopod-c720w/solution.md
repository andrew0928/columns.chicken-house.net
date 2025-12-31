---
layout: synthesis
title: "敗家新目標... Dopod C720w"
synthesis_type: solution
source_post: /2007/01/01/new-gadget-target-dopod-c720w/
redirect_from:
  - /2007/01/01/new-gadget-target-dopod-c720w/solution/
postid: 2007-01-01-new-gadget-target-dopod-c720w
---

以下內容是根據原文中提到的實際問題與取捨（待機過短、低電量掉話、螢幕相容性、WiFi/3G取捨、鍵盤效率、綁約時程等）所萃取與延展的可教學解決方案案例。為保持嚴謹，凡原文未提供數據的部分，以下均以「建議指標／待量測」方式呈現，不杜撰未出現的實測數據。

## Case #1: 智慧型手機待機過短的診斷與優化

### Problem Statement（問題陳述）
**業務場景**：使用者以手機處理日常通話與行事曆／聯絡人同步（Outlook），但現役 Mio 8390 待機僅約兩天，一旦某天通話較多便無法撐過一天，影響工作聯絡與行程協調。希望在不犧牲必要功能的前提下延長待機。
**技術挑戰**：辨識電力消耗主因（基帶、螢幕、背景同步、App），並以可驗證的方式逐步削減耗電。
**影響範圍**：通話不中斷、待機時間、資料同步可靠性、裝置可用性。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 電池健康度下降（容量衰退）— 老化導致實際可用 mAh 減少。
2. 無線電持續駐網／搜尋訊號 — 訊號差時基帶功耗升高。
3. 背景同步（如郵件推播）過於頻繁 — 高頻喚醒與資料連線耗電。

**深層原因**：
- 架構層面：電源管理策略缺乏資料導向的調校（無基準與監測）。
- 技術層面：3G/多頻掃描與高亮度／長開螢幕的功耗特性未控。
- 流程層面：無例行化的電池校正與耗電源頭回歸分析流程。

### Solution Design（解決方案設計）
**解決策略**：以「量測-調整-驗證」的迭代方式，先建立耗電基準，再逐項調整（關閉非必要推播、鎖定 2G、降低螢幕亮度、優化同步時段），最後評估是否更換高品質電池或採購新機。

**實施步驟**：
1. 建立耗電基準
- 實作細節：裝設輕量監測程式記錄電池百分比、螢幕亮度、資料連線狀態、基帶狀態。
- 所需資源：.NET Compact Framework、Microsoft.WindowsMobile.Status
- 預估時間：2-4 小時

2. 調整耗電配置
- 實作細節：關閉推播/改為排程、鎖定 2G、降低亮度/逾時熄屏、清理常駐 App。
- 所需資源：裝置設定、ActiveSync 選項
- 預估時間：1-2 小時

3. 硬體處置
- 實作細節：更換原廠或高品質高容量電池，並執行一次完整充放電校正。
- 所需資源：電池、充電器
- 預估時間：0.5-1 小時（不含運送）

**關鍵程式碼/設定**：
```csharp
// .NET Compact Framework (Windows Mobile)
// 監測電池電量與網路狀態（示意）
using Microsoft.WindowsMobile.Status;
using System;

public class PowerLogger
{
    private SystemState _battery = new SystemState(SystemProperty.PowerBatteryStrength);
    private SystemState _signal = new SystemState(SystemProperty.PhoneSignalStrength);
    private SystemState _dataConn = new SystemState(SystemProperty.ConnectionsNetworkCount);

    public PowerLogger()
    {
        _battery.Changed += (s, e) => Log("Battery", _battery.CurrentValue);
        _signal.Changed += (s, e) => Log("Signal", _signal.CurrentValue);
        _dataConn.Changed += (s, e) => Log("DataConn", _dataConn.CurrentValue);
    }

    private void Log(string key, object value)
    {
        // TODO: append to file with timestamp
        // 建議格式: yyyy-MM-dd HH:mm:ss, key, value
    }
}
```

實際案例：原文指出 Mio 8390 待機僅 2.x 天，通話多時會撐不過一天。
實作環境：Windows Mobile 5/6 智慧型手機、.NET CF 2.0、ActiveSync 4.5（PC 端為 Windows XP 時代）。
實測數據：
- 改善前：原文未提供；建議量測待機小時、螢幕開啟時間、通話總分鐘。
- 改善後：待量測（同上指標）。
- 改善幅度：待量測（% 或倍數）。

Learning Points（學習要點）
核心知識點：
- 行動裝置耗電來源分解（基帶/螢幕/背景同步/常駐 App）
- 以資料驅動的節能調校方法論
- Windows Mobile 狀態 API 監測

技能要求：
- 必備技能：系統設定調整、基本程式碼閱讀、日誌分析
- 進階技能：耗電模型建立、迭代調校設計

延伸思考：
- 同法適用於 Android/iOS 的耗電剖析（工具不同）
- 風險：過度關閉同步導致收訊延遲
- 優化：自動化情境（上班/下班）切換配置

Practice Exercise（練習題）
- 基礎練習：關閉推播、改為每小時一次同步，記錄 24 小時耗電（30 分鐘設定+24 小時觀察）
- 進階練習：撰寫簡單監測 App，輸出 CSV（2 小時）
- 專案練習：完成一份耗電分析報告，提出三項優化與預估效益（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：完成監測與三項設定調整
- 程式碼品質（30%）：事件處理穩定、檔案輸出正確
- 效能優化（20%）：待機時數實際提升（需佐證）
- 創新性（10%）：自動化情境切換或視覺化儀表板


## Case #2: 低電量通話斷訊的風險控制

### Problem Statement（問題陳述）
**業務場景**：通話進行中，電量從兩格掉到一格即掉話，造成重要通聯中斷。
**技術挑戰**：在不更動營運商與網路環境下，降低低電量狀態的掉話風險。
**影響範圍**：客戶溝通、關鍵通話失敗率、品牌信任。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 電池電壓塌陷（High TX power 時電壓下陷）— 基帶重置／進入保護。
2. 訊號弱導致發射功率拉高 — 提高瞬時電流需求。
3. 低電量時 OS/基帶採取保護策略（降載/斷線）。

**深層原因**：
- 架構層面：電源管理與通話品質保護未關聯。
- 技術層面：無門檻警戒與通話策略（例：低電量禁撥出）。
- 流程層面：缺乏「低電量情境」的通話 SOP（如改用座機/VoIP）。

### Solution Design（解決方案設計）
**解決策略**：建立低電量門檻與動作（警示、建議改用替代通道）、優先確保良好收訊環境、必要時更換電池與韌體。

**實施步驟**：
1. 設定低電量警戒與禁用撥出建議
- 實作細節：偵測 <20% 電量時彈出提示；通話開始時再次檢查。
- 所需資源：.NET CF 狀態 API、UI 提示
- 預估時間：1 小時

2. 收訊改善與替代方案
- 實作細節：固定在收訊佳處通話、提供 WiFi VoIP（見 Case #11）。
- 所需資源：WiFi/耳麥
- 預估時間：0.5 小時

3. 硬體與韌體
- 實作細節：更換電池；檢查有無基帶韌體更新（見 Case #9）。
- 所需資源：電池、OEM 更新工具
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
```csharp
// 低電量撥號防護（示意）— 無法攔截所有撥號，至少提示使用者
using Microsoft.WindowsMobile.Status;

public class CallGuard
{
    private readonly SystemState _battery = new SystemState(SystemProperty.PowerBatteryStrength);
    private readonly SystemState _talking = new SystemState(SystemProperty.PhoneCallTalking);

    public CallGuard()
    {
        _talking.Changed += (s, e) =>
        {
            bool inCall = (bool)_talking.CurrentValue;
            int batt = (int)_battery.CurrentValue;
            if (inCall && batt <= 20)
            {
                ShowWarning("電量過低，建議改用座機或 WiFi 通話，避免斷線。");
            }
        };
    }

    private void ShowWarning(string msg)
    {
        // TODO: 顯示對話框或氣泡通知
    }
}
```

實際案例：原文描述電量降至一格時幾乎必掉話。
實作環境：Windows Mobile 5/6、.NET CF 2.0。
實測數據：
- 改善前：原文未提供；建議記錄「低電量通話掉話率」。
- 改善後：待量測（同指標）。
- 改善幅度：待量測。

Learning Points
- 低電量對 RF 子系統的影響與防護策略
- 事件驅動的系統提示與風險告知
- 替代通道（VoIP）導入思維

技能要求
- 必備技能：狀態監測、UI 提示
- 進階技能：通話事件監測、風險策略設計

延伸思考
- 自動切換到 WiFi 通話的可行性與限制
- 不同電池內阻對瞬時掉壓的影響
- 如何以更精細的門檻（溫度、RSSI）控制

Practice Exercise
- 基礎：在電量 <20% 時彈出提示（30 分鐘）
- 進階：記錄低電量期間的通話成敗（2 小時）
- 專案：低電量風險儀表板與建議動作（8 小時）

Assessment Criteria
- 功能完整性（40%）：低電量提示與事件記錄
- 程式碼品質（30%）：穩定不當機
- 效能優化（20%）：掉話率下降（需量測）
- 創新性（10%）：動態門檻（含訊號強度）


## Case #3: 手機選型決策矩陣：鍵盤、WiFi 與 3G 的取捨

### Problem Statement
**業務場景**：候選機種為 Dopod C720w（鍵盤、橫向螢幕、WiFi、無 3G）與 595（3G、QVGA 直向、相容性佳）。需在打字效率、資料連線、相容性與電力之間做權衡。
**技術挑戰**：建立可重複的量化評分模型，避免主觀決策失誤。
**影響範圍**：生產力、連線成本與穩定性、後續 App 相容性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 使用習慣差異（文字輸入頻繁度）未量化。
2. 網路使用型態（WiFi 可用性 vs 3G 需求）未評估。
3. App 相容性受螢幕比例影響（360x240 vs 240x320）。

**深層原因**：
- 架構層面：缺少統一的評估框架。
- 技術層面：未把耗電與連線品質納入模型。
- 流程層面：缺標準化需求蒐集與加權。

### Solution Design
**解決策略**：建立加權評分矩陣（輸入效率、資料連線、相容性、電力、價格），以分數輔助決策。

**實施步驟**：
1. 定義指標與權重
- 實作細節：輸入效率（WPM）、資料場景（WiFi 覆蓋/3G 時數）、相容性（目標 App 清單）、電力（預估待機/通話）。
- 所需資源：問卷/歷史使用紀錄
- 預估時間：1 小時

2. 建立計算腳本與比較
- 實作細節：以 Python/Excel 計算每台分數，輸出排名。
- 所需資源：Python/Excel
- 預估時間：1 小時

**關鍵程式碼/設定**：
```python
# 簡化的加權評分（示意）
weights = {
    "typing": 0.25,      # 鍵盤/輸入效率
    "connectivity": 0.25,# WiFi/3G 符合需求
    "compat": 0.20,      # App 相容性
    "battery": 0.20,     # 待機/通話
    "price": 0.10
}

# 分數 1~5（依自評/測試結果填寫）
C720w = {"typing":5,"connectivity":4,"compat":3,"battery":4,"price":3}
D595  = {"typing":3,"connectivity":4,"compat":5,"battery":3,"price":3}

def score(device):
    return sum(device[k]*weights[k] for k in weights)

print("C720w:", score(C720w))
print("595:", score(D595))
```

實際案例：原文作者選擇放棄 3G，傾向 C720w（鍵盤、WiFi、橫向螢幕）。
實作環境：Python 3.x 或 Excel。
實測數據：
- 改善前：無量化依據（主觀）。
- 改善後：有分數與依據（待填權重與分數）。
- 改善幅度：決策透明度與一致性提升（可記錄決策時間下降）。

Learning Points
- 建立可重複的 MCDM（多準則決策）流程
- 權重敏感度分析
- 將耗電/相容性資訊納入

技能要求
- 必備技能：資料整理、簡單腳本
- 進階技能：AHP/SMART 等進階決策法

延伸思考
- 加入 TCO（違約金、資費）為成本維度
- 不同使用者角色的權重模板

Practice Exercise
- 基礎：用 5 指標為兩台機種打分（30 分鐘）
- 進階：做權重敏感度曲線（2 小時）
- 專案：為 3 台以上機種出具選型報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：指標/權重/分數/結論
- 程式碼品質（30%）：可重複/可調整
- 效能優化（20%）：決策效率提升（記錄用時）
- 創新性（10%）：可視化/互動儀表板


## Case #4: 320x240 橫向螢幕的 App 相容性改造

### Problem Statement
**業務場景**：C720w 為 360x240（橫向）設計，常見 App 假設 240x320（直向）而出現 UI 排版錯位或被裁切。
**技術挑戰**：在 .NET CF/WinForms 上實作自適應 UI。
**影響範圍**：App 可用性、使用體驗、維運成本。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. UI 寫死絕對座標與尺寸。
2. 未偵測螢幕方向/解析度變化。
3. 缺乏最小支援尺寸策略。

**深層原因**：
- 架構層面：非響應式 UI 結構。
- 技術層面：未使用 Dock/Anchor 之類自適應控件。
- 流程層面：相容性測試覆蓋不足。

### Solution Design
**解決策略**：引入自適應布局與資源切分（橫/直向資源），加入螢幕偵測並根據模式重排。

**實施步驟**：
1. 螢幕偵測與重排
- 實作細節：啟動時讀取解析度與方向，動態設置控件 Anchor/Dock。
- 所需資源：Microsoft.WindowsCE.Forms
- 預估時間：2-3 小時

2. UI 資源切分與最小尺寸
- 實作細節：針對不同方向提供資源配置或程式化布局。
- 所需資源：專案資源管理
- 預估時間：3-4 小時

**關鍵程式碼/設定**：
```csharp
using Microsoft.WindowsCE.Forms;

public partial class MainForm : Form
{
    public MainForm()
    {
        InitializeComponent();
        AdaptLayout();
    }

    private void AdaptLayout()
    {
        int w = SystemSettings.ScreenWidth;
        int h = SystemSettings.ScreenHeight;
        var orientation = SystemSettings.ScreenOrientation;

        // 依螢幕設定 Dock/Anchor
        headerPanel.Dock = DockStyle.Top;
        contentPanel.Dock = DockStyle.Fill;
        actionPanel.Dock = DockStyle.Bottom;

        // 針對橫向縮放字體/間距
        if (w > h) {
            this.Font = new Font(this.Font.FontFamily, 8F, FontStyle.Regular);
            // 重新計算控制項寬高...
        }
    }
}
```

實際案例：原文提及 C720w 橫向螢幕與相容性差異。
實作環境：Windows Mobile 5/6、.NET CF 2.0/3.5。
實測數據：
- 改善前：相容性問題清單（待盤點）。
- 改善後：通過率提升（待量測）。
- 改善幅度：待量測。

Learning Points
- 小螢幕裝置 UI 響應式設計
- WinForms/CF 的 Dock/Anchor 應用
- 測試矩陣設計

技能要求
- 必備：WinForms 佈局、資源管理
- 進階：自動化 UI 測試

延伸思考
- 以 XAML/WPF 或 Web 混合技術降低相容性風險（新平台）
- 多 DPI 與主題資源管理

Practice Exercise
- 基礎：為一個表單做橫直向皆可用（30 分鐘）
- 進階：完成 UI 重排工具/函式庫（2 小時）
- 專案：改造一個舊 App 通過 320x240/240x320 測試（8 小時）

Assessment Criteria
- 功能完整性（40%）：橫直向皆可用
- 程式碼品質（30%）：結構清晰、易維護
- 效能（20%）：啟動/重排流暢
- 創新（10%）：佈局自動化工具


## Case #5: Outlook 同步可靠性強化與資料備援

### Problem Statement
**業務場景**：更換手機前後，需確保聯絡人/行事曆資料完整遷移且可雙向同步，避免遺漏與重複。
**技術挑戰**：ActiveSync 設定不當易產生重複或遺失。
**影響範圍**：通訊錄完整性、行程準確性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 初次同步未先備份。
2. 多端同步（PC/裝置）規則不明。
3. 類別/欄位對應不一致。

**深層原因**：
- 架構：缺乏前置備份與回復策略。
- 技術：不同裝置欄位支援差異。
- 流程：缺驗證清單與回歸測試。

### Solution Design
**解決策略**：先備份 PST/匯出 CSV，單一主端初次同步，啟用重複合併策略與小批量驗證。

**實施步驟**：
1. 備份與清理
- 實作細節：Outlook 匯出 PST/CSV；清理重複項。
- 所需資源：Outlook 桌面端
- 預估時間：1-2 小時

2. ActiveSync 規則設定
- 實作細節：設定同步方向、排程、衝突解決策略（以 PC 為主）。
- 所需資源：ActiveSync 4.x
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```text
ActiveSync 設定：
- Tools > Options > 選擇 Contacts/Calendar
- Rules/Conflicts：初次「以 PC 為主」
- Schedule：關閉 Push，採定時或手動（見 Case #14）
Outlook 匯出：
- File > Import and Export... > Export to a file > .pst / .csv
```

實際案例：原文強調 Smartphone + Outlook 的價值，對遷移可靠性有需求。
實作環境：Windows XP + Outlook 2003/2007、ActiveSync 4.5。
實測數據：
- 改善前：未知重複率/遺漏率。
- 改善後：抽樣比對 100 筆無遺漏/重複（待量測）。
- 改善幅度：待量測。

Learning Points
- 初次同步的安全策略
- 衝突解決與欄位對應
- 驗證清單設計

技能要求
- 必備：Outlook/ActiveSync 設定
- 進階：資料清理與比對（VBA/腳本）

延伸思考
- 雲端服務（Exchange/365）可降低風險
- 第三方 PIM 備份工具

Practice Exercise
- 基礎：完成 PST 備份與單向同步（30 分鐘）
- 進階：撰寫 VBA 比對重複聯絡人（2 小時）
- 專案：制定遷移 SOP 與檢核表（8 小時）

Assessment Criteria
- 功能完整性（40%）：備份/同步/驗證
- 程式碼品質（30%）：VBA/腳本健壯性
- 效能（20%）：遷移失誤率下降
- 創新（10%）：自動化驗證工具


## Case #6: 以 WiFi 取代 3G 的資料同步策略

### Problem Statement
**業務場景**：原文使用者「用不大到 3G」，C720w 具 WiFi。希望以 WiFi 完成資料同步，降低成本與耗電。
**技術挑戰**：避免裝置在行動網路上自動連線。
**影響範圍**：資費、待機時間、同步穩定性。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 行動資料自動連線設定開啟。
2. Push 同步觸發資料連線。
3. 應用預設允許任意網路連線。

**深層原因**：
- 架構：未定義「WiFi 優先」規則。
- 技術：無法區分網路類型的 App 設定。
- 流程：缺少同步時段規劃。

### Solution Design
**解決策略**：關閉 Push、改為手動/排程於 WiFi 可用時；移除行動資料 APN 或設為需手動撥號。

**實施步驟**：
1. 設定 ActiveSync
- 實作細節：Schedule 設為手動；或只在連 PC 時同步。
- 所需資源：ActiveSync
- 預估時間：10 分鐘

2. 連線管理
- 實作細節：移除/禁用資料 APN；僅保留 WiFi。
- 所需資源：裝置連線設定
- 預估時間：10-20 分鐘

**關鍵程式碼/設定**：
```text
ActiveSync > Menu > Schedule
- Peak/Off-peak: Manual
- When roaming: Do not sync
連線設定：
- Settings > Connections > GPRS/3G：刪除 APN 或改為手動撥號
- WiFi：設定已知 SSID，自動連線
```

實際案例：原文選擇放棄 3G，偏好 WiFi。
實作環境：Windows Mobile 5/6、ActiveSync 4.5。
實測數據：
- 改善前：月行動數據用量/待機時數（待量測）。
- 改善後：WiFi 為主、行動數據近零（待量測）。
- 改善幅度：待量測。

Learning Points
- 同步排程對耗電/資費的影響
- APN 管理與風險（Apps 需連線時）
- WiFi 覆蓋規劃

技能要求
- 必備：系統設定、WiFi 管理
- 進階：行為自動化（定時開關 WiFi）

延伸思考
- 在公司/家中場景自動同步
- 風險：無行動資料時緊急狀況無法連線

Practice Exercise
- 基礎：將同步改為手動並在 WiFi 下執行一次（30 分鐘）
- 進階：建立兩個時段自動化腳本（2 小時）
- 專案：月度用量/電力報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：設定正確、只在 WiFi 同步
- 程式碼品質（30%）：自動化腳本可維護
- 效能（20%）：耗電/資費下降
- 創新（10%）：情境自動化設計


## Case #7: 實體鍵盤提升輸入效率的評估與配置

### Problem Statement
**業務場景**：C720w 具 QWERTY 鍵盤，輸入文字密集（郵件/訊息）者可顯著增產。
**技術挑戰**：量化鍵盤對輸入效率的影響並最佳化快捷鍵。
**影響範圍**：郵件回覆速度、溝通效率。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. T9 與 QWERTY 輸入效率差距未被量化。
2. 快捷鍵/巨集未配置。
3. 手機輸入法設定未最佳化。

**深層原因**：
- 架構：缺乏輸入效能指標。
- 技術：快捷鍵不可用或未啟用。
- 流程：未建立輸入模板（簽名、常用片語）。

### Solution Design
**解決策略**：WPM 測試、快捷鍵映射、常用片語快速插入，建立前後對照。

**實施步驟**：
1. 基準 WPM 測試
- 實作細節：用同一段文字，測 T9 vs QWERTY。
- 所需資源：測試文本
- 預估時間：30 分鐘

2. 快捷鍵與片語
- 實作細節：設定 App 快捷鍵、建立常用片語模板。
- 所需資源：裝置設定、簡易工具
- 預估時間：30-60 分鐘

**關鍵程式碼/設定**：
```text
配置示例：
- 郵件 App：長按鍵對應「回覆全部」「加簽名」
- 常用片語：如「收到，謝謝」「請見附件」以縮寫展開
```

實際案例：原文將實體鍵盤列為 C720w 優勢之一。
實作環境：Windows Mobile 郵件/短信 App。
實測數據：
- 改善前：WPM（T9）（待量測）
- 改善後：WPM（QWERTY）（待量測）
- 改善幅度：待量測

Learning Points
- 輸入效率量化方法
- 快捷鍵/片語管理
- 生產力度量

技能要求
- 必備：系統與 App 快捷鍵設定
- 進階：自動展開片語腳本

延伸思考
- 外接藍牙鍵盤
- 語音輸入取代文字

Practice Exercise
- 基礎：完成 WPM 測試（30 分鐘）
- 進階：設定 5 個快捷鍵/片語（2 小時）
- 專案：郵件處理流程優化（8 小時）

Assessment Criteria
- 功能完整性（40%）：完成測試與配置
- 程式碼品質（30%）：片語展開正確
- 效能（20%）：WPM 提升
- 創新（10%）：工作流自動化


## Case #8: 綁約期間的採購時程與成本風險管理

### Problem Statement
**業務場景**：門號綁約至 2007/05，提前換機可能產生違約金。需規劃最佳換機時點。
**技術挑戰**：用數據評估「立即換機 vs 等合約到期」。
**影響範圍**：TCO、現金流、風險管理。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 違約金成本不明。
2. 換機帶來的效益未量化（待機/效率）。
3. 價格波動與新機發布節奏未知。

**深層原因**：
- 架構：缺失 TCO 模型。
- 技術：缺評估模板。
- 流程：無決策門檻（如 ROI>0 才提前）。

### Solution Design
**解決策略**：建立 TCO/ROI 計算模板，含違約金、時間價值與效率收益。

**實施步驟**：
1. 蒐集成本與效益數據
- 實作細節：違約金、機價、待機/效率提升帶來的產值估算。
- 所需資源：電信合約、內部人事成本
- 預估時間：1 小時

2. 產出決策報表
- 實作細節：做出現金流比較，找出盈虧平衡點。
- 所需資源：Excel
- 預估時間：1 小時

**關鍵程式碼/設定**：
```excel
# Excel（示意）
ROI = (效率提升帶來的月度產值 × 可用月數 - 違約金 - 新機差額) / 總成本
決策：若 ROI > 0 且 風險可接受 → 提前換機；否則等待到期
```

實際案例：原文選擇等待至 2007/05。
實作環境：Excel 或 Google Sheets。
實測數據：依實際填入（原文未提供）。

Learning Points
- TCO 與 ROI 在採購中的運用
- 風險緩解策略（等待/保留方案）

技能要求
- 必備：試算表、基本財務概念
- 進階：敏感度/情境分析

延伸思考
- 搭配促銷檔期/新機週期
- 二手機折舊/轉售價

Practice Exercise
- 基礎：建立一張 ROI 模板（30 分鐘）
- 進階：跑三種情境（2 小時）
- 專案：出具採購建議書（8 小時）

Assessment Criteria
- 功能完整性（40%）：模板與結論
- 資料品質（30%）：假設合理
- 效能（20%）：決策效率
- 創新（10%）：可視化


## Case #9: 無線電基帶韌體更新以改善掉話

### Problem Statement
**業務場景**：通話掉話與斷訊頻發，考慮是否存在基帶韌體缺陷。
**技術挑戰**：安全更新基帶，避免變磚。
**影響範圍**：通話穩定性、裝置可用性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 既有韌體版本已知缺陷。
2. 與營運商網路相容性不足。
3. 低電量保護策略過於保守。

**深層原因**：
- 架構：版本管理與回滾缺失。
- 技術：更新工具/流程不清楚。
- 流程：缺測試與備援裝置。

### Solution Design
**解決策略**：查詢 OEM/電信商公告，先備份資料，再於充足電量下更新，並保留回滾方案。

**實施步驟**：
1. 前置準備
- 實作細節：備份 PIM 資料、確認電量>80%、使用原廠 ROM。
- 所需資源：原廠更新工具、USB 線
- 預估時間：1 小時

2. 更新與驗證
- 實作細節：更新後進行通話壓測（連續通話測試）。
- 所需資源：測試腳本/清單
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
```text
更新要點：
- 僅使用 OEM 官方韌體
- 充電+接上電源，避免中斷
- 更新後撥測：連續 10 通、每通 10 分鐘、不同訊號條件
```

實際案例：原文掉話情境，可能受韌體影響（建議驗證）。
實作環境：OEM 更新工具。
實測數據：待量測（掉話率前後對比）。

Learning Points
- 基帶韌體與通話品質關係
- 更新風險控管

技能要求
- 必備：資料備份、更新操作
- 進階：測試計畫設計

延伸思考
- 不同基地台廠牌的相容性
- 若無官方更新則評估換機

Practice Exercise
- 基礎：撰寫更新前檢核表（30 分鐘）
- 進階：設計通話壓測腳本（2 小時）
- 專案：更新與測試報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：完成更新與測試
- 程式碼品質（30%）：測試腳本可用
- 效能（20%）：掉話率下降
- 創新（10%）：回滾策略


## Case #10: 高容量電池與電源校正

### Problem Statement
**業務場景**：待機不足，評估更換高容量電池與電源校正。
**技術挑戰**：選擇可靠電池並執行正確校正流程。
**影響範圍**：待機、通話時間。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 原電池老化。
2. 高負載時電壓下陷。
3. 校正不當導致電量顯示不準。

**深層原因**：
- 架構：無維護週期。
- 技術：選品不當/假電池風險。
- 流程：缺校正 SOP。

### Solution Design
**解決策略**：採購原廠或信譽良好副廠電池，完成三循環充放電校正。

**實施步驟**：
1. 選購與驗證
- 實作細節：序號/防偽查驗。
- 所需資源：供應商資訊
- 預估時間：1 小時

2. 校正流程
- 實作細節：充滿→使用至 10-15%→關機充滿，重複 2-3 次。
- 所需資源：充電器
- 預估時間：1-2 天（含循環）

**關鍵程式碼/設定**：
```text
校正紀錄表：
- 日期 / 充電起訖 / 使用時數 / 最低電量 / 體感
```

實際案例：原文待機過短。
實作環境：N/A。
實測數據：待量測（待機時數/通話分鐘）。

Learning Points
- 電池健康與容量/內阻
- 校正方法

技能要求
- 必備：選品與安全充電
- 進階：記錄與分析

延伸思考
- 原廠 vs 副廠權衡
- 行動電源備援

Practice Exercise
- 基礎：填寫一輪校正紀錄（30 分鐘）
- 進階：比較兩顆電池表現（2 小時）
- 專案：電池選型報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：完成校正
- 資料品質（30%）：紀錄完整
- 效能（20%）：待機改善
- 創新（10%）：可視化


## Case #11: 蜂窩不佳時的 WiFi VoIP 備援

### Problem Statement
**業務場景**：低電量或弱訊號時易掉話，考慮以 WiFi VoIP 作為備援通道。
**技術挑戰**：確保語音品質與可用性。
**影響範圍**：通話成功率、成本。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 蜂窩訊號弱/電量低。
2. 缺備援通話通道。
3. 網路切換不即時。

**深層原因**：
- 架構：單一通道依賴。
- 技術：VoIP 未部署。
- 流程：無切換 SOP。

### Solution Design
**解決策略**：在 WiFi 可用處使用 VoIP（如 Skype for WM 時代），並建立切換準則（低電量、弱訊號）。

**實施步驟**：
1. 安裝與設定 VoIP
- 實作細節：帳號登入、音訊測試。
- 所需資源：WiFi、耳麥
- 預估時間：30 分鐘

2. 切換策略
- 實作細節：低電量/弱訊號時，改用 VoIP 方案。
- 所需資源：內部 SOP
- 預估時間：30 分鐘

**關鍵程式碼/設定**：
```text
SOP：
- RSSI < 2 格 或 電量 < 20% → 以 WiFi + VoIP 撥打
- 優先使用有線/高品質 WiFi
```

實際案例：原文提 WiFi 為 C720w 優勢。
實作環境：Windows Mobile 可用之 VoIP App（歷史版本）。
實測數據：待量測（VoIP 成功率/通話品質 MOS）。

Learning Points
- 多通道通話的可用性設計
- VoIP 品質評估

技能要求
- 必備：網路設定、App 部署
- 進階：QoS/測試

延伸思考
- 現代可替換為 WhatsApp/Teams 等通話
- 對應安全策略

Practice Exercise
- 基礎：完成一次 WiFi 通話測試（30 分鐘）
- 進階：弱訊號場景測試（2 小時）
- 專案：備援通話策略文件（8 小時）

Assessment Criteria
- 功能完整性（40%）：通話可用
- 程式碼品質（30%）：N/A（流程/設定為主）
- 效能（20%）：成功率/品質
- 創新（10%）：自動提醒/切換建議


## Case #12: 應用相容性清單與驗證流程

### Problem Statement
**業務場景**：595（QVGA 直向）相容性較好；C720w 可能遇到相容性問題。需在換機前建立清單與驗證流程。
**技術挑戰**：確認關鍵 App 在不同解析度可用。
**影響範圍**：業務連續性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. App 未支援橫向/非標準比例。
2. 測試覆蓋不足。
3. 無替代 App 清單。

**深層原因**：
- 架構：缺應用目錄與分級。
- 技術：缺相容性標註。
- 流程：無切換回退計畫。

### Solution Design
**解決策略**：編制關鍵 App 清單，建立相容性測試卡與替代方案。

**實施步驟**：
1. 盤點與分級
- 實作細節：Must/Should/Could，標註解析度需求。
- 所需資源：內部需求訪談
- 預估時間：1 小時

2. 驗證與備援
- 實作細節：逐一測試，記錄問題，列出替代方案。
- 所需資源：測試表單
- 預估時間：2-4 小時

**關鍵程式碼/設定**：
```text
測試卡欄位：
- App 名稱 / 版本 / 解析度支援 / 橫向支援 / 測試結果 / 備援方案
```

實際案例：原文明確提及相容性差異。
實作環境：目標機種實機/模擬。
實測數據：通過率、阻斷項（待量測）。

Learning Points
- 相容性管理
- 測試文檔

技能要求
- 必備：測試方法
- 進階：替代 App 尋找

延伸思考
- 長期維護的應用目錄
- 版本迭代影響

Practice Exercise
- 基礎：建立 10 款 App 測試卡（30 分鐘）
- 進階：完成實測並標註結果（2 小時）
- 專案：相容性報告與建議（8 小時）

Assessment Criteria
- 功能完整性（40%）：清單+結果
- 資料品質（30%）：記錄可追溯
- 效能（20%）：阻斷風險降低
- 創新（10%）：替代方案完備


## Case #13: 2G/3G 網路模式設定以延長待機

### Problem Statement
**業務場景**：使用者「用不大到 3G」，且 3G 可能帶來更高耗電。需鎖定 2G 以延長待機。
**技術挑戰**：安全切換網路模式，避免無訊號。
**影響範圍**：待機時間、通話穩定性、資料連線。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 3G 掃描與駐網耗電較高。
2. 訊號切換頻繁增加功耗。
3. App 背景使用行動資料。

**深層原因**：
- 架構：未定義節能優先級。
- 技術：未鎖定網路模式。
- 流程：無例行檢查。

### Solution Design
**解決策略**：在可行範圍鎖定 GSM/2G 模式，必要時手動切回 3G。

**實施步驟**：
1. 調整網路模式
- 實作細節：設定 Network Type 為 GSM Only（裝置選單）。
- 所需資源：裝置設定
- 預估時間：10 分鐘

2. 驗證通話與簡訊
- 實作細節：進行撥測、收發簡訊測試。
- 所需資源：N/A
- 預估時間：20 分鐘

**關鍵程式碼/設定**：
```text
設定路徑（視機型而異）：
- Settings > Phone > Band/Network Type > GSM (2G) Only
注意：如需 3G 資料，手動切回「Auto/3G」
```

實際案例：原文決定放棄 3G。
實作環境：Windows Mobile 5/6。
實測數據：待量測（待機時數、通話成功率）。

Learning Points
- 網路模式對功耗影響
- 測試驗證流程

技能要求
- 必備：系統設定
- 進階：自動化切換（有風險）

延伸思考
- 現代網路（4G/5G）對應策略
- 覆蓋差區域的風險

Practice Exercise
- 基礎：切換為 2G 並完成撥測（30 分鐘）
- 進階：記錄 24 小時待機差異（2 小時配置+觀察）
- 專案：網路模式與耗電關聯報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：設定與測試
- 資料品質（30%）：記錄完整
- 效能（20%）：待機提升
- 創新（10%）：自動化提醒


## Case #14: Push 與排程同步策略以延長待機

### Problem Statement
**業務場景**：背景推播導致頻繁喚醒與資料連線，縮短待機。
**技術挑戰**：在可接受的延遲內平衡電力與同步。
**影響範圍**：待機時間、郵件及時性。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. Push 開啟。
2. 同步間隔過密。
3. Roaming 同步未關閉。

**深層原因**：
- 架構：未定義 SLA（延遲容忍）。
- 技術：排程未優化。
- 流程：無尖離峰策略。

### Solution Design
**解決策略**：關閉 Push，設定尖峰/離峰不同間隔，Roaming 禁止同步。

**實施步驟**：
1. 調整排程
- 實作細節：Peak 30-60 分、Off-peak 手動。
- 所需資源：ActiveSync
- 預估時間：10 分鐘

2. 驗證延遲
- 實作細節：測試郵件送達延遲與電力變化。
- 所需資源：測試郵件
- 預估時間：1 小時

**關鍵程式碼/設定**：
```text
ActiveSync > Menu > Schedule
- Peak times: Every 60 minutes
- Off-peak: Manual
- When roaming: Do not sync
```

實際案例：原文提待機短；此法為通用修正。
實作環境：ActiveSync 4.5。
實測數據：待量測（待機提升、郵件延遲）。

Learning Points
- 同步策略設計
- 用戶體驗 vs 電力

技能要求
- 必備：ActiveSync 設定
- 進階：SLA/OKR 設計

延伸思考
- 事件觸發同步（插電/連 WiFi）
- 高優先 vs 低優先郵件分流

Practice Exercise
- 基礎：修改排程與測試收郵延遲（30 分鐘）
- 進階：尖離峰配置（2 小時）
- 專案：同步策略 A/B 測試報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：設定與測試
- 資料品質（30%）：延遲/耗電記錄
- 效能（20%）：待機提升
- 創新（10%）：情境化策略


## Case #15: 電池與通話品質監測日誌工具開發（.NET CF）

### Problem Statement
**業務場景**：原文無實測數據。需要一個輕量日誌工具持續記錄電量、訊號、通話狀態，為優化提供證據。
**技術挑戰**：資源有限環境下穩定記錄且不影響續航。
**影響範圍**：資料驅動決策。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 無可用數據。
2. 人工記錄繁瑣。
3. 抽樣偏誤。

**深層原因**：
- 架構：缺監測/儲存機制。
- 技術：API 使用與省電取捨。
- 流程：資料分析缺口。

### Solution Design
**解決策略**：開發低頻抽樣（每 1-5 分）日誌工具，記錄至 CSV，支援事件觸發（通話開始/結束）。

**實施步驟**：
1. 事件與抽樣實作
- 實作細節：SystemState 電池/訊號/通話事件；Timer 低頻寫檔。
- 所需資源：.NET CF 2.0
- 預估時間：2-4 小時

2. 匯出與分析
- 實作細節：CSV 匯出至 PC，Excel 分析。
- 所需資源：ActiveSync
- 預估時間：1 小時

**關鍵程式碼/設定**：
```csharp
using Microsoft.WindowsMobile.Status;
using System.IO;
using System.Windows.Forms;

public class LoggerApp
{
    private string path = "\\My Documents\\powerlog.csv";
    private Timer timer = new Timer();

    public LoggerApp()
    {
        timer.Interval = 60000; // 1 min
        timer.Tick += (s,e)=>WriteRow("TICK");
        timer.Start();

        new SystemState(SystemProperty.PhoneCallTalking).Changed += (s,e)=>WriteRow("CALL");
    }

    private void WriteRow(string reason)
    {
        int batt = (int)SystemState.GetValue(SystemProperty.PowerBatteryStrength);
        int signal = (int)SystemState.GetValue(SystemProperty.PhoneSignalStrength);
        using (var sw = new StreamWriter(path, true))
        {
            sw.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss},{batt},{signal},{reason}");
        }
    }
}
```

實際案例：供原文場景量測改進。
實作環境：Windows Mobile 5/6、.NET CF 2.0。
實測數據：執行後產出（待量測）。

Learning Points
- 低資源環境開發
- 事件/抽樣混合監測

技能要求
- 必備：.NET CF 開發
- 進階：資料分析

延伸思考
- 視覺化 Dashboard
- 雲端上傳（當代替代）

Practice Exercise
- 基礎：完成日誌寫入（30 分鐘）
- 進階：加上 CSV 匯出與標記（2 小時）
- 專案：一週數據分析報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：穩定記錄
- 程式碼品質（30%）：資源管理
- 效能（20%）：低耗電
- 創新（10%）：視覺化


## Case #16: 舊機到新機的資料遷移與驗證

### Problem Statement
**業務場景**：從 Mio 8390 遷移至 C720w/595，需完整帶移聯絡人與行事曆，避免遺失。
**技術挑戰**：不同機型/韌體/解析度下的資料一致性。
**影響範圍**：營運連續。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 多端同步風險。
2. 欄位支援差異。
3. 缺驗證與回復。

**深層原因**：
- 架構：遷移 SOP 缺失。
- 技術：備份與還原工具多樣。
- 流程：無抽樣核對。

### Solution Design
**解決策略**：先在 PC 端統一資料源（Outlook），舊機→PC 同步、備份，PC→新機單向初始化，同步後抽樣核對。

**實施步驟**：
1. 舊機同步與備份
- 實作細節：舊機→PC 同步，導出 PST/CSV。
- 所需資源：Outlook/ActiveSync
- 預估時間：1 小時

2. 新機初始化與驗證
- 實作細節：PC→新機單向同步，抽樣核對 50-100 筆。
- 所需資源：ActiveSync
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
```text
SOP：
- 舊機：同步 → 匯出 PST → 關閉舊機同步
- 新機：首次同步設定以 PC 為主 → 完成初次後改回雙向
- 驗證：抽樣比對姓名/電話/生日/備註
```

實際案例：原文規劃換機。
實作環境：Outlook + ActiveSync。
實測數據：待量測（遺漏/重複率）。

Learning Points
- 低風險遷移
- 驗證與回復

技能要求
- 必備：ActiveSync/Outlook
- 進階：比對工具/腳本

延伸思考
- 改用雲端（Exchange）降低風險
- 多裝置同步策略

Practice Exercise
- 基礎：完成一次單向初始化（30 分鐘）
- 進階：抽樣比對與修正（2 小時）
- 專案：完整遷移報告（8 小時）

Assessment Criteria
- 功能完整性（40%）：遷移完成
- 資料品質（30%）：無遺漏/重複
- 效能（20%）：一次成功率
- 創新（10%）：自動化比對


--------------------------------
案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 6（WiFi 同步策略）
  - Case 7（鍵盤效率）
  - Case 8（綁約/TCO 模板）
  - Case 10（電池校正）
  - Case 13（2G/3G 模式）
  - Case 14（排程同步）
- 中級（需要一定基礎）
  - Case 1（待機優化）
  - Case 2（低電量掉話防護）
  - Case 5（Outlook 同步可靠性）
  - Case 11（VoIP 備援）
  - Case 12（相容性驗證）
  - Case 16（資料遷移）
  - Case 15（監測工具開發）
  - Case 3（選型決策矩陣）
- 高級（需要深厚經驗）
  - Case 4（UI 相容性改造）
  - Case 9（基帶韌體更新）

2) 按技術領域分類
- 架構設計類
  - Case 3、8、12
- 效能優化類
  - Case 1、10、13、14、15
- 整合開發類
  - Case 4、5、11、16
- 除錯診斷類
  - Case 2、9、15
- 安全防護類
  - Case 2（風險控制/防呆）

3) 按學習目標分類
- 概念理解型
  - Case 3、8、12
- 技能練習型
  - Case 5、6、7、10、13、14、16
- 問題解決型
  - Case 1、2、9、11、15
- 創新應用型
  - Case 4（UI 自適應）、Case 15（低資源監測）

--------------------------------
案例關聯圖（學習路徑建議）

- 建議先學：
  - Case 3（選型決策）→ 確立需求與評分框架
  - Case 1（待機優化基礎）→ 了解耗電要素
  - Case 14（同步策略）→ 快速見效的省電手段

- 依賴關係與順序：
  - Case 1 → Case 15（有監測數據再談優化）
  - Case 2 依賴 Case 1/15（需電量與通話事件監測）
  - Case 6/13（WiFi/2G 策略）依賴 Case 3（需求）與 Case 1（耗電效果）
  - Case 4（UI 改造）與 Case 12（相容性驗證）互補：設計與測試
  - Case 5（同步可靠性）→ Case 16（遷移落地）
  - Case 9（韌體更新）在 Case 2（掉話）且 Case 1/15（證據）後進行
  - Case 11（VoIP 備援）在 Case 2 之後作為替代通道
  - Case 8（綁約/TCO）貫穿決策前後，於 Case 3 後評估採購時點
  - Case 10（電池更換）在 Case 1 優化仍不足時採取

- 完整學習路徑建議：
  1) Case 3 → 明確需求與評估指標
  2) Case 1 → 建立耗電基準與初步優化
  3) Case 15 → 實作監測工具，蒐集數據
  4) Case 14、6、13 → 逐步套用同步與網路節能策略
  5) Case 2 → 低電量掉話風險控制
  6) Case 5 → 準備資料一致性基礎
  7) Case 12 → 應用相容性驗證
  8) Case 4 → 必要時進行 UI 改造（開發者）
  9) Case 11 → 建立 WiFi VoIP 備援
  10) Case 10 → 若續航仍不足，換電池+校正
  11) Case 9 → 韌體更新（有證據後）
  12) Case 8 → 完成 TCO/時程決策
  13) Case 16 → 執行資料遷移與驗證
  14) Case 7 → 鍵盤與工作流增產配置（收尾優化）

說明：以上案例均以原文提及的實際困擾與取捨為出發點，補充可操作的技術方案、程式碼（於需要之處）與可量測的指標設計，但不杜撰原文未提供的實際數據，保留「待量測」以鼓勵在實作/練習中完成驗證。