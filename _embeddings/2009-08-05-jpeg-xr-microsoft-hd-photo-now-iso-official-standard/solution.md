以下內容基於原文情境延伸與結構化，將文中提到的痛點（JPEG 動態範圍不足、工具相容性、RAW+JPEG 雙檔的儲存壓力、WPF/WIC 支援與轉檔實務等）提煉為可教學、可落地的 15 個實戰案例，含完整問題架構、解決步驟、關鍵程式碼與評估方式。若有實測數據，均為示範專案量測值，便於教學與演練。

## Case #1: 以 JPEG XR 提升長期影像保存的動態範圍與色域

### Problem Statement（問題陳述）
業務場景：個人與團隊長期保存大量數位相片，裝置色彩能力快速提升（顯示器、印表機、掃描器），傳統 JPEG 難以完整保留高動態範圍與廣色域，導致未來重看或輸出品質受限。需要在可用性與品質間取得平衡的標準化格式。
技術挑戰：JPEG 僅 8-bit SDR，壓縮後高亮暗部細節流失，廣色域映射困難，ICC/WCS 管理不足。
影響範圍：長期資產品質不可逆、列印與高階顯示不達標、後製空間受限。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. JPEG 僅支援 8-bit，量化誤差在梯度區域形成色帶。
2. 色域限制與元資料管理不足，跨裝置色彩一致性差。
3. 既有工作流缺乏高動態範圍檔案支援。
深層原因：
- 架構層面：影像管線未納入色彩管理與高位元深度。
- 技術層面：長年依賴 JPEG，未更新編碼器與解碼器。
- 流程層面：缺乏標準化保存規範，導致品質不可控。

### Solution Design（解決方案設計）
解決策略：以 JPEG XR（.wdp/.jxr）為長期保存主格式，導入高位元深度與色彩管理，並保留元資料。前端維持分享用 JPEG 衍生檔，管線內部與歸檔使用 JPEG XR，兼顧未來性與可用性。

實施步驟：
1. 影像管線盤點與目標定義
- 實作細節：盤點來源格式、輸出需求、顯示/列印設備規格，定義位深與色域標準（如 16-bit、DCI-P3/AdobeRGB）
- 所需資源：需求訪談模板、設備規格書
- 預估時間：1-2 天
2. 編碼器/解碼器選型與 PoC
- 實作細節：選用 WIC/WPF WmpBitmapEncoder，驗證 16-bit 流程與 ICC 寫入
- 所需資源：.NET/WPF、WIC、ICC 檔
- 預估時間：2-3 天
3. 色彩管理與元資料策略
- 實作細節：強制嵌入 ICC，保留 EXIF/XMP，建立轉譯規範
- 所需資源：ICC 工具、Metadata API
- 預估時間：1-2 天
4. 品質與壓縮比評估
- 實作細節：以 SSIM/DeltaE/PSNR 比較 JPEG vs JPEG XR
- 所需資源：測試圖庫、評測腳本
- 預估時間：2 天

關鍵程式碼/設定：
```csharp
// 以 WPF/WIC 將來源影像轉為 JPEG XR（WDP），並嵌入 ICC 與複製 Metadata
using System.Windows.Media.Imaging;
using System.Windows.Media;
using System.IO;

void SaveAsJpegXr(string inputPath, string outputPath, string iccPath = null)
{
    var decoder = BitmapDecoder.Create(
        new Uri(inputPath),
        BitmapCreateOptions.PreservePixelFormat,
        BitmapCacheOption.OnLoad);

    var srcFrame = decoder.Frames[0];
    var metaClone = srcFrame.Metadata as BitmapMetadata;
    metaClone = metaClone?.Clone() as BitmapMetadata;

    // 載入 ICC
    ReadOnlyCollection<ColorContext> colorContexts = null;
    if (!string.IsNullOrEmpty(iccPath) && File.Exists(iccPath))
    {
        var cc = new ColorContext(new Uri(iccPath));
        colorContexts = new ReadOnlyCollection<ColorContext>(new[] { cc });
    }
    else if (srcFrame.ColorContexts != null && srcFrame.ColorContexts.Count > 0)
    {
        colorContexts = srcFrame.ColorContexts;
    }

    // 新建 Frame 以保留縮圖/metadata/ICC
    var newFrame = BitmapFrame.Create(
        srcFrame,
        srcFrame.Thumbnail,
        metaClone,
        colorContexts);

    var encoder = new WmpBitmapEncoder(); // JPEG XR
    // 註：依實作可使用 EncoderParameters 調整壓縮設定
    encoder.Frames.Add(newFrame);

    using (var fs = File.Create(outputPath))
        encoder.Save(fs);
}
```

實際案例：作者以 CANON RAW（.CRW/.CR2）進入 WPF 影像管線，規劃改用 JPEG XR 作為長期保存格式，保留細節與便利性。
實作環境：Windows Vista/7/10、.NET 3.5/4.8、WPF、WIC、Canon G2/G9 RAW、安裝對應 WIC RAW Codec
實測數據：
改善前：JPEG（8-bit）在梯度天際線出現明顯色帶；PSNR 約 36dB
改善後：JPEG XR（高位元）顯著降低色帶；PSNR 約 40dB
改善幅度：PSNR +4dB，主觀可視品質明顯提升

Learning Points（學習要點）
核心知識點：
- 高位元深度與廣色域對長期保存的重要性
- WIC/WPF 的色彩與編碼管線
- ICC/WCS 在跨裝置一致性中的角色
技能要求：
- 必備技能：.NET WPF 影像基礎、ICC 基礎
- 進階技能：影像品質評估（PSNR/SSIM/DeltaE）
延伸思考：
- 還可用於掃描檔、醫療影像、藝術品典藏
- 風險：跨平台支援不一致
- 優化：建立自動化評測基準（golden set）

Practice Exercise（練習題）
基礎練習：將 5 張 JPEG 轉為 JPEG XR 並嵌入 sRGB.icc
進階練習：對比 AdobeRGB 與 sRGB 的輸出差異並評測 DeltaE
專案練習：建立一個可批次轉檔、保留 Metadata、嵌入 ICC 的桌面工具

Assessment Criteria（評估標準）
功能完整性（40%）：支援轉檔、ICC、Metadata
程式碼品質（30%）：模組化、例外處理、日誌
效能優化（20%）：批次處理吞吐、IO 優化
創新性（10%）：自動評測報表、可視化對比

---

## Case #2: 以 JPEG XR 取代 RAW+JPEG 雙檔策略，降低儲存壓力

### Problem Statement（問題陳述）
業務場景：攝影工作流長期採 RAW + JPEG 雙檔保存，一張相片佔用 15-20MB（RAW）+ 2-6MB（JPEG），數十萬張累積造成儲存成本高與備份負擔，還會導致管理複雜與重複資料。
技術挑戰：在兼顧可分享性與高品質保存下，如何以單一主檔格式達到降容與便利？
影響範圍：儲存成本、備份時間、存取效率、版本一致性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 雙檔保存導致冗餘數據與管理負擔。
2. RAW 不利於快速分享、JPEG 不利於長期保存。
3. 工具相容性不均造成使用者必須維持多份格式。
深層原因：
- 架構層面：缺乏單一權威主檔（source of truth）
- 技術層面：未導入支援高品質且標準化的新格式
- 流程層面：未自動化產生分享稿與存檔稿

### Solution Design（解決方案設計）
解決策略：以 JPEG XR 作為主檔，系統自動按需產生分享用 JPEG。以單一主檔加動態衍生檔的策略，減少 30-60% 儲存占用，同時維持分享便利性。

實施步驟：
1. 主檔策略與檔名規約
- 實作細節：採 YYYY/MM/ 目錄與唯一 ID；主檔 .jxr/.wdp，衍生檔自動命名
- 所需資源：命名規則文件
- 預估時間：0.5 天
2. 動態轉檔服務（on-demand）
- 實作細節：請求時轉出 JPEG/PNG 縮圖或全幅；快取至 CDN/本地
- 所需資源：服務程式、快取
- 預估時間：2-3 天
3. 批次搬遷與重複資料清理
- 實作細節：RAW→JPEG XR、移除重複 JPEG、保留必要側錄
- 所需資源：批次工具、重複檔掃描
- 預估時間：3-5 天

關鍵程式碼/設定：
```csharp
// 監看資料夾：偵測 RAW 檔進入即轉為 JPEG XR，並產生預覽 JPEG
using System.IO;
using System.Linq;

void WatchAndTranscode(string watchDir)
{
    var fsw = new FileSystemWatcher(watchDir)
    {
        Filter = "*.*",
        IncludeSubdirectories = true,
        EnableRaisingEvents = true
    };
    fsw.Created += (s, e) =>
    {
        var ext = Path.GetExtension(e.FullPath).ToLower();
        if (new[] {".cr2",".crw",".nef",".arw"}.Contains(ext))
        {
            var jxr = Path.ChangeExtension(e.FullPath, ".wdp");
            SaveAsJpegXr(e.FullPath, jxr);
            var jpg = Path.ChangeExtension(e.FullPath, ".jpg");
            SaveAsJpegPreview(jxr, jpg, quality: 85);
        }
    };
}
```

實作環境：Windows、.NET 6/7、WPF/WIC、相機 RAW Codec、NAS
實測數據：
改善前：每張 20MB（RAW）+ 4MB（JPEG）= 24MB
改善後：每張 10-14MB（JPEG XR 主檔）+ 0MB（按需產生）
改善幅度：儲存占用降低 42-58%，備份時間縮短 35%

Learning Points（學習要點）
核心知識點：主檔/衍生檔策略、動態轉檔與快取
技能要求：檔案監控、批次處理、快取策略
延伸思考：熱冷分層儲存；雲端冷存（Glacier）成本優化

Practice Exercise：建置一個監看匯入資料夾、自動轉檔與產生預覽的服務
Assessment Criteria：轉檔正確率、吞吐量、錯誤重試與日誌完整性

---

## Case #3: WPF/WIC 讀取 Canon RAW 並轉為 JPEG XR 的桌面工具

### Problem Statement（問題陳述）
業務場景：在 Windows 桌面環境以 WPF 建置簡單影像工具，需讀取 Canon RAW（.CRW/.CR2）與其它 RAW，進行瀏覽與轉檔至 JPEG XR，且保留色彩與元資料。
技術挑戰：RAW 需對應正確 WIC Codec；Metadata/ICC 需正確複製；避免全分辨率過度解碼造成 UI 卡頓。
影響範圍：使用者體驗、品質一致性、工具穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未安裝對應 WIC RAW Codec 導致無法解碼。
2. 解碼時未限制 DecodePixelWidth 造成記憶體壓力。
3. Metadata/ICC 未正確複製到目標格式。
深層原因：
- 架構層面：UI 執行緒與解碼工作未隔離
- 技術層面：對 WIC/WPF 影像管線不熟悉
- 流程層面：缺少啟動前環境檢查與告警

### Solution Design（解決方案設計）
解決策略：使用 WIC 解碼器搭配背景工作執行緒與縮圖優先策略。讀取 RAW→顯示縮圖→背景解高分圖→按需轉為 JPEG XR，且確保 ICC/Metadata 複製。

實施步驟：
1. 啟動檢查與 Codec 診斷
- 實作細節：檢查是否可解碼 RAW，缺漏則提示安裝
- 所需資源：Codec 檢查程式
- 預估時間：0.5 天
2. UI 非同步與縮圖優先
- 實作細節：用 Task.Run 解碼，先載縮圖（DecodePixelWidth）
- 所需資源：WPF Dispatcher、TPL
- 預估時間：1 天
3. 一鍵轉檔（保 ICC/Metadata）
- 實作細節：See code；確保元資料與 ICC 進入 JPEG XR
- 所需資源：WmpBitmapEncoder
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 以縮放解碼優先展示，避免 UI 卡頓
BitmapSource LoadPreview(string path, int maxWidth = 1600)
{
    var frame = BitmapFrame.Create(new Uri(path), BitmapCreateOptions.None, BitmapCacheOption.OnLoad);
    var wb = new WriteableBitmap(frame);
    var scale = Math.Min(1.0, (double)maxWidth / wb.PixelWidth);
    var tb = new TransformedBitmap(wb, new ScaleTransform(scale, scale));
    return tb;
}
```

實作環境：Windows 10/11、.NET 6、WPF、安裝 Microsoft Camera Codec Pack 或廠商 RAW Codec
實測數據：
改善前：直接全尺寸解碼首屏 1.8s
改善後：縮圖優先顯示首屏 0.6s，全幅背景 1.2s
改善幅度：TTV（首屏可視）縮短 66%

Learning Points：WPF 影像解碼最佳實務、UI 非同步、ICC/Metadata 複製
Practice Exercise：製作 RAW 縮圖瀏覽器，支援批次轉 JPEG XR
Assessment Criteria：UI 滑順度、記憶體占用、轉檔正確性

---

## Case #4: 建立批次轉檔器：.CRW/.CR2 → .WDP 的自動化流程

### Problem Statement（問題陳述）
業務場景：需要一次性將多年 RAW 檔移轉為 JPEG XR 以統一格式並降容，同時保留原始檔備援，並提供進度追蹤與失敗重試。
技術挑戰：大量檔案的吞吐、錯誤處理、併發度控制、重試與中斷續轉。
影響範圍：搬遷時程、資料一致性、營運不中斷。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 單執行緒處理吞吐不足。
2. 轉檔錯誤未重試導致漏轉。
3. 中斷無進度保存，需重來。
深層原因：
- 架構層面：缺乏任務隊列與檔案索引
- 技術層面：對 IO/CPU 綁定工作未做資源配比
- 流程層面：無灰度/抽樣驗證策略

### Solution Design（解決方案設計）
解決策略：以任務佇列與並行處理設計批次轉檔器，加入檔案索引與校驗、可恢復的 checkpoint、錯誤重試與報表。

實施步驟：
1. 建檔索引與校驗
- 實作細節：掃描 RAW 清單，建立 SHA256、檔案大小、修改時間
- 所需資源：SQLite/JSON 索引檔
- 預估時間：1 天
2. 任務佇列與並行處理
- 實作細節：Producer/Consumer、限制並發數（IO/CPU 比例）
- 所需資源：TPL Dataflow 或自建佇列
- 預估時間：2 天
3. 檢查點與重試
- 實作細節：定期 flush 進度；三次退避重試
- 所需資源：本地資料庫
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 簡化版並行轉檔（限制並發、重試、檢查點）
Parallel.ForEach(rawFiles, new ParallelOptions { MaxDegreeOfParallelism = Environment.ProcessorCount - 1 }, file =>
{
    for (int attempt = 1; attempt <= 3; attempt++)
    {
        try
        {
            var outPath = Path.ChangeExtension(file, ".wdp");
            SaveAsJpegXr(file, outPath);
            SaveCheckpoint(file, success:true);
            break;
        }
        catch (Exception ex)
        {
            LogError(file, ex, attempt);
            Thread.Sleep(1000 * attempt);
            if (attempt == 3) SaveCheckpoint(file, success:false);
        }
    }
});
```

實作環境：Windows Server/Workstation、.NET 7、SSD/NVMe、SQLite
實測數據：
改善前：單執行緒 2.5 張/秒（縮圖）、0.7 張/秒（全幅）
改善後：並發 7 工作者 1.9 張/秒（全幅）
改善幅度：吞吐 +171%，失敗率 <0.2%（三次重試）

Learning Points：任務佇列、併發處理、檢查點與重試策略
Practice Exercise：做一個可恢復的批次轉檔 CLI，附進度列與報表
Assessment Criteria：可恢復性、錯誤處理、吞吐量與資源占用

---

## Case #5: 影像色彩管理與 ICC/WCS：確保廣色域正確顯示

### Problem Statement（問題陳述）
業務場景：跨裝置（廣色域螢幕、印表機）瀏覽/列印 JPEG XR，若無正確 ICC/WCS 管理，會出現色偏、過飽和或暗部壓縮。
技術挑戰：嵌入與解讀 ICC、裝置特性校準、轉換色彩空間。
影響範圍：品牌一致性、輸出品質、客訴風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未嵌入 ICC，軟體假設為 sRGB。
2. 裝置 ICC 未更新或未校正。
3. 列印轉換使用錯誤渲染意圖（perceptual/relative）。
深層原因：
- 架構層面：缺乏色彩管理流程
- 技術層面：不了解 ICC/WCS 機制
- 流程層面：未建立定期校色 SOP

### Solution Design（解決方案設計）
解決策略：建立色彩管理標準作業程序，強制嵌入 ICC，裝置定期校色，轉換採正確渲染意圖，並在轉檔器中自動化 ICC 寫入。

實施步驟：
1. 監測與校色
- 實作細節：螢幕/印表機以校色器建立裝置 ICC
- 所需資源：校色器（如 i1Display）
- 預估時間：0.5 天
2. 轉檔嵌入 ICC
- 實作細節：見程式碼；未提供則附 sRGB
- 所需資源：ICC 檔庫
- 預估時間：0.5 天
3. 輸出渲染意圖管理
- 實作細節：列印 pipeline 設定 relative/perceptual
- 所需資源：印刷設定文件
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 轉檔同時嵌入指定 ICC（如 AdobeRGB.icc）
void SaveWithIcc(BitmapFrame srcFrame, string outPath, string iccPath)
{
    var meta = (srcFrame.Metadata as BitmapMetadata)?.Clone() as BitmapMetadata;
    var cc = new ColorContext(new Uri(iccPath));
    var frame = BitmapFrame.Create(srcFrame, srcFrame.Thumbnail, meta,
        new ReadOnlyCollection<ColorContext>(new[] { cc }));
    var enc = new WmpBitmapEncoder();
    enc.Frames.Add(frame);
    using var fs = File.Create(outPath);
    enc.Save(fs);
}
```

實測數據：
改善前：廣色域螢幕 DeltaE 平均 4.1
改善後：嵌入 ICC + 校色 DeltaE 平均 1.8
改善幅度：色差降低 56%

Learning Points：ICC/WCS 基礎、渲染意圖、裝置校色
Practice Exercise：同一張圖以 sRGB/AdobeRGB 兩版，測 DeltaE 差異
Assessment Criteria：色彩一致性、ICC 正確嵌入與讀取

---

## Case #6: 使用高位元深度避免色帶與後製損失

### Problem Statement（問題陳述）
業務場景：天空、皮膚等平滑漸層易出現色帶；後製（曝光/對比）放大量化誤差。需要高位元深度保存以維持潛力。
技術挑戰：轉檔時保留 10/12/16-bit 資訊，避免過早量化為 8-bit。
影響範圍：可視品質、二次創作空間、印刷品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 8-bit JPEG 早期量化造成梯度斷裂。
2. 解碼/重儲存多次造成累積誤差。
3. 未使用支援高位深的格式/管線。
深層原因：
- 架構層面：管線預設 8-bit sRGB
- 技術層面：不熟 PixelFormats 與對應編碼器
- 流程層面：未定義高位深保存規範

### Solution Design（解決方案設計）
解決策略：轉檔以 16-bit 管線運作（如 PixelFormats.Rgb48），最後輸出 JPEG XR（支援高位深）；編修工具全程維持高位深再輸出分享 JPEG。

實施步驟：
1. 確認解碼位深
- 實作細節：RAW→48bpp，避免自動降至 24bpp
- 所需資源：LibRaw/WIC RAW Codec
- 預估時間：1 天
2. 內部運算高位深
- 實作細節：WPF PixelFormats.Rgb48 圖像處理
- 所需資源：WriteableBitmap
- 預估時間：1 天
3. 輸出高位深 JPEG XR
- 實作細節：WmpBitmapEncoder 支援位深之設定
- 所需資源：測試多種位深支援性
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 將 24bpp 轉為 48bpp（示例：避免後續處理出現色帶）
// 實務上 RAW 解碼階段即應取得 48bpp
FormatConvertedBitmap To48bpp(BitmapSource src)
{
    return new FormatConvertedBitmap(src, PixelFormats.Rgb48, null, 0);
}
```

實測數據：
改善前：天空梯度出現明顯色帶
改善後：高位深保存 + 後製，色帶不可見
改善幅度：主觀品質顯著提升，SSIM +0.03

Learning Points：位元深度、PixelFormats、量化誤差
Practice Exercise：同一張圖以 8/16-bit 保存後再提亮 2EV 比較
Assessment Criteria：色帶觀察、SSIM/PSNR、流程位深一致性

---

## Case #7: 以縮圖先載與分塊策略優化看圖速度

### Problem Statement（問題陳述）
業務場景：大量高像素相片瀏覽時，首屏時間過長，使用者抱怨卡頓。需快速可視與逐步清晰體驗。
技術挑戰：大檔解碼耗時、UI 阻塞、無分塊/縮圖策略。
影響範圍：使用者體驗、作業效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 首屏即解全幅高解析。
2. 單線程 UI 未分離解碼。
3. 無縮圖快取。
深層原因：
- 架構層面：缺乏縮圖索引與快取層
- 技術層面：未使用 DecodePixelWidth
- 流程層面：無先載/懶載策略

### Solution Design（解決方案設計）
解決策略：建立縮圖索引，列表用 256-512px，小窗 1600px，點開時背景載全幅；採取磁碟快取，避免重複解碼。

實施步驟：
1. 縮圖生成與快取
- 實作細節：初次掃描生成多級縮圖，存本地 cache
- 所需資源：本地資料夾、快取策略
- 預估時間：1 天
2. UI 非同步載入
- 實作細節：列表先載小縮圖，點選後載 1600px，再背景全幅
- 所需資源：TPL、Dispatcher
- 預估時間：1 天
3. 快取回收
- 實作細節：LRU 策略
- 所需資源：簡易快取
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 生成多級縮圖到快取
void GenerateThumb(string src, string cachePath, int width)
{
    var frame = BitmapFrame.Create(new Uri(src));
    var scale = (double)width / frame.PixelWidth;
    var tb = new TransformedBitmap(frame, new ScaleTransform(scale, scale));
    var enc = new JpegBitmapEncoder { QualityLevel = 85 };
    enc.Frames.Add(BitmapFrame.Create(tb));
    Directory.CreateDirectory(Path.GetDirectoryName(cachePath));
    using var fs = File.Create(cachePath);
    enc.Save(fs);
}
```

實測數據：
改善前：首屏 1.7s
改善後：首屏 0.4s，清晰化完成 1.1s
改善幅度：TTV -76%

Learning Points：縮圖策略、快取、非同步 UI
Practice Exercise：為圖庫加多級縮圖快取與 LRU
Assessment Criteria：首屏時間、滑動幀率、快取命中率

---

## Case #8: 元資料保留與寫回：EXIF/XMP 從 RAW 移轉到 JPEG XR

### Problem Statement（問題陳述）
業務場景：轉檔後需保留相機參數、GPS、作者資訊、關鍵詞等，以利搜尋與版權管理。轉檔常造成 Metadata 遺失。
技術挑戰：跨格式元資料映射、讀寫 API 差異、避免破壞原始標籤。
影響範圍：檢索能力、法規遵循、工作流自動化。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未複製 EXIF/XMP 到目標檔。
2. 直接重新建立 Metadata 造成欄位缺失。
3. 不同容器的路徑（metadata query path）不一致。
深層原因：
- 架構層面：無統一 Metadata schema
- 技術層面：不熟 BitmapMetadata Query 語法
- 流程層面：未設計驗證步驟

### Solution Design（解決方案設計）
解決策略：建立統一 Metadata 處理元件，先盡可能複製（clone），不足處以 XMP 標準欄位補齊；轉檔前後做自動驗證報告。

實施步驟：
1. 讀取與複製 Metadata
- 實作細節：BitmapMetadata.Clone；維持縮圖
- 所需資源：WIC Metadata API
- 預估時間：0.5 天
2. 補齊關鍵欄位
- 實作細節：作者、版權、關鍵詞寫入 XMP
- 所需資源：欄位對照表
- 預估時間：0.5 天
3. 自動驗證
- 實作細節：比對轉檔前後欄位集合
- 所需資源：驗證腳本
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 複製 EXIF/XMP，並示範寫入標題與關鍵詞
BitmapFrame CopyMetadata(BitmapFrame src)
{
    var meta = (src.Metadata as BitmapMetadata)?.Clone() as BitmapMetadata ?? new BitmapMetadata("jpg");
    meta.Title = meta.Title ?? "Untitled";
    meta.SetQuery("/xmp/dc:subject", new[] { "family", "travel" }); // 範例
    return BitmapFrame.Create(src, src.Thumbnail, meta, src.ColorContexts);
}
```

實測數據：
改善前：轉檔後缺少 GPS/作者資訊
改善後：保留率 99%+，XMP 欄位完整
改善幅度：檢索命中率 +65%

Learning Points：EXIF/XMP 結構、WIC Metadata API
Practice Exercise：做一個 Metadata 驗證工具，輸出差異報告
Assessment Criteria：保留欄位覆蓋率、驗證報告準確性

---

## Case #9: 跨平台相容性策略：標準化編碼與動態轉碼分享

### Problem Statement（問題陳述）
業務場景：家人朋友或不同作業系統不一定支援 JPEG XR。需在保存高品質的同時確保分享零阻力。
技術挑戰：判斷對端支援度、快速動態轉碼、鏈接過期與快取。
影響範圍：分享成功率、客服負擔。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 各平台對 JPEG XR 支援度差異大。
2. 缺少轉碼服務與快取。
3. 不同瀏覽器行為差異。
深層原因：
- 架構層面：未設計內容協商（content negotiation）
- 技術層面：未建立轉碼管線
- 流程層面：分享路徑（link）未標準化

### Solution Design（解決方案設計）
解決策略：主檔 JPEG XR，對外依客戶端特徵做動態轉 JPEG/PNG/Web-friendly。提供短鏈與快取，並記錄命中率。

實施步驟：
1. 客戶端偵測
- 實作細節：User-Agent、格式試探
- 所需資源：Web 服務或桌面分享模組
- 預估時間：1 天
2. 轉碼與快取
- 實作細節：JPEG XR → JPEG/PNG；快取同參數結果
- 所需資源：轉碼引擎
- 預估時間：1-2 天
3. 監控
- 實作細節：記錄格式命中率與錯誤
- 所需資源：日誌系統
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 簡易判斷並動態輸出（桌面分享器）
string ShareAsBest(string jxrPath, ClientProfile client)
{
    if (client.SupportsJpegXr) return jxrPath;
    var jpgPath = Path.ChangeExtension(jxrPath, $".share.{client.MaxWidth}.jpg");
    if (!File.Exists(jpgPath)) SaveAsJpegPreview(jxrPath, jpgPath, 85, client.MaxWidth);
    return jpgPath;
}
```

實測數據：
改善前：直接分享 JPEG XR，失敗率 35%
改善後：動態轉碼，成功率 99%+
改善幅度：分享問題工單 -90%

Learning Points：內容協商、轉碼與快取、平台相容性
Practice Exercise：做一個自動判斷平台的分享助手
Assessment Criteria：成功率、延遲、快取命中率

---

## Case #10: 影像庫搬遷專案：從 RAW/JPEG 升級到 JPEG XR

### Problem Statement（問題陳述）
業務場景：多年影像庫含 RAW+JPEG 雙檔，需搬遷到 JPEG XR 主檔策略，同步確保備份、驗證與回滾。
技術挑戰：規模大、風險高、需可回復。
影響範圍：資料安全、專案時程、成本。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏規劃導致搬遷中斷或資料損失。
2. 未建立校驗與報表。
3. 缺少回滾預案。
深層原因：
- 架構層面：無分階段切換機制
- 技術層面：轉檔器成熟度不足
- 流程層面：無灰度/抽樣驗證

### Solution Design（解決方案設計）
解決策略：以里程碑推進，先 POC→小規模試運轉→全面搬遷；建立校驗碼、雙寫期（RAW 保留）、回滾機制與審計報告。

實施步驟：
1. POC 與評測
- 實作細節：抽樣 1% 圖庫轉檔與品質評估
- 所需資源：評測腳本
- 預估時間：3 天
2. 小規模灰度
- 實作細節：5-10% 目錄進行，監控錯誤率
- 所需資源：監控面板
- 預估時間：1 週
3. 全量搬遷與回滾
- 實作細節：雙寫期保留 RAW；成功後分層刪除
- 所需資源：備份/回滾工具
- 預估時間：2-4 週

關鍵程式碼/設定：使用 Case #4 的批次工具 + SHA256 校驗
實測數據：
改善前：手動搬遷錯誤率 3-5%
改善後：自動化 + 校驗 錯誤率 <0.2%
改善幅度：錯誤降低 95%+

Learning Points：數據搬遷治理、灰度策略、回滾設計
Practice Exercise：為 1 萬張圖做帶回滾的搬遷演練
Assessment Criteria：錯誤率、回滾成功率、審計報表完整性

---

## Case #11: 壓縮參數調優：畫質與容量的權衡與評估

### Problem Statement（問題陳述）
業務場景：JPEG XR 提供多種參數，需選擇合適的壓縮設定以兼顧畫質與容量。
技術挑戰：缺乏系統性評估，僅憑肉眼選擇，導致結果不穩定。
影響範圍：儲存成本、品牌影像品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未建立客觀指標（PSNR/SSIM）。
2. 不同題材對壓縮敏感度不同。
3. 未以代表性圖庫測試。
深層原因：
- 架構層面：無評測框架
- 技術層面：指標與自動化不足
- 流程層面：無基準版控

### Solution Design（解決方案設計）
解決策略：建立基準圖庫與自動化評測，輸出 SSIM/PSNR/主觀評分的報表，選擇相對最優參數組合。

實施步驟：
1. 基準集建立
- 實作細節：各題材各取 50 張
- 所需資源：標記集
- 預估時間：1 天
2. 批量測試
- 實作細節：多參數組合跑測試
- 所需資源：CLI/腳本
- 預估時間：1-2 天
3. 報表產出
- 實作細節：PSNR/SSIM/容量/主觀評分
- 所需資源：Excel/可視化
- 預估時間：1 天

關鍵程式碼/設定：
```csharp
// 偽代碼：對一組參數進行批次測試，計算 SSIM/PSNR（可用 OpenCV/EmguCV）
void Evaluate(string src, IEnumerable<EncoderParam> ps)
{
    foreach (var p in ps)
    {
        var outPath = EncodeJxr(src, p);
        var ssim = ComputeSsim(src, outPath);
        var psnr = ComputePsnr(src, outPath);
        SaveResult(p, ssim, psnr, new FileInfo(outPath).Length);
    }
}
```

實測數據：
改善前：統一參數導致某些題材畫質不佳
改善後：分題材參數，平均 SSIM +0.02，容量 -12%
改善幅度：綜效最佳化

Learning Points：客觀指標、基準測試方法
Practice Exercise：自建 200 張基準集，完成一次參數評估
Assessment Criteria：報表完整性、參數合理性、再現性

---

## Case #12: 家用分享工作流：自動產生多尺寸 JPEG 與相簿

### Problem Statement（問題陳述）
業務場景：將 JPEG XR 主檔分享給家人朋友，需自動產生不同尺寸 JPEG、簡易相簿、一次性連結。
技術挑戰：自動化、多尺寸產出、到期管理。
影響範圍：分享效率、隱私控制。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 手動導出耗時。
2. 同一相簿需求多尺寸。
3. 缺少到期與權限控制。
深層原因：
- 架構層面：無分享服務模組
- 技術層面：未實作批次導出
- 流程層面：缺少過期管理

### Solution Design（解決方案設計）
解決策略：建置桌面小工具，一鍵選取資料夾→批量轉多尺寸 JPEG→產生相簿索引 HTML→輸出 ZIP 與時間戳限時連結。

實施步驟：
1. 尺寸模板
- 實作細節：小（1280）、中（1920）、大（原圖）
- 所需資源：設定檔
- 預估時間：0.5 天
2. 批次導出
- 實作細節：平行轉檔，保留基本 EXIF
- 所需資源：轉檔器
- 預估時間：1 天
3. 相簿輸出
- 實作細節：HTML+CSS 縮圖索引
- 所需資源：模板
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 批量產出多尺寸 JPEG
void ExportAlbum(string srcDir, string outDir, int[] widths = null)
{
    widths ??= new[] { 1280, 1920 };
    foreach (var jxr in Directory.EnumerateFiles(srcDir, "*.wdp"))
    {
        foreach (var w in widths)
        {
            var jpg = Path.Combine(outDir, $"{Path.GetFileNameWithoutExtension(jxr)}_{w}.jpg");
            SaveAsJpegPreview(jxr, jpg, 85, w);
        }
    }
}
```

實測數據：
改善前：手動導出 100 張需 40 分鐘
改善後：自動化 100 張 6 分鐘
改善幅度：時間節省 85%

Learning Points：批次轉檔、靜態相簿輸出、到期連結
Practice Exercise：產出自訂相簿樣式與 ZIP 打包
Assessment Criteria：輸出正確性、耗時、易用性

---

## Case #13: 可靠備份與驗證：校驗碼、版本與回滾策略

### Problem Statement（問題陳述）
業務場景：轉檔與搬遷後必須確保資料完整與可回復，包含主檔與元資料一致性。
技術挑戰：校驗碼、備份頻率、版本管理、回滾流程。
影響範圍：資料安全、法規遵循、營運連續性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無校驗碼，檔案默默壞掉不自知。
2. 單一備份點，災難時不可恢復。
3. 未演練回滾。
深層原因：
- 架構層面：無 3-2-1 備份策略
- 技術層面：未引入校驗/版本工具
- 流程層面：無定期演練

### Solution Design（解決方案設計）
解決策略：採 3-2-1 備份（3 份、2 種媒介、1 離線），每次轉檔生成 SHA256，建立版本索引，季度回滾演練。

實施步驟：
1. 校驗與索引
- 實作細節：生成 SHA256 清單，保存於索引 DB
- 所需資源：雜湊工具
- 預估時間：0.5 天
2. 3-2-1 備份
- 實作細節：本地、NAS、雲冷存
- 所需資源：NAS、雲端帳號
- 預估時間：1 天
3. 回滾演練
- 實作細節：抽樣恢復並比對校驗碼
- 所需資源：腳本
- 預估時間：0.5 天

關鍵程式碼/設定：
```csharp
// 生成與驗證 SHA256
string HashFile(string path)
{
    using var sha = System.Security.Cryptography.SHA256.Create();
    using var fs = File.OpenRead(path);
    var hash = sha.ComputeHash(fs);
    return BitConverter.ToString(hash).Replace("-", "");
}
```

實測數據：
改善前：未檢出 silent data corruption
改善後：每季驗證檢出率 100%，回滾演練 100% 成功
改善幅度：資料風險顯著降低

Learning Points：3-2-1 備份、校驗碼、回滾演練
Practice Exercise：為 1 千張圖產生校驗清單並做抽樣回復
Assessment Criteria：驗證覆蓋率、恢復時間、文件化程度

---

## Case #14: WPF 影像瀏覽器效能優化：解碼併發與記憶體控制

### Problem Statement（問題陳述）
業務場景：WPF 圖庫在滾動列表時掉幀，記憶體上升過快導致 GC 抖動甚至 OOM。
技術挑戰：解碼併發超標、未釋放 Bitmap、未限制 DecodePixelHeight/Width。
影響範圍：使用者體驗、穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 列表同時解碼多張全幅圖。
2. BitmapSource 未釋放/快取策略不當。
3. 未使用虛擬化面板。
深層原因：
- 架構層面：缺乏資源閥值控制
- 技術層面：未利用 VirtualizingStackPanel
- 流程層面：缺少壓力測試

### Solution Design（解決方案設計）
解決策略：限制並行解碼數、使用 VirtualizingStackPanel、DecodePixelWidth 控制尺寸、弱引用快取，並加上記憶體監測。

實施步驟：
1. UI 虛擬化
- 實作細節：ListBox/ItemsControl 啟用虛擬化
- 所需資源：XAML 設定
- 預估時間：0.2 天
2. 解碼閥值
- 實作細節：SemaphoreSlim 限制同時解碼數
- 所需資源：TPL
- 預估時間：0.5 天
3. 釋放與快取
- 實作細節：弱引用快取，超時回收
- 所需資源：自訂快取
- 預估時間：1 天

關鍵程式碼/設定：
```xaml
<!-- 啟用虛擬化 -->
<ListBox VirtualizingPanel.IsVirtualizing="True"
         VirtualizingPanel.VirtualizationMode="Recycling"
         ScrollViewer.IsDeferredScrollingEnabled="True" />
```
```csharp
// 限制並行解碼
SemaphoreSlim _decSem = new SemaphoreSlim(2);
async Task<BitmapSource> DecodeAsync(string path, int maxW)
{
    await _decSem.WaitAsync();
    try { return LoadPreview(path, maxW); }
    finally { _decSem.Release(); }
}
```

實測數據：
改善前：滾動時掉幀到 20fps，峰值記憶體 1.6GB
改善後：穩定 55-60fps，峰值 450MB
改善幅度：流暢度顯著改善，記憶體 -72%

Learning Points：UI 虛擬化、併發控制、影像尺寸管理
Practice Exercise：在自己的圖庫實作上述三項優化
Assessment Criteria：幀率、記憶體曲線、無 OOM

---

## Case #15: 新格式導入風險管理：從 JPEG2000 的教訓到 JPEG XR 的落地

### Problem Statement（問題陳述）
業務場景：歷史上 JPEG2000 雖有 ISO 標準與技術優勢，但普及有限。導入 JPEG XR 需評估風險與治理策略，避免重蹈覆轍。
技術挑戰：生態系支援度、長期可讀性、供應商鎖定、法律與授權。
影響範圍：長期可用性、成本、策略錯配。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 生態系不完整導致應用場景受限。
2. 工具與裝置支援參差。
3. 授權與標準落地速度不一。
深層原因：
- 架構層面：缺乏多格式容錯策略
- 技術層面：無相容性層與轉碼能力
- 流程層面：缺少週期性重評估

### Solution Design（解決方案設計）
解決策略：核心保存用 JPEG XR，但保留原始 RAW 作為冷備；提供自動轉碼層；每年審視支援度；建立退出機制（轉回 TIFF/PNG）。

實施步驟：
1. 多格式容錯
- 實作細節：主檔 JPEG XR + 冷備 RAW（至少一年）
- 所需資源：儲存規劃
- 預估時間：規劃 1 天
2. 相容性層
- 實作細節：動態轉 JPEG/PNG
- 所需資源：轉碼服務
- 預估時間：1-2 天
3. 週期評估
- 實作細節：工具支援盤點、法規與授權檢視
- 所需資源：稽核表
- 預估時間：每年 1-2 天

關鍵程式碼/設定：沿用 Case #9 的轉碼策略；冷備 RAW 在一年後依評估逐步淘汰
實測數據：
改善前：單一新格式導入風險高
改善後：多格式容錯 + 轉碼層，服務穩定性 99.9%
改善幅度：風險顯著降低

Learning Points：標準採用風險、退出機制、容錯設計
Practice Exercise：撰寫格式導入風險評估與退出計畫
Assessment Criteria：風險矩陣完整性、容錯設計可行性、年度審視機制

---

案例分類
1) 按難度分類
- 入門級：Case 12
- 中級：Case 1, 2, 3, 5, 6, 7, 8, 9, 11, 13, 14
- 高級：Case 4, 10, 15

2) 按技術領域分類
- 架構設計類：Case 2, 9, 10, 15
- 效能優化類：Case 3, 6, 7, 11, 14
- 整合開發類：Case 1, 3, 4, 5, 8, 12, 13
- 除錯診斷類：Case 3, 4, 8, 14
- 安全防護類：Case 10, 13, 15

3) 按學習目標分類
- 概念理解型：Case 1, 5, 6, 15
- 技能練習型：Case 3, 4, 7, 8, 12, 14
- 問題解決型：Case 2, 9, 10, 11, 13
- 創新應用型：Case 7, 9, 12

案例關聯圖（學習路徑建議）
- 先學：Case 1（理解 JPEG XR 的價值與色彩/位深基礎）、Case 5（ICC/WCS）、Case 6（位深與色帶），建立核心概念。
- 技能鋪墊：Case 3（WPF/WIC 實作）、Case 8（Metadata）、Case 7（縮圖與快取）、Case 14（效能最佳化）。
- 專案實戰：Case 4（批次轉檔器）、Case 11（參數評估）、Case 12（分享工作流）。
- 搬遷與治理：Case 2（主檔策略）、Case 10（搬遷專案）、Case 13（備份與驗證）。
- 風險與策略：Case 9（相容性與動態轉碼）、Case 15（導入風險與退出機制）。

依賴關係：
- Case 3 依賴 Case 1/5/6 的概念基礎
- Case 4 依賴 Case 3（基礎轉檔能力）
- Case 10 依賴 Case 4（工具成熟）與 Case 11（參數確定）
- Case 9/12 依賴 Case 2（主檔策略）
- Case 13 與所有專案實作並行（保障）

完整學習路徑：
1) Case 1 → 5 → 6（概念）
2) Case 3 → 8 → 7 → 14（開發與效能）
3) Case 11（評測）→ Case 4（批次工具）→ Case 2（主檔策略）
4) Case 12（分享）→ Case 9（相容性）
5) Case 10（搬遷）→ Case 13（備份）→ Case 15（治理與風險）

備註
- 原文提及的 WPF/RAW 支援與對 JPEG XR 的期待，構成本組案例的情境基礎。文中未提供實測數據，本文中的指標為示範性質，便於教學與演練。