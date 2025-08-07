# LCOW Labs: Linux Container On Windows

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 什麼是 LCOW (Linux Container On Windows)？其運作原理為何？
LCOW 透過 Windows 既有的 Hyper-V Container 機制，為每個 Container 啟動一個精簡 VM，並把原本放在 VM 內的 NanoServer OS 改為 LinuxKit（或 Ubuntu），讓 Windows 能「原生」執行 Linux Container。

## Q: Microsoft 為何要推出 LCOW？它與 WSL 的關係是什麼？
Microsoft 打算以 LCOW 取代 Windows Subsystem for Linux (WSL)。相較於在 Windows Kernel 內轉換 system call 的 WSL，LCOW 架構更精簡、相容性更佳、維護成本更低，且同時支援 Linux Container。

## Q: 若想在目前的預覽階段體驗 LCOW，需要什麼測試環境？
1. Windows 10 Pro Insider Preview 1709 (OS Build 16299.0)  
2. Docker for Windows Edge 17.09.0-ce（內含預設 Docker daemon）  
3. 另外從 GitHub 下載支援 LCOW 的 Docker daemon (master-dockerproject-2017-10-03)  

## Q: 在同一個 Docker daemon 裡可以同時跑 Windows Container 和 LCOW 嗎？
不行。LCOW 版的 Docker daemon 目前只能跑 Linux Container；若要執行 Windows Container，必須切回 Docker for Windows 預設的 Docker daemon。

## Q: 嘗試在 LCOW daemon 裡執行 Windows Container（例如 nanoserver）會發生什麼事？
會失敗並出現錯誤訊息  
“panic: inconsistency - windowsfilter graphdriver should not be used when in LCOW mode”，  
之後 LCOW daemon 也會被迫關閉，需要手動重新啟動。

## Q: 使用 LCOW 跑 Linux Container 的啟動速度大約如何？
在 i7-4785T / 16 GB RAM / 7200 rpm 舊 HDD 的電腦上，執行 hello-world Container 從啟動到結束大約 5 秒鐘即可完成。

## Q: 透過兩個不同 Docker daemon 分別啟動的 Linux 與 Windows Container 網路能互通嗎？
可以。兩邊會取得同一網段的 IP，彼此可直接以 IP 位址互相 ping 通。但因為各自屬於不同 daemon，無法使用 `--link` 或內建 DNS 解析找到對方。

## Q: 為何作者要做這些測試？
為了確認當未來系統架構同時包含 Linux 與 Windows 服務時，是否能在「單一開發機」上同時執行並測試兩種 Container。

## Q: 2017/10 Windows 更新（Fall Update）在 Container 方面還有哪些重點改進？
• NanoServer 基礎映像縮減 70%（約 330 MB → 80 MB）  
• ServerCore 映像也縮小 20% 以上  
• 提供 .NET Core 2.0 與 PowerShell 6.0 的預覽映像  
• Container Volume 新增對 SMB 分享目錄的掛載支援  
• 加強對各種 Orchestrator（包含 Kubernetes）的網路功能  
• 支援 Named pipe mapping、效能提升與 bug 修正