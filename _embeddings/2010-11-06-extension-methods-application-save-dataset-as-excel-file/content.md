---
layout: post
title: "Extension Methods 的應用: Save DataSet as Excel file..."
categories:

tags: [".NET","C#","MSDN","Tips","有的沒的","技術隨筆"]
published: true
comments: true
redirect_from:
  - /2010/11/06/extension-methods-的應用-save-dataset-as-excel-file/
  - /columns/post/2010/11/06/SaveDataSetAsExcelFile.aspx/
  - /post/2010/11/06/SaveDataSetAsExcelFile.aspx/
  - /post/SaveDataSetAsExcelFile.aspx/
  - /columns/2010/11/06/SaveDataSetAsExcelFile.aspx/
  - /columns/SaveDataSetAsExcelFile.aspx/
wordpress_postid: 13
---

好久沒寫東西了，趁著還記得 C# 怎麼寫的時後多補幾篇 =_=

要靠程式輸出Excel已經是個FAQ級的問題了，看過我之前文章的大概都知到，我很懶的寫那種FAQ級的東西，不是說寫了沒用，而是太多人寫，一定有寫的比我好的... 到最後連我自己忘了都會去查別人寫的，那我寫了還有啥用?

所以當然是有些特別的東西，才會想寫這篇... 我碰到的問題是，程式要處理的都是 DataSet 物件，不過 DataSet 物件是從 Excel 來的，處理完也要能回存回 Excel ..., 只不過為了先把 POC 作完，現在是以 DataSet 原生的 XML 格式代替。

其實以儲存的角度來看，XML很好用。不過要教會客戶編輯XML可是個大挑戰啊... 像 Excel 這樣有個表格還是比較容易上手一點。原本的程式長的像這樣:

**原本的程式 (處理 dataset xml)**

```csharp
DataSet ds = new DataSet();
ds.ReadXml("data.xml");
// do something
ds.WriteXml("data.xml");
```

我對程式碼的要求其實還蠻龜毛的，常常光為了一個變數名字取的好不好，就要想半天... 對於程式的結構寫起來漂不漂亮也是。上面的程式，要把 XML 換成 EXCEL 其實很簡單，把 ReadXml( ) 換成對等的載入 Excel 的程式碼，WriteXml( ) 也換成對等的輸出 Excel 就可以收工了。不過看起來就是不順眼，因為被太多細節干擾了，未來回過頭來看自己寫的 code, 如果一眼望去不能馬上看出這段 code 在做什麼，那就是不及格的作品了... 所以，我想要的 code 最好能像這樣:

**期望的程式 (處理 excel 檔)**

```csharp
DataSet ds = new DataSet();
ds.ReadExcel("data.xls");
// do something
ds.WriteExcel("data.xls");
```

看起來酷多了，這段程式很清楚的說明他在幹嘛... load excel, processing... and save excel...

繼承的作法，想都不用想就不考慮了。因為我的程式要嘛就直接用 System.Data.DataSet, 不然就是配合 XSD 讓 visual studio 替我 generate typed dataset 的類別... 這些情況下要用到我自訂的衍生類別都不方便... 於是我就把念頭動到 C# 的 extension ...

要怎麼把 DataSet 存成 Excel, 這就是典型的 FAQ 級的問題了，請各位 GOOGLE 一下就有了，不然文後我也附了幾個參考連結...。這裡的重點是 C# extension, 它很神奇的能讓你不需要重新編譯，也不需要拿到原始碼，就能 "擴充" 原本類別的能力。靠這樣的機制，我就能夠改造 .NET Framework 內建的 DataSet, 把它改造成我想要的樣子，如上面的範例用的 ReadExcel( ) / WriteExcel( )。

C# Extension 是我慣用的說法，其實它正統的名字是 Extension Methods, 是 .NET 3.0 之後提供的功能，不只 C#，VB.NET 也支援。它能讓你在現有的 class 上 "附加" 新的 method ... 是的，沒錯，它的能力有限，只能增加 "method", 而且只能是 instance method, 不能是 class ( static ) method, 也不能是 property 或 field ...

不過這樣也足夠了，先來看看這種 code 要怎麼寫:

**ExtensionMethods 示範**

```csharp
public static class NPOIExtension
{
    public static void ReadExcel(this DataSet ds, string inputFile)
    {
        //do something
    }

    public static void WriteExcel(this DataSet ds, string outputFile)
    {
        //do something
    }
}
```

其實這又是另一種 Microsoft 提供的 Syntex Sugar 而已.. 注意到關鍵在那邊了嗎? 其實 "extension methods" 只不過是普通的 static method 而已，關鍵就在它的第一個參數，型別就是要附加的 class, 而宣告時要再額外加個 "this" modifier 來標示它，意思就是在裡面的 code, 這個參數就把它當作 "this" 來用 ...

換個角度看，其實這只是編譯器幫我們動一點手腳而已，好讓我們的 code 看起來會漂亮一點。用 extension methods 寫的 code, 其實跟這樣的寫法是完全同等的:

**不用 extension methods 的寫法**

```csharp
DataSet ds = new DataSet();
NPOIExtension.ReadXml(ds, "data.xml");
// do something
NPOIExtension.WriteXml(ds, "data.xml");

public static class NPOIExtension
{
   public static void ReadExcel(DataSet context, string inputFile)
    {
        // do something
    }
   public static void WriteExcel(DataSet context, string outputFile)
    {
        // do something
    }
}
```

少了 this 的用法，看起來就沒這麼神奇了。就是一般的 static method 而已。我喜歡 C# 就是喜歡它有很多這類的 syntax sugar, 可以滿足我寫程式想把程式碼弄的漂漂亮亮的慾望... extension methids 就是一例，還有像 yield return, attribute 等等也是個經典...

這樣的改變讓我想起，以前公司新進工程師我都會教一堂課，就是講物件是怎麼一回事? 最早是 C / C++ 版，後來改用 javascript 來講這門課。講的就是一步一步示範如何由 procedure oriented language 轉變到 object oriented language 的過程。C++ 是個最清楚的例子，它靠 C 的 function pointer + struct, 用指標指向 function, 把 data 及 function 包裝在 struct 裡，就變成一個 object. (所以 C++ 的 struct 才會跟 class 這麼像啊)。而繼承的問題，則是在 struct 裡動一點手腳，用 virtual table 的方式，讓你寫起 code 來 "好像" 真的有物件導向這麼回事。其實 C++ 的 method, 也只是個普通的 function, 只不過它第一個參數一定叫作 "this" 而已...

扯遠了，整篇的目的只是要講，用 Extension Method 可以把 code 包的很漂亮，而且也真的可以動而已... 哈哈，最後貼一下完整的 source code, 證明我沒有唬爛...

程式我調一下，我只實作了 WriteExcel( ) 的部份，從 DataSet XML 讀進來，存成 Excel, 單純的一個轉檔程式。而轉換的過程中是這樣對應的: 一個 DataSet 就代表一個 EXCEL workbook，而一個 DataTable, 則對應到 EXCEL sheet。DataTable 的 Row / Column, 當然就是對應到 EXCEL Row 跟 Cell 了:

**完整的 source code**

```csharp
public class Program
{
    static void Main(string[] args)
    {
        DataSet ds = new DataSet();
        ds.ReadXml("data.xml");
        // do something
        ds.WriteExcel("data.xls");
    }
}

public static class NPOIExtension
{
    public static void WriteExcel(this DataSet context, string outputFile)
    {
        HSSFWorkbook workbook = new HSSFWorkbook();

        foreach (DataTable table in context.Tables)
        {
            Sheet sheet = workbook.CreateSheet(table.TableName);

            Row headerRow = sheet.CreateRow(0);
            for(int cpos = 0; cpos < table.Columns.Count; cpos++)
            {
                Cell cell = headerRow.CreateCell(cpos);
                cell.SetCellType(CellType.STRING);
                cell.SetCellValue(table.Columns[cpos].ColumnName);
            }

            int rpos = 0;
            foreach (DataRow row in table.Rows)
            {
                rpos++;
                Row sheetRow = sheet.CreateRow(rpos);
                for (int cpos = 0; cpos < table.Columns.Count; cpos++)
                {
                    object value = row[cpos];
                    Cell cell = sheetRow.CreateCell(cpos);
                    cell.SetCellValue((value == null) ? (null) : (value.ToString()));
                }
            }
        }

        if (File.Exists(outputFile)) File.Delete(outputFile);
        FileStream fs = File.OpenWrite(outputFile);
        workbook.Write(fs);
        fs.Close();
    }
}
```

對啦，這真的是全部的 code ... 開個 console project 就可以跑了。我就說我很少貼超過百行的 code ... 哈哈

順帶一提，NPOI 這個 open source project 做的真不錯，可以在 pure .net 環境下就能處理 excel ... 這個範例就是用 NPOI 寫的，有興趣的朋友可以參考看看!

---

Reference:

1. MSDN: Extension Methods (C# Programming Guide)
   [http://msdn.microsoft.com/en-us/library/bb383977.aspx](http://msdn.microsoft.com/en-us/library/bb383977.aspx)

2. NPOI (in CodePlex.com)
   [http://npoi.codeplex.com/](http://npoi.codeplex.com/)

3. MSDN 學習園地的 NPOI 介紹文章 (中譯版)
   在 Server 端存取 Excel 檔案的利器：NPOI Library
   [http://msdn.microsoft.com/zh-tw/ee818993.aspx](http://msdn.microsoft.com/zh-tw/ee818993.aspx)

4. 另一套類似NPOI 的函式庫: Koogra
   Koogra Excel BIFF/XLSX Reader Library
   [http://koogra.sourceforge.net/](http://koogra.sourceforge.net/)

5. 直接用 OpenXML format 的範例
   [http://www.dotblogs.com.tw/mis2000lab/archive/2008/04/24/3454.aspx](http://www.dotblogs.com.tw/mis2000lab/archive/2008/04/24/3454.aspx)

6. Microsoft Open XML SDK 1.0 / 2.0 for Microsoft Office
   1.0 ([http://www.microsoft.com/downloads/en/details.aspx?FamilyId=AD0B72FB-4A1D-4C52-BDB5-7DD7E816D046&displaylang=en](http://www.microsoft.com/downloads/en/details.aspx?FamilyId=AD0B72FB-4A1D-4C52-BDB5-7DD7E816D046&displaylang=en))
   2.0 ([http://www.microsoft.com/downloads/en/details.aspx?FamilyID=c6e744e5-36e9-45f5-8d8c-331df206e0d0&DisplayLang=en](http://www.microsoft.com/downloads/en/details.aspx?FamilyID=c6e744e5-36e9-45f5-8d8c-331df206e0d0&DisplayLang=en))

後記: 本來有寫一段，是整理到底有幾種方法，可以在 .NET 環境下輸出 EXCEL 的... 不過後來決定沒放在本文，就挪到 reference ... 簡單的比較，需要的可以看看

1. 直接用 Excel 提供的物件

   這種方式就是透過程式去操作 Excel 。優點是只要 Excel 有提供的功能，大概都做的到。不過也因為功能太多，用起來很複雜。這方法致命的缺點就是效能。它相當於你真的開啟 Excel 然後命令它做事，想像一下，要能很順暢的執行 Excel 的機器，都不會太差。單機的 windows form 程式還好，如果碰到 server side 的程式，如 ASP.NET 這種，只要同時有五個人點這個功能，你的 server 大概就跑不動了...。

2. 透過 Jet odbc / oledb driver

   這種方式沒有第一種的缺點，不過也沒有它的優點。既然是透過 odbc 這類存取資料庫的 driver 來存取，那麼你也只能把 Excel 檔當成某種資料庫來看待。處理資料還不成問題，要套用公式或是輸出畫面就辦不到了。這方法還有個大缺點，Jet driver [沒有 x64 的版本](/post/2008/07/26/x64-2-ASPNET-2b-ODBC-(e8ae80e58f96-CSV).aspx) .... windows 2008 r2 之後就沒有 x86 版了，這方法不是長久之計...

3. 輸出 HTML, 用 Excel 開啟

   這方法很簡單，只要輸出 HTML table, 再調整 content type, 讓 browser 叫 excel 出來幫你開啟就好了。老實說我一直覺的這招有點投機 XD，好處是很簡單，缺點是對 EXCEL 的掌控程度很低，大概就是幫你把資料貼進去的程度而已，不能用公式，也不能輸出多個 sheet 。

4. Open XML Format 直接輸出

   Office 2007 開始，就放棄用了十幾年的 Ole structed storage compound file 二進位檔的格式，改以 XML 為主 (當然還是支援舊版的格式啦)。只要你知道它的 schema, 不需要太複雜的步驟就可以直接輸出 .xlsx 了。

   熟 XML 的話，甚至是寫寫 XSLT 就可以生的出來。不過這還蠻考驗你對 XML / Open XML 的掌握程度... 算是小有門崁的作法。

5. 透過 NPOI / Koogra 這類 3rd party 含式庫

   這些含式庫都可以不需要安裝龐大的 Excel, 就有處理 excel 檔的能力。跟 Open XML 不同的是，這些 library 能夠處理到比較頭痛的 2003 及之前版本的 binary file, 相容性比 XML 來的好。
