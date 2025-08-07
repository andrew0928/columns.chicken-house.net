# 掃雷回憶錄 – Windows Container Network & Docker Compose

# 問題／解決方案 (Problem/Solution)

## Problem: 以 `-p hostPort:containerPort` 做 Port Mapping 時，主機 (Container Host) 本機瀏覽 `localhost` 卻連不到 Container

**Problem**  
在 Windows Server 2016/Windows Container 環境，啟動容器時執行  
```powershell
docker run -d -p 8000:80 --name demo-iis microsoft/iis
```  
理論上應可在主機端以 `http://localhost:8000` 存取，但實際卻無法連線，只能在其他電腦以 `http://<Host-IP>:8000` 存取服務。

**Root Cause**  
Windows Container 使用的 WinNAT 並不支援 NAT Loopback。  
因此從 Container Host 自身送往 `localhost:<mapped-port>` 的封包，不會再被轉回 Container 內部，導致連線失敗。

**Solution**  
1. 測試時直接使用 Container 內部 IP + 內部 Port：  
   ```powershell
   $ip = docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" demo-iis
   # 例: http://$ip:80
   ```  
2. 或改由其他電腦以 Host 的對外 IP + Mapped Port 存取：`http://<Host-IP>:8000`  
3. Windows 14300 之後版本已會自動加入對應 Firewall Rule，無需再手動開 Port。

**Cases 1**  
• 示範用 IIS Container，主機 `localhost:8000` 無法連線；改用外機 `http://10.0.0.5:8000` 成功。  
• 使用 `docker inspect` 取得 192.168.14.216，主機改打 `http://192.168.14.216:80` 即可連線。

---

## Problem: `--link` 在 Windows Container 僅「半套」實作，導致誤判可用

**Problem**  
開發人員預期用 Linux Docker 習慣的 `--link <service>` 讓兩個容器互相解析名稱：  
```powershell
docker run -d --name web microsoft/iis
docker run -it --rm --link web microsoft/windowsservercore cmd
```  
在第二個容器中 `nslookup web` 解析得到 IP，但 `ping web` 卻失敗，造成以為網路異常。

**Root Cause**  
官方文件已標註 **Container Linking 在 Windows 尚未支援**。  
目前僅在防火牆層簡單開放流量，並未於 HNS (Host Networking Service) 中完成 DNS 設定，因此只完成了「半套」功能。

**Solution**  
1. 不再使用 `--link`，改採 Docker Network 預設的內建 DNS：直接用 service name。  
2. 若需進階 service discovery，請使用 Docker Compose / Swarm mode overlay network 等正式做法。

**Cases 1**  
• 未加 `--link`：`nslookup` 有結果但 `ping` 失敗。  
• 加 `--link`：`nslookup` 成功且 `ping` 成功，但功能僅限於當前執行中的容器；實務上仍建議捨棄。

---

## Problem: 使用 Docker-Compose 時，Service Name 解析不穩定，NGINX/應用程式啟動常常失敗

**Problem**  
Compose 定義  
```yaml
services:
  webapp:
    image: sample/webapp
  proxy:
    build: ./nginx
    depends_on: [webapp]
```  
proxy (NGINX) 啟動過程中，常因 `host not found in upstream "webapp"` 而退出，或在 `scale` 後只吃到第一台 webapp。

**Root Cause**  
1. Container 啟動早於 DNS 記錄更新，第一次查詢失敗後「負快取」被寫入 Windows DNS Client Cache (`ipconfig /displaydns`)。  
2. 後續即便 DNS 伺服器已回應正確 IP，Client Cache 仍以負快取回應，除非 `ipconfig /flushdns`。  
3. scale 增加 / 減少 service 數量時，Cache 亦不會即時失效，造成 NGINX 只看到舊 IP 清單。

**Solution**  
A. 於容器內啟動邏輯前加「等待 DNS 生效」機制。  
   範例 `start-nginx.cmd`  
   ```batch
   :loop
   ipconfig /flushdns
   nginx.exe
   powershell -c "Start-Sleep 1"
   goto loop
   ```  
B. 當 Compose `scale` 變更後，以 `docker exec` 呼叫自訂 `reload.cmd`：  
   ```batch
   ipconfig /flushdns
   nginx -s reload
   ```  
   直到 NGINX reload 成功為止。  
C. 若可調整應用程式，建議採 NGINX `resolver ... valid=30s` 或其他不使用 OS DNS Cache 的方式。

**Cases 1**  
• 導入上述 loop 之後，整組 `docker-compose up -d` 在 30–60 秒內穩定啟動，不再隨機失敗。  

**Cases 2**  
• `docker-compose scale webapp=5` 後，先執行 `docker exec proxy reload.cmd`，NGINX 即能正確分流至 5 台 Web App。

---

## Problem: 升級 Windows 10 Creators Update (1703/1704) 後，既有 `nat` Network 失效，Container 無法上網

**Problem**  
原本可正常運作的開發機在更新系統、安裝 Docker for Windows 或手動刪除/重建 HNS switch 後，所有以預設 `nat` 啟動之容器都無法 `ping 8.8.8.8`，外界也無法透過 Port Mapping 連入。

**Root Cause**  
Creators Update 引入「多個 NAT Network」與 Overlay Network 支援，升級過程中舊有 `nat` 可能殘留失效設定 (Gateway/DNS/路由表 錯誤)。雖然原因難以追溯，但實際為 **預設 nat 網路已經損毀**。

**Solution**  
1. 直接繞過舊 `nat`，另外建立一條新的 NAT Network：  
   ```powershell
   docker network create -d nat andrew-nat
   ```  
2. 啟動容器時指定新網路：  
   ```powershell
   docker run --rm -it --network andrew-nat microsoft/windowsservercore cmd.exe
   ```  
3. 經測試，新 NAT Network 連外、Port Mapping 均恢復正常。若確定新網路穩定，可考慮刪除舊 `nat` 以免混淆。

**Cases 1**  
• 新建立 `andrew-nat` 後，`ipconfig` 顯示正確 Gateway `172.17.144.1`；`ping 8.8.8.8` 全數成功，原預設 `nat` 仍失敗。  

---

以上各雷區均來自 2017/01–06 間實戰經驗，後續若 Microsoft 已更新網路堆疊，部份問題可能已消失；建議先確認最新文件或版本，再決定是否仍需套用上述繞道做法。