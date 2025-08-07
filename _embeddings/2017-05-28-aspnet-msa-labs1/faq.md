# 容器化的微服務開發 #1, IP查詢架構與開發範例

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是「Container Driven Development」？
作者自創的名詞，指的是從「容器」視角出發來設計與開發應用程式：  
1. 一開始就假設服務未來一定跑在 Docker／Container 環境；  
2. 程式碼、執行環境、相依項目全部封裝成可重複部署的 Image；  
3. 讓 DevOps、部署與擴充都以操作 Container 為核心，而非針對 OS 或實體機器做客製設定。

## Q: 這個「IP 查詢微服務」的核心需求有哪些？
1. 高可用性（High Availability）與可水平擴充（Scalability）  
2. IP 資料庫自動更新  
3. 提供用戶端 SDK，並在 SDK 內建 Client-side Cache  
4. 良好的 DX（Developer Experience），讓開發者容易整合與使用

## Q: 作者規劃的整體架構包含哪些元件？各自職責是什麼？
1. Reverse Proxy：負責 Load-balancing，將流量分配到多個 WebAPI 實例。  
2. IP2C.WebAPI：ASP.NET WebAPI，對外提供 `/api/ip2c/{ipValue}` 的 REST 查詢。  
3. IP2C.Worker：背景排程程式，定期下載並驗證最新的 IP 資料檔，更新至共用儲存體。  
4. Shared Storage (Volume)：存放 `ipdb.csv`，由 Worker 寫入，WebAPI 讀取。  
5. IP2C.SDK：供其他 .NET 專案呼叫 WebAPI 的 NuGet 套件，並內建快取。  
6. CI/CD Pipeline：編譯、單元測試、產生 Docker Image／NuGet Package，並推送至 Registry / Server。

## Q: IP2C.WebAPI 的查詢網址格式與回傳 JSON 為何？
• 查詢網址：`/api/ip2c/{ipv4 的 4 byte 轉成的 int 數值}`  
  例：8.8.8.8 → 0x08080808 → 134744072 → `/api/ip2c/134744072`  
• 回傳範例：  
```json
{
  "CountryName": "United States",
  "CountryCode": "US"
}
```

## Q: IP2C.Worker 具體做哪些事？
1. 以固定週期（範例每 3 分鐘）下載官方提供的 `.gz` 版 IP 資料檔。  
2. 解壓縮成 `ipdb.csv`，並以 IP2C.NET 進行基本單元測試驗證正確性。  
3. 測試通過後備份舊檔 (`ipdb.bak`)，再以新檔替換。  
4. 全程僅以 `Console.WriteLine` 輸出 Log，方便用 `docker logs` 直接閱讀。  
5. 以容器 daemon 方式執行，省去撰寫 Windows Service 或排程設定。

## Q: 使用 Docker 容器化對開發者最大的好處是什麼？
• 不必處理 IIS、Windows Service、排程器等繁雜設定；  
• 「程式 + 執行環境」一次打包，避免「在我電腦上正常」的環境落差；  
• 建置、測試、部署全流程可自動化（CI/CD）；  
• 共享 Volume、Port 映射、環境變數皆由部署人員在 `docker run` 時決定，開發者無需額外寫 Code 支援。

## Q: 要在本機同時啟動 WebAPI 與 Worker，並共享同一份資料檔，指令怎麼下？
```dos
md d:\data

docker run -d -p 8000:80 ^
  -v d:\data:c:/inetpub/wwwroot/App_Data ip2c/webapi

docker run -d ^
  -v d:\data:c:/IP2C.Worker/data ip2c/worker
```
說明：兩個 `-v` 參數把主機 `d:\data` 同時掛到兩個 Container 內不同路徑，達成檔案共享。

## Q: 要查看背景 Container 的執行紀錄該怎麼做？
使用 `docker logs <container-id>`，即可讀取該 Container 透過 `Console.WriteLine` 輸出的標準輸出／錯誤。

## Q: 為什麼容器能解決「在我電腦上沒問題」的老問題？
因為 Docker Image 已把 OS 版本、Runtime、依賴套件與應用程式一併封裝並版本化，  
部署到任何支援 Docker 的環境都以相同快照啟動，大幅減少環境不一致造成的錯誤。

## Q: 本系列下一篇將介紹什麼？
作者預告下一篇會說明：  
1. SDK 的實作與封裝方式  
2. Reverse Proxy 的設定  
3. Docker Compose 在多服務協調部署上的應用