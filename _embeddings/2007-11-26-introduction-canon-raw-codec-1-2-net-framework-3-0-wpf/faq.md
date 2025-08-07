# 前言: Canon Raw Codec 1.2 + .NET Framework 3.0 (WPF)

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Canon 釋出的 Raw Codec 1.2 對使用 G9 相機拍攝的 .CR2 檔案帶來了什麼直接好處？
在 Windows XP 與 Vista 上，G9 所產生的 .CR2 檔案終於可以直接預覽與顯示，不再需要額外轉檔或外掛程式。

## Q: 為什麼在 WPF 中透過 BitmapSource.Metadata 讀取不到任何 EXIF/Metadata？
目前版本的 Canon Codec 並未在 BitmapSource 層級暴露 Metadata；只能在各個 Frame 物件上取得對應的 Metadata，因此直接對 BitmapSource.Metadata 呼叫只會得到 null。

## Q: 想列舉出一張影像裡所有已存在的 Metadata Query 該怎麼做？
BitmapMetadata 其實實作了 IEnumerable<string> 介面，只要把 BitmapMetadata 丟進 foreach 迴圈即可列舉出所有可用的 Query 字串。

## Q: 若 InPlaceMetadataWriter 無法成功更新 Metadata，有沒有替代方案？
可以先呼叫 metadata.Clone() 取得複本，對複本做修改後再塞回 Encoder，如此即可繞過 InPlaceMetadataWriter 目前遇到的限制。

## Q: 使用 Canon Codec 處理 G9 之 4000×3000、約 15 MB 的 .CR2 影像，全幅解碼再以 JpegEncoder 儲存 100% 品質的 JPEG，大概需要多久？
在 Core2Duo E6300（2 GB RAM、Windows XP MCE 2005 SP2）環境下，整個流程約需 80 秒。

## Q: Canon Codec 在多核心 CPU 上的效能表現如何？
即使在雙核心 CPU 上或手動開兩條執行緒，整體 CPU 使用率仍僅 50%–60%，無法充分吃滿多核心資源；相對地，Microsoft 內建的 Codec 能透過 Thread Pool 發揮完整效能。