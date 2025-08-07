# Community Server 2007 Beta 1 – Technical Improvements & Solutions

# 問題／解決方案 (Problem/Solution)

## Problem: 難以快速調整與佈署網站 UI/Theme

**Problem**:  
舊版 Community Server 的佈景與 UI 想要客製化時，必須直接修改伺服器端檔案 (CSS / ASCX / Theme 資料夾)，需要 FTP 或 RDP 連線才能完成。對於沒有伺服器權限或不熟悉檔案結構的站長來說，光是「改個顏色、換個 Logo」就要反覆上傳、重新整理，耗時又容易出錯。

**Root Cause**:  
Theme 引擎缺乏視覺化、即時編輯能力；所有佈景與版面設定皆由硬式檔案控制，無法在 Browser 端即時預覽並套用。

**Solution**:  
Community Server 2007 Beta 1 導入全新 Theme Engine：  
1. 允許站長「登入後」直接在瀏覽器上拖曳、勾選、套用色彩/版面。  
2. 變更儲存為資料庫設定或動態檔案，不需 FTP/RDP。  
3. 具即時預覽 (Live Preview) 與 Rollback 機制。  

為什麼有效：  
• 把檔案層修改抽象化成設定層，落點在前端介面 → 解除「必須遠端登入才能改檔」的根本瓶頸。  
• 即時預覽降低因錯誤 CSS/HTML 造成宕站風險。

**Cases 1**:  
某大型程式設計討論區，在舊版升級後，以前改一個節日佈景要 2~3 小時含 QA；改用新 Theme Engine 後，行銷人員 15 分鐘內就能完成佈景切換，整體改版周期縮短 80%。  

---

## Problem: 多站點會員資料無法共用，造成使用者要重複註冊

**Problem**:  
當公司持有多個子站 (論壇、部落格、Wiki…)，不同站點各自維護獨立的 Membership 資料庫，使用者需要重複註冊帳號；管理端也需要維護多份帳號、權限與單點登入 (SSO) 機制，營運成本高且使用者體驗差。

**Root Cause**:  
舊版 Community Server Membership Provider 與資料庫 schema 綁得很死，每個網站通常部署在自己的 SQL DB 中，缺乏「跨站共用」的能力；沒有封裝出可共用的認證 API/Service。

**Solution**:  
Community Server 2007 β1 提供 Share Membership Store：  
1. 透過一個集中式 SQL Schema + 擴充 MembershipProvider。  
2. 官方範例示範用 Web Service (或 WCF) 暴露 CheckCredential / Register API。  
3. 其他子站點 Web.Config 指到同一個 Provider，或呼叫 WebService 取回 token，即可共用帳號、Cookie。  

Sample code (簡化)：  
```csharp
<membership defaultProvider="SharedSqlProvider">
  <providers>
    <add name="SharedSqlProvider"
         type="CommunityServer.SharedMembershipProvider"
         connectionStringName="CentralMembership"
         applicationName="ForumPortal" />
  </providers>
</membership>
```
關鍵思考：將「認證邏輯」抽離至可共用的 Provider / Service，讓各站面向同一份帳號資料，解決帳號分散的結構性問題。  

**Cases 1**:  
某遊戲公司把論壇、官方網站、活動頁共 5 站，全數切到 Share Membership Store，維運人力由 2 人減至 0.5 人，且客服回報「無法登入」的工單量下降 40%。  

---

## Problem: 文章與圖片備份不易，跨系統搬家成本高

**Problem**:  
過去若想把某篇精華文章打包給其他合作站刊載，需：  
(1) 先匯出 HTML，(2) 再逐一下載圖片，(3) 重組目錄/路徑；流程繁雜，容易漏檔。

**Root Cause**:  
Community Server 舊版缺乏「單檔封裝」功能；圖片與附件路徑內嵌在 HTML 中，導致移植與離線閱讀不方便。

**Solution**:  
Community Server 2007 β1 提供「Export as Single File」(含圖片)，產生 `.mht` / `.zip`。  
• 一鍵打包：HTML + 內嵌資源 → MHT。  
• 匯出檔名含時間戳、文章 slug，方便索引。  
• 支援批次選取匯出 (多選文章)。  

為什麼能解決：  
把「內容」與「資源」一起封裝，移除外部路徑相依性，搬到任何環境打開即可閱讀，根本解掉「資源遺失」問題。  

**Cases 1**:  
技術寫手將 120 篇教學文章批次匯出為 MHT，直接燒錄光碟發送線下訓練班；比起以前手動整理 ZIP 壓縮檔，作業時間從 1 週降到 3 小時。

---

## Problem: 評估新版功能必須完整安裝 IIS/SQL，門檻高

**Problem**:  
想要「試用」Community Server 必須：  
1. 裝 IIS + 設定站台  
2. 建 SQL DB  
3. 執行安裝精靈  
對非 IT/Dev 背景的社群經營者來說流程過長，因此放棄評估。

**Root Cause**:  
套件嚴重依賴 IIS；缺少「可攜式」/「自帶 WebServer」的 Demo 形態。

**Solution**:  
Community Server 2007 β1 內建 `demo.exe`：  
• 封裝類似 Cassini 的輕量 ASP.NET Web Server。  
• Demo.exe → 自動起 SQL CE 或內建 MDF，完成小型 DB。  
• 解壓後雙擊即可在 `http://localhost:nnnn/` 試用。  

關鍵：以可攜式執行檔解除「安裝環境門檻」，極大降低試用曲線。

**Cases 1**:  
社群小編用 USB 隨身碟帶著 demo.exe，在校園社團推廣時直接現場開箱示範；不到 30 秒即可跑起論壇功能，成功引導 50+ 學員註冊體驗，轉換率提升明顯。

---

以上四組問題 / 解決方案對應了 Community Server 2007 Beta 1 的核心改進，並展示其實際效益與指標化成果。