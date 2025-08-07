# 後端工程師必備: CLI 傳遞物件的處理技巧

# 問題／解決方案 (Problem/Solution)

## Problem: CLI 之間只能傳純文字，難以直接交換物件

**Problem**:  
在撰寫多道 CLI 串接 (pipeline) 的自動化流程時，往往發現 STDIN / STDOUT 似乎只能處理字串。當上一個 CLI 產生複雜物件而下一個 CLI 也需要完整物件才能繼續運算時，開發者被迫把物件轉成字串、再切割、再重組，流程又長又易錯。

**Root Cause**:  
1. 對 STDIN / STDOUT 的誤解：大多數人把它想成「文字流 (TextReader / TextWriter)」，忽略它其實是「位元流 (Stream)」。  
2. 因此只使用字串管線，未善用物件序列化技術。

**Solution**:  
將物件序列化為 JSON，直接寫進 Console.Out；接收端從 Console.In 讀取並反序列化回原型別。以 `IEnumerable<DataModel>` 封裝產出與接收流程，讓每筆資料一進一出保持串流 (stream) 形式。  

Sample code (產出端)：
```csharp
var json = JsonSerializer.Create();
foreach (var model in GenerateData())
{
    json.Serialize(Console.Out, model);
    Console.Out.WriteLine();   // 每筆一行
}
```
Sample code (接收端)：
```csharp
var json = JsonSerializer.Create();
var reader = new JsonTextReader(Console.In) { SupportMultipleContent = true };
while (reader.Read())
    yield return json.Deserialize<DataModel>(reader);
```

關鍵思考點：  
• JSON 序列化將「物件」轉成跨語言可讀的文字格式，任何支援 STDIN / STDOUT 的 CLI 都能傳輸。  
• 使用 `yield return` 讓資料仍以「拉取式」串流存在，不需全量載入記憶體。

**Cases 1**:  
CLI-DATA 連接 CLI-P1：
```
dotnet CLI-DATA.dll | dotnet CLI-P1.dll > nul
```
CLI-P1 逐筆 log：
```
[P1] data(1) start/end ...
```
證實：資料透過 pipeline 順利還原為 `DataModel`，每筆立刻被下一道處理，記憶體占用穩定。

---

## Problem: JSON 太肥大，跨網路或大量資料時傳輸開銷過高

**Problem**:  
在實務中，1000 筆 `DataModel` 使用 JSON 共 108,893 bytes，當透過 ssh 或其他遠端 shell 連線時，傳輸時間、頻寬及磁碟 I/O 皆成為瓶頸。

**Root Cause**:  
1. JSON 為文字格式，欄位名稱重複出現，Base64 編碼又造成額外 33% 膨脹。  
2. 過度焦點在「可讀性」，忽略跨網路場景對資料量的敏感度。

**Solution**:  
(1) 以 .NET 內建 `BinaryFormatter` 改為二進位序列化。  
(2) 再使用現成 CLI `gzip -9` 於管線中即時壓縮。  

Sample code (BinaryFormatter)：  
```csharp
var fmt = new BinaryFormatter();
var os = Console.OpenStandardOutput();
foreach (var m in GenerateData()) fmt.Serialize(os, m);
```
使用 gzip 壓縮 / 解壓：
```shell
dotnet CLI-DATA.dll | gzip -9 -c -f | gzip -d | dotnet CLI-P1.dll
```

關鍵思考點：  
• 二進位序列化移除欄位名稱與 Base64 的字串開銷。  
• gzip 在 CLI 世界已有成熟實作，無須自行寫壓縮邏輯。  
• 保持「一筆資料就序列化一次」— downstream 免等待全檔案完成即可開始處理。

**Cases 1**:  
資料大小比較 (1000 筆)  
• JSON：108,893 bytes  
• BinaryFormatter：430,000 bytes (欄位資訊多，未壓縮不一定較小)  
• Binary + gzip：47,064 bytes ↘ 56% (vs JSON)  
效益：網路傳輸量顯著下降，跨主機 pipeline 反應更靈敏。

---

## Problem: 需對 pipeline 物件做條件過濾，grep / find 無法處理二進位

**Problem**:  
當 CLI-P1 僅需處理 `SerialNO` 為 7 的倍數且前 5 筆物件時，若資料已被二進位或 gzip 包裝，傳統文字工具（grep、awk、findstr）無從下手。

**Root Cause**:  
1. shell 層面的文字工具只能依字串 pattern 過濾，不識別序列化物件。  
2. 開發者若改寫成讀完全部→反序列化→過濾，再輸出，將失去串流優勢並耗費大量記憶體。

**Solution**:  
在接收端持續以 `IEnumerable<DataModel>` 串流迭代，再利用 LINQ 延遲查詢 (`Where`, `Take`) 即時挑選所需物件。  

Sample code：
```csharp
foreach(var model in ReceiveData().Where(x => x.SerialNO % 7 == 0).Take(5))
{
    DataModelHelper.ProcessPhase1(model);
}
```
關鍵思考點：  
• LINQ 延遲執行與 `yield return` 相容——每讀一物件即判斷條件，成立才進入後續邏輯。  
• 立即 `break` 時，上游序列化即可停止，減少不必要 CPU/IO。

**Cases 1**:  
執行結果僅處理 5 筆符合條件資料：
```
[P1] data(7)  start/end
[P1] data(14) start/end
...
[P1] data(35) start/end
```
效益：  
• 不需額外暫存或解析全文，保留 pipeline 的即時與低占用特性。  
• 完全在熟悉的 C# 語境完成過濾，省卻 shell & binary 互轉複雜度。

---

以上三個常見開發情境展示：  
1. 「物件可傳遞」→ 解決 CLI only-text 迷思  
2. 「選擇合適序列化＋壓縮」→ 針對效能/容量最佳化  
3. 「串流 LINQ 過濾」→ 回到熟悉語言做精準資料處理  

只要遵守「一筆進、一筆處理、一筆出」的串流原則，就能把 CLI 當作輕量級 micro-pipeline，靈活組裝出高效、自動化、生產力佳的後端流程。