---
layout: synthesis
title: "水電工日誌 6. 機櫃設備展示"
synthesis_type: solution
source_post: /2007/10/05/electrician-diary-6-rack-equipment-showcase/
redirect_from:
  - /2007/10/05/electrician-diary-6-rack-equipment-showcase/solution/
---

以下內容基於提供的文章情境，萃取並重構出具教學價值的解決方案案例。每個案例均包含問題、根因、解法、步驟、關鍵設定/程式碼、實作參考、成效指標建議與練習評估。涉及的實測數據若非原文明確提供，以下以「可量測指標/建議目標」方式呈現，避免誤引。

## Case #1: 一坪雜物間改造成家庭機房與15U機櫃選型

### Problem Statement（問題陳述）
業務場景：家庭新居有一坪左右的小房間，不易善用。作者決定作為小型機房，集中安置網通設備、伺服器、交換器、PBX、DVR等，需兼顧放置、安全、散熱、走線與未來擴充。  
技術挑戰：在狹小空間內準確選型機櫃（高度、深度）、確保所有設備放得下且可維護，避免發生擺不進去或晃動不穩。  
影響範圍：設備放置安全、日後維護性、散熱與線材動線；若出錯，將造成返工與成本浪費。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 空間規劃不足：房間尺寸限制導致尺寸預估風險高。  
2. 設備清單不完整：未先盤點U位需求與深度，易誤買過小/過大的機櫃。  
3. 配件預估失準：層板/導軌缺少導致後續追加與拆裝返工。

深層原因：
- 架構層面：未建立「機櫃資產配置與容量規劃」方法論。  
- 技術層面：忽略設備深度、線纜彎折半徑、前後門開啟空間與底座輪腳水平調整。  
- 流程層面：缺少「上架清單→擺放圖→驗證」標準流程與驗收表。

### Solution Design（解決方案設計）
解決策略：先做容量與尺寸規劃（U位、深度、重量、散熱與電力預估），產出標準化的「機櫃擺放圖與設備清單」，選擇15U帶輪與支撐腳、內建PDU與防蟲穿線孔之機櫃，再按圖施工與驗收。

實施步驟：
1. 建立上架規劃
- 實作細節：盤點設備尺寸/重量/發熱，規劃U位，預留20%空位。  
- 所需資源：捲尺、設備規格書、Google Sheet/Excel。  
- 預估時間：0.5天

2. 選型與驗收
- 實作細節：選15U機櫃（帶輪、支撐腳、前壓克力門、可拆背門、內建PDU、防蟲孔），定位與水平調整。  
- 所需資源：15U機櫃、水平尺、防滑墊。  
- 預估時間：0.5天

3. 上架與布線初配
- 實作細節：先重後輕、下重上輕，先PDU/配線，再上重型設備、最後輕型；預留維護抽取空間。  
- 所需資源：層板/導軌、束帶、魔鬼氈。  
- 預估時間：1天

關鍵程式碼/設定：
```yaml
# rackplan.yaml — 機櫃配置與容量規劃範例
rack:
  height_u: 15
  depth_mm: 600
  pdu: true
  casters: true
  leveling_feet: true
  cable_entry: insect_proof_grommets
layout:
  - u: 1-2
    device: PDU (內建)
  - u: 3
    device: Patch Panel 24p
  - u: 4
    device: ADSL Modem
  - u: 5-6
    device: DVR (w/ IDE 160GB)
  - u: 7-8
    device: Analog PBX (3外線/8分機)
  - u: 9-10
    device: D-Link 24p Switch
  - u: 11-14
    device: 4U Server (NAT/Web/DNS/VPN/RAID1/Fax)
  - u: 15
    device: Spare (風道/擴充)
capacity:
  target_utilization: <=0.8
  front_clearance_mm: 600
  rear_clearance_mm: 600
  cable_bend_radius_mm: 30
```

實際案例：原文選15U機櫃，尺寸在預料中，避免「擺不進去」；內建PDU、可拆背門、防蟲穿線孔，品質穩固。  
實作環境：家用機房、一坪空間；設備如文列出。  
實測數據：  
改善前：無規劃，存在尺寸風險與返工風險  
改善後：一次到位，無「擺不進」問題  
改善幅度：以「返工次數=0」與「U位使用率≤80%」作為驗收目標

Learning Points（學習要點）
核心知識點：
- 機櫃容量規劃與U位配置  
- 前後散熱通道與設備深度評估  
- 上下重量分配與移動/調平

技能要求：
- 必備技能：尺寸量測、設備規格閱讀、配置圖繪製  
- 進階技能：散熱通道設計、重量安全評估

延伸思考：
- 未來增加UPS與線纜管理臂的擴充性  
- 機櫃深度不夠的風險  
- 如何用CFD/風速計進一步優化風道

Practice Exercise（練習題）
- 基礎練習：以自宅設備清單產出rackplan.yaml與擺放圖（30分鐘）  
- 進階練習：加入UPS與NAS，重算U位與散熱餘裕（2小時）  
- 專案練習：完成一次上架模擬與驗收表（8小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：是否覆蓋所有設備與擴充位  
- 程式碼品質（30%）：rackplan.yaml合理且可維護  
- 效能優化（20%）：散熱/走線/維護空間設計  
- 創新性（10%）：工具化（表單、模板）加分


## Case #2: 機櫃風扇噪音過大與散熱取捨

### Problem Statement（問題陳述）
業務場景：機櫃上方自帶雙風扇但運轉聲過大，家庭環境不適；作者選擇關閉風扇、移除背門改善噪音，同時以點對點風扇為HDD散熱。  
技術挑戰：如何在降噪與散熱間取得平衡，避免溫度過高導致故障。  
影響範圍：硬體壽命、家庭噪音舒適度、設備穩定性。  
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 機櫃風扇轉速高、噪音大。  
2. 小房間回音與共振放大噪音。  
3. 無分區導風，風扇效率低，以大噪音換少量散熱。

深層原因：
- 架構層面：未配置前進後出之風道與風隔板。  
- 技術層面：風扇選型未考量風量/靜壓/噪音曲線。  
- 流程層面：缺少溫度監控與噪音量測驗收。

### Solution Design（解決方案設計）
解決策略：關閉原風扇並替換為低噪音PWM風扇、建立前進後出風道，保留HDD定點主動散熱；同時以溫度與噪音為KPI驗收。

實施步驟：
1. 風道與風扇優化
- 實作細節：移除背門（改善排風）、在HDD位置加PWM靜音風扇，必要時加風隔板引導氣流。  
- 所需資源：Noctua/BeQuiet等低噪風扇、風隔板、矽膠減震釘。  
- 預估時間：0.5天

2. 監控與調速
- 實作細節：用lm-sensors+fancontrol依HDD/CPU溫度調速，設定目標溫度。  
- 所需資源：Linux、lm-sensors、fancontrol。  
- 預估時間：0.5天

關鍵程式碼/設定：
```bash
# 安裝與設定風扇調速
sudo apt install lm-sensors fancontrol
sudo sensors-detect
sudo pwmconfig   # 互動式對應PWM通道
sudo nano /etc/fancontrol
# 例：目標HDD溫度<40°C、CPU<70°C
```

實際案例：作者停用原風扇、拆背門，並以HDD點對點風扇維持硬碟<40°C。  
實作環境：Linux主機+4U機殼。  
實測數據：  
改善前：機櫃風扇噪音無法接受  
改善後：改用靜音風扇+風道優化，HDD溫度<40°C（文中提及）  
改善幅度：以dBA量測與HDD溫度為KPI（建議）

Learning Points（學習要點）
- 風量/靜壓/噪音曲線與風道設計  
- lm-sensors與fancontrol調速  
- 家庭機房的聲學考量

技能要求：
- 必備技能：硬體拆裝、Linux基本操作  
- 進階技能：風道規劃、噪音測試

延伸思考：
- 加裝進/出風溫度探頭  
- 門板與濾網引起的靜壓損耗  
- 以CFD或實測風速進一步優化

Practice Exercise（練習題）
- 基礎：配置fancontrol使HDD<40°C（30分鐘）  
- 進階：比較不同風扇噪音與溫度曲線（2小時）  
- 專案：設計完整風道與噪音驗收報告（8小時）

Assessment Criteria
- 功能完整性（40%）：溫度/噪音雙KPI達標  
- 程式碼品質（30%）：fancontrol參數清晰可維護  
- 效能優化（20%）：風道設計有效  
- 創新性（10%）：量測自動化與報表


## Case #3: 防蟲防塵穿線與機櫃進線孔管理

### Problem Statement（問題陳述）
業務場景：機櫃底部開防蟲線孔，需兼顧大量線纜穿入與阻止蟑螂螞蟻。  
技術挑戰：如何在不影響散熱與維護的前提下，實現密封與高可用的線纜進出。  
影響範圍：衛生與設備壽命、灰塵污染、維護便利性。  
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 機櫃進線孔與牆面穿線未密封。  
2. 線纜洞口過大、無毛刷或護圈。  
3. 灰塵與昆蟲可隨線進入。

深層原因：
- 架構層面：未規劃線纜進出與密封配件。  
- 技術層面：忽略電信/櫃體常用毛刷面板與護套。  
- 流程層面：缺少定期清潔與濾網維護流程。

### Solution Design（解決方案設計）
解決策略：使用帶毛刷的穿線面板與橡膠護圈、蜂巢濾網與可拆面板，建立標準化進線與密封方案。

實施步驟：
1. 進線孔整備
- 實作細節：量測孔徑，裝設毛刷面板與橡膠護圈，預留維護口。  
- 所需資源：毛刷面板、護圈、防塵濾網、束帶。  
- 預估時間：2小時

2. 密封驗收與維護
- 實作細節：以手電檢查縫隙、定期更換濾網；建立清潔SOP。  
- 所需資源：清潔工具、濾網耗材。  
- 預估時間：1小時

關鍵程式碼/設定：
```ini
# materials.ini — 防蟲防塵材料清單
[brush_panels]
size=1U, 2U

[grommets]
type=rubber_edge, split-grommet
diameter=10-50mm

[filters]
type=foam,honeycomb
change_cycle=3 months
```

實際案例：原文提及機櫃底層有三個防蟲線孔。  
實作環境：家用機櫃。  
實測數據：  
改善前：昆蟲與灰塵入侵風險  
改善後：孔位封堵、濾網管理  
改善幅度：以內部積塵量與入侵事件為KPI（建議）

Learning Points
- 櫃體穿線配件與密封工法  
- 濾網選型與更換周期  
- 維護SOP建立

Practice Exercise
- 基礎：安裝一組毛刷面板（30分鐘）  
- 進階：制定防塵更換與清潔SOP（2小時）  
- 專案：完成全櫃進線密封與驗收（8小時）

Assessment Criteria
- 完整性（40%）：所有孔位處理到位  
- 品質（30%）：無割傷線纜、無鬆動  
- 效能（20%）：維持散熱氣流  
- 創新（10%）：可拆式/模組化設計


## Case #4: 重型4U機殼安全上架與兒童誤觸防護

### Problem Statement（問題陳述）
業務場景：4U機殼裝滿硬碟與電源，重量>10kg，上下架有掉落風險；家中有小孩，需防止誤觸。  
技術挑戰：確保重物安全上架與固定、提升操作安全性與防呆。  
影響範圍：人身安全、設備損毀、家庭安全。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 無導軌/層板支撐，徒手上架危險。  
2. 櫃門未上鎖，小孩可能誤開操作。  
3. 沒有雙人作業或防墜措施。

深層原因：
- 架構層面：未配置承重導軌或層板。  
- 技術層面：缺乏扭力與承重評估。  
- 流程層面：欠缺「上架前檢查清單」與雙人作業規範。

### Solution Design
解決策略：採用承重導軌/層板、雙人上架、門鎖與告示；建立上架檢查清單，降低操作風險。

實施步驟：
1. 機構加固
- 實作細節：安裝承重導軌或層板，前後固定螺絲到位，使用防鬆墊圈。  
- 所需資源：導軌/層板、M6螺絲、防鬆墊。  
- 預估時間：2小時

2. 安全流程
- 實作細節：雙人抬運、戴手套、上架前清單；上鎖與張貼告示。  
- 所需資源：工作手套、警示貼、櫃門鎖。  
- 預估時間：1小時

關鍵程式碼/設定：
```text
# 上架前檢查清單（節錄）
[ ] 導軌/層板承重≥設備重量×1.5
[ ] 前後螺絲固定、扭力適中
[ ] 線纜鬆弛量足夠，無拉扯
[ ] 櫃門可正常上鎖與開關
[ ] 雙人確認「三步走」口令
```

實際案例：作者提及機殼很重、擔心掉落，採用「先鎖門」避免小孩誤觸。  
實作環境：家用15U機櫃+4U機殼。  
實測數據：  
改善前：存在掉落與誤觸風險  
改善後：加固+上鎖，風險降低  
改善幅度：以「事故=0、鬆動=0」為KPI（建議）

Learning Points
- 導軌與層板承重選型  
- 上架SOP與人因安全  
- 物理安全（門鎖/告示）

Practice Exercise
- 基礎：撰寫你專案的上架檢查清單（30分鐘）  
- 進階：為現有設備加裝導軌並驗收（2小時）  
- 專案：完成人因安全培訓與演練（8小時）

Assessment Criteria
- 完整性（40%）：清單與流程可落地  
- 品質（30%）：固定穩固、無共振  
- 效能（20%）：上架時間與失誤率  
- 創新（10%）：人因工程細節


## Case #5: HDD定點散熱與濾網防塵，維持<40°C

### Problem Statement
業務場景：4U機殼左側為HDD區，作者裝8cm風扇對HDD吹，內藏濾網；實測HDD溫度未超過40°C。  
技術挑戰：確保HDD在安全溫度、降低粉塵累積與噪音。  
影響範圍：資料安全、硬碟壽命、維護成本。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. HDD密集安裝、無足夠風量則溫度上升。  
2. 無濾網會快速積塵，影響散熱。  
3. 風扇直吹若無調速，噪音高。

深層原因：
- 架構層面：HDD氣流通道未系統設計。  
- 技術層面：缺少溫度監控與自動調速。  
- 流程層面：濾網清潔無周期化。

### Solution Design
解決策略：保留8cm定點風扇+濾網，加入SMART溫度監控與風扇調速，週期性清潔濾網。

實施步驟：
1. 溫度監控
- 實作細節：smartmontools監控HDD溫度，設告警<->調速。  
- 所需資源：smartmontools、fancontrol。  
- 預估時間：1小時

2. 防塵維護
- 實作細節：濾網每季清潔更換，建立維護記錄。  
- 所需資源：濾網耗材、記錄表單。  
- 預估時間：30分鐘/季

關鍵程式碼/設定：
```bash
sudo apt install smartmontools
sudo smartctl -A /dev/sdX | grep -i temperature
# 可搭配cron定期紀錄溫度，超標發mail或調速
```

實際案例：文中HDD風扇+濾網方案，實溫<40°C。  
實作環境：Linux主機+4U機殼+多HDD。  
實測數據：  
改善前：HDD溫度未知  
改善後：<40°C（文本）  
改善幅度：以<40°C與濾網阻塞率<30%為KPI（建議）

Learning Points
- SMART監控與硬碟溫度管理  
- 濾網阻塞與風量影響  
- 噪音與風量平衡

Practice Exercise
- 基礎：用smartctl讀HDD溫度（30分鐘）  
- 進階：寫一個溫度超標告警腳本（2小時）  
- 專案：設計HDD風道與濾網保養表（8小時）

Assessment Criteria
- 完整性（40%）：監控/調速/保養三位一體  
- 品質（30%）：腳本與紀錄規範  
- 效能（20%）：溫度/噪音均衡  
- 創新（10%）：可視化報表


## Case #6: 使用舊硬體建置NAT閘道與防火牆（iptables）

### Problem Statement
業務場景：作者以古董級ASUS P2B-DS主機擔任NAT分響器，並承載Web/DNS/VPN等對外服務。  
技術挑戰：在老舊硬體上維持穩定、安全的NAT/轉發與必要轉送。  
影響範圍：全家網路可用性與安全性、對外服務可達性。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. ADSL環境需要NAT與端口轉送。  
2. 老硬體資源有限需輕量穩定方案。  
3. 未啟用內核轉發或規則錯誤會造成無法上網。

深層原因：
- 架構層面：單機承載多服務，需嚴格邊界控制。  
- 技術層面：iptables規則與狀態追蹤配置不當。  
- 流程層面：缺少版本控管與備份。

### Solution Design
解決策略：採用Linux+iptables，啟用內核轉發、設立缺省拒絕策略、放行必要服務與端口轉送，版本化規則。

實施步驟：
1. 內核與規則初始化
- 實作細節：開IP轉發、設定NAT、設缺省DROP、狀態追蹤。  
- 所需資源：Debian/Ubuntu、iptables-persistent。  
- 預估時間：1小時

2. 端口轉送與服務放行
- 實作細節：Web/DNS/VPN/DVR等必要端口轉送與限速/限制來源。  
- 所需資源：iptables、文檔。  
- 預估時間：1小時

關鍵程式碼/設定：
```bash
# /etc/sysctl.d/99-nat.conf
net.ipv4.ip_forward=1
sudo sysctl -p /etc/sysctl.d/99-nat.conf

# 假設WAN介面ppp0，LAN介面eth0
WAN=ppp0; LAN=eth0; LANNET=192.168.1.0/24
iptables -F; iptables -t nat -F
iptables -P INPUT DROP; iptables -P FORWARD DROP; iptables -P OUTPUT ACCEPT
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
# 管理與必要服務
iptables -A INPUT -p tcp --dport 22 -s 192.168.1.0/24 -j ACCEPT
iptables -A INPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
# NAT
iptables -t nat -A POSTROUTING -o $WAN -j MASQUERADE
iptables -A FORWARD -i $LAN -o $WAN -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
# 端口轉送示例（DVR、VPN、Web）
iptables -t nat -A PREROUTING -i $WAN -p tcp --dport 8080 -j DNAT --to 192.168.1.10:80
iptables -t nat -A PREROUTING -i $WAN -p udp --dport 1194 -j DNAT --to 192.168.1.2:1194
iptables -A FORWARD -p tcp -d 192.168.1.10 --dport 80 -j ACCEPT
iptables -A FORWARD -p udp -d 192.168.1.2 --dport 1194 -j ACCEPT
```

實際案例：作者以單機承載NAT/Web/DNS/VPN等服務。  
實作環境：舊PC+Linux。  
實測數據：  
改善前：多機分散、管理複雜  
改善後：單機合併易維護  
改善幅度：以Ping loss、NAT吞吐、服務可達性為KPI（建議）

Learning Points
- IP轉發、狀態防火牆、端口轉送  
- 對外服務邊界最小化  
- 規則版本控管與備份

Practice Exercise
- 基礎：建立基本NAT上網（30分鐘）  
- 進階：加入DVR/ VPN端口轉送與來源限制（2小時）  
- 專案：用Ansible管理iptables規則（8小時）

Assessment Criteria
- 完整性（40%）：NAT/轉發/服務皆可用  
- 品質（30%）：規則清晰、有註解  
- 效能（20%）：吞吐與延遲合理  
- 創新（10%）：IaC自動化


## Case #7: 在同一台主機佈建Web/DNS與動態DNS

### Problem Statement
業務場景：作者同機承載Web/DNS服務，需要外網可達且域名可解析。  
技術挑戰：外IP不固定（ADSL），需動態DNS；安全暴露面最小化。  
影響範圍：對外服務可用性、安全性。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 住宅網路動態IP，域名需隨IP更新。  
2. DNS/Web同機需良好邊界控管。  
3. 轉送與NAT策略需一致。

深層原因：
- 架構層面：權威DNS與遞迴DNS隔離不足風險。  
- 技術層面：Nginx與BIND配置缺乏最小化暴露。  
- 流程層面：域名更新與憑證更新自動化缺乏。

### Solution Design
解決策略：使用ddclient更新動態DNS，Nginx作Web入口，BIND權威Zone最小化，採用自動化續期（如Let’s Encrypt）。

實施步驟：
1. 動態DNS
- 實作細節：ddclient定期更新A記錄。  
- 所需資源：ddclient、動態DNS供應商。  
- 預估時間：1小時

2. Web/DNS配置
- 實作細節：Nginx最小暴露；BIND僅對外權威Zone。  
- 所需資源：nginx、bind9。  
- 預估時間：1小時

關鍵程式碼/設定：
```nginx
# /etc/nginx/sites-available/site.conf
server {
  listen 80;
  server_name yourdomain.example.com;
  root /var/www/html;
  location / {
    try_files $uri $uri/ =404;
  }
}
```

```bind
; /etc/bind/db.yourdomain.example.com
$TTL 300
@ IN SOA ns1.yourdomain.example.com. admin.yourdomain.example.com. (
  2025010101 3600 600 1209600 300 )
@ IN NS ns1.yourdomain.example.com.
@ IN A 1.2.3.4
www IN A 1.2.3.4
```

```ini
# /etc/ddclient.conf
protocol=dyndns2
use=web, web=checkip.dyndns.org
server=members.dyndns.org
login=yourlogin
password=yourpass
yourdomain.example.com
```

實際案例：文中提及提供Web/DNS對外服務。  
實作環境：Linux主機+ADSL。  
實測數據：  
改善前：IP變動導致域名失效  
改善後：動態DNS自動更新  
改善幅度：DNS停頓時間≤TTL（建議）

Learning Points
- 動態DNS工作機制  
- 權威DNS與Nginx基本配置  
- TTL與更新策略

Practice Exercise
- 基礎：設好ddclient與Nginx首頁（30分鐘）  
- 進階：BIND建立一個權威zone（2小時）  
- 專案：加入Let’s Encrypt自動續期（8小時）

Assessment Criteria
- 完整性（40%）：域名解析與網站可用  
- 品質（30%）：配置清晰與安全  
- 效能（20%）：TTL與更新延遲  
- 創新（10%）：自動化程度


## Case #8: VPN遠端存取（WireGuard）整合家庭服務

### Problem Statement
業務場景：作者提供VPN服務供遠端維護與內網資源存取（含DVR）。  
技術挑戰：在住宅網路上實作低負擔且安全的VPN。  
影響範圍：遠端維護、安全隔離。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 需安全訪問內網與DVR，不宜直接曝露。  
2. 舊硬體需要輕量協定。  
3. NAT環境需端口轉送。

深層原因：
- 架構層面：遠端管理與監控網段需隔離。  
- 技術層面：金鑰管理與路由宣告不當將引發風險。  
- 流程層面：憑證/金鑰輪換與撤銷缺失。

### Solution Design
解決策略：採用WireGuard（輕量、效能高），僅開放UDP 51820，使用允許清單宣告內網路由，DVR透過VPN存取。

實施步驟：
1. 伺服端安裝與設定
- 實作細節：wg-quick up，生成金鑰、宣告內網路由。  
- 所需資源：wireguard-tools。  
- 預估時間：1小時

2. 客戶端配置與端口轉送
- 實作細節：在iptables放行UDP 51820並DNAT到WG主機。  
- 所需資源：iptables。  
- 預估時間：30分鐘

關鍵程式碼/設定：
```ini
# /etc/wireguard/wg0.conf (server)
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = <server_private_key>

[Peer]
# notebook
PublicKey = <peer_public_key>
AllowedIPs = 10.10.0.2/32, 192.168.1.0/24
```

實際案例：文中提及提供VPN對外服務。  
實作環境：Linux主機+ADSL+NAT。  
實測數據：  
改善前：需開多個對外端口  
改善後：單端口VPN進入再存取內網  
改善幅度：暴露面減少（開放端口數下降）為KPI（建議）

Learning Points
- WireGuard基本概念與金鑰管理  
- 允許清單與路由宣告  
- 與iptables/NAT整合

Practice Exercise
- 基礎：建一組WG伺服器與1客戶端（30分鐘）  
- 進階：透過VPN訪問內網DVR（2小時）  
- 專案：金鑰輪換與撤銷機制（8小時）

Assessment Criteria
- 完整性（40%）：VPN連線與內網可達  
- 品質（30%）：配置最小權限  
- 效能（20%）：延遲與吞吐  
- 創新（10%）：自動化管理


## Case #9: RAID1檔案伺服器（mdadm + Samba）

### Problem Statement
業務場景：作者在同一主機提供家中共用資料夾，使用RAID1以確保資料安全。  
技術挑戰：在舊硬體上實作軟體RAID1與檔案分享，兼顧穩定與相容。  
影響範圍：家庭資料可用性、備援能力。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 單顆硬碟故障風險高。  
2. 家庭多裝置需要共享。  
3. 檔案分享與權限管理需簡化。

深層原因：
- 架構層面：存取與備援策略未制定。  
- 技術層面：mdadm監控與Samba權限。  
- 流程層面：缺備份與失效演練。

### Solution Design
解決策略：以mdadm組RAID1並掛載至共享路徑，Samba發布家用共享；建立巡檢與重建流程。

實施步驟：
1. 建陣列與掛載
- 實作細節：mdadm建立RAID1、fstab掛載、啟用監控郵件。  
- 所需資源：mdadm、smartmontools。  
- 預估時間：1小時

2. Samba共享
- 實作細節：簡單用戶/來賓存取、目錄權限。  
- 所需資源：samba。  
- 預估時間：1小時

關鍵程式碼/設定：
```bash
sudo mdadm --create /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc
sudo mkfs.ext4 /dev/md0
sudo mkdir -p /srv/share
echo "/dev/md0 /srv/share ext4 defaults 0 2" | sudo tee -a /etc/fstab
sudo mount -a
```

```ini
# /etc/samba/smb.conf（節錄）
[family]
   path = /srv/share
   browseable = yes
   read only = no
   guest ok = yes
```

實際案例：文中提及RAID1用於家中共享資料夾。  
實作環境：Linux主機+多HDD。  
實測數據：  
改善前：單盤風險高  
改善後：RAID1容錯1盤  
改善幅度：以MTTR/可用性與重建時間為KPI（建議）

Learning Points
- mdadm基本操作與監控  
- Samba存取控制  
- 故障演練與資料備援

Practice Exercise
- 基礎：建立RAID1並共享（30分鐘）  
- 進階：模擬單盤故障與重建（2小時）  
- 專案：加上備份到外接碟/雲（8小時）

Assessment Criteria
- 完整性（40%）：RAID1正常共享  
- 品質（30%）：權限與掛載配置  
- 效能（20%）：讀寫效能合理  
- 創新（10%）：備援策略


## Case #10: 家用傳真伺服器整合（HylaFAX/mgetty+sendfax）

### Problem Statement
業務場景：作者同機整合傳真功能，降低實體傳真機需求。  
技術挑戰：在Linux上用類比數據機提供收發傳真與歸檔。  
影響範圍：辦公流程數位化、紙本成本。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. 需要集中管理傳真收發。  
2. 兼容類比線路與PBX。  
3. 軟硬體驅動與穩定性。

深層原因：
- 架構層面：通訊與存儲整合。  
- 技術層面：數據機驅動、AT指令相容。  
- 流程層面：收發通知與歸檔工作流。

### Solution Design
解決策略：使用HylaFAX或mgetty+sendfax，設定收件夾與電郵通知，與PBX對接分線。

實施步驟：
1. 安裝與測試
- 實作細節：確認modem /dev/ttyS*，測AT、收發測試。  
- 所需資源：外接/內接modem、mgetty/HylaFAX。  
- 預估時間：2小時

2. 工作流與通知
- 實作細節：到件自動轉PDF、寄Email；發件回執。  
- 所需資源：郵件系統。  
- 預估時間：1小時

關鍵程式碼/設定：
```bash
sudo apt install mgetty mgetty-fax
sudo nano /etc/mgetty+sendfax/mgetty.config
# port ttyS0
#  speed 38400
#  data-only no
```

實際案例：文中主機同時擔負傳真機功能。  
實作環境：Linux+類比電話線/總機。  
實測數據：  
改善前：紙本流程繁雜  
改善後：數位化歸檔、Email通知  
改善幅度：以紙張節省量與處理時效為KPI（建議）

Learning Points
- 類比modem與FAX軟體  
- 接到PBX分機/外線  
- 數位歸檔流程

Practice Exercise
- 基礎：完成一份收/發測試（30分鐘）  
- 進階：PDF自動化歸檔與Email通知（2小時）  
- 專案：與家用NAS歸檔整合（8小時）

Assessment Criteria
- 完整性（40%）：收發成功與歸檔  
- 品質（30%）：配置與通知可靠  
- 效能（20%）：處理時延  
- 創新（10%）：與業務流程整合


## Case #11: 舊Panasonic總機退場與簡易類比PBX導入

### Problem Statement
業務場景：舊Panasonic總機設備老舊、手冊缺失、專用話機昂貴且功能難以使用；作者改採簡易類比PBX（3外線/8內線）。  
技術挑戰：以低成本實現多外線/多分機、轉接/保留等功能。  
影響範圍：家庭多點電話配置、桌面空間、可用性。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 舊系統可用性差、學習成本高。  
2. 專用話機成本過高。  
3. 維護資料缺失（手冊/設定）。

深層原因：
- 架構層面：專屬硬體綁定不利維護與擴充。  
- 技術層面：功能操作靠專用燈號與按鍵，替代性差。  
- 流程層面：無文件化與培訓。

### Solution Design
解決策略：導入簡易類比PBX，使用標準話機，透過指令碼（如#11/#12選線、##保留）達成基本交換功能，降低成本與學習難度。

實施步驟：
1. 佈線與分機規劃
- 實作細節：RJ11外線到PBX、各房間分機配線，標籤化。  
- 所需資源：PBX、打線工具、標籤機。  
- 預估時間：0.5天

2. 操作指令與告示
- 實作細節：常用操作貼在話機旁，家庭成員培訓。  
- 所需資源：操作小卡。  
- 預估時間：1小時

關鍵程式碼/設定：
```csv
# extension_map.csv
ext,location,notes
101,LivingRoom,主話機
102,Study,#
103,MasterBR,#
201,Fax,接PBX外線2
```

實際案例：文中改採簡易PBX，普通話機即可用，靠指令操作轉接/選線。  
實作環境：類比PBX+RJ11。  
實測數據：  
改善前：多台話機佔空間且難操作  
改善後：分機化、桌面清爽、易用  
改善幅度：以桌面話機數量與誤操作率下降為KPI（建議）

Learning Points
- PBX基本拓撲（外線/內線）  
- 類比話機可用性與成本  
- 操作手冊與培訓

Practice Exercise
- 基礎：畫一張PBX拓撲圖（30分鐘）  
- 進階：制定分機編碼與操作卡（2小時）  
- 專案：完成整屋分機布線與標籤（8小時）

Assessment Criteria
- 完整性（40%）：外線/內線可用  
- 品質（30%）：標籤與文件化  
- 效能（20%）：操作學習曲線  
- 創新（10%）：擴充構想（語音留言等）


## Case #12: 類比線路REN超載與通話雜音治理

### Problem Statement
業務場景：先前每處擺兩台話機，導致類比線路電力推不動、有雜音；導入PBX後改善。  
技術挑戰：控制REN（Ringer Equivalence Number）負載與佈線品質。  
影響範圍：通話品質、可靠性。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 同一路線掛太多話機，REN超載。  
2. 線材品質或接頭不良。  
3. 平行接線導致反射與干擾。

深層原因：
- 架構層面：未使用PBX集中管理分機。  
- 技術層面：不清楚REN總負載限制（多為REN 5上限）。  
- 流程層面：缺佈線驗收與REN預算。

### Solution Design
解決策略：以PBX集中外線，分機各自掛載，控制每回路REN總和，校正接線與接頭品質。

實施步驟：
1. REN盤點與整改
- 實作細節：盤點話機REN值、計算並控制在上限內。  
- 所需資源：話機規格書、測試電話。  
- 預估時間：1小時

2. 佈線驗收
- 實作細節：替換劣化線材、壓接RJ11、消除並聯長支路。  
- 所需資源：壓線鉗、線測。  
- 預估時間：1小時

關鍵程式碼/設定：
```yaml
# ren_calc.yaml
loop_1_max: 5.0
devices:
  - name: phone_living
    ren: 0.8
  - name: phone_study
    ren: 0.8
  - name: fax
    ren: 1.0
total: 2.6 # <= loop_1_max -> OK
```

實際案例：文中指出多機並掛造成雜音與推不動，導入PBX後解決。  
實作環境：家用類比線路。  
實測數據：  
改善前：雜音明顯  
改善後：分機化、通話清晰  
改善幅度：以主觀SNR提升與斷線率為KPI（建議）

Learning Points
- REN負載概念  
- 類比線佈線原則  
- PBX在品質治理的作用

Practice Exercise
- 基礎：計算自家REN總和（30分鐘）  
- 進階：重做不良接頭與測試（2小時）  
- 專案：制定REN預算與接線標準（8小時）

Assessment Criteria
- 完整性（40%）：REN計算與合規  
- 品質（30%）：佈線與接頭品質  
- 效能（20%）：通話品質改善  
- 創新（10%）：記錄與SOP


## Case #13: 專用DVR取代PC錄影與保留期估算

### Problem Statement
業務場景：先前以PC錄影，軟體與驅動問題頻發且與日常使用衝突；改用專用DVR（含160GB IDE）並啟用偵測動態錄影。  
技術挑戰：提升穩定性並用有限容量達成合理保留期與遠端存取。  
影響範圍：監控可靠性、維運成本。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. PC兼用導致資源競爭與崩潰。  
2. 驅動/軟體穩定性差。  
3. 連續錄影容量壓力大。

深層原因：
- 架構層面：專用型與通用型方案定位不清。  
- 技術層面：動態偵測與碼率配置不當。  
- 流程層面：遠端查看與回放流程不順暢。

### Solution Design
解決策略：導入獨立DVR與動態錄影，計算保留期；提供PC軟體與Web瀏覽存取（需JRE）。

實施步驟：
1. DVR部署與容量規劃
- 實作細節：設定動態偵測、碼率/解析度，估算保留期。  
- 所需資源：DVR、硬碟。  
- 預估時間：1小時

2. 網路與存取
- 實作細節：設定固定IP與端口，透過VPN或限制來源存取。  
- 所需資源：路由/防火牆。  
- 預估時間：1小時

關鍵程式碼/設定：
```text
# 保留期估算（示例）
days = (容量GB * 0.93) / (碼率Mbps * 0.125 * 3600 * 24) # 連續錄影
# 以160GB、1.5Mbps計：~9.4天；動態錄影視觸發比例延長
```

實際案例：文中改用專用DVR，160GB、動態觸發、軟體/網頁皆可看。  
實作環境：DVR+IDE硬碟。  
實測數據：  
改善前：PC軟體/驅動不穩  
改善後：專機穩定、可多日保留  
改善幅度：以宕機次數與可回放天數為KPI（建議）

Learning Points
- 專用DVR與NVR取捨  
- 動態偵測與碼率影響  
- 保留期計算

Practice Exercise
- 基礎：設定動態偵測與時間區段（30分鐘）  
- 進階：測不同碼率對保留期影響（2小時）  
- 專案：建立回放與匯出流程SOP（8小時）

Assessment Criteria
- 完整性（40%）：錄影/回放/匯出皆可用  
- 品質（30%）：碼率與觸發配置  
- 效能（20%）：保留期達標  
- 創新（10%）：自動報表


## Case #14: DVR網頁端JRE相容性與安全沙箱化

### Problem Statement
業務場景：DVR提供Web介面以Java Applet播放，需安裝JRE；現代瀏覽器不支援NPAPI，兼容與安全成為挑戰。  
技術挑戰：在現代環境安全地使用舊式瀏覽技術。  
影響範圍：遠端監看便利性與資安風險。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. Java Applet（NPAPI）被主流瀏覽器移除。  
2. 直接在主機安裝舊JRE有風險。  
3. DVR廠商軟體相容性有限。

深層原因：
- 架構層面：舊設備協定封閉。  
- 技術層面：缺乏替代（RTSP/HTML5）。  
- 流程層面：未建立「受限環境」操作規範。

### Solution Design
解決策略：將舊JRE與支援NPAPI的舊版瀏覽器關在VM或容器中，僅透過VPN訪問DVR，限制網段與權限。

實施步驟：
1. 受限環境建立
- 實作細節：建立Windows 7/Ubuntu + Firefox ESR 52 + JRE 8u老版本的VM，封網僅允許到DVR/VPN。  
- 所需資源：VirtualBox/VMware、舊版瀏覽器安裝檔。  
- 預估時間：1-2小時

2. 網路與存取控制
- 實作細節：VM防火牆白名單、只讀快照，僅VPN後訪問DVR。  
- 所需資源：本地防火牆、VPN。  
- 預估時間：1小時

關鍵程式碼/設定：
```bash
# Ubuntu裝IcedTea-Web（JNLP替代），視DVR支援而定
sudo apt install icedtea-netx
# 若必須老瀏覽器，建議使用VM並封網
```

實際案例：文中指出Web端需JRE才能看。  
實作環境：DVR + Web Applet。  
實測數據：  
改善前：新版瀏覽器無法播放/高風險  
改善後：受限VM可用且風險隔離  
改善幅度：以攻擊面縮小與變更「僅VPN可達」為KPI（建議）

Learning Points
- 舊技術相容策略（隔離/沙箱）  
- VM網路白名單與快照回滾  
- 以VPN縮小暴露面

Practice Exercise
- 基礎：建立一個受限VM（30分鐘）  
- 進階：VM內完成DVR瀏覽與回放（2小時）  
- 專案：VM硬化與操作SOP（8小時）

Assessment Criteria
- 完整性（40%）：在VM內可用  
- 品質（30%）：網路與權限最小化  
- 效能（20%）：使用流暢度  
- 創新（10%）：自動快照回滾流程


## Case #15: 24埠Fast Ethernet交換器的成本/效能取捨

### Problem Statement
業務場景：作者採購二手D-Link 24埠FE交換器（網咖退場），未上GBE以控成本。  
技術挑戰：在FE限制下確保家用負載可用與未來擴充。  
影響範圍：檔案傳輸、監控串流、上網體驗。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. GBE成本高。  
2. 家用平均吞吐低，FE足夠。  
3. 二手設備可能老化。

深層原因：
- 架構層面：核心/接入分層未規劃。  
- 技術層面：無VLAN/QoS（若為非管理型）。  
- 流程層面：缺乏效能基準與監測。

### Solution Design
解決策略：保留FE，將高吞吐需求放在同段、避開核心瓶頸；以iperf基準測試，為未來升級GBE預留布線。

實施步驟：
1. 網段與負載規劃
- 實作細節：DVR、家用分享與NAT靠近同交換器，減少跨段流量。  
- 所需資源：網路拓撲圖。  
- 預估時間：1小時

2. 基準測試與監測
- 實作細節：iperf測FE吞吐，日後監測利用率。  
- 所需資源：iperf3。  
- 預估時間：30分鐘

關鍵程式碼/設定：
```bash
# iperf3測試
iperf3 -s  # 伺服端
iperf3 -c 192.168.1.x -t 30
```

實際案例：作者使用二手D-Link 24p FE交換器。  
實作環境：家用網路+ADSL。  
實測數據：  
改善前：不確定FE是否足夠  
改善後：以基準測試佐證可用性  
改善幅度：以鏈路利用率<70%為KPI（建議）

Learning Points
- 成本/效能權衡  
- 基準測試方法  
- 升級路線規劃

Practice Exercise
- 基礎：做一次iperf3測試（30分鐘）  
- 進階：繪製負載熱點與拓撲優化（2小時）  
- 專案：提出GBE升級計畫與成本估算（8小時）

Assessment Criteria
- 完整性（40%）：拓撲與測試完整  
- 品質（30%）：資料可信/可複現  
- 效能（20%）：瓶頸定位  
- 創新（10%）：升級策略


## Case #16: 結構化佈線與配線架（Patch Panel）標準化

### Problem Statement
業務場景：作者使用配線架集中網路線；需標準化打線與標籤，避免「一坨線」難維護。  
技術挑戰：T568B打線與標籤、配線與終端測試。  
影響範圍：維護效率、故障定位。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 線材無標籤、端到端不可追。  
2. 打線標準不一致。  
3. 無測試驗收。

深層原因：
- 架構層面：缺乏佈線標準。  
- 技術層面：T568B色序不熟。  
- 流程層面：缺驗收與文檔。

### Solution Design
解決策略：採用TIA/EIA-568B標準，標籤化每個port，完成打線後以測試器驗收，建立配線對照表。

實施步驟：
1. 打線與測試
- 實作細節：按T568B色序打線，使用測試器確認。  
- 所需資源：打線工具、測試器。  
- 預估時間：2小時

2. 標籤與文檔
- 實作細節：生成port位號對照表，貼標籤。  
- 所需資源：標籤機、表格工具。  
- 預估時間：1小時

關鍵程式碼/設定：
```text
# T568B色序（針腳1->8）：白橘、橘、白綠、藍、白藍、綠、白棕、棕
```

```csv
# patchpanel_label.csv
port,room,walljack
1,Study,A1
2,Living,A2
...
```

實際案例：文中提及配線架存在。  
實作環境：家用有線網路。  
實測數據：  
改善前：線路不可追溯  
改善後：端到端對照清晰  
改善幅度：以問題定位時間縮短為KPI（建議）

Learning Points
- T568B標準  
- 測試與驗收  
- 文檔與標籤

Practice Exercise
- 基礎：完成1U 24埠打線與測試（30分鐘）  
- 進階：建立對照表與貼標籤（2小時）  
- 專案：繪製全屋佈線圖（8小時）

Assessment Criteria
- 完整性（40%）：全部端口合格  
- 品質（30%）：標籤清晰耐用  
- 效能（20%）：快速定位能力  
- 創新（10%）：數位化台帳


## Case #17: ADSL橋接模式與伺服器PPPoE撥接，消除雙重NAT

### Problem Statement
業務場景：ADSL Modem位於機櫃，NAT閘道在Linux主機；若Modem同時做NAT，會形成雙重NAT。  
技術挑戰：確保外部可達（Web/DNS/VPN/DVR）且路由清楚。  
影響範圍：連線穩定、端口轉送與VPN。  
複雜度評級：中

### Root Cause Analysis
直接原因：
1. Modem路由/NAT與主機NAT疊加。  
2. 端口映射複雜且易錯。  
3. 外網可達性下降。

深層原因：
- 架構層面：邊界設備責任未界定。  
- 技術層面：PPPoE/橋接知識不足。  
- 流程層面：變更未文檔化。

### Solution Design
解決策略：將ADSL Modem調為橋接，Linux主機PPPoE撥接取得公網IP，由主機統一NAT與端口轉送。

實施步驟：
1. 調整Modem為Bridge
- 實作細節：登入Modem管理改為Bridge，關閉其DHCP/NAT。  
- 所需資源：Modem後台帳密。  
- 預估時間：30分鐘

2. Linux撥接與路由
- 實作細節：pppoeconf或systemd-networkd建立ppp0，更新iptables使用ppp0。  
- 所需資源：pppoe套件。  
- 預估時間：30分鐘

關鍵程式碼/設定：
```bash
sudo apt install pppoeconf
sudo pppoeconf
# 成功後介面為ppp0，配合Case #6 iptables使用ppp0為WAN
```

實際案例：文中ADSL Modem在交換器上方，NAT在伺服器。  
實作環境：ADSL+Linux。  
實測數據：  
改善前：雙重NAT時端口轉送凌亂  
改善後：單一NAT、路由清晰  
改善幅度：以端口可達率與故障率下降為KPI（建議）

Learning Points
- 橋接與路由模式差異  
- PPPoE基本操作  
- 單一NAT的可維護性

Practice Exercise
- 基礎：把測試Modem設為Bridge（30分鐘）  
- 進階：主機PPPoE並完成端口轉送（2小時）  
- 專案：變更記錄與回滾方案（8小時）

Assessment Criteria
- 完整性（40%）：撥接成功、對外服務可達  
- 品質（30%）：變更紀錄與回滾  
- 效能（20%）：延遲/丟包  
- 創新（10%）：監控告警


## Case #18: 家用機櫃物理存取控制與誤觸防護

### Problem Statement
業務場景：家中有小孩，作者於操作時先鎖門避免誤觸；家庭機房需基本物理安全。  
技術挑戰：在家中實現低成本的物理存取控制與變更管理。  
影響範圍：安全、誤關機、設備毀損。  
複雜度評級：低

### Root Cause Analysis
直接原因：
1. 櫃門可輕易開啟。  
2. 無告示或權限提醒。  
3. 維運時無變更控管。

深層原因：
- 架構層面：物理安全未納入設計。  
- 技術層面：缺少簡易感測與告警。  
- 流程層面：變更/巡檢流程缺乏。

### Solution Design
解決策略：櫃門上鎖、警示告示、變更記錄；可加磁簧開關+蜂鳴器或Home Assistant監控開門事件。

實施步驟：
1. 物理與提示
- 實作細節：加裝門鎖、鎖孔管理、警示貼紙。  
- 所需資源：機櫃鎖、標示。  
- 預估時間：1小時

2. 開門偵測與記錄
- 實作細節：磁簧開關+Raspberry Pi GPIO，推送到Telegram。  
- 所需資源：磁簧、Pi、簡易腳本。  
- 預估時間：2小時

關鍵程式碼/設定：
```python
# door_alert.py (Raspberry Pi)
import RPi.GPIO as GPIO
import requests, time
SENSOR=17
TOKEN="bot_token"; CHAT_ID="chat_id"
GPIO.setmode(GPIO.BCM); GPIO.setup(SENSOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
while True:
    if GPIO.input(SENSOR)==GPIO.LOW:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                     params={"chat_id":CHAT_ID,"text":"Rack door opened"})
        time.sleep(5)
    time.sleep(0.2)
```

實際案例：作者平時會先鎖門避免誤觸。  
實作環境：家庭機櫃。  
實測數據：  
改善前：誤觸風險  
改善後：上鎖+告警  
改善幅度：以誤觸事件數=0為KPI（建議）

Learning Points
- 物理安全層的重要性  
- 簡易IoT告警  
- 變更/巡檢流程

Practice Exercise
- 基礎：製作警示貼與鎖具清單（30分鐘）  
- 進階：Pi+磁簧偵測告警（2小時）  
- 專案：制定家庭機房物理安全SOP（8小時）

Assessment Criteria
- 完整性（40%）：鎖具/告示/告警三合一  
- 品質（30%）：告警可靠與低誤報  
- 效能（20%）：回應時效  
- 創新（10%）：與Home Assistant整合


--------------------------------
案例分類

1) 按難度分類
- 入門級：
  - Case 3 防蟲防塵穿線
  - Case 4 重型4U安全與上鎖（基礎版）
  - Case 5 HDD散熱與濾網
  - Case 11 簡易PBX導入
  - Case 12 REN與雜音治理
  - Case 15 FE交換器取捨
  - Case 16 配線架標準化
  - Case 18 物理存取控制
- 中級：
  - Case 1 一坪機房與機櫃選型
  - Case 2 機櫃散熱與噪音平衡
  - Case 6 NAT閘道（iptables）
  - Case 7 Web/DNS/動態DNS
  - Case 8 VPN（WireGuard）
  - Case 9 RAID1+Samba
  - Case 13 DVR與保留期
  - Case 17 ADSL橋接PPPoE
- 高級：
  - Case 14 DVR JRE相容與沙箱化（老技術安全隔離）

2) 按技術領域分類
- 架構設計類：Case 1, 2, 13, 15  
- 效能優化類：Case 2, 5, 15  
- 整合開發類：Case 6, 7, 8, 9, 10, 17  
- 除錯診斷類：Case 12, 16  
- 安全防護類：Case 6, 8, 14, 18

3) 按學習目標分類
- 概念理解型：Case 1, 12, 13, 15  
- 技能練習型：Case 3, 5, 16, 17  
- 問題解決型：Case 2, 6, 7, 8, 9, 10, 11  
- 創新應用型：Case 14, 18

--------------------------------
案例關聯圖（學習路徑建議）
- 建議先學：
  - Case 1（整體機櫃與空間規劃，為一切基礎）
  - Case 16（配線與標準化，避免後續維運困難）
  - Case 15（了解現有交換器效能邊界）
- 依賴關係：
  - Case 17（ADSL橋接PPPoE）→ Case 6（NAT/iptables）→ Case 7（Web/DNS）→ Case 8（VPN）→ Case 13/14（DVR遠端存取）
  - Case 2/5（散熱噪音/HDD溫度）依賴Case 1（機櫃規劃）
  - Case 9（RAID1+Samba）可獨立於網路，但建議在Case 6完成後以利權限與安全
  - Case 11/12（PBX/REN）依賴Case 16（配線標準與標籤）
  - Case 18（物理安全）可在Case 1後即刻實施
- 完整學習路徑：
  1) Case 1 → 16 → 15（空間+佈線+效能邊界）
  2) Case 17 → 6 → 7 → 8（網路邊界與服務可達）
  3) Case 13 → 14（監控與相容性安全）
  4) Case 2 → 5（散熱與噪音優化）
  5) Case 9 → 10（檔案與傳真整合）
  6) Case 11 → 12（PBX部署與品質治理）
  7) Case 3 → 18（物理與環境安全）
  全部完成後，形成「家用機房即小型企業級」的完整實戰體系。