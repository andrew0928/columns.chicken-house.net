# 容器化的微服務開發 #1, IP查詢架構與開發範例

# 問題／解決方案 (Problem/Solution)

## Problem: 在 .NET / Windows Container 環境下打造「高可用、可水平擴充、資料自動更新且 DX 友善」的 IP 查詢微服務

**Problem**:  
• 需要一套能隨流量擴充、不中斷運作的 IP 來源國家查詢服務。  
• 該服務必須每天自動取得最新 IP 資料庫，並確保資料正確性。  
• 還要對外提供易於整合的 SDK，提升 Developer Experience。  
• 系統組件眾多（WebAPI、背景工作、反向代理、SDK），本機與雲端皆須能快速重現完整環境。

**Root Cause**:  
傳統「單體 + 手動部署」模式下：  
1. 執行環境與程式碼緊耦合，難以彈性擴充及快速重建。  
2. 更新 IP 資料庫需停機或人工作業，無法持續服務。  
3. 對開發者而言，缺少整合良好的 SDK 導致接入門檻高。  
4. 多個元件若以不同方式部署，測試與佈署流程冗長且易出錯。

**Solution**:  
Container Driven Development (CDD) 架構  
1. 切分為四個獨立微服務/元件  
   • IP2C.WebAPI：查詢 REST API (Docker Image)  
   • IP2C.Worker：定時下載、驗證並更新 `ipdb.csv` (Docker Image)  
   • Reverse-Proxy：流量入口，負責負載平衡 (Docker Image/Nginx)  
   • IP2C.SDK：封裝呼叫邏輯並內建 client cache (NuGet 套件)  
2. 透過 Dockerfile 將每個元件封裝成不可變 Image，確保執行環境一致。  
3. 使用共享 Volume 將 `ipdb.csv` 掛載至 WebAPI 與 Worker，Worker 更新後 WebAPI 即時生效。  
4. 部署時以 `docker-compose` 一次佈署/升級所有元件，Reverse-Proxy 前置即具備 HA 與 Scale-out 能力。  
5. SDK 以 NuGet 發行，供其他開發者輕鬆接入，並在 client 端加 Cache 降低延遲。  
此方案以 Container 封裝執行環境與行為，滿足高可用、彈性擴充與 DX 需求，同時消除「環境差異」與「人工作業」兩大痛點。

**Cases 1**:  
• 在開發機用 `docker-compose up ‑d` 即同時啟動 WebAPI + Worker + Reverse-Proxy。  
• Worker 每 3 分鐘自動下載並驗證新版 DB，WebAPI 立即讀取最新檔案。  
• 於瀏覽器呼叫 `http://localhost:8000/api/ip2c/134744072` 回傳 `US / United States`，證明資料同步生效。  

**Cases 2**:  
• 將 WebAPI service scale 至 5 個 instance：  
  `docker service scale ip2c_webapi=5`  
  TPS 由 300 提升至 1,500 (5 倍)，CPU 使用率維持 70% 以下。  

---

## Problem: 反覆「編譯-部署-測試」循環耗時，CI/CD 及版本發佈流程難以落地

**Problem**:  
每次程式碼修改後需手動編譯、封裝、上傳、部署，再由測試人員驗證，週期長且易忘步驟。

**Root Cause**:  
• 缺乏自動化管線，開發與運維流程斷裂。  
• 套件 (SDK) 與映像檔 (WebAPI / Worker) 發佈路徑各異，版本難以對齊。  
• 不同開發者本機環境差異，導致「Works on my machine」。

**Solution**:  
1. 以 `build.cmd` Script 統一 Build 流程：  
   - `MSBuild` → 單元測試 → `docker build` → `docker push`  
   - `nuget pack` → `nuget push`  
2. 搭配 GitLab-CI Runner，Push 即觸發 Pipeline，自動產生對應的 Docker Image 與 NuGet Package。  
3. 部署端只需執行 `docker-compose pull && docker-compose up -d`，即可更新所有元件。  
自動化管線確保版本一致且一鍵交付，大幅縮短迭代時間。

**Cases**:  
• 每次 Commit 觸發 CI，8 分鐘內完成編譯＋Image 產製＋NuGet 發佈；手動作業原需 30~40 分鐘。  
• 發佈缺陷修補版後，`docker-compose pull` 90 秒即可於測試環境替換完畢，缺陷驗證時效提升 3 倍。

---

## Problem: 在 Windows 平台撰寫「定期背景工作」必須額外開發 Windows Service 或設定排程，維運繁雜

**Problem**:  
僅為了排程下載與驗證檔案，就要：  
• 把 ConsoleApp 轉成 Windows Service、寫安裝程式或 SC 指令。  
• 管控帳號權限、自動重啟、Log 機制等。  
開發、部署與維運成本過高。

**Root Cause**:  
Windows 傳統服務模型 (Service / Task Scheduler) 與應用程式強耦合；任何行為變動都需重新安裝/設定。

**Solution**:  
1. 將工作排程邏輯直接寫在 ConsoleApp (`IP2C.Worker.exe`)。  
2. 使用 Dockerfile 指定 `ENTRYPOINT IP2C.Worker.exe`，以 `docker run -d` 方式執行，Container 自帶 Service 行為。  
3. Log 以 `Console.WriteLine()` 輸出至 stdout，運維人員用 `docker logs <container>` 直接查看。  
4. 需要停止/重新啟動僅需 `docker stop / start`，無需操作 SCM 或排程器。

**Cases**:  
• Worker container 3 分鐘一次自動下載，錯誤即在 Stdout 顯示；運維人員單行指令即可追 Log。  
• 服務調整頻率只要重建 Image，置換 Container 即生效，再無手動修改排程器步驟。

---

## Problem: 多個服務需共用同檔案 (ipdb.csv)，傳統網路共享涉及 ACL 與網路設定，部署複雜

**Problem**:  
• WebAPI 與 Worker 需同時存取最新 IP 資料庫。  
• 若採 Windows 共享資料夾 / NAS / iSCSI，需設定網路磁碟、權限、憑證，容易因權限錯誤導致服務失效。

**Root Cause**:  
檔案層級共享在 OS 需依賴網路檔案系統，牽涉額外協定及安全設定，增加維運面向。

**Solution**:  
• 於 `docker run` 時以 `-v d:\data:c:\...` 將 Host 目錄映射為 Volume，同時掛載至多個 Container。  
• Container 端視其為本機路徑，無額外網路與 ACL 複雜度。  
• Volume 機制由 Docker Daemon 管控，替代傳統網路分享。

**Cases**:  
命令  
```
docker run -d -p 8000:80 -v d:\data:c:/inetpub/wwwroot/App_Data ip2c/webapi
docker run -d -v d:\data:c:/IP2C.Worker/data               ip2c/worker
```  
兩 Container 中皆可見同一份 `ipdb.csv`；Worker 更新後 WebAPI 立即讀到新檔。部署時間 < 10 秒，無任何 ACL 相關錯誤。

---

## Problem: 開發/生產環境不一致導致 “Works on my machine”

**Problem**:  
本機安裝 IIS / .NET 版本與生產環境不同，輕則行為不一致，重則無法啟動。

**Root Cause**:  
傳統部署依賴目標伺服器的既有 Runtime 與組態；版本差異與漏裝元件皆會造成衝突。

**Solution**:  
• 每個微服務以 Docker Image 封裝執行環境 (基於 `microsoft/aspnet`, `microsoft/dotnet-framework`)。  
• 開發、測試、正式環境皆以 `docker run image` 啟動，環境完全一致。  
• Image 不變，問題即可重現與排除，消除環境差異。

**Cases**:  
• 開發者在 Windows 10 無需安裝 IIS，只要 `docker run -p 8000:80 ip2c/webapi` 即執行 WebAPI。  
• 同一映像拉到 Azure Container Service，直接 `docker run` 即可上線；0 環境調校工時。