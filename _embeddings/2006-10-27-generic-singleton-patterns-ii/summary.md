# 泛型 + Singleton Patterns (II)

## 摘要提示
- 設計目標: 透過泛型與繼承，把 Singleton 的細節完全封裝於基底類別，讓使用者零負擔。
- 泛型約束: 使用 where T : GenericSingletonBase<T>, new() 確保型別安全並保證有公開無參數建構式。
- 靜態實例: 以 public readonly static T Instance = new T(); 提供執行期唯一物件。
- 實作成本: 實作類別僅需繼承 GenericSingletonBase<T>，不必再撰寫任何 Singleton 程式碼。
- 使用體驗: 取得實例時直接透過 ClassName.Instance，無需轉型或額外程式。
- 函式庫觀念: 函式庫作者多做苦工，使用者端程式越簡潔越好。
- 與上一篇關聯: 承接第一篇鋪陳的問題與需求，這篇給出最終精簡解答。
- 代碼精煉: 整體解決方案僅數行程式，即可滿足多型別共用 Singleton 機制。
- 可讀性: 透過乾淨的 API 與自我說明的類別名稱，提高程式碼維護性。
- 擴充性: 同一套基礎框架可支援任意數量的 Singleton 類別，且不相互影響。

## 全文重點
作者在上一篇文章介紹了將 Singleton 與泛型結合時會遇到的問題——重複撰寫靜態欄位、建構式保護與轉型等樣板程式碼，既冗長又易出錯。本篇則直接給出最終解法：先寫一個泛型基底類別 GenericSingletonBase<T>，透過 where T : GenericSingletonBase<T>, new() 的約束，確保所有派生型別皆符合「繼承自自己、且具備公開無參數建構式」的條件。接著在基底類別內宣告 public readonly static T Instance = new T(); 由 CLR 保證靜態欄位於第一次存取時執行序安全地初始化，從而實現 Singleton 的「唯一」語意。

如此一來，任何想套用 Singleton 模式的類別只要繼承 GenericSingletonBase<SelfType> 即可，不必再寫私有建構式、鎖定區段或 GetInstance 方法。使用端的程式碼也簡化為 ClassName.Instance，避免醜陋而危險的轉型或重複呼叫。作者強調，函式庫設計者應該把複雜度留在框架內部，讓使用者以最直觀的方式完成工作；而泛型機制正是消除樣板與增進型別安全的最佳利器。最後，作者以短短數行示範如何宣告 GenericSingletonImpl1 與如何在呼叫端取得相同實例，並幽默地以「收工」作結，凸顯方案的簡潔與實用。

## 段落重點
### 問題背景與設計目標
作者回顧上一篇文章所留下的懸念：如何同時滿足 Singleton 模式與泛型型別安全，又不讓使用者撰寫重複程式。目標是「基底類別辛苦、使用者快樂」，也就是將所有 Singleton 細節集中於函式庫，讓實際業務類別僅需最少設定。

### GenericSingletonBase<T> 的實作
核心程式碼只有三行：宣告 public class GenericSingletonBase<T>，以 where T : GenericSingletonBase<T>, new() 約束確保繼承與建構式合法；在類別內定義 public readonly static T Instance = new T();。CLR 對靜態欄位的延遲載入保證了執行序安全與唯一路徑，完美符合 Singleton 要求。

### 實際套用：GenericSingletonImpl1
示範類別 GenericSingletonImpl1 : GenericSingletonBase<GenericSingletonImpl1>，僅加上可選的建構式以印出訊息驗證，完全不需撰寫額外 Singleton 控制碼。也因為繼承規則與泛型約束，編譯期就能防止錯誤用法。

### 呼叫方式與成果驗證
使用端程式碼直接以 GenericSingletonImpl1.Instance 取得實例，多次呼叫得到相同物件，且無需型別轉換或鎖定邏輯。作者以「很好，收工」做結，強調整套解決方案的簡約、易讀與可重用，並再次呼應「函式庫作者多做苦工」的設計哲學。