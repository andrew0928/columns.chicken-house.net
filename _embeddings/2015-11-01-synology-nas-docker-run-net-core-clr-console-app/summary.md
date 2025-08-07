# 同場加映: 用 Synology NAS 的 Docker 環境，執行 .NET Core CLR Console App

## 摘要提示
- Synology NAS Docker: 利用 NAS 內建的 Docker 套件，省去自行安裝 Linux 與 Docker 的繁瑣流程。
- VS2015 Core CLR 專案: 以「Console Application (Package)」建立 DNX Core 5.0 專案並編譯輸出。
- microsoft/aspnet 映像: 透過 NAS Docker Registry 下載 1.0.0-beta8-coreclr 映像，大小約 350 MB。
- 容器目錄掛載: 將 NAS 的 /docker/netcore 掛載到容器 /home 以便快速複製編譯檔案。
- dnu restore: 進入容器後先還原相依套件，確保執行環境完整。
- dnx 啟動: 以 dnx HelloCoreCLR.dll 執行主程式，成功輸出「Hello World」。
- 記憶體佔用: .NET Core 容器僅佔約 6 MB RAM，極度精簡。
- 適用機種: Docker 只支援 Intel CPU 的特定 Synology 型號，購買前務必查清單。
- 整體流程: 開發端 Windows、部署端 NAS，一條龍完成跨平台驗證。
- 採購建議: 若主要目的是測試 Docker/.NET Core，可考慮入手支援 Docker 的 NAS，省時省力。

## 全文重點
作者在前一篇文章說明了如何手動在 Linux 上部署 .NET Core，這篇改採 Synology NAS 內建的 Docker 套件示範同一流程。首先於 Visual Studio 2015 建立支援 Core CLR 的 Console Application (Package) 專案，切換執行環境為 DNX Core 5.0，寫入簡單的「Hello World」程式後編譯，並在 artifacts/bin 目錄取得輸出檔案。接著於 NAS 套件中心安裝 Docker，從 Registry 下載 microsoft/aspnet:1.0.0-beta8-coreclr 映像。啟動容器時命名為 NetCoreCLR，於「Advanced Settings」將 NAS 端 /docker/netcore 掛載到容器 /home，並將剛剛編譯的檔案複製到該目錄。容器啟動後透過 DSM 介面開啟 Terminal，切至 /home/ 目錄，執行 dnu restore 下載相依套件，再以 dnx HelloCoreCLR.dll 執行程式，即可在 NAS-Docker 環境中看到預期輸出。整個容器的記憶體佔用僅約 6 MB，相較於完整 VM 十分輕巧。最後作者提醒，並非所有 Synology 型號皆支援 Docker，目前僅限採用 Intel CPU 的中高階機種；若讀者打算為 Docker 或 .NET Core 測試添購 NAS，務必先檢查官方支援清單。

## 段落重點
### 開發環境準備: Core CLR 版「Hello World!」
在 Windows 的 Visual Studio 2015 中，以「Console Application (Package)」類型建立名為 HelloCoreCLR 的專案，明確選擇 DNX Core 5.0 執行環境，程式碼僅印出「Hello World」。於專案屬性勾選「Produce outputs on build」後建置，編譯成果會出現在 solution/artifacts/bin 之下，檔案結構與過去 .NET Framework 不同，但已包含執行所需的 dll 與 json 設定檔。此步驟完成的重點在於取得可攜式、跨平台的 .NET Core 執行檔，後續可直接搬移至任何支援的 Docker 容器。

### 事前準備: NAS + Docker
首先在 Synology 套件中心安裝官方 Docker 套件；QNAP 等其他品牌需另尋對應方案。打開 Docker 介面後，到 Registry 以 microsoft/aspnet 為關鍵字搜尋，並選擇 tag 1.0.0-beta8-coreclr 下載映像，容量約 350 MB。下載完成時 DSM 會推播通知，此階段即等同於在傳統命令列執行 docker pull。整個過程透過 GUI 進行，對不熟 Linux 的使用者而言大幅降低門檻。

### 佈署與執行
在 Docker UI 點選剛下載的映像並 Launch，將容器命名為 NetCoreCLR。資源限制可保持預設，接著進入 Advanced Settings 把 NAS 端 /docker/netcore 掛到容器 /home，並取消唯讀限制，以利傳送程式檔案。完成設定後 Apply 即可產生並啟動容器，接著將 VS 編譯輸出複製進 NAS 的對應資料夾。於容器 Details 內開啟 Terminal，切換至 /home，先執行 dnu restore 下載缺少的 NuGet 套件；完成後以 dnx HelloCoreCLR.dll 執行程式，可看到終端機列印「Hello World」。檢視 DSM 的資源監控，整個 .NET Core 容器僅耗用約 6 MB RAM，證明 Core CLR 的精簡優勢。文章最後列出官方支援 Docker 的 Synology 型號，提醒讀者購買前先確認 CPU 為 Intel 且機種在清單內，以免無法安裝 Docker。