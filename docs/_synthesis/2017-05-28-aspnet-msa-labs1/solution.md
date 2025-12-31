---
layout: synthesis
title: "容器化的微服務開發 #1, IP查詢架構與開發範例"
synthesis_type: solution
source_post: /2017/05/28/aspnet-msa-labs1/
redirect_from:
  - /2017/05/28/aspnet-msa-labs1/solution/
postid: 2017-05-28-aspnet-msa-labs1
---

以下內容依據原文情境抽取，整理為 16 個可教學、可實作、可評估的解決方案案例。每個案例包含問題、根因、解法、程式碼/設定、實測與學習要點，便於在實戰教學、專案練習與能力評估中使用。

## Case #1: 從需求出發的容器驅動微服務拆分設計

### Problem Statement（問題陳述）
業務場景：看似單純的「IP 所屬國家查詢」服務，實際上要達到高可用可擴充、資料自動更新、提供易用 SDK 與良好 DX。若只做一支 API，無法同時滿足營運穩定性、資料新鮮度與開發者體驗。
技術挑戰：如何以微服務與容器思維，拆分出能獨立運作、可水平擴充且維運簡單的服務組合。
影響範圍：服務可用性、擴展性、資料時效、開發者採用度與維運負擔。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單體 API 難以兼顧查詢負載與資料更新，職責相互干擾。
2. 人工更新資料檔成本高、風險大，且無法保證一致性。
3. 缺少 SDK 與快取策略，導致重複查詢、延遲與成本增加。

深層原因：
- 架構層面：未釐清職責邊界（查詢與更新混在同一進程）。
- 技術層面：缺少容器化標準化環境與部署模式。
- 流程層面：缺乏 CI/CD 與自動化，導致頻繁手動介入。

### Solution Design（解決方案設計）
解決策略：依職責拆分為 WebAPI（查詢）、Worker（資料更新）、Reverse Proxy（前端流量分發）、共享儲存（資料檔）、Client SDK（開發者整合與客戶端快取），全部容器化，透過標準化映像檔與部署介面（port、volume、env）組裝。

實施步驟：
1. 微服務邊界定義
- 實作細節：拆分 API 與更新程序；Reverse Proxy 前置；共享資料夾供讀取。
- 所需資源：設計圖、ADR（Architecture Decision Record）。
- 預估時間：0.5 天

2. 容器化標準化
- 實作細節：為 WebAPI/Worker 撰寫 Dockerfile，定義 EXPOSE/VOLUME/ENTRYPOINT。
- 所需資源：Docker Engine（Windows Container）。
- 預估時間：0.5 天

3. 部署與驗證
- 實作細節：以 -p/-v 參數組裝服務；端到端驗證。
- 所需資源：本機/雲端節點、共享資料夾。
- 預估時間：0.5 天

關鍵程式碼/設定：
```dos
:: 啟動 WebAPI 與 Worker 並共享資料夾
docker run -d -p 8000:80 -v d:\data:c:/inetpub/wwwroot/App_Data ip2c/webapi
docker run -d -v d:\data:c:/IP2C.Worker/data ip2c/worker
```

實際案例：文章中以 Reverse Proxy + 多個 IP2C.WebAPI（HA/Scale）+ IP2C.Worker（自動更新）+ 共享資料夾 + SDK（含 client cache）設計。
實作環境：Windows 10 Pro/Server 2016、Windows Containers、.NET Framework、ASP.NET WebAPI2、Docker。
實測數據：
改善前：單體 API，更新與查詢耦合，難以水平擴充。
改善後：獨立微服務配合容器化部署，達成 HA 與資料自動更新。
改善幅度：職責清晰，擴展與維運難度顯著下降（質性提升）。

Learning Points（學習要點）
核心知識點：
- 容器驅動開發（CDD）拆分思維
- 以共享卷（Volume）解耦讀寫職責
- SDK 與快取設計提升 DX 與效能

技能要求：
- 必備技能：Docker 基礎、REST 設計、.NET 基礎
- 進階技能：微服務邊界劃分、部署拓樸設計

延伸思考：
- 可應用於其他查詢型服務（地理資料、黑名單等）
- 限制：共享檔案為單點；需考慮分散式存儲
- 優化：以物件儲存、CDN 或分散式 KV 取代檔案共享

Practice Exercise（練習題）
- 基礎練習：畫出自己的微服務拆分圖（30 分鐘）
- 進階練習：用 Docker 組裝 2 服務 + 共享卷雛形（2 小時）
- 專案練習：完成 IP2C 全套（WebAPI/Worker/Reverse Proxy/SDK）（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：服務可獨立運作且協作良好
- 程式碼品質（30%）：模組邊界清晰，設定外部化
- 效能優化（20%）：查詢延遲與資源用量合理
- 創新性（10%）：提出更彈性的儲存與快取策略


## Case #2: ASP.NET WebAPI 容器化，移除本機 IIS 依賴

### Problem Statement（問題陳述）
業務場景：開發團隊需要快速在本機與多環境驗證 IP 查詢 API，但若依賴各環境的 IIS 安裝與設定，繁瑣且不一致，增加測試與部署成本。
技術挑戰：以容器方式封裝 ASP.NET 執行環境與應用，讓開發/測試/部署一體化。
影響範圍：建置時間、環境一致性、部署速度與風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. IIS/ASP.NET 執行環境安裝成本高且易不一致。
2. 手動發佈與檔案拷貝容易出錯。
3. 回滾與重現舊版困難。

深層原因：
- 架構層面：未將執行環境與應用封裝為不可變映像。
- 技術層面：缺少 Dockerfile 與映像建置流程。
- 流程層面：缺少自動化建置與發佈脚本。

### Solution Design（解決方案設計）
解決策略：以 microsoft/aspnet 為基底，COPY 發佈輸出，EXPOSE 80，宣告 App_Data 為 VOLUME，藉由 docker build/run 完成一致環境與可重現部署。

實施步驟：
1. 建置輸出產生
- 實作細節：MSBuild 產生 Web Deploy 封裝/發佈輸出。
- 所需資源：MSBuild、.NET SDK。
- 預估時間：0.5 小時

2. 撰寫 Dockerfile
- 實作細節：FROM microsoft/aspnet，COPY 到 inetpub/wwwroot，EXPOSE 80，VOLUME App_Data。
- 所需資源：Docker Desktop（Windows）。
- 預估時間：0.5 小時

3. 建置與啟動
- 實作細節：docker build -t ip2c/webapi；docker run -p 8000:80。
- 所需資源：本機 Docker。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```dockerfile
FROM microsoft/aspnet
WORKDIR c:/inetpub/wwwroot/
COPY . .
EXPOSE 80
VOLUME ["c:/inetpub/wwwroot/App_Data"]
```

實際案例：文章提供 Dockerfile 並以 docker run -p 8000:80 啟動，不需在本機安裝 IIS。
實作環境：Windows 容器、ASP.NET WebAPI2。
實測數據：
改善前：需安裝/設定 IIS，流程多步驟。
改善後：docker build/run，數秒內啟動。
改善幅度：建置與部署體驗明顯簡化（質性）。

Learning Points（學習要點）
核心知識點：
- Dockerfile 基本指令（FROM/COPY/EXPOSE/VOLUME）
- Web 應用的容器化
- 發佈輸出與映像關係

技能要求：
- 必備技能：ASP.NET 發佈、Docker 基礎
- 進階技能：分層映像與快取最佳化

延伸思考：
- 可應用於任何 .NET Framework WebApp
- 風險：App_Data 持久化與安全性
- 優化：多階段建置、CI 接入

Practice Exercise（練習題）
- 基礎練習：將範例 WebAPI 容器化並對外露出 8000（30 分鐘）
- 進階練習：加入 Health Check 與環境變數設定（2 小時）
- 專案練習：擴充成多環境（dev/test/prod）映像產出（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：容器可啟動並回應 API
- 程式碼品質：Dockerfile 清晰、最少指令
- 效能優化：建置快取合理利用
- 創新性：加入建置最佳化技巧


## Case #3: 不重啟服務的資料檔熱更新（MemoryCache + File Change Monitor）

### Problem Statement（問題陳述）
業務場景：IP 查詢 API 需使用 12MB CSV 資料檔，且會定期更新。若每次更新都重啟服務或重新載入整站，影響可用性與效能。
技術挑戰：在不重啟服務情況下，偵測檔案變更並熱更新記憶體索引。
影響範圍：查詢延遲、可用性、更新時段穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 檔案更新與應用程序生命週期耦合。
2. 缺少變更監控導致記憶體資料過期。
3. 手動重啟造成短暫中斷。

深層原因：
- 架構層面：未設計讀寫分離與熱更新機制。
- 技術層面：未利用快取與檔案變更監視。
- 流程層面：更新策略未標準化。

### Solution Design（解決方案設計）
解決策略：以 MemoryCache 快取 IPCountryFinder，搭配 HostFileChangeMonitor 監看 ipdb.csv；檔案變更時自動失效並重建快取，達成熱更新。

實施步驟：
1. 建立快取載入器
- 實作細節：首次請求載入資料；以檔案監視器設定失效。
- 所需資源：System.Runtime.Caching。
- 預估時間：0.5 小時

2. 實作 File Change Monitor
- 實作細節：HostFileChangeMonitor 監看 App_Data/ipdb.csv。
- 所需資源：.NET Framework。
- 預估時間：0.5 小時

3. 驗證熱更新
- 實作細節：由 Worker 更新檔案後，API 端自動載入新資料。
- 所需資源：Worker 容器、共享卷。
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
private IPCountryFinder LoadIPDB()
{
    string cachekey = "storage:ip2c";
    var result = MemoryCache.Default.Get(cachekey) as IPCountryFinder;
    if (result == null)
    {
        string filepath = HostingEnvironment.MapPath("~/App_Data/ipdb.csv");
        var cip = new CacheItemPolicy();
        cip.ChangeMonitors.Add(new HostFileChangeMonitor(new List<string>{ filepath }));
        result = new IPCountryFinder(filepath);
        MemoryCache.Default.Add(cachekey, result, cip);
    }
    return result;
}
```

實際案例：WebAPI 以 MemoryCache + HostFileChangeMonitor 監看 App_Data/ipdb.csv；Worker 更新檔案後 API 熱更新。
實作環境：ASP.NET WebAPI2、.NET Framework。
實測數據：
改善前：更新需重啟或手動 reload。
改善後：檔案更新後自動換新快取，無須重啟。
改善幅度：可用性提升（質性），更新窗口零中斷。

Learning Points（學習要點）
核心知識點：
- MemoryCache 與變更監控
- 資料熱更新設計
- 讀寫分離的落地實務

技能要求：
- 必備技能：ASP.NET WebAPI、.NET 快取 API
- 進階技能：熱更新與一致性策略

延伸思考：
- 可應用於任何基於檔案的索引
- 風險：大型檔案載入記憶體壓力
- 優化：索引增量更新、分片

Practice Exercise（練習題）
- 基礎練習：改寫範例以監看另一個檔案（30 分鐘）
- 進階練習：加入快取統計與健康檢查端點（2 小時）
- 專案練習：設計可插拔的索引供應器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：檔案變更即時生效
- 程式碼品質：清晰、低耦合
- 效能優化：載入延遲可接受
- 創新性：提出增量/分片方案


## Case #4: 無排程器的容器內排程（長駐 Console + ENTRYPOINT）

### Problem Statement（問題陳述）
業務場景：需要固定頻率（例如每三分鐘）抓取並更新 IP 資料檔。傳統做法需安裝 Windows Service 或排程器，安裝維護麻煩。
技術挑戰：如何在容器中以最小代價實作長駐、可控的排程程序。
影響範圍：維運複雜度、可靠性、可觀測性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Windows Service/排程器帶來額外安裝與維護負擔。
2. 容器環境中傳統模式不必要且反模式。
3. 缺乏統一的啟停與健康探測介面。

深層原因：
- 架構層面：未將服務視為容器進程（PID 1）。
- 技術層面：未善用 ENTRYPOINT/daemon 模式。
- 流程層面：啟停與監控未標準化。

### Solution Design（解決方案設計）
解決策略：撰寫長駐 Console App，內部以 while + Task.Delay 週期觸發更新；Dockerfile 使用 ENTRYPOINT；以 docker run -d 背景執行並用 docker logs 觀測。

實施步驟：
1. 排程主迴圈
- 實作細節：基於基準時間計算下一次觸發間隔，避免漂移。
- 所需資源：.NET Console。
- 預估時間：0.5 小時

2. 容器化
- 實作細節：Dockerfile 設定 ENTRYPOINT 指向可執行檔。
- 所需資源：Windows 容器。
- 預估時間：0.5 小時

3. 背景執行與監控
- 實作細節：docker run -d 與 docker logs。
- 所需資源：Docker CLI。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
while (true)
{
    TimeSpan wait = TimeSpan.FromMilliseconds(
        period.TotalMilliseconds - (DateTime.Now - start).TotalMilliseconds % period.TotalMilliseconds);
    Console.WriteLine("wait: {0} (until: {1})", wait, DateTime.Now.Add(wait));
    Task.Delay(wait).Wait();
    UpdateFile(@"http://software77.net/geo-ip/?DL=1", filepath);
}
```
```dockerfile
FROM microsoft/dotnet-framework:latest
WORKDIR c:/IP2C.Worker
COPY . .
VOLUME ["c:/IP2C.Worker/data"]
ENTRYPOINT IP2C.Worker.exe
```

實際案例：Worker 容器每三分鐘自動更新，訊息輸出至 stdout，運維以 docker logs 讀取。
實作環境：.NET Framework Console、Windows 容器。
實測數據：
改善前：需安裝服務或設定排程器。
改善後：一行 docker run -d 啟動即可。
改善幅度：安裝維護成本顯著下降（質性）。

Learning Points（學習要點）
核心知識點：
- 容器進程模型與 ENTRYPOINT
- 去排程器化的容器執行
- 漂移安全的週期計算

技能要求：
- 必備技能：Console App、Dockerfile
- 進階技能：健康檢查、重啟策略

延伸思考：
- 可應用於任何週期性工作
- 風險：單進程單點，可考慮副本與 backoff
- 優化：加入 retry/jitter、可配置化

Practice Exercise（練習題）
- 基礎練習：將任何 console 任務容器化並以 -d 方式運行（30 分鐘）
- 進階練習：增加 backoff + retry（2 小時）
- 專案練習：加入健康檢查與告警（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：可週期執行且持續運行
- 程式碼品質：簡潔健壯
- 效能優化：CPU/記憶體占用合理
- 創新性：提升容器可觀測性


## Case #5: 原子性更新 ipdb.csv，避免半成品讀取

### Problem Statement（問題陳述）
業務場景：資料更新過程若被 API 讀取到半成品（未下載完成或未驗證），將導致查詢錯誤或例外，影響可用性。
技術挑戰：確保下載、解壓、驗證後才進行替換，並保留備份以支援回退。
影響範圍：服務穩定性、資料一致性、回滾能力。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 直接覆蓋目標檔案，導致競態條件。
2. 缺乏更新前內容驗證。
3. 無備援檔案回退機制。

深層原因：
- 架構層面：讀寫未解耦與缺少原子替換策略。
- 技術層面：缺少 .temp/.bak 工作檔管理。
- 流程層面：缺乏更新管控與回復流程。

### Solution Design（解決方案設計）
解決策略：下載到 .temp → 驗證成功後將舊檔改名為 .bak → 將 .temp 原子移動為正式檔，失敗則保留舊檔。確保 API 永遠讀到有效檔案。

實施步驟：
1. 寫入隔離
- 實作細節：所有寫入先落至 .temp。
- 所需資源：檔案系統操作。
- 預估時間：0.5 小時

2. 驗證檔案
- 實作細節：用 IPCountryFinder 做樣本查詢驗證。
- 所需資源：IP2C.NET。
- 預估時間：0.5 小時

3. 原子替換與備份
- 實作細節：File.Move 實現原子替換，保留 .bak。
- 所需資源：.NET IO API。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
string temp = Path.ChangeExtension(file, ".temp");
string back = Path.ChangeExtension(file, ".bak");
if (DownloadAndExtractGZip(url, temp) && TestFile(temp))
{
    if (File.Exists(back)) File.Delete(back);
    if (File.Exists(file)) File.Move(file, back);
    File.Move(temp, file); // 原子替換
}
```

實際案例：Worker 以 .temp/.bak 工作檔實作更新並驗證成功後替換。
實作環境：.NET Framework、Windows 檔案系統。
實測數據：
改善前：可能讀到半成品，產生錯誤。
改善後：僅在驗證通過後替換，且有 .bak 回退。
改善幅度：一致性與可回復性大幅提升（質性）。

Learning Points（學習要點）
核心知識點：
- 原子替換與工作檔策略
- 更新前驗證（Contract Test）
- 回滾機制設計

技能要求：
- 必備技能：.NET IO、例外處理
- 進階技能：一致性策略、回復流程

延伸思考：
- 可應用於任何檔案型資料更新
- 風險：跨磁碟分割區 Move 非原子
- 優化：鎖定/檔案句柄協定

Practice Exercise（練習題）
- 基礎練習：為任意檔案更新加入 .temp/.bak 流程（30 分鐘）
- 進階練習：加入多筆驗證與回復報告（2 小時）
- 專案練習：對大型檔案實作分塊下載與原子合併（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：失敗不覆蓋、成功原子替換
- 程式碼品質：錯誤處理完備
- 效能優化：最小停頓時間
- 創新性：更安全的替換策略


## Case #6: 用 Docker Volume 共享資料，取代 SMB/ACL 繁瑣設定

### Problem Statement（問題陳述）
業務場景：WebAPI 與 Worker 必須共享資料檔。傳統用網路共享（SMB/ACL）設定繁雜且常遇權限問題，增加維運成本。
技術挑戰：以容器原生方式讓多服務安全共享檔案，並簡化部署。
影響範圍：部署複雜度、安全風險、可移植性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. SMB/ACL 管理繁重且易錯。
2. 多機共享需額外基礎設施與帳號管理。
3. 本地/雲端環境差異導致不可移植。

深層原因：
- 架構層面：未採用容器 Volume 標準化資料入口。
- 技術層面：缺乏 -v 綁定策略。
- 流程層面：缺少部署標準化腳本。

### Solution Design（解決方案設計）
解決策略：Host 資料夾綁定到多個容器內目錄（-v host:container），WebAPI 讀、Worker 寫。以 Docker 管理掛載，避免網路分享與 ACL 複雜性。

實施步驟：
1. 規劃資料夾與掛載點
- 實作細節：Host d:\data 對應到兩服務容器內資料夾。
- 所需資源：檔案系統。
- 預估時間：0.5 小時

2. 以 -v 綁定啟動容器
- 實作細節：兩條 docker run 均掛載相同 host 目錄。
- 所需資源：Docker CLI。
- 預估時間：0.5 小時

3. 驗證共享
- 實作細節：docker exec 進入容器確認檔案同步。
- 所需資源：命令列。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```dos
docker run -d -p 8000:80 -v d:\data:c:/inetpub/wwwroot/App_Data ip2c/webapi
docker run -d -v d:\data:c:/IP2C.Worker/data ip2c/worker
```

實際案例：文章以 d:\data 同時掛載至兩容器達成共享與即時更新。
實作環境：Windows 容器、Windows 檔案系統。
實測數據：
改善前：需設定共享與 ACL，常遇權限問題。
改善後：單純目錄綁定，部署與維運簡化。
改善幅度：維運負擔顯著降低（質性）。

Learning Points（學習要點）
核心知識點：
- Docker Volume/Bind Mount
- 讀寫職責分離
- 資料持久化策略

技能要求：
- 必備技能：Docker 基礎、檔案系統
- 進階技能：Volume 驗證、備份策略

延伸思考：
- 可替換為雲端檔案/物件儲存
- 風險：單機目錄非高可用
- 優化：分散式存儲與副本

Practice Exercise（練習題）
- 基礎練習：兩容器共享一檔案並驗證（30 分鐘）
- 進階練習：改為命名 Volume 並備份（2 小時）
- 專案練習：對接雲端檔案服務（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：兩容器可共享資料
- 程式碼品質：啟動腳本清晰
- 效能優化：I/O 運作正常
- 創新性：更先進的持久化方案


## Case #7: 容器化日誌：stdout + docker logs，免框架也可觀測

### Problem Statement（問題陳述）
業務場景：Worker 需記錄更新流程與錯誤。傳統引入 NLog/Log4Net 帶來設定成本，分散式讀取不便。
技術挑戰：以容器友善方式收集日誌，簡化設定並維持可觀測性。
影響範圍：問題診斷效率、維運成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 傳統日誌框架需額外設定與儲存目標。
2. 容器執行個體多，集中收集不易。
3. 本地/雲端設定差異。

深層原因：
- 架構層面：未採用容器標準輸出作為日誌入口。
- 技術層面：缺乏 docker logs、log driver 概念。
- 流程層面：日誌查詢與保留策略未定義。

### Solution Design（解決方案設計）
解決策略：Worker 直接 Console.WriteLine 輸出至 stdout，運維以 docker logs 讀取；後續可接 log driver/ELK/Cloud Logging。

實施步驟：
1. 輸出改為 stdout
- 實作細節：Console.WriteLine 記錄關鍵事件。
- 所需資源：.NET Console。
- 預估時間：0.25 小時

2. 啟動與查詢
- 實作細節：docker run -d 後用 docker logs <id>。
- 所需資源：Docker CLI。
- 預估時間：0.25 小時

3. 規劃保留與匯出
- 實作細節：後續配置 log driver/sidecar。
- 所需資源：Docker/ELK/Cloud。
- 預估時間：1 小時

關鍵程式碼/設定：
```dos
docker ps -a
docker logs <container-id>
```

實際案例：文章以 docker logs 直接查看 Worker 更新日誌與時間戳。
實作環境：Windows 容器、Docker CLI。
實測數據：
改善前：需額外配置日誌框架。
改善後：零設定可讀取，後續再擴展。
改善幅度：開發與維運成本降低（質性）。

Learning Points（學習要點）
核心知識點：
- 容器標準輸出作為日誌來源
- docker logs 與 log driver
- 可觀測性最小可行實踐

技能要求：
- 必備技能：Console/CLI
- 進階技能：集中式日誌方案整合

延伸思考：
- 適用所有容器化工作負載
- 風險：高流量需集中式方案
- 優化：結合結構化日誌（JSON）

Practice Exercise（練習題）
- 基礎練習：在 Worker 增加關鍵日誌並以 docker logs 檢視（30 分鐘）
- 進階練習：導出到 ELK/Cloud（2 小時）
- 專案練習：統一日誌格式與追蹤 ID（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：日誌可查可追
- 程式碼品質：最小侵入
- 效能優化：日誌量可控
- 創新性：集中式整合設計


## Case #8: Windows NAT loopback 限制下的本機測試策略

### Problem Statement（問題陳述）
業務場景：在 Windows 容器環境，本機以映射埠測試容器服務時，受 winnat 限制（不支援 NAT loopback），導致 Localhost 測試失敗。
技術挑戰：如何在開發機上成功存取容器內服務以進行驗證。
影響範圍：本機開發體驗、測試效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Windows NAT 既有限制，不支援 loopback。
2. 預期以 localhost:映射埠 測試失敗。
3. 缺乏替代存取方案。

深層原因：
- 架構層面：網路拓樸認知不足。
- 技術層面：未知 docker inspect 查詢容器 IP 方法。
- 流程層面：未形成測試操作準則。

### Solution Design（解決方案設計）
解決策略：透過 docker inspect 取得容器 NAT 後 IP，改以容器 IP:內部埠（80）存取；或在前方配置 Reverse Proxy/Port Proxy。

實施步驟：
1. 查詢容器 IP
- 實作細節：docker inspect -f 指令。
- 所需資源：Docker CLI。
- 預估時間：0.25 小時

2. 以容器 IP 測試
- 實作細節：瀏覽器/HTTP 工具直連容器 IP:80。
- 所需資源：Web 客戶端。
- 預估時間：0.25 小時

3. 制定指引
- 實作細節：在 README 記錄測試方式與限制。
- 所需資源：文件。
- 預估時間：0.25 小時

關鍵程式碼/設定：
```bash
# 取得容器 IP（nat 網路）
docker inspect -f "{{ .NetworkSettings.Networks.nat.IPAddress }}" <container-id>
# 以容器 IP 測試，例如 http://<container-ip>:80/api/ip2c/134744072
```

實際案例：文中提醒 winnat 不支援 loopback，需查容器 IP 測試。
實作環境：Windows 10/Server 2016、Docker for Windows（Windows Containers）。
實測數據：
改善前：localhost 測試失敗。
改善後：以容器 IP 成功測試。
改善幅度：本機測試可行性恢復（質性）。

Learning Points（學習要點）
核心知識點：
- Windows NAT 與容器網路
- docker inspect 用法
- 測試替代路徑

技能要求：
- 必備技能：Docker CLI
- 進階技能：本機代理/Reverse Proxy

延伸思考：
- 可在前方加反向代理解此痛點
- 風險：IP 變動需重查
- 優化：編寫 script 自動化查 IP

Practice Exercise（練習題）
- 基礎練習：取得容器 IP 並成功打 API（30 分鐘）
- 進階練習：以 Nginx 做本機轉發（2 小時）
- 專案練習：開發一鍵查 IP + 打測試工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：可在本機成功測試
- 程式碼品質：腳本可讀可維護
- 效能優化：測試流程簡潔
- 創新性：改善測試體驗方法


## Case #9: 端到端本機整合測試（WebAPI + Worker + 共享卷）

### Problem Statement（問題陳述）
業務場景：需在開發機上一次啟動 WebAPI 與 Worker，並驗證資料自動更新是否可被 API 即時讀到，確保整合流程正確。
技術挑戰：如何以最小手續完成端到端整合與驗證。
影響範圍：回歸測試效率、整體品質信心。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少標準啟動順序與共享卷設定。
2. 未驗證 API 端對更新檔的熱載入。
3. 測試環境與正式部署差異可能導致誤判。

深層原因：
- 架構層面：整合測試流程未定義。
- 技術層面：啟動命令與參數未標準化。
- 流程層面：缺少端到端檢查清單。

### Solution Design（解決方案設計）
解決策略：以兩條 docker run 指令啟動服務並掛載同一 host 資料夾；待 Worker 更新後以瀏覽器/工具測 API；以 docker logs 觀察更新循環。

實施步驟：
1. 準備共享資料夾
- 實作細節：md d:\data。
- 所需資源：檔案系統。
- 預估時間：5 分鐘

2. 啟動服務
- 實作細節：-p 8000:80 啟 API；兩者 -v 掛 d:\data。
- 所需資源：Docker。
- 預估時間：10 分鐘

3. 驗證整合
- 實作細節：等待一輪更新，打 http://localhost:8000/api/ip2c/134744072。
- 所需資源：瀏覽器/HTTP 客戶端。
- 預估時間：15 分鐘

關鍵程式碼/設定：
```dos
md d:\data
docker run -d -p 8000:80 -v d:\data:c:/inetpub/wwwroot/App_Data ip2c/webapi
docker run -d -v d:\data:c:/IP2C.Worker/data ip2c/worker
```

實際案例：文章示範啟動兩服務並成功從 API 讀到 Worker 更新之檔案。
實作環境：Windows 容器、.NET Framework。
實測數據：
改善前：缺少端到端驗證，問題晚期才暴露。
改善後：本機快速驗證，縮短迭代。
改善幅度：迭代速度與品質保證提升（質性）。

Learning Points（學習要點）
核心知識點：
- 端到端整合測試最小落地
- 共享卷與熱更新聯動
- 日誌輔助驗證

技能要求：
- 必備技能：Docker 操作
- 進階技能：測試腳本與驗證點設計

延伸思考：
- 可自動化為 CI 中的整合測試
- 風險：本機條件與雲端差異
- 優化：以 Compose 或腳本一鍵啟動

Practice Exercise（練習題）
- 基礎練習：依步驟完成本機端到端測試（30 分鐘）
- 進階練習：寫一個驗證腳本自動打 API（2 小時）
- 專案練習：將整合測試接入 CI Pipeline（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：端到端場景成功
- 程式碼品質：啟動腳本與驗證腳本清楚
- 效能優化：等待時間與重試策略合理
- 創新性：自動化程度


## Case #10: 前置 Reverse Proxy 實作負載平衡與高可用

### Problem Statement（問題陳述）
業務場景：IP 查詢 API 必須支援高併發與故障隔離，單一實例不足以承載或容錯，需要多副本與前置負載平衡。
技術挑戰：在容器環境下如何快速前置反向代理並將流量分配到多個 API 實例。
影響範圍：可用性、擴充性、容錯能力。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單實例成為瓶頸與單點故障。
2. 缺少流量分配策略與健康檢查。
3. 客戶端直連服務導致升級困難。

深層原因：
- 架構層面：未有前端閘道/反向代理。
- 技術層面：未配置負載演算法與健康探測。
- 流程層面：無滾動更新機制。

### Solution Design（解決方案設計）
解決策略：在前方配置 Reverse Proxy（如 Nginx/IIS ARR/NGINX for Windows），將請求分發到多個 WebAPI 容器實例，並引入健康檢查以實現容錯。

實施步驟：
1. 部署反向代理
- 實作細節：容器化或系統服務方式。
- 所需資源：Nginx/IIS ARR。
- 預估時間：1 小時

2. 配置後端池與健康檢查
- 實作細節：定義多個 WebAPI 實例位址。
- 所需資源：代理設定檔。
- 預估時間：1 小時

3. 壓測與故障演練
- 實作細節：模擬熔斷與節點下線。
- 所需資源：壓測工具。
- 預估時間：1 小時

關鍵程式碼/設定：
```nginx
upstream ip2c_api {
    server 172.20.0.11:80;
    server 172.20.0.12:80;
}
server {
    listen 80;
    location / {
        proxy_pass http://ip2c_api;
        proxy_connect_timeout 2s;
        proxy_read_timeout 5s;
    }
}
```

實際案例：文章提出以 Reverse Proxy 前置並水平擴充 WebAPI 實例。
實作環境：Windows 容器/主機 + 反向代理服務。
實測數據：
改善前：單點、無容錯。
改善後：多副本分流，具備容錯能力。
改善幅度：HA/Scale 能力顯著提升（質性）。

Learning Points（學習要點）
核心知識點：
- 反向代理與負載平衡
- 健康檢查與熔斷
- 水平擴充策略

技能要求：
- 必備技能：代理設定
- 進階技能：零停機發布、藍綠/金絲雀

延伸思考：
- 可替換為 API Gateway
- 風險：代理自身成為單點
- 優化：多層高可用與自動擴縮

Practice Exercise（練習題）
- 基礎練習：配置 Nginx 轉發兩個 WebAPI 副本（30 分鐘）
- 進階練習：加入健康檢查與熔斷（2 小時）
- 專案練習：實作滾動升級（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：負載均衡可用
- 程式碼品質：設定清晰
- 效能優化：延遲穩定
- 創新性：部署策略設計


## Case #11: Client SDK 與 Client-side Cache 降低重複查詢

### Problem Statement（問題陳述）
業務場景：第三方服務/前端應用頻繁查詢相同 IP，若每次都呼叫 API 將造成延遲與成本，且整合門檻高。
技術挑戰：提供易用 SDK 封裝呼叫並加入客戶端快取，降低重複請求與延遲。
影響範圍：延遲、流量、DX。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 重複請求相同 IP 沒有快取。
2. 開發者需重複撰寫呼叫程式與錯誤處理。
3. 缺少標準化重試與逾時策略。

深層原因：
- 架構層面：缺乏用戶端抽象層。
- 技術層面：沒有 TTL/快取淘汰策略。
- 流程層面：發佈/升級 SDK 管道缺失。

### Solution Design（解決方案設計）
解決策略：提供 .NET SDK，封裝 HttpClient 呼叫與錯誤處理；以 MemoryCache（或 ConcurrentDictionary + TTL）對相同 IP 結果做短期快取，減少 API 壓力。

實施步驟：
1. SDK 介面定義
- 實作細節：GetCountryAsync(ip)；錯誤回傳型別。
- 所需資源：Class Library。
- 預估時間：1 小時

2. 快取策略
- 實作細節：設定 TTL（例如 1~5 分鐘）、鍵值為 IP。
- 所需資源：MemoryCache/自製快取。
- 預估時間：1 小時

3. NuGet 包裝與發佈
- 實作細節：.nuspec/PackageReference，nuget push。
- 所需資源：NuGet Server。
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
public class Ip2cClient {
    private readonly HttpClient _http = new HttpClient{ Timeout = TimeSpan.FromSeconds(3)};
    private readonly MemoryCache _cache = MemoryCache.Default;
    private readonly CacheItemPolicy _policy = new CacheItemPolicy{ AbsoluteExpiration = DateTimeOffset.Now.AddMinutes(3)};
    private readonly string _baseUrl;
    public Ip2cClient(string baseUrl){ _baseUrl = baseUrl.TrimEnd('/'); }

    public async Task<(string CountryCode,string CountryName)> GetCountryAsync(string ipv4){
        if (_cache.Get(ipv4) is ValueTuple<string,string> hit) return hit;
        var rsp = await _http.GetAsync($"{_baseUrl}/api/ip2c/{IpToUInt32(ipv4)}");
        rsp.EnsureSuccessStatusCode();
        dynamic json = Newtonsoft.Json.Linq.JObject.Parse(await rsp.Content.ReadAsStringAsync());
        var val = ((string)json.CountryCode, (string)json.CountryName);
        _cache.Set(ipv4, val, _policy);
        return val;
    }
    private static uint IpToUInt32(string ip){ var s=ip.Split('.').Select(byte.Parse).ToArray(); return (uint)(s[0]<<24|s[1]<<16|s[2]<<8|s[3]); }
}
```

實際案例：文章提出提供 SDK 與 client-side cache 的設計（下一篇細述），此處給出實作範式。
實作環境：.NET Framework/.NET Standard。
實測數據：
改善前：重複查詢皆打 API。
改善後：熱點 IP 命中快取，降低延遲與流量。
改善幅度：命中率愈高收益愈大（質性）。

Learning Points（學習要點）
核心知識點：
- SDK 封裝與 DX
- 客戶端快取 TTL 策略
- 逾時/重試/錯誤處理

技能要求：
- 必備技能：HttpClient、NuGet
- 進階技能：快取政策與測評

延伸思考：
- 可提供多語言 SDK
- 風險：快取不一致/過期資料
- 優化：Etag/If-Modified-Since

Practice Exercise（練習題）
- 基礎練習：寫一個簡單 SDK 並快取結果（30 分鐘）
- 進階練習：加入重試與熔斷（2 小時）
- 專案練習：封裝成 NuGet 自動發佈（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：API 封裝可用、快取生效
- 程式碼品質：清晰 API 與錯誤處理
- 效能優化：命中率與延遲改善
- 創新性：更進階的快取/同步策略


## Case #12: CI/CD：GitLab Runner + build script + Registry/NuGet

### Problem Statement（問題陳述）
業務場景：服務需頻繁更新迭代，手動建置映像與 NuGet 發佈易錯且耗時，缺乏自動化。
技術挑戰：建立從提交到建置測試、映像產出、NuGet 包裝與部署的自動化管線。
影響範圍：交付速度、品質、一致性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 手動建置與發佈步驟多、不可重現。
2. 測試未自動化，品質風險高。
3. 部署決策與版本控管缺乏紀律。

深層原因：
- 架構層面：缺少標準化 pipeline。
- 技術層面：缺乏 build script 與 Runner。
- 流程層面：未定義發版節奏與核准機制。

### Solution Design（解決方案設計）
解決策略：提交觸發 CI → 編譯 + 單元測試 → build WebAPI/Worker 映像並推 Registry → SDK 打包 NuGet 並推送 → 決定上版時用 Compose/腳本部署。

實施步驟：
1. 建置腳本
- 實作細節：MSBuild 編譯、docker build/tag/push；nuget pack/push。
- 所需資源：build.cmd。
- 預估時間：1 小時

2. CI Runner 配置
- 實作細節：GitLab Runner 指向腳本。
- 所需資源：GitLab。
- 預估時間：1 小時

3. 部署腳本/Compose
- 實作細節：用拉取最新映像重啟服務。
- 所需資源：Registry、Deploy 節點。
- 預估時間：1 小時

關鍵程式碼/設定：
```dos
"c:\Program Files (x86)\MSBuild\14.0\Bin\MSBuild.exe" /p:Configuration=Release /p:DeployOnBuild=true
pushd .
cd IP2C.WebAPI\obj\Release\Package\PackageTmp
docker build -t ip2c/webapi:latest .
popd
:: 類似流程套用至 Worker；SDK 以 nuget pack/push
```

實際案例：文中使用 GitLab CI-Runner（本文略述）概念，示範以 build script 半自動發佈。
實作環境：GitLab、Docker Registry、NuGet Server。
實測數據：
改善前：手動建置與發佈。
改善後：提交觸發、自動產物、可重現。
改善幅度：交付速度與一致性大幅提升（質性）。

Learning Points（學習要點）
核心知識點：
- CI/CD pipeline 設計
- 容器映像與 NuGet 產物管理
- 發版與部署策略

技能要求：
- 必備技能：MSBuild、Docker CLI、NuGet
- 進階技能：CI/CD Orchestration

延伸思考：
- 可加入安全掃描與簽章
- 風險：Registry/NuGet 權限管理
- 優化：多階段流水線與快取

Practice Exercise（練習題）
- 基礎練習：以腳本建置映像（30 分鐘）
- 進階練習：CI Runner 執行腳本（2 小時）
- 專案練習：完成全自動化發版（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：端到端自動化可運行
- 程式碼品質：腳本穩定且可讀
- 效能優化：建置時間可控
- 創新性：加入品保關卡


## Case #13: 下載 .gz 檔、解壓與驗證的資料更新流程

### Problem Statement（問題陳述）
業務場景：官方只提供 .gz 壓縮下載，需自動解壓並驗證內容正確性（如測試 168.95.1.1 應為 TW），確保服務使用正確資料。
技術挑戰：可靠下載、串流解壓、格式驗證、錯誤處理與回報。
影響範圍：資料正確性、穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 下載可能失敗或中斷。
2. 解壓與寫檔需處理串流與緩衝。
3. 未驗證即上線風險高。

深層原因：
- 架構層面：缺少驗證用 Contract Test。
- 技術層面：串流處理與 GZip 實作缺。
- 流程層面：異常處理與回報不足。

### Solution Design（解決方案設計）
解決策略：以 HttpClient 下載串流，GZipStream 解壓逐塊寫入 .temp，完成後以 IPCountryFinder 試查樣本 IP 驗證，再進行原子替換。

實施步驟：
1. 串流下載與解壓
- 實作細節：4096 Bytes 緩衝讀寫。
- 所需資源：HttpClient、GZipStream。
- 預估時間：1 小時

2. 契約驗證
- 實作細節：指定幾筆可信 IP 檢查。
- 所需資源：IP2C.NET。
- 預估時間：0.5 小時

3. 原子替換
- 實作細節：見 Case #5。
- 所需資源：檔案系統。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
using (var client = new HttpClient())
{
    var rsp = client.GetAsync(url).Result;
    if (rsp.StatusCode == HttpStatusCode.OK)
    {
        using var source = rsp.Content.ReadAsStreamAsync().Result;
        using var gzs = new GZipStream(source, CompressionMode.Decompress);
        using var fs = File.OpenWrite(file);
        var buffer = new byte[4096];
        int count;
        while((count = gzs.Read(buffer, 0, buffer.Length)) > 0)
            fs.Write(buffer, 0, count);
        return true;
    }
}
return false;
```

實際案例：Worker 下載 .gz 並以 168.95.1.1 → TW 測試驗證。
實作環境：.NET Framework。
實測數據：
改善前：下載後未驗證即上線有風險。
改善後：通過驗證才發布。
改善幅度：品質風險下降（質性）。

Learning Points（學習要點）
核心知識點：
- 串流與 GZip 解壓
- 契約式驗證
- 異常處理流程

技能要求：
- 必備技能：HttpClient、IO
- 進階技能：可恢復下載、重試

延伸思考：
- 可加入校驗碼（Checksum）
- 風險：來源站不穩定
- 優化：CDN/多源下載

Practice Exercise（練習題）
- 基礎練習：下載解壓任意 .gz 檔（30 分鐘）
- 進階練習：加入重試與校驗（2 小時）
- 專案練習：封裝為可重用更新模組（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：解壓與驗證通過
- 程式碼品質：資源釋放與錯誤處理完善
- 效能優化：下載/解壓效率
- 創新性：可靠性增強設計


## Case #14: IPv4 整數與點分字串轉換（API 參數協議）

### Problem Statement（問題陳述）
業務場景：API 規格使用「IPv4 四個位元組整數表示」作為參數，需在 API 端將整數轉回點分字串查詢資料。
技術挑戰：正確位移與遮罩運算，避免大小端或溢位錯誤。
影響範圍：查詢正確性、API 契約穩定性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 位元操作錯誤導致 IP 解析錯。
2. 參數型別與範圍驗證不足。
3. 忽略大小端與符號位影響。

深層原因：
- 架構層面：API 契約定義需清楚。
- 技術層面：缺少工具方法與測試。
- 流程層面：缺單元測試覆蓋。

### Solution Design（解決方案設計）
解決策略：實作 ConvertIntToIpAddress(uint) 與反向轉換，加入單元測試與邊界條件驗證。

實施步驟：
1. 轉換函式
- 實作細節：位移 + 0x00ff 遮罩。
- 所需資源：C#。
- 預估時間：0.25 小時

2. 單元測試
- 實作細節：8.8.8.8 ↔ 134744072。
- 所需資源：測試框架。
- 預估時間：0.25 小時

3. 契約文件
- 實作細節：API 說明文件化。
- 所需資源：README/Swagger。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
private string ConvertIntToIpAddress(uint ipv4_value)
{
    return string.Format("{0}.{1}.{2}.{3}",
        (ipv4_value >> 24) & 0x00ff,
        (ipv4_value >> 16) & 0x00ff,
        (ipv4_value >> 8)  & 0x00ff,
        (ipv4_value >> 0)  & 0x00ff);
}
```

實際案例：WebAPI 控制器使用上述方法處理整數參數。
實作環境：ASP.NET WebAPI2。
實測數據：
改善前：位移錯誤可能導致錯誤國別。
改善後：轉換正確且可測。
改善幅度：資料正確性保障（質性）。

Learning Points（學習要點）
核心知識點：
- 位元運算與遮罩
- API 契約設計
- 單元測試

技能要求：
- 必備技能：C#、單元測試
- 進階技能：泛用 IP 工具庫

延伸思考：
- 支援 IPv6 轉換
- 風險：不同語言實作差異
- 優化：內部以結構表示 IP

Practice Exercise（練習題）
- 基礎練習：撰寫雙向轉換（30 分鐘）
- 進階練習：加入 IPv6 支援（2 小時）
- 專案練習：封裝為跨語言工具（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：轉換正確
- 程式碼品質：清晰可測
- 效能優化：常數時間與低配置
- 創新性：泛化設計


## Case #15: 選用合適 Base Image，標準化執行環境

### Problem Statement（問題陳述）
業務場景：WebAPI 與 Worker 分別需要 ASP.NET/IIS 與 .NET Framework 執行環境，若自行安裝建置繁瑣且易不一致。
技術挑戰：選用官方基底映像以快速取得正確執行環境並減少建置步驟。
影響範圍：建置時間、穩定性、維護成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 自行安裝 runtime 容易錯配。
2. 不同環境版本不一致。
3. 建置時間冗長。

深層原因：
- 架構層面：缺乏不可變映像概念。
- 技術層面：未利用官方基底映像。
- 流程層面：映像管理策略缺失。

### Solution Design（解決方案設計）
解決策略：WebAPI 以 microsoft/aspnet（含 IIS+ASP.NET runtime）為基底；Worker 以 microsoft/dotnet-framework 為基底，COPY 應用即可。

實施步驟：
1. 映像選型
- 實作細節：根據應用需求挑選基底。
- 所需資源：Docker Hub。
- 預估時間：0.25 小時

2. Dockerfile 撰寫
- 實作細節：FROM 正確基底 + COPY。
- 所需資源：Docker。
- 預估時間：0.5 小時

3. 驗證執行
- 實作細節：容器啟動與功能驗證。
- 所需資源：CLI/瀏覽器。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```dockerfile
# WebAPI
FROM microsoft/aspnet
# Worker
FROM microsoft/dotnet-framework:latest
```

實際案例：文章分別採用 microsoft/aspnet 與 microsoft/dotnet-framework。
實作環境：Windows 容器。
實測數據：
改善前：手動安裝 runtime 耗時且易錯。
改善後：基底映像開箱可用。
改善幅度：建置時間縮短為數秒級（質性）。

Learning Points（學習要點）
核心知識點：
- 基底映像選型
- 不可變映像
- 執行環境標準化

技能要求：
- 必備技能：Dockerfile
- 進階技能：自建基底映像

延伸思考：
- 可建立企業基底映像
- 風險：映像更新策略
- 優化：精簡層與安全掃描

Practice Exercise（練習題）
- 基礎練習：替換為官方基底快速啟動（30 分鐘）
- 進階練習：加入安全掃描（2 小時）
- 專案練習：打造團隊共用基底映像（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：映像可用
- 程式碼品質：Dockerfile 精簡
- 效能優化：建置快取有效
- 創新性：企業基底策略


## Case #16: 容器取代 Windows Service：統一啟停與生命週期

### Problem Statement（問題陳述）
業務場景：傳統背景任務需以 Windows Service 方式安裝與維護。容器化後，希望以統一方式管理啟停與重啟，簡化維運。
技術挑戰：將背景服務轉為容器進程並透過 Docker 操控生命週期與日誌。
影響範圍：維運流程、故障處理、彈性擴充。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Windows Service 安裝/升級麻煩。
2. 啟停與日誌查詢介面分散。
3. 跨環境搬遷困難。

深層原因：
- 架構層面：缺統一生命週期管理。
- 技術層面：未用容器管理進程。
- 流程層面：維運手冊繁冗。

### Solution Design（解決方案設計）
解決策略：以容器長駐進程（ENTRYPOINT）取代 Service，使用 docker run -d 啟動，docker stop/restart/ps/logs 管控生命週期與觀測。

實施步驟：
1. 將服務改為 Console
- 實作細節：主迴圈 + 日誌到 stdout。
- 所需資源：.NET Console。
- 預估時間：1 小時

2. 容器化與啟動
- 實作細節：ENTRYPOINT、-d 背景。
- 所需資源：Docker。
- 預估時間：0.5 小時

3. 操作手冊
- 實作細節：定義啟停/重啟/查日誌命令。
- 所需資源：README。
- 預估時間：0.5 小時

關鍵程式碼/設定：
```dos
docker run -d ip2c/worker
docker stop <id> && docker start <id>
docker logs <id>
```

實際案例：Worker 改以容器長駐運行，維運僅需 Docker 命令。
實作環境：Windows 容器。
實測數據：
改善前：需 Service 安裝/設定。
改善後：Docker 命令統一操作。
改善幅度：維運簡化（質性）。

Learning Points（學習要點）
核心知識點：
- 容器生命週期管理
- Daemon 模式
- 可觀測性介面統一

技能要求：
- 必備技能：Docker CLI
- 進階技能：自動重啟策略

延伸思考：
- 可與編排器（Swarm/K8s）結合
- 風險：單節點容器失效
- 優化：自動重啟/健康檢查

Practice Exercise（練習題）
- 基礎練習：以 docker 命令管理服務生命週期（30 分鐘）
- 進階練習：加入 restart policy（2 小時）
- 專案練習：遷移到編排器（8 小時）

Assessment Criteria（評估標準）
- 功能完整性：啟停控制與日誌可用
- 程式碼品質：服務主迴圈健壯
- 效能優化：資源占用穩定
- 創新性：維運自動化設計


========================
案例分類
========================

1. 按難度分類
- 入門級（適合初學者）
  - Case 7（容器化日誌）
  - Case 8（NAT 測試策略）
  - Case 14（IP 轉換）
  - Case 15（基底映像）
  - Case 16（容器取代 Service）
- 中級（需要一定基礎）
  - Case 2（WebAPI 容器化）
  - Case 3（熱更新資料檔）
  - Case 4（容器內排程）
  - Case 5（原子性更新）
  - Case 6（Volume 共享）
  - Case 9（端到端整合）
  - Case 10（Reverse Proxy）
  - Case 11（SDK + 客戶端快取）
  - Case 12（CI/CD）
  - Case 13（下載解壓與驗證）
- 高級（需要深厚經驗）
  - Case 1（容器驅動微服務拆分設計）

2. 按技術領域分類
- 架構設計類
  - Case 1、10、12、16
- 效能優化類
  - Case 3、6、11、14、15
- 整合開發類
  - Case 2、4、5、9、13
- 除錯診斷類
  - Case 7、8、9
- 安全防護類
  - Case 5（一致性與回滾，偏可用性/可靠性面向）

3. 按學習目標分類
- 概念理解型
  - Case 1、10、15、16
- 技能練習型
  - Case 2、3、4、5、6、13、14
- 問題解決型
  - Case 7、8、9、12
- 創新應用型
  - Case 11（SDK + 快取設計）、Case 12（管線拓展）

========================
案例關聯圖（學習路徑建議）
========================

- 建議先學：
  - 基礎環境與概念：Case 15（基底映像）、Case 2（WebAPI 容器化）、Case 16（容器生命週期）、Case 7（日誌）
  - 目標：先能「把服務跑起來並看得到」

- 依賴關係與循序：
  - Case 2（WebAPI 容器化） → Case 14（IP 轉換正確性） → Case 3（熱更新資料檔）
  - Case 4（容器內排程） → Case 13（下載/解壓/驗證） → Case 5（原子替換）
  - Case 6（Volume 共享） ←（依賴）Case 2、4 完成基本容器
  - Case 9（端到端整合） ←（依賴）Case 2、4、6、3、5、13
  - Case 10（Reverse Proxy/HA） ←（依賴）Case 2 完成多副本
  - Case 11（SDK + 客戶端快取） ←（依賴）Case 2（API 穩定）
  - Case 12（CI/CD） ←（依賴）Case 2、4 基本映像可建置
  - Case 1（整體拆分設計）貫穿全程，最好在學習開始與結束各回顧一次

- 完整學習路徑建議：
  1) Case 15 → 2 → 16 → 7（打好容器與觀測基礎）
  2) Case 14 → 3（確保 API 正確與熱更新）
  3) Case 4 → 13 → 5（建立可靠的資料更新流水）
  4) Case 6 → 9（打通共享與端到端聯測）
  5) Case 10（引入 HA/Scale 思維）
  6) Case 11（強化 DX 與效能）
  7) Case 12（落地 CI/CD 自動化）
  8) 回到 Case 1（總結容器驅動微服務設計，檢視優化點）

以上 16 個案例均對應原文場景，含問題、根因、解法、實作與驗證，並可直接用於課程、實作與評估。