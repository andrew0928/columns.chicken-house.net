---
layout: synthesis
title: "在 Docker 上面執行 .NET (CoreCLR) Console App"
synthesis_type: solution
source_post: /2015/10/31/coreclr-helloworld-consoleapp/
redirect_from:
  - /2015/10/31/coreclr-helloworld-consoleapp/solution/
---

以下為基於原文內容重組的 16 個可教可練的技術問題解決案例。每個案例均包含：問題、根因、解法（含指令/程式碼/流程）、實際效益與可評估的學習與實作要點。

## Case #1: 在 Docker 中快速執行 .NET Core Console（免建 image）
### Problem Statement（問題陳述）
- 業務場景：開發者需在 Linux（Ubuntu Server 或 NAS 上的 Docker）快速驗證 .NET Core（CoreCLR）Console App 能否跨平台執行，但不想為一次性測試就建立自製 Docker image，只求最短路徑完成「Hello World」跨 OS 跑通。
- 技術挑戰：網路文件多聚焦於 ASP.NET 在 Docker 的封裝（Dockerfile 建 image），較少示範 Console App 的最小步驟，加上 Linux/DNX/DNU/DNVM 工具鏈初學成本高。
- 影響範圍：若不能快速驗證跨平台執行，會延誤團隊對 .NET Core 與容器化的評估，增加採用門檻與試錯成本。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. 文件焦點錯位：官方與社群多以 Web 範例與 Dockerfile 打包為主，未覆蓋 Console App 快速驗證流程。
  2. 工具鏈陌生：DNVM/DNU/DNX 與傳統 .NET Workflow 差異大，初期無法串起「還原→執行」。
  3. 封裝過度：為一次性測試建立 image 增加不必要的準備工，延長驗證時間。
- 深層原因：
  - 架構層面：將「環境就緒」與「應用封裝」耦合，欠缺最小化驗證策略。
  - 技術層面：對核心 CLI（docker exec、docker cp、dnvm/dnu/dnx）指令鏈不熟悉。
  - 流程層面：未建立「先快跑通、後再最佳化封裝」的漸進式流程。

### Solution Design（解決方案設計）
- 解決策略：使用 Microsoft 官方 ASP.NET CoreCLR 基底 image（已含 DNX/DNVM/DNU），以 docker exec 進入容器互動式執行，透過 docker cp 投遞專案，dnu restore 後 dnx run 直接跑起 Console App，快速驗證跨平台可行性，再視需求演進至建置自有 image。

- 實施步驟：
  1. 取得並啟動官方基底容器
     - 實作細節：pull 指定 tag；run 時加上 -d 與 --restart always
     - 所需資源：Docker（Linux/NAS/Toolbox）
     - 預估時間：10 分鐘
  2. 進入容器與投遞專案
     - 實作細節：docker ps 取得 ID；docker exec 進 shell；docker cp 投遞專案資料夾
     - 所需資源：VS 2015 專案目錄（含 project.json）
     - 預估時間：10-15 分鐘
  3. 還原相依與執行
     - 實作細節：dnvm list/upgrade；dnu restore；dnx run
     - 所需資源：容器網路可通往 NuGet
     - 預估時間：10-20 分鐘

- 關鍵程式碼/設定：
```bash
# 1) Docker 端
sudo docker pull microsoft/aspnet:1.0.0-beta8-coreclr
sudo docker run -d --restart always --name coreclrbase microsoft/aspnet:1.0.0-beta8-coreclr
sudo docker ps -a
sudo docker exec -it coreclrbase /bin/bash

# 2) 專案投遞（在 Docker Host）
sudo docker cp ./ConsoleApp1 coreclrbase:/home/ConsoleApp1

# 3) 容器內還原與執行
cd /home/ConsoleApp1
dnvm list
# 如需可：dnvm upgrade -r coreclr -arch x64
dnu restore
dnx run
```

```csharp
// Program.cs
using System;
class Program {
  static void Main(string[] args) {
    Console.WriteLine("Hello! .NET Core on Linux via Docker");
  }
}
```

```json
// project.json (beta8 sample)
{
  "version": "1.0.0-*",
  "description": "ConsoleApp1",
  "frameworks": {
    "dnxcore50": {
      "dependencies": {
        "System.Console": "4.0.0-beta-23516"
      }
    }
  }
}
```

- 實際案例：作者以 microsoft/aspnet:1.0.0-beta8-coreclr 為基底，將 ConsoleApp1 丟入容器，dnu restore 後 dnx 執行成功。
- 實作環境：Ubuntu Server（或 NAS Docker）、Visual Studio 2015 RTM、Docker 1.x、microsoft/aspnet:1.0.0-beta8-coreclr
- 實測數據：
  - 改善前：無法在 Linux 上快速驗證 Console App 跨平台執行
  - 改善後：一個上午內完成跨平台執行驗證（dnu restore + dnx run 成功）
  - 改善幅度：從「無法驗證/卡關」到「100% 跑通最小範例」

Learning Points（學習要點）
- 核心知識點：
  - 使用官方基底 image 快速就緒，避免過早封裝
  - docker exec/docker cp 對 ad-hoc 驗證的價值
  - DNVM/DNU/DNX 基本工作流：列版本→還原→執行
- 技能要求：
  - 必備技能：Docker CLI、Linux 基本指令、.NET 專案結構
  - 進階技能：自製 Dockerfile 封裝、私有 NuGet 快取
- 延伸思考：
  - 從快速驗證演進到正式封裝與 CI/CD？
  - 容器內還原套件對網路與安全的風險？
  - 改用 volume 掛載減少 docker cp 的反覆傳檔？
- Practice Exercise（練習題）
  - 基礎：使用上述指令在容器內跑出 Hello World（30 分）
  - 進階：改以 volume 掛載專案並執行（2 小時）
  - 專案：在 CI 產出 image，啟動即執行 Console App（8 小時）
- Assessment Criteria（評估標準）
  - 功能完整性（40%）：可在容器內成功執行並輸出訊息
  - 程式碼品質（30%）：project.json 依賴正確、結構清晰
  - 效能優化（20%）：還原時間與步驟最小化（如快取 NuGet）
  - 創新性（10%）：提出 volume/多架構擴展做法


## Case #2: 用容器取代 VM 避免 OS 開銷與管理負擔
### Problem Statement（問題陳述）
- 業務場景：小規模服務（如個人/團隊部落格）傳統以多台 VM 實作三層架構，雖可擴展但為 OS 維運與資源開銷所苦（AV 同時掃描、OS 更新），影響主機效能與穩定性。
- 技術挑戰：VM 完整虛擬化導致每台皆需 OS 管理與資源；在小負載場景性價比不佳。
- 影響範圍：資源浪費、維運複雜度提升、系統可靠性下降（高峰掃描造成宕機）。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. OS 重複運行：每個 VM 都要跑一套 OS（CPU/RAM/IO 消耗）。
  2. 管理噪音：AV、Patch、更新會在多 VM 同時發生。
  3. 過度工程：小規模負載不需要全三層多 VM 的隔離強度。
- 深層原因：
  - 架構層面：未依負載與成本選擇恰當隔離等級。
  - 技術層面：忽略容器只虛擬應用層的優勢。
  - 流程層面：VM lifecycle 管理成本被低估。

### Solution Design（解決方案設計）
- 解決策略：以 Docker 將各組件容器化（Web、DB、Reverse Proxy），共用宿主 OS 核心，達到架構隔離與資源效率兼顧；對外以反向代理歸一 port/url；資源緊湊時仍可保三層邏輯。

- 實施步驟：
  1. 拆分服務與容器設計
     - 實作細節：Web/DB/Proxy 各一容器，網段隔離
     - 所需資源：Docker、映像（如 WordPress/MySQL/Nginx）
     - 預估時間：1 小時
  2. 建立容器與網路
     - 實作細節：docker network、對外僅開 proxy port
     - 所需資源：Docker CLI 或 NAS Docker UI
     - 預估時間：1 小時
  3. 導入反向代理與備份
     - 實作細節：Nginx 反代、DB/volume 備份計畫
     - 所需資源：Nginx 設定、排程工具
     - 預估時間：1-2 小時

- 關鍵程式碼/設定（示意）：
```nginx
# nginx reverse proxy (示例)
server {
  listen 80;
  server_name blog.example.com;
  location / {
    proxy_pass http://wordpress:80;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-For $remote_addr;
  }
}
```

- 實際案例：作者以 NAS（Synology）Docker 套件架設 WordPress，配合反向代理與備份，實際運行替代原本 PC+VM 架構。
- 實作環境：Synology DS-412+（Atom 2C/1GB RAM）、Docker、WordPress 容器
- 實測數據：
  - 改善前：PC Server（Q9400/4C/8GB）+ VM，資源開銷大
  - 改善後：NAS 上完成同等架構，運算資源不到原本 1/4
  - 改善幅度：約 75% 資源節省（以 CPU/RAM 綜合觀感）

Learning Points（學習要點）
- 核心知識點：
  - 容器與 VM 的隔離層差異與成本
  - 反向代理在多容器對外曝光治理上的角色
  - 小負載場景的「合理隔離」策略
- 技能要求：
  - 必備技能：Docker 基礎、Nginx 反代、Volume/備份
  - 進階技能：Compose/Swarm 編排、資源監控
- 延伸思考：
  - 何時才需要回到 VM/實體隔離？
  - 多租戶/安全需求提升時的加固手法？
  - 引入 Compose 後的維運自動化？
- Practice Exercise（練習題）
  - 基礎：用兩個容器（Web+DB）跑起部落格（30 分）
  - 進階：加入 Nginx 反向代理與自動備份（2 小時）
  - 專案：以 Compose 一鍵部署三容器並加上健康檢查（8 小時）
- Assessment Criteria（評估標準）
  - 功能完整性（40%）：服務可用且代理配置正確
  - 程式碼品質（30%）：設定檔清晰可讀、版本化
  - 效能優化（20%）：資源用量與端口治理合理
  - 創新性（10%）：自動化與監控強化


## Case #3: 用真實專案（部落格）取代 POC，完整練習 Docker
### Problem Statement（問題陳述）
- 業務場景：學 Docker 若只做 POC（「能跑就好」）容易忽略實務要素（反代、備份、持久化、升級），導致投入生產時再次踩雷；需要以真實部落格搬遷來練習完整生命週期。
- 技術挑戰：涵蓋網路、儲存、備援與備份，且需兼顧 NAS 上的有限資源。
- 影響範圍：若不做實戰，日後上線仍需補課，影響進度與品質。
- 複雜度評級：中

### Root Cause Analysis（根因分析）
- 直接原因：
  1. POC 目標侷限：只驗證可運行，未練到維運重點。
  2. 工具錯覺：以為 NAS 上 Docker 和實體主機一樣簡單。
  3. 持久化忽略：資料與設定未設計 volume 與備份。
- 深層原因：
  - 架構層面：缺少對完整 App Lifecycle 的規畫。
  - 技術層面：對反向代理、備份/還原流程不足。
  - 流程層面：缺乏實作驗證與演練。

### Solution Design（解決方案設計）
- 解決策略：選擇部落格搬遷為練習目標，從映像選擇、資料持久化、反代、備份復原到升級流程完整走一遍，確保從開發到維運全鏈打通。

- 實施步驟：
  1. 選擇映像與設計資料卷
     - 實作細節：網站與資料分卷（WordPress volume、DB volume）
     - 所需資源：Docker/NAS 儲存
     - 預估時間：1 小時
  2. 部署與反代
     - 實作細節：容器啟動與 Nginx 反代、域名解析
     - 所需資源：Nginx/域名
     - 預估時間：1-2 小時
  3. 備份與升級演練
     - 實作細節：排程備份、容器升版回滾流程
     - 所需資源：排程工具、備份儲存
     - 預估時間：2 小時

- 關鍵程式碼/設定（示意）：
```bash
# 資料持久化示例（WordPress + MySQL）
docker network create blognet
docker run -d --name db --network blognet \
  -e MYSQL_ROOT_PASSWORD=secret -e MYSQL_DATABASE=wp \
  -v /volume1/docker/db:/var/lib/mysql mysql:5.7

docker run -d --name wp --network blognet -p 8080:80 \
  -e WORDPRESS_DB_HOST=db:3306 \
  -e WORDPRESS_DB_USER=root -e WORDPRESS_DB_PASSWORD=secret \
  -v /volume1/docker/wp:/var/www/html wordpress:latest
```

- 實際案例：作者以 NAS Docker 成功搬家部落格，涵蓋反代與備份考量。
- 實作環境：Synology Docker 套件、Nginx、WordPress/MySQL
- 實測數據：
  - 改善前：只做 POC，缺乏維運驗證
  - 改善後：完整演練，日後佈署心中有譜
  - 改善幅度：從「未知風險」降至「已演練可控」

Learning Points
- 核心知識點：POC 與實戰差異、資料持久化策略、反向代理與升級回滾
- 技能要求：Docker/Nginx/Volume/備份必備；Compose/監控進階
- 延伸思考：如何引入 CI/CD 與 IaC？NAS 資源瓶頸如何監控？
- 練習題：將個人站點容器化（30 分）；加入備份與回滾（2 小時）；以 Compose 完成一鍵部署（8 小時）
- 評估：可用性（40%）/ 設定品質（30%）/ 可維運性（20%）/ 創新（10%）


## Case #4: 手動架設 Ubuntu Docker Host，補齊 NAS UI 以外的能力
### Problem Statement（問題陳述）
- 業務場景：Synology Docker UI 讓上手容易，但真正佈署/升級需要熟悉 CLI 與 Linux 基礎；需在舊筆電上自建 Ubuntu Server + Docker，掌握安裝與設定細節。
- 技術挑戰：從 0 到 1 的 Linux 環境建置、Docker 安裝、使用者/權限與網路設定。
- 影響範圍：若僅依賴 UI，面對非 NAS 環境佈署將手足無措。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. UI 與真實 CLI 差距：UI 隱藏大量細節。
  2. 環境差異：實體主機與 NAS 生態不同。
  3. 文件碎片：安裝路徑眾多、版本相依性複雜。
- 深層原因：
  - 架構層面：環境抽象層不足導致遷移成本高。
  - 技術層面：Linux/網路/權限知識缺口。
  - 流程層面：缺乏安裝/設定步驟記錄與自動化。

### Solution Design
- 解決策略：在實體/虛擬機安裝 Ubuntu Server，使用官方 Docker 套件庫安裝 Docker Engine，完成測試與基本守護設定（開機自啟、使用者群組、mirror），建立可複製的筆記。

- 實施步驟：
  1. 安裝 Ubuntu 與先決條件
     - 實作細節：更新 APT、安裝必要工具
     - 資源：Ubuntu ISO、網路
     - 時間：30-60 分
  2. 安裝 Docker Engine
     - 實作細節：加官方 repo、安裝 docker-ce
     - 資源：GPG key、APT
     - 時間：30 分
  3. 基礎驗證與權限
     - 實作細節：hello-world、加入 docker 群組
     - 資源：CLI
     - 時間：20 分

- 關鍵程式碼/設定：
```bash
sudo apt-get update && sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update && sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER
docker run hello-world
```

- 實際案例：作者自建 Ubuntu Server，親走安裝與設定細節，強化日後升級與改參能力。
- 實作環境：Ubuntu Server、Docker CE
- 實測數據：
  - 改善前：只熟 NAS UI，遷移能力不足
  - 改善後：CLI 熟悉，遇部署問題心中有譜
  - 改善幅度：從「不知如何下手」到「獨立建置成功」

Learning Points：Linux/Docker 安裝、權限管理；進階：自動化腳本與 Ansible
練習題：以腳本自動安裝 Docker（30 分）/ 加入 registry mirror 與 logrotate（2 小時）/ 出一份主機硬化流程（8 小時）
評估：可重現性（40%）/ 腳本品質（30%）/ 穩定性（20%）/ 創新（10%）


## Case #5: 釐清 CoreCLR、DNX、DNVM、DNU 工具鏈，避免用錯
### Problem Statement
- 業務場景：ASP.NET 5（vNext）時代名詞大改，若不先釐清 CoreCLR/DNX/DNVM/DNU 關係，容易在還原/執行/升級步驟誤操作，導致卡關。
- 技術挑戰：新舊概念映射複雜，同名詞與 Java 類比易混淆。
- 影響範圍：學習效率與問題定位速度大幅下降。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 名詞更新頻繁（Project K → DNX）。
  2. 與傳統 .NET/Java 類比易誤解（DNVM 非 VM）。
  3. 工具職責界線不清（版本管理 vs 執行 vs 還原）。
- 深層原因：
  - 架構層面：工具權責未被內建於 IDE 流程。
  - 技術層面：缺少「一圖看懂」的知識地圖。
  - 流程層面：未先建立最小工作流心智模型。

### Solution Design
- 解決策略：以功能導向快速定義：DNVM（版本管理）、DNX（執行）、DNU（開發工具/還原），建立固定工作序列（dnvm → dnu → dnx），在容器中用同一套指令流程跑通。

- 實施步驟：
  1. 名詞對照表與最小工作流
     - 實作細節：建立速記卡與指令清單
     - 資源：官方文件
     - 時間：30 分
  2. 實操驗證
     - 實作細節：在容器內依序執行 dnvm/dnu/dnx
     - 資源：官方 image
     - 時間：30 分
  3. 錯誤場景演練
     - 實作細節：刻意用錯 runtime/跳過 restore
     - 資源：容器環境
     - 時間：1 小時

- 關鍵程式碼/設定：
```bash
# 心智序列：版本 → 套件 → 執行
dnvm list
dnvm upgrade -r coreclr -arch x64
dnu restore
dnx run
```

- 實際案例：作者於容器中依序操作 dnvm/dnu/dnx 跑通 Console App。
- 實測數據：
  - 改善前：概念混亂，摸索時間長
  - 改善後：固定序列 3 步驟跑通
  - 改善幅度：定位效率顯著提升（由無序探索→有序流程）

Learning Points：工具職責、最小工作流；進階：多 runtime 並存策略
練習題：列出命令與說明卡（30 分）/ 故障演練與排錯記錄（2 小時）/ 做一張工具鏈關係圖（8 小時）
評估：準確度（40%）/ 梳理清晰度（30%）/ 排錯效率（20%）/ 創新（10%）


## Case #6: Windows 上用 Docker Toolbox 快速就緒
### Problem Statement
- 業務場景：手邊只有 Windows，要快速獲得可用的 Docker 環境進行 .NET Core 容器實驗。
- 技術挑戰：安裝多元（Toolbox/WSL/手動 VM），新手容易卡虛擬化細節。
- 影響範圍：環境就緒時間直接影響學習曲線。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 無 Linux 主機可用。
  2. 虛擬化組合繁雜。
  3. 多版本相依導致踩雷。
- 深層原因：
  - 架構層面：環境抽象不足。
  - 技術層面：不熟 Boot2Docker/VirtualBox。
  - 流程層面：無一鍵初始化步驟。

### Solution Design
- 解決策略：採用 Docker Toolbox（含 Windows 客戶端、VirtualBox 與 Boot2Docker），透過 docker-machine 快速建立預設 VM，立即具備 Docker Host 能力開始實驗。

- 實施步驟：
  1. 安裝 Toolbox
     - 細節：下載官方安裝包
     - 資源：管理員權限
     - 時間：10-15 分
  2. 建立與驗證主機
     - 細節：docker-machine create default；docker version
     - 資源：VirtualBox
     - 時間：10-15 分
  3. 連線與測試
     - 細節：eval env；docker run hello-world
     - 時間：10 分

- 關鍵程式碼/設定：
```bash
docker-machine create --driver virtualbox default
docker-machine env default
eval $(docker-machine env default)
docker run hello-world
```

- 實際案例：作者建議無 Linux 環境者可用 Toolbox 快速起步。
- 實測數據：
  - 改善前：零 Docker 環境
  - 改善後：30-40 分鐘內可運行容器
  - 改善幅度：Time-to-First-Container 明顯縮短

Learning Points：docker-machine 基本用法；進階：切換多 Host
練習題：建兩台 machine 並切換（30 分）/ 部署 .NET App 至 default（2 小時）/ 撰寫一鍵初始化腳本（8 小時）
評估：成功率（40%）/ 步驟清晰（30%）/ 自動化程度（20%）/ 創新（10%）


## Case #7: 互動式進入容器（docker exec）像 VM 一樣操作
### Problem Statement
- 業務場景：需要在現成容器內進行 DNVM/DNU/DNX 命令列操作，不想為臨時測試重建 image。
- 技術挑戰：不了解如何「進到」容器內互動操作。
- 影響範圍：若不會 exec，無法快速實驗/排錯。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 容器與 VM 心智模型未連接。
  2. 不熟 docker exec 參數（-it）。
  3. 容器識別（ID/Name）取得不熟。
- 深層原因：
  - 架構層面：把容器當黑盒。
  - 技術層面：CLI 使用不足。
  - 流程層面：缺少「快速進箱」標準作業。

### Solution Design
- 解決策略：以 docker ps 查找容器 ID/Name，docker exec -it <id> /bin/bash 進入，將容器視為輕量「可進入的執行環境」，完成 ad-hoc 操作。

- 實施步驟：
  1. 查容器
     - 細節：docker ps -a 與 --format
     - 時間：5 分
  2. 進容器
     - 細節：exec -it /bin/bash
     - 時間：5 分
  3. 操作並退出
     - 細節：進行 dnu/dnx；exit
     - 時間：10-20 分

- 關鍵程式碼/設定：
```bash
docker ps -a
docker exec -it <container_id_or_name> /bin/bash
# 容器內操作...
dnvm list && dnu restore && dnx run
exit
```

- 實際案例：作者以 exec 進入 microsoft/aspnet 容器進行 .NET 指令操作。
- 實測數據：
  - 改善前：無法在容器內執行命令列
  - 改善後：秒級進入並完成測試
  - 改善幅度：排錯效率顯著提升

Learning Points：exec 常見參數與 TTY；進階：nsenter/exec 多進程管理
練習：嘗試多個 shell session（30 分）/ 使用 --user 切換身分（2 小時）/ 腳本化常用操作（8 小時）
評估：操作熟練（40%）/ 安全意識（30%）/ 效率（20%）/ 創新（10%）


## Case #8: 以 docker cp 投遞 .NET 專案，快速驗證
### Problem Statement
- 業務場景：只需快速把 VS 專案丟進容器跑起來，不必先設 volume 或建 image。
- 技術挑戰：容器與宿主檔案系統隔離，如何傳檔最直覺？
- 影響範圍：若卡在傳檔，整體驗證將延誤。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 未設定共享目錄/volume。
  2. 不熟 docker cp 語法。
  3. 路徑/權限不明。
- 深層原因：
  - 架構層面：未規劃持久化策略。
  - 技術層面：檔案傳輸手段不了解。
  - 流程層面：缺少「投遞→驗證→清理」作業。

### Solution Design
- 解決策略：使用 docker cp 直接將專案資料夾複製到容器內的工作目錄，完成還原與執行；事後再考慮 volume 與正式封裝。

- 實施步驟：
  1. 準備專案
     - 細節：包含 project.json、程式碼
     - 時間：5 分
  2. 複製
     - 細節：docker cp ./ConsoleApp1 <id>:/home/ConsoleApp1
     - 時間：5 分
  3. 還原與執行
     - 細節：dnu restore；dnx run
     - 時間：10-15 分

- 關鍵程式碼/設定：
```bash
docker cp ./ConsoleApp1 coreclrbase:/home/ConsoleApp1
docker exec -it coreclrbase /bin/bash -lc "cd /home/ConsoleApp1 && dnu restore && dnx run"
```

- 實際案例：作者將專案置於 /home/ConsoleApp1 後成功運行。
- 實測數據：
  - 改善前：無法快速傳檔
  - 改善後：一條指令完成投遞
  - 改善幅度：傳檔時間縮短為秒級

Learning Points：cp 用法與限制；進階：volume、bind mount 與同步
練習：cp 單檔與資料夾（30 分）/ 改用 bind mount（2 小時）/ 設計傳檔與清理腳本（8 小時）
評估：正確性（40%）/ 便利性（30%）/ 可維護性（20%）/ 創新（10%）


## Case #9: 用 DNVM 選對 CoreCLR x64 Runtime，避免執行失敗
### Problem Statement
- 業務場景：容器內可能存在多個 DNX 版本/架構，若選錯 runtime 造成無法執行或不兼容。
- 技術挑戰：如何檢視、安裝與切換適合的 DNX（coreclr x64）？
- 影響範圍：執行錯誤、時間浪費。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 多版本並存，預設可能非 coreclr。
  2. 架構不符（x86/x64）。
  3. 版本過舊與套件不匹配。
- 深層原因：
  - 架構層面：缺少 runtime 管理策略。
  - 技術層面：DNVM 指令不熟。
  - 流程層面：未在還原前確認 runtime。

### Solution Design
- 解決策略：以 dnvm list 檢視，dnvm install/upgrade 安裝 coreclr x64；固定專案對應版本，避免不兼容。

- 實施步驟：
  1. 檢視版本
     - 細節：dnvm list
     - 時間：3 分
  2. 安裝/升級
     - 細節：dnvm upgrade -r coreclr -arch x64
     - 時間：5-10 分
  3. 驗證
     - 細節：dnx --version、跑範例
     - 時間：5 分

- 關鍵程式碼/設定：
```bash
dnvm list
dnvm upgrade -r coreclr -arch x64
dnx --version
```

- 實際案例：作者選用 coreclr x64 版本成功執行。
- 實測數據：
  - 改善前：可能出現版本/架構錯配
  - 改善後：執行穩定
  - 改善幅度：避免 100% 的版本錯配錯誤

Learning Points：runtime/架構選擇；進階：鎖定專案 global.json
練習：安裝多版本並切換（30 分）/ 撰寫版本鎖定策略（2 小時）/ 建版本管理指南（8 小時）
評估：正確性（40%）/ 可重現性（30%）/ 風險控制（20%）/ 創新（10%）


## Case #10: 用 DNU 還原 NuGet 相依，解決缺套件問題
### Problem Statement
- 業務場景：容器內第一次執行專案，常缺失 NuGet 相依套件，需要在 Linux 容器內完成還原。
- 技術挑戰：網路/代理/來源設定與 DNU 用法。
- 影響範圍：無法編譯/執行，開發者誤判為跨平台不支援。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 容器為乾淨環境，缺少套件。
  2. NuGet 來源/網路未通。
  3. DNU 指令不熟。
- 深層原因：
  - 架構層面：缺 NuGet 快取策略。
  - 技術層面：來源與代理未配置。
  - 流程層面：缺還原前檢查步驟。

### Solution Design
- 解決策略：容器內執行 dnu restore，必要時配置 NuGet.Config 或使用代理；完成後再 dnx run。

- 實施步驟：
  1. 檢查網路與來源
     - 細節：ping、NuGet feed
     - 時間：5 分
  2. 還原
     - 細節：dnu restore
     - 時間：5-15 分
  3. 驗證
     - 細節：檢查 packages 資料夾
     - 時間：3 分

- 關鍵程式碼/設定：
```bash
cd /home/ConsoleApp1
dnu restore --no-cache
# 必要時放置 NuGet.Config 到 ~/.config/NuGet/NuGet.Config
```

- 實際案例：作者於容器中成功 dnu restore 下載相依後執行成功。
- 實測數據：
  - 改善前：缺少相依導致無法執行
  - 改善後：一次指令解決，順利編譯/執行
  - 改善幅度：從 0% 成功率提升到 100%（在網路通暢前提）

Learning Points：NuGet 還原流程；進階：私有快取/代理
練習：切換來源與代理（30 分）/ 設置本地快取（2 小時）/ 封裝還原至 CI（8 小時）
評估：成功率（40%）/ 配置品質（30%）/ 穩定性（20%）/ 創新（10%）


## Case #11: 以 DNX 執行 Console App 並驗證系統資訊
### Problem Statement
- 業務場景：需要在 Linux 容器內實際執行 .NET Core Console，並向團隊證明「確實在 Linux 上跑」。
- 技術挑戰：正確進入專案目錄、判斷當前 OS 環境。
- 影響範圍：跨平台可行性的決策。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 未在專案根目錄執行 dnx。
  2. 未還原完成就執行。
  3. 未能證明執行環境（Windows Terminal 誤導）。
- 深層原因：
  - 架構層面：驗證方法未定義。
  - 技術層面：環境檢測方法不熟。
  - 流程層面：缺少「執行前檢查表」。

### Solution Design
- 解決策略：在容器內到專案根目錄，dnu restore 完成後 dnx run；以輸出/系統指令輔佐顯示 OS 版本，避免混淆。

- 實施步驟：
  1. 準備專案與還原
     - 細節：參見前案
     - 時間：10-15 分
  2. 執行與驗證
     - 細節：dnx run；併發一個 shell 印出 /etc/os-release
     - 時間：5 分
  3. 留證
     - 細節：截圖或 log 保存
     - 時間：5 分

- 關鍵程式碼/設定：
```bash
# 容器內
cd /home/ConsoleApp1
dnu restore
dnx run
cat /etc/os-release  # 顯示容器 Linux 發行版資訊
```

- 實際案例：作者以 DNX 執行並附上 OS 資訊，證明在 Ubuntu Server 上運行。
- 實測數據：
  - 改善前：跨平台可行性不明
  - 改善後：成功執行並佐證 OS
  - 改善幅度：決策信心顯著提升

Learning Points：dnx run 使用、OS 證明方法；進階：程式內印出 Runtime 資訊
練習：輸出更多環境資訊（30 分）/ 自動化驗證腳本（2 小時）/ 產出驗證報告（8 小時）
評估：可證性（40%）/ 自動化（30%）/ 清晰度（20%）/ 創新（10%）


## Case #12: 使用 --restart always 提升容器可用性
### Problem Statement
- 業務場景：容器意外退出或宿主重開機後需自動恢復，避免手動啟動。
- 技術挑戰：不熟 Dockerd restart policy。
- 影響範圍：服務可用性與維運負擔。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 容器預設不自啟。
  2. 忽略 policy 設定。
  3. 重啟/崩潰後需人工介入。
- 深層原因：
  - 架構層面：可用性設計不足。
  - 技術層面：Docker run 參數不熟。
  - 流程層面：未建立復原自動化。

### Solution Design
- 解決策略：在 docker run 時加 --restart always，確保宿主重啟/容器崩潰可自動起來。

- 實施步驟：
  1. 設定 policy
     - 細節：--restart always/on-failure
     - 時間：3 分
  2. 測試重啟
     - 細節：重啟 dockerd 或 OS
     - 時間：10-15 分
  3. 監控驗證
     - 細節：docker ps；log
     - 時間：5 分

- 關鍵程式碼/設定：
```bash
docker run -d --restart always --name coreclrbase microsoft/aspnet:1.0.0-beta8-coreclr
```

- 實際案例：作者啟動官方基底容器即加上 --restart always。
- 實測數據：
  - 改善前：容器停止需手動啟動
  - 改善後：自動恢復
  - 改善幅度：運維手動介入次數降至 0（同場景）

Learning Points：restart policy；進階：搭配 healthcheck 與監控
練習：比較 always/on-failure/no（30 分）/ 注入 healthcheck（2 小時）/ 產出可用性測試腳本（8 小時）
評估：可靠性（40%）/ 配置正確（30%）/ 測試覆蓋（20%）/ 創新（10%）


## Case #13: 用 docker ps -a 管理容器識別，避免操作錯箱
### Problem Statement
- 業務場景：需對特定容器 exec/cp，若辨識錯 ID/Name 會操作到錯誤目標。
- 技術挑戰：大量容器與隨機 ID，名稱策略不一致。
- 影響範圍：誤操作、資料覆寫。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 只記短 ID，容易混淆。
  2. 名稱未規則化。
  3. 不使用過濾/格式化。
- 深層原因：
  - 架構層面：命名規範缺失。
  - 技術層面：ps/format 運用不足。
  - 流程層面：SOP 未要求核對。

### Solution Design
- 解決策略：使用 docker ps -a 與 --filter/--format 建立一致查詢與命名規範，避免錯誤目標。

- 實施步驟：
  1. 建命名規範
     - 細節：名稱含用途/環境
     - 時間：20 分
  2. 快速查詢
     - 細節：--filter name=xxx；--format
     - 時間：10 分
  3. 前置核對
     - 細節：exec/cp 前雙重確認
     - 時間：5 分

- 關鍵程式碼/設定：
```bash
docker ps -a --format "table {{.Names}}\t{{.ID}}\t{{.Image}}\t{{.Status}}"
docker ps --filter "name=coreclr" --format "{{.ID}} {{.Names}}"
```

- 實際案例：作者以 ps 拿到容器 ID/Name 再 exec 進入。
- 實測數據：
  - 改善前：可能誤箱操作
  - 改善後：定位準確
  - 改善幅度：誤操作風險趨近 0

Learning Points：ps 過濾/格式化；進階：label 與查詢
練習：定義命名規則（30 分）/ 用 label 管理容器（2 小時）/ 寫查詢腳本（8 小時）
評估：準確性（40%）/ 規範性（30%）/ 可維運性（20%）/ 創新（10%）


## Case #14: 文件焦點與需求不符（Web 封裝 vs Console 快測）的戰術調整
### Problem Statement
- 業務場景：官方/社群文多示範 ASP.NET + Dockerfile 建 image，與「Console App 快速驗證」不符。
- 技術挑戰：若盲從文件，投入過度封裝與時間成本。
- 影響範圍：學習曲線變長，影響決策時效。
- 複雜度評級：中

### Root Cause Analysis
- 直接原因：
  1. 文件場景偏 Web。
  2. 缺少 Console 快測範例。
  3. 讀者未調整策略。
- 深層原因：
  - 架構層面：把封裝當前置條件。
  - 技術層面：不熟容器互動式操作。
  - 流程層面：未以「最短成功路徑」為導向。

### Solution Design
- 解決策略：先以官方基底 image + exec/cp + dnx run 快速達成「能跑」，後續再依需要回補 Dockerfile 與自製 image。

- 實施步驟：
  1. 確認目標
     - 細節：明確定義「最小成功」
     - 時間：10 分
  2. 選擇最短路徑
     - 細節：exec/cp/restore/run
     - 時間：30-60 分
  3. 再封裝
     - 細節：將成功範例寫入 Dockerfile
     - 時間：1-2 小時

- 關鍵程式碼/設定：參考 Case #1/#8/#11

- 實際案例：作者未照官方封裝路徑，改走 exec/cp 快速跑通 Console App。
- 實測數據：
  - 改善前：長時間研究 Dockerfile 與封裝
  - 改善後：一個上午完成跨平台驗證
  - 改善幅度：學習/驗證周期顯著縮短

Learning Points：需求導向的技術策略；進階：封裝與快測的權衡
練習：寫出兩版流程並比較（30 分）/ 從快測轉封裝（2 小時）/ 制定團隊最短路徑 SOP（8 小時）
評估：策略貼合度（40%）/ 成本效益（30%）/ 可演進性（20%）/ 創新（10%）


## Case #15: 三階段學習路徑（Docker→Host→CoreCLR）加速跨平台成功
### Problem Statement
- 業務場景：跨入 Linux + Docker + .NET Core 同時學習難度高，需要可落地的學習分階策略。
- 技術挑戰：領域跨度大、易在初期挫折放棄。
- 影響範圍：團隊導入與個人成長。
- 複雜度評級：低

### Root Cause Analysis
- 直接原因：
  1. 嘗試一次學太多。
  2. 缺少里程碑設計。
  3. 無實戰驅動。
- 深層原因：
  - 架構層面：未規劃學習依賴順序。
  - 技術層面：基礎不牢，難以串接。
  - 流程層面：無檢核點。

### Solution Design
- 解決策略：分三階段：1) 以 NAS Docker 完成真實應用；2) 手動架設 Ubuntu Docker Host；3) 熟悉 DNVM/DNU/DNX，將 Console App 在 Linux 容器跑通，漸進收斂到目標。

- 實施步驟：
  1. NAS 實戰（應用）
     - 細節：WordPress + 反代 + 備份
     - 時間：1-2 天
  2. 自建 Host（平台）
     - 細節：Ubuntu + Docker CLI
     - 時間：半天
  3. CoreCLR（運行）
     - 細節：dnvm/dnu/dnx 串接
     - 時間：半天

- 關鍵程式碼/設定：綜合前述案例指令

- 實際案例：作者按此三步驟，終於在一個上午完成 Hello .NET Core on Linux。
- 實測數據：
  - 改善前：無結構化學習，效率低
  - 改善後：分階推進、如期達成
  - 改善幅度：學習效率明顯提升

Learning Points：學習路徑設計；進階：將路徑產品化為新手包
練習：制定個人路線圖（30 分）/ 團隊共用手冊（2 小時）/ 建置教學專案模板（8 小時）
評估：可實施性（40%）/ 任務切分（30%）/ 時間掌控（20%）/ 創新（10%）


## Case #16: 採用 .NET Core + Linux 的「混搭架構」選擇權
### Problem Statement
- 業務場景：過去 .NET 僅限 Windows，導致架構選型受限；如今 .NET Core 支援 Linux，系統架構可在 Windows/Linux 混搭，需重新評估部署策略。
- 技術挑戰：跨 OS 組合的工具鏈、佈署與維運差異。
- 影響範圍：成本、效能與組織技能佈局。
- 複雜度評級：高

### Root Cause Analysis
- 直接原因：
  1. 歷史上 .NET 鎖定 Windows。
  2. 新技術快速演進（CoreCLR）。
  3. 既有決策慣性。
- 深層原因：
  - 架構層面：平台綁定影響長期成本。
  - 技術層面：異質平台工具與知識差異。
  - 流程層面：佈署/監控/運維需統一化。

### Solution Design
- 解決策略：以容器為抽象層統一運行環境，針對工作負載選擇最適 OS，降低鎖定；在 PoC/實戰後制定混搭準則與遷移計劃。

- 實施步驟：
  1. 能力驗證
     - 細節：Console/ASP.NET 在 Linux 容器跑通
     - 時間：半天
  2. 成本/效能評估
     - 細節：Windows vs Linux 成本與效能對照
     - 時間：1-2 天
  3. 準則與路線圖
     - 細節：何時選哪個 OS、遷移與維運標準化
     - 時間：2 天

- 關鍵程式碼/設定：以容器/映像統一，不需重寫程式碼（參考 Case #1~#12）

- 實際案例：作者強調 .NET 開放與 Linux 支援將深刻影響未來架構決策。
- 実測數據：
  - 改善前：平台選擇單一（Windows）
  - 改善後：可在 Linux 運行（+Docker）
  - 改善幅度：平台選擇權從 1 擴展到 2（本質性提升）

Learning Points：平台選型策略；進階：跨平台運維一體化
練習：完成跨平台 PoC（30 分）/ 成本模型與準則文件（2 小時）/ 雙平台佈署管線（8 小時）
評估：策略完整性（40%）/ 證據充足（30%）/ 可落地性（20%）/ 創新（10%）



案例分類
1) 按難度分類
- 入門級：Case #5, #6, #7, #8, #9, #10, #11, #12, #13
- 中級：Case #1, #3, #4, #14, #15
- 高級：Case #2, #16

2) 按技術領域分類
- 架構設計類：Case #2, #14, #15, #16
- 效能優化類：Case #2（資源效率）、#12（可用性間接提升）
- 整合開發類：Case #1, #3, #4, #6, #8, #9, #10, #11
- 除錯診斷類：Case #7, #13
- 安全防護類：Case #3（備份/回滾，間接安全）

3) 按學習目標分類
- 概念理解型：Case #5, #14, #16
- 技能練習型：Case #6, #7, #8, #9, #10, #11, #12, #13
- 問題解決型：Case #1, #3, #4, #2
- 創新應用型：Case #15, #16, #14


案例關聯圖（學習路徑建議）
- 先學：
  - Case #5（名詞與工具鏈）→ 建立心智模型
  - Case #6（Windows 快速環境）或 Case #4（Ubuntu 主機）
- 依賴關係：
  - Case #7（exec）與 #13（ps）是進箱與定位前置能力
  - Case #8（cp）→ #10（restore）→ #11（run）→ #9（選 runtime）
  - Case #12（restart）補充運維可用性
  - Case #1 綜合應用（免建 image 快跑通）
  - Case #3（實戰應用）與 #2（容器化 vs VM）深化架構思維
  - Case #14（策略調整）與 #15（學習路徑）形成方法論
  - Case #16（混搭架構）成為最終架構選型視角
- 完整學習路徑建議：
  1) Case #5 → 2) Case #6 或 #4 → 3) Case #7 + #13 → 4) Case #8 → 5) Case #10 → 6) Case #9 → 7) Case #11 → 8) Case #12 → 9) Case #1（整合驗證）
  10) Case #3（以實戰檢核）→ 11) Case #2（對比 VM 策略）→ 12) Case #14（調整學習/封裝策略）
  13) Case #15（形成個人/團隊路線圖）→ 14) Case #16（制定混搭架構原則）

以上 16 個案例皆源自原文的實戰情境與操作步驟，並補強成教學級的可實作方案與評估依據，可直接用於課程、專案練習與評量。