# API & SDK Design #4, API 上線前的準備 - Swagger + Azure API Apps

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 API Developer Experience（DX）？
- A簡: DX 是針對開發者的使用體驗，涵蓋功能性、可靠性、可用性與愉悅度，影響學習、整合、測試與維運效率。
- A詳: API DX 是面向開發者的整體使用體驗，包含四個面向：功能性（解決問題的完整度與品質）、可靠性（可用、可擴展與穩定）、可用性（學習與測試門檻、錯誤處理支援）、愉悅度（使用過程的友好感）。在上線階段，可靠性與可用性尤其關鍵，因為它們直接影響開發者能否快速了解、接入與穩定運行你的 API。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q3, A-Q16

A-Q2: API DX 的四大要點是什麼？
- A簡: 功能性、可靠性、可用性、愉悅度。各自對應解題品質、非功能需求、學習測試便利、整體使用感受。
- A詳: DX 的四大要點依序是：功能性（解題能力與品質）、可靠性（可用性、擴展性、穩定性等非功能需求）、可用性（可發現性、學習曲線、測試與錯誤處理支援）、愉悅度（體驗是否愉快）。文章著重於上線前確保可靠性與可用性，包括自動化文件、線上體驗工具、測試隔離、記錄與監控，以及良好 hosting。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, A-Q16

A-Q3: 為何 Reliability 與 Usability 在上線特別重要？
- A簡: 因為它們直接影響可用與可學、可測，確保穩定與開發效率，是 API 被採用的關鍵門檻。
- A詳: 上線後 API 的穩定與可擴展（可靠性）確保服務可承載真實流量；同時可用性確保開發者能快速理解文件、試用、測試、除錯，降低整合成本。雲端平台（如 Azure）可強化可靠性，而 Swagger、線上體驗、XML 註解、自動化文件與良好錯誤處理則提升可用性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q8, B-Q11

A-Q4: 為什麼傳統 PDF/Word 不適合當 API 文件？
- A簡: 難維護、難查閱，無法內嵌於開發流程，缺少自動化與可操作性，易與實作脫節。
- A詳: 靜態文件（PDF/Word）更新、搜尋與對齊版本困難，且無法在 IDE 即時輔助。相對地，透過程式碼 XML 註解與 Swagger 產生可操作文件，能於編譯、IntelliSense 或 UI 中即時呈現，與 API 實作同步，並支援線上嘗試、測試用例與錯誤回饋，顯著提升可用性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q3, B-Q5

A-Q5: 什麼是「可操作的自動化文件」？
- A簡: 由程式與契約自動產出，能即時查閱、互動測試與追蹤更新的文件，如 Swagger UI。
- A詳: 可操作文件指能與系統互動的說明，不只是文字。以 C# XML 註解搭配 Swashbuckle 產生 Swagger 定義與 UI，文件會隨編譯更新，開發者可於 UI 直接嘗試 API、看輸入輸出、觀察回應碼。此種自動化文件降低學習成本並減少文件與實作不一致風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q5, C-Q2

A-Q6: 什麼是 Swagger（OpenAPI）？
- A簡: 一套以 JSON/YAML 描述 HTTP API 的開放規格，並形成完整工具鏈支援文件、測試與程式碼產生。
- A詳: Swagger（現名 OpenAPI）用結構化格式描述端點、參數、模型與回應。它的生態包含 Editor、UI、Codegen 與整合工具。以此規格可自動生成可互動文件、Server/Client 程式碼骨架與 SDK，減少手工同步成本。對 ASP.NET 可用 Swashbuckle 自動從程式反推定義。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q3, C-Q1

A-Q7: Swagger 與 WSDL 有何相似與差異？
- A簡: 皆為介面契約規格；WSDL 主於 SOAP，Swagger 主於 REST/HTTP，且具更豐富網頁化工具鏈。
- A詳: WSDL 定義 SOAP 服務契約，強調 XML 與操作；Swagger 定義 REST/HTTP API，以 JSON/YAML 表述端點、資源與模型。兩者皆使介面契約化，但 Swagger 生態有完善 UI、Editor 與 Codegen，貼近現今 REST 與前後端分離開發模式，學習與整合門檻較低。
- 難度: 中級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q7

A-Q8: Swagger 生態系包含哪些工具？
- A簡: Swagger Editor、UI、Server/Client Codegen、註解與整合工具，涵蓋設計、文件、測試與產碼。
- A詳: 生態系從定義到落地：Editor 支援線上編輯與匯入；UI 將定義轉為互動式文件與測試器；Codegen 生成多語系 Server/Client 程式碼；另有註解套件（如 Swashbuckle）與整合平台（如 SwaggerHub）。如此連接契約、開發、測試與發布，提升可用性與一致性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, C-Q5

A-Q9: 什麼是 Swashbuckle？在 ASP.NET 的角色？
- A簡: ASP.NET WebAPI 的 Swagger 產生器，從程式與 XML 註解自動輸出定義與 UI。
- A詳: Swashbuckle 於 ASP.NET WebAPI/ASP.NET Core 中擔任「反向生成」角色，讀取控制器、路由與 XML 註解，輸出 OpenAPI 定義與 Swagger UI。它讓既有程式碼直接擁有可互動文件與測試器，並與開發流程緊密結合，是 .NET 生態實現 DX 的關鍵元件。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q1, C-Q4

A-Q10: 什麼是 Swagger UI？能解決什麼問題？
- A簡: 基於 HTML 的互動式 API 文件與測試工具，支援試呼叫、觀察回應與快速學習。
- A詳: Swagger UI 讀取 OpenAPI 定義，自動生成可瀏覽的文件與操作介面。開發者能在瀏覽器中輸入參數、試呼叫端點、檢視回應碼與內容，無需先建立專案或安裝工具。這大幅降低試用與學習門檻，並將文件從靜態轉為能驗證真實行為的互動資源。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q4, B-Q5

A-Q11: 為什麼要提供線上體驗工具給開發者？
- A簡: 降低初用障礙，縮短「看懂—試用—整合」時間，提升採用率與成功率。
- A詳: 線上體驗（如 Swagger UI、JS Test Console）讓開發者無需搭環境即可觸發 API、觀察輸入輸出與錯誤，快速建立心智模型。避免先備條件過多（Web 伺服器、樣板專案等）而流失動能，對推廣與支援社群極有幫助，也是良好 DX 的核心實踐。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, A-Q10, A-Q3

A-Q12: 為何需要 API 測試隔離環境？
- A簡: 避免測試影響正式資料與用量，保障壓測、TDD 與自動化測試可順利進行。
- A詳: 測試常需大量或非典型請求，若直打正式系統，可能造成費用與資料污染。隔離環境（如 Azure Deployment Slots 的 eval/beta）提供專用設定與資料來源，允許壓測、TDD、CI/CD 自動化，並能在上線前於近正式環境條件驗證，降低風險。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q9, C-Q10

A-Q13: API 除錯與日誌在 DX 的角色？
- A簡: 能迅速界定問題、擷取關鍵訊息並追溯根因，是開發者自助與支援溝通的基礎。
- A詳: 良好日誌與例外處理讓開發者區分用戶顯示與開發資訊，於問題發生時可精準定位。搭配 Azure 診斷、Log Stream、應用遙測，能即時或歷史查閱事件。應用 NLog、ELMAH 等套件，結合平台工具，顯著縮短 MTTR，提升支援效率與體驗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8, D-Q5

A-Q14: 為什麼要重視 API 管理與監控？
- A簡: 防濫用、控用量、即時告警與趨勢洞察，保障穩定與商業可控性。
- A詳: API 可能遭不當使用或突增流量。管理與監控可追蹤金鑰、用量、錯誤率與延遲，異常時告警並自動化因應（如限流或中斷）。若用量與計費綁定，更需設定閾值與通知。雲平台與 API 管理服務可簡化此工作，減少自建負擔。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, C-Q7, D-Q9

A-Q15: 什麼是 Azure API Apps？與 Web Apps 有何關係？
- A簡: API Apps 是 Azure App Service 中針對 API 的 Web App 型態，擁有 API 友善的設定與整合。
- A詳: Azure API Apps 基於 App Service Web Apps，提供 HTTPS 預設、API Definition 設定、CORS 管理、診斷與 Log Stream、Deployment Slots 等能力。它讓開發者專注於 API 實作，平台負責部署、監控與擴展，降低維運複雜度並提升上線速度與可靠性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q9, C-Q7

A-Q16: Azure API Apps 對 DX 的直接助益有哪些？
- A簡: 一鍵 HTTPS、API 定義註冊、CORS 設定、診斷與即時日誌、部署插槽切換，上線與維運更敏捷。
- A詳: API Apps 免設證書即可啟用 HTTPS；可在 Portal 設定 API Definition URL 供平台與整合服務發現；CORS 可配置且免重佈署；診斷與 Log Stream 支援即時與歷史排錯；Deployment Slots 支援多環境與快速 Swap，大幅優化可用性、測試便捷與上線可靠性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, C-Q8, C-Q9

A-Q17: Server Code First 與 Definition First 的差異？
- A簡: 前者先寫程式反推定義；後者先寫定義再產碼。取捨在控制力、同步性與團隊流程。
- A詳: Code First 可快速為既有程式生成文件與 UI，適合漸進導入；Definition First 先鎖定契約，再用 Codegen 產生 Server/Client，利於前後端協作與版本控管。兩者皆需處理同步問題；Definition First 更契合契約驅動，但 Codegen 二次產生與合併仍具挑戰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q6, B-Q14

A-Q18: 為何難以在 Build 階段自動檢出契約違規？
- A簡: Swagger 與實作間缺乏強型別編譯期檢測，常需以測試補位，形成流程挑戰。
- A詳: 與以介面強制的 WCF 相比，Swagger 的契約多在執行期或工具鏈校驗，缺少編譯器級別的型別檢查。當實作與定義不同步時，不易於 Build 階段即報錯，需以單元測試、契約測試與 CI 驗證來補強，確保版本演進與相容性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, D-Q6, A-Q17

---

### Q&A 類別 B: 技術原理類

B-Q1: Swagger 定義文件如何描述 HTTP API？
- A簡: 以 JSON/YAML 描述路徑、方法、參數、模型與回應，形成統一可機器讀取的契約。
- A詳: 技術原理說明：OpenAPI 2.0 以 paths 定義端點與 HTTP 動詞，parameters 描述輸入，definitions 描述資料模型，responses 描述回應碼與型別。關鍵流程：編寫或生成定義→校驗→供 UI/Codegen 使用。核心組件：Editor、UI、Validator 與 Codegen。此結構化描述連結文件、測試與產碼。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q6, C-Q5

B-Q2: 在 ASP.NET 啟用 XML Comments 的原理與流程？
- A簡: 以三斜線註解在編譯時輸出 XML，供工具讀取並生成文件或 IntelliSense。
- A詳: 原理：編譯器將 /// 註解收斂為 XML 檔。流程：在專案屬性啟用「XML documentation file」→以 Swashbuckle IncludeXmlComments 導入→Swagger UI 顯示摘要與說明。核心組件：編譯器、XML 檔、Swashbuckle 管線。這讓文件隨程式同步，降低文檔傾斜風險。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, A-Q5, B-Q3

B-Q3: Swashbuckle 如何從程式生成 Swagger 定義？
- A簡: 透過反射與屬性/路由資訊，結合 XML 註解，動態輸出 OpenAPI JSON。
- A詳: 原理：掃描控制器/Action 的路由、HTTP 動詞、參數與回傳型別，並合併 XML 註解。流程：註冊 SwaggerConfig→組態管線→在 /swagger/docs/{ver} 輸出 JSON。核心組件：ApiExplorer、SwaggerGen、Swagger UI。此機制支援 Code First 的自動契約導出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q4, A-Q9

B-Q4: Swashbuckle 的 API Action 衝突如何解？
- A簡: Swagger 不含查詢字串比對，需以策略挑選或合併描述避免同路徑動詞衝突。
- A詳: 原理：Swagger 以路徑＋動詞映射，忽略 query，導致多 Action 同路徑衝突。流程：在 SwaggerConfig 使用 ResolveConflictingActions 指定策略（如 First()）選定描述或自定合併。核心組件：ApiDescriptions、衝突解析委派。確保輸出定義唯一，避免 UI/Codegen 失敗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, D-Q2, A-Q7

B-Q5: 啟用 Swagger UI 的機制與路由？
- A簡: 在 SwaggerConfig 啟用 EnableSwaggerUi，UI 由定義渲染，通常掛載於 /swagger。
- A詳: 原理：中介管線註冊 UI 靜態資源與配置，讀取 /swagger/docs/{ver} 的定義渲染頁面。流程：安裝套件→啟用 UI→瀏覽 /swagger。核心組件：Swagger UI 靜態資源、配置腳本、JSON 端點。完成後可互動測試 API 並查看文件。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q4, B-Q3, A-Q10

B-Q6: Swagger Editor 的產碼流程如何運作？
- A簡: 導入定義後選擇語言與框架，生成 Server/Client 程式碼骨架供擴充。
- A詳: 原理：以範本引擎將定義映射至語言/框架模板。流程：開啟 Editor→貼入定義→Generate Server/Client→下載專案。核心組件：語言模板、型別映射、模型/方法生成器。可快速建立 Server stub 與 Client SDK，促進契約驅動開發。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q6, A-Q8

B-Q7: C# Client SDK 由 Swagger 生成的架構有哪些？
- A簡: 含 API 客戶端類別、模型（DTO）、序列化、組態與錯誤處理基礎。
- A詳: 原理：將 paths 轉為方法、definitions 轉為模型。流程：依模板產生 ApiClient、Configuration、Models 與序列化輔助。核心組件：HTTP 客戶端封裝、請求建構、回應處理、例外轉換。此骨架具備良好層次，適合作為 SDK 起點再客製。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, A-Q7, D-Q7

B-Q8: Azure API Apps 的 HTTPS 機制如何提供？
- A簡: 預設 *.azurewebsites.net 由平台管理憑證，服務自帶 HTTPS，免自行配置。
- A詳: 原理：App Service 為共用網域配置憑證，所有 App 立即受惠。流程：建立 App→使用預設網域→自動啟用 HTTPS。核心組件：平台憑證管理、WAF/Frontends。若自訂網域則需另行綁定憑證。此機制大幅降低安全上線門檻。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, A-Q15, A-Q16

B-Q9: Azure Portal 的 API Definition 設定如何被發現？
- A簡: 在 Portal 設置 OpenAPI URL，供平台與整合服務讀取契約進行發現與集成。
- A詳: 原理：App Metadata 儲存定義 URL，相關服務（如工具或工作流）可查詢使用。流程：在 API Settings 指定 Swagger JSON URL→平台記錄→其他服務 discover 並引用。核心組件：Portal 設定、App Metadata、取用方整合。提升契約可發現性與自動化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, A-Q16, B-Q5

B-Q10: CORS 與瀏覽器同源策略在 API Apps 的實作？
- A簡: 透過 Portal 設定允許來源與方法，讓瀏覽器放行跨站請求，免重佈署更新。
- A詳: 原理：瀏覽器依同源策略限制跨域，CORS 回應標頭決定放行。流程：Portal 設定允許來源→平台回應對應標頭→前端 JS 能跨域呼叫。核心組件：CORS 設定、預檢請求（OPTIONS）、回應標頭。此做法將設定外移，便於快速修正。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q3, C-Q7, A-Q16

B-Q11: Azure 診斷與 Log Stream 的運作流程？
- A簡: 啟用診斷將事件寫入檔案或儲存體，Log Stream 提供即時串流檢視。
- A詳: 原理：平台攔截應用與伺服器日誌，並將其輸出至檔案系統或儲存體。流程：Portal 啟用診斷→選擇儲存位置→使用 Log Stream 監看即時輸出。核心組件：診斷提供者、文件系統、串流端點。對排錯與在地重現困難時尤為重要。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q8, D-Q5, A-Q13

B-Q12: Deployment Slots 的架構與 Swap 原理？
- A簡: 多插槽共用資源但獨立設定與代碼，Swap 以流量切換方式秒級對調上線。
- A詳: 原理：Slots 為同一 App 的多個部署實例，具各自 URL 與設定快照。流程：建立 Test/Beta Slot→部署→驗證→Swap 對調與生產位。核心組件：插槽設定、交換規則、暖機/連線黏著。可實現零停機上線與快速回滾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q9, D-Q9, A-Q12

B-Q13: API 使用量管理與告警的原理（概念）
- A簡: 收集請求統計、設置閾值與動作（告警/限流/中斷），維護穩定與成本控制。
- A詳: 原理：以計量指標（QPS、錯誤率、耗時）監控，用量到閾值時觸發告警或自動化行為。流程：收集度量→設定告警→通知或執行限制。核心組件：遙測、告警規則、策略（限流/突發防護）。雖文中未實作，可借助平台或 API 管理服務落地。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q14, D-Q9, C-Q7

B-Q14: DevOps/CI 與契約檢核的技術挑戰與可行路徑
- A簡: 缺編譯期檢查，改以契約測試與單元測試在 CI 中驗證，輔以 Codegen 與規則校驗。
- A詳: 原理：Swagger 契約不強制編譯期安全，需以測試補強。流程：在 CI 中加入契約校驗（lint/validate）與契約測試（根據定義自動呼叫 API），並對 Codegen 產碼與實作一致性進行比對。核心組件：Validator、測試框架、CI 管線。權衡成本與覆蓋率。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q18, D-Q6, C-Q5

---

### Q&A 類別 C: 實作應用類

C-Q1: 如何在 ASP.NET WebAPI 安裝與設定 Swashbuckle？
- A簡: 透過 NuGet 安裝 Swashbuckle，配置 SwaggerConfig，啟用 UI 與 XML 註解。
- A詳: 步驟：1) NuGet 安裝 Swashbuckle（Install-Package Swashbuckle）；2) 專案生成 SwaggerConfig.cs；3) 啟用 c.EnableSwaggerUi()；4) 設定 IncludeXmlComments 指向產生之 XML；5) 建置後瀏覽 /swagger。注意：確保發佈組態也輸出 XML。最佳實踐：版本化定義、妥善命名標籤與摘要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q5, C-Q2

C-Q2: 如何啟用 XML 文件輸出並連結到 Swagger？
- A簡: 在專案屬性勾選 XML documentation file，並於 SwaggerConfig IncludeXmlComments。
- A詳: 步驟：1) 專案屬性→Build→勾選 XML documentation file（Release 也要勾）；2) SwaggerConfig 中 c.IncludeXmlComments(HostingEnvironment.MapPath("~/bin/YourApi.XML"))；3) 重新建置。注意：發佈後 XML 檔路徑需存在。最佳實踐：為控制器、動作與模型撰寫完整註解。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q1, A-Q5

C-Q3: 如何處理 Swashbuckle 的 API 衝突設定？
- A簡: 在 SwaggerConfig 使用 ResolveConflictingActions，指定挑選策略避免衝突。
- A詳: 步驟：1) 開啟 SwaggerConfig；2) 加入 c.ResolveConflictingActions(apiDescriptions => apiDescriptions.First()); 3) 重新建置。注意：更理想是調整路由/設計，避免同路徑多義動作。最佳實踐：清晰分頁參數、避免過度重載。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q2, A-Q7

C-Q4: 如何啟用並存取 Swagger UI？
- A簡: 在 SwaggerConfig 啟用 EnableSwaggerUi，建置後瀏覽 /swagger 即可操作。
- A詳: 步驟：1) 在 SwaggerConfig 呼叫 .EnableSwaggerUi(c => { … }); 2) 建置並執行網站；3) 於瀏覽器開啟 /swagger；4) 直接輸入參數 Try it out。注意：需能存取 /swagger/docs/{ver} JSON。最佳實踐：設定正確 Host/Schemes、保護非公開環境的 UI 存取。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, A-Q10, C-Q1

C-Q5: 如何使用 Swagger Editor 產生 ASP.NET Server Stub？
- A簡: 將定義貼入 Editor，選 Generate Server→Aspnet5/MVC5，下載專案編譯。
- A詳: 步驟：1) 開啟 editor.swagger.io；2) 貼上 OpenAPI JSON；3) 選單 Generate Server→選 ASP.NET；4) 下載專案；5) 編譯並補齊控制器實作。注意：Codegen 僅骨架，後續需合併既有邏輯。最佳實踐：用於 Definition First 或作為重構起點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, A-Q17, D-Q6

C-Q6: 如何用 Swagger Editor 產生 C# .NET 客戶端 SDK？
- A簡: 在 Editor 選 Generate Client→C#，取得 ApiClient、Models 等類別作為 SDK。
- A詳: 步驟：1) Editor 貼上定義；2) Generate Client→C# .NET 2.0；3) 下載並參考專案；4) 設定 BasePath 與認證；5) 呼叫 API 方法。注意：確認型別映射與序列化設定。最佳實踐：包裝重用、加入重試策略與日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, D-Q7, A-Q8

C-Q7: 如何在 Azure API Apps 設定 API Definition 與 CORS？
- A簡: Portal→API Settings 設定 Swagger URL；同頁設定 CORS 允許來源，免重佈署。
- A詳: 步驟：1) 部署 API 至 App Service；2) Portal→API settings→填入 Swagger Docs URL；3) 啟用 CORS，加入允許來源；4) 儲存後立即生效。注意：公開 UI/定義時留意存取控制。最佳實踐：分環境配置、最小化允許來源清單。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, A-Q16

C-Q8: 如何開啟 Azure 診斷與即時 Log Stream？
- A簡: Portal 啟用診斷記錄至檔案或儲存體，使用 Log Stream 即時查看輸出。
- A詳: 步驟：1) Portal→App→Diagnostics settings；2) 啟用「Application logging」「Web server logging」；3) 選擇檔案系統或儲存體；4) 開啟 Log stream 觀察。注意：控制保留期與成本。最佳實踐：搭配應用層日誌（如 NLog/ELMAH）產出結構化訊息。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q5, A-Q13

C-Q9: 如何建立與使用 Azure Deployment Slots 進行上線？
- A簡: 建立 test/beta 插槽部署驗證，無誤後 Swap 對調生產位置，秒級上線。
- A詳: 步驟：1) Portal→Deployment slots→Add Slot；2) 部署新版本至 Slot；3) 驗證功能與設定；4) Swap 與生產對調；5) 必要時再 Swap 回滾。注意：管理插槽設定與連線字串。最佳實踐：上線前暖機、流量健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q9, A-Q12

C-Q10: 如何規劃開發者測試區（eval slot）與正式隔離？
- A簡: 使用專用插槽搭配獨立設定/資料，限制用量，提供安全試爆場。
- A詳: 步驟：1) 建立 eval Slot；2) 設定不同連線字串與測試資料；3) 啟用 CORS/金鑰控管；4) 監控用量與告警；5) 於文件標注測試端點。注意：避免測試資料污染正式。最佳實踐：限制權限與速率，定期重置測試庫。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q12, B-Q13, D-Q10

---

### Q&A 類別 D: 問題解決類

D-Q1: Swagger UI 例外：找不到 XML 註解檔怎麼辦？
- A簡: 啟用 Release 的 XML 輸出，確認部署含 XML，修正 SwaggerConfig 路徑。
- A詳: 症狀：Swagger UI 報錯或不顯示註解。原因：Release 未輸出 XML、檔案未佈署或路徑錯誤。解法：在 Release 勾選 XML documentation file；確認 bin 中有 XML；SwaggerConfig 使用 HostingEnvironment.MapPath 正確指向。預防：CI 檢查檔案存在、發佈設定包含 XML。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q2, B-Q5

D-Q2: Swashbuckle 報重複路徑/動詞衝突如何處理？
- A簡: 使用 ResolveConflictingActions 指定策略，或重構路由避免同路徑多義。
- A詳: 症狀：產生定義時拋衝突例外。原因：Swagger 不含 query 判斷，導致同 path+verb 多 Action。解法：在 SwaggerConfig 指定 c.ResolveConflictingActions(...First())；或調整路由與參數設計。預防：設計一致性，避免過度重載與隱含路由。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q3, A-Q7

D-Q3: Swagger UI 無法從前端呼叫 API（CORS 問題）？
- A簡: 在 Azure 啟用 CORS 並設定允許來源，確認預檢與標頭符合前端需求。
- A詳: 症狀：瀏覽器跨域錯誤或預檢失敗。原因：未設定 CORS、允許來源不含前端站，或自訂標頭未允許。解法：Portal→API settings→CORS 加入來源；允許必要方法/標頭。預防：文件說明跨域限制，分環境配置，最小權限原則。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, C-Q7, A-Q16

D-Q4: 佈署到 Azure 後遇 401/403 或跨網域受阻？
- A簡: 檢查驗證設定、App 設定變數與 CORS；使用診斷與 Log Stream 追因。
- A詳: 症狀：授權失敗或跨網域封鎖。原因：金鑰/憑證設定錯誤、連線字串缺失、CORS 未設。解法：確認環境變數、應用設定；補齊 CORS 允許；如走 HTTPS 檢視 Host/Scheme 設定。預防：在 Slots 分開設定、設定檢核清單納入 CI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q11, D-Q3

D-Q5: 佈署後 API 啟動失敗，如何診斷？
- A簡: 啟用診斷與 Log Stream，查看應用/伺服器日誌，鎖定缺檔路徑與例外。
- A詳: 症狀：應用 500、啟動中斷。原因：設定/檔案缺失、路徑錯誤、相依不符。解法：啟用應用/伺服器日誌→Log Stream 即時觀察→下載歷史日誌定位；修正組態與檔案。預防：發佈設定包含必要檔（XML、靜態資源）、健康檢查與煙霧測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8, D-Q1

D-Q6: Swagger 定義與實作不同步導致客戶端失敗？
- A簡: 導入契約測試與 CI 驗證，更新定義或實作，使兩者一致。
- A詳: 症狀：Client SDK 反序列化或端點錯誤。原因：實作變更未更新定義或反之。解法：修正 Swagger 定義或程式碼；在 CI 加入定義驗證與契約測試。預防：採用 Definition First 或嚴格流程把關，發佈前自動化校驗。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, C-Q5, C-Q6

D-Q7: 產生的 Client SDK 呼叫失敗或模型不匹配？
- A簡: 檢查 BasePath、序列化設定與模型定義版本，必要時局部客製 SDK。
- A詳: 症狀：404/400 或資料映射錯誤。原因：基底 URL 錯誤、認證缺、模型差異。解法：設定正確 BasePath/認證；比對定義與模型；調整序列化與命名策略；必要時覆寫產生碼。預防：版本鎖定、釋出說明與相容性策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q6, D-Q6

D-Q8: 日誌過多或過少，如何調整？
- A簡: 設計分級與結構化日誌，動態調整等級，保留關鍵情境與追蹤。
- A詳: 症狀：訊息淹沒關鍵或無法定位。原因：缺分級、無結構化、無動態等級。解法：定義 Info/Warn/Error/Debug；採用 NLog/ELMAH；關鍵路徑打點；以設定切換等級。預防：制定日誌政策、定期檢視與清理、加上相關 ID 便於串接分析。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, C-Q8, B-Q11

D-Q9: Swap 上線後異常，如何回滾與定位？
- A簡: 立即 Swap 回前版本，透過日誌與差異比對設定/代碼找出根因。
- A詳: 症狀：Swap 後錯誤率升高或功能異常。原因：設定差異、環境相依、隱藏缺陷。解法：立即 Swap 回滾；比對插槽設定與機密；檢查遙測與日誌；重建測試案例重現。預防：上線前暖機、健康檢測、設定標記為插槽設定並版本化。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q12, C-Q9, A-Q14

D-Q10: 測試流量誤灌正式環境，如何補救與預防？
- A簡: 立即限流或停用金鑰，清理測試資料；建立 eval slot 與用量防護。
- A詳: 症狀：用量暴增、資料污染。原因：測試未隔離、金鑰管理鬆散。解法：暫停/旋轉金鑰；刪除污染資料；通報相關方。預防：建立 eval slot、限制權限與 CORS、用量告警與自動停用、區分測試與正式金鑰。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q10, B-Q13, A-Q12

---

### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 API Developer Experience（DX）？
    - A-Q2: API DX 的四大要點是什麼？
    - A-Q3: 為何 Reliability 與 Usability 在上線特別重要？
    - A-Q4: 為什麼傳統 PDF/Word 不適合當 API 文件？
    - A-Q5: 什麼是「可操作的自動化文件」？
    - A-Q6: 什麼是 Swagger（OpenAPI）？
    - A-Q9: 什麼是 Swashbuckle？在 ASP.NET 的角色？
    - A-Q10: 什麼是 Swagger UI？能解決什麼問題？
    - B-Q1: Swagger 定義文件如何描述 HTTP API？
    - B-Q2: 在 ASP.NET 啟用 XML Comments 的原理與流程？
    - B-Q5: 啟用 Swagger UI 的機制與路由？
    - C-Q1: 如何在 ASP.NET WebAPI 安裝與設定 Swashbuckle？
    - C-Q2: 如何啟用 XML 文件輸出並連結到 Swagger？
    - C-Q4: 如何啟用並存取 Swagger UI？
    - A-Q15: 什麼是 Azure API Apps？與 Web Apps 有何關係？

- 中級者：建議學習哪 20 題
    - A-Q11: 為什麼要提供線上體驗工具給開發者？
    - A-Q12: 為何需要 API 測試隔離環境？
    - A-Q13: API 除錯與日誌在 DX 的角色？
    - A-Q16: Azure API Apps 對 DX 的直接助益有哪些？
    - A-Q17: Server Code First 與 Definition First 的差異？
    - B-Q3: Swashbuckle 如何從程式生成 Swagger 定義？
    - B-Q4: Swashbuckle 的 API Action 衝突如何解？
    - B-Q6: Swagger Editor 的產碼流程如何運作？
    - B-Q7: C# Client SDK 由 Swagger 生成的架構有哪些？
    - B-Q8: Azure API Apps 的 HTTPS 機制如何提供？
    - B-Q9: Azure Portal 的 API Definition 設定如何被發現？
    - B-Q10: CORS 與瀏覽器同源策略在 API Apps 的實作？
    - B-Q11: Azure 診斷與 Log Stream 的運作流程？
    - B-Q12: Deployment Slots 的架構與 Swap 原理？
    - C-Q3: 如何處理 Swashbuckle 的 API 衝突設定？
    - C-Q5: 如何使用 Swagger Editor 產生 ASP.NET Server Stub？
    - C-Q6: 如何用 Swagger Editor 產生 C# .NET 客戶端 SDK？
    - C-Q7: 如何在 Azure API Apps 設定 API Definition 與 CORS？
    - C-Q8: 如何開啟 Azure 診斷與即時 Log Stream？
    - C-Q9: 如何建立與使用 Azure Deployment Slots 進行上線？

- 高級者：建議關注哪 15 題
    - A-Q18: 為何難以在 Build 階段自動檢出契約違規？
    - B-Q13: API 使用量管理與告警的原理（概念）
    - B-Q14: DevOps/CI 與契約檢核的技術挑戰與可行路徑
    - C-Q10: 如何規劃開發者測試區（eval slot）與正式隔離？
    - D-Q1: Swagger UI 例外：找不到 XML 註解檔怎麼辦？
    - D-Q2: Swashbuckle 報重複路徑/動詞衝突如何處理？
    - D-Q3: Swagger UI 無法從前端呼叫 API（CORS 問題）？
    - D-Q4: 佈署到 Azure 後遇 401/403 或跨網域受阻？
    - D-Q5: 佈署後 API 啟動失敗，如何診斷？
    - D-Q6: Swagger 定義與實作不同步導致客戶端失敗？
    - D-Q7: 產生的 Client SDK 呼叫失敗或模型不匹配？
    - D-Q8: 日誌過多或過少，如何調整？
    - D-Q9: Swap 上線後異常，如何回滾與定位？
    - D-Q10: 測試流量誤灌正式環境，如何補救與預防？
    - A-Q14: 為什麼要重視 API 管理與監控？