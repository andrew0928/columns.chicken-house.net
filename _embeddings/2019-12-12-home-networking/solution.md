# 水電工日誌 #7. 事隔 12 年的家用網路架構大翻新

# 問題／解決方案 (Problem/Solution)

## Problem: 家中 Wi-Fi 連線不穩、漫遊體驗差

**Problem**:  
家中出現以下困擾：  
1. 走到不同空間需要手動切換 SSID，否則會黏在訊號弱的 AP。  
2. RT-N16 僅支援 2.4 GHz；小米 Wi-Fi Mini 雖有 5 GHz 但僅 100 Mbps LAN，且兩台皆無 Mesh 或企業級漫遊機制。  
3. 家人一旦 Wi-Fi 斷線就會抱怨，維運成本高。

**Root Cause**:  
• 既有設備規格落後（僅單頻、無 802.11ac、無 802.11r/k/v 漫遊）。  
• LAN 介面速率與無線能力不對等，導致瓶頸與頻繁斷線。  
• 無集中管理，設定分散、難以最佳化。

**Solution**:  
• 汰換為 2 台 UniFi AP AC-Lite，採 PoE 吸頂安裝。  
• 於 NAS 內利用 Docker 部署 UniFi Controller，集中配置 SSID、頻道、功率與漫遊參數。  
• 全屋僅保留單一 SSID，讓裝置自動在多顆 AP 間快速漫遊。  

```bash
# 範例：在 UniFi Controller 中啟用 802.11r
wireless:
  wlan:
    - name: "HomeWiFi"
      ft_psk: true        # 快速漫遊
      bandsteering: "on"
```

**Cases 1**:  
• 部署後全屋平均 RSSI 提升 ~15 dB，手機影音播放無卡頓。  
• 家人從未再回報「為何不能連線」；日常維運量體感下降 >80%。

**Cases 2**:  
• 來訪朋友以單一 SSID 即可在客廳、書房、房間自由移動，VoIP 通話 30 分鐘無中斷。  

---

## Problem: 舊路由器／Switch 高溫故障、缺乏 PoE 與管理功能

**Problem**:  
1. MikroTik RB450G 長期運作溫度達 90 °C，電容鼓裂後整機故障。  
2. Belkin 24-port 無網管 Switch 無法 VLAN、LACP，且電容老化無法開機。  
3. 原系統不支援 PoE，UniFi AP 得額外插變壓器，走線混亂。

**Root Cause**:  
• 早期家用產品散熱設計差，高溫導致電容壽命嚴重縮短。  
• 無網管 Switch 缺乏 Layer-2 功能，難以隔離 NAS/IoT/MOD 流量。  
• PoE 需求被忽略，導致供電與訊號分離、布線複雜。

**Solution**:  
• Router 換成 Ubiquiti EdgeRouter-X SFP：  
  – 提供 24 V PoE-out；SoC 內建 5-port Hardware Switch 便於 VLAN。  
  – 低功耗無風扇，機身溫度常態 <45 °C。  
• Switch 換成 NETGEAR GS116E (16 port Smart Managed)：  
  – 支援 VLAN、QoS、LACP，體積小可置於機櫃。  
• 關鍵 AP 直接由 EdgeRouter 提供 PoE，一條網線完成資料與供電。

```bash
# EdgeRouter CLI：啟用 PoE 並指定 Port 為 Trunk
set interfaces ethernet eth0 description 'VLAN-Trunk'
set interfaces ethernet eth0 poe output 24v
set interfaces ethernet eth0 vif 10
set interfaces ethernet eth0 vif 20
commit ; save
```

**Cases 1**:  
• Router／Switch 長時間全速運作，機殼表面溫度約 40 °C；半年無任何當機紀錄。  
• 移除 2 顆 AC 變壓器，機櫃配線縮減 30 %，易於整理與散熱。

---

## Problem: 三網段需求但實體 Port 有限，手動跳線低效

**Problem**:  
需要同時滿足：  
1. Server LAN（NAS/VM 等需獨立防火牆）。  
2. Home LAN（一般裝置）。  
3. VDSL/PPPoE 測試端口。  
若用傳統 Switch，需 3 台獨立設備與 6 條跳線，成本及空間皆過高。

**Root Cause**:  
• 未採用 VLAN，導致「一網段一 Switch」的僵硬架構。  
• Router 與 Switch 若不能穿透 Tag，跨設備無法共享 Trunk Port。  
• 自身對 VLAN 概念不足，難以一次規劃完成。

**Solution**:  
• 使用 EdgeRouter-X SFP 內建 Hardware Switch 功能 + GS116E Smart Switch：  
  – 設定 VLAN 10(Server)、20(Home)、30(VDSL)。  
  – eth0 <-> GS116E-port1 做 Tag-Trunk，一條線傳 3 個 VLAN。  
  – 其餘實體 Port 視需求指定 Access 或 Trunk。  
• NAS 透過 LACP (802.3ad) 綁定 2 Port，跨 VLAN 傳輸 2 Gbps。  

```bash
# Router 端建立三個 VLAN 子介面
set interfaces switch switch0 vif 10 description 'ServerLAN'
set interfaces switch switch0 vif 20 description 'HomeLAN'
set interfaces switch switch0 vif 30 description 'VDSL'
# Switch 端 (GS116E) 使用 WebUI 指 map: port1=Trunk(10,20,30)，其餘依需求 Access
```

**Cases 1**:  
• 原需 3 台 Switch → 精簡為 1 台；Patch-cord 從 6 條降至 1 條 Trunk。  
• NAS 透過 LACP 讀寫大型檔案可達 180 MB/s，家用電腦同時存取不掉速。  
• PPPoE 測試僅需將 PC Port 指定 VLAN 30，秒級完成撥號測試。

---

## Problem: 虛擬化環境需多 Port NIC，主機板內建網卡驅動支援度差

**Problem**:  
新裝的 X570 主機板內建非 Intel NIC，於 ESXi / Proxmox 內驅動不完整，  
缺 VLAN Tag 與 SR-IOV 等功能，影響開發與測試工作。

**Root Cause**:  
• Realtek/Marvel 等 NIC 在伺服器或虛擬化 OS 上原生驅動缺功能。  
• 需多埠網卡做 Lab 測試（PPPoE、Trunk、隔離網段），單 Port 無法滿足。

**Solution**:  
• 添購 Intel i350-T4 伺服器級 4-port GbE 網卡：  
  – 全平台原生驅動；支援 VLAN Tagging、Teaming、SR-IOV。  
  – 每 Port 可獨立對應不同 VLAN，或匯聚作 LACP。

```bash
# Linux 啟用四個 VLAN 子介面
ip link add link eno3 name eno3.10 type vlan id 10
ip link add link eno3 name eno3.20 type vlan id 20
ip link add link eno3 name eno3.30 type vlan id 30
ip link set dev eno3 up
ip addr add 192.168.10.2/24 dev eno3.10
```

**Cases 1**:  
• 在 Proxmox 中直通一埠給 pfSense VM，另一埠給 ESXi Lab，實現多環境同時運行。  
• PPPoE 撥號／LACP 聚合等測試作業，改為 GUI 內切換，工時縮短 >50%。

---

## Problem: 需驗證新架構效能，擔心 NAT 與 SFP 介面成瓶頸

**Problem**:  
更換設備後必須確認：  
1. LAN ↔ LAN 誤封包或 CPU Bottleneck。  
2. LAN ↔ WAN 經 NAT 仍可跑滿 100/40 Mbps HiNet。  

**Root Cause**:  
• 未啟用 Hardware Offload 時 EdgeRouter 會走 CPU，可能塞爆。  
• Router/Switch 錯誤的 MTU 或 LACP 設定亦可能拖慢速度。

**Solution**:  
• 於 EdgeRouter CLI 啟用 hardware-offload；並在 UniFi Controller 調校 MTU=1500。  
• 使用 6.8 GB 影片檔由 NAS → PC 測試；再以 HiNet SpeedTest 驗證 NAT。  

**Cases 1**:  
• LAN ↔ LAN 實測 986 Mbps（約線速極限），CPU 使用率 <10%。  
• 經 NAT 上網 91/39 Mbps，符合 ISP 100/40 訂閱方案。  
• 研判未來升級 1 Gbps 光世代仍有餘裕；QoS 需求可斟酌是否關閉 Offload。

---

以上為本次「家用網路大翻新」過程中，實際遭遇的每一項問題、成因分析、對應解決手法及最終成效。希望能成為日後規劃中小型網路環境、或想入門 VLAN／PoE／多埠 NIC 的讀者參考。