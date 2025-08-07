```markdown
# Canon G9 入手, 不過…

## 摘要提示
- 選機考量: 作者在 G 系列與 S 系列之間權衡良久，最終因 RAW 與熱靴功能選擇了 G9。
- 畫質落差: 小尺寸 CCD 擠進 1200 萬畫素導致畫質僅與舊 G2 打平，甚至偶爾略輸。
- 檔案容量: RAW 檔 12–15 MB、JPEG 3–4 MB，逼得作者立即加購 SDHC 卡與新讀卡機。
- RAW 相容性: 多款常見軟體均無法解 G9 的 .CR2，僅隨機附的 ZoomBrowserEx 能用。
- 歸檔程式中斷: 自寫自動歸檔工具仰賴 EXIF，因解不了 RAW 而全面停擺。
- 官方 Codec 發布: Canon Raw Codec 1.2 終於支援 G9／G2，但僅標示 Vista 32 bit。
- 實測表現: XP 也可用，惟解碼單張近 60 秒、僅單執行序，雙核心無法加速。
- EXIF 缺失: 透過 WPF 呼叫時抓不到任何 Metadata，BitmapMetadata 為 null。
- 效率困境: 解碼慢又無 EXIF，RAW 流程仍不可行，只能暫以 RAW+JPEG 兩軌拍攝。
- 後續展望: 期盼 Canon 改進 Codec，再行更新歸檔程式，否則只能繼續撐著用。

## 全文重點
作者苦等多年的 Canon PowerShot G 系列終於在 G9 重新加入 RAW 與 DIGIC III，他因而狠下心購買水貨省下約 3000 元。對比 G2、G6、S 系機種後，G9 是唯一同時具備熱靴、IS 及 RAW 的折衷選擇。然而實際使用兩週後，問題接踵而來：畫質並未顯著超越五年前的 G2；1200 萬畫素造成檔案暴增，使原本隨機附贈的 32 MB 記憶卡形同虛設，只得加購 8 GB SDHC 與新讀卡機。最大難題在於 RAW 相容性：Photoshop、DPP、Picasa、Microsoft 及各式第三方工具通通無法正確讀取 G9 的 .CR2，僅能倚賴功能陽春的 ZoomBrowserEX。此情況直接拖垮作者原本以 EXIF 為核心的自動歸檔系統，工作流程被迫改成 RAW+JPEG 雙檔並行，再手動跳過 RAW→JPEG 的轉換。

好消息是 Canon 近日釋出 Raw Codec 1.2，名義上供 Vista 32 bit 使用，但實測在 XP SP2 亦可搭配 .NET 3.0/WPF 調用。壞消息則是效能與功能不如預期：單張 15 MB 檔案解碼近一分鐘且僅用到單核心，WPF 介面更無法取得任何 Metadata，導致歸檔程式仍然無法自動分類、改名或修正方向。換言之，Canon 雖解決了「能不能開」的門檻，卻未解決「開得快不快、資料完不完整」的實務需求。作者只得繼續以 RAW+JPEG 撐場，等待 Canon 未來改版，方能重新啟動自己的自動化流程。

## 段落重點
### 購買動機與型號取捨
作者自 G6 世代起即尋覓新機，但 G6 沿用舊 DIGIC、效能欠佳；S2/S3 無熱靴；S5 有改進仍不滿意。G7 雖大改版卻砍掉 RAW，直到 G9 重回 RAW、升至 DIGIC III 才符合需求。雖然沒有「G8」，但在考量熱靴、IS、體積與價格後，作者終於入手水貨 G9 省下約 3000 元。

### 使用初體驗與硬體瓶頸
實拍兩週發現畫質與舊 G2 差距有限，小尺寸 CCD 逼進 1200 萬畫素使高 ISO 雜訊增多。RAW 檔 12–15 MB、JPEG 3–4 MB，一旦啟用 RAW+JPEG 每張佔用近 18 MB，32 MB 隨機卡僅能試拍，被迫加購 8 GB SDHC 並汰換讀卡機。雖稍感失望，但鏡頭含 IS、整體操作仍屬可接受。

### RAW 相容性全面失靈
最大障礙是軟體支援貧弱：Photoshop 更新後仍認不得 G9，Canon 自家 Ric/DPP 舊版亦拒讀，Microsoft Raw Viewer、Picasa 顏色錯誤，唯一可用僅 ZoomBrowserEX。由於作者自寫歸檔程式仰賴 EXIF 與自動轉檔，整個工作流程因此停擺，只能先用 RAW+JPEG 並手動處理。

### Canon Raw Codec 1.2 發布與測試
喜訊是 Canon 終於發布 Raw Codec 1.2 支援 G9/G2，且在 XP SP2＋.NET 3.0/WPF 可運作；噩耗則是效能低下：Core2Duo E6300 解一張需近 60 秒、CPU 利用率僅 50%，顯示為 STA 單執行緒；更糟的是透過 WPF 调用時無法取得任何 EXIF Metadata。缺乏關鍵資料與低效率使歸檔程式依舊無法恢復，作者只能繼續 RAW+JPEG，等待 Canon 改進 Codec 或另尋替代方案。
```
