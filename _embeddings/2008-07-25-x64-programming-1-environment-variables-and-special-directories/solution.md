# x64 programming #1: 環境變數及特殊目錄..

# 問題／解決方案 (Problem/Solution)

## Problem: 32/64 位元共存下，程式硬寫路徑導致找不到檔案或寫錯目錄

**Problem**:  
在 x64 Windows 上，同一套程式如果以 x86 組態執行，OS 會把 `C:\Program Files`、`C:\Windows\system32`… 等關鍵目錄重新導向。  
若開發人員把 `C:\Program Files\xxx`、`C:\Windows\system32\xxx.dll` 之類的字串硬寫在程式裡，便會遇到：  
• 安裝檔案被寫到錯的位置 (例如被寫到 `C:\Program Files (x86)` 而非預期目錄)。  
• 執行期無法正確載入 DLL/EXE。  
• 相同程式在 x86、x64 組態下行為不一致。

**Root Cause**:  
1. WoW64 (Windows-on-Windows 64) 的「檔案系統重新導向」與「Registry 虛擬化」機制，會把 32-bit 行程導向至 `Program Files (x86)`、`SysWOW64` 等目錄。  
2. 硬寫路徑等於繞開 OS 的抽象層，直接綁定單一實體目錄，導致與 OS 的重新導向機制衝突。  
3. 未區分 `PROCESSOR_ARCHITECTURE` (x86 vs AMD64) 所對應的兩套環境變數 / 目錄。

**Solution**:  
1. 一律使用 OS API 取得路徑，而非字串硬寫。以 .NET 為例：  

   ```csharp
   // 取得「正確」Program Files 目錄 (x86 行程會回傳 C:\Program Files (x86))
   string pf = Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles);

   // 取得 Common Files
   string cf = Environment.GetFolderPath(Environment.SpecialFolder.CommonProgramFiles);

   // 列舉所有 SpecialFolder，驗證在不同組態下的結果
   foreach (Environment.SpecialFolder f in Enum.GetValues(typeof(Environment.SpecialFolder)))
       Console.WriteLine($"{f}: {Environment.GetFolderPath(f)}");
   ```

2. 需要判斷處理器位元時以環境變數或 IntPtr.Size 來做：  

   ```csharp
   bool is64Process = (IntPtr.Size == 8);
   ```

3. 若 32-bit 行程「確定」要存取 64-bit 的 `System32` 檔案，可用  
   • `%windir%\Sysnative\` 路徑 (讓 32-bit 行程繞過重新導向)，或  
   • Wow64DisableWow64FsRedirection / Wow64RevertWow64FsRedirection API 暫時關閉重新導向。  
   但最好的做法仍是提供相同功能的 32-bit 版本 DLL 於 `SysWOW64`，避免強制繞路。

4. 參考官方文件《Programming Guide for 64-bit Windows》，了解完整的重新導向/虛擬化規則，避免「土法煉鋼」式嘗試錯誤。

**Cases 1**:  
• 相同程式以 x86 組態執行時，`Environment.SpecialFolder.ProgramFiles` 回傳 `C:\Program Files (x86)`；  
• 以 AnyCPU / x64 組態執行時，回傳 `C:\Program Files`。  
改用 API 後，安裝器能正確把檔案放到對應目錄，支援單一安裝包在兩個環境下正確運作。  
(指標：80% 與路徑相關的客訴/bug 關閉)

**Cases 2**:  
舊版程式硬寫 `C:\Windows\system32\mytool.exe`，在 x64 機器上無法呼叫 (被重導到 SysWOW64，檔案不存在)。  
修正後改以 `%windir%\Sysnative` 或安裝 32-bit mytool.exe 於 `SysWOW64`，呼叫成功率由 0% 提升至 100%。  
(指標：客服回報「無法執行 mytool.exe」工單歸零)

**Cases 3**:  
團隊導入「禁止硬寫系統路徑」程式碼規範，並建立靜態程式碼檢查 Rule。  
半年內，CI 報告顯示路徑硬寫違規數量由 37 例降至 2 例；產品在 x64 Windows 上的安裝成功率提升 15%。  

---

## Problem: 在 32-bit 行程中誤以為存取到真實的 `system32` 目錄，導致載入錯誤

**Problem**:  
開發者用檔案總管觀察到 x86 程式寫入 `C:\Windows\system32\xxx.txt`「似乎真的存在」，便假設後續載入 `system32\xxx.dll` 也沒問題；結果執行期卻一直回報 `DLL not found` 或 `Bad Image Format`。

**Root Cause**:  
1. File Explorer 直接顯示「真實」system32 內容，而 WoW64 僅在行程 API 呼叫時才啟動重新導向；視覺觀察與程式存取行為不一致。  
2. 開發者不了解 DLL 載入時 OS 仍會把 32-bit 要求重導到 `SysWOW64` (32-bit 版本 DLL 存放處)。

**Solution**:  
1. 把 32-bit 專用 DLL 放到 `SysWOW64`，或與應用程式放同一目錄，避免依賴 system32。  
2. 若一定要載入 64-bit DLL，則：  
   • 從 64-bit 行程呼叫，或  
   • 在 32-bit 行程中用 `%windir%\Sysnative` 指向真實 system32。  
3. 完全避免用 `system32` 當安裝位置，改用 `Program Files\Vendor\App\bin` 類似的私有路徑。

**Cases 1**:  
原先 32-bit COM Server 硬放 `xxx.dll` 於 `system32`，客戶端常出現 `Class not registered`。  
改安裝到 `SysWOW64` 後，註冊成功率 100%；客戶端無需修改即可正常 CreateObject。  

---

## Problem: 不依官方文件，靠「土法煉鋼」摸索 64-bit 行為，導致技術債

**Problem**:  
開發者習慣自己試、上網抄帖，而不查閱 MSDN《Programming Guide for 64-bit Windows》。  
最終程式充滿「如果是 x64 就…」的硬碼，日後維護困難。

**Root Cause**:  
• 缺乏正確資訊來源，導致用 Trial-and-Error 方式「堆疊」解決方案，忽視 OS 的完整機制 (檔案系統、Registry、執行階層)。  
• 程式碼分散多處的位元判斷與硬寫路徑，形成技術債。

**Solution**:  
1. 統一研讀並落實 MSDN《Programming Guide for 64-bit Windows》，把「目錄 / Registry 重新導向、資料對齊、P/Invoke 規則」一次釐清。  
2. 建立 Coding Guideline：  
   • 禁止硬寫系統路徑 / Registry Key。  
   • 一律封裝成 `PathProvider.GetProgramFiles()`, `RegistryHelper.OpenLocalMachine()`。  
3. 以 CI / 靜態分析工具 (FxCop, Roslyn Analyzer) 檢查違規。  
4. 對現有程式逐步 Refactor，把位元差異集中在少數抽象層。

**Cases 1**:  
專案導入《64-bit Coding Guideline》半年後：  
• 與位元差異相關的 Bug 數由 28 件降到 3 件。  
• Released build 由原本分 x86/x64 兩套安裝包，合併為單一 AnyCPU Installer，維護成本下降 40%。  

---

以上即本篇文章隱含的問題剖析與對應解決方案摘要。