# [敗家] 對岸的迷你 PC (i5-5250U)，當自用 server 的好選擇

# 問題／解決方案 (Problem/Solution)

## Problem: 家用 NAS 效能不足，市售 NUC/ITX 組合又貴又弱

**Problem**:  
• 想在家裡長期跑 Docker（WordPress、其他服務），原本的 NAS 效能嚴重不足；  
• 舊 NB 當 server 噪音大、效能低、壽命有限；  
• 市售 NUC / mini-ITX 方案不是規格太弱 (Atom/Celeron/i3、單通道記憶體、單 LAN)、就是價格過高，無法取得「小體積、省電、雙通道 RAM、雙 LAN」的平價設備。

**Root Cause**:  
1. 主流 NUC 產品聚焦在 HTPC 與輕薄辦公市場，成本壓力導致規格精簡。  
2. 自組 mini-ITX 雖可自由搭配，但殼＋板＋電源＋散熱體積偏大、功耗較高，且成本難壓到 6–7K (NTD) 以下。  
3. NAS SoC 設計側重 I/O 與低功耗，不適合大量容器化運算。

**Solution**:  
• 改鎖定大陸白牌無風扇 mini-PC（i5-5250U，雙 DDR3L SO-DIMM、雙 Giga LAN、mSATA×2），整機含運約 NTD $(6100)。  
• 安裝流程  
  1. 自備 2×4 GB DDR3L + 2.5" HDD/SSD；  
  2. 以 USB 隨身碟安裝 Windows 10 / Linux Server；  
  3. 透過 BIOS (&lt;DEL&gt; 進入，&lt;F11&gt; 選開機裝置) 完成啟動設定；  
  4. 確認 LAN/Wi-Fi/USB 等核心元件可由 OS 自帶驅動辨識。  
• 為何可解問題  
  - i5-5250U ≈ 2C/4T、TDP 15 W，效能與功耗取得平衡；  
  - 雙通道記憶體插槽、雙 Giga LAN 滿足容器與網路服務需求；  
  - 全鋁散熱外殼＋無風扇設計解決長開機箱噪音與灰塵問題；  
  - 成本遠低於同等級品牌 NUC／ITX 組合。

**Cases 1**:  
情境：將原本跑在 Synology NAS 的 WordPress＋MySQL 移至新機 Docker。  
結果：  
  – 首次頁面回應時間由 2.3 s ↓ 1.1 s (-52%)；  
  – 佔用功耗 14 W (待機)／26 W (Docker-compose up 全載)，較舊 NB 省 40%。  

**Cases 2**:  
情境：利用雙 LAN 做內外網分流（eth0 對外、eth1 走內部 10G 交換機）。  
結果：文件同步檔案傳輸峰值 110 MB/s，與桌機內網實測幾乎無差；  
強化了家中 GitLab Runner 與 NAS 備份效率。  

---

## Problem: 主機板 SATA 埠失效，無法掛 2.5" HDD

**Problem**:  
裝機測試時，主板唯一的 SATA 埠始終偵測不到 2.5" HDD，導致系統碟無法安裝。

**Root Cause**:  
• 大陸白牌產線 QC 不嚴；  
• 低價出清可能包含功能不全的料件，故 SATA Port 故障機率偏高。

**Solution**:  
1. 自購 mSATA → SATA 轉接卡 (NTD $100)；  
2. DIY SATA-Power 線 (小 4P → SATA) 供電；  
3. 將 2.5" HDD 插在 mSATA 插槽透過轉卡使用。  
關鍵思考：主板仍有兩個良品 mSATA，繞開壞掉的 SATA Port 即可恢復儲存功能。

**Cases 1**:  
• 完成改裝後，CrystalDiskMark 連續讀寫 105 / 102 MB/s，與直接接板載 SATA 差距 <3%；  
• 省去退貨等待時間，系統可如期上線。  

---

## Problem: 可能收到 Engineering Sample (ES) CPU，影響穩定度與日後維修

**Problem**:  
網友普遍反映同型號白牌機常用 ES CPU 充數，ES 版可能存在穩定性、無保障保固或鎖頻差異。

**Root Cause**:  
廠商為壓低成本，採購 Intel 工程樣片 (ES) 料件組裝；ES 晶片不在 Intel 售後體系內。

**Solution**:  
• 下單前與賣家溝通：註明「需正式版 SRxxx 編號 CPU」；  
• 若只剩 ES，要求免費升級上層型號 (i7-5600U) 或換店家；  
• 收貨時以 CPU-Z 檢查 stepping/標籤，確認非「Qxxx」字首 ES 編號。  

**Cases 1**:  
透過事先溝通，最終拿到量產版 i5-5250U (SR23Z)，跑 48 hr stress test 無掉核心/熱當，BIOS 也無頻率鎖定異常。  

---

## Problem: 無線網卡與隨機附件規格被偷料或遺漏

**Problem**:  
1. 標示 300 M 無線實際只附 150 M 1T1R Dell 1703；  
2. 主機板專用 SATA-Power 線漏寄，導致開機受阻。  

**Root Cause**:  
• 賣家為壓低總價，採用低階/拆機無線卡；  
• 出貨流程不完善，小配件容易漏包裝。

**Solution**:  
A. 無線網卡  
  – 若需要高速/藍牙，一次性購入 Intel Dual-Band AC-7260，約 NTD $700，規格 ac 867 M + BT4.0。  
B. 電源線  
  – 光華商場購買小 4P → SATA Power 公頭，十餘元自製。  
關鍵思考：在低價白牌市場，將「必要零件自備、非必要降級可接受」設定為預期，可大幅降低等待及退換貨成本。

**Cases 1**:  
• 換裝 Intel AC-7260 後，5 GHz link rate 867 Mbps，iperf 實測 500+ Mbps，適合未佈 LAN 的客廳 TV Box。  
• DIY 電源線後，整機安裝時間從拖延 1 週 → 30 分鐘內搞定。

---

## Problem: 傳統 PC/NB 當長開 Server 風扇噪音與灰塵問題

**Problem**:  
• 宿舍/家中放置舊 PC 或 NB 當伺服器時，風扇 24×7 運轉噪音大；  
• 長期吸塵導致散熱片積灰，溫度飆升易當機，後續維護麻煩。

**Root Cause**:  
風扇屬機械零件，磨損＋灰塵堆積為最常見故障來源；NB 散熱結構對連續高負載並不友善。

**Solution**:  
• 採用全鋁無風扇外殼 mini-PC：  
  – 整體外殼即為散熱片，無任何轉動零件；  
  – i5-5250U TDP 15 W，風道需求低。  
• Stress-test（CPU-Z 100% 2 h）溫度穩定在 58 °C，不到 85 °C 保護門檻。  

**Cases 1**:  
• 放入機櫃後實測背景噪音從 42 dB (A) ↓ 無可感差異；  
• 三個月未開機殼除塵，內部仍乾淨，維護成本大幅降低。

---

