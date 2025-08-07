# [架構師觀點] 開發人員該如何看待 AI 帶來的改變?

## 摘要提示
- PoC實驗: 透過「安德魯小舖 GPTs」示範 LLM + 自建 API 即可完成全流程線上購物。
- API設計: 只有 API First、語意清晰、文件完備的介面，LLM 才能無痛串接。
- UX變革: LLM 能直接理解「意圖」，以對話取代繁瑣操作，重塑使用者體驗。
- LLM中控: 未來系統將以 LLM 為協調中心，UI 與服務成為外掛式插件。
- 微軟佈局: Azure OpenAI、Copilot、Semantic Kernel 形成雲、端、框架三位一體。
- 架構師責任: 帶隊將系統改造成 AI-Ready，精準 API、Task-Oriented UI、正確框架缺一不可。
- 開發者技能: 必備 Prompt、向量資料庫、Semantic Kernel 等新技術並深化 DDD。
- 計算 vs 意圖: 要能區分需精準運算的「計算」與需語意推理的「意圖」工作。
- 框架演進: MVC 將讓位給以 LLM 為核心的 Semantic Kernel 式架構。
- 思維轉換: AI 價值在於理解意圖並協作，軟體角色與流程勢必全面翻新。

## 全文重點
作者以「安德魯小舖 GPTs」PoC 說明 LLM 與現有 API 結合的真實威力：只要公開 Swagger 規格並用自然語言描述角色、目標與限制，GPTs 便能自行決定何時呼叫哪支 API、如何彙整結果並與使用者對談。過程中他發現技術門檻不高，反而是思維門檻巨大——API 不再寫給人而是寫給 AI，用意在讓 LLM 能「望文生義」地正確操作。此體驗引出四層洞察：一、LLM 讓「意圖」與「操作」之間的鴻溝被填平，UX 優化邁向降維打擊；二、LLM 勢必成為系統的協作中樞，所有應用都將圍繞 AI 而設計；三、微軟正以 Azure OpenAI（模型／算力）、Copilot（入口／中控）、Semantic Kernel（開發框架）構築完整生態；四、團隊角色需全面轉型：架構師要負責切分「計算」與「意圖」、設計 AI-Friendly API、挑選正確框架並引入 Task-Oriented UI；開發者則需掌握 AI 工具、Prompt、向量 DB、Semantic Kernel，並深化領域模型與 API 工藝。最終結論是：AI 已成不可逆趨勢，短期可用 Copilot 類工具提升效率，長期則必須在架構、流程、技能與心態上全面 AI 化，方能於新時代立足。

## 段落重點
### 1, 安德魯小舖 GPTs - Demo
作者基於 OpenAI GPTs 建立「安德魯小舖」店長，掛上自建線上商店 API。GPTs 透過 Swagger 自行選擇呼叫 `/products`、`/carts`、`/checkout` 等路徑，完成瀏覽、試算折扣、加購、結帳、查詢歷史等全流程；展示了 LLM 在沒有前端 UI、僅以對話即可補足業務邏輯的能力，也反向證明 API 命名、參數與文件若不合理，LLM 理解與推論就會失靈。

### 1-1, (問) 店裡有賣什麼?
啟動對話後 GPTs 立即呼叫 `GET /api/products`，自動將回傳 JSON 摘要成易讀清單並回覆使用者，顯示其能從接口說明判斷何時發 API 及如何格式化輸出。

### 1-2, (刁難) 預算 與 折扣
作者要求「3000 元內買最多飲料」，GPTs 推演折扣規則、連續試算 `POST /estimate` 多次並給出最佳組合；顯示 LLM 具推理與迭代能力，但亦可能出現答案不穩定，突顯計算任務過度依賴 AI 的風險。

### 1-3, (刁難) 調整訂單
改以口語「多兩罐啤酒」且暗示「家裡有小孩」，GPTs 成功解析同義字與隱含條件，自動更新購物車、過濾酒類再結帳，佐證其語意理解較傳統 Bot 高出數個層次。

### 1-4, (刁難) 整理訂購紀錄
要求統計歷史訂單數量與品項，GPTs 先呼叫 `/member/orders` 取回原始 JSON，再自行摘要、統計並以表格呈現，使複雜數據報表一步到位。

### 1-5, PoC 小結
PoC 暴露兩大重點：1) 整合門檻低但思維門檻高，傳統經驗反成包袱；2) API 成為 AI 與系統唯一溝通管道，必須從「能動就好」進化到「AI 可讀、可推理」。

### 2, 軟體開發的改變
AI 使電腦首度能處理「不明確」指令；LLM 能解碼語意、重組流程，對 UX、架構與角色定位皆是根本性顛覆，開發將從 UI-Driven 轉為 LLM-Driven。

### 2-1, 使用者體驗
過往介面優化只是讓指令更好按，仍需使用者理解操作；LLM 可直接理解目的，讓長輩也能用聊天完成任務，意圖與操作的斷層被填平。

### 2-2, 由 LLM 整合所有資源
LLM 透過 Function Calling 把自然語言轉成 API Call，並自動抽參數、整理結果，形同新一代 Orchestrator；API 若無一致性，Prompt 補不完。

### 2-3, 應用圍繞 AI
未來 UI、流程、服務將包成「Plugins」供 LLM 協調；API 不再寫給人，而是寫給 AI，使「AI-Friendly」成為競爭門檻。

### 2-4, 角色變化
LLM 將嵌入 OS，Copilot 變成主要介面；架構師要懂 AI 中控與分工，前端設計、後端設計到開發流程均需重塑，否則易被淘汰。

### 3, 看懂 Microsoft 的 AI 技術布局
微軟以 Azure OpenAI（模型/算力）、Copilot（入口）、Semantic Kernel（框架）三管齊下，重現當年 Wintel 策略，把 AI 烙印到雲、端、開發生態。

### 3-1, LLM 服務
Azure OpenAI 提供 GPT-4 期貨與私有算力，並計畫將模型縮小到 Edge；未來 AI PC 需 NPU 支援，Windows 12 可能成為第一個 AI OS。

### 3-2, Copilot
Copilot 有望成為 OS 級中控，負責把自然語言映射到各種本地或雲端資源；與 ChatGPT 相似但更能整合硬體、權限與多 App。

### 3-3, AI 開發框架
Semantic Kernel（對標 LangChain）把 Plugins、Planner、Memory、Connector 標準化，讓開發者可快速把服務掛給 LLM；未來還會上伸到 OS、下沉到 PaaS。

### 3-4, 應用模式
Semantic Kernel 示意圖顯示 LLM 站在 Controller/Orchestrator 角色；應用程式將以 Plugins 形式暴露功能，Copilot 等 UI 僅是多元入口。

### 4, 架構師、資深人員該怎麼看待 AI ?
核心任務是引領團隊成為 AI Ready：清楚劃分意圖 vs 計算、重設 API、重拆 UI、導入對話驅動框架，並用有限狀態機確保安全。

### 4-1, 分清楚邊界
精準運算（交易）應留給傳統程式；模糊推理（推薦）交給 LLM，以免性能與正確性失衡。

### 4-2, 精準 API
API 要符合領域模型、有限狀態機、OAuth/Swagger 標準，才能讓 LLM 準確呼叫並避免業務錯誤。

### 4-3, Task 導向 UI
UI 不再全罩式流程，而應切成可被 Copilot 組合的 Task；作者在認證流程花最多時間，就是借鏡。

### 4-4, 選擇框架
需熟悉 Semantic Kernel 結構並正確安置 Kernel、Skill、Planner、Memory 元件，方能累積可重用資產。

### 5, 開發人員該怎麼看待 AI ?
開發者除了用 AI 工具提效，還要升級技術棧、深化領域知識，向「AI 時代的後端工匠」邁進。

### 5-1, 效率工具
應積極採用 ChatGPT、GitHub Copilot、Copilot Chat 等輔助寫碼、除錯、文件撰寫，提高產能並持續學習。

### 5-2, 必要技術
必須掌握 Prompt Engineering、向量資料庫、Semantic Kernel 或 LangChain 等框架，並學會部署 RAG 與管理 API 金鑰。

### 5-3, 深化領域
DDD、API First、微服務拆分能力更形關鍵；沒有精準的領域 API，服務將成 LLM 時代孤島。

### 6, 結論
AI 不再只是輔助工具，而是驅動新架構、新流程的核心力量；短期先用工具提效，長期要在思維、架構、技能上全面 AI 化。作者借 PoC 體悟：趁早擁抱變革、精準設計 API、啟用對話驅動框架，才能在 AI 世代保有競爭力。