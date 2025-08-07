```markdown
# 在 Docker 上面執行 .NET (CoreCLR) Console App

# 問題／解決方案 (Problem/Solution)

## Problem: 使用傳統 VM 佈署小型 .NET 應用，資源成本與維運負擔過高  
**Problem**:  
• 在單一實體主機上為了維持「三層式」架構而需要開多台 VM。  
• 每台 VM 都必須安裝 OS、Patch、Anti-Virus，掃毒時還會同時佔用大量 I/O 與 CPU。  
• 小規模系統很快就被「OS + 防毒 + Patch」耗盡資源，應用程式本身反而跑不動。  

**Root Cause**:  
1. VM 完整虛擬化了作業系統 → 每個 VM 都是一份 OS。  
2. OS 本身的背景服務（更新、掃毒）與維運工作（Patch、監控）變成多重負擔。  
3. 架構「被迫」與硬體資源綁定，無法依需求做細粒度的水平切割。  

**Solution**:  
• 用 Docker Container 只虛擬化「應用程式執行環境」而非整個 OS。  
• 將三層分別封裝成 3 個 Container，互相隔離又共享同一個主機核心。  
• Container 無 OS 掃毒、Patch，維運僅針對映像檔做版本管理。  
• 無需為規模小的專案額外採購/維護多台 VM，只要一台 NAS 或一台 Ubuntu Server 即可佈署完整架構。  

**Cases 1**:  
• 過去：PC Server (Q9400/8 GB RAM) + 10 台 VM。  
• 轉換後：Synology DS-412+ (Atom 2C/1 GB RAM) + 多個 Docker Container  
→ 同樣架構只佔原本 < 25 % 的硬體資源，電費與運維成本同步下降。  

---

## Problem: 在 Linux/Docker 上跑 .NET Core Console App 時缺乏「非 ASP.NET」範例  
**Problem**:  
• 官方與社群文章多聚焦「ASP.NET 5 + Dockerfile 打包」情境。  
• 只是想單純執行一支 Console App，卻找不到一步到位的流程，導致大量試錯。  

**Root Cause**:  
1. 文件生態以 Web 為主，Console 範例稀少。  
2. 多數教學直接要求自行製作 Dockerfile 與映像檔，對想先驗證程式碼的人過度複雜。  
3. 對 Windows 開發者而言，Linux CLI（cp、bash、dnvm/dnu/dnx）不熟悉，資訊碎片化更易造成阻礙。  

**Solution**:  
• 直接使用 Microsoft 官方提供之 ASP.NET 5 CoreCLR 預先建好之映像檔 (microsoft/aspnet:1.0.0-beta8-coreclr)，避免自行 build。  
• 流程：  
  ```bash
  # 1. 下載映像
  sudo docker pull microsoft/aspnet:1.0.0-beta8-coreclr  

  # 2. 啟動 Container（daemon）
  sudo docker run -d --restart always microsoft/aspnet  

  # 3. 取得 Container ID
  sudo docker ps -a  

  # 4. 進入 Container
  sudo docker exec -it <CONTAINER_ID> /bin/bash  

  # 5. 將 VS2015 編譯產物複製進 Container
  sudo docker cp ./ConsoleApp1 <CONTAINER_ID>:/home/ConsoleApp1  

  # 6. Container 內操作
  cd /home/ConsoleApp1
  dnvm list                # 確認可用 Runtime
  dnvm install latest -r coreclr -arch x64
  dnu restore              # 還原 NuGet 相依
  dnx run                  # 執行 Console App
  ```
• 避免撰寫 Dockerfile，也不需要瞭解 Linux 套件安裝細節；開發者只要學會 `docker exec`/`docker cp` 即可。  

**Cases 1**:  
• 從「第一次寫指令」到成功印出  
  ```
  Hello! .NET Core!
  ```
  時間 < 4 小時（含查資料）；後續第二次相同佈署流程僅需 10 分鐘完成。  

---

## Problem: 微軟生態系開發者跨入 Docker + .NET Core 的學習曲線過高  
**Problem**:  
• 必須同時理解 Docker 基本概念、Linux 環境、CoreCLR 新工具鏈（DNVM/DNU/DNX）。  
• 缺乏一條漸進式「由易到難」的路徑，常見做法是直接安裝 preview/RC 版 VS 或在 Linux hand-install，容易踩雷。  

**Root Cause**:  
1. 工具鏈名稱多且相依關係複雜，DNVM ≠ VM，易混淆。  
2. 開發者若完全沒 Linux 基礎，Docker CLI 與檔案系統觀念落差大。  
3. 官方文件分散：Docker 文件談 Container；.NET 文件談 Runtime；缺少「整合」教學。  

**Solution**:  
提出「三階段漸進式」學習流程：  
1. 先以 NAS Docker GUI 或 Docker Toolbox 體驗 Container 概念（零 Linux 安裝成本）。  
2. 再手動在舊筆電安裝 Ubuntu Server，完整走一次 CLI 安裝 Docker → 體驗實際維運工作。  
3. 最後才切入 CoreCLR，集中火力熟悉三大工具：  
   • DNVM (.NET Version Manager) – 安裝/切換 Runtime  
   • DNU  (.NET Utilities)      – 還原/Build/發行  
   • DNX  (.NET Execution Env.) – 啟動 .NET 程式  
   透過最小可執行範例 (Hello World Console) 先完成「編譯-還原-執行」閉環，再進一步研究 MVC6 / ASP.NET 5。  

**Cases 1**:  
• 前置準備時間：環境（NAS + Ubuntu）約 1 週；真正專注於 CoreCLR 強化僅 1 天，即可在 Linux Container 成功跑 Code。  
• 學習曲線被切成 3 個明確 Milestone，團隊新人依照文件即可在 2 天內完成同等環境。  

```
