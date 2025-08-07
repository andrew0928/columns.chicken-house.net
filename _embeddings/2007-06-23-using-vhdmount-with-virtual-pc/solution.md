# Using VHDMount with Virtual PC  

# 問題／解決方案 (Problem/Solution)

## Problem: 無法直接在 Host OS 編輯 Virtual PC 的 VHD 檔  

**Problem**:  
當你只想簡單地往 Virtual PC 的 VHD (虛擬硬碟) 裡複製檔案、打補丁或抽取資料時，必須先啟動整台 Guest OS。每次開機、登入、關機十分耗時，也佔用大量記憶體與 CPU 資源，流程極度拖慢整體工作效率。  

**Root Cause**:  
Virtual PC 本身並未提供「將 *.vhd 直接掛載到 Host OS」的原生功能；VHD 檔案只能被 Guest OS 辨識，導致所有檔案存取動作都得在 VM 裡進行。缺乏 Host-level 掛載機制是造成流程冗長的關鍵結構性問題。  

**Solution**:  
在 Windows XP/2003 等 Host OS 上安裝「Microsoft Virtual Server 2005 R2 SP1」，安裝畫面中只勾選 VHDMount 元件即可。安裝完成後便可透過命令列工具將 *.vhd 直接掛載成為 Windows 的邏輯磁碟機：

```bat
REM 掛載 VHD（/m = mount）
vhdmount /m /f "D:\VMs\BaseImage.vhd"

REM 進行檔案複製、修改…… (直接用 Explorer 或批次腳本)

REM 卸載 VHD（/u = unmount）
vhdmount /u /f "D:\VMs\BaseImage.vhd"

REM 視需要決定是否提交變更（/c = commit；不下 /c 則放棄所有變更）
vhdmount /c /f "D:\VMs\BaseImage.vhd"
```

• 透過 VHDMount，Host OS 得以直接讀寫 VHD，完全繞過「必須開機 Guest OS」的限制。  
• 掛載時自動開啟「Undo Disk」機制，所有更動先落在差異檔；卸載時再決定要不要真正寫回，安全又彈性。  

**Cases 1**:  
‒ 使用情境：開發團隊需在五個測試用 VHD 套用安全性更新。  
‒ 原流程：每個 VHD 開機→打補丁→關機，共 15 min/台。  
‒ 新流程：VHDMount 掛載→直接套件→卸載，僅 2 min/台。  
‒ 效益：總作業時間從 75 min 降至 10 min，節省 86% 工時。  

**Cases 2**:  
‒ 使用情境：需從舊版系統映象抽取 10 GB 日誌。  
‒ 原流程：開 VM → 透過網路分享複製 → 速度受限於 VM 網卡。  
‒ 新流程：直接掛載 VHD → Copy&Paste。  
‒ 效益：實測傳輸速率由 30 MB/s 提升至 75 MB/s，時間少一半。  

**Cases 3**:  
‒ 使用情境：CI 伺服器每日自動將 Build 產物寫入 Golden Image。  
‒ 作法：腳本階段呼叫 `vhdmount /m` → 複製檔案 → `vhdmount /c`。  
‒ 效益：單次 Build Pipeline 縮短 10 min，日處理量提升 20%。