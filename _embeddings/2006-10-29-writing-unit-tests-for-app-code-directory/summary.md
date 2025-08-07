# 替 App_Code 目錄下的 code 寫單元測試 ?

## 摘要提示
- JUnit／NUnit: 文章開場說明主流單元測試框架的由來與特性。
- App_Code 機制: ASP.NET 2.0 會自動編譯 ~/App_Code 下的原始碼，帶來方便也帶來限制。
- DLL 缺失困擾: App_Code 沒有固定的實體組件檔，造成測試框架難以載入。
- Hosting 依賴: 置於 App_Code 的程式大量仰賴 HttpContext 等環境物件，脫離 IIS 難以執行。
- NUnit 執行流程: 預設以獨立 AppDomain 執行測試，與 Web Hosting 環境衝突。
- 改框架不可行: 嘗試修改 NUnit 原始碼後發現成本過高而放棄。
- NUnitLite 發現: 透過 Google 找到專為受限環境設計的輕量版框架。
- Vision 符合需求: NUnitLite 去除多 AppDomain、GUI 等重量級功能，適合嵌入式與 Add-in 情境。
- ASP.NET 測試解法: 將 NUnitLite 原始碼直接置入專案，讓測試以與網站相同的 AppDomain 執行。
- 成果與展望: 雖然版本僅 0.1.0.0 且尚未能直接編譯，但已足以解決作者目前問題，後續將示範實際用法。

## 全文重點
作者在開發 ASP.NET 2.0 Web Site 時，想為 ~/App_Code 目錄下的程式撰寫單元測試。傳統的測試框架（如 NUnit 或 Visual Studio 的 Unit Test）都假設被測程式以固定的 DLL 形式存在，並且在獨立於 Web Hosting 的 AppDomain 中執行；然而 ASP.NET Web Site 模型在執行期才把 App_Code 轉成隨機命名的暫存組件，測試程式在設計階段無法得知確切檔名，加上程式強烈依賴 HttpContext、Session、Request 等環境物件，離開 IIS 便無法運作，導致無法以傳統方式進行測試。

作者嘗試直接修改 NUnit 原始碼，將 Runner 的 AppDomain 行為移除，但發現程式碼結構複雜，維護成本過高而放棄。經過搜尋，終於找到目標明確、僅保留 NUnit 部分語法的輕量框架 NUnitLite。NUnitLite 以「只提供本質最需要的功能」為願景，完全以原始碼形式分發，不含 GUI、多執行緒、額外 AppDomain 等「重量級」特性，非常適合在受限或必須與宿主共處的環境（例如嵌入式系統或軟體外掛）直接編譯與運行。對 ASP.NET 而言，只要把 NUnitLite 原始碼放入同一個 Web Site， 測試程式就能和 App_Code 產生於同一個 AppDomain、共享完整 HttpContext，成功解決找不到 DLL 與環境依賴的兩大痛點。

雖然目前的 NUnitLite 只到 0.1.0.0，且最新原始碼尚無法一次編譯通過，但整體概念與實際測試顯示，它已能有效支援作者的需求。文章最後預告將在下一篇詳述如何在實務專案中整合與撰寫測試案例。

## 段落重點
### 主流測試框架與 ASP.NET App_Code 機制
作者先介紹 JUnit／NUnit 的盛行，接著說明 ASP.NET 2.0 Web Site 的 App_Code 自動編譯特性：把原始碼丟進這個目錄即可在 IIS 執行時動態產生組件。便利之餘，也缺乏實體 DLL，使依賴組件路徑的工具陷入困境。

### 為何傳統 NUnit 無法直接測試 App_Code
要撰寫單元測試面臨兩難：1) 暫存組件路徑隨機且深藏於 Temporary ASP.NET Files，測試工具難以定位；2) App_Code 內容倚賴 HttpContext 等 Hosting 物件，離開 IIS 會拋例外。NUnit Runner 為了隔離測試，更在獨立 AppDomain 執行，進一步奪走環境依賴，致使測試無法進行。

### 嘗試修改 NUnit 但宣告失敗
作者不甘心，檢視並 Trace NUnit 核心碼，意圖取消獨立 AppDomain，但 Runner 設計嚴謹且與整體結構緊密耦合。改動意味著必須維護自製的 NUnit 分支，違背「只想跑測試而非維護框架」的初衷，因此作罷。

### 發現並評估 NUnitLite
透過大量搜尋終於找到 CodePlex 上的 NUnitLite。官方 Vision 描述其目標：為資源受限或需嵌入的場景提供最小可行子集，移除 GUI、多執行緒、延伸性、獨立 AppDomain 等重量級功能。這正與 ASP.NET Web Site 的需求不謀而合：測試與程式碼同屬單一 AppDomain，還能直接使用 HttpContext。

### 結論與後續計畫
NUnitLite 雖仍處於早期 0.1.0.0 版本且最新原始碼有編譯問題，但已成功解決 DLL 缺失與 Hosting 依賴兩大難題，足以成為作者的「救星」。文章最後透露將另寫篇幅示範實際整合與測試範例，並對解決方案表達滿意與期待。