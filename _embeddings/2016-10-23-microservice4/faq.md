# API & SDK Design #2, 設計專屬的 SDK

# 問答集 (FAQ, frequently asked questions and answers)

## Q: API 與 SDK 的差別是什麼？
API（Application Programming Interface）強調的是「I（Interface）」，它僅是一份用來與程式溝通的「介面定義」；而 SDK（Software Development Kit）強調的是「K（Kit）」，除了對應的 API 呼叫封裝外，還可能包含文件、範例、工具與 Library，目的在於讓開發者更容易、有效率地使用該 API。

## Q: 為什麼在雲端／分散式環境下特別需要區分 API 與 SDK？
在單機時代，API 與 SDK 往往同時安裝於本機，差異不明顯；到了雲端，API 多半成為線上 HTTP/REST 服務，使用者只要會下 HTTP 就能呼叫。此時 SDK 的價值在於：
1. 把重複、瑣碎的呼叫細節封裝起來。  
2. 針對不同語言／平台提供最佳化的 Library。  
3. 提供額外的工具（產生程式碼、快取、效能最佳化等）以提高開發效率。

## Q: 為什麼要替自己的 API 開發專屬 SDK？
若沒有 SDK，每位使用者都得重複撰寫同樣的 HTTP 呼叫、JSON 反序列化與分頁處理等樣板程式碼。文章中的範例證明：  
• 在主程式加上一行 `new Demo.SDK.Client(...)` 就能省去原本約 150 行的重複程式。  
• SDK 讓開發者專注於商業邏輯，減少錯誤與維護成本。

## Q: API／SDK 更新時會遇到哪些典型風險？
當 API 版本升級（例如欄位名稱由 SerialNo 改為 BirdNo）卻未同步更新 SDK 或使用者的 APP 時，APP 可能無法正確運作，甚至產生不可預期的行為。風險點包括：  
1. API／Server 端與 SDK 端的資料格式不一致。  
2. APP 延遲升級 SDK，造成新舊版本並存。  
3. 無法快速定位問題來源（Server？SDK？APP？）。

## Q: 如何透過「合約（Contract）」機制降低版本衝擊？
做法是在 Solution 中獨立出 `Demo.Contracts` 專案，把所有 API Data Model 與 SDK Client 介面以 C# Interface／Class 的形式「程式碼化」。  
• Server、SDK、APP 皆引用同一份 Contracts。  
• 任何對 Contracts 的變更都需由架構師／Product Owner 控制並記錄版本。  
• 只要編譯能通過，就代表各端遵守相同合約，藉此大幅降低不一致風險。

## Q: 在 .NET 範例中如何實作 APP 與 SDK 之間的相容性？
1. 於 `Demo.Contracts` 內定義 `ISDKClient` 介面。  
2. SDK 端 (`Demo.SDK.Client`) 實作該介面，並使用 Factory Pattern 暴露 `Create()` 方法。  
3. APP 只透過 `ISDKClient` 操作，而非直接依賴具體實作。  
如此一來，只要 `ISDKClient` 不變，APP 更新 SDK DLL 即可；若介面變動，編譯器會立即提示需要重建或修改程式。

## Q: 更新責任分工為何？（API、Server、SDK、APP）
• API 定義與 Server 端：由原廠即時更新。  
• SDK：原廠發布新版，APP 開發者決定何時採用。  
• APP：由開發者自行排程升級。  
透過 Contracts 與版本策略，可在「原廠已更新、APP 尚未升級」的期間內維持服務相容。

## Q: 第一版 SDK 帶來的立即成效是什麼？
• APP 主程式變得簡潔易讀，只處理真正的商業邏輯。  
• 呼叫 API 的樣板程式碼集中於 SDK，利於統一維護。  
• Server 分頁、JSON 解析、錯誤處理等細節被完全封裝。  
• 為後續加入快取、重試、效能優化等功能奠定基礎。

## Q: 文章後續還會討論哪些議題？
作者將在下一篇繼續探討：  
• API 的版本控制策略。  
• 如何設計向前相容（Backward Compatibility）的機制。  
• 進一步完善 CI/CD 流程與線上維運做法。