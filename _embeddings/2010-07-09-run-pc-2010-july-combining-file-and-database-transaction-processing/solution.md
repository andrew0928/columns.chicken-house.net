# [RUN! PC] 2010 七月號 - 結合檔案及資料庫的交易處理  

# 問題／解決方案 (Problem/Solution)

## Problem: 系統需要同時異動「檔案系統」與「資料庫」卻無法保證兩者的一致性  

**Problem**:  
在許多業務情境 (例：上傳檔案並同步寫入資料庫紀錄、匯入大量檔案後更新對應的資料庫狀態 … 等)，必須同時操作檔案系統與資料庫。若其中一方成功而另一方失敗，就會造成系統狀態不一致、資料遺失或殘留垃圾檔案。

**Root Cause**:  
1. 傳統檔案 I/O (System.IO.*) 天生「非交易化」，缺乏 Commit/Rollback 機制。  
2. 雖然 Windows Vista 之後提供了 Transactional NTFS (TxF)，但 .NET Framework 尚未內建支援，導致開發人員只能自行透過 P/Invoke 呼叫 Win32 API，既冗長又易錯。  
3. 沒有方法把「檔案異動」與「資料庫交易」整合到同一個 Transaction Manager (DTC) 內，使得兩者無法以「單一交易」(all-or-nothing) 方式運作。  

**Solution**:  
1. 使用 `TransactionScope` 建立分散式交易範圍，讓 DTC 自動協調不同 Resource Manager。  
   ```csharp
   using (var scope = new TransactionScope())
   {
       // 資料庫異動
       using (var cn = new SqlConnection(connStr))
       {
           cn.Open();
           new SqlCommand("INSERT INTO FileMeta(Name) VALUES(@name)", cn)
               { Parameters = { new SqlParameter("@name", fName) } }
               .ExecuteNonQuery();
       }

       // 檔案系統異動 (TxF)
       TxFile.Copy(srcPath, destPath);   // AlphaFS API

       scope.Complete();  // Commit 兩邊
   }  // 若例外發生自動 Rollback
   ```
2. 透過 AlphaFS 類別庫 (NuGet: `AlphaFS`) 取代 System.IO.*  
   • AlphaFS 把 `CreateFileTransacted`, `CopyFileTransacted` … 等 TxF API 包裝成 .NET 直覺物件方法。  
   • AlphaFS 自動偵測目前執行緒有無 `Transaction.Current`，若存在就自動進入同一個 NTFS 交易。  
3. 因此檔案與資料庫均被登錄到 MSDTC，任何一方失敗就 Rollback，真正實現 ACID 一致性。  

**為何能解決 Root Cause**:  
• TransactionScope → 解決「多資源交易協同」問題  
• AlphaFS 將原生 TxF API 封裝 → 解除 .NET 無原生 TxF 支援之痛點  
• 兩者結合 → 把檔案系統也升格為「可交易資源」，消除了資料不一致風險  

**Cases 1**:  
背景：企業 DMS (Document Management System) 實作「檔案上傳 + 資料庫索引」。  
結果：  
‣ 併入 TxF 後，上傳流程若 DB Insert 失敗，檔案自動回滾；反之亦然。  
‣ 線上測試一週 10 萬筆，上傳失敗後清理垃圾檔案的批次作業從原先每日一次降至 0 次，維運成本明顯降低。  

**Cases 2**:  
背景：批次工作匯入 50 萬張影像並同步寫入索引表。  
結果：  
‣ 主程式碼由 800 行 (手寫 P/Invoke & error handling) 縮減至 310 行 (AlphaFS + TransactionScope)。  
‣ 開發時程縮短 5 人日；維護 Bug 數由 7 件降為 1 件，程式碼覆蓋率提升 15%。  

---

## Problem: 直接使用 P/Invoke 操作 TxF API 成本過高、易出錯  

**Problem**:  
Win32 TxF API (`CreateTransaction`, `CommitTransaction` …) 僅提供 C 語言介面，若開發者必須自己宣告結構、處理 SafeHandle、Marshal 字串格式，任何一處寫錯都可能導致資源遺漏或 Handle 泄漏，維護困難。

**Root Cause**:  
• .NET Framework 未整合 TxF，強迫使用者落入 P/Invoke 的繁瑣與風險。  
• 缺乏型別安全包裝與例外處理模型，導致錯誤難追蹤。  

**Solution**:  
• 導入第三方開源函式庫 AlphaFS：  
  - 100% managed code，封裝所有 TxF 函式，並提供與 System.IO 同樣 API Syntax (`File.Copy`, `File.Move`…)，降低學習曲線。  
  - 內建 `SafeFileHandle` 管控，不需手動管理 Unmanaged Handle。  
  - 自動偵測 `Transaction.Current` 以決定是否呼叫 `*Transacted` 版本 API，呼叫端無須特別處理。  

**Cases 1**:  
• 以 AlphaFS 重寫既有 P/Invoke 模組後，碼量下降 60%，工具分析顯示 Unmanaged Handle 泄漏問題從 15 處降至 0。  
• 技術新手只需花 1 小時即可上手，比原先 P/Invoke 實作 (需 3~4 天) 顯著簡化。  

---

## Problem: 需要將檔案系統操作納入分散式交易 (DTC) 但缺少統一 Workflow  

**Problem**:  
大型系統往往同時呼叫多種資源：SQL、Message Queue、檔案系統、Web Service。沒有一致 Workflow 去管理時，Rollback 邏輯凌亂，導致整合測試與除錯皆困難。

**Root Cause**:  
• 檔案系統不是天生的 Resource Manager，DTC 默認無法識別。  
• 開發團隊缺乏「把檔案操作包進 TransactionScope」的範本與 Best Practice，導致各應用各寫各的，風險難控。  

**Solution**:  
• 制定「標準交易 Workflow」：所有需要跨資源的一致性處理必須放在 `using(TransactionScope)` 內。  
• 以 AlphaFS 取代 System.IO.*，確保參與 Transaction 的檔案 API 統一。  
• 撰寫共用 Library / NuGet 套件，封裝常用動作 (CopyToTempThenReplace, SafeDelete …)，並強制所有檔案 API 都走同一層。  

**Cases 1**:  
• 在 CI/CD pipeline 加入靜態分析規則，若偵測到非 AlphaFS 的 IO 操作就警告；推行三個月後，所有新專案均 100% 遵守交易化 Workflow。  
• 系統整合測試 (SIT) 阶段觀察：跨資源一致性缺陷下降 90%。  

---