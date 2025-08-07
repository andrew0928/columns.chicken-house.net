# [BlogEngine.NET] 改造工程 - 整合 FunP 推推王

## 摘要提示
- 整合動機: 搬家到 BlogEngine.NET 後重新評估社群書籤方案，最終決定導入 FunP 推推王。
- 工具比較: 黑米卡載入慢且易破版，FunP Script 簡潔、速度快、相容性佳。
- 版面規劃: 依原 CS 風格重排版面，移除 Rating、Tags 與多餘書籤，保留單一推文按鈕。
- IFRAME 嵌入: 拆解 FunP 官方 Script，改以直接產生 IFRAME 提升效能與可控性。
- 推文按鈕: 於 PostView.ascx 動態組出網址、標題、內文與分類並送入 FunP。
- 發文連結: 另建 <a> 連結，一次帶入文章資訊免重填，簡化使用流程。
- 封存頁面優化: 修改 archive.aspx.cs，以推文次數取代 Rating，批次產生數百 IFRAME 仍較原法順暢。
- 效能觀察: 大量 IFRAME 仍吃資源，但相較原先 document.write 方式已大幅改善。
- 智財與計數: 加入智財權聲明並預告自製 ViewCounter 擴充元件以統計點閱。
- 後續展望: 持續以同樣手法優化其他功能，提升整體閱讀與維護體驗。

## 全文重點
作者在將部落格搬遷至 BlogEngine.NET 後，希望重新整合社群書籤服務。比較黑米與 FunP 兩家產品後，他發現黑米卡載入速度慢且與版型不合，容易使版面崩毀；反觀 FunP 的腳本結構簡單、呼叫速度快且穩定，因此決定專注與 FunP 結合。  
在動手前作者先訂下八項改造目標：移除內建 Rating；以推文數取代計數器並維持原 CS 風格；只保留一套書籤按鈕；捨棄 Tags 以分類為主；調整分類位置；加上智財權宣告；補上自製計數器；推文時自動填入文章基本資訊。  
作者分析 FunP 的「推推王小貼紙」僅是透過 &lt;SCRIPT&gt; 動態插入一段 IFRAME，他直接擷取最終生成的 HTML：  
&lt;IFRAME src="http://funp.com/tools/buttoniframe.php?url=…" …&gt;&lt;/IFRAME&gt;  
並在佈景 PostView.ascx 中自行產生相同的 IFRAME。為了讓推文時自動夾帶網址、標題、前七十字內文及分類，他以 Server.UrlEncode 在伺服端組字串，並額外產生一個提交到 FunP 的 &lt;a&gt; 連結。經此調整後，文章頁面僅載入輕量 IFRAME，不再依賴 document.write 或 eval，也不會出現版面掛掉的情況。  
接著他修改 archive.aspx.cs，將原本顯示 Rating 的區塊改為 FunP 推文按鈕，一次為二百多篇文章、近五百顆按鈕批次產生 IFRAME。雖然 IE 在載入大量 IFRAME 時仍顯得吃力，但比起官方腳本同時執行多段 JavaScript 已大幅順暢。  
整體而言，透過直接嵌入 IFRAME 與伺服端組字串的方式，作者成功達成版面整潔、效能提升及自動帶參數推文的目標；最後並預告下一篇將分享自製的 ViewCounter Extension，用以記錄每篇文章的瀏覽量，持續優化 BlogEngine 的功能性與可維護性。

## 段落重點
### 整合動機與選擇過程
作者回顧過去在舊站加掛推文貼紙效果不佳的經驗，搬到 BlogEngine.NET 後再度面臨「要不要加社群書籤、選哪一家」的抉擇；他先試用黑米卡卻因速度慢、版面易毀而放棄，最終看上 FunP 腳本簡潔、載入快且不破版，決定全力與 FunP 整合。

### 版面與功能調整規劃
在動手寫程式前作者先列出八項具體目標：捨棄 Rating、以推文計數取代舊計數器、保留單一書籤、移除 Tags、重排分類位置、加入智財聲明、補上自製流量計數器，以及讓推文自動帶入文章資料，確保改造有清晰主題而非隨意拼貼。

### 改造前後版面對照
透過截圖展示原 CS 樣式、初搬家後樣式與最終改造成果，可以看出推文按鈕成功取代原計數器且版面更簡潔；同時移除了多餘標籤與側欄元素，使閱讀焦點更集中。

### 拆解 FunP 官方 Script
作者研究 FunP 提供的工具，發現其核心僅是 &lt;SCRIPT&gt; 動態寫出一段含參數的 IFRAME，因而決定不走繞路的 JavaScript，而是直接在佈景裡輸出同樣的 IFRAME HTML，既降低失敗風險也易於除錯。

### 在 PostView.ascx 嵌入推文 IFRAME
於 PostView.ascx 中，作者先以正則去除文章 HTML、擷取前七十字，再以 Server.UrlEncode 將網址、標題、內文及分類組成參數；最後直接輸出 &lt;IFRAME …&gt;，實現每篇文章都有即時推文按鈕且不依賴前端脚本。

### 建立一鍵推文提交連結
為避免讀者點推文後還要手動填資料，作者另行產生 &lt;a href="…push/submit/add.php?...&gt;，把同組參數帶到 FunP 發文頁，並用官方圖示做按鈕，使推文流程更順暢。

### 優化 archive.aspx 並取代 Rating
封存頁面一次列出兩百多篇文章，作者把 Rating 區塊改為 FunP 推文數顯示，於 archive.aspx.cs 動態生成 IFRAME；雖一次要載入數百 IFRAME 仍消耗資源，但比官方作法大幅減輕瀏覽器負擔。

### 效果評估與後續計畫
改造後版面穩定、不再因腳本衝突而崩毀，讀者推文操作也更直覺；作者最後預告即將發布自寫 ViewCounter Extension 以補 BlogEngine 缺乏點閱統計的缺口，並計畫持續以相同思路優化其他功能。