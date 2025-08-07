# Docker 初體驗 - Synology DSM 上面架設 WordPress / Redmine / Reverse Proxy

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Docker？它與傳統 VM 有何差異？
Docker 是一種「輕量化虛擬化」技術，它不將整個硬體虛擬化，也不需要在每個容器裡再裝一套 OS。  
容器只隔離應用程式執行環境，啟動速度通常 2～3 秒即可完成，CPU/RAM 開銷幾乎與原生執行無異，因此特別適合運算資源有限的 NAS。

## Q: Synology DSM 為何加入 Docker 是一個「天大的好消息」？
1. DSM 內建資源有限，跑傳統 VM 會拉高硬體需求；Docker 輕量化更符合家用 NAS。  
2. Docker Hub 上有大量現成映像 (image)，可隨選即用，選擇遠多於 Synology Package Center。  
3. 有統一的容器管理介面，方便做 Port Mapping、CPU/RAM 配額與 Volume 掛載。  
4. 未來若要搬遷，只要匯出容器即可直接搬到 Azure／AWS 等具備 Docker 執行環境的雲端。

## Q: 官方 WordPress 映像在 Synology 上常常 crash，該怎麼辦？
作者改用社群提供的「NGINX + PHP-FPM 版 WordPress 映像」(amontaigu/wordpress) 搭配官方 MySQL 映像，意外地完全解決了 container crash 的問題。

## Q: NGINX 是什麼？為什麼會被拿來取代 Apache？
NGINX 是由俄國人開發的高效能 Web Server，市佔約十多％。  
特色：  
1. 核心精簡，記憶體佔用低、吞吐量高。  
2. 以編譯時加入所需功能為主，不走大量動態模組的路線。  
在資源有限的家用 NAS 上特別合適。

## Q: 什麼是 Reverse Proxy？為什麼本案例一定要用到它？
Reverse Proxy（反向代理）負責接受外部用戶的請求，轉送到內部真正的 Web 服務，再把結果回傳給用戶。  
本案例中 Synology 的 Apache 已經佔用 80 埠，但 WordPress 容器只能開在 8012 埠。透過 Apache 本身的 Proxy 模組把 `http://columns.chicken-house.net/` 轉向 `http://nas:8012/`，即可讓外界仍以 80 埠存取 WordPress。

## Q: 在 Synology DSM 上如何把 WordPress 容器「映射」到 80 埠？
步驟摘要：  
1. 在 DSM「Web Station」先建立一個 Virtual Host，指向 `columns.chicken-house.net` (80)。  
2. SSH 登入 NAS，編輯 `/etc/httpd/httpd-vhost.conf-user`，於對應 VirtualHost 區塊加入：  
   ```
   ProxyPreserveHost On
   ProxyRequests     Off
   <Location />
     ProxyPass        http://nas:8012/
     ProxyPassReverse http://columns.chicken-house.net/
   </Location>
   ```  
3. 重新啟動 Apache： `httpd -k restart`  
完成後，外部使用者即可直接透過 80 埠存取 WordPress。

## Q: 使用 Docker 架 WordPress 相對於 Synology 套件中心版本有何優勢？
1. URL 不會強迫多出「/wordpress」子目錄，可維持漂亮且有利 SEO 的網址。  
2. 想架多個 WordPress，可分別跑多個容器，相互獨立、好管理。  
3. 容器可輕鬆搬遷到其他支援 Docker 的平台 (Azure/AWS 等)。  
4. Docker Hub 映像選擇遠多於 Synology 套件中心。  
5. 資源、埠、Volume 等管理更彈性，介面一致。

## Q: 修改 Apache 設定檔後要特別注意什麼？
Synology DSM 圖形介面若再次調整 Virtual Host，系統會覆寫 `/etc/httpd/httpd-vhost.conf-user`，導致自訂的 Reverse Proxy 設定遺失。  
建議修改完成後務必備份該檔案，或保留腳本以便快速還原。