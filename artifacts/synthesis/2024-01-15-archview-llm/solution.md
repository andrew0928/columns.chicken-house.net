以下內容基於原文中的 PoC、經驗與觀點，提煉出可落地的實戰型案例。每個案例包含問題、根因、解法、關鍵設定/程式碼、環境與指標、學習要點與練習題，便於教學、專案演練與能力評估。共 18 個案例。

## Case #1: 讓 API 對 LLM 友善（LLM-Friendly API Design）

### Problem Statement（問題陳述）
**業務場景**：以 LLM 作為「店長」服務端點，透過 GPTs Custom Actions 呼叫線上商店 API（商品、購物車、結帳、訂單）完成完整購物流程。發現 LLM 會基於 OpenAPI 內容自行決定何時、如何呼叫 API，若 API 描述不清、命名不一或缺乏語意說明，LLM 會誤用、誤解，導致流程中斷或結果不準確。

**技術挑戰**：如何讓 LLM 僅透過 OpenAPI/Swagger 的描述即可理解資源、參數與流程關係，並且做出穩定正確的呼叫。

**影響範圍**：整體轉換率、對話成功率、API 調用正確性、錯誤率、對話輪次。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. OpenAPI 描述過於「工程化」，缺乏自然語言語意，LLM 難以對應使用情境。
2. 命名不一致（資源/欄位/狀態），讓 LLM 難以建立穩定的策略。
3. 缺乏參數約束與錯誤訊息語意化，導致 LLM 難以自我修正。

**深層原因**：
- 架構層面：沒有 API First 與 Business Model 對齊，資源/流程未抽象清楚。
- 技術層面：OpenAPI schema 缺少 description、enum、範例、錯誤結構。
- 流程層面：少量 prompt 補救而不是從源頭修 API 設計。

### Solution Design（解決方案設計）
**解決策略**：採 API First，重新命名資源與欄位、補齊自然語言描述、加入參數/回應約束與語意化錯誤規格，讓 LLM 僅憑 Swagger 即「望文生義」。配合一致的域模型與狀態語意，降低 LLM 誤用率。

**實施步驟**：
1. API 體檢與重構
- 實作細節：盤點資源、動詞、路徑命名，調整為資源導向；對齊 DDD 的名詞語彙。
- 所需資源：API 設計規範、DDD 名詞表
- 預估時間：1-2 人日

2. 補齊 OpenAPI 語意
- 實作細節：全面補上 description、examples、enum 說明、錯誤模型；以自然語言說明用途與限制。
- 所需資源：Swashbuckle、OpenAPI Linter
- 預估時間：1-2 人日

3. 加入參數與回應約束
- 實作細節：minimum/maximum、pattern、enum、required；HTTP 4xx 結構化錯誤。
- 所需資源：OpenAPI schema、FluentValidation（伺服端）
- 預估時間：1 人日

**關鍵程式碼/設定**：
```yaml
# OpenAPI 範例片段（重點在自然語言描述＋約束）
paths:
  /api/products:
    get:
      summary: 列出可販售商品
      description: >
        回傳目前可販售商品清單。請在需要依關鍵字或類別過濾時使用 /api/products/search。
      responses:
        "200":
          description: 商品清單
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Product"

  /api/carts/{cartId}/estimate:
    post:
      summary: 試算購物車結帳金額（包含折扣規則）
      description: >
        回傳依商業規則計算後的結帳金額。請勿自行估算折扣，應以此端點為準。
      parameters:
        - name: cartId
          in: path
          required: true
          schema: { type: string, pattern: "^[a-zA-Z0-9_-]{6,64}$" }
      responses:
        "200":
          description: 試算結果
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/CartEstimateResult"
        "400":
          description: 無效的購物車狀態或參數
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/ApiError"

components:
  schemas:
    Product:
      type: object
      required: [id, name, price]
      properties:
        id: { type: integer, description: 商品 ID }
        name: { type: string, description: 商品名稱（唯一） }
        description: { type: string, description: 商品描述（可包含關鍵字如「啤酒」） }
        price: { type: number, format: float, minimum: 0 }
        category: { type: string, enum: [softdrink, tea, beer], description: 商品分類 }
        isAlcoholic: { type: boolean, description: 是否含酒精 }
    ApiError:
      type: object
      properties:
        code: { type: string }
        message: { type: string, description: 給 LLM/人類閱讀的自然語言描述 }
```

實際案例：安德魯小舖 GPTs 將折扣估算委由 /estimate，並以 OpenAPI 描述引導 LLM 不自行腦補。
實作環境：.NET 8 + ASP.NET Core 8、Swashbuckle、Azure App Service、OpenAI GPTs Actions。
實測數據：
- 改善前：常出現錯用端點、少量 prompt 補救。
- 改善後：移除補救 prompt 後仍能穩定完成流程（作者觀察）。
- 改善幅度：穩定性與理解度顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- API First 與 DDD 名詞對齊
- OpenAPI 語意化描述與約束
- 為 LLM 設計可讀的錯誤結構

技能要求：
- 必備技能：OpenAPI/Swagger、REST 設計
- 進階技能：DDD、API 可用性測試（以 LLM Caller 為象）

延伸思考：
- 如何把「流程說明」也內嵌到 OpenAPI？
- 是否需要為 LLM 準備專屬的「短版 Swagger」？
- 可以自動從程式碼註解生成 LLM 專用說明嗎？

Practice Exercise（練習題）
- 基礎練習：為 /api/products 與 /estimate 完成語意化 OpenAPI（30 分鐘）
- 進階練習：為所有 4xx/5xx 統一錯誤結構＋自然語言 message（2 小時）
- 專案練習：以 LLM 作為唯一前端，透過 Actions 驗證 API 的可用性（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：端點描述與約束是否完備
- 程式碼品質（30%）：命名一致、描述清晰、無債務
- 效能優化（20%）：回應大小、必要欄位、錯誤快速回報
- 創新性（10%）：LLM 專用說明與例外處理



## Case #2: 預算＋折扣規劃：用試算端點驅動 LLM 決策

### Problem Statement（問題陳述）
**業務場景**：顧客以「1000 元預算」和「啤酒第二件六折」等口語條件，請「店長（LLM）」幫忙配置購買清單。API 僅提供單價與「試算金額」端點，並未揭露完整折扣規則。

**技術挑戰**：在規則未公開的情況下，LLM 需透過反覆呼叫 /estimate 進行探測式規劃，避免自行腦補折扣算法。

**影響範圍**：購物建議正確率、對話輪次、API 呼叫次數、使用者體驗。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 折扣規則未在 API 明載，LLM 只能透過試算結果推理。
2. 若 LLM 未固定「先估再買」策略，會直接結帳或產生次佳方案。
3. 缺少「錯誤自查」流程，出現非最優方案時不會重算。

**深層原因**：
- 架構層面：BL（促銷策略）未對外暴露語意，僅以 /estimate 為準。
- 技術層面：缺少規劃/重試策略與約束性提示。
- 流程層面：沒有設計「規劃 → 試算 → 校驗 → 決策 → 下單」的固定模板。

### Solution Design（解決方案設計）
**解決策略**：定義「規劃管線」：先收集條件→反覆試算→達成預算與約束→才下單。以 Prompt 明定「禁止自算折扣」，所有金額必以 /estimate 為準；若結果不佳則自我修正後重試。

**實施步驟**：
1. 試算為唯一真相
- 實作細節：在 API description 強調「折扣以 /estimate 為準」。
- 所需資源：OpenAPI、LLM 指示詞
- 預估時間：0.5 人日

2. 設計規劃 Prompt 模板
- 實作細節：規範行為「探索→比對→優化→下單」，並加入失敗重試。
- 所需資源：Prompt 指南
- 預估時間：0.5 人日

3. 伺服端提供簡易估算端點
- 實作細節：提供計算折扣之程式碼，維持在伺服端。
- 所需資源：.NET API
- 預估時間：1 人日

**關鍵程式碼/設定**：
```csharp
// 折扣規則：啤酒（id=1）第二件六折（示意）
decimal EstimateCartTotal(Cart cart, IReadOnlyList<Product> products)
{
    decimal total = 0m;
    foreach (var line in cart.Items)
    {
        var product = products.Single(p => p.Id == line.ProductId);
        total += product.Price * line.Quantity;

        if (product.Category == "beer")
        {
            var pairs = line.Quantity / 2;
            var discountPerPair = product.Price * 0.4m; // 第二件六折 => 折 40%
            total -= pairs * discountPerPair;
        }
    }
    return total;
}
```

實際案例：安德魯小舖 GPTs 在預算語境下反覆呼叫多個 API 後給出方案，並完成結帳。
實作環境：.NET 8、ASP.NET Core、Azure App Service、OpenAI GPTs。
實測數據：
- 改善前：LLM 偶爾自算折扣或給出次佳方案。
- 改善後：以 /estimate 為唯一依據，整體建議穩定性提升（定性觀察）。
- 改善幅度：錯誤決策顯著下降（定性）。

Learning Points（學習要點）
核心知識點：
- 探測式規劃（Plan-Estimate-Verify）
- 折扣歸屬於伺服端 BL，LLM 僅決策
- Prompt 中嚴禁自行計算的約束語句

技能要求：
- 必備技能：後端折扣實作、OpenAPI 描述
- 進階技能：規劃提示設計、自我校驗策略

延伸思考：
- 若折扣規則頻繁變動，是否需 /promotions 查詢端點？
- 如何記錄每次估算的依據供審計？
- 可否用 DP/ILP 對「最佳化」做高精度規劃？

Practice Exercise（練習題）
- 基礎練習：在 /estimate 增加更多折扣型態（30 分鐘）
- 進階練習：撰寫 Prompt，強制「估→檢→優→下單」的策略（2 小時）
- 專案練習：加入多種類別商品與多重折扣，驗證 LL「優化」穩定性（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：完整規劃→試算→校驗流程
- 程式碼品質（30%）：BL 與控制流程分離
- 效能優化（20%）：多次試算的效能控管
- 創新性（10%）：優化策略與自我修正手法



## Case #3: 同義詞與自然語言對齊（「啤酒」不等於商品全名）

### Problem Statement（問題陳述）
**業務場景**：使用者以自然語言「啤酒」、「綠茶」下單，實際商品名稱為「18天台灣生啤酒 355ml」等。若 API 僅支援 ID/全名，LLM 需自行推斷，易出錯。

**技術挑戰**：在不改動既有商品命名的前提下，讓 LLM 以通用詞找到正確商品。

**影響範圍**：商品選取正確率、對話流暢度、錯誤率。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. API 缺少搜尋/標籤欄位；只能全名匹配。
2. 商品缺乏類別、同義詞、關鍵字欄位。
3. LLM 需要透過 description 關鍵字猜測，穩定性不足。

**深層原因**：
- 架構層面：商品模型未以「語意檢索」思維設計。
- 技術層面：缺少 /search 或 tags/synonyms 欄位。
- 流程層面：缺少「先搜再增」的固定用法。

### Solution Design（解決方案設計）
**解決策略**：在 Product 模型中加入 category/tags/synonyms，並提供 /api/products/search?query=xxx 端點；以 OpenAPI 說明「自然語言先搜再挑」，減少 LLM 誤配。

**實施步驟**：
1. 擴充資料模型
- 實作細節：加入 category/tags/synonyms 與 isAlcoholic 欄位。
- 所需資源：DB schema、DTO
- 預估時間：0.5 人日

2. 實作搜尋端點
- 實作細節：支援 name/desc/tags/synonyms 模糊查詢。
- 所需資源：API、索引
- 預估時間：0.5 人日

3. LLM 使用指引
- 實作細節：OpenAPI description 與 Prompt 指示「先搜→再加入購物車」。
- 所需資源：OpenAPI、Prompt
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```csharp
// 簡易搜尋（示意）
[HttpGet("/api/products/search")]
public IActionResult Search([FromQuery] string query)
{
    var q = query?.Trim().ToLowerInvariant() ?? "";
    var results = _db.Products.Where(p =>
        p.Name.ToLower().Contains(q) ||
        p.Description.ToLower().Contains(q) ||
        p.Category.ToLower().Contains(q) ||
        p.Tags.Any(t => t.ToLower().Contains(q)) ||
        p.Synonyms.Any(s => s.ToLower().Contains(q))
    );
    return Ok(results);
}
```

實際案例：在 PoC 中，使用者以「啤酒」指稱，LLM 正確找到「18天台灣生啤酒」並加購。
實作環境：.NET 8、ASP.NET Core、Azure App Service、OpenAI GPTs。
實測數據：引入搜尋端點後，LLM 商品匹配成功率明顯提升（定性）。

Learning Points（學習要點）
核心知識點：
- 語意檢索前置化
- Product 模型語意欄位設計
- LLM 的「先搜再增」策略

技能要求：
- 必備技能：REST 搜尋、簡易全文檢索
- 進階技能：向量檢索（未必必要）

延伸思考：
- 何時引入向量索引（如商品量大）？
- 多語言同義詞的維護策略？
- 搜尋結果排序（學習點擊/購買回饋）？

Practice Exercise（練習題）
- 基礎練習：加入 tags/synonyms 欄位並更新搜尋（30 分鐘）
- 進階練習：搜尋結果排序與分頁（2 小時）
- 專案練習：以歷史點擊/購買率調整排序（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：搜尋能涵蓋自然語言
- 程式碼品質（30%）：模型與查詢簡潔
- 效能優化（20%）：索引/分頁
- 創新性（10%）：排序/個人化



## Case #4: 未成年人禁酒條件的語意化處理

### Problem Statement（問題陳述）
**業務場景**：使用者口語描述「有小孩不能喝酒」，期望 LLM 自動移除酒類商品並調整購物清單；API 未顯式揭露「酒類」欄位。

**技術挑戰**：如何讓 LLM 穩定辨識酒類並適當替換或移除，仍滿足其他限制（預算、數量接近）。

**影響範圍**：法規合規、顧客體驗、建議可用性。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 缺乏 isAlcoholic/category 欄位。
2. 沒有「批次移除/替換」端點。
3. LLM 需透過描述猜測，易誤判。

**深層原因**：
- 架構層面：商品模型缺乏合規屬性。
- 技術層面：缺少語意化的清單操作端點。
- 流程層面：無「約束優先」決策策略（先滿足禁酒，再滿足預算/數量）。

### Solution Design（解決方案設計）
**解決策略**：在模型中加入 isAlcoholic，提供 /carts/{id}/remove-by-category 與 /carts/{id}/replace 的端點；Prompt 指示「先滿足禁酒條件，再試算」。

**實施步驟**：
1. 模型擴充與資料標註
- 實作細節：新增 isAlcoholic；資料回填。
- 所需資源：資料清整
- 預估時間：0.5 人日

2. 清單操作端點
- 實作細節：移除指定分類、替換品。
- 所需資源：API
- 預估時間：1 人日

3. Prompt 規則
- 實作細節：優先滿足合規，再試算調整。
- 所需資源：Prompt
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```yaml
# OpenAPI 端點描述（摘要）
/api/carts/{cartId}/remove-by-category:
  post:
    summary: 從購物車移除指定分類商品（如：alcoholic）
    description: 先滿足法規/合規約束，再進行下一步規劃。
    parameters:
      - in: path
        name: cartId
        required: true
        schema: { type: string }
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [category]
            properties:
              category: { type: string, enum: [alcoholic] }
```

實際案例：使用者以「有小孩」描述，LLM 成功移除酒類商品並重規劃。
實作環境：.NET 8、ASP.NET Core、Azure App Service、OpenAI GPTs。
實測數據：合規約束優先策略後，結果符合期望（定性）。

Learning Points（學習要點）
核心知識點：
- 合規屬性建模（isAlcoholic）
- 批次操作端點設計
- 「約束優先」決策策略

技能要求：
- 必備技能：REST 設計、資料建模
- 進階技能：多約束規劃策略

延伸思考：
- 更多合規屬性（年齡分級、過敏原）
- 合規優先順序配置化
- 與內容安全政策（Safety）聯動

Practice Exercise（練習題）
- 基礎練習：新增 isAlcoholic 並提供移除端點（30 分鐘）
- 進階練習：加入 replace 端點與試算整合（2 小時）
- 專案練習：多合規屬性（過敏原），策略化優先級（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：禁酒/替換流程可行
- 程式碼品質（30%）：模型與端點清晰
- 效能優化（20%）：批次操作效率
- 創新性（10%）：政策化/可配置策略



## Case #5: 不可預測 LLM 行為下的訂單狀態機與冪等設計

### Problem Statement（問題陳述）
**業務場景**：LLM 可能以非預期順序呼叫 API（先結帳、後建購物車等）。若缺乏狀態控管與冪等機制，容易產生錯誤或重複訂單。

**技術挑戰**：設計有限狀態機（FSM）嚴格控管流程，加入冪等機制保證重試安全。

**影響範圍**：資料一致性、金流安全、稽核與客訴。

**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. API 未限制狀態轉移，任何順序都能呼叫。
2. 缺少 Idempotency-Key，重試可能重複下單。
3. 回應錯誤不具語意，LLM 無法修正順序。

**深層原因**：
- 架構層面：缺乏有限狀態機的設計。
- 技術層面：未實作冪等鍵與衝突處理。
- 流程層面：未定義「預期順序」的錯誤引導。

### Solution Design（解決方案設計）
**解決策略**：引入 FSM（Cart: New→Filled→CheckingOut→Paid→Closed），伺服端驗證轉移合法性；所有關鍵操作支援 Idempotency-Key；錯誤訊息提供「應改呼叫的下一步」。

**實施步驟**：
1. 定義 FSM 與狀態檢查
- 實作細節：以 Stateless 實作，端點前置檢查。
- 所需資源：Stateless 套件、DB 欄位
- 預估時間：1-2 人日

2. 加入冪等鍵
- 實作細節：針對 create/checkout 等端點，要求 Idempotency-Key。
- 所需資源：DB 唯一索引、Header 規範
- 預估時間：1 人日

3. 錯誤引導
- 實作細節：4xx 錯誤附「建議下一步端點」。
- 所需資源：錯誤格式
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```csharp
// Stateless FSM（示意）
var machine = new StateMachine<OrderState, Trigger>(order.State);

machine.Configure(OrderState.CartCreated)
    .Permit(Trigger.AddItem, OrderState.CartUpdated);

machine.Configure(OrderState.CartUpdated)
    .Permit(Trigger.Checkout, OrderState.CheckingOut);

machine.Configure(OrderState.CheckingOut)
    .Permit(Trigger.PaymentConfirmed, OrderState.Paid);

machine.Configure(OrderState.Paid)
    .Permit(Trigger.Close, OrderState.Closed);
```

實際案例：原 PoC 寬鬆（任意 PaymentId 可通過），此設計可防暴走，利於上線。
實作環境：.NET 8、ASP.NET Core、Stateless、Azure App Service。
實測數據：引入 FSM＋冪等後，流程錯誤與重複下單風險顯著下降（定性）。

Learning Points（學習要點）
核心知識點：
- 有限狀態機的 API 設計
- 冪等性（Idempotency-Key）
- 錯誤引導語意化

技能要求：
- 必備技能：Stateless/狀態機、REST 實務
- 進階技能：分散式冪等設計

延伸思考：
- 跨服務狀態同步（Saga/Outbox）
- 金流 Webhook 與狀態遷移
- 回滾與補償策略

Practice Exercise（練習題）
- 基礎練習：為 checkout 加入 FSM 驗證（30 分鐘）
- 進階練習：加入 Idempotency-Key 流程（2 小時）
- 專案練習：整合金流 Webhook 與補償機制（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：合法轉移＋冪等
- 程式碼品質（30%）：狀態清晰、測試齊備
- 效能優化（20%）：鎖與併發控制
- 創新性（10%）：錯誤引導與自修正策略



## Case #6: 從自製登入改為標準 OAuth2（提升 LLM Actions 成功率）

### Problem Statement（問題陳述）
**業務場景**：GPTs Actions 自動化呼叫 API；若採自製登入/Token 流程，LLM 難以穩定執行，作者實測嘗試多次均不理想。改為標準 OAuth2 後，一晚搞定且穩定運作。

**技術挑戰**：讓 LLM 能「無需提示技巧」即可通過授權並使用 API。

**影響範圍**：整體成功率、開發/維運成本、安全性。

**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 非標準登入流程，LLM 無固定策略。
2. 缺乏 OpenAPI securitySchemes，Actions 無法理解授權。
3. 無 PKCE/標準授權碼流程，無法對接平台預期行為。

**深層原因**：
- 架構層面：忽略「平台期望的安全對接」。
- 技術層面：缺 OAuth2/OIDC 能力。
- 流程層面：以 prompt 補救取代標準化協定。

### Solution Design（解決方案設計）
**解決策略**：採 OAuth2 Authorization Code with PKCE；OpenAPI 宣告 securitySchemes 與 security；伺服端實作 JWT 驗證；用平台支援的授權對接減少摩擦。

**實施步驟**：
1. OpenAPI 安全宣告
- 實作細節：components.securitySchemes + 全域 security。
- 所需資源：OpenAPI
- 預估時間：0.5 人日

2. 伺服端 OAuth2/OIDC
- 實作細節：實作授權端/或對接現成 IdP，JWT 驗證。
- 所需資源：OpenIddict/Duende/外部 IdP
- 預估時間：1-2 人日

3. Actions 連動測試
- 實作細節：在 GPTs 設定 OAuth 資訊，跑通授權＋API 調用。
- 所需資源：GPTs 設定頁
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```yaml
# OpenAPI OAuth2 宣告（簡化示意）
components:
  securitySchemes:
    OAuth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: https://auth.example.com/authorize
          tokenUrl: https://auth.example.com/token
          scopes:
            orders.read: 讀取訂單
            carts.write: 管理購物車
security:
  - OAuth2: [orders.read, carts.write]
```

實際案例：作者放棄自製流程，改實作 OAuth2 後，Actions 穩定運作，刪除大量補救 prompt。
實作環境：.NET 8、ASP.NET Core、OpenIddict/Duende、Azure App Service、OpenAI GPTs。
實測數據：從「頻繁失敗」到「穩定通過授權」（定性）；開發工時顯著降低（定性）。

Learning Points（學習要點）
核心知識點：
- OAuth2/OIDC 與 PKCE
- OpenAPI securitySchemes
- GPTs Actions 授權對接模式

技能要求：
- 必備技能：JWT/OAuth2 基礎
- 進階技能：IdP 對接與範圍管理

延伸思考：
- 多租戶與組織範圍
- 權限最小化（least privilege）
- Token 生命週期與輪轉

Practice Exercise（練習題）
- 基礎練習：為 API 增加 OAuth2 安全宣告（30 分鐘）
- 進階練習：用 OpenIddict/Duende 搭建簡易 IdP（2 小時）
- 專案練習：在 GPTs 設好 Actions OAuth，完成端到端測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：授權能端到端運作
- 程式碼品質（30%）：設定清楚、錯誤處理完善
- 效能優化（20%）：Token 驗證效能、快取
- 創新性（10%）：多範圍細粒度控制



## Case #7: 訂單歷史彙整與統計（LLM 摘要強化 UX）

### Problem Statement（問題陳述）
**業務場景**：顧客詢問「我買過哪些？各買了幾件？」API 僅提供原始訂單與項目，格式冗長；LLM 要在對話中總結、統計並回傳摘要。

**技術挑戰**：讓 LLM 正確地在會話上下文中彙整多筆 JSON，並提供正確總數。

**影響範圍**：客服體驗、資訊可讀性、回覆準確率。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. API 沒有提供彙整端點（僅 raw data）。
2. LLM 缺少輸出格式統一規範。
3. 回覆缺乏可核對的數字欄位。

**深層原因**：
- 架構層面：將摘要責任留給前端/LLM，未定義最終格式。
- 技術層面：缺少「訊息→結構化輸出」流程。
- 流程層面：未定義「先取資料→再摘要→再展示」的標準節奏。

### Solution Design（解決方案設計）
**解決策略**：保留 /member/orders 原樣，新增「摘要指示」Prompt 與「輸出 JSON 再轉可讀格式」的兩階段流程；可選擇導入函數呼叫/工具，使 LLM 固定輸出結構再渲染。

**實施步驟**：
1. 定義摘要 Schema
- 實作細節：name、totalQty、totalAmount 等欄位。
- 所需資源：JSON Schema
- 預估時間：0.5 人日

2. 兩階段輸出
- 實作細節：先輸出 JSON（可機器處理），再轉表格/文字。
- 所需資源：LLM Prompt、前端渲染
- 預估時間：0.5 人日

3. 驗證與誤差修正
- 實作細節：檢查合計是否等於原始資料加總，不符時要求 LLM 重算。
- 所需資源：檢核邏輯
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```json
// LLM 工具輸出結構（示意）
{
  "productsSummary": [
    { "name": "18天台灣生啤酒 355ml", "totalQty": 12, "totalAmount": 780 },
    { "name": "可口可樂 350ml", "totalQty": 36, "totalAmount": 648 }
  ],
  "grandTotalAmount": 1428
}
```

實際案例：PoC 中 LLM 將冗長原始訂單整理為可讀摘要與表格。
實作環境：OpenAI GPTs、現有 /member/orders、任意前端渲染。
實測數據：摘要之後的資訊可讀性大幅提升、回覆更貼近客服語境（定性）。

Learning Points（學習要點）
核心知識點：
- 兩階段輸出（機器可讀→人類可讀）
- JSON Schema 與表格渲染
- 回覆自校驗

技能要求：
- 必備技能：API 消費與資料摘要
- 進階技能：函數呼叫與 Schema 驗證

延伸思考：
- 大量資料需先做 server-side 預彙整？
- 訂單抽樣摘要 vs 全量摘要？
- 多輪對話如何維持上下文一致？

Practice Exercise（練習題）
- 基礎練習：設計摘要 JSON Schema（30 分鐘）
- 進階練習：加入自校驗策略（2 小時）
- 專案練習：將摘要渲染為 Markdown/HTML 表格（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：摘要完整、可核對
- 程式碼品質（30%）：結構清晰、驗證到位
- 效能優化（20%）：大資料處理策略
- 創新性（10%）：自我修正策略



## Case #8: 將 LLM 回應標準化為 Markdown 表格

### Problem Statement（問題陳述）
**業務場景**：客服/商務常希望以表格查看統計。LLM 能自然回應，但若無格式約束，資訊不易複製/再加工。

**技術挑戰**：限制 LLM 以 Markdown 表格輸出、欄位固定、可再次匯入。

**影響範圍**：可讀性、報告再利用、跨工具流程。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無輸出格式提示。
2. 欄位命名不統一，難二次處理。
3. 表格與原始 JSON 不一致，無法比對。

**深層原因**：
- 架構層面：未定義輸出標準。
- 技術層面：缺少轉換模板。
- 流程層面：缺少「先 JSON、後表格」。

### Solution Design（解決方案設計）
**解決策略**：固定「先產 JSON、再渲染表格」；提供欄位清單與 Markdown 格式範例；在不一致時要求重試。

**實施步驟**：
1. 定義欄位與表頭
- 實作細節：name、qty、amount 等。
- 所需資源：模板
- 預估時間：0.5 人日

2. Prompt 片語庫
- 實作細節：加入「請輸出 Markdown 表格」片語。
- 所需資源：Prompt
- 預估時間：0.5 人日

3. 一致性檢查
- 實作細節：比對 JSON 與表格欄位、一致性。
- 所需資源：小工具/檢核程式
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```
指示詞片段：
- 請先輸出結構化 JSON，再以相同欄位輸出 Markdown 表格。
- 表頭固定為：商品, 數量, 金額(元)
- 若 JSON 與表格合計不一致，請自我修正後重試輸出。
```

實際案例：PoC 中 LLM 由冗長 JSON 轉為可讀表格，方便使用者理解。
實作環境：OpenAI GPTs 或任一 LLM。
實測數據：可讀性與二次使用性提升（定性）。

Learning Points（學習要點）
核心知識點：
- 報表格式標準化
- 一致性檢核
- Prompt 模板化

技能要求：
- 必備技能：Prompt 設計
- 進階技能：輸出可驗證流程

延伸思考：
- 直接輸出 CSV/TSV？
- 多語系表頭切換？
- 表格過長時的折疊策略？

Practice Exercise（練習題）
- 基礎練習：將任意 JSON 轉 Markdown 表格（30 分鐘）
- 進階練習：加入自校驗與重試（2 小時）
- 專案練習：做一個「JSON→表格」小型服務（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可讀、可核對
- 程式碼品質（30%）：模板清楚、可擴充
- 效能優化（20%）：長表格處理
- 創新性（10%）：格式多樣化



## Case #9: 對 LLM 呼叫加上護欄（參數約束與錯誤語意）

### Problem Statement（問題陳述）
**業務場景**：LLM 可能傳負數數量、異常 cartId，造成 4xx/5xx。若無參數約束與語意化錯誤，LLM 難以自動修正。

**技術挑戰**：兼顧 OpenAPI schema 約束與伺服端驗證，回傳能引導 LLM 修正的錯誤。

**影響範圍**：錯誤率、重試成本、成功率。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. OpenAPI schema 未定義 minimum/pattern。
2. 伺服端未做強固驗證。
3. 錯誤訊息不具引導性。

**深層原因**：
- 架構層面：忽略「LLM 會犯人類常識錯誤」的預設。
- 技術層面：schema 與伺服端驗證缺一不可。
- 流程層面：未將錯誤視為「LLM 對話的一部分」。

### Solution Design（解決方案設計）
**解決策略**：OpenAPI 嚴格約束＋伺服端 FluentValidation；統一錯誤結構（含建議修正方式）；必要時回傳「下一步建議」。

**實施步驟**：
1. Schema 約束
- 實作細節：minimum、pattern、enum、required。
- 所需資源：OpenAPI
- 預估時間：0.5 人日

2. 伺服端驗證
- 實作細節：FluentValidation/自訂驗證。
- 所需資源：.NET 套件
- 預估時間：1 人日

3. 語意化錯誤
- 實作細節：ApiError {code, message, hint, nextActions[]}
- 所需資源：錯誤規格
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```json
{
  "code": "InvalidQuantity",
  "message": "數量必須為 1~99 的整數。",
  "hint": "請將 quantity 設在 1~99 範圍內。",
  "nextActions": [
    { "path": "/api/carts/{cartId}/items", "method": "POST", "paramsHint": { "quantity": "1~99" } }
  ]
}
```

實際案例：對 LLM 出錯參數回以語意化錯誤，LLM 能自動修正重試。
實作環境：.NET 8、FluentValidation、OpenAPI、OpenAI GPTs。
實測數據：LLM 誤用端點時的自我修正率提升（定性）。

Learning Points（學習要點）
核心知識點：
- 雙層驗證：Schema＋Server
- 語意化錯誤結構設計
- 對話式除錯

技能要求：
- 必備技能：OpenAPI/驗證
- 進階技能：錯誤引導設計

延伸思考：
- 將錯誤作為「工具回饋」的一部分餵給 LLM
- 分級錯誤（可修復/不可修復）
- 自動回退策略

Practice Exercise（練習題）
- 基礎練習：加入數量的 minimum/maximum（30 分鐘）
- 進階練習：撰寫 FluentValidation 與一致錯誤（2 小時）
- 專案練習：為 5 類常見錯誤設計 nextActions（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：錯誤可引導修復
- 程式碼品質（30%）：驗證分層清楚
- 效能優化（20%）：低成本驗證
- 創新性（10%）：對話式錯誤引導



## Case #10: 以 DDD/Domain API 精簡邏輯（API First）

### Problem Statement（問題陳述）
**業務場景**：PoC 顯示，LLM 扛起大量 UX/流程邏輯後，後端 API 可極度精簡，只保留「核心域」能力（商品、購物車、試算、結帳、訂單）。

**技術挑戰**：如何用少量端點覆蓋完整核心流程，同時對 LLM 友善。

**影響範圍**：後端複雜度、維護成本、擴充性。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. 傳統設計將大量 UI/流程搬到後端。
2. LLM 識別意圖後可彈性組合 API，冗餘端點反而造成困惑。
3. 未以業務模型抽象出穩定資源。

**深層原因**：
- 架構層面：未採 API First 與 DDD 名詞表。
- 技術層面：端點碎片化、粒度不一。
- 流程層面：未以「LLM 調度」視角反設計 API。

### Solution Design（解決方案設計）
**解決策略**：以 Domain 切割最小可用能力，僅保留 Products/Carts/Estimate/Checkout/Orders 五大群組；其餘由 LLM 規劃（如預算、替換、摘要）。

**實施步驟**：
1. 名詞與界限上下文
- 實作細節：建立 ubiquitous language，對齊名稱。
- 所需資源：DDD Workshop
- 預估時間：1 人日

2. 端點最小集
- 實作細節：精簡端點，維持清晰 CRUD＋試算＋交易。
- 所需資源：API 設計
- 預估時間：1 人日

3. LLM 職責邊界
- 實作細節：用 Prompt 清楚切邊界。
- 所需資源：Prompt 指南
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```yaml
# 最小端點集（摘要）
/api/products (GET)
/api/products/search?query= (GET)
/api/carts (POST)
/api/carts/{id}/items (POST/DELETE)
/api/carts/{id}/estimate (POST)
/api/checkout/create (POST)
/api/checkout/{id}/confirm (POST)
/api/member/orders (GET)
```

實際案例：PoC 最終確立由 LLM 接手大部分「流程/UX」，API 僅保核心域能力。
實作環境：.NET 8、ASP.NET Core、Azure App Service、OpenAI GPTs。
實測數據：端點數減少、說明更精準，LLM 誤用率下降（定性）。

Learning Points（學習要點）
核心知識點：
- DDD 名詞表與 API First
- LLM 驅動下的最小端點集
- 功能與流程拆分

技能要求：
- 必備技能：DDD/REST 設計
- 進階技能：邊界設計與權責分工

延伸思考：
- 微服務如何與 LLM 呼叫對齊？
- API Gateway 如何提供 LLM 友善視圖？
- 版本管理策略（LLM 背後大量依賴文件）

Practice Exercise（練習題）
- 基礎練習：從既有端點縮減為最小集（30 分鐘）
- 進階練習：為最小集補齊自然語言描述（2 小時）
- 專案練習：以最小集重新跑通整個購物流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：完整覆蓋用例
- 程式碼品質（30%）：簡潔穩固
- 效能優化（20%）：少端點更高命中率
- 創新性（10%）：邊界清晰



## Case #11: 面對 LLM 不穩定（不 100%）的自我檢查與重試

### Problem Statement（問題陳述）
**業務場景**：作者實測中，LLM 偶爾給出「不是最優」或錯誤方案；抱怨後再算一次就對了。需要在流程內化「自校驗→重算」。

**技術挑戰**：在不暴露思考鏈的前提下，設計序貫的自查重試，提升最終正確性。

**影響範圍**：成功率、對話輪次、API 呼叫次數。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. LLM 具隨機性，非完全穩定。
2. 缺乏自我檢查檢核點。
3. 無「計畫 vs 結果」的對比步驟。

**深層原因**：
- 架構層面：流程未內建自我修正。
- 技術層面：沒有標準的檢核函式/工具。
- 流程層面：缺「不滿意→重試」的機制。

### Solution Design（解決方案設計）
**解決策略**：每次給出方案後，必做「驗證步驟」：以 /estimate 對照預算、約束、用戶偏好；不過關則自我修正再試一次（限制重試次數）。

**實施步驟**：
1. 檢核清單
- 實作細節：預算、禁品、數量接近、優惠已用盡。
- 所需資源：Prompt 清單
- 預估時間：0.5 人日

2. 重試控制
- 實作細節：最多重試 N 次，否則回報「無解/建議放寬條件」。
- 所需資源：策略設定
- 預估時間：0.5 人日

3. 日誌與可觀測
- 實作細節：記錄每次檢核與修正，利於評估。
- 所需資源：Logging
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```text
指示詞片段：
- 給出方案後，務必呼叫 /estimate 驗證是否滿足：預算、禁酒、數量接近。
- 若未滿足，請調整購物清單並再次驗證；最多重試 3 次。
- 回覆中請列出「最終合格」的理由與驗證數據摘要。
```

實際案例：作者觀察，抱怨後重算即對；將此轉為流程可提升穩定性。
實作環境：OpenAI GPTs、現有 API。
實測數據：引入自我檢查與重試後，錯誤方案顯著下降（定性）。

Learning Points（學習要點）
核心知識點：
- 自我檢查（self-check）
- 重試與中止條件
- 透明化驗證資料

技能要求：
- 必備技能：Prompt 策略
- 進階技能：可觀測性與 A/B 驗證

延伸思考：
- 自我反思（self-consistency）策略融合
- 以工具函式返回「檢核通過/未通過」布林值
- 成本控制（重試上限/停止）

Practice Exercise（練習題）
- 基礎練習：加入固定檢核清單（30 分鐘）
- 進階練習：實作重試上限與中止（2 小時）
- 專案練習：收集多輪檢核資料做成 KPI 看板（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：檢核與重試機制
- 程式碼品質（30%）：策略清晰可調
- 效能優化（20%）：成本/輪次受控
- 創新性（10%）：自我反思技巧



## Case #12: 「店長」系統指示（System Prompt）設計

### Problem Statement（問題陳述）
**業務場景**：LLM 扮演「店長」，需理解角色責任、授權邊界、語氣、成功策略（先搜、先估、先檢核）。

**技術挑戰**：把業務規則、作業流程、禁忌行為清晰嵌入 System Prompt。

**影響範圍**：對話品質、成功率、合規性。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未寫清楚角色與禁令（如：禁自行計算折扣）。
2. 缺少「典型流程」說明。
3. 缺少錯誤處理策略。

**深層原因**：
- 架構層面：把流程當前端交互，忽視 LLM 的 Orchestrator 角色。
- 技術層面：未模板化指示。
- 流程層面：無版本化與回歸測試。

### Solution Design（解決方案設計）
**解決策略**：製作可版本化 System Prompt：角色、語氣、策略、禁忌、合規；列出關鍵 API 使用規約（先搜/先估/先檢核/再下單）。

**實施步驟**：
1. 指示模板
- 實作細節：以段落模板維護與版本化。
- 所需資源：Repo/檔案
- 預估時間：0.5 人日

2. 流程卡
- 實作細節：把流程寫成要點，便於 LLM 遵循。
- 所需資源：流程圖/要點清單
- 預估時間：0.5 人日

3. 測試與微調
- 實作細節：多輪對話測試 + 迭代 Prompt。
- 所需資源：測試腳本
- 預估時間：1 人日

**關鍵程式碼/設定**：
```
System Prompt 範例（片段）
- 你是線上商店的店長，需以友善、專業、簡潔的語氣服務。
- 禁止自行計算任何折扣，所有金額以 /api/carts/{id}/estimate 為準。
- 若使用者僅說「啤酒/綠茶」，先呼叫 /api/products/search 查找。
- 若提及「有小孩」等語句，移除 isAlcoholic=true 的項目後再規劃。
- 策略：先規劃→試算→檢核→下單；不通過則自我修正最多 3 次。
```

實際案例：PoC 中透過角色設定與行為規範，LLM 能接近「真人店長」服務體驗。
實作環境：OpenAI GPTs。
實測數據：語氣一致性提高、誤用 API 機率下降（定性）。

Learning Points（學習要點）
核心知識點：
- System Prompt 結構化
- 策略式指令
- 版本化與回歸測試

技能要求：
- 必備技能：Prompt 基礎
- 進階技能：策略模板與實驗

延伸思考：
- 多語言切換
- 動態插入店規/促銷公告
- 團隊協作維護 Prompt

Practice Exercise（練習題）
- 基礎練習：寫一份店長指示詞（30 分鐘）
- 進階練習：加入失敗重試策略（2 小時）
- 專案練習：建立 Prompt 版本與 A/B 測試（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：包含角色/策略/禁令
- 程式碼品質（30%）：可維護、版本化
- 效能優化（20%）：減少輪次/誤用
- 創新性（10%）：結合營運公告



## Case #13: 以 Swagger 快速掛上 GPTs Custom Actions

### Problem Statement（問題陳述）
**業務場景**：希望免寫額外 glue code，讓 LLM 自動讀 Swagger 並決定何時呼叫 API。

**技術挑戰**：準備對 Actions 友善的 Swagger，並在 GPTs 後台正確掛載。

**影響範圍**：開發門檻、集成速度、維護成本。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. Swagger 缺少 description 與例子。
2. 未宣告安全機制。
3. 忽略 LLM 會以自然語言理解 description。

**深層原因**：
- 架構層面：文件非以 LLM 為讀者。
- 技術層面：Swagger 欠完備。
- 流程層面：未形成「文件→掛載→測試」的節奏。

### Solution Design（解決方案設計）
**解決策略**：將 Swagger 作為 LLM 文件，補語意、例子、安全宣告；在 GPTs 後台匯入；以測試對話驗證。

**實施步驟**：
1. Swagger 完備化
- 實作細節：description、examples、安全宣告。
- 所需資源：Swashbuckle
- 預估時間：0.5 人日

2. GPTs 掛載
- 實作細節：在 Custom Actions 中貼上 Swagger URL。
- 所需資源：GPTs 後台
- 預估時間：0.5 人日

3. 對話測試
- 實作細節：發起包含搜尋/加入/試算/結帳的對話腳本。
- 所需資源：測試腳本
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```json
// GPTs Actions 設定（概念示意）
{
  "schema": "openapi",
  "url": "https://yourapp.azurewebsites.net/swagger/v1/swagger.json",
  "auth": {
    "type": "oauth2",
    "authorizationUrl": "https://auth.example.com/authorize",
    "tokenUrl": "https://auth.example.com/token"
  }
}
```

實際案例：PoC 成功以 GPTs Actions 調用 API 完成整個購物流程。
實作環境：Azure App Service、OpenAI GPTs、Swagger（Swashbuckle）。
實測數據：幾乎零樣板碼即可連動（定性）。

Learning Points（學習要點）
核心知識點：
- Swagger 作為 LLM 指南
- GPTs Actions 掛載
- 對話式端到端測試

技能要求：
- 必備技能：Swagger/REST
- 進階技能：對話測試設計

延伸思考：
- 多環境（測試/正式）切換
- 版本管理與回退
- 自動化 Actions 健康檢查

Practice Exercise（練習題）
- 基礎練習：把本地 API 掛上 GPTs（30 分鐘）
- 進階練習：加上 OAuth2 設定與測試（2 小時）
- 專案練習：寫 5 段端到端對話腳本跑通流程（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能調用主要端點
- 程式碼品質（30%）：文件清晰
- 效能優化（20%）：回應時間/錯誤率
- 創新性（10%）：自動化測試腳本



## Case #14: Azure App Service 快速部署 PoC（易揮發資料的風險控管）

### Problem Statement（問題陳述）
**業務場景**：PoC 快速上線驗證，用Azure App Service 部署，資料放記憶體，重啟清空。需平衡便利與風險。

**技術挑戰**：提供足夠穩定性與可用性，同時告知限制並準備升級路徑。

**影響範圍**：體驗連續性、測試可信度、風險控管。

**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 記憶體儲存，重啟即清空。
2. 無 HA 與持久層。
3. 未設健康檢查與自動擴展。

**深層原因**：
- 架構層面：PoC 模式未設計可持續性。
- 技術層面：缺乏持久化與監控。
- 流程層面：未規劃升級步驟。

### Solution Design（解決方案設計）
**解決策略**：保留 PoC 便利、明示限制，補上健康檢查與基礎監控；提供升級藍圖（DB、快取、備援）。

**實施步驟**：
1. 部署與健康檢查
- 實作細節：App Service、/health 檢查。
- 所需資源：Azure CLI
- 預估時間：0.5 人日

2. 基礎監控
- 實作細節：Application Insights、日志。
- 所需資源：Azure 服務
- 預估時間：0.5 人日

3. 升級路徑文件
- 實作細節：加入 DB、Redis、區域冗餘方案。
- 所需資源：設計文件
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```bash
# Azure CLI（示意）
az webapp up --runtime "DOTNET|8.0" --name yourapp --resource-group your-rg

# 健康檢查端點
GET /health -> 200 OK
```

實際案例：作者以 App Service 快速上線驗證；明示無 HA 與資料易揮發。
實作環境：Azure App Service、.NET 8、App Insights（可選）。
實測數據：快速驗證可行性；接受 PoC 限制（定性）。

Learning Points（學習要點）
核心知識點：
- PoC vs 產品級部署的差異
- 健康檢查/監控
- 升級藍圖

技能要求：
- 必備技能：Azure 基礎部署
- 進階技能：可觀測性/可用性設計

延伸思考：
- 容器化與 CI/CD
- 藍綠部署/金絲雀釋出
- 成本最佳化

Practice Exercise（練習題）
- 基礎練習：部署到 App Service 並加 /health（30 分鐘）
- 進階練習：接入 App Insights（2 小時）
- 專案練習：寫一份升級藍圖（DB/快取/HA）（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可用/可測
- 程式碼品質（30%）：設定清晰
- 效能優化（20%）：監控到位
- 創新性（10%）：升級設計



## Case #15: 從 GPTs 過渡到自有 Orchestrator（Semantic Kernel）

### Problem Statement（問題陳述）
**業務場景**：PoC 用 GPTs 很快，但長期需要自有 Orchestrator（本地/企業控管、組裝插件、記憶、規劃）。

**技術挑戰**：以 Semantic Kernel（SK）重構：插件（Skills/Plugins）、規劃器（Planner）、記憶（Memory）、連接器（Connectors）。

**影響範圍**：擴展性、私有化、跨模組協作、成本。

**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. GPTs 平台封閉，難整合企業內資源。
2. 缺少可插拔與跨模組編排。
3. 記憶/規劃需自控。

**深層原因**：
- 架構層面：需標準化 AI App 架構（SK）。
- 技術層面：需要 Plugins/Planner/Memory 能力。
- 流程層面：CI/CD 與治理。

### Solution Design（解決方案設計）
**解決策略**：以 SK 建立 Plugins 封裝現有 API；用 Planner 將自然語言轉為 Plan；Memory 記錄上下文；Connectors 串模型（本地/雲）。

**實施步驟**：
1. 寫 Plugins
- 實作細節：將 products、cart、orders 包裝為 SK Functions。
- 所需資源：SK SDK（C#/.NET）
- 預估時間：1-2 人日

2. 加入 Planner
- 實作細節：把「先搜/估/檢/下」寫成樣板計畫。
- 所需資源：SK Planner
- 預估時間：1 人日

3. 記憶與連接器
- 實作細節：對話記憶、模型接入（Azure OpenAI 或本地）。
- 所需資源：Memory store
- 預估時間：1 人日

**關鍵程式碼/設定**：
```csharp
public class CartPlugin
{
    private readonly ICartService _svc;

    public CartPlugin(ICartService svc) => _svc = svc;

    [SKFunction, SKName("AddItemToCart")]
    public async Task<string> AddItemAsync(string cartId, int productId, int quantity)
        => await _svc.AddItemAsync(cartId, productId, quantity);

    [SKFunction, SKName("EstimateCart")]
    public async Task<decimal> EstimateAsync(string cartId)
        => await _svc.EstimateAsync(cartId);
}
```

實際案例：作者計畫以 SK 重構 PoC；本文闡明 SK 架構適配未來主流。
實作環境：.NET 8、Semantic Kernel 1.x、Azure OpenAI。
實測數據：可控性/擴展性提升（定性）。

Learning Points（學習要點）
核心知識點：
- SK 五大構件：Kernel/Plugins/Planner/Memory/Connectors
- Orchestration 模式
- 從平台化過渡到自控

技能要求：
- 必備技能：.NET/SK 開發
- 進階技能：多模型/多插件協作

延伸思考：
- 作業系統級 Orchestrator（未來趨勢）
- PaaS 級 AI 應用基座
- 治理與權限模型

Practice Exercise（練習題）
- 基礎練習：撰寫一個 SK Plugin 包裝 /products（30 分鐘）
- 進階練習：Planner 將「預算購買」轉成 Plan（2 小時）
- 專案練習：加入 Memory 與多插件協作（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：插件＋規劃＋記憶
- 程式碼品質（30%）：介面清晰、可測
- 效能優化（20%）：模型/插件協作效率
- 創新性（10%）：連接器多元化



## Case #16: LLM vs Code 邊界判斷（意圖 vs 計算）

### Problem Statement（問題陳述）
**業務場景**：哪些交給 LLM（意圖理解與規劃），哪些交給 API（精確計算與交易）？作者總結：折扣計算等精確任務交給 API，預算規劃交給 LLM。

**技術挑戰**：制定適用的決策準則與執行邊界。

**影響範圍**：正確率、成本、可維護性。

**複雜度評級**：中

### Root Cause Analysis（根因分析）
**直接原因**：
1. LLM 成本高且有隨機性。
2. 精確計算用 LLM 易出錯。
3. 意圖/條件的理解 LLM 擅長。

**深層原因**：
- 架構層面：未定義邊界。
- 技術層面：沒有固定的流程模板。
- 流程層面：需求分析仍以 MVC 思維。

### Solution Design（解決方案設計）
**解決策略**：建立「邊界決策樹」：意圖/多變/語義模糊→LLM；精確/可測/交易→API；在 Prompt 中寫死「計算/交易皆走 API」。

**實施步驟**：
1. 邊界準則
- 實作細節：列出任務清單與分類。
- 所需資源：決策表
- 預估時間：0.5 人日

2. 流程模板
- 實作細節：先 LLM 規劃→API 試算/交易。
- 所需資源：模板/範本
- 預估時間：0.5 人日

3. 執行監控
- 實作細節：標注每步是 LLM 還是 API，便於審核。
- 所需資源：日誌
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```
指示詞要點：
- 涉及金額、庫存、交易之精確計算，一律透過 API 完成。
- 你只負責理解意圖、規劃方案、協調 API 呼叫順序與參數。
```

實際案例：PoC 實證此邊界能提升穩定度與正確性。
實作環境：OpenAI GPTs、既有 API。
實測數據：錯誤率下降、對話更聚焦（定性）。

Learning Points（學習要點）
核心知識點：
- 邊界判斷與模板化
- 意圖/計算分工
- 成本/風險平衡

技能要求：
- 必備技能：需求拆解
- 進階技能：流程工程

延伸思考：
- 隨著模型進步，邊界會變嗎？
- 可以根據信心分數調整邊界？
- 人在回圈（HITL）介入時機？

Practice Exercise（練習題）
- 基礎練習：為 5 個任務判斷 LLM vs API（30 分鐘）
- 進階練習：落地成流程模板（2 小時）
- 專案練習：紀錄決策與結果，建立回饋機制（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：邊界清晰
- 程式碼品質（30%）：模板可重用
- 效能優化（20%）：成本/輪次下降
- 創新性（10%）：動態邊界



## Case #17: AI×API 可觀測性（工具呼叫追蹤與關聯）

### Problem Statement（問題陳述）
**業務場景**：LLM 會自發決定呼叫 API，若缺乏可觀測性，難以重現問題與優化流程。

**技術挑戰**：建立以「對話 Session」為核心的關聯 ID，記錄每次工具呼叫、參數與結果、錯誤與修正。

**影響範圍**：除錯效率、優化能力、責任切清。

**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 無關聯 ID/Session 設計。
2. 日誌缺少上下文（prompt、工具呼叫）。
3. 無指標（成功率、輪次、錯誤率）。

**深層原因**：
- 架構層面：未把「LLM 行為」當作系統事件。
- 技術層面：缺分散式追蹤與結構化日誌。
- 流程層面：無 SLO/KPI。

### Solution Design（解決方案設計）
**解決策略**：在每次對話注入 x-session-id，API 層以結構化日誌（Serilog）紀錄 call、參數、結果；導入 Application Insights/OTEL，建立儀表板（對話成功率、API 調用分布、錯誤 TopN）。

**實施步驟**：
1. 關聯 ID 與結構化日誌
- 實作細節：x-session-id 透傳；Serilog JSON。
- 所需資源：Serilog/中介程式
- 預估時間：1 人日

2. 追蹤與儀表板
- 實作細節：App Insights/OTEL，建立看板。
- 所需資源：Azure/OTEL
- 預估時間：1-2 人日

3. KPI 與警示
- 實作細節：成功率、平均輪次、4xx/5xx 門檻警示。
- 所需資源：監控告警
- 預估時間：0.5 人日

**關鍵程式碼/設定**：
```csharp
// Serilog 結構化日誌（示意）
Log.ForContext("SessionId", sessionId)
   .ForContext("Action", "AddItem")
   .ForContext("Params", new { cartId, productId, quantity })
   .Information("LLM tool call invoked");
```

實際案例：便於重現 LLM 行為、找出誤用端點與常見錯誤。
實作環境：.NET 8、Serilog、App Insights/OTEL、OpenAI GPTs。
實測數據：除錯時間下降、行為洞察提升（定性）。

Learning Points（學習要點）
核心知識點：
- 對話關聯追蹤
- 結構化日誌與可觀測性
- KPI/SLO for AI×API

技能要求：
- 必備技能：Logging/Tracing
- 進階技能：監控設計

延伸思考：
- 隱私/合規（PII 遮罩）
- 成本監控（token/call）
- 自動化修復與建議

Practice Exercise（練習題）
- 基礎練習：導入 x-session-id 與結構化日誌（30 分鐘）
- 進階練習：建立 App Insights 儀表板（2 小時）
- 專案練習：KPI 與警示門檻設計（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：可追蹤、可視化
- 程式碼品質（30%）：上下文完善
- 效能優化（20%）：低開銷
- 創新性（10%）：洞察與自動化



## Case #18: 金流安全與驗證（取代「任意 PaymentId 即通過」）

### Problem Statement（問題陳述）
**業務場景**：PoC 簡化「拿到支付 ID 就當成功」，方便驗證流程。但產品上線需真正驗證支付，避免詐欺與對帳問題。

**技術挑戰**：整合外部金流（模擬亦可），建立支付狀態查核、Webhook 回補、冪等與對帳。

**影響範圍**：金流安全、財務正確性、法遵。

**複雜度評級**：高

### Root Cause Analysis（根因分析）
**直接原因**：
1. 未驗證支付狀態。
2. 缺 Webhook 更新狀態。
3. 無對帳機制。

**深層原因**：
- 架構層面：交易流程與金流整合缺失。
- 技術層面：狀態機未含「金流回補」。
- 流程層面：缺對帳/稽核程序。

### Solution Design（解決方案設計）
**解決策略**：建立 /checkout/create→取得 paymentIntent；/checkout/{id}/confirm 僅接受 verified 狀態；導入金流 Webhook 更新；提供 /reconcile 對帳工具；全程 Idempotency-Key。

**實施步驟**：
1. 金流整合
- 實作細節：PaymentIntent 建立/確認 API。
- 所需資源：金流 Sandbox
- 預估時間：2 人日

2. Webhook 與狀態回補
- 實作細節：收到成功事件 → 訂單轉 Paid。
- 所需資源：Webhook 端點
- 預估時間：1 人日

3. 對帳工具
- 實作細節：拉取交易清單比對，出報表。
- 所需資源：批次工具
- 預估時間：1 人日

**關鍵程式碼/設定**：
```csharp
// 只在金流已 verified 時才允許完成
if (!paymentService.IsVerified(paymentIntentId))
    return BadRequest(new ApiError { code="PaymentNotVerified", message="請先完成支付驗證。" });

Transition(order, Trigger.PaymentConfirmed);
```

實際案例：PoC 為快速驗證刻意簡化；此方案為產品化必備強化。
實作環境：.NET 8、外部金流 Sandbox、Webhook、Stateless FSM。
實測數據：避免假支付、提高對帳正確性（定性）。

Learning Points（學習要點）
核心知識點：
- 金流整合模式
- Webhook 與狀態機
- 對帳流程

技能要求：
- 必備技能：Webhook/金流 API
- 進階技能：對帳與稽核

延伸思考：
- 3D Secure、風險評分
- 異常單補償流程
- PCI 與個資保護

Practice Exercise（練習題）
- 基礎練習：建立 PaymentIntent 模擬（30 分鐘）
- 進階練習：Webhook 回補與 FSM 整合（2 小時）
- 專案練習：對帳批次與報表（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：支付驗證＋狀態回補
- 程式碼品質（30%）：安全健全
- 效能優化（20%）：Webhook 可用性
- 創新性（10%）：風控策略



——————————
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case 3 同義詞與自然語言對齊
  - Case 8 Markdown 表格輸出
  - Case 12 店長 System Prompt 設計
  - Case 13 掛上 GPTs Actions
  - Case 14 Azure App Service PoC 部署
- 中級（需要一定基礎）
  - Case 1 LLM-Friendly API 設計
  - Case 2 預算＋折扣規劃
  - Case 4 禁酒條件處理
  - Case 7 訂單歷史彙整
  - Case 9 參數護欄與錯誤語意
  - Case 10 Domain API 精簡
  - Case 11 自我檢查與重試
  - Case 16 LLM vs Code 邊界
- 高級（需要深厚經驗）
  - Case 5 狀態機與冪等
  - Case 6 OAuth2 標準授權
  - Case 15 Semantic Kernel Orchestrator
  - Case 17 可觀測性與追蹤
  - Case 18 金流安全與對帳

2. 按技術領域分類
- 架構設計類：Case 2, 5, 10, 15, 16, 18
- 效能優化類：Case 9, 11, 17（間接提升效率與成功率）
- 整合開發類：Case 1, 3, 4, 6, 7, 8, 12, 13, 14, 15
- 除錯診斷類：Case 9, 11, 17
- 安全防護類：Case 4, 6, 9, 18

3. 按學習目標分類
- 概念理解型：Case 2, 10, 15, 16
- 技能練習型：Case 1, 3, 6, 7, 8, 12, 13, 14
- 問題解決型：Case 4, 5, 9, 11, 17, 18
- 創新應用型：Case 2, 15


——————————
案例關聯圖（學習路徑建議）

- 入門起步（先學）：
  1) Case 13（把 Swagger 掛到 GPTs Actions）
  2) Case 12（設計店長 System Prompt）
  3) Case 1（把 API 改成 LLM-Friendly）
  4) Case 14（部署 PoC 到 Azure App Service）

- 進一步強化（中級）：
  5) Case 3（搜尋與同義詞）→ 6) Case 4（禁酒條件處理）
  7) Case 7（訂單歷史彙整）→ 8) Case 8（表格輸出）
  9) Case 2（預算＋折扣規劃）→ 10) Case 11（自我檢查與重試）
  11) Case 9（護欄與錯誤語意）→ 12) Case 10（Domain API 精簡）

- 產品級能力（高級）：
  13) Case 6（OAuth2 標準授權）→ 14) Case 5（狀態機與冪等）
  15) Case 17（可觀測性與追蹤）
  16) Case 18（金流安全與對帳）

- 架構升級與創新：
  17) Case 16（LLM vs Code 邊界）→ 18) Case 15（Semantic Kernel Orchestrator）

依賴關係提示：
- Case 1 是大多數後續案例的前置（文件與語意是基礎）。
- Case 6（OAuth2）與 Case 5（FSM）是走向產品化的關鍵支柱。
- Case 15（SK）建立在前述邊界清楚、API 精簡、流程可觀測的前提上。

完整學習路徑總結：
- 先把 API 文件與基本掛載跑通（13→12→1→14）
- 增強自然語言能力與摘要展示（3→4→7→8）
- 讓 LLM 真正接手規劃但可自我修正（2→11→9→10）
- 產品化安全與穩定（6→5→17→18）
- 最後過渡至可控的 AI 開發框架（16→15）

以上 18 個案例皆出自原文 PoC 與觀點延伸，保留原文中的核心挑戰與成效觀察，同時補齊可落地的程式碼、流程與教學練習。