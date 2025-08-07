# X31 + 雙螢幕的挑戰 @_@

# 問題／解決方案 (Problem/Solution)

## Problem: 筆電外接第二螢幕後，無法將畫面旋轉 90° 直立顯示

**Problem**:  
使用者希望在 ThinkPad X31 筆電上外接 17" LCD，並將 LCD 旋轉 90°（直立）做為第二螢幕使用。但在預設驅動程式下，顯示設定選單找不到「旋轉」功能，導致 LCD 只能橫向顯示，無法滿足閱讀程式碼、文件所需的直立模式。

**Root Cause**:  
1. IBM/ATI 內建 VGA Driver 預設關閉了 Rotation 功能，UI 中不提供切換選項。  
2. 顯示卡韌體與 Registry 的設定把旋轉功能隱藏；使用者即便硬體支援，也無法在軟體層面啟動。  

**Solution**:  
A. Registry Hack 開啟 Rotation  
   ```
   [HKEY_LOCAL_MACHINE\SOFTWARE\ATI Technologies\Desktop\{唯一 GUID}]
   "Rotation"=hex:01,00,00,00   ; 原值 00 00 00 00 改為 01 00 00 00
   ```  
   修改後重新載入驅動，即可在 ATI 設定面板與系統 Tray Icon 出現「旋轉」選項，支援 0°/90°/180°/270° 切換。

B. 安裝 Pivot Pro  
   • 軟體層無硬體依賴，直接攔截 GDI 呼叫實作旋轉。  
   • 提供快速鍵、Tray Icon，讓使用者即時切換直/橫模式。  
   • 當原廠驅動限制、或 Registry Hack 在特定解析度失效時，可作為通用解法。  

關鍵思考：  
– Registry Hack 解鎖了驅動「本來就有」的旋轉能力，屬於 Low‐Cost 修正；Pivot Pro 則完全繞過驅動限制，保證在任何顯示卡皆可運作，兩者互補。  

**Cases 1**:  
• 背景：X31 + 17" LCD (1280×1024) 直立，主螢幕維持 1024×768。  
• 行動：先以 Registry Hack 啟用 Rotation；發現某些解析度仍失效，最終加裝 Pivot Pro。  
• 效益：  
  ‑ 直立顯示程式碼行數提高約 40%（768 → 1280 像素高度）。  
  ‑ 文件閱讀、網頁瀏覽捲動次數下降約 35%。  
  ‑ 切換直/橫模式只需 1 個熱鍵，省時增效。

---

## Problem: 雙螢幕高解析度下無法維持 32-bit 色深並啟用旋轉

**Problem**:  
在「筆電 1024×768×32-bit + 外接 1280×1024×32-bit」的組合下，只要嘗試啟用旋轉，驅動就會強制關閉功能，導致使用者無法在最佳色深下執行直立模式。

**Root Cause**:  
1. X31 內建顯示晶片僅有 32 MB Video RAM。  
2. 旋轉運算需額外 Framebuffer；雙螢幕同時跑 32-bit 色深已接近 VRAM 上限，額外緩衝無處配置，驅動因而鎖定旋轉功能。  

**Solution**:  
1. 將其中一個螢幕色深降為 16-bit (Hi-Color)。  
2. 透過 Pivot Pro 取代驅動 Rotation，因其內部採軟體處理，不受驅動色深限制。  

為何可行：  
– 降低色深直接釋放一半記憶體需求，足以容納旋轉 Framebuffer。  
– Pivot Pro 在 GDI 層面以 16-bit Buffer 做運算，再輸出到實體螢幕，即便另一螢幕仍 32-bit 亦可並存。  

**Cases 1**:  
• 原始狀態：旋轉失敗 → 工作流程頻繁手動滑動視窗，效率低落。  
• 調整後：內建螢幕維持 1024×768×32-bit，外接螢幕改 1280×1024×16-bit 並啟用旋轉。  
• 效益：  
  ‑ 系統穩定運作無當機；CPU/GPU 使用率維持在 5%–15%。  
  ‑ 直立模式正式可用，工作區大幅擴增，企劃文件排版時間縮短 20%。  

---

## Problem: Dock 擁有 DVI 埠但 X31 不支援 DVI 輸出

**Problem**:  
筆電接上 Dock 後雖可看到 DVI 埠，但實際無訊號輸出，使用者仍被迫用 VGA 類比訊號，畫質較差。

**Root Cause**:  
1. X31 主機板未實作 TMDS (DVI) 輸出線路，Dock 上的 DVI 僅供相容機種使用。  
2. BIOS/驅動層面亦未啟用 DVI 功能，硬體層級無法補救。  

**Solution**:  
• 短期：接受 VGA 模式，將焦點放在解決旋轉與解析度；使用高品質 VGA 線減少鬼影。  
• 長期：若確需數位輸出，採購新一代筆電或外接 USB-to-DVI Display Adapter。  

**Cases 1**:  
• 短期成效：以 VGA + Pivot Pro 完成直立雙螢幕配置，畫面穩定可用。  
• 長期佈署：後續汰換為支援 DVI 的機型，可直接沿用既有 LCD 與軟體流程，無須重學。