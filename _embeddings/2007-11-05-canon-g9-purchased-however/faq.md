# Canon G9 入手, 不過...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 作者為什麼最後選擇 Canon PowerShot G9，而沒有買 G6、S 系列或 G7？
作者需要熱靴、RAW 格式以及較新的影像處理器。S2/S3 沒有熱靴、S5 雖然有但仍想留在 G 系列；G6 仍用舊版 DIGIC、改進有限；G7 取消 RAW、光圈變小且少了翻轉 LCD，因此最終選擇把 RAW 加回、改用 DIGIC III 的 G9。

## Q: Canon 有推出 G8 嗎？
沒有，Canon 在 G7 之後直接跳到 G9，並未發表 G8。

## Q: 水貨版 G9 比公司貨大約便宜多少？
大約便宜新台幣 3,000 元。

## Q: G9 的畫質表現讓作者最失望的地方是什麼？
1/1.7 吋的小型 CCD 卻塞進 1,200 萬畫素，成像品質多數情況只與舊機 G2 打成平手，甚至偶爾被 G2 超車，未出現預期中的畫質「奇蹟」。

## Q: 以 12 MP 拍攝時，RAW 與 JPEG 檔案各有多大？附贈 32 MB SD 卡夠用嗎？
RAW 約 12–15 MB、JPEG 約 3–4 MB，同錄 RAW+JPEG 可達 18 MB；原廠附的 32 MB SD 卡嚴重不足，只能另購大容量 SDHC 及相容讀卡機。

## Q: 剛入手時，有哪些軟體能正確讀取 G9 的 .CR2 RAW 檔？
作者試過 Photoshop 外掛、Canon Raw Image Converter、DPP 3.0、Raw Codec for Vista、Microsoft Raw Image Viewer 皆失敗，Google Picasa 讀得到但顏色錯誤，唯一可用的是隨機光碟附的 ZoomBrowser EX。

## Q: Canon Raw Codec 1.2 的發布解決了哪些問題？
它終於支援 G9（亦含 G2）RAW 檔，且能與 .NET 3.0 WPF 協同運作，即使官方標註僅支援 Vista 32 bit，實測在 Windows XP SP2 也可使用，總算能「讀得開」檔案。

## Q: 使用 Canon Raw Codec 1.2 解 15 MB 的 .CR2 檔大約需要多久？CPU 利用率如何？
在 Core2Duo E6300 上約需近 1 分鐘，CPU 佔用僅約 50%，疑似為單執行緒，無法充分運用雙核心。

## Q: 透過 WPF 調用 Canon Raw Codec 1.2 能取得 EXIF／Metadata 嗎？
無法，WPF 回傳的 BitmapMetadata 物件為 null，完全讀不到 EXIF 資料。

## Q: 作者目前的臨時做法與後續打算是什麼？
暫時持續以 RAW+JPEG 模式拍攝，歸檔程式只先處理 JPEG，RAW 當備份；待 Canon 進一步改進 Raw Codec 再全面更新流程。

## Q: 除了上述問題，作者對 G9 仍有哪些滿意之處？
電子零件升級及鏡頭加入 IS 效果顯著，整體而言仍覺得這台相機物有所值。