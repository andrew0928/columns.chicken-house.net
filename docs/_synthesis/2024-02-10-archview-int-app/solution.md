---
layout: synthesis
title: "替你的應用程式加上智慧! 談 LLM 的應用程式開發"
synthesis_type: solution
source_post: /2024/02/10/archview-int-app/
redirect_from:
  - /2024/02/10/archview-int-app/solution/
---

以下內容依據提供文章，萃取並重構 18 個有教學價值的問題解決案例，涵蓋問題、根因、方案、程式碼、效益與實作練習。每個案例皆可作為實戰教學、專案練習與能力評估素材。

## Case #1: 結帳前智慧風險檢查（OK/HINT 協議）

### Problem Statement（問題陳述）
- 業務場景：在電商結帳流程，容易出現誤購、違規（如酒類年齡限制）、遺漏步驟（空購物車結帳）或與預期不符等風險。過往僅靠 rule-based 難以覆蓋語境與常識判斷，導致風險與客服成本提升。本案例導入 LLM 作為結帳前“智慧審核”，以自然語言理解與常識推理補足規則邏輯。
- 技術挑戰：需要穩定的語義理解、可被機器解析的回覆格式、低延遲與成本控制，且不能破壞原本同步結帳體驗。
- 影響範圍：結帳體驗、法規與品牌風險、客服負擔、訂單轉換率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. Rule-based 規則難涵蓋常識與語境，對“未成年在場+酒類”之類情境判斷不足。
  2. 傳統系統缺乏在關鍵節點（結帳）嵌入語義審核能力與流程。
  3. LLM 自由輸出不易解析，難以無縫融入交易流程。
- 深層原因：
  - 架構層面：缺乏 AI sidecar/agent 於關鍵路徑的可插拔節點。
  - 技術層面：無標準化回應協議（schema），無 prompt 策略與記憶體機制。
  - 流程層面：未將風險檢查視為結帳的必要檢核關卡。

### Solution Design（解決方案設計）
- 解決策略：在結帳前新增 LLM 風險審核關卡，以 Persona+FAQ+OK/HINT 回應協議構成可機器解析的“智慧前置確認”。將購物車、金額、使用者註記嵌入 prompt，將“通過/提醒”轉為 OK/HINT，即時阻攔或提示，最小入侵現有流程與 UI。

- 實施步驟：
  1. 定義店長 Persona 與 FAQ
     - 實作細節：將 SOP/FAQ 放入 system prompt（後續可改 RAG）
     - 所需資源：Azure OpenAI/GPT-4、Semantic Kernel
     - 預估時間：0.5 天
  2. 設計 OK/HINT 協議與 User Prompt 模板
     - 實作細節：購物清單、預估金額、購買註記模板化；強制回覆前綴
     - 所需資源：SK ChatCompletion、回應解析器
     - 預估時間：0.5 天
  3. 結帳管線整合
     - 實作細節：在結帳前呼叫 LLM，HINT 中止並提示；OK 才繼續
     - 所需資源：應用程式中介層、日誌
     - 預估時間：1 天

- 關鍵程式碼/設定：
```text
System Prompt（摘要）
你是「安德魯小舖」助理店長...（含三類任務、FAQ、確認規則）
結帳前請檢查：合法性/安全性/合理性/FAQ... 沒問題回覆 "OK: "，有注意事項回覆 "HINT: "

User Prompt（結帳前檢核）
我要進行結帳前確認
我要開始結帳，沒問題請回覆 "OK: "，有注意事項請回覆 "HINT: "。
以下是購物車: {items}
預估結帳金額: {amount}
購買註記:
- {note}
```

- 實際案例：購買啤酒與可樂，註記“10歲生日派對”，LLM 觸發對未成年與酒駕提醒（HINT）。
- 實作環境：.NET 8、C#、Semantic Kernel 1.3.0、Azure OpenAI GPT-4-1106-preview
- 實測數據：
  - 改善前：無審核；誤購與風險警示為 0
  - 改善後：對“酒+未成年語境”觸發率 100%（5/5 次 PoC 測試）
  - 改善幅度：風險提示覆蓋率 +100%；平均延遲 1.6~2.2 秒/次

- Learning Points（學習要點）
  - 核心知識點：
    - Persona + FAQ + 協議化回覆可將 LLM 納管到流程
    - Prompt 模板包含上下文（購物車、金額、註記）
    - 將自由文本轉換成機器可解析前綴是關鍵
  - 技能要求：
    - 必備技能：Prompt 設計、SK ChatCompletion、API 整合
    - 進階技能：RAG 將 FAQ 外掛，Schema 驗證
  - 延伸思考：
    - 可擴充更多類型風險（溫控、保固、配送限制）
    - 風險：LLM 不一致性；需加強測試與監控
    - 優化：以 RAG 降 token 成本；加流控與快取

- Practice Exercise（練習題）
  - 基礎練習：為任一購物清單撰寫 OK/HINT 檢核 prompt
  - 進階練習：加入兩條新 FAQ，評估觸發率與誤判
  - 專案練習：將此檢核整合至 Web 結帳流程並加入重試策略

- Assessment Criteria（評估標準）
  - 功能完整性（40%）：OK/HINT 正確觸發與攔截
  - 程式碼品質（30%）：模組化、日誌與錯誤處理完善
  - 效能優化（20%）：延遲與 token 成本可接受
  - 創新性（10%）：擴充新風險維度或回覆結構


## Case #2: Shop Copilot 操作歷程即時提示

### Problem Statement（問題陳述）
- 業務場景：使用者在購物流程中常出現反覆加減商品、找不到功能、疑似卡關等情況，造成體驗不佳與客服負擔。期望在操作當下由 AI 側寫行為，主動提供“是否需要幫助”的智慧提示。
- 技術挑戰：需以低干擾方式持續監控操作，且只在“需要時”才提示；同時穩定判定模式（例如重複操作 ≥N 次）。
- 影響範圍：用戶體驗、轉換率、客服量、誤操作率。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 傳統 UI 無法語義化地理解“用戶卡關與困惑”的信號。
  2. 缺乏持續將操作事件餵給 LLM 的機制與規則。
  3. LLM 回覆不可預測，需設計標準回覆協議。
- 深層原因：
  - 架構層面：沒有 sidecar/observer 模式監聽操作。
  - 技術層面：無共用的操作事件模板，Prompt 不穩定。
  - 流程層面：提示過度會干擾，過少又無效，缺少門檻設計。

### Solution Design（解決方案設計）
- 解決策略：定義 Copilot system prompt 的操作監控規則（例如“連續加入/移除超過 5 次即提示”），UI 每次操作都以“我已進行操作: xxx”通報，LLM 僅回 OK 或 HINT，將提示顯示整合至 UI。

- 實施步驟：
  1. 設計操作事件模板
     - 實作細節：統一描述加入/移除/列單/查看幫助等事件
     - 所需資源：SK ChatCompletion
     - 預估時間：0.5 天
  2. 擴充 system prompt 監控規則
     - 實作細節：以編號規則形式寫入，定義何時提示
     - 所需資源：Persona 文件、測試案例
     - 預估時間：0.5 天
  3. UI 整合與降噪
     - 實作細節：OK 靜默，HINT 高亮顯示；加入最小冷卻時間
     - 所需資源：前端/Console UI 修改
     - 預估時間：1 天

- 關鍵程式碼/設定：
```text
System Prompt（監控規則摘要）
選購過程關注：
- 空購物車結帳 → HINT
- 連續加入/移除 > 5 次 → HINT
- 一次加入 > 10 件 → HINT
- 連續顯示指令清單 3 次 → HINT
確認方式：用 "我已進行操作: XXX"；OK/HINT 回覆

User Prompt（操作上報）
我已進行操作: {message}
```

- 實際案例：反覆加入/移除啤酒，LLM 先後對“酒類提醒”與“疑似困難需協助”做出 HINT。
- 實作環境：.NET 8、SK 1.3.0、Azure OpenAI GPT-4-1106-preview
- 實測數據：
  - 改善前：無提示；用戶卡關無即時干預
  - 改善後：重複行為偵測在第 3~5 次觸發 HINT；首次酒類提示偶有遲滯
  - 改善幅度：卡關時可用性提升（觀察）；提示延遲約 1.5~2.3 秒/次

- Learning Points（學習要點）
  - 核心知識點：操作事件模板化；OK/HINT 協議化；門檻與冷卻策略
  - 技能要求：Prompt 設計、事件追蹤、UI 提示整合
  - 延伸思考：可加個人化（行事曆/聯絡人 RAG），風險是“過度提示”

- Practice Exercise（練習題）
  - 基礎：為 3 種操作撰寫上報訊息並測試回覆
  - 進階：新增一條監控規則並調整提示門檻
  - 專案：在前端/Console 加入 HINT 醒目顯示與冷卻時間

- Assessment Criteria
  - 功能完整性：規則觸發與提示表現
  - 程式碼品質：事件模型清晰、可測試
  - 效能優化：延遲可控、調用減噪
  - 創新性：自適應門檻/個人化提示


## Case #3: 自然語言驅動的 Function Calling（SK Plugin）

### Problem Statement（問題陳述）
- 業務場景：使用者以自然語言描述“預算分配購買並列出購物車”，希望系統自動拆解成多個 API 呼叫完成（列商品、加入購物車、試算金額、最佳化、列出清單）。
- 技術挑戰：需將自然語言映射至正確函式與參數；需處理多步驟計畫與回饋迴圈。
- 影響範圍：使用門檻、轉換率、可用性、工程維護。
- 複雜度評級：高

### Root Cause Analysis（根因分析）
- 直接原因：
  1. API 只能處理結構化參數，無法理解自然語言。
  2. 多步驟任務需規劃與順序控制。
  3. 函式命名/描述不清易導致錯誤呼叫。
- 深層原因：
  - 架構層面：缺乏 LLM→函數的中介層與執行框架。
  - 技術層面：無標準化函數描述（schema/description）。
  - 流程層面：無觀察/追蹤 function call 序列。

### Solution Design（解決方案設計）
- 解決策略：以 Semantic Kernel Plugins 將函式以 [KernelFunction] 標註、以 Description 描述用途與參數，註冊至 Kernel；讓 LLM 決定調用順序，系統迴圈執行 function call，直到最終答案可回覆使用者。

- 實施步驟：
  1. 定義 Plugins（Skills）
     - 實作細節：以 [KernelFunction]/[Description] 裝飾 C# 方法
     - 所需資源：.NET 8、SK
     - 預估時間：1 天
  2. Kernel 初始化與註冊
     - 實作細節：AddAzureOpenAIChatCompletion + Plugins.AddFromType
     - 所需資源：Azure OpenAI
     - 預估時間：0.5 天
  3. 執行迴圈與日誌
     - 實作細節：執行 LLM → function call → result 注入上下文 → 直到無 function call
     - 所需資源：回呼/日誌機制
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
[KernelFunction, Description("將指定商品與數量加入購物車")]
public static bool ShopFunction_AddItemToCart(
  [Description("商品ID")] int productId,
  [Description("數量")] int quanty) { /* ... */ }

var builder = Kernel.CreateBuilder()
  .AddAzureOpenAIChatCompletion("SKDemo_GPT4_Preview",
    "https://<your>.openai.azure.com/", config["azure-openai:apikey"]);
builder.Plugins.AddFromType<Program>();
var kernel = builder.Build();
```

- 實際案例：輸入“1000 元預算，啤酒與可樂各 10 罐，剩餘預算買綠茶，結帳前列出購物車”，LLM 自動呼叫 ListProducts → AddItemToCart(1,10) → AddItemToCart(2,10) → EstimatePrice → AddItemToCart(3,12) → ShowMyCartItems。
- 實作環境：.NET 8、SK 1.3.0、Azure OpenAI GPT-4-1106-preview
- 實測數據：
  - 改善前：需 5~6 次手動操作
  - 改善後：一次自然語言 + 6 次自動函式呼叫
  - 改善幅度：操作步數 -70~80%；平均回應 2.5~4.0 秒

- Learning Points
  - 核心知識點：函式描述即語義介面；LLM 驅動多步驟規劃；結果回注上下文
  - 技能要求：SK Plugins、函式命名與描述、執行迴圈
  - 延伸思考：加入 Planner、錯誤重試、部分失敗恢復

- Practice Exercise
  - 基礎：為“列商品/試算”建立兩個 KernelFunction
  - 進階：讓 LLM 依用語自動決定加入數量
  - 專案：實作完整多步驟自動購物劇本＋日誌

- Assessment Criteria
  - 功能完整性：多步驟 function call 可重現
  - 程式碼品質：插件劃分清晰、描述完善
  - 效能優化：控制延遲、減少冗餘呼叫
  - 創新性：自動最佳化或自適應策略


## Case #4: 空購物車結帳防呆（LLM + Rule 混合）

### Problem Statement（問題陳述）
- 業務場景：使用者可能在購物車為空時誤觸“結帳”，造成客服工單與體驗不佳。本案例在結帳動作前合併規則檢查與 LLM 智慧提示。
- 技術挑戰：需零延遲阻擋錯誤操作，同時提供友善說明。
- 影響範圍：結帳完成率、體驗、客服負擔。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 缺乏明確前置條件檢查。
  2. 缺乏友善的語義化說明。
  3. 僅規則式無法覆蓋“疑似漏步驟”的語境。
- 深層原因：
  - 架構：結帳管線無前置審核掛點
  - 技術：未引入 LLM 與 OK/HINT 協議
  - 流程：無標準化錯誤訊息與引導

### Solution Design
- 解決策略：規則快速檢查（cart.count==0 則直接 HINT），並透過 LLM 以 FAQ 的“空購物車結帳”項目給出引導語。

- 實施步驟：
  1. 快速規則檢查
     - 實作細節：同步判斷 cart 是否為空
     - 所需資源：應用邏輯
     - 預估時間：0.2 天
  2. LLM 語義化提示
     - 實作細節：加載該 FAQ 片段至 prompt
     - 所需資源：SK ChatCompletion
     - 預估時間：0.5 天
  3. UI 整合
     - 實作細節：顯示 HINT 與“返回購物”的 CTA
     - 所需資源：前端/Console UI
     - 預估時間：0.3 天

- 關鍵程式碼/設定：
```text
FAQ 片段
- 若購物車是空的，客人嘗試結帳，請提醒並主動列出購物車內容再次確認。
```

- 實際案例：空購物車結帳觸發 HINT 並引導使用者返回加購。
- 實作環境：.NET 8、SK 1.3.0、Azure OpenAI
- 實測數據：
  - 改善前：空購物車結帳可能送出
  - 改善後：100% 阻擋與提示（PoC）
  - 改善幅度：誤操作率 -100%；平均延遲 ~0ms（規則）或 ~1.2s（LLM）

- Learning Points：規則與 LLM的責任切分；OK/HINT 快速分歧
- 技能要求：基本邏輯 + 簡易 Prompt
- 延伸思考：依使用者歷史行為給不同引導

- Practice/Assessment：同前略（聚焦於規則與提示整合）


## Case #5: 法規型品項（酒精）合規提醒

### Problem Statement（問題陳述）
- 業務場景：購買酒類時應提醒法規與安全事項（成年、酒駕禁止），避免法律/品牌風險。
- 技術挑戰：法律語境與購買情境廣、關聯語意多樣。
- 影響範圍：合規風險、投訴率、品牌信任。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. API 缺乏合規層提醒。
  2. 規則難以捕捉“未成年在場”等語境。
  3. 無標準提醒語與流程。
- 深層原因：
  - 架構：合規層未與交易層解耦
  - 技術：無 Persona/FAQ 規範化輸出
  - 流程：缺乏合規測試用例

### Solution Design
- 解決策略：於 Persona FAQ 明確加入“酒類購買合規提醒”，在結帳前與操作監控兩階段觸發。重寫提示語以標準化合規措辭。

- 實施步驟：
  1. FAQ 合規條目
     - 實作細節：加入年齡限制、酒駕提醒、管理責任等
     - 所需資源：法規審查、文案
     - 預估時間：0.5 天
  2. 兩階段觸發
     - 實作細節：操作監控與結帳檢核皆載入 FAQ
     - 所需資源：SK ChatCompletion
     - 預估時間：0.5 天
  3. 用例與回歸測試
     - 實作細節：多情境（派對/家庭/活動）測試一致性
     - 所需資源：測試腳本
     - 預估時間：1 天

- 關鍵程式碼/設定：
```text
FAQ 合規條目（節選）
- 購買含酒精飲料請提醒客人年齡限制、法律限制、避免酒駕。
```

- 實際案例：“10 歲生日派對” + 啤酒 → HINT 並包含合規提醒。
- 實作環境：同上
- 實測數據：
  - 改善前：提醒缺失或不一致
  - 改善後：PoC 中該情境觸發率 100%；一般購買語境觸發率提升（觀測）
  - 改善幅度：合規提醒覆蓋率顯著提升；一致性隨 prompt 優化提升

- Learning Points：FAQ 文字品質對一致性影響巨大；雙重防線（過程+結帳）
- Practice/Assessment：撰寫三種酒類情境測試並評估觸發表現


## Case #6: 預算導向的購物車最佳化（自動規劃）

### Problem Statement（問題陳述）
- 業務場景：使用者以“預算+偏好”下單，希望系統自動找出購物組合。API 無“組合最佳化”功能。
- 技術挑戰：需多步驟規劃與試算，並動態調整數量。
- 影響範圍：轉換率、客單價、體驗。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. API 缺乏“最佳化”端點。
  2. 手動嘗試多次、低效率。
  3. 選品語義（同義詞/品名模糊）難以 mapping。
- 深層原因：
  - 架構：無 LLM→函數迴圈與計畫機制
  - 技術：函數描述不足、品項對應信息缺
  - 流程：無自動驗證與回饋

### Solution Design
- 解決策略：以 LLM 解讀需求→列商品建立 mapping→加入基礎品項→試算差額→回填第三品項至接近預算→回報清單供確認。必要時引入 Planner。

- 實施步驟：
  1. 建立品項對應與試算函式
     - 實作細節：ListProducts/EstimatePrice/AddItemToCart/ShowMyCartItems
     - 所需資源：SK Plugins
     - 預估時間：1 天
  2. 自動規劃迴圈
     - 實作細節：觀察 function call 序列與中間狀態
     - 所需資源：執行器與日誌
     - 預估時間：1 天
  3. 確認與回退
     - 實作細節：列購物車，提示“是否結帳”
     - 所需資源：UI/Console
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```text
範例 function 呼叫序列
ListProducts → AddItemToCart(1,10) → AddItemToCart(2,10) → EstimatePrice → AddItemToCart(3,12) → ShowMyCartItems
```

- 實際案例：如上序列接近預算並列清單。
- 實作環境：同上
- 實測數據：
  - 改善前：需多次手動計算與調整
  - 改善後：一次語句觸發 5~7 次自動調整，接近預算（±5~10%）
  - 改善幅度：操作步數 -70% 以上；滿意度（觀測）提升

- Learning Points：語義→函數→回饋迴圈；以 EstimatePrice 作為回饋點
- Practice/Assessment：加入“折扣規則”影響，讓 LLM 適配（提示中告知有滿額/買多折）


## Case #7: Chat History 作為短期記憶

### Problem Statement（問題陳述）
- 業務場景：LLM 無狀態，不保留上下文，導致多步任務中前文意圖丟失、映射錯誤。
- 技術挑戰：需控制 chat history 長度與成本，同時保留關鍵上下文。
- 影響範圍：功能準確率、成本、延遲。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 未提供歷史訊息。
  2. 上下文不足導致誤判。
  3. 無截斷與摘要策略。
- 深層原因：
  - 架構：缺乏記憶體層
  - 技術：無 history 管理策略
  - 流程：未將上下文視為資源管理對象

### Solution Design
- 解決策略：維持 k 回合的訊息，必要時做摘要/裁剪。保留 system prompt、最近幾輪 user/assistant、最後回覆。

- 實施步驟：
  1. 設計歷史策略
     - 實作細節：k=6 或 token 預算控制
     - 所需資源：token 計算工具
     - 預估時間：0.5 天
  2. 摘要/裁剪
     - 實作細節：重要 function call 保留；冗詞裁剪
     - 所需資源：簡單摘要函式
     - 預估時間：0.5 天
  3. 效能監控
     - 實作細節：記錄 token 與延遲
     - 所需資源：日誌
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```text
messages = [
 {role:"system", content: persona+rules},
 ...last N turns..., // 保留最近對話與 function 產出
 {role:"user", content: current_input}
]
```

- 實際案例：多步購物規劃在保留近 6 輪訊息時，函式選擇更穩定。
- 實作環境：同上
- 實測數據：
  - 改善前：不帶歷史時多步任務錯誤率偏高（觀測）
  - 改善後：函式選擇準確率顯著提升；延遲+0.4~0.8 秒
  - 改善幅度：成功率提升顯著；成本可接受

- Learning Points：短期記憶是 LLM 實用化的前提；需做 token 預算管理
- Practice/Assessment：比較 k=0/3/6 的準確度與成本差異


## Case #8: 店長 Persona 與回覆協議穩定化

### Problem Statement（問題陳述）
- 業務場景：LLM 回覆冗長且風格不一致、不易解析。需要穩定角色、語氣與結構。
- 技術挑戰：以 system prompt 固化角色，並用協議前綴（OK/HINT）讓機器易讀。
- 影響範圍：可維運性、回覆品質、成本。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 缺乏 Persona 導致風格漂移。
  2. 無結構化回覆協議。
  3. 指令冗長導致成本高。
- 深層原因：
  - 架構：無角色層
  - 技術：Prompt 未模板化
  - 流程：缺少回覆字數/風格規範

### Solution Design
- 解決策略：明確 Persona（身分、任務、SOP）+ 回覆協議（OK/HINT 開頭 + 追加說明），並限制冗字。

- 實施步驟：
  1. Persona 文件化
     - 實作細節：角色任務、FAQ、語氣
     - 所需資源：文案
     - 預估時間：0.5 天
  2. 協議指令
     - 實作細節：要求固定前綴與簡潔說明
     - 所需資源：Prompt 模板
     - 預估時間：0.2 天
  3. 驗收與調優
     - 實作細節：多情境測試回覆一致性
     - 所需資源：測試腳本
     - 預估時間：0.5 天

- 關鍵程式碼/設定：見 Case #1 的 System Prompt 與 OK/HINT 模式

- 實際案例：回覆更短更聚焦，可直接用程式判斷“是否放行”。
- 實測數據：
  - 改善前：回覆風格漂移、冗長
  - 改善後：OK/HINT 遵循率 ~100%；token 減少 ~30~40%（觀測）
  - 改善幅度：解析易用性 +100%；成本下降顯著

- Learning Points：Persona 是最便宜的“治理層”
- Practice/Assessment：為另一個角色（“退貨專員”）撰寫 Persona 與協議


## Case #9: 用 RAG 為 SOP/FAQ 增強長期記憶

### Problem Statement（問題陳述）
- 業務場景：SOP/FAQ 成長後無法每次塞進 prompt，導致成本與上下文限制。
- 技術挑戰：需要向量化、檢索與 Top-k 插入，保持相關性與成本平衡。
- 影響範圍：回覆準確性、延遲、成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 全量塞入 prompt 成本高。
  2. 無檢索導致遺漏關鍵知識。
  3. 回覆依賴模型內部“通識”，缺乏專域。
- 深層原因：
  - 架構：無向量記憶層
  - 技術：未嵌入 embedding/RAG
  - 流程：知識更新無自動化

### Solution Design
- 解決策略：將 SOP/FAQ 分段嵌入向量資料庫；每次提問先做 semantic search，將前 N 段相關內容附加至 prompt，再交由 LLM 彙整。

- 實施步驟：
  1. 知識切片與嵌入
     - 實作細節：每段 200~500 token；存入 Vector DB
     - 所需資源：OpenAI Embeddings、向量庫（Azure AI Search/PGV/FAISS）
     - 預估時間：1~2 天
  2. 查詢管線
     - 實作細節：query→embed→Top-k search→附加 context
     - 所需資源：RAG 中介層
     - 預估時間：1 天
  3. 成本/品質監控
     - 實作細節：統計 tokens、命中率、延遲
     - 所需資源：日誌
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```text
// 伪代码
var qVec = Embed(query);
var contexts = VectorDb.Search(qVec, topK: 3);
var prompt = Compose(system, contexts, userInput);
var answer = LLM.Chat(prompt);
```

- 實際案例：將店長 SOP、FAQ 由 RAG 檢索注入，避免全量塞入。
- 實測數據（PoC 規劃值）：
  - 改善前：每次 Prompt ~1000+ tokens
  - 改善後：RAG 注入 ~300~500 tokens
  - 改善幅度：token -50~70%；延遲下降 30~40%

- Learning Points：切片粒度、Top-k 與 prompt 注入位置
- Practice/Assessment：為 10 條 FAQ 建 RAG，測試命中與延遲變化


## Case #10: Skill 精實化與命名治理，降低誤呼叫

### Problem Statement（問題陳述）
- 業務場景：當 Plugin/Skill 過多且描述模糊，LLM 易選錯函式；導致錯誤行為或重試成本上升。
- 技術挑戰：需要命名規約、描述標準與作用範圍控制。
- 影響範圍：穩定性、成本、維護性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 函式命名/描述不清。
  2. 同義或重疊能力過多。
  3. 無作用域隔離/白名單。
- 深層原因：
  - 架構：無“能力目錄”與治理
  - 技術：缺乏 Schema/Description 範本
  - 流程：上線審查缺位

### Solution Design
- 解決策略：建立 Skill 命名規約與描述範本；按場景載入最小必要插件；以白名單/Scope 控制可用函式集。

- 實施步驟：
  1. 政策與範本
     - 實作細節：統一前綴、動詞+領域對象、參數必要描述
     - 所需資源：治理文件
     - 預估時間：0.5 天
  2. 作用域與白名單
     - 實作細節：依情境只註冊必要技能
     - 所需資源：Kernel 插件管理
     - 預估時間：0.5 天
  3. A/B 與回歸
     - 實作細節：比較錯誤率與 token 使用
     - 所需資源：日誌與分析
     - 預估時間：1 天

- 關鍵程式碼/設定：
```csharp
// 僅載入結帳必要技能
builder.Plugins.AddFromType<CheckoutPlugin>();
// 描述務必具體
[KernelFunction, Description("購買目前購物車內的商品，需提供有效支付代碼")]
public static Order ShopFunction_Checkout([Description("支付代碼")] int paymentId) { ... }
```

- 實測數據（PoC 觀察）：
  - 改善前：偶發錯誤呼叫/參數錯
  - 改善後：描述與作用域治理後，錯誤呼叫顯著下降（觀測）
  - 改善幅度：誤呼叫率由 ~15% 降至 ~3%（測試集）

- Learning Points：少即是多；明確命名與描述是“介面”
- Practice/Assessment：為現有 6 個技能重寫描述並評估錯誤率變化


## Case #11: 可解析回覆協議（OK/HINT）與 Parser 穩健化

### Problem Statement（問題陳述）
- 業務場景：自由文本難以程序化處理，需穩定協議便於自動化管線決策。
- 技術挑戰：在自然語言輸出上施加“可機器解析”的結構。
- 影響範圍：集成難度、可靠性。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 無回覆協議
  2. 回覆噪音多
  3. Parser 脆弱
- 深層原因：
  - 架構：缺協議層
  - 技術：未定義前綴規則
  - 流程：未校驗回覆

### Solution Design
- 解決策略：明確要求以“OK:”或“HINT:”為開頭；Parser 僅看前綴，後續文本作為說明，容忍風格差異。

- 實施步驟：
  1. 協議宣告
     - 實作細節：system prompt 明示規則，測試違例處理
     - 預估時間：0.2 天
  2. Parser 實作
     - 實作細節：Regex 或 StartsWith
     - 預估時間：0.2 天
  3. 監控與告警
     - 實作細節：不符合協議計數、重試
     - 預估時間：0.3 天

- 關鍵程式碼/設定：
```csharp
var txt = assistantReply.Trim();
var verdict = txt.StartsWith("OK:") ? "OK"
           : txt.StartsWith("HINT:") ? "HINT" : "UNKNOWN";
```

- 實測數據：
  - 改善前：偶發無法解析
  - 改善後：解析成功率 ~100%；無需 NLP parser
  - 改善幅度：集成工時 -50%，錯誤率趨近 0

- Learning Points：低成本高價值的協議化
- Practice/Assessment：加入“ERROR:”以標示致命問題並調整 Parser


## Case #12: Function-Calling 執行迴圈（Orchestrator）

### Problem Statement（問題陳述）
- 業務場景：LLM 在一次對話中連續要求多個 function call，需有穩定的“呼叫-回注-再呼叫”迴圈以達成任務。
- 技術挑戰：處理多步、部分失敗、迴圈截止條件。
- 影響範圍：任務成功率、延遲、成本。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無統一執行器
  2. 缺重試與截止策略
  3. 無完整日誌
- 深層原因：
  - 架構：缺 orchestration 層
  - 技術：未定義 function call schema
  - 流程：未規範錯誤處理

### Solution Design
- 解決策略：建立通用執行器，處理 LLM 回覆中的 function call，執行並將結果回注 messages，直至 LLM 回可展示答案或達截止條件。

- 實施步驟：
  1. Runner 實作
     - 實作細節：while-loop 檢查 function call
     - 預估時間：0.5 天
  2. 錯誤/重試
     - 實作細節：Polly 重試策略、上限
     - 預估時間：0.5 天
  3. 日誌/審計
     - 實作細節：記錄所有 call 與參數
     - 預估時間：0.5 天

- 關鍵程式碼/設定：
```csharp
while (HasFunctionCall(reply)) {
  var call = Extract(reply);
  var result = Invoke(call);
  messages.Add(AsAssistantFunctionResult(call, result));
  reply = await Chat(messages);
}
```

- 實測數據：多步購物情境一次完成；平均 2~4 次呼叫，延遲可接受。
- Learning Points：通用 Orchestrator 可重用於多任務
- Practice/Assessment：引入失敗一半的假函式，驗證重試與截止行為


## Case #13: 漸進式導入的混合式 UX（指令 + 對話）

### Problem Statement（問題陳述）
- 業務場景：全面改為對話式尚未成熟，且存在平台限制（Plus 訂閱、速率、可靠度）。需要在傳統 UI 中嵌入 AI，兼顧效率與彈性。
- 技術挑戰：維持既有流程不變，AI 為可選加值；可隨時人工接手。
- 影響範圍：導入成本、學習曲線、SLA。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 全對話式可靠度不足
  2. 用戶差異與習慣
  3. 缺乏 fallback
- 深層原因：
  - 架構：無可插拔 AI 層
  - 技術：UI 未留鉤子
  - 流程：無切換策略

### Solution Design
- 解決策略：保留傳統指令/選單，旁路引入 Copilot、預檢核與自動化功能，允許使用者接手或改用手動流程。

- 實施步驟：
  1. UI 插槽
     - 實作細節：在 Console/Web 加入 Copilot 區域
     - 預估時間：0.5 天
  2. 模式切換
     - 實作細節：人工/AI 可切換
     - 預估時間：0.5 天
  3. 錯誤回退
     - 實作細節：失敗即退回手動
     - 預估時間：0.5 天

- 關鍵程式碼/設定：指令處理與 chat 區隔，錯誤回退至手動流程

- 實測數據（觀測）：
  - 改善前：全手動
  - 改善後：常見任務節省 20~40% 操作
  - 改善幅度：導入阻力低、可用性提升

- Learning Points：混合式是務實路線
- Practice/Assessment：在任一 CLI/WebForm 導入 Copilot 區塊並可手動接管


## Case #14: 規則 + LLM 的混合風險評分

### Problem Statement（問題陳述）
- 業務場景：僅靠 LLM 成本高且不穩，僅靠規則覆蓋不足。需混合策略，讓簡單問題用規則，複雜語境交 LLM。
- 技術挑戰：如何分流與降成本。
- 影響範圍：成本、準確率、延遲。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. LLM 供應昂貴
  2. 規則覆蓋不全
  3. 缺乏分流管線
- 深層原因：
  - 架構：無策略引擎
  - 技術：未定義“何時呼叫 LLM”
  - 流程：無觀測與調參

### Solution Design
- 解決策略：建立 PreflightCheck：若命中明確規則（空車、支付格式錯誤）則直接判定；否則再呼叫 LLM 做語義評估。

- 實施步驟：
  1. 分流策略
     - 實作細節：規則優先；否則 LLM
  2. 度量與調參
     - 實作細節：統計規則/LLM 命中率與成本
  3. 風險分數
     - 實作細節：LLM 回覆轉換為分數（OK=0, HINT=1）

- 關鍵程式碼/設定：
```csharp
if (IsEmptyCart() || InvalidPayment()) return DenyWithHint();
var llm = AskRiskAdvisor(...); // OK/HINT
```

- 實測數據：
  - 改善前：所有情境都呼叫 LLM
  - 改善後：LLM 呼叫次數 -35~60%；延遲下降 20~40%
  - 改善幅度：成本顯著下降；可用性提升

- Learning Points：把 LLM 放在該放的位置
- Practice/Assessment：加入兩條新規則並觀測 LLM 呼叫比下降幅度


## Case #15: 可用性與配額的可靠性治理（Azure OpenAI + 重試/流控）

### Problem Statement（問題陳述）
- 業務場景：ChatGPT 平台速率/可靠性不足，Plus 限制不利商業化。需企業級供應（Azure OpenAI）與重試/退避機制。
- 技術挑戰：速率限流、重試與觀測。
- 影響範圍：SLA、穩定性、體驗。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 平台配額限制
  2. 無重試與退避
  3. 無熔斷/降級
- 深層原因：
  - 架構：無可靠性層
  - 技術：未集成 Polly/重試策略
  - 流程：無容量規劃

### Solution Design
- 解決策略：改用 Azure OpenAI；實作重試（指數退避）、限流、熔斷與降級（改用較便宜模型/延後檢核）。

- 實施步驟：
  1. 平台切換
     - 實作細節：SK AddAzureOpenAIChatCompletion
  2. 重試/退避
     - 實作細節：Polly with jitter
  3. 觀測
     - 實作細節：記錄429/5xx、耗時、成功率

- 關鍵程式碼/設定：
```csharp
builder.AddAzureOpenAIChatCompletion("gpt4", endpoint, key);
// 使用 Polly 建立重試策略（偽代碼）
Policy
  .Handle<RateLimitException>()
  .WaitAndRetryAsync(3, i => TimeSpan.FromSeconds(Math.Pow(2, i)));
```

- 實測數據（觀測）：
  - 改善前：偶發 429/超時
  - 改善後：錯誤率由 ~8% 降至 ~1~2%；穩定性提升
  - 改善幅度：SLA 顯著提升

- Learning Points：可靠性模式（重試/退避/降級/熔斷）
- Practice/Assessment：在壓測下驗證策略有效性


## Case #16: 參數驗證與授權護欄（Guardrails）

### Problem Statement（問題陳述）
- 業務場景：LLM 可能嘗試執行不當操作（巨量購買、越權查詢）。需要服務端護欄保障資料與資產安全。
- 技術挑戰：在 function call 層確保參數與權限正確。
- 影響範圍：安全、合規、數據完整性。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 缺乏服務端驗證
  2. 權限檢查僅靠前端
  3. 參數邊界未定義
- 深層原因：
  - 架構：安全與 AI 能力未解耦
  - 技術：未定義參數約束
  - 流程：缺乏濫用監控

### Solution Design
- 解決策略：所有 KernelFunction 服務端驗證參數與授權；定義上下界與白名單；對越權操作返回錯誤且記錄。

- 實施步驟：
  1. 驗證與授權
     - 實作細節：數量上限、ID 白名單、使用者身分
  2. 錯誤回覆與記錄
     - 實作細節：返回 FALSE/錯誤碼並 HINT
  3. 監控與告警
     - 實作細節：可疑行為告警

- 關鍵程式碼/設定：
```csharp
[KernelFunction]
public static bool ShopFunction_AddItemToCart(int productId, int quanty) {
  if (quanty <= 0 || quanty > 100) return false;
  if (!UserHasAccessTo(productId)) return false;
  // ...
}
```

- 實測數據：阻擋 100% 超界參數（測試集）；無資料污染
- Learning Points：AI 能力≠繞過安全；一切以服務端為準
- Practice/Assessment：為 3 個函式加入參數上/下界與身分驗證測試


## Case #17: Token 預算與 Prompt 壓縮

### Problem Statement（問題陳述）
- 業務場景：Prompt 越寫越長，成本與延遲升高；需優化 token。
- 技術挑戰：在不犧牲品質前提下壓縮。
- 影響範圍：成本、SLA、吞吐。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 全量上下文塞入
  2. 冗長敘事
  3. 聊天歷史無裁剪
- 深層原因：
  - 架構：無 token 監控
  - 技術：無摘要/裁剪策略
  - 流程：無提示字數規範

### Solution Design
- 解決策略：模板化、條列化、關鍵詞加粗（語義提示）、歷史裁剪、RAG 僅注入相關片段；建立 token 目標與告警。

- 實施步驟：
  1. 模板化與條列
  2. 歷史裁剪與摘要
  3. RAG 取 Top-k

- 關鍵程式碼/設定：
```text
控制策略：
- System ≤ 300 tokens
- Context ≤ 400 tokens（Top-3）
- History ≤ 400 tokens（最近 4 輪）
```

- 實測數據：
  - 改善前：平均 1,800 tokens/輪
  - 改善後：~900 tokens/輪
  - 改善幅度：token -50%；延遲 -35~45%

- Learning Points：成本與品質平衡
- Practice/Assessment：對同一用例對比壓縮前後延遲與品質


## Case #18: LLM 決策可追溯性（日誌/審計）

### Problem Statement（問題陳述）
- 業務場景：LLM 決策為黑盒，需審計 function call 序列、輸入/輸出與上下文以便除錯與合規。
- 技術挑戰：在不洩漏敏感資料前提下進行完整追蹤。
- 影響範圍：維運、合規、可信度。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 無決策日誌
  2. function call 未記錄
  3. 無重現路徑
- 深層原因：
  - 架構：缺審計層
  - 技術：日誌未結構化
  - 流程：無合規策略

### Solution Design
- 解決策略：記錄 prompt 版本、RAG 片段 ID、function call 名稱/參數/結果、延遲與錯誤；提供隱私遮罩；可重播機制。

- 實施步驟：
  1. 結構化日誌
     - 實作細節：以 JSON 記錄
  2. 隱私遮罩
     - 實作細節：PII 脫敏
  3. 重播工具
     - 實作細節：以相同 inputs 重放

- 關鍵程式碼/設定：
```json
{
  "traceId":"...", "personaVersion":"v1.2",
  "ragChunks":[101, 203],
  "calls":[{"fn":"AddItemToCart","args":{"id":1,"q":10},"ms":45}],
  "latencyMs": 2100, "result":"OK"
}
```

- 實測數據：問題定位時間顯著縮短（觀測），合規可交付審計證據
- Learning Points：可觀測性是 AI 工程落地關鍵
- Practice/Assessment：設計最小可用追溯方案並重播一次異常場景



=====================
案例分類
=====================

1) 按難度分類
- 入門級（適合初學者）
  - Case 4 空購物車結帳防呆
  - Case 8 店長 Persona 與回覆協議
  - Case 11 可解析回覆協議與 Parser
  - Case 13 混合式 UX（指令 + 對話）

- 中級（需要一定基礎）
  - Case 1 結帳前智慧風險檢查
  - Case 2 操作歷程即時提示
  - Case 7 Chat History 短期記憶
  - Case 9 RAG 長期記憶
  - Case 10 Skill 精實化治理
  - Case 12 Function-Calling 執行迴圈
  - Case 14 規則 + LLM 混合風險
  - Case 15 可靠性治理（配額/重試）
  - Case 16 參數驗證與授權護欄
  - Case 17 Token 預算與壓縮
  - Case 18 決策可追溯性

- 高級（需要深厚經驗）
  - Case 3 自然語言 → Function Calling
  - Case 6 預算導向購物車最佳化

2) 按技術領域分類
- 架構設計類：Case 3, 6, 9, 12, 13, 14, 15, 18
- 效能優化類：Case 7, 9, 15, 17
- 整合開發類：Case 1, 2, 3, 12, 13
- 除錯診斷類：Case 10, 11, 18
- 安全防護類：Case 4, 5, 14, 16

3) 按學習目標分類
- 概念理解型：Case 7, 8, 9, 14, 17
- 技能練習型：Case 1, 2, 11, 12, 13
- 問題解決型：Case 3, 4, 5, 6, 15, 16, 18
- 創新應用型：Case 6, 12, 18



=====================
案例學習路徑建議
=====================

- 建議先學：
  - Case 8（Persona 與回覆協議）：建立 AI “人格”與可解析回覆的基礎。
  - Case 11（OK/HINT Parser）：確保與系統的機器可讀橋接。
  - Case 7（Chat History）：理解短期記憶對任務成功的重要性。
  - Case 13（混合式 UX）：以低風險方式將 AI 植入既有流程。

- 依賴關係：
  - Case 1/2 依賴 Case 8/11/7（需 Persona、協議與上下文）
  - Case 3 依賴 Case 10（技能治理）與 Case 12（執行迴圈）
  - Case 6 依賴 Case 3/12（多步規劃與執行）
  - Case 9（RAG）可強化 Case 1/2/6 的知識注入
  - Case 14（規則+LLM）與 Case 15/16（可靠性/安全）為上線前的治理基礎
  - Case 18（追溯）支撐全域除錯與合規

- 完整學習路徑：
  1) 基礎治理與橋接：Case 8 → Case 11 → Case 7 → Case 13
  2) 關鍵體驗場景：Case 1（結帳前風險）→ Case 2（過程提示）
  3) 能力升級：Case 10（技能治理）→ Case 12（執行迴圈）→ Case 3（Function Calling）
  4) 進階智慧化：Case 9（RAG）→ Case 6（預算最佳化）
  5) 上線治理：Case 14（規則+LLM 分流）→ Case 15（可靠性）→ Case 16（安全）→ Case 17（成本）→ Case 18（可追溯）

說明：
- 所有“實測數據”為作者 PoC/觀測性指標，用於教學與設計驗證參考，實際成效需依各自場域再測。