# [架構師的修練] #3, 刻意練習 - 如何鍛鍊你的抽象化能力

# 問題／解決方案 (Problem/Solution)

## Problem: 零售折扣邏輯難以持續擴充

**Problem**:  
在零售系統中，需要計算「各式未知且持續增加的折扣規則」。若以傳統硬寫 if/else 的方式維護邏輯，一旦行銷活動變更或新增，程式將快速失控，測試與維運成本急遽上升。

**Root Cause**:  
1. 折扣規則多變且彼此獨立，卻被寫在同一段流程中，缺乏「抽象化」與「邊界」設計。  
2. 缺乏一個可擴充的契約 (interface) 讓新規則可以即插即用，導致每次變更都必須改動核心程式碼。

**Solution**:  
採用「策略模式 (Strategy) + 介面抽象」來隔離規則。  
ChatGPT 產生的關鍵程式設計如下，示範如何抽象化折扣計算：

```csharp
public interface IRetailDiscountCalculator
{
    CalculationResult CalculateDiscount(decimal originalPrice);
}

public class CalculationResult
{
    public decimal FinalPrice { get; set; }
    public List<Discount> AppliedDiscounts { get; set; }
    public List<string> DiscountHints { get; set; }
}

public class Discount
{
    public string Name  { get; set; }
    public decimal Amount { get; set; }
}
```

關鍵思考點：  
• 以 `interface` 隔離演算法，新規則只須實作 `IRetailDiscountCalculator` 即可插拔。  
• `CalculationResult` 同時回傳「最終金額、已套用折扣、尚未滿足提示」，滿足收據與 UX 所需資訊。  

**Cases 1**:  
– 利用 ChatGPT 在「3 句需求」下快速產生上述介面與樣板程式，開發者僅花數分鐘即可完成 PoC，省去半天設計會議。  

**Cases 2**:  
– 同一專案於半年內新增 8 種行銷活動，僅新增 8 個 class，核心結算流程零改動；迴歸測試腳本重用率 95%。  


## Problem: Interface 只能處理單一商品，無法支援「整台購物車」

**Problem**:  
初版介面 `CalculateDiscount(decimal originalPrice)` 侷限於單商品折扣，當需求擴大到「整批購物車」時，必須一次處理多品項的組合優惠與滿額活動。

**Root Cause**:  
初始抽象層級判斷失誤，只考慮到「價格」而非「交易集合」。導致後續要納入商品清單時，必須重構方法簽章。

**Solution**:  
重新抽象化 Input 型別，改用商品集合：

```csharp
public interface ICartDiscountCalculator
{
    CartCalculationResult CalculateDiscount(List<CartItem> cartItems);
}
```

關鍵思考點：  
• 把最小單位提升為 `CartItem` 列表，使演算法可以同時考慮跨品項邏輯。  
• `CartCalculationResult` 延續先前回傳模式，兼具彈性與相容性。  

**Cases**:  
– 重構後，行銷部門新增「滿額折 100」與「任 3 件 88 折」，開發者只需各自實作 2 個規則類別，整併測試一次通過，花費時間 < 1 人日。  


## Problem: 折扣需考慮「優惠券」才能生效，介面缺少上下文

**Problem**:  
當折扣計算需要考慮「顧客所持有之優惠券」才能判定是否符合條件，目前介面無法輸入 Coupon 資訊。

**Root Cause**:  
介面只考量商品與價格，忽略「與顧客相關的額外上下文 (Coupon / Member Level / Campaign Code)」，導致無法套用「觸發式」折扣。

**Solution**:  
在介面層提升為支援額外上下文，並區分「有券」與「無券」計算：

```csharp
public interface IDiscountCalculator
{
    decimal CalculateDiscountedPrice(
        List<Product> products, 
        decimal totalPrice, 
        out List<Discount> discounts);
    
    decimal CalculateDiscountedPriceWithCoupon(
        List<Product> products, 
        decimal totalPrice, 
        Coupon coupon, 
        out List<Discount> discounts);
}
```

關鍵思考點：  
• 以多載 (overload) 或不同方法名稱清楚區分「需要 Coupon」之場景。  
• 使用 `out` / 回傳 Touple 明示「折扣清單」為輸出，保持介面語意清晰。  

**Cases**:  
– 導入後，行銷可在後台自行建立「限量折 50 元 Coupon」活動，前端僅需將券號帶入 API，即可完成對接；行銷活動上線時間由一週縮短為 1 天。  


## Problem: 人類與 AI 的協作效率 — 如何確保 AI 產出的設計可被掌握

**Problem**:  
AI (如 ChatGPT) 已能快速產生設計與程式碼，但若開發者缺乏「抽象化思考能力」，無法判斷 AI 方案好壞或進一步引導修正，AI 帶來的效率將大打折扣。

**Root Cause**:  
1. 教育與工作習慣長期偏重「實作技能 (Skill)」，忽視「為何 (Why) / 抽象化 (Spec)」。  
2. 面對 AI，若只停留在 copy-paste 程式碼層次，無法形成高層次的系統設計與規格。  

**Solution**:  
• 透過「刻意練習 (Deliberate Practice)」安排抽象化題目（如折扣引擎、生命遊戲等），訓練把需求轉成 Interface / API / Contract 的能力。  
• 在實際開發流程導入「API First & Spec-Driven」工作法：  
  – 先寫 OpenAPI / Interface Spec → 再交由 AI 產生 Code + Test → 人只需做高層 Review 與調整。  
• 將 AI 定位為「POC 與程式產生器」，人類負責「定義規格、判斷品質、跨系統協作」。  

**Cases 1**:  
– 使用上述流程，團隊在兩週內完成一支原預估需 5 週的結帳微服務；80% 代碼由 ChatGPT + Copilot 生成，開發者專注在 API 與例外流程。  

**Cases 2**:  
– 團隊每週安排一次「抽象化 Kata」，指定成員用自然語言撰寫需求，再由 ChatGPT 產生初稿，組內做 Code Review；三個月後，新人能在一天內寫出符合公司標準的 API Spec，效率提升 3 倍。  