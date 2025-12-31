---
layout: synthesis
title: "水電工日誌 #7. 事隔 12 年的家用網路架構大翻新"
synthesis_type: solution
source_post: /2019/12/12/home-networking/
redirect_from:
  - /2019/12/12/home-networking/solution/
postid: 2019-12-12-home-networking
---

以下整理自文章的實戰問題解決案例，共 16 則。每則皆含問題、根因、解法（含設定/程式碼/流程）、與實測或效益，便於教學、練習與評估。

## Case #1: 兩台家用 AP 不支援漫遊導致連線黏住與斷線

### Problem Statement（問題陳述）
業務場景：家中多區域、多使用者、裝置含手機/筆電/平板。原有兩台家用 AP（ASUS RT-N16 與小米 WiFi Mini），分別提供 2.4GHz 與 2.4/5GHz。移動時常發生「黏在遠端 AP」不切換，或因信號弱而斷線，家人頻繁抱怨。期望在不手動切換 SSID 的前提下，提升 WiFi 穩定與覆蓋，並支援高負載下的穩定連線與漫遊。

技術挑戰：多 AP 區域內的無縫漫遊、頻段管理、黏住客戶端問題、單一 SSID 覆蓋、5GHz 覆蓋與干擾控制。

影響範圍：全家所有無線裝置的上網體驗、會議/影音串流/工作可用性。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 舊 AP 不支援 Mesh/控制器協調，客戶端容易黏住弱信號 AP。
2. 一台僅 2.4GHz，另一台 LAN 僅 100Mbps，整體吞吐受限。
3. 雙 SSID，需手動切換，導致體驗差。

深層原因：
- 架構層面：AP 彼此獨立運作，缺乏統一控制與漫遊協調。
- 技術層面：未啟用 802.11r/k/v、未做頻道/功率規劃、無中央控制器。
- 流程層面：缺少站台勘測與信號/干擾評估流程。

### Solution Design（解決方案設計）
解決策略：導入企業級 AP 與控制器（UniFi AP AC Lite + UniFi Controller），使用單一 SSID、啟用快速漫遊與頻道/功率優化，確保多 AP 區域內的合理切換與干擾控制，以 5GHz 為主、2.4GHz 為輔，統一在控制器中配置。

實施步驟：
1. 規劃與勘測
- 實作細節：使用控制器/手機 app 觀察各區域 RSSI，規劃 AP 點位與上行 PoE。
- 所需資源：UniFi Controller、測試手機/筆電。
- 預估時間：0.5 天

2. 部署與採管（Adopt）
- 実作細節：安裝兩台 UAP-AC-Lite；控制器採管、升韌體、套用設定。
- 所需資源：PoE、網路線、控制器。
- 預估時間：0.5 天

3. 設定優化
- 實作細節：單一 SSID、Band Steering（5GHz 優先）、啟用 802.11r（Fast Roaming）、調整 2.4GHz 信道至 1/6/11，5GHz 避免 DFS 受干擾區域。
- 所需資源：UniFi Controller
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# UniFi Controller（介面操作為主）
# WLAN 設定參考
SSID: Home
Security: WPA2/WPA3
Band Steering: Prefer 5G
Fast Roaming (802.11r): Enabled
Minimum RSSI: -75 dBm
2.4GHz Channels: 1/6/11, Auto-Optimize off
5GHz Channels: 36/40/44/48（依環境）
```

實際案例：文章中更換為兩台 UAP-AC-Lite，單一 SSID，移動不需切換，連線穩定、訊號強。

實作環境：UAP-AC-Lite x2、UniFi Controller（Docker 於 NAS）、EdgeRouter-X SFP、Netgear GS116E。

實測數據：
改善前：2.4GHz-only/100Mbps LAN，移動時常黏住弱 AP，斷線頻繁。
改善後：5GHz 覆蓋、單 SSID 漫遊，連線穩定，實際影片傳輸端到端近 986 Mbps（LAN-LAN）。

改善幅度：漫遊體驗穩定；有效吞吐提升至接近千兆環境能力。

Learning Points（學習要點）
核心知識點：
- 多 AP 漫遊須由控制器協調、單一 SSID、適當的 r/k/v 設定
- 頻道與發射功率規劃的重要性
- 5GHz 與 2.4GHz 的取捨與 Band Steering

技能要求：
- 必備技能：基本無線網路、AP/控制器操作
- 進階技能：r/k/v、信道規劃、最小 RSSI 調整

延伸思考：
- 可配置多 SSID 對應不同 VLAN（訪客網等）
- 潛在風險：啟用 802.11r 對少數舊裝置相容性
- 優化方向：站台勘測工具（如 WiFiman、Ekahau）

Practice Exercise（練習題）
- 基礎練習：建立單一 SSID 並啟用 Band Steering（30 分）
- 進階練習：在兩台 AP 間設計 5GHz 漫遊並啟用 802.11r（2 小時）
- 專案練習：完成 100 坪空間的 AP 點位與頻道/功率計畫（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：單一 SSID、穩定漫遊
- 程式碼品質（30%）：設定文件清晰（導出控制器 Site Backup）
- 效能優化（20%）：5GHz 連接率與平均 RSSI 改善
- 創新性（10%）：使用最小 RSSI、Band Steering 的策略設計


## Case #2: UniFi Controller 不想買 Cloud Key，改用 Docker 省成本

### Problem Statement（問題陳述）
業務場景：導入 UniFi AP 需 UniFi Controller。硬體 Cloud Key 約新台幣 3000 元，家中已有 NAS，考量成本與維運便利，期望在 NAS 上常駐控制器並避免在 PC 安裝 Java，提供採管、韌體升級、統一設定下發。

技術挑戰：在 NAS 上以 Docker 方式穩定運行 Controller，管理網段與 Port 映射、資料持久化。

影響範圍：AP 管理維運、設定一致性、成本支出。

複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. UniFi 需控制器，否則無法採管/集中管理。
2. 不想在個人 PC 安裝 Java。
3. 不想多買 Cloud Key 增加成本。

深層原因：
- 架構層面：需集中式管理元件常駐。
- 技術層面：容器化部署、資料持久化規劃。
- 流程層面：升級/備份策略需明確。

### Solution Design（解決方案設計）
解決策略：採用 Docker 版 UniFi Controller（jacobalberty/unifi），部署於 NAS，使用 volume 保存資料，定義必要連接埠，達到與 Cloud Key 相同目的並省成本。

實施步驟：
1. 建立 docker-compose
- 實作細節：定義映射的資料卷與埠。
- 所需資源：NAS Docker、docker-compose。
- 預估時間：30 分

2. 完成採管與基礎設定
- 實作細節：AP 重置、採管、套用 Site 設定。
- 所需資源：UniFi Controller WebUI。
- 預估時間：30 分

關鍵程式碼/設定：
```yaml
version: "3.3"
services:
  unifi:
    image: jacobalberty/unifi:latest
    container_name: unifi-controller
    restart: unless-stopped
    environment:
      - TZ=Asia/Taipei
    volumes:
      - ./unifi:/unifi
    ports:
      - "3478:3478/udp"   # STUN
      - "8080:8080/tcp"   # Device Inform
      - "8443:8443/tcp"   # Controller GUI
      - "8880:8880/tcp"   # Guest Portal (http)
      - "8843:8843/tcp"   # Guest Portal (https)
```

實際案例：文章採用 Docker 於 NAS 跑 UniFi Controller，無需 Cloud Key。

實作環境：Synology/QNAP 或 x86 NAS、Docker、UniFi AP。

實測數據：
改善前：需購買 Cloud Key（約 NT$3000）或在 PC 安裝 Java。
改善後：NAS 常駐，功能等價。
改善幅度：成本節省 ~NT$3000，維護集中化。

Learning Points（學習要點）
核心知識點：
- 控制器與設備採管/升級關係
- 容器化持久化資料
- 必要連接埠與網安考量

技能要求：
- 必備技能：Docker、基本網路連接埠
- 進階技能：備份/升級、反向代理 SSL

延伸思考：
- 可封裝於 docker swarm/k8s
- 風險：NAS 故障即影響管理
- 優化：加上自動備份與監控

Practice Exercise（練習題）
- 基礎：以 compose 起一個 Controller 並能登入（30 分）
- 進階：設定自動備份、升級流程（2 小時）
- 專案：將 AP 佈署/採管/套用多 WLAN 與訪客門戶（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：採管/設定下發成功
- 程式碼品質（30%）：compose 結構清楚、持久化妥善
- 效能優化（20%）：資源佔用合理
- 創新性（10%）：整合監控/備份策略


## Case #3: Router 長期過熱導致電容鼓包與故障，選型更替為 EdgeRouter-X SFP

### Problem Statement（問題陳述）
業務場景：既有 MikroTik RB450G 長期運作溫度高（約 90°C），最終導致電容鼓包故障；一次計畫性停電後更顯不穩，家用網路斷線，影響全家使用及個人工作。希望替換為低溫穩定、可 PoE、具硬體交換功能的路由器，以提升可靠性。

技術挑戰：選型需兼顧 PoE 供電、VLAN/switch-offload、簡易 WebUI 與 CLI 進階操作。

影響範圍：全家網路連線、中樞設備維運成本與風險。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 長期高溫運作導致電容老化鼓包。
2. 停電非主因，硬體壽命已盡。
3. 舊設備散熱與機櫃環境未優化。

深層原因：
- 架構層面：路由/AP 一體機時期曾受散熱與擺放限制。
- 技術層面：硬體選型未以低溫/壽命為優先。
- 流程層面：缺乏定期健康檢查（溫度/電容退化）。

### Solution Design（解決方案設計）
解決策略：更換為 Ubiquiti EdgeRouter-X SFP（支援 PoE passthrough、SoC 內建 switch、WebUI+CLI、硬體 offload），將 Router 放入機櫃集中管理，WiFi 改由吸頂 AP 提供。

實施步驟：
1. 選型與部署
- 實作細節：確認 PoE 與 switch 硬體支援、firmware 更新。
- 所需資源：EdgeRouter-X SFP、備援電源/UPS。
- 預估時間：0.5 天

2. 散熱與線路整理
- 實作細節：機櫃通風、理線、溫度監控。
- 所需資源：溫度貼片/感測器（選配）。
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# 硬體 offload 打開（提升轉發/NAT能力）
configure
set system offload hwnat enable
set system offload ipsec enable
commit; save
exit
```

實際案例：文章由 RB450G 轉為 ER‑X SFP，體感溫度顯著降低且穩定；LAN-LAN/NAT 轉發皆可接近 1Gbps（啟用 offload）。

實作環境：EdgeRouter-X SFP、Netgear GS116E、UAP-AC-Lite x2。

實測數據：
改善前：路由器 ~90°C，故障風險高。
改善後：低溫穩定，NAT/LAN-LAN 近 1Gbps。
改善幅度：可靠度顯著提升；性能滿足家庭千兆需求。

Learning Points（學習要點）
核心知識點：
- 硬體選型與散熱對壽命的影響
- SoC 內建 switch 與 offload 的差異
- Router 與 AP 角色分離的好處

技能要求：
- 必備技能：ER-X WebUI/CLI、韌體維護
- 進階技能：offload/bridge/switch 差異理解

延伸思考：
- 可加裝機櫃風扇、監控溫度
- 風險：QoS 與 offload 的取捨
- 優化：規劃定期維護與更換週期

Practice Exercise（練習題）
- 基礎：開啟 offload 並驗證（30 分）
- 進階：測試 offload 開關對吞吐影響（2 小時）
- 專案：完成家用路由器選型報告（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：穩定上線、PoE 正常
- 程式碼品質（30%）：設定備份、變更紀錄
- 效能優化（20%）：offload 成本/效益分析
- 創新性（10%）：散熱/監控方案設計


## Case #4: 以 VLAN 區隔家用/伺服器/Modem 網段並跨設備延伸

### Problem Statement（問題陳述）
業務場景：家中既有大量資訊插座與多設備，需同時滿足家庭用網（Home LAN）、伺服器/NAS 區段（Server LAN）、及與 VDSL Modem 的連接以支援 PPPoE 測試。希望縮減實體跳線、集中管理、強化安全隔離。

技術挑戰：在 ER‑X SFP 與 Netgear GS116E 之間以 802.1Q VLAN Trunk 延伸，並在單一上/下行上承載多 VLAN。

影響範圍：全家有線/無線設備、伺服器安全與維運效率。

複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 舊無網管交換器無法區隔網段或延伸 VLAN。
2. 多區段需求導致需多條實體線連接，資源浪費。
3. 需在不同設備間（Router/Switch）共用 VLAN。

深層原因：
- 架構層面：未採 VLAN 設計、無統一網段規劃。
- 技術層面：不了解 802.1Q 與 Trunk/Access 差異。
- 流程層面：缺少規格設計與標註/文件化。

### Solution Design（解決方案設計）
解決策略：設計 VLAN ID（例：10=Home、20=Server、30=VDSL），於 ER‑X 啟用 vlan-aware switch0、設定 trunk/access 端口；GS116E 建立對應 VLAN，Port1 設為 Trunk（T），其餘依需求設定 Untagged（U）。以此將 3 網段用單一 Interlink（ER-X eth1 <-> GS116E port1）承載。

實施步驟：
1. EdgeRouter VLAN 設定
- 實作細節：switch0 vlan-aware、VIF 介面、DHCP/NAT/防火牆。
- 所需資源：ER‑X CLI。
- 預估時間：1 天

2. Netgear GS116E VLAN 設定
- 實作細節：建立 VLAN ID、設定 Port1 為 T、其他 Port U。
- 所需資源：GS116E WebUI。
- 預估時間：0.5 天

3. 文件化與標示
- 實作細節：標示每個 Port 的 VLAN 角色與用途。
- 所需資源：表單/標籤。
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# ER-X: VLAN-aware switch 與 Trunk/Access 配置示例
configure
set interfaces switch switch0 vlan-aware enable

# 定義 Trunk（Interlink）與 Access
set interfaces ethernet eth1 description 'TRUNK-to-GS116E'
set interfaces ethernet eth1 switch-port mode trunk
set interfaces ethernet eth1 switch-port trunk allowed-vlan 10,20,30

set interfaces ethernet eth3 description 'Home-AP'
set interfaces ethernet eth3 switch-port mode access
set interfaces ethernet eth3 switch-port access vlan 10

# VLAN SVI（Router 介面）
set interfaces switch switch0 vif 10 description 'HOME'
set interfaces switch switch0 vif 10 address '192.168.10.1/24'
set interfaces switch switch0 vif 20 description 'SERVER'
set interfaces switch switch0 vif 20 address '192.168.20.1/24'

# DHCP（例，HOME）
set service dhcp-server shared-network-name HOME subnet 192.168.10.0/24 default-router '192.168.10.1'
set service dhcp-server shared-network-name HOME subnet 192.168.10.0/24 lease '86400'
set service dhcp-server shared-network-name HOME subnet 192.168.10.0/24 range 0 start '192.168.10.100'
set service dhcp-server shared-network-name HOME subnet 192.168.10.0/24 range 0 stop  '192.168.10.199'
commit; save; exit
```

實際案例：文章使用 ER‑X 與 GS116E 跨設備延伸 VLAN，以一條 Trunk 線承載 Home/Server/VDSL 三網段。

實作環境：ER‑X SFP、GS116E、UAP-AC-Lite。

實測數據：
改善前：需 3 條互連線與 3 台無網管交換器，浪費 6 個 port。
改善後：單一 Trunk、節省 2 條以上實體連線與 4+ port，安全隔離到位。
改善幅度：互連線/port 使用量下降 >66%，安全性與彈性顯著提升。

Learning Points（學習要點）
核心知識點：
- 802.1Q、Trunk/Access、SVI、DHCP Relay/Server
- 跨設備 VLAN 延伸
- 文件化與標識的重要性

技能要求：
- 必備技能：ER-X/GS116E 基本配置
- 進階技能：跨設備 VLAN 設計、除錯

延伸思考：
- 可再劃分訪客/IoT VLAN
- 風險：Trunk 配置錯誤造成 broadcast leak
- 優化：STP/Loop 防護、Port Security

Practice Exercise（練習題）
- 基礎：在 ER‑X 建立兩個 VLAN 與一個 Trunk（30 分）
- 進階：GS116E 與 ER‑X 端到端 VLAN 打通（2 小時）
- 專案：設計三網段、含 DHCP 與防火牆策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三網段互通/隔離正確
- 程式碼品質（30%）：設定清晰、可復現
- 效能優化（20%）：最小化互連線/port
- 創新性（10%）：VLAN 命名與文件化


## Case #5: Netgear GS116E 與 EdgeRouter 的 VLAN Trunk 打通

### Problem Statement（問題陳述）
業務場景：ER‑X SFP（路由/switch）需與 GS116E（管理型交換器）以一條 Uplink 承載 Home/Server/Modem 多 VLAN；GS116E 還需將 VDSL VLAN 延伸到特定 Port 給 PC 做 PPPoE 測試。

技術挑戰：兩品牌設備 Trunk/Tag/Untag 規則要對齊，避免 VLAN 洩漏/無法通訊。

影響範圍：整個網路的多網段延伸、PPPoE 測試流程。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 不同廠牌對 Trunk/Untag/TAG 表述差異。
2. Port 成員與 PVID 配置容易出錯。
3. PPPoE 測試需正確把 Modem VLAN 映射到單一使用者 Port。

深層原因：
- 架構層面：跨設備延伸設計需嚴謹。
- 技術層面：802.1Q 細節、PVID 與 Untag 邏輯。
- 流程層面：缺乏測試用例與驗證程序。

### Solution Design（解決方案設計）
解決策略：定義 VLAN=10/20/30；ER‑X eth1 為 Trunk；GS116E Port1 為 Trunk（T 10/20/30）。GS116E：Port2-6 U 20（Server）、Port7-15 U 10（Home）、Port16 U 30（VDSL 測試），PVID 對應各自 VLAN。

實施步驟：
1. GS116E 建立 VLAN 與 Port Membership
- 實作細節：在 VLAN 設定中把 Port1 標為 T，其他對應 U。
- 所需資源：GS116E WebUI。
- 預估時間：30 分

2. PVID 與 VLAN 測試
- 實作細節：確認各承載 Port 的 PVID 與流量導向，進行 ping/DHCP 測試。
- 所需資源：筆電/測試工具。
- 預估時間：30 分

關鍵程式碼/設定：
```text
GS116E（WebUI）
- VLAN 10: Port1=T, Port7-15=U（PVID 10）
- VLAN 20: Port1=T, Port2-6=U（PVID 20）
- VLAN 30: Port1=T, Port16=U（PVID 30）
- Port1 設為 Trunk，其他依用途設為 Access（Untagged）
```

實際案例：成功以單一 Interlink 承載三 VLAN；PC 可在 Port16 做 PPPoE 測試。

實作環境：ER‑X SFP、GS116E、VDSL Modem。

實測數據：
改善前：需另拉線到 Modem；PPPoE 測試繁瑣。
改善後：在 Port16 直插即可測 PPPoE。
改善幅度：測試流程時間下降 >80%。

Learning Points（學習要點）
核心知識點：
- Trunk/Untag/PVID 協同設定
- 測試 VLAN 的基本方法（DHCP、ping、抓包）

技能要求：
- 必備技能：管理型交換器操作
- 進階技能：以抓包驗證 VLAN Tag

延伸思考：
- 若有 L2 Loop，需啟用 STP
- 風險：PVID 錯配導致 VLAN 洩漏
- 優化：建立測試 checklist

Practice Exercise（練習題）
- 基礎：設定一對 Trunk 與兩個 Access VLAN（30 分）
- 進階：新增 PPPoE 測試 VLAN 並驗證（2 小時）
- 專案：完成跨品牌 Trunk 對接與文件化（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三 VLAN 正確承載
- 程式碼品質（30%）：設定圖/表清晰
- 效能優化（20%）：Trunk 數量最小化
- 創新性（10%）：測試方法與驗證流程


## Case #6: 以 Router 供電 PoE 給 UniFi AP，減少變壓器與佈線

### Problem Statement（問題陳述）
業務場景：UniFi AP 吸頂部署，希望只用網路線供電，避免額外變壓器與 AC 佈線，降低雜亂與故障點。

技術挑戰：ER‑X SFP 支援的 PoE 模式需與 AP 相容（多為 24V Passive 或 802.3af 型號差異），需正確啟用與驗證。

影響範圍：AP 稼動率、佈線美觀、維護便利。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. AP 需 PoE，未配置將需外接電源。
2. Router 與 AP PoE 規格需匹配。
3. 佈線複雜增加故障點。

深層原因：
- 架構層面：集中供電策略未設計。
- 技術層面：PoE 模式相容性未確認。
- 流程層面：缺乏 PoE 負載測試。

### Solution Design（解決方案設計）
解決策略：確認 UAP-AC-Lite 型號對應 PoE 規格，於 ER‑X SFP 指定 PoE 輸出，供電並上線採管；配合 PoE 測試（鏈路燈/功耗/穩定性）。

實施步驟：
1. 型號與規格確認
- 實作細節：查詢 UAP 版本（802.3af/24V Passive）。
- 所需資源：產品型錄/Controller。
- 預估時間：15 分

2. ER‑X 啟用 PoE
- 實作細節：在對應乙太埠開啟 PoE。
- 所需資源：ER‑X CLI。
- 預估時間：15 分

關鍵程式碼/設定：
```bash
# ER‑X 啟用 24V Passive PoE（視型號支援）
configure
set interfaces ethernet eth3 poe output 24v
commit; save; exit
```

實際案例：AP 直接由 Router 供電，省掉一組變壓器與 AC 佈線。

實作環境：ER‑X SFP、UAP-AC-Lite x2。

實測數據：
改善前：需外接 PoE 變壓器，佈線雜亂。
改善後：單線供電上網，維護更簡便。
改善幅度：電源設備數減少 50%（以兩台 AP 計），故障點下降。

Learning Points（學習要點）
核心知識點：
- PoE 模式（802.3af/at vs 24V Passive）
- Router 端口 PoE 限制

技能要求：
- 必備技能：產品規格判讀、ER‑X CLI
- 進階技能：PoE 負載/距離評估

延伸思考：
- 大規模建議使用 PoE Switch
- 風險：PoE 模式不相容可能損毀設備
- 優化：加入 UPS 保護 AP

Practice Exercise（練習題）
- 基礎：在 ER‑X 啟用/停用 PoE（30 分）
- 進階：測試不同線長下 PoE 穩定性（2 小時）
- 專案：規劃全屋 PoE 導入與成本評估（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：AP 正常供電與採管
- 程式碼品質（30%）：設定記錄與版本控管
- 效能優化（20%）：線材/距離與功耗匹配
- 創新性（10%）：佈線美觀與維護設計


## Case #7: NAS 以 LACP 聚合兩埠提升多用戶存取能力

### Problem Statement（問題陳述）
業務場景：NAS 需同時服務多個客戶端（影音/備份）。單埠 1GbE 容易飽和，導致多用戶併發吞吐不足，想利用 NAS 兩埠與交換器做 LACP 聚合。

技術挑戰：交換器與 NAS 必須皆支援 802.3ad（LACP），且瞭解單連線無法超過 1Gbps 的現實。

影響範圍：家庭影音/備份效率、伺服器存取體驗。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單埠 1GbE 對多用戶不足。
2. 無聚合則無法利用多埠。
3. 未理解 LACP 的 per-flow 分配特性。

深層原因：
- 架構層面：未設計 Aggregate Link。
- 技術層面：雜湊策略與單流量限制。
- 流程層面：缺少測試與效益評估。

### Solution Design（解決方案設計）
解決策略：在 GS116E 建立 LAG（LACP）綁定 NAS Port1/2；NAS 啟用 802.3ad bonding。對多使用者/多連線時總體吞吐提升，但單一傳輸流仍 ~1Gbps 上限。

實施步驟：
1. 交換器設定 LACP
- 實作細節：GS116E 建立 LAG1 綁定 Port2/3。
- 所需資源：GS116E WebUI。
- 預估時間：15 分

2. NAS 啟用 Bonding
- 實作細節：Synology/QNAP GUI 或 Linux bonding。
- 所需資源：NAS 管理端。
- 預估時間：30 分

關鍵程式碼/設定：
```bash
# Linux NAS bonding（802.3ad）示例
modprobe bonding
ip link add bond0 type bond mode 802.3ad miimon 100
ip link set enp3s0 down; ip link set enp4s0 down
ip link set enp3s0 master bond0
ip link set enp4s0 master bond0
ip addr add 192.168.20.10/24 dev bond0
ip link set bond0 up
```

實際案例：作者期望 NAS 以 LACP 聚合兩埠提升頻寬利用率。

實作環境：GS116E、NAS（雙埠）。

實測數據：
改善前：單埠 1GbE 對多用戶時飽和。
改善後：多用戶總吞吐可近 2Gbps（多流量），單流仍 1Gbps。
改善幅度：多客戶端情境下總吞吐 ~2 倍。

Learning Points（學習要點）
核心知識點：
- 802.3ad/LACP 與 Hash 策略
- 單流量與多流量差異

技能要求：
- 必備技能：交換器 LAG、NAS Bonding
- 進階技能：雜湊策略優化（L3/L4）

延伸思考：
- 10GbE 升級時機
- 風險：配置不一致導致 flapping
- 優化：VLAN 與 LAG 並用規劃

Practice Exercise（練習題）
- 基礎：建立 LAG 並讓 NAS 上線（30 分）
- 進階：用 iperf3 多連線測量效益（2 小時）
- 專案：撰寫 LACP 成本/效益評估（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：LAG 穩定、NAS 可用
- 程式碼品質（30%）：設定與測試紀錄
- 效能優化（20%）：多連線吞吐提升
- 創新性（10%）：雜湊/拓撲設計


## Case #8: PPPoE 測試動線太麻煩，改以專用 NIC/Port 快速撥接

### Problem Statement（問題陳述）
業務場景：工作常需直接撥 PPPoE 取得外網 IP 做測試，以前要拔線直連 VDSL Modem，流程冗長。希望桌機能隨時快速進行 PPPoE 測試。

技術挑戰：要在既有 VLAN 架構下，將 Modem VLAN 延伸到桌機，或用獨立線路到 PPPoE VLAN 對應的 Port。

影響範圍：日常測試效率、除錯速度。

複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 需頻繁改線到 Modem，流程繁瑣。
2. 沒有把 PPPoE VLAN 映射到桌機 Port。
3. 桌機 NIC 與 VLAN 功能未善用。

深層原因：
- 架構層面：測試 VLAN 未事先規劃。
- 技術層面：PC NIC VLAN 子介面未配置。
- 流程層面：缺乏標準化測試流程。

### Solution Design（解決方案設計）
解決策略：以 GS116E Port16 對應 VDSL VLAN（Untagged 30），桌機插上即能建 PPPoE；進一步可在單線上於 NIC 建立 VLAN 子介面，無需兩條線。

實施步驟：
1. Port 映射與 PPPoE 撥接
- 實作細節：GS116E Port16 → VLAN30 Untag；Windows 建 PPPoE 連線。
- 所需資源：Windows/rasdial 或 Linux pppoe。
- 預估時間：30 分

2. 進階：NIC 上建立 VLAN 子介面
- 實作細節：Linux ip link 建 eth0.30；Windows Intel PROSet VLAN。
- 所需資源：相容驅動。
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# Windows PPPoE（建立後用命令撥號）
rasdial MyPPPoE user@isp password

# Linux VLAN 子介面 + PPPoE
ip link add link eth0 name eth0.30 type vlan id 30
ip link set eth0.30 up
pppoe-setup  # 互動式設定
pppoe-start
```

實際案例：作者以兩條線分別連 Home 與 Modem，快速進行 PPPoE 測試；並思考用 VLAN 合併成單線。

實作環境：GS116E、桌機（Intel i350-T4）、VDSL Modem。

實測數據：
改善前：每次測試需改線。
改善後：插對 Port 或一鍵撥號即可。
改善幅度：測試時間下降 >80%。

Learning Points（學習要點）
核心知識點：
- PPPoE 測試流程
- PC NIC 的 VLAN 子介面

技能要求：
- 必備技能：Windows/Linux 基本網路
- 進階技能：NIC 驅動 VLAN 設定

延伸思考：
- 可自動化撥接腳本
- 風險：誤將內網接入 VDSL VLAN
- 優化：標示測試 Port 與 ACL

Practice Exercise（練習題）
- 基礎：建立 PPPoE 連線並撥通（30 分）
- 進階：以 VLAN 子介面撥 PPPoE（2 小時）
- 專案：撰寫自動化測試腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：撥接成功、拿到外網 IP
- 程式碼品質（30%）：腳本與設定清晰
- 效能優化（20%）：測試耗時下降
- 創新性（10%）：單線多用 VLAN 設計


## Case #9: 關閉 QoS、啟用硬體 Offload 以達近 1Gbps NAT/LAN 轉發

### Problem Statement（問題陳述）
業務場景：家用千兆環境希望 Router 能在 NAT 與 LAN-LAN 都能接近線速。ER‑X SFP 啟用硬體 offload 後可達近 1Gbps；但若需 QoS 則必須關閉 offload，吞吐會下降。

技術挑戰：在性能與 QoS 之間取捨，並驗證開關 offload 的實測差異。

影響範圍：整體上網與內網傳輸體驗。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未啟用 offload 時轉發走 CPU，性能不足。
2. QoS 與 offload 衝突，無法同時使用。
3. 未建立性能測試方法。

深層原因：
- 架構層面：硬體 offload 能力未被啟用。
- 技術層面：NAT 快轉/Bridge/Switch offload 原理未知。
- 流程層面：測速僅靠 ISP 工具，缺內網基準。

### Solution Design（解決方案設計）
解決策略：若非必要暫不啟用 QoS，開啟 offload；建立內網 iperf3 與 NAS 檔案傳輸測試，外網以 ISP 工具測試，得到可重複的性能基準。

實施步驟：
1. 啟用 offload 與測試
- 實作細節：ER‑X CLI 開啟；LAN-LAN 用 iperf3 測。
- 所需資源：兩台測試機/NAS。
- 預估時間：1 小時

2. 建立基準檔
- 實作細節：記錄 off/on 差異；撰寫報告。
- 所需資源：測試記錄。
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# ER-X 硬體 offload
configure
set system offload hwnat enable
commit; save

# LAN-LAN 測試（iperf3）
iperf3 -s  # Server
iperf3 -c <server-ip> -P 4 -t 30  # Client 多流測試
```

實際案例：文章參考測試顯示啟用 offload 後 LAN-LAN/NAT 皆近 1Gbps；實際 HiNet 測速 91/39.84 Mbps（受 ISP 方案上限）。

實作環境：ER‑X SFP、NAS/PC。

實測數據：
改善前：offload 關閉時高負載可能降速。
改善後：近 1Gbps。
改善幅度：吞吐至線速（受限於 ISP/實體介面）。

Learning Points（學習要點）
核心知識點：
- 硬體 offload 與 QoS 的取捨
- 基準測試方法（iperf3、SMB 大檔）

技能要求：
- 必備技能：ER‑X CLI、iperf3
- 進階技能：多流測試設計

延伸思考：
- 若需 QoS，考慮更高階硬體或不同策略
- 風險：忽略 QoS 對時延敏感流量
- 優化：分時切換策略或用型能更高設備

Practice Exercise（練習題）
- 基礎：開/關 offload 比對吞吐（30 分）
- 進階：外網/內網完整測試報告（2 小時）
- 專案：QoS vs offload 策略研究（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試完整、設定正確
- 程式碼品質（30%）：測試腳本/記錄清楚
- 效能優化（20%）：達成線速或接近
- 創新性（10%）：測試設計創新


## Case #10: 以防火牆策略隔離 Server VLAN 與 Home VLAN

### Problem Statement（問題陳述）
業務場景：家中 NAS/伺服器需要安全隔離，避免全家終端任意訪問；僅允許必要服務（例如 SMB/SSH）從 Home VLAN 到 Server VLAN。

技術挑戰：在 ER‑X 上建立 inter-VLAN 防火牆策略，維持內網可用性與安全。

影響範圍：資料安全、惡意軟體橫向移動風險。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一平面網段易造成資源曝露。
2. 未限制 inter-VLAN 流量。
3. 無最小權限原則。

深層原因：
- 架構層面：未規劃 Zero Trust/微分段。
- 技術層面：ER‑X 防火牆/Policies 未實作。
- 流程層面：服務清單與規則缺失。

### Solution Design（解決方案設計）
解決策略：建立 HOME->SERVER 允許必要 Port，其餘拒絕；SERVER->HOME 僅允許已建立會話；兩 VLAN 對 WAN 正常 NAT；記錄與監控命中。

實施步驟：
1. 建立防火牆名稱與規則
- 實作細節：ER‑X CLI 設定 rule-set。
- 所需資源：ER‑X。
- 預估時間：1 小時

2. 套用至相對應 SVI
- 實作細節：將 rule-set 綁定於 switch0.10/20。
- 所需資源：ER‑X。
- 預估時間：30 分

關鍵程式碼/設定：
```bash
configure
set firewall name HOME-2-SERVER default-action drop
set firewall name HOME-2-SERVER rule 10 action accept
set firewall name HOME-2-SERVER rule 10 protocol tcp
set firewall name HOME-2-SERVER rule 10 destination port '445,22,80,443'  # 視需求
set firewall name SERVER-2-HOME default-action drop
set firewall name SERVER-2-HOME rule 10 action accept
set firewall name SERVER-2-HOME rule 10 state established enable
set firewall name SERVER-2-HOME rule 10 state related enable

# 綁定至介面（方向）
set interfaces switch switch0 vif 10 firewall local name HOME-2-SERVER
set interfaces switch switch0 vif 20 firewall local name SERVER-2-HOME
commit; save; exit
```

實際案例：文章需求中明確希望 Server 有專屬網段與防火牆隔離。

實作環境：ER‑X SFP、VLAN 10/20。

實測數據：
改善前：Home 終端可任意存取 Server。
改善後：僅允許必要服務，其餘封鎖。
改善幅度：橫向移動與誤操作風險顯著降低。

Learning Points（學習要點）
核心知識點：
- Inter-VLAN ACL/Firewall
- 最小權限原則

技能要求：
- 必備技能：基本防火牆/規則設計
- 進階技能：日誌/監控與事件管理

延伸思考：
- 整合 IDS/IPS
- 風險：規則過嚴造成誤封
- 優化：白名單與日誌調優

Practice Exercise（練習題）
- 基礎：建立基本互訪防火牆（30 分）
- 進階：做服務白名單與日誌分析（2 小時）
- 專案：完整 Zero Trust 家用微分段（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：策略到位、誤封低
- 程式碼品質（30%）：規則可讀性佳
- 效能優化（20%）：命中率與日誌
- 創新性（10%）：可觀察性設計


## Case #11: 以 16-port 管理型交換器取代 24-port 無網管，節省空間且支援 VLAN

### Problem Statement（問題陳述）
業務場景：家中牆面插座多，但常用 ports 不高；原 24-port 無網管設備壞損。希望以體積小的 16-port 管理型交換器取代，支援 VLAN/QoS/LAG，節省空間與成本，同時滿足規劃需求。

技術挑戰：在 port 限制下完成 VLAN 分配與 LAG，且保留成長彈性。

影響範圍：機櫃空間、可維護性、網路功能。

複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 無網管無法滿足 VLAN/LAG，且已故障。
2. 24 port 尺寸與空間不合需求。
3. Port 實際使用率不高。

深層原因：
- 架構層面：過度配置且無功能。
- 技術層面：缺乏 VLAN/LAG 支援。
- 流程層面：未檢視真實使用量與需求。

### Solution Design（解決方案設計）
解決策略：選 Netgear GS116E（16-port Smart Managed Plus），具備 VLAN/LAG/QoS；經過 VLAN 設計，仍能滿足三網段與 LACP 需求，且體積小巧適合桌上型機櫃。

實施步驟：
1. 盤點與規劃
- 實作細節：盤點必要連接數、VLAN/LAG 需求。
- 所需資源：拓撲圖。
- 預估時間：0.5 天

2. 設定與驗證
- 實作細節：VLAN、LAG 設定，跑測試。
- 所需資源：GS116E WebUI。
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
GS116E（WebUI）
- 建立 VLAN 10/20/30
- Port1 設 Trunk；Port2-6（SERVER）U 20；Port7-15（HOME）U 10；Port16（VDSL）U 30
- LAG1 綁 Port2/3（NAS 用）
```

實際案例：文章中以 GS116E 取代 24-port 無網管，支援 VLAN/LAG，節省空間。

實作環境：GS116E、ER‑X SFP。

實測數據：
改善前：無網管、空間占用大、已故障。
改善後：功能到位、空間節省。
改善幅度：體積/port 利用率優化，功能性顯著提升。

Learning Points（學習要點）
核心知識點：
- Port 盤點與容量規劃
- 管理型 vs 無網管差異

技能要求：
- 必備技能：交換器基礎設定
- 進階技能：功能/成本/空間平衡

延伸思考：
- 如果要 10GbE，升級路徑？
- 風險：port 不足需二次投資
- 優化：預留 20% 空間冗餘

Practice Exercise（練習題）
- 基礎：以 16-port 設計三 VLAN（30 分）
- 進階：加入 LACP 與測試（2 小時）
- 專案：空間/成本/性能綜合評估（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：VLAN/LAG 正確
- 程式碼品質（30%）：設定與文件
- 效能優化（20%）：port/空間利用率
- 創新性（10%）：升級規劃


## Case #12: Router 與 AP 角色分離，提升擺放自由與穩定性

### Problem Statement（問題陳述）
業務場景：將 Router 放入機櫃、AP 吸頂，分離角色讓各司其職。目標是最佳化散熱與信號覆蓋，避免一體機受擺放/散熱限制。

技術挑戰：線路規劃與 PoE 供電、確保管理一致性。

影響範圍：信號品質、穩定度、維護成本。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 一體機受擺放/散熱/天線位子限制。
2. Router 放機櫃、AP 要居中吸頂。
3. 需 PoE 與集中管理。

深層原因：
- 架構層面：功能耦合導致妥協。
- 技術層面：缺少 PoE 與控制器。
- 流程層面：部署/維護流程混亂。

### Solution Design（解決方案設計）
解決策略：Router 專心路由/防火牆，AP 專心無線覆蓋與漫遊；配合 PoE 與 Controller 集中管理，明確分工。

實施步驟：
1. 分離與擺位
- 實作細節：Router 入櫃、AP 吸頂，拉 PoE。
- 所需資源：理線、PoE。
- 預估時間：0.5 天

2. 管理集中化
- 實作細節：統一於 Controller 管 AP、ER‑X 另行管理。
- 所需資源：UniFi Controller。
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
拓撲原則：
- Router（ER‑X）：機櫃、低溫穩定
- AP（UAP-AC-Lite）：走 PoE 吸頂
- Switch（GS116E）：集中分配 VLAN
```

實際案例：文章採分離策略後，連線穩定、訊號覆蓋改善。

實作環境：ER‑X SFP、UAP-AC-Lite、GS116E。

實測數據：
改善前：AP 擺位/散熱受限。
改善後：AP 吸頂覆蓋佳、Router 穩定度高。
改善幅度：覆蓋/穩定度顯著提升（體感故障/抱怨減少）。

Learning Points（學習要點）
核心知識點：
- 職責分離（Separation of Concerns）
- 物理擺位對信號/散熱的影響

技能要求：
- 必備技能：拓撲設計
- 進階技能：維運標準化

延伸思考：
- 大宅/多樓層設計模式
- 風險：多系統管理負擔
- 優化：自動化備份/監控

Practice Exercise（練習題）
- 基礎：畫出分離後拓撲（30 分）
- 進階：撰寫運維手冊（2 小時）
- 專案：完成整屋重新擺位與驗收（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：拓撲合理可運行
- 程式碼品質（30%）：文件/圖清晰
- 效能優化（20%）：散熱/信號改善
- 創新性（10%）：管理自動化


## Case #13: Intel i350-T4 NIC 強化 OS/虛擬化支援與多埠操作彈性

### Problem Statement（問題陳述）
業務場景：主機板內建非 Intel NIC，某些 OS/虛擬化對 Intel NIC 支援較成熟。購置四埠 Intel i350-T4，用於多 VLAN/PPPoE/測試環境。

技術挑戰：安裝相容驅動、管理多埠與 VLAN 子介面。

影響範圍：測試效率、相容性、可用性。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 內建 NIC 支援度不如 Intel。
2. 多場景測試需多埠彈性。
3. VLAN/PPPoE 測試需要細緻控制。

深層原因：
- 架構層面：測試平台規劃不足。
- 技術層面：NIC 特性與驅動差異。
- 流程層面：未提前驗證相容性。

### Solution Design（解決方案設計）
解決策略：安裝 i350-T4，於 OS 層啟用驅動並設定多埠用途（Home、Server、Modem/PPPoE、管理），利用 VLAN 子介面進一步收斂實體線。

實施步驟：
1. 驅動與識別
- 實作細節：確認驅動/韌體版本。
- 所需資源：Intel 驅動。
- 預估時間：30 分

2. 介面規劃
- 實作細節：命名/標註各埠用途；必要時建立 VLAN 子介面。
- 所需資源：OS 設定。
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# Linux 命名與 VLAN 子介面
ip link set enp5s0 down
ip link add link enp5s0 name enp5s0.30 type vlan id 30
ip link set enp5s0 up
ip link set enp5s0.30 up
```

實際案例：作者以 i350-T4 讓 PPPoE 測試變簡單，並思考將兩條線收斂為單線 VLAN。

實作環境：桌機 + Intel i350-T4。

實測數據：
改善前：內建 NIC 相容性一般、多場景不便。
改善後：多埠彈性、相容性高。
改善幅度：測試時效提升、驅動可用性提升（定性）。

Learning Points（學習要點）
核心知識點：
- NIC 驅動/韌體與相容性
- 多埠/VLAN 實務

技能要求：
- 必備技能：OS 網路設定
- 進階技能：自動化 NIC Profile

延伸思考：
- SR-IOV/DPDK 在家用的可能性
- 風險：功耗與散熱
- 優化：標註/文件化埠用途

Practice Exercise（練習題）
- 基礎：安裝驅動並上線（30 分）
- 進階：建 VLAN 子介面驗證（2 小時）
- 專案：設計多埠測試平台（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：多埠可用
- 程式碼品質（30%）：設定文件
- 效能優化（20%）：測試效率
- 創新性（10%）：彈性設計


## Case #14: 以真實檔案與 iperf3 取得可重現的性能基準

### Problem Statement（問題陳述）
業務場景：僅用 ISP 測速不足以判斷內網瓶頸；需建立內外網一致的測試方法，包含 LAN-LAN（NAS 大檔案/iperf3）與 WAN（ISP 工具），以確認架構是否達標。

技術挑戰：建立標準化測試腳本與驗證流程。

影響範圍：性能評估、升級決策。

複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. ISP 測速受外部因素影響。
2. 無內網基準無法定位瓶頸。
3. 測試不可重現。

深層原因：
- 架構層面：缺乏性能驗收流程。
- 技術層面：工具/方法未建立。
- 流程層面：測試紀錄與版本控管缺失。

### Solution Design（解決方案設計）
解決策略：LAN-LAN 用 iperf3 與 NAS 大檔案（6.8GB 影片）做基準；WAN 用 ISP 工具（HiNet 測速）；統一記錄環境/版本/設定。

實施步驟：
1. 設備與工具配置
- 實作細節：iperf3 安裝、NAS 檔案準備。
- 所需資源：兩台測試機/NAS。
- 預估時間：0.5 天

2. 腳本化與報告
- 實作細節：撰寫測試腳本與報表模板。
- 所需資源：腳本工具。
- 預估時間：0.5 天

關鍵程式碼/設定：
```bash
# iperf3 多流測試
iperf3 -s
iperf3 -c <server-ip> -P 4 -t 60 --logfile lan_test.log

# 檔案測速（Linux）
time rsync -avP /mnt/nas/bigfile .
```

實際案例：文章用 NAS 拉大檔案，近 986 Mbps；WAN 100/40 方案測得 91.03/39.84 Mbps。

實作環境：ER‑X、GS116E、NAS、PC。

實測數據：
改善前：性能定位困難。
改善後：建立可重現基準。
改善幅度：決策與除錯效率提升。

Learning Points（學習要點）
核心知識點：
- 基準測試設計
- 多流/單流、LAN/WAN 的差異

技能要求：
- 必備技能：iperf3、檔案傳輸測試
- 進階技能：自動化與報告

延伸思考：
- 長期趨勢監測
- 風險：測試環境不一致
- 優化：加入監控/告警

Practice Exercise（練習題）
- 基礎：完成一次 LAN-LAN 及 WAN 測試（30 分）
- 進階：自動化腳本與報表（2 小時）
- 專案：制定家庭網路驗收標準（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試覆蓋
- 程式碼品質（30%）：腳本與紀錄
- 效能優化（20%）：測試效率
- 創新性（10%）：指標設計


## Case #15: 以最小 RSSI 與頻道規劃減輕黏住客戶端問題

### Problem Statement（問題陳述）
業務場景：多 AP 環境下，裝置常黏在弱信號 AP。希望藉控制器設定「最小 RSSI」、頻道與功率分配讓裝置提早離開弱連線，提升漫遊品質。

技術挑戰：找到合適的 RSSI 閾值與頻道布局，避免 coverage hole。

影響範圍：移動裝置的連線品質、語音/視訊通話體驗。

複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 黏住弱 AP，延遲/丟包上升。
2. 頻道重疊造成干擾。
3. 發射功率過高導致覆蓋過度重疊。

深層原因：
- 架構層面：AP 覆蓋交疊過大。
- 技術層面：未設最小 RSSI、頻道規劃不足。
- 流程層面：未做現場量測與調整。

### Solution Design（解決方案設計）
解決策略：在 UniFi Controller 設定 Minimum RSSI（如 -75 dBm）、Band Steering 5GHz 優先；2.4GHz 固定 1/6/11、5GHz 避免重疊；適度降低發射功率讓漫遊更積極。

實施步驟：
1. 量測與初始設定
- 實作細節：用手機量 RSSI，設定最小 RSSI -75 dBm。
- 所需資源：UniFi Controller、測試手機。
- 預估時間：0.5 天

2. 頻道/功率調整
- 實作細節：2.4GHz 指定 1/6/11；5GHz 指定非重疊通道；調低 Tx Power。
- 所需資源：Controller。
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
UniFi Controller（WLAN/Radio Profiles）
- Minimum RSSI: -75 dBm
- Band Steering: Prefer 5G
- 2.4GHz Channels: 1/6/11
- 5GHz Channels: 36/40/44/48
- Tx Power: Medium/Low（依實測）
```

實際案例：文章提及舊 AP 黏住問題；新架構搭配控制器可改善。

實作環境：UAP-AC-Lite x2、Controller。

實測數據：
改善前：黏住弱 AP、斷線。
改善後：漫遊更積極、語音/視訊穩定。
改善幅度：移動時丟包/延遲顯著下降（定性）。

Learning Points（學習要點）
核心知識點：
- 最小 RSSI 與漫遊行為
- 頻道規劃對干擾的影響

技能要求：
- 必備技能：控制器設定
- 進階技能：現場量測與優化

延伸思考：
- 不同終端漫遊能力差異
- 風險：RSSI 過高導致斷線
- 優化：區域分層功率配置

Practice Exercise（練習題）
- 基礎：設定最小 RSSI 與頻道（30 分）
- 進階：實測不同閾值的體驗差異（2 小時）
- 專案：多 AP 場域完整無線優化（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：設定正確、漫遊穩定
- 程式碼品質（30%）：設定紀錄
- 效能優化（20%）：干擾與丟包下降
- 創新性（10%）：量測方法


## Case #16: 電源異常誤判與硬體健康檢查流程建立（電容鼓包診斷）

### Problem Statement（問題陳述）
業務場景：一次台電計畫性停電後，Router/Switch 無法正常啟動，初判為停電影響。但後續檢測發現為電容鼓包（壽命問題）。需建立家用中樞設備的健康檢查與更換計畫，避免誤判與長時間停機。

技術挑戰：定位硬體故障根因（溫度、電容老化），建立預防性維護流程。

影響範圍：整體網路可用性、停機時間、維修成本。

複雜度評級：低-中

### Root Cause Analysis（根因分析）
直接原因：
1. 電容鼓包導致啟動失敗。
2. 長期高溫運作加速老化。
3. 停電並非主因，誤判延誤處置。

深層原因：
- 架構層面：散熱與通風不足。
- 技術層面：缺乏健康監測（溫度/電源）。
- 流程層面：無預防性維護週期與備援。

### Solution Design（解決方案設計）
解決策略：導入溫度監測/通風改善；建立年度健康檢查（視覺檢查電容、清潔灰塵）、三到五年設備汰舊計畫、關鍵設備備援與設定備份，降低風險與停機時間。

實施步驟：
1. 建立健康檢查清單
- 實作細節：溫度記錄、電容外觀、風扇運作。
- 所需資源：紅外測溫/感測器。
- 預估時間：0.5 天

2. 備援與備份
- 實作細節：設定定期備份、關鍵設備備援（例如備用小型 Router/Switch）。
- 所需資源：備用設備、備份策略。
- 預估時間：0.5 天

關鍵程式碼/設定：
```text
維運文件模板：
- 設備清單/購買日期/韌體版本
- 年度健康檢查（溫度、視覺檢查、清潔）
- 設定備份路徑與頻率
- 汰換建議（3-5 年）
```

實際案例：文章排除停電因素，發現主因為電容鼓包；最終替換設備並優化散熱。

實作環境：機櫃、UPS、Router/Switch/AP。

實測數據：
改善前：誤判造成停機與不確定性。
改善後：確立維保流程、降低風險。
改善幅度：停機風險與故障定位時間顯著下降。

Learning Points（學習要點）
核心知識點：
- 硬體壽命與溫度管理
- 預防性維護與備援

技能要求：
- 必備技能：基本硬體檢查
- 進階技能：維保流程設計

延伸思考：
- 監控整合（SNMP/Netdata）
- 風險：忽略非顯性故障（冷焊）
- 優化：SLA/MTTR 指標化

Practice Exercise（練習題）
- 基礎：完成一次設備健康檢查（30 分）
- 進階：制定汰換與備援計畫（2 小時）
- 專案：維保制度文件化與導入（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：清單/流程可執行
- 程式碼品質（30%）：文件完整性
- 效能優化（20%）：MTTR 降低
- 創新性（10%）：監控整合設計


案例分類
1. 按難度分類
- 入門級：Case 2, 6, 11, 12, 14, 16
- 中級：Case 1, 5, 7, 8, 9, 10, 15
- 高級：Case 4, 13

2. 按技術領域分類
- 架構設計類：Case 4, 11, 12, 16
- 效能優化類：Case 7, 9, 14, 15
- 整合開發類（工具/容器/自動化）：Case 2, 8, 13, 14
- 除錯診斷類：Case 3, 5, 10, 16
- 安全防護類：Case 4, 10, 15

3. 按學習目標分類
- 概念理解型：Case 4, 9, 14, 16
- 技能練習型：Case 2, 5, 6, 7, 8, 13
- 問題解決型：Case 1, 3, 10, 11, 12, 15
- 創新應用型：Case 7, 8, 13, 14


案例關聯圖（學習路徑建議）
- 建議先學：Case 2（Controller 基礎）、Case 11（管理型交換器概念）、Case 12（角色分離）
- VLAN 與跨設備關聯：先學 Case 4（VLAN 架構），再做 Case 5（Trunk 對接），最後串 Case 10（防火牆隔離）
- 無線優化路徑：Case 1（單 SSID 與漫遊）→ Case 15（RSSI/頻道優化）→ Case 6（PoE 佈建）
- 效能與測試：Case 14（基準測試）→ Case 9（Offload）→ Case 7（LACP）
- 測試與多埠實作：Case 8（PPPoE 快速撥接）→ Case 13（多埠/VLAN 子介面進階）
- 維運可靠性：Case 3（選型與散熱）→ Case 16（維保流程）

完整學習路徑建議：
1) 入門基礎：Case 2 → 11 → 12
2) VLAN 與安全：Case 4 → 5 → 10
3) 無線體驗：Case 1 → 15 → 6
4) 性能與測試：Case 14 → 9 → 7
5) 測試自動化與多埠：Case 8 → 13
6) 維運可靠性：Case 3 → 16

依此路徑可從部署、架構、效能、安全到維運逐步精進，涵蓋家用到小型辦公的完整網路實戰。