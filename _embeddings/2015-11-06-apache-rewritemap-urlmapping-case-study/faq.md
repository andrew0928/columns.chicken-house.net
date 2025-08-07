# Case Study: BlogEngine -> WordPress 大量(舊)網址轉址問題處理

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在將 BlogEngine 文章移至 WordPress 後必須處理舊網址轉址？
轉移後兩套系統的 URL 格式完全不同，若不轉址，外部早已存在的連結（約 400 篇 × 6 種格式 = 2,400 條）將全部失效，造成使用者與搜尋引擎取得 404。

## Q: BlogEngine 舊文章實際上出現了哪 6 種 URL 格式？
1. /post/2008/07/10/Title.aspx  
2. /columns/post/2008/07/10/Title.aspx  
3. /post/Title.aspx  
4. /columns/post/Title.aspx  
5. /post.aspx?id=GUID  
6. /columns/post.aspx?id=GUID  

## Q: 一開始以 Apache Redirect 指令為何不可行？
需要為每篇文章與每種格式各寫一條 `Redirect 301`，共約 2,400 條。  
缺點：  
1. 不易維護——任何異動都得重跑產生器。  
2. 無法處理例外（如日期錯誤）。  
3. 效能差——每個請求都要線性比對所有條件。

## Q: 改用 RewriteRule（正規表示式）後仍有哪些問題？
雖能用 1 條 RegExp 取代 4 條 Redirect，但仍需 400 條規則；維護困難且大量 RegExp 比對對 NAS 的 CPU 依舊吃重。

## Q: 最終選擇 RewriteMap 的原因是什麼？
RewriteMap 以 Hash Table 方式查表，時間複雜度 O(1)，效能比 Redirect/RewriteRule 快約 10 倍；同時只需 1 條 RewriteRule 搭配 1 份對照表即可，維護方便。

## Q: RewriteMap 轉址的實作範例是什麼？
```
RewriteEngine ON
RewriteMap slugmap "txt:/volume/slugmap.txt"
RewriteRule "^(/columns)?/post(/\d+)?(/\d+)?(/\d+)?/(.*)\.aspx" "?p=${slugmap:$5}" [R=301,L]
```
`slugmap.txt` 內為「舊 slug → WordPress 文章 ID」對照，例如：  
`GoodProgrammer1   65`

## Q: 實際成效如何？  
1. 404 數量：Google Search Console 顯示從上千筆降到剩 6 筆（皆屬可忽略之錯誤連結）。  
2. 回應時間：  
   • 10/28 啟用 W3 Total Cache 後大幅下降。  
   • 11/06 改用 RewriteMap，再下降 15–20%，平均由 1130 ms 至 907 ms。  
   • 整體效能已回到原先放在 GoDaddy 時的水準。

## Q: 若要再提升 RewriteMap 效能，有何建議？
將文字檔對照表編譯成 Apache 支援的 DBM 二進位檔，以減少磁碟 I/O 與載入時間，可進一步加速查表。