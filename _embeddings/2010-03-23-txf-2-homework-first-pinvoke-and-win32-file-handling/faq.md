# [TxF] #2. 先作功課 - 熟悉 P/Invoke 及 Win32 檔案處理

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 為什麼在 .NET (C#) 使用 Transactional NTFS 時一定得靠 P/Invoke？
TxF 目前只提供非受控的 Win32 API，並沒有官方的 managed library。若想在 C# 裡存取這些 API，就必須透過 Platform Invocation (P/Invoke) 來呼叫 unmanaged code。

## Q: 只要熟悉標準 Win32 檔案處理 API，大約能掌握多少 TxF 的用法？
作者指出，若弄懂了 Win32 檔案 API 的操作方式，大概就已經學會了 8 成的 TxF。

## Q: 要如何在 C# 中宣告並呼叫 Win32 的 MoveFile 函式？
```csharp
[DllImport("kernel32.dll")]
static extern bool MoveFile(string lpExistingFileName, string lpNewFileName);

// 使用範例
bool ok = MoveFile(@"C:\file1.txt", @"C:\file2.txt");
```
`DllImport` 指出函式位於 kernel32.dll，`extern` 則宣告這是外部函式。回傳值為 `bool`，對應 Win32 的 `BOOL`。

## Q: 在 P/Invoke 宣告裡的 `extern` 關鍵字與 `[DllImport]` 屬性各自的用途是什麼？
• `extern`：告訴編譯器這個函式的實作來自程式之外（外部 DLL）。  
• `[DllImport("…")]`：指定該函式實際位於哪一個 DLL，並提供 CLR 載入與繫結所需的資訊。

## Q: 如何把 Win32 的 `CreateFile` 所得到的檔案 Handle 與 .NET 的 `FileStream` 搭配？
1. 先以 P/Invoke 呼叫 `CreateFile` 取得檔案 Handle (可用 `IntPtr` 或 `SafeFileHandle` 表示)。  
2. 將這個 Handle 傳入 `new FileStream(handle, FileAccess.Read)` 建構式。  
3. 之後即可用 `StreamReader`、`BinaryReader` 等 .NET 類別對檔案資料進行讀寫。

## Q: 為什麼 .NET 2.0 之後建議改用 `SafeFileHandle` 而非 `IntPtr` 來保存 Handle？
`SafeFileHandle` 繼承自 `SafeHandle`，實作了 `IDisposable`，能在適當時機自動釋放底層 Handle。相較之下，使用 `IntPtr` 需要手動呼叫 `CloseHandle`，容易遺漏而導致資源外洩，因此新版 .NET 將只帶 `IntPtr` 的 `FileStream` 建構式標示為 obsolete。

## Q: 想快速查到各種 Win32 API 的 P/Invoke 宣告，哪裡有現成資源？
可參考網站 PINVOKE.NET  
http://www.pinvoke.net/index.aspx  
該站彙整了大量 Win32 API 對應的 C# 宣告，以及 Visual Studio 外掛與查詢工具，可大幅減少手動轉型別與查資料的時間。