# [架構師觀點] 開發人員該如何看待 AI 帶來的改變?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 安德魯小舖 GPTs 的 PoC 告訴我們什麼？
PoC 證明了只要把「角色設定＋知識庫＋符合 OpenAPI 規格的自家 API」掛進 GPTs，LLM 便能像店員一樣以對話方式完成整個購物流程——包含瀏覽商品、試算折扣、修改購物車、結帳與查訂單。技術本身門檻不高，但對「整合與思維」要求極高；最大震撼是 GPTs 能自動推理並補上 API 中沒有實作的業務邏輯，真正做到「理解使用者意圖並選用正確 API」。

## Q: AI 成熟後，軟體開發流程的核心改變是什麼？
最大的改變是「LLM 先於 UI」，也就是先讓大型語言模型理解使用者意圖，再由 LLM 決定要呼叫哪些 API、怎樣組合資料、最後再把結果轉譯回自然語言或 UI 互動。未來：
1. LLM 會成為作業系統的一部分並負責 Orchestration。  
2. Copilot 式介面將變成主要的人機互動入口。  
3. API 將成為 LLM 與既有系統溝通的唯一通道，並且必須能被語言模型讀得懂、用得對。  

## Q: 為什麼「AI-Friendly API」如此關鍵？要符合哪些原則？
因為未來呼叫你 API 的不是人類開發者，而是不受你約束、靠文件與描述推理的 LLM。API 若要被 AI 善用，設計必須：
1. 精準對應領域模型與業務流程，盡量避免特殊例外。  
2. 以標準安全機制（APIKey / OAuth2）公開，並附完整 OpenAPI / Swagger 描述，讓 LLM 能「望文生義」。  
3. 採有限狀態機與嚴謹錯誤處理，確保即使被錯誤順序或參數呼叫也不會失控。  
否則便是「無法被 AI 善用的 API」，在新世代將逐漸被淘汰。

## Q: 架構師需要如何帶領團隊邁向 AI-Ready？
1. 釐清「計算任務」與「意圖任務」邊界：前者保持傳統程式精準計算，後者交給 LLM 推理。  
2. 重新設計精準合理的核心 API，並確保符合 AI-Friendly 原則。  
3. 將 UI 依「任務」顆粒化，能由 Copilot/LLM 處理的情境就交給語言介面，其餘保留最必要的操作畫面。  
4. 選定並落實新的 AI 開發框架（如 Semantic Kernel），把系統各元件放在正確層次，逐步重構現有服務。

## Q: 開發人員在 AI 世代該具備哪些能力？
1. 善用 GitHub Copilot、ChatGPT 等工具大幅提升日常產能。  
2. 學會 Prompt Engineering、向量資料庫與 RAG 基礎，並熟悉 Semantic Kernel 或 LangChain 等 AI 應用框架。  
3. 深化 Domain Design／DDD／API First 能力，因為未來服務核心是高品質的領域 API，而不是大量畫面與 CRUD 代碼。

## Q: Microsoft 在 AI 佈局的三大核心是什麼？
1. Azure OpenAI Service：提供雲端 GPT-系列與其他 Foundation Models。  
2. Copilot：作業系統與生產力工具的主入口，負責整合本地與雲端資源。  
3. Semantic Kernel：讓開發者把 LLM、記憶體、外部 Plugin/API 串成一個可擴充的 AI 應用開發框架。

## Q: Semantic Kernel 在 AI 應用架構裡扮演什麼角色？
Semantic Kernel 負責協調「Model（LLM）-Memory（對話/知識庫）-Plugins（外部 API / Function）」三大元件。  
它提供 Planner、Skill、Connector 等機制，讓開發者能用程式方式定義 Prompt、掛上自家 API，並交由 Kernel 自動決定何時呼叫何種 Function、如何保留上下文記憶，最終形成可重用的 AI Application 基礎骨架。

## Q: Demo 過程中最大的教訓是什麼？
最大的教訓是「不合理的 API / UI 流程會大幅拉高整合難度」。作者原先省略標準 OAuth2，想靠 Prompt 引導 GPTs 先登入再呼叫業務 API，結果花了兩週仍問題叢生；改成一天實作完整 OAuth2 流程、把認證邊界交回傳統程式碼，整個 PoC 立刻順暢。結論：認證、交易等精準計算仍應由後端嚴謹掌控，LLM 負責「理解意圖與編排流程」即可。

## Q: 面對 AI 帶來的變革，開發人員到底「該如何看待」？
把 AI 視為「必備基礎建設」而非「附加功能」。短期先借助 AI 工具加速現有工作；中長期則要主動學習 AI 開發框架與新技術，把自己的程式碼、API 與系統設計都養成 AI-Friendly。換言之：擁抱 AI、升級技能、精準聚焦領域價值，你就不必擔心被 AI 取代，而能與 AI 並肩前行。