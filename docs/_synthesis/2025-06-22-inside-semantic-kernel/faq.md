---
layout: synthesis
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"
synthesis_type: faq
source_post: /2025/06/22/inside-semantic-kernel/
redirect_from:
  - /2025/06/22/inside-semantic-kernel/faq/
postid: 2025-06-22-inside-semantic-kernel
---
# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 Chat Completion API？
- A簡: 回答自然語言問題的核心介面，透過累積對話歷史與模型參數生成回應。
- A詳: Chat Completion API 是 LLM 最主要的推理介面。呼叫時會攜帶完整對話歷史（system/user/assistant 角色）、指定模型（如 gpt-4o-mini）、必要參數（如 temperature），可選附件（tools、response_format）。每次新訊息都重新送出上下文，模型在當下 context 決定下一步回答或工具呼叫。此 API 是 Chat、結構化輸出與 Function Calling 的共用基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, A-Q2, B-Q2

Q2: Chat Completion API 的消息角色有哪些？
- A簡: 常用三角色：system（規範）、user（提問）、assistant（模型回覆）。
- A詳: 對話由多個 message 構成，role 決定語義與優先權。system 用於設定全域規則與身份；user 承載使用者意圖與問題；assistant 為 LLM 生成的可讀回覆。引入工具後，assistant 會含 tool_calls；工具執行回傳以 tool（或 tool-result）角色加入歷史，供模型繼續推理。掌握角色有助於設計正確的對話流程與權限。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, A-Q6, B-Q5

Q3: 什麼是 Structured Output（結構化輸出）？
- A簡: 指定模型輸出 JSON 格式，必要時以 JSON Schema約束欄位與型別。
- A詳: Structured Output 讓 LLM 以機器可解析的 JSON 物件回覆，避免自由文字造成的不確定性。可搭配 JSON Schema 規範欄位、型別、必填與枚舉，並加入執行狀態旗標（如 success、reason）。此作法讓開發者能直接反序列化為程式物件，強化錯誤判定與後續流程銜接，兼顧可靠性與可維護性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, A-Q5

Q4: JSON Schema 在 LLM 中的作用是什麼？
- A簡: 定義輸出結構與型別，提升可解析性、驗證性與失敗可判定。
- A詳: JSON Schema 讓 LLM 回覆可被程式嚴格驗證，避免欄位缺漏或型別錯誤。開發者可在 Schema 加入 result_code 或 success 布林，形成 API 風格的明確狀態。當模型無法確定答案時，以「失敗」狀態回報，讓程式走替代路徑（如查詢外部服務）。此策略能降幻覺、減解析成本，並簡化後續業務邏輯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q4, D-Q3

Q5: 為什麼開發者應該使用 JSON 輸出？
- A簡: 便於反序列化、錯誤處理與與非AI邏輯集成，降低成本。
- A詳: JSON 輸出讓 LLM 回覆直接進入程式語言的型別系統，避免文字解析複雜度。加入 success/status 欄位即可判定可用性，無需猜測。以單一職責設計，讓 LLM僅負責「不可或缺」的語言理解與推理，其他如查詢、計算、格式轉換交由程式碼或外部 API，達到穩定、高效、低成本的整體架構。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q4, D-Q10

Q6: 什麼是 Function Calling（工具使用）？
- A簡: 預宣告可用工具，讓模型在對話中主動選用並傳回呼叫需求。
- A詳: Function Calling 是在對話開始時公布可用的工具（函式規格與參數），模型推理過程中決定何時呼叫哪個工具與傳遞哪些參數。主程式執行工具並將結果回寫到對話歷史，模型再基於新證據繼續推理。此機制將 LLM 變成可控的「編排器」，能驅動外部系統、資料庫與工作流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, A-Q8

Q7: Tool Use 與 Function Calling 有何差異？
- A簡: 本質相同，均指模型在推理中選用外部工具執行任務。
- A詳: Tool Use 是泛稱，Function Calling 多指具體 API 封裝。兩者核心皆為「宣告工具規格→模型決定→主程式執行→回寫結果→模型續推理」。差異在生態與實作，如 MCP、OpenAPI、SDK 插件等不同方式提供工具清單與呼叫協定。本質上皆是讓模型能安全、可控地操作外部系統。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q16, A-Q6, B-Q5

Q8: 為何需要在對話前宣告工具？
- A簡: 讓模型理解能力邊界與可用資源，提升計畫與決策品質。
- A詳: 事前宣告工具相當於提供「可執行的能力地圖」。模型能依任務規劃流程、拆分步驟並為每步選擇最合適資源。明確的描述與參數規格降低誤用與幻覺。也使主程式能安全地審計每次工具呼叫，確保合規與可觀測。此設計是 Agent 化的關鍵前提。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q16, D-Q4

Q9: 什麼是 RAG（檢索增強生成）？
- A簡: 以檢索找到相關內容後，讓模型依據來源生成更準確回覆。
- A詳: RAG 將「檢索」與「生成」結合：先以向量相似度或搜尋引擎取得證據，再把證據與問題組合成提示送入 LLM，生成可引用來源的答案。它能降低模型幻覺、彌補訓練知識時差，支持企業專屬知識庫。RAG 是可靠 AI 應用的基礎設計模式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q8, B-Q11, A-Q10

Q10: RAG 的核心價值是什麼？
- A簡: 提升準確性、可追溯性與時效性，支援私域知識。
- A詳: RAG 的價值在於「有據可依」。答案源自檢索到的內容，能引用連結、文件與段落，便於審核合規。它避免純模型回覆的幻覺，能讓企業私有文件（政策、手冊、程式碼庫）成為有效知識來源。搭配 Function Calling，還能動態檢索外部服務，形成可維護、可觀測的知識工作流。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q8, D-Q5

Q11: 什麼是 Semantic Kernel（SK）？
- A簡: 微軟開源的 AI 應用框架，統一 LLM、工具與插件的編排。
- A詳: SK 提供抽象化的 Kernel、Plugins、Memory 等構件，支援多家 LLM/Embedding 供應商，以及 OpenAPI/Swagger 插件導入。它能管理 Chat History、工具呼叫、提示模板與長期記憶接口，讓開發者以一致方式建構 Agent、RAG 與工作流，減少耦合與重複實作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, A-Q12, C-Q6

Q12: 什麼是 Microsoft Kernel Memory（MSKM）？
- A簡: 專注長期記憶與 RAG 管線的獨立服務與 SDK。
- A詳: MSKM 是微軟團隊打造的 RAG 服務層，提供文件導入（抽取、分段、向量化、儲存）、查詢、擴充管線與連接器。可部署成 Web 服務或嵌入應用，透過 NuGet 與 Docker Image 使用。與 SK 深度整合，內建 SK Memory 插件與相同連接器生態，適合 .NET 開發者落地高規模 RAG。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q11, C-Q7

Q13: SK Memory 與 MSKM 的差異？
- A簡: SK Memory偏抽象向量存取；MSKM提供完整RAG管線。
- A詳: SK Memory 類似 ORM 對應向量儲存與檢索接口，聚焦 CRUD 與相似度查詢。MSKM 則負責端到端的導入管線，包括內容抽取、分段策略、向量化、標籤與儲存，並提供服務化運行模式。兩者互補：SK 編排應用流程，MSKM管理長期資料與檢索品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, B-Q10

Q14: 什麼是向量資料庫？
- A簡: 支援高維向量相似度檢索的資料系統，用於語意比對。
- A詳: 向量資料庫儲存文本的嵌入向量，提供相似度查詢（如 cosine）。查詢時將問題轉為向量，找出最相近的內容段落。它可伴隨原文、來源、標籤等中繼資料，支持過濾與排序。是 RAG的核心基礎設施，關係到檢索準確度與延遲。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q26, B-Q11, A-Q15

Q15: 什麼是 Chunking（分段）？
- A簡: 依模型與語義將長文切片，便於嵌入與檢索。
- A詳: Chunking 以固定長度、語義界線或重疊策略將長文切成段。嵌入模型常有最佳輸入長度（如 512 tokens），過長會失真，過短會失上下文。良好分段能提升相似度比對準確率，搭配摘要、段落標題等增強資訊密度，可顯著改善 RAG 效果。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q5, A-Q16

Q16: 什麼是 Embedding（向量化）？
- A簡: 將文字轉為數值向量，供語意相似度計算。
- A詳: Embedding 以專用模型將文本映射到高維空間，語意相近者距離更近。RAG 需對文件段與查詢同時向量化，才能進行相似度檢索。模型選擇影響語域適配性（如技術文、中文），需考量輸入長度上限與效能/成本。向量化結果與中繼資料一同存入向量庫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q12, B-Q26

Q17: 什麼是 MCP（Model Context Protocol）？
- A簡: 統一 LLM 與工具的通訊協定，支援工具清單與呼叫。
- A詳: MCP 定義 tools/list、tools/call、resources/list、prompts/list 等 RPC 介面，通訊支持 stdio 與基於 SSE 的 HTTP。它讓不同語言與平台以一致方式暴露工具供 LLM 操作，被譽為「AI 的 USB-C」。可用 C# 實作 MCP server，讓 Claude Desktop 等客戶端即插即用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, C-Q10, A-Q7

Q18: MCP 的 stdio 與 SSE 有何差異？
- A簡: stdio走標準輸入輸出；SSE以單向事件串流傳訊。
- A詳: stdio 適合 CLI/桌面整合，延遲低且易除錯；SSE（Server-Sent Events）依 HTTP 單向事件推送，便於雲端部署與瀏覽器環境。兩者皆可承載 JSON-RPC，實作方依場景選擇。了解通訊差異有助規劃部署架構與偵錯手段。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q16, C-Q10, D-Q2

Q19: 為什麼讓 LLM 只做「非它不可」的事？
- A簡: 降成本提穩定，計算與搜尋交給程式與外部API。
- A詳: LLM 擅長語義理解與推理，不擅長確定性計算、批量格式轉換、資料過濾。將可程式化任務交回代碼，避免每次都耗費大量 tokens。此單一職責原則讓系統更可控、可測、可擴展，並能大幅節省成本、降低延遲。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q5, D-Q10, B-Q18

Q20: 什麼是 temperature（溫度）？
- A簡: 控制模型回覆的隨機性，高溫更創意，低溫更穩定。
- A詳: temperature 調節取樣分布，高值讓模型探索更廣、創意更豐富，但一致性下降；低值貼近訓練分布，結果更可預測。在結構化輸出與工具呼叫場景，通常偏低以確保格式與決策穩定；在創意生成則可提高促進發散。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q1, D-Q10

Q21: Chat History 與 Memory 有何差異？
- A簡: Chat History 是短期對話上下文；Memory 是長期知識儲存。
- A詳: Chat History 每次請求都攜帶累積訊息，影響模型當下推理，是短期記憶。Memory 指向量庫與長期資料（如文件、FAQ），供檢索時引用。SK 管理 Chat History；MSKM 管理 Memory 與 RAG 管線。兩者協同讓模型既「記得你剛說過什麼」，又「引用可靠知識」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q12, B-Q9, B-Q11

Q22: AI 應用的短期記憶與長期記憶是什麼？
- A簡: 短期為當次對話歷史；長期為可持久檢索的知識。
- A詳: 短期記憶是 Chat History 的訊息序列，影響下一步推理與工具決策。長期記憶是導入到向量庫與資料系統的文檔、摘要、FAQ等，可跨會話共享。RAG 就是「先查長期記憶，再生成」。分工清楚才能控成本與提升可重用性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q21, B-Q8, B-Q11

Q23: 為何要產生「檢索專用資訊」？
- A簡: 將作者視角映射到使用者提問視角，提升語意對齊。
- A詳: 長文直切常造成語意不對齊。先用 LLM 生成摘要、段落摘要、FAQ、問題/原因/解法等視角化內容，再向量化與標籤，就能讓查詢命中更準。此先製程序不隨查詢次數增長，成本可控，能顯著改善企業級 RAG 品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q9, D-Q5

Q24: 使用 SDK 與直接呼叫 HTTP API 有何差異？
- A簡: SDK提升便利與一致性；HTTP更原始靈活但需自管細節。
- A詳: 直接 HTTP 透明可控，適合研究協定與細節；SDK 抽象化規格與錯誤處理、內建型別與工具整合（如 SK 的 C# 型別即生成 JSON Schema）。在複雜場景（多工具、多模型、多插件）SDK能大幅減工程負擔，但需承擔相依。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q24, C-Q2, C-Q6

Q25: Search GPT 類功能的本質是什麼？
- A簡: 以工具觸發搜尋，取回來源後讓模型整合回答並引用。
- A詳: 本質是「Function Calling + RAG」。提示要求引用來源，宣告搜尋工具（與參數），模型推斷何時呼叫、如何組合查詢條件，取得結果後再生成答案。可替換搜尋目標為私域知識庫（如 MSKM），便能由「通用搜尋」變為「企業檢索」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, B-Q22, C-Q6

Q26: 什麼是「土炮 Function Calling」？
- A簡: 以訊息約定前綴模擬工具對話，主程式攔截執行。
- A詳: 在不支援 Function Calling 的模型上，以 system 提示約定兩種前綴（如「請執行指令」給工具、「安德魯大人您好」給用戶），模型生成符合前綴的訊息，主程式攔截工具前綴執行並回寫結果。雖不正式但能驗證流程與概念。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q23, C-Q4, D-Q4

---

### Q&A 類別 B: 技術原理類

Q1: Chat Completion API 如何運作？
- A簡: 每次送出完整對話歷史，模型依上下文生成回覆或工具呼叫。
- A詳: 技術原理說明：請求含 headers（APIKey）、model與參數、messages、可選tools與response_format。關鍵步驟：1) 累積歷史（含 system/user/assistant/tool/tool-result）2) 送出請求，模型在當前上下文決策 3) 若有 tool_calls，主程式執行工具並回寫結果，重複直至完成。核心組件：模型、消息角色、工具規格、回應解析。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q2, B-Q5

Q2: Chat Completion API 的執行流程與主要欄位？
- A簡: headers、model參數、messages、tools、response_format與回應usage。
- A詳: 技術原理說明：HTTP POST 至 /v1/chat/completions，Authorization Bearer 帶金鑰。流程：1) 構造 payload 2) 設定 model（如 gpt-4o-mini）與 temperature 3) messages含角色 4) optional tools與response_format（如 json_schema）。回應含 choices、usage token、finish_reason。核心組件：請求/回應結構、token計量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q2, B-Q19

Q3: 結構化輸出（JSON 模式）如何保障解析？
- A簡: 以指定格式或 Schema，讓模型遵循可機器驗證的結構。
- A詳: 技術原理說明：response_format 指定 json_object 或 json_schema。流程：1) 在提示要求 JSON 2) 提供 Schema（欄位型別、必填、枚舉）3) 反序列化並驗證。核心組件：Schema、驗證器、錯誤處理。可加入 success/status 欄位，建立 API 式語義，處理不可回答情況。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, D-Q3

Q4: 如何用 JSON Schema 強化錯誤判定？
- A簡: 在 Schema 定義狀態欄位與嚴格型別，拒絕不合格輸出。
- A詳: 技術原理說明：Schema加入 success、code、message，並限定必要欄位型別與 pattern，讓驗證階段即判定成功/失敗。流程：1) 模型輸出 JSON 2) 驗證 Schema 3) 失敗走替代路徑（重試、改查）。核心組件：Schema、驗證器、重試策略。此法降低幻覺與解析錯誤成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, D-Q3, C-Q3

Q5: Function Calling 的技術機制？
- A簡: 先宣告工具規格，模型回傳 tool_calls，主程式執行並回寫。
- A詳: 技術原理說明：tools含名稱、描述、參數。assistant 回應含 tool_calls（name與arguments）。流程：1) 宣告 tools 2) 模型判定需要呼叫 3) 主程式執行工具 4) 將工具結果以 tool（或 tool-result）加入 messages 5) 再次呼叫模型續推理。核心組件：工具規格、呼叫協定、結果回寫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q7, C-Q4

Q6: 連續動作的 Function Calling 如何運作？
- A簡: 工具間具順序相依，模型迭代規劃、呼叫與整合成最終回覆。
- A詳: 技術原理說明：多步驟場景（如查空檔→新增事件），每步須先獲得前一步結果。流程：1) 模型產生第一個 tool_calls 2) 主程式執行並回寫 3) 模型基於新上下文決策下一步工具 4) 直到目標達成才以 assistant 對用戶回覆。核心組件：上下文管理、工具鏈、迭代控制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, C-Q5, D-Q9

Q7: tool 與 tool-result 的角色與流程？
- A簡: tool為呼叫意圖；tool-result為執行回傳，皆納入歷史供續推理。
- A詳: 技術原理說明：assistant/tool_calls 表意圖與參數，主程式執行後以 tool（含結果 payload）回寫。流程：每次新結果更新上下文，模型再基於完整歷史做決策。核心組件：訊息角色設計、結果封裝、序列化與可觀測性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q5, C-Q5

Q8: RAG 的標準管線原理？
- A簡: 先轉換查詢為檢索條件，再檢索證據、組裝提示給模型生成。
- A詳: 技術原理說明：1) Query Reformulation（收斂問題）2) Retrieval（向量相似度或搜尋引擎）3) Prompt Assembly（將證據與任務指令組合）4) Generation（引用來源生成答案）。核心組件：向量庫、嵌入模型、標籤過濾、提示模板。品質取決於導入與檢索策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q11, C-Q8

Q9: MSKM 的架構與運作模式？
- A簡: 以服務+SDK運行，提供導入管線、查詢與SK整合的 RAG 平台。
- A詳: 技術原理說明：MSKM 提供內容抽取→分段→向量化→儲存的管線與查詢接口。可部署為 Web 服務（Docker）、或嵌入程式。核心步驟：導入、標籤、索引、查詢。核心組件：Connectors（LLM/Embedding）、Handlers（管線處理）、SK Memory Plugin（供工具化）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q11, C-Q7

Q10: SK 與 MSKM 如何協同工作？
- A簡: SK 編排對話與工具，MSKM管理長期記憶與檢索，透過插件整合。
- A詳: 技術原理說明：SK 掌控 Chat History、提示與工具呼叫；MSKM 管理導入與查詢。流程：在 SK 掛載 MSKM 的 Memory 插件，模型可直接呼叫 MSKM 搜索；或用 SK 先生成檢索專用內容，再送入 MSKM。核心組件：Plugins、Memory 接口、連接器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q12, C-Q6

Q11: 文件導入管線的技術原理？
- A簡: 內容抽取、分段、向量化與儲存，形成可檢索的長期記憶。
- A詳: 技術原理說明：1) Extraction（PDF→文字、圖片→OCR）2) Chunking（基於 tokens/語義/重疊）3) Embedding（選模型生成向量）4) Store（向量+原文+Meta）。流程：將文檔轉為可查詢單位，建立索引與標籤。核心組件：Handlers、Embedding 模型、向量庫。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q16, C-Q8

Q12: 分段策略與嵌入模型長度如何影響檢索？
- A簡: 模型有最佳輸入長度，分段需兼顧語義與上下文重疊。
- A詳: 技術原理說明：嵌入模型如 text-embedding-3-large 建議 512 tokens。過長失焦，過短失語境。流程：設計分段長度、重疊量、段落邊界與標題；搭配摘要提升資訊密度。核心組件：Chunker、摘要器、標籤策略。正確策略顯著提升命中與答案品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q13, D-Q5

Q13: 為何摘要、FAQ、案例能提升檢索品質？
- A簡: 將作者視角轉換為提問視角，提升語義對齊與密度。
- A詳: 技術原理說明：摘要（全局/段落）濃縮主旨；FAQ將問答化；問題/原因/解法映射故障排除脈絡。流程：用 LLM 先生成檢索專用內容，再向量化與標籤。核心組件：生成模板、標籤系統、導入管線。此法顯著改善長文命中與可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q23, C-Q9, D-Q5

Q14: 標籤（tags）在檢索中的作用？
- A簡: 作為過濾與排序的中繼資料，限定語域與內容範圍。
- A詳: 技術原理說明：在導入階段對 chunk 加上主題、語言、文件來源、段落類型等標籤。查詢時以 tags 進行過濾，減少語域噪音。核心步驟：標籤設計→導入寫入→查詢過濾。核心組件：Meta Schema、Filter 引擎、權重策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8, C-Q9

Q15: 如何用 BingSearch 作為 RAG 插件？
- A簡: 以工具規格宣告搜尋，模型自動構造查詢與取回結果。
- A詳: 技術原理說明：在 SK 掛載 BingSearch 插件，宣告查詢參數（query、limit、filters）。流程：模型決定是否呼叫，主程式執行並回寫來源與摘要，再由模型生成帶引用的答案。核心組件：插件連接器、工具參數設計、引用規範提示。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q25, C-Q6, D-Q8

Q16: MCP 的工具清單與呼叫流程機制？
- A簡: tools/list列出可用工具；tools/call帶參數調用並回傳結果。
- A詳: 技術原理說明：MCP 以 JSON-RPC 提供工具枚舉與呼叫介面。流程：client initialize→tools/list→挑選工具→tools/call(arguments)→回傳結果。核心組件：MCP server 實作、通訊層（stdio/SSE）、序列化策略。保證跨語言與平台一致運作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q10, D-Q2

Q17: MCP 與 OpenAPI/Swagger 對照原理？
- A簡: OpenAPI定義HTTP介面；MCP定義LLM工具協定與通訊。
- A詳: 技術原理說明：OpenAPI 靜態描述 REST 規格，便於生成客戶端；MCP 是 LLM 工具的運行協定，提供清單/呼叫/資源等 RPC。兩者可互補：用 OpenAPI 生成工具規格，再以 MCP 暴露給 LLM。核心組件：規格文件、協定實作、序列化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q10, C-Q6

Q18: LLM 成本與效能的取捨原理？
- A簡: 以程式代替可確定任務，降低 tokens，提升吞吐。
- A詳: 技術原理說明：LLM 成本隨 tokens 與模型級別增長。策略：1) 嚴格結構化輸出 2) 單一職責分工 3) 導入前生成檢索內容（一次性成本）4) 快取重用 5) 選擇適配模型（o1 用於高品質生成）。核心組件：成本監控、快取、降噪提示。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q19, D-Q10, C-Q8

Q19: Chat Completion 回應結構與使用計量？
- A簡: choices含訊息；usage含prompt/completion/total tokens。
- A詳: 技術原理說明：回應含 id、model、choices（message與finish_reason）、usage（prompt/completion/total）。流程：解析 message、判定是否工具呼叫、記錄 tokens 作為成本指標。核心組件：解析器、成本監控、重試策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q10, C-Q1

Q20: response_format：json_object vs json_schema？
- A簡: json_object僅格式要求；json_schema能嚴格驗證欄位型別。
- A詳: 技術原理說明：json_object 要求回覆為 JSON；json_schema 提供完整欄位定義與驗證。流程：選擇合適模式、提供 Schema、於程式端驗證與反序列化。核心組件：Schema 定義、驗證器、錯誤路徑。推薦用 schema 取得更強穩定性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q4, D-Q3

Q21: Planning 層如何落地 Function Calling？
- A簡: 手工提示規劃步驟，讓模型輸出指令序列與參數。
- A詳: 技術原理說明：以 system 提示定義目標與可用動作，要求模型輸出 JSON 指令序列（含參數）。主程式解析後執行。流程：規劃→執行→回寫→迭代。核心組件：策略提示、指令語法、監控。適用於前端+後端混合工具場景。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q6, C-Q4, B-Q6

Q22: Search GPT 的提示設計機制？
- A簡: 明確要求引用來源、禁止超出檢索內容的回答。
- A詳: 技術原理說明：在 system 提示宣告任務：必須先檢索，回答需含來源 URL，且不可超出證據。流程：宣告搜尋工具與參數，讓模型主動判斷檢索需求。核心組件：規範化提示、工具宣告、來源引用格式。此設計提升可追溯性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q25, C-Q6, C-Q8

Q23: 不支援 Function Calling 的模型如何模擬？
- A簡: 以前綴約定訊息角色，主程式攔截執行並回寫結果。
- A詳: 技術原理說明：system 提示定義「給用戶」與「給工具」前綴，模型依規則生成。流程：主程式監聽訊息，遇工具前綴則執行並回寫，再呼叫模型續推理。核心組件：前綴規約、解析器、執行器。用於驗證流程或暫時替代。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q26, C-Q4, D-Q4

Q24: SDK 相依與便利性的取捨？
- A簡: SDK帶來型別與工具整合便利，但需跟隨版本與生態。
- A詳: 技術原理說明：SDK 封裝協定細節、提供型別安全與插件機制（如 SK）。風險在相依變動與封裝限制。策略：關鍵路徑保留 HTTP 能力、非關鍵採 SDK 提升生產力。核心組件：抽象層、相依管理、版本治理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, C-Q2, C-Q6

Q25: MSKM 的部署選項與適用情境？
- A簡: Docker服務適合規模擴展；嵌入模式適合輕量與離線。
- A詳: 技術原理說明：Docker 適合雲端與團隊共享、易於水平擴展；嵌入模式將 MSKM 核心納入應用，降低外部依賴。選擇依任務量、延遲、運維能力而定。核心組件：容器化、連接器、資源配置與監控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q9, D-Q1

Q26: 向量相似度檢索的基本原理？
- A簡: 將查詢嵌入為向量，比對庫中向量的距離取得相關段落。
- A詳: 技術原理說明：輸入與文件段皆嵌入為向量，透過距離度量（cosine、dot）排序相似度。流程：查詢嵌入→過濾（tags）→Top-K→組裝提示。核心組件：嵌入模型、距離函數、索引結構（HNSW等）、中繼資料。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q16, B-Q8

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何用 HTTP Client 呼叫 OpenAI Chat Completion？
- A簡: 構造POST請求，帶APIKey、模型、messages與參數送出。
- A詳: 具體步驟：1) 設定 URL /v1/chat/completions 2) Headers：Authorization Bearer、Content-Type 3) Body含model、messages、temperature 4) 送出並解析choices與usage。程式碼片段：
  POST https://api.openai.com/v1/chat/completions
  Authorization: Bearer YOUR_KEY
  { "model":"gpt-4o-mini", "messages":[{ "role":"system","content":"..."},{ "role":"user","content":"..."}], "temperature":0.2 }
  注意事項：妥善管理金鑰、重試與錯誤處理、統計tokens。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, A-Q1, D-Q8

Q2: 如何用 OpenAI .NET SDK 實作簡單對話？
- A簡: 建立客戶端、指定模型與訊息，呼叫並讀取assistant回覆。
- A詳: 具體步驟：1) 安裝 OpenAI .NET SDK 2) 初始化 client（APIKey）3) 建立 ChatRequest：model、messages 4) 呼叫 CreateChatCompletionAsync 5) 讀取 result.Choices[0].Message.Content。程式碼：
  var client = new OpenAIClient(key);
  var req = new ChatRequest(model:"gpt-4o-mini", messages:new[]{new("system","..."), new("user","...")});
  var res = await client.Chat.CreateCompletion(req);
  注意事項：例外處理、timeout、模型版本與費用監控。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q24, B-Q24, C-Q1

Q3: 如何用 Semantic Kernel 實作 Structured Output並反序列化？
- A簡: 定義C#型別，SK自動產生Schema，回覆直接反序列化。
- A詳: 具體步驟：1) 定義 C# record/class 對應 JSON 2) 在 SK 建立 Function 要求輸出該型別 3) 呼叫並取得結果物件。程式碼片段：
  public record Address(string? street_address,string? city,string? postal_code,string? country);
  var result = await kernel.InvokeAsync<Address>(prompt);
  注意事項：欄位可空性、加入成功/失敗欄、驗證回覆，降低格式錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q3, D-Q3

Q4: 如何設計「購物清單」的 Function Calling？
- A簡: 宣告add/delete工具與參數，要求輸出指令序列JSON。
- A詳: 具體步驟：1) system提示列出可用動作與JSON格式 2) user描述需求 3) 模型生成 [{action, item, quantity}] 4) 程式解析並執行。程式碼片段（JSON設計）：
  [{ "action":"add", "item":"butter","quantity":"1" },{ "action":"delete","item":"bread" }]
  注意事項：動作語義清晰、枚舉與必填欄位、重複項合併、邏輯衝突處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q21, A-Q6

Q5: 如何實作「行程安排助理」的多步驟工具呼叫？
- A簡: 宣告check_schedule與add_event，迭代執行與回寫歷史。
- A詳: 具體步驟：1) 宣告兩工具規格（日期範圍、事件資訊）2) user提出需求 3) 模型先tool_calls:check_schedule 4) 執行並回寫tool-result 5) 模型判定空檔後tool_calls:add_event 6) 成功後assistant回覆。程式碼要點：迴圈處理tool_calls，直到finish_reason=stop。注意事項：時區、衝突檢查、錯誤重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, D-Q9

Q6: 如何在 SK 中掛載 BingSearch 等外部插件？
- A簡: 以插件或 OpenAPI 規格注入，設定金鑰與工具參數。
- A詳: 具體步驟：1) 取得 Bing Search 金鑰 2) 在 SK 建立插件（或注入 Swagger）3) 將工具暴露於 Kernel 4) 在提示中要求引用來源。程式碼片段：
  kernel.Plugins.Add(BingSearchPlugin(apiKey));
  var answer = await kernel.InvokeAsync("search", new{ query="景點", limit=3 });
  注意事項：速率限制、來源格式、multitool協調與安全過濾。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, A-Q25, D-Q8

Q7: 如何部署 MSKM Docker 並以 SDK 存取？
- A簡: 拉取官方映像，設定環境變數與連接器，程式端用NuGet訪問。
- A詳: 具體步驟：1) docker pull mskm:tag 2) docker run -p 8080:8080 -e EMBEDDING_PROVIDER=... 3) 檢查健康檢查 4) .NET 專案安裝 KernelMemory NuGet 5) 以客戶端導入/查詢。注意事項：版本選擇（中文分段建議0.96.x）、金鑰管理、連接器配置與資源限制。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q1, C-Q8

Q8: 如何將文章導入 MSKM，並加入「摘要」處理？
- A簡: 在管線加入Summarization handler或先用SK生成後導入。
- A詳: 具體步驟：1) 準備原文（md、pdf等）2) 配置 MSKM pipeline：Extraction→Chunking→Summarization→Embedding→Store 3) 或先用 SK 生成全局/段落摘要，再以自訂欄位導入。程式碼要點：tags 標示類型、語言。注意事項：摘要長度控制、中文模型適配、來源追蹤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q13, D-Q5

Q9: 如何生成 FAQ、問題/原因/解法並送入檢索？
- A簡: 用 LLM模板生成視角化內容，加上標籤後向量化導入。
- A詳: 具體步驟：1) 設計提示模板：FAQ、Problem/RootCause/Resolution/Example 2) 用高推理模型（如 o1）生成 3) 對每項加 tags（type、topic、language）4) 向量化與導入 MSKM。注意事項：一次性成本可控、嚴謹審核、避免重複與矛盾內容、持續更新。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q23, B-Q13, C-Q8

Q10: 如何以 MCP C# SDK 封裝 MSKM 為 MCPServer？
- A簡: 實作initialize、tools/list與tools/call，串接MSKM查詢。
- A詳: 具體步驟：1) 引入 MCP C# SDK 2) 實作 initialize 與 notifications 3) tools/list 輸出 search 等工具 4) tools/call 接受 arguments，調用 MSKM 查詢並回傳 5) 以 stdio/HTTP（SSE）運行。注意事項：中文 JSON 編碼（必要時 \uXXXX）、錯誤處理與安全過濾。可用 Claude Desktop 驗證。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q16, D-Q2, C-Q7

---

### Q&A 類別 D: 問題解決類（10題）

Q1: MSKM 新版中文分段出現「晶晶體」怎麼辦？
- A簡: 退版至0.96.x，等待新版修正；或自訂chunk策略。
- A詳: 症狀：中文分段出現疊字與斷詞異常。可能原因：token為基準的切分未針對中文優化。解決步驟：1) Docker 退版到 0.96.x 2) 自訂 Chunker（字詞分界/重疊）3) 加入段落摘要提升語義密度。預防：升級前在預備環境驗證中文處理品質與管線配置。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q7, B-Q12, C-Q8

Q2: Claude Desktop 與 MCP C# SDK 中文 JSON 無法解析？
- A簡: 將輸出改為\uXXXX編碼；追蹤SDK修正並回報issue。
- A詳: 症狀：中文包含於 JSON-RPC 回應，客戶端解析錯誤。原因：序列化與編碼不一致。解法：1) 調整 JsonSerializationOptions，輸出 Unicode escape 2) 自建 SDK 或等官方修正 3) 加入端到端測試。預防：在多語環境驗證編碼策略，設警示記錄。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q10, B-Q18, B-Q16

Q3: JSON 模式輸出不符 Schema 或缺欄位怎麼辦？
- A簡: 嚴格驗證、加入success欄與重試策略，必要時改寫提示。
- A詳: 症狀：反序列化失敗或欄位不全。原因：提示不夠明確、模型隨機性。解法：1) 使用 json_schema 2) Schema 加 success/status 3) 低溫度 4) 顯式示例 5) 加入重試與評估。預防：集中式 Schema 管理與單元測試，錯誤路徑清晰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q4, C-Q3

Q4: 工具未被模型選用或被錯誤呼叫怎麼辦？
- A簡: 強化工具描述與使用時機，限制參數與加入示例。
- A詳: 症狀：模型忽略必要工具或誤用參數。原因：工具描述模糊、提示不足。解法：1) 詳述用途、時機與限制 2) 示範正反例 3) 參數加型別/枚舉 4) 在系統提示明確要求先檢索後回答。預防：觀測工具呼叫率、調整提示與規格。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q22, A-Q8

Q5: RAG 檢索結果牛頭不對馬嘴如何改善？
- A簡: 生成摘要/FAQ/案例並加標籤，優化分段與過濾策略。
- A詳: 症狀：答案與原文語義偏離。原因：分段策略不當、語域不一致。解法：1) 先生成檢索專用內容 2) 調整 chunk 長度與重叠 3) 使用 tags 過濾 4) 選擇更適配的嵌入模型。預防：導入管線評測、查詢日誌分析與持續迭代。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q13, C-Q9

Q6: Chat History 過長導致成本高或截斷？
- A簡: 摘要對話、分段任務、以工具回寫資料減少上下文。
- A詳: 症狀：tokens 激增、回覆品質下降。原因：歷史累積過多。解法：1) 定期摘要歷史 2) 任務結束清理 3) 將資料移入長期記憶（MSKM） 4) 工具回寫取代冗長文本。預防：上下文上限監控與策略綁定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, B-Q8, C-Q8

Q7: 向量模型選擇錯誤導致查詢品質差？
- A簡: 選語域適配模型、遵守最佳長度、試驗Top-K與重疊。
- A詳: 症狀：相似度排序不合理。原因：模型語域不符或長度失當。解法：1) 選擇適配語言/領域模型 2) 控制輸入長度（如512 tokens）3) 調整 Top-K 與重疊策略 4) 以人工基準集驗證。預防：定期回歸測試與模型升級驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q26, C-Q8

Q8: SDK/HTTP 呼叫錯誤與認證失敗怎麼排查？
- A簡: 檢查端點與金鑰、Header、權限；加入重試與日誌。
- A詳: 症狀：401/403 或解析錯誤。原因：金鑰錯、端點不符、Header缺。解法：1) 驗證環境變數與設定檔 2) 比對 API 版本 3) 捕捉例外與重試退避 4) 記錄請求/回應。預防：集中式祕密管理、健全健康檢查。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, C-Q7

Q9: 工具呼叫的順序相依造成失敗？
- A簡: 嚴格依結果迭代，等待回寫後再決策下一步。
- A詳: 症狀：先加事件未先查空檔。原因：忽略前置工具依賴。解法：1) 迴圈處理 tool_calls 2) 每步必回寫 tool-result 3) 時序檢查與鎖定資源。預防：明確規範流程、加回合上限與時間戳驗證。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q7, C-Q5

Q10: 成本過高：LLM處理可用程式碼的任務？
- A簡: 以單一職責分工，代碼處理搜尋/計算，LLM專注推理。
- A詳: 症狀：費用高、延遲長。原因：將可確定性任務交給 LLM。解法：1) JSON Schema+反序列化 2) 程式處理格式/查詢/計算 3) 快取與重用 4) 選更便宜模型處理標準任務。預防：成本監控、提示審核與工具化設計。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q18, C-Q6

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Chat Completion API？
    - A-Q2: Chat Completion API 的消息角色有哪些？
    - B-Q2: Chat Completion API 的執行流程與主要欄位？
    - A-Q3: 什麼是 Structured Output（結構化輸出）？
    - A-Q4: JSON Schema 在 LLM 中的作用是什麼？
    - B-Q3: 結構化輸出（JSON 模式）如何保障解析？
    - A-Q5: 為什麼開發者應該使用 JSON 輸出？
    - A-Q6: 什麼是 Function Calling（工具使用）？
    - B-Q5: Function Calling 的技術機制？
    - A-Q9: 什麼是 RAG（檢索增強生成）？
    - A-Q10: RAG 的核心價值是什麼？
    - B-Q8: RAG 的標準管線原理？
    - C-Q1: 如何用 HTTP Client 呼叫 OpenAI Chat Completion？
    - C-Q2: 如何用 OpenAI .NET SDK 實作簡單對話？
    - D-Q8: SDK/HTTP 呼叫錯誤與認證失敗怎麼排查？

- 中級者：建議學習哪 20 題
    - A-Q11: 什麼是 Semantic Kernel（SK）？
    - A-Q12: 什麼是 Microsoft Kernel Memory（MSKM）？
    - A-Q13: SK Memory 與 MSKM 的差異？
    - B-Q9: MSKM 的架構與運作模式？
    - B-Q10: SK 與 MSKM 如何協同工作？
    - B-Q11: 文件導入管線的技術原理？
    - A-Q15: 什麼是 Chunking（分段）？
    - A-Q16: 什麼是 Embedding（向量化）？
    - B-Q12: 分段策略與嵌入模型長度如何影響檢索？
    - B-Q13: 為何摘要、FAQ、案例能提升檢索品質？
    - B-Q14: 標籤（tags）在檢索中的作用？
    - C-Q3: 如何用 Semantic Kernel 實作 Structured Output並反序列化？
    - C-Q4: 如何設計「購物清單」的 Function Calling？
    - C-Q5: 如何實作「行程安排助理」的多步驟工具呼叫？
    - C-Q6: 如何在 SK 中掛載 BingSearch 等外部插件？
    - A-Q25: Search GPT 類功能的本質是什麼？
    - B-Q22: Search GPT 的提示設計機制？
    - D-Q4: 工具未被模型選用或被錯誤呼叫怎麼辦？
    - D-Q5: RAG 檢索結果牛頭不對馬嘴如何改善？
    - D-Q6: Chat History 過長導致成本高或截斷？

- 高級者：建議關注哪 15 題
    - A-Q17: 什麼是 MCP（Model Context Protocol）？
    - A-Q18: MCP 的 stdio 與 SSE 有何差異？
    - B-Q16: MCP 的工具清單與呼叫流程機制？
    - B-Q17: MCP 與 OpenAPI/Swagger 對照原理？
    - C-Q10: 如何以 MCP C# SDK 封裝 MSKM 為 MCPServer？
    - D-Q2: Claude Desktop 與 MCP C# SDK 中文 JSON 無法解析？
    - A-Q23: 為何要產生「檢索專用資訊」？
    - C-Q8: 如何將文章導入 MSKM，並加入「摘要」處理？
    - C-Q9: 如何生成 FAQ、問題/原因/解法並送入檢索？
    - B-Q18: LLM 成本與效能的取捨原理？
    - B-Q21: Planning 層如何落地 Function Calling？
    - B-Q24: SDK 相依與便利性的取捨？
    - D-Q1: MSKM 新版中文分段出現「晶晶體」怎麼辦？
    - D-Q7: 向量模型選擇錯誤導致查詢品質差？
    - D-Q10: 成本過高：LLM處理可用程式碼的任務？