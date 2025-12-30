---
layout: synthesis
title: "掃雷回憶錄 - Windows Container Network & Docker Compose"
synthesis_type: solution
source_post: /2017/01/15/docker-networks/
redirect_from:
  - /2017/01/15/docker-networks/solution/
---

以下內容將文章中的所有問題解決實務拆解為可教學、可演練、可評估的 15 個案例，皆遵循統一結構，含問題、根因、方案、實作步驟、關鍵程式碼、實測成效與練習與評估要點。案例環境除另行註明外，均以文中環境為主：
- Windows Server 2016 (10.0.14393) / 非 VM
- Docker 1.12.2-cs2-ws-beta
- Docker Compose 1.10.0-rc1
- 預設 Docker network: nat


## Case #1: Windows 容器主機無法用 localhost 連到容器的對應埠（NAT loopback 不支援）

### Problem Statement（問題陳述）
業務場景：在 Windows Server 2016 主機上起一個 IIS 容器，將容器的 80 對外映射到主機 8000，用於本機驗證與除錯。開發者希望用 http://localhost:8000 直接從主機測試服務可用性。
技術挑戰：Windows 容器使用 WinNAT，未支援 NAT loopback（hairpin NAT），導致主機自己無法透過映射的主機埠回打到容器。
影響範圍：本機無法測試，易誤判為服務未啟動或防火牆封鎖，拖慢開發與除錯效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. WinNAT 缺乏 NAT loopback 支援，無法 hairpin 回到同一主機上映射的容器埠。
2. Docker on Windows 採用 WinNAT，port mapping 在本機不生效。
3. 參考 Linux 經驗（可用 localhost 測試）導致錯誤預期。

深層原因：
- 架構層面：NAT 實作不支援 loopback。
- 技術層面：Windows networking stack（WinNAT）限制。
- 流程層面：測試與診斷步驟未區分主機本機與遠端測試行為差異。

### Solution Design（解決方案設計）
解決策略：分離本機與遠端測試路徑。本機測試以容器「內部 IP + 內部埠」存取；遠端測試以「主機對外 IP + 映射埠」驗證。建立一套快速查 IP 的標準流程與指令範本。

實施步驟：
1. 建立容器與埠映射
- 實作細節：將容器 80 對外映射至主機 8000
- 所需資源：Docker Engine
- 預估時間：5 分鐘
2. 遠端驗證
- 實作細節：用其他電腦透過 http://<HOST_IP>:8000 測試
- 所需資源：同網段任一主機
- 預估時間：5 分鐘
3. 本機驗證（用容器 IP）
- 實作細節：以 docker inspect 取得容器 IP，改用 http://<CONTAINER_IP>:80
- 所需資源：Docker CLI
- 預估時間：5 分鐘

關鍵程式碼/設定：
```powershell
# 建立 IIS 容器並映射埠
docker run -d --name demo-iis -p 8000:80 microsoft/iis

# 遠端機器測試
# 瀏覽 http://<HOST_IP>:8000

# 本機查容器 IP 並測試（以容器原始埠）
docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" demo-iis
# 例如顯示 192.168.14.216
# 本機瀏覽 http://192.168.14.216:80/
```

實際案例：文中以 demo-iis 為例，本機 http://localhost:8000 失敗；遠端 http://<HOST_IP>:8000 成功；本機用容器 IP+80 成功。
實作環境：Windows Server 2016 (10.0.14393), Docker 1.12.2-cs2-ws-beta
實測數據：
改善前：localhost:8000 本機 0% 成功
改善後：本機用容器 IP + 80、遠端用 HOST_IP + 8000 → 100% 成功
改善幅度：+100%（對本機可測角度）

Learning Points（學習要點）
核心知識點：
- WinNAT 不支援 NAT loopback
- 容器「對外映射埠」與「容器內部埠」的差異
- 遠端與本機測試方法不同

技能要求：
- 必備技能：Docker 基本操作（run、inspect）
- 進階技能：網路測試與診斷（瀏覽器、curl）

延伸思考：
- 若需本機以 localhost 測試，是否可用反向代理或 portproxy（非本文範圍）？
- 在 CI/CD pipeline 中如何自動化容器 IP 提取與驗證？
- 是否以健康檢查來取代人工作業？

Practice Exercise（練習題）
基礎練習：建立 IIS 容器並以容器 IP 驗證（30 分鐘）
進階練習：撰寫腳本自動取得容器 IP 並以 curl 測試（2 小時）
專案練習：做一個本機/遠端雙通路驗證腳本與報表（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能從本機與遠端正確驗證服務
程式碼品質（30%）：腳本結構清晰、錯誤處理完善
效能優化（20%）：驗證耗時短、重試策略合理
創新性（10%）：提供額外的本機代理/自動化改進


## Case #2: 快速取得容器內部 IP 的實務（加速本機驗證與除錯）

### Problem Statement（問題陳述）
業務場景：團隊需在主機本機快速驗證容器服務可用性，但 NAT loopback 限制導致需改用容器內部 IP。若每次用 docker inspect 手動翻找，耗時且易出錯。
技術挑戰：如何用最少指令、最高準確度取得容器在 nat 上的 IP。
影響範圍：本機驗證與除錯效率顯著受影響。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 容器 IP 由 Docker 與 Windows HNS 動態分配，非固定。
2. 不熟悉 docker inspect 的累進式查詢語法，人工搜尋浪費時間。
3. 未形成標準化查詢指令範本。

深層原因：
- 架構層面：容器網路為虛擬化網段，IP 不固定。
- 技術層面：inspect 輸出結構化 JSON，需查詢路徑。
- 流程層面：缺少標準作業流程（SOP）與工具化。

### Solution Design（解決方案設計）
解決策略：建立可重用的一行指令範本，直接取回 nat 網段的容器 IP；搭配 alias 或腳本固化流程，降低人工成本。

實施步驟：
1. 建立標準查詢指令
- 實作細節：docker inspect -f filter 語法
- 所需資源：Docker CLI
- 預估時間：10 分鐘
2. 將指令包裝成腳本/alias
- 實作細節：Windows 批次檔或 PowerShell 函數
- 所需資源：PowerShell / cmd
- 預估時間：20 分鐘

關鍵程式碼/設定：
```powershell
# 精準取得指定容器在 nat 網路中的 IP
docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" <container-name>

# 例如：
docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" demo-iis
# 輸出：192.168.14.216
```

實際案例：文中用該查詢快速找到 demo-iis 的 192.168.14.216，完成本機以容器 IP 測試。
實作環境：Windows Server 2016 (10.0.14393), Docker 1.12.2-cs2-ws-beta
實測數據：
改善前：開發者手動翻 inspect 結果，耗時 ~1 小時除錯
改善後：一行指令直接輸出 IP，耗時 < 10 秒
改善幅度：> 99% 時間節省（就緒時間）

Learning Points（學習要點）
核心知識點：
- docker inspect templating filter
- 容器多網卡/多網路時的查詢技巧
- 快速驗證流程標準化

技能要求：
- 必備技能：Docker CLI 與 inspect
- 進階技能：PowerShell/批次檔封裝

延伸思考：
- 多 network 場景如何選取正確網路？
- 是否能加入健檢（HTTP 200/握手）一步到位？

Practice Exercise（練習題）
基礎練習：為三個容器輸出 IP 清單（30 分鐘）
進階練習：寫一支 get-container-ip.ps1 並支援 network 參數（2 小時）
專案練習：製作容器服務健康檢查器（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可針對指定 network 正確輸出 IP
程式碼品質（30%）：可維護性與錯誤處理
效能優化（20%）：大量容器時仍快速
創新性（10%）：整合健康檢查/報表


## Case #3: 不要用 --link：Windows 上連結支援不完整，改用 DNS-based 服務發現

### Problem Statement（問題陳述）
業務場景：要讓兩個容器互通，嘗試使用 Docker 傳統 --link，但在 Windows 環境出現行為不一致（有時通、有時不通）。
技術挑戰：官方文件標註 container linking 不支援，實測卻出現部分可用的混淆狀態（例如加了 --link 時 nslookup/ping 正常；未加時 nslookup 有 IP 但 ping 找不到）。
影響範圍：配置混亂、除錯浪費時間、可靠性不足。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 官方聲明 Windows 不支援 container linking（--link）。
2. Windows 實作疑似只處理部分網路/防火牆層級，DNS/名稱解析行為不一致。
3. 以 ping 作為唯一驗證易被 DNS cache/解析路徑影響。

深層原因：
- 架構層面：Windows 容器網路堆疊與 Linux 差異，Legacy linking 不再主推。
- 技術層面：預設 network 已提供內建 DNS 服務發現。
- 流程層面：沿用過往習慣未切換至服務名稱（service name）模式。

### Solution Design（解決方案設計）
解決策略：全面改用預設 network 的 DNS 服務發現，以容器/服務名稱通訊；停止依賴 --link。驗證時以 nslookup/實際應用層連線為主。

實施步驟：
1. 啟動服務容器（不使用 --link）
- 實作細節：起 demo-iis（IIS）
- 所需資源：Docker
- 預估時間：5 分鐘
2. 啟動測試容器，驗證 DNS
- 實作細節：nslookup 服務名；避免以 ping 作唯一依據
- 所需資源：microsoft/windowsservercore
- 預估時間：10 分鐘
3. 在應用中改用服務名連線
- 實作細節：proxy 對後端用主機名（如 webapp）
- 所需資源：應用設定/NGINX
- 預估時間：30 分鐘

關鍵程式碼/設定：
```powershell
# 啟動服務容器（無 --link）
docker run -d --name demo-iis microsoft/iis

# 在另一個容器中驗證 DNS 解析
docker run -it --rm microsoft/windowsservercore cmd.exe

# 容器內
nslookup demo-iis
# 避免以 ping 作唯一驗證依據
```

實際案例：文中觀察到未加 --link 時 nslookup 有 IP，但 ping 仍回報找不到；提醒不要以 ping 作唯一驗證，並改走服務名稱與 DNS 服務發現。
實作環境：同上
實測數據：
改善前：依賴 --link 與 ping，行為不一致，成功率不穩定
改善後：改用服務名（DNS），行為一致可預期
改善幅度：穩定度顯著提升（不確定 → 穩定）

Learning Points（學習要點）
核心知識點：
- Windows 上不支援 --link
- 預設 network 的 DNS 服務發現
- 驗證工具選擇：nslookup/應用層連線優於 ping

技能要求：
- 必備技能：Docker run、基本 DNS
- 進階技能：以服務名設計系統拓撲

延伸思考：
- 在 Compose/Swarm 中以服務名通訊的最佳實踐？
- 健康檢查與重試策略如何輔助？

Practice Exercise（練習題）
基礎練習：兩個容器以服務名互通（30 分鐘）
進階練習：將應用設定改為服務名（2 小時）
專案練習：以服務名完成一個含 proxy/backend 的小系統（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：去除 --link 後互通正常
程式碼品質（30%）：設定清晰、可維護
效能優化（20%）：DNS 解析延遲可控
創新性（10%）：加入健康檢查或重試機制


## Case #4: nslookup 找得到、ping 找不到：定位到 Windows DNS 負快取

### Problem Statement（問題陳述）
業務場景：容器間通訊時，nslookup 已解析出目標服務 IP，但 ping 卻回報「找不到主機」。導致誤判目標服務不可達。
技術挑戰：兩種工具輸出互相矛盾，難以判斷真因。
影響範圍：診斷時間拉長、啟動流程不穩定。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Windows DNS Resolver Cache 內存在 webapp 的負快取（Name does not exist）。
2. ping 優先讀本機快取，未再查詢 DNS。
3. 容器啟動早期寫入的負快取無 TTL，長期不更新。

深層原因：
- 架構層面：Resolver Cache 行為與工具（ping/nslookup）查詢路徑差異。
- 技術層面：容器啟動序與 DNS 記錄更新有時間差。
- 流程層面：缺少快取檢視與清理步驟。

### Solution Design（解決方案設計）
解決策略：以 ipconfig /displaydns 觀察快取狀態辨識負快取；以 ipconfig /flushdns 清除快取後重試。將快取檢視與清理納入標準排錯流程。

實施步驟：
1. 觀察 DNS 快取
- 實作細節：ipconfig /displaydns 檢視 webapp 項目
- 所需資源：容器內 cmd.exe
- 預估時間：5 分鐘
2. 清除快取並重試
- 實作細節：ipconfig /flushdns；重跑 ping/nslookup
- 所需資源：同上
- 預估時間：5 分鐘

關鍵程式碼/設定：
```bat
ipconfig /displaydns
rem 若看到 webapp -> Name does not exist 即為負快取

ipconfig /flushdns
ping webapp
```

實際案例：文中發現 webapp 在 Resolver Cache 中為「Name does not exist」，清除快取後重試數次才恢復。
實作環境：同上
實測數據：
改善前：nslookup 有 IP、ping 失敗
改善後：多次 flush 後，ping 成功
改善幅度：從不確定 → 可恢復（仍需多次嘗試）

Learning Points（學習要點）
核心知識點：
- Windows DNS Resolver Cache 行為
- nslookup 與 ping 差異
- 快取檢視/清理

技能要求：
- 必備技能：Windows 網路指令
- 進階技能：排錯流程化

延伸思考：
- 是否能建立自動重試與指數退避？
- 應用層是否應避免依賴 ICMP 驗證？

Practice Exercise（練習題）
基礎練習：在容器內重現並清理負快取（30 分鐘）
進階練習：撰寫 flush+驗證的批次檔（2 小時）
專案練習：整合到啟動前健檢腳本（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能辨識與清理負快取
程式碼品質（30%）：腳本健壯
效能優化（20%）：重試策略合理
創新性（10%）：自動化可視化


## Case #5: NGINX 啟動失敗（DNS 未就緒）— 用 start-nginx.cmd 等待 DNS 就緒再啟動

### Problem Statement（問題陳述）
業務場景：以 docker-compose 啟動 proxy（NGINX）與 webapp，proxy 偶發「host not found in upstream」後退出，導致整組應用啟動不穩定。
技術挑戰：webapp 的 DNS 記錄尚未就緒或被負快取，NGINX 啟動即讀不到 upstream。
影響範圍：部署啟動不確定，可能半夜重啟失敗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. NGINX 啟動時查不到 webapp 的 DNS。
2. Windows Resolver Cache 可能存有負快取。
3. depends_on 只保證啟動順序，不保證服務可用。

深層原因：
- 架構層面：服務就緒與名稱解析存在時間差。
- 技術層面：NGINX 啟動行為需依賴 DNS 成功。
- 流程層面：缺少啟動前重試/等待機制。

### Solution Design（解決方案設計）
解決策略：將 NGINX 啟動封裝在批次檔，以無限迴圈清理 DNS 快取並嘗試啟動，直到成功。透過 docker-compose 的 command 呼叫該腳本。

實施步驟：
1. 編寫 start-nginx.cmd
- 實作細節：flushdns → nginx.exe → sleep → loop
- 所需資源：批次檔、NGINX
- 預估時間：30 分鐘
2. 調整 compose 以 command 啟動
- 實作細節：在 proxy 服務使用 command 指定腳本
- 所需資源：docker-compose.yml
- 預估時間：10 分鐘

關鍵程式碼/設定：
```bat
:: start-nginx.cmd
cd /d c:\nginx
:loop
ipconfig /flushdns
nginx.exe
powershell /c sleep 1
goto loop

# docker-compose.yml (片段)
services:
  proxy:
    build: ./mvcproxy
    command: start-nginx.cmd
    depends_on:
      - webapp
    ports:
      - "80:80"
```

實際案例：文中加入 start-nginx.cmd 後，多次啟動皆能在 30~60 秒內成功穩定啟動。
實作環境：同上
實測數據：
改善前：啟動偶發失敗（host not found）
改善後：0.5~1 分鐘內穩定啟動
改善幅度：啟動穩定性由不確定 → 100%

Learning Points（學習要點）
核心知識點：
- 啟動前等待與重試模式
- depends_on 與「就緒」的差異
- DNS 快取清理對啟動的影響

技能要求：
- 必備技能：批次檔、Compose 配置
- 進階技能：設計健壯的重試策略

延伸思考：
- 是否用健康檢查（healthcheck）替代？
- 可否以 backoff 控制重試頻率與上限？

Practice Exercise（練習題）
基礎練習：將 NGINX 啟動改為腳本控制（30 分鐘）
進階練習：加入最大重試次數與日誌（2 小時）
專案練習：建立通用「等待就緒」模板，供多服務重用（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：啟動穩定、能自我恢復
程式碼品質（30%）：腳本可維護、日誌清楚
效能優化（20%）：等待時間與重試策略合理
創新性（10%）：加入健康檢查、超時保護


## Case #6: depends_on 只能控順序不保證可用性：以啟動腳本補齊「就緒」能力

### Problem Statement（問題陳述）
業務場景：docker-compose 使用 depends_on 控制 webapp 先於 proxy 啟動，但 NGINX 仍偶發無法解析 webapp 而失敗。
技術挑戰：depends_on 僅控制容器啟動順序，並不等待服務真正 ready（含 DNS 就緒）。
影響範圍：啟動流程不穩，需人為介入。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. depends_on 不包含 readiness sematics。
2. Windows 的 DNS 就緒與快取刷新需要時間。
3. NGINX 啟動即刻讀 upstream 導致失敗。

深層原因：
- 架構層面：編排工具與應用啟動時序解耦。
- 技術層面：缺少健康檢查或等待機制。
- 流程層面：預期與實際行為不一致。

### Solution Design（解決方案設計）
解決策略：沿用 depends_on 控制順序，再以啟動腳本（Case #5）提供 readiness gating：反覆 flushdns + 啟動，直到成功。

實施步驟：
1. 在 compose 配置 depends_on
- 實作細節：proxy depends_on webapp
- 所需資源：docker-compose.yml
- 預估時間：5 分鐘
2. 將啟動邏輯外移到 command/腳本
- 實作細節：見 Case #5
- 所需資源：批次檔
- 預估時間：30 分鐘

關鍵程式碼/設定：
```yaml
services:
  proxy:
    build: ./mvcproxy
    command: start-nginx.cmd
    depends_on:
      - webapp
```

實際案例：文中將啟動寫到 command 與腳本後，proxy 能在 webapp 就緒與 DNS 可解後自然啟動。
實作環境：同上
實測數據：
改善前：偶發失敗
改善後：穩定啟動（30~60 秒內）
改善幅度：由非決定性 → 決定性

Learning Points（學習要點）
核心知識點：
- depends_on 侷限
- readiness 與 liveness 概念
- 外掛腳本解耦啟動與就緒

技能要求：
- 必備技能：Compose 配置
- 進階技能：啟動腳本與健檢設計

延伸思考：
- 升級到支援 healthcheck 的流程？
- 以 sidecar 方式提供等待器？

Practice Exercise（練習題）
基礎練習：為 proxy 加上 depends_on（30 分鐘）
進階練習：增設等待 webapp TCP:80 可用的偵測（2 小時）
專案練習：將等待器抽象成可重用容器（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：順序與就緒皆滿足
程式碼品質（30%）：配置清晰、可維護
效能優化（20%）：等待機制不過度
創新性（10%）：健康檢查/sidecar 設計


## Case #7: Compose 擴編（scale）後 DNS 仍只指到一台：用 flush + nginx reload 更新 upstream

### Problem Statement（問題陳述）
業務場景：webapp 由 1 台擴編至 5 台後，proxy 仍只連到第一台，負載均衡失效。
技術挑戰：容器內的 DNS 快取仍保留單一 A record，未載入新的多筆 A records。
影響範圍：流量集中於單一實例，可靠性與效能下降。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Windows 容器的 Resolver Cache 未更新多筆 A records。
2. NGINX 未重新載入，仍持用舊 upstream 解析結果。
3. 擴編時未觸發客戶端的 DNS 刷新。

深層原因：
- 架構層面：客戶端 DNS 快取與服務拓撲變更未耦合。
- 技術層面：需要對 NGINX 下 reload 指令。
- 流程層面：缺少擴編後客戶端刷新步驟。

### Solution Design（解決方案設計）
解決策略：製作 reload.cmd 在 NGINX 容器內執行 flushdns 後再 nginx -s reload；擴編後執行該腳本，強制更新解析與配置。

實施步驟：
1. 編寫 reload.cmd
- 實作細節：ipconfig /flushdns → nginx -s reload
- 所需資源：批次檔、NGINX
- 預估時間：15 分鐘
2. 擴編後執行 reload
- 實作細節：docker exec 進 proxy 執行 reload.cmd
- 所需資源：Docker CLI
- 預估時間：5 分鐘

關鍵程式碼/設定：
```bat
:: reload.cmd
cd /d c:\nginx
ipconfig /flushdns
nginx -s reload

:: 擴編後操作
docker-compose scale webapp=5
docker exec containers_proxy_1 reload.cmd
```

實際案例：多次 flush + reload 後，ipconfig /displaydns 顯示 webapp 已有 5 筆 A records。
實作環境：同上
實測數據：
改善前：只命中 1 台
改善後：DNS 快取含多筆 A records，可分散至 5 台
改善幅度：可用節點數 +400%

Learning Points（學習要點）
核心知識點：
- DNS 多 A records 與客戶端快取
- NGINX reload 機制
- 擴編後客戶端刷新步驟

技能要求：
- 必備技能：Docker exec、NGINX 操作
- 進階技能：部署後回滾/重載流程

延伸思考：
- 自動觸發 reload 的方法？
- 加入健康檢查以避免將流量導向不健康實例？

Practice Exercise（練習題）
基礎練習：擴編至 3 台並手動 reload（30 分鐘）
進階練習：寫自動化腳本偵測擴編並 reload（2 小時）
專案練習：建置簡易 LB + scale + reload 完整流程（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：擴編後可均衡到多台
程式碼品質（30%）：腳本穩定、日誌清楚
效能優化（20%）：reload 次數最小化
創新性（10%）：自動偵測拓撲變更


## Case #8: 多次 flush/reload 才成功：因應多層快取的粗暴但有效流程

### Problem Statement（問題陳述）
業務場景：執行 reload.cmd 後仍報「host not found in upstream」，必須連續執行多次才成功。
技術挑戰：存在多層快取或延遲，單次 flush/reload 無法立即生效。
影響範圍：操作體驗差、需人工多次重跑。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Windows 端或 NGINX 端存在多層快取/延遲。
2. DNS 記錄更新與應用重載不同步。
3. 操作腳本缺少重試機制。

深層原因：
- 架構層面：多層快取不可見。
- 技術層面：DNS/應用都需同步刷新。
- 流程層面：缺重試與告警。

### Solution Design（解決方案設計）
解決策略：將「多次 flush + reload」納入標準操作或腳本化（雖然粗暴），確保最終成功；後續再視情況優化。

實施步驟：
1. 人為重複執行 reload.cmd
- 實作細節：一鍵重複，直到成功
- 所需資源：Docker exec
- 預估時間：5 分鐘
2. 納入 runbook
- 實作細節：標記需多次重試
- 所需資源：文件
- 預估時間：10 分鐘

關鍵程式碼/設定：
```powershell
# 連續執行直到不再出現 "host not found"（示意流程）
for /L %i in (1,1,10) do docker exec containers_proxy_1 reload.cmd
```

實際案例：文中作者手動重跑約 10 次才成功。
實作環境：同上
實測數據：
改善前：單次操作失敗
改善後：多次重跑後成功
改善幅度：成功率由 0% → 100%（多次嘗試後）

Learning Points（學習要點）
核心知識點：
- 多層快取影響實務操作
- 粗暴但務實的應急手段
- 後續優化方向（健康檢查、backoff）

技能要求：
- 必備技能：命令列自動化
- 進階技能：重試與 backoff 策略

延伸思考：
- 如何觀察到每一層快取狀態？
- 是否以 NGINX stream/動態解析替代？

Practice Exercise（練習題）
基礎練習：寫一個重試 10 次的小腳本（30 分鐘）
進階練習：加入錯誤偵測與 backoff（2 小時）
專案練習：把此流程整合入 CI/CD（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能自動重試至成功
程式碼品質（30%）：錯誤處理與日誌
效能優化（20%）：避免無效重試
創新性（10%）：告警與觀測


## Case #9: NGINX Windows 版 resolver 指令不生效—退而求其次用 reload 手法

### Problem Statement（問題陳述）
業務場景：希望用 NGINX resolver 指令跳過系統 DNS 快取並控制 TTL，使 NGINX 能自行管理解析更新。
技術挑戰：在 Windows 版 NGINX 上，resolver 設定始終無法生效，參考範例多為 Linux。
影響範圍：無法以 NGINX 自身機制解決快取問題，只能用外部方法。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Windows 版 NGINX 與文件/範例（偏 Linux）存在落差。
2. 實測中 resolver 未奏效。
3. 本地 DNS 問題複雜，非 NGINX 單點可控。

深層原因：
- 架構層面：軟體跨平台行為差異。
- 技術層面：Windows DNS/NGINX 互動不明確。
- 流程層面：投入時間成本高，難短期搞定。

### Solution Design（解決方案設計）
解決策略：暫不鑽研 resolver 設定，採取外部 reload 策略（Case #7/#8），以確保線上穩定；正式上線再由 NGINX 專家優化。

實施步驟：
1. 暫用 reload.cmd
- 實作細節：flushdns + nginx -s reload
- 所需資源：同前
- 預估時間：15 分鐘
2. 文件化 TODO
- 實作細節：待 Windows 版 NGINX/團隊專家處理
- 所需資源：內部議題追蹤
- 預估時間：10 分鐘

關鍵程式碼/設定：
```nginx
# 期望使用但未成功的方向（文件示例）
# resolver 127.0.0.1 valid=30s;

# 暫用外部 reload 策略（見 reload.cmd）
```

實際案例：作者嘗試 resolver 未果，改用 reload 流程。
實作環境：同上
實測數據：
改善前：NGINX 啟動/更新易失敗
改善後：可透過 reload 流程恢復
改善幅度：穩定性顯著提升（可控）

Learning Points（學習要點）
核心知識點：
- 跨平台行為差異
- 以替代策略保證穩定
- 技術債管理（TODO）

技能要求：
- 必備技能：NGINX 操作
- 進階技能：技術風險評估

延伸思考：
- Windows 版 NGINX 的可行 resolver 方案？
- 是否改採 Linux 容器跑 NGINX？

Practice Exercise（練習題）
基礎練習：以 reload 方案維持穩定（30 分鐘）
進階練習：調研 Windows NGINX resolver 可行性（2 小時）
專案練習：比較 Windows vs Linux NGINX 行為（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能可靠更新 upstream
程式碼品質（30%）：設定清晰
效能優化（20%）：reload 影響最小化
創新性（10%）：替代架構提案


## Case #10: 用「console 容器」做網路探針：快速進入網段內除錯

### Problem Statement（問題陳述）
業務場景：docker-compose 啟動多服務後，從主機外部不易掌握容器網段內部狀況，影響除錯效率。
技術挑戰：需要能在同網段內直接執行 nslookup、ping、ipconfig 等工具。
影響範圍：診斷速度與正確性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 主機外部視角有限。
2. 缺乏持續在線的探針容器以便隨時 exec 進入。
3. 無法直接看到容器內 DNS 快取等細節。

深層原因：
- 架構層面：容器網路隔離。
- 技術層面：需要長駐容器提供交互埠。
- 流程層面：排錯資產（工具容器）缺位。

### Solution Design（解決方案設計）
解決策略：在 compose 中加入一個 console 容器，以 ping -t localhost 保持長駐，隨時 docker exec 進入做網路檢查。

實施步驟：
1. 在 compose 增加 console 服務
- 實作細節：用 windowsservercore，command：ping -t localhost
- 所需資源：docker-compose.yml
- 預估時間：10 分鐘
2. 使用 docker exec 進入 console
- 實作細節：執行 nslookup/ping/ipconfig
- 所需資源：Docker CLI
- 預估時間：5 分鐘

關鍵程式碼/設定：
```yaml
services:
  console:
    image: microsoft/windowsservercore
    command: ping -t localhost
    depends_on:
      - webapp
      - proxy

# 進入 console 容器
docker exec -it containers_console_1 cmd.exe
```

實際案例：作者透過 console 容器觀察到 nslookup 有 IP、但 ping 失敗，進一步用 displaydns 找到負快取。
實作環境：同上
實測數據：
改善前：外部視角難以定位
改善後：容器網段內視角，定位速度顯著提升
改善幅度：診斷時間大幅下降（定性）

Learning Points（學習要點）
核心知識點：
- 工具容器（toolbox）的價值
- docker exec 的除錯技巧
- 內視角觀測 DNS/網路

技能要求：
- 必備技能：Compose、exec
- 進階技能：除錯流程設計

延伸思考：
- 是否以 BusyBox/專用工具箱容器？
- 自動收集網路診斷報告？

Practice Exercise（練習題）
基礎練習：新增 console 服務並進入操作（30 分鐘）
進階練習：撰寫一鍵收集網路診斷資訊腳本（2 小時）
專案練習：打造內部「網路探針」容器（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能內部檢查 DNS/網路
程式碼品質（30%）：腳本與配置清晰
效能優化（20%）：診斷快速低干擾
創新性（10%）：自動化與可視化


## Case #11: Dockerfile CMD 啟動失敗容器即退出—改由 compose 的 command 控制並便於除錯

### Problem Statement（問題陳述）
業務場景：將 NGINX 以 Dockerfile 的 CMD 啟動，若啟動失敗，容器立即退出，除錯困難。
技術挑戰：需要在啟動失敗時讓容器保持存活，以便進入確認日誌與環境。
影響範圍：除錯效率低。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 容器主行程（CMD）退出即容器退出。
2. NGINX 啟動失敗導致容器自動停掉。
3. 無法即時進入容器查看。

深層原因：
- 架構層面：容器以主行程存活模型。
- 技術層面：CMD 與 compose command 行為差異。
- 流程層面：未區分「生產啟動」與「除錯啟動」。

### Solution Design（解決方案設計）
解決策略：將 Dockerfile 中 CMD 拿掉，改由 docker-compose.yml 的 command 指定啟動腳本（如 start-nginx.cmd），並可在失敗時維持容器存活以便除錯。

實施步驟：
1. 調整 Dockerfile
- 實作細節：移除 CMD
- 所需資源：Dockerfile
- 預估時間：5 分鐘
2. 在 compose 以 command 啟動
- 實作細節：command: start-nginx.cmd
- 所需資源：docker-compose.yml
- 預估時間：10 分鐘

關鍵程式碼/設定：
```dockerfile
# Dockerfile
FROM microsoft/windowsservercore
COPY nginx           /nginx
COPY start-nginx.cmd /
# 不在此處寫 CMD，改交由 compose 控制
```

實際案例：作者為便於排錯，將 CMD 拿掉，透過 compose 的 command 呼叫批次檔，成功提升除錯便利性。
實作環境：同上
實測數據：
改善前：啟動失敗容器即退出，不易除錯
改善後：可主動控制啟動流程並保留除錯窗口
改善幅度：除錯效率顯著提升（定性）

Learning Points（學習要點）
核心知識點：
- 容器主行程模型
- Dockerfile CMD vs compose command
- Debug-friendly 啟動策略

技能要求：
- 必備技能：Dockerfile/Compose
- 進階技能：啟動腳本與除錯流程

延伸思考：
- 是否使用 entrypoint 腳本更合適？
- 在 CI 中如何切換「除錯模式」與「生產模式」？

Practice Exercise（練習題）
基礎練習：將 CMD 邏輯移至 compose（30 分鐘）
進階練習：提供除錯模式（保活）與生產模式（嚴格退出）（2 小時）
專案練習：打造可切換模式的啟動框架（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能在失敗時便於除錯
程式碼品質（30%）：清晰的模式切換
效能優化（20%）：啟動邏輯簡潔
創新性（10%）：自動收集日誌與狀態


## Case #12: Windows 10 Creators Update 後容器無法上網：新建 NAT 網路恢復連線

### Problem Statement（問題陳述）
業務場景：升級 Windows 10 Creators Update（1704）後，容器對外連線（如 ping 8.8.8.8）失敗。
技術挑戰：預設 nat 網路看似正常（inspect 無異常），但容器實際無法通。
影響範圍：所有對外依賴的容器功能失效（下載、API 呼叫）。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 系統更新後預設 nat 網路「看起來正常但實際不可用」。
2. 可能因之前手動刪改 nat、安裝 Docker for Windows、Hyper-V 切換等操作影響。
3. 具體根因未確認，但問題集中於預設 nat。

深層原因：
- 架構層面：Windows 更新與 HNS 狀態互動複雜。
- 技術層面：nat 網路內部參數或狀態異常。
- 流程層面：重大更新後缺少網路回歸測試與復原手段。

### Solution Design（解決方案設計）
解決策略：避開壞掉的預設 nat，新建一個 nat 網路（andrew-nat），並在跑容器時指定使用該網路，成功恢復外聯。

實施步驟：
1. 新建 NAT 網路
- 實作細節：docker network create -d nat andrew-nat
- 所需資源：Docker CLI
- 預估時間：5 分鐘
2. 指定網路啟動容器
- 實作細節：docker run --network andrew-nat ...
- 所需資源：Docker CLI
- 預估時間：5 分鐘
3. 驗證外聯
- 實作細節：容器內 ping 8.8.8.8
- 所需資源：cmd.exe
- 預估時間：5 分鐘

關鍵程式碼/設定：
```powershell
docker network create -d nat andrew-nat
docker network inspect andrew-nat

# 使用新網路啟動容器
docker run --rm -it --network andrew-nat microsoft/windowsservercore cmd.exe

# 容器內驗證
ping 8.8.8.8
ipconfig /all
```

實際案例：作者新建 andrew-nat 後，容器立刻可通外網，ping 8.8.8.8 成功。
實作環境：Windows 10 Creators Update（1704）
實測數據：
改善前：Reply from <container_ip>: Destination host unreachable/timeout
改善後：Reply from 8.8.8.8（8~9ms，0% loss）
改善幅度：連通性 0% → 100%

Learning Points（學習要點）
核心知識點：
- 多 NAT 支援（1704 起）
- 以替代網路規避壞狀態
- 回歸測試的重要性

技能要求：
- 必備技能：Docker network 基本操作
- 進階技能：網路問題繞路策略

延伸思考：
- 是否應保留「恢復良好」的網路作為預設？
- 需不需要清理壞 nat？風險評估？

Practice Exercise（練習題）
基礎練習：新建 NAT 並驗證外聯（30 分鐘）
進階練習：將現有服務切到新 NAT（2 小時）
專案練習：寫一鍵「網路自測與切換」工具（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：可恢復容器外聯
程式碼品質（30%）：腳本與文檔清晰
效能優化（20%）：切換對服務影響最小
創新性（10%）：自動判障與回退策略


## Case #13: 新建 NAT 後的健檢：docker network inspect 與容器內 ipconfig

### Problem Statement（問題陳述）
業務場景：新建 andrew-nat 後，需要確認網段、Gateway、DNS 等配置是否合理，確保後續服務穩定。
技術挑戰：如何用最小步驟驗證新網路配置與容器端網卡參數一致性。
影響範圍：避免後續連線隱患。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未檢查新 NAT 的子網與網關，可能與現網衝突。
2. 容器端網卡參數需與網路配置一致。
3. 忽略健檢易導致後續隱性錯誤。

深層原因：
- 架構層面：虛擬網路與實體/其他虛擬網段互動。
- 技術層面：IPAM 與 HNS 自動配置需核對。
- 流程層面：缺乏驗證清單。

### Solution Design（解決方案設計）
解決策略：以 docker network inspect 檢查 NAT 配置、在容器內以 ipconfig /all 檢視網卡參數，兩相對照確認。

實施步驟：
1. 檢查網路（host）
- 實作細節：docker network inspect andrew-nat
- 所需資源：Docker CLI
- 預估時間：5 分鐘
2. 檢查容器網卡（container）
- 實作細節：ipconfig /all
- 所需資源：cmd.exe
- 預估時間：5 分鐘

關鍵程式碼/設定：
```powershell
docker network inspect andrew-nat
docker run --rm -it --network andrew-nat microsoft/windowsservercore cmd.exe
# 容器內
ipconfig /all
```

實際案例：作者在 andrew-nat 下容器可通外網，ipconfig 顯示正確的 Gateway/DNS。
實作環境：同 Case #12
實測數據：
改善前：未知配置
改善後：配置明確、連線成功
改善幅度：風險降低（定性）

Learning Points（學習要點）
核心知識點：
- network inspect 與容器端 ipconfig 的對照
- 子網/Gateway/DNS 檢查重點
- 建立網路健檢清單

技能要求：
- 必備技能：Docker CLI、Windows 網路指令
- 進階技能：網段規劃

延伸思考：
- 如何將健檢自動化並存檔？
- 變更監控（Config drift）？

Practice Exercise（練習題）
基礎練習：對新 NAT 做 inspect 與容器內 ipconfig（30 分鐘）
進階練習：撰寫健檢腳本並產出報告（2 小時）
專案練習：將健檢納入部署流水線（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能完整輸出關鍵參數
程式碼品質（30%）：報告清晰
效能優化（20%）：健檢快速
創新性（10%）：異常告警


## Case #14: NGINX 作為前端，用服務名導流至 webapp（nginx.conf 與 compose 配置）

### Problem Statement（問題陳述）
業務場景：以 NGINX 前端負載均衡至後端 webapp，需用服務名（webapp）作為 upstream，配合 Compose 服務發現。
技術挑戰：nginx.conf 要用服務名，不用硬編 IP；Compose 要正確定義服務與網路。
影響範圍：降低耦合、利於擴編與滾動更新。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 服務應透過名稱而非 IP 連接，利於拓撲變更。
2. Compose 與預設 network 提供 DNS 解析服務名→多 IP。
3. 若使用 IP 導致更新困難。

深層原因：
- 架構層面：服務名驅動的服務發現。
- 技術層面：nginx upstream 用服務名。
- 流程層面：以 Compose 控制部署與擴編。

### Solution Design（解決方案設計）
解決策略：在 nginx.conf 將 upstream 指向 webapp；Compose 定義 webapp/proxy/console 與外部 nat 網路，proxy 對外映射 80。

實施步驟：
1. 撰寫 nginx.conf
- 實作細節：upstream 指向 server webapp
- 所需資源：NGINX for Windows
- 預估時間：15 分鐘
2. 編寫 compose
- 實作細節：webapp 暴露 80（內部）、proxy 對外 80:80，networks 指向 nat
- 所需資源：docker-compose.yml
- 預估時間：30 分鐘

關鍵程式碼/設定：
```nginx
# nginx.conf（片段）
events { worker_connections 4096; }
http {
  upstream production { server webapp; }
  server {
    listen 80;
    location / { proxy_pass http://production/; }
  }
}
```

```yaml
# docker-compose.yml（片段）
version: '2.1'
services:
  webapp:
    image: andrew0928/mvcdemo:1.0
    ports: ["80"]   # 僅內部
  proxy:
    build: ./mvcproxy
    command: start-nginx.cmd
    depends_on: [webapp]
    ports: ["80:80"]
  console:
    image: microsoft/windowsservercore
    command: ping -t localhost
    depends_on: [webapp, proxy]
networks:
  default:
    external:
      name: nat
```

實際案例：作者以服務名 webapp 作為 upstream，並以外部 nat 作為預設網路。
實作環境：同上
實測數據：
改善前：耦合 IP 難以擴編
改善後：以服務名連線，配合 scale 與 reload 可導流至多實例
改善幅度：可維護性/擴展性顯著提升（定性）

Learning Points（學習要點）
核心知識點：
- 服務名導向（DNS 服務發現）
- 內外埠差異（內部 80 vs 對外 80:80）
- 外部網路（external nat）配置

技能要求：
- 必備技能：NGINX/Compose 設定
- 進階技能：動態拓撲支援

延伸思考：
- 日後改用動態服務發現（Consul/DNS SRV）？
- 自動 reload 與健康檢查？

Practice Exercise（練習題）
基礎練習：完成 proxy→webapp 導流（30 分鐘）
進階練習：擴編並用 reload 實測（2 小時）
專案練習：完成一個具彈性擴展的前後端（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：導流正常
程式碼品質（30%）：配置清楚
效能優化（20%）：基本 LB 生效
創新性（10%）：自動 reload 維運化


## Case #15: 以遠端測試先行的三段式驗證：隔離 NAT loopback 與實際連通問題

### Problem Statement（問題陳述）
業務場景：映射埠後從主機本機測不到服務，需分辨是 NAT loopback 限制還是服務本身不可用。
技術挑戰：若只用 localhost 測試，易誤判。
影響範圍：排錯時間拉長。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. NAT loopback 不支援導致 localhost 測試必然失敗。
2. 未先做遠端驗證。
3. 缺少標準化排錯順序。

深層原因：
- 架構層面：本機/遠端路徑行為不同。
- 技術層面：WinNAT 限制。
- 流程層面：排錯步驟未流程化。

### Solution Design（解決方案設計）
解決策略：建立三段式驗證流程：先遠端（HOST_IP:映射埠）→再本機（容器 IP:內部埠）→最後（如需）再研究本機代理方案。以此快速定位問題層次。

實施步驟：
1. 遠端驗證（首要）
- 實作細節：http://<HOST_IP>:<mapped_port>
- 所需資源：同網段任一主機
- 預估時間：5 分鐘
2. 本機驗證（容器 IP）
- 實作細節：inspect 取 IP；http://<CONTAINER_IP>:<container_port>
- 所需資源：Docker CLI
- 預估時間：5 分鐘
3. 深挖（必要時）
- 實作細節：檢查防火牆/代理/其他
- 所需資源：系統工具
- 預估時間：30 分鐘

關鍵程式碼/設定：
```powershell
# Step 1: 遠端機
Start-Process "http://<HOST_IP>:8000"

# Step 2: 本機
docker inspect -f "{{.NetworkSettings.Networks.nat.IPAddress}}" demo-iis
# 假設 192.168.14.216
Start-Process "http://192.168.14.216:80"
```

實際案例：文中先遠端成功，再本機以容器 IP 成功，定位為 NAT loopback 限制。
實作環境：同上
實測數據：
改善前：只做 localhost 測試，結論不清
改善後：依序驗證，5~10 分鐘內定位
改善幅度：定位效率大幅提升（定性）

Learning Points（學習要點）
核心知識點：
- 分層驗證思維
- 本機/遠端行為差異
- 標準化排錯順序

技能要求：
- 必備技能：基本網路驗證
- 進階技能：排錯流程設計

延伸思考：
- 是否將流程寫成 SOP + 工具？
- 如何在 CI/CD 加入自動化驗證？

Practice Exercise（練習題）
基礎練習：按三步完成驗證（30 分鐘）
進階練習：寫腳本自動化（2 小時）
專案練習：把該流程做成內部工具（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：能快速定位問題
程式碼品質（30%）：工具清晰易用
效能優化（20%）：驗證時間短
創新性（10%）：流程自動化


## Case #16: 在 Compose 使用 external nat：與主機現有 NAT 對齊，避免網路碎片化

### Problem Statement（問題陳述）
業務場景：docker-compose 預設會建立專案專屬 network。希望所有服務使用主機既有 nat，以便與其他容器一致、簡化網路管理。
技術挑戰：將 default network 指定為 external nat。
影響範圍：避免多個類似網段並存造成管理複雜。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 預設會建立 project_default network。
2. Windows nat 已存在且可用。
3. 多個網路導致管理與診斷分散。

深層原因：
- 架構層面：統一網路利於觀測與維護。
- 技術層面：Compose 可指向 external network。
- 流程層面：網路標準化策略。

### Solution Design（解決方案設計）
解決策略：在 docker-compose.yml 中將 default 指向 external nat。

實施步驟：
1. 編輯 compose
- 實作細節：networks.default.external.name = nat
- 所需資源：docker-compose.yml
- 預估時間：5 分鐘
2. 重建服務
- 實作細節：up -d
- 所需資源：Docker CLI
- 預估時間：5 分鐘

關鍵程式碼/設定：
```yaml
networks:
  default:
    external:
      name: nat
```

實際案例：文中 compose 已採用 external nat 作為 default。
實作環境：同上
實測數據：
改善前：多個預設網路（潛在）
改善後：統一使用 nat
改善幅度：網路管理複雜度下降（定性）

Learning Points（學習要點）
核心知識點：
- Compose external network
- 網路治理/一致性
- 與現有基礎設施整合

技能要求：
- 必備技能：Compose 設定
- 進階技能：網路治理

延伸思考：
- 是否建立命名規範？（專案→網段）
- overlay 可用後如何演進？

Practice Exercise（練習題）
基礎練習：將 default 指向 external nat（30 分鐘）
進階練習：多專案共用同一 nat（2 小時）
專案練習：設計專案級網路治理策略（8 小時）

Assessment Criteria（評估標準）
功能完整性（40%）：服務皆掛載到 nat
程式碼品質（30%）：配置簡潔一致
效能優化（20%）：減少網路切換與問題
創新性（10%）：網路治理方案



案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 1, 2, 6, 10, 11, 15, 16
- 中級（需要一定基礎）
  - Case 3, 4, 5, 7, 8, 12, 13, 14
- 高級（需要深厚經驗）
  - 無（本文聚焦於實戰排錯與工程化技巧）

2) 按技術領域分類
- 架構設計類
  - Case 14, 16
- 效能優化類
  - Case 5, 7, 8（啟動與運行穩定性/有效性）
- 整合開發類
  - Case 5, 6, 11, 14, 16
- 除錯診斷類
  - Case 1, 2, 3, 4, 7, 8, 10, 12, 13, 15
- 安全防護類
  - 無（本文未聚焦安全配置）

3) 按學習目標分類
- 概念理解型
  - Case 1, 3, 6, 14, 16（NAT loopback、link 不支援、服務名導向）
- 技能練習型
  - Case 2, 4, 10, 11, 13（inspect、displaydns、exec、ipconfig）
- 問題解決型
  - Case 5, 7, 8, 12, 15（啟動 gating、擴編後刷新、網路壞了新建 NAT、三段式驗證）
- 創新應用型
  - Case 5, 7, 16（腳本化 gating、reload、自訂網路治理）



案例關聯圖（學習路徑建議）

- 起步階段（基礎概念與快速成功）
  1) 先學 Case 1（NAT loopback 限制與正確測試方式）
  2) 接著 Case 2（快速取得容器 IP）
  3) 然後 Case 15（三段式驗證流程）

- 網路診斷能力建立
  4) Case 10（console 探針容器）
  5) Case 4（nslookup 與 ping 差異、負快取排錯）
  6) Case 3（避免 --link，服務名思維）

- 啟動與就緒工程化
  7) Case 6（depends_on 侷限）
  8) Case 5（start-nginx.cmd 等待就緒實作）
  9) Case 11（用 compose command 提升除錯性）

- 擴編與動態拓撲
  10) Case 14（nginx 以服務名導流）
  11) Case 7（擴編後 flush + reload 更新 upstream）
  12) Case 8（多層快取下的重試策略）
  13) Case 9（resolver 不生效的替代策略）

- 系統性網路韌性
  14) Case 12（更新後網路壞掉時的新建 NAT）
  15) Case 13（新 NAT 健檢）
  16) Case 16（Compose external nat 一致性治理）

依賴關係說明：
- Case 5 依賴 Case 6 的思維（就緒 vs 順序）；Case 7/8 依賴 Case 5（有啟動與重載能力）。
- Case 12/13 為同一串：先建網（12）再健檢（13）。
- Case 14（服務名導向）是 Case 7/8 能有效的前提。
- 基礎診斷（Case 1/2/4/10/15）是所有後續案例的能力底座。

完整學習路徑建議：
- 先完成基礎（Case 1 → 2 → 15 → 10 → 4 → 3）
- 再做啟動工程化（Case 6 → 5 → 11）
- 進入擴編與動態拓撲（Case 14 → 7 → 8 → 9）
- 最後掌握系統級網路恢復與治理（Case 12 → 13 → 16）

此路徑能從「懂測試」→「會診斷」→「能工程化啟動與擴編」→「具備網路恢復與治理能力」，完整覆蓋文中所有踩雷與掃雷精華。