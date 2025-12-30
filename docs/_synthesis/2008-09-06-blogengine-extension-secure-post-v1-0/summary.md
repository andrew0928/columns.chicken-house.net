---
layout: synthesis
title: "BlogEngine Extension: Secure Post v1.0"
synthesis_type: summary
source_post: /2008/09/06/blogengine-extension-secure-post-v1-0/
redirect_from:
  - /2008/09/06/blogengine-extension-secure-post-v1-0/summary/
---

# BlogEngine Extension: Secure Post v1.0

## 摘要提示
- 需求背景: 以最小成本在 BlogEngine.NET 為特定文章提供密碼保護，避免建立帳號與登入流程
- 設計原則: 不建帳號、不登入；密碼於伺服端驗證；未輸入密碼前不在前端輸出文章內容
- 技術切入點: 透過攔截 Post.Serving 事件動態改寫文章輸出內容
- 啟用條件: 僅當文章內文以 [password] 開頭時才套用密碼保護
- 驗證流程: 使用者輸入密碼後以 ?pwd=xxx 方式帶到文章網址，伺服端比對後放行
- 已登入者豁免: 若使用者已通過 BlogEngine 身分驗證，則不套用密碼保護
- 管理設定: 藉由 Extension Manager 提供三個可調參數（顯示訊息、密碼提示、指定密碼）
- 實作規模: 少於百行的 C# 程式碼即可完成，核心在事件攔截與 HTML 輸出
- 安裝方式: 單一檔案 SecurePost.cs 放入 ~/App_Code/Extension 並於後台啟用
- 安全取捨: 密碼以明碼出現在網址上，未加入雜湊；重點在「避免檢視原始碼即洩露」

## 全文重點
作者因家中使用需求，需在 BlogEngine.NET 上為少數文章加上簡單密碼保護，且不希望建立使用者帳號或強制登入。回顧現有擴充多以角色與分類授權為主，無法滿足「特定文章輸入暗號可見」的需求，因此自行開發一個輕量的 Extension：SecurePost v1.0。

實作核心是攔截 BlogEngine 的 Post.Serving 事件，於文章輸出前檢查條件並改寫內容。若文章不需保護則原樣輸出；若需保護，預設改為顯示提示訊息與密碼輸入 UI。使用者輸入密碼後，前端以將密碼附在查詢字串 ?pwd=xxx 的方式重導回文章頁，伺服端在事件處理器中以 Request["pwd"] 與設定的密碼比對，正確則放行輸出文章原文，否則持續顯示密碼提示畫面。已登入的使用者（Identity.IsAuthenticated）直接略過保護。為避免全站套用，另設啟用規則：僅當文章內容以 [password] 開頭時才啟用密碼保護，便於作者精準控制哪些文章需保護。

為提供更佳可用性，作者透過 Extension Manager 暴露三個可調參數：顯示訊息、密碼提示與指定密碼，並設定預設值及說明。這些設定以 ExtensionSettings 匯入並於執行時讀取，不需另建資料表或檔案。整體程式不到百行，關鍵在事件掛載、條件檢查與組合 HTML 片段；其餘多為樣板式設定與輸出。

在安全性取捨上，作者刻意不實作前後端雜湊或更進階的保護，認知到密碼會以明碼出現在網址上，強調本擴充目標是「基本保護」：避免在前端原始碼直接露出內容與密碼，而非抵禦進階攻擊或竊聽。安裝上，僅需將 SecurePost.cs 放入 ~/App_Code/Extension、於後台 Extension Manager 啟用並視需求調整設定即可使用。最後作者提供完整程式碼，並說明轉載方式與回饋期待。

## 段落重點
### 需求背景與目標
作者需在 BlogEngine.NET 上實現特定文章的密碼保護，避免沿用過往以 IIS 整合式驗證或需創建帳號的模式，因其操作複雜且不符合需求。需求聚焦在簡單、無登入的保護：閱讀特定文章前輸入暗號即可。檢視既有擴充如 Password Protected Post 發現其走角色與分類授權，與本需求不符，因此決定自行開發。設計目標為輕量、易用與最小侵入，並以文章為單位啟用保護。

### 事件攔截與原型驗證（POC）
技術切入點選擇 BlogEngine 的 Extension 機制，透過在類別靜態建構子掛載 Post.Serving 事件，於每次文章內容輸出前進行攔截與改寫。POC 階段先以最小程式碼驗證能否改寫輸出，將原文替換為一段包含密碼輸入欄位與 GO 按鈕的 HTML。此階段證明可在不改動核心程式的前提下，動態控制單篇文章的呈現內容。

### 密碼檢查與啟用條件
正式邏輯在事件處理器中加入兩道檢查：一是是否帶有正確的密碼參數（Request["pwd"] == Password）以決定是否放行；二是文章內文是否以 [password] 開頭，僅符合者才啟用保護，避免全站文章被攔截。另補充一條：若使用者已登入（Identity.IsAuthenticated），則直接略過保護。這些條件以數行程式碼完成，使 POC 迅速可用。作者承認密碼會以明碼出現在網址上，雖可考慮 MD5/SHA256 雜湊，但前後端同步實作過於繁瑣，故在此版本不納入，聚焦基本防護。

### 參數化與 Extension Manager 整合
為讓非技術使用者可管理提示文字與密碼，作者利用 ExtensionSettings 對應 Extension Manager 的可編輯項目，新增三個參數：顯示訊息、密碼提示、指定密碼，並提供預設值與說明文字。設定以 IsScalar 方式儲存，避免複雜資料結構，並透過 ExtensionManager.ImportSettings 與 GetSettings 輕鬆載入。此步驟讓整體擴充在不新增資料庫或檔案的情況下具備配置能力，大幅降低維護成本。

### 安裝、使用方式與展示
完成的 SecurePost.cs 僅需放到 ~/App_Code/Extension，即視為安裝完成。於後台以管理者身分進入 Extension Manager，可見 SecurePost 並進行設定編輯。實際使用時，在需保護的文章開頭加入 [password]，未登入者將看到自定提示與密碼欄位；輸入正確密碼後即顯示文章原文。文中以截圖展示輸入畫面與成功顯示結果，證明流程順暢，且使用者體驗簡潔直接。

### 完整程式碼與授權聲明
作者提供完整的 SecurePost.cs 程式，程式量不到百行，核心涵蓋事件掛載、條件檢查、HTML 拼接與設定載入。授權上鼓勵自由使用與散佈，但請引用本文連結而非另行上傳程式碼檔供下載；若認為有幫助，歡迎留言、推薦或贊助。整體呈現一個從需求、設計到交付的完整微型擴充實作案例，示範如何在 BlogEngine.NET 上以最小代價達成實用功能。

## 資訊整理

### 知識架構圖
1. 前置知識：
- 了解 BlogEngine.NET 的架構與 Extension 機制
- 基本 C# 與 ASP.NET（HttpContext、事件、字串處理）
- HTML/JavaScript 基礎（簡單表單與導向）
- 基本安全觀念（伺服端驗證、不要只做前端隱藏）

2. 核心概念：
- 事件攔截 Post.Serving：在文章輸出前接管內容生成
- 內容啟用標記：[password] 作為是否啟用保護的旗標
- 伺服端驗證：以 Request["pwd"] 比對設定密碼，避免前端洩漏
- 權限繞過條件：已登入使用者不需輸入密碼
- Extension 設定：透過 ExtensionSettings/ExtensionManager 管理訊息/提示/密碼
關係說明：Post.Serving 事件每次輸出文章時觸發 → 檢查是否標記為受保護([password]) → 若未登入且未通過密碼，改寫 e.Body 為「輸入密碼」UI → 密碼以 ?pwd= 明碼帶回同頁 → 伺服端驗證通過則放行原文。

3. 技術依賴：
- BlogEngine.Core：Post、ServingEventArgs、ServingLocation、Extension、ExtensionSettings、ExtensionManager
- ASP.NET：HttpContext、User.Identity、Request 取 QueryString
- UI 組裝：StringBuilder 產生 HTML，Server.HtmlEncode 做轉義
- 部署位置：~/App_Code/Extension 下放置 .cs 檔以自動載入

4. 應用場景：
- 單純想保護少數文章、不想建立帳號系統的部落格
- 家用/內部分享等低安全需求內容
- 快速上線、可由管理介面修改提示與密碼的輕量需求
- 不適用於高敏感資料（因為密碼以明碼出現在 URL）

### 學習路徑建議
1. 入門者路徑：
- 安裝/熟悉 BlogEngine.NET 基本結構與後台 Extension Manager
- 了解如何在 ~/App_Code/Extension 放入並啟用擴充
- 實作與觀察 Post.Serving 事件如何改寫 e.Body
- 透過設定面板調整 SecurePostMessage/PasswordHint/PasswordValue 並測試

2. 進階者路徑：
- 將明碼 ?pwd= 改為更安全的傳遞（POST、TempData、短期 Token、或使用 Cookie/Session 記錄通過狀態）
- 為 Feed（ServingLocation.Feed）提供替代輸出或隱藏策略
- i18n/多語系與樣式優化、無障礙/行動裝置體驗
- 支援每篇文章自訂密碼、到期時間、或與分類/標籤結合

3. 實戰路徑：
- 建立範例文章，在文首加上 [password]
- 部署 SecurePost.cs，於後台啟用並設定訊息/提示/密碼
- 用未登入與已登入兩種身分測試；檢查正確/錯誤密碼行為
- 監看 Server Log 與 QueryString，評估是否需要改良密碼傳遞與通過狀態保存

### 關鍵要點清單
- Post.Serving 事件攔截：在輸出文章前接管內容並可改寫 e.Body（優先級: 高）
- 啟用標記 [password]：只有內文以此開頭的文章才啟用保護（優先級: 高）
- 伺服端密碼驗證：使用 HttpContext.Current.Request["pwd"] 與設定值比對（優先級: 高）
- 已登入者直通：User.Identity.IsAuthenticated 為 true 時不需輸入密碼（優先級: 中）
- ExtensionSettings 設定：透過 ExtensionManager 提供 UI 編輯訊息/提示/密碼（優先級: 高）
- HTML/JS 提示頁：以 StringBuilder 輸出簡易輸入框與導向 GO 按鈕（優先級: 中）
- 安全限制（明碼於 URL）：?pwd= 會暴露密碼，不適合敏感內容（優先級: 高）
- 不只前端隱藏：避免僅用 DHTML 隱藏文章，必須伺服端把關（優先級: 高）
- 內容輸出位置差異：ServingLocation.Feed 可選擇不同處理（目前範例未處理）（優先級: 低）
- HtmlEncode 使用：對顯示訊息做編碼避免 XSS（優先級: 中）
- 部署位置與載入：將 .cs 檔放 ~/App_Code/Extension 即可被載入（優先級: 中）
- 參數初始化：提供 SecurePostMessage、PasswordHint、PasswordValue 預設值（優先級: 低）
- 結構簡潔：少量程式碼（<100 行）即可完成 MVP（優先級: 低）
- 可擴充方向：改用 Cookie/Session、POST 提交、雜湊/Token、每篇獨立密碼（優先級: 中）
- 使用情境界線：適合簡單防護、不取代完整身份驗證/授權機制（優先級: 高）