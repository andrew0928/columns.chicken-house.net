# .NET RAG 神器 ─ Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 摘要提示
- Chat Completion API: 以 OpenAI ChatCompletion 為核心，示範從 HTTP、SDK 到 Semantic Kernel 的基本呼叫流程與通訊模式。  
- JSON Mode: 透過 Json Schema 讓 LLM 產生結構化輸出，方便程式以物件方式接手後續流程。  
- Function Calling: 說明 LLM 如何根據工具定義產生指令並取得結果，奠定 Agent 化應用的基礎能力。  
- 進階 Function Flow: 以「排程晨跑」案例展示多輪工具呼叫與結果回饋的完整往返機制。  
- RAG 基礎: 結合檢索與生成，讓 LLM 引用外部知識庫回答最新或專有領域問題。  
- Microsoft Kernel Memory: 將 RAG 封裝成服務，可雲端部署亦可內嵌，並提供 SK Memory Plugin 直接串接。  
- RAG 優化: 透過摘要、FAQ、解決方案等多視角內容，提升長文向量檢索的相關性與精確度。  
- MCP 整合: 以 Model Context Protocol 將 MSKM 暴露為 MCPServer，與 Claude Desktop、No-code 平台等互通。  
- 土炮 Function Calling: 在不支援工具呼叫的模型上，以角色標記與對話規則手動實作同樣流程。  
- 問卷回饋: 近百位開發者對課程內容、時程與後續主題給出高度評價與建議。

## 全文重點
本文整理自作者三月直播與八日臉書貼文，主軸是如何在 .NET 環境把 LLM 的「結構化輸出、Function Calling 與 RAG」三項基礎能力落實為可維運的企業級應用。  
首先透過 Day 0 介紹 Chat Completion API 的訊息格式（header、model 參數、messages、tools、response_format），奠定後續所有範例的通訊基礎；並以 HTTP、OpenAI .NET SDK 及 Semantic Kernel 三種寫法對照，讓讀者體會抽象層次差異。  
Day 1 聚焦 JSON Mode，指出開發者應要求 LLM 直接回傳符合 Json Schema 的物件，並於物件內明確標示成功或失敗，以降低解析成本與幻覺風險。  
Day 2-3 進入 Function Calling：Day 2 先講單輪指令生成，Day 3 以行事曆排程為例，示範 LLM 如何根據工具庫決定呼叫順序、等待程式執行結果，再回覆最終答案，完整展示「Calling-Return-Calling」迴圈。  
Day 4 引入 RAG，解釋檢索強化生成流程：問題收斂→向量或搜尋引擎檢索→將結果與問題組成新 prompt 交給 LLM。作者示範使用 BingSearch plugins，讓 LLM 具備即時查詢能力。  
Day 5 正式介紹 Microsoft Kernel Memory（MSKM）—一套由 Semantic Kernel 團隊開發的開源 RAG 服務。MSKM 以 Docker/源碼雙模式部署，並內建 SK Memory Plugin，使 LLM 能把「長期記憶」當工具呼叫。  
Day 6 深談進階 RAG：面對長文與多篇文章，僅靠分段向量化常導致語意失真；作者利用 LLM 在匯入前生成摘要、段落摘要、FAQ、問題解決對映等多種「檢索專用文本」，搭配自訂 pipeline 或外部預處理，大幅提升相關性。  
Day 7 探討 MSKM 與外部系統的整合：列舉 GPTs Custom Action、No Code 平台 Custom Tools、MCPServer 等多種通訊協定，並以 MCP C# SDK 將 MSKM 暴露給 Claude Desktop；同時說明 MCP 的 initialize、tools/list、tools/invoke 標準流程。  
Day 8 則示範「土炮」方式：即使模型不原生支援 Function Calling，只要在 system prompt 定義對話規則並於應用程式端攔截特定前綴訊息，一樣能完成工具呼叫往返。  
最後作者彙整 93 份問卷回饋：學員最受用的主題依序為 Function Calling、RAG 與 MSKM；多數人透過 SDK 或 SK 存取 LLM，並對後續進階 Agent、事件驅動、實務案例保持高度興趣。整體評分平均九成以上。

## 段落重點
### 相關資源與連結
彙整直播錄影、投影片、範例程式碼與問卷網址，方便讀者邊看文章邊對照原始素材；同時說明本文為直播後的整理稿，未來新內容將持續補充到此。

### Day 0 – Chat Completion API
解析 Chat Completion 的訊息格式與通訊模式，只靠單一 API 即可實作完整對話；示範 HTTP、OpenAI SDK 與 Semantic Kernel 三種呼叫層級，提醒開發者了解抽象層帶來的便利與限制。

### Day 1 – Structured Output (JSON Mode)
闡述為何在程式內應使用 Json Schema 強制 LLM 回傳結構化結果；提出成功/失敗旗標、職責切割與成本考量三點原則，並用多語言範例說明 SDK 帶來的 schema 生成優勢。

### Day 2 – Function Calling (Basic)
介紹 Function Calling 又稱 Tool Use 的概念：於 system prompt 宣告可用函式，LLM 根據意圖輸出 action 與參數。以購物清單為例，示範 LLM 如何把自然語意翻譯為 add/delete 指令集合。

### Day 3 – Function Calling (Case Study)
深入探討多輪指令流程，以「排程 30 分鐘晨跑」為例，說明 tool、tool-result、assistant 三種訊息如何交替；強調理解原理後，可選用 Semantic Kernel、n8n、Dify 等框架簡化實作。

### Day 4 – RAG with Function Calling
將 Function Calling 應用於 RAG：LLM 先辨識問題，再自行組出搜尋函式與參數，檢索結果後生成答案；透過 plugins，可讓 LLM 彷彿「會用 Google」，並能隨時切換為私有知識庫。

### Day 5 – MSKM: RAG as a Service
介紹 Microsoft Kernel Memory 的定位與兩種部署模式（服務與內嵌），解釋其解決「長期記憶」的向量化、存儲與檢索流程；點出 MSKM 與 SK 的兩大整合優勢：Memory Plugin 與共用 Connector。

### Day 6 – 進階 RAG 應用
說明單純分段向量化在長文場景的缺陷，提出摘要、段落摘要、FAQ、問題解決對映等多視角生成策略；藉由 SK 先行加工，或在 MSKM 自訂 pipeline，顯著提升查詢命中率。

### Day 7 – MSKM 與其他系統整合
盤點四種 Function Calling 通路：GPT Custom Action、No Code Tools、MCPServer、SK Plugins；重點介紹 MCP 協定（stdio/SSE）與 csharp-sdk 實作，並演示 Claude Desktop 透過 MSKM 進行 RAG。

### Day 8 – 土炮 Function Calling
展示在不支援工具呼叫的模型上，以 system prompt 定義「請執行指令／安德魯大人您好」雙角色，配合程式端攔截與轉發即可重現 Function Calling 流程；提醒實務仍以原生支援模型為佳。

### 問券回饋
統計 93 份問卷：Function Calling、RAG、MSKM 為最受用主題；多數開發者偏好 SDK 與 SK；對進階 Agent、實務案例、事件驅動整合等後續課題呼聲最高，整體滿意度逾 90%。