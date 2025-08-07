# Azure Labs: Mixed-OS Docker Swarm

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Mixed-OS Docker Swarm？
Mixed-OS Docker Swarm 指的是在同一個 Docker Swarm 叢集內，同時加入 Windows 與 Linux 兩種作業系統的節點，使叢集能同時部署並執行 Windows 與 Linux 容器。

## Q: 如何在既有的 Windows Swarm 中加入新的 Linux Node？
在 Azure 建立一台 Ubuntu Server（例如 lcs4），安裝 Docker 後，到 Swarm 的 manager 節點執行  
`docker swarm join-token worker` 取得 token，接著在 Linux 主機上輸入  
`docker swarm join --token <token> <manager_ip>:2377`  
即可把該 Linux 主機加入叢集成為 worker node。

## Q: 為什麼要替 Swarm 節點加上 os 的 label？
Swarm manager 不會自動判斷容器所需的作業系統，若未標註，manager 可能把 Linux 容器排到 Windows 節點上，導致容器建立失敗並不斷重試。透過  
`docker node update --label-add os=<windows|linux> <node>`  
標記節點，再在建立服務時加上 constraint，可避免此問題。

## Q: 若要讓服務只在 Linux 節點執行，該怎麼下指令？
建立服務時加入限制條件，例如  
`docker service create --name web --network ingress --replicas 3 --constraint 'node.labels.os==linux' nginx`  
就會讓 Swarm 只在標記為 `os=linux` 的節點上排程該服務。

## Q: Windows Container 目前支援 Routing Mesh 嗎？
尚未支援。作者實測無法讓 Windows 容器透過 Routing Mesh 做負載平衡，只能等待 Microsoft 之後的更新（官方僅以 “coming soon” 回應）。

## Q: Docker 的 DNSRR 在混合叢集裡能正常解析服務名稱嗎？
作者測試結果顯示：在 Linux 節點使用 127.0.0.11 做 `nslookup`，無論查詢 Windows 或 Linux 服務名稱皆得不到紀錄；Windows 容器甚至無法對 127.0.0.11 進行查詢。目前原因未明，仍待後續釐清。

## Q: 微軟官方 Demo 是如何做 Web 負載平衡的？
官方影片中另開一台不屬於 Swarm 的 Windows Server，單純跑 Nginx，並手動將三個 Web 容器對外的動態埠寫入 nginx.conf 進行負載平衡；節點或埠變動時必須重新修改設定。

## Q: 在 Azure 上完成本次混合 Swarm 實驗需要多少成本？
不高。作者使用 Azure 免費試用的 6,300 元新台幣額度，兩天連續開機測試僅花約 600 元，遠低於免費額度。

## Q: 作者對 Legacy .NET 應用未來的部署策略是什麼？
與其全面改寫成 .NET Core，作者更傾向將現有 .NET 應用以容器化方式部署，透過微服務與 Mixed-OS Swarm 讓 Windows 與 Linux 系統協同運作，認為現階段投資 Docker 與容器技術最具效益。