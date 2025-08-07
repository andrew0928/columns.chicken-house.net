# [TxF] #2. 先作功課 ─ 熟悉 P/Invoke 及 Win32 檔案處理

# 問題／解決方案 (Problem/Solution)

## Problem: .NET 想使用 Transactional NTFS (TxF) 時沒有 Managed Wrapper

**Problem**:  
在 C# 專案中欲使用 Windows 的「Transactional NTFS (TxF)」功能，以確保檔案操作具有 ACID 特性；然而官方僅釋出 Win32 API，並未提供任何 .NET/Managed Library。對純 .NET 開發者而言，等於無法直接引用現成類別來完成「交易式檔案操作」。

**Root Cause**:  
TxF API 只存在於 unmanaged 的 `kernel32.dll`，.NET Framework BCL 並未提供對應封裝。若不經過橋接，就無法在 managed 環境內呼叫這些函式。

**Solution**:  
利用 Platform Invocation (P/Invoke) 技術，手動宣告 Win32 API 的 C# 對應 Signature，並透過 `extern` 與 `DllImport` 修飾即可呼叫 unmanaged 函式。以下以最簡單的檔案搬移 API `MoveFile` 為例：

```csharp
// C# signature
[DllImport("kernel32.dll")]
static extern bool MoveFile(string lpExistingFileName, string lpNewFileName);

// 使用範例
string src = @"C:\file1.txt";
string dst = @"C:\file2.txt";

Console.Write($"move file: {src} -> {dst} ... ");
Console.WriteLine(MoveFile(src, dst) ? "OK!" : "FAIL!");
```
關鍵思考點  
1. `DllImport` 指定目標 DLL (`kernel32.dll`)。  
2. 透過 `string` → `LPCTSTR` 的自動封送即可簡化參數轉換。  
3. 回傳值 `BOOL` 直接對應 C# `bool`。  
4. 有了 P/Invoke 橋接能力，往後所有 TxF API 皆可比照辦理。

**Cases 1**:  
執行程式前 `DIR C:\*.TXT` 僅有 `file1.txt`；執行後再次列目錄，`file1.txt` 已消失、`file2.txt` 出現，證實已成功透過 Win32 `MoveFile` 完成檔案搬移。

---

## Problem: 透過 Win32 API 開檔 (CreateFile) 後的 HANDLE 無法安全管理

**Problem**:  
在示範 TxF 前，需要先掌握「以 Win32 `CreateFile` 開檔、再用 .NET `FileStream` 讀取內容」的流程。但 `CreateFile` 回傳的是未受控的 `HANDLE`，若開發者直接以 `IntPtr` 接住並手動呼叫 `CloseHandle`，很容易出現資源洩漏、錯誤釋放等風險；此外，`new FileStream(IntPtr, FileAccess)` 早已標示為 `Obsolete`。

**Root Cause**:  
1. `HANDLE` 屬於 OS 資源，需明確釋放。  
2. 早期以 `IntPtr` + `CloseHandle` 方式缺乏 RAII/Dispose 機制。  
3. .NET 2.0 起，建議透過 `SafeHandle` 家族封裝，以確保例外或中途結束時仍能安全釋放資源。

**Solution**:  
改用 `SafeFileHandle` 取代 `IntPtr`，並直接交由 `FileStream(SafeFileHandle, FileAccess)` 建構式使用；`SafeHandle` 已內建 `IDisposable`，CLR 也能於終結期 (finalize) 自動釋放 Handle。

```csharp
using Microsoft.Win32.SafeHandles;
using System.IO;
using System.Runtime.InteropServices;

class PInvokeSafeHandleSample
{
    [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Auto)]
    static extern SafeFileHandle CreateFile(
        string lpFileName,
        uint dwDesiredAccess,
        uint dwShareMode,
        IntPtr lpSecurityAttributes,
        uint dwCreationDisposition,
        uint dwFlagsAndAttributes,
        IntPtr hTemplateFile);

    static void Main()
    {
        // 0x80000000 = GENERIC_READ, 0x1 = FILE_SHARE_READ, 3 = OPEN_EXISTING
        SafeFileHandle handle = CreateFile(
            @"C:\file1.txt", 0x80000000, 0x00000001,
            IntPtr.Zero, 3, 0, IntPtr.Zero);

        using (var fs = new FileStream(handle, FileAccess.Read))
        using (var reader = new StreamReader(fs))
        {
            Console.WriteLine(reader.ReadToEnd());
        }   // using 作用域結束，自動 Dispose -> SafeHandle.Close()

        // 不需手動呼叫 CloseHandle
    }
}
```
關鍵思考點  
1. `SafeFileHandle` 本質繼承 `SafeHandle`，CLR 於終結或 `Dispose()` 時會自動呼叫 `CloseHandle`。  
2. .NET 與 OS 之間的 Handle 生命週期統一由 `SafeHandle` 負責，減少人為錯誤。  
3. 透過 `using` 區塊實現 deterministic dispose，符合 .NET 資源管理慣例。

**Cases 1**:  
• 編譯時不再出現 *obsolete constructor* 警告。  
• 執行程式即可安全讀出 `file1.txt` 內容；以 ProcMon 或 Handle 工具觀察，檔案於程式結束即已正確關閉，無遺留 Handle。

---

## Problem: Win32 API Flags 與 .NET 類型對應繁瑣、易讀性差

**Problem**:  
`CreateFile`、`MoveFileEx` 等函式均須傳入多組旗標 (Access、Share、Disposition、Attributes)。若直接在 C# 內以裸數值 (uint) 撰寫，不僅可讀性低，也增加維護成本及錯誤機率。

**Root Cause**:  
1. Win32 Header 內的 `#define` 無法被 C# 編譯器直接引用。  
2. 未對應為 Enum 便需讓開發者自行查表、硬填常數。  
3. 對旗標的 bitwise 組合缺乏型別安全檢查。

**Solution**:  
(1) 先以 Enum 方式在 C# 端自行定義常用旗標；(2) 或直接利用社群整理好的 pinvoke.net 及 VS 插件，「一鍵」產生對應的 Enum 與 Signature。

```csharp
[Flags]
public enum DesiredAccess : uint
{
    GENERIC_READ    = 0x80000000,
    GENERIC_WRITE   = 0x40000000
}

[Flags]
public enum ShareMode : uint
{
    FILE_SHARE_READ = 0x00000001,
    FILE_SHARE_WRITE= 0x00000002
}

/* ... 其他列舉略 ... */

// Signature 只要替換對應 enum 即可
[DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
static extern SafeFileHandle CreateFile(
    string lpFileName,
    DesiredAccess dwDesiredAccess,
    ShareMode dwShareMode,
    IntPtr lpSecurityAttributes,
    CreationDisposition dwCreationDisposition,
    FlagsAndAttributes dwFlagsAndAttributes,
    IntPtr hTemplateFile);
```
關鍵思考點  
Enum 化後可  
a) 透過 IntelliSense 提示降低查表成本；  
b) 以 `Enum.HasFlag()` 或 `|` 運算符清楚組合旗標；  
c) 編譯器層即能進行型別安全檢驗。

**Cases 1**:  
• 專案後續維護者無須再比對 MSDN 常數，只要看 Enum 名稱即可理解意義。  
• 重構/修改時因有型別限制，可有效避免錯誤填入不相容旗標。  

---