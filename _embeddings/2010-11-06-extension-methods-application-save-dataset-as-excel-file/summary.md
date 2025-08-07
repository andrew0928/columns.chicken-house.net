# Extension Methods 的應用: Save DataSet as Excel file...

## 摘要提示
- Extension Method: 透過 C# 的 Extension Methods 為 DataSet 擴充 ReadExcel 與 WriteExcel，讓程式碼語意清晰又易維護。  
- NPOI: 借助 NPOI 開源函式庫，在不安裝 Excel 的前提下於純 .NET 環境內讀寫 xls。  
- Code Refactor: 以語法糖取代繁雜呼叫，避免繼承帶來的型別耦合並維持 IDE 產生之 Typed DataSet 的便利。  
- Implementation: Extension Method 本質為 static 方法，僅在第一個參數前加 this，編譯器自動轉換呼叫語法。  
- Sample Code: 全文僅百餘行的 Console 範例展示從 XML 轉存 Excel 的完整流程。  
- Design Philosophy: 作者強調「一眼看懂」的程式碼美學，包含命名與結構的簡潔。  
- Alternative Approaches: 列舉五種 .NET 輸出 Excel 作法，分析功能、相容性與效能差異。  
- Performance: 指出 COM 自動化操控 Excel 雖功能完整，卻在伺服器端效能與穩定度不足。  
- Compatibility: NPOI 可處理 2003 以前的 BIFF 二進位格式，對舊版檔案相容性高於 OpenXML。  
- Resources: 提供 MSDN、NPOI、OpenXML SDK 等延伸閱讀連結以便深入研究。

## 全文重點
作者因專案需求，需要將來自 Excel 的資料以 DataSet 形式處理後再儲回 Excel。雖 DataSet 內建 ReadXml/WriteXml 已能對應 XML 檔案，但讓客戶直接編輯 XML 並不友善，因此希望保留 DataSet 工作流程，同時把輸入輸出改為 Excel。為了維持程式碼可讀性，他想讓呼叫端依舊只需寫 ds.ReadExcel()/ds.WriteExcel() 即可，而不被雜亂的細節淹沒。  
由於重新繼承 DataSet 不但麻煩且與 VS 產生的 Typed DataSet 不相容，作者決定利用 .NET 3.0 之後提供的 Extension Methods。透過建立一個 static 類別 NPOIExtension，並以 this DataSet 為首參數，即可動態為 DataSet「貼」上 ReadExcel 與 WriteExcel 方法，而呼叫方則享有仿原生介面的流暢語法。文中先示範 ReadXml/WriteXml 的舊程式，再展示期望的新語法，接著比較「加 this」與「不加 this」兩種呼叫方式的程式碼等價性，說明 extension 不過是編譯器提供的語法糖。  
核心實作選用 NPOI 函式庫，因其能在純 .NET 環境處理 97–2003 BIFF 二進位格式且不需安裝 Excel。範例程式僅數十行：建立 HSSFWorkbook、對 DataSet.Tables 逐一轉成 Sheet、先輸出欄位列，再輸出資料列，最後寫檔即成。整段程式碼可直接放入 Console Project 執行，證明概念。  
文章最後匯整多種在 .NET 內輸出 Excel 的做法：1) COM 自動化直接控制 Excel；2) Jet ODBC/OLEDB 當成資料庫操作；3) 輸出 HTML 由 Excel 開啟；4) 直接產生 OpenXML；5) NPOI/Koogra 等第三方函式庫，並逐一比較效能、相容性與開發門檻，強調在伺服器端或 64bit 環境 NPOI 更顯彈性。附錄多則參考連結，方便讀者深究 Extension Methods 與各類 Excel 方案。

## 段落重點
### 原本的程式 (處理 dataset xml)
作者先回顧現況：DataSet 透過 ReadXml/WriteXml 讀寫 data.xml，雖然 XML 儲存格式好用，但對使用者不友善；客戶仍偏好用 Excel 編輯。程式碼層面看來也顯雜亂——核心邏輯被檔案格式細節干擾，回顧時不易一眼看出意圖，無法達到作者對「漂亮程式碼」的標準。

### 期望的程式 (處理 excel 檔)
理想畫面是 DataSet 具備 ReadExcel/WriteExcel，呼叫端仍維持三行：載入、處理、存檔。這種語法直接揭示「讀 Excel → 處理 → 存 Excel」的流程，讓意圖與實作細節分離。作者排除「繼承 DataSet」方案，因為 Typed DataSet 等情境下型別不便更換。

### ExtensionMethods 示範
透過宣告 public static class NPOIExtension 並撰寫  
public static void ReadExcel(this DataSet ds, string inputFile) {...}  
即可在編譯期替任何 DataSet 實例加上名為 ReadExcel 的方法；同理亦可加 WriteExcel。除第一個參數多個 this，其他皆為普通 static 方法。Extension Method 僅能增添 instance method，無法加入屬性、欄位或 static method，但對需求已足夠。

### 不用 extension methods 的寫法
若去掉 this 修飾，呼叫端需寫 NPOIExtension.ReadExcel(ds, "data.xls")；邏輯相同但語法失去物件導向暢感。作者藉此說明 extension method 只是編譯器語法糖：編譯時仍轉為靜態呼叫，只是替開發者包裝成像「物件自帶功能」般自然，滿足程式碼美學與可讀性。

### 完整的 source code
給出可編譯的範例：主程式先 ReadXml，再 WriteExcel。WriteExcel 內部以 NPOI 建立 HSSFWorkbook；每個 DataTable 轉為 Sheet，先輸出欄名，再逐列寫入資料，最後以 workbook.Write 寫至檔案。整體不足百行，證明 Extension Method 與 NPOI 組合即可輕鬆完成 XML→Excel 的轉檔。

### Reference
列出十餘條延伸閱讀：MSDN Extension Methods 文件、NPOI 專案首頁、MSDN 中文介紹、Koogra 函式庫、OpenXML 範例及 SDK 下載等，方便讀者進一步研究不同技術路徑與工具。

### 後記
作者整理五種 .NET 輸出 Excel 的方案並比較：  
1) COM 自動化功能最完整但效能差且不適用伺服器；  
2) Jet ODBC/OLEDB 僅能當資料庫使用，且缺乏 x64 版；  
3) 輸出 HTML 讓 Excel 開啟最省事，但只能貼資料；  
4) 直接產生 OpenXML 相對現代，需熟悉 Schema；  
5) NPOI / Koogra 提供純 .NET 讀寫 BIFF/XLSX 的平衡做法。  
綜合考量效能、相容性與開發難度，作者此處選用 NPOI 加 Extension Method 作為最適切的解決方案。