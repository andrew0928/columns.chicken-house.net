# Extension Methods 的應用: Save DataSet as Excel file...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者沒有直接繼承 DataSet，而是選擇用 Extension Methods 來加入 ReadExcel／WriteExcel？
使用者的程式碼可能同時用到 `System.Data.DataSet` 或 VS 依 XSD 產生的 Typed DataSet。改用自己繼承的 DataSet 會讓這兩種做法都變得不方便；Extension Methods 則可在「不重編譯、也不用原始碼」的前提下，直接替既有型別（這裡是 DataSet）附加新功能。

## Q: 什麼是 C# 的 Extension Methods？它有哪些限制？
Extension Methods 是 .NET 3.0 之後提供的機制，可在現有型別上「掛」出新的實體方法。它其實只是 static 方法，第一個參數加上 `this` 來指定要擴充的型別。  
限制：  
1. 只能新增「實體方法」，不能新增 static 方法、property 或 field。  
2. 本質上仍是 static 方法，只是編譯器在語法上做了糖衣包裝。

## Q: 如何用 Extension Methods 讓 DataSet 直接讀寫 Excel？
宣告一個 static 類別，例如 `NPOIExtension`，並實作  
```csharp
public static void ReadExcel(this DataSet ds, string inputFile) { ... }
public static void WriteExcel(this DataSet ds, string outputFile) { ... }
```  
之後即可寫出：
```csharp
DataSet ds = new DataSet();
ds.ReadExcel("data.xls");
// ...資料處理...
ds.WriteExcel("data.xls");
```
看起來就像 DataSet 內建了 ReadExcel／WriteExcel 一樣。

## Q: 如果不用 Extension Methods，同樣的呼叫長相會變成什麼？
必須直接呼叫 static 方法並手動傳入 DataSet 參數：
```csharp
DataSet ds = new DataSet();
NPOIExtension.ReadExcel(ds, "data.xls");
// ...資料處理...
NPOIExtension.WriteExcel(ds, "data.xls");
```
語意雖相同，但可讀性較差。

## Q: WriteExcel 方法的核心流程是什麼？
1. 建立 `HSSFWorkbook`。  
2. 對 DataSet 內每個 `DataTable`：  
    a. 建立一個 Sheet（以 TableName 為名）。  
    b. 產生第 0 列當作表頭，填入欄位名稱。  
    c. 逐列、逐欄將資料寫入對應的 Excel Row/Cell。  
3. 若輸出檔已存在先刪除，再用 `FileStream` 將 Workbook 寫入檔案。

## Q: DataSet 與 Excel 在此範例中的對映關係為何？
• 一個 DataSet → 一個 Excel Workbook  
• 一個 DataTable → Workbook 中的一張 Sheet  
• DataTable 的 Row／Column → Excel 的 Row／Cell

## Q: 在 .NET 環境下還有哪些常見的輸出 Excel 方法？
1. 直接自動化 Excel 物件模型（功能最全，但效能差且不適合 Server Side）。  
2. 透過 Jet ODBC／OleDB Driver 把 Excel 當資料庫操作（不支援 x64）。  
3. 產生 HTML Table，改 Content-Type 讓 Excel 開啟（簡單但客製化能力低）。  
4. 直接輸出 Office Open XML (`.xlsx`)。  
5. 使用第三方函式庫，如 NPOI、Koogra，可在純 .NET 下處理新版或舊版 Excel 二進位格式。