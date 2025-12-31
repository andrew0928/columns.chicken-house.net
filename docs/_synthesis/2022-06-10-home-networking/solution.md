---
layout: synthesis
title: "水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路"
synthesis_type: solution
source_post: /2022/06/10/home-networking/
redirect_from:
  - /2022/06/10/home-networking/solution/
postid: 2022-06-10-home-networking
---

以下為針對原文內容提取且可落地實作的 17 個解決方案案例，皆包含問題、根因、方案、步驟、關鍵設定/程式碼、實測數據與教學練習，便於課程、專題與評測使用。

------------------------------------------------------------

## Case #1: 家用網路設備整併到 UniFi + NAS

### Problem Statement（問題陳述）
- 業務場景：家用網路歷經 15 年演進，曾同時運行 Router、DVR、電話總機、非網管交換器、PC Server 等多種異質設備，佈線混雜含同軸電纜與 RJ11，管理介面分散。需要整併為少數設備並統一管理，降低維護成本並提升可用性。
- 技術挑戰：如何在不犧牲功能（VLAN、PoE、監控、VPN、DNS、備份）的前提下，用最少的設備與統一平台完成整併。
- 影響範圍：涵蓋整個家庭骨幹網路、Wi-Fi、監控、儲存與服務承載。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 設備異質且分散管理，維護成本高。
  2. 同軸電纜、RJ11 等過時介面已不合時宜。
  3. 舊 PC 伺服器與 DVR 已老化、故障率提升。
- 深層原因：
  - 架構層面：沒有統一控制器與可視化拓樸，擴充困難。
  - 技術層面：缺乏 PoE、L3 管理、整合式監控與反向代理能力。
  - 流程層面：設定跨多台設備重複進行且易錯，變更風險高。

### Solution Design（解決方案設計）
- 解決策略：以 UniFi 全家桶（UDM-Pro + USW-Enterprise 24 PoE + UAP）統一網路控制、PoE 供電與監控；以 Synology NAS 取代自組 PC 伺服器承載服務（Docker/VM/備份）。布線全面統一 RJ45，透過 Patch Panel 實現結構化佈線與彈性跳線。

- 實施步驟：
  1. 資產盤點與目標規劃
     - 實作細節：列出所有現有設備與功能，對照目標（VLAN、PoE、監控、VPN、DNS、10G/2.5G）。
     - 所需資源：表單/資產清單工具
     - 預估時間：0.5 天
  2. 核心設備採購與安裝
     - 實作細節：UDM-Pro、USW-Enterprise 24 PoE、UAP AC-Lite/LR、NAS（DS1821+）、SFP+ DAC、2.5G NIC。
     - 所需資源：機櫃、CAT6A 短跳線、Patch Panel
     - 預估時間：1-2 天
  3. 重新佈線與標示
     - 實作細節：RJ45 統一，RJ11 相容需求保留；電話/同軸淘汰；Patch Panel 標示與色碼。
     - 所需資源：壓線工具、標籤機、跳線
     - 預估時間：1 天
  4. 控制器與服務整合
     - 實作細節：UniFi OS Console 導入設備；NAS 上佈署 Docker 與核心服務。
     - 所需資源：UDM-Pro、Synology DSM
     - 預估時間：0.5-1 天

- 關鍵程式碼/設定：
```text
拓樸與命名規範（節選）
- Rack U space: Router(1U), Switch(1U), NAS x2(4U), UPS
- 網段：TRUNK(10.0.0.0/24), NAS(192.168.100.0/24), HOME(192.168.200.0/24), GUEST/IOT(192.168.201.0/24)
- 標色：主幹藍、客戶端白、對外黑、SFP+ DAC 標記
```

- 實際案例：以 5U 機櫃容納 Router、Switch、NAS、UPS；廢除 DVR、電話總機、非管控交換器與自組 PC 伺服器。
- 實作環境：UDM-Pro（FW 1.12.22）、UniFi Network 7.1.66、USW-Enterprise 24 PoE、Synology DS1821+。
- 實測數據：
  - 改善前：多台異質設備、分散 UI、維護頻繁。
  - 改善後：單一 Console 管理、Patch Panel 統一、5U 即可容納。
  - 改善幅度：設備數量減少 >50%，維護路徑縮短為單一平台。

Learning Points（學習要點）
- 核心知識點：
  - 控制器導向網路設計思維（SDN）。
  - 結構化佈線與標示體系的重要性。
  - 家用環境中以 NAS 承載服務的優勢。
- 技能要求：
  - 必備技能：基礎網路、PoE、NAS 管理。
  - 進階技能：SDN 控制器、Docker 卷管理、機櫃規劃。
- 延伸思考：
  - 何時選擇 All-in-One vs. 模組化？
  - UniFi Protect 綁定自家攝影機，如何評估替代方案？
  - 預留 10G/2.5G 的升級彈性。
- Practice Exercise：
  - 基礎：列出家中設備清單與功能映射（30 分）
  - 進階：設計 5U 內的設備安置與跳線圖（2 小時）
  - 專案：完成從舊網到新網的切換與回復計劃（8 小時）
- Assessment Criteria：
  - 功能完整性（40%）：所有功能移轉與可用
  - 程式碼品質（30%）：文件與標示、命名規範
  - 效能優化（20%）：佈線、散熱、電源
  - 創新性（10%）：自動化與報表

------------------------------------------------------------

## Case #2: VLAN 隔離與骨幹規劃（TRUNK/NAS/HOME/GUEST/MODEM）

### Problem Statement（問題陳述）
- 業務場景：家中同時存在家人上網、Lab、NAS、IoT/訪客與直撥 PPPoE 需求，需隔離網段、控制互通與管理路由。
- 技術挑戰：跨 Router/Switch/AP 進行 VLAN Tag/Untag 與 PVID 設定繁瑣且易錯；Guest Portal 與訪客隔離設定複雜。
- 影響範圍：涵蓋所有有線/無線設備與跨網段存取。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 多設備手動設定 VLAN，易發生不通。
  2. Guest 與內網隔離需額外 Portal/防火牆規則。
  3. 缺少拓樸與流量視覺化工具。
- 深層原因：
  - 架構：未集中化控制與網段策略。
  - 技術：對 VLAN tag/pvid/routing 理解不足。
  - 流程：變更需重複在多台設備操作。

### Solution Design（解決方案設計）
- 解決策略：以 UDM-Pro + UniFi Controller 定義 VLAN Networks 與 Port Profile，透過 AP SSID 綁定 VLAN，並以內建防火牆規則與路由控制跨網通訊。

- 實施步驟：
  1. 定義 VLAN Networks
     - 實作細節：TRUNK(0, 10.0.0.0/24)、MODEM(10)、NAS(100, 192.168.100.0/24)、HOME(200, 192.168.200.0/24)、GUEST/IOT(201, 192.168.201.0/24)。
     - 所需資源：UniFi Controller
     - 預估時間：0.5 小時
  2. Port Profiles 與 SSID 綁定
     - 實作細節：Switch 介面設定 Tagged/Untagged 與 PVID，SSID 綁 HOME/GUEST。
     - 所需資源：USW-Enterprise、UAP
     - 預估時間：1 小時
  3. 基礎防火牆與路由
     - 實作細節：限制 GUEST/IOT 不可互通內部網；NAS 僅開放必要服務給 HOME。
     - 所需資源：UDM-Pro FW
     - 預估時間：1 小時

- 關鍵程式碼/設定：
```text
防火牆規則示例（概念）
- Block: Source=GUEST(201), Destination=LAN (RFC1918), Action=Drop
- Allow: Source=HOME(200), Destination=NAS(100): SMB(445)/HTTPS(443)
- Allow: GUEST(201) -> Internet
```

- 實際案例：作者以 5 個用途網段建立隔離，管理拓樸與 PORT 流量統計於 UniFi Console。
- 實作環境：UDM-Pro / USW-Enterprise 24 PoE / UAP。
- 實測數據：
  - 改善前：變更 VLAN 需跨 3 台設備重覆設定；錯誤率高。
  - 改善後：單一控制器集中設定與可視化。
  - 改善幅度：操作步驟減少約 60-70%。

Learning Points
- 核心知識點：VLAN/PVID/Trunk、SSID 與 VLAN 綁定、跨網段路由。
- 技能要求：必備 VLAN/路由基礎；進階 L3 Switch 與 ACL。
- 延伸思考：IoT 安全模型、跨 VLAN 服務暴露面縮減。
- Practice：基礎—建 3 個 VLAN；進階—配置 ACL；專案—以圖描述終端口規劃。
- 評估：隔離正確性、規則最小授權、文件完整性。

------------------------------------------------------------

## Case #3: 訪客/IoT 網段隔離（Guest Network）

### Problem Statement
- 業務場景：家中 IoT 與訪客設備可信度低，需允許上網但不可觸達內部服務。
- 技術挑戰：傳統 Router 設定訪客隔離與 Captive Portal 複雜。
- 影響範圍：所有訪客與 IoT 無線設備。
- 複雜度：低

### Root Cause Analysis
- 直接原因：IoT/訪客與內部資產在同網段，缺乏隔離。
- 深層原因：
  - 架構：沒有專用訪客網。
  - 技術：缺少 L2/L3 隔離與認證入口。
  - 流程：臨時訪客加入流程未標準化。

### Solution Design
- 解決策略：以 UDM-Pro 內建 Guest Network 功能建立 GUEST/IOT(201) SSID 與網段，預設隔離內網、允許上網。

- 實施步驟：
  1. 建立 Guest Network（VLAN 201）
  2. 建立 SSID: GUEST，綁定 VLAN 201
  3. 測試：GUEST 能上網且無法掃描內部 RFC1918

- 關鍵設定：
```text
UniFi Controller
- Network: GUEST/IOT (VLAN 201, 192.168.201.0/24, Guest Policy=ON)
- WLAN: SSID=GUEST, Network=GUEST/IOT
```

- 實際案例：作者以 UDM-Pro Guest Network 取代自行搭建的 Portal。
- 實測：訪客可上網；掃描 192.168.100.0/24 無回應。

Learning Points
- 知識點：Guest Policy 隔離、SSID 與 VLAN 對應。
- 技能：基礎 SSID/VLAN；進階策略縮減。
- 練習：建 Guest SSID（30 分）；進階加入 QR 與時間制限（2 小時）。

------------------------------------------------------------

## Case #4: AdGuard Home 實作內網 DNS Rewrite + 全局廣告阻擋

### Problem Statement
- 業務場景：自架服務需以網域而非 IP 存取，避免 Hairpin NAT；同時希望全家設備阻擋廣告/惡意網域。
- 技術挑戰：維護內部 DNS 對映（Split-Horizon），又需上游轉遞與黑白名單。
- 影響範圍：所有內外部服務存取與上網體驗。
- 複雜度：中

### Root Cause Analysis
- 直接原因：內網服務無可解析域名；瀏覽器出現憑證警告。
- 深層原因：
  - 架構：缺少內部 DNS 區域與反向代理規劃。
  - 技術：缺乏統一黑名單與 Rewrite 介面。
  - 流程：手動 hosts/瀏覽器例外繁瑣。

### Solution Design
- 解決策略：在 NAS Docker 佈署 AdGuard Home，集中處理 DNS 過濾/黑白名單/Rewrite，配合 Synology 反向代理與 Let’s Encrypt。

- 實施步驟：
  1. 以 Docker 佈署 AdGuard Home
  2. 設上游 DNS、啟用濾網清單
  3. 建立內部服務 rewrite（如 bitwarden.home）
  4. 于 Synology 建反向代理與憑證

- 關鍵程式碼/設定：
```yaml
# docker-compose.yml (AdGuard Home)
version: "3"
services:
  adguardhome:
    image: adguard/adguardhome:latest
    container_name: adguardhome
    ports:
      - "53:53/tcp"
      - "53:53/udp"
      - "3000:3000"
    volumes:
      - /volume1/docker/adguard/conf:/opt/adguardhome/conf
      - /volume1/docker/adguard/work:/opt/adguardhome/work
    restart: unless-stopped
```
```text
AdGuard → DNS Rewrite
- bitwarden.home.chicken-house.net  ->  192.168.100.50
```

- 實際案例：作者用 AdGuard Home + Synology Reverse Proxy 與免費憑證整合，所有服務共用 443。
- 實作環境：Synology DSM、Docker、AdGuard Home。
- 實測數據：
  - 改善前：以 IP+Port 存取且有 SSL 警告。
  - 改善後：以網域+HTTPS 存取，瀏覽器零警告；廣告/惡意域名阻擋生效。
  - 幅度：用戶體感顯著改善；維護成本下降。

Learning Points
- 知識點：本地 DNS、上游轉遞、域名 Rewrite、反向代理。
- 技能：Docker/DSM 操作、憑證綁定。
- 練習：以內網服務建立一個域名與憑證（2 小時）。

------------------------------------------------------------

## Case #5: Teleport VPN（WireGuard）與 L2TP 回退

### Problem Statement
- 業務場景：外出需安全連回家中資源，傳統 L2TP 配置繁瑣且易踩坑。
- 技術挑戰：快速布署、免手動設定參數、使用體驗佳。
- 影響範圍：遠端工作、行動裝置存取內網。
- 複雜度：低-中

### Root Cause Analysis
- 直接原因：L2TP 設定冗長，裝置相容性問題。
- 深層原因：
  - 架構：缺少現代化、輕量且高效協定。
  - 技術：用戶端參數配置錯誤率高。
  - 流程：裝置導入流程不一致。

### Solution Design
- 解決策略：啟用 UDM-Pro Teleport（WireGuard 基礎），以 WiFiman App 一鍵導入；Windows 端暫以 L2TP 備援。

- 實施步驟：
  1. UDM-Pro 開啟 Teleport，產生邀請連結
  2. 用戶手機安裝 WiFiman → 點連結導入
  3. 測試連通內部網；Windows 端配置 L2TP 備援

- 關鍵設定/指令：
```text
UDM-Pro → Teleport: Generate Link → Share (SMS/Email)
Client: WiFiman → Accept → Connect
L2TP 備援：UDM-Pro 內建 VPN Server 配置 + 帳號（RADIUS）
```

- 實際案例：行動端幾乎零設定導入成功；Windows 端暫以 L2TP。
- 實測數據：
  - 改善前：L2TP 設定步驟繁多。
  - 改善後：手機端 1-2 分鐘完成導入；連線穩定。
  - 幅度：導入時間降低 >80%。

Learning Points
- 知識點：WireGuard 對比 OpenVPN/L2TP、行動端零配置體驗。
- 練習：為兩台手機發放 Teleport 連結並回報延遲與速率（30 分）。

------------------------------------------------------------

## Case #6: 以 Traffic Rules 實現家長監護（Parental Control）

### Problem Statement
- 業務場景：需限制孩子在特定時段使用社群/影音 App。過去以 MAC/IP 封鎖被輕易繞過。
- 技術挑戰：需 L7 App 辨識、可排程、精準指定裝置。
- 影響範圍：家庭無線設備。
- 複雜度：中

### Root Cause Analysis
- 直接原因：傳統基於 IP/Port 的封鎖對現代 App 無效。
- 深層原因：
  - 架構：缺少 L7 流量辨識。
  - 技術：沒有時間維度的規則引擎。
  - 流程：每次改規則需跨設備與手動維護。

### Solution Design
- 解決策略：啟用 UniFi Traffic Identification，建立 Traffic Rules（Category=Social Networks 或 App 群組），指定 Target 裝置與排程，Action=Block。

- 實施步驟：
  1. 開啟 Traffic & Device Identification
  2. 新增 Rule：Category=Social Networks，Target=Child's iPhone，Schedule=Mon-Fri 22:00-24:00，Action=Block
  3. 驗證實效與例外清單

- 關鍵設定：
```text
Traffic Rule
- Match: Category = Social Networks
- Target: Device = <Child-iPhone>
- Schedule: Mon-Fri, 22:00-24:00
- Action: Block
```

- 實際案例：示範以圖形化 UI 定義時段封鎖，效果可靠。
- 實測數據：
  - 改善前：需額外 SSID/VLAN/防火牆組合；易被繞過。
  - 改善後：GUI 3 分鐘完成；封鎖精準。
  - 幅度：設定時間縮短 >70%，管控成功率顯著提升。

Learning Points
- 知識點：L7 Category、時間排程、Target 裝置群組。
- 練習：建立兩條不同 App 類別的時段封鎖（30 分）。

------------------------------------------------------------

## Case #7: 一線路多 PPPoE：Dual WAN（WAN1 動態 + WAN2 撥接固定 IP）

### Problem Statement
- 業務場景：同一條 HiNet 光世代線需同時撥兩組 PPPoE，WAN1 提供一般上網（浮動 IP）、WAN2 提供 NAS 對外服務（撥接固定 IP）。
- 技術挑戰：UDM-Pro 前版本 Port 綁定限制、無 Policy Routing，導致 WAN2 僅作備援。
- 影響範圍：外部服務、下載、來源 IP 控制。
- 複雜度：中-高

### Root Cause Analysis
- 直接原因：早期 UDM-Pro 無 Port Remapping 與 Traffic Routes。
- 深層原因：
  - 架構：雙 WAN 僅冗餘，無流向控制。
  - 技術：Policy Routing/Traffic Routes 缺失。
  - 流程：手動調整路徑繁瑣。

### Solution Design
- 解決策略：升級 UDM-Pro 1.12.22 + UniFi Network 7.1.66，啟用 Port Remapping（RJ45 作 WAN，SFP+ 作 LAN），建立兩組 PPPoE，利用 Traffic Routes 指定 NAS 經 WAN2，上網預設走 WAN1；Port Forward 指定 WAN2。

- 實施步驟：
  1. Internet：建立 PPPoE x2（WAN1=動態；WAN2=撥接固定 IP）
  2. Port Remapping：Port8,9→WAN；Port10,11（SFP+）→LAN
  3. Traffic Routes：Source=NAS，Action=Use WAN2
  4. Port Forward：Interface=WAN2，443/80 → NAS

- 關鍵設定/指令：
```text
Traffic Routes
- Rule#1: Source=Group(NAS VLAN 100), Category=Internet, Interface=WAN2
Port Forward
- Interface: WAN2
- From: 443 -> To: 192.168.100.50:443
```

- 實際案例：作者以 myip.com / whatismyipaddress.com 驗證不同裝置/網站走不同 WAN。
- 實測數據：
  - 改善前：WAN2 只能備援。
  - 改善後：NAS 固定對外 IP，其他流量走 WAN1；驗證 IP 正確。
  - 幅度：外部服務可用性大幅提升；來源 IP 控制達成。

Learning Points
- 知識點：Dual PPPoE、Port Remapping、Policy Routing。
- 練習：建立第三條規則：特定域名走 WAN2（2 小時，含驗證）。

------------------------------------------------------------

## Case #8: Traffic Routes 指定特定裝置/網站走特定 WAN（路由策略驗證）

### Problem Statement
- 業務場景：需將某裝置連到特定網站的流量改走 WAN2 以驗證路徑。
- 技術挑戰：以網域為條件在測試中不生效，須以 IP 指定。
- 影響範圍：細粒度流量控制與驗證。
- 複雜度：低-中

### Root Cause Analysis
- 直接原因：Domain-Based Routing 在特定站點暫未匹配成功。
- 深層原因：
  - 架構：DNS 解析/快取/多 IP 導致匹配困難。
  - 技術：CDN 多 A 記錄與 Anycast。
  - 流程：測試方法未固化（需 nslookup）。

### Solution Design
- 解決策略：以 nslookup 取得目標站 IP 列表，Traffic Route 以 IP 為 Category 條件設規則，指定裝置流量走 WAN2。

- 實施步驟：
  1. nslookup 目標域名取得 IPv4
  2. Traffic Routes：Category=IP Address=目標 IP、Source=裝置、Interface=WAN2
  3. 以 myip.com 等站驗證來源 IP

- 關鍵程式碼/設定：
```bash
# Windows
nslookup myip.com
# UniFi Traffic Routes
Category: IP Address = 172.67.208.45, 104.21.23.5
Source: ANDREW-PC
Interface: WAN2
```

- 實際案例：作者以 myip.com 測試，對照組走 WAN1，驗證成功。
- 實測數據：測試頁面回報的 Public IP 分別對應 WAN1/WAN2，符合預期。

Learning Points
- 知識點：CDN/多 IP、域名與策略路由關係。
- 練習：為三個常用站建立 IP-Based 路由規則並驗證（1 小時）。

------------------------------------------------------------

## Case #9: MODEM VLAN 直撥 PPPoE（繞過路由器測試/臨時需求）

### Problem Statement
- 業務場景：需在 PC 端直接撥 PPPoE 取得外部 IP，繞過家用 Router 做測試或臨時需求。
- 技術挑戰：需將 ONT/小烏龜透過特定 VLAN 直接橋接到終端裝置。
- 影響範圍：測試/除錯與特殊應用。
- 複雜度：中

### Root Cause Analysis
- 直接原因：Router/NAT 會干擾測試與來源 IP。
- 深層原因：
  - 架構：缺少直連 MODEM 的 VLAN。
  - 技術：Port/VLAN 映射概念不清。
  - 流程：缺少預先規劃的測試 Port。

### Solution Design
- 解決策略：建立 MODEM VLAN (ID=10) 直連小烏龜，Switch 上對應 Port 設為 Untagged VLAN 10，PC 插該 Port 並以 OS 原生 PPPoE 撥接。

- 實施步驟：
  1. 建立 VLAN 10：MODEM (No DHCP)
  2. Switch Port X：Untagged=VLAN 10
  3. Windows 網路設定：新增 PPPoE 撥接 → 帳密輸入 → 撥接

- 關鍵設定：
```text
USW Port X Profile: Untagged VLAN=10 (MODEM), Tagged=None
Windows: 新增 PPPoE 連線 → 使用者名稱/密碼（ISP 提供）
```

- 實測：PC 能取得 ISP 發放的 Public IP，與家用路由無關。

Learning Points
- 知識點：Bridge 概念、Untagged/Tagged、OS 層撥接。
- 練習：在實驗 VLAN 中完成一次 PPPoE 撥接（30-45 分）。

------------------------------------------------------------

## Case #10: UniFi Protect 居家監控導入（G3-Flex/G3-Instant）

### Problem Statement
- 業務場景：傳統 DVR + 類比攝影機頻繁故障、介面難用、佈線複雜（同軸+供電）。
- 技術挑戰：改為 IP/PoE 或 Wi-Fi + USB-C 電源，統一於 UDM-Pro 內建 Protect 管理。
- 影響範圍：家庭室內外監控、遠端查看與錄影。
- 複雜度：中

### Root Cause Analysis
- 直接原因：類比攝影機與 DVR 老化，UI 不友善。
- 深層原因：
  - 架構：非 IP 化，無集中管理。
  - 技術：PoE/Wi-Fi 規劃與電源供應未標準化。
  - 流程：錄影備份流程缺乏。

### Solution Design
- 解決策略：UDM-Pro 裝碟即錄，採用 G3-Flex（PoE）與 G3-Instant（Wi-Fi + USB-C），以 Protect Web/APP 管理與查看；如需備份以 Synology SS 抄錄（見下一案）。

- 實施步驟：
  1. UDM-Pro 裝入硬碟、啟用 Protect
  2. 以 PoE/Wi-Fi 加電與網路接入攝影機
  3. 定義動態偵測/錄影留存策略

- 關鍵設定：
```text
UDM-Pro Protect
- Add Device: UVC-G3-Flex (PoE), UVC-G3-Instant (Wi-Fi)
- Recording: Motion-based / Continuous
- Retention: 依硬碟容量配置
```

- 實測：使用者反饋介面易用；家庭成員頻繁使用 APP 檢視。
- 限制：UniFi Protect 僅支援自家攝影機；備份導出不便。

Learning Points
- 知識點：PoE vs Wi-Fi 攝影機取捨、存儲與留存。
- 練習：佈署 1 PoE + 1 Wi-Fi 攝影機並開啟動態偵測（2 小時）。

------------------------------------------------------------

## Case #11: 監控備援錄影：UniFi Protect RTSP → Synology Surveillance Station

### Problem Statement
- 業務場景：UniFi Protect 雖易用，但大量匯出/備援方案不足，需要長期留存/備援。
- 技術挑戰：將 Protect 串接 NAS 作為二次錄影。
- 影響範圍：關鍵畫面留存、防止單點故障。
- 複雜度：中

### Root Cause Analysis
- 直接原因：Protect 匯出大量影像不便。
- 深層原因：
  - 架構：單一錄影點。
  - 技術：備援流程未建立。
  - 流程：無自動化同步抄錄。

### Solution Design
- 解決策略：啟用每支 UniFi Camera 的 RTSP，於 Synology SS 新增「自訂攝影機」以 RTSP 拉流錄影。

- 實施步驟：
  1. Protect 啟用攝影機 RTSP URL
  2. Synology SS → 新增攝影機 → 自訂（RTSP）
  3. 設錄影排程/留存

- 關鍵設定（示例）：
```text
RTSP URL（範例）
rtsp://<camera-ip>:554/s0   # 依機型通道而定

Synology SS:
- 相容性：User-defined / Generic RTSP
- URL：rtsp://user:pass@camera-ip:554/s0
```

- 實測：NAS 成功二次錄影，作為備援留存。
- 限制：Synology SS 通常需授權；資源占用增加。

Learning Points
- 知識點：RTSP 拉流、雙平台錄影留存。
- 練習：將 1 台攝影機 RTSP 串入 SS 並驗證回放（1-2 小時）。

------------------------------------------------------------

## Case #12: Synology Reverse Proxy + Let’s Encrypt（多服務共用 443）

### Problem Statement
- 業務場景：多個 Docker 服務需以 HTTPS 與自訂網域對外/對內提供，避免不同埠號與 SSL 警告。
- 技術挑戰：反向代理規則與憑證自動續約。
- 影響範圍：所有 Web 服務體驗與維護成本。
- 複雜度：中

### Root Cause Analysis
- 直接原因：服務散落不同 Port；無憑證導致警告。
- 深層原因：
  - 架構：未集中於反向代理。
  - 技術：憑證申請與續約流程不熟。
  - 流程：DNS 對應未自動化。

### Solution Design
- 解決策略：於 Synology Control Panel → Application Portal 設定反向代理，讓多個服務共用 443，並綁定 Let’s Encrypt 憑證；配合 AdGuard DNS Rewrite。

- 實施步驟：
  1. Docker 起服務（例：Bitwarden）
  2. AdGuard 設定內網域名 → 映射至 NAS
  3. DSM → Reverse Proxy：domain → 127.0.0.1:Port
  4. DSM → Security → Certificate：申請/綁定

- 關鍵設定：
```text
Reverse Proxy (範例)
- Source: https://bitwarden.home.chicken-house.net:443
- Destination: http://127.0.0.1:8080

Certificate:
- Let's Encrypt (Auto-renew) → bind to "bitwarden.home.chicken-house.net"
```

- 實測：Web 服務以 HTTPS/單一域名提供，瀏覽器無警告。
- 改善幅度：服務數量擴張時，新增成本近似 0（僅新增一條規則）。

Learning Points
- 知識點：反向代理、SNI/單埠多網站、憑證自動化。
- 練習：為兩個容器服務建立反向代理與憑證（2 小時）。

------------------------------------------------------------

## Case #13: 自架 Bitwarden 密碼管理（NAS + RAID + 備份）

### Problem Statement
- 業務場景：敏感資料不願託管第三方，需要自架密碼管理器，要求高可用與資料可靠。
- 技術挑戰：保護資料、RAID 與備份、證書與反向代理整合。
- 影響範圍：全家密碼安全。
- 複雜度：中

### Root Cause Analysis
- 直接原因：外部雲服務信任問題。
- 深層原因：
  - 架構：缺乏高可用與備份策略。
  - 技術：容器化與儲存隔離。
  - 流程：更新/備份/復原流程未定義。

### Solution Design
- 解決策略：使用 NAS Docker 佈署 Bitwarden（或 Vaultwarden），資料卷存於 RAID1，Hyper Backup/快照週期備份，反向代理與憑證如前案。

- 實施步驟：
  1. 佈署容器，Mount 卷至 RAID1 區
  2. DSM 設定備份任務（每日/每週）
  3. Reverse Proxy + 憑證；AdGuard DNS 解析

- 關鍵程式碼/設定：
```yaml
# docker-compose.yml (Vaultwarden 輕量版)
version: "3"
services:
  vaultwarden:
    image: vaultwarden/server:latest
    container_name: vaultwarden
    ports:
      - "8080:80"
    volumes:
      - /volume1/docker/vaultwarden:/data
    environment:
      - SIGNUPS_ALLOWED=true
    restart: unless-stopped
```

- 實測：資料庫僅數十 MB；在 RAID1 + 備份下可靠度高。
- 改善幅度：資料掌控度 100%；服務中斷風險大幅降低。

Learning Points
- 知識點：自架密碼管理、RAID/備份策略。
- 練習：完成 Vaultwarden 佈署 + 憑證（2 小時）。

------------------------------------------------------------

## Case #14: 長時間 FTP 任務：FileZilla GUI in Docker + Browser VNC

### Problem Statement
- 業務場景：需在 NAS 端長時間執行 FTP Client 任務，桌機不常開機且無合適的 Web FTP 客戶端。
- 技術挑戰：以 Web 方式遠端操作 GUI FTP。
- 影響範圍：大型檔案傳輸、長任務不間斷。
- 複雜度：中

### Root Cause Analysis
- 直接原因：缺乏 Web 版 FTP client。
- 深層原因：
  - 架構：需 GUI 程式但又希望瀏覽器遠端。
  - 技術：VNC in Browser。
  - 流程：任務須在 NAS 端持續進行。

### Solution Design
- 解決策略：使用 jlesage/filezilla Docker Image（含 X11/VNC），透過瀏覽器嵌入式 VNC 控制 FileZilla。

- 實施步驟：
  1. 佈署容器並開啟 VNC Web Port（預設 5800）
  2. 掛載資料夾為上/下載目錄
  3. 瀏覽器連 http://nas:5800 即可操作

- 關鍵程式碼/設定：
```yaml
version: "3"
services:
  filezilla:
    image: jlesage/filezilla
    container_name: filezilla
    ports:
      - "5800:5800"     # Web VNC
    volumes:
      - /volume1/data/downloads:/config/downloads
      - /volume1/data/uploads:/config/uploads
    restart: unless-stopped
```

- 實測：瀏覽器即可操作 FTP GUI，NAS 端長時間任務不中斷。
- 改善幅度：省去在個人電腦長時間開機需求。

Learning Points
- 知識點：Headless GUI in Docker、VNC-over-Web。
- 練習：上傳/下載各 10GB 檔案並觀察穩定性（1-2 小時）。

------------------------------------------------------------

## Case #15: Iperf3 在 NAS 容器化 + 端到端吞吐測試流程

### Problem Statement
- 業務場景：升級 2.5G/10G 後需驗證端到端吞吐，避免用檔案傳輸受磁碟快取影響。
- 技術挑戰：提供常駐 Iperf3 Server 並標準化測試方法。
- 影響範圍：所有性能驗證與除錯。
- 複雜度：低-中

### Root Cause Analysis
- 直接原因：檔案傳輸受磁碟/快取干擾，無法反映純網路性能。
- 深層原因：
  - 架構：缺乏標準性能驗證工具常駐。
  - 技術：端點 CPU 與路徑差異。
  - 流程：測試設計不一致。

### Solution Design
- 解決策略：在 NAS 以 Docker 佈署 iperf3 server；PC 端與 UDM-Pro/USW 各組合跑 Client；紀錄結果與 CPU。

- 實施步驟：
  1. 佈署 iperf3 容器（常駐）
  2. 客戶端（PC/UDM-Pro/其他）跑 iperf3 -c 測試
  3. 記錄吞吐與 CPU，對照路徑/ACL/策略

- 關鍵程式碼/設定：
```bash
# Server on NAS
docker run -d --name iperf3 -p 5201:5201 networkstatic/iperf3 -s

# Client on PC (Windows)
iperf3.exe -c <nas_dns_or_ip> -P 4 -t 10

# Client on UDM/USW（若可）
iperf3 -c <nas_ip> -P 4 -t 10
```

- 實測（文中節選）：PC→NAS（跨 VLAN）僅 1.41 Gbps；同 VLAN 可達 2.37 Gbps；見後續兩案根因與改善。
- 改善幅度：建立可重複驗證流程，定位瓶頸更精準。

Learning Points
- 知識點：iperf3 參數、並發、CPU 影響。
- 練習：同 VLAN/跨 VLAN 路徑各自測試並比對（30 分）。

------------------------------------------------------------

## Case #16: UDM-Pro 內部架構瓶頸（8 埠 1G 交換器 vs 10G 埠）

### Problem Statement
- 業務場景：預期 8 台 1G 裝置同時存取 10G NAS 可近 8G 匯聚，但實際做不到。
- 技術挑戰：UDM-Pro 內部架構造成 8 埠 1G 與 10G 間存在 1G 瓶頸。
- 影響範圍：內網匯聚吞吐與拓樸設計。
- 複雜度：中

### Root Cause Analysis
- 直接原因：UDM-Pro 內建 8 埠交換器與路由板之間僅 1G 連結。
- 深層原因：
  - 架構：All-in-One 設計共享背板限制。
  - 技術：內部 Switch-to-Router 連線受限。
  - 流程：未採用外部專業交換器作核心。

### Solution Design
- 解決策略：以外部 L2/L3 交換器（USW-Enterprise 24 PoE）作核心，所有裝置含 NAS/PC 接入該交換器，UDM-Pro 僅作路由（uplink）。

- 實施步驟：
  1. 10G SFP+：NAS ↔ USW
  2. 2.5G：PC ↔ USW
  3. UDM-Pro ↔ USW 以 10G 上聯
  4. 內部裝置盡量不接 UDM-Pro 8 埠

- 關鍵設定：
```text
物理連線：
NAS (10G SFP+) <-> USW SFP+ #1
UDM-Pro SFP+ (LAN) <-> USW SFP+ #2
PC (2.5G) <-> USW 2.5G Port
```

- 實測：改善匯聚路徑瓶頸，為後續效能修復提供基礎。

Learning Points
- 知識點：設備內部背板/上聯瓶頸、核心-匯聚-接入層次化。
- 練習：繪製兩種拓樸（UDM 為核心 vs USW 為核心）對比吞吐預期（1 小時）。

------------------------------------------------------------

## Case #17: Threat Management L7 造成跨 VLAN 吞吐下降 → 以 L3 Switch Offload 路由

### Problem Statement
- 業務場景：PC（2.5G）跨 VLAN 存取 NAS（10G）僅 ~1.41 Gbps；同 VLAN 可達 2.37 Gbps。UDM-Pro CPU 飆高（70-85%）。
- 技術挑戰：找出瓶頸（Threat Management L7）、驗證、在不關閉防護下恢復吞吐。
- 影響範圍：跨 VLAN 檔案/服務存取效能。
- 複雜度：高

### Root Cause Analysis
- 直接原因：跨 VLAN 路徑經 UDM-Pro，Threat Management 啟用導致 L7 檢測吃 CPU。
- 深層原因：
  - 架構：跨 VLAN 預設由 Router 進行 L3。
  - 技術：L7 深度檢測成本高。
  - 流程：未在交換器上啟用 L3 SVI。

### Solution Design
- 解決策略：分兩階段驗證與修復：先暫關 Threat Management 驗證極限（確實達 9.1 G），再於 USW-Enterprise 啟用 L3（SVI）接手內網 VLAN 間路由，使跨 VLAN 路徑不再經 UDM-Pro。

- 實施步驟：
  1. 驗證：關 Threat Management（臨時）
     - 觀察 NAS→UDM-Pro 達 ~9.1 G
  2. 啟用 L3 Switch
     - 在 USW 建立各網段 SVI（VLAN 100/200…）
     - 將內網 VLAN 間路由交由 USW
     - UDM-Pro 僅作 Default Route 轉 Internet
  3. 驗證：PC↔NAS（跨 VLAN）應達 ~2.35 G（受 2.5G NIC 限制）

- 關鍵程式碼/設定（概念）：
```text
USW-Enterprise L3 (概念)
- Interface VLAN100: 192.168.100.1/24
- Interface VLAN200: 192.168.200.1/24
- Static Route (default): 0.0.0.0/0 -> UDM-Pro LAN IP
ACL：
- 允許必要跨網服務，其他限縮
```

- 實際案例與數據（節選）：
  - 改善前（UDM-Pro 路由 + Threat Mgmt ON）：~1.41 Gbps
  - Threat Mgmt OFF 測試：NAS→UDM-Pro ~9.1 G
  - L3 Switch On（Threat Mgmt 保留）：PC↔NAS（跨 VLAN）~2.35 G（受 2.5G 界面）
  - 改善幅度：1.41 → 2.35 G，約 +66.7%；且保留威脅防護。

Learning Points
- 知識點：L3 Offload、SVI、Threat Management 對效能的影響。
- 練習：
  - 基礎：在測試 VLAN 上建立 SVI（30 分）
  - 進階：完成兩 VLAN 跨網路由於交換器端（2 小時）
  - 專案：量測 Threat Mgmt ON/OFF 與 L3 On/Off 的四象限效能矩陣（8 小時）
- 風險：ACL 設錯恐開啟橫向移動；需最小授權原則。

------------------------------------------------------------

# 案例分類

1) 按難度分類
- 入門級：#3, #4, #5, #6, #14, #15
- 中級：#1, #2, #7, #8, #9, #10, #11, #12, #13
- 高級：#16, #17

2) 按技術領域分類
- 架構設計類：#1, #2, #16, #17
- 效能優化類：#15, #16, #17
- 整合開發類：#4, #12, #13, #14
- 除錯診斷類：#8, #9, #15, #17
- 安全防護類：#5, #6, #7, #11, #12, #13

3) 按學習目標分類
- 概念理解型：#1, #2, #3, #16
- 技能練習型：#4, #5, #9, #12, #14, #15
- 問題解決型：#6, #7, #8, #11, #17
- 創新應用型：#10, #13

# 案例關聯圖（學習路徑建議）

- 先學（基礎與觀念）：
  1. #1（整併思維）→ #2（VLAN 架構）→ #3（Guest/IOT）
  2. 並行學：#4（DNS Rewrite）→ #12（Reverse Proxy + SSL）

- 進階網路服務與安全：
  - #5（Teleport VPN）→ #6（Traffic Rules/家長控管）
  - #7（Dual PPPoE）→ #8（策略路由驗證）→ #9（直撥 PPPoE 測試）
  - #10（Protect 監控）→ #11（RTSP 備援錄影）

- 整合與自架應用：
  - #13（Bitwarden 自架）→ #14（FileZilla VNC in Docker）
  - #15（Iperf3 常駐與測試流程）

- 效能與架構優化（高級）：
  - #16（UDM-Pro 架構瓶頸理解）
  - #17（L3 Offload 解法）← 依賴 #2、#15
  - 完整學習路徑：#1 → #2 → #4/#12 → #5/#6 → #7/#8/#9 → #10/#11 → #13/#14 → #15 → #16 → #17

此路徑由基礎架構（整併/VLAN/DNS/代理）出發，逐步加入安全（VPN/Rules/多撥）、服務（監控/自架）、效能（iperf3/架構瓶頸/L3 offload），最後形成能獨立規劃、整合、除錯與優化的完整能力閉環。
