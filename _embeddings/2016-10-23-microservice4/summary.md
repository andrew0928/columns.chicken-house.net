# API & SDK Design #2, 設計專屬的 SDK

## 摘要提示
- API 與 SDK 定義: API 是溝通介面的「定義」，SDK 是為了方便開發而提供的「套件」與程式庫。
- 硬體介面類比: 以插座與 USB 標準比喻 API 的角色，強調規範的重要性與相容性。
- 雲端時代差異: 現代 API 多為雲端 HTTP/REST；使用者免安裝，開發者可藉 SDK 簡化呼叫與最佳化。
- Azure/Flickr 範例: 官方與社群共同維護多語 SDK，展示跨平台支持與包裝價值。
- 建立自家 SDK: 以 C# 範例將呼叫 API 的重複樣板碼下沉至 SDK，讓 APP 聚焦商業邏輯。
- 分頁與序列化封裝: SDK 內部包裝 HttpClient、JSON 反序列化與 server paging，輸出易用列舉介面。
- 演進與風險: API/SDK 版本更新不同步會造成執行結果錯誤，須在架構面控管。
- 契約導向設計: 將 API 定義 code 化為 Contracts 專案，讓前後端以編譯檢查維持一致。
- SDK 合約與工廠: 以 ISDKClient 介面與工廠模式穩定 APP 與 SDK 關係，降低升級衝擊。
- 架構與治理: 以權限與版本管控、CI/CD 確保持續交付；後續需導入版本管理與向前相容策略。

## 全文重點
本文釐清 API 與 SDK 的本質差異：API 是應用程式之間溝通的介面定義，類似硬體世界中的插座、USB 等標準；SDK 則是為了讓開發者更容易使用這些 API 而提供的套件與工具。在雲端時代，API 多以 HTTP/REST 形式存在，使用者不需安裝，本地端只要會呼叫即可；但開發者常需反覆處理請求組裝、序列化、分頁、快取與最佳化等樣板工作，這些正是 SDK 能發揮價值之處。文章以 Azure 與 Flickr 為例，說明官方與社群如何提供多語系 SDK，並凸顯 SDK 在易用性與效能上的包裝角色。

延續前文的 C# 範例，作者先示範直接用 HttpClient 呼叫 API 的冗長流程：初始化、發送請求、解析 JSON、處理分頁、再以 Linq 過濾，總計逾百行樣板碼。如果服務規模擴大，數以千計的開發者將重複相近實作，造成浪費與一致性問題。解法是抽出共用 Library 成為 SDK，將連線、序列化、分頁等細節封裝為型別安全且可列舉的介面，讓 APP 端只需關注查詢與展示邏輯。經過重構後，APP 僅以一行建立 SDK Client 並直接以 Linq 操作資料，程式大幅精簡。

然而真正的挑戰在於版本演進。API 與 SERVER 由原廠可立即更新，SDK 雖可快速發行，但 APP 的更新節奏不一，會出現舊 APP/SDK 對新 SERVER 的交叉組合，導致難以預期的錯誤。文中以資料欄位從 SerialNo 改為 BirdNo 的案例說明：SERVER 更動但 SDK 未同步，雖不拋例外，卻因反序列化對不上而查無資料。此情境凸顯需透過架構治理來降低風險。

作者提出以「契約」導向解決：將 API 的資料模型與介面定義獨立為 Contracts 專案，供前後端與 SDK 共同參考，以編譯期檢查確保一致，並在版本控管與權限上嚴格管理，視 Contracts 的變更為 API 的正式異動。進一步，為穩定 APP 與 SDK 的關係，定義 ISDKClient 介面同置於 Contracts，SDK 以工廠方法產生具體 Client 實作。如此一來，SDK 內部可自由重構與優化，只要不破壞介面，即可支援「只換 DLL 不改碼」或「重編不改碼」的升級路徑；僅在大版本異動時才要求 APP 調整程式碼。整體架構因此形成：APP 僅依賴 Contracts 與 SDK 介面，SDK 依賴 Contracts 並封裝對 SERVER 的實作，SERVER 依據 Contracts 提供一致的 API。

結尾提醒：文中多以原生 .NET 能力示範（interface、yield、HttpClient、Json 反序列化等），為的是讓讀者理解設計原理，再視情況導入成熟框架如 Swagger/OpenAPI、OData、JWT 等以處理更完整的真實場景。作者強調基礎理解的重要，避免過度依賴框架而在世代更替時失去判斷與落地能力。下一篇將進一步討論 API 版本控制與向前相容策略，完善整體 API/SDK 的演進與治理。

## 段落重點
### 什麼是 "API"?
API 是應用程式間的溝通介面定義，重點在「Interface」。類比硬體世界的插座、USB、HDMI 等標準，由具公信力組織或原廠制定，讓供給與使用雙方依規範對接。落到軟體，API 是紙上規格，SERVER 依規格提供服務，客戶端依規格開發；API 本身不等於實作，而是規範所有對話的語言與格式。

### 什麼是 "SDK"?
SDK 是開發用套件（Kit），通常由 API 提供方或社群為了降低使用 API 的門檻而提供的程式庫、工具、樣板與文件。在雲端時代，終端使用者不必安裝，開發者可直接呼叫 HTTP/REST；但為簡化重複性工作與最佳化體驗，SDK 會在客戶端處理序列化、驗證、快取、分頁等細節，輸出更直觀的介面。

### Microsoft Azure SDK
Azure 提供眾多 PaaS 服務與 API。直接用 HttpClient 呼叫常需十餘行以上；官方 SDK 以 Library 封裝重複模式並加入效能與體驗優化（例如本地計算、驗證、快取），並支援多語平台（.NET、Java、Node.js 等），顯著降低開發成本。

### Flickr SDK
Flickr 提供完整 API 並聚合多語 SDK，許多由社群在 GitHub 維護（如 ActionScript、C、Go、Java、.NET）。此範例顯示：即便非官方實作，只要契合 API 規格與開源協作，也能建立健全的 SDK 生態圈。

### YOUR FIRST SDK!
示範從直接呼叫 API 的冗長流程（初始化、請求、JSON 解析、分頁、Linq 篩選）抽取共用程式成為 SDK。APP 僅建立 SDK Client，透過易用方法與列舉介面取得資料並以 Linq 操作。SDK 內部封裝 HttpClient、反序列化與 server paging（yield return），使 APP 專注業務邏輯，達到精簡與一致。

### SDK / API 的更新及維護問題?
API 與 SERVER 可由原廠即時更新，SDK 也能快速發佈；但 APP 更新節奏難同步，形成「舊 SDK/APP 對新 SERVER」的組合風險。以欄位更名（SerialNo→BirdNo）為例：SERVER 先改、SDK 未更新，反序列化雖不拋錯但結果為空，導致業務錯誤。需在架構上提前布防，避免非預期行為。

### API: APP 與 Service 之間簽訂的合同
以契約（Contract）方式將 API 定義「code 化」，新建 Demo.Contracts 專案，集中放置資料物件與介面定義，供 SERVER、SDK、APP 共用。以編譯器強制一致、以版本控管與權限治理變更（視為 API 修訂）。搬移流程包含先行調整 namespace、搬移類別、重設參考，讓專案以 Contracts 為單一真相來源。

### SDK client interface: APP 與 SDK 之間簽訂的合同
除 API 契約外，還需穩定 APP 與 SDK 的相依關係。於 Contracts 定義 ISDKClient，SDK 以工廠方法建立具體實作，APP 僅依賴介面。如此可支持多種升級模式：只換 DLL 不改碼、重編不改碼；僅於大版本才要求調整程式。SDK 得以內部重構與優化，同時維持對 APP 的穩定外觀。

### 結論
至此形成清晰的開發/部署藍圖：原廠維護 SERVER、API 規範與 SDK；APP 開發者依 Contracts 與 SDK 開發，透過 CI/CD 平順演進。本文以原生 .NET 示範原理，實務上可引入 Swagger/OpenAPI、OData、JWT 等成熟框架以應對更廣泛需求。下一篇將聚焦 API 版本控制與向前相容策略，完善整體治理。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
- HTTP/REST 基礎（路由、方法、狀態碼、序列化/反序列化）
- .NET/C# 基本功（HttpClient、IEnumerable/yield return、介面與類別、命名空間/專案引用）
- 軟體設計原則（抽象與封裝、Factory Pattern、契約導向設計）
- 版本與相容性概念（語意化版本、向前/向後相容）
- 基礎 DevOps/CI-CD 概念與雲端 API 門面（Azure API App Service、API Management）

2. 核心概念：本文的 3-5 個核心概念及其關係
- API vs SDK：API 是介面定義（契約），SDK 是為了方便使用 API 的開發套件（實作+工具）
- 契約式設計（Contracts）：將 API 的資料模型與 SDK 介面「程式碼化」成共享契約，強化前後端一致性
- 封裝與抽象：以 SDK 封裝呼叫細節（HttpClient、分頁、JSON），讓 App 專注業務邏輯
- 相容性與版本管理：API/SDK 更新引發的破壞性變更風險，需透過契約、介面穩定性與版本策略控管
- 架構分層與所有權：SERVER/API/SDK 由原廠維護，APP 由開發者維護，更新節奏不同需設計緩衝

3. 技術依賴：相關技術之間的依賴關係
- App 依賴 SDK（以 ISDKClient 介面規範）→ SDK 依賴 Contracts → API Server 依賴 Contracts
- SDK 內部依賴 HttpClient、JSON 反序列化（Newtonsoft.Json）
- 分頁處理依賴 Server 提供的 $start/$take 參數協定，Client 以 yield return 流式化
- 可選替代方案：OpenAPI/Swagger（契約生成）、OData（查詢/分頁）、JWT（授權）

4. 應用場景：適用於哪些實際場景？
- 對外提供公有 API 的平台（需多語言或跨團隊協作）
- 多 App 客戶端共用同一組服務，想降低重複碼與誤用風險
- 頻繁演進的 API（需要穩定對外介面與良好版本治理）
- 需要雲上門面治理（流量、金鑰、配額、快取、分析）的 API 發布（Azure API Management）

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
- 學習 REST/HTTP 與 JSON 基礎；用 HttpClient 呼叫簡單 Web API
- 了解 API 與 SDK 的差異與角色
- 將一段重複的 API 呼叫流程抽成最小 Library（封裝 BaseAddress、GET、反序列化）

2. 進階者路徑：已有基礎如何深化？
- 擴充 SDK：實作分頁（$start/$take）並以 IEnumerable + yield return 流式封裝
- 導入 Contracts 專案：資料模型（BirdInfo）共用，消除手動對齊風險
- 設計 SDK 介面（ISDKClient）與 Factory Pattern，讓 App 依賴介面而非實作
- 練習破壞性變更案例（欄位改名）並驗證契約/編譯期保護如何攔截問題

3. 實戰路徑：如何應用到實際專案？
- 建立多專案解決方案：ApiWeb、SDK、Contracts、Client App，明確所有權與引用
- 對 API/SDK 制定版本策略與更新流程（發版節奏、相容性測試、降級路徑）
- 以 CI/CD 自動化建置與部署，並用 API Management 暴露/治理 API
- 視需求引入 OpenAPI、OData、JWT 等框架，並保留合約與抽象的設計原則

### 關鍵要點清單
- API 與 SDK 的本質差異: API 是介面定義，SDK 是為了開發者便利的實作與工具集合 (優先級: 高)
- 契約程式碼化（Contracts 專案）: 用共享的資料型別/介面取代口頭或文件定義，讓編譯器保障一致性 (優先級: 高)
- 封裝呼叫細節: 在 SDK 內封裝 HttpClient、URI、JSON、錯誤處理與分頁，讓 App 專注業務 (優先級: 高)
- 分頁與流式存取: 以 $start/$take + IEnumerable/yield return 將分頁封裝成可迭代資料流 (優先級: 中)
- 破壞性變更風險: 欄位改名/結構變動若未同步 SDK，會造成邏輯錯誤，需設計前置檢查與版本控管 (優先級: 高)
- ISDKClient 介面穩定性: App 依賴 SDK 介面而非實作，提高替換與升級的彈性 (優先級: 高)
- Factory Pattern 應用: 以工廠方法建立 SDK Client，集中初始化/檢查/版本協商 (優先級: 中)
- 專案分層與所有權: ApiWeb/SDK/Contracts 由原廠維運，App 由開發者維護，需設計更新緩衝 (優先級: 中)
- 版本與相容性策略: 區分小改（不需重編）、需重編、需改碼的等級，規劃升級路徑 (優先級: 高)
- CI/CD 與治理: 持續建置部署與 Azure API Management 等門面治理強化可靠性 (優先級: 中)
- 例外與回溯機制: SDK 遇到版本不符或契約不一致時能偵測、降級或回報清楚錯誤 (優先級: 中)
- 文件與樣例程式: SDK 應附清晰文件、範例與工具以降低接入門檻 (優先級: 中)
- 可替代框架意識: 知道何時用 OpenAPI/OData/JWT 等框架，何時自行封裝以維持可控性 (優先級: 中)
- 學習基礎優先: 先理解原理再採框架，避免框架更迭時失去設計與診斷能力 (優先級: 中)
- 效能與快取考量: 可將可預期結果於 SDK 層快取或優化請求以減少往返 (優先級: 低)