---
layout: synthesis
title: "Windows Container FAQ - 官網沒有說的事"
synthesis_type: solution
source_post: /2016/09/05/windows-container-faq/
redirect_from:
  - /2016/09/05/windows-container-faq/solution/
postid: 2016-09-05-windows-container-faq
---
{% raw %}

## Case #1: 判斷並選擇正確的容器平台（Windows Container vs Docker for Windows）

### Problem Statement（問題陳述）
**業務場景**：團隊計畫將現有的 ASP.NET WebForms 與部分商用元件容器化，希望透過 Docker 縮短佈署時間並提升一致性。但成員混淆了「Windows Container」與「Docker for Windows（Linux Docker）」，嘗試在開發機上用 Docker for Windows 直接跑 Windows 應用，導致屢次失敗與評估結論失準。管理階層因此質疑可行性並暫停 POC。
**技術挑戰**：需要快速識別應用與容器平台的匹配關係，避免把 Windows App 放到 Linux 容器或反之。
**影響範圍**：錯誤平台選擇造成反覆嘗試、評估延誤、CI 設計誤導與人力浪費。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 概念混淆：將「Docker for Windows」誤解為可執行 Windows App 的平台。
2. 核心差異：Windows Container 共享的是 Windows Kernel；Docker for Windows（預設）是 Linux Engine。
3. 團隊缺乏平台檢核清單：無標準化決策步驟導致錯用。

**深層原因**：
- 架構層面：未建立「工作負載-平台」對應矩陣。
- 技術層面：忽略 Kernel 與系統 API 相容性是容器能否執行的先決條件。
- 流程層面：POC 前未定義平台鑑別與驗證流程。

### Solution Design（解決方案設計）
**解決策略**：建立「工作負載平台決策表」與「平台鑑別腳本」，在 POC 前先自動檢驗 Docker Daemon OS、Image OS 與 App 類型是否相容，並明確規範 Windows 應用需以 Windows Container 執行，Linux 應用需以 Linux Container 執行。

**實施步驟**：
1. 平台檢核
- 實作細節：以 docker version/docker info 讀出 Server OS；建立決策表（Windows App→Windows Container）。
- 所需資源：Docker CLI
- 預估時間：0.5 小時

2. 鑑別腳本與開發者指引
- 實作細節：撰寫腳本輸出「Daemon OS」「Image OS」與建議；納入 PR 檢查清單。
- 所需資源：Shell/PowerShell、團隊 Wiki
- 預估時間：2 小時

**關鍵程式碼/設定**：
```bash
# 檢查 Docker Daemon 的 OS（必須與目標 Image OS 相符）
docker version --format '{{.Server.Os}}/{{.Server.Arch}}'

# 快速決策腳本（bash），Windows 可用 Git Bash
daemon_os=$(docker version --format '{{.Server.Os}}')
image=$1
img_os=$(docker manifest inspect --verbose "$image" 2>/dev/null | \
  grep -i '"os"' | head -n 1 | tr -d '", ' | cut -d: -f2)

echo "DaemonOS=$daemon_os, ImageOS=$img_os"
if [ "$daemon_os" != "$img_os" ]; then
  echo "不相容：請改用 $daemon_os 平台對應的映像或切換 Daemon"
  exit 1
fi
echo "平台相容，可以部署"
```

實際案例：多數團隊誤把 Windows App 放到 Docker for Windows（Linux）執行，經此檢核流程，在計畫初期即避免錯誤。
實作環境：Windows Server 2016（Windows Container）、開發機 Docker for Windows（Linux）
實測數據：
- 改善前：平台誤用導致部署失敗率高、POC 延誤（文章未提供）
- 改善後：導入檢核後於提交前即可攔截（建議指標：0 平台誤用）
- 改善幅度：N/A（本文未提供；建議自行量測）

Learning Points（學習要點）
核心知識點：
- Windows Container 與 Docker for Windows 的本質差異
- 容器與 Kernel 相容性是第一優先
- 以自動化鑑別降低人為錯用

技能要求：
- 必備技能：Docker CLI、OS 基本概念
- 進階技能：腳本化檢核、CI 前置檢查

延伸思考：
- 如何在 CI Pipeline 中強制執行平台鑑別？
- 混合環境（雙引擎）下的最佳實踐？
- 團隊知識管理如何降低再次誤用風險？

Practice Exercise（練習題）
- 基礎練習：撰寫腳本輸出 Daemon 與 Image OS（30 分鐘）
- 進階練習：把鑑別腳本整合到 pre-commit hook（2 小時）
- 專案練習：建立平台決策文件與範本專案（8 小時）

Assessment Criteria（評估標準）
- 功能完整性（40%）：能正確鑑別並阻擋不相容部署
- 程式碼品質（30%）：腳本可維護、具錯誤處理
- 效能優化（20%）：鑑別耗時低於 1s
- 創新性（10%）：與 CI/CD 深度整合、視覺化報表


## Case #2: 修正於 Windows Container 引擎拉取 Linux Image 的錯誤

### Problem Statement（問題陳述）
**業務場景**：團隊在 Windows Server 2016 主機啟用 Windows Container，嘗試直接拉取並運行既有的 Linux 映像（如 alpine, nginx），希望重用既有容器。但執行時出現 OS 不相容錯誤，導致服務無法啟動。
**技術挑戰**：辨識 OS 不相容錯誤，快速替換成 Windows 版等效映像或重建 Windows 版映像。
**影響範圍**：部署中斷、測試停擺；評估 Windows Container 成本被高估。
**複雜度評級**：低

### Root Cause Analysis（根因分析）
**直接原因**：
1. 在 Windows Container 上拉取 Linux OS 映像。
2. 忽略 image OS 與 host OS 必須一致的限制。
3. 缺乏 Windows Base Image 的替代清單。

**深層原因**：
- 架構層面：映像策略未區分多平台。
- 技術層面：未建立 Windows 等效基底（nanoserver, windowsservercore）。
- 流程層面：鏡像來源審核流程缺失。

### Solution Design（解決方案設計）
**解決策略**：在 Windows Container 環境統一以 microsoft/nanoserver 或 microsoft/windowsservercore 為 base，對應重建需要的映像；建立「Linux→Windows」映像對照表。

**實施步驟**：
1. 檢測並攔截不相容映像
- 實作細節：docker run 時檢查錯誤訊息「image operating system … cannot be used on this platform」。
- 所需資源：Docker CLI
- 預估時間：0.5 小時

2. 重建 Windows 版映像
- 實作細節：選擇合適 base（nanoserver 輕量，servercore 相容性高）。
- 所需資源：Dockerfile、Windows Base Images
- 預估時間：2-4 小時

**關鍵程式碼/設定**：
```Dockerfile
# 以 Windows Server Core 為基底重建工具映像
FROM microsoft/windowsservercore:latest
SHELL ["powershell", "-Command"]
# 範例：安裝 7zip 或其他必要工具
RUN Invoke-WebRequest -UseBasicParsing https://www.7-zip.org/a/7z1900-x64.msi -OutFile 7z.msi ; \
    Start-Process msiexec -ArgumentList '/i 7z.msi /qn' -Wait ; \
    Remove-Item 7z.msi -Force
CMD ["powershell"]
```

實際案例：嘗試在 Windows Container 上跑 alpine/nginx 失敗，改用 windowsservercore + IIS 重建網頁服務成功。
實作環境：Windows Server 2016 TP5, Docker Engine for Windows
實測數據：
- 改善前：Linux 映像 100% 無法啟動
- 改善後：Windows 重建映像可啟動（建議指標：成功率、重建耗時）
- 改善幅度：N/A（本文未提供）

Learning Points（學習要點）
- Windows Container 僅能用 Windows Image
- nanoserver vs windowsservercore 的取捨
- 建立等效映像策略

技能要求：
- 必備：Dockerfile 基礎、PowerShell
- 進階：Windows 套件靜默安裝與最佳化

延伸思考：
- 如何以層次化 Dockerfile 降低重建成本？
- 針對商用套件的授權與安裝自動化？

Practice Exercise
- 基礎：用 windowsservercore 建置工具映像（30 分鐘）
- 進階：將常用 Linux 映像功能在 Windows 上重建（2 小時）
- 專案：建立團隊「Linux→Windows」對照倉儲（8 小時）

Assessment Criteria
- 功能完整性（40%）：映像可用且功能等效
- 程式碼品質（30%）：Dockerfile 可維護
- 效能優化（20%）：映像體積與建置時間控制
- 創新性（10%）：自動化重建流程


## Case #3: 修正嘗試在 Docker for Windows（Linux）中執行 Windows 應用

### Problem Statement（問題陳述）
**業務場景**：開發者於 Windows 10 安裝 Docker for Windows，嘗試將既有 .exe 或 ASP.NET 應用放入容器執行，但容器為 Linux 引擎導致執行失敗。團隊以為是 Docker 不成熟而否定容器化。
**技術挑戰**：識別 Docker for Windows 預設是 Linux Engine，並切換至 Windows Container 或使用 Windows Server 主機。
**影響範圍**：錯誤結論誤導決策，造成 POC 失敗。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. 將 Windows 應用置入 Linux 容器。
2. 未理解 Docker for Windows 背後是 Hyper-V Linux VM。
3. 未檢查 Server OS。

**深層原因**：
- 架構層面：開發機設計未支援 Windows Container。
- 技術層面：Kernel 相容性忽略。
- 流程層面：缺少平台切換驗證清單。

### Solution Design
**解決策略**：於開發機上改用 Windows Container（或改用 Windows Server 2016 主機），以 Windows Base Image 重建映像；建立「切換/確認引擎」標準流程。

**實施步驟**：
1. 確認並切換到 Windows 引擎
- 實作細節：檢查 docker version；必要時改用 Windows Server。
- 所需資源：Docker Desktop（支援 Windows 引擎）或 Windows Server
- 預估時間：0.5-1 小時

2. 重建 Windows 映像
- 實作細節：選用 microsoft/windowsservercore 或 nanoserver。
- 所需資源：Dockerfile
- 預估時間：2-4 小時

**關鍵程式碼/設定**：
```powershell
# 檢查當前 Docker Server OS
docker version --format '{{.Server.Os}}'

# 若為 Linux，請切換（在新版 Docker Desktop 可用 UI 切換到 Windows containers）
# 或改在 Windows Server 2016 上安裝 Windows 版 Docker Engine

# 範例：簡單 Windows 映像
# Dockerfile
FROM microsoft/nanoserver:latest
SHELL ["powershell","-Command"]
RUN echo 'Hello from Windows Container' > C:\hello.txt
CMD ["cmd","/c","type C:\\hello.txt"]
```

實際案例：開發機由 Linux 引擎切至 Windows 引擎後，Windows App 得以正常容器化。
實作環境：Windows 10 Pro（RS1 之後）、Windows Server 2016
實測數據：N/A（本文未提供；建議追蹤切換前後的部署成功率）

Learning Points
- Docker for Windows ≠ Windows Container
- 如何辨識/切換容器引擎
- Windows Base Image 的使用

技能要求
- 必備：Docker 基礎、Windows 管理
- 進階：跨平台開發環境治理

延伸思考
- 團隊統一開發環境的政策如何制定？
- CI 上應用雙引擎的最佳實踐？

Practice Exercise
- 基礎：辨識 Docker Server OS 並輸出報告（30 分鐘）
- 進階：建立 Windows/Nano 範例映像（2 小時）
- 專案：制定「平台切換 SOP + Checklist」（8 小時）

Assessment Criteria
- 功能完整性（40%）：可正確切換與運行 Windows App
- 程式碼品質（30%）：映像建置可靠
- 效能（20%）：建置與啟動時間可控
- 創新性（10%）：環境檢核自動化


## Case #4: 在 Windows Server 2016 啟用 Windows Container

### Problem Statement
**業務場景**：團隊選定 Windows Server 2016 作為容器主機，但初次安裝後無法使用 docker 指令或拉取 Windows 映像。需要標準化安裝與啟用流程，快速讓主機具備 Windows Container 能力。
**技術挑戰**：安裝容器功能與 Docker Engine、設定開機服務與網路，確保能拉取 microsoft/* 基底映像。
**影響範圍**：延誤 POC、持續整合管線停滯。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 未啟用 Containers 功能與安裝 Docker 引擎。
2. 網路/NAT 未正確初始化。
3. 缺少標準化自動化腳本。

**深層原因**：
- 架構層面：主機佈署未模版化。
- 技術層面：對 Windows 容器先決條件不熟。
- 流程層面：缺少 IaC/自動化。

### Solution Design
**解決策略**：以 PowerShell 腳本化安裝與設定，包含啟用容器功能、安裝 DockerMsftProvider、安裝 docker、重啟與驗證，納入伺服器建置流程。

**實施步驟**：
1. 安裝與啟用
- 實作細節：啟用 Containers 角色、安裝 Docker 套件。
- 所需資源：PowerShell、DockerMsftProvider
- 預估時間：0.5 小時

2. 驗證與基底映像拉取
- 實作細節：拉取 microsoft/windowsservercore、microsoft/nanoserver。
- 所需資源：網路通路、Docker Hub
- 預估時間：1-2 小時（視頻寬）

**關鍵程式碼/設定**：
```powershell
# 以系統管理員 PowerShell 執行
Install-WindowsFeature -Name containers
Install-Module -Name DockerMsftProvider -Repository PSGallery -Force
Install-Package -Name docker -ProviderName DockerMsftProvider -Force
Restart-Computer -Force

# 重開後驗證
docker version
docker pull microsoft/windowsservercore:latest
docker pull microsoft/nanoserver:latest
docker images
```

實際案例：TP5 主機可成功拉取與運行 windowsservercore/nanoserver 容器。
實作環境：Windows Server 2016 TP5
實測數據：N/A（本文未提供；建議量測：從裸機到可用的平均建置時間）

Learning Points
- Windows Container 前置安裝步驟
- DockerMsftProvider 使用
- 基底映像驗證

技能要求
- 必備：PowerShell、Windows 管理
- 進階：自動化佈署（如 DSC/Ansible）

延伸思考
- 以映像快取（registry mirror）縮短拉取時間
- 以 IaC 建置可複製主機

Practice Exercise
- 基礎：用 PS 腳本完成安裝（30 分鐘）
- 進階：加上錯誤重試與日誌（2 小時）
- 專案：包裝成一鍵佈署（8 小時）

Assessment Criteria
- 功能完整性（40%）：主機可成功啟動容器
- 程式碼品質（30%）：腳本具可讀性與重試
- 效能（20%）：建置時間優化
- 創新性（10%）：IaC 整合


## Case #5: 在 Windows 10（RS1）使用 Hyper‑V 隔離的 Windows Container

### Problem Statement
**業務場景**：開發機為 Windows 10 Pro/Enterprise，需本機開發 Windows Container，且因安全與相容性考量希望使用 Hyper‑V 隔離模式。
**技術挑戰**：啟用必要功能（Containers、Hyper-V）、安裝 Docker，並以 Hyper‑V 隔離啟動容器。
**影響範圍**：本機開發效率、與生產環境一致性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 未啟用 Hyper-V 與 Containers 功能。
2. 不清楚如何指定 Hyper‑V 隔離。
3. 缺乏可複製的設定流程。

**深層原因**：
- 架構層面：開發環境標準化不足。
- 技術層面：隔離模式與旗標不熟悉。
- 流程層面：無安裝腳本。

### Solution Design
**解決策略**：以 PowerShell 啟用功能與安裝，並以 --isolation=hyperv 執行容器，收斂為團隊一鍵腳本。

**實施步驟**：
1. 啟用功能與安裝
- 實作細節：Enable-WindowsOptionalFeature for Containers/Hyper-V。
- 所需資源：PowerShell、重開機權限
- 預估時間：0.5 小時

2. 驗證 Hyper‑V 隔離
- 實作細節：docker run --isolation=hyperv。
- 所需資源：Docker CLI
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```powershell
Enable-WindowsOptionalFeature -Online -FeatureName containers -All
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
Restart-Computer -Force

# 安裝 Docker Desktop 或使用 Windows Server 版 Docker Engine
docker run --isolation=hyperv --rm microsoft/nanoserver:latest cmd /c ver
```

實際案例：Win10 RS1 啟用後可運行 Hyper‑V 隔離 Windows 容器。
實作環境：Windows 10 Pro/Ent RS1+
實測數據：N/A（本文未提供；建議指標：容器啟動耗時、資源佔用）

Learning Points
- Windows 容器隔離類型
- Hyper‑V 隔離啟動方式
- 開發環境標準化

技能要求
- 必備：Windows 功能管理、Docker CLI
- 進階：自動化安裝/政策佈署（GPO/Intune）

延伸思考
- 何時用 Hyper‑V vs Process 隔離？
- 對效能與密度的影響？

Practice Exercise
- 基礎：啟用功能並拉取 nanoserver（30 分鐘）
- 進階：比較兩種隔離的啟動時間（2 小時）
- 專案：團隊一鍵安裝包（8 小時）

Assessment Criteria
- 功能完整性（40%）：可成功以 Hyper‑V 隔離啟動
- 程式碼品質（30%）：腳本可重用
- 效能（20%）：量測與報告
- 創新性（10%）：安裝自動偵測與回報


## Case #6: 使用 Linux Docker Client 遠端管理 Windows Container

### Problem Statement
**業務場景**：營運團隊多以 Linux 終端機作業，但需要管理 Windows Server 上的 Windows Container。希望不換工具即可進行 build/run/logs 等日常操作。
**技術挑戰**：跨 OS 使用 docker client 連線 Windows Docker Daemon，並妥善配置安全（TLS）。
**影響範圍**：運維效率與工具一致性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 不知道 Docker Client 可跨平台對接。
2. Windows Daemon 未開啟 TCP/TLS 端點。
3. 憑證配置不完整。

**深層原因**：
- 架構層面：遠端管理端點未標準化。
- 技術層面：TLS 與 daemon.json 設定不熟。
- 流程層面：缺乏金鑰/憑證發放流程。

### Solution Design
**解決策略**：在 Windows 主機設定 daemon.json 啟用 TCP/TLS，簽發客戶端憑證，Linux 端以 DOCKER_HOST/DOCKER_CERT_PATH 連線。

**實施步驟**：
1. 設定 Windows Docker Daemon
- 實作細節：daemon.json 設定 hosts 與 TLS 憑證位置。
- 所需資源：憑證、Windows 管理權限
- 預估時間：1-2 小時

2. Linux 端連線與驗證
- 實作細節：設 DOCKER_HOST、DOCKER_TLS_VERIFY、DOCKER_CERT_PATH。
- 所需資源：Docker CLI、憑證
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```json
// Windows: C:\ProgramData\Docker\config\daemon.json
{
  "hosts": ["npipe://", "tcp://0.0.0.0:2376"],
  "tls": true,
  "tlscacert": "C:\\ProgramData\\Docker\\certs\\ca.pem",
  "tlscert": "C:\\ProgramData\\Docker\\certs\\server-cert.pem",
  "tlskey": "C:\\ProgramData\\Docker\\certs\\server-key.pem",
  "tlsverify": true
}
```
```bash
# Linux 端
export DOCKER_HOST=tcp://win-docker.example.com:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=$HOME/.docker/win
docker info
docker ps
```

實際案例：Linux 運維終端可日常管理 Windows 容器叢集。
實作環境：Windows Server 2016, Linux 工作站
實測數據：N/A（本文未提供；建議量測：跨平台操作成功率、延遲）

Learning Points
- Docker Client/Server 分離與協定共通
- daemon.json 基礎
- 安全遠端操作

技能要求
- 必備：Docker CLI、TLS 概念
- 進階：憑證生命週期管理

延伸思考
- 如何以反向代理統一入口與審計？
- 多主機的金鑰輪替策略？

Practice Exercise
- 基礎：配置非 TLS 連線於測試網段（30 分鐘）
- 進階：配置 TLS 並成功 docker ps（2 小時）
- 專案：寫自動化腳本簽發與分發憑證（8 小時）

Assessment Criteria
- 功能完整性（40%）：可安全連線並操作
- 程式碼品質（30%）：設定清晰可維護
- 效能（20%）：連線穩定與延遲低
- 創新性（10%）：自動化與審計整合


## Case #7: 從 Docker Hub 取得 Windows Base Image 並驗證 OS

### Problem Statement
**業務場景**：開發者需從 Docker Hub 搜尋並拉取 Windows 基底映像，但 Hub 上不易辨識映像究竟是 Linux 或 Windows，常拉錯造成時間浪費。
**技術挑戰**：在拉取前辨識映像 OS；建立可重用的驗證命令或流程。
**影響範圍**：頻寬浪費、CI 失敗。
**複雜度評級**：低

### Root Cause Analysis
**直接原因**：
1. Hub 缺乏明確 OS 標示。
2. 未使用 manifest/inspect 辨識。
3. 缺乏白名單（microsoft/*）。

**深層原因**：
- 架構層面：映像治理缺失。
- 技術層面：未善用 manifest inspect。
- 流程層面：缺少映像來源審核。

### Solution Design
**解決策略**：建立「拉取前檢查」命令流程：優先使用 microsoft/*（nanoserver, windowsservercore, iis），輔以 docker manifest inspect 或拉取後 docker inspect 以確認 OS。

**實施步驟**：
1. 建立白名單與檢查腳本
- 實作細節：先比對命名空間，後用 manifest inspect。
- 所需資源：Docker CLI
- 預估時間：1 小時

2. CI 前置檢查
- 實作細節：於 Pipeline 拉取前先驗證 OS。
- 所需資源：CI 工具
- 預估時間：1 小時

**關鍵程式碼/設定**：
```bash
# 拉取前檢查 OS（需新版 CLI 支援 manifest）
img="$1"
docker manifest inspect --verbose "$img" | grep -i '"os"' | head -n1

# 拉取後再次驗證
docker pull "$img"
docker inspect --format '{{.Os}}' "$img"
```

實際案例：統一從 microsoft/nanoserver、microsoft/windowsservercore 取得基底，提高成功率。
實作環境：Windows Server 2016
實測數據：N/A（本文未提供；建議量測：錯誤拉取率、節省頻寬）

Learning Points
- Base image 選擇與驗證
- manifest/inspect 用法
- 映像治理

技能要求
- 必備：Docker 基礎
- 進階：CI 前置檢查自動化

延伸思考
- 內部鏡像代理與快取策略
- OS/版本 pinning 的治理

Practice Exercise
- 基礎：驗證 3 個映像的 OS（30 分鐘）
- 進階：把檢查整合入 CI（2 小時）
- 專案：建立團隊映像白名單與審核流程（8 小時）

Assessment Criteria
- 功能完整性（40%）：能準確辨識 OS
- 程式碼品質（30%）：腳本健壯
- 效能（20%）：檢查快速
- 創新性（10%）：自動修正/建議替代映像


## Case #8: 將 ASP.NET WebForms 以 Windows Server Core + IIS 容器化

### Problem Statement
**業務場景**：公司主力應用為 ASP.NET WebForms 搭配商用套件，無法移植到 .NET Core。希望先以 Windows 容器與 IIS 部署，提升一致性與可移植性。
**技術挑戰**：建置 IIS 映像、部署 WebForms、處理 ASP.NET 需求（如 .NET Framework）。
**影響範圍**：主力產品的交付速度與一致性。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 現有應用依賴 Windows/.NET Framework。
2. 誤以為只能在 Linux 容器執行。
3. 缺少 Windows IIS 基底映像。

**深層原因**：
- 架構層面：未建立 Windows 容器化路徑。
- 技術層面：IIS 映像建置經驗不足。
- 流程層面：缺少自動化部署腳本。

### Solution Design
**解決策略**：選用 microsoft/iis 或 windowsservercore 加裝 IIS，將 WebForms 應用打包，提供標準入口點與健康檢查。

**實施步驟**：
1. 建置 IIS 基底映像
- 實作細節：基於 microsoft/iis 或在 windowsservercore 啟用 IIS。
- 所需資源：Dockerfile、PowerShell
- 預估時間：1-2 小時

2. 部署網站與設定
- 實作細節：複製網站、設定應用集區、開放 80/443。
- 所需資源：網站檔案、IIS 設定
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
```Dockerfile
# 範例：使用 microsoft/iis 作為基底
FROM microsoft/iis:latest
SHELL ["powershell","-Command"]

# 啟用 ASP.NET 4.5 功能（視版本調整）
RUN dism /online /enable-feature /all /featurename:IIS-ASPNET45

# 複製網站到預設站台
COPY ./WebSite/ C:/inetpub/wwwroot/

EXPOSE 80
# 可選：健康檢查頁面或入口點維持前景
```

實際案例：WebForms 成功在 Windows 容器上以 IIS 提供服務。
實作環境：Windows Server 2016, microsoft/iis
實測數據：N/A（本文未提供；建議追蹤：映像建置時間、部署耗時）

Learning Points
- Windows + IIS 容器化步驟
- IIS/ASP.NET 功能啟用
- 文件與設定打包

技能要求
- 必備：IIS 基礎、Dockerfile
- 進階：IIS 自動化設定（appcmd/powershell）

延伸思考
- 日誌/設定外掛模式（Config as Code）
- 多站台與 SSL 憑證管理

Practice Exercise
- 基礎：建立 IIS 映像顯示 Hello（30 分鐘）
- 進階：部署 WebForms 範例站台（2 小時）
- 專案：自動化建置/部署 Pipeline（8 小時）

Assessment Criteria
- 功能完整性（40%）：站台可正常服務
- 程式碼品質（30%）：Dockerfile 清晰、可重建
- 效能（20%）：啟動時間、映像大小
- 創新性（10%）：健康檢查/監控整合


## Case #9: 在 Nano Server 上建置輕量級 Windows 應用

### Problem Statement
**業務場景**：部分工具/服務僅需極少 Windows 元件。團隊希望用 Nano Server 基底打造更小、更快啟動的映像，提升密度與拉取速度。
**技術挑戰**：Nano Server 功能精簡，需確定相容性與安裝方式（多用 PowerShell）。
**影響範圍**：映像大小、啟動速度、節省頻寬成本。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. 不清楚 Nano Server 的限制（如 API/元件缺）。
2. 直接沿用 servercore 指令導致失敗。
3. 安裝步驟需調整為 PowerShell 腳本化。

**深層原因**：
- 架構層面：未分層設計映像（輕重分離）。
- 技術層面：Nano 相容性理解不足。
- 流程層面：缺乏相容性清單。

### Solution Design
**解決策略**：以 microsoft/nanoserver 為基底，先做「功能探測 PoC 映像」，建立可用指令/元件清單，再針對正式應用打包。

**實施步驟**：
1. 功能探測映像
- 實作細節：測試必要可執行檔/工具可用性。
- 所需資源：PowerShell
- 預估時間：1 小時

2. 正式映像建置
- 實作細節：以 RUN 指令安裝必要元件；縮小層。
- 所需資源：工具安裝包
- 預估時間：1-2 小時

**關鍵程式碼/設定**：
```Dockerfile
FROM microsoft/nanoserver:latest
SHELL ["powershell","-Command"]
# 測試可用性與拋出版本資訊
RUN $PSVersionTable; \
    echo 'Nano Ready' > C:\ready.txt
CMD ["cmd","/c","type C:\\ready.txt"]
```

實際案例：工具型容器改用 Nano 將映像體積與啟動時間顯著下降（具體數據未提供）。
實作環境：Windows Server 2016, nanoserver
實測數據：N/A（本文未提供；建議量測：映像大小、拉取/啟動時間）

Learning Points
- Nano vs Server Core 差異
- PowerShell 腳本化安裝
- 層數與映像最佳化

技能要求
- 必備：Dockerfile、PowerShell
- 進階：映像瘦身技巧

延伸思考
- 多階段建置（若工具鏈支援）
- 基底版本 pinning 與 CVE 管理

Practice Exercise
- 基礎：建立 Nano Hello 映像（30 分鐘）
- 進階：在 Nano 上安裝常用工具（2 小時）
- 專案：Nano 與 Server Core 成本效益比較（8 小時）

Assessment Criteria
- 功能完整性（40%）：應用能在 Nano 正常運作
- 程式碼品質（30%）：Dockerfile 乾淨
- 效能（20%）：映像大小與啟動時間
- 創新性（10%）：瘦身策略


## Case #10: 缺乏 --link 功能下的服務連線替代方案

### Problem Statement
**業務場景**：團隊以微服務設計，但在 Windows Server 2016 TP5 上無法使用 Docker 的 container linking（--link）。Web 需連線 API 容器，難以自動建立服務間連線。
**技術挑戰**：無法使用 --link 時，如何安全穩定地讓容器彼此訪問。
**影響範圍**：服務拆分被迫回退、部署腳本複雜。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. TP5 不支援 --link。
2. 內建 DNS/name 解析尚未提供。
3. 無 overlay network。

**深層原因**：
- 架構層面：對服務發現的內部依賴過高。
- 技術層面：不熟悉替代連線策略。
- 流程層面：配置值管理混亂。

### Solution Design
**解決策略**：改以明確的 Port Publishing + 外部服務註冊/環境變數注入方式，讓 Web 以組態得知 API 位址；或使用主機級反向代理統一入口。

**實施步驟**：
1. 固定連線端點
- 實作細節：對 API 發布固定 HostPort，Web 以環境變數讀取。
- 所需資源：docker run、組態管理
- 預估時間：1 小時

2. 反向代理集中路由（可選）
- 實作細節：主機層 Nginx/IIS ARR 做路由，Web 只訪問固定域名。
- 所需資源：反向代理
- 預估時間：2 小時

**關鍵程式碼/設定**：
```powershell
# 啟動 API 並固定宿主機 Port 5000
docker run -d --name api -p 5000:80 myorg/api:win

# 啟動 Web，注入 API_URL（以宿主機 IP + 5000）
$hostIp="192.168.1.10"
docker run -d --name web -p 8080:80 -e API_URL="http://$hostIp:5000" myorg/web:win
```

實際案例：以固定 HostPort 與環境變數成功串接 Web→API。
實作環境：Windows Server 2016 TP5
實測數據：N/A（本文未提供；建議量測：部署腳本錯誤率、回滾率）

Learning Points
- 無 link 情況下的連線策略
- 環境變數/配置注入
- 反向代理應用

技能要求
- 必備：Docker 埠對映、環境變數
- 進階：反向代理與服務路由

延伸思考
- 導入服務註冊/發現（Consul）可否簡化？
- 未來支援內建 DNS 後的遷移策略？

Practice Exercise
- 基礎：以 HostPort 串接兩容器（30 分鐘）
- 進階：加入反向代理與路由規則（2 小時）
- 專案：腳本化多服務啟停與配置（8 小時）

Assessment Criteria
- 功能完整性（40%）：可靠連通
- 程式碼品質（30%）：腳本清晰
- 效能（20%）：延遲與吞吐量
- 創新性（10%）：可觀測性整合


## Case #11: 未提供內建 DNS 解析下的服務發現替代

### Problem Statement
**業務場景**：TP5 尚未提供 name/service-based IP 解析，容器無法透過服務名稱互相解析。微服務間難以解耦。
**技術挑戰**：在無內建 DNS 的情況下提供穩定的服務發現。
**影響範圍**：部署耦合度升高，維護成本增加。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 內建 DNS 尚未上線。
2. CLI 無對應功能。
3. 無 overlay 支援。

**深層原因**：
- 架構層面：依賴平台內建 DNS。
- 技術層面：不了解 Windows HNS 可設定自訂 DNS。
- 流程層面：缺少服務登錄策略。

### Solution Design
**解決策略**：在宿主層建置服務發現（如 Consul/DNSMasq），並用 Windows HNS 建立指定 DNSServerList 的網路，讓容器使用該 DNS；或在應用層以配置中心提供端點。

**實施步驟**：
1. 建立自訂 HNS 網路設定 DNS
- 實作細節：以 HNS JSON 建立 NAT/Transparent 網路並指定 DNS。
- 所需資源：PowerShell、HNS
- 預估時間：2 小時

2. 部署外部服務發現
- 實作細節：在宿主或外部主機跑 Consul，註冊服務。
- 所需資源：Consul/DNSMasq
- 預估時間：2-4 小時

**關鍵程式碼/設定**：
```powershell
# 以 HNS 建立帶自訂 DNS 的 NAT 網路
$hnsRequest = @"
{
  "Name":  "customnat",
  "Type":  "NAT",
  "Subnets":  [{"AddressPrefix":  "172.30.0.0/24", "GatewayAddress": "172.30.0.1"}],
  "DNSServerList": "192.168.1.100"
}
"@
Invoke-Expression "New-HnsNetwork -InputObject $hnsRequest"

# 使用該網路啟動容器
docker network create -d nat customnat
docker run -d --network customnat myorg/api:win
```

實際案例：透過外部 DNS（Consul）+ HNS 指定 DNS 成功提供名稱解析。
實作環境：Windows Server 2016 TP5
實測數據：N/A（本文未提供；建議量測：解析成功率、故障切換時間）

Learning Points
- HNS 網路模型
- 外部服務發現整合
- 遷移到內建 DNS 的路徑

技能要求
- 必備：Windows 網路/HNS、Docker network
- 進階：服務發現架構（Consul）

延伸思考
- DNS 故障的降級方案？
- 安全與 ACL 控制？

Practice Exercise
- 基礎：建立自訂 DNS 的 HNS 網路（30 分鐘）
- 進階：容器使用服務名存取 API（2 小時）
- 專案：以 Consul 建立多服務名稱解析（8 小時）

Assessment Criteria
- 功能完整性（40%）：名稱解析可用
- 程式碼品質（30%）：設定可重用
- 效能（20%）：解析延遲低
- 創新性（10%）：自動註冊整合


## Case #12: 不支援 --dns/--dns-search 的容器 DNS 設定替代

### Problem Statement
**業務場景**：容器需要使用企業內部 DNS，但 TP5 不支援 --dns/--dns-search 選項，導致解析與搜尋域策略無法直接配置。
**技術挑戰**：在不變更 CLI 參數的情況下，為容器指定 DNS。
**影響範圍**：服務無法解析內部域名、部署失敗。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. CLI 不支援 --dns/--dns-search。
2. 預設使用宿主 DNS 但不符合需求。
3. 未知替代方式（HNS）。

**深層原因**：
- 架構層面：網路配置仰賴 CLI。
- 技術層面：HNS 能力未被運用。
- 流程層面：主機層 DNS 管理未納入容器需求。

### Solution Design
**解決策略**：以 HNS 建立客製網路時指定 DNSServerList 與（如有）Domain；或變更宿主 DNS，讓容器繼承。

**實施步驟**：
1. 建立自訂 HNS 網路指定 DNS
- 實作細節：同 Case #11，但加入搜尋域（若支援）。
- 所需資源：PowerShell/HNS
- 預估時間：1 小時

2. 宿主 DNS 調整（備援方案）
- 實作細節：將宿主 DNS 指向企業 DNS。
- 所需資源：Windows 網路設定權限
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```powershell
$hns = @"
{
  "Name": "corpnet",
  "Type": "NAT",
  "Subnets":[{"AddressPrefix":"172.31.0.0/24","GatewayAddress":"172.31.0.1"}],
  "DNSServerList": "10.0.0.10,10.0.0.11"
}
"@
New-HnsNetwork -InputObject $hns
docker network create -d nat corpnet
docker run -d --network corpnet myorg/app:win
```

實際案例：容器成功使用企業 DNS 完成內部解析。
實作環境：Windows Server 2016 TP5
實測數據：N/A（本文未提供；建議量測：解析成功率）

Learning Points
- 以 HNS 取代 CLI DNS 參數
- 宿主層 DNS 繼承策略
- 網路治理

技能要求
- 必備：Windows 網路、PowerShell
- 進階：企業 DNS/AD DNS 管理

延伸思考
- 多 DNS 容錯與負載平衡
- 對混合雲 DNS 的擴展

Practice Exercise
- 基礎：HNS 指定 DNS 的容器（30 分鐘）
- 進階：切換不同 DNS 並驗證（2 小時）
- 專案：企業 DNS 政策文件（8 小時）

Assessment Criteria
- 功能完整性（40%）：解析符合政策
- 程式碼品質（30%）：設定清晰
- 效能（20%）：解析延遲
- 創新性（10%）：自動化與監控


## Case #13: 不支援 --hostname 的替代：解除應用對主機名耦合

### Problem Statement
**業務場景**：某些 Windows 應用啟動時會讀取機器名稱用於授權或節點識別，但 TP5 不支援以 --hostname 指定容器主機名，導致應用啟動異常。
**技術挑戰**：在無法改主機名的前提下，提供應用可用的識別資訊。
**影響範圍**：授權檢核、叢集節點識別。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. CLI 不支援 --hostname。
2. Windows 容器變更計算機名需重啟且非設計用途。
3. 應用硬耦合 hostname。

**深層原因**：
- 架構層面：以主機名作識別的設計不利容器化。
- 技術層面：未提供替代識別方式。
- 現程式碼：未參數化。

### Solution Design
**解決策略**：改以環境變數/設定檔提供節點 ID 或授權 ID，應用改讀 ENV 優先，其次再退回主機名；以容器名稱作為邏輯識別。

**實施步驟**：
1. 調整應用讀取識別
- 實作細節：優先讀 ENV NODE_ID，否則 docker 容器名。
- 所需資源：程式碼調整
- 預估時間：2-4 小時

2. 啟動注入識別
- 實作細節：docker run -e NODE_ID=...
- 所需資源：啟動腳本
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```powershell
# C# 範例：優先讀環境變數，其次容器名（以 HOSTNAME 環境變數或 API 取得）
var nodeId = Environment.GetEnvironmentVariable("NODE_ID");
if (string.IsNullOrWhiteSpace(nodeId))
{
    nodeId = Environment.MachineName; // 退回
}
Console.WriteLine($"NodeId={nodeId}");
```
```powershell
# 啟動時注入
docker run -d --name app1 -e NODE_ID="license-node-01" myorg/app:win
```

實際案例：以環境變數提供授權/節點識別，應用穩定啟動。
實作環境：Windows Server 2016 TP5
實測數據：N/A（本文未提供；建議量測：啟動成功率、授權驗證時間）

Learning Points
- 容器友善的識別策略
- 環境變數/容器名使用
- 反耦合設計

技能要求
- 必備：應用組態化
- 進階：十二要素應用實踐

延伸思考
- 對授權綁定硬體的應用如何容器化？
- 識別與安全的平衡

Practice Exercise
- 基礎：改用環境變數驅動識別（30 分鐘）
- 進階：容器名/ENV 雙路 fallback（2 小時）
- 專案：重構一個需主機名的模組（8 小時）

Assessment Criteria
- 功能完整性（40%）：應用可啟動且識別正確
- 程式碼品質（30%）：參數化良好
- 效能（20%）：啟動穩定
- 創新性（10%）：可移植性設計


## Case #14: 不支援 --add-host 的替代：啟動時動態更新 hosts

### Problem Statement
**業務場景**：在 TP5 中無法用 --add-host 寫入容器 hosts 檔，部分舊系統仍需臨時 hosts 映射。需提供無 CLI 參數的替代實作。
**技術挑戰**：確保在容器啟動時以權限允許的方式安全修改 hosts。
**影響範圍**：暫時導流、灰度、與內網測試。
**複雜度評級**：中

### Root Cause Analysis
**直接原因**：
1. CLI 不支援 --add-host。
2. 容器檔案系統需以系統帳戶修改 hosts。
3. 缺乏自動化入口點腳本。

**深層原因**：
- 架構層面：配置推送未集中化。
- 技術層面：不了解 Windows hosts 檔位置與權限。
- 流程層面：啟動流程不可擴展。

### Solution Design
**解決策略**：在映像內提供 entrypoint.ps1，啟動時根據環境變數寫入 C:\Windows\System32\drivers\etc\hosts，然後再啟動主服務。

**實施步驟**：
1. 寫入入口點腳本
- 實作細節：解析 ENV HOSTS_ENTRIES，逐行追加。
- 所需資源：PowerShell
- 預估時間：1 小時

2. Dockerfile 與啟動
- 實作細節：ENTRYPOINT 指向腳本，環境變數注入。
- 所需資源：Dockerfile
- 預估時間：0.5 小時

**關鍵程式碼/設定**：
```Dockerfile
FROM microsoft/windowsservercore:latest
SHELL ["powershell","-Command"]
COPY entrypoint.ps1 C:/entrypoint.ps1
ENTRYPOINT ["powershell","-File","C:\\entrypoint.ps1"]
```
```powershell
# entrypoint.ps1
$hostsFile = "C:\Windows\System32\drivers\etc\hosts"
$entries = $env:HOSTS_ENTRIES # 例如 "10.0.0.5 api.local;10.0.0.6 db.local"
if ($entries) {
  $entries.Split(";") | ForEach-Object {
    if ($_ -match "^\s*\d+\.\d+\.\d+\.\d+\s+\S+") {
      Add-Content -Path $hostsFile -Value $_
    }
  }
}
# 啟動主應用
Start-Process "C:\app\app.exe" -NoNewWindow -Wait
```
```powershell
# 啟動
docker run -e HOSTS_ENTRIES="10.0.0.5 api.local;10.0.0.6 db.local" myorg/app:win
```

實際案例：成功以啟動腳本替代 --add-host 實現臨時解析。
實作環境：Windows Server 2016 TP5
實測數據：N/A（本文未提供；建議量測：hosts 更新成功率、回滾時間）

Learning Points
- 入口點腳本化
- 配置以環境變數注入
- 權限與安全考量

技能要求
- 必備：PowerShell、Windows 路徑
- 進階：安全與審計

延伸思考
- 改用外部 DNS/代理是否更佳？
- 防止 hosts 汙染的清理策略

Practice Exercise
- 基礎：寫入單筆 hosts（30 分鐘）
- 進階：支援多筆與格式校驗（2 小時）
- 專案：灰度路由方案（8 小時）

Assessment Criteria
- 功能完整性（40%）：hosts 正確更新
- 程式碼品質（30%）：腳本健壯
- 效能（20%）：啟動延遲低
- 創新性（10%）：回滾與審計


## Case #15: 沒有 overlay network 下的多主機部署策略

### Problem Statement
**業務場景**：TP5 不支援 overlay driver，跨主機容器間網通與服務發現受限。團隊仍希望在多台 Windows 主機分散負載。
**技術挑戰**：在無 overlay 下，設計可運作的多主機拓撲與路由策略。
**影響範圍**：可用性、擴展性與維運複雜度。
**複雜度評級**：高

### Root Cause Analysis
**直接原因**：
1. 缺乏 overlay driver。
2. 內建 DNS/alias 等配套不足。
3. CLI 多網段參數受限。

**深層原因**：
- 架構層面：假設容器網路跨主機可透明。
- 技術層面：不熟悉 Windows HNS transparent/l2bridge。
- 流程層面：缺少外部負載平衡器策略。

### Solution Design
**解決策略**：採用以下之一或組合：單主機多容器部署；使用 HNS Transparent（l2bridge）讓容器取得實體網段 IP；以主機層負載平衡（NLB/硬體 LB）將流量分配至各主機上的服務。

**實施步驟**：
1. 建立 Transparent 網路
- 實作細節：HNS 建立 l2bridge/transparent，容器獲得實網段 IP。
- 所需資源：網管協作、VLAN 設定（如需）
- 預估時間：2-4 小時

2. 外部負載平衡
- 實作細節：以 NLB/硬體 LB 指向各容器 IP 或各主機對映埠。
- 所需資源：LB 設備
- 預估時間：2 小時

**關鍵程式碼/設定**：
```powershell
# 建立 Transparent 網路（示意，實際視網路環境）
$hnsJson = @"
{
  "Name": "transparent",
  "Type": "Transparent"
}
"@
New-HnsNetwork -InputObject $hnsJson

docker network create -d transparent trans
docker run -d --network trans myorg/api:win
```

實際案例：以外部 LB 導流至多台主機上的 API 容器，達成水平擴展。
實作環境：Windows Server 2016 TP5
實測數據：N/A（本文未提供；建議量測：可用性、RPS）

Learning Points
- HNS Transparent/l2bridge 概念
- 外部 LB 整合
- 漸進式多主機策略

技能要求
- 必備：Windows 網路、LB 基礎
- 進階：企業網路與 VLAN 實務

延伸思考
- 之後支援 overlay 時的演進路徑
- 與 Kubernetes on Windows 的未來整合

Practice Exercise
- 基礎：建立 transparent 網路並通外網（30 分鐘）
- 進階：以 NLB 做雙主機流量分配（2 小時）
- 專案：設計高可用拓撲與演練（8 小時）

Assessment Criteria
- 功能完整性（40%）：跨主機可服務
- 程式碼品質（30%）：網路設定清晰
- 效能（20%）：吞吐與延遲
- 創新性（10%）：可遷移性設計


--------------------------------
案例分類

1. 按難度分類
- 入門級（適合初學者）
  - Case #1 平台判斷
  - Case #2 修正拉取 Linux 映像
  - Case #3 修正在 Linux 引擎跑 Windows App
  - Case #7 取得並驗證 Windows Base Image
- 中級（需要一定基礎）
  - Case #4 啟用 Windows Container（Server）
  - Case #5 Win10 + Hyper‑V 隔離
  - Case #6 Linux Client 管理 Windows 主機
  - Case #8 WebForms + IIS 容器化
  - Case #9 Nano Server 輕量化
  - Case #10 無 --link 的服務連線
  - Case #12 無 --dns/--dns-search 的 DNS 設定
  - Case #14 無 --add-host 的 hosts 更新
- 高級（需要深厚經驗）
  - Case #11 無內建 DNS 的服務發現替代
  - Case #13 無 --hostname 的反耦合
  - Case #15 無 overlay 的多主機部署策略

2. 按技術領域分類
- 架構設計類
  - Case #1, #10, #11, #13, #15
- 效能優化類
  - Case #9（映像瘦身／啟動時間）
- 整合開發類
  - Case #4, #5, #6, #7, #8, #12, #14
- 除錯診斷類
  - Case #2, #3
- 安全防護類
  - Case #6（TLS 遠端管理）

3. 按學習目標分類
- 概念理解型
  - Case #1, #3, #7
- 技能練習型
  - Case #4, #5, #6, #8, #9, #12, #14
- 問題解決型
  - Case #2, #10, #11, #13, #15
- 創新應用型
  - Case #9, #15


案例關聯圖（學習路徑建議）
- 先學案例（基礎概念與平台識別）：
  - Case #1 → Case #2 → Case #3 → Case #7
- 環境建置與工具整合（依賴基本概念）：
  - Case #4（Server）與 Case #5（Win10）可並行；完成後學 Case #6（跨平台管理）
- 應用容器化實作（依賴基礎與環境建置）：
  - Case #8（IIS/WebForms）與 Case #9（Nano 輕量化）
- 網路限制與替代方案（依賴前述全部基礎）：
  - Case #10（無 --link）→ Case #11（無內建 DNS）
  - Case #12（無 --dns/--dns-search）與 Case #13（無 --hostname）可穿插
  - 收斂到 Case #15（無 overlay 的多主機策略）
- 完整路徑建議：
  1) Case #1 → 2 → 3 → 7（建立正確心智模型與映像辨識）
  2) Case #4/5 → 6（裝好環境與管理方式）
  3) Case #8/9（完成應用容器化）
  4) Case #10 → 11 → 12/13 → 14（網路與配置限制的替代解）
  5) Case #15（規劃多主機拓撲與演進）
- 依賴關係：
  - Case #11、#12 依賴 HNS 概念（可由 #10 引入）
  - Case #15 依賴 #10/#11 的服務連線與發現策略
  - Case #8 依賴 #4/#5（環境）與 #7（映像）
{% endraw %}