# API & SDK Design #4：API 上線前的準備－Swagger + Azure API Apps

## 摘要提示
- DX 思維: API 上線前要從開發者體驗的「功能、可靠度、可用度、愉悅度」全面檢視。
- Usability 核心: 文件自動化、線上試用、測試隔離與除錯支援是降低 API 進入門檻的關鍵。
- Swagger: 以 JSON 描述 API Contract，形成文件、測試、CodeGen 一條龍工具鏈。
- Swashbuckle: 在 ASP.NET WebAPI 內自動產生 Swagger Definition 與 UI，並可讀取 XML Comments。
- Code First vs. Definition First: 介紹兩種開發流程及現階段自動化檢查的缺口。
- Azure API Apps: 提供 HTTPS、Swagger 註冊、CORS、Log/Monitor、Slots 等營運機制，一鍵解決維運痛點。
- Log 與除錯: 結合 NLog、ELMAH 與 Azure Log Stream，快速定位生產問題。
- Deployment Slots: 用於藍綠部署、測試沙箱與快速回滾，強化 DevOps 流程。
- API 管理挑戰: 權杖控管、流量監視與費用告警需透過後續的 Azure API Management 完成。
- 結論: 選對工具與雲端平台，可將維運雜務外包，專注於 API 本身的價值與演進。

## 全文重點
本文聚焦於「API 服務在程式完成之後正式上線前必須思考的事項」，核心主題為如何提升 Developer Experience（DX）以及如何挑選合適的雲端 Hosting。作者首先以「功能、可靠度、可用度、愉悅度」為框架，歸納出五大實務需求：學習與文件、體驗與導引、測試隔離、除錯追蹤、用量監控。接著將需求拆成三大技術面向──API Framework、System Service、Operation，並分別以 Swagger、Swashbuckle、NLog/ELMAH 與 Azure API Apps 對應解決方案。文章第二段深入介紹 Swagger 生態系：以 JSON 描述 API；透過 Swashbuckle 在 .NET WebAPI 中逆向產出 Definition、Swagger UI；再利用 Editor 產生 Client/Server Code，提高文件與測試自動化程度。作者也討論 Code First 與 Definition First 兩條流程，指出目前無法於編譯期自動比對 Contract 與實作的一大缺口，暫以單元測試輔助。

第三段說明 Azure API Apps 為何適合作為 API Hosting：平台內建免費 HTTPS、Swagger 入口與 CORS 設定，不需自行維護；Diagnostics 與 Log Stream 讓線上除錯即時化；Deployment Slots 支援藍綠部署及沙箱測試，降低上線風險；此外還可結合 Application Insights 進行進階監控。最後作者以實務經驗提醒：在 DevOps 時代，選擇成熟的雲端服務可顯著降低維運成本，讓團隊專注在 API 本身的演進與相容性控制。本文透過具體範例與設定步驟，完整展示從開發、測試、部署到營運的最佳實踐。

## 段落重點
### 除了寫好 API service 之外，你還需要些什麼?
API 上線不能只看程式碼，必須回到「誰要用、怎麼用」的本質。作者引用 InfoQ 的 DX 四要素，指出在 Hosting 階段「可靠度」可交給雲端平台，但「可用度」需仔細設計：文件呈現方式要可搜尋、可互動；新手體驗必須零安裝即可試跑；測試過程需有隔離環境；錯誤與日誌要能快速回溯；用量與權限必須有監控與告警。這些需求將影響後續技術選型與架構劃分。

### 1. API 是否易於學習與了解?
傳統 PDF/Word 已不足；理想狀態是程式註解能自動轉文件並在 IDE 中即時提示。選型時要考慮文件生成與開發流程能否無縫整合，例如 C# XML Comments 結合 Swagger 即可達到「自動化、可執行」的文件效果。

### 2. API 是否易於學習及體驗?
降低第一次嘗試的摩擦力是提升 DX 的捷徑。類似 Facebook 的 Social Plugins 或 JS Console，透過線上互動式工具，讓開發者「點擊即執行」並觀察結果，省去本機安裝、環境設定與程式碼骨架的時間。

### 3. API 是否易於測試?
良好的 API 應提供 Sandbox 或模式切換以支援自動測試與壓力測試；若僅有正式環境，開發者難以進行 TDD 或 CI/CD。設計時要能隔離測試資料、模擬金流等副作用，以確保測試不影響真實交易。

### 4. API 是否易於除錯? 追查 LOG?
安全考量常讓錯誤訊息被隱藏，但對開發者而言細節越多越好。需同時具備精確的例外回報機制與可搜尋的集中日誌，並能與 Hosting 平台整合，縮短問題定位時間。

### 5. API 是否易於管理? 監控?
API 若無用量與權杖控管，易遭濫用。理想方案應提供 API Key 發放、流量警戒、超額停用與費用告警等功能。若不自行開發，則需選擇具備相關服務的雲端或第三方平台。

### Swagger, Best API Framework & Tool chain
Swagger 以標準 JSON 定義 API，伴生的工具鏈涵蓋 Editor、UI、CodeGen、Registry。作者於 ASP.NET WebAPI 透過 Swashbuckle 採「Server Code First」流程：先寫 Controller，再自動產生 Definition 與 Swagger UI，並載入 XML Comments；在 UI 中可即時試調 API；利用 Editor 又能反向生成多語言 Client 或 Server Skeleton，加速 SDK 與文件同步。

### 1. 指定 xml comments 檔案路徑
在專案屬性開啟 XML Documentation，再於 SwaggerConfig.cs 透過 IncludeXmlComments 指向輸出路徑，Swagger UI 即可同步顯示 method 註解，文件與程式零時差。

### 2. 排解 API Action 衝突
因 Swagger URL 不含 QueryString，遇到 Route 重疊需手動 ResolveConflictingActions。作者採以第一筆為準的預設策略，提醒讀者依專案需求調整。

### 3. 啟用 Swagger UI Support
於 EnableSwaggerUi 區段解除註解即可開啟互動式文件；瀏覽 /swagger 便能查看所有 Endpoint 及嘗試呼叫，改善學習曲線。

### 4. 其他的用法
Swashbuckle 還支援多版本、OAuth2、篩選器等進階功能，可參考官方 GitHub 進一步設定，以符合較複雜的實務場景。

### 5. 測試 Swagger UI
實際執行後，Swagger UI 可列出 API、顯示摘要與參數，並返回 JSON 結果；Definition URL（/swagger/docs/v1）則供其他工具存取。

### 6. 測試 Swagger Code Generator
將 Definition 貼入 Swagger Editor，可生成 ASP.NET5 伺服端骨架或 C# .NET2.0 用戶端 SDK；產生的 Controller 包含 Route、註解與 Model，省去大量樣板工作。

### 7. Swagger 使用心得
Swagger 生態完整，但目前缺乏「編譯期 Contract 檢查」能力，無法在 CI 階段自動偵測實作與定義不符；作者暫以單元測試彌補，並期待更完善的工具或流程。

### Azure API Apps, 專為 API 設計的 hosting environment
Azure API Apps 建立在 App Service 之上，針對 API 場景預設最佳化。它內建 SSL、Swagger 註冊、CORS、診斷、監控，並支援水平/垂直擴充與 Deployment Slots。選用 Azure 可將可靠度與維運需求外包，開發者得以專注於核心邏輯。

### 1. 內建 HTTPS 支援
所有 *.azurewebsites.net 網域自帶 Microsoft SSL 憑證，即使使用 Free Plan 也能立即提供安全通訊，省去證書購買與更新麻煩。

### 2. API settings (swagger, CORS) 支援
Portal 介面可直接設定 Swagger Definition URL 與 CORS 白名單，修改無須重佈署；讓服務自動被其他 Azure 元件探索，亦保障瀏覽器跨源呼叫安全。

### 3. 內建 Logging, Alert, Diagnostic 的支援
透過 Diagnostic Logs、Log Stream、Application Insights，可即時或事後檢視錯誤與性能指標。作者示範如何開啟 FileSystem Logs，並用 Log Stream 快速定位缺失 XML Comments 導致的 Swagger 例外。

### 4. 支援多個測試區域及組態－Deployment Slots
Slots 讓同一服務擁有多組 URL 與組態，可用於 Beta 測試、藍綠部署或開發者 Sandbox。Swap 操作數秒內完成，上線失敗亦能迅速回滾，符合 DevOps 快速迭代需求。

### 5. Azure API Apps 使用心得
App Service 歷經多年成熟，功能齊備；挑選正確平台可大幅降低維運門檻，把團隊資源集中在 API 價值，而非底層基礎設施。

### 結論
API 上線不只是程式碼 deploy，還包含文件、測試、監控、版本演進與快速回滾的全生命週期管理。透過 Swagger + Azure API Apps 的組合，可在開發端獲得自動化文件與 SDK，在雲端端取得 SSL、診斷、部署及擴充支援，整體 DX 與可靠度同步提升。下一步將面臨版本演進的相容性挑戰，作者預告將於後續文章探討多版本共存策略。