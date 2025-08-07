```markdown
# 專為 Windows 量身訂做的 Docker for Windows (Beta) !

## 摘要提示
- Beta Program: Docker 於三歲生日推出 Mac/Windows 原生 Beta，作者終於拿到測試 Token。
- Hyper-V 整合: Windows 版全面改採 Hyper-V，免除 VirtualBox 與系統獨佔性衝突。
- Alpine Linux: Boot2Docker 被替換成 Alpine Linux＋Busybox，啟動速度與資源占用更優。
- 原生 UI: 內建設定與自動更新介面，Docker Engine/VM 由同一服務管理。
- Nested Hyper-V: 文章示範在實體 PC→Win10 VM→MobyLinuxVM 的三層巢狀虛擬化。
- 安裝流程: 透過 MSI 套件＋Beta Token 一鍵安裝，未啟用 Hyper-V 會自動補裝並重開機。
- CLI 體驗: 可直接在 Windows Shell 執行 docker 指令，免再 SSH 進 Linux VM。
- Volume Mount: 新增 Share Drives 勾選機制，本機磁碟可快速掛載至 Container。
- 隔離技術: Docker CLI 已內建 --isolation 參數，可在未來選擇 process 與 hyperv 兩級隔離。
- DevOps 意義: 原生整合大幅降低桌面端學習成本，為 Windows Container 及跨架構部署鋪路。

## 全文重點
本文介紹 Docker for Windows Beta 的新功能與實測心得。過去在 Windows 上必須依靠 Docker Toolbox 與 VirtualBox，體驗不佳且與 Hyper-V 互斥；新版改以 Hyper-V 執行 MobyLinuxVM，並把 Boot2Docker ISO 換成更輕量的 Alpine Linux。安裝採原生 MSI，第一次執行若偵測不到 Hyper-V 會自動啟用並重開機；安裝完畢後，Docker 服務會自動建立並管理 VM，並提供圖形化設定介面，包含 CPU/RAM 調整與磁碟分享。
作者為避免在工作機安裝 Beta，示範了巢狀虛擬化：於實體 PC 開一台 Windows 10 VM，再在其內啟動 MobyLinuxVM。啟用 Nested Hyper-V 需使用 PowerShell，且必須關閉動態記憶體、啟用 MAC Spoofing、確保宿主與客體皆為最新 Hyper-V 版本。完成後即可在 VM 內安裝 Docker for Windows、輸入 Beta Token，並透過 Windows Shell 直接執行 docker 指令。
測試包含兩部份：1) 執行 hello-world 容器驗證基本功能；2) 透過 Share Drives 將本機目錄掛載到容器，證實讀寫可互通。雖然其底層仍以 Windows 共享資料夾繞行，但流程大幅簡化。最後作者探討 Windows Container 的隔離層級，指出 Docker CLI 已支援 --isolation=hyperv，顯示與 Microsoft 深度合作，未來可在同一套工具鏈下同時管理 Linux 與 Windows Container。整體而言，Beta 版大幅提升 Windows 桌面開發者的使用體驗，並為後續 DevOps 流程、跨架構映像及 Windows Server 2016 容器化奠定基礎。

## 段落重點
### Docker for Windows Beta, 操作體驗大躍進!
作者概述新版帶來的五大官方改進：Hyper-V 取代 VirtualBox、原生應用與自動更新、可與 Toolbox 並存、快速且正確的 Volume Mount、預設支援 x86/ARM 多架構。同時點出實務感受：安裝不再需要手動改 VM、Boot2Docker 改為 Alpine Linux、整合性與啟動速度明顯提升；對 DevOps 流程而言，能在主流桌面 OS 直接體驗 Docker 為推廣帶來巨大助力。作者亦肯定 Docker 透過併購與社群建立完整生態系的策略。

### Tips: 如何在 VM 裡面體驗 Docker for Windows?
為避免 Beta 軟體影響日常工作，作者決定在 VM 內再跑 Docker for Windows，形成三層架構：實體機→Win10 VM→MobyLinuxVM。文中先以示意圖說明層級，並提醒讀者須先完成 Nested Hyper-V 的設定，否則 MobyLinuxVM 將無法啟動。

### STEP #1 準備好支援 Nested Hyper-V 的 VM
詳細說明啟用巢狀虛擬化流程：宿主與第一層 VM 需為 Windows 10 Pro/Ent 或 Server 2016 Build 10565 以上；使用 PowerShell Enable-VmProcessor 指令開啟 ExposeVirtualizationExtensions，並關閉動態記憶體。列舉官方限制（Intel VT-x、不可套用檢查點、需 4 GB 記憶體等），並附上作者實際 VM 配置截圖供參考。

### STEP #2 在 VM 內安裝設定 Docker for Windows Beta
步驟包含：下載 MSI、執行安裝精靈、首次啟動時若未啟用 Hyper-V 會自動安裝並重開機；輸入 Beta Token 後 Docker 服務會建立 MobyLinuxVM。若 Nested 設定錯誤則 VM 會啟動失敗，作者建議以在 Win10 VM 手動新建一台測試 VM 驗證。安裝完成後，系統托盤出現 Docker 圖示，可透過 Settings UI 調整 VM 資源。

### STEP #3 執行 Docker Container: Hello-World
在 Win10 VM 的 CMD/PowerShell 直接執行 `docker run --rm hello-world`，成功拉取映像並輸出歡迎訊息，證實三層虛擬化架構可正常運作。相較舊流程無須 SSH 進 Linux，再次體現原生 CLI 的便利。

### STEP #4 掛載 Windows Folder, 給 Container 使用
介紹 Share Drives 介面：勾選欲共享磁碟後，Docker 會於 Windows 建立網路分享。作者以 Alpine Linux 容器示範，未勾選時資料夾雖可掛載但宿主看不到變動；啟用共享後即可雙向讀寫，證實新 Volume Driver 有效解決以往需經 Samba/CIFS 的窘境。

### 後記: Container Isolation Technology
探討 Windows Container 的未來方向。Docker CLI 已加入 `--isolation` 參數，可在 Windows 容器選擇 process 或 hyperv 隔離。引用 MSDN 文件說明 Hyper-V Container 透過輕量 VM 提供 kernel 隔離，並展示 `docker run --isolation=hyperv` 範例，顯示 Docker 與 Microsoft 在容器安全層面的合作成果。

### 總結
文章強調 Beta 版已解決 Windows 桌面開發者長久以來的痛點：與 Hyper-V 衝突、Volume 掛載困難、指令不直觀等；透過原生整合與巢狀虛擬化，即使在測試環境也能放心體驗。隨著 Windows Server 2016 與 Windows Container 的成熟，Docker 與微軟的深度合作將使跨平台 DevOps 更趨一致，開發團隊應及早投入學習，以把握未來生產環境的容器化趨勢。
```
