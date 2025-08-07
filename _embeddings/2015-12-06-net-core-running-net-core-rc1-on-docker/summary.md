```markdown
# [.NET Core] Running .NET Core RC1 on Docker ‑ DOTNET CLI

## 摘要提示
- RC1發佈: .NET Core／ASP.NET 5 進入 Go-Live 階段，可正式佈署並獲微軟支援  
- 跨平台: 同時支援 Windows、OS X、Linux，適合開始評估導入  
- DOTNET CLI: 以單一 dotnet 指令整合 DNVM、DNX、DNU，版本 0.0.1-alpha  
- Docker映像: 提供 microsoft/aspnet 與 microsoft/dotnet 兩種，分別對應舊新工具  
- 可拋棄容器: docker run --rm 搭配 -v，容器僅充當一次性編譯環境  
- Hello World流程: init→restore→compile→run 四步驟在 Linux 容器跑 C#  
- 原生編譯: dotnet compile 已支援產生 native code，提高效能  
- 移植門檻: BCL 缺口與第三方套件版本衝突是跨平台最大挑戰  
- 研究方向: 後續將測試效能、記憶體與企業部署效益  
- 參考資源: 官方 GitHub README 與多位微軟技術部落格可供查閱  

## 全文重點
Microsoft 在 Connect 2015 大會宣布 .NET Core 與 ASP.NET 5 RC1，標示產品已凍結功能並達到「Go Live」品質，開發者得以安心將其用於生產環境並取得官方支援。隨 RC1 而來的最大改變是推出「DOTNET CLI」，將原本分散的 DNVM、DNX、DNU 命令整併為單一 dotnet 指令，並於 Docker Hub 提供兩款映像：延用舊工具的 microsoft/aspnet，以及搭載新 CLI 的 microsoft/dotnet。新 CLI 不僅結構清晰，更開始支援 Native Compilation 等功能。

文章重點放在如何於 Docker 容器中使用 DOTNET CLI。若僅需編譯而不在容器執行程式，可透過  
docker run --rm -v $PWD:/myapp -w /myapp microsoft/dotnet dotnet compile  
實現一次性建置環境；也可啟動 /bin/bash 以互動模式多次下達 dotnet 指令。作者以「Hello World」示範：首先 pull 映像並 run 容器，接著用 dotnet init 建立 Program.cs 與 project.json；dotnet restore 下載 NuGet 相依套件；dotnet compile 完成編譯；最後 dotnet run 在 Linux 主控台輸出訊息，證明 .NET 程式能順利跨平台運行。

雖操作流程簡化，但移植現有 .NET 專案仍受三大因素影響：1) 仍僅存在於 .NET Framework 的 BCL 必須改寫或等待 Core 支援；2) 部分第三方套件尚未發布 RC1 版本，導致 restore 失敗或 assembly 缺漏；3) Beta 至 RC1 API 與包名稱變動，使舊專案升級時常出現編譯及執行錯誤，甚至 output 消失等異常。作者將於後續文章深入評估不同平台的效能差異、記憶體管理特性，並分析企業在導入 .NET Core＋Linux 時可期待的成本與部署效益。

## 段落重點
### Announcing .NET Core and ASP.NET 5 RC1
RC1 代表功能凍結、品質成熟，並取得 Go-Live 支援；跨 Windows、OS X、Linux 三平台釋出，使企業與開發者能正式規畫部署。作者強調自己研究焦點在於跨平台後能帶來的成本、資源與部署彈性，而非僅僅在 Linux 執行程式本身。

### 新玩意：DOTNET CLI 整合工具
RC1 推出 DOTNET CLI，把 DNVM、DNX、DNU 三種工具統整至單一 dotnet 命令，使用者可透過 init、restore、compile、publish、run 等子命令完成完整生命週期。Docker Hub 提供兩映像：microsoft/aspnet（舊工具）與 microsoft/dotnet（新 CLI），後者亦新增 Native Compilation 等功能，命名及結構更易理解。

### DOTNET CLI Container 的使用技巧
官方 README 提示可利用 docker run --rm 配合 -v 掛載，把容器當成一次性建置環境，編譯完即自動清除，減少系統污染。若需頻繁操作，可改以 /bin/bash 進入互動式 shell，結束後容器才被移除，兼具便利與乾淨。

### Hands-On Lab：Hello World 範例操作
步驟：1) pull microsoft/dotnet；2) run 容器並進入 /bin/bash；3) dotnet init 建置專案架構；4) dotnet restore 還原套件；5) dotnet compile 編譯，可選 --native；6) dotnet run 執行並顯示 “Hello World!”。過程中示範如何使用 -v 掛載目錄及 --name 指定容器名稱，並觀察相依套件下載與版本衝突警告。

### 兼談跨平台移植與常見問題
真正的門檻在於 API 與套件支援度：部分 BCL 尚未移植至 .NET Core，許多第三方庫也未跟上 RC1；Beta → RC1 的包名與 API 變動造成 restore 或執行失敗。作者在 Windows 10／VS2015 beta8 專案搬移時就遇到 runtime 指向 .NET 4.6.1、console 無輸出等問題，顯示環境一致性的重要。後續將針對效能、記憶體與企業導入價值再作深入分析。
```