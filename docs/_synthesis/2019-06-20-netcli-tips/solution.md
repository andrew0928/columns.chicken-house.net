---
layout: synthesis
title: "後端工程師必備: CLI 傳遞物件的處理技巧"
synthesis_type: solution
source_post: /2019/06/20/netcli-tips/
redirect_from:
  - /2019/06/20/netcli-tips/solution/
postid: 2019-06-20-netcli-tips
---

## Case #1: 以 JSON 行為單位在 CLI Pipeline 傳遞物件（行分隔 JSON）

### Problem Statement（問題陳述）
**業務場景**：團隊要將一個產生資料的 CLI（CLI-DATA）與一個處理資料的 CLI（CLI-P1）以管線串接，讓資料像生產線般一筆一筆流動處理，避免一次載入全部資料造成延遲與記憶體壓力。希望每個資料模型能獨立傳遞，讓下游立即開始處理，並保留可讀性與除錯便利性。  
**技術挑戰**：STDIN/STDOUT 常被誤認為只適合純文字，實作時若用 JSON 陣列包裹所有資料，接收端得等待全檔解析完才能開始，無法達成流式處理與低延遲。  
**影響範圍**：延遲到第一筆資料開始處理的時間、整體的吞吐、記憶體占用、可觀察性（Debug/Log）。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 將所有物件包成單一 JSON 陣列，導致接收端需要完整 parsing 後才能開始使用。  
2. 對 STDIN/STDOUT 的理解停留在 TextReader/TextWriter 層級，忽略其實為 Stream 層級可處理任意資料。  
3. 缺乏以資料筆數為單位的邊界設計，接收端不易識別分筆物件。

**深層原因**：
- 架構層面：資料傳輸協定未釐清「單筆邊界」與「流式運作」的設計目標。  
- 技術層面：未使用 JsonTextReader 的多內容模式，或 line-delimited JSON 的最佳實務。  
- 流程層面：缺乏以流式處理為導向的開發與測試（例如即時消費、邊產邊處理）。

### Solution Design（解決方案設計）
**解決策略**：以「行分隔 JSON（每行一個 JSON 物件）」傳遞資料，生產端逐筆序列化並加上換行，消費端使用 JsonTextReader 並開啟 SupportMultipleContent 逐筆反序列化，雙端以 IEnumerable<DataModel>/yield return 抽象化資料來源與處理流程，達到即時、低延遲、可串接的 pipeline。

**實施步驟**：
1. 生產端逐筆序列化輸出  
- 實作細節：使用 Newtonsoft.Json 的 JsonSerializer，每輸出一筆後 Console.Out.WriteLine()。  
- 所需資源：Newtonsoft.Json、.NET（Core）。  
- 預估時間：0.5 天。

2. 消費端逐筆反序列化  
- 實作細節：JsonTextReader(Console.In) 並設 jsonreader.SupportMultipleContent = true，while(Read()) 逐筆 Deserialize。  
- 所需資源：Newtonsoft.Json、.NET（Core）。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```csharp
// Producer (CLI-DATA)
var json = JsonSerializer.Create();
foreach (var model in GenerateData())
{
    json.Serialize(Console.Out, model);
    Console.Out.WriteLine(); // 以換行分隔每筆 JSON
}

// Consumer (CLI-P1)
IEnumerable<DataModel> ReceiveData()
{
    var json = JsonSerializer.Create();
    var reader = new JsonTextReader(Console.In) { SupportMultipleContent = true };
    while (reader.Read())
        yield return json.Deserialize<DataModel>(reader);
}
```

實際案例：CLI-DATA | CLI-P1 串接，CLI-P1 log 即時顯示 data(n) start/end，證明逐筆處理生效。  
實作環境：Windows + .NET (Core) + Newtonsoft.Json。  
實測數據：  
改善前：使用 JSON 陣列包裹，需完整讀畢才開始處理（高首筆延遲，非流式）。  
改善後：每筆輸出即被下一段消費，首筆延遲接近 0（以讀到首行為準）。  
改善幅度：首筆延遲由 O(n) 降為 O(1)（概念性；以示例 log 可觀察）。

Learning Points（學習要點）
核心知識點：
- 行分隔 JSON（LDJSON/NDJSON）適合流式處理。
- JsonTextReader.SupportMultipleContent 可逐筆讀取相鄰 JSON。
- IEnumerable/yield return 實現應用內的 pull-based 流式。

技能要求：
- 必備技能：C# 串流、Newtonsoft.Json、Console I/O。  
- 進階技能：設計可組合的資料管線抽象。

延伸思考：
- 也可用 System.Text.Json 搭配自定 Tokenizer 實作。  
- 風險：若輸出端未換行或 JSON 壞掉，接收端需要錯誤處理。  
- 優化：加入 schema 驗證或協定版本欄位。

Practice Exercise（練習題）
- 基礎練習：將 1000 筆模型以行分隔 JSON 輸出與讀取。  
- 進階練習：在接收端加入異常 JSON 行的跳過與告警。  
- 專案練習：設計三段 pipeline（產生→處理→彙整）皆採行分隔 JSON 串接。

Assessment Criteria（評估標準）
- 功能完整性（40%）：逐筆輸出/輸入運作並產生正確結果。  
- 程式碼品質（30%）：清楚的抽象與錯誤處理。  
- 效能優化（20%）：首筆延遲與記憶體占用控制。  
- 創新性（10%）：協定設計與可觀測性提升。


## Case #2: JsonTextReader 多內容模式讀取相鄰 JSON 物件

### Problem Statement（問題陳述）
**業務場景**：資料生產端每行輸出一個 JSON 物件供下游消費。接收端若以預設方式讀取，常見情況是只讀第一個物件或在第二個物件遇到解析問題，造成 pipeline 中斷。  
**技術挑戰**：Newtonsoft.Json 預設假設只有一個根內容，串流式的多物件輸入會導致解析狀態無法正確前進，出現阻塞或例外。  
**影響範圍**：導致資料處理中斷、吞吐降低、需要額外包裝陣列或緩存，失去流式特性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 預設 JsonTextReader 僅預期單一 JSON 根節點。  
2. 多個相鄰 JSON 根節點未以陣列包裹，Reader 狀態機需明確允許多內容。  
3. 缺少 while(Read()) 迭代與逐筆反序列化。

**深層原因**：
- 架構層面：未定義串流協定與解析策略。  
- 技術層面：忽略 SupportMultipleContent 開關與迭代模式。  
- 流程層面：未以示例或測試確保接收端能處理多筆根內容。

### Solution Design（解決方案設計）
**解決策略**：開啟 JsonTextReader.SupportMultipleContent，搭配 while (reader.Read()) 與逐筆 json.Deserialize<T>(reader) 讀取相鄰物件，保留流式消費能力。

**實施步驟**：
1. 啟用多內容模式  
- 實作細節：reader.SupportMultipleContent = true。  
- 所需資源：Newtonsoft.Json。  
- 預估時間：0.25 天。

2. 逐筆讀取反序列化  
- 實作細節：while (reader.Read()) yield return json.Deserialize<T>(reader)。  
- 所需資源：同上。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```csharp
var json = JsonSerializer.Create();
var reader = new JsonTextReader(Console.In) { SupportMultipleContent = true };
while (reader.Read())
{
    var item = json.Deserialize<DataModel>(reader);
    // consume item...
}
```

實際案例：文章之 CLI-P1 示範可連續處理 1000 筆資料。  
實作環境：Windows + .NET (Core) + Newtonsoft.Json。  
實測數據：  
改善前：只能讀取第一筆或於第二筆拋例外。  
改善後：穩定逐筆讀取 1000 筆。  
改善幅度：處理成功率由低提升至 100%。

Learning Points（學習要點）
核心知識點：
- JsonTextReader 的多內容模式。  
- 流式 JSON 解析的常見陷阱。  
- Reader/Deserializer 的狀態管理。

技能要求：
- 必備技能：C# I/O、Newtonsoft.Json Reader 模型。  
- 進階技能：流式解析例外處理策略。

延伸思考：
- 可加入行號、位移量以便故障診斷。  
- 可應用於 log ingestion、事件流解析。  
- 潛在風險：上游輸出異常導致 reader 卡住。

Practice Exercise（練習題）
- 基礎：開啟 SupportMultipleContent，成功讀取 10 筆相鄰 JSON。  
- 進階：注入一筆壞 JSON，實作跳過與錯誤報告。  
- 專案：設計可觀測的 JSON 流解析器（含 metrics）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：多筆相鄰 JSON 正確讀取。  
- 程式碼品質（30%）：清晰的狀態與錯誤處理。  
- 效能優化（20%）：逐筆處理無額外緩存。  
- 創新性（10%）：解析錯誤自我修復策略。


## Case #3: 移除頂層陣列，降低首筆延遲與記憶體占用

### Problem Statement（問題陳述）
**業務場景**：CLI-DATA 需輸出大量資料給 CLI-P1 處理。若以 JSON 陣列包裹所有資料，下游必須讀完整個陣列才能開始，大幅拉高首筆延遲與記憶體占用，不利於串流與即時處理。  
**技術挑戰**：維持 JSON 格式又要兼顧逐筆處理；不包陣列時要保證接收端能正確分割資料邊界。  
**影響範圍**：首筆延遲、記憶體峰值、處理節奏、可組合性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 陣列包裹導致消費端必須完整解析集合。  
2. 缺乏逐筆邊界控制。  
3. 缺少與接收端協定一致的輸出格式。

**深層原因**：
- 架構層面：未以「資料單元」為中心設計協定。  
- 技術層面：序列化策略未對齊流式需求。  
- 流程層面：缺少針對首筆延遲的測試與驗收。

### Solution Design（解決方案設計）
**解決策略**：採行分隔 JSON（每行一物件），避免頂層集合。消費端採多內容模式逐筆解析，實現即時處理與低記憶體占用。

**實施步驟**：
1. 生產端每筆物件獨立輸出  
- 實作細節：Serialize 後 WriteLine。  
- 所需資源：Newtonsoft.Json。  
- 預估時間：0.25 天。

2. 接收端即時消費  
- 實作細節：SupportMultipleContent + while(Read()) 逐筆 Deserialize。  
- 所需資源：同上。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```csharp
// 不使用頂層陣列；每行一物件
json.Serialize(Console.Out, model);
Console.Out.WriteLine();
```

實際案例：文章展示前 10 行輸出與即時處理 log。  
實作環境：Windows + .NET (Core) + Newtonsoft.Json。  
實測數據：  
改善前：需等待整個 JSON 陣列解析完。  
改善後：第一行即開始處理。  
改善幅度：首筆延遲顯著降為接近 0（概念性）。

Learning Points（學習要點）
核心知識點：
- 流式協定設計的關鍵：單元與邊界。  
- JSON 陣列 vs 行分隔 JSON 的取捨。  
- 生產線式資料流的架構思維。

技能要求：
- 必備技能：序列化、CLI pipeline。  
- 進階技能：協定演進與相容性處理。

延伸思考：
- 可加入 header（版本、校驗）以強化健壯性。  
- 風險：行內含換行或破壞格式需防禦。  
- 優化：行內壓縮或欄位壓縮策略。

Practice Exercise（練習題）
- 基礎：比較使用頂層陣列 vs 行分隔 JSON 的首筆可處理時間。  
- 進階：加入心跳訊息與 keep-alive。  
- 專案：規劃一個可演進的行分隔 JSON 協定（含版本號）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：逐筆處理可行。  
- 程式碼品質（30%）：協定一致性與錯誤處理。  
- 效能優化（20%）：首筆延遲與記憶體峰值表現。  
- 創新性（10%）：協定設計可演進性。


## Case #4: 以 IEnumerable/yield 抽象跨 CLI 的資料來源

### Problem Statement（問題陳述）
**業務場景**：希望 CLI-DATA 的資料產生與 CLI-P1 的資料消費能以一致抽象（IEnumerable<DataModel>）串接，讓商業邏輯像呼叫 RPC 一樣，不感知跨程式界線與 I/O 細節。  
**技術挑戰**：若將 I/O 細節混入業務邏輯，難以測試與重用；不使用 yield 將喪失流式特性。  
**影響範圍**：可測試性、重用性、流式處理效率。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 業務邏輯直接依賴 Console I/O。  
2. 無迭代器（yield）導致需緩存全部資料。  
3. 缺少可組合抽象，使 pipeline 模組化困難。

**深層原因**：
- 架構層面：界面與實作耦合。  
- 技術層面：未善用 IEnumerable 的 pull 模式。  
- 流程層面：缺乏單元測試與注入策略。

### Solution Design（解決方案設計）
**解決策略**：產生端（GenerateData）與接收端（ReceiveData）統一回傳 IEnumerable<DataModel>，以 yield return 流式輸出/輸入；業務函式只接 IEnumerable<T>，隔離 I/O 細節。

**實施步驟**：
1. 提取資料來源與接收器  
- 實作細節：抽出 GenerateData()/ReceiveData() 回傳 IEnumerable<T>。  
- 所需資源：C# IEnumerable/yield。  
- 預估時間：0.5 天。

2. 業務邏輯對 IEnumerable 編程  
- 實作細節：ProcessPhase1(IEnumerable<DataModel>)，內部 foreach。  
- 所需資源：同上。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```csharp
static IEnumerable<DataModel> GenerateData() { /* yield return model; */ }

static IEnumerable<DataModel> ReceiveData()
{
    var json = JsonSerializer.Create();
    var reader = new JsonTextReader(Console.In) { SupportMultipleContent = true };
    while (reader.Read()) yield return json.Deserialize<DataModel>(reader);
}
```

實際案例：文章重構 CLI-DATA/CLI-P1，兩端皆提供 IEnumerable 流。  
實作環境：.NET (Core)。  
實測數據：  
改善前：業務邏輯緊耦合 I/O、不可測試。  
改善後：可針對 IEnumerable 建立單元測試；保留流式處理。  
改善幅度：可測試性大幅提升（質性）。

Learning Points（學習要點）
核心知識點：
- yield return 與 pull-based streaming。  
- 分離 I/O 與業務邏輯。  
- 可組合的資料處理 API 設計。

技能要求：
- 必備技能：IEnumerable、委派/高階函式。  
- 進階技能：Functional-style pipeline 設計。

延伸思考：
- 支援 async（IAsyncEnumerable）以提升 I/O 效率。  
- 風險：上游阻塞會傳遞到下游。  
- 優化：加入取消與背壓設計。

Practice Exercise（練習題）
- 基礎：將 ProcessPhase1 改為接受 IEnumerable<DataModel>。  
- 進階：以 Fake IEnumerable 建立單元測試。  
- 專案：三段以上的 IEnumerable 管線組合與測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：抽象可被多處使用。  
- 程式碼品質（30%）：低耦合、高內聚。  
- 效能優化（20%）：保持流式、避免緩存。  
- 創新性（10%）：API 設計可擴展性。


## Case #5: 改用 BinaryFormatter 進行二進位序列化傳輸

### Problem Statement（問題陳述）
**業務場景**：擔心 JSON 文字化與 Base64 帶來的體積與效能開銷，希望嘗試以 .NET BinaryFormatter 直接進行二進位物件序列化傳遞，以保留型別資訊與避免字串化成本。  
**技術挑戰**：跨程式邊界進行二進位寫入/讀取，需要正確處理 STDIN/STDOUT Stream；需考量 BinaryFormatter 的相容性與安全性。  
**影響範圍**：序列化速度、輸出體積、可讀性、相容性、風險面。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. JSON Base64 造成 Buffer 膨脹。  
2. 文字處理與解析成本不可忽視。  
3. 期望以二進位傳遞減少 CPU 負擔。

**深層原因**：
- 架構層面：資料交換格式未明確標準化（跨語言相容性不足）。  
- 技術層面：BinaryFormatter 會包含型別中繼資料，可能導致體積增加。  
- 流程層面：未評估安全與版本演進。

### Solution Design（解決方案設計）
**解決策略**：Producer 以 BinaryFormatter.Serialize() 寫入 Console.OpenStandardOutput()；Consumer 以 BinaryFormatter.Deserialize() 循環從 Console.OpenStandardInput() 讀取，維持逐筆處理。

**實施步驟**：
1. Producer 寫入二進位  
- 實作細節：formatter.Serialize(os, model)。  
- 所需資源：.NET BinaryFormatter。  
- 預估時間：0.5 天。

2. Consumer 逐筆反序列化  
- 實作細節：while (istream.CanRead) yield return (DataModel)formatter.Deserialize(istream)。  
- 所需資源：同上。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```csharp
// Producer
var formatter = new BinaryFormatter();
var os = Console.OpenStandardOutput();
foreach (var model in GenerateData())
    formatter.Serialize(os, model);

// Consumer
var formatter = new BinaryFormatter();
var istream = Console.OpenStandardInput();
while (istream.CanRead)
{
    var model = formatter.Deserialize(istream) as DataModel;
    // consume model...
}
```

實際案例：CLI-DATA | CLI-P1 流程如文中示範可運作。  
實作環境：Windows + .NET (Core)。  
實測數據：  
改善前（JSON）：108,893 bytes（1000 筆）。  
改善後（二進位）：430,000 bytes（1000 筆）。  
改善幅度：反而增大約 295%（二進位包含中繼資料）。  

Learning Points（學習要點）
核心知識點：
- STDIN/STDOUT 是 Stream，可處理二進位。  
- BinaryFormatter 特性與限制。  
- 二進位格式與跨語言相容性的取捨。

技能要求：
- 必備技能：.NET 序列化 API。  
- 進階技能：自定序列化/跨語言格式（Protobuf、MessagePack）。

延伸思考：
- 風險：BinaryFormatter 對不受信資料不安全，.NET 官方不建議對外部輸入使用。  
- 應用：內部受信環境可作快速原型。  
- 優化：改用 Protobuf/MessagePack 並加 gzip。

Practice Exercise（練習題）
- 基礎：以 BinaryFormatter 作 1000 筆序列化/反序列化。  
- 進階：加入版本欄位並測試相容性。  
- 專案：替換為 MessagePack，量測體積與速度。

Assessment Criteria（評估標準）
- 功能完整性（40%）：二進位串流可 round-trip。  
- 程式碼品質（30%）：明確風險告知與錯誤處理。  
- 效能優化（20%）：序列化效率與體積管理。  
- 創新性（10%）：替代格式的比較與結論。


## Case #6: 二進位資料流加上 GZip 壓縮，顯著縮小傳輸體積

### Problem Statement（問題陳述）
**業務場景**：當 pipeline 跨網路（例如透過 ssh），傳輸體積會直接影響延遲與費用。BinaryFormatter 未壓縮時體積偏大，需要壓縮以提升效率。  
**技術挑戰**：不改動現有程式碼，能否用現成 CLI 工具在管線上動態壓縮與解壓縮，兼顧串接與可維護性。  
**影響範圍**：網路時間、頻寬成本、處理吞吐。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. BinaryFormatter 含型別中繼資料，原始體積大。  
2. 直接傳送未壓縮資料在網路上成本高。  
3. 需求是「串流壓縮」，而非離線壓縮。

**深層原因**：
- 架構層面：未將壓縮視為 pipeline 可替換階段。  
- 技術層面：不了解可直接用現成 gzip CLI 嵌入管線。  
- 測試層面：缺少對體積與速率的度量。

### Solution Design（解決方案設計）
**解決策略**：以 gzip -9 -c 壓縮 STDOUT、以 gzip -d 解壓 STDIN，在兩個 CLI 中間插入壓縮/解壓階段，不改原程式碼達成傳輸體積最小化。

**實施步驟**：
1. 產生資料並壓縮至檔案（或直接管線）  
- 實作細節：dotnet CLI-DATA.dll | gzip.exe -9 -c -f > data.gz。  
- 所需資源：gzip（Git for Windows 或其他發行）。  
- 預估時間：0.25 天。

2. 以管線動態壓縮/解壓再送入消費端  
- 實作細節：dotnet CLI-DATA.dll | gzip -9 -c | gzip -d | dotnet CLI-P1.dll。  
- 所需資源：同上。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```shell
# 壓縮到檔案
dotnet CLI-DATA.dll | gzip.exe -9 -c -f > data.gz

# 以檔案供應 + 解壓 + 消費
type data.gz | gzip.exe -d | dotnet CLI-P1.dll
```

實際案例：文中示範三段指令，log 顯示 CLI-P1 正常消費。  
實作環境：Windows + .NET (Core) + gzip（Git for Windows）。  
實測數據：  
改善前（BinaryFormatter 未壓縮）：430,000 bytes（1000 筆）。  
改善後（GZip）：47,064 bytes（1000 筆）。  
改善幅度：約 89.1% 體積縮減。

Learning Points（學習要點）
核心知識點：
- 壓縮可視為 pipeline 的一個 stage。  
- 現成 CLI 工具可大幅縮短實作時間。  
- 壓縮率與 CPU 成本的權衡。

技能要求：
- 必備技能：CLI 管線操作、gzip。  
- 進階技能：針對資料結構選擇最佳壓縮策略。

延伸思考：
- 可替換為 zstd、brotli。  
- 風險：CPU 壓縮開銷、時延與吞吐取捨。  
- 優化：依資料型態選擇壓縮等級。

Practice Exercise（練習題）
- 基礎：重現 47,064 bytes 成果。  
- 進階：量測 -1、-9 壓縮級別的時間與體積差。  
- 專案：設計可配置的「壓縮中介 CLI」。

Assessment Criteria（評估標準）
- 功能完整性（40%）：壓縮/解壓接力成功。  
- 程式碼品質（30%）：指令與腳本可維護。  
- 效能優化（20%）：壓縮率與延遲折衷。  
- 創新性（10%）：替代演算法比較。


## Case #7: 善用現成 CLI 工具（gzip）避免重造輪子

### Problem Statement（問題陳述）
**業務場景**：為達成壓縮需求，開發者打算在應用程式內嵌入壓縮程式碼，但會增加維護與相依成本。  
**技術挑戰**：如何以最小變更、最短時間導入可靠壓縮能力，並保持 pipeline 易組合。  
**影響範圍**：開發效率、維運負擔、可靠性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 直覺上想在程式碼中自行實作壓縮。  
2. 忽略作業系統與開發工具生態已有成熟 CLI。  
3. 忽略「管線即組件」的設計哲學。

**深層原因**：
- 架構層面：未把通用能力（壓縮）視為可插拔階段。  
- 技術層面：對系統工具熟悉度不足。  
- 流程層面：缺乏復用既有解法的文化。

### Solution Design（解決方案設計）
**解決策略**：以 gzip.exe（隨 Git for Windows 附帶）提供壓縮/解壓能力，透過管線串接兩端 CLI，達到「零程式碼變更」的快速整合。

**實施步驟**：
1. 安裝/取得 gzip  
- 實作細節：安裝 Git for Windows 或其他發行版提供的 gzip。  
- 所需資源：Git for Windows。  
- 預估時間：0.25 天。

2. 導入管線串接  
- 實作細節：dotnet CLI-DATA.dll | gzip -9 -c | gzip -d | dotnet CLI-P1.dll。  
- 所需資源：shell。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```shell
dotnet CLI-DATA.dll | gzip.exe -9 -c -f > data.gz
type data.gz | gzip.exe -d | dotnet CLI-P1.dll
```

實際案例：文中指令重現。  
實作環境：Windows + Git for Windows（gzip）。  
實測數據：  
改善前：需開發壓縮功能（高成本）。  
改善後：直接使用 gzip（零開發）。  
改善幅度：導入時間從天縮短至小時等級（質性）。

Learning Points（學習要點）
核心知識點：
- 工具鏈復用的價值。  
- UNIX 哲學：一器一事、可組合。  
- Pipeline 模式的可插拔性。

技能要求：
- 必備技能：CLI 基礎、管線操作。  
- 進階技能：將通用能力標準化為 stage。

延伸思考：
- 也可用 7z、tar 等工具。  
- 風險：環境相依（需保證工具存在）。  
- 優化：用腳本封裝以提高可移植性。

Practice Exercise（練習題）
- 基礎：在乾淨環境只靠 gzip 完成壓縮串接。  
- 進階：撰寫 cross-platform 腳本（PowerShell/Bash）。  
- 專案：模板化你的 pipeline stage 以便重用。

Assessment Criteria（評估標準）
- 功能完整性（40%）：工具導入與串接無誤。  
- 程式碼品質（30%）：腳本清晰。  
- 效能優化（20%）：適當壓縮等級。  
- 創新性（10%）：工具替換方案。


## Case #8: 動態壓縮解壓的管線佈署（壓縮傳輸、原樣處理）

### Problem Statement（問題陳述）
**業務場景**：上游希望以壓縮節省網路傳輸，下游既有處理器（CLI-P1）期待接收未壓縮資料，如何在不中斷既有處理器的情況下導入壓縮？  
**技術挑戰**：需保證資料串流在中段完成壓縮/解壓，兩側保持無感。  
**影響範圍**：部署簡易性、兼容性、延遲。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 兩端程式碼未設計壓縮邏輯。  
2. 直接改動處理器風險高。  
3. 需要中段代理完成轉換。

**深層原因**：
- 架構層面：未對傳輸層策略（壓縮）做分層。  
- 技術層面：不熟悉管線多段串接能力。  
- 流程層面：缺少灰度導入方案。

### Solution Design（解決方案設計）
**解決策略**：以兩個 gzip stage（壓縮、解壓）插入管線中，保持上下游原樣，最小化影響面，快速導入。

**實施步驟**：
1. 插入壓縮 stage  
- 實作細節：dotnet CLI-DATA.dll | gzip -9 -c。  
- 所需資源：gzip。  
- 預估時間：0.25 天。

2. 插入解壓 stage  
- 實作細節：… | gzip -d | dotnet CLI-P1.dll。  
- 所需資源：同上。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```shell
dotnet CLI-DATA.dll | gzip -9 -c -f | gzip -d | dotnet CLI-P1.dll > nul
```

實際案例：文章展示 4 個 process 併發執行（dotnet×2、gzip×2）。  
實作環境：Windows + .NET + gzip。  
實測數據：  
改善前：無壓縮，網路成本高。  
改善後：中段壓縮傳輸、落地前解壓。  
改善幅度：體積縮減同 Case #6（~89%）。

Learning Points（學習要點）
核心知識點：
- 中間層轉換（middleware-like）。  
- 無侵入式導入新策略。  
- 併發管線觀察與驗證。

技能要求：
- 必備技能：管線組合。  
- 進階技能：觀察進程/資源（tasklist、perf）。

延伸思考：
- 可封裝為單一「轉換器」CLI。  
- 風險：額外 CPU 成本與潛在瓶頸。  
- 優化：位置與並行度調整。

Practice Exercise（練習題）
- 基礎：在本機串接壓縮/解壓 stage。  
- 進階：在 ssh 遠端場景評估延遲改善。  
- 專案：自製「壓縮代理」CLI，支援多演算法。

Assessment Criteria（評估標準）
- 功能完整性（40%）：上下游無需修改即可運作。  
- 程式碼品質（30%）：腳本/部署可讀。  
- 效能優化（20%）：觀察延遲與 CPU。  
- 創新性（10%）：動態切換演算法。


## Case #9: 使用 LINQ 過濾流式物件（複雜條件不可用 grep）

### Problem Statement（問題陳述）
**業務場景**：上游傳來的物件只需處理符合特定條件的子集（例如 SerialNO 為 7 的倍數且只取前 5 筆），純文字工具（grep/find）無法對二進位或物件做語意過濾。  
**技術挑戰**：在保持流式處理（逐筆）前提下執行複雜條件過濾與截斷，並且要能「提早停止」避免不必要的計算。  
**影響範圍**：處理時間、資源耗用、業務正確性。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 文字工具不適合物件語意過濾。  
2. 未利用 IEnumerable 的延遲執行與短路特性。  
3. 全量處理造成浪費。

**深層原因**：
- 架構層面：未將過濾邏輯納入處理 stage。  
- 技術層面：對 LINQ 延遲與短路特性不熟悉。  
- 流程層面：缺少最小必要集的設計。

### Solution Design（解決方案設計）
**解決策略**：在 CLI-P1 內對 ReceiveData() 返回的 IEnumerable 使用 LINQ where 與 Take，逐筆過濾且達到條件即停止後續拉取，最大化節省資源。

**實施步驟**：
1. 套用過濾與截斷  
- 實作細節：from x in ReceiveData() where x.SerialNO % 7 == 0 select x).Take(5。  
- 所需資源：LINQ。  
- 預估時間：0.25 天。

2. 驗證短路  
- 實作細節：觀察 log 只處理 5 筆（7,14,21,28,35）。  
- 所需資源：log。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```csharp
foreach (var model in (from x in ReceiveData()
                       where x.SerialNO % 7 == 0
                       select x).Take(5))
{
    DataModelHelper.ProcessPhase1(model);
}
```

實際案例：文章展示 log 僅出現 5 筆符合條件資料。  
實作環境：.NET (Core)。  
實測數據：  
改善前：1000 筆全量處理。  
改善後：僅處理 5 筆。  
改善幅度：處理筆數降 99.5%。

Learning Points（學習要點）
核心知識點：
- LINQ 延遲執行與短路（Take）。  
- 在 IEnumerable 上做流式過濾。  
- 物件語意過濾 vs 文字過濾。

技能要求：
- 必備技能：LINQ 基礎。  
- 進階技能：Query 可讀性與效能權衡。

延伸思考：
- 可用 Select 投影只保留必要欄位。  
- 風險：過濾條件變更需同步測試。  
- 優化：以預先索引/快取降低計算。

Practice Exercise（練習題）
- 基礎：改寫條件過濾為「SerialNO 為 5 的倍數取 3 筆」。  
- 進階：加入多欄位條件與投影。  
- 專案：封裝可配置的過濾 stage（由 CLI 參數注入）。

Assessment Criteria（評估標準）
- 功能完整性（40%）：過濾與短路正確。  
- 程式碼品質（30%）：條件表達清晰可維護。  
- 效能優化（20%）：避免不必要計算。  
- 創新性（10%）：可配置化的 query stage。


## Case #10: Take 短路讓上游提早停止拉取，降低整體工作量

### Problem Statement（問題陳述）
**業務場景**：實務上經常只需前 K 筆符合條件的資料，剩餘資料不需要處理，若不短路會造成上游仍持續生產與解碼，浪費資源。  
**技術挑戰**：需確保 IEnumerable pipeline 在下游停止枚舉後，上游即停止提供後續資料，達成背壓式節流。  
**影響範圍**：CPU、I/O、整體處理時間。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未利用 IEnumerable 的拉取模式。  
2. 未使用 Take 等短路運算子。  
3. 錯誤設計為先全量載入再過濾。

**深層原因**：
- 架構層面：缺乏背壓與早停設計。  
- 技術層面：對 iterator 行為理解不足。  
- 流程層面：未以最小必要工作量為目標。

### Solution Design（解決方案設計）
**解決策略**：在下游以 Take(k) 明確截斷，再加上 where 過濾，確保 foreach 中途 break 導致上游停止 Read/Deserialize，達到端到端早停。

**實施步驟**：
1. 加入 Take 截斷  
- 實作細節：…Where(...).Take(5)。  
- 所需資源：LINQ。  
- 預估時間：0.25 天。

2. 驗證上游早停  
- 實作細節：觀察 log 與生產端輸出是否停止。  
- 所需資源：log。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```csharp
var filtered = ReceiveData().Where(x => x.SerialNO % 7 == 0).Take(5);
// foreach 遍歷 filtered 完畢後，上游不再 Read/Deserialize
```

實際案例：log 僅處理到 SerialNO 35。  
實作環境：.NET (Core)。  
實測數據：  
改善前：全量 1000 筆解碼與處理。  
改善後：僅解碼/處理 5 筆。  
改善幅度：99.5% 以上工作量降低（概念性）。

Learning Points（學習要點）
核心知識點：
- IEnumerable 的 pull/backpressure。  
- LINQ 短路的端到端效果。  
- 觀察性驗證。

技能要求：
- 必備技能：LINQ、迭代器。  
- 進階技能：設計背壓友善的 stage。

延伸思考：
- 改用 IAsyncEnumerable 增強 I/O 效率。  
- 風險：無保證上游資源立即釋放，需清理策略。  
- 優化：CancellationToken 傳遞。

Practice Exercise（練習題）
- 基礎：以 Take(1) 觀察首筆即停。  
- 進階：在上游加入可觀測計數器。  
- 專案：設計支援取消的 pipeline。

Assessment Criteria（評估標準）
- 功能完整性（40%）：端到端早停生效。  
- 程式碼品質（30%）：清楚的短路與釋放。  
- 效能優化（20%）：顯著減少上游工作量。  
- 創新性（10%）：取消/背壓設計。


## Case #11: 二進位輸出直送終端的混亂與防範策略

### Problem Statement（問題陳述）
**業務場景**：若使用者直接執行產生二進位輸出的 CLI（非管線），資料會噴灑到終端造成亂碼與操作混亂，影響使用體驗與支援成本。  
**技術挑戰**：需在可輸出二進位與可閱讀性之間做妥善預設與防呆。  
**影響範圍**：使用者體驗、支援成本、可用性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 終端預期文字，二進位會導致亂像。  
2. 使用者不一定以管線方式消費輸出。  
3. 程式未辨識輸出是否已被重導。

**深層原因**：
- 架構層面：輸出模式無預設策略。  
- 技術層面：未利用 Console.IsOutputRedirected。  
- 流程層面：缺乏使用情境測試。

### Solution Design（解決方案設計）
**解決策略**：預設輸出 JSON 可讀文本；若偵測到輸出已重導或指定旗標，才輸出二進位。提供參數切換模式與清楚說明。

**實施步驟**：
1. 偵測輸出重導與旗標  
- 實作細節：Console.IsOutputRedirected 或 --binary/--json 參數。  
- 所需資源：.NET Console API。  
- 預估時間：0.5 天。

2. 設定合理預設與錯誤訊息  
- 實作細節：未重導卻二進位時給出警告。  
- 所需資源：log/usage。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```csharp
bool preferBinary = args.Contains("--binary");
if (!Console.IsOutputRedirected && preferBinary)
{
    Console.Error.WriteLine("Warning: Binary output to terminal may be unreadable. Consider piping or using --json.");
}
// 根據模式輸出 JSON 或 Binary
```

實際案例：文章提醒「直接把 binary data 輸出到 terminal 會搞得一團亂」。  
實作環境：.NET (Core)。  
實測數據：  
改善前：終端亂碼、使用者困惑。  
改善後：預設友善、可選切換。  
改善幅度：使用錯誤率顯著降低（質性）。

Learning Points（學習要點）
核心知識點：
- Console.IsOutputRedirected 的應用。  
- 產品化預設與防呆。  
- 文件化與使用說明。

技能要求：
- 必備技能：CLI 介面設計。  
- 進階技能：使用體驗與可用性工程。

延伸思考：
- 自動 fallback：若非重導自動改 JSON。  
- 風險：誤判情境造成預期外行為。  
- 優化：提供 --force-binary。

Practice Exercise（練習題）
- 基礎：加入 --binary/--json 參數與重導偵測。  
- 進階：根據模式輸出不同 Content-Type 標記。  
- 專案：打造友善的 CLI UX 範本專案。

Assessment Criteria（評估標準）
- 功能完整性（40%）：模式切換與偵測正確。  
- 程式碼品質（30%）：清楚的使用說明。  
- 效能優化（20%）：無多餘開銷。  
- 創新性（10%）：UX 小改進（如彩色提示）。


## Case #12: 以 CLI log 驗證流式處理與併發執行

### Problem Statement（問題陳述）
**業務場景**：需要證明 pipeline 為「邊產邊處理」，且多個 process 併發工作。  
**技術挑戰**：如何以最小成本收集證據，讓團隊確信流式處理與併發是確實運作的。  
**影響範圍**：信任度、可觀測性、除錯效率。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏可觀察訊號。  
2. 對 pipeline 行為的認知僅停留在理論。  
3. 無系統化驗證流程。

**深層原因**：
- 架構層面：未建立可觀測性標準。  
- 技術層面：log 與系統工具未整合使用。  
- 流程層面：驗證步驟未文檔化。

### Solution Design（解決方案設計）
**解決策略**：在 CLI-P1 中對每筆資料 log start/end，並使用 tasklist 觀察 gzip/dotnet 進程；必要時配合 clip 將輸出快速複製，建立可驗證證據鏈。

**實施步驟**：
1. 增加關鍵 log  
- 實作細節：每筆處理前後記錄 SerialNO 與時間。  
- 所需資源：log 框架。  
- 預估時間：0.25 天。

2. 觀察進程與記錄  
- 實作細節：tasklist | clip，貼至筆記中存證。  
- 所需資源：Windows 內建工具。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```text
[P1][time] data(7) start...
[P1][time] data(7) end...
# tasklist | clip 取得當前進程清單
```

實際案例：文中展示連續的 start/end 與進程清單。  
實作環境：Windows + .NET + tasklist + clip。  
實測數據：  
改善前：無證據、難以說服。  
改善後：log 與進程清單證實流式與併發。  
改善幅度：團隊對系統信心提升（質性）。

Learning Points（學習要點）
核心知識點：
- 可觀測性基礎：log、process 狀態。  
- 工具鏈快速蒐證（clip）。  
- 验證方法學。

技能要求：
- 必備技能：log 設計。  
- 進階技能：可觀測性與 SRE 實務。

延伸思考：
- 導入 metrics（qps、延遲）與 tracing。  
- 風險：log 過量影響效能。  
- 優化：抽樣 log。

Practice Exercise（練習題）
- 基礎：加入 start/end log。  
- 進階：輸出處理時間統計。  
- 專案：導入 Prometheus 指標。

Assessment Criteria（評估標準）
- 功能完整性（40%）：關鍵 log 完整。  
- 程式碼品質（30%）：log 結構清晰。  
- 效能優化（20%）：log 量控制。  
- 創新性（10%）：自動化蒐證腳本。


## Case #13: 以 type + gzip -d 重放壓縮檔測試處理器

### Problem Statement（問題陳述）
**業務場景**：希望重放先前錄製的壓縮資料（.gz）來測試 CLI-P1 的穩定性與可重現問題。  
**技術挑戰**：需將離線壓縮檔透過管線解壓後餵給處理器，模擬真實上游輸出。  
**影響範圍**：測試效率、問題重現能力、維運。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏方法將 .gz 餵入處理器。  
2. 測試資料重放流程未定義。  
3. 需要零修改應用程式的測試手段。

**深層原因**：
- 架構層面：測試注入點未定義。  
- 技術層面：未活用 CLI 組合。  
- 流程層面：測試資料管理不完善。

### Solution Design（解決方案設計）
**解決策略**：以 type data.gz | gzip -d | dotnet CLI-P1.dll 將檔案解壓並直接輸入處理器，重現真實流式場景。

**實施步驟**：
1. 錄製資料  
- 實作細節：dotnet CLI-DATA.dll | gzip -9 -c > data.gz。  
- 所需資源：gzip。  
- 預估時間：0.25 天。

2. 重放資料  
- 實作細節：type data.gz | gzip -d | dotnet CLI-P1.dll。  
- 所需資源：同上。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```shell
type data.gz | gzip.exe -d | dotnet CLI-P1.dll
```

實際案例：文章展示該組合可用。  
實作環境：Windows + gzip + .NET。  
實測數據：  
改善前：難以重現線上資料。  
改善後：可快速重放測試。  
改善幅度：測試效率大幅提升（質性）。

Learning Points（學習要點）
核心知識點：
- 測試資料重放與生產一致性。  
- CLI 組合的靈活性。  
- 快速回歸測試。

技能要求：
- 必備技能：檔案/管線操作。  
- 進階技能：測試資料版本管理。

延伸思考：
- 建置測試資料倉庫。  
- 風險：敏感資料需脫敏。  
- 優化：加入時間戳與檔案校驗。

Practice Exercise（練習題）
- 基礎：錄製 1000 筆資料並重放。  
- 進階：在重放時插入過濾 stage。  
- 專案：建立自動化重放工具。

Assessment Criteria（評估標準）
- 功能完整性（40%）：重放成功。  
- 程式碼品質（30%）：腳本清晰。  
- 效能優化（20%）：重放接近真實節奏。  
- 創新性（10%）：測試資料治理方案。


## Case #14: 以 clip.exe 快速捕捉命令輸出以利紀錄與分享

### Problem Statement（問題陳述）
**業務場景**：在撰寫文件或回報問題時，需要將 tasklist、指令結果快速貼到工單或聊天中，手動滑鼠選取易漏、耗時。  
**技術挑戰**：如何一鍵將 STDOUT 內容放入剪貼簿，提升溝通效率。  
**影響範圍**：文件化效率、協作體驗。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏快速導出到剪貼簿的方法。  
2. 手動選取易錯。  
3. 不熟悉 Windows 內建工具。

**深層原因**：
- 架構層面：資訊傳遞流程未優化。  
- 技術層面：工具使用知識缺口。  
- 流程層面：缺少標準操作指引。

### Solution Design（解決方案設計）
**解決策略**：使用 Windows 內建 clip.exe，將命令輸出導入剪貼簿，減少手動步驟。

**實施步驟**：
1. 基本使用  
- 實作細節：tasklist | clip。  
- 所需資源：Windows clip.exe。  
- 預估時間：即時。

2. 文件化與教學  
- 實作細節：在貢獻指南中加入示例。  
- 所需資源：Wiki。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```shell
tasklist | clip
```

實際案例：文章示範使用方式與 /? help。  
實作環境：Windows。  
實測數據：  
改善前：手動選取複製。  
改善後：一鍵複製到剪貼簿。  
改善幅度：操作時間減少 80%+（估算）。

Learning Points（學習要點）
核心知識點：
- clip.exe 的用途。  
- STDOUT 重導的多樣化。  
- 文件化的小工具價值。

技能要求：
- 必備技能：命令列基礎。  
- 進階技能：編寫內部操作手冊。

延伸思考：
- 可配合 powershell/alias 提速。  
- 風險：剪貼簿敏感資料外洩。  
- 優化：先經過遮罩工具。

Practice Exercise（練習題）
- 基礎：將三個不同指令輸出導至剪貼簿。  
- 進階：以批次檔封裝常用輸出。  
- 專案：建立「診斷資料一鍵收集」腳本。

Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出正確入剪貼簿。  
- 程式碼品質（30%）：腳本可讀可維護。  
- 效能優化（20%）：操作步驟最少化。  
- 創新性（10%）：人性化的提示與遮罩。


## Case #15: 定義資料模型並確保可序列化（[Serializable] + 欄位/屬性）

### Problem Statement（問題陳述）
**業務場景**：為了能在 JSON/二進位之間自由切換，資料模型需具備穩定的序列化特性與欄位設計（ID、SerialNO、Stage、Buffer），以支援多種傳輸策略。  
**技術挑戰**：同一模型需同時支援 JSON 與 BinaryFormatter，欄位/屬性與列舉需正確標註與設計。  
**影響範圍**：相容性、序列化成功率、跨格式轉換。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 模型未標示可序列化（BinaryFormatter）。  
2. 欄位/屬性命名與型別不一致。  
3. 列舉未固定。

**深層原因**：
- 架構層面：資料契約未明確化。  
- 技術層面：不同序列化器需求未對齊。  
- 流程層面：缺少契約測試。

### Solution Design（解決方案設計）
**解決策略**：定義 [Serializable] 的 DataModel，使用屬性（get/set）與穩定欄位，列舉型別固定，確保 JSON 與 BinaryFormatter 均可使用。

**實施步驟**：
1. 建模與標註  
- 實作細節：[Serializable]；public 屬性；列舉固定。  
- 所需資源：.NET。  
- 預估時間：0.25 天。

2. 雙格式測試  
- 實作細節：JSON 與 BinaryFormatter 互相 round-trip 測試。  
- 所需資源：單元測試。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```csharp
[Serializable]
public class DataModel
{
    public string ID { get; set; }
    public int SerialNO { get; set; }
    public DataModelStageEnum Stage { get; set; } = DataModelStageEnum.INIT;
    public byte[] Buffer = null;
}
```

實際案例：文章提供模型定義並在兩種序列化中使用。  
實作環境：.NET (Core)。  
實測數據：  
改善前：可能出現二進位序列化失敗或欄位遺漏。  
改善後：雙格式可用。  
改善幅度：序列化成功率提升至 100%（測例）。

Learning Points（學習要點）
核心知識點：
- 可序列化類型設計。  
- 列舉與預設值。  
- 欄位/屬性在不同序列化器的行為。

技能要求：
- 必備技能：C# 類型系統。  
- 進階技能：資料契約演進策略。

延伸思考：
- DataContract/DataMember 精確控制。  
- 風險：BinaryFormatter 安全議題。  
- 優化：以 DTO 分離內部/外部模型。

Practice Exercise（練習題）
- 基礎：對模型做 JSON/Binary round-trip。  
- 進階：加入新欄位、維持相容。  
- 專案：定義版本化資料契約並加測試。

Assessment Criteria（評估標準）
- 功能完整性（40%）：雙格式可 round-trip。  
- 程式碼品質（30%）：清晰契約定義。  
- 效能優化（20%）：欄位合理。  
- 創新性（10%）：契約演進設計。


## Case #16: 產生端逐筆輸出＋換行確保邊界（避免黏包/解析模糊）

### Problem Statement（問題陳述）
**業務場景**：多筆 JSON 相鄰輸出時，接收端需辨識每筆邊界，否則可能出現黏包造成解析錯誤或等待。  
**技術挑戰**：如何用最小代價在文字格式下建立可靠的記錄邊界。  
**影響範圍**：解析正確性、延遲、穩定性。  
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. JSON 缺少天然記錄分隔符。  
2. 未以換行分隔輸出。  
3. 接收端 reader 無法定位起訖。

**深層原因**：
- 架構層面：協定未定義邊界。  
- 技術層面：輸出/解析策略未對齊。  
- 流程層面：缺少錯誤注入測試。

### Solution Design（解決方案設計）
**解決策略**：每筆序列化後接一個換行；接收端以多內容模式逐筆讀取，並在錯誤時報告行號，降低故障定位成本。

**實施步驟**：
1. 輸出加換行  
- 實作細節：Serialize + Console.Out.WriteLine()。  
- 所需資源：Json.NET。  
- 預估時間：即時。

2. 解析與行號紀錄  
- 實作細節：在錯誤訊息包含當前筆數。  
- 所需資源：log。  
- 預估時間：0.25 天。

**關鍵程式碼/設定**：
```csharp
json.Serialize(Console.Out, model);
Console.Out.WriteLine(); // 邊界
```

實際案例：文中 Producer 如此實作。  
實作環境：.NET (Core)。  
實測數據：  
改善前：相鄰 JSON 易解析混亂。  
改善後：逐筆穩定解析。  
改善幅度：解析穩定性顯著提升（質性）。

Learning Points（學習要點）
核心知識點：
- 邊界在流式協定中的重要性。  
- 以換行作為簡單且可靠的分隔。  
- 錯誤診斷友善性。

技能要求：
- 必備技能：I/O 與序列化。  
- 進階技能：協定可觀測性設計。

延伸思考：
- 可用長度前綴（length-prefix）替代換行。  
- 風險：內容內含換行需 escape 或 base64。  
- 優化：長度前綴更嚴謹。

Practice Exercise（練習題）
- 基礎：以換行分隔輸出 1000 筆並解析。  
- 進階：模擬破壞一行並偵測。  
- 專案：改為 length-prefix 協定。

Assessment Criteria（評估標準）
- 功能完整性（40%）：逐筆邊界明確。  
- 程式碼品質（30%）：錯誤訊息友善。  
- 效能優化（20%）：解析高效。  
- 創新性（10%）：協定優化提案。


## Case #17: 使用 Json 與 Binary 格式的取捨與決策框架

### Problem Statement（問題陳述）
**業務場景**：不同場景下對可讀性、體積、速度、安全、跨語言有不同要求，需在 JSON 與 Binary（二進位）格式間做合理選擇，並可套用壓縮組合。  
**技術挑戰**：缺乏一個以實測與風險為基礎的決策框架，容易拍腦袋。  
**影響範圍**：維護成本、可移植性、效能。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 單一維度（速度）決策，忽略體積與相容性。  
2. 忽略壓縮後的真實體積。  
3. 未評估安全風險（BinaryFormatter）。

**深層原因**：
- 架構層面：無格式選型準則。  
- 技術層面：缺測量與對照。  
- 流程層面：缺決策紀錄與回溯。

### Solution Design（解決方案設計）
**解決策略**：建立決策表：JSON（可讀、跨語言、體積中等）、BinaryFormatter（型別豐富、體積大、不安全）、Binary+Gzip（體積小、CPU 成本），依需求勾選，並以實測數據（108,893/430,000/47,064 bytes）佐證。

**實施步驟**：
1. 蒐集指標  
- 實作細節：對同一資料生成 JSON、Binary、Binary+Gzip 體積。  
- 所需資源：現有示例。  
- 預估時間：0.5 天。

2. 定義選型準則  
- 實作細節：可讀性/相容性/體積/安全/維護。  
- 所需資源：團隊共識。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```text
JSON: 108,893 bytes
BinaryFormatter: 430,000 bytes
Binary + GZip: 47,064 bytes
```

實際案例：數據來自文章測試（1000 筆）。  
實作環境：.NET (Core)、Newtonsoft.Json、BinaryFormatter、gzip。  
實測數據：如上。  
改善前：無依據的格式選擇。  
改善後：以數據與準則決策。  
改善幅度：決策品質提升（質性）。

Learning Points（學習要點）
核心知識點：
- 多維度格式選型（功能/非功能）。  
- 以數據為本的工程決策。  
- 風險管控（BinaryFormatter 安全）。

技能要求：
- 必備技能：基準測試與度量。  
- 進階技能：決策紀錄（ADR）。

延伸思考：
- 引入 Protobuf/MessagePack 對比。  
- 風險：過度優化單一指標。  
- 優化：情境化決策模板。

Practice Exercise（練習題）
- 基礎：重現 3 組體積測量。  
- 進階：加入 MessagePack+gzip。  
- 專案：撰寫本團隊格式選型 ADR。

Assessment Criteria（評估標準）
- 功能完整性（40%）：測試可重現。  
- 程式碼品質（30%）：測試腳本清晰。  
- 效能優化（20%）：指標完整。  
- 創新性（10%）：決策模板設計。


## Case #18: Pipeline 思維下的一進一出準則（每讀一筆、處理一筆、輸出一筆）

### Problem Statement（問題陳述）
**業務場景**：為達生產線式流動，系統需遵守「取得一筆→處理一筆→輸出一筆」的節奏，避免堆積與延遲。  
**技術挑戰**：若任一階段違反此準則（例如批次聚合再輸出），會破壞整體流式特性。  
**影響範圍**：延遲、記憶體、吞吐。  
**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未以單筆為粒度設計處理。  
2. 中途緩存與聚合。  
3. 缺乏流式思維與驗收標準。

**深層原因**：
- 架構層面：資料流設計不一致。  
- 技術層面：未善用 IEnumerable 與管線工具。  
- 流程層面：無流式專用測試。

### Solution Design（解決方案設計）
**解決策略**：所有 stage 遵循單筆處理輸出；以 IEnumerable/yield 實作；以 LINQ 保持延遲與短路；以 log/metrics 監控每筆處理時間。

**實施步驟**：
1. API 準則化  
- 實作細節：所有 stage 接受/回傳 IEnumerable<T>。  
- 所需資源：C#。  
- 預估時間：1 天。

2. 驗收與監控  
- 實作細節：每筆 log 與延遲指標。  
- 所需資源：log、metrics。  
- 預估時間：0.5 天。

**關鍵程式碼/設定**：
```csharp
IEnumerable<TOut> Stage(IEnumerable<TIn> src)
{
    foreach (var x in src)
    {
        var y = Process(x);
        yield return y; // 不緩存，逐筆產出
    }
}
```

實際案例：文章以 IEnumerable 串聯 ReceiveData/Process。  
實作環境：.NET (Core)。  
實測數據：  
改善前：批次導致高延遲與高記憶體。  
改善後：逐筆低延遲與常數記憶體。  
改善幅度：首筆延遲顯著下降（質性）。

Learning Points（學習要點）
核心知識點：
- 流式處理準則。  
- 延遲與吞吐的平衡。  
- 可觀測性支撐流式驗收。

技能要求：
- 必備技能：IEnumerable、LINQ。  
- 進階技能：流式架構設計。

延伸思考：
- 需要聚合時如何不破壞流式（滑動視窗）。  
- 風險：上游堵塞傳遞。  
- 優化：非同步與背壓。

Practice Exercise（練習題）
- 基礎：將某批次處理改為逐筆輸出。  
- 進階：加入滑動視窗聚合。  
- 專案：端到端流式 pipeline，含 metrics。

Assessment Criteria（評估標準）
- 功能完整性（40%）：逐筆輸出準則落地。  
- 程式碼品質（30%）：API 清晰一致。  
- 效能優化（20%）：首筆延遲/記憶體。  
- 創新性（10%）：視窗化聚合設計。


-----------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）：Case #2, #3, #7, #11, #12, #13, #14, #16  
- 中級（需要一定基礎）：Case #1, #4, #5, #6, #8, #9, #10, #15, #18  
- 高級（需要深厚經驗）：Case #17（決策與治理）

2. 按技術領域分類
- 架構設計類：#1, #3, #4, #17, #18  
- 效能優化類：#6, #8, #9, #10, #16  
- 整合開發類：#7, #13, #14, #12, #11  
- 除錯診斷類：#12, #16  
- 安全防護類：#5（BinaryFormatter 安全風險提示）、#17（風險面）

3. 按學習目標分類
- 概念理解型：#1, #3, #18, #17  
- 技能練習型：#2, #4, #6, #7, #13, #16  
- 問題解決型：#5, #8, #9, #10, #11, #12, #15  
- 創新應用型：#6, #8, #17

-----------------------
案例關聯圖（學習路徑建議）
- 入門順序（基礎概念 → 基礎技能 → 流式思維）：  
1) Case #3（移除頂層陣列，理解流式 JSON）  
2) Case #2（多內容模式解析）  
3) Case #16（換行邊界）  
4) Case #1（完整 JSON 流式管線）

- 進階抽象與實作（可組合與可測試）：  
5) Case #4（IEnumerable/yield 抽象）  
6) Case #18（逐筆處理準則）  
7) Case #9（LINQ 過濾）  
8) Case #10（Take 短路與早停）

- 效能與體積（壓縮與管線整合）：  
9) Case #5（BinaryFormatter 實驗）  
10) Case #6（Binary+GZip 最佳化）  
11) Case #8（壓縮中段導入）  
12) Case #7（善用現成 CLI）

- 測試與可觀測性：  
13) Case #13（重放測試）  
14) Case #12（log 與進程觀察）

- 使用者體驗與產品化：  
15) Case #11（二進位防呆）  
16) Case #14（clip 提升紀錄效率）

- 決策與治理（最後統整）：  
17) Case #17（格式選型決策框架）

依賴關係：
- Case #1 依賴 #2, #3, #16（解析與邊界）  
- Case #9, #10 依賴 #4（IEnumerable）  
- Case #6, #8 依賴 #5（了解二進位特性）  
- Case #17 依賴 #5, #6 的實測數據

完整學習路徑：
#3 → #2 → #16 → #1 → #4 → #18 → #9 → #10 → #5 → #6 → #8 → #7 → #13 → #12 → #11 → #14 → #17

此路徑從流式 JSON 基礎開始，逐步建立抽象與流程準則，再進入效能體積優化與整合，最後以可觀測、產品化與決策治理收束，形成一條從實作到架構的完整學習曲線。