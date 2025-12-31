---
layout: synthesis
title: "容器化的微服務開發 #1, IP查詢架構與開發範例"
synthesis_type: summary
source_post: /2017/05/28/aspnet-msa-labs1/
redirect_from:
  - /2017/05/28/aspnet-msa-labs1/summary/
postid: 2017-05-28-aspnet-msa-labs1
---

# 容器化的微服務開發 #1, IP查詢架構與開發範例

## 摘要提示
- 容器驅動開發: 以容器為前提設計微服務，讓執行環境與部署需求反向影響架構與程式撰寫方式。
- 架構藍圖: 以 Reverse Proxy + 多個 WebAPI 節點達成 HA/Scale-out，搭配 Worker 週期更新 IP 資料庫。
- 高可用與擴展性: 透過反向代理分流與容器化的水平擴展，讓服務可彈性擴充與容錯。
- 自動更新資料: Worker 下載、解壓、驗證 IP DB，再原子替換共享檔案，降低服務中斷風險。
- SDK 與快取: 提供 .NET SDK 包裝 REST 呼叫並內建 client-side cache，提升 DX 與效能。
- DevOps 流程: Push 觸發 CI 編譯與測試，Image 發佈至 Registry，SDK 推至 NuGet，Compose 一鍵部署。
- 技術棧: Windows Container + .NET Framework + ASP.NET Web API + Docker + Azure 的實作範例。
- WebAPI 容器化: 使用 microsoft/aspnet 基底 Image，Expose 80，將 App_Data 宣告為可掛載 Volume。
- Worker 容器化與日誌: Console 應用以 ENTRYPOINT 背景執行，stdout 直接用 docker logs 檢視。
- Volume 共享: 以 Host 目錄同掛兩個容器同步資料，簡化跨服務檔案共享與權限設定。

## 全文重點
文章以一個「IP 所屬國家查詢」微服務為題，示範如何用容器驅動開發思維設計、實作與部署。作者指出不少容器文章偏重既有應用的容器化，而忽略開發者視角。因此本文採用 Windows Container + .NET Framework + Azure，從需求出發：高可用與可擴展、自動更新 IP 資料庫、提供易用 SDK（含客戶端快取）、以及良好開發者體驗。整體架構以 Reverse Proxy 負責分流，後端多實例的 IP2C.WebAPI 提供查詢服務；另有 IP2C.Worker 週期從官方來源下載最新 IP DB，解壓與驗證無誤後，部署至共享儲存供 WebAPI 熱載入使用。SDK 封裝 REST 呼叫並加入快取，減少重複查詢。

DevOps 規劃方面，Git Push 觸發 CI 進行編譯與單元測試；通過後將 WebAPI 與 Worker 打包成 Docker Image 上傳至 Registry；SDK 產生 NuGet 套件並推送；正式發版則以預先定義的 Docker Compose 滾動更新。文章接著展示 Solution 結構與各專案職責：WebAPI 使用 ASP.NET Web API 2，路由形如 /api/ip2c/{ipv4整數}，以 MemoryCache + HostFileChangeMonitor 監控 App_Data/ipdb.csv；其 Dockerfile 基於 microsoft/aspnet，Expose 80 並將 App_Data 宣告為 Volume。Worker 則是 Console App，定時下載 .gz、解壓、以內建測試驗證檔案，通過後備份舊檔並原子替換；其 Dockerfile 基於 microsoft/dotnet-framework，設定 ENTRYPOINT 執行。

作者示範在本機同時啟動 WebAPI 與 Worker 容器，透過 -v 將同一個 Host 目錄分別掛載到兩個容器內的資料夾，達到共享資料庫檔案；用 docker logs 直接檢視 Worker 輸出，證明排程與更新運作正常；並透過瀏覽器呼叫 WebAPI 完成查詢。文中強調容器的三大部署介面：network、volume、environment variables，讓開發者專注於程式本身，不必再為服務註冊、排程、安裝器、檔案分享與權限等瑣事分心。最後指出容器讓相同的 Image 從開發機到叢集都能一致執行，藉由 scale-out 應對高流量，展現容器技術帶來的生產力與可維運性。下一篇將介紹 SDK、Reverse Proxy 與 Docker Compose 的實務運用。

## 段落重點
### 容器驅動開發 (Container Driven Development)
作者先釐清目標：即使是單純的「IP 查詢」也需達成獨立運作、可擴展與自動更新等微服務準則。需求包括高可用與擴展性、自動更新 IP 資料庫、提供含快取的 SDK，以及良好的開發者體驗。基於此，設計以 Reverse Proxy 為前端入口，後端多實例 WebAPI 供查詢；另設置 Worker 週期更新資料庫並驗證，合格後發布至共享儲存給 WebAPI 使用。SDK 封裝 REST 與快取，降低呼叫成本。DevOps 側重自動化：Git Push 觸發 CI 編譯與測試；通過後建置 Image 並推至 Registry；SDK 打包 NuGet 並發布；最後以 Docker Compose 進行升版。作者強調容器化不僅是「把程式丟進容器」，而是從設計之初就以容器行為（映像建置、網路/Volume/環境變數、可平行擴展、可觀測）來倒推系統分工與開發方式，讓服務能在不同環境中一致部署與操作。

### 建立微服務 Solution: IP2C
Solution 結構包含：build.cmd（整體編譯與發行腳本，亦可嵌入 CI）、docker-compose.yml（部署定義）、IP2C.NET 與 IP2CTest（來自 Darkthread 的高效查詢函式庫及其單元測試）、IP2C.WebAPI（ASP.NET Web API 2，提供 REST 查詢）、IP2C.Worker（Console App，定時更新資料）、IP2C.SDK（呼叫 WebAPI 的 .NET Library，內建 client-side cache）。作者將 DevOps 實作以簡化的 build script 示範，並在後續環節直接手動部署到 Azure，聚焦於程式與容器建置。此段的重點是界定各專案的單一職責與分層邊界，使後續容器化與部署行為精確可控，並提供完整的原始碼連結以供讀者參考與實作。

### Project: IP2C.WebAPI
WebAPI 提供查詢路由 /api/ip2c/{ipv4整數}，以 JSON 回傳 CountryName 與 CountryCode。資料來源為 App_Data/ipdb.csv（約 12MB），核心查詢邏輯使用 IP2C.NET。為兼顧效能與即時更新，利用 MemoryCache 與 HostFileChangeMonitor 監控檔案變動，檔案更新可熱載入。Dockerfile 基於 microsoft/aspnet，將已編譯好的 Web 檔案複製至 c:/inetpub/wwwroot，Expose 80，並將 App_Data 宣告為 Volume，利於部署時掛載共享儲存。作者示範以 MSBuild 編譯並 docker build 成 Image，透過 docker run -p 8000:80 啟動本機測試，也提醒 Windows NAT 不支援 loopback 的限制。關鍵在於：WebAPI 容器化後，開發機不需安裝 IIS/Express，即可以與正式環境一致的方式運行與驗證，縮短環境差異帶來的除錯成本。

### Project: IP2C.Worker
Worker 的任務是「可靠地」定期更新 IP DB：在排程時間到達時下載官方 .gz 檔、解壓、以內建測試（如查詢特定 IP 是否回傳預期國別）驗證檔案正確，再備份舊檔並原子替換；若首次執行無舊檔則以內附版本墊檔。記錄方面不額外導入 logging framework，而是直接 Console.WriteLine 輸出 stdout，由運維以 docker logs 取得。Dockerfile 基於 microsoft/dotnet-framework，指定工作目錄、宣告資料 Volume，並以 ENTRYPOINT 啟動可長駐的 Console 程式；以 -d 背景模式執行即等同於服務常駐。此設計避免了傳統 Windows Service 的安裝與管理、工作排程器設定、安裝器撰寫等繁瑣步驟，將服務生命週期、日誌存取與升版行為全面交由容器與 Docker 工具鏈統一治理，極大化開發專注度與可維運性。

### Test Run: IP2C Services (WebAPI + Worker) on Local PC
實測同機啟動 WebAPI 與 Worker 兩個容器，關鍵在「共享資料」：建立一個 Host 目錄（如 d:\data），以 -v 分別掛載至 WebAPI 的 App_Data 與 Worker 的 data，Worker 更新後 WebAPI 即可熱讀新檔。作者示範以 docker logs 觀察 Worker 定時更新紀錄，並在容器內部以 dir 驗證檔案備份與替換；隨後用瀏覽器呼叫 /api/ip2c/134744072（對應 8.8.8.8）驗證查詢成功。此段延伸說明容器部署三大介面：Network（埠對映）、Volume（檔案/資料夾掛載）、Environment Variables（設定注入），大幅簡化了跨服務檔案共享相較傳統檔案分享/網路磁碟/iSCSI 的權限與設定難題。同一套 Image 與設定手法，從開發機可無痛平移到 Swarm/叢集，藉由增加 WebAPI 實例達成水平擴展，以一致的工序應對不同規模與流量場景。

### 小結
作者總結容器帶來的核心價值：以一致的映像規格封裝執行環境與應用，讓開發者省去環境相依、服務安裝、排程設定、共享權限與安裝器等大量非功能性工作，把心力專注在業務邏輯；而運維則以標準化的 docker run/compose 介面控制網路、存儲與環境設定，輕鬆完成升版與擴展。本文完成了 WebAPI 與 Worker 的容器化與本機驗證；後續篇章將介紹 SDK 設計、Reverse Proxy 配置與 Docker Compose 的整合實務，持續完善整體微服務開發與部署體驗。

## 資訊整理

### 知識架構圖
1. 前置知識：
- 基本微服務觀念（單一職責、獨立部署、可擴展）
- Docker 基本操作（image、container、Dockerfile、run、logs）
- .NET Framework/ASP.NET Web API2 基礎
- Windows Container 與容器網路/Volume 映射概念
- 基本 CI/CD 概念（編譯、測試、發佈到 Registry/NuGet）

2. 核心概念：
- 容器驅動開發（Container Driven Development, CDD）：以容器運行與部署特性反向設計服務與程式結構
- 微服務拆分：WebAPI（查詢）、Worker（資料更新）、SDK（呼叫與快取）、Reverse Proxy（流量分配）
- 不可變基礎設施與映像檔：以 Dockerfile 定義可重建的運行環境與映像
- 執行期外部化配置與資源：以 Port、Volume、Env 控制連線、儲存與設定
- DevOps/CI-CD：自動化編譯、測試、製版、發佈（Docker Registry、NuGet）

3. 技術依賴：
- IP2C.WebAPI 依賴：ASP.NET WebAPI2、IP2C.NET 函式庫、IIS（microsoft/aspnet base image）、共享資料檔（Volume）
- IP2C.Worker 依賴：.NET Console、HTTP/GZip、IP2C.NET、檔案系統、排程邏輯、共享資料夾（Volume）
- IP2C.SDK 依賴：HTTP REST 呼叫、用戶端快取、NuGet 發佈
- CI/CD 依賴：Git（push 觸發）、建置/測試、Docker build/push、NuGet pack/push、Compose 部署
- 平台/基礎設施：Windows 10 Pro/Enterprise 或 Windows Server 2016（Windows Container）、Docker Engine、Registry、Azure（運行環境）

4. 應用場景：
- IP 所屬國家查詢微服務（高可用、水平擴展）
- 需定期更新的只讀查詢型服務（資料由 Worker 下載驗證後上線）
- 為外部開發者提供 SDK 的服務（簡化呼叫、提升 DX，並提供用戶端快取）
- 需要快速迭代、重建、跨環境一致運行的企業內部服務

### 學習路徑建議
1. 入門者路徑：
- 了解微服務與容器基本概念與優勢
- 動手寫最小 WebAPI，使用 microsoft/aspnet 建 Dockerfile，docker build/run/logs
- 練習 Volume 掛載與 Port 映射，觀察容器外部化資源
- 使用 IP2C.NET 本地查詢，串進 WebAPI（完成最小通路）

2. 進階者路徑：
- 開發 Worker 容器：排程邏輯、下載/解壓/驗證/回滾備援（.temp/.bak）
- 在本機以共享 Volume 讓 WebAPI 與 Worker 協同
- 導入 SDK：封裝 REST 呼叫與用戶端快取策略，打包 NuGet
- 撰寫 Dockerfile 最佳化（base image、層數、ENTRYPOINT/EXPOSE/VOLUME）

3. 實戰路徑：
- 設計 CI/CD：推送即建置、單元測試、Docker build/push、NuGet pack/push
- 使用 docker-compose 定義多服務與反向代理、健康檢查、環境變數
- 部署到雲端（如 Azure），擴展 WebAPI 實例並以 Reverse Proxy 做流量分配
- 監控與日誌：使用 docker logs 起步，逐步引入集中式日誌與度量

### 關鍵要點清單
- 容器驅動開發（CDD）：以容器運行特性反向影響架構與程式設計，減少非功能性樣板碼與運維耦合（優先級: 高）
- 微服務拆分：WebAPI/Worker/SDK/Reverse Proxy 明確職責分離，提升可維護與獨立部署能力（優先級: 高）
- Dockerfile 基礎：FROM/COPY/WORKDIR/EXPOSE/VOLUME/ENTRYPOINT 的正確使用與分層思維（優先級: 高）
- 執行期外部化：以 Port、Volume、Env 管理外部連線、資料與配置，將關注點從程式轉向部署（優先級: 高）
- 共享資料策略：用 Volume 在 WebAPI 與 Worker 間共享 ipdb.csv，簡化檔案分享與權限（優先級: 高）
- Worker 設計：定時下載、解壓、驗證（單元測試）、備份與原子替換，確保線上資料安全更新（優先級: 高）
- WebAPI 設計：輕量 REST 端點、快取與檔案監控（MemoryCache + HostFileChangeMonitor）（優先級: 中）
- SDK 與 DX：封裝 REST 呼叫與用戶端快取，NuGet 發佈，降低接入成本（優先級: 中）
- 日誌策略：以 stdout/Console 搭配 docker logs 起步，後續可導入集中式日誌（優先級: 中）
- CI/CD 流程：Push 觸發建置/測試，產出 Docker image 與 NuGet 套件，提升交付效率（優先級: 高）
- 映像基底選型：microsoft/aspnet 與 dotnet-framework base image 的取用與差異（優先級: 中）
- 反向代理與擴展：Reverse Proxy 分流 + 多個 WebAPI 實例達成 HA/Scale-out（優先級: 中）
- 本地到雲端一致性：相同映像在本機/雲端一致運行，簡化環境差異（優先級: 高）
- Docker 運行模式：前景/背景（-d）、互動模式、容器生命週期與服務化思維（優先級: 中）
- 安全與回滾：更新流程中的備份（.bak）、臨時檔（.temp）與驗證機制，降低風險（優先級: 中）