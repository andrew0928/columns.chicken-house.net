---
layout: synthesis
title: "Generic Type 的繼承..."
synthesis_type: faq
source_post: /2007/02/12/generic-type-inheritance/
redirect_from:
  - /2007/02/12/generic-type-inheritance/faq/
postid: 2007-02-12-generic-type-inheritance
---

# Generic Type 的繼承與 ASP.NET UserControl 的應用 FAQ

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

Q1: 什麼是 .NET 的泛型（Generic Type）？
- A簡: 泛型讓型別參數化，於編譯期保證型別安全，避免轉型與裝箱。
- A詳: 泛型是將型別作為參數傳入類別、方法、介面或委派的一種語言機制。以 List<T>、Dictionary<TKey,TValue> 為例，T/TKey/TValue 在使用時才被具體化。其優點包含：編譯期型別檢查、減少轉型與裝箱成本、改善 API 可讀性與重用性。本文用 Editor<T> 展示在 WebForms UserControl 上的應用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q6, B-Q3

Q2: 什麼是泛型基底類別（Generic Base Class）？
- A簡: 指以型別參數定義的父類別，子類可指定型別實參繼承。
- A詳: 泛型基底類別是以型別參數定義的抽象或具體父類別，例如 Editor<T>。衍生時可指定具體型別參數（如 DateEditor : Editor<DateTime>），讓子類獲得強型別能力與共通行為。此設計將共通邏輯上移，子類專注具體型別差異。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q1, B-Q3

Q3: 為何要在 ASP.NET UserControl 中使用泛型？
- A簡: 取得強型別 Value 屬性，統一共通功能並避免醜陋轉型。
- A詳: UserControl 經常需要讀寫不同型別資料。若以 object 表示 Value，將充斥轉型與易錯邏輯。改用 Editor<T>，Value 直接是 T，編譯期檢查、IDE 支援更佳。更重要的是，所有編輯器共享基底，容易集中實作事件、快取、持久化、驗證與統一行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q4

Q4: 在繼承時指定型別參數後，子類別是否仍是泛型？
- A簡: 否。指定後成為關閉式型別，子類本身不再是泛型。
- A詳: 當以 DateEditor : Editor<DateTime> 繼承時，Editor<T> 的 T 被具體化為 DateTime，DateEditor 已是關閉式（closed）型別，本身不再具型別參數。好處是可在標記中直接使用 DateEditor，並具備完整的強型別屬性與行為。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q3

Q5: Editor<T> 的核心價值是什麼？
- A簡: 抽象出共通行為，提供強型別 Value 與可重用基礎。
- A詳: Editor<T> 作為所有編輯器的共同基底，定義抽象 Value 屬性與跨型別共通能力（事件、驗證、狀態保存、樣式規範）。它讓 DateEditor、BoolEditor…等僅關注其 UI 與 T 的轉換，用少量子類程式碼套用大量父類別的既有能力。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4, B-Q5

Q6: 使用 object 作為 Value 與使用泛型的差異是什麼？
- A簡: object 需轉型且易出錯；泛型強型別、可讀性與效能較佳。
- A詳: Value: object 雖通用，但每次取用需轉型，產生轉型例外風險與裝箱成本，也讓 API 不清晰。使用 Editor<T> 的 Value:T，能編譯期檢查、IDE 智慧提示、避免裝箱解除裝箱，並讓錯誤更早被發現，維護性與效能更好。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q3, B-Q10

Q7: 何謂強型別（Strongly-Typed）Value 屬性？
- A簡: 屬性型別即為資料型別，無需轉型，編譯期保證正確。
- A詳: 強型別 Value 指 Editor<T>.Value 直接是 T（如 DateTime），呼叫者無需轉型。IDE 能提供成員提示，錯誤在編譯期即被發現，比 object 更安全。這特質在設計大型可重用控制項時特別重要。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q10

Q8: 為什麼要讓不同型別編輯器共用同一基底類別？
- A簡: 集中共用功能、簡化維護、支援多型與反射自動化。
- A詳: 共用基底使功能只需實作一次：統一事件（OnChange）、狀態持久化（記住上次值）、驗證與樣式。也為反射與屬性驅動的表單生成鋪路，透過多型呼叫統一 API，減少重複程式碼與風險。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, B-Q6

Q9: 何謂多型（Polymorphism）在此案例中的角色？
- A簡: 以共同基底抽象操作，對不同子類以相同方式呼叫。
- A詳: 多型允許以 Editor<T> 的共同介面處理 DateEditor、BoolEditor 等實例，呼叫 Value、訂閱事件時無需關心具體型別。配合反射生成表單，可用同一流程收集值並回寫物件，實現真正的「一次實作，到處使用」。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q9, C-Q5

Q10: 什麼是「開放式」與「關閉式」泛型？
- A簡: 開放式未指定型別參數；關閉式已具體化為具體型別。
- A詳: Editor<T> 是開放式（open）泛型；DateEditor : Editor<DateTime> 是關閉式（closed）泛型。只有關閉式型別可實例化或供標記使用。理解兩者有助於正確繼承與註冊控制項。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q3

Q11: 泛型與 Singleton 模式如何結合？
- A簡: 以泛型基底封裝單例邏輯，子類指定自身型別繼承。
- A詳: 可設計 Singleton<T>，限制 T 有無參數建構，並在基底管理單例實例。子類以 FooManager : Singleton<FooManager> 使用。與 Editor<T> 類似，都是以泛型基底抽出共用機制並於子類具體化。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q15

Q12: 使用泛型基底對重用性與維護性有何影響？
- A簡: 大幅提升重用，集中維護點，降低功能碎片化風險。
- A詳: 基底集中行為（事件、驗證、持久化、記錄），子類只關注呈現與轉換。變更一處，所有編輯器受益，降低不一致與回歸風險。對大型專案尤其有利，能建立長期可演進的控制項庫。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q8, B-Q4, B-Q5

Q13: ASP.NET 控制項屬性的宣告型別如何影響標記綁定？
- A簡: 屬性型別決定標記值的型別轉換與序列化行為。
- A詳: 在 WebForms，標記中的屬性字串會透過 TypeConverter 或解析器轉為屬性宣告型別。例如 Value: DateTime，標記需可被轉為 DateTime。正確宣告型別可享框架自動轉換與設計時支援；否則需自訂 Converter。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q11, C-Q8, D-Q2

Q14: 泛型基底與介面（IValueEditor<T>）的差異？
- A簡: 基底可內建行為；介面僅約束契約，需重複實作。
- A詳: 介面提供最小契約（如 Value get/set），但共通能力（事件、持久化、驗證）需各子類重複實作。泛型基底可直接提供這些行為並允許覆寫，降低重複。若需多重實作或現有繼承限制，介面更靈活。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, B-Q6

Q15: 什麼情境不適合使用泛型基底編輯器？
- A簡: 型別很少、需求單一或設計限制無法共同繼承時。
- A詳: 若僅少數控制項、重用價值低、或控制項框架/設計器不支援泛型繼承，導入成本可能高於收益。此外，若需要多個不同基底或跨框架（非 WebForms），改用介面或組合模式可能更合適。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q16

Q16: 為何示例看似平凡，卻能大幅提升價值？
- A簡: 基底抽象讓一次投資擴散至所有子編輯器。
- A詳: 看似只多了個 Editor<T>，但它建立了可延展的地基：事件、狀態、驗證、樣式、記錄、追蹤等皆可集中實作並立即下放。後續新增型別編輯器幾乎零摩擦，對長期演進與維護極為有利。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, A-Q12, B-Q4

### Q&A 類別 B: 技術原理類

Q1: Editor<T> 基底類別如何運作？
- A簡: 以抽象 Value 屬性定義契約，承載共通事件與行為。
- A詳: 原理說明：Editor<T> 以 UserControl 為基底，宣告 abstract T Value {get;set;}，並可內建事件（OnChange）、驗證、持久化。流程：子類在 setter/getter 與 UI 控制項做轉換；基底攔截 set 觸發事件與紀錄。核心組件：UserControl、抽象 Value、事件、可選存取器與輔助服務。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q5, B-Q4, C-Q1

Q2: DateEditor : Editor<DateTime> 的執行流程為何？
- A簡: UI 與 Value 映射；操作日曆更新 Value，事件隨之觸發。
- A詳: 原理：DateEditor 於 getter 讀 Calendar.SelectedDate，setter 寫入並可 Raise OnChange。關鍵步驟：初始化 UI、同步 Value 與 UI、處理 UI 事件更新 Value、呼叫基底的事件或持久化。組件：Calendar、DateEditor、Editor<T> 事件管線。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q2, B-Q4

Q3: CLR 中泛型封閉與繼承的規則是什麼？
- A簡: 開放式不可實體化；關閉式可用；子類繼承需具體化。
- A詳: 原理：開放式類型僅為型別定義，不能建立實例或出現在執行實例成員上。流程：宣告 Editor<T>、衍生以 Editor<DateTime>，產生封閉型別 DateEditor；編譯器與 CLR 為每個關閉型別生成對應中繼資料。組件：型別系統、JIT、執行期型別引擎。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q4, A-Q10

Q4: 共用 OnChange 事件的設計機制是什麼？
- A簡: 基底宣告事件，子類於值變更時 Raise，統一處理。
- A詳: 原理：在 Editor<T> 宣告 event EventHandler<ValueChangedEventArgs<T>> Changed。流程：子類於 setter 或 UI 事件時呼叫 RaiseChanged(old,new)。核心組件：事件委派、引數類別、基底 Raise 方法。此模式解耦 UI 與頁面邏輯，所有編輯器一致行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q3, A-Q8

B5: 「記住上次輸入」功能背後機制是什麼？
- A簡: 在 set 時寫入存儲，於初始化時讀回還原 Value。
- A詳: 原理：攔截 Value 設定點，將值序列化存入檔案/DB/快取；載入控制項時嘗試讀回預設值。流程：Key 設計（使用者+欄位識別）、序列化、存取層、異常處理與過期策略。組件：序列化器、儲存服務介面、Editor<T> 勾點。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q4, A-Q12

Q6: 反射與屬性動態產生編輯畫面的原理是什麼？
- A簡: 反射讀型別成員，按型別映射建立對應 Editor<T>。
- A詳: 原理：用反射取得目標物件的屬性/欄位、型別、特性（Attribute）；依映射表決定用哪個編輯器（如 int→IntEditor）。流程：遍歷成員→建立控制項→設初值→加入容器→綁定事件。組件：反射 API、型別映射字典、控制項工廠。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q6, A-Q9

Q7: 類型到編輯器的映射策略如何設計？
- A簡: 以字典或屬性標註對應，支援覆寫與自訂擴充。
- A詳: 原理：建立 Dictionary<Type, Type> 或以 Attribute 指定 Editor 類型。流程：先查特性→再查字典→fallback 規則（如 nullable/集合）。組件：映射表、工廠方法（Activator/DI）、快取。設計需考慮複雜型別與可擴充性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q7

Q8: 在頁面生命週期中如何正確載入動態編輯器？
- A簡: 於 OnInit 建立控制項並保留順序，確保 ViewState。
- A詳: 原理：WebForms 需於 Init 前建立相同控制項樹，否則 ViewState 與事件遺失。流程：OnInit 建立→設定 ID→加入容器→資料綁定於 Load/PreRender→回傳時重建相同樹。組件：Page lifecycle、ViewState、Control ID 管理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q3, C-Q5

Q9: 泛型基底類別與多型方法呼叫的關係？
- A簡: 以基底參考統一存取子類行為，實現多型分派。
- A詳: 原理：Page 以 Editor<?> 集合迭代，透過共同介面取值、綁事件。流程：建立集合→逐一呼叫 Value、Subscribed Changed→彙總結果。組件：虛擬/抽象成員、多型分派、集合結構。這是表單自動化的技術核心。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, C-Q6

Q10: 強型別 Value 對型別安全與效能有何影響？
- A簡: 消除轉型與裝箱，降低錯誤率並提升效能。
- A詳: 原理：以 T 直接操作，CLR 不需裝箱/拆箱，少了不必要的轉型與反射。流程：讀/寫 Value→直接 IL 呼叫→JIT 最佳化。組件：JIT、型別系統、泛型實作。對高頻存取的編輯器特別有益。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, A-Q7

Q11: 在標記中 value="2000/01/01" 如何轉為 DateTime？
- A簡: WebForms 以 TypeConverter 將字串轉為屬性型別。
- A詳: 原理：解析標記屬性字串，尋找目標型別的 TypeConverter 或 Parse 方法。流程：取得屬性型別→呼叫 Converter.ConvertFrom→指派屬性。組件：TypeConverter、CultureInfo、設計階段序列化。文化設定不一致會造成轉換錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: D-Q2, C-Q8

Q12: 泛型基底如何與依賴注入（DI）整合？
- A簡: 基底定義服務介面，子類或頁面由容器注入實作。
- A詳: 原理：Editor<T> 依賴抽象服務（儲存、驗證、記錄），由 DI 容器在建立控制項時注入。流程：註冊服務→建立編輯器→容器注入→使用服務。組件：介面、DI 容器、工廠。可降低耦合並提升測試性。
- 難度: 高級
- 學習階段: 進階
- 關聯概念: C-Q4, C-Q9

Q13: 用 Attribute 控制外觀與驗證的機制？
- A簡: 成員加標註，表單生成時據以設定編輯器。
- A詳: 原理：定義如 [Editor(typeof(...))]、[Display(Name=...)]、[Required]。流程：反射讀取屬性→根據標註選擇編輯器、標題、必要性與範圍→套用驗證規則。組件：自訂 Attribute、反射、驗證服務。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: C-Q5, C-Q6

Q14: Generic constraints 在此設計中的用途與限制？
- A簡: 可限制 T（如 struct）但多為 UI 編輯器非必要。
- A詳: 原理：where T: struct/class/new() 可限制可用型別。流程：宣告 Editor<T> 時加入條件→編譯期檢查。組件：泛型約束、編譯器。多數編輯器場景用不到，但若需確保可建立預設值或值型別，可適度使用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10

Q15: 與 Singleton 模式結合時的運作原理？
- A簡: 泛型基底封裝單例取用，子類僅繼承即可使用。
- A詳: 原理：Singleton<T> 持有靜態 Lazy<T>，確保執行緒安全初始化。流程：子類 Singleton<Foo>.Instance 取得唯一實例。組件：靜態欄位、Lazy、泛型。與 Editor<T> 同理，皆以泛型封裝共同行為。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q11

Q16: 編輯器集合的管理與組合（Composite）如何設計？
- A簡: 以容器管理多個 Editor，統一遍歷與彙整。
- A詳: 原理：建立 EditorContainer 管理子編輯器集合，提供 Validate、CollectValues 等操作。流程：新增/移除編輯器→統一驗證→輸出模型。組件：容器控制項、集合、迭代。利於大型表單模組化與重用。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q5, C-Q6, D-Q9

### Q&A 類別 C: 實作應用類（10題）

Q1: 如何實作 Editor<T> 基底類別？
- A簡: 繼承 UserControl，宣告抽象 Value 與共用事件。
- A詳: 步驟：
  - 建立 public abstract class Editor<T> : UserControl
  - 宣告 public abstract T Value {get;set;}
  - 加入事件與共用功能
  代碼：
  ```csharp
  public abstract class Editor<T> : UserControl {
    public event EventHandler<ValueChangedEventArgs<T>> Changed;
    protected void RaiseChanged(T oldV, T newV) =>
      Changed?.Invoke(this, new ValueChangedEventArgs<T>(oldV, newV));
    public abstract T Value { get; set; }
  }
  public sealed class ValueChangedEventArgs<T> : EventArgs {
    public T OldValue { get; } public T NewValue { get; }
    public ValueChangedEventArgs(T o,T n){OldValue=o;NewValue=n;}
  }
  ```
  注意：保持抽象最小，避免過早綁死 UI 細節。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q1, B-Q4

Q2: 如何建立 DateEditor 並與 Calendar 綁定？
- A簡: 建立 DateEditor : Editor<DateTime>，映射 SelectedDate。
- A詳: 步驟：
  - 建立 DateEditor.ascx 與 Calendar 控制項
  - 在 code-behind 覆寫 Value
  代碼：
  ```aspx
  <%@ Control Language="C#" Inherits="DateEditor" %>
  <asp:Calendar runat="server" ID="cal" />
  ```
  ```csharp
  public class DateEditor : Editor<DateTime> {
    public override DateTime Value {
      get => cal.SelectedDate;
      set { var old = cal.SelectedDate; cal.SelectedDate = value; RaiseChanged(old, value); }
    }
  }
  ```
  注意：處理 SelectedDate 預設值與文化格式。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, D-Q8

Q3: 如何在 Editor<T> 加入並觸發 OnChange 事件？
- A簡: 基底定義事件，子類在 UI 改變時呼叫 RaiseChanged。
- A詳: 步驟：
  - 在 Editor<T> 宣告 Changed 事件與 RaiseChanged
  - 子類在 setter 或 UI 事件（TextChanged/SelectionChanged）呼叫 RaiseChanged
  代碼：
  ```csharp
  protected void cal_SelectionChanged(object s, EventArgs e) {
    var old = Value; Value = cal.SelectedDate; // setter 內 RaiseChanged
  }
  ```
  注意：避免重複 Raise；可於 setter 比對值是否變更。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q5

Q4: 如何實作「記住上次輸入」功能？
- A簡: 設定時保存值，載入時讀取預設值還原。
- A詳: 步驟：
  - 設計 IValueStore 介面與具體實作（File/DB）
  - 在基底於 setter/OnLoad 呼叫儲存/讀取
  代碼：
  ```csharp
  public interface IValueStore { bool TryGet(string k,out string v); void Set(string k,string v); }
  protected virtual string Key => $"{Context.User.Identity.Name}:{UniqueID}";
  protected IValueStore Store { get; set; }
  protected override void OnLoad(EventArgs e){
    base.OnLoad(e);
    if(!IsPostBack && Store?.TryGet(Key,out var s)==true) Value = (T)TypeDescriptor.GetConverter(typeof(T)).ConvertFromString(s);
  }
  public override T Value { get => GetValue(); set { var old=GetValue(); SetValue(value); Store?.Set(Key, TypeDescriptor.GetConverter(typeof(T)).ConvertToInvariantString(value)); RaiseChanged(old,value);} }
  ```
  注意：考慮序列化、文化、隱私與過期政策。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q6

Q5: 如何用反射為物件動態產生編輯表單？
- A簡: 反射屬性→依映射產生 Editor<T>→設定初值→加入容器。
- A詳: 步驟：
  - 建立 Type→Editor 類型映射或使用 Attribute
  - 於 OnInit 迭代屬性建立控制項
  - 設定 ID 與初值，加入 PlaceHolder
  代碼：
  ```csharp
  var props = model.GetType().GetProperties();
  foreach (var p in props){
    var edType = map.Resolve(p.PropertyType, p); // 自訂
    var ed = (Control)LoadControl(edType, null);
    ed.ID = $"ed_{p.Name}";
    ((dynamic)ed).Value = p.GetValue(model);
    placeholder.Controls.Add(ed);
  }
  ```
  注意：於 OnInit 建立，確保 ViewState；處理 Nullable/集合。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q8

Q6: 如何將編輯器值回寫到物件實例？
- A簡: 遍歷編輯器集合，按屬性名取值並賦回模型。
- A詳: 步驟：
  - 於提交時迭代 PlaceHolder 中的 Editor 控制項
  - 以命名規則或映射找到對應屬性
  - 將 Value 指派回模型
  代碼：
  ```csharp
  foreach (var p in model.GetType().GetProperties()){
    var ed = placeholder.FindControl($"ed_{p.Name}") as Control;
    if (ed is null) continue;
    var val = ((dynamic)ed).Value;
    p.SetValue(model, val);
  }
  ```
  注意：處理驗證失敗、型別轉換與例外保護。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q9, D-Q4

Q7: 如何為複雜型別（如 MemberInfo）自訂 Editor？
- A簡: 設計專屬 UI 與選取邏輯，實作 Value 的序列化。
- A詳: 步驟：
  - 規劃查詢/選取 UI（搜尋、清單）
  - 以穩定鍵（ID/Name）保存，轉換為型別實例
  - 覆寫 Value get/set 與事件 Raise
  代碼（概念）：
  ```csharp
  public class MemberEditor : Editor<MemberInfo> {
    public override MemberInfo Value { get { return _svc.GetById(hfId.Value); } set { hfId.Value = value?.Id; RaiseChanged(null, value); } }
  }
  ```
  注意：避免在 getter 中做昂貴查詢；可快取。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q7, C-Q9

Q8: 如何在標記中使用自訂編輯器並傳入初值？
- A簡: 註冊控制項，於標記設定屬性，靠 TypeConverter 轉換。
- A詳: 步驟：
  - 在頁面頂端註冊
  ```aspx
  <%@ Register Src="~/Controls/DateEditor.ascx" TagPrefix="ch" TagName="DateEditor" %>
  ```
  - 在標記使用
  ```aspx
  <ch:DateEditor runat="server" ID="de" Value="2000/01/01" />
  ```
  注意：Value 型別與格式需可轉換；文化設定一致；複雜型別需自訂轉換器。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, D-Q2

Q9: 如何封裝編輯器庫以便重用與發佈？
- A簡: 萃取共用專案、標準化 API，搭配 NuGet/元件包裝。
- A詳: 步驟：
  - 將 Editor<T> 與子類放入 Class Library + 控制項資源
  - 定義清楚命名、事件、驗證與擴充點
  - 撰寫說明與範例，建立 NuGet 套件或內部包
  注意：維護版本相容性、嚴格語意版本、API 穩定與設計文件。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q16, D-Q10

Q10: 如何撰寫單元測試驗證 Editor<T> 的 Value 與事件？
- A簡: 模擬 UI 互動，斷言 Value 與 Changed 事件正確。
- A詳: 步驟：
  - 建立子類測試替身（可注入假儲存/驗證）
  - 設定 Value 觸發事件，捕捉引數比對舊新值
  - 模擬 UI 事件，驗證 setter 與 Raise 行為
  代碼（片段）：
  ```csharp
  var ed = new DateEditor(); bool raised=false;
  ed.Changed += (s,e)=> { raised=true; Assert.Equal(old,e.OldValue); };
  ed.Value = DateTime.Today;
  Assert.True(raised);
  ```
  注意：對 WebForms 可用 Page 测试工具或多用分離邏輯以便測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q4, C-Q1

### Q&A 類別 D: 問題解決類（10題）

Q1: 以泛型為基底的 UserControl 無法在設計階段載入怎麼辦？
- A簡: 使用關閉式子類註冊至標記，避免直接引用開放式泛型。
- A詳: 症狀：設計器/工具箱無法顯示或拋例外。原因：設計器不支援開放式泛型。解法：建立具體子類（如 DateEditor : Editor<DateTime>），在 .ascx 或 @Register 使用子類；必要時提供設計時 Dummy。預防：避免將開放泛型直接用於標記或設計器。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q3

Q2: 標記設定 Value="2000/01/01" 出現格式/轉換錯誤？
- A簡: 確認文化設定與 TypeConverter，必要時自訂轉換。
- A詳: 症狀：初始化時 Format/Convert 例外。原因：文化差異、格式不符、缺少轉換器。解法：統一 CultureInfo、使用不變文化格式、為複雜型別實作 TypeConverter；或改於程式設定 Value。預防：文件標示可接受格式，於控件內保護性解析。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q11, C-Q8

Q3: 動態新增編輯器後回傳事件不觸發或 ViewState 遺失？
- A簡: 在 OnInit 建立控制項並固定 ID 與順序。
- A詳: 症狀：PostBack 後值/事件不見。原因：生命週期時機錯誤、ID 變動。解法：於 OnInit 重建相同控制樹；設定穩定 ID；於 Load/PreRender 再做資料同步。預防：將生成邏輯集中於 Init；撰寫測試覆蓋回傳。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q8, C-Q5

Q4: 反射產生表單時找不到對應編輯器怎麼辦？
- A簡: 建立健全型別映射與預設策略，支援覆寫。
- A詳: 症狀：某些屬性無法呈現。原因：映射表缺漏、複雜型別未支援。解法：提供預設 Editor（如文字）或 [Editor] Attribute 指定；擴充映射處理 Nullable、Enum、集合。預防：為常見型別建立單元測試與覆蓋報告。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5

Q5: OnChange 事件未觸發或觸發兩次如何處理？
- A簡: 於 setter 比對舊新值，統一由一處 RaiseChanged。
- A詳: 症狀：事件未響應或重複。原因：UI 事件與 setter 重複 Raise、或未在正確處 Raise。解法：將 Raise 放於 setter 並比對值改變；UI 事件只設定 Value。預防：撰寫事件流測試，避免在多處 Raise。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: C-Q3, B-Q4

Q6: 「記住上次輸入」保存或讀取失敗怎麼辦？
- A簡: 檢查 Key、序列化、存儲權限與錯誤處理。
- A詳: 症狀：值未還原或寫入失敗。原因：Key 不穩定（ID 變動）、序列化錯誤、存儲無權限或策略不當。解法：用穩定 Key（User+Control Path）、統一 Converter、加入重試/降級。預防：加遷移測試與監控，記錄例外。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q4

Q7: Nullable、Enum 或集合型別編輯錯誤如何處理？
- A簡: 提供特殊 Editor，或在映射實作泛用處理。
- A詳: 症狀：無法設定 null、枚舉顯示錯亂、集合無編輯器。原因：未處理 Nullable<T>、Enum 名稱/值轉換、集合 UI 複雜。解法：為 Nullable 提供清除選項；Enum 使用 DropDownList 並轉換；集合提供子表格或多選 UI。預防：映射層有專門規則。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, C-Q5

Q8: 子控制項為 null 或 SelectedDate 未設定拋例外？
- A簡: 檢查控制項生命週期與預設值防護。
- A詳: 症狀：NullReference 或未初始化值。原因：存取時機錯誤、UI 預設值未設定。解法：於 OnInit/OnLoad 確保子控制項已建立；在 getter/setter 加入空值與預設處理。預防：初始化守則與單元測試覆蓋。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q2, C-Q2

Q9: 大量反射與控制項導致效能不佳怎麼優化？
- A簡: 快取反射結果、延遲載入、減少 ViewState 與控件數量。
- A詳: 症狀：頁面載入慢、記憶體高。原因：反射頻繁、控件樹龐大、ViewState 膨脹。解法：快取 PropertyInfo、使用虛擬化或分頁、關閉不必要 ViewState、以輕量輸入替代複雜控件。預防：壓測與剖析、設定性能目標。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q6, B-Q16

Q10: 程式庫升級造成二進位相容性問題怎麼辦？
- A簡: 遵守語意版本，避免破壞性變更與提供過渡層。
- A詳: 症狀：升級後編譯或執行期失敗。原因：簽章變動、命名調整、移除成員。解法：提供 Obsolete 過渡、維持舊 API wrapper、明確版號策略。預防：API 檢查工具、相容性測試套件、文件公告。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: C-Q9

### 學習路徑索引
- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 .NET 的泛型（Generic Type）？
    - A-Q2: 什麼是泛型基底類別（Generic Base Class）？
    - A-Q3: 為何要在 ASP.NET UserControl 中使用泛型？
    - A-Q4: 在繼承時指定型別參數後，子類別是否仍是泛型？
    - A-Q5: Editor<T> 的核心價值是什麼？
    - A-Q6: 使用 object 作為 Value 與使用泛型的差異是什麼？
    - A-Q7: 何謂強型別（Strongly-Typed）Value 屬性？
    - A-Q8: 為什麼要讓不同型別編輯器共用同一基底類別？
    - A-Q10: 什麼是「開放式」與「關閉式」泛型？
    - B-Q1: Editor<T> 基底類別如何運作？
    - B-Q2: DateEditor : Editor<DateTime> 的執行流程為何？
    - C-Q1: 如何實作 Editor<T> 基底類別？
    - C-Q2: 如何建立 DateEditor 並與 Calendar 綁定？
    - C-Q3: 如何在 Editor<T> 加入並觸發 OnChange 事件？
    - C-Q8: 如何在標記中使用自訂編輯器並傳入初值？

- 中級者：建議學習哪 20 題
    - A-Q9: 何謂多型（Polymorphism）在此案例中的角色？
    - A-Q12: 使用泛型基底對重用性與維護性有何影響？
    - A-Q13: 控制項屬性型別如何影響標記綁定？
    - A-Q14: 泛型基底與介面的差異？
    - B-Q3: CLR 中泛型封閉與繼承的規則是什麼？
    - B-Q4: 共用 OnChange 事件的設計機制是什麼？
    - B-Q5: 「記住上次輸入」功能背後機制是什麼？
    - B-Q6: 反射與屬性動態產生編輯畫面的原理是什麼？
    - B-Q7: 類型到編輯器的映射策略如何設計？
    - B-Q8: 在頁面生命週期中如何正確載入動態編輯器？
    - B-Q9: 泛型基底與多型方法呼叫的關係？
    - B-Q10: 強型別 Value 對型別安全與效能影響？
    - B-Q11: 標記 value 的轉換機制？
    - C-Q4: 如何實作「記住上次輸入」功能？
    - C-Q5: 如何用反射為物件動態產生編輯表單？
    - C-Q6: 如何將編輯器值回寫到物件實例？
    - C-Q7: 如何為複雜型別自訂 Editor？
    - D-Q2: 標記 Value 轉換錯誤怎麼辦？
    - D-Q3: 動態新增編輯器後事件不觸發？
    - D-Q5: OnChange 事件未觸發或觸發兩次？

- 高級者：建議關注哪 15 題
    - A-Q11: 泛型與 Singleton 模式如何結合？
    - A-Q15: 什麼情境不適合使用泛型基底編輯器？
    - A-Q16: 為何示例看似平凡卻價值高？
    - B-Q12: 泛型基底如何與依賴注入整合？
    - B-Q13: 用 Attribute 控制外觀與驗證的機制？
    - B-Q14: Generic constraints 的用途與限制？
    - B-Q15: 與 Singleton 模式結合時的運作原理？
    - B-Q16: 編輯器集合的管理與組合如何設計？
    - C-Q9: 如何封裝編輯器庫以便重用與發佈？
    - C-Q10: 如何撰寫單元測試驗證 Editor<T>？
    - D-Q1: 泛型基底 UserControl 設計時無法載入？
    - D-Q4: 反射產生表單找不到對應編輯器？
    - D-Q6: 記住上次輸入保存或讀取失敗？
    - D-Q9: 大量反射/控件導致效能不佳？
    - D-Q10: 程式庫升級造成相容性問題？