---
layout: synthesis
title: "Finally..."
synthesis_type: solution
source_post: /2007/09/11/finally/
redirect_from:
  - /2007/09/11/finally/solution/
---

說明：原文僅描述家庭佈線未完成、僅一台設備上線、電話線未接、但自架 blog server 已上線，以及線材凌亂等情境。為滿足實戰教學需求，以下案例均基於原文情境推導與標準做法設計，用於訓練與評估；包含的實測數據為教學示意或常見可達成水準，非原文直接提供之數據。

## Case #1: 自架 Blog 伺服器動態 IP 外網上線（DDNS + NAT 轉發）

### Problem Statement（問題陳述）
業務場景：家用網路僅有一台電腦上線，blog 伺服器已架設但需對外提供服務。住家使用動態 IP，無固定 DNS 紀錄，外部無法穩定存取；目標是在現有路由器環境下，讓 blog 網域可被外網穩定解析並透過 80/443 連入。
技術挑戰：動態 IP 下的 DNS 更新、NAT 轉發與防火牆放行、憑證申請與續期自動化。
影響範圍：外部使用者無法連線、SEO 與可用性不佳、維運成本高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無 DDNS：ISP 提供動態 IP，DNS 無法跟隨更新。
2. NAT 未設：未建立 80/443 轉發至內部伺服器。
3. 憑證缺失：HTTPS 不可用，瀏覽器警告導致用戶流失。

深層原因：
- 架構層面：未規劃對外服務與家用網並存架構。
- 技術層面：缺乏 DDNS、自動簽發憑證與續期流程。
- 流程層面：沒有部署與變更紀錄，設定易失控。

### Solution Design（解決方案設計）
解決策略：在路由器上部署 DDNS 客戶端，將動態 IP 與網域綁定；設定 80/443 NAT 轉發與最小化的防火牆規則；導入自動化憑證工具（acme/certbot 或 Caddy），確保 HTTPS 可用且免人工維護。

實施步驟：
1. 啟用 DDNS 並校驗解析
- 實作細節：註冊 DuckDNS/Cloudflare，安裝 ddclient 或 luci-app-ddns
- 所需資源：OpenWrt 路由器、DDNS 帳號
- 預估時間：1 小時
2. 設定 NAT 與憑證
- 實作細節：80/443 轉發到 blog server；以 acme.sh 或 Caddy 取得/續期憑證
- 所需資源：路由器管理權限、網域、ACME 客戶端
- 預估時間：2 小時

關鍵程式碼/設定：
```bash
# OpenWrt: 80/443 轉發
uci add firewall redirect
uci set firewall.@redirect[-1].name='http_to_blog'
uci set firewall.@redirect[-1].src='wan'
uci set firewall.@redirect[-1].src_dport='80'
uci set firewall.@redirect[-1].dest='lan'
uci set firewall.@redirect[-1].dest_ip='192.168.1.10'
uci set firewall.@redirect[-1].dest_port='80'
uci set firewall.@redirect[-1].proto='tcp'
uci commit firewall && /etc/init.d/firewall restart

# ddclient (Cloudflare)
cat <<'EOF' >/etc/ddclient.conf
protocol=cloudflare, \
zone=example.com, \
ttl=1
login=CF_API_TOKEN
password='CF_API_TOKEN'
blog.example.com
EOF
```

實際案例：原文家庭環境，自架 blog server 需上線。
實作環境：OpenWrt 22.03、Debian 12（Nginx）、Cloudflare DNS。
實測數據：
改善前：外部可達率不穩定（IP 變更即失效）、HTTPS 不可用
改善後：外部可達率 99.5%；憑證自動續期；DNS 更新延遲 < 60 秒
改善幅度：可用性顯著提升，人工維護降至零

Learning Points（學習要點）
核心知識點：
- 動態 IP 下的 DDNS 原理與部署
- NAT/防火牆與服務暴露的最小化原則
- ACME 協議與憑證自動化
技能要求：
- 必備技能：路由器管理、Linux 基本操作
- 進階技能：DNS/ACME 工作原理、逆向代理
延伸思考：
- 可改用反向代理服務或 Tunnel（如 Cloudflare Tunnel）免開埠
- 動態 IP 頻繁變動時的 TTL 與快取影響
- 加入 WAF 或速率限制以提升防護

Practice Exercise（練習題）
- 基礎練習：在測試域名上完成 DDNS 綁定（30 分鐘）
- 進階練習：完成 80/443 轉發並通過 HTTPS 憑證測試（2 小時）
- 專案練習：使用 Caddy/Nginx 建立可外網存取的 blog 站（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：DDNS 正常、80/443 可達、HTTPS 有效
- 程式碼品質（30%）：設定檔結構清晰、變更可追溯
- 效能優化（20%）：TLS 配置合理、首包時間與端口開放最少化
- 創新性（10%）：引入自動化與風險緩解（WAF/速率限制）

---

## Case #2: 22 埠配線架映射與標籤化（從 2 埠可用到全面可管）

### Problem Statement（問題陳述）
業務場景：住家已佈線共 22 個資訊插座，但僅有 2 埠接通；地面線材凌亂，無法快速定位每條線的去處。需完成端點到配線架的映射、標籤與文檔，讓後續擴容與維護可控。
技術挑戰：無文檔、無標籤、端點難追蹤；既有線路長度與路由不明，測試與記錄耗時。
影響範圍：工時增加、誤插造成中斷、維護風險高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未標籤：端點與配線架無一致編碼。
2. 無拓撲：未建立房間—配線架對照表。
3. 缺測試：未做通斷與速率認證（CAT6/1G）。

深層原因：
- 架構層面：缺少結構化佈線治理（命名規範）。
- 技術層面：欠缺測試工具與方法（toner、測試儀）。
- 流程層面：無變更管理與文檔更新機制。

### Solution Design（解決方案設計）
解決策略：以房間/面板/埠號為核心建立命名規範；使用訊號追蹤與測試儀完成映射；以 YAML 維護資產清單，並為每個端點貼標；建立更新流程。

實施步驟：
1. 勘查與測試
- 實作細節：使用 tone generator + probe 追蹤；用線測試儀做通斷/速率測試
- 所需資源：尋線器、網路測試儀、標籤機
- 預估時間：4 小時
2. 文檔與標籤
- 實作細節：建立 ports.yaml；印製配線架與面板標籤；照片存證
- 所需資源：YAML 模板、標籤紙
- 預估時間：2 小時

關鍵程式碼/設定：
```yaml
# ports.yaml（配線映射與備註）
- id: P01
  room: Living
  wallplate: WP-LV-01
  jack: A
  patch_panel_port: 01
  cable_cat: CAT6
  test: PASS_1G
  note: TV櫃後方
- id: P02
  room: Study
  wallplate: WP-ST-01
  jack: B
  patch_panel_port: 02
  cable_cat: CAT6
  test: PASS_1G
  note: 書桌左側
```

實際案例：原文家庭的 22 埠僅接 2 埠且線材凌亂。
實作環境：CAT6 佈線、配線架+理線器、標籤機。
實測數據：
改善前：已知映射 2/22；平均定位時間 20 分鐘/埠
改善後：已知映射 22/22；平均定位時間 2 分鐘/埠
改善幅度：文檔覆蓋率 9%→100%；定位效率 10x

Learning Points（學習要點）
核心知識點：
- 結構化佈線命名規範與資產管理
- 配線映射與測試方法
- 文檔即基礎設施（IaC 思維的實體化）
技能要求：
- 必備技能：使用尋線器/測試儀、基本 YAML
- 進階技能：建立與維護配置資產庫
延伸思考：
- 導入 QR code 連結至端點詳情
- 以相片/圖資形成「現況基線」
- 用小型 CMDB 工具管理（如 NetBox）

Practice Exercise（練習題）
- 基礎練習：完成 4 埠映射與標籤（30 分鐘）
- 進階練習：建立 ports.yaml 並生成標籤（2 小時）
- 專案練習：完成 22 埠全量映射與照片存證（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：映射/標籤/照片齊備
- 程式碼品質（30%）：YAML 結構與可維護性
- 效能優化（20%）：定位時間與錯誤率下降
- 創新性（10%）：數位化資產管理方式

---

## Case #3: 線材凌亂的整理與風險控制（理線、走線、固定）

### Problem Statement（問題陳述）
業務場景：地上散落多股網路線與延長線，易絆倒且難以維護。希望將線材上架固定，縮短裸露線長，提升安全性與維護效率，並為後續擴充留餘裕。
技術挑戰：既有長度與路徑不一、缺少理線器材、無既定走線規則。
影響範圍：安全風險、設備損害、維護工時與停機風險。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無理線方案：未採用纜線槽、理線架。
2. 線長過餘：冗長的 slack 無處收納。
3. 缺固定：無魔鬼氈/扣具固定。

深層原因：
- 架構層面：未設計低/高壓分離與走線層級。
- 技術層面：未選擇適當長度/規格線材。
- 流程層面：無標準作業程序（SOP）。

### Solution Design（解決方案設計）
解決策略：制定走線規則與安全距離，安裝纜線槽與理線板，使用魔鬼氈集中 slack；低壓與市電分離，建立物料清單與 SOP。

實施步驟：
1. 規劃與安裝
- 實作細節：安裝理線槽、D 型扣、魔鬼氈；規劃分層走線
- 所需資源：纜線槽、魔鬼氈、螺絲/膨塞
- 預估時間：3 小時
2. 整理與驗收
- 實作細節：按區捆綁與標籤；拍照存證與更新 BOM
- 所需資源：標籤機、手機相機
- 預估時間：2 小時

關鍵程式碼/設定：
```yaml
# bom.yaml（物料與區域）
materials:
  - name: CableTray_60cm
    qty: 3
  - name: Velcro_Ties
    qty: 50
  - name: D_Rings
    qty: 12
zones:
  - name: RackTop
  - name: DeskBack
rules:
  - separate_low_high_voltage: true
  - slack_loop_per_zone: 30cm
```

實際案例：原文提及地上一堆線導致困擾。
實作環境：家用弱電櫃/電視櫃。
實測數據：
改善前：裸露線長 ~12m；安全事故風險高；變更耗時 30 分鐘/次
改善後：裸露線長 <1m；風險顯著降低；變更耗時 10 分鐘/次
改善幅度：安全性與效率雙提升

Learning Points（學習要點）
核心知識點：
- 走線與理線最佳實務
- 低/高壓分離與 EMI 基礎
- 視覺化與照片存證
技能要求：
- 必備技能：手工具使用、基礎安全知識
- 進階技能：理線規劃與審美化管理
延伸思考：
- 增設理線架前後對氣流與散熱的影響
- 冗餘長度標準化（30–50cm）
- 可維護性與美觀的平衡

Practice Exercise（練習題）
- 基礎練習：整理 5 條線並拍照前後對比（30 分鐘）
- 進階練習：完成一個區域的走線規劃與 BOM（2 小時）
- 專案練習：完成全屋弱電區域整理（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：固定到位、低高壓分離
- 程式碼品質（30%）：BOM/規則可重用
- 效能優化（20%）：裸露線長與工時下降
- 創新性（10%）：整齊度與可審核性

---

## Case #4: 未完成端接的資訊插座收尾（Punch-down 與測試）

### Problem Statement（問題陳述）
業務場景：家中 22 埠僅 2 埠可用，其餘未端接或測試。需完成所有資訊插座的端接（T568B）、測試通斷與速率，確保日後隨插即用。
技術挑戰：端接品質、對針順序、彎折半徑與衰減控制。
影響範圍：無法擴充到更多房間、網速不穩、隱性故障。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未端接：Keystone/Jacks 未壓接或順序錯誤。
2. 未測試：未完成通斷與 1G/2.5G 認證。
3. 彎折與拉伸：施工傷害造成接觸不良。

深層原因：
- 架構層面：未規劃插座/配線架對應。
- 技術層面：缺端接工具或經驗。
- 流程層面：缺少驗收清單與記錄。

### Solution Design（解決方案設計）
解決策略：按 T568B 規範端接；使用打線工具與測試儀；建立每埠驗收清單與記錄，將結果回填 ports.yaml。

實施步驟：
1. 端接與物理檢查
- 實作細節：按色碼打線、控制彎折半徑
- 所需資源：打線工具、Keystone、剪鉗
- 預估時間：4 小時（20 埠）
2. 測試與記錄
- 實作細節：通斷、對線、1G 認證；上傳結果
- 所需資源：測試儀、相機
- 預估時間：3 小時

關鍵程式碼/設定：
```yaml
# checklist.yaml（每埠驗收）
- port: 03
  standard: T568B
  continuity: PASS
  pair_map: "1-1,2-2,3-3,6-6,4-4,5-5,7-7,8-8"
  speed: "1G PASS"
  bend_radius: ">=4x cable dia"
  photo: "photos/port03.jpg"
```

實際案例：原文提及僅 2 埠接好。
實作環境：CAT6、Keystone、測試儀。
實測數據：
改善前：可用埠 2/22；未知故障率高
改善後：可用埠 20+/22；通過 1G 測試 100%
改善幅度：可用埠提升 10x 以上

Learning Points（學習要點）
核心知識點：
- T568B 端接與對線
- 通斷與速率測試
- 端接品質控管
技能要求：
- 必備技能：手工端接與檢查
- 進階技能：測試與缺陷定位
延伸思考：
- 2.5G/10G 未來升級的佈線要求
- 面板與配線架最佳匹配
- 端接與散熱/走線關係

Practice Exercise（練習題）
- 基礎練習：端接 2 埠並通過通斷（30 分鐘）
- 進階練習：完成 8 埠端接與 1G 測試（2 小時）
- 專案練習：收尾全屋所有埠並建檔（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：通斷/速率合格
- 程式碼品質（30%）：記錄完整可追溯
- 效能優化（20%）：失效率下降
- 創新性（10%）：工具與流程優化

---

## Case #5: 未接電話線的整合與 VoIP 化（SIP/ATA）

### Problem Statement（問題陳述）
業務場景：家中電話線未接，若仍需室內話機或總機功能，可透過 VoIP 節省佈線與月費，並與結構化佈線共用 RJ45。
技術挑戰：SIP 設定、延遲與回聲、與 LAN 共存的 QoS。
影響範圍：通話品質、可靠性、緊急通話。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. RJ11 未納入配線管理。
2. 無 SIP/ATA 介面，話機無法註冊。
3. 無 QoS，語音與資料搶資源。

深層原因：
- 架構層面：未定義語音 VLAN。
- 技術層面：不了解 SIP/NAT 穿越。
- 流程層面：無號碼移轉與備援預案。

### Solution Design（解決方案設計）
解決策略：採用雲端 SIP 或自建 Asterisk；以 ATA 連接傳統話機或採 IP Phone；建立 Voice VLAN 與 QoS，確保延遲與抖動受控。

實施步驟：
1. 設定 SIP 與分機
- 實作細節：Asterisk 建立 pjsip 帳號、extensions
- 所需資源：Asterisk/FreePBX 或雲端 SIP
- 預估時間：2 小時
2. 配置 QoS 與 VLAN
- 實作細節：Voice VLAN、DSCP 46；ATA/Phone 設定
- 所需資源：管理型交換器、路由器
- 預估時間：2 小時

關鍵程式碼/設定：
```ini
; /etc/asterisk/pjsip.conf
[6001]
type=endpoint
context=internal
disallow=all
allow=ulaw,alaw
auth=6001-auth
aors=6001

[6001-auth]
type=auth
auth_type=userpass
username=6001
password=StrongPass!

[6001]
type=aor
max_contacts=1
```

實際案例：原文提及電話線未接。
實作環境：Asterisk 18、ATA 或 IP Phone、管理型交換器。
實測數據：
改善前：室內電話不可用；撥出/撥入失敗率 100%
改善後：話機註冊成功；端到端延遲 < 150ms；抖動 < 20ms
改善幅度：可用性從 0→100%

Learning Points（學習要點）
核心知識點：
- SIP 註冊與撥號流程
- QoS/DSCP 與語音 VLAN
- NAT 穿越與保活
技能要求：
- 必備技能：基本 VoIP 設定
- 進階技能：Asterisk Dialplan 與 QoS 調校
延伸思考：
- 雙線備援：行動門號 + VoIP
- E911/緊急通話配置
- SRTP/TLS 安全性

Practice Exercise（練習題）
- 基礎練習：建立一支分機可內線互撥（30 分鐘）
- 進階練習：完成外呼/來電與 QoS（2 小時）
- 專案練習：部署 3 分機的小型 PBX（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：註冊、撥入撥出、語音品質
- 程式碼品質（30%）：Asterisk 配置結構
- 效能優化（20%）：延遲/抖動控制
- 創新性（10%）：安全與備援

---

## Case #6: 僅單機上線的網路擴展與 VLAN 區隔

### Problem Statement（問題陳述）
業務場景：目前僅 1 台電腦上線，需將多房間端點接入並對伺服器/家用設備/IoT 區隔，降低相互干擾與風險。
技術挑戰：管理型交換器設定、VLAN Trunk、路由與 DHCP。
影響範圍：擴展可用性與安全性、網段間可視性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 交換器未部署或僅非管理型。
2. 無 VLAN 與子網劃分。
3. 單一 DHCP 混雜所有設備。

深層原因：
- 架構層面：無網段分層（LAN/DMZ/IoT）。
- 技術層面：不熟 DSA/VLAN。
- 流程層面：無地址規劃與命名。

### Solution Design（解決方案設計）
解決策略：部署管理型交換器，以 VLAN 劃分 LAN(10)/DMZ(20)/IoT(30)/Mgmt(99)，路由器建立對應介面與 DHCP，Trunk 到交換器。

實施步驟：
1. 路由器子介面與 DHCP
- 實作細節：OpenWrt DSA 建 VLAN 與介面
- 所需資源：OpenWrt、管理型交換器
- 預估時間：2 小時
2. 交換器 VLAN/Trunk
- 實作細節：Trunk 到路由器、Access 到端點
- 所需資源：交換器 Web/CLI
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# /etc/config/network（OpenWrt 範例）
config device
  option name 'br-lan'
  option type 'bridge'
  list ports 'lan1'
  list ports 'lan2'
  list ports 'lan3'
  list ports 'lan4'

config bridge-vlan
  option device 'br-lan'
  option vlan '10'
  list ports 'lan1:t' 'lan2:u*'  # lan2 為 LAN access

config bridge-vlan
  option device 'br-lan'
  option vlan '20'
  list ports 'lan1:t' # DMZ 經 trunk

config interface 'dmz'
  option proto 'static'
  option device 'br-lan.20'
  option ipaddr '192.168.20.1'
  option netmask '255.255.255.0'
```

實際案例：原文環境僅單機上線。
實作環境：OpenWrt 22.03、TP-Link/Unifi 管理型交換器。
實測數據：
改善前：可用接點 1；無網段隔離
改善後：可用接點 10+；LAN/DMZ/IoT 三段隔離
改善幅度：擴展能力與安全邊界顯著提升

Learning Points（學習要點）
核心知識點：
- VLAN/Trunk/Access 基礎
- 子網規劃與 DHCP
- DSA 架構
技能要求：
- 必備技能：交換器與路由器配置
- 進階技能：多 VLAN 問題診斷
延伸思考：
- L3 交換器本地路由
- mDNS/Chromecast 跨 VLAN
- 以 ACL 細化東西向流量

Practice Exercise（練習題）
- 基礎練習：建立一個新 VLAN 與 DHCP（30 分鐘）
- 進階練習：Trunk + Access 完成 DMZ 連通（2 小時）
- 專案練習：三網段 + 互通策略（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：VLAN 劃分/連通正確
- 程式碼品質（30%）：配置清晰可維護
- 效能優化（20%）：廣播域縮減
- 創新性（10%）：策略合理

---

## Case #7: 家用 DMZ 防火牆策略（對外服務最小暴露）

### Problem Statement（問題陳述）
業務場景：自架 blog server 需對外開放，應與家用 LAN 隔離，避免側移攻擊。
技術挑戰：區域劃分、最小規則集、日誌審計。
影響範圍：家庭資料安全、設備風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 伺服器與家用設備共網段。
2. 防火牆規則過寬。
3. 無審計/告警機制。

深層原因：
- 架構層面：缺少 DMZ 區域。
- 技術層面：不了解區域間策略。
- 流程層面：無變更審核。

### Solution Design（解決方案設計）
解決策略：建立 DMZ 區域與 zone policy；WAN->DMZ 僅開 80/443；DMZ 禁止主動到 LAN；啟用記錄與告警。

實施步驟：
1. 區域與政策
- 實作細節：OpenWrt zone 與 forward 規則
- 所需資源：路由器
- 預估時間：1 小時
2. 日誌與告警
- 實作細節：Log 前置、簡單告警
- 所需資源：syslog/Grafana Loki
- 預估時間：2 小時

關鍵程式碼/設定：
```bash
# /etc/config/firewall（節選）
config zone
  option name 'dmz'
  option network 'dmz'
  option input 'REJECT'
  option output 'ACCEPT'
  option forward 'REJECT'

config forwarding
  option src 'wan'
  option dest 'dmz'
  option enabled '0'  # 禁止由WAN主動轉發，僅允許DNAT

config rule
  option name 'WAN-HTTP-HTTPS'
  option src 'wan'
  option dest 'dmz'
  option dest_ip '192.168.20.10'
  option proto 'tcp'
  option dest_port '80 443'
  option target 'DNAT'
```

實際案例：原文環境需對外服務。
實作環境：OpenWrt 22.03。
實測數據：
改善前：DMZ 與 LAN 無隔離；LAN 被掃描到的埠 10+
改善後：DMZ->LAN 全阻；LAN 暴露埠 0
改善幅度：側移風險顯著降低

Learning Points（學習要點）
核心知識點：
- 區域型防火牆設計
- DNAT 與最小暴露
- 審計與告警
技能要求：
- 必備技能：基本防火牆操作
- 進階技能：策略建模與日誌分析
延伸思考：
- IDS/IPS（Suricata）導入
- GeoIP/Rate limit
- 「預設拒絕、按需放行」原則

Practice Exercise（練習題）
- 基礎練習：建立 DMZ 區域（30 分鐘）
- 進階練習：完成 DNAT 與阻斷 DMZ->LAN（2 小時）
- 專案練習：加上告警與報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：隔離有效、對外服務可達
- 程式碼品質（30%）：規則清晰
- 效能優化（20%）：最小暴露
- 創新性（10%）：增設偵測/告警

---

## Case #8: Blog 伺服器系統強化（SSH、UFW、Fail2ban）

### Problem Statement（問題陳述）
業務場景：自架主機暴露於網際網路，需最小化攻擊面與提升入侵防護。
技術挑戰：安全基線、服務端口控管、暴力破解防護。
影響範圍：資料外洩、服務中斷。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. SSH 密碼登入未停用。
2. 防火牆未限制入站。
3. 無暴力破解防護。

深層原因：
- 架構層面：無硬化基線。
- 技術層面：忽略最小權限原則。
- 流程層面：無更新與稽核。

### Solution Design（解決方案設計）
解決策略：停用密碼、啟用金鑰；UFW 僅放行 22/80/443；Fail2ban 封鎖爆破來源；自動更新。

實施步驟：
1. 強化 SSH 與 UFW
- 實作細節：sshd_config、UFW 規則
- 所需資源：Debian/Ubuntu
- 預估時間：1 小時
2. Fail2ban 與更新
- 實作細節：ssh jail、自動更新
- 所需資源：Fail2ban、unattended-upgrades
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# SSH 基本強化
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# UFW
sudo ufw default deny incoming
sudo ufw allow 22,80,443/tcp
sudo ufw enable

# Fail2ban
sudo apt-get install fail2ban -y
cat | sudo tee /etc/fail2ban/jail.d/ssh.local <<'EOF'
[sshd]
enabled = true
port = 22
maxretry = 5
bantime = 3600
EOF
sudo systemctl restart fail2ban
```

實際案例：原文自架 blog server。
實作環境：Debian 12。
實測數據：
改善前：開放埠 8 個；SSH 爆破無防護
改善後：開放埠 3 個；爆破封鎖率 ~100%
改善幅度：攻擊面縮減、入侵風險下降

Learning Points（學習要點）
核心知識點：
- 最小暴露與金鑰認證
- UFW 與 Fail2ban
- 基線加固流程
技能要求：
- 必備技能：Linux 管理
- 進階技能：安全策略落地
延伸思考：
- Port knocking/多因素
- 應用層 WAF
- 日誌集中化與審計

Practice Exercise（練習題）
- 基礎練習：UFW 配置最小開放（30 分鐘）
- 進階練習：設置 Fail2ban 規則（2 小時）
- 專案練習：完成一份安全基線腳本（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：SSH/防火牆/爆破防護到位
- 程式碼品質（30%）：設定清晰可復用
- 效能優化（20%）：端口最少化
- 創新性（10%）：多重防護

---

## Case #9: HTTPS 自動化（Caddy/Certbot 與 HSTS）

### Problem Statement（問題陳述）
業務場景：外部用戶需安全連線，手動憑證維護成本高且風險大。
技術挑戰：憑證自動簽發與續期、強化傳輸安全。
影響範圍：用戶信任、SEO、瀏覽器相容性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 手動簽憑證易過期。
2. 未強制 HTTPS 與 HSTS。
3. 憑證更新不中斷部署。

深層原因：
- 架構層面：缺乏自動化代理。
- 技術層面：對 ACME/挑戰不足理解。
- 流程層面：無續期監控。

### Solution Design（解決方案設計）
解決策略：使用 Caddy 自動簽發與續期；強制重導 HTTPS 與 HSTS；或用 Certbot + Nginx 自動續期腳本。

實施步驟：
1. 部署 Caddy
- 實作細節：Caddyfile 綁定網域與站點路徑
- 所需資源：Caddy、網域
- 預估時間：1 小時
2. 測試與監控
- 實作細節：SSL Labs 測試、續期監控
- 所需資源：SSL Labs、Cron
- 預估時間：1 小時

關鍵程式碼/設定：
```conf
# Caddyfile
blog.example.com {
  root * /var/www/blog
  encode gzip
  file_server
  header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
}
```

實際案例：原文自架 blog。
實作環境：Caddy 2.7、Debian 12。
實測數據：
改善前：無 HTTPS；瀏覽器警告
改善後：A 級評分（SSL Labs）、自動續期、強制 HTTPS
改善幅度：安全性與信任度顯著提升

Learning Points（學習要點）
核心知識點：
- ACME 自動化與挑戰類型
- HSTS 與安全標頭
- 代理與靜態站服務
技能要求：
- 必備技能：Web 伺服器配置
- 進階技能：證書管理與監控
延伸思考：
- DNS-01 挑戰搭配內網站點
- OCSP Stapling/HTTP/3
- 多站多網域管理

Practice Exercise（練習題）
- 基礎練習：Caddy 部署單站（30 分鐘）
- 進階練習：加入 HSTS 與安全標頭（2 小時）
- 專案練習：含反代與多站點配置（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：HTTPS/HSTS 正常
- 程式碼品質（30%）：配置清晰
- 效能優化（20%）：壓縮/HTTP2/3
- 創新性（10%）：自動化與監控

---

## Case #10: 可用性監控與告警（Prometheus/Blackbox）

### Problem Statement（問題陳述）
業務場景：自架站點上線後需監控可用性與資源，快速發現問題並縮短 MTTR。
技術挑戰：拉取式監控、URL 探測、告警路由。
影響範圍：停機時間、用戶體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無可用性監控。
2. 無資源監控（CPU/記憶體/磁碟）。
3. 無告警與分派。

深層原因：
- 架構層面：缺少監控與告警組件。
- 技術層面：不了解 exporter 與 probe。
- 流程層面：無 on-call 流程。

### Solution Design（解決方案設計）
解決策略：部署 Prometheus + Node/Blackbox Exporter，配置告警規則與通知（Email/Telegram），可視化 Grafana。

實施步驟：
1. 安裝與探測
- 實作細節：Node Exporter 資源、Blackbox HTTP 探測
- 所需資源：Prometheus/Grafana
- 預估時間：2 小時
2. 告警與儀表
- 實作細節：Alertmanager 規則、儀表板
- 所需資源：Alertmanager
- 預估時間：2 小時

關鍵程式碼/設定：
```yaml
# prometheus.yml（節選）
scrape_configs:
- job_name: 'node'
  static_configs: [{targets: ['192.168.20.10:9100']}]
- job_name: 'blog_http'
  metrics_path: /probe
  params: { module: [http_2xx] }
  static_configs: [{targets: ['https://blog.example.com']}]
  relabel_configs:
  - source_labels: [__address__]
    target_label: __param_target
  - target_label: __address__
    replacement: '127.0.0.1:9115'
```

實際案例：自架 blog 需監控。
實作環境：Prometheus 2.52、Grafana 10。
實測數據：
改善前：故障發現依賴人工；MTTD 不可控
改善後：HTTP 可用性監控；告警 < 1 分鐘；MTTR 顯著下降
改善幅度：可觀測性從 0→完整

Learning Points（學習要點）
核心知識點：
- Exporter/Probe 與拉取模型
- 告警規則與路由
- 可視化儀表板
技能要求：
- 必備技能：Linux/容器部署
- 進階技能：監控規則設計
延伸思考：
- 合成監控與事後分析
- SLO/SLA 定義
- 黑盒+白盒混合監控

Practice Exercise（練習題）
- 基礎練習：HTTP 探測站點（30 分鐘）
- 進階練習：新增 Node Exporter 與告警（2 小時）
- 專案練習：完整監控堆疊（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：探測/告警可用
- 程式碼品質（30%）：配置清楚
- 效能優化（20%）：低誤報
- 創新性（10%）：儀表板設計

---

## Case #11: 備份與還原策略（Restic + 定期演練）

### Problem Statement（問題陳述）
業務場景：blog 資料需定期備份至異地，並確保可還原。
技術挑戰：資料一致性、排程、自動清理與加密。
影響範圍：資料遺失風險、合規。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無備份程序與排程。
2. 無加密與保留策略。
3. 未驗證還原。

深層原因：
- 架構層面：缺少異地備援。
- 技術層面：工具選型與腳本化不足。
- 流程層面：無演練（RPO/RTO 不明）。

### Solution Design（解決方案設計）
解決策略：使用 Restic 以加密方式備份至雲儲存（B2/S3），設排程與保留策略，建立還原演練流程。

實施步驟：
1. 備份腳本與排程
- 實作細節：Restic repo、環境變數、systemd timer
- 所需資源：Restic、B2/S3 帳戶
- 預估時間：2 小時
2. 還原演練
- 實作細節：定期抽樣還原、校驗
- 所需資源：測試目錄/容器
- 預估時間：2 小時

關鍵程式碼/設定：
```bash
# backup.sh
export RESTIC_REPOSITORY="b2:mybucket:blog"
export RESTIC_PASSWORD="Str0ngPass!"
export B2_ACCOUNT_ID=xxx
export B2_ACCOUNT_KEY=yyy

restic backup /var/www/blog /etc/nginx
restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
```

實際案例：自架 blog。
實作環境：Restic 0.16、B2。
實測數據：
改善前：RPO=不明、RTO=不明
改善後：RPO=24h；RTO=30 分鐘（演練）
改善幅度：可恢復性明確

Learning Points（學習要點）
核心知識點：
- RPO/RTO 與備份策略
- Restic 與保留策略
- 還原驗證
技能要求：
- 必備技能：Shell 與排程
- 進階技能：儲存成本與安全
延伸思考：
- 熱備與冷備搭配
- DB 一致性快照
- 版本控管與審計

Practice Exercise（練習題）
- 基礎練習：備份一個資料夾（30 分鐘）
- 進階練習：建立保留/清理策略（2 小時）
- 專案練習：備份+還原演練報告（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可備可還
- 程式碼品質（30%）：腳本穩健
- 效能優化（20%）：備份時間/成本控制
- 創新性（10%）：可觀測性/告警

---

## Case #12: 斷電韌性（UPS + NUT 自動關機）

### Problem Statement（問題陳述）
業務場景：家用電力不穩，伺服器需避免非預期斷電導致檔案損毀。
技術挑戰：UPS 通訊、門檻觸發、自動關機。
影響範圍：資料一致性、設備壽命。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 無 UPS 或未連結通訊。
2. 欠電池門檻設定。
3. 無自動關機流程。

深層原因：
- 架構層面：缺乏電力韌性。
- 技術層面：不了解 NUT/USB HID。
- 流程層面：無斷電演練。

### Solution Design（解決方案設計）
解決策略：配置 NUT 與 UPS，設定低電門檻自動關機；通電後自動開機。

實施步驟：
1. NUT 安裝與設定
- 實作細節：upsd/users/upsmon
- 所需資源：NUT、相容 UPS
- 預估時間：1 小時
2. 演練與自動開機
- 實作細節：測試觸發、BIOS 自動開機
- 所需資源：BIOS 設定
- 預估時間：1 小時

關鍵程式碼/設定：
```conf
# /etc/nut/ups.conf
[myups]
driver = usbhid-ups
port = auto
desc = "Home UPS"

# /etc/nut/upsmon.conf（節選）
MONITOR myups@localhost 1 monuser pass master
SHUTDOWNCMD "/sbin/shutdown -h now"
```

實際案例：自架 blog。
實作環境：NUT 2.8、APC/Online UPS。
實測數據：
改善前：非預期關機/月 2 次；資料風險高
改善後：受控關機；非預期關機 0 次
改善幅度：可靠性大幅提升

Learning Points（學習要點）
核心知識點：
- UPS 型號與通訊
- NUT 架構
- 關機門檻與演練
技能要求：
- 必備技能：Linux 服務配置
- 進階技能：電力與韌性規劃
延伸思考：
- 雙 UPS/雙電源冗餘
- 監控 UPS 指標
- 電池維護週期

Practice Exercise（練習題）
- 基礎練習：NUT 連線並讀值（30 分鐘）
- 進階練習：設門檻並演練（2 小時）
- 專案練習：撰寫斷電 SOP（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：受控關機
- 程式碼品質（30%）：設定正確
- 效能優化（20%）：誤觸發為零
- 創新性（10%）：監控整合

---

## Case #13: 內網以網域存取（Hairpin NAT/本地域名解析）

### Problem Statement（問題陳述）
業務場景：家中裝置需以 blog.example.com 存取站點，即使在內網也應可用；避免用內外不同網址。
技術挑戰：Hairpin NAT 或本地 DNS 覆寫、憑證一致性。
影響範圍：用戶體驗、應用相容性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 路由器不支援 NAT loopback。
2. DNS 未覆寫到內部 IP。
3. 憑證僅對外 IP 有效。

深層原因：
- 架構層面：未設 Split-horizon DNS。
- 技術層面：不理解 Hairpin 與 Host-override。
- 流程層面：無網域一致性策略。

### Solution Design（解決方案設計）
解決策略：啟用 NAT Reflection 或在 dnsmasq 中加入 host 覆寫，內網解析到私網 IP，HTTPS 憑證不變。

實施步驟：
1. 啟用 Hairpin/Reflection
- 實作細節：OpenWrt 反射設定
- 所需資源：路由器
- 預估時間：30 分鐘
2. DNS 覆寫
- 實作細節：dnsmasq 新增 host record
- 所需資源：OpenWrt
- 預估時間：30 分鐘

關鍵程式碼/設定：
```bash
# /etc/config/firewall（反射）
uci set firewall.@defaults[0].reflection='1'
uci commit firewall && /etc/init.d/firewall restart

# /etc/config/dhcp（DNS 覆寫）
config host
  option name 'blog'
  option dns '1'
  option ip '192.168.20.10'
  option domain 'example.com'
```

實際案例：內外一致訪問需求。
實作環境：OpenWrt 22.03。
實測數據：
改善前：內網以外網 IP 存取失敗；App 無法回環
改善後：內外一致可存取；憑證一致
改善幅度：體驗與維護成本降低

Learning Points（學習要點）
核心知識點：
- NAT loopback 與 Split DNS
- dnsmasq host-override
- 憑證與網域一致性
技能要求：
- 必備技能：路由/DNS 基礎
- 進階技能：多網段 DNS 規劃
延伸思考：
- 內外不同 IP 的快取策略
- 多 WAN/故障轉移時的解析策略
- 服務發現與 mDNS

Practice Exercise（練習題）
- 基礎練習：新增一條 host 覆寫（30 分鐘）
- 進階練習：配置並驗證 hairpin NAT（2 小時）
- 專案練習：設計小型 Split DNS（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：內外一致
- 程式碼品質（30%）：配置簡潔
- 效能優化（20%）：解析延遲低
- 創新性（10%）：策略設計

---

## Case #14: Blog 伺服器性能優化（Nginx 快取與壓縮）

### Problem Statement（問題陳述）
業務場景：blog 上線後需提升載入速度並減輕伺服器負載，確保峰值可用。
技術挑戰：靜態資源快取、壓縮、HTTP/2。
影響範圍：用戶體驗、SEO。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未啟用壓縮與快取。
2. 靜態資源未長快取。
3. 動態頁面沒快取層。

深層原因：
- 架構層面：缺少反向代理與快取。
- 技術層面：不熟 Nginx/Cache 控制。
- 流程層面：無壓測與基準。

### Solution Design（解決方案設計）
解決策略：啟用 gzip、cache-control；對動態（如 WordPress）加 fastcgi_cache；導入 HTTP/2。

實施步驟：
1. Nginx 壓縮與靜態快取
- 實作細節：gzip、expires、immutable
- 所需資源：Nginx
- 預估時間：1 小時
2. 動態快取與壓測
- 實作細節：fastcgi_cache、ab/wrk 測試
- 所需資源：wrk、ab
- 預估時間：2 小時

關鍵程式碼/設定：
```nginx
gzip on;
gzip_types text/css application/javascript application/json;

location ~* \.(css|js|png|jpg|svg)$ {
  expires 30d;
  add_header Cache-Control "public, max-age=2592000, immutable";
}

# WordPress fastcgi_cache 範例
fastcgi_cache_path /var/cache/nginx levels=1:2 keys_zone=FCGI:10m inactive=60m;
location ~ \.php$ {
  include fastcgi_params;
  fastcgi_pass unix:/run/php/php8.2-fpm.sock;
  fastcgi_cache FCGI;
  fastcgi_cache_valid 200 10m;
}
```

實際案例：自架 blog。
實作環境：Nginx 1.24、PHP-FPM 8.2。
實測數據：
改善前：TTFB ~450ms；p95 首畫面 1.8s
改善後：TTFB ~220ms；p95 首畫面 1.0s
改善幅度：延遲下降 ~50%，吞吐提升 2x

Learning Points（學習要點）
核心知識點：
- HTTP 快取與壓縮
- fastcgi_cache 與無狀態渲染
- 壓測方法
技能要求：
- 必備技能：Nginx 配置
- 進階技能：壓測與性能分析
延伸思考：
- CDN 前置
- HTTP/3 與 BBR
- 影像優化與懶載

Practice Exercise（練習題）
- 基礎練習：開啟 gzip 與靜態快取（30 分鐘）
- 進階練習：增加 fastcgi_cache（2 小時）
- 專案練習：壓測與調優報告（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：快取與壓縮生效
- 程式碼品質（30%）：配置正確
- 效能優化（20%）：TTFB/QPS 提升
- 創新性（10%）：CDN/HTTP3

---

## Case #15: IPv6 雙棧上線與防火牆

### Problem Statement（問題陳述）
業務場景：ISP 支援 IPv6，blog 站點需同時提供 v4/v6，以提升連線品質。
技術挑戰：前綴委派、RA、IPv6 防火牆與隱私位址。
影響範圍：可達性、未來相容。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未啟用 IPv6。
2. 無 AAAA 記錄。
3. 防火牆未設 v6 規則。

深層原因：
- 架構層面：缺少 v6 設計。
- 技術層面：不了解 PD/RA。
- 流程層面：無 DNS 與安全同步。

### Solution Design（解決方案設計）
解決策略：啟用 IPv6 前綴委派與 LAN RA；配置 v6 防火牆；DNS 新增 AAAA；伺服器綁定 v6。

實施步驟：
1. 啟用 IPv6 與 DNS
- 實作細節：ip6assign、AAAA 紀錄
- 所需資源：OpenWrt、DNS
- 預估時間：1 小時
2. 防火牆與測試
- 實作細節：僅放行 80/443；測試 v6 可達
- 所需資源：Ping6、curl -6
- 預估時間：1 小時

關鍵程式碼/設定：
```bash
# /etc/config/network
config interface 'wan6'
  option proto 'dhcpv6'

config interface 'lan'
  option ip6assign '64'

# /etc/config/firewall（v6 服務）
config rule
  option family 'ipv6'
  option src 'wan'
  option proto 'tcp'
  option dest_port '80 443'
  option target 'ACCEPT'
```

實際案例：自架 blog 提供 v6。
實作環境：OpenWrt、Nginx。
實測數據：
改善前：僅 IPv4；部分用戶走 CGNAT
改善後：v4/v6 雙棧；AAAA 可達
改善幅度：連線路徑更短、握手延遲降低

Learning Points（學習要點）
核心知識點：
- PD/RA 與 v6 地址規劃
- v6 防火牆與服務曝光
- DNS AAAA 與測試
技能要求：
- 必備技能：路由配置
- 進階技能：v6 安全策略
延伸思考：
- 僅 v6 + NAT64/DNS64
- 隱私地址與追蹤
- v6 下的 WAF/CDN

Practice Exercise（練習題）
- 基礎練習：啟用 AAAA（30 分鐘）
- 進階練習：設 v6 防火牆與測試（2 小時）
- 專案練習：完整雙棧部署（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：v6 可達與防火牆正確
- 程式碼品質（30%）：配置清楚
- 效能優化（20%）：握手延遲改善
- 創新性（10%）：v6 最佳化

---

## Case #16: Wi‑Fi 覆蓋與 VLAN SSID 分離（IoT/Guest）

### Problem Statement（問題陳述）
業務場景：有線端點有限，需以 Wi‑Fi 提供更多設備接入，同時隔離 IoT 與訪客，避免影響主網。
技術挑戰：多 SSID 到 VLAN 映射、漫遊、隔離策略。
影響範圍：安全、體驗、容量。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單 SSID 混合所有設備。
2. 無訪客隔離與帶寬控管。
3. 無 802.11k/v/r 優化。

深層原因：
- 架構層面：缺少無線與有線整合方案。
- 技術層面：不熟 SSID-VLAN 映射。
- 流程層面：無頻道與功率規劃。

### Solution Design（解決方案設計）
解決策略：建立 Main/IoT/Guest 三 SSID，映射到 VLAN 10/30/40；Guest 隔離，IoT 僅允許到雲端與特定控制器；規劃信道與功率。

實施步驟：
1. SSID 與 VLAN
- 實作細節：AP/路由器 SSID-VLAN 設定、交換器 Trunk
- 所需資源：支援 VLAN 的 AP/路由器
- 預估時間：2 小時
2. 隔離與優化
- 實作細節：Client Isolation、頻道規劃、帶寬限制
- 所需資源：AP 管理介面
- 預估時間：2 小時

關鍵程式碼/設定：
```bash
# OpenWrt /etc/config/wireless（節選）
config wifi-iface
  option ssid 'Home-Main'
  option network 'lan'   # VLAN 10
  option encryption 'sae-mixed'
config wifi-iface
  option ssid 'Home-IoT'
  option network 'iot'   # VLAN 30
  option isolate '1'
config wifi-iface
  option ssid 'Home-Guest'
  option network 'guest' # VLAN 40
  option isolate '1'
```

實際案例：有線稀缺，擴增 Wi‑Fi 載具。
實作環境：OpenWrt AP、管理型交換器。
實測數據：
改善前：單 SSID；IoT 與主網混雜
改善後：三 SSID；IoT/Guest 隔離；漫遊穩定
改善幅度：安全與體驗提升

Learning Points（學習要點）
核心知識點：
- SSID 到 VLAN 映射
- 訪客隔離與帶寬控制
- 信道/功率規劃
技能要求：
- 必備技能：AP/交換器設定
- 進階技能：Wi‑Fi 優化
延伸思考：
- 802.11k/v/r 導入
- Mesh 與有線回程取捨
- IoT ACL 精細控制

Practice Exercise（練習題）
- 基礎練習：建立第二個 SSID（30 分鐘）
- 進階練習：SSID-VLAN 映射與隔離（2 小時）
- 專案練習：完整三 SSID 部署（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：三 SSID 可用且隔離
- 程式碼品質（30%）：配置清楚
- 效能優化（20%）：干擾/漫遊優化
- 創新性（10%）：ACL/限速

---

案例分類
1. 按難度分類
- 入門級：Case 3, 8, 9, 12, 13
- 中級：Case 1, 2, 4, 5, 6, 7, 10, 11, 14, 15, 16
- 高級：無（可延伸至高級如 IDS/CDN/HA）

2. 按技術領域分類
- 架構設計類：Case 6, 7, 15, 16
- 效能優化類：Case 14
- 整合開發類：Case 1, 5, 9, 11
- 除錯診斷類：Case 2, 4, 10, 13
- 安全防護類：Case 7, 8, 12, 15

3. 按學習目標分類
- 概念理解型：Case 6, 7, 13, 15
- 技能練習型：Case 2, 3, 4, 8, 9, 12, 16
- 問題解決型：Case 1, 5, 10, 11, 14
- 創新應用型：Case 9, 14, 16（可延伸 HTTP/3、Mesh）

案例關聯圖（學習路徑建議）
- 先學基礎與實體層：Case 3（理線）→ Case 2（映射）→ Case 4（端接）
- 網路帶起來與分段：Case 6（VLAN）→ Case 7（DMZ 防火牆）→ Case 13（Hairpin/DNS）
- 讓站點上線與安全：Case 1（DDNS/NAT）→ Case 9（HTTPS）→ Case 8（硬化）
- 可用性與可靠性：Case 10（監控）→ Case 11（備份）→ Case 12（UPS）
- 擴展與體驗：Case 15（IPv6）→ Case 14（性能）→ Case 16（Wi‑Fi/IoT/Guest）
依賴關係：
- Case 2/4 完成後，Case 6 的 VLAN 分段更順利
- Case 6/7 為 Case 1/9 的安全基礎
- Case 10/11/12 為全局 SRE 能力建設
完整學習路徑：
- 物理層治理（3→2→4）
- 二三層網路（6→7→13）
- 服務上線（1→9→8）
- 可觀測性與韌性（10→11→12）
- 進階與優化（15→14→16）

以上 16 個案例均由原文情境推導，涵蓋從佈線到上線、安全、可觀測、效能與無線整合的完整實戰路徑。