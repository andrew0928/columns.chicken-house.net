# [BlogEngine Extension] PostViewCount 1.0

## 摘要提示
- 重寫動機: 原有 Counter 功能受限、XML I/O 效能差且缺乏 ThreadSafe 機制，促使作者自行開發新版 PostViewCounter。
- 設計目標: 新版需支援流水帳紀錄、ThreadSafe 讀寫、快取機制與自動壓縮 (Compact)。
- 檔案格式: 由集中式 PostViews.xml 改為「一篇文章一檔」的 ~/App_Code/counter/{post-id}.xml，並加入 base 與 hit 節點。
- 同步機制: 以 Flyweight + Dictionary 儲存 SyncRoot 物件，再配合 lock 與檔案層級 File Lock，確保多執行緒安全。
- Compact 策略: 當記錄過多時，刪除舊 hit 節點並累加到 base 屬性，維持總計不變且控制檔案大小。
- BlogEngine 擴充架構: 採事件 (Event Handler) 而非傳統 Provider，並提供 ExtensionSettings API 管理獨立設定檔。
- 設定頁面: 透過 ExtensionSettings 宣告 MaxHitRecordCount、HitRecordTTL 兩參數，由 BE 自動產生 UI。
- 主要程式碼: 提供 PostViewCounter.cs，放入 ~/App_Code/Extension 即可安裝。
- 佈署簡易: 無需額外安裝程序，複製檔案後即可於 Extension Manager 啟用。
- 進階學習: 文章包含 ThreadSafe、Flyweight、Factory Pattern、WeakReference 等設計概念示範。

## 全文重點
作者原本使用社群提供的 BlogEngine.NET Counter Extension，但在長期使用後發現僅能統計總點閱數、XML 讀寫程式過於簡陋且在高併發環境下容易互相覆寫資料，加上缺乏快取導致效能不佳，於是決定自行重寫 PostViewCounter 1.0。新版本首先重新定義資料格式：改用「一篇文章一檔」的 XML，於 counter 節點維護 base 屬性以紀錄先前總計，並以多個 hit 節點保存每一次點閱的時間、IP、Referer 等資訊；當記錄過多時即可刪除舊 hit 並將刪除筆數加回 base，以達到檔案自動壓縮的目的。

技術核心為 ThreadSafe 的 I/O 實作。作者採取雙層鎖定：程式層面利用 Dictionary<string, object> 為每個 counterID 配置一個 SyncRoot 物件，透過 lock (SyncRoot) 保證同一篇文章的所有執行緒序列化；檔案層面再輔以 File Lock 作為第二道保險。為避免因大量 Counter 物件滯留記憶體，作者未使用 Flyweight 直接快取完整 Counter，而僅將極小的 SyncRoot 物件存入 Dictionary；Counter 本身則視需求 new 出來，用完便等待 GC 回收。

在 BlogEngine 架構面，作者研究官方文件後發現 1.4 版改採事件驅動而非 Provider，擴充程式只需訂閱 Post.Serving 事件即可插入邏輯；設定值透過 ExtensionSettings 宣告資料表結構即可由系統自動產生後台 UI，並提供 XML 儲存。PostViewCounter 僅需定義 MaxHitRecordCount 與 HitRecordTTL，使用者便能在後台調整保留筆數與天數。

整體而言，新版 PostViewCounter 具備：
1. 完整流水帳紀錄與自動壓縮機制；
2. ThreadSafe 與快取設計確保高併發穩定；
3. 與 BlogEngine 1.4 ExtensionManager 完美整合，部署僅需複製單一 .cs 檔；並透過開放原始碼讓其他開發者學習 Flyweight、WeakReference 與事件式擴充等實作細節。

## 段落重點
### 1. 引言與動機
作者因 BlogEngine 1.4 發佈而延後撰寫文章；指出既有 Counter Extension 只能累計總點擊且在多執行緒情境下資料易被覆寫，並無快取機制，效能及可靠度不足，決心自行開發。

### 2. 功能需求與目標
列出新版本四大需求：能記錄流水帳、ThreadSafe 讀寫、有效快取以簡化鎖定邏輯、以及自動 Compact 以控制檔案大小，並藉此兼顧詳盡統計與長期效能。

### 3. 舊檔案格式與新格式設計
解析原 ~/App_Data/PostViews.xml 僅存總數的缺陷；提出新 ~/App_Code/counter/{post-id}.xml 格式，於 counter@base 存既有總數並以多筆 hit 節點保存詳細資料，並說明 Compact 時如何更新 base 與刪舊 hit。

### 4. ThreadSafe 與鎖定策略
討論 File Lock 只能拋例外無法等待的限制；說明採用 Flyweight 範式在記憶體中為每篇文章配置一個 object 作為 SyncRoot，再以 lock 確保序列化，同時保留檔案級鎖做為保險；比較快取 Counter 與僅快取 SyncRoot 的記憶體成本差異。

### 5. 程式碼實作重點
展示 Counter 類別中 SyncRoot 取得與 Hit() 實作；說明為何未採用完整 Factory + WeakReference，而以簡約方式達到效能與可回收性的平衡；並提供完整 PostViewCounter.cs 供下載。

### 6. BlogEngine 擴充機制與設定
解析 BlogEngine 採事件驅動設計，可直接訂閱 Post.Serving 事件插入邏輯；介紹 ExtensionSettings API，可宣告欄位、預設值及提示文字，由系統自動產生後台設定頁，並示範程式碼與最終 UI 截圖。

### 7. 安裝方式與結語
說明安裝極為簡單，只需將 PostViewCounter.cs 複製到 ~/App_Code/Extension 目錄並於 Extension Manager 啟用即可；邀請讀者提供意見，並提供下載連結。