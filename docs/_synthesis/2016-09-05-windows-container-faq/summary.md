---
layout: synthesis
title: "Windows Container FAQ - 官網沒有說的事"
synthesis_type: summary
source_post: /2016/09/05/windows-container-faq/
redirect_from:
  - /2016/09/05/windows-container-faq/summary/
postid: 2016-09-05-windows-container-faq
---

# Windows Container FAQ - 官網沒有說的事

## 摘要提示
- Windows Container 與 Docker for Windows: 兩者不同；前者跑原生 Windows 應用並共享 Windows kernel，後者是在 Windows 上管理 Linux VM 裡的 Docker。
- 技術現況與版本: Windows Container 依賴 Windows Server 2016（TP5 時期）；Windows 10 可用 Hyper-V 隔離類型。
- 相容性邊界: Windows Container 無法執行 Linux 映像；需使用為 Windows 打包的 container image。
- 工具一致性: 可用同一套 Docker CLI/Client 管理 Windows Container，甚至可用 Linux 端的 Docker Client 遠端操作。
- 映像來源與基底: 主要從 Docker Hub 取得；Microsoft 提供 windowsservercore 與 nanoserver 作為 base image。
- 開發與延伸: 典型延伸映像如 microsoft/iis 由 base image 演化；官方 GitHub 提供 Dockerfile 範例。
- 網路功能限制: TP5 時期缺少 container linking、內建 DNS 名稱解析、overlay network 等，影響微服務部署體驗。
- 部署門檻與建議: 現階段可評估可行性並著手實驗，但需預期網路與相依功能的不完整。
- 生態系整合: Windows Container 盡量沿用 Docker 生態（API、映像格式、Registry、管理協定、叢集等）。
- 學習資源: 官方 FAQ、部署指南與深度文章可作為從 Linux Docker 轉向 Windows Container 的入門路徑。

## 全文重點
本文作者以實務視角梳理 Windows Container 的重點與常見誤解，特別是官方 FAQ 未充分交代之處。背景上，多數企業仍運行傳統 ASP.NET Web Forms 或商用軟體，直接升上 .NET Core 並完全採用 Docker（Linux）並不切實際；相對地，Windows Container 讓現有的 Windows 應用在容器化道路上有了可用的承接方案。文章指出，Windows Container 並非 Docker for Windows：兩者服務的對象、核心、可執行應用完全不同。Windows Container 是微軟在 Windows Server 2016 首次提供的容器功能，容器共享的是 Windows kernel，能運行原生 Windows 應用程式；Docker for Windows 則是協助在 Windows 上便利地操作一個 Hyper-V 裡的 Linux VM 與其內的 Docker Engine，能執行的依然是 Linux 應用。

在可用性方面，Windows Container 於 Windows Server 2016 上提供，TP5 時期已可試用，正式版預期隨 2016 年 10 月 Windows Server 2016 發布。此外，微軟支援兩種隔離類型：傳統 process/namespace 隔離，以及 Hyper-V 隔離；後者在 Windows 10 Pro/Enterprise RS 更新後可用。就生態系而言，Windows Container 盡可能與 Docker 生態對齊，包括 API、CLI、映像格式、Registry、叢集與管理協定等，因此使用者可以沿用既有工具鏈；你甚至能用 Linux 的 Docker Client 來管理 Windows 上的 Container Engine。

關於映像來源與建立，Windows Container 不相容於 Linux 的映像，必須使用專為 Windows 打包的映像。可從 Docker Hub 取得，如 microsoft/windowsservercore、microsoft/nanoserver 與 microsoft/iis 等。常見做法是以官方 base image（windowsservercore、nanoserver）為基礎延伸，並參考微軟在 GitHub 提供的範例 Dockerfile。值得注意的是，Docker Hub 在辨識某映像屬於 Linux 或 Windows 平台上並不直觀，取用時需特別留意。

在實務問題與限制上，TP5 雖可支援多數容器基本功能，但網路功能仍不完整，對部署微服務架構造成阻礙。Docker 在 Linux 世界提供的 container linking、服務名稱解析（內建 DNS）、overlay network 與多種 networking options 在 TP5 上尚未支援或僅部分支援，導致服務間通訊、動態解析與跨主機網路編排更繁瑣。文中引用官方清單，明確指出不支援的 Docker 網路選項（例如 --link、--dns、--hostname、--net-alias、overlay 預設驅動等）。若你的目標是大規模微服務與動態服務發現，目前的 Windows Container 需等待後續更新或採用替代方案。

總結來說，若目標是容器化既有 Windows 應用，現在就能在 Windows Server 2016（TP5）環境中開始實驗與評估，並享受與 Docker 生態兼容的工具鏈；但必須接受網路與相關功能尚未完整的現實。對初學者與從 Linux Docker 轉換而來的讀者，本文也整理了官方 FAQ、部署指南與深度文章作為進一步學習資源。

## 段落重點
### 參考資料
作者整理了進入 Windows Container 的快速資源：官方 FAQ、Windows Server 部署指南，適合理解 Docker on Linux 者轉向 Windows Container 時使用。此外，推薦閱讀 InfoQ 的專文，從更宏觀的角度理解 Windows 與 Docker 的關係與演進。這些資料有助於釐清平台差異與部署步驟，並提供最佳實務與常見問題的參考。

### Q1. Windows Container 跟 Docker for Windows 是一樣的東西嗎?
核心差異在於執行環境與支援應用：Windows Container 由微軟在 Windows Server 2016 首度提供，容器共享 Windows kernel，可執行原生 Windows 應用；Docker for Windows 則是讓你在 Windows 上便捷地操作一個 Hyper-V 裡的 Linux VM 與其中的 Docker Engine，因此執行的是 Linux 應用。儘管底層不同，Windows Container 盡量與 Docker 生態對齊，包含 API、CLI、映像格式、Registry 與叢集協定等，方便使用者沿用同一套工具與流程。

### Q2. 怎麼樣才能使用 Windows Container ?
目前支援重點在 Windows Server 2016，TP5 為當時可用的公開技術預覽版，正式版預期 2016/10 發布。啟用 Windows Container 需依官方快速入門進行設定。隔離模式有兩種：傳統 process/namespace 隔離，以及透過 Hyper-V 的更強隔離；Windows 10 Pro/Enterprise 在 2016/08 RS 更新後可使用 Hyper-V 隔離的 Windows Container，並有對應的安裝指南。理解這兩種隔離的差異有助於在安全性、相容性與效能間做取捨。

### Q3. Windows Container 能執行現有的 Docker Container Image 嗎?
不行。因為 Windows Container 以 Windows kernel 為基礎，無法執行以 Linux 為目標的映像。要在 Windows Container 執行，必須使用 Windows 版本的 container image。取得方式與 Docker 一致：可以用 Dockerfile 自行建置，或是從 Docker Hub 或其他 Registry 直接拉取。

### Q4. 我能用 Docker Client 管理 Windows Container 嗎?
可以。Docker Client 在協定與用法上是共通的，你甚至能在 Linux 環境使用 Docker Client 遙控管理 Windows Server 上的 Container Engine。這意味著現有自動化腳本、CI/CD 管線與管理工具可以最小改動地延伸至 Windows Container 場景，提升跨平台操作的一致性。

### Q5. Windows Container 的 Image 可以從哪裡取得?
與 Docker 生態一致，主要從 Docker Hub 取得。微軟提供兩個官方 base image：microsoft/nanoserver 與 microsoft/windowsservercore，常見的 microsoft/iis 等映像也是基於這些 base 進一步封裝。實作上可用這些 base image 寫 Dockerfile 自行擴充；微軟在 GitHub 提供了範例可供參考。需注意的是，Docker Hub 並無直覺方式區分某映像是 Linux 或 Windows 版，拉取前請確認平台標註或文件說明以避免相容性問題。

### Q6. 目前 Windows Server 2016 Tech Preview 5 有那些問題?
TP5 整體可運作，評估可行性已足夠；然而網路相關能力尚不完整，對需要微服務與動態服務發現的場景較為不利。當前不支援或尚未完整支援的功能包括：container linking（--link）、服務名稱/內建 DNS 解析、預設 overlay network driver，以及多項 Docker 網路選項（--add-host、--dns、--dns-opt、--dns-search、--hostname、--net-alias、--aux-address、--internal、--ip-range 等）。這使得跨容器通訊、名稱解析與跨主機網段編排需改以替代方法或等待後續服務更新。對開發者而言，若當前工作重心是將既有 Windows 應用容器化並在單機或簡單網路拓撲中運行，TP5 已足以實作與測試；若要部署大規模微服務，則需預先規畫網路與服務發現的替代機制或等待正式版新增支援。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 具備 Docker 基礎概念（鏡像/容器、Dockerfile、Registry、Client/Engine）
   - 基本 Windows Server/Windows 10 管理與 Hyper-V 概念
   - 了解 Linux 與 Windows Kernel 差異（容器相依作業系統核心）

2. 核心概念：
   - Windows Container 與 Docker for Windows 差異：前者運行 Windows 應用，後者在 Windows 上運行 Linux Docker
   - Kernel 相容性：容器與映像需與底層 Kernel 一致（Windows 只能跑 Windows App）
   - 隔離類型：Process/Namespace 隔離與 Hyper-V 隔離
   - 生態系共用：共用 Docker API/Client/Registry/Image 格式等
   - 版本與支援：Windows Server 2016（TP5 時期限制）、Windows 10 Pro/Ent（僅 Hyper-V 隔離）

3. 技術依賴：
   - Windows Container 依賴 Windows Kernel（非 Linux Kernel）
   - Docker 生態系（Client、Registry、Image 格式）作為管理與交付層
   - 基底映像（microsoft/windowsservercore、microsoft/nanoserver）作為自建映像依據
   - Hyper-V 作為可選隔離技術（Windows 10 上的必要條件）

4. 應用場景：
   - 將既有 Legacy Windows 應用（IIS、.NET Framework 應用）容器化
   - 在 Windows 環境導入 Docker 工作流（CI/CD、映像管理、Registry）
   - 在開發/測試環境快速複製一致的 Windows 執行環境
   - 初步探索微服務架構於 Windows（注意 TP5 網路功能限制）

### 學習路徑建議
1. 入門者路徑：
   - 先熟悉 Docker 基礎（容器/映像/Registry、Docker CLI）
   - 了解 Windows Container 與 Docker for Windows 的差異與相容性限制
   - 在 Windows Server 2016 或 Windows 10（Hyper-V 隔離）依官方快速入門完成安裝與第一個容器執行
   - 從 Microsoft 提供的基底映像拉取與運行（nanoserver、windowsservercore、iis）

2. 進階者路徑：
   - 撰寫 Dockerfile 建置自有 Windows 映像，最佳化層（Layers）與映像大小
   - 熟練使用 Docker Client 遠端管理 Windows 容器主機
   - 研究容器網路模型與目前限制，設計可行的服務間通訊策略
   - 將傳統服務（如 IIS Web Site）模組化並建立自動化 Build/Push 流程

3. 實戰路徑：
   - 將一個既有 WebForm/MVC 應用打包為 IIS on windowsservercore 的映像，配置環境參數
   - 建立私有 Registry 或使用 Docker Hub 版控映像，串接 CI/CD
   - 規劃多容器應用拓撲並以目前可用的網路機制實作（暫代替不支援功能）
   - 監控與記錄：在容器中整合日誌輸出與健康檢查，驗證擴展與回滾流程

### 關鍵要點清單
- Windows Container vs Docker for Windows：前者跑 Windows App，後者在 Windows 上跑 Linux Docker（VM 裡）(優先級: 高)
- Kernel 相容性：容器必須與底層 Kernel 相符，不能跨 Windows/Linux 映像運行 (優先級: 高)
- 支援平台：Windows Server 2016（正式版才完整），Windows 10 僅支援 Hyper-V 隔離 (優先級: 高)
- 隔離模式：Process/Namespace 與 Hyper-V 雙模式選擇，依安全與相容性需求取捨 (優先級: 中)
- Docker 生態共用：可用相同 Docker Client、API、Registry、Image 格式管理 Windows 容器 (優先級: 高)
- 基底映像選擇：microsoft/nanoserver 與 microsoft/windowsservercore 作為建置起點 (優先級: 高)
- 常用映像：microsoft/iis 等從基底映像延伸，適合承載 Web 應用 (優先級: 中)
- 取得映像：從 Docker Hub 拉取（辨識 Windows/Linux 映像需留心）或自行 Build (優先級: 中)
- Docker 客戶端相容：可用 Linux 版 Docker Client 管理 Windows 容器主機 (優先級: 中)
- 網路功能限制（TP5）：不支援 --link、內建名稱解析、overlay driver 等，影響微服務部署 (優先級: 高)
- 微服務影響：由於網路限制，設計服務間通訊需替代方案或等待更新 (優先級: 中)
- 部署學習資源：MSDN FAQ、Deployment 指南與官方 Sample 倉庫 (優先級: 中)
- 遷移策略：Legacy Windows 應用可先容器化於 Windows Server 2016，逐步導入 CI/CD (優先級: 中)
- 性能與安全：Hyper-V 隔離提升隔離度但有額外開銷，需依場景評估 (優先級: 低)
- 時程與版本意識：TP5 為技術預覽，有錯誤與缺功能，正式版釋出後再評估落地 (優先級: 中)