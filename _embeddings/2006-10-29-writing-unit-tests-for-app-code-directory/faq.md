# 替 App_Code 目錄下的 code 寫單元測試？

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是單元測試（Unit Testing）？
- A簡: 單元測試是針對最小可測單元（函式/類別）驗證行為的自動化測試。目標是早期發現缺陷、提升設計品質並支援重構。
- A詳: 單元測試指對程式中最小的可測單元進行自動化驗證，常以函式或類別為粒度。透過固定輸入預期輸出，確保邏輯正確。它能縮短回歸時間、提升設計內聚與可測性，並促進重構與持續整合。常見框架包含 JUnit、NUnit、MSTest、NUnitLite 等，依語言與執行環境選用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q4, A-Q16

A-Q2: 什麼是 NUnit？
- A簡: NUnit 是 .NET 平台的單元測試框架，受 JUnit 啟發，支援屬性標註、斷言與 Test Runner 等功能。
- A詳: NUnit 是 .NET 常用的單元測試框架，沿襲 JUnit 概念，透過屬性（如 Test、TestFixture）標註測試，並以 Assert 驗證結果。其 Test Runner 通常在獨立 AppDomain 載入測試組件，提供隔離、報告與插件擴充。適用於標準 Class Library 與多數 .NET 應用，但對特殊 Hosting（如 ASP.NET Web Site App_Code）需額外處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q2, A-Q8

A-Q3: JUnit 與 NUnit 的關係為何？
- A簡: NUnit 受 JUnit 啟發，概念相近；差異在平台與語言（Java vs .NET）及部分特性與工具整合。
- A詳: JUnit 是 Java 的經典單元測試框架，提出以註解/命名約定定義測試與斷言的模式。NUnit 移植該理念至 .NET，提供相似 API 與使用經驗。兩者皆支援斷言、測試夾具、生命週期方法，但整合生態系不同。NUnit 常配合 .NET 特性（AppDomain、屬性、反射），而 JUnit 在 JVM 環境下有 Gradle/Maven 等更緊密整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q8

A-Q4: 什麼是 NUnitLite？核心價值是什麼？
- A簡: NUnitLite 是精簡版測試框架，以原始碼嵌入專案，少依賴、不用獨立 AppDomain，適合資源或環境受限。
- A詳: NUnitLite 為 NUnit 的輕量化實作，僅涵蓋核心子集功能。它以原始碼形式加入使用者專案中，不提供 GUI、插件、多執行緒與獨立 AppDomain 等重量特性，換取在特殊或受限環境中可直接執行，如 ASP.NET Web Site、嵌入式或外掛情境。核心價值在控制執行環境、降低依賴並提升可移植性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q3, C-Q1

A-Q5: ASP.NET 的 App_Code 是什麼？
- A簡: App_Code 是 ASP.NET 2.0 起提供的目錄，放入的原始碼會在 Hosting 環境中自動編譯並載入執行。
- A詳: 在 ASP.NET Web Site 專案中，App_Code 目錄是動態編譯機制的核心之一。放入的 C#/VB 原始碼會由 ASP.NET 編譯系統於執行時自動編譯成組件並載入，開發者不需手動建置 DLL。它大幅簡化 Web Site 的部署，但同時讓外部工具難以直接參考生成的 DLL，對傳統單元測試工作流造成挑戰。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q20, D-Q1

A-Q6: 什麼是 ASP.NET Hosting 環境？為何重要？
- A簡: 它是 ASP.NET 在 IIS/自宿主中提供的執行環境，管理 HttpRuntime/HttpContext 等生命週期，影響程式可測性。
- A詳: ASP.NET Hosting 指在 IIS 或自宿主中由 ASP.NET 管理請求處理的環境，涵蓋 Application Domain 建立、HttpRuntime 啟動、HttpContext/Request/Response 與 Session 管理。許多 Web 程式碼仰賴這些物件運作。因此，若測試在非 Hosting 環境執行（如純 Console Runner 或獨立 AppDomain），涉及 HttpContext 的程式易失效或不可測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q2, A-Q13

A-Q7: 為什麼 App_Code 下的程式難用傳統 Test Runner 測試？
- A簡: 因無固定 DLL 可參考，且傳統 Runner 在獨立 AppDomain，缺少 ASP.NET Hosting 與 HttpContext 支援。
- A詳: App_Code 動態編譯無固定實體 DLL；即便能在暫存目錄找到，也因路徑雜湊與版本變動而不穩。傳統 NUnit/MSTest Runner 為隔離而另建 AppDomain 載入測試組件，無 ASP.NET Hosting 管線與 HttpContext。故依賴 Hosting 的 Web 程式碼在該環境缺乏必要基礎設施而無法正確測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q2, D-Q1

A-Q8: NUnit 與 NUnitLite 有何差異？
- A簡: NUnit 功能完整、隔離強（獨立 AppDomain、GUI、擴充），NUnitLite 輕量、可嵌入、在同域執行，適合特殊環境。
- A詳: NUnit 提供豐富功能：Runner GUI、擴充點、多執行緒與隔離 AppDomain，適合一般類庫與服務的常態測試。NUnitLite 刪減這些重量特性，改以原始碼嵌入，於同一 AppDomain 掃描與執行測試，降低依賴並允許在 Web Site、嵌入式或外掛型環境中運作。兩者 API 類似，遷移成本低，但特性覆蓋不同。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q1, A-Q17

A-Q9: MSTest 與 NUnit/NUnitLite 的差異？
- A簡: MSTest 深度整合 VS/企業工具；NUnit 社群廣泛、跨平台；NUnitLite 輕量可嵌入，適合受限環境。
- A詳: MSTest（Microsoft Unit Test Framework）與 VS、Azure DevOps 整合緊密，提供測試探索、資料驅動等企業功能。NUnit 社群生態豐富、擴充插件多，跨平台友好。NUnitLite 聚焦「源碼嵌入、同域執行、少依賴」以支援特殊 Hosting。選擇依情境：企業整合選 MSTest，一般 .NET 類庫選 NUnit，受限環境選 NUnitLite。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q4, A-Q17

A-Q10: Temporary ASP.NET Files 是什麼？
- A簡: 這是 ASP.NET 動態編譯的暫存輸出目錄，放置由 App_Code 等產生的組件，路徑具雜湊與不穩定性。
- A詳: 執行 ASP.NET Web Site 時，系統會將頁面與 App_Code 原始碼動態編譯並輸出至 c:\Windows\Microsoft.NET\Framework\Temporary ASP.NET Files。目錄含雜湊與版本資訊，可能隨部署或修改而改變。雖可在此找到組件，但不建議作為正式參考來源，因其易變動且非受支援的契約。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, B-Q5, A-Q20

A-Q11: 為什麼 Test Runner 要用獨立 AppDomain？
- A簡: 為隔離測試對主程式的影響、支援重載組件與資源清理，但代價是與 Hosting 環境脫鉤。
- A詳: 獨立 AppDomain 可將測試與 Runner 隔離，避免組件鎖定、靜態狀態污染，並允許重複載入測試組件與回收資源。這有利於穩定與可擴充，但對需要原生 Hosting（如 ASP.NET 的 HttpRuntime）的場景，會造成環境不一致，導致 HttpContext 缺失與測試失敗。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q10, A-Q7

A-Q12: 為何不建議直接引用暫存 DLL 測試 App_Code？
- A簡: 暫存 DLL 路徑不穩、版本雜湊、可能清理重建，缺乏穩定契約，維護困難且易失敗。
- A詳: 暫存 DLL 來自動態編譯，目錄含雜湊與時間變數，IIS 回收或部署變更會重建內容。引用這些 DLL 易造成路徑失效、版本不符與難以複製的問題。更重要的是，這不是官方支援的開發契約，將測試依賴其上會引入脆弱性。建議改以 NUnitLite 嵌入、或改用 Class Library 拆分可測部分。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, C-Q7, A-Q10

A-Q13: 哪些 ASP.NET 程式碼最依賴 HttpContext？為何影響測試？
- A簡: 存取 Request/Response/Session/Application、Server 與使用 HttpContext 靜態取用皆高度依賴，脫離 Hosting 即失效。
- A詳: Web 邏輯若直接讀寫 HttpContext.Current、Request.QueryString、Response.Cookies、Session 與 Application 狀態，或依賴 Server.MapPath、User/Identity 等，皆需 Hosting 提供。脫離管線的 Runner 無法注入這些物件，導致 NullReference 或行為不一致。須以抽象包裝或在 Hosting 內執行測試來化解。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q2, B-Q4

A-Q14: 為何在 Web Site 中嵌入 NUnitLite 而非用外部 Runner？
- A簡: 嵌入可在相同 AppDomain、相同 Hosting 下執行測試，避免環境落差，測到真實依賴。
- A詳: 外部 Runner 多在獨立 AppDomain 或非 Hosting 環境，對依賴 HttpContext 的程式難以覆蓋。將 NUnitLite 原始碼加入 Web Site，由頁面或管線啟動測試，可使測試與應用共享同一 AppDomain、配置與生命週期，確保 HttpRuntime/HttpContext 可用，降低偽陽/偽陰，特別適合 App_Code 的動態編譯模式。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, B-Q3

A-Q15: Web Site 與 Web Application 專案的差異對測試的影響？
- A簡: Web Site 動態編譯無固定 DLL；Web Application 預先編譯成單一組件，較易引用並用傳統 Runner 測試。
- A詳: Web Site 使用 App_Code 動態編譯，部署簡單但難以被外部 Runner 引用。Web Application 專案（WAP）採 MSBuild 預先編譯，輸出可預期的 DLL，方便用 NUnit/MSTest 測試與 CI。若以測試優先，將可測邏輯抽出為類庫或改採 WAP，可顯著改善工具鏈整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q7, A-Q5, A-Q12

A-Q16: 為什麼要將業務邏輯與 HttpContext 解耦？
- A簡: 解耦可提升可測性與重用性，讓邏輯在非 Hosting 環境也能測試，降低對靜態狀態的依賴。
- A詳: 直接讀寫 HttpContext 將邏輯綁死於 Web 管線，使測試需仰賴 Hosting 或複雜模擬。透過抽象介面、參數傳遞與包裝器注入（如 IHttpContext、IRequest），可將核心演算法與協定互動分離，讓多數邏輯在普通 Runner 中測試，僅少數邊界需在 Hosting 測試，提升覆蓋與維護性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, B-Q6, D-Q5

A-Q17: 何時選擇 NUnit 而非 NUnitLite？
- A簡: 當測試目標為類庫/服務、無 Hosting 特殊限制且需要完整功能與生態整合時，選 NUnit 較適合。
- A詳: 若目標程式已有穩定 DLL，無需在特殊環境共域執行，且希望使用完整 Runner、插件、平行化、報表與工具鏈，NUnit 是更佳選擇。NUnitLite 適合資源受限或必須在宿主環境內執行的情境。也可混用：邏輯層用 NUnit，宿主敏感層用 NUnitLite。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q9, C-Q7

A-Q18: 使用 NUnitLite 的限制與取捨是什麼？
- A簡: 功能較少、缺 GUI/擴充與跨域隔離；但可嵌入、同域執行、依賴少，適合受限環境。
- A詳: NUnitLite 移除許多重量級能力，如外掛、GUI、多執行緒與獨立 AppDomain，報告與平行化也較弱。這換得源碼嵌入、少依賴與在特殊宿主（ASP.NET、外掛）中共域運行。選用時需接受功能取捨，並自行設計啟動點與輸出格式，以符合團隊流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q1, D-Q4

A-Q19: 在 ASP.NET 中，單元測試與整合測試如何區分？
- A簡: 單元測試聚焦純邏輯與可替身依賴；整合測試涉及 Hosting、管線與真實資源互動。
- A詳: 單元測試應隔離外部依賴（HttpContext/資料庫），以替身注入僅測算法與邏輯。整合測試則在真實或擬真 Hosting 中驗證組件協作，如路由、模組、Session 與權限。對 Web Site，常以 NUnitLite 完成宿主內的輕量整合測試，同時將業務邏輯抽離做純單元測試，兩者互補。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q6, B-Q4

A-Q20: 為何 App_Code 沒有對應實體 DLL？
- A簡: 因採動態編譯與載入，組件在 Temporary ASP.NET Files 生成且路徑雜湊，不提供穩定外部引用。
- A詳: Web Site 模型優先簡化部署，將原始碼於執行時由 ASP.NET 編譯。產物存於暫存資料夾，命名與目錄含雜湊與版本資訊，供內部載入使用。這不是產品化發布的可預期輸出，因此沒有保證的 DLL 名稱與位置，也不建議外部工具直接依賴。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q12, D-Q7


### Q&A 類別 B: 技術原理類

B-Q1: App_Code 的動態編譯與載入流程如何運作？
- A簡: ASP.NET 偵測 App_Code 變更，以 BuildManager 編譯成暫存組件，載入至應用域供後續請求使用。
- A詳: 原理說明：ASP.NET 啟動時掃描 App_Code 與相關子目錄，建立檔案監視；變更觸發 BuildManager 動態編譯。關鍵流程：檔案監聽→語言提供者編譯→輸出暫存組件→載入至 AppDomain。核心組件：BuildManager、CodeDomProvider、AssemblyCache。此流程保證開發便利，但讓外部引用組件變得不穩定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q10, A-Q20

B-Q2: NUnit Test Runner 的執行架構是什麼？
- A簡: Runner 在獨立 AppDomain 載入測試組件，反射掃描測試，依生命週期執行，產出報告並回收。
- A詳: 原理說明：為隔離與可重載，Runner 建立新 AppDomain 載入測試 DLL。關鍵步驟：解析測試組件→建立 AppDomain→反射掃描 TestFixture/Test→執行 SetUp/Test/TearDown→收集結果→卸載域。核心組件：反射器、執行器、報告器、域管理器。此架構在無 Hosting 的情境穩定，但對依賴 HttpContext 的測試會落空。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q7, B-Q10

B-Q3: NUnitLite 如何在同一 AppDomain 運作？
- A簡: 作為嵌入原始碼，直接在當前 AppDomain 掃描與執行測試，使用簡化執行器與輸出。
- A詳: 原理說明：NUnitLite 不創建新 AppDomain，而在目前進程與域中以反射掃描標註測試。關鍵步驟：初始化 Runner→掃描當前載入組件→執行生命週期→輸出結果（文字/自定）。核心組件：TestDiscoverer、TestRunner、Reporter。這讓它能在 ASP.NET Hosting 共域運作，獲取 HttpContext 與應用設定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q14, C-Q1

B-Q4: ASP.NET Hosting 與 HttpContext 的生命週期機制是什麼？
- A簡: 每次請求建立 HttpContext，經過模組、處理常式管線，請求結束釋放，與應用域/池管理關聯。
- A詳: 原理說明：IIS/HttpRuntime 接收請求建立 HttpContext，封裝 Request/Response/Session。關鍵流程：Authenticate→Authorize→ResolveHandler→ExecuteHandler→EndRequest。核心組件：HttpRuntime、HttpApplication、HttpModule、HttpHandler、HttpContext。測試若在此生命週期外，相關物件為空或行為不同，需在宿主內或以替身模擬。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, A-Q13, C-Q6

B-Q5: 為何引用 Temporary ASP.NET Files 不穩定？
- A簡: 暫存檔案含雜湊與版本，IIS 回收或變更即重建，路徑與名稱常變，非正式契約。
- A詳: 原理說明：編譯輸出為內部快取，與路徑、時間、版本組合產生雜湊。關鍵情況：web.config 變更、程式碼更新、應用池回收會觸發重建。核心組件：AssemblyCache、文件監視器。這導致外部引用常失效、難以重現，且不同機器/使用者目錄可能不同。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q12, D-Q7

B-Q6: 在 .NET 中如何模擬 HttpContext？
- A簡: 以替身包裝器或模擬工具建立假的 HttpContext/Request/Response，或用輕量自宿主建立真正管線。
- A詳: 原理說明：用介面與包裝器替換靜態取用，或以自訂 HttpContext/HttpRequest/HttpResponse 物件模擬必要屬性。關鍵步驟：抽象依賴→注入替身→設定期望資料。核心選項：自製 fake、第三方模擬器、使用 OWIN/自宿主啟動最小化管線。對強依賴場景，宿主內執行更可靠。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q16, C-Q6, D-Q2

B-Q7: 將測試嵌入 Web Site 的測試入口應如何設計？
- A簡: 建立專用頁面/處理常式或後台任務作為 Runner 入口，限制訪問並輸出機器可讀結果。
- A詳: 原理說明：以 HttpHandler/Page 作為啟動點，呼叫 NUnitLite Runner。關鍵步驟：路由到測試端點→執行掃描/測試→輸出 JSON/文字→保護端點（驗證/白名單）。核心組件：NUnitLite Runner、路由、授權與日誌。此設計確保在宿主內執行且便於整合 CI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, C-Q8, D-Q8

B-Q8: 使用 Global.asax 啟動測試的風險與流程？
- A簡: 應用啟動時觸發 Runner 會影響啟動時間與狀態污染，需隔離執行與控制環境。
- A詳: 原理說明：在 Application_Start 呼叫 NUnitLite 可自動驗證。流程：啟動→初始化 Runner→執行測試→輸出結果→標記狀態。風險：延長啟動、污染快取/Session、在生產環境誤執行。需加環境開關、獨立資料來源與可重入設計，並避免在使用者請求關鍵路徑中執行。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q3, D-Q5, D-Q10

B-Q9: 將 App_Code 遷移至 Class Library 的編譯與部署架構？
- A簡: 抽離邏輯為類庫專案，MSBuild 預編譯成 DLL，Web 引用該 DLL，方便傳統 Runner 測試與 CI。
- A詳: 原理說明：分層將可測邏輯移入獨立類庫，Web 僅保留薄控制器/視圖。流程：新建類庫→搬移與調整相依→NuGet 參考→Web 引用→以 NUnit/MSTest 測試→CI 建置部署。核心組件：MSBuild、測試框架、套件管理。此法大幅提升可測性與可維護性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, A-Q15, A-Q16

B-Q10: 測試隔離與 AppDomain 邊界的原理？
- A簡: AppDomain 提供組件隔離與可卸載，但跨域溝通受限；同域共享狀態快，風險是污染與難卸載。
- A詳: 原理說明：AppDomain 隔離組件載入上下文，可卸載整個域釋放資源。跨域需可序列化代理，限制互操作。同域則共享靜態/快取，執行快速但易互相影響。NUnit 取前者求穩定，NUnitLite 取後者求嵌入便利。選擇需依宿主需求權衡。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q11, A-Q8, D-Q5


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何在 Web Site 中加入 NUnitLite 並執行測試？
- A簡: 以原始碼方式加入 NUnitLite，建立啟動入口（頁面或處理常式），在請求中呼叫 Runner 執行並輸出結果。
- A詳: 
  - 步驟：下載 NUnitLite 原始碼→放入 App_Code/子資料夾→建立 TestRunner.aspx 或 .ashx→在 Page_Load 呼叫 new AutoRun().Execute(args)。
  - 代碼：new NUnitLite.AutoRun().Execute(new string[] { });
  - 注意：限制訪問、區分環境、避免生產執行，輸出文字/JSON便於 CI。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q7, A-Q14

C-Q2: 如何建立 TestRunner.aspx 在站內觸發測試？
- A簡: 新增頁面並在後端以 NUnitLite 掃描與執行測試，將結果寫入 Response 供瀏覽或 CI 解析。
- A詳: 
  - 步驟：建立 TestRunner.aspx.cs→Page_Load 執行 Runner→Response.Write 結果。
  - 代碼：int rc = new AutoRun().Execute(new[]{ "--noh" }); Response.Write("RC="+rc);
  - 注意：加入驗證/白名單、加上超時與錯誤處理，避免阻塞。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, C-Q1, D-Q8

C-Q3: 如何在 Global.asax 啟動時跑測試並寫入日誌？
- A簡: 在 Application_Start 呼叫 Runner，將結果輸出到檔案或日誌，並以環境變數開關控制啟用。
- A詳: 
  - 步驟：Global.asax.cs 中 Application_Start→判斷 config→執行 AutoRun→寫入 log。
  - 代碼：if(DebugTests) new AutoRun().Execute(new[]{"--labels=All"});
  - 注意：避免生產啟動、使用非同步或背景工作、不污染 HttpContext/快取。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, D-Q10, A-Q14

C-Q4: 如何在 App_Code 中撰寫第一個 NUnitLite 測試？
- A簡: 建立測試類別標註 TestFixture/Test，寫斷言並由 TestRunner 入口執行，觀察輸出結果。
- A詳: 
  - 步驟：新增 MyTests.cs 至 App_Code→引用 NUnitLite 屬性→實作測試。
  - 代碼：[TestFixture] class CalcTests{ [Test] public void Add(){ Assert.AreEqual(3,new Calc().Add(1,2)); }}
  - 注意：避免與網站命名衝突、分離測試命名空間、保持測試原子性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, A-Q4, A-Q1

C-Q5: 如何為依賴 HttpContext 的方法設計可測包裝？
- A簡: 以介面抽象 Http 依賴，透過建構子/方法注入，測試中傳入替身，運行時傳入真實包裝。
- A詳: 
  - 步驟：定義 IHttpContextAbstraction→建立 HttpContextWrapper→業務類別注入。
  - 代碼：public interface IRequest{string QS(string k);} // 測試以假物件實作
  - 注意：避免直接取用 HttpContext.Current，改以注入取得，降低耦合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q6, D-Q2

C-Q6: 如何在站內使用假的 HttpContext 執行測試？
- A簡: 建立簡化的 HttpContext/Request/Response 物件或使用模擬器，在 Runner 呼叫前設置 HttpContext.Current。
- A詳: 
  - 步驟：自訂 SimpleHttpContext→於 TestRunner 建立並指派 HttpContext.Current→執行測試。
  - 代碼：HttpContext.Current = new HttpContext(new HttpRequest("x","http://t/", ""), new HttpResponse(TextWriter.Null));
  - 注意：僅涵蓋必要屬性；部分 API 仍需真實 Hosting。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q6, A-Q13, D-Q2

C-Q7: 如何將 App_Code 程式碼遷移到 Class Library 以利測試？
- A簡: 將業務邏輯抽出為類庫專案，Web 僅保留薄控制層，使用 NUnit/MSTest 在類庫層測試。
- A詳: 
  - 步驟：建立類庫→搬移無 Http 相依邏輯→調整命名空間與參考→Web 引用 DLL→加建置腳本。
  - 代碼：以專案參考連結；測試專案引用類庫並撰寫 NUnit 測試。
  - 注意：保留少量 Web 邊界，降低跨專案相依。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q15, A-Q16

C-Q8: 如何在 CI 中以 IIS Express 啟動網站並觸發 NUnitLite 測試？
- A簡: 以命令啟動 IIS Express 指向站台，curl 訪問受保護的 TestRunner 端點，解析回傳結果決定成敗。
- A詳: 
  - 步驟：啟動 iisexpress /path:site /port:8080→等待就緒→curl http://localhost:8080/testrunner→解析 RC。
  - 代碼：curl … | find "RC=0"
  - 注意：加上憑證或 API Key、限制來源、啟動超時與重試策略。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, D-Q8, C-Q2

C-Q9: 如何避免嵌入式測試影響真實使用者？
- A簡: 在隔離環境與獨立設定執行測試，限制端點存取，避免共享狀態與資源衝突。
- A詳: 
  - 步驟：建立測試專用 web.config 變體→使用獨立資料庫/快取→限制端點權限→關閉外部整合。
  - 代碼：以環境旗標控制 new AutoRun().Execute()
  - 注意：不要在生產執行；若必要，確保唯讀與節流，記錄審計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, D-Q5, D-Q8

C-Q10: 如何追蹤 Temporary ASP.NET Files 以定位編譯問題？
- A簡: 檢視暫存目錄輸出、開啟 ASP.NET 編譯日誌，利用清除暫存與回收協助重現問題。
- A詳: 
  - 步驟：定位暫存目錄→觀察最新輸出→事件檢視器/Failed Request Tracing→清除暫存→再現。
  - 代碼：iisreset 或刪除 Temporary ASP.NET Files 子目錄後重試
  - 注意：不要把暫存 DLL 作為長期依賴，只作診斷用途。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, A-Q10, D-Q7


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到「找不到 App_Code 對應 DLL」怎麼辦？
- A簡: 避免直接依賴 DLL；改用 NUnitLite 在站內執行，或將邏輯抽出到可編譯的 Class Library。
- A詳: 
  - 症狀：外部 Runner 需 DLL，App_Code 無固定輸出。
  - 原因：動態編譯輸出於暫存，路徑不穩。
  - 解法：嵌入 NUnitLite 站內跑；或重構為類庫供 NUnit/MSTest。
  - 預防：新代碼遵循分層，減少 App_Code 直接承載核心邏輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, A-Q12, C-Q1

D-Q2: 測試中 HttpContext.Current 為 null 怎麼處理？
- A簡: 在宿主內執行測試，或以假 HttpContext/包裝器注入必要資訊，避免直接存取靜態。
- A詳: 
  - 症狀：測試拋 NullReference 或 Hosting 錯誤。
  - 原因：非 Hosting 環境缺少 HttpContext。
  - 解法：用 NUnitLite 共域運行；或注入替身/自建 HttpContext。
  - 預防：用介面抽象 Http 依賴，減少靜態取用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q6, C-Q6

D-Q3: 在 NUnit Runner 測試 ASP.NET 代碼出現 HostingException？
- A簡: Runner 與 Hosting 脫鉤導致，改在 ASP.NET 內執行測試或以自宿主建立最小管線。
- A詳: 
  - 症狀：例外訊息指示需在 Hosting 環境。
  - 原因：獨立 AppDomain 未初始化 HttpRuntime。
  - 解法：改用 NUnitLite 站內入口；或啟動自宿主（IIS Express）後以 HTTP 觸發。
  - 預防：解耦 Web 依賴，將邏輯放類庫測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, C-Q2, C-Q8

D-Q4: NUnitLite 原始碼無法 build 怎麼解？
- A簡: 對應版本相容性問題；切換符合專案的分支/版本，逐步移植必要檔案並修正命名空間。
- A詳: 
  - 症狀：編譯錯誤或缺少相依。
  - 原因：版本不一致、相依差異。
  - 解法：選擇穩定版本；最小化引入檔案；比對相依套件；逐步修正命名空間。
  - 預防：鎖定版本至 repo，建立最小可重現示例與 CI 驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q1, C-Q4

D-Q5: 測試污染 Session/Application 狀態如何避免？
- A簡: 測試前後清理，共用狀態最小化，使用替身或隔離資料存放，避免跨測試干擾。
- A詳: 
  - 症狀：測試互相影響、結果不穩。
  - 原因：同域共用靜態/Session/Application。
  - 解法：加 SetUp/TearDown 清理；使用獨立鍵/容器；禁用快取或以測試命名空間隔離。
  - 預防：設計無狀態服務，將狀態注入並可替換。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q8, C-Q9

D-Q6: 伺服器上執行測試缺少權限（AspNetHostingPermission）？
- A簡: 測試需要足夠信任等級與檔案/網路權限，調整應用池帳戶與配置或改在非生產環境執行。
- A詳: 
  - 症狀：安全例外、權限不足。
  - 原因：部分 API 需更高信任與資源權限。
  - 解法：調整應用池身分、授予檔案/網路權限、於測試環境執行。
  - 預防：最小權限原則、測試環境與生產隔離。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q8, C-Q9, B-Q7

D-Q7: 臨時目錄路徑每次不同導致參考失敗怎麼辦？
- A簡: 不要直接參考暫存輸出；以嵌入式 Runner 或預編譯類庫方式替代依賴。
- A詳: 
  - 症狀：編譯/執行時找不到 DLL。
  - 原因：Temporary ASP.NET Files 路徑雜湊、重建。
  - 解法：NUnitLite 站內跑；或抽出類庫固定輸出。
  - 預防：工具鏈不依賴暫存路徑，使用穩定工件。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, A-Q12, C-Q1

D-Q8: 測試端點被防火牆或驗證攔截怎麼處理？
- A簡: 為端點配置專用驗證與白名單，於 CI 使用憑證/Token 訪問，避免公開暴露。
- A詳: 
  - 症狀：CI 呼叫 401/403 或逾時。
  - 原因：端點受認證/網路策略限制。
  - 解法：配置僅內網/CI IP 白名單；使用 API Key/Basic Auth；在測試環境放行。
  - 預防：將端點置於受控網段，加入審計與節流。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q8, C-Q2

D-Q9: 測試結果不穩定與應用程序池回收的關係？
- A簡: 回收會重建 AppDomain 與暫存編譯，造成狀態丟失與路徑變動，需穩定啟動與重試機制。
- A詳: 
  - 症狀：偶發失敗、找不到類型/組件。
  - 原因：應用池回收導致域重啟與暫存重建。
  - 解法：在測試前暖機；偵測回收後重跑；避免依賴暫存路徑。
  - 預防：設定回收時窗、健康檢查與預載入。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q5, C-Q10

D-Q10: 嵌入式測試啟動過慢如何優化？
- A簡: 減少掃描範圍、分組執行、快取探測結果，並避免在 Application_Start 同步跑全部測試。
- A詳: 
  - 症狀：啟動延遲、超時。
  - 原因：全站掃描與大量 I/O/反射。
  - 解法：以篩選參數限制測試、分批跑、非同步觸發、结果緩存。
  - 預防：常態測試於 CI，站內僅執行快速健康檢查。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q8, C-Q3, C-Q2


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是單元測試（Unit Testing）？
    - A-Q2: 什麼是 NUnit？
    - A-Q3: JUnit 與 NUnit 的關係為何？
    - A-Q4: 什麼是 NUnitLite？核心價值是什麼？
    - A-Q5: ASP.NET 的 App_Code 是什麼？
    - A-Q10: Temporary ASP.NET Files 是什麼？
    - A-Q15: Web Site 與 Web Application 專案的差異對測試的影響？
    - A-Q20: 為何 App_Code 沒有對應實體 DLL？
    - A-Q8: NUnit 與 NUnitLite 有何差異？
    - A-Q9: MSTest 與 NUnit/NUnitLite 的差異？
    - C-Q4: 如何在 App_Code 中撰寫第一個 NUnitLite 測試？
    - C-Q2: 如何建立 TestRunner.aspx 在站內觸發測試？
    - C-Q1: 如何在 Web Site 中加入 NUnitLite 並執行測試？
    - D-Q1: 遇到「找不到 App_Code 對應 DLL」怎麼辦？
    - D-Q7: 臨時目錄路徑每次不同導致參考失敗怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q6: 什麼是 ASP.NET Hosting 環境？為何重要？
    - A-Q7: 為什麼 App_Code 下的程式難用傳統 Test Runner 測試？
    - A-Q11: 為什麼 Test Runner 要用獨立 AppDomain？
    - A-Q12: 為何不建議直接引用暫存 DLL 測試 App_Code？
    - A-Q13: 哪些 ASP.NET 程式碼最依賴 HttpContext？為何影響測試？
    - A-Q16: 為什麼要將業務邏輯與 HttpContext 解耦？
    - A-Q17: 何時選擇 NUnit 而非 NUnitLite？
    - A-Q18: 使用 NUnitLite 的限制與取捨是什麼？
    - A-Q19: 在 ASP.NET 中，單元測試與整合測試如何區分？
    - B-Q1: App_Code 的動態編譯與載入流程如何運作？
    - B-Q2: NUnit Test Runner 的執行架構是什麼？
    - B-Q3: NUnitLite 如何在同一 AppDomain 運作？
    - B-Q5: 為何引用 Temporary ASP.NET Files 不穩定？
    - B-Q7: 將測試嵌入 Web Site 的測試入口應如何設計？
    - C-Q5: 如何為依賴 HttpContext 的方法設計可測包裝？
    - C-Q7: 如何將 App_Code 程式碼遷移到 Class Library 以利測試？
    - C-Q8: 如何在 CI 中以 IIS Express 啟動網站並觸發 NUnitLite 測試？
    - D-Q2: 測試中 HttpContext.Current 為 null 怎麼處理？
    - D-Q3: 在 NUnit Runner 測試 ASP.NET 代碼出現 HostingException？
    - D-Q9: 測試結果不穩定與應用程序池回收的關係？

- 高級者：建議關注哪 15 題
    - B-Q4: ASP.NET Hosting 與 HttpContext 的生命週期機制是什麼？
    - B-Q8: 使用 Global.asax 啟動測試的風險與流程？
    - B-Q10: 測試隔離與 AppDomain 邊界的原理？
    - B-Q6: 在 .NET 中如何模擬 HttpContext？
    - C-Q6: 如何在站內使用假的 HttpContext 執行測試？
    - C-Q3: 如何在 Global.asax 啟動時跑測試並寫入日誌？
    - C-Q9: 如何避免嵌入式測試影響真實使用者？
    - C-Q10: 如何追蹤 Temporary ASP.NET Files 以定位編譯問題？
    - D-Q4: NUnitLite 原始碼無法 build 怎麼解？
    - D-Q5: 測試污染 Session/Application 狀態如何避免？
    - D-Q6: 伺服器上執行測試缺少權限（AspNetHostingPermission）？
    - D-Q8: 測試端點被防火牆或驗證攔截怎麼處理？
    - D-Q10: 嵌入式測試啟動過慢如何優化？
    - A-Q14: 為何在 Web Site 中嵌入 NUnitLite 而非用外部 Runner？
    - A-Q18: 使用 NUnitLite 的限制與取捨是什麼？