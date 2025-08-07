# 從 API First 到 AI First

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 AI 充分普及的未來，軟體開發人員要如何維持競爭力？
基礎功夫必須扎實。包括軟體設計原理、乾淨且可重用的抽象、良好的 API 設計、穩定的 CI/CD 流程，以及對資料與模型的 DevOps 能力。

## Q: 為什麼說「當 coding 可以量產時，決勝的是抽象化設計的品質」？
因為生成式 AI 寫一次性或客製化程式碼的速度與品質都可能比人快、比人好；唯有高品質、可重用、可維護的抽象層設計，才是人類開發者無可取代的價值所在。

## Q: 如果 coding 速度已不再是瓶頸，軟體開發競爭的關鍵會轉到哪裡？
將轉向基礎建設與架構決策。例如：如何系統化地管理模型、資料與算力；如何在 CI/CD Pipeline 中納入 AI 元件；以及如何確保整體架構可持續演進。

## Q: 生成式 AI 如何用「不同維度」來改善使用者體驗 (UX)？
LLM 能直接理解自然語言中的「意圖」，再自動呼叫 API 完成任務。它不再只是執行明確指令，而是先推論使用者真正想做的事，再代為操作系統，提供比傳統 UI 更直覺的體驗。

## Q: 過去電商網站通常用什麼方法來取得個人化與滿意度資訊？
1) 大量收集行為與交易資料進行統計，2) 監控跳出率、轉換率等指標，3) 透過問卷或評分機制（常搭配優惠誘因）請使用者回饋。  
這些方式多半是事前布署或事後統計，較難即時掌握個別使用者的真實情緒與需求。

## Q: 什麼是 AI DX？為何 API 設計品質在 AI 時代特別重要？
AI DX（Developer Experience for AI）指讓 LLM 或其他 AI Agent 能「看得懂且正確呼叫」你的 API 的體驗。  
若 API 規格清晰、一致且安全，AI 可減少 prompt 引導與錯誤呼叫，系統也較易測試與維護；反之將大幅增加成本與風險。

## Q: Copilot 模式在應用程式架構中的角色是什麼？
在 MVC 架構中，Controller 為「正駕駛」，Copilot(LMM) 為「副駕駛」。  
Controller 負責核心商業邏輯；Copilot 監聽操作脈絡、理解意圖並在需要時主動協助（或由使用者直接對 Copilot 提問），兩者協同完成流程。

## Q: RAG（Retrieval-Augmented Generation） 的基本工作流程為何？
1) LLM 先解析使用者問題並產生查詢。  
2) 系統用該查詢向向量資料庫檢索相關文件片段。  
3) 將檢索結果（知識片段）與原始問題合併成擴充 prompt。  
4) 再送入 LLM 生成最終答案。這樣可利用外部私有知識庫補足 LLM 原生知識的不足。

## Q: DevOps 流程在 AI 時代需要新增哪一條 Pipeline？
除了傳統的 Provisioning、Deployment、App Config 三條 Pipeline之外，還需要「AI Pipeline」，用來自動化資料收集、模型訓練、模型部署與推論算力調度，實作完整的 AI GitOps。

## Q: 開發者在 AI 時代應具備哪些新的基本能力？
1) API First 設計與 AI DX 思維。  
2) 能在架構圖上正確放置 LLM 與相關服務。  
3) 了解向量嵌入 (Embedding)、VectorDB、Prompt Engineering、Function Calling 等 AI 元件。  
4) 熟悉常用設計模式，如 RAG、推薦系統、Copilot / Agent Workflow，並能將其整合進實際產品。