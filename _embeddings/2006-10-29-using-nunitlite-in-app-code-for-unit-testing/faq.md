# 利用 NUnitLite, 在 App_Code 下寫單元測試

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 ASP.NET Web 應用程式中建議使用 NUnitLite 而不是 NUnit 來執行 App_Code 下的單元測試？
NUnit 的組件數量多，且在 Web 環境下無法順利載入由 ASP.NET 動態產生的 App_Code 組件；它還會另外建立 AppDomain 並以獨立執行緒跑測試，對 Web 應用來說風險較高。NUnitLite 較精簡，不會做這些額外動作，放進網站就能輕鬆執行，因此更適合快速的 Web-based 專案。

## Q: 要在 ASP.NET 2.0 Web Site 中建立一個「能執行 App_Code 下測試」的 Test Runner，步驟是什麼？
1. 建立一個 Web Site 專案。  
2. 參考 (Reference) 自行編譯好的 `NUnitLite.dll`。  
3. 建立 `NUnitLiteTestRunner.aspx`，在 `Page_Load` 中寫下：  
```csharp
this.Response.ContentType = "text/plain";
Console.SetOut(this.Response.Output);
ConsoleUI.Main(new string[] { "App_Code" });
```  
瀏覽器開啟此頁即可看到類似 NUnitConsole 的文字輸出結果。

## Q: 範例中的 `ConfigurationTest` 主要檢查了哪些事項？
1. `SessionEnableTest`：確認 `HttpContext.Current.Session` 不為 null，代表網站已啟用 Session。  
2. `TempFolderAccessTest`：  
   • 檢查 `web.config` 裡設定的 `temp-folder` 是否存在。  
   • 測試在該目錄中能成功建立、讀取、寫入並刪除暫存檔，確保資料夾權限正確。

## Q: 若瀏覽器（例如 IE）把 `NUnitLiteTestRunner.aspx` 的輸出誤判為 XML 而顯示錯誤，該怎麼辦？
直接在該頁面按滑鼠右鍵並選擇「View Source」，即可正確看到純文字的測試結果。

## Q: 對於「環境設定屬於系統測試，不該放進 unit test」的質疑，作者怎麼回應？
作者認為在多個網站或由不懂程式的人部署的環境中，設定正確與否極為重要，但卻常被忽略。既然 NUnitLite 已讓撰寫與執行測試變得容易，就應把環境與設定檢查也納入測試流程，實際上能更快發現與修正問題。