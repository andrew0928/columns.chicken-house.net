---
layout: synthesis
title: "//build/2016 - The Future of C#"
synthesis_type: summary
source_post: /2016/04/09/build2016_csharp7_preview/
redirect_from:
  - /2016/04/09/build2016_csharp7_preview/summary/
postid: 2016-04-09-build2016_csharp7_preview
---

# //build/2016 - The Future of C#

## 摘要提示
- C# 7 核心目標: 以編譯器層級的 syntactic sugar 提升程式碼可讀性與開發效率，且不需新 Runtime 支援。
- 聚焦三大語法: 本文重點解析 Tuples、Record Type、Pattern Matching 的設計動機與實務價值。
- Tuples 回傳多值: 以 tuple literals 讓方法能同時回傳多個強型別值，避免 out 參數與類別樣板程式。
- Record Type 易於建模: 以唯讀屬性的不可變資料型別簡化資料建模，並內建值相等比較與 with 複製更新。
- Pattern Matching 精準分派: 整合型別判斷、轉型與條件過濾，讓分支邏輯更貼近問題本質。
- 語法背後原理: 新語法由編譯器展開為既有 C#/IL 等價碼，主要改善可讀性而非效能。
- OOP vs. Pattern: 多型封裝與 pattern matching 各有場景，應依重用性與資料來源彈性選擇。
- 與 JS/JSON 的影響: 語法演進朝向更容易產生與處理結構化資料，回應大量資料處理需求。
- VS 15 啟用方式: 以條件式編譯符號啟用 C# 7 預覽語法，直接在 VS 15 Preview 體驗。
- 寫作動機與文化: 作者以「語法潔癖」視角剖析設計巧思，補足華文圈少見的語法層討論。

## 全文重點
本文回顧 //Build/2016 的「The Future of C#」場次，聚焦 C# 7 三項關鍵語法：Tuples、Record Type 與 Pattern Matching。作者以「對程式碼優雅與可讀性的堅持」為切入點，說明這些新特性本質上都屬於編譯器可處理的 syntactic sugar，不需新 Runtime 支援，對既有平台相容性高。其技術目的不是追求效能提升，而是讓程式碼更貼近問題表述、減少樣板碼、降低出錯機會，並提升維護與重構效率。

Tuples 讓方法能以簡潔的語法回傳多個強型別的值，既避免 out/ref 參數的冗長，也不必為一次性模型多宣告小型類別；相較泛型 Tuple<T1,T2> 只有 Item1/Item2 的貧乏命名，新語法提供具名欄位，閱讀與維護大幅改善。Record Type 提供不可變、唯讀屬性的資料型別，天然支援值相等比較與 with 語法的局部更新，能用一行聲明取代冗長樣板，特別適合資料查詢結果或 DTO 場景；加上繼承支援，能以低成本建立明確的資料層次。Pattern Matching 則將 is、as/cast 與條件判斷融合，無論用 switch 或 if-else，都能以單一語法同時完成型別比對、轉型、以及屬性條件過濾（透過 when 子句），讓分支邏輯直觀呈現商業規則，避免傳統兩段式判斷與轉型的樣板與潛在例外。

作者進一步以 IL 與反編譯結果說明，這些新語法會在編譯階段被展開為傳統 C# 等價碼：switch 轉為 if-else，pattern matching 轉為 as 轉型加 null 檢查與條件判斷，證實其價值在於可讀性與維護性，而非執行期效能差異。因此，既有可讀性良好的物件導向設計不必為了「新語法」而強行重寫；反之，當資料來源來自資料庫或 JSON、封裝重用性不高時，pattern matching 與 records/tuples 能更有效率地解決問題。

在策動與趨勢上，作者指出 C# 的演進受 JavaScript/JSON 的影響日增：讓程式內建更容易建造與篩選結構化資料的語法，以呼應現代應用對大量資料處理的需求。最後，文章附上在 Visual Studio 15 Preview 啟用 C# 7 語法的方法（以條件式編譯符號開啟），並以個人對語法設計的喜愛作結，強調這些改變能讓程式碼更乾淨、更貼近思考邏輯，對開發者是實質利多。

## 段落重點
### Tuples Literal, 一次傳回多個回傳值
作者從 C 語言 getchar 傳回 int 與 EOF 的經典設計限制談起，指出「只能回傳單一值」的語言表達力不足，迫使 API 在回傳型別、錯誤訊號與副通道（如 out/ref）之間折衷。C# 7 的 Tuples 以 tuple literals（例如 (int Width, int Height)）讓方法自然回傳多個具名強型別欄位，既省去為一次性需求宣告類別的負擔，也避免 out/ref 帶來的可讀性與使用成本。與 .NET 既有的 Tuple<T1,T2> 相比，新語法提供具名欄位（Width、Height），顯著提升可讀性與維護性，避免 Item1/Item2 的語意貧乏。作者推測編譯器會在背後自動生成對應型別（類似匿名型別），執行效能與既有作法等價，差異主要在語法與可讀性層面。除回傳值外，Tuples 也可直接以 literals 建立變數作為輕量封裝，適合在邏輯計算過程傳遞多個相關值，減少臨時資料結構與樣板碼。

### Record Type, 只包含屬性的資料型別
Record Type 被定位為「只有唯讀屬性」的不可變資料型別，用來大幅簡化資料建模的樣板程式。典型情境是從資料庫或查詢結果取得部分欄位，過去若為了強型別常需定義多個近似類別；使用 records 可用一行式宣告（如 class Person(string First, string Last);）自動獲得唯讀屬性、值相等比較（IEquatable<T>）、以及 with 語法的不可變更新（以建立新物件替代修改）。這種設計降低了為資料傳輸與查詢結果建立模型的成本，並天然鼓勵不可變資料結構，有利於並行與推理正確性。Record Type 亦支援繼承，可用於建立清晰的資料階層（例如幾何型別的父子關係），搭配 pattern matching 能在不引入複雜行為封裝的情況下，維持良好的資料結構設計與直觀處理流程。作者強調，syntactic sugar 的好處在於編譯期代碼生成，開發者可專注於語意表達而非樣板細節，維持程式碼整潔與一致性。

### Pattern Matching, 物件的型別判定及比對語法
Pattern Matching 將型別判定、轉型與條件過濾合併為單一語法，支援於 switch 或 if-else 中使用。作者以幾何圖形（Triangle/Rectangle/Square）計算面積加總為例，對比傳統 OOP 多型（以虛擬方法 GetArea）與 pattern matching 分支：在僅需一次性處理、重用性要求低的情境下，pattern matching 能讓分支邏輯直接對應型別與屬性條件（透過 when 子句），寫法更貼近業務規則，避免先 is 再 cast 的兩段式樣板與潛在例外。作者展示 if-else 與 switch 寫法的對照，說明 pattern matching 可讀性與維護性優勢。進一步以 IL 與反編譯結果證實編譯器會將其展開為 as 轉型、null 檢查與條件判斷的等價碼，因此效能上無本質差異，重點在語法層面的正交性與原子化操作（如 TryParse 一次完成檢查與解析）的設計哲學。作者並討論取捨：若需求側重封裝、行為重用與狀態一致性，傳統多型設計較佳；若資料來自外部（DB/JSON）且僅需直覺處理與過濾，pattern matching 更有效率。整體而言，它讓 C# 更擅長對結構化資料進行匹配與計算，與現代資料密集應用相符。

### Visual Studio 15 Preview 啟用 C# 7 新語法支援
本文提供在 Visual Studio 15 Preview 體驗 C# 7 語法的步驟。VS 15（版本 15.0，非 VS 2015）在 Roslyn 架構下已內建語言新特性，但預設停用。要啟用需於專案的條件式編譯符號新增 __DEMO__ 與 __DEMO_EXPERIMENTAL__，設定路徑為「專案 > 屬性 > Build」。完成後即可在 IDE 內直接撰寫並編譯 C# 7 語法，編輯器亦會正確辨識，無語法錯誤提示。作者提醒，因為這些特性屬於編譯器等級的 sugar，編譯產物能於既有 Runtime 正常執行，開發者可安心在預覽通道中先行嘗試，並評估團隊代碼風格與可讀性的收益。

### 後記
作者以「語法潔癖」的個人偏好總結本篇，指出華文技術圈較少在語法設計與可讀性層面進行深入討論，因此撰文補足觀點：好的語法能使程式碼更直接反映思考邏輯，減少機械式樣板與心智負擔，長期提升維護品質。文末也以輕鬆筆調分享 //Build/2016 講者的 C# 超人 T 恤趣聞，呼應對 C# 語言演進的熱愛與期待。

### References
列出官方影片、語言提案與多篇社群文章，涵蓋 C# 7 新特性的預覽、啟用說明、設計討論與背景脈絡，便於延伸閱讀與追蹤後續變更。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C# 語言基礎（類別/物件、屬性、方法、存取修飾）
   - OOP 與多型、繼承介面（abstract/virtual/override）
   - 型別系統與轉型（is/as、casting）、ref/out、例外處理
   - 泛型、集合與 LINQ 基礎
   - 不可變物件（immutability）與等值判斷（Equals/IEquatable）
   - Visual Studio 與 Roslyn（編譯器概念、條件式編譯符號）

2. 核心概念（3-5 個）及關係：
   - Tuples（具名 tuple 字面量）：以最小樣板一次回傳/承載多值，提升可讀性；可做為一般資料承載不僅限回傳值
   - Record Type（僅屬性、不可變、值相等語意）：快速宣告資料型別，天生支援值相等與 with 複製；可繼承
   - Pattern Matching（型別與屬性條件的樣式比對）：整合 is + casting + 條件，於 switch/if 中直接比對與解構行為
   - Syntactic Sugar（編譯期轉換）：上述特性皆由編譯器展開，無需新 Runtime，效能本質不變
   - 可讀性與設計取捨：在多型封裝 vs. 模式比對直述式風格間選用，視重用需求與資料來源而定

3. 技術依賴：
   - Roslyn C# 編譯器（VS "15" Preview 支援，預設關閉需啟用符號）
   - 現有 .NET Runtime 即可（語法糖轉成既有 IL）
   - 與現有語法的關聯：switch/if、is/as、物件初始器、繼承、IEquatable

4. 應用場景：
   - 多回傳值 API（避免多餘 DTO 或 out/ref 參數）
   - 資料整形與搬運（DB/JSON 查詢結果的臨時資料結構）
   - 異質集合處理（多型別物件的分類、過濾與聚合）
   - 以不可變模型建構業務物件（快照、with 複製修改）
   - 提升可讀性與維護性（將「型別判定+條件」表達為單一原子操作）

### 學習路徑建議
1. 入門者路徑：
   - 複習 C# 基礎（類別、屬性、方法、集合、例外、is/as）
   - 了解 ref/out 的侷限與多回傳需求
   - 練習 Tuple 字面量與具名元素，取代 out 方案
   - 認識不可變資料觀念與 IEquatable 的基本意義

2. 進階者路徑：
   - 使用 Record Type 建立不可變資料模型，練習 value equality 與 with 表達式
   - 在 if/switch 中使用 Pattern Matching 與 when 守衛做條件過濾
   - 比較多型封裝 vs. Pattern Matching 的設計取捨
   - 透過 IL 觀察或反編譯理解語法糖的展開與效能等價

3. 實戰路徑：
   - 將既有 out/ref API 重構為回傳 Tuple（具名欄位）
   - 將臨時查詢結果改用 Record Type 表達，並以 with 做不可變更新
   - 對異質集合的業務邏輯改寫為 Pattern Matching（含 when 條件）以提升可讀性
   - 在 VS "15" Preview 啟用相關語法並建立 POC，驗證可讀性與錯誤率下降

### 關鍵要點清單
- Tuples 字面量與具名元素: 以 (Width: 800, Height: 600) 直接建立/回傳多值並具名存取，取代 out/ref 與雜訊型別 (優先級: 高)
- Tuple 非僅回傳值: 可在一般變數、集合中運用 tuple 字面量作為輕量資料載體 (優先級: 中)
- Record Type 定義: 以 class Person(string First, string Last); 一行宣告不可變資料型別，側重屬性與值相等 (優先級: 高)
- Record 的值相等語意: 自動實作 IEquatable<T>，比較以內容為準，適合資料模型與測試斷言 (優先級: 中)
- Record 的 with 複製: 以 with { Prop = ... } 產生更新後的新實例，符合不可變模型實務 (優先級: 高)
- Record 的繼承: Record 仍可做繼承階層（如各幾何形狀），方便分層描述資料 (優先級: 中)
- Pattern Matching 基礎: 將 is + casting 合併到 case/if 中，直述型別判定與存取 (優先級: 高)
- Pattern Matching 的 when 守衛: 在樣式比對中加入屬性條件（如高度 > 5）以一次完成篩選與操作 (優先級: 高)
- 與多型封裝的取捨: 重用與封裝強時用多型；一次性計算/資料驅動時用 Pattern Matching 較直觀 (優先級: 高)
- 語法糖與效能: C# 7 新語法為編譯期展開，IL 等價，效能不因語法改寫而本質改變 (優先級: 高)
- 與 TryParse 類比: 將多步（檢查+轉型/解析）收斂為不可分割動作，提高可讀性與安全性 (優先級: 中)
- VS "15" Preview 啟用方式: 以條件式編譯定義 __DEMO__, __DEMO_EXPERIMENTAL__ 啟用新語法（當時預設關閉） (優先級: 中)
- Roslyn 的角色: 新語法能快速落地於編譯器/IDE，無需改動 Runtime，提升語言演進速度 (優先級: 中)
- 與 JSON/資料導向思維的呼應: Tuples/Records 便於在程式內快速塑形資料，Pattern Matching 便於過濾與聚合 (優先級: 中)
- API 設計啟示: 多回傳值與不可變模型讓 API 更語意化，減少臨時類別與副作用 (優先級: 中)