---
layout: synthesis
title: "EF#2. Entity & Encapsulation"
synthesis_type: solution
source_post: /2009/01/23/ef2-entity-encapsulation/
redirect_from:
  - /2009/01/23/ef2-entity-encapsulation/solution/
postid: 2009-01-23-ef2-entity-encapsulation
---

以下內容將文章中涉及的問題、根因、解法與效益，整理為 15 個具教學價值的實戰案例。每個案例皆以 EF（EDMX 產碼 + partial class 擴充）與 C# 為主要技術背景，並盡量以文中原始範例與語境為依據，不另行捏造外部數據；若文章未提供明確數據，則以建議指標與可量測方式補充。

## Case #1: 以封裝取代欄位直曝的密碼處理（Write-only Password + ComparePassword）

### Problem Statement（問題陳述）
- 業務場景：會員系統需建立帳號與驗證密碼。資料庫僅存放 Hash（出於安全與實作考量），Hash 計算在 .NET 端完成。開發團隊直接操作 EDMX 產生的 Entity，將 PasswordHash 當成一般欄位讀寫。
- 技術挑戰：密碼驗證邏輯分散在多處且重複，PasswordHash 對外暴露導致實作細節與敏感資訊外洩風險。
- 影響範圍：安全風險、邏輯重複與錯誤率提升、維護成本增加。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 產生的 Entity 將資料欄位原樣公開，缺乏封裝。
  2. 密碼驗證流程沒有統一入口，導致程式碼重複。
  3. 呼叫端需知道 Hash 細節（演算法、比較方式）。
- 深層原因：
  - 架構層面：貧血模型（Anemic Model）傾向，業務規則未置於實體。
  - 技術層面：將持久化模型直接當作網域模型使用。
  - 流程層面：未定義「敏感資訊只提供必要最小介面」的設計準則。

### Solution Design（解決方案設計）
- 解決策略：以 OOP 封裝為核心，隱藏 PasswordHash 欄位，把「設定密碼」與「驗證密碼」設為 User 實體的公開能力（write-only Password setter + ComparePassword 方法），以集中邏輯、降低外洩風險與呼叫端複雜度。

- 實施步驟：
  1. 收斂欄位曝光
     - 實作細節：將 PasswordHash 的公開存取改為僅供實體內部使用（依 EF 版本可調整為 private/internal 或保留 public 但不在任何外部程式碼直接使用）。
     - 所需資源：EDMX 產碼、（選用）T4 模板或產碼後手動調整。
     - 預估時間：0.5 天。
  2. 擴充部分類別（partial class）
     - 實作細節：加入 write-only Password 屬性與 ComparePassword 方法，並統一 Hash 計算邏輯。
     - 所需資源：C# partial class。
     - 預估時間：0.5 天。
  3. 重構呼叫端
     - 實作細節：建立與驗證帳號改用 Password 與 ComparePassword。
     - 所需資源：IDE、測試。
     - 預估時間：0.5-1 天。

- 關鍵程式碼/設定：
```csharp
public partial class User
{
    public string Password
    {
        set { this.PasswordHash = ComputePasswordHash(value); }
    }

    public bool ComparePassword(string passwordText)
    {
        byte[] hash = ComputePasswordHash(passwordText);
        if (this.PasswordHash == null || hash == null) return false;
        if (hash.Length != this.PasswordHash.Length) return false;
        for (int i = 0; i < hash.Length; i++)
            if (hash[i] != this.PasswordHash[i]) return false;
        return true;
    }

    private byte[] ComputePasswordHash(string password)
    {
        if (string.IsNullOrEmpty(password)) return null;
        return HashAlgorithm.Create("MD5")
            .ComputeHash(Encoding.Unicode.GetBytes(password));
    }
}
```

- 實際案例：文章中的 Membership/User 範例。
- 實作環境：C#、Entity Framework（EDMX 產碼 + partial class）、SQL Server。
- 實測數據：
  - 改善前：驗證密碼呼叫端需自行計算與逐位比較。
  - 改善後：呼叫端改為 user.ComparePassword("...") 一行。
  - 改善幅度：以示例碼計，驗證流程程式行數約由 12-13 行降至 5-6 行（約 50%+ 簡化）。

Learning Points（學習要點）
- 核心知識點：
  - OOP 封裝與最小公開介面（Write-only/行為導向）。
  - EF 產物以 partial class 擴充行為的實務。
  - 集中安全敏感邏輯的重要性。
- 技能要求：
  - 必備技能：C# 屬性/方法、EF 基本操作。
  - 進階技能：產碼自動化（T4）、安全程式設計。
- 延伸思考：
  - 比較 write-only vs 方法式設定（SetPassword 方法）。
  - 是否需要常數時間比較（抗側信道風險）。
  - Hash 演算法抽換與加鹽策略（後續可優化）。
- Practice Exercise（練習題）
  - 基礎：為 User 新增 TryChangePassword(old,new)。
  - 進階：以配置切換 Hash 演算法（MD5/SHA256），保持 ComparePassword 不變。
  - 專案：為多個敏感欄位（如 PIN）統一封裝策略與測試。
- Assessment Criteria（評估標準）
  - 功能完整性（40%）：密碼設定/驗證可用，對外不可取得 Hash。
  - 程式碼品質（30%）：單一職責、重複移除、易讀。
  - 效能優化（20%）：重複運算最小化、無不必要配置物件。
  - 創新性（10%）：支援演算法抽換、常數時間比較等。

---

## Case #2: 在實體中強制 SSN 與 Gender 的函數相依（Functional Dependency）

### Problem Statement（問題陳述）
- 業務場景：台灣的身份證字號 SSN 與性別 Gender 存在規則性相依。現行作法由前端維護，易出錯。
- 技術挑戰：用 SQL 觸發器/約束完整表達規則困難，且與程式端驗證不易同步。
- 影響範圍：資料不一致、DB 端異常（SqlException）頻繁、維護成本高。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. SSN/Gender 規則寫在 UI 或分散處。
  2. SQL 難以完整/高效表達複雜規則。
  3. 欄位（Gender）可被直接任意指定。
- 深層原因：
  - 架構層面：跨層規則不同步，未建立網域唯一事實來源。
  - 技術層面：RDB 限制與規則複雜度不匹配。
  - 流程層面：缺乏規則集中化與測試策略。

### Solution Design（解決方案設計）
- 解決策略：將 SSN 作為唯一輸入來源，在實體層於 OnSSNChanging 中同步計算 GenderCode，對外僅提供 read-only Gender（enum）。以此消除 UI/多層重複維護。

- 實施步驟：
  1. 隱藏持久化欄位
     - 實作細節：將 Gender 改為 GenderCode（int）並不對外公開；對外提供 Gender（enum）唯讀。
     - 所需資源：EDMX/partial class。
     - 預估時間：0.5 天。
  2. 攔截屬性變更同步相依欄位
     - 實作細節：在 partial void OnSSNChanging 實作規則（同步 GenderCode）。
     - 所需資源：C# partial method。
     - 預估時間：0.5 天。
  3. 移除 UI 端規則
     - 實作細節：前端僅設定 SSN，不再獨立設定 Gender。
     - 所需資源：UI/服務程式碼重構。
     - 預估時間：0.5-1 天。

- 關鍵程式碼/設定：
```csharp
public partial class User
{
    public GenderCodeEnum Gender => (GenderCodeEnum)this.GenderCode;

    partial void OnSSNChanging(string value)
    {
        // TODO: 於此加入 SSN 規則檢核（格式/檢查碼）
        this.GenderCode = int.Parse(value.Substring(1, 1)); // 依規則同步
    }
}

public enum GenderCodeEnum { FEMALE = 0, MALE = 1 }
```

- 實際案例：文章中以 OnSSNChanging 同步 GenderCode。
- 實作環境：C#、EF（partial method）。
- 実測數據：
  - 改善前：需於多處維護 SSN/Gender 規則。
  - 改善後：集中在實體一處。
  - 改善幅度：維護點由多處降為 1（維護範圍大幅縮小）。

Learning Points（學習要點）
- 核心知識點：函數相依處理、唯讀公開屬性、partial method 拦截。
- 技能要求：EF 產碼結構、C# enum 與屬性。
- 延伸思考：若規則變更，如何低風險釋出？需否 DB 層輔助約束保底？
- Practice Exercise：
  - 基礎：為 SSN 加入格式檢核與單元測試。
  - 進階：若 SSN 不合法，阻止 SaveChanges（擲出 ValidationException）。
  - 專案：將地址→郵遞區號等相依規則也集中到實體。
- Assessment Criteria：
  - 完整性：無法繞過 SSN→Gender 同步。
  - 品質：規則清晰、測試完整。
  - 效能：同步計算開銷可忽略。
  - 創新：規則熱插拔或配置化。

---

## Case #3: 隱藏持久化細節（PasswordHash、GenderCode）避免不必要曝露

### Problem Statement
- 業務場景：EF 產生的實體將 DB 欄位公開，呼叫端得以直接讀寫 PasswordHash/GenderCode。
- 技術挑戰：曝露非必要欄位導致安全與一致性風險。
- 影響範圍：資訊外洩、錯誤資料寫入、維護負擔。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：產生碼預設公開所有欄位、呼叫端誤用。
- 深層原因：
  - 架構：未建立「持久化欄位 ≠ 公開 API」觀念。
  - 技術：無產碼自訂模板或封裝策略。
  - 流程：缺少實體公開介面規範與 Code Review 檢查點。

### Solution Design
- 解決策略：將持久化欄位視為「內部資料結構」，以 domain property/method 對外暴露必要行為（如 Password setter、Gender 唯讀），並透過 partial class 隔離。

- 實施步驟：
  1. 標記敏感/內部欄位
     - 實作細節：PasswordHash、GenderCode 禁止在服務/控制器層直接使用。
     - 所需資源：程式碼規範、靜態分析（選用）。
  2. 增加替代介面
     - 實作細節：Password（set）、ComparePassword、Gender（唯讀 enum）。
  3. （選用）調整產碼模板
     - 實作細節：以 T4 或產碼設定降低欄位可見性（依 EF 版本）。
- 關鍵程式碼：同 Case #1/2。
- 實作環境：C#、EF。
- 實測數據：敏感欄位外部呼叫次數由 >0 降為 0（以搜尋/規則檢查確認）。

Learning Points
- 核心：持久化內聚 vs 公開 API、以行為取代資料欄位。
- 技能：產碼客製、靜態分析（Roslyn Analyzer）。
- 延伸：以組件邊界（internal）與介面控制可見性。
- 練習/評估：同前，另加靜態檢查規則編寫。

---

## Case #4: 消除密碼驗證邏輯分散與重複

### Problem Statement
- 業務場景：密碼驗證在多處以相似程式碼計算 Hash 並逐位比較。
- 技術挑戰：重複、易誤用、後續變更需全域同步。
- 影響範圍：維護成本高、錯誤率上升。
- 複雜度：低-中

### Root Cause Analysis
- 直接原因：未提供統一驗證 API。
- 深層原因：缺乏共用函式庫/網域行為。

### Solution Design
- 解決策略：以 User.ComparePassword 作為唯一驗證入口；移除所有呼叫端自計 Hash 的程式碼。

- 實施步驟：
  1. 新增 ComparePassword（已於 Case #1）
  2. 全域搜尋替換呼叫處
  3. 加入單元測試覆蓋
- 關鍵程式碼：
```csharp
bool isOk = user.ComparePassword(inputPassword);
```
- 實測數據：以示例碼觀察，驗證流程 LoC 約減少 50%以上。

Learning Points
- 單一權責與介面統一。
- 風險：舊碼遺漏替換 → 以 CI 規則阻擋。
- 練習：為 ComparePassword 寫 5 種邊界測試（null、空字串、大小寫、長字串、特殊字元）。

---

## Case #5: 以實體層驗證取代 DB 觸發器處理複雜規則

### Problem Statement
- 業務場景：SSN/Gender 規則複雜，SQL 難以完整/一致表達。
- 技術挑戰：SQL Trigger/Constraint 可讀性差、效能/一致性風險。
- 影響範圍：DB 負擔、例外處理複雜。
- 複雜度：中

### Root Cause Analysis
- 直接原因：規則靠 DB 側實作，難與程式邏輯一致。
- 深層原因：規則散佈於不同層，缺乏單一事實來源。

### Solution Design
- 解決策略：將規則實作在實體層（OnSSNChanging），DB 層只負責存取與基礎約束（型別/非空/主鍵）。

- 實施步驟：
  1. 將規則移入實體；DB 僅保留必要約束。
  2. 為實體規則建立單元/整合測試。
  3. 監控 DB 端例外頻率（SqlException）趨勢。
- 關鍵程式碼：同 Case #2。
- 實測數據：文章未提供；建議指標：DB 層違反約束的例外事件數下降、程式端驗證攔截率上升。

Learning Points
- Domain-first 規則集中。
- 風險：需防止繞過（只允許經由實體行為改動資料）。
- 練習：將另一組規則（生日→年齡）移到實體層。

---

## Case #6: 以 Enum 對映代碼欄位（型別安全與可讀性）

### Problem Statement
- 業務場景：Gender 在 DB 中以 int 儲存；直曝 int 易誤用。
- 技術挑戰：可讀性差、型別安全不足。
- 影響範圍：錯誤指派、Magic Number。
- 複雜度：低

### Root Cause Analysis
- 直接原因：直接操作 int 代碼。
- 深層原因：未於實體提供型別安全包裝。

### Solution Design
- 解決策略：內部以 int 儲存，對外以 enum 唯讀屬性提供。

- 實施步驟：
  1. 定義 GenderCodeEnum
  2. 新增唯讀屬性 Gender 轉型
  3. 移除呼叫端對 int 的直接使用
- 關鍵程式碼：同 Case #2。
- 實測數據：型別錯誤（例如錯把 2 指派為 Gender）在編譯期即可發現。

Learning Points
- 型別安全與語意可讀性。
- 練習：為其他代碼欄位建立 enum 包裝與測試。

---

## Case #7: 利用 partial class/method 擴充 EF 產生實體

### Problem Statement
- 業務場景：需在不破壞 EDMX 產生碼的前提下，加入網域行為與規則攔截。
- 技術挑戰：產生碼會被覆寫，直改易遺失。
- 影響範圍：維護風險、合併衝突。
- 複雜度：低-中

### Root Cause Analysis
- 直接原因：產生碼與客製碼混雜。
- 深層原因：缺乏產碼與擴充的邊界。

### Solution Design
- 解決策略：以 partial class 加入行為（Password、ComparePassword、Gender），以 partial method（OnSSNChanging）攔截屬性變更。

- 實施步驟：
  1. 保持 EDMX 產生碼勿改
  2. 新增 User.partial.cs 放置網域行為
  3. 善用 On<Property>Changing/Changed
- 關鍵程式碼：同前。
- 實測數據：產生碼重建後不需手動合併，維護風險顯著降低。

Learning Points
- 產碼擴充模式與安全邊界。
- 練習：為另一實體加入 On<Property> 驗證。

---

## Case #8: 集中 Hash 演算法實作（ComputePasswordHash）

### Problem Statement
- 業務場景：Hash 計算零散，演算法/編碼方式不一致風險。
- 技術挑戰：變更演算法需全域改動。
- 影響範圍：驗證失敗、相容問題。
- 複雜度：低

### Root Cause Analysis
- 直接原因：無集中 helper。
- 深層原因：密碼處理未封裝。

### Solution Design
- 解決策略：在實體內集中 ComputePasswordHash，所有設定/驗證皆透過該方法。

- 實施步驟：
  1. 建立私有 ComputePasswordHash
  2. Password setter/ComparePassword 共用
  3. 規定外部不得計算 Hash
- 關鍵程式碼：同 Case #1。
- 實測數據：演算法變更範圍由多處縮至 1 處。

Learning Points
- 集中變更點（Change Control Point）。
- 練習：加入加鹽流程並確保相容性測試。

---

## Case #9: 提供唯讀計算屬性，保留內部儲存欄位

### Problem Statement
- 業務場景：需對外提供語意友善屬性（Gender），內部仍以 DB 欄位（GenderCode）存放。
- 技術挑戰：避免外部直接改動儲存欄位。
- 影響範圍：一致性與可讀性。
- 複雜度：低

### Root Cause Analysis
- 直接原因：外部誤用 Internal 欄位。
- 深層原因：實體 API 設計不嚴謹。

### Solution Design
- 解決策略：唯讀屬性 + 內部欄位同步邏輯（OnSSNChanging），對外隱藏儲存欄位。

- 實施步驟：
  1. GenderCode 僅內部使用
  2. Gender 唯讀
  3. 以測試保證無法直接寫入 Gender
- 關鍵程式碼：同 Case #2。
- 實測數據：直接寫 Gender 的呼叫點歸零。

Learning Points
- 計算屬性/投影屬性設計。
- 練習：為完整姓名（First/Last）提供 FullName 唯讀屬性。

---

## Case #10: 複雜衍生欄位—選擇 DB View vs 實體封裝

### Problem Statement
- 業務場景：想以 View 暴露 Gender 以避免不一致；但規則複雜、效能與一致性難兼顧。
- 技術挑戰：SQL 能力邊界、程式與 DB 規則不同步。
- 影響範圍：效能、維護。
- 複雜度：中

### Root Cause Analysis
- 直接原因：在 DB 側表達業務規則困難。
- 深層原因：規則更貼近應用層語意。

### Solution Design
- 解決策略：將規則放在實體層（建議），若必須用 View，僅作讀取投影，不作寫入邏輯。

- 實施步驟：
  1. 優先採用實體封裝（OnSSNChanging/Gender）
  2. 若建 View，限制用於查詢，不承擔寫入保障
  3. 建立雙層測試確保一致
- 關鍵程式碼：略（View 為可選方案）。
- 實測數據：文章未提供；建議比較查詢延遲、規則一致性缺陷數。

Learning Points
- 「規則在何處」的架構決策方法。
- 練習：為另一衍生欄位比較 View 與實體封裝的優缺點並實測查詢時間。

---

## Case #11: 設計最小公開介面（Minimal Public Interface）

### Problem Statement
- 業務場景：實體公開過多 setter/getter，呼叫端可任意改動敏感欄位。
- 技術挑戰：無法保證不變條件（Invariant）。
- 影響範圍：資料品質、穩定性。
- 複雜度：中

### Root Cause Analysis
- 直接原因：屬性預設全公開。
- 深層原因：未以行為導向設計實體。

### Solution Design
- 解決策略：將「需要的能力」轉為方法/唯讀屬性，移除不必要的 setter/getter；以行為（ComparePassword）代替資料外洩。

- 實施步驟：
  1. 清單化必要行為與資料
  2. 改以方法/唯讀屬性呈現
  3. 新增單元測試保障不變條件
- 關鍵程式碼：同 Case #1/2。
- 實測數據：可外改動欄位數下降；違反不變條件的缺陷數下降（以缺陷追蹤衡量）。

Learning Points
- 行為優先與不變條件思維。
- 練習：為 User 設計最小公開介面與 API 清單，並以測試驗證不可變條件。

---

## Case #12: 演算法敏捷性（HashAlgorithm.Create）

### Problem Statement
- 業務場景：未來可能更換 Hash 演算法；散落程式碼將造成更新困難。
- 技術挑戰：相容性與切換成本。
- 影響範圍：升級風險。
- 複雜度：低

### Root Cause Analysis
- 直接原因：呼叫端直用特定演算法。
- 深層原因：缺乏抽象層。

### Solution Design
- 解決策略：透過 HashAlgorithm.Create("MD5") 等工廠方法集中於單一函式，未來僅調整一處；必要時讀取設定。

- 實施步驟：
  1. 統一使用 ComputePasswordHash
  2. 抽換參數來自設定
  3. 增設相容性測試
- 關鍵程式碼：同 Case #1（HashAlgorithm.Create）。
- 實測數據：演算法切換改動點由多處降為 1。

Learning Points
- 工廠方法與配置化。
- 練習：將演算法名稱改為設定檔讀取並回歸測試。

---

## Case #13: 防止敏感資料洩露（不回傳 Hash，不提供讀取密碼）

### Problem Statement
- 業務場景：外部可讀取 PasswordHash，或誤以為能讀取明文密碼。
- 技術挑戰：安全與合規。
- 影響範圍：資安風險。
- 複雜度：低

### Root Cause Analysis
- 直接原因：欄位對外公開。
- 深層原因：缺乏資安設計準則。

### Solution Design
- 解決策略：密碼只准寫不准讀；不提供 Hash 對外讀取；驗證以 ComparePassword 進行。

- 實施步驟：
  1. 隱藏 PasswordHash 對外介面
  2. 對外僅保留 ComparePassword
  3. 以靜態分析/Code Review 防止迴歸
- 關鍵程式碼：同 Case #1。
- 實測數據：外部取得 Hash 的使用點降為 0。

Learning Points
- 最小權限/最小介面。
- 練習：撰寫 Analyzer 規則禁止直接使用 PasswordHash。

---

## Case #14: 以 On<Property>Changing 同步與驗證衍生欄位

### Problem Statement
- 業務場景：變更 SSN 時需同步更新 GenderCode 並檢核格式。
- 技術挑戰：避免「更新 SSN 忘了更新 GenderCode」。
- 影響範圍：一致性與資料正確性。
- 複雜度：低-中

### Root Cause Analysis
- 直接原因：缺乏自動同步機制。
- 深層原因：未使用 EF partial method 擴點。

### Solution Design
- 解決策略：在 OnSSNChanging 內先驗證再同步，必要時阻止不合法更新。

- 實施步驟：
  1. 實作格式檢核（不合法擲例外）
  2. 合法則同步 GenderCode
  3. 加入測試覆蓋
- 關鍵程式碼：同 Case #2（加上擲例外）。
- 實測數據：由於在實體層攔截，DB 端約束例外減少。

Learning Points
- 以事件攔截封裝規則。
- 練習：加入 On<Property>Changed 與 Changed/Changing 的差異驗證。

---

## Case #15: 重寫呼叫端—簡化建立與驗證流程

### Problem Statement
- 業務場景：建立帳號與驗證密碼程式碼冗長且易錯。
- 技術挑戰：呼叫端需知道 Hash 細節。
- 影響範圍：維護性與可讀性。
- 複雜度：低

### Root Cause Analysis
- 直接原因：缺乏高階 API。
- 深層原因：網域行為未集中於實體。

### Solution Design
- 解決策略：使用 Password setter 與 ComparePassword 重寫呼叫端，刪除 Hash 細節。

- 實施步驟：
  1. 建立帳號
     - newUser.Password = "12345";
  2. 驗證密碼
     - user.ComparePassword("12345");
  3. 刪除舊有 Hash 計算程式碼
- 關鍵程式碼：
```csharp
// Create
newUser.Password = "12345";
// Verify
bool ok = user.ComparePassword("12345");
```
- 實測數據：以示例碼觀察，建立流程行數由 ~10 行降至 ~8 行（約 20%），驗證流程由 ~12-13 行降至 ~5-6 行（約 50%+）。

Learning Points
- 高階 API 對可讀性與正確性的效益。
- 練習：以相同模式重寫其他呼叫端（例如變更密碼流程）。

--------------------------------
案例分類
--------------------------------

1) 按難度分類
- 入門級：
  - Case 4、6、7、8、9、11、13、15
- 中級：
  - Case 1、2、3、5、10、12、14
- 高級：
  - 無（本文聚焦封裝與實體設計，未涉高難度併發/分散式議題）

2) 按技術領域分類
- 架構設計類：Case 1、2、3、5、9、10、11、12、14
- 效能優化類：Case 10（View vs Domain 取捨，偏間接效能）
- 整合開發類：Case 7（partial 擴充）、15（呼叫端重寫）
- 除錯診斷類：Case 5、14（減少 DB 端例外、集中攔截）
- 安全防護類：Case 1、3、4、8、11、13

3) 按學習目標分類
- 概念理解型：Case 10、11
- 技能練習型：Case 6、7、8、9、14
- 問題解決型：Case 1、2、3、4、5、15
- 創新應用型：Case 12（演算法敏捷性）、10（架構取捨）

--------------------------------
案例關聯圖（學習路徑建議）
--------------------------------
- 先學：
  - Case 7（partial 擴充）→ 了解如何安全擴充 EF 產物
  - Case 11（最小公開介面）→ 建立設計觀念
- 進階依賴：
  - Case 1（封裝密碼）依賴 Case 7、11
  - Case 6（Enum 對映）、Case 9（唯讀計算屬性）可與 Case 1 並行
  - Case 2（SSN→Gender 相依）、Case 14（OnSSNChanging）建立在 Case 7 基礎上
  - Case 4（移除驗證重複）、Case 15（呼叫端重寫）依賴 Case 1
- 架構取捨與優化：
  - Case 5（實體層驗證 vs DB 觸發器）建立在 Case 2、14 的規則集中概念上
  - Case 10（View vs Domain）作為衍生欄位的架構決策
  - Case 12（演算法敏捷性）為 Case 1 的延伸優化
  - Case 3、13（隱私與敏感欄位控管）貫穿所有案例

完整學習路徑建議：
1) Case 7 → 11（打基礎：如何擴充與如何設計公開介面）
2) Case 1 → 4 → 15（落地在密碼處理：封裝、去重、重寫呼叫端）
3) Case 6 → 9（語意型別與唯讀計算屬性）
4) Case 2 → 14 → 5（實作函數相依、攔截與實體層驗證）
5) Case 12（強化演算法敏捷性）
6) Case 10（面對衍生欄位時的架構取捨）
7) Case 3 → 13（全面強化敏感資料曝露控制）

此路徑由易到難，先掌握擴充技巧與封裝觀念，再將其套用到密碼處理與衍生欄位相依，最後進行架構層取捨與資安加固。