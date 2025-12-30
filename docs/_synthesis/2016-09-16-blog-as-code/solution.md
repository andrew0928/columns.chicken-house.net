---
layout: synthesis
title: "Blogging as code !!"
synthesis_type: solution
source_post: /2016/09/16/blog-as-code/
redirect_from:
  - /2016/09/16/blog-as-code/solution/
---

以下內容基於原文逐一抽取並結構化整理，共 17 個完整的實戰型解決方案案例。每一案均包含問題、根因、方案、實施步驟、程式碼與可量化（或功能性）成效。

## Case #1: 「Blogging as Code」從動態系統轉為 GitHub Pages 靜態架構

### Problem Statement（問題陳述）
業務場景：多年使用各種部落格系統（.Text、Community Server、BlogEngine、WordPress），維運成本高、升級繁瑣、資料遷移痛苦。對開發者而言，原生版本控制弱、編輯器體驗不佳，且許多功能過度或冗餘。希望用更單純的方式維護內容、節省運算資源，同時實現版本化管理。
技術挑戰：取消後端 runtime 與資料庫的同時，仍需保有文章清單、分類、標籤、分頁、回應、按讚與統計等功能。
影響範圍：涵蓋整個網站架構、文章生命週期管理、外部插件整合與發佈流程。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 動態系統需持續維運與升級，投入心力高。
2. 內建版本控制與 Markdown 支援弱，無法匹配開發者工作流。
3. 功能過量與依賴資料庫，增加 SLA 與風險。
深層原因：
- 架構層面：架構依賴 runtime + DB，與實際需求（純內容展示）不匹配。
- 技術層面：編輯器與版本控管非開發者導向。
- 流程層面：發佈仰賴後台，難以融入 CI/CD 或 PR 流程。

### Solution Design（解決方案設計）
解決策略：改採 GitHub Pages + Jekyll + Markdown + Git，將所有內容與設定以程式碼管理。文章、標籤、分類全部以靜態生成，互動功能嵌入第三方服務。開源儲存庫，發佈以 push 代替後台操作。

實施步驟：
1. 建立 GitHub Repo 與 Pages
- 實作細節：開啟 GitHub Pages，設定 branch（main 或 gh-pages）。
- 所需資源：GitHub 帳號、Git。
- 預估時間：0.5 小時
2. 初始化 Jekyll 專案
- 實作細節：建立 _config.yml、_posts/ 結構，挑選主題。
- 所需資源：Jekyll（Pages 上由 GitHub 處理）、本機工具（可選）。
- 預估時間：1 小時
3. 定義內容規範與前置資料
- 實作細節：統一 front matter 欄位（title、tags、categories、permalink）。
- 所需資源：Markdown、Liquid。
- 預估時間：1 小時
4. 整合外部互動服務
- 實作細節：加入 GA、Open Graph、按讚/分享、留言。
- 所需資源：GA/FB/Disqus snippet。
- 預估時間：1 小時

關鍵程式碼/設定：
```yaml
# _config.yml — Minimal
title: "My Blog as Code"
theme: minima
plugins:
  - jekyll-redirect-from
markdown: kramdown
permalink: /:year/:month/:day/:title/
```

實際案例：使用 GitHub Pages 全自動建置。撰寫文章推上指定 branch，Jekyll 自動生成網站。
實作環境：GitHub Pages（Jekyll）、VS Code、Markdown/Liquid。
實測數據：
改善前：需維運 DB/後台、升級/備份複雜。
改善後：無 runtime process、無 DB、push 即發佈。
改善幅度：後台維運與 DB 維護降至 0；發佈流程收斂為 Git 操作。

Learning Points（學習要點）
核心知識點：
- 靜態網站適用場景判斷
- GitHub Pages 與 Jekyll 基本運作
- Markdown/Liquid 內容驅動模式
技能要求：
- 必備技能：Git 基本操作、Markdown
- 進階技能：Jekyll/Liquid 模板客製
延伸思考：
- 可否以 Actions 增強建置流程？
- 大量內容的建置時間如何優化？
- 多作者協作與審核流程如何設計？

Practice Exercise（練習題）
- 基礎練習：建立一個新 repo，啟用 GitHub Pages，發一篇文章。
- 進階練習：自訂 permalink 與主題佈景，加入 tags/categories。
- 專案練習：為現有內容建立完整資訊架構（含 index、tags、categories、archive）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：Pages 正常建置、文章可見、連結正確。
- 程式碼品質（30%）：清晰的配置與前置資料規範。
- 效能優化（20%）：合理的建置時間與資源配置。
- 創新性（10%）：模板、流程自動化或擴充性設計。


## Case #2: Windows 本機預覽工作流（Jekyll + VS Code + IIS Express）

### Problem Statement（問題陳述）
業務場景：主要工作環境在 Windows，希望能在本機邊寫作邊預覽，並能看到草稿。部分檔名含中文需正常服務，且需快速分流預覽不同服務模式。
技術挑戰：Jekyll for Windows 搭配內建 web server 對中文檔名支援不佳；需要同時保有 watch build 與中文資源可存取。
影響範圍：開發效率、預覽準確性、錯誤早期發現。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Jekyll 內建 web server（Windows）對中文檔名支援問題。
2. 需要同時有 watch 編譯與可靠的靜態檔案服務。
3. 草稿預覽需要不同於正式站的行為。
深層原因：
- 架構層面：單一服務承擔多職能導致限制。
- 技術層面：Windows 上編碼/行為差異。
- 流程層面：缺少準確分境（draft vs prod）與對應服務。

### Solution Design（解決方案設計）
解決策略：雙服務分工。Jekyll 負責 build + watch 與 4000 連線；IIS Express 直接服務 _site 目錄於 4001。VS Code 管理 repository 與 Markdown 寫作，並可同步預覽。

實施步驟：
1. 啟動 VS Code
- 實作細節：code d:\blog 開啟專案資料夾。
- 所需資源：VS Code。
- 預估時間：1 分鐘
2. 啟動 Jekyll（含草稿）
- 實作細節：jekyll s --draft -w 於 4000 埠。
- 所需資源：Jekyll for Windows。
- 預估時間：1 分鐘
3. 啟動 IIS Express 服務 _site
- 實作細節：iisexpress /port:4001 /path:d:\blog\_site。
- 所需資源：IIS Express。
- 預估時間：1 分鐘

關鍵程式碼/設定：
```bat
:: 1) 啟動 VS Code
code d:\blog

:: 2) 啟動 Jekyll（含草稿、監看變更）
jekyll s --draft -w

:: 3) IIS Express 服務 _site
"c:\Program Files\IIS Express\iisexpress.exe" /port:4001 /path:d:\blog\_site
```

實作環境：Windows、Jekyll for Windows、VS Code、IIS Express。
實測數據：
改善前：Docker 監看模式下 rebuild 可能近 20 分鐘。
改善後：Windows 上初次 build 約 40 秒；rebuild 約 30 秒。
改善幅度：rebuild 時間從 ~20 分鐘降至 ~30 秒（約 97.5%）。

Learning Points（學習要點）
核心知識點：
- 本機雙服務分層預覽策略
- Jekyll drafts 模式
- Windows 編碼與檔名相容性
技能要求：
- 必備技能：命令列操作、Jekyll 基礎
- 進階技能：多服務並行、IIS Express 使用
延伸思考：
- 可否用 nginx 或其他輕量 server 取代 IIS Express？
- 如何以批次腳本一鍵啟/停三個流程？

Practice Exercise（練習題）
- 基礎：啟動三步驟並成功預覽草稿。
- 進階：將三步驟寫成一鍵批次檔或 PowerShell。
- 專案：加上自動加壓縮/資產編譯流程並於 _site 測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：兩個預覽通道可用、草稿可見。
- 程式碼品質（30%）：腳本清楚、參數可配置。
- 效能優化（20%）：重建時間穩定在 30–40 秒級。
- 創新性（10%）：增加自動化與快捷操作。


## Case #3: Docker for Windows 下 Jekyll 檔案變更無法監測（改用 --force_polling）

### Problem Statement（問題陳述）
業務場景：希望在 Windows 以 Docker 快速跑起 Jekyll 以免安裝 Ruby/Gems。但發現 watch 模式對檔案變更不反應，開發體驗差。
技術挑戰：volume 掛載後，檔案系統變更通知不足，導致 Jekyll 無法即時重建。
影響範圍：開發效率、回饋延遲、CPU/IO 負載。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Docker volume 轉譯層未轉遞 Windows 檔案變更通知。
2. Jekyll 預設依賴監測事件來觸發 rebuild。
3. 大量檔案時 polling 負擔高。
深層原因：
- 架構層面：虛擬化與宿主檔案系統事件的語義差異。
- 技術層面：Jekyll/Watchman 在 Docker for Windows 的限制。
- 流程層面：持續 watch 導致資源消耗與延遲升高。

### Solution Design（解決方案設計）
解決策略：在 docker run 中加入 --force_polling，改以輪詢監控變更，確保變更被偵測。同時接受稍高的延遲與資源開銷。

實施步驟：
1. 以官方 image 啟動 Jekyll
- 實作細節：掛載本機 D:\Blog 至 /srv/jekyll，開 4000 埠，啟用 --watch --force_polling。
- 所需資源：Docker for Windows。
- 預估時間：10 分鐘
2. 驗證變更偵測
- 實作細節：編輯一篇文章並觀測 rebuild 時間。
- 所需資源：VS Code、瀏覽器。
- 預估時間：5 分鐘

關鍵程式碼/設定：
```bash
docker run -ti --rm -p 4000:4000 \
  -v D:\Blog:/srv/jekyll \
  jekyll/jekyll:pages \
  jekyll s --watch --force_polling
```

實作環境：Windows 10、Docker for Windows、jekyll/jekyll:pages。
實測數據：
改善前：變更不被偵測（卡死）。
改善後：偵測延遲約 15 秒，成功 rebuild。
改善幅度：從 0% 偵測成功率 → 穩定偵測（延遲 15 秒）；功能性改善 100%。

Learning Points（學習要點）
核心知識點：
- Docker volume 與檔案事件差異
- Jekyll watch 與 polling 模式
- 開發時延遲與資源消耗取捨
技能要求：
- 必備技能：Docker 基本操作
- 進階技能：容器資源觀察與調校
延伸思考：
- 是否可用容器內編輯（避開 volume）？
- 是否用同步工具（mutagen/samba）改善事件傳遞？

Practice Exercise（練習題）
- 基礎：依指令啟動容器並成功 rebuild。
- 進階：測量不同檔量下的偵測延遲差異。
- 專案：寫一個簡報比較 polling 與非 polling 的權衡。

Assessment Criteria（評估標準）
- 功能完整性（40%）：容器內 watch 可用。
- 程式碼品質（30%）：指令與參數清晰可移植。
- 效能優化（20%）：延遲控制在可接受範圍。
- 創新性（10%）：提出替代同步方案。


## Case #4: 避免 Docker 監看高負載：改為檔變更自動重啟容器（PowerShell）

### Problem Statement（問題陳述）
業務場景：在 Docker + --force_polling 下，CPU/IO 高，rebuild 非常慢（近 20 分鐘），影響寫作體驗。
技術挑戰：Polling 對大量檔案耗費巨大，需改為事件驅動式重啟建置。
影響範圍：建置時間、電腦資源、迭代速度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. polling 需輪詢大量檔案導致高負載。
2. 容器內 watch 受限於 volume 橋接機制。
3. 動輒數百篇文章，掃描成本高。
深層原因：
- 架構層面：持續 watch 與容器資源配置不匹配。
- 技術層面：事件傳遞缺陷導致 fallback 到昂貴 polling。
- 流程層面：缺少自動化重啟機制。

### Solution Design（解決方案設計）
解決策略：停用容器內 watch，改用 PowerShell FileSystemWatcher 偵測宿主檔變更，觸發 docker 容器重啟一次建置，避免長時間 polling。

實施步驟：
1. 建立 PowerShell 監看腳本
- 實作細節：監聽新增/修改/刪除事件，debounce 後重啟容器。
- 所需資源：PowerShell、Docker CLI。
- 預估時間：0.5 小時
2. 調整 docker run 參數
- 實作細節：移除 --watch/--force_polling，改為一次性 build serve。
- 所需資源：Docker。
- 預估時間：10 分鐘

關鍵程式碼/設定：
```powershell
# watch-and-restart.ps1
$path = "D:\Blog"
$cmd  = { docker stop jekyll 2>$null; docker rm jekyll 2>$null;
  docker run -d --name jekyll -p 4000:4000 -v D:\Blog:/srv/jekyll jekyll/jekyll:pages jekyll s }

$fsw = New-Object IO.FileSystemWatcher $path, "*.*"
$fsw.IncludeSubdirectories = $true
$fsw.EnableRaisingEvents = $true

$timer = New-Object Timers.Timer
$timer.Interval = 2000; $timer.AutoReset = $false
$timer.add_Elapsed({ & $cmd })

Register-ObjectEvent $fsw Changed -Action { $timer.Stop(); $timer.Start() } | Out-Null
Register-ObjectEvent $fsw Created -Action { $timer.Stop(); $timer.Start() } | Out-Null
Register-ObjectEvent $fsw Deleted -Action { $timer.Stop(); $timer.Start() } | Out-Null

& $cmd
Write-Host "Watching $path. Press Ctrl+C to exit."
while ($true) { Start-Sleep 1 }
```

實作環境：Windows、PowerShell、Docker for Windows。
實測數據：
改善前：polling 模式 rebuild 近 20 分鐘。
改善後：重啟建置約 70 秒（一次完整 build）。
改善幅度：~96% 減少重建等待時間；CPU/IO 高負載顯著下降。

Learning Points（學習要點）
核心知識點：
- 事件驅動 vs 輪詢式監看
- Debounce 防抖設計
- 容器化開發流程自動化
技能要求：
- 必備技能：PowerShell、Docker CLI
- 進階技能：檔案監看與併發/抖動控制
延伸思考：
- 可否用 docker compose 與 healthcheck 強化流程？
- 是否可加上錯誤通知（toast/email）？

Practice Exercise（練習題）
- 基礎：運行腳本，觸發一次重啟。
- 進階：加入檔案過濾與多目錄監看。
- 專案：封裝成跨平台腳本（PowerShell + Bash）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：變更能自動重啟。
- 程式碼品質（30%）：腳本結構與錯誤處理。
- 效能優化（20%）：等待時間明顯下降。
- 創新性（10%）：通知/日誌/指標蒐集。


## Case #5: 切換至 Jekyll for Windows 以加速開發迭代

### Problem Statement（問題陳述）
業務場景：Docker 方案雖簡化安裝，但在監看模式下重建過慢，無法滿足頻繁編輯。需要更快的本機開發迭代。
技術挑戰：兼顧相容性與效能，並保留 watch 與 drafts 預覽。
影響範圍：日常寫作效率、即時預覽體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Docker 受限於資源配置（2 CPU、2GB RAM）。
2. Volume 帶來 IO penalty。
3. Polling 監看機制效率低。
深層原因：
- 架構層面：容器化便利 vs 原生效能的取捨。
- 技術層面：Windows 原生 Jekyll 在 watch/IO 更快。
- 流程層面：開發流程需最小延遲。

### Solution Design（解決方案設計）
解決策略：在 Windows 原生安裝 Ruby 與 Jekyll，開啟 watch 與 drafts，搭配 IIS Express 服務 _site 以避免中文檔名問題。

實施步驟：
1. 安裝 Ruby 與必要 gems
- 實作細節：Ruby 2.2 + jekyll + bundler。
- 所需資源：RubyInstaller for Windows。
- 預估時間：30–60 分鐘
2. 啟動工作流（見 Case #2）
- 實作細節：jekyll s --draft -w + iisexpress。
- 所需資源：VS Code、IIS Express。
- 預估時間：3 分鐘

關鍵程式碼/設定：
```bat
gem install bundler jekyll
jekyll s --draft -w        :: 4000
"c:\Program Files\IIS Express\iisexpress.exe" /port:4001 /path:d:\blog\_site
```

實作環境：Windows、Ruby 2.2、Jekyll、IIS Express。
實測數據：
改善前：Docker rebuild 近 20 分鐘，build 約 70 秒。
改善後：Windows 初次 build ~40 秒，rebuild ~30 秒。
改善幅度：rebuild 時間下降約 97.5%；初次 build 加速約 43%。

Learning Points（學習要點）
核心知識點：
- 原生 vs 容器效能比較
- watch/drafts 的開發體驗設計
- 多通道預覽
技能要求：
- 必備技能：Windows 安裝軟體、命令列
- 進階技能：多服務並行測試
延伸思考：
- 是否可用 WSL2 達到更佳折衷？
- 如何將 Windows 原生流程自動化封裝？

Practice Exercise（練習題）
- 基礎：安裝並運行 jekyll s --draft -w。
- 進階：量測多篇改動時的 rebuild 時間。
- 專案：把流程寫成 VS Code 任務與快捷鍵。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可持續預覽與 watch。
- 程式碼品質（30%）：腳本與依賴管理。
- 效能優化（20%）：rebuild 穩定 30–40 秒。
- 創新性（10%）：自動化與工具整合。


## Case #6: Ruby 版本相容性問題（Windows 上使用 Ruby 2.2）

### Problem Statement（問題陳述）
業務場景：在 Windows 安裝 Jekyll，遇到部分 gems 與最新 Ruby（2.3）不相容，導致安裝/執行失敗。
技術挑戰：找出可用版本組合，避免長時間排錯。
影響範圍：本機建置、依賴安裝、後續更新。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 一些 gems 在 Windows 上不支援 Ruby 2.3。
2. gem/native extension 編譯失敗。
3. 組合爆炸導致排錯困難。
深層原因：
- 架構層面：依賴鏈長且版本敏感。
- 技術層面：Windows 原生擴展編譯門檻。
- 流程層面：缺少可重現的依賴版本鎖定。

### Solution Design（解決方案設計）
解決策略：使用 Ruby 2.2（經驗證可用），搭配 Bundler 鎖定 dependencies。於 Windows 安裝路徑配置與 PATH 正確。

實施步驟：
1. 安裝 Ruby 2.2 與 DevKit
- 實作細節：下載 RubyInstaller 2.2，安裝 DevKit。
- 所需資源：RubyInstaller。
- 預估時間：20–30 分鐘
2. 安裝 gems 與建置
- 實作細節：gem install jekyll bundler；bundle install。
- 所需資源：Bundler、Gem。
- 預估時間：10–20 分鐘

關鍵程式碼/設定：
```bat
ruby -v                           :: 確認 2.2.x
gem install bundler jekyll
bundle init && bundle add jekyll
bundle exec jekyll s --draft -w
```

實作環境：Windows、Ruby 2.2、Jekyll。
實測數據：
改善前：Ruby 2.3 安裝失敗、無法執行。
改善後：Ruby 2.2 + Jekyll 正常 build/rebuild。
改善幅度：從無法運作 → 穩定運作（功能性 100%）。

Learning Points（學習要點）
核心知識點：
- 依賴版本鎖定與可重現性
- Windows 上 Ruby/native 擴展注意事項
- Bundler 用法
技能要求：
- 必備技能：命令列、安裝工具
- 進階技能：Gemfile 與版本管理
延伸思考：
- 是否可用 Docker/WSL2 避免版本相容性？
- 用 Gemfile.lock 固定專案依賴。

Practice Exercise（練習題）
- 基礎：安裝 Ruby 2.2 並成功跑 jekyll s。
- 進階：加入一個常見 plugin 並解決依賴。
- 專案：用 Bundler 管理多 plugin 的版本鎖定。

Assessment Criteria（評估標準）
- 功能完整性（40%）：環境可執行。
- 程式碼品質（30%）：Gemfile 清楚、版本固定。
- 效能優化（20%）：無冗餘依賴、啟動快速。
- 創新性（10%）：提供跨環境可重現方案。


## Case #7: Jekyll 內建 Web Server 不支援中文檔名的繞道方案

### Problem Statement（問題陳述）
業務場景：文章含中文命名的圖片/資源，Jekyll 內建 web server 在 Windows 下無法正確存取，預覽掉圖。
技術挑戰：保留 Jekyll watch 優勢，同時讓中文資源可正常服務。
影響範圍：預覽正確性、內容合規、發佈前驗證。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 內建 web server 與 Windows 編碼/URL 處理差異。
2. 中文檔名 URL 編碼與檔案系統存取落差。
3. 同服務承擔建置與靜態服務導致限制。
深層原因：
- 架構層面：單服務不足以涵蓋所有需求。
- 技術層面：國際化/編碼差異。
- 流程層面：缺少分工與備援。

### Solution Design（解決方案設計）
解決策略：Jekyll 僅負責 build/watch；另以 IIS Express 直接服務 _site 目錄，中文資源由 IIS Express 提供。

實施步驟：
1. 正常啟動 Jekyll（watch）
- 實作細節：jekyll s --draft -w。
- 所需資源：Jekyll。
- 預估時間：1 分鐘
2. 以 IIS Express 服務 _site
- 實作細節：/port:4001 指向 _site。
- 所需資源：IIS Express。
- 預估時間：1 分鐘

關鍵程式碼/設定：
```bat
jekyll s --draft -w
"c:\Program Files\IIS Express\iisexpress.exe" /port:4001 /path:d:\blog\_site
```

實作環境：Windows、IIS Express、Jekyll。
實測數據：
改善前：中文資源在內建 server 預覽掉圖。
改善後：中文資源在 IIS Express 正常顯示。
改善幅度：預覽準確度從不可靠 → 穩定（功能性 100%）。

Learning Points（學習要點）
核心知識點：
- 多服務分工策略
- 中文檔名與 URL 編碼
- 預覽與建置分離
技能要求：
- 必備技能：命令列、IIS Express 使用
- 進階技能：URL/編碼知識
延伸思考：
- 統一英文檔名命名規範是否更佳？
- 是否在 CI 加入檔名檢查（lint）？

Practice Exercise（練習題）
- 基礎：在 _site 透過 IIS Express 成功服務中文檔名資源。
- 進階：撰寫一個檔名檢查腳本避免大小寫/編碼問題。
- 專案：把檔名規範與檢查納入 PR 流程。

Assessment Criteria（評估標準）
- 功能完整性（40%）：中文資源可見。
- 程式碼品質（30%）：腳本與設定明確。
- 效能優化（20%）：多服務不互相干擾。
- 創新性（10%）：加入規範與自動檢查。


## Case #8: 檔名大小寫差異導致 GitHub Pages 掉圖

### Problem Statement（問題陳述）
業務場景：本機（Windows）預覽正常，上線（GitHub Pages/Linux）卻掉圖。追查發現 Markdown 內連結 a.png，實檔 a.PNG。
技術挑戰：Windows 檔案系統大小寫不敏感，GitHub Pages 環境大小寫敏感；且 Windows 上 Git 對大小寫變更不一定偵測。
影響範圍：內容正確性、上線品質、快修成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 連結與檔名大小寫不一致。
2. Windows 對大小寫不敏感，開發期不易發現。
3. Git 在 Windows 對大小寫變動可能不追蹤。
深層原因：
- 架構層面：開發環境與上線環境語義差。
- 技術層面：檔名大小寫敏感性差異。
- 流程層面：缺少大小寫一致性檢查。

### Solution Design（解決方案設計）
解決策略：統一檔名大小寫，並以 Git 正確提交改名。加入檔案命名規範與檢查（lint），避免再次發生。

實施步驟：
1. 修正檔名與連結
- 實作細節：先改為暫存檔名再改回，讓 Git 追蹤變更；或設定 core.ignorecase。
- 所需資源：Git、VS Code。
- 預估時間：10–20 分鐘
2. 建立命名規範與檢查
- 實作細節：PR 檢查腳本，避免混用大小寫。
- 所需資源：Node/PowerShell 任一。
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# 讓 Git 確認大小寫變更
git config core.ignorecase false
git mv images/a.PNG images/a_temp.png
git mv images/a_temp.png images/a.png
git commit -m "Fix case sensitivity for a.png"
```

實作環境：Windows（開發）、GitHub Pages（上線）。
實測數據：
改善前：上線掉圖。
改善後：上線正常顯示。
改善幅度：可用性從失敗 → 正常（功能性 100%）。

Learning Points（學習要點）
核心知識點：
- 跨平台大小寫敏感差異
- Git 對改名/大小寫的行為
- 命名規範的重要性
技能要求：
- 必備技能：Git
- 進階技能：CI 中的檔名 lint
延伸思考：
- 加入 pre-commit hook 檢查？
- 以 slug 化流程處理檔名？

Practice Exercise（練習題）
- 基礎：以 git mv 正確修正大小寫。
- 進階：寫 pre-commit 檢查大小寫不一致。
- 專案：為專案建立完整檔名規範與驗證。

Assessment Criteria（評估標準）
- 功能完整性（40%）：問題消失、上線正常。
- 程式碼品質（30%）：提交記錄清晰。
- 效能優化（20%）：檢查腳本效率。
- 創新性（10%）：自動化與治理。


## Case #9: IIS Express 把 .aspx 路徑交給 ASP.NET 導致 404（改用 Jekyll 服務）

### Problem Statement（問題陳述）
業務場景：為相容舊網址，Jekyll 產生 foo.aspx/index.html，希望當作靜態目錄索引處理；但 IIS Express 遇到 .aspx 會交給 ASP.NET 處理，導致 404。
技術挑戰：同一路徑在不同 server 行為不同，需要在本機正確模擬。
影響範圍：相容性測試、舊連結驗證、上線品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. IIS Express 預設處理程序映射 .aspx → ASP.NET 管線。
2. 靜態相容策略與動態映射衝突。
3. 本機預覽與上線邏輯不一致。
深層原因：
- 架構層面：歷史資產相容與 server 特性差異。
- 技術層面：Handler 映射。
- 流程層面：缺少一致的預覽環境。

### Solution Design（解決方案設計）
解決策略：遇到 .aspx 相容測試時，切回 Jekyll 的內建 server 進行預覽；避免 IIS Express 的 ASP.NET 管線介入。

實施步驟：
1. 切換預覽通道
- 實作細節：.aspx 測試時改連線至 Jekyll server（4000）。
- 所需資源：瀏覽器/Jekyll。
- 預估時間：即時
2. 上線驗證
- 實作細節：以 GitHub Pages 驗證最終行為。
- 所需資源：GitHub Pages。
- 預估時間：5–10 分鐘

關鍵程式碼/設定：
```txt
策略：IIS Express（4001）供一般預覽；遇 .aspx 相容情境 → 改用 Jekyll（4000）
# 無需額外設定，採操作層面的切換
```

實作環境：Windows、Jekyll、IIS Express。
實測數據：
改善前：本機 .aspx 測試 404。
改善後：改用 Jekyll 預覽 .aspx 相容行為正確。
改善幅度：相容性測試成功率從 0% → 100%。

Learning Points（學習要點）
核心知識點：
- Handler 映射差異
- 多預覽通道的場景切換
- 舊連結相容策略
技能要求：
- 必備技能：基本網頁伺服器概念
- 進階技能：相容性設計
延伸思考：
- 是否自訂 IIS handler 規則以模擬上線？
- 在文件中清楚說明預覽切換指引。

Practice Exercise（練習題）
- 基礎：切換不同 port 預覽不同場景。
- 進階：嘗試為 IIS Express 新增靜態映射規則。
- 專案：整理預覽切換手冊與快捷。

Assessment Criteria（評估標準）
- 功能完整性（40%）：兩通道切換順暢。
- 程式碼品質（30%）：設定清楚可復現。
- 效能優化（20%）：最少步驟達成目標。
- 創新性（10%）：最佳化切換體驗。


## Case #10: WordPress 匯出中文網址 %00%00 問題（XML 預處理 + 自寫匯入工具）

### Problem Statement（問題陳述）
業務場景：WordPress 匯出 XML 對中文網址支持不良，輸出成一長串 %00%00… 的 URL 與檔名，不僅影響 _posts 檔名，也讓留言對應失效。
技術挑戰：需要在匯入 Jekyll 前修正 URL 與檔名，保留留言對應。
影響範圍：文章永久連結、檔案命名、留言顯示。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. WordPress 匯出時中文 slug 轉為錯誤的 URL escape。
2. 匯入工具未處理中文，造成檔名/連結不可讀。
3. 留言服務以 URL 為識別，對不上新址。
深層原因：
- 架構層面：來源系統對 i18n 支援不足。
- 技術層面：slug/URL 與檔名轉換缺少自訂。
- 流程層面：缺乏匯入前的預處理步驟。

### Solution Design（解決方案設計）
解決策略：先對 WordPress XML 進行中文 URL 修正（解碼、轉正確 slug），再以自寫 C# 工具產生正確的 Jekyll front matter 與檔名，並保留留言對應 ID。

實施步驟：
1. 預處理 XML
- 實作細節：對 URL 欄位進行解碼/正規化。
- 所需資源：.NET/C#、HttpUtility。
- 預估時間：1–2 小時
2. 產生 Jekyll 檔案
- 實作細節：根據 XML 產生 _posts 檔案、permalink、redirect_from、wordpress_postid。
- 所需資源：自寫匯入工具。
- 預估時間：2–4 小時

關鍵程式碼/設定：
```csharp
// C#：修正中文網址 slug
var raw = "%E7%B4%80%E9%8C%84"; // 範例
var decoded = System.Web.HttpUtility.UrlDecode(raw); // "紀錄"
var slug = decoded; // 可另做正規化/拼音轉換
// 產生 front matter 含 permalink 與 wordpress_postid
```

實作環境：Windows、.NET/C#、Jekyll。
實測數據：
改善前：檔名與 URL 不可讀、留言對不上。
改善後：檔名與 URL 正常、留言可對應。
改善幅度：功能性恢復 100%；遷移可行。

Learning Points（學習要點）
核心知識點：
- 匯入管線設計與預處理
- URL/slug 與檔名策略
- 留言識別關聯（url/id）
技能要求：
- 必備技能：C#/.NET、字串處理
- 進階技能：批次檔案生成、自動化遷移
延伸思考：
- 是否將工具開源供他人使用？
- slug 規則統一與長期治理。

Practice Exercise（練習題）
- 基礎：取一筆中文 URL 做解碼並建立合理 slug。
- 進階：撰寫小工具批次輸出 10 篇 _posts。
- 專案：完成完整匯入工具（含 redirect_from 與 comments 對應）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確檔名、permalink、留言對應。
- 程式碼品質（30%）：程式結構清晰、容錯。
- 效能優化（20%）：批次處理速度與記憶體管理。
- 創新性（10%）：規則化與擴充性設計。


## Case #11: 留言對應修復（URL 正規化 + ID 標記）

### Problem Statement（問題陳述）
業務場景：留言系統多以 URL 為識別。若僅修正文章 permalink 而未修正匯出 XML 的 URL，留言將全數遺失。
技術挑戰：確保新 permalink 與留言識別一致，或提供舊→新對照。
影響範圍：社群互動完整性、SEO、遷移可信度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. WordPress 匯出 XML 的中文網址錯誤。
2. 留言系統依賴 URL/identifier 無法匹配。
3. 僅修文不修 URL 的部分遷移作法不完整。
深層原因：
- 架構層面：留言識別與 permalink 綁定強。
- 技術層面：需要 URL 對照映射。
- 流程層面：遷移步驟未考慮留言。

### Solution Design（解決方案設計）
解決策略：遷移流程中加入 URL 正規化，並在 front matter 記錄原系統 post id（wordpress_postid），供前端或留言服務使用。

實施步驟：
1. 修正匯出 XML 的 URL
- 實作細節：先解決 %00%00 問題（見 Case #10）。
- 所需資源：C# 工具。
- 預估時間：1–2 小時
2. 前置資料標記
- 實作細節：front matter 加入 wordpress_postid 與正規 permalink。
- 所需資源：Jekyll。
- 預估時間：1 小時

關鍵程式碼/設定：
```yaml
---
title: "終於升速了!"
permalink: "/2008/10/10/終於升速了/"
wordpress_postid: 59
---
```

實作環境：Jekyll、前端留言插件（FB/Disqus）。
實測數據：
改善前：留言消失。
改善後：留言對回原文（取決於留言服務識別策略）。
改善幅度：留言可見率 0% → 可用（功能性修復）。

Learning Points（學習要點）
核心知識點：
- 留言識別與 URL/ID 綁定
- 遷移資料對齊與映射
- front matter 拓展策略
技能要求：
- 必備技能：YAML/前端插件使用
- 進階技能：資料對齊與批次處理
延伸思考：
- 是否以 Disqus identifier 直接設定？
- 沒有原始留言 API 時的替代方案？

Practice Exercise（練習題）
- 基礎：在一篇文章加入 wordpress_postid 並顯示。
- 進階：建立 id→permalink 映射檔。
- 專案：製作留言遷移策略與 PoC。

Assessment Criteria（評估標準）
- 功能完整性（40%）：留言能對應。
- 程式碼品質（30%）：front matter 清楚一致。
- 效能優化（20%）：批次產出映射。
- 創新性（10%）：備援策略設計。


## Case #12: 分類與標籤的完整遷移與展示

### Problem Statement（問題陳述）
業務場景：部分匯入工具僅支援 category 或 tags，且主題不一定同時提供分類/標籤雲。需保留舊文章的內容組織與導覽。
技術挑戰：挑選支援完善的主題並在匯出時標記正確分類/標籤。
影響範圍：導覽體驗、SEO、內容維護。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 匯出工具與主題支援不一。
2. 缺少統一前置資料欄位。
3. 導覽頁/雲圖需主題支援。
深層原因：
- 架構層面：內容結構與佈景緊耦合。
- 技術層面：前置資料標準化不足。
- 流程層面：未先驗證主題相容性。

### Solution Design（解決方案設計）
解決策略：挑選同時支援 categories/tags 的主題；匯出時將分類與標籤完整寫入 front matter，確保後續模板可渲染雲圖或索引。

實施步驟：
1. 主題驗證
- 實作細節：挑選支援 categories/tags 的佈景。
- 所需資源：Jekyll 主題。
- 預估時間：0.5–1 小時
2. 完整標記
- 實作細節：確保 front matter 同時含有 categories 與 tags。
- 所需資源：匯入工具/手動補齊。
- 預估時間：批次 1–2 小時

關鍵程式碼/設定：
```yaml
---
layout: post
title: "範例"
categories: ["技術","遷移"]
tags: ["Jekyll","WordPress","Migration"]
---
```

實作環境：Jekyll、支援分類/標籤的主題。
實測數據：
改善前：僅部分分類/標籤可見。
改善後：分類/標籤完整渲染，雲圖與列表可用。
改善幅度：導覽覆蓋率 50% → 100%。

Learning Points（學習要點）
核心知識點：
- front matter 結構化資料
- 主題功能驗證
- 內容導覽設計
技能要求：
- 必備技能：YAML、主題設定
- 進階技能：模板客製
延伸思考：
- 是否建立 tags/categories 的索引頁自動生成？
- 標籤治理與合併策略。

Practice Exercise（練習題）
- 基礎：為 3 篇文章補齊分類與標籤。
- 進階：建立 categories/tags 索引頁。
- 專案：整理全站標籤治理方案與統一命名。

Assessment Criteria（評估標準）
- 功能完整性（40%）：導覽完整。
- 程式碼品質（30%）：front matter 一致性。
- 效能優化（20%）：索引頁生成效率。
- 創新性（10%）：導覽體驗設計。


## Case #13: 舊連結相容（jekyll-redirect-from 插件）

### Problem Statement（問題陳述）
業務場景：歷經多套系統，外部連結格式多樣（含 .aspx）。遷移後需讓舊連結正常導至新網址，避免 404 與 SEO 流失。
技術挑戰：同一內容需接受多個來源 URL，並於靜態站內完成重導。
影響範圍：SEO、用戶體驗、外部引用。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多代系統產生不同 URL 模式。
2. 靜態站需在生成期就處理重導資訊。
3. 需支援多個舊路徑。
深層原因：
- 架構層面：靜態站內導策略。
- 技術層面：生成器插件與前置資料。
- 流程層面：舊→新映射維護。

### Solution Design（解決方案設計）
解決策略：使用 jekyll-redirect-from 插件，在 front matter 中列出所有舊路徑，建置時自動生成重導頁。

實施步驟：
1. 安裝與啟用插件
- 實作細節：_config.yml 加入 jekyll-redirect-from。
- 所需資源：GitHub Pages 內建支援。
- 預估時間：5 分鐘
2. 為文章補齊 redirect_from
- 實作細節：列出所有舊 URL。
- 所需資源：匯入工具/手工整理。
- 預估時間：視數量 1–3 小時

關鍵程式碼/設定：
```yaml
# _config.yml
plugins:
  - jekyll-redirect-from
```

```yaml
---
title: "終於升速了!"
permalink: "/2008/10/10/終於升速了/"
redirect_from:
  - /columns/post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx/
  - /post/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx/
  - /post/e7b582e696bce58d87e9809fe4ba86!.aspx/
  - /columns/2008/10/10/e7b582e696bce58d87e9809fe4ba86!.aspx/
  - /columns/e7b582e696bce58d87e9809fe4ba86!.aspx/
wordpress_postid: 59
---
```

實作環境：GitHub Pages + Jekyll。
實測數據：
改善前：舊連結 404。
改善後：舊連結 200/301 導向新頁。
改善幅度：相容成功率 0% → 100%。

Learning Points（學習要點）
核心知識點：
- 靜態重導設計
- front matter 多來源路徑策略
- 遷移中的 SEO 保全
技能要求：
- 必備技能：YAML、Jekyll 插件
- 進階技能：映射表生成
延伸思考：
- 是否產出 sitemap 與 301 規則報表？
- 舊→新映射的長期維護方法。

Practice Exercise（練習題）
- 基礎：為一篇文加入兩個 redirect_from。
- 進階：寫腳本從 CSV 生成 front matter。
- 專案：完成全站舊連結對照與驗證。

Assessment Criteria（評估標準）
- 功能完整性（40%）：重導全通。
- 程式碼品質（30%）：front matter 結構正確。
- 效能優化（20%）：建置時間影響可控。
- 創新性（10%）：映射管理工具化。


## Case #14: 靜態站處理 WordPress 查詢字串 "?p=59"（前端 JS 重導）

### Problem Statement（問題陳述）
業務場景：WordPress 常見 query 模式 ?p=59，靜態站無法以 query 決定頁面，需保留此連結相容。
技術挑戰：無後端路由，需於前端解析並導向對應 permalink。
影響範圍：舊連結相容性、用戶體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態站不解析 query route。
2. 舊連結分發仍存在。
3. 缺少 id → permalink 對照。
深層原因：
- 架構層面：無 runtime 路由。
- 技術層面：需前端實現重導。
- 流程層面：映射資料維護。

### Solution Design（解決方案設計）
解決策略：在根 index 或專用 redirect 頁注入 JS，讀取 ?p=xxx，查表導向正確 permalink。映射表可由匯入工具產生。

實施步驟：
1. 建立映射表
- 實作細節：以 wordpress_postid → permalink 的 JSON。
- 所需資源：匯入工具輸出 JSON。
- 預估時間：0.5–1 小時
2. 前端導向
- 實作細節：在頁面載入時解析 query，重導。
- 所需資源：JavaScript。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```html
<script>
  const map = { "59": "/2008/10/10/終於升速了/" };
  const params = new URLSearchParams(location.search);
  const id = params.get('p');
  if (id && map[id]) location.replace(map[id]);
</script>
```

實作環境：Jekyll、前端 JS。
實測數據：
改善前：/?p=59 404 或停留首頁。
改善後：/?p=59 導向正確文章。
改善幅度：相容成功率 0% → 100%。

Learning Points（學習要點）
核心知識點：
- 靜態站前端重導
- 映射資料生成與維護
- 無後端情境的相容策略
技能要求：
- 必備技能：JavaScript 基礎
- 進階技能：資料生成自動化
延伸思考：
- 使用 Service Worker 或 Edge 函式是否更優？
- 大型映射表的載入效能如何優化？

Practice Exercise（練習題）
- 基礎：為兩個 id 完成重導。
- 進階：自動從 front matter 產出 JSON 映射。
- 專案：建立全站 query 重導方案與測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：重導可用、無循環。
- 程式碼品質（30%）：結構清晰、容錯。
- 效能優化（20%）：映射載入最小化。
- 創新性（10%）：生成與部署自動化。


## Case #15: 用 Liquid 嵌入 GA/AdSense/OG/FB 按鈕等第三方功能

### Problem Statement（問題陳述）
業務場景：靜態站缺乏動態功能（分析、廣告、社交），需以最小成本補齊。
技術挑戰：需根據頁面資訊（title、permalink）動態填值，並可重用於模板。
影響範圍：成效追蹤、社群分享、收益。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態站無內建外掛生態。
2. 第三方功能需正確 meta 與腳本。
3. 每頁資訊需注入。
深層原因：
- 架構層面：以模板引擎提供變數注入。
- 技術層面：Liquid 可動態渲染。
- 流程層面：集中於 _includes 管理。

### Solution Design（解決方案設計）
解決策略：以 Liquid 在 _includes 與 _layouts 中插入第三方 snippet，使用 page/site 變數填充，達到可維護的一次定義、全站生效。

實施步驟：
1. 加入 GA/OG/Ad/FB Snippet
- 實作細節：把官方 HTML/JS 貼入 _includes。
- 所需資源：GA/FB/AdSense 代碼。
- 預估時間：0.5–1 小時
2. 模板整合
- 實作細節：在 default/post 佈局 include。
- 所需資源：Liquid 模板。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```html
<!-- _includes/og.html -->
<meta property="og:title" content="{{ page.title }}">
<meta property="og:url" content="{{ site.url }}{{ page.url }}">
<meta property="og:type" content="article">

<!-- _includes/ga.html -->
<script>/* Google Analytics snippet，略 */</script>

<!-- _layouts/post.html -->
<html>
<head>
  {% include og.html %}{% include ga.html %}
</head>
<body> ... FB 按讚/分享 snippet ... </body>
</html>
```

實作環境：Jekyll、Liquid。
實測數據：
改善前：無分析、無社交 meta。
改善後：GA/OG/FB/Ad 生效（功能補齊）。
改善幅度：功能覆蓋 0% → 100%。

Learning Points（學習要點）
核心知識點：
- Liquid 模板與變數
- _includes 重用模式
- 第三方腳本整合
技能要求：
- 必備技能：HTML、Liquid
- 進階技能：SEO/social meta 最佳化
延伸思考：
- 多環境（dev/prod）注入開關如何處理？
- 隱私與 Cookie 同意策略？

Practice Exercise（練習題）
- 基礎：加入 OG 與 GA 至 post 佈局。
- 進階：加入條件渲染（僅 prod 啟用）。
- 專案：建立可配置的第三方整合模組。

Assessment Criteria（評估標準）
- 功能完整性（40%）：meta/腳本正確。
- 程式碼品質（30%）：模板分層清楚。
- 效能優化（20%）：載入最小化。
- 創新性（10%）：條件化與權限控管。


## Case #16: 以 Git 管理內容版本與站點設定（Branch/PR/回溯）

### Problem Statement（問題陳述）
業務場景：傳統部落格對文章版本控制薄弱，無法對多篇文章、站點設定一起版本化與回溯。需要開發者友善的工作流。
技術挑戰：將內容、設定、模板皆納入版本管理，支援分支、PR、備份與還原。
影響範圍：內容品質、審核流程、回滾。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. CMS 內建版本控制粒度小。
2. 缺乏多檔一致回溯能力。
3. 難以採用開發者協作流程。
深層原因：
- 架構層面：內容即程式碼。
- 技術層面：Git 適合文本與設定。
- 流程層面：PR/Review/Branch 流程。

### Solution Design（解決方案設計）
解決策略：將 posts、_config.yml、_layouts 等全部納入 repo。以 branch 建站改版，用 PR 審核內容，必要時回滾。支援 fork/pull request。

實施步驟：
1. 建立標準 repo 結構
- 實作細節：明確目錄、.gitignore。
- 所需資源：Git。
- 預估時間：0.5 小時
2. 設計流程
- 實作細節：feature 分支寫作、PR 審核、squash merge。
- 所需資源：GitHub。
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
git checkout -b feature/new-post
git add _posts/2025-01-01-my-post.md _config.yml
git commit -m "Add new post + config"
git push origin feature/new-post
# 建立 PR，審核通過後 merge
```

實作環境：GitHub/Git。
實測數據：
改善前：文章/設定分散、回溯困難。
改善後：統一版本化，可 branch/merge/rollback。
改善幅度：治理能力顯著提升（質性）。

Learning Points（學習要點）
核心知識點：
- 內容即程式碼（docs-as-code）
- PR 與審核流程
- 回滾與災難復原
技能要求：
- 必備技能：Git 基礎
- 進階技能：GitHub Flow/PR Review
延伸思考：
- 以 Actions 驗證鏈（lint、連結檢查）。
- 保護分支與審核規則設計。

Practice Exercise（練習題）
- 基礎：建立 feature 分支新增文章。
- 進階：提交 PR 並請同伴審核。
- 專案：導入 CI 驗證（連結/大小寫檔名）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：全站受控。
- 程式碼品質（30%）：提交與歷史乾淨。
- 效能優化（20%）：CI 檢查合理。
- 創新性（10%）：流程自動化。


## Case #17: 使用 Jekyll Drafts 保護未完成文章（--drafts）

### Problem Statement（問題陳述）
業務場景：不希望草稿在未完成前就公開，但仍需本機完整預覽與測試。
技術挑戰：保持草稿私密的同時，於本機預覽包含草稿的全站效果。
影響範圍：內容安全、發佈準確性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 草稿預覽需求與公開發佈矛盾。
2. 預覽期需顯示尚未發佈內容。
3. 手動控管容易誤發。
深層原因：
- 架構層面：編譯期標記草稿。
- 技術層面：Jekyll 提供 drafts 模式。
- 流程層面：預覽與上線分離。

### Solution Design（解決方案設計）
解決策略：本機用 jekyll s --drafts（或 --draft），將 _drafts 內容一併生成；正式發佈只 push 穩定內容，避免草稿上線。

實施步驟：
1. 建立 _drafts 目錄
- 實作細節：草稿放於 _drafts，不含日期。
- 所需資源：Jekyll。
- 預估時間：5 分鐘
2. 本機預覽
- 實作細節：jekyll s --draft -w。
- 所需資源：Jekyll。
- 預估時間：5 分鐘

關鍵程式碼/設定：
```bash
# _drafts/my-next-post.md
jekyll s --draft -w
```

實作環境：Jekyll。
實測數據：
改善前：易誤發或無法完整預覽。
改善後：草稿安全、預覽完整。
改善幅度：誤發風險大幅降低（質性）。

Learning Points（學習要點）
核心知識點：
- 草稿管理
- 編譯期條件生成
- 預覽/上線分離
技能要求：
- 必備技能：Jekyll 基礎
- 進階技能：流程治理
延伸思考：
- 搭配分支（draft-branch）管理草稿？
- 草稿分享給協作者的方式？

Practice Exercise（練習題）
- 基礎：建立一篇草稿並預覽。
- 進階：草稿轉正並發佈。
- 專案：草稿審核工作流（label/PR）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：草稿不外流。
- 程式碼品質（30%）：目錄結構清晰。
- 效能優化（20%）：預覽快速。
- 創新性（10%）：治理流程設計。


--------------------------------
案例分類
--------------------------------

1. 按難度分類
- 入門級（適合初學者）
  - Case 7（中文檔名繞道）
  - Case 12（分類與標籤）
  - Case 15（Liquid 嵌入第三方）
  - Case 16（Git 版本管理）
  - Case 17（Drafts 模式）
- 中級（需要一定基礎）
  - Case 2（Windows 本機工作流）
  - Case 3（Docker polling 問題）
  - Case 4（PowerShell 自動重啟）
  - Case 5（切換 Jekyll for Windows）
  - Case 6（Ruby 版本相容）
  - Case 8（大小寫敏感）
  - Case 9（.aspx 預覽切換）
  - Case 14（Query 前端重導）
- 高級（需要深厚經驗）
  - Case 1（架構轉換：Blogging as Code）
  - Case 10（WordPress 中文 URL 遷移）
  - Case 11（留言對應修復）
  - Case 13（多來源舊連結相容）

2. 按技術領域分類
- 架構設計類：Case 1
- 效能優化類：Case 2、3、4、5、8
- 整合開發類：Case 7、12、13, 14, 15, 16, 17
- 除錯診斷類：Case 6、8、9、10、11
- 安全防護類：無（可延伸至權限/隱私/內容防護的未來工作）

3. 按學習目標分類
- 概念理解型：Case 1、16
- 技能練習型：Case 2、5、7、12、15、17
- 問題解決型：Case 3、4、6、8、9、10、11、13、14
- 創新應用型：Case 4、15、16（流程自動化與模板化）

--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 起步（概念與基礎）
  1) 先學 Case 1（整體架構轉換概念），理解靜態站可行性與 as-code 思維。
  2) 接著 Case 16（Git 版本化），建立內容即程式碼的流程基礎。
  3) 再做 Case 17（Drafts 模式）確保開發安全。

- 本機開發與效能（Windows 路線）
  4) Case 2（Windows 工作流），建立雙通道預覽能力。
  5) Case 6（Ruby 相容）確保環境穩定。
  6) Case 5（改用 Jekyll for Windows）獲得更佳效能。
  7) Case 7（中文檔名繞道）、Case 8（大小寫敏感），確保預覽與上線一致性。
  8) Case 9（.aspx 差異）處理特殊相容場景。

- Docker 替代方案與自動化（可選分支）
  9) Case 3（Docker polling 問題）理解限制。
  10) Case 4（PowerShell 自動重啟）建置事件驅動式工作流。

- 遷移與相容（資料與連結）
  11) Case 10（中文 URL 遷移）先修正來源資料。
  12) Case 11（留言對應修復）保留社群資產。
  13) Case 12（分類/標籤完整化）恢復導覽。
  14) Case 13（redirect-from）處理舊路徑相容。
  15) Case 14（?p=59 前端重導）補齊 query 類連結。

- 完整度與營運
  16) Case 15（GA/OG/Ad/FB 整合）補齊營運所需觀測與社交功能。

依賴關係摘要：
- Case 1 → Case 16 → Case 17 → Case 2/5/6 → Case 7/8/9
- Docker 路線：Case 3 → Case 4（可替代 Case 5）
- 遷移路線：Case 10 → Case 11 → Case 12 → Case 13 → Case 14
- 最後整合：Case 15

完整學習路徑建議：
1) Case 1 → 16 → 17（建立理念與基礎流程）
2) Windows 本機開發：Case 2 → 6 → 5 → 7 → 8 → 9
   或 Docker 分支：Case 3 → 4
3) 資料遷移與相容：Case 10 → 11 → 12 → 13 → 14
4) 營運整合：Case 15

此路徑自概念→環境→效能→遷移→營運，能在最短時間內獲得有效果的靜態部落格開發與遷移能力。