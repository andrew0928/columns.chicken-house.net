# 三個好用的 ASP.NET HttpHandler

## 摘要提示
- 懶人動機: 作者因「懶」而開發三個 Handler，目的是減少網站維護的重複與麻煩工作。  
- MediaServiceHttpHandler: 自動將影音檔請求由 HTTP 轉向 Windows Media Service，節省個人 ADSL 主機頻寬。  
- RssMonitorHttpHandler: 監控目錄下所有檔案並動態產生 RSS，讓純靜態網頁也能被 RSS Reader 訂閱。  
- ZipVirtualFolderHttpHandler: 讓 .zip 檔在網站中被視為虛擬目錄，可瀏覽內容或下載整包檔案。  
- 頻寬優化: 透過流媒體服務分流，避免大檔案直接佔用 Web 伺服器頻寬。  
- 靜態網頁升級: 不改動 HTML，就能立即擁有「最新檔案通知」的 RSS 功能。  
- 一檔多用: 上傳一份 zip 既能提供線上瀏覽又能整包下載，降低維護成本。  
- 使用門檻低: 只需在 web.config 註冊 Handler，不必改動現有程式碼或檔案結構。  
- 範例完整: 文章提供實際 URL 測試範例與操作說明。  
- 原始碼分享: 可下載 ChickenHouse.Web.zip 直接套用或參考學習。  

## 全文重點
作者在個人網站經營過程中，經常因為頻寬不足、檔案同步與更新通知等瑣事而困擾。為一勞永逸，他利用 ASP.NET 提供的 HttpHandler 機制，寫出三支輕量卻實用的 Handler，不需改動既有頁面或資料結構，只要在 web.config 內註冊即可立即啟用。  
第一支 MediaServiceHttpHandler 針對影音檔（video/audio）進行攔截，當使用者原本以 HTTP 播放大檔時，Handler 會自動判斷並將連線改導向至 mms:// 位址，由 Windows Media Service 接手串流播放。如此可大量減輕 Web 主機，尤其是以 ADSL 架站的頻寬壓力，前端播放器只要版本 7.0 以上，整個過程對使用者透明。  
第二支 RssMonitorHttpHandler 主要解決「不記得目錄裡何時新增檔案」的困擾。它會把指定目錄下的每一個檔案當作文章節點，動態輸出符合 RSS 2.0 格式的 feed。只要訂閱該 feed，就能像訂閱 Blog 一樣，即時得知有無新檔案，特別適合全由 .html 組成的純靜態網站，讓「沒有後端程式」的站台也能輕鬆加入 RSS 功能。  
第三支 ZipVirtualFolderHttpHandler 則解決相簿或檔案下載站常見的「一份線上預覽、一份壓縮檔下載」雙重維護問題。它會把任何副檔名為 .zip 的檔案視為子目錄：在網址後面加 / 即可瀏覽 zip 內目錄與檔案；加 /default.htm 之類檔名則直接讀取壓縮包內的指定檔；加 ?download 參數則維持傳統整包下載。結果是只需上傳一個 zip，就同時滿足線上瀏覽與批次下載兩種需求，大幅精簡備份與更新作業。  
全文充滿「簡化作業流程」的精神：頻寬分流、靜態網頁 RSS 化、壓縮包虛擬目錄化，全部建立在 ASP.NET 既有的可擴充管線上，不改程式、不搬檔案也能立即享受便利。文末作者提供 ChickenHouse.Web.zip 讓讀者可以直接下載程式碼，若覺得實用，留言支持即可。

## 段落重點
### 前言
作者坦言一切靈感都來自「懶」：個人站台頻寬小、檔案多且常更新，既不想教家人區分不同協定，也不願意重複維護檔案，因此決定動手寫三支專用 HttpHandler。

### MediaServiceHttpHandler
功能：攔截影音檔請求，自動將 HTTP 連線改導向 mms:// 串流。  
效益：使用者無感切換，網站避免大檔佔據頻寬；僅需播放器 7.0 以上版本即可支援。  
適用情境：個人 ADSL 架站、影音資料庫、大量串流需求的網站。

### RssMonitorHttpHandler
功能：掃描特定目錄，將每個檔案視為文章節點輸出 RSS。  
效益：靜態網頁立即擁有「新增檔案通知」功能，讀者可用 RSS Reader 追蹤。  
範例：作者以小孩成長照片的靜態相簿示範，無須額外程式即可訂閱。

### ZipVirtualFolderHttpHandler
功能：將 .zip 視為虛擬資料夾，可線上瀏覽、指定檔案直連或整包下載。  
效益：一次上傳、一份維護，解決線上預覽與壓縮下載的雙份檔案困擾。  
網址示例：  
- /slide.zip?download  → 直接下載  
- /slide.zip/          → 瀏覽壓縮包內容  
- /slide.zip/default.htm → 直開壓縮包內檔案  

### 結語與下載
三支 Handler 都是為了省事而生，部署簡單、立即見效；作者附上 ChickenHouse.Web.zip 原始碼，鼓勵有同樣需求的人自行下載使用並回饋意見。