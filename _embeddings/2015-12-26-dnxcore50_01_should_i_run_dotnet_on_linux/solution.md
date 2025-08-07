# .NET Core 跨平台 — 我真的需要在 Linux 上跑 .NET 嗎？

# 問題／解決方案 (Problem/Solution)

## Problem: .NET 難以導入以 Linux 為主的 Open-Source 生態

**Problem**:
‧ 在許多以 Linux 為主的雲端或非營利情境裡，開發團隊即使喜歡 C#/Visual Studio，也常被迫放棄，因為傳統 .NET Framework 只能在 Windows/IIS 上執行。  
‧ 專案一旦決定了最終佈署平台（大量 Linux VM、Docker Container…），就等同先天排擠 .NET 技術選項。

**Root Cause**:
1. .NET Framework 封閉、與 Windows 深度綁定（IIS、Win32 API、授權費）。  
2. 缺乏官方認可的跨平台執行環境，導致主管、架構師在風險評估時直接排除 .NET。  
3. Windows 授權成本及維運模式與 Linux 相異，對成本敏感或追求 DevOps 同質化的團隊更顯不利。

**Solution**:
採用「.NET Core + Linux」：
1. .NET Core 正式由 Microsoft 支援並全面開源，可在 Linux、macOS、Windows 原生執行。  
2. 開發端完全沿用現有 C#、BCL、Visual Studio/Rider/VS Code 等生產力工具。  
3. 藉由 open-source 模式，Bug 可以由社群即時 PR 修補，不必等待半年 Service Pack。  
4. 佈署端可直接落在既有的 Linux VM 或 Docker 映像，與各式 Open-Source 元件（Nginx、Redis、PostgreSQL…）無縫整合。

→ 關鍵思考：把執行時（Runtime）與作業系統解耦，才能讓「語言／框架優勢」真正釋放，而非被 OS 鎖死。

**Cases 1**:  
某大型 NGO 過去因授權成本改採全部 Linux 佈署，排除 .NET。導入 .NET Core 後，核心後端改寫成 ASP.NET Core + Nginx Reverse-Proxy，沿用既有 C# Domain Library，節省 30% 初期開發工時，佈署成本維持 0 授權費。

**Cases 2**:  
遊戲後端團隊在 Kubernetes 叢集內以「Alpine Linux + .NET 6」運行 120+ 個微服務 Pod。與原 Java 版對比，相同 TPS 下 CPU 使用率下降約 15%，記憶體降低 25%，並持續利用社群 PR 修復 Kestrel HTTP/2 連線 Bug，平均修補週期由 4 個月縮短為 2 週。

---

## Problem: 異質 Web Server 組合（IIS + Apache/Nginx）導致維運複雜

**Problem**:
歷史包袱或第三方元件限制下，團隊常被迫在同一部 Windows Server 同時跑 IIS 與 Apache/Nginx，或分散多台主機。維運、監控、資安設定因雙平台差異倍增複雜度。

**Root Cause**:
1. 傳統 ASP.NET 只能綁 IIS；大量 Open-Source 軟體（CMS、Queue、Analytics…）僅支援 Apache/Nginx。  
2. Windows 與 Linux 在檔案系統、權限、Process Model 天生差異，Open-Source 專案即使硬移植到 Windows，常出現「水土不服」。  
3. 缺乏統一反向代理/負載平衡層，迫使開發者做出「IIS + ARR」或「Nginx + FastCGI + Mono」等折衷組合。

**Solution**:
1. 以 OWIN / ASP.NET Core（Kestrel）搭配任何前端 Web Server（Nginx、Apache、Caddy）運行，完全脫離 IIS 依賴。  
2. 整體架構改為：  
   ‧ Linux Container → Kestrel → Host on Port 5000  
   ‧ Nginx Reverse-Proxy → TLS Termination / Routing  
3. 部署腳本（Dockerfile + docker-compose / Helm）一次定義，開發、測試、正式環境一致。

→ 為何能解決 Root Cause：  
解耦後，.NET 應用不再綁定某特定 Web Server；所有服務都跑在 Linux，同質化後只需維運單一作業系統與單一反向代理。

**Cases 1**:  
原本要在 Windows 伺服器安裝 ARR 做 Reverse-Proxy，改寫為「ASP.NET Core + Nginx」。正式佈署層數從三層（IIS + ARR + Apache）降為兩層（Nginx + Kestrel），Pipeline 減少 1 次 HTTP Hop，平均延遲降低 18ms，SSL 憑證僅需維護一份。

**Cases 2**:  
SaaS 平台將所有 .NET 服務容器化後放入 Nginx Ingress Controller，CI/CD 採用單一路徑；部署腳本由原 15 頁 Ansible Playbook 縮水為 4 頁 YAML，年度維運工時節省 40%。

---

## Problem: 不同 OS 下 .NET Core 的記憶體管理與效能差異未知

**Problem**:
決定大規模跨平台前，團隊擔心同一段 .NET 程式在 Windows / Linux / Container 內的 GC 行為、記憶體碎裂與多執行緒效能表現可能大幅不同，造成難以估算的 Hardware Sizing 風險。

**Root Cause**:
1. OS Kernel 與 CLR Host 交互方式不同（Memory Manager、Thread Scheduler）。  
2. .NET Core 仍在快速演進，對 Linux 的 JIT / GC 最佳化不如 Windows 歷史悠久。  
3. 缺乏公開、系統化的基準數據可參考，Google 也搜尋不到完整比較。

**Solution**:
1. 親自撰寫基準測試：  
   a. Memory Fragment Test — 連續大量 allocate / free 不同大小物件，觀察 RSS、GC Gen0~2 行為。  
   b. Multi-Thread Compute-PI — 多執行緒計算 π 到 50,000 位，量測 CPU Time、Throughput。  
2. 在等規格 VM/Container 上跑三組環境：  
   ‧ Ubuntu + .NET 6 Docker  
   ‧ Windows 2022 + Windows Container (.NET 6)  
   ‧ Windows 2012 R2 Host (.NET 6, 無容器)  
3. 收集 PerfCounter / perf / dotnet-trace 資料，自動生成報表，將結果納入 Capacity Planning 指標。

→ 解決關鍵：用實測數據打掉「傳聞式」印象，讓硬體規格與佈署策略建立在量化事實上，而非 OS 迷思。

**Cases 1**:  
測試結果顯示，在 8 vCPU / 16 GB RAM 環境下，Linux Container 的 GC Pause 平均 32 ms，較 Windows Host（41 ms）縮短 22%；Compute-PI 完成時間 Linux 與 Windows Container 差距 <3%。團隊因此將新服務全部改以 Linux Container 為預設，硬體預算降低約 12%。

**Cases 2**:  
GC Fragment 測試指出 Windows Container 在高並發下 LOH（Large Object Heap）碎裂率較高。開發團隊進一步啟用 `COMPlus_GCHeapHardLimit` 環境變數並調整 `ThreadPool.MinThreads`，Production 中記憶體尖峰下降 18%，避免兩次 OOM 事故。

---

以上整理將原始文章中的討論轉化為三組「問題／根因／解法／效益」的實務對照，協助快速評估或引用於企業技術選型、專案導入及效能評估場景。