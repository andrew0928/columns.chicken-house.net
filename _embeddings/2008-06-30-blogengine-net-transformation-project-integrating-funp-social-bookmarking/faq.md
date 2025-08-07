# [BlogEngine.NET] 改造工程 - 整合 FunP 推推王

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者最後決定與哪一個共用書籤服務整合？  
作者最終只整合了「FunP 推推王」，並放棄了黑米等其他服務。

## Q: 為什麼作者捨棄黑米而選擇 FunP？  
黑米卡載入速度較慢，且在同一頁放置過多標籤時常導致版面掛掉；相對地，FunP 的 Script 撰寫風格較合作者胃口、速度較快，也沒有破壞版面的問題，因此作者改用 FunP。

## Q: 作者用什麼方式取代 BlogEngine.NET 內建的 Rating 機制？  
作者直接以 FunP 的推文按鈕取代 Rating，並在 PostView.ascx 及 archive.aspx.cs 中嵌入 `IFRAME`，顯示 FunP 推文次數，完全停用 BlogEngine 內建的 Rating。

## Q: 作者對部落格版面與功能做了哪些主要調整？  
1. 移除內建 Rating，改用 FunP 推文。  
2. 以推文按鈕取代原 CS 樣式中的計數器。  
3. 只保留一套共用書籤（FunP），刪除其他。  
4. 停用 Tags，改以分類為主。  
5. 將分類區塊由右下移至右上。  
6. 加入智慧財權聲明以防止盜文。  
7. 自行補上文章計數器（於下一篇詳述）。  
8. 推文時自動帶入文章標題、內文與標籤等資訊。

## Q: 為什麼作者直接輸出 `<IFRAME>` 而不使用 FunP 官方提供的 JavaScript？  
官方 Script 透過 `document.write` 或 `eval` 產生 HTML，除錯不易且效能較差；作者直接輸出帶參數的 `<IFRAME>`，程式碼單純、效能較佳，也較不會造成版面問題。

## Q: 作者如何在 PostView.ascx 產生 FunP 推文按鈕？  
在伺服端先將文章連結、標題、內文片段及分類進行 URL Encode，之後輸出一段 `<IFRAME>`（顯示推文次數）與 `<a>`（發起推文）的 HTML，達到推文與顯示計數的功能。

## Q: archive.aspx 頁面一次要載入上百顆推文按鈕時，作者採用了什麼作法？  
作者同樣以 `<IFRAME>` 方式取代原本顯示 Rating 的欄位，在 `archive.aspx.cs` 中以程式動態產生含 FunP 參數的 `<IFRAME>`，雖一次載入四、五百個 `IFRAME` 仍稍耗效能，但已較官方 Script 流暢。

## Q: 完成整合後的實際效果如何？  
版面不再因載入書籤 Script 而掛掉，載入速度明顯改善；唯在封存頁一次載入大量 `IFRAME` 時 IE 仍會吃力，但整體觀看及操作上已順眼許多。

## Q: 下一篇文章將介紹什麼主題？  
作者預告下一篇將釋出自製的「PostViewCounter Extension」，用來統計每篇文章的點閱率。