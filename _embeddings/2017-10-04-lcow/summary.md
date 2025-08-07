# LCOW Labs: Linux Container On Windows

## 摘要提示
- LCOW: Microsoft 以 Hyper-V Container + LinuxKit 讓 Windows 原生執行 Linux Container。
- 取代 WSL: 秋季更新將以 LCOW 取代 WSL，架構更精簡、相容性更高。
- 測試環境: Windows 10 Insider 16299 + Docker for Windows Edge 17.09 + 自行編譯 daemon。
- 多重 Engine: 系統同時存在三套 Docker Engine，需以 ‑H 參數手動切換。
- LAB1 成果: 在 LCOW 下 busybox 與 hello-world 5 秒內啟動完成。
- LAB2 受限: LCOW daemon 仍無法啟動 Windows Container，出現 windowsfilter graphdriver 錯誤。
- LAB3 網路: 不同 daemon 啟動的 Win / Linux 容器可互 Ping，但無 DNS 與 link 功能。
- 效能觀察: i7-4785T + 16 GB RAM + 舊 HDD 仍能維持良好容器啟動速度。
- Insider 新功能: 更小的 NanoServer / ServerCore 映像、SMB Volume、K8s 網路強化等。
- 後續展望: 正式版將簡化 Mixed-OS 開發流程，作者計畫以 docker-compose 進一步驗證。

## 全文重點
本文介紹 Microsoft 最新推出的 LCOW（Linux Container On Windows）技術，以及作者利用 Windows 10 Insider Preview 與 Docker for Windows Edge 版進行的系列實驗。LCOW 透過 Hyper-V Container 把傳統用於 Windows 容器的 NanoServer 映像替換成 LinuxKit，讓 Windows 能「原生」執行 Linux 容器，並計畫在 2017 秋季更新後逐步取代 WSL。  
作者準備了三套互相獨立的 Docker Engine──Docker Desktop 的 Linux engine、Windows engine 以及手動安裝的支援 LCOW daemon，必須用 ‑H 指定 named pipe 才能切換。  
在 LAB1 中，作者成功於 LCOW 模式啟動 busybox 與 hello-world 容器，並以影片展示約 5 秒就能完成 VM 啟動、映像展開及程式執行的流程，證明 LCOW 結合 Hyper-V 仍可維持接近原生容器的速度。  
LAB2 嘗試用同一支 LCOW daemon 啟動 Windows 容器，仍因 graphdriver 相容性問題失敗，顯示目前版本尚不支援「單一 daemon 同時跑 Win / Linux 容器」。  
LAB3 聚焦在網路互通；分別用不同 daemon 起了一個 Windows Server Core 與一個 BusyBox，兩者皆獲得 172.28.x.x 網段 IP，互 Ping 成功，但因為彼此不在同一 daemon 內，無法透過 ‑-link 或內建 DNS 解析互相名稱。  
文章最後整理 Windows Server Insider 16278 帶來的其他容器新功能：NanoServer 映像瘦身 70%、ServerCore 縮小 20%、SMB Volume mount、Kubernetes 網路強化、Named Pipe 映射等，並期待正式版釋出後能在單一開發機實現跨 OS docker-compose 架構。

## 段落重點
### 前言：LCOW 介紹與背景
作者回顧 Microsoft 從 Mixed-OS Docker Swarm 到 LCOW 的推進，說明 LCOW 利用 Hyper-V Container 在每個容器背後動態啟動一個極小化 LinuxKit/Ubuntu VM，讓 Windows 系統得以直接執行 Linux 二進位。與 WSL 需修改 kernel 不同，LCOW 架構更單純且可一併支援完整的 Linux 容器生態系，象徵 Microsoft 打破 Windows / Linux 壁壘的決心。

### 準備測試環境
為趕在 .NET Conf 之前驗證 LCOW，作者採用 Windows 10 Pro Insider Build 16299、Docker for Windows Edge 17.09 與 GitHub 上最新 master-dockerproject daemon。安裝流程主要是下載支援 LCOW 的 dockerd.exe 與對應 LinuxKit 映像，啟動後透過 named pipe `//./pipe/docker_lcow` 存取。完成後，系統同時擁有：1) Docker Desktop 的 Linux engine、2) Docker Desktop 的 Windows engine、3) 支援 LCOW 的獨立 engine，需靠 `docker -H` 切換。

### LAB1：Run BusyBox / Hello-World
首先在 LCOW daemon 裡執行 `busybox sh` 以及 `hello-world` 容器，證明 Windows 在不安裝任何 VM 管理工具的前提下就能直接跑 Linux 指令。作者以 i7-4785T + 16 GB RAM + 傳統 7200rpm HDD 的設備錄影，從命令下達到程式結束僅約 5 秒，足見 Hyper-V + LinuxKit 的啟動成本已大幅降低，帶來近似原生 Docker 體驗。

### LAB2：Run Windows Container with LCOW
接著嘗試在同一支 LCOW daemon 內拉取並啟動 `microsoft/nanoserver`，但下載完成後 daemon 出現 `windowsfilter graphdriver should not be used when in LCOW mode` 並崩潰，需要手動重啟。此實驗說明當前預覽版仍無法同時在一個 daemon 內混跑 Windows 與 Linux 容器，需待後續版本修正。

### LAB3：Networking
為測試跨 OS 容器互聯，作者在預設 Windows daemon 啟動一個 Windows Server Core 容器，在 LCOW daemon 啟動 BusyBox。兩者獲得不同 172.28.x.x IP，可互相 Ping 通，顯示 Hyper-V Switch 能把兩張虛擬交換器橋接。但因 Docker daemon 相互隔離，`docker ps` 彼此看不到對方，也無 ‑-link 與內建 DNS 功能，仍需手動以 IP 溝通。

### 小結與後續
雖然預覽版仍受限於單一 daemon 不能同時跑 Win / Linux 容器，但 LCOW 已展現快速、低門檻的 Linux 執行能力。配合 Insider 16278 的映像瘦身、SMB Volume、Kubernetes 網路等改進，Windows 在容器化領域的落差正迅速縮小。作者期待正式版釋出後，用 docker-compose 實現 NGINX on Linux + ASP.NET on Windows 的混合範例，並呼籲開發者持續關注。