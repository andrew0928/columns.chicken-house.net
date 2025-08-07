# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在開發 AI 應用前，必須先徹底了解 Chat Completion API？
Chat Completion API 幾乎是所有 LLM 雲端服務的唯一核心端點，只要掌握它就能完成問答、工具呼叫、RAG 等各式需求。真正的難度不在 API 本身，而是如何運用各種「AI App Design Patterns」去解決業務問題。

## Q: 對開發者而言，讓 LLM 輸出 JSON（並附上 Json Schema）有什麼好處？
1. 可以直接反序列化成強型別物件，方便後續程式碼處理。  
2. Schema 中可明確標示成功或失敗欄位，讓程式不用靠猜測判斷 LLM 是否答得出來。  
3. 只保留 LLM「非它不可」的職責，其餘交由傳統程式碼處理，效能與費用都更可控。

## Q: 如果 LLM 約有 1 % 機率回答不出結果，程式應該怎麼判斷？
在 Json Schema 中加上顯式的狀態欄位（例如 `"is_success": true/false`），由 LLM 主動回報是否取得答案，而不要靠字串解析或例外偵測去猜測結果。

## Q: 是否所有工作都應該交給 LLM 一次完成？
不應該。建議採「單一職責」原則：  
‧ 讓 LLM 專注在推理、生成等 AI 強項；  
‧ 搜尋、格式轉換、數值計算等可由一般程式或外部 API 處理，以降低 token 成本並提升可靠度。

## Q: 什麼是 Function Calling？為何被視為 LLM 時代最重要的基礎能力？
Function Calling（或 Tool Use）允許先把可呼叫的函式清單與參數定義傳給 LLM；LLM 在對話過程中自行判斷是否要呼叫這些函式、以及以何種參數呼叫。它讓 LLM 能像「總機」一樣調度外部系統，開啟 Agent 化與自動化工作的可能。

## Q: 多步驟 Function Calling 實務上如何運作？
對話除了 `system/user/assistant` 角色，還會加入  
‧ `assistant(+tool_calls)`：LLM 告知要執行的函式與參數；  
‧ `tool`：應用程式執行函式後，把回傳結果貼回對話。  
LLM 可根據最新對話歷程反覆規劃→執行→檢視→再規劃，直到任務完成。

## Q: 一個典型 RAG（Retrieval Augmented Generation）流程包含哪些步驟？
1. 問題收斂（Re-write/Refine Query）。  
2. 依收斂後的關鍵字或向量到檢索系統查詢相關內容。  
3. 將檢索結果與原始問題組成新 prompt，交給 LLM 生成最終答案。

## Q: RAG 如何透過 Function Calling 自動被觸發？
只要將「search」之類的檢索函式註冊到 LLM 的 tools，並在 system prompt 中說明「先搜尋再回答」。LLM 便會在需要時自行呼叫該函式，把搜尋結果納入回答，完成 RAG 流程。

## Q: Microsoft Kernel Memory (MSKM) 是什麼？解決了哪個痛點？
MSKM 是微軟開源的「RAG as a Service」。它處理長期記憶管理：文件抽取、分段、向量化、標籤、儲存、查詢等整條 Pipeline，讓開發者不用自己打造繁複的長文檔資料處理機制。

## Q: MSKM 與 Semantic Kernel (SK) 如何整合？
1. MSKM 已內建 SK 的 Memory Plugin，可直接掛到 Kernel 當成工具，讓 LLM 用 Function Calling 操作 MSKM。  
2. MSKM 本身即使用 SK 打造，所以 SK 支援的各種 LLM / Embedding Connector（OpenAI、Azure OpenAI、Ollama、Claude …）在 MSKM 皆可沿用。

## Q: 為何在大型文件做 RAG 時，單靠「固定長度分段」常常查不到重點？
使用者詢問的語意角度（question/problem）與作者撰寫文章的角度不一定一致，單純切片後向量化容易牛頭不對馬嘴。可先用 LLM 生成「摘要、段落摘要、FAQ、Problem/Resolution」等多種視角的文本，再一起向量化存入 MSKM，可大幅提升檢索精度。

## Q: 最近 MSKM Docker 映像有什麼已知問題？該怎麼辦？
2025 / 02 之後的 0.97.x 版本重寫 chunking 流程，中文會出現「疊字」錯誤。暫時建議回退到 0.96.x 版本，官方 Issue 仍在修復中。

## Q: 如果使用的模型原生不支援 Function Calling，還能用嗎？
可以。透過「土炮」法：  
1. 在 system prompt 定義好「給使用者的回覆」與「給工具的指令」前置詞；  
2. 應用程式攔截帶有指令前置詞的訊息，解析後自行呼叫對應函式並回貼結果；  
3. 依序把完整對話再送回 LLM。  
只要模型推理能力夠強，仍能模擬出 Function Calling 效果。

## Q: 參與者問卷顯示，哪些主題對大家最有幫助？
統計結果前三名為：  
1. 進階 RAG 與檢索資料前處理技巧。  
2. Function Calling 與底層 Request/Response 流程解析。  
3. Microsoft Kernel Memory 與 Semantic Kernel 的整合實作。