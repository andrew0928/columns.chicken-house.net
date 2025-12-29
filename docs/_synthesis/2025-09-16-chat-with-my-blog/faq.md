---
layout: synthesis
title: "讓 Agent 懂我的部落格: MCP-first 的服務化設計 - faq"
synthesis_type: faq
source_post: /2025/09/16/chat-with-my-blog/
redirect_from:
  - /2025/09/16/chat-with-my-blog/faq/
---

# 讓 Agent 懂我的部落格: MCP-first 的服務化設計 FAQ

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 MCP（Model Context Protocol）？
- A簡: MCP 是為 Agent 設計的工具協定，重在提供可操作的上下文與工具，非傳統 API。
- A詳: MCP 是一種「面向 Agent 的服務協定」，核心在於讓模型可以取得、管理並運用任務所需的上下文（context），藉由 Tools、Prompts、Resources三類原語提供工作流程中的「可執行能力」。它不是把 REST API包一層，而是用「Workflow First」方式設計工具介面，幫助 Agent按真實工作脈絡高效完成任務，避免 UI導向與人類暗默溝通的依賴。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, B-Q1

Q2: 什麼是「MCP-first」的設計思維？
- A簡: 以 Agent 為主要使用者，從工作流程出發設計工具與上下文，優先於傳統 API。
- A詳: MCP-first 是把系統的主要「外部介面」定位為 Agent 的工具集，而非人類或既有應用的 API。它要求先理解使用者與 Agent如何完成任務的流程，再設計最貼近該流程的 Tools與指引（instructions），確保上下文可控、步驟可執行、回應可理解。對應演進路徑：API-first → AI-first → MCP-first，反映未來使用者將與 Agent高頻互動。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q4, B-Q16

Q3: 為什麼「MCP ≠ API」？
- A簡: API面向應用程式；MCP面向Agent與工作流程，回應更傾向可理解的指引與片段。
- A詳: API 強調結構化資料與端點的契約；MCP 強調「執行任務的上下文與工具」。MCP 回應常用 Markdown與 instructions，夾帶使用規則與下一步指引；工具介面也分層（發現/規劃/執行），避免一次曝露過多端點。把 REST API直接包成 MCP會忽略 workflow 與語境管控，導致 Agent選擇困難、幻覺或誤用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q11, B-Q13

Q4: 什麼是「Workflow First」設計？
- A簡: 先拆解真實任務流程，再設計貼合步驟的工具與上下文管理。
- A詳: Workflow First 是把實際使用情境逐步分析（如解答、解題、學習），抽出行動（如取得說明、檢索片段、讀全文、找相關），再映射為 MCP Tools（GetInstructions、SearchChunks、GetPostContent、GetRelatedPosts）。目的是讓 Agent 不需轉換邏輯即可執行，降低認知負擔，提高成果穩定性與準確性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q10

Q5: MCP 的三大原語（Primitives）是什麼？
- A簡: Prompts、Tools、Resources；分別提供指引、可操作能力與原始素材。
- A詳: MCP 以三類原語服務 Agent：Prompts（使用說明與指引，讓模型理解工具用法與目的）、Tools（可調用的動作，如檢索片段、抓全文、查相關）、Resources（原始內容或連結，如文章 Markdown）。三者協同管理上下文，避免將不必要資訊灌入，做到「先檢索後讀取」以控管 context window。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, B-Q13, B-Q20

Q6: 為何要把部落格服務化成 MCP？
- A簡: 讓 Agent 能精準檢索、理解與重用文章知識，直接用於解答、解題與寫程式。
- A詳: 長文敘事不利直接 RAG。將部落格以 MCP 工具化，提供說明（GetInstructions）、片段檢索（SearchChunks）、全文（GetPostContent）、相關（GetRelatedPosts），並配合內容正規化（synthesis）與上下文管理。結果是 Agent 能把文章變為可操作的素材，提升文件撰寫、系統設計、程式碼生成的效率與品質。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q7, C-Q1

Q7: 「內容服務化、正規化、流程效率化」三者差異？
- A簡: 服務化供工具與介面；正規化重塑內容；效率化清理流程與技術債。
- A詳: 服務化是發布 MCP與設計 Tools，讓 Agent可用；正規化是用 LLM預先生成 FAQ/solutions/chunks 等合用型態，提升檢索精度；效率化是重構 repo、修舊文與路徑、標準化格式，確保 pipeline順暢。三者相互支撐：工具須有好內容，內容須有好流程。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, B-Q7, D-Q7

Q8: 什麼是內容正規化（synthesis）？為何不用「只靠 RAG」？
- A簡: 將長文重塑為可用片段與結構型態，提升檢索與應用效果。
- A詳: 長文含故事與推理脈絡，切片後難以完整應用。synthesis 先用 LLM將內容精煉成 FAQ、解法摘要、重點片段等結構，然後再做向量索引與 RAG。這能提高「查到即用」的精準度，降低幻覺與語境偏離，特別適合架構師觀點的深度文章。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, D-Q5

Q9: RAG 在長篇敘事文章上的限制是什麼？
- A簡: 切片易破壞主題完整性與推理脈絡，難以直接用於解題。
- A詳: RAG 依賴 chunking 與向量檢索。長文通常跨情境與推理步驟，8KB左右的片段不一定包含完整觀念與可用流程，檢索出來難以直接用於解題。需先做 synthesis，重構內容為可用單元（FAQ、solutions、code blocks），再 RAG，以維持語境與可操作性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q8, B-Q10

Q10: 什麼是「Context Engineering」？核心價值是什麼？
- A簡: 精準管理上下文，確保只把必要資訊放進模型的思考窗。
- A詳: Context Engineering 是以工程方法管理模型的上下文：控制資訊量、排序重要度、分層檢索、延遲讀取。目標是避免 context window爆量與離題，維持高效推理與可控結果。實務上透過「先檢索後讀取」、分層工具設計、synthesis、Markdown格式回應等策略落地。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q13, D-Q4

Q11: MCP Tools 如何對齊 Agent 的思考流程？
- A簡: 以「了解→檢索→讀全文→找相關」步驟設計工具與回應。
- A詳: 先 GetInstructions 讓 Agent知道使用規則與任務風格；用 SearchChunks 快速找到可能有用的片段；用 GetPostContent 讀取需要的完整內容；用 GetRelatedPosts 擴展相近主題。工具回應含指引與結構化片段，讓 Agent能無縫推理與組裝解答或程式碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q10, C-Q3

Q12: GetInstructions 是什麼？有何作用？
- A簡: 提供使用規則與任務風格的動態說明，引導後續工具正確使用。
- A詳: GetInstructions 是「發現層」工具，返回Markdown形式的操作指引、邊界與範例，讓 Agent 知道應如何觸發與串聯其他工具。類似 Shopify 的 learn_shopify_api，甚至可返回會話標識（如 conversationId）以強制先完成初始化，提升可靠性與一致性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, B-Q12, C-Q6

Q13: SearchChunks 與 SearchPosts 有何差異？
- A簡: Chunks找片段線索；Posts找文章清單。前者快線索，後者拓展範圍。
- A詳: SearchChunks 傾向向量檢索小片段，快速提供「可引用」的重點或摘要；SearchPosts則返回符合主題的文章列表，用於下一步全文讀取或拓展探索。兩者搭配能做到先縮窄再擴展，避免一次讀太多無用內容。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q4, B-Q10

Q14: GetPostContent 與 GetRelatedPosts 的用途？
- A簡: 前者抓指定全文與片段；後者提供相關主題延伸閱讀。
- A詳: GetPostContent 以 postid、synthesis、position、length等參數精準取得文章全文或重點片段；GetRelatedPosts基於元資料、嵌入或連結關係返回相關文章列表，供 Agent拓展脈絡或交叉驗證。兩者把「讀全文」與「找相關」明確化。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, B-Q6, C-Q9

Q15: 為什麼用 Markdown 回應比 HTML 更適合 LLM？
- A簡: Markdown資訊密度高、雜訊少、結構清晰，模型更易理解與抽取。
- A詳: HTML包含大量展示用標籤與樣式，對模型形成噪音。Markdown能用標題、清單、程式碼區塊清晰分界，方便模型抽取、分段與引用。Shopify、Context7均以 Markdown回應以提高檢索後的「可用性」與準確性，減少幻覺與解析成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q13, B-Q10, C-Q9

Q16: 「發現/規劃/執行」三層設計是什麼？
- A簡: 先知可用工具，再規劃參數與步驟，最後執行具體操作。
- A詳: 參考 Block 的「洋蔥式架構」：發現層工具返回指引或可用資源（如 learn_shopify_api）；規劃層工具幫助選擇與配置（如 chunks檢索、schema説明）；執行層工具完成最終動作（如抓全文、驗證GraphQL）。分層避免Agent一次面對過多選項，降低誤用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q14, C-Q6

Q17: Shopify.Dev MCP 的設計精髓是什麼？
- A簡: 強制初始化、分層工具、Markdown回應、GraphQL驗證閉環。
- A詳: Shopify 用 learn_shopify_api 強制先取得conversationId；search_docs_chunks與fetch_full_docs落實「先檢索後讀取」；introspect_graphql_schema與validate_graphql_codeblocks形成「生成→驗證」閉環，確保產出可用。所有回應採Markdown，夾帶操作指引以減少模型誤解。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q14, D-Q2

Q18: Context7 MCP 的定位與價值？
- A簡: 提供最新、版本精準的官方文件與範例，直接進入上下文。
- A詳: Context7 以兩個工具（resolve-library-id、get-library-docs）服務開發者：先解析庫ID，再抓主題文件與可用程式碼。回應同時包含使用規則與信任分數（trust score），減少過時或幻覺 API。目標是「不換分頁、不過時、不憑空」，把正確素材送進模型。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q15, B-Q13, C-Q10

Q19: 什麼是 conversationId？為何重要？
- A簡: 會話識別碼，保證工具在同一脈絡下協同與授權。
- A詳: 以 Shopify為例，learn_shopify_api 返回 conversationId，後續工具必須攜帶它。此舉一方面強制初始化指引進入上下文，另一方面維持狀態一致與安全邊界，避免亂用工具或跨脈絡污染。也是「流程管控」的實務手段。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, D-Q2, C-Q6

Q20: MCP 如何支援「解答/解題/學習」三種情境？
- A簡: 以片段檢索、全文閱讀、相關延伸與指引串起完整工作流程。
- A詳: 解答偏向快速片段（SearchChunks）；解題需組合多文、建立方案（SearchPosts+GetPostContent+GetRelatedPosts）；學習需引導路徑與練習（GetInstructions+Resources）。以工具映射步驟，讓 Agent 像前輩導師，給線索、連文、組解、產碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, C-Q3, C-Q4

Q21: 什麼是 AI IDE 與 Vibe Coding？
- A簡: 以 VSCode+Copilot等 Agent 互動寫程式，靠對話驅動開發。
- A詳: AI IDE 指整合 Agent 的編程環境（VSCode+Copilot、Cursor等），Vibe Coding 是以自然指令與上下文素材引導 Agent 生成與修正程式碼。配合 MCP，Agent 可先檢索文章精華與範例，再產碼並迭代，顯著提升開發效率與品質。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q5, B-Q22, D-Q9

Q22: 什麼是 JSONL 與 CLI Pipeline 的概念？
- A簡: JSONL是行為單位的JSON；CLI Pipeline以標準輸入輸出串接處理。
- A詳: JSONL 以每行一筆JSON，適合串流與批次；CLI Pipeline透過 stdin/stdout 串接處理，方便並行。文中以 .NET 的 Channel+Task 實作平行處理，Agent 依 MCP文章內容生成程式框架，快速搭建可測試的管線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, C-Q5, D-Q3

Q23: 為何要做 LLM 預先生成（synthesis）？
- A簡: 提前把內容重塑成可檢索、可組裝與可引用的精華單元。
- A詳: synthesis 讓長文轉為 FAQ、Solutions、摘要與片段，提升向量索引精度與回應質量。成本在 token與工程，但可換回更穩定的「查到可用」與更低的幻覺率，特別適合架構思考與案例型文章。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q7, D-Q5

Q24: MCP 與 SaaS 的未來關係為何？
- A簡: MCP 將成為 Agent 時代的「新 API」，驅動生態整合與工作流程訂閱。
- A詳: SaaS 過去靠 API 生態整合；Agent 時代，MCP 讓模型可直接理解工具與指引、自己呼叫執行。未來重點不在「有無 API」，而在「MCP 品質」。服務將以「可被 Agent無縫使用」為價值，生態改以工作流程為中心。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, A-Q25, B-Q19

Q25: 什麼是「工作流程訂閱」？
- A簡: 訂閱可被 Agent 直接執行的流程能力，而非僅軟體功能。
- A詳: 從「套裝軟體」到「服務訂閱」再到「工作流程訂閱」，使用者將訂閱能賦能其 Agent 的流程工具。MCP-first 提供可用工具與上下文，使 Agent 即開即用。這是軟體商業模式與產品設計的下一步。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q24, B-Q16, C-Q10

---

### Q&A 類別 B: 技術原理類

Q1: 部落格 MCP 的工具如何協同運作？
- A簡: 先指引，再片段檢索，讀全文，找相關；以兩段式上下文管理。
- A詳: 流程為 GetInstructions→SearchChunks→（可選）SearchPosts→GetPostContent→GetRelatedPosts。先以 instructions 控制行為與邊界，再以 chunks快速提供線索；必要時擴展文章清單；最後讀取指定全文片段與延伸相關。此「先檢索後讀取」機制控管 context window，避免資訊爆量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q10, C-Q3
  
Q2: GetInstructions 的技術機制與設計重點？
- A簡: 返回動態指引與規則，可含會話標識，強制初始化流程。
- A詳: GetInstructions 回應 Markdown，含使用規則、步驟建議、工具清單與範例。可返回如 conversationId 之類標識，要求後續所有工具必須攜帶，達到「強制先學、再用」的效果。設計重點：易讀、可抽取、含禁止事項與安全邊界，保障可控行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q11, D-Q1

Q3: SearchChunks 的向量檢索原理與流程？
- A簡: 將片段嵌入向量空間，依語義相似度快速找重點。
- A詳: 內容先被切片與synthesis，再建立向量索引。Query嵌入後以相似度召回片段，返回Markdown含引用與摘要。關鍵：良好切片策略、精煉內容、適當limit與多次迭代查詢。可搭配再查全文以提升可靠性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q8, D-Q3

Q4: SearchPosts 的索引與查詢管線如何設計？
- A簡: 以標題、標籤、時間與嵌入混合排序，返回文章清單。
- A詳: 為文章建立元資料索引（tags、年份、系列）與全文嵌入；Query同時匹配元資料與語義相似度，混合打分排序，返回 postid與摘要。用於「擴展探索」，為下一步 GetPostContent 做準備，避免一次讀過多內容。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q10, C-Q4

Q5: GetPostContent 的參數如何影響輸出？
- A簡: synthesis、position、length控制片段型態、起點與長度。
- A詳: synthesis 指定輸出型態（origin/solution/faq/summary等）；position與length控制片段範圍，便於精準引用或小窗閱讀；postid 指定文章。設計目標是避免整篇灌入模型，僅拉必要片段，以保上下文品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q9, D-Q4

Q6: GetRelatedPosts 的關聯度如何計算？
- A簡: 以元資料、語義嵌入與連結關係綜合評分。
- A詳: 相關性可由 tags/series/time、embedding相似度、文內互鏈、社交信號等綜合。返回限量清單，防止擴散性閱讀造成context膨脹。設計重點是可調權重與limit，契合不同情境（解題、學習）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q10, D-Q4

Q7: 內容預處理（synthesis）管線如何設計？
- A簡: 長文→拆段→精煉→結構化→嵌入，產出可檢索單元。
- A詳: Pipeline：抽取重點段落、生成FAQ/solutions/摘要、標註元資料（主題、層次）、產出Markdown片段；再做向量嵌入與索引。需選模型與prompt迭代以平衡成本與品質。目標：「查到即用」並保持語境完整。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, D-Q5, C-Q7

Q8: 長文切片（chunking）策略與8KB限制如何管理？
- A簡: 依語意段落切片，搭配摘要頭尾，控制大小與關聯。
- A詳: 以語意斷點切片，避免機械字數；每片段可含導言與結尾摘要以保上下文；對應模型8KB上下文限制，採限量召回、多輪查詢、延遲讀全文策略，確保模型負載可控。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q3, B-Q10, D-Q4

Q9: Context Window 管理的策略有哪些？
- A簡: 先檢索後讀取、限量召回、摘要化、分段迭代。
- A詳: 以「檢索→篩選→讀取」兩段式，控制chunk數量與大小；優先摘要型輸出；分批注入上下文，必要時引用外部資源URI。不僅依模型容量，更根據任務複雜度與關鍵性動態調整。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q10, B-Q10, D-Q4

Q10: 「先檢索再讀取」機制的技術原理？
- A簡: 用向量檢索找線索，再精準拉取必要全文片段。
- A詳: 第一階段以 embeddings召回片段/文章清單；第二階段以postid與位置拉取精準片段或全文；回應統一用Markdown以便抽取。此機制兼顧效率與準確性，是 Context Engineering 的關鍵。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q3, B-Q5

Q11: Shopify「learn_shopify_api」強制初始化的效益？
- A簡: 保證先讀指引再用工具，降低誤用與偏離，提升一致性。
- A詳: 強制取得 conversationId 使後續工具必需在同一會話脈絡執行。好處：確保指引入窗、狀態一致與安全邊界生效；避免 Agent直接執行造成錯誤或上下文污染。屬「發現層」控管技巧。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, A-Q19, D-Q2

Q12: conversationId 維持會話狀態的原理？
- A簡: 以標識綁定工具調用的上下文，形成可控的連貫會話。
- A詳: 工具要求攜帶conversationId，伺服端以此關聯設定、授權與上下文資訊；客端Agent亦以此辨識指引與先前回應。實現「會話一致、工具一致、上下文一致」三一致原則，降低錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, D-Q2, C-Q6

Q13: 為何回應要採用 Markdown 而非 HTML？
- A簡: 降噪、強結構、易抽取；提升模型理解與生成品質。
- A詳: Markdown便於模型建立層次（標題/清單/代碼）、做段落抽取與引用；HTML常含樣式與額外標籤干擾。回應以 Markdown加指引是多個成功 MCP 的共同做法（Shopify、Context7），落地效益明顯。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q15, B-Q10, C-Q9

Q14: GraphQL introspection 與 validate 工具如何配合？
- A簡: 先查 schema 建構查詢，再以驗證工具檢查代碼正確。
- A詳: introspect_graphql_schema 返回可用欄位與結構，Agent 擬定查詢或突變；validate_graphql_codeblocks 對生成片段做語法與版本驗證，避免幻覺API與過時用法。形成「生成→驗證→修正」閉環。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, D-Q9, C-Q10

Q15: Context7 的兩工具工作流如何設計？
- A簡: 先解析庫ID，再抓主題文件與程式碼；帶信任分數與指引。
- A詳: resolve-library-id 返回可選ID與trust score、使用規則；get-library-docs 以ID與topic返回Markdown文件與程式碼片段。兩步設計降低選擇困難，確保素材來源正確且可用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q18, C-Q10, D-Q3

Q16: 如何降低 Agent 認知負荷、簡化工具介面？
- A簡: 分層、限量、帶指引、語義命名，對齊任務步驟。
- A詳: 工具介面用任務語義命名（SearchChunks/Posts等）、分發現規劃執行；回應帶清晰指引與範例；限制返回量與必要欄位。避免把 API 端點一對一搬進 MCP，改以workflow映射。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q16, D-Q10

Q17: MCP 中如何設計安全性與邊界控制？
- A簡: 指引明確、會話綁定、參數驗證、結果驗證。
- A詳: 以 instructions 明定可/不可為；conversationId 維持會話邊界；工具參數做校驗與白名單；對生成結果（如GraphQL）做 validate。避免對外接口暴露過多，降低誤用與攻擊面。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q11, B-Q12, D-Q2

Q18: 如何避免「UI導向」與「檯面下溝通」的壞習慣？
- A簡: 回到領域與流程，設計可解問題的工具與指引。
- A詳: MCP不是把現有UI能做的事開出去；也不靠人類默契。應以領域問題與工作流程做工具抽象，讓 Agent 按指引執行。避免隱藏規則與語意不清，回應中直接嵌入必要instructions。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, A-Q4, C-Q6

Q19: Streamable HTTP 的 MCP 通信流程是什麼？
- A簡: 以HTTP承載MCP互動，工具可流式返回多段結果。
- A詳: MCP Host 支援以HTTP建立工具調用與回應通道；流式返回便於邊檢索邊生成、逐段注入上下文。部署時需提供公開URL並遵循Host要求，客端按協定注冊工具與描述。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q1, C-Q2, D-Q6

Q20: MCP 的 Resources 可如何設計（延伸）？
- A簡: 提供原文、附件URI、代碼片段，支援就地引用。
- A詳: 資源可包含文章Markdown、片段URI、圖片/代碼檔；Agent在VSCode等環境直接「加上下文」使用。資源與工具相輔，讓「拉片段、讀全文」與「開原文」形成完整閉環。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, C-Q9, D-Q4

Q21: 如何用 MCP Inspector 觀察工具調用？
- A簡: 監看工具呼叫與參數，理解Agent的思路與流程。
- A詳: Inspector展示工具清單、描述、調用歷程與回應內容。可見Query策略、limit設定、synthesis選擇等，協助迭代工具接口與指引，優化實際效果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q3, D-Q3

Q22: Coding Agent 如何用 MCP context 生成程式碼？
- A簡: 先取文章精華片段，再按需求產碼並迭代修正。
- A詳: Agent用SearchPosts查主題、GetPostContent取solution片段、SearchChunks補技術細節，將素材注入context；再根據指令生成程式碼，搭配回圈測試與修正。示例：.NET Channel並行JSONL處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, B-Q23, D-Q9

Q23: CLI Pipeline 平行處理架構的原理是什麼？
- A簡: 以Channel+Task生產者/消費者模式並行處理JSONL。
- A詳: Producer從STDIN讀JSONL寫入Channel；多個Consumer以指定並行度讀取處理；將結果輸出STDOUT。優點是控並行、具彈性、易測試；適合大規模資料處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q22, C-Q5, D-Q3

Q24: 如何提升RAG精準度？索引與元資料的要點？
- A簡: 精煉內容、語意切片、豐富元資料、多信號混排。
- A詳: 先做synthesis，避免原始長文直接切；片段包含導言/摘要；元資料涵蓋主題/系列/年份/標籤；排序綜合語義相似度與元資料；limit與多輪查詢配合「先檢索後讀取」。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q8, D-Q3

Q25: ChatGPT 與 Claude在MCP調用上的差異？
- A簡: Claude直線一次查；ChatGPT常多輪微調查，文字潤飾較強。
- A詳: 實測中Claude按指引先GetInstructions再一次SearchChunks；ChatGPT則分兩次查詢，先粗後精，并有Thinking模式微調Query。兩者都能正確引用與回鏈；風格差異在查詢策略與語言表達。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, D-Q9, B-Q21

---

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何在 VSCode 安裝並使用本部落格 MCP？
- A簡: 以MCP: Add Server加入HTTP URL，完成後直接在Agent調用工具。
- A詳: 步驟：1) VSCode按F1→MCP: Add Server→選HTTP；2) 輸入URL：https://columns-lab.chicken-house.net/api/mcp/（保留結尾斜線）；3) 命名後確認。可用/mcp GetInstruction強制初始化。最佳實踐：先讀指引再查片段；查片段先限量，需全文再GetPostContent；相關拓展用GetRelatedPosts，避免上下文爆量。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, A-Q12, D-Q6

Q2: 如何在 ChatGPT Plus 啟用 MCP 並掛上 Server？
- A簡: 開啟MCP Beta，新增HTTP Host，填入本MCP URL即可使用。
- A詳: 步驟：1) 在ChatGPT設定啟用MCP（Beta）；2) 新增HTTP類型的MCP Host，填入URL：https://columns-lab.chicken-house.net/api/mcp/；3) 在對話中以自然語言觸發工具（或先要求進行GetInstruction）。注意：需Plus訂閱；初次使用務必要求列出引用來源與連結以驗證結果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q19, A-Q20, D-Q9

Q3: 如何用 MCP 查詢「微服務分散式交易」相關內容？
- A簡: 先初始化指引，再以SearchChunks檢索關鍵詞，必要時讀全文。
- A詳: 步驟：1) /mcp GetInstruction；2) SearchChunks query含：分散式交易、Saga、2PC、Outbox等；synthesis選summary/faq/solution；limit 8-10；3) 若需詳讀，取postid用GetPostContent（solution）；4) 延伸主題用GetRelatedPosts。最佳實踐：要求列引用標題+URL，避免幻覺。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q3, D-Q3

Q4: 如何用 MCP 生成部落格演進時間線摘要？
- A簡: 用SearchPosts抓不同年份改版文，整合摘要並列連結。
- A詳: 步驟：1) SearchPosts query含：BlogEngine、WordPress、Jekyll、GitHub Pages、年份；2) 對每postid用GetPostContent synthesis=summary，控制length；3) 整合為時間序Markdown清單，附標題與URL。注意：limit控制在合理範圍，避免上下文膨脹；摘要保持100字內。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q5, D-Q4

Q5: 如何以 MCP+Copilot 建立 JSONL CLI 平行處理範例？
- A簡: 搜主題文→取solution片段→生成程式骨架→補測試資料。
- A詳: 步驟：1) SearchPosts query：pipeline、CLI、stdio、jsonl；2) GetPostContent synthesis=solution；3) 要求Agent生成Channel+Task並行處理框架；4) 生成測試jsonl與shell指令；5) 執行與驗證。程式碼片段：
  ```
  var ch = Channel.CreateBounded<UserItem>(100);
  // producer: stdin -> ch.writer
  // consumers: parallel tasks -> process -> stdout
  ```
  注意：控制並行度、處理錯誤輸出stderr。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q23, A-Q22, D-Q3

Q6: 如何設計自己的GetInstructions（仿Shopify）？
- A簡: 回應必含使用規則、流程建議、會話標識與示例。
- A詳: 步驟：1) 定義回應Markdown版型：必做步驟、工具清單、禁止事項；2) 生成會話標識（conversationId或等價概念）；3) 在其他工具做校驗：無標識則拒絕。示例段落：MANDATORY FIRST STEP、SAVE THIS CONVERSATION ID。注意：避免過長；提供簡明示例。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q12, D-Q2

Q7: 如何為長文建立synthesis版本以供RAG？
- A簡: 產出FAQ、Solutions、摘要片段與元資料，做向量索引。
- A詳: 步驟：1) 用LLM生成FAQ（Q/A）、solutions（流程+代碼小段）、summary（150-300字）；2) 標註主題、系列、難度、應用場景；3) 產出Markdown片段；4) 嵌入索引。注意：控制token成本；用小型模型做初稿，大模型做質檢；保持一致格式。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q7, B-Q8, D-Q5

Q8: 如何設定SearchChunks的query/synthesis/limit？
- A簡: Query含關鍵詞與同義詞；synthesis選summary/faq；limit 5-10。
- A詳: 步驟：1) Query寫主題詞+技術術語，如「Saga、Outbox、一致性」；2) synthesis選summary（先看概念）或faq（直取問答）；3) limit設定5~10，避免灌入過多；4) 若結果不理想，微調Query或分兩輪查詢。最佳實踐：要求返回引用標題+URL。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q10, D-Q3

Q9: 如何用Resources提供文章原文給VSCode？
- A簡: 以URI或Markdown資源暴露原文，Agent可就地加上下文。
- A詳: 步驟：1) 在MCP server實作資源清單，包含postid→URI、標題、摘要；2) VSCode中指示Agent「Add context」以載入原文；3) 配合GetPostContent拉小段。注意：URI需可公開訪問；回應用Markdown降低噪音。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q20, A-Q15, D-Q6

Q10: 如何整合MCP與企業知識庫（仿Context7）？
- A簡: 先解析庫ID，再抓主題文件與範例，回應內含指引。
- A詳: 步驟：1) 設計resolve-library-id：返回ID、trust score、使用規則；2) 設計get-library-docs：輸入ID與topic，返回Markdown文件與code；3) 為各庫維護版本與權威來源；4) 在回應中嵌入指引避免誤用。注意：限制tokens與返回數量，控制上下文。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: B-Q15, A-Q24, D-Q3

---

### Q&A 類別 D: 問題解決類（10題）

Q1: Agent未先呼叫GetInstructions導致工具失敗怎麼辦？
- A簡: 提醒初始化，或在對話中明確要求/mcp GetInstruction。
- A詳: 症狀：工具報錯或表現異常。原因：缺少初始化指引與狀態。解法：在對話中要求先執行GetInstructions；或在server側對未初始化直接返回錯誤與提示。預防：在指引與工具描述中強調「必做第一步」，必要時強制校驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, B-Q11, C-Q6

Q2: 缺少conversationId造成錯誤如何修復？
- A簡: 重新執行初始化工具，抽取並保存ID，後續工具攜帶。
- A詳: 症狀：後續工具返回「缺ID」錯誤。原因：未初始化或Agent未抽取ID。解法：再次呼叫初始化工具，指示模型「從回應抽取ID並保存」，重試後續工具。預防：在工具描述與回應Markdown中用醒目提示、範例代碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q12, C-Q6

Q3: 向量檢索結果不精準的原因與對策？
- A簡: 內容未精煉、切片不當、Query詞弱；需synthesis與迭代。
- A詳: 症狀：返回片段離題或無用。原因：原文未synthesis、切片破壞語境、Query不含關鍵術語。解法：先做synthesis；優化chunk策略；加入同義詞與專有名詞；分兩輪查詢微調；降低limit。預防：建立標準化元資料與查詢模板。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q7, C-Q8

Q4: Context window爆量導致回覆偏離怎麼處理？
- A簡: 改用兩段式、限量召回、摘要化、分批注入上下文。
- A詳: 症狀：回覆冗長、抓不到重點。原因：一次灌入過多全文或片段。解法：先SearchChunks，再GetPostContent小段；使用summary/faq；limit控制在5-10；分批注入。預防：在工具指引中強調「先檢索後讀取」與限量策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q10, C-Q4

Q5: RAG表現不佳處理長篇敘事時如何改善？
- A簡: 先做synthesis，生成FAQ/solutions，再進行向量索引。
- A詳: 症狀：長文檢索後無法直接解題。原因：切片不含完整觀念與流程。解法：synthesis出結構化單元；向量索引這些單元；查得後直接可用。預防：建立內容生成標準與審查流程，確保品質一致。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: A-Q8, B-Q7, C-Q7

Q6: VSCode無法連線Streamable HTTP MCP怎麼辦？
- A簡: 檢查URL格式、尾斜線、Host支援與網路權限。
- A詳: 症狀：無法新增或工具不可用。原因：URL錯誤、結尾斜線缺失、Host不支援HTTP、代理或防火牆阻擋。解法：確認URL：https://columns-lab.chicken-house.net/api/mcp/；改用支援的Host；檢查網路設定。預防：文件與指引中明示格式要求。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q19, A-Q6

Q7: HTML舊文轉Markdown造成圖片連結壞怎麼處理？
- A簡: 批次轉檔、路徑規範化、寫校正工具修復引用。
- A詳: 症狀：圖片或連結失效。原因：歷史路徑混亂、檔名語系問題。解法：AI輔助批次轉換HTML→Markdown；統一路徑與檔名規則（中文→英文）；寫小工具校正圖檔與連結，生成對照表。預防：在repo建立發佈前檢查pipeline。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q7, C-Q7, B-Q20

Q8: 中文檔名/網址造成repo錯誤如何修復？
- A簡: 批次改名為英文、修路徑、建立轉址與對照表。
- A詳: 症狀：編譯/部署失敗或檔案找不到。原因：中文路徑在某些工具/平台不友善。解法：AI輔助批次改名；路徑規範化；建立RewriteMap或轉址；維護一份對照表便於檢索。預防：規範新文命名。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, D-Q7, C-Q1

Q9: Agent出現幻覺或引用錯誤連結怎麼辦？
- A簡: 要求列引用標題+URL，啟用驗證工具或交叉查核。
- A詳: 症狀：答非所問或連到錯頁。原因：上下文不足、素材過時、未驗證。解法：在指令中要求「列引用與連結」；必要時以validate工具檢查；交叉用SearchPosts與GetPostContent核對。預防：回應採Markdown、明確instructions。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q2, C-Q3

Q10: 工具介面設計過度API化導致交互不佳怎麼修正？
- A簡: 改以workflow語義設計，回應嵌入指引與示例。
- A詳: 症狀：Agent選擇困難、誤用頻繁。原因：一對一映射API端點、不含指引。解法：分層（發現/規劃/執行）、語義命名、限量返回、Markdown指引。預防：以「使用者會問什麼」出發設計。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q3, A-Q16, B-Q16

---

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 MCP（Model Context Protocol）？
    - A-Q2: 什麼是「MCP-first」的設計思維？
    - A-Q3: 為什麼「MCP ≠ API」？
    - A-Q4: 什麼是「Workflow First」設計？
    - A-Q5: MCP 的三大原語（Primitives）是什麼？
    - A-Q6: 為何要把部落格服務化成 MCP？
    - A-Q13: SearchChunks 與 SearchPosts 有何差異？
    - A-Q14: GetPostContent 與 GetRelatedPosts 的用途？
    - A-Q15: 為什麼用 Markdown 回應比 HTML 更適合 LLM？
    - B-Q1: 部落格 MCP 的工具如何協同運作？
    - B-Q10: 「先檢索再讀取」機制的技術原理？
    - C-Q1: 如何在 VSCode 安裝並使用本部落格 MCP？
    - C-Q2: 如何在 ChatGPT Plus 啟用 MCP 並掛上 Server？
    - C-Q3: 如何用 MCP 查詢「微服務分散式交易」相關內容？
    - D-Q1: Agent未先呼叫GetInstructions導致工具失敗怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q7: 「內容服務化、正規化、流程效率化」三者差異？
    - A-Q8: 什麼是內容正規化（synthesis）？為何不用「只靠 RAG」？
    - A-Q10: 什麼是「Context Engineering」？核心價值是什麼？
    - A-Q16: 「發現/規劃/執行」三層設計是什麼？
    - A-Q17: Shopify.Dev MCP 的設計精髓是什麼？
    - A-Q18: Context7 MCP 的定位與價值？
    - A-Q19: 什麼是 conversationId？為何重要？
    - A-Q20: MCP 如何支援「解答/解題/學習」三種情境？
    - A-Q21: 什麼是 AI IDE 與 Vibe Coding？
    - A-Q22: 什麼是 JSONL 與 CLI Pipeline 的概念？
    - B-Q2: GetInstructions 的技術機制與設計重點？
    - B-Q3: SearchChunks 的向量檢索原理與流程？
    - B-Q4: SearchPosts 的索引與查詢管線如何設計？
    - B-Q5: GetPostContent 的參數如何影響輸出？
    - B-Q11: Shopify「learn_shopify_api」強制初始化的效益？
    - B-Q12: conversationId 維持會話狀態的原理？
    - B-Q14: GraphQL introspection 與 validate 工具如何配合？
    - C-Q4: 如何用 MCP 生成部落格演進時間線摘要？
    - C-Q5: 如何以 MCP+Copilot 建立 JSONL CLI 平行處理範例？
    - D-Q3: 向量檢索結果不精準的原因與對策？

- 高級者：建議關注哪 15 題
    - A-Q23: 為何要做 LLM 預先生成（synthesis）？
    - A-Q24: MCP 與 SaaS 的未來關係為何？
    - A-Q25: 什麼是「工作流程訂閱」？
    - B-Q7: 內容預處理（synthesis）管線如何設計？
    - B-Q8: 長文切片（chunking）策略與8KB限制如何管理？
    - B-Q9: Context Window 管理的策略有哪些？
    - B-Q16: 如何降低 Agent 認知負荷、簡化工具介面？
    - B-Q17: MCP 中如何設計安全性與邊界控制？
    - B-Q24: 如何提升RAG精準度？索引與元資料的要點？
    - C-Q6: 如何設計自己的GetInstructions（仿Shopify）？
    - C-Q7: 如何為長文建立synthesis版本以供RAG？
    - C-Q10: 如何整合MCP與企業知識庫（仿Context7）？
    - D-Q4: Context window爆量導致回覆偏離怎麼處理？
    - D-Q5: RAG表現不佳處理長篇敘事時如何改善？
    - D-Q10: 工具介面設計過度API化導致交互不佳怎麼修正？