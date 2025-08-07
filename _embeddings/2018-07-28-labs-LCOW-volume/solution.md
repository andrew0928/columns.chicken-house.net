# 使用 LCOW 掛載 Volume 的效能陷阱

# 問題／解決方案 (Problem/Solution)

## Problem: 透過 LCOW 掛載 Volume 時，Jekyll Build 耗時大增 (135 s vs 12 s)

**Problem**:  
在 Windows 環境中，開發者希望同時執行 Windows 與 Linux Container，所以改用 LCOW (Linux Container on Windows)。當用 Jekyll Docker Image 進行網站編譯時，只要 Source 或 Destination 透過 Volume 掛載到 Host，整體編譯時間會從 12 秒暴增到 135 秒以上，開發週期被嚴重拖慢。

**Root Cause**:  
1. LCOW 會為每一個 Linux Container 啟動獨立的 LinuxKit VM，Volume I/O 需要跨越  
   Host Windows → Hyper-V → LinuxKit → Container 四層。  
2. Volume 對應到 VHDX，以 9P / CIFS 等機制轉譯，再加上 AUFS/overlayfs，自然產生高 I/O latency。  
3. Jekyll Build 需大量小檔案寫入、修改，放大了 metadata 與 file-lock 交換頻率，造成效能雪崩。

**Solution**:  
1. 盡量採用「container → container」路徑：  
   ```bash
   docker run --rm -v (無) jekyll/jekyll:2.4.0 \
     jekyll build -s /tmp/source -d /tmp/site
   ```  
   • Source 及 Destination 都落在 Container Layer，避免跨 VM/Host I/O。  
2. 若必須保留 Volume，僅將 Source 置於 Volume，Destination 落在 Container；編譯後再用 `docker cp` 或 CI 步驟回傳產物。  
3. 重 I/O 工作可改回 Docker for Windows (共用單一 MobyLinux VM) 或直接使用 WSL / 原生 Linux；LCOW 僅用於需要 Windows+Linux 混跑與功能驗證。

**Cases 1**:  
LAB1 實測  
• LCOW container→container：12.86 s  
• LCOW volume→container：135.49 s  
同一套程式碼，透過調整儲存路徑即可將 Build 時間縮短 10 倍以上。

---

## Problem: LCOW Volume→Volume 連續大量寫入會隨機出現 “Operation not permitted” 錯誤

**Problem**:  
使用 LCOW 時，將 Source 與 Destination 都掛在 Volume；Jekyll Build 進行到一半便隨機噴出 `Operation not permitted @ apply2files` 導致編譯中斷，無法穩定重現成果。

**Root Cause**:  
1. LinuxKit 的 9P / SMB 對同一 Volume 雙向大量 I/O 存在競態 (file-lock / rename)。  
2. Volume ↔ LinuxKit ↔ Container 三層的 inode / lock 同步延遲，造成 random access 出錯。  
3. 驅動尚未針對 heavy parallel write 做完整測試，屬於 LCOW 仍在預覽的既知缺陷。

**Solution**:  
1. 避免 Volume→Volume，將至少一端 (建議 Destination) 改回 Container 路徑。  
2. 或者改用 Docker for Windows / 原生 Linux 進行大量檔案產生，再將結果透過 CI 發佈。  
3. 等待 LCOW 更新 (LinuxKit FS Driver) 或直接回報 Issue 追蹤修補。

**Cases 1**:  
LAB1 測試 #1  
• 同一 Image 在 Docker for Windows 可完成 (120 s)  
• LCOW 在 68 s–70 s 隨機失敗，顯示 Volume 雙向寫入不穩定。

---

## Problem: Hyper-V Isolation 與 Cross-OS Volume I/O 效能下降 3–13 倍

**Problem**:  
在 Windows Server/Windows 10 上選擇 Hyper-V Isolation (含 LCOW) 後，即便是單純 `dd` 連續寫入測試也呈現數倍效能差異。例如 Windows Container (process) 寫入 1 GB 只需 1.6 s，但切換到 Hyper-V Isolation 卻需要 5.9 s；LCOW 寫入 Volume 則衰退到 21–41 s。

**Root Cause**:  
1. Hyper-V Isolation 必須建立迷你 VM，I/O 經過 VirtIO / VMBus，叢集 context-switch 激增。  
2. Windows ↔ LinuxKit ↔ AUFS 三層 filesystem 轉換 (NTFS → ext4/overlay) 未做直通優化。  
3. 雲端 VM 再開 Hyper-V (Nested Virtualization) 更增加 L2 TLB miss 及 Storage Network latency。

**Solution**:  
1. Production/CI: 儘量使用「process isolation」，只在極端安全需求才用 Hyper-V。  
2. Kubernetes / Swarm 部署：利用 Node Label 把 Windows Container 派到 Windows Node、Linux Container 派到 Linux Node，完全避免 Nested + Hyper-V 疊加。  
3. 開發環境：  
   • 用 LCOW 方便地同時起 Windows+Linux 容器驗證邏輯與網路整合。  
   • I/O 密集工作放到 Docker for Windows 或 WSL/原生 Linux 處理，再把成果 mount 回 Windows。  
4. 若必需 Hyper-V Isolation，可考慮持久化資料走獨立網路儲存 (e.g. NFS/Samba)，降低 VM 內部 overlay 負載。

**Cases 1** (Windows Server 1803, 實體):  
• process → container：1.57 s  
• hyper-v → container：5.90 s (↑276 %)  

**Cases 2** (Windows 10 Pro + Docker for Windows):  
• LCOW → volume：41.14 s  
• Docker for Windows → volume：9.10 s (同樣 Hyper-V 但共用單 VM，效能僅劣化 3×)

**Cases 3** (Azure DS4v3, Nested Hyper-V):  
• hyper-v → container：66.82 s  
• hyper-v → volume：3.39 s  
Nested 架構導致 container-layer I/O 失衡，證實不適合 Production。

---
