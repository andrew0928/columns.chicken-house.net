# [架構師觀點] .NET 開發人員該如何看待 Open Source Solutions?

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Microsoft 在 Satya Nadella 時代，對開發者最核心的策略定位是什麼？
Microsoft 希望「抓住所有開發者」，無論使用何種平台，都能在 Microsoft 的工具與雲端服務上完成開發、佈署與營運。從 .NET Core 開放原始碼、跨 Windows／Linux／macOS 執行，到 Visual Studio/Visual Studio Code 跨平台，再到 Azure 提供完整 Windows 與 Linux 工作負載，都是為了落實「Mobile (Applications & Services) First, Cloud (Applications & Services) First」的目標。

## Q: 為什麼作者建議 .NET 開發者要儘早轉移到 .NET Core？
1. .NET Core 天生跨平台，可在 Windows、Linux、macOS 以及 Docker Container 上執行，讓佈署選項更有彈性。  
2. 維持 C#／Visual Studio 生態系優勢，卻能同時享有開放原始碼的快速演進。  
3. SQL Server 也將有 Linux 版本，整體解決方案不再受限於「只能跑在 Windows」的政治或成本考量。

## Q: 為何要優先導入容器化 (Docker) 的佈署管理方式？
Docker 把「開發」與「佈署」徹底脫鉤，只要把服務包成 Container：  
• 開發端不必再為環境差異煩惱。  
• IT 可用 Docker Swarm、Compose，甚至 Mesos／DC/OS 或 Azure Container Service，快速建立從幾台到上萬台的 Cluster。  
• 任何時候需要擴充、縮減或搬遷服務，只要操作 Container 即可，大幅降低維運與擴充門檻。

## Q: .NET 陣營開發者若要迎向「混搭架構」的未來，應優先學哪些關鍵技術？
1. Docker 容器技術（不論在 Windows、macOS 或 Linux 上）。  
2. 主流 Open Source 元件：Nginx、HAProxy、MySQL、Redis…等。  
3. .NET Core 與相關跨平台開發／測試／CI 流程。

## Q: StackOverflow 架構示例中，.NET 與 Open Source 服務是如何混搭的？
StackOverflow 的 Web 與 Service Tier 以 .NET/C# 為核心，資料庫用 SQL Server，但同時在 Linux Server 上運行 ElasticSearch（搜尋）、Redis（快取）與 HAProxy（負載平衡），藉此挑選「各領域最適合的元件」來組合整體服務。

## Q: 作者如何回答「這種混搭真的適合我們嗎？困難點在哪裡？」  
在傳統環境下，開發、維運與測試要同時理解 Windows 和 Linux，確實複雜且門檻高；但若採用 .NET Core + Docker：  
• 開發仍可維持 C#／Visual Studio 的生產力。  
• 維運端僅需面對 Container 編排，無須深入每一套 Linux 軟體的安裝細節。  
• 規模大小彈性，從單機到大型 Cluster 都能以同一套方式處理；因此「混搭」的難度大幅降低，可視實際需求自由取捨。