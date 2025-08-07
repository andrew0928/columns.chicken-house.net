# 專為 Windows 量身訂做的 Docker for Windows (Beta) !

# 問答集 (FAQ, frequently asked questions and answers)

## Q: Docker for Windows (Beta) 與過去的 Docker Toolbox 最大的差異是什麼？
Docker for Windows (Beta) 捨棄了 VirtualBox，改採 Windows 10 內建的 Hyper-V 來承載 Alpine Linux + Docker Engine，屬於「原生」應用程式；整合度、速度與穩定度都比 Docker Toolbox 好，並提供自動更新、Volume 掛載加速、跨架構（x86/ARM）建構等功能。

## Q: 為什麼作者認為改用 Hyper-V 意義重大？
Hyper-V 與其他 Hypervisor（如 VirtualBox）屬獨佔關係，過去如果主機已啟用 Hyper-V 就無法再用 VirtualBox 來跑 Docker；新版直接使用 Hyper-V 省去手動改造，讓 Windows 開發者可以無縫體驗 Docker。

## Q: 可以在「VM 裡」再安裝 Docker for Windows 嗎？需要什麼條件？
可以，只要透過 Nested Hyper-V。條件包含：
1. 內外兩層 OS 都必須是 Windows 10 Pro/Enterprise (build 10565/10586 以上) 或 Windows Server 2016。
2. 外層 VM 必須先以 PowerShell 啟用 Nested Virtualization。
3. VM 需關閉 Dynamic Memory、啟用 MAC Spoofing，並至少配置 4 GB RAM。
4. 目前僅支援 Intel VT-x 處理器。

## Q: Nested Hyper-V 啟用後有哪些限制？
• Dynamic Memory 與即時調整記憶體將失效。  
• 套用 Checkpoint、Save/Restore、Live Migration 會失敗。  
• 僅能在最新 Hyper-V 上運作，且僅支援 Intel VT-x。  

## Q: 安裝 Docker for Windows 時若未先啟用 Hyper-V 會怎樣？
第一次啟動程式會跳出提示「Install & Restart」，自動幫你安裝 Hyper-V 並重新開機；若 Nested Hyper-V 未正確設定，內建的 MobyLinuxVM 將無法啟動並顯示錯誤訊息。

## Q: 如何在 Docker for Windows 內掛載本機資料夾給 Container？
1. 在 Docker 設定畫面勾選 Settings → Shared Drives，勾選要分享的磁碟機（C:\、D:\…）。  
2. 於 `docker run` 使用 `-v <windows_path>:<container_path>` 參數，例如  
   `docker run -it -v C:\code:/src alpine /bin/ash`  
   即可在容器內透過 /src 存取 Windows 本機 C:\code 的檔案。

## Q: 若未勾選 Shared Drives 就直接 `-v` 掛載會發生什麼事？
指令不會報錯，但容器收到的其實是 Docker 引擎另外建立的一塊匿名 Volume，本機資料夾與容器路徑不會同步。

## Q: 如何驗證 Docker for Windows 已可正常運作？
在 Windows 的 Cmd/PowerShell 直接執行  
`docker run --rm hello-world`  
若能正確印出 hello-world 訊息，代表多層 VM 與 Docker CLI 均已串通完成。

## Q: Windows Container 支援哪些隔離層級？如何切換？
Docker CLI 的 `--isolation` 參數提供  
• default：依 Daemon 設定；  
• process：僅用 namespace 隔離；  
• hyperv：啟用 Hyper-V Container（Kernel 隔離）。  
在 Windows 執行 Hyper-V Container 範例：  
`docker run -it --isolation=hyperv nanoserver cmd`

## Q: Docker 與 Microsoft 的密切合作對開發者有何意義？
1. Windows Container 將與 Docker 架構、工具及 API 高度相容。  
2. 開發、打包、部署流程可沿用現有 Docker 生態系。  
3. Docker Hub 已支援 Windows Container 映像，未來跨平台部署更一致。

## Q: 未來 Docker for Windows 還會加入哪些支援？
官方已預告將補完 Windows 端的多架構（x86/ARM）建構/執行能力，並持續強化與 Windows Container、Hyper-V Container 的整合。