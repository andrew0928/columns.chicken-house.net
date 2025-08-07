# 在 Docker 上面執行 .NET (CoreCLR) Console App

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 可以在 Linux 的 Docker Container 中執行 .NET Core (CoreCLR) Console Application 嗎？
可以。只要在 Docker 主機上拉下 Microsoft 提供的 ASP.NET CoreCLR 映像檔 (例如 microsoft/aspnet:1.0.0-beta8-coreclr)，把已編譯好的 .NET Core Console 程式複製進 Container，並在 Container 內以 dnvm/dnu/dnx 等指令啟動即可成功執行。

## Q: 讓「Hello World」Console App 在 Docker 裡跑起來，作者實際做了哪些步驟？
1. `docker pull microsoft/aspnet:1.0.0-beta8-coreclr` 下載官方映像。  
2. `docker run -d --restart always microsoft/aspnet` 以背景模式啟動 Container。  
3. `docker exec -it <container-id> /bin/bash` 進入 Container 的 shell。  
4. 用 dnvm 確認/安裝想要的 CoreCLR 版 dnx。  
5. 將 Visual Studio 2015 產出的 Console App 檔案透過 `docker cp` 複製到 Container，例如 `/home/ConsoleApp1/`。  
6. 進入專案資料夾，執行 `dnu restore` 下載相依套件。  
7. 最後以 `dnx run` 啟動程式，看到「Hello .Net Core!」即代表成功。

## Q: 為什麼作者認為「.NET 開源 + 支援 Linux」的影響大於 ASP.NET 5 架構本身？
因為開源並支援多平台改變的是整個 .NET 生態與系統佈署策略，日後在 Windows 或 Linux 上都能採用「混搭」架構，對系統架構師的決策影響遠超過 MVC6、動態編譯等單純開發層面的變動。

## Q: 相較於傳統虛擬機 (VM)，Docker 帶來的主要優勢是什麼？
Docker 只虛擬化「應用程式執行環境」，不需要為每個服務安裝並維護完整作業系統，因此能節省大量運算資源與維運成本，也避免一台實體主機內多台 VM 同時執行作業系統與防毒程式造成的效能拖累。

## Q: 小型應用為什麼不適合硬拆成三台 VM 實作三層式架構？Docker 又如何改變這件事？
對規模不大的系統，一台低規格 VM 就能運作，硬拆三台 VM 只會增加維運負擔與資源消耗。使用 Docker 則可在同一台實體機上以三個 Container 切分層次，兼顧架構正確性又不需額外 OS 負擔。

## Q: 作者在正式執行 .NET Core 前做了哪些前置準備？
1. 先花時間熟悉 Docker 的概念、應用與實作，並把自己的 WordPress 部落格搬進 NAS Docker 環境。  
2. 手動在舊筆電安裝 Ubuntu Server，體驗從零建置 Docker 執行環境的細節。  
3. 研究 .NET Core 的核心工具 (DNVM、DNU、DNX) 與佈署流程，才開始測試 Console App。

## Q: 什麼是 Core CLR？
Core CLR 全名「.NET Core Common Language Runtime」，是為跨平台重新封裝的 CLR。與傳統 Windows-only 的 .NET Framework 不同，Core CLR 可在 Linux、macOS 等系統上運行，且可依專案需求只佈署用得到的 Base Class Library。

## Q: DNVM、DNX、DNU 分別扮演什麼角色？
• DNVM (.NET Version Manager)：管理與切換不同版本的 DNX。  
• DNX (.NET Execution Environment)：啟動並執行 .NET/ASP.NET 應用，相當於 .NET 的執行器。  
• DNU (.NET Utilities)：開發人員工具，用於建置 (build)、還原套件 (restore) 等工作。

## Q: 作者實驗時選用的 Docker 映像是哪一個？
Microsoft 官方在 Docker Hub 釋出的 “ASP.NET 5 Preview” 映像，標籤為 microsoft/aspnet:1.0.0-beta8-coreclr。

## Q: 作者遇到的最大困難是什麼？最後如何解決？
市面教學大多著重「在 Docker 跑 ASP.NET Web 站台」，而作者只想跑 Console App，因此缺少一步到位的說明。作者最後改以 `docker exec` 進入官方映像的 Container，直接手動執行 dnvm/dnu/dnx 並複製程式，才成功在 Ubuntu Server 上跑出「Hello .Net Core!」。