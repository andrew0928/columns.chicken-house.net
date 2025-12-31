---
layout: synthesis
title: "[.NET Core] Running .NET Core RC1 on Docker - DOTNET CLI"
synthesis_type: faq
source_post: /2015/12/06/net-core-running-net-core-rc1-on-docker/
redirect_from:
  - /2015/12/06/net-core-running-net-core-rc1-on-docker/faq/
postid: 2015-12-06-net-core-running-net-core-rc1-on-docker
---

# [.NET Core] Running .NET Core RC1 on Docker - DOTNET CLI

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 .NET Core RC1？
- A簡: .NET Core 的候選發布版，功能凍結且標註 Go Live，支援 Windows、OS X、Linux，可用於正式環境。
- A詳: .NET Core RC1 是跨平台 .NET 的 Release Candidate（候選發布版本），代表功能已完成（Feature Freeze），並達到可投入生產環境的穩定度。官方宣告 RC1 為 Go Live，遇到問題可向 Microsoft 支援求助。本次 RC1 同步支援 Windows、OS X 與 Linux，並伴隨 Docker 映像與新命令列工具 DOTNET CLI，方便開發者快速建立、還原相依、編譯與執行 .NET Core 應用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q4, B-Q11

A-Q2: RC、Beta、RTM 有何差異？
- A簡: Beta 功能仍可能變動；RC 功能凍結、近最終；RTM 為正式釋出，可大規模部署。
- A詳: Beta（測試版）仍持續加入功能與修正，API 與工具可能變動；RC（候選發布版）功能凍結（Feature Freeze），進入穩定化，若無重大問題將進入 RTM；RTM（Release to Manufacturing）為正式版，可大規模生產部署。RC 若標註 Go Live，即允許將應用部署到正式環境並獲得支援。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q5

A-Q3: 什麼是 ASP.NET 5 RC1？
- A簡: ASP.NET 在 RC1 階段，同步支援跨平台，屬 Go Live，可用於生產佈署。
- A詳: ASP.NET 5 RC1 與 .NET Core RC1 同步發布，標註 Go Live，意指可在正式環境使用並獲得官方支援。它建立在 .NET Core 之上（亦可在 .NET Framework 上），可於 Windows、OS X 與 Linux 執行。RC1 的目標是提供近似最終版的體驗，讓團隊提前規畫部署與相依更新。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q4, B-Q11

A-Q4: 「Go Live」在 RC1 代表什麼？
- A簡: 表示可將應用部署到生產，若遇問題可向 Microsoft 支援尋求協助。
- A詳: Go Live 是官方對品質的背書，允許在 RC 階段就進行正式環境部署。對企業意義在於，可及早享受新版本的功能與效益，並將風險控制在受支援範圍內。雖非 RTM，但因功能凍結與穩定度提升，搭配支援通道，足以承擔生產使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2

A-Q5: 什麼是 Feature Freeze（FF）？
- A簡: 功能凍結，停止加入新功能，專注修正與穩定，為 RC 的關鍵特徵。
- A詳: Feature Freeze 指產品進入穩定化階段，不再增加新功能，改以修正缺陷、提升相容性與文件完善度為主。對開發者而言，API 與工具變動降低，適合進行相依更新與遷移驗證。FF 是 RC 階段的重要標誌，降低導入風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q1

A-Q6: 什麼是 DOTNET CLI？
- A簡: .NET Core 的命令列工具，整合建置、還原、執行與發佈，取代 DNVM/DNX/DNU 分散工具。
- A詳: DOTNET CLI 是 .NET Core 的統一命令列介面，以單一 dotnet 指令提供 init、restore、compile、run、publish 等工作流程。相較 Beta 時期的 DNVM（管理）、DNX（執行）、DNU（維護），CLI 命名清晰、流程一致，並隨 Docker 映像釋出，便於跨平台與容器化開發。RC1 時期 CLI 處於早期預覽（0.0.1-alpha）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q1, B-Q14

A-Q7: DOTNET CLI 與 DNVM/DNX/DNU 的差異？
- A簡: CLI 將原三套工具整合成一個 dotnet 指令，命名直觀、流程一致，並新增能力。
- A詳: Beta 時期需分別使用 DNVM（Runtime 管理）、DNX（執行）、DNU（相依維護）。CLI 將常用工作整合於 dotnet 命令下，降低學習曲線並避免命令混淆。除 restore、compile、run，也增添可編譯為原生碼等能力。CLI 的 Docker 映像（microsoft/dotnet）隨 RC1 提供，利於標準化環境。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q11, B-Q9

A-Q8: 為什麼需要 DOTNET CLI？
- A簡: 提供跨平台一致的開發體驗，簡化建置流程，利於自動化與容器化。
- A詳: CLI 讓 Windows、OS X、Linux 皆可用一致命令完成還原、編譯與執行，減少工具差異帶來的摩擦。命令語意直觀，便於腳本化與 CI/CD，搭配 Docker 映像可快速建立一次性或可重現的建置環境，對團隊協作與部署極具價值。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q10

A-Q9: Docker 在本情境扮演什麼角色？
- A簡: 提供可重現、輕量的 .NET Core 開發與建置環境，支援一次性容器使用。
- A詳: Docker 將 .NET Core 工具與相依打包成映像，團隊可用相同環境進行還原、編譯與執行。透過 --rm 產生一次性容器，-v 掛載原始碼資料夾，-w 設定工作目錄，即可在容器內編譯主機檔案，避免汙染主機並確保結果一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q6, B-Q7

A-Q10: 什麼是 microsoft/aspnet 映像？
- A簡: 基於 DNX 工具鏈的 ASP.NET 映像，RC1 時期仍提供，適合舊流程或相容需求。
- A詳: microsoft/aspnet 是使用 DNVM/DNX/DNU 的映像，RC1 已升級相依，但保留 Beta 時期工具流程。若既有專案仍依賴 DNX 或尚未遷移 CLI，可使用此映像延續開發或部署。不過新專案建議採用 CLI 導向映像（microsoft/dotnet）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q9

A-Q11: 什麼是 microsoft/dotnet 映像？
- A簡: 內含 DOTNET CLI 的 .NET Core 映像，支援 init/restore/compile/run 等命令。
- A詳: microsoft/dotnet 是 CLI 導向映像，內含 dotnet 工具（0.0.1-alpha 預覽）與必要相依。適合以容器進行專案初始化、還原套件、編譯與執行，甚至可僅用來編譯而在主機或其他環境執行，達成「容器建置、任意執行」模式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q10

A-Q12: 什麼是一次性（可拋棄）容器？
- A簡: 用 --rm 啟動的容器，工作完成即自動刪除狀態，適合建置或測試任務。
- A詳: 一次性容器以 docker run --rm 建立，指令完成後自動清除，可避免長期堆積暫存狀態。常見用法是以 -v 掛載原始碼，-w 設定目錄，在容器內執行 dotnet restore/compile，結束即還原乾淨環境，利於重現與隔離。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q10

A-Q13: Docker 的 -v、-w、--rm 代表什麼？
- A簡: -v 掛載資料夾，-w 設定工作目錄，--rm 任務結束自動刪除容器。
- A詳: -v host:container 使主機目錄映射到容器，便於容器讀寫主機檔案；-w 指定容器內工作目錄，讓命令以該目錄為基準；--rm 讓容器在命令結束後自動清除狀態，避免佔用資源並保持環境整潔，是一次性建置的關鍵選項。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q6, B-Q7

A-Q14: dotnet init/restore/compile/run 是什麼？
- A簡: init 建立骨架；restore 還原套件；compile 編譯；run 直接編譯並執行。
- A詳: init 產生基本專案（如 Program.cs、project.json）；restore 透過 NuGet 還原相依；compile 將原始碼編譯為輸出（亦可選擇原生編譯預覽）；run 會在需要時先編譯再執行。此四步構成最小可行開發循環，適合容器化工作流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q3, B-Q4, B-Q5

A-Q15: 什麼是「編譯為原生機器碼」？
- A簡: 將程式預先編成平台機器碼，縮短啟動時間與部署體積，RC1 為預覽能力。
- A詳: 除 IL（中介語言）外，CLI 提供將應用編譯成目標平台機器碼的選項（預覽）。原生編譯可改善啟動延遲、降低部署對執行時的依賴，但需留意平台綁定、大小與除錯差異。RC1 強調此功能仍在演進中，適合實驗與評估。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q15

A-Q16: 為何 .NET Core 跨平台有價值？
- A簡: 可用同一技術堆疊覆蓋多平台，結合 Linux 生態與容器優勢，降低成本。
- A詳: 跨平台讓團隊在 Windows、OS X、Linux 共用語言、庫與工具，擴大人才與套件生態。部署上可利用 Linux 與 Docker 的成熟優勢，提升彈性與效能/成本比。對原使用 Microsoft 解決方案的企業，有助於雲原生轉型與大規模佈署。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q20, B-Q11

A-Q17: Windows 與 Linux 執行 .NET Core 的差異（高層）？
- A簡: 介面與工具一致，但執行時、檔案系統與周邊生態不同，需測試與調整。
- A詳: CLI 與語言在各平台一致，但實際執行涉及系統 API、檔案系統大小寫、路徑分隔、網路與權限模型差異。部分 BCL 僅在 Windows/.NET Framework 提供，移植至 .NET Core/Linux 時需替換或重構。跨平台時需加強自動化測試與相依審視。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, D-Q5

A-Q18: NuGet 在流程中的角色是什麼？
- A簡: 套件管理與相依解析來源，restore 會從 NuGet 下載並快取相依。
- A詳: dotnet restore 使用 NuGet 設定與來源（如 nuget.org）解析 project.json 的相依圖，下載對應版本與遞迴相依，並快取以加速後續建置。相依版本衝突或來源設定錯誤會導致還原失敗，是建置穩定度的關鍵環節。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q3

A-Q19: 為何 RC1 是投入 .NET Core 的好時機？
- A簡: 功能穩定、Go Live 可生產，工具與映像齊備，利於評估與漸進導入。
- A詳: RC1 功能凍結與 Go Live 支援，風險可控；CLI 與 Docker 映像同步提供，降低環境建置成本。此時投入可提早識別相依差異與移植風險，為 RTM 前完成調整，縮短正式版落地時間。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q4, A-Q6

A-Q20: 容器與 VM 在本情境中的差異？
- A簡: 容器更輕量且粒度細，可作為單一應用執行或一次性建置環境，VM 較重。
- A詳: VM 提供完整 OS 隔離，啟動與資源成本較高；容器共享宿主核心，啟動快、資源小，能以「單一應用」方式運作。本文示範以容器僅承擔還原/編譯的工作，再把產物回到主機使用，突顯容器在開發/建置的敏捷性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q12, B-Q10

---

### Q&A 類別 B: 技術原理類

B-Q1: DOTNET CLI 如何運作？
- A簡: 以 dotnet 單一進入點呼叫子命令，讀取專案設定，串接還原、編譯、執行流程。
- A詳: 技術原理說明：CLI 提供單一可執行檔 dotnet，依子命令（init/restore/compile/run/publish）分派行為，解析專案（project.json）相依與目標框架，再呼叫對應組件執行。關鍵步驟或流程：解析命令→載入設定→相依解析（NuGet）→編譯（Roslyn/工具鏈）→執行。核心組件介紹：命令分派器、NuGet 相依解析、編譯器與執行時（.NET Core Runtime）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, A-Q14

B-Q2: dotnet init 的執行流程為何？
- A簡: 在目前資料夾建立最小專案骨架，含 Program.cs 與 project.json。
- A詳: 技術原理說明：init 以樣板產生最小可編譯專案。關鍵步驟或流程：檢查目錄→產生 Program.cs（預設 Hello World）→建立 project.json（含相依與框架）→輸出提示。核心組件介紹：樣板檔、檔案系統 API、CLI 模板邏輯。其目的是快速啟動專案，使後續 restore/compile/run 接續工作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q4

B-Q3: dotnet restore 背後的機制是什麼？
- A簡: 解析 project.json，相依圖經 NuGet 下載與快取，供編譯與執行使用。
- A詳: 技術原理說明：restore 讀取 project.json 的 dependencies 與 frameworks，與 NuGet 來源溝通取得相依套件與版本。關鍵步驟或流程：解析相依→版本解析與去衝突→下載套件→本機快取。核心組件介紹：NuGet 客戶端、來源伺服、快取機制。失敗多因版本不相容或來源設定錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q3

B-Q4: dotnet compile 的原理與輸出？
- A簡: 以相依為輸入，將程式碼編為輸出；可產生 IL，並提供原生編譯預覽。
- A詳: 技術原理說明：compile 呼叫編譯器，基於還原後的相依，產生組件與符號。關鍵步驟或流程：載入相依→語法編譯→連結目標框架→輸出工件（bin）。核心組件介紹：編譯器、框架引用、輸出版型。若出現版本衝突警告，多由相依樹不同版本導致，需調整相依或鎖定版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q4

B-Q5: dotnet run 的執行流程？
- A簡: 如需則先編譯，再依目標框架啟動執行，輸出標準輸出。
- A詳: 技術原理說明：run 會檢查輸出是否最新，必要時先 compile；然後定位入口點並以對應 runtime 啟動。關鍵步驟或流程：檢查變更→編譯→載入 runtime→執行主程式→輸出 IO。核心組件介紹：命令執行器、執行時、主機器（Console）。若框架目標設定不符，可能造成無法啟動或輸出異常。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q6

B-Q6: 在容器內掛載主機目錄如何運作（-v、-w）？
- A簡: -v 對映主機路徑至容器，-w 設定容器工作目錄，讓命令在該路徑操作主機檔案。
- A詳: 技術原理說明：Docker 以 bind mount 將主機檔案系統節點映射至容器命名空間。關鍵步驟或流程：解析 -v 引數→建立掛載→切換 -w 目錄→執行命令。核心組件介紹：Docker 引擎、檔案系統掛載、命名空間。此機制讓容器可編譯主機來源檔，不需將程式碼打包進映像。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q3

B-Q7: --rm 一次性容器的生命週期機制？
- A簡: 容器退出即清理檔案系統層與元資料，避免堆積臨時狀態。
- A詳: 技術原理說明：Docker 將容器層視為可寫層；指定 --rm 時，進程結束便移除容器紀錄與可寫層。關鍵步驟或流程：建立容器→執行命令→進程退出→清理容器層。核心組件介紹：容器可寫層、映像層、垃圾回收。適合建置、測試等短命任務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q10

B-Q8: -it 與 /bin/bash 的作用？
- A簡: -i 保持 STDIN，-t 配置 tty，/bin/bash 啟動互動 shell 以便反覆執行命令。
- A詳: 技術原理說明：-i 讓容器保持標準輸入開啟，-t 分配虛擬終端；/bin/bash 啟動 shell。關鍵步驟或流程：分配 tty→建立互動會話→執行命令→退出回收。核心組件介紹：TTY 子系統、Shell、標準 IO。開發時利於在容器內多次執行 dotnet 命令。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q7

B-Q9: microsoft/aspnet 與 microsoft/dotnet 架構差異？
- A簡: 前者 DNX 工具鏈、相容舊流程；後者 CLI 工具鏈，對應新命令與工作流。
- A詳: 技術原理說明：aspnet 映像預裝 DNVM/DNX/DNU 與對應 runtime；dotnet 映像預裝 CLI。關鍵步驟或流程：依映像內工具選擇 restore/build/run 命令與路徑。核心組件介紹：DNX 工具鏈 vs DOTNET CLI、對應 runtime 與相依。選擇取決於專案工具鏈與遷移狀態。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11

B-Q10: 「在容器編譯、不在容器執行」的模式如何設計？
- A簡: 以 --rm 與 -v 掛載來源進容器內 compile，輸出留在主機，執行在主機或他處。
- A詳: 技術原理說明：容器只負責建置，檔案透過 bind mount 留在主機。關鍵步驟或流程：docker run --rm -v $PWD:/app -w /app microsoft/dotnet dotnet compile。核心組件介紹：一次性容器、掛載、CLI。優點是環境可重現、主機潔淨；執行可在不同節點進行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q12, C-Q3

B-Q11: RC1 如何支援跨平台？
- A簡: 官方提供對 Windows/OS X/Linux 的 runtime 與工具，CLI 命令一致，容器加速落地。
- A詳: 技術原理說明：.NET Core 將 runtime 與 BCL 以跨平台實作提供，CLI 與 NuGet 為共通工具層。關鍵步驟或流程：相依解析→針對目標框架編譯→使用對應 runtime 執行。核心組件介紹：.NET Core Runtime、BCL、CLI、Docker 映像。此組合降低平台差異對開發鏈的影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q16

B-Q12: 「Go Live」支援模式的技術意涵？
- A簡: 表示品質到位、回報通道開放、支援流程就緒，可承載生產級問題。
- A詳: 技術原理說明：Go Live 需要穩定的安裝包、相依鏈與工具；並提供支援與修補節奏。關鍵步驟或流程：問題回報→支援協作→修補釋出。核心組件介紹：支援系統、版本管控、回饋機制。對技術團隊是導入風險控制與升級策略可行的訊號。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q19

B-Q13: project.json 在 RC1 的角色？
- A簡: 定義相依與目標框架，驅動 restore/compile/run 全流程行為。
- A詳: 技術原理說明：project.json 描述 dependencies 與 frameworks，影響相依解析與執行時選擇。關鍵步驟或流程：CLI 讀取→解析相依→決定目標框架→驅動編譯與執行。核心組件介紹：JSON 解析、NuGet 相容規則、框架 TFM。設置不當會導致還原或執行錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q5

B-Q14: 為何 dotnet -h 只顯示部分命令？
- A簡: 早期預覽版尚未完整展示，仍可使用 init/restore 等命令，屬工具演進階段現象。
- A詳: 技術原理說明：CLI 於 0.0.1-alpha 時命令呈現尚不一致，help 清單未覆蓋所有可用子命令。關鍵步驟或流程：查閱讀我檔與範例確認命令集。核心組件介紹：CLI 命令解析與說明系統。此屬早期版本常態，後續會趨於一致。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, C-Q4

B-Q15: 原生編譯（Native）在 CLI 中的工作原理（預覽）？
- A簡: 以工具鏈將 IL 預先轉為目標平台機器碼，縮短啟動，換取平台鎖定。
- A詳: 技術原理說明：在編譯階段透過原生工具鏈將 IL AOT 成機器碼。關鍵步驟或流程：分析相依→靜態連結→產出平台特定二進位。核心組件介紹：AOT 編譯器、平台鏈結器。優勢是啟動快；代價是平台專屬與除錯差異，RC1 僅供試驗。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15

B-Q16: .NET Framework 與 .NET Core 的 BCL 差異如何影響移植？
- A簡: .NET Core 僅提供子集合與新 API，部分僅 Windows API 需替換或重構。
- A詳: 技術原理說明：BCL 範圍不同導致 API 缺失或行為差異。關鍵步驟或流程：盤點相依→辨識不支援 API→以跨平台替代或抽象→重構測試。核心組件介紹：BCL、相容性填充（如相容封裝）、第三方套件支援度。移植痛點在 UI、特定系統 API 與 Windows 專屬功能。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q17, D-Q5

B-Q17: 容器中的 Console 輸出如何傳遞到主機？
- A簡: 透過標準輸出/錯誤串流映射到 Docker 日誌與終端；TTY/互動選項會影響行為。
- A詳: 技術原理說明：容器進程的 STDOUT/STDERR 由 Docker 擷取並輸出至客戶端或日誌。關鍵步驟或流程：建立進程→串流接管→終端顯示。核心組件介紹：Docker 日誌、TTY、標準 IO。若未分配 TTY 或應用緩衝策略不同，可能出現「編譯成功、執行成功但畫面無輸出」的觀感差異。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q6, B-Q8

B-Q18: 版本衝突警告的成因與原理？
- A簡: 相依樹含多版本組件，解析時選擇近期版本，導致警告，需調整鎖定。
- A詳: 技術原理說明：相依解析遇多版本候選，NuGet 依規則選擇一版，其他成為衝突來源。關鍵步驟或流程：建構相依圖→版本挑選→輸出警告。核心組件介紹：NuGet 解析器、版本範圍與浮動。解法在於統一版本、鎖檔或直接引用正確版本以壓制衝突。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q4, B-Q3

B-Q19: 以掛載方式迭代開發 vs 把程式碼打包入映像的權衡？
- A簡: 掛載利於熱迭代與一次性建置；打包利於部署一致與不可變運行。
- A詳: 技術原理說明：掛載模式將開發循環留在主機，容器供建置工具；打包模式將程式與相依固定於映像。關鍵步驟或流程：掛載→編譯→清理 vs 建立 Dockerfile→build→run。核心組件介紹：bind mount、映像層。選擇取決於開發/部署場景。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q9

B-Q20: 為何 RC1 工具可能行為不一致？
- A簡: 早期預覽版仍在快速演進，命令、help 與範例可能不同步。
- A詳: 技術原理說明：工具在 alpha/RC 階段變動頻仍，說明資料、映像與命令列參數更新節奏不同。關鍵步驟或流程：比對 README、官方部落格、映像標籤。核心組件介紹：CLI、Docker 映像、文件。遇異常時應回到官方來源核對版本與指令用法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, D-Q2

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何取得 DOTNET CLI 的 Docker 映像？
- A簡: 使用 docker pull microsoft/dotnet 拉取 CLI 映像，作為建置與執行環境。
- A詳: 具體實作步驟：在主機執行 sudo docker pull microsoft/dotnet。關鍵程式碼片段或設定：
  docker pull microsoft/dotnet
  注意事項與最佳實踐：確認網路可達與儲存空間；使用特定標籤可控版本一致性；團隊應鎖定映像版本避免漂移。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q1

C-Q2: 如何啟動互動式容器以便開發測試？
- A簡: 以 --name、--rm、-it 啟動並進入 /bin/bash，結束即清除容器狀態。
- A詳: 具體實作步驟：執行
  sudo docker run --name dotnet --rm -t -i microsoft/dotnet /bin/bash
  關鍵程式碼片段或設定：-t -i 分配 TTY 與互動；--rm 一次性；/bin/bash 啟動 shell。注意事項與最佳實踐：完成後 exit 以清除容器；避免同名容器衝突；必要時以 -v 掛載程式碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, A-Q12

C-Q3: 如何只在容器內編譯當前目錄專案？
- A簡: 掛載當前資料夾為 /myapp，設定工作目錄，執行 dotnet compile。
- A詳: 具體實作步驟：在專案根目錄執行
  docker run --rm -v "$PWD":/myapp -w /myapp microsoft/dotnet dotnet compile
  關鍵程式碼片段或設定：-v "$PWD":/myapp、-w /myapp。注意事項與最佳實踐：確保 project.json 存在；先執行 dotnet restore；以 --rm 保持環境潔淨。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q10

C-Q4: 如何用 dotnet init 建立 Hello World 專案？
- A簡: 新建資料夾，進入後執行 dotnet init，即生成 Program.cs 與 project.json。
- A詳: 具體實作步驟：
  mkdir HelloWorld && cd HelloWorld
  dotnet init
  關鍵程式碼片段或設定：Program.cs（預設輸出 "Hello World!"）、project.json（相依與框架）。注意事項與最佳實踐：若搭配 IDE 可略過 init；請在空目錄執行避免覆蓋檔案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q14

C-Q5: 如何還原相依套件（restore）？
- A簡: 在專案根目錄執行 dotnet restore，從 NuGet 下載相依並快取。
- A詳: 具體實作步驟：
  dotnet restore
  關鍵程式碼片段或設定：檢查 project.json 的 dependencies 與 frameworks；必要時設定 NuGet 來源。注意事項與最佳實踐：首次還原可能耗時；鎖定版本減少衝突；使用公司內部鏡像可提速。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q3

C-Q6: 如何編譯專案並處理常見警告？
- A簡: 執行 dotnet compile；若有版本衝突警告，統一套件版本或調整相依。
- A詳: 具體實作步驟：
  dotnet compile
  關鍵程式碼片段或設定：檢查輸出警告中顯示的組件與版本；於 project.json 固定版本或提升至一致版本。注意事項與最佳實踐：定期審視相依；以最小相依策略降低衝突；建立 CI 驗證警告為零。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q18, D-Q4

C-Q7: 如何執行應用並看到輸出？
- A簡: 執行 dotnet run，必要時加 -it 啟動容器，確保 TTY 與標準輸出正常。
- A詳: 具體實作步驟：
  dotnet run
  關鍵程式碼片段或設定：於 docker run 加 -t -i；確認 Console.WriteLine 在程式中。注意事項與最佳實踐：若出現無輸出，檢查 TTY、緩衝與框架設定；確保 run 前已 restore/compile 成功。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q17, D-Q6

C-Q8: 如何將現有專案調整為 .NET Core（RC1）在容器內執行？
- A簡: 更新 project.json 目標框架至 dnxcore50，移除僅限 .NET Framework 相依。
- A詳: 具體實作步驟：在 project.json 的 frameworks 指定 dnxcore50，移除 net46x 專屬 API 相依，改用跨平台替代。關鍵程式碼片段或設定：
  "frameworks": { "dnxcore50": {} }
  注意事項與最佳實踐：審視 BCL 差異；第三方套件需支援 .NET Core；以單元測試覆蓋移植風險。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q16, D-Q5

C-Q9: 如何產出可部署成果（publish）？
- A簡: 使用 dotnet publish 產生部署輸出，搭配容器或主機部署。
- A詳: 具體實作步驟：
  dotnet publish
  或在容器中：
  docker run --rm -v "$PWD":/app -w /app microsoft/dotnet dotnet publish
  關鍵程式碼片段或設定：檢視輸出資料夾；選擇目標框架與配置。注意事項與最佳實踐：鎖定版本與來源；將 publish 納入 CI/CD 管線；輸出檔納入映像建置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q19

C-Q10: 如何建立一鍵編譯的 Shell 別名或腳本？
- A簡: 以別名包裝 docker run --rm -v "$PWD":/app -w /app dotnet compile。
- A詳: 具體實作步驟：加入 ~/.bashrc
  alias dnc='docker run --rm -v "$PWD":/app -w /app microsoft/dotnet dotnet'
  使用：
  dnc restore && dnc compile
  關鍵程式碼片段或設定：別名或 Makefile/NPM Script。注意事項與最佳實踐：鎖定映像標籤；在 CI 與本機共用同一腳本，確保一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q3

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: docker pull microsoft/dotnet 失敗怎麼辦？
- A簡: 檢查網路與權限、使用 sudo、改用特定標籤或鏡像來源重試。
- A詳: 問題症狀描述：docker pull 卡住或報錯找不到映像。可能原因分析：網路受限、未使用 sudo 權限、標籤不存在。解決步驟：sudo docker login（必要時）→docker pull microsoft/dotnet:指定標籤→檢查 DNS/Proxy。預防措施：使用近端鏡像/快取伺服；在 CI 設映像代理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1

D-Q2: dotnet -h 與實際可用命令不一致？
- A簡: 屬早期工具現象，依官方 README/範例操作與指定版本標籤。
- A詳: 問題症狀描述：help 列出命令少於文件或缺少 init/restore。可能原因分析：CLI 早期版尚未統一。解決步驟：查閱映像 README；直接嘗試 dotnet init/restore；必要時切換映像版本。預防措施：團隊鎖定工具版本；在文件中標明對應 CLI 版本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, B-Q20

D-Q3: dotnet restore 下載失敗或極慢？
- A簡: 檢查 NuGet 來源、網路、權限；配置企業鏡像或快取以提速。
- A詳: 問題症狀描述：restore 報錯或長時間無進度。可能原因分析：NuGet 來源不可達、代理未設、憑證問題。解決步驟：檢查 nuget.config；設定可靠來源；測試 curl/ping；重試或切換網路。預防措施：建置企業內部 NuGet 快取；版本鎖定減少下載。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q5

D-Q4: 編譯出現相依版本衝突警告怎麼處理？
- A簡: 統一相依版本、於 project.json 鎖定或直接參考指定版本。
- A詳: 問題症狀描述：compile 出現衝突警告。可能原因分析：相依樹不同套件要求多版本。解決步驟：檢視警告詳情→統一版本→必要時升級或降級相依；加入直接引用壓制。預防措施：使用版本範圍最小化；定期相依審視；CI 阻擋新衝突進入主幹。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q6

D-Q5: 容器內執行顯示 runtime 不支援或找不到組件？
- A簡: 調整 project.json 目標為 dnxcore50、移除 .NET Framework 專屬相依。
- A詳: 問題症狀描述：執行報錯目標框架不符、找不到組件。可能原因分析：專案仍針對 .NET Framework 4.6.x；第三方不支援 .NET Core。解決步驟：在 project.json 設 "frameworks": {"dnxcore50": {}}；替換不支援 API；重跑 restore。預防措施：設跨平台抽象；選用支援 .NET Core 的套件。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q16, C-Q8

D-Q6: 編譯與執行成功但 Console 沒有輸出？
- A簡: 檢查 TTY/互動參數、輸出緩衝與目標框架設定，改用 -t -i 啟動。
- A詳: 問題症狀描述：dotnet run 無任何終端輸出。可能原因分析：未分配 TTY；IO 緩衝；框架或程式邏輯。解決步驟：以 -t -i 啟動容器；確認 Console.WriteLine 存在；嘗試直接執行編譯輸出。預防措施：建立輸出測試；在 CI 驗證標準輸出；規範啟動參數。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, C-Q7

D-Q7: docker run 提示「permission denied」或無法進入 bash？
- A簡: 以 sudo 執行、確認映像存在、檢查入口點與命令拼寫。
- A詳: 問題症狀描述：啟動容器失敗。可能原因分析：缺少 root 權限；映像未拉取；命令錯誤。解決步驟：sudo docker images 驗證→sudo docker pull→檢查 /bin/bash 路徑。預防措施：加入 docker 群組；製作啟動腳本減少拼寫錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2

D-Q8: 掛載 -v 後容器內看不到或無法寫入檔案？
- A簡: 檢查路徑、權限與 SELinux/AppArmor；確認以絕對路徑掛載。
- A詳: 問題症狀描述：容器內無檔或寫入失敗。可能原因分析：相對路徑誤用、權限不足、MAC 安全策略。解決步驟：使用 -v "$(pwd)":/app；chown 或授權；調整安全設定或標記。預防措施：統一掛載約定；在專案根執行命令。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q3

D-Q9: 專案在 Windows 可跑，但容器/Linux 失敗？
- A簡: 可能使用僅限 Windows API 或大小寫/路徑差異，需抽象與測試覆蓋。
- A詳: 問題症狀描述：跨平台行為不一致。可能原因分析：BCL 差異、檔案系統大小寫、路徑分隔、權限。解決步驟：抽象系統相依；使用 Path API；修正大小寫；加入跨平台測試。預防措施：在 CI 同時跑 Windows 與 Linux；避免平台特定 API。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q17, B-Q16

D-Q10: 找不到對應的第三方套件（不支援 .NET Core）怎麼辦？
- A簡: 尋找支援替代、使用多目標編譯或自行抽象重寫關鍵功能。
- A詳: 問題症狀描述：restore/compile 報不支援 .NET Core。可能原因分析：套件僅支援 .NET Framework。解決步驟：尋找替代套件；多目標分離相依；以介面抽象並為 .NET Core 實作；逐步移除阻塞相依。預防措施：規劃相依策略；優先選擇跨平台套件。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, C-Q8

---

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 .NET Core RC1？
    - A-Q2: RC、Beta、RTM 有何差異？
    - A-Q4: 「Go Live」在 RC1 代表什麼？
    - A-Q5: 什麼是 Feature Freeze（FF）？
    - A-Q6: 什麼是 DOTNET CLI？
    - A-Q7: DOTNET CLI 與 DNVM/DNX/DNU 的差異？
    - A-Q9: Docker 在本情境扮演什麼角色？
    - A-Q11: 什麼是 microsoft/dotnet 映像？
    - A-Q12: 什麼是一次性（可拋棄）容器？
    - A-Q13: Docker 的 -v、-w、--rm 代表什麼？
    - A-Q14: dotnet init/restore/compile/run 是什麼？
    - C-Q1: 如何取得 DOTNET CLI 的 Docker 映像？
    - C-Q2: 如何啟動互動式容器以便開發測試？
    - C-Q4: 如何用 dotnet init 建立 Hello World 專案？
    - C-Q7: 如何執行應用並看到輸出？

- 中級者：建議學習哪 20 題
    - A-Q10: 什麼是 microsoft/aspnet 映像？
    - A-Q15: 什麼是「編譯為原生機器碼」？
    - A-Q16: 為何 .NET Core 跨平台有價值？
    - A-Q18: NuGet 在流程中的角色是什麼？
    - B-Q1: DOTNET CLI 如何運作？
    - B-Q3: dotnet restore 背後的機制是什麼？
    - B-Q4: dotnet compile 的原理與輸出？
    - B-Q5: dotnet run 的執行流程？
    - B-Q6: 在容器內掛載主機目錄如何運作（-v、-w）？
    - B-Q7: --rm 一次性容器的生命週期機制？
    - B-Q9: microsoft/aspnet 與 microsoft/dotnet 架構差異？
    - B-Q10: 「在容器編譯、不在容器執行」的模式如何設計？
    - B-Q17: 容器中的 Console 輸出如何傳遞到主機？
    - B-Q18: 版本衝突警告的成因與原理？
    - C-Q3: 如何只在容器內編譯當前目錄專案？
    - C-Q5: 如何還原相依套件（restore）？
    - C-Q6: 如何編譯專案並處理常見警告？
    - C-Q9: 如何產出可部署成果（publish）？
    - D-Q3: dotnet restore 下載失敗或極慢？
    - D-Q4: 編譯出現相依版本衝突警告怎麼處理？

- 高級者：建議關注哪 15 題
    - A-Q17: Windows 與 Linux 執行 .NET Core 的差異（高層）？
    - B-Q11: RC1 如何支援跨平台？
    - B-Q13: project.json 在 RC1 的角色？
    - B-Q14: 為何 dotnet -h 只顯示部分命令？
    - B-Q15: 原生編譯（Native）在 CLI 中的工作原理（預覽）？
    - B-Q16: .NET Framework 與 .NET Core 的 BCL 差異如何影響移植？
    - B-Q19: 以掛載方式迭代開發 vs 把程式碼打包入映像的權衡？
    - B-Q20: 為何 RC1 工具可能行為不一致？
    - C-Q8: 如何將現有專案調整為 .NET Core（RC1）在容器內執行？
    - D-Q1: docker pull microsoft/dotnet 失敗怎麼辦？
    - D-Q2: dotnet -h 與實際可用命令不一致？
    - D-Q5: 容器內執行顯示 runtime 不支援或找不到組件？
    - D-Q6: 編譯與執行成功但 Console 沒有輸出？
    - D-Q9: 專案在 Windows 可跑，但容器/Linux 失敗？
    - D-Q10: 找不到對應的第三方套件（不支援 .NET Core）怎麼辦？