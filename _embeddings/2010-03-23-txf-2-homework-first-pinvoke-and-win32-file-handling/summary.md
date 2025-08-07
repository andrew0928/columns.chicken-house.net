# [TxF] #2. 先作功課 - 熟悉 P/Invoke 及 Win32 檔案處理

## 摘要提示
- P/Invoke簡介: 在 .NET 中呼叫 Win32 API 需用 P/Invoke，這是使用 Transactional NTFS 的前置技能。  
- MoveFile範例: 透過 MoveFile 示範最精簡的 DllImport 宣告與 extern 關鍵字用法。  
- extern與DllImport: extern 表示外部函式，DllImport 指定來源 DLL 與對應簽章。  
- HANDLE與IntPtr: Windows 將各種資源以 HANDLE 管理，於 managed 端以 IntPtr 橋接。  
- CreateFile/CloseHandle: 以 P/Invoke 開啟檔案後，可將取得的指標交給 FileStream 操作。  
- SafeHandle取代IntPtr: .NET 2.0 起鼓勵用 SafeFileHandle 包裝 HANDLE，藉 IDisposable 自動回收。  
- 與System.IO整合: FileStream 內建可接受 SafeFileHandle 的建構式，無縫使用非受控句柄。  
- 實務配合TxF: 只要熟悉標準檔案 API，即可掌握八成以上 TxF 的交易式檔案操作。  
- 工具資源: 建議利用 pinvoke.net 與 MSDN 查詢正確簽章與旗標值。  
- 後續文章預告: 下一篇將正式示範「交易式」檔案處理，請備妥 Vista/2008/7/2008 R2。  

## 全文重點
本文屬於「交易式 NTFS」系列的前置篇，目的在於讓 C# 開發者先熟悉呼叫原生 Win32 檔案 API 的技巧。由於 TxF 目前僅提供非受控介面，想在 .NET 中使用就得依賴 P/Invoke。文章首先說明 extern 與 DllImport 的基本寫法，並以 MoveFile 為入門範例，示範如何在 managed 端宣告並呼叫該函式。接著作者說明 Windows 以 HANDLE 管理系統資源，介紹 CreateFile/CloseHandle 的簽章，並示範把取得的 IntPtr 直接交給 FileStream 讀取檔案內容。  
.NET 2.0 之後 IntPtr/CloseHandle 的做法被標示為過時，建議改用 SafeFileHandle。SafeFileHandle 派生自 SafeHandle，實作了 IDisposable，可在例外或 GC 發生時自動釋放底層 HANDLE，使用上更安全。作者隨即提供改寫範例：以 SafeFileHandle 取代 IntPtr，並透過 FileStream(SafeFileHandle, FileAccess) 的建構式直接讀檔，最後再呼叫 SafeHandle.Close() 釋放。  
除了程式碼講解，作者也提醒讀者要查 MSDN 了解各種旗標值，並推薦 pinvoke.net 作為快速取得 C# 簽章的工具。文末指出，只要把標準檔案 API 搞懂，未來切入 TxF 幾乎沒障礙；下一篇將出現第一個真正的「交易式」檔案範例，鼓勵讀者先準備好支援 TxF 的作業系統。  

## 段落重點
### 前言：為何要先學 P/Invoke
TxF 只暴露非受控 Win32 API，缺乏 managed library，因此在 .NET 使用 TxF 勢必要透過 P/Invoke。作者不打算深入語法細節，而是聚焦在檔案 API 的實戰，藉此奠定後續交易式檔案操作的基礎。

### MoveFile API 與最基礎的 P/Invoke
從最簡單、沒有指標與 HANDLE 的 MoveFile 著手，說明原生簽章 BOOL WINAPI MoveFile(LPCTSTR, LPCTSTR)；再展示對應的 C# 聲明 `[DllImport("kernel32.dll")] static extern bool MoveFile(string, string);`，強調 extern 與 DllImport 的角色。

### 範例一：呼叫 MoveFile 並驗證結果
以 Console 程式示範將 C:\file1.txt 搬移為 C:\file2.txt。執行前後透過 DIR 指令比對，證實 managed 程式成功呼叫 Win32 API。此例奠基於單純字串參數，屬於入門級練習。

### HANDLE、IntPtr 與 CreateFile
引入 Windows 核心概念 HANDLE，說明它比傳統指標多了系統管理機制。在 C# 端以 IntPtr 作為對應型別。接著列出 CreateFile 與 CloseHandle 的 DllImport 簽章，並解釋各旗標含意，以便日後能自行查 MSDN 組合。

### 範例二：以 IntPtr 整合 System.IO
用 CreateFile 取得檔案 HANDLE，直接傳給 `new FileStream(IntPtr, FileAccess)`，隨後以 StreamReader 讀取全文，再手動呼叫 CloseHandle。程式雖能運作，但會觸發過時警告，顯示此構造函式已被淘汰。

### SafeHandle 的出現與範例三
介紹 SafeHandle 階層與資源安全性優勢；示範改用 SafeFileHandle 版的 CreateFile 宣告，並改以 `new FileStream(SafeFileHandle, FileAccess)` 開檔。最後僅需 `SafeHandle.Close()` 即可釋放，整體更符合 .NET 設計理念。

### 小結與後續預告
回顧呼叫 Win32 API 的主要步驟：宣告簽章、對應型別、處理旗標、妥善釋放 HANDLE。掌握這些，就已具備八成 TxF 能力。作者預告下一篇將正式示範交易式檔案操作，並提醒使用者準備支援 TxF 的新一代 Windows。

### 參考資源
列出 pinvoke.net 供快速查詢 C# 簽章；MSDN MoveFile 文件供旗標與回傳值參照；Wikipedia 的 P/Invoke 條目提供背景；以及 MSDN 上關於 SafeHandle 與 Critical Finalization 的深入說明。