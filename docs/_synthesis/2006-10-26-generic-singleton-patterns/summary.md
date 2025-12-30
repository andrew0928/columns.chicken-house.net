---
layout: synthesis
title: "泛型 + Singleton Patterns"
synthesis_type: summary
source_post: /2006/10/26/generic-singleton-patterns/
redirect_from:
  - /2006/10/26/generic-singleton-patterns/summary/
---

# 泛型 + Singleton Patterns

## 摘要提示
- .NET 2.0 泛型: 利用泛型可讓 Singleton 模式更易於重用與維護。
- 傳統 Singleton: 單一類別的 Singleton 很簡單，但一旦多類別需求就產生重複樣板碼。
- 程式碼重複問題: 每個類別都要再寫一份 static Instance 與私有建構式，維護成本高。
- 繼承解法雛形: 以基底類別集中共用邏輯，透過 Type 與反射建立實例並用 Hashtable 緩存。
- API 易用性差: 需要傳 typeof(...) 給 Instance(Type) 使用起來冗長、可讀性差。
- 反射與快取: 以 Activator.CreateInstance(Type) 動態建立並以字典保存實例。
- 介面設計美感: 作者強調 library 應兼顧可讀性與優雅，現況無法接受。
- 目標設計方向: 結合繼承與泛型，達到型別安全、簡潔 API、避免重複碼。
- 問題本質: 在多型別套用 Singleton 時，同一段樣板碼反覆出現且介面不友善。
- 待續預告: 將提出「最得意」的泛型化 Singleton 解法，改善呼叫端體驗。

## 全文重點
文章探討如何在 .NET Framework 2.0 的泛型機制下，優化 Singleton 設計模式的實作與重用。作者先以傳統做法示範單一類別的 Singleton：以私有建構式限制外部建立、再搭配 static 欄位與屬性提供唯一實例。此作法在只有一個類別時很直接，但擴展到多個需要 Singleton 的類別時，會導致樣板碼重複：每個類別都要再寫一次同樣的 static Instance 與懶漢式初始化邏輯，不僅冗長也增加維護風險。

為了去除重複碼，作者嘗試用繼承集中共用邏輯：建立一個 SingletonBase，提供 public static SingletonBase Instance(Type seed) 方法，內部用 Hashtable 將 Type 對應到其唯一實例，當查無實例時透過 Activator.CreateInstance(seed) 以反射建立並快取。再讓各具體類別 (SingletonBaseImpl1、SingletonBaseImpl2) 繼承此基底類別，即可共用 Singleton 管理機制。

然而，這個解法雖然把重複的程式碼集中，但對使用者不友善：呼叫端必須寫出 SingletonBase.Instance(typeof(SingletonBaseImpl1)) 這種樣式，不僅冗長、型別安全不足，也失去原本 Instance 屬性那種簡潔清楚的 API 感受。從設計與可讀性角度，作者認為這樣的 library 品質不佳，難以接受。

基於對程式碼美感與維護性的堅持，作者提出直覺的改進方向：一方面透過繼承將共用邏輯留在基底類別；另一方面引入泛型以在不同型別之間重用同一套邏輯，同時維持型別安全與良好的呼叫體驗。文章最後預告將給出一個結合繼承與泛型、看起來更「得意」的實作，作為後續的完整解答。

整體來說，本文聚焦在三個重點：第一，傳統 Singleton 在多類別情境造成樣板碼氾濫；第二，以反射和快取集中管理雖能消重，卻犧牲了型別安全與 API 優雅；第三，泛型提供了在型別維度重用邏輯的能力，若與繼承搭配，有望實現既簡潔又安全的 Singleton 模式。作者以此鋪陳問題與設計思路，為下一篇的泛型化 Singleton 方案鋪路。

## 段落重點
### 前言：Singleton 與 Generic 的關聯
作者指出，乍看之下 Singleton 與泛型似乎無直接關聯，但在 .NET 2.0 引入泛型後，兩者結合能顯著改善 Singleton 的實作與重用性。文章以此為起點，準備從非泛型的傳統作法談起，逐步展示問題與改進的方向。

### 傳統非泛型的 Singleton 範例
示範一個典型的 Singleton：類別內有一個私有的 static 欄位保存唯一實例，對外暴露 public static 屬性 Instance 懶漢式建立，並以私有建構式避免外部 new。這個模式在只有單一類別時是簡潔且標準的。不過，一旦第二個、第三個類別也需要 Singleton，就需要把同樣的 static 欄位與屬性全部再寫一次，等於把樣板碼在每個類別複製一遍，既重複又不易維護。

### 以繼承集中共用程式碼
為解決重複碼，作者引入一個 SingletonBase，提供 static 方法 Instance(Type seed)，內部用 Hashtable 當作快取表，以 Type 為 key 保存每個子類別的唯一實例；當對應項目不存在時，使用 Activator.CreateInstance(seed) 動態建立並存回。具體的子類別只需繼承 SingletonBase，即可共享同一套 Singleton 管理機制。此設計成功達到「共用邏輯寫一次」的目標。

### 使用上不友善的痛點
雖然重複碼被消除，但呼叫端的程式碼變得醜陋且不直觀：每次取得實例都得寫 SingletonBase.Instance(typeof(SingletonBaseImplX))。這種 API 需要顯式傳 Type，既冗長也缺乏型別安全的直覺性（回傳的是基底型別，還需轉型或承受資訊不明確）。對強調程式設計美感與可讀性的作者而言，這種寫法不符合高品質 class library 的要求。

### 解決策略與泛型方向（待續）
作者總結解題思路：一是用繼承把共用的 Singleton 管理邏輯集中；二是用泛型在不同實作型別間重用同一套機制，同時保留型別安全與良好的呼叫體驗。目標是讓用戶端能用接近 T.Instance 或泛型化的簡潔寫法，消除 typeof(...) 以及轉型的雜訊。文末預告將在後續文章提出「最得意」的實作，完善這個結合泛型與 Singleton 的設計。

## 資訊整理

### 知識架構圖
1. 前置知識
- 了解 Singleton 設計模式的目的與基本實作（私有建構子、靜態實例存取）
- 熟悉 C#/.NET 的 static 成員、類別建構與存取修飾詞
- 了解 .NET 2.0 的泛型（generics）概念與動機
- 基本的繼承與多型觀念
- 了解反射與 Activator.CreateInstance 的用途
- 了解集合類別（如 Hashtable）的使用

2. 核心概念
- Singleton 模式：每個類別僅有一個實例，透過靜態屬性/方法存取
- 代碼重複問題：多個類別都要套用 Singleton 時，傳統寫法導致重複樣板代碼
- 繼承集中邏輯：以基底類別集中管理單例的生命週期與存放
- 反射動態建立：使用 Activator.CreateInstance(Type) 依型別動態產生實例
- 泛型改善介面：以泛型達到型別安全與更優雅的 API，避免傳 Type、避免轉型

3. 技術依賴
- 基本 Singleton 依賴：static 欄位/屬性 + 私有建構子
- 繼承式解法依賴：反射（Activator.CreateInstance）+ 儲存容器（Hashtable）+ Type 作為 key
- 泛型式解法（構想）：.NET 2.0 Generics 提供類型參數化與型別安全的存取介面，取代基於 Type 的 API 與轉型

4. 應用場景
- 專案中有多個類別都需要單例語意時，避免重複樣板代碼
- 希望以一致且美觀的 API 存取各自的單例（例如 Instance<T>() 或 GenericSingleton<T>.Instance）
- 封裝單例建立與儲存邏輯，降低重複與維護成本

### 學習路徑建議
1. 入門者路徑
- 先理解傳統 Singleton 的基本寫法（私有建構子 + 靜態屬性）
- 練習將單一類別改造成 Singleton，觀察使用端如何存取
- 思考若有第二、第三個類別需要 Singleton，會產生哪些重複

2. 進階者路徑
- 將 Singleton 共同邏輯抽到基底類別，以繼承集中管理
- 探索使用反射（Activator.CreateInstance）配合 Hashtable 以 Type 為 key 的儲存方式
- 評估這種 API 在可讀性、型別安全與易用性的缺點

3. 實戰路徑
- 規劃以泛型提供型別安全的單例存取介面，避免傳 Type 與轉型
- 將既有專案中的多個 Singleton 實作收斂到單一泛型機制
- 建立小型測試或範例，驗證多型別的單例能正確建立與重複取用（本文至此為設計動機與過程，實作待續）

### 關鍵要點清單
- 傳統 Singleton 基本寫法: 私有建構子配合靜態屬性回傳唯一實例 (優先級: 高)
- 多類別重複樣板問題: 多個類別各自實作 Singleton 會造成重複與維護成本 (優先級: 高)
- API 一致性與美感: 追求乾淨、易讀、可重用的單例存取介面 (優先級: 中)
- 繼承集中邏輯: 以基底類別集中實例建立與管理，減少重複 (優先級: 高)
- 使用 Type 做為鍵: 以 Type 作為 Hashtable 的 key，管理不同類別的單例 (優先級: 中)
- 反射動態建立: 透過 Activator.CreateInstance(Type) 在執行期建立實例 (優先級: 中)
- 物件轉型負擔: 基於物件或基底型別的回傳需要轉型，降低型別安全與可讀性 (優先級: 中)
- 非泛型 API 的冗長: 需要傳 typeof(...)，使用端顯得繁瑣、不優雅 (優先級: 中)
- .NET 2.0 泛型動機: 使用泛型可提供型別安全與更直覺的 API (優先級: 高)
- 設計目標 DRY: 以泛型與繼承實現「不要重複自己」（Don’t Repeat Yourself） (優先級: 高)
- 可維護性提升: 集中與抽象化單例邏輯，降低未來修改成本 (優先級: 中)
- 實作演進思路: 由單類別 Singleton → 繼承集中 → 規劃泛型化 (優先級: 中)
- 版本前提: 依賴 .NET Framework 2.0 才能使用泛型機制 (優先級: 中)
- 文末結論狀態: 文章提出動機與方向，具體泛型實作將於後續續篇說明 (優先級: 中)