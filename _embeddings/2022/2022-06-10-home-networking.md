---
source_file: "_posts/2022/2022-06-10-home-networking.md"
generated_date: "2025-01-03 11:00:00 +0800"
version: "1.1"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# 水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路 - 生成內容

## Metadata

### 原始 Metadata

```yaml
layout: post
title: "水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "有的沒有的", "敗家", "UniFi"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2022-06-10-home-networking/2022-06-12-03-36-32.png
```

### 自動識別關鍵字
keywords:
  primary:
    - UniFi
    - 家用網路
    - 網路設備整合
    - UDM-PRO
    - 10G網路
  secondary:
    - VLAN
    - PoE
    - USW-ENT
    - 監控攝影機
    - NAS
    - Layer 3 Switch

### 技術堆疊分析
tech_stack:
  languages:
    - Shell
    - Dockerfile
  frameworks:
    - Docker
    - Jekyll
    - GitHub Pages
  tools:
    - UniFi Network Controller
    - AdGuard Home
    - Iperf3
    - VSCode
    - Portainer
  platforms:
    - Synology DSM
    - UniFi OS
    - Linux

### 參考資源
references:
  internal_links:
    - /2007/10/05/水電工日誌-6-機櫃設備展示/
    - /2019/12/12/home-networking/
    - /2016/09/16/blog-as-code/
    - /2018/07/28/labs-lcow-volume/
    - /2016/02/07/buy_minipc_server/
  external_links:
    - https://tw.store.ui.com/collections/unifi-network-unifi-os-consoles/products/udm-pro-1
    - https://adguard.com/zh_tw/adguard-home/overview.html
    - https://www.wireguard.com/
    - https://bitwarden.com/
    - https://www.home-assistant.io/
  mentioned_tools:
    - UDM-PRO
    - USW-Enterprise-24-PoE
    - UniFi Protect
    - Synology DS1821+
    - AdGuard Home
    - Teleport VPN

### 內容特性
content_metrics:
  word_count: 8500
  reading_time: "42 分鐘"
  difficulty_level: "中高級"
  content_type: "心得"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)

作者分享了從2019年開始的家用網路設備全面升級經歷，以UniFi全家餐為核心進行整合。文章詳細記錄了五個主要目標的實現過程：網路設備整合、網路基礎建設、居家監控、網路服務，以及邁向10G網路。作者透過UDM-PRO、USW-Enterprise 24 PoE、UniFi AP等設備，成功將原本複雜的機櫃設備從多台不同廠牌的設備整合為統一的UniFi生態系統。在網路基礎建設方面，作者建立了5個VLAN進行網段隔離，並配置了VPN、DNS、威脅防護等服務。居家監控從傳統的DVR系統升級為UniFi Protect的IP攝影機方案。網路服務則透過Synology NAS的Docker環境架設了包括AdGuard Home、Bitwarden、VS Code等多種個人服務。最後在10G網路的探索中，作者發現了UDM-PRO的架構限制和威脅管理功能對效能的影響，並透過啟用Layer 3 Switch功能來解決瓶頸問題。整個升級過程體現了軟體整合帶來的便利性，也為其他有類似需求的使用者提供了寶貴的實戰經驗。

### 關鍵要點 (Key Points)

- 從2019年開始進行的UniFi全家餐網路設備整合計畫
- 透過UDM-PRO統一管理路由、交換、WiFi、監控等功能
- 建立5個VLAN實現網段隔離和流量管理
- 使用Layer 3 Switch解決10G網路的效能瓶頸
- 透過NAS Docker環境架設多種個人網路服務

### 前言與理想網路環境規劃 (Section Summaries)

作者回顾了15年前的網路設備配置，發現許多當年的投資已經過時，包括同軸電纜、市內電話系統等都已荒廢。現代網路環境的核心是穩定可靠的IP網路和足夠的頻寬，因此作者制定了設備精簡化和規格統一的原則。文章提出了五個具體目標：網路設備整合、網路基礎建設、居家監控、網路服務，以及10G網路升級。作者強調所有設備都朝向IP化和PoE化發展，以UniFi全家餐統一管理所有網路功能，並將其他服務整合到NAS平台。這種規劃思維體現了從硬體導向轉向軟體整合的現代網路建設理念，為後續的詳細實施奠定了基礎。

### 網路設備整合與機櫃演進 (Section Summaries)

作者詳細介紹了目前運作中的UniFi設備配置，包括UDM-PRO擔任核心路由器和控制器角色、USW-Enterprise 24 PoE提供Layer 3交換和PoE供電、多台UniFi AP負責無線覆蓋。相比15年前複雜的設備配置，現在只需5U機櫃空間就能完成所有功能。作者展示了機櫃的演進歷程，從2007年的多設備混合配置，到2019年的過渡期混亂狀態，最終達到2022年的簡潔統一配置。線材部分全面統一為CAT5E網路線，連電話線都改用相同規格，實現了結構化佈線的目標。作者特別推薦UniFi原廠的可彎護套跳線，不僅品質可靠且能保持整潔的外觀。整個整合過程突顯了軟體統一管理帶來的巨大優勢，大幅簡化了網路設備的維護和管理工作。

### VLAN規劃與網路基礎建設 (Section Summaries)

作者建立了5個不同用途的VLAN進行網段隔離和管理：TRUNK(10.0.0.0/24)作為設備骨幹、MODEM直連光世代數據機、NAS(192.168.100.0/24)供存儲和實驗使用、HOME(192.168.200.0/24)供家人日常上網、GUEST/IOT(192.168.201.0/24)隔離不信任設備。除了基本的網段劃分，作者還配置了DNS重寫服務AdGuard Home、L2TP和新推出的Teleport VPN、以及威脅管理等安全功能。Teleport VPN基於WireGuard協議，提供了比傳統VPN更簡便的設定體驗。新版本firmware還增加了Traffic Rules功能，能夠根據應用程式類別、設備群組、時間排程等條件進行精細的流量控制，特別適合實現家長控制功能。這些高度整合的網管功能讓原本複雜的企業級網路管理在家用環境中變得平易近人。

### 監控系統與UniFi Protect (Section Summaries)

作者從傳統的DVR監控系統升級到UniFi Protect平台，使用G3-Flex有線攝影機和G3-Instant WiFi攝影機取代了原本的同軸電纜類比攝影機。UniFi Protect內建於UDM-PRO中，只需插入硬碟即可開始錄影，Web介面和手機APP的使用體驗遠超傳統DVR設備。雖然攝影機選擇僅限於UniFi自家產品且經常缺貨，但產品品質穩定可靠，G3-Instant更是高CP值的入門選擇。WiFi攝影機採用通用的USB-C供電，可搭配行動電源作為備用電源。作者也提到可以透過UniFi Protect提供的RTSP串流，搭配Synology Surveillance Station建立錄影備份機制。整體而言，UniFi Protect提供了企業級的監控功能和消費級的使用體驗，是家用監控系統的理想選擇。

### NAS網路服務與Docker應用 (Section Summaries)

作者使用Synology DS1821+搭配32GB RAM和10G網卡，透過Docker環境架設了多種網路服務。基礎服務包括AdGuard Home提供DNS過濾、Portainer管理Docker容器、以及搭配Let's Encrypt憑證的Reverse Proxy服務。個人應用方面主要是Bitwarden密碼管理器，作者特別強調NAS相較於自組PC在資料可靠性方面的優勢，內建的RAID和備份機制更適合重要服務的長期運行。網路工具部分包括Iperf3進行頻寬測試、以及透過VNC提供Web界面的FileZilla FTP客戶端。開發相關服務則包括VS Code Server讓使用者可透過瀏覽器進行程式開發、Jekyll環境支援GitHub Pages本地預覽、以及為了懷舊目的重新架設的Blog Engine環境。這些服務的組合展現了現代NAS平台的強大擴展性，能夠滿足從基礎網路服務到專業開發環境的各種需求。

### 10G網路升級與效能調校 (Section Summaries)

作者在邁向10G網路的過程中發現了兩個重要瓶頸。首先是UDM-PRO的架構限制，內建的8埠交換器與10G埠之間僅有1G連接，因此必須搭配專業交換器才能充分利用10G頻寬。其次是啟用威脅管理功能會大幅影響路由效能，在進行跨VLAN通訊時速度會被限制在1.4Gbps左右。作者透過啟用USW-Enterprise 24 PoE的Layer 3 Switch功能，讓VLAN間的路由直接在交換器層級處理，成功解決了效能瓶頸問題。實際測試結果顯示，PC到NAS的連線速度能夠達到2.35Gbps的理論上限。作者建議要建置10G網路的使用者需要仔細考慮整體架構設計，避免單一設備成為效能瓶頸。這個升級過程也證明了專業級Layer 3交換器在家用高速網路環境中的重要性。

## 問答集 (Q&A Pairs)

### Q1. 為什麼選擇UniFi全家餐而不是其他品牌？

Q: 作者為什麼最終選擇UniFi全套設備，而不是混用其他品牌的網路設備？
A: 主要原因是UniFi的高度整合優勢。雖然單純就功能或CP值而言，UniFi的Router/Switch不是最突出的選擇，但其軟體整合能力讓半調子網管也能建構複雜的網路環境。相比其他品牌如MikroTek雖然功能更強大，但學習門檻太高。UniFi Network Controller能夠在單一介面管理所有設備，大幅簡化VLAN設定、Guest Network配置等複雜操作，這是其他廠牌難以提供的使用體驗。

### Q2. 家用網路環境需要切VLAN嗎？好處是什麼？

Q: 在家用環境中建立多個VLAN有什麼實際好處？如何規劃？
A: 作者建立了5個VLAN分別服務不同需求：保障家人上網品質、隔離LAB實驗環境、管控不信任設備的網路存取、以及支援多重PPPoE連線。VLAN隔離可以防止實驗環境影響家用網路、限制IoT設備的存取權限、並為不同用途的流量提供專屬頻寬。配合UniFi的整合管理，原本複雜的企業級網路功能在家用環境中變得容易實現和維護。

### Q3. UniFi Protect相比傳統DVR有什麼優勢？

Q: UniFi Protect監控系統比傳統DVR和其他方案有什麼優勢和劣勢？
A: 優勢包括：優秀的Web介面和手機APP、內建於UDM-PRO無需額外硬體、IP攝影機支援PoE或WiFi連接、高度整合的使用體驗。劣勢則是攝影機只能使用UniFi自家產品、經常缺貨、高階機種價格較貴、備份機制有限。不過整體而言，UniFi Protect提供了企業級功能和消費級體驗的完美結合，遠勝傳統DVR的難用介面。

### Q4. 為什麼選擇NAS而不是自組PC當伺服器？

Q: 用NAS架設服務與自組PC相比有什麼考量？
A: NAS相較於自組PC的主要優勢在於資料可靠性。NAS以儲存為出發點，內建RAID和備份機制，更適合運行重要服務如密碼管理器。雖然自組PC在效能和擴展性方面更強，但維護複雜且資料安全性考量不足。對於需要長期穩定運行的服務，NAS的低功耗、易管理特性和完善的資料保護機制是更好的選擇。硬體資源雖然有限但足以應付大部分家用服務需求。

### Q5. Traffic Rules功能如何實現家長控制？

Q: UniFi的Traffic Rules功能如何用於管控家中小孩的上網時間和內容？
A: Traffic Rules提供了三個維度的控制：Category（可選擇特定APP或網站類別）、Target（可指定特定設備或設備群組）、Schedule（可設定時間排程）。例如可以設定「週一到週五晚上10點到12點禁止兒子手機使用Social Networks」這類精細控制。相比傳統的IP或MAC地址封鎖，這種基於應用程式識別的方式更難被繞過，且設定更直觀。這功能解決了UniFi長期缺乏家長控制功能的問題。

### Q6. 10G網路升級會遇到什麼瓶頸？

Q: 在家用環境升級10G網路會遇到哪些技術瓶頸？如何解決？
A: 主要瓶頸有兩個：UDM-PRO架構限制和威脅管理效能影響。UDM-PRO內建的8埠交換器與10G埠間僅1G連接，需搭配專業交換器。啟用威脅管理會限制跨VLAN路由效能至1.4Gbps。解決方案是使用支援Layer 3的交換器直接處理VLAN間路由，避開UDM-PRO的處理瓶頸。此外還需考慮線材規格、網卡支援、以及整體頻寬規劃等因素。

### Q7. 如何透過NAS建立完整的個人雲端服務？

Q: 如何利用NAS的Docker環境建立類似雲端服務的個人應用？
A: 關鍵是建立DNS、SSL憑證、Reverse Proxy的基礎架構。首先用AdGuard Home提供DNS重寫，讓內部服務可用域名存取。接著申請Let's Encrypt免費SSL憑證，搭配NAS內建的Reverse Proxy讓多個服務共用443埠。最後在Docker中部署各種服務如Bitwarden密碼管理、VS Code開發環境、檔案管理等。這個組合提供了完整的個人雲端體驗，既保有隱私又享有便利性。

### Q8. Teleport VPN相比傳統VPN有什麼優勢？

Q: UniFi的Teleport VPN相比L2TP等傳統VPN協議有什麼特色？
A: Teleport VPN基於WireGuard協議，相比OpenVPN更快速簡易。最大優勢是設定極其簡單：在Controller產生連結、手機點擊連結自動完成設定，無需手動輸入伺服器位址、密碼等資訊。WiFi Man APP會自動處理所有配置，使用時只需開關VPN即可。雖然目前缺少Windows客戶端，但行動裝置的使用體驗已經非常優秀，是懶人福音的VPN解決方案。

## 解決方案 (Solutions)

### P1. 複雜網路設備整合困難

Problem: 家用網路環境中使用多個不同廠牌設備，管理複雜且設定分散，增加維護負擔和故障排除難度。

Root Cause: 不同廠牌設備的管理介面、設定方式、功能整合度不一，缺乏統一的管理平台。當設備數量增加時，每個功能都需要在不同系統間切換設定，容易出錯且難以維護。

Solution: 採用UniFi全家餐解決方案，透過單一UniFi Network Controller管理所有網路設備。包括路由器(UDM-PRO)、交換器(USW-ENT)、無線AP、監控攝影機等都整合在同一管理平台，實現設備統一、介面統一、設定統一。

Example:
```bash
# 單一控制台管理所有UniFi設備
- UDM-PRO: Router + Firewall + Controller + Protect
- USW-ENT: Layer 3 Switch + PoE
- UAP: WiFi Access Points
- 統一透過 UniFi OS Console 管理
```

### P2. VLAN設定與管理複雜

Problem: 在多設備環境中設定VLAN需要在每台設備上分別配置tag/untag、PVID等參數，容易設定錯誤導致網路不通。

Root Cause: 傳統網路設備需要在路由器、交換器、AP等設備上分別設定VLAN參數，每次修改都需要更改多台設備，且各廠商的設定方式不同，增加了出錯機率。

Solution: 透過UniFi Network Controller建立Network配置，自動將VLAN設定推送到所有相關設備。支援網段管理、路由規則、防火牆政策的統一配置。

Example:
```yaml
# UniFi Network 設定範例
Networks:
  - TRUNK: VLAN 0 (10.0.0.0/24) - 設備骨幹
  - HOME: VLAN 200 (192.168.200.0/24) - 家用設備  
  - NAS: VLAN 100 (192.168.100.0/24) - 儲存與實驗
  - GUEST: VLAN 201 (192.168.201.0/24) - 訪客隔離
```

### P3. 家長控制功能實現困難

Problem: 傳統路由器的家長控制功能設定複雜，基於IP/MAC的封鎖容易被繞過，且無法提供精細的應用程式層級控制。

Root Cause: 早期的UniFi產品缺乏簡易的家長控制功能，需要透過複雜的VLAN和防火牆規則組合實現，對一般使用者門檻太高。

Solution: 使用UDM-PRO新版firmware的Traffic Rules功能，提供基於應用程式識別的流量控制，支援時間排程和設備群組管理。

Example:
```yaml
# Traffic Rules 設定範例
Rule: 限制小孩上網時間
Category: Social Networks (Facebook, Instagram等)
Target: 小孩的手機設備
Schedule: 週一~週五 22:00-24:00
Action: Block
```

### P4. 10G網路效能瓶頸

Problem: UDM-PRO啟用威脅管理功能後，跨VLAN的路由效能被限制在1.4Gbps，無法發揮10G網路的真實效能。

Root Cause: UDM-PRO的威脅管理需要深度封包檢測，消耗大量CPU資源。同時UDM-PRO內建交換器與10G埠間的架構限制也影響整體throughput。

Solution: 啟用Layer 3交換器功能，讓VLAN間路由直接在交換器層級處理，避開UDM-PRO的效能瓶頸。同時合理規劃威脅管理的啟用範圍。

Example:
```bash
# Layer 3 Switch 配置
USW-ENT-24POE:
- 啟用 Layer 3 Switch 功能
- VLAN間路由在交換器處理
- 減少UDM-PRO CPU負載
- 實現 PC -> NAS 2.35Gbps 滿速傳輸
```

### P5. 個人雲端服務架設複雜

Problem: 自架網路服務需要處理DNS、SSL憑證、反向代理等複雜配置，對一般使用者技術門檻過高。

Root Cause: 傳統架設方式需要分別設定DNS伺服器、申請和管理SSL憑證、配置Nginx等反向代理，每個環節都需要專業知識。

Solution: 利用NAS內建功能結合Docker服務，透過AdGuard Home + Let's Encrypt + Reverse Proxy的整合方案，簡化個人雲端服務的架設和管理。

Example:
```yaml
# 個人雲端服務架構
DNS: AdGuard Home (域名重寫)
SSL: Let's Encrypt (自動更新憑證)  
Proxy: Synology Reverse Proxy
Services: 
  - Bitwarden (密碼管理)
  - VS Code Server (程式開發)
  - 各種Docker應用
```

### P6. 監控系統升級與整合

Problem: 傳統DVR監控系統介面難用、需要同軸電纜布線、錄影備份困難，且與網路系統整合度低。

Root Cause: 傳統監控系統採用專屬的類比或HD-SDI標準，需要專用線材和設備，與IP網路基礎設施無法整合，管理介面通常也很陽春。

Solution: 採用UniFi Protect平台搭配IP攝影機，利用現有網路基礎設施，透過PoE供電或WiFi連接，整合在統一的管理平台中。

Example:
```yaml
# UniFi Protect 監控架構
設備: UDM-PRO (內建Protect) + HDD
攝影機: 
  - G3-Flex (PoE有線)
  - G3-Instant (WiFi + USB-C)
管理: Web介面 + 手機APP
備份: RTSP -> Synology Surveillance Station
```

## 版本異動紀錄

### v1.1 (2025-01-03)
- 修正摘要格式，改用第三人稱敘述，加入生成工具資訊
- 完善技術堆疊分析和參考資源連結
- 調整問答集和解決方案內容，使其更貼近實際應用場景

### v1.0 (2025-01-03)
- 初始版本
