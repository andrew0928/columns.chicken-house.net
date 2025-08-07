# 水電工日誌 #8. 家用網路設備整合, UniFi + NAS 升級之路

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這次家用網路升級專案的 5 大目標是什麼？
1. 網路設備整併：AP、Router、Switch、DVR 都換成 UniFi 全家桶，伺服器則集中到 Synology NAS。  
2. 網路基礎建設：以 VLAN 做區隔，確保家人上網品質、實驗區隔離，以及能彈性使用 HiNet 多組 PPPoE。  
3. 居家監控：汰換類比 DVR，改用 UniFi Protect + G3 系列 IPCAM，走 PoE 或 Wi-Fi。  
4. 網路服務：DNS（AdGuard Home）、VPN、Lab、Docker 服務等全部搬進 NAS 與 UDM-PRO。  
5. 邁向 10G 網路：骨幹先 10G／2.5G 混用，NAS 與 Switch 用 SFP+ 10G，桌機及行動端先升級到 2.5G。

## Q: 最終留下並持續服役的主要 UniFi 網路硬體有哪些？
• UDM-PRO (路由、防火牆、Controller、Protect NVR)  
• USW-Enterprise 24 PoE (Layer-3、12×2.5G + 2×10G SFP+、全埠 PoE+)  
• USW-Flex Mini (書桌小型 Switch)  
• UAP-AC-Lite ×2 及 UAP-AC-LR ×1 (Wi-Fi AP)

## Q: UniFi 1.12.22 韌體更新帶來哪些關鍵功能，使作者能同時撥兩條 PPPoE？
1. Port Remapping：UDM-PRO 的 Port 8/9/10/11 可自由指定為 LAN、WAN1、WAN2。  
2. Traffic Routes：新增 Policy Routing 介面，可為指定裝置或網段選擇走 WAN1 或 WAN2。  
因此作者得以讓 WAN1 用浮動 IP 給全家上網，WAN2 用固定 IP 專供 NAS 及對外服務。

## Q: 在 UniFi 環境下要做「父母監護 (Parental Control)」具體做法是什麼？
升級到 UniFi Network 7.x 後，使用 Settings → Firewall & Security → Traffic Management → Rules：  
1. 以「Category」直接選擇 Social Networks、Gaming 等 L7 應用類別；  
2. 以「Target」指定子女的裝置或 VLAN；  
3. 以「Schedule」勾選平日 22:00-24:00 等時間；  
4. Action 設為 Block。  
透過三維條件 (類別 / 裝置 / 時段) 就能圖形化完成時段上網管制。

## Q: 為何作者在啟用 UDM-PRO 的 Threat Management 時，PC→NAS 僅跑到約 1.4 Gbps？最終如何排除瓶頸？
Threat Management 進行 L7 封包檢測，CPU 使用率飆高，造成 Routing 僅剩約 1.4 Gbps。  
解法：  
1. 關閉 Threat Management 可瞬間恢復 9 Gbps 以上。  
2. 更根本的做法是把 VLAN Routing 移到 USW-Enterprise 24 PoE 的 Layer-3 Switch，由 Switch 就近處理跨 VLAN 流量，UDM-PRO 僅當 Router，用戶端即能穩定跑滿 2.5 Gbps。

## Q: 新的居家監控系統長怎樣？與舊式 DVR 相比優點為何？
• 硬體：UDM-PRO 內建 UniFi Protect + 3.5" HDD、攝影機採 G3-Flex (PoE) 與 G3-Instant (Wi-Fi + USB-C)。  
• 優點：  
  - 全網路／PoE 化，無同軸與獨立電源煩惱；  
  - Web 與 APP 介面友善，動態事件時間軸一目了然；  
  - Protect 提供 RTSP，可再交由 Synology Surveillance Station 當備份錄影。

## Q: 為什麼作者選擇「NAS + Docker」而非自組 PC 來跑家用服務？
1. NAS 先天具 RAID 與備份機制，資料可靠度高；  
2. 長時運作功耗低，比 PC Server 省電；  
3. DSM 內建 Docker、Reverse Proxy、Let's Encrypt，自架服務 (AdGuard Home、Bitwarden、FileZilla、Iperf3 等) 快速又易維護；  
4. 開發需求可再加裝 code-server (Web VS Code) 與 GitHub Pages 容器，直接在瀏覽器完成撰寫與部署。

## Q: 若家用網路想升級 10G、又使用 UDM-PRO，有哪些架構上的注意事項？
1. UDM-PRO 內部 8 ×1G Switch 與 10G SFP+ 是以 1 Gbps 匯流排串接，無法讓多個 1G 埠合計超過 1 Gbps 往 10G 口輸出。  
2. 若要真正跑滿 10G，應新增一台具 10G 上行且支援 L3 的 Switch (如 USW-Enterprise 系列)，將骨幹流量交由 Switch 負責，再用 10G 上行接回 UDM-PRO。  
3. 若只需兩個 10G 埠，可在 1.12.22 之後把第二個 SFP+ 也映射為 LAN 使用，省去額外 Switch，但無法同時兼顧大量 1G 用戶與高效防禦功能。

