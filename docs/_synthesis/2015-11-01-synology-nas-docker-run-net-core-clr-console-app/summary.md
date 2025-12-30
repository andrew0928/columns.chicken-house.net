---
layout: synthesis
title: "同場加映: 用 Synology NAS 的 Docker 環境，執行 .NET Core CLR Console App"
synthesis_type: summary
source_post: /2015/11/01/synology-nas-docker-run-net-core-clr-console-app/
redirect_from:
  - /2015/11/01/synology-nas-docker-run-net-core-clr-console-app/summary/
---

# 同場加映: 用 Synology NAS 的 Docker 環境，執行 .NET Core CLR Console App

## 摘要提示
- Synology Docker: 直接在 Synology NAS 上用 Docker 執行 .NET Core，免去自行架 Linux 的複雜設定。
- 專案範本選擇: 在 VS2015 建立 Console Application (Package)，並切換到 DNX Core 5.0。
- 編譯產出設定: 勾選 Produce outputs on build，編譯後輸出至 solution/artifacts/bin。
- 取得映像檔: 於 NAS 的 Docker/Registry 拉取 microsoft/aspnet:1.0.0-beta8-coreclr。
- 建立容器: 使用 Launch Container 精靈建立 NetCoreCLR 容器。
- 目錄掛載: 將 NAS 的 /docker/netcore 掛載至容器 /home，並取消唯讀以利檔案存取。
- 套件還原: 進容器後以 dnu restore 還原相依套件。
- 執行方式: 使用 dnx HelloCoreCLR.dll 在容器內啟動 Console App。
- 資源占用: .NET Core 容器記憶體占用極低，約 6MB。
- 採購提醒: Synology 僅部分（多為 Intel CPU）機型支援 Docker，購買前須查核清單。

## 全文重點
本文延續前文的 .NET Core Console App 實驗，改以 Synology NAS 內建的 Docker 環境實作，展示如何在不重建整套 Linux 環境的前提下，快速執行 .NET Core 應用。流程自 Visual Studio 2015 建立「Console Application (Package)」專案起手，切換執行時為 DNX Core 5.0，並在專案屬性勾選產出編譯檔以取得 artifacts/bin 下的輸出。NAS 端僅需安裝 Docker 套件，於 Registry 拉取 microsoft/aspnet:1.0.0-beta8-coreclr 映像，之後以 GUI 啟動容器、設定容器名稱與資源限制，關鍵在進階設定中把 NAS 的 /docker/netcore 掛載到容器 /home，使複製好的編譯輸出可直接在容器中使用。容器啟動後，開啟 Terminal 進入 dnxcore50 環境，先以 dnu restore 還原套件，再用 dnx HelloCoreCLR.dll 執行，成功輸出訊息。整體操作相較自行搭建 Linux/容器顯著簡化，資源消耗也極低，約 6MB 記憶體。文末提醒若為了 Docker 打算採購 NAS，須先確認支援清單；就 Synology 而言，僅部分多為 Intel CPU 的機種支援 Docker，並提供官方連結與機型列表供參考。總結而言，對不追求極致效能、只想快速驗證 .NET Core 的開發者，Synology NAS 的 Docker 是省時省力的解決方案。

## 段落重點
### 開發環境準備: Core CLR 版 "Hello World !"
作者以 Visual Studio 2015 建立 .NET Core Console App，需從 Visual C# > Web 中選擇 Console Application (Package) 範本，並切換運行時為 DNX Core 5.0。為取得可部署的編譯輸出，必須在專案屬性勾選「Produce outputs on build」，編譯後在 solution/artifacts/bin 下可看到產物。接著於程式加入基本輸出（Hello World），並以 Ctrl+F5 驗證。此流程重點在選對支援 Core CLR 的專案類型與正確輸出設定，因為 .NET Core 專案的目錄與產出結構與傳統 .NET Framework 有所不同，需特別留意，之後才方便複製到 NAS 進行容器化執行。

### 事前準備: NAS + Docker
在 Synology NAS 上，先透過套件中心安裝 Docker 套件。開啟 Docker 應用後，於 Registry 搜尋並拉取 microsoft/aspnet 映像，指定標籤 1.0.0-beta8-coreclr，映像大小約 350MB；下載完成 DSM 會通知。這一步提供一個預建、可執行 .NET Core 的基礎環境，省去自行建立 Linux、安裝相依套件與配置執行時的成本。相比手動搭建，此步驟透過圖形化介面完成映像抓取，對初學者或只求快速驗證的開發者而言更友善。

### 佈署與執行
以 Docker GUI 啟動容器（相當於 docker run），將其命名為 NetCoreCLR；資源限制可先略過。進入 Advanced Settings，將 NAS 的 /docker/netcore 掛載至容器的 /home，並取消唯讀，讓先前在 VS 編譯輸出的檔案能被容器讀寫。將本機產出複製到 NAS 的掛載目錄後，啟動容器、開啟 Details 裡的 Terminal。進入 dnxcore50 目錄後，先執行 dnu restore 還原相依套件，接著用 dnx HelloCoreCLR.dll 啟動程式並看到輸出。作者實測容器記憶體占用僅約 6MB，顯示 .NET Core 在該映像上的資源需求相當精簡。最後提醒若為 Docker 而採購 NAS，需先確認 Synology 支援型號（多為 Intel 架構），避免買到不支援 Docker 的機種。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 了解 .NET Core（早期 DNX/CoreCLR 架構）與 Visual Studio 2015 的基本使用
   - 基本 Docker 概念（image、container、volume 掛載）
   - Synology DSM 套件中心與權限/共享資料夾管理
2. 核心概念：
   - .NET Core CLR Console App：以 DNX Core 5.0 執行的主控台程式，需產出可部署的輸出
   - Docker 容器化環境：在 Synology NAS 上透過 Docker 套件拉取 microsoft/aspnet:1.0.0-beta8-coreclr image 執行
   - Volume 掛載：將 NAS 目錄（/docker/netcore）掛載至容器內（/home），以便置入編譯輸出
   - DNX/DNU 工具鏈：容器內以 dnu restore 還原套件、dnx 執行應用
   - 映像標籤與相依：指定 tag 1.0.0-beta8-coreclr，約 350MB，容器記憶體占用極小
3. 技術依賴：
   - Synology 機種需支援 Docker（多為 Intel CPU 機種）
   - DSM 安裝 Docker 套件 → 從 Registry 拉取 microsoft/aspnet:1.0.0-beta8-coreclr → 以 GUI 啟動容器
   - 本機 VS2015 產出 artifacts/bin 輸出 → 複製至 NAS 掛載資料夾 → 容器內執行 dnu/dnx
4. 應用場景：
   - 在家用/小型辦公環境快速驗證 .NET Core Console App
   - 想避開自行建立 Linux/CLI 環境的完整安裝流程
   - 以低資源成本啟動暫時性測試環境或 PoC

### 學習路徑建議
1. 入門者路徑：
   - 認識 Docker 基本概念（image、container、volume）
   - 在 VS2015 建立 .NET Core CLR Console App，了解「Produce outputs on build」並找到 artifacts/bin
   - 於 Synology DSM 安裝 Docker 套件、從 Registry 拉取指定位號 image
2. 進階者路徑：
   - 練習在 Docker 容器中使用 dnu restore、dnx 執行流程
   - 設計並測試資料夾掛載策略（唯讀/讀寫、路徑規劃）
   - 以 DSM Docker GUI 等同於 docker run 的參數調校（資源限制、環境變數）
3. 實戰路徑：
   - 將 VS 產出的 Console App 自動化複製至 NAS 掛載資料夾（批次/腳本）
   - 建立多個容器測試不同組態或版本標籤
   - 監控容器資源使用（記憶體、CPU）與記錄容器日誌

### 關鍵要點清單
- 機種相容性：Synology 僅部分（多為 Intel CPU）機種支援 Docker，採購前務必確認（優先級: 高）
- Docker 套件安裝：於 DSM 套件中心安裝官方 Docker 套件，作為基礎執行環境（優先級: 高）
- 映像選擇：從 Registry 拉取 microsoft/aspnet:1.0.0-beta8-coreclr（文章示例版本），約 350MB（優先級: 中）
- VS 專案模板：在 VS2015 選用 Console Application (Package)（歸在 Web 範疇），支援 Core CLR（優先級: 中）
- 目標 Runtime：切換至 DNX Core 5.0，確保以 CoreCLR 執行（優先級: 高）
- 產出設定：勾選 Produce outputs on build，於 artifacts/bin 取得可部署輸出（優先級: 高）
- Volume 掛載：將 NAS /docker/netcore 掛載到容器 /home，並取消唯讀以利檔案存取（優先級: 高）
- 啟動容器：以 DSM Docker GUI 的 Launch 流程，相當於 docker run（優先級: 中）
- 容器終端機：進入容器 details → terminal，以便執行還原與啟動命令（優先級: 中）
- 套件還原：於容器內執行 dnu restore，解決相依套件（優先級: 高）
- 執行應用：使用 dnx HelloCoreCLR.dll 啟動 Console App（優先級: 高）
- 資源占用：示例容器記憶體約 6MB，適合輕量測試（優先級: 低）
- GUI 與 CLI 對應：理解 DSM GUI 操作對應 docker 指令，便於日後自動化（優先級: 中）
- 檔案流程：本機編譯 → 複製輸出至 NAS 掛載資料夾 → 容器內執行（優先級: 中）
- 版本時代性：本文基於 DNX/beta8 時期流程，實務應注意與新版本之差異（優先級: 中）