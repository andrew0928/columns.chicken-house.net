# //build/2016 - The Future of C#

## 摘要提示
- C# 7 新語法: 文章聚焦 Tuples、Record Types 與 Pattern Matching 三項語法糖，解析其語意與使用情境。  
- Tuples: Tuple Literal 允許方法以具名欄位一次傳回多值，取代 out 參數與額外包裝類別。  
- Record Types: 以一行宣告產生唯讀、值相等的資料型別，並可透過 with 建立修改版實體。  
- Pattern Matching: 新版 is 與 switch 支援同時型別判斷與拆解，並可加上 when 條件過濾。  
- 語法糖定位: 三項功能皆屬編譯期展開，對 IL 與執行效能無影響，重點在可讀性與維護性。  
- VS "15" Preview: 安裝預覽版並在專案定義 __DEMO__、__DEMO_EXPERIMENTAL__ 即可試用 C# 7。  
- 代碼美感: 作者自述對程式碼「潔癖」，偏愛能讓程式更簡潔優雅的語言特性。  
- 範例對照: 以計算多邊形面積為例，比較傳統多型模式與 Pattern Matching 的差異。  
- 反組譯觀察: IL 及反編譯結果證實編譯器僅將新語法轉換成傳統 is/cast/if 邏輯。  
- 演進趨勢: 作者認為 C# 正受 JavaScript/JSON 思維影響，朝向快速建構與操作資料的方向發展。  

## 全文重點
作者參加 //Build 2016 之後，重複觀看「The Future of C#」影片，並針對 C# 7 最受自己關注的三大語法糖——Tuples、Record Types、Pattern Matching——撰寫心得。  
Tuples 透過 (int Width, int Height) 這種具名 tuple literal 讓方法能一次傳回多個強型別值，省去過去必須宣告額外類別、使用 out 參數或依賴 Tuple<T1,T2> 但只能用 Item1/Item2 的窘境。雖然語法上更簡潔，但編譯後依舊會展開成隱藏類別，效能並無差異，只是大幅減少樣板程式並提升可讀性。  
Record Types 則把「只包含唯讀屬性」的資料類別再度濃縮：class Person(string First, string Last); 一行就能產生自動實作 IEquatable<T> 的不可變物件。搭配 with 運算子，可基於既有實例產生只差異化屬性的全新物件。因其本質仍是 class，亦支援繼承，可用於輕量化 Domain Model、資料傳輸或快速定義多邊形等結構。  
Pattern Matching 進一步改善在大量物件中做「型別判定 → 轉型 → 條件判斷」的繁瑣流程。在 switch 或 if 敘述中，可寫成 case Triangle t when t.Side1>5: ...，將 is 與 cast 合併，並以 when 篩選屬性條件。作者以多邊形面積統計為例，比較傳統多型設計與 Pattern Matching 的整理式寫法；反組譯結果顯示編譯器只是展開成連續的 as 與 if 驗證，證明其為純語法糖。  
文中亦說明如何在 Visual Studio "15" Preview 透過條件編譯開啟 C# 7 支援；只要於專案 Build 設定加入 __DEMO__ 和 __DEMO_EXPERIMENTAL__ 即可體驗。作者最後分享自己對程式碼美感的堅持，以及對新語法讓 C# 更貼近 JavaScript 式快速資料操作的觀察與期待。整體而言，這些新特性雖不改善執行效能，卻能讓開發者用更直覺、易維護的方式表達意圖。

## 段落重點
### Tuples Literal，一次傳回多個回傳值
此段首先指出傳統語言只能回傳單一值，導致諸如 ANSI C int getchar() 的荒謬介面設計；接著回顧以封裝類別、out 參數與 System.Tuple 解法的缺陷。C# 7 的 Tuple Literal 允許 (int Width,int Height) GetSize() 這種具名方式一次回傳多值，呼叫端可用 var s = GetSize(); Console.WriteLine($"{s.Width}, {s.Height}") 直接取用。此語法僅是編譯階段自動產生隱藏類別，效能與傳統方法相同，但大幅減少樣板程式並增進程式可讀性；此外 Tuple Literal 亦可用於直接建立資料變數如 var size = (width:800,height:600)。  

### Record Type，只包含屬性的資料型別
作者說明在 ORM 或資料傳輸情境下，為每種查詢結果建立冗長 class 既麻煩又污染命名空間；Record Type 透過 class Person(string First,string Last); 一行宣告即可產生只含唯讀屬性、支援值相等判定(IEquatable<T>) 的不可變物件。透過 with 語法可基於既有實例生成修改版，如 var son = me with { First="Peter" };。Record 仍是 class，因而可繼承：Triangle、Rectangle、Square 等幾何結構皆可簡潔定義。此機制使大量資料結構的宣告、比較與複製操作省時又易讀。  

### Pattern Matching，物件的型別判定及比對語法
本段聚焦於在 foreach 處理多型集合時，傳統 is + cast + if 帶來的冗長與潛在例外；Pattern Matching 允許写作 case Triangle x when x.Side1>5:，在單一句子完成型別檢查、轉型與屬性篩選。作者以計算多邊形總面積為例，展示用 switch 與 if 兩種 Pattern 寫法，再對照傳統寫法的繁瑣。透過 ILDASM 與 Reflector 可見編譯器將 Pattern 還原為 as 與巢狀 if，證實其為純語法糖。作者進一步比較多型設計與 Pattern Matching 的適用場景：前者利於封裝與重用，後者則在單次資料處理、缺乏行為封裝需求時更簡潔。  

### Visual Studio 15 Preview 啟用 C# 7 新語法支援
作者說明欲體驗 C# 7 必須安裝 VS "15" Preview（非 VS 2015），並在專案 Build 的 Conditional compilation symbols 加入 __DEMO__ 和 __DEMO_EXPERIMENTAL__ 兩宏。設定完成後 IDE 即能辨識新語法、正常編譯與執行。此流程展示了 Roslyn 架構讓語言功能與 IDE 支援解耦，提供更快的實驗通道。  

### 後記
作者感嘆中文技術部落格鮮少討論語法層面的細節，因此撰寫本文分享對「程式碼美學」的執著；並提及講者穿著的 C# 超人 T 恤令人心動。結尾附上多篇相關資料連結，鼓勵讀者深入探索。整體而言，作者認為 C# 7 的語法糖雖屬「小改」卻能大幅提升程式表達力，值得每位對程式碼潔淨度有要求的開發者關注與嘗試。  

### References
列出官方 Channel 9 影片、Roslyn 提案、數篇社群文章與啟用教學，供讀者進一步參考與實作。  

