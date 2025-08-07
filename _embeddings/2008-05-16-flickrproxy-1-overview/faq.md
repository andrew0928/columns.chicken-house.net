# FlickrProxy #1 - Overview

# 問答集 (FAQ, frequently asked questions and answers)

## Q: FlickrProxy 的核心概念是什麼？
FlickrProxy 透過 ASP.NET HttpHandler，在「讀取網頁時」動態判斷圖片是否已經上傳到 Flickr。  
• 若尚未上傳且判定不需要上傳，就像一般網站一樣直接回傳圖檔內容。  
• 若需要上傳，則程式會自動把圖片傳到 Flickr，最後再把這個 HTTP Request 重新導向到 Flickr 上的圖片連結。  
這讓站點頻寬負擔降低，同時保留完整檔案在自己的伺服器上。

## Q: 作者為什麼不直接使用 Windows Live Writer 的 Flickr 外掛 (或其他類似 plug-in)？
1. 這類外掛是在「發文當下」一次性完成上傳與嵌入，導致日後換帳號、換服務或沒有 WLW 可用時就受限。  
2. 舊文章的圖片無法 retroactively 轉移到新服務。  
3. 作者希望把決策與動作放在伺服器端，隨時可關閉或更換設定，不被單一帳號或服務鎖死。

## Q: FlickrProxy 與 WLW + Flickr 外掛相比，最大的差別是什麼？
WLW 外掛屬於「用戶端一次性處理」，而 FlickrProxy 則是「伺服器端即時處理」。  
前者效能較好，但彈性小；後者效能略差，卻能隨時停用、更換圖床，且網站始終保有完整檔案備份。

## Q: 目前作者已證明這種做法可行嗎？
是的，作者先做了一個 POC (Proof of Concept)，在範例網頁上把所有圖片自動轉址到另一個目錄，並用 Fiddler 驗證請求流程，證實技巧可行。

## Q: 除了圖片，作者還打算把哪些檔案類型導向其他雲端服務？
• 影片：理想狀態是自動轉傳到 YouTube (目前僅做到 HTTP → RTSP 轉址)。  
• 壓縮檔 (ZIP)：目前以「虛擬資料夾」方式呈現，未來考慮自動轉存到 Microsoft SkyDrive 或類似服務。

## Q: 接下來的開發規劃是什麼？
作者打算把先前寫的另外兩個 HttpHandler 與本次的 FlickrProxy 整合，做成一套統一的 provider 架構，並陸續發表後續文章。