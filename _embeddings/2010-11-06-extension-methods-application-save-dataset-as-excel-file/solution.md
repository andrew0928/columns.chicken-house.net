以下內容基於原文，將具教學價值的問題解決點梳理為 18 個可實作的案例，皆包含問題、根因、解法、關鍵程式碼與練習與評估項，便於實戰教學、專案演練與能力評估。

## Case #1: 用 Extension Methods 讓 DataSet 直接讀寫 Excel（替代 XML）

### Problem Statement（問題陳述）
業務場景：團隊的處理流程以 DataSet 為核心，資料來源與輸出本應是 Excel，但 POC 階段以 DataSet 原生 XML 代替。內部處理雖可運作，但對外交付時，要求可讓使用者直接在 Excel 中檢視與編輯。希望在不破壞現有 DataSet 為核心的架構下，讓程式碼語意清晰地表達「讀 Excel、處理、寫 Excel」，且不引入過多樣板或侵入性改動。
技術挑戰：DataSet 缺少 ReadExcel/WriteExcel；不可改動 DataSet 原型且不便繼承；需有簡潔語法。
影響範圍：可維持既有處理邏輯，提升程式可讀性與交付價值；若處理不當會造成維護困難與使用者體驗不佳。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. DataSet 沒有內建 Excel I/O 方法，只支援 XML 讀寫。
2. 使用者不易編輯 XML，導致交付體驗差。
3. 繼承 DataSet 不方便（與 Typed DataSet 生成衝突）。
深層原因：
- 架構層面：資料處理流程強耦合 DataSet，但未抽象 I/O。
- 技術層面：缺乏可直觀使用的 Excel I/O API。
- 流程層面：POC 階段以 XML 快速替代，但未規劃回到 Excel 的交付面。

### Solution Design（解決方案設計）
解決策略：以 C# Extension Methods 為 DataSet 附加 ReadExcel/WriteExcel 簽名，內部實作採 NPOI 完成工作簿/工作表輸出；在不修改核心處理邏輯的前提下，讓調用端語意簡潔。先落地 WriteExcel（輸出），讀取可先沿用 ReadXml 或以其他 FAQ 方案補齊。

實施步驟：
1. 建立擴充類別 NPOIExtension
- 實作細節：宣告 public static class，方法第一參數宣告 this DataSet。
- 所需資源：.NET 3.x+，NPOI。
- 預估時間：0.5 小時。
2. 實作 WriteExcel 對應 DataSet→Workbook 映射
- 實作細節：DataTable→Sheet，Columns→Header，Rows→Cell；處理檔案覆寫。
- 所需資源：NPOI HSSFWorkbook。
- 預估時間：1.5 小時。
3. 串接至既有流程
- 實作細節：保持 ds.ReadXml → ds.WriteExcel 流程，替代輸出端。
- 所需資源：現有專案。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public static class NPOIExtension
{
    public static void WriteExcel(this DataSet context, string outputFile)
    {
        var workbook = new HSSFWorkbook();
        foreach (DataTable table in context.Tables)
        {
            var sheet = workbook.CreateSheet(table.TableName);
            var header = sheet.CreateRow(0);
            for (int c = 0; c < table.Columns.Count; c++)
            {
                var cell = header.CreateCell(c);
                cell.SetCellType(CellType.STRING);
                cell.SetCellValue(table.Columns[c].ColumnName);
            }
            int rpos = 1;
            foreach (DataRow row in table.Rows)
            {
                var r = sheet.CreateRow(rpos++);
                for (int c = 0; c < table.Columns.Count; c++)
                {
                    var cell = r.CreateCell(c);
                    var v = row[c];
                    cell.SetCellValue(v == null || v == DBNull.Value ? "" : v.ToString());
                }
            }
        }
        if (File.Exists(outputFile)) File.Delete(outputFile);
        using (var fs = File.OpenWrite(outputFile)) workbook.Write(fs);
    }
}
```

實際案例：作者以 WriteExcel 實作 DataSet XML→Excel 轉檔，成功交付單檔轉換。
實作環境：.NET 3.x（支援 Extension Methods）、NPOI、HSSFWorkbook（.xls）。
實測數據：
改善前：輸出 XML，客戶不易編輯。
改善後：輸出 .xls，可直接編輯。
改善幅度：可用性與可溝通性顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- Extension Methods 語法與限制
- DataSet→Excel 的結構映射
- NPOI 基本 API 使用
技能要求：
- 必備技能：C#、DataSet、檔案 I/O
- 進階技能：NPOI 物件模型、格式化
延伸思考：
- 如何加入 ReadExcel？
- 如何支援 xlsx？
- 如何保留型別與格式？
Practice Exercise（練習題）
- 基礎練習：為 DataSet 增加 WriteExcel 並輸出一個簡單表。
- 進階練習：支援多 DataTable 多 Sheet 與檔案覆寫保護。
- 專案練習：封裝 NuGet 套件，提供讀/寫與選項設定。
Assessment Criteria（評估標準）
- 功能完整性（40%）：能輸出含標題與資料的 .xls
- 程式碼品質（30%）：擴充方法結構清晰、命名恰當
- 效能優化（20%）：輸出時機與 I/O 使用合理
- 創新性（10%）：API 設計貼近使用者語意

---

## Case #2: 無需繼承 DataSet：以擴充方法解決 Typed DataSet 相容性

### Problem Statement（問題陳述）
業務場景：系統有兩類 DataSet 使用方式：直接使用 System.Data.DataSet，以及搭配 XSD 由 Visual Studio 產生的 Typed DataSet。因不同專案、模組、第三方整合而存在多樣 DataSet 實作，若以自訂衍生類封裝 Excel I/O，勢必造成泛用性低且導入成本高。希望能一處實作，處處可用。
技術挑戰：Typed DataSet 是工具生成類別，替換成自訂子類不便；組態異質，需低侵入性方案。
影響範圍：擴展失敗會造成多版本維護、重複碼與風險提高。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Typed DataSet 由工具生成，無法輕易改為繼承樹狀結構。
2. 現有模組均以 DataSet 為共通介面，難以替換型別。
3. 需求僅為加方法，不需改動內部狀態。
深層原因：
- 架構層面：核心模型耦合 DataSet 且已經廣泛傳播。
- 技術層面：繼承會破壞相容性；不適合侵入式改造。
- 流程層面：多團隊協作下難以做大規模重構。

### Solution Design（解決方案設計）
解決策略：使用 Extension Methods 在不修改與不繼承的前提下，為 DataSet 與其子類（含 Typed DataSet）提供一致 API。這是編譯器語法糖，呼叫點看似成員方法，但實則靜態方法調用，零侵入、易於替換。

實施步驟：
1. 定義單一擴充類與命名空間
- 實作細節：public static class，方法簽名 this DataSet。
- 所需資源：.NET 3.x+。
- 預估時間：0.5 小時。
2. 分層命名與相依注入
- 實作細節：將 Excel 具體實作放入內部服務以利測試。
- 所需資源：介面/小型 DI。
- 預估時間：1 小時。
3. 導入專案
- 實作細節：using 擴充命名空間，原碼無須改型別。
- 所需資源：專案調整。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
namespace MyCompany.DataSet.Excel
{
    public static class DataSetExcelExtensions
    {
        public static void WriteExcel(this DataSet ds, string path) { /* NPOI 實作 */ }
        public static void ReadExcel(this DataSet ds, string path) { /* 另案/FAQ 實作 */ }
    }
}
```

實際案例：作者拒絕繼承方案，改採 Extension Methods，成功覆蓋所有 DataSet 使用情境。
實作環境：.NET 3.x、C# 3.0、任一 DataSet 變體。
實測數據：
改善前：需為不同 DataSet 寫多套 I/O。
改善後：單一擴充對外 API。
改善幅度：維護成本顯著下降（定性）。

Learning Points（學習要點）
- Extension Methods 在相容性改造的價值
- 工具生成類型與繼承的衝突
- 零侵入 API 設計
技能要求：
- 必備：C# 語法、.NET 型別系統
- 進階：API 設計、命名空間與可發現性設計
延伸思考：
- 如何避免命名衝突？
- 如何設計過載與選項？
- 是否需提供非擴充的替代 API？
Practice Exercise
- 基礎：新增一個擴充方法 ToCsv(this DataSet)。
- 進階：為 Typed DataSet 驗證擴充可用性與單元測試。
- 專案：設計一套可發現性高的擴充 API 規範與範本。
Assessment Criteria
- 功能完整性（40%）：擴充 API 覆蓋面
- 程式碼品質（30%）：命名與可讀性
- 效能（20%）：零額外裝箱與過度配置
- 創新（10%）：API 易用性

---

## Case #3: 用擴充方法提升可讀性：消除 Helper 類的噪音

### Problem Statement（問題陳述）
業務場景：維護人員回看舊程式碼，常被靜態 Helper 類與多層呼叫干擾，難以一眼理解「這段在做什麼」。對外釋出的樣板也偏冗長，降低團隊溝通效率。希望讓核心流程呈現「讀→處理→存」的語意，視覺上清晰且最少干擾。
技術挑戰：以不改變邏輯的方式改善語意；避免過多樣板代碼。
影響範圍：閱讀與維護效率、上手成本、溝通成本。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 靜態 Helper 調用噪音大，掩蓋意圖。
2. 程式碼缺少語意化 API。
3. 過度樣板代碼分散注意力。
深層原因：
- 架構層面：缺少語意層 API。
- 技術層面：未運用語法糖改善可讀性。
- 流程層面：未規範可讀性與樣式標準。

### Solution Design（解決方案設計）
解決策略：將常用的資料 I/O 操作以擴充方法表達為語意動詞（ReadExcel/WriteExcel），讓主流程只保留關鍵三行；將細節封裝在擴充方法內部，必要時提供文件與 IntelliSense 註解。

實施步驟：
1. 設計語意一致的命名
- 實作細節：動詞化、對稱化命名（Read*/Write*）。
- 所需資源：團隊命名規範。
- 預估時間：0.5 小時。
2. 實作擴充與文件註解
- 實作細節：XML doc，示例片段。
- 所需資源：IDE/編輯器。
- 預估時間：1 小時。
3. 導入程式碼樣式
- 實作細節：守則檔、PR 規範。
- 所需資源：lint/分析工具。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
DataSet ds = new DataSet();
ds.ReadExcel("in.xls");    // 語意清楚：讀取 Excel
// do something
ds.WriteExcel("out.xls");  // 語意清楚：寫出 Excel
```

實際案例：作者由 ReadXml/WriteXml 改為 ReadExcel/WriteExcel，回頭閱讀時一眼看懂。
實作環境：.NET 3.x、NPOI。
實測數據：
改善前：主流程充斥 Helper 類干擾。
改善後：主流程三行呈現意圖。
改善幅度：可讀性顯著提升（定性）。

Learning Points
- 語意化 API 設計
- 擴充方法與程式碼美學
- 文件與 IntelliSense 協作
技能要求：
- 必備：命名、API 設計
- 進階：文件生成、樣式規範
延伸思考：
- 何時不應使用擴充方法？
- 如何避免過度魔法？
- 如何保持 API 對稱與一致性？
Practice Exercise
- 基礎：為 Stream 增加 ReadAllText/WriteAllText 擴充。
- 進階：為 DataTable 設計 ToSheet/FromSheet 擴充與測試。
- 專案：撰寫 API 設計指南，涵蓋命名、對稱性與實作範例。
Assessment Criteria
- 功能（40%）：API 可用性
- 品質（30%）：可讀性與一致性
- 效能（20%）：無過度包裝
- 創新（10%）：介面友善度

---

## Case #4: DataSet→Workbook 映射策略：多表對應多工作表輸出

### Problem Statement（問題陳述）
業務場景：單一 DataSet 常包含多個 DataTable（像多個報表頁），需輸出為單一 Excel 檔中的多個 Sheet，表頭需對應欄位，資料列逐列輸出。希望有一致且簡單的映射策略，讓任何 DataSet 都能一致輸出，作為通用工具。
技術挑戰：正確映射 DataSet 結構至 Excel 結構；處理表頭、資料、列號與欄位位置。
影響範圍：輸出檔正確性、相容性與未來維護成本。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 缺乏標準映射策略造成輸出不一致。
2. Excel 工作簿/工作表結構與 DataSet 結構不同。
3. 忽略表頭與資料分界導致資料錯位。
深層原因：
- 架構層面：未沉澱通用映射規約。
- 技術層面：未熟悉 NPOI 的物件模型。
- 流程層面：缺少一致化工具。

### Solution Design（解決方案設計）
解決策略：將「一 DataSet→一 Workbook；一 DataTable→一 Sheet；DataColumn→第一列表頭；DataRow→資料列；欄位索引→儲存格索引」定為標準；以迴圈實作，確保暫無樣式即能可靠輸出。

實施步驟：
1. 訂立映射規約
- 實作細節：文件化規約，避免分歧。
- 所需資源：文件庫。
- 預估時間：0.5 小時。
2. 編碼實作與封裝
- 實作細節：雙層迴圈（表→列→欄）。
- 所需資源：NPOI。
- 預估時間：1 小時。
3. 加入最小驗證
- 實作細節：空表處理、名稱去除非法字元。
- 所需資源：單元測試。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
foreach (DataTable table in ds.Tables)
{
    var sheet = wb.CreateSheet(table.TableName);
    var header = sheet.CreateRow(0);
    for (int c = 0; c < table.Columns.Count; c++)
        header.CreateCell(c).SetCellValue(table.Columns[c].ColumnName);

    for (int r = 0; r < table.Rows.Count; r++)
    {
        var row = sheet.CreateRow(r + 1);
        for (int c = 0; c < table.Columns.Count; c++)
            row.CreateCell(c).SetCellValue(Convert.ToString(table.Rows[r][c] ?? ""));
    }
}
```

實際案例：作者採此規則完成轉檔工具，正確輸出多表多頁。
實作環境：.NET、NPOI HSSF。
實測數據：
改善前：無標準輸出規則。
改善後：一套規則通用輸出。
改善幅度：錯位與遺漏問題顯著降低（定性）。

Learning Points
- 結構映射設計
- NPOI 基本迴圈輸出
- 偏移量（header 導致 r+1）
技能要求：
- 必備：DataSet 結構、NPOI API
- 進階：驗證與防呆
延伸思考：
- 如何支援樣式與寬度自動調整？
- 表名過長或重複的處理？
- 大資料量分頁策略？
Practice Exercise
- 基礎：把兩個 DataTable 輸出為兩個 Sheet。
- 進階：處理重複表名與自動加序號。
- 專案：做一個可設定映射規則的匯出庫。
Assessment Criteria
- 功能（40%）：正確輸出多 Sheet
- 品質（30%）：代碼清晰
- 效能（20%）：迴圈效率
- 創新（10%）：規則可設定性

---

## Case #5: 產生表頭列：以 DataColumn 名稱輸出標題

### Problem Statement（問題陳述）
業務場景：輸出報表時需要清楚的欄位標題，否則 Excel 檔可讀性差且無法由使用者直接判讀。希望自動以 DataColumn 名稱做為第一列表頭，避免手動維護標題清單。
技術挑戰：在迴圈中插入表頭，處理欄位順序與型別顯示。
影響範圍：輸出檔的可讀性與使用體驗。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 未輸出表頭導致理解困難。
2. 手動維護標題易出錯。
3. 欄位順序若被打亂會造成困惑。
深層原因：
- 架構層面：缺少一致的表頭策略。
- 技術層面：未標示 header 列的偏移。
- 流程層面：無自動化與測試覆蓋。

### Solution Design（解決方案設計）
解決策略：建立 headerRow = sheet.CreateRow(0)，以 DataColumn 次序逐一建立 Cell 並填入 ColumnName；資料列自 r+1 開始，確保表頭穩定對位。

實施步驟：
1. 插入表頭列
- 實作細節：Row 0 專用，欄位以 Columns 序列。
- 所需資源：NPOI。
- 預估時間：0.5 小時。
2. 單元測試驗證
- 實作細節：比對第一列值與 DataColumn 名稱。
- 所需資源：測試框架。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
var header = sheet.CreateRow(0);
for (int c = 0; c < table.Columns.Count; c++)
    header.CreateCell(c).SetCellValue(table.Columns[c].ColumnName);
```

實際案例：作者於示例程式中產生表頭，提升可讀性。
實作環境：.NET、NPOI。
實測數據：
改善前：無標頭。
改善後：自動表頭。
改善幅度：可讀性提升（定性）。

Learning Points
- Header 偏移與序列一致性
- 自動化與去樣板
技能要求：
- 必備：NPOI Cell/Row API
- 進階：國際化標題與映射
延伸思考：
- 需否提供自定義標題映射表？
- 表頭樣式（加粗、底色）？
Practice Exercise
- 基礎：為單表輸出標頭。
- 進階：提供欄位顯示名對照表。
- 專案：可配置的表頭樣式引擎。
Assessment Criteria
- 功能（40%）：表頭正確
- 品質（30%）：簡潔穩定
- 效能（20%）：無冗餘
- 創新（10%）：樣式化能力

---

## Case #6: Null 與 DBNull 安全處理，避免 Excel 出現空值異常

### Problem Statement（問題陳述）
業務場景：資料來源常含 Null/DBNull，若未處理，輸出 Excel 可能出現 "null" 字串、不正確值或引發例外。需保證匯出安全與一致空值策略（空字串或留空）。
技術挑戰：辨識 DBNull.Value 與 null，避免 SetCellValue 例外。
影響範圍：資料品質、使用者信任度、後續分析錯誤。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. DataRow 欄位可能是 DBNull.Value。
2. 直接 ToString() 對 DBNull 會回 "System.DBNull".
3. NPOI 對 Null 處理需顯式。
深層原因：
- 架構層面：缺少空值策略。
- 技術層面：未處理 DBNull 與 null 差異。
- 流程層面：缺乏測試樣本覆蓋空值。

### Solution Design（解決方案設計）
解決策略：統一判斷 v == null || v == DBNull.Value 時以空字串輸出；後續若要保型別，再延伸為型別映射策略。

實施步驟：
1. 封裝 Null 處理函式
- 實作細節：object→string 的安全轉換。
- 所需資源：共用工具。
- 預估時間：0.5 小時。
2. 導入至迴圈輸出
- 實作細節：所有 SetCellValue 前先轉換。
- 所需資源：現有方法。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
string SafeString(object v) => (v == null || v == DBNull.Value) ? "" : v.ToString();
// 使用
cell.SetCellValue(SafeString(row[c]));
```

實際案例：作者示例中已處理 null→空字串策略。
實作環境：.NET、NPOI。
實測數據：
改善前：有機會出現 DBNull 文字或例外。
改善後：統一空字串。
改善幅度：穩定性提升（定性）。

Learning Points
- DBNull vs null 差異
- 一致空值策略
技能要求：
- 必備：C# 空值處理
- 進階：型別安全轉換
延伸思考：
- 是否需輸出為真正空白儲存格（非空字串）？
- 空值對數值/日期的影響？
Practice Exercise
- 基礎：撰寫 SafeString。
- 進階：提供 SafeValue，支援多型別。
- 專案：建立資料清洗管線前置於輸出。
Assessment Criteria
- 功能（40%）：空值不例外
- 品質（30%）：易用且集中
- 效能（20%）：無多餘處理
- 創新（10%）：多型別支援

---

## Case #7: 避免 COM Automation 效能瓶頸：改用 NPOI 伺服器端輸出

### Problem Statement（問題陳述）
業務場景：原採用 Excel COM Automation（以程式操控 Excel）輸出報表。單機桌面可運作，但在 Web/Server 場景中，同時 5 人觸發功能時伺服器即明顯卡頓甚至停擺。需改以伺服器友好的方式輸出 Excel，不依賴 Office 安裝。
技術挑戰：替換實作而不改變對外行為，確保相容性與效能。
影響範圍：伺服器穩定度、可擴展性、併發能力。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. COM Automation 等同於在伺服器啟動 Excel 進程，資源極重。
2. Office 並非設計用於伺服器自動化。
3. 併發時進程數暴增，鎖死/權限問題頻發。
深層原因：
- 架構層面：錯誤選型，把桌面技術搬到伺服器。
- 技術層面：缺乏無 Office 依賴的輸出庫。
- 流程層面：未做併發/負載測試。

### Solution Design（解決方案設計）
解決策略：改用純 .NET 的 NPOI 實作 Excel BIFF（.xls）或 XSSF（.xlsx），避免任何 Office 進程與 COM。以擴充方法封裝，替換點最小化。

實施步驟：
1. 封裝 Excel 輸出層
- 實作細節：以接口+擴充方法包裝實作。
- 所需資源：NPOI。
- 預估時間：1.5 小時。
2. 負載測試
- 實作細節：JMeter/Locust 模擬 10～100 併發。
- 所需資源：測試工具。
- 預估時間：2 小時。
3. 部署驗證
- 實作細節：無 Office 伺服器環境驗證。
- 所需資源：測試環境。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 以 NPOI 取代 COM：無需安裝 Office
var wb = new HSSFWorkbook(); // 或 XSSFWorkbook for .xlsx
// 建立 Sheet/Row/Cell 如前述，最後寫入 FileStream
```

實際案例：作者指出 COM 伺服器端效能不佳，改用 NPOI 成功。
實作環境：Windows Server，不安裝 Office。
實測數據：
改善前：同時 5 人即可能跑不動（原文描述）。
改善後：純程式庫輸出，併發可明顯提升（依硬體與實作）。
改善幅度：伺服器穩定性顯著提升（定性）。

Learning Points
- 伺服器端選型原則
- 避免 Office COM 的常識
- 無依賴程式庫優勢
技能要求：
- 必備：.NET I/O、NPOI
- 進階：負載測試、併發調優
延伸思考：
- 大檔案記憶體壓力與串流化
- .xlsx 與 .xls 的選擇
Practice Exercise
- 基礎：以 NPOI 替換一段 COM 匯出。
- 進階：加入 JMeter 測試 50 併發。
- 專案：封裝服務並提供非同步匯出 API。
Assessment Criteria
- 功能（40%）：無 Office 依賴成功輸出
- 品質（30%）：封裝良好可替換
- 效能（20%）：併發測試通過
- 創新（10%）：非同步/串流設計

---

## Case #8: 規避 Jet ODBC/OLEDB 在 x64 的缺口：選擇 NPOI/OpenXML

### Problem Statement（問題陳述）
業務場景：有團隊以 Jet ODBC/OLEDB 將 Excel 當資料庫操作，於 Windows Server 2008 R2（含後續 x64-only 環境）部署時無法運作，因缺少 x64 Jet Driver。需選擇不依賴 Jet 的方案。
技術挑戰：確保在 x64 環境可運作且具長期支持。
影響範圍：部署成功率、平台相容性、維運風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. Jet Driver 無 x64 版本（原文指出）。
2. OS 新版多為 x64-only。
3. 透過 ODBC/OLEDB 僅能當資料庫存取，功能有限。
深層原因：
- 架構層面：錯誤依賴未來不可用的元件。
- 技術層面：方案受制於驅動支援。
- 流程層面：未進行部署環境風險評估。

### Solution Design（解決方案設計）
解決策略：改採不依賴 Jet 的 NPOI 或 Open XML SDK；若僅需讀/寫資料格，NPOI 是一致方案，若重視 .xlsx 與 Open XML 生態，採 Open XML SDK。

實施步驟：
1. 選型評估
- 實作細節：功能需求（公式/樣式/格式）、檔版型（xls/xlsx）。
- 所需資源：PoC。
- 預估時間：1 小時。
2. 替換實作
- 實作細節：將 OLEDB 呼叫改為 NPOI/OpenXML。
- 所需資源：程式庫、測試資料。
- 預估時間：2 小時。
3. 部署驗證
- 實作細節：x64 環境煙囪測試。
- 所需資源：x64 伺服器。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
// 以 NPOI 讀寫，完全不依賴 ODBC/OLEDB 驅動
using NPOI.HSSF.UserModel; // .xls
using NPOI.XSSF.UserModel; // .xlsx (若選)
```

實際案例：原文指出 Jet 無 x64，建議選 NPOI/Koogra/OpenXML。
實作環境：x64 Windows Server。
實測數據：
改善前：x64 無法部署。
改善後：無驅動依賴，可部署。
改善幅度：平台相容性大幅提升。

Learning Points
- 部署環境與驅動依賴
- 長期維護的選型觀
技能要求：
- 必備：平台與架構評估
- 進階：替代方案 PoC
延伸思考：
- Linux/.NET Core 環境的相容性？
- 容器化部署的檔案系統權限？
Practice Exercise
- 基礎：把 OLEDB 讀 Excel 改為 NPOI。
- 進階：支援 .xls/.xlsx 同時讀寫。
- 專案：寫一份部署相容性清單與自動檢查腳本。
Assessment Criteria
- 功能（40%）：替換成功
- 品質（30%）：清晰的選型文件
- 效能（20%）：無顯著退化
- 創新（10%）：自動化檢查

---

## Case #9: 以 HTML 匯出作為快速替代方案

### Problem Statement（問題陳述）
業務場景：在功能簡單、趕交付的情況下，只需將資料貼到 Excel 供使用者下載，不需要公式/格式/多 Sheet。需最快速的方法讓瀏覽器以 Excel 開啟下載。
技術挑戰：用最小成本產生可被 Excel 開啟的輸出。
影響範圍：開發速度、功能邊界、使用期望管理。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 實際需求僅為表格資料。
2. Excel 能開啟 HTML table。
3. 標準 Excel 功能（公式/多 Sheet）不在需求內。
深層原因：
- 架構層面：小功能不需大成本。
- 技術層面：利用 Excel 對 HTML 的容忍度。
- 流程層面：交付時程壓力大。

### Solution Design（解決方案設計）
解決策略：輸出 HTML table，HTTP Header 設為 application/vnd.ms-excel 或使用 .xls 副檔名，讓瀏覽器呼叫 Excel 開啟。明確告知限制。

實施步驟：
1. 生成 HTML table
- 實作細節：thead/tbody 正確結構。
- 所需資源：字串產生器或 Razor。
- 預估時間：0.5 小時。
2. 設定 Content-Type/Disposition
- 實作細節：attachment; filename=xxx.xls。
- 所需資源：Web 框架。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
Response.ContentType = "application/vnd.ms-excel";
Response.AddHeader("Content-Disposition", "attachment;filename=export.xls");
Response.Write("<table><tr><th>A</th></tr><tr><td>1</td></tr></table>");
```

實際案例：原文將此法列為快速但掌控度低的方案。
實作環境：ASP.NET。
實測數據：
改善前：無法快速交付。
改善後：快速可被 Excel 開啟。
改善幅度：交付速度大幅提升（功能有限）。

Learning Points
- Content-Type/Disposition 控制下載
- 快速替代方案的限制
技能要求：
- 必備：HTTP/HTML
- 進階：字元編碼與地區設定
延伸思考：
- 大資料量時的記憶體消耗？
- 如何引導使用者期望？
Practice Exercise
- 基礎：輸出簡單 HTML table 讓 Excel 開啟。
- 進階：加入樣式控制列寬。
- 專案：封裝為一鍵匯出元件。
Assessment Criteria
- 功能（40%）：可在 Excel 開啟
- 品質（30%）：HTML 正確
- 效能（20%）：輸出流暢
- 創新（10%）：易用介面

---

## Case #10: 採用 Open XML SDK 直寫 .xlsx 的策略

### Problem Statement（問題陳述）
業務場景：目標平台主要使用 Office 2007+，要求產出 .xlsx，且希望不依賴舊版 BIFF 格式或第三方庫。開發團隊熟悉 XML，可接受學習曲線。
技術挑戰：理解 Open XML 結構（Parts、Relationships、SharedStrings、Styles）。
影響範圍：功能深度、學習成本、長期維護。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. .xlsx 為 Open XML 格式。
2. 直接輸出需掌握 schema。
3. 相較 NPOI，學習曲線較陡。
深層原因：
- 架構層面：希望依賴官方 SDK。
- 技術層面：XML/打包格式複雜。
- 流程層面：需時間投資學習。

### Solution Design（解決方案設計）
解決策略：使用 Open XML SDK 2.x，建立 WorkbookPart/WorksheetPart，寫入 SheetData 與 SharedStringTable；封裝為擴充方法供 DataSet 調用。

實施步驟：
1. 建立檔案與主要部件
- 實作細節：SpreadsheetDocument.Create，WorkbookPart。
- 所需資源：Open XML SDK。
- 預估時間：2 小時。
2. 寫入 Sheet 與資料
- 實作細節：sheetData.Append(Row/Cell)；SharedStrings。
- 所需資源：SDK。
- 預估時間：2 小時。
3. 封裝為擴充方法
- 實作細節：DataSet→多 Worksheet。
- 所需資源：現有架構。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
using (var doc = SpreadsheetDocument.Create(path, SpreadsheetDocumentType.Workbook))
{
    var wbPart = doc.AddWorkbookPart(); wbPart.Workbook = new Workbook();
    var wsPart = wbPart.AddNewPart<WorksheetPart>(); wsPart.Worksheet = new Worksheet(new SheetData());
    var sheets = wbPart.Workbook.AppendChild(new Sheets());
    sheets.Append(new Sheet { Id = wbPart.GetIdOfPart(wsPart), SheetId = 1, Name = "Sheet1" });
    // 寫入 rows/cells 至 wsPart.Worksheet.SheetData
    wbPart.Workbook.Save();
}
```

實際案例：原文提供 OpenXML 參考與 SDK 連結。
實作環境：.NET、Open XML SDK 2.x。
實測數據：
改善前：無 .xlsx 直寫方案。
改善後：純 SDK 直寫 .xlsx。
改善幅度：相容性與可控性提升（學習成本高）。

Learning Points
- Open XML 結構
- SharedStrings 與樣式
技能要求：
- 必備：XML、.NET
- 進階：Open XML 深入
延伸思考：
- 大檔案的串流與壓縮
- 與 NPOI 的取捨
Practice Exercise
- 基礎：用 SDK 產出一張簡單表。
- 進階：加入 SharedStrings 與樣式。
- 專案：完成 DataSet→.xlsx 匯出擴充。
Assessment Criteria
- 功能（40%）：成功開啟 .xlsx
- 品質（30%）：結構正確
- 效能（20%）：合理效能
- 創新（10%）：樣式/公式

---

## Case #11: NPOI 與 Koogra 的選型與相容性權衡

### Problem Statement（問題陳述）
業務場景：需在不安裝 Office 的環境處理 Excel，考量 .xls/.xlsx 相容性、社群活躍度、API 易用性。NPOI 與 Koogra 都在選項中。
技術挑戰：不同庫對格式與功能支援不完全一致。
影響範圍：長期維護、功能可達性、Bug 修復速度。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多庫並存且支援度各異。
2. 團隊技術棧與使用習慣不同。
3. 版本與社群活躍度影響問題處理。
深層原因：
- 架構層面：需可替換的抽象層。
- 技術層面：格式支援差異。
- 流程層面：缺選型決策依據。

### Solution Design（解決方案設計）
解決策略：評估需求（xls/xlsx/公式/樣式/效能），以抽象介面包裝 Excel 服務，具體實作可以切換 NPOI 或 Koogra；先以社群更活躍、文件較完整的 NPOI 作為預設。

實施步驟：
1. 定義 IExcelExporter 介面
- 實作細節：Export(DataSet, path)。
- 所需資源：設計介面。
- 預估時間：0.5 小時。
2. 提供 NPOI/Koogra 實作
- 實作細節：兩個類各自實作。
- 所需資源：兩套庫。
- 預估時間：2 小時。
3. 擴充方法適配
- 實作細節：WriteExcel 呼叫預設實作。
- 所需資源：現有擴充。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public interface IExcelExporter { void Export(DataSet ds, string path); }
public class NpoiExporter : IExcelExporter { /* 使用 NPOI */ }
public static class DataSetExcelExt {
    public static void WriteExcel(this DataSet ds, string path, IExcelExporter exporter = null)
        => (exporter ?? new NpoiExporter()).Export(ds, path);
}
```

實際案例：原文同列 NPOI 與 Koogra 作為第三方庫。
實作環境：.NET。
實測數據：
改善前：選型不明確。
改善後：介面抽象可替換。
改善幅度：風險可控（定性）。

Learning Points
- 可替換設計
- 選型評估表
技能要求：
- 必備：介面設計
- 進階：可插拔架構
延伸思考：
- 以 DI/工廠決定實作？
- 以設定檔切換？
Practice Exercise
- 基礎：實作 NpoiExporter。
- 進階：新增 KoograExporter。
- 專案：設計選型與切換策略文件。
Assessment Criteria
- 功能（40%）：兩實作皆可用
- 品質（30%）：抽象清晰
- 效能（20%）：無明顯差異
- 創新（10%）：動態切換

---

## Case #12: POC 階段：以 DataSet XML 替代讀 Excel，仍可輸出 Excel

### Problem Statement（問題陳述）
業務場景：POC 階段時間有限，資料來源原為 Excel，但暫以 DataSet.ReadXml 讀入。仍需讓使用者得到 Excel 成果檔驗證。需最小改動完成「XML→處理→Excel」流程。
技術挑戰：快節奏下控制風險與交付品質。
影響範圍：驗證效率、需求確認速度。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 讀 Excel 實作耗時且多選項。
2. POC 需快，先用 XML 代替。
3. 仍須輸出 Excel 讓客戶檢視。
深層原因：
- 架構層面：I/O 層可替換性不足。
- 技術層面：Excel 讀入多種方案難抉擇。
- 流程層面：POC 以速度優先。

### Solution Design（解決方案設計）
解決策略：維持 ReadXml，新增 WriteExcel 擴充；先完成輸出端，確保客戶可驗證；待 POC 通過再補讀 Excel 實作。

實施步驟：
1. 寫輸出端擴充
- 實作細節：WriteExcel 完成（見 Case #1）。
- 所需資源：NPOI。
- 預估時間：2 小時。
2. 補回讀入端
- 實作細節：ReadExcel 於後續版本加入。
- 所需資源：選型與實作。
- 預估時間：後續安排。

關鍵程式碼/設定：
```csharp
var ds = new DataSet();
ds.ReadXml("data.xml");
// process...
ds.WriteExcel("data.xls"); // 先完成輸出端
```

實際案例：原文即採此做法。
實作環境：.NET、NPOI。
實測數據：
改善前：無法產出 Excel。
改善後：可產出 Excel 供驗證。
改善幅度：POC 驗證效率提升。

Learning Points
- 分段交付策略
- 風險控制與排序
技能要求：
- 必備：DataSet XML、NPOI
- 進階：需求溝通
延伸思考：
- 何時回補讀端？
- 需求變更如何不影響交付？
Practice Exercise
- 基礎：完成 XML→Excel。
- 進階：加入基本資料清洗。
- 專案：制定 POC→正式版的技術路線圖。
Assessment Criteria
- 功能（40%）：可產出 Excel
- 品質（30%）：流程穩定
- 效能（20%）：足夠快
- 創新（10%）：路線清晰

---

## Case #13: 在不支援 Extension Methods 的情境改用靜態方法

### Problem Statement（問題陳述）
業務場景：跨語言或舊專案（語言版本不支援擴充方法）需共用同一功能。希望在不同語言或編譯器下，能以靜態方法調用，避免語法糖限制。
技術挑戰：在失去語法糖時保持 API 可用性。
影響範圍：跨專案可重用性、團隊協作。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. Extension Methods 本質是靜態方法語法糖。
2. 舊版語言/工具可能不支援。
3. 需提供後備方案。
深層原因：
- 架構層面：可用性覆蓋不足。
- 技術層面：忽略語言/環境差異。
- 流程層面：缺乏多語言策略。

### Solution Design（解決方案設計）
解決策略：保留與公開等價靜態方法 NPOIExtension.WriteExcel(DataSet, path)，讓所有情境可用；在支援擴充的語言中以 using 呈現語法糖。

實施步驟：
1. 提供靜態方法
- 實作細節：與擴充方法共用內部實作。
- 所需資源：重構。
- 預估時間：0.5 小時。
2. 文件標註
- 實作細節：README 標註兩種用法。
- 所需資源：文件。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public static class NPOIExtension
{
    public static void WriteExcel(DataSet ds, string path) { /* 同一實作 */ }
    public static void WriteExcel(this DataSet ds, string path) => WriteExcel(ds, path);
}
```

實際案例：原文示例明確指出兩者等價。
實作環境：任意 .NET 語言。
實測數據：
改善前：不支援擴充時無法使用。
改善後：靜態方法可用。
改善幅度：覆蓋面提升。

Learning Points
- Extension 的本質
- API 雙路徑設計
技能要求：
- 必備：C#、API 設計
- 進階：多語言互通
延伸思考：
- COM 可見性需求？
- F# 等語言的友善 API？
Practice Exercise
- 基礎：提供等價靜態方法。
- 進階：封裝共用實作層。
- 專案：撰寫多語言使用手冊。
Assessment Criteria
- 功能（40%）：兩路徑可用
- 品質（30%）：無重複碼
- 效能（20%）：同等效率
- 創新（10%）：多語言範例

---

## Case #14: 正確認識 Extension Methods 的能力與限制

### Problem Statement（問題陳述）
業務場景：團隊部分成員誤以為擴充方法可新增屬性或靜態方法，或可改變類別行為，導致設計預期錯誤與實作偏差。需建立正確心智模型。
技術挑戰：釐清只能新增執行個體方法且無法存取私有成員。
影響範圍：API 設計正確性、風險控制。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 對語法糖理解不足。
2. 混淆擴充方法與部分類別。
3. 對可見性與限制不熟悉。
深層原因：
- 架構層面：知識傳遞不完整。
- 技術層面：語言特性理解片面。
- 流程層面：缺少設計審查。

### Solution Design（解決方案設計）
解決策略：以示例說明「只是靜態方法的語法糖」，只能新增 instance method，不可新增屬性/欄位/靜態方法；不可存取 private；建議用於「語意輔助」而非「改造類別」。

實施步驟：
1. 教程與示例
- 實作細節：對等寫法對照（擴充 vs 靜態）。
- 所需資源：教學文。
- 預估時間：1 小時。
2. 設計審查清單
- 實作細節：何種情況應/不應使用。
- 所需資源：團隊規範。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
// 擴充方法只是下列靜態方法的糖衣
public static void WriteExcel(this DataSet ds, string path) => CoreWrite(ds, path);
public static void WriteExcel(DataSet ds, string path) => CoreWrite(ds, path);
```

實際案例：原文明確描述限制。
實作環境：C# 3.0+。
實測數據：
改善前：錯誤期待常見。
改善後：共識提升。
改善幅度：設計偏誤減少。

Learning Points
- 語法糖與底層實相
- 能力與限制邊界
技能要求：
- 必備：C# 語言特性
- 進階：API 溝通
延伸思考：
- 何時改用擴充 vs 繼承 vs 組合？
Practice Exercise
- 基礎：列出 5 條限制並舉例。
- 進階：重寫一段誤用的擴充 API。
- 專案：制定擴充方法使用準則。
Assessment Criteria
- 功能（40%）：概念正確
- 品質（30%）：案例清晰
- 效能（20%）：N/A
- 創新（10%）：準則易用

---

## Case #15: 以 using 模式改寫 I/O：防止資源外洩與檔案鎖定

### Problem Statement（問題陳述）
業務場景：匯出 Excel 後偶見檔案被鎖或資源未釋放，導致後續覆寫失敗或清理困難。需保證 FileStream 正確釋放與例外安全。
技術挑戰：確保所有 I/O 皆在 using 區塊中並正確關閉。
影響範圍：穩定性、維運效率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 手動 Close 易遺漏。
2. 例外時未釋放。
3. 資源所有權不清楚。
深層原因：
- 架構層面：未制定 I/O 規範。
- 技術層面：未充分使用 using。
- 流程層面：缺少程式碼審查點。

### Solution Design（解決方案設計）
解決策略：所有 FileStream/Workbook 類型採 using；覆寫前先 File.Exists 刪除；將 I/O 封裝在最窄範圍內。

實施步驟：
1. 改寫 using
- 實作細節：using(var fs = File.OpenWrite(...))。
- 所需資源：重構。
- 預估時間：0.5 小時。
2. 增加覆寫保護
- 實作細節：存在則刪；處理例外。
- 所需資源：Try/Catch 日誌。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
if (File.Exists(path)) File.Delete(path);
using (var fs = File.OpenWrite(path))
{
    workbook.Write(fs);
} // 自動釋放與解鎖
```

實際案例：原文示例有 Close，建議最佳化為 using。
實作環境：.NET。
實測數據：
改善前：偶發鎖檔/未釋放。
改善後：資源確保釋放。
改善幅度：穩定性提升。

Learning Points
- IDisposable 與 using 模式
- 例外安全
技能要求：
- 必備：C# 資源管理
- 進階：靜態分析
延伸思考：
- 大檔案串流與 flush 策略？
Practice Exercise
- 基礎：以 using 改寫 I/O。
- 進階：加上重試策略。
- 專案：建立 I/O 風格檢查規則。
Assessment Criteria
- 功能（40%）：無鎖檔
- 品質（30%）：資源釋放完善
- 效能（20%）：I/O 合理
- 創新（10%）：重試/回退

---

## Case #16: 單元測試導向的 Excel 匯出驗證

### Problem Statement（問題陳述）
業務場景：匯出正確性常被忽略，交付後才發現欄位錯位、表頭遺漏。希望建立單元測試，生成檔案後再以 NPOI 讀回驗證內容。
技術挑戰：以程式驗證 Excel 內容，不依賴人工檢查。
影響範圍：品質保障、避免回歸。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 人工檢查易疏漏。
2. 無自動化測試導致回歸未被發現。
3. 不同資料集變化多。
深層原因：
- 架構層面：缺少測試友好設計。
- 技術層面：未知如何讀回驗證。
- 流程層面：缺測試文化。

### Solution Design（解決方案設計）
解決策略：用 NPOI 讀回剛輸出的 Excel，驗證表頭與幾筆資料；對特殊值（null、中文、長字串）設測試；將檔案輸出至暫存目錄並自動清理。

實施步驟：
1. 建立測試資料集
- 實作細節：小型 DataSet 含各種值。
- 所需資源：測試框架。
- 預估時間：0.5 小時。
2. 寫入並讀回
- 實作細節：WriteExcel→用 NPOI 讀回 Sheet/Row/Cell。
- 所需資源：NPOI。
- 預估時間：1 小時。
3. 斷言
- 實作細節：Assert 表頭與資料相等。
- 所需資源：測試框架。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
ds.WriteExcel(path);
using (var fs = File.OpenRead(path))
{
    var wb = new HSSFWorkbook(fs);
    var sheet = wb.GetSheetAt(0);
    Assert.Equal("Name", sheet.GetRow(0).GetCell(0).StringCellValue);
    Assert.Equal("John", sheet.GetRow(1).GetCell(0).StringCellValue);
}
```

實際案例：延伸自原文實作，加入測試策略。
實作環境：.NET、xUnit/NUnit、NPOI。
實測數據：
改善前：常見回歸。
改善後：自動驗證。
改善幅度：品質提升。

Learning Points
- 可測性設計
- 用同庫讀回驗證
技能要求：
- 必備：單元測試
- 進階：檔案 I/O 假件化
延伸思考：
- 以 memory stream 減少 I/O？
Practice Exercise
- 基礎：驗證表頭正確。
- 進階：驗證多 Sheet。
- 專案：建立完整測試套件模板。
Assessment Criteria
- 功能（40%）：測試覆蓋關鍵路徑
- 品質（30%）：斷言清晰
- 效能（20%）：測試速度
- 創新（10%）：工具化

---

## Case #17: 單元格型別映射策略：從純字串改為動態型別

### Problem Statement（問題陳述）
業務場景：目前將所有值以字串寫入（cell.SetCellType(CellType.STRING)），雖簡單，但失去數值/日期/布林型別，使用者無法直接做計算或排序。需建立型別映射策略，輸出正確的 CellType。
技術挑戰：正確判斷 DataColumn/DataRow 的型別與空值並映射至 NPOI。
影響範圍：可用性、後續分析體驗。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 目前強制字串化。
2. Excel 對字串數值無法計算。
3. 缺少映射層。
深層原因：
- 架構層面：輸出層簡化過度。
- 技術層面：型別轉換策略未定。
- 流程層面：未與需求對齊格式要求。

### Solution Design（解決方案設計）
解決策略：根據 DataColumn.DataType 或值型別決定 CellType；對 decimal/double 用 SetCellValue(double)；對 DateTime 用 SetCellValue(DateTime) 並套用日期格式；對 bool 用 SetCellValue(bool)；其餘字串。

實施步驟：
1. 型別映射表
- 實作細節：Type→動作對照。
- 所需資源：小型字典。
- 預估時間：1 小時。
2. 實作 SetCellValueByType
- 實作細節：switch 型別與空值處理。
- 所需資源：NPOI。
- 預估時間：1 小時。
3. 加入格式（日期/數值）
- 實作細節：資料格式 DataFormat 設置。
- 所需資源：NPOI 樣式。
- 預估時間：1 小時。

關鍵程式碼/設定：
```csharp
void SetCellValue(ICell cell, object v)
{
    if (v == null || v == DBNull.Value) return;
    switch (v)
    {
        case bool b: cell.SetCellValue(b); break;
        case DateTime dt:
            cell.SetCellValue(dt);
            var style = cell.Sheet.Workbook.CreateCellStyle();
            style.DataFormat = cell.Sheet.Workbook.CreateDataFormat().GetFormat("yyyy-mm-dd");
            cell.CellStyle = style; break;
        case IConvertible _ when double.TryParse(Convert.ToString(v), out var d):
            cell.SetCellValue(d); break;
        default: cell.SetCellValue(v.ToString()); break;
    }
}
```

實際案例：原文以字串輸出，這裡給出改進策略。
實作環境：.NET、NPOI。
實測數據：
改善前：全部字串，使用者需手動轉型。
改善後：正確型別，立即可算可排。
改善幅度：使用體驗顯著提升。

Learning Points
- 型別判斷與 NPOI API
- 資料格式化
技能要求：
- 必備：C# 型別系統
- 進階：NPOI 樣式
延伸思考：
- 大量格式化的效能影響？
Practice Exercise
- 基礎：為數值/日期正確輸出。
- 進階：加入自訂格式選項。
- 專案：型別映射可配置化。
Assessment Criteria
- 功能（40%）：型別正確
- 品質（30%）：程式簡潔
- 效能（20%）：格式建立重用
- 創新（10%）：可配置

---

## Case #18: 安全覆寫輸出檔與檔案存在策略

### Problem Statement（問題陳述）
業務場景：輸出檔經常同名，容易覆寫舊檔；若使用者希望保留舊版，需提供安全策略（如自動加時間戳或安全覆寫確認）。在批次或自動化環境需避免人工介入。
技術挑戰：既要避免誤覆寫，又要在服務場景自動運作。
影響範圍：資料安全、合規性、審計。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 直接刪除既存檔可能導致資料流失。
2. 無版本管理。
3. 無統一命名策略。
深層原因：
- 架構層面：缺少輸出命名規範。
- 技術層面：無安全覆寫選項。
- 流程層面：未納入合規要求。

### Solution Design（解決方案設計）
解決策略：提供 WriteExcel 的選項參數，如 OverwriteMode（Fail、Replace、Versioning）；預設 Versioning，在檔名後加上 yyyyMMddHHmmss；伺服器任務可設定 Replace。

實施步驟：
1. 定義選項
- 實作細節：enum OverwriteMode。
- 所需資源：小型設定類。
- 預估時間：0.5 小時。
2. 實作策略
- 實作細節：存在檔時根據模式處理。
- 所需資源：IO 操作。
- 預估時間：1 小時。
3. 文件與預設
- 實作細節：預設 Versioning。
- 所需資源：說明文件。
- 預估時間：0.5 小時。

關鍵程式碼/設定：
```csharp
public enum OverwriteMode { Fail, Replace, Versioning }
public static void WriteExcel(this DataSet ds, string path, OverwriteMode mode = OverwriteMode.Versioning)
{
    string finalPath = path;
    if (File.Exists(path))
    {
        if (mode == OverwriteMode.Fail) throw new IOException("File exists");
        if (mode == OverwriteMode.Versioning)
        {
            var ts = DateTime.Now.ToString("yyyyMMddHHmmss");
            finalPath = Path.Combine(Path.GetDirectoryName(path)!, $"{Path.GetFileNameWithoutExtension(path)}_{ts}{Path.GetExtension(path)}");
        }
        else File.Delete(path);
    }
    using (var fs = File.OpenWrite(finalPath)) { /* write workbook */ }
}
```

實際案例：原文示例刪除既存檔，這裡延伸出安全策略。
實作環境：.NET。
實測數據：
改善前：直接刪除，可能遺失。
改善後：版本化或失敗提示。
改善幅度：安全性提升。

Learning Points
- 輸出安全策略
- 可配置化選項
技能要求：
- 必備：IO 與例外處理
- 進階：合規思維
延伸思考：
- 記錄審計日志？
- 與檔案儲存服務整合？
Practice Exercise
- 基礎：實作三種模式。
- 進階：加入審計日志。
- 專案：與雲端儲存（S3/Azure Blob）整合版本化。
Assessment Criteria
- 功能（40%）：模式可用
- 品質（30%）：API 清楚
- 效能（20%）：IO 合理
- 創新（10%）：審計整合

---

案例分類

1. 按難度分類
- 入門級（適合初學者）：Case 3, 5, 6, 9, 12, 13, 14, 15
- 中級（需要一定基礎）：Case 1, 2, 4, 8, 11, 16, 18
- 高級（需要深厚經驗）：Case 7, 10, 17

2. 按技術領域分類
- 架構設計類：Case 2, 3, 11, 14, 18
- 效能優化類：Case 7, 15
- 整合開發類：Case 1, 4, 5, 6, 8, 9, 10, 12, 13, 17
- 除錯診斷類：Case 15, 16
- 安全防護類：Case 18

3. 按學習目標分類
- 概念理解型：Case 14, 11
- 技能練習型：Case 1, 4, 5, 6, 9, 10, 13, 15
- 問題解決型：Case 2, 7, 8, 12, 16, 18
- 創新應用型：Case 3, 17, 11

案例關聯圖（學習路徑建議）
- 建議先學：Case 14（正確認知 Extension Methods）→ Case 13（靜態方法後備）→ Case 3（語意化 API）
- 進一步：Case 12（POC 快速落地）→ Case 1（DataSet 寫 Excel 核心）→ Case 4（多表映射）→ Case 5（表頭）→ Case 6（Null 安全）→ Case 15（using/I-O 安全）
- 可靠性：Case 16（單元測試驗證）
- 進階選型與平台：Case 7（避開 COM）、Case 8（避開 Jet/x64 問題）、Case 11（NPOI/Koogra）
- 格式與新標準：Case 10（Open XML .xlsx）
- 進一步優化：Case 17（型別映射），Case 18（安全覆寫策略）

依賴關係：
- Case 1 依賴 Case 3/14 的概念與 API 設計思路
- Case 4, 5, 6 依賴 Case 1 的基本輸出能力
- Case 16 測試依賴 Case 1/4/5 的功能點
- Case 7, 8, 11, 10 為選型與平台延伸，不必嚴格依序，但建議在完成 Case 1 後評估
- Case 17 在 Case 6 基礎上深化型別處理
- Case 18 在 Case 15 的 I/O 安全上增加策略層

完整學習路徑建議：
1) 14 → 13 → 3（建立正確心智模型與語意化習慣）
2) 12 → 1（快速落地與核心輸出）→ 4 → 5 → 6 → 15（打造穩定可用的匯出管線）
3) 16（加入品質保證）
4) 7 → 8 → 11（伺服器端正確選型與相容性）
5) 10（掌握 .xlsx 官方路線）→ 17（型別與格式專業度提升）→ 18（安全策略與合規）

以上 18 個案例皆從原文的問題、根因、解法與參考脈絡出發，並補充實作細節與練習/評估設計，供實務訓練與專案演練使用。