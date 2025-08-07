# FlickrProxy #2 - 實作

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 開發 FlickrProxy 的主要目的是什麼？
FlickrProxy 旨在讓 Blogger 保持原本「直接把圖檔丟到部落格」的使用習慣，同時自動把圖片轉存到 Flickr，之後再以 302 Redirect 的方式把讀取圖片的流量導向 Flickr，達到節省 Blog 端頻寬且隨時可還原的效果。

## Q: FlickrProxy HttpHandler 處理一張圖片的完整流程是什麼？
1. 接收瀏覽器對圖片的 HTTP Request，判斷是否符合轉存條件（目錄、大小等）。  
2. 檢查 ASP.NET Cache 或暫存檔，若已存在對應 Flickr URL，直接 302 Redirect。  
3. 若 Cache 不存在：  
   ‑ 計算檔案 Hash、建立 Cache 檔。  
   ‑ 透過 Flickr API 上傳圖片並取得 photoID 與各 Size 的 URL。  
   ‑ 以程式實際去抓 URL，找出第一個可用（通常由 Medium → Large → Original 測試）。  
   ‑ 將 URL 與 photoID 寫入 Cache，最後 302 Redirect 至該 URL。

## Q: 要讓 FlickrProxy 在 IIS／ASP.NET 環境正常攔截 *.jpg，必須做哪些設定？
1. 在 IIS「應用程式對應」把 *.jpg 指到 aspnet_isapi.dll，讓要求先進入 ASP.NET。  
2. 在 Web.config 全域 httpHandlers 區塊宣告：  
   `<add path="*.jpg" verb="*" type="System.Web.StaticFileHandler" />`  
   讓預設 *.jpg 仍能正常顯示。  
3. 再於特定目錄（如 ~/storage）利用 `<location>` 重綁：  
   `<add path="*.jpg" verb="*" type="ChickenHouse.Web.HttpHandlers.FlickrProxyHttpHandler,App_Code" />`  
   只攔截該目錄內的圖片並交由 FlickrProxy 處理。

## Q: 上傳到 Flickr 之前，程式需要準備哪些授權資訊？
必須先取得三項憑證：  
1. Flickr API Key  
2. Shared Secret Key  
3. Auth Token（使用者登入並授權後產生）  
有了這三組序號後，`Flickr flickr = new Flickr(apiKey, sharedSecret); flickr.AuthToken = token;` 即可正常呼叫 Upload 與其他 API。

## Q: 程式如何挑選最終要使用的 Flickr 影像 URL？
利用 `CheckFlickrUrlAvailability()` 依序測試 `MediumUrl`、`LargeUrl`、`OriginalUrl`，哪個首先成功回應即採用；若途中發生例外則跳出迴圈，保留最後一個可用的（尺寸最大的）網址。

## Q: 對最終瀏覽者而言，使用 FlickrProxy 與一般顯示圖片有何差異？
瀏覽者看不出任何差別，HTML 與圖片網址都保持原狀；唯一的變化是第一次載入圖片時瀏覽器收到 302 Redirect 轉向 Flickr，之後所有流量都直接向 Flickr 取圖，Blog 伺服器不再負擔該圖片的下載頻寬。

## Q: 實際測試結果證明了什麼？
以 Fiddler 監看可見：  
1. 讀取 `smile_sunkist.jpg` 先收到 302 Redirect。  
2. 瀏覽器隨即改向 Flickr URL 下載圖片並正常顯示。  
登入作者 Flickr 帳號也能看到同一張圖已被自動上傳，證明 FlickrProxy 的自動上傳、建 Cache 與重新導向流程全部生效。