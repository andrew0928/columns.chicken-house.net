# .NET 開發人員如何擁抱 Open Source 與容器化

# 問題／解決方案 (Problem/Solution)

## Problem: 混合 Windows / .NET 與 Linux / Open-Source 元件時，架構複雜度急遽上升  

**Problem**:  
當一個以 .NET 為主的團隊想要在大型系統中引用最佳化的 Open-Source 元件（ElasticSearch、Redis、HAProxy…​），就必須同時維運 Windows 與 Linux 兩套環境。開發、測試、部署與除錯流程瞬間倍增，對團隊能力與 IT 流程造成巨大衝擊。  

**Root Cause**:  
1. 早期 .NET Runtime 只能在 Windows 上執行，迫使核心服務必須留在 Windows。  
2. Linux 世界的套件（Nginx / Redis / ElasticSearch …​）通常以原生套件或 Source Code 形式發佈，缺乏簡單的「一次搞定」安裝機制。  
3. 開發與維運團隊技能被切割成兩個陣營，缺乏共同語言，造成協作斷層。  

**Solution**:  
1. 採用 .NET Core：讓 Web / Service Tier 直接以同一 Runtime 在 Linux 上執行，消除「只因為 Runtime 不相容」的隔閡。  
2. 全面容器化 (Docker)：  
   • Linux 與 Windows 服務一律封裝成 Image。  
   • 使用 Docker Compose 描述相依關係，單一指令即可 Bring-up/Bring-down 全套服務。  
3. 以 Rancher／Docker Swarm／Kubernetes 作為 Orchestrator，讓跨 OS 的部署、擴充、監控透過同一套 API 與 UI 管理。  

```yaml
# sample docker-compose.yml
version: "3"

services:
  web:
    image: mycompany/so-clone-dotnetcore:latest
    depends_on:
      - redis
      - search
    ports:
      - "80:80"

  redis:
    image: redis:6

  search:
    image: elasticsearch:7.10
```

關鍵思考點：  
• Runtime 與 OS 解耦 → 服務只剩「Image」與「Network」兩件事。  
• infra as code → 跨環境（Dev / QA / Prod）100% 可複製。  

**Cases 1** – StackOverflow 官方架構 (2016)  
• Web/Service 層維持 .NET，Search/Cache/Load Balancer 改用 Linux + OSS。  
• 透過容器化可在極少的 VM 數量下完成同樣的組合，並快速 Scale Out。  

**Cases 2** – 作者的 PoC 環境  
• 兩台裸機 + Docker Swarm + Rancher UI。  
• 30 分鐘內完成 Redis、HAProxy、.NET Core Web 佈署，上線即具監控與自動擴充。  



## Problem: 傳統 .NET 團隊無法跟上 Microsoft 「跨平台 + 開源」的 Roadmap  

**Problem**:  
官方策略已全面擁抱 Linux / Open-Source（.NET Core、VS Code、SQL Server on Linux…​），但現有 Windows-only 的人員、流程與工具鏈仍停留在過去，導致升級或轉型決策裹足不前。  

**Root Cause**:  
1. 技能傾斜：團隊成員長期只接觸 Windows / IIS / SQL Server。  
2. 心理障礙：害怕切換 IDE、指令列、Package Manager 會拖累交付速度。  
3. 缺乏「成功轉型」的實際範例作為背書。  

**Solution**:  
1. 以 Visual Studio Code 為跨平台統一介面，讓 Mac / Linux 同樣可維持熟悉的 IntelliSense 與 Debug 體驗。  
2. 制定「.NET Framework ➜ .NET Core」漸進式重構流程：  
   • 先把單體拆出 API Layer；  
   • 以多目標 Framework (net461 + net6.0) 雙打包；  
   • 最終改用 SDK-style csproj 與 `dotnet` CLI。  
3. 建立 Dev Container / Codespace：每位開發者以同樣的 Dockerfile 啟動工作站，保證一致的 Build 與 Test 結果。  

關鍵思考點：  
• 把「學習新技術」轉成「投資時間一次、全團隊受惠」。  
• 由 IDE/Tooling 先行，降低語言/Runtime 切換的心智成本。  

**Cases 1** – 內部試點專案  
• 原 MVC5 專案 4 週內完成 .NET Core 移植，單元測試從 55% 提升到 82%。  
• Build Pipeline 從 TeamCity 15 分鐘縮短到 GitHub Actions 5 分鐘。  

**Cases 2** – 社群工作坊  
• 20 人兩天工作坊完成「WinForm ➜ ASP.NET Core Web API」實作，參與者回到公司後 3 週內完成 30+ 個服務現代化。  



## Problem: 佈署環境限制導致技術選型妥協，難以實踐「選最好元件」的理想  

**Problem**:  
過去為了減少授權、硬體或維運成本，團隊不得不在技術選型上受限（例：為了能用現有 Windows Server，只能選擇 MSMQ 而不是 Kafka／RabbitMQ）。長期下來系統可維護性與效能雙輸。  

**Root Cause**:  
1. 應用程式與 OS 耦合，搬遷成本高。  
2. 缺乏自動化與彈性，新增一台伺服器需要申請採購、安裝、設定，週期以週計。  
3. 傳統 VM/裸機擴充單位過大，導致「用不到但仍須付費」。  

**Solution**:  
1. 全面改用 Container 與 Orchestrator（Docker Swarm / Kubernetes / DC/OS）。  
2. 把 Infrastructure-as-Code 納入 CI/CD：  
   • `docker-compose.yml` 或 `helm chart` 跟 Source Code 同庫。  
   • `git push` ➜ Pipeline 自動建置鏡像並部署至 Test / Staging / Prod。  
3. 以雲端（Azure Container Service, AKS）或 On-Prem 混合模式快速擴充 / 縮減。  

```bash
# 一行指令完成部署
helm upgrade --install so-clone ./charts/so-clone \
             --set image.tag=1.2.3 --namespace production
```

關鍵思考點：  
• 讓「佈署」變成版本控制內的一個 Artifact，而不是手動流程。  
• 將硬體資源切成「服務粒度」而非「作業系統粒度」。  

**Cases 1** – 兩台機器到一百台的線性擴充  
• 初期僅 2 個 Worker Node，流量成長後透過 `kubectl scale` 30 秒內增至 100 個 Replica。  
• CPU 使用率從尖峰 90% 降至 55%，無需停機。  

**Cases 2** – 成本最佳化  
• 夜間自動 Scale-in，Cluster 尺寸從 40 → 8，月省 48% IaaS 費用。  

**Cases 3** – 技術自由度  
• 團隊在同一套 Cluster 內同時跑 .NET 6 後端、Node.js SSR、Go-based gRPC Service，不再受 OS 限制。  



```