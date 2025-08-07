# 從 CommunityServer 2007 到 BlogEngine.NET

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者最後決定把網站從 CommunityServer 2007 搬到 BlogEngine.NET？
作者本來就有搬家的想法，評估後發現 BlogEngine.NET 採用標準的 ASP.NET Master／UserControl 架構、程式碼精實、開發環境容易建立，因此只花了幾天就拍板決定改用 BlogEngine.NET。

## Q: 匯出／匯入文章時使用了什麼格式與工具？
利用 BlogML。CommunityServer 2007 透過 CodePlex 上的匯出工具產生 BlogML 檔，再用 BlogEngine.NET 官方提供的 ClickOnce WinForm 匯入工具（透過 Web Service）把 BlogML 載入新系統。

## Q: 在 BlogEngine.NET 匯入 BlogML 時遇到的 Exception 是什麼？怎麼解決？
匯入時 BlogEngine.NET 把文章的修改時間抓成 0000/01/01 00:00:00.000，再扣台灣時區 -8 小時後變成負值而丟出 Exception。作者打開 Visual Studio 2008，把產生錯誤的那行程式碼拿掉後就能順利匯入。

## Q: 搬家完成後立刻冒出的主要問題有哪些？
1. 圖檔連結仍是舊站的絕對網址  
2. ARTICLE 文章沒被匯入  
3. 站內文章互連失效  
4. 站外舊網址全變 404  
5. BlogEngine.NET 沒有內建 View Count  
6. 舊的瀏覽次數無法直接搬過去  
7. 版面需要加廣告與自訂控制項  
8. 原先在 CommunityServer 動手加的功能要自己重寫

## Q: BlogEngine.NET 沒有 View Count 功能，作者怎麼補上？
安裝 MosesOfEgypt 撰寫的「View Count Extension」，並自行撰寫程式把舊系統的瀏覽數據匯入新系統。

## Q: 站內文章連結全失效時，作者用什麼方法修復？
採兩階段 (2-pass) 處理：  
第一輪先把文章匯入並在 BlogML 中記下新網址與 PostID；  
第二輪重新讀取 BlogML，對每篇文章內容做 Search & Replace，把舊連結換成新格式。

## Q: 如何讓外部仍指向舊 CommunityServer URL 的連結自動轉到正確的新文章？
在 BlogEngine.NET 加寫一段 URL 轉向程式，能解析舊格式 URL，先顯示提示頁再自動導到對應的新網址，確保外部連結不會 404。

## Q: 作者對 BlogEngine.NET 原始碼的整體評價是什麼？
程式碼量不多但架構乾淨清楚，建置開發環境非常容易，修改難度大約只有 CommunityServer 的三分之一，讓人改起來很舒服。