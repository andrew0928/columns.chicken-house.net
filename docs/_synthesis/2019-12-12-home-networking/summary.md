---
layout: synthesis
title: "水電工日誌 #7. 事隔 12 年的家用網路架構大翻新"
synthesis_type: summary
source_post: /2019/12/12/home-networking/
redirect_from:
  - /2019/12/12/home-networking/summary/
---

# 水電工日誌 #7. 事隔 12 年的家用網路架構大翻新

## 摘要提示
- 停電導火線: 設備實際故障主因是老化與電容鼓起，停電只是契機促成全面更新。
- WiFi 升級: 以兩台 UniFi AP AC Lite 取代舊 AP，統一 SSID、支援漫遊與 PoE，改善覆蓋與穩定性。
- 控制平台: 以 UniFi Controller（Docker 版）集中管理 AP，免買 Cloud Key、維運更彈性。
- 路由器選型: 改用 Ubiquiti EdgeRouter-X SFP，重視低溫、PoE、硬體交換功能與易用 WebUI。
- 交換器升級: 換 Netgear GS116E 智能型交換器，引入 VLAN/QoS/LAG，取代無網管設備。
- VLAN 架構: 以多 VLAN 分隔家庭網、伺服器網與寬頻接入，提升安全性與彈性。
- LACP 與測試: NAS 使用 LACP，PC 可直接 PPPoE 測試對外 IP，提升實驗與維運效率。
- 效能驗證: LAN-LAN 近線速、WAN 端受 ISP 上限限制；硬體 offloading 可達近 1Gbps。
- 架構哲學: 從網管規則（VLAN、路由、Firewall）得到 rule engine 設計靈感。
- 維運心得: 以設備分工（Router 入櫃、AP 吸頂）、VLAN 精簡配線，達成可靠與易管理的家庭網。

## 全文重點
作者在家中重裝網路設備，起因於一次停電後路由與交換器相繼掛點，進一步檢視才知是長年老化導致電容鼓起。趁雙十一更新，目標集中在兩件事：徹底解決 WiFi 覆蓋/漫遊不佳與不穩問題，以及重整路由與交換的基礎架構。WiFi 採用兩台企業級 UniFi AP AC Lite，依賴 UniFi Controller 做統一管理與設定，透過 PoE 與吸頂部署改善訊號與可用性；Controller 則以 Docker 架設於 NAS 上，節省成本並避免在 PC 上安裝 Java。

路由器選擇 Ubiquiti EdgeRouter-X SFP，原因在於低溫、PoE 供電支援、硬體交換（內建 SoC 5 port switch）以及尚可的 WebUI；雖與 UniFi 產品線分離、無法被 Controller 管理，但功能與穩定性符合需求。交換器改採 Netgear GS116E（簡易網管型16埠），以支援 VLAN、QoS、LAG 等功能，取代舊 Belkin 24 埠無網管機，從根本上解決 MOD、NAS 隔離與多網段需求，並以 VLAN 精簡跨設備連線。另番外購入 Intel i350-T4 四埠 NIC 以求更佳的驅動相容性、虛擬化/伺服器用途支援，也利於進行 PPPoE 測試與多場景實驗。

整體網路規劃將家庭 LAN、伺服器 LAN 與 VDSL 接入分為不同 VLAN，並在 EdgeRouter 與 Netgear 之間以 Trunk 將多 VLAN 穿越單一上行連結，符合「AP 直掛 PoE」「關鍵線路直接 Router」「NAS 可 LACP」「PC 可就地 PPPoE」等目標。最終部署完成後，LAN-to-LAN 檔案傳輸逼近 1Gbps 實體上限，WAN 速度則受 ISP 100/40 方案所限；若啟用硬體 offloading，EdgeRouter 能在 LAN/WAN 兩端維持近滿速。作者並由網管抽象（VLAN tag、Routing table、Firewall policy 與優先序）得到設計啟發：以規則與優先級取代硬編邏輯與繁雜開關，強化系統對複雜需求的適應性。整體翻新雖耗時近一月，但以設備分工、集中管理與 VLAN 化配線，為家用網路帶來穩定、可維護與可擴充的長期價值。

## 段落重點
### 前言與動機
作者自 12 年前家裡整修完成後，幾乎未再動過網路架構；一次計畫性停電後路由與交換器相繼掛點，雖有 UPS 並事先關機，但實際故障主因是設備老化與電容鼓起。舊路由短暫被維修起死回生後仍再度故障，促使作者順勢在雙十一前後全面翻新。此次更新的兩大目的：一是解決長期 WiFi 連線品質差、漫遊不順與覆蓋問題；二是重新規劃路由與交換架構，使網段分流、安全隔離與維運測試更便利。回顧 12 年前以自架 NAT server、設備能跑就好為方針的時代，現今需求已升級到更高的穩定度、可擴展性與集中管理能力，這也成為本次架構更新的主軸。

### 敗家有理 #1, UniFi AP
WiFi 是全家體感最強的項目。舊設備為 ASUS RT-N16 與小米 WiFi Mini，存在僅 2.4GHz、LAN 只有 100Mbps、無 Mesh 與 SSID 不易漫遊等痛點。作者一次購入兩台 UniFi AP AC Lite，主打企業級多 AP 統一 SSID 漫遊、吸頂式設計與 PoE 供電，並由 UniFi Controller 統一管理，部署設定僅需少量操作即可下發至所有 AP。為節省成本且提高維運彈性，Controller 以 Docker 方式裝在 NAS 上，免購 Cloud Key 也避免在 PC 安裝 Java。這套組合提供穩定訊號、管理一致與部署便利，實現了「用過就回不去」的體驗。

### 敗家有理 #2, Router + Switch
作者長期將路由與 WiFi 分工：路由器入機櫃負責穩定與性能，AP 則置頂求覆蓋。本次選擇 Ubiquiti EdgeRouter-X SFP 作為路由，原因包括：支援 PoE 方便直供 UniFi AP、運作低溫避免再度「電容爆」、WebUI 較合胃口且具硬體交換（SoC 內建 5 埠 switch），利於 VLAN 彈性配置。雖然 EdgeRouter 不受 UniFi Controller 管理，但可接受。交換器改為 Netgear GS116E 智能網管型，支援 VLAN/QoS/LAGP，取代舊 Belkin 24 埠無網管機，從根本上實現網段隔離和關鍵連線的簡化。考量家用實際埠數、空間與散熱，改採 16 埠桌上型放機櫃，兼顧擴充與精巧。

### 敗家有理 #3, (亂入) Intel i350-T4
因新主機板內建非 Intel NIC，為了在多作業系統、伺服器與虛擬化場景獲得更佳驅動相容性與穩定性，作者另購 Intel i350-T4 四埠伺服器級網卡。多埠設計讓日常測試更靈活，例如可同時接家庭 LAN 與 Modem LAN，以 PPPoE 直撥取得對外 IP 進行測試；也為未來 LACP、VLAN Tagging、虛擬交換與容錯設計預留彈性。這筆「亂入」升級，強化了桌機作為測試/開發/驗證平台的角色。

### 網路規劃 - 切割 VLAN
此段為整體翻新的核心。需求包含：伺服器/NAS 獨立網段與防火牆隔離、AP 需 PoE 直供、關鍵線路直上路由、PC 就地 PPPoE 測試、NAS 以 LACP 提升吞吐。關鍵挑戰在於多 VLAN 橫跨路由與交換器，多設備間需以 Trunk 精簡連線。EdgeRouter-X SFP 內建硬體 switch，能在路由側靈活定義 per-port VLAN，搭配 Netgear GS116E 的 VLAN 設定，將家庭 LAN、伺服器 LAN 與 VDSL 接入三網分層，再以單一上行連結承載多 VLAN，避免多台無網管 switch 所需的冗餘連線與埠浪費。UniFi AP 因 PoE 需求直掛路由，其他設備依角色接入交換器。最終達成：安全隔離、彈性調度、配線精簡與維運便利。作者附上參考教學資源，建議新手從 VLAN 基礎觀念與 802.1Q 實作切入。

### 實測效能
作者以 NAS 大檔案傳輸驗證 LAN-LAN 性能，經路由轉發（無 NAT）達約 986 Mbps，逼近千兆上限；經 NAT 走 ISP 測速則受 100/40 方案限制，實測約 91/40 Mbps。參考外部測評顯示，若啟用 EdgeRouter 硬體 offloading，不論 LAN to LAN 或 LAN to WAN 皆可接近 1Gbps 滿速，但若需 QoS 則需關閉 offloading。綜合而言，現階段架構的性能與可靠性已大幅超過家用需求，有餘裕支撐未來增添服務與裝置。

### 後記
本次翻新歷時近一月，從選型、部署到 VLAN 規劃均具挑戰；然而以設備分工（Router 入櫃、AP 吸頂）、集中管理（Controller on NAS）與 VLAN 化配線，最終達到穩定、可維護與可擴充的家用網。作者雖自認非網管專業，卻從網路設備的規則化思維獲得軟體設計啟發：透過可組合的 rules、priority 與 policy，將複雜需求收斂為可配置的領域知識，提升系統適應力與可維護性。這份從網管到軟體的跨域靈感，亦將延伸至 rule engine 的實務應用。

## 資訊整理

### 知識架構圖
1. 前置知識
   - 基礎網路概念：LAN/WAN、IP 與子網、NAT、PPPoE
   - 無線網路：2.4/5GHz、SSID 與漫遊、Mesh 與 Controller 的差異
   - VLAN 與 802.1Q：Tagged/Untagged、Trunk/Access 介面
   - 交換器與路由器：L2/L3 差異、硬體 offloading、基本防火牆規則
   - 進階：PoE 供電、LACP（鏈路聚合）、Docker 基礎（於 NAS 安裝服務）

2. 核心概念（3-5 個）及其關係
   - 角色分離：AP 與 Router 分離部署，AP 放最佳收訊點、Router 置於機櫃，提升穩定與維護性
   - Controller-based WiFi：UniFi AP + Controller 形成單一 SSID 無縫漫遊，集中管理設定與監控
   - VLAN 切割與跨設備 Trunk：以 802.1Q 在 Router 與 Managed Switch 之間建立 Trunk，彈性分配各 VLAN 的 Access port
   - PoE 與佈線簡化：以 Router 的 PoE 直供 AP，減少變壓器與電源佈線
   - 效能與可靠性：硬體 offloading、LACP 擴充 NAS 吞吐、溫度與壽命（電容）管理

3. 技術依賴
   - UniFi AP AC Lite 需 UniFi Controller（軟體或 Cloud Key）；文中以 Docker 於 NAS 部署 Controller
   - EdgeRouter X SFP（MediaTek SoC）內建 5 埠硬體 switch，可做 per-port VLAN 與 PoE 給 AP
   - Netgear GS116E（簡易網管）提供 VLAN/QoS/LAG（LACP）以配合 Router 進行跨設備 VLAN
   - Intel i350-T4 NIC 支援多埠、VLAN Tag/LACP，利於 PC/Server 測試與聚合
   - VDSL Modem + PPPoE 路徑，用於直接對外測試與撥接

4. 應用場景
   - 家用/小型辦公室多 AP 無縫漫遊（單 SSID）
   - 以 VLAN 隔離 Server/NAS、家用網段、寬頻/Modem 管理網段
   - PC 直連 PPPoE 進行網路測試與疑難排解
   - 以 LACP 提升 NAS 匯流排頻寬，改善多客戶端併發吞吐
   - 透過 PoE 與 VLAN Trunk 減少配線、集中管理、提升可擴充性

### 學習路徑建議
1. 入門者路徑
   - 釐清需求與畫出拓樸草圖（設備、房型、拉線）
   - 學會 VLAN 基礎（Tagged/Untagged、Trunk/Access）
   - 選擇分離式架構：獨立 Router + UniFi AP，建立單一 SSID
   - 在 NAS 上用 Docker 部署 UniFi Controller，完成 AP 佈署與基礎監控

2. 進階者路徑
   - 在 EdgeRouter X SFP 設定 per-port VLAN、Inter-VLAN Routing 與基本防火牆
   - 於 GS116E 配置 VLAN、設定與 Router 的 Trunk，規劃各房間/設備的 Access port
   - 佈建 PoE 供電給 AP、優化 AP 位置與功率
   - 啟用 LACP（NAS + Switch），規劃多客戶端的吞吐資源

3. 實戰路徑
   - 制定實體配線與 Port Mapping（標籤化）、完成跨設備 Trunk 連結
   - 驗證：AP 漫遊、VLAN 隔離/互通、防火牆規則、PPPoE 直撥測試
   - 效能調校：啟用硬體 offloading、評估 QoS（與 offloading 的取捨）
   - 維運：設定備份、監控紀錄、溫度與 UPS 管理、定期健康檢查

### 關鍵要點清單
- 分離式架構（Router/AP 分離）：提升穩定、維護與擺位彈性（優先級: 高）
- UniFi Controller 生態：集中管理多 AP、單 SSID 無縫漫遊（優先級: 高）
- PoE 佈署：以網路線供電簡化安裝與供電安全（優先級: 中）
- VLAN 802.1Q（Tagged/Untagged）：基礎的邏輯隔離方法（優先級: 高）
- Trunk 與 Access Port 規劃：跨設備（Router/Switch）傳遞多 VLAN 的關鍵（優先級: 高）
- EdgeRouter X SFP 硬體 switch：per-port VLAN 與低溫、PoE 的選型考量（優先級: 中）
- GS116E 簡易網管：VLAN/QoS/LAG 功能滿足家用進階需求（優先級: 中）
- Inter-VLAN Routing + 防火牆：在隔離與必要互通間取得平衡（優先級: 高）
- LACP（NAS 聚合）：提升多用戶同時存取的總體吞吐（優先級: 中）
- PPPoE 直撥測試通道：快速定位問題於 LAN/Router/ISP 層級（優先級: 中）
- 硬體 Offloading vs QoS：效能與功能的取捨需依場景決策（優先級: 中）
- AP 佈點與漫遊：多台 AP 的功率/信道規劃影響體感品質（優先級: 中）
- Docker 化 Controller：避免在 PC 安裝 Java，提升穩定性與可維運性（優先級: 低）
- 熱設計與壽命（電容鼓脹教訓）：溫度管理與 UPS 以外的硬體健康（優先級: 中）
- 埠位與配線標籤化：Trunk/Access/PoE 的清楚標示有助維運與擴充（優先級: 中）