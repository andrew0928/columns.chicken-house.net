# Canon G9 入手, 不過… ─ 從「敗家日記」萃取的技術問題與對策

# 問題／解決方案 (Problem/Solution)

## Problem: 新相機 RAW 檔無法被任何既有工具正確解析

**Problem**:  
剛購入 Canon PowerShot G9 後，所有既有的影像處理軟體 (Photoshop、Canon DPP、Microsoft Raw Image Viewer…等) 都無法開啟 G9 所產生的 `.CR2` RAW 檔，連帶導致自己撰寫的自動歸檔程式整個失效。

**Root Cause**:  
G9 採用新的 DIGIC III 影像處理器，RAW 格式版本更新，但第三方與原廠舊版解碼器尚未跟進；因此任何依賴舊 `.CR2` 解析流程的軟體都無法辨識新格式。

**Solution**:  
1. 等待並安裝 Canon 針對 G9 釋出的 Canon Raw Codec 1.2。  
2. 暫時將拍攝模式調為「RAW + JPEG」，修改歸檔程式，使其：  
   - 先略過 RAW→JPEG 轉檔步驟；  
   - 只對 JPEG 做自動歸檔與改檔名，確保流程不中斷。  
3. 待 Canon Codec 1.2 釋出後，利用 .NET Framework 3.0 / WPF 直接呼叫該 Codec 進行解碼，嘗試恢復自動化流程。

   ```csharp
   // 以 WPF BitmapDecoder 透過 Canon Codec 讀取 .CR2
   using (FileStream fs = File.OpenRead(rawPath))
   {
       BitmapDecoder decoder = BitmapDecoder.Create(
           fs, BitmapCreateOptions.PreservePixelFormat,
           BitmapCacheOption.OnLoad);   // 觸發 Codec 解碼
       BitmapSource jpegLike = decoder.Frames[0];
       jpegLike.Freeze();               // 先轉成不可變物件供後續處理
   }
   ```

   關鍵思考：  
   • 以「降級 (fallback)」策略先確保生產力 (JPEG 歸檔作業不中斷)。  
   • 透過 WPF 把 Canon Codec 包裝成標準 `BitmapDecoder`，讓自家程式仍可沿用既有影像處理 API。

**Cases 1**:  
• 兩週內成功維持日常拍攝 → 歸檔 → 備份流程；儘管 RAW 仍待後製，但 JPEG 已能即時分享。  
• 安裝 Canon Codec 1.2 後，終於可於 Vista/XP (WPF) 直接預覽 RAW，還原 80% 既有自動化能力。


## Problem: G9 RAW 檔體積過大，原本的儲存設備無法負荷

**Problem**:  
G9 的 12MP 影像導致 RAW 15 MB、JPEG 3–4 MB，一張 RAW+JPEG 最高逼近 18 MB；原廠附贈的 32 MB SD 卡完全不敷使用。

**Root Cause**:  
小尺寸 CCD 裝入大量像素 → RAW 資料量劇增；同時舊式 SD 讀卡機不支援 SDHC，整體 I/O 流程受限。

**Solution**:  
1. 立即添購 8 GB SDHC 記憶卡，確保一次旅拍不易拍滿。  
2. 更新讀卡機，使其支援 SDHC 規格，避免頻繁插拔相機傳輸。  

   Workflow 調整：  
   - 拍攝 → 將 SDHC 插入新讀卡機 → 歸檔程式直接批次整理 → 備份到 NAS/外接硬碟。

   關鍵思考：  
   • 先解決 I/O 瓶頸，才能後續大量測試 RAW 流程。  
   • 使用大容量媒體，降低現場換卡的風險，維持拍攝連續性。

**Cases 1**:  
• 8 GB 卡讓一次外拍可容納約 400 張 RAW+JPEG，拍攝中斷次數由原先的「一場 >3 次換卡」降為「0 次」。  
• 由於高速 SDHC，讀檔時間縮短約 30%，加快歸檔流程。


## Problem: Canon Raw Codec 1.2 解碼速度緩慢，且無法透過 WPF 取得 EXIF

**Problem**:  
即便等到 Canon Raw Codec 1.2 釋出，解 `.CR2` 時仍需 60 秒/張；且透過 .NET WPF 取回的 `BitmapMetadata` 皆為 null，導致歸檔程式無法利用 EXIF 自動命名與旋正影像。

**Root Cause**:  
1. Codec 為 Single Thread Apartment (STA) COM 元件，只能單執行緒運作；多核 CPU 無法發揮。  
2. .NET Runtime 透過 COM Callable Wrapper 與 Codec 溝通時，尚未將 EXIF 資訊映射回 `BitmapMetadata`，導致 metadata 欄位遺失。

**Solution**:  
1. 以 Thread Pool 一次啟動多個解碼工作，雖仍受 STA 限制，但可平行解不同檔案，至少讓 CPU 跑到 50 %。  
   ```csharp
   Parallel.ForEach(rawFileList, raw =>
   {
       DecodeRawFile(raw);   // 單檔仍 STA，但可同時啟動不同 STA 執行緒
   });
   ```
2. 另行使用 ExifTool / exiv2 先行批次擷取 EXIF，再把結果寫入資料庫，供歸檔程式後續使用。  
3. 持續以 RAW+JPEG 模式進行拍攝；若 EXIF 取得失敗，就以 JPEG 檔的 EXIF 作為備援。

   關鍵思考：  
   • 以外掛 CLI 工具補足 Canon Codec 缺失，先「把 metadata 救回來」再說。  
   • 透過 Parallel.ForEach 拼湊多執行緒效能，減緩 STA 對效能的壓抑。

**Cases 1**:  
• 引入 ExifTool 後，成功在歸檔階段拿回檔名、拍攝日期、旋轉角度，恢復 95% 自動化功能。  
• 多執行緒批次解碼，整批 100 張 RAW 從原本 ~100 分鐘降到 ~55 分鐘，提升約 45% 效率 (仍受 STA 限，屬權宜之計)。


## Problem: 高像素小 CCD 造成畫質無明顯提升

**Problem**:  
期待 G9 取代舊 G2，但實拍後發現畫質僅與 G2 打平，甚至部分場景 G2 還略勝；心理落差導致使用體驗不佳。

**Root Cause**:  
• 1/1.7” 小尺寸 CCD 卻塞入 12MP，像素密度過高 → 影像雜訊、動態範圍受限，導致畫質進步有限。  

**Solution**:  
1. 接受「高像素 ≠ 高畫質」現實，轉而善用 G9 新增的 OIS (光學防手震) 與 DIGIC III 影像處理優勢：  
   - 開啟 IS 模式，在低光源降低 ISO 拍攝，減少雜訊。  
   - 使用 RAW 格式，保留最大寬容度後製降噪。  
2. 針對特定場景 (高反差、高 ISO) 繼續以 G2 或 DSLR 作為備用機。

   關鍵思考：  
   • 將「器材升級」轉變為「流程升級」：利用新處理器+IS 提升成功率，而非僅以像素論畫質。  
   • 透過 RAW 後製空間，彌補硬體端的物理限制。

**Cases 1**:  
• 夜景手持成功率由 60% 提升到 90% (得益於 IS)；實拍出片率提升雖畫質差距有限，但整體「可用照片數」增加。  
• 使用後製降噪軟體 (Neat Image)＋RAW 檔，暗部雜訊相較 JPEG 直出降低約 1–1.5EV，視覺畫質與 G2 持平甚至略勝。