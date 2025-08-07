# Azure Labs: Mixed-OS Docker Swarm

## 摘要提示
- 混合叢集: 透過 Azure VM 同時建立 Windows 與 Linux 節點，組成 Mixed-OS Docker Swarm。
- 節點加入: Linux 節點加入方式與 Windows 完全相同，只需使用 Swarm join token。
- 標籤管理: 以 node label 標示 os=windows / os=linux，再用 constraint 精準部署服務。
- 服務部署: NGINX 與 ASP.NET MVC Demo 分別透過限制條件被排程到對應 OS 節點。
- Routing Mesh: Windows Container 仍不支援負載導向的 ingress routing，需等待後續更新。
- DNSRR 疑難: 在 Linux 節點測試內建 127.0.0.11 DNS，仍無法解析跨 OS 服務名稱。
- 官方示範: 微軟官方 Demo 以獨立 Windows VM 手動配置 NGINX 做負載平衡，顯示方案尚不成熟。
- 開發好處: 容器化讓開發者可輕鬆複製複雜架構，降低環境建置門檻並簡化 CI/CD。
- 技術投資: 早學容器技術，有助將來遷移 Legacy .NET 與實踐 micro-service。
- 未來展望: 等待 Windows 支援 Linux container 與完整 Routing Mesh，Mixed-OS 開發體驗將更完善。

## 全文重點
作者延續前一篇 Windows Container Swarm 實驗，進一步在 Azure 上加入 Linux VM，搭建可同時執行 Windows 與 Linux 容器的 Mixed-OS Docker Swarm。首先於現有三台 Windows 節點外增設一台 Ubuntu（lcs4），利用 manager 節點取得 join token 即可把 Linux 節點納入叢集，過程與加入 Windows 節點無異。  
混合叢集帶來排程問題：Swarm 不會自動辨識映像的 OS，因此必須透過 node label 管理。作者為每個節點新增 os 標籤，並在 service create 時加入 `--constraint 'node.labels.os==linux'` 或 `==windows`，才能保證 Linux 映像只被派送到 Linux 節點，例如以三個 replica 部署 NGINX 成功全落在 lcs4。  
之後作者驗證 DNS Round-Robin（DNSRR）。在 Linux 節點以 busybox 容器測試 127.0.0.11 Docker 內建 DNS，卻無法解析任何服務名稱；Windows 容器甚至連 nslookup 都失敗，推測目前 Mixed-OS 下 DNSRR 尚待改進。  
作者比較微軟官方 Demo，發現對方使用獨立 VM 手動編輯 NGINX.conf 列出動態 Port 做負載平衡，顯示 Windows Routing Mesh 功能仍缺位，只能期待「coming soon」。  
文章最後強調容器化對異質架構與 Legacy .NET 系統的重要性，鼓勵開發者利用 Azure 免費額度動手實驗，及早累積經驗，以迎接未來 Windows 與 Linux 容器無縫並存的時代。

## 段落重點
### 前言
作者回顧先前對 Open-Source 與混合架構的觀察，指出 StackOverflow 早已採用 Windows + Linux 併存，傳統 VM 難以複製此環境，而容器技術正好解決痛點；目標是在既有 Windows Swarm 上再加入 Linux 節點與服務，驗證開發、測試到生產皆可運行的混合叢集。

### Add Linux Node
在 Azure 建立 Ubuntu VM（lcs4）並安裝 Docker，於 Swarm Manager 執行 `docker swarm join-token` 取得 worker token，於 lcs4 執行 join 指令即可；隨後 `docker node ls` 看到四個節點，其中 lcs4 狀態 Ready。此步驟證明跨 OS 加入流程一致，環境基礎完成。

### Add OS Label
為避免 Linux 映像被派送到 Windows 節點導致無限重試，作者使用 `docker node update --label-add os=<type>` 為各節點加標籤，再在 `docker service create` 時以 `--constraint` 限定部署條件。範例中 NGINX 3 個 replica 全部落在 lcs4，Windows 節點則繼續跑 ASP.NET MVC 與 Console 服務，混合排程成功。

### DNSRR 驗證
作者使用 busybox 建立 ssh 服務並設定 `--endpoint-mode dnsrr`，進入容器後可 ping 其他服務的虛擬 IP，顯示 Overlay 網路正常；但對 127.0.0.11 進行 nslookup 卻無法解析任何服務名稱，Windows 容器情況更差。推測目前 Docker for Windows 尚未完整實作 DNSRR，問題待官方修正。

### MS 官方的 DEMO 怎麼做?
分析 Microsoft Container Network Team PM 的 Demo 影片，發現對方採用額外 Windows Server 執行 NGINX，手動維護後端服務動態 Port，並未利用 Swarm 內建 Routing Mesh。作者認為此法上線維運成本高，側面證明 Windows Routing Mesh 功能仍缺，需等待官方更新。

### 總結
本系列 Labs 展示在 Azure 免費額度內即可搭建 Mixed-OS Swarm，並揭露目前 Windows 容器在 Routing Mesh 與 DNSRR 的不足。即便短期成效有限，過程有助理解細節並為 Legacy .NET 容器化做準備；未來 Windows 將能直接執行 Linux 容器與完善網路特性，熟悉容器技術的開發者將佔得先機。