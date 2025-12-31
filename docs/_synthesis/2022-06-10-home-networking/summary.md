---
layout: synthesis
title: "水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路"
synthesis_type: summary
source_post: /2022/06/10/home-networking/
redirect_from:
  - /2022/06/10/home-networking/summary/
postid: 2022-06-10-home-networking
---

# 水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路

## 摘要提示
- UniFi 全家桶整合: 以 UDM-PRO+USW+UAP 取代零散設備，機櫃精簡至核心路由、交換器與 NAS。
- VLAN 架構: 以 TRUNK/NAS/HOME/GUEST/MODEM 分網，落實隔離、流量控管與訪客/IOT 安全。
- DNS 與廣告阻擋: 以 NAS 上的 AdGuard Home 提供 DNS 解析、黑白名單與內部域名覆寫。
- VPN 方案: 採 L2TP 與 Teleport（基於 WireGuard），行動端零設定體驗佳。
- 家長監護: 透過 Traffic Rules 以 App 類別、裝置與時段三維度精準封鎖或允許。
- 雙 PPPoE 與流量路由: 利用 Port Remapping 與 Traffic Routes，實作 WAN1/2 分流與特定服務專線。
- 居家監控: 以 UniFi Protect + G3-Flex/G3-Instant 取代傳統 DVR，同步建議 NAS 做 RTSP 備份。
- NAS + Docker 生態: 以 DS1821+ 跑容器（Bitwarden、Iperf3、FileZilla、code-server），配合反代與免費 SSL。
- 走向 10G/2.5G: 骨幹先 10G（SFP+ DAC），用 2.5G 滿足端點，線材統一 RJ45/CAT5e 維持性價比。
- 效能與瓶頸: UDM-PRO 架構與 Threat Management 限速，改由 L3 Switch 接手跨 VLAN 路由解決。

## 全文重點
作者自 2019 年網通設備故障後切入 UniFi 生態，兩年半完成家用網路全面升級與整併：以 UDM-PRO 為核心，搭配 Enterprise 24 PoE L3 交換器與多台 UniFi AP，將 AP/DVR/Router/Switch 全數整合，同時把原先分散的服務收斂到 Synology NAS 與 Docker 上。其理想藍圖包含五大目標：設備整併、網路基礎建設、居家監控、網路服務與邁向 10G。

在基礎建設上，作者規劃 5 個 VLAN（TRUNK、NAS、HOME、GUEST/IOT、MODEM），達成設備隔離、訪客/IOT 安全與實驗區域獨立；以 AdGuard Home 處理 DNS 解析、黑白名單與內部域名 rewrite，與 NAS 反代和 Let’s Encrypt 憑證配合，形成自有域名的統一入口。遠端連線採 L2TP 與 Teleport（WireGuard 核心），行動端透過 WiFiman 幾乎零配置即可回家。UDM-PRO 新版（1.12.22+）與 Network 7.1+ 帶來 Traffic Rules/Routes：前者以 App 類別、裝置與排程三維度落實家長監護（如封社群 App 夜間時段）；後者實現多 PPPoE 與分流，作者以 WAN1 浮動 IP 供一般上網、WAN2 固定 IP 專供 NAS 對外服務，並能針對來源/目的做特定路由，端點也可繞過路由器直接 PPPoE。

居家監控上，作者以 UniFi Protect 搭配 G3-Flex/G3-Instant 取代傳統 DVR/類比攝影機，體驗佳、整合度高；惟僅支援自家相機與備份彈性不足，建議以 NAS（Surveillance Station 或 RTSP）同步抄寫作為二次備援。服務層面則以 DS1821+（Ryzen Embedded V1500B）承載 Docker：Bitwarden 密碼庫、Iperf3 網測、FileZilla GUI（VNC Web 客戶端）、code-server（Web 版 VSCode）與 Jekyll/GitHub Pages 本地預覽；透過 AdGuard Home + NAS 反代 + 免費 SSL，實現以域名統一入口、安全可維運的自架服務。作者也闡述 NAS 較自組 PC 作為家用服務器的優勢：儲存出發的設計、低功耗長時運行與備份/RAID 完整度。

在 10G 部分，採「骨幹 10G、端點 2.5G」的務實策略：NAS 採 SFP+ DAC 直連交換器，端點以 2.5G NIC 應用。實測揭露兩大瓶頸：其一為 UDM-PRO 的內部架構，10G 與 1G×8 等同兩台機器拼裝，跨區流量易在內部 1G 處受限；其二為 Threat Management 啟用時消耗 CPU，跨 VLAN 傳輸速率掉到約 1.4Gbps。對策是將跨 VLAN 路由改由 USW-Enterprise L3 Switch 處理，避開 UDM-PRO 的 L7 檢測與內部匯流限制，使 PC↔NAS 速度恢復至 2.3~2.5Gbps 合理表現。整體而言，此升級路徑在成本、管理複雜度與實際性能間取得平衡：硬體用 UniFi 統一、服務交給 NAS，核心靠軟體整合與可視化控制，達到家用可維護、可擴充、體驗佳的網路環境。

## 段落重點
### 前言：理想的網路環境
作者回顧 15 年前的布線與設備，指出同軸電纜、市話總機與過度保守的 CAT5e 都難以應付現今需求；新願景是「一切往 IP 與 PoE 化」，設備精簡、規格統一。五大目標依序為：1) 網路設備整併（AP/DVR/Router/Switch 都納入 UniFi，服務整合至 NAS）；2) 網路基礎建設（以 VLAN 隔離、QoS 與政策控管，兼用多 PPPoE）；3) 居家監控（全面 IP Camera + PoE/WiFi，擺脫傳統 DVR）；4) 網路服務（DNS、個人服務與 LAB 轉移 NAS + Docker）；5) 邁向 10G（骨幹升級，端點依需 2.5G）。核心信念是用穩定網路與足夠頻寬搭配軟體整合，減少硬體堆疊。

### 目標 1, 網路設備整併
現況採 UDM-PRO 為控制中樞，USW-Enterprise 24 PoE 作為 L3 交換與供電骨幹，桌面側再以 Flex Mini；無線以 UAP AC-Lite/LR 布建。老舊的 Netgear/MikroTik/小米路由與白牌 DVR/電話總機/第四台設備悉數退役。為 10G 做準備，NAS 裝 Mellanox SFP+ NIC 走 DAC；桌機與筆電升至 2.5G。交換器選擇 ENT 24 PoE 取得 2×SFP+ 与 12×2.5G 與 L3 能力，比 8 埠款更耐用。線路一體化：沿用當年以 CAT5e 結構化佈線的智慧，換面板為 RJ45、機櫃端進 patch panel，電話 RJ11 插 RJ45 兼容，透過跳線靈活轉換用途。整理後 5U 即容納 Router/Switch/NAS/UPS，視覺與維護大幅簡化。

### 目標 2, 網路基礎建設
依賴 UniFi OS Console 的整合，讓非專職網管也能部署 VLAN、VPN、威脅防護、監控與流量分析。作者實作 5 條 VLAN：TRUNK（骨幹設備）、MODEM（直連數據機供 PPPoE/MOD）、NAS（容器/LAB）、HOME（家人上網）、GUEST/IOT（訪客與不可信裝置隔離）。UDM-PRO 提供拓樸、Port 與 App 流量可視化，搭配 Internal DNS rewrite（NAS 的 AdGuard Home）讓內外域名與反代協同。VPN 採 L2TP 與 Teleport（WireGuard 底層），後者行動端一鍵生效。新版引入 Traffic Rules（App 類別/終端/時段三維度控制）與 Traffic Routes（指定來源/目的/介面分流），進一步提升家庭情境（家長監護）與多 PPPoE 應用（WAN1/2 分工、端點直撥）。

### VLAN
切分 TRUNK/NAS/HOME/GUEST/IOT/MODEM，明確劃分骨幹、家用、實驗與訪客環境，提升安全與維護效率。早期在多廠牌設備上手動設定 tag/untag 與 PVID 相當繁瑣，UDM-PRO 與 Controller 將 Guest Portal、VLAN、路由統整於單一介面，拓樸與流量亦可視化，讓排錯與調整更直觀。跨 VLAN 路由後續由 L3 Switch 接手以解效能瓶頸。

### DNS - AdGuard Home
DNS 放在 NAS Docker，以 AdGuard Home 做廣告/惡意站攔截與內部域名覆寫，其他查詢轉上游 DNS。此舉是所有自架服務的根基：搭配 NAS 反代與 Let’s Encrypt，對內用私網 IP 直達、對外有 SSL 與域名的一致入口，簡化 Port 記憶與安全警示。

### VPN - Teleport VPN / L2TP
UDM-PRO 內建多種 VPN 並含 RADIUS。L2TP 為通用備援；Teleport（WireGuard）在行動端以 WiFiman 幾乎零設定即可通道建立，體驗顯著優於傳統 VPN。Web 端產生邀請連結、手機點擊同意即完成，惟目前仍缺原生 Windows 客戶端，兩者並行使用。

### Traffic Rules - Parental Control
解決過往 UniFi 家用場景缺乏「家長監護」的痛點。新 Traffic Rules 支援三維度：Category（App/Domain/IP/Region/Internet/Local）、Target（全部/群組/指定裝置）、Schedule（多種模板）與 Action（Allow/Block）。背後仰賴 L7 流量辨識，免記港口與 IP，即可一鍵封鎖社群、影音等 App 群組；典型情境如暑期平日晚間封鎖子女手機使用社群 App，部署門檻大幅降低。

### Traffic Routes - Multiple PPPoE Connection
UDM-PRO 1.12.22 與 Network 7.1.66 帶來 Port Remapping 與 Traffic Routes。作者以雙 PPPoE 於單線路同時撥入，WAN1 用浮動 IP 作預設上網，WAN2 用固定 IP 服務 NAS（DDNS、對外服務、Port Forward）與特定來源/目的分流；Port Remapping 讓 SFP+ 可自由指派 LAN/WAN；Traffic Routes 可針對來源裝置或目標網域/IP 指示走 WAN1/2，並驗證 MyIP 等網站顯示不同外部位址。

### 目標 3, 居家監控
傳統 DVR/同軸與電源布線不易、UI 難用，改以 UniFi Protect + G3-Flex（PoE）與 G3-Instant（WiFi+USB-C 供電）升級；UDM-PRO 內建 Protect，插 HDD 即錄影，Web/APP 操作友善。缺點是僅支援自家相機與備份彈性低，建議以 NAS 同步接 RTSP 作第二份錄影。UniFi AP 穩定度提升後，WiFi Cam 成熟可用，供電容易，亦可搭配行動電源作簡易不斷電。

### 目標 4, 網路服務
DS1821+（Ryzen V1500B）升級 32GB RAM 與 10G SFP+ NIC，做為家用服務核心。以 Docker 佈署 ADGuardHome、Portainer、Bitwarden、Iperf3、FileZilla（VNC Web 介面）、code-server（Web VS Code）、Jekyll/GitHub Pages 等；DNS rewrite + 反代 + 免費 SSL + 自有網域，快速發布安全可訪的內部/外部服務。作者主張 NAS 優於自組 PC 作服務器：天然具備 RAID/備份、低功耗穩定、易維護，特別適合存放關鍵資料服務（如 Bitwarden）。另以 code-server 搭配本地容器預覽，實現「瀏覽器即開發機」的遠端寫作/開發流程。

### 網路基礎服務相關
以 AdGuard Home 提供內部 DNS 與覆寫，Portainer 取代 DSM 內建 Docker UI；NAS 反代分流各容器服務，Let’s Encrypt 自動簽憑證，瀏覽器免警示且集中在 443。範例展示 Bitwarden：容器映射端口、DNS 指向、反代規則、憑證綁定四步完成，達到對內友善、對外安全。

### 個人應用相關
探討 NAS 作服務器的優勢：資料保護/備份先天到位、電力與長時運轉優化、操作門檻相對友善。以 Bitwarden 為例，家用負載輕但資料重要，放 NAS 容器優於自組 PC。作者也分享從 MiniPC/Linux Docker 過渡的經驗與抉擇。

### Network Tools
以 FileZilla（Docker 打包 GUI+VNC）作長任務 FTP 客戶端，瀏覽器即用；Iperf3 常駐容器做網速測試，透過 docker exec 或 DSM 內建終端機操作，科學量測 2.5G/10G 效能，輔助後續骨幹診斷。

### Labs for Web Developer
開發工作以 code-server（Web VS Code）+ GitHub Pages/Jekyll 為核心：在 NAS 上本地預覽、編輯與一鍵推送，實現隨地以瀏覽器工作。另復刻舊站（BlogEngine on Mono）以 Docker 重現，驗證備份與兼容性。作者仍在尋找可於此環境自動處理剪貼簿圖像的 VSCode 擴充，以求全雲端化寫作流程。

### 參考資源
彙整 Teleport/WireGuard、UniFi Protect、G3 Instant、AdGuard Home、Bitwarden、FileZilla 與 Iperf3 等官方/部落格/YouTube 連結，便於延伸研究與上手。

### 目標 5, 邁向 10G 的路
策略是骨幹先 10G（NAS 與交換器走 SFP+ DAC 降溫省成本），端點多以 2.5G 應用，逐步升級。實測顯示兩大瓶頸：UDM-PRO 內部等同「10G 路由＋1G×8 交換」的合體，跨區流量在內部 1G 匯流處受限；另外 Threat Management 啟用時消耗大量 CPU，跨 VLAN 傳輸僅約 1.4Gbps。停用威脅偵測可回到接近理論值，但失去保護不理想。最終以 USW-Enterprise L3 Switch 承擔跨 VLAN 路由，使 PC↔NAS 穩定達 2.3~2.5Gbps，內網流量不再繞行 UDM-PRO，兼顧效能與安全。

### UDM-PRO 架構上的瓶頸
UDM-PRO 的 10G 與 1G×8 在硬體邏輯上如兩台設備拼合，內部存在 1G 匯流限制；若 NAS 在 10G 口、用戶在 1G×8 端，整體吞吐難以同時拉滿。社群常見做法是「所有終端進專業交換器，UDM-PRO 僅作上聯路由」。新韌體雖允許第二個 SFP+ 指派為 LAN，提升彈性，但根本問題仍需外置交換器承流才能破局。

### 啟用 threat management 的效能瓶頸
Iperf3 測試指出：PC→NAS 跨 VLAN 僅約 1.4Gbps，關閉 Threat Management 後回升；原因在於 UDM-PRO 做 L7 檢測吃 CPU，成為路由瓶頸。解方是啟用 L3 Switch 做跨 VLAN 路由，內網流量就近在交換器處理，避開 UDM-PRO 的 L7 分析與內部限制，效能與穩定度顯著改善。

### 小結
15 年前後對比，最大差異在「用軟體整合取代硬體堆疊」。UniFi 提供一體化管理與視覺化操作，NAS+Docker 則成為自架服務的穩定平台；兩者搭配讓家用網路同時具備可擴充、好維護與夠快的特性。雖未全面 10G，且設備偶有缺貨，但現況已達「家用最適」：核心用 UniFi 穩定控管、服務交給 NAS 專責執行、效能靠 L3 Switch 聰明分流。整體經驗與踩坑筆記可供家用升級者參考與借鏡。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基礎網路概念：IP、子網、DHCP、NAT、PPPoE、路由 vs 交換
   - VLAN 與網段隔離：Tagged/Untagged、PVID、Trunk/Access
   - 家用網路設備常識：Router/Firewall、L2/L3 Switch、WiFi AP、PoE 供電
   - NAS 與 Docker：容器部署、Volume、Reverse Proxy、SSL 憑證
   - 基礎資安與監控：Threat Management、L7 流量識別、家庭監控（RTSP、錄影）

2. 核心概念：
   - UniFi 整合生態：以 UDM-Pro 為核心，集中管控 Router/Switch/AP/Protect
   - 網段分離與流量治理：VLAN、L3 交換、Traffic Rules、Traffic Routes、Guest/IOT 隔離
   - 服務集中在 NAS：Docker 化（DNS、反代、工具、個人服務）＋ 憑證自動化
   - 家庭 VPN 與遠端：L2TP 與 Teleport（WireGuard 底層）一鍵接入
   - 走向 10G 的務實路徑：核心先升 10G（SFP+ DAC），邊緣 2.5G，辨識 UDM-Pro 架構與效能瓶頸
   - 概念間關係：UniFi 提供網路控制面；VLAN/Traffic* 負責治理與路由策略；NAS 提供服務承載與對外發布；10G/2.5G 與布線是性能基礎。

3. 技術依賴：
   - UniFi OS/Network/Protect（UDM-Pro、USW-Enterprise、UAP）
   - Synology DSM：Docker、Reverse Proxy、Let’s Encrypt、Surveillance Station（可作 Protect 備份）
   - DNS 層：AdGuard Home（Rewrite/過濾/上游轉發）
   - VPN：Teleport（WireGuard）與 L2TP/IPsec、RADIUS
   - L3 路由：USW-Enterprise L3 Inter-VLAN Routing 減負 UDM-Pro
   - 對外存取：Domain + DDNS、Port Forward、固定 PPPoE IP
   - 實體連接：SFP+ DAC、CAT5e/CAT6A、2.5G/10G NIC

4. 應用場景：
   - 家用網路整併與維運簡化（單一控制台、拓樸可視化、流量監控）
   - 家庭網段隔離（家人/實驗室/LAN 主幹/NAS/Guest-IoT）
   - 家長監護（依 App 類別、裝置、時段的 Traffic Rules）
   - 雙 PPPoE 多出口（NAS 走固定 IP，其他走浮動；針對域名/IP 制定路由）
   - 家庭監控（UniFi Protect + PoE/WiFi 攝影機，NAS RTSP 備份）
   - 個人服務託管（Bitwarden、自架工具、GitHub Pages 預覽、code-server）
   - 10G/2.5G 提速（核心鏈路先升級、辨識 UDM-Pro Threat Mgmt 瓶頸、以 L3 Switch 分流）

### 學習路徑建議
1. 入門者路徑：
   - 認識家庭網路元件與基本設定（WAN/LAN、DHCP、WiFi、PPPoE）
   - 在 UniFi Controller 建立單一 SSID 與基本 VLAN（HOME/Guest）
   - 在 NAS 安裝 AdGuard Home，做簡單 DNS Rewrite
   - 體驗 UniFi Protect（先裝一台攝影機），熟悉 Web/APP 操作

2. 進階者路徑：
   - 規劃多 VLAN（TRUNK/NAS/HOME/GUEST/IOT/MODEM），掌握 Tagged/Untagged 與 Port Profile
   - 啟用 Traffic Rules（App 類別/裝置/時段）實作 Parental Control
   - 設定 Teleport/L2TP VPN；導入 RADIUS 管理帳號
   - 在 NAS 佈署 Docker 堆疊：Reverse Proxy、Let’s Encrypt、Portainer；以域名進站
   - 練習 Traffic Routes 與 Dual PPPoE（NAS 固定 IP、其他走浮動 IP）

3. 實戰路徑：
   - 細化 Inter-VLAN 路由：於 L3 Switch 落地，以減少 UDM-Pro CPU 與 Threat Mgmt 影響
   - 監控與備援：Protect 錄影，NAS 以 RTSP 同步第二份備份
   - 內外服務發布：Port Forward 精準指到 WAN1/2；以 WAF/Threat Mgmt/更新機制降低風險
   - 效能檢核：以 iperf3 驗證 2.5G/10G 實測路徑，調整布線與路由
   - 開發者工作流：code-server + GitHub Pages 本地預覽；自架 Bitwarden 等低資源高價值服務

### 關鍵要點清單
- UniFi 全家桶整合：以 UDM-Pro 為控制中樞整合 Router/Switch/AP/Protect，簡化家用網管複雜度 (優先級: 高)
- VLAN 規劃與隔離：TRUNK/NAS/HOME/GUEST/IOT/MODEM 分網段，控管存取與流量邊界 (優先級: 高)
- Guest/IOT 網路：以 Guest Network 與防火牆隔離不受信設備，僅允許上網不入內網 (優先級: 高)
- Traffic Rules（家長控制）：以 App 類別/裝置/時段規則做允許/封鎖，符合家庭場景 (優先級: 高)
- Traffic Routes（多出口）：Dual PPPoE 與策略路由，NAS/特定服務走固定 IP，其他走浮動 (優先級: 高)
- Teleport VPN（WireGuard）：行動端一鍵連回家，降低傳統 VPN 設定門檻 (優先級: 中)
- AdGuard Home（DNS 中樞）：黑白名單過濾＋Rewrite，作為內網域名與服務導流基座 (優先級: 高)
- NAS 反代與憑證：DSM Reverse Proxy + Let’s Encrypt，自動化 HTTPS 與多服務同埠發布 (優先級: 高)
- 家庭監控（UniFi Protect）：PoE/WiFi 攝影機整合錄影，RTSP 輸出可交由 NAS 備份 (優先級: 中)
- 10G/2.5G 升級策略：核心先 10G（SFP+ DAC），端點 2.5G，線材與溫控考量（RJ45 vs SFP+）(優先級: 中)
- UDM-Pro 架構認知：內建 8 埠交換與 10G 連結有結構限制，重流量改走外部 Switch (優先級: 高)
- Threat Management 效能影響：L7 檢測吃 CPU，跨 VLAN 大流量建議以 L3 Switch 分擔路由 (優先級: 高)
- L3 Switch Inter-VLAN Routing：就近於交換器路由，減少往返 UDM-Pro，提升吞吐 (優先級: 高)
- 實測與診斷（iperf3）：以容器化 iperf3 驗證每段鏈路，定位瓶頸再調整 (優先級: 中)
- 個人服務容器化：Bitwarden、FileZilla（VNC）、code-server、工具服務以 NAS+Docker 託管 (優先級: 中)
