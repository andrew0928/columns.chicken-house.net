# 利用 NUnitLite，在 App_Code 下寫單元測試

## 摘要提示
- Web Config 檢查: 透過單元測試把「環境設定正確性」納入自動化驗證流程。
- NUnitLite 適用: 相對於完整的 NUnit，NUnitLite 體積小、相容 Web 環境、不會額外建立 AppDomain。
- App_Code 整合: 測試程式直接放在 App_Code，部署時無須另外編譯組件。
- Browser Test Runner: 以 ASP.NET 頁面簡單包裝 ConsoleUI，瀏覽器即可看到測試結果。
- Session 檢查: 範例示範如何驗證 Session 是否啟用。
- TempFolder 測試: 示範讀寫刪除暫存檔，確保應用程式可存取指定目錄。
- 五步驟流程: 建站、引用 DLL、撰寫 Test Runner、撰寫 TestFixture、部署驗證。
- IE 顯示問題: 若瀏覽器把純文字誤當 XML，可直接檢視原始碼取得結果。
- NUnit 與 NUnitLite 比較: NUnitLite 無多餘組件、無額外執行緒，更適合小型 Web 專案。
- 實務價值: 在未必有完整 QA 流程的專案中，用現有單元測試框架做額外環境自檢最經濟。

## 全文重點
本文以實務導向的角度，說明如何在 ASP.NET 2.0 Web Site 中利用 NUnitLite 進行單元測試，並將「確認部署環境與組態設定正確」也納入測試範圍。作者指出 Web-based 應用程式常被安裝於多個不同站台，由不熟程式的人員操作，若能在發佈前即自動驗證 Session 是否開啟、暫存目錄是否可存取，能大幅減少線上問題。文中提供一個名為 NUnitLiteWebSite 的範例專案，示範以下五個步驟：

1. 建立 Web Site 專案。
2. 下載並編譯 NUnitLite 原始碼，加入專案參考。
3. 新增 NUnitLiteTestRunner.aspx，將 ConsoleUI 的輸出導向 Response，使瀏覽器可直接呈現測試結果。
4. 在 App_Code 目錄撰寫 TestFixture，實作 SessionEnableTest 與 TempFolderAccessTest，分別驗證 Session 與暫存目錄。
5. 部署網站後，先開啟 NUnitLiteTestRunner.aspx 觀看結果；若組態有誤（例如 web.config 關閉 Session），測試會立即失敗。

作者分享執行結果截圖，並說明若 IE 將純文字誤判為 XML，可用「檢視原始碼」取得輸出。最後比較 NUnit 與 NUnitLite：前者組件多、會額外建立 AppDomain 與執行緒，不建議直接用在 Web Site；後者精簡、載入 App_Code 無阻，對中小型 Web 專案更符合「快速、方便」的需求。文章以幽默口吻結語，鼓勵讀者將類似環境檢查納入單元測試，提升部署成功率。

## 段落重點
### 前言與動機
作者延續前一篇文章，說明公司產品屬於 Web-based，經常被安裝到多個站台，由於安裝人員未必懂程式，光靠人工檢查容易遺漏設定。他主張把「環境與組態驗證」視為單元測試的一部分，利用現成框架降低實作成本。

### Step 1 建立 Web Site Project
示範先於 Visual Studio 建立一般 ASP.NET 2.0 Web Site，並提供完整範例下載連結 NUnitLiteWebSite.zip，做為後續示範基礎。

### Step 2 引用 NUnitLite.dll
指引讀者至 NUnitLite 官方網站下載原始碼自行編譯，再把生成的 NUnitLite.dll 加入專案參考，以取得測試框架核心功能。

### Step 3 實作 NUnitLiteTestRunner.aspx
透過三行程式碼：設定回應類型為 text/plain、把 Console 輸出導向 Response、呼叫 ConsoleUI.Main() 掃描 App_Code 執行測試，輕鬆把 Console 版 Runner 移植到瀏覽器環境。

### Step 4 撰寫 TestFixture
在 App_Code 新增 ConfigurationTest 類別，包含兩個 [Test] 方法：SessionEnableTest 驗證 HttpContext.Current.Session 不為空；TempFolderAccessTest 檢查 web.config 的 temp-folder 存取權限，能建立、讀取、刪除檔案，確保目錄權限正確。

### Step 5 部署與執行
將網站發佈到目標伺服器後，先開 NUnitLiteTestRunner.aspx 觀察測試結果；若全部通過代表環境正確，若關閉 Session 等設定錯誤，頁面立即顯示失敗訊息，方便快速回饋。

### NUnit vs. NUnitLite 與結論
作者說明完整 NUnit 雖功能豐富，但組件眾多、會額外產生 AppDomain 與執行緒，且無法直接載入 App_Code，不適合輕量 Web Site；NUnitLite 則體積小、整合無負擔。透過本文步驟，開發者可把重要環境檢查自動化，提升部署品質，對中小型專案尤其划算。最後作者以輕鬆語氣邀請讀者鼓掌並實際試用。