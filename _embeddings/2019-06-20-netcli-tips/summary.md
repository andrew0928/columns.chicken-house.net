# 後端工程師必備: CLI 傳遞物件的處理技巧

## 摘要提示
- Pipeline物件傳遞: STDIN/STDOUT 本質為 Stream，可配合序列化在 CLI 之間傳送複雜物件。
- Json序列化: 逐筆 Json 輸出並逐筆還原，可避免一次載入全部資料的記憶體負擔。
- BinaryFormatter: 改用二進位序列化可降低 CPU 耗用，但檔案體積不一定較小。
- GZip壓縮: 善用現成 gzip 工具即可在 Pipeline 中壓縮/解壓資料，大幅縮小傳輸量。
- IEnumerable串流: 以 yield return 把 CLI 內部邏輯也變成串流，維持「邊讀邊處理」。
- LINQ過濾: 對 ReceiveData() 直接套用 LINQ 查詢即可在程式端快速篩選目標物件。
- CLI組合: dotnet CLI + gzip + clip 等指令可隨意拼裝，靈活完成跨網路或本機資料流。
- PowerShell對比: PowerShell 內建物件管線很方便，自製 CLI 亦能用相同概念達成。
- 開發心法: 先理解基礎 I/O 與串流概念，再選擇最簡單工具解決問題，無須動用大框架。
- 實務建議: 將輸入輸出規格抽象化，以標準格式與流程設計，後續擴充與整合最省力。

## 全文重點
作者以 .NET Core 範例說明 CLI 間如何傳遞自訂物件。核心觀念是：STDIN 與 STDOUT 都是位元流，只要將物件序列化成適合的格式並逐筆輸出，就能像 PowerShell 一樣在 Pipeline 內傳遞物件而非純文字。文章先以 JsonSerializer 把 DataModel 物件逐筆寫出，接收端用 JsonTextReader 設定 SupportMultipleContent 逐筆還原，證明資料可邊讀邊處理。若擔心 Json 體積大，可改 BinaryFormatter；若需跨網路傳輸再加上 gzip，透過「dotnet CLI | gzip -9 | …」即可完成壓縮傳遞。因所有方法都以 IEnumerable<DataModel> 為介面，既能保留串流特性，也方便於程式內再套用 LINQ，像「where x.SerialNO % 7 == 0」這類查詢可一行解決。文末作者提醒，不必一開始就使用龐大框架，熟悉基礎 I/O、序列化與現成 CLI 工具，再配合 C# 語言特性，就能快速構建高效、可組合、易維護的後端處理流程。

## 段落重點
### 前言與範疇說明
作者延續前篇「CLI + PIPELINE 開發技巧」，補充多個實用小技巧；聚焦於物件在命令列管線中的傳遞與過濾，並示範如何把 LINQ 串流思維與作業系統的 Pipeline 結合，強調用簡單工具就能打造靈活後端流程。

### 透過 PIPELINE 傳遞物件 (Json)
說明 STDIO 層級屬於 Stream，可傳遞任何位元資料。示範將 IEnumerable<DataModel> 逐筆以 JsonSerializer 寫出，接收端用 JsonTextReader.SupportMultipleContent 逐筆反序列化，再呼叫自訂 ProcessPhase1() 處理，成功於 Windows Shell 建立「dotnet CLI-DATA | dotnet CLI-P1」的物件管線。

### 透過 PIPELINE 傳遞物件 (Binary)
若對 Json 體積或效能不滿，可改用 BinaryFormatter。程式僅需將 JsonSerializer 換成 BinaryFormatter，並直接使用 Console.OpenStandardOutput()／Input()。實測輸出可正常被下一段 CLI 讀取並處理；但檔案大小反而增至約 430 KB，顯示二進位未必最省空間。

### 透過 PIPELINE 傳遞物件 (Binary + GZip)
為解決傳輸量問題，引入 gzip。示範「dotnet CLI-DATA | gzip -9 -c」產生 data.gz，體積降為約 47 KB，再以「type data.gz | gzip -d | dotnet CLI-P1」驗證可以邊解壓邊處理。整套流程可串成四個 Process，且 Windows 亦可透過 clip.exe 把指令輸出直接送至剪貼簿，增加便利性。

### 使用 LINQ 過濾來自 PIPELINE 的物件
因 ReceiveData() 回傳 IEnumerable<DataModel>，可直接套用 LINQ。範例以 「from x in ReceiveData() where x.SerialNO % 7 == 0 select x).Take(5)」 篩出序號為 7 的倍數且僅取前五筆，隨後送入 ProcessPhase1()。保留串流特性，當條件滿足即停止後續讀取，有效節省資源。

### 小結
整篇強調「小工具、大威力」：只要理解 Stream、序列化與 Pipeline，本地或遠端都能透過簡短 CLI 組合完成複雜資料處理；配合 C# 的 yield 與 LINQ，更可保持程式碼可讀性與彈性。作者鼓勵開發者先把基礎打好，再選最符合場景的輕量解法，才能寫出高效率且易維護的後端程式。