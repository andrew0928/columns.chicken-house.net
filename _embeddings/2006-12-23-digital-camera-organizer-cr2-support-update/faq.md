# 歸檔工具更新 - .CR2 Supported

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這次更新的歸檔工具是否已經支援 Canon 的 .CR2 RAW 檔？
是的，經過實際測試後，工具已經能夠正確處理 .CR2 檔案。

## Q: 在處理 .CR2 檔時，與先前支援的 RAW 格式有何差異？
主要差異是 .CR2 檔不會額外產生 .thm 縮圖檔，因此由 RAW 直接轉存的 JPG 不含完整 EXIF；其餘 Library 的呼叫方式與其他 RAW 格式完全相同。

## Q: 使用 Canon DSLR 時，還需要另外將 .CR2 轉成 .JPG 嗎？
通常不需要。多數 Canon DSLR 會在拍攝時另存一張原圖大小的 JPG，已能滿足一般需求，自行再轉檔意義不大。

## Q: MediaFilerFileExtensionAttribute 在這次更新裡做了哪些調整？
它改為可用逗號（,）一次指定多個副檔名，並配合 Factory Pattern 的 Create() 讓同一個 MediaFiler 能同時處理多種副檔名。

## Q: 設定檔新增了哪一段與 .CR2 相關的配置？
在設定檔中新增了 pattern.cr2，用來描述 .CR2 的檔案規則。

## Q: 更新檔案可以從哪裡下載？
可透過以下連結取得：  
http://www.chicken-house.net/files/chicken/ChickenHouse.Tools.DigitalCameraFiler.Binary.zip

## Q: 作者用來測試 .CR2 支援的相機樣本來源是什麼？
作者主要使用公司老闆的 Canon 20D 拍攝的樣本檔進行測試，文中也提到朋友新購入的 Canon 5D。

## Q: 作者在 Canon G2 + 外接閃光燈下遇到的 RAW 解析問題是什麼？
若外閃因回電不足未能觸發，拍出的曝光不足 RAW 檔在 Microsoft Raw Image Viewer 與其 Library 會解碼失敗並拋出例外。