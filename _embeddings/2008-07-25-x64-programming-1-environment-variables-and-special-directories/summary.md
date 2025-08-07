# x64 programming #1: 環境變數及特殊目錄..

## 摘要提示
- x86/x64 路徑差異: 同一支程式在 x86 與 x64 模式下，ProgramFiles 等目錄字串會自動指向不同路徑。
- SpecialFolder API: 使用 Environment.SpecialFolder 取得路徑，可避免手動硬寫目錄造成錯誤。
- 環境變數對照: PROCESSOR_ARCHITECTURE、ProgramFiles、CommonProgramFiles… 於 x86 與 x64 執行時值不同。
- 路徑重新導向: 64 位元 Windows 會針對檔案系統、Registry、Win32 API 進行 WOW64 Redirection。
- System32/SysWOW64: x86 程式雖見到 system32，但實際載入與存取多數檔案時會被導向至 syswow64。
- 磁碟空間雙倍: x64 作業系統為相容性同時存放 32/64 位元檔案，C 槽體積因此變大。
- 程式設計建議: 不要「湊路徑」，應透過 API 或環境變數取得正確位置。
- MSDN 正解: 官方「Programming Guide for 64-bit Windows」章節提供完整的相容性與最佳實作。
- 範例程式: 文中示範 C# 迴圈列舉 SpecialFolder 與環境變數，直觀比較差異。
- 下一篇預告: 作者將分享 IIS6 + x64 所遇到的「靈異事件」。

## 全文重點
本文作者基於實務經驗，示範了在 Vista x64 環境中，同一支 C# 程式以 x86、x64/Any CPU 兩種編譯設定執行時，系統回傳的特殊目錄與環境變數差異。首先藉由 Environment.SpecialFolder 列舉桌面、文件、ProgramFiles 等路徑，發現 x86 模式會指向 “C:\Program Files (x86)”，而 x64 模式則指向 “C:\Program Files”。接著列出所有環境變數，觀察 PROCESSOR_ARCHITECTURE、ProgramFiles、CommonProgramFiles(x86)、ProgramW6432、PROCESSOR_ARCHITEW6432 等關鍵變數如何因執行位元數改變而自動切換。作者提醒，硬寫路徑在 64 位元平台極易失敗，應透過 API 或環境變數取得正確位置；同理，Win32 API、Registry 與檔案系統也存在 WOW64 Redirection，32 位元程式會被導向至對應 32 位元路徑與金鑰。特別的是 system32 目錄：x86 程式看見的仍是 system32，但載入 DLL 或存檔時實際落點為 syswow64。由於系統同時保存兩套檔案，使用者會感覺到 C 槽變得更「肥大」。最後作者建議開發者參考 MSDN《Programming Guide for 64-bit Windows》，不要再依賴坊間零散、未驗證的做法，以免在 64 位元下踩雷。

## 段落重點
### 前言：被 x64 折騰的心得
作者長期在 64 位元環境開發，發現最常踩雷的是「目錄寫死」。文中決定透過程式實測，讓大家直觀看到 x86 與 x64 差異，並強調若程式只因「跑得動就交差」，遲早會在 64 位元環境出包。

### 列舉 SpecialFolder 的實驗
使用 C# 迴圈列舉 Environment.SpecialFolder，分別以 x86 與 x64/Any CPU 執行。結果顯示桌面、文件等使用者路徑一致，但 ProgramFiles、CommonProgramFiles 會從 “C:\Program Files (x86)” 切換成 “C:\Program Files”。說明使用 API 可讓程式自動取得正確路徑，無須人工判斷。

### 列舉環境變數的實驗
再以 Environment.GetEnvironmentVariables() 取出所有變數，比對兩模式下的輸出。x86 模式會出現 PROCESSOR_ARCHITECTURE=x86、ProgramFiles (x86) 等，而 x64 模式則顯示 AMD64、ProgramFiles 與額外的 (x86) 欄位供 64 位元程式存取 32 位元資料。此處也看到 ProgramW6432、PROCESSOR_ARCHITEW6432 等專用變數，提醒開發者利用變數判斷目前執行位元及定位資料夾。

### System32 與 SysWOW64 的「隱形轉換」
同樣目錄問題最複雜的是 system32。實測發現即使 x86 程式寫檔到 C:\Windows\system32，實際檔案卻真的存在 system32；然而當程式嘗試載入 DLL 或執行檔時，作業系統會自動將呼叫導向至 C:\Windows\syswow64 的 32 位元版本。此層「WOW64 Redirection」同樣套用在 Registry 與 API 上，保證 32 位元程式不需修改即可運作，但也可能造成路徑誤判。

### 結語與延伸閱讀
因為 64 位元 Windows 必須同時維持 32/64 相容性，系統磁碟空間與維護成本都會增加。開發者若想真正支援 x64，需要熟悉 MSDN《Programming Guide for 64-bit Windows》所列最佳實踐，避免「土法煉鋼」。作者預告下一篇將分享 IIS6 在 x64 下遇到的種種「靈異事件」，供讀者參考。