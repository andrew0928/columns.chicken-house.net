# Rancher ─ 管理內部及外部 (Azure) Docker Cluster 的好工具

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Rancher？它能幫 Docker 使用者解決哪些問題？
Rancher 是一套完整的 Docker Engine 與 Cluster 管理平台，提供易於操作的 Web UI、資源監控、內建 Load Balancer、In-Service Upgrade 等功能。使用者只需定義 Container 組態，Rancher 會自動處理主機加入、資源分配與服務升級，讓佈署及維運大幅簡化。

## Q: 作者為何最後選擇 Rancher 而不是 Docker Cloud？
1. Docker Cloud 免費版只能管理 1 個 Node，之後每台每月要付 15 美元；Rancher 完全免費。  
2. Docker Cloud 缺少 CPU / RAM / Disk 使用率等即時統計；Rancher 內建完整 Dashboard。  
因此作者改投入 Rancher 的懷抱。

## Q: 作者特別推薦 Rancher 的哪些核心特性？
1. 直覺且資訊完整的 UI（含主機與每個 Container 的資源使用率）。  
2. 支援 In-Service Upgrade，可不中斷服務完成版本更新。  
3. 內建 HAProxy Load Balancer。  
4. 安裝容易，亦提供專用輕量 Linux─Rancher OS。  
5. 同時支援 Cattle、Docker Swarm、Mesos 等 Orchestration。  
6. 可直接在 Azure 等多家雲端建立或擴充主機。  
7. 支援多個 Environment，方便區隔 Dev／Prod 及多個 Cluster。

## Q: 什麼是 Rancher OS？如何用它快速建立 Rancher Server？
Rancher OS 是專為執行 Docker 打造的精簡 Linux（約 28 MB），系統啟動後 Docker 為 PID 1。  
安裝流程：  
1. 先把 Rancher OS 裝到磁碟（官方指令 ros install …）。  
2. 開機後執行 `docker run -d --restart=always -p 8080:8080 rancher/server` 即可啟動 Rancher Server。  
之後透過 `http://<IP>:8080` 便可進入管理介面。

## Q: 跑 Rancher Server 至少需要多少主機資源？
官方建議至少 1 GB RAM；作者實測給 2 GB RAM 才較順暢。由於 Rancher Server 本身使用多個 Java 元件，Container start 後還需 1–2 分鐘才完全就緒。

## Q: 作者在實驗中規劃了哪些 Environment？目的為何？
作者建立兩組獨立 Cluster：  
1. Local Environment ─ 內網 VM，供開發／測試使用。  
2. Azure Environment ─ 部署於 Azure 資料中心，做為正式環境。  
兩者統一由同一套 Rancher Server 管理，驗證 Dev/Prod 隔離且集中操作的可行性。

## Q: Rancher 如何讓佈署與擴充服務變得「無腦」？
1. 以 Stack 方式上傳或貼上 `docker-compose.yml` 即可一鍵佈署。  
2. 要擴充服務，只需在 UI 把 Scale 數字改大，Rancher 會自動在不同 Host 啟動對應數量的 Container 並更新 Load Balancer 設定。

## Q: Rancher 內建的 Load Balancer 用什麼實作？如何設定？
Rancher 的 Load Balancer 以 HAProxy 為基礎。新增 LB Service 時，只要在 UI 指定要代理的 Target Service，Rancher 便會自動產生並維護 HAProxy 設定；進階需求亦可自行填入原生 HAProxy 設定片段。

## Q: 什麼是 In-Service Upgrade？它如何實現零停機更新？
In-Service Upgrade 會根據新的 compose 設定：  
1. 先拉取新映像並啟動新 Container。  
2. 等新 Container 健康後，再逐批次停止並移除舊 Container。  
3. 若測試 OK 點選「Finish Upgrade」回收舊資源；若失敗可按「Rollback」瞬間回復舊版本。  
整個過程服務持續對外提供。

## Q: 進行 In-Service Upgrade 時，Batch Size、Batch Interval、Start Before Stopping 代表什麼？
1. Batch Size：每批同時要替換多少個 Container。  
2. Batch Interval：兩批次之間的等待秒數，確保新批次已穩定。  
3. Start Before Stopping：勾選時表示先啟動新 Container 再停舊的，可降低中斷風險。

## Q: Rancher 目前有哪些限制是作者認為尚待改進的？
1. 無法像 Azure Cloud Service 那樣提供 Production / Staging 雙環境一鍵切換，上線前缺少「預覽」機制。  
2. 目前還不能匯入外部既有的 Docker Swarm Cluster，必須透過 Rancher 介面重新建立主機；官方表示正在開發中。