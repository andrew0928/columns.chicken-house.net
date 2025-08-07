# Windows Live Writer - Plugin 處女作...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Windows Live Writer 內建的圖片上傳有什麼致命缺點，讓作者決定自己寫外掛？
Windows Live Writer 會把所有透過它上傳的圖檔再存成一次 JPEG。由於 JPEG 是破壞性壓縮，畫質會變差，而且 WLW 使用的品質值不低，檔案大小常常反而變大，造成「畫質變差、檔案變肥」的兩敗局面。

## Q: 作者寫的外掛如何解決這個 JPEG 重壓縮的問題？
外掛讓使用者在「Insert → 插入圖片(從網路芳鄰)」時，先從設定好的 UNC 網路分享挑圖；外掛會把圖片複製到對應的網站目錄，然後直接在文章裡插入正確的 URL，整個流程跳過 WLW 的重壓縮機制。

## Q: 要使用這個外掛，需要在 Windows Live Writer 裡做哪些設定？
1. 把外掛 DLL 放到 WLW 的 Plugins 資料夾。  
2. 開啟 WLW，進入 Tools → Preferences → Plugins。  
3. 在新出現的外掛名稱旁按 [Options]，填入「UNC 路徑」與對應的「URL」。設定完成後即可使用「插入圖片(從網路芳鄰)」功能。

## Q: 為什麼作者沒有直接用 MetaBlog API 來上傳圖片？
作者測試後發現 WLW 的外掛機制無法取得使用者的 Weblog 帳號與密碼。這大概是為了安全性（避免外掛偷密碼），導致無法在外掛內呼叫 MetaBlog API 上傳圖片，因此此方案被放棄。

## Q: 這個外掛目前能下載或正式使用嗎？
不能。作者表示目前版本只是「自爽」作品，缺乏防呆機制，也不確定 Microsoft 之後會不會修掉 WLW 的圖片問題，暫時不打算公開 DLL。如需後續版本，可能會改寫成可設定 Blog URL、帳號與密碼的 MetaBlog API 版本，再視情況釋出。