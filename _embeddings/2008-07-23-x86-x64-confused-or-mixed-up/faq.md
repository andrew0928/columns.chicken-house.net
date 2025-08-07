# x86? x64? 傻傻分不清楚...

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 用 .NET 專案把「Platform」設成 ANY CPU，程式在 x64 Windows 上就一定可以正常執行嗎？
不一定。ANY CPU 只代表 IL 在載入時會依作業系統自動轉成 32 或 64 位元，但如果程式在執行期間還要呼叫「只有 x86 版」的 COM 元件（例如 CDO、Jet/ODBC driver 等），當程序被載成 64 位元時就會發生 Run-time Error。

## Q: 16 → 32 位元與 32 → 64 位元的相容模式，微軟採取了哪些不同做法？
16 → 32 時期靠的是處理器的 v86 mode，加上 Windows 內的 wowexec，所有 16 位元程式集中在單一 32 位元 Process 執行；32 → 64 時期則改用 WoW64，在 User-mode 即可同時提供 32 與 64 位元環境，但「同一個 Process 不能同時存在兩種位元的程式碼」，必須擇一執行。

## Q: 64 位元 Windows 為什麼會有兩個 Program Files 與 System32 目錄？
為了隔離 32 與 64 位元程式。64-bit 應用安裝到「Program Files」，32-bit 應用安裝到「Program Files (x86)」。同理，原本的 System32 在 x64 Windows 其實存放 64-bit DLL，32-bit DLL 則放在 SysWow64。Registry 也有對映機制，各維持一份。

## Q: 在同一支程式內能同時載入 x86 與 x64 COM 元件嗎？
不行。WoW64 的限制之一就是「In-process」元件必須與呼叫者位元數相同；若主程式是 32 位元，就只能載入 x86 COM，反之亦然。

## Q: 如果必須同時使用「只支援 x86 的 Canon RAW Codec」與「只支援 x64 的 Media Encoder」，有解嗎？
做法是把功能拆成多個獨立 .exe：需要 Canon RAW 的部分以 x86 編譯、使用 x86 COM；需要 Media Encoder 的部分則以 x64 編譯、使用 x64 COM。各程式各自運作，透過檔案或參數串接，可同時充分利用多核心 CPU。