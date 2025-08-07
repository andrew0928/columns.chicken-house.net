# .NET Core 跨平台 #5 ─ 多工運算效能大考驗：計算圓周率測試

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 這次測試的目的是什麼？
透過計算 10000 位圓周率的 CPU-bound 工作，比較 .NET Core 在不同作業系統與虛擬／容器環境下的多核心運算效能，並藉此了解各平台在 JIT、執行緒與排程機制上的差異。

## Q: 為什麼選擇「計算 10000 位圓周率」當作測試項目？
計算高位數圓周率會大量佔用 CPU，但幾乎不消耗 I/O 與記憶體，非常適合作為純 CPU-bound 基準測試，能直接觀察執行緒排程與 JIT 編譯效能。

## Q: 測試使用了哪些效能指標？
1. Total Execute Time：所有工作全部完成所花的總時間。  
2. Average Execute Time：單一 Task 完成時間的平均值。  
3. Efficiency Rate (%)：平行處理帶來的整體效益提升百分比。

## Q: 參與測試的作業系統／環境有哪些？
1. Windows Server 2012 R2 (Server Core)  
2. Windows Server 2016 TP4 Nano Server（Windows Container 內）  
3. Ubuntu 15.10 + Docker (image: microsoft/dotnet)  
4. Boot2Docker 1.9 + Docker (image: microsoft/dotnet)  
5. 實體機對照組：Windows 10 Enterprise

## Q: 在多核心（4 Core / 8 Core）情境下哪個平台效能最好？
Windows Server 2016 Tech Preview 4 Nano Server 取得最佳 Total Execute Time 與最高 Efficiency Rate，整體領先其他平台。

## Q: 單核心環境下最快的是誰？
在 1 Core 測試中，最輕量的 Boot2Docker 1.9 提供了最短的執行時間。

## Q: 測得的最高 Efficiency Rate 為多少？出現在哪個平台？
最高 Efficiency Rate 為 531%，出現在 Windows Server 2016 TP4 Nano Server 於 8 Core 測試時。

## Q: Ubuntu 在此次測試中的表現如何？
Ubuntu 15.10 + Docker 在 Total Execute Time 與 Average Execute Time 均敬陪末座，為四個虛擬／容器平台中最慢。

## Q: 從結果看，選擇執行 .NET Core 的最佳平台建議是什麼？
如果首要考量是運算效能並且開發語言為 C#，選擇 Windows Server（特別是 2016 版）相對較有利；然而各平台差距約 10% 左右，實務上仍須綜合管理、維護成本與系統相容性再做決定。

## Q: 為何 .NET Core 在 Windows 上仍顯著領先？
Microsoft 對 Windows 平台的 JIT 編譯器、執行緒與排程機制掌握度最高，最佳化投入亦較多，故在同樣硬體條件下展現出更佳的執行效率。