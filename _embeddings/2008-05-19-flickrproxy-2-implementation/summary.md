# FlickrProxy #2 - 實作

## 摘要提示
- 需求／目標: 讓 Blogger 不改任何習慣即可把圖片自動轉存至 Flickr 並節省網站頻寬。  
- 技術核心: 以 ASP.NET 自訂 HttpHandler 攔截 *.jpg 請求並 302 Redirect 至 Flickr。  
- 系統流程: 判斷是否需轉存→檢查快取→上傳 Flickr→寫入快取→重新導向。  
- 快取機制: 同時運用 ASP.NET Cache 與磁碟檔案 (Hash+XML) 儲存對應資訊。  
- FlickrNet 應用: 需 API Key、Secret、Token 完成 OAuth 認證並呼叫 UploadPicture。  
- IIS 配置: 將 *.jpg 映射到 aspnet_isapi.dll，再以 <location> 覆寫特定目錄 Handler。  
- Web.config: 一般 *.jpg 走 System.Web.StaticFileHandler，~/storage/*.jpg 走 FlickrProxyHttpHandler。  
- 程式重點: BuildCacheInfoFile() 上傳並回傳可用之最大尺寸 URL；CheckFlickrUrlAvailability() 驗證可下載。  
- 測試結果: 第一次請求產生 302 並上傳檔案，之後所有請求皆直接從 Flickr 下載。  
- 優勢概述: 無須更動 HTML 與上稿流程，可隨時移除，對資料零侵入，高度可回復。

## 全文重點
作者為了減輕部落格伺服器的影像流量，同時避免改動任何使用者操作流程，設計了一個名為 FlickrProxy 的 ASP.NET HttpHandler。此 Handler 專門攔截指定資料夾內的 *.jpg 請求，依照「先快取、後上傳、再重導向」的流程，將圖片自動上傳至 Flickr，並把瀏覽器重導向到 Flickr 所提供的影像 URL。

整套機制的基礎在於 IIS 與 ASP.NET 的組態。首先必須在 IIS 中將 *.jpg 指定給 .NET ISAPI，讓所有圖片請求都有機會被程式碼攔截；其次在 Web.config 內先讓一般圖片維持原本由 System.Web.StaticFileHandler 處理，再透過 <location> 細分出 ~/storage 目錄改由 FlickrProxyHttpHandler 接手。如此即可確保只有目標目錄的圖片會被轉存，其他靜態檔案仍維持原狀。

Handler 實作上先以檔案內容 Hash 值產生對應的 XML 快取檔，並於 ASP.NET Cache 保存相同資訊。若快取存在便直接取出 Flickr URL 並回傳 302；反之則呼叫 FlickrNet API 上傳圖片，獲取 photoID 與各尺寸 URL，再檢查可用性後寫入快取並重導向。為確保 API 可用，需事先向 Flickr 申請 API Key 與 Secret，並透過示範程式取得一次性 Token。由於 Flickr 伺服器偶爾對特定尺寸回應「photo not available」，程式使用 CheckFlickrUrlAvailability() 逐一嘗試 Medium、Large、Original 三種連結，自動挑選最大且可用的版本。

實際測試顯示，第一次載入圖片時瀏覽器收到 302，Handler 立即上傳檔案；上傳成功後同一與後續請求皆直接命中快取並被導向 Flickr，網頁端完全無感，卻能節省部落格後端頻寬。整個專案完成後僅需調整設定與部署單一 Handler，即可隨時啟用或停用，不會破壞原始資料結構。

## 段落重點
### 計畫目標與動機
作者希望讓家人或 Blogger 不必理解 Flickr，即可繼續以原有方式上傳圖片。為節省伺服器流量，目標是在不改 HTML、不改上稿流程的前提下，自動把瀏覽器請求導向 Flickr；同時必要時可隨時還原，不影響既有資料。

### 系統流程與 UML 設計
程式採三階段流程：1.接收請求與條件判斷；2.檢查 ASP.NET Cache 與磁碟快取；3.若無資料則計算 Hash、上傳 Flickr、寫快取，再把瀏覽器 302 Redirect 到新網址。作者並繪製 UML Sequence Diagram 說明整個呼叫時序。

### IIS 與 ASP.NET 組態
因 IIS 會直接回傳靜態檔，必須先把 *.jpg 映射到 aspnet_isapi.dll。接著於 Web.config 內增加 httpHandlers 設定，先用 System.Web.StaticFileHandler 當預設，再在 <location path="storage"> 區段指定所有 *.jpg 交給 FlickrProxyHttpHandler。如此既可攔截目標圖片，又不影響網站其他檔案。

### 主要程式碼結構
Handler 入口先確保快取目錄存在，之後判定 CacheInfoFile 是否存在：若有則直接從 ASP.NET Cache 或 XML 取回 Flickr URL；若無則呼叫 BuildCacheInfoFile() 上傳並建立資料。BuildCacheInfoFile() 使用 FlickrNet.UploadPicture() 傳檔並取回 PhotoInfo，再透過自訂 CheckFlickrUrlAvailability() 測試各尺寸，選取最大可用 URL。最後把來源路徑、Flickr URL、photoID 寫入 XML 並回傳。

### Flickr API 認證與上傳
FlickrNet 必須取得 API Key、Shared Secret 以及使用者授權的 Token。作者利用套件範例程式引導一次性登入取回 Token，之後便可於程式中設定 flickr.AuthToken 進行自動上傳。傳檔後再調用 PhotosGetInfo() 取得不同尺寸連結，以解決 Flickr 偶爾回應「photo not available」的不確定性。

### 測試結果與效益評估
在測試網頁中嵌入一張 /storage/smile_sunkist.jpg 圖片，第一次載入時 Fiddler 顯示 302 Redirect，且 Flickr 相簿已出現該圖；之後任何人訪問同一 URL 都直接向 Flickr 下載。對使用者而言畫面無差異，對站台而言只在首次瀏覽時付出一次上傳流量，其後完全節省圖片傳輸成本，並且因採設定與 Handler 實作，可隨時移除而不影響資料。