# Windows Container FAQ - 官網沒有說的事

## 摘要提示
- 目標讀者: 本文鎖定已熟悉 Linux Docker、想快速了解 Windows Container 的技術人員。
- 核心差異: Windows Container 與 Docker for Windows 是兩套不同技術，前者跑 Windows App、後者跑 Linux App。
- 使用條件: 目前僅 Windows Server 2016（TP5）與更新後的 Windows 10 Pro/Ent 支援 Windows Container。
- 相容性: Windows Container 無法直接執行 Linux 容器映像，必須使用專為 Windows 打包的映像。
- 管理工具: Docker Client 與 Docker API 完全共用，可跨平台遙控 Windows Container。
- 取得映像: Microsoft 在 Docker Hub 提供 windowsservercore、nanoserver 兩大基底映像及多款延伸範例。
- 隔離模式: Windows Container 支援 Process-isolation 及 Hyper-V-isolation 雙模式。
- 網路限制: TP5 缺乏 container linking、內建 DNS 等網路功能，微服務部署受限。
- 上市時程: Microsoft 預計 2016/10 發行正式版，TP5 已可用於概念驗證與相容性評估。
- 求助管道: 官網 FAQ、部署文件與 Microsoft GitHub 範例是現階段最佳參考來源。

## 全文重點
作者原先因工作仍以 ASP.NET WebForm 為主，難以直接享受 .NET Core 與 Linux Docker 的效益，遂將研究重點轉向能承載既有 Windows 應用的 Windows Container。於 2016 年 Community Open Camp 擔任講者後發現社群需求殷切，因而整理出一份「官網沒說的 FAQ」，協助讀者快速掌握 Windows Container 的真實使用情境與限制。

文中首先區分 Windows Container 與 Docker for Windows：兩者皆利用 Docker 生態，但前者是 Microsoft 在 Windows Server 2016 原生實作的 Container Engine，以 Windows Kernel 為基礎，只能執行 Windows 應用；後者僅是在 Windows 上用 Hyper-V 啟動微型 Linux VM，透過預先配置的工具讓使用者方便操作 Linux Docker，實際執行的仍是 Linux 應用。

接著說明使用條件與安裝步驟，目前官方僅支援 Windows Server 2016 TP5 及更新後的 Windows 10（Hyper-V 隔離）。Windows Container 提供 Process 與 Hyper-V 兩種隔離層級，佈署方式可參考官方快速入門文件。對於相容性，Windows Container 不能直接運行現有 Linux 映像，必須自行以 Windows Server Core 或 Nano Server 基底重建映像，或從 Docker Hub 搜尋「microsoft/*」前綴的 Windows 版本。

作者強調 Docker Client、API、映像格式、Registry 等皆與 Linux Docker 共用，使用者可直接用 Linux 或 Windows 的 Docker CLI 管理 Windows Container。映像來源則推薦官方發行的 windowsservercore、nanoserver 兩個 base image，GitHub 上亦有多種範例 Dockerfile 可參考。

最後列舉目前 TP5 的主要痛點：雖整體穩定度已足以評估可行性，但網路功能仍未完整，包括 container linking、內建 DNS、overlay network driver 與多項 DNS 相關參數均尚未支援，使得在 Windows 上部署微服務架構仍需等待正式版或後續 servicing update。作者鼓勵讀者若有其他疑問可於留言區討論，他將持續補充。

## 段落重點
### 前言與動機
作者因工作環境仍以 Legacy ASP.NET WebForm 為主，無法立即遷移至 .NET Core 與 Linux Docker，遂將研究焦點轉向能直接承載現有 Windows 應用的 Windows Container；並在社群演講後發現需求旺盛，決定撰寫 FAQ 補足官方文件不足之處。

### 參考資料
列出官方 FAQ、部署教學與 InfoQ 深度文章，適合已懂 Linux Docker 但對 Windows Container 不熟的讀者先行閱讀。

### Q1. Windows Container 與 Docker for Windows 差異
Windows Container 是 Windows Server 2016 內建的容器引擎，共用 Windows Kernel、執行 Windows App；Docker for Windows 則在 Hyper-V VM 中跑 Linux Docker，引擎仍為 Linux Kernel，執行 Linux App。兩者共享 Docker 生態但應用對象截然不同。

### Q2. 如何啟用 Windows Container
目前僅 Windows Server 2016 (TP5) 與更新後的 Windows 10 Pro/Ent 支援。Server 版本提供 Process 與 Hyper-V 隔離兩模式；Windows 10 只能使用 Hyper-V 隔離。官方文件詳細說明安裝步驟與系統需求。

### Q3. 是否能執行現有 Docker 映像
不能。Windows Container 僅接受 Windows 應用映像，需透過 Dockerfile 重新建構或至 Registry 尋找 Windows 版本映像。

### Q4. Docker Client 是否通用
可以。Docker CLI 與 API 跨平台相容，Linux 版 CLI 也能遙控 Windows Container Engine，管理體驗一致。

### Q5. 映像來源與建置
Microsoft 在 Docker Hub 提供 windowsservercore 與 nanoserver 兩大 base image 及 iis 等延伸映像；GitHub 上亦有官方範例 Dockerfile，可協助開發者快速打包 Windows 應用。唯一缺點是 Hub 上尚無明確標示映像屬於 Linux 或 Windows，需自行辨識。

### Q6. TP5 既有問題與限制
整體穩定度足以進行概念驗證，但網路功能殘缺：container linking、內建 DNS、overlay driver 及多項 DNS/hostname 相關參數均未支援，造成微服務架構布署困難。預計正式版或後續更新才會補齊，開發者需留意此限制。