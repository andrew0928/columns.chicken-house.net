---
layout: synthesis
title: "不只是 TDD #2, 兩個版本自我驗證 + 執行期驗證"
synthesis_type: solution
source_post: /2017/01/31/leetcode2-assert/
redirect_from:
  - /2017/01/31/leetcode2-assert/solution/
---

以下內容基於原文的技術脈絡，萃取並重組為可教學、可實作、可評估的 16 個解決方案案例。每個案例均包含問題、根因、方案、實作片段、實測數據與練習與評估設計。

## Case #1: 以「保守版本」建立可靠基線（Shortest Palindrome）

### Problem Statement（問題陳述）
業務場景：面對 LeetCode 題目 Shortest Palindrome，新手或在陌生問題領域時，直接追求最優演算法風險高，且官方測資只有 3 筆，無法充分驗證。需要一個「可靠基線」作為後續優化與自我驗證的對照組。
技術挑戰：最佳化會大幅改動主邏輯，若無對照組，很難確定正確性。
影響範圍：錯誤的最佳化可能導致隱性邏輯錯誤，難以發現與回退。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 測資稀少（LeetCode 只有 3 筆）導致覆蓋不足。
2. 演算法改寫幅度大，缺少穩定的正確性參照（oracle）。
3. 先追求效能忽略正確性，易引入 regression。
深層原因：
- 架構層面：缺少「雙版本對照」的驗證機制。
- 技術層面：未建立可讀性高、易驗證的基準解。
- 流程層面：測試驅動僅止於單元測試，未建立「自動 oracle」。

### Solution Design（解決方案設計）
解決策略：先實作最容易寫、可恥但有用的保守版本（BasicSolution），確保功能正確，再用它作為 oracle 驗證後續效能版。正確性優先，效能其次。

實施步驟：
1. 實作 O(n^2) 保守演算法
- 實作細節：向右掃描首尾字符匹配，check 驗證頭段為回文，padtext 反轉剩餘前置。
- 所需資源：C#, .NET, MSTest
- 預估時間：1-2 小時
2. 以少量既有測資建立初步信心
- 實作細節：使用 LeetCode 現有 3 筆測資驗證
- 所需資源：MSTest
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
public class BasicSolution
{
    private string source = null;

    public string ShortestPalindrome(string s)
    {
        if (string.IsNullOrEmpty(s)) return "";
        this.source = s;

        char target = s[0];
        for (int right = s.Length - 1; right >= 0; right--)
        {
            if (s[right] != target) continue;
            if (check(right))
            {
                return padtext(right);
            }
        }
        return null; // 不應達到
    }

    private bool check(int right)
    {
        for (int i = 0; i <= (right - i); i++)
            if (this.source[i] != this.source[right - i]) return false;
        return true;
    }

    private string padtext(int right)
    {
        var sb = new StringBuilder();
        sb.Append(this.source.Substring(right + 1).Reverse().ToArray());
        sb.Append(this.source);
        return sb.ToString();
    }
}
```
實際案例：用 BasicSolution 作為後續快速版的結果對照組。
實作環境：C# 7+/ .NET Framework 或 .NET 6+/ MSTest。
實測數據：
改善前：無可靠基線、僅 3 筆測資。
改善後：建立保守基線，3/3 測資通過。
改善幅度：基線可用性從 0 到 1（建立 oracle）。

Learning Points（學習要點）
核心知識點：
- 正確性優先於效能的工程策略
- 基線（oracle）設計
- 低複雜度演算法作為對照組
技能要求：
- 必備技能：C#、基本演算法實作
- 進階技能：將基線內聚為可重用組件
延伸思考：
- 可用於任何未知領域的需求探索階段
- 風險：若基線本身錯誤，會誤導後續驗證
- 可加入更多 invariants 輔助驗證基線自身正確性
Practice Exercise（練習題）
- 基礎練習：實作 BasicSolution 並通過 3 筆官方測資（30 分鐘）
- 進階練習：新增 10 筆極端測資並確保通過（2 小時）
- 專案練習：以同法為另一題建立基線並用於對照（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可生成正確最短回文
- 程式碼品質（30%）：結構清晰、命名合理
- 效能優化（20%）：合理使用 StringBuilder
- 創新性（10%）：可擴展為 oracle 的設計

---

## Case #2: 兩版本等價性測試（結果對比）

### Problem Statement（問題陳述）
業務場景：在撰寫效能更佳的新版 Solution 時，希望確保結果與保守版 BasicSolution 完全一致。將兩版實作同時輸入相同資料，比較輸出等價性。
技術挑戰：測資過少，容易誤判「似乎都對」；需要大量資料自動對比。
影響範圍：避免因最佳化導致錯誤結果流入提交/上線。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 新舊演算法差異大，回歸風險高。
2. 官方測資僅 3 筆，覆蓋嚴重不足。
3. 人工比對成本高且易疏漏。
深層原因：
- 架構層面：缺少內建「雙實作」對比點。
- 技術層面：未建立隨機資料產生器與對照測試。
- 流程層面：測試仍偏重少量手工案例。

### Solution Design（解決方案設計）
解決策略：在單元測試中同時呼叫新舊兩版，對比結果等價性；搭配隨機資料生成器，快速擴大覆蓋。

實施步驟：
1. 建立測試宿主
- 實作細節：SubmitHost（新）與 CheckingHost（舊）並存
- 所需資源：MSTest
- 預估時間：0.5 小時
2. 撰寫等價性測試
- 實作細節：隨機生成多組字串，Assert.AreEqual 對比
- 所需資源：Random、MSTest
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
[TestClass]
public class UnitTest1
{
    private Solution SubmitHost = null;      // 新版
    private BasicSolution CheckingHost = null; // 舊版
    private const string text = "abcdefghijklmnopqrstuvwxyz";
    private static Random rnd = new Random();

    [TestInitialize]
    public void Init()
    {
        this.SubmitHost = new Solution();
        this.CheckingHost = new BasicSolution();
    }

    [TestMethod]
    public void CheckingTestCases()
    {
        foreach (string randomtext in GenRandomText(10000, 100))
        {
            Assert.AreEqual(
                this.SubmitHost.ShortestPalindrome(randomtext),
                this.CheckingHost.ShortestPalindrome(randomtext));
        }
    }

    private static IEnumerable<string> GenRandomText(int maxlength, int run)
    {
        for (int index = 0; index < run; index++)
        {
            var sb = new StringBuilder();
            for (int i = 0; i < rnd.Next(maxlength + 1); i++)
            {
                sb.Append(text[rnd.Next(26)]);
            }
            yield return sb.ToString();
        }
    }
}
```
實際案例：100 組隨機長度 ≤ 10000 的字串，逐筆比對新舊結果。
實作環境：C# / .NET / MSTest。
實測數據：
改善前：僅 3 組官方測資。
改善後：可動態擴增至 100～10000 組隨機測資。
改善幅度：測資量 +97～+9997 組（相較 3 組）。

Learning Points（學習要點）
核心知識點：
- 兩版本等價性測試（dual-implementation oracle）
- 單元測試動態資料供應
- property-based 測試思維
技能要求：
- 必備技能：單元測試框架、隨機資料產生
- 進階技能：測試資料分佈設計、可重現隨機性
延伸思考：
- 套用到 refactor/微服務行為一致性驗證
- 風險：舊版若錯誤，將導致錯誤等價
- 優化：加入額外性質檢查（例如回文字性）
Practice Exercise（練習題）
- 基礎：把 run 從 100 改 1000，觀察測試時間（30 分）
- 進階：加入固定種子以利重現（2 小時）
- 專案：把等價性測試接進 CI（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：兩版結果完全一致
- 程式碼品質（30%）：測試可維護、無 magic number
- 效能優化（20%）：可控制執行時間
- 創新性（10%）：分佈/策略多樣化

---

## Case #3: 隨機測試資料產生器（覆蓋擴張引擎）

### Problem Statement（問題陳述）
業務場景：現有測資不足，需快速擴大輸入空間涵蓋率；針對字串題，需控制長度與字符集。
技術挑戰：需兼顧長度分佈、字符分佈與極端值。
影響範圍：直接影響缺陷暴露率與回歸測試充足性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 官方測資量少且分佈不明。
2. 人工設計測資耗時且偏見重。
3. 無可重用的隨機資料產生工具。
深層原因：
- 架構層面：測試資料層未模組化。
- 技術層面：缺少可參數化的 generator。
- 流程層面：測試資料生成未自動化。

### Solution Design（解決方案設計）
解決策略：實作可參數化的字串隨機生成器，支援長度上限、字母表、迭代次數，與等價性測試結合。

實施步驟：
1. 實作 Generator
- 實作細節：可設定 maxlength、run、字符集
- 所需資源：C#
- 預估時間：0.5 小時
2. 接進單元測試
- 實作細節：foreach 餵入兩版對比
- 所需資源：MSTest
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
// 可重用隨機字串產生器
public static IEnumerable<string> GenRandomText(string alphabet, int maxLen, int count, int? seed = null)
{
    var rnd = seed.HasValue ? new Random(seed.Value) : new Random();
    for (int k = 0; k < count; k++)
    {
        int len = rnd.Next(maxLen + 1);
        var sb = new StringBuilder(len);
        for (int i = 0; i < len; i++) sb.Append(alphabet[rnd.Next(alphabet.Length)]);
        yield return sb.ToString();
    }
}
```
實際案例：以 a-z、maxLen=10000、count=100 產生測資。
實作環境：C# / MSTest。
實測數據：
改善前：僅 3 筆。
改善後：一鍵生成 100～10000 筆。
改善幅度：資料覆蓋大幅增加（+97～+9997 筆）。

Learning Points（學習要點）
核心知識點：
- 測試資料生成與參數化
- 可重現隨機性（seed）
- 資料分佈與極端值
技能要求：
- 必備技能：C#、集合、隨機
- 進階技能：資料分佈設計（均勻/偏態）
延伸思考：
- 可引入 property-based framework（FsCheck 等）
- 風險：非可重現導致 flakiness
- 優化：紀錄隨機種子以重現缺陷
Practice Exercise（練習題）
- 基礎：加入大寫字母與數字集合（30 分）
- 進階：加入固定 seed 重現失敗案例（2 小時）
- 專案：包成可重用測試工具庫（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可生成指定分佈與長度
- 程式碼品質（30%）：API 清楚、易用
- 效能優化（20%）：大量資料時無明顯瓶頸
- 創新性（10%）：支持多分佈或策略

---

## Case #4: 以保守版離線產生「靜態測資 + 正解」（CSV）

### Problem Statement（問題陳述）
業務場景：新版開發期間，不希望每次測試都耗時生成大量隨機資料；希望批次生成靜態測資與標準答案，供之後快速回歸。
技術挑戰：需將「保守版」結果落成檔案，並能被單元測試讀取。
影響範圍：縮短回歸測試時間、提升重複利用率。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 大量動態測試耗時。
2. 缺乏可重用、固定的測資檔。
3. 測試資料管理混亂。
深層原因：
- 架構層面：未建立資料提供層（data source）
- 技術層面：未實作生成器輸出 CSV/XML
- 流程層面：缺少靜態回歸集

### Solution Design（解決方案設計）
解決策略：撰寫 console 工具，以 BasicSolution 計算 expected，輸出 CSV（input, expected），單元測試讀檔驗證新版結果。

實施步驟：
1. 產生器工具
- 實作細節：調用 BasicSolution 計算 expected，寫入 CSV
- 所需資源：C# Console
- 預估時間：1 小時
2. 單元測試讀檔
- 實作細節：逐列讀取 CSV，比對新版 output 與 expected
- 所需資源：MSTest/NUnit
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
// Console：生成 100 筆靜態測資
static void Main()
{
    var basic = new BasicSolution();
    using var sw = new StreamWriter("cases.csv");
    sw.WriteLine("input,expected");

    foreach (var s in GenRandomText("abcdefghijklmnopqrstuvwxyz", 1000, 100, seed: 42))
    {
        var expected = basic.ShortestPalindrome(s).Replace(",", "\\,"); // 簡單 escape
        var inputEsc = s.Replace(",", "\\,");
        sw.WriteLine($"{inputEsc},{expected}");
    }
}
```
實際案例：100 筆靜態測資持久化，供長期回歸。
實作環境：C# Console / File IO。
實測數據：
改善前：每次測試重新生成資料（不穩定、耗時）。
改善後：固定 100 筆靜態測資常態化使用。
改善幅度：測試時間穩定、可重現性提升（靜態化）。

Learning Points（學習要點）
核心知識點：
- 離線 oracle 生成
- 測試資料管理與重現
- 測試與生產資料隔離
技能要求：
- 必備技能：檔案處理、CSV
- 進階技能：資料 escape/UTF-8 處理
延伸思考：
- 可用 JSONL、Parquet 等格式
- 風險：靜態集過時；需定期再生
- 優化：版本標記與雜湊校驗
Practice Exercise（練習題）
- 基礎：把 100 改 1000 筆（30 分）
- 進階：加入極端資料的專屬區段（2 小時）
- 專案：加上簡單 schema 與 metadata（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可生成可讀取的資料集
- 程式碼品質（30%）：清楚的欄位與 escape
- 效能優化（20%）：大量資料輸出效率
- 創新性（10%）：格式/工具通用性

---

## Case #5: 極端/邊界案例的「靜態測試」增補

### Problem Statement（問題陳述）
業務場景：隨機測試往往難以涵蓋特定極端狀況（超長、全相同字元、僅一處差異等），需人工挑選并納入測試。
技術挑戰：如何系統化納入、高可讀且能長期保留。
影響範圍：顯著提升對 corner case 的防禦力。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 隨機測試不保證覆蓋特定模式。
2. 極端案例人工維護成本高。
3. 缺少對應 expected。
深層原因：
- 架構層面：缺少專用極端資料清單
- 技術層面：未以保守版自動產 expected
- 流程層面：無將極端資料納入回歸機制

### Solution Design（解決方案設計）
解決策略：維護極端輸入清單，離線用 BasicSolution 填 expected，與隨機測試並行。

實施步驟：
1. 建立 ExtremeCases 檔
- 實作細節：列出模板如 1000 個一樣字元、交替字元等
- 所需資源：CSV/JSON
- 預估時間：0.5 小時
2. 以保守版填 expected
- 實作細節：批次運算 expected，回寫檔案
- 所需資源：Console 工具
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
// 測試中載入極端案例
[TestMethod]
public void ExtremeCases()
{
    var submit = new Solution();
    var basic = new BasicSolution();
    var extremeInputs = new[] {
        new string('a', 1000),
        new string('a', 999) + "b",
        "ab".PadRight(1000, 'a')
    };

    foreach (var input in extremeInputs)
    {
        Assert.AreEqual(
            basic.ShortestPalindrome(input),
            submit.ShortestPalindrome(input));
    }
}
```
實際案例：超長、全相同、單點不同等案例加入回歸。
實作環境：C# / MSTest。
實測數據：
改善前：極端案例未覆蓋。
改善後：固定納入多類極端案例（至少 3 類以上）。
改善幅度：corner 覆蓋率顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- 極端測試的重要性
- 模式化輸入設計
- 與 oracle 結合生成 expected
技能要求：
- 必備技能：C# 字串操作
- 進階技能：極端輸入模式設計
延伸思考：
- 可引入模糊測試（fuzz）
- 風險：極端輸入過於集中、不具代表性
- 優化：將極端案例分級與覆蓋報告
Practice Exercise（練習題）
- 基礎：新增 5 類極端模式（30 分）
- 進階：把極端清單改由檔案讀取（2 小時）
- 專案：製作可視化的覆蓋報告（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可穩定重現極端場景
- 程式碼品質（30%）：清楚命名與註解
- 效能優化（20%）：長字串處理效率
- 創新性（10%）：極端模式設計巧思

---

## Case #6: 有界窮舉（小範圍全覆蓋）檢驗

### Problem Statement（問題陳述）
業務場景：在小範圍（例如長度 ≤ 3 或 4）的輸入上做完全窮舉，以確定某些邏輯在該範圍內無誤。
技術挑戰：需要產生全部組合並防止爆炸性增長。
影響範圍：小範圍內的完全信心，補強隨機測試盲點。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 隨機測試仍可能漏掉關鍵短字串模式。
2. 無窮舉工具導致難以做全覆蓋。
3. 粗心忽略小長度邊界。
深層原因：
- 架構層面：無輸入空間建模
- 技術層面：無生成器支援笛卡兒積
- 流程層面：缺乏「局部全覆蓋」思路

### Solution Design（解決方案設計）
解決策略：限制字元集與長度，窮舉所有字串，逐一比對新舊結果，形成局部的 100% 覆蓋。

實施步驟：
1. 產生器（遞迴/迭代）
- 實作細節：生成長度 0..N 的所有字串
- 所需資源：C#
- 預估時間：1 小時
2. 等價性驗證
- 實作細節：逐一比對新舊輸出
- 所需資源：MSTest
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
IEnumerable<string> EnumerateAll(string alphabet, int maxLen)
{
    yield return string.Empty;
    foreach (int len in Enumerable.Range(1, maxLen))
    {
        foreach (var s in EnumerateLen(alphabet, len))
            yield return s;
    }

    IEnumerable<string> EnumerateLen(string a, int len)
    {
        if (len == 0) { yield return ""; yield break; }
        foreach (var prefix in EnumerateLen(a, len - 1))
            foreach (char c in a)
                yield return prefix + c;
    }
}
```
實際案例：alphabet = "ab", maxLen = 4 → 1 + 2 + 4 + 8 + 16 = 31 組全覆蓋。
實作環境：C#。
實測數據：
改善前：短字串模式覆蓋不明。
改善後：小範圍 100% 覆蓋可證。
改善幅度：短長度覆蓋率從不明到 100%。

Learning Points（學習要點）
核心知識點：
- 有界輸入空間建模
- 全覆蓋與隨機測試互補
- 組合爆炸與界限控制
技能要求：
- 必備技能：遞迴、迭代
- 進階技能：記憶化/迭代優化
延伸思考：
- 大範圍不適用，需與隨機/極端混用
- 風險：過度依賴小範圍覆蓋
- 優化：按風險挑選 alphabet 與 N
Practice Exercise（練習題）
- 基礎：實作 maxLen=3 的窮舉（30 分）
- 進階：加入進度回報與中斷控制（2 小時）
- 專案：與等價性測試整合自動跑（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：生成正確組合
- 程式碼品質（30%）：無重複、易讀
- 效能優化（20%）：合理控制時間/空間
- 創新性（10%）：多策略生成功能

---

## Case #7: 在主程式植入 Fail-Fast 斷言（Runtime 驗證）

### Problem Statement（問題陳述）
業務場景：單元測試屬黑箱；實際執行時仍可能出現不可預期狀態，需在 runtime 立即偵測並中止，降低修復成本。
技術挑戰：如何不影響正式版效能，又能在開發時 Fail-Fast。
影響範圍：大幅縮小偵錯範圍，快速定位。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 僅靠測試難涵蓋所有執行路徑。
2. 錯誤延遲暴露，成本高。
3. 正式版不允許頻繁崩潰。
深層原因：
- 架構層面：缺乏 runtime 驗證點
- 技術層面：未使用條件式編譯隱去斷言
- 流程層面：缺乏 Fail-Fast 概念

### Solution Design（解決方案設計）
解決策略：以條件式編譯搭配自訂斷言，在 LOCAL_DEBUG 模式下啟用，正式版剔除；將關鍵不變量全數檢查。

實施步驟：
1. 設定條件式編譯
- 實作細節：#define LOCAL_DEBUG / #if (LOCAL_DEBUG)
- 所需資源：C# 編譯器
- 預估時間：0.5 小時
2. 斷言點佈設
- 實作細節：在狀態轉換前後插斷言
- 所需資源：程式碼審視
- 預估時間：1-2 小時

關鍵程式碼/設定：
```csharp
#if (LOCAL_DEBUG)
    if (unexpectedCondition) throw new Exception("Fail-Fast: invariant broken");
// 說明：在開發/測試環境，滿足條件即中止，快速定位。
#endif
```
實際案例：ZumaGame 中對統計與實際資料一致性的斷言（見 Case #8）。
實作環境：C#。
實測數據：
改善前：錯誤可能在多步後才顯現，定位困難。
改善後：一破壞不變量立即中止；正式版 overhead ≈ 0。
改善幅度：錯誤定位從事後轉為即時。

Learning Points（學習要點）
核心知識點：
- Fail-Fast 思維
- 斷言與條件式編譯
- 黑箱/白箱測試互補
技能要求：
- 必備技能：C# 前處理器
- 進階技能：不變量設計與驗證點選擇
延伸思考：
- 可用 Guard Clauses 提升可讀性
- 風險：斷言條件不當造成誤報
- 優化：斷言訊息含上下文
Practice Exercise（練習題）
- 基礎：在 2 個關鍵點加入斷言（30 分）
- 進階：斷言訊息帶入關鍵狀態（2 小時）
- 專案：制訂斷言佈設清單（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：可即時攔截異常狀態
- 程式碼品質（30%）：斷言語義清楚
- 效能優化（20%）：正式版剔除無 overhead
- 創新性（10%）：斷言策略完整度

---

## Case #8: 統計資訊 vs 實際資料一致性斷言（ZumaGame Invariant）

### Problem Statement（問題陳述）
業務場景：ZumaGame 需要依統計資料（顏色計數）做決策；若統計與實際 board 不一致，很難判斷是 bug 還是演算法問題。
技術挑戰：在每個可能影響統計的操作點同步驗證一致性。
影響範圍：顯著縮小偵錯範圍，快速區分類型。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 多處維護統計，易不同步。
2. 錯誤延後顯現，難定位。
3. 無集中一致性檢查。
深層原因：
- 架構層面：狀態/統計分離但未保證一致
- 技術層面：缺少 invariant 檢查函式
- 流程層面：未形成「每步皆驗」習慣

### Solution Design（解決方案設計）
解決策略：實作 AssertStatisticData()，在 LOCAL_DEBUG 下逐步檢查 board 聚合計數與統計表一致，若不一致立即 throw。

實施步驟：
1. 撰寫 invariant 檢查
- 實作細節：遍歷 board 聚合計數，與統計相等
- 所需資源：C#
- 預估時間：1 小時
2. 佈設檢查點
- 實作細節：於每次修改前後呼叫
- 所需資源：程式碼審視
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
private void AssertStatisticData()
{
#if (LOCAL_DEBUG)
    var stat = new Dictionary<char, int>() { { 'R', 0 }, { 'Y', 0 }, { 'B', 0 }, { 'G', 0 }, { 'W', 0 } };
    foreach (var n in this.CurrentBoard) stat[n.Color] += n.Count;
    foreach (char c in new[] { 'R', 'Y', 'B', 'G', 'W' })
        if (stat[c] != this.CurrentBoardStatistic[c]) throw new Exception($"Stat mismatch for {c}");
#endif
}
```
實際案例：每次步驟執行前後都呼叫 AssertStatisticData。
實作環境：C#。
實測數據：
改善前：問題來源不明（程式 bug 或演算法不佳）。
改善後：一旦不一致立即攔截並定位到最近變更點。
改善幅度：偵錯範圍縮小到單步。

Learning Points（學習要點）
核心知識點：
- Invariant 設計
- 聚合 vs 單一來源一致性
- 前後置檢查
技能要求：
- 必備技能：集合操作、字典
- 進階技能：狀態同步設計
延伸思考：
- 可擴至多種統計與衍生資料
- 風險：漏掉檢查點
- 優化：自動化檢查點插入或 AOP
Practice Exercise（練習題）
- 基礎：為另一種統計新增檢查（30 分）
- 進階：統一 invariant 檢查入口（2 小時）
- 專案：做成可重用 invariant framework（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：不一致即中止
- 程式碼品質（30%）：簡潔可讀
- 效能優化（20%）：正式版無負擔
- 創新性（10%）：檢查點策略設計

---

## Case #9: 步驟前置條件檢查（Precondition Guards）

### Problem Statement（問題陳述）
業務場景：ZumaGame 執行一步行為時，若位置超界或手牌不足，應立即中止而非繼續執行，避免污染後續狀態。
技術挑戰：在正確的位置插入 guard，並不影響正式版。
影響範圍：避免非法狀態傳播，提升穩定性。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 缺少 precondition 檢查。
2. 非法狀態在多步後才顯現。
3. 例外無上下文，難定位。
深層原因：
- 架構層面：狀態轉換缺少契約
- 技術層面：未使用 guard/契約式程式設計
- 流程層面：未規範前置條件檢查

### Solution Design（解決方案設計）
解決策略：在 ApplyStep 的開頭插入條件檢查（位置上界、手牌數量），LOCAL_DEBUG 下直接拋例外。

實施步驟：
1. 分析前置條件
- 實作細節：索引界限、資源是否足夠
- 所需資源：程式碼走查
- 預估時間：0.5 小時
2. Guard 實作
- 實作細節：條件不符直接 throw
- 所需資源：C#
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
private void ApplyStep(GameStep step)
{
#if (LOCAL_DEBUG)
    if (this.CurrentBoard.Count <= step.Position) throw new Exception("Position OOB");
    if (this.CurrentHand[step.Color] == 0) throw new Exception("No card in hand");
#endif

    this.AssertStatisticData(); // 前置一致性檢查

    if (this.CurrentBoard[step.Position].Color == step.Color)
        this.CurrentBoard[step.Position].Count++;

    // ... 其他邏輯

    this.AssertStatisticData(); // 後置一致性檢查
}
```
實際案例：ZumaGame 一步執行前後的 guard 與 invariant。
實作環境：C#。
實測數據：
改善前：非法狀態悄悄擴散。
改善後：立即攔截，定位清晰。
改善幅度：非法狀態傳播時間→0。

Learning Points（學習要點）
核心知識點：
- Precondition/Guard Clause
- 前置/後置條件
- 契約式程式設計（DbC）
技能要求：
- 必備技能：例外處理
- 進階技能：錯誤訊息與上下文
延伸思考：
- 可抽象為 Guard utility
- 風險：誤判合法狀態
- 優化：錯誤訊息攜帶 step、board 摘要
Practice Exercise（練習題）
- 基礎：新增 2 個 guard（30 分）
- 進階：封裝 Guard 幫助器（2 小時）
- 專案：導入到另一項目（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：非法即攔截
- 程式碼品質（30%）：Guard 清晰靠前
- 效能優化（20%）：正式版無負擔
- 創新性（10%）：Guard 可重用性

---

## Case #10: Debug 友善 ToString + 條件式編譯

### Problem Statement（問題陳述）
業務場景：Debug 時需快速看懂複合物件狀態；正式提交（如 LeetCode）不希望攜帶額外負擔。
技術挑戰：以最小代價提供高可讀輸出，且不進入正式版。
影響範圍：大幅提升除錯效率、避免提交冗餘碼。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 頻繁展開物件樹耗時。
2. 正式版不需 debug 字串生成。
3. 平台編譯模式未知（例如 LeetCode）。
深層原因：
- 架構層面：Debug 觀測點缺乏
- 技術層面：未使用條件式編譯剔除
- 流程層面：Debug 輸出未標準化

### Solution Design（解決方案設計）
解決策略：覆寫 ToString，並用 #if(LOCAL_DEBUG) 包裹；自定義符號確保在未知編譯環境不會啟用。

實施步驟：
1. ToString 覆寫
- 實作細節：輸出關鍵狀態摘要
- 所需資源：C#
- 預估時間：0.5 小時
2. 條件式編譯
- 實作細節：#define LOCAL_DEBUG 控制
- 所需資源：C# 前處理器
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
#if (LOCAL_DEBUG)
public override string ToString()
{
    var sb = new StringBuilder();
    foreach (var n in this.CurrentBoard) sb.Append(n.ToString());
    return sb.ToString();
}
#endif
```
實際案例：在 VS Debugger watch 直接看到摘要。
實作環境：C#，Visual Studio。
實測數據：
改善前：逐屬性展開、成本高。
改善後：一行摘要觀測；正式版 0 overhead。
改善幅度：觀測步驟數顯著下降（定性）。

Learning Points（學習要點）
核心知識點：
- Debug 可觀測性設計
- 條件式編譯與平台差異
- 提交前去冗策略
技能要求：
- 必備技能：C#、字串處理
- 進階技能：摘要設計與可讀性
延伸思考：
- 可增加 DebuggerDisplay 屬性
- 風險：ToString 太昂貴
- 優化：限制輸出長度
Practice Exercise（練習題）
- 基礎：為 1 個類增加 ToString（30 分）
- 進階：加入 DebuggerDisplay（2 小時）
- 專案：建立 Debug 輸出規範（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：輸出關鍵狀態
- 程式碼品質（30%）：無洩漏正式版
- 效能優化（20%）：低成本輸出
- 創新性（10%）：可讀性設計

---

## Case #11: 自訂編譯符號隔離 Debug/Release 行為

### Problem Statement（問題陳述）
業務場景：提交到未知編譯環境（如 LeetCode）時，無法確定是否是 Debug/Release；需保證除錯碼一定不會被編譯進去。
技術挑戰：使用自定編譯符號，避免依賴平台的 Debug/Release。
影響範圍：防止性能/行為污染，確保提交純淨。
複雜度評級：低

### Root Cause Analysis（根因分析）
直接原因：
1. 平台可能不是 Debug/Release 的預期設定。
2. 斷言/ToString 若進入正式版會有成本與風險。
3. 手動刪除易出錯。
深層原因：
- 架構層面：未統一編譯符號
- 技術層面：前處理器用法不足
- 流程層面：提交前清理缺流程化

### Solution Design（解決方案設計）
解決策略：統一使用 #define LOCAL_DEBUG，凡 Debug 專用代碼一律在 #if(LOCAL_DEBUG) 內；提交環境不定義此符號，自動剔除。

實施步驟：
1. 宣告符號
- 實作細節：檔頭 #define LOCAL_DEBUG（本機）
- 所需資源：C#
- 預估時間：0.1 小時
2. 包裹 Debug 專用段落
- 實作細節：所有斷言/ToString/調試碼必包裹
- 所需資源：程式走查
- 預估時間：0.5 小時

關鍵程式碼/設定：
```csharp
#define LOCAL_DEBUG

// ... 檔案內所有調試段落
#if (LOCAL_DEBUG)
// Debug only code
#endif
```
實際案例：LeetCode 提交端未定義該符號，調試碼一律剔除。
實作環境：C#。
實測數據：
改善前：可能把調試碼帶入。
改善後：提交端零調試碼、零 overhead。
改善幅度：正式版多餘碼→0。

Learning Points（學習要點）
核心知識點：
- 自訂編譯符號
- 可攜性與提交純淨
- 調試碼治理
技能要求：
- 必備技能：前處理器
- 進階技能：建置管線整合
延伸思考：
- 可用 csproj 設定條件化符號
- 風險：遺漏包裹
- 優化：靜態分析檢查
Practice Exercise（練習題）
- 基礎：將 2 處調試碼包裹（30 分）
- 進階：csproj 設定多組符號（2 小時）
- 專案：提交前自動檢查（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：正式版無調試碼
- 程式碼品質（30%）：一致使用符號
- 效能優化（20%）：0 overhead
- 創新性（10%）：工具化檢查

---

## Case #12: 以保守版作為「驗算」的廣義實踐（多策略驗證）

### Problem Statement（問題陳述）
業務場景：僅用同法重算無法避免邏輯錯誤；需用另一套方法（保守版）驗算新版結果。
技術挑戰：新版與舊版路徑差異大，但輸出需一致。
影響範圍：大幅降低最佳化帶來的風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 新版路徑複雜，肉眼難審。
2. 傳統「重算」無法避免邏輯性錯誤。
3. 無第二算法來源。
深層原因：
- 架構層面：缺少平行實作
- 技術層面：無統一對比框架
- 流程層面：驗算過程未自動化

### Solution Design（解決方案設計）
解決策略：以保守版作「可敬的對手」，雙實作結果對比 + 隨機/極端/窮舉三路測試策略，形成廣義驗算。

實施步驟：
1. 平行實作對比
- 實作細節：建立對比測試與報告
- 所需資源：MSTest
- 預估時間：1 小時
2. 三路測試策略
- 實作細節：隨機、極端、有界窮舉
- 所需資源：測試工具集
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
// 統一驗算入口（示意）
void VerifyWithOracle(string input)
{
    var got = new Solution().ShortestPalindrome(input);
    var expect = new BasicSolution().ShortestPalindrome(input);
    Assert.AreEqual(expect, got, $"Mismatch on input: {input}");
}
```
實際案例：多策略驗算 Shortest Palindrome。
實作環境：C# / MSTest。
實測數據：
改善前：單一策略、信心不足。
改善後：三路並行，錯誤暴露率提高。
改善幅度：缺陷偵測能力顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- 多策略驗證
- 不同算法路徑的對比
- 測試分層
技能要求：
- 必備技能：單元測試設計
- 進階技能：測試策略編排
延伸思考：
- 可加入 property 斷言（結果為回文、最短性）
- 風險：oracle 錯誤
- 優化：多個 oracle 交叉驗證
Practice Exercise（練習題）
- 基礎：封裝 VerifyWithOracle（30 分）
- 進階：加入回文字性 property 檢查（2 小時）
- 專案：產出統計報告（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：驗算全面
- 程式碼品質（30%）：封裝良好
- 效能優化（20%）：批次驗證效率
- 創新性（10%）：多策略整合

---

## Case #13: 性能最佳化的「安全護欄」流程（效能 vs 正確）

### Problem Statement（問題陳述）
業務場景：希望新版「效率好上好幾倍」，但不能破壞正確性。需要以科學方法逐步最佳化並有護欄。
技術挑戰：如何量測效能且同時驗證等價性。
影響範圍：避免效能優化導致錯誤上線。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 最佳化往往牽涉資料結構/演算法重構。
2. 測試覆蓋不足導致錯誤被放大。
3. 缺少效能量測基準。
深層原因：
- 架構層面：缺少效能實驗場
- 技術層面：未建立基準資料集
- 流程層面：未把等價性當作 gate

### Solution Design（解決方案設計）
解決策略：先以等價性測試守門，通過後再進行微基準測試；將效率成果以固定資料集量測。

實施步驟：
1. 構建固定資料集
- 實作細節：100/1000 筆隨機 + 極端集合
- 所需資源：Case 3/4
- 預估時間：1 小時
2. 等價性 Gate
- 實作細節：新舊結果完全一致方可進入效能量測
- 所需資源：MSTest
- 預估時間：0.5 小時
3. 微基準測試
- 實作細節：Stopwatch 量測平均/分位
- 所需資源：C#
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
var sw = Stopwatch.StartNew();
foreach (var s in dataset) new Solution().ShortestPalindrome(s);
sw.Stop();
Console.WriteLine($"Elapsed: {sw.ElapsedMilliseconds} ms");
// 先通過等價性再量測時間
```
實際案例：以 100 筆長度≤10000 字串做時間對比。
實作環境：C#。
實測數據：
改善前：無效能基準。
改善後：建立固定資料集與量測流程。
改善幅度：可量化改進幅度（依實測）。

Learning Points（學習要點）
核心知識點：
- 先正確、後效能
- 微基準測試
- Gate 化流程
技能要求：
- 必備技能：時間量測
- 進階技能：分位數統計
延伸思考：
- 可用 BenchmarkDotNet
- 風險：JIT/GC 影響需預熱
- 優化：Warmup、多次迭代
Practice Exercise（練習題）
- 基礎：加入 warmup（30 分）
- 進階：量測 p95（2 小時）
- 專案：報表自動化（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：等價性優先
- 程式碼品質（30%）：量測可信
- 效能優化（20%）：可重現結果
- 創新性（10%）：量測方法設計

---

## Case #14: 將單元測試精神延伸至 Runtime（運行期驗證）

### Problem Statement（問題陳述）
業務場景：不少問題只有在真實運行（資料量、狀態組合）才會出現；需把測試精神延伸到運行期。
技術挑戰：在不中斷使用者體驗前提下，最大化檢測能力。
影響範圍：提高生產環境的問題可見性與可追溯性。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 測試環境難以完全模擬生產。
2. 黑箱測試觸及不到內部狀態。
3. 錯誤訊息粒度低。
深層原因：
- 架構層面：缺乏運行期驗證點與遙測
- 技術層面：無斷言/不變量在運行期的變體
- 流程層面：無運行期快速回饋機制

### Solution Design（解決方案設計）
解決策略：以條件式編譯或特性開關，將斷言/不變量、輔助輸出在指定環境（如內部測試）啟用；生產環境用軟性警告與遙測替代硬中止。

實施步驟：
1. 環境分級
- 實作細節：區分 DEV/TEST/PROD 行為
- 所需資源：設定管理
- 預估時間：1 小時
2. 驗證點設計
- 實作細節：PROD 改為警示+記錄上下文
- 所需資源：Logging/Tracing
- 預估時間：2 小時

關鍵程式碼/設定：
```csharp
if (env.IsProd)
{
    if (!invariantOk) logger.Warn("Invariant broken: {context}");
}
else // Dev/Test
{
#if (LOCAL_DEBUG)
    if (!invariantOk) throw new Exception("Fail-Fast invariant");
#endif
}
```
實際案例：將斷言在本機/測試環境硬中止，在生產降級為遙測警示。
實作環境：C#，設定管理/日誌框架。
實測數據：
改善前：生產問題難追溯。
改善後：生產可見性提升且不影響可用性。
改善幅度：可觀測性明顯提升（定性）。

Learning Points（學習要點）
核心知識點：
- 運行期驗證設計
- 特性開關/環境分級
- 可觀測性
技能要求：
- 必備技能：設定與日誌
- 進階技能：遙測方案
延伸思考：
- 可加入指標與追蹤（trace）
- 風險：誤報造成警報疲勞
- 優化：採樣與頻率控制
Practice Exercise（練習題）
- 基礎：引入 env 開關（30 分）
- 進階：日誌帶上下文（2 小時）
- 專案：與 APM 整合（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：不同環境不同策略
- 程式碼品質（30%）：配置清晰
- 效能優化（20%）：生產低成本
- 創新性（10%）：可觀測性設計

---

## Case #15: 微服務切分重構的雙版本對比（行為一致性守門）

### Problem Statement（問題陳述）
業務場景：將單體服務切割成多個微服務，需確保外部可見行為不變；在重構過程中比對新舊行為。
技術挑戰：如何在不影響使用者的情況下比較結果一致性。
影響範圍：防止重構導致功能偏差。
複雜度評級：高

### Root Cause Analysis（根因分析）
直接原因：
1. 重構幅度大、依賴多。
2. 無完整既有測試。
3. 上線前缺乏行為一致性驗證。
深層原因：
- 架構層面：缺少 shadow/canary 管道
- 技術層面：未建立「雙寫/雙算」比對機制
- 流程層面：無灰度驗證流程

### Solution Design（解決方案設計）
解決策略：在流量鏡像或影子請求（shadow）下，同時對舊與新服務計算，離線比對結果；差異則告警與回溯。

實施步驟：
1. 鏡像/影子請求
- 實作細節：複製請求到新舊服務
- 所需資源：API Gateway/Service Mesh
- 預估時間：2-3 天
2. 離線對比與報告
- 實作細節：結果持久化、差異比對
- 所需資源：資料庫/比對器
- 預估時間：1-2 天

關鍵程式碼/設定：
```csharp
// 伺服器端示意：雙路調用與比對
var oldRes = await OldService.HandleAsync(req);
var newRes = await NewService.HandleAsync(req);
if (!Equals(oldRes, newRes))
    logger.Error("Behavior diff: {reqId}", req.Id); // 生產降級為記錄
```
實際案例：作者提及用此法輔助微服務重構，保證不影響可見結果。
實作環境：微服務基礎設施（Gateway/Mesh/Log）。
實測數據：
改善前：無一致性保障。
改善後：新舊行為差異可發現、可追蹤。
改善幅度：一致性信心顯著提升（定性）。

Learning Points（學習要點）
核心知識點：
- Shadow traffic/雙算對比
- 行為一致性驗證
- 重構風險控制
技能要求：
- 必備技能：API 基礎、日誌
- 進階技能：Gateway/Mesh 配置
延伸思考：
- 可擴展到資料寫入（雙寫）
- 風險：隱私/合規與成本
- 優化：抽樣與壓力控制
Practice Exercise（練習題）
- 基礎：做本機雙路對比 PoC（30 分）
- 進階：加上持久化差異報告（2 小時）
- 專案：在預備環境導入影子流量（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：差異可發現
- 程式碼品質（30%）：對比邏輯清晰
- 效能優化（20%）：低侵入
- 創新性（10%）：灰度策略

---

## Case #16: 以性質（property）加強結果驗證（回文 + 最短性）

### Problem Statement（問題陳述）
業務場景：即使兩版等價，若 oracle 本身錯誤仍無法保證正確；可用通用性質補強（結果必為回文、且最短）。
技術挑戰：如何在不昂貴的情況下驗證性質。
影響範圍：提升驗證嚴密度，降低 oracle 風險。
複雜度評級：中

### Root Cause Analysis（根因分析）
直接原因：
1. 單一 oracle 可能失誤。
2. 缺乏對通用性質的檢查。
3. 性質驗證成本未知。
深層原因：
- 架構層面：測試僅限等價對比
- 技術層面：無性質檢查輔助
- 流程層面：缺少「雙保險」驗證

### Solution Design（解決方案設計）
解決策略：在 LOCAL_DEBUG 下加入性質斷言：結果為回文；如果砍掉頭部的回文部分以外，剩餘部分皆最小反轉前置。

實施步驟：
1. 回文字性檢查
- 實作細節：雙指針對頭尾
- 所需資源：C#
- 預估時間：0.5 小時
2. 最短性檢查（簡化）
- 實作細節：確認結果由原字串加上某段反轉前置構成
- 所需資源：C#
- 預估時間：1 小時

關鍵程式碼/設定：
```csharp
#if (LOCAL_DEBUG)
bool IsPalindrome(string s)
{
    int i = 0, j = s.Length - 1;
    while (i < j) if (s[i++] != s[j--]) return false;
    return true;
}

void AssertPalindromeProperties(string input, string output)
{
    if (!IsPalindrome(output)) throw new Exception("Not a palindrome");
    if (!output.EndsWith(input)) throw new Exception("Must end with original input");
    // 更嚴格的最短性可藉由比較所有候選頭回文長度，但成本較高
}
#endif
```
實際案例：在等價性測試後再加性質檢查。
實作環境：C#。
實測數據：
改善前：僅等價性檢查。
改善後：性質檢查雙保險。
改善幅度：驗證嚴密度提升（定性）。

Learning Points（學習要點）
核心知識點：
- Property-based 驗證
- 性質 vs 例舉
- 成本與價值平衡
技能要求：
- 必備技能：基礎字串與邏輯
- 進階技能：設計可檢性質
延伸思考：
- 可接入 FsCheck
- 風險：最短性完整驗證成本高
- 優化：用 oracle + 性質綜合
Practice Exercise（練習題）
- 基礎：加入 IsPalindrome 驗證（30 分）
- 進階：嘗試最短性快速檢查（2 小時）
- 專案：實作幾個通用性質（8 小時）
Assessment Criteria（評估標準）
- 功能完整性（40%）：能檢測明顯錯誤
- 程式碼品質（30%）：邏輯簡潔
- 效能優化（20%）：成本可控
- 創新性（10%）：性質設計

---

案例分類
1. 按難度分類
- 入門級（適合初學者）
  - Case 3（隨機生成器）
  - Case 4（離線靜態測資）
  - Case 5（極端案例）
  - Case 10（ToString）
  - Case 11（編譯符號）
- 中級（需要一定基礎）
  - Case 1（保守基線）
  - Case 2（兩版等價測試）
  - Case 6（有界窮舉）
  - Case 7（Fail-Fast）
  - Case 8（統計一致性）
  - Case 9（前置條件）
  - Case 12（廣義驗算）
  - Case 16（性質驗證）
- 高級（需要深厚經驗）
  - Case 13（安全最佳化流程）
  - Case 14（運行期驗證）
  - Case 15（微服務雙版本對比）

2. 按技術領域分類
- 架構設計類
  - Case 12, 13, 14, 15
- 效能優化類
  - Case 1, 13
- 整合開發類
  - Case 2, 4, 5, 6, 15
- 除錯診斷類
  - Case 7, 8, 9, 10, 11, 16
- 安全防護類
  - Case 7, 9, 14（Fail-Fast/Guard 提升穩定性）

3. 按學習目標分類
- 概念理解型
  - Case 1, 7, 12, 14
- 技能練習型
  - Case 3, 4, 5, 6, 10, 11, 16
- 問題解決型
  - Case 2, 8, 9, 13
- 創新應用型
  - Case 15（微服務影子對比）

案例關聯圖（學習路徑建議）
- 入門先學（建立基礎工具與思維）
  1) Case 1（保守基線）
  2) Case 3（隨機生成器）
  3) Case 4（離線靜態測資）
  4) Case 5（極端案例）
  5) Case 6（有界窮舉）
- 強化驗證能力（雙實作與白箱）
  6) Case 2（兩版等價測試）
  7) Case 7（Fail-Fast）
  8) Case 8（統計一致性）
  9) Case 9（前置條件）
  10) Case 10（ToString）
  11) Case 11（編譯符號）
  12) Case 16（性質驗證）
- 進階工程化與上線能力
  13) Case 13（安全最佳化流程）
  14) Case 14（運行期驗證）
  15) Case 15（微服務雙版本對比）
依賴關係：
- Case 2 依賴 Case 1（有 oracle）
- Case 4/5/6/16 與 Case 2 互補（資料與性質）
- Case 7/8/9/10/11 與所有演算法實作交織（白箱驗證）
- Case 13 依賴 Case 2（等價性 gate）
- Case 15 借用 Case 2/14 的對比與運行期驗證思路
完整學習路徑建議：
- 先建立「正確性優先」的基線與資料生成（Case 1,3,4,5,6）
- 再導入雙版本等價測試與白箱斷言（Case 2,7,8,9,10,11,16）
- 最後進入工程化：效能、安全上線與重構（Case 13,14,15）

以上 16 個案例均可直接落地於日常開發、演算法練習與大型系統重構中，形成從「正確性 → 覆蓋 → 白箱 → 效能 → 上線」的完整閉環。