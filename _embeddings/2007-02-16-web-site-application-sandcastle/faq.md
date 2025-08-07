```markdown
# Web Site Application + Sandcastle

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 ASP.NET 2.0 的 Web Site 專案中製作說明文件 (Help) 會遇到困難？
NDoc、Sandcastle 這類說明文件產生器需要兩種輸入檔案：  
1. 編譯後的 Assembly (DLL) 供反射擷取 metadata  
2. 編譯器在編譯時匯出的 XML Documentation  
而 Web Site 專案的程式碼只要放在 App_Code 目錄就能執行，預設既不產生 DLL，也不輸出 XML，所以無法直接交給這些工具處理。

## Q: 把 `/doc` 編譯器選項寫進 web.config 就能解決 XML 文件輸出問題嗎？
在 web.config 的 `<system.codedom>` 節點加入 `/doc:xxx.xml` 的確能產生 XML，但 ASP.NET 以「目錄為單位」重複編譯 App_Code 中的程式碼，同一個檔名的 XML 會被不斷覆寫；只要 App_Code 有多層目錄就會失敗，因此線上環境並不實用。

## Q: 使用 Visual Studio 2005 的 Web Deployment Project 可以一次拿到 DLL 和 XML 嗎？
不行。Web Deployment Project 先呼叫 aspnet_compiler.exe 產生多個 Assembly，再用 Merge 工具合併成單一 DLL，雖然 DLL 取得了，但仍然沒有 XML Documentation，所以仍無法直接餵給 NDoc/Sandcastle。

## Q: 作者最終是如何成功產生 DLL 與 XML，並交給 Sandcastle 的？
作者改用「手動」呼叫 C# 編譯器：  
```
csc.exe /out:App_Code.dll /doc:App_Code.xml /target:library /recurse:App_Code\*.cs
```  
這個指令把 App_Code 下所有 `.cs` 檔一次編成 DLL，同時輸出 XML，接著就能順利交給 NDoc 或 Sandcastle 產生 Help 檔。

## Q: 手動使用 csc.exe 的作法有什麼限制？
1. App_Code 可能包含 WSDL、XSD 等檔案，這些在正式編譯時會自動產生額外程式碼，csc.exe 無法處理。  
2. .ascx/.aspx 對應的 partial class 另一半程式碼是由引擎動態產生，也不會被 csc.exe 編入。  
3. 若要完全重現 ASP.NET 的編譯流程，得額外撰寫 batch 或 MSBuild Task，幾乎等於重做一個 aspnet_compiler.exe，工程太大，不划算。

## Q: Sandcastle 與 NDoc 產生 CHM 文件的速度差異如何？
作者實測：使用 NDoc 生成 CHM 約 20 分鐘即可完成，而改用 Sandcastle 需要大約 60 分鐘，速度明顯偏慢。
```