---
layout: synthesis
title: "[.NET Core] Running .NET Core RC1 on Docker - DOTNET CLI"
synthesis_type: summary
source_post: /2015/12/06/net-core-running-net-core-rc1-on-docker/
redirect_from:
  - /2015/12/06/net-core-running-net-core-rc1-on-docker/summary/
postid: 2015-12-06-net-core-running-net-core-rc1-on-docker
---

# [.NET Core] Running .NET Core RC1 on Docker - DOTNET CLI

## 摘要提示
- .NET Core RC1「Go Live」: 微軟宣布 .NET Core/ASP.NET 5 RC1，支援 Windows/OS X/Linux，允許上正式環境並提供支援。
- Docker 官方映像: 推出 microsoft/aspnet 與 microsoft/dotnet 兩種映像，分別對應舊 DNX 工具鏈與新 DOTNET CLI。
- DOTNET CLI 整合: 新 CLI 將 DNVM/DNX/DNU 統整為 dotnet 指令，命名清晰並新增原生編譯等能力。
- 容器用法轉變: 以「一次性容器」與掛載 Volume 方式在容器內編譯、在主機上執行，提升開發迭代效率。
- 關鍵 Docker 參數: 使用 --rm 自動清理、-v 掛載目錄、-w 設定工作目錄，將容器當成工具箱使用。
- 基本開發流程: 透過 dotnet init/restore/compile/run 從零建立並執行 Console「Hello World」。
- 相依套件管理: dotnet restore 從 NuGet 下載大量相依，替代舊 dnu restore 流程。
- 原生編譯選項: dotnet compile 已支援將程式碼編譯為原生機器碼（Native），為 RC 階段新能力之一。
- 跨平台移植挑戰: BCL 差異與第三方套件尚未支援 .NET Core 是移植痛點，非僅「能在 Linux 跑」的問題。
- 實作經驗與問題: RC 與 Beta 差異導致 runtime/相依版本/輸出行為等問題，需統一升級至 RC1 環境驗證。

## 全文重點
文章回顧 Microsoft Connect 2015 宣布的 .NET Core/ASP.NET 5 RC1 重點：版本進入可正式上線的「Go Live」階段，跨平台支援完整。作者說明自己研究 .NET Core 的核心目標在於理解跨平台轉移與企業導入效益，而非僅在 Linux 執行。此次 RC1 除了於 Docker Hub 更新映像，也帶來新命令列工具 DOTNET CLI，統整了 Beta 時期分散的 DNVM/DNX/DNU，命名清楚、組織更佳，並新增原生編譯等機制。微軟同時提供兩種容器映像：microsoft/aspnet 沿用 DNX 工具鏈但版本提升至 RC1；microsoft/dotnet 則內建新 CLI（0.0.1-alpha preview）。

作者主張開發時不必把容器當 VM 用，可將其退化為單一工具執行單元：以 --rm 建立一次性容器、用 -v 掛載主機目錄、-w 設定工作目錄，於容器內完成編譯或還原相依，再立即銷毀容器，讓主機直接拿到產物。相較於每次進出容器執行單一命令，作者偏好先啟動 shell 一次性完成多步驟，結束 shell 時再自動清理容器。

實作部分以「Hello World」示範完整流程：先 docker pull microsoft/dotnet，docker run 啟動 bash；透過 dotnet -h 檢視命令，再以 dotnet init 產生 Program.cs 與 project.json；接著 dotnet restore 從 NuGet 下載相依套件；使用 dotnet compile 進行編譯（雖有版本警告但可略過）；最後 dotnet run 成功輸出「Hello World!」。此流程展現 RC1 時期 CLI 的核心開發體驗與命令整合程度。

作者也分享實務挑戰：將 Windows 10/VS2015（ASP.NET 5 beta8）建立的專案直接搬到 microsoft/dotnet 容器時，遭遇目標 Runtime 不符（預設跑到 .NET Framework 4.6.1 而非 Core）、相依組件/NuGet 版本找不到、甚至執行成功但 Console 無輸出等怪異行為。研判主因是 Beta 與 RC1 的破壞性差異，建議統一升級到 RC1 再驗證。最後預告系列將持續從跨平台與 Runtime 差異（效能、記憶體管理）等面向深入，並評估企業導入 .NET Core + Linux 的整體效益。

## 段落重點
### Announcing .NET Core and ASP.NET 5 RC1
- 內容摘要: 微軟宣布 .NET Core 與 ASP.NET 5 RC1，支援 Windows、OS X、Linux，屬「Go Live」等級，可上線並獲官方支援。作者點出 RC（功能凍結、品質達標）的重要時間點，適合觀望者入門。文章定位不做傳統安裝教學，而專注研究心得與官方文件未及的資訊，包含跨平台價值、.NET Core 架構改進、對企業導入 Linux 的效益。並規劃系列主題：1) DOTNET CLI 與 DNX 工具鏈的關係；2) CLI 搭配 Docker 的技巧；3) 實作 Hello World；4) Windows/Linux Runtime 差異（效能）；5) Runtime 差異（記憶體管理）；6) 待定。此段為全篇背景與系列藍圖，為後續實作鋪陳。

### 新玩意: DOTNET CLI, 整合 DNVM / DNX / DNU 的命令列工具
- 內容摘要: RC1 帶來新 CLI，把原本分別負責 Runtime 管理（DNVM）、執行（DNX）、套件維護（DNU）的工具統整至單一 dotnet 指令，命名直觀、結構清晰，且加入先前沒有的能力如原生編譯。因 CLI 僅 0.0.1-alpha，微軟同時提供兩個 Docker 映像：microsoft/aspnet（延用 DNX 工具鏈、版本升至 RC1、用法延續先前文章）與 microsoft/dotnet（內含新 CLI），方便使用者在過渡期並行採用，降低破壞性更新帶來的摩擦。

### DOTNET CLI Container 的使用技巧
- 內容摘要: 作者先列官方 GitHub README 與快速入門等關鍵參考。核心觀念是「把容器當工具箱」：不必把應用長駐容器內運行，可在容器內完成編譯動作即可。示例命令以 docker run --rm -v "$PWD":/myapp -w /myapp microsoft/dotnet:0.0.1-alpha dotnet compile 展示一次性容器模式：掛載主機目錄至容器、設定工作目錄、執行編譯，結束即自動清理容器。作者依開發需求調整為啟動 /bin/bash，進入後一口氣完成多步驟，離開 shell 再刪除容器，兼顧靈活性與整潔。
- 實作流程：1) docker pull microsoft/dotnet 抓映像；2) docker run --name dotnet --rm -ti microsoft/dotnet /bin/bash 進入容器；3) dotnet -h 檢視可用命令（實際可用不止畫面列出的 compile/publish/run）；4) dotnet init 產生 Program.cs 與 project.json；5) dotnet restore 還原相依（首次會下載眾多套件）；6) dotnet compile 編譯（可見支援原生編譯選項，過程可能出現相依版本警告）；7) dotnet run 執行並輸出「Hello World!」。此法亦可用 -v 掛載既有程式碼資料夾，容器負責工具鏈，主機保留程式與產物。
- 問題與經驗：從 VS2015（ASP.NET 5 beta8）專案直接移至 microsoft/dotnet 容器時，遇到目標 Runtime 不相容（誤用 .NET Framework 4.6.1）、相依組件解析失敗、NuGet 版本不匹配、甚至執行有結果但 Console 無輸出等狀況。作者推測源於 Beta 與 RC1 的差異與斷層，建議全面升級到 RC1 統一驗證。並強調真正的移植門檻在於 BCL 與第三方套件對 .NET Core 的支援度，而非僅操作流程。後續將持續以效能、記憶體管理等面向剖析 Windows/Linux Runtime 差異與企業導入效益。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 .NET/C# 與 NuGet 套件管理概念
   - Linux 基本指令與 Shell 操作
   - Docker 基本概念（image、container、volume、旗標如 -v、--rm）
   - .NET Core 與 ASP.NET 5（當時名）版本脈絡：Beta → RC1 → RTM

2. 核心概念：
   - .NET Core RC1 可用於生產（Go Live）且跨平台（Windows/OS X/Linux）
   - DOTNET CLI 統一 DNVM/DNX/DNU 的新命令列工具（dotnet init/restore/compile/run/publish）
   - Docker 官方映像：microsoft/aspnet（沿用 DNX 工具鏈）與 microsoft/dotnet（DOTNET CLI alpha）
   - 容器用法模式：一次性可拋棄容器（--rm）與開發互動式 Shell 進入（/bin/bash）
   - 開發工作流：專案初始化 → 還原依賴 → 編譯（含原生編譯選項）→ 執行

3. 技術依賴：
   - DOTNET CLI 依賴 .NET Core runtime 與 NuGet 套件來源
   - 開發/編譯在容器中運行需正確掛載程式碼目錄（-v）與工作目錄（-w）
   - microsoft/dotnet 映像內建 CLI；microsoft/aspnet 映像內建 DNX 工具鏈
   - 版本相依與相容性：Beta 8 專案移轉至 RC1 可能面臨 runtime/assembly/nuget 版本差異

4. 應用場景：
   - 在 Linux/Docker 上快速體驗與開發 .NET Core
   - CI/CD 中以容器完成還原、編譯、測試、發布（可用一次性容器）
   - 跨平台驗證與效能/記憶體管理測試
   - 企業導入 .NET Core + Linux 的移轉與部署

### 學習路徑建議
1. 入門者路徑：
   - 安裝 Docker → docker pull microsoft/dotnet
   - 使用 docker run -it 進入容器 Shell
   - 使用 dotnet init/restore/compile/run 完成 Hello World
   - 嘗試 --rm 與 -v 綁定本機目錄，理解可拋棄容器與檔案共用

2. 進階者路徑：
   - 比較 microsoft/aspnet 與 microsoft/dotnet 映像與工具鏈差異
   - 熟悉 dotnet publish、原生編譯選項與發布產物結構
   - 研究 RC1 與 Beta 的相容性議題（runtime、BCL、NuGet 版本）
   - 建立自訂 Dockerfile，分層優化 restore/compile 的快取

3. 實戰路徑：
   - 以綁定 Volume 的方式在容器內完成還原/編譯，產物保留於本機
   - 串接 CI（例如 GitHub Actions/GitLab CI）用一次性容器執行 dotnet restore/build/test/publish
   - 針對現有 .NET 專案進行 .NET Core 移轉評估：BCL 替代、第三方套件支援、組態與日誌
   - 進行效能（Compute Pi）與記憶體碎片測試，蒐集跨平台差異資料

### 關鍵要點清單
- .NET Core RC1（Go Live）: RC1 支援上線部署並可獲得微軟支援，適合開始導入評估 (優先級: 高)
- DOTNET CLI 整合: 新的 dotnet 單一入口整合了 DNVM/DNX/DNU 的任務與工作流 (優先級: 高)
- 主要 CLI 指令: init/restore/compile/run/publish 構成開發到發布的完整鏈 (優先級: 高)
- 官方 Docker 映像選擇: microsoft/aspnet（DNX）與 microsoft/dotnet（DOTNET CLI alpha）用途不同 (優先級: 高)
- 一次性容器 --rm: 使用 --rm 執行一次性編譯/測試可保持環境乾淨 (優先級: 中)
- Volume 綁定 -v: 用 -v 將本機目錄掛入容器以保存編譯產物與共用原始碼 (優先級: 高)
- 工作目錄 -w: 設定 -w /myapp 確保 CLI 在正確專案目錄運行 (優先級: 中)
- RC1 依賴還原: dotnet restore 會拉取大量相依套件，需配置正確的 NuGet 源 (優先級: 中)
- 編譯與原生輸出: dotnet compile 支援產出 IL 與（預覽的）原生機器碼選項 (優先級: 中)
- 版本相容性風險: Beta 8 → RC1 可能出現 runtime/assembly/nuget 版本衝突與執行異常 (優先級: 高)
- BCL 與第三方限制: 僅支援 .NET Core 的 API 與套件可跨平台，需替代不相容功能 (優先級: 高)
- 容器互動式開發: 以 /bin/bash 進入容器反覆 restore/build/run，提升迭代效率 (優先級: 中)
- 發布與部署: 透過 dotnet publish 搭配 Dockerfile 可實作可重現的部署流程 (優先級: 高)
- 企業導入效益: .NET Core + Linux 可整合既有基礎設施（nginx、MySQL、容器編排）降低成本 (優先級: 中)
- 故障排除能力: 早期文件稀少，需依經驗排查（例如 console 輸出異常、套件版本不符）(優先級: 中)