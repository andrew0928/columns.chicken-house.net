---
layout: synthesis
title: "從 Intent 到 Assertion #1, 聊聊 Vibe Testing 實驗心得"
synthesis_type: faq
source_post: /2025/05/01/vibe-testing-poc/
redirect_from:
  - /2025/05/01/vibe-testing-poc/faq/
postid: 2025-05-01-vibe-testing-poc
---
# 從 Intent 到 Assertion：Vibe Testing 與 AI 驅動 API 自動化測試 FAQ

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Vibe Testing？
- A簡: Vibe Testing 是以「意圖到斷言」為主線，利用 AI 將抽象情境自動展開測試步驟並生成報告的方式。
- A詳: Vibe Testing 將使用者的測試意圖（Intent）透過大模型的 Tool Use/Function Calling 能力，映射為可執行的 API/UI 操作，再以斷言（Assertion）驗證結果。其核心是分離「測什麼」（領域案例）與「怎麼測」（介面規格與執行器），以最小人力成本完成測試設計、執行與報告，達到在多介面（API、Web、App）重用測試意圖的願景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q5, B-Q1

Q2: 什麼是 Intent 與 Assertion？
- A簡: Intent 是測試的意圖與期望行為；Assertion 是驗證結果是否符合期望的斷言。
- A詳: 在測試設計中，Intent描述「要測什麼」與期望的業務行為，例如購物車不得超過10件；Assertion則是形式化的檢查點，確保執行後的系統狀態或回應（HTTP狀態碼、資料內容）符合預期。AI可把Intent展開成操作步驟，再對每步驟生成對應的Assertion以判定通過或失敗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q9

Q3: 為什麼要從 Intent 到 Assertion 自動化？
- A簡: 它能減少人工作業、提升一致性，快速覆蓋業務規則並生成可追溯報告。
- A詳: 傳統自動化仰賴工程師手寫腳本，意圖到執行需大量翻譯工作。AI已具備成熟的工具使用能力，能將情境與規格轉為可執行步驟並自動檢查結果。此流程縮短迭代、提高測試覆蓋率與一致性，並讓人力專注於「測什麼有意義」的高價值工作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, B-Q1

Q4: 什麼是 AC（Acceptance Criteria）？
- A簡: AC是驗收準則，定義某功能在何種條件下算是達標的正式描述。
- A詳: AC將需求具體化為可驗證的條件，例如「同商品加入購物車最多10件」。在Vibe Testing中，AC是生成測試案例的來源，AI據此展開合法與非法情境，並以斷言檢查回應與狀態，形成可追溯的測試報告與結果標記（pass/fail）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, B-Q19

Q5: 什麼是「Domain 層級測試案例」？
- A簡: 它以業務規則為核心，不涉及具體API參數或UI操作細節的測試敘述。
- A詳: Domain層級案例描述業務意圖與預期，例如「空購物車中嘗試加入11件可口可樂，應被拒」。此層次不依賴技術細節，有利跨介面重用。Test Runner在執行前再結合介面規格（API Spec/UI Flow），把抽象案例映射成確切的呼叫與斷言。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q7

Q6: Given/When/Then 在測試中的意義是什麼？
- A簡: Given為前置條件，When為步驟執行，Then為預期驗證，構成測試三部曲。
- A詳: Given：準備環境與資料（例：建立空購物車、選定可口可樂）；When：依情境執行操作（例：加入11件）；Then：對結果做斷言（例：應回400，購物車應保持空）。此結構能清楚分離準備、執行與驗證，便於AI展開步驟與生成可追溯報告。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q9

Q7: 什麼是「AI Ready」的 API？
- A簡: 能被AI精準理解與操作的API，具清晰領域封裝、完整規格與一致認證。
- A詳: AI Ready強調三點：1)領域導向設計，將商業規則封裝在API內，減少呼叫端拼湊；2)精準規格（OpenAPI/Swagger）讓模型可靠生成URI、Headers與Payload；3)標準化認證授權（如OAuth2），可透過統一機制取得Token。這些讓AI測試穩定、可預期。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q15, B-Q17

Q8: CRUD 型 API 與領域導向 API 的差異？
- A簡: CRUD偏資料操作，領域導向封裝業務規則，前者測試易失控，後者更適合AI。
- A詳: CRUD只提供增刪改查，業務規則由呼叫端拼接，AI測試易不確定、路徑發散。領域導向API內建流程與約束，像「加入購物車」已包含合法性檢查。AI透過規格即可穩定操作、斷言，減少測試腳本複雜度與風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, B-Q17

Q9: API 自動化測試與傳統腳本測試有何差異？
- A簡: 傳統需手寫腳本；AI自動從案例展開步驟並生成報告，減少人工作業。
- A詳: 傳統測試依賴人工定義流程、變數串接和斷言。AI驅動的方式將案例與規格交給模型，由模型選用工具執行API並自動構造請求與驗證回應，輸出報告（Markdown/JSON），提升效率與一致性，降低維護成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q25

Q10: 什麼是 Function Calling/Tool Use？
- A簡: 模型在對話中選用外部工具或函式，以完成特定操作並回傳結果的能力。
- A詳: Function Calling讓模型依任務需求呼叫定義好的函式或API，傳入結構化參數並取得真實回應。Tool Use則是廣義的工具選用（API、瀏覽器、電腦操作）。在測試中，模型會選用API插件完成Given/When，並以回應資料進行Then斷言。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q16

Q11: Agent 與 Function Calling 的關係是什麼？
- A簡: Agent是長流程的自治執行者；Function Calling是Agent執行工具的基礎能力。
- A詳: Agent具備目標導向、記憶、工具選用與規劃能力，能跨步驟完成任務；Function Calling則提供在單次或多輪對話中精準呼叫外部功能的介面。測試場景可用輕量的Function Calling完成，也能擴展為Agent以處理更複雜流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q18

Q12: 什麼是 Semantic Kernel？
- A簡: 微軟提供的LLM應用框架，支援插件、Prompt、工具選用與結構化輸出。
- A詳: Semantic Kernel整合多家模型供應商，提供Kernel與Plugins機制、PromptTemplate與FunctionChoiceBehavior等能力。可將OpenAPI轉為可用插件，讓模型自動選用API，並輸出Markdown/JSON報告，適合構建AI驅動的測試執行器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q16

Q13: Plugins 在 Semantic Kernel 中的角色是什麼？
- A簡: Plugins包裝外部工具/API，讓模型可被動選用並執行具體操作。
- A詳: 在Kernel中，Plugins即工具集合。ImportPluginFromOpenApiAsync可把Swagger轉成函式集合，由模型在對話時自動挑選並組織呼叫流程。也可自製環境控制插件（認證、語系、幣別、時區）以降低測試步驟耦合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q10

Q14: OpenAPI/Swagger 在AI測試中的作用是什麼？
- A簡: 它提供精準規格，讓模型可靠生成URI、Headers與Payload並正確呼叫API。
- A詳: OpenAPI定義路徑、方法、參數、Schema與授權等細節。Semantic Kernel可將其轉為插件，模型即能讀懂如何呼叫、傳什麼資料與期待何回應。無精準規格將導致模型猜測、錯誤與不一致，降低測試可用性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q2

Q15: 為什麼需要精準的規格文件？
- A簡: 它避免模型猜測，確保工具選用與參數構造正確，提升測試可靠性。
- A詳: 在AI驅動測試中，模型不是人類工程師，唯有依賴規格才能正確生成請求。人工維護規格在開發期難以同步，易失真。理想做法是CICD自動產生與校驗Swagger，讓測試與程式碼保持一致，避免因文件落差而誤判。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, B-Q2

Q16: 什麼是結構化輸出（Structured Output）？
- A簡: 以JSON模式與Schema約束模型輸出，便於系統整合與統計分析。
- A詳: 結構化輸出讓模型遵守預定JSON結構欄位與型別，產生機器可讀的報告（案例名稱、結果、Context、步驟明細）。與Markdown並行可兼顧人讀與機讀。可透過OpenAI/Kernel設定JsonMode與Schema，減少解析成本與錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, A-Q19

Q17: OAuth2 在測試中的角色為何？
- A簡: 它提供標準化認證機制，Test Runner可取得Token並附加於呼叫流程。
- A詳: 多數API需授權才能操作。Test Runner可設計認證插件，透過OAuth2流程（授權碼/密碼模式等）獲取Access Token，於每次呼叫附加於Authorization Header。此標準化減少測試步驟耦合，聚焦業務驗證而非登入細節。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q13

Q18: 測試環境控制包含哪些面向？
- A簡: 包含使用者身份、語系、幣別、時區、店別等，影響API行為與斷言。
- A詳: 環境控制是測試可重現的關鍵。用插件統一設定Context（user token、locale zh-TW、currency TWD、timezone UTC+8等），避免每個案例重覆處理，降低干擾與互相污染。環境不同可能改變回應與解釋，需明確管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q10

Q19: Markdown 報告與 JSON 報告有何差異？
- A簡: Markdown適合人閱讀；JSON適合系統整合、統計與告警。
- A詳: Markdown提供清楚的步驟表格與說明，便於人工Review；JSON則提供固定欄位（結果、Context、步驟、斷言）。大型測試需聚合分析與儀表板，應以JSON為主，Markdown輔助審查。可同時生成兩種格式滿足不同場景。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8

Q20: AI 驅動的API自動化測試核心價值是什麼？
- A簡: 以最少人力，快速覆蓋業務場景，提升一致性與可追溯性。
- A詳: AI可從案例與規格推論步驟、生成請求、執行工具、判定結果並寫報告。降低手工維護腳本與變數串接的成本，縮短回饋迭代，讓測試人員聚焦於「測什麼才有意義」。此方式能更快暴露規格與行為偏差。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, B-Q25

Q21: Vibe Coding 與 Vibe Testing 有何異同？
- A簡: 兩者皆以自然敘事驅動；前者產生程式碼，後者展開測試與斷言。
- A詳: Vibe Coding讓AI依意圖生成程式碼；Vibe Testing讓AI依意圖生成測試步驟與報告。兩者均重視高品質敘事與規格。Testing更注重斷言與可重現性，需更嚴謹的環境與輸出結構。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q16

Q22: MCP 與 Console Test Runner 有何差異？
- A簡: MCP偏大規模整合與桌面代理；Console適合PoC與快速驗證核心。
- A詳: MCP提供跨應用整合與桌面代理能力，但需處理更多平台細節。Console Test Runner在PoC階段能快速驗證「從意圖到斷言」的核心路徑，避開非關鍵障礙。成熟後可升級到MCP以支援更大範圍的自動化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q18

Q23: UI 自動化與 API 自動化的關聯為何？
- A簡: 皆可用相同Domain案例；差別在介面規格與執行器不同。
- A詳: 若能提供UI操作規格（如Browser Use/Computer Use）與對應Runner，Domain案例可重用於API與UI測試。API較成熟因OpenAPI完善；UI需更精準、低成本的操作技術與標準規格才能穩定擴張。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q18, A-Q5

Q24: 為什麼「測什麼」比「怎麼測」更重要？
- A簡: 測試價值在於挑對案例與斷言；執行細節可交給AI自動展開。
- A詳: GenAI暴露長期問題：工程師往往不善於選擇有意義的測試。AI能自動產生步驟，但「測什麼」需人判斷與審核。Domain案例與AC的品質，決定測試有效性、覆蓋率與風險暴露速度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q5

Q25: TDD 與 AI 驅動測試有何關係？
- A簡: 可先寫案例讓紅燈顯示差距，再逐步讓程式通過AI執行的測試。
- A詳: 與TDD精神一致：先定義預期（紅燈），再落實行為，使測試轉綠。AI Test Runner能快速執行大量案例、給出一致報告，縮短回饋。關鍵是保持規格與案例同步，避免紅燈來自文件落差而非功能缺陷。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q22, B-Q23

---

### Q&A 類別 B: 技術原理類

Q1: Test Runner 整體架構如何運作？
- A簡: 以Semantic Kernel載入API插件，用Prompt驅動工具選用，執行步驟並產出報告。
- A詳: 技術原理說明：Kernel載入OpenAPI為Plugins，模型依Prompt與案例選用工具。流程：1)環境控制（認證、Context）2)Given展開準備步驟3)When執行操作4)Then做斷言5)輸出Markdown與JSON報告。核心組件：Kernel、Plugins、PromptTemplate、FunctionChoiceBehavior、AuthCallback。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q13

Q2: OpenAPI 轉 Plugin 的機制是什麼？
- A簡: 用ImportPluginFromOpenApiAsync讀取Swagger，生成函式集合供模型調用。
- A詳: 技術原理說明：Semantic Kernel解析OpenAPI路徑、方法、參數與Schema，建立KernelFunction。關鍵步驟：指定pluginName、swagger URI、executionParameters（命名空間、HTTP客戶端、AuthCallback）。核心組件：OpenApiFunctionExecutionParameters、KernelFunction集合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q16

Q3: FunctionChoiceBehavior.Auto 的背後機制是什麼？
- A簡: 讓模型自動判斷何時使用插件函式並傳遞正確參數執行。
- A詳: 技術原理說明：Auto模式授權模型依目標挑選與呼叫函式，避免手動回合控制。流程：模型依System/User訊息推論需要工具，生成函式調用指令與參數；Kernel轉為HTTP請求、收回應，回填對話。核心組件：PromptExecutionSettings、FunctionChoiceBehavior、Tool Call事件。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q1

Q4: 三段Prompt設計如何協作？
- A簡: System定鐵律、User注入案例、User定報告格式，協同驅動流程。
- A詳: 技術原理說明：System訊息制定不容違背的SOP（Given/When/Then、禁止假回應）；第二段User載入Domain案例；第三段User指定輸出格式（Markdown/JSON）。流程：模型遵循鐵律展開步驟→執行工具→依格式生成報告。核心組件：PromptTemplate、KernelArguments。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q3

Q5: 如何避免LLM假造API回應？
- A簡: 在System Prompt明確禁用生成或快取，強制真實呼叫取得回應。
- A詳: 技術原理說明：以鐵律聲明「所有API request/response不可生成或以快取替代」，要求真實HTTP。流程：設定、導入插件、執行工具、驗證回應來源。核心組件：System Prompt規範、HTTP Client監測、日誌檢查（印出Request/Response）以佐證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q7, C-Q7

Q6: 插件的 AuthCallback 如何工作？
- A簡: 在每次請求前加入Authorization: Bearer <token>，確保授權通過。
- A詳: 技術原理說明：OpenApiFunctionExecutionParameters提供AuthCallback，在發送HTTP前注入標頭。流程：取得Token（OAuth2）→AuthCallback添加Header→執行API→驗證回應。核心組件：AuthCallback、Token管理、環境插件（使用者上下文）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q6

Q7: 如何從Given展開為API呼叫步驟？
- A簡: 將前置條件對映到可執行API，如建立空購物車、列出商品選取ID。
- A詳: 技術原理說明：模型解析案例語意，匹配規格內可用API。步驟：1)CreateCart代替清空操作2)GetProducts選出「可口可樂」並記錄productId。核心組件：規格解析、語意對映、狀態暫存（Context）供後續When使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q9

Q8: When步驟的執行流程是什麼？
- A簡: 根據案例執行主要操作，呼叫對應API並收集回應做後續斷言。
- A詳: 技術原理說明：以加入購物車為例，呼叫POST /api/carts/{id}/items傳入productId與qty，接著GET /api/carts/{id}檢視結果。流程：構造參數→執行→保存回應。核心組件：工具函式、上下文共享、錯誤攔截與重試策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, C-Q9

Q9: Then斷言的檢查機制如何設計？
- A簡: 根據AC比對回應狀態與內容，如HTTP 400與購物車項目應為空。
- A詳: 技術原理說明：模型將預期結果轉為檢查點，對回應進行驗證。流程：比對狀態碼與資料結構；標記結果為start_fail/exec_fail/test_fail/test_pass。核心組件：斷言規則、回應解析、結果彙整與標準化輸出。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, C-Q7

Q10: Context管理與環境插件如何設計？
- A簡: 以插件統一管理使用者、語系、時區、幣別等，避免測試互相污染。
- A詳: 技術原理說明：為測試配置固定上下文，減少案例耦合。流程：初始化環境→取得token→設定locale/currency/timezone→傳遞至各步驟。核心組件：環境插件、上下文儲存（記憶）、清理機制。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q18, D-Q10

Q11: 結構化輸出如何在Runner中實現？
- A簡: 設定JSON模式與Schema，要求模型輸出固定欄位與型別。
- A詳: 技術原理說明：以Schema約束案例名稱、結果、Context與步驟列表。流程：在Prompt或SDK指定JsonMode→注入Schema→解析輸出→持久化。核心組件：Schema定義、解析器、資料倉儲/儀表板。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q8

Q12: 報告生成的欄位與格式原理是什麼？
- A簡: 報告需呈現Context、各步驟API/請求/回應/結果與Then說明。
- A詳: 技術原理說明：Markdown面向人工審閱，提供表格與敘述；JSON面向系統整合，固定欄位可統計。流程：模型收集每步驟的請求/回應、結果與說明，彙整為兩種格式。核心組件：模板設計、欄位對映、輸出校驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q19, C-Q7

Q13: Token管理與安全考量有哪些？
- A簡: 妥善取得、存放與輪替Token，控制授權範圍並防止外泄。
- A詳: 技術原理說明：OAuth2流程取得Access Token，於AuthCallback附加。需考慮有效期、刷新、最小權限與加密儲存。流程：發放、使用、更新與撤銷。核心組件：認證伺服器、秘密管理、審計日誌。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q4, A-Q17

Q14: 模型選型與效能考量（如 o4-mini）？
- A簡: 選擇能可靠Tool Use且成本/延遲可接受的模型，權衡速度與準確度。
- A詳: 技術原理說明：模型需善於函式選用與規格理解。o4-mini可在約一分鐘完成案例。考量：回應延遲、費用、可靠性、Token限制。核心組件：模型供應商、API限額與重試機制。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q6, B-Q3

Q15: 對話歷史與PromptTemplate的作用？
- A簡: 用模板管理多訊息片段，插入變數（案例），降低程式複雜度。
- A詳: 技術原理說明：PromptTemplate統一管理System/User訊息與占位符（test_case）。流程：設定模板→注入KernelArguments→一次提交。核心組件：Prompt模板、變數注入、歷史管理（如需分回合）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, B-Q4

Q16: ImportPluginFromOpenApiAsync的關鍵參數是什麼？
- A簡: pluginName、swagger URI、executionParameters（命名空間、HTTP、Auth）。
- A詳: 技術原理說明：此API將Swagger轉函式集。步驟：指定名稱與來源URI；設置EnablePayloadNamespacing、HttpClient、AuthCallback。核心組件：OpenApiFunctionExecutionParameters、HTTP日誌觀察。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q2, B-Q2

Q17: 如何挑選API以支持AI Ready？
- A簡: 優先選擇封裝業務規則、規格完整且認證一致的API。
- A詳: 技術原理說明：AI Ready要求：清晰的業務邏輯與錯誤碼、OpenAPI精準定義、標準化OAuth2。流程：審查API設計→補齊規格→標準化認證→小範圍試跑。核心組件：API設計準則、規格工具鏈、CICD集成。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q7, D-Q5

Q18: UI自動化技術（Browser Use/Computer Use）如何擴展到Runner？
- A簡: 以UI操作規格為插件，與Domain案例結合，重用測試意圖。
- A詳: 技術原理說明：Browser Use/Computer Use提供精準的UI操作API。流程：提供UI規格→轉為插件→Runner選用工具執行Given/When→Then以UI狀態斷言。核心組件：UI操作SDK、規格轉換、環境隔離。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q23, B-Q1

Q19: 測試案例展開與規格合併的管道是什麼？
- A簡: 先生成Domain案例，再由模型結合API規格展開為具體步驟。
- A詳: 技術原理說明：分層設計：左半邊「意圖與案例」、右半邊「規格與Runner」。流程：案例審核→注入Prompt→模型選用工具並映射參數→執行→斷言。核心組件：案例庫、規格庫、Runner。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q4

Q20: 如何在報告中標記start_fail/exec_fail/test_fail/test_pass？
- A簡: 以標準結果枚舉對應階段失敗或通過，提升可追蹤與統計性。
- A詳: 技術原理說明：start_fail表示Given不可執行；exec_fail為When步驟失敗；test_fail為Then不符預期；test_pass為整案通過。流程：每步驟收集結果→匯總標記。核心組件：結果枚舉、彙整器、儀表板。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q7, D-Q9

Q21: 執行流程的錯誤處理與重試如何設計？
- A簡: 為網路與限額設計重試，對業務錯誤做斷言，不混淆技術與業務。
- A詳: 技術原理說明：網路/限額故障可重試；業務錯誤需紀錄為斷言失敗。流程：區分技術與業務錯誤→設重試策略→落地日誌→生成報告。核心組件：重試器、錯誤分類器、日誌系統。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q6, D-Q1

Q22: 如何將多案例批次執行與整合？
- A簡: 以案例池批次投遞，生成JSON報告，集中存儲與告警。
- A詳: 技術原理說明：Runner對案例列表迭代執行，統一環境控制。流程：載入案例→逐案執行→收集JSON→匯入資料庫/儀表板。核心組件：案例管理器、報告聚合器、告警引擎。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q10, B-Q11

Q23: 如何在CICD管線中嵌入Test Runner？
- A簡: 以流水線步驟觸發Runner，收集JSON結果，設阈值決定放行。
- A詳: 技術原理說明：在PR或Release階段自動執行測試。流程：拉取規格→跑Runner→解析結果→根據失敗率與關鍵案例判斷通過。核心組件：CI代理、測試步驟、報告解析器與阻斷條件。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, B-Q22

Q24: 安全與授權在AI測試中的風險管理？
- A簡: 控制Token範圍、隔離環境、審計呼叫，避免越權與資料外流。
- A詳: 技術原理說明：測試需最小權限與隔離資料。流程：設定測試帳號與權限→加密Token→記錄與審核呼叫→清理環境。核心組件：IAM、祕密管理、審計/合規工具。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q4, B-Q13

Q25: 與Postman/傳統工具的技術差異是什麼？
- A簡: 傳統工具偏手動編排；AI以規格與案例自動推理步驟與參數。
- A詳: 技術原理說明：Postman擅長調試與集合管理，但需人定義變數串接。AI Runner能根據案例與規格自動生成請求與斷言，跨案例重用意圖。核心組件：模型推理與工具選用vs人工作業。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q1

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何用 .NET 建置最小可用的 Test Runner？
- A簡: 建立Console專案，加入Semantic Kernel，配置模型與HTTP客戶端。
- A詳: 具體步驟：1)新建.NET Console專案 2)安裝Semantic Kernel 3)AddOpenAIChatCompletion設定模型（如o4-mini）與API Key 4)Build Kernel 5)準備Prompt與ExecutionSettings 6)InvokePromptAsync取回報告。注意：記錄HTTP日誌、超時與重試、環境隔離。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q3

Q2: 如何將Swagger匯入成為Kernel Plugin？
- A簡: 使用ImportPluginFromOpenApiAsync，指定pluginName、swagger URI與執行參數。
- A詳: 程式碼片段：await kernel.ImportPluginFromOpenApiAsync("andrew_shop", new Uri(".../swagger.json"), new OpenApiFunctionExecutionParameters { EnablePayloadNamespacing=true, HttpClient=..., AuthCallback=... }); 注意：URI可用v1路徑，啟用命名空間避免鍵衝突，設定HTTP日誌便於驗證。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q16

Q3: 如何撰寫 System Prompt 的鐵律？
- A簡: 清楚定義G/W/T語意，嚴禁假回應與快取，規範失敗標記。
- A詳: 具體步驟：在System訊息中描述：Given前置失敗標記[無法執行]；When失敗標記[執行失敗]；Then不符標記[測試不過]；禁止生成或快取API結果。程式碼：以PromptTemplate嵌入固定文字。注意：語句明確、無歧義；與報告枚舉一致。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5

Q4: 如何載入外部測試案例並代入PromptTemplate？
- A簡: 以KernelArguments注入test_case變數，動態替換模板占位符。
- A詳: 具體步驟：1)從檔案或資料庫讀入案例文字 2)PromptTemplate包含{test_case}占位符 3)InvokePromptAsync時傳入new(settings){["test_case"]=案例內容}。注意：確保案例格式一致，避免換行與符號被轉義。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q15, B-Q19

Q5: 如何設定FunctionChoiceBehavior.Auto以啟用工具選用？
- A簡: 在PromptExecutionSettings配置Auto，使模型自動決定何時調用插件函式。
- A詳: 程式碼片段：var settings=new PromptExecutionSettings{ FunctionChoiceBehavior=FunctionChoiceBehavior.Auto() }; 在InvokePromptAsync传入settings。注意：確保插件匯入成功、規格完整，避免模型因資訊不足不選工具。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q2

Q6: 如何實作OAuth2 AuthCallback並附加Token？
- A簡: 在OpenApiFunctionExecutionParameters中設定AuthCallback加入Authorization標頭。
- A詳: 程式碼片段：AuthCallback=(request,cancel)=>{ var ctx=APIExecutionContextPlugin.GetContext(); request.Headers.Add("Authorization",$"Bearer {userAccessToken}"); return Task.CompletedTask; } 注意：Token取得與更新機制、最小權限、錯誤處理與重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q4

Q7: 如何生成Markdown格式的測試報告？
- A簡: 在User訊息指定報告模板（Context、G/W/T表格、結果枚舉）。
- A詳: 具體步驟：1)在Prompt中要求列出Context 2)Given/When以表格列API/Request/Response/結果/說明 3)Then列預期與實際對比 4)加總測試結果。注意：格式清晰、易讀；避免模型省略關鍵欄位；與JSON並行生成。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, A-Q19

Q8: 如何同時生成JSON結構化報告？
- A簡: 以JsonMode與Schema約束輸出，包含name、result、context與steps。
- A詳: 具體步驟：1)定義JSON Schema欄位 2)在Prompt或SDK指定Structured Output要求 3)解析回傳JSON、驗證Schema 4)存入資料庫或發送告警。注意：欄位命名一致、型別檢查、錯誤容忍（回退重試）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, A-Q16

Q9: 如何執行「加入11件可口可樂」案例？
- A簡: Given建立空購物車與查商品ID；When加11件與查購物車；Then斷言失敗。
- A詳: 具體步驟：1)POST /api/carts/create→取得cartId 2)GET /api/products→找「可口可樂」productId 3)POST /api/carts/{id}/items qty=11 4)GET /api/carts/{id}查看項目 5)Then預期400與購物車空；若回200且含11件則test_fail。注意：記錄請求/回應。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8

Q10: 如何整合測試報告收集與告警？
- A簡: 聚合JSON報告入資料庫，設置失敗閾值與關鍵案例告警。
- A詳: 具體步驟：1)Runner批次執行案例 2)收集JSON報告 3)匯入DB或Elastic/Timeseries 4)儀表板呈現通過率、失敗Top N 5)Webhook/Email告警。注意：標準化欄位、去重、環境維度分析與趨勢追蹤。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q22, B-Q23

---

### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到「預期400但實際回200」怎麼辦？
- A簡: 確認AC與API行為，標記test_fail，回饋需求或修正服務端。
- A詳: 症狀：加入11件商品回200且購物車含項目。原因：服務端未實作上限約束或規格不一致。解決：與產品/後端對齊AC，補實作或修正規格；在報告標記test_fail並附說明。預防：TDD紅燈起步、規格自動化校驗。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q9

Q2: Plugin匯入失敗或Schema解析錯誤怎麼辦？
- A簡: 檢查Swagger有效性、版本與參數；啟用命名空間避免衝突。
- A詳: 症狀：ImportPluginFromOpenApiAsync拋例外。原因：Swagger不合法、版本不符、Schema衝突。解決：用linters驗證OpenAPI、更新版本、EnablePayloadNamespacing。預防：CICD中加入規格校驗與自動產生。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q16

Q3: 模型不選用工具而直接回覆怎麼辦？
- A簡: 強化System鐵律、補充規格、檢查Auto設定與插件可見性。
- A詳: 症狀：模型口述結果未呼叫API。原因：Prompt不嚴、規格不足、Auto未設定。解決：明確禁用假回應、補充Swagger、啟用FunctionChoiceBehavior.Auto。預防：回合日誌審查、對話示例引導工具使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q5

Q4: OAuth2 認證失敗或Token過期怎麼處理？
- A簡: 檢查授權流程與範圍，實作刷新與重試，確保最小權限。
- A詳: 症狀：401/403或Token失效。原因：憑證錯誤、範圍不符、過期未刷新。解決：重走授權流程、實作刷新機制、重試策略。預防：Token生命週期管理、祕密管理與審計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q13

Q5: 測試案例與規格不一致時如何處置？
- A簡: 回看AC與Swagger，對齊改動；標記失敗並建立追蹤工單。
- A詳: 症狀：案例預期與API回應結構不符。原因：規格更新未同步、文件人工維護失真。解決：更新案例或服務端使兩者一致；CICD自動產生規格。預防：需求變更即觸發測試與規格再生。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q23

Q6: Rate limit或Timeout導致測試中斷怎麼辦？
- A簡: 實作重試與退避，分批執行，監控限額並優化模型選型。
- A詳: 症狀：呼叫失敗或延遲過長。原因：限額受限、網路不穩、模型延遲。解決：加退避重試、節流與批次、監控限額、改用更快模型或分片執行。預防：容量規劃與儀表板監控。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q14, B-Q21

Q7: LLM產生假資料或使用快取的風險如何避免？
- A簡: 在System嚴禁生成回應，記錄HTTP往返以核驗真實性。
- A詳: 症狀：回應看似合理但未呼叫API。原因：模型自我完成意圖。解決：鐵律禁止生成/快取；強制顯示Request/Response；比較日誌。預防：工具使用示例、測試用對話模板強制工具路徑。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q7

Q8: 面對CRUD型API難以自動化測試怎麼辦？
- A簡: 以領域封裝重構或加上服務層；測試偏向流程與業務斷言。
- A詳: 症狀：步驟繁瑣、邏輯在呼叫端。原因：純CRUD設計。解決：重構API為領域操作或建立中介服務層；明確錯誤碼與約束。預防：設計階段導入領域導向與AI Ready準則。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q17

Q9: 報告結構不一致導致整合失敗怎麼處理？
- A簡: 強制Schema與校驗；不合格輸出重試或標記為格式錯誤。
- A詳: 症狀：JSON欄位缺失或型別不符。原因：模型漂移或Prompt不穩。解決：加入Schema校驗與修復、必要時重試；在儀表板標示格式異常。預防：固定模板、示例輸出、版本化欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8

Q10: 批次測試互相干擾（環境污染）如何防範？
- A簡: 強制環境隔離、清理策略與Context管理，避免案例相互影響。
- A詳: 症狀：案例間共享狀態導致結果失真。原因：未重置環境或重用資源。解決：每案建立新上下文與資源；完成後清理；用隔離帳號與資料。預防：環境插件統一控管、用例設計遵循隔離原則。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q10, C-Q10

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Vibe Testing？
    - A-Q2: 什麼是 Intent 與 Assertion？
    - A-Q6: Given/When/Then 在測試中的意義是什麼？
    - A-Q4: 什麼是 AC（Acceptance Criteria）？
    - A-Q5: 什麼是「Domain 層級測試案例」？
    - A-Q9: API 自動化測試與傳統腳本測試有何差異？
    - A-Q10: 什麼是 Function Calling/Tool Use？
    - A-Q12: 什麼是 Semantic Kernel？
    - A-Q14: OpenAPI/Swagger 在AI測試中的作用是什麼？
    - A-Q19: Markdown 報告與 JSON 報告有何差異？
    - A-Q20: AI 驅動的API自動化測試核心價值是什麼？
    - C-Q1: 如何用 .NET 建置最小可用的 Test Runner？
    - C-Q2: 如何將Swagger匯入成為Kernel Plugin？
    - C-Q3: 如何撰寫 System Prompt 的鐵律？
    - C-Q7: 如何生成Markdown格式的測試報告？

- 中級者：建議學習哪 20 題
    - A-Q7: 什麼是「AI Ready」的 API？
    - A-Q8: CRUD 型 API 與領域導向 API 的差異？
    - A-Q15: 為什麼需要精準的規格文件？
    - A-Q16: 什麼是結構化輸出（Structured Output）？
    - A-Q17: OAuth2 在測試中的角色為何？
    - A-Q18: 測試環境控制包含哪些面向？
    - B-Q1: Test Runner 整體架構如何運作？
    - B-Q2: OpenAPI 轉 Plugin 的機制是什麼？
    - B-Q3: FunctionChoiceBehavior.Auto 的背後機制是什麼？
    - B-Q4: 三段Prompt設計如何協作？
    - B-Q5: 如何避免LLM假造API回應？
    - B-Q6: 插件的 AuthCallback 如何工作？
    - B-Q7: 如何從Given展開為API呼叫步驟？
    - B-Q9: Then斷言的檢查機制如何設計？
    - B-Q11: 結構化輸出如何在Runner中實現？
    - B-Q12: 報告生成的欄位與格式原理是什麼？
    - C-Q5: 如何設定FunctionChoiceBehavior.Auto以啟用工具選用？
    - C-Q6: 如何實作OAuth2 AuthCallback並附加Token？
    - C-Q8: 如何同時生成JSON結構化報告？
    - D-Q3: 模型不選用工具而直接回覆怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q23: UI 自動化與 API 自動化的關聯為何？
    - A-Q22: MCP 與 Console Test Runner 有何差異？
    - A-Q21: Vibe Coding 與 Vibe Testing 有何異同？
    - B-Q10: Context管理與環境插件如何設計？
    - B-Q14: 模型選型與效能考量（如 o4-mini）？
    - B-Q17: 如何挑選API以支持AI Ready？
    - B-Q18: UI自動化技術（Browser Use/Computer Use）如何擴展到Runner？
    - B-Q21: 執行流程的錯誤處理與重試如何設計？
    - B-Q22: 如何將多案例批次執行與整合？
    - B-Q23: 如何在CICD管線中嵌入Test Runner？
    - B-Q24: 安全與授權在AI測試中的風險管理？
    - C-Q9: 如何執行「加入11件可口可樂」案例？
    - C-Q10: 如何整合測試報告收集與告警？
    - D-Q6: Rate limit或Timeout導致測試中斷怎麼辦？
    - D-Q8: 面對CRUD型API難以自動化測試怎麼辦？