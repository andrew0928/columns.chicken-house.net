---
layout: synthesis
title: ".NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用"
synthesis_type: faq
source_post: /2025/06/22/inside-semantic-kernel/
redirect_from:
  - /2025/06/22/inside-semantic-kernel/faq/
---

# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 Chat Completion API？
- A簡: 以對話歷史為輸入，產生下一步回應的生成式 API，支援角色、參數、工具與格式控制。
- A詳: Chat Completion 是主流 LLM 的通用對話介面。呼叫端將 messages（含 system、user、assistant 等角色）與模型參數（如 model、temperature）一併送出，模型回傳下一步回應。多輪對話即重複「歷史訊息＋新問題」的往返。進階還可啟用 tools（函數調用）與 response_format（JSON Mode/Schema），讓回答更可控、可結構化並可觸發外部動作。此 API 是構建聊天機器人、Agent、RAG 與工作流程自動化的基石。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, B-Q5

A-Q2: Chat Completion 中常見的角色（role）有哪些？
- A簡: system 設定規則，user 提問，assistant 回答；含工具用的 tool 與 tool-result。
- A詳: 角色決定訊息語義與優先權。system 為對話全局規則與行為約束；user 為使用者輸入；assistant 是模型對使用者的可見回覆。啟用工具後，assistant 還可攜帶 tool_calls 要求呼叫特定函數；tool 則是外部系統回寫的執行結果（又稱 tool-result）。這些角色共同構成三方對話，支持規則設定、問題提出、工具調用與最終回覆。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q9, B-Q7

A-Q3: 什麼是 Context Window（上下文視窗）？
- A簡: 模型一次可讀取的對話上下文容量，以 token 計，影響記憶與成本。
- A詳: Context Window 定義模型一次能處理的 tokens 上限，包含提示、對話歷史、工具輸出與引用片段。視窗越大，可讀歷史越多，但費用與延遲也上升。設計時需取捨：關鍵歷史摘要化、插入必要引用、避免冗長與重複。對 RAG 而言，挑選最相關片段餵入是關鍵；對 Function Calling 而言，保留工具規格與近期狀態尤為重要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q11, D-Q7

A-Q4: Temperature 是什麼？為什麼重要？
- A簡: 控制隨機度的參數。低溫穩定、可重現；高溫多樣、具創意。
- A詳: temperature 決定模型取樣的發散程度。0~0.3 偏確定性，適合程式碼、事實、工具參數；0.7 以上鼓勵創意表達。RAG 與 Function Calling 多採低溫確保可重現與格式穩定；生成文案、腦力激盪可提高溫度。實務可搭配 top_p、presence_penalty 微調。不同任務可分流至不同溫度的子步驟以兼顧準確與創意。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q5, C-Q2, D-Q1

A-Q5: 什麼是 Structured Output（JSON Mode）？
- A簡: 要求模型依指定結構（常用 JSON/Schema）輸出，利於程式解析與驗證。
- A詳: Structured Output 讓模型按照既定格式回覆，常見為 JSON 物件並搭配 Json Schema 限定欄位、型別與必填性。優點：可直接反序列化為物件，降低解析成本；能加上成功/失敗旗標與錯誤碼，提升健壯性；與 Function Calling 搭配時，可穩定產出函數參數。此能力使 LLM 能以「可靠介面」嵌入系統流程。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, B-Q5, C-Q2

A-Q6: JSON Schema 在 LLM 應用中的角色是什麼？
- A簡: 定義輸出資料契約，限制欄位型別與規則，提升可控性與可驗證性。
- A詳: JSON Schema 是結構化輸出的契約，描述欄位型別、必要欄位、枚舉、格式（如 email/uri）與巢狀結構。應用上可內含 success、errors、reason 等欄位，避免以文字猜測執行狀態；也可對工具參數施加嚴格限制防止誤動作。搭配 SDK 可自動生成/驗證，確保上下游系統協作穩定。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q6, D-Q1

A-Q7: 為什麼開發者應選擇 JSON 輸出而非純文字？
- A簡: 可機器處理、可驗證、易除錯；降低幻覺風險，利於流程編排與擴充。
- A詳: 純文字回答友善人類但不利機器；JSON 輸出可直接反序列化、檢查必填欄位、判定成功與錯誤，與非 AI 程式無縫銜接。對成本也有益：可把能用程式完成的工作從 LLM 移出，將 LLM 限縮在不可替代的推理任務上。長期可降低錯誤率、加速開發與維運，提升系統可靠性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q5, D-Q1

A-Q8: Structured Output 與 Function Calling 有何差異？
- A簡: 前者管「輸出格式」，後者管「可用工具與呼叫流程」，常互補使用。
- A詳: Structured Output 聚焦回答的結構化與可驗證性；Function Calling 則讓模型選擇並呼叫外部函數、接收結果後續推理。兩者可結合：用 JSON Schema 穩定產出工具參數；用工具回傳結構化結果再整合為最終回覆。前者像資料契約，後者像行為介面，聯手構成 Agent 能力。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q9, B-Q7

A-Q9: 什麼是 Function Calling（工具使用）？
- A簡: 讓模型按需呼叫外部函數/服務，取回結果後再推理或完成任務。
- A詳: 在對話開始宣告可用的工具（名稱、描述、參數結構）。模型在推理過程判斷是否需要工具，產生 tool_calls（含函數名與參數），宿主程式執行後回填 tool 結果。模型可多輪交替「呼叫→觀察→決策」，直到可以給出最終回答。這使 LLM 能協同各系統，落實自動化與工作流編排。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q2, B-Q7, C-Q4

A-Q10: 為什麼需要 Function Calling？
- A簡: 讓 LLM 取用即時資料與動作能力，超越純生成，實作可執行的智能代理。
- A詳: 僅靠語言模型無法存取最新資料、內網系統或執行具副作用的操作。Function Calling 解鎖「觀察世界與作用於世界」的能力，常見於排程、查庫、下單、查天氣/地點等任務。它也是多工具協作（含規劃與回饋）的基礎，與 RAG、Workflow、Agent 框架相互促成。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q9, C-Q5

A-Q11: tool 與 tool-result 在對話中各扮演什麼角色？
- A簡: tool_calls 是模型的呼叫意圖；tool 是宿主執行後回填的結果訊息。
- A詳: assistant 帶著 tool_calls 代表「需要執行哪個工具與參數」；宿主程式收到後實際執行並以 role=tool 回寫結果與同一 id 對應。模型看到結果再決定下一步：追加工具、或轉為最終回答。此三方回合構成可觀察、可調試、可追溯的執行序列。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5, D-Q3

A-Q12: 什麼是 RAG（檢索增強生成）？
- A簡: 先檢索相關內容，再把結果餵入模型生成答案，確保即時與可引用。
- A詳: RAG 解耦了「知識持有」與「語言生成」。流程含：問題收斂/改寫→檢索（向量庫/搜尋引擎）→重排序→組裝提示（含引用）→生成回答。優勢：資料可更新、可控來源、合規可追溯。是企業將自身知識帶入 LLM 的主流做法。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q11, C-Q6

A-Q13: 為什麼需要 RAG，而非只依賴模型訓練知識？
- A簡: 訓練知識滯後且不可控；RAG 提供新鮮、可引用、可管理的企業知識。
- A詳: 通用模型訓練資料有時效落差、版權與錯誤風險，也難以納入私有知識。RAG 讓知識獨立管理與更新，以檢索引用方式融入生成。它降低幻覺、合規可追溯、維運更靈活，總體成本也更佳。必要時再搭配微調形成混合策略。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q11, B-Q25, D-Q9

A-Q14: RAG 與向量資料庫的關係是什麼？
- A簡: 向量庫儲存向量化片段並以相似度檢索，是 RAG 的核心基礎設施。
- A詳: 文檔先經 chunking，再以 Embedding 模型轉成向量，連同原文與中繼資料寫入向量庫。查詢時，把問題轉向量，在庫中找最相似片段回傳。此過程決定檢索相關性與召回率，直接影響最終回答品質。也可混用全文檢索與重排序提升精度。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q12, B-Q13, C-Q6

A-Q15: 什麼是 Semantic Kernel（SK）？
- A簡: 微軟開源的 .NET AI 應用框架，整合 LLM、工具、記憶、插件與工作流。
- A詳: SK 提供 Kernel 作為中樞，統一管理模型連接、工具（插件）、記憶（向量存取）、規劃與執行流程。它支持多家 LLM/Embedding 供應商、Swagger 注入工具、與 MSKM 深度整合。對 .NET 開發者，SK 兼顧抽象與擴展性，是構建 Agent/RAG 的首選框架之一。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, B-Q8, C-Q9

A-Q16: 什麼是 Microsoft Kernel Memory（MSKM）？
- A簡: 微軟開源的 RAG 服務，提供文件管線、向量化、儲存、查詢與 SK 插件。
- A詳: MSKM 聚焦長期記憶與 RAG。它具文件匯入管線（抽取、分段、標籤、向量化、儲存）、查詢 API、與可替換的 AI/DB 連接器。可部署為獨立 Web 服務或嵌入應用。並內建 SK Memory 插件，讓模型能以 Function Calling 操控知識庫。是 .NET 生態中可擴展、可編排的 RAG 中樞。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, B-Q14, B-Q15

A-Q17: MSKM 與 SK 的差異與互補？
- A簡: SK 是應用框架；MSKM 是 RAG 服務。前者編排 AI 流程，後者管理知識。
- A詳: SK 提供 Kernel、插件、規劃與多模型抽象，適合撰寫 Agent 與工作流。MSKM 專注於文件處理管線、向量化/儲存與查詢，負責長期記憶。兩者協作：用 SK 建構對話與工具調用，把 MSKM 插為記憶工具；或由 MSKM 作為後端服務，SK/其他客端統一檢索增強。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, B-Q16, C-Q6

A-Q18: 什麼是「RAG as a Service」？
- A簡: 以獨立 Web/雲服務提供 RAG 能力，外部以 API 存取與擴充。
- A詳: 將匯入、向量化、儲存、檢索等職責封裝成可部署服務（如 MSKM），用戶以 SDK/HTTP 存取。好處：跨語言、可水平擴展、責任清晰、維運集中。亦可選擇嵌入式模式於單機應用內運作。此服務化有利於把 RAG 視為平台能力與組織資產。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q6, D-Q8

A-Q19: 文檔處理管線（Ingestion Pipeline）是什麼？
- A簡: 從抽取、分段、標籤、向量化到儲存的一連串可插拔步驟。
- A詳: 典型步驟為：內容抽取（PDF/OCR/HTML→純文字）、清理正規化、分段（長度/重疊/語意）、中繼資料標注（來源、語言、主題）、Embedding 轉向量、寫入向量庫/索引。後續可擴展摘要、FAQ 生成、品質檢查與審計。MSKM 提供可客製的 Handler 與連接器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15, B-Q13, C-Q7

A-Q20: 什麼是 Chunking？為何重要？
- A簡: 將長文切成檢索友善的片段，兼顧涵蓋與語意完整，提高召回與精度。
- A詳: Chunk 過短失資訊、過長稀釋語意。常見策略：固定長度（含重疊）、句段/標題感知、語意分段、混合策略。對中文需注意切詞與字元長度。搭配段落摘要、關鍵詞補充，可彌補視角落差（問題 vs 作者視角）。良好 Chunking 直接決定 RAG 表現上限。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, C-Q7, D-Q5

A-Q21: 什麼是「生成檢索專用內容」（Synthesis for RAG）？
- A簡: 先用 LLM 產生摘要/FAQ/案例等視角內容，再入庫提升檢索對齊。
- A詳: 許多原文以作者視角書寫，與使用者提問語式不一致。先離線生成整體摘要、段落摘要、FAQ（Q/A）、解決方案（問題/原因/修復），並打上類型標籤，使查詢能更準確匹配。成本僅在匯入時支付，換得顯著精度提升，特別適用長文與知識密集領域。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q18, C-Q8, D-Q4

A-Q22: 什麼是 MCP（Model Context Protocol）？
- A簡: LLM 與外部工具/資源互通的開放協定，標準化工具列舉與呼叫。
- A詳: MCP 規範了 initialize、tools/list、tools/call、resources/list 等 JSON-RPC 介面，並定義傳輸通道（stdio、SSE/HTTP）。任何語言都可實作 MCP Server 提供工具，MCP 客端（如 Claude Desktop）統一探索與呼叫。它是工具互通的「AI 版 USB-C」，便於跨生態整合。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q21, B-Q22, C-Q10

A-Q23: 什麼是「土炮 Function Calling」？何時適用？
- A簡: 在不支援工具的模型上，以規則化前綴與回合控制模擬工具調用。
- A詳: 透過 System Prompt 自訂對話規則，例如以「請執行指令：」開頭代表工具請求；宿主攔截並執行，再把結果當下一輪歷史回寫。雖不如原生工具穩健，但推理夠強的模型仍可運作。適用於 API 不支援工具、或臨時實驗；正式產品仍建議用原生機制與框架。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q23, C-Q4, D-Q2

A-Q24: 為何強調單一職責與成本意識？
- A簡: 讓 LLM 做「不可替代的推理」，其餘交給程式/服務，控錯控費控風險。
- A詳: 搜尋、格式轉換、數值計算、規則校驗等由程式更快更便宜更穩定。把任務拆分：LLM 負責理解、判斷、規劃、歧義消解；工具/程式負責可確定的執行。另以 JSON 輸出與錯誤旗標協作，提升可監控性。此架構能將單次決策放大百萬倍仍可控。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q19, D-Q10


### Q&A 類別 B: 技術原理類

B-Q1: Chat Completion 的 HTTP 請求與回應如何運作？
- A簡: 送出 model、messages、參數（可含 tools/format），回傳 choices 與 usage。
- A詳: 技術原理說明：以 POST 包含 headers（認證）、body（model、temperature 等）與 messages（role+content），可選 tools 與 response_format。關鍵步驟或流程：1) 準備對話歷史與新訊息；2) 設定模型與參數；3) 發送請求；4) 解析 choices[0].message；5) 追加至歷史再進入下一回合。核心組件介紹：HTTP 客戶端、序列化器、重試/超時、日誌與費用計量（usage.tokens）。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, C-Q1, D-Q8

B-Q2: 在 .NET 用 HttpClient 呼叫 Chat Completion 的步驟？
- A簡: 建 JSON、設 Header、POST、讀回 choices，再更新對話歷史循環。
- A詳: 技術原理說明：以 HttpClient 設 Authorization: Bearer、Content-Type: application/json；序列化請求物件。關鍵步驟或流程：1) 定義 messages；2) 設定 model、temperature；3) HttpClient.PostAsync；4) 解析 choices[0].message；5) 將回覆加入歷史。核心組件介紹：HttpClient、JsonSerializer、POCO 請求/回應模型、Token 計費解析、錯誤/重試策略。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, A-Q2, D-Q8

B-Q3: 用 OpenAI .NET SDK 實作簡單對話原理？
- A簡: 以 SDK 封裝請求模型，建立客戶端並呼叫 Chat，簡化序列化與錯誤處理。
- A詳: 技術原理說明：SDK 抽象了 HTTP 細節，提供 Chat API 的強型別介面與模型常數。關鍵步驟或流程：1) 建立 OpenAIClient；2) 構建 ChatCompletionsOptions（messages/params）；3) 調用 GetChatCompletionsAsync；4) 取 choices.First().Message。核心組件介紹：OpenAIClient、ChatMessage、ChatCompletionsOptions、流式回應（若支持）、重試與策略配置。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q1, A-Q1, A-Q4

B-Q4: 在 Semantic Kernel 實作簡單 Chat 的設計？
- A簡: 用 Kernel 管理模型與插件，通過 ChatService 送入歷史並取得回覆。
- A詳: 技術原理說明：SK 抽象不同模型供應商，提供 ChatCompletionService 與 PromptTemplate 系統。關鍵步驟或流程：1) 建 Kernel 並註冊模型；2) 建 ChatHistory 加入 system/user；3) 調用 chat.GetChatMessageContentAsync；4) 反覆追加對話。核心組件介紹：Kernel、IChatCompletionService、PromptTemplate、ChatHistory、插件（Functions）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q3, B-Q8

B-Q5: JSON Mode 如何強制結構化輸出？
- A簡: 設定 response_format 或在 SDK 指定 JSON Schema，模型依契約生成。
- A詳: 技術原理說明：在請求中指定 response_format（type=json_object 或 json_schema）並提供 schema；部分 SDK 可由型別推導。關鍵步驟或流程：1) 定義 Schema（含必填、枚舉）；2) 於請求指定；3) 回傳後用 JSON Schema 驗證；4) 反序列化。核心組件介紹：Schema 定義器、Validator、反序列化器、錯誤處理（重試/回退提示）。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q6, C-Q2

B-Q6: 設計 JSON Schema 的關鍵原則是什麼？
- A簡: 明確欄位、必填/選填、型別、枚舉，加入 success 與 error 欄位。
- A詳: 技術原理說明：Schema 是契約，應防止模稜兩可。關鍵步驟或流程：1) 釐清下游需求；2) 建立必要欄位、型別、格式；3) 設計錯誤語意（success、reason、codes）；4) 加範例與單元測試。核心組件介紹：JSON Schema 草案版本、格式驗證器、產生器（由 C# type 生成）與相容性測試。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q1, C-Q2

B-Q7: Function Calling 的回合機制如何運作？
- A簡: assistant 送出 tool_calls，宿主執行回寫 tool，模型再決策下一步。
- A詳: 技術原理說明：三方回合（模型/宿主/使用者）循環，直到模型產出可見回答。關鍵步驟或流程：1) 宣告工具規格；2) 模型判斷要用工具並產生參數；3) 宿主執行並回寫 tool 結果；4) 模型觀察結果，迭代或收斂。核心組件介紹：工具描述（name/desc/params）、對話歷史管理、工具執行器、錯誤與重試策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q11, C-Q5

B-Q8: 如何在 SK 定義並註冊 Plugin/Function？
- A簡: 以原生方法或 Swagger 匯入工具，註冊至 Kernel 供模型選用。
- A詳: 技術原理說明：SK 支援 Native Functions（C# 方法）、或以 OpenAPI/Swagger 自動產生工具介面。關鍵步驟或流程：1) 寫 C# 方法/提供 OpenAPI 描述；2) Kernel.ImportPlugin；3) 在 Chat 流程啟用工具；4) 處理工具輸入/輸出。核心組件介紹：Kernel、Plugins、Function Invocation Pipeline、輸入輸出序列化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, C-Q9, A-Q15

B-Q9: 多步驟依賴的工具鏈如何規劃？
- A簡: 透過模型推理規劃順序，逐步「呼叫→觀察→決策」直到達成目標。
- A詳: 技術原理說明：模型可根據工具結果動態改變路徑，形成人在回圈的自動化規劃。關鍵步驟或流程：1) 明確目標與工具說明；2) 讓模型能觀察中間結果；3) 設停止條件與最大步數；4) 記錄每步以利除錯。核心組件介紹：對話歷史、工作記錄器、規劃提示、保護欄（Guardrails）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q10, C-Q5, D-Q2

B-Q10: 如何檢測工具呼叫失敗與重試策略？
- A簡: 以結構化成功旗標、錯誤碼、例外攔截與退避重試機制。
- A詳: 技術原理說明：工具輸出應包含成功/失敗與錯誤細節；宿主層監控例外與狀態碼。關鍵步驟或流程：1) 規範工具輸出；2) 捕捉與分類錯誤（暫時/永久）；3) 指數退避重試；4) 人工回退或替代路徑。核心組件介紹：重試策略（Polly 等）、遙測/告警、審計日誌、死信隊列。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q2, D-Q8, A-Q7

B-Q11: RAG 的整體執行流程與組件？
- A簡: 問題收斂→檢索→重排→擴充提示→生成，依賴向量庫與管線。
- A詳: 技術原理說明：RAG 將知識外部化並按需引用。關鍵步驟或流程：1) Query Reformulation；2) 檢索（k 值、過濾）與可能的 Re-Rank；3) Construct Prompt（任務規則、來源節錄、引用格式）；4) 生成答案；5) 追加來源。核心組件介紹：Embedding 模型、向量庫、Re-Ranker、提示模板、審核與評估工具。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, B-Q12, C-Q6

B-Q12: 向量化與相似度檢索的原理？
- A簡: 將文字映成向量空間，以餘弦/內積衡量語意相近並檢索前 k 個。
- A詳: 技術原理說明：Embedding 模型將字串映射至高維向量；相似度以 cosine/inner product；向量索引（HNSW、IVF）加速近似最近鄰。關鍵步驟或流程：1) 清理文本；2) 分段；3) 向量化；4) 寫入索引；5) 查詢向量→取 top-k。核心組件介紹：Embedding 模型、向量索引、維度配置、精召取捨與記憶體/儲存成本。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q13, D-Q10

B-Q13: Chunking 策略比較：固定長度、重疊、語意切分？
- A簡: 固定長度穩定、重疊補上下文、語意切分更貼題但成本高。
- A詳: 技術原理說明：不同策略影響片段語意完整與召回。關鍵步驟或流程：1) 選定基本長度（依模型最佳 token）；2) 依需要加重疊（如 10–20%）；3) 對章節/標題/句子做語意切分；4) 混合策略並驗證。核心組件介紹：Tokenizer、句法分段器、語意分段器、實驗框架與評估指標（Precision/Recall）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q20, D-Q5, C-Q7

B-Q14: MSKM 架構：服務模式與嵌入模式？
- A簡: 可部署為 Web 服務或嵌入程式；共用管線與連接器。
- A詳: 技術原理說明：MSKM 以獨立服務呈現 RAG 能力，也可當內嵌庫。關鍵步驟或流程：1) 服務模式：以 SDK/HTTP 匯入與檢索；2) 嵌入模式：直接在應用內執行管線；3) 均可配置 AI/DB。核心組件介紹：匯入管線 Handlers、Embedding/LLM 連接器、向量儲存、查詢 API、SK 插件支援。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q16, C-Q6, D-Q5

B-Q15: MSKM 文件匯入 Pipeline 的各 Handler 作用？
- A簡: 抽取→清理→分段→標籤→向量化→儲存；可插拔擴充摘要等。
- A詳: 技術原理說明：Pipeline 將非結構化資料轉成可檢索結構。關鍵步驟或流程：1) Content Extraction（PDF/OCR/HTML）；2) Normalize/Cleanup；3) Chunking；4) Metadata Tagging；5) Embedding；6) Persist。核心組件介紹：Handlers（可自訂）、連接器（OpenAI/Azure/本地）、向量庫（多種選擇）、任務佇列與重試。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, C-Q7, C-Q8

B-Q16: 如何將 MSKM 作為 SK 的 Memory Plugin 使用？
- A簡: 以 MSKM 提供的 NuGet 插件掛入 SK，讓模型透過工具存取知識。
- A詳: 技術原理說明：MSKM 提供符合 SK 插件介面的包，Kernel 可直接導入。關鍵步驟或流程：1) 安裝 MSKM SDK/插件；2) Kernel.ImportPlugin(MSKM)；3) 在 Chat 啟用工具使用；4) 設定索引、過濾與來源回傳。核心組件介紹：Kernel、MSKM Plugin、工具規格、檢索參數（k、filter、fields）。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q17, C-Q9, D-Q4

B-Q17: 如何在 RAG 中混用外部搜尋（如 Bing）與 MSKM？
- A簡: 以多工具檢索，模型協調使用，最後彙整引用與答案。
- A詳: 技術原理說明：透過 SK 將 Bing 與 MSKM 都註冊為工具，模型按任務情境先查位置/天氣，再查內部知識。關鍵步驟或流程：1) 定義兩類工具；2) 模型工具選擇與參數抽取；3) 聚合與去重；4) 統一回答與引用。核心組件介紹：多工具路由、聚合器、引用渲染器、速率與配額管理。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9, A-Q12, B-Q9

B-Q18: 為何「內容綜合」能提升 RAG 精度？
- A簡: 將作者視角轉換為問題/摘要等使用者視角，改善語意對齊與召回。
- A詳: 技術原理說明：查詢多以問題視角，直接向量化原文常不對齊。先離線生成摘要、FAQ、案例與標籤，提高檢索表達能力。關鍵步驟或流程：1) 批次生成多視角文件；2) 寫入索引；3) 查詢時適配視角；4) 實測調參。核心組件介紹：LLM（可用高推理模型）、生成任務框架、索引更新策略、評估報表。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21, C-Q8, B-Q25

B-Q19: Token/成本估算與優化策略？
- A簡: 估計提示與生成用量，透過摘要、壓縮與分流降低成本。
- A詳: 技術原理說明：成本≈（提示+輸出）tokens×單價。關鍵步驟或流程：1) 監測 usage；2) 壓縮對話歷史與引用；3) 分流任務：推理給 LLM，規則交程式；4) 批次處理與快取。核心組件介紹：Token 計數器、壓縮/摘要器、緩存層、成本儀表板。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q24, D-Q10, C-Q8

B-Q20: 如何降低幻覺與提升可追溯性？
- A簡: 強化規則、引用來源、失敗就拒答、限制生成範圍與風險。
- A詳: 技術原理說明：RAG 的核心是「以引用為準」。關鍵步驟或流程：1) 提示要求僅據引用回答；2) 無充分證據則拒答；3) 回傳來源 URL；4) 對關鍵數據用工具驗證。核心組件介紹：Guardrails、Citation 渲染、來源白名單、反事實檢查與審計日誌。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: D-Q9, A-Q12, C-Q9

B-Q21: MCP 通訊流程：initialize、tools/list、tools/call？
- A簡: 先初始化，再列舉工具，呼叫工具回傳結果，皆透過 JSON-RPC。
- A詳: 技術原理說明：MCP 定義標準 JSON-RPC 訊息。關鍵步驟或流程：1) initialize（通報協定版本、能力）；2) tools/list（可用工具）；3) tools/call（帶參數）→返回 result；4) 可選 resources/list 等。核心組件介紹：MCP Server/Client、傳輸通道（stdio/SSE）、序列化器、錯誤/事件通知。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q22, C-Q10, D-Q6

B-Q22: MCP 的 stdio 與 SSE 傳輸差異？
- A簡: stdio 走本機管道，簡單低延遲；SSE 為 HTTP 單向串流，便於網路部署。
- A詳: 技術原理說明：兩種通道都承載 JSON-RPC。關鍵步驟或流程：1) stdio：主機程序啟子程序以 stdin/stdout 通訊；2) SSE：以 HTTP 長連線單向推播，常見雲端環境。核心組件介紹：進程生命週期、連線管理、心跳/重連、字元編碼處理（特別是多語言）。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q21, D-Q6, C-Q10

B-Q23: 不支援工具的模型如何實現「土炮」工具調用？
- A簡: 以前綴約定訊號並由宿主解析執行，回填結果入歷史。
- A詳: 技術原理說明：以提示工程規範角色與訊號詞，模型輸出「請執行指令：...」。關鍵步驟或流程：1) 設定對話規則；2) 偵測前綴；3) 宿主執行對應函式；4) 回寫執行結果；5) 迭代至完成。核心組件介紹：前綴解析器、對話狀態機、參數校驗器、最大步數與超時。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q23, C-Q4, D-Q2

B-Q24: 工具安全與權限：如何保護敏感操作？
- A簡: 以 OAuth/OpenAPI 定義邊界，白名單、審計與最小權限。
- A詳: 技術原理說明：工具是副作用入口，需零信任防護。關鍵步驟或流程：1) OpenAPI 明確規格與範圍；2) OAuth/OIDC 驗證；3) 參數與輸出白名單；4) 行為審計與速率限制；5) 人審門檻。核心組件介紹：API Gateway、秘密管理、審計日誌、策略引擎（ABAC/RBAC）。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: D-Q2, D-Q8, A-Q24

B-Q25: 如何評估 RAG 品質（Retrieval/Answer/End-to-End）？
- A簡: 分層評估：召回/精度、回答正確性、整體任務成功率與引用品質。
- A詳: 技術原理說明：把問題拆層評測以定位瓶頸。關鍵步驟或流程：1) Retrieval：nDCG、Recall@k；2) Answer：EM/F1、人工評審；3) E2E：Task Success、來源引用正確性；4) A/B 與回歸測試。核心組件介紹：標註數據集、評測腳本、審核工具、儀表板。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q13, B-Q18, D-Q4

B-Q26: SK 與 No-Code 平台（如 Dify、n8n）如何選擇？
- A簡: No-Code 快速落地；SK 彈性可維運。規模、控制與團隊能力決定。
- A詳: 技術原理說明：No-Code 提供可視化工作流、內建工具與託管；SK 提供程式級可控、型別安全與深度整合。關鍵步驟或流程：1) 需求盤點（速度 vs 可控）；2) PoC 快速用 No-Code；3) 長期核心能力轉入 SK；4) 雙軌並行。核心組件介紹：插件生態、部署模式、監控與測試框架、成本與授權。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, C-Q9, D-Q10


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何以 HttpClient 實作最小 Chat Completion？
- A簡: 準備 messages 與參數，POST 到 /v1/chat/completions，解析 choices。
- A詳: 具體實作步驟：1) 建立 HttpClient 與 Bearer Token；2) 定義匿名物件 {model, messages, temperature}；3) 序列化為 JSON；4) PostAsync；5) 解析 choices[0].message。關鍵程式碼片段或設定：
  var req = new { model="gpt-4o-mini", messages=new[]{ new{role="system",content="..."} , new{role="user",content="..."}}, temperature=0.2 };
  var res = await http.PostAsJsonAsync(url, req);
  var json = await res.Content.ReadAsStringAsync();
- 注意事項與最佳實踐：設定超時/重試、記錄 usage、封裝 POCO 型別與錯誤處理。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q2, D-Q8

C-Q2: 如何用 JSON Mode 抽取地址並反序列化為 C# 物件？
- A簡: 定義 Json Schema，要求結構輸出，回傳後驗證並反序列化。
- A詳: 具體實作步驟：1) 定義 Schema（street_address/city/postal_code/country）；2) 請求中設 response_format=json_schema；3) 回傳後以 Schema 驗證；4) JsonSerializer.Deserialize<Address>(); 片段：
  var options = new ChatOptions { ResponseFormat = JsonSchema(schema) };
  var reply = await client.ChatAsync(prompt, options);
- 注意事項與最佳實踐：加入 success 欄位；對空值/不確定以 null 表示；必要時重試或降級手工解析。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q5, D-Q1

C-Q3: 如何在 Semantic Kernel 以 C# 型別直出結構化結果？
- A簡: 以 SK 的型別映射與 JSON 模式，直接反序列化為目標型別。
- A詳: 具體實作步驟：1) 定義 C# record Address；2) 以 SK 設定 JSON 輸出綁定；3) 呼叫 chat 並讓 SK 轉為 Address；程式碼片段（概念）：
  var result = await chat.GetStructuredAsync<Address>(history, schemaFromType: true);
- 注意事項與最佳實踐：為欄位加上說明/範例；加入布林 success 與 error 訊息；對版本升級保留相容欄位。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, A-Q7

C-Q4: 如何在 Chat 中實作購物清單的基本 Function Calling？
- A簡: 宣告 add/delete 工具，讓模型輸出指令序列，再由程式執行。
- A詳: 具體實作步驟：1) 定義工具 specs（名稱、描述、參數）；2) 啟用 tools；3) 監聽 assistant.tool_calls；4) 宿主依序執行並以 role=tool 回填；5) 模型彙整回答。關鍵程式碼片段：
  if (msg.ToolCalls != null) foreach(var t in msg.ToolCalls){ var r=Exec(t); history.AddToolResult(t.Id,r); }
- 注意事項與最佳實踐：加成功旗標、錯誤處理與最大步數；保留審計記錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q8, A-Q9

C-Q5: 如何實作排程助理（check_schedule/add_event）的多輪工具使用？
- A簡: 讓模型先查空檔再下訂，回填每步結果，直到回覆人類可讀訊息。
- A詳: 具體實作步驟：1) 定義 check_schedule 與 add_event；2) 啟用工具；3) 觀察第一次 tool_calls（查時間段）；4) 執行並回寫列出時段；5) 等待第二次 tool_calls（新增事件）；6) 成功後 assistant 回覆。關鍵程式碼：同 C-Q4，但包含多輪與狀態管理。
- 注意事項與最佳實踐：處理時區、衝突檢測、權限；避免無限迴圈。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q9, D-Q3

C-Q6: 如何部署 MSKM Docker 並以 SDK 建立索引？
- A簡: 拉取官方映像啟動，配置 AI/DB，使用 SDK 匯入文件與查詢。
- A詳: 具體實作步驟：1) docker pull kernelmemory:stable；2) docker run -e OPENAI_KEY=... -p 8080:8080；3) 以 NuGet SDK 呼叫 Import/Query API；4) 驗證檢索。關鍵設定：AI 供應商、Embedding 模型、向量庫連線。
- 注意事項與最佳實踐：版本選擇（中文 chunking 請避開有缺陷的版本）、資源限制、資料卷持久化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, B-Q15, D-Q5

C-Q7: 如何把 Markdown 部落格匯入 MSKM 並加上標籤？
- A簡: 先抽取純文與中繼資料，再以自訂 Handler 或前置處理附加 tags。
- A詳: 具體實作步驟：1) 解析 front-matter（title/tags/date）；2) 萃取正文；3) 送入 MSKM Import（附 metadata: source/url/topic）; 4) 設定 chunking。程式碼片段：await mskm.ImportAsync(new Document{ Content=text, Tags={ "type:blog","topic:RAG"}});
- 注意事項與最佳實踐：移除導覽/程式碼區塊噪音、保留來源 URL、語言標籤、長文分段策略。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q19, B-Q13, D-Q4

C-Q8: 如何用 SK 先生成摘要/FAQ/案例再寫入 MSKM？
- A簡: 以 LLM 批次生成多視角內容，附類型標籤後向量化入庫。
- A詳: 具體實作步驟：1) 用高推理模型生成 abstract、paragraph-abstract、FAQ、解決方案；2) 為每類加 tags（view:summary/faq/solution）；3) 調用 MSKM 匯入 API；4) 查詢時偏好相應類型。程式碼片段：var faq = await chat.GetStructuredAsync<List<QA>>(...); await mskm.ImportAsync(faqDoc);
- 注意事項與最佳實踐：控制長度、去除重複、審核敏感資訊、建立評測集。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q21, B-Q18, D-Q4

C-Q9: 如何在 SK 串接 Bing Search 與 MSKM 進行混合 RAG？
- A簡: 同時匯入兩種工具，讓模型按情境選擇，最後合併引用與回答。
- A詳: 具體實作步驟：1) ImportPlugin(Bing)、ImportPlugin(MSKM)；2) 提示強化「需列出來源 URL」；3) 監聽工具呼叫順序；4) 合併結果並去重；5) 回答時呈現來源清單。程式碼片段：kernel.ImportPlugin(bing); kernel.ImportPlugin(mskm); await chat.InvokeAsync(...);
- 注意事項與最佳實踐：限速與錯誤隔離；對外資訊與內部知識不同權重或優先。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q17, B-Q20, D-Q10

C-Q10: 如何用 MCP C# SDK 封裝 MSKM 為 MCP Server 並接 Claude？
- A簡: 實作 tools/list/call 代理 MSKM 查詢，透過 stdio/SSE 暴露給客端。
- A詳: 具體實作步驟：1) 建 MCP Server 專案；2) 定義 search 工具（query/limit）；3) tools/call 內呼 MSKM Query API；4) 回傳 JSON 結果；5) 用 Claude Desktop 連接並測試。程式碼片段（概念）：server.RegisterTool("search", args=> mskm.Query(args.query,args.limit));
- 注意事項與最佳實踐：中文字元編碼（必要時使用 \uXXXX 轉義）、錯誤處理、工具描述清晰。
- 難度: 高級
- 學習階段: 進階
- 関聯概念: B-Q21, B-Q22, D-Q6


### Q&A 類別 D: 問題解決類（10題）

D-Q1: 遇到「回傳 JSON 不合法」怎麼辦？
- A簡: 啟用 JSON Mode/Schema、回傳前驗證、錯誤時重試或降級。
- A詳: 問題症狀描述：回應含多餘文字、缺逗號、欄位遺漏導致反序列化失敗。可能原因分析：未啟用 JSON 模式、Schema 不嚴格、溫度過高或提示混雜。解決步驟：1) 指定 response_format=json_schema；2) 回傳後 Schema 驗證；3) 失敗則重試或要求「只輸出 JSON」；4) 降級手工解析。預防措施：加入 success 與 error 欄位、降低溫度、加範例與單測。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, B-Q6, C-Q2

D-Q2: 為何 LLM 沒有觸發 Function Calling？
- A簡: 工具描述不足、提示優先級錯、輸出格式或參數不清導致。
- A詳: 問題症狀描述：模型直接文字回答而非發出 tool_calls。可能原因分析：system 未明示工具用途、描述/範例不足、對話歷史缺結果觀察欄位、或模型不支援工具。解決步驟：1) 強化工具描述與何時使用；2) 加few-shot；3) 確保記錄 tool 結果入歷史；4) 不支援則採「土炮」方案。預防措施：最大步數、監控與告警、工具測試集。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q23, C-Q4

D-Q3: 工具回傳後對話卡住怎麼辦？
- A簡: 確認以 role=tool 回寫並綁對 id，避免模型無法銜接。
- A詳: 問題症狀描述：模型反覆無回應或重複要求同一工具。可能原因分析：tool 結果未加入歷史、id 不匹配、或內容過長被截斷。解決步驟：1) 檢查對話歷史是否含 tool 結果；2) 校正 call-id 對應；3) 壓縮結果要點。預防措施：建立對話驗證器、序列化單元測試、限制結果大小。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11, B-Q7, C-Q5

D-Q4: RAG 結果「不中要點」的原因與修正？
- A簡: 視角不對齊、Chunk 策略不佳、缺少摘要/FAQ 導致。
- A詳: 問題症狀描述：返回片段語意相關度低、回答避重就輕。可能原因分析：文章過長、分段稀釋語意、查詢與作者視角不一致。解決步驟：1) 改良 chunking（重疊/語意）；2) 離線生成摘要/FAQ/案例；3) 加 re-rank；4) Query 改寫。預防措施：在匯入管線加入綜合步驟、標籤管理、建立評測集。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q13, B-Q18, C-Q8

D-Q5: 中文 Chunking 出現「疊字/晶晶體」怎麼辦？
- A簡: 檢查工具版本與 tokenizer，必要時降版或自訂分段。
- A詳: 問題症狀描述：中文內容被錯誤切分或重複字。可能原因分析：特定版本 chunk-by-token 對中文處理不佳。解決步驟：1) 退回已知穩定版本；2) 改用語意/句段切分；3) 自訂 Handler。預防措施：升級前壓測中文語料、加入語言偵測與多策略回退。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q13, B-Q14, C-Q6

D-Q6: MCP 中文 JSON 編碼亂碼或無法解析怎麼辦？
- A簡: 改用 \uXXXX 轉義輸出或統一編碼，檢查客端解析器。
- A詳: 問題症狀描述：MCP 客端顯示亂碼或丟擲 JSON 解析錯。可能原因分析：多端字元編碼不一致、客端不支援直出 Unicode。解決步驟：1) 以序列化選項強制 \uXXXX；2) 檢查 stdio/SSE 管道；3) 更新或修補 SDK。預防措施：跨語言字串測試、CI 自動化驗證。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q22, C-Q10, B-Q21

D-Q7: 出現「context length exceeded」如何處理？
- A簡: 壓縮歷史、降低 k 值、用摘要/關鍵點，必要時換長上下文模型。
- A詳: 問題症狀描述：API 拒絕、或強制截斷導致回答怪異。可能原因分析：對話歷史過長、引用片段太多、模型視窗不足。解決步驟：1) 歷史摘要化；2) 調整 k 與片段長度；3) 移除冗餘；4) 升級長上下文模型。預防措施：提示模板優化、預估 token、上線前壓測。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q3, B-Q11, C-Q9

D-Q8: 429/速率限制與超時如何處理？
- A簡: 指數退避重試、節流、併發控制與分批處理，外加快取。
- A詳: 問題症狀描述：頻繁 429、逾時、或延遲飆升。可能原因分析：併發過高、供應商配額不足、網路不穩。解決步驟：1) 退避重試（Polly）；2) 併發/節流；3) 快取重複請求；4) 分批匯入；5) 監控與告警。預防措施：容量規劃、預留配額、就近路由與健康檢查。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q10, B-Q19, C-Q6

D-Q9: 幻覺與錯誤引用來源怎麼診斷？
- A簡: 強制僅據引用回答、比對來源 URL、必要時拒答並記錄。
- A詳: 問題症狀描述：回答內容自創或引用不符。可能原因分析：提示不嚴、檢索結果不佳、模型過度自由生成。解決步驟：1) 提示要求列出引用並僅據引用回答；2) 自動驗證來源出處；3) 調整檢索與 re-rank；4) 啟用拒答策略。預防措施：Guardrails、來源白名單、問答評測。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q20, B-Q25, C-Q9

D-Q10: 成本激增或延遲過高的原因與優化？
- A簡: 引用過量、歷史冗長、模型過大；採摘要、k 值調整與分流。
- A詳: 問題症狀描述：費用與延遲不可控。可能原因分析：context 膨脹、工具結果過長、使用高價模型。解決步驟：1) 對話與引用摘要化；2) 減少 k 與片段長度；3) 分層架構（便宜模型預處理）；4) 快取與重用；5) 設 SLO 與熔斷。預防措施：成本儀表板、壓力測試、定期調參。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q19, C-Q9, A-Q24


### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 Chat Completion API？
    - A-Q2: Chat Completion 中常見的角色（role）有哪些？
    - A-Q3: 什麼是 Context Window（上下文視窗）？
    - A-Q4: Temperature 是什麼？為什麼重要？
    - A-Q5: 什麼是 Structured Output（JSON Mode）？
    - A-Q6: JSON Schema 在 LLM 應用中的角色是什麼？
    - A-Q7: 為什麼開發者應選擇 JSON 輸出而非純文字？
    - A-Q9: 什麼是 Function Calling（工具使用）？
    - A-Q12: 什麼是 RAG（檢索增強生成）？
    - A-Q14: RAG 與向量資料庫的關係是什麼？
    - B-Q1: Chat Completion 的 HTTP 請求與回應如何運作？
    - B-Q5: JSON Mode 如何強制結構化輸出？
    - C-Q1: 如何以 HttpClient 實作最小 Chat Completion？
    - C-Q2: 如何用 JSON Mode 抽取地址並反序列化為 C# 物件？
    - D-Q1: 遇到「回傳 JSON 不合法」怎麼辦？

- 中級者：建議學習哪 20 題
    - A-Q8: Structured Output 與 Function Calling 有何差異？
    - A-Q10: 為什麼需要 Function Calling？
    - A-Q11: tool 與 tool-result 在對話中各扮演什麼角色？
    - A-Q15: 什麼是 Semantic Kernel（SK）？
    - A-Q16: 什麼是 Microsoft Kernel Memory（MSKM）？
    - A-Q17: MSKM 與 SK 的差異與互補？
    - A-Q19: 文檔處理管線（Ingestion Pipeline）是什麼？
    - A-Q20: 什麼是 Chunking？為何重要？
    - B-Q4: 在 Semantic Kernel 實作簡單 Chat 的設計？
    - B-Q7: Function Calling 的回合機制如何運作？
    - B-Q8: 如何在 SK 定義並註冊 Plugin/Function？
    - B-Q11: RAG 的整體執行流程與組件？
    - B-Q12: 向量化與相似度檢索的原理？
    - B-Q13: Chunking 策略比較：固定長度、重疊、語意切分？
    - B-Q14: MSKM 架構：服務模式與嵌入模式？
    - C-Q4: 如何在 Chat 中實作購物清單的基本 Function Calling？
    - C-Q5: 如何實作排程助理（check_schedule/add_event）的多輪工具使用？
    - C-Q6: 如何部署 MSKM Docker 並以 SDK 建立索引？
    - D-Q2: 為何 LLM 沒有觸發 Function Calling？
    - D-Q3: 工具回傳後對話卡住怎麼辦？

- 高級者：建議關注哪 15 題
    - A-Q18: 什麼是「RAG as a Service」？
    - A-Q21: 什麼是「生成檢索專用內容」？
    - A-Q22: 什麼是 MCP（Model Context Protocol）？
    - A-Q23: 什麼是「土炮 Function Calling」？何時適用？
    - A-Q24: 為何強調單一職責與成本意識？
    - B-Q9: 多步驟依賴的工具鏈如何規劃？
    - B-Q15: MSKM 文件匯入 Pipeline 的各 Handler 作用？
    - B-Q17: 如何在 RAG 中混用外部搜尋（如 Bing）與 MSKM？
    - B-Q18: 為何「內容綜合」能提升 RAG 精度？
    - B-Q19: Token/成本估算與優化策略？
    - B-Q20: 如何降低幻覺與提升可追溯性？
    - B-Q21: MCP 通訊流程：initialize、tools/list、tools/call？
    - B-Q22: MCP 的 stdio 與 SSE 傳輸差異？
    - C-Q8: 如何用 SK 先生成摘要/FAQ/案例再寫入 MSKM？
    - C-Q10: 如何用 MCP C# SDK 封裝 MSKM 為 MCP Server 並接 Claude？