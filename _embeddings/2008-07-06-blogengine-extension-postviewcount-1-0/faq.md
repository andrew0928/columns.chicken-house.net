# [BlogEngine Extension] PostViewCount 1.0

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼作者決定重寫 PostViewCount，而舊版 Counter 有哪些不足？
舊版 Counter 只有「總點閱數」(Total Count)，XML 讀寫程式碼混亂、未處理多執行緒同時存取導致資料被覆寫、且未使用快取 (CACHE) 加速；長期使用後這些限制使作者無法滿足需求，因此決定自行重寫。

## Q: 作者對新版 Counter 的功能期望有哪些？
1. 能記錄「流水帳」─每一次點擊的時間、來源 IP、Referer 等。  
2. 讀寫檔案必須是 Thread-Safe，能在多執行緒下安全更新。  
3. 善用 CACHE，降低併發控制複雜度。  
4. 支援 COMPACT：在記錄過多時自動刪除舊資料，同時保持正確總點閱數。

## Q: 新的資料檔格式長什麼樣子？`/counter/@base` 有何作用？
每篇文章各有一個 `~/App_Code/counter/{post-id}.xml` 檔案。  
根節點 `<counter>` 內帶屬性 `base="數字"` 表示「基礎點擊數」，再加上底下所有 `<hit ... />` 筆數便是最終總點閱數。當進行 COMPACT、刪除舊 `<hit>` 記錄時，被刪除的筆數會加回 `base`，確保統計不失真。

## Q: 新版 Counter 採用了什麼多執行緒同步策略？
作者使用 `Monitor`/`lock` 搭配  
`static Dictionary<string, object> _counter_syncroot`：  
每個 counterID 只對應一個極小的「鎖定物件」，所有對同一篇文章的操作都鎖定同一物件以確保 Thread-Safe；檔案層面的 File Lock 只做第二層保護。

## Q: 要怎麼在 BlogEngine.NET 安裝 PostViewCounter？
下載 `PostViewCounter.cs` 後，直接放到 `~/App_Code/Extension` 目錄即可。重新整理後，Extension Manager 便會出現「PostViewCounter」，啟用即可開始使用。

## Q: 這個 Extension 可以設定哪些參數？
透過 Extension Manager 的設定頁面可調整：  
• MaxHitRecordCount – 最多保留多少筆 `<hit>` 記錄 (預設 500)。  
• HitRecordTTL – 每筆記錄保留的最長天數 (預設 90 天)。  
只有同時滿足「未超過筆數上限」且「未超過保留天期」的紀錄才會被留下。

## Q: 為什麼 BlogEngine.NET 採事件 (Event Handler) 而非 Provider 方式來撰寫 Extension？
事件模型不需修改既有基底類別即可加入新功能；新增需求只要再定義事件即可，較不會破壞既有外掛，相較 Provider pattern 更具延展性與相容性。