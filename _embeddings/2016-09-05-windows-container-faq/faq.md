# Windows Container FAQ - 官網沒有說的事

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Windows Container 與 Docker for Windows 是一樣的東西嗎？
不一樣。  
• Windows Container 是微軟自 Windows Server 2016 起內建的容器引擎，與 Docker 架構相容，但共用的是 Windows Kernel，只能執行 Windows 應用程式。  
• Docker for Windows 則是在 Windows 上啟動一台 Alpine Linux 虛擬機，讓你操作 Linux 版 Docker Engine，因此只能執行 Linux 應用程式。

## Q: 要在什麼環境才能使用 Windows Container？
目前僅支援 Windows Server 2016；公開的最新版本是 2016/04 發佈的 Tech Preview 5，正式版預計 2016/10 釋出。  
若想在桌機體驗，Windows 10 Pro／Enterprise 在 2016/08 的 RS 更新後，可透過 Hyper-V 隔離模式執行 Windows Container。

## Q: Windows Container 能執行現有的 Linux Docker Image 嗎？
不能。Windows Container 只能執行 Windows 應用程式，必須使用為 Windows 打包的 Container Image。

## Q: 我可以用 Docker Client 來管理 Windows Container 嗎？
可以。Docker Client 與 Docker API 是共用的，甚至可以用 Linux 版 Docker Client 直接連線到 Windows Server 上的 Container Engine 進行管理。

## Q: 要去哪裡取得 Windows Container 的 Image？
方式與傳統 Docker 相同，可從 Docker Registry 取得或自行以 Dockerfile 建置。  
在 Docker Hub 上可搜尋 microsoft/windowsservercore、microsoft/nanoserver、microsoft/iis 等官方基礎映像。  
官方也在 GitHub 提供範例 Dockerfile，參見「Windows Container Samples」。

## Q: Windows Server 2016 Tech Preview 5 執行 Windows Container 時有哪些已知問題或限制？
大部分情境已能正常運作，但網路相關功能尚未完整：  
• 不支援 container linking (--link)。  
• 目前沒有內建的名稱／服務解析（DNS 解析支援將以後續更新補上）。  
• 預設的 overlay network driver 及多項 Docker 網路參數 (--dns、-h、--net-alias 等) 皆未支援。  
若需要大量網路功能（如微服務架構），需等正式版或後續更新。

## Q: 有哪些官方或社群文件可協助熟悉 Linux Docker 的人快速上手 Windows Container？
1. 微軟官方「關於 Windows 容器 – 常見問題集」。  
2. 微軟官方「容器主機部署 – Windows Server」。  
3. InfoQ 文章〈细说Windows与Docker之间的趣事〉。  
4. GitHub 專案「Windows Container Samples」提供多種範例 Dockerfile。