# 後端工程師必備: CLI 傳遞物件的處理技巧

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 .NET CLI 中，可以用 STDIN/STDOUT 傳遞二進位資料甚至物件？
STDIN 與 STDOUT 在 .NET 中本質是 Stream 層級，而非 TextReader/TextWriter 層級，所以除了純文字外，也能直接處理二進位資料，只要下一段 Pipeline 能正確解析即可。

## Q: 兩個 CLI 程式之間要如何透過 Pipeline 傳遞物件？
做法是在「生產端」把物件序列化（最簡單是逐筆輸出 JSON），寫到 STDOUT；「消費端」再從 STDIN 逐筆反序列化還原成物件後繼續處理。

## Q: 為什麼示範程式選擇「一筆物件輸出一次 JSON」，而不是整批包成陣列？
逐筆輸出可讓下游以串流（stream）方式即時處理，不必等到整批資料都到齊再一次解析，符合 Pipeline「一筆進、一筆出」的處理哲學。

## Q: 覺得 JSON 太佔空間或效率不佳，有其他做法嗎？
可以改用 .NET 內建的 BinaryFormatter 做二進位序列化，以減少文字開銷並加快序列化/反序列化速度。

## Q: 同樣 1000 筆資料，JSON 與 BinaryFormatter 的檔案大小差多少？
測試結果：JSON 約 108,893 bytes；BinaryFormatter 約 430,000 bytes（因為含型別資訊）。

## Q: 可以在 Pipeline 中直接壓縮資料嗎？該怎麼做？
可以，把序列化資料再透過 gzip 壓縮，例如：  
`dotnet CLI-DATA.dll | gzip -9 -c -f > data.gz`  
壓縮後相同資料只剩約 47,064 bytes。

## Q: 要邊壓縮邊解壓再串到下一個 CLI，可以用什麼指令？
範例：  
`dotnet CLI-DATA.dll | gzip -9 -c -f | gzip -d | dotnet CLI-P1.dll`

## Q: 如果前一關傳來的物件並不是全部都需要，該如何在程式內過濾？
因為反序列化後仍是 `IEnumerable<DataModel>`，可直接用 LINQ，例如：  
`foreach (var m in ReceiveData().Where(x => x.SerialNO % 7 == 0).Take(5)) { … }`  
即可濾出 SerialNO 為 7 的倍數且僅取前 5 筆。

## Q: Windows 內建的 clip.exe 可以拿來做什麼？
`clip.exe` 能把任何 CLI 的 STDOUT 直接送進剪貼簿，例如：  
`tasklist | clip`  
執行後就能直接貼上 `tasklist` 的結果，省去手動複製。

## Q: 這些技巧帶來的最大收穫是什麼？
只要掌握「STDIO 就是 Stream」的觀念，並靈活運用序列化、壓縮與 LINQ 等基礎工具，就能在不依賴大型框架的情況下快速打造高效又彈性的 CLI Pipeline。