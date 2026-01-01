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
- A簡: 面向 AI Agent 的協議，提供工具與上下文管理，讓模型按工作流程取用資料與能力，而非傳統 API。
- A詳: MCP 是設計給 AI Agent 使用的協議，核心在模型的上下文（Context）與工作流程（Workflow）管理。它以 Tools、Resources、Prompts 為原語，使 Agent 能像人類處理任務般先獲取指示，再檢索片段與原文，最後執行具體操作。MCP 不只是把 REST API 包裝，而是「讓模型理解與使用」的介面設計，貼近任務流程與語意表達（多用 Markdown），以提升準確度與效率。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q4, B-Q1

Q2: MCP 與傳統 API 有何不同？
- A簡: MCP 以工作流程與上下文為中心，API 注重端點與資料格式；MCP 是給 Agent 的工具集。
- A詳: 傳統 API 強調端點、參數與回傳格式，多面向人類開發者；MCP 則面向 Agent 的操作語境，重視「如何被模型理解」與「如何支援任務流程」。MCP 工具常回傳帶說明的 Markdown、流程引導與必要上下文（如 conversationId），並分層提供探索、規劃、執行能力，避免把 UI 或脫離領域問題的設計搬進介面。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q8, B-Q10

Q3: 為什麼要把部落格做成 MCP？
- A簡: 讓 Agent能有效用文章資源，降低理解門檻，支援解答、解題、寫程式、寫文件等任務。
- A詳: 長文敘事不利於直接 RAG，將部落格服務化為 MCP，讓 Agent可依工作流程先讀使用說明，再檢索片段與原文，最後整合解決。配合內容正規化（預先用 LLM 生成 FAQ、Solutions、摘要），能顯著提升檢索精度與應用效果，支持 Chat、整理歷史、vibe coding/ writing 等多樣場景。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q2, C-Q1

Q4: 什麼是 Workflow First 的設計？
- A簡: 先從使用情境與任務流程出發，反推需要的工具與介面，再定義 MCP 規格。
- A詳: Workflow First 強調以「真人如何完成任務」為基準設計工具。先拆解情境（如解題：認識前輩→問線索→讀原文→找相關），抽出必要動作（GetInstructions、SearchChunks、GetPostContent、GetRelatedPosts 等），再讓 Agent依此操作。此法避免 API-first 的端點導向偏差，讓工具與上下文貼近任務脈絡，降低幻覺與誤用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, B-Q2, A-Q13

Q5: MCP 的核心原語（Primitives）有哪些？
- A簡: Tools、Resources、Prompts。分別提供操作能力、外部內容、指示與規則。
- A詳: MCP 以三類原語支撐 Agent：Tools 提供可調用的功能（如檢索、讀原文、驗證）；Resources 暴露外部資料（如檔案、文章內容）；Prompts 則是指示與使用規則，常以 Markdown嵌入工具回覆。這三者共同構成上下文與工作流程，確保 Agent 能按步驟正確執行。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q10, A-Q2

Q6: 工具（Tools）在 MCP 中扮演什麼角色？
- A簡: 讓 Agent以合乎流程的方式完成任務，是貼近情境的「操作手腳」。
- A詳: Tools 是 MCP 的可調用能力，需貼近使用者的工作流程與領域問題，而非 UI導向。好的工具會：回傳同時包含結果與使用規則的 Markdown、降低誤用成本、支援探索→規劃→執行分層；並讓 Agent能循序操作（先取指令、再查片段、再讀全文、再執行）。工具品質直接影響 Agent 準確度與效率。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q10, A-Q4

Q7: 為什麼 MCP 回應常用 Markdown 而非 JSON？
- A簡: Markdown含語意標示與人類可讀的指引，利於 LLM 理解與抽取規則與重點。
- A詳: 面向模型的輸出應兼顧「可讀性」與「語意線索」。Markdown能在結果旁就地提供指示、限制、重要提醒（如 conversationId），也可用標題、列表、程式碼區塊呈現結構，高密度且低噪音。相較純 JSON，Markdown更有助 LLM 作業時即時理解規則與抽取必要資料，提升推理與操作精度。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, A-Q2, A-Q5

Q8: MCP-first 與 API-first 的差異？
- A簡: MCP-first 以 Agent使用與流程為中心；API-first 以端點與資料模型為中心。
- A詳: API-first 面向人類工程師，強調契約清晰與資料一致；MCP-first 面向 Agent，重視上下文、流程引導與誤用防護。MCP-first會把「探索→規劃→執行」嵌入工具回覆與交互，並提供指示與驗證機制（如先學 API、再查 chunks、再取全文、再驗 code），從而提高生成可靠度。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q10, A-Q29

Q9: 為什麼需要內容正規化（預先用 LLM 生成）？
- A簡: 長文切片不易直接用，需轉為合用型態（FAQ、Solutions、摘要）以提升檢索與應用。
- A詳: 部落格多為敘事長文，直接切片做 RAG會失去脈絡且片段不完整。預先用 LLM重整為 FAQ、Solutions、Summary、Key points 等合用型態，能讓向量檢索更精準、Agent更易組合答案與步驟，也節省交互成本，提高解答、解題、coding 等應用的成功率。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q3, A-Q10

Q10: RAG 是什麼？為何長文不適合直接用？
- A簡: 檢索增強生成。長文切碎後片段缺主題完整性，檢索與應用效果受限。
- A詳: RAG 在生成前先檢索相關內容以增強答案。對敘事長文，切片常不完整，無法直接支持解題或實作。需先做內容正規化，把長文轉為合適的單元（FAQ、Solutions、摘要），再向量化檢索、逐步取用，才能在 Agent 流程中發揮效果。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q9, B-Q3, B-Q17

Q11: 什麼是「synthesis」在本文中的意義？
- A簡: 文章的應用型態標記，如 summary、solution、faq，用於檢索與取用。
- A詳: 「synthesis」代表內容的用途視角標記。查 chunks 或 posts 時指定 synthesis，可控制回傳為摘要、解法、FAQ等型態，利於 Agent在不同任務精準取用。這是內容正規化的關鍵，使檢索不只找文，更找「可用的結構化知識」。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, B-Q2, C-Q7

Q12: MCP Tools 設計有哪些原則？
- A簡: 對齊工作流程、就地提供指示、分層探索規劃執行、回傳低噪音高語意格式。
- A詳: 原則包括：1) 以情境與任務步驟反推工具；2) 工具回覆夾帶使用規則、限制與關鍵 ID；3) 分層設計（探索→規劃→執行）；4) 採 Markdown、摘要與片段優先，再取全文；5) 提供驗證工具（如程式碼檢查）。這些做法可大幅降低 Agent 亂用與幻覺。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q10, A-Q29

Q13: 部落格的四種使用情境是什麼？
- A簡: 訂閱、解答、解題、學習。各自對應不同工作流程與工具設計。
- A詳: 訂閱是日常閱讀；解答針對具體問題找明確答案；解題是面對情境化難題需組合解法與範例；學習則需系統化路徑與材料。每種情境的流程不同，應抽取相應工具（指示、檢索片段、取全文、找相關），讓 Agent能自然完成任務。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q9, C-Q3

Q14: 「解答」與「解題」的差異？
- A簡: 解答是找固定答案；解題需因地制宜組合方案與步驟，無標準答案。
- A詳: 解答處理 question，有明確結論與定義；解題處理 problem，需分析情境、挑選策略、組合步驟與範例，最後形成可落地的 solution。MCP 設計需支援兩者：前者偏 FAQ/摘要；後者需相關文章、片段、原文與驗證工具，輔以工作流程引導。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q5, B-Q2

Q15: 什麼是 Context Engineering？
- A簡: 以工程方法管理模型上下文，控制資訊量與關聯，提高準確與效率。
- A詳: Context Engineering 是設計「進到模型的資訊」的藝術與工程。包括先取必要指示、分批取片段、再取全文、限制回傳大小、指定 synthesis、避免爆量堆疊等。其目標是讓模型在有限視窗中保持重點清晰與推理正確，直接影響 Agent 能力與品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, B-Q17, D-Q3

Q16: 為什麼「為了技術而技術」是錯誤方向？
- A簡: 應用優先，設計需回到情境與問題本身，技術只是手段。
- A詳: 本文主張先釐清應用目標與流程，再選技術與規格。單純追逐技術容易忽略使用場景與工作流程，導致檢索不準、幻覺多、整合效能差。MCP-first 與內容正規化都以「能用」為核心，才能讓 Agent 真正幫助使用者解答與解題。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, A-Q12, B-Q9

Q17: 為何 Shopify.Dev MCP 被視為優良案例？
- A簡: 它分層設計、強制學習指示、以 chunks/Markdown 檢索與全文取得、提供程式驗證。
- A詳: Shopify 的 learn_shopify_api 要求先取得指示與 conversationId，之後 search_docs_chunks 檢索片段、fetch_full_docs 取全文（Markdown），GraphQL 的 introspect 與 validate 提供查綱目與驗代碼。整體貼合「探索→規劃→執行」，強化可靠與可用性，降低幻覺與誤用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q11, B-Q12

Q18: Context7 MCP 的定位與特色是什麼？
- A簡: 提供新版與版本化的開發文件檢索，兩工具即可拉高可用度，回傳含指示。
- A詳: Context7 以 resolve-library-id + get-library-docs 支援開發者查官方文件與程式碼範例。回覆同時包含使用規則、信任分數、版本資訊等，利於 Agent 選擇高品質資料源，避免舊資料與幻覺 API。精簡工具設計，對齊「找來源→取主題→用範例」的工作流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, A-Q12, D-Q8

Q19: 為何要先呼叫 GetInstructions 或 learn_shopify_api？
- A簡: 取得使用規則與必要識別（如 conversationId），避免後續工具失敗或誤用。
- A詳: 許多 MCP 設計把「必讀指示」與「必要識別」置於首要步驟。Shopify 更強制其他工具需帶 conversationId，否則回錯。先讀指示可讓 Agent 把規則與限制放進上下文，後續檢索與執行更安全可控，降低操作歧義與上下文污染。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q10, C-Q2, D-Q1

Q20: 什麼是 conversationId？為何重要？
- A簡: 對話識別，用來維持上下文連續與權限校驗，保證工具正確運行。
- A詳: 在某些 MCP（如 Shopify），conversationId 是會話的唯一識別。取得後必須在後續工具呼叫帶入，以表明你已讀指示、維持上下文連續、讓伺服器驗證使用步驟。此機制有效防誤用，也讓分層流程（探索→規劃→執行）有可控邊界。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q10, D-Q1, A-Q12

Q21: chunk 與 post 有何不同？
- A簡: chunk 是局部片段，利檢索快速；post 是完整文章，利深入理解與引用。
- A詳: 檢索時先取 chunks 可快速聚焦主題與線索，減少上下文雜訊；需要完整脈絡時再取 post 全文（多用 Markdown）。兩者搭配能兼顧速度與精度：先找線索→再讀原文→最後組合答案或解法，符合 Workflow First。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, B-Q5, B-Q17

Q22: 為何偏好 Markdown 而非 HTML 提供內容？
- A簡: Markdown高資訊密度、低格式噪音，利模型理解與抽取重點與代碼區塊。
- A詳: HTML 混雜許多呈現標籤，對 LLM 造成解析負擔與雜訊。Markdown 以標題、清單、程式碼塊、連結等語意結構表達重點，利於模型抽取指示、片段與示例，提升檢索與生成準確度。Shopify/Context7 都以 Markdown 回覆。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q7, B-Q11, B-Q13

Q23: MCP 在未來 SaaS 生態中的角色？
- A簡: 成為 Agent 時代的「API 等價物」，讓服務被 Agent 直接使用與整合。
- A詳: 過去 SaaS 以 API 促進整合；Agent 時代，AI 能自行讀規格、呼叫工具、組合流程。提供高品質 MCP 能讓使用者以 Agent 即時接入服務，無須繁重串接。MCP 品質將成為長期競爭力指標，驅動「工作流程訂閱」的新型態服務。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q1, A-Q8, A-Q29

Q24: 什麼是 Streamable HTTP（MCP 連線方式）？
- A簡: 一種支援串流的 HTTP 介面，MCP Host 可透過它連接 MCP Server。
- A詳: Streamable HTTP 讓 MCP Host 與 Server 以 HTTP 串流互動，傳遞工具呼叫、回覆與中間事件，利於在 VSCode、ChatGPT 等環境快速掛載第三方 MCP。本文提供部落格 MCP 的 HTTP URL，無需 API key 即可體驗。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, D-Q5, B-Q14

Q25: 什麼是 vibe coding 與 vibe writing？
- A簡: 以對話驅動的協作方式，Agent 依文章或需求脈絡生成程式或內容。
- A詳: vibe coding 是用對話告知需求與參考文章，Agent 透過 MCP 檢索片段與原文，再生成或改寫程式框架與測試。vibe writing 類似，讓 Agent 蒐集與編排資料、產出初稿或清單。此法強化「用我的知識工作」的體驗與效率。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q5, B-Q19

Q26: 為何要流程效率化（清理技術債）？
- A簡: 移除阻礙（舊格式、壞連結）才能讓正規化與檢索順暢、成本更低。
- A詳: 若有大量 HTML 舊文、中文檔名/網址、壞圖徑等，向量化與檢索品質會受損。先以 AI IDE（如 Copilot）批次重構為 Markdown、整理路徑與工具，能提升正規化與 RAG 效果，縮短發布管線、降低 token 成本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q7, D-Q6, C-Q8

Q27: 何謂「對 Agent 友善」的 MCP 設計要點？
- A簡: 明確指示、低誤用成本、分層工具、語意清晰輸出、必要驗證與防護。
- A詳: 設計要點包括：工具首呼叫提供使用規則與必要 ID；回應夾帶操作手冊；先 chunks 再全文；輸出 Markdown；提供驗證工具（如 GraphQL 驗代碼）；限制回傳大小與語意範圍；以工作流程拆解工具。這些能提升準確度與可用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q10, D-Q1

Q28: API 設計中的「合情合理」與「可靠」指什麼？
- A簡: 符合常理（易被 LLM理解）與守住邊界（防誤用與例外），面向 AI 使用。
- A詳: 合情合理指設計貼近常理與領域問題，讓 LLM 易理解且少錯誤；可靠指即便被亂呼叫，也能守住邊界、錯誤可控、不留漏洞。這些原則延伸到 MCP 設計，透過指示、驗證與分層流程，強化安全與正確。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q10, D-Q1

Q29: 「發現/規劃/執行」分層有何價值？
- A簡: 讓 Agent 先探索資源與規則，再規劃細節，最後執行，降低混亂與幻覺。
- A詳: 分層能把工具量化且可控：發現層引導資源與指示（learn_shopify_api、GetInstructions）；規劃層檢索與取全文（search_docs_chunks、SearchChunks、GetPostContent）；執行層產生與驗證（validate_graphql_codeblocks）。此法讓 Agent 步步就緒，可靠完成任務。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q11, B-Q12

Q30: 為何將知識庫轉為 FAQ/Solutions 有價值？
- A簡: 把敘事長文轉為可用單元，提升檢索精度與可組合性，支援多場景。
- A詳: FAQ、Solutions、摘要等是「可用的知識結構」，能直接回答、組合步驟或指引實作。相較長文切片，正規化後更利向量檢索與 Agent 作業，能用在教學、測驗、解題與 coding 等多場景，且控制上下文更精準。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q7, C-Q7


### Q&A 類別 B: 技術原理類

Q1: MCP Server 整體如何運作？
- A簡: Host 透過協議呼叫 Tools，回傳含指示的內容，Agent依流程取用並組合行動。
- A詳: MCP Host（如 VSCode、ChatGPT）用 Streamable HTTP 連 MCP Server。Agent 先呼叫「指示」工具取得規則/ID，再用檢索工具（chunks/posts）收集線索，必要時取全文或相關文章，最後執行或驗證。回覆常用 Markdown，內含結果＋操作說明，支援分層流程與上下文管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q24, C-Q1

Q2: 本文部落格的 MCP Tools 規格與流程？
- A簡: GetInstructions→SearchChunks/Posts→GetPostContent→GetRelatedPosts，支援不同任務。
- A詳: 工具包含：GetInstructions（使用說明）、SearchChunks（片段檢索，支援 synthesis）、SearchPosts（文章清單）、GetPostContent（讀原文，支援位置長度）、GetRelatedPosts（找相關）。流程上先讀指示，再以 chunks 聚焦線索，必要時取全文與相關，最後交由 Agent 組合答案或實作。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q21, C-Q6

Q3: SearchChunks 的檢索原理與流程是什麼？
- A簡: 以向量檢索找片段，指定 synthesis 控制用途，限制回傳數量以控上下文。
- A詳: SearchChunks 接受 query、synthesis、limit，對預先正規化的內容做向量檢索。先取少量高關聯片段（FAQ、solution、summary等），讓 Agent迅速掌握重點；再視需要延展到全文。此流程符合「探索→規劃」，降低上下文爆量與噪音。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, A-Q21, D-Q2

Q4: SearchPosts 的原理與用法？
- A簡: 以向量與過濾條件找文章清單，利於定位主材料或建立閱讀計畫。
- A詳: SearchPosts 支援 query、synthesis、limit，回傳符合條件的文章清單與必要中繼資訊。用於「規劃層」判斷有哪些主材料值得深入，搭配 GetPostContent 取全文，或用 GetRelatedPosts擴展範圍，形成可執行的學習或解題路線。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, A-Q13, C-Q4

Q5: GetPostContent 如何設計與使用？
- A簡: 以 postid 讀原文內容，支援指定位置與長度，避免一次塞爆上下文。
- A詳: GetPostContent(postid, synthesis, position, length) 允許分段讀取，配合 synthesis 控制用途（摘要、解法等），避免全文一次注入造成視窗擁擠。此設計符合 Context Engineering，讓 Agent 能精準拉取必要段落，提升理解與生成品質。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, A-Q21, D-Q3

Q6: GetRelatedPosts 背後機制是什麼？
- A簡: 以語義關聯查相近文章，加強解題/學習時的材料廣度與脈絡延展。
- A詳: 根據內容向量與主題標註，找出與指定文章高度相關的其他文章。此工具在解題時擴展思路與範例，在學習時建立串連性的材料脈絡，配合 SearchChunks 與 GetPostContent形成「先聚焦、再延展」的流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, A-Q13, D-Q7

Q7: 內容預處理（LLM 生成）流程原理？
- A簡: 將長文轉為 FAQ/solution/summary 等單元，便於向量化與檢索取用。
- A詳: 先以 LLM 將原文抽取重點、重組為可用型態（FAQ、Solutions、摘要、關鍵概念），再做向量化與索引。查詢時就能直接命中可用單元，而非僅有敘事片段，提升檢索精度、組合答案效率與跨場景適用性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q30, C-Q7

Q8: Context Management 的核心機制有哪些？
- A簡: 控量、分段、分層、標記用途、就地指示與驗證，維持視窗內重點清晰。
- A詳: 核心包括：限制回傳（limit）、分段讀取（position/length）、分層（先chunks後全文）、用途標記（synthesis）、就地指示（Markdown規則）、必要驗證（如代碼檢查）。這些機制讓 Agent 在有限視窗中保持重點與正確推理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, D-Q3, B-Q5

Q9: 如何從情境抽工具（Workflow First 步驟）？
- A簡: 描述真人流程→抽出動作→對應 MCP 原語→定義工具規格。
- A詳: 先寫下使用者會如何做（如解題：先認識助手→問線索→讀原文→找相關），把括號內的動作抽成 Tools（GetInstructions、SearchChunks、GetPostContent、GetRelatedPosts）。再為每工具定義輸入/輸出、回覆格式（Markdown＋指示），最後串成流程並測試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q2, C-Q8

Q10: Shopify learn_shopify_api 的機制與作用？
- A簡: 強制首呼叫，回覆指示與 conversationId，後續工具無此 ID 即失敗。
- A詳: 此工具是「發現層」的守門員。回覆包含使用規則與「必帶」conversationId，確保 Agent 已讀指示且有上下文連續。此防護避免誤用、提高可控性，為接續的檢索與執行打好地基，是 MCP-first 的典範作法。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, D-Q1, B-Q11

Q11: Shopify 的 search_docs_chunks 與 fetch_full_docs 原理？
- A簡: 先用 chunks 精準檢索，再以 Markdown 取全文，減噪並提升理解。
- A詳: search_docs_chunks 利用向量檢索回傳片段（帶路徑），fetch_full_docs 再用路徑取回 Markdown 全文。以「先片段後全文」的策略控制上下文大小與語義密度，讓 Agent 能準確定位主題並逐步擴展理解，降低幻覺。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q21, A-Q22, B-Q10

Q12: Shopify 的 introspect_graphql_schema 與 validate_graphql_codeblocks？
- A簡: 先查綱目（欄位/型別），後驗代碼合法性，確保生成正確可執行。
- A詳: introspect 依查詢與過濾取得 GraphQL schema 片段，幫 Agent 明確欄位與型別。生成代碼後，validate 工具檢查語法與版本一致性。此「規劃→驗證」流程讓 Agent 可靠生成可用代碼，降低 API 幻覺與版本錯配。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, A-Q29, D-Q9

Q13: Context7 的 resolve-library-id 與 get-library-docs 原理？
- A簡: 先定位正確文件庫與版本，再依主題拉取含範例的 Markdown 資料。
- A詳: resolve-library-id 回覆候選庫的 ID、信任分數、版本等，就地提供選擇指引；get-library-docs 依 ID 與主題取回官方文件與程式範例（Markdown）。此精簡兩步法對齊「找來源→取主題→用範例」的開發流程，降低幻覺與舊資料風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, D-Q8, C-Q10

Q14: Streamable HTTP 的 MCP 連接流程？
- A簡: 在 Host 內新增 HTTP Server URL，建連後即可呼叫工具並串流回覆。
- A詳: 以 VSCode為例：MCP: Add Server→HTTP→輸入 Server URL→命名→建立。建立後可在對話中直接呼叫工具（如 /mcp GetInstructions），回覆與事件以串流形式到客端。此法讓多種 Host 無痛掛載第三方 MCP。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, D-Q5, A-Q24

Q15: Agent 使用 MCP 的一般交互步驟？
- A簡: 先讀指示→檢索片段→取全文/相關→生成或執行→必要時驗證。
- A詳: Step1：呼叫 GetInstructions/learn_shopify_api；Step2：SearchChunks 定位線索；Step3：GetPostContent/ fetch_full_docs 讀全文與 GetRelatedPosts 擴展；Step4：生成答案、解法或代碼；Step5：用驗證工具檢查（如 GraphQL validate）。此步驟鏈能提升可靠度。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q2, A-Q12, C-Q2

Q16: 如何在 VSCode 安裝 MCP Server 並呼叫工具？
- A簡: 加入 HTTP Server URL，打開對話，直接用 /mcp 工具指令呼叫。
- A詳: VSCode：F1→MCP: Add Server→HTTP→輸入 URL→命名→完成。於聊天面板輸入「/mcp GetInstructions」強制讀指示，之後自然詢問部落格相關問題，Agent 會自行選用 SearchChunks/Posts、GetPostContent、GetRelatedPosts 等工具。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, C-Q2, D-Q5

Q17: RAG 增強的「先片段後全文」流程？
- A簡: 先少量片段鎖定重點，再逐段取全文，降低視窗壓力與噪音。
- A詳: 以 SearchChunks 取 5~10 片段（FAQ、摘要、解法），確立主題與關鍵，再用 GetPostContent 指定段落取全文，必要時取相關文章。此流程符合 Context Engineering，提升生成的精度與可讀性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q21, D-Q3

Q18: CLI JSONL 平行處理（C# Channels）的技術原理？
- A簡: Producer 從 STDIN 讀 JSONL 入 Channel，Consumer 以指定平行度處理並輸出結果。
- A詳: 建立 bounded Channel<UserItem>；Producer 任務讀 STDIN 逐行反序列化寫入；多個 Consumer 以平行度 N 讀 Channel，處理單筆邏輯，輸出結果至 STDOUT。此架構比舊 BlockingCollection 更現代，控制背壓與錯誤更清晰。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, D-Q10, A-Q25

Q19: 以 Agent 執行 vibe coding 的架構？
- A簡: Agent 先檢索文章片段與原文，再生成程式框架與測試資料，使用者補業務邏輯。
- A詳: 流程為：SearchPosts 定位文章→GetPostContent 讀解法段落→SearchChunks 找示例片段→生成骨架程式與假資料（JSONL、Shell script）→使用者補每筆處理邏輯→執行驗證。此架構把知識轉為可用程式，加速上手。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, A-Q25, D-Q10

Q20: 控制 context window 的策略有哪些？
- A簡: 限量回傳、分段取用、用途標記、就地指示、必要時清理或總結。
- A詳: 具體作法：limit 控回傳數量；position/length 分段讀全文；synthesis 指定用途單元；工具回覆帶指示避免重複；必要時以總結壓縮上下文後再引入新材料。目標是避免爆量，維持重點與推理正確。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q15, D-Q3, B-Q5


### Q&A 類別 C: 實作應用類（10題）

Q1: 如何安裝並使用安德魯的 MCP Server？
- A簡: 在支援 Streamable HTTP 的 Host 加入 URL，無需 API key，即可呼叫工具。
- A詳: 步驟：1) 選 Host（VSCode/ChatGPT）；2) 新增 Server：URL https://columns-lab.chicken-house.net/api/mcp/（保留結尾斜線）；3) 在 VSCode：F1→MCP: Add Server→HTTP→輸入 URL→命名→完成；4) 開始聊天，詢問部落格主題。注意：首次可用「/mcp GetInstructions」確保讀指示。最佳實踐：先問摘要，再取全文，再問相關。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q14, C-Q2, D-Q5

Q2: 如何強制 Agent 先呼叫 GetInstructions？
- A簡: 在 Host 對話中輸入「/mcp GetInstructions」，將指示載入上下文。
- A詳: 步驟：1) 開啟聊天視窗；2) 輸入「/mcp GetInstructions」；3) 檢查回覆包含使用規則與注意事項；4) 之後再發問題。注意：某些 Host 會自動判斷，但手動呼叫更可控。最佳實踐：把指示貼近對話起點，後續檢索與生成更穩定。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q15, D-Q1

Q3: 如何用 Agent 問「微服務交易基礎知識」並取得引用？
- A簡: 先呼叫指示，再用關鍵詞查 chunks，要求回覆附標題與網址。
- A詳: 步驟：1) /mcp GetInstructions；2) 提出問題並指定關鍵詞（如「分散式交易、Saga、2PC、TCC、Outbox」）；3) Agent 會呼叫 SearchChunks（synthesis: summary/faq）；4) 要求「列出引用文章標題＋網址」。注意：limit 8~10 控噪音；必要再取全文。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q13, B-Q3, D-Q2

Q4: 如何用 VSCode+Copilot 進行 vibe writing 整理部落格演進史？
- A簡: 在對話中描述輸出格式與字數、附標題與連結，Agent 會檢索並編排。
- A詳: 步驟：1) 啟用 MCP；2) 下指令：列出系統移轉歷史（年份＋主項＋子項＋100字內＋附文章標題與連結）；3) Agent 呼叫 SearchPosts/Chunks→生成 Markdown；4) 檢視與微調。注意：指定排序與格式；最佳實踐：逐段驗收，提高準確性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, A-Q25, D-Q8

Q5: 如何用 Coding Agent 實作 CLI JSONL 平行處理（C# Channels）？
- A簡: 讓 Agent檢索文章後生成程式框架，使用 Channel 讀寫、指定平行度。
- A詳: 步驟：1) 啟 VSCode 專案（Console App）；2) 請 Agent 參考 pipeline CLI 文章；3) 生成 Channel 架構與 Producer/Consumer；4) 補 ProcessSingleItem 邏輯；5) 生成測試 JSONL與 Shell；6) 執行驗證。程式碼片段：建立 bounded Channel<UserItem>，Producer ReadFromStdin()、Consumer ReadAllAsync() 以 parallelismN 處理。注意：錯誤處理與背壓。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, D-Q10, A-Q25

Q6: 如何撰寫 SearchChunks 查詢語句以提高精準度？
- A簡: 結合主題＋術語＋同義詞，指定 synthesis 與 limit，避免過寬或過窄。
- A詳: 步驟：1) 列主題與關鍵術語（如「微服務、分散式交易、Saga、2PC、TCC、Outbox」）；2) 同義詞與英文（distributed transaction）；3) 指定 synthesis（summary/solution/faq）；4) 控制 limit（8~10）。注意：根據回覆微調 Query；必要分兩次查詢（先廣後精）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q2, A-Q11

Q7: 如何設計 synthesis 參數以獲取合用內容？
- A簡: 依目的選 summary/solution/faq 等，讓回覆即為可用單元。
- A詳: 原則：1) 快速理解用 summary；2) 準備步驟用 solution；3) 快速問答用 faq；4) 讀全文前先取摘要減噪。步驟：在 SearchChunks/Posts、GetPostContent 指定 synthesis，讓 Agent 更易組合答案或實作。注意：避免一次混太多，用分次查詢。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q2, D-Q3

Q8: 如何在 MCP Server 中設計 GetRelatedPosts？
- A簡: 以向量相似度與主題標註找相關，限制回傳數量，附標題與連結。
- A詳: 步驟：1) 為每文建立向量與主題標記；2) 以 postid 查相似文；3) 回覆 Markdown 列表（標題＋URL＋簡述）；4) 支援 limit。注意：避免重複、加入多樣性；最佳實踐：配合 chunks 回覆，形成擴展閱讀路線。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, D-Q7, A-Q21

Q9: 如何依 Shopify.Dev MCP 取得 GraphQL 代碼並驗證？
- A簡: 先 learn_shopify_api 拿 conversationId→查 chunks→取全文→生成→validate。
- A詳: 步驟：1) learn_shopify_api（保存 conversationId）；2) search_docs_chunks（主題：欲查資源）→paths；3) fetch_full_docs 讀 Markdown；4) 生成 GraphQL query/mutation；5) validate_graphql_codeblocks 驗合法性。注意：帶 API 與 version；遵循指示避免錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q11, B-Q12

Q10: 如何整合 Context7 與 Agent 生成可用程式碼？
- A簡: 先 resolve-library-id 選高信任庫與版本，再 get-library-docs 拉主題範例。
- A詳: 步驟：1) 用關鍵字查庫（resolve-library-id），依信任分數與版本選擇；2) get-library-docs（指定 topic、tokens）取回 Markdown 與代碼片段；3) 融合到對話上下文，生成程式；4) 自行測試與微調。注意：明確主題、限制 tokens、避免舊版範例。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, D-Q8, A-Q18


### Q&A 類別 D: 問題解決類（10題）

Q1: 遇到工具回覆錯誤，疑似未先讀指示怎麼辦？
- A簡: 先呼叫 GetInstructions 或 learn_shopify_api，保存必要 ID，再重試後續工具。
- A詳: 症狀：工具報錯、提示缺 conversationId 或未初始化。原因：未按流程先讀指示。解法：1) /mcp GetInstructions（或 learn_shopify_api）；2) 保存必要識別（如 conversationId）；3) 重新呼叫檢索或執行工具。預防：在工作流模板中固定首步為「讀指示」。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q19, B-Q10, C-Q2

Q2: SearchChunks 結果不精準或太多怎麼辦？
- A簡: 收斂查詢詞、指定 synthesis、降低 limit、分兩次查詢逐步精準。
- A詳: 症狀：回覆片段雜或偏題。原因：Query過寬、未指定用途、limit過大。解法：1) 加入術語與同義詞；2) 指定 synthesis（summary/faq/solution）；3) limit 8~10；4) 二階查詢（先粗再精）。預防：建立查詢模板與詞彙表。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q3, C-Q6, A-Q11

Q3: Context window 爆量導致答非所問如何處置？
- A簡: 分段取用、限量回傳、先摘要後全文、必要時以總結清理上下文。
- A詳: 症狀：回答漂移、遺漏重點。原因：一次引入過多內容。解法：1) GetPostContent 用 position/length 分段；2) SearchChunks limit 控制；3) 先 summary 再全文；4) 讓 Agent 提供總結再繼續。預防：固定流程「先片段後全文」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q17, A-Q15

Q4: GetPostContent 回傳空或 postid 無效怎麼辦？
- A簡: 檢查 postid 正確性、大小寫與路徑，改用 SearchPosts 再取全文。
- A詳: 症狀：讀全文失敗或空回覆。原因：postid 錯誤、文章不存在、位置參數不當。解法：1) 先用 SearchPosts 定位正確 postid；2) 檢查 position/length；3) 再呼叫 GetPostContent。預防：讓 Agent 以清單選文，不手寫 id。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q4, B-Q5, C-Q1

Q5: Streamable HTTP 連線失敗或 URL 斜線錯誤怎麼辦？
- A簡: 確認 URL 保留結尾斜線，Host 支援 MCP HTTP，重試加伺服器健康檢查。
- A詳: 症狀：連線建立失敗、工具不可用。原因：URL 格式錯（少結尾 /）、Host 不支援、網路阻斷。解法：1) 用正確 URL：https://columns-lab.chicken-house.net/api/mcp/；2) 檢查 Host 設定；3) 測試網路；4) 重建連線。預防：建立安裝清單與驗收步驟。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, B-Q14, A-Q24

Q6: 文章仍為 HTML 導致檢索品質差如何改善？
- A簡: 先做內容重構為 Markdown，清理路徑與連結，再向量化建立索引。
- A詳: 症狀：檢索雜訊多、片段難用。原因：HTML 格式噪音。解法：1) 用 AI IDE 批次轉 Markdown；2) 修正圖徑與連結；3) 正規化為 FAQ/solution/summary；4) 重建向量索引。預防：發布管線統一 Markdown。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q26, B-Q7, C-Q8

Q7: 相關文章找不到或不準怎麼處理？
- A簡: 改良相似度計算與標註，限制回傳數，加入多樣性與人工校準。
- A詳: 症狀：GetRelatedPosts 回覆不相關或重複。原因：向量品質或標註不足。解法：1) 增強標註與主題分類；2) 設定 limit；3) 去重與多樣性策略；4) 定期人工校準樣本。預防：建立標註規範與回測。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q8, A-Q21

Q8: Agent 幻覺生成且未引用真實文章怎麼辦？
- A簡: 要求附引用清單，先 chunks 後全文，必要時以 Context7/官方文件佐證。
- A詳: 症狀：回答自說自話、無真實引用。原因：上下文不足或資料源不清。解法：1) 明確要求「附文章標題＋URL」；2) 先用 SearchChunks 再取全文；3) 使用 Context7/Shopify 官方文件工具交叉驗證。預防：把「附引用」寫入提示模板。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q18, C-Q3, B-Q13

Q9: GraphQL 驗證失敗（Shopify）怎麼排查？
- A簡: 先 introspect schema 取欄位，再 validate codeblocks，檢查 API/version 與語法。
- A詳: 症狀：代碼不可執行或語法錯。原因：欄位不匹配、版本錯誤、語法不合。解法：1) introspect_graphql_schema 取正確綱目；2) validate_graphql_codeblocks 檢查；3) 修正版本與 API 參數；4) 重試。預防：固定「查綱目→生成→驗證」流程。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q12, C-Q9, A-Q29

Q10: CLI 平行處理效能不佳或例外頻繁如何優化？
- A簡: 調整平行度與 Channel容量，加強錯誤處理與背壓策略，優化序列化。
- A詳: 症狀：吞吐低、例外多。原因：平行度不匹配、背壓不足、序列化慢。解法：1) 以壓測調整 parallelism；2) 調整 Channel容量；3) try/catch 與錯誤重試；4) 使用高效序列化；5) 減少同步 I/O。預防：壓測基準與監控日誌。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q18, C-Q5, A-Q25


### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 MCP（Model Context Protocol）？
    - A-Q2: MCP 與傳統 API 有何不同？
    - A-Q3: 為什麼要把部落格做成 MCP？
    - A-Q4: 什麼是 Workflow First 的設計？
    - A-Q13: 部落格的四種使用情境是什麼？
    - A-Q14: 「解答」與「解題」的差異？
    - A-Q21: chunk 與 post 有何不同？
    - A-Q22: 為何偏好 Markdown 而非 HTML 提供內容？
    - A-Q24: 什麼是 Streamable HTTP（MCP 連線方式）？
    - C-Q1: 如何安裝並使用安德魯的 MCP Server？
    - C-Q2: 如何強制 Agent 先呼叫 GetInstructions？
    - C-Q3: 如何用 Agent 問「微服務交易基礎知識」並取得引用？
    - D-Q1: 遇到工具回覆錯誤，疑似未先讀指示怎麼辦？
    - D-Q5: Streamable HTTP 連線失敗或 URL 斜線錯誤怎麼辦？
    - A-Q7: 為什麼 MCP 回應常用 Markdown 而非 JSON？

- 中級者：建議學習哪 20 題
    - B-Q2: 本文部落格的 MCP Tools 規格與流程？
    - B-Q3: SearchChunks 的檢索原理與流程是什麼？
    - B-Q5: GetPostContent 如何設計與使用？
    - B-Q6: GetRelatedPosts 背後機制是什麼？
    - B-Q7: 內容預處理（LLM 生成）流程原理？
    - B-Q8: Context Management 的核心機制有哪些？
    - B-Q10: Shopify learn_shopify_api 的機制與作用？
    - B-Q11: Shopify 的 search_docs_chunks 與 fetch_full_docs 原理？
    - B-Q12: Shopify 的 introspect_graphql_schema 與 validate_graphql_codeblocks？
    - B-Q13: Context7 的 resolve-library-id 與 get-library-docs 原理？
    - A-Q12: MCP Tools 設計有哪些原則？
    - A-Q15: 什麼是 Context Engineering？
    - A-Q18: Context7 MCP 的定位與特色是什麼？
    - A-Q29: 「發現/規劃/執行」分層有何價值？
    - C-Q6: 如何撰寫 SearchChunks 查詢語句以提高精準度？
    - C-Q7: 如何設計 synthesis 參數以獲取合用內容？
    - C-Q8: 如何在 MCP Server 中設計 GetRelatedPosts？
    - D-Q2: SearchChunks 結果不精準或太多怎麼辦？
    - D-Q3: Context window 爆量導致答非所問如何處置？
    - D-Q8: Agent 幻覺生成且未引用真實文章怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q23: MCP 在未來 SaaS 生態中的角色？
    - A-Q8: MCP-first 與 API-first 的差異？
    - B-Q1: MCP Server 整體如何運作？
    - B-Q17: RAG 增強的「先片段後全文」流程？
    - B-Q18: CLI JSONL 平行處理（C# Channels）的技術原理？
    - B-Q19: 以 Agent 執行 vibe coding 的架構？
    - B-Q20: 控制 context window 的策略有哪些？
    - C-Q5: 如何用 Coding Agent 實作 CLI JSONL 平行處理（C# Channels）？
    - C-Q9: 如何依 Shopify.Dev MCP 取得 GraphQL 代碼並驗證？
    - C-Q10: 如何整合 Context7 與 Agent 生成可用程式碼？
    - D-Q9: GraphQL 驗證失敗（Shopify）怎麼排查？
    - D-Q10: CLI 平行處理效能不佳或例外頻繁如何優化？
    - A-Q27: 何謂「對 Agent 友善」的 MCP 設計要點？
    - A-Q30: 為何將知識庫轉為 FAQ/Solutions 有價值？
    - A-Q16: 為什麼「為了技術而技術」是錯誤方向？