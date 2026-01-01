---
layout: synthesis
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"
synthesis_type: summary
source_post: /2025/06/22/inside-semantic-kernel/
redirect_from:
  - /2025/06/22/inside-semantic-kernel/summary/
postid: 2025-06-22-inside-semantic-kernel
---
# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 摘要提示
- Chat Completion API: 所有示範都以 OpenAI 規格的 Chat Completions 為基礎，核心難題在「怎麼用」而非 API 本身。
- Structured Output / JSON Schema: 用可反序列化的結構化輸出接軌程式流程，並明確標示成功/失敗以降低不確定性。
- Function Calling（Basic）: LLM 能把自然語言意圖翻譯成「指令序列＋參數」，成為工具/系統的控制中樞。
- Function Calling（Case Study）: 透過 tool / tool-result 的多回合對話，完成有相依順序的任務（如排程）。
- RAG 與 Function Calling: RAG 的「檢索→組 prompt→生成」可由 Function Calling 觸發，形成類 SearchGPT 的工作模式。
- Microsoft Kernel Memory（MSKM）定位: MSKM 解決長期記憶與文件匯入管線（ingestion）等完整 RAG 流程，並以服務＋SDK 形式提供。
- MSKM × Semantic Kernel（SK）整合: MSKM 內建 SK Memory Plugin，且 MSKM 本身也用 SK 打造，天然相容多種 connector。
- 進階 RAG：生成檢索用內容: 在匯入前用 LLM 生成摘要/FAQ/解題案例等多視角內容，提高長文與跨視角查詢的命中率。
- MSKM 對外整合（MCP 等）: 可把 MSKM 封裝成 MCP Server，接到 Claude Desktop 等 host，讓 LLM 以統一協定使用工具。
- 土炮 Function Calling: 即使模型/介面不支援原生 function calling，也可用 prompt 規範角色與訊息前綴，靠應用程式攔截執行。

## 全文重點
本文整理一場以「.NET 開發 AI 應用」為主題的直播內容，從最底層的 LLM Chat Completion 操作，一路鋪陳到結構化輸出、Function Calling、RAG，再到 .NET 生態中用來落地 RAG 的核心組合：Semantic Kernel（SK）與 Microsoft Kernel Memory（MSKM），最後延伸到 MCP 等跨系統整合與「土炮」替代方案，並附上相關資源、範例程式碼與問券回饋統計。

作者先以 Chat Completion API 作為所有案例的共同基礎，強調 LLM 的 API 形式其實相對單純：把 system/user/assistant 等歷史訊息一起送出，得到下一段回覆；複雜度不在 API，而在「如何把它設計成能解決問題的應用模式（design patterns）」。接著進入 Day 1 的 Structured Output，討論當 LLM 成為應用程式的一個服務時，開發者要思考輸出格式、失敗判定與責任切分等工程問題。作者主張以 JSON／JSON Schema 讓輸出可直接反序列化為 C# 型別，並在輸出中明確標示成功/失敗，避免程式端用猜測與例外處理去對抗 LLM 的不確定性；同時把搜尋、計算、格式轉換等「程式做更好更便宜」的工作留給 code，LLM 只做非它不可的語意理解與抽取。

Day 2～3 聚焦 Function Calling（Tool Use）。先以購物清單例子說明：只要先告訴模型有哪些可用動作與參數，LLM 就能把對話意圖翻譯成指令序列（近似自然語言到指令集的編譯器）。進一步的案例則展示多回合工具呼叫：LLM 先要求查行事曆（tool），應用程式代為執行後回傳結果（tool-result），LLM 再決定新增行程，最後以自然語言回覆使用者。作者指出，理解這個「history 逐步累積、每回合帶著工具結果再推理」的本質，能幫助開發者在框架不足或需要更高層 planning 時自行掌控流程。

Day 4 將 RAG 放在 Function Calling 之後，是因為作者把「檢索」視為一種工具呼叫：RAG 的基本流程是把問題收斂成查詢、檢索資料（向量庫/全文檢索/搜尋引擎皆可）、再把檢索結果組成 prompt 讓 LLM 基於外部知識回答並附來源；而觸發檢索、產生查詢參數、限制回答範圍等，都可以透過 Function Calling + JSON 模式完成，形成類似 SearchGPT 的體驗，且搜尋目標可替換成自家知識庫。

Day 5 正式引入 MSKM，定位為「RAG as a Service」與長期記憶管理的核心：相較 SK 的 Memory（更像向量資料庫的抽象與 CRUD/相似度檢索介面），真正棘手的文件匯入管線（內容抽取、分段、標註、向量化、寫入、查詢等）需要更完整的流程與長時間任務處理能力，因此 MSKM 以獨立服務＋SDK 形式提供，可用 docker 部署、也能內嵌於應用。作者並點出 MSKM 與 SK 的兩個整合亮點：MSKM 內建 SK Memory Plugin 便於以工具形式掛進 SK；且 MSKM 本身以 SK 開發，SK 支援的各種 AI connector（LLM/embedding 等）也能在 MSKM 延伸使用。

Day 6 討論進階 RAG：僅靠把長文切 chunk 並向量化，對於「跨視角」問題常會命中不佳，尤其作者部落格文章長、單篇可切成上百段，查詢很容易落到不對焦的片段。改進策略是在匯入前先用 LLM 生成「更適合被檢索」的內容，例如整篇摘要、段落摘要、FAQ、解題案例（problem/root cause/resolution/example），並用 tags 分類後一併向量化。這等於把「作者寫作視角」轉換成「使用者提問視角」的索引素材，因為這些生成是離線處理一次即可，作者甚至選用更強但較貴的模型（如 o1）換取更好的檢索品質。作者也因此將 RAG 視為一種需要客製化調教的設計模式，而非買來即用的產品。

Day 7 延伸到 MSKM 與其他系統整合，整理 function calling 可落地的多種管道：ChatGPT GPTs/Custom Action、No-code 平台（如 Dify）、支援 MCP 的 host（如 Claude Desktop）、或自行用 SK 在本地做 native function calling。作者指出這些方式本質一致：一是把工具規格告訴 LLM，二是 host 代替 LLM 執行工具並回傳結果。MCP 則以明確協定與通訊方式（stdio、SSE/http）標準化這套流程，因而被稱為 AI 的 USB-C；文中也分享實作 MCP Server 封裝 MSKM 的 demo，以及目前在中文 chunking 與中文 JSON 編碼上的踩坑與 workaround。

Day 8 則回應「模型不支援原生 function calling 怎麼辦」：只要推理能力足夠，function calling 可被視為 API 封裝問題。作者示範以土炮 system prompt 自訂角色與訊息前綴，讓模型輸出「給使用者看的話」與「要求祕書執行的指令」，由應用程式攔截指令並執行、再把結果回灌到對話歷史中，仍能完成類 function calling 的閉環，藉此幫助讀者理解背後通訊本質。

最後文章整理問券回饋：多數人最有收穫的集中在 function calling、RAG 與 MSKM 的落地方式，以及從底層 API 到框架整合的循序拆解；後續期待包含 MCP、更進階整合情境、更多實作工作坊與商務案例等。

## 段落重點

### 相關資源與連結
本文提供完整延伸材料：作者臉書、YouTube 錄影、回饋問卷、GitHub 範例程式庫與 .NET Conf 2024 簡報。整體內容採「先在 FB 分段釋出→事後整理成文章」的方式，以對抗 AI 領域快速迭代造成的資訊時效問題。讀者可依需求選擇：想快速理解觀念看文章段落與簡報；想看完整實作流程看影片；想直接動手則從 GitHub demo 進入。

### Day 0, Chat Completion API
全篇的共同基礎是 Chat Completion 的對話模型：每次呼叫都把 system/user/assistant 的對話歷史一起 POST 給 API，取得下一段 assistant 回覆；若要繼續對話，就把這次回覆也加入 history 再呼叫一次。作者用最小示例說明 request 組成（headers、model/parameters、messages，以及可選的 tools、response format），並強調 API 其實不複雜，真正要學的是如何把它組合成能解題的應用設計模式（AI App Design Patterns）。同時也交代接下來段落的閱讀方式：每日主題在 FB 有介紹，實作與細節在影片，兩者搭配可吸收更多討論脈絡。

### Day 1, Structured Output
作者以「從對話抽取地址」為例，說明當 LLM 功能要進入應用程式與批次流程時，開發者不能只用「貼到 ChatGPT 叫它回答」的思維，而要思考工程化議題：輸出格式要可被程式可靠消化、如何判定失敗（避免靠猜或例外）、以及責任切分（LLM 做語意抽取，其他任務交給程式與外部 API）。核心做法是使用 JSON output，最好再提供 JSON Schema，讓結果能立刻 deserialize 成 C# object 並進入後續流程；此外在輸出內顯式帶出成功/失敗狀態，降低幻覺與不確定性造成的風險。作者也提到 SDK/框架帶來的差異：若要手寫 schema 與驗證成本高，Semantic Kernel 可用 C# type 直接生成需求，讓開發體驗改變。

### Day 2, Function Calling (Basic)
作者將 Function Calling（Tool Use）視為 LLM 普及以來最具威力的能力之一，也是 Agent 與 AI 主控周邊系統的基礎。以購物清單為例：先用 system prompt 定義允許的動作（add/delete）與參數格式，再給使用者需求，LLM 便能推論意圖並輸出對應的指令序列（以 JSON 表示），等同把自然語言翻譯成可執行的「指令集」。作者提醒：此階段只是「呼叫指令」的表達，真正完整閉環還需要「執行並回傳結果」，進一步的多回合流程留到隔天案例。

### Day 3, Function Calling (Case Study)
此段以「找明早 30 分鐘慢跑空檔並自動加入行事曆」為案例，完整拆解 function calling 的多回合閉環：LLM 先要求呼叫工具 check_schedule，應用程式代為執行後用 tool-result 回傳可用/不可用時段；LLM 再根據結果要求 add_event，應用程式回傳 success，最後 LLM 才以自然語言向使用者確認完成。作者同時說明訊息角色：system/user/assistant 外，還有 tool（LLM 要求執行）與 tool-result（工具結果回灌）。並指出：雖可用土炮方式自己串，但實務上建議用成熟框架（如 SK）、no-code 平台（n8n/dify）或支援工具協定的客戶端（Claude Desktop/Cursor）簡化大量細節；然而開發者仍必須理解原理，才能在跨前後端、多工具、或更高層 planning 情境下掌控設計。

### Day 4, RAG with Function Calling
作者介紹 RAG（檢索增強生成）的核心目的：讓 LLM 依據外部檢索內容回答，避免只依賴訓練記憶（可能過時或偏差）。基本流程為：收斂問題成查詢 → 檢索（向量庫/全文檢索/搜尋引擎皆可）→ 組合檢索結果與問題進 prompt 生成答案並附來源。作者刻意把 RAG 放在 function calling 之後，因為「檢索」可以被當成一種 tool：在 system prompt 交代必須先檢索、回答要附來源且不得編造，再提供搜尋工具定義，LLM 就能自動把提問轉成查詢參數（仰賴 JSON/structured output 抽取），必要時呼叫搜尋工具取得結果後再生成答案。這相當於做出 SearchGPT 類能力，只是把搜尋來源換成自己的知識庫；作者也以 Bing Search plugin + 其他 plugin（定位、天氣）展示 LLM 如何整合工具鏈完成複合需求。

### Day 5, MSKM: RAG as a Service
主角 Microsoft Kernel Memory（MSKM）登場，被定位為解決 AI App「長期記憶」與完整文件匯入管線的服務化方案。作者指出 SK 的 Memory 更像向量資料庫的抽象（類 EF 對 RDBMS），但真正困難的 ingestion 流程（抽取、分段、標註、向量化、寫入、查詢等）與長任務處理，SK 只涵蓋其中一小段，因此 MSKM 被獨立成「服務＋SDK」：可用 docker 直接部署，也能以 serverless/內嵌方式整合進應用。並強調 MSKM 與 SK 的互補：MSKM 內建支援 SK Memory Plugin，能直接掛進 SK 的工具箱讓 LLM 透過 function calling 操作；且 MSKM 本身用 SK 開發，SK 的多種 AI connector（openai/azure openai/ollama/claude…）也可直接沿用。作者結論是：在 .NET 領域，SK + MSKM 是目前成熟度很高的組合，但受眾是開發者，因此需先具備 JSON、function calling、RAG 等基礎觀念才能體會其設計價值。

### Day 6, 進階 RAG 應用, 生成檢索專用的資訊
作者以自身部落格長文（單篇 50k～100k、330 篇）做實測，指出只靠預設 pipeline（抽取→chunking→embedding→store）雖能回答近距離問題，但對「抽象、跨段、跨視角」的提問常命中不佳：文章被切成 100+ chunks 後，向量檢索容易挑到語意密度不匹配的片段。改善關鍵是：在匯入前或匯入 pipeline 中，先用 LLM 生成更適合被檢索的「索引內容」，例如整篇摘要、段落摘要、FAQ、解題案例（problem/root cause/resolution/example）等，並加上 tags 後一起向量化。這相當於把「作者的寫作方式」轉譯成「使用者提問方式」的多視角資料，讓相似度檢索更容易對焦。由於這些生成是離線一次性工作，作者選用較強模型（如 o1）換取品質，再交由 MSKM 管理與檢索，最後用 RAG 回答。作者因此將 RAG 視為必須調教的設計模式：要理解內容特性、預期查詢方式，並準備一套工具箱（SK、MSKM、no-code 平台等）靈活組裝。

### Day 7, MSKM 與其他系統的整合應用
此段整理 function calling 在不同生態的落地途徑：ChatGPT GPTs + Custom Action（OpenAPI + OAuth）、No-code 平台（如 Dify 的 Custom Tools，亦基於 OpenAPI）、Claude Desktop 等 MCP Host、或自行以 SK 掛 plugin 進行 native function calling。作者強調這些方式本質一致：一是把 function specs 提供給 LLM，二是由 host 以統一方式執行並回傳 function result。MCP（Model Context Protocol）則把這套流程標準化成協定（initialize、tools/list、tools/call、resources/list、prompts/list…），並支援 stdio 與基於 SSE 的 http 通訊，使工具整合跨語言跨平台，因而被稱為 AI 的 USB-C。作者也分享實務踩坑：MSKM docker image 新版 chunking 對中文 token 分段有問題需暫退版；MCP csharp-sdk/Claude Desktop 對含中文的 JSON 編碼處理不佳需暫時 workaround，並附 demo 程式碼與指令範例。

### Day 8, 土炮 Function Calling
作者回應「Deepseek r1 不支援 function calling 卻能被某些 client 使用」的疑問，指出：是否支援常是 API 封裝層問題，只要模型推理夠強，仍可用 prompt + 應用程式攔截來土炮實作。作者先回顧原生 function calling 的三要點：定義 tools、區分 user/tools 的三方對話、由 LLM 產生要用哪個 tool 與參數；再用自訂 system prompt 定義兩種前綴語句（一種給使用者、一種要求「秘書」執行指令），讓 LLM 在純文字回覆中輸出可被程式判讀的「工具呼叫」。應用程式偵測到指令前綴就去執行工具並把結果再回灌到對話歷史，循環直到 LLM 回覆完成。作者強調此法主要用於理解原理與特殊情境，正規開發仍建議使用支援 function calling 的模型與能協助管理流程的框架（如 SK）。

### 問券回饋 (統計至 2025/06/22)
作者統計直播/錄影回收 93 份問卷，整理出多個面向：哪些主題對工作最有幫助、常用的 LLM 存取方式、內容節奏是否冗長，以及文字回饋的分類彙整。整體而言，回饋集中肯定「循序漸進從底層到整合」、「function calling 的 request/response 脈絡被講清楚」、「RAG 落地與切片/索引策略很有啟發」，也有人期望後續能更深入 MCP、更多產業應用/工作坊、更多 agent/process 相關內容，並提到部分細節（如向量/節奏/投影片）希望更清晰或更慢。整体評分圖亦顯示多數回饋為正向，問卷也將持續開放蒐集後續意見。

## 資訊整理

### 知識架構圖
1. **前置知識**：學習本主題前需要掌握什麼？
   - LLM 基本概念：Prompt、token、context window、幻覺與不確定性
   - OpenAI Chat Completions 的通訊模型：request/response、messages(role: system/user/assistant)
   - .NET 基礎：HttpClient、JSON 序列化/反序列化、NuGet、SDK 使用
   - API 與規格：JSON Schema、OpenAPI/Swagger（理解「規格→可被工具化」）
   - 檢索基本概念：全文檢索 vs 向量檢索、Embedding、chunking

2. **核心概念**：本文的 3-5 個核心概念及其關係
   - **Chat Completion 是一切的基礎**：所有能力（結構化輸出、工具呼叫、RAG）都可視為在同一對話協定上擴充。
   - **Structured Output（JSON/JSON Schema）**：把 LLM 輸出「工程化」，讓程式能穩定解析、判斷成功/失敗、進入後續流程。
   - **Function Calling / Tool Use**：讓 LLM 不是只回答文字，而能「決定要呼叫什麼工具與參數」，由宿主程式代執行並回傳結果，形成迭代式任務完成。
   - **RAG（檢索增強生成）**：先檢索再生成；常由 Function Calling 觸發（工具=搜尋/查詢），再把檢索結果餵回 LLM 生成答案並要求引用來源。
   - **MSKM（Microsoft Kernel Memory）+ SK（Semantic Kernel）**：MSKM 專注長期記憶與文件 ingestion pipeline（RAG as a Service），SK 提供工具/Plugin 編排與更高階開發體驗，兩者可透過 Plugin 整合。

3. **技術依賴**：相關技術之間的依賴關係
   - Chat Completion API  
     →（加上 response_format / JSON Schema）Structured Output  
     →（加上 tools 定義 + tool/tool-result 訊息）Function Calling（可連續多輪）  
     →（工具 = 搜尋/向量庫查詢）RAG  
   - Semantic Kernel（框架）  
     → 封裝 Chat、Structured Output、Function Calling 的流程與程式樣板  
     → 以 Plugins 提供工具給 LLM（含 Swagger 注入）  
   - Kernel Memory（服務/SDK）  
     → 提供文件匯入 pipeline（抽取/分段/向量化/儲存）與檢索介面  
     → 內建支援 SK Memory Plugin（讓 MSKM 能成為 SK 的工具箱）  
   - MCP（Model Context Protocol）  
     → 以協定標準化「列出工具/呼叫工具/回傳結果」  
     → 可把 MSKM 封裝成 MCP Server，供 Claude Desktop 等 Host 使用  
   - No-code / Client 平台（Dify、GPTs Custom Action、Claude Desktop、Cursor）  
     → 不同形態提供：工具規格宣告 + 代執行工具 + 回傳結果 的宿主能力

4. **應用場景**：適用於哪些實際場景？
   - 大量對話/文本的**資訊抽取**（地址、欄位、分類、狀態）並進入後端流程
   - **Agent/助理型應用**：排程、下單、查詢系統、跨系統編排（連續工具呼叫）
   - **SearchGPT 類產品**：外部搜尋（Bing/Google/內部知識庫）+ 引用來源回答
   - **企業/團隊知識庫 RAG**：文件匯入、長期記憶管理、權限/標籤檢索（偏後端服務型）
   - **內容型資產（長文/大量文章）RAG 優化**：先生成摘要/FAQ/解決方案視角內容，提高命中率
   - **跨宿主整合**：用 MCP 把能力輸出給桌面端/No-code 平台/不同 LLM Host

---

### 學習路徑建議
1. **入門者路徑**：零基礎如何開始？
   1) 先用 HttpClient 打通 Chat Completions（理解 messages/role/context window）  
   2) 學會 Structured Output：先 JSON，再 JSON Schema，並做 C# deserialize  
   3) 學會 Function Calling 的「三方對話」概念：assistant(tool_calls) → tool-result → assistant  
   4) 用 SK 重做一次相同案例（體會框架減少的樣板與風險）

2. **進階者路徑**：已有基礎如何深化？
   1) 連續 Function Calling case study（有相依順序、要看 tool-result 再決策）  
   2) 將 RAG 視為「工具呼叫的應用」：query 生成、檢索、引用來源、避免超出檢索內容  
   3) 引入 MSKM：理解為何 SK Memory 不足以涵蓋 ingestion pipeline，改用 MSKM 管 long-term memory  
   4) 研究不同宿主形態（Swagger/GPTs/Dify/MCP）在「工具規格宣告+代執行」上的等價性

3. **實戰路徑**：如何應用到實際專案？
   1) 選定一個「可量化」任務：抽取結構化資料 / 自動排程 / 知識庫問答  
   2) 先定義輸出契約（JSON Schema + success/failure 欄位）與工具清單（最小可用）  
   3) 做 RAG：選檢索來源（Bing/全文/向量庫/MSKM），落實引用來源與「不回答檢索未提及」  
   4) 對長文內容做 ingestion 前增強：摘要/FAQ/解決方案視角 + tags，再送入 MSKM  
   5) 規劃整合面：SK Plugins（程式內）或 MCP Server（跨工具生態），再決定部署型態（service / embedded）

---

### 關鍵要點清單
- Chat Completions 通訊模型：每次都送出完整對話歷史，LLM 回傳下一步內容 (優先級: 高)
- Message Roles（system/user/assistant）：用 role 管理上下文與優先權，是工程化對話的基礎 (優先級: 高)
- Structured Output（JSON Mode）：要求固定 JSON 格式，讓後續程式可可靠接手處理 (優先級: 高)
- JSON Schema 支援：用 schema 約束輸出結構，降低解析失敗與歧義 (優先級: 高)
- 成功/失敗明確回報：在輸出中加入可判斷狀態，避免靠猜測或例外處理 (優先級: 高)
- 單一職責與成本意識：LLM 做「非它不可」的事，其餘交給程式/外部 API，避免 token 成本放大 (優先級: 高)
- Function Calling（Basic）：LLM 產生要呼叫的工具與參數，程式依序執行 (優先級: 高)
- Function Calling（Return/Loop）：tool-result 回填後，LLM 依結果決策下一步直到完成任務 (優先級: 高)
- RAG 基本流程：問題收斂→檢索→組 prompt 生成答案，是可被拆解的管線 (優先級: 高)
- 用 Function Calling 觸發 RAG：把「搜尋/查庫」包成工具，讓 LLM 自動決定何時檢索 (優先級: 高)
- Semantic Kernel 的價值：以 Plugins/抽象封裝減少手刻細節，適合複雜 tool-use 流程 (優先級: 中)
- Kernel Memory 的定位（RAG as a Service）：補足 ingestion pipeline（抽取/分段/向量化/儲存/查詢）與長期記憶管理 (優先級: 高)
- MSKM × SK 整合：MSKM 提供 SK Memory Plugin，讓 MSKM 能直接成為 LLM 可用工具 (優先級: 高)
- 進階 RAG：先生成「摘要/FAQ/解決方案」等檢索專用內容以對齊使用者查詢視角 (優先級: 高)
- MCP 與多宿主整合：以協定標準化 tools/list、tools/call 等，將 MSKM 封裝成 MCP Server 供 Claude Desktop 等使用 (優先級: 中)