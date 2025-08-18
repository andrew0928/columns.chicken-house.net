# .NET RAG 神器 – Microsoft Kernel Memory 與 Semantic Kernel 整合應用

# 問答集 (FAQ)

## Q: 文章中的所有範例都圍繞哪一支 API？它的基本通訊模式是什麼？
Chat Completion API。  
開發者把「對話歷史 (messages)」一次 POST 給 API，每則訊息標示 role（system / user / assistant）。API 依此返回下一段 assistant 回應；若要繼續對話，就把先前歷史連同新問題再次呼叫同一支 API。

## Q: 為什麼在應用程式中最好要求 LLM 以 JSON Mode 並遵守 JSON Schema 回傳結果？
1. 可以直接反序列化成物件，方便後續非 AI 程式碼處理。  
2. 在輸出中「明確」標示成功 / 失敗，比事後自行解析或拋例外安全。  
3. 讓 LLM 只做「非它不可」的任務，搜尋、格式轉換等可交由一般程式碼執行，節省 Token 成本與費用。

## Q: 設計結構化輸出時，作者建議遵守哪三個原則？
1. 以 JSON Schema 定義回傳格式。  
2. 在輸出欄位中顯式標示執行結果狀態。  
3. 單一職責：LLM 只負責擅長的推理／語意任務，其餘交給傳統程式碼。

## Q: 什麼是 Function Calling？為何作者稱它為「威力最大的功能」？
Function Calling 或 Tool Use 是在對話一開始就告訴 LLM 可用的函式（含參數），之後讓 LLM 自行決定何時呼叫函式、何時直接回答文字。它把「自然語言意圖」即時轉譯成「程式指令序列」，是各種 Agent 與自動化流程的基礎。

## Q: 以「管理購物清單」為例，Function Calling 基本流程是什麼？
1. 在 system prompt 宣告可用動作（add / delete 及參數）。  
2. 使用者提出需求。  
3. LLM 回傳一段 JSON，列出需要被執行的動作與參數。  
4. 應用程式依序執行這些動作後，把結果回寫對話歷史（tool-result）。  
5. LLM 檢視結果後，決定是否繼續呼叫函式或向使用者回覆最終訊息。

## Q: Retrieval Augmented Generation (RAG) 是什麼？基本步驟有哪些？
RAG（檢索增強生成）是在回答前先檢索外部知識，再請 LLM 依據檢索結果生成回應。  
步驟：  
1. 根據問題收斂成檢索條件。  
2. 到向量資料庫／搜尋引擎取回相關內容。  
3. 把檢索內容與原問題組合成 prompt，送給 LLM 生成最終答案。

## Q: 如何利用 Function Calling 自動觸發 RAG？
將「搜尋知識庫」宣告成一支 tool，並以 JSON Schema 定義 query、limit 等參數。當 LLM 判定需要外部知識時，會自行產生 tool_call，應用程式執行檢索並把結果以 tool-result 回傳，LLM 再基於新資訊回答使用者。

## Q: Microsoft Kernel Memory（MSKM）主要解決什麼痛點？它與 Semantic Kernel 的關係是什麼？
MSKM 專門處理「長期記憶」的整個生命週期：文件文字化、分段、向量化、儲存與查詢。  
它由與 Semantic Kernel 同一團隊開發：  
1. MSKM 內建 Semantic Kernel 的 Memory Plugin，可直接掛進 SK 當工具被 LLM 使用。  
2. MSKM 本身也是用 SK 撰寫，SK 支援的 LLM/Embedding 連接器都可沿用。

## Q: MSKM 提供哪兩種主要部署模式？
1. Web Service：以容器或獨立服務部署，透過 HTTP API 存取。  
2. Serverless / In-Process：將核心組件以 NuGet 套件嵌入自己的應用程式。

## Q: 作者如何提高長篇文章的 RAG 檢索精度？
在匯入向量庫前，先用 LLM 生成「檢索專用內容」，例如：  
• 全文摘要  
• 每段摘要  
• FAQ（question/answer）  
• 故障案例（problem/root-cause/resolution）  
並附加適當 tag 再向量化。如此查詢時能得到語意更對齊的片段，顯著提升 Recall。

## Q: 若使用的模型原生不支援 Function Calling，該如何「土炮」實作？
在 system prompt 自行定義「與工具對話」的格式，例如要求 LLM 以「請執行指令: …」作為呼叫工具的前置詞。  
應用程式掃描每段回應，遇到該前置詞就解析指令、執行外部函式，再把結果以另一固定前置詞回貼給 LLM。只要模型推理能力夠好，仍可完成整個 call-return 流程。