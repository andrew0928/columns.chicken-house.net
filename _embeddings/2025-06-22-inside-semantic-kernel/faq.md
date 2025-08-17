# .NET RAG 神器 ─ Microsoft Kernel Memory 與 Semantic Kernel 整合應用

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Microsoft Kernel Memory (MSKM)？它與 Semantic Kernel (SK) 如何搭配？
MSKM 是微軟開源的「長期記憶/文件索引服務」，負責完成文件文字化、分段、向量化、儲存與查詢等 RAG 需要的全部流程；SK 則提供 LLM 互動、Function Calling、Plugins 等能力。  
兩者的整合點有二：  
1. MSKM NuGet 套件已內建「SK Memory Plugin」，可以直接掛到 SK 內，讓 LLM 透過 Function Calling 操作 MSKM。  
2. MSKM 本身也是用 SK 撰寫，SK 支援的各種 LLM／Embedding 連接器在 MSKM 內開箱即用。  

## Q: 為什麼開發者在設計 LLM 輸出時，應該使用 JSON Schema？
使用 JSON Schema 可以：  
1. 讓 LLM 產生結構化輸出，一次反序列化成 C# 物件便於後續程式碼處理。  
2. 明確標示成功或失敗欄位，降低靠「猜測」判斷結果的風險。  
3. 把 LLM 侷限在「非它不可」的任務，其餘轉交傳統程式邏輯，避免浪費 token 及成本。  

## Q: 一次 Chat Completion API 呼叫的基本結構有哪些區塊？
1. Headers（含 API Key 等認證資訊）  
2. Model 與參數（如 temperature）  
3. Messages（對話歷程，含 role）  
4. Tools（可選，用於 Function Calling 的工具定義）  
5. Response Format（可選，指定回應格式或 JSON Schema）  

## Q: Function Calling 是如何讓 LLM 與程式碼互動的？
開發者在呼叫前「公布」可用函式（tools），對話過程中 LLM 依語意判斷：  
1. 直接回文字給使用者；或  
2. 回傳 tool_call，要求應用程式代為執行函式並回傳結果；  
應用程式把結果以 tool-result 形式餵回 LLM，直到 LLM 判定任務完成。此機制開啟了 Agent、自動化流程等高階應用。  

## Q: 什麼是 Retrieval Augmented Generation (RAG)？為何常與 Function Calling 一起使用？
RAG 透過「先檢索、後生成」提高答案新穎度與正確性，基本流程為：  
1. 收斂使用者問題，轉成查詢條件；  
2. 到向量資料庫（或搜尋引擎）取回相關片段；  
3. 把檢索結果 + 問題組成 prompt，交給 LLM 生成最終回覆。  
若把「檢索」實作成 tool，LLM 便能用 Function Calling 自動決定何時檢索、如何組合參數，形成完整的 RAG 鏈。  

## Q: MSKM 提供哪兩種主要的部署／使用模式？
1. Web Service　：以 Docker image 或原始碼部署，透過 HTTP API 存取。  
2. Serverless／Embedded　：直接把 MSKM 核心嵌入自家 .NET 應用程式，不經 HTTP，於程式內呼叫。  

## Q: 提升 RAG 檢索準確度，有哪些「文件前處理」技巧？
作者實測以下方法能大幅改善命中率：  
1. 生成「全文摘要」(abstract)。  
2. 為每個段落生成摘要 (paragraph-abstract)。  
3. 轉成 FAQ（question/answer)。  
4. 轉成「解決方案案例」(problem/root cause/resolution/example)。  
這些由 LLM 預先產生的內容再向量化儲存，可對齊使用者多元的提問視角。  

## Q: 若模型原生不支援 Function Calling，可以土炮實作嗎？
可以。核心只需落實三點：  
1. 以 system prompt 說明「有哪些工具」及對話規則。  
2. 讓 LLM 用固定前置詞區分「給使用者」與「給工具」的訊息。  
3. 應用程式攔截工具訊息、執行指令，再把結果插回對話。  
即便使用不支援 Function Calling 的模型，也能手動完成類似流程。  

## Q: Function Calling 的三個基礎要件是什麼？
1. 定義工具清單與參數格式。  
2. 在訊息中區分 user、assistant、tool 三方角色。  
3. 讓 LLM 「自行」產生 tool 名稱與對應參數，應用程式負責執行並回傳結果。  

## Q: 問卷調查中，哪個主題被認為對工作幫助最大？
根據 93 份回覆，RAG 與其進階應用（尤其是「生成檢索專用資訊」與「MSKM 介紹」）得到最多人票選為「對工作幫助最大」的主題。