# 掃雷回憶錄 - Windows Container Network & Docker Compose

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 Windows 容器主機上，把容器的 80 port 對應到 8000 之後，無法用 http://localhost:8000 存取？
Windows 容器的 NAT 由 WinNAT 代管，而 WinNAT 不支援 NAT loop-back。  
因此主機本身無法透過 localhost 或 127.0.0.1 去走回自己的轉址規則。  
解決方法：  
1. 在其他電腦上以 http://<主機對外 IP>:8000 存取。  
2. 若一定要在本機測試，就先用 `docker inspect` 查出容器拿到的內部 IP，再以 `http://<容器 IP>:80` (原始埠) 連線。

---

## Q: Windows 容器還支援 `--link` 嗎？
官方文件已明列「container linking (--link) 不支援」。  
實際測試可發現 **部分行為仍會出現**：  
‧ 使用 `--link` 時，DNS 會短暫解析到對方容器 IP，但隨即就找不到。  
‧ 不建議在 Windows 環境依賴 `--link`；改用 Docker 內建的 DNS/service-discovery 或其他方案較穩定。

---

## Q: 使用 docker-compose 啟動多個服務時，偶爾會出現 “host not found” 或 nginx 找不到後端服務，原因是什麼？
主因是 **Windows 容器內的 DNS 快取寫入了「查詢失敗」的記錄**，導致之後一直讀到錯誤結果：  
1. 第一次查詢時 DNS 尚未就緒，被寫入「Name does not exist」。  
2. 快取沒有 TTL，除非手動清除，它永遠不會再去 DNS 解析。  
3. 隨 docker-compose scale 增減服務也會遇到舊快取未更新的問題。  
解決方式：  
‧ 在容器啟動腳本中加入迴圈：`ipconfig /flushdns` → 嘗試啟動服務 → 失敗就 sleep 1 秒重試。  
‧ 若用 nginx，可在 scale 之後執行自訂批次檔 `reload.cmd`：先 flush DNS，再 `nginx -s reload`。

---

## Q: 升級 Windows 10 Creator Update (1704) 後，所有容器都無法上網，該怎麼辦？
Creator Update 新增「可同時建立多個 NAT network」功能，升級過程偶爾會讓 **預設的 `nat` 網路損毀**。  
處理步驟：  
1. 直接另建一個新的 NAT network，例如  
   `docker network create -d nat my-nat`  
2. 啟動容器時加上 `--network my-nat`（或在 docker-compose.yml 指定）。  
新的 NAT network 會正常分配位址與轉送，容器即可恢復外部連線能力。

---

## Q: 目前 (Windows Server 2016 / Win10 1704) 還有哪些 Docker 網路功能尚未支援？
官方列出的缺漏包含：  
1. 預設 overlay network driver（因此本機無法直接建置 Swarm overlay）  
2. container linking (--link)  
3. CLI 選項：`--add-host`、`--dns-opt`、`--dns-search`、`--aux-address`、`--internal`、`--ip-range` 等  
這些功能預計會陸續補齊，使用前建議先查官方文件與發行說明。

---

## Q: 在本機 Windows Server 2016 能否直接建立 Docker Swarm overlay 網路？
目前正式版本尚未支援，無法在本機 Windows 叢集直接啟用 overlay network。  
不過 Azure Container Service 的 private preview 已能同時管理 Windows / Linux 節點並使用 Swarm；顯示官方正積極開發，日後應會落地到一般發行版。

---

## Q: 若 Windows 容器之間要做服務發現，建議用什麼機制？
1. Windows Docker Engine 內建 DNS：同一個 network 內，可直接用 **容器名稱** 做主機名稱互相解析。  
2. 注意 DNS cache 問題，如有不穩定可在啟動腳本中定期 `ipconfig /flushdns`。  
3. 規模再大一點，可考慮搭配 Consul、etcd 等專門的 service registry。