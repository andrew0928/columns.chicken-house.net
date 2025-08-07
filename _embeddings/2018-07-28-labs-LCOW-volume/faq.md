# 使用 LCOW 掛載 Volume 的效能陷阱

# 問答集 (FAQ, frequently asked questions and answers)

## Q: 在 LCOW 下把 Volume 掛進 Linux Container 做大量檔案 I/O，效能表現如何？
實測以 Jekyll 建站為例，source 放在 Volume、destination 放在 Container（volume → container）時需 135 秒；若全部放在 Container（container → container）只要 12 秒，效能落差超過 10 倍；若 source、destination 都放在 Volume（volume → volume）甚至無法順利完成。

## Q: Docker for Windows 與 LCOW 在純 container → container 的 I/O 效能有差別嗎？
幾乎沒有差別。兩者皆約 12 秒即可完成同一份 Jekyll 專案的 build，顯示在不經過 Volume 時兩種 Engine 的 I/O 效能相當。

## Q: Hyper-V 隔離層級會如何影響 Windows Container 的 I/O 效能？
以 Windows Server 1803 為例，  
1. Process 隔離寫入 Container：1.57 秒  
2. Hyper-V 隔離寫入 Container：5.90 秒（效能下降 3.7 倍）  
3. Hyper-V 隔離寫入 Volume：2.21 秒（僅下降約 35%）  
可見 Hyper-V 主要影響的是 Container 內部磁碟而非掛載的 Volume。

## Q: 為什麼 Docker for Windows 的 Linux Container 寫入 Volume 速度優於 LCOW？
Docker for Windows 透過在 Host 開 SMB Share，把 Windows 磁碟直接掛給唯一的 Linux VM 使用；LCOW 則為每一個 Linux Container 建立獨立 VM，檔案 I/O 需多層轉譯，導致 volume → container 測得 41 秒，而 Docker for Windows 僅 9 秒。

## Q: 在 Azure VM 裝 Hyper-V 再跑 Windows／Linux Container，效能值得參考嗎？
不值得。Nested virtualization 下 I/O 效能嚴重下滑（單次 dd 測試可高達 60 秒以上），不建議在生產環境使用此架構，只適合做相容性或概念驗證實驗。

## Q: 儘管 Volume I/O 效能差，為什麼作者仍推薦開發人員使用 LCOW？
LCOW 讓 Windows Container 與 Linux Container 可同時在同一台 Windows 機器、同一個 Docker Engine 及同一張網路共存，並能寫在同一份 Docker Compose。對需要混用 .NET Framework（Windows）與各式 Linux 服務的開發者而言，部署、測試、CI/CD 都更便利；在開發階段「便利性與一致性」往往比極致 I/O 效能更為重要。