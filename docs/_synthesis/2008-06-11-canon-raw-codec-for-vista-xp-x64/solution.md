---
layout: synthesis
title: "Canon Raw Codec for Vista / XP x64 ..."
synthesis_type: solution
source_post: /2008/06/11/canon-raw-codec-for-vista-xp-x64/
redirect_from:
  - /2008/06/11/canon-raw-codec-for-vista-xp-x64/solution/
---

以下內容基於原文主題（Vista/XP x64 上的 Canon CR2 RAW 檔案預覽/解碼問題）萃取並延伸出可操作的教學案例。說明：原文明確提到兩條解法線索（第三方 x64 編解碼器、在 Vista x64 以 WOW64 跑 32 位元方案），但並未提供實測數據。因此所有案例均不虛構效益數值，並提供可量測的方法。若需嚴格只取原文直述範圍，優先參考 Case 1 與 Case 2。

## Case #1: Vista x64 無法預覽 CR2，改用第三方 x64 編解碼器（原文直述）

### Problem Statement（問題陳述）
- 業務場景：攝影工作者在 Windows Vista x64 以檔案總管瀏覽 Canon CR2 檔，需要快速挑片與產生縮圖，但系統僅顯示通用圖示，無法預覽內容，影響檔案管理與初步篩選工作。
- 技術挑戰：缺少官方 x64 版 Canon RAW Codec，64 位元檔案總管無法載入 32 位元編解碼器。
- 影響範圍：Explorer 縮圖、Windows Photo Gallery 檢視、其他依賴 WIC 的應用。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 64 位元 Explorer 僅能載入 64 位元 WIC 編解碼器，官方僅有 32 位元版本。
  2. CR2 為相機廠牌自有 RAW 格式，缺省系統無通用解碼器。
  3. WIC 解碼器未註冊於 64 位元登錄機碼，導致系統不識別。
- 深層原因：
  - 架構層面：WIC/COM 元件按位元分流，64/32 位元互不相容。
  - 技術層面：供應商缺少 x64 釋出，僅能依賴第三方。
  - 流程層面：環境建置未納入影像編解碼元件相依性管理。

### Solution Design（解決方案設計）
- 解決策略：採購並部署支援 x64 的第三方 CR2 編解碼器（如 Ardfry CR2 Codec x64），完成安裝與註冊，清空縮圖快取後驗證 Explorer/Photo Gallery 可即時預覽。

- 實施步驟：
  1. 確認作業系統與 Explorer 位元
     - 實作細節：在工作管理員確認 explorer.exe 非標示為 *32（表示 64 位），或於系統資訊檢視 x64。
     - 所需資源：系統資訊、工作管理員
     - 預估時間：5 分鐘
  2. 安裝第三方 x64 CR2 Codec
     - 實作細節：下載並以系統管理員權限安裝，完成後重新登入。
     - 所需資源：Ardfry CR2 Codec x64 安裝包（付費）
     - 預估時間：10 分鐘
  3. 清除縮圖快取並重啟 Explorer
     - 實作細節：刪除 thumbcache_*.db，避免舊快取干擾。
     - 所需資源：命令列
     - 預估時間：5 分鐘
  4. 註冊檢查與驗證
     - 實作細節：檢查 WIC Decoders 登錄機碼是否存在，並用測試資料夾驗證縮圖。
     - 所需資源：reg query、測試 CR2 檔
     - 預估時間：10 分鐘

- 關鍵程式碼/設定：
```cmd
:: 清除縮圖快取（Vista/Win7 路徑相近）
taskkill /f /im explorer.exe
del /f /q "%LocalAppData%\Microsoft\Windows\Explorer\thumbcache_*.db"
start explorer.exe

:: 檢查 64 位元 WIC 解碼器註冊
reg query "HKLM\SOFTWARE\Microsoft\Windows Imaging Component\Decoders" /s
```

- 實際案例：原文提到第三方 CR2 codec（Ardfry）可用於 Vista/XP x64。
- 實作環境：Windows Vista x64；Explorer（64 位元）；第三方 CR2 x64 編解碼器。
- 實測數據：
  - 改善前：原文未提供（建議量測：縮圖顯示成功率、首批生成時間）。
  - 改善後：原文未提供（建議量測：同上）。
  - 改善幅度：原文未提供（以秒/檔案或每資料夾平均秒數量測）。

Learning Points（學習要點）
- 核心知識點：
  - WIC 與 64/32 位元編解碼器相容性
  - Explorer 縮圖快取對顯示結果的影響
  - 第三方影像編解碼器選型要點
- 技能要求：
  - 必備技能：基本系統管理、安裝與權限設定
  - 進階技能：登錄機碼檢查與 WIC 元件診斷
- 延伸思考：
  - 此法可用於其他 RAW 格式（NEF/ARW）？
  - 第三方元件的安全/授權風險？
  - 如何標準化到多機部署？

Practice Exercise（練習題）
- 基礎練習：安裝 x64 CR2 Codec，清除快取並驗證縮圖（30 分）
- 進階練習：撰寫步驟文件供團隊複用，含截圖與風險說明（2 小時）
- 專案練習：在 5 台 x64 機器上標準化部署與回報結果（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：縮圖/預覽是否穩定顯示
- 程式碼品質（30%）：清理與驗證腳本正確性、可重複
- 效能優化（20%）：縮圖首批生成時間是否可接受
- 創新性（10%）：是否提出通用化部署/回滾策略


## Case #2: Vista x64 透過 WOW64 強制使用 32 位元鏈路預覽 CR2（原文直述）

### Problem Statement（問題陳述）
- 業務場景：在沒有預算購買第三方 codec 前，需於 Vista x64 暫時預覽 CR2 檔案以挑片，嘗試以 WOW64 讓 32 位元流程可用。
- 技術挑戰：預設 Explorer 為 64 位元，無法載入 32 位元 CR2 codec；需強制使用 32 位元殼層/檢視器。
- 影響範圍：Explorer 縮圖、Windows Photo Gallery。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 64 位元進程不能載入 32 位元 DLL（編解碼器）。
  2. Canon 官方僅有 32 位元 codec。
  3. Explorer 單實例機制，預設以 64 位元執行。
- 深層原因：
  - 架構層面：WOW64 僅提供 32 位元應用執行層，不跨位元載入。
  - 技術層面：需要啟動 32 位元 Explorer/WPG 並關閉 64 位元實例。
  - 流程層面：暫時性 Hack 缺少 SOP，易回退失效。

### Solution Design（解決方案設計）
- 解決策略：安裝 32 位元 Canon RAW codec；以 WOW64 啟動 32 位元 Explorer 或 Windows Photo Gallery，確保整條鏈路為 32 位元，成功載入 32 位元編解碼器。

- 實施步驟：
  1. 安裝 32 位元 Canon RAW codec
     - 實作細節：於 Vista x64 可安裝 32 位元版本，註冊於 WOW6432Node。
     - 所需資源：官方 32 位元 codec 安裝包
     - 預估時間：10 分鐘
  2. 啟動 32 位元 Explorer
     - 實作細節：先關閉 64 位元 explorer.exe，再自 SysWOW64 啟動。
     - 所需資源：命令列
     - 預估時間：5 分鐘
  3. 或啟動 32 位元 Windows Photo Gallery
     - 實作細節：自 Program Files (x86) 路徑啟動。
     - 所需資源：捷徑設定
     - 預估時間：5 分鐘
  4. 驗證與風險提示
     - 實作細節：以工作管理員確認 *32 徽記；記錄成功率。
     - 所需資源：工作管理員
     - 預估時間：5 分鐘

- 關鍵程式碼/設定：
```cmd
:: 關閉 64 位元 Explorer 並以 32 位元重啟
taskkill /f /im explorer.exe
"%SystemRoot%\SysWOW64\explorer.exe"

:: 啟動 32 位元 Windows Photo Gallery（視實際安裝）
"%ProgramFiles(x86)%\Windows Photo Gallery\WindowsPhotoGallery.exe"
```

- 實際案例：原文提及「在 Vista x64 下，用 WOW 來跑」的權宜之計。
- 實作環境：Windows Vista x64；32 位元 Canon RAW codec。
- 實測數據：
  - 改善前/後/幅度：原文未提供（建議量測：預覽成功率、切換流程耗時）。

Learning Points（學習要點）
- 核心知識點：
  - WOW64 機制與位元不相容性
  - Explorer 單實例與位元控制
  - 權宜 Hack 的風險與回退
- 技能要求：
  - 必備技能：進程管理、檔案總管重啟
  - 進階技能：32/64 位元元件佈局與登錄機碼辨識
- 延伸思考：
  - 如何自動化啟停與驗證？
  - 長期維護風險與替代方案？
  - 何時應購買正式 x64 codec？

Practice Exercise（練習題）
- 基礎練習：以 WOW64 啟動 32 位元 Explorer 並驗證 CR2 縮圖（30 分）
- 進階練習：寫一鍵批次檔完成啟停與驗證流程（2 小時）
- 專案練習：撰寫 SOP 與風險告知，並回收使用者回饋（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：32 位元流程可穩定啟動並顯示縮圖
- 程式碼品質（30%）：批次/腳本健壯性與可維護性
- 效能優化（20%）：切換流程耗時最小化
- 創新性（10%）：自動化與安全性考量


## Case #3: XP x64 無法預覽 CR2，部署支援 XP x64 的第三方編解碼器（延伸）

### Problem Statement
- 業務場景：老舊的 XP x64 工作站仍需瀏覽 CR2，缺少官方 x64 codec，造成挑片流程阻塞。
- 技術挑戰：XP x64 的 WIC/殼層能力較弱，需相容的第三方 codec。
- 影響範圍：Explorer 縮圖、部分老舊應用相容性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 官方無 x64 codec；XP x64 環境過舊。
  2. WIC 元件可能未安裝或版本過低。
  3. 編解碼器註冊未完成或權限不足。
- 深層原因：
  - 架構層面：XP x64 殼層對 WIC 整合有限。
  - 技術層面：第三方需提供 XP x64 兼容版本。
  - 流程層面：未建立舊平台相容性清單。

### Solution Design
- 解決策略：選型支援 XP x64 的第三方 CR2 codec，確保安裝先決條件（含 WIC），完成註冊與驗證。

- 實施步驟：
  1. 盤點系統先決條件
     - 細節：確認 WIC 存在與版本；安裝必要更新。
     - 資源：系統更新、WIC 套件
     - 時間：20 分鐘
  2. 安裝第三方 x64 codec
     - 細節：以管理員權限安裝。
     - 資源：安裝包
     - 時間：10 分鐘
  3. 驗證與快取清理
     - 細節：清理縮圖快取並測試。
     - 資源：命令列
     - 時間：5 分鐘

- 關鍵程式碼/設定：
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows Imaging Component\Decoders" /s
```

- 實際案例：主題延伸自原文之「XP x64」場景。
- 實作環境：Windows XP x64；第三方 x64 codec。
- 實測數據：原文未提供（建議量測方法同 Case #1）。

Learning Points
- 核心：舊平台相容性與先決條件管理
- 技能：系統更新、WIC 診斷
- 延伸：技術債管理與淘汰計畫

Practice Exercise
- 基礎：驗證 WIC 與解碼器註冊（30 分）
- 進階：寫安裝前檢查腳本（2 小時）
- 專案：完成 XP x64 相容性報告（8 小時）

Assessment
- 功能完整性、腳本品質、風險控管、創新性（配比同上）


## Case #4: 64/32 位元錯配導致預覽失敗的定位與修復（延伸）

### Problem Statement
- 業務場景：安裝了 codec 仍看不到縮圖，疑似因位元錯配導致載入失敗。
- 技術挑戰：判斷 Explorer/WPG 位元與 codec 位元是否一致。
- 影響範圍：Explorer、第三方 WIC 應用。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 64 位元 Explorer 對應 32 位元 codec。
  2. 僅安裝了單一位元版本。
  3. 註冊機碼寫入到錯誤樹（WOW6432Node）。
- 深層原因：
  - 架構：位元隔離
  - 技術：註冊位置與 CLSID 不一致
  - 流程：缺乏安裝後驗證

### Solution Design
- 策略：確認進程位元、同時安裝對應位元 codec、修正登錄註冊並重建快取。

- 實施步驟：
  1. 確認進程位元（Task Manager 是否顯示 *32）
  2. 安裝對應位元 codec（x64 與 x86）
  3. 檢查兩個註冊表路徑（含 WOW6432Node）
  4. 重啟與快取清理

- 關鍵程式碼/設定：
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows Imaging Component\Decoders" /s
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows Imaging Component\Decoders" /s
```

- 實作環境：Vista/XP x64。
- 實測數據：原文未提供（建議量測：修復前後縮圖成功率）。

Learning Points：位元檢查、雙版本佈署
Practice：撰寫位元自檢腳本（30 分）；建立安裝 SOP（2 小時）
Assessment：是否能快速定位錯配並修復


## Case #5: 安裝後縮圖未更新，清除縮圖快取與重建（延伸）

### Problem Statement
- 業務場景：安裝 codec 後仍顯示舊圖示或空白縮圖。
- 技術挑戰：縮圖快取未重建。
- 影響範圍：Explorer 全站縮圖顯示。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：thumbcache 資料庫未清除。
- 深層原因：
  - 架構：Explorer 使用快取 DB
  - 技術：安裝不會自動刷新
  - 流程：缺少安裝後清理步驟

### Solution Design
- 策略：停止 Explorer、清除縮圖快取 DB、重啟並重新生成。

- 實施步驟：
  1. 停止 Explorer
  2. 刪除 thumbcache_*.db
  3. 重啟 Explorer
  4. 開啟包含 CR2 的資料夾等待重建

- 關鍵程式碼/設定：
```cmd
taskkill /f /im explorer.exe
del /f /q "%LocalAppData%\Microsoft\Windows\Explorer\thumbcache_*.db"
start explorer.exe
```

- 實測數據：原文未提供（建議量測：重建耗時/資料夾）。

Learning Points：快取機制
Practice：寫一鍵清理批次檔
Assessment：縮圖是否恢復與穩定


## Case #6: .CR2 副檔名關聯錯誤，導致開啟流程錯亂（延伸）

### Problem Statement
- 業務場景：雙擊 CR2 開啟到錯誤程式，拖慢作業。
- 技術挑戰：副檔名關聯與預設 App 未正確設定。
- 影響範圍：挑片流程與檔案開啟協定。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：assoc/ftype 設定不正確。
- 深層原因：
  - 架構：每副檔名對應一類型
  - 技術：安裝過多工具造成覆蓋
  - 流程：未管控預設程式

### Solution Design
- 策略：重設 .CR2 關聯到期望的檢視器或 Photo Gallery。

- 實施步驟：
  1. 檢查現有關聯
  2. 重設 ftype/assoc
  3. 測試雙擊行為

- 關鍵程式碼/設定：
```cmd
assoc .cr2
ftype | findstr /i cr2

:: 範例：將 CR2 關聯到自訂檢視器（請換成實際路徑）
assoc .cr2=cr2file
ftype cr2file="C:\Program Files\Viewer\View.exe" "%%1"
```

Learning Points：檔案關聯
Practice：切換不同檢視器比一比
Assessment：雙擊開啟是否正確/快速


## Case #7: 多個 CR2 編解碼器衝突，導致顯示不穩（延伸）

### Problem Statement
- 業務場景：安裝多套影像工具後，CR2 縮圖忽隱忽現。
- 技術挑戰：解碼器註冊重疊/衝突。
- 影響範圍：Explorer/第三方應用。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：多個解碼器註冊同副檔名/CLSID。
- 深層原因：
  - 架構：COM 登錄覆蓋
  - 技術：未控制載入順序
  - 流程：安裝/更新未標準化

### Solution Design
- 策略：盤點現有註冊，移除重複/舊版，保留單一路徑。

- 實施步驟：
  1. 列示 WIC Decoders（含 WOW6432Node）
  2. 卸載不必要的 codec
  3. 清理殘留登錄（謹慎）
  4. 重建快取並測試

- 關鍵程式碼/設定：
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows Imaging Component\Decoders" /s
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\Windows Imaging Component\Decoders" /s
```

Learning Points：COM 註冊衛生
Practice：做一份「已安裝解碼器盤點表」
Assessment：穩定性是否改善


## Case #8: 企業環境大量部署付費 x64 CR2 Codec（延伸）

### Problem Statement
- 業務場景：多台 x64 工作站需統一具備 CR2 預覽能力。
- 技術挑戰：靜默安裝、授權合規、版本控管。
- 影響範圍：IT 維運、人員生產力。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：手動安裝成本高且易不一致。
- 深層原因：
  - 架構：無集中部署機制
  - 技術：缺少 MSI 參數與回報
  - 流程：授權與資產缺管

### Solution Design
- 策略：以 GPO/SCCM 進行 MSI 靜默部署，建立授權與驗證流程。

- 實施步驟：
  1. 取得 MSI 與授權檔
  2. 測試 msiexec 靜默參數
  3. 建立 GPO/套件並分派
  4. 蒐集回報與抽測

- 關鍵程式碼/設定：
```cmd
msiexec /i "CR2Codec-x64.msi" /qn /norestart
```

Learning Points：企業佈署
Practice：在測試 OU 套用 GPO 部署
Assessment：安裝成功率、版本一致性


## Case #9: 第三方 codec 安全與信任驗證（延伸）

### Problem Statement
- 業務場景：需導入非官方付費 codec，關注安全風險。
- 技術挑戰：檔案簽章驗證、來源信任、執行白名單。
- 影響範圍：端點安全、法遵。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：外部 DLL 載入風險。
- 深層原因：
  - 架構：Shell 會載入第三方 DLL
  - 技術：缺少簽章/散列驗證
  - 流程：缺乏審核流程

### Solution Design
- 策略：導入 Authenticode 驗證、AppLocker 白名單與檔案雜湊稽核。

- 實施步驟：
  1. 檢查 DLL 簽章
  2. 設定 AppLocker/WDAC 政策
  3. 建立供應商安全審核清單

- 關鍵程式碼/設定：
```powershell
Get-AuthenticodeSignature "C:\Program Files\Vendor\CR2Codec64.dll" | Format-List
```

Learning Points：簽章與白名單
Practice：建立一份允許清單策略
Assessment：阻擋未簽章 DLL 成功率


## Case #10: 縮圖生成效能不佳的最佳化（延伸）

### Problem Statement
- 業務場景：大量 CR2 的資料夾開啟很慢。
- 技術挑戰：首次縮圖生成耗時高、I/O 密集。
- 影響範圍：使用者體驗、挑片效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：首次生成全部縮圖。
- 深層原因：
  - 架構：Explorer 應需解碼
  - 技術：快取大小限制
  - 流程：未預先生成縮圖

### Solution Design
- 策略：調整檢視模式、分批開啟、預先生成縮圖並保留快取。

- 實施步驟：
  1. Explorer 改用「中/大圖示」避免一次載入超多
  2. 分批資料夾歸檔，降低首批壓力
  3. 以工具預先生成縮圖（可寫小工具，見 Case #16）

- 關鍵程式碼/設定：N/A（操作為主）

Learning Points：I/O 與快取策略
Practice：設計預渲染流程
Assessment：首批開啟時間對比


## Case #11: 修復損毀的 WIC 解碼器註冊（延伸）

### Problem Statement
- 業務場景：明明安裝 codec，仍報錯或無法載入。
- 技術挑戰：WIC 解碼器註冊損毀或缺失。
- 影響範圍：所有依賴 WIC 的應用。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：登錄鍵缺失/指向無效檔案。
- 深層原因：
  - 架構：COM 註冊依賴正確 CLSID/Path
  - 技術：安裝失敗/權限不足
  - 流程：未做安裝後驗證

### Solution Design
- 策略：重新安裝 codec，必要時手動修復註冊並重啟。

- 實施步驟：
  1. 反安裝再重裝
  2. 以 reg query 檢查 CLSID 與路徑
  3. 重啟系統與清快取

- 關鍵程式碼/設定：
```cmd
reg query "HKCR\CLSID\{WIC-Decoder-CLSID}" /s
```

Learning Points：COM/WIC 登錄診斷
Practice：撰寫註冊健檢清單
Assessment：修復後穩定性


## Case #12: RAW 檢視顏色不正確，導入 ICC 與色彩管理（延伸）

### Problem Statement
- 業務場景：預覽顏色失真，影響初步判斷。
- 技術挑戰：ICC Profile/顯示器色校正未配置。
- 影響範圍：所有影像預覽。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：未正確載入 ICC/螢幕校色檔。
- 深層原因：
  - 架構：WIC/檢視器色彩管理差異
  - 技術：裝置設定缺漏
  - 流程：未納入色管 SOP

### Solution Design
- 策略：安裝正確 ICC，使用 colorcpl 設定預設色域，驗證不同檢視器。

- 實施步驟：
  1. 安裝相機/顯示器 ICC
  2. colorcpl 設定預設
  3. 比較多檢視器呈現

- 關鍵程式碼/設定：
```cmd
colorcpl.exe
```

Learning Points：色彩管理
Practice：建立色管校正步驟
Assessment：顏色一致性


## Case #13: 由第三方轉向官方 x64 Codec 的切換與回滾（延伸）

### Problem Statement
- 業務場景：官方 x64 codec 發佈後，需平順替換第三方。
- 技術挑戰：相容性驗證、回滾策略、停機風險。
- 影響範圍：全站預覽功能。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：兩套編解碼器共存風險。
- 深層原因：
  - 架構：註冊衝突
  - 技術：CLSID/副檔名處理差異
  - 流程：變更管理不足

### Solution Design
- 策略：隔離測試→試點→全面替換→觀察→回滾預案。

- 實施步驟：
  1. 建測試機驗證相容性
  2. 小範圍試點佈署
  3. 卸載第三方/安裝官方
  4. 問題回滾預案

- 關鍵程式碼/設定：N/A（流程主導）

Learning Points：變更管理
Practice：撰寫切換 Runbook
Assessment：切換過程零中斷


## Case #14: 不改殼層，改用應用層檢視器挑片（延伸）

### Problem Statement
- 業務場景：殼層預覽不穩或無法導入第三方 codec。
- 技術挑戰：改以應用（如相機廠自帶檢視器/相片管理器）挑片。
- 影響範圍：使用者流程改變。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：殼層無法穩定載入 codec。
- 深層原因：
  - 架構：殼層依賴 WIC
  - 技術：應用內建解碼
  - 流程：工具選型未靈活切換

### Solution Design
- 策略：導入專用檢視器作為挑片工具，不依賴殼層縮圖。

- 實施步驟：安裝→設定為預設檢視器→建立挑片工作流→再回存目錄結構。

- 關鍵程式碼/設定：N/A

Learning Points：工具替代策略
Practice：設計與試跑挑片工作流
Assessment：挑片效率是否改善


## Case #15: 虛擬化備援：在 32 位元 VM 中挑片（延伸）

### Problem Statement
- 業務場景：主機 x64 無法導入 codec，但急需挑片。
- 技術挑戰：在 VM 中使用 32 位元系統與官方 32 位元 codec。
- 影響範圍：操作體驗、I/O。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：主機無法載入 codec。
- 深層原因：
  - 架構：位元不相容
  - 技術：VM 共享資料夾/效能
  - 流程：臨時性備援方案

### Solution Design
- 策略：建立 XP/Vista 32 位元 VM，安裝官方 32 位元 codec 與檢視器，透過共享資料夾挑片。

- 實施步驟：安裝 VM→建置 32 位元 OS→安裝 codec→掛載共享→挑片→同步標記。

- 關鍵程式碼/設定：N/A（VM 管理操作）

Learning Points：備援思維
Practice：快速建 VM 範本
Assessment：任務完成時效


## Case #16: 建立 WPF/WIC 小工具驗證 CR2 解碼可行（延伸）

### Problem Statement
- 業務場景：需要客觀驗證系統是否能解 CR2（非只靠 Explorer）。
- 技術挑戰：呼叫 WIC 解碼並輸出測試圖。
- 影響範圍：診斷流程、迴歸測試。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：缺少可重複驗證工具。
- 深層原因：
  - 架構：WIC 在 .NET/WPF 可直接使用
  - 技術：需簡短程式驗證
  - 流程：自動化測試缺位

### Solution Design
- 策略：用 C# WPF BitmapDecoder 建立即讀即寫工具，若失敗即回報例外。

- 實施步驟：
  1. 建立 .NET 專案（WPF/控制台皆可）
  2. 讀取 CR2 並輸出 PNG
  3. 捕捉錯誤並報告

- 關鍵程式碼/設定：
```csharp
// 需要參考 PresentationCore.dll
using System;
using System.IO;
using System.Windows.Media.Imaging;

class TestWicCr2 {
  static int Main(string[] args) {
    if (args.Length < 2) {
      Console.WriteLine("Usage: TestWicCr2 <input.cr2> <output.png>");
      return 2;
    }
    try {
      var decoder = BitmapDecoder.Create(new Uri(Path.GetFullPath(args[0])),
        BitmapCreateOptions.None, BitmapCacheOption.OnLoad);
      var frame = decoder.Frames[0];
      var encoder = new PngBitmapEncoder();
      encoder.Frames.Add(BitmapFrame.Create(frame));
      using (var fs = File.Open(args[1], FileMode.Create)) encoder.Save(fs);
      Console.WriteLine("OK");
      return 0;
    } catch (Exception ex) {
      Console.Error.WriteLine("Decode failed: " + ex.Message);
      return 1;
    }
  }
}
```

Learning Points：WIC 基本呼叫
Practice：打包成便攜式測試工具
Assessment：成功/失敗準確偵測


## Case #17: 自動化健康檢查腳本：位元/註冊/快取一鍵檢測（延伸）

### Problem Statement
- 業務場景：多機環境需快速判斷 CR2 預覽不可用的原因。
- 技術挑戰：自動化檢測位元、註冊與快取狀態。
- 影響範圍：IT 支援效率。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：人工檢查耗時易漏。
- 深層原因：
  - 架構：多點位風險
  - 技術：需要整合檢查邏輯
  - 流程：缺少巡檢工具

### Solution Design
- 策略：撰寫 PowerShell 腳本檢查 Explorer 位元、WIC 登錄、縮圖快取大小與最後更新時間，輸出建議行動。

- 實施步驟：撰寫→測試→部署→週期性執行。

- 關鍵程式碼/設定：
```powershell
# 簡化示例：檢查 WIC Decoders 與縮圖快取大小
$paths = @(
 'HKLM:\SOFTWARE\Microsoft\Windows Imaging Component\Decoders',
 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows Imaging Component\Decoders'
)
foreach ($p in $paths) {
  try { Get-ChildItem $p -ErrorAction Stop | Out-Null; Write-Host "[OK] $p" }
  catch { Write-Warning "[MISSING] $p" }
}
$thumbDir = "$env:LOCALAPPDATA\Microsoft\Windows\Explorer"
$size = (Get-ChildItem $thumbDir -Filter "thumbcache_*.db" -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
Write-Host "Thumbcache total bytes:" $size
```

Learning Points：診斷自動化
Practice：擴充腳本加入建議修復
Assessment：問題定位準確率/時間


==============================
案例分類
==============================

1. 按難度分類
- 入門級：Case 5, 6, 10, 14
- 中級：Case 1, 2, 3, 4, 7, 11, 12, 13, 15, 16, 17
- 高級：Case 8, 9

2. 按技術領域分類
- 架構設計類：Case 13
- 效能優化類：Case 10
- 整合開發類：Case 1, 3, 4, 8, 15
- 除錯診斷類：Case 2, 5, 6, 7, 11, 16, 17
- 安全防護類：Case 9

3. 按學習目標分類
- 概念理解型：Case 1, 2, 4, 12, 13
- 技能練習型：Case 5, 6, 10, 11, 16, 17
- 問題解決型：Case 3, 7, 8, 15
- 創新應用型：Case 9, 14

==============================
案例關聯圖（學習路徑建議）
==============================

- 先學哪些案例？
  - 入門基礎：Case 5（快取）、Case 6（關聯）
  - 核心概念：Case 1（x64 codec 正途）、Case 2（WOW64 權宜）
- 依賴關係：
  - Case 4 依賴理解 Case 1/2 的位元相容性
  - Case 7 依賴 Case 4 的註冊/位元概念
  - Case 10 效能優化建立在 Case 1/5 的穩定顯示後
  - Case 11、Case 17 建立於 Case 4/5 的診斷基礎
  - Case 8（大量部署）需先完成 Case 1 的單機驗證
  - Case 9（安全）伴隨 Case 1/8 的導入過程
  - Case 16（小工具驗證）可在 Case 1 後作為回歸測試基礎
  - Case 13（切換官方）需熟悉 Case 7/8（衝突/佈署）
  - Case 15（VM 備援）可隨時替代 Case 2

- 完整學習路徑建議：
  1) Case 5 → 6 → 1 → 2（基礎健檢 + 主要兩路方案）
  2) Case 4 → 7 → 11 → 17（位元/註冊/診斷體系）
  3) Case 10（效能）→ 16（驗證工具）→ 8（佈署）→ 9（安全）
  4) Case 12（色管）→ 14（工具替代）→ 15（VM 備援）
  5) 最後學 Case 13（官方切換），完成全生命週期治理

說明與後續
- 原文僅提供方案線索，未附實測數據。若您需要，我可依您的環境（機種、OS 版本、磁碟類型、影像數量）提供量測腳本與報表模板，並將上述案例擴充為含量化指標的完整教材集。