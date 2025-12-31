---
layout: synthesis
title: "IBM ThinkPad X111 ..."
synthesis_type: solution
source_post: /2005/06/29/ibm-thinkpad-x111/
redirect_from:
  - /2005/06/29/ibm-thinkpad-x111/solution/
postid: 2005-06-29-ibm-thinkpad-x111
---

以下結果基於原文有限資訊加以整理。說明：原文主要是採購與使用滿意度的簡述，未提供具體問題細節、量化數據與完整解法流程。為了達成教學、練習與評估的需求，以下共列出15個案例，其中：
- 直接抽取自原文脈絡的微案例：Case #1（SD 卡導向的機型選擇）、Case #4（採購過程有阻礙）。
- 其餘為從原文場景（X31/X40、內建 SD、1.8" HDD、低電壓 CPU、雙機佈署等）延伸的實務教學案例，屬於通用可複用的「衍生案例」。所有「實測數據」部分，原文未提供，以下以「建議評估指標/示例目標值」呈現，非原文實測。

## Case #1: 以 SD 卡工作流為核心的機型選型與照片導入自動化

### Problem Statement（問題陳述）
- 業務場景：兩位使用者常用 SD 卡相機拍攝，需頻繁把照片匯入筆電。考量日常便利性與攜帶性，選擇內建 SD 讀卡機的機型，減少外接設備依賴，提升導入效率與穩定性。
- 技術挑戰：避免外接讀卡機不穩定與插拔頻繁造成的接觸不良，並建立一致、低錯誤率的照片導入流程與檔案命名規範。
- 影響範圍：若導入流程低效，將影響使用者時間成本、照片整理正確性與資料安全性。
- 複雜度評級：低

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 依賴外接讀卡機，插拔繁瑣且易接觸不良。
  2. 手動複製流程不一致，易遺漏或重複導入。
  3. 檔案命名與目錄結構缺乏標準，後續整理困難。
- 深層原因：
  - 架構層面：裝置存取流程缺少自動化與標準化。
  - 技術層面：未建立熱插拔觸發的導入腳本與去重邏輯。
  - 流程層面：未定義導入、驗證、備份到歸檔的「端到端」流程。

### Solution Design（解決方案設計）
- 解決策略：選擇內建 SD 讀卡機的機型，並建立自動導入腳本與資料結構規範，從插卡、導入、去重、按日期分檔到備份，一次到位，將人工作業轉為可重複的自動化流程。

- 實施步驟：
  1. 建立自動導入腳本
     - 實作細節：偵測可移除磁碟，掃描 DCIM，按拍攝日期建立資料夾並去重導入。
     - 所需資源：PowerShell 或 Bash、排程器（Windows Task Scheduler 或 udev/cron）
     - 預估時間：1 小時
  2. 制定目錄與命名規範
     - 實作細節：YYYY/MM/DD/相機代號；檔名加上拍攝時間與hash短碼
     - 所需資源：團隊規範文件
     - 預估時間：30 分鐘

- 關鍵程式碼/設定：
```powershell
# 自動導入 SD 卡照片（Windows/PowerShell）
$sd = Get-WmiObject Win32_LogicalDisk | Where-Object {$_.DriveType -eq 2} | Select-Object -First 1
if ($sd) {
  $src = Join-Path $sd.DeviceID 'DCIM'
  $date = Get-Date -Format 'yyyyMMdd'
  $dst = Join-Path "$env:USERPROFILE\Pictures" "Import\$date"
  New-Item -ItemType Directory -Force -Path $dst | Out-Null

  Get-ChildItem $src -Recurse -Include *.JPG,*.JPEG,*.PNG,*.MP4 |
    ForEach-Object {
      $hash = (Get-FileHash $_.FullName -Algorithm MD5).Hash.Substring(0,8)
      $newName = "{0}_{1}{2}" -f $_.BaseName, $hash, $_.Extension
      $target = Join-Path $dst $newName
      if (-not (Test-Path $target)) {
        Copy-Item $_.FullName $target
      }
    }
}
```

- 實際案例：原文中以「兩人皆用 SD 卡相機」作為選型依據，選擇內建 SD 的機型。
- 實作環境：Windows 或 Linux 皆可；PowerShell 5+/Bash
- 實測數據：
  - 改善前：手動導入約 3-5 分鐘/次（易重複導入）
  - 改善後：自動導入約 30-60 秒/次（含去重）
  - 改善幅度：導入耗時目標下降 60-80%（示例目標值）

- Learning Points（學習要點）
  - 核心知識點：
    - 以需求（SD 卡頻繁導入）驅動的機型選型
    - 可移除裝置偵測與自動化腳本
    - 去重與命名規範的重要性
  - 技能要求：
    - 必備技能：基礎腳本、檔案系統操作
    - 進階技能：事件驅動自動化、hash 去重
  - 延伸思考：
    - 可擴展到相機 RAW 工作流與雲端備份
    - 風險：腳本錯誤可能造成誤刪；需先做備份
    - 優化：加入 EXIF 解析與自動相簿分類

- Practice Exercise（練習題）
  - 基礎練習：改寫腳本，僅導入最近7天檔案（30 分鐘）
  - 進階練習：加入 EXIF 拍攝日期判斷與 RAW 檔支援（2 小時）
  - 專案練習：建置完整照片導入、備份、雲端同步管線（8 小時）

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：能偵測 SD、去重、分檔
  - 程式碼品質（30%）：結構清晰、錯誤處理、日誌
  - 效能優化（20%）：導入耗時、CPU/IO 負載
  - 創新性（10%）：EXIF/AI 標籤、自動分類

---

## Case #2: 雙機一致性佈署（Golden Image）降低重複安裝成本

### Problem Statement
- 業務場景：同時購置兩台 X40，若逐台手動安裝 OS/驅動/工具將耗時且易不一致，影響後續維護。
- 技術挑戰：建立可重複、可移植的標準化系統映像，確保兩台機器配置一致。
- 影響範圍：佈署時間、穩定性、維護成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 手動安裝重複且易遺漏步驟
  2. 驅動版本不一致導致不穩定
  3. 使用者設定差異造成體驗不一
- 深層原因：
  - 架構層面：缺乏標準化映像與設定版本控管
  - 技術層面：未掌握佈署工具（Sysprep/Clonezilla）
  - 流程層面：未定義佈署與驗證清單

### Solution Design
- 解決策略：建立一台基準機，完成 OS/驅動/套件與設定，使用 Sysprep 通用化後，透過 Clonezilla 等工具製作映像並複製到第二台。

- 實施步驟：
  1. 建立基準映像
     - 實作細節：安裝 OS、驅動、更新、必要軟體；清理暫存
     - 所需資源：驅動包、更新離線包
     - 預估時間：2-3 小時
  2. Sysprep 與映像佈署
     - 實作細節：Sysprep 通用化並關機，使用 Clonezilla 製作/還原
     - 所需資源：Sysprep、Clonezilla USB
     - 預估時間：1-2 小時

- 關鍵程式碼/設定：
```cmd
:: 通用化並準備 OOBE（Windows）
C:\Windows\System32\Sysprep\Sysprep.exe /generalize /oobe /shutdown
```

- 實際案例：原文提及一次性購買兩台 X40，適合導入雙機一致佈署。
- 實作環境：Windows/Linux 皆可；Windows 建議 Sysprep+Clonezilla，Linux 可用 dd/partclone
- 實測數據：
  - 改善前：逐台安裝 3-4 小時/台
  - 改善後：基準機 3 小時 + 複製 1 小時/台
  - 改善幅度：總工時目標下降 30-50%（示例目標值）

- Learning Points
  - 核心知識點：Golden Image、Sysprep、Clonezilla
  - 技能要求：磁碟映像、驅動整合
  - 延伸思考：後續可加入自動化設定後置腳本

- Practice Exercise
  - 基礎：列出驅動與軟體白名單（30 分鐘）
  - 進階：完成一次 Sysprep + 還原（2 小時）
  - 專案：建立可版本控管的映像流程（8 小時）

- Assessment
  - 功能完整性：映像可開機且驅動正常
  - 程式碼品質：腳本化後置設定
  - 效能：佈署時間縮短
  - 創新性：版本控管與自動驗證

---

## Case #3: 桌機到新筆電的資料移轉與結構化歸檔

### Problem Statement
- 業務場景：從舊桌機遷移大量文件、照片與個人設定到兩台新 X40，需兼顧正確性、速度與結構化歸檔。
- 技術挑戰：避免遺漏或重複檔案，確保資料校驗與一致結構。
- 影響範圍：資料完整性、使用者上手速度。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：手動 copy 易遺漏；不同使用者結構不一致；缺乏校驗
- 深層原因：
  - 架構：未定義跨設備資料結構
  - 技術：缺少校驗與日誌
  - 流程：缺少清單與驗收步驟

### Solution Design
- 解決策略：使用 Robocopy/rsync 建立可重跑的鏡像遷移流程，含日誌、排除、校驗與結構規範。

- 實施步驟：
  1. 規劃目錄與排除清單
     - 細節：明確使用者資料夾、排除 Temp/Cache
     - 資源：目錄清單文件
     - 時間：30 分鐘
  2. 執行鏡像與驗收
     - 細節：Robocopy/rsync + 校驗 + 日誌
     - 資源：外接硬碟
     - 時間：1-2 小時

- 關鍵程式碼/設定：
```cmd
:: Windows：鏡像遷移（含重試、日誌）
robocopy "D:\Users\Old" "E:\Migrate\Old" /MIR /R:1 /W:1 /XD Temp Cache /LOG+:migrate.log /TEE
```

- 實測數據（建議指標）：
  - 改善前：手動搬移錯漏率高
  - 改善後：0 遺漏（以日誌與隨機抽驗驗證）
  - 幅度：錯漏率降至可忽略（目標）

- Learning Points：檔案鏡像、排除策略、日誌校驗
- Practice：設計排除清單（30 分）、加上 hash 校驗（2 小時）、完整遷移專案（8 小時）
- Assessment：完整性40/品質30/效能20/創新10

---

## Case #4: 採購議價與流程標準化（原文提及過程「OOXX」）

### Problem Statement
- 業務場景：一次買兩台，價格談妥但過程有阻礙（OOXX）。需建立清晰需求、書面報價、交付驗收流程，降低溝通成本。
- 技術挑戰：多商家比價與規格對齊、避免漏配或規格誤解。
- 影響範圍：採購時間、成本、客訴風險。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：口頭溝通易誤解；報價項缺漏；無驗收清單
- 深層原因：
  - 架構：缺乏採購模板與比價欄位
  - 技術：無自動化比價與驗算
  - 流程：無書面確認與里程碑

### Solution Design
- 解決策略：制定標準需求書、比價表與驗收清單，價格與配件逐項對齊，以書面為準；用小工具計算總價與折扣。

- 實施步驟：
  1. 需求與比價模板
     - 細節：CPU/RAM/HDD/配件/保固/交期欄位
     - 資源：Spreadsheet
     - 時間：30 分鐘
  2. 自動化驗算
     - 細節：用腳本計總價、折扣、單價/配件拆分
     - 資源：Python
     - 時間：30 分鐘

- 關鍵程式碼/設定：
```python
items = [
  {"name":"ThinkPad X40", "unit": 45000, "qty": 2, "discount": 0.05},
  {"name":"RAM 512MB", "unit": 1200, "qty": 2, "discount": 0.00},
]
total = sum(i["unit"]*i["qty"]*(1-i["discount"]) for i in items)
print(f"Total: {total:,}")
```

- 實測數據（建議指標）：
  - 改善目標：議價往返次數下降 30%+；驗收缺漏 0 件

- Learning Points：需求規格化、比價驗算
- Practice：建立比價模板（30 分）、加入多商家比價匯出（2 小時）、完整採購流程範本（8 小時）
- Assessment：完整性40/品質30/效能20/創新10

---

## Case #5: 1.8 吋 HDD I/O 最佳化（低速碟的系統調優）

### Problem Statement
- 業務場景：X40 使用 1.8" HDD，隨機 IO 慢造成開機與應用啟動延遲。
- 技術挑戰：在不更換硬體前提下降低磁碟 IO 負載。
- 影響範圍：啟動時間、系統回應。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：1.8" HDD 隨機讀寫性能弱；背景索引/更新佔用 I/O
- 深層原因：
  - 架構：未分層快取與延後任務
  - 技術：檔案系統選項未優化
  - 流程：開機自啟動過多

### Solution Design
- 解決策略：關閉不必要索引、調整檔案系統選項（Linux noatime）、減少啟動程序，並定期重整磁碟。

- 實施步驟：
  1. 調整檔案系統/索引
     - 細節：Windows 關閉索引服務；Linux noatime
     - 資源：系統設定、fstab
     - 時間：30 分鐘
  2. 啟動精簡與排程維護
     - 細節：禁用不必要自啟；排程 defrag
     - 資源：Autoruns/Task Scheduler
     - 時間：30 分鐘

- 關鍵程式碼/設定：
```ini
# /etc/fstab（Linux）：避免更新 atime 以減少寫入
UUID=xxxx-xxxx / ext4 defaults,noatime,nodiratime 0 1
```

- 實測數據（建議指標）：
  - 目標：開機時間下降 20-40%；磁碟佔用峰值下降

- Learning Points：磁碟 IO 行為、檔案系統選項
- Practice：測試 noatime 的效應（30 分）、量測開機差異（2 小時）、寫報告（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #6: 低電壓 CPU 的開機與常駐程式精簡

### Problem Statement
- 業務場景：Pentium M LV 1.1GHz 對常駐程式敏感，過多常駐拖慢系統。
- 技術挑戰：識別與關閉非必要啟動項，維持功能不受影響。
- 影響範圍：開機時間、互動延遲。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：自啟動程式過多；排程任務過於頻繁
- 深層原因：
  - 架構：缺乏應用白名單
  - 技術：不了解 Run/Services/Tasks 註冊位置
  - 流程：安裝軟體默認自啟未清理

### Solution Design
- 解決策略：建立啟動白名單，關閉不必要的 Run/Services/Tasks 項，並以量測驗證。

- 實施步驟：
  1. 盤點啟動項
     - 細節：列出 Run、服務、排程任務
     - 資源：PowerShell、Autoruns
     - 時間：30 分鐘
  2. 精簡與驗證
     - 細節：禁用非必要項，量測開機時間
     - 資源：powercfg/BootRacer
     - 時間：30 分鐘

- 關鍵程式碼/設定：
```powershell
# 列出常見啟動項（Windows）
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
Get-ItemProperty "HKLM:\Software\Microsoft\Windows\CurrentVersion\Run"
Get-ScheduledTask | Where State -eq 'Ready' | Select TaskName,TaskPath
```

- 實測數據（建議指標）：開機時間目標下降 20-30%，CPU 峰值更平滑

- Learning Points：啟動機制、瓶頸辨識
- Practice：建立白名單（30 分）、精簡并量測（2 小時）、完整優化報告（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #7: 記憶體與分頁檔策略（低 RAM 環境優化）

### Problem Statement
- 業務場景：內建 256MB + 插槽 512MB 的低 RAM 環境下，分頁檔策略將影響體驗。
- 技術挑戰：在 RAM 受限下平衡分頁檔大小、磁碟負載與穩定性。
- 影響範圍：多工能力、應用切換延遲。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：RAM 不足導致頻繁分頁；分頁檔大小不當
- 深層原因：
  - 架構：缺少記憶體監測與警戒線
  - 技術：不了解分頁對 I/O 的影響
  - 流程：安裝過多背景程式

### Solution Design
- 解決策略：監測工作集，設定固定大小分頁檔，降低碎片與無序擴張；精簡常駐。

- 實施步驟：
  1. 監測與決策
     - 細節：記錄高峰 RAM 使用量
     - 資源：Performance Monitor
     - 時間：30 分鐘
  2. 設定分頁檔
     - 細節：固定大小，靠近磁碟外圈（若可）
     - 資源：WMIC/系統設定
     - 時間：15 分鐘

- 關鍵程式碼/設定：
```cmd
:: 停用自動分頁並設定固定大小（Windows）
wmic computersystem where name="%computername%" set AutomaticManagedPagefile=False
wmic pagefileset where name="C:\\pagefile.sys" set InitialSize=1024,MaximumSize=1024
```

- 實測數據（建議指標）：前後切換延遲下降；磁碟佔用更穩定

- Learning Points：分頁機制、記憶體監測
- Practice：量測不同大小影響（30 分）、撰寫報告（2 小時）、導入團隊基準（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #8: 電池續航與校正（行前準備）

### Problem Statement
- 業務場景：出國唸書/差旅需要長續航，須以設定與校正延長電池可用時間與壽命。
- 技術挑戰：建立省電計畫、關閉高耗能項、校正電池。
- 影響範圍：外出生產力、電池老化速度。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：螢幕亮度過高、無線持續掃描、背景程式耗電
- 深層原因：
  - 架構：缺乏電源管理策略
  - 技術：不了解 powercfg/校正流程
  - 流程：未定期健康檢查

### Solution Design
- 解決策略：建立省電電源計畫、關閉不必要硬體（藍牙/無線）、定期做電池報告與校正。

- 實施步驟：
  1. 建立省電計畫
     - 細節：降低亮度、CPU 最低/最大狀態
     - 資源：powercfg
     - 時間：15 分鐘
  2. 健康檢查與校正
     - 細節：batteryreport、完整放充
     - 資源：電源管理工具
     - 時間：1-2 小時

- 關鍵程式碼/設定：
```cmd
:: 產生電池報告（Windows 8+）
powercfg /batteryreport /output "%USERPROFILE%\Desktop\battery-report.html"
```

- 實測數據（建議指標）：續航提升 10-20% 目標；健康度趨勢穩定

- Learning Points：電源管理、電池健康
- Practice：產出報告（30 分）、調參前後對比（2 小時）、長期追蹤專案（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #9: 無內建光碟的作業系統安裝（USB 可開機）

### Problem Statement
- 業務場景：若無內建光碟，需以 USB 安裝系統或從外接光碟開機。
- 技術挑戰：製作可開機 USB、BIOS 設定與相容性。
- 影響範圍：重灌/佈署效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：缺乏光碟；USB 相容性不一
- 深層原因：
  - 架構：未事先準備開機媒體
  - 技術：DiskPart/UEFI/Legacy 差異
  - 流程：未定義重灌步驟

### Solution Design
- 解決策略：以 DiskPart 製作 FAT32 開機碟，BIOS 設定 USB boot priority，必要時用外接光碟。

- 實施步驟：
  1. 製作 USB
     - 細節：清碟、主分割、FAT32、Active
     - 資源：DiskPart、ISO
     - 時間：15-30 分鐘
  2. BIOS 設定與安裝
     - 細節：啟用 USB boot、Legacy/UEFI 調整
     - 資源：BIOS
     - 時間：15 分鐘

- 關鍵程式碼/設定：
```cmd
:: DiskPart 指令
diskpart
list disk
select disk X
clean
create partition primary
active
format fs=fat32 quick
assign
exit
xcopy X:\* Y:\ /E /H
```

- 實測數據（建議指標）：重灌時間目標 < 30-45 分鐘

- Learning Points：開機介質製作、BIOS 設定
- Practice：製作 USB 並試開機（30 分）、安裝並記錄耗時（2 小時）、撰寫 SOP（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #10: SD 卡相容性與效能驗證（選卡與讀卡機匹配）

### Problem Statement
- 業務場景：相機與筆電內建 SD 讀卡機之間需相容且足夠快，以免導入瓶頸。
- 技術挑戰：測試不同卡片速度、可靠度與誤碼情形。
- 影響範圍：導入時間、資料完整性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：卡片速度等級差異；讀寫相容問題
- 深層原因：
  - 架構：未定義效能底線
  - 技術：缺乏一致測試方法
  - 流程：未建立驗收流程

### Solution Design
- 解決策略：建立基準測試（順序/隨機）、誤碼檢測與最低標準，據此選卡與讀卡機。

- 實施步驟：
  1. 基準測試
     - 細節：順序寫/讀、隨機讀寫
     - 資源：dd/diskspd/H2testw
     - 時間：30-60 分鐘
  2. 驗收與記錄
     - 細節：記錄結果與合格標準
     - 資源：表單
     - 時間：30 分鐘

- 關鍵程式碼/設定：
```bash
# Linux：順序寫讀測試（注意將 of 設為 SD 裝置的測試檔，勿覆蓋裝置頭）
dd if=/dev/zero of=/media/sd/test.bin bs=64K count=4096 oflag=direct
dd if=/media/sd/test.bin of=/dev/null bs=64K iflag=direct
```

- 實測數據（建議指標）：順序讀寫 > 20-30MB/s（依設備標準）；0 誤碼

- Learning Points：I/O 測試方法、品質驗收
- Practice：撰寫測試腳本（30 分）、多卡比對報告（2 小時）、制定選型標準（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #11: TrackPoint/滑鼠靈敏度與精度調校

### Problem Statement
- 業務場景：長時間使用 TrackPoint 或小黑鼠，需兼顧精確與舒適度。
- 技術挑戰：調整靈敏度、加速度、滾輪行為。
- 影響範圍：輸入效率、疲勞度。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：默認靈敏度不適合個人
- 深層原因：
  - 架構：未建立配置檔與備份
  - 技術：不熟悉註冊表或 Xinput
  - 流程：未保存個人參數

### Solution Design
- 解決策略：建立可重現的設定檔，將靈敏度/加速度標準化並雲端同步。

- 實施步驟：
  1. 參數試調與導出
     - 細節：測試多組，選定最佳
     - 資源：註冊表/Xinput
     - 時間：30 分鐘
  2. 自動套用
     - 細節：登入時自動套用參數
     - 資源：登入腳本
     - 時間：15 分鐘

- 關鍵程式碼/設定：
```cmd
:: Windows 設定滑鼠靈敏度（示例）
reg add "HKCU\Control Panel\Mouse" /v MouseSensitivity /t REG_SZ /d 12 /f
reg add "HKCU\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d 1 /f
```

- 實測數據（建議指標）：指標鎖定目標更精準、選字誤差率下降

- Learning Points：人機參數調優、設定可移植性
- Practice：建立個人配置檔（30 分）、多裝置同步方案（2 小時）、撰寫使用指南（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #12: 小容量硬碟的備份策略（40GB HDD）

### Problem Statement
- 業務場景：40GB 硬碟空間有限，需建立高效率、差異化備份，避免滿盤與備份失敗。
- 技術挑戰：選擇差異/增量備份、排除不必要資料、確保可還原。
- 影響範圍：資料安全、空間利用。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：全量備份占空間、耗時
- 深層原因：
  - 架構：無備份策略（3-2-1）
  - 技術：不熟差異/增量工具
  - 流程：無定期驗還原

### Solution Design
- 解決策略：以 3-2-1 為基準：本地差異備份 + 外接硬碟週期全量 + 雲端重要檔案同步；定期驗還原。

- 實施步驟：
  1. 差異備份排程
     - 細節：robocopy 只備份變更
     - 資源：Task Scheduler
     - 時間：30 分鐘
  2. 還原演練
     - 細節：隨機抽檔還原檢驗
     - 資源：外接硬碟
     - 時間：30 分鐘

- 關鍵程式碼/設定：
```cmd
:: 差異備份（Windows）
robocopy "C:\Users\Me\Documents" "E:\Backup\Documents" /E /XO /FFT /R:1 /W:1 /LOG+:backup.log
```

- 實測數據（建議指標）：備份成功率 100%；還原抽驗通過率 100%

- Learning Points：3-2-1 策略、差異備份
- Practice：設定排程（30 分）、驗還原演練（2 小時）、撰寫 SOP（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #13: 行動使用資料保護（加密容器/磁碟）

### Problem Statement
- 業務場景：出國或攜帶筆電時需保護敏感資料，避免遺失外洩。
- 技術挑戰：低資源系統上導入輕量加密且兼顧效能。
- 影響範圍：資料安全、合規。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：行動場景風險高；未加密
- 深層原因：
  - 架構：無分級保護策略
  - 技術：不熟加密工具（VeraCrypt 等）
  - 流程：密碼與金鑰治理不足

### Solution Design
- 解決策略：建立加密容器（或全碟），採強密碼與金鑰備援；將敏感資料集中存放容器中。

- 實施步驟：
  1. 建立與掛載容器
     - 細節：AES 加密、NTFS/ext4
     - 資源：VeraCrypt
     - 時間：30-60 分鐘
  2. 政策與備援
     - 細節：密碼策略、金鑰備份離線保存
     - 資源：密碼管理器
     - 時間：30 分鐘

- 關鍵程式碼/設定：
```bash
# VeraCrypt（CLI 介面因平台而異，避免在命令列明文密碼）
veracrypt --text --create /path/Secure.vc --size 2G --encryption AES --hash SHA-512 --filesystem NTFS
veracrypt --text --mount /path/Secure.vc /mnt/secure
```

- 實測數據（建議指標）：性能損耗可接受（目標 <10-15%）；0 資料外洩事件

- Learning Points：威脅模型、加密實務
- Practice：建立容器與掛載（30 分）、整合備份（2 小時）、撰寫安全政策（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #14: 多設備資產與保固管理（雙機情境）

### Problem Statement
- 業務場景：同時管理 X31 + X40 + X40，需追蹤序號、購買日期、保固到期、配件。
- 技術挑戰：建立資產台帳與到期提醒。
- 影響範圍：維保效率、成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：無台帳、到期無提醒
- 深層原因：
  - 架構：缺乏集中化資產資料
  - 技術：未自動化提醒
  - 流程：交接與維護不明

### Solution Design
- 解決策略：以 CSV 管理資產，腳本產出即將到期清單與提醒郵件。

- 實施步驟：
  1. 建立台帳
     - 細節：序號/購買日/到期日/配件/使用者
     - 資源：Spreadsheet
     - 時間：30 分鐘
  2. 自動提醒
     - 細節：腳本計算剩餘天數並寄信
     - 資源：Python/SMTP
     - 時間：30 分鐘

- 關鍵程式碼/設定：
```python
import csv, datetime
today = datetime.date.today()
with open('assets.csv') as f:
    for r in csv.DictReader(f):
        due = datetime.datetime.strptime(r['warranty_until'], "%Y-%m-%d").date()
        days = (due - today).days
        if days <= 30:
            print(f"[提醒] {r['device']} 序號{r['sn']} 30天內到期（{days}天）")
```

- 實測數據（建議指標）：到期漏掉 0 件；維保回應時間縮短

- Learning Points：資產管理、到期治理
- Practice：建 CSV（30 分）、加入郵件通知（2 小時）、導入部門（8 小時）
- Assessment：完整性/品質/效能/創新

---

## Case #15: 驅動與應用統一安裝（雙機快速就緒）

### Problem Statement
- 業務場景：兩台新機需要一致的驅動與常用軟體版本，避免版本漂移。
- 技術挑戰：以腳本自動安裝、記錄與可重跑。
- 影響範圍：穩定性、維護成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：手動安裝易版本不一致
- 深層原因：
  - 架構：無套件清單與版本鎖定
  - 技術：缺乏安裝自動化
  - 流程：無變更紀錄

### Solution Design
- 解決策略：建立驅動與軟體清單，使用套件管理器（Windows 可用 Chocolatey/winget；Linux 用 apt/yum）批次安裝並記錄日誌。

- 實施步驟：
  1. 清單與版本鎖定
     - 細節：列出必裝與版本
     - 資源：packages.txt
     - 時間：30 分鐘
  2. 腳本安裝與驗證
     - 細節：安裝後列版本，產生日誌
     - 資源：套件管理器
     - 時間：30-60 分鐘

- 關鍵程式碼/設定：
```powershell
# Windows（示例以 winget 為例）
winget import --import-file packages.json --accept-source-agreements --accept-package-agreements
winget list > installed.txt
```

- 實測數據（建議指標）：兩機差異 0；安裝時間目標 < 30 分鐘/台

- Learning Points：版本控管、安裝自動化
- Practice：編寫 packages.json（30 分）、加入版本鎖定與回溯（2 小時）、整合映像流程（8 小時）
- Assessment：完整性/品質/效能/創新

------------------------------------------------------------

案例分類

1) 按難度分類
- 入門級：Case 1, 4, 8, 11, 14
- 中級：Case 2, 3, 5, 6, 7, 10, 12, 15
- 高級：Case 9, 13

2) 按技術領域分類
- 架構設計類：Case 2, 4, 12, 14, 15
- 效能優化類：Case 5, 6, 7, 8, 10, 11
- 整合開發類：Case 1, 2, 3, 9, 12, 15
- 除錯診斷類：Case 5, 6, 7, 10
- 安全防護類：Case 13, 14

3) 按學習目標分類
- 概念理解型：Case 1, 4, 8, 14
- 技能練習型：Case 3, 5, 6, 7, 10, 11, 12, 15
- 問題解決型：Case 2, 9, 13
- 創新應用型：Case 1, 5, 12（流程優化/自動化延伸）

案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 1（需求導向選型與自動化思維）
  - Case 4（規格化與流程意識）
  - Case 3（資料移轉基本功）
  - Case 12（備份觀念與實作）
- 依賴關係：
  - Case 2 依賴 Case 15（驅動/套件清單）與 Case 3（資料移轉）
  - Case 5/6/7/8（效能與電源優化）可在 Case 2 後進行
  - Case 9（USB 安裝）在安裝/重灌需求時與 Case 2 並行
  - Case 10（SD 效能）與 Case 1（SD 流程）互補
  - Case 13（加密）與 Case 12（備份）須協同規劃
  - Case 14（資產/保固）覆蓋整體生命週期
- 完整學習路徑：
  1 → 4 → 3 → 12 → 15 → 2 → 5 → 6 → 7 → 8 → 10 → 11 → 9 → 13 → 14

備註：原文未提供量化成效與技術細節，以上案例為在原始場景之上建立的可操作教學設計，供實戰練習與能力評估之用。若您能提供更完整的原始問題、遇到的具體錯誤訊息或量測數據，可再將各案例細化為更貼近真實的端到端解決方案。