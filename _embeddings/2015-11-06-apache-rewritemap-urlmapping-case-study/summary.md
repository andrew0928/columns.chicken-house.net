# Case Study: BlogEngine -> WordPress 大量舊網址轉址處理

## 摘要提示
- 轉站需求: BlogEngine 移轉至 WordPress 後產生約 2400 筆舊網址必須轉址。
- URL 類型: 舊系統共歸納出 6 種不同格式，含日期、無日期與 GUID 參數。
- 初步做法: 以 Apache Redirect 301 逐條列出 2400 條規則，先解燃眉之急。
- 缺點暴露: Redirect 難維護、無法彈性處理例外，又造成效能衰退。
- 正規式改良: 改用 RewriteRule＋RegExp，將 400 篇文章濃縮成 400 條規則。
- 效能疑慮: 研究 Mozilla Benchmark 發現大量 RewriteRule 仍拉低回應速度。
- 核心方案: 引入 RewriteMap，利用 Hash Table 概念 O(1) 查表，僅一條規則完成轉址。
- 實作重點: 建立 slug‐id 對照檔，並轉為 dbm 檔以提升 I/O 效率。
- 效益數據: Google Search Console 顯示 11/06 後 404 連結急降，平均回應時間再降 15~20%。
- 維運便利: 規則縮減、易於增修，後續僅需更新映射表即可。

## 全文重點
作者將部落格由 BlogEngine 遷移至 WordPress，發現舊文章約 400 篇，而外部連入的 URL 有六種不同格式，合計 2400 筆以上需重新導向。第一版直接以 Apache Redirect 301 列出全部規則雖可運作，但維護困難、無法容錯且效能低落。第二版利用 RewriteRule 與正規表示式縮減規則數量，可對付格式差異及錯字，但仍需 400 條規則，CPU 消耗仍高。為尋求最佳解，作者參考 Mozilla 基準測試，決定採用 RewriteMap。RewriteMap 透過 Hash Table 查詢，將大量比對轉為 O(1) 查表，僅需一條 RewriteRule 搭配外部對照檔便能處理所有舊網址，同時支援例外與維護需求。最終以文字檔或 dbm 檔存放 slug 對 WordPress 文章 ID 的映射，並用 Google Search Console 觀測成效。結果顯示 404 錯誤數量由千餘筆降至個位數，平均回應時間從 1.1 秒降至 0.9 秒；配合 W3 Total Cache，效能已與原本放置於 GoDaddy 的環境相當。整個案例證明 RewriteMap 在大量轉址場景兼具效率與可維護性。

## 段落重點
### 前情提要
作者於 2015/10 將部落格從 ASP.NET 的 BlogEngine 1.6 移轉至 WordPress，因兩套系統 URL 格式迥異，外部引用失效。粗估 400 篇文章 × 6 種格式產生 2400 個舊連結，若不妥善處理將造成 SEO 與使用者體驗衝擊。

### 舊網址盤點
先列舉 BlogEngine 預設含日期與多部落格子目錄的兩類 URL，再透過 Google Search Console 下載 .CSV，額外揪出無日期及 GUID 參數等四類，總計六種格式。某些連結甚至含日期錯誤，需設計例外機制。

### Redirect 初步方案
在 NAS 上以 Apache Reverse Proxy 前端接 WordPress，第一版採 Redirect 301，透過程式自動產生 2400 條規則。雖暫時可用，但維護不易、無容錯且每次請求都要線性比對規則，浪費 CPU。

### RewriteRule 與正規表達式改進
第二版改用 RewriteRule 搭配複雜 RegExp，一條規則即可涵蓋四種含 slug 的格式，規則數降為 400 條並能處理日期錯誤等例外。然而多條 RegExp 仍需逐條比對，理論效能仍不理想。

### 效能問題與 Benchmark
作者搜尋相關文獻，引用 Mozilla 1500 條規則測試圖表，發現 Redirect 與 RewriteRule 回應時間明顯偏高，而 RewriteMap 省去逐條比對，效能最佳，呼應大量轉址場景需求。

### RewriteMap 終極方案
實作 RewriteEngine ON，宣告 RewriteMap slugmap 指往外部對照檔，再以單一 RewriteRule 判定 URL 並查表輸出 WordPress 文章 ID；對照檔可轉為 dbm 進一步提升存取速度。此作法將規則維護集中於一個映射檔，新增文章僅需追加一行。

### 首波成效評估
比較三個時間點：搬家當日回應時間激增、10/28 啟用 W3 Total Cache 明顯下降、11/01 引入 RewriteMap 後再度下探，回到 GoDaddy 時期水準。404 檢索錯誤亦同步大量減少。

### 11/09 追蹤結果
重新提交已解決的 404 之後，Search Console 僅回報 6 筆遺留錯誤，判斷屬無效來源鏈結可忽略。回應時間曲線穩定維持在 1 秒上下，顯示新架構表現可靠。

### 11/13 追蹤結果
Google 數據延伸至 11/11，再次確認 404 數量維持低檔，平均回應時間由 1130ms 進一步降至 907ms，估計 RewriteMap 取代 2400 條規則帶來約 15–20% 額外效益，證實方案超出原先預期。