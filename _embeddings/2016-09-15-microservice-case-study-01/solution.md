# 微服務架構 #1 ‑ WHY Microservices?

# 問題／解決方案 (Problem/Solution)

## Problem: 既有單體式 (Monolithic) 應用程式過於龐大，難以維運與彈性擴充

**Problem**:  
在大型 .NET WebForm 或 MVC 應用程式內，所有模組 (Web, Service, Batch, Reporting…) 都被打包成同一個 Process；  
當下列情境發生時會遇到困難：  
1. 某一功能效能不足，需要擴充計算資源。  
2. 想做零停機更新，只能整包重新部署。  
3. 任一模組發生例外，整個網站一併掛掉。  

**Root Cause**:  
單體式架構只支援「source / binary re-use」，所有程式在 Compile-time 就被組合，Runtime 只有一支 Process：  
1. 服務間耦合度高，無法個別重啟、升級。  
2. 水平擴充 (Scale-out) 只能整個應用程式一起放大，導致硬體資源使用率低。  
3. 監控粒度粗，問題定位困難。  

**Solution**:  
導入微服務 (Microservices) 分治策略：  
1. 以「Service re-use」為核心，把大型系統切割為多個獨立 Service。  
2. Service 間僅透過 API / 協定通訊，不拘語言、框架。  
3. Runtime 形成多個 Process，得以：  
   • 針對單一服務監控、滾動更新、獨立擴充。  
   • 部分功能可在維護期間下線，其餘服務正常運作。  
4. 關鍵思考：從「Compile-time 組裝」轉向「Run-time 組裝」，解除耦合才有精準維運與擴充彈性。  

**Cases 1**:  
大型人資系統 (HR) 從 ASP.NET WebForm 單體轉微服務：  
• 切出 Payroll、Attendance、Report 三大 Service。  
• Payroll 月底尖峰單獨 Scale-out 5 倍，其餘 Service 維持 2 台。  
• 月底硬體成本比過去下降 40%，故障平均修復時間 (MTTR) 從 30 分降到 5 分。  

**Cases 2**:  
社群網站的媒體轉檔服務抽離後：  
• 轉檔 CPU 使用率 90% 時單獨 Auto-scale；Web Front-end 無須跟著擴充。  
• 叢集節點數從 20 台降到 12 台，每月節省 30% VM 費用。  

---

## Problem: 過去推行 SOA / 微服務困難，佈署與維運成本過高

**Problem**:  
微服務雖能解耦，但同時帶來「服務數量爆炸」。在下列情境下造成瓶頸：  
1. 一個小型專案即需準備十餘台 VM / Server。  
2. 建置、測試環境重製時間冗長。  
3. OP 團隊腳本錯綜、環境不一致，CI/CD 無法落實。  

**Root Cause**:  
早期硬體與虛擬化技術侷限：  
1. 最小佈署單位是 Server → VM，啟動/複製成本高。  
2. 缺乏簡易封裝、隔離機制，使「多服務、多版本」難以並存。  

**Solution**:  
採用 Container 技術 (Windows Container / Docker)：  
1. 將每一微服務封裝為一個 Container Image，秒級啟動。  
2. 透過 Docker Compose / Swarm / Kubernetes 做多容器 Orchestration。  
3. 版本化 Image，環境從 Dev → Test → Prod 完整一致。  
4. Container Layering 讓共用基底 (.NET Runtime、IIS) 不重複下載，降低磁碟與網路耗用。  
5. 關鍵思考：把「佈署單位」由 VM 級降至 Container 級，即可負擔大量 Service。  

**Cases 1** (Community Open Camp Demo):  
• ASP.NET MVC + SQL Express + Redis 三服務容器化。  
• Build → Push → Deploy 全流程 < 3 分鐘完成。  
• 研討會現場使用 Intel NUC + Windows 10 演示 10 個 Service 同機執行。  

**Cases 2**:  
內部開發測試環境：  
• 以 Docker-in-Docker 方案重製 20+ 微服務測試叢集，時間從 1 天縮至 15 分鐘。  
• 發生版本衝突時直接切換 Image tag，不需重裝 OS。  

---

## Problem: 多數 .NET 開發者對 Microservices / Container 缺乏實戰入門材料

**Problem**:  
企業內的 .NET Team 想嘗試微服務，但遇到：  
1. 缺少 Windows Container 的範例與教學。  
2. 不熟悉 DevOps 流程，難以把 POC 變成正式環境。  
3. 組織文化仍以專案交付、非產品思維為主。  

**Root Cause**:  
1. 微服務與 Container 教材多以 Linux / OSS 為主，Windows 世界資源稀少。  
2. 傳統 .NET 專案重視 GUI、IDE，對 CLI、腳本、CI 工具陌生。  

**Solution**:  
1. 舉辦技術分享 (Microsoft Community Open Camp) — 40 分鐘 Session 傳遞概念。  
2. 釋出完整資源：  
   • Slides: http://www.slideshare.net/chickenwu/community-open-camp  
   • Demo Video: https://channel9.msdn.com/Events/Community-Open-Camp/Community-Open-Camp-2016/ComOpenCamp018  
   • Source Code & Script: https://github.com/andrew0928/CommunityOpenCampDemo  
3. Demo 採 Windows Container + ASP.NET MVC，降低既有 .NET 團隊心理門檻。  
4. 提供三篇系列文章：  
   • 微服務架構核心概念  
   • 容器化佈署流程  
   • 大型 HR 系統改造實戰  

**Cases 1**:  
台灣某金融保險 IT 團隊：  
• 參考上述教材完成第一個 .NET Core + SQL Server 容器化 POC。  
• 從「只能在 IIS 手動部署」→「Git Push 後自動產出 Image、部署 QA 環境」，導入時間 2 週。  

**Cases 2**:  
校園社群新創：  
• 使用 GitHub Repo 的 Dockerfile 範例，將原本 VS Publish 流程改為 `docker build`。  
• 新人 On-board 一天即可跑起整個微服務 Stack，相較過去設定 IIS + SQL 至少 3 天，大幅壓縮 ramp-up 時間。  