# API & SDK Design #4 ─ API 上線前的準備：Swagger + Azure API Apps

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼 API 上線前必須特別重視 Developer Experience (DX)？
API 的使用者與開發者同為工程師，良好的 DX 直接影響他們願不願意採用你的服務。若能在文件、測試、除錯、監控等層面降低門檻，就能大幅提升 API 的學習曲線與後續維運效率。

## Q: API Developer Experience 涵蓋哪四大核心面向？
InfoQ 文章指出的四大面向為：  
1. Functionality：是否有效且優雅地解決問題  
2. Reliability：可用性、擴充性、穩定性等非功能需求  
3. Usability：是否容易被發現、學習、撰寫測試與處理錯誤  
4. Pleasure：使用過程是否愉悅  
作者特別強調在「上線」階段最需要兼顧的是 Reliability 與 Usability。

## Q: 上線前要如何具體檢查 API 的 Usability？
作者將 Usability 細分成五項：  
1. 易於學習與了解：自動化、可操作的文件 (如 Swagger UI 與 IntelliSense)  
2. 易於體驗：線上試玩／測試工具，降低「第一次使用」門檻  
3. 易於測試：提供隔離的 sandbox 或測試環境  
4. 易於除錯：完整的 logging 與 error‐handling 機制  
5. 易於管理與監控：金鑰管理、呼叫次數限制、用量警示等

## Q: 為達成上述需求，作者最終採用了哪些工具與服務？
1. Swagger (及 .NET 的 Swashbuckle 套件) ‒ 處理文件、線上測試、SDK 產生  
2. NLog + ELMAH ‒ 統一例外與日誌管理  
3. Azure App Service / API Apps ‒ 負責佈署、監控、擴充與環境管理

## Q: 為何選擇 Swagger 作為 API Framework？
Swagger 以 JSON 形式描述 HTTP API，並擁有完整的生態系：  
• Swagger UI → 動態文件 + 線上 Try-it-out 測試  
• Code Generator → 可產生多語言的 Client SDK 與 Server Skeleton  
• Swagger Editor / Hub → 協同編輯與版本管理  
透過 Swashbuckle，.NET 開發者可直接從程式碼反向產生 Swagger 定義與 UI，解決文件、測試與 SDK 的大部分痛點。

## Q: 在 ASP.NET Web API 中如何啟用 Swashbuckle 產生 Swagger UI？
1. 以 NuGet 安裝 Swashbuckle  
2. 在 `SwaggerConfig.cs`：  
   • 指定 XML comments 路徑 (IncludeXmlComments)  
   • 處理 action 衝突 (ResolveConflictingActions)  
   • 開啟 `EnableSwaggerUi()`  
3. 重新編譯後，瀏覽 `/swagger` 即可看到文件與即時測試介面，同時 `/swagger/docs/v1` 提供 JSON 定義。

## Q: 使用 Swagger Editor 可自動產出哪些程式碼？
Swagger Editor 可一鍵產生：  
• Server Side：如 ASP.NET Web API Skeleton  
• Client Side：例如 C# .NET 2.0 SDK  
產生的專案已含 Model 與 API Wrapper，能做為快速開發或撰寫自訂 SDK 的起點。

## Q: Azure API Apps 為 API Hosting 帶來哪些主要優勢？
1. 內建 HTTPS：所有 `*.azurewebsites.net` 網域自帶 SSL 憑證  
2. API Settings：GUI 方式設定 Swagger 定義 URL 與 CORS  
3. Logging & Diagnostics：Log Stream、Application Insights、Alert 等即時監控工具  
4. Deployment Slots：多版本佈署、秒級 Swap、快速 Rollback  
這些功能讓開發者專注在 API 本身，將維運成本交由平台處理。

## Q: Deployment Slots 在實務上可解決哪些痛點？
• 上線前可在 Staging/Test Slot 以正式設定驗證新版本，測試完成後一鍵 Swap 上線  
• 發生異常時可秒級回切至前一版本  
• 可額外建立 Sandbox Slot，供外部開發者無風險地測試 API

## Q: 作者對長期維護 API 相容性仍面臨哪些挑戰？
Swagger 雖能產生定義與程式碼，但尚缺乏「在編譯或 CI 階段自動比對 Contract 與實作是否一致」的利器。目前作者以單元測試補強，未來仍尋求更自動化的檢測方法。