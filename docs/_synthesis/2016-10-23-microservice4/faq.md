---
layout: synthesis
title: "API & SDK Design #2, 設計專屬的 SDK"
synthesis_type: faq
source_post: /2016/10/23/microservice4/
redirect_from:
  - /2016/10/23/microservice4/faq/
---

# API & SDK Design #2, 設計專屬的 SDK

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 API？
- A簡: API 是應用程式溝通的介面定義，描述可被呼叫的方式與資料格式，強調 Interface 而非實作。
- A詳: API（Application Programming Interface）是服務或元件對外暴露的「溝通契約」，說明有哪些操作、要傳什麼參數、回傳什麼資料，以及錯誤處理的行為。它本身偏向「紙上的定義」，像硬體界的 USB、HDMI 標準，讓不同廠商能互通。應用情境包含系統 API、HTTP/REST 服務、微服務之間的協作等。良好的 API 有清楚的文件、穩定的版本策略與可預期的相容性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q4, A-Q7

A-Q2: 為什麼 API 在分散式環境與單機時代意義不同？
- A簡: 單機多為本機函式呼叫；分散式需跨網路、版本與相容性管理，介面穩定性更關鍵。
- A詳: 單機時代多依賴系統 API 或本機元件，呼叫成本低、變更範圍小；分散式/雲端則跨網路、跨團隊與跨部署，API 必須承擔延遲、故障、版本並存、相容性、資安與治理等要求。這使 API 的「契約性」與「治理」變得核心，例如文件化、版本策略、限流、驗證、監控等。API 設計需能支撐 CI/CD 與多用戶端長期演進。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q9, A-Q18

A-Q3: 什麼是 SDK？
- A簡: SDK 是供開發者使用特定 API 的工具組（Kit），常含程式庫、範例、文件與工具。
- A詳: SDK（Software Development Kit）聚焦於「Kit」，是為了更容易、正確、高效地使用 API 的配套組合。它可封裝重複樣板碼、提供型別安全、最佳化與快取，並附帶文件、範本、工具與範例。雲端時代因 API 多為 HTTP/REST，SDK 主要以程式庫封裝呼叫細節，降低學習與開發成本，並可針對語言/平台最佳化（如 .NET、Java、Node.js）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5, A-Q19

A-Q4: API 與 SDK 的差異？
- A簡: API 是介面定義；SDK 是實作工具組。API 告訴你怎麼連；SDK 幫你把細節做到好。
- A詳: API 僅是「能做什麼、怎麼叫」的定義，不含具體客戶端實作；SDK 則是「如何更好地使用 API」的工具組，內含程式庫、最佳實踐與文件。以 HTTP API 為例，API 說明端點與格式；SDK 用程式庫封裝 HttpClient、序列化、分頁、快取、錯誤處理與重試，提供型別安全的介面，降低重工與錯誤。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q3, B-Q2

A-Q5: 為什麼需要 SDK，既然可直接用 HttpClient？
- A簡: SDK 減少重複樣板碼、強化型別安全與效能最佳化，並統一錯誤處理與相容性。
- A詳: 直接用 HttpClient 得自行處理位址組裝、Header、序列化/反序列化、分頁、錯誤處理、重試、快取等，成本高且易出錯。SDK 封裝共通細節，提供強型別方法（如 GetBirdInfos）、yield 流式枚舉、客端快取、統一重試/超時設定，並可內建版本檢查與遞移引導，讓數以千計的開發者共享最佳實踐，穩定能力與一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, A-Q6

A-Q6: SDK 的核心價值是什麼？
- A簡: 開發體驗、正確性、效能與治理一致性，以可重用程式庫內化最佳實踐。
- A詳: 核心價值包含四面向：開發體驗（API 易用、型別安全、減少樣板碼）、正確性（集中化驗證、錯誤處理、重試策略）、效能（客端快取、分頁流式、序列化最佳化）、治理一致性（版本檢查、遞移策略、記錄與遙測）。藉由 SDK，供應方能將最佳實踐落地到每個客戶端，降低整體系統風險與總擁有成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q13, B-Q2

A-Q7: 什麼是「API 是契約（Contract）」？
- A簡: API 契約是前後端共同遵守的型別與行為約定，確保彼此一致與可驗證。
- A詳: 契約將 API 定義具體化為可編譯的介面與資料型別（如 .NET 介面與 POCO），讓前後端共享同一份定義，透過編譯器與測試驗證一致性。像 WCF 的合約思想：變更需受控、版本需標示、相容性需評估。實務上可抽出 Contracts 專案，由架構師/產品負責人核准變更，於版控與 CI 中嚴格管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q10, B-Q4

A-Q8: 如何把 WCF 合約概念套用到 HTTP/REST？
- A簡: 以共享型別/介面實作契約，透過 Contracts 專案與編譯驗證維持一致性。
- A詳: 雖然 REST 無強制介面語言，但可用共享程式碼（介面、DTO）將合約「程式碼化」。將資料模型（BirdInfo）與 SDK 介面（ISDKClient）抽至 Demo.Contracts，供服務與客戶端共同參照。變更時由版控與 CI 驗證破壞性差異，維持穩定。輔以文件與 API 規格（可延伸至 OpenAPI/Swagger）對齊。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q10, A-Q7

A-Q9: API、SERVER、SDK、APP 的責任與更新節奏有何差異？
- A簡: API/SERVER 由原廠即時更新；SDK 原廠發布但由開發者決定升級；APP 由開發者自控。
- A詳: 原廠可即時修改 SERVER 與 API 定義，但 APP 開發者未必能同步升級，形成「新版 SERVER 對舊版 SDK/APP」風險。SDK 雖能快速發布新版，但落地到每個 APP 需時間。故需有契約管理、版本策略、相容性等級與撤換計畫，並在 SDK 中加入版本檢測與降級/提示機制，降低破壞性影響。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, D-Q2, B-Q9

A-Q10: 為什麼要把 Contracts 抽成獨立專案？
- A簡: 使合約成為單一真實來源，集中權限與版本管理，讓編譯與 CI 驗證相容性。
- A詳: 將 DTO 與介面抽至 Demo.Contracts，讓服務端與 SDK/APP 參照同一份定義。任何變更都在版控上可追蹤，且可限制修改權限（架構師/PO）。編譯錯誤能即時揭露破壞性改動；CI 可做合約差異檢查。此舉提高治理能力，避免「手動同步」造成的潛在不一致與線上事故。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q4, D-Q9

A-Q11: 什麼是 SDK Client 介面（ISDKClient）？
- A簡: 定義 SDK 對 APP 提供的操作集合，隔離實作，維持二進位與原始碼相容性。
- A詳: ISDKClient 將公開能力（如 GetBirdInfos/GetBirdInfo）抽象化，APP 僅依賴介面。SDK 內可自由調整實作（HttpClient、快取、重試），不影響呼叫端。好處包括：Mock 友善、便於替換與測試、版本進化時可維持相容性；也可用工廠/DI 管理生命週期與配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q5, D-Q8

A-Q12: 為何在 SDK 中使用工廠模式（Factory Pattern）？
- A簡: 隱藏實作細節與初始化流程，控管建置邏輯，便於配置與演進。
- A詳: 透過 Client.Create(uri) 隱藏建構子，統一初始化（BaseAddress、Header、Timeout、重試策略等），可依環境產生不同實作（如測試、快取版）。升級時可在工廠注入版本檢測、特徵旗標與相容性分流，避免呼叫端變更。亦利於注入記錄、遙測與診斷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q5, D-Q6

A-Q13: 什麼是相容性等級？（二進位、原始碼、破壞性）
- A簡: 分為直接替換 DLL、不改碼重編、需改碼三層級，逐步影響升級難度。
- A詳: 等級1：二進位相容（drop-in replacement），APP 不重編即可運作；等級2：原始碼相容（recompile），需重編但不改碼；等級3：破壞性變更（breaking），需改碼配合。規劃 SDK 發布時應盡量維持前兩者，對破壞性變更以新大版號、遞移指南與過渡期處理，避免線上事故。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, D-Q2, D-Q8

A-Q14: 什麼是 Server-side Paging？
- A簡: 由伺服器分頁回傳資料，客端以 $start/$take 等參數逐批取得，提高效率。
- A詳: 大量資料若一次拉回會占用網路與記憶體。Server-side Paging 讓伺服器根據 start/take 回應分片，客端以迴圈或 IEnumerable/yield 逐批處理。好處是降低延遲尖峰與資源壓力，也使串流化消費、早期過濾與中途停止成為可能。常見於 REST 查詢端點的查詢參數。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q1, D-Q4

A-Q15: yield return 在 SDK 中的角色是什麼？
- A簡: 讓資料逐筆流式輸出，降低記憶體占用，與分頁搭配提升使用體驗。
- A詳: 使用 C# 的 yield return 將集合延遲評估，SDK 內部分頁抓取、外部以 foreach 消費。優點是邊取邊用、可中途停止、降低大集合一次載入的成本。與 LINQ 組合能以查詢表達式過濾結果，讓呼叫端專注業務邏輯，將通訊與分頁複雜度封裝於 SDK。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, B-Q3, C-Q3

A-Q16: 為何 JSON 欄位更名會導致反序列化問題？
- A簡: 反序列化依欄位名稱對應，改名會對不到屬性，資料變空或預設值。
- A詳: JSON 轉物件時以欄位名配對屬性（大小寫敏感依框架），若後端將 SerialNo 改為 BirdNo，而客端仍用舊的 BirdInfo，則該屬性會取不到值，進一步影響查詢邏輯（如以 SerialNo 過濾）。此屬於破壞性 API 變更，應以版本化、相容層或映射處理，並更新 Contracts 與 SDK。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q1, A-Q7, B-Q6

A-Q17: 為什麼在客端做快取/驗證/最佳化？
- A簡: 降低網路往返、改善延遲、降低伺服器負載，提升整體體驗與韌性。
- A詳: 客端可快取不常變的資料、做預檢（參數驗證）、合併請求、背景預取與退避重試，以減少呼叫次數與失敗率。這些共通最佳化適合放進 SDK 統一實作與調參。也可加入記錄與遙測以觀察用戶端行為，支援容量規劃與問題診斷，並在 API 改版時提供相容性處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q8, D-Q7

A-Q18: Azure API App 與 API Management 的角色？
- A簡: API App 提供部署平台；API Management 提供門戶、金鑰、限流、版本與分析。
- A詳: API App Service 讓你以平台即服務部署與運行 API；API Management 則是 API 門面與治理工具，含開發者入口、金鑰與驗證、政策（限流、轉換、快取）、版本化、分析與監控。當 API 對外發佈或跨團隊使用時，這兩者可大幅降低運維與治理成本，強化可觀測性與安全。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q9, D-Q10

A-Q19: 雲端時代 SDK 的意義如何改變？
- A簡: 由安裝套件轉為封裝雲端 API 的程式庫與工具，強調易用、最佳化與治理。
- A詳: 過去 SDK 包含系統再散佈套件與工具；雲端時代 API 已在網上，使用者不必安裝，但開發者仍需便利與正確性。SDK 成為封裝 HTTP/REST 的客端程式庫與工具，提供型別安全、最佳化、版本檢測與治理能力，輔以文件與範例，跨語言/平台提供一致體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q5, B-Q8

A-Q20: 為何「先自己實作，再引入框架」有學習價值？
- A簡: 先理解本質與問題，選框架時更精準，遇缺口也能自行補齊。
- A詳: 直接套框架易忽略原理與限制，框架換代時可移轉的知識少。先土法自建（如契約、分頁、驗簽）能理解為何需要規範與最佳化，再選 Swagger/OData/JWT 等成熟方案。對架構師而言，這有助於評估風險、做取捨與治理，保留在框架之外解決問題的能力。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q7, D-Q10

### Q&A 類別 B: 技術原理類

B-Q1: HttpClient 呼叫 REST API 如何運作？
- A簡: 建立 BaseAddress，發送 GET/POST，讀取回應內容，序列化/反序列化處理。
- A詳: 原理：以 HttpClient 設定 BaseAddress/Headers，依端點與查詢參數送出請求（GetAsync），接收 HttpResponseMessage，讀取字串內容並以 JSON 反序列化為型別。流程：初始化客戶端→組 URI→送出→檢查狀態碼→讀取內容→轉型→回傳。核心組件：HttpClient、HttpResponseMessage、序列化器（如 Newtonsoft.Json）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, A-Q5, B-Q2

B-Q2: SDK 封裝 HttpClient 的架構與組件？
- A簡: 以客戶端類別包裝通訊、序列化、分頁、快取與錯誤處理，提供型別安全方法。
- A詳: 原理：將通訊細節集中在 SDK.Client，暴露語意化方法（GetBirdInfos）。流程：建構或工廠初始化 HttpClient→設定 BaseAddress→封裝請求/回應→反序列化為 DTO→以 IEnumerable/yield 輸出。核心組件：Client 類別、DTO（BirdInfo）、序列化器、分頁與快取模組、錯誤/重試策略。目標是簡化使用並統一行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6, C-Q3

B-Q3: 分頁讀取搭配 IEnumerable/yield 的原理？
- A簡: SDK 內部逐批呼叫頁面，外部以延遲列舉消費，達到流式處理與低記憶體。
- A詳: 原理：將服務端 $start/$take 分頁與 C# 的 yield return 結合。流程：current=0→呼叫一頁→反序列化→逐筆 yield→若回傳數量<頁大小則結束→否則 current+=take 繼續。核心組件：IEnumerable<T>、yield、分頁參數管理。好處：邊取邊用、可中途停止、降低一次性載入成本，並能與 LINQ 管線式處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q15, C-Q3

B-Q4: 合約專案（Demo.Contracts）的技術設計？
- A簡: 將 DTO 與介面抽離至獨立專案，供前後端共享，受版控與權限管理。
- A詳: 原理：以單一真實來源（Contracts）承載 DTO（BirdInfo）與 SDK 介面（ISDKClient）。流程：建立類庫→搬移型別→調整 namespace→更新引用→編譯驗證→限制修改權限。核心組件：DTO、介面、版控策略、CI 驗證。此設計讓任何破壞性變動在編譯期被揭露，並利於語意化版本管理與審核流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, C-Q2, D-Q9

B-Q5: SDK 客戶端介面與工廠的機制是什麼？
- A簡: 介面定義對外能力，工廠統一建構與配置，隔離實作並支援替換與測試。
- A詳: 原理：介面（ISDKClient）只暴露業務方法；工廠（Client.Create）負責實例建立、初始化與策略注入。流程：APP 呼叫工廠→產生具體 Client→設定 HttpClient/策略→回傳介面。核心組件：ISDKClient、Client、工廠方法、DI/設定。優點：相容性維持、Mock 容易、可依環境切換實作（快取/診斷版）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, C-Q5

B-Q6: API 改動導致 APP/SDK 異常的技術原因？
- A簡: 型別與欄位名稱不一致導致反序列化失敗或行為改變，屬破壞性變更。
- A詳: 原理：序列化依欄位名/結構對應，服務端改 BirdInfo.SerialNo→BirdNo 造成客端對不到屬性，值為預設，進而使篩選邏輯無效。流程：服務改動→Contracts/SDK 未更新→執行時錯誤或結果不正確。核心組件：DTO/JSON 映射、版本策略、相容層。解法：契約共用、版本化、向前相容映射、SDK 檢測與提示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, D-Q1, D-Q2

B-Q7: 重構抽離型別與 namespace 的正確流程？
- A簡: 先調整 namespace，再搬移檔案，最後更新參考並以編譯/測試驗證。
- A詳: 原理：降低移動造成的斷鏈與重工。流程：1) 於原專案先改 BirdInfo 的 namespace 為 Demo.Contracts，IDE 自動修正引用；2) 將檔案搬到 Contracts 專案；3) 所有專案引用 Contracts；4) 編譯修錯；5) 執行測試。核心組件：IDE 重構、版控、CI。此序確保改動小步前進、可回溯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, D-Q9, A-Q10

B-Q8: SDK 與多語言/平台的設計差異？
- A簡: SDK 與語言/平台耦合，需分別提供實作（.NET/Java/Node），維持一致行為。
- A詳: 原理：不同語言具差異（型別、序列化、併發），SDK 需各自最佳化但行為一致。流程：定義共同契約與語意→各語言實現→共用規範與測試案例→治理版本與文件。核心組件：跨語言規格、測試矩陣、發佈管線。案例：Azure SDK 與 Flickr 提供多語言客戶端（甚至社群維護）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, A-Q18, D-Q10

B-Q9: 版本控制與 CI/CD 在 API/SDK 發布如何協作？
- A簡: 以語意化版本與契約檢查，CI 驗證破壞性變更，CD 推送 API 與 SDK。
- A詳: 原理：語意化版本標示改動等級；CI 比對 Contracts 差異，跑相容性/合約測試；CD 部署服務與產出 SDK 套件（NuGet）。流程：提 PR→CI 驗證→審核→標記版號→部署→發布 SDK→通知開發者。核心組件：版控、CI/CD、套件庫、公告管道。確保改版可預期、可回滾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, D-Q10, C-Q10

B-Q10: 手工契約 vs Swagger/OData 的技術差異？
- A簡: 手工契約強理解與彈性；Swagger/OData 提供標準化描述與工具鏈。
- A詳: 手工以介面/DTO 維持契約，利於學習與精細控制，但需自建工具。Swagger（OpenAPI）標準化描述端點與模型，生程式碼與文件；OData 提供查詢語法與慣例，減少樣板。選擇取決於團隊能力與需求：先手工理解本質，再引入框架可加速且避免黑箱。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q20, C-Q7, C-Q10

### Q&A 類別 C: 實作應用類

C-Q1: 如何用 HttpClient 直接呼叫 /api/birds 並做分頁？
- A簡: 設 BaseAddress，迴圈以 $start/$take 取頁面，反序列化後處理，直到不足一頁結束。
- A詳: 步驟：1) 建立 HttpClient 並設定 BaseAddress；2) 以 do/while 迴圈呼叫 /api/birds?$start={current}&$take={pagesize}；3) 讀取內容並 JsonConvert.DeserializeObject<T[]>；4) 處理結果；5) 若回傳數量<頁大小則結束。程式碼片段：var res=client.GetAsync($"/api/birds?$start={s}&$take={t}").Result; var arr=JsonConvert.DeserializeObject<BirdInfo[]>(await res.Content.ReadAsStringAsync()); 注意：處理逾時、錯誤碼，避免 .Result 阻塞 UI。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q14, D-Q5

C-Q2: 如何把 BirdInfo 搬到 Demo.Contracts 並共用？
- A簡: 先改 namespace 再搬移檔案，更新各專案參考，編譯驗證修正。
- A詳: 步驟：1) 在原專案將 BirdInfo 的 namespace 改為 Demo.Contracts（IDE 自動修正使用端）；2) 新增 Demo.Contracts 類庫；3) 將檔案搬到 Contracts；4) Demo.ApiWeb、Demo.SDK、Demo.Client 皆參考 Contracts；5) 重建解決錯誤。程式碼片段：namespace Demo.Contracts { public class BirdInfo { ... } } 注意：小步提交、跑測試，限制 Contracts 變更權限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, B-Q4, D-Q9

C-Q3: 如何實作 SDK 的 GetBirdInfos()（分頁+yield）？
- A簡: 內部迴圈按頁取資料，反序列化後以 yield return 逐筆輸出直到結束。
- A詳: 步驟：1) Client 內維持 HttpClient；2) current=0、pagesize=5；3) 呼叫 /api/birds?$start=...；4) var items=JsonConvert.DeserializeObject<BirdInfo[]>；5) foreach yield return；6) 若 items.Length<pagesize 結束。程式碼片段：foreach (var it in items) yield return it; current+=pagesize; 注意：例外處理、逾時、最大頁數保護，避免無限迴圈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, A-Q15, D-Q4

C-Q4: 如何在 APP 使用 SDK + LINQ 進行查詢與篩選？
- A簡: 建立 ISDKClient，GetBirdInfos() 後以 LINQ where/select 進行過濾與投影。
- A詳: 步驟：1) var client=Demo.SDK.Client.Create(uri)；2) var q=from x in client.GetBirdInfos() where x.SerialNo=="40250" select x；3) foreach 顯示。程式碼片段：foreach(var b in client.GetBirdInfos().Where(x=>x.SerialNo=="40250")) { ... } 注意：屬性名稱需與契約一致；大量過濾可改為伺服器端查詢以減少傳輸。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, D-Q1, D-Q7

C-Q5: 如何設計 ISDKClient 與工廠方法？
- A簡: 介面定義方法；Client 實作並提供 static Create(Uri) 隱藏建構與設定。
- A詳: 步驟：1) Contracts 定義 ISDKClient{IEnumerable<BirdInfo> GetBirdInfos();BirdInfo GetBirdInfo(string)}；2) SDK 實作 Client:ISDKClient；3) 提供靜態工廠 Create(Uri)；4) APP 以 ISDKClient 依賴。程式碼片段：ISDKClient c=Client.Create(new Uri("http://...")); 注意：避免直接 new，便於替換、測試與加入策略（快取、重試）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, A-Q11, D-Q8

C-Q6: 如何在 SDK 中加入型別安全的 JSON 反序列化？
- A簡: 以共享 DTO 做泛型反序列化，統一錯誤處理與轉換策略。
- A詳: 步驟：1) 於 Contracts 定義 DTO（BirdInfo）；2) SDK 以 JsonConvert.DeserializeObject<BirdInfo[]>/BirdInfo 轉型；3) 包裝通用方法 Deserialize<T>(string)；4) 捕捉 JsonException 並轉為自訂例外。程式碼片段：T obj=JsonConvert.DeserializeObject<T>(json); 注意：欄位改名需更新 DTO；可加 JsonProperty 映射。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q6, D-Q3

C-Q7: 如何在 Server 端實作 $start/$take 分頁 API？
- A簡: 接收查詢參數，查詢資料來源後以 Skip/Take 取片段並回傳 JSON。
- A詳: 步驟：1) Web API 端點讀取 $start/$take；2) 驗證範圍與上限；3) 從資料集 OrderBy 再 Skip(start).Take(take)；4) 回傳序列化結果。程式碼片段：var data=q.OrderBy(x=>x.Id).Skip(start).Take(take).ToArray(); return Ok(data); 注意：固定排序、限制最大 take、防注入與資源濫用。可配合 API Management 限流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q3, D-Q4

C-Q8: 如何在 SDK 加入簡易快取減少重複呼叫？
- A簡: 以記憶體字典快取特定請求結果，設定過期時間與無效化策略。
- A詳: 步驟：1) 定義 MemoryCache<key,result>；2) 以 URI/參數當 key；3) 呼叫前查快取，命中即回；4) 未命中則呼叫並存入；5) 設定 TTL 與容量限制。程式碼片段：if(cache.TryGetValue(k,out v)) return v; v=await Call(); cache.Set(k,v,TimeSpan.FromMinutes(5)); 注意：適用唯讀/變動不頻繁；需處理同步化與一致性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q17, D-Q7, B-Q2

C-Q9: 重構時如何安全調整 namespace 與參考？
- A簡: 以 IDE 重構工具先改 namespace，再搬檔更新參考，小步編譯驗證。
- A詳: 步驟：1) 以 Rename/Refactor 改 namespace；2) 搬移檔案到 Contracts；3) 更新各專案參考；4) 重建並修正錯誤；5) 執行自動化測試。程式碼片段：namespace Demo.Contracts { ... } 注意：每步提交一次、變更小而可回溯、避免大量手動替換導致遺漏。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, A-Q10, D-Q9

C-Q10: 如何把 SDK 發佈為 NuGet 套件供開發者使用？
- A簡: 設定套件中繼資料，打包 Contracts/SDK，推送至私有/公有 NuGet 源。
- A詳: 步驟：1) 在 SDK 專案設定 PackageId/Version/Description；2) 以 dotnet pack 產生 .nupkg；3) 驗證依賴（Contracts 可內嵌或分包）；4) 推送 dotnet nuget push 至 feed；5) 文件化使用方式。注意：嚴格版本策略（SemVer）、相容性聲明、變更紀錄與遞移指南；CI 自動打包發布。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q9, A-Q13, D-Q10

### Q&A 類別 D: 問題解決類

D-Q1: 欄位 SerialNo 改為 BirdNo 導致查無資料怎麼辦？
- A簡: 症狀為結果空白；原因是 DTO 與 JSON 欄位不匹配；更新契約/SDK 並調整篩選。
- A詳: 症狀：APP 使用舊 SDK 查詢回傳空集合或篩選無效。原因：服務端將欄位更名，反序列化對不到屬性，值為預設。解法：更新 Demo.Contracts 與 SDK 的 BirdInfo，發布新版 SDK，APP 升級並重編；短期可加 JsonProperty 映射或後端提供兼容欄位。預防：契約變更審核、版本化、除錯與相容性測試。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q16, B-Q6, A-Q13

D-Q2: APP 用舊版 SDK 呼叫新版 API 不相容，如何處置？
- A簡: 先回退/加相容層，再引導升級 SDK；提供版本檢測與遞移指南。
- A詳: 症狀：功能異常、空結果或例外。原因：破壞性 API 變更。解法：短期在服務端加相容層或版本端點（/v1,/v2），或回退部署；同步發布新版 SDK 與說明。步驟：1) 服務側緊急相容/回退；2) SDK/Contracts 更新；3) 通知與期限；4) 監控遷移。預防：語意化版本、棄用期、SDK 版本檢測與警示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q13, B-Q9

D-Q3: 呼叫成功但反序列化失敗或回傳空集合的原因？
- A簡: 可能是欄位名不符、資料形狀改變或空回應，需檢查模式與日誌。
- A詳: 症狀：HTTP 200，但資料為預設/空。原因：欄位改名、型別不符、包裹層級變動、空回應、序列化設定差異。解法：比對 JSON 與 DTO、啟用日誌、加嚴格反序列化設定與錯誤拋出、加入契約測試。預防：契約共用、JsonProperty 映射、版本化與文件同步，SDK 加入架構檢測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q6, B-Q6

D-Q4: 分頁讀取出現重複或漏資料怎麼辦？
- A簡: 需固定排序並正確更新游標；檢查終止條件與資料一致性。
- A詳: 症狀：結果有重複或缺漏。原因：未固定排序、資料在讀取中變更、游標/計數錯誤。解法：1) 服務端固定 OrderBy；2) 使用不可變更游標（如 Id>lastId）取代 offset；3) 檢查 items.Length<pageSize 終止；4) 重試策略。預防：定義分頁慣例與最大頁大小，寫整合測試覆蓋邊界頁。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q3, C-Q7

D-Q5: 使用 .Result/.Wait() 造成阻塞或死鎖怎麼辦？
- A簡: 改用 async/await，設定逾時與取消權杖，避免同步等待。
- A詳: 症狀：UI 卡死、ThreadPool 被占滿。原因：同步等待造成上下文死鎖或資源佔用。解法：將 SDK 與 APP 全面 async 化（GetAsync/ReadAsStringAsync await），提供取消與逾時設定；Console 可較安全但仍建議非同步。預防：禁止在 UI 執行緒用 .Result，建立非同步編碼規範與審查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, B-Q1, D-Q7

D-Q6: SDK 連線位址/環境切換失敗如何診斷？
- A簡: 檢查 BaseAddress、路由、DNS/防火牆與憑證；在工廠加入驗證與健康檢查。
- A詳: 症狀：連不上或 404。原因：BaseAddress 錯誤、路由變更、DNS/FW 限制、TLS 憑證問題。解法：記錄實際 URI、比對 Swagger/文件、以 curl/瀏覽器驗證；工廠建立時做 ping/健康檢查。預防：環境配置集中、使用設定檔與特徵旗標，SDK 加入清晰錯誤訊息。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q5, C-Q5

D-Q7: 高延遲或大量資料效能不佳如何優化？
- A簡: 啟用分頁與流式處理、客端快取與過濾下推，設逾時與重試/退避。
- A詳: 症狀：請求慢、記憶體高。原因：一次取回過大、重複請求、伺服器負載。解法：分頁+yield、在查詢端加入條件（伺服器端過濾）、快取常用資料、壓縮、減少欄位、設定逾時與重試退避。預防：在 SDK 內建這些策略、CI 做效能回歸測試、以 API Management 做快取/限流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q8, B-Q2

D-Q8: 升級 SDK 後 APP 需重編或改碼的判斷與策略？
- A簡: 依相容性等級判斷：二進位/原始碼/破壞性，提供對應遷移步驟。
- A詳: 症狀：替換 DLL 後無法啟動或編譯失敗。原因：API 表面變化（方法簽章/命名）或行為改變。策略：宣告語意化版本，維持舊介面至過渡期；提供相容層、Obsolete 標示與遷移指南；破壞性改版需新大版號。預防：契約審核、API Review、消費者測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, A-Q11, B-Q9

D-Q9: 合約專案變更導致多專案編譯錯誤如何排查？
- A簡: 先鎖定變更點，比對差異，逐專案修正引用與命名空間，跑 CI 測試。
- A詳: 症狀：大量型別無法解析。原因：搬移型別、改 namespace 或簽章。解法：以版控差異檢視 Contracts 改動；更新所有引用與 using；IDE 批次修正；重建並跑測試定位剩餘問題。預防：小步重構、事先通告、合約變更審核與自動化相容性檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q2, A-Q10

D-Q10: 如何預防 API 改版造成線上事故？
- A簡: 建立版本策略、棄用期、相容層與治理工具（API Management、CI 檢查）。
- A詳: 症狀：升級後客戶端大量失敗。預防：語意化版本與多版本並存；提供 deprecation 期與告警；在 SDK 加版本檢測與警示；API Management 設政策與轉換；CI 比對契約差異並跑消費者測試；建立回滾機制與藍綠部署；發布遷移指南與監控影響面。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q18, B-Q9, A-Q7

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 API？
    - A-Q3: 什麼是 SDK？
    - A-Q4: API 與 SDK 的差異？
    - A-Q2: 為什麼 API 在分散式環境與單機時代意義不同？
    - A-Q5: 為什麼需要 SDK，既然可直接用 HttpClient？
    - A-Q14: 什麼是 Server-side Paging？
    - A-Q15: yield return 在 SDK 中的角色是什麼？
    - A-Q16: 為何 JSON 欄位更名會導致反序列化問題？
    - B-Q1: HttpClient 呼叫 REST API 如何運作？
    - C-Q1: 如何用 HttpClient 直接呼叫 /api/birds 並做分頁？
    - C-Q4: 如何在 APP 使用 SDK + LINQ 進行查詢與篩選？
    - C-Q2: 如何把 BirdInfo 搬到 Demo.Contracts 並共用？
    - D-Q1: 欄位 SerialNo 改為 BirdNo 導致查無資料怎麼辦？
    - D-Q6: SDK 連線位址/環境切換失敗如何診斷？
    - D-Q5: 使用 .Result/.Wait() 造成阻塞或死鎖怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: SDK 的核心價值是什麼？
    - A-Q7: 什麼是「API 是契約（Contract）」？
    - A-Q10: 為什麼要把 Contracts 抽成獨立專案？
    - A-Q11: 什麼是 SDK Client 介面（ISDKClient）？
    - A-Q12: 為何在 SDK 中使用工廠模式（Factory Pattern）？
    - A-Q13: 什麼是相容性等級？（二進位、原始碼、破壞性）
    - A-Q17: 為什麼在客端做快取/驗證/最佳化？
    - B-Q2: SDK 封裝 HttpClient 的架構與組件？
    - B-Q3: 分頁讀取搭配 IEnumerable/yield 的原理？
    - B-Q4: 合約專案（Demo.Contracts）的技術設計？
    - B-Q5: SDK 客戶端介面與工廠的機制是什麼？
    - B-Q7: 重構抽離型別與 namespace 的正確流程？
    - C-Q3: 如何實作 SDK 的 GetBirdInfos()（分頁+yield）？
    - C-Q5: 如何設計 ISDKClient 與工廠方法？
    - C-Q6: 如何在 SDK 中加入型別安全的 JSON 反序列化？
    - C-Q7: 如何在 Server 端實作 $start/$take 分頁 API？
    - C-Q8: 如何在 SDK 加入簡易快取減少重複呼叫？
    - D-Q2: APP 用舊版 SDK 呼叫新版 API 不相容，如何處置？
    - D-Q3: 呼叫成功但反序列化失敗或回傳空集合的原因？
    - D-Q4: 分頁讀取出現重複或漏資料怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q18: Azure API App 與 API Management 的角色？
    - A-Q20: 為何「先自己實作，再引入框架」有學習價值？
    - B-Q8: SDK 與多語言/平台的設計差異？
    - B-Q9: 版本控制與 CI/CD 在 API/SDK 發布如何協作？
    - B-Q10: 手工契約 vs Swagger/OData 的技術差異？
    - C-Q10: 如何把 SDK 發佈為 NuGet 套件供開發者使用？
    - D-Q7: 高延遲或大量資料效能不佳如何優化？
    - D-Q8: 升級 SDK 後 APP 需重編或改碼的判斷與策略？
    - D-Q9: 合約專案變更導致多專案編譯錯誤如何排查？
    - D-Q10: 如何預防 API 改版造成線上事故？
    - A-Q9: API、SERVER、SDK、APP 的責任與更新節奏有何差異？
    - A-Q8: 如何把 WCF 合約概念套用到 HTTP/REST？
    - A-Q19: 雲端時代 SDK 的意義如何改變？
    - C-Q9: 重構時如何安全調整 namespace 與參考？
    - C-Q7: 如何在 Server 端實作 $start/$take 分頁 API？