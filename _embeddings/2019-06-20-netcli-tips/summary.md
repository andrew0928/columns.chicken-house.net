# 後端工程師必備: CLI 傳遞物件的處理技巧

## 摘要提示
- Pipeline 與物件: 以 STDIN/STDOUT 為 Stream，透過序列化可在 CLI 間傳遞物件而非僅限純文字。
- Json 序列化: 逐筆輸出 JSON 並逐筆反序列化，避免必須等完整文件才處理，支援串流化處理。
- Binary 序列化: 以 BinaryFormatter 序列化可直接在管線內傳遞二進位物件資料。
- GZip 壓縮: 善用外部 gzip 工具壓縮/解壓 STDIO 串流，大幅縮小傳輸體積。
- IEnumerable 抽象: 以 IEnumerable<DataModel> 抽象資料來源/去向，讓 CLI 間傳遞像在本機方法鏈接。
- LINQ 過濾: 在接收端對 IEnumerable 串流直接使用 LINQ 進行過濾與限制筆數。
- 一筆一處理: 堅持「取一筆、處理一筆、輸出一筆」的串流原則，維持穩定與低記憶體占用。
- 工具組合: 善用現成 CLI（gzip、clip 等）與程式碼混搭，避免重造輪子。
- 跨平台思維: .NET Core 配合 PowerShell 或 *nix shell，技巧同樣適用於跨網路與跨平台。
- 輕量解法: 不必動用大型框架，運用基礎知識與簡單技巧即可高效解決問題。

## 全文重點
本文延續先前 CLI + Pipeline 的實務經驗，說明如何在命令列工具間傳遞「物件」，並以 .NET 程式碼示範完整串流化處理。作者首先打破「STDIN/STDOUT 只能處理文字」的迷思，指出在 .NET 中它們本質為 Stream，能處理二進位資料；問題只是管線下一站未必能理解二進位，導致直接輸出到終端會亂碼，因此需要兩端協調格式。做法一是以 JSON 進行逐筆序列化與反序列化：生產端將 IEnumerable<DataModel> 逐筆寫出為 JSON 行，消費端以 JsonTextReader 支援多段內容逐筆還原，兩端皆以 IEnumerable 抽象來源/去向，使跨 CLI 的資料流看起來像同一段方法鏈，達到「拉式」串流。

進一步，若介意 JSON 體積或效率，可改以 BinaryFormatter 進行二進位序列化，同樣透過 Console.OpenStandardInput/Output 串流化處理；範例證實可無縫銜接。不過作者實測 1000 筆資料，JSON 產生約 108,893 bytes，BinaryFormatter 卻達 430,000 bytes，顯示二進位不必然更省，視型別與序列化器而定。故提出以 gzip 進行壓縮的管線組合：直接在 CLI 間以「producer | gzip -9 -c | gzip -d | consumer」傳遞，驗證可行且將輸出有效縮至約 47,064 bytes。作者強調「有槌子不見得每處都要敲」——既然是 CLI 生態，許多工作可交給現成工具，不必在程式裡重複實作。同場加映 Windows 的 clip.exe 可將 STDOUT 送進剪貼簿，展示 CLI 生態的便利。

在邏輯層，作者堅持串流處理原則：每筆獨立處理與輸出，能讓資料像在產線上不斷流動，減少等待與記憶體堆積。配合 C# 的 yield return 與 IEnumerable，接收端即可用 LINQ 在串流上做過濾與限制，例如範例以 where x.SerialNO % 7 == 0 再 Take(5) 僅處理特定筆數。此方式保留了串流的「延遲評估」，foreach 中斷即停止消耗後續資料。作者總結，良好設計 CLI I/O 規範與資料抽象，可讓你把熟悉的 C# 技能帶進命令列場景，與 PowerShell 或 *nix shell 自由組合，快速組裝高效率、可跨網路的資料處理流程，毋須大型框架也能優雅解決問題。

## 段落重點
### 透過 PIPELINE 傳遞物件 (Json)
作者指出 STDIN/STDOUT 在 .NET 是 Stream，可處理二進位資料；若管線兩端皆由你掌控，就能以序列化格式安全傳遞物件。示範以 IEnumerable<DataModel> 產生資料，生產端逐筆 JSON 序列化寫出，每筆一行，避免消費端需等待完整集合。接收端以 JsonTextReader 並開啟 SupportMultipleContent，逐筆反序列化並處理，同時再序列化回輸出，證實管線可自然串接。以 IEnumerable 做為跨 CLI 的抽象，讓「跨進程資料流」與「同進程方法串接」擁有一致開發體驗。此設計落實串流思維：資料逐筆進、逐筆處理、逐筆出，降低延遲與記憶體占用，也讓後續組合其他工具更彈性。

### 透過 PIPELINE 傳遞物件 (Binary)
若不滿意 JSON 的體積或速度，可改以 BinaryFormatter 進行二進位序列化。生產端以 Console.OpenStandardOutput 取得輸出串流，逐筆 formatter.Serialize；接收端以 Console.OpenStandardInput 逐筆 formatter.Deserialize 還原物件。雖然終端顯示成亂碼，不影響在管線內的正確傳遞與處理。實測顯示整體流程與 JSON 版同樣可順利運作。此處強調觀念：在管線中采取標準串流 API，選擇合適的序列化器即可交換格式，重點在兩端協議一致並遵守「一筆一處理」的串流原則。

### 透過 PIPELINE 傳遞物件 (Binary + GZip)
作者測試 1000 筆資料：JSON 約 108,893 bytes，而 BinaryFormatter 竟達 430,000 bytes，顯示二進位不必然更小。為降低跨網路或跨程序傳輸成本，示範以現成 gzip 工具壓縮 STDOUT：producer | gzip -9 -c -f > data.gz，檔案縮至約 47,064 bytes。再以 type data.gz | gzip -d | consumer 驗證解壓後仍能逐筆處理。最後以 producer | gzip -9 -c | gzip -d | consumer 整線演練，證實可行。作者提醒別一切都在程式中實作，CLI 生態已有成熟工具可直接組裝；並順帶分享 clip.exe 可將輸出送入剪貼簿，展現命令列工作流的高可組合性與高生產力。

### 使用 LINQ 過濾來自 PIPELINE 的物件
在接收端以 IEnumerable 與 yield return 串起資料流後，即可用 LINQ 直接對串流做查詢與篩選。作者示範將 ReceiveData() 作為查詢來源，使用 where x.SerialNO % 7 == 0 篩選 7 的倍數，再以 Take(5) 取前五筆並處理。由於 IEnumerable 僅單向、延遲評估，foreach 中途中斷即停止消耗後續資料，維持串流效率。此模式使得 CLI 間傳遞的物件能以熟悉的 C# 語法優雅操作，無需借助外部 grep/find，特別是在物件結構複雜或資料為二進位且經壓縮時，於程式內過濾更精準也更實用。

### 小結
本文主張以簡馭繁：不必倚賴龐大框架，透過正確的抽象與基礎功即可打造強韌的 CLI 資料管線。關鍵做法包括：把 STDIN/STDOUT 視為 Stream、逐筆序列化（JSON/Binary）、必要時以 gzip 壓縮、以 IEnumerable 封裝資料流並配合 yield return 與 LINQ 實作串流化處理與過濾。再配合既有命令列工具（如 gzip、clip），能快速建構跨程序、可跨網路的高效資料處理流程。核心精神在於：清楚定義輸入輸出與處理邏輯，善用現有工具與語言特性，讓日常開發用最小成本取得穩定且可擴充的效果。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本 CLI 與 Shell 概念：STDIN/STDOUT/PIPELINE、命令串接與重導向
   - .NET I/O 與序列化基礎：Stream 與 TextReader/TextWriter 的差異、JSON/Binary 序列化
   - C# 迭代與集合：IEnumerable<T>、yield return、LINQ 基本操作
   - 基本壓縮工具：gzip 的使用與管線操作

2. 核心概念：
   - 以 Stream 為核心的 CLI 資料傳遞：STDIN/STDOUT 可處理二進位不僅是文字
   - 物件序列化跨 CLI 傳遞：JSON 與 Binary 的取捨（可讀性、體積、效率）
   - 串流處理原則：一筆一筆處理與輸出，維持生產線式流水
   - 抽象化資料來源：以 IEnumerable<T> 把跨 CLI 的資料流抽象為可枚舉序列
   - LINQ 於串流的過濾與截斷：在消費端用 LINQ 做條件過濾與 Take 等操作

3. 技術依賴：
   - .NET Console 與 Stream：Console.OpenStandardInput/Output 與 Json/Binary 序列化器
   - 序列化器選擇：JsonSerializer vs BinaryFormatter（以及可選的壓縮層）
   - 外部工具整合：gzip 於管線中壓縮/解壓；Windows clip.exe 輔助輸出
   - Shell/PowerShell：命令管線對接，跨程序資料流動

4. 應用場景：
   - 以多個 CLI 組合的資料處理流水線（生產線式加工）
   - 跨主機（如 SSH）以標準輸入輸出串接的遠端處理
   - 在消費端快速篩選上游資料（LINQ）避免多餘處理
   - 壓縮大流量資料的管線傳輸（節省網路/磁碟空間）
   - 用簡單工具（clip、gzip）提升開發與運維日常效率

### 學習路徑建議
1. 入門者路徑：
   - 理解 STDIN/STDOUT/PIPELINE 與重導向基礎
   - 練習用 Console.In/Out 讀寫純文字
   - 以 System.Text.Json 實作單筆物件序列化/反序列化到標準輸入輸出
   - 將資料來源與接收端封裝為 IEnumerable<T> + yield return

2. 進階者路徑：
   - 改寫為逐筆 JSON 行（NDJSON 風格），支援多筆內容解析
   - 將消費端加入 LINQ where/take 等串流過濾
   - 導入二進位序列化實作（並理解與比較體積與效能差異）
   - 在管線加入 gzip 壓縮/解壓，觀察檔案大小與端到端效應

3. 實戰路徑：
   - 規劃上游 CLI 產出物件序列與下游多階段處理 CLI
   - 為每階段定義清晰的輸入輸出契約（JSON Schema 或版本欄位）
   - 實測在本機與遠端（SSH）環境，以 gzip/並行化優化吞吐
   - 加入日誌與錯誤處理，確保中途中斷能優雅停止或續傳

### 關鍵要點清單
- 以 Stream 思維看待 STDIN/STDOUT：不僅是文字，能安全傳遞二進位資料（優先級: 高）
- 單筆序列化逐行輸出（NDJSON 型式）：避免需完整載入全部資料才可解析（優先級: 高）
- IEnumerable<T> + yield return 抽象資料流：讓跨 CLI 的資料像本機序列一樣操作（優先級: 高）
- LINQ 串流過濾與截斷：where/Take 搭配 foreach 即時消費，省資源（優先級: 高）
- JSON vs Binary 取捨：JSON 可讀好整合，Binary 可能更快但不易除錯（優先級: 高）
- 管線分工借力工具：用 gzip 等現成 CLI 實現壓縮等過程（優先級: 中）
- 支援多筆 JSON 的解析技巧：JsonTextReader.SupportMultipleContent（優先級: 中）
- 生產線式設計原則：一筆進一筆出，避免批次積壓與記憶體爆量（優先級: 高）
- 遠端管線傳輸思維：SSH 等將 STDIO 跨網，壓縮可顯著降成本（優先級: 中）
- CLI 之間的契約穩定：明確定義物件欄位與版本，避免反序列化失敗（優先級: 高）
- 簡捷小工具提升效率：clip 把結果送剪貼簿、tasklist 管線查詢（優先級: 低）
- 日誌與可觀測性：在每階段輸出處理開始/結束資訊助於追蹤（優先級: 中）
- 緩衝與背壓考量：管線中會有 buffer，注意上下游速率差（優先級: 中）
- 錯誤處理與恢復：逐筆處理便於跳過壞件與持續前進（優先級: 中）
- 跨平台 Shell 差異：PowerShell 能傳遞物件，傳統 *nix shell 偏文字（優先級: 低）