# 家用伺服器／多媒體整合升級至 Windows Vista 的案例整理

# 問題／解決方案 (Problem/Solution)

## Problem: 同一台機器同時提供「伺服器級網路服務」與「Media Center 多媒體功能」衝突

**Problem**:  
家裡只有一台 PC，需要同時做到：  
1) RRAS、IIS、Media Service、SQL Express、DNS、DHCP、SMTP 等伺服器級網路服務；  
2) Media Center (MCE) 功能，用來看電視、錄影、抓節目表；  
3) 一般桌機功能 (上網、玩遊戲)。  
實際佈署時發現「網路服務」與「MCE/桌機體驗」在同一個 OS 中常因版本或功能限制互相牴觸，無法穩定並存。

**Root Cause**:  
• 伺服器級服務 (RRAS、IIS、DNS…等) 在 Windows Server 版本才提供完整支援；  
• Media Center 功能只出現在 MCE / Vista Home/Ultimate 版本；  
• OS 版別差異導致兩種功能必須在不同作業系統環境才能同時運作。  

**Solution**:  
將「網路服務」移至 Virtual PC 的 Guest OS，Host OS 採用 Vista Ultimate 以啟用 MCE 與桌機體驗。  
Workflow：  
1. Host OS 安裝 Vista Ultimate (x64)。  
2. 於 Host 端安裝 Microsoft Virtual PC。  
3. 建立 VM，掛載原本的 Windows 2003 x64 映像 (或其他 Server 版)。  
4. 為 VM 配置 256 ~ 512 MB RAM（Virtual PC 不支援 SMP，CPU 只吃到 1 核即可應付低負載）。  
5. 在 VM 內設定 RRAS、IIS、DNS、DHCP、SMTP 等服務；外部網段透過虛擬網路橋接。  
6. Host 端則專心跑 MCE、Volume Shadow Copy、RAID-1、批次備份與桌面應用。  

關鍵思考點：  
• 用虛擬化把「功能衝突」轉成「環境隔離」；  
• 伺服器服務低負載，配給少量記憶體即可足以運作；  
• Host OS 成功切換到 Vista 後，MCE 與日常桌機需求不再受 Server 版限制。  

**Cases 1**:  
背景 ─ 原機 E6300 + 3 GB RAM 僅跑 Web/File Server，CPU 利用率 < 5%。  
行動 ─ 伺服器服務搬入 VM (256 MB→後來提高到 512 MB)，Host 換 Vista Ultimate。  
效益 ─  
• Host 可直接使用 MCE 看/錄 TV，解除舊日 MCE 啟動問題；  
• VM 雖限單 CPU 核心，但低流量 Web/File 服務無人覺得變慢；  
• 一台設備同時滿足「家庭娛樂 + 私人雲端」需求，節省另一台伺服器硬體與電費。  

---

## Problem: 硬體資源長期閒置，造成成本與能源浪費

**Problem**:  
原本整台 PC 只為了跑幾項低流量的網路服務 (loading 不到 5%) 卻佔用 E6300 + 3 GB RAM 的硬體，形成明顯的硬體閒置與能源浪費。  

**Root Cause**:  
• 以「一台實體機對應一組服務」的傳統做法，無法彈性調整效能；  
• 伺服器工作量遠低於硬體規格，導致 CPU、RAM 長期空轉。  

**Solution**:  
透過虛擬化 (Virtual PC) 將伺服器工作壓縮至 VM，只撥 256~512 MB RAM、單核心 CPU；剩餘硬體資源留給桌面與多媒體。  
關鍵點：根據實際負載分配資源，一台實體機即可同時滿足多重角色，避免「過度配置」。  

**Cases 1**:  
行動 ─ VM 僅占用主機 8~16% RAM，CPU 單核心低速運轉；Host 端 RAM、GPU 全力支援 Vista Aero/MCE 與遊戲。  
效益 ─  
• 電力耗用較單獨兩台伺服器 + 桌機更低；  
• 實體機數量減半，後續維護成本 (備份、更新、噪音、散熱) 亦降低；  
• 使用者體感：伺服器服務與桌面/遊戲皆運行流暢，無性能瓶頸。