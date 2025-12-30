---
layout: synthesis
title: "[TxF] #2. 先作功課 - 熟悉 P/Invoke 及 Win32 檔案處理..."
synthesis_type: summary
source_post: /2010/03/23/txf-2-homework-first-pinvoke-and-win32-file-handling/
redirect_from:
  - /2010/03/23/txf-2-homework-first-pinvoke-and-win32-file-handling/summary/
---

# [TxF] #2. 先作功課 - 熟悉 P/Invoke 及 Win32 檔案處理...

## 摘要提示
- 文章目的: 為使用 Transactional NTFS（TxF）預先熟悉 P/Invoke 與 Win32 檔案 API 的必要技巧。
- P/Invoke 基本觀念: 透過 DllImport 與 extern 在 C# 中呼叫 unmanaged 的 Win32 API。
- MoveFile 範例: 以最單純的 MoveFile API 示範 P/Invoke 的宣告與呼叫流程。
- HANDLE 與指標: Windows 以 HANDLE 抽象系統資源，P/Invoke 以 IntPtr 對應 unmanaged pointer。
- CreateFile 讀檔: 使用 CreateFile 取得檔案 HANDLE，再以 FileStream 包裝讀取內容。
- IntPtr 與相容性: 舊式以 IntPtr 建構 FileStream 已過時，建議改用安全控制代碼。
- SafeHandle/SafeFileHandle: 以 SafeHandle 系列安全管理 HANDLE 的生命週期與釋放。
- API 對應與 TxF: TxF API 與傳統 Win32 檔案 API 一一對應，先熟悉後者即掌握多數 TxF 用法。
- 旗標參數: Win32 API 大量使用 uint flags，實務可查文件或轉為 enum 以增可讀性。
- 實作資源: 推薦使用 PINVOKE.NET 與 MSDN 查詢正確的 C# 簽章與文件。

## 全文重點
本文作為 Transactional NTFS（TxF）系列的鋪陳，重點不在完整講解 P/Invoke 理論，而是以實作導向快速掌握在 C# 中呼叫 Win32 檔案 API 的方法。作者首先以 MoveFile 做為入門，示範如何用 DllImport 標註 kernel32.dll 並以 extern 宣告對應函式，即可在 managed 環境中直接呼叫 unmanaged API，並以簡單案例驗證搬移檔案的結果。接著深入到 Windows 資源管理概念：作業系統以 HANDLE 表徵各種資源（檔案、視窗等），而在 P/Invoke 世界則以 System.IntPtr 對映 unmanaged 的指標。延伸範例展示以 CreateFile 開檔，取得 HANDLE（IntPtr），再用 FileStream 包裝讀取檔案內容；此舉揭示了 .NET 的 IO 類別其實也是圍繞 Win32 HANDLE 進行包裝。

然而，使用 IntPtr 建構 FileStream 在 .NET 2.0 起已被標示為過時，建議改用 SafeHandle 系列（本文以 SafeFileHandle 示範）。SafeHandle 不僅封裝了原本的指標與 CloseHandle 釋放邏輯，還實作 IDisposable，能在適當時機自動釋放 unmanaged 資源，安全性與可靠性更高。作者透過將 CreateFile 的回傳型別改為 SafeFileHandle、以 FileStream(handle, FileAccess) 建構並最後呼叫 handle.Close()，完成等效且較安全的實作，並點出這正是 FileStream 提供多種「看似奇怪」建構式的原因：為了與 P/Invoke/Win32 HANDLE 無縫整合。

文章最後總結：呼叫 Win32 API 的關鍵在於正確對應型別（字串、指標/HANDLE、旗標）與簽章，掌握 MoveFile、CreateFile、CloseHandle/SafeHandle 等基本操作，即已具備應用 TxF 的八成能力。至於大量以 uint flags 表示的選項，可視需求轉為 enum 提升可讀性。作者同時提供實用資源（PINVOKE.NET、MSDN、Wiki）以供查詢正確簽章與語意。下一篇將進一步展示第一個「交易式」檔案處理範例，建議讀者準備具 TxF 支援的 Windows 版本（Vista/7/Server 2008/R2）。

## 段落重點
### 前言與目標：為 TxF 預作 P/Invoke 與 Win32 檔案處理功課
本文銜接前一篇 TxF 介紹，指出 TxF 僅提供 Win32 API，並無現成的 managed library，因此現階段在 .NET/C# 中使用 TxF 必須依賴 P/Invoke。作者強調本文不企圖全面講授 P/Invoke 與 Marshal 細節，而是以最務實的方式，聚焦「如何配合 Windows API 進行檔案處理」。原因在於 TxF 的新 API 幾乎與標準 Win32 檔案 API 一一對應，熟悉一般檔案 API 的 P/Invoke 用法，就等同掌握了多數 TxF 的實作基礎。文章將以檔案搬移與開啟讀取作為範例，逐步建立從簡到繁的呼叫模型。

### 以 MoveFile 入門：DllImport 與 extern 的最小可行示範
作者先以 MoveFile 這個不涉指標/Handle 的 API 起手，展示如何以 [DllImport("kernel32.dll")] 與 extern 宣告對應函式，並在 C# 中直接呼叫。範例以 C:\file1.txt 搬移到 C:\file2.txt，透過命令列前後狀態驗證成功。此段的重點在於：了解 extern 代表外部函式、DllImport 指定來源 DLL、以及 P/Invoke 在最單純情境下的回傳值處理（BOOL 對映為 C# 的 bool）。這個基礎步驟說明了 managed 與 unmanaged 邊界的最小接面，打通後續更進階案例所需的宣告與呼叫路徑。

### 進階到 HANDLE 與 CreateFile：以 IntPtr 串接 FileStream
在邁向讀寫檔案內容前，作者說明 Windows 世界以 HANDLE 代表系統資源，雖然本質上是指標，但由作業系統統一管理。接著示範使用 CreateFile 取得檔案 HANDLE（P/Invoke 簽章以 IntPtr 承接），再將該 IntPtr 傳入 FileStream 建構式，構成以 .NET IO 讀取檔案內容的橋接。此範例並帶出多個常見要點：CreateFile 的參數需提供權限、共用模式、建立行為與屬性旗標；而 IntPtr 是在 P/Invoke 世界對映指標的核心型別。這段範例最關鍵的體悟是：.NET 的 FileStream 等 IO 類別實則是對 Win32 HANDLE 的包裝，因此能直接從 Handle 建構，順利讀取內容。

### 從 IntPtr 過渡到 SafeHandle：避免過時建構式並提升安全性
作者指出以 IntPtr 建構 FileStream 的方式在 .NET 2.0 後被標示為過時，編譯器會給出警告，建議改用 SafeFileHandle。SafeHandle（此處以 SafeFileHandle 為具體實作）將 HANDLE 與釋放邏輯（原本需呼叫 CloseHandle）合而為一，並實作 IDisposable，使資源回收更安全、可靠，降低因遺漏 Close 或例外中斷導致資源洩漏的風險。作者提供等效的 SafeFileHandle 版本：CreateFile 直接回傳 SafeFileHandle，FileStream 以該 Handle 建構，最後呼叫 handle.Close() 即可。此段亦點出為何 FileStream 會有看似特殊的建構式：為與 P/Invoke/Win32 HANDLE 緊密整合之設計結果。

### 收斂與資源：掌握型別對應與旗標即可上手 TxF
總結上文，呼叫 Win32 API 的關鍵在於正確的簽章與型別對應：字串、布林、指標/HANDLE（IntPtr 或 SafeHandle）、以及大量以 uint 表示的 flags。本文刻意未將 flags 全部轉為 enum，是因為可讀性屬選配，查文件即可；但實務上轉為 enum 會更清楚。當 MoveFile、CreateFile、CloseHandle/SafeHandle 的基本技巧熟悉後，實作 TxF 幾乎沒有門檻，因其 API 與標準檔案 API 高度對應。最後提供實用資源：PINVOKE.NET 可查各 API 的 C# 簽章與工具，MSDN 可查 API 參數與語意，Wiki 可快速理解 P/Invoke。下一篇將示範第一個「交易式」檔案處理案例，建議準備具 TxF 支援的 Windows 作業系統。

## 資訊整理

### 知識架構圖
1. 前置知識：學習本主題前需要掌握什麼？
   - 基本 C# 與 .NET 程式設計（類別、方法、屬性、IDisposable）
   - Windows/Win32 檔案處理概念（檔案開啟、讀寫、搬移、資源釋放）
   - 非受控程式碼與指標概念（POINTER、HANDLE 的概念）
   - 基本 Windows 平台知識（kernel32.dll、Unicode/ANSI 字元集）

2. 核心概念：本文的 3-5 個核心概念及其關係
   - P/Invoke：在 C# 中宣告和呼叫 unmanaged 的 Win32 API 的橋樑
   - HANDLE 與 IntPtr：用 IntPtr 代表 unmanaged 的指標／控制代碼
   - SafeHandle/SafeFileHandle：以安全方式管理 HANDLE 的生命週期（IDisposable）
   - Win32 檔案 API：MoveFile、CreateFile、CloseHandle 等基本操作
   - 與 .NET IO 的銜接：用 FileStream 的「以 Handle 為參數」建構式進行讀寫
   關係：P/Invoke 連結到 Win32 API；Win32 API 回傳 HANDLE；在 .NET 端用 IntPtr 或 SafeHandle 承接，再交給 FileStream 使用；此模式亦是未來 TxF 的基礎。

3. 技術依賴：相關技術之間的依賴關係
   - TxF（Transactional NTFS）依賴 Win32 檔案 API 的操作模式與參數
   - C# 呼叫 Win32 需透過 P/Invoke（DllImport、extern static）
   - HANDLE 管理建議使用 SafeHandle 家族，避免手動 CloseHandle 遺漏
   - FileStream 依賴 SafeFileHandle 的建構式（舊的 IntPtr 建構式已不建議使用）
   - DllImport 的 CharSet/SetLastError 設定影響 API 呼叫正確性與錯誤追蹤

4. 應用場景：適用於哪些實際場景？
   - 在 C# 中直接使用 Win32 檔案 API 以取得框架未包裝的能力（含 TxF）
   - 需要與舊有原生程式庫互通或漸進式遷移到 .NET
   - 系統工具、底層檔案操作、特殊旗標或行為（共享模式、建立/開啟模式）控制
   - 研究或實作 Transactional NTFS 的檔案交易式操作（Vista/2008/7/2008 R2 等）

### 學習路徑建議
1. 入門者路徑：零基礎如何開始？
   - 了解 DllImport 與 extern static 的基本用法
   - 從 MoveFile 這類無指標的簡單 API 開始練習
   - 認識 IntPtr、基本字元集設定（CharSet.Auto）與 SetLastError
   - 在範例程式中驗證結果（用最小可行測試檔案搬移）

2. 進階者路徑：已有基礎如何深化？
   - 練習 CreateFile/CloseHandle 的開啟與讀寫流程，理解各旗標含義
   - 由 IntPtr 過渡到 SafeFileHandle，熟悉資源釋放與 IDisposable
   - 使用 FileStream(handle) 讀取檔案內容，觀察 API 與 .NET IO 的銜接
   - 查閱 MSDN 與 pinvoke.net，將魔法數字 flags 系統化為列舉

3. 實戰路徑：如何應用到實際專案？
   - 封裝 Win32 檔案呼叫為內部服務層（宣告、錯誤處理、資源管理一致化）
   - 對常用 API 建立強型別列舉與常數，減少硬編碼
   - 導入 SafeHandle 全面管理 HANDLE 生命週期，避免資源洩漏
   - 基於上述基礎延伸到 TxF API，實作交易式檔案操作（須在支援的 Windows 版本測試）

### 關鍵要點清單
- DllImport 基礎：以 DllImport 標註並指定 DLL（如 kernel32.dll），讓 C# 能呼叫 Win32 API (優先級: 高)
- extern static 宣告：P/Invoke 的方法需為 extern static，表示方法實作在外部 DLL (優先級: 高)
- MoveFile 範例：從無指標的 MoveFile 入門，快速驗證 P/Invoke 流程 (優先級: 高)
- IntPtr 的角色：用 IntPtr 承接 unmanaged 指標/HANDLE，是兩個世界的橋樑 (優先級: 高)
- CreateFile 與檔案旗標：理解存取、共享、建立模式與屬性旗標對行為的影響 (優先級: 高)
- CloseHandle 的必要性：未使用 SafeHandle 時需手動 CloseHandle，否則會資源洩漏 (優先級: 高)
- SafeHandle/SafeFileHandle：以安全的 RAII/IDisposable 模式管理 HANDLE，取代 IntPtr + CloseHandle (優先級: 高)
- FileStream 與 Handle：使用 FileStream(SafeFileHandle, FileAccess) 來以 .NET 方式操作已開啟的 HANDLE (優先級: 中)
- 反對使用 IntPtr 建構式：FileStream(IntPtr, FileAccess) 已被棄用，應改用 SafeFileHandle (優先級: 中)
- CharSet 與字串封送：透過 CharSet.Auto/Unicode 控制字元集封送，避免路徑包含非 ASCII 時出錯 (優先級: 中)
- SetLastError 的使用：在 DllImport 設定 SetLastError = true 以利從 Marshal.GetLastWin32Error 取得錯誤碼 (優先級: 中)
- HANDLE 與 POINTER 差異：HANDLE 是 OS 管理的資源抽象，不等同一般指標，需正確關閉 (優先級: 中)
- 與 TxF 的關聯：TxF API 與標準 Win32 檔案 API 一一對應，先熟悉後者即可掌握多數 TxF 用法 (優先級: 高)
- 參考資源：pinvoke.net 可查 C# 宣告範本；MSDN 提供 API 詳細說明 (優先級: 中)
- 平台需求：TxF 測試與使用需在 Vista/Windows 7/Server 2008/2008 R2 等支援版本 (優先級: 低)