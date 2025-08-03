---
source_file: "_posts/2024/2024-01-15-archview-llm.md"
generated_date: "2025-01-12 10:30:00 +0800"
version: "1.0"
tools:
  - claude_sonnet_3_5
model: "claude-3-5-sonnet-20241022"
---

# [架構師觀點] 開發人員該如何看待 AI 帶來的改變? - 生成內容

## 原始 Metadata

```yaml
layout: post
title: "[架構師觀點] 開發人員該如何看待 AI 帶來的改變?"
categories:
- "系列文章: 架構師觀點"
tags: ["架構師觀點","技術隨筆"]
published: true
comments_disqus: false
comments_facebook: false
comments_gitalk: true
redirect_from:
logo: /wp-content/images/2024-01-15-archview-llm/2024-01-20-12-29-24.jpg
```

## 擴增 Metadata

### 自動識別關鍵字
keywords:
  primary:
    - LLM (大型語言模型)
    - GPTs
    - Semantic Kernel
    - API First
    - AI 應用架構
    - Microsoft Copilot
  secondary:
    - ChatGPT
    - 軟體開發框架
    - Domain API
    - AI Ready
    - Prompt Engineering
    - 架構師觀點

### 技術堆疊分析
tech_stack:
  languages:
    - C#
    - JavaScript
    - Python
  frameworks:
    - ASP.NET Core
    - Semantic Kernel
    - LangChain
  tools:
    - Visual Studio
    - GitHub Copilot
    - ChatGPT
    - Azure App Service
  platforms:
    - Azure
    - Windows
    - OpenAI

### 參考資源
references:
  internal_links:
    - /2016/05/05/archview-net-open-source/
    - /2020/03/10/interview-abstraction/
  external_links:
    - https://openai.com/blog/introducing-gpts
    - https://platform.openai.com/docs/guides/function-calling
    - https://learn.microsoft.com/en-us/semantic-kernel/overview/
    - https://github.com/microsoft/semantic-kernel/
    - https://github.com/andrew0928/AndrewDemo.NetConf2023
  mentioned_tools:
    - OpenAI GPTs
    - Azure OpenAI Service
    - Microsoft Copilot
    - Semantic Kernel

### 內容特性
content_metrics:
  word_count: 15000
  reading_time: "30 分鐘"
  difficulty_level: "進階"
  content_type: "技術洞察與實作"

## 摘要 (Summaries)

### 文章摘要 (Article Summary)
作者在這篇文章中深入探討了 AI 技術，特別是大型語言模型（LLM）對軟體開發帶來的根本性改變。透過實作「安德魯小舖 GPTs」這個概念驗證專案，作者展示了如何利用 OpenAI 的 GPTs 功能，結合自行開發的購物 API，打造出一個能夠理解自然語言、處理複雜購物需求的智慧店員系統。這個實驗成功地驗證了 LLM 能夠扮演使用者意圖與精確 API 呼叫之間的橋樑角色，突破了傳統 UI/UX 設計的限制。作者認為，這種變革將從根本上改變軟體開發的架構，未來的應用程式將以 LLM 為中控中心，透過自然語言理解來協調各種服務和功能。文章進一步分析了 Microsoft 在 AI 領域的技術布局，包括 Azure OpenAI Service、Copilot 和 Semantic Kernel 三大支柱，並預測這些技術將如何整合成為下一代的軟體開發生態系。最後，作者為架構師和開發人員提供了具體的建議，包括如何設計 AI Friendly 的 API、如何運用新的開發框架，以及如何在這波 AI 浪潮中保持競爭力。

### 關鍵要點 (Key Points)
- LLM 突破了使用者意圖與系統操作之間的隔閡，能夠理解自然語言並轉換為精確的 API 呼叫
- API 設計必須更加精準、合理且符合領域邏輯，才能被 AI 有效使用
- Semantic Kernel 代表了 AI 時代的新型應用程式開發框架
- Microsoft 的 AI 布局包含雲端服務、使用者介面和開發框架三個層面
- 架構師需要引領團隊將系統改造為 AI Ready 的應用程式
- 開發人員需要掌握 Prompt Engineering、向量資料庫等新技能

### 段落摘要 (Section Summaries)

1. **安德魯小舖 GPTs - Demo**：作者透過實作一個線上購物的 GPTs 應用，展示了 LLM 如何理解使用者的自然語言需求，並正確地呼叫後端 API 完成購物流程。這個 demo 包含了商品瀏覽、預算評估、購物車管理、結帳等完整功能。最令人驚艷的是，GPTs 能夠理解隱含的需求（如「有小孩不能喝酒」），自動調整購物內容，甚至能在 API 未提供的功能上進行「腦補」，例如根據預算和折扣條件推薦最佳購買組合。整個過程中，GPTs 展現了出色的語意理解能力和邏輯推理能力，成功扮演了智慧店員的角色。

2. **軟體開發的改變**：作者深入分析了 LLM 技術成熟後對軟體開發帶來的根本性改變。傳統上，電腦只能處理明確的指令，而 LLM 的出現打破了這個限制，能夠理解使用者的「意圖」而非僅是「操作」。這將導致軟體架構的重大轉變：LLM 將成為應用程式的中控中心，負責解析使用者意圖並協調各種服務。API 的角色也將改變，不再只是給開發者使用的介面，而是需要設計得讓 AI 能夠理解和正確使用。作者預測，未來的軟體開發將圍繞著 AI 展開，各種開發框架和工具都會配合這個趨勢進行調整。

3. **看懂 Microsoft 的 AI 技術布局**：作者分析了 Microsoft 在 AI 領域的三大技術支柱：Azure OpenAI Service（雲端 AI 服務）、Copilot（使用者介面層）和 Semantic Kernel（開發框架）。這三者相互配合，形成完整的 AI 應用生態系。作者預測，LLM 將成為作業系統的一部分，Copilot 將成為主要的操作介面，而 Semantic Kernel 則提供了開發 AI 應用程式的標準框架。文章也提到了目前還缺少的部分，如作業系統層級的 AI 支援和雲端 PaaS 服務，但相信這些空缺很快會被填補。

4. **架構師、資深人員該怎麼看待 AI**：作者為架構師提供了四個重要觀點。首先，必須分清楚哪些任務適合用 LLM 處理（意圖理解），哪些需要精確計算。其次，API 設計必須更加精準合理，符合領域邏輯，才能讓 AI 正確使用。第三，UI 設計應該以任務為單位進行拆解，配合 Copilot 的運作模式。最後，需要選擇正確的開發框架（如 Semantic Kernel），並將系統的各個元件正確地放置在框架中。作者強調，架構師必須引領團隊逐步將系統改造為 AI Ready 的應用程式。

5. **開發人員該怎麼看待 AI**：作者建議開發人員從三個方面提升自己。首先，要熟悉各種 AI 工具來提高工作效率，如 GitHub Copilot、ChatGPT 等。其次，需要掌握 AI 時代的必要技術棧，包括 Prompt Engineering、向量資料庫、Semantic Kernel 等。第三，要深化領域設計和開發能力，特別是 API 設計和 DDD（領域驅動設計）。作者特別強調，隨著 UI 和流程邏輯越來越多地被 LLM 接管，核心的領域 API 開發將變得更加重要，需要更高的設計水準和實作品質。

## 問答集 (Q&A Pairs)

### Q1, 什麼是 GPTs？它與一般的 ChatGPT 有什麼不同？
Q: GPTs 是什麼技術？它和普通的 ChatGPT 使用上有什麼差異？
A: GPTs 是 OpenAI 在 2023 年 11 月發布的新服務，它允許使用者在 ChatGPT 的基礎上進行客製化。你可以預先設定角色（用自然語言描述）、上傳知識庫檔案，並掛載自己的 API（Custom Action）。GPTs 會根據這些設定來回應使用者，並在適當時機自動呼叫你的 API。相較於一般 ChatGPT，GPTs 更像是一個領域專家，能夠結合特定知識和外部系統來完成任務。

### Q2, 為什麼說 API 設計在 AI 時代變得更重要？
Q: 文章提到 API 設計必須「AI Friendly」，這是什麼意思？為什麼 API 設計變得如此關鍵？
A: 在 AI 時代，呼叫你 API 的不再只是其他開發者，而是 AI（如 LLM）。AI 理解 API 的方式是透過文件和描述，因此 API 設計必須合理、一致且符合現實世界的邏輯。不合理或特殊的設計會讓 AI 難以理解和正確使用。「AI Friendly」的 API 需要有清晰的命名、合理的流程、嚴謹的狀態管理，並且要能處理各種可能的呼叫順序，因為你無法預測或約束 AI 會如何使用你的 API。

### Q3, Semantic Kernel 是什麼？它在 AI 應用開發中扮演什麼角色？
Q: 文章多次提到 Semantic Kernel，這個框架的作用是什麼？
A: Semantic Kernel 是 Microsoft 推出的 AI 應用程式開發框架，它提供了整合 LLM 到應用程式的標準架構。框架包含 Kernel（核心）、Skill（技能/插件）、Planner（規劃器）、Memory（記憶）、Connector（連接器）等元件。它讓開發者能夠有系統地組織 AI 功能，協調 LLM 與其他服務的互動。就像 MVC 框架定義了 Web 應用的標準結構，Semantic Kernel 定義了 AI 應用的標準結構。

### Q4, LLM 如何理解使用者意圖並呼叫正確的 API？
Q: LLM 是如何將自然語言轉換為 API 呼叫的？這個過程是如何運作的？
A: LLM 透過「Function Calling」機制來實現這個轉換。首先，你需要提供 API 的規格說明（如 OpenAPI/Swagger），包含每個 API 的用途描述。當使用者輸入自然語言時，LLM 會分析語意，理解使用者的意圖，然後根據 API 描述判斷應該呼叫哪個 API。LLM 還會從對話內容中萃取出必要的參數，組成正確的 API 請求。這個過程就像 LLM 在扮演一個懂得所有 API 功能的專家，能夠將使用者需求翻譯成具體的系統操作。

### Q5, 作為開發人員，現在應該學習哪些 AI 相關技能？
Q: 面對 AI 浪潮，開發人員應該優先學習哪些技術和工具？
A: 開發人員應該從三個層面提升：1) 工具層面：熟悉 GitHub Copilot、ChatGPT 等提升效率的工具；2) 技術棧層面：學習 Prompt Engineering、向量資料庫（如 Pinecone）、NoSQL、Semantic Kernel 或 LangChain 框架；3) 設計能力層面：深化 API 設計、領域驅動設計（DDD）、微服務架構等核心能力。特別重要的是理解如何設計 AI Friendly 的 API，因為這將是未來系統整合的關鍵。

### Q6, Microsoft 的 AI 布局對軟體開發有什麼影響？
Q: 文章分析了 Microsoft 的 AI 技術布局，這對一般開發者有什麼意義？
A: Microsoft 的布局顯示了 AI 技術的發展方向：雲端服務（Azure OpenAI）、使用者介面（Copilot）、開發框架（Semantic Kernel）三位一體。這預示著：1) Windows 可能會內建 LLM 能力，成為 AI OS；2) Copilot 將成為主要的操作介面；3) 應用程式開發將轉向 AI 優先的架構。開發者應該關注這些趨勢，提前學習相關技術，準備迎接開發模式的轉變。

### Q7, 為什麼說 UI 的重要性會降低？
Q: 文章提到 UI 和流程設計的比重會降低，這是什麼意思？UI 會消失嗎？
A: UI 不會消失，但其角色會改變。傳統上，改善使用者體驗主要靠優化 UI 設計和操作流程。但有了 LLM 後，使用者可以直接用自然語言表達意圖，由 AI 來處理複雜的操作流程。例如，購物網站不需要複雜的篩選和比較介面，使用者只需告訴 AI「幫我在預算內買最划算的組合」。因此，UI 會更專注於特定的精確操作（如填表單），而複雜的流程控制會交給 LLM 處理。

### Q8, 什麼是「安德魯小舖 GPTs」？它展示了什麼概念？
Q: 作者的 PoC 專案「安德魯小舖 GPTs」具體做了什麼？有什麼特別之處？
A: 這是一個購物助理的 GPTs 應用，使用者可以用自然語言完成整個購物流程。特別之處在於：1) GPTs 能理解複雜需求，如預算限制、購買偏好；2) 能處理隱含需求，如「有小孩不能買酒」；3) 能在 API 未提供的功能上進行推理，如計算最佳購買組合；4) 展示了 LLM 如何作為中控中心，協調 API 呼叫完成任務。這個 PoC 驗證了未來應用程式可能的樣貌：以對話為主要介面，由 AI 協調後端服務。

## 解決方案 (Solutions)

### P1, API 設計不符合 AI 使用需求
Problem: 現有的 API 設計過於技術導向，充滿特殊規則和例外情況，導致 AI 難以理解和正確使用
Root Cause: 傳統 API 設計時假設使用者是其他開發者，可以透過文件和溝通了解特殊規則，但 AI 只能依靠 API 描述和一致的邏輯
Solution: 重新設計 API，遵循以下原則：1) 使用清晰且符合領域的命名；2) 保持操作邏輯的一致性；3) 實作嚴謹的狀態機，避免非法操作；4) 在 API 描述中使用自然語言清楚說明用途和限制
Example: 
```yaml
# 改善前
POST /api/proc/exec?action=buy&pid=123

# 改善後  
POST /api/orders/create
{
  "items": [
    {
      "productId": 123,
      "quantity": 2
    }
  ]
}
```

### P2, LLM 無法處理複雜的認證授權流程
Problem: GPTs 在處理需要多步驟的認證流程時經常失敗，無法正確維護認證狀態
Root Cause: 認證授權屬於需要精確執行的任務，不適合交由 LLM 透過理解和推理來處理
Solution: 1) 實作標準的 OAuth2 流程，讓 GPTs 平台處理認證；2) 將認證邏輯從業務邏輯中分離；3) 使用 GPTs 內建的認證機制而非自行實作；4) 簡化 API 的認證需求，避免複雜的 token 管理
Example:
```javascript
// 在 GPTs 設定中使用標準 OAuth
{
  "auth": {
    "type": "oauth",
    "authorization_url": "https://api.example.com/oauth/authorize",
    "token_url": "https://api.example.com/oauth/token"
  }
}
```

### P3, 如何讓現有系統變成 AI Ready
Problem: 現有的系統架構是為傳統 UI 操作設計的，無法有效支援 AI 整合
Root Cause: 系統缺乏明確的 API 層、業務邏輯與 UI 緊密耦合、沒有考慮自然語言介面的需求
Solution: 採取漸進式改造：1) 先抽離核心業務邏輯為獨立的 API 層；2) 確保每個 API 都有清晰的職責和描述；3) 實作 API Gateway 統一管理；4) 逐步加入 Semantic Kernel 等 AI 框架；5) 建立 Prompt 模板庫管理自然語言介面
Example:
```csharp
// 使用 Semantic Kernel 整合現有 API
var kernel = Kernel.Builder
    .WithAzureOpenAIChatCompletion(deployment, endpoint, apiKey)
    .Build();

// 註冊現有 API 為 Skills
kernel.ImportFunctions(new OrderService(), "OrderSkills");
kernel.ImportFunctions(new ProductService(), "ProductSkills");
```

### P4, 團隊缺乏 AI 開發經驗
Problem: 開發團隊習慣傳統開發模式，不知道如何開始導入 AI 技術
Root Cause: AI 開發需要不同的思維模式和技術棧，團隊缺乏相關知識和實戰經驗
Solution: 1) 從小型 PoC 開始，如內部工具的 AI 助手；2) 安排團隊學習 Prompt Engineering 和 AI 開發框架；3) 先使用成熟的 AI 服務（如 Azure OpenAI）而非自行訓練模型；4) 建立 AI 開發的最佳實踐和設計模式；5) 逐步將 AI 能力整合到現有產品中
Example:
```python
# 簡單的 Prompt Engineering 範例
def create_product_search_prompt(user_query):
    return f"""
    你是一個購物助理。根據以下客戶需求，搜尋並推薦合適的產品：
    
    客戶需求：{user_query}
    
    請考慮：
    1. 預算限制
    2. 使用場景
    3. 品質要求
    
    回應格式：
    - 推薦產品清單（最多5個）
    - 每個產品的推薦理由
    """
```

### P5, 如何評估 AI 功能的投資報酬率
Problem: 導入 AI 技術需要投資，但難以評估實際效益和回報
Root Cause: AI 的價值often體現在使用者體驗提升和長期競爭力，短期內難以量化
Solution: 建立多維度的評估標準：1) 測量使用者完成任務的時間縮短；2) 統計自然語言介面的使用率；3) 追蹤客戶滿意度提升；4) 計算人力成本節省（如客服工作量降低）；5) 評估新功能開發速度的提升。先從內部工具開始，累積數據後再推廣到產品
Example:
```yaml
# AI 功能效益評估指標
metrics:
  efficiency:
    - task_completion_time: -60%  # 任務完成時間減少
    - user_clicks_required: -75%   # 所需點擊次數減少
  
  adoption:
    - ai_interface_usage: 45%      # AI 介面使用率
    - user_retention: +20%         # 用戶留存提升
  
  cost_saving:
    - support_ticket_reduction: 30%  # 客服工單減少
    - development_time: -40%         # 開發時間縮短
```

## Version Changes
- v1.0 (2025-01-12): 初始版本