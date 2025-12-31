---
layout: synthesis
title: "後端工程師必備: CLI 傳遞物件的處理技巧"
synthesis_type: faq
source_post: /2019/06/20/netcli-tips/
redirect_from:
  - /2019/06/20/netcli-tips/faq/
postid: 2019-06-20-netcli-tips
---

# 後端工程師必備: CLI 傳遞物件的處理技巧

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 CLI 的 Pipeline？
- A簡: Pipeline 以 STDIN/STDOUT 串接多個程式，用串流方式逐筆處理資料，形成可組合的處理鏈。
- A詳: CLI 的 Pipeline 是以作業系統將前一個程式的標準輸出（STDOUT）接到下一個程式的標準輸入（STDIN），讓多個工具以串流方式逐筆處理、逐步轉換資料。其優點包含：鬆耦合、可重用、能應對大量資料、易以外部工具（如 gzip、grep）擴充流程。只要遵守逐筆處理的設計，便能像工廠生產線般持續輸出結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q6, B-Q5

A-Q2: STDIN/STDOUT 與 TextReader/TextWriter 有何差異？
- A簡: STDIN/STDOUT 是位元流（Stream）層級，可處理二進位；TextReader/Writer 為文字層級。
- A詳: 在 .NET 中，STDIN/STDOUT 位於 Stream 層級，能處理二進位資料；而 TextReader/TextWriter 屬文字抽象，會牽涉編碼與字元轉換。若僅用文字 API，往往誤以為只能傳文字。掌握 STDIN/STDOUT 的流本質，即可在 CLI 間傳遞 JSON、二進位或壓縮資料，兼顧效率與相容性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, D-Q1

A-Q3: 為什麼 CLI 可以傳遞二進位資料？
- A簡: 因為 STDIN/STDOUT 是 Stream，天然能承載任意位元資料，而非只能文字。
- A詳: Pipeline 接面在 OS 層是位元流，故能承載任何資料型態（影像、序列化物件、壓縮檔等）。唯一風險是若直接把二進位吐到終端機，螢幕會顯示亂碼且可能觸發控制碼。實務上要保證下游能正確解碼，或將輸出重導到檔案/另一程式處理，避免對人類使用者展示。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, B-Q13

A-Q4: 什麼是「透過 Pipeline 傳遞物件」？
- A簡: 將物件序列化為 JSON 或二進位，經 STDOUT 傳下游，於 STDIN 反序列化還原。
- A詳: 物件無法直接穿越進程邊界，需序列化為可傳輸的位元流（如 JSON、Binary、壓縮後）。上游以序列化寫至 STDOUT，下游由 STDIN 解出還原為物件。文章以 Json.NET 與 BinaryFormatter 示範，並透過逐筆輸出 JSON（每物件一行）或連續二進位區塊，達成跨 CLI 的物件傳遞。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, C-Q1

A-Q5: JSON 與 Binary 序列化的差異？
- A簡: JSON 可讀性佳、體積可能較小；Binary 通常更快但可讀性差且相容性受限。
- A詳: JSON 屬文字格式，跨語言相容、除錯易、可逐行書寫並利於串流；但包含 Base64 二進位欄位時可能膨脹。Binary 格式可避免字串編碼開銷，通常更快，但不利跨語言、版本脆弱，若採用 BinaryFormatter 亦有安全疑慮。文章測得 1000 筆資料 JSON 約 108,893 bytes、Binary 約 430,000 bytes。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q6, D-Q9

A-Q6: PowerShell 物件管線與傳統 *nix 文字管線差在哪？
- A簡: PowerShell 原生傳遞物件；傳統 shell 傳文字。PowerShell 下游可直接取屬性。
- A詳: *nix shell 歷史悠久，多以文字行為單位；PowerShell 較新，將物件作為一等公民，管線中的每個節點接收/輸出 .NET 物件。若自建 CLI 工具鏈，亦可模擬此體驗：以 JSON/二進位序列化穿越管線，下游反序列化後即是強型別物件，利於複雜邏輯與靈活查詢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1, C-Q9

A-Q7: 為什麼要在 CLI 中處理物件而非純文字？
- A簡: 物件保留結構與型別，處理複雜資料更穩定，減少脆弱的字串解析。
- A詳: 純文字需大量字串處理與正則解析，對結構化資料易脆弱且維護成本高。以物件傳遞可保留欄位與型別，利於 LINQ 過濾、分段處理與重用既有商業邏輯。透過序列化與反序列化，可在 CLI 間建立高可讀、高可測的資料流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q7, C-Q3

A-Q8: 什麼是 IEnumerable<T> 在串流處理中的角色？
- A簡: IEnumerable<T> 提供延遲、逐筆的 Pull 型迭代，適合管線串流處理。
- A詳: IEnumerable<T> 搭配 yield return 能讓生產端按需產出元素；消費端 foreach 進度即驅動上游持續生產。這種 Pull 型串流使記憶體占用低、可早出結果、可中途 break 停止後續處理。文章以 GenerateData()/ReceiveData() 回傳 IEnumerable<DataModel> 展示此模式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q25, C-Q2

A-Q9: LINQ 在串流資料中的意義？
- A簡: LINQ 能以查詢語法對 IEnumerable 逐筆過濾、轉換，保持延遲求值。
- A詳: 對 IEnumerable 的 LINQ（Where、Select、Take 等）不會預先把資料載入記憶體，而是在枚舉過程逐筆套用條件。這非常適合管線式處理，例如只取 SerialNO 為 7 的倍數且僅前 5 筆，再交給後續階段。好處是省記憶體、可早停、好組合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, B-Q7, B-Q22

A-Q10: 為何選擇「每行輸出一個 JSON 物件」？
- A簡: 便於串流消費與邊讀邊處理，避免需待完整陣列才能開始。
- A詳: 若以陣列包裹所有物件，下游需等整體 JSON 完成並解析整塊，才開始處理，延遲高且耗記憶體。逐行吐出每個 JSON 物件則可邊讀邊反序列化、立即處理與輸出，實現真正流水線行為，也利於與其他文字工具（grep、head）搭配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q1, D-Q8

A-Q11: JsonTextReader.SupportMultipleContent 是什麼？
- A簡: 它允許連續 JSON 內容串接於同一輸入流時，逐筆讀取反序列化。
- A詳: Json.NET 的 JsonTextReader 預設期待單一 JSON 文檔。將 SupportMultipleContent 設為 true 後，可在同一串流連續出現多份 JSON（如每行一個物件），reader.Read() 會逐段解析，讓下游以 while/read 模式不斷反序列化每個物件，與逐筆輸出相配合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, D-Q2

A-Q12: 為何要考慮壓縮（gzip）？
- A簡: 跨網路或大量資料時，壓縮能顯著降低傳輸體積與時間成本。
- A詳: 文章以 1000 筆資料測得：JSON 約 108,893 bytes，Binary 約 430,000 bytes；若再經 gzip，二進位輸出壓至約 47,064 bytes。當透過 ssh 等將 STDIO 跨機傳遞時，壓縮可降低頻寬與等待時間。CLI 容易引入 gzip 等現成工具，快速改善效能而不侵入程式碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q5, D-Q7

A-Q13: 什麼是 Pipeline Buffer 與背壓（backpressure）現象？
- A簡: OS 為管線提供有限緩衝；消費端慢時生產端會被阻塞或快速結束。
- A詳: 管線兩端速率不同時，OS 以 Pipe Buffer 暫存資料。若消費端慢，生產端寫滿緩衝即被阻塞；若生產端很快完成輸出（如 CLI-DATA），則迅速結束，但資料仍在管線緩衝等待後續消費。理解此現象有助診斷「看似當機」或出現延遲的行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, D-Q3

A-Q14: 在 Windows 與 Linux 使用這些技巧有何差異？
- A簡: 概念相同；工具供應差異（如 gzip、clip），PowerShell/ssh 可補足。
- A詳: Pipeline 與 STDIO 本質跨平台一致。Linux 原生具備豐富 CLI 工具；Windows 可用 PowerShell、Git for Windows 中的 gzip、OpenSSH。關鍵在資料格式與串流模式，不在 OS。妥善設計後，同一 CLI 串流策略可在多平台運作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q9, B-Q9

A-Q15: 安全性：BinaryFormatter 為何需謹慎？
- A簡: BinaryFormatter 具已知風險且已被標示不建議使用，不可反序列化不信任資料。
- A詳: BinaryFormatter 對型別資料進行深度序列化，歷來有反序列化攻擊風險，.NET 新版已標示為 obsolete。不應處理外部或不信任來源；建議改用 System.Text.Json、DataContractJsonSerializer、MessagePack、ProtoBuf 等更安全、跨語言佳的格式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q17, D-Q9, C-Q4

A-Q16: 抽象化 GenerateData()/ReceiveData() 的價值？
- A簡: 抽象回傳 IEnumerable<DataModel>，可在跨 CLI 邏輯中重用與測試。
- A詳: 將生產與消費資料的細節（序列化/反序列化/STDIO）封裝在方法內，對外只暴露 IEnumerable<DataModel>，能讓應用邏輯像處理本機集合一樣組合 LINQ、分層測試、替換來源（檔案/網路/記憶體），提升可維護性與可測性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q2, C-Q3

A-Q17: DataModel 的結構與意圖是什麼？
- A簡: 含 ID、SerialNO、Stage、Buffer 等欄位，用於示範序列化與流程階段。
- A詳: 範例的 DataModel 具備字串 ID、序號 SerialNO、處理階段 Stage（枚舉）與位元組陣列 Buffer。這些欄位讓 JSON/Binary 序列化與壓縮的差異明顯，亦便於展示流程內狀態變更與 LINQ 過濾（如序號為 7 倍數）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q3, B-Q1

A-Q18: 為何示範用 Guid 與 Random.NextBytes？
- A簡: 產生唯一 ID 與隨機 Buffer，便於觀察序列化體積與處理行為。
- A詳: Guid.NewGuid() 生成獨特識別，Random.NextBytes() 產生隨機內容使序列化輸出更接近真實資料（包含二進位），便於比較 JSON Base64 與 Binary 的體積與效能、壓縮效果，並確保每筆資料可追蹤處理日誌。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q12

A-Q19: IEnumerable 單向巡覽一次有何影響？
- A簡: 只能前進且消耗式，利於低記憶體，但需小心重複枚舉與副作用。
- A詳: IEnumerable 每次 MoveNext() 都可能觸發上游計算/IO，屬消耗式串流。優點是低占用、可早停；但重複迭代會重做工作，且中途副作用（如寫檔、寫網路）不可逆。設計時避免在查詢與副作用混雜、明確界定資料流邊界。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q25, C-Q10

A-Q20: 何時用外部 CLI（gzip、grep、clip），何時自己寫程式？
- A簡: 簡單通用任務交給 CLI；結構化/型別敏感邏輯由程式處理。
- A詳: 壓縮、搜尋純文字、重導等通用任務可直接用現成 CLI，提高開發效率。涉及複雜結構化資料、型別安全、跨版本契約、商業規則與安全需求，則應在程式中以物件操作。善用兩者優勢，可快速構建可靠、可維護的處理鏈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q5, C-Q6

---

### Q&A 類別 B: 技術原理類

B-Q1: JSON 物件在管線中如何運作？
- A簡: 上游逐筆序列化 JSON 到 STDOUT，下游以 JsonTextReader 多文檔模式逐筆還原。
- A詳: 技術原理說明：使用 Json.NET 的 JsonSerializer 逐筆 Serialize(model) 到 Console.Out，並在每筆後換行。下游以 JsonTextReader 包裝 Console.In，將 SupportMultipleContent 設為 true，搭配 while (reader.Read()) 與 json.Deserialize<T>(reader) 逐筆取得物件。關鍵步驟：逐筆輸出、換行分隔、Reader 多文檔設定。核心組件：JsonSerializer、JsonTextReader、Console.In/Out。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, C-Q1

B-Q2: Binary 序列化在管線中如何運作？
- A簡: 以 BinaryFormatter 將物件寫入 STDOUT，下游從 STDIN 連續反序列化。
- A詳: 技術原理說明：Console.OpenStandardOutput() 取得 Stream，BinaryFormatter.Serialize(stream, model) 連續寫入；下游以 Console.OpenStandardInput()，在迴圈中 formatter.Deserialize(stream) 還原 DataModel。關鍵步驟：直接操作 Stream、連續寫入/讀取物件。核心組件：BinaryFormatter、StandardInput/Output Stream。注意：BinaryFormatter 現已不建議用於不信任資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q15, C-Q4

B-Q3: 在管線中如何加入 gzip 壓縮/解壓？
- A簡: 以現成 gzip.exe 夾在兩端中間，壓縮輸出或解壓輸入以減少傳輸體積。
- A詳: 技術原理說明：管線本質是位元流連接。將 dotnet CLI-DATA.dll | gzip -9 -c -f 將上游壓縮；下游以 gzip -d | dotnet CLI-P1.dll 解壓後再反序列化。關鍵步驟：在 OS 管線嵌入工具、設定壓縮等級、保留串流連續性。核心組件：gzip.exe、STDIO、兩端序列化器。也可改用 .NET 的 GZipStream 內建類別。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, C-Q5, C-Q6

B-Q4: ReceiveData() 的設計原理是什麼？
- A簡: 以 IEnumerable<T> 包裝反序列化迭代，透過 yield return 逐筆輸出。
- A詳: 技術原理說明：將 Console.In/Stream 包裝成讀取器（JsonTextReader 或 Stream），while 迴圈持續讀，反序列化為 DataModel 後 yield return。關鍵步驟：建立 reader、讀取條件、逐筆產出、結束條件。核心組件：IEnumerable<T>、yield return、序列化器/Reader。此設計讓上層用 foreach 即可串流消費。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, C-Q2, B-Q25

B-Q5: OS 層的 Pipeline 是如何把程式串起來的？
- A簡: 前程式 STDOUT 與後程式 STDIN 由 OS pipe 連接，資料以 FIFO 緩衝傳遞。
- A詳: 技術原理說明：建立管線時，OS 建立匿名 pipe，將前進程的標準輸出檔案描述符連到 pipe 寫端，後進程的標準輸入連到讀端。關鍵步驟：建立 pipe、子行程繼承、重導 IO。核心組件：pipe 緩衝、檔案描述符/Handle、STDIO。此設計帶來背壓與緩衝限制，需配合串流策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q3

B-Q6: 逐行 JSON 與陣列 JSON 的解析流程差異？
- A簡: 逐行可即時反序列化；陣列需完整讀畢再解析整批，延遲與記憶體較高。
- A詳: 技術原理說明：逐行每個 JSON 物件可在 reader.Read() 發現新 token 即還原；陣列需等到配對的結束括號，且內含逗號與空白處理。關鍵步驟：分段界線（換行 vs 結尾）判定。核心組件：JsonTextReader 流式讀取、SupportMultipleContent。逐行利於管線與 LINQ 邊讀邊過濾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q11, D-Q8

B-Q7: LINQ 在處理串流資料的機制？
- A簡: 延遲求值，Where/Select 會包裝迭代器，逐筆過濾與轉換。
- A詳: 技術原理說明：LINQ to Objects 為 IEnumerable 擴充方法，回傳新的迭代器物件，當 foreach 觸發 MoveNext() 時才執行條件與投影。關鍵步驟：建立迭代器、鏈式包裝、終端操作驅動。核心組件：IEnumerable、迭代器狀態機、yield。可輕易加入 Take、Skip 等控制數量與早停。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q3, B-Q25

B-Q8: 管線中日誌輸出應如何設計？
- A簡: 建議資料走 STDOUT，日誌走 STDERR，避免混雜破壞下游解析。
- A詳: 技術原理說明：將結構化資料輸出固定使用 STDOUT；日誌/診斷信息輸出到 STDERR。關鍵步驟：程式內分離通道、併用重導（> 與 2>）。核心組件：Console.Out、Console.Error、OS 重導語法。這可避免 JSON/二進位被日誌污染，維持可組合性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q10, C-Q7

B-Q9: 為何 ssh 能讓管線跨網路？
- A簡: ssh 會把遠端程式的 STDIO 綁定到本地連線，使管線像本機般運作。
- A詳: 技術原理說明：ssh 在本機與遠端建立加密通道，將遠端命令的 STDIN/STDOUT/STDERR 綁到通道上，本地可像讀寫檔案般串接。關鍵步驟：ssh 連線、命令執行、IO 轉發。核心組件：ssh client/server、PTY/非交互模式。配合 gzip 等壓縮可顯著提升跨網效率。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, C-Q9

B-Q10: clip.exe 的工作機制？
- A簡: 接收 STDIN 並寫入 Windows 剪貼簿，便於把命令輸出貼到應用程式。
- A詳: 技術原理說明：clip.exe 讀取標準輸入的文字內容，透過 Win32 剪貼簿 API 設置到系統剪貼簿。關鍵步驟：pipeline 重導、clip 取流、設置剪貼簿。核心組件：STDIN、剪貼簿 API。典型用法：tasklist | clip，快速把查詢內容複用到其他工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q8

B-Q11: Json.NET 與 System.Text.Json 在串流上的考量？
- A簡: Json.NET 功能成熟，支援多文檔；System.Text.Json 輕量快速，串流需對應 API。
- A詳: 技術原理說明：Json.NET 提供 JsonTextReader.SupportMultipleContent 便於多物件串流；System.Text.Json 具 Utf8JsonReader/序列化器，亦支援序列化/反序列化與逐段讀寫。關鍵步驟：選擇能支援逐筆處理的 API。核心組件：JsonSerializer、Utf8JsonReader。兩者皆可達成逐筆 JSON 管線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q1

B-Q12: 影響序列化效能與體積的因素？
- A簡: 欄位內容（如 Base64）、格式特性、壓縮、序列化器實作均會影響。
- A詳: 技術原理說明：JSON 對二進位欄位需 Base64，體積膨脹；Binary 省去文字編碼但受型別版本影響。壓縮對高熵/低熵資料效果不同。序列化器選擇（Json.NET、System.Text.Json、MessagePack）對 CPU/體積有顯著差異。關鍵步驟：以實測數據評估。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q12, D-Q5

B-Q13: 為何不應把二進位直接輸出到終端機？
- A簡: 會顯示亂碼、可能觸發控制碼，且無法被人類閱讀或安全處理。
- A詳: 技術原理說明：終端機期待文字與控制序列，遇二進位可能亂碼、改變狀態（鈴聲/色彩/游標）。關鍵步驟：把二進位導向檔案或下一個程式，不直接呈現。核心組件：終端機編碼、控制碼。避免誤導使用者與破壞顯示。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, D-Q1

B-Q14: 管線緩衝與流程控制如何影響效能？
- A簡: 緩衝可平滑速率差，但過小會頻繁阻塞；過大浪費記憶體且延遲清空。
- A詳: 技術原理說明：OS pipe 具固定容量；生產端快於消費端時會阻塞寫入；消費端快則等待讀取。關鍵步驟：控制每筆大小、壓縮、降低每筆處理時間、必要時分段。核心組件：pipe buffer、進程調度。良好串流設計可穩定吞吐。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q3

B-Q15: 多階段管線的設計考量？
- A簡: 清晰的介面契約、單一職責、錯誤與日誌分流、可組合與測試。
- A詳: 技術原理說明：每一階段僅關注轉換一件事，定義輸入/輸出格式契約（版本、相容），利用 STDOUT/STDERR 分流，維持可串接。關鍵步驟：介面設計、錯誤處理、資源釋放。核心組件：序列化格式、IEnumerable、外部工具鏈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, A-Q16, D-Q10

B-Q16: 資料契約與版本相容如何管理？
- A簡: 明確版本化 DataModel，避免破壞性變更；跨語言優先採中立格式。
- A詳: 技術原理說明：Binary 格式強耦合型別版本；JSON 較寬鬆、可新增欄位。關鍵步驟：加欄位預設與相容策略、標示版本、為反序列化提供後備處理。核心組件：序列化設定、相容測試。跨團隊建議用 JSON/Protobuf/MessagePack。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q5, D-Q6

B-Q17: 反序列化安全風險與防護機制？
- A簡: 不信任輸入可能觸發攻擊；需白名單型別、限制解析器、驗證資料。
- A詳: 技術原理說明：特別是 BinaryFormatter 可被精心構造 payload 利用。關鍵步驟：避免 BinaryFormatter、使用安全序列化器、設定型別白名單、限制自動型別解析、對資料做 Schema 驗證。核心組件：序列化器設定、安全審核。原則：永不信任外部輸入。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, D-Q9

B-Q18: 枚舉器中例外（Exception）如何影響上游/下游？
- A簡: MoveNext() 擲出例外會中斷迭代，可能遺漏釋放，需確保 finally 清理資源。
- A詳: 技術原理說明：IEnumerable 的 MoveNext() 是實際執行點。例外會終止迭代並冒泡至呼叫端。關鍵步驟：用 using/finally 確保 Reader/Stream 關閉、對單筆失敗做重試/略過策略。核心組件：迭代器狀態機、IDisposable。設計要能局部失敗不中斷整體。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q3, C-Q10

B-Q19: 如何判斷串流結束？
- A簡: 文字流靠 Read() 返回 false；二進位 Deserialize 需偵測 EOF 或捕捉例外。
- A詳: 技術原理說明：JsonTextReader.Read() 於 EOF 回 false；BinaryFormatter 在到 EOF 時常以例外結束，需辨識 Stream.CanRead 已無資料或捕捉 SerializationException。關鍵步驟：明確結束條件、避免無限迴圈。核心組件：Reader 介面、Stream 屬性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, D-Q2

B-Q20: 為何 JSON 更利於跨語言/跨平台？
- A簡: 文字開放格式、工具與庫廣泛、對版本變更較寬容。
- A詳: 技術原理說明：JSON 是語言不可知的資料表示，幾乎所有平台具備穩定庫與工具；新增欄位通常不破壞舊版解析。關鍵步驟：定義清晰 Schema、加入預設值策略。核心組件：JSON 序列化器、Schema 驗證。適用於需與非 .NET 工具鏈協作的場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q16

B-Q21: 壓縮應放在何層實作較佳？
- A簡: 以外部 CLI 快速驗證與整合；若需封裝則在應用加入 GZipStream。
- A詳: 技術原理說明：外部 gzip 工具零侵入、易組合；應用層 GZipStream 可跨平台部署一致且免依賴外部工具。關鍵步驟：先用 CLI 驗證收益，再決定內建化。核心組件：gzip.exe、GZipStream、管線重導。依部署與可控性取捨。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q6

B-Q22: Take(5) 如何在串流中早停？
- A簡: Take 會在取得指定數量後停止枚舉，立即終止上游後續讀取。
- A詳: 技術原理說明：Take 產生包裝迭代器，內部計數達閾值後 MoveNext() 回傳 false，進而停止驅動上游。關鍵步驟：正確放置 Take 在查詢鏈，避免先 materialize。核心組件：LINQ 迭代器、MoveNext()。用於限制處理量、快速預覽與抽樣。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q3

B-Q23: JsonTextReader.SupportMultipleContent 的底層行為？
- A簡: 在遇到多個根級 JSON 時，允許一次一個地解析各自的 token 樹。
- A詳: 技術原理說明：啟用後，reader 會在完成一個完整 JSON 後停下，等待下一次 Read() 開始解析下一個根節點，不要求整個流只能有一個根。關鍵步驟：循環呼叫 Read()、在邊界點進行 Deserialize。核心組件：Json.NET Tokenizer。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q11, B-Q1

B-Q24: 為何逐筆輸出時建議每筆後寫入換行？
- A簡: 換行提供人類可讀與工具友善的界線，便於排錯與外部工具處理。
- A詳: 技術原理說明：雖 SupportMultipleContent 可不靠換行，加入換行能讓 head/tail/grep 等工具輕鬆操作、並於人類目視檢查時清晰。關鍵步驟：Serialize 後 Console.Out.WriteLine()。核心組件：文本邊界、UNIX 工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q6

B-Q25: foreach 與串流資料的驅動關係？
- A簡: foreach 的 MoveNext() 會驅動上游產出下一筆，是 Pull 模式。
- A詳: 技術原理說明：在 IEnumerable 模式下，消費端控制節奏。只有當 foreach 需要下一筆資料時，上游才會從 STDIN 讀、反序列化並傳遞。關鍵步驟：把高成本操作延後到枚舉點。核心組件：IEnumerable、迭代器。利於後續早停與節流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q7, C-Q3

---

### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何實作「每行一筆 JSON」的輸出 CLI？
- A簡: 用 Json.NET Serialize(model) 到 Console.Out，逐筆後加 WriteLine()。
- A詳: 具體步驟：1) 建立 JsonSerializer；2) foreach 逐筆產生 DataModel；3) json.Serialize(Console.Out, model)；4) Console.Out.WriteLine()。程式碼：
  JsonSerializer json = JsonSerializer.Create();
  foreach (var m in GenerateData()) { json.Serialize(Console.Out, m); Console.Out.WriteLine(); }
  注意：資料與日誌分道；保留逐筆輸出。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q10, A-Q17

C-Q2: 如何實作「逐筆接收 JSON」的 ReceiveData()？
- A簡: 建立 JsonTextReader 包裝 Console.In，開啟 SupportMultipleContent，yield 反序列化。
- A詳: 步驟：1) var reader = new JsonTextReader(Console.In){SupportMultipleContent=true}; 2) while(reader.Read()) yield return serializer.Deserialize<DataModel>(reader); 程式碼：
  var s = JsonSerializer.Create(); var r = new JsonTextReader(Console.In){SupportMultipleContent=true};
  while (r.Read()) yield return s.Deserialize<DataModel>(r);
  注意：EOF 結束、將錯誤寫 STDERR、釋放 Reader。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q19, B-Q4

C-Q3: 如何以 LINQ 過濾 SerialNO 為 7 倍數且只處理前 5 筆？
- A簡: 在 ReceiveData() 上套 Where 與 Take(5)，再 foreach 處理。
- A詳: 步驟：1) var q = from x in ReceiveData() where x.SerialNO%7==0 select x; 2) foreach (var m in q.Take(5)) ProcessPhase1(m); 程式碼：
  foreach (var m in (from x in ReceiveData() where x.SerialNO%7==0 select x).Take(5)) { ProcessPhase1(m); }
  注意：延遲求值會早停；避免副作用混雜查詢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q22, B-Q7

C-Q4: 如何改為二進位序列化（示範 BinaryFormatter）？
- A簡: 上游 BinaryFormatter.Serialize(StdOut)；下游 Deserialize(StdIn) 逐筆讀。
- A詳: 步驟：上游：
  var f=new BinaryFormatter(); using var os=Console.OpenStandardOutput();
  foreach(var m in GenerateData()) f.Serialize(os,m);
  下游：
  var f=new BinaryFormatter(); using var ins=Console.OpenStandardInput();
  while(true){ yield return (DataModel)f.Deserialize(ins); }
  注意：BinaryFormatter 已不建議用於不信任資料；可考慮 MessagePack/Protobuf。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q2, D-Q6

C-Q5: 如何用 gzip.exe 壓縮/解壓整段管線？
- A簡: 以外部工具夾在中間：上游 | gzip -9 -c -f | gzip -d | 下游。
- A詳: 步驟：1) 產生：dotnet CLI-DATA.dll | gzip -9 -c -f > data.gz；2) 消費：type data.gz | gzip -d | dotnet CLI-P1.dll；3) 串起來：dotnet ... | gzip -9 -c -f | gzip -d | dotnet ...。注意：Windows 可用 Git for Windows 的 gzip，確認 PATH；測試體積效益。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, A-Q12, A-Q14

C-Q6: 不依賴外部工具，如何用 GZipStream 實作壓縮/解壓？
- A簡: 以 GZipStream 包裝標準輸入/輸出 Stream，讀寫時自動壓縮/解壓。
- A詳: 步驟：上游輸出壓縮：
  using var os=Console.OpenStandardOutput();
  using var gz=new GZipStream(os,CompressionLevel.Optimal);
  formatter.Serialize(gz,m);
  下游解壓：
  using var ins=Console.OpenStandardInput();
  using var gz=new GZipStream(ins,CompressionMode.Decompress);
  迴圈 Deserialize(gz)。
  注意：正確 Flush/Dispose；與 JSON 串流需自行界線管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q21, B-Q3

C-Q7: 如何正確分流資料與日誌（避免污染 JSON/二進位）？
- A簡: 固定資料走 Console.Out，日誌走 Console.Error，或以 logger 設定不同輸出。
- A詳: 步驟：1) 程式內將日誌寫 Console.Error；2) shell 用 > 與 2> 分別重導；3) 產線中避免把 STDERR 接給資料下游。範例：dotnet CLI | dotnet P1 1>data.json 2>log.txt。注意：下游只讀 STDIN，不解析日誌；便於排錯不影響資料。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, D-Q10

C-Q8: 如何把命令輸出快速複製到剪貼簿？
- A簡: 使用 clip.exe，將 STDIN 寫入剪貼簿：command | clip。
- A詳: 步驟：1) 在 Windows 執行 tasklist | clip；2) 於目標應用 Ctrl+V 貼上。設定：clip 無參數即讀 STDIN；/ ? 顯示說明。注意：僅支援文字；二進位不適合。搭配 JSON Pretty Print 再送 clip 可提高可讀性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, A-Q14

C-Q9: 如何跨機器串接管線（ssh 示例）？
- A簡: 以 ssh 轉發遠端命令 STDIO，在本機與遠端命令間建立管線。
- A詳: 步驟（類 Linux）：ssh user@host "dotnet CLI-DATA.dll" | gzip -d | dotnet CLI-P1.dll；或本機壓縮後傳到遠端：dotnet CLI-DATA.dll | gzip -9 | ssh user@host "gzip -d | dotnet CLI-P1.dll"。注意：權限、路徑、.NET 安裝；跨網傳輸建議壓縮。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q9, A-Q12

C-Q10: 如何為串流處理加入取消與早停控制？
- A簡: 以 Take/Skip 控量，並透過 CancellationToken 與檢查鍵入中斷循環。
- A詳: 步驟：1) 查詢端加入 Take(n)；2) 於迭代器內週期性檢查 token.IsCancellationRequested；3) 捕捉 OperationCanceledException 作優雅結束。程式碼要點：foreach 前套 .Take(n)、在長工時 ProcessPhase 檢查取消。注意：確保釋放 Reader/Stream。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, B-Q18, A-Q19

---

### Q&A 類別 D: 問題解決類（10題）

D-Q1: 執行二進位輸出時終端機出現亂碼怎麼辦？
- A簡: 不要直接輸出到終端；將二進位重導到檔案或下游程式消費。
- A詳: 症狀：畫面亂碼、鈴聲或控制碼干擾。原因：終端機預期文字，收到原始二進位。解決：以 > 檔案或管線給消費者；必要時以 Base64 或 JSON 包裹。預防：預設將 Binary Serializer 用於非終端輸出，或加入格式偵測與警告。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, A-Q3, C-Q7

D-Q2: JsonTextReader 只讀到第一筆 JSON 就停了？
- A簡: 啟用 SupportMultipleContent，並以 while (Read()) 逐筆反序列化。
- A詳: 症狀：只還原第一筆，後續無資料。原因：Reader 預設僅支援單文檔。解決：reader.SupportMultipleContent = true；使用 while(reader.Read()) 迴圈搭配 Deserialize。預防：逐行輸出 JSON，並加入換行輔助排錯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q1, C-Q2

D-Q3: 管線卡住或執行緩慢如何診斷？
- A簡: 檢查背壓：消費端是否慢、pipe 緩衝是否滿；分離 I/O 與 CPU 瓶頸。
- A詳: 症狀：看似當機、輸出延遲。原因：下游慢導致上游阻塞；壓縮/反序列化成本高。解法：以 head/Take 減少資料測試、關閉壓縮對比、監控 CPU/IO、拆分階段、調整批量。預防：採逐筆處理、控制每筆大小、必要時增加緩衝或並行化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q14, B-Q22

D-Q4: 記憶體使用過高怎麼辦？
- A簡: 改為串流處理，避免一次載入全部；使用 IEnumerable 與 yield。
- A詳: 症狀：常見於先收集到 List 再處理。原因：物件堆疊過大、GC 壓力。解法：將來源與消費都改成逐筆；避免 materialize；以 Take/Skip 控制；建立邊讀邊寫。預防：介面契約以串流為主，工具用 head/grep 搭配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q4, C-Q3

D-Q5: JSON 效能差或體積大該怎麼優化？
- A簡: 改 Binary 或加入 gzip；調整欄位（避免巨大 Base64）、選更快序列化器。
- A詳: 症狀：CPU 高、輸出檔大。原因：Base64 編碼與字串處理開銷。解法：Binary 格式或壓縮；若必須 JSON，考慮 System.Text.Json、縮小欄位、拆分大二進位以外部檔案承載。預防：先以樣本實測再定案格式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q12, C-Q5

D-Q6: Binary 反序列化拋錯（版本不符）怎麼辦？
- A簡: 確保同版本契約或改用版本友善格式（JSON/Protobuf/MessagePack）。
- A詳: 症狀：SerializationException、型別解析失敗。原因：Binary 強耦合組件版本與型別。解法：統一共用模型組件版本；使用 Binder 或升級策略；最好改採版本相容格式。預防：明確版本策略與相容性測試。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, A-Q5, C-Q4

D-Q7: Windows 找不到 gzip 怎麼處理？
- A簡: 安裝 Git for Windows 或 Gnu 工具，或改用 .NET GZipStream。
- A詳: 症狀：'gzip' 不是內部或外部命令。原因：系統未安裝或 PATH 未設。解法：安裝 Git（附 gzip）、將 bin 加入 PATH；或在程式內以 GZipStream 實作。預防：發佈說明列必要工具，或完全內建化壓縮。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, C-Q6, A-Q14

D-Q8: 逐行 JSON 解析錯誤（界線不清）怎處理？
- A簡: 確保每筆輸出換行，或正確設定 SupportMultipleContent。
- A詳: 症狀：解析失敗或合併成一筆。原因：缺換行或 reader 設定錯誤。解法：輸出每筆後 WriteLine()；讀取端開啟 SupportMultipleContent；測試時用 head/tail 檢視分行。預防：建立格式契約並寫入測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q6, B-Q24, C-Q2

D-Q9: 反序列化安全風險如何避免？
- A簡: 不信任輸入，禁用 BinaryFormatter；使用安全序列化器並驗證資料。
- A詳: 症狀：潛在 RCE、資料破壞。原因：反序列化器解析任意型別。解法：改用 System.Text.Json/Protobuf/MessagePack；限制型別解析；加上架構驗證與白名單。預防：安全規範、審核、模糊測試。尤其跨網資料務必加強。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q17, C-Q4

D-Q10: 日誌污染資料輸出怎麼辦？
- A簡: 把日誌導到 STDERR，資料保留在 STDOUT，必要時獨立檔案。
- A詳: 症狀：下游 JSON 解析失敗、混入 [P1] 記錄。原因：把日誌寫到 STDOUT。解法：Console.Error.WriteLine() 輸出日誌；shell 使用 2> 分流；或使用結構化日誌到檔案。預防：開發規範與測試，檢查輸出只含資料。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, C-Q7, A-Q20

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 CLI 的 Pipeline？
    - A-Q2: STDIN/STDOUT 與 TextReader/TextWriter 有何差異？
    - A-Q3: 為什麼 CLI 可以傳遞二進位資料？
    - A-Q4: 什麼是「透過 Pipeline 傳遞物件」？
    - A-Q5: JSON 與 Binary 序列化的差異？
    - A-Q6: PowerShell 物件管線與傳統 *nix 文字管線差在哪？
    - A-Q7: 為什麼要在 CLI 中處理物件而非純文字？
    - A-Q10: 為何選擇「每行輸出一個 JSON 物件」？
    - B-Q1: JSON 物件在管線中如何運作？
    - B-Q3: 在管線中如何加入 gzip 壓縮/解壓？
    - B-Q8: 管線中日誌輸出應如何設計？
    - C-Q1: 如何實作「每行一筆 JSON」的輸出 CLI？
    - C-Q2: 如何實作「逐筆接收 JSON」的 ReceiveData()？
    - C-Q5: 如何用 gzip.exe 壓縮/解壓整段管線？
    - D-Q2: JsonTextReader 只讀到第一筆 JSON 就停了？

- 中級者：建議學習哪 20 題
    - A-Q8: 什麼是 IEnumerable<T> 在串流處理中的角色？
    - A-Q9: LINQ 在串流資料中的意義？
    - A-Q11: JsonTextReader.SupportMultipleContent 是什麼？
    - A-Q12: 為何要考慮壓縮（gzip）？
    - A-Q13: 什麼是 Pipeline Buffer 與背壓（backpressure）現象？
    - A-Q16: 抽象化 GenerateData()/ReceiveData() 的價值？
    - B-Q4: ReceiveData() 的設計原理是什麼？
    - B-Q6: 逐行 JSON 與陣列 JSON 的解析流程差異？
    - B-Q7: LINQ 在處理串流資料的機制？
    - B-Q12: 影響序列化效能與體積的因素？
    - B-Q14: 管線緩衝與流程控制如何影響效能？
    - B-Q22: Take(5) 如何在串流中早停？
    - B-Q24: 為何逐筆輸出時建議每筆後寫入換行？
    - B-Q25: foreach 與串流資料的驅動關係？
    - C-Q3: 如何以 LINQ 過濾 SerialNO 為 7 倍數且只處理前 5 筆？
    - C-Q4: 如何改為二進位序列化（示範 BinaryFormatter）？
    - C-Q6: 不依賴外部工具，如何用 GZipStream 實作壓縮/解壓？
    - C-Q7: 如何正確分流資料與日誌（避免污染 JSON/二進位）？
    - D-Q3: 管線卡住或執行緩慢如何診斷？
    - D-Q5: JSON 效能差或體積大該怎麼優化？

- 高級者：建議關注哪 15 題
    - A-Q15: 安全性：BinaryFormatter 為何需謹慎？
    - A-Q19: IEnumerable 單向巡覽一次有何影響？
    - B-Q9: 為何 ssh 能讓管線跨網路？
    - B-Q11: Json.NET 與 System.Text.Json 在串流上的考量？
    - B-Q15: 多階段管線的設計考量？
    - B-Q16: 資料契約與版本相容如何管理？
    - B-Q17: 反序列化安全風險與防護機制？
    - B-Q18: 枚舉器中例外（Exception）如何影響上游/下游？
    - B-Q19: 如何判斷串流結束？
    - B-Q21: 壓縮應放在何層實作較佳？
    - C-Q9: 如何跨機器串接管線（ssh 示例）？
    - C-Q10: 如何為串流處理加入取消與早停控制？
    - D-Q6: Binary 反序列化拋錯（版本不符）怎麼辦？
    - D-Q9: 反序列化安全風險如何避免？
    - D-Q10: 日誌污染資料輸出怎麼辦？