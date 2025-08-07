# .NET RAG 神器 - Microsoft Kernel Memory 與 Semantic Kernel 整合應用

## 摘要提示
- Chat Completion API: 以 OpenAI ChatCompletion 為核心，展示從 HTTP 到 SDK 的完整呼叫流程與訊息格式。
- Json Mode: 利用 Json Schema 要求 LLM 產生結構化輸出，方便程式端反序列化與錯誤判斷。
- Function Calling: 說明工具清單、三方對話與工具結果回填，並用購物清單、行事曆範例示範。
- RAG 流程: 將「收斂問題 → 檢索 → 生成」拆解，展示在 Function Calling 中自動觸發檢索的作法。
- Microsoft Kernel Memory: 以「RAG as a Service」形式提供向量化、匯入管線與 SK 插件整合。
- Semantic Kernel: 作為 .NET 端統一的 LLM orchestrator，連接 OpenAI、MSKM 及各種 Plugins。
- 進階 RAG: 透過摘要、FAQ、解決方案等視角預先生成檢索片段，大幅提升查詢命中率。
- MCP 整合: 以 MCPServer 將 MSKM 暴露給 Claude Desktop 等 Host，實作跨平台工具協定。
- 土炮 Function Calling: 即使模型不支援 Tool Use，也可用系統提示詞與角色約定手動實現。
- 問券分析: 93 份回饋顯示架構觀念、Function Calling 與 RAG 實務最受歡迎，亦收集後續課程建議。

## 全文重點
本文整理了作者八日直播內容與簡報，從 LLM 最基礎的 Chat Completion API 說起，逐步引入 Json Mode、Function Calling、RAG，再延伸到 Microsoft Kernel Memory（MSKM）與 Semantic Kernel（SK）的整合實戰。首先透過 Day 0 範例闡述 ChatCompletion 的 headers、model 參數、messages 與 tools 五大區塊，確立「一切都是對話歷史重送」的觀念；隨後在 Day 1 強調結構化輸出的必要性，藉由 Json Schema 讓 LLM 回傳嚴謹格式並附上成功 / 失敗旗標，降低幻覺與後續程式判斷成本。

Day 2、Day 3 以購物清單及行事曆排程為例，解析 Function Calling 的呼叫與回傳序列，說明工具定義、tool / tool-result 訊息以及多輪規劃（Planning）的實際運作；接著在 Day 4 將 Function Calling 與檢索增強生成（RAG）結合，示範 LLM 如何自行組裝搜尋參數並向外部向量庫或搜尋引擎索取資料，再根據來源內容回覆使用者。

Day 5 進入主題 MSKM，介紹其兩種部署模式（獨立 Web Service 與 Serverless 內嵌），以及與 SK 互補的 Memory Plugin。MSKM 透過可插拔的 pipeline（文字化、分段、向量化、儲存）處理長期記憶，並提供 NuGet / Docker 雙管道方便導入。Day 6 進一步分享如何在匯入階段利用 LLM 先行生成摘要、FAQ、解決方案等多種視角片段，以 tag 區分並向量化，顯著提升 RAG 命中率並降低 token 浪費。

Day 7 聚焦異質整合，包含 GPTs Custom Action、Dify No-Code、MCPServer for Claude Desktop 及 SK Plugins 四種路徑，說明它們本質皆為「宣告工具規格 + 代執行 + 回填結果」的變形，而 MCP 透過 stdio / SSE 擔任 AI 的 USB-C。Day 8 則示範「土炮」策略：即使模型不支援 Tool Use，只要在 system prompt 約定前置詞即可手動攔截並執行指令，強調理解協議比依賴框架更重要。

最後作者公布問卷統計，架構說明、Function Calling、RAG 及 MSKM 實務最獲好評，同時收納對進階 Agent、事件驅動、多模態及工作坊形式的期待，為未來課程鋪路。

## 段落重點
### 相關資源與連結
整合 Facebook 貼文、YouTube 錄影、問卷、GitHub 範例與 .NET Conf 簡報，方便讀者事後查證、下載程式碼與回饋意見。

### Day 0, Chat Completion API
從最原始的 HTTP 呼叫到 OpenAI .NET SDK、再到 Semantic Kernel，逐步剖析 ChatCompletion Request/Response 結構；說明 context window 反覆重送的原理，奠定後續 Json Mode 與 Function Calling 的基礎。

### Day 1, Structured Output
闡述為何開發者應要求 LLM 產生 Json 並附 Schema：方便反序列化、明確成功失敗旗標、將非 AI 的數值計算留給程式處理；示範地址萃取案例在三種呼叫方式下的差異。

### Day 2, Function Calling (Basic)
介紹 Tool Use 開啟 Agent 能力的重要性，並以購物清單情境說明如何讓 LLM 自動將自然語言轉為 add/delete 指令序列，完成「Calling」但尚未涵蓋回傳。

### Day 3, Function Calling (Case Study)
以「排定晨跑」為例展示完整呼叫—回傳—再呼叫流程：LLM 先檢查行程、再新增事件、最後向使用者報告，揭示 tool 與 tool-result 角色在 chat history 中的運作方式，並提醒實務可用 SK 將繁瑣流程封裝。

### Day 4, RAG with Function Calling
解釋 RAG 三步驟並指出其本質亦屬 Function Calling 應用；透過 system prompt + tool 定義讓 LLM 主動生成搜尋參數，組裝檢索結果後回答，示範如何快速打造類 Search GPT。

### Day 5, MSKM: RAG as a Service
介紹 Microsoft Kernel Memory 的定位、部署模式與 pipeline；說明它如何補齊 SK 僅有短期 / 抽象向量層的不足，並列出與 SK 的兩大協同優勢：內建 Memory Plugin 與共用 Connector。

### Day 6, 進階 RAG 應用, 生成檢索專用的資訊
分享作者對大量長文（部落格）實驗，證實單純 chunking 命中率不足；提出摘要、FAQ、問題-根因-解法等多視角內容生成，再向量化存入 MSKM，可顯著提升搜尋品質並降低 token 成本。

### Day 7, MSKM 與其他系統的整合應用
比較 GPTs Custom Action、No-Code 平台、MCPServer、SK Plugins 四條整合路徑，點出它們皆滿足「工具宣告 + 統一回傳」兩要件；實作 MCPServer 連結 Claude Desktop，並分享版本踩雷與修補。

### Day 8, 土炮 Function Calling
示範在不支援 Tool Use 的模型上以角色前置詞手動區隔 user 與 tool 對話，依序呼叫 ChatCompletion 即可完成功能；強調理解 protocol 可在任何模型上複製 Function Calling 機制。

### 問券回饋 (統計至 2025/06/22)
收集 93 份問卷，顯示最受青睞主題為架構觀念、Function Calling、RAG 與 MSKM；學員期待進一步探討 MCP、Agent、事件驅動與產業案例，並普遍肯定本課程深度與實用性。