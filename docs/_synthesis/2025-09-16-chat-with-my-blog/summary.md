---
layout: synthesis
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計"
synthesis_type: summary
source_post: /2025/09/16/chat-with-my-blog/
redirect_from:
  - /2025/09/16/chat-with-my-blog/summary/
postid: 2025-09-16-chat-with-my-blog
---
# 讓 Agent 懂我的部落格: MCP-first 的服務化設計

## 摘要提示
- MCP-first: 以 MCP 為核心把部落格資源服務化，讓 Agent 能在工作流程中精準運用內容。
- Workflow First: MCP 不是 API 包裝，必須從使用者與 Agent的工作流程設計出 Tools、Prompts、Resources。
- Tools 設計: 核心工具包含 GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts，對應發現/檢索/取用。
- 內容正規化: 以 LLM 預先生成 FAQ、Solution 等合用型態，提升 RAG 精度與可用性。
- 效率化重構: 透過 AI IDE 清技術債、轉 Markdown、修路徑與連結，優化內容管線。
- 實作案例: 問答對話、部落格演進史整理、依文章 vibe coding 三類任務驗證設計。
- 產業參考: Shopify.Dev 與 Context7 的 MCP 設計示範分層工具與「為 Agent 而設計」的最佳實務。
- API→MCP: 預示 SaaS 的下一步是 MCP 作為 Agent 時代的 API，朝「工作流程訂閱」演化。
- Context 工程: 以「先檢索後讀取」與強制流程起手式控管資訊量，讓回答更穩定精準。
- 使用說明: 提供 Streamable HTTP 的 MCP URL，可於 VSCode/ChatGPT Plus 直接加入使用。

## 全文重點
作者提出「讓 Agent 懂我的部落格」的目標，以 MCP-first 重構部落格，把內容變成可被 Agent在工作流程中有效使用的工具與素材。動機來自長文心法對人類讀者門檻高，但 AI 能把碎片化知識轉為可解題的上下文。整體改造分三路：一是內容服務化，設計 MCP Tools 對應 Agent 的思考脈絡與操作流程；二是內容正規化，先以 LLM 將長文重煉成適合 RAG 的型態（FAQ、Solution、Summary、Origin等），讓檢索更精準可用；三是流程效率化，用 AI IDE 清技術債、轉格式與修管線，讓後續預處理與服務化更順暢。

文章核心主張「MCP != API」，要從 Workflow First 出發思考 Agent 如何解題，將人類的操作拆解為工具介面。作者以「微服務的排程處理」為例，分析真人會先理解專家用法（GetInstructions），再找線索（SearchChunks）、定位原文（GetPostContent）、延展相關（GetRelatedPosts），因此 MCP 工具就自然落在這些步驟。並以三個案例驗證：ChatGPT 問答能精準引用與回鏈；在 VSCode + Copilot 中用 MCP 快速整理部落格演進史；依文章以 Coding Agent 生成符合現代 .NET 寫法的並行 CLI 管線，展現從「找→讀→用」的端到端體驗。

後半探討 Shopify.Dev 與 Context7 的 MCP 設計：Shopify 以「洋蔥式分層」工具與強制起手式 learn_shopify_api（發 conversationId）保證流程一致，再以 search_docs_chunks/fetch_full_docs 控管上下文，並提供 GraphQL introspect/validate 確保代碼正確；Context7 以兩個簡單工具 resolve-library-id 與 get-library-docs，直接把「最新、版本化、可執行」的官方片段寫入上下文，避免幻覺與過時代碼。作者據此提出產業觀察：SaaS 的 API 將演化為 MCP，「Agent 成為主要使用者」後，軟體服務的價值在於能否以 MCP 提供可直接被 Agent操作的工作流程。收尾指出 Context 管理是效率關鍵，需用「先檢索後讀取」與流程護欄避免爆量資訊；並提供 MCP URL 與 VSCode/ChatGPT 使用方式。下一篇將深入內容預處理的設計。

## 段落重點
### 1, 為什麼要把部落格做成 MCP?
作者目標是讓長文心法能被 Agent有效理解與應用，縮短從閱讀到解題的距離。改造分三項：內容服務化（設計 MCP Tools 對應 Agent流程）、內容正規化（先以 LLM 重煉成利於RAG的型態，解決長文切片不完整的問題）、流程效率化（用 AI IDE 清技術債與重構 repo）。其中 Tools 的介面設計是成敗關鍵，必須以情境與工作流程為導向，而非僅把既有 REST 包裝成 MCP。作者亦回顧對 MCP 的理解源於研究 Shopify.Dev 與社群分享，體認「Model Context Protocol」的重點在於如何為模型塑造可操作的上下文。

### 2, MCP != API, 從流程的角度設計
作者強調 MCP 不是 API 包裝，設計要從 Workflow First 出發。提出自己的 MCP Tools 規格：GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts，並解釋其對應「發現/檢索/取用/延展」的步驟。再回扣過去「API First→AI First」的演講要點：API 要合情合理、可靠、精準對應領域問題、避免 UI 導向與檯面下溝通。如今進一步體會到，面對 Agent 呼叫不可預測，必須以工作流程設計工具，讓 LLM 能在上下文中自然操作，降低誤用與幻覺。

### 參考1: 從 API First 到 AI First
整理兩篇舊文的核心：為 AI 設計的介面要合乎常理、邊界嚴密、直指領域問題；避免 UI導向與人類默契的黑箱。作者自省去年仍以 API視角排除障礙，如今意識到真正焦點是「context + workflow」。結論是：不要用 API 的角度設計 MCP，改以工作流程設計，讓工具自然嵌入 Agent 的解題脈絡。

### 參考2: iHower 電子報 #31
引用 iHower 的整理與 Block 的 Playbook：當工具爆量時，用分層（發現/規劃/執行）引導 Agent；MCP-first 是開發典範轉移，工具介面要為 AI 使用者設計。作者補充 Agent 擬人化的觀點：使用者授權工具給 Agent，MCP 的設計需符合使用者工作流程，使 Prompt 無需額外轉譯，避免幻覺與偏差。

### 參考 3: Workflow First, 使用情境分析
以讀者常見需求（訂閱/解答/解題/學習）分析工作流程，選「解題」示範：真人會先理解前輩（GetInstructions）、索取線索（SearchChunks）、獲取原文與延伸（GetPostContent/GetRelatedPosts）。因此 MCP Tools 直接設計為上述動作。作者列出第一版工具規格與參數設計，說明工具越貼近流程，Agent 操作成本越低，應變更好。後續以案例驗證此設計。

### 3, 三個實際的案例示範
三類任務展示端到端體驗：1）問答對話：在 ChatGPT/Claude 皆能準確檢索與引用，查詢策略略有不同但結果正確且可回鏈；2）部落格演進史整理：在 VSCode + Copilot 下以 MCP 快速彙整多篇散佈內容，產出時間序摘要與連結，效率遠勝手工；3）vibe coding：依文章用 Coding Agent 產生現代化 .NET 並行 CLI 管線，示範從 SearchPosts/GetPostContent/SearchChunks到程式生成的完整流程，且語法與庫選擇更新至當代最佳做法。

### 案例 1, 直接對話的應用 (ChatGPT)
同題在 ChatGPT Plus（GPT-5 + Thinking）與 Claude Sonnet 4 的使用觀察：兩者皆先 GetInstructions，再以 SearchChunks 檢索相關主題片段；Claude直線思考一次查詢，ChatGPT傾向分兩次迭代查詢優化範圍。回覆皆能準確摘要並附正確引用連結，展現 MCP 工具在問答場景的可用性與穩定性。附分享連結以供讀者參考完整對話。

### 案例 2, 整理我的部落格演進史
在 VSCode + Copilot 中以提示要求彙整部落格系統演進（年份/系統/客製化/參考文），Agent 透過 MCP 快速檢索並回填 Markdown。示範段落包含 BlogEngine.NET 時期的匯入與擴充、短期 WordPress 嘗試、改用 Jekyll + GitHub Pages 等。作者對比九年前的手工整理，感嘆生成式AI在文本整編上的躍進，強調不以 AI 代寫文章，但高度接受其在資料搜集與整理上的賦能。

### 案例 3, 拿文章來 vibe coding
切換至 VSCode + Copilot 的 Coding Agent，要求依「後端工程師必備：CLI + Pipeline」文章實作 STDIN JSONL 並行處理框架。Agent 先透過 MCP 檢索文章與片段，再輸出以 Channel reader/writer 的現代 .NET 寫法、生成測試資料與腳本，完成端到端驗證。作者指出此法不僅滿足架構要求，還自動更新到更佳語法與庫，展現以「找→讀→用」串起知識到產出。

### 案例小結
除文中示範，作者亦測試了 Resource 用法（在 VSCode 直接以 URI取文）、agent mode 下 add context、從部落格作為知識庫生成學習計畫、測驗題與實作講義等。整體證明內容服務化後，可大量衍生教育與工程應用，且能精準對齊作者當年觀念與心法。

### 4, 參考 Shopify / Context7 的 MCP 設計
選兩個優秀 MCP 做設計觀摩：Shopify.Dev 對開發者場景設計分層工具、流程護欄與 GraphQL 支援；Context7 專注於通用開發文件檢索，以最小工具集將「官方、最新、版本化」片段寫入上下文。兩者共同重點：先「發現」與「學習」規則，再「檢索」與「取用」內容，並以 Markdown 輸出提升 LLM 理解品質，杜絕幻覺與過時資訊。

### MCP 設計參考 1: Shopify.Dev MCP
工具集包含 learn_shopify_api（強制起手式，發 conversationId）、search_docs_chunks/fetch_full_docs（先檢索片段再取全文）、introspect_graphql_schema/validate_graphql_codeblocks（先得正確Schema、後驗代碼）。關鍵巧思是把使用規則與會話ID嵌入回應，迫使Agent遵循流程；以 Markdown 供上下文閱讀更精準；並以最後一步的驗證工具保障產出正確，形成完整的「發現/檢索/生成/驗證」鏈。

### MCP 設計參考 2: Context7
僅兩個工具：resolve-library-id（把泛名庫解析為 Context7 兼容ID）與 get-library-docs（依ID與主題取回官方最新片段），但回應同時夾帶「使用規則」與「信任分數/片段數等元資料」，讓 Agent 能即時理解並選擇最佳來源。此設計直攻 Coding Agent 需求：減少分頁切換、避免幻覺、避免過時代碼，使「寫在上下文的官方片段」成為生成保真度的核心。

### MCP 應用的想像 - 下個世代的 API
作者預測 MCP 將成為 Agent 時代的 API。SaaS 過去靠 API 供整合，如今 Agent 能自讀規格與主動呼叫，服務方更該提供 MCP 以工作流程為單位交付能力。軟體產業從套裝→服務訂閱→工作流程訂閱演化，開發者工具的變遷（大型IDE→輕量IDE+Agent→CLI Agent）與文件成為顯學，正是典範轉移證據。結論：未來軟體公司必須 MCP-first，品質決定服務能否長遠。

### 5, 總結
作者提供 MCP 使用方式：Streamable HTTP，URL 為 https://columns-lab.chicken-house.net/api/mcp/（請保留尾斜線），可在 VSCode（MCP: Add Server→HTTP→URL）或 ChatGPT Plus（Beta）使用；可用 /mcp GetInstruction 強制起手式。測試題例如「安德魯文章中的微服務交易技巧與引用」。心得總結：效率關鍵在 Context Window 管理與流程護欄（先檢索後讀取、強制 learn），Shopify/Context7 的設計印證了 Context Engineering 的極致。作者自此習得 MCP 的設計手感，並看清 API→MCP 的產業路線。下篇將深入內容預處理與合用型態的設計法，說明如何把 MCP 與 Context 管理整合到最佳效益。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本了解 LLM、RAG、向量檢索與 Prompt/Instructions 概念
   - API 設計與 Domain-driven 介面思維（API First 的優缺點）
   - Agent 與 MCP（Model Context Protocol）的角色與結構：Prompts、Tools、Resources
   - 工作流程（Workflow）設計與 Context Engineering（上下文管理）

2. 核心概念：
   - MCP-first 而非 API-first：以工作流程與上下文為核心設計工具
   - 內容服務化＋正規化：先將長文精煉為可用的「合用型態」，再提供檢索
   - Workflow-first 工具介面：以「發現—規劃—執行」分層設計工具，降低 Agent 操作障礙
   - Context 管理與效率：先查片段（chunks）再取全文（full docs），只把必要內容放入 context window
   - 實戰應用閉環：訂閱／解答／解題／學習等場景由 MCP Tools 串起，示範 Q&A、vibe writing、vibe coding

3. 技術依賴：
   - MCP Host（支援 Streamable HTTP）
   - 向量檢索與內容預處理（LLM 精煉、synthesis 標註：origin/solution/faq/summary）
   - 開發環境與 Agent：VSCode + GitHub Copilot、ChatGPT Plus（MCP Beta）、Claude
   - 參考設計：Shopify Dev MCP（conversationId＋tools discipline）、Context7（resolve + get docs）
   - 部落格內容治理：Markdown 化、檔名與連結修復、Repo 重構（AI IDE）

4. 應用場景：
   - 問答對話：把部落格當知識庫，Agent 精準回答並附引用
   - 資料整理（vibe writing）：跨文檔彙整演進史、計畫、講義、考題
   - 程式生成（vibe coding）：依文章解法直接產出骨架與現代化程式碼
   - 學習路徑生成：由文章生成教學計畫與 Handson Labs
   - 開發者工作台：在 VSCode 以 MCP Tools 檢索、取用、引用文章與片段

### 學習路徑建議
1. 入門者路徑：
   - 了解 MCP 與 Agent 的基礎概念、MCP ≠ API 的差異
   - 熟悉「Workflow-first」與「Context + Workflow」設計思維
   - 安裝並試用 MCP Server（HTTP Streamable），體驗 Tools 呼叫與回應
   - 基礎 RAG、向量檢索與「chunks→全文」的操作心法

2. 進階者路徑：
   - 設計自有 MCP Tools（GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts）
   - 內容正規化：用 LLM 將長文轉為可檢索的 synthesis 型態（origin/solution/faq/summary）
   - 引入「發現—規劃—執行」分層與「指令即回應」的工具內嵌指引（仿 Shopify 的 conversation discipline）
   - Context Engineering：控制窗口大小、避免信息爆量、分步取得必要內容

3. 實戰路徑：
   - 在 VSCode + Copilot 實作：以 SearchPosts + GetPostContent + SearchChunks 支援 vibe coding
   - 以 ChatGPT Plus（MCP）進行 Q&A，觀察不同模型的查詢策略與工具連鎖
   - 建構內容處理管線：HTML→Markdown、檔名與連結規範、圖檔工具、Disqus 遷移表
   - 導入測試場景：生成教學計畫、考題、講義，驗證 MCP Tools 的覆蓋度與穩定性

### 關鍵要點清單
- MCP-first 設計：以 Agent 的工作流程為中心設計工具介面，不是把 REST API 直接包成 MCP (優先級: 高)
- Workflow-first 思維：先定義「使用情境→工作流程→所需工具」，再落規格 (優先級: 高)
- Tools 清單與責任：GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts 的分工 (優先級: 高)
- GetInstructions 作為動態指令源：把「使用規則」做成可呼叫的工具，確保指令進入 context (優先級: 高)
- 內容正規化（synthesis）：將長文轉為 origin/solution/faq/summary 等型態以提升檢索精度 (優先級: 高)
- 先查片段再取全文：SearchChunks→Fetch Full（或 GetPostContent）以降低 context 汙染 (優先級: 高)
- Context Engineering：嚴控窗口大小與資訊密度，避免「爆量」造成理解失效 (優先級: 高)
- RAG 的適配：長文不適合直接切塊，需先 LLM 精煉再入庫，提升檢索與應用效果 (優先級: 高)
- Shopify Dev MCP 心法：mandatory discovery tool、conversationId 紀律、工具層級分工 (優先級: 中)
- Context7 心法：resolve library → get docs，回應內嵌使用規則＋信任與覆蓋度提示 (優先級: 中)
- 問題 vs 難題：question（有明確答案）與 problem（需因地制宜解法）分辨，設計不同工具支持 (優先級: 中)
- AI IDE 重構：HTML→Markdown、檔案規範、連結修補、Repo 結構清理，為內容處理管線打底 (優先級: 中)
- Vibe coding 實戰：以文章解法與片段為上下文，生成現代化程式碼（如 channel 替代 BlockingCollection） (優先級: 中)
- MCP Host 與接入：Streamable HTTP、在 VSCode/ChatGPT Plus 安裝與使用流程 (優先級: 低)
- 成本與效益：內容預處理最耗時耗 token，但帶來精準檢索與高效實作（需雲資源與額度） (優先級: 低)

