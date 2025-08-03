---
source_file: "_posts/2019/2019-12-12-home-networking.md"
generated_date: "2025-08-03 15:00:00 +0800"
version: "1.0"
tools:
  - github_copilot
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# 水電工日誌 #7. 事隔 12 年的家用網路架構大翻新 - 生成內容

## Metadata

### 原始 Metadata
```yaml
layout: post
title: "水電工日誌 #7. 事隔 12 年的家用網路架構大翻新"
categories:
- "系列文章: 水電工日誌"
tags: ["水電工", "敗家"]
published: true
comments: true
redirect_from:
logo: /wp-content/images/2019-12-12-home-networking/network.jpg
```

### 自動識別關鍵字
- **主要關鍵字**: 家用網路, VLAN, 網路架構, WiFi, Router, Switch, UniFi AP, EdgeRouter, PoE, 網路設備
- **次要關鍵字**: ASUS RT-N16, Ubiquiti, NETGEAR, Intel i350-T4, hardware offloading, LACP, PPPoE, 雙十一

### 技術堆疊分析
- **程式語言**: 無特定程式語言
- **框架/函式庫**: UniFi Controller, Docker
- **工具平台**: EdgeRouter-X SFP, UniFi AP AC Lite, NETGEAR GS116Ev2, Intel i350-T4, NAS
- **開發模式**: 網路架構設計, VLAN規劃, 設備整合, 家庭網路管理

### 參考資源
- **內部連結**: 
  - 水電工日誌系列文章
  - .NET Conf 2019演講
- **外部連結**: 
  - UniFi產品頁面
  - VLAN教學文章
  - Mobile01討論串
- **提及工具**: UniFi Controller, Docker, NAS, HiNET測速軟體

### 內容特性
- **文章類型**: 開箱文, 實作分享, 網路架構規劃
- **難度等級**: 中級
- **閱讀時間**: 約15-20分鐘
- **實作程度**: 包含詳細的設備選擇和網路規劃過程

## 摘要 (Summaries)

### 文章摘要 (Article Summary)
本文記錄作者在家用網路設備故障後，進行的大規模網路架構翻新過程。包括WiFi設備升級到UniFi AP系統、路由器和交換器的替換、以及透過VLAN技術重新規劃網路架構。作者詳細分享了設備選擇考量、VLAN規劃設計、實際安裝配置和效能測試結果，並從網路管理的角度分享對軟體開發的啟發。

### 關鍵要點 (Key Points)
1. 將WiFi AP與Router功能分離，提供更好的網路覆蓋和管理彈性
2. 透過VLAN技術實現網路分段，提升安全性和管理效率
3. PoE技術簡化AP安裝，減少電源適配器需求
4. 企業級設備在家用環境的優勢：穩定性、可管理性和擴展性
5. 網路架構設計原則可以啟發軟體系統的設計思維

### 段落摘要1 (Section Summaries)
**WiFi系統升級**: 從傳統的消費級WiFi路由器升級到企業級UniFi AP系統。解決了WiFi覆蓋不足、漫遊切換和多頻段管理問題。UniFi系統支援統一SSID、自動漫遊和集中管理，提供更好的使用體驗。

### 段落摘要2 (Section Summaries)
**Router和Switch替換**: 選擇EdgeRouter-X SFP作為新路由器，支援PoE和硬體Switch功能。搭配NETGEAR GS116Ev2網管交換器，提供VLAN、QoS等進階功能。考量因素包括溫度控制、PoE支援和管理介面易用性。

### 段落摘要3 (Section Summaries)
**VLAN網路規劃**: 設計三組VLAN分別用於VDSL連線、Server網段和Home網段。透過跨設備的VLAN配置，實現網路分段和安全隔離。解決了NAS獨立網段、防火牆隔離和PPPoE直接撥接等需求。

### 段落摘要4 (Section Summaries)
**效能測試與心得**: 實測網路效能達到近似滿速，證明設備選擇和配置的正確性。分享從網路設備管理中獲得的軟體開發啟發，特別是規則引擎和領域知識在複雜系統設計中的應用價值。

## 問答集 (Q&A Pairs)

### Q1, 為什麼要將WiFi AP與Router功能分離
Q: 為什麼不選擇WiFi路由器一體機，而要分離WiFi AP和Router功能？
A: 分離設計有幾個優勢：1.Router可以放置在機櫃內專注穩定性，AP可以放在最佳訊號位置；2.可以根據覆蓋需求增加多個AP而不影響路由功能；3.企業級AP提供更好的漫遊體驗和集中管理；4.設備故障時影響範圍較小，維護更靈活。

### Q2, UniFi系統相比傳統WiFi路由器有什麼優勢
Q: UniFi AP系統相比傳統消費級WiFi路由器有哪些具體優勢？
A: UniFi系統主要優勢包括：1.統一SSID實現無縫漫遊，不需手動切換網路；2.UniFi Controller提供集中管理，可同時管理多個AP；3.企業級穩定性和效能；4.PoE供電簡化安裝；5.支援大規模部署和專業網路管理功能；6.吸頂式設計美觀且訊號覆蓋更佳。

### Q3, VLAN在家用網路中的實際應用價值
Q: 在家用環境中使用VLAN技術有什麼實際價值？值得這麼複雜的設定嗎？
A: VLAN在家用環境的價值：1.網路分段提升安全性，例如隔離NAS和一般上網設備；2.提升網路效率，避免廣播風暴；3.支援多種網路服務，如MOD、VoIP等；4.方便管理和故障排除；5.為未來擴展預留彈性。雖然設定複雜，但對於有多種網路設備和服務需求的環境很有價值。

### Q4, PoE技術在家用網路部署中的優勢
Q: PoE（Power over Ethernet）技術在家用網路中有什麼實際好處？
A: PoE技術的主要優勢：1.簡化安裝，只需一條網路線即可提供數據和電力；2.減少電源適配器數量，降低故障點；3.便於AP安裝在最佳位置，不受電源插座限制；4.集中供電管理，可透過UPS保護；5.未來擴展更靈活，移動設備不需重新佈電源線。

### Q5, 網管設備選擇的關鍵考量因素
Q: 選擇網路設備時應該考慮哪些關鍵因素？如何在功能和成本之間取得平衡？
A: 關鍵考量因素：1.實際需求分析（頻寬、埠數、功能需求）；2.未來擴展性和升級路徑；3.設備穩定性和溫度控制；4.管理介面的易用性；5.廠商支援和社群資源；6.總體擁有成本。建議先明確需求再選設備，避免功能過剩或不足，同時考慮學習成本和維護複雜度。

### Q6, 網路架構設計對軟體開發的啟發
Q: 網路設備的設計思維如何應用到軟體系統開發中？
A: 網路設備的設計理念可以啟發軟體開發：1.規則引擎架構：透過可配置的規則和優先順序處理複雜邏輯；2.分層設計：如OSI七層模型可應用於軟體架構分層；3.標準化接口：如VLAN tag概念可應用於系統間通信；4.領域知識抽象：將複雜問題抽象成標準化的配置模式；5.可擴展性設計：透過模組化和標準化支援未來擴展。

## 解決方案 (Solutions)

### P1, 家用WiFi覆蓋不足和漫遊問題
Problem: 大坪數住宅WiFi訊號覆蓋不均，需要手動切換不同AP的SSID，用戶體驗不佳
Root Cause: 傳統消費級WiFi路由器功率有限，多個不同SSID的AP無法提供無縫漫遊體驗
Solution: 採用企業級UniFi AP系統，透過統一控制器管理多個AP，實現統一SSID和自動漫遊
Example:
```bash
# UniFi Controller Docker部署
docker run -d \
  --name=unifi-controller \
  -e PUID=1000 \
  -e PGID=1000 \
  -p 8080:8080 \
  -p 8443:8443 \
  -p 3478:3478/udp \
  -v /path/to/data:/config \
  --restart unless-stopped \
  linuxserver/unifi-controller
```

### P2, 網路分段和安全隔離需求
Problem: 家用網路中NAS、工作設備、一般上網設備混在同一網段，存在安全風險且難以管理
Root Cause: 使用無網管交換器無法實現網路分段，所有設備都在同一廣播域中
Solution: 透過VLAN技術實現網路分段，配置不同安全等級的網段並設定防火牆規則
Example:
```bash
# EdgeRouter VLAN配置示例
configure
set interfaces switch switch0 vlan 10 description "Server LAN"
set interfaces switch switch0 vlan 20 description "Home LAN"
set interfaces switch switch0 vlan 30 description "VDSL"

# 設定防火牆規則隔離不同VLAN
set firewall group network-group SERVER_NETS network 192.168.10.0/24
set firewall group network-group HOME_NETS network 192.168.20.0/24
commit
save
```

### P3, 網路設備供電和線路管理複雜化
Problem: 網路設備增多導致電源適配器數量激增，線路管理混亂，故障排除困難
Root Cause: 每個網路設備都需要獨立電源，缺乏統一的供電和管理機制
Solution: 採用PoE技術集中供電，搭配UPS保護，簡化線路管理並提升可靠性
Example:
```bash
# PoE配置示例（EdgeRouter-X SFP）
configure
set interfaces switch switch0 switch-port interface eth1 poe output on
set interfaces switch switch0 switch-port interface eth2 poe output on

# 檢查PoE狀態
show poe

# 設定PoE功率預算
set poe interface eth1 power 24v
commit
save
```

## 版本異動紀錄

### v1.0 (2025-08-03)
- 初始版本，基於原始文章建立embedding content
- 包含家用網路架構設計的完整過程
- 加入VLAN規劃和設備選擇的詳細分析
- 提供網路管理對軟體開發啟發的深度思考
