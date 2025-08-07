# 水電工日誌 #7．事隔 12 年的家用網路架構大翻新

## 摘要提示
- 設備老化：12 年前佈建的 Router 與 Switch 因電容鼓起相繼損壞，促成全面換裝。
- UniFi AP：以企業級 UniFi-AP AC Lite 取代舊 Wi-Fi，解決訊號不穩與無縫漫遊需求。
- EdgeRouter-X SFP：選用支援 PoE 與硬體 Switch 的路由器，降低溫度並簡化佈線。
- GS116E Switch：改用可管控 VLAN／QoS 的 16 埠 Giga Switch，提高彈性與隔離度。
- VLAN 重新規劃：三組 VLAN 橫跨 Router 與 Switch，並以單線 Trunk 節省埠位。
- PoE 供電：AP 直接由 Router 供電，減少變壓器與插座需求。
- LACP 與 PPPoE：NAS 以 LACP 聚合雙埠增頻寬，工作 PC 可隨時 PPPoE 撥接測試。
- 效能驗證：LAN 內部傳輸可達 986 Mbps，WAN 測速亦逼近 100/40 M 帶寬上限。
- 經驗反思：透過網通領域知識（VLAN、Rule Engine）獲得軟體系統設計靈感。
- 自宅實踐：機櫃整併、Docker Controller 及多埠 Intel NIC，完成理想家庭網路。

## 全文重點
作者因一次停電意外發現家中 12 年前布建的 Router 與 Switch 因電容老化陸續報銷，遂決定趁雙十一將整套家用網路全面翻新。首先針對全家高度依賴的無線網路，導入兩台企業級 UniFi-AP AC Lite，配合 Docker 形式的 UniFi Controller，藉單一 SSID 實現漫遊並以 PoE 供電。其後以 Ubiquiti EdgeRouter-X SFP 取代舊 MikroTik Router，理由是支援硬體 Switch、PoE 及較低溫度；並搭配 Netgear GS116E Managed Switch，藉 VLAN、QoS、LACP 提升彈性。作者另外為桌機添購四埠 Intel i350-T4 Server NIC，以利未來 PPPoE 測試及頻寬聚合。

網路規劃方面，作者將家庭網路分成「家用 LAN」、「Server LAN」與「VDSL WAN」三組 VLAN，Router 與 Switch 以 Trunk 線互通，並將 UniFi AP 直接接到 Router 以確保 PoE 供電。如此一來，不僅節省實體連線與埠位，也讓關鍵線路和主機受到防火牆隔離。實測結果顯示，NAS 進行大型檔案傳輸可達 986 Mbps，透過 NAT 的對外速度亦近乎 100/40 M 滿載。開啟硬體 offload 後 Router 仍維持近 1 Gbps 轉發效能。

經歷近一個月的摸索與施工，作者完成機櫃整理與天花板 AP 安裝，並分享 VLAN 入門資源。最後，他從網路設備「以 Rule + Priority 解決複雜需求」的設計中汲取靈感，認為軟體開發亦可借鏡此種領域知識模型，提升系統彈性與可維護性。

## 段落重點
### 前言：停電觸發的全面換裝
作者回顧 12 年前重新裝修時布建的有線網路與機櫃，原本運作穩定，但一次計畫性停電暴露電容老化問題，Router 先暫時復活後再度死亡，Switch 也告報銷。趁雙十一無折扣的「敗家氛圍」以及家人對 Wi-Fi 穩定的期待，他決定大幅更新家用網路，同時記錄為久違的「水電工日誌」。

### 敗家有理 #1：UniFi AP
舊 ASUS RT-N16 與小米 Mini 組合不僅訊號衰減、只支援 2.4 G 或 100 M LAN，也缺乏 Mesh 漫遊。作者終於下手購買兩台 UniFi-AP AC Lite：企業級、吸頂設計、支援 PoE 與單 SSID 自動漫遊，再透過 Docker 部署 UniFi Controller 而免買 Cloud Key。社群口碑證實其穩定與易管理，堪稱「會自體繁殖」的 Wi-Fi 解決方案。

### 敗家有理 #2：Router + Switch
過去刷機後的 RT-N16 主責 Routing，而 Wi-Fi 功能交由其他 AP；本次改用 Ubiquiti EdgeRouter-X SFP。選擇理由包含內建 5 埠硬體 Switch、支援 24 V PoE、低溫不燙手與尚可的 WebUI。為了 VLAN 與 LAG 需求，再添購 Netgear GS116E 16 埠簡易網管 Switch，取代已故的 Belkin 24 埠非網管機，讓未來能以單一 Switch 靈活切分網段並節省連線。

### 敗家有理 #3：(亂入) Intel i350-T4
為提升桌機與虛擬化環境的穩定度與相容性，作者額外購得四埠 Intel i350-T4 Server NIC。多埠設計可同時用於家用 LAN 與直接接 VDSL Modem 撥 PPPoE 做測試，甚至可考慮進一步以 VLAN Tag 合併實體線路，為實驗與頻寬聚合預留彈性。

### 網路規劃：切割 VLAN
面對 NAS 隔離、防火牆、PoE、LACP 與測試環境等多重需求，作者設計三組 VLAN（紅：VDSL、綠：Server LAN、藍：Home LAN），並利用 EdgeRouter 的硬體 Switch 功能與 GS116E 的 VLAN Trunk，把 Router 與 Switch 之間的多色流量以單線互聯。如此節省至少兩條 Patch 線與多個埠位，同時確保 AP 供電、關鍵線路直達 Router、NAS 以 LACP 擴增頻寬，整體拓撲與埠位分配更具彈性與可維護性。

### 實測效能
作者以 6.8 GB 影片檔作 LAN 內傳輸測試，經 Router 轉發可跑出 986 Mbps；對外使用 HiNET 測速軟體，在 100/40 M 頻寬下實測 91/40 M，顯示 LAN 與 WAN 皆達瓶頸上限。參考資料指出，開啟硬體 offload 的 EdgeRouter-X SFP 在 LAN–LAN 與 LAN–WAN 皆能逼近 1 Gbps，故目前配置足以滿足家庭需求。

### 後記：從網路設備汲取軟體設計靈感
作者自承是網管門外漢，純粹因「阿宅的自嗨」而動手翻新，但在設定 VLAN、Routing、Firewall 的過程中體會到「領域知識萃取」的重要；網路設備以 rule＋priority 處理複雜需求的方式，讓他聯想到軟體開發中的 Rule Engine。藉由觀摩成熟系統的解決模式，他獲得了在軟體架構上重用規則、提高彈性與維運性的啟發，也鼓勵讀者多從不同資訊領域尋找靈感。