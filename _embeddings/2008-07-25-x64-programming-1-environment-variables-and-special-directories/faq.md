# x64 programming #1: 環境變數及特殊目錄..

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 64 位元 Windows 上執行 .NET 程式時，`Environment.SpecialFolder.ProgramFiles` 會依建置目標 (x86 與 x64/Any CPU) 回傳哪些路徑？
x86 目標下會回傳 `C:\Program Files (x86)`；  
x64/Any CPU 目標下會回傳 `C:\Program Files`。

## Q: 為什麼在撰寫程式時不應該把 `C:\Program Files\` 之類的路徑寫死？
因為在 64 位元作業系統中，32 位元程式實際使用的安裝路徑是 `C:\Program Files (x86)`，若硬寫成 `C:\Program Files\` 會導致路徑錯誤與資源存取失敗。

## Q: 透過 `Environment.GetEnvironmentVariables()` 觀察，可用哪個環境變數判斷目前行程是 32 位元還是 64 位元？
`PROCESSOR_ARCHITECTURE`。  
‒ 32 位元行程顯示 `x86`  
‒ 64 位元行程顯示 `AMD64`

## Q: 在 64 位元 Windows 中，系統如何處理 32 位元程式對 Registry 與檔案系統的存取？
系統會啟用 WOW64 重新導向機制：  
1. Registry 會被重新導向至對應的 32 位元節點。  
2. 檔案系統會將對系統目錄 (如 `System32`) 的呼叫轉向至 `SysWOW64` 中的 32 位元版本。

## Q: `C:\Windows\System32` 在 64 位元系統裡究竟存放的是什麼檔案？32 位元程式會實際讀取到這些檔案嗎？
`System32` 目錄裡存放的是 64 位元的系統檔案。  
當 32 位元程式想載入該目錄下的 DLL 或 EXE 時，WOW64 會把存取自動轉向到 `C:\Windows\SysWOW64` 中相對應的 32 位元檔案。

## Q: 安裝 64 位元 Windows 後，為什麼系統磁碟 (通常是 C:) 會比 32 位元時「變肥」？
因為許多系統檔案、DLL 及程式都必須同時保留 32 位元與 64 位元兩個版本，導致同樣的元件要在 `System32` 與 `SysWOW64`（或 `Program Files` 與 `Program Files (x86)`）各存放一份。

## Q: 想正式學習 64 位元程式開發應參考哪份官方文件？
請閱讀 MSDN 的「Programming Guide for 64-bit Windows」(網址：https://msdn.microsoft.com/en-us/library/bb427430(VS.85).aspx)。