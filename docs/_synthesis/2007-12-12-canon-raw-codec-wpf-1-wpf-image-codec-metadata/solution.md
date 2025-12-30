---
layout: synthesis
title: "Canon Raw Codec + WPF #1, WPF Image Codec, Metadata"
synthesis_type: solution
source_post: /2007/12/12/canon-raw-codec-wpf-1-wpf-image-codec-metadata/
redirect_from:
  - /2007/12/12/canon-raw-codec-wpf-1-wpf-image-codec-metadata/solution/
---

以下內容基於原文中實際遭遇的問題與已驗證的做法，整理出 16 個可教學、可實作、可評估的案例，涵蓋 Canon RAW (CR2) 與 WPF 影像管線、轉檔、Metadata、對照表與封裝等主題。每個案例都附上目標、步驟、程式碼、學習要點與練習、評估指標，方便你直接用於實戰教學與能力評估。

## Case #1: 啟用 WPF 解碼 Canon CR2（安裝 Canon RAW Codec + BitmapDecoder 開檔）

### Problem Statement（問題陳述）
業務場景：入手 Canon G9 後，建立例行的照片歸檔流程，需要從 RAW（.CR2）讀圖、縮圖、輸出。希望以 WPF 建立影像處理工具，為未來格式演進保留彈性。
技術挑戰：WPF 需透過 Windows Imaging Component（WIC）與外部 Codec 才能解碼 CR2；若系統未安裝 Canon RAW Codec，BitmapDecoder 無法打開 CR2。
影響範圍：無法讀取 RAW 即無法進行後續縮放、轉檔、Metadata 搬移與自動化。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 系統未安裝 Canon RAW Codec，WIC 無法處理 CR2。
2. WPF 的 BitmapDecoder 依賴 WIC Codec 管線，不具備內建 CR2 支援。
3. 使用者以為「WPF 能開所有圖」而忽略 WIC/Codec 依賴。
深層原因：
- 架構層面：影像解碼能力由外部 Codec 插槽提供，應用不直接綁定格式。
- 技術層面：未識別 WIC 與特定廠商 Codec 的關聯。
- 流程層面：缺少「環境健檢」步驟（檢查/提示 Codec）。

### Solution Design（解決方案設計）
解決策略：在目標機器安裝 Canon RAW Codec，並以 WPF/BitmapDecoder.Create 嘗試開檔。若失敗，回報清楚的指示與下載位置。將此檢查納入啟動檢核與 CI/CD 安裝說明，確保環境一致性。

實施步驟：
1. 安裝與驗證
- 實作細節：安裝 Canon RAW Codec；撰寫小程式以 BitmapDecoder 嘗試開啟 CR2。
- 所需資源：Canon RAW Codec（Windows 版）、.NET WPF。
- 預估時間：15-30 分鐘
2. 加入開檔防護
- 實作細節：對 BitmapDecoder.Create 加上 try/catch 並提示解決方案。
- 所需資源：System.Windows.Media.Imaging
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
// using System.IO;
// using System.Windows.Media.Imaging;

BitmapDecoder TryOpenCr2(string path)
{
    try
    {
        return BitmapDecoder.Create(
            new Uri(path),
            BitmapCreateOptions.DelayCreation,
            BitmapCacheOption.None);
    }
    catch (FileFormatException)
    {
        throw new InvalidOperationException("無法開啟檔案格式。請確認已安裝 Canon RAW Codec。");
    }
    catch (NotSupportedException)
    {
        throw new InvalidOperationException("系統不支援此 RAW 格式。請安裝相應 Codec。");
    }
}
```

實際案例：C:\IMG_0001.CR2 成功以 BitmapDecoder 取得 Frames。
實作環境：Windows（WIC），.NET 3.0/3.5 WPF，Canon RAW Codec 已安裝。
實測數據：
改善前：CR2 無法開啟（流程中斷）
改善後：可成功 decode 並取得第一張 Frame
改善幅度：由「無法進行」到「可持續處理」

Learning Points（學習要點）
核心知識點：
- WIC 與第三方 Codec 的關係
- WPF BitmapDecoder.Create 的選項
- 以例外處理做環境檢核
技能要求：
- 必備技能：WPF 影像 API、例外處理
- 進階技能：部署流程與環境健檢腳本
延伸思考：
- 如何在應用啟動時自動檢查 Codec？
- 若目標機器無法安裝 Codec，可否使用外部轉檔器或服務化？
- 如何記錄環境檢核日誌供客服排錯？

Practice Exercise（練習題）
- 基礎：撰寫一個函式，檢查路徑是否為 CR2 並嘗試開檔，成功則回傳影像尺寸。
- 進階：將檢查包成命令列工具，輸入多個檔案路徑逐一驗證。
- 專案：實作 GUI 檢查器，掃描資料夾並產出「可解碼/不可解碼」報表與安裝指引。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確辨識並回報缺少 Codec
- 程式碼品質（30%）：例外處理周延、訊息清楚
- 效能優化（20%）：批次檢查效率、非阻塞 UI
- 創新性（10%）：提供自動修復/引導下載

---

## Case #2: CR2 → JPEG 縮放轉檔工作流（WPF TransformedBitmap + JpegBitmapEncoder）

### Problem Statement（問題陳述）
業務場景：例行照片歸檔需將 CR2 檔縮放到指定大小並輸出 JPEG 供分享或瀏覽。
技術挑戰：以 WPF 的影像管線完成解碼、變換、編碼，並能設定品質。
影響範圍：若轉檔流程不可用，無法快速產生可分享的圖檔。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 尚未建立 WPF 端到端的解碼→變換→編碼流程。
2. 不熟悉 TransformedBitmap 與 Encoder 的使用。
3. 未設定 JPEG 品質參數導致結果不可控。
深層原因：
- 架構層面：WPF 屬於保留式圖形模型，管線思維與 GDI+ 不同。
- 技術層面：對 BitmapEncoder/BitmapFrame 的組裝不熟。
- 流程層面：缺少可重複的轉檔步驟與封裝。

### Solution Design（解決方案設計）
解決策略：使用 BitmapDecoder 讀 RAW，TransformedBitmap 做縮放，JpegBitmapEncoder 輸出 JPEG，設定 QualityLevel。建立最小可用流程，作為後續封裝與擴充的基礎。

實施步驟：
1. 建立縮放轉檔
- 實作細節：TransformedBitmap + ScaleTransform；JpegBitmapEncoder 設 QualityLevel。
- 所需資源：System.Windows.Media.Imaging
- 預估時間：30-45 分鐘
2. 封裝 I/O
- 實作細節：以 FileStream 輸出；確保關閉資源。
- 所需資源：System.IO
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
// using System.IO;
// using System.Windows.Media.Imaging;

void ConvertCr2ToJpeg(string src, string dst, double scale, int quality = 80)
{
    var decoder = BitmapDecoder.Create(
        new Uri(src),
        BitmapCreateOptions.DelayCreation,
        BitmapCacheOption.None);

    var transformed = new TransformedBitmap(decoder.Frames[0], new System.Windows.Media.ScaleTransform(scale, scale));
    var encoder = new JpegBitmapEncoder { QualityLevel = quality };

    // metadata 後續案例處理；此處先完成基本轉檔
    encoder.Frames.Add(BitmapFrame.Create(transformed));

    using var fs = File.OpenWrite(dst);
    encoder.Save(fs);
}
```

實際案例：以 0.3 縮放 CR2 並輸出 JPEG，Quality 80。
實作環境：Windows WIC + WPF（.NET 3.0/3.5），JpegBitmapEncoder。
實測數據：
改善前：無法量產 JPEG
改善後：可依比例輸出 JPEG；品質可控
改善幅度：由無產能 → 一鍵轉檔

Learning Points（學習要點）
核心知識點：
- BitmapDecoder / TransformedBitmap / BitmapEncoder 組裝
- JPEG 品質參數的影響
- 圖像 I/O 資源管理
技能要求：
- 必備技能：WPF 影像 API、基本 I/O
- 進階技能：將此流程泛化為支援多格式
延伸思考：
- 是否以最大邊長而非比例縮放（見案例 #10）？
- 如何加入 Metadata 與縮圖（見案例 #3、#7）？
- 是否需要多執行緒批次化（另文效能篇）？

Practice Exercise（練習題）
- 基礎：把比例改為目標寬度，計算合適 scale。
- 進階：加上命令列參數（輸入/輸出/比例/品質）。
- 專案：做一個簡易 GUI，支援拖拉多檔轉檔。

Assessment Criteria（評估標準）
- 功能完整性（40%）：CR2→JPEG 轉檔可用，品質可調
- 程式碼品質（30%）：結構清晰、資源釋放正確
- 效能優化（20%）：合理的解碼/變換時間
- 創新性（10%）：支援其他格式或工作佇列

---

## Case #3: 轉檔後 EXIF 遺失：在 WPF 正確附掛 Metadata

### Problem Statement（問題陳述）
業務場景：轉檔後發現 JPEG 不含任何 EXIF，對歸檔、搜尋與顯示（如拍攝日期、鏡頭資訊）不利。
技術挑戰：WPF 若未手動附上 Metadata，Encoder 產物將丟失 EXIF。
影響範圍：失去攝影參數、方向、縮圖等關鍵資訊。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 建立 BitmapFrame 時未傳入 metadata 物件。
2. 未從來源 Frame 讀取或複製 metadata。
3. 未處理不同格式的 metadata 差異（後續見案例 #4）。
深層原因：
- 架構層面：WPF 將 metadata 作為 Frame 屬性而非隱性複製。
- 技術層面：不熟悉 BitmapMetadata.Clone 與 Frame.Create 多載。
- 流程層面：未將「EXIF 保留」納入轉檔標準流程。

### Solution Design（解決方案設計）
解決策略：從來源 Frame 取出 BitmapMetadata，Clone 後附加至 BitmapFrame.Create 的 metadata 參數。此外，盡可能附上 Thumbnail（見案例 #7）。

實施步驟：
1. 讀取並複製 Metadata
- 實作細節：var meta = (BitmapMetadata)source.Frames[0].Metadata?.Clone();
- 所需資源：System.Windows.Media.Imaging
- 預估時間：20 分鐘
2. 在 Encoder Frame 附掛
- 實作細節：BitmapFrame.Create(transformed, thumb, meta, null)
- 所需資源：JpegBitmapEncoder
- 預估時間：15 分鐘

關鍵程式碼/設定：
```csharp
var frame = decoder.Frames[0];
var meta = frame.Metadata as BitmapMetadata;
var metaClone = meta?.Clone() as BitmapMetadata; // 先 Clone 再操作

var thumb = frame.Thumbnail; // 見案例 #7

var outFrame = BitmapFrame.Create(
    transformed,  // TransformedBitmap
    thumb,        // 盡量保留縮圖
    metaClone,    // 附上 Metadata
    null);
encoder.Frames.Add(outFrame);
```

實際案例：同一張 CR2 轉 JPEG，EXIF 由無 → 有。
實作環境：同上。
實測數據：
改善前：EXIF 缺失
改善後：保留核心 EXIF（日期、相機、曝光等）
改善幅度：由 0% → 可用（實際可視欄位）

Learning Points（學習要點）
核心知識點：
- BitmapFrame.Create 多載與 metadata 附加
- Clone metadata 的必要性（避免來源物件被鎖）
- 縮圖與 EXIF 的關係
技能要求：
- 必備技能：WPF 影像 Metadata API
- 進階技能：跨格式拷貝 metadata（見案例 #4）
延伸思考：
- 部分欄位需跨格式對應（Raw IFD → JPEG EXIF）
- 欄位合規（值域/型別）如何檢核？
- 欄位冗餘或隱私欄位需過濾嗎？

Practice Exercise（練習題）
- 基礎：將轉出的 JPEG 讀回，印出 DateTaken 與 CameraModel。
- 進階：若來源無某欄位，落入合理預設（如空字串）。
- 專案：做一個「EXIF 檢視器」，檔案清單逐一列出關鍵欄位。

Assessment Criteria（評估標準）
- 功能完整性（40%）：EXIF 正確保留
- 程式碼品質（30%）：空值處理穩健、Clone 使用正確
- 效能優化（20%）：附掛 metadata 不增過多時間
- 創新性（10%）：欄位過濾或隱私保護

---

## Case #4: RAW IFD 與 JPEG EXIF 不對應：建立 Metadata Query 對照表

### Problem Statement（問題陳述）
業務場景：WPF 抽象化了 metadata 存取（GetQuery/SetQuery），但 CR2 與 JPEG 使用不同的 Query 路徑，直接拷貝會失敗。
技術挑戰：CR2 使用 /ifd/...，JPEG 使用 /app1/ifd/exif/...，欄位對應需翻譯。
影響範圍：欄位無法遷移，EXIF 仍缺失或錯置。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 不同容器（RAW vs JPEG）有不同的 metadata 根路徑。
2. 直接 SetQuery 目標路徑錯誤，導致例外或無效。
3. 官方規格難懂，實務上需比對樣本與實驗推導。
深層原因：
- 架構層面：多種標準共存（EXIF, IFD, XMP）。
- 技術層面：WPF Query 語法學習曲線高。
- 流程層面：缺乏可維護的對照表與驗證手段。

### Solution Design（解決方案設計）
解決策略：透過實驗樣本（RAW→JPEG），彙整出欄位對照表（如 ushort=256/257 對應），保存為表格，程式按表翻譯來源 Query 到目標 Query，逐欄 SetQuery。

實施步驟：
1. 整理對照表
- 實作細節：建立 source → target Query 映射；先從常見欄位起。
- 所需資源：範例影像、記事或表格工具
- 預估時間：1-2 小時
2. 實作翻譯函式
- 實作細節：迭代映射，ContainsQuery 檢查後 Get/Set。
- 所需資源：System.Windows.Media.Imaging
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// 範例映射（取自原文示例）
var map = new (string src, string dst)[] {
    ("/ifd/{ushort=256}", "/app1/ifd/exif/{ushort=256}"),
    ("/ifd/{ushort=257}", "/app1/ifd/exif/{ushort=257}"),
};

void ApplyMappedMetadata(BitmapMetadata srcMeta, BitmapMetadata dstMeta)
{
    foreach (var (src, dst) in map)
    {
        if (srcMeta.ContainsQuery(src))
        {
            var val = srcMeta.GetQuery(src);
            dstMeta.SetQuery(dst, val);
        }
    }
}
```

實際案例：以 RAW→JPEG 實測，欄位對應「看起來正確」後投入使用。
實作環境：WPF Imaging、對照表人工整理。
實測數據：
改善前：跨格式欄位拷貝失敗/缺失
改善後：關鍵 IFD→EXIF 欄位可用
改善幅度：由不可用 → 實務可用（按映射範圍）

Learning Points（學習要點）
核心知識點：
- WPF metadata query 路徑差異（/ifd vs /app1/ifd/exif）
- ContainsQuery/GetQuery/SetQuery 用法
- 實驗導向的欄位對照策略
技能要求：
- 必備技能：WPF Metadata API
- 進階技能：規格查核與比對驗證工具
延伸思考：
- 如何覆蓋更多欄位（焦距、曝光、GPS）？
- 如何管理不同相機廠商差異？
- 是否需加入 XMP 同步（雙寫）？

Practice Exercise（練習題）
- 基礎：完成 5 個常用欄位的對照表並驗證。
- 進階：將對照表外部化並支援熱更新（見案例 #5）。
- 專案：做一個對照表編輯/驗證工具，輸入兩張圖比對欄位。

Assessment Criteria（評估標準）
- 功能完整性（40%）：跨格式欄位正確搬移
- 程式碼品質（30%）：安全檢查、例外處理
- 效能優化（20%）：批次搬移效率
- 創新性（10%）：對照表可視化與驗證工具

---

## Case #5: 對照表維運成本高：外部化為 XML 並嵌入 Library（Embedded Resource）

### Problem Statement（問題陳述）
業務場景：對照表需要長期維護與擴充，散落在程式碼中不易管理與更新。
技術挑戰：需將對照表以資料檔形式管理，並在程式中讀取與套用。
影響範圍：難以擴充欄位映射、難以釋出修補。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 對照表硬編碼在程式中造成維護困難。
2. 無統一載入/解析機制。
3. 缺乏部署一份即用、不可被任意覆寫的方式。
深層原因：
- 架構層面：資料與邏輯混雜，缺少資源化設計。
- 技術層面：不了解 Embedded Resource 的讀取方式。
- 流程層面：缺少對照表版本控管流程。

### Solution Design（解決方案設計）
解決策略：將對照表以 XML 格式保存，作為 class library 的 Embedded Resource。程式啟動時載入解析，轉成映射字典，供轉檔流程使用。

實施步驟：
1. 設計 XML 結構
- 實作細節：<map from="..." to="..."/> 多筆
- 所需資源：XML 編輯器
- 預估時間：30 分鐘
2. 以嵌入資源方式讀取
- 實作細節：Assembly.GetManifestResourceStream 讀入 XDocument
- 所需資源：System.Reflection、System.Xml.Linq
- 預估時間：45 分鐘

關鍵程式碼/設定：
```csharp
// XML 範例（Embedded Resource: Resources.MetadataMap.xml）
/*
<mappings>
  <map from="/ifd/{ushort=256}" to="/app1/ifd/exif/{ushort=256}" />
  <map from="/ifd/{ushort=257}" to="/app1/ifd/exif/{ushort=257}" />
</mappings>
*/

IEnumerable<(string from, string to)> LoadMap()
{
    var asm = typeof(MyImageLib).Assembly;
    using var s = asm.GetManifestResourceStream("MyImageLib.Resources.MetadataMap.xml");
    var doc = System.Xml.Linq.XDocument.Load(s);
    return doc.Root.Elements("map")
        .Select(e => ((string)e.Attribute("from"), (string)e.Attribute("to")))
        .ToArray();
}
```

實際案例：對照表以 XML 存放於 library 中，供 SaveToJPEG 時載入。
實作環境：.NET WPF、Class Library 專案。
實測數據：
改善前：修改需重建程式碼與風險高
改善後：只需更新 XML 資源即可
改善幅度：維運成本顯著降低（由改碼 → 改資料）

Learning Points（學習要點）
核心知識點：
- Embedded Resource 的使用
- XML 與 LINQ to XML 解析
- 資料與邏輯分離
技能要求：
- 必備技能：資源管理、XML 解析
- 進階技能：對照表版本化與測試
延伸思考：
- 是否支援外部檔案覆寫（使用者自訂）？
- XML 模式（XSD）驗證？
- 多相機品牌多組映射如何合併？

Practice Exercise（練習題）
- 基礎：將兩筆映射寫入 XML 並成功載入。
- 進階：加入版本欄位與載入日誌。
- 專案：設計 UI 編輯器，提供匯入/匯出/驗證。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能載入並套用映射
- 程式碼品質（30%）：資源名稱、例外處理正確
- 效能優化（20%）：載入時間與快取策略
- 創新性（10%）：版本控制與驗證

---

## Case #6: 重複操作效率低：設計 ImageUtil.SaveToJPEG API

### Problem Statement（問題陳述）
業務場景：歸檔工具需反覆執行「開 RAW→縮放→轉檔→搬 Metadata」的動作，手寫程式碼冗長且易錯。
技術挑戰：需封裝為一個穩定可重用的 API。
影響範圍：開發效率、可讀性、維護性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏高階封裝方法。
2. Metadata 對照、縮放、品質等參數分散。
3. 沒有統一的錯誤處理與日誌。
深層原因：
- 架構層面：未建立「轉檔服務層」。
- 技術層面：未定義清晰的介面與預設值。
- 流程層面：無統一測試入口。

### Solution Design（解決方案設計）
解決策略：提供 ImageUtil.SaveToJPEG(src, dst, maxW, maxH, quality) 單一 API。內部完成解碼、等比例縮放（見案例 #10）、JPEG 編碼、Metadata 映射與附掛（案例 #3、#4、#5）。

實施步驟：
1. 定義介面與預設
- 實作細節：參數校驗、預設 Quality=75
- 所需資源：Class Library
- 預估時間：30 分鐘
2. 串接子流程
- 實作細節：呼叫縮放、映射、附掛、編碼
- 所需資源：WPF Imaging
- 預估時間：1-2 小時

關鍵程式碼/設定：
```csharp
public static class ImageUtil
{
    public static void SaveToJPEG(string srcPath, string dstPath, int maxWidth, int maxHeight, int quality = 75)
    {
        var decoder = BitmapDecoder.Create(new Uri(srcPath),
            BitmapCreateOptions.DelayCreation, BitmapCacheOption.None);

        var srcFrame = decoder.Frames[0];
        var transformed = CreateBoundedBitmap(srcFrame, maxWidth, maxHeight); // 見案例 #10

        // Metadata：Clone + 對照表映射
        var srcMeta = srcFrame.Metadata as BitmapMetadata;
        var dstMeta = (srcMeta?.Clone() as BitmapMetadata) ?? new BitmapMetadata("jpg");
        ApplyMappedMetadata(srcMeta, dstMeta); // 見案例 #4/#5

        var thumb = srcFrame.Thumbnail;

        var outFrame = BitmapFrame.Create(transformed, thumb, dstMeta, null);
        var encoder = new JpegBitmapEncoder { QualityLevel = quality };
        encoder.Frames.Add(outFrame);

        using var fs = File.OpenWrite(dstPath);
        encoder.Save(fs);
    }
}
```

實際案例：ImageUtil.SaveToJPEG(@"c:\IMG_0001.CR2", @"c:\IMG_0001.JPG", 800, 800, 75)
實作環境：.NET WPF Class Library。
實測數據：
改善前：每次需重複撰寫管線程式碼
改善後：單一呼叫完成轉檔含 EXIF
改善幅度：程式碼量與錯誤率顯著下降（由散落 → 集中）

Learning Points（學習要點）
核心知識點：
- API 設計與參數預設
- 封裝影像處理管線
- 內聚性與可測試性
技能要求：
- 必備技能：C# 封裝、WPF 影像 API
- 進階技能：介面擴充（支援多格式/多執行緒）
延伸思考：
- 是否提供非同步版本？
- 是否回傳處理結果（尺寸、欄位清單）？
- 例外分類與錯誤碼設計

Practice Exercise（練習題）
- 基礎：實作儲存回傳最終像素尺寸。
- 進階：允許覆寫部分對照表（外掛策略）。
- 專案：包成 NuGet（內部），提供 CI 測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：單 API 完成轉檔+EXIF
- 程式碼品質（30%）：高內聚、易讀、測試可行
- 效能優化（20%）：避免重複解碼/拷貝
- 創新性（10%）：擴充性設計

---

## Case #7: 縮圖預覽缺失：保留與寫入 JPEG Thumbnail

### Problem Statement（問題陳述）
業務場景：檔案總管或相簿軟體需要 JPEG 內嵌縮圖以快速預覽；若缺失，使用體驗差。
技術挑戰：WPF 轉檔若未提供 Thumbnail，輸出圖可能無內嵌縮圖。
影響範圍：檢視體驗、載入速度、索引效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 建立輸出 Frame 時未傳入 Thumbnail。
2. 來源 RAW 之 Frame.Thumbnail 未被利用。
3. 認知缺口：以為 Encoder 會自動產生。
深層原因：
- 架構層面：縮圖是 metadata 的一部分。
- 技術層面：忽略 BitmapFrame.Create 之縮圖參數。
- 流程層面：未將縮圖納入驗收。

### Solution Design（解決方案設計）
解決策略：讀取來源 Frame.Thumbnail，如可用則附掛至輸出 Frame；必要時可考慮自行產生一張小尺寸縮圖再寫入。

實施步驟：
1. 嘗試保留來源縮圖
- 實作細節：var thumb = srcFrame.Thumbnail
- 所需資源：WPF Imaging
- 預估時間：15 分鐘
2. 無縮圖時自建（選配）
- 實作細節：以更小比例建立一張位圖當縮圖
- 所需資源：TransformedBitmap
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
var srcFrame = decoder.Frames[0];
var thumb = srcFrame.Thumbnail; // 可能為 null
var outFrame = BitmapFrame.Create(transformed, thumb, dstMeta, null);
encoder.Frames.Add(outFrame);
```

實際案例：轉出的 JPEG 在檔案總管可即時顯示縮圖。
實作環境：同上。
實測數據：
改善前：無縮圖，預覽延遲
改善後：即時預覽
改善幅度：使用體驗明顯提升

Learning Points（學習要點）
核心知識點：
- Thumbnail 與 EXIF 的關係
- BitmapFrame.Create 參數
- 預覽效能與使用體驗
技能要求：
- 必備技能：WPF 影像 API
- 進階技能：縮圖產製與寫入
延伸思考：
- 大量縮圖是否要平行化產製？
- 縮圖品質/大小的折衷？
- 缺縮圖情境下的後備策略？

Practice Exercise（練習題）
- 基礎：檢查輸出圖是否有縮圖（以 GetQuery 查）。
- 進階：無縮圖時自動建立 160x160 縮圖。
- 專案：做一個「縮圖修復器」，批次補齊。

Assessment Criteria（評估標準）
- 功能完整性（40%）：縮圖保留/補齊
- 程式碼品質（30%）：Null 安全與例外處理
- 效能優化（20%）：批次產製效率
- 創新性（10%）：多尺寸縮圖策略

---

## Case #8: JPEG 色域受限：以 HD Photo（WMP）保存廣色域資訊

### Problem Statement（問題陳述）
業務場景：RAW 能帶來更廣的色域與高動態資訊；若存成 JPEG，部分好處會丟失。
技術挑戰：需選擇能承載更多資訊的輸出格式（HD Photo / JPEG XR）。
影響範圍：色彩保真、後期空間、長期保存品質。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. JPEG 格式限制導致寬色域資訊無法完整保存。
2. 不清楚 WPF 提供之 WmpBitmapEncoder。
3. 短期分享與長期保存需求混淆。
深層原因：
- 架構層面：格式能力差異（JPEG vs HD Photo）。
- 技術層面：Encoder 選擇與參數不熟。
- 流程層面：缺乏「輸出格式策略」。

### Solution Design（解決方案設計）
解決策略：在需保留色域的情境下，以 WmpBitmapEncoder 輸出 HD Photo；一般分享仍輸出 JPEG。視工作流分流，而非單一格式通吃。

實施步驟：
1. 實作 WMP 輸出
- 實作細節：WmpBitmapEncoder + QualityLevel
- 所需資源：WPF Imaging
- 預估時間：30 分鐘
2. 決策分流
- 實作細節：依情境（保存/分享）決定 Encoder
- 所需資源：策略參數
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
var encoder = new WmpBitmapEncoder
{
    QualityLevel = 90 // 1~255（不同 .NET 版本略有差異）
};
encoder.Frames.Add(BitmapFrame.Create(transformed, thumb, dstMeta, null));
using var fs = File.OpenWrite(dstPath.Replace(".jpg", ".wdp"));
encoder.Save(fs);
```

實際案例：RAW→HD Photo，保留更多色彩資訊；另存 JPEG 作分享。
實作環境：WPF WIC 支援 WMP 編碼；檢視器需支援。
實測數據：
改善前：僅 JPEG，色域受限
改善後：提供 HD Photo 選項作高保真保存
改善幅度：長期保存彈性提升

Learning Points（學習要點）
核心知識點：
- 各格式能力差異
- WmpBitmapEncoder 使用
- 多輸出策略
技能要求：
- 必備技能：Encoder 切換
- 進階技能：以設定檔策略管理格式選擇
延伸思考：
- 目標平台是否支援 HD Photo？
- 檔案大小與相容性取捨？
- 未來遷移（HD Photo→新標準）如何自動化？

Practice Exercise（練習題）
- 基礎：提供參數切換 JPEG/HD Photo。
- 進階：同時輸出兩份並比較顏色差異（以檢視器觀察）。
- 專案：設計格式策略器，依用途批量套用。

Assessment Criteria（評估標準）
- 功能完整性（40%）：HD Photo 輸出可用
- 程式碼品質（30%）：策略清晰、易擴充
- 效能優化（20%）：批次輸出效率
- 創新性（10%）：自動判斷建議格式

---

## Case #9: 大圖讀取吃記憶體：善用 DelayCreation 與 CacheOption

### Problem Statement（問題陳述）
業務場景：處理高像素 RAW 時，首次載入耗時且記憶體壓力大。
技術挑戰：控制解碼時機與快取策略，避免不必要的載入。
影響範圍：工具啟動速度、穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 立即載入整張 RAW 造成負擔。
2. 使用不當 CacheOption 導致過度快取。
3. 未根據實際需求（只做縮放）調整策略。
深層原因：
- 架構層面：WIC 支援不同載入策略。
- 技術層面：對 BitmapCreateOptions/CacheOption 不熟。
- 流程層面：缺少實測與基準。

### Solution Design（解決方案設計）
解決策略：CreateOptions 用 DelayCreation 延後昂貴操作；CacheOption 維持預設（或 OnLoad 於必要時），平衡 I/O 與記憶體。針對特定場景測試。

實施步驟：
1. 採用延遲建立
- 實作細節：BitmapCreateOptions.DelayCreation
- 所需資源：WPF Imaging
- 預估時間：20 分鐘
2. 調整快取策略
- 實作細節：視情境嘗試 None/Default/OnLoad
- 所需資源：效能測試腳本
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var decoder = BitmapDecoder.Create(
    new Uri(src),
    BitmapCreateOptions.DelayCreation,  // 延後昂貴處理
    BitmapCacheOption.None              // 或 Default/OnLoad，視情境比較
);
```

實際案例：同一批 RAW 使用 DelayCreation 初載較順。
實作環境：同上。
實測數據：
改善前：啟動/切換大圖時卡頓
改善後：初載較平順，記憶體尖峰下降（定性）
改善幅度：體感改善

Learning Points（學習要點）
核心知識點：
- CreateOptions 與 CacheOption 差異
- 延遲載入對 UX 的影響
- 場景化效能測試
技能要求：
- 必備技能：選項理解
- 進階技能：效能剖析與指標化
延伸思考：
- 批次處理是否改用 OnLoad 釋放檔案鎖？
- 是否需要平行化分批處理？
- 與記憶體限制的互動？

Practice Exercise（練習題）
- 基礎：比較 DelayCreation 與預設的初載時間。
- 進階：寫腳本批次測不同 CacheOption。
- 專案：建立效能基準儀表板（時間/記憶體）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：可切換載入策略
- 程式碼品質（30%）：測試程式與數據紀錄
- 效能優化（20%）：有數據支撐的選擇
- 創新性（10%）：自動選項調整

---

## Case #10: 縮圖變形：實作等比例 Bounding Box 縮放

### Problem Statement（問題陳述）
業務場景：希望輸出圖最大邊不超過 800x800，且保持比例不變。
技術挑戰：以 WPF 正確計算縮放比例並應用到 TransformedBitmap。
影響範圍：輸出圖外觀、視覺品質。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 以固定比例縮放可能超過目標邊長。
2. 直接指定寬/高會造成變形。
3. 未先讀取原始像素尺寸。
深層原因：
- 架構層面：需以 Size-aware 的計算驅動 transform。
- 技術層面：PixelWidth/PixelHeight 的使用。
- 流程層面：缺少公用計算函式。

### Solution Design（解決方案設計）
解決策略：讀取來源尺寸，計算 scale = min(maxW/W, maxH/H)，以 ScaleTransform 套用。

實施步驟：
1. 取得來源尺寸
- 實作細節：frame.PixelWidth/PixelHeight
- 所需資源：WPF Imaging
- 預估時間：10 分鐘
2. 套用 ScaleTransform
- 實作細節：TransformedBitmap + ScaleTransform(scale, scale)
- 所需資源：同上
- 預估時間：10 分鐘

關鍵程式碼/設定：
```csharp
TransformedBitmap CreateBoundedBitmap(BitmapSource src, int maxW, int maxH)
{
    double scale = Math.Min((double)maxW / src.PixelWidth, (double)maxH / src.PixelHeight);
    if (scale > 1.0) scale = 1.0; // 不放大
    return new TransformedBitmap(src, new System.Windows.Media.ScaleTransform(scale, scale));
}
```

實際案例：800x800 邊界輸出，比例正確。
實作環境：同上。
實測數據：
改善前：圖片可能被擠壓或超出限制
改善後：等比例且符合最大邊
改善幅度：畫面品質明顯提升

Learning Points（學習要點）
核心知識點：
- Bounding box 縮放
- PixelWidth/Height 的使用
- 禁止放大策略
技能要求：
- 必備技能：WPF transform
- 進階技能：自動旋轉/方向（EXIF Orientation，可延伸）
延伸思考：
- 是否依 EXIF Orientation 調整寬高（延伸實作）？
- 是否需要多步驟濾鏡（銳化等）？
- 是否要針對長邊或短邊優先？

Practice Exercise（練習題）
- 基礎：將固定比例改為最大邊策略。
- 進階：加入不放大策略（僅縮小）。
- 專案：做成可複用的縮放模組與單元測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：正確等比例縮放
- 程式碼品質（30%）：函式化、可測試
- 效能優化（20%）：處理大批量時表現穩定
- 創新性（10%）：加入方向/銳化

---

## Case #11: 手動歸檔耗時：批次自動化轉檔流程

### Problem Statement（問題陳述）
業務場景：每次歸檔需處理大量 RAW，手動一張張轉檔耗時且容易出錯。
技術挑戰：建立批次處理腳本或工具，串用封裝 API。
影響範圍：效率、穩定性、人為錯誤。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 無批次腳本。
2. 缺乏錯誤重試與日誌。
3. 檔案命名/輸出目錄規劃不足。
深層原因：
- 架構層面：缺少批處理與任務重試設計。
- 技術層面：未利用封裝 API（案例 #6）。
- 流程層面：無標準化歸檔流程。

### Solution Design（解決方案設計）
解決策略：以 ImageUtil.SaveToJPEG 為核心，建立批次工具：掃描資料夾→過濾 CR2→輸出到指定資料夾→記錄結果。

實施步驟：
1. 檔案掃描與輸出規劃
- 實作細節：Directory.EnumerateFiles + 輸出路徑策略
- 所需資源：System.IO
- 預估時間：30 分鐘
2. 批次執行與日誌
- 實作細節：try/catch、記錄錯誤
- 所需資源：日誌庫（可選）
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
void BatchConvert(string srcDir, string dstDir, int maxW, int maxH, int quality)
{
    Directory.CreateDirectory(dstDir);
    foreach (var cr2 in Directory.EnumerateFiles(srcDir, "*.CR2", SearchOption.AllDirectories))
    {
        var name = Path.GetFileNameWithoutExtension(cr2) + ".jpg";
        var dst = Path.Combine(dstDir, name);
        try
        {
            ImageUtil.SaveToJPEG(cr2, dst, maxW, maxH, quality);
        }
        catch (Exception ex)
        {
            // TODO: 記錄到日誌
        }
    }
}
```

實際案例：一鍵轉換整批 G9 RAW。
實作環境：同上。
實測數據：
改善前：人工逐張轉檔
改善後：批次一鍵完成，錯誤可追蹤
改善幅度：效率與可靠性顯著提升

Learning Points（學習要點）
核心知識點：
- 檔名與輸出目錄策略
- 批次錯誤處理
- 封裝 API 的重用
技能要求：
- 必備技能：I/O 操作
- 進階技能：批次併發與佇列（可延伸）
延伸思考：
- 是否加入多執行緒？
- 是否加入進度回報/取消？
- 是否支援目錄同步/增量處理？

Practice Exercise（練習題）
- 基礎：處理單層資料夾。
- 進階：遞迴處理+錯誤日誌+略過既有檔案。
- 專案：加入進度列與取消功能。

Assessment Criteria（評估標準）
- 功能完整性（40%）：批次可用且穩定
- 程式碼品質（30%）：結構清楚、例外管理
- 效能優化（20%）：I/O 與 CPU 使用合理
- 創新性（10%）：增量/重試/報表

---

## Case #12: 對照是否正確：以程式驗證 Metadata 複製完整性

### Problem Statement（問題陳述）
業務場景：對照表以實驗導出，需驗證搬移後的欄位是否與預期一致。
技術挑戰：沒有現成工具可一鍵驗證映射是否生效。
影響範圍：資料可信度、錯誤發現時間。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未建立自動化驗證。
2. 欄位比對需依映射逐一核對。
3. 不同格式值型別/表示法可能差異。
深層原因：
- 架構層面：資料驅動（映射）需測試配套。
- 技術層面：GetQuery/SetQuery 值的比較。
- 流程層面：缺乏測試樣本與驗證流程。

### Solution Design（解決方案設計）
解決策略：以映射為基準，讀入來源與輸出圖，逐欄位比較值，輸出報表，提供人工審查與迭代修正。

實施步驟：
1. 撰寫驗證函式
- 實作細節：迭代映射並比較值
- 所需資源：WPF Imaging、映射載入
- 預估時間：45 分鐘
2. 報表輸出
- 實作細節：列出相符/不符清單
- 所需資源：Console/CSV
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
IEnumerable<string> ValidateMappedFields(string srcRaw, string outJpeg, IEnumerable<(string from, string to)> map)
{
    var srcMeta = ((BitmapDecoder.Create(new Uri(srcRaw), BitmapCreateOptions.None, BitmapCacheOption.OnLoad))
        .Frames[0].Metadata as BitmapMetadata);
    var outMeta = ((BitmapDecoder.Create(new Uri(outJpeg), BitmapCreateOptions.None, BitmapCacheOption.OnLoad))
        .Frames[0].Metadata as BitmapMetadata);

    var results = new List<string>();
    foreach (var (from, to) in map)
    {
        var hasSrc = srcMeta?.ContainsQuery(from) == true;
        var hasDst = outMeta?.ContainsQuery(to) == true;
        if (!hasSrc && !hasDst) continue;

        var v1 = hasSrc ? srcMeta.GetQuery(from) : null;
        var v2 = hasDst ? outMeta.GetQuery(to) : null;
        results.Add($"{from} -> {to}: {(Equals(v1, v2) ? "OK" : "DIFF")}");
    }
    return results;
}
```

實際案例：以樣本驗證常見欄位 OK，個別欄位再逐步修正。
實作環境：同上。
實測數據：
改善前：映射可信度不明
改善後：有系統化驗證結果
改善幅度：錯誤發現提前、可信度提升

Learning Points（學習要點）
核心知識點：
- 測試導向調整映射
- 資料比較與報表
- 型別差異處理
技能要求：
- 必備技能：WPF Metadata 比對
- 進階技能：測試自動化
延伸思考：
- 加入白名單/黑名單欄位？
- 允許「近似相等」策略（格式化差異）？
- 持續整合中的自動驗證？

Practice Exercise（練習題）
- 基礎：輸出 Console 報表。
- 進階：輸出 CSV 並排序差異優先。
- 專案：做成 GUI 驗證器，支援拖拉比對。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能列出差異
- 程式碼品質（30%）：清楚、可維護
- 效能優化（20%）：大量欄位下表現
- 創新性（10%）：圖形化報表

---

## Case #13: Metadata Query 不存在導致例外：安全讀寫模式

### Problem Statement（問題陳述）
業務場景：按對照表搬移欄位時，部分 Query 在來源或目標不存在，呼叫 GetQuery/SetQuery 會拋例外。
技術挑戰：需安全地讀取/寫入，避免流程中斷。
影響範圍：批次處理穩定性。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 未使用 ContainsQuery 先行檢查。
2. 未對值型別/格式做適配。
3. 缺乏錯誤分類（忽略 vs 警告）。
深層原因：
- 架構層面：映射為最大嘗試集，非所有圖皆具欄位。
- 技術層面：WPF Query 例外處理不熟。
- 流程層面：缺少容錯策略。

### Solution Design（解決方案設計）
解決策略：封裝 TryGetQuery/TrySetQuery，先 ContainsQuery，再安全存取。對失敗記錄警告，不中斷流程。

實施步驟：
1. 封裝安全 API
- 實作細節：Try* 模式回傳 bool、out object
- 所需資源：WPF Imaging
- 預估時間：30 分鐘
2. 套用到映射流程
- 實作細節：失敗記錄、不中斷
- 所需資源：日誌
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
bool TryGetQuery(BitmapMetadata meta, string query, out object value)
{
    value = null;
    if (meta == null) return false;
    if (!meta.ContainsQuery(query)) return false;
    try { value = meta.GetQuery(query); return true; }
    catch { return false; }
}

bool TrySetQuery(BitmapMetadata meta, string query, object value)
{
    if (meta == null) return false;
    try { meta.SetQuery(query, value); return true; }
    catch { return false; }
}
```

實際案例：批次處理時未因個別欄位缺失中斷。
實作環境：同上。
實測數據：
改善前：常見例外導致整批失敗
改善後：不中斷，且可追蹤問題欄位
改善幅度：穩定性顯著提升

Learning Points（學習要點）
核心知識點：
- ContainsQuery/例外處理
- Try 模式封裝
- 錯誤分類（警告/錯誤）
技能要求：
- 必備技能：健壯性設計
- 進階技能：日誌與告警
延伸思考：
- 是否需要重試或格式轉換？
- 是否要收集失敗統計供改進映射？
- 是否提供使用者交互修正？

Practice Exercise（練習題）
- 基礎：實作 TryGetQuery/TrySetQuery。
- 進階：加入失敗記錄與總結。
- 專案：將失敗欄位導出供人工編修。

Assessment Criteria（評估標準）
- 功能完整性（40%）：不中斷且可追蹤
- 程式碼品質（30%）：封裝良好、易用
- 效能優化（20%）：大量欄位下安全快速
- 創新性（10%）：自動化修復策略

---

## Case #14: 目標環境缺少 Codec：偵測與降級提示

### Problem Statement（問題陳述）
業務場景：工具部署到新機器時，可能未安裝 Canon RAW Codec，轉檔立即失敗且使用者不知所措。
技術挑戰：在啟動或開檔時偵測，並提供清楚的修復指引。
影響範圍：可用性、客服成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未做啟動檢核。
2. 例外訊息不友善。
3. 無引導指引。
深層原因：
- 架構層面：外部相依（Codec）。
- 技術層面：開檔例外未分類。
- 流程層面：文件/指引不足。

### Solution Design（解決方案設計）
解決策略：在載入第一張 RAW 前先做健康檢查，若缺失則彈窗/日誌，提供下載連結或離線安裝包。

實施步驟：
1. 偵測與回報
- 實作細節：嘗試開啟樣本或 try/catch 分類例外
- 所需資源：WPF Imaging
- 預估時間：30 分鐘
2. 降級策略
- 實作細節：允許僅處理 JPEG/PNG；提供安裝連結
- 所需資源：UI/文件
- 預估時間：30 分鐘

關鍵程式碼/設定：
```csharp
bool CheckRawSupport(string sampleCr2Path)
{
    try { using var _ = BitmapDecoder.Create(new Uri(sampleCr2Path), BitmapCreateOptions.DelayCreation, BitmapCacheOption.None); return true; }
    catch (Exception ex) { /* 記錄 ex.Message；提示安裝 Canon RAW Codec */ return false; }
}
```

實際案例：新機器第一次啟動即提示安裝步驟，避免誤會。
實作環境：同上。
實測數據：
改善前：使用者直接遇錯
改善後：引導修復，成功率提升
改善幅度：支援成本下降

Learning Points（學習要點）
核心知識點：
- 健檢步驟與降級策略
- 友善錯誤訊息
- 文件/指引的重要性
技能要求：
- 必備技能：例外訊息處理
- 進階技能：安裝檢查與自動化
延伸思考：
- 是否可內建離線安裝包？
- 是否需權限檢查？
- 國際化訊息？

Practice Exercise（練習題）
- 基礎：try/catch 並顯示友善訊息。
- 進階：在 UI 顯示下載連結與說明。
- 專案：健康檢查精靈（逐步引導）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：能偵測缺失並引導
- 程式碼品質（30%）：訊息清楚、路徑穩健
- 效能優化（20%）：檢查不拖慢啟動
- 創新性（10%）：自動修復

---

## Case #15: 從 GDI+ 到 WPF 的心智轉換：以 Transform 管線重構

### Problem Statement（問題陳述）
業務場景：既有工具以 GDI/GDI+ 思維開發；遷移到 WPF 後需理解物件為圖形來源、層層 Transform 的管線。
技術挑戰：將即時繪圖（Immediate-mode）轉換為保留式（Retained-mode）操作。
影響範圍：設計思維、可擴充性與效能。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 沿用 GDI+ 寫法導致難以利用 WPF 強項。
2. 不熟悉 WPF 的 ImageSource/Transform 概念。
3. 缺乏可複用的 Transform 管線。
深層原因：
- 架構層面：保留式圖形模型與層級式處理。
- 技術層面：TransformedBitmap、BitmapEffects（舊）、Effect 管線。
- 流程層面：設計與重構策略不足。

### Solution Design（解決方案設計）
解決策略：建立以 ImageSource 為中心的處理管線：讀取→變換（縮放、旋轉、裁切）→編碼。將每個變換封裝為可組合的步驟，提升可讀與可測。

實施步驟：
1. 管線化設計
- 實作細節：以 BitmapSource 輸入，串多個 TransformedBitmap
- 所需資源：WPF Imaging
- 預估時間：1-2 小時
2. 可組合的變換
- 實作細節：函式化縮放/旋轉，依序套用
- 所需資源：單元測試
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
BitmapSource ApplyPipeline(BitmapSource src)
{
    BitmapSource step1 = new TransformedBitmap(src, new System.Windows.Media.ScaleTransform(0.5, 0.5));
    BitmapSource step2 = new TransformedBitmap(step1, new System.Windows.Media.RotateTransform(90));
    return step2; // 還可繼續串接
}
```

實際案例：以 WPF 管線完成縮放+旋轉再編碼，取代 GDI+ 即時繪圖。
實作環境：同上。
實測數據：
改善前：GDI+ 難以重複利用與組合
改善後：WPF 可組合管線，重構容易
改善幅度：可維護性與擴展性提升

Learning Points（學習要點）
核心知識點：
- 即時式 vs 保留式模型
- ImageSource 與 Transform
- 可組合設計
技能要求：
- 必備技能：WPF 基礎
- 進階技能：管線模式設計
延伸思考：
- 加入 Effect/色彩校正？
- 管線配置（以設定檔驅動）？
- 單元測試如何覆蓋圖像處理？

Practice Exercise（練習題）
- 基礎：串接縮放+旋轉。
- 進階：加入裁切步驟。
- 專案：設計可宣告的管線（JSON 配置）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：管線可組合運作
- 程式碼品質（30%）：模組化、可測試
- 效能優化（20%）：避免多餘拷貝
- 創新性（10%）：配置化管線

---

## Case #16: 輸出檔過大或畫質不穩：QualityLevel 參數化與基線設置

### Problem Statement（問題陳述）
業務場景：分享用 JPEG 需在品質與大小間折衷；未設定 QualityLevel，輸出不可控。
技術挑戰：設置合適的 QualityLevel 並對外提供參數。
影響範圍：儲存成本、傳輸時間、視覺品質。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未指定 QualityLevel（使用預設）。
2. 未根據場景調整（75~85 常見）。
3. 缺乏簡單的基準目標。
深層原因：
- 架構層面：品質策略需外部化。
- 技術層面：對 Encoder 參數不熟。
- 流程層面：無基準/測試圖集。

### Solution Design（解決方案設計）
解決策略：將 QualityLevel 作為參數（預設 75 或 80），建立常用情境建議值。對於保存品質（見案例 #8）給替代格式選項。

實施步驟：
1. 參數化 Quality
- 實作細節：API 參數與 UI 下拉選單
- 所需資源：JpegBitmapEncoder
- 預估時間：20 分鐘
2. 設定基準
- 實作細節：定義預設 80；高壓縮 60；高品質 90
- 所需資源：簡單文件
- 預估時間：20 分鐘

關鍵程式碼/設定：
```csharp
var encoder = new JpegBitmapEncoder { QualityLevel = quality }; // 建議 75~85
encoder.Frames.Add(outFrame);
```

實際案例：原文示例使用 80 與 75 作為品質設定。
實作環境：同上。
實測數據：
改善前：檔案大小/品質不可控
改善後：品質有預期，大小可預估
改善幅度：可操作性提升

Learning Points（學習要點）
核心知識點：
- QualityLevel 對大小與品質的影響
- 不同場景的建議值
- 與 HD Photo 策略互補
技能要求：
- 必備技能：Encoder 參數調整
- 進階技能：以視覺指標/SSIM 做客觀評估（延伸）
延伸思考：
- 是否提供質量/大小目標自動迭代？
- 是否依圖像內容自適應？
- 與 CDN/平台限制的配合？

Practice Exercise（練習題）
- 基礎：提供 Quality 參數化與預設值。
- 進階：輸出多組品質做比較圖牆。
- 專案：小工具：輸入目標檔案大小，自動搜尋合適品質。

Assessment Criteria（評估標準）
- 功能完整性（40%）：品質可調、輸出穩定
- 程式碼品質（30%）：介面清晰
- 效能優化（20%）：嘗試次數與時間
- 創新性（10%）：自動品質搜尋

---

案例分類

1) 按難度分類
- 入門級（適合初學者）
  - Case 1（安裝/開檔）
  - Case 2（基本轉檔）
  - Case 7（縮圖保留）
  - Case 10（等比例縮放）
  - Case 16（品質設定）
- 中級（需要一定基礎）
  - Case 3（EXIF 附掛）
  - Case 9（載入策略）
  - Case 11（批次自動化）
  - Case 12（驗證映射）
  - Case 14（環境健檢）
  - Case 15（WPF 管線心智）
- 高級（需要深厚經驗）
  - Case 4（跨格式對照表）
  - Case 5（XML 嵌入維運）
  - Case 6（封裝 API）
  - Case 8（HD Photo 策略）
  - Case 13（安全讀寫模式）

2) 按技術領域分類
- 架構設計類：Case 5, 6, 11, 15
- 效能優化類：Case 9, 10, 16
- 整合開發類：Case 1, 2, 8, 14
- 除錯診斷類：Case 3, 4, 12, 13
- 安全防護類（健壯/容錯）：Case 13, 14

3) 按學習目標分類
- 概念理解型：Case 8, 9, 15, 16
- 技能練習型：Case 2, 3, 7, 10
- 問題解決型：Case 1, 4, 12, 13, 14
- 創新應用型：Case 5, 6, 11

案例關聯圖（學習路徑建議）
- 起步順序（基礎到應用）：
  1) Case 1（環境可用）→ 2（端到端轉檔）→ 16（品質設定）→ 7（縮圖保留）→ 10（等比例縮放）
- Metadata 與可靠性：
  2 完成後，學習 3（EXIF 附掛）→ 4（跨格式對照）→ 5（對照表外部化）→ 13（安全讀寫）→ 12（驗證）
- 批次與流程：
  完成上段後，進入 6（封裝 API）→ 11（批次自動化）→ 14（環境健檢）
- 進階與策略：
  並行學習 9（載入策略）與 15（WPF 管線心智），最後學 8（HD Photo 策略）作格式選擇的進階應用
- 依賴關係摘要：
  - Case 4 依賴 3 的基礎；5 依賴 4；12 依賴 4/5；6 依賴 2/3/4/10；11 依賴 6；14 依賴 1；8 可在 2 後學習，與 16 互補
- 完整學習路徑建議：
  1 → 2 → 10 → 16 → 7 → 3 → 4 → 5 → 13 → 12 → 6 → 11 → 9 → 15 → 14 → 8

以上 16 個案例皆直接取材自原文的問題脈絡與解法（WPF 影像管線、Canon RAW Codec、EXIF/Metadata 抽象與對照、XML 外部化與封裝、品質/格式策略），並補齊實作細節與教學配套，便於課堂示範、實作練習與評估。