---
layout: synthesis
title: "[TxF] #2. 先作功課 - 熟悉 P/Invoke 及 Win32 檔案處理..."
synthesis_type: faq
source_post: /2010/03/23/txf-2-homework-first-pinvoke-and-win32-file-handling/
redirect_from:
  - /2010/03/23/txf-2-homework-first-pinvoke-and-win32-file-handling/faq/
postid: 2010-03-23-txf-2-homework-first-pinvoke-and-win32-file-handling
---

# [TxF] #2. 先作功課 - 熟悉 P/Invoke 及 Win32 檔案處理...

## 問題與答案 (FAQ)

### Q&A 類別 A: 概念理解類

A-Q1: 什麼是 P/Invoke？
- A簡: P/Invoke 是 .NET 以 DllImport 呼叫非受控 DLL 函式的機制，用來存取 Win32 等系統 API。
- A詳: P/Invoke（Platform Invocation Services）讓受控環境（C#、VB.NET）能呼叫非受控程式庫（如 kernel32.dll 的 Win32 API）。開發者以 extern 與 DllImport 標註方法，CLR 會執行型別封送（marshaling），將 managed 型別與 unmanaged 參數互轉。本文以 MoveFile、CreateFile 等檔案 API 為例，示範如何在 C# 中直接使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, A-Q6, B-Q1

A-Q2: 什麼是 Win32 API？
- A簡: Win32 API 是 Windows 提供的非受控函式集，透過 DLL 暴露系統功能如檔案、行程、視窗。
- A詳: Win32 API 是 Windows 作業系統層級的函式介面，分佈在 kernel32.dll、user32.dll 等動態連結程式庫中。檔案處理常用 API 包含 MoveFile、CreateFile、CloseHandle。這些函式以 C 介面定義，回傳 HANDLE、BOOL 等 C 型別，需要以 P/Invoke 才能在 .NET 使用。TxF 新 API 亦與這些 Win32 函式一一對應。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q14, B-Q13

A-Q3: 什麼是 managed code 與 unmanaged code 的差異？
- A簡: 受控碼受 CLR 管理、具 GC 與安全性；非受控碼直接由 OS 執行、需自行管理資源。
- A詳: Managed code 由 CLR 管理，具記憶體回收（GC）、例外處理與型別安全；Unmanaged code 直接以機器碼由 OS 執行（如 Win32 API、C/C++ DLL），須手動管理記憶體與資源。兩者介接需考量封送、呼叫約定與資源生命週期，因此 .NET 以 P/Invoke 提供橋接機制，並提供 IntPtr、SafeHandle 等型別協助安全操作。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, A-Q9, A-Q10

A-Q4: 為什麼使用 TxF 需要 P/Invoke？
- A簡: TxF 官方僅提供 Win32 API，未提供 .NET 包裝，因此需以 P/Invoke 呼叫。
- A詳: 文章指出 Transactional NTFS（TxF）僅提供 Win32 API 版本，沒有 managed library。欲在 C# 使用 TxF，就必須用 P/Invoke 自行宣告對應函式簽章。且 TxF API 與標準檔案 API 一一對應，因此先熟悉 MoveFile、CreateFile 等一般 Win32 API，即可很快上手對應的交易式版本。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q12, C-Q10

A-Q5: 什麼是 Transactional NTFS（TxF）？
- A簡: TxF 讓 NTFS 檔案操作具交易性，支援提交與回復，確保原子性與一致性。
- A詳: Transactional NTFS 是 Windows 提供的檔案系統交易機制，讓檔案建立、搬移、寫入等操作可納入同一交易中，成功則提交，失敗能回復，確保原子性與一致性。TxF 的 API 與傳統 Win32 檔案 API 互相對應（如 MoveFileTransacted），因此掌握一般 API 的使用方式與句柄管理，是學習 TxF 的基礎。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q4, B-Q12, C-Q10

A-Q6: 什麼是 DllImport Attribute？
- A簡: DllImport 標示外部 DLL 與項目名稱、字元集、錯誤回報等資訊，用於 P/Invoke 綁定。
- A詳: DllImport 是用於 extern 方法的屬性，用以指定 DLL 名稱、EntryPoint（預設為方法名）、CharSet（字串封送）、SetLastError（啟用 Win32 錯誤碼回報）等。以 [DllImport("kernel32.dll")] 搭配 extern 宣告，即可於 C# 呼叫 MoveFile、CreateFile 等非受控函式。正確設定能避免字串亂碼與錯誤碼遺失。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q1, B-Q2, B-Q4

A-Q7: extern 關鍵字在 C# 中的用途是什麼？
- A簡: extern 用於宣告外部實作的方法，常與 DllImport 搭配呼叫非受控函式。
- A詳: 在 C# 中，extern 表示方法的實作位於組件外部，需由執行期連結至外部函式。P/Invoke 以 extern 方法對應非受控 DLL 的匯出函式，且此方法必為 static，無物件關聯。透過 DllImport 指定 DLL 與封送設定，即可在程式中直接呼叫該方法。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q6, B-Q1, B-Q2

A-Q8: HANDLE 與一般指標（POINTER）有何差異？
- A簡: HANDLE 是 OS 管理的資源代稱，較抽象安全；指標是記憶體位址，操作更直接。
- A詳: 在 Windows，HANDLE 代表由系統管理的資源參照（如檔案、視窗、行程）。它通常在實作上為指標或整數，但視為不透明的代碼，必須用對應 API 使用與釋放（如 CloseHandle）。一般指標則是任意記憶體位址操作，風險較高。於 .NET 中以 IntPtr 或 SafeHandle 代表 HANDLE，提升安全性與可管理性。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, A-Q10, B-Q7

A-Q9: 什麼是 IntPtr？
- A簡: IntPtr 是平台相依的指標大小整數型別，用於承載指標或句柄。
- A詳: System.IntPtr 是 .NET 提供的型別，用以封裝指標或句柄值。其大小隨平台而變（32 位系統為 4 位元組，64 位為 8 位元組）。在 P/Invoke 世界裡常用 IntPtr 代表 unmanaged 指標/HANDLE，充當跨界橋樑。不過在管理 OS 資源上，建議以 SafeHandle 家族型別取代裸 IntPtr，避免資源外洩。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q8, A-Q10, B-Q11

A-Q10: 什麼是 SafeHandle 與 SafeFileHandle？
- A簡: SafeHandle 是安全包裝的句柄基類；SafeFileHandle 專用於檔案句柄並支援安全釋放。
- A詳: SafeHandle 提供可靠終結（CriticalFinalizerObject），並實作 IDisposable，確保在失敗或例外下也能釋放 OS 句柄。SafeFileHandle 是針對檔案句柄的衍生型別。新版 .NET 建議以 FileStream(SafeFileHandle, …) 建構串流，避免使用 IntPtr 舊式建構式，降低資源外洩與錯誤釋放風險。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q9, B-Q7, B-Q8

A-Q11: 為什麼 FileStream(IntPtr) 建構式被標示過時？
- A簡: 因為以裸 IntPtr 管理句柄不安全，建議改用 SafeFileHandle 版本確保釋放。
- A詳: 以 IntPtr 建構 FileStream 會忽略句柄生命週期的安全管理，容易造成句柄外洩或重複釋放。自 .NET 2.0 起建議改用 FileStream(SafeFileHandle, FileAccess)，由 SafeFileHandle 管理 Close/Dispose 與終結時機，確保例外發生時仍能回收，提升可靠性與安全性。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q8, D-Q9

A-Q12: SetLastError 與 CharSet 在 DllImport 中的意義？
- A簡: SetLastError 允許取回 Win32 錯誤；CharSet 決定字串封送為 Unicode 或 ANSI。
- A詳: SetLastError=true 指示 CLR 呼叫後保留 Win32 的最後錯誤，可用 Marshal.GetLastWin32Error 讀取。CharSet 決定 string 如何封送；在現代 Windows 建議使用 CharSet.Unicode（或 Auto）以支援中文與長路徑。兩者正確設定有助於正確診斷與處理跨境字串問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q4, B-Q5, D-Q6

A-Q13: MoveFile 的功能與回傳值為何？
- A簡: MoveFile 將現有檔案移動或重新命名，成功回傳非零（true），失敗回傳零（false）。
- A詳: MoveFile(LPCTSTR existing, LPCTSTR new) 執行檔案搬移或改名。成功回傳 BOOL 非零；失敗回傳零，可配合 SetLastError 與 GetLastError/Marshal.GetLastWin32Error 取得錯誤碼（如存取被拒、目標已存在、路徑錯誤）。P/Invoke 對應為 extern bool MoveFile(string, string) 搭配適當 CharSet。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: B-Q3, C-Q1, D-Q1

A-Q14: CreateFile 的用途與常見參數是什麼？
- A簡: CreateFile 用於開啟/建立檔案或裝置，參數涵蓋存取、分享、建立模式與屬性旗標。
- A詳: CreateFile(name, access, share, sec, disposition, flags, template) 回傳檔案 HANDLE。常見值：access=GENERIC_READ(0x80000000)，share=FILE_SHARE_READ(0x1)，disposition=OPEN_EXISTING(3)。以 P/Invoke 可回傳 IntPtr 或 SafeFileHandle，後者更安全。失敗時可檢查錯誤碼判斷分享衝突或權限不足。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, C-Q2, D-Q2

A-Q15: CloseHandle 的角色是什麼？
- A簡: CloseHandle 負責釋放 OS 句柄資源；在 .NET 建議以 SafeHandle.Dispose 取代。
- A詳: 任何由 CreateFile 等 API 取得的 HANDLE 必須在不再使用時呼叫 CloseHandle 釋放，否則將造成資源外洩。在 .NET 中以 SafeFileHandle（或 SafeHandle）管理句柄，能以 using/Dispose 自動釋放，避免遺漏釋放或多次釋放的錯誤，提升可靠性。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q10, B-Q9, D-Q8

A-Q16: P/Invoke 的核心價值與風險為何？
- A簡: 價值是直通系統能力；風險在封送錯誤與資源管理不當，需用 SafeHandle 與正確宣告。
- A詳: P/Invoke 可快速使用 OS 功能（如 TxF、檔案 API），避免重寫 native wrapper。然而風險包括：型別對應錯誤、CharSet 不當、錯誤碼遺失、句柄外洩、跨平台差異。最佳實務是正確宣告 DllImport、使用 SafeHandle、啟用 SetLastError、以 enum 取代裸常數，並加上錯誤處理。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q1, B-Q5, D-Q8


### Q&A 類別 B: 技術原理類

B-Q1: P/Invoke 在 CLR 中如何運作？
- A簡: CLR 依 DllImport 綁定函式位址，執行封送轉換並呼叫 DLL，回傳時再轉回 managed 型別。
- A詳: 原理說明：編譯 extern 方法時，CLR 依 DllImport 載入指定 DLL，解析輸出項目，建立 thunk。流程：參數封送→呼叫非受控→回傳值與 out 參數封送回 managed。核心組件：DllImport、Marshaler、Loader。正確宣告型別與 CharSet 是成功的關鍵。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q1, A-Q6, B-Q2

B-Q2: DllImport 如何解析目標函式與呼叫約定？
- A簡: 依名稱或 EntryPoint 解析匯出，預設 stdcall，並依 CharSet 影響字串與名稱修飾。
- A詳: 原理：DllImport 可指定 EntryPoint；省略時用方法名。流程：載入 DLL→查找匯出→建立委派樣板。核心：CallingConvention 預設 Winapi（多為 stdcall）、CharSet.ANSI/Unicode/Auto 影響字串封送與名稱修飾（A/W）。設定不當會造成 EntryPointNotFound 或字串錯亂。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q6, D-Q4, B-Q4

B-Q3: MoveFile 的 P/Invoke 簽章如何映射？
- A簡: 將 BOOL 映為 bool，LPCTSTR 映為 string；以 DllImport 指向 kernel32.dll 即可。
- A詳: 原理：C 宣告 BOOL WINAPI MoveFile(LPCTSTR, LPCTSTR)。映射：bool 對 BOOL、string 對 LPCTSTR。流程：定義 [DllImport("kernel32.dll", CharSet=Auto)] extern static bool MoveFile(string, string)。核心：CharSet 決定呼叫 MoveFileW 或 MoveFileA；回傳 false 時結合 SetLastError 診斷。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, C-Q1, D-Q1

B-Q4: 字串封送與 CharSet.Auto 有何影響？
- A簡: CharSet 決定使用 ANSI 或 Unicode 版本；Auto 在 NT 系列選 Unicode，避免亂碼。
- A詳: 原理：Win32 多以 A（ANSI）/W（Wide）雙版本匯出。流程：CharSet.Unicode→W 函式，ANSI→A 函式，Auto→依平台選擇（現代 Windows 為 Unicode）。核心：使用 Unicode 可正確處理中文與長路徑；若指定錯誤可能導致找不到檔案或亂碼。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q6, C-Q8

B-Q5: SetLastError 與 Marshal.GetLastWin32Error 的關係？
- A簡: SetLastError=true 讓 CLR 保存錯誤碼，可用 Marshal.GetLastWin32Error 讀取診斷。
- A詳: 原理：Win32 每執行緒維護最後錯誤碼。流程：DllImport(SetLastError=true)→呼叫 API→回傳後立即呼叫 Marshal.GetLastWin32Error 取得錯誤。核心：避免在讀取前進行其他 P/Invoke 以免覆蓋；錯誤碼輔助判斷分享衝突、權限不足等。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q12, D-Q1, D-Q2

B-Q6: CreateFile 的參數與旗標如何設計？
- A簡: 依需求設定 access、share、creationDisposition 與 flags；常用 GENERIC_READ、OPEN_EXISTING。
- A詳: 原理：CreateFile 控制開啟/建立行為。流程：決定存取（GENERIC_READ/WRITE）、共享（FILE_SHARE_READ/WRITE）、建立（CREATE_NEW/OPEN_EXISTING/CREATE_ALWAYS 等）、屬性（FILE_ATTRIBUTE_*）。核心組件：正確旗標與安全回傳型別（SafeFileHandle）避免 INVALID_HANDLE_VALUE 與分享衝突。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, C-Q4, D-Q7

B-Q7: HANDLE 生命週期與 SafeHandle 的可靠終結機制？
- A簡: SafeHandle 以可靠終結確保句柄釋放，避免例外時資源外洩，優於手動 CloseHandle。
- A詳: 原理：SafeHandle 繼承自 CriticalFinalizerObject，終結器在 CLR 崩潰時仍高機率執行。流程：建構→使用→Dispose/Close→終結器後備釋放。核心：避免雙重釋放、競態；與 FileStream/using 搭配減少泄漏。是 P/Invoke 管理 OS 資源的首選。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, A-Q15, D-Q8

B-Q8: FileStream 如何接受既有的檔案句柄？
- A簡: 以 FileStream(SafeFileHandle, FileAccess) 包裝現有句柄，受益於 SafeHandle 管理。
- A詳: 原理：FileStream 提供以 SafeFileHandle 建構的多載，讓 native 取得的句柄能被 .NET I/O 使用。流程：P/Invoke 取句柄→建構 FileStream→讀寫→Dispose 順便關閉句柄。核心組件：SafeFileHandle；避免已過時的 IntPtr 建構式，確保釋放正確。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q11, C-Q3, D-Q9

B-Q9: CloseHandle 與 SafeHandle.Dispose 的差異？
- A簡: CloseHandle 是函式呼叫；SafeHandle.Dispose 管理呼叫時機並防止重複釋放。
- A詳: 原理：CloseHandle 直接關閉句柄，需自行確保只呼叫一次且未被他處使用。SafeHandle 封裝狀態與參考計數，Dispose/Close 僅釋放一次，終結器為後備。流程：managed 使用→Dispose→避免重入。核心：以 SafeHandle 防呆，減少手誤造成的資源問題。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q15, B-Q7, D-Q8

B-Q10: BOOL 與 C# bool 的封送原理是什麼？
- A簡: Win32 BOOL 是 4 位整數；C# bool 封送為 UnmanagedType.Bool，可正確互通真偽。
- A詳: 原理：Win32 的 BOOL 為 32 位整數（0/非0）。P/Invoke 預設將 C# bool 封送為 UnmanagedType.Bool（4 位），與 Win32 一致。流程：回傳與參數皆自動封送。核心：避免用 1 位的 VARIANT_BOOL 概念；若需精確控制可以 MarshalAs 指定。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q3, D-Q1, A-Q16

B-Q11: IntPtr 的位元寬度與跨平台考量？
- A簡: IntPtr 隨平台變 32/64 位，適合承載指標；避免用 int/long 直接承接句柄值。
- A詳: 原理：IntPtr.Size 反映平台位元寬度。流程：P/Invoke 參數/回傳以 IntPtr 接收指標或句柄，CLR 會依平台正確寬度封送。核心：避免將句柄映為 int，會在 x64 截斷；改用 IntPtr 或 SafeHandle。AnyCPU 下注意原生 DLL 僅支援單一位元時的相容性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q9, C-Q9, D-Q5

B-Q12: TxF API 與非交易式 API 的對應機制？
- A簡: TxF 多以「Transacted」變體對應既有 API，使用交易內容參數擴充原流程。
- A詳: 原理：TxF 以與傳統 API 等價的介面提供交易能力（如 CreateFileTransacted、MoveFileTransacted），新增交易內容/物件參數。流程：開始交易→呼叫對應 Transacted API→提交或回復。核心：先掌握非交易式 API 簽章與句柄管理，再套用交易擴充即可。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q4, A-Q5, C-Q10

B-Q13: kernel32.dll 在檔案 API 中扮演什麼角色？
- A簡: kernel32.dll 提供核心系統服務與檔案 I/O 函式，如 MoveFile、CreateFile、CloseHandle。
- A詳: 原理：kernel32.dll 是 Windows 核心子系統一部份，封裝大量系統呼叫。流程：應用程式透過 P/Invoke 連結 kernel32 的匯出函式以進行檔案與處理程序控制。核心組件：Loader、Import Table。正確指定 DLL 名稱與函式對應，是 P/Invoke 成功的基本前提。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q2, B-Q1, C-Q1

B-Q14: 檔案分享模式（ShareMode）機制如何影響 I/O？
- A簡: ShareMode 決定他人可否同時讀/寫/刪除；設定不當會引發分享衝突錯誤。
- A詳: 原理：CreateFile 的 dwShareMode 定義其他開啟者可共享的權限（READ/WRITE/DELETE）。流程：A 以 READ 開啟且不允許寫共享，B 嘗試寫入會失敗。核心：依需求設置共享，讀檔常用 FILE_SHARE_READ；寫入時視情況允許 READ，共享設定影響並行度與錯誤率。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, D-Q7, C-Q4

B-Q15: P/Invoke 的安全性與可靠性如何提升？
- A簡: 用 SafeHandle、正確 CharSet/SetLastError、明確 enum 與防呆檢查，降低風險。
- A詳: 原理：以型別與生命週期安全取代裸值。流程：宣告時用 SafeHandle、CharSet.Unicode、SetLastError；執行時檢查回傳與錯誤碼；以 enum 封裝旗標、using 確保釋放。核心：最小權限、清楚邊界、記錄錯誤與單元測試，提升互操作穩定性。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, D-Q8, C-Q6

B-Q16: 為何熟悉 Win32 檔案 API 等於掌握 80% 的 TxF？
- A簡: TxF 與標準 API 一一對應，只需在既有流程上加交易語境與控制即可。
- A詳: 原理：TxF 的 Transacted 函式在語意與參數結構上延續非交易式版本，只多交易控制。流程：按一般檔案 API 使用→以交易開始/提交/回復包住。核心：掌握 MoveFile、CreateFile、CloseHandle、句柄管理與錯誤處理，即可快速遷移到 TxF 工作流。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: A-Q4, B-Q12, C-Q10


### Q&A 類別 C: 實作應用類（10題）

C-Q1: 如何以 P/Invoke 呼叫 MoveFile 移動檔案？
- A簡: 定義 DllImport 對應簽章，呼叫 MoveFile(old, new)，判斷回傳與錯誤碼。
- A詳: 實作步驟：1) 宣告 [DllImport("kernel32.dll", CharSet=CharSet.Auto, SetLastError=true)] static extern bool MoveFile(string src,string dst); 2) 呼叫並檢查回傳。程式碼: 
  ```
  if(!MoveFile(a,b)) Console.WriteLine(Marshal.GetLastWin32Error());
  ```
  注意事項：使用 Unicode/Auto 避免路徑亂碼；失敗時立即讀取錯誤碼。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q13, B-Q3, D-Q1

C-Q2: 如何使用 CreateFile + FileStream 讀取檔案內容？
- A簡: 先以 CreateFile 開啟取得句柄，再用 FileStream 包裝讀取，最後正確釋放。
- A詳: 步驟：1) P/Invoke CreateFile 以 GENERIC_READ、FILE_SHARE_READ、OPEN_EXISTING。2) 用 FileStream(handle, FileAccess.Read) 讀取。3) 關閉串流與句柄。程式碼:
  ```
  var h=CreateFile(path,0x80000000,1,IntPtr.Zero,3,0,IntPtr.Zero);
  using(var fs=new FileStream(h,FileAccess.Read)){...}
  ```
  注意：IntPtr 版本舊，建議改用 SafeFileHandle。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q6, C-Q3

C-Q3: 如何改用 SafeFileHandle 與 FileStream？
- A簡: 讓 CreateFile 回傳 SafeFileHandle，再以 FileStream(SafeFileHandle, …) 讀寫。
- A詳: 步驟：1) 將 CreateFile 回傳型別改為 SafeFileHandle。2) 以 FileStream(handle, FileAccess.Read) 建構。3) using 確保釋放。程式碼:
  ```
  [DllImport("kernel32",SetLastError=true,CharSet=CharSet.Auto)]
  static extern SafeFileHandle CreateFile(...);
  using(var h=CreateFile(...))
  using(var fs=new FileStream(h,FileAccess.Read)){...}
  ```
  注意：避免手動 CloseHandle；檢查 h.IsInvalid。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q10, B-Q8, D-Q9

C-Q4: 如何用 enum 結構化 CreateFile 旗標？
- A簡: 以 [Flags] enum 定義 GENERIC_READ、FILE_SHARE_READ、OPEN_EXISTING 等提高可讀性。
- A詳: 步驟：1) 定義 enum FileAccessMask、FileShareMode、CreationDisposition。2) 修改簽章參數型別。程式碼:
  ```
  [Flags] enum FileAccessMask:uint{ GENERIC_READ=0x80000000, GENERIC_WRITE=0x40000000 }
  [Flags] enum FileShareMode:uint{ READ=1, WRITE=2 }
  enum CreationDisposition:uint{ CREATE_NEW=1, OPEN_EXISTING=3 }
  ```
  注意：仍以 uint 傳遞，避免值錯誤。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q6, B-Q14, D-Q7

C-Q5: 如何取得 Win32 錯誤碼進行診斷？
- A簡: DllImport 設 SetLastError=true，呼叫失敗後立即取 Marshal.GetLastWin32Error。
- A詳: 步驟：1) 在 P/Invoke 標記 SetLastError=true。2) 呼叫 API 後檢查回傳。3) 若 false 或無效句柄，Console.WriteLine(Marshal.GetLastWin32Error())。程式碼:
  ```
  if(!MoveFile(a,b)){ var err=Marshal.GetLastWin32Error(); }
  ```
  注意：勿在讀錯前做其他 P/Invoke，以免錯誤碼被覆蓋。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, D-Q1, D-Q2

C-Q6: 如何安全釋放 HANDLE（using/Dispose 範例）？
- A簡: 以 SafeFileHandle 並配合 using，自動釋放；避免手動多次 CloseHandle。
- A詳: 步驟：1) 讓 API 回傳 SafeFileHandle。2) using 包起來。3) 在 FileStream 上也用 using。程式碼:
  ```
  using(var h=CreateFile(...))
  using(var fs=new FileStream(h,FileAccess.Read)){...}
  ```
  注意：判斷 h.IsInvalid；不要再手動呼叫 CloseHandle，以免雙重釋放。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q9, D-Q8

C-Q7: 如何封裝 Win32 檔案 API 成 .NET 類別？
- A簡: 建立 FileNative 類別收斂 P/Invoke，提供易用方法並處理錯誤與釋放。
- A詳: 步驟：1) 建立靜態類別宣告 MoveFile/CreateFile。2) 提供 TryMove、OpenRead 包裝方法。3) 於包裝中轉換 enum、檢查錯誤碼。程式碼:
  ```
  public static bool TryMove(string a,string b,out int err){
    bool ok=MoveFile(a,b); err=ok?0:Marshal.GetLastWin32Error(); return ok;
  }
  ```
  注意：公開 SafeFileHandle 以利 using；撰寫單元測試。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q16, B-Q15, D-Q1

C-Q8: 如何設定 CharSet 確保 Unicode 路徑正確？
- A簡: 在 DllImport 指定 CharSet.Unicode 或 Auto，字串參數改以寬字元封送。
- A詳: 步驟：1) 修改宣告為 [DllImport("kernel32", CharSet=CharSet.Unicode)]。2) 檢查所有 string 參數。3) 測試含中文/長路徑。程式碼:
  ```
  [DllImport("kernel32",CharSet=CharSet.Unicode)]
  static extern bool MoveFile(string a,string b);
  ```
  注意：避免預設 ANSI 造成亂碼或找不到檔案。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, D-Q6, C-Q1

C-Q9: 如何在 32/64 位環境正確處理 IntPtr？
- A簡: 用 IntPtr/SafeHandle 承接句柄，避免用 int；設定合適平台目標避免位元不符。
- A詳: 步驟：1) 簽章用 IntPtr 或 SafeFileHandle。2) 專案 Platform target 選 x64/x86/AnyCPU 依相依 DLL。3) 避免將句柄 cast 為 int。程式碼:
  ```
  IntPtr h = CreateFile(...); // 或 SafeFileHandle
  ```
  注意：BadImageFormat 多為位元不符；以 SafeHandle 更穩妥。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, D-Q5, C-Q3

C-Q10: 如何為 TxF API 預先準備 P/Invoke？
- A簡: 比照非交易式 API 定義 Transacted 版本簽章，並檢查 OS 版本支援。
- A詳: 步驟：1) 依對應關係宣告如 MoveFileTransacted/CreateFileTransacted。2) 加入 SetLastError 與 Unicode。3) 檢查 OS（Vista/2008/7 以上）。程式碼（示意）:
  ```
  [DllImport("kernel32",CharSet=CharSet.Unicode,SetLastError=true)]
  static extern bool MoveFileTransacted(string a,string b,IntPtr p,IntPtr q,uint flags,IntPtr tx);
  ```
  注意：先熟悉非交易式流程再套用交易參數。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: A-Q4, B-Q12, A-Q5


### Q&A 類別 D: 問題解決類（10題）

D-Q1: MoveFile 回傳 false，如何診斷？
- A簡: 啟用 SetLastError，立即呼叫 Marshal.GetLastWin32Error 判斷錯誤並對症處理。
- A詳: 症狀：MoveFile 回傳 false。可能原因：目標已存在、存取被拒、路徑錯誤、字串封送錯。解決：DllImport 設 SetLastError=true；失敗後立刻取錯誤碼；依碼調整權限/路徑。預防：使用 CharSet.Unicode；先檢查目標是否存在；記錄錯誤以利追蹤。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q5, C-Q1, A-Q13

D-Q2: CreateFile 取得無效句柄怎麼辦？
- A簡: 檢查 IsInvalid 或 IntPtr 是否為 -1，讀取錯誤碼，調整旗標與分享模式。
- A詳: 症狀：CreateFile 回 -1/IsInvalid。原因：路徑錯、權限不足、分享衝突、旗標不當。解決：確認路徑與存在性；以 GENERIC_READ + FILE_SHARE_READ 開啟；使用 OPEN_EXISTING；讀取錯誤碼查明；改用 SafeFileHandle。預防：以 enum 管理旗標；例外/錯誤碼紀錄。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: A-Q14, B-Q6, C-Q4

D-Q3: DllNotFoundException（找不到 kernel32.dll）？
- A簡: 確認在 Windows 執行且 DLL 名稱正確；非 Windows 無法使用該 API。
- A詳: 症狀：執行時拋 DllNotFoundException。原因：在非 Windows 平台或名稱拼寫錯誤。解決：確保程式在 Windows 上執行；DLL 名稱為 "kernel32.dll"；條件化程式碼避免在其他平台呼叫。預防：以 RuntimeInformation 判斷 OS；將互操作集中管理並作平台檢查。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q13, B-Q1, C-Q7

D-Q4: EntryPointNotFoundException 要怎麼排查？
- A簡: 檢查函式名/EntryPoint、CharSet 對應（A/W 版）、呼叫約定是否正確。
- A詳: 症狀：找不到匯出項目。原因：方法名不符、未指定 EntryPoint、CharSet 導致選錯 A/W 版本、CallingConvention 不符。解決：改用正確方法名或 EntryPoint；設定 CharSet.Unicode；保留預設 CallingConvention。預防：參考官方文件或 pinvoke.net 簽章。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q2, B-Q4, C-Q1

D-Q5: BadImageFormatException（位元不符）如何處理？
- A簡: 修正平台目標（x86/x64/AnyCPU）與原生相依一致，避免載入失敗。
- A詳: 症狀：啟動或呼叫時拋 BadImageFormat。原因：程式為 x64 但依賴僅有 x86 原生 DLL，或反之。解決：在專案設定 Platform target 與原生庫一致，或改 AnyCPU 但確保依賴齊全。預防：建立 CI 檢核平台相容；以 IntPtr/SafeHandle 避免尺寸截斷。
- 難度: 中級
- 學習階段: 進階
- 關聯概念: B-Q11, C-Q9, A-Q9

D-Q6: 中文或長路徑發生亂碼或找不到檔案？
- A簡: 設 CharSet.Unicode 或 Auto，確保字串以寬字元封送，避免 ANSI 限制。
- A詳: 症狀：含中文/長路徑操作失敗。原因：使用 ANSI 版本函式。解決：DllImport 指定 CharSet.Unicode；確認 API 有對應 W 版；測試混合語系檔名。預防：統一使用 Unicode 封送；避免預設 ANSI 的宣告。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: B-Q4, C-Q8, A-Q12

D-Q7: 檔案分享衝突（Access denied）怎麼處理？
- A簡: 調整 dwShareMode 與存取權，或延後重試；確保他程式允許相容共享。
- A詳: 症狀：CreateFile/MoveFile 失敗，錯誤碼顯示拒絕存取/分享衝突。原因：他進程獨占開啟或共享不相容。解決：讀取時使用 FILE_SHARE_READ；寫入需協調共享；加入重試與退避。預防：規劃 I/O 策略、減少鎖定時間、事前檢查是否被占用。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q14, C-Q4, A-Q14

D-Q8: 句柄洩漏造成資源耗盡如何避免？
- A簡: 改用 SafeHandle 與 using，自動釋放資源；避免手動 Close 遺漏與重複釋放。
- A詳: 症狀：長時間執行後失敗或資源耗盡。原因：未關閉句柄或例外中斷未釋放。解決：改以 SafeFileHandle 與 using；檢測程式碼路徑釋放點。預防：移除裸 IntPtr 管理、集中封裝互操作、加壓力測試檢查句柄數。
- 難度: 中級
- 學習階段: 核心
- 關聯概念: B-Q7, B-Q9, C-Q6

D-Q9: FileStream(IntPtr) 過時警告如何處理？
- A簡: 改用 FileStream(SafeFileHandle, …) 建構式，並以 SafeFileHandle 接受 CreateFile。
- A詳: 症狀：編譯出現 obsolete 警告。原因：以 IntPtr 建構 FileStream 已不建議。解決：修改 P/Invoke 回傳型別為 SafeFileHandle；使用新的建構式。預防：統一以 SafeHandle 管理所有 OS 句柄；在程式碼檢查阻擋舊建構式使用。
- 難度: 初級
- 學習階段: 基礎
- 關聯概念: A-Q11, B-Q8, C-Q3

D-Q10: 權限或 UAC 導致檔案操作失敗怎麼辦？
- A簡: 在允許位置操作、以必要權限執行或提升權限；並檢查錯誤碼確認原因。
- A詳: 症狀：目錄受保護（如 C:\ 根），操作失敗。原因：UAC/ACL 限制。解決：改用使用者資料夾路徑；以提升權限執行；設定適當 ACL。預防：遵循最佳路徑慣例（AppData、ProgramData），在安裝/部署階段處理權限設定。
- 難度: 初級
- 學習階段: 核心
- 關聯概念: D-Q1, A-Q16, C-Q7


### 學習路徑索引

- 初學者：建議先學習哪 15 題
    - A-Q1: 什麼是 P/Invoke？
    - A-Q2: 什麼是 Win32 API？
    - A-Q3: 什麼是 managed code 與 unmanaged code 的差異？
    - A-Q6: 什麼是 DllImport Attribute？
    - A-Q7: extern 關鍵字在 C# 中的用途是什麼？
    - A-Q9: 什麼是 IntPtr？
    - A-Q10: 什麼是 SafeHandle 與 SafeFileHandle？
    - A-Q11: 為什麼 FileStream(IntPtr) 建構式被標示過時？
    - A-Q12: SetLastError 與 CharSet 在 DllImport 中的意義？
    - A-Q13: MoveFile 的功能與回傳值為何？
    - A-Q14: CreateFile 的用途與常見參數是什麼？
    - C-Q1: 如何以 P/Invoke 呼叫 MoveFile 移動檔案？
    - C-Q3: 如何改用 SafeFileHandle 與 FileStream？
    - D-Q1: MoveFile 回傳 false，如何診斷？
    - D-Q9: FileStream(IntPtr) 過時警告如何處理？

- 中級者：建議學習哪 20 題
    - B-Q1: P/Invoke 在 CLR 中如何運作？
    - B-Q2: DllImport 如何解析目標函式與呼叫約定？
    - B-Q3: MoveFile 的 P/Invoke 簽章如何映射？
    - B-Q4: 字串封送與 CharSet.Auto 有何影響？
    - B-Q5: SetLastError 與 Marshal.GetLastWin32Error 的關係？
    - B-Q6: CreateFile 的參數與旗標如何設計？
    - B-Q7: HANDLE 生命週期與 SafeHandle 的可靠終結機制？
    - B-Q8: FileStream 如何接受既有的檔案句柄？
    - B-Q9: CloseHandle 與 SafeHandle.Dispose 的差異？
    - B-Q14: 檔案分享模式（ShareMode）機制如何影響 I/O？
    - C-Q2: 如何使用 CreateFile + FileStream 讀取檔案內容？
    - C-Q4: 如何用 enum 結構化 CreateFile 旗標？
    - C-Q5: 如何取得 Win32 錯誤碼進行診斷？
    - C-Q6: 如何安全釋放 HANDLE（using/Dispose 範例）？
    - C-Q8: 如何設定 CharSet 確保 Unicode 路徑正確？
    - D-Q2: CreateFile 取得無效句柄怎麼辦？
    - D-Q4: EntryPointNotFoundException 要怎麼排查？
    - D-Q6: 中文或長路徑發生亂碼或找不到檔案？
    - D-Q7: 檔案分享衝突（Access denied）怎麼處理？
    - D-Q8: 句柄洩漏造成資源耗盡如何避免？

- 高級者：建議關注哪 15 題
    - A-Q4: 為什麼使用 TxF 需要 P/Invoke？
    - A-Q5: 什麼是 Transactional NTFS（TxF）？
    - A-Q16: P/Invoke 的核心價值與風險為何？
    - B-Q10: BOOL 與 C# bool 的封送原理是什麼？
    - B-Q11: IntPtr 的位元寬度與跨平台考量？
    - B-Q12: TxF API 與非交易式 API 的對應機制？
    - B-Q15: P/Invoke 的安全性與可靠性如何提升？
    - B-Q16: 為何熟悉 Win32 檔案 API 等於掌握 80% 的 TxF？
    - C-Q7: 如何封裝 Win32 檔案 API 成 .NET 類別？
    - C-Q9: 如何在 32/64 位環境正確處理 IntPtr？
    - C-Q10: 如何為 TxF API 預先準備 P/Invoke？
    - D-Q3: DllNotFoundException（找不到 kernel32.dll）？
    - D-Q5: BadImageFormatException（位元不符）如何處理？
    - D-Q10: 權限或 UAC 導致檔案操作失敗怎麼辦？
    - B-Q13: kernel32.dll 在檔案 API 中扮演什麼角色？