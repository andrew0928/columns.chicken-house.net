---
layout: synthesis
title: "在 Docker 上面執行 .NET (CoreCLR) Console App"
synthesis_type: summary
source_post: /2015/10/31/coreclr-helloworld-consoleapp/
redirect_from:
  - /2015/10/31/coreclr-helloworld-consoleapp/summary/
postid: 2015-10-31-coreclr-helloworld-consoleapp
---

# 在 Docker 上面執行 .NET (CoreCLR) Console App

## 摘要提示
- .NET 跨平台: 微軟開放 .NET 並支援 Linux，改變生態與架構決策遠勝單純框架升級。
- Docker 角色: 以容器取代過度虛擬化，維持架構彈性同時降低資源與維運成本。
- 架構思維: 混搭架構將成常態，Windows 與 Linux 皆可成為 .NET 的部署選項。
- 實作策略: 先掌握 Docker 生態與部署，再進入 .NET CoreCLR 的執行與工具鏈。
- 名詞釐清: DNVM、DNX、DNU 與 Core CLR 的關係是理解與上手的關鍵。
- 懶人作法: 直接使用 Microsoft ASP.NET 5 Docker Image，省去在 Linux 手動安裝 DNX。
- 操作核心: 透過 docker exec 進入容器，用 dnvm/dnu/dnx 邏輯還原開發環境。
- 部署步驟: 拉 image、啟容器、進 bash、傳檔、restore 套件、dnx 執行 console app。
- 學習重點: 先解決環境與工具再寫程式，能縮短跨平台落地的時間成本。
- 實戰心得: 文件多偏 Web 範例，Console App 需自行摸索流程，步驟可作為入門指引。

## 全文重點
作者記錄將 .NET Core（CoreCLR）Console App 放入 Docker 在 Linux 上執行的完整過程與心得。文章先點出微軟自新任 CEO 上任後推動 .NET 開源與跨平台的戰略意義，這不僅影響開發框架，更將改變企業在系統與部署層級的架構決策。與此同時，Docker 的崛起以輕量級容器解決 VM 過度虛擬化導致的資源浪費與維運負擔，使得「以理想架構拆分服務」在效能與成本上更可行，促成未來 Windows 與 Linux 混搭部署的主流化。

在實作策略上，作者先從實際案例入手：以 NAS 的 Docker 套件搬遷自家部落格，進一步自行架設 Ubuntu Server 並熟悉 Docker 指令與環境管理，確保面對升級或調整設定時有足夠掌控。接著將焦點放到 .NET Core 的執行與工具鏈，透過最小可行範例（Console App 的「Hello World」）來驗證跨平台執行，而非一開始就鑽研 ASP.NET 5 的應用程式開發。

為避免在 Linux 內手動安裝 DNX，作者採用 Microsoft 官方的 ASP.NET 5 Preview Docker Image，並非照官方教學製作自有 image，而是以 docker exec 進入現成容器，將其視作一個可互動的隔離執行環境。文中釐清了 Core CLR、DNX（執行環境）、DNVM（版本管理）、DNU（套件與建置工具）的關係後，給出具體步驟：拉取 image、啟動容器、查找 container id、進入容器 bash、用 Visual Studio 編譯 Console App、以 docker cp 將檔案丟入容器、用 dnvm 確認/安裝版本、dnu restore 套件、最後以 dnx 執行程式。並透過輸出系統資訊證明實際在 Linux 容器中執行成功。

作者強調，本次最大的挑戰在於多數教學聚焦於 ASP.NET Web 範例，Console App 的流程需要自行摸索。整個過程不僅驗證了工具與環境的可行性，也為後續深入 ASP.NET 5 的研究鋪路。對於想從 Windows 生態跨入 Linux/.NET Core 的讀者，文內步驟與心法提供了一條務實的學習路徑：先懂容器與部署，再以最小範例打通核心工具鏈，最後才是擴展到更完整的應用。

## 段落重點
### 前言：.NET 跨平台與 Docker 的意義
微軟宣布 .NET（v5）可在 Linux 上運行並開源，作者認為這對整體生態與架構決策的影響遠超過單純框架層面的變化。與此同時，Docker 以容器技術提供輕量隔離的應用執行環境，避免 VM 層層虛擬化帶來的資源與維運負擔，讓以服務拆分維持架構正確性與彈性變得更實際。作者先在 NAS 上用 Docker 搬遷 WordPress，再在舊筆電安裝 Ubuntu Server，為 .NET Core 的實驗鋪路。目標是將最基本的 .NET Core Console App 丟進 Docker 並成功執行，藉以掌握跨平台與容器整合的關鍵脈絡。

### 進入主題: .NET Core CLR 體驗
作者擬定三步驟策略：一是快速理解並實作 Docker 的實際應用，而非僅止於概念性 POC；二是親手架設 Ubuntu + Docker 的實戰環境，走過安裝與設定細節以利未來維護與升級；三是熟悉 .NET CoreCLR 的運用方法與工具（DNVM、DNU、DNX），以 Console App 作為最小可行範例，先打通執行與部署流程，再延伸到 ASP.NET 5 的開發研究。此路徑能降低跨平台門檻，將學習重點放在環境與工具鏈的掌握。

### .NET Core CLR 的名詞定義
為避免觀念混淆，作者先釐清幾個核心名詞與關係：Core CLR 是跨平台的執行時（含 VM/JIT/BCL），可個別部署且只佈署所需 BCL。DNX 是 .NET 的執行環境，相當於啟動 .NET App 的宿主。DNVM 是 DNX 的版本管理工具，可安裝、升級或切換不同 DNX。DNU 則是開發工具，負責建置與還原 NuGet 相依。理解這四者角色是上手 .NET Core 與 ASP.NET 5（當時稱）的前提，亦是進容器後操作的關鍵。

### 將 .NET Core APP 放進 Docker 執行
作者選擇使用 Microsoft 的 ASP.NET 5 Preview Docker Image 以快速具備 DNX 環境，並非立刻撰寫 Dockerfile 包成自有 image；改以 docker exec 進入容器互動操作，等同把容器當成一個可登入的輕量環境。具體步驟包括：docker pull 取得 image、docker run 啟動容器、docker ps 取得 container id、docker exec -it 進入 bash；在本機以 Visual Studio 2015 建立 Console App 並編譯，再以 docker cp 複製檔案進容器；於容器中用 dnvm list/upgrade 管理執行環境、在專案目錄 dnu restore 取得相依套件、最後以 dnx 啟動執行。作者以輸出 OS 資訊佐證程式確實在 Linux 容器中運行。過程中最大難點是多數教學以 Web 範例為主，Console App 需自行串起流程；本文即是將探索後的可行路徑整理為可重用的筆記，提供給想從 Windows 跨入 Linux 的 .NET 開發者參考。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 C#/.NET 與命令列操作
   - Docker 基本概念與常用指令（image、container、pull/run/exec/cp）
   - Linux 基本檔案系統與 shell 操作
   - 了解 .NET Core/CoreCLR 與傳統 .NET Framework 的差異

2. 核心概念：
   - .NET Core/CoreCLR：跨平台的 .NET 執行時，精簡可個別部署的 CLR 與 BCL
   - DNX/DNVM/DNU：當時期 ASP.NET 5/.NET Core 的執行環境、版本管理與開發工具鏈
   - Docker 容器化：以 image 建立隔離的執行環境，較 VM 更輕量
   - 佈署流程：使用官方 ASP.NET 5 CoreCLR 映像，將 console app 放入容器，透過 dnvm/dnu/dnx 執行
   - 關係：.NET 應用在 Docker 容器中執行，容器內以 DNX 啟動程式、DNU 還原套件、DNVM 管理 DNX 版本

3. 技術依賴：
   - 主機端：Docker Host（NAS/Ubuntu/Windows + Docker Toolbox）
   - 容器映像：microsoft/aspnet:1.0.0-beta8-coreclr（官方預覽映像）
   - 工具鏈依賴：DNVM（安裝/切換 DNX）→ DNX（執行 app）→ DNU（還原 NuGet 套件）
   - 檔案傳遞：docker cp 在 host 與 container 間傳檔
   - 指令序：docker pull → docker run → docker ps → docker exec（進入 bash）→ dnvm list/install → dnu restore → dnx run

4. 應用場景：
   - 在 Linux 上執行 .NET Core（含 console app）以驗證跨平台
   - 以容器化實作輕量、模組化的系統架構與實驗環境
   - 家用/小型環境（NAS）節省資源部署部落格/服務
   - 開發/測試快速驗證（不需完整 VM 與安裝流程）
   - 預備正式化佈署（日後再以 Dockerfile 打包、結合反向代理與備份）

### 學習路徑建議
1. 入門者路徑：
   - 安裝 Docker（Windows 可用 Docker Toolbox；或使用支援 Docker 的 NAS）
   - 熟悉基本指令：pull/run/ps/exec/cp
   - 了解 CoreCLR 與 DNX/DNVM/DNU 的角色
   - 以官方映像 microsoft/aspnet:1.0.0-beta8-coreclr 啟動容器，將 Hello World console app 複製進容器並執行

2. 進階者路徑：
   - 在 Ubuntu Server 親手安裝與設定 Docker 環境
   - 練習容器內版本管理：dnvm list/install/upgrade，選擇 coreclr x64
   - 使用 dnu restore 管理 NuGet 相依
   - 探索容器管理最佳實務（--restart、logs、volume 掛載）

3. 實戰路徑：
   - 將應用與相依打包成自有 Docker image（撰寫 Dockerfile）
   - 以反向代理（如 Nginx）統一對外端口與 URL，規劃備份與維運
   - 將流程納入 CI/CD，於建置階段還原套件與執行測試
   - 規劃多容器組合與資源配置（從 PoC 走向可上線的部署）

### 關鍵要點清單
- CoreCLR 定義：.NET Core 的跨平台執行時，精簡可個別部署，僅佈署所需 BCL (優先級: 高)
- DNX 角色：.NET 執行環境與命令列啟動器，負責啟動 .NET/ASP.NET 應用 (優先級: 高)
- DNVM 角色：DNX 版本管理工具，用於安裝、切換、升級 DNX (優先級: 高)
- DNU 角色：開發工具（相當於建置與套件管理），進行 build 與 NuGet 相依還原 (優先級: 高)
- Docker vs VM：容器僅虛擬化應用環境，更輕量且降低維運負擔 (優先級: 高)
- 官方映像使用：選用 microsoft/aspnet:1.0.0-beta8-coreclr 省略環境安裝，直接進入執行 (優先級: 中)
- Docker 指令序：pull → run（可加 -d 與 --restart）→ ps → exec -it 進入 bash (優先級: 高)
- 容器互動：在容器內以 root/shell 操作，如同 SSH 進入輕量系統 (優先級: 中)
- 檔案傳遞：使用 docker cp 在 Host 與 Container 間複製應用檔案 (優先級: 高)
- 版本選擇：dnvm list/ install/ upgrade 選定 coreclr x64 對應的 DNX 版本 (優先級: 中)
- 相依還原：在專案目錄執行 dnu restore，從 NuGet 拉取缺少的套件 (優先級: 高)
- 執行應用：以 dnx run 在容器內執行 .NET Core console app (優先級: 高)
- 環境選擇：NAS、Ubuntu Server、或 Docker Toolbox/Boot2Docker 皆可作為 Host (優先級: 中)
- 架構影響：.NET 開放與跨平台促成混搭架構與容器化部署決策 (優先級: 中)
- 實作建議：避免只做 PoC；納入反向代理、備份、維運與資源規劃 (優先級: 中)