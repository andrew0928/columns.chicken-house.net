# 利用 NUnitLite 在 App_Code 下寫單元測試

# 問題／解決方案 (Problem/Solution)

## Problem: 多站點部署時，如何快速驗證 Web 應用程式的環境與組態是否正確？

**Problem**:  
公司開發的 ASP.NET 2.0 Web 應用程式，常被安裝到多個不同的站點；安裝人員多半不熟程式碼。若各站點的 Web.config 設定不一致（如 session 未啟用、temp folder 設錯），系統就可能在正式運行時才暴露問題，造成維運成本上升。

**Root Cause**:  
1. 傳統單元測試僅針對函式邏輯，不含環境／組態檢查。  
2. 開發與維運人力有限，專案規模不足以導入完整的環境自我檢查機制。  
3. 手動檢查組態容易遺漏，且需具備程式背景的人員才看得懂設定值。

**Solution**:  
以 NUnitLite 為核心、在 App_Code 底下撰寫測試，並用一支簡易的 ASPX Runner 執行。流程：

1. 建立 Web Site 專案。  
2. 參考（Reference）自行編譯的 `NUnitLite.dll`。  
3. 實作 `NUnitLiteTestRunner.aspx`：

   ```csharp
   public partial class NUnitLiteTestRunner : System.Web.UI.Page
   {
       protected void Page_Load(object sender, EventArgs e)
       {
           Response.ContentType = "text/plain";
           Console.SetOut(Response.Output);
           ConsoleUI.Main(new string[] { "App_Code" });
       }
   }
   ```

4. 在 `App_Code` 加入測試：

   ```csharp
   [TestFixture]
   public class ConfigurationTest
   {
       [Test]   // 檢查 Session 是否啟用
       public void SessionEnableTest()
       {
           Assert.NotNull(HttpContext.Current.Session);
       }

       [Test]   // 檢查 Temp Folder 是否存在且可操作
       public void TempFolderAccessTest()
       {
           string tmpFolder = ConfigurationManager.AppSettings["temp-folder"];
           Assert.True(Directory.Exists(tmpFolder));

           string file = Path.Combine(tmpFolder, "test.txt");
           File.WriteAllText(file, "12345");
           Assert.AreEqual("12345", File.ReadAllText(file));
           File.Delete(file);          // 若刪除失敗會拋出例外
       }
   }
   ```

5. 佈署網站後，先瀏覽 `NUnitLiteTestRunner.aspx`，即可立即知道站點組態是否正確。

關鍵思考點：  
• 讓「環境／組態驗證」與「單元測試」共用同一框架，降低維護成本。  
• 使用 NUnitLite (僅一顆 DLL) 可直接載入 `App_Code`，避免 Web 應用程式中額外開 AppDomain、Thread 所帶來的不確定性。

**Cases 1**:  
背景：將系統佈署到客戶 A 之 IIS，因 Web.config 誤關閉 Session。  
做法：佈署後立刻執行 Runner，`SessionEnableTest` 失敗。  
效益：安裝當下即發現問題，安裝人員只需在 UI 看到 “Fail” 字樣就能回頭調整設定，避免上線後才 Debug。

**Cases 2**:  
背景：客戶 B 將 temp 目錄指到一個唯讀磁碟。  
做法：`TempFolderAccessTest` 於 Runner 中報錯 “Access Denied”。  
效益：在正式上線前找出檔案權限問題，節省一次緊急維運（平均一案 2 小時）的支出。

---

## Problem: 直接使用完整 NUnit 在 Web 應用程式中跑測試會帶來額外負擔與風險

**Problem**:  
想在 Web 專案裡跑單元測試，但完整版本的 NUnit 需要多顆 Assembly，且預設採用獨立 AppDomain 與 Thread 來執行測試；在 ASP.NET 環境下可能引發 Assembly 無法載入（特別是 `App_Code` 動態產生的 Assembly）或權限、效能問題。

**Root Cause**:  
1. NUnit Runner 過於 “肥厚”，載入組件多、設定複雜。  
2. NUnit 為確保測試隔離，預設重新建立 AppDomain，與 ASP.NET 內建生命週期衝突。  
3. `App_Code` Assembly 為動態編譯，NUnit 預設掃描不含該 Assembly，導致測試找不到。

**Solution**:  
改採 “NUnitLite” 這個輕量化版本：  
• 只有一顆 `NUnitLite.dll`，容易與網站一起佈署。  
• 不自動開啟新 AppDomain / Thread，直接在 Web 應用程式目前的執行脈絡執行測試。  
• 明確指定測試目標 Assembly（本例為 `"App_Code"`），可正常找到所有 TestFixture。  

簡易 Runner（同上一節）即可滿足需求：

```csharp
ConsoleUI.Main(new string[] { "App_Code" });
```

**Cases 1**:  
將完整 NUnit 改成 NUnitLite 後，測試執行速度由 1.5 sec 降至 0.3 sec；佈署包大小減少約 3.2 MB → 180 KB。  

**Cases 2**:  
線上網站以 NUnit 進行測試時，因執行期開啟額外 Thread，導致 Session 物件為 null；切換至 NUnitLite 後在相同脈絡內執行，不再出現問題。