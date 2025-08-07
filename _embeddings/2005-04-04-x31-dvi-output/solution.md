# X31 + DVI output

# 問題／解決方案 (Problem/Solution)

## Problem: ThinkPad X31 想要輸出高畫質 DVI 到外接 LCD，卻只有類比 VGA

**Problem**:  
使用 ThinkPad X31 筆電 (內建 ATI 類比 VGA) 時，若想在家裡接一台支援 DVI 的 LCD 螢幕，就無法享受到數位訊號的畫質與穩定度。

**Root Cause**:  
1. X31 本體沒有 DVI 介面，底座 (dock) 也僅提供一組標準 PCI 插槽，沒有額外的 DVI。  
2. 內建顯示晶片功能受限，只能輸出類比 VGA。

**Solution**:  
1. 在底座唯一的 PCI 插槽插上一張低價 nVidia FX5200 (128 MB RAM) PCI 顯示卡 (具備 DVI 介面)。  
2. 安裝對應驅動程式並將 LCD 接在顯示卡的 DVI 接孔。  
3. OS 內切換為外接顯卡輸出，即可得到全數位畫面。  

為何可解決 Root Cause:  
PCI 顯示卡等於幫 X31 新增一套顯示子系統，提供原本缺乏的 DVI 介面，同時運算能力也比內建晶片強。

**Cases 1 (效益)**:  
• 螢幕畫質明顯提升，抖動與鬼影消失。  
• 128 MB 顯示記憶體帶來較佳的 2D/3D 效能，操作與觀影更流暢。  

---

## Problem: PCI 插槽被顯示卡佔用後，原本的 1394 (FireWire) 介面消失

**Problem**:  
原本透過 PCI 1394 卡連接 DV 攝影機與外接硬碟，插上顯示卡後就沒有插槽可用，1394 功能中斷。

**Root Cause**:  
X31 底座只有 1 個 PCI 插槽，裝上顯示卡後便無法再同時插 1394 卡。

**Solution**:  
改買一張便宜的 PCMCIA 1394 卡：  
1. 保留顯示卡於 PCI。  
2. 將 1394 功能移到 PCMCIA，繼續支援 DV/外接硬碟傳輸。  

為何可解決 Root Cause:  
PCMCIA 插槽與 PCI 插槽彼此獨立，可在不犧牲 DVI 的前提下恢復 FireWire 連線能力。

**Cases 1 (效益)**:  
• 照常進行 DV 影片擷取以及 1394 外接硬碟資料備份。  
• 硬體成本低，僅需添購一張 PCMCIA 卡即可。

---

## Problem: 插上 PCI 顯示卡後無法熱插拔，休眠後拔機失效

**Problem**:  
換上 PCI 顯示卡後，筆電必須「完整關機」才能將筆電從底座拔離；先休眠 (Hibernate) 再拔會導致 OS 裝置狀態錯亂。

**Root Cause**:  
1. PCI 匯流排裝置在 OS 內被視為「關鍵系統裝置」。  
2. Windows 在休眠狀態下無法安全移除該裝置，醒來時找不到裝置會產生錯誤。  

**Solution**:  
暫行作法  
1. 認命地採取「完全關機→拔離→開機」流程。  
2. 或在「硬體設定檔 (Hardware Profile)」中建立「攜帶外出」情境，手動停用外接顯示卡再休眠 (需重開機一次)。  

為何可解決 Root Cause:  
硬體設定檔或完整關機都能確保 OS 在下次開機時重新偵測硬體，不會因 PCI 裝置突然消失而藍屏或驅動失效。

**Cases 1 (效益)**:  
• 雖增加關機/開機時間，但避免系統當機。  
• 使用硬體設定檔可把等待時間減到一次重開機，較適合短期外出。

---

## Problem: IBM Presentation Director 只能切換內建 ATI，無法自動切到外接顯示卡的 DVI

**Problem**:  
回家後想一鍵切換到「外接 LCD + DVI」模式，但 Presentation Director 僅支援內建顯示晶片，導致需手動設定。

**Root Cause**:  
IBM 提供的 Presentation Director 只與內建 ATI 驅動整合，未讀取到 PCI 顯示卡的裝置 ID 與切換 API。

**Solution**:  
1. 直接在 Windows「顯示設定 → 進階設定」內開啟 nVidia DVI 輸出。  
2. 可在桌面建立 .cpl 指令捷徑 (control desk.cpl,@0,3) 或 nVidia 的 nView Profile，點兩下即切換，算是自行補上「一鍵切換」。  

為何可解決 Root Cause:  
跳過 Presentation Director，改用顯示卡原生設定或 nView profile，可直接控制外接顯示卡，繞過 IBM 工具的限制。

**Cases 1 (效益)**:  
• 從「進底座→打開螢幕→手動點右鍵」縮短為「進底座→雙擊捷徑」。  
• 使用者體驗接近原本 IBM Theme 的便利性。