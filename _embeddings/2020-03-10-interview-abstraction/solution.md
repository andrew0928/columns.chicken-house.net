# 折扣機制抽象化設計案例

# 問題／解決方案 (Problem/Solution)

## Problem: 同一家 POS / 電商平台要面對五花八門的折扣，程式碼愈寫愈亂

**Problem**:  
• 實體零售或電商在促銷期間會同時推出「第二件六折」、「滿六件折 100」、「買一送一」、「任兩箱 88 折」…等多種折扣。  
• 現場結帳 (POS) 或線上結帳 (Shopping Cart) 必須一次計算所有折扣後才知道最終應付金額。  
• 多數開發人員第一時間以「歸納 + `if / else` + 大量 flag」硬寫。規則一多程式碼難維護，也很難應付下一波未知折扣。

**Root Cause**:  
1. 結帳核心程式與「折扣計算細節」耦合，同一支 `Checkout` 函式充滿 switch / if。  
2. 缺乏「抽象化介面」去隔離──當新規則出現時只好進結帳主程式改碼。  
3. 折扣間互斥 (排除) 或跨商品配對根本沒有統一契約可遵循，只能硬塞處理旗標，日後一定失控。

**Solution**:  
抽象出一條「折扣規則工作流」並固定其介面。核心做法如下：

1. 定義 Domain Entity  
   ```csharp
   public class Product {
       public int Id;
       public string SKU;
       public string Name;
       public decimal Price;
       public HashSet<string> Tags;      // 關鍵：標籤描述屬性或促銷身份
   }
   ```

2. 定義抽象折扣規則 (RuleBase)  
   ```csharp
   public abstract class RuleBase {
       public string Name, Note;
       public string ExclusiveTag = null;                 // (進階) 互斥用
       public abstract IEnumerable<Discount> Process(CartContext cart);
   }
   ```

3. 定義結帳上下文 (CartContext) 與 POS Pipeline  
   ```csharp
   public class CartContext {
       public readonly List<Product> PurchasedItems = new();
       public readonly List<Discount> AppliedDiscounts = new();
       public IEnumerable<Product> GetVisiblePurchasedItems(string exTag)
           => string.IsNullOrEmpty(exTag)
                 ? PurchasedItems
                 : PurchasedItems.Where(p => !p.Tags.Contains(exTag));
       public decimal TotalPrice;
   }

   public class POS {
       public readonly List<RuleBase> ActivedRules = new();
       public void Checkout(CartContext cart) {
           cart.TotalPrice = cart.PurchasedItems.Sum(p => p.Price);
           foreach (var r in ActivedRules) {
               var d = r.Process(cart);
               cart.AppliedDiscounts.AddRange(d);
               cart.TotalPrice -= d.Sum(x => x.Amount);
               // 若為互斥折扣，標記排除標籤
               if (r.ExclusiveTag != null)
                   foreach (var dis in d)
                       foreach (var p in dis.Products)
                           p.Tags.Add(r.ExclusiveTag);
           }
       }
   }
   ```

4. 實作任意規則＝繼承 `RuleBase`  
   範例：「任 2 箱 88 折」  
   ```csharp
   class Buy2Boxes88Rule : RuleBase {
       public Buy2Boxes88Rule() { Name="任二箱 88折"; }
       public override IEnumerable<Discount> Process(CartContext cart) {
           var list = cart.GetVisiblePurchasedItems(ExclusiveTag)
                          .Where(p => p.Tags.Contains("熱銷飲品"))
                          .OrderByDescending(p => p.Price).ToList();
           for(int i=0;i+1<list.Count;i+=2){
               var two=list.Skip(i).Take(2).ToArray();
               yield return new Discount{
                    Rule=this, Products=two,
                    Amount= two.Sum(p=>p.Price)*0.12m };
           }
       }
   }
   ```
   新折扣僅需增加類別並 `pos.ActivedRules.Add(new …)` ，Checkout 本身 0 修改，靠多型自動串起。

**Cases 1**:  
一次啟用 6 條規則（滿件折 100、第二件 5 折、加 10 元多 1 件、餐餐超值配、任兩箱 88 折、滿千折百），同一筆訂單 18 項商品計算結果：
• 原價：$2,445.00  
• 自動比對後折抵：$515.50  
• 最終應付：$1,929.50  
全程不改 `POS.Checkout` 中任何一行。

**Cases 2 – 新增「餐餐超值配」配對優惠**  
只新增 `ComboRule` 類別 + 資料表列出 (飲料Tag, 鮮食Tag, 組合價)，Checkout 立即能處理 39/49/59 與跨區 49+59、59+49 組合。四筆商品心算應付 $118，系統輸出同值，驗證正確。

**Cases 3 – 折扣排除**  
老闆要求「衛生紙滿 6 件折 100」與「同商品加 10 元多 1 件」互斥。  
做法：只在兩條 Rule 建構時指定 `ExclusiveTag = "ex"`。系統自動標籤排除，結帳金額由 $2,187.50 → $2,327.50，符合期望，全程不碰其他程式碼。

## Problem: 新增「配對折扣」與「折扣互斥」時，框架本身必須跟着改動

**Problem**:  
抽象化第一版搞定單品 / 滿件 / 打折，但當要商務「鮮食+飲料組合價」或「A 折扣中到就不得再享 B」時，原框架需要再修改 Process 流程，否則規則間打架。

**Root Cause**:  
1. 原抽象只考慮「一條規則＝純粹掃描購物車計算」；忽略了「規則之間互斥」與「多品項配對」的橫向溝通需求。  
2. 缺少「在商品上留下運算中間狀態」的通道，導致規則無法得知前序規則的處置結果。

**Solution**:  
在不破壞既有 API 的前提下，最小增量調整：

1. 於 `RuleBase` 增加 `ExclusiveTag` 欄位：若不為 null，代表本規則屬互斥族群。  
2. 於 `POS.Checkout()` 結束每條規則後，將該規則已折抵的商品貼上 `ExclusiveTag`。  
3. 於 `CartContext.GetVisiblePurchasedItems(tag)` 統一過濾；任何規則若帶入自己的 `ExclusiveTag`，即可輕鬆取得「尚可折扣」商品。  
4. 用「標籤策略」解決所有配對需求。配對條件只要寫成 `(tagA, tagB, price)` 表格；跨區 49+59 只需再列一筆。`ComboRule` 讀表即可配對。  

關鍵思考：  
• 「貼標籤」= 留中繼狀態。規則之間靠標籤溝通而非直接呼叫 → 仍符合「規則間解耦」。  
• 對 Checkout 來說只多兩行：「呼叫 rule.Process」與「把折扣商品貼 tag」，流程仍單一出口。  
• 未動到之前任何折扣程式碼，保證向下相容。

**Cases 1: 配對＋排除同時存在**  
測試檔 products4.json  
– 8 串衛生紙 (滿 6 折 100)  
– 5 串氣泡水 (第二件 10 元)  
設定兩條規則同屬 `ex` 互斥。  
系統輸出：只套用前一條滿件折扣 100，氣泡水僅剩 1 組 second-10 折，金額由 2,187.50 調為 2,327.50。

**Cases 2: 讀者 PR 多版本驗證**  
4 份 Pull Requests 以不同實作（Proxy、Queue、Enum flag…）插入同一 Checkout pipeline；皆能計算正確。再次證明介面抓得好，多型威力大，外部團隊可相容擴充。

## Problem: 每次加規則就得重編／重發，部署費時

**Problem**:  
行銷人員隨時要加新活動；若每次都要請 RD 編譯佈署，時效慢＋成本高。

**Root Cause**:  
折扣邏輯寫死在 DLL，無法動態載入；Rule 建構子參數也不支援從外部資料來源 (DB / JSON) 注入。

**Solution**:  
1. 將 `RuleBase` 子類兩種資料切分：  
   • 不會變的計算邏輯 ⇒ 留在程式。  
   • 常變的門檻 / 折扣額 / Tag 組合 ⇒ 改用 DB / JSON 配置，啟動時透過 `Activator.CreateInstance()`＋ DI 反射生成。  
2. Checkout 流程不動，達到「只改資料，不改程式」。  

**Cases**:  
• Marketing 透過後台新增「#咖啡 全品項第二件 7 折」；系統只寫入一筆規則資料，服務熱載成功，門市立即可賣，無須重新部署。  

---

以上三組問題與解決方案，展示了「抽象化介面 + OOP 多型 + 商品標籤」如何把看似無窮無盡的折扣機制，收斂成：

1. Checkout 主流程永遠只有 *一條*。  
2. 新規則＝新增 class 或新增資料，不修改舊程式。  
3. 互斥、配對、跨區、加價升級… 均以最少程式碼擴充。  

這就是「隱藏細節、提取重點」的抽象化威力。