---
layout: synthesis
title: "[.NET Core] Running .NET Core RC1 on Docker - DOTNET CLI"
synthesis_type: solution
source_post: /2015/12/06/net-core-running-net-core-rc1-on-docker/
redirect_from:
  - /2015/12/06/net-core-running-net-core-rc1-on-docker/solution/
---

以下內容基於文章所提供的資訊，萃取並整理出15個具教學價值的「問題解決案例」。每個案例聚焦在實際遇到的問題、可追溯的成因、可操作的解法（含命令與程式碼片段），以及可評估的效益與練習建議。文中若未提供明確數據，則以「建議指標」形態呈現評估方式，便於教學與能力評估。

## Case #1: 只在 Docker 內進行編譯（不在容器內執行）
### Problem Statement（問題陳述）
**業務場景**：團隊在 Linux 主機上嘗試 .NET Core RC1，但現有運行環境尚未容器化，期望利用 Docker 快速取得一致的 SDK/CLI 來「編譯」專案，同時仍在宿主機上管理/執行產物（或交付到其他環境）。
**技術挑戰**：如何在不長駐容器、且不把應用放入容器執行的前提下，只借用容器中的 DOTNET CLI 完成編譯。
**影響範圍**：若做不到，開發者需在宿主機手動安裝/維護 SDK，版本不一致、環境污染與重現性差。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 開發環境需要 RC1 工具鏈，但宿主機可能並未安裝或版本不一致。
2. 不希望把執行流程也容器化，只需要編譯動作。
3. 缺乏「一次性容器」的操作模式認知。

**深層原因**：
- 架構層面：環境管理未容器化，需局部採用容器化能力（編譯）以維持低侵入。
- 技術層面：不了解 Docker volume、工作目錄與 --rm 的組合使用。
- 流程層面：缺乏「編譯環境即容器」的可拋棄式工作流設計。

### Solution Design（解決方案設計）
**解決策略**：使用官方 microsoft/dotnet 映像，將原始碼目錄以 volume 掛載進容器，設定容器內工作目錄，執行 dotnet compile 後即刪除容器狀態（--rm），達成「只在容器內編譯」。

**實施步驟**：
1. 取得官方 CLI 映像
- 實作細節：確保可從 Docker Hub 取得 RC1 前後相容映像
- 所需資源：Docker Engine、microsoft/dotnet:0.0.1-alpha
- 預估時間：5-10 分鐘（取決於網路）

2. 編譯（一次性容器）
- 實作細節：將宿主當前目錄掛載到容器 /myapp，並指定工作目錄
- 所需資源：Docker、DOTNET CLI
- 預估時間：1-5 分鐘（首次還要還原套件）

**關鍵程式碼/設定**：
```bash
# 只在容器內編譯，不進入容器 Shell
docker run --rm -v "$PWD":/myapp -w /myapp microsoft/dotnet:0.0.1-alpha dotnet compile
```

實際案例：引用文章中 GitHub README 的用法，將目前目錄掛載至容器，並以 dotnet compile 完成編譯。
實作環境：Linux 主機 + Docker，引入 microsoft/dotnet:0.0.1-alpha CLI 映像。
實測數據：
- 改善前：需在宿主機安裝/維護 SDK，版本管理困難
- 改善後：不需安裝 SDK；編譯環境可重現
- 改善幅度：定性改善（環境一致性↑、維護成本↓）

Learning Points（學習要點）
核心知識點：
- Docker volume 與工作目錄 -v 與 -w 的使用
- 一次性容器 --rm 的價值
- dotnet compile 的基本用法

技能要求：
- 必備技能：Docker 基礎、Linux CLI、.NET CLI 基本命令
- 進階技能：容器化建置流程設計、CI 中使用容器建置

延伸思考：
- 也可將產物 publish 後產出至宿主機目錄供部署
- 風險：容器刪除後不保留任何未掛載的檔案
- 優化：將 NuGet 快取掛載為 volume 以加速還原（進階議題）

Practice Exercise（練習題）
- 基礎練習：用上述命令對 HelloWorld 專案進行編譯（30 分鐘）
- 進階練習：加入依賴套件，觀察首次 vs 二次編譯時間差（2 小時）
- 專案練習：建立小型 CLI 專案並在 CI 中以相同方式建置（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能在容器內完成編譯並產出可執行/可運行產物
- 程式碼品質（30%）：專案結構清晰，設定檔簡潔
- 效能優化（20%）：合理利用 volume、減少重複還原
- 創新性（10%）：延伸出可重現的 build 腳本或 CI 範本


## Case #2: 用互動式 Shell 進行快速迭代（--rm + -it）
### Problem Statement（問題陳述）
**業務場景**：在原型開發與測試階段，需要頻繁進出容器執行 init/restore/compile/run，單次命令不便於持續迭代。
**技術挑戰**：如何在容器內開一個可互動的 Shell，完成多次命令交互後再自動清理容器狀態。
**影響範圍**：若需要反覆 docker run，開發體驗差、效率低。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 單次命令模式不便於連續操作。
2. 未善用 -it 及 --rm 的組合。
3. 未將源碼目錄掛載進容器導致每次進入容器都需重新準備。

**深層原因**：
- 架構層面：缺乏適合原型與迭代的容器工作流。
- 技術層面：對 Docker 互動模式的理解不足。
- 流程層面：未定義快速迭代的容器操作標準。

### Solution Design（解決方案設計）
**解決策略**：以 -it 啟動 bash，掛載源碼路徑，工作完畢退出 Shell 即自動清除容器（--rm），達成快速迭代與無狀態整潔。

**實施步驟**：
1. 啟動互動式容器
- 實作細節：掛載 $PWD、指定工作路徑、-it 進入 bash
- 所需資源：microsoft/dotnet 映像
- 預估時間：即時

2. 在容器內進行 dotnet 命令
- 實作細節：依序 dotnet init、dotnet restore、dotnet compile、dotnet run
- 所需資源：DOTNET CLI
- 預估時間：5-20 分鐘（首次 restore 時較久）

**關鍵程式碼/設定**：
```bash
# 互動式 shell，結束後自動清理容器
docker run --name dotnet-dev --rm -it \
  -v "$PWD":/work -w /work \
  microsoft/dotnet /bin/bash

# 容器內操作
dotnet init
dotnet restore
dotnet compile
dotnet run
```

實際案例：文章作者採用此方式進入容器 shell 後進行多次命令與測試。
實作環境：Linux + Docker + microsoft/dotnet:0.0.1-alpha。
實測數據：
- 改善前：每次命令皆需 docker run；上下文不連續
- 改善後：一次進入，多次操作；退出即清理
- 改善幅度：定性改善（迭代速度↑、殘留容器數=0）

Learning Points（學習要點）
核心知識點：
- docker run -it 與 --rm 的綜合使用
- 互動式容器適配開發迭代

技能要求：
- 必備技能：Docker CLI、.NET CLI 常用命令
- 進階技能：制定團隊容器迭代規範

延伸思考：
- 可固定掛載 NuGet cache（進階議題）以加速 restore
- 風險：未掛載的修改在容器刪除後即消失
- 優化：配合 Makefile 或腳本封裝常用命令

Practice Exercise（練習題）
- 基礎練習：在容器內完成 HelloWorld 的 init→restore→compile→run（30 分鐘）
- 進階練習：修改程式碼並反覆 run，體驗迭代效率（2 小時）
- 專案練習：把此流程寫成開發腳本提供團隊使用（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能在單次 shell 會話中完成整套流程
- 程式碼品質（30%）：腳本化、結構清楚
- 效能優化（20%）：迭代操作步驟最小化
- 創新性（10%）：加入常見檢查如 dotnet --info、清理工具等


## Case #3: 正確選擇 Docker 基礎映像（microsoft/aspnet vs microsoft/dotnet）
### Problem Statement（問題陳述）
**業務場景**：團隊同時接觸 Beta 時期 DNX 工具鏈與 RC1 的 DOTNET CLI，常混用映像與指令，導致環境不一致與操作混亂。
**技術挑戰**：如何根據目標工具鏈正確選擇映像：microsoft/aspnet（DNX/DNVM/DNU）或 microsoft/dotnet（DOTNET CLI）。
**影響範圍**：若映像選擇錯誤，會導致指令無法使用、依賴不匹配、建置失敗。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 同時存在兩代工具鏈（DNX vs DOTNET CLI）。
2. 映像名稱相近，易混淆用途。
3. 專案目標框架與工具鏈未對齊。

**深層原因**：
- 架構層面：工具鏈演進造成短期並存。
- 技術層面：對映像內工具差異認識不足。
- 流程層面：專案/團隊未制定工具版本策略。

### Solution Design（解決方案設計）
**解決策略**：明確區分用途：microsoft/aspnet（DNX 系列）給舊專案；microsoft/dotnet（DOTNET CLI）給 RC1 新工具。新專案優先使用 microsoft/dotnet，舊專案則持續用 microsoft/aspnet 或升級後再切換。

**實施步驟**：
1. 決策與拉取映像
- 實作細節：根據專案狀態選擇映像
- 所需資源：Docker Hub
- 預估時間：5-10 分鐘

2. 驗證映像內容
- 實作細節：進容器檢查 dotnet 或 dnx/dnu/dnvm 是否存在
- 所需資源：-it 進入容器
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bash
# DNX 舊工具（RC1 前後的 ASP.NET）：
docker pull microsoft/aspnet

# 新 DOTNET CLI：
docker pull microsoft/dotnet

# 驗證（進入容器查看指令）
docker run --rm -it microsoft/dotnet dotnet -h
docker run --rm -it microsoft/aspnet dnx --help
```

實際案例：文章明確指出兩個映像的用途與差異。
實作環境：Docker + 兩種官方映像。
實測數據：
- 改善前：工具鏈混用導致指令不可用、建置中斷
- 改善後：工具與映像對齊，流程順暢
- 改善幅度：定性改善（失敗率↓、溝通成本↓）

Learning Points（學習要點）
核心知識點：
- DNX/DNU/DNVM vs DOTNET CLI 的世代差異
- 官方映像的用途區分

技能要求：
- 必備技能：Docker、.NET 工具鏈基礎知識
- 進階技能：制定工具版本治理策略

延伸思考：
- 何時升級舊專案至 DOTNET CLI？
- 風險：升級過程中的相依性不相容
- 優化：用容器平行維護兩套環境以降低風險

Practice Exercise（練習題）
- 基礎練習：分別進入兩種映像驗證可用指令（30 分鐘）
- 進階練習：將一個 HelloWorld 在兩個映像下建立與執行（2 小時）
- 專案練習：制定團隊映像選用準則文件（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：兩映像操作與指令驗證完整
- 程式碼品質（30%）：操作腳本與文件清晰
- 效能優化（20%）：拉取與驗證流程高效
- 創新性（10%）：提出可視化決策流程或工具鏈偵測腳本


## Case #4: DNX 工具與 DOTNET CLI 指令對應與過渡
### Problem Statement（問題陳述）
**業務場景**：團隊成員習慣 DNU restore、DNX run 等命令，轉向 DOTNET CLI 後常記不住新指令，影響效率。
**技術挑戰**：建立 DNX→DOTNET CLI 的指令對照，降低認知成本。
**影響範圍**：容易用錯命令、查找時間增加。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 指令名稱與用法變動。
2. 文件不足、搜尋資料少。
3. 舊習慣難以快速切換。

**深層原因**：
- 架構層面：工具整合（DNVM/DNX/DNU→dotnet 一個入口）。
- 技術層面：命令參數與語意改變。
- 流程層面：未建立團隊遷移對照表。

### Solution Design（解決方案設計）
**解決策略**：建立最小對照清單，將常用 DNX 命令映射至 DOTNET CLI；在容器與文件中內嵌此對照，協助過渡。

**實施步驟**：
1. 撰寫對照說明
- 實作細節：整理常用命令映射
- 所需資源：README/內部Wiki
- 預估時間：1 小時

2. 內嵌輔助腳本
- 實作細節：提供 help.sh 顯示對照
- 所需資源：Shell
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# DNX -> DOTNET CLI 映射（說明用）
# DNVM (runtime 管理) -> dotnet（整合入口，版本隨映像/安裝而定）
# DNU restore -> dotnet restore
# DNX run     -> dotnet run
# DNU publish -> dotnet publish
# DNX build   -> dotnet compile
```

實際案例：文章說明 DOTNET CLI 整合 DNVM/DNX/DNU 並命名更清晰。
實作環境：Docker + microsoft/dotnet。
實測數據：
- 改善前：轉換成本高，操作錯誤頻繁
- 改善後：學習曲線降低，命令一致
- 改善幅度：定性改善（學習成本↓）

Learning Points（學習要點）
核心知識點：
- 指令對照與變更點
- 新 CLI 的單入口理念

技能要求：
- 必備技能：了解舊指令的意義
- 進階技能：文件化/訓練他人

延伸思考：
- 是否需要在 CI 中替換舊命令？
- 風險：老專案仍需舊命令
- 優化：提供兩套腳本薄纏（shim）期間過渡

Practice Exercise（練習題）
- 基礎練習：把 DNU restore 改用 dotnet restore（30 分鐘）
- 進階練習：將舊專案 build/run 腳本全面換成 dotnet（2 小時）
- 專案練習：出一份團隊過渡指南與腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：新命令可完整替代舊命令
- 程式碼品質（30%）：對照文檔與腳本清晰
- 效能優化（20%）：命令數量與參數簡化
- 創新性（10%）：提供自動檢測與提示工具


## Case #5: 在容器中用 dotnet init 建立專案骨架
### Problem Statement（問題陳述）
**業務場景**：無法使用 Visual Studio，在 Linux 容器內需快速建立 .NET Core RC1 專案並開始撰寫程式。
**技術挑戰**：在 CLI/容器環境下快速產生 Program.cs 與 project.json（RC1 時期）。
**影響範圍**：若無快速起手方式，會阻礙學習與迭代。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. GUI IDE 不可用或不便。
2. 不熟悉 RC1 期的 CLI 子命令。
3. 文件稀少。

**深層原因**：
- 架構層面：CLI 驅動的起手體驗需建立。
- 技術層面：dotnet init 隱藏在 -h 未列出的命令中（當時）。
- 流程層面：缺乏標準化起手步驟。

### Solution Design（解決方案設計）
**解決策略**：使用 dotnet init 在當前目錄產生骨架，立即跟進 restore→compile→run，完成最短可行迭代。

**實施步驟**：
1. 初始化專案
- 實作細節：dotnet init 產生 Program.cs、project.json
- 所需資源：microsoft/dotnet 容器
- 預估時間：1 分鐘

2. 依賴還原並編譯運行
- 實作細節：dotnet restore→compile→run
- 所需資源：NuGet 頻寬
- 預估時間：5-20 分鐘（首次）

**關鍵程式碼/設定**：
```bash
# 容器內
mkdir /tmp/HelloWorld && cd /tmp/HelloWorld
dotnet init
dotnet restore
dotnet compile
dotnet run
```

實際案例：文章示範執行後生成 Program.cs 與 project.json，並成功輸出「Hello World!」。
實作環境：microsoft/dotnet:0.0.1-alpha。
實測數據：
- 改善前：手動建立檔案與設定，易出錯
- 改善後：一鍵產生骨架，快速啟動
- 改善幅度：定性改善（上手時間↓）

Learning Points（學習要點）
核心知識點：
- dotnet init 的用途
- init→restore→compile→run 的基本循環

技能要求：
- 必備技能：CLI 操作
- 進階技能：客製化骨架/範本

延伸思考：
- 可自製範本（當時期的 CLI 功能有限）
- 限制：RC1 命令仍在變動，後續版本可能異動
- 優化：寫簡易腳本封裝四步驟

Practice Exercise（練習題）
- 基礎練習：建立 HelloWorld 並輸出環境資訊（30 分鐘）
- 進階練習：加入一個 NuGet 相依並成功編譯（2 小時）
- 專案練習：建立團隊共用範本倉庫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能成功建立並執行
- 程式碼品質（30%）：檔案結構與命名良好
- 效能優化（20%）：最小步驟完成最大結果
- 創新性（10%）：自動化腳本/範本管理


## Case #6: 使用 dotnet restore 取得 RC1 相依（大量依賴的認知與處理）
### Problem Statement（問題陳述）
**業務場景**：即使是 HelloWorld，也會在 restore 時拉下大量相依。開發者質疑是否操作錯誤或相依過多。
**技術挑戰**：理解 .NET Core 模組化後的依賴特性與還原行為，避免誤判。
**影響範圍**：對工具鏈失去信心、誤以為設定有問題。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. .NET Core 將 BCL 模組化，帶來較多細粒度套件。
2. 首次 restore 需下載完整依賴樹。
3. 網路/鏡像來源導致等待時間偏長。

**深層原因**：
- 架構層面：平台模組化設計。
- 技術層面：NuGet 的依賴解析與快取機制。
- 流程層面：未建立首次還原的心理預期與時間規劃。

### Solution Design（解決方案設計）
**解決策略**：如實使用 dotnet restore 並觀察依賴樹，接受首次耗時，後續在相同環境下將顯著縮短；必要時改用互動式容器避免重複還原。

**實施步驟**：
1. 執行還原
- 實作細節：dotnet restore；確保網路暢通
- 所需資源：NuGet 官方來源
- 預估時間：首次 5-20 分鐘

2. 驗證與重試
- 實作細節：檢查錯誤訊息、重跑命令
- 所需資源：容器日誌
- 預估時間：依情況

**關鍵程式碼/設定**：
```bash
# 容器內
dotnet restore
# 如需調查可加上 --verbose 或檢視輸出，理解依賴解析情形
```

實際案例：作者觀察到 HelloWorld 也需大量相依，屬正常現象。
實作環境：microsoft/dotnet:0.0.1-alpha。
實測數據：
- 改善前：對還原時間與相依量不確定
- 改善後：理解與接受首次耗時特性，流程穩定
- 改善幅度：定性改善（預期管理↑）

Learning Points（學習要點）
核心知識點：
- .NET Core 模組化與 NuGet 相依解析
- 首次還原 vs 後續還原差異

技能要求：
- 必備技能：閱讀 CLI 輸出、基本網路診斷
- 進階技能：快取與鏡像優化（超出本文範圍）

延伸思考：
- 可考慮在 CI 中預熱相依（進階）
- 風險：網路不穩導致還原失敗
- 優化：持久化快取（後續延伸）

Practice Exercise（練習題）
- 基礎練習：執行 restore 並記錄主要套件（30 分鐘）
- 進階練習：新增/移除一個依賴，觀察差異（2 小時）
- 專案練習：撰寫簡報說明 .NET Core 相依模型（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能成功還原
- 程式碼品質（30%）：project.json 依賴描述清晰（RC1 時期）
- 效能優化（20%）：減少重複還原
- 創新性（10%）：提出快取策略建議


## Case #7: 編譯時出現相依版本衝突警告的處理策略
### Problem Statement（問題陳述）
**業務場景**：編譯 dotnet compile 時出現版本衝突警告，但仍可產生產物。需判斷是否可忽略或需調整依賴版本。
**技術挑戰**：在 RC1 時期相依版本更迭頻繁，如何穩定建置。
**影響範圍**：潛在執行期問題或行為不一致風險。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 依賴樹中不同套件拉入不同版本的相同組件。
2. RC1 過渡期的套件版本尚不穩定。
3. 目標框架設定與依賴選型不一致。

**深層原因**：
- 架構層面：多目標框架與跨平台依賴整合的複雜性。
- 技術層面：NuGet 版本解析策略與浮動版本。
- 流程層面：缺乏鎖定版本或一致性策略。

### Solution Design（解決方案設計）
**解決策略**：短期可先記錄與監控警告；中期在 project.json 明確鎖定一致版本或調整目標框架；必要時減少非必要依賴。

**實施步驟**：
1. 記錄與重現
- 實作細節：保存警告訊息，確認可重現
- 所需資源：建置日誌
- 預估時間：30 分鐘

2. 調整依賴版本
- 實作細節：在 project.json 指定明確版本，避免浮動
- 所需資源：NuGet 套件版本資訊
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
```json
// project.json（RC1 時代示意）
// 原則：對關鍵套件明確指定 rc1 尾碼的版本以避免衝突
{
  "version": "1.0.0-*",
  "frameworks": { "dnxcore50": {} },
  "dependencies": {
    "System.Console": "4.0.0-rc1-*"
    // 其他依賴盡量採同一 rc1 範圍
  }
}
```

實際案例：作者在 compile 出現版本警告，暫時略過並計畫後續處理。
實作環境：microsoft/dotnet:0.0.1-alpha。
實測數據：
- 改善前：警告頻繁
- 改善後：版本鎖定後警告下降（建議評估）
- 改善幅度：定性建議（以警告數量、建置穩定性衡量）

Learning Points（學習要點）
核心知識點：
- NuGet 版本解析與鎖定策略
- RC1 版本尾碼一致性

技能要求：
- 必備技能：閱讀建置輸出
- 進階技能：依賴圖分析與衝突解消

延伸思考：
- 可否建立 NuGet 鎖檔（後續版本提供）
- 風險：過度鎖定導致升級困難
- 優化：對關鍵依賴鎖定，次要依賴保留彈性

Practice Exercise（練習題）
- 基礎練習：重現一個警告並記錄（30 分鐘）
- 進階練習：調整版本以消除警告（2 小時）
- 專案練習：整理團隊依賴管理規範（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能穩定建置
- 程式碼品質（30%）：版本管理清晰
- 效能優化（20%）：警告數量下降
- 創新性（10%）：依賴分析自動化腳本


## Case #8: dotnet run 成功輸出 Hello World 的端到端驗證
### Problem Statement（問題陳述）
**業務場景**：需要在純 CLI/容器環境驗證 .NET Core RC1 的最小可運行閉環（init→restore→compile→run）。
**技術挑戰**：確保每一步都成功，並在終端看到正確輸出。
**影響範圍**：端到端若不通，後續遷移沒有基礎。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 步驟漏做或順序錯誤。
2. 依賴未還原完整。
3. 容器 stdout 顯示環境不當。

**深層原因**：
- 架構層面：CLI 驅動流程需要嚴謹步驟。
- 技術層面：對 run 的期望與輸出通道不確定。
- 流程層面：缺少最小閉環驗證流程。

### Solution Design（解決方案設計）
**解決策略**：嚴格遵循 init→restore→compile→run 四步，並確認命令輸出；必要時使用 -it 保證輸出互動。

**實施步驟**：
1. 建立與還原
- 實作細節：dotnet init、dotnet restore
- 所需資源：容器、網路
- 預估時間：10-20 分鐘（首次）

2. 編譯與執行
- 實作細節：dotnet compile、dotnet run
- 所需資源：CLI
- 預估時間：1-3 分鐘

**關鍵程式碼/設定**：
```csharp
// Program.cs
using System;
public class Program {
    public static void Main(string[] args) {
        Console.WriteLine("Hello World!");
    }
}
```

實際案例：文章最終在容器內看到 Hello World! 成功輸出。
實作環境：microsoft/dotnet:0.0.1-alpha。
實測數據：
- 改善前：無法驗證最小閉環
- 改善後：完成端到端驗證，奠定基礎
- 改善幅度：定性改善（風險↓）

Learning Points（學習要點）
核心知識點：
- CLI 基本循環四步驟
- 容器輸出與互動

技能要求：
- 必備技能：CLI 基本操作
- 進階技能：將閉環驗證納入 PR 檢查流程

延伸思考：
- 將此閉環變成 Health Check 的基準
- 風險：後續包裝/部署流程仍需補強
- 優化：加入 dotnet publish 測試

Practice Exercise（練習題）
- 基礎練習：完成並截圖輸出（30 分鐘）
- 進階練習：加入參數與輸入交互（2 小時）
- 專案練習：建立 CI 任務自動跑此閉環（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：四步驟皆通
- 程式碼品質（30%）：程式結構簡潔
- 效能優化（20%）：步驟自動化
- 創新性（10%）：加入簡單測試


## Case #9: VS2015 Beta 8 專案移轉至 RC1 CLI 專案的相容性問題
### Problem Statement（問題陳述）
**業務場景**：既有於 Windows/VS2015（ASP.NET 5 beta 8）建立的 .NET Core 專案搬到 microsoft/dotnet 容器後出現各種錯誤。
**技術挑戰**：工具鏈與套件版本跨 Beta→RC1 的變更導致相容性破裂。
**影響範圍**：專案無法在 Linux/容器中建置與運行。
**複雜度評級**：中-高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 專案目標 runtime/TFM 未對齊 .NET Core RC1。
2. 依賴的 assemblies 與套件版本不匹配。
3. NuGet 無法解析到正確 RC1 版本。

**深層原因**：
- 架構層面：跨版本的重大變更（Beta→RC）。
- 技術層面：project.json 與 TFM 的命名/語義變化。
- 流程層面：缺乏系統化升級路徑與驗證。

### Solution Design（解決方案設計）
**解決策略**：在容器內以 dotnet init 建立 RC1 範本專案，逐步移植原有程式碼與依賴；確保目標框架與套件版本全部對齊 RC1，再進行編譯與運行。

**實施步驟**：
1. 建立 RC1 範本
- 實作細節：在容器裡 dotnet init 產生骨架
- 所需資源：microsoft/dotnet
- 預估時間：30 分鐘

2. 移植與對齊
- 實作細節：移植程式碼、調整 project.json 的 frameworks 與 dependencies 至 RC1
- 所需資源：NuGet 套件資訊
- 預估時間：0.5-2 天（依專案大小）

**關鍵程式碼/設定**：
```json
// project.json（RC1 過渡示意）
// 確保使用 .NET Core 的目標框架（例如 dnxcore50 當時期）
{
  "version": "1.0.0-*",
  "frameworks": {
    "dnxcore50": {}
  },
  "dependencies": {
    "System.Console": "4.0.0-rc1-*"
  }
}
```

實際案例：作者描述 beta8 專案搬到 RC1 容器後碰到多重問題，建議全面升級至 RC1 再驗證。
實作環境：VS2015(beta8) → microsoft/dotnet(RC1)。
實測數據：
- 改善前：建置/執行錯誤頻繁
- 改善後：建立純 RC1 專案再移植，問題顯著減少（建議評估）
- 改善幅度：定性改善（成功率↑）

Learning Points（學習要點）
核心知識點：
- 跨版本升級策略（新建範本→移植）
- TFM 與依賴一致性

技能要求：
- 必備技能：讀懂 project.json
- 進階技能：相依版本管理、相容性驗證

延伸思考：
- 可否小步快跑升級，先確保 Console 專案成功
- 風險：第三方不支援 RC1 的阻塞
- 優化：分解專案、先遷移純 .NET Core 可運行部分

Practice Exercise（練習題）
- 基礎練習：用 RC1 範本重建 HelloWorld 並比較差異（30 分鐘）
- 進階練習：將一個類庫移植到 RC1（2 小時）
- 專案練習：擬定完整升級計畫並實施（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：移植後能 build/run
- 程式碼品質（30%）：依賴清晰、無冗餘
- 效能優化（20%）：減少不必要變更
- 創新性（10%）：制定可複用的升級手冊


## Case #10: 避免在 Linux 容器中預設到 .NET Framework 4.6.1（目標框架設定）
### Problem Statement（問題陳述）
**業務場景**：Windows 產生的專案預設目標 .NET Framework（如 4.6.1），搬到 Linux 容器後不支援，導致 runtime 不支援錯誤。
**技術挑戰**：在 RC1/CLI 專案中正確設定 .NET Core 目標框架。
**影響範圍**：專案無法在 Linux 上執行。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. TFM 指向 .NET Framework 而非 .NET Core。
2. project.json 沒有正確的 frameworks 配置。
3. 依賴選型也偏向 .NET Framework。

**深層原因**：
- 架構層面：跨平台目標需切換 TFM。
- 技術層面：TFM 縮寫與含義不熟悉。
- 流程層面：移植時未檢查目標框架。

### Solution Design（解決方案設計）
**解決策略**：調整 project.json 的 frameworks，明確指向 .NET Core（RC1 時期常見為 dnxcore50），移除僅支援 .NET Framework 的依賴。

**實施步驟**：
1. 檢查並修改 TFM
- 實作細節：將 net461/net46 改為 dnxcore50（RC1 時期）
- 所需資源：編輯器
- 預估時間：30 分鐘

2. 相依調整
- 實作細節：替換成 .NET Core 相容的套件
- 所需資源：NuGet
- 預估時間：1-3 小時

**關鍵程式碼/設定**：
```json
// 將 .NET Framework TFM 改為 .NET Core TFM（RC1 時期示例）
{
  "frameworks": {
    "dnxcore50": {}
  }
}
```

實際案例：作者提及容器中預設跑到 .NET Framework 4.6.1 導致不支援，須改為 .NET Core。
實作環境：VS→Linux 容器。
實測數據：
- 改善前：runtime not supported
- 改善後：轉為 .NET Core 後可編譯/運行
- 改善幅度：定性改善（可運行性↑）

Learning Points（學習要點）
核心知識點：
- TFM 的概念與選擇
- 跨平台與 BCL 差異

技能要求：
- 必備技能：編輯 project.json
- 進階技能：替換相依、API 相容性檢查

延伸思考：
- 後續版本 TFM 語法可能變更
- 風險：第三方套件不支援 .NET Core
- 優化：先用 Console 專案驗證 TFM 正確性

Practice Exercise（練習題）
- 基礎練習：將一個 net46 專案改為 dnxcore50 並成功 build（30 分鐘）
- 進階練習：找出不相容 API 並替換（2 小時）
- 專案練習：整理 TFM/相依替換清單（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：轉換後可運行
- 程式碼品質（30%）：相依清爽
- 效能優化（20%）：最少變更達成目標
- 創新性（10%）：自動檢測不相容 API 的腳本


## Case #11: NuGet 找不到正確版本的排除（RC1 源與版本對齊）
### Problem Statement（問題陳述）
**業務場景**：在容器中 restore 時，出現「找不到正確版本」或版本解析錯誤。
**技術挑戰**：RC1 時期套件源與版本頻繁更動，需確保來源與版本一致。
**影響範圍**：還原無法成功，阻塞建置。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. NuGet 源未指向正確 RC1 來源。
2. project.json 使用了不相容的版本號。
3. 本地殘留舊源或快取干擾。

**深層原因**：
- 架構層面：套件發佈渠道變動大。
- 技術層面：v2/v3 feed 與 rc1 尾碼管理。
- 流程層面：未建立標準 NuGet 源設定。

### Solution Design（解決方案設計）
**解決策略**：設定正確的 NuGet sources（官方 v3），清理或明確選擇 RC1 尾碼版本，必要時新增 RC1 相關來源（依官方公告）。

**實施步驟**：
1. 設定 NuGet.Config
- 實作細節：添加/確認 https://api.nuget.org/v3/index.json
- 所需資源：NuGet.Config
- 預估時間：30 分鐘

2. 對齊版本
- 實作細節：project.json 指定 rc1-* 範圍
- 所需資源：套件版本資訊
- 預估時間：1 小時

**關鍵程式碼/設定**：
```xml
<!-- NuGet.Config（示意） -->
<configuration>
  <packageSources>
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <!-- 如官方指引還需其他 RC1 源，酌量添加 -->
  </packageSources>
</configuration>
```

實際案例：作者遇到 nuget 找不到正確版本等問題，計畫升級與對齊 RC1 後再驗證。
實作環境：microsoft/dotnet 容器。
實測數據：
- 改善前：restore 失敗
- 改善後：源與版本對齊後 restore 成功（建議評估）
- 改善幅度：定性改善（成功率↑）

Learning Points（學習要點）
核心知識點：
- NuGet v3 源設定
- 版本尾碼與範圍指定

技能要求：
- 必備技能：編輯 NuGet.Config
- 進階技能：版本策略與套件源治理

延伸思考：
- 私有源/快取鏡像的佈建
- 風險：多源優先序造成解析混亂
- 優化：統一源管理於團隊設定檔

Practice Exercise（練習題）
- 基礎練習：配置 NuGet.Config 並成功 restore（30 分鐘）
- 進階練習：替換一個套件的 rc1 版本並驗證（2 小時）
- 專案練習：撰寫團隊 NuGet 源治理指南（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：restore 穩定成功
- 程式碼品質（30%）：設定檔清晰
- 效能優化（20%）：還原時間合理
- 創新性（10%）：源健康檢查腳本


## Case #12: 解決「assemblies 找不到」的依賴解析問題
### Problem Statement（問題陳述）
**業務場景**：移轉至容器/RC1 後報錯「找不到某些 assemblies」，即便已執行 restore。
**技術挑戰**：釐清 assemblies 缺失是 TFM 不符、版本衝突或源問題。
**影響範圍**：無法編譯/執行。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 目標框架不符導致相依不解析。
2. NuGet 源/版本錯誤。
3. restore 被舊快取或多源干擾。

**深層原因**：
- 架構層面：跨平台依賴的分歧。
- 技術層面：依賴樹解析與 TFM 相容性。
- 流程層面：缺乏標準化檢查清單。

### Solution Design（解決方案設計）
**解決策略**：逐項檢查 TFM→源→版本→restore 輸出，必要時新建 RC1 範本專案對照差異，鎖定原因後調整設定。

**實施步驟**：
1. 列出差異
- 實作細節：比較 RC1 範本的 project.json 與失敗專案的差異
- 所需資源：兩專案目錄
- 預估時間：1 小時

2. 修正並重試
- 實作細節：修正 TFM、sources、版本號後 re-restore、re-compile
- 所需資源：CLI
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
```bash
# 比對差異（示意）
diff -u failing/project.json working-rc1-template/project.json

# 重新還原與編譯
dotnet restore
dotnet compile
```

實際案例：作者提到 assemblies 找不到、版本不對齊等症狀。
實作環境：microsoft/dotnet。
實測數據：
- 改善前：編譯中斷
- 改善後：調整後能順利編譯（建議評估）
- 改善幅度：定性改善（穩定性↑）

Learning Points（學習要點）
核心知識點：
- 依賴缺失診斷流程
- 範本專案作為對照組

技能要求：
- 必備技能：diff/比對、閱讀錯誤訊息
- 進階技能：系統化除錯清單

延伸思考：
- 可建立 preflight 檢查腳本
- 風險：多變因素耦合導致排查時間拉長
- 優化：標準化專案模板

Practice Exercise（練習題）
- 基礎練習：故意移除一個依賴並觀察錯誤（30 分鐘）
- 進階練習：寫出排查清單並成功修復（2 小時）
- 專案練習：建立 preflight 腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能修復依賴缺失
- 程式碼品質（30%）：設定合理、簡潔
- 效能優化（20%）：排查效率
- 創新性（10%）：自動化檢測工具


## Case #13: 成功編譯/執行但 Console 沒有輸出（STDOUT 互動問題）
### Problem Statement（問題陳述）
**業務場景**：在容器中 compile/run 都成功，但終端沒有看到 Console.WriteLine 的輸出。
**技術挑戰**：判斷是運行時/輸出通道/互動參數問題。
**影響範圍**：降低可觀察性，難以確認程式行為。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 容器啟動未使用 -it，標準輸出/緩衝交互受影響。
2. TFM 或執行方式導致輸出管道不一致。
3. 程式碼未明確 flush（少見，但可檢查）。

**深層原因**：
- 架構層面：容器互動模式影響輸出觀察。
- 技術層面：STDOUT/TTY 的差異。
- 流程層面：未規範 run 參數。

### Solution Design（解決方案設計）
**解決策略**：以 -it 啟動容器，確保 TTY/STDIN；在容器內 run；若仍無輸出，最小化程式碼並檢查 TFM 與 CLI 輸出。必要時加上 flushed 輸出測試。

**實施步驟**：
1. 以 -it 互動模式執行
- 實作細節：docker run -it 進入 bash，再 dotnet run
- 所需資源：Docker
- 預估時間：30 分鐘

2. 最小化與檢查
- 實作細節：最小程式碼輸出、檢查 TFM
- 所需資源：編輯器
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
docker run --rm -it -v "$PWD":/work -w /work microsoft/dotnet /bin/bash
dotnet run
```

實際案例：作者提及曾遇到「執行成功但沒有 console output」的怪異問題。
實作環境：microsoft/dotnet。
實測數據：
- 改善前：輸出不可見
- 改善後：互動模式與最小化驗證後可見（建議評估）
- 改善幅度：定性改善（可觀察性↑）

Learning Points（學習要點）
核心知識點：
- Docker 互動/TTY 對輸出的影響
- 最小可重現原則

技能要求：
- 必備技能：Docker run 參數
- 進階技能：STDOUT/管道診斷

延伸思考：
- 在 CI 中如何收集標準輸出
- 風險：不同終端行為差異
- 優化：加入輸出檢查測試

Practice Exercise（練習題）
- 基礎練習：對比 -it 與非 -it 的 run 輸出（30 分鐘）
- 進階練習：撰寫最小輸出程式並驗證（2 小時）
- 專案練習：建立輸出監測腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出可穩定看見
- 程式碼品質（30%）：測試程式精簡
- 效能優化（20%）：問題定位快速
- 創新性（10%）：輸出檢查自動化


## Case #14: 第三方套件與 BCL 不支援 .NET Core 的移植規劃
### Problem Statement（問題陳述）
**業務場景**：既有程式使用大量僅支援 .NET Framework 的 BCL/第三方套件，需移植至 Linux/.NET Core。
**技術挑戰**：辨識不相容 API 與套件，尋找替代或重寫。
**影響範圍**：移植工作量大、風險高。
**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 僅支援 .NET Framework 的 API/套件在 .NET Core 不可用。
2. 跨平台差異（檔案系統、進程、UI）。
3. 套件尚未針對 RC1 發佈相容版本。

**深層原因**：
- 架構層面：.NET Core 與 .NET Framework 的設計差異。
- 技術層面：API Surface 範圍缺口。
- 流程層面：缺乏系統性的相容性審核。

### Solution Design（解決方案設計）
**解決策略**：先建立最小可運行的 Core 專案，逐步引入功能；對不相容部分進行梳理，替換為 Core 相容套件或抽象化後重寫。

**實施步驟**：
1. 建立核心骨架
- 實作細節：Console/Library 先跑通 RC1
- 所需資源：microsoft/dotnet
- 預估時間：1 天

2. 相容性審核與替換
- 實作細節：列出不相容 API/套件，尋找替代或重寫
- 所需資源：文件/社群
- 預估時間：數天至數週

**關鍵程式碼/設定**：
```markdown
Implementation Example（實作範例）
- 建立相容性清單（API、套件）
- 以 Interface 抽象外部相依，為 Core 與非 Core 提供不同實作
```

實際案例：作者指出真正門檻在 BCL 與第三方不支援 .NET Core 的改寫。
實作環境：跨平台移植情境。
實測數據：
- 改善前：無法在 Linux 執行
- 改善後：關鍵路徑可在 .NET Core 運行
- 改善幅度：定性改善（可運行性↑、技術債↓）

Learning Points（學習要點）
核心知識點：
- 相容性審核方法
- 抽象化與替換策略

技能要求：
- 必備技能：API 分析
- 進階技能：重構與替代設計

延伸思考：
- 分階段上雲/上容器
- 風險：功能退化或工期增加
- 優化：先挑無外部依賴的模塊遷移

Practice Exercise（練習題）
- 基礎練習：列出一份不相容清單（30 分鐘）
- 進階練習：替換一個不相容套件（2 小時）
- 專案練習：完成一條端到端功能的移植（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：核心功能可運行
- 程式碼品質（30%）：抽象設計合理
- 效能優化（20%）：移植成本可控
- 創新性（10%）：替代策略有創意


## Case #15: 用 --rm 避免容器殘留與環境污染（流程最佳化）
### Problem Statement（問題陳述）
**業務場景**：頻繁試驗 CLI/容器命令，容易累積大量中間容器與狀態。
**技術挑戰**：如何保持環境乾淨、降低清理由此產生的成本。
**影響範圍**：docker ps -a 混亂、硬碟佔用、操作風險增加。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 忘記清理退出容器。
2. 使用非一次性容器進行短任務。
3. 未形成操作習慣。

**深層原因**：
- 架構層面：缺乏輕量的實驗流程設計。
- 技術層面：對 --rm 認知不足。
- 流程層面：未制定清理政策。

### Solution Design（解決方案設計）
**解決策略**：對短任務一律使用 --rm；對互動任務也在退出時自動清理；搭配 volume 確保資料持久化。

**實施步驟**：
1. 一次性容器運行
- 實作細節：docker run --rm 搭配 -v/-w
- 所需資源：Docker
- 預估時間：即時

2. 清理檢查
- 實作細節：定期檢查 docker ps -a、docker system prune（慎用）
- 所需資源：CLI
- 預估時間：5 分鐘

**關鍵程式碼/設定**：
```bash
# 一次性容器執行範例
docker run --rm -v "$PWD":/myapp -w /myapp microsoft/dotnet:0.0.1-alpha dotnet compile
```

實際案例：作者示範 --rm 的使用，完成任務即刪除容器狀態。
實作環境：Docker。
實測數據：
- 改善前：殘留容器多
- 改善後：短任務無殘留
- 改善幅度：定性改善（環境整潔度↑）

Learning Points（學習要點）
核心知識點：
- --rm 的行為
- 容器狀態生命周期管理

技能要求：
- 必備技能：Docker 常用命令
- 進階技能：系統化清理策略

延伸思考：
- 搭配命名慣例便於觀察
- 風險：未掛載資料將遺失
- 優化：資料一律掛載 volume

Practice Exercise（練習題）
- 基礎練習：以 --rm 跑一次 build（30 分鐘）
- 進階練習：設計清理腳本（2 小時）
- 專案練習：制定環境治理準則（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：短任務皆採用 --rm
- 程式碼品質（30%）：清理腳本可靠
- 效能優化（20%）：環境整潔、占用可控
- 創新性（10%）：自動化治理機制


## Case #16: 只在容器內編譯，不在容器內執行（工作分離）
### Problem Statement（問題陳述）
**業務場景**：出於合規或部署策略，只允許在容器內編譯，但不允許在容器內執行應用（例如交付到既有 VM）。
**技術挑戰**：將編譯產物產出至宿主機並在其他環境運行。
**影響範圍**：若產物不可攜或缺少相依，將無法部署。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 不清楚編譯產物位置與攜帶需求。
2. 未掛載產出目錄，退出容器後產物丟失。
3. 缺乏發佈（publish）流程認知。

**深層原因**：
- 架構層面：建置與運行環境分離。
- 技術層面：產物封裝與相依收集。
- 流程層面：交付管道設計不足。

### Solution Design（解決方案設計）
**解決策略**：掛載專案目錄，於容器內完成 compile（或 publish），讓產物留在宿主機目錄；運行由目標環境負責。

**實施步驟**：
1. 掛載與編譯
- 實作細節：-v "$PWD":/myapp -w /myapp，執行 dotnet compile（或 publish）
- 所需資源：Docker
- 預估時間：1-5 分鐘

2. 驗證產物
- 實作細節：在宿主機檢查 bin/ 輸出
- 所需資源：檔案系統
- 預估時間：10 分鐘

**關鍵程式碼/設定**：
```bash
docker run --rm -v "$PWD":/myapp -w /myapp microsoft/dotnet:0.0.1-alpha dotnet compile
# 產物會出現在宿主 $PWD 下的 bin/ 對應資料夾
```

實際案例：文章的「只在容器內編譯」示例可延伸為工作分離策略。
實作環境：Docker + CLI。
實測數據：
- 改善前：需在多環境重複安裝 SDK
- 改善後：產物可攜，部署靈活
- 改善幅度：定性改善（可移植性↑）

Learning Points（學習要點）
核心知識點：
- 產物路徑與攜帶
- 建置/運行分離的 DevOps 思維

技能要求：
- 必備技能：檔案/目錄管理
- 進階技能：發佈流程設計

延伸思考：
- 後續版本 dotnet publish 更適合部署產物
- 風險：目標環境需具備對應 runtime
- 優化：在目標環境安裝相容 runtime 或採 self-contained（後續版本）

Practice Exercise（練習題）
- 基礎練習：將產物留在宿主並在另一台機器運行（30 分鐘）
- 進階練習：寫部署腳本（2 小時）
- 專案練習：設計完整建置/部署管道（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：產物可攜、可運行
- 程式碼品質（30%）：腳本與設定清晰
- 效能優化（20%）：建置/部署時間合理
- 創新性（10%）：流程自動化程度高


## Case #17: 參考資料稀少時的「官方來源優先」策略
### Problem Statement（問題陳述）
**業務場景**：RC1 初期文件稀少，Google 搜尋不到足夠解法，問題無法快速排除。
**技術挑戰**：如何在資訊不足時建立可靠的學習與驗證路徑。
**影響範圍**：排障時間拉長、信心受影響。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 新版剛釋出，社群內容不足。
2. 舊版資料與現況不符。
3. 文件/樣例分散。

**深層原因**：
- 架構層面：快速演進期。
- 技術層面：API/命令變動頻繁。
- 流程層面：未建立權威來源的追蹤清單。

### Solution Design（解決方案設計）
**解決策略**：鎖定官方 GitHub README、Getting Started 與幾位核心部落格（Hanselman、ScottGu 等），先跑通官方最小樣例，再逐步擴展。

**實施步驟**：
1. 彙整權威來源
- 實作細節：建立書籤與內部 wiki
- 所需資源：官方連結清單
- 預估時間：1 小時

2. 以官方樣例驗證
- 實作細節：直接照範例跑通後再套用到自專案
- 所需資源：容器/CLI
- 預估時間：半天

**關鍵程式碼/設定**：
```markdown
Implementation Example（實作範例）
- 優先參考：
  - .NET CLI Preview Docker Image（GitHub README）
  - .NET Core Getting Started（官方）
  - 相關官方/核心部落格公告
```

實際案例：作者列出官方 README 與多篇核心文章作為主要參考。
實作環境：—（策略性）
實測數據：
- 改善前：查無資料
- 改善後：有可靠樣例可跑
- 改善幅度：定性改善（排障效率↑）

Learning Points（學習要點）
核心知識點：
- 權威來源優先
- 樣例先行的驗證方法

技能要求：
- 必備技能：閱讀英文技術文件
- 進階技能：建立團隊知識庫

延伸思考：
- 可設定文件維護責任人
- 風險：官方文件更新導致差異
- 優化：定期檢視與更新清單

Practice Exercise（練習題）
- 基礎練習：用官方樣例跑通 HelloWorld（30 分鐘）
- 進階練習：將參考資料整理成內部頁面（2 小時）
- 專案練習：建立「遇障先驗樣例」的流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能用官方樣例通關
- 程式碼品質（30%）：文件整理清楚
- 效能優化（20%）：排障速度提升
- 創新性（10%）：建立可共享的知識版型


## Case #18: 以容器驅動的跨平台學習路徑（從 HelloWorld 到正式部署的過渡）
### Problem Statement（問題陳述）
**業務場景**：計畫由 Windows/.NET Framework 過渡到 Linux/.NET Core，需要可分階段、可回溯的學習/導入路徑。
**技術挑戰**：平衡新舊工具鏈共存、風險控制與學習曲線。
**影響範圍**：影響團隊技能升級與專案里程碑。
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 新舊環境差異大。
2. 缺少階段性目標。
3. 過於追求一次到位導致風險高。

**深層原因**：
- 架構層面：跨平台體系轉換。
- 技術層面：工具鏈與依賴重構。
- 流程層面：缺乏學習與導入藍圖。

### Solution Design（解決方案設計）
**解決策略**：以容器為學習與實作載具，從 HelloWorld（Console）開始，逐步處理相依、TFM、第三方兼容；確立 CLI 基本功，再延伸到部署。

**實施步驟**：
1. 基礎閉環
- 實作細節：Case 5/8 流程跑通
- 所需資源：microsoft/dotnet
- 預估時間：1-2 天

2. 兼容與移植
- 實作細節：Case 9/10/11/12/14 的策略
- 所需資源：依賴分析
- 預估時間：1-4 週

**關鍵程式碼/設定**：
```markdown
Implementation Example（實作範例）
- 以 container + DOTNET CLI 作為「教具」
- 每個里程碑產出腳本、文件與可重複步驟
```

實際案例：文章作者以容器為教具，逐步擴大研究範圍並回到主線驗證。
實作環境：Docker + DOTNET CLI（RC1）。
實測數據：
- 改善前：無路徑、嘗試零散
- 改善後：有分段學習與導入藍圖
- 改善幅度：定性改善（風險↓、可控性↑）

Learning Points（學習要點）
核心知識點：
- 以容器構建學習沙盒
- 分階段導入與驗證

技能要求：
- 必備技能：前述各案例之技能
- 進階技能：規劃與治理

延伸思考：
- 將學習路徑融入新人訓練
- 風險：投入時間與人力成本
- 優化：以最小可行步驟迭代

Practice Exercise（練習題）
- 基礎練習：完成 HelloWorld 閉環與文檔（30 分鐘）
- 進階練習：挑選一段老程式碼移植（2 小時）
- 專案練習：提交完整導入計畫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：達成各階段成果
- 程式碼品質（30%）：腳本化、文件化
- 效能優化（20%）：學習/導入成本可控
- 創新性（10%）：因地制宜的改良


--------------------------------
案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case 1, 2, 3, 4, 5, 6, 8, 15
- 中級（需要一定基礎）
  - Case 7, 9, 10, 11, 12, 16, 18
- 高級（需要深厚經驗）
  - Case 14

2. 按技術領域分類
- 架構設計類
  - Case 14, 18
- 效能優化類
  - Case 6, 7, 15, 16
- 整合開發類
  - Case 1, 2, 3, 4, 5, 8, 9, 10, 11, 12
- 除錯診斷類
  - Case 7, 11, 12, 13
- 安全防護類
  - （本文未涉及安全控制細節，暫無）

3. 按學習目標分類
- 概念理解型
  - Case 3, 4, 6, 17
- 技能練習型
  - Case 1, 2, 5, 8, 15, 16
- 問題解決型
  - Case 7, 9, 10, 11, 12, 13
- 創新應用型
  - Case 14, 18

--------------------------------
案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 3（選擇映像、認識工具鏈）
  - Case 4（命令對應）
  - Case 5（dotnet init 起手）
  - Case 1/2（容器化工作流、一次性與互動模式）
  - Case 6（restore 認知）
  - Case 8（端到端閉環）
- 依賴關係：
  - Case 9、10、11、12（移轉與相容性）依賴 Case 3/4/5/6/8 的基礎
  - Case 13（輸出診斷）依賴 Case 2/8 的運行技能
  - Case 14（BCL/第三方移植）依賴 Case 9/10/11/12 的相容性處理能力
  - Case 16（工作分離）依賴 Case 1/5/8
  - Case 18（導入藍圖）綜合以上所有能力
- 完整學習路徑建議：
  1) 基礎認知：Case 3 → Case 4 → Case 5  
  2) 容器工作流：Case 1 → Case 2 → Case 6 → Case 8  
  3) 移轉與相容：Case 9 → Case 10 → Case 11 → Case 12 → Case 13  
  4) 進階與落地：Case 16 → Case 14 → Case 18  
  如此路徑由易到難、由點到面，能在 RC1 工具與容器環境下建立可復現的開發與移植能力。