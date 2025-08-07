# [.NET Core] Running .NET Core RC1 on Docker - DOTNET CLI

# 問答集 (FAQ, frequently asked questions and answers)

## Q: .NET Core / ASP.NET 5 推出 RC1 代表什麼意義？
RC (Release Candidate) 表示功能已經凍結、品質達到可正式發布的水準，並且是「Go-Live」等級；只要沒有重大問題，接下來就會進入 RTM，因此目前是評估或導入 .NET Core 的好時機。

## Q: Microsoft 在 Docker Hub 上釋出的與 RC1 相關的兩個 Image 有何不同？
1. microsoft/aspnet：仍採用 DNVM / DNX / DNU 指令集，只是版本升級到 RC1。  
2. microsoft/dotnet：內含全新的 DOTNET CLI（v0.0.1-alpha preview），把 DNVM / DNX / DNU 整合成單一 `dotnet` 指令，並加入原生編譯等新功能。

## Q: DOTNET CLI 與舊有的 DNVM / DNX / DNU 是什麼關係？
DOTNET CLI 把 DNVM（Runtime 管理）、DNX（執行）、DNU（維護）三支工具整併成單一 `dotnet` 指令，使用者透過 `dotnet init / restore / compile / run` 等命令即可完成專案初始化、套件還原、編譯與執行；目前版本仍是 0.0.1-alpha，屬於早期預覽。

## Q: 如何在 Docker 容器內從零開始建立並執行一個 .NET Core「Hello World」？
1. 下載映像：`docker pull microsoft/dotnet`  
2. 啟動容器：`docker run --name dotnet --rm -it microsoft/dotnet /bin/bash`  
3. 建立專案：`dotnet init`（產生 Program.cs 與 project.json）  
4. 還原套件：`dotnet restore`  
5. 編譯程式：`dotnet compile`  
6. 執行程式：`dotnet run`  
最後即可在終端機看到「Hello World!」。

## Q: `docker run --rm -v "$PWD":/myapp -w /myapp microsoft/dotnet dotnet compile` 這段指令在做什麼？
`--rm` 讓容器在命令結束後自動移除；`-v` 把目前目錄掛載進容器，`-w` 設定工作目錄。結果是在一次性（可拋棄）的容器中完成專案編譯而不必長時間保留容器。

## Q: 採用 DOTNET CLI 時常見的障礙有哪些？
由 Beta 版升到 RC1 可能遇到：  
• 預設執行到 .NET Framework 4.6.1 而非 .NET Core runtime  
• 相依的 Assembly/套件版本衝突或找不到  
• NuGet 無法解析正確版本  
• 程式能編譯執行但 Console 無輸出  
建議先全面更新至 RC1，相依套件也同步升級，再逐一排除上述差異帶來的問題。