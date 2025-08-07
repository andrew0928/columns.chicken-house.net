# 容器化的微服務開發 #1：IP 查詢架構與開發範例

## 摘要提示
- 微服務概念：服務需「小而專」、可獨立部署並支援 HA/Scale-out。  
- Container Driven Development：以「容器優先」思維設計程式與部署流程。  
- IP2C 服務架構：由 Reverse Proxy、WebAPI、Worker、SDK 四部分組成。  
- Windows Container + .NET：示範在 Windows Container 上開發 ASP.NET WebAPI 與 Console Worker。  
- 自動更新資料：Worker 週期性下載並驗證最新 IP 資料庫，確保查詢正確性。  
- Client SDK：提供封裝呼叫與快取機制，提升 DX 並減少頻繁存取。  
- DevOps 流程：CI 編譯→單元測試→製作 Docker Image / NuGet Package→Compose 部署。  
- Volume 共用：利用 Docker volume 讓多個 Container 共用 IP 資料檔，簡化網路磁碟權限問題。  
- 本機測試：單機即可用 docker run／compose 模擬完整服務，享受「寫完就跑」。  
- 開發體驗提升：容器把執行環境與部署細節抽象化，開發者專注商業邏輯，不再寫多餘的 Service／Installer Code。  

## 全文重點
作者以「IP 查詢來源國家」為範例，示範如何把一組原本僅由程式庫與批次腳本構成的小功能，升級為「可獨立運作且易於擴充」的微服務。在 Container Driven Development 的理念下，整個系統被拆分為數個互不相依、可獨立部署的服務：  
1. IP2C.WebAPI：核心查詢服務，負責接收 REST 呼叫並回傳國家代碼與名稱。  
2. IP2C.Worker：背景程序，定期從官方網站下載最新 IP-to-Country CSV，解壓並測試，通過後覆寫共享資料夾。  
3. 反向 Proxy (範例中以 Nginx / IIS ARR 為例)：統一入口，負責負載平衡與服務發現。  
4. IP2C.SDK：封裝呼叫邏輯並加入用戶端快取，方便開發者直接透過 NuGet 取得與使用。

在開發層面，作者選擇 Windows Container + .NET Framework，一來沿用既有 C# 程式碼，二來展示在 Windows 平台也能享受與 Linux 相同的容器化體驗。WebAPI 與 Worker 都用極簡 Dockerfile 打包：  
• WebAPI 基於 microsoft/aspnet Image，載入編譯後的站台檔並開放 80 Port。  
• Worker 基於 microsoft/dotnet-framework Image，COPY 後直接以 Console 模式作為 ENTRYPOINT。  

建置流程透過 build.cmd 完成：程式碼 Push 到 Git 觸發 CI；MSBuild 編譯與單元測試通過後，WebAPI 與 Worker 製成 Image 推上 Registry，SDK 打成 NuGet 並上傳；最後用 docker-compose 將多個 Instance 與 Proxy 一次佈署。

在本機測試階段，開發者只需：  
• docker run -d -p 8000:80 -v d:\data:... ip2c/webapi  
• docker run -d ‑v d:\data:... ip2c/worker  
即可讓兩支服務共用同一份 ipdb.csv，Worker 下載後立即被 WebAPI 使用；log 以 docker logs 直接查看，毋須安裝 Windows Service 或排程器。整個過程凸顯容器的幾項優勢：  
• 一致的執行環境：減少「在我電腦可以跑」的問題。  
• 部署與擴充簡化：同一份 Image 可在單機、Swarm、K8s 隨處橫移。  
• 避免重複造輪：不必再寫 Installer、Service Host、排程設定等雜務碼。  
• 開發與運維邊界明確：Developer 做 Image，IT/DevOps 決定 Port、Volume、Env。  

作者最後提醒：本文尚未涵蓋 Reverse Proxy 與 Compose 佈署細節，下一篇將補完 SDK、Proxy 與更完整的 Docker Compose 操作，進一步體驗容器化微服務在雲端環境中的實戰威力。

## 段落重點
### 容器驅動開發 (Container Driven Development)
作者先破題指出，以往談微服務多著重「把舊應用包進容器」，較少從「一開始就為容器而寫」的開發者視角切入。因此提出「Container Driven Development」概念：在設計程式時，就把部署目標鎖定為 Container，反向推導出系統拆分、資料流、共用資源與 DevOps 流程。以 IP 查詢為例，需求包含高可用、自動更新、提供 SDK 與良好 DX，於是產生 WebAPI、Worker、SDK 等角色；接著再思考哪部件需要 Volume、哪部件要可水平擴充，並用 Docker 標準化這些行為。此方法讓開發、測試、部署皆沿用相同 Artefact，降低環境差異並提高維運效率。

### 建立微服務 Solution: IP2C
專案結構以多個獨立 Project 組成單一 Solution：IP2C.NET Library 與其 Test、IP2C.WebAPI、IP2C.Worker、IP2C.SDK，再加 build.cmd 與 docker-compose.yml。build.cmd 負責編譯、跑測試、製作 Image/Package；compose 準備部署定義。如此拆分的好處是模組邊界清晰，各子服務可依職責獨立演進；且藉由 CI/CD Pipeline，把「程式碼 → 可部署 Artefact」完全自動化，讓開發者專注商業邏輯而非環境建置。

### Project: IP2C.WebAPI
WebAPI 用 ASP.NET WebAPI2 撰寫，唯一責任是在 /api/ip2c/{ipv4-int} 回傳國家名稱與代碼。資料載入採 MemoryCache＋HostFileChangeMonitor，偵測 ipdb.csv 一被覆寫就自動重新載入；這樣 WebAPI 不需重開即可使用新資料。Dockerfile 僅 four 行：FROM microsoft/aspnet、WORKDIR、COPY、EXPOSE＆VOLUME，即刻把程式與執行環境打包。透過 docker build && docker run -p 8000:80，即能在任何啟用 Windows Container 的機器啟動服務，完全不需 IIS/Express 的手動安裝。

### Project: IP2C.Worker
Worker 是單純 Console App，啟動後每三分鐘下載官方 .gz、解壓成 .csv，跑簡易測試通過才覆蓋舊檔；同時 Console.WriteLine 即是 Log。Dockerfile 同樣簡潔，ENTRYPOINT 直接執行可執行檔。因 Container 天生就是 Daemon，只要 docker run -d 就能變成背景服務，log 用 docker logs 即可調閱，省去撰寫 Windows Service、排程及 Installer 的所有繁瑣程式。共享資料則透過 Volume 對映到 Host Folder，讓 Worker 與多個 WebAPI Instance 同時存取。

### Test Run: IP2C Services (WebAPI + Worker) on Local PC
作者示範在本機創建 d:\data，分別把該資料夾掛進 WebAPI 與 Worker。Worker 每次更新 ipdb.csv，WebAPI 立即讀到最新檔。開發者可用瀏覽器呼叫 http://localhost:8000/api/ip2c/134744072 測試 8.8.8.8；再透過 docker exec 進入 Container 察看檔案或 docker logs 查閱執行紀錄。過程中沒有額外帳號、ACL、網路磁碟設定，Volume 直接呈現共享效果。此例清楚說明：在 Container 世界裡，擴充或搬移服務只需關注 Port/Volume/Env 三元素，其餘由 Docker 處理。

### 小結
藉由本篇 Hands-On，讀者可體會容器化對開發者的吸引力：它大幅降低服務拆分、測試與部署的門檻，讓「程式 = Image」成為事實；而運維人員也可用相同 Artefact 依需求水平擴充、滾動更新或回溯版本。作者預告下一篇將進一步補完 SDK、Reverse Proxy 與 docker-compose 實戰，讓整體架構全面雲端化。