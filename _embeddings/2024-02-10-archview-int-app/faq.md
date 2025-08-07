# 替你的應用程式加上智慧! 談 LLM 的應用程式開發

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 如果想替既有 APP 加入 LLM 智慧，可以依照哪些階段循序推進?
1. 無智慧：維持既有選單/按鈕操作。  
2. 關鍵節點用 AI 評估風險：例如結帳前請 LLM 幫忙做「常識」檢查與提醒。  
3. 全程 Copilot 輔助：在使用者每一步操作後即時分析歷程並給出建議或提示。  
4. 全對話式操作：讓 Agent 具備 Function-Calling 能力，使用者只需自然語言即可完成整個流程。  

## Q: LLM 型應用程式的核心架構要素有哪些?
它由五個「層」組合而成：  
1. LLM（大腦）  
2. Chat History（短期記憶）  
3. Knowledge / RAG（長期記憶，向量資料庫檢索）  
4. Skills / Plugins（技能；可被 LLM 呼叫的函式或 API）  
5. Persona & Personal Information（角色設定與個人化資料）  
這些元素合併後才能讓 AI 又「懂你在說什麼」又「做得到你要的事」。

## Q: 開發 LLM 智慧應用時，對開發者最關鍵的新能力是什麼?
兩件事最重要：  
1. Prompt Engineering：能以精簡、明確的自然語言提示控制 LLM 行為與品質。  
2. Skill / Plugin 設計：把正確且精煉的 Domain API 以描述化方式暴露給 LLM，讓模型能判斷何時呼叫、帶什麼參數。

## Q: 未來的應用程式會如何運用 AI？  
AI 將嵌入在主流 OS 或各種 APP 內，從被動回答（Chatbot）、知識檢索（RAG）、並排協助（Copilot）一路走向可自主完成任務（Fully Autonomous Agent）。使用者體驗將從按鈕點擊轉為自然語言對談。

## Q: 對軟體開發流程與角色有何影響？  
程式碼量將下降，重心轉向：  
‒ 定義業務語意與提示、  
‒ 維護技能/API 規格、  
‒ 確保資料與安全。  
開發者不會消失，但「寫程式」愈來愈像「寫提示」，自然語言將成為未來的重要「程式語言」。