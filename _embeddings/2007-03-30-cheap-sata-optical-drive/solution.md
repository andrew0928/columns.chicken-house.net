# 便宜的 SATA 光碟機

# 問題／解決方案 (Problem/Solution)

## Problem: 新主機板沒有原生 IDE，舊光碟機無法直接使用  

**Problem**:  
• DIY 多年的舊電腦使用 IDE 介面光碟機。  
• 近年 Intel 965 (ICH8) 晶片組開始取消原生 IDE Port，只剩額外第三方 IDE 控制晶片。  
• 外掛 IDE 控制晶片的驅動程式相容度差、常出現抓不到裝置或系統藍畫面，造成安裝 OS、讀片備份都很麻煩。  

**Root Cause**:  
1. 晶片組規格演進：Intel 自 9xx 系列起大幅減少 / 移除 PATA (IDE) 支援，鼓勵全面轉向 SATA。  
2. 外掛 IDE 控制器僅靠 PCI-E / PCI 通道轉接，驅動程式品質與微碼更新跟不上主板 BIOS 與 OS 版本，導致不穩定。  
3. 使用者仍沿用舊式 IDE 光碟機，介面不相容、驅動又不穩定，形成使用瓶頸。  

**Solution**:  
改採「原生 SATA 介面 DVD-ROM」。  
步驟／邏輯：  
1. 直接利用主板原生 SATA Port，完全省去第三方 IDE 控制晶片與驅動。  
2. 透過拍賣平台 (Y拍) 搜尋「SATA DVD-ROM」，找到 BenQ DW1640 OEM 版 (型號被標示為 PHILIPS DROM6316)；  
   ‑ 單價＋運費兩台共約 NTD 1,000。  
3. 安裝方式：  
   ```text
   ‑ SATA Signal Cable → 主板 SATA Port  
   ‑ SATA Power Cable  → 電源供應器原生 SATA Power 端子
   ```  
   無傳統 4-pin 電源、無 Master/Slave 跳線，減少裝線錯誤。  
4. BIOS 與 Windows Device Manager 均可直接辨識，不需額外 Driver。  

為何能解決 Root Cause：  
• 徹底避開 PATA → 不再受限外掛 IDE 晶片及驅動。  
• SATA 熱插拔與序列傳輸設計，提升傳輸穩定度。  
• OEM 光碟機成本已大幅降低，在不增加預算下即可升級。  

**Cases 1**:  
背景：作者兩台桌機皆更新到 965 晶片組主板，安裝 Windows 時常因 IDE 光碟機抓不到而卡關。  
採取方案：一次購買兩台 SATA DVD-ROM (NTD 1,000) 安裝於兩台電腦。  
成效：  
• OS 安裝與讀片完全正常，未再出現驅動衝突。  
• 機殼理線更簡潔；比原本 IDE 排線減少 30% 佔空間。  
• 省下排查 IDE Driver 問題的時間 ≒ 2-3 小時／台。  
• 每台電腦硬體升級成本僅 NTD 500，即可恢復光碟讀取功能。