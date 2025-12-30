---
layout: synthesis
title: "API & SDK Design #4, API 上線前的準備 - Swagger + Azure API Apps"
synthesis_type: summary
source_post: /2016/11/27/microservice6/
redirect_from:
  - /2016/11/27/microservice6/summary/
---

# API & SDK Design #4, API 上線前的準備 - Swagger + Azure API Apps

## 摘要提示
- DX（Developer Experience）: API 使用者是開發者，需以功能、可靠度、可用性與愉悅感來設計整體體驗。
- Usability 重點: 文件自動化、可探索性、快速體驗與可測試性是 API 上線前的核心。
- Reliability 與雲端: 可靠度可交由雲端服務保障，選對平台可快速達到可用性、延展性與穩定性。
- Swagger 生態系: 以標準 JSON 定義 API，串起文件、UI測試、Client/Server 代碼生成等完整工具鏈。
- Swashbuckle 實務: 在 ASP.NET WebAPI 透過註解與設定自動產生 Swagger 定義與 Swagger UI。
- 測試與除錯: 提供分離的測試環境、良好 logging 與例外處理機制，降低開發摩擦。
- API 管理與監控: 需涵蓋授權金鑰、呼叫頻率、異常警示與用量保護，避免濫用與成本失控。
- Azure API Apps: 內建 HTTPS、CORS、Swagger 設定、診斷與監控、Deployment Slots，降低維運門檻。
- DevOps 友善: 部署插槽支援預備上線、快速回滾與體驗區，促成持續交付實踐。
- 合約一致性挑戰: Swagger 難在編譯時驗證 code/contract 一致性，需以單元測試與 CI 補強。

## 全文重點
本文聚焦 API 上線前的整備，從 DX（Developer Experience）出發，強調 API 的使用者即是開發者，應以更自動化、可操作的方式提供文件與體驗，而非傳統 PDF。作者將考量分成三大面向：API Framework（文件、體驗、工具鏈）、API system service（Log 與錯誤處理）、API Operation（監控、擴充、高可用）。工具上選擇以 Swagger 打造 API 合約與工具鏈、NLog+ELMAH 進行記錄與錯誤追蹤、Azure App Service（API Apps）作為託管環境。

在 Usability 層面，作者提出五大問題：是否易於學習與了解（自動化文件、IntelliSense 友好）、是否易於學習及體驗（線上互動測試與體驗工具）、是否易於測試（提供獨立測試區域，避免在正式環境進行破壞性操作）、是否易於除錯（可用的 logging 與詳細錯誤訊息給開發者）、是否易於管理與監控（授權、配額、異常告警與用量上限）。這些需求引出對應方案：以 Swagger 提供可探索文件與即時測試、以成熟 logging/error handling 套件強化可觀測性、以雲端平台提供監控、擴展與部署機制。

Swagger 作為核心 API Framework，透過標準 JSON 定義形式建立生態系，可生成文件、互動式測試 UI、Client/Server 代碼，並與後端定義同步。作者在 ASP.NET WebAPI 採用 Swashbuckle：啟用 XML 註解整合、處理 action 衝突、開啟 Swagger UI，並示範使用 Swagger Editor 生成伺服端與客戶端程式碼。雖實用，但作者指出以 Swagger 目前難以在編譯期驗證 code 與 contract 完全一致，若採 Code First 或 Definition First 皆需在 CI 階段以單元測試補強相容性驗證。

託管方面，Azure API Apps 提供 API 專用設定與運維能力：預設 HTTPS、API Definition 與 CORS 管理、診斷與 Log Streaming、Application Insights、以及 Deployment Slots 實現預備上線與快速回滾。Deployment Slots 亦可作為對外開發者測試體驗區，達成與正式環境隔離。這些能力讓團隊把心力放在服務本身而非維運瑣事，促成 DevOps 與持續交付的落地。

結尾總結：善用 Swagger 與 Azure API Apps 等工具，可大幅提升 API 的 DX 與上線效率，使服務更接近大廠標準。下一步的挑戰是版本演進下的相容性維持，需規劃合約管理與多版本支援策略。

## 段落重點
### 除了寫好 API service 之外，你還需要些什麼?
本文先定義 API DX 的四要素：功能、可靠度、可用性、愉悅感。上線前重點落在 Reliability 與 Usability。可靠度多由雲端平台提供；可用性則聚焦於開發者學習與使用的流暢度。作者從實務出發提出五大檢核：1) 易學易懂：文件應自動化、可操作，與開發流程結合（如 XML 註解+IntelliSense）。2) 易學及體驗：提供線上互動工具與範例，讓開發者零安裝即可測 API（如 Facebook Plugins/Test Console）。3) 易於測試：配置獨立測試區域與資料，不影響正式環境，支援壓測與自動化。4) 易於除錯：完善 logging 與錯誤處理，對開發者回傳足夠細節。5) 易於管理與監控：授權金鑰申請、用量/費率與異常警示、配額保護等，以避免濫用與成本風險。對應到方案層面，作者將需求歸為三類：API Framework（文件、體驗、工具鏈）、API system service（Log/Exception）、API Operation（監控/擴充/HA）。最後明確選擇：Swagger 解決文件與工具鏈；NLog+ELMAH 解決記錄與錯誤；Azure App Service（API Apps）解決部署、監控、擴展與多環境。

### 1. API 是否易於學習與了解?
強調文件必須內嵌於開發流程，從純文件轉向可操作與自動化的文件。以 C# XML 註解結合 IntelliSense 與自動生成說明為例，讓開發者在編碼時即見文件，降低查詢成本。理想狀態是文件與服務版本同步，從開發、維護、發佈一氣呵成。Action：導入能與流程整合的 API 文件方案。

### 2. API 是否易於學習及體驗?
降低初用門檻至關重要。最佳實踐是提供線上體驗工具（配置器、互動式範例、線上 Console），讓使用者只需瀏覽器即可嘗試，避免事前準備伺服器、專案與編輯器等。Action：選擇能提供即時呼叫與觀察結果的工具（如 Swagger UI），盡量避免自建。

### 3. API 是否易於測試?
API 開發需反覆驗證。若無獨立測試環境，將迫使開發者在正式環境做不合適操作（如金流測試）。需提供隔離的測試區、測試帳號與資料、甚至壓測能力，支援 DevOps/TDD/CI 流程。Action：在設計與託管上規劃測試隔離與安全邊界。

### 4. API 是否易於除錯? 追查 LOG?
API 將細節封裝於後端，遇錯需快速定位。建議提供細緻的開發者導向錯誤訊息、完善日誌、可查詢與關聯追蹤能力。安全上對終端使用者可節制，但對開發者需透明。Action：導入集中式 log 管理與一致的例外處理策略。

### 5. API 是否易於管理? 監控?
API 經營是攻防戰，既要促使用也要防濫用。需涵蓋：授權金鑰申請、使用狀況監控、異常用量告警、配額/費用保護與自動中斷。Action：評估現成套件與平台能力，以簡化自建成本。

### Swagger, Best API Framework & Tool chain
Swagger 以 JSON 定義 API 合約，形成完善生態：定義、文件、互動式 UI、Client/Server Codegen、Registry/Hub 等。作者採 ASP.NET WebAPI + Swashbuckle，走 Server Code First：由程式碼與 XML 註解自動產生定義與 UI，並以 Swagger Editor 生成客戶端與伺服端骨架。實作要點含：啟用 XML 註解輸出、處理路由衝突、開啟 Swagger UI。優勢在快速提供文件與體驗、加速 SDK 產生與一致性；限制在難以於編譯期驗證 code/contract 同步，Definition First 與 Code First 各有利弊。現階段以單元測試與 CI 加強契約相容性檢查，彌補編譯期缺口。

### 1. 指定 xml comments 檔案路徑
在專案屬性啟用 XML documentation，並於 SwaggerConfig 指定 XML 路徑，讓 Swagger UI 顯示程式內註解。此作法把「文件」內嵌於程式設計，確保說明與代碼同步更新，降低文件維護成本，且於 IntelliSense 與 UI 一次貢獻，符合 DX 易學易懂原則。

### 2. 排解 api action 衝突
Swagger 2.0 映射規則與 WebAPI 差異可能導致相同路徑/方法的 action 衝突（如含 query 的分頁 GET）。可在設定中以策略挑選優先 action 或合併描述。此步驟確保定義檔可被正確生成與消費，避免 UI 與 Codegen 中斷。

### 3. 啟用 swagger ui support
解除設定中的註解啟用 Swagger UI，於 /swagger 提供互動式文件與試調工具。開發者可直接在瀏覽器輸入參數、Try it out 即時取得回應，達成「零安裝、即測試」，有效降低首次體驗與問題定位時間。

### 4. 其他的用法
Swashbuckle 尚支援更多特性（如安控、版本化、過濾器、擴充欄位等），可視需求前往 GitHub 深入。此彈性讓團隊能逐步擴張契約治理、鑑權與文件品質，而不必一次到位，降低導入阻力。

### 5. 測試 swagger ui
示範實際運行 Swagger UI 與定義端點（/swagger/docs/v1），確認 XML 註解顯示與互動測試可行。此步讓團隊與外部開發者共用單一真實來源的合約與行為觀測窗口，縮短認知差距。

### 6. 測試 swagger code generator
以 Swagger Editor 匯入定義後，生成 ASP.NET WebAPI 骨架與 C# 客戶端 SDK。產物包含 model 與 API 類別，結構完整、可作為 SDK 起點。此流程提升一致性與交付速度，避免手刻錯誤並促進多語言支援。

### 7. Swagger 使用心得
Swagger 生態在定義、文件、測試與 Codegen 上相當成熟，足以成為首選。挑戰在 contract 與 code 的一致性難以於編譯期保證；無論 Code First 或 Definition First，重生成與合併皆有成本。作者建議以 CI 的單元測試把關相容性，待未來工具成熟再補足編譯期驗證空白。

### Azure API Apps, 專為 API 設計的 hosting environment
選擇雲端託管以專注業務邏輯。Azure API Apps（屬 App Service）提供 API 友善功能：預設 HTTPS、API Definition 設定、CORS 管理、診斷與 Log Streaming、Application Insights、與 Deployment Slots。以這些能力可大幅降低維運門檻，快速監控、擴展與回滾，並建立獨立測試/體驗區，完整支援 DevOps 與 CI/CD 流程。對開發者而言，不必自建伺服器與機制，即可獲得企業級可靠度與觀測性。

### 1. 內建 https 支援
App Service 預設提供 *.azurewebsites.net 網域與憑證，免費層亦可用，免除 SSL 佈建與續期成本。對 API 而言，傳輸加密是基本盤，平台內建可立即啟用，縮短上雲工期並提升安全基準線。

### 2. API settings (swagger, cors) 支援
Portal 內可設定 API Definition（Swagger URL）與 CORS 白名單。若已使用 Swashbuckle，貼上定義端點即可供平台或整合服務探索。CORS 從 web.config 解耦，改以平台層控管，變更無須重新部署，讓體驗型前端更易整合。

### 3. 內建 logging, alert, diagnostic 的支援
即使應用未埋 Log，也可透過平台診斷與 Log Streaming 即時查看輸出，或下載歷史檔調查。結合 Application Insights 可獲取更完整的遙測、追蹤與查詢。作者示範以診斷找出 Release 未產出 XML 註解導致 Swagger 例外，快速定位並修復。

### 4. 支援多個測試區域及組態，可以快速切換上線的 Deployment Slots
Deployment Slots 允許建立多個插槽（如 test、staging），各自有獨立 URL 與設定。可在真實環境測試新版本，一鍵 swap 即可上線，故障再快速回滾。亦可用作對外開發者的「體驗區」，以正式程式碼+測試設定提供安全可控的試調場域。

### 5. Azure API Apps 使用心得
App Service 作為成熟的託管環境，功能完整、操作門檻低，能把維運的「柴米油鹽」標準化與平台化。對團隊而言，可將人力集中在產品價值與 DX 打磨，而非環境建置與維護，實質提升交付效率與服務品質。

### 結論
上線前的關鍵在於用對工具與平台，將 DX 需求（文件、體驗、測試、除錯、管理）以 Swagger 與 Azure API Apps 系統性落地，讓小團隊也能具備大廠水準。接下來的課題是版本演進下的相容性維護，需規劃合約治理與多版本策略，並以 CI/測試制度化把關，確保從 1.0 平穩邁向 1.1、1.2 乃至 2.0。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - HTTP/REST 基本概念與狀態碼
   - JSON 與序列化、API 契約觀念（Contract-first vs Code-first）
   - ASP.NET Web API 基礎（Controller、Routing、Filters）
   - Swagger/OpenAPI 基礎與 Swashbuckle 使用
   - 雲端基礎：Azure App Service/API Apps、CORS、HTTPS/憑證
   - 基本日誌與例外處理（NLog、ELMAH）

2. 核心概念（及其關係）：
   - Developer Experience（DX）：由 Functionality、Reliability、Usability、Pleasure 構成；上線階段特別關注 Reliability 與 Usability
   - Swagger/OpenAPI 生態：以 API 定義為核心，驅動文件、UI 測試、Client/Server Codegen 與整合工具
   - Hosting 與運維（Azure API Apps）：提供 HTTPS、CORS、Logging/Diagnostics、監控與 Deployment Slots，強化 Reliability/Usability
   - 測試與除錯：隔離測試環境、日誌與例外處理、線上體驗工具、與 CI/CD 流程銜接
   - 監控與治理：用量監控、授權金鑰/API Token、異常警示與流量控管（延伸至 API Management）

3. 技術依賴：
   - ASP.NET Web API -> Swashbuckle 產生 Swagger 定義與 Swagger UI
   - Swagger 定義 -> Swagger UI（互動文件）與 Code Generator（Client/Server 範本）
   - NLog/ELMAH -> Azure App Service Diagnostics/Log Stream/Application Insights（觀測與追查）
   - Azure API Apps（App Service）-> 內建 HTTPS、API Definition 註冊、CORS、Deployment Slots、Scale/Monitoring
   - CI/CD -> 單元測試彌補契約偏離檢測不足（Swagger 難以在編譯期嚴格驗證）

4. 應用場景：
   - API 上線前後的文件與體驗：即時互動文件、線上 Try-it-out 測試
   - 快速提供測試/體驗環境：以 Deployment Slots 建置 eval/test/staging
   - 多環境設定與快速回滾：swap 上線、遇故障秒級回退
   - 觀測性與故障排除：Log streaming、診斷日誌、例外彙整、即時流量觀察
   - SDK 起步：以 Swagger Codegen 產生初版 Client/Server/Model 作為開發腳手架

### 學習路徑建議
1. 入門者路徑：
   - 了解 REST/HTTP 與 JSON -> 建立最小 ASP.NET Web API 專案
   - 安裝 Swashbuckle -> 開啟 XML Comments -> 看到 Swagger UI 並成功呼叫一支 API
   - 在 Azure 建立 API App（App Service）-> 部署並以預設 HTTPS 測試 -> 啟用 CORS

2. 進階者路徑：
   - 撰寫良好註解與模型綁定，處理 Swagger 衝突（ResolveConflictingActions）
   - 使用 Swagger Editor -> 匯入本機 Swagger JSON -> 產生 Client/Server 範本並比較差異
   - 導入 NLog/ELMAH -> 使用 Azure Diagnostics/Log Stream 排錯 -> 加入 Application Insights
   - 建立 Deployment Slots（test/eval/staging）-> 練習 swap 發佈與回滾

3. 實戰路徑：
   - 設計測試隔離策略與假資料/沙箱流程（避免動到正式金流/訂單）
   - 將 Swagger 定義納入版本控管並於 CI 產物輸出 -> 單元測試驗證 API 行為（彌補編譯期契約驗證不足）
   - 以 Codegen 快速產生 SDK 初版 -> 按需調整封裝與錯誤處理
   - 監控與告警門檻設定（用量異常、延遲、錯誤率）-> 擴展至 API Management 進行金鑰/配額治理

### 關鍵要點清單
- DX 四構面：Functionality/Reliability/Usability/Pleasure；上線聚焦 Reliability 與 Usability (優先級: 高)
- Swagger/OpenAPI 定義為核心：驅動文件、UI 測試、Codegen 與整合 (優先級: 高)
- Swashbuckle：從 ASP.NET Web API 反射產生 Swagger JSON 與 Swagger UI (優先級: 高)
- XML Comments 自動化文件：以程式註解同步生成文件與 IntelliSense (優先級: 高)
- ResolveConflictingActions：處理 Swagger 無法區分的路由衝突 (優先級: 中)
- 互動體驗（Try it out）：降低首次使用門檻、便於快速驗證 (優先級: 高)
- 測試隔離/沙箱環境：支援開發與壓測，避免影響正式資源（如金流） (優先級: 高)
- Logging 與 Exception Handling：NLog + ELMAH 搭配 Azure 診斷/Log Stream (優先級: 高)
- Azure API Apps 內建 HTTPS：零設定即取得 TLS 保護 (優先級: 高)
- API Settings（Definition/CORS）：Portal 管控 Swagger 位置與跨域策略 (優先級: 中)
- Diagnostics/Monitoring：即時流量、事件、應用遙測（App Insights） (優先級: 中)
- Deployment Slots：staging/test/eval 多槽部署、秒級切換與回滾 (優先級: 高)
- Code-first vs Definition-first：選型與流程取捨，影響協作與版本控管 (優先級: 中)
- 契約一致性挑戰：Swagger 難於編譯期強驗；以單元測試與 CI 補位 (優先級: 高)
- 後續治理（API Management）：金鑰、配額、用量監控與告警（延伸議題） (優先級: 中)