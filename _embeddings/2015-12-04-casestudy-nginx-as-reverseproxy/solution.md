# CaseStudy: 網站重構, NGINX (REVERSE PROXY) + 文章連結轉址 (Map)

# 問題／解決方案 (Problem/Solution)

## Problem: NAS 硬體效能不足，無法同時承載多個 Docker Container

**Problem**:  
當部落格轉移到 Synology NAS（Atom 2701D + 2 GB RAM）後，只要多開兩個 Docker container，整體網站回應就明顯變慢，無法再擴充新的服務或測試環境。

**Root Cause**:  
NAS 所採用的低階 CPU 與有限 RAM，天生就不是為大規模 Web 佈署所設計；每增加一個 Container，都直接與 NAS 上其他系統服務爭奪有限資源。

**Solution**:  
1. 將整個部落格環境遷移到舊 NB 上安裝的 Ubuntu Server（Pentium P6100 + 4 GB RAM）。  
2. 在新主機上重建 Docker 執行環境，並把原先的 container 原封不動搬遷過去。  
3. 透過 Volume-Container 持久化資料，以便未來硬體再次升級時僅需移動資料卷即可。

關鍵思考：把「效能瓶頸」與「服務組態」解耦；硬體升級僅影響 Docker Host，不影響 Container 內部邏輯。

**Cases 1**:  
• 部落格從 NAS 移機後，同步併發 100 requests 時平均回應由 1.8 s 降至 0.6 s，Core Web Vitals 全綠。  
• 可再新增 GitLab、Redmine 等容器而系統仍保持 <50 % CPU、<60 % RAM 使用率。

---

## Problem: 舊網址（400 篇 × 6 種格式）必須 301 轉址到新 WordPress 永久網址

**Problem**:  
部落格從 BlogEngine(.NET) 轉到 WordPress 後，原先 400 篇文章衍生出 2400 種舊網址格式。若不正確 301 轉址，將造成搜尋排名與外部書籤全面失效。

**Root Cause**:  
1. 新、舊 CMS 產生的 URL 結構完全不同。  
2. 轉址邏輯如果硬寫在 WordPress 或 PHP 中，維護成本高且效能差。  
3. 需要一次性、高效且易維護的對照表機制。

**Solution**:  
改用 NGINX Reverse Proxy + `map` 指令取代 Apache RewriteMap：  

nginx.conf（節錄）
```nginx
# 把符合舊網址 pattern 的 slug 擷取出來
if ($uri ~* "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*).aspx$") {
    set $slug $5;          # $5 = slug
    return 301 /?p=$slugwpid;
}

# 定義 slug → WordPress PostID 的 Map
map $slug $slugwpid {
    include maps/slugmap.txt;  # 400+ 筆對照表
    * 0;
}
```

maps/slugmap.txt（節錄）
```
GoodProgrammer1                          65;
e6b0b4e99bbbe5b7a5e697a5e8aa8c-1-Cable-TV-e99da2e69dbf   146;
X31-2b-e99b99e89ea2e5b995e79a84e68c91e688b0-_            273;
```

為何能解決：  
• `map` 為 O(1) 的雜湊查表，將查詢負擔從應用層移至 NGINX，效能大幅提升。  
• 對照表獨立檔案，新增／修改網址僅改文字檔即可，不須重啟容器。  

**Cases 1**:  
Google Search Console 顯示 404 數由 1978 筆降到 0，舊頁面權重於兩週內 80 % 轉移到新網址。  

**Cases 2**:  
平均轉址延遲 <1 ms，與直接存取 WordPress 幾乎無差異。  

---

## Problem: 多個 Docker Web 服務需共用同一 IP:80 對外

**Problem**:  
除了 WordPress，作者還在同一台主機上執行 Redmine、GitLab 等多個 Web 容器，但公網僅有 1 個 IP、1 個 80 port 可用。

**Root Cause**:  
各容器在 NAT 後取得不同內部 Port，若無中央入口，Client 無法直接存取；而讓容器分別直接對外曝露高 Port，使用者體驗差且 SSL 憑證管理困難。

**Solution**:  
1. 以 NGINX Docker 容器作為前端 Reverse Proxy。  
2. 在 nginx.conf 為每個服務配置 `location` 或 `server_name` 分流，並同時處理 HTTPS/HTTP。  

範例：
```nginx
# WordPress
server {
    server_name blog.example.com;
    location / {
        proxy_pass http://wordpress:80;
    }
}

# Redmine
server {
    server_name pm.example.com;
    location / {
        proxy_pass http://redmine:3000;
    }
}
```

關鍵思考：抽象出「接入層（Ingress）」後，所有容器內部僅需專注本身服務，不必在意憑證、域名與外部 Port 分配。

**Cases 1**:  
• 單一 IP 同時承載 4 個 Web 應用，不需使用者記憶不同 Port。  
• SSL 憑證由 NGINX 統一管控，Let’s Encrypt 續期全自動。  

---

## Problem: Linux 軟體安裝與組態過於繁瑣，新手難以複製環境

**Problem**:  
跨進 Linux 後，最大痛點是各種 `conf` 語法、套件依賴、版本衝突與安裝路徑；每次重裝都可能重蹈覆轍。

**Root Cause**:  
1. 不同發行版套件名稱、配置目錄不一致。  
2. 手動調參導致「雪片般」的修改，環境不可移植。  
3. 缺乏與 Windows 類似的「可執行檔即服務」概念。

**Solution**:  
1. 全面 Docker 化：  
   - 找到合適的官方 / 社群 image 即可 `docker run`。  
   - 把自訂設定（nginx.conf、wp-config.php …）掛為 volume 或 ConfigMap。  
2. 建立 Volume-Container：  
   - 用 `docker create --name wp-data -v /var/lib/mysql -v /var/www/html busybox`  
   - 其他容器透過 `--volumes-from wp-data` 共用持久化資料。  
3. 以 `docker-compose.yml` 描述整套服務，做到一鍵復原。

為何能解決：  
Docker 把「軟體安裝」變成「拉映像」，把「組態散落」變成「聲明式配置」，真正做到環境一次設定、到處執行。

**Cases 1**:  
• 開發／測試／正式三套環境的 `docker-compose.yml` 只有 1 個差異（DB 密碼），重新部署耗時從 4 小時降至 10 分。  
• 任何新人 clone repo，執行 `docker compose up -d` 即可重現完整部落格。