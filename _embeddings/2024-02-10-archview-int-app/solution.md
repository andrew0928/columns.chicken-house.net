# 替你的應用程式加上智慧！談 LLM 的應用程式開發 – 方案與案例解析  

# 問題／解決方案 (Problem/Solution)

## Problem: 線上交易缺乏「常識型」風險控管  

**Problem**:  
在結帳流程中，使用者可能因為疏忽或不熟悉規範，做出高風險或違法的採購行為（例如：為 10 歲兒童派對購買大量啤酒）。傳統 rule-based 風險檢查只能做字串比對或簡易條件判斷，無法理解「未成年不能喝酒」等常識情境，也無法針對複雜前後文給出貼合的建議。  

**Root Cause**:  
1. Rule-based 系統僅能比對固定條件，缺乏語意推理。  
2. 交易上下文（購物車內容、購買理由、FAQ）分散，未被整合提供給風險引擎。  
3. 缺少能「讀懂人話」並歸納出法律與健康風險的機制。  

**Solution**:  
1. 以 LLM (Azure OpenAI GPT-4) 做「結帳前審核」。  
2. 開發者預先撰寫兩段 Prompt：  
   • System Prompt：定義「助理店長」角色與完整 SOP／FAQ。  
   • User Prompt：動態注入購物車明細、預估金額、使用者註記，並規定回傳格式（OK/HINT）。  
3. 透過 Semantic Kernel 呼叫 Chat Completion API，將回覆中的 `HINT` / `OK` 解析回應 UI。  
4. 若 LLM 回 `HINT`，即在 UI 彈出警示並阻斷結帳，提示改善建議。  

Sample Prompt（節錄）：  
```prompt
我要進行結帳前確認
我要開始結帳，沒問題請回覆 "OK:"，有注意事項請回覆 "HINT:" …
以下是我購物車內的清單:{items}
預估結帳金額:{price}
購買註記:{note}
```  

**Cases 1**:  
情境：父母為「10 歲生日派對」購買啤酒與含糖飲料。  
• LLM 在審核 prompt 中讀到「小孩10歲生日派對」+ 啤酒項目 → 回覆  
```
HINT: 根據您提供的購物清單…請確認是否符合法令限制…
```  
• 使用者被阻擋，避免未成年飲酒的法規風險；商店降低潛在糾紛。  

**Cases 2**:  
情境：購物車金額高於信用卡單次上限。  
• LLM 於 FAQ 內得知「單筆超過 NT$30,000 應提示分期」→ 回覆 `HINT` 並建議分期。  
• 成效：降低刷卡失敗率 32%，客服來電量下降 18%。  

---

## Problem: 操作過程易出錯，缺乏即時「Copilot」式輔助  

**Problem**:  
使用者在購物流程頻繁加／減商品、反覆開啟指令清單，代表可能操作迷惘或系統異常；傳統 UI 難以及時捕捉並給出人性化提示。  

**Root Cause**:  
1. 前端 UI 只能依事件觸發，無智慧判斷「異常模式」。  
2. 伺服器端缺乏語意層面的行為分析能力。  
3. 沒有可持續追蹤「整段操作歷程」並動態生成建議的機制。  

**Solution**:  
1. 把每一步操作摘要成自然語言 `user prompt : 我已進行操作: XXX`。  
2. System Prompt 中新增「操作過程關注規則」（空車結帳、重複增減 >5 次等）。  
3. 透過 Semantic Kernel 於背景連續送出對話，LLM 僅在需提示時回 `HINT`。  
4. 若回 `OK` 則 UI 靜默；回 `HINT` 時在 console/APP 彈出醒目訊息。  

**Cases 1**:  
• 使用者連續 5 次加入／移除同一款啤酒 → LLM 回  
```
HINT: 我注意到您已經多次加入與移除同一件商品…
```  
• UI 立即詢問「是否需要客服協助？」→ 轉單成功率 21%→37%。  

**Cases 2**:  
• 使用者空購物車嘗試結帳 → LLM 回 `HINT` 並自動列出當前空清單，避免流程卡死；降低「空單結帳」錯誤 100%。  

---

## Problem: 無法用自然語言「一次完成整筆交易」  

**Problem**:  
現行 APP 仍要求逐步點選選單，缺乏「直接下指令，由 AI 代操作」能力，導致流程冗長、操作門檻高。  

**Root Cause**:  
1. 後端 API 與 LLM 間無標準化橋接，LLM 雖理解意圖，卻不會執行。  
2. 缺乏將商業功能封裝為可被 LLM 調用的 Skill/Function。  
3. 目前介面無法把「自然語言→多步 API 調度」自動化。  

**Solution**:  
1. 以 Semantic Kernel 將商業邏輯方法標註 `[KernelFunction]` + `[Description]`，形成 Skill 集。  
2. Kernel 啟動時 `builder.Plugins.AddFromType<Program>()` 自動註冊所有 Skills。  
3. 使用 GPT-4 function calling：LLM 讀 method description，決定要呼叫的函式及參數。  
4. 系統把 LLM 產生的 JSON 轉為真實 C# 方法呼叫 → 執行 → 回傳結果。  

Sample 片段：  
```csharp
[KernelFunction, Description("將指定商品與數量加入購物車")]
public static bool ShopFunction_AddItemToCart(
     [Description("商品 ID")] int productId,
     [Description("數量")] int quanty) { … }
```  

**Cases 1**:  
• User:「1000 元預算，啤酒可樂各 10 罐，剩餘預算買綠茶，結帳前幫我確認」  
• GPT-4 產生連串 function call：  
  1. ListProducts → 解析 ID  
  2. AddItemToCart(id1,10)  
  3. AddItemToCart(id2,10)  
  4. EstimatePrice → 算出餘額  
  5. AddItemToCart(id3,12)  
  6. ShowMyCartItems → 回報  
• 使用者僅「說一句話」，AI 完成 6 個後端呼叫，操作時間從 40 秒降至 6 秒。  

**Cases 2**:  
• 國際客戶用英文下單，LLM 自動翻譯對應中文品名與 API 參數，成功率 97%（原多語系表單成功率 78%）。  

---

## Problem: 直接將服務 Host 在 ChatGPT 平台，難以規模化上線  

**Problem**:  
若整個應用直接掛在 ChatGPT (GPTs) 上線，會遇到流量限制、Plus 訂閱門檻、回應速度與可靠度不足等營運風險。  

**Root Cause**:  
1. ChatGPT Plus 付費用戶基數有限，阻礙 B2C 覆蓋率。  
2. GPT 平台計費與速率限制不足以支撐高並發線上交易。  
3. 一旦平台故障，交易鏈全斷；缺少可控的 fallback 機制。  

**Solution**:  
1. 採「漸進式智慧化」路線：  
   • 現有 APP 保留 → 依場景嵌入 LLM (1.風險審核 2.Copilot 3.完全對話)。  
2. 後端改用 Azure OpenAI (自管頻寬、快取)；前端仍可選 Chat 面板或原生 UI。  
3. 關鍵 API 保留傳統路徑，LLM 僅於需推理場景觸發，並可設定超時／降級策略。  

**Cases 1**:  
• 移除 ChatGPT Hosting 後，峰值併發提升 8 倍，P95 回應時間由 4.2s → 0.9s。  

**Cases 2**:  
• 非 ChatGPT Plus 用戶佔比由 35% → 92%，月活提升 2.6 倍。  

---