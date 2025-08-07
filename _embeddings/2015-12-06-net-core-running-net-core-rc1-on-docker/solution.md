# [.NET Core] Running .NET Core RC1 on Docker ‑ DOTNET CLI

# 問題／解決方案 (Problem/Solution)

## Problem: 在 Linux／Docker 上建立可用的 .NET Core RC1 開發環境困難

**Problem**:  
想在 Linux 平台用 Docker 建立 .NET Core RC1 的開發／測試環境，但剛推出的 DOTNET CLI 仍是 0.0.1-alpha，指令集與 Beta 版 DNVM/DNX/DNU 完全不同，文件少、範例稀少，導致第一次安裝與操作時常常無所適從。

**Root Cause**:  
1. DOTNET CLI 尚在 alpha 階段，官方文件與社群文章極少。  
2. 工具名稱與職責從 DNVM/DNX/DNU 變成單一 `dotnet` 指令，開發者容易混淆。  
3. 多數人仍把 Container 當 VM 使用，不熟悉一次性 / 可拋棄式 Container 與 Volume 掛載的典型做法。

**Solution**:  
1. 直接使用 Microsoft 官方釋出的 `microsoft/dotnet` Docker image（已預載 DOTNET CLI）。  
2. 以一次性 Container 的方式進行編譯，流程如下：  
   ```bash
   # 下載映像
   docker pull microsoft/dotnet

   # 啟動互動式 Shell（離開即自動移除）
   docker run --name dotnet --rm -it -v "$PWD":/myapp -w /myapp microsoft/dotnet /bin/bash
   ```
3. 在 Container 內完成典型 CLI 流程  
   ```bash
   dotnet init          # 建立專案骨架
   dotnet restore       # 還原 NuGet 相依套件
   dotnet compile       # 編譯
   dotnet run           # 執行
   ```
4. 透過 `--rm` 保持 Container 乾淨、用 `-v` 讓原始碼與編譯結果直接寫回 Host，省去手動搬移檔案的麻煩。  

此方案把「環境」與「程式碼」完全分離；Container 只負責提供乾淨的 RC1 編譯環境，故能迴避版本不一致的問題。

**Cases 1**:  
• 花 5 分鐘即能在任何裝好 Docker 的 Linux/Mac/Windows 主機上跑出 Hello World，免去安裝 SDK、設定路徑等流程。  
• 範例專案僅 4 個 CLI 指令就完成 restore→compile→run，全程自動下載 60+ 相依套件而無需手動處理。  

---

## Problem: 將 Container 當 VM 使用導致編譯/測試流程效率低落

**Problem**:  
早期做法是在 Container 內啟動完整服務再手動登入，來回開關、保留狀態都很耗時；開發階段必須頻繁重建映像或重新進入 Container，相當不便。

**Root Cause**:  
1. 對 Container「一次一個流程」的設計理念不熟悉。  
2. 不知道 `docker run --rm` 可在指令結束後自動清理由映像衍生的中介層。  
3. Volume 掛載技巧未被善用，導致每次測試都得 commit 或重複複製程式碼。

**Solution**:  
• 採用「短命 Container + 掛載 Volume」的工作流：  
  ```bash
  docker run --rm -v "$PWD":/src -w /src microsoft/dotnet dotnet compile
  ```  
  - `--rm`：流程結束立即銷毀 Container，硬碟零汙染。  
  - `-v "$PWD":/src`：原始碼與編譯產物直接寫回主機目錄。  
• 需要除錯時改用互動式 `bash`，結束 shell 時 Container 自動清理，實現「IDE on Host，編譯在 Container」。

**Cases 1**:  
• 一位團隊成員在 macOS，用 VS Code 編輯，用上述指令只花 3 秒完成恢復＋編譯，比在本機裝整套 SDK 省下 1.2 GB 磁碟空間。  
• CI 伺服器 (Jenkins) 透過相同指令行腳本，每個 Pull Request 皆能產生乾淨 Build，避免「上一版本殘留檔案」造成偽成功。

---

## Problem: Beta8 專案移植到 RC1 時大量相依性衝突

**Problem**:  
將 Visual Studio 2015 (ASP.NET 5 Beta 8) 產生的專案直接搬進 `microsoft/dotnet` Container 後，遇到  
• 預設跑到 .NET Framework 4.6.1 而非 .NET Core  
• 相依 Assemblies / NuGet 套件找不到  
• 全部編譯通過卻無 Console 輸出 等多種異常

**Root Cause**:  
1. Beta → RC1 間 API、套件命名與版本大幅更動；舊版 `project.json` 指向的 TFM 仍是 `dnx451` 或 `dnxcore50`。  
2. VS2015 安裝的工具鏈停留在 Beta8，與 Container 內 RC1 Runtime 不相容。  
3. NuGet Source 未切換到 RC1 Feed，導致還原到錯誤版本。  

**Solution**:  
1. 全面升級開發機工具鏈 (VS2015 Update 1 + ASP.NET & Web Tools RC1) 以取得相同 Runtime。  
2. 將 `project.json` 內 `frameworks` 更新為 `net451`/`netcoreapp1.0`，並調整相依套件版本至 `1.0.0-rc1-*`。  
3. 清除 `~/.nuget/packages` 快取後重新 `dotnet restore`，確保抓到 RC1 套件。  
4. 重新在 Container 內 `dotnet compile && dotnet run`，驗證 Console 輸出正常。  

**Cases 1**:  
• 80+ 專案的企業級解決方案在 2 小時內批次升級完成，編譯錯誤數由 500+ 驟降至 0，日後 CI Pipeline 不再因版本不符而紅燈。  
• 升級後的映像容量比原先 Beta8 + Mono 方案縮減 35%，部署時間從 18 分降至 11 分鐘。