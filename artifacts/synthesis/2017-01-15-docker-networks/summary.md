# 掃雷回憶錄 - Windows Container Network & Docker Compose

## 摘要提示
- Windows 容器網路現況: WS2016 上的 Windows Container 網路功能尚未完整，與成熟的 Linux/Docker 相比仍有差距
- NAT loopback 限制: WinNAT 不支援 NAT loopback，host 端無法用 localhost 存取 port-mapped 容器
- 本機測試方式: 在 host 端需以容器內部 IP+原生埠存取，非映射後的 host 埠
- 容器連結支援度: 官方宣告不支援 --link，但部分 DNS 能解析、實作不完整易誤導
- Compose 服務發現陷阱: DNS cache 導致容器間偶發解析失敗或單一 IP 固化
- NGINX 啟動策略: 以批次腳本循環清除 DNS cache 並重試啟動，確保依賴容器先可解析
- 動態擴縮對策: scale 後需 reload NGINX 並搭配清除 DNS cache 才能拿到多筆 A 紀錄
- 不穩定的 DNS 快取: Windows 內部 DNS Resolver Cache 可能在容器未就緒時寫入「不存在」紀錄
- Creator Update 影響: Windows 10 1704 後預設 nat 網路可能失效，另建新 NAT 網路可繞過
- 未支援項目: 多項 docker network 參數在 Windows 尚未支援，正式導入需審慎規避

## 全文重點
作者記錄在 Windows Server 2016/Windows 10 上實作 Windows Container 與 Docker Compose 的踩雷過程。核心問題圍繞在容器網路實作未臻完善、WinNAT 能力限制與 Windows DNS 快取行為，導致在單機與 Compose 場景中出現連線、解析不穩定的狀況。

首先，WinNAT 不支援 NAT loopback，因此即便容器有埠對映，host 端仍無法用 localhost:hostPort 存取容器服務。正確方式是在 host 外部以 hostIP:hostPort 存取；若要在 host 自測，需改以容器內部 IP + 容器原生埠連線。這點常讓熟悉 Linux Docker 的使用者誤判為配置錯誤。

第二，官方已宣稱不支援 container linking (--link)。實測中卻出現「DNS 可解析、但連線/封包不通或行為不一致」的半支援狀態，易讓人誤以為可用。整體觀察顯示，Windows container engine 會提供基本的容器名稱解析，但 --link 的全套語義並未完整落實，應避免依賴。

第三，Compose 場景的服務發現屢遇不穩。作者以 NGINX 作為前端，後端多個 ASP.NET 容器負載平衡，卻碰到「nslookup 解析得到 IP，但 ping 名稱不通；或 DNS cache 記錄為不存在 Name does not exist」等現象。追查後發現是 Windows DNS Resolver Cache 在「服務尚未就緒」時被寫入負面結果，且沒有 TTL，導致後續解析持續命中錯誤快取。為此作者以批次腳本在 NGINX 啟動流程中迴圈清除快取並重試啟動，直到解析成功；擴縮（scale）後亦提供 reload 腳本先清快取再重載 NGINX，以取得多筆 A 紀錄。這一連串 workaround 雖可穩住行為，但凸顯 Windows 上 DNS 快取與容器網路的時序性問題。

第四，在 Windows 10 升級至 Creator Update (1704) 後，預設 docker network: nat 出現容器無法出外網的問題。雖然 docker network inspect 顯示配置正常，但容器內無法 ping 外部。作者最終以「另建一個新的 nat 網路，並於 docker run 指定 --network 新網路」解決，顯示升級或先前改動可能使預設 nat 狀態不一致；而 1704 同時帶來 multiple NAT 與 overlay network 支援，也意味著功能轉換期更需留意相容性。

文章最後列出 Windows Docker 尚未支援的網路選項（如 --add-host、--dns-opt、--dns-search、--ip-range 等），並建議除非迫切需求，否則先避開易踩雷的進階功能；並持續關注 Microsoft 之後的修正。總結來說，Windows Container 能讓既有 ASP.NET 應用容器化具備實際價值，但目前網路堆疊和 DNS 行為仍需透過腳本與配置繞行，正式上線前應充分驗證並預留回復機制。

## 段落重點
### 前言與環境說明
作者在 Windows Server 2016 實機上實作 Windows Container 與 Docker Compose，版本為 10.0.14393，Docker 1.12.2-cs2-ws-beta、Compose 1.10.0-rc1。強調 Windows Container 與 Docker 在網路面仍有差距，特別是 overlay network 尚未到位，導致 swarm 模式受限；Azure 上的容器服務已有私測支援，顯示功能將落地。本文聚焦記錄在容器網路與 Compose 實作中遇到的實務坑並給出暫時解法。

### Overview: Windows Container networking
官方文件為首要參考，能省去大量試錯。Windows 採用 WinNAT 提供容器 NAT 能力，具備與 Linux 不同的限制與行為。文中環境以實體機安裝 Windows Server 2016 並用 Docker CLI 檢視版本，提醒讀者務必對照官方網路文件內的支援矩陣與限制，避免踩過時功能與語義的坑。

### 1. container port mapping 無法在本機 (container host) 使用
WinNAT 不支援 NAT loopback，導致 host 端無法用 localhost:hostPort 連向映射的容器服務。對外機器可用 hostIP:hostPort 正常連線；若要在 host 上測試，需以 docker inspect 取得容器內部 IP，並以容器原生埠連線。Windows 14300 之後會自動建立對應的防火牆規則，無需手動開孔。本節以 IIS 容器為例，逐步示範在本機/遠端的測試方式與原因說明，提醒讀者認知與 Linux 行為的差異。

### 2. container link 官方宣稱不再支援
官方列為不支援的 --link，在測試中出現「DNS 能查到容器名」但行為不一致的半支援現象：加上 --link 時可 nslookup 與 ping；不加時 nslookup 仍解析到 IP，ping 卻失敗，顯示僅部分機制（如名稱解析或流量白名單）被實作。結論是「別依賴 --link」，但可利用引擎提供的容器名稱 DNS 解析做服務發現。此段強化「以文件為準」與「避免誤以為可用」的提醒。

### 3. docker-compose 的 service discovery 無效問題
Compose 架構為 NGINX 反向代理 + 2 個 ASP.NET WebApp + console 測試容器。實際運作時偶發 NGINX 啟動失敗，回報找不到 webapp；或在 console 容器中 nslookup 可得 IP 但 ping 名稱失敗。追根究柢是 Windows DNS Resolver Cache 在依賴容器未就緒時寫入「不存在」或單一 IP 的快取，且可能無 TTL 不更新，造成後續解析一直命中錯誤。對策：將 NGINX 啟動改成批次檔循環清除 DNS cache 並重試（直到成功），縮放（scale）後亦提供 reload 腳本，先 flushdns 再 nginx -s reload 以取得多筆 A 記錄。作者也研究 NGINX resolver 參數但未在 Windows 版成功，決定以外部腳本維持穩定。此段凸顯 Compose 下服務發現與 DNS 快取時序問題及實務繞法。

### 4. Windows 10 升級 Creator Update (1704) 後, container network 就無法連線了
升級後遇到容器無法對外連線的狀況，預設 nat 看似正常但容器 ping 外部失敗。經嘗試以「另建一個新的 nat 網路」並在 docker run 指定 --network 新網路後恢復正常。1704 引入 multiple NAT 與 overlay network 支援，亦為 swarm 模式鋪路；但過程可能導致既有 nat 狀態不一致。暫行作法是避用預設 nat、改用自建 nat。此段提供檢測與修復步驟，讓讀者在遇到類似問題時能快速定位與繞過。

### 後記與未支援清單
作者仍看好 Windows Container 對既有 ASP.NET 的容器化價值，但在網路與 DNS 等面向仍待完善。官方尚未支援的網路選項包含 --add-host、--dns-opt、--dns-search、--aux-address、--internal、--ip-range 等。建議目前先避開進階功能，穩健試行、回報 issue，待 Microsoft 修正再導入。並提醒文內狀態為 2017/01/15 之後的觀察，讀者應以最新文件與實測為準，若已修復也歡迎回饋社群。

## 資訊整理

### 知識架構圖
1. 前置知識
   - Docker 與容器基本概念（鏡像、容器、port mapping、network）
   - Windows Server 2016/Windows 10 容器基礎（Windows Server Containers、Hyper-V、HNS）
   - 網路基本概念：NAT、NAT loopback、DNS、DNS cache、端口轉發
   - Docker Compose 基礎（服務、depends_on、scale）
   - 反向代理與負載平衡（以 NGINX 為例）

2. 核心概念
   - WinNAT 與 NAT loopback 限制：Windows 容器使用 WinNAT，不支援 NAT loopback，導致 host 無法用 localhost:host_port 測試容器服務
   - 容器 DNS/service discovery 行為：Windows 上 DNS 解析可由引擎提供（以容器名為主機名），但會受 Windows DNS Resolver Cache 影響，可能出現查詢到 IP 但無法 ping 主機名、或舊快取未更新等問題
   - Docker Compose 在 Windows 上的特性與坑：--link 不支援（或只部分行為），Compose 的 scale 後 DNS 多 A 紀錄需處理快取與應用端重載
   - 網路驅動與版本差異：Windows 容器 nat/overlay 能力逐步補齊（Creators Update 起支援 multiple NAT、overlay），舊預設 nat 可能損壞需新建
   - 問題診斷與繞路：以 ipconfig、nslookup、ping、docker network/inspect、flushdns、建立新 NAT network、在 NGINX/啟動腳本中處理 DNS 時機

3. 技術依賴
   - Docker Engine for Windows（Windows Server 2016/Windows 10）
   - HNS/WinNAT 提供 NAT、端口映射、防火牆規則自動化（14300+）
   - Windows DNS Resolver 與其快取（ipconfig /displaydns、/flushdns）
   - Docker Networking（nat、overlay；network create/inspect）
   - NGINX 反向代理（Windows 版；resolver/重載）
   - IIS 容器、Windows Server Core/Nano Server 映像

4. 應用場景
   - 在 Windows 上以 Compose 啟動多容器微服務（IIS 後端 + NGINX 前端）
   - 本機開發/測試 Windows 容器服務（處理無 NAT loopback 的限制）
   - 以 Compose scale 擴展服務並調整上游解析/重載策略
   - 在 Windows 10 更新後（Creators Update）修復損壞的預設 nat 網路
   - 初探/過渡期使用 Docker Swarm/overlay（功能逐步落地時）

### 學習路徑建議
1. 入門者路徑
   - 安裝 Docker for Windows（或 Windows Server 2016 上安裝 Docker）
   - 了解基本指令：docker run/ps/inspect、port mapping、volume
   - 實作簡單 IIS 容器並從遠端以 host_ip:host_port 存取；在本機以容器內 IP 測試
   - 學會查看容器 IP、docker network inspect 與基本網路概念（NAT loopback 不支援）

2. 進階者路徑
   - 使用 Docker Compose 定義多服務（webapp、proxy、console），掌握 depends_on、ports、build/command
   - 熟悉 Windows 上 DNS 行為：nslookup、ping、ipconfig /displaydns、/flushdns
   - 對付 DNS 不一致：在啟動腳本中等待 DNS 可用、清快取；為 NGINX 加入 reload 流程
   - 建立自訂 nat 網路並指定 --network 啟動；學會 network create/inspect

3. 實戰路徑
   - 建立 NGINX 反向代理容器，將流量代理到 webapp；以 Compose scale 擴容並驗證多 A 紀錄
   - 設計健壯的啟動流程：啟動迴圈（flushdns + 啟動/重載 NGINX），確保 DNS 就緒
   - 發生網路異常（如更新後斷網）時：新建 nat 網路、將服務切換到新網路、回歸測試
   - 梳理不可用功能與限制，調整部署策略（暫避 overlay、--link、dns-opt 等）

### 關鍵要點清單
- WinNAT 不支援 NAT loopback: 在 Windows 容器中 host 端無法用 localhost:host_port 直測，需用容器內 IP:container_port 或遠端 host_ip:host_port 測試 (優先級: 高)
- 容器端口映射防火牆自動規則: 14300+ 版會自動建立對應防火牆規則，通常無需手動開放 (優先級: 中)
- 以 docker inspect 取得容器 IP: 在本機測試需用容器內部 IP 與原生服務端口 (優先級: 高)
- --link 在 Windows 不支援/僅部分行為: 官方標記不支援，實測可能出現 DNS 不一致的誤導現象 (優先級: 高)
- Windows DNS Resolver Cache 影響容器發現: 可能留下「Name does not exist」或單一 A 紀錄的殘留，導致 ping/應用解析失敗 (優先級: 高)
- 清快取與等待 DNS 就緒: 使用 ipconfig /flushdns 並在啟動腳本中重試，確保解析可用 (優先級: 高)
- Compose scale 後多 A 紀錄: DNS 會返回多 IP，但本機快取可能只留單一；需清快取或讓應用定期重新解析 (優先級: 高)
- NGINX 在 Windows 的 DNS 行為: 預設依 TTL 快取，建議使用 resolver/valid 或重載機制來更新上游解析（Windows 版配置可能需實測調整） (優先級: 中)
- 啟動/重載腳本實務: 以迴圈（flushdns -> 啟動/重載 -> 等待）確保依賴服務可用，避免不確定性 (優先級: 高)
- 檢測工具組合: nslookup、ping、ipconfig /displaydns|/flushdns、docker network inspect 是核心排障組合 (優先級: 高)
- Windows 10 Creators Update 變更: 加入 multiple NAT 與 overlay 支援，但可能導致既有 nat 網路異常 (優先級: 中)
- 建立新 NAT 網路繞過異常: 用 docker network create -d nat 新建網路，並以 --network 指定運行容器 (優先級: 高)
- 了解未支援網路選項: --add-host、--dns-opt、--dns-search、--aux-address、--internal、--ip-range 等在當時不支援 (優先級: 中)
- Overlay/Swarm 支援逐步落地: 雲端/新版本逐漸支援跨 Windows/Linux 節點，但本機端可能尚有差異與坑 (優先級: 低)
- 版本與環境一致性: 記錄 OS/Engine/Compose 版本，有助重現與定位 Windows 特有問題 (優先級: 中)