# 三個好用的 ASP.NET HttpHandler

# 問答集 (FAQ, frequently asked questions and answers)

## Q: ChickenHouse.Web.HttpHandlers.MediaServiceHttpHandler 可以解決什麼問題？
它讓放在網站上的大型 video / audio 檔案自動轉址到 Windows Media Service 播放，避免佔用網站頻寬；對使用者來說依舊點選原本的 HTTP 連結即可收看或收聽。

## Q: 使用 MediaServiceHttpHandler 有什麼前提？
只要使用者的 Windows Media Player 版本在 7.0 以上，轉址與播放就會全自動完成，無需額外設定 mms:// 或 http://。

## Q: ChickenHouse.Web.HttpHandlers.RssMonitorHttpHandler 的主要功能是什麼？
它會把指定目錄下的所有檔案視為「文章」，自動產生 RSS Feed；新增檔案時，RSS Reader 便能像追蹤 blog 新文一樣通知使用者。

## Q: 這個 RSS 監看 Handler 對於純 *.html 的靜態網站有何幫助？
站長不需做任何額外動作，整個靜態網站立即擁有「RSS 訂閱」能力，方便讀者追蹤網站中新加入的 HTML 檔案。

## Q: ChickenHouse.Web.HttpHandlers.ZipVirtualFolderHttpHandler 如何減少維護相簿網頁時的檔案重複？
它把 *.zip 檔視為一個「虛擬目錄」，可直接線上瀏覽或連入 ZIP 內檔案，站長只要上傳一次 ZIP 就同時滿足「打包下載」與「線上瀏覽」兩種需求，避免維護兩份內容。

## Q: 使用 ZipVirtualFolderHttpHandler 時，常見的存取方式與範例 URL 是什麼？
1. 下載整個 ZIP：  
   http://www.chicken-house.net/files/chicken/slide.zip?download  
2. 線上瀏覽 ZIP 內容：  
   http://www.chicken-house.net/files/chicken/slide.zip  
3. 直接連到 ZIP 內檔案（如 default.htm）：  
   http://www.chicken-house.net/files/chicken/slide.zip/default.htm  

## Q: 作者提供的三個 HttpHandler 範例程式碼在哪裡下載？
可從以下連結取得：  
[ChickenHouse.Web.zip](/wp-content/be-files/ChickenHouse.Web.zip)