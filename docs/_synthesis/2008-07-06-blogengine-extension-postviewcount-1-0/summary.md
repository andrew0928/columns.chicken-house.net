---
layout: synthesis
title: "[BlogEngine Extension] PostViewCount 1.0"
synthesis_type: summary
source_post: /2008/07/06/blogengine-extension-postviewcount-1-0/
redirect_from:
  - /2008/07/06/blogengine-extension-postviewcount-1-0/summary/
postid: 2008-07-06-blogengine-extension-postviewcount-1-0
---

# [BlogEngine Extension] PostViewCount 1.0

## 摘要提示
- 動機與不足: 既有 Counter Extension 只記總數、I/O 設計粗糙、缺少快取與並發處理，無法滿足需求
- 目標功能: 增加流水帳記錄、ThreadSafe 寫入、運用快取、可壓縮歷史紀錄
- 檔案格式重構: 由單一總表改為每篇文章獨立 XML，含 base 累計與 hit 明細
- 流水帳內容: 每次點閱記錄時間、IP、Referer、User-Agent，供分析使用
- Compact 機制: 砍舊 hit 記錄並累加到 base，維持總數不變同時控制檔案大小
- 併發寫入策略: 採雙層保護，主以 Monitor 鎖定，檔案鎖為次要備援
- 鎖定對象設計: 以 flyweight 字典存放每個 counterID 的輕量 lock 物件，避免大型物件長駐
- BlogEngine 擴充模式: 採事件驅動(Event Handler)而非 Provider，擴充更彈性
- 設定管理: 使用 ExtensionSettings 定義並儲存參數，支援獨立設定檔與簡易管理介面
- 安裝方式: 下載單一檔案放入 ~/App_Code/Extension，即可於 Extension Manager 啟用

## 全文重點
作者因現有 BlogEngine.NET 的 Counter 擴充套件只提供總數計數、XML I/O 設計不佳、缺乏快取與多執行緒寫入保護，決定自行開發 PostViewCount 1.0，目標是在保留簡單部署的前提下提升實用性與穩定性。新版本的核心在於資料儲存與併發控制：資料格式從集中式的 PostViews.xml 轉為每篇文章一個獨立 XML，內含 base 屬性加總與多筆 hit 明細。每筆 hit 記錄時間、來源 IP、Referer 與 User-Agent，便於後續分析。隨著資料量成長，擴充設計加入 compact 機制，當命中記錄超過限制或逾越 TTL 時，會刪除舊明細並把刪除筆數累加到 base，維持總數一致且檔案輕量。

ThreadSafe 是本次重點。作者選擇以 Monitor 鎖作為主機制，檔案鎖為次要保護，原因在於檔案鎖失敗會丟出例外並不適合作為主要同步工具。為確保相同 counterID 的操作會鎖到同一把鎖，採用 flyweight 方式在靜態 Dictionary<string, object> 中存放每個 counterID 專用的輕量 lock 物件。這避免了把完整 Counter 物件放入快取造成 GC 無法回收的風險，也不需引入 WeakReference 複雜度。Counter 本身則走「用完即丟」策略，降低記憶體壓力。

在與 BlogEngine 的整合上，作者分析官方採事件驅動(Event Handler)設計，與常見 Provider 模式不同。事件模式好處在於擴充點不需改抽象基類即可增加，避免因基底變動導致既有外掛破壞。設定管理方面，BlogEngine 1.4 為每個擴充提供獨立設定檔與一致 API，作者使用 ExtensionSettings 定義 MaxHitRecordCount 與 HitRecordTTL 等參數，並於 Extension Manager 提供簡易 UI 管理，讓 runtime 自動處理儲存與載入。

整體來說，PostViewCount 1.0 同時解決了資料明細需求與併發一致性，並提供可維運的 compact 策略與輕量鎖設計；部署上只需將單一檔案放入 ~/App_Code/Extension，即可於 Extension Manager 看到外掛並啟用。文末提供原始碼下載連結，便於進一步研究或直接使用。

## 段落重點
### 背景與動機
作者原本使用第三方 BlogEngine Counter Extension，功能雖可用但僅能統計總數，且 XML 讀寫程式品質不佳、未處理同時讀寫導致資料互相覆蓋，亦缺少快取加速。隨着 BlogEngine 1.4 發布與官方擴充教學文章出現，作者決定自行實作更合用的版本。需求明確為四點：記錄流水帳(時間、IP、Referer等)、ThreadSafe 寫入、引入快取降低 I/O、以及提供自動 compact 以控制檔案大小。這些訴求聚焦在資料儲存模型與併發處理設計。

### 新的檔案格式設計
舊版集中式 PostViews.xml 僅記錄每篇文章的總數，難以擴充。新設計改為每篇文章對應一個獨立 XML 檔，節點 counter 上有 base 屬性，並以多個 hit 節點保存點閱的時間、來源 IP、Referer、User-Agent。總數=base+hit 節點數，既直觀也方便維護。當資料量暴增時，compact 機制會刪除舊 hit 記錄並把刪除的筆數累加到 base 中，既保留總體統計正確性，又讓記錄檔維持在合理大小。這套格式同時符合易讀、易寫與後續分析的需求。

### ThreadSafe 與鎖定策略
並發寫入是關鍵問題。雖然檔案系統提供檔案鎖，但失敗即丟例外不利流暢控制，故設計以 Monitor 為主，檔案鎖為輔。要讓同一篇文章的多個請求鎖到同一物件，作者評估兩種方案：以 Counter 物件為鎖或以獨立鎖物件為鎖。前者需實作 flyweight factory 並面臨物件長駐字典無法回收的風險，除非導入 WeakReference 增加複雜度；作者最終採後者，在靜態字典以 counterID 對應一個輕量 new object() 作為鎖，成本低、可控性高。Counter 則保持短生命週期，避免記憶體壓力。最終在 Hit 流程以 lock(SyncRoot) 包覆檔案更新，保障一致性。

### 程式碼片段與邏輯要點
核心程式以靜態 Dictionary<string, object> 保存各 counterID 專屬的 SyncRoot；在 Counter 建構時以 lock 保護字典新增動作，確保鎖物件單一且可共用；在 Hit 時以 lock(SyncRoot) 包住檔案更新，避免競態與覆寫。資料寫回邏輯包含：新增 hit 記錄時同時評估是否達到 MaxHitRecordCount 或超過 HitRecordTTL，若達條件則執行 compact，刪除舊紀錄並調整 base。透過簡潔的格式與同步策略，I/O 次數可配合快取策略減少，維持效能與正確性。

### BlogEngine 擴充架構與設定機制
BlogEngine 採事件驅動的 Extension 架構，與常見 Provider 基底類別的模式不同。Provider 模式在設計時就限定擴充邊界，若要新增擴充點須改變抽象基類，易破壞相容性；事件模式僅需新增事件即可擴展功能，耦合度較低。設定管理方面，1.4 版本提供每個 Extension 獨立設定檔，並以 ExtensionSettings API 暴露「像 DataTable」的設定存放方案，支援欄位命名、型別與多筆資料；在此案例中定義 MaxHitRecordCount 與 HitRecordTTL 兩個參數、預設值與說明，並透過 Extension Manager 呈現管理 UI，Runtime 則負責儲存與載入，降低擴充程式的樣板負擔。

### 安裝與下載
作者提供即裝即用的單檔部署方式：將 PostViewCounter.cs 複製至 ~/App_Code/Extension，於 BlogEngine 的 Extension Manager 中即可看到並啟用外掛，無需額外安裝步驟。對想直接使用的讀者可略過實作細節；若想深入研究同步與資料格式設計，可下載原始碼閱讀與調整。下載連結為 http://columns.chicken-house.net/wp-content/be-files/PostViewCounter.cs。整體方案在正確性、可維運性與簡易部署間取得平衡，適合需要精確統計與擴充潛力的 BlogEngine 部署者。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - C#/.NET 與 ASP.NET 基礎（檔案 I/O、XML 讀寫）
   - 多執行緒與同步機制（lock/Monitor、檔案鎖 File Lock、執行緒安全觀念）
   - 快取（Cache）設計概念與效能權衡
   - 設計模式（Factory、Flyweight、WeakReference）
   - BlogEngine.NET 結構與擴充機制（事件、ExtensionSettings）

2. 核心概念：
   - Post 檢視計數器（Counter）：記錄總次數與每次點閱的流水帳（time、referer、IP、UA）
   - 資料儲存格式：改為每篇文章一個 XML（/App_Code/counter/{post-id}.xml），以 counter@base + hit 元素組合總數
   - 執行緒安全：以每個 counterID 對應一個鎖物件的字典，使用 Monitor lock；檔案鎖為第二層保護
   - 快取與壓實（Compact）：以 Cache 降低 I/O；當流水帳過多或過期時刪除 hit 並累加至 base
   - 擴充架構：採 BlogEngine 的事件驅動模型（Event Handler）與 ExtensionSettings 管理設定

3. 技術依賴：
   - .NET/C# 語言與 System.Xml、檔案系統 API
   - ASP.NET 應用程式生命週期與多執行緒存取
   - BlogEngine.NET 1.4 事件模型（Post.Serving）與 ExtensionSettings API
   - 依賴關係：Extension 依賴 BlogEngine 事件；Counter 邏輯依賴 XML 儲存與 Cache；Compact 依賴 counter@base；執行緒安全依賴 counterID→SyncRoot 字典；File Lock 為輔助

4. 應用場景：
   - 部落格文章檢視數統計與簡易分析（時間、來源、使用者代理）
   - 高流量站台的檔案型計數需求，需控制檔案尺寸（Compact）
   - 多執行緒環境（多用戶同時瀏覽）避免競態條件與寫入衝突
   - 需要快速安裝部署的 BlogEngine.NET 擴充套件

### 學習路徑建議
1. 入門者路徑：
   - 了解 BlogEngine.NET 的基本架構與如何安裝 Extension
   - 熟悉 C# lock/Monitor 與簡單 XML 讀寫
   - 先實作只計總數的 counter，再逐步加入設定頁面的讀寫

2. 進階者路徑：
   - 實作 per-post XML 結構（counter@base + hit attributes）
   - 設計每個 counterID 的同步字典並以 Monitor 保護臨界區；檔案鎖當第二層
   - 導入快取策略，並完成 Compact（MaxHitRecordCount、HitRecordTTL）
   - 比較事件模型與 Provider 模型的擴充性、相容性與維護成本；評估 WeakReference 的替代設計

3. 實戰路徑：
   - 將檔案放入 ~/App_Code/Extension，於 Extension Manager 啟用
   - 配置 ExtensionSettings：MaxHitRecordCount、HitRecordTTL
   - 壓測並觀測在高併發下的正確性與效能（含檔案鎖失敗處理）
   - 監控 XML 檔大小與 Compact 觸發頻率，調整快取與閾值

### 關鍵要點清單
- 檔案結構（per-post XML）：以 ~/App_Code/counter/{post-id}.xml 存放，counter@base + hit 元素組合總數 (優先級: 高)
- 流水帳內容：hit 記錄 time、referer、remote-host、user-agent 以利後續分析 (優先級: 中)
- Compact 機制：刪除舊 hit 並將筆數累加至 counter@base，維持總數不變且控檔案大小 (優先級: 高)
- 同步策略（SyncRoot 字典）：為每個 counterID 建立鎖物件，使用 Monitor 保護 I/O 臨界區 (優先級: 高)
- 檔案鎖（File Lock）：當作第二層保護，處理檔案層級的衝突風險 (優先級: 中)
- 快取應用：以 Cache 降低頻繁 I/O 與同步壓力，提升效能 (優先級: 高)
- Flyweight/Factory 取捨：避免將 Counter 實體放入長存字典導致無法 GC，改以鎖物件 flyweight (優先級: 中)
- WeakReference 考量：若需快取 Counter 實體，可用弱參考避免記憶體洩漏 (優先級: 低)
- 事件驅動擴充：BlogEngine 採 Event Handler 而非 Provider，擴充性較佳、相容性較高 (優先級: 高)
- ExtensionSettings：以設定架構建立 schema 與 UI，支援 1.4 獨立設定檔 (優先級: 高)
- 關鍵參數：MaxHitRecordCount、HitRecordTTL 控制資料量與保存期限 (優先級: 中)
- 併發風險管理：讀寫 XML 的競態條件與覆寫風險需以同步與檔案鎖緩解 (優先級: 中)
- 安裝部署：將 PostViewCounter.cs 複製至 ~/App_Code/Extension 並於 Extension Manager 啟用 (優先級: 中)
- 效能與可維護性：在詳細紀錄與檔案大小、I/O 負載之間取得平衡 (優先級: 中)
- 版本差異：BlogEngine 1.3 共用設定檔 vs 1.4 獨立設定檔，API 使用一致 (優先級: 低)