# CSS 擋右鍵：用 DHTML Behavior 一次解決全站右鍵封鎖

# 問題／解決方案 (Problem/Solution)

## Problem: 企業內部 Web 內容需要「全面封鎖右鍵」  

**Problem**:  
企業內部的內容管理系統被要求「所有網頁都必須禁用滑鼠右鍵」。  
‧ 專案已經有數百頁 HTML；  
‧ 若用傳統做法，必須在每一頁手動插入 `<script>`、或在所有連結加 `oncontextmenu="return false"`；  
‧ 每多一頁，就要再貼一次「檔右鍵」程式碼，維護極為痛苦。  

**Root Cause**:  
1. 右鍵封鎖是「行為」，而非「樣式」。傳統 HTML/CSS 把樣式與行為切開，導致開發者只能一頁一頁加 Script。  
2. 專案缺少「集中式行為管理」機制；任何行為層面的修改都必須重新發版所有頁面。  

**Solution**: 以 DHTML Behavior (.htc) + CSS 把「行為」變成「樣式」  
1. 撰寫 `context-menu-blocker.htc`：  
   ```html
   <!-- context-menu-blocker.htc -->
   <script language="JScript">
     // 當元件附掛到元素上時執行
     window.attachEvent("oncontextmenu", function(evt){
        evt.returnValue = false;   // 取消右鍵選單
     });
   </script>
   ```  
2. 於全站的 CSS 加入一行：  
   ```css
   /* 只要一行就能把右鍵封鎖行為撒出去 */
   body { behavior: url('context-menu-blocker.htc'); }
   ```  
3. 發布：把 `.htc` 檔及更新後的 CSS 佈署到網站根目錄，即完成全站封鎖。  

為何能解決根本原因：  
‧ Behavior 技術讓「腳本行為」被當成「樣式」綁到元素；任何加載該 CSS 的頁面都自動得到相同行為，徹底去除「逐頁貼 Script」的痛苦。  

**Cases 1**: 專案快速導入  
背景：內網內容系統已有 500+ 靜態頁。  
行動：新增 `.htc` 與一行 CSS。  
成效：  
- 封鎖右鍵部署時間由原估 2 人日 ↓ 到 30 分鐘；  
- 之後新增頁面「零改動」即自帶封鎖功能，維護成本趨近 0。  

---

（本文僅示範「行為集中管理」概念；DHTML Behavior 僅 IE 5+ 支援，跨瀏覽器請採用 unobtrusive JS / 事件代理等現代方案。）