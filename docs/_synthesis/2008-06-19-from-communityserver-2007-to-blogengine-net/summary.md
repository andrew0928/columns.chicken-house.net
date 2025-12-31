---
layout: synthesis
title: "從 CommunityServer 2007 到 BlogEngine.NET"
synthesis_type: summary
source_post: /2008/06/19/from-communityserver-2007-to-blogengine-net/
redirect_from:
  - /2008/06/19/from-communityserver-2007-to-blogengine-net/summary/
postid: 2008-06-19-from-communityserver-2007-to-blogengine-net
---

# 從 CommunityServer 2007 到 BlogEngine.NET

## 摘要提示
- 搬站動機與決策: 從成熟的 CommunityServer 2007 遷移到較年輕的 BlogEngine.NET，短時間決策、邊做邊修正。
- BlogML 匯入流程: 使用 BlogML 匯出/匯入與 BlogEngine.NET 的 ClickOnce 匯入工具完成初步搬遷。
- 匯入技術問題: 文章修改時間解析為 0000/01/01 並牽涉到時區校正，導致例外錯誤。
- 站內外連結修補: 絕對路徑圖片、站內文章互連、站外既有連入的舊網址全面修正與轉址。
- Article 類型遺漏: CommunityServer 的 Article 內容雖進 BlogML，但被 BlogEngine.NET 匯入工具略過，需自修。
- 瀏覽計數補齊: BlogEngine.NET 無內建 View Count，以 Extension 擴充並自行匯入舊站數據。
- 版面與自訂功能: 以 Master Page + CSS 調整版面、安插 Google Ads，移植自寫控制項與功能。
- 以程式解問題: 多數問題需動用 Visual Studio 2008 自行撰寫程式批次處理與修補。
- 內鏈雙階段修正: 先匯入建立新 PostID，再以第二階段批次 SEARCH & REPLACE 完成站內連結更新。
- 舊址相容與提示: 實作舊制網址相容轉址並加入提示頁，避免「無聲」轉跳造成混淆。

## 全文重點
作者紀錄將部落格平台由 CommunityServer 2007 遷移至 BlogEngine.NET 的過程與心得。雖然搬家的念頭醞釀已久，但實際決定與執行相當快速，於是以「先上車後補票」的方式，一邊搬一邊修。技術策略上，取徑 BlogML 標準：先以 CommunityServer 工具匯出 BlogML，再用 BlogEngine.NET 官方提供的 ClickOnce WinForm 工具、透過 BlogEngine.NET 的 Web Service 匯入。不過過程中遇到數項阻礙，包括時間欄位被解析為 0000/01/01、涉入時區轉換導致例外，必須打開 Visual Studio 2008 改程式碼繞過問題，才完成首輪匯入。

完成初步匯入後，實務上的「收尾工程」才是大宗。首先是圖片與站內外連結：由於 Windows Live Writer 產出的圖片常用絕對網址，搬家後仍指向舊站，必須批次調整；站內文章互連因為網址結構改變亦須修正；站外連回作者舊站的連結若不處理，將造成 404，嚴重影響流量。作者設計了舊址相容層，可接受 CommunityServer 格式舊 URL，導向至 BlogEngine.NET 新網址，並特意加入提示頁，讓轉向「可感知、可追蹤」，符合防禦式程式設計的精神。

內容類型方面，CommunityServer 的 Blog 與 Article 皆能匯出至 BlogML，但 BlogEngine.NET 匯入工具不吃 Article，作者遂以程式自動化補匯。功能面則補上 BlogEngine.NET 原生缺少的瀏覽計數（View Count）：先安裝社群提供的 View Count Extension，再自行將舊站統計資料匯入新系統。視覺與佈局上，作者偏好 BlogEngine.NET 的清爽結構，僅以 Master Page 與 CSS 微調並嵌入 Google Ads、移植自寫控制項；另把原在 CommunityServer 客製的項目逐一檢視，保留可用者、淘汰不再需要者、再規劃尚未改寫者。

站內連結修正採雙階段策略：第一階段執行基本匯入並在 BlogML 元資料標注新網址與 PostID；第二階段再對舊文章進行全文搜尋與取代，將內文中的舊連結轉為新連結。此舉解決了「匯入前無法預知新網址樣式」的先天困難。經過一輪輪的調整與程式化修補，圖像顯示、站內互連、站外轉入、瀏覽統計與版面整合皆告穩定。作者對 BlogEngine.NET 的程式碼結構予以肯定：碼量精簡、架構清楚、易於理解與擴充，開發環境建置容易，修改難度約為 CommunityServer 的三分之一，讓整體搬遷在「能動手寫程式」的前提下變得可控可解。

總結而言，此次搬遷的核心在於：以標準格式（BlogML）打通內容搬運、用程式與擴充機制補齊平台差異、針對連結相容與 SEO/流量損失風險採取防禦式設計。當最棘手的網址轉換與相容性處理搞定，其他收尾工作便順理成章。作者最後呼籲有意自 CommunityServer 遷移至 BlogEngine.NET 的朋友參考其作法，以降低遷移成本與風險。

## 段落重點
### 開場與搬站背景
作者澄清不是個人搬家，而是網站平台搬遷。從成熟的 CommunityServer 2007 遷至較年輕的 BlogEngine.NET，決策迅速、準備略顯倉促。雖然早有搬家打算，但真正落實只花了幾天，因此選擇邊做邊記錄，將過程中遇到的麻煩與解法分享給有相同需求的人，視為功德一件。

### 使用 BlogML 與匯入流程
遷移策略採 BlogML。CommunityServer 2007 透過現成工具匯出 BlogML；BlogEngine.NET 則提供 ClickOnce 的 WinForm 匯入工具，經由 BlogEngine.NET 站台的 Web Service 完成匯入。RSS 匯入雖名義上支援，但嘗試失敗，故改走 BlogML。實作上流程順暢，介面簡潔，能準確執行匯入工作。

### 匯入時間與時區問題的技術坑
實測遇到關鍵錯誤：CommunityServer 產出的 BlogML 在 BlogEngine.NET 匯入時，文章修改時間被解析為 0000/01/01 00:00:00.000；再加上 BlogEngine.NET 會做時區校正（台灣時區需 -8 小時），造成時間成負值並拋出 Exception。作者直接打開 Visual Studio 2008，移除有問題的時間處理行為後順利匯入，完成第一步，但也預示後續仍需大量動手修。

### 八大問題總覽（連結、類型、計數、版面、自訂）
作者列出實務八大坑：1) 圖片連結為絕對路徑，仍指回舊站；2) Article 類型內容被匯入工具忽略；3) 站內文章互連改動大；4) 站外連入導致新站 404 與流量驟降；5) 缺少瀏覽計數功能；6) 舊站瀏覽計數無法自動匯入；7) 版面需整合廣告與自寫控制項；8) 過往在 CommunityServer 客製的功能需逐一評估、移植或淘汰。上述多半需自行寫程式或撰寫擴充來補齊。

### 程式碼品質觀察與開發體驗
為解決上述問題，作者多次直接 Trace 與修改 BlogEngine.NET 原始碼，體感良好：建置開發環境容易、碼量精簡、架構清晰、易於閱讀與擴充，改動起來「很舒服」。相較之下，CommunityServer 雖強大且早於 .NET 2.0 即自建完整架構，但整體修改難度較高。整段表達對 BlogEngine.NET 工程品質的正面評價，也說明為何以程式輔助遷移是可行路徑。

### 版面整合與廣告嵌入
作者展示完成後的版面成果，僅以 CSS 與 Master Page 做小幅調整，嵌入 Google Ads，視覺上相當契合。這反映 BlogEngine.NET 的頁面組成（Master/UserControl）足以支撐常見的佈局與商業化需求，且改動成本低。

### 站內連結的雙階段（2 PASS）修正策略
因為匯入前無法預知 BlogEngine.NET 生成的新網址與 PostID，無法在 BlogML 靜態改寫就一次到位。作者改採兩段式：第一階段先正常匯入，並在原 BlogML 附註新網址與 PostID；第二階段再對舊文章逐篇做搜尋替換，把站內互連改為新鏈結。此策略有效解決站內互連失效問題，內文示例（如「四核 CPU」）已能指向新站正確位置。

### 站外連結相容與轉址提示頁
為避免外站既有連入（如 Darkthread）失效造成大量 404 與流量流失，作者實作舊制網址相容層：新站可接受 CommunityServer 格式的舊 URL，並轉跳至對應新文；同時刻意加上提示頁與倒數，讓轉向可被感知、可診斷，符合防禦式程式設計與可觀測性原則。示範案例顯示，從外站點入舊址會先看到提示，再自動導至新文，確保內容可達且不中斷。

### 收尾與建議
作者總結：網址相容與轉址是搬家最棘手的一環，一旦搞定，其餘如圖片、內鏈、版面、計數等問題便可逐項解決。整體遷移依賴標準（BlogML）、擴充機制（Extension）與必要的程式化修補，終能平穩落地。文末鼓勵有意從 CommunityServer 遷往 BlogEngine.NET 的讀者參考其方法，降低遷移風險與成本，並戲稱幾位友人別再觀望，趁早動手。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
   - ASP.NET 基礎（Master Page、UserControl）
   - C# 與 Visual Studio（專案建置、偵錯、修改程式碼）
   - IIS 與網站部署（測試環境/正式環境）
   - BlogML 與 RSS 格式（XML 結構與轉匯流程）
   - 時區與日期時間處理（UTC/本地時間偏移）
   - URL 規劃、重寫與 301 轉址（SEO/連結相容）
   - 文字替換、正規表示式與批次處理
2. 核心概念：本文的 3-5 個核心概念及其關係
   - 內容轉移：以 BlogML 將 Community Server 內容移至 BlogEngine.NET（匯出→匯入）
   - 相容性修復：修正時間欄位、內外部連結、圖片連結與文章類型差異
   - 擴充與客製：利用 BlogEngine.NET Extension、版型（Master/UserControl）與自寫程式補齊功能（View Count、廣告、工具）
   - 連結保留與導流：建立舊網址到新網址的對應與轉址提示頁，維持外部引用與 SEO
   - 自動化流程：採用雙階段（Two-pass）處理，先匯入再回寫新連結以便批次修正內文
3. 技術依賴：相關技術之間的依賴關係
   - BlogML 匯入工具（ClickOnce WinForm）依賴 BlogEngine.NET 提供的 Web Service
   - 轉址/路由對應依賴新系統的路由規則與自訂處理程式
   - View Count 需安裝 BlogEngine.NET Extension，並自行匯入舊資料
   - 版型客製依賴 ASP.NET Master Page、CSS 調整與使用者控制項
   - 內文連結修正依賴 Two-pass 流程（第一次建立 PostID/新連結映射，第二次批次替換）
4. 應用場景：適用於哪些實際場景？
   - 從舊版部落格/社群平台遷移到新引擎或自架平台
   - 站點改版時維持外部連結相容與 SEO
   - 將混合內容（Blog/Article）整併為單一內容模型
   - 部落格功能補強（瀏覽數、廣告、程式碼格式化、機器人防護）
   - 以小成本導入新平台並保留既有內容與流量

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
   - 了解 BlogML 與基本匯出/匯入流程
   - 在本機建置 BlogEngine.NET 測試站（IIS/開發伺服器皆可）
   - 使用官方匯入工具進行試匯入，熟悉錯誤訊息與日誌
   - 練習修正圖片絕對連結為相對/新域名
2. 進階者路徑：已有基礎如何深化？
   - 研究 BlogEngine.NET 架構與 Extension 開發模式
   - 規劃路由與轉址策略，實作舊→新網址對映與提示頁
   - 設計 Two-pass 內容修正流程，批次修正站內連結
   - 調整版型（Master Page/CSS）並整合廣告與常用控制項
3. 實戰路徑：如何應用到實際專案？
   - 建立完整遷移清單（內容、媒體、連結、計數器、外掛）
   - 以預備環境演練一次完整搬遷（含資料備份與回復方案）
   - 撰寫修復腳本：日期欄位修補、內文連結替換、View Count 匯入
   - 佈署與監控：啟用 301/提示頁、觀察 404 日誌並滾動式修復

### 關鍵要點清單
- BlogML 匯出/匯入流程: 以 BlogML 在不同部落格引擎間移轉內容的標準做法（優先級: 高）
- 匯入工具與 Web Service: BlogEngine.NET 的 ClickOnce 匯入工具需連接其 Web Service 進行資料寫入（優先級: 高）
- 日期/時區修正: 針對匯入時修改時間為 0000 與時區偏移造成的例外進行程式層修補（優先級: 高）
- 圖片絕對連結轉換: 將 Windows Live Writer 產生的絕對網址改為新站可用的路徑（優先級: 高）
- Article 類型遺漏問題: Community Server 的 Article 內容需自訂流程或工具納入匯入（優先級: 中）
- 站內連結修復（Two-pass）: 先匯入取得新 PostID/URL，再回填內文批次替換舊連結（優先級: 高）
- 站外連結相容與轉址: 建立舊 URL 對映與轉址（可含提示頁），維持外部引用與 SEO（優先級: 高）
- View Count 擴充與匯入: 安裝 View Count Extension 並自行遷入舊計數資料（優先級: 中）
- 版型與廣告整合: 透過 Master Page/CSS 調整版面並加入廣告元件（優先級: 中）
- 擴充功能遷移: 盤點並重實作既有客製（如 Bot Check、Code Formatter）（優先級: 中）
- 錯誤可視化與可追蹤性: 以提示頁、ASSERT/TRACE 揭露轉址與例外狀況，利於維運（優先級: 中）
- 測試與日誌導向修復: 透過 404/應用程式日誌監控遷移遺漏並迭代修正（優先級: 高）
- 架構可讀性與維護性: BlogEngine.NET 架構精簡易懂，便於快速上手與客製（優先級: 中）