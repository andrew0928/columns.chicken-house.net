# FlickrProxy #3 - 終於搞定大圖網址錯誤的問題

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼透過 PhotosGetInfo 取得的 LargeUrl 有時候會失效？
Flickr 曾經調整過圖片網址的組成規則：當上傳的圖片尺寸不大時，系統會判定不需要另外產生「Large」尺寸，而直接引用原始檔 (Original)。PhotosGetInfo 只回傳一堆與圖片相關的 ID，再按照舊規則「湊」出各種尺寸的網址；若實際上沒有 Large 大小，就會產生錯誤的 URL，導致圖片無法顯示。

## Q: 解決大圖網址錯誤最直接的方法是什麼？
改用 PhotosGetSizes() API。這支 API 會直接回傳 Flickr 目前實際可用的每一種尺寸（含 label、source、url、width、height 等），因此不會產生不存在的尺寸網址，從而避免圖片掛掉的問題。

## Q: PhotosGetInfo 與 PhotosGetSizes 兩種 API 的主要差異是什麼？
1. PhotosGetInfo 只給出圖片相關 ID，再依照固定規則組出多種尺寸的 URL；如果 Flickr 沒產生該尺寸，組出的 URL 可能失效。  
2. PhotosGetSizes 直接向 Flickr 查詢並回傳「實際存在」的各種尺寸及對應網址，不受尺寸是否存在的問題影響，因此較為保險可靠。