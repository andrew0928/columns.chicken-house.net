# [實戰] 十分鐘搞定! 在 Azure 上面佈署 Docker Container! - Docker Cloud 託管服務體驗

# 問題／解決方案 (Problem/Solution)

## Problem: 大量建立 Docker Host ‒ 佈建速度慢、易出錯  

**Problem**:  
當要在 Azure（或多個雲端）快速開始「Docker 化」專案時，需要先建立數台已安裝好 Docker Engine 的 Linux VM。若以傳統方式逐台手動開 VM、設定憑證、防火牆與安裝 Docker，流程繁瑣且容易發生錯誤，導致專案啟動時間被大幅拉長。  

**Root Cause**:  
1. 缺乏跨雲端的一致化佈建工具。  
2. 建立 VM、安裝 Docker、配置網路需要多重步驟和權限設定，手動操作耗時易漏。  

**Solution**:  
採用「Docker Cloud – Nodes」(內建 Docker Machine 能力) 直接呼叫 Azure API，完成：  
a. 上傳 Docker Cloud 產生的管理憑證至 Azure。  
b. 在 Docker Cloud 介面勾選地區、VM 規格、磁碟大小與節點數量。  
c. 一鍵 Launch，Docker Cloud 自動：  
   • 建立 Azure VM (Ubuntu + Docker Engine – CS 版)  
   • 安裝/註冊 Docker Cloud Agent  
   • 回報節點狀態到 Dashboard  
如此即可 5–10 分鐘內完成多台 Docker Host 佈建，並統一受 Docker Cloud 控制。  

**Cases 1**:  
• 示範建立 Basic A1 VM + 60 GB HDD，約 7 分鐘完成。  
• 所有動作全自動產生相對應雲端服務、網路設定。  
• 減少 8–10 個手動步驟，零失誤完成佈建。  

**Cases 2**:  
• 個人 Mini-PC 亦可被註冊為 Node，只需一次性安裝 Agent，同樣受 Docker Cloud 監管，免除日常 SSH 操作。  

---

## Problem: 多容器服務手動部署複雜、難維護  

**Problem**:  
以 WordPress 為例，需同時佈署 reverse-proxy、web、db、data 等 3–4 個 Container，還要建立 link、port 與 volume。若用 docker run 指令逐一完成，對團隊與新手都是高摩擦流程。  

**Root Cause**:  
1. Docker Engine CLI 為單機導向，缺少「一次性定義 → 一鍵啟動」能力。  
2. 配置分散在多條指令中，日後重建或遷移時容易遺漏參數。  

**Solution**:  
利用 Docker Compose 語法寫成 Stackfile，透過 Docker Cloud「Stacks」功能一次部署：  

```yaml
db:
  image: mysql:latest
  environment:
    - MYSQL_ROOT_PASSWORD=YES
  restart: always

web:
  image: amontaigu/wordpress:latest
  links:
    - db:mysql
  ports:
    - "80:80"
  restart: always
```

步驟：  
1. Stacks → Create → 填入 Stack 名/Stackfile。  
2. Save and Deploy。  
Docker Cloud 依序完成 image 下載、container 建立與啟動。  

**關鍵思考點**:  
• 把基礎設計抽象化為宣告式檔案，任何環境可重複使用 → 解決「指令分散」的結構問題。  

**Cases 1**:  
• WordPress 雙容器 (web+db) 4 分鐘部署完成；自動取得 `*.dockerapp.io` 公網 FQDN，立即可訪問。  
• 同樣方式一天內成功搬遷既有部落格、Redmine、GitLab 共 4 個 Stacks。  

---

## Problem: 高可用(HA)與彈性擴充困難  

**Problem**:  
單一 VM/Container 故障即中斷服務；流量高峰時無法快速擴充第二、第三個實例。  

**Root Cause**:  
1. 缺少容器排程與資源調度層。  
2. Host 間網路、Port 重複、健康檢查等協調機制複雜，需要專業 DevOps 才能自行打造。  

**Solution**:  
在 Docker Cloud 啟用 Swarm-based Orchestration：  
• 將服務副本數 (containers) 由 1 調整到 N，Docker Cloud 依節點資源自動分配。  
• 支援 Rolling Redeploy：一次只重建一個 Container，確保服務不中斷。  
• 動態 Ports mapping + 前端 Reverse Proxy 設計，可避免多實例的 Port 衝突。  

**Cases 1**:  
• 調整 `web` 服務 Scale=2，系統提示需第二 Node，加入後 8 秒內自動啟動第 2 個 Container，分散流量。  
• 於凌晨更新映像：Rolling Redeploy 2 分鐘完成，全程 0 Downtime。  

**Cases 2**:  
• 商業帳號每增加 1 Node 僅 USD $15/mo + VM 成本，取代傳統兩台負載平衡 IaaS 架構，可省 60–70% 維運費用。  

---

## Problem: 變更配置需重建 Container，手動重打指令低效率  

**Problem**:  
Container 無法線上修改 Port/Volume 等設定；修改後須重新建立，但若沒保存原指令，重建耗時且易出錯。  

**Root Cause**:  
傳統 CLI 操作與設定檔分離，缺乏版本化與「差異比較」。  

**Solution**:  
• 把所有設定集中於 Stackfile；在 Docker Cloud 內 Edit → Save。  
• 系統自動標記需要 Redeploy 的 Service (黃色驚嘆號)。  
• 一鍵 Redeploy (Stack 或單一 Service) → 由舊 Container 換新 Container。  

關鍵：以 Declarative File 作為唯一事實來源 (single source of truth)，UI 只做版本管控與一鍵出動。  

**Cases**:  
• 修改 WordPress `image` tag → 按 Redeploy，全流程 30 秒，網站正常運作。  
• 讓新人僅修改 YAML 並按按鈕，即能升級服務，降低 80% 操作門檻。  

---

## Problem: Linux / 雲端新手對防火牆、Agent 安裝、權限設定不熟悉  

**Problem**:  
作者自述是 Linux 門外漢，先前以手動方式實作常碰到阻礙，如開通 Port、安裝 CS Docker、維護憑證與 SSH Key 等。  

**Root Cause**:  
1. Linux 基礎薄弱而導致環境差異問題。  
2. 每家雲端 (Azure、AWS…) 認證流程不同，手動整合成本高。  

**Solution**:  
• 使用 Docker Cloud 提供的「雲端憑證下載 + 上傳 Azure 兩步法」完成授權。  
• 之後所有 VM 由 Docker Cloud 自動帶入適當設定 (防火牆 Port 2376、Agent 配置)。  
• 介面導引式操作，簡化學習曲線。  

**Cases**:  
• 完成憑證上傳 + Subscription ID 填寫只花 3 分鐘。  
• 從「擔心設定失敗」到「全程按鈕」，大幅縮短 1–2 天摸索時間。  

---

## Problem: 個人/中小團隊缺乏專職維運人員，成本壓力大  

**Problem**:  
若要享有與大雲端 PaaS 類似的佈署/監管體驗，一般情況需購買昂貴平台或僱用 DevOps。  

**Root Cause**:  
傳統解法要不自建 Kubernetes 叢集，要不購買商用 PaaS，初期成本高。  

**Solution**:  
• Docker Cloud ★免費帳號★支援 1 Node，已含 GUI、Stack、Auto-Build、私有 Repo。  
• 自購 Mini-PC + Docker Cloud，硬體一次成本 < TWD 5,000；線上服務免費。  
• 若日後擴充，每新 Node 僅 USD $15/mo，按需付費。  

**Cases**:  
• 文章作者以 1 天時間完成部落格、Redmine、GitLab 全站搬遷，硬體+雲端管理 0 元維運成本。  
• 相比傳統租用 VPS + 手動安裝，每月節省約 60% 費用與 90% 人力。  

---