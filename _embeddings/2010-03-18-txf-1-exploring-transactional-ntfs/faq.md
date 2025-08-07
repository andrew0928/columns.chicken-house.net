# [TxF] #1. 初探 Transactional NTFS

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 Transactional NTFS (TxF)？
Transactional NTFS 並不是全新的檔案系統，而是一組與既有檔案 API 幾乎一對一對應的「交易式」Win32 API，讓開發者能以資料庫交易的方式對檔案進行讀寫、刪除等操作，可在同一交易中進行 Commit 或 Rollback。

## Q: TxF 首次在哪些 Windows 版本中正式提供？
TxF 首度隨 Windows Vista 與 Windows Server 2008 一同正式對外釋出。

## Q: 使用 TxF 進行檔案操作有什麼好處？
透過 TxF，可將多個檔案動作包裝成單一交易；若其中任何一步失敗，可立即 Rollback，使檔案系統回到交易開始前的狀態，帶來與資料庫類似的 ACID 體驗。

## Q: 在 .NET Managed Code 中想用 TxF，目前有哪些方法？
1. 直接以 C/C++ 呼叫 Win32 TxF API。  
2. 透過 P/Invoke 在 C# 中呼叫這些 Win32 API。  
3. 採用第三方（非官方）封裝的 .NET 類別庫，例如 AlphaFS。

## Q: 微軟是否已在 .NET Framework 內提供官方的 TxF Managed Library？
沒有。至今 TxF 仍未被正式併入 .NET Framework，因而必須使用 P/Invoke 或第三方函式庫來存取。

## Q: Distributed Transaction Coordinator (DTC) 可以如何與 TxF 搭配？
DTC 可作為分散式交易協調器，將本機檔案 I/O（TxF）、登錄檔操作（TxR）及資料庫存取整合在同一個交易範圍內。在 .NET 中可透過 TransactionScope 使用 DTC 來管理這些跨資源的交易。

## Q: 作者提供的 TxF 範例程式流程為何？
1. 呼叫 `CreateTransaction` 建立交易物件。  
2. 以 `DeleteFileTransactedW` 等「支援交易」的 API 對檔案進行操作。  
3. 全部成功則 `CommitTransaction`；若有例外則 `RollbackTransaction`。  
4. 最後呼叫 `CloseHandle` 釋放交易物件。

## Q: 有沒有開源專案可取代 System.IO.* 並內建 TxF 支援？
有，AlphaFS 專案目標是完全取代 System.IO 命名空間，額外提供 TxF、長路徑等進階檔案系統功能，適合想在 .NET 中平滑使用 TxF 的開發者。

## Q: 進一步瞭解 TxF 還可以參考哪些資源？
文章列出多個參考連結，包括  
‧ AlphaFS 專案（alphafs.codeplex.com）  
‧ MSDN Magazine 2007/07 之 TxF 文章  
‧ Bart De Smet 的三篇 TxF+C# 系列文章  
‧ CodeProject「Windows Vista TxF / TxR」教學  
‧ MSDN 上的 TxF 效能與使用時機說明等。