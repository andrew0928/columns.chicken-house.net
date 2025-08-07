# [架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?

## 摘要提示
- StackOverflow架構: 以 .NET 為核心、跨 Windows/Linux 混搭最佳元件展示未來趨勢。  
- Microsoft定位: 從「平台優先」轉向「應用與服務優先」，全面擁抱開源與跨平台。  
- Visual Studio策略: 一套 IDE 打通 UWP、Xamarin、Cordova 及原生 C/C++ 開發。  
- .NET Core: 開源、跨 Windows/Linux/macOS，可同時滿足攻與守的佈署需求。  
- VS Code: 輕量跨平台 IDE，輔以 VS for Mac，形成全家桶。  
- Windows 與容器: Windows Server 2016/Windows 10 原生支援 Docker、Hyper-V Container 與 WSL。  
- Azure: 從單純 .NET 雲轉型為全方位 OSS 雲，提供一鍵佈署樣板。  
- 混搭架構門檻: Docker 與 Container Orchestration 降低安裝、設定與維運痛點。  
- 學習重點: Docker、生態系熱門 OSS 服務（Nginx、Redis…）、及早轉到 .NET Core。  
- 個人轉型: 以最小代價跨入 Linux/OSS 世界，掌握開發、IT、個人職涯三層面。  

## 全文重點
本文以 StackOverflow 2016 架構為例，說明大型 .NET 網站如何透過混搭 Linux 服務（ElasticSearch、Redis、HAProxy）達到效能與擴充性的最佳化。作者指出，隨著 Satya Nadella 上任，Microsoft 從過去封閉的「Windows + .NET」策略，快速轉向「抓住所有開發者」的開源跨平台路線；Visual Studio 支援多種 Bridge 與 Xamarin，.NET Core 開放源碼並可於多平台執行，VS Code、VS for Mac 補足非 Windows 開發空缺，Windows 10/Server 2016 引入 Docker 與 WSL，Azure 亦成為 OSS 友善雲端。  
在此大背景下，純粹的 Windows 技術人員必須調整心態：目標是能自由選用最適合的技術組合，而非被平台綁住。實作上，開發層面應盡快遷移到 .NET Core 以確保佈署彈性；架構層面則採用 Docker 容器化所有服務，再以 Swarm、Mesos、DC/OS 或 Azure Container Service 進行編排，藉此降低安裝、設定與擴充複雜度；個人能力層面則鎖定 Docker、生態系熱門 OSS（Nginx、HAProxy、MySQL、Redis 等）與 Linux 基礎操作，建立跨平台觀念。  
最終，作者以自身半年多的學習經驗提醒 .NET 同溫層的開發者：別再陷入 Windows/Linux 的意識形態之爭，現在正是低門檻擁抱開源、提升職涯競爭力的最佳時機。

## 段落重點
### 引言：StackOverflow 混搭架構的啟示  
作者以 StackOverflow 2016 系統圖為切入，說明其 Web 與 Service Tier 使用 .NET、資料庫採 SQL Server，卻同時在搜尋、快取與負載平衡層大量使用 Linux 與 OSS。此混搭提高了複雜度，但證明在需求驅動下選擇最合適元件的價值，並引出後續「當混搭不再困難」的思考。

### STEP #1 看懂 Microsoft 的定位及策略  
Nadella 上任後，Microsoft 把「留住／吸引開發者」視為首要任務，因此大舉開源、跨平台：.NET Core、VS Family、SQL Server on Linux、Windows 10 WSL、Docker 合作、Azure 全面支援 Linux/OSS。策略核心從「平台優先」轉成「應用與服務優先」，只要開發者使用 MS 產品與雲端即可。

### 用 Visual Studio 開發所有平台的 APP  
透過 UWP + 橋接專案、Xamarin 與 Cordova，VS 能將現有 Android/iOS/WP 專案轉為 UWP，或反向一次開發多平台；最新支援 C/C++ 遠端編譯至 Linux，顯示 VS 企圖成為「唯一」全平台 IDE。

### 用 .NET Core 開發所有平台的 Server Side Application  
.NET Core 自 //Build 2015 起走向完全開源，包含 Runtime、BCL 與編譯器。開發者不必再依賴 Mono 即可於 Linux/macOS 部署 ASP.NET，形成「寫一次、跑任何地方」的伺服器基礎。

### 用 Visual Studio Code 當作所有平台的 IDE 第一選擇  
VS Code 以 Electron 為基礎，跨 Windows/macOS/Linux，並透過擴充套件提供 IntelliSense、偵錯與 Git 整合。雖然僅 1.x 版，但輕量與快速更新讓其成為非 Windows 環境寫 .NET、Node.js、Go 等語言的首選。

### 用 Windows 10 / 2016 當作所有平台的開發環境  
Windows Server 2016 支援 Windows Container；透過 Hyper-V 或未來的 WSL，可同機器同時跑 Linux Container。桌面版 Windows 10 則整合 Docker for Windows 與 Bash on Ubuntu，讓開發與測試流程無縫切換。

### 用 Microsoft Azure 當作所有服務執行的平台  
Azure 現已提供各式 Linux VM 與 OSS 市集樣板，並針對容器推出 Azure Container Service，支援 Swarm、Kubernetes、Mesos。雲端策略由「只給 .NET」轉為「任何技術皆可上 Azure」。

### STEP #2 個人該如何轉變?  
當平台藩籬被拆除，開發者可像 StackOverflow 一樣自由組合最佳解，但同時要面對跨技術維運的門檻。若 Microsoft 的布局成功，這些門檻將被 Docker 與 .NET Core 大幅降低，甚至小團隊、一台伺服器亦能搭建同級架構。

### DEV: 開發架構上的考量 - 盡早轉移到 .NET Core  
C#/Java 最適合大型系統；C# 在 Anders 與 VS 的加持下持續演進。採 .NET Core 可同時享有 Windows 佈署的穩定與 Linux 佈署的彈性，加上 SQL Server on Linux，更能純粹以需求決定平台，不再受政治因素干擾。

### IT: 架構設計上的考量 - 盡早採納容器化的佈署管理方式 (Docker)  
開發與佈署藉容器完全脫鉤：服務封裝為 Image，組合關係交由 Compose 管理，叢集由 Swarm/Mesos/DC-OS 或 Azure 容器服務負責。Windows Containers 雖仍限制多，但方向明確；若使用 Rancher 等平台，負載平衡、Scale Out 更為簡易。

### IDP: 個人的學習及發展計畫 - 趕緊熟悉這一切  
對傳統 .NET 工程師而言，進入 Linux/OSS 生態的最佳捷徑為：1) 熟悉 Docker 操作與基本 Linux 指令；2) 了解常用 OSS 服務的角色與設定範例；3) 將日常專案升級至 .NET Core。如此即可在最短時間內具備跨平台開發、佈署與維運能力。

### 結論  
作者回顧半年來深入 Docker 與 .NET Core 的動機：不是趕潮流，而是看見微軟生態劇變帶來的機會。雖仍是 Linux 菜鳥，但透過容器技術已能有效整合兩派優勢。期望所有 .NET 同好把握時機，跳脫意識形態，擁抱開源混搭以提升未來競爭力。