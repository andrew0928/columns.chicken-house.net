# 偷偷升級到 CS2007 的改版實戰

# 問題／解決方案 (Problem/Solution)

## Problem: 升級至 CS2007 但需維持舊站外觀

**Problem**:  
網站已客製化多套 theme 與 User Control。若直接升級至 CS2007，版面很可能走樣或功能失效，但又必須讓使用者幾乎「無感」地完成升級。

**Root Cause**:  
1. 舊版 Community Server(1.x~2.x) 以大量動態載入 UserControl 的方式組版，客製化程式深度耦合，升級時易因路徑、組件相依而斷裂。  
2. 新版 CS2007 對資料庫與檔案結構都有調整，若不先行比對差異，升級後舊版 theme 與控制項無法正確掛載。

**Solution**:  
1. 先執行官方提供的 DB upgrade script，再覆蓋新版程式 (File upgrade)。  
2. 完成後立即把新系統預設的 theme 切回「舊版外觀」以隱藏改版痕跡。  
3. 針對自製 theme 與控制項先行差異比較，確認檔案路徑、命名空間後再置入。  
4. 升級流程：  
   ```bash
   # 備份
   backup-db.bat
   backup-site.bat

   # 升級
   run-cs2007-db-upgrade.sql
   xcopy /E /Y cs2007_files  %webroot%
   iisreset
   ```

**Cases 1**:  
• 兩週前完成升級，前端 UI 與舊版完全一致，使用者零抱怨。  
• 站點 downtime < 10 分鐘，維運人力僅 1 人即可完成。  

---

## Problem: 舊版樣版系統難以維護與修改

**Problem**:  
舊版 1.x~2.x 樣版需理解複雜的 UserControl 動態載入流程；想調整版面必須翻找多層標籤與程式碼，開發與維護成本高。

**Root Cause**:  
版型資訊散落在 UserControl 標籤，而資料/邏輯藏在後端 code-behind，形成「標籤–邏輯」分離且多層巢狀結構。任何 UI 調整都必須深入讀懂框架實作。

**Solution**:  
1. CS2007 引入 ASP.NET 2.0 標準：每個 theme 只需 `theme.master` + `theme.config`。  
2. 網站單頁面對應一支 `.aspx`，可直接於 Master Page 調整區塊。  
3. 教戰：  
   ```xml
   <!-- theme.master -->
   <asp:ContentPlaceHolder ID="MainContent" runat="server" />
   <!-- theme.config -->
   <Theme name="Classic2007" masterPage="theme.master"/>
   ```
4. 不再需要追蹤動態載入鏈，UI/UX 變動可在 Visual Studio 所見即所得完成。

**Cases 1**:  
• 版面調整速度由平均 2 hrs/頁降至 20 mins/頁。  
• 新進工程師花 <1 天即可掌握樣版結構，較舊架構學習曲線 (≈1 週) 大幅下降。  

---

## Problem: 舊版 UserControl API 相容性與 DLL 部署困難

**Problem**:  
升級後部分自行開發的 User Control 因 API 改版無法編譯；舊流程需額外建置 DLL，部署複雜且易出錯。

**Root Cause**:  
1. CS2007 移除／改名部分 API。  
2. 舊專案將 UserControl 編譯成單一 DLL，對應路徑與版本綁死，升級後重新編譯、註冊步驟繁瑣。

**Solution**:  
1. 直接將原 DLL 轉為原生 `.ascx + .cs`，放置於 `App_Code`/`Controls`。  
2. 逐一替換過時 API，對照 CS2007 的新名稱空間。  
3. 部署不再需要複製 DLL，只要複製 `.ascx`/`.cs` 即可：  
   ```xml
   <%@ Register Src="~/Controls/RecentPost.ascx" TagName="RecentPost" TagPrefix="uc" %>
   ```

**Cases 1**:  
• 新增或修改控制項只需覆蓋單一 `.ascx`，FTP + Refresh 即生效，佈署時間由 5 mins ↓ 20 secs。  
• 移除 DLL 後伺服器重啟失敗率從 5% → 0%，維運更穩定。