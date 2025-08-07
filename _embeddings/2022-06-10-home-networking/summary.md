```markdown
# 水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路

## 摘要提示
- UniFi整合: 作者以 UDM-PRO 為核心，將 Router、Switch、AP、DVR 及 PoE 電源全數換成 UniFi 系統，機櫃縮減至 5U。
- VLAN規畫: 建立 TRUNK、NAS、HOME、GUEST/IOT 等 5 個 VLAN，以路由、防火牆及排程確保流量隔離與品質。
- Traffic Rules/Routes: UDM-PRO 1.12 版引入 Traffic Management，可做家長控制及多 PPPoE 進階路由。
- 居家監控: 捨棄傳統 DVR，改用 UniFi Protect + G3 Flex/Instant，搭配 NAS 做 RTSP 備份。
- NAS應用: Synology DS1821+ 加 32 GB RAM、10G NIC，透過 Docker 提供 AdGuardHome、Bitwarden、code-server 等服務。
- 10G升級: 主幹採 10G DAC + 2.5G Client，並以 USW-Enterprise-24-PoE 執行 L3 Routing 避開 UDM-PRO 處理瓶頸。
- 線材統一: 全屋 Cat5e + PoE，舊同軸與電話插座改 RJ45，搭配 UniFi 可彎跳線提升佈線彈性。
- VPN新體驗: Teleport (WireGuard) 與 L2TP 併用，WiFiman App 一鍵配對，外出可安全回家。
- 家用需求演進: 15 年內從同軸、電話總機轉向 All-IP 與雲端，網路成為唯一基礎設施。
- 軟硬體心得: 高度可視化 Controller 與 Docker 生態讓「半調子網管」也能輕鬆玩 VLAN、10G 與自架服務。

## 全文重點
作者回顧 15 年來的家庭網路演進，從早期同軸第四台、電話總機與 PC-Server，到今日完全 IP 化、PoE 化的環境。2019 年因設備故障試用 UniFi AP 後深陷「全家餐」漩渦，最終以 UDM-PRO 為核心，把 Router、Switch、Wi-Fi、DVR 與 UPS 重新整併，機櫃體積大減，管理全交由 UniFi OS Console。  
網路設計分五大目標：1) 設備整併、2) 基礎建設、3) 居家監控、4) 網路服務、5) 邁向 10G。硬體方面新增 UDM-PRO、USW-Enterprise-24-PoE、AC-Lite/LR AP 與 PoE Camera，並淘汰 Asus、小米路由、舊 DVR 與電話系統；線材以 Cat5e 配 RJ45，全屋可彎短跳線與 DAC 銅纜完成 10G/2.5G 佈線。  
在基礎建設上，UDM-PRO 整合 VLAN、VPN、威脅偵測與流量分析。作者設計五個 VLAN，並透過新版 Traffic Rules 實作家長控制、訪客隔離及多 PPPoE 雙線路（浮動 IP 與固定 IP）出口。Teleport VPN 採 WireGuard 架構，一鍵邀請即可連回家。  
監控部分以 UniFi Protect 取代 DVR，G3 Flex/Instant 透過 PoE 或 USB-C 供電，錄影存於 UDM-PRO 硬碟，RTSP 再備份到 NAS。  
服務層則由 Synology DS1821+ 承擔，安裝 10G NIC 並跑 Docker：AdGuardHome 負責 DNS 過濾與內網 Rewrite；Bitwarden 做密碼管理；Iperf3、FileZilla、code-server 與 GitHub Pages 打造隨時可用的開發與檔案環境。  
在 10G 部署過程發現兩大瓶頸：UDM-PRO 內部架構僅 1 Gbps 連接 8 埠 Switch，且啟用 Threat Management 時 CPU 成為效能瓶頸。作者改以 USW-Enterprise 的 L3 Routing 讓跨 VLAN 流量不經 UDM-PRO，成功在 NAS-PC 間跑滿 2.35 Gbps；若威脅偵測關閉，10G 亦能全速。  
最終，作者達成「設備簡化、管理集中、安全分流、10G 可擴充」的目標，並體會到軟體整合的重要性—有了 UniFi 控制器與 NAS Docker，即使非專業網管也能輕鬆擁有企業級功能。

## 段落重點
### 前言：理想的網路環境
作者反省 2007 年的佈線失誤（同軸、Cat5e、RJ12 電話）並提出五大新目標：設備精簡、網段隔離、全 IP 監控、可靠服務與 10G 升級；強調現代家庭只需穩定頻寬與統一規格，其他功能皆可軟體化。

### 目標 1：網路設備整併
詳細列出現役設備（UDM-PRO、USW-Enterprise-24-PoE、UAP AC-Lite/LR 等）與淘汰列表，說明如何以 PoE、DAC 與可彎跳線取代舊路由、DVR、電話總機，並展示 2007→2019→2022 機櫃演進照片，體現「5U 完成所有需求」的成果。

### 目標 2：網路基礎建設
1) VLAN：TRUNK、MODEM、NAS、HOME、GUEST/IOT 五網段及其用途；2) DNS：在 NAS 上部署 AdGuardHome 做廣告阻擋與內網解析；3) VPN：L2TP 與 Teleport WireGuard，一鍵邀請行動裝置；4) Traffic Rules：新版家長控制與 APP 分類封鎖；5) Traffic Routes：雙 PPPoE 實現浮動/固定 IP 分流、特定裝置或網站走指定線路。

### 目標 3：居家監控
以 UniFi Protect + G3 Flex/Instant 改寫監控體驗，PoE 或 USB-C 供電減少佈線難度；Web 與手機 UI 友善，搭配 NAS 透過 RTSP 同步備份，淘汰傳統 DVR 及同軸攝影機。

### 目標 4：網路服務
新購 Synology DS1821+（32 GB RAM、10G NIC）成為 Docker 平台：AdGuardHome、Portainer、Bitwarden、Iperf3、FileZilla、Home Assistant、code-server 等服務一站整合；利用 DNS Rewrite、Let’s Encrypt 與 Reverse Proxy 提供 HTTPS 入口，並透過 VSCode Web 實現雲端寫作與 CI／CD 發布部落格。

### 目標 5：邁向 10G 的路
主幹採 SPF+ 10G + Cat5e 2.5G；揭露 UDM-PRO 內部 1G Bottleneck 與 Threat Management CPU 負荷，透過 USW-Enterprise 啟用 L3 Routing 分擔跨 VLAN 流量，Iperf3 測試 NAS-PC 穩定達 2.3 Gbps，關閉威脅偵測可見 9 Gbps；提醒選線材、介面與韌體版本的重要性。

### 小結
硬體由「多盒子」轉「單平台」，軟體靠 UniFi Controller 與 Docker 整合；歷經三年升級終於達成穩定、安全、可視化且具擴充彈性的家庭網路。作者鼓勵讀者依自身需求參考此方案，體驗軟硬結合的現代家庭基礎建設。
```
