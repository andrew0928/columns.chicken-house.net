# [RUN! PC] 2010 七月號－結合檔案及資料庫的交易處理

## 摘要提示
- Transactional NTFS: 介紹 TxF 與 TransactionScope 的整合機制，將檔案與資料庫操作併入同一筆交易。  
- 過往問題: .NET 尚未原生支援 TxF，開發者必須透過複雜的 P/Invoke 呼叫 Win32 API。  
- AlphaFS 套件: 提供類似 System.IO 的 API，同時包裝多種 NTFS 進階功能，簡化 TxF 應用。  
- 實務範例: 文章附上可下載的示範程式，展示如何同時提交或回復檔案與資料庫異動。  
- 錯誤復原: 透過單一交易確保系統在任何例外狀況下皆可一致地回滾。  
- 效能考量: 結合交易時需評估 I/O 負載與資料庫鎖定時間，避免過長的交易區段。  
- 適用場景: 檔案與資料庫需同時保持一致性的業務，如批次匯入、檔案上傳附帶資料列寫入。  
- 系統需求: TxF 僅適用於 NTFS 檔案系統且需 Windows Vista／Server 2008 以上版本。  
- 未來展望: 微軟尚未將 TxF 納入 .NET Framework，但第三方函式庫已填補空缺。  
- 讀者互動: 作者提供下載連結並歡迎讀者回饋問題與心得。  

## 全文重點
本篇文章延續五月號對 Transactional NTFS（TxF）的基礎介紹，進一步說明如何將檔案系統的交易與 ADO.NET 或其他資料庫交易透過 TransactionScope 物件整合為單一可提交（commit）或回滾（rollback）的單元。首先，作者回顧傳統開發者若要在 .NET 環境呼叫 TxF，必須使用 P/Invoke 直接操作 Win32 API，不僅程式碼繁複、錯誤率高，也難以與現有的 System.IO 類別相容。接著文章引入 AlphaFS 這個第三方開源類別庫，該庫提供與 System.IO 幾乎一致的介面，但內部已支援多種 NTFS 進階機制，包括卷影複製（VSS）、硬連結（Hard Link）與本篇重點的 TxF。透過 AlphaFS，開發者只需將 using 區塊替換為 Alphaleonis.Win32.Filesystem，即可在 TransactionScope 中同時包裹檔案與資料庫操作。文章示範了建立 TransactionScope、開啟 SQL 交易、寫入資料列、再寫入檔案，最後一次性 Commit 的完整流程；若任何一步發生例外，TransactionScope 會自動 Rollback，確保檔案與資料庫狀態一致。作者也提醒，TxF 只能運作在 NTFS 上，且自 Windows 10 起 Microsoft 亦宣布 TxF 為 deprecated，實務導入須衡量系統版本與長期維護策略。此外，交易區段過長可能導致檔案鎖定或資料庫死鎖，建議開發者分割工作或使用暫存機制降低風險。文末作者貼出完整範例碼下載，邀請讀者給予回饋並討論在企業應用中的可行與限制。整體而言，本文提供了一條在現有 .NET 平台中實現跨層一致性交易的可行方案，並透過 AlphaFS 大幅降低實作門檻。

## 段落重點
### 引言：延續 Transactional NTFS 的探索
作者首先感謝 RUN! PC 編輯刊登續篇，並回顧五月號已介紹的 TxF 基礎與 P/Invoke 實作限制。目的在於讓開發者了解，單靠 System.IO 難以在 .NET 中同步檔案與資料庫的 ACID 特性，因此本期將聚焦「如何簡單整合」。

### TxF 與 TransactionScope 的整合技巧
說明 TransactionScope 的工作模式與分散式交易協調器（MSDTC）的角色，再示範如何透過 TxF 的檔案 API 參與同一個交易。示例程式碼包含建立 TransactionScope、執行 SQLCommand、利用 AlphaFS 寫入檔案，最後 Commit 或自動 Rollback，證明兩者可被視為一致單元。

### AlphaFS：消弭 P/Invoke 的痛點
介紹 AlphaFS 這個開源類別庫的背景及功能範圍，重點在於只需將 using 指向 Alphaleonis.Win32.Filesystem，原有 System.IO 語意幾乎不變，即可存取 TxF API。作者展示將先前繁瑣的 P/Invoke 重構成數行 AlphaFS 呼叫，大幅降低錯誤及開發成本。

### 實作示例與下載資源
提供讀者可下載的範例專案（RunPC-201007.zip），其中包含完整的 Visual Studio Solution、SQL 建置腳本與範例檔案。透過此範例，讀者可直接體驗透過單一按鈕觸發的檔案＋資料庫交易，並觀察例外時自動回滾的效果。

### 注意事項與未來展望
作者提醒 TxF 僅在 NTFS 且 Vista／Server 2008 以上系統可用，新版 Windows 對 TxF 的支援已進入維護模式，不建議依賴於核心業務邏輯；同時需考量交易持續時間、MSDTC 設定與效能影響。最後邀請讀者在部落格留言交流，並期待未來 .NET 能原生支援檔案交易或有更完善的替代解決方案。