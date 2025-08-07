# 掃雷回憶錄 - Windows Container Network & Docker Compose

## 摘要提示
- WinNAT Loopback: Windows 容器埠對映無法在 Host 端以 localhost 存取，原因是 WinNAT 不支援 NAT loopback。
- --link 半殘: Docker CLI 的 `--link` 在 Windows 上僅部分可用，DNS 解析失效造成「看似可連其實不通」的錯覺。
- DNS Cache 陷阱: docker-compose 啟動多服務時常因 Windows 內部 DNS 快取殘留而導致 service discovery 斷線。
- Nginx Workaround: 透過批次檔反覆 `flushdns` 與重新載入 Nginx，暫時解決 DNS 更新延遲問題。
- Scale 失效: 使用 `docker-compose scale` 增減實例後需手動清除 DNS 快取，否則流量只會打到舊 IP。
- 尚缺 Overlay: 目前 Windows 容器仍未支援 Overlay network，Swarm 模式只能等待微軟後續實作。
- Creator Update 雷: 升級 Win10 1704 後預設 nat network 壞掉，需自行建立新的 NAT network 才能上網。
- 多 NAT 支援: 1704 之後 Windows 開放多個 NAT network，也同步加入 Overlay 與 Swarm 基礎能力。
- 官方限制: `--dns-search、--add-host` 等多項網路參數在 Windows 仍不支援，建置前須留意。
- 實戰心法: 先熟悉官方文件與常見地雷，必要時以腳本、重建網路等方式旁路，待正式支援再全面導入。

## 全文重點
作者在 Windows Server 2016 與 Windows 10 (Creator Update) 環境中實測 Windows Container 與 docker-compose，紀錄數個重大的網路暗坑。首先，由於 WinNAT 不支援 NAT loopback，容器埠對映只能從外部主機連入，Host 端必須改用容器內部 IP 測試。其次，官方宣稱不支援 `--link`，但實測僅防火牆連通，DNS 卻無相對應解析，造成「可 nslookup、不可 ping」的半殘現象。第三，使用 docker-compose 管理多服務時，Windows 會把「查不到結果」的負面 DNS 紀錄寫入本機快取，導致 Nginx 或其他服務在啟動、scale 或重部署時找不到新容器；作者以無限迴圈批次檔持續 `ipconfig /flushdns` 並重啟 Nginx，才確保所有實例都能被解析。第四，升級 Win10 1704 後，預設 nat network 無法連線，建立自訂 NAT 網路即可恢復功能；此版本開始支援多 NAT 與 Overlay，但仍有許多 CLI 參數缺席。整體而言，Windows Container 網路層仍在發展期，若非必要宜暫以 workaround 避開，並持續追蹤微軟更新。

## 段落重點
### Overview: Windows Container Networking
Windows Server 2016 推出後，Windows 容器成為焦點，但與成熟的 Linux 版 Docker 相比，網路功能尚嫌不足，尤其 Overlay network 仍待實作；作者在實體伺服器 (版本 14393、Docker 1.12.2、Compose 1.10.0-rc1) 上進行測試，為後續踩雷鋪陳。

### 1. container port mapping 無法在本機使用
由於 WinNAT 不支援 NAT loopback，將容器的 80 對映至 Host 8000 時，Host 端無法用 `localhost:8000` 存取，只能用外部電腦或查詢容器內部 IP 再連 80 埠；14300 之後系統會自動開防火牆規則，不需手動新增。

### 2. container link 官方宣稱不再支援
官方文件列入「不支援」，實測卻呈現半殘：加 `--link` 的容器彼此可透過 DNS 名稱互 ping，少了 `--link` 時 DNS 仍可解析但實際 ping 失敗；推論僅防火牆例外生效，DNS 端沒正確寫入，凸顯 `--link` 不宜再依賴。

### 3. docker-compose 的 service discovery 無效問題
在 Compose 定義 Nginx + 多個 ASP.NET WebApp 時，容器啟動順序導致首次解析失敗的負面紀錄被快取，後續即便 DNS 已正確回應，Windows 仍沿用錯誤快取；作者透過批次檔無限迴圈 `flushdns` 並重跑 Nginx，確保待 DNS 正確後自動啟動，並在 scale 變更時加跑 `reload.cmd` 重刷快取。

### 4. Win10 Creator Update 後網路全斷
升級 1704 或改裝 Docker for Windows 後，預設 nat network 失效，容器無法對外。作者改用 `docker network create -d nat 自訂名` 建立新 NAT 網路並在 `docker run --network` 指定，新網路即可正常連線；此版同時引入多 NAT 與 Overlay 支援，意味 Windows Swarm 終於可行。

### 後記
Windows Container 網路雖仍漏洞百出，但微軟持續更新，Azure ACS 亦已展示 Windows/Linux 混合 Swarm，可預期功能終將完善；作者建議現階段先熟悉問題與暫時解法，真正進入生產前再視微軟修補進度決定是否全面導入。