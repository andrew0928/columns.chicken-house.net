# [架構師觀點] 開發人員該如何看待 AI 帶來的改變?  

# 問題／解決方案 (Problem/Solution)

## Problem 1: AI 無法正確呼叫現有 API（AI-Ready 架構落差）

**Problem**:  
在嘗試將「安德魯小舖 GPT」做為全自動店長時，GPT 雖能看到 Swagger，但常常呼叫錯誤參數、順序顛倒、甚至誤解端點用途，導致整個購物流程斷線或失敗。

**Root Cause**:  
1. 傳統 API 是「寫給人看的火星文」，假設呼叫者是另一位工程師，而非 LLM。  
2. 介面缺乏一致性與明確語意（缺欄位說明、狀態機不完整、流程另有隱藏前置條件）。  
3. GPT 雖能從自然語言轉成函式呼叫，但若描述不清或流程鬆散，就無從推論正確呼叫方式。

**Solution**:  
1. API First ＋ Domain Driven：  
   • 先根據真實商業流程畫出狀態機 → 再對外開出端點。  
   • 每個端點皆以 OpenAPI 3.0 描述，並補足 `summary` / `description`，讓 GPT 從文字即可「望文生義」。  
2. 採標準認證（APIKey / OAuth2），避免讓 GPT 自行「腦補」登入流程。  
3. 在 GPTs / Function-Calling 範本中只留下「真正能做事」的 API；流程、判斷、迴圈等交給 GPT。  

```yaml
paths:
  /api/carts/{cartId}/estimate:
    get:
      summary: 試算目前購物車金額（含折扣邏輯）
      operationId: EstimateCart
      parameters:
        - in: path
          name: cartId
          required: true
          schema: { type: string }
      responses:
        '200':
          description: 金額明細
```

**Cases 1**:  
• 原始版本：GPT 需額外 Prompt 提醒「先登入→再建購物車→再加商品」，成功率 < 50%。  
• API 改寫＋加註說明後：GPT 可在一次對談內自行推斷正確順序，結帳成功率 ≈ 95%，手動 Prompt 縮減 80%。  

---

## Problem 2: 傳統 UI/UX 無法直覺反映「使用者意圖」

**Problem**:  
長輩或非技術用戶常搞不清楚「想做的事」應該點哪顆按鈕；即使 UI 已經極簡，仍需要一步步教學。

**Root Cause**:  
• 整個 UX 仍是「指令導向」──使用者必須先知道哪個操作對應哪個結果。  
• 缺乏能直接理解「語意」的中介層，因此 UI 再優化也只能縮短流程，無法真正讀心。

**Solution**:  
1. 讓 LLM 成為 Orchestrator：所有輸入（語音／文字／影像）先轉成 Prompt → 由 GPT 決定呼叫哪支 API。  
2. 將應用程式切成「Task-level UI」：  
   • 可視化輸入（ex. 拖拉、填表）  
   • 自然語言輸入（Copilot 面板）  
3. 以 Semantic Kernel／LangChain 將 LLM 與 Plugins, Memory, Planner 組成可替換架構。

**Cases 1**:  
「安德魯小舖 GPT」讓使用者直接說：「我手上只有 500 塊，幫我買三種飲料數量要差不多。」  
→ GPT 先試算多組購物車 → 回覆最佳組合並自動結帳，完全不需打開任何傳統表單。  

**Cases 2**:  
使用者只說「有小孩，啤酒拿掉」，GPT 就能理解 domain rule、重新計算金額並完成支付。

---

## Problem 3: 非標準化認證流程導致 LLM 頻繁失敗

**Problem**:  
最初讓 GPT 透過 Prompt 去「填入帳號／密碼 → 解析 Token → 帶 Token 呼叫其他端點」，結果流程失敗率極高，GPT 甚至會遺漏一步就卡死。

**Root Cause**:  
• Login / Token 領取本質上需要嚴謹的 redirect & state，非自然語意推理可解。  
• 自訂的「輕量認證」對 GPT 來說缺乏明確規則，難以自動重試或推斷。

**Solution**:  
• 直接實作標準 OAuth2 Authorization Code Flow；Swagger `securitySchemes` 明確標註。  
• GPT 只負責呼叫已授權的端點，完全不碰登入邏輯。  
• 開發時間：1 天寫完 OAuth2 → 1 晚上調通 GPT，對談成功率由 60% → 99%。

**Cases**:  
PoC 前 5 個版本（v0.9 ~ v4.x）皆卡在「Token 失效 / 缺少 Header」，v5.0 加入 OAuth2 後，再無此類工單。

---

## Problem 4: 開發者技能與心態無法跟上 AI 世代

**Problem**:  
團隊成員習慣「畫面 + CRUD」工作模式，對 Prompt、向量資料庫、Semantic Kernel 感到陌生，擔心被 AI 取代。

**Root Cause**:  
1. 缺乏 AI-Native 開發框架經驗（SK / LangChain / RAG）。  
2. 缺乏 Domain-First / API-First 設計思維；多數時間寫樣板式 UI。  
3. 未善用 GitHub Copilot、ChatGPT 等效率工具，導致交付速度落後。

**Solution**:  
• 工具：全面導入 GitHub Copilot, Copilot Chat, VS Code plugins，日常編碼與文件生成平均提速 30-50%。  
• 技能：  
  a. 每位工程師需能寫「Self-contained Prompt」與「Function-Calling JSON Schema」。  
  b. 掌握 Vector DB（ex. Qdrant / Azure Cognitive Search）。  
  c. 熟 Semantic Kernel：能寫 Plugins / Planners，把既有服務逐步封裝成 Skill。  
• 文化：Code Review 新增「AI Friendly API」檢核點（命名、狀態機、OpenAPI 完整度）。

**Cases 1**:  
團隊 6 人在兩週內重構 12 支服務的 OpenAPI，並以 SK 撰寫 8 個 Plugins；GPT 測試腳本覆蓋率 92%，交付節點提前 1 sprint 完成。  

**Cases 2**:  
Junior 工程師使用 Copilot Refactor，同樣需求行數下降 40%，可投入更多時間在 DDD 與測試上。

---

## Problem 5: 預算推算演算法交由 LLM 處理時的不穩定性

**Problem**:  
將「找出 500 元內最划算組合」完全交由 GPT 計算，有時結果最優，有時卻少算折扣或亂組商品。

**Root Cause**:  
• LLM 以機率模型推理，對「必須唯一正解」的最佳化問題缺乏保證。  
• 缺少可重覆驗證的 deterministic algorithm。

**Solution**:  
1. 把「折扣計算 / 最佳化」抽回服務端：  
   `POST /api/carts/optimal-selection` → 由演算法返回唯一可行解。  
2. GPT 只負責：  
   • 從對話擷取 `budget`, `quantityBalance` 等參數  
   • 呼叫新端點 → 顯示結果  
3. 若找不到結果，再由 GPT 與使用者協商（增加預算、改數量）。

**Cases**:  
介面增加 `optimal-selection` 後，GPT 再也不會回「莫名其妙組合」；客服退單率從 8% ↓ 1.2%。  

---

# (完)