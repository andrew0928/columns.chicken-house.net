# Next Ten Years...

# 問題／解決方案 (Problem/Solution)

## Problem: 十年老舊伺服器難以擴充且隨時面臨當機風險

**Problem**:  
家用伺服器使用十年的 ASUS P2B-DS 主機板與 IDE 硬碟架構，面臨以下困境：  
1. 市面上已難以購買容量經濟的 IDE 硬碟。  
2. 嘗試加裝 PCI 4-port SATA 卡因 BIOS 過於老舊而無法開機。  
3. 硬碟剩餘空間長期低於 5%，只要搬移大檔案或 SQL Server Express 資料庫做大量 I/O，網站就會掛掉。  
4. 臨時向同事借用過渡機，一開機就耗電 150W，以其處理能力而言非常不划算。

**Root Cause**:  
1. 核心硬體（主機板、BIOS）過時，只支援 IDE，導致儲存設備無法升級。  
2. 系統碟容量小且老化，I/O 效能低落，造成應用程式（SQL Express）崩潰。  
3. 老舊硬體功耗高，散熱環境差，維護成本上升。  

**Solution**:  
一次性整換為「低功耗、易擴充」的新伺服器組態：  

```plain
CPU  : Intel Core2 Quad Q9300  (四核心入門款，功耗與溫度低於 Q6600)
RAM  : DDR2-800 2GB x4         (共 8GB)
MB   : ASUS P5E-VM DO (Intel Q35) ― 內建 VGA、六個 SATA、四條 RAM
HDD  : WD GreenPower 750GB x3  ― 低溫、省電，空閒時自降 7200→5400rpm
PSU  : 330W 高效率電源
NIC  : 另加一張網卡即可
OS   : Windows Server 2003 x64 全新安裝
```

關鍵思考：  
1. Q35 商用晶片組內建 VGA，免去「伺服器為了偶爾維修而插獨顯」的雞肋。  
2. WD GP 系列以降轉速節能，配合 3 顆 750GB 提供 >2TB 空間並降低溫度。  
3. 四核心 Q9300 在相同功耗下比舊 P6 架構帶來數倍效能，避免 I/O 與 CPU 打架。  
4. 330W 高效率 PSU + 全機待機約 70W、滿載 <100W，相對舊機省電約 35%~50%。  

**Cases 1**:  
‧ 交換前：IDE 硬碟 160GB×2，剩餘空間 <5%，夜間備份時 SQL 2005 Express 當機，網站掛掉平均每週 1 次。  
‧ 交換後：SATA 磁碟陣列 2.25TB，可用空間 >70%，全月零當機；SQL 無 I/O Freeze。  

**Cases 2**:  
‧ 交換前：老舊主機板 + PCI 裝置 4 張（網卡×2、USB 擴充、VGA），待機 150W。  
‧ 交換後：單板整合 VGA ‑ 減 1 張；USB/SATA 皆內建 ‑ 減 1 張；待機 70W，滿載 95W；每月省電 ≒ (150-95)W × 24h × 30d = 39.6kWh。  

**Cases 3**:  
‧ 交換前：搬移檔案／清硬碟常造成網站離線，必須深夜維護。  
‧ 交換後：大檔傳輸不再拖垮 SQL，無需額外 IP 分享器做「移機期間備援」；真正移機時間縮短至 1 晚完成。  

---

## Problem: 不支援 Windows Server 2003 x64 的 USB Modem 驅動

**Problem**:  
新伺服器改裝 Windows Server 2003 x64 後，原有 USB Modem 無相容驅動，收發傳真功能中斷。

**Root Cause**:  
1. 老舊 USB Modem 廠商已停止更新，僅提供 32-bit 驅動。  
2. Windows Server 2003 x64 驅動簽章要求嚴格，強制阻擋未簽名驅動安裝。  

**Solution**:  
短期：向社群詢問、收集「仍提供 2003 x64 驅動的 USB Modem 型號」。  
長期：評估改用網路型 Fax-to-Mail 服務，移除實體 Modem 依賴，避免 OS 版本升級造成驅動斷層。  

**Cases 1**:  
‧ 在論壇調查後鎖定兩款市售中階 USB Modem (含 2003 x64 WHQL 驅動)，預計下單替換。  
‧ 過渡期間以同事寄放之 IP 分享器的 Fax-to-Email 功能暫代，確保文件接收不中斷。