# Network Bridge in Windows 2003 ─ 把 100 Mbps 與 GBE 無痛整併

# 問題／解決方案 (Problem/Solution)

## Problem: 檔案傳輸速度受限於 100 Mbps，備份／燒片流程效率低落

**Problem**:  
家中的 Desktop PC 需要定期向 Server 取得 ISO 映像檔再燒成 DVD。  
• 100 Mbps 網路下，單次複製 ISO 約 10 分鐘  
• 燒錄與 Verify 各需 10 分鐘  
整體流程動輒 30 分鐘以上，嚴重拖慢工作節奏。

**Root Cause**:  
1. 現有網路骨幹僅 100 Mbps，頻寬成為主要瓶頸。  
2. 雖然主機板內建 1 GbE (Marvell)，但因過去穩定性疑慮而被 BIOS 關閉。  
3. 伺服器端既有 NAT、RRAS、VPN、DHCP 等設定皆依賴單一 100 Mbps 介面，若改掛到 1 GbE 需大幅重建設定，維運成本高。

**Solution**:  
啟用內建 1 GbE NIC，並在 Windows 2003 Server 端使用「Software Network Bridge」將  
• Intel 82559 100 Mbps NIC  
• Marvell 1 GbE NIC  
合併為單一邏輯介面。  
步驟摘要：  
```text
1. BIOS → Enable Marvell GBE LAN
2. Windows 2003 → Network Connections
   → Select兩張網卡 → 右鍵「Bridge Connections」
3. 保留原有 TCP/IP, RRAS, DHCP 等設定於 Bridge 介面
4. Desktop PC 端亦啟用 1 GbE 並直接以 Cat5e/6 對接 Server
```
關鍵思考：  
• Bridge 後在 OS 層僅出現 1 個 Network Interface，既有服務設定完全不需調整。  
• 100 Mbps 與 1 GbE 可同時存在，舊設備仍能以 100 Mbps 存取，Desktop⇄Server 走 1 GbE。  

**Cases 1**: 傳輸效能  
• 單一 ISO 複製時，1 GbE 連線利用率可達 30 %（≈ 240 Mbps）；對比先前 100 Mbps 幾近 90 % 利用率，傳輸時間從 10 分鐘降至約 3 分半，整體流程縮短 66 %。  
• 若同時從不同磁碟讀取檔案，可飆升至 60 %（≈ 480 Mbps），顯示瓶頸已轉移至 Disk I/O。  

**Cases 2**: 維運便利性  
• RRAS、DHCP、VPN 等服務皆無須重新設定路由或 DHCP Scope，避免維運風險。  
• 既有 100 Mbps Client 不受影響，仍透過 Intel NIC 存取網路。  

---

## Problem: 想導入 1 GbE 卻避免額外子網與 Routing 複雜度

**Problem**:  
若為 1 GbE 裝置獨立規劃新子網：  
• 需調整 DHCP、靜態路由、Firewall Rule  
• 家中僅少量裝置，新增子網顯得小題大作  
此複雜度讓升級遲遲無法執行。

**Root Cause**:  
1. 傳統做法是一個子網對應一種媒介速度。  
2. 在小型環境中，Routing Table 與 DHCP Scope 的修改成本遠大於硬體成本。  

**Solution**:  
利用 Windows 2003 內建「軟體橋接」技術，把兩張不同速率的 NIC 強制整併於同一 Broadcast Domain，保持單一子網，無須改動任何 Layer-3 設定。  

**Cases 1**: 設計簡化  
• 不額外設定 Static Route／VLAN，所有裝置仍存取 192.168.x.x/24。  
• DHCP Server 不需新增作用域，避免 IP 漏水或設定錯誤。  

**Cases 2**: 部署時間  
• 從「決定升級」到「完成啟用」僅花 <30 分鐘（包含 BIOS 設定與 Windows 重開機）。  

---

## Problem: Marvell 1 GbE Driver 在高負載環境不穩定

**Problem**:  
過去在公司 Virtual Server 2005 上使用內建 Marvell 1 GbE：  
• 大流量運作 1~2 週後網路無故中斷  
• 需手動 Disable / Enable 介面才恢復  
導致 Production VM 網路斷訊風險。

**Root Cause**:  
Marvell 驅動程式在重負載或長時間運行下，可能觸發未知錯誤（資源洩漏 / IRQ 問題），造成 NIC 進入異常狀態；與 Intel PRO 系列相比，Firmware 與 Driver 成熟度較低。

**Solution**:  
1. 關鍵服務仍綁定在 Intel 82559 (100 Mbps) NIC，確保穩定性。  
2. 1 GbE 主要用於 Desktop⇄Server 的檔案傳輸，流量與連線數相對有限；即使偶發重啟 NIC，也不影響對外服務。  
3. 若流量成長，可再添購 Intel 1 GbE 卡替換。  

**Cases 1**: 折衷運行三個月觀察  
• 家用環境峰值流量低於 200 Mbps，Marvell NIC 未再出現斷線。  
• 關鍵外部 VPN / DNS / DHCP 流量仍走 Intel 100 Mbps，服務可用度 100 %。  

**Cases 2**: 成本效益  
• 無需立即採購新 Intel 1 GbE，延後 CAPEX，待未來確定需要再投資。  

---