```markdown
# Web Site Application + Sandcastle

## 摘要提示
- Sandcastle：製作 .NET 說明檔的新工具，但需要 DLL 與 XML 才能運作。  
- Assembly & XML：說明文件產生器仰賴組件與編譯時匯出的註解 XML。  
- App_Code 機制：ASP.NET 2.0 的即時編譯讓程式碼不經 DLL 與 XML，造成文件生成困難。  
- compilerOptions：在 web.config 內加入 /doc 參數可輸出 XML，卻因資料夾分割而反覆遭覆寫。  
- aspnet_compiler.exe：能產生 DLL，但仍無法同步產生註解 XML。  
- Web Deployment Project：可將多個 DLL 併為單一組件，同樣無法解決 XML 匯出問題。  
- MSBuild 自訂 Task：可透過 Csc Task 自行編譯，但設定複雜、維護成本高。  
- csc.exe 手動編譯：直接對 App_Code 目錄下的 .cs 進行編譯，成功取得 DLL 與 XML。  
- 限制檔案類型：WSDL、XSD 與 .ascx/.aspx 產生的程式碼無法被單純 csc.exe 編譯涵蓋。  
- 效率與取捨：Sandcastle 速度遠慢於 NDoc，最終以手動 csc 解決主要需求，其餘部分暫時放棄。  

## 全文重點
作者欲在 ASP.NET Web Site 專案中為 C# 程式碼產生 Sandcastle 說明檔，卻碰上 ASP.NET 2.0 的即時編譯機制：程式碼只要放入 App_Code 便能執行，系統在執行階段才動態編譯，因而缺少建置階段必備的 DLL 與對應 XML 註解。為解決此缺口，作者嘗試四種方式。第一，於 web.config 的 <compiler> 標籤加 /doc 參數，在開發機可成功輸出 XML，但因 ASP.NET 逐資料夾編譯導致檔案反覆覆寫而失敗。第二，使用 aspnet_compiler.exe 或 Web Deployment Project 能產生 DLL，卻無法同時帶出 XML。第三，自寫 MSBuild 專案並呼叫 Csc Task 可行但成本過高。最終作者採第四案：手動執行 csc.exe，將 App_Code 下的所有 .cs 編譯為單一 DLL 並開啟 /doc 產生 XML，再交予 Sandcastle 製作說明檔。此法能覆蓋大多數 class library，惟無法處理自動產生的 Proxy、Typed DataSet 以及 .ascx/.aspx 相關程式碼。作者權衡後接受此不足，並抱怨 Sandcastle 產生 CHM 花費 60 分鐘，比舊工具 NDoc 慢三倍；然而在無更佳方案前，手動 csc 結合法仍為最實際作法。

## 段落重點
### 問題與背景
作者需要為 Web Application 內的共用類別庫產生說明文件。NDoc 停止更新後，唯一支援 .NET 2.0 泛型等語法的工具是 Sandcastle，但其硬性需求──已編譯的 DLL 與對應 XML 註解──在 ASP.NET 2.0 Web Site 專案中並不存在，因為程式碼於 App_Code 資料夾中由執行階段即時編譯。如何取得兩個檔案成為本文討論核心。

### 在 web.config 裡加上 compiler option 輸出 XML
作者首先嘗試在 <system.codedom><compiler> 節點加入 compilerOptions="/doc:c:\sample.xml"，並用 aspnet_compiler.exe 產生 DLL。開發環境可成功得到 XML，但放入正式站時，因 ASP.NET 以資料夾為單位重複編譯，XML 檔在每次編譯時被覆寫且檔名不可使用萬用字元，導致多層目錄的情境完全失敗，只能作罷。

### Web Deployment Project
接著改用 Visual Studio 2005 SP1 內建的 Web Deployment Project。其流程先以 aspnet_compiler.exe 產生多個組件，再用 Assembly Merge 工具併成一支 DLL，簡化了部署。但此流程依舊無法從編譯器取得 XML 註解，因此對產生說明檔並無助益。

### 寫 MSBuild Project File
搜尋資料時發現有人透過自訂 MSBuild Task，把所有 .cs 檔加入 Csc Task，以 /doc 與 /out 參數一次生成 DLL 與 XML。作者評估後認為此解法需重寫整個建置腳本，而專案本身並未大量使用 MSBuild，學習與維護成本過高，故未採用。

### 手動下 CSC.exe 指令
最終作者決定「硬上」：直接呼叫 csc.exe /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs。此命令把 App_Code 內所有 C# 檔編譯成單一 DLL 並導出 XML，成功滿足 Sandcastle 的輸入需求。雖仍需額外批次檔或腳本，但實作快速且維護簡單。

### 方法限制與取捨
手動 csc.exe 僅能處理純 .cs 檔，對於放在 App_Code 中的 WSDL、XSD 產生之 Proxy 與 Typed DataSet 及 .ascx/.aspx 的分部類別都無法涵蓋；若要彌補必須仿造 aspnet_compiler.exe 的行為，自行實作完整流程，工程浩大。作者最終接受缺口，因為主要的可共用類別都已覆蓋；至於 Sandcastle 產生 CHM 比 NDoc 慢三倍，也只能先忍受。

```