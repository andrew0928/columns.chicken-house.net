# .NET Core 跨平台 #1, 我真的需要在 Linux 上跑 .NET 嗎?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 既然 .NET 在 Windows 上已經能正常執行，為什麼還要考慮在 Linux 上跑 .NET？
對開發者來說，.NET Core + Linux 至少帶來三項直接效益：  
1. 可以繼續沿用既有的 .NET 開發資源（BCL、Visual Studio 以及手上的 C# 程式碼）。  
2. .NET Core 本身開源，可立即受惠於全球 open-source 社群的維護與擴充。  
3. 官方保證的跨平台支援讓 .NET 程式能「名正言順」地在 Windows 之外的環境執行，進而和大量 Linux/open-source 解決方案自然整合。

## Q: 目前就把既有系統全部搬到 .NET Core + Linux 上值得嗎？
短期來看並不急迫。現階段 .NET Core 還在起步（僅 RC），整體生態與 4.6 版本的 .NET Framework 相比仍有落差，缺乏立即轉移的誘因；然而從長期投資角度，趁早了解與掌握 .NET Core 技術會是值得的準備。

## Q: 採用 .NET Core + Linux 在眼前最明顯的好處有哪些？
1. 既有 .NET 程式碼與工具可直接延用，降低學習與搬遷成本。  
2. 開源模式讓 Bug 修正與新功能能由社群快速推進。  
3. 拓寬部署平台的選擇，可與各式 open-source 元件（如 Nginx、Apache、Docker）做更緊密的混搭。

## Q: 從長遠角度投資 .NET Core + Linux 有哪些戰略價值？
1. 讓 .NET 在以 Linux 為大宗的雲端／開源生態維持市佔率，對抗 Java 等競品。  
2. 配合 Azure 支援 Linux 的市場需求，為微軟雲端服務帶來更多客戶與營收。  
3. 開放 .NET 可吸引並留住開發者社群，為未來十年的技術布局鋪路。

## Q: 微軟為何選擇將 .NET Core 開源並跨平台？
微軟需要在雲端時代跟上以 Linux 為主流的潮流。一旦開發者與客戶在 Azure 上大量使用 Linux，若 .NET 無法跟隨，等同於把市場拱手讓人；透過開源與跨平台，微軟得以提供更完整的整合服務，把使用者留在自家生態圈。

## Q: ASP.NET 5 在 Linux 上運行時，需要哪些配合調整？
由於 Linux 世界不會有 IIS，ASP.NET 5 必須透過 OWIN 抽象層，才能輕鬆掛載在 Nginx 或 Apache 背後執行（通常配合 Reverse Proxy 模式），而不再受限於 Windows 專屬的 IIS。

## Q: 過去哪些情境會讓架構師放棄 .NET、選擇純 Linux 方案？
1. 專案最終部署只允許使用 Linux（如某些非營利組織或授權費敏感的環境）。  
2. 需要搭配的 open-source 套件在 Windows 上水土不服或維護成本高。  
3. 為了簡化維運，希望整體環境「一條龍」統一在同一作業系統上。

## Q: .NET Core 的出現對 C# 與 Visual Studio 使用者意味著什麼？
開發者能保有熟悉的語言（C#）與最佳化的開發體驗（Visual Studio），同時獲得開源與跨平台的彈性；換言之，不必放棄原本的生產力，就能把產品部署到最適合、最具成本效益的平台。

## Q: 作者打算用哪些實驗比較 .NET Core 在不同平台的差異？
作者規劃了兩項測試：  
1. 記憶體管理差異 —— 以「Memory Fragment Test」觀察不同 OS／架構／GC 策略下的行為。  
2. 運算速度與效能 —— 以多執行緒計算 50,000 位數 π 的程式，分別在 Linux + Docker、Windows 2016 + Windows Container，以及 Windows 2012 R2（Host OS）執行並比較效能。