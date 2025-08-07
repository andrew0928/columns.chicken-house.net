# Canon Raw Codec + WPF #2, ThreadPool

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者要自己寫一套批次縮圖工具，而不是繼續使用 Microsoft 的 Resize Pictures Power Toys？
Windows XP 時代的 Resize Pictures Power Toys 在 Windows Vista 之後就無法使用；作者仍想要一鍵完成「右鍵→Resize pictures」的批次縮圖功能，所以決定自己動手寫一個替代工具。

## Q: 將 Canon G9 的 RAW 檔（4000×3000）轉成同尺寸 JPEG 時，內建 Canon RAW Codec 大約需要多少時間？
每張檔案大約需要 60~80 秒。

## Q: 如果把同一張 RAW 檔直接縮成 800×600 的 JPEG，速度是否改善？原因是什麼？
只要約 5 秒。推測 Canon RAW Codec 在 decode 階段就針對「先解小尺寸預覽」做了最佳化，因此大幅縮短處理時間。

## Q: 為何使用 .NET 內建 ThreadPool 仍無法有效利用雙核心 CPU？
Canon RAW Codec 本身無法同時在多執行緒下平行運作；即使 ThreadPool 同時派出多支執行緒，CPU 使用率仍停在約 60%，無法拉滿兩核心。

## Q: 內建 ThreadPool 造成 UI 不順暢的主要原因是什麼？
ThreadPool 的工作執行緒無法指定優先權，長時間佔用 CPU 的影像轉檔工作會壓住 UI Thread，導致進度條雖然在跑，預覽圖卻顯示不出來。

## Q: 作者認為一個「理想的 ThreadPool」需要哪些功能？
1. 固定且可控制的執行緒數量  
2. 可以調整執行緒優先權  
3. 支援多組 ThreadPool（例如 RAW 專用 1 執行緒，高優先；JPEG 專用 4 執行緒，低優先）  
4. 能夠用簡單方式等待所有工作完成  

## Q: 作者最後如何解決效能與 UI 反應問題？
他自行實作了一個 SimpleThreadPool，具備上述功能，讓 Canon RAW 解碼與 JPEG 編碼分別跑在不同優先權、不同數量的執行緒上。

## Q: 使用 SimpleThreadPool 後實際效能提升多少？
在 125 張 JPEG + 22 張 RAW（G9 及 G2）混合轉檔測試中，處理時間由 110 秒降到 90 秒，且 UI 順暢，縮圖完成後即時顯示。