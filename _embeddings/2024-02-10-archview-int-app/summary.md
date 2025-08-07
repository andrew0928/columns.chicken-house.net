# 替你的應用程式加上智慧! 談 LLM 的應用程式開發

## 摘要提示
- 演進四階段: 作者以「安德魯小舖」PoC 示範從傳統操作到全對話式代理的四段智慧化歷程。  
- Semantic Kernel: 透過 SK 將 LLM、記憶體、RAG 與 Plugins 組合，快速為 App 注入語意理解與動作能力。  
- RAG 長期記憶: 利用向量資料庫＋Embedding 擴充模型知識，降低 token 成本並提升回答準確度。  
- Skills／Function Calling: 為 LLM 登錄 API 或程式函式，讓模型能「理解→決策→帶參數呼叫」完成任務。  
- Copilot 模式: 在傳統 UI 旁加入 AI，隨時觀察操作並即時給建議，提高易用性與安全性。  
- Prompt Engineering: 好的 persona、系統提示與用字精簡是控制 LLM 行為與成本的關鍵。  
- 架構轉變: UI／Domain／Data 三層架構外，需新增 LLM、Memory、Plugins 等元件。  
- 開發者角色: 未來程式設計將漸往「寫提示」與「定義技能」移動，而非大量手寫程式碼。  
- End of Programming: 作者呼應業界觀點，認為自然語言或將成為新版「程式語言」。  
- 實務建議: 先在最需語意判斷的環節小步導入 AI，再逐步擴大到全自動代理型應用。

## 全文重點
本文以作者自建的「安德魯小舖」Demo 為主線，說明如何把大型語言模型 (LLM) 逐步嵌入現有應用。第一段先展示四個階段：1️⃣純傳統選單操作；2️⃣在關鍵節點用 LLM 檢查風險、補足常識；3️⃣如 GitHub Copilot 般併行監看流程並提出即時建議；4️⃣允許 AI 解析自然語言、自動呼叫函式完成整個交易。藉由 System Prompt 與 User Prompt 的設計，LLM 能在結帳前提示未成年飲酒風險，或主動偵測異常操作並給出 HINT。

第二段深入解析系統架構。核心為 LLM，搭配 Chat History 提供短期記憶，向量資料庫＋RAG 提供長期知識，Plugins（Skills）則讓模型得以呼叫外部 API 執行任務，Persona/Prompt 用來限制或塑形行為。Microsoft Semantic Kernel 以統一介面整合上述元件：Models、Memories、Plugins，再由 Planner／Orchestration 管理多步驟調用。作者示範如何用 C# Attribute 標註方法即成 Plugin，並經由 `builder.Plugins.AddFromType<>()` 註冊，使 GPT-4 能自動選擇 `ShopFunction_AddItemToCart` 等函式並帶入正確參數。

第三段提出未來觀察：當 LLM 價格下降、推理速度提升且工具鏈完備，「用嘴寫程式」將成現實；開發者主責或轉為定義 Prompt、維護知識庫與技能清單。作者認為精準運算與語意運算必須共存，企業須判斷何時交由 AI、何時用傳統算法。最後他引用「The End of Programming」與相關 Tech Talk，指出組織已能接受人類工程師的錯誤容忍度，同理也能學會與不完美但高潛力的 AI 協作。

## 段落重點
### 1. 「安德魯小舖」的進化
作者以線上商店 Demo 為例，拆成四階段驗證如何導入 AI。第一階段僅是數字選單，做為對照組；第二階段在結帳等關鍵點引入 LLM，利用 System Prompt＋FAQ 讓 AI 判斷未成年飲酒、空購物車結帳等風險並以 HINT 回報；第三階段比照 Copilot，將每次使用者指令封裝為 `我已進行操作:` 的 User Prompt 傳給模型，模型只有在偵測到異常時才以 HINT 顯示，達到「全程旁聽、適時提醒」；第四階段賦予模型 Function Calling 能力，透過 Semantic Kernel 將購物 API 封裝為 Skills，GPT-4 能解讀一句自然語言（如「千元預算買啤酒可樂各10，其餘買綠茶」）並自動拆解為多個函式呼叫，完成加購、試算、列車確認等流程，開啟全對話式操作的可能。

### 2. 探索 LLM 應用的系統架構與開發框架
作者先對比傳統 UI/Domain/Data 三層，再加入 LLM 後需新增 Chat History（短期記憶）、Vector DB＋RAG（長期知識）、Skills／Plugins（可執行動作）與 Persona（角色設定）。Semantic Kernel 以 Models、Memories、Plugins 三大抽象物整合各家模型、向量庫及函式；開發者只需以 C# Attribute 描述說明，SK 便能把 method 轉成可被 GPT 理解的「技能」，並自動進行決策、填參與呼叫。作者強調 Prompt Engineering 與良好 API 分割的重要：Skills 重質不重量，過雜反增混淆。文中亦引用 GitHub 部落格與 CS50 Talk 圖示，闡述 LLM、Orchestration、外部資源間的互動全貌。

### 3. 未來的發展（個人觀點）
面對「StackOverflow→ChatGPT→Copilot」的轉變，作者預測十年內自然語言將成主流「程式語言」，而 LLM 成為新的 CLR。開發者工作將從撰寫控制流轉向撰寫提示、配置知識、定義技能；Prompt Engineering 及 AI-API 設計會是核心能力。雖然 LLM 仍有幻覺與不可預測，但人類也容忍員工犯錯，組織同樣能擁抱 AI。未來軟體設計需判斷何部分追求數值精準、何部分交由語意推理。作者引用「The End of Programming」觀點：當我們接受不完美而具潛力的 AI，才能釋放真正的生產力，並呼籲資深工程師調整心態，在變革前線重新定位自我價值。