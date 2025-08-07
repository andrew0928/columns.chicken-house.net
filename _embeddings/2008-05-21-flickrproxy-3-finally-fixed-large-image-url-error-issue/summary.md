# FlickrProxy #3 - 終於搞定大圖網址錯誤的問題

## 摘要提示
- 上傳後網址失效: 上傳成功但透過 API 取得的大圖網址常出現「Photo not available」。
- PhotosGetInfo 侷限: 取得的 MediumUrl、LargeUrl 其實是依 ID 以固定格式拼湊，並非 Flickr 真實網址。
- Flickr 網址調整: Flickr 曾修改圖片存放規則，小圖不再產生 Large 版本，導致舊格式失效。
- 轉用 PhotosGetSizes: 透過 PhotosGetSizes 直接向 Flickr 查詢可用尺寸與真實網址，完全解決錯誤。
- 除錯教訓: 問題根源在未詳讀文件、僅憑方法名稱猜用法，造成不必要的排錯時間。
- 程式碼前後對照: 原以 PhotoInfo 逐一嘗試 Medium/Large/Original，改為迴圈讀取 SizeCollection。
- 不需多餘驗證: 失去不確定性後，可移除額外的 CheckFlickrUrlAvailability 檢查。
- FlickrProxy 完備: 修正後的 FlickrProxy 邁入可正式使用的階段。
- API 理解重要: 開發時應掌握 API 背後資料來源與規格變動，避免踩坑。
- 經驗紀錄: 透過部落格分享除錯過程，方便日後追溯與他人參考。

## 全文重點
作者在開發 FlickrProxy 時，遇到上傳照片雖然成功卻無法正確顯示大圖的問題：使用 FlickrNet 的 PhotosGetInfo(photoId) 取回 MediumUrl 與 LargeUrl 後，部分圖片點擊後顯示「Photo not available」。初期以為是暫時性讀取失敗，然而比對 Flickr 網站實際圖片網址才發現 API 回傳的有時與線上顯示的不一致。追查程式碼後才明白，PhotosGetInfo 其實只回傳一組用來「拼湊」網址的 ID；若圖片尺寸不足以生成 large 版本，Flickr 會直接跳到 original，造成以舊格式組出的 large 連結失效。換言之，並非 API 回傳錯誤，而是開發者對運作方式誤解，再加上 Flickr 曾更新網址規則，才造成顯示落差。  
為徹底排除風險，作者改用另一個 API：PhotosGetSizes(photoId)。此方法直接呼叫 Flickr 伺服器查詢實際存在的各種尺寸，並一次取得 label、source、url、width、height 等資訊，因此不再需要自行判斷或驗證網址有效性。程式碼修改後，作者將原先嘗試抓取 Medium→Large→Original 的三段式寫法，替換成迴圈遍歷 SizeCollection，把所有可用尺寸寫入快取 XML，顯示層再按需取用對應大小即可。如此不僅解決大圖錯誤，也簡化了檢查流程，讓 FlickrProxy 進入穩定可用階段。最後作者自勉：遇到問題勿急於下結論，應先詳閱官方文件，理解 API 背後機制，以免重蹈覆轍。

## 段落重點
### 問題描述
上傳照片後雖能取得 photoId，但透過 PhotosGetInfo 取得的 LargeUrl 有時顯示失敗，造成展示大圖時常出現「photo not available」。

### 原因分析
PhotosGetInfo 僅提供 ID 讓程式依既定格式組合網址；Flickr 更新過路徑規則，若圖片過小不產生 Large 版，就會導向 Original，導致舊格式拼出的 large 連結無效。

### 解決方案
改採 PhotosGetSizes 直接向 Flickr 查詢實際可用尺寸與真實網址，避免自己拼湊與版本差異問題，並一次取得完整尺寸清單以供前端選用。

### 程式碼修改前後
舊版程式碼以 Medium→Large→Original 逐一嘗試並透過 CheckFlickrUrlAvailability 驗證；新版以 foreach 迴圈讀取 SizeCollection，將 label、source、url、width、height 寫入 XML 快取，簡潔且無失敗風險。

### 經驗與結語
問題並非 API「錯誤」，而是開發者對其機制了解不足；透過文件與論壇搜尋後找到關鍵 API 即迎刃而解。修正後的 FlickrProxy 更穩定，也提醒自己與讀者開發前要做足功課。