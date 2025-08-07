# Windows Live Writer 民間外掛解法：避免圖片二次壓縮

# 問題／解決方案 (Problem/Solution)

## Problem: Windows Live Writer 上傳圖片會被重新存成 JPEG，導致畫質下降與檔案變大  

**Problem**:  
在 Windows Live Writer（以下簡稱 WLW）撰寫部落格文章並插入圖片時，不論使用 MetaBlog API 或 FTP，WLW 都會先將圖片重新轉存為 JPEG 後再上傳。結果常見兩大困境：  
1. JPEG 為破壞式壓縮，二次存檔後畫質變差。  
2. WLW 預設的 JPEG Quality 值偏高，檔案大小往往比原圖更肥。  

**Root Cause**:  
WLW 內部的「Insert Picture」流程被設計成：  
• 讀取圖片 → 重新輸出為 JPEG → 透過 MetaBlog API / FTP 上傳。  
此流程無暴露可設定的「關閉再次壓縮」或「自訂 Quality」介面，導致使用者無從調整，只能接受 WLW 的重新編碼策略。  

**Solution**: 自行撰寫 WLW 外掛，改用「先手動複製、後插入網址」的流程  
1. 利用 Windows Live Writer SDK，以 .NET 開發一支 Plugin。  
2. 在 Plugin Option 內預先對應：  
   • 圖片實體存放的 UNC 網路路徑 (e.g. `\\NAS\BlogImages`)  
   • 圖片於網站端公開的 URL 前綴 (e.g. `https://myblog.com/images`)  
3. 使用者在 WLW 選單執行「Insert → 插入圖片(從網路芳鄰)」後：  
```
workflow
┌──────────────┐              ┌───────────────┐
│OpenFileDialog│───選圖───▶│ Plugin Logic │
└──────────────┘              └───────────────┘
        │ 1. 將選取的本機檔案 Copy 至 UNC 目的地
        │ 2. 組出對應的公開 URL
        ▼
WLW 編輯器將圖片以 <img src="公開 URL"> 方式插入
```  
4. 因為檔案已經直接被複製到最終儲存位置，WLW 只需插入「網址」，整個 JPEG 重新轉存步驟完全被繞過。  

關鍵點：  
• 把「圖片檔案搬運」與「文章編輯」兩個職責拆開。  
• 透過事先設定好的路徑對應，Plugin 能自動完成複製與 URL 轉換，使用者體驗維持「選檔即完成」。  

**Cases 1**: 個人部落格實測  
背景：拍攝相片原始檔 2.1 MB，原本用 WLW 直接上傳後變 2.8 MB，畫質還出現色階。  
使用 Plugin 後：  
• 檔案大小維持 2.1 MB（零再壓縮）。  
• 文章編輯流程時間差幾乎為 0（選完圖即插入）。  

**Cases 2**: 家人使用情境  
背景：家人習慣使用 WLW，但對圖片品質要求高。  
成效：啟用外掛後，家人不再需要先用「Insert Picture From Web」繞路，完全無痛升級；部落格相簿畫質與相簿平台一致，客訴率 0。  


## Problem: WLW Plugin 無法直接取得使用者的 Weblog 帳號密碼，難以走 MetaBlog API 上傳

**Problem**:  
作者原本打算在外掛裡呼叫 MetaBlog API 的 `newMediaObject` 來上傳圖片，卻發現 Plugin Framework 沒有任何介面可以取得目前 WLW 已設定好的部落格帳號、密碼與 Blog URL。開發者若強行實作，只能要求使用者再次輸入一組帳號資訊，體驗不佳。  

**Root Cause**:  
• WLW Plugin 被官方定位在「編輯層」（Editing Layer），而非「發佈層」（Publishing Layer）。  
• 為避免安全風險（外掛偷取使用者憑證），Framework 刻意不傳遞帳密給外掛。  

**Solution**: 改採「路徑對應＋檔案複製」方式，完全捨棄需要帳密的 MetaBlog API 流程  
• Plugin 透過 UNC 路徑對應，直接做檔案複製，省去與 Blog 後端認證的需求。  
• 若日後需要真正的 API 上傳，可在 Option 畫面額外讓使用者自填 Blog URL / 帳號 / 密碼，再自行呼叫 MetaBlog API；此設計留做下一版擴充。  

**Cases**:  
現行版本僅 2 小時完成 MVP，因不需管理帳號安全議題，整體維護成本幾乎為 0。若 Microsoft 後續版本修正圖片壓縮問題，只需停用 Plugin 即可，影響面最小化。  