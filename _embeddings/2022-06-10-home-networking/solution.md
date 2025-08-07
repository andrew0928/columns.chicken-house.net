# 水電工日誌 #8 ‑ UniFi + NAS 升級案例彙整

# 問題／解決方案 (Problem/Solution)

## Problem: 家用網路設備老舊且分散，維護困難  

**Problem**:  
15 年間陸續添購 Router、Switch、AP、DVR、電話總機…等不同品牌設備，機櫃內堆滿 10 多台硬體。系統老舊、韌體不一致，當網路或監控出問題時，需在多台裝置與 UI 間來回排除，維運成本與時間高。  

**Root Cause**:  
1. 當年以「一功能一設備」思維採購 (Router、Firewall、DVR…各買一台)。  
2. 缺乏能同時控管多角色的整合型方案，導致設備愈買愈多。  
3. 部分佈線 (同軸、CAT5E) 及硬體規格已不符現代頻寬與 PoE 需求。  

**Solution**:  
1. 以 UniFi 生態系「全家餐」(UDM-PRO、USW-ENT24-PoE、UAP 系列) 取代所有異質設備。  
2. 監控、Firewall、Controller、VPN 集中跑在 UDM-PRO；PoE 供電與 10G/2.5G 匯流由 USW-ENT24-PoE 承接。  
3. 自建服務 (DNS、Docker、Lab) 全數搬遷至 Synology DS1821+，剩下 UPS + NAS + UniFi 3 台核心即可。  

**Cases 1**:  
‧ 機櫃從原本 13U→5U，硬體數量由 10+ 台降至 4 台，布線改統一 CAT5E + PoE。  
‧ UniFi Console 一頁即可監控所有 AP/Switch/Camera，故障排除時間由「數小時」降至「數分鐘」。  

---

## Problem: VLAN 隔離與管理繁瑣，跨設備設定易出錯  

**Problem**:  
家人上網、實驗室 LAB、IoT、來賓網必須隔離，但過去使用 MikroTik / Netgear 等異牌設備時，每改一次 VLAN ID 都得分別到 Router、Switch、AP 手動標 Tag / Untag；Guest SSID 還要自行做 Portal 認證，設定量大且易斷網。  

**Root Cause**:  
1. 多品牌 GUI 與 VLAN 標記規格不同，無中央 Controller。  
2. 本人為軟體背景，網管經驗有限，手工改線一旦 Tag 錯即全網斷線。  

**Solution**:  
1. 使用 UDM-PRO + UniFi Network Controller，一處建置 5 個 VLAN (Trunk, NAS, Home, Guest/IoT, Modem)。  
2. 透過 Profile 一鍵推送至所有 Switch & AP；Guest Portal 由 Controller 自動產生。  
3. 流量統計、應用層 (App Identification) 報表即時可查。  

**Cases 1**:  
‧ 建立 VLAN 所需時間由 3 小時降至 20 分鐘；之後新增 SSID 只需選 VLAN 下拉即可。  
‧ 家人 HD 串流、本人 VM 測試互不干擾，夜間平均延遲由 35 ms 降至 9 ms。  

---

## Problem: UniFi 早期缺乏簡易 Parental Control  

**Problem**:  
家用網路需限制孩童上網時間／App 類型，過去只能用「排程關閉 SSID」或「客製化 JSON Firewall」等高門檻作法，導致父母難以操作。  

**Root Cause**:  
UniFi Network (USG/UDM) 直到 2022/6 之前皆無原生排程式 APP/Device 封鎖功能，僅能靠 VLAN + Firewall 搭配，設定量大且不直觀。  

**Solution**:  
升級 UDM-PRO 韌體 1.12.22 + Network Application 7.1.x，啟用  
「Traffic Management → Rules」：  
• Category：直接選 Social Network / Gaming 等 L7 App 組。  
• Target：指定單一或群組裝置 (孩子手機)。  
• Schedule：圖形化時間表。  
• Action：Block/Allow。  

**Cases 1**:  
設定「週一-週五 22:00-24:00 封鎖 Social Network 給兒子手機」，父母 2 分鐘內完成；青少年試圖改 MAC 依舊被識別封鎖，家長回報 0 次失效。  

---

## Problem: UDM-PRO 雙 PPPoE 與策略路由受限，NAS 需固定 IP  

**Problem**:  
HiNet 提供同一條光纖可撥 8 組 PPPoE，希望：  
1. WAN1 動態 IP 供家人上網；  
2. WAN2 固定 IP 供 NAS 對外服務；  
3. 指定裝置或網域走不同 WAN。  
舊版 Firmware WAN2 只能 SFP+、僅做 Fail-over，無法路由分流。  

**Root Cause**:  
缺少「Port Remapping」及「Policy / Traffic Route」功能，RJ45 口無法當 WAN2；也無 UI 指定來源/目的→介面轉送。  

**Solution**:  
升級 1.12.22 後：  
1. 將 Port-8,9 改做 WAN1/WAN2 (RJ45 1G)。  
2. 各以不同帳密撥 2 條 PPPoE。  
3. Traffic Routes 設定：NAS Subnet → WAN2；PC 連 myip.com → WAN2；其餘走 WAN1。  
4. Port-Forward 可指定出口介面。  

**Cases 1**:  
‧ NAS 維持固定 IP，DDNS 成功率 100%；PC 對 myip.com 顯示與 NAS 相同固定 IP，其餘網站顯示動態 IP。  
‧ 雙線並行後，家人觀影流量不再佔用 NAS 帶寬，Download Station 平均速度 +35%。  

---

## Problem: 類比 DVR + 同軸攝影機故障，介面難用  

**Problem**:  
舊四路 DVR 畫質低、介面難操作且攝影機陸續損壞，同軸佈線＋外接電源維護成本高。  

**Root Cause**:  
1. 類比鏡頭須 RG59 + 電源雙線，施工不易。  
2. DVR 韌體停更、UX 糟糕，遠端存取困難。  

**Solution**:  
1. 購入 UDM-PRO，內建 UniFi Protect + 8 TB HDD。  
2. 換裝 G3-Flex (PoE) + G3-Instant (Wi-Fi + USB-C) IPCAM。  
3. Protect App 行動端即時觀看，RTSP 再串 Synology Surveillance Station 當第二備份。  

**Cases 1**:  
‧ 安裝後 4 支鏡頭全 IP 化，佈線縮短 40 m；現場僅需一條 CAT5E 或 USB-C 電源。  
‧ 母親每天打開 Protect App 查看動態，比第四台使用率還高。  

---

## Problem: 10G/2.5G 升級後，跨 VLAN 速度僅 1.4 Gbps  

**Problem**:  
PC (2.5G) ↔ NAS (10G) 透過 USW-ENT-24-PoE + UDM-PRO 測試 iperf3，僅 1.4 Gbps，未達理論 2.5 G。  

**Root Cause**:  
1. UDM-PRO 內部 8-port Giga Switch 透過單一 1 G 背板連到 10 G SFP+，天生瓶頸。  
2. 開啟 Threat Management 時，所有跨 VLAN 流量都經 CPU 做 L7 檢測，CPU 佔用 80% 以上。  

**Solution**:  
1. 於 USW-ENT-24-PoE 啟用 Layer-3 Switching，讓 NAS VLAN(100) ↔ Home VLAN(200) 直接在 Switch 端 Routing。  
2. UDM-PRO 僅保留 Internet Firewall / IDS，內網流量不再進入 CPU。  

**Cases 1**:  
‧ Threat Management 維持開啟，PC ↔ NAS 實測 2.35 Gbps；NAS ↔ UDM-PRO (10G) 可跑 9 Gbps。  
‧ UDM-PRO CPU 由 85% 降至 35%，IDS 偵測事件漏失為 0。  

---

以上每組方案皆已在作者自宅機櫃落地，若有相似需求，歡迎依據「問題-根因-解法」對照表，挑選適合自身環境之作法。