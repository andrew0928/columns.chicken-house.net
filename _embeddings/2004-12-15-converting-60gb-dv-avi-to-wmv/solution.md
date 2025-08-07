# 大工程：60 GB DV-AVI 壓成多版本 WMV 的自動化實務

# 問題／解決方案 (Problem/Solution)

## Problem: DV 影片檔佔據硬碟空間且轉檔流程費時又繁瑣  
**Problem**:  
• 60 GB 的 DV-AVI 檔 (約 6 小捲 DV 帶) 長期堆在家用 Server，快速吃滿硬碟空間。  
• 轉檔必須透過 GUI 一支一支點擊 Microsoft Media Encoder，每完成一支又要人工再點下一支，晚上讓 PC「排班」壓檔時需要人值班。  

**Root Cause**:  
1. DV 原生格式位元率高：1 小時 ≒ 10 GB。  
2. 缺乏批次（batch）機制，Media Encoder GUI 無法一次排程多檔。  
3. 個人偏好把素材全部暫存硬碟，再決定要不要燒光碟；導致硬碟長期「爆倉」。  

**Solution**:  
撰寫批次檔 (batch file) + Microsoft Media Encoder 9 CLI，自動化「多規格」轉檔流程。  
Workflow 重點：  
1. 指定一個 Watch Folder；只要把 DV-AVI 複製進去即可觸發批次。  
2. 批次檔依序呼叫 MediaEncoder 命令列，針對同一支影片一次輸出 5 種 Profile：  
   - 720×480 @ 2.1 Mbps：DVD 備份用  
   - 360×240 @ 1.2 Mbps：丟進 XBOX，家人客廳播放  
   - 250 kbps：Pocket PC 版  
   - 140 kbps：SmartPhone 版  
   - 140 / 65 kbps：網站串流版  
3. 全程無人工互動；睡前把檔案複製進資料夾，早上起床就得到 5 份成品。  

為何能解決 Root Cause：  
• Media Encoder 9 提供命令列介面，可完全取代 GUI 點擊。  
• 批次腳本一次執行多條設定，移除人工值班。  
• 多版本同時產生後即可把原始 DV 刪除，釋放大量硬碟。  

**Cases 1** (作者個人實作)  
背景：家用 Server + ThinkPad X31 共同壓檔。  
成果指標：  
- 60 GB DV 原始檔 → 5 種 WMV 加總 < 10 GB，硬碟釋放約 50 GB。  
- 每晚可自動轉 2~3 支 DV（取決於 CPU），人員操作時間從每支影片 2~3 分鐘降為 0 分鐘。  
- 家人可在客廳 (XBOX)、行動裝置、網站三處即時觀看，同步滿足備份與分享需求。  

**Cases 2** (影片分享流程)  
背景：將 (5) MediaService 版本直接掛在 Blog Sidebar。  
成果：家人朋友可隨點即播，不必再下載龐大 DV 檔；網站流量控制於 140 kbps，頻寬成本低。  

**Cases 3** (炫耀用途)  
背景：PocketPC / SmartPhone 版讓家長外出攜帶孫子影片。  
成果：影片檔每支僅數十 MB，可存於記憶卡；大幅提升行動展示便利性。