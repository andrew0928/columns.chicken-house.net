# 替 App_Code 目錄下的 code 寫單元測試 ?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 ASP.NET 2.0 的 App_Code 目錄下編寫的程式碼，用傳統單元測試框架 (Microsoft Unit Test Framework、NUnit) 很難測試？
1. App_Code 目錄的原始碼在執行時由 ASP.NET 動態編譯，沒有固定且可預期的 *.dll 可以被測試工具載入。  
2. 編譯後的組件被放在 `c:\Windows\Microsoft.NET\Framework\Temporary ASP.NET Files\`，路徑經過雜湊編碼且每次可能不同，手動定位十分不便。  
3. NUnit 等 Test Runner 會在獨立的 AppDomain 內執行測試；然而 App_Code 中的程式碼普遍依賴 ASP.NET Hosting 環境 (如 HttpContext)。在沒有 Hosting 環境的 AppDomain 中，相關程式碼便無法執行，導致測試失敗或無法進行。

## Q: 作者最後用什麼方法成功替 App_Code 程式碼撰寫並執行單元測試？
作者改用 NUnitLite。NUnitLite 採用「以原始碼形式嵌入」的方式，不會另外啓動獨立的 AppDomain，也不需要事先編譯出 dll，因此可以直接在 ASP.NET Hosting 環境裡執行測試，成功解決了 App_Code 測試的障礙。

## Q: 與完整版 NUnit 相比，NUnitLite 有哪些精簡設計讓它適合在 ASP.NET Hosting（或其他受限環境）中跑測試？
1. 不使用獨立的 AppDomain ─ 測試可以在目前的 Hosting 環境內直接執行。  
2. 無 GUI、無多執行緒與可插拔擴充機制 ─ 大幅降低資源需求並簡化相依性。  
3. 以「原始碼」方式發佈 ─ 測試專案只要把 NUnitLite 的 source code 納入即可，不需額外安裝或參考外部 dll。  
這些特性使它能在資源受限或必須受控於特殊執行環境（例如 IIS 與 ASP.NET）的情況下順利運作。

## Q: 如果硬把需要測試的程式碼抽離 ASP.NET Hosting 環境再測試，可行嗎？
成效有限。大多數 ASP.NET 程式都會接觸到 HttpContext（Application、Session、Request、Response 等），真正完全不依賴這些物件的程式碼比例很低。即使將程式碼抽離出來測試，也只能覆蓋少數邏輯，整體錯誤風險仍高，因此不算理想方案。

## Q: 文章最後對 NUnitLite 的評價是什麼？
雖然目前版本僅 0.1.0.0，甚至最新釋出尚未能直接 build，但它已經能有效解決作者在 App_Code 單元測試上的主要問題，因此被視為「救星」並給予正面評價。