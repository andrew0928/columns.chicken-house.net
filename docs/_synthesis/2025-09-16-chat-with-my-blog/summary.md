---
layout: synthesis
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計"
synthesis_type: summary
source_post: /2025/09/16/chat-with-my-blog/
redirect_from:
  - /2025/09/16/chat-with-my-blog/summary/
---

# 讓 Agent 懂我的部落格: MCP-first 的服務化設計

## 摘要提示
- MCP-first: 以「工作流程優先」設計 MCP tools，讓 Agent 真正能理解並運用部落格內容。
- 三大目標: 內容服務化、內容正規化、流程效率化，分別對應 tools 設計、LLM 預處理與 repo 重構。
- Context Engineering: 以精準檢索與分段讀取策略，控制 context window，避免資訊爆量。
- Tools 設計心法: MCP 不是 API，需貼合 Agent 的思考脈絡與工作流程。
- Synthesis 預處理: 先將長文轉成「合用」結構（FAQ、Solutions 等），再進行 RAG。
- Workflow First: 由使用情境（訂閱、解答、解題、學習）反推出工具需求。
- 實作工具集: GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts。
- 實戰案例: Chat 對話、歷史整理、vibe coding，展現 Agent + MCP 的效率與精準。
- 產業觀察: SaaS 的 API-first 正轉向 MCP-first，Agent 成為主要使用者。
- 標竿學習: Shopify.Dev 與 Context7 以「發現/規劃/執行」分層與嵌入式 instructions 保障準確性。

## 全文重點
作者將長期以深度、脈絡性強的技術文章轉化為可供 Agent 高效運用的資源，提出以 MCP-first 的服務化設計實作「Chat with My Blog」。核心是把部落格重構為 Agent 可使用的工具與素材，透過三大方向推進：一是內容服務化，用 MCP 提供貼合工作流程的 tools；二是內容正規化，先以 LLM 將長文精煉為可檢索與可應用的結構化素材（如 FAQ、Solutions、Origin、Summary 等 synthesis 型態），再進行 RAG；三是流程效率化，利用 AI IDE 清除技術債，重構 repo、轉檔與修復資源，以支援後續自動化處理。

作者強調 MCP 與 API 本質不同：MCP 是為 Agent 的「context + workflow」而設計，tools 必須對齊「真人會怎麼做」的流程，透過工作情境（訂閱、解答、解題、學習）的分析，萃取出 Agent 需要被授權的操作能力，形成 tools 規格。由此導出一組精煉的工具：GetInstructions（說明與動態指引）、SearchChunks（向量檢索片段）、SearchPosts（文章清單）、GetPostContent（文章內容與 synthesis 區塊）、GetRelatedPosts（相關文章）。

文中以三個實作案例展示：在 ChatGPT/Claude 中以問答抓準分散式交易知識並正確回引；在 VS Code + Copilot 中快速整理「部落格演進史」並直接編修 markdown；以「vibe coding」把文章內方法論轉化為可執行程式碼（如 STDIN JSONL 平行處理），且產生測試數據與腳本，證明 MCP + Agent 能把「知識 → 解法 → 代碼」打通。

在標竿學習部分，作者深入剖析 Shopify.Dev MCP 與 Context7 的工具設計。Shopify 以「learn_shopify_api」強制對話初始化取得 conversationId 並注入 instructions，結合 search_docs_chunks/fetch_full_docs 的先檢索後讀取，以及 GraphQL 的 introspect/validate 雙保險，完整落實「發現-規劃-執行」分層與品質門檻。Context7 則以兩個極簡工具（resolve-library-id、get-library-docs）配上回應中內嵌 instructions 與權重資訊（trust score），讓 Agent 自主選源、取例、組裝解法。

作者進一步提出產業觀察：當 Agent 成為主要使用者，MCP 將成為下一代 API。SaaS 從「服務訂閱」邁向「工作流程訂閱」，工具生態將圍繞 MCP 發展。開發者工作型態亦正由大型 IDE → 輕量 IDE + Agent → 純 CLI Agent 遷移，文件與規格的價值躍升。結尾提供公開 MCP 伺服器（Streamable HTTP）與使用指引，並總結 Context Engineering 的核心觀念：以嚴謹的檢索與分段讀取策略，確保只將必要資訊帶入 context；以內容預處理提升 RAG 精度；以 workflow-first 的 tools 設計，讓 Agent 穩定重現人類專家流程。下一篇將詳述內容預處理與發佈流水線。

## 段落重點
### 1, 為什麼要把部落格做成 MCP?
作者期望讓部落格內容被 Agent 有效理解與應用，縮短讀者「看懂到能用」的距離。將改造目標分為三項：內容服務化（用 MCP 對齊 workflow 設計 tools）、內容正規化（LLM 預先生成適合 RAG 的結構化素材，解決長文切片無效問題）、流程效率化（用 AI IDE 清理技術債與重構 repo）。關鍵發現是：MCP 設計重點不在規格本身，而在於 context 與 workflow 的設計，tools 好壞直影 Agent 表現。預處理方面以 synthesis 型態（FAQ、solution 等）提升檢索精確度；流程上大規模處理 HTML → Markdown、檔名規範、資源路徑修復等，以確保後續自動化順暢。

### 2, MCP != API, 從流程的角度設計
作者回顧「API First → AI First」的觀念轉移：API 必須合情合理、可被 AI 可靠使用；且需精準對應領域問題，而非 UI 導向與檯面下溝通。進一步體會到 MCP 並非 API 包裝，而是「Workflow First」的設計：先界定 Agent 在特定任務中的操作步驟，再反推出應授權的工具。作者給出本專案 tools 清單（GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts），並指出資源也有支援但暫不展開，強調設計過程受 Shopify 與 Anthropic MCP 心法啟發。

### 參考1: 從 API First 到 AI First
摘錄作者過往演講觀點：API 設計需符合「常理」與「可靠」兩基礎，避免 UI 偏斜與檯面下默契；面對 AI 呼叫不可預測，唯有讓介面對應領域本質、或做到邏輯無懈可擊。作者反思當時是用「排除壞習慣」方式接近目標，如今回望其實已在靠攏「context + workflow」設計。於是提出更直接的主張：「別用 API 角度設計 MCP，要從工作流程來設計」，讓工具自然服務於任務脈絡。

### 參考2: iHower 電子報 #31
引用 iHower 整理的資源與 Block Playbook：未來是「人 × Agent」協作，MCP 是使用者授權給 Agent 的工具集。重點在於授權步驟與工具對齊流程，以減少 prompt 轉換與幻覺。Block 的「發現/規劃/執行」分層有助於在多工具環境下規模化；同時強調從工具思維轉向 Agent 思維：為「會問什麼」設計工具介面，而非把 API 生硬映射到 MCP。

### 參考 3: Workflow First, 使用情境分析
從四大使用情境拆解需求：訂閱、解答、解題、學習。以「解題」為例，模擬向前輩請益的流程：先取得使用說明（GetInstructions）、再請前輩給線索（SearchChunks）、取得原文與延伸（GetPostContent、GetRelatedPosts）。將這些步驟轉為 MCP tools，即是將「真人流程」授權給 Agent 操作。並展示最終採用的 tools 規格與參數（含 synthesis 與限制），強調工具對齊流程能降低 Agent 操作成本與失敗率。

### 3, 三個實際的案例示範
展示三類任務：1) 問答對話以分散式交易為題，比較 Claude 與 ChatGPT 在查詢策略與文字風格的差異，兩者皆可正確回引；2) 在 VS Code + Copilot 以 MCP 整理「部落格演進史」，一分鐘生成可用的時間序清單與連結；3) vibe coding：以「CLI + Pipeline」文章為知識源，自動產出 C# 平行處理 JSONL 的骨架碼、測試資料與腳本，展現從文章到代碼的快速落地。三例共同顯示 MCP 將「知識 → 操作 → 交付」打通。

### 案例 1, 直接對話的應用 (ChatGPT)
以同一問題測試 ChatGPT（GPT-5 + Thinking）與 Claude Sonnet 4：Claude流程直線（GetInstructions→SearchChunks→生成），ChatGPT採兩段檢索微調查詢。兩者皆正確引用文章與連結，差異在語氣與組織。作者公開 ChatGPT 對話連結供參。此例展示 tools 資訊如何進入 context 並有效引導答案生成。

### 案例 2, 整理我的部落格演進史
在 VS Code 的 agent mode 直接下指令生成時間序的系統遷移紀錄，含要點摘要與參考連結（2008 起：BlogEngine.NET、客製化與擴充、WordPress 嘗試、2016 Jekyll + GitHub Pages）。效果與正確性高，遠勝以往手工蒐整。作者強調雖不以 AI 代筆整文，但讓 AI 處理資料搜整、交叉引用與編修是自然且高效的應用。

### 案例 3, 拿文章來 vibe coding
以「後端工程師必備: CLI + PIPELINE 開發技巧」為源，在空白 console app 中請 Agent 生成以 STDIN 消費 JSONL、限制平行度的處理骨架，並自動給出 Channel 實作、測試資料與 shell 腳本。與作者 2019 年寫法相比，AI 生成版本採用較新語法/庫（Channel 取代 BlockingCollection），同時滿足架構設計意圖與現代風格；顯示「文章知識 + MCP 檢索 + LLM 程式設計」能快速產出可跑的解法。

### 案例小結
除展示的三例外，作者也試過直接以 resource 讀文章、加 context 附件、從部落格生成學習計劃、測驗題、Hands-on Labs 講義等，效果皆佳。結論是：當工具設計貼合流程與內容結構優化後，Agent 可以高效重現作者當年寫作時的核心洞見與方法論。

### 4, 參考 Shopify / Context7 的 MCP 設計
兩個標竿案例凸顯 MCP 設計要點。Shopify.Dev 以「learn_shopify_api」作為強制第一步，嵌入 conversationId 與 instructions 以維持對話狀態與規範遵循；以 search_docs_chunks/fetch_full_docs 實作「先檢索、後讀取」，且統一傳回 Markdown 降噪；GraphQL 提供 introspect 與 validate 雙工具，確保產出的代碼可用。Context7 以兩個工具實現端到端：解析庫 ID 與抓取對應主題的最新文件與範例，回應中同時夾帶使用規則與信任分數，讓 Agent 自主選擇最佳來源，兼顧精準度與可操作性。

### MCP 設計參考 1: Shopify.Dev MCP
工具包含 learn_shopify_api、search_docs_chunks、fetch_full_docs、introspect_graphql_schema、validate_graphql_codeblocks。learn_shopify_api 強制產生 conversationId 並注入使用規則，未攜帶即拒絕後續工具呼叫，等於建立「發現層」與「會前準備」。檢索工具回傳 Markdown 片段以降低雜訊，full docs 在需要時再取；GraphQL 以 introspect 產生正確 schema 片段、validate 驗證生成 code blocks，形成規劃與執行的閉環，最大化正確率與安全性。

### MCP 設計參考 2: Context7
兩工具極簡：resolve-library-id 與 get-library-docs。前者回覆包含 Library ID、描述、代碼片段數與 trust score，且在回覆中內嵌明確 instructions，引導 Agent 正確選擇；後者按主題與 token 限額回傳對應文件與可複製的範例代碼。設計理念是「把真人查文件→選例子→拼解法」流程內化到 MCP，並用嵌入式說明與加權資訊輔助 Agent 自主決策。

### MCP 應用的想像 - 下個世代的 API
作者判斷 MCP 將成為 Agent 時代的 API：SaaS 從「有 API 供人串接」轉為「有 MCP 供 Agent 即插即用」。開發工具也顯示典範轉移：由大型 IDE 向輕量 IDE + Agent，再到 CLI Agent；文件/規格被重新重視，像 AWS Kiro、GitHub Spec Kit 等工具崛起。當使用者與服務的互動轉由 Agent 主導，MCP 品質將成為服務競爭力關鍵，未來可能走向「工作流程訂閱」型態。

### 5, 總結
作者公開 MCP 伺服器（Streamable HTTP：https://columns-lab.chicken-house.net/api/mcp/，URL 結尾須含 /，免登入與 API Key），並建議在 VS Code 以「MCP: Add Server…」加入；必要時可用「/mcp GetInstruction」強制載入說明。示範查詢範例與使用提示後，作者總結本專案的核心收穫：Agent 的瓶頸在 context window，MCP 設計須以「精準檢索→選讀必要片段」控量；Shopify 的流程控管與 Context7 的嵌入說明，皆是優良實踐。下一篇將深入內容預處理與發佈流程，說明如何把文章轉成適合 RAG 的 synthesis 結構，以達到極致的 Context Management。

### 我的 MCP 使用說明
提供使用通道：Streamable HTTP，URL 為 https://columns-lab.chicken-house.net/api/mcp/（需保留結尾 /）。VS Code 以 MCP: Add Server 加入即可；ChatGPT Plus 亦可（MCP Beta）。可先執行 /mcp GetInstruction 導入說明。示例提問：請列出安德魯文章中處理微服務交易的重要技巧，並附上引用標題與連結，驗證 tools 的檢索與回引能力。

### Side Project 的觀察與心得
MCP 的價值在於「Context Engineering」：以流程化工具組合，確保只把必要資訊帶進 context；以「先檢索後取全文」與 synthesis 化內容結構提升精準度與可用性。作者在這次實作中建立 MCP 設計手感，也看見產業由 API-first 轉向 MCP-first 的趨勢。內容面，將長文轉為 FAQ、Solutions 等應用型結構比單純壓縮更有效；流程面，清理技術債與自動化 pipeline 是規模推進的基礎。下一篇將完整揭露內容預處理方法與實作細節。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 理解 MCP（Model Context Protocol）的基本概念與與 API 的差異
   - LLM 的 context window、RAG、向量檢索與內容分塊（chunks）概念
   - Workflow-first 思維：以任務流程與語境設計工具，而非以端點/畫面為中心
   - 基礎開發實務：GitHub Pages/Jekyll、Markdown、CLI/IDE 與 Coding Agent（如 VSCode + Copilot）
   - 基本安全與可靠性思維：介面邊界、錯誤處理、可靠呼叫與指令遵循

2. 核心概念及關係：
   - MCP-first 服務化：以 Agent 為主要使用者，提供「工具」而非僅是 API
   - Workflow-first 設計：先還原使用情境與工作流程，再反推必要 tools、prompts、resources
   - 內容正規化與預處理：用 LLM 將長文精煉為適合檢索/應用的結構（如 FAQ/solutions/summary）
   - 精準 Context 管理：先檢索後取用，控制進入 context 的資訊總量與必要性
   - 工具分層與指令引導：發現/規劃/執行分層、強制指令（如 conversationId）確保正確流程

3. 技術依賴：
   - MCP Host（支援 Streamable HTTP）與 MCP Server（工具/資源/提示）
   - 向量檢索與 RAG 管線（chunks、post meta、synthesis 型態）
   - LLM 模型（Claude/ChatGPT/本地/雲端）與 Prompt 設計
   - IDE/Agent 整合（VSCode + Copilot、CLI Agents、ChatGPT MCP Beta）
   - 部落格內容資產與發佈管線（Jekyll/GitHub Pages、Markdown、Repo 重構）

4. 應用場景：
   - 問答式檢索（Chat with My Blog）：將部落格作為精準知識庫供 Agent 回答
   - 情境解題：從問題到方案的工作流程導向檢索與串接（chunks → posts → related）
   - Vibe coding/vibe writing：以文章方案直接驅動代碼骨架與文檔整理
   - 開發文件/API 助理：如 Shopify/Context7 的設計，為開發者提供即時、版本化、可驗證的資源
   - 學習路徑生成：從部落格知識生成學習計畫、測驗與 hands-on 指南

### 學習路徑建議
1. 入門者路徑：
   - 了解 MCP 與 API 的差異、三大原語（Prompts/Tools/Resources）
   - 練習 Workflow-first：用一個具體情境列出步驟→映射為 tools
   - 安裝並試用現成 MCP（如本篇提供 URL），觀察 Agent 的 tool calls 與結果
   - 以簡單檢索任務驗證：SearchChunks → SearchPosts → GetPostContent

2. 進階者路徑：
   - 設計符合流程的 tools 介面與嚴格指令（例如「必須先 GetInstructions」）
   - 建置內容預處理管線：LLM 精煉為 synthesis（origin/solution/faq/summary）
   - 向量索引與 chunk 策略：控制長文分片、meta、position/length 查取
   - 整合 IDE/Agent：在 VSCode + Copilot 中以 MCP 資源驅動 coding 任務
   - 導入分層工具策略（發現/規劃/執行），並加入驗證工具（如 GraphQL 校驗）

3. 實戰路徑：
   - 實作一個 MCP Server：至少包含 GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts
   - 建置內容管線：HTML→Markdown、檔名正規化、圖檔與連結修復、RAG 索引
   - 端到端測試：用 ChatGPT/Claude/VSCode 驅動三類任務（問答/整理/寫碼）
   - 量測與調優：context token 使用、檢索精度、回覆正確性、工具使用路徑
   - 安全與可靠性：強制流程令牌（conversationId）、邊界檢查、錯誤防護

### 關鍵要點清單
- MCP-first 思維：以 Agent 為主要使用者設計工具與流程，而非把 REST 端點搬運過來 (優先級: 高)
- Workflow-first 設計：先定義使用者/Agent的實際工作流程，再反推 tools 規格 (優先級: 高)
- GetInstructions 作為必經步驟：用工具返回動態指令與會話令牌，強制正確流程 (優先級: 高)
- 工具分層（發現/規劃/執行）：降低「太多工具」的選擇困難，提高路徑可控性 (優先級: 中)
- 內容預處理/正規化：將長文精煉為可檢索、可應用的結構（FAQ/solution/summary） (優先級: 高)
- 精準 Context 管理：先檢索（chunks）再取全文，嚴控進入 context 的資訊量 (優先級: 高)
- 向量檢索與 RAG 策略：為長文設定 chunk、meta、synthesis 提升命中與可用性 (優先級: 高)
- 工具介面貼近語境：參數命名與回傳格式偏向 Agent可讀（Markdown + 指令），而非僅 JSON (優先級: 中)
- 驗證工具（如 GraphQL 校驗）：在產生程式碼/查詢後加入機器可驗證的防護 (優先級: 中)
- IDE/Agent 整合：在 VSCode/Copilot 中以 MCP 餵入知識，直接驅動 coding (優先級: 中)
- 技術債清理與資料管線：HTML→Markdown、檔名/連結正規化，確保檢索與維運效率 (優先級: 中)
- 案例導向驗證：問答、部落格史整理、vibe coding 三類場景端到端測試 (優先級: 中)
- API vs MCP 差異：MCP 是為「工作流程工具」與「Agent語境」設計，不同於端點交換 (優先級: 高)
- 安全與可靠性：即使被「胡亂呼叫」也守邊界，流程令牌與規則放入工具回覆 (優先級: 中)
- 未來趨勢：MCP 將成為 Agent 時代的「下個世代 API」，SaaS 需要 MCP 品質作為護城河 (優先級: 中)