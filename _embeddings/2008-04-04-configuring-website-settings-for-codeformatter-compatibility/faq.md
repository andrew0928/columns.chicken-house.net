# 搭配 CodeFormatter，網站須要配合的設定

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼安裝 CodeFormatter 後還必須把 CSS 手動放到部落格伺服器？
CodeFormatter 產生的 HTML 本身非常簡潔，所有樣式都抽離到 CSS 檔案中。如果不把原廠提供的 CSS 貼到部落格伺服器，程式碼範例就不會有正確的語法上色與排版效果。

## Q: 在 CommunityServer (CS) 上要如何加入這段 CSS？
進入 CS 的 DashBoard→版面設定→“Custom Styles (Advanced)” 頁面，將文章中提供的 C# Code Formatter CSS 內容整段貼入並儲存即可生效。

## Q: 如何讓「copy code」按鈕能正常複製程式碼到剪貼簿？
1. 在原來的 CSS 後面再加上一段  
   ```
   .copycode { cursor:hand; color:#c0c0ff; display:none; behavior:url('/themes/code.htc'); }
   ```  
2. 把 code.htc 檔案放到 `/themes/` 目錄（路徑需與 CSS 中的 `behavior:url()` 相同）。  
3. 發文時勾選「產生出來的 HTML 會包含原始程式碼」選項。完成後，程式碼區塊標題右方的 [copy code] 連結就可正常運作。

## Q: 為什麼作者選擇用 HTC 來實作複製功能，而不是直接插入 `<script>`？
CommunityServer 會過濾 `<script>` 標籤，直接寫 JavaScript 會被擋下；HTC (HTML Component) 則能像 CSS 一樣統一管理事件，只要瀏覽器是 IE 系列即可支援，因此能迴避 CS 的安全限制。

## Q: 預覽功能做了哪些調整？
作者把預覽改寫成 HTA (HTML Application) 形式，避免直接用 IE 開啟本機 HTML 時跳出的安全警告，並在畫面中加入原作者與作者自己網站的連結。

## Q: 插件與範例檔案可以在哪裡下載？
可至以下網址下載最新版  
http://www.chicken-house.net/files/chicken/ChickenHouse.LiveWriterAddIns.zip