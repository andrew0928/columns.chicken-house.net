# C#: yield return #1. How It Work ?

## 摘要提示
- 語法糖概念: C# 以 compiler-generated code 取代繁瑣實作，讓開發者用簡潔語法取得 Iterator 功能。  
- IEnumerator 與 Iterator Pattern: 透過介面封裝「巡訪」與「處理」行為，達到結構化設計目的。  
- 傳統手寫 IEnumerator: 必須自行撰寫 MoveNext、Current、Reset 等方法，程式冗長且不易維護。  
- Loop 實作侷限: iteration 與 process 混雜，邏輯耦合導致重用與變更成本高。  
- yield return 優勢: 一行關鍵字即可自動產生對應 IEnumerator 類別，保留語意簡潔與設計彈性。  
- 範例比較: 以「列舉 1~100、過濾 2 或 3 的倍數」對照傳統 loop、手寫 IEnumerator 與 yield return 三種寫法。  
- 反組譯觀察: 使用 Reflector 可看到編譯器額外產生的 `<YieldReturnSample3>d__0` 類別，完整實作 IEnumerator。  
- 語言設計取向: .NET 願意為語法簡潔修改 IL 與編譯器，與 Java 謹守 VM 相容性的策略形成對比。  
- 延伸議題鋪陳: Author 暗示下一篇將把 Iterator 與 Thread Synchronization 結合，探討進階應用。  

## 全文重點
本文以 C# 的 yield return 為主題，從語言設計哲學談起，指出 .NET 為了提升可讀性與開發效率，允許編譯器替開發者生成大量樣板程式碼，形成所謂「語法糖」。作者先以 Iterator Pattern 的理論基礎切入，說明 IEnumerator 介面如何分離「巡訪集合」與「處理元素」兩種關注點；接著以列舉 1~100 的整數為例，示範若依正統做法必須手動撰寫整個 IEnumerator 類別，包含私有狀態、MoveNext 與 Current 等實作，程式碼冗長且易出錯。再將同一需求以傳統 for 迴圈完成，雖然簡短卻無法重複利用，因為過濾與輸出邏輯被硬編在同一區塊。  
在進階範例中，作者加入「只列出 2 或 3 的倍數」條件，凸顯 loop 版本不得不混合判斷與輸出，程式可讀性進一步下降，而手寫 IEnumerator 雖然職責分離卻更加繁瑣。此時 yield return 出場，只需把迴圈寫在一個傳回 IEnumerable<int> 的方法中，於符合條件時直接使用「yield return current;」，由編譯器自動產生隱藏類別 `<YieldReturnSample3>d__0` 來實作整個 IEnumerator。開發者以極少的程式碼，即可享受 Iterator 帶來的結構優勢，同時維持最直覺的迴圈寫法。  
最後作者透過 Reflector 反組譯，展示編譯後的自動生成程式碼：隱藏類別完整實作 IEnumerable、IEnumerator、IDisposable 等介面，並用 state machine 技巧維持函式暫態，讓每次 MoveNext 都能回到「yield return」之後的狀態繼續執行。這揭露了 yield return 背後的技術原理，也呼應了 .NET 為語法糖所做的編譯層支援。文章結尾埋下伏筆，將在下一篇探討 Iterator 與多執行緒同步的結合，提醒讀者持續關注。

## 段落重點
### 引言：C# 與 Java 的設計取向
作者先談 .NET 與 Java 在語言演進的策略差異。Java 為維持跨平台，相對保守於修改 VM 與語法；.NET 則願意讓編譯器承擔複雜度，引入豐富的 Syntax Sugar，包括本文主角 yield return，使開發者能用少量程式碼完成複雜工作。

### Iterator Pattern 與 IEnumerator 基礎
回顧 Design Patterns 中的 Iterator 定義：「不需知道集合內部結構即可依序存取元素」。.NET 透過 IEnumerator 介面具體落實此模式，將「巡訪次序」與「元素處理」解耦。若採手寫 IEnumerator，必須維護 start、end、current 等狀態並實作 MoveNext/Current/Reset，程式碼冗繁。

### Loop 實作範例與缺點
以單純列印 1~100 為例，傳統 for 迴圈最快寫完，但巡訪與處理交織，一旦需求變動（例如改變過濾條件或輸出方式）就得同時修改同一區塊，缺乏彈性與重用能力。

### 進階需求：過濾 2 或 3 的倍數
當加入「僅顯示 2 或 3 的倍數」時，loop 版本需插入多重條件判斷；而手寫 IEnumerator 雖可分離 concern，但必須額外撰寫 do..while 及狀態控制，代價高昂。此段主要用來凸顯 yield return 的價值。

### yield return 亮相與簡化效果
作者展示僅用一個方法加 yield return 的寫法，即可回傳 IEnumerable<int>，供 foreach 直接使用。程式仍保有易讀的傳統迴圈形式，同時自動具備 Iterator Pattern 的彈性，是「魚與熊掌兼得」的解答。

### 反組譯分析：隱藏 State Machine
透過 Reflector 反組譯，讀者可見到編譯器產生之 `<YieldReturnSample3>d__0` 類別：  
1. 實作 IEnumerable/IEnumerator/IDisposable。  
2. 以 switch-state 方式保存執行點，支援多次 MoveNext/Current。  
3. 建立初始 threadId 以確認執行緒上下文。  
此段證明 yield return 其實是編譯階段自動生成 state machine 的產物。

### 結語與下集預告
作者總結 yield return 的優雅與實用，並埋下伏筆：下一篇將把 Iterator 技術與多執行緒同步 (Thread Sync) 結合，探討更高階的應用場景，邀請讀者持續追蹤。