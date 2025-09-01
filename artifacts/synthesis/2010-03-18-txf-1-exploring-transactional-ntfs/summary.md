# [TxF] #1. 初探 Transactional NTFS

## 摘要提示
- Transactional NTFS(TxF): 在 Windows Vista/2008 首度提供，讓檔案操作具備交易特性的一組 Win32 API，而非新的檔案系統
- TxR: 與 TxF 同期推出的 Transactional Registry，提供登錄檔的交易式操作
- API 等價性: 幾乎對應既有檔案 API 的一對一版本，新增交易語意
- 開發方式: 可用 C/C++ 呼叫 Win32、C# 以 P/Invoke、或採用第三方 .NET 封裝
- 交易整合: 可配合 DTC，將檔案 I/O 與資料庫操作納入同一個分散式交易
- TransactionScope: 在 .NET 世界中以 TransactionScope 統一包裝 TxF、TxR 與 DB 交易
- 範例重點: 以 CreateTransaction、DeleteFileTransactedW、Commit/RollbackTransaction 示範交易式刪檔
- .NET 缺口: 官方未提供內建的 managed library，使用體驗不若純 .NET 直覺
- AlphaFS: 可替代 System.IO.* 的開源專案，提供 TxF 支援與進階檔案功能
- 後續規劃: 系列文將續談使用情境、搭配 DTC 的作法與更多實作細節

## 全文重點
本文作為系列文開篇，介紹 Transactional NTFS（TxF）的定位、使用方式與整體價值。TxF 並非一個全新的檔案系統，而是 Windows 自 Vista/Server 2008 起提供的一組交易式檔案操作 API，幾乎與既有 Win32 檔案 API 一對一對應，讓檔案操作具備資料庫常見的交易語意：要嘛全部成功、要嘛全部回滾。同期也有針對 Registry 的交易式功能（TxR）。

作者分享了在 .NET 環境中使用 TxF 的幾種路徑：直接以 C/C++ 呼叫 Win32 API、在 C# 用 P/Invoke、或採用第三方封裝好的 .NET 類別庫。雖然 P/Invoke 並非長久之計、型別不如純 .NET 直覺，但就功能而言已可實作可靠的交易式檔案流程。文中示範以 CreateTransaction 建立交易，逐一以 DeleteFileTransactedW 刪除多個檔案，最後依成功與否決定 Commit 或 Rollback，展現「把檔案操作當成資料庫交易」的直覺與穩定性。

更進一步，TxF 能與 Distributed Transaction Coordinator（DTC）整合，將本機檔案 I/O 與資料庫存取納入同一個分散式交易，達成跨資源一致性。在 .NET 世界裡，這樣的整合應以 TransactionScope 為主軸，TxF、TxR、資料庫都能在同一範圍內管理。不過作者指出，微軟雖已在平台層面完成關鍵能力，卻尚未把 TxF 正式納入 .NET Framework 的 managed library，導致開發體驗仍需要 P/Invoke 或 COM 介面，與一般 .NET 程式風格有所落差。

對希望以 .NET 友善方式採用 TxF 的開發者，作者推薦開源專案 AlphaFS。AlphaFS 目標是作為 System.IO.* 的替代方案，維持熟悉用法的同時帶來更完整的 Windows 檔案系統支援，其中包含對 TxF 的支援，適合想在 .NET 中落地交易式檔案操作的團隊。文末提供多篇參考資源，包括 MSDN Magazine 的介紹、部落格系列與 CodeProject 範例，並預告後續將分享更多研究心得與應用情境，包含搭配 DTC/TransactionScope 的實作方向。

整體而言，TxF 的價值在於把「交易」這種可預期、可回復的語意帶進檔案系統操作，讓檔案處理能以接近資料庫的可靠度來組織工作流程；配合 DTC，還能把跨資源的一致性納入同一套交易機制。雖然目前在 .NET 層缺乏官方 managed 支援，但透過 P/Invoke、COM 介面或 AlphaFS 仍然可行，足以在需要強一致性的檔案場景中發揮作用。

## 段落重點
### 緒論：為何關注 TxF
作者長期想研究 TxF，本文先聚焦概念與應用價值，不著墨太多程式碼。目標是讓讀者理解交易式檔案操作能解決什麼問題、可如何善用，以及相關資源與後續方向，詳細實作將留待系列文續篇。

### TxF 與 TxR 的定位與特性
Transactional NTFS（TxF）自 Windows Vista/2008 首度提供，名稱雖含 NTFS，實際是提供交易語意的一組 Win32 API，而非新檔案系統；其 API 幾乎對應傳統檔案 API。一同推出的還有 TxR（Transactional Registry），以類似方式為登錄檔提供交易式操作。這使得以往僅見於資料庫的「全成全敗」與回復能力，首次在檔案與登錄檔領域成為可用選項。

### .NET 使用途徑與程式碼示例
在 .NET 目前沒有官方 managed library 的情況下，使用方式包括：C/C++ 直呼 Win32、以 C# 的 P/Invoke 包 Win32、或採用第三方封裝。作者以簡短範例展示 CreateTransaction 建立交易，針對多個檔案呼叫 DeleteFileTransactedW，成功則 Commit、失敗則 Rollback，最後釋放 Handle。此流程讓批次檔案操作具備一致性與可回復性，貼近資料庫交易的使用體驗。

### 與 DTC/TransactionScope 的整合思路
若不滿足於直接呼叫 API 的粒度與風格，可藉由 DTC 提供分散式交易協調，把本機檔案 I/O 與資料庫存取納入同一交易範圍。在 .NET 開發中，建議以 TransactionScope 作為統一入口，TxF、TxR、以及資料庫資源都能受其管理。作者未貼示例，主因是 COM 介面在 C# 程式風格上較為突兀，但觀念與方向清楚：利用 .NET 交易基礎設施，實現跨資源一致性。

### 官方支援缺口與 AlphaFS 替代方案
雖然平台能力充足，但微軟尚未將 TxF 正式併入 .NET Framework 的 managed 類別庫，導致開發體驗不若純 .NET 直觀。作者推薦 AlphaFS 作為 System.IO.* 的替代選項：維持相似 API 表面，同時提供進階功能與 TxF 支援，對需要在 .NET 中實作交易式檔案處理的團隊相當實用。

### 結語與後續規劃、參考資源
本文作為系列開篇，重在預覽 TxF 的能力、搭配 DTC/TransactionScope 的可能應用，以及可用資源。作者預告後續將陸續分享研究心得與實作細節。文末整理多個學習來源，包括 AlphaFS 專案頁、MSDN Magazine 文章、相關部落格系列與 CodeProject 範例，提供讀者深入探索與動手實作的起點。

## 資訊整理

### 知識架構圖
1. 前置知識：
   - 基本檔案系統與 NTFS 概念
   - 交易（Transaction）基本原理：ACID、commit/rollback
   - Windows 平台與 Win32 API 基礎
   - .NET/C# 基礎與 P/Invoke 使用概念
   - 分散式交易與 DTC（Distributed Transaction Coordinator）概念
2. 核心概念：
   - Transactional NTFS（TxF）：以交易方式操作檔案的 Win32 API 集合，不是新的檔案系統
   - Transactional Registry（TxR）：以交易方式操作 Windows Registry 的對應 API
   - KTM（Kernel Transaction Manager）：建立與管理交易物件的核心機制（CreateTransaction 等）
   - System.Transactions 與 TransactionScope：在 .NET 內整合 TxF/TxR/資料庫的交易邏輯
   - DTC：跨資源（檔案、資料庫等）的分散式交易協調
   彼此關係：TxF/TxR 提供交易化的 I/O API，KTM 管交易，.NET 端可用 TransactionScope 包裝，跨資源時由 DTC 協調。
3. 技術依賴：
   - 作業系統層：Windows Vista/Server 2008（起）支援 TxF/TxR
   - 原生 API：CreateTransaction、CommitTransaction、RollbackTransaction、DeleteFileTransactedW 等
   - .NET 與互通：P/Invoke 呼叫 Win32；或使用第三方 .NET 函式庫（如 AlphaFS）
   - 分散式交易：COM 介面與 DTC；.NET 透過 System.Transactions 橋接
4. 應用場景：
   - 需要檔案操作具備原子性與可回復性的情境（例如批次刪檔/搬移、組態檔更新）
   - 將檔案 I/O 與資料庫更新打包在同一交易中，確保一致性
   - 需要透過 TransactionScope 管理多個資源的一致性（TxF + TxR + DB）

### 學習路徑建議
1. 入門者路徑：
   - 了解交易基本概念與 NTFS 基礎
   - 讀過 TxF/TxR 是 API 不是新檔案系統的觀念
   - 寫一個最小 P/Invoke 範例：CreateTransaction + DeleteFileTransactedW + Commit/Rollback
   - 瀏覽官方參考與入門文章（MSDN Magazine 範例）
2. 進階者路徑：
   - 在 .NET 使用 TransactionScope 將檔案刪除/建立與資料庫操作納入同一交易
   - 理解 DTC 的角色與何時會提升為分散式交易
   - 導入第三方函式庫（如 AlphaFS）以提升可讀性與開發體驗
3. 實戰路徑：
   - 為專案抽象出「交易化檔案服務」介面，封裝 TxF/AlphaFS 或退回一般 I/O 的策略
   - 建立整合測試：模擬中途失敗，驗證 rollback 對檔案與資料庫的一致性
   - 參考「何時使用 TxF」「效能考量」文件，針對批次量、鎖定、錯誤處理做實測與調校

### 關鍵要點清單
- TxF 定義: Transactional NTFS 是一組讓檔案操作具備交易語意的 Win32 API，而非新的檔案系統 (優先級: 高)
- TxR 對應: Transactional Registry 以相同理念對應到 Windows Registry 操作 (優先級: 中)
- API 對等性: TxF 幾乎為既有檔案 API 提供一對一的交易化版本（如 DeleteFileTransactedW）(優先級: 高)
- KTM 交易物件: 透過 CreateTransaction 建立交易、CommitTransaction/RollbackTransaction 完成/還原 (優先級: 高)
- .NET 官方支援缺口: .NET Framework 未內建正式 managed 包裝，需 P/Invoke 或第三方 (優先級: 高)
- 使用選項: C/C++ 直接呼叫 Win32、C# 以 P/Invoke、或採用第三方 .NET 函式庫 (優先級: 高)
- AlphaFS: 可作為 System.IO 的替代，提供 TxF 支援與更豐富的檔案系統功能 (優先級: 中)
- 與 TransactionScope 整合: 在 .NET 中以 TransactionScope 將 TxF/TxR/資料庫操作包進單一交易 (優先級: 高)
- DTC 分散式交易: 需要跨資源一致性時，DTC 提供協調能力（可能從本機提升為分散式）(優先級: 中)
- 原子性與回復性: TxF 帶來資料庫式的原子提交與失敗回復能力於檔案操作 (優先級: 高)
- 程式碼樣式考量: 純 P/Invoke 可行但不夠直覺，建議以抽象層或第三方庫改善可維護性 (優先級: 中)
- 範例重點: 以交易批次刪除多個檔案，任何一步失敗可整體 rollback (優先級: 高)
- 效能與使用時機: 需閱讀與評估「效能考量」「何時使用 TxF」的官方建議 (優先級: 中)
- 測試策略: 必須設計故障注入與整合測試，驗證 rollback 對檔案與資料庫的一致性 (優先級: 中)
- 參考資源: MSDN Magazine 文章、B# 部落格、CodeProject 範例與官方文件可作為實作指引 (優先級: 低)