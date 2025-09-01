# [BlogEngine.NET] 改造工程 - 整合 FunP 推推王

## 摘要提示
- 選型考量: 在黑米與推推王之間比較速度與穩定性，最終選擇 FunP。
- 版面與功能取捨: 捨棄內建 Rating 與 Tags，精簡共用書籤僅留 FunP。
- 介面一致性: 以推文按鈕取代原 CS 樣式中的計數器，維持版面風格。
- FunP 整合方式: 直接插入 IFRAME 生成推文按鈕，避開多層 script 包裝。
- 推文資料帶入: 自動帶出標題、摘要與分類為 tags，減少手動輸入。
- 程式實作: 在 PostView.ascx 中以 C# 組裝參數並輸出 IFRAME 與連結。
- 封存頁優化: 在 archive.aspx.cs 以 IFRAME 取代 Rating，顯示推薦數。
- 效能觀察: 多達數百個 IFRAME 同頁載入會拖慢 IE 效能。
- 版面問題改善: 改以直接 IFRAME 嵌入後，避免版面掛掉與樣板衝突。
- 後續工作: 預告自製 PostViewCounter Extension 以補點閱率功能。

## 全文重點
作者將部落格平台搬遷至 BlogEngine.NET 後，重新檢視是否整合社群書籤服務。先比較黑米與 FunP：黑米雖有黑米卡可取代「關於作者」區塊，但實測發現載入速度慢、同頁放置多個元件時易拖垮樣板；FunP 的前端程式風格與載入效率較佳，且不會造成版面崩壞，最終決定僅整合 FunP。

為了避免功能混亂與視覺雜訊，作者先訂出調整方針：捨棄內建 Rating 機制，將推文按鈕作為主要互動指標；保留原 CS 風格並用推文按鈕取代原計數器；只使用一種社群書籤並移除多餘按鈕；停用 Tags、改以分類為主，並調整分類位置至右上；新增智財權聲明、補上自製計數器，以及在推文時自動帶出文章基本資訊（標題、摘要、標籤）。

技術面上，作者檢視 FunP 官方工具，發現其本質是插入一個帶參數的 IFRAME。為了降低複雜度與除錯成本，直接在 BlogEngine 的 PostView.ascx 中輸出 IFRAME，並用 C# 先處理好各項參數：將文章正文去除 HTML 後取前 70 字作為摘要、對 URL/標題/摘要進行 UrlEncode、並把分類轉換成 tags[] 參數。推文按鈕顯示與推文提交連結分別以 IFRAME 和 A 連結實作，讓使用者能快速推文且自動帶入必要資訊。

在封存頁（archive.aspx）亦套用相同策略：原本以 Rating 顯示的區塊改為 FunP 推薦數的 IFRAME。由於作者文章總量大，封存頁可能同時載入近五百個 IFRAME，IE 表現吃力，但相較於過往 script 方式造成的版面崩壞仍較能接受。整體成果讓版面更乾淨、一致，互動焦點清楚，並解決先前載入不穩定問題。文末預告將推出自製的 PostViewCounter Extension，以補足 BlogEngine 未內建的每篇文章點閱統計需求。

## 段落重點
### 選擇社群書籤服務：黑米 vs. FunP
作者曾在舊站使用過推推王貼紙，搬家至 BlogEngine.NET 後再度考慮整合社群書籤。比較黑米與 FunP 的工具後，發現黑米雖提供黑米卡可取代「關於作者」，但速度偏慢、同頁多元件會拖垮樣板；FunP 的 script 風格清晰、表現穩定不破版。為避免多家書籤造成雜亂，決定只整合 FunP，並與版型風格一致化。

### 改造方針與版面調整
作者設定多項改造原則，避免盲目加功能：捨棄 BlogEngine 內建 Rating，改以 FunP 推文為互動指標；以推文按鈕取代原 CS 樣式中的計數器，維持既有視覺辨識；移除左下方多種社群書籤按鈕，專注於單一服務；取消 Tags，改以分類為主，並把分類移到右上以減少干擾；新增智財權聲明；補上自製計數器；推文操作自動帶入文章標題、摘要與分類（當作 tags），降低使用者操作負擔。透過前後對照（原 CS 樣式、修改前後截圖），展示版面更精簡、互動焦點更集中。

### 直接嵌入 FunP IFRAME：PostView.ascx 實作
分析 FunP 的官方工具後，作者發現核心只是插入一個帶參數的 IFRAME，因此捨棄多層 script 產生 HTML 的做法，直接在 PostView.ascx 製作 IFRAME，降低出錯與除錯成本。程式步驟包括：用 Regex 移除文章內文 HTML，截取前 70 字作為摘要；將文章連結、標題、摘要進行 UrlEncode；把每個分類組裝成 tags[] 查詢字串；最後輸出 IFRAME 顯示推文按鈕。此方式提升穩定度，避免過往 script 造成的版面掛掉問題。

### 自動帶入推文資料與提交流程
除了顯示推文按鈕，作者也製作了直接提交推文的連結，讓讀者在 FunP 推文頁可自動帶入必要資料，包含 url、標題（s）、摘要（t）與 tags。為此，部分參數沿用前段已計算好的編碼結果，並輸出為簡單的 A 連結搭配圖片。此做法兼顧可讀性與維護性，並降低使用者操作成本。

### 封存頁（archive.aspx）整合與效能觀察
在封存頁面，作者將原本顯示 Rating 的區塊改成 FunP 推薦數 IFRAME，於 archive.aspx.cs 中為每篇文章輸出一個 IFRAME。由於文章數量多，封存頁同時載入四五百個 IFRAME，IE 表現偏吃力，但相較於使用官方 script 可能引發版面崩壞，此法更穩定、也較易控管。整體上，頁面風格一致，資訊架構更清楚，互動元素集中，成效顯著改善。

### 結語與後續計畫
經過本次改造，作者完成了 FunP 推推王的整合，精簡了互動機制並改善版面穩定度與使用流程。雖然在大量 IFRAME 場景下仍有效能負擔，但實務上可接受。作者最後預告將針對 BlogEngine 未內建的點閱統計需求，自行開發 PostViewCounter Extension，於後續文章分享實作細節。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- ASP.NET Web Forms 基礎（UserControl、ascx、code-behind）
- BlogEngine.NET 結構與主題（Themes、PostView.ascx、archive.aspx/.cs）
- 前端基礎：HTML、IFRAME、A 標籤、圖片、屬性
- 伺服端與用戶端差異（server-side render vs client-side script）
- 字串處理與 URL 編碼（Server.UrlEncode）
- 簡單正規表達式處理（去除 HTML 標籤）

2. 核心概念：本文的 3-5 個核心概念及其關係
- 第三方社群書籤整合：以 FunP 推推王為例，透過 IFRAME 或超連結帶參數集成到文章頁與封存頁
- 伺服端產生可預測的標記：避免 client-side script 的不穩定性，直接在伺服端組出 IFRAME/A 標籤與查詢參數
- 文章資訊預填：從文章內容擷取標題、摘要、分類作為 tag，並進行 URL 編碼後帶入提交網址
- 版面與功能取捨：以推文數取代內建 Rating，精簡標籤區塊、調整分類顯示位置、加入智財權聲明與自製計數器
- 效能與穩定性考量：避免大量 client script；封存頁多 IFRAME 造成瀏覽器吃力時的權衡

3. 技術依賴：相關技術之間的依賴關係
- BlogEngine 頁面/主題檔 → 在 PostView.ascx、archive.aspx.cs 注入 FunP 元件
- 伺服端 C# 程式碼 → 組合已編碼的 URL 參數（文章連結、標題、摘要、tags[]）
- FunP 服務端點 → IFRAME: /tools/buttoniframe.php?url=...&s=...；提交: /push/submit/add.php?url=...&s=...&t=...&tags[]=...&via=tools
- 正規表達式 → 從 Post.Content 去除 HTML 以生成摘要
- 瀏覽器端渲染 → IFRAME/IMG 加載與多實例的效能影響

4. 應用場景：適用於哪些實際場景？
- 將 BlogEngine.NET 或類似 CMS/Blog 平台整合在地社群書籤/推文服務
- 用伺服端方式產生第三方元件的 HTML 以提升穩定性與除錯性
- 用推文數據取代或輔助內建評分機制
- 在封存/列表頁大規模渲染社群按鈕時的最佳化實務
- 文章分享入口預填資訊，降低使用者操作成本

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 安裝並熟悉 BlogEngine.NET 結構與佈景主題位置
- 認識 PostView.ascx 與 archive.aspx 的角色與渲染流程
- 練習在 PostView.ascx 中加入簡單的 IFRAME/IMG/A 標籤
- 了解基本 URL 編碼與查詢字串組合

2. 進階者路徑：已有基礎如何深化？
- 在伺服端以 C# 組合 FunP 參數（文章連結、標題、摘要、tags[]）
- 使用 Regex 去除 HTML 並限制摘要長度
- 重構版面：移除 Rating、Tags，調整分類顯示位置，加入智財權宣告
- 在 archive.aspx.cs 中以伺服端字串產生多個 IFRAME，並評估載入成本

3. 實戰路徑：如何應用到實際專案？
- 將 FunP IFRAME 直接插入 PostView.ascx，並在文章頁顯示推文按鈕
- 建立提交連結 A 標籤，預帶文章標題、摘要、分類標籤與 via=tools
- 在封存頁（archive.aspx）以相同方法替換 Rating 區塊為推文按鈕
- 針對大量 IFRAME 的頁面進行效能測試與微調（載入延遲、分批渲染、條件顯示）

### 關鍵要點清單
- FunP IFRAME 按鈕：以 IFRAME 載入 http://funp.com/tools/buttoniframe.php?url=...&s=... 顯示推文狀態（優先級: 高）
- 提交連結參數：使用 /push/submit/add.php?url=...&s=標題&t=摘要&tags[]=...&via=tools 預填資訊（優先級: 高）
- 伺服端產生標記：在 PostView.ascx 與 archive.aspx.cs 直接輸出 HTML，取代 client script（優先級: 高）
- URL 編碼：對文章連結、標題、摘要、分類名稱進行 Server.UrlEncode（優先級: 高）
- 摘要生成：用 Regex 去除 HTML，限制長度（例如 70 字）並加上「...」（優先級: 中）
- 版面取捨：以推文取代 Rating，移除 Tags，調整分類位置，提升可讀性（優先級: 中）
- 效能權衡：封存頁大量 IFRAME（數百個）可能拖慢瀏覽器，需測試與優化（優先級: 高）
- 服務選型：比較不同社群書籤（FunP vs 黑米），衡量速度、相容性與穩定性（優先級: 中）
- 除錯便利性：避免 document.write/eval 等黑盒腳本，偏向可控的伺服端輸出（優先級: 高）
- 主題檔定位：熟悉 Themes/PostView.ascx 與頁面 archive.aspx 的修改點（優先級: 中）
- 類別作為標籤：以文章分類映射為 tags[]，簡化標籤系統（優先級: 中）
- 取代 Rating 的資料位：在 archive 頁將原 Rating 欄位替換為推文按鈕（優先級: 中）
- 智財權宣告：在版面加入版權/智財權說明以因應內容被盜用（優先級: 低）
- 自訂計數器：規劃文章瀏覽次數計數器（延伸至下一篇）（優先級: 低）
- 參數 s 的用途：控制按鈕外觀或尺寸（如 s=1、s=12），需依服務文件對應（優先級: 低）