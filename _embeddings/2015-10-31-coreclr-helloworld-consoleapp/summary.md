# 在 Docker 上面執行 .NET (CoreCLR) Console App

## 摘要提示
- .NET核心開源: Microsoft 將 .NET Core 及其 CLR 開放原始碼並支援 Linux，為生態系帶來跨平台轉變。  
- Docker容器: 以容器技術取代傳統 VM，可減少系統資源浪費並簡化維運流程。  
- 架構混搭: 未來系統架構可在 Windows 與 Linux 混合佈署，Architect 必須提早因應。  
- 環境準備: 作者使用 Synology NAS 與 Ubuntu Server 自建 Docker 實驗平台。  
- DNVM-DNX-DNU: 了解三大命令（版本管理、執行環境、開發工具）是操作 .NET Core 的基礎。  
- CoreCLR定義: CoreCLR 重新封裝 CLR 與 BCL，可獨立佈署並跨平台運行。  
- 官方Image: 選用 Microsoft 提供的 aspnet Docker Image，跳過繁雜安裝直接取得執行環境。  
- Console範例: 透過 dnu restore 與 dnx 執行，成功在 Linux 容器印出 “Hello .NET Core!”。  
- 操作步驟: docker pull、run、exec、cp 等指令串起整個部署與測試流程。  
- 實務體驗: 作者強調動手實作與後續維運才是學習新技術的關鍵，而不僅是 POC。  

## 全文重點
本文記錄作者如何在 Docker 容器中執行一支最簡單的 .NET Core（CoreCLR）Console 應用程式，並分享過程中的心路歷程與技術重點。Microsoft 在 Satya Nadella 上任後宣布 .NET 開源並原生支援 Linux，這一策略不僅影響開發模式，更衝擊系統架構與部署思維。同一時間，容器技術 Docker 迅速崛起，以「只虛擬化應用層」的方式解決傳統 VM 過度消耗資源與管理複雜度的痛點；兩者若能結合，可讓 .NET 應用在 Windows 與 Linux 間自由穿梭，並以微服務或三層式架構拆分成多個容器獨立部署。

作者先透過 Synology NAS 內建 Docker 套件和一台舊筆電重裝的 Ubuntu Server，實際練習容器管理、反向代理、備份等維運工作，確認自身對 Docker 的掌握。接著把焦點放到 .NET Core 的三大命令：DNVM（版本管理）、DNX（執行環境）與 DNU（開發工具），並說明 CoreCLR 與傳統 .NET Framework 在可攜性與封裝上的差異。為了省去在 Linux 手動安裝 .NET Core 的麻煩，他直接拉取 Microsoft 提供的「aspnet:1.0.0-beta8-coreclr」Image；透過 docker run 啟動後，以 docker exec 取得互動 Shell，將 Visual Studio 2015 編譯好的 Hello World 複製進容器。最後在容器內執行 dnu restore 下載相依套件，再用 dnx 呼叫程式，成功在 Ubuntu Server 列印訊息，完成「在 Linux 上跑 .NET」的里程碑。

文章強調：1) Architect 應及早熟悉跨平台與容器化帶來的混搭部署模式；2) 學習新技術不能停在 POC，必須涵蓋環境建置與維運；3) 善用官方提供的 Docker Image 可大幅縮短嘗試門檻。全文詳述背景觀念、名詞定義及逐步操作流程，供對 .NET Core 與 Docker 有興趣、但尚未熟悉 Linux 的開發者參考。

## 段落重點
### 進入主題: .NET Core CLR 體驗
作者說明學習路徑：首先以最短時間理解 Docker 概念與實作，並選擇搬遷個人 WordPress Blog 作為實戰目標，藉此體會容器對架構與資源的優勢；其次自建 Ubuntu Server 練習純命令列管理，補足 NAS 圖形介面遮蔽的細節；最後才開始接觸 .NET Core，決定先以 Console App 而非 ASP.NET 進行測試，確保熟悉 DNVM、DNU、DNX 的基本操作。透過「先環境、後程式」的策略，他為後續深入 ASP.NET 5 打下堅實基礎，也示範了學習新技術應該從整體部署觀點出發。

### .NET Core CLR 的名詞定義
本段整理關鍵名詞：CoreCLR 是可跨平台的 .NET 執行時，內含最小化 BCL，可按需佈署；DNX 相當於 .NET 的 runtime/啟動器，對等於 Java 的 java.exe；DNVM 是管理多版本 DNX 的工具，負責安裝、升級與切換；DNU 則提供建置、相依套件復原等功能，類似 javac + npm 組合。理解這四者的關係是能否在非 Windows 環境順利開發與部署 .NET Core 的關鍵。作者推薦兩篇國外文章作進一步閱讀，並以圖示輔助說明，使讀者快速掌握新舊框架差異與開發流程。

### 將 .NET Core APP 放進 Docker 執行
實作部分，作者採「懶人方案」：直接 `docker pull microsoft/aspnet:1.0.0-beta8-coreclr` 取得含 .NET Core 的官方 Image，避免自行在 Linux 安裝 DNX。接著以 `docker run -d --restart always` 背景啟動容器，`docker exec -it <id> /bin/bash` 進入互動 Shell。程式方面，他使用 Visual Studio 2015 建立 ConsoleApp1，編譯後透過 `docker cp` 複製至容器 `/home/ConsoleApp1/`。在容器內執行 `dnvm list` 檢查並啟用 x64 coreclr 版本，`dnu restore` 還原 NuGet 相依，最後 `dnx run` 成功輸出 “Hello .NET Core!” 及 OS 版本資訊。此流程證明 .NET Core 可在 Linux 容器無縫執行，並示範了 docker 指令與 DNX 工具鏈的串接方法。作者以此為起點，未來將深入研究 ASP.NET 5 與更複雜的部署策略。