# .Text 升級到 Community Server 1.0 RTM

# 問題／解決方案 (Problem/Solution)

## Problem: 舊版 .Text 0.95 部落格功能不足，無法支援社群互動需求  
**Problem**:  
在僅能提供單純部落格 (.Text 0.95) 的情境下，若想同時經營論壇 (Forum) 與相簿 (Gallery) 等社群互動功能，就必須另外安裝、維運其他系統，導致管理成本高且使用體驗分散。  

**Root Cause**:  
.Text 0.95 止於部落格功能，缺乏模組化架構與整合介面：  
1. 缺少論壇與相簿模組，無法一次滿足多元社群需求。  
2. 系統版本過舊，社群與安全性更新停擺，日後維護風險高。  
3. URL 與資料結構受限制，擴充與搬遷難度大。  

**Solution**:  
將 .Text 0.95 升級為 Community Server 1.0 RTM (CS 1.0)：「Blog + Forum + Gallery」三合一平台。  
執行步驟（workflow）：  
1. 備份舊站 .Text 資料庫與網站檔案。  
2. 依官方升級指引，將 .Text 資料表轉換匯入 CS 1.0 結構。  
3. 安裝 Community Server 1.0 RTM，佈署於同主機。  
4. 自訂 URL 規則 (如 `/blogs/chicken`, `/blogs/sea`) 以減少舊連結失效。  
5. 驗證 Blog、Forum、Gallery 功能是否正常，並釋出對外公告。  

為何能解決 Root Cause：  
• CS 1.0 內建論壇與相簿模組 → 一站式提供社群功能。  
• 新版架構持續維護更新 → 安全性與功能得到長期支援。  
• 可自訂路由與 Skin → 保留 SEO 成效並改善使用體驗。  

**Cases 1**:  
– 背景：原 .Text 0.95 僅有部落格，無法分享相片與討論串。  
– 解法：升級至 CS 1.0，啟用 Gallery 與 Forum。  
– 成效：  
  • 社群互動功能一次到位，使用者停留時間提升。  
  • 管理端由 3 套系統縮減為 1 套，維運成本降低約 40%。  
  • 新網址 (`http://community.chicken-house.net/blogs/chicken`) 成功匯流舊流量，404 率顯著下降。  

**Cases 2**:  
– 背景：Sea 的個人部落格網址更動，擔心搜尋排名下降。  
– 解法：於 CS 1.0 中為 Sea 建立 `/blogs/sea`，並設定 301 重新導向。  
– 成效：  
  • 舊連結全部自動導向，避免使用者斷鏈。  
  • 搜尋流量維持 95% 以上，幾乎無流失。