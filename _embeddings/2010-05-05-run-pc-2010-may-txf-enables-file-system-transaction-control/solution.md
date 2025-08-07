# [RUN! PC] 2010 五月號 ‑ TxF 讓檔案系統也能達到交易控制  

# 問題／解決方案 (Problem/Solution)

## Problem: 無法確保多步驟檔案作業的「一次到位」(Atomicity)

**Problem**  
在安裝程式、備份工具或任何需要「先複製 → 再刪除 → 最後重新命名」等多步驟檔案作業的情境下，若中途斷電或程式拋出例外，就會留下半套用的檔案，造成資料毀損，甚至影響系統正常開機。

**Root Cause**  
傳統 NTFS I/O 呼叫 (CreateFile、MoveFile、WriteFile …​) 完全獨立執行，檔案系統沒有「交易」觀念；一旦錯誤發生，已經完成的 I/O 無從回復，只能靠開發者自行寫「還原 (rollback)」程式碼。

**Solution**  
使用 Windows Vista 之後內建的 Transactional NTFS (TxF)。  
關鍵步驟：  
```csharp
using (var scope = new TransactionScope())
{
    File.WriteAllText(@"C:\Data\A.txt", "v1");
    File.Move(@"C:\Data\A.txt", @"C:\Data\B.txt");
    scope.Complete();          // 1 行指令 Commit
}
// 若任何例外或系統異常，KTM 自動 Rollback
```
TxF 透過 Kernel Transaction Manager (KTM) 把一組檔案異動寫入 WAL (write-ahead log)，只有在 `Commit` 時才真正套用；如發生錯誤，KTM 直接走還原流程，確保檔案系統回到「完全未執行」或「完全執行」的其中一種狀態。

**Cases 1**  
範例程式 (附件 TransactionDemo.zip) 在搬移檔案時，人工拔電源測試十次，重新開機後檔案名稱與內容皆維持原狀，驗證原子性。  

**Cases 2**  
某備份工具導入 TxF，程式碼量由 1 200 行降到 820 行；一年內「備份後檔案遺失」客服單由每月平均 15 件降為 0。  

**Cases 3**  
大型遊戲安裝程式將 1 500+ 個檔案複製動作包在一個 TransactionScope 中，安裝被強制中止後重新執行不需額外掃 Disk Clean，使用者回報的「安裝後檔案殘留」問題消失。

---

## Problem: 手工實作 Rollback 與同步機制，維護成本高

**Problem**  
沒有 TxF 時，開發者必須：  
1. 先複製備份檔  
2. 執行實際操作  
3. 失敗時再還原備份  
4. 多執行緒還得加鎖  
流程冗長又易漏錯，只要少寫一個 `catch` 或 `finally`，就可能留下垃圾檔案或產生併發衝突。

**Root Cause**  
缺乏作業系統層級的交易支援，使得「一致性」與「同步」問題落到應用程式層自行負責；而 Win32 / .NET 早期僅提供低階 Mutex / Critical Section，無法涵蓋跨行程、跨機器的檔案一致性。

**Solution**  
1. 建立 `CreateTransaction()` 取得 Tx Handle  
2. 以 `CreateFileTransacted`、`MoveFileTransacted`… 進行 I/O  
3. 由 `CommitTransaction()` 或 `RollbackTransaction()` 統一收尾  
TxF 內部整合鎖定與日誌回復機制，同時支援 MSDTC，讓交易可橫跨多行程甚至多台機器。  

**Cases 1**  
影像處理服務重構後，把 420 行自訂備份／還原程式碼縮減為 40 行 TransactionScope；Code Review 發現的檔案處理 Bug 量下降 70%。  

**Cases 2**  
批次結算程式原採目錄級別 Mutex，導致 15% Performance Penalty；改用 TxF 後，移除大範圍鎖定，作業吞吐量提升 20%。

---

## Problem: TxF 僅有 Win32 API，.NET 開發者呼叫門檻高

**Problem**  
TxF API (CreateFileTransacted、MoveFileTransacted…) 為原生 Win32 函式，需要 P/Invoke、HANDLE 管理、結構對齊與安全性設定，造成 .NET 團隊導入意願低，或導入後產生 HANDLE 泄漏、記憶體存取違例等新問題。

**Root Cause**  
TxF 發表時 .NET Framework 尚無對應封裝；直到 .NET 4.0 才加入 System.Transactions 的 DTC 自動提升能力，還是缺少完整檔案層封裝。

**Solution**  
A. 使用社群專案 AlphaFS：  
```csharp
using (var scope = new TransactionScope())
{
    Alphaleonis.Win32.Filesystem.Directory.DeleteTransacted(
        @"C:\Temp\Work", recursive:true);
    scope.Complete();
}
```  
B. 部分場景以簡易 P/Invoke Helper (隨文附連結) 直接封裝，並搭配 `SafeFileHandle + CriticalFinalizerObject` 避免 Handle 泄漏。  

**Cases 1**  
新人使用 AlphaFS，在 30 分鐘內完成「交易式刪除」功能；對照上一版純 P/Invoke 實作花費 1 天且仍出現 Handle 泄漏，再用 WinDbg 檢測方才發現。  

**Cases 2**  
CI 建置工具以 AlphaFS 重寫後，因減少 SafeHandle Finalizer 壓力，GC 時間縮短，整體建置流程加速 8%。