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
- MCP-first: 以工作流程與上下文為核心重新設計工具介面，讓 Agent 能有效運用部落格資源。
- 內容服務化: 透過 MCP 提供符合 Agent 思考與操作的 tools，而非單純包裝既有 API。
- 內容正規化: 先用 LLM將長文重組為可檢索與可應用的型態（如 FAQ/solution/chunks），提升 RAG 精準度。
- 流程效率化: 借助 AI IDE 重構整個 repo、格式與資產，清理技術債以支撐內容預處理。
- Workflow First: 不以端點導向，而以使用情境與流程拆解來反推應該提供的 MCP 工具。
- 工具設計要訣: 工具須同時傳遞 instructions、結果與防呆機制，減少幻覺並維持上下文精準。
- 實作案例: 問答、演進史整理、vibe coding 三類情境，展現 MCP 對 chat、文件整理與程式生成的增益。
- 標竿學習: Shopify.Dev 與 Context7 展示分層發現/規劃/執行與「為 Agent 設計」的最佳實務。
- SaaS變遷: 從 API-first 過渡到 MCP-first，未來將朝「工作流程訂閱」與 Agent 互動為主。
- 使用方式: 提供 Streamable HTTP MCP Server，支援 VSCode 與 ChatGPT Plus，建議先執行 GetInstructions。

## 全文重點
作者以「讓 Agent 懂我的部落格」為目標，啟動一個 MCP-first 的重構與服務化 side project，核心理念是為 Agent 的工作流程與上下文量身設計工具，而不是把既有 REST API 改裝成 MCP。整體分為三大目標：內容服務化（設計 MCP tools 以支援 Agent 的解題流程）、內容正規化（用 LLM預先精煉長文為適合檢索與應用的結構化片段），以及流程效率化（藉助 AI IDE 重構 repo、清理格式與資產，消除技術債）。

在設計 MCP 時，作者採用 Workflow First 的方法：先分析讀者使用部落格的主要情境（訂閱、解答、解題、學習），再以「真人會怎麼做」的流程來反推所需工具，形成工具集包含 GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts。重點不在規格細節，而在如何讓 Agent 的思考脈絡能被工具支持，並使上下文管理精準且高效。

作者以三個實測案例展示 MCP 的效益：一是 Chat with My Blog 的問答場景，對比 Claude 與 ChatGPT 的查詢與回應風格，說明工具呼叫與查詢策略如何影響結果；二是用 VSCode + Copilot 整理部落格演進史，MCP 讓資料蒐集和交叉引用變得快速、精準且可直接嵌入 markdown；三是 vibe coding，讓 Coding Agent依據文章思路生成可實作的平行處理 CLI 範例，且會自動選用較新的語法與函式庫，展現 MCP 對「把知識變成程式」的助力。

為精進設計，作者研讀並反向分析 Shopify.Dev 與 Context7 的 MCP：Shopify 的洋蔥式分層（發現/規劃/執行）與強制會話 id 的防呆設計，搭配以 markdown 返回 chunks、完整文件與 schema introspection/validation；Context7 以兩個簡潔工具完成「解析庫ID」與「抓取對應版本且主題聚焦的權威文件」，並在回應中直接嵌入使用規則與可信度，讓 Agent 即時做正確選擇。這些範式體現 MCP 是為流程與上下文設計的工具，不同於給人類開發者的 API。

作者進一步提出行業觀察：在 Agent 時代，MCP 會成為新一代的「API」。SaaS 的競爭關鍵從「能否提供 API 供串接」轉為「能否提供高品質 MCP 供 Agent 無縫使用」，軟體服務的訂閱型態可能從工具與服務轉向「工作流程訂閱」。以開發工具為例，生態已從大型 IDE（Visual Studio）走向輕量 IDE + Agent 再到 CLI Agent，反映「由 Agent 主導程式處理」的趨勢與文檔的重要性提升。

最後作者提供 MCP 使用說明（Streamable HTTP URL）與建議操作（VSCode/ChatGPT Plus；先執行 GetInstructions）。並總結：MCP 設計與 Context Management 是相輔相成的兩大必備能力。當前最大瓶頸仍是 context window 尺度，因此工具需嚴控「只將必要資訊進入上下文」。下一篇將專注談內容預處理與合適型態的生成，以完整交代 MCP + Agent 的最大化整合方法。

## 段落重點
### 前言與動機
作者長文習慣完整交代思路與脈絡，但讀者從「理解」到「能用以解題」的門檻仍高。傳統作法（縮短篇幅、只寫步驟、拆成多篇）都無法解痛。作者提出以 MCP-first 將部落格「服務化」，把文章轉為 Agent 可用的工具與素材，讓 AI 的理解能力對接部落格資產，縮短從閱讀到應用的距離。本系列分兩篇：本篇談服務化與 MCP 設計；下篇談內容預處理與發布流程。Side project 已完成並上線，提供公開 MCP Server（Streamable HTTP），讀者可直接用支援的 Host 體驗。此改造也呼應 2016 年「Blogging as Code!」的轉折：當年把系統改為靜態內容；現在則把被動內容變成主動可被 Agent 使用的服務。

### 1, 為什麼要把部落格做成 MCP?
核心目標是讓部落格文章能被 Agent「好好利用」，其中關鍵在精準檢索與優雅整合 Agent。作者將改造拆成三目標：1) 內容服務化：用 MCP 設計合乎流程的工具，重心是 context 與 workflow，而非規格本身；2) 內容正規化：LLM 先將長文重新生成為適合 RAG 的結構與片段，避免長文斷開後的語義不完整，雖耗 token 但成效顯著；3) 流程效率化：用 AI IDE（如 Copilot）重構 repo、統一格式與路徑、轉 HTML 為 Markdown、修復連結與圖檔，清理技術債以支撐後續自動化。作者強調 MCP 不等於 API，若只將 REST 包裝成 MCP是錯誤；真正要針對 Agent 解題的脈絡與流程設計工具界面。此觀念來自觀摩 Anthropic 團隊分享與 Shopify MCP 的實務。

### 2, MCP != API, 從流程的角度設計
作者回顧「API First 到 AI First」的演講要點：API 要合乎常理、可靠無例外；要精準對應領域問題；避免 UI 導向與檯面下溝通習慣。進一步體會「Workflow First」的激進觀點：別用 API 思維設計 MCP，應先從工作流程出發。以使用情境分析讀者需求（訂閱、解答、解題、學習），再以「真人會怎麼做」來拆解流程，將流程中的動作映射到 MCP 的 primitives（Prompts、Tools、Resources）。以「解題」為例，會先理解前輩的使用說明（GetInstructions）、拿線索片段（SearchChunks）、再獲取原始文章與相關文（GetPostContent/GetRelatedPosts）。因此作者的 MCP tools 形成：GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts。此工具集緊貼解題流程，讓 Agent 操作門檻降低、上下文更精準，後續再以實例驗證設計成效。

### 3, 三個實際的案例示範
作者展示三類情境：1) 問答（ChatGPT/Claude）：Agent 以 SearchChunks 等工具檢索部落格片段，對比模型的查詢策略與文字風格，皆能引用正確文章且無顯著幻覺；2) 整理演進史（VSCode+Copilot）：給出排序與格式要求，Agent 以 MCP 快速收集並生成含標題/連結的條目，直接寫回 markdown，效率遠勝人工交叉查找；3) 依文章 vibe coding（VSCode+Copilot）：以「CLI + pipeline + STDIO + jsonl 平行處理」要求，Agent 先用 MCP 檢索文章與 chunks，再生成符合設計要點的 C# 程式，並選用較新語法（如 channel reader/writer），還輔以測試資料與腳本。這些案例顯示：簡短的指令可導出高價值產出，關鍵在 MCP 把過往文章的知識與範例準確嵌入上下文，讓 Agent 能把「文字知識」轉成「可執行解法」。作者並補充其他延伸應用（資源注入、學習計畫與考題生成等）同樣奏效。

### 4, 參考 Shopify / Context7 的 MCP 設計
作者深入分析兩個標竿：Shopify.Dev 與 Context7。Shopify 採「洋蔥式」分層：learn_shopify_api 為必經的「發現層」，強制產出 conversationId 以約束後續工具呼叫並把官方 instructions 放入上下文；search_docs_chunks/fetch_full_docs 提供以 markdown 形式的精準片段與全文，利於 RAG 與 LLM解析；introspect_graphql_schema/validate_graphql_codeblocks 支援 GraphQL 的查詢規劃與最終驗證，形成流程防呆。Context7 則以兩個工具達成：resolve-library-id 與 get-library-docs，回應內直接夾帶使用規則與可信度（trust score），以版本、主題與 token 限額精準拉取權威文件與範例 code。兩者共同體現：MCP 是「為 Agent工作流程」設計的工具，不同於「為人類開發者」設計的 API；工具回應應同時傳遞指引與結果，並有機制約束與優化上下文。作者进一步提出觀點：MCP 將成為 Agent時代的新「API」，SaaS 的戰略從 API-first 移向 MCP-first，甚至走向「工作流程訂閱」。

### MCP 應用的想像 - 下個世代的 API
作者從產業演進談趨勢：過去十年 SaaS 倚賴 API 形成生態與整合，如今 Agent 可自讀規格並自主呼叫工具，整合工程大幅減少，MCP 成為面向 Agent 的新介面。開發工具市場已快速轉向 AI IDE 與 CLI Agent，反映「由 Agent 主導程式處理」的典範轉移與文檔的重要性抬升。未來的核心競爭不再只是提供 API，而是提供高品質 MCP，讓使用者的 Agent 能無縫接入你的服務。作者以多場分享與觀察指出：MCP-first 的浪潮已具備方向與標準化動能，企業需布局以面對工作流程與使用者習慣的改變。

### 5, 總結
作者提供 MCP 使用方式：Streamable HTTP URL（需完整尾斜線）、免登入/免 API Key，VSCode 以「MCP: Add Server」安裝，ChatGPT Plus（beta）亦可用，建議先執行 GetInstructions 以讓 Agent 正確載入說明。測試提示例：詢問微服務交易技巧並要求列出引用文章。最後的心得指出：現階段瓶頸在 context window 尺度，必須以流程與工具設計嚴控「只有必要資訊進入上下文」，這也是極致的 Context Engineering。Shopify 案例展示「先學習再檢索再讀取」的控管手法；作者自己的做法是在內容端進行「結構型重組」（FAQ、solutions、chunks）而非粗暴壓縮，以獲得更精準的 RAG 效果。整體收穫在於看清 MCP 的設計手感與 API→MCP 的產業轉型。下篇將專談內容預處理與發佈流程，補完 MCP 與 Context 管理的雙主軸。

## 資訊整理

### 知識架構圖
1. 前置知識
   - 了解 LLM 基礎（prompt、function calling、RAG/向量檢索、context window）
   - MCP 概念與生態（Model Context Protocol、Streamable HTTP、Host/Server）
   - Workflow 設計思維（以任務流程而非 UI/API 出發）
   - 內容工程（長文切片、LLM 預先精煉/轉型、synthesis 標記）
   - 基礎工程環境（Jekyll/GitHub Pages、VSCode/GitHub Copilot、Repo 重構）
2. 核心概念
   - MCP-first ≠ API 包裝：為 Agent 的工作流程設計工具介面
   - Workflow-first：工具圍繞「發現→規劃→執行」與使用情境設計
   - 內容正規化/預處理：先用 LLM 轉成可用型態（origin/solution/faq/summary），再做 RAG
   - Context Engineering：只把必要資訊放進 context，管控爆量與幻覺
   - Tool 設計最小集：GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts
   關係：Workflow 決定工具設計；正規化內容+精準檢索提升 Agent 應用；Context 管理貫穿全流程
3. 技術依賴
   - MCP Server（Streamable HTTP）與 Host（VSCode/ChatGPT 等）
   - 向量索引與檢索（chunks、synthesis 標籤）
   - LLM 模型與提示工程（工具說明、工作指引）
   - 內容處理流水線（文章轉 Markdown、清理鏈結與圖檔、LLM 批次精煉）
   - 守門/會話模式（如 learn_shopify_api 的 conversationId 類型手法）
4. 應用場景
   - Chat with My Blog：問答檢索、引用來源、跨文整合
   - 知識整理：時序盤點、主題彙整、生成學習計畫與考題
   - Vibe coding：以文生碼，將文章方法學轉為可執行專案骨架
   - IDE 整合：VSCode + Copilot/Agent 端到端工作流
   - SaaS 未來：公開 MCP 作為 Agent 時代的「下一代 API」

### 學習路徑建議
1. 入門者路徑
   - 了解 MCP 與 API 的差異；閱讀 Shopify/Context7 的公開範例
   - 安裝一個 MCP Host（如 VSCode/ChatGPT），接入「安德魯部落格 MCP」
   - 用 GetInstructions→SearchChunks→GetPostContent 的最小閉環做一次 Q&A
   - 嘗試把一篇長文切片並標註 synthesis（summary/faq/solution）
2. 進階者路徑
   - 以「Workflow-first」重繪你的使用情境，反推需要的 tools 規格
   - 建立內容預處理管線：LLM 精煉、標籤化、向量化、相關文關聯
   - 設計「發現/規劃/執行」的分層工具（如 instructions→search→fetch）
   - 加入守門/會話控制（如 mandatory instruction、conversation id）
   - 評估檢索品質與成本（limit/position/length、token 控制、觀測與迭代）
3. 實戰路徑
   - 為你的領域實作 MCP Server（Streamable HTTP），部署與監控
   - 與 VSCode/ChatGPT 整合，複製三個案例：Q&A、知識整理、vibe coding
   - 建立 telemetry 與測試集（命中率、引用正確性、模型對比）
   - 強化可靠性與安全性（邊界條件、錯誤恢復、授權/配額）
   - 推進「MCP-first」對外策略，將服務以工具形態釋出

### 關鍵要點清單
- MCP ≠ API：為 Agent 的工作流程設計工具，不是把 REST 端點改裝 (優先級: 高)
- Workflow-first 設計：以「發現→規劃→執行」驅動 tools 與 prompts (優先級: 高)
- GetInstructions 作為守門：先給使用規則/動態資訊，降低誤用與幻覺 (優先級: 高)
- 最小工具集：SearchChunks/SearchPosts/GetPostContent/GetRelatedPosts 的職責邊界 (優先級: 高)
- 內容正規化/預處理：先 LLM 精煉成可檢索/可應用型態再做 RAG (優先級: 高)
- Synthesis 標籤：origin/solution/faq/summary 等視用途檢索與回填 (優先級: 中)
- Context Engineering：嚴格控管進入 context 的資訊量與階段性引入 (優先級: 高)
- 相關文關聯：GetRelatedPosts 提升跨文脈絡理解與串讀效率 (優先級: 中)
- 「先檢索再取全文」：chunks 命中後按需 fetch full markdown，降低噪音 (優先級: 高)
- 會話/強制步驟模式：仿 Shopify 的 conversationId 與 mandatory-first-step (優先級: 中)
- 工具可讀回應：以 Markdown 傳回結果+使用規則，利於 LLM 理解與後續行動 (優先級: 中)
- IDE/Agent 實戰：VSCode+Copilot 將文章知識落地到程式骨架（vibe coding）(優先級: 中)
- Repo/內容工程：批次轉檔、修連結、結構清理，讓後續檢索與管線穩定 (優先級: 中)
- 成本/效能治理：limit/position/length 與 token 預算、模型選型與監測 (優先級: 中)
- MCP-first 的未來：SaaS 對 Agent 友善的「下一代 API」戰略地位 (優先級: 高)