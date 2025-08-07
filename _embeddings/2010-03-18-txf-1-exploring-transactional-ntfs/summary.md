# [TxF] #1. 初探 Transactional NTFS

## 摘要提示
- Transactional NTFS: Vista/2008 首度內建的檔案「交易」功能，並非新檔案系統而是一組 Win32 API。
- API 對等: 幾乎與既有檔案 API 一對一對應，開發者可用相似語意撰寫具交易性的檔案操作。
- TxF 與 TxR: 同期推出的還有針對 Registry 的 Transactional Registry（TxR），概念一致。
- 分散式交易: 搭配 DTC 及 .NET TransactionScope，可把檔案、資料庫等多來源包成單一分散式交易。
- 開發方式: 目前無官方 managed wrapper，只能用 C/C++ 或 P/Invoke，或採第三方封裝。
- 代碼示例: 文章展示約 30 行 C# + P/Invoke 即能完成「批次刪檔且可 Rollback」的範例。
- AlphaFS: 開源專案提供 System.IO.* 的替代實作，內建 TxF 支援，是 .NET 開發者可考慮的方案。
- 技術價值: 在檔案層得到資料庫等級的 ACID 特性，能提升應用程式可靠度與一致性。
- 框架缺口: 雖有 System.Transactions 整合，但 TxF 仍未正式併入 .NET Framework 基礎類別庫。
- 系列展望: 作者預告後續文章將深入 TxF + DTC + TransactionScope 的實戰與效能議題。

## 全文重點
作者長久以來想研究 Transactional NTFS（TxF），終於在過年期間動手。TxF 自 Windows Vista / Windows Server 2008 開始提供，讓開發者能以交易（Transaction）的方式操作檔案，且 API 與傳統檔案 API 幾乎一一對應，使用者不必學習全新語法。除檔案外，微軟也推出對 Registry 的 TxR。TxF 最大魅力在於可與 Distributed Transaction Coordinator（DTC）整合，將檔案 I/O 與資料庫存取放入同一個分散式交易，任何一環失敗即可整體回復，彷彿把檔案當成資料庫來使用。

目前的障礙是缺乏官方 managed library；開發者必須選擇 C/C++ 直接呼叫 Win32 API、在 C# 透過 P/Invoke，或是採用他人封裝的 .NET Class Library。文章以簡短 C# 範例示範如何建立交易、刪除多個檔案並在失敗時 Rollback。雖然 P/Invoke 不盡理想，但仍是堪用方案。若追求較乾淨的 .NET 使用體驗，可透過 TransactionScope 或利用支持 TxF 的開源專案 AlphaFS，它旨在取代 System.IO.*，並納入更多先進功能。作者最後列出多篇官方與社群文件，並預告未來將持續整理實務心得，尤其著墨於 TxF 與 DTC 的結合與效能考量。

## 段落重點
### 1. 動機與背景
作者長期想實驗 TxF，終於抽空開始研究。本篇定位為概念介紹，不深入程式碼，先說明 TxF 基本面與可能用法，為系列文章開場。

### 2. 什麼是 Transactional NTFS
TxF 並不是全新檔案系統，而是 Windows 自 Vista 起提供的一組 Win32 API，可讓檔案操作具備 ACID 特性。同期另有處理 Registry 的 TxR。

### 3. 交易式檔案帶來的想像
以往只有資料庫提供交易；透過 TxF，檔案 I/O 也能 rollback。若再結合 DTC，可把檔案與資料庫打包為單一跨資源交易，失敗即可整體回復。

### 4. 現階段可行的開發方式
微軟未提供官方 managed wrapper，開發者常用三法：C/C++ 直接呼叫、C# P/Invoke、或使用第三方封裝。各方法雖可行，但 P/Invoke 程式碼不甚優雅。

### 5. C# + P/Invoke 範例
文章展示建立交易、批次刪檔、Commit / Rollback 的範例，僅二三十行即可完成，證明 TxF API 易於上手，即使代碼稍顯原始。

### 6. DTC 與 TransactionScope 整合
若要進一步優化，可在 .NET 透過 TransactionScope 讓 TxF、TxR、Database 同屬一個分散式交易，無須直接操作繁瑣的 COM 介面。

### 7. AlphaFS 與其他替代方案
對有「程式碼潔癖」的開發者，AlphaFS 提供 System.IO.* 的替代版本並內建 TxF，使用體驗更符合 .NET 習慣，是實務開發的推薦方案。

### 8. 結語與後續計畫
本文僅為 TxF 預覽，展示其能力與整合方向；作者將於後續文章深入討論 TxF + DTC 的實戰技巧與效能議題，並整理更多資源。

### 9. 延伸閱讀與參考
附上 AlphaFS、MSDN Magazine 文章、部落格與 CodeProject 範例及官方文件，方便讀者進一步研究 TxF 的應用、最佳實踐與效能考量。