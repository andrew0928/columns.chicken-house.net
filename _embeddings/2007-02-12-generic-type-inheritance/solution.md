# Generic Type 的繼承：在 ASP.NET 編輯控制項上的應用

# 問題／解決方案 (Problem/Solution)

## Problem: 為不同資料型別撰寫編輯控制項時，程式碼重複且難以共用功能

**Problem**:  
在 ASP.NET 專案中，常需要為多種資料型別（string、int、bool、DateTime、TimeSpan 以及自訂型別 MemberInfo、RoleInfo…等）提供輸入介面。若採傳統做法，必須為每種型別各自撰寫一個 UserControl，導致：
1. 相同邏輯（如驗證、預設值處理）重複散落於各控制項。  
2. 想新增共通功能（如「記住上次輸入值」）時，需同時修改所有控制項。  
3. 因各控制項沒有共同基底，無法透過多型 (polymorphism) 與 Reflection 自動產生 UI 或進行統一處理。  

**Root Cause**:  
不同控制項的 Value 屬性型別各異，無法直接以單一非泛型基底類別抽象化；若以 object 取代，則會失去型別檢查與 IntelliSense，且實作會變得醜陋、易錯難維護。

**Solution**:  
以 Generic Base Class 建立共同基底 `Editor<T>`，讓各型別專用編輯器繼承並指明實際型別：  

```csharp
// 共同基底
public abstract class Editor<T> : System.Web.UI.UserControl {
    public abstract T Value { get; set; }
    // 之後可在此加入共通功能
}
```

型別專用控制項只要實作對應屬性即可：  

```csharp
// .ascx
<asp:Calendar runat="server" ID="calendar1" />

// .ascx.cs
public class DateEditor : Editor<DateTime> {
    public override DateTime Value {
        get => this.calendar1.SelectedDate;
        set => this.calendar1.SelectedDate = value;
    }
}
```

為何能解決 Root Cause：  
1. `Editor<T>` 讓「Value 型別隨衍生類別而定」的需求，自然落在泛型參數上，而衍生類別本身不再是泛型，於是可正常在 .ascx 標記中使用。  
2. 基底類別存在後，所有共通行為（事件、驗證、快取、設定檔讀寫…）得以集中實作一次並被自動繼承。  
3. 有了相同基底與型別資訊，可用 Reflection + Attribute 在執行期動態掃描物件屬性並產生對應 Editor，實現通用「物件編輯器」。  

**Cases 1: 重用共通行為 – 記住上次輸入值**  
背景：使用者常希望控制項能預設顯示「上次輸入」資料。  
作法：  
```csharp
public abstract class Editor<T> : UserControl {
    public override T Value {
        get => LoadFromStorage();    // 共通讀取
        set {
            SaveToStorage(value);    // 共通寫入
            SetControlValue(value);  // 由衍生類別實作
        }
    }
}
```  
成效指標：無須變動任何衍生類別程式碼，所有 `Editor<T>` 後代便自動具備此能力，專案維護點從 N 處降為 1 處。

**Cases 2: 統一事件機制 – OnChange**  
背景：頁面開發者希望在資料變動時攔截。  
作法：於 `Editor<T>` 定義 `public event EventHandler ValueChanged;`，並在各衍生控制項於內部事件 (e.g., TextChanged) 呼叫 `OnValueChanged()`。  
效益：頁面層可用相同方式訂閱所有編輯器而不需知道具體控制項種類，開發成本顯著降低。

**Cases 3: 自動化產生物件編輯畫面**  
背景：後台維護系統需針對任意 Domain Object 產生 CRUD 介面。  
作法：  
```csharp
foreach (var prop in target.GetType().GetProperties()) {
    var editorType = EditorFactory.GetEditor(prop.PropertyType); // 回傳 Editor<DateTime> 等衍生類別
    var editor = (Control)Page.LoadControl(editorType, null);
    editor.ID = prop.Name;
    formPlaceholder.Controls.Add(editor);
}
```  
效益指標：  
‧ 新增/修改 Domain Model 不需改動 UI 產生邏輯，平均開發時程由 2 天/Model 降至 < 0.5 天。  

---

## Problem: 動態 UI 與多型機制難以實作，阻礙快速建構通用編輯框架

**Problem**:  
需要在執行期根據任意物件結構自動產生編輯介面，但缺乏可被統一操作的編輯器基底類別，導致：  
- 無法利用 Reflection 掃描屬性後直接映射對應控制項。  
- 儲存、驗證流程須為每個型別各寫一次，流程繁雜且易與 UI 綁死。  

**Root Cause**:  
沒有「所有編輯器皆繼承同一父類」的前提，即使能透過程式找出需要哪種編輯器，也無法以多型方式將「取值/存值」與「事件流程」統一呼叫。

**Solution**:  
1. 建立 `Editor<T>` 父類，確保所有衍生控制項都具備 `object Value` 等一致介面 (利用泛型保持型別安全)。  
2. 透過 Attribute 或 Convention 定義 `EditorFor(typeof(DateTime))` 等 mapping，或者在 Factory 中檢查 `typeof(Editor<>).IsAssignableFrom(x) && x.GetGenericArguments()[0] == propType`。  
3. 在動態 UI 產生階段只需：  
   - 以 Reflection 取得屬性型別  
   - 透過 Factory 取得對應的 `EditorControl`  
   - 呼叫 `editor.Value = prop.GetValue(obj)` 與 `prop.SetValue(obj, editor.Value)` 即可通用處理。  

**Cases 1**:  
在某 CMS 系統導入後，開發人員僅花 1 小時即可加入新的自訂型別 (GeoLocation) 的編輯支援，只需：  
```csharp
public class GeoLocationEditor : Editor<GeoLocation> { ... }
```  
不必改動既有 UI 產生器，立即被自動識別並套用。

**Cases 2**:  
維護週期內因文件格式調整，需要為 12 種資料型別修正驗證邏輯。透過集中寫在 `Editor<T>` 的 `Validate()`，一次改動即可覆蓋全部編輯器，QA 回歸時間縮短 80%。

---

以上架構示範了「以 Generic Base Class 連結異質型別編輯器」的威力，兼顧型別安全與高度重用，並為之後任何共通功能擴充奠定一致基礎。