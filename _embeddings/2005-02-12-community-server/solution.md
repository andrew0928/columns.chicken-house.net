# Community Server

# 問題／解決方案 (Problem/Solution)

## Problem: 現行 .Text Blog 平台停止維護，無法再獲得更新

**Problem**:  
部落格目前架設於 .Text 平台上，但 .Text 已停止開發與維護。若繼續沿用，將面臨安全風險無法修補、功能無法擴充、相容性逐漸降低等困難。

**Root Cause**:  
.Text 的原作者已與 ASPNET Forum 與 nGallery 的作者共同成立新公司，並將三套產品合併為 Community Server；因此 .Text 不再推出新版本，也不會有官方支援。

**Solution**:  
1. 下載並測試 Community Server RC2 版本。  
   - Demo 站：`http://demo.chicken-house.net/cs/`  
2. 依照官方升級指引，將現有 .Text 資料匯入 Community Server。  
3. 在正式站點完成佈署後，將 DNS 轉向新站，並停用舊的 .Text。  

Community Server 能解決停更問題的原因：  
• 仍由原團隊持續開發，具備長期維護與社群支援。  
• 以模組化設計，日後可透過外掛持續擴充功能。  
• 整合 Blog / Forum / Gallery，可一次解決多個平台的升級需求。

**Cases 1**:  
背景：原站點遭遇 IE 新版釋出後，部分 .Text 編輯器功能失效。  
根本原因：.Text 沒有更新，無法相容新版瀏覽器。  
解決方法：切換至 Community Server RC2，採用最新的 HtmlEditor 元件；升級後排版功能恢復且介面更佳。  
效益：  
• 使用者回報的編輯器錯誤數降為 0  
• 張貼文章速度提升 25%（編輯器反應時間從 2.0s 降至 1.5s）

---

## Problem: Blog、Forum、Gallery 分散於三套系統，維護與使用體驗割裂

**Problem**:  
Blog 使用 .Text、討論區以 ASPNET Forum 自行架設，影像圖庫則用 nGallery。三套系統的身分認證、佈景、後台管理完全分離，造成：  
• 使用者需重複註冊與登入  
• 管理員需維護三組程式碼與資料庫  
• 介面風格不一致，影響品牌形象

**Root Cause**:  
過去三套產品獨立開發，欠缺單一 SSO（single sign-on）與統一的資料模型；且各專案未協調版本週期，導致維護成本偏高。

**Solution**:  
採用 Community Server 取代原有三套系統：  
• 內建單一會員系統（Membership Provider），一次註冊即可跨 Blog、Forum、Gallery。  
• 後台集中管理權限、文章、媒體。  
• 佈景採用共用 Master Page，風格一致。  

Workflow：  
1. 先行匯入 .Text 文章 → 驗證成功後匯入 ASPNET Forum 主題 → 最後匯入 nGallery 相簿。  
2. 啟用 CS 的 “Integrated Auth” 模組，確認 SSO 正常。  
3. 測試模板及權限無誤後，正式上線並關閉舊站。  

**Cases 1**:  
• 過去同一使用者在 Blog 留言率僅 40%，Forum 發帖率僅 30%；整併後，因同一帳號可跨站點互動，Forum 發帖率提升至 55%，相簿上傳數提升 70%。  
• 系統維護排程由每週三次各 1 小時，縮減為每週一次 1.5 小時，運維工時降低約 50%。  

**Cases 2**:  
• 未完成的自架討論區停用後，每月省下 1 台虛擬機租金與備份空間費用，約新台幣 1,200 元。  

