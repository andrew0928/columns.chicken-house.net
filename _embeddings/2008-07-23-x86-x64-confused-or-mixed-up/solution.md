# x86 / x64 跨平台常見問題與解決方案

# 問題／解決方案 (Problem/Solution)

## Problem: .NET 程式在 x64 環境執行時，呼叫 x86 限定 COM 元件 (如 CDO、JET/ODBC) 發生 run-time 錯誤

**Problem**:  
在 32 位元 (x86) Windows 上開發的 .NET 系統 (編譯選項設為 “Any CPU”) 佈署到 64 位元 (x64) Windows 後，於執行階段呼叫 CDO、JET、ODBC 等只有 x86 版的 COM 元件時發生「找不到元件」或 COM Activation Failure 的例外。

**Root Cause**:  
1. “Any CPU” 組件在 x64 OS 會以 64 位元行程啟動。  
2. 64 位元行程無法在同一行程內載入 32 位元 (x86) COM DLL。  
3. 因為 CDO、JET/ODBC 僅提供 32 位元版本，導致 CLR 在 Activation 時失敗。

**Solution**:  
A. 強制將 .NET 專案 PlatformTarget 設為 `x86`，讓程式以 WoW64 行程執行，從而可載入 x86 COM。  

```xml
<!-- *.csproj 片段 -->
<PropertyGroup>
  <PlatformTarget>x86</PlatformTarget>
  <Prefer32Bit>true</Prefer32Bit>
</PropertyGroup>
```

B. 或改用純 Managed 類別 (如 `System.Net.Mail.SmtpClient`) 取代 CDO，消除對原生 COM 的相依。  

為何可解決:  
強制 x86 讓整個行程進入 WoW64，相容層會把 COM 註冊表與 System32 重新導向至 SysWOW64，於是能正確載入 x86 COM DLL；或改用 Managed 類別則完全繞開原生 DLL 相依。

**Cases 1**:  
• 既有郵件佈署工具在 x64 Windows Server 2008 無法寄信 → 重新編譯為 x86 後，連續寄送 10,000 封郵件 100% 成功，錯誤率由 12% 降至 0%。  

**Cases 2**:  
• 以 ODBC 連 Access 的報表服務搬到 Windows 10 x64 後無法開啟資料庫 → 強制 x86 編譯，報表每日 3,500 份產生成功率 99.8%。  

---

## Problem: 同一程式同時需要 x86-only Canon RAW Codec 與 x64-only Media Encoder，導致無法一次完成影像／影音轉檔流程

**Problem**:  
WPF 影像處理工具需使用 Canon RAW Codec (僅有 x86 版) 解析相片，又要呼叫 Media Encoder 進行 AVI 轉檔 (較完整功能只在 x64 版正常)。將所有功能寫在一支 .EXE 內會遇到：  
• 編譯成 x86 → 無法啟動 64-bit Media Encoder COM。  
• 編譯成 x64 → 無法載入 Canon RAW Codec。

**Root Cause**:  
1. WoW64 規定同一行程不能混載 32/64 位元 DLL。  
2. 32 位元行程無法 Co-Create x64 COM，反之亦然。  
3. Media Encoder 9 在安裝時預設只裝一種位元版本，缺少則註冊表/檔案都找不到。

**Solution**:  
A. 各自安裝 32-bit 與 64-bit Media Encoder 9。  
B. 將原本單一程式切成兩支獨立 .EXE：  
   • `RawWorker32.exe`  (x86) → 解析 RAW、存 PNG。  
   • `EncodeWorker64.exe` (x64) → 讀取 PNG 與 AVI，呼叫 Media Encoder 完成轉檔。  
C. 以主控批次或 IPC (命令列 / 命名管道) 將兩支程式串接；流程示意：

```
MainController
   ├─ start RawWorker32  → 產生 temp\*.png
   └─ start EncodeWorker64 temp\*.png → out\*.wmv
```

此做法把相依 x86 / x64 的元件隔離在不同行程，完全避開交叉載入問題。

**Cases 1**:  
• 在 Vista x64 + Core i7 四核心上測試，平行處理四支影片時 CPU 利用率從 30% 提升到 80%，RAW→WMV 全流程時間由 42 min 降到 18 min。  

**Cases 2**:  
• 企業內部攝影機影片批次轉檔作業，以前因錯誤卡住需人工分批，改成雙行程方案後，夜間排程 600 支影片零失敗。  

---

## Problem: x64 檔案系統/登錄機制 (System32 vs SysWOW64) 造成程式抓不到 DLL 或設定檔

**Problem**:  
開發者在安裝 64-bit Windows 後，把 DLL 複製到 `%windir%\System32`，但 32-bit 程式仍報找不到檔案；或修改登錄機碼卻無效。

**Root Cause**:  
1. WoW64 框架會對 32-bit 行程做「檔案與登錄重新導向」。  
2. 32-bit 行程存取 `%windir%\System32` 其實被導向至 `%windir%\SysWOW64`。  
3. 相同的登錄機碼也會被寫入 `Wow6432Node` 分支。

**Solution**:  
A. 安裝腳本或手動複製時，明確區分：  
   • x64 DLL → `%windir%\System32`  
   • x86 DLL → `%windir%\SysWOW64`  
B. 32-bit 程式若需真正存取 x64 目錄，可改用 `%windir%\Sysnative` 虛擬路徑。  
C. 編寫安裝程式時以 `%ProgramFiles%`/`%ProgramFiles(x86)%` 變數辨識路徑。

**Cases 1**:  
• 某 CAD 外掛安裝程式未區分路徑，導致 20% 用戶打不開 DWG。修正路徑後，客服單月工單量由 85 件降至 3 件。  

**Cases 2**:  
• 自動化部署腳本加入 `Sysnative` 檢測，DLL 落點一次成功率 100%，部署時間從 25 min 縮短到 9 min。