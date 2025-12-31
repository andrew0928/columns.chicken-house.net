---
layout: synthesis
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計"
synthesis_type: faq
source_post: /2025/09/16/chat-with-my-blog/
redirect_from:
  - /2025/09/16/chat-with-my-blog/faq/
postid: 2025-09-16-chat-with-my-blog
---
# 讓 Agent 懂我的部落格: MCP-first 的服務化設計

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 MCP（Model Context Protocol）？
- A簡: MCP 是為 AI Agent 設計的通訊協定，重點在「提供可用的上下文與工作流程工具」，不是一般對人或對系統的 REST API。
- A詳: MCP 是由 Anthropic 推出的協定，用來讓 AI Agent能以「工具、資源、指令」三種原語與外部服務互動。它優先考慮模型的上下文與工作流程，將指令（instructions）與工具（tools）做「合情合理」的整合，讓 Agent 能正確探索、規劃、執行。與傳統 API 不同，MCP 回應通常更偏向模型易理解的形式（如 markdown），並鼓勵以「Workflow First」思維設計介面，以降低幻覺與錯誤操作，提升任務完成的穩定度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, B-Q1

Q2: 為什麼要把部落格做成 MCP？
- A簡: 讓 Agent可高效率檢索、理解並應用文章內容，直接支援解答、解題、學習與寫作/程式等情境。
- A詳: 文章多且長，人工閱讀到可應用常需跨越多道門檻。透過 MCP-first 將「部落格」服務化為 Agent 可直接使用的工具與素材，讓 Agent能先取得使用說明（GetInstructions），再依情境查片段（SearchChunks）、查文章（SearchPosts）、取原文（GetPostContent）、找相關文（GetRelatedPosts）。配合內容預處理與 RAG，整體流程可以從「看懂」到「能用」大幅縮短，直接用於文件整理、系統設計、撰寫程式與教學測驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q2, C-Q1

Q3: MCP 與 API 有何差異？
- A簡: MCP 以 Agent 為主要使用者，設計焦點在上下文與工作流程；API 多聚焦資料與操作的對外封裝。
- A詳: 傳統 API 側重資料結構與操作接口，由人或系統按文件呼叫；MCP 則將工具、資源、指令封裝成「模型可理解的工作流程」，常使用 markdown 說明規則與意圖，並在回應中嵌入使用指引。MCP 不鼓勵一對一包裝 REST 端點，而是從「使用情境與流程」反推工具集合，讓 Agent 能先發現（discover）、再規劃（plan）、後執行（execute），降低誤用與幻覺，提升結果品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q10, B-Q22

Q4: 什麼是「Workflow First」設計？
- A簡: 先分析使用情境與工作流程，再據此設計 MCP 工具介面，讓 Agent 順著人類思路完成任務。
- A詳: Workflow First 從真實使用過程與決策節點出發：例如解題時，先取得使用說明（GetInstructions），再找線索（SearchChunks），接著取原始文章（GetPostContent）與延伸閱讀（GetRelatedPosts）。工具設計與回應格式貼近此流程，Agent 不需轉換心智模型即可執行；相對於 API-first、UI-first，這種設計減少「檯面下溝通」與「案例偏斜」，提升可靠性與泛化力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q2, A-Q3

Q5: MCP-first 與 API-first 的差異與核心價值是什麼？
- A簡: MCP-first 讓系統從一開始就面向 Agent 使用與上下文管理，API-first 面向人/系統封裝操作。
- A詳: API-first 強調一致、可靠的操作界面；MCP-first 則更重視 Agent 的發現/規劃/執行三層需求，將指令與工具設計為模型可理解的語境格式，強制流程遵循（如必先 learn_shopify_api 取得 conversationId）。MCP-first 能減少幻覺、避免誤用、提升任務成功率，對 Agent 時代的 SaaS 是關鍵競爭力與生態接口。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q11, A-Q3

Q6: 為何工具設計比規格更重要？
- A簡: 流程與上下文正確可大幅降低出錯，工具設計需貼合思路，規格只是落地的結果。
- A詳: MCP 的本質在於「讓 Agent 按人類流程工作」。若只研究規格而忽略 context/workflow，工具容易偏向端點封裝而非任務流程，導致模型理解成本高、誤用增多。先釐清情境與步驟，再回推合適的工具集合與回應格式，才能在有限的 context window 中高效率傳遞必要訊息。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q7, B-Q9

Q7: 什麼是「內容服務化」？
- A簡: 把文章變成 Agent 可直接使用的工具與素材，供檢索、引用、生成、編排等任務。
- A詳: 內容服務化不只是提供文章 API，而是將內容的查找、取得、延伸等過程拆成 MCP 工具：例如 SearchChunks/Posts、GetPostContent、GetRelatedPosts，回應以模型友好的 markdown 附說明與強調。這讓 Agent 能在上下文中即時取得合用資料，直接支持解答、解題、教學與程式生成。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q4, A-Q2

Q8: 什麼是「內容正規化（預處理）」？
- A簡: 先用 LLM 將長文轉成適合 RAG 的結構（如 FAQ、Solution、Summary），提高檢索精度。
- A詳: 長文常含多個主題且敘事連貫，不利於直接分塊後的向量檢索。預處理以 LLM 重新生成合用型態，提煉為 FAQ/Q&A、解法摘要、重點片段等，並標記用途（synthesis: origin/solution/faq/summary），使 SearchChunks/Posts 能精準命中，降低「切碎不可用」問題，提升 Agent 的理解與應用能力。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q3, C-Q10

Q9: 什麼是「流程效率化（AI IDE 重構）」？
- A簡: 用 AI Agent+IDE 整體清理與重構內容/結構，降低技術債，提升後續管線效率。
- A詳: 包含 HTML→Markdown 轉換、批次改檔名（中文→英文）、修正路徑、匯出轉址對照、清理不必要素材、統整本地與 Pages 的驗證環境等。透過 vibe writing/coding 與 Copilot，重構後讓預處理與檢索更穩定，整體內容管線更流暢。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q8, A-Q8

Q10: 「Question」與「Problem」的差異？
- A簡: Question求明確答案；Problem需依情境找到可行解法，沒有唯一正解。
- A詳: 在部落格使用情境中，「解答」針對定義清楚的問題找確定回答；「解題」則是根據需求背景、限制、風險與目標，形成方法與步驟的解決方案。MCP 需支援兩者：SearchChunks/Posts 快速定位答案；GetPostContent/RelatedPosts 提供原文與延伸，支持形成方案。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q4, D-Q2

Q11: 為何 RAG 不適合直接處理長文章？
- A簡: 長文敘事連貫、多主題，切塊後常成片段，檢索命中難以直接用，需預處理提升合用度。
- A詳: 直接對長文進行 chunking，常在向量限制（如 8KB）下失去上下文連貫，命中片段內容孤立，難以生成正確可用回答。先將長文轉為 FAQ、Solutions、Summaries 等合用結構，並標注用途與元資料，再進行向量索引，可大幅提升命中精度與可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q3, C-Q10

Q12: 什麼是「context window 管理」？
- A簡: 控制進入模型上下文的資訊量與品質，僅保留必要內容，避免爆量與焦點漂移。
- A詳: 模型能處理的上下文有限，且量大不一定代表好。MCP 設計上用「先檢索後讀取」策略（如 search_docs_chunks→fetch_full_docs），分層傳遞必需片段，減少不相關或過度冗長資料，讓 Agent 保持正確工作焦點，提升生成品質與效率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q12, D-Q6

Q13: MCP 的三大原語（Primitives）是什麼？
- A簡: Prompts（指令）、Tools（工具）、Resources（資源），協同支援模型行動與上下文。
- A詳: Prompts 提供指令與規則，Tools 封裝可執行的操作（查找、取得、驗證等），Resources 提供可讀取的外部資料（文檔、檔案、URI）。三者共同構建 Agent 的「可行上下文」，並以模型友好的格式傳遞，確保任務在有限 context window 下仍高效可靠。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q22, A-Q6

Q14: 我的 MCP 提供哪些工具？
- A簡: GetInstructions、SearchChunks、SearchPosts、GetPostContent、GetRelatedPosts 五項核心工具。
- A詳: GetInstructions 提供使用說明與工作方式；SearchChunks 依 query+synthesis 找片段；SearchPosts 依條件找文章清單；GetPostContent 取指定文章內容（支援位置/長度）；GetRelatedPosts 提供文章間的相關清單。這些工具構成從發現、定位、取用到延伸的完整工作流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q3, C-Q4

Q15: 為何將「使用說明」做成 Tool（而非僅 description）？
- A簡: 強制 Agent 先取指令，確保流程合規與上下文就位，降低誤用。
- A詳: 參考 Shopify 的 learn_shopify_api 設計，透過工具回應嵌入必讀規則與動態資訊（如會話識別），確保 Agent 在呼叫其他工具前已遵循正確指引。相較僅寫在描述，工具回應更容易被模型納入上下文並執行後續操作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q2, D-Q1

Q16: 為何要讓使用者授權 MCP 給 Agent？
- A簡: MCP 是使用者授予 Agent 的工具與資料存取通道，需明確控制範圍與規則。
- A詳: Agent 是代理行動者，應在使用者授權下存取外部工具與資料。MCP 將授權工具化，明確使用規則與限制，配合 Host 的安全與審計，讓 Agent 在合規、可控的範圍內完成任務，避免濫用或越權。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, D-Q10, B-Q20

Q17: 為何拆解工作流程為工具能提升 Agent 表現？
- A簡: 工具貼近人類思路，模型可直覺操作；降低心智轉換成本與幻覺風險。
- A詳: 將「人類會怎麼做」變成工具序列（先說明→找線索→取原文→延伸），Agent 只需在上下文中逐步執行即可。工具回應包含使用規則與重點標註，避免模型自行猜測，提升精準度、可用性與可靠性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q7, D-Q6

Q18: Shopify Dev MCP 的核心理念是什麼？
- A簡: 分層工具設計：先學規則（發現）、再查文/架構（規劃）、最後驗證/執行。
- A詳: Shopify 提供 learn_shopify_api（必先呼叫，生成 conversationId）、search_docs_chunks（片段檢索）、fetch_full_docs（取全文）、introspect_graphql_schema（查 GraphQL 架構）與 validate_graphql_codeblocks（驗證生成的 GraphQL）。這種洋蔥式分層，強化流程可靠性與上下文品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q11, B-Q13

Q19: Context7 MCP 的定位與價值？
- A簡: 通用開發文件檢索服務，最少工具即能提供最新、版本對應的官方文檔與範例。
- A詳: 僅用 resolve-library-id（定位庫 ID）與 get-library-docs（取主題文檔/範例），直接以 markdown 提供官方內容與代碼片段，避免過時資料與幻覺 API。強調在上下文中送入「可直接用」的準確材料，支援多框架與庫的即時開發輔助。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, B-Q12, C-Q8

Q20: 為何 MCP 被稱為「下個世代的 API」？
- A簡: Agent 時代，整合由 Agent主動完成，介面須面向上下文與流程，MCP 正好對應。
- A詳: 傳統 SaaS 依靠 API 建生態；Agent 時代，AI 能自讀規格並執行工具，串接工程大幅縮減。MCP-first 能讓服務即刻被 Agent 使用並尊重流程規則與上下文邊界，成為新一代生態基礎。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q20, D-Q10

Q21: 使用者習慣如何轉向 Agent 導向？
- A簡: 從大型 IDE→輕量 IDE+Agent→CLI Agent，更多工作交由 Agent 自動完成。
- A詳: 過去強調工具/範本/片段；如今重視「如何讓 Agent 正確工作」。寫好規格與文件（如 Kiro、Spec Kit）成為顯學。這種轉變促使 MCP-first 成為主設計思維，讓內容與工具服務化以支援 Agent。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q20, B-Q25, C-Q9

Q22: Visual Studio、VSCode+Copilot、CLI Agent 的演進意義？
- A簡: 開發重心由手動操作轉向 Agent 驅動，工具逐步輕量化、流程自動化。
- A詳: 大型 IDE 難以匹配 Agent 工作方式；VSCode+Copilot 改善互動與上下文管理；CLI Agent 更貼近自動化工作流與管線。反映出內容與工具需 MCP-first 設計，讓 Agent 能直接使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q21, C-Q6, D-Q10

Q23: 什麼是「vibe coding / vibe writing」？
- A簡: 以「意圖驅動」與「上下文協作」方式讓 Agent 協助寫程式或寫作，強調流暢對話。
- A詳: 使用者以自然語言表達目標與邊界，Agent 透過 MCP 工具檢索與組織內容，再生成代碼或段落。流程依靠準確的上下文管理與分層工具，能快速達成從意圖到可用產物的轉換。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q6, C-Q5, B-Q9

Q24: GetRelatedPosts 的用途是什麼？
- A簡: 擴展閱讀範圍，提供相近主題文章清單，支援深入理解與方案形成。
- A詳: 在解題/學習情境中，僅取原文可能不足，透過 GetRelatedPosts 找到相近核心概念、延伸案例或補充脈絡。搭配 SearchChunks 與 GetPostContent，能快速建立完整上下文，提升生成品質。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q4, D-Q2

Q25: 什麼是「synthesis 模式」？
- A簡: 指內容用途標記（如 origin、solution、faq、summary），供檢索與生成時精準選材。
- A詳: 透過 LLM 預處理將文章轉成多種合用型態：origin（原文片段）、solution（解法）、faq（問答）、summary（重點）。Search 時傳入需要的 synthesis，可降低命中噪音與提升內容可用度，強化 RAG 的精度與適配度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q10, D-Q2

Q26: 為何 Shopify 要先 learn_shopify_api 取得 conversationId？
- A簡: 強制流程先讀指令與上下文，後續工具需帶此 ID 才能執行，避免亂用。
- A詳: learn_shopify_api 回應嵌入必讀規則與 conversationId，要求 Agent 在後續所有工具都附上該 ID，確保上下文一致與流程合規。此設計能顯著降低錯誤與幻覺，提升工具組合的可靠性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q1, B-Q10


### Q&A 類別 B: 技術原理類

Q1: MCP 如何運作？整體技術架構是什麼？
- A簡: MCP 由 Host、Server、Tools、Resources、Prompts 組成，透過模型上下文驅動工具呼叫完成任務。
- A詳: 技術原理說明：Host（如 VSCode、ChatGPT）連線 MCP Server，Agent 先讀 Prompts/Instructions，使用 Tools（如查找、取得、驗證）取得 Resources（文檔、內容、URI）。關鍵流程：發現→規劃→執行，回應格式偏向模型友好（markdown+規則+高亮）。核心組件：Host（連線與授權）、Server（工具實作）、Index（向量索引）、Synthesis（用途標記）、Validator（語法/規則驗證）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q3, B-Q10

Q2: 「我的 MCP」工具如何串成工作流程？
- A簡: 先 GetInstructions，再用 SearchChunks/Posts 迅速定位，最後以 GetPostContent/RelatedPosts豐富上下文。
- A詳: 技術原理說明：以 Workflow First 將解答/解題流程拆成連續操作。關鍵步驟：1) GetInstructions 建立互動規則；2) SearchChunks 依 query+synthesis 命中片段；3) SearchPosts 找文章清單；4) GetPostContent 取原文；5) GetRelatedPosts 擴充上下文。核心組件：向量索引、內容標記（synthesis）、元資料（postid、position、length）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, A-Q4, C-Q4

Q3: SearchChunks 的技術原理是什麼？
- A簡: 以向量索引與用途標記檢索片段，命中精準內容，供上下文生成。
- A詳: 技術原理說明：內容預處理為 chunk，建立向量嵌入索引；查詢時按 query 與 synthesis 過濾與排名。關鍵流程：1) 預切與標注（faq/solution/summary/origin）；2) 嵌入與索引；3) 查詢重排序；4) 回應以markdown附來源與重點。核心組件：Embedding 模型、向量資料庫、Synthesis 標記器、Ranking/Filtering。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q25, C-Q10

Q4: SearchPosts 的原理與用途？
- A簡: 以元資料與語義搜尋取得文章清單，快速定位主題與來源。
- A詳: 技術原理說明：對文章層級建立索引（標題、標籤、年份、主題），結合語義檢索。關鍵流程：1) 文章級 metadata 建檔；2) 查詢匹配與排序；3) 回應清單含 postid、title、link；4) 搭配 GetPostContent 快速取原文。核心組件：Metadata 索引、語義檢索器、清單生成器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q14, C-Q4, D-Q2

Q5: GetPostContent 如何設計與運作？
- A簡: 依 postid 取原文，可指定 position/length/synthesis，控制上下文大小與用途。
- A詳: 技術原理說明：服務端維護文章儲存與片段定位；支援局部取用與用途導向。關鍵流程：1) 驗證 postid；2) 解析位置與長度；3) 輸出對應文字（markdown），附來源標記；4) 支援 synthesis 提取特定型態（如 solution）。核心組件：內容儲存、定位器、切片器、格式化器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q9, C-Q8

Q6: 為何「回應格式」偏向 markdown 而非 JSON？
- A簡: markdown更利模型理解意圖與重點，能嵌入規則與結構，降低誤解。
- A詳: 技術原理說明：Agent 以模型解讀內容，markdown 可高亮標題、清單、警示與代碼塊，便於提取與遵循。關鍵流程：回應嵌入 instructions、重點與引用，模型能即時吸收並採取行動。核心組件：回應模板、序列化器、標註器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q12, A-Q6

Q7: 如何把工作流程映射成 MCP 工具集合？
- A簡: 拆情境為連續步驟，針對每步設計工具與回應，確保上下文接力與規則執行。
- A詳: 技術原理說明：分析「真人會怎麼做」，用 discover→plan→execute 分層法。關鍵流程：1) 盤點角色/目標/信息源；2) 為每步設計工具與回應模板；3) 嵌入規則與防呆；4) 測試並微調。核心組件：流程圖、工具規格、模板庫、測試場景。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q2, C-Q9

Q8: 內容預處理（LLM synthesis）的技術重點？
- A簡: 用 LLM 提煉長文為合用結構（FAQ/solution/summary），並標注用途以利檢索。
- A詳: 技術原理說明：以生成任務將長文轉為不同型態素材，控制字數與資訊密度。關鍵流程：1) 範式化（FAQ/解法/摘要）；2) 標注 synthesis；3) 嵌入與索引；4) 驗收與回溯修正。核心組件：Prompt 範本、模型選型、質檢器、索引器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, A-Q11, C-Q10

Q9: Context window 管理在 MCP 設計的作用？
- A簡: 以「先檢索後讀取」與局部取用，確保只把必要資料送入上下文。
- A詳: 技術原理說明：工具分層與切片參數避免爆量。關鍵流程：1) Search 命中；2) 局部取文（position/length/synthesis）；3) 延伸再取相關；4) 控制總量。核心組件：切片器、窗口管理器、延伸器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q5, D-Q6

Q10: Shopify 的「洋蔥式架構」是如何分層的？
- A簡: 發現層（學規則）、規劃層（查文/架構）、執行層（生成與驗證），層層相依。
- A詳: 技術原理說明：learn_shopify_api→search_docs_chunks/fetch_full_docs→introspect_graphql_schema/validate_graphql_codeblocks。關鍵流程：強制先學規則，後查文/架構，最後執行與驗證。核心組件：Instructions、Docs/Search、GraphQL Schema、Validator。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, B-Q11, B-Q12

Q11: learn_shopify_api 的機制與意義？
- A簡: 生成必需的 conversationId 與規則，其他工具需帶此 ID 才能運作。
- A詳: 技術原理說明：工具回應以 markdown 嵌入強制規則與 ID。關鍵流程：1) 取得規則與 ID；2) 後續工具皆需附 ID；3) 遵循版本與 API 限制。核心組件：ID 生成、規則模板、會話管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q26, D-Q1, B-Q10

Q12: search_docs_chunks / fetch_full_docs 的設計重點？
- A簡: 片段檢索與全文取得分離，內容以 markdown 提供，提升精度與可讀性。
- A詳: 技術原理說明：先以向量檢索片段，再視需要取全文，避免上下文過量。關鍵流程：查片段→過濾→回應重點→取全文補足。核心組件：Chunk 索引、Doc 資源、格式化回應。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, A-Q12, B-Q14

Q13: introspect_graphql_schema / validate_graphql_codeblocks 的作用？
- A簡: 前者提供可用欄位與架構，後者驗證模型產生的 GraphQL 是否合法。
- A詳: 技術原理說明：introspect 回應可用 schema 範圍供生成；validate 對代碼塊檢查語法與版本。關鍵流程：架構獲取→生成→驗證→修正。核心組件：Schema Provider、Validator、版本管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q7, B-Q10

Q14: Context7 的兩工具如何支援最新文檔生成？
- A簡: 先 resolve-library-id 找到庫 ID，再 get-library-docs 取主題文檔與代碼片段。
- A詳: 技術原理說明：最小工具組合，回應含「使用規則」與「可信度分數」。關鍵流程：庫定位→主題提取→代碼塊輸出→上下文注入。核心組件：庫目錄、主題索引、片段供應器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, C-Q8, D-Q10

Q15: 「Chat with my blog」端到端如何運作？
- A簡: Host 連 MCP→GetInstructions→Search→取文→延伸→生成回答，引用來源。
- A詳: 技術原理說明：Agent 在 Host（如 ChatGPT/VSCode）下呼叫 MCP 工具，分層取得必要上下文。關鍵流程：指令→檢索→取原文→延伸→生成；回應含引用與連結。核心組件：Host、MCP 工具、索引、生成模型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q4, A-Q2

Q16: 「vibe writing」如何結合 MCP？
- A簡: 用 Agent 在 VSCode 中請求檢索與編排，直接改寫 Markdown 內容。
- A詳: 技術原理說明：Agent 利用 Search/Fetch 工具組織內容，回應以 markdown 編排，Host 可直接套入文件。關鍵流程：需求→檢索→編排→貼入→校對。核心組件：MCP 工具、Markdown 模板、Host 編輯器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, D-Q4, A-Q23

Q17: 「vibe coding」如何將文章轉程式碼？
- A簡: Agent 以 MCP 檢索文章解法與片段，結合使用者意圖生成程式骨架與測試。
- A詳: 技術原理說明：SearchPosts→GetPostContent（solution）→SearchChunks（技術關鍵），生成代碼與測試資源。關鍵流程：定位文章→抽取解法→生成骨架→補測資源→執行驗證。核心組件：MCP 工具、代碼生成器、測試資源器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q3, A-Q23

Q18: C# CLI JSONL 平行處理的核心原理？
- A簡: STDIN 讀 JSONL，Channel 建生消模型，限定平行度處理並輸出結果。
- A詳: 技術原理說明：使用 System.Threading.Channels 建立有界通道，Producer 逐行讀入 JSONL（ReadFromStdin），Consumer 以固定平行度（Enumerable.Range）處理（ProcessSingleItem），再 OutputResult。關鍵流程：讀入→入隊→並行處理→輸出→等待完成。核心組件：Channel、Async/Task、序列化器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q6, D-Q6, A-Q22

Q19: GPT 與 Claude 在 SearchChunks 的行為差異？
- A簡: Claude一次直線檢索；GPT 可能分兩次查詢調整範圍，思考更迭代。
- A詳: 技術原理說明：不同模型在「思考模式」與「工具使用策略」上差異。關鍵流程：先取指令→發出查詢→迭代調整→生成回答。核心組件：思考擴展（Thinking）、查詢優化、結果整合。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: D-Q4, C-Q4, A-Q15

Q20: 面向 AI 的可靠性與邊界設計要點？
- A簡: 合情合理與滴水不漏，防止亂調用與越權，確保工具與資源安全。
- A詳: 技術原理說明：AI 可能以未預期方式呼叫工具；需加防呆、強制順序、驗證層。關鍵流程：必先指令→ID/版本要求→輸入驗證→輸出校驗；記錄與審計。核心組件：驗證器、安全閥、審計管道。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q1, D-Q10, A-Q6

Q21: 長文 chunk 限制（如 8KB）如何影響設計？
- A簡: 片段容易失上下文，需預處理為合用結構並用局部取用策略。
- A詳: 技術原理說明：限制導致片段孤立與不可用。關鍵流程：預處理標注→命中片段→按位置/長度取用→延伸補上下文。核心組件：切片器、標注器、延伸器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q5, C-Q10

Q22: 為何工具回應常夾帶使用規則（instructions）？
- A簡: 模型可即時閱讀並執行，避免另查文件造成誤用或理解落差。
- A詳: 技術原理說明：回應包含規則、重點與警示，模型納入上下文後可直接據此行動。關鍵流程：嵌入說明→立即執行→回應連貫。核心組件：說明模板、重點高亮、警示標註。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q11, B-Q14

Q23: MCP 的 Resources 在設計上扮演什麼角色？
- A簡: 作為可讀取的外部資料來源，供工具或上下文直接引用。
- A詳: 技術原理說明：Resources 可為檔案、URI、文檔等，常以模型友好格式提供。關鍵流程：資源登錄→工具取用→上下文注入。核心組件：資源管理器、取用器、格式化器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q8, D-Q8

Q24: Streamable HTTP 的 MCP Server 有何特點？
- A簡: 以 HTTP 連線傳遞工具回應，支援 Host（如 VSCode/ChatGPT）直接使用。
- A詳: 技術原理說明：以標準 HTTP 為傳輸層，實作 MCP 工具與回應序列化。關鍵流程：Host 註冊→工具呼叫→回應串流→上下文注入。核心組件：HTTP 服務、MCP 協定層、Host 配置。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, D-Q5

Q25: VSCode 作為 MCP Host 的運作原理？
- A簡: VSCode 透過擴展連 MCP Server，代理工具呼叫與回應注入編輯流程。
- A詳: 技術原理說明：Host 管理 Server 註冊、工具列表、回應展示與編輯器整合。關鍵流程：Add Server→呼叫→回應插入→文件改寫。核心組件：Host 擴展、工具面板、編輯器接口。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q5, D-Q5

Q26: 為何在 MCP 設計中強調「先檢索後讀取」？
- A簡: 控制上下文量與相關性，優先找到精準片段，再補全文，維持焦點。
- A詳: 技術原理說明：以檢索縮小範圍，再依需求選擇取全文或延伸。關鍵流程：命中→抽取→延伸→生成。核心組件：檢索器、抽取器、延伸器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q9, A-Q12


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 VSCode 安裝並使用「我的 MCP」？
- A簡: 以 MCP: Add Server→HTTP→輸入 URL 完成註冊，即可在 Agent 模式使用工具。
- A詳: 具體步驟：1) F1→「MCP: Add Server」；2) 選 HTTP；3) URL: https://columns-lab.chicken-house.net/api/mcp/（末尾斜線不可省略）；4) 命名並確認；5) 啟用 Agent，在聊天中直接使用搜尋與取文。注意：無需登入或 API Key；最佳實踐：先呼叫 GetInstructions。示例命令：/mcp GetInstruction。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q24, D-Q5

Q2: 如何在 ChatGPT Plus（beta）使用 MCP 整合我的 Server？
- A簡: 開啟 MCP beta，加入 Streamable HTTP Server URL，開始在對話中用工具。
- A詳: 步驟：1) 在 ChatGPT 設定中啟用 MCP（beta）；2) 新增 MCP Server，URL 同上；3) 在對話中先 /mcp GetInstruction 或直接提問「安德魯的文章…」；4) 觀察工具呼叫（SearchChunks/Posts 等）。注意：需 Plus 訂閱；目前仍屬測試版。最佳實踐：要求附引用與網址。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, D-Q4, A-Q21

Q3: 如何強制 Agent 先讀使用說明（GetInstructions）？
- A簡: 在對話輸入「/mcp GetInstruction」，讓 Agent 將說明載入上下文。
- A詳: 步驟：1) 在 VSCode/ChatGPT 對話輸入命令；2) 檢視回應中的使用規則與重點；3) 後續要求任務（查文、取文等）。注意：確保指令已被模型納入上下文；若行為異常可重發命令。最佳實踐：在長任務前先執行一次。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, D-Q1, B-Q2

Q4: 如何撰寫查詢以檢索分散式交易相關文章與片段？
- A簡: 使用 SearchChunks/Posts，傳入關鍵詞與 synthesis（如 solution/faq），限制回傳數量。
- A詳: 步驟：1) 明確關鍵詞：Saga、2PC、TCC、Outbox、一致性；2) 呼叫 SearchChunks（query+limit+synthesis）；3) 如需文章清單，用 SearchPosts；4) 用 GetPostContent 取原文重點；5) 要延伸用 GetRelatedPosts。注意：限制回應數避免上下文爆量；要求附引用。最佳實踐：分兩次查詢迭代縮小範圍。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, A-Q10, D-Q2

Q5: 如何用 MCP 整理「部落格演進史」並直接編寫 Markdown？
- A簡: 在 VSCode Agent 對話描述期望格式，請求檢索與編排，讓 Agent改寫文件。
- A詳: 步驟：1) 說明時間序、主項目/子項目、字數與連結格式；2) Agent 用 SearchPosts/Chunks 檢索；3) 生成 Markdown 清單；4) 檔案直接改寫或貼入；5) 人工驗收調整。注意：要求附標題+URL；控制每項字數與一致格式。最佳實踐：先 GetInstructions，再交代格式模板。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q16, A-Q23, D-Q4

Q6: 如何用 MCP+Copilot 實作 C# CLI 的 JSONL 平行處理？
- A簡: 以檢索文章解法，生成程式框架，使用 Channel 建生消並行處理。
- A詳: 步驟：1) 新建 console 專案；2) 要求 Agent 參考「CLI+Pipeline」文章；3) 讓 Agent 生成 Channel/Producer/Consumer 程式；4) 補上處理邏輯（ProcessSingleItem）；5) 執行測試。關鍵程式碼：
```csharp
var channel = Channel.CreateBounded<UserItem>(100);
await foreach (var item in reader.ReadAllAsync())
{
  var processed = await ProcessSingleItem(item, workerId);
  await OutputResult(processed);
}
```
注意：控制平行度與錯誤處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q6, A-Q22

Q7: 如何產生測試 JSONL 與 Shell scripts 驗證 CLI？
- A簡: 請 Agent 生成 JSONL 假資料與基本 shell 指令，串起管線測試。
- A詳: 步驟：1) 要求 10 筆 UserItem JSONL；2) 請 Agent 生成測試腳本，如：
```bash
cat test-data.jsonl | dotnet run -- 2 2>/dev/null | head -n 3
```
3) 調整平行度測試吞吐；4) 檢查 STDERR 錯誤輸出。注意：資料欄位一致性與時間格式；管線要處理大小量資料。最佳實踐：加入 head/tee 快速觀察結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q18, D-Q6, C-Q6

Q8: 如何在程式中以「Search→Get→Related」工作流實作檢索？
- A簡: 先 SearchPosts 定位文章，再 GetPostContent 取重點，最後 GetRelatedPosts擴展上下文。
- A詳: 步驟：1) 程式呼叫 SearchPosts(query,synthesis,limit)；2) 取 postid 以 GetPostContent(postid,...)；3) 若需延伸，再 GetRelatedPosts(postid,limit)；4) 組合上下文生成回答或代碼。示例（偽碼）：
```pseudo
posts = SearchPosts(q,"solution",8)
content = GetPostContent(posts[0].id,"solution")
related = GetRelatedPosts(posts[0].id,5)
```
注意：控制 limit 與 synthesis 精度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q5, A-Q24

Q9: 如何設計一套「自己的 MCP 工具」以 Workflow First？
- A簡: 盤點情境→拆步驟→設計工具與回應→嵌入規則→測試與微調。
- A詳: 步驟：1) 釐清使用情境（解答/解題/學習/開發）；2) 操作步驟拆解；3) 為每步設計工具（discover/plan/execute）與回應模板（markdown+instructions）；4) 嵌入必讀規則與防呆；5) 以真實案例測試迭代。注意：避免 API 對映思維，一切以流程導向。最佳實踐：先做最小工具集，逐步擴展。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q10, D-Q10

Q10: 如何將長文預處理為 FAQ/Solutions 以提升 RAG？
- A簡: 用 LLM 範式化重組內容、標注 synthesis、建立向量索引並質檢。
- A詳: 步驟：1) 設計 Prompt 範本（FAQ/solution/summary）；2) 控字數與結構化標題；3) 標注 synthesis；4) 做嵌入與索引；5) 隨機抽樣質檢與回修。注意：避免過度壓縮失真；保留引用與連結。最佳實踐：對熱門主題優先預處理。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q8, A-Q11, D-Q3


### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到 Agent 忽略 MCP 使用說明（未先讀指令）怎麼辦？
- A簡: 症狀：工具亂用或報錯。解法：強制 /mcp GetInstruction、嵌入必讀規則、驗證流程。
- A詳: 症狀：呼叫工具缺必要參數、流程順序錯亂。原因：未讀使用說明、未將回應納入上下文。解決步驟：1) 在對話先執行 /mcp GetInstruction；2) 檢查回應是否被模型吸收；3) 再執行後續工具。預防：工具回應內嵌必讀規則，採「先學後用」強制門檻（如 Shopify 的 conversationId）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q11, C-Q3

Q2: SearchChunks 命中不準或內容不可用的原因與解法？
- A簡: 病因：長文未預處理、query不精確、synthesis不對。解法：強化預處理與查詢策略。
- A詳: 症狀：命中片段無法直接回答/生成。原因：長文切片失連貫、未標注用途、關鍵詞過寬。解決：1) 先做 LLM 預處理標注（faq/solution/summary）；2) 調整查詢詞與限制；3) 使用 SearchPosts+GetPostContent補上下文。預防：建置合用型資料與定期質檢。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q3, C-Q4

Q3: 長文被切碎導致不可用，如何修復？
- A簡: 先重生成 FAQ/解法摘要，再以局部取用與延伸策略補上下文。
- A詳: 症狀：片段孤立、答案支離。原因：直接 chunking 失主題完整性。解決：1) LLM 重組為 FAQ/solution/summary；2) 建索引標注用途；3) 局部取文（position/length）；4) 用 RelatedPosts 擴展。預防：熱門長文優先預處理與多層索引。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q5, C-Q10

Q4: GPT 與 Claude 回答風格差異造成理解困難怎麼調整？
- A簡: 症狀：一板一眼 vs 潤飾易讀。解法：要求附引用、條列重點、限制風格與篇幅。
- A詳: 症狀：Claude偏直線技術、GPT偏文字優化。原因：模型思考與生成風格不同。解決：1) 指定回應格式（清單/表頭+引用+連結）；2) 限制篇幅與包含重點；3) 要求列出使用的工具呼叫與參數。預防：設定系統提示與對話模板。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, C-Q5, C-Q2

Q5: VSCode 無法連線 MCP Server（HTTP）怎麼辦？
- A簡: 症狀：註冊失敗/工具不出現。解法：確認 URL、末尾斜線、網路與 Host 擴展。
- A詳: 症狀：Add Server 後看不到工具或回應錯誤。原因：URL 錯、末尾斜線遺漏、網路封鎖、Host 未啟用 MCP。解決：1) 檢查 URL：https://columns-lab.chicken-house.net/api/mcp/；2) 確保可連外；3) 更新 VSCode 與 MCP 擴展；4) 重啟 Host。預防：記錄環境設定與版本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q24, A-Q14

Q6: 上下文爆量導致焦點漂移或效能不佳怎麼處理？
- A簡: 症狀：回答離題、生成品質下降。解法：分層檢索、局部取用、限制回傳數。
- A詳: 症狀：長任務中模型變慢或失焦。原因：上下文塞太多不必要內容。解決：1) 用 Search 命中再取局部；2) 控制 limit；3) 用 synthesis 精選用途；4) 逐步延伸而非一次塞滿。預防：設計洋蔥式工具與窗口策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q12, C-Q4

Q7: GraphQL 代碼塊驗證失敗（Shopify）該如何處理？
- A簡: 症狀：工具回報不合法。解法：先 introspect 架構，再修正並 validate 重試。
- A詳: 症狀：validate_graphql_codeblocks 報錯。原因：欄位不存在、版本不符、語法錯。解決：1) 先用 introspect_graphql_schema 取可用欄位；2) 修正查詢；3) 再 validate；4) 依錯誤訊息調整。預防：先 learn_shopify_api 取得規則與版本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, B-Q11, A-Q18

Q8: 文章連結或圖檔路徑壞掉影響檢索怎麼修復？
- A簡: 症狀：引用失效、取文錯誤。解法：AI 重構 Repo、修轉址、清資源。
- A詳: 症狀：檢索命中但取文/資源錯。原因：舊格式、中文檔名、路徑錯亂。解決：1) AI IDE 清理與轉換（HTML→Markdown、中文→英文檔名）；2) 修正路徑與轉址表；3) 清理不必要素材。預防：發文管線檢查與自動驗證。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, C-Q5, B-Q23

Q9: 中文檔名/網址造成檢索與路徑問題怎麼避免？
- A簡: 症狀：連結失效、索引不穩。解法：批次改英文、統一格式與轉址。
- A詳: 症狀：搜尋不一致、引用錯誤。原因：中文編碼與相容性問題。解決：1) 批次改檔名為英文；2) 統一路徑規則；3) 建轉址對照表；4) 更新所有引用。預防：發文規範與預檢工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, D-Q8, C-Q10

Q10: 工具太多導致 Agent 選擇困難怎麼設計？
- A簡: 解法：採洋蔥式分層（發現/規劃/執行）、必讀規則、最小工具集。
- A詳: 症狀：Agent 常挑錯工具或流程亂。原因：工具設計圍繞端點而非流程。解決：1) 發現層強制先學規則；2) 規劃層檢索與架構；3) 執行層生成與驗證；4) 以最小工具集起步。預防：Workflow First 與回應嵌入 instructions。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q10, B-Q7, C-Q9


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 MCP（Model Context Protocol）？
    - A-Q2: 為什麼要把部落格做成 MCP？
    - A-Q3: MCP 與 API 有何差異？
    - A-Q7: 什麼是「內容服務化」？
    - A-Q9: 什麼是「流程效率化（AI IDE 重構）」？
    - A-Q10: 「Question」與「Problem」的差異？
    - A-Q12: 什麼是「context window 管理」？
    - A-Q13: MCP 的三大原語（Primitives）是什麼？
    - A-Q14: 我的 MCP 提供哪些工具？
    - A-Q23: 什麼是「vibe coding / vibe writing」？
    - B-Q15: 「Chat with my blog」端到端如何運作？
    - B-Q24: Streamable HTTP 的 MCP Server 有何特點？
    - B-Q25: VSCode 作為 MCP Host 的運作原理？
    - C-Q1: 如何在 VSCode 安裝並使用「我的 MCP」？
    - C-Q3: 如何強制 Agent 先讀使用說明（GetInstructions）？

- 中級者：建議學習哪 20 題
    - A-Q4: 什麼是「Workflow First」設計？
    - A-Q5: MCP-first 與 API-first 的差異與核心價值是什麼？
    - A-Q6: 為何工具設計比規格更重要？
    - A-Q8: 什麼是「內容正規化（預處理）」？
    - A-Q11: 為何 RAG 不適合直接處理長文章？
    - A-Q12: 什麼是「context window 管理」？
    - A-Q25: 什麼是「synthesis 模式」？
    - A-Q26: 為何 Shopify 要先 learn_shopify_api 取得 conversationId？
    - B-Q1: MCP 如何運作？整體技術架構是什麼？
    - B-Q2: 「我的 MCP」工具如何串成工作流程？
    - B-Q3: SearchChunks 的技術原理是什麼？
    - B-Q5: GetPostContent 如何設計與運作？
    - B-Q9: Context window 管理在 MCP 設計的作用？
    - B-Q10: Shopify 的「洋蔥式架構」是如何分層的？
    - B-Q12: search_docs_chunks / fetch_full_docs 的設計重點？
    - B-Q13: introspect_graphql_schema / validate_graphql_codeblocks 的作用？
    - C-Q4: 如何撰寫查詢以檢索分散式交易相關文章與片段？
    - C-Q5: 如何用 MCP 整理「部落格演進史」並直接編寫 Markdown？
    - D-Q2: SearchChunks 命中不準或內容不可用的原因與解法？
    - D-Q6: 上下文爆量導致焦點漂移或效能不佳怎麼處理？

- 高級者：建議關注哪 15 題
    - A-Q20: 為何 MCP 被稱為「下個世代的 API」？
    - A-Q21: 使用者習慣如何轉向 Agent 導向？
    - A-Q22: Visual Studio、VSCode+Copilot、CLI Agent 的演進意義？
    - B-Q7: 如何把工作流程映射成 MCP 工具集合？
    - B-Q8: 內容預處理（LLM synthesis）的技術重點？
    - B-Q11: learn_shopify_api 的機制與意義？
    - B-Q14: Context7 的兩工具如何支援最新文檔生成？
    - B-Q18: C# CLI JSONL 平行處理的核心原理？
    - C-Q6: 如何用 MCP+Copilot 實作 C# CLI 的 JSONL 平行處理？
    - C-Q8: 如何在程式中以「Search→Get→Related」工作流實作檢索？
    - C-Q9: 如何設計一套「自己的 MCP 工具」以 Workflow First？
    - C-Q10: 如何將長文預處理為 FAQ/Solutions 以提升 RAG？
    - D-Q1: 遇到 Agent 忽略 MCP 使用說明（未先讀指令）怎麼辦？
    - D-Q10: 工具太多導致 Agent 選擇困難怎麼設計？
    - D-Q7: GraphQL 代碼塊驗證失敗（Shopify）該如何處理？