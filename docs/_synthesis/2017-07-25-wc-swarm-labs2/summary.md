---
layout: synthesis
title: "Azure Labs: Mixed-OS Docker Swarm"
synthesis_type: summary
source_post: /2017/07/25/wc-swarm-labs2/
redirect_from:
  - /2017/07/25/wc-swarm-labs2/summary/
postid: 2017-07-25-wc-swarm-labs2
---

# Azure Labs: Mixed-OS Docker Swarm

## 摘要提示
- 混合作業系統 Swarm: 在同一個 Docker Swarm 中同時加入 Windows 與 Linux 節點，形成 Mixed-OS 叢集
- 開發環境動機: 為滿足實務上「以領域選最佳解」的混搭架構需求，容器化讓跨 OS 的本機/共用環境更可行
- Azure 實作: 以 Azure VM 延伸先前的 Windows Swarm，加掛一台 Ubuntu VM 作為 Linux 節點
- 節點加入流程: 透過 docker swarm join-token 取得對應 token，將新節點加入為 worker/manager
- 節點標籤管理: 使用 node labels（如 os=windows/linux）與 constraints，精準排程到相容 OS
- 服務部署示範: 以 NGINX（Linux 容器）在 Swarm 上建 service，透過 constraint 部署至 Linux 節點
- Routing Mesh 限制: 當時 Windows 容器尚未支援 routing mesh，導致跨 OS 網路行為不一致
- DNSRR 疑難: 在 Mixed-OS 下用 Docker 原生 DNS（127.0.0.11）查詢 service 名稱失敗，疑似設定或支援差異
- 官方示範省思: 微軟示範以叢集外獨立 NGINX+靜態 port 配置負載，難以應對動態擴縮與重啟
- 實務觀點: 以容器化延續 .NET legacy 部署，擁抱微服務與異質協作，提早踩雷為未來遷移做準備

## 全文重點
作者延續前一篇 Windows Container Swarm 的實驗，將 Linux 節點納入既有 Swarm，完成混合 OS 的容器叢集，以回應現代系統在不同領域採最佳技術組合（Windows+Linux）的需求。環境架構上，原有三台 Windows 節點與 ingress 已就緒，新增一台 Ubuntu VM（lcs4），以 docker swarm join-token 在 manager 取得 token，將 lcs4 加入叢集。加入後以 docker node ls 確認四節點皆 Ready。

混合 OS 帶來的關鍵挑戰在於排程：若直接建立 Linux 映像（如 NGINX）的服務而不加限制，Swarm 可能把任務指派到 Windows 節點，導致建立失敗並不斷重試。正解是為節點加上標籤（os=windows/linux），並在建立服務時以 --constraint 'node.labels.os==linux' 指定僅部署至相容節點。示範中 NGINX 服務 replicas=3 成功全部跑在 lcs4。作者驗證瀏覽器連線至 lcs4 public IP 能看到 NGINX 預設頁，但 Windows 容器當時尚未支援 routing mesh，因此無法像 Linux 一樣用同一虛擬 IP 跨節點透明轉送。

作者進一步針對 DNSRR（DNS round-robin）做測試：在 Linux 節點建立 busybox 服務並進入容器，確認能 ping 到同網段的其他容器 IP，但透過 Docker 原生 DNS（127.0.0.11）nslookup 服務名（包含 Windows 端的 mvcdemo/console 與 Linux 端的 nginx/ssh）皆查不到記錄。相較 Windows 容器更糟的是，Windows 端連 127.0.0.11 的查詢行為也異常，疑似未正確綁定 DNS。作者因此研判要嘛是手法與設定有缺漏，要嘛是當時的支援仍有缺口。

對照微軟官方影片示範，第三段以叢集外另一台 Windows Server 跑 NGINX 並手工編輯 nginx.conf 指向三個 Web 實例的動態 port 做負載，雖能運作但不實務：加節點或容器重啟導致端口變動就需重配，難以自動化與擴展。這也印證當時在 Windows 容器網路上的不足，作者選擇靜待「coming soon」的 routing mesh 完善支持。

總結上，本文是一次系統性踩雷：用 Azure 快速搭建 Mixed-OS Swarm，建立節點標籤與排程約束的正確實作心法，並揭示 Windows 容器在 routing mesh 與 Docker DNS 的限制。從實務出發，作者主張以容器化部署現存 .NET 應用，採微服務與異質協作，避免全面重寫的高風險路線；在未來 .NET Core/Windows 容器日趨成熟時，先行累積容器化經驗才能把握遷移窗口。

## 段落重點
### Add Linux Node
作者在既有的 Windows Swarm（wcs1~wcs3 與 ingress）中，新增一台 Ubuntu VM（lcs4），以實作 Mixed-OS 叢集。步驟為：在 manager（wcs1）上用 docker swarm join-token 取得對應 worker/manager 的 token，於 lcs4 執行 join 指令，即可加入叢集。特別提醒 Azure 建置時需確保同一虛擬網路，避免誤建在 classic network 導致互通失敗。加入後透過 docker node ls 可見四節點皆 Ready，至此基礎環境完成，為後續在叢集中同時部署 Linux 容器鋪路。

### Add OS Label
混合 OS 下，Swarm 預設不會辨識映像對應 OS，相容性需由使用者明確約束。作者先示範錯誤情境：直接建立 NGINX 服務，Swarm 將任務派到 Windows 節點，容器建立失敗並反覆重試，造成資源浪費。正確做法是為節點加上標籤 os=windows/linux（docker node update --label-add），建立服務時加上 --constraint 'node.labels.os==linux'，讓排程僅落在 Linux 節點。實測以 NGINX replicas=3 成功全數部署於 lcs4，並以瀏覽器連 lcs4 公網 IP 驗證服務可用。文中亦點出當時 Windows 容器尚未支援 routing mesh，限制了跨節點的透明流量導向。

### DNSRR 驗證
作者嘗試釐清前一篇未能成功驗證的 DNSRR 行為。在 Linux 節點建立 busybox 服務（endpoint-mode=dnsrr）並進入容器後，先以 ping 驗證同網段容器 IP 可達，確認網路與 Overlay 正常。但以 Docker 原生 DNS（127.0.0.11）對服務名（含 Windows 的 mvcdemo/console 與 Linux 的 nginx/ssh）進行 nslookup 均失敗，顯示名稱解析未生效。相較 Windows 容器的狀況，Linux 至少能對 127.0.0.11 發出查詢但無記錄；Windows 端甚至疑似未正確綁定 DNS 服務。作者推測可能為自身設定缺漏或當時產品支援限制，並公開徵求更正與回饋。

### MS 官方的 DEMO 怎麼做? (2017/07/31 補充)
作者檢視微軟官方示範影片，第三段以叢集外一台獨立 Windows Server 跑 NGINX，手動維護 nginx.conf，將流量導向三個 Web 實例的動態對外埠口以達到負載平衡。作者批評此法不具可擴展性：每增節點或容器重啟導致端口變動，配置即需手動更新，無法滿足實務的自動化與彈性。此舉側面印證了當時 Windows 容器網路（如 routing mesh）的支援尚未完善，故官方示範採取繞道做法。作者因而選擇等待正式 routing mesh 支援落地，以獲得一致與自動化的體驗。

### 總結
本篇以 Azure 快速實作 Mixed-OS Swarm，整理出在混合 OS 叢集上正確部署的要點：務必以 node labels 與 constraints 控制排程，避免跨 OS 錯派造成失敗與重試；同時揭露 Windows 容器當時在 routing mesh 與 Docker DNS/DNSRR 的不足與實務落差。從組織與技術策略來看，作者主張先容器化既有 .NET 應用，採微服務與異質協作取代一刀切重寫，因應未來 5~10 年 Windows 與 Linux 並存的現實。提早學習與踩雷，有助將來在 .NET Core 與 Windows 容器完整成熟時，迅速、低風險地完成遷移與擴展。作者以此鼓勵開發者把握現有雲端額度實作，累積經驗，迎接容器化成為軟體發行與部署主流的時代。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本容器概念（Image、Container、Registry、Network）
   - Docker 基本操作（docker run/ps/images、docker swarm 基礎）
   - Azure 建立與管理 VM、VNet/子網路基礎
   - Linux/Windows 伺服器基本操作與網路常識（VLAN、IP、Port、DNS）
   - 基本 CI/CD 與環境一致性觀念

2. 核心概念：
   - Mixed-OS Docker Swarm：在同一個 Swarm 集群中同時納管 Windows 與 Linux 節點
   - 節點標籤與排程約束（labels/constraints）：用 node.labels.os 精準控制跨 OS 的服務部署
   - 服務與網路（service、replicas、ingress、routing mesh、DNSRR）：Swarm 模式的流量導向與名稱解析
   - Windows 容器網路限制：當時 Routing Mesh 與 DNS 解析在 Windows 容器上的限制與替代方案
   - 開發到生產的一致性：用容器化與 Swarm/Compose 降低異質環境落差

3. 技術依賴：
   - Docker Swarm 模式依賴：Manager/Worker 節點、Raft、Join Token
   - 服務調度依賴：節點標籤（node labels）→ 排程約束（--constraint）→ 正確 OS 上執行
   - 網路依賴：ingress overlay、Docker Embedded DNS（127.0.0.11）、DNSRR/Virtual IP
   - 平台依賴：Azure VM、同一 VNet/子網（避免 Classic/Resource Manager 混淆）
   - 未來能力依賴：Windows Server 以 Hyper-V 支援 Linux 容器的路線

4. 應用場景：
   - 企業混合技術棧（.NET Framework/Windows + OSS/Linux）統一用容器部署
   - 開發/測試/生產環境一致化與快速複製
   - 逐步容器化 Legacy .NET 應用，與新建 Linux 服務共存
   - 以 NGINX 等 Linux 元件為 Windows 應用提供周邊（LB/反向代理/靜態資源）
   - 建立跨 OS 微服務拓撲，服務間透過 overlay network 通訊

### 學習路徑建議
1. 入門者路徑：
   - 了解容器與 Docker 核心概念與基本指令
   - 在本機分別啟動 Windows 與 Linux 容器（或各自的 VM）
   - 初試 docker swarm init、docker service create 與 docker service ps 基本流程

2. 進階者路徑：
   - 在雲端（Azure）建立多台 VM，部署 Swarm（1 manager + 多 worker）
   - 操作 join-token、node ls、service ls/ps，並實作節點標籤與約束調度
   - 練習 overlay/ingress 網路、端點模式（VIP vs DNSRR），理解 Routing Mesh 工作方式與限制

3. 實戰路徑：
   - 從既有 Windows .NET 應用建立映像，與 Linux NGINX/工具鏈組合
   - 建立 Mixed-OS Swarm，為 Linux/Windows 服務分別配置 constraints 與副本數
   - 以 CI/CD 自動化部署與版本更新；在限制條件下設計可靠的流量導向策略（暫用外部 LB 或靜態配置）

### 關鍵要點清單
- Mixed-OS Swarm 集群：在同一 Swarm 內同時管理 Windows 與 Linux 節點，實現異質共存（優先級: 高）
- Join Token 機制：worker 與 manager 使用不同 Token 安全加入集群（優先級: 中）
- Azure 網路一致性：所有 VM 必須在同一 VNet/子網，避免 Classic/ARM 混用導致互通失敗（優先級: 高）
- 節點標籤（node labels）：為節點加上 os=windows/linux 標記，作為排程依據（優先級: 高）
- 排程約束（--constraint）：用 node.labels.os==linux/windows 精準投放服務至對應 OS（優先級: 高）
- 服務副本與調度：replicas 控制實例數，manager 依規則分配至可用節點（優先級: 中）
- Ingress 網路與 Routing Mesh：對外單一入口分發到服務副本；當時 Windows 容器支援有限（優先級: 中）
- DNSRR 與 Docker Embedded DNS：127.0.0.11 提供服務名稱解析；在 Windows/混合環境可能遇到解析限制（優先級: 中）
- 問題排查命令：docker node ls、service ls/ps、ps -a、exec/nslookup/ping 用於定位排程與網路問題（優先級: 高）
- NGINX 作為 Linux 邊車：可在 Linux 節點上提供反代/LB，暫替 Routing Mesh 缺口（但需管理動態端口與配置）（優先級: 中）
- CI/CD 與環境一致性：容器化與自動化部署降低跨 OS 技術棧的協作成本（優先級: 高）
- Legacy .NET 容器化策略：優先封裝與切分服務，逐步演進到微服務與跨 OS 協作（優先級: 高）
- 風險與限制認知：Windows 容器網路功能（如 DNSRR、Routing Mesh）在當時版本存在缺口需替代方案（優先級: 高）
- 未來能力演進：Windows Server 透過 Hyper-V 路線支援 Linux 容器，提升開發機一鍵啟動整套環境的可行性（優先級: 中）