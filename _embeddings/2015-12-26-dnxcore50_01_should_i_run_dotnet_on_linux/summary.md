# .NET Core 跨平台 #1, 我真的需要在 Linux 上跑 .NET 嗎?

## 摘要提示
- 跨平台價值: .NET Core 使現有 .NET 資源能在 Linux 上獲得官方支援，消弭 Windows／Linux 隔閡。  
- Open Source 助益: 開源讓社群能即時修補 Bug、閱讀原始碼、提升生態系整合度。  
- 部署彈性: 可在 Linux 佈署 ASP.NET 服務，與 Apache／Nginx、Docker 等工具自然整合。  
- 眼前優點: 沿用 BCL、Visual Studio、既有 C# 程式碼，降低學習與轉移成本。  
- 長遠優點: 搶佔雲端與 OSS 市佔率，強化 Azure 競爭力，與 Java 分庭抗禮。  
- 工具優勢: C# 語言設計精良，搭配 Visual Studio 形成難以取代的開發體驗。  
- 架構演進: OWIN 出現，讓 ASP.NET 5 可脫離 IIS 直接掛載在主流 Web Server。  
- 雲端趨勢: Linux 為雲端主力，微軟必須提供跨平台解決方案以留住 .NET 開發者。  
- 效能探索: 作者將透過記憶體管理與圓周率多執行緒運算，比較不同平台效能。  
- 投資時機: 雖短期誘因不足，但為未來十年技能布局，值得現在就投入學習。  

## 全文重點
作者回應「為何要在 Linux 跑 .NET」的疑問，指出 .NET Core 雖仍處起步階段，但其跨平台、開源與官方支援特性，帶來立即與長遠的雙重收益。立即面向包括：既有 .NET 程式碼與工具可直接移轉、能借力龐大的開源社群快速修復與創新、以及正式取得在非 Windows 系統執行的合法性，進一步與 Apache、Nginx、Docker 等 OSS 組件無縫整合。長期而言，微軟藉由開源 .NET 增強在雲端與 OSS 世界的影響力，鞏固 Azure 業務並與 Java 競爭；加上 C# 與 Visual Studio 的優勢，足以持續吸引開發者。作者認為，過往 Windows／Linux 的二分選擇導致許多專案無法採用 .NET，如今跨平台將消弭此障礙，並促成 OWIN 等架構革新。雖短期企業仍以 Windows Server／IIS 為主，但從個人職涯及技術演化角度看，提早熟悉 .NET Core、Docker 與 Linux 相當重要。為驗證跨平台差異，作者計畫以記憶體碎片化與多執行緒計算 π 值兩個實驗，比較 Linux Docker、Windows Container 及傳統 Windows Server 環境之效能差異，後續文章將詳述結果。

## 段落重點
### 緒論：為何在 Linux 跑 .NET？
作者回顧 .NET Core 仍處 RC 階段，功能與完整 .NET Framework 相比仍有限，現階段缺乏立即遷移誘因。然而他強調放眼長期，投資 .NET Core 跨平台是值得的。核心理由在於：同時保有 .NET 生態成熟度及跨平台彈性，並能與開源世界互補。作者以自己追蹤 SMTP 編碼 Bug 的經驗說明，開源能縮短修補周期、提升問題透明度。

### 投資在 .NET Core + Linux 眼前的好處
1) 沿用全部 .NET 開發資源：BCL、Visual Studio 及累積的 C# 程式碼皆可復用；2) 借力開源社群：Bug 能被快速發現與提交 PR 修復，開發者可直接閱讀原始碼；3) 官方跨平台保證：.NET 應用能「名正言順」部署於 Linux，與其他 OSS 組件同屬原生環境，避免 Windows／Linux 雙棧帶來的維運複雜度。作者舉 IIS 與 Apache／Nginx 共存的歷史窘境，說明單一平台所帶來的技術及成本優勢。OWIN 的出現，亦使 ASP.NET 5 可在主流 Web Server 上運行，解決過去開發與部署環境差異的痛點。

### 投資在 .NET Core + Linux 長遠的好處
微軟開源 .NET 的兩大戰略動機：其一，在以 Linux 為大宗的雲端與 OSS 生態中維持 .NET 的市佔與開發者黏著度，與 Java 競爭；其二，促進 Azure 業務成長，因雲端客戶多採 Linux，微軟需提供更緊密的跨平台支援以增強黏著。C# 語言與 Visual Studio 仍居開發效率與體驗之首，但以往授權成本阻礙了大規模部署；開源及跨平台策略可望逐步扭轉。雖短期企業現況未變，作者看好在 Satya Nadella 領導下微軟重新贏得開發者信任，顯示出與 Bill Gates 時期相似的技術導向精神。

### 回到主題，了解 .NET Core 在不同平台上的表現
為評估跨平台的實際差異，作者計畫重用早年撰寫的測試程式，從「記憶體碎片化」與「多執行緒計算圓周率」兩面向，比對 .NET Core 在 Linux Docker、Windows 2016 Container 與 Windows 2012 R2 環境的資源使用與效能。前者延續其 20 年來對 virtual memory 行為的研究，後者測試 50,000 位 π 值運算，觀察 OS 與執行階段對速度的影響。後續兩篇文章將詳述實驗過程與結果，作為本系列的實證補充。