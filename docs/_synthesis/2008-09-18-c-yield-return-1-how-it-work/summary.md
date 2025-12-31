---
layout: synthesis
title: "[C#: yield return] #1. How It Work ?"
synthesis_type: summary
source_post: /2008/09/18/c-yield-return-1-how-it-work/
redirect_from:
  - /2008/09/18/c-yield-return-1-how-it-work/summary/
postid: 2008-09-18-c-yield-return-1-how-it-work
---

# [C#: yield return] #1. How It Work ?

## 摘要提示
- yield return: 以簡潔語法撰寫可逐步產生序列的迭代器，編譯器自動生成複雜底層實作。
- IEnumerable/IEnumerator: 透過標準介面提供逐一存取集合元素的機制，分離巡訪與處理邏輯。
- Syntax Sugar: C# 為提高可讀性與開發效率，讓編譯器承擔繁瑣樣板碼生成。
- Iterator Pattern: 不需了解集合內部結構，即可依序取出元素的設計模式實踐。
- 迭代與處理分離: 使用 IEnumerator 可將迭代規則與使用者邏輯分開，提升可維護性。
- 基本範例（1~100）: 展示手寫 IEnumerator 與單純 for 迴圈的對照，說明動機。
- 條件篩選示例: 用迭代器封裝「2 或 3 倍數」過濾，使用端程式碼不變。
- yield + foreach: 以方法直接回傳 IEnumerable，使用 foreach 取得序列，語意清晰。
- 反編譯揭密: 編譯器將 yield return 轉為隱藏類別與狀態機，實作 MoveNext 等細節。
- 後續串接主題: 與多執行緒、同步機制的關聯性預告，為系列文章鋪陳。

## 全文重點
文章從 C# 與 Java 的設計取向談起：Java 長期保守維持 VM 與語法穩定，而 C#/.NET 積極以編譯器讓步提供語法糖，使開發者以更簡潔的程式碼表達常見模式。核心主角是 yield return 與 IEnumerable<T> 的結合，它讓我們用直覺式的流程撰寫迭代邏輯，卻能獲得完整的迭代器實作。

作者先以傳統做法說明：若要依序產生 1 至 100，手寫 IEnumerator 需實作 Current、MoveNext、Reset 等，樣板碼冗長；而使用單純 for 迴圈雖短，但把「如何迭代」與「要做什麼」混在同一層，未來變更任一面向都不利。Iterator Pattern 的價值在於將「巡訪順序」與「處理行為」解耦。為凸顯此差異，作者進一步將需求改為只輸出 1~100 間的 2 或 3 倍數：for 迴圈版本必須在同一段程式碼裡混入判斷與輸出；相對地，若用 IEnumerator，過濾條件被內聚在 MoveNext 的邏輯中，而消費端的使用程式碼完全不變，展現了關注點分離的好處。

接著作者提出 yield return 的解法：透過一個回傳 IEnumerable<int> 的方法，在方法內用 for 與條件過濾，遇到符合條件的值就 yield return。使用端僅以 foreach 取值。這種寫法看似違背傳統「函式呼叫必須執行完才能返回」的直覺，因為每次 yield return 像是中斷並多次返回。但透過反編譯可見真相：編譯器會產生一個隱藏類別，實作 IEnumerable 與 IEnumerator，並用狀態變數與 switch 將原本的方法體改寫為狀態機；每次 MoveNext 都能從上次中斷處續行，正是 yield 的運作原理。

總結來說，yield return 是 C# 的語法糖，讓我們以極簡語法撰寫迭代器，同時擁抱 Iterator Pattern 的優點，維持使用端 API 的優雅（foreach），而底層複雜度由編譯器處理。文末也預告後續將把 IEnumerator 與執行緒同步議題串起，說明更進階的應用情境。

## 段落重點
### 引言：C# 與 Java、語法糖與設計觀
作者從產業與語言演進談起：Java 長期謹慎維持 VM 與語法的相容性，而 C#/.NET 則積極提供語法糖來提昇開發體驗。yield return 與 IEnumerable<T> 即屬於此類語法與標準介面的配合，讓常見的設計模式（如 Iterator）用最小語意成本表達。此鋪陳的目的，是讓讀者意識到：語言設計不僅為易寫，更是把常用模式變成一等公民，降低樣板碼與心智負擔。

### 以手寫 IEnumerator 產生 1~100：樣板碼的負擔
首先展示傳統方式：實作 IEnumerator<int> 來產生 1 至 100。必須提供 Current、MoveNext、Reset、Dispose 以及非泛型介面的對應實作，程式碼龐雜。對比之下，直接用 for 迴圈列印當然更短，但一旦需求希望把「如何巡訪」和「巡訪後做什麼」分開，迴圈寫法就會讓關注點糾纏。這段透過實例讓讀者看到 Iterator Pattern 的必要性：當迭代策略獨立於使用邏輯時，替換或複用變得簡單。

### Iterator Pattern 的目的：分離巡訪與處理
引用設計模式中的 Iterator：不需理解集合內部結構亦可依序存取元素。作者將其意義延伸到一般序列（不僅是集合）：把迭代規則（順序、過濾、產生）與處理行為（顯示、累加、轉換）解耦，才能在需求變更時局部調整。例如改變產生順序、插入條件、切換資料來源，都不應牽動使用端的程式碼。這正是 for 迴圈混寫法的短板，也是 IEnumerator 類型化抽象的優勢所在。

### 進階範例：2 或 3 倍數的過濾，迴圈 vs. IEnumerator
當需求變為輸出 1~100 中「2 或 3 的倍數」，單純的 for 寫法必須在同一段程式碼內混入判斷與輸出；任何一端改變（過濾條件或輸出方式）都會彼此影響。換成 IEnumerator 後，過濾條件集中在 MoveNext 內，外部取得資料的程式碼完全不變。這例子清楚說明：Iterator Pattern 讓同一個消費端可以接不同的迭代規則，達到關注點分離、易於替換與測試。

### yield return 的優雅解：方法即迭代器、foreach 即使用端
作者提出以 yield return 回傳 IEnumerable<int> 的方法版本。在方法裡用 for 與條件判斷，符合即 yield return；使用端以 foreach 逐一取得。此寫法同時具備兩者優點：語法像寫普通迴圈一樣直覺，又保留了迭代器的抽象與可重用性。對開發者而言不需手寫任何 IEnumerator 樣板碼，API 也更自然地以 IEnumerable 暴露，便於組合與測試。

### 反編譯揭秘：編譯器自動生成狀態機與隱藏類別
面對「函式如何多次返回」的直覺疑慮，作者以反編譯說明編譯器如何將 yield 方法轉換為隱藏類別，實作 IEnumerable/IEnumerator，並以狀態欄位與 switch 組成狀態機。每次 MoveNext 會根據狀態從上次中斷點續行，yield return 的值存放於欄位並由 Current 取回。也展示了 GetEnumerator 的邏輯與執行緒相關欄位，說明這一切是嚴謹的編譯期變換，而非魔法。

### 收束與預告：設計模式落地與多執行緒關聯
總結 yield return 是強力的語法糖，讓 Iterator Pattern 在 C# 中以最小成本落地，同時維持使用端以 foreach 消費的優雅介面。作者也保留伏筆，指出 IEnumerator 與執行緒同步之間存在有趣的連結，下一篇將進一步探討，延伸讀者對迭代器與執行緒模型互動的理解。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C# 基本語法（方法、控制流程、for/while）
   - 物件導向與介面概念（interface、實作）
   - .NET 集合基礎（Array、List、Collection）
   - foreach 的運作機制與 IEnumerable/IEnumerator
2. 核心概念：
   - Iterator Pattern：將「巡訪順序」與「處理工作」解耦
   - IEnumerable/IEnumerator：標準化的序列巡訪協定
   - yield return：語法糖，讓編譯器產生迭代器狀態機
   - 狀態機（State Machine）：編譯器產生的類別，透過 MoveNext/Current 持續返回元素
   - 語法糖與編譯器轉換：以簡潔語法換取背後大量樣板碼
   關係：foreach 依賴 IEnumerable/IEnumerator；yield return 由編譯器轉為實作 IEnumerable/IEnumerator 的狀態機；這整體實現即是 Iterator Pattern。
3. 技術依賴：
   - foreach → 需要 IEnumerable.GetEnumerator() 取得 IEnumerator
   - IEnumerator → 需要 MoveNext() 與 Current（和非泛型 Current）
   - yield return → 編譯器生成 sealed 類別，同時實作 IEnumerable<T> 與 IEnumerator<T>
   - 生成類別 → 內部以欄位保存狀態（<>1__state）、目前值（<>2__current）、區域變數、初始執行緒 Id 等
4. 應用場景：
   - 需要逐步、惰性（lazy）產生序列的情境（大資料、串流、昂貴計算）
   - 需要將「取資料邏輯」與「資料處理」分離（提高可替換性與重用性）
   - 需要以管線方式過濾/轉換元素（例如「取 1..100 中 2 或 3 的倍數」）
   - 想避免手寫冗長的 IEnumerator 樣板碼，提升可讀性與維護性

### 學習路徑建議
1. 入門者路徑：
   - 了解 foreach 背後對 IEnumerable/IEnumerator 的需求
   - 手寫一個簡易 IEnumerator（輸出 1..N），體會樣板碼
   - 改用 yield return 重寫相同功能，觀察程式碼明顯簡化
   - 用 Reflector/ILSpy 反編譯 yield 方法，對照手寫版本
2. 進階者路徑：
   - 練習多種迭代邏輯（篩選、跳號、早停）皆以 yield 實作
   - 了解編譯器生成類別的欄位/狀態設計（<>1__state、Current、MoveNext 流程）
   - 熟悉 IEnumerable<T>.GetEnumerator 與執行緒 Id 最佳化（重入與新實例）
   - 比較 loop 直寫 vs. yield vs. 手寫 IEnumerator 的可維護性與耦合度
3. 實戰路徑：
   - 在實務專案中，將資料來源巡訪（DB 分頁、檔案列舉、網路串流）改用 yield
   - 將複雜條件過濾邏輯封裝為可組合的 yield 方法（管線化）
   - 加入單元測試驗證邊界條件（空序列、早停、例外處理）
   - 監看效能與記憶體（延遲計算、逐步消耗）並與一次性載入相比

### 關鍵要點清單
- Iterator Pattern 的目的: 將「巡訪集合元素」與「元素處理」分離，無需了解內部結構即可依序存取 (優先級: 高)
- IEnumerable 與 IEnumerator: foreach 依賴這兩個介面提供 GetEnumerator/MoveNext/Current (優先級: 高)
- 手寫 IEnumerator 的樣板碼: 需實作 MoveNext、Current、非泛型 Current、Reset/Dispose，冗長易錯 (優先級: 中)
- yield return 的本質: 語法糖，讓編譯器自動產生實作 IEnumerable/IEnumerator 的狀態機類別 (優先級: 高)
- 狀態機欄位 <>1__state: 控制 MoveNext 的跳轉與流程狀態，對應程式跑到哪一步 (優先級: 高)
- <>2__current 與 Current 屬性: 保存並回傳目前迭代值，供外部讀取 (優先級: 中)
- 局部變數捕捉: yield 方法中的區域變數會變成生成類別的欄位以便跨次呼叫保存狀態 (優先級: 中)
- GetEnumerator 最佳化: 生成類別可能根據執行緒 Id 與狀態重用或新建迭代器實例 (優先級: 低)
- Reset 與 NotSupportedException: 生成的 IEnumerator.Reset 通常拋出 NotSupportedException (優先級: 低)
- 分離 iteration 與 process 的價值: 使巡訪策略可替換、測試更容易、重用性提高 (優先級: 高)
- 與直接 loop 的比較: loop 易把巡訪與處理耦合，維護與替換邏輯困難 (優先級: 中)
- 範例：篩選 2 或 3 的倍數: 用 yield 封裝條件過濾，呼叫端保持乾淨（foreach） (優先級: 中)
- 反編譯驗證: 透過 Reflector/ILSpy 可看到編譯器產生的 sealed 類別與 MoveNext 邏輯 (優先級: 中)
- 惰性評估與逐步輸出: yield 支援按需產生元素，適合大資料或昂貴計算 (優先級: 高)
- 語法糖的取捨: 以易讀性換取背後複雜樣板碼，由編譯器保證正確性與相容性 (優先級: 中)