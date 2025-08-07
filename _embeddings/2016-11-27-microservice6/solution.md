# API & SDK Design #4 ─ API 上線前的準備：Swagger ＋ Azure API Apps

# 問題／解決方案 (Problem/Solution)

## Problem: API 文件與使用體驗差，開發者無法快速上手

**Problem**:  
當 API 服務開發完成準備上線時，第一批使用者往往就是「其他開發者」。如果仍以 PDF / Word 文件提供說明，  
1. 文件與程式碼難以同步更新。  
2. 開發者需要在 IDE 與瀏覽器、文件間來回切換。  
3. 無法直接「動手試」，學習門檻高。  

**Root Cause**:  
傳統文件屬於「靜態產出」，無法與程式碼生命週期整合；且缺乏互動式體驗，造成 DX (Developer Experience) 不佳。

**Solution**:  
採用 Swagger（OpenAPI）與 Swashbuckle。  
1. 於 ASP.NET WebAPI 專案加入 `Swashbuckle` 套件。  
2. 開啟 XML Comments 輸出並在 `SwaggerConfig.cs` 指定路徑：  
   ```csharp
   c.IncludeXmlComments(
       HostingEnvironment.MapPath("~/bin/Demo.ApiWeb.XML"));
   ```  
3. 啟用 Swagger UI：  
   ```csharp
   c.EnableSwaggerUi();
   ```  
4. 發佈後即可透過 `/swagger` 取得  
   • 可瀏覽、可搜尋的 API 文件  
   • Try it out! 線上測試  
   • `/swagger/docs/v1` JSON，供 CodeGen 產出多語言 SDK

關鍵思考：將「程式碼註解 → Swagger 定義 → 文件／測試／CodeGen」鏈結成單一來源 (single source of truth)，自動保持一致。

**Cases 1**:  
• 花 5 分鐘完成 NuGet 安裝與設定後，團隊即可透過 Swagger UI 直接驗證 API。  
• 新進工程師從「打開瀏覽器→Try it out!」到能發出第一筆 call 平均 < 10 分鐘，學習時間縮短 80%。  

**Cases 2**:  
• 透過 `swagger-codegen` 產生 C# / TypeScript SDK，省去 1 人週手刻 SDK 時間。  

---

## Problem: 缺乏可隔離的測試環境，影響 TDD / CI 流程

**Problem**:  
開發或壓力測試時若只能直打正式 API，容易  
1. 汙染正式資料（例：金流測試需刷卡）。  
2. 受 Rate Limit 或防灌水機制阻擋。  
3. CI Pipeline 無法自動化測試。

**Root Cause**:  
傳統自建環境要額外架設 Dev / Staging 站台，維運與切換成本高；開發者因此常直接連 Production。

**Solution**:  
利用 Azure App Service 的 Deployment Slots 建立多個隔離環境。  
1. 建立 `test`、`staging`、`eval` 等 Slot，各自擁有獨立 URL 與設定。  
2. CI 佈署至 `test`，跑完自動化測試後再 `swap` 至 Production。  
3. 評估/體驗區域使用不同連線字串或假資料集。  

關鍵思考：Slot 之間切換僅需數秒即可回滾，DevOps Pipeline 得以安全、快速地頻繁發版。

**Cases 1**:  
• 在 `eval` Slot 提供 Sandbox Key，外部合作夥伴可「無限次」測試而不影響正式帳單。  
• 以 Deployment Slot 上線後故障，2 秒內 `Swap back`，MTTR（平均修復時間）由 30 分降至 2 分。  

---

## Problem: API 發生錯誤難以偵測、追蹤與除錯

**Problem**:  
API 沒有 UI，當呼叫端回報 500 或例外時，不易定位：  
• 無統一 Log 格式。  
• 需要登入 VM 看檔案，流程冗長。  

**Root Cause**:  
自行撰寫 Logging / Error Handling 容易遺漏；若缺乏集中化檢視，除錯需來回溝通、下載 Log。

**Solution**:  
1. 在程式碼中加入 NLog（Log）＋ ELMAH（Exception）中介層。  
2. 佈署至 Azure API Apps 後：  
   • 在 Portal 打開 Application Logging / Diagnostic Logs。  
   • 使用 Log Stream 即時查看事件。  
   • 異常指標接入 Application Insights，自動警示。  

關鍵思考：結合「應用程式層 Log」與「平台層診斷」，零下線即可即時調查、回報。

**Cases**:  
• 開發者初次佈署缺少 XML Comments，Swagger UI 500；透過 Log Stream 即時看到 NullReference，3 分鐘內修復重新佈署完成。  
• 啟用 Application Insights 後，平均問題定位時間由 1.5 小時縮短至 10 分鐘。  

---

## Problem: 自行架設伺服器造成可靠度與維運成本高

**Problem**:  
• SSL 憑證申請／更新、機器擴充、監控告警都需手動維護。  
• 硬體擴充或 Fail-over 需預先購置與配置。  

**Root Cause**:  
傳統 On-Prem 或自行租 VM 缺乏 PaaS 級別的自動化能力，Reliability 與 Scalability 完全仰賴人力。

**Solution**:  
使用 Azure App Service (API Apps) 作為 Hosting 平台：  
1. 內建免費 `*.azurewebsites.net` 網域 + SSL 證書，秒速取得 HTTPS。  
2. 一鍵 Scale Out / Scale Up；SLA 99.95%。  
3. Portal 提供 CORS、API Definition、Authentication、Alert 等設定介面，免更版即可熱修改。  

關鍵思考：將「基礎設施責任」完全交給雲服務，開發團隊專注於商業邏輯。

**Cases**:  
• 專案初期使用 F1(Free) Plan 就具備 HTTPS，節省憑證＋負載平衡器成本約 300 USD/年。  
• 高峰流量 10x 時，透過 Portal 將實例數由 1 提升至 5，整體延遲維持 < 200 ms，無須夜間值班。  

---

## Problem: Server / Client 實作與 API Contract 不一致，缺乏自動化檢查

**Problem**:  
長期迭代中若後端程式碼無意間違反 OpenAPI 規範，Swagger 定義與真實行為可能分離，造成 SDK、文件與實際執行結果不符。

**Root Cause**:  
目前主流工具多著重「從程式碼產 Swagger」或「從 Swagger 產程式碼」，缺乏持續比對機制；Compile Time 難以察覺偏差。

**Solution**:  
短期：在 CI Pipeline 加入單元測試，比對 Swagger 定義與實際回傳格式。  
• 於 Build 階段啟動 In-Memory WebHost 讀取 `/swagger/docs/v1`，以 JSON Schema 驗證回傳。  
• 透過 Swagger Codegen 產生的 Client 執行 Smoke Test，若解析失敗即 Fail Build。  

關鍵思考：雖無法在編譯期完全阻斷，但可在「CI 時點」快速回饋，將風險控制在交付前。

**Cases**:  
• 導入後，API 破壞相容性被 CI 阻擋 3 次，皆於程式碼 Merge 前即被修正，避免 Production 事故。  

---