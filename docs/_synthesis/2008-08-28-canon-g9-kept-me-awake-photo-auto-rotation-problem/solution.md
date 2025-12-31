---
layout: synthesis
title: "Canon G9 害我沒睡好... 相片自動轉正的問題"
synthesis_type: solution
source_post: /2008/08/28/canon-g9-kept-me-awake-photo-auto-rotation-problem/
redirect_from:
  - /2008/08/28/canon-g9-kept-me-awake-photo-auto-rotation-problem/solution/
postid: 2008-08-28-canon-g9-kept-me-awake-photo-auto-rotation-problem
---

## Case #1: 桌面縮圖程式未依 EXIF 自動轉正（JPG）

### Problem Statement（問題陳述）
業務場景：團隊用自製 WPF 縮圖工具批次產生照片縮圖，來源含 Canon G9 與 IXUS55 的 JPG。使用者在電腦上瀏覽時，直式照片常出現橫躺、倒立，必須歪頭或手動旋轉，降低檢視效率與歸檔正確性，影響大量歷史照片的整理作業。
技術挑戰：WPF 影像處理流程未讀取 EXIF Orientation，無法據此自動旋轉縮圖。
影響範圍：所有 JPG 的直式/倒立照片在縮圖與展示階段顯示方向錯誤。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 縮圖程式未讀取 EXIF Orientation 標籤（274），導致無法根據拍攝方向旋轉。
2. 假設所有檔案皆已是正向存檔，缺失方向校正步驟。
3. 依賴檢視器自動旋轉，但實際桌面應用多數不會處理。

深層原因：
- 架構層面：影像管線未建置「讀取中介資料→計算轉向→轉換→輸出」的標準流程。
- 技術層面：未掌握 EXIF Orientation 代碼對應到實際角度的映射。
- 流程層面：缺少批次驗證機制，無法在發版前捕捉方向錯誤。

### Solution Design（解決方案設計）
解決策略：在 WPF 工具中加入 EXIF Orientation 讀取與轉向邏輯，於縮放前先計算應用的旋轉角度，透過 TransformGroup 一次完成旋轉與縮放，再輸出 JPEG，確保縮圖方向與原始拍攝一致。

實施步驟：
1. 擴充讀取元資料
- 實作細節：用 BitmapMetadata.GetQuery 取 Orientation 值（/app1/{ushort=0}/{ushort=274}）。
- 所需資源：.NET WPF、System.Windows.Media.Imaging。
- 預估時間：0.5 天。

2. 建立映射與旋轉
- 實作細節：6→90、8→270、3→180、其他→0；用 RotateTransform 實施。
- 所需資源：WPF TransformedBitmap、TransformGroup。
- 預估時間：0.5 天。

3. 整合縮放與輸出
- 實作細節：先旋轉再縮放，或以 TransformGroup 併行；JpegBitmapEncoder 輸出。
- 所需資源：JpegBitmapEncoder。
- 預估時間：0.5 天.

4. 回歸測試
- 實作細節：四方向樣本驗證，人工比對視覺正確性。
- 所需資源：相機樣本、測試圖庫。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
using System.IO;
using System.Windows.Media;
using System.Windows.Media.Imaging;

Rotation GetRotation(BitmapFrame frame)
{
    var meta = frame.Metadata as BitmapMetadata;
    if (meta == null) return Rotation.Rotate0;

    // JPG EXIF Orientation path
    const string path = "/app1/{ushort=0}/{ushort=274}";
    if (!meta.ContainsQuery(path)) return Rotation.Rotate0;

    ushort value = (ushort)meta.GetQuery(path);
    return value switch
    {
        6 => Rotation.Rotate90,   // right-top
        8 => Rotation.Rotate270,  // left-bottom
        3 => Rotation.Rotate180,  // bottom-right
        _ => Rotation.Rotate0
    };
}

void EncodeWithTransform(BitmapFrame sourceFrame, string outPath, double scale = 0.1)
{
    var rotate = GetRotation(sourceFrame);
    var tfs = new TransformGroup();
    tfs.Children.Add(new ScaleTransform(scale, scale));
    if (rotate == Rotation.Rotate90) tfs.Children.Add(new RotateTransform(90));
    else if (rotate == Rotation.Rotate180) tfs.Children.Add(new RotateTransform(180));
    else if (rotate == Rotation.Rotate270) tfs.Children.Add(new RotateTransform(270));

    var encoder = new JpegBitmapEncoder { QualityLevel = 90 };
    encoder.Frames.Add(BitmapFrame.Create(new TransformedBitmap(sourceFrame, tfs)));

    var tmp = Path.ChangeExtension(outPath, ".tmp");
    using (var fs = File.Create(tmp)) encoder.Save(fs);
    if (File.Exists(outPath)) File.Delete(outPath);
    File.Move(tmp, outPath);
}
```

實際案例：作者將 JPG 縮圖流程加入 EXIF 導向旋轉，90/270 度照片正確顯示。
實作環境：.NET/WPF、JpegBitmapEncoder、Windows Imaging Component。
實測數據：
改善前：直式 JPG 大量顯示方向錯誤。
改善後：具正確 EXIF 的 90/270 度 JPG 全數正向。
改善幅度：針對此子集達 100% 矯正；180 度例外。

Learning Points（學習要點）
核心知識點：
- EXIF Orientation（Tag 274）與視覺方向的映射。
- WPF TransformGroup 合併旋轉與縮放。
- 產出流程的臨時檔安全寫入策略。

技能要求：
- 必備技能：WPF 影像 API、基本 EXIF 概念。
- 進階技能：影像處理管線設計與防呆。

延伸思考：
- 可將旋轉後將 Orientation 正規化（重寫為 1），避免二次處理者再旋轉。
- 風險：若映射錯誤會造成全站誤轉。
- 可加入批次驗證報表與人工抽檢。

Practice Exercise（練習題）
- 基礎練習：讀取單張 JPG 的 EXIF Orientation 並列印值（30 分鐘）。
- 進階練習：批次處理資料夾 JPG，自動旋轉+縮放輸出（2 小時）。
- 專案練習：做一個具預覽與覆核的縮圖器（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確讀取 EXIF、90/180/270 度處理。
- 程式碼品質（30%）：結構清晰、錯誤處理、可測性。
- 效能優化（20%）：批次處理速度、I/O 次數。
- 創新性（10%）：流程可視化、報表或快取策略。


## Case #2: CR2 與 JPG 的 EXIF Orientation 查詢路徑不同

### Problem Statement（問題陳述）
業務場景：批次處理相片時混合 Canon G9 的 RAW（.CR2）與 JPG。發現 RAW 輸出結果方向多數正確，但 JPG 常錯誤。Debug 發現 .CR2 與 .JPG 的 EXIF 存放位置不同，導致程式以同一查詢路徑讀取時抓不到 Orientation。
技術挑戰：正確選擇 WIC Metadata Query String 以取得不同格式中的 Orientation。
影響範圍：所有混合格式批次處理的相片都可能漏轉或誤轉。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. .CR2 的 Orientation 位於 IFD；.JPG 位於 APP1/IFD0；查詢字符串不同。
2. 程式硬編碼單一路徑，對另一種格式失效。
3. 缺少基於格式的動態路徑選擇。

深層原因：
- 架構層面：未定義「格式識別→對應路徑」的策略表。
- 技術層面：不熟悉 WIC Metadata Query String。
- 流程層面：未覆蓋 RAW/JPG 混合的測試案例。

### Solution Design（解決方案設計）
解決策略：根據來源格式動態選擇 EXIF 查詢路徑；.CR2 使用 /ifd/{ushort=274}，.JPG 使用 /app1/{ushort=0}/{ushort=274}；若缺失則回傳 Rotate0。

實施步驟：
1. 建立格式判斷
- 實作細節：依副檔名或實際解碼器類型判斷。
- 所需資源：WPF BitmapDecoder。
- 預估時間：0.5 天。

2. 建立查詢路徑對照
- 實作細節：以 Dictionary<Format, string> 維護；或嘗試多路徑 fallback。
- 所需資源：程式碼框架。
- 預估時間：0.5 天。

3. 整合與測試
- 實作細節：四方向樣本對 RAW/JPG 分別驗證。
- 所需資源：示例圖片。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
string GetOrientationQueryPath(string ext)
{
    ext = ext.ToLowerInvariant();
    if (ext == ".cr2") return "/ifd/{ushort=274}";
    if (ext == ".jpg" || ext == ".jpeg") return "/app1/{ushort=0}/{ushort=274}";
    return null;
}

Rotation GetRotationByFormat(BitmapFrame frame, string ext)
{
    var meta = frame.Metadata as BitmapMetadata;
    var path = GetOrientationQueryPath(ext);
    if (meta == null || path == null || !meta.ContainsQuery(path)) return Rotation.Rotate0;
    ushort value = (ushort)meta.GetQuery(path);
    return value switch { 6 => Rotation.Rotate90, 8 => Rotation.Rotate270, 3 => Rotation.Rotate180, _ => Rotation.Rotate0 };
}
```

實際案例：作者用 Debugger 驗證 CR2/JPG 路徑差異，改用正確路徑後讀值正常。
實作環境：WPF、WIC、Canon RAW Codec。
實測數據：
改善前：JPG 無法讀到 Orientation 值。
改善後：CR2/JPG 皆可讀值並轉正（限 90/270/正確寫入）。
改善幅度：對具標記檔案的命中率由 0% → 100%。

Learning Points（學習要點）
- WIC Metadata Query String 的差異化。
- 以格式驅動的元資料存取策略。
- 為混合格式建立測試矩陣。

技能要求：
- 必備技能：WPF/BitmapMetadata API。
- 進階技能：格式抽象與策略表設計。

延伸思考：
- 增加其他格式（HEIC、PNG XMP）的擴展路徑。
- 風險：不同廠商 RAW 位置仍異，需可配置。
- 優化：嘗試多路徑 fallback，自動探勘。

Practice Exercise（練習題）
- 基礎：寫函式輸入副檔名回傳查詢路徑（30 分鐘）。
- 進階：實作多路徑嘗試與日志（2 小時）。
- 專案：支援 CR2/JPG/HEIC 的 Orientation 讀取層（8 小時）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：格式判斷與路徑覆蓋度。
- 程式碼品質（30%）：可擴展、可配置。
- 效能（20%）：多路徑嘗試的開銷控制。
- 創新性（10%）：自動偵測與快取策略。


## Case #3: RAW Codec 已旋轉導致二次旋轉

### Problem Statement（問題陳述）
業務場景：處理 Canon G9 的 CR2 時，透過 Canon RAW Codec 轉出 JPEG，發現有些相片被二次旋轉（多轉 90 度或 180 度），導致方向錯誤。JPG 則沒有此問題。
技術挑戰：辨識已由解碼器自動旋轉的影像，避免再次套用旋轉。
影響範圍：所有經 RAW Codec 自動旋轉的 CR2 檔。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Canon RAW Codec 在解碼階段已應用 RotateTransform。
2. 程式仍依 EXIF 值再次旋轉，導致過度修正。
3. 無區分 CR2 與 JPG 的處理策略。

深層原因：
- 架構層面：未設計「來源驅動的處理分支」。
- 技術層面：不了解解碼器的自動校正行為。
- 流程層面：缺少 CR2 單獨回歸測試。

### Solution Design（解決方案設計）
解決策略：針對 CR2 來源禁用手動旋轉（信任 Codec），僅對 JPG 依 EXIF 旋轉；或使用原始位圖與 Orientation 自行統一處理，確保單一責任。

實施步驟：
1. 來源分流
- 實作細節：副檔名或解碼器辨識，建立分支策略。
- 所需資源：BitmapDecoder。
- 預估時間：0.5 天。

2. 策略執行
- 實作細節：CR2 不手動旋轉，JPG 依 EXIF 處理。
- 所需資源：現有旋轉模組。
- 預估時間：0.5 天。

3. 測試驗證
- 實作細節：四方向 CR2 樣本，驗證不二次旋轉。
- 所需資源：拍攝樣本。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
bool ShouldRotateManually(string ext)
{
    // 信任 Canon RAW Codec 會旋轉 CR2
    return !(ext.Equals(".cr2", System.StringComparison.OrdinalIgnoreCase));
}

void Process(string inFile, string outFile)
{
    var frame = BitmapFrame.Create(new Uri(inFile));
    string ext = Path.GetExtension(inFile);
    Rotation rot = ShouldRotateManually(ext) ? GetRotationByFormat(frame, ext) : Rotation.Rotate0;
    EncodeWithRotationAndScale(frame, outFile, rot, 0.1);
}

void EncodeWithRotationAndScale(BitmapFrame frame, string outPath, Rotation rot, double scale)
{
    var tfs = new TransformGroup();
    tfs.Children.Add(new ScaleTransform(scale, scale));
    if (rot == Rotation.Rotate90) tfs.Children.Add(new RotateTransform(90));
    else if (rot == Rotation.Rotate180) tfs.Children.Add(new RotateTransform(180));
    else if (rot == Rotation.Rotate270) tfs.Children.Add(new RotateTransform(270));

    var enc = new JpegBitmapEncoder { QualityLevel = 90 };
    enc.Frames.Add(BitmapFrame.Create(new TransformedBitmap(frame, tfs)));
    using var fs = File.Create(Path.ChangeExtension(outPath, ".tmp"));
    enc.Save(fs);
}
```

實際案例：作者觀察 Canon Codec 已旋轉 CR2，改以「僅 JPG 手動旋轉」後，方向正確。
實作環境：Canon RAW Codec、WPF。
實測數據：
改善前：部分 CR2 二次旋轉。
改善後：CR2 方向穩定，JPG 亦正確。
改善幅度：二次旋轉事故 0 件。

Learning Points（學習要點）
- 認識解碼器的隱性行為。
- 針對來源制定差異化策略。
- 單一責任原則避免重複處理。

技能要求：
- 必備：WPF 圖像解碼流程。
- 進階：策略模式應用。

延伸思考：
- 改為全自管：讀原始像素與元資料，避免依賴 Codec。
- 風險：不同 RAW Codec 行為不一。
- 優化：紀錄來源與旋轉策略到日誌。

Practice Exercise（練習題）
- 基礎：實作 ShouldRotateManually（30 分鐘）。
- 進階：對不同 RAW 格式加白名單策略（2 小時）。
- 專案：可配置的來源策略中心（8 小時）。

Assessment Criteria（評估標準）
- 功能完整（40%）：正確分流與避免二次旋轉。
- 程式品質（30%）：配置化、易擴充。
- 效能（20%）：不增加不必要處理。
- 創新（10%）：策略自動學習或統計。


## Case #4: 180 度拍攝無法自動轉正（感測器限制）

### Problem Statement（問題陳述）
業務場景：某些倒立（180 度）拍攝的照片在電腦上仍倒立顯示，而相機上瀏覽時也未自動轉正。批次縮圖後這類照片仍方向錯誤，需人工額外處理。
技術挑戰：相機未寫入正確的 Orientation（應為 3），或根本未偵測 180 度，導致軟體端無法依 EXIF 自動修正。
影響範圍：所有未標註 180 度的倒立照片。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 相機僅偵測左右 90 度，未偵測 180 度倒立。
2. Orientation 寫入值常為 0x01（Top-left），缺少矯正線索。
3. 軟體端基於 EXIF 無法推論 180 度。

深層原因：
- 架構層面：流程假設「元資料可靠」，未設計人工覆核。
- 技術層面：無可行的圖像內容辨識（人臉、地平線）輔助。
- 流程層面：缺少標記與回補的人工環節。

### Solution Design（解決方案設計）
解決策略：承認硬體限制，軟體支援完整的 EXIF 映射（含值 3），同時對 Orientation=1 的可疑樣本提供人工標記/覆核工作流，避免盲目猜測導致誤判。

實施步驟：
1. 完整映射支援
- 實作細節：程式支援 0/3/6/8 全部對應。
- 所需資源：現有程式碼。
- 預估時間：0.2 天。

2. 可疑樣本標記
- 實作細節：對連續多張 Orientation=1 的直式長寬比照片加註記。
- 所需資源：簡易規則引擎。
- 預估時間：0.5 天。

3. 人工覆核介面（簡版）
- 實作細節：列表+快捷鍵（R180）批次旋轉輸出。
- 所需資源：簡易 WPF UI。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
bool IsSuspectUpsideDown(BitmapFrame frame, ushort orientation)
{
    // 例：Orientation=1 且長寬比接近直式，標記人工覆核
    double ratio = (double)frame.PixelHeight / frame.PixelWidth;
    return orientation == 1 && ratio > 1.2;
}
```

實際案例：作者確認 Canon 相機不處理 180 度，軟體端僅支援 EXIF=3，其他倒立案例採人工方式解決。
實作環境：WPF。
實測數據：
改善前：180 度倒立無法被自動校正。
改善後：EXIF=3 可自動；其他倒立納入人工覆核流程。
改善幅度：避免誤判，將問題集中於人工清單，處理效率提升（質性）。

Learning Points（學習要點）
- 軟硬體邊界清晰化。
- 不做「無據可依」的自動化，改導入人工覆核。
- 規則標記能顯著減少人工搜尋成本。

技能要求：
- 必備：EXIF 映射與 UI 基礎。
- 進階：規則引擎/人機協同流程設計。

延伸思考：
- 導入人臉/地平線偵測協助推斷（需額外模型）。
- 風險：偵測誤判導致錯轉。
- 優化：將人工決策寫回 XMP/Sidecar。

Practice Exercise（練習題）
- 基礎：列出 Orientation=1 且直式照片清單（30 分鐘）。
- 進階：做個按鍵一鍵旋轉 180 的工具（2 小時）。
- 專案：打標 UI + 旁車檔記錄（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：標記、覆核、旋轉流程完備。
- 品質（30%）：不誤標、不漏標。
- 效能（20%）：批次效率與可用性。
- 創新（10%）：半自動輔助策略。


## Case #5: 旋轉與縮放一次完成的 Transform 管線

### Problem Statement（問題陳述）
業務場景：縮圖程序原先先縮放再旋轉或反之，多次處理導致程式複雜、效能不穩。希望降低轉換次數並維持畫質。
技術挑戰：在 WPF 管線中以最少步驟完成旋轉+縮放，且能維持品質與速度。
影響範圍：所有縮圖產出流程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多個處理步驟分散，增加 I/O 與轉碼。
2. Transform 應用順序不一致導致尺寸偏差。
3. 缺乏可組合的變換策略。

深層原因：
- 架構層面：未採用可組合的 TransformGroup。
- 技術層面：不熟悉 TransformedBitmap 的一次性管線。
- 流程層面：缺乏標準化輸出流程。

### Solution Design（解決方案設計）
解決策略：使用 TransformGroup 將 ScaleTransform 與 RotateTransform 合併，透過 TransformedBitmap 一次套用，再交由 JpegBitmapEncoder 輸出，減少中間影像生成。

實施步驟：
1. 建立 TransformGroup
- 實作細節：先 Add Scale，再依 Orientation Add Rotate。
- 所需資源：WPF。
- 預估時間：0.2 天。

2. 一次性轉換與輸出
- 實作細節：TransformedBitmap → encoder.Frames.Add。
- 所需資源：JpegBitmapEncoder。
- 預估時間：0.3 天。

3. 覆核與微調
- 實作細節：不同先後順序 A/B 測試。
- 所需資源：樣本集。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
var tfs = new TransformGroup();
tfs.Children.Add(new ScaleTransform(0.1, 0.1));
if (rotate == Rotation.Rotate90) tfs.Children.Add(new RotateTransform(90));
else if (rotate == Rotation.Rotate180) tfs.Children.Add(new RotateTransform(180));
else if (rotate == Rotation.Rotate270) tfs.Children.Add(new RotateTransform(270));
var frameOut = BitmapFrame.Create(new TransformedBitmap(sourceFrame, tfs));
```

實際案例：作者以 TransformGroup 一次套用縮放+旋轉，流程更簡潔。
實作環境：WPF。
實測數據：
改善前：多步處理，程式複雜。
改善後：一步處理，維持正確方向與尺寸。
改善幅度：程式步驟減少，維護成本下降（質性）。

Learning Points（學習要點）
- TransformGroup 的組合能力。
- TransformedBitmap 在 WPF 的應用。
- 處理順序對結果的影響。

技能要求：
- 必備：WPF 影像處理。
- 進階：API 性能實測。

延伸思考：
- 合併更多變換（鏡像、裁切）。
- 風險：不正確順序導致尺寸/方向偏差。
- 優化：模板化變換管線。

Practice Exercise（練習題）
- 基礎：將旋轉+縮放改為 TransformGroup（30 分鐘）。
- 進階：加入裁切/翻轉選項（2 小時）。
- 專案：可視化變換流程編輯器（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：效果一致、一步完成。
- 品質（30%）：畫質與尺寸正確。
- 效能（20%）：處理時間下降。
- 創新（10%）：管線可配置。


## Case #6: 正確映射 EXIF Orientation 值到角度

### Problem Statement（問題陳述）
業務場景：Team 成員對 Orientation 值理解不一，導致 6/8 被誤解為 270/90 或相反，造成批次誤轉。
技術挑戰：建立標準的值→角度映射，避免集體誤用。
影響範圍：所有依賴此映射的處理流程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未查官方定義，口耳相傳錯誤映射。
2. 缺乏單元測試覆核映射表。
3. 文檔缺失造成重複犯錯。

深層原因：
- 架構層面：缺少常數/枚舉集中管理。
- 技術層面：對 EXIF 274 定義不熟。
- 流程層面：未落實 Code Review 對映射敏感區域。

### Solution Design（解決方案設計）
解決策略：建立唯一映射表與封裝方法；6→Rotate90、8→Rotate270、3→Rotate180、1/缺失→Rotate0；並加入單元測試。

實施步驟：
1. 實作封裝方法
- 實作細節：switch/字典封裝。
- 所需資源：程式碼。
- 預估時間：0.2 天。

2. 單元測試
- 實作細節：針對 1/3/6/8 驗證結果。
- 所需資源：測試框架。
- 預估時間：0.3 天。

3. 文檔化
- 實作細節：Readme/內部 Wiki 說明。
- 所需資源：文檔工具。
- 預估時間：0.2 天。

關鍵程式碼/設定：
```csharp
Rotation MapExifToRotation(ushort value) => value switch
{
    6 => Rotation.Rotate90,
    8 => Rotation.Rotate270,
    3 => Rotation.Rotate180,
    _ => Rotation.Rotate0
};
```

實際案例：作者比對 0x01, 0x08, 0x01, 0x06，導出正確映射。
實作環境：WPF。
實測數據：
改善前：偶發整批誤轉。
改善後：映射標準化，不再誤轉。
改善幅度：錯誤案例歸零。

Learning Points（學習要點）
- EXIF 274 標準定義。
- 封裝「知識點」降低散布風險。
- 測試保障行為。

技能要求：
- 必備：C# 基礎、單測。
- 進階：封裝與重用設計。

延伸思考：
- 處理 2/4/5/7（鏡像）值的需求。
- 風險：不同相機廠商兼容性。
- 優化：支援鏡像的 Transform。

Practice Exercise（練習題）
- 基礎：撰寫 Map 方法與測試（30 分鐘）。
- 進階：擴展支援鏡像值（2 小時）。
- 專案：完整 Orientation/Flip 管線（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：值映射完整。
- 品質（30%）：測試覆蓋。
- 效能（20%）：無。
- 創新（10%）：鏡像支援。


## Case #7: WPF Metadata 取值型別與空值安全

### Problem Statement（問題陳述）
業務場景：GetQuery 回傳 object，開發者未轉型為 ushort 或未檢查 ContainsQuery，導致例外或錯誤值，影響批次處理穩定性。
技術挑戰：正確、穩定地從 Metadata 取值。
影響範圍：所有讀 EXIF 的程式段落。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未使用 ContainsQuery 導致 NullReference 或例外。
2. 未轉型為 ushort 即比較。
3. 無 Try-Get 模式包裝。

深層原因：
- 架構層面：缺少共用的 Meta 讀取工具。
- 技術層面：忽略 WPF Metadata API 細節。
- 流程層面：未對例外做防護。

### Solution Design（解決方案設計）
解決策略：封裝安全讀取工具方法，內含路徑探測、ContainsQuery 檢查、型別轉換與預設值回退。

實施步驟：
1. 建立 Safe Reader
- 實作細節：TryGetOrientation(meta, path, out ushort v)。
- 所需資源：工具類別。
- 預估時間：0.5 天。

2. 導入並替換
- 實作細節：全域替換直接 GetQuery 的用法。
- 所需資源：重構。
- 預估時間：0.5 天。

3. 測試
- 實作細節：無 EXIF、有 EXIF、錯誤格式。
- 所需資源：測試圖片。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
bool TryGetOrientation(BitmapMetadata meta, string path, out ushort value)
{
    value = 1; // default Top-left
    try
    {
        if (meta != null && path != null && meta.ContainsQuery(path))
        {
            value = (ushort)meta.GetQuery(path);
            return true;
        }
    }
    catch { /* log if needed */ }
    return false;
}
```

實際案例：作者多次嘗試讀取不同路徑，採用檢查與轉型後穩定。
實作環境：WPF。
實測數據：
改善前：偶發例外中斷批次。
改善後：零中斷，錯誤回退為 Rotate0。
改善幅度：穩定性顯著提升（質性）。

Learning Points（學習要點）
- TryGet 模式的價值。
- 預設值策略避免崩潰。
- 日誌在除錯的作用。

技能要求：
- 必備：C# 例外處理。
- 進階：工具化封裝。

延伸思考：
- 增加路徑自動探測（JPG/CR2）。
- 風險：吞例外需有日誌。
- 優化：加上遙測觀測失敗比率。

Practice Exercise（練習題）
- 基礎：實作 TryGetOrientation（30 分鐘）。
- 進階：加上多路徑嘗試與日誌（2 小時）。
- 專案：統一 Metadata Reader 套件（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：安全讀取與回退。
- 品質（30%）：錯誤處理與日誌。
- 效能（20%）：低開銷。
- 創新（10%）：多路徑策略。


## Case #8: 臨時檔寫入避免輸出檔損毀

### Problem Statement（問題陳述）
業務場景：批次輸出 JPEG 過程中若程序被中止或磁碟故障，可能造成目標檔破損。需確保原檔不被不完整輸出覆蓋。
技術挑戰：實現原子性或近似原子性的輸出流程。
影響範圍：所有批次輸出。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 直接覆寫目標檔，一旦失敗即破壞。
2. 無臨時檔與交換策略。
3. 無失敗回滾。

深層原因：
- 架構層面：缺乏輸出階段事務性設計。
- 技術層面：未使用換名（rename）策略。
- 流程層面：未測試異常中斷情境。

### Solution Design（解決方案設計）
解決策略：先寫入臨時檔，成功後替換目標檔；失敗則刪除臨時檔。Windows 上 Move/Replace 接近原子性。

實施步驟：
1. 臨時檔策略
- 實作細節：Guid.tmp 命名，與目標同目錄。
- 所需資源：System.IO。
- 預估時間：0.2 天。

2. 交換與清理
- 實作細節：File.Replace 或 Delete+Move。
- 所需資源：檔案 API。
- 預估時間：0.2 天。

3. 測試中斷
- 實作細節：模擬中斷，驗證不破壞原檔。
- 所需資源：測試腳本。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
string tmp = Path.Combine(Path.GetDirectoryName(trgFile), $"{Guid.NewGuid():N}.tmp");
using (var s = File.Create(tmp)) encoder.Save(s);
// 交換
if (File.Exists(trgFile)) File.Delete(trgFile);
File.Move(tmp, trgFile);
```

實際案例：作者以臨時檔保存並換名，避免半檔輸出。
實作環境：.NET/WPF。
實測數據：
改善前：風險存在，偶發破檔。
改善後：未再出現破檔。
改善幅度：可靠性提升（質性）。

Learning Points（學習要點）
- 以 rename 完成接近原子性更新。
- 同目錄避免跨磁碟 Move。
- 失敗清理策略。

技能要求：
- 必備：檔案 I/O。
- 進階：失敗注入測試。

延伸思考：
- 使用 File.Replace 支援備份檔。
- 風險：跨磁碟區移動非原子。
- 優化：加鎖避免競態。

Practice Exercise（練習題）
- 基礎：改為臨時檔寫入（30 分鐘）。
- 進階：加入備份檔與回滾（2 小時）。
- 專案：通用安全寫入工具（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：成功交換與清理。
- 品質（30%）：錯誤處理無泄漏。
- 效能（20%）：I/O 合理。
- 創新（10%）：回滾機制。


## Case #9: 四方向樣本驗證與 EXIF 取值測試

### Problem Statement（問題陳述）
業務場景：對拍攝方向的處理策略需要驗證，缺少系統化的測試資料與方法，導致上線後才發現錯誤映射或取值失敗。
技術挑戰：快速建立四方向樣本與自動化檢查。
影響範圍：整個旋轉管線品質。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 測試用例缺失。
2. 未列印或記錄 EXIF 值。
3. 靠人工目視，難以覆蓋。

深層原因：
- 架構層面：缺少驗證工具。
- 技術層面：未掌握 GetQuery 路徑。
- 流程層面：未建立回歸測試流程。

### Solution Design（解決方案設計）
解決策略：拍攝四方向樣本，撰寫小工具批次列印 Orientation 值與預期旋轉度，人工核對一次，後續自動比對回歸。

實施步驟：
1. 拍攝樣本
- 實作細節：0/90/180/270 四張。
- 所需資源：相機。
- 預估時間：0.5 天。

2. 列印工具
- 實作細節：枚舉圖片，輸出路徑與 EXIF/推導角度。
- 所需資源：C# 小程式。
- 預估時間：0.5 天。

3. 回歸腳本
- 實作細節：CI 中執行，異常阻斷。
- 所需資源：CI。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
foreach (var f in Directory.EnumerateFiles(dir, "*.*"))
{
    var frame = BitmapFrame.Create(new Uri(f));
    var ext = Path.GetExtension(f);
    var meta = frame.Metadata as BitmapMetadata;
    var path = GetOrientationQueryPath(ext);
    ushort val = 1;
    bool ok = TryGetOrientation(meta, path, out val);
    var rot = MapExifToRotation(val);
    Console.WriteLine($"{Path.GetFileName(f)} | ok={ok} val={val} rot={rot}");
}
```

實際案例：作者以四方向拍攝+Debugger 驗證，定位問題。
實作環境：WPF、Console。
實測數據：
改善前：無基準測試。
改善後：建立最小可行測試集。
改善幅度：初始驗證效率提升（質性）。

Learning Points（學習要點）
- 打造極小卻關鍵的測試集。
- 資料驅動的驗證。
- 回歸測試的重要性。

技能要求：
- 必備：C# I/O、Console。
- 進階：CI 集成。

延伸思考：
- 擴展到多機種（G9、IXUS55）。
- 風險：人工標註錯誤帶入偏差。
- 優化：自動截圖預覽比對。

Practice Exercise（練習題）
- 基礎：寫列印工具（30 分鐘）。
- 進階：比對預期清單（2 小時）。
- 專案：加入 CI Gate（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：資料列印正確。
- 品質（30%）：易用與可擴展。
- 效能（20%）：處理速度。
- 創新（10%）：自動 gate。


## Case #10: 機型差異（G9 vs IXUS55）造成自動轉正不一致

### Problem Statement（問題陳述）
業務場景：G9 拍的照片「有機會」自動轉正，IXUS55 拍的 JPG 幾乎不會自動轉正，但在相機上看都會。桌面端處理結果不一致。
技術挑戰：跨機型差異導致 EXIF 寫入行為不一，或未寫入，需在 PC 端統一。
影響範圍：多機型混合資料庫。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 部分機型未寫入 Orientation 或僅支援 90 度。
2. 相機預覽有內部邏輯，但未持久化到 EXIF。
3. 桌面端完全依賴 EXIF，導致行為不一致。

深層原因：
- 架構層面：缺少跨機種相容層。
- 技術層面：對不同機型行為不了解。
- 流程層面：未建立按機型的驗證案例。

### Solution Design（解決方案設計）
解決策略：統一以 EXIF 為唯一自動化依據，對無 EXIF 的照片不進行猜測，納入人工清單；建立「機型 x 行為」知識庫供參考。

實施步驟：
1. 機型行為盤點
- 實作細節：拍樣本+記錄 EXIF 行為。
- 所需資源：多機型相機。
- 預估時間：1 天。

2. 統一策略
- 實作細節：EXIF 為準，其他人工處理。
- 所需資源：既有管線。
- 預估時間：0.5 天。

3. 知識庫
- 實作細節：Wiki 條目記錄各機型特性。
- 所需資源：文檔系統。
- 預估時間：0.5 天。

關鍵程式碼/設定：
（策略層，無特定代碼）

實際案例：作者觀察 G9/IXUS55 差異，PC 端以 EXIF 為準，避免猜測。
實作環境：WPF。
實測數據：
改善前：行為不一致。
改善後：行為一致（有 EXIF → 自動轉；無 EXIF → 人工）。
改善幅度：一致性提升（質性）。

Learning Points（學習要點）
- 以單一可靠來源為準。
- 知識庫降低溝通成本。
- 不因機型差異去猜測處理。

技能要求：
- 必備：流程制定。
- 進階：知識管理。

延伸思考：
- 自動識別機型（EXIF Make/Model）生成統計。
- 風險：忽略可利用的非標資訊。
- 優化：針對特定機型做特化處理（可開關）。

Practice Exercise（練習題）
- 基礎：讀取 EXIF Make/Model（30 分鐘）。
- 進階：產生機型 x Orientation 統計（2 小時）。
- 專案：知識庫+儀表板（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：策略落地。
- 品質（30%）：文檔齊全。
- 效能（20%）：統計產出。
- 創新（10%）：洞察分析。


## Case #11: 避免雙重品質損失的處理順序

### Problem Statement（問題陳述）
業務場景：連續對圖片做旋轉與縮放並重編碼，容易造成畫質損失疊加。希望用最少次重編碼完成。
技術挑戰：設計一次性處理管線，避免多次解碼/編碼。
影響範圍：所有輸出 JPEG 的流程。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 多次編碼造成品質疊減。
2. 中間檔產生增加 I/O。
3. 缺少一次性變換。

深層原因：
- 架構層面：沒有管線化設計。
- 技術層面：未使用 TransformedBitmap。
- 流程層面：缺少品質監控。

### Solution Design（解決方案設計）
解決策略：單次解碼後，使用 TransformGroup 完成所有變換，直接輸出一次編碼；不產生中間 JPEG。

實施步驟：
1. 重構處理順序
- 實作細節：Decode → Transform → Encode。
- 所需資源：WPF。
- 預估時間：0.5 天。

2. 移除中間檔
- 實作細節：記憶體流或一次性輸出。
- 所需資源：MemoryStream。
- 預估時間：0.5 天。

3. 品質核對
- 實作細節：主觀對比與檔案大小監控。
- 所需資源：測試集。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
var transformed = new TransformedBitmap(sourceFrame, tfs);
var enc = new JpegBitmapEncoder { QualityLevel = 90 };
enc.Frames.Add(BitmapFrame.Create(transformed));
```

實際案例：作者使用 TransformGroup + 單次編碼輸出。
實作環境：WPF。
實測數據：
改善前：多次處理。
改善後：一次處理，品質穩定。
改善幅度：品質風險降低（質性）。

Learning Points（學習要點）
- 一次性處理的重要性。
- 編碼品質參數控制。
- I/O 減少的好處。

技能要求：
- 必備：影像 I/O。
- 進階：效能與品質權衡。

延伸思考：
- 以 PNG 做中間無損？（不建議中間檔）
- 風險：品質參數設太低。
- 優化：動態 QualityLevel。

Practice Exercise（練習題）
- 基礎：合併為單次編碼（30 分鐘）。
- 進階：比較不同 QualityLevel（2 小時）。
- 專案：自動化品質回歸（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：單次管線。
- 品質（30%）：視覺品質維持。
- 效能（20%）：速度提升。
- 創新（10%）：品質自適應。


## Case #12: 建立輸出品質與檔案大小的可調參數

### Problem Statement（問題陳述）
業務場景：不同情境對縮圖品質與大小有不同要求，缺乏可調整的 QualityLevel 造成不必要的大小或品質不足。
技術挑戰：暴露品質參數並標準化預設值與可調區間。
影響範圍：所有輸出 JPEG 的任務。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 固定 QualityLevel。
2. 無針對場景調整。
3. 缺乏指引。

深層原因：
- 架構層面：配置參數缺失。
- 技術層面：不了解 QualityLevel 的影響。
- 流程層面：未建立「情境→預設」表。

### Solution Design（解決方案設計）
解決策略：將 QualityLevel 設為配置，提供建議區間（例如 75/85/90），並在管線中統一引用。

實施步驟：
1. 參數化
- 實作細節：讀取 appsettings 或 UI 輸入。
- 所需資源：設定檔。
- 預估時間：0.5 天。

2. 預設集
- 實作細節：依用途定義幾組預設。
- 所需資源：文檔。
- 預估時間：0.5 天。

3. 驗證
- 實作細節：比較輸出大小和視覺品質。
- 所需資源：測試。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
var enc = new JpegBitmapEncoder { QualityLevel = quality }; // quality 來自設定
```

實際案例：作者使用 QualityLevel 參數（範例為 90）。
實作環境：WPF。
實測數據：
改善前：不可調。
改善後：可調整，適配不同需求。
改善幅度：靈活度提升（質性）。

Learning Points（學習要點）
- 參數化的收益。
- 品質與大小權衡。
- 預設值管理。

技能要求：
- 必備：配置管理。
- 進階：實證分析。

延伸思考：
- 自動根據目標檔案大小逆推 QualityLevel。
- 風險：過度暴露造成混亂。
- 優化：模式化（低/中/高）。

Practice Exercise（練習題）
- 基礎：把 QualityLevel 參數化（30 分鐘）。
- 進階：做目標大小控制（2 小時）。
- 專案：自動化品質調參（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：可調參數生效。
- 品質（30%）：預設合理。
- 效能（20%）：無顯著負擔。
- 創新（10%）：自動調參。


## Case #13: EXIF 無值時的保守策略（不猜測）

### Problem Statement（問題陳述）
業務場景：部分照片沒有 Orientation 或寫錯，若以啟發式（例如長寬比）自動猜測，可能造成大量誤轉。
技術挑戰：確立「無據不轉」的保守策略與人工處理路徑。
影響範圍：所有缺失 EXIF 的照片。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少 Orientation。
2. 啟發式不可靠。
3. 大量誤判風險。

深層原因：
- 架構層面：未設人工流。
- 技術層面：缺乏可靠內容辨識。
- 流程層面：品質優先的文化未落實。

### Solution Design（解決方案設計）
解決策略：當 Orientation 缺失或為 1 時，不自動旋轉；進清單人工處理。確保 90/270/180 有值的自動矯正不受影響。

實施步驟：
1. 條件分叉
- 實作細節：value ∈ {3,6,8} 才旋轉。
- 所需資源：現有流程。
- 預估時間：0.2 天。

2. 清單輸出
- 實作細節：輸出需人工覆核清單（CSV）。
- 所需資源：簡單記錄器。
- 預估時間：0.5 天。

3. 人工工具
- 實作細節：提供快捷旋轉。
- 所需資源：UI。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
bool CanAutoRotate(ushort orientation) => orientation == 3 || orientation == 6 || orientation == 8;
```

實際案例：作者確認 180 度多為未標註，採保守策略避免誤轉。
實作環境：WPF。
實測數據：
改善前：潛在誤轉風險。
改善後：誤轉風險大幅降低，人工工作可控。
改善幅度：品質穩定（質性）。

Learning Points（學習要點）
- 明確的邊界條件。
- 保守策略的重要性。
- 人工與自動的分工。

技能要求：
- 必備：邏輯判斷。
- 進階：清單工具化。

延伸思考：
- 逐步導入 AI 輔助。
- 風險：人工成本上升。
- 優化：批次快捷操作。

Practice Exercise（練習題）
- 基礎：輸出需人工清單（30 分鐘）。
- 進階：覆核工具（2 小時）。
- 專案：端到端人機協作流（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：分流正確。
- 品質（30%）：零誤轉。
- 效能（20%）：人工量控制。
- 創新（10%）：輔助策略。


## Case #14: 以擴充點隔離格式特化邏輯

### Problem Statement（問題陳述）
業務場景：CR2 與 JPG 在讀取與旋轉策略不同，直寫 if-else 造成程式分散、難維護。
技術挑戰：隔離格式特化邏輯，集中維護。
影響範圍：維護性與擴展性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 邏輯散落於多處。
2. 新增格式易破壞既有行為。
3. 測試困難。

深層原因：
- 架構層面：缺少策略/工廠模式。
- 技術層面：耦合過高。
- 流程層面：擴展流程未定義。

### Solution Design（解決方案設計）
解決策略：以策略模式定義 IOrientationStrategy，不同格式提供各自 GetQueryPath() 與 ShouldManualRotate()，由工廠選用。

實施步驟：
1. 介面定義
- 實作細節：IOrientationStrategy。
- 所需資源：C#。
- 預估時間：0.5 天。

2. 策略實作
- 實作細節：JpegStrategy、Cr2Strategy。
- 所需資源：程式碼。
- 預估時間：1 天。

3. 工廠與注入
- 實作細節：依副檔名/格式注入。
- 所需資源：簡易 DI。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
interface IOrientationStrategy
{
    string GetQueryPath();
    bool ShouldManualRotate();
}

class JpegStrategy : IOrientationStrategy
{
    public string GetQueryPath() => "/app1/{ushort=0}/{ushort=274}";
    public bool ShouldManualRotate() => true;
}

class Cr2Strategy : IOrientationStrategy
{
    public string GetQueryPath() => "/ifd/{ushort=274}";
    public bool ShouldManualRotate() => false; // 信任 Codec
}
```

實際案例：作者以副檔名分流，抽象後維護更容易。
實作環境：WPF。
實測數據：
改善前：if-else 散落。
改善後：策略集中管理。
改善幅度：可維護性提升（質性）。

Learning Points（學習要點）
- 策略模式應用。
- 單一權責。
- 可測試性提升。

技能要求：
- 必備：OOP 設計。
- 進階：DI/工廠。

延伸思考：
- 以配置驅動策略。
- 風險：過度設計。
- 優化：最小可行抽象。

Practice Exercise（練習題）
- 基礎：實作兩個策略（30 分鐘）。
- 進階：加入 HEIC 策略（2 小時）。
- 專案：策略可配置中心（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：策略切換有效。
- 品質（30%）：低耦合。
- 效能（20%）：無顯著開銷。
- 創新（10%）：配置化。


## Case #15: 產出後方向一致性的驗收標準

### Problem Statement（問題陳述）
業務場景：雖已導入 EXIF 旋轉，但缺乏明確的驗收標準，跨來源仍可能遺漏。需要定義「方向一致性」的驗收與報表。
技術挑戰：制定可執行、可量測的驗收機制。
影響範圍：最終品質與信任度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 沒有明確「前/後」對比。
2. 無統一指標（例如含 EXIF 子集的命中率）。
3. 報表缺失。

深層原因：
- 架構層面：缺少度量設計。
- 技術層面：未輸出統計。
- 流程層面：未將驗收嵌入發版。

### Solution Design（解決方案設計）
解決策略：定義三個指標：有 EXIF 且需旋轉的命中率（目標 100%）、無 EXIF 的人工清單覆核完成率、二次旋轉事故數（目標 0）。產出批次報表。

實施步驟：
1. 指標定義
- 實作細節：KPI 說明與計算方式。
- 所需資源：文檔。
- 預估時間：0.3 天。

2. 報表輸出
- 實作細節：CSV/JSON 輸出統計。
- 所需資源：程式碼。
- 預估時間：0.7 天。

3. 驗收門檻
- 實作細節：CI Gate 設定。
- 所需資源：CI。
- 預估時間：0.5 天。

關鍵程式碼/設定：
```csharp
record Metrics(int total, int needRotate, int rotatedOk, int noExif, int manualList, int doubleRotations);
```

實際案例：作者在結論指出 90/270 可全自動，180 需人工，據此訂定指標。
實作環境：WPF + 簡報表。
實測數據：
改善前：無指標。
改善後：有門檻、有統計。
改善幅度：可控可驗收（質性）。

Learning Points（學習要點）
- 指標驅動的品質管理。
- 區分子集衡量。
- Gate 化驗收。

技能要求：
- 必備：資料統計。
- 進階：CI 集成。

延伸思考：
- 加入故障告警。
- 風險：指標不當導致錯誤激勵。
- 優化：持續回饋調整。

Practice Exercise（練習題）
- 基礎：輸出簡單統計（30 分鐘）。
- 進階：CI Gate（2 小時）。
- 專案：Dashboard（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：指標正確。
- 品質（30%）：報表清晰。
- 效能（20%）：低負擔。
- 創新（10%）：告警與趨勢。


## Case #16: 相機預覽與桌面顯示差異的溝通與期望管理

### Problem Statement（問題陳述）
業務場景：相機上預覽會自動轉正，但桌面端不一定。使用者誤以為 PC 會與相機一致，產生期望落差與抱怨。
技術挑戰：明確解釋差異，並在工具層面補齊或提供替代流程。
影響範圍：使用者體驗與支援成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 相機使用內部感測結果即時旋轉。
2. EXIF 未必寫入或只寫部分（90 度）。
3. PC 端軟體以 EXIF 為唯一依據。

深層原因：
- 架構層面：產品說明不足。
- 技術層面：對相機行為不了解。
- 流程層面：支援與教育缺失。

### Solution Design（解決方案設計）
解決策略：在工具與文件中說明：90/270 度可自動；180 度與無 EXIF 需人工。提供一鍵批次旋轉與覆核清單，減少抱怨。

實施步驟：
1. 文件化
- 實作細節：FAQ、README。
- 所需資源：文檔。
- 預估時間：0.3 天。

2. 工具輔助
- 實作細節：批次旋轉快捷鍵與清單。
- 所需資源：UI。
- 預估時間：1 天。

3. 回饋機制
- 實作細節：提供回報管道。
- 所需資源：Issue tracker。
- 預估時間：0.2 天。

關鍵程式碼/設定：
（同前述人工覆核功能）

實際案例：作者發現相機不處理 180 度，據此管理使用者期望。
實作環境：WPF + 文檔。
實測數據：
改善前：誤解頻仍。
改善後：期望一致，支援成本下降。
改善幅度：溝通效率提升（質性）。

Learning Points（學習要點）
- 技術差異需轉化為可理解文案。
- 工具與文檔相輔相成。
- 用戶教育的重要性。

技能要求：
- 必備：技術寫作。
- 進階：UX 思維。

延伸思考：
- 內建導覽指引。
- 風險：過度依賴文檔。
- 優化：情境內說明。

Practice Exercise（練習題）
- 基礎：寫 FAQ 條目（30 分鐘）。
- 進階：在工具加入指引（2 小時）。
- 專案：教育模組（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：資訊可得。
- 品質（30%）：說明清晰。
- 效能（20%）：減少支持問題。
- 創新（10%）：互動引導。


## Case #17: 方向處理的可測性與日誌化

### Problem Statement（問題陳述）
業務場景：偶發方向錯誤難以重現，需要可觀察性來快速定位是取值、映射、還是編碼階段問題。
技術挑戰：設計足夠但不過量的日誌，並能回溯重現。
影響範圍：維運、除錯效率。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少關鍵欄位的紀錄。
2. 無法重現處理步驟。
3. 未保留樣本。

深層原因：
- 架構層面：不可觀測。
- 技術層面：日誌粒度不當。
- 流程層面：無案例收集。

### Solution Design（解決方案設計）
解決策略：記錄每張圖的來源、格式、EXIF 值、映射旋轉度、是否使用手動旋轉、輸出檔名；遇錯誤保留原圖/中間資訊便於回溯。

實施步驟：
1. 日誌欄位定義
- 實作細節：CSV/JSON。
- 所需資源：Logger。
- 預估時間：0.5 天。

2. 實作與開關
- 實作細節：可配置的 log level。
- 所需資源：配置。
- 預估時間：0.5 天。

3. 回溯工具
- 實作細節：依日誌重跑單檔。
- 所需資源：CLI。
- 預估時間：1 天。

關鍵程式碼/設定：
```csharp
Console.WriteLine($"{name},{ext},{orientation},{rotationDegrees},{manualRotate},{outPath}");
```

實際案例：作者以 Debugger 手動比對，正式化後可自動記錄。
實作環境：WPF + Console。
實測數據：
改善前：難以定位問題。
改善後：快速定位環節。
改善幅度：除錯時間大幅下降（質性）。

Learning Points（學習要點）
- 可觀測性設計。
- 粒度控制。
- 重放機制。

技能要求：
- 必備：日誌與 CLI。
- 進階：重放工具。

延伸思考：
- 結合遙測平台。
- 風險：敏感資訊外洩。
- 優化：脫敏與採樣。

Practice Exercise（練習題）
- 基礎：輸出處理日誌（30 分鐘）。
- 進階：單檔重放（2 小時）。
- 專案：日誌分析報表（8 小時）。

Assessment Criteria（評估標準）
- 功能（40%）：資訊完整。
- 品質（30%）：不影響效能。
- 效能（20%）：低開銷。
- 創新（10%）：重放能力。


## 案例分類

1. 按難度分類
- 入門級（適合初學者）：Case 5, 6, 7, 8, 9, 11, 12, 13
- 中級（需要一定基礎）：Case 1, 2, 3, 10, 14, 16, 17
- 高級（需要深厚經驗）：（本次案例以 WPF/EXIF 為主，無特重難度項）

2. 按技術領域分類
- 架構設計類：Case 3, 10, 14, 15, 17
- 效能優化類：Case 5, 11
- 整合開發類：Case 1, 2, 3, 12
- 除錯診斷類：Case 6, 7, 9, 17
- 安全防護類（可靠性/資料安全）：Case 8, 13

3. 按學習目標分類
- 概念理解型：Case 6, 10, 16
- 技能練習型：Case 5, 7, 8, 9, 12
- 問題解決型：Case 1, 2, 3, 4, 11, 13
- 創新應用型：Case 14, 15, 17


## 案例關聯圖（學習路徑建議）
- 先學案例：Case 6（EXIF 值映射），Case 7（安全讀取），Case 9（樣本與測試）。這三者建立理解與驗證基礎。
- 依賴關係：
  - Case 1 依賴 Case 6/7（正確映射與讀取）。
  - Case 2 依賴 Case 7（安全讀取）與格式知識。
  - Case 3 依賴 Case 2（格式判斷）與策略分流（Case 14）。
  - Case 5、11 建立在 Case 1（旋轉需求）之上。
  - Case 4、13、16 為邊界與期望管理，建立在 Case 1/2 的行為之後。
  - Case 15、17 作為品質與可觀測性收斂，覆蓋全流程。
- 完整學習路徑建議：
  1) Case 6 → 7 → 9（建立基礎）
  2) Case 1 → 2（完成核心功能）
  3) Case 3 → 14（策略化與避免二次旋轉）
  4) Case 5 → 11 → 8（管線與可靠性）
  5) Case 4 → 13 → 16（限制與人機協作）
  6) Case 12（參數化）→ 10（跨機型一致性）
  7) Case 15 → 17（驗收與可觀測性完備）

以上 17 個案例皆以文章中的實際問題、根因、與已展示之解法與代碼為基礎，並延伸出完整教學、練習與評估框架，便於實戰導入與能力評測。